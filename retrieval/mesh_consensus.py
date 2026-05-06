"""
retrieval/mesh_consensus.py
──────────────────────────────
[v7.5] Cross-Vault Weighted Consensus Engine
Implementa la meritocrazia epistemica tra vault nella Mesh.
Il peso del voto di un vault dipende dalla densità di prove (nodi, fonti) 
che possiede su un determinato topic.
"""

import logging
from typing import List, Dict, Optional
from dataclasses import dataclass

logger = logging.getLogger("NeuralVault-MeshConsensus")

@dataclass
class WeightedVote:
    vault_id: str
    verdict: str # "SUPPORTS", "CONTRADICTS", "UNCERTAIN"
    weight: float
    evidence_count: int

@dataclass
class ConsensusResult:
    claim: str
    consensus_score: float
    verdict: str
    participating_vaults: int
    total_epistemic_weight: float

class MeshConsensusEngine:
    """
    Gestisce il consenso distribuito pesato per competenza.
    """
    def __init__(self, engine):
        self.engine = engine

    async def compute_epistemic_weight(self, vault_id: str, topic: str, stats: Dict) -> float:
        """
        Calcola il peso epistemico di un vault (locale o remoto) su un topic.
        Il peso è basato su:
        - node_count (quantità)
        - primary_sources (qualità)
        - recency (freschezza)
        - coherence (assenza di contraddizioni interne)
        """
        node_count = stats.get("node_count", 0)
        source_density = stats.get("source_density", 0.0) # Rapporto paper/nodi
        recency_score = stats.get("recency_score", 0.5)
        internal_coherence = stats.get("coherence", 1.0)
        
        # Algoritmo: Ponderazione delle dimensioni
        weight = (
            0.4 * min(node_count / 100, 1.0) +      # Saturazione a 100 nodi
            0.3 * source_density +                  # Più fonti primarie = più peso
            0.2 * recency_score +                   # Più recente = più peso
            0.1 * internal_coherence                # Più coerente = più peso
        )
        
        return max(0.1, weight) # Minimo garantito per ogni partecipante attivo

    async def run_sovereign_consensus(self, claim: str, peer_responses: List[Dict]) -> ConsensusResult:
        """
        Calcola il verdetto finale basato sui voti pesati dei peer.
        """
        if not peer_responses:
            return ConsensusResult(claim, 0.0, "UNCERTAIN", 0, 0.0)
            
        votes = []
        for resp in peer_responses:
            # Calcolo peso del peer basato sulle statistiche fornite nella risposta
            weight = await self.compute_epistemic_weight(
                resp.get("peer_id", "unknown"),
                claim,
                resp.get("stats", {})
            )
            
            votes.append(WeightedVote(
                vault_id=resp.get("peer_id"),
                verdict=resp.get("verdict", "UNCERTAIN"),
                weight=weight,
                evidence_count=resp.get("stats", {}).get("node_count", 0)
            ))
            
        # Aggregazione voti pesati
        support_weight = sum(v.weight for v in votes if v.verdict == "SUPPORTS")
        contradict_weight = sum(v.weight for v in votes if v.verdict == "CONTRADICTS")
        total_weight = sum(v.weight for v in votes)
        
        if total_weight == 0:
            return ConsensusResult(claim, 0.0, "UNCERTAIN", 0, 0.0)
            
        # Punteggio finale normalizzato
        consensus_score = (support_weight - contradict_weight) / total_weight
        
        # Verdetto
        if consensus_score > 0.6: verdict = "VERIFIED"
        elif consensus_score < -0.6: verdict = "REFUTED"
        else: verdict = "DISPUTED"
        
        logger.info(f"⚖️ [MeshConsensus] Verdetto per '{claim[:30]}...': {verdict} (Score: {consensus_score:.2f})")
        
        return ConsensusResult(
            claim=claim,
            consensus_score=consensus_score,
            verdict=verdict,
            participating_vaults=len(votes),
            total_epistemic_weight=total_weight
        )
