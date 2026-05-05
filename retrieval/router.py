"""
retrieval/router.py
───────────────────
Adaptive Query Router (v4.2.0)
Decide la strategia di recupero ottimale analizzando l'intento e le caratteristiche della query.
"""

from enum import Enum
from dataclasses import dataclass
import re

class RetrievalStrategy(Enum):
    HYBRID = "hybrid"           # Default: HNSW + BM25 + Graph
    RELATIONAL = "relational"   # Priorità al Grafo (lookup entità)
    LEXICAL = "lexical"         # Priorità a BM25 (termini tecnici, codice)
    DENSE = "dense"             # Priorità a HNSW (concetti astratti)
    SPECULATIVE = "speculative" # Genera ipotesi prima di cercare (Gap #4)

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

    def route(self, query: str) -> RoutingDecision:
        query_l = query.lower()
        
        # 1. Rilevamento Codice / Tecnico (LEXICAL)
        if any(re.search(p, query) for p in self.code_patterns) or len(query_l.split()) < 3:
            return RoutingDecision(
                strategy=RetrievalStrategy.LEXICAL,
                alpha=0.25, # Spostamento aggressivo verso il lessicale
                use_reranker=True
            )
            
        # 2. Rilevamento Astratto / Concettuale (DENSE)
        if any(k in query_l for k in self.abstract_keywords) or len(query_l) > 100:
            return RoutingDecision(
                strategy=RetrievalStrategy.DENSE,
                alpha=0.85, # Spostamento verso il semantico puro
                use_reranker=True
            )

        # 3. Rilevamento Relazionale (RELATIONAL)
        if any(k in query_l for k in self.relational_keywords):
            return RoutingDecision(
                strategy=RetrievalStrategy.RELATIONAL,
                alpha=0.5,
                use_reranker=False
            )
            
        # 4. Rilevamento Comparativo / Complesso (HYBRID + Multi)
        if any(k in query_l for k in ["differenza", "confronto", "migliore", "perché"]):
            return RoutingDecision(
                strategy=RetrievalStrategy.HYBRID,
                alpha=0.6,
                use_reranker=True,
                multi_query=True
            )
            
        # 5. Default: Hybrid bilanciato
        return RoutingDecision(
            strategy=RetrievalStrategy.HYBRID,
            alpha=0.75,
            use_reranker=True
        )
