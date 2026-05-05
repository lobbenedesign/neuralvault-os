import json
import logging
import uuid
import threading
from typing import List, Dict, Optional, Any
from pathlib import Path

class CommunityEngine:
    """
    🌌 NeuralVault v6.0: Hierarchical GraphRAG Engine.
    Handles graph partitioning, community summarization, and hierarchical retrieval.
    """
    def __init__(self, engine):
        self.engine = engine
        self.logger = logging.getLogger("CommunityEngine")
        self._lock = threading.Lock()
        self.is_clustering = False

    def build_graph_and_cluster(self):
        """
        [v6.1] Infallible Clustering Engine: Hybrid Graph + K-Means strategy.
        Analizza i collegamenti semantici e raggruppa i nodi in Galassie Concettuali.
        Se i link sono scarsi, utilizza il clustering vettoriale per garantire risultati.
        """
        def _execute_hybrid_clustering():
            import numpy as np
            from sklearn.cluster import KMeans
            
            # 1. Recupero ID e Metadati (Ottimizzato: Usiamo cache RAM se possibile)
            all_ids = self.engine._prefilter.filter("1=1")
            if not all_ids: return []
            
            self.logger.info(f"🌌 [H-RAG] Inizio analisi su {len(all_ids)} nodi...")
            
            adj = {}
            nodes_with_vectors = []
            
            # Recupero dati in batch per performance
            for nid in all_ids:
                node = self.engine.get_node(nid) # Usa RAM-first logic
                if node:
                    if hasattr(node, 'edges') and node.edges:
                        adj[nid] = [e.target_id for e in node.edges if e.weight > 0.15] # Soglia più permissiva
                    
                    if node.vector is not None:
                        nodes_with_vectors.append(nid)

            # --- STADIO 1: Connected Components (Graph-based) ---
            visited = set()
            graph_communities = []
            for start_node in all_ids:
                if start_node not in visited and start_node in adj:
                    cluster = []
                    queue = [start_node]
                    visited.add(start_node)
                    while queue:
                        curr = queue.pop(0)
                        cluster.append(curr)
                        for neighbor in adj.get(curr, []):
                            # [FIX] neighbor in all_ids invece di neighbor in adj per non spezzare il grafo
                            if neighbor not in visited and neighbor in all_ids:
                                visited.add(neighbor)
                                queue.append(neighbor)
                    if len(cluster) >= 3: # Minimo 3 nodi per una galassia strutturale
                        graph_communities.append(cluster)

            # --- STADIO 2: Semantic Clustering (K-Means Fallback) ---
            # Identifichiamo nodi orfani o cluster troppo piccoli
            orphan_ids = [nid for nid in nodes_with_vectors if nid not in visited]
            
            semantic_communities = []
            if len(orphan_ids) > 10:
                self.logger.info(f"🧠 [H-RAG] Rilevati {len(orphan_ids)} nodi orfani. Avvio clustering semantico...")
                
                # Estraiamo i vettori degli orfani
                orphan_vectors = []
                valid_orphan_ids = []
                for oid in orphan_ids:
                    node = self.engine.get_node(oid)
                    if node and node.vector is not None:
                        orphan_vectors.append(node.vector)
                        valid_orphan_ids.append(oid)
                
                if orphan_vectors:
                    # Numero dinamico di cluster (1 ogni 50 nodi, max 30)
                    n_clusters = min(max(3, len(orphan_vectors) // 50), 30)
                    kmeans = KMeans(n_clusters=n_clusters, n_init=10, random_state=42)
                    labels = kmeans.fit_predict(np.array(orphan_vectors))
                    
                    temp_clusters = {}
                    for idx, label in enumerate(labels):
                        if label not in temp_clusters: temp_clusters[label] = []
                        temp_clusters[label].append(valid_orphan_ids[idx])
                    
                    for cluster in temp_clusters.values():
                        if len(cluster) >= 2: semantic_communities.append(cluster)

            return graph_communities + semantic_communities

        with self._lock:
            if self.is_clustering: return
            self.is_clustering = True

        try:
            # Esecuzione tramite Sandbox per sicurezza
            audit = self.engine.sandbox.run_simulation("Hybrid Hierarchical Clustering", _execute_hybrid_clustering)
            
            if audit.success:
                # [v6.1] Utilizziamo direttamente il risultato validato dalla Sandbox
                communities = audit.result
                if not communities:
                    self.logger.warning("🌌 [H-RAG] Nessuna Galassia identificata dalla simulazione.")
                    return
                
                # Pulizia atomica
                self.engine._prefilter.execute("DELETE FROM neural_communities")
                self.engine._prefilter.execute("UPDATE vault_metadata SET community_id = NULL")

                # Salvataggio nel DB
                created_count = 0
                for i, cluster in enumerate(communities):
                    comm_id = f"comm_{uuid.uuid4().hex[:6]}"
                    for nid in cluster:
                        self.engine._prefilter.execute(
                            "UPDATE vault_metadata SET community_id = ? WHERE id = ?",
                            (comm_id, nid)
                        )
                    self.engine._prefilter.execute(
                        "INSERT INTO neural_communities (id, level, node_count) VALUES (?, 1, ?)",
                        (comm_id, len(cluster))
                    )
                    created_count += 1
                
                self.logger.info(f"✅ Clustering completato: {created_count} Galassie identificate.")
            else:
                self.logger.error(f"🚨 Clustering scartato dal Supervisor Sandbox.")
                
        except Exception as e:
            self.logger.error(f"❌ Errore critico nel clustering: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.is_clustering = False

    async def generate_community_summaries(self):
        """
        L'Archivista analizza ogni Galassia e genera una sintesi strutturata.
        """
        # Recuperiamo comunità senza riassunto
        pending = self.engine._prefilter.execute(
            "SELECT id FROM neural_communities WHERE summary IS NULL"
        ).fetchall()

        for (comm_id,) in pending:
            # Recuperiamo i testi dei nodi in questa comunità
            nodes = self.engine._prefilter.query_nodes(f"community_id = '{comm_id}'", limit=30)
            if not nodes: continue

            # Estrazione sicura del testo dai metadati JSON con fallback su Deep Hydration
            texts = []
            for n in nodes:
                m = n.get('metadata', {})
                node_text = m.get('text', "")
                
                # [Deep Hydration Fallback] Se il testo manca nei metadati DuckDB, caricalo dal Kernel
                if not node_text:
                    full_node = self.engine.get_node(n['id'])
                    if full_node:
                        node_text = full_node.text
                
                if node_text:
                    texts.append(node_text[:600])
            
            if not texts: continue
            combined_text = "\n---\n".join(texts)
            
            prompt = f"""### TASK: Generate a Sovereign Intelligence Report for this Concept Galaxy.
### DATA:
{combined_text}

### OUTPUT FORMAT:
Respond ONLY with a JSON object:
{{
  "title": "Short evocative title (max 5 words)",
  "summary": "Comprehensive summary of the shared knowledge",
  "key_concepts": ["concept1", "concept2", "concept3"]
}}
"""
            try:
                # Usiamo l'LLM di sistema (AUDIT o CHAT)
                model = getattr(self.engine, 'settings', {}).get("chat_model", "llama3.2")
                # Chiamata simulata/placeholder per l'integrazione con l'orchestratore
                # In una vera implementazione useremmo self.engine.lab.ask(...)
                response = await self.engine.agent007_lab.ask_fast(prompt, model=model)
                
                # Pulizia della risposta (a volte gli LLM aggiungono markdown)
                clean_json = response.strip()
                if "```json" in clean_json:
                    clean_json = clean_json.split("```json")[1].split("```")[0].strip()
                
                data = json.loads(clean_json)
                
                self.engine._prefilter.execute(
                    "UPDATE neural_communities SET title = ?, summary = ?, key_concepts = ? WHERE id = ?",
                    (data['title'], data['summary'], json.dumps(data['key_concepts']), comm_id)
                )
                self.logger.info(f"🏛️ Galassia '{data['title']}' riassunta con successo.")

            except Exception as e:
                self.logger.error(f"❌ Errore nel riassunto comunità {comm_id}: {e}")

    def hierarchical_search(self, query: str, limit: int = 5) -> List[Dict]:
        """
        Ricerca Gerarchica: Prima trova le comunità rilevanti, poi i nodi atomici.
        """
        # 1. Cerchiamo tra i riassunti delle comunità
        # Nota: In un'implementazione completa useremmo embedding sui riassunti.
        # Qui usiamo una ricerca testuale su DuckDB per velocità.
        try:
            comm_res = self.engine._prefilter.execute(
                "SELECT id, title, summary FROM neural_communities WHERE summary ILIKE ? LIMIT 3",
                (f"%{query}%",)
            ).fetchall()
            
            results = []
            for cid, title, summary in comm_res:
                results.append({
                    "id": cid,
                    "type": "community",
                    "title": title,
                    "text": summary,
                    "score": 0.95
                })
            
            return results
        except:
            return []
