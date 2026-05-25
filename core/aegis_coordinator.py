"""
neuralvault.core.aegis_coordinator
──────────────────────────────────
Aegis Commit Coordinator (2PC WAL & Event Sourcing Recovery).
Garantisce la coerenza transazionale e la consistenza finale tra DuckDB e KùzuDB.
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional

class AegisCommitCoordinator:
    """
    Gestisce la riconciliazione atomica all'avvio (Reconciliation-on-Boot).
    Verifica l'allineamento dei conteggi dei nodi tra DuckDB e KùzuDB,
    ripristina lo stato a partire dal più recente Snapshot,
    e riesegue la proiezione degli eventi persi dal ledger.
    """
    def __init__(self, engine, kuzu_projection, log_path: str = "vault_data/aegis_event_log.jsonl"):
        self.engine = engine
        self.kuzu_proj = kuzu_projection
        self.log_path = log_path
        self.logger = logging.getLogger("Sovereign.AegisCoordinator")

    def _find_latest_snapshot_in_log(self) -> Optional[str]:
        """Scansiona il log alla ricerca del più recente evento SNAPSHOT_CREATED valido."""
        if not os.path.exists(self.log_path):
            return None
        latest_snapshot = None
        try:
            with open(self.log_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if not line.strip():
                        continue
                    event = json.loads(line)
                    if event.get("event_type") == "SNAPSHOT_CREATED":
                        payload = event.get("payload", {})
                        snapshot_file = payload.get("snapshot_file")
                        if snapshot_file and os.path.exists(snapshot_file):
                            latest_snapshot = snapshot_file
            return latest_snapshot
        except Exception as e:
            self.logger.debug(f"Error scanning log for snapshots: {e}")
            return None

    def check_and_reconcile(self) -> bool:
        """
        Esegue il controllo di coerenza tra DuckDB e KùzuGraph.
        Restituisce True se il sistema è coerente o è stato riallineato con successo.
        """
        self.logger.info("🏺 [Aegis Coordinator] Starting storage consistency check...")
        
        # Allineamento dinamico del percorso del log
        if not os.path.exists(self.log_path):
            root_log = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "aegis_event_log.jsonl"))
            if os.path.exists(root_log):
                self.log_path = root_log
                
        # 1. Recupero conteggio DuckDB
        duck_count = 0
        try:
            res = self.engine._prefilter.fetchall("SELECT COUNT(*) FROM vault_metadata")
            if res:
                duck_count = res[0][0]
        except Exception as e:
            self.logger.error(f"Error reading DuckDB node count: {e}")
            return False

        # 2. Recupero conteggio KùzuDB
        kuzu_count = 0
        try:
            res = self.kuzu_proj.conn.execute("MATCH (n:KnowledgeNode) RETURN COUNT(*)")
            if res.has_next():
                kuzu_count = res.get_next()[0]
        except Exception as e:
            self.logger.error(f"Error reading KùzuDB node count: {e}")
            return False

        self.logger.info(f"📊 [Count Check] DuckDB: {duck_count} | KùzuDB: {kuzu_count}")
        
        # Self-Healing: Se DuckDB ha 0 nodi ma l'engine ha nodi caricati in RAM (idratati via Snapshot o Episodic),
        # ricostruiamo immediatamente il pre-filtraggio relazionale in DuckDB a partire dalla memoria!
        if duck_count == 0 and hasattr(self.engine, '_nodes') and len(self.engine._nodes) > 0:
            self.logger.warning("⚠️ [Aegis Coordinator] DuckDB was empty but Engine RAM has hydrated nodes. Synchronizing DuckDB from RAM...")
            nodes_to_insert = []
            for nid, node in self.engine._nodes.items():
                coll = getattr(node, 'collection', None) or (node.metadata.get("source") if node.metadata else None) or "nodes"
                meta = node.metadata if node.metadata else {}
                nodes_to_insert.append((nid, coll, meta))
            
            try:
                self.engine._prefilter.add_nodes_batch(nodes_to_insert)
                duck_count = len(nodes_to_insert)
                self.logger.info(f"✅ [Aegis Coordinator] DuckDB populated successfully with {duck_count} nodes from RAM.")
            except Exception as e:
                self.logger.error(f"❌ [Aegis Coordinator] Failed to synchronize DuckDB from RAM: {e}")

        # Disaster Recovery Engine: Se entrambi sono vuoti o c'è una grave discrepanza, cerchiamo lo snapshot
        if duck_count == 0 or kuzu_count == 0 or abs(duck_count - kuzu_count) > 1:
            latest_snapshot_path = self._find_latest_snapshot_in_log()
            if latest_snapshot_path:
                self.logger.info(f"📸 [Snapshot Recovery] Disaster state detected. Restoring from: {latest_snapshot_path}")
                from core.snapshot_daemon import AegisSnapshotDaemon
                daemon = AegisSnapshotDaemon(self.engine, self.kuzu_proj)
                if daemon.restore_from_snapshot(latest_snapshot_path):
                    snapshot_seq = daemon.event_bus.sequence_counter
                    self.logger.info(f"🔄 Replaying events from sequence > {snapshot_seq}")
                    return self._replay_event_ledger(start_from_sequence=snapshot_seq)

        # Se i conteggi coincidono, verifichiamo anche le relazioni ed usciamo felici
        if duck_count == kuzu_count and duck_count > 0:
            self.logger.info("✅ [Aegis Coordinator] Node stores are perfectly aligned.")
            self._reconcile_relations()
            return True

        # Se c'è discrepanza, attiviamo il replay del ledger
        self.logger.warning(
            f"⚠️ [Mismatch Detected] DuckDB has {duck_count} nodes but KùzuDB has {kuzu_count}. "
            "Engaging Replay Ledger recovery daemon."
        )
        return self._replay_event_ledger()

    def _replay_event_ledger(self, start_from_sequence: int = 0) -> bool:
        """
        Ripercorre l'Aegis Event Log per ricostruire i nodi grafici mancanti in KùzuDB.
        Ignora gli eventi registrati prima di start_from_sequence (già presenti nello snapshot).
        """
        if not os.path.exists(self.log_path):
            self.logger.warning(f"Aegis Event Log not found at {self.log_path}. Reconstructing from DuckDB directly.")
            return self._reconstruct_from_duckdb()

        recovered_nodes = 0
        try:
            with open(self.log_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if not line.strip():
                        continue
                    event = json.loads(line)
                    event_type = event.get("event_type")
                    sequence = event.get("sequence", 0)
                    payload = event.get("payload", {})
                    
                    if sequence <= start_from_sequence:
                        continue
                        
                    if event_type == "NODE_CREATED":
                        node_id = payload.get("id")
                        if not node_id:
                            continue
                            
                        # 1. Proiettiamo in KùzuDB se manca
                        res = self.kuzu_proj.conn.execute(
                            "MATCH (n:KnowledgeNode {id: $id}) RETURN COUNT(*)", 
                            {"id": node_id}
                        )
                        exists = False
                        if res.has_next():
                            exists = res.get_next()[0] > 0
                            
                        if not exists:
                            self.kuzu_proj.handle_event("NODE_CREATED", payload)
                            recovered_nodes += 1
                            
                        # 2. Proiettiamo in RAM dell'Engine se manca
                        if node_id not in self.engine._nodes:
                            from index.node import VaultNode
                            import numpy as np
                            vector_list = payload.get("vector")
                            metadata = payload.get("metadata", {})
                            node = VaultNode(
                                id=node_id, 
                                text=payload.get("text", ""), 
                                vector=np.array(vector_list) if vector_list else None, 
                                metadata=metadata
                            )
                            self.engine._nodes[node_id] = node
                            
                        # 3. Proiettiamo in DuckDB se manca
                        try:
                            check_duck = self.engine._prefilter.fetchall(
                                "SELECT COUNT(*) FROM vault_metadata WHERE id = ?", (node_id,)
                            )
                            if check_duck and check_duck[0][0] == 0:
                                self.engine._prefilter.execute(
                                    "INSERT INTO vault_metadata (id, collection, metadata) VALUES (?, ?, ?)",
                                    (node_id, "nodes", json.dumps(payload.get("metadata", {})))
                                )
                        except Exception as e:
                            self.logger.debug(f"DuckDB replay insertion error: {e}")

            self.logger.info(f"✅ [Aegis Coordinator] Replayed event log. Recovered {recovered_nodes} missing nodes in KùzuDB.")
            self._reconcile_relations()
            
            # Verify counts after replay to catch truncated event logs
            kuzu_count = 0
            try:
                res = self.kuzu_proj.conn.execute("MATCH (n:KnowledgeNode) RETURN COUNT(*)")
                if res.has_next():
                    kuzu_count = res.get_next()[0]
            except Exception:
                pass
                
            duck_count = 0
            try:
                res = self.engine._prefilter.fetchall("SELECT COUNT(*) FROM vault_metadata")
                if res:
                    duck_count = res[0][0]
            except Exception:
                pass
                
            if duck_count != kuzu_count:
                self.logger.warning(
                    f"⚠️ [Aegis Coordinator] Count mismatch persists after event log replay (DuckDB: {duck_count} vs KùzuDB: {kuzu_count}). "
                    "Executing Deep Reconstruction from DuckDB..."
                )
                return self._reconstruct_from_duckdb()
                
            return True
        except Exception as e:
            self.logger.error(f"Error during event log replay: {e}")
            return self._reconstruct_from_duckdb()

    def _reconstruct_from_duckdb(self) -> bool:
        """
        Caso di fallback estremo: ricostruisce i nodi grafici leggendo direttamente da DuckDB.
        """
        self.logger.info("🛠️ [Deep Recovery] Reconstructing Kùzu graph nodes directly from DuckDB...")
        try:
            # Ottimizzazione ad alte prestazioni: pre-carichiamo tutti gli ID presenti in KùzuDB in un set
            # per evitare di fare decine di migliaia di query Cypher individuali
            kuzu_ids = set()
            try:
                res_ids = self.kuzu_proj.conn.execute("MATCH (n:KnowledgeNode) RETURN n.id")
                while res_ids.has_next():
                    kuzu_ids.add(res_ids.get_next()[0])
            except Exception as ek:
                self.logger.debug(f"Error pre-fetching Kùzu IDs: {ek}")

            res = self.engine._prefilter.fetchall("SELECT id, collection, metadata FROM vault_metadata")
            recovered = 0
            for row in res:
                node_id = row[0]
                collection = row[1]
                meta_str = row[2]
                
                meta = json.loads(meta_str) if isinstance(meta_str, str) else meta_str
                
                if node_id not in kuzu_ids:
                    payload = {
                        "id": node_id,
                        "title": meta.get("title", "Untitled"),
                        "type": meta.get("type", "generic"),
                        "timestamp": meta.get("created_at", 0.0)
                    }
                    self.kuzu_proj.handle_event("NODE_CREATED", payload)
                    recovered += 1
                    
            self.logger.info(f"✅ [Deep Recovery] Successfully restored {recovered} nodes in KùzuDB.")
            self._reconcile_relations()
            return True
        except Exception as e:
            self.logger.error(f"Failed deep recovery from DuckDB: {e}")
            return False

    def _reconcile_relations(self):
        """
        Verifica che tutte le relazioni causali presenti nei nodi DuckDB siano proiettate in KùzuDB.
        """
        self.logger.info("🔗 [Aegis Coordinator] Reconciling graph relationships...")
        reconciled_edges = 0
        try:
            # [v11.2 Optimization] Pre-fetch all existing edges from KùzuDB into a set for O(1) set lookups,
            # avoiding 100,000+ individual Cypher queries at startup.
            existing_edges = set()
            try:
                res_edges = self.kuzu_proj.conn.execute(
                    "MATCH (a:KnowledgeNode)-[r:CausalEdge]->(b:KnowledgeNode) "
                    "RETURN a.id, b.id, r.relation_type"
                )
                while res_edges.has_next():
                    row = res_edges.get_next()
                    existing_edges.add((row[0], row[1], str(row[2])))
            except Exception as ee:
                self.logger.debug(f"Error pre-fetching Kùzu edges: {ee}")

            # [Self-Healing] Thread-Safe Snapshot of active nodes to prevent concurrent mutation errors
            with self.engine._lock:
                active_nodes = list(self.engine._nodes.items())
                
            for node_id, node in active_nodes:
                # Thread-safe read of node edges to avoid concurrent modification exceptions
                with self.engine._lock:
                    edges = list(node.edges)
                    
                for edge in edges:
                    target_id = edge.target_id
                    relation = edge.relation
                    weight = edge.weight
                    
                    # Verify if the edge exists in our O(1) set
                    exists = (node_id, target_id, str(relation)) in existing_edges
                        
                    if not exists:
                        # Creiamo l'arco mancante in KùzuDB
                        self.kuzu_proj.conn.execute(
                            "MATCH (a:KnowledgeNode {id: $src}), (b:KnowledgeNode {id: $tgt}) "
                            "MERGE (a)-[r:CausalEdge {relation_type: $rel}]->(b) "
                            "ON CREATE SET r.weight = $w",
                            {"src": node_id, "tgt": target_id, "rel": str(relation), "w": float(weight)}
                        )
                        reconciled_edges += 1
                        # Aggiungiamo al set locale per evitare duplicati successivi
                        existing_edges.add((node_id, target_id, str(relation)))
                        import time
                        time.sleep(0.005) # Yield GIL to unblock FastAPI endpoints and Dashboard UI
                        
            if reconciled_edges > 0:
                self.logger.info(f"✅ [Aegis Coordinator] Reconciled {reconciled_edges} missing causal links in KùzuDB.")
            else:
                self.logger.info("✅ [Aegis Coordinator] Graph relationships are fully synchronized.")
        except Exception as e:
            self.logger.error(f"Error reconciling relationships: {e}")
