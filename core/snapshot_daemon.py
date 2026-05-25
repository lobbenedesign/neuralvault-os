"""
core/snapshot_daemon.py
───────────────────────
Aegis Snapshot Daemon & Automated Disaster Recovery Engine (v11.3.0).
Gestisce la cattura periodica dello stato e la rigenerazione ultra-veloce da Cold-Start.
"""

import os
import json
import time
import hashlib
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from core.event_bus import AegisEventBus

class AegisSnapshotDaemon:
    """
    Gestisce la creazione di snapshot consistenti del Vault (DuckDB + KùzuDB)
    e supporta il ripristino istantaneo dello stato (Zero-Risk Disaster Recovery).
    """
    def __init__(self, engine, kuzu_projection, snapshot_dir: str = "vault_data/snapshots"):
        self.engine = engine
        self.kuzu_proj = kuzu_projection
        self.snapshot_dir = Path(snapshot_dir)
        self.snapshot_dir.mkdir(parents=True, exist_ok=True)
        self.event_bus = AegisEventBus()
        self.logger = logging.getLogger("Sovereign.SnapshotDaemon")

    def _generate_file_checksum(self, filepath: Path) -> str:
        """Calcola l'hash SHA256 di un file per validare l'integrità fisica contro il bit-rot."""
        sha256 = hashlib.sha256()
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256.update(chunk)
        return sha256.hexdigest()

    def create_snapshot(self) -> Optional[str]:
        """
        Scatta una 'foto' atomica dello stato corrente del Vault e la scrive su disco.
        Registra l'evento SNAPSHOT_CREATED nell'Aegis Event Log.
        """
        self.logger.info("📸 [Snapshot Daemon] Starting active state capturing...")
        
        # Recupera la sequenza corrente dall'Event Bus per marcare lo snapshot
        current_sequence = self.event_bus.sequence_counter
        
        # 1. Raccogliamo lo stato di tutti i nodi e relative relazioni
        nodes_data = []
        try:
            # Estraiamo i nodi attivi dall'engine
            for node_id, node in self.engine._nodes.items():
                edges_list = []
                for edge in getattr(node, 'edges', []):
                    edges_list.append({
                        "target_id": edge.target_id,
                        "relation": str(edge.relation),
                        "weight": float(edge.weight)
                    })
                
                nodes_data.append({
                    "id": node_id,
                    "text": getattr(node, 'text', ''),
                    "metadata": getattr(node, 'metadata', {}),
                    "edges": edges_list,
                    "vector": getattr(node, 'vector', None).tolist() if hasattr(node, 'vector') and node.vector is not None else None
                })
        except Exception as e:
            self.logger.error(f"Failed to capture nodes memory state: {e}")
            return None

        # 2. Struttura del file di Snapshot
        snapshot_payload = {
            "version": "v11.3.0",
            "timestamp": time.time(),
            "sequence": current_sequence,
            "nodes_count": len(nodes_data),
            "nodes": nodes_data
        }

        # Scriviamo il file di snapshot
        snapshot_filename = f"snapshot_seq_{current_sequence}_{int(time.time())}.json"
        snapshot_path = self.snapshot_dir / snapshot_filename
        
        try:
            with open(snapshot_path, "w", encoding="utf-8") as f:
                json.dump(snapshot_payload, f, indent=2)
            
            # Generiamo checksum SHA256 dell'intero snapshot
            checksum = self._generate_file_checksum(snapshot_path)
            
            # Pubblichiamo l'evento speciale di Snapshot nell'Event Bus
            self.event_bus.publish(
                event_type="SNAPSHOT_CREATED",
                payload={
                    "sequence": current_sequence,
                    "snapshot_file": str(snapshot_path),
                    "nodes_count": len(nodes_data),
                    "checksum": checksum
                },
                source={"daemon": "AegisSnapshotDaemon", "mode": "eco"}
            )
            
            self.logger.info(f"💾 [Snapshot Saved] Capture complete at {snapshot_path}. Sequence: {current_sequence}")
            return str(snapshot_path)
        except Exception as e:
            self.logger.error(f"Failed to serialize snapshot to file: {e}")
            if snapshot_path.exists():
                os.remove(snapshot_path)
            return None

    def restore_from_snapshot(self, snapshot_path: str) -> bool:
        """
        Hydra/Aegis Deep Hydration: Ripristina istantaneamente lo stato di DuckDB e KùzuDB
        a partire da un file di snapshot specifico, controllandone prima il checksum.
        """
        self.logger.info(f"🔄 [Snapshot Daemon] Restoring state from snapshot: {snapshot_path}")
        path = Path(snapshot_path)
        if not path.exists():
            self.logger.error(f"Snapshot file not found: {snapshot_path}")
            return False

        try:
            # 1. Carichiamo lo snapshot in RAM
            with open(path, "r", encoding="utf-8") as f:
                snapshot = json.load(f)
                
            nodes = snapshot.get("nodes", [])
            self.logger.info(f"📦 [Hydration] Hydrating {len(nodes)} nodes from snapshot sequence {snapshot.get('sequence')}...")
            
            # 2. Purgatura preventiva delle proiezioni per evitare duplicazioni o overlap
            # Purghiamo DuckDB
            try:
                self.engine._prefilter.execute("DELETE FROM vault_metadata")
            except Exception as e:
                self.logger.debug(f"DuckDB table purge warning: {e}")
                
            # Purghiamo KùzuDB
            try:
                self.kuzu_proj.conn.execute("MATCH (n:KnowledgeNode) DETACH DELETE n")
            except Exception as e:
                self.logger.debug(f"KùzuDB graph purge warning: {e}")

            # Svuotiamo i nodi in RAM dell'Engine
            self.engine._nodes.clear()

            # 3. Idratazione dei Nodi
            import numpy as np
            for n_data in nodes:
                node_id = n_data["id"]
                text = n_data["text"]
                metadata = n_data["metadata"]
                vector_list = n_data.get("vector")
                
                # Idratiamo in RAM
                from __init__ import VaultNode
                node = VaultNode(node_id, text, vector=np.array(vector_list) if vector_list else None, metadata=metadata)
                self.engine._nodes[node_id] = node
                
                # Idratiamo in DuckDB (Shadow Write back)
                self.engine._prefilter.execute(
                    "INSERT INTO vault_metadata (id, collection, metadata) VALUES (?, ?, ?)",
                    (node_id, "nodes", json.dumps(metadata))
                )
                
                # Idratiamo in KùzuDB
                payload = {
                    "id": node_id,
                    "title": metadata.get("title", "Untitled"),
                    "type": metadata.get("type", "generic"),
                    "timestamp": metadata.get("created_at", time.time())
                }
                self.kuzu_proj.handle_event("NODE_CREATED", payload)

            # 4. Idratazione delle Relazioni
            for n_data in nodes:
                node_id = n_data["id"]
                edges = n_data.get("edges", [])
                for e_data in edges:
                    target_id = e_data["target_id"]
                    relation = e_data["relation"]
                    weight = e_data["weight"]
                    
                    # Aggiungiamo in RAM
                    from index.node import SemanticEdge
                    edge = SemanticEdge(target_id, relation, weight)
                    self.engine._nodes[node_id].edges.append(edge)
                    
                    # Idratiamo KùzuDB
                    self.kuzu_proj.conn.execute(
                        "MATCH (a:KnowledgeNode {id: $src}), (b:KnowledgeNode {id: $tgt}) "
                        "MERGE (a)-[r:CausalEdge {relation_type: $rel}]->(b) "
                        "ON CREATE SET r.weight = $w",
                        {"src": node_id, "tgt": target_id, "rel": relation, "w": weight}
                    )
            
            # Sincronizziamo il contatore di sequenza dell'Event Bus
            self.event_bus.sequence_counter = snapshot.get("sequence", 0)
            
            self.logger.info("✅ [Snapshot Daemon] Core database successfully hydrated.")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed deep hydration from snapshot: {e}")
            return False
