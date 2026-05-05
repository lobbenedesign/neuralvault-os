"""
retrieval/critique.py
──────────────────────
Sovereign Critique Engine (Self-RAG v4.2.0)
Valuta la qualità della risposta generata rispetto al contesto e alla query.
"""

import json
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class CritiqueResult:
    is_supported: bool
    relevance_score: float
    utility_score: float
    feedback: str
    suggested_action: str  # "deliver" | "refine" | "reject"

class SovereignCritiqueEngine:
    def __init__(self, engine):
        self.engine = engine

    async def audit_response(self, query: str, context: str, response: str) -> CritiqueResult:
        """
        Esegue un'analisi tripartita della risposta (Self-Critique).
        """
        orch = getattr(self.engine, 'orchestrator', None)
        if not orch:
            return CritiqueResult(True, 1.0, 1.0, "Orchestrator not ready.", "deliver")
        prompt = f"""
        Analizza criticamente la RISPOSTA generata per la DOMANDA basandoti sul CONTESTO fornito.
        
        DOMANDA: {query}
        CONTESTO: {context}
        RISPOSTA: {response}
        
        Valuta i seguenti punti in formato JSON:
        1. "grounding": la risposta è supportata dal contesto? (0-10)
        2. "relevance": la risposta risponde direttamente alla domanda? (0-10)
        3. "utility": la risposta è utile e professionale? (0-10)
        4. "critique": breve spiegazione dei punti deboli.
        5. "action": "deliver" (se tutto > 7), "refine" (se 4-7), "reject" (se < 4).
        """
        
        try:
            # Usiamo il Consensus per una critica imparziale
            critique_json = await orch.get_consensus_response(
                prompt, 
                "Critique Mode: Acting as a Sovereign Auditor.",
                format="json"
            )
            
            data = json.loads(critique_json)
            return CritiqueResult(
                is_supported=data.get("grounding", 0) > 7,
                relevance_score=data.get("relevance", 0) / 10.0,
                utility_score=data.get("utility", 0) / 10.0,
                feedback=data.get("critique", "Nessun feedback."),
                suggested_action=data.get("action", "deliver")
            )
        except Exception as e:
            print(f"⚠️ [Critique Error] Fallimento audit: {e}")
            return CritiqueResult(True, 1.0, 1.0, "Audit bypassed.", "deliver")
