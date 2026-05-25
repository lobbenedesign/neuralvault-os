"""
retrieval/router.py
───────────────────
Adaptive Query Router & Hydra Query Engine (v10.1)
Gestisce l'instradamento delle query e il recupero parallelo multi-head.
"""

import asyncio
import logging
import time
import re
from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Optional, Any

class RetrievalStrategy(Enum):
    HYBRID = "hybrid"           # Default: HNSW + BM25 + Graph
    RELATIONAL = "relational"   # Priorità al Grafo (lookup entità)
    LEXICAL = "lexical"         # Priorità a BM25 (termini tecnici, codice)
    DENSE = "dense"             # Priorità a HNSW (concetti astratti)
    SPECULATIVE = "speculative" # Genera ipotesi prima di cercare (Gap #4)
    FACTUAL_BYPASS = "factual_bypass" # [v10.2 Decision OS] Bypass rapido per query fattuali/dirette

@dataclass
class RoutingDecision:
    strategy: RetrievalStrategy
    alpha: float                # Peso HNSW (0.0 - 1.0)
    use_reranker: bool
    multi_query: bool = False
    
class AdaptiveQueryRouter:
    def __init__(self):
        # Keyword per rilevamento intenti
        self.code_patterns = [
            r"def\s+", r"class\s+", r"import\s+", r"__init__", r"self\.", 
            r"async\s+", r"await\s+", r"function", r"const\s+",
            r"rust", r"cargo", r"fn\s+", r"pub\s+fn", r"impl\s+",
            r"c\+\+", r"std::", r"vector<", r"template<"
        ]
        self.abstract_keywords = [
            "concetto", "filosofia", "teoria", "opinione", "sentimento",
            "percezione", "essenza", "significato", "visione", "futuro"
        ]
        self.relational_keywords = [
            "chi", "chi è", "relazione", "collegamento", "connesso", 
            "autore", "entità", "appartiene", "padre", "figlio"
        ]
        self.causal_keywords = [
            "what if", "cosa succede se", "previsione", "simulazione", 
            "se cambio", "se modifico", "se riduco", "se aumento", 
            "conseguenze", "impatto di", "scenario", "cosa accadrebbe"
        ]
        self.factual_keywords = [
            "ip", "password", "chiave", "token", "valore", "config", 
            "configurazione", "porta", "host", "email", "telefono", 
            "indirizzo", "data", "quando", "dove"
        ]

    def route(self, query: str) -> RoutingDecision:
        query_l = query.lower()
        
        # Check per bypass fattuale immediato
        is_code = any(re.search(p, query) for p in self.code_patterns)
        is_causal = any(k in query_l for k in self.causal_keywords)
        is_factual = (any(k in query_l for k in self.factual_keywords) or len(query_l.split()) <= 2) and not is_code
        
        if is_factual and not is_causal:
            return RoutingDecision(strategy=RetrievalStrategy.FACTUAL_BYPASS, alpha=0.1, use_reranker=False)

        if is_code or len(query_l.split()) < 3:
            return RoutingDecision(strategy=RetrievalStrategy.LEXICAL, alpha=0.25, use_reranker=True)
        if any(k in query_l for k in self.abstract_keywords) or len(query_l) > 100:
            return RoutingDecision(strategy=RetrievalStrategy.DENSE, alpha=0.85, use_reranker=True)
        if any(k in query_l for k in self.relational_keywords):
            return RoutingDecision(strategy=RetrievalStrategy.RELATIONAL, alpha=0.5, use_reranker=False)
        if any(k in query_l for k in ["differenza", "confronto", "migliore", "perché"]):
            return RoutingDecision(strategy=RetrievalStrategy.HYBRID, alpha=0.6, use_reranker=True, multi_query=True)
        return RoutingDecision(strategy=RetrievalStrategy.HYBRID, alpha=0.75, use_reranker=True)

class HydraQueryEngine:
    """
    🏺 [v10.2] THE HYDRA (Intelligent Multi-Head Parallel Retrieval)
    Classifica gli intenti delle query e lancia solo le teste necessarie per massimizzare le performance.
    """
    def __init__(self, engine):
        self.engine = engine
        self.router = AdaptiveQueryRouter()
        self.logger = logging.getLogger("HydraQueryEngine")
        
        # Componenti specializzati (v10.1)
        from retrieval.sparse_neural import SparseNeuralEncoder
        self.sparse_head = SparseNeuralEncoder(engine)

    async def query(self, query: str, top_k: int = 10) -> Dict[str, Any]:
        start_time = time.time()
        
        # 1. Classificazione degli intenti ed instradamento intelligente
        decision = self.router.route(query)
        self.logger.info(f"🚦 [Query Router] Decision: {decision.strategy} (alpha={decision.alpha})")
        
        # Selezione dinamica delle teste basata sull'intento per risparmiare RAM e cicli CPU
        tasks = []
        heads_triggered = []
        
        if decision.strategy == RetrievalStrategy.FACTUAL_BYPASS:
            # Bypass Fattuale: solo Dense HNSW (MRL 256D) + DuckDB Claims velocissimo
            tasks.append(self._head_dense(query, top_k))
            tasks.append(self._head_claims(query, top_k))
            heads_triggered = ["Dense (MRL 256D Bypass)", "Claims Factual Fetch"]
        elif decision.strategy == RetrievalStrategy.LEXICAL:
            # Ricerca Lessicale/Tecnica: Sparse Neural + Claims
            tasks.append(self._head_expansion(query, top_k))
            tasks.append(self._head_claims(query, top_k))
            heads_triggered = ["Sparse (Expansion)", "Claims Audit"]
        elif decision.strategy == RetrievalStrategy.DENSE:
            # Ricerca Semantica/Astratta: Dense HNSW + Galaxies
            tasks.append(self._head_dense(query, top_k))
            tasks.append(self._head_galaxies(query, top_k))
            heads_triggered = ["Dense (HNSW)", "Galaxies"]
        elif decision.strategy == RetrievalStrategy.RELATIONAL:
            # Ricerca Relazionale/Strutturale: Kùzu Graph + Dense HNSW
            tasks.append(self._head_causal(query, top_k))
            tasks.append(self._head_dense(query, top_k))
            heads_triggered = ["Causal Graph", "Dense (HNSW)"]
        else:
            # Ricerca Complessa/Ibrida: Attiva tutte le teste parallele
            tasks = [
                self._head_dense(query, top_k),
                self._head_expansion(query, top_k),
                self._head_causal(query, top_k),
                self._head_claims(query, top_k),
                self._head_galaxies(query, top_k)
            ]
            heads_triggered = ["Dense", "Sparse", "Causal", "Claims", "Galaxies"]
        
        # Esecuzione parallela massiva ristretta
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filtriamo eccezioni
        valid_results = [r for r in results if isinstance(r, list)]
        
        # 2. RRF Fusion (Reciprocal Rank Fusion)
        fused = self._reciprocal_rank_fusion(valid_results, top_k)
        
        return {
            "query": query,
            "results": fused,
            "telemetry": {
                "duration": time.time() - start_time,
                "heads_active": len(valid_results),
                "heads_triggered": heads_triggered,
                "strategy": str(decision.strategy.value)
            }
        }

    async def _head_dense(self, query: str, k: int) -> List[Dict]:
        """Ricerca HNSW pura."""
        try:
            # Assumiamo che engine.query supporti i parametri top_k e use_sparse
            return self.engine.query(query, top_k=k, use_sparse=False)
        except: return []

    async def _head_expansion(self, query: str, k: int) -> List[Dict]:
        """Ricerca via Espansione Neurale (SPLADE Simulation)."""
        try:
            sparse_vec = await self.sparse_head.encode(query)
            if not sparse_vec: return []
            return self.engine.query(query, top_k=k, use_dense=False, sparse_vector=sparse_vec)
        except: return []

    async def _head_causal(self, query: str, k: int) -> List[Dict]:
        """Ricerca Relazionale integrata via KùzuDB."""
        try:
            import sys
            api_mod = sys.modules.get("api")
            kuzu_proj = getattr(api_mod, "kuzu_projection", None)
            if kuzu_proj:
                # Estraiamo i nodi connessi adiacenti tramite Cypher query veloce
                result = kuzu_proj.conn.execute(
                    "MATCH (a:KnowledgeNode)-[r:CausalEdge]->(b:KnowledgeNode) "
                    "WHERE a.id ILIKE $q OR b.id ILIKE $q OR a.title ILIKE $q "
                    "RETURN DISTINCT b.id, b.title LIMIT $k",
                    {"q": f"%{query}%", "k": k}
                )
                nodes = []
                while result.has_next():
                    row = result.get_next()
                    nodes.append({"id": row[0], "text": row[1], "source": "kuzu_graph"})
                return nodes
            return []
        except Exception as e:
            self.logger.debug(f"Kùzu search head error: {e}")
            return []

    async def _head_claims(self, query: str, k: int) -> List[Dict]:
        """Ricerca nelle asserzioni verificate (wiki_claims)."""
        try:
            if hasattr(self.engine, '_prefilter'):
                res = self.engine._prefilter.execute(
                    "SELECT page_id, claim_text FROM wiki_claims WHERE claim_text ILIKE ? LIMIT ?",
                    (f"%{query}%", k)
                ).fetchall()
                return [{"id": r[0], "text": r[1], "source": "wiki_claims"} for r in res]
            return []
        except: return []

    async def _head_galaxies(self, query: str, k: int) -> List[Dict]:
        """Ricerca nei riassunti delle comunità/galassie."""
        try:
            return []
        except: return []

    def _reciprocal_rank_fusion(self, search_results: List[List[Dict]], k: int, c: int = 60) -> List[Dict]:
        """Fonde più liste di risultati mantenendo la pertinenza (Algorithm: RRF)."""
        scores = {}
        all_nodes = {}
        
        for result_list in search_results:
            for rank, node in enumerate(result_list):
                node_id = str(node.get("id") or node.get("node_id", ""))
                if not node_id: continue
                
                all_nodes[node_id] = node
                scores[node_id] = scores.get(node_id, 0) + 1.0 / (c + rank + 1)
        
        sorted_ids = sorted(scores.keys(), key=lambda x: scores[x], reverse=True)
        
        final = []
        for nid in sorted_ids[:k]:
            n = all_nodes[nid]
            n["rrf_score"] = scores[nid]
            final.append(n)
            
        return final
