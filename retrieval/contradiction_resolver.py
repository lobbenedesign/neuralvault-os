import logging
import json
import re
from typing import List, Dict, Optional
from index.node import RelationType

logger = logging.getLogger("NeuralVault-Resolver")

class ContradictionResolver:
    """
    ⚖️ [CONTRADICTION RESOLVER]
    Agente decisionale della Corte Suprema. 
    Propone sintesi per risolvere i conflitti logici identificati nel Vault.
    """
    def __init__(self, engine, orchestrator):
        self.engine = engine
        self.orchestrator = orchestrator

    async def resolve_pending_contradictions(self):
        """Scansiona gli archi CONTRADICTS e tenta una risoluzione via sintesi."""
        contradictions = []
        for node in self.engine._nodes.values():
            for edge in node.edges:
                if edge.relation == RelationType.CONTRADICTS:
                    contradictions.append((node.id, edge.target_id))

        logger.info(f"⚖️ [Resolver] Trovate {len(contradictions)} contraddizioni da risolvere.")
        
        for id_a, id_b in contradictions[:5]: # Risoluzione batch limitata
            await self._synthesize_resolution(id_a, id_b)

    async def _synthesize_resolution(self, id_a, id_b):
        node_a = self.engine._nodes.get(id_a)
        node_b = self.engine._nodes.get(id_b)
        if not node_a or not node_b: return

        prompt = f"""
        CONFLITTO RILEVATO:
        TESI A: {node_a.text}
        TESI B: {node_b.text}

        Compito: Agisci come Arbitro della Corte Suprema. Crea una SINTESI che risolva la contraddizione 
        o spieghi perché entrambi i punti di vista sono validi in contesti diversi.
        La sintesi deve essere oggettiva e tecnica.
        
        Rispondi ESCLUSIVAMENTE con un JSON:
        {{
            "resolution_text": "la sintesi finale...",
            "action": "MERGE" | "REPLACE_A" | "REPLACE_B" | "KEEP_BOTH_WITH_EXPLANATION",
            "confidence": 0.0-1.0
        }}
        """
        
        try:
            response = await self.orchestrator.get_consensus_response(prompt, "Arbitrator")
            
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if not json_match: return
            result = json.loads(json_match.group(0))
            
            if result.get("confidence", 0) > 0.8:
                logger.info(f"✅ [Resolver] Risoluzione sintetizzata per {id_a[:8]} vs {id_b[:8]}")
                
                # Crea il nodo di Risoluzione
                res_node = await self.engine.upsert_text(
                    result["resolution_text"],
                    metadata={
                        "type": "resolution",
                        "resolved_nodes": [id_a, id_b],
                        "strategy": result["action"]
                    }
                )
                
                # Collega i nodi originali alla risoluzione
                self.engine.add_relation(id_a, res_node.id, RelationType.RESOLVED_BY)
                self.engine.add_relation(id_b, res_node.id, RelationType.RESOLVED_BY)
                
                # Rimuovi l'arco di contraddizione (optional, or keep for history)
                # Qui lo teniamo ma cambiamo il peso o lo stato
                
                self.engine._prefilter.log_event(
                    "CONTRADICTION_RESOLVED",
                    "Logic",
                    res_node.id,
                    f"Risoluzione generata tra {id_a[:8]} e {id_b[:8]}."
                )
                
        except Exception as e:
            logger.error(f"❌ [Resolver Error] {e}")
