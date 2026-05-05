import logging
import asyncio
from typing import List, Dict, Optional
from index.node import RelationType
import numpy as np

logger = logging.getLogger("NeuralVault-Contradiction")

class ContradictionMapper:
    """
    ⚖️ [CONTRADICTION MAPPER]
    Identifica proattivamente le incongruenze logiche nel Vault.
    Crea archi di tipo CONTRADICTS tra nodi che si smentiscono a vicenda.
    """
    def __init__(self, engine, orchestrator):
        self.engine = engine
        self.orchestrator = orchestrator
        self.vault = engine

    async def scan_for_contradictions(self, limit: int = 50):
        """
        Esegue una scansione profonda cercando coppie di nodi ad alta similarità
        ma potenziale disaccordo logico.
        """
        logger.info("🔍 [Contradiction] Avvio scansione integrità logica...")
        
        # 1. Trova coppie candidate (High Similarity)
        # Nota: In un sistema reale useremmo un'operazione batch su HNSW.
        # Qui simuliamo con i nodi più recenti.
        all_nodes = list(self.vault._nodes.values())
        if len(all_nodes) < 2: return
        
        candidates = []
        # Strategia: Prendi gli ultimi N nodi e confrontali con il resto
        recent_nodes = sorted(all_nodes, key=lambda x: x.created_at, reverse=True)[:limit]
        
        for node_a in recent_nodes:
            if not node_a.vector is not None: continue
            
            # Cerca nel Vault nodi simili a node_a
            results = await self.engine.query(node_a.text, top_k=5)
            for res in results:
                node_b = res.node
                if node_a.id == node_b.id: continue
                
                # Se sono molto simili (> 0.85) ma non sono già collegati come contraddizioni
                if res.dense_score > 0.85:
                    has_contradiction = any(e.relation == RelationType.CONTRADICTS and e.target_id == node_b.id for e in node_a.edges)
                    if not has_contradiction:
                        candidates.append((node_a, node_b))

        logger.info(f"⚖️ [Contradiction] Identificate {len(candidates)} coppie candidate per l'audit.")
        
        for n_a, n_b in candidates:
            await self._audit_pair(n_a, n_b)

    async def _audit_pair(self, node_a, node_b):
        """Usa l'LLM per verificare se esiste una contraddizione reale."""
        prompt = f"""
        CONTESTO A: {node_a.text[:500]}
        CONTESTO B: {node_b.text[:500]}

        Questi due testi si contraddicono logicamente o fattualmente?
        Rispondi ESCLUSIVAMENTE con un JSON nel formato:
        {{
            "contradiction": true/false,
            "reason": "breve spiegazione",
            "confidence": 0.0-1.0
        }}
        """
        
        try:
            # Usiamo un modello leggero per l'audit rapido
            raw_response = await self.orchestrator.get_consensus_response(
                prompt, 
                "Contradiction Auditor",
                target_model=self.engine.settings.get("court_judge_1")
            )
            
            import json
            import re
            json_match = re.search(r'\{.*\}', raw_response, re.DOTALL)
            if not json_match: return
            
            result = json.loads(json_match.group(0))
            
            if result.get("contradiction") and result.get("confidence", 0) > 0.7:
                logger.warning(f"🚨 [Contradiction Found] {node_a.id[:8]} vs {node_b.id[:8]}: {result['reason']}")
                
                # Crea l'arco di contraddizione (Rosso nella Nebula)
                self.vault.add_relation(node_a.id, node_b.id, RelationType.CONTRADICTS, weight=result['confidence'])
                
                # Log nel Ledger per la Timeline
                self.engine._prefilter.log_event(
                    event_type="CONTRADICTION_DETECTED",
                    topic_cluster="Logic Integrity",
                    node_id=node_a.id,
                    description=f"Contraddizione rilevata con {node_b.id[:8]}: {result['reason']}"
                )
        except Exception as e:
            logger.error(f"❌ [Contradiction Audit Fail] {e}")
