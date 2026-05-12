import json
import logging
import uuid
import threading
import asyncio
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
            import torch
            from index.turboquant import NativeKMeans
            
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
                    device = 'mps' if torch.backends.mps.is_available() else 'cpu'
                    kmeans = NativeKMeans(n_clusters=n_clusters, n_iter=15, device=device)
                    t_vectors = torch.from_numpy(np.array(orphan_vectors)).float().to(device)
                    kmeans.fit(t_vectors)
                    labels = kmeans.assign(t_vectors).cpu().numpy()
                    
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
                    # [v8.4] Generazione Titolo Temporaneo Euristico per visibilità immediata
                    temp_title = f"GALAXY: {cluster[0][:8]}"
                    try:
                        node_data = self.engine.get_node(cluster[0])
                        if node_data and hasattr(node_data, 'title') and node_data.title:
                            temp_title = f"NUCLEO: {node_data.title[:25]}"
                    except: pass

                    self.engine._prefilter.execute(
                        "INSERT INTO neural_communities (id, level, title, node_count) VALUES (?, 1, ?, ?)",
                        (comm_id, temp_title, len(cluster))
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
        [v8.4] Robust Fallback: Se l'LLM fallisce, genera titoli basati su parole chiave.
        """
        # Recuperiamo comunità senza riassunto
        pending = self.engine._prefilter.execute(
            "SELECT id FROM neural_communities WHERE summary IS NULL"
        ).fetchall()

        if not pending: return
        
        self.logger.info(f"🏛️ [H-RAG] Avvio sintesi per {len(pending)} Galassie...")
        
        # Limitiamo a 2 sintesi parallele per maggiore stabilità su macchine locali
        semaphore = asyncio.Semaphore(2)
        
        async def _summarize_single(comm_id):
            async with semaphore:
                try:
                    # Recuperiamo i testi dei nodi in questa comunità
                    nodes = self.engine._prefilter.query_nodes(f"community_id = '{comm_id}'", limit=20)
                    if not nodes: return

                    # Estrazione sicura del testo e dei titoli per fallback
                    texts = []
                    fallback_titles = []
                    for n in nodes:
                        m = n.get('metadata', {})
                        node_text = m.get('text', "")
                        node_title = m.get('title', "")
                        
                        if node_title: fallback_titles.append(node_title)
                        
                        if not node_text:
                            full_node = self.engine.get_node(n['id'])
                            if full_node:
                                node_text = full_node.text
                        
                        if node_text:
                            texts.append(node_text[:500]) # Ridotto per evitare overflow di contesto
                    
                    if not texts: return
                    combined_text = "\n---\n".join(texts)
                    
                    # Generazione Fallback immediata (in caso di crash LLM)
                    default_title = fallback_titles[0] if fallback_titles else f"Cluster {comm_id}"
                    default_summary = "Analisi tematica basata sulla densità di nodi correlati nel Vault."
                    
                    prompt = f"""### TASK: Generate a Sovereign Intelligence Report for this Concept Galaxy.
### DATA:
{combined_text}

### OUTPUT FORMAT (JSON ONLY):
{{
  "title": "Evocative title (max 5 words)",
  "summary": "1-2 sentences summarizing the core knowledge",
  "key_concepts": ["concept1", "concept2", "concept3"]
}}
"""
                    response = ""
                    try:
                        # [v8.4] Use engine.orchestrator which is the correct reference for the NeuralLabOrchestrator
                        model = getattr(self.engine, 'settings', {}).get("chat", "llama3.2:3b")
                        if hasattr(self.engine, 'orchestrator'):
                            response = await self.engine.orchestrator.ask_fast(prompt, model=model)
                        else:
                            # Fallback if orchestrator is not yet linked
                            self.logger.warning("⚠️ Orchestrator not found, using direct LLM call fallback.")
                            response = ""
                    except Exception as llm_err:
                        self.logger.error(f"⚠️ LLM Error for {comm_id}: {llm_err}")
                        response = ""

                    if response:
                        try:
                            # Pulizia JSON avanzata
                            clean_json = response.strip()
                            if "```json" in clean_json:
                                clean_json = clean_json.split("```json")[1].split("```")[0].strip()
                            elif "{" in clean_json:
                                clean_json = clean_json[clean_json.find("{"):clean_json.rfind("}")+1]
                            
                            try:
                                data = json.loads(clean_json)
                            except json.JSONDecodeError:
                                # Tentativo di riparazione JSON
                                repaired = clean_json.strip()
                                if repaired.endswith(','): repaired = repaired[:-1]
                                open_braces = repaired.count('{') - repaired.count('}')
                                open_brackets = repaired.count('[') - repaired.count(']')
                                if repaired.count('"') % 2 != 0: repaired += '"'
                                repaired += ']' * max(0, open_brackets)
                                repaired += '}' * max(0, open_braces)
                                data = json.loads(repaired)
                            
                            title = data.get('title', default_title)
                            summary = data.get('summary', default_summary)
                            concepts = data.get('key_concepts', ["Vault", "Knowledge"])
                            
                            self.engine._prefilter.execute(
                                "UPDATE neural_communities SET title = ?, summary = ?, key_concepts = ? WHERE id = ?",
                                (title, summary, json.dumps(concepts), comm_id)
                            )
                            self.logger.info(f"🏛️ Galassia '{title}' sintetizzata con successo.")
                            return
                        except Exception as parse_err:
                            self.logger.warning(f"⚠️ JSON Parse error for {comm_id}, using heuristic extraction: {parse_err}")
                            # Heuristic extraction if JSON fails but response exists
                            if len(response) > 50:
                                self.engine._prefilter.execute(
                                    "UPDATE neural_communities SET title = ?, summary = ? WHERE id = ?",
                                    (default_title, response[:250] + "...", comm_id)
                                )
                                return

                    # SE TUTTO FALLISCE (LLM Offline o Timeout): Fallback Sovrano
                    self.logger.warning(f"🛡️ [Archivista] Fallback Sovrano attivato per {comm_id}")
                    self.engine._prefilter.execute(
                        "UPDATE neural_communities SET title = ?, summary = ? WHERE id = ?",
                        (f"NUCLEO: {default_title[:30]}", default_summary, comm_id)
                    )

                except Exception as e:
                    self.logger.error(f"❌ Errore critico nel riassunto {comm_id}: {e}")

        # Lanciamo i task
        tasks = [_summarize_single(cid[0]) for cid in pending]
        await asyncio.gather(*tasks)
        self.logger.info("✅ [H-RAG] Ciclo di sintesi completato.")

    def hierarchical_search(self, query: str, limit: int = 5) -> List[Dict]:
        """
        Ricerca Gerarchica Avanzata: Cerca tra titoli, riassunti e concetti chiave delle Galassie.
        """
        try:
            # [v6.1] Infallible Hierarchical Matching
            search_query = """
                SELECT id, title, summary, node_count 
                FROM neural_communities 
                WHERE title ILIKE ? 
                   OR summary ILIKE ? 
                   OR CAST(key_concepts AS VARCHAR) ILIKE ?
                ORDER BY (title ILIKE ?) DESC, node_count DESC
                LIMIT ?
            """
            pattern = f"%{query}%"
            # In DuckDB, per cercare in JSON castiamo a VARCHAR o usiamo funzioni specifiche.
            # Qui usiamo il cast per semplicità e compatibilità.
            comm_res = self.engine._prefilter.execute(
                search_query, 
                (pattern, pattern, pattern, pattern, limit)
            ).fetchall()
            
            results = []
            for cid, title, summary, count in comm_res:
                results.append({
                    "id": cid,
                    "type": "community",
                    "title": title or "Galassia Senza Nome",
                    "text": summary or "Nessun riassunto disponibile.",
                    "node_count": count,
                    "score": 0.95
                })
            
            return results
        except Exception as e:
            self.logger.error(f"⚠️ [Hierarchical Search Error] {e}")
            return []
