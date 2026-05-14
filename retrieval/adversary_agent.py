import time
import json
import logging
import random
import re
import asyncio
from typing import List, Dict, Any, Optional
from index.node import RelationType
from utils.event_bus import NeuralEventType

logger = logging.getLogger("SovereignAdversary")

class SovereignAdversaryAgent:
    """
    😈 [AD-007] THE SCEPTIC - Devil's Advocate Agent.
    Purpose: Automated Popperian Falsification.
    It monitors new knowledge and actively seeks contradictions to test hypothesis strength.
    """
    def __init__(self, engine, orchestrator=None):
        self.engine = engine
        self.orchestrator = orchestrator
        self.identity = {
            "id": "AD-007",
            "name": "The Sceptic",
            "role": "Devil's Advocate",
            "archetype": "guardian",
            "motto": "Nullius in verba"
        }
        self.pos = {"x": -5000000.0, "y": 3000000.0, "z": -5000000.0}
        self.status = "Hunting for inconsistencies..."
        self.target_node = None
        self.active_debates = {}

    def get_capability_ld(self):
        return {
            "@context": "https://neuralvault.io/context/agent",
            "@type": "SovereignAgent",
            "id": self.identity["id"],
            "name": self.identity["name"],
            "role": self.identity["role"],
            "capabilities": ["Popperian Falsification", "Hypothesis Challenging", "Adversarial Auditing"],
            "archetype": self.identity["archetype"]
        }

    async def challenge_hypothesis(self, node_id: str, hypothesis_text: str):
        """
        🚀 Innesca un attacco logico a una nuova ipotesi.
        1. Cerca prove contrastanti nel Vault (Semantic Tension).
        2. Se non bastano, innesca una ricerca web mirata alla smentita.
        3. Genera un 'Adversarial Report' per la Supreme Court.
        """
        self.status = f"Falsifying node {node_id[:8]}..."
        logger.info(f"😈 [Adversary] Challenging node {node_id}: {hypothesis_text[:50]}...")

        # 1. Recupero evidenze contrastanti (Contradiction Search)
        # Usiamo il kernel per cercare nodi con bassa similarità ma pertinenza tematica
        results = await self.engine.query(hypothesis_text, k=10)
        
        contradictions = []
        for res in results:
            if res.node.id == node_id: continue
            # Se la similarità è media (0.6-0.8) ma il testo sembra divergere, è un potenziale conflitto
            if 0.5 < res.final_score < 0.82:
                contradictions.append(res)

        # 2. Sintesi Adversariale (LLM)
        adversarial_model = self.engine.orchestrator.settings.get("audit", "llama3.2:3b")
        
        context = "\n".join([f"- [{r.node.id}] {r.node.text[:200]}" for r in contradictions])
        prompt = f"""
        ROLE: Devil's Advocate (Popperian Falsifier).
        HYPOTHESIS: "{hypothesis_text}"
        
        EVIDENCES:
        {context}
        
        TASK:
        1. Trova le debolezze logiche nell'ipotesi.
        2. Usa le evidenze fornite per creare un contro-argomento.
        3. Se mancano dati, suggerisci cosa cercare per smentire questa tesi.
        
        Return JSON: {{"weaknesses": ["..."], "counter_argument": "...", "falsification_score": 0.0-1.0}}
        """
        
        try:
            raw_response = await self.engine.orchestrator.get_consensus_response(prompt, "Sovereign Adversary", target_model=adversarial_model)
            json_match = re.search(r'\{.*\}', raw_response, re.DOTALL)
            report = json.loads(json_match.group(0)) if json_match else {"weaknesses": ["Unverifiable"], "falsification_score": 0.5}
        except Exception as e:
            logger.error(f"Adversary LLM Error: {e}")
            report = {"weaknesses": ["Analysis engine timeout"], "falsification_score": 0.3}

        # 3. Escalation alla Supreme Court se lo score è alto
        if report.get("falsification_score", 0) > 0.6:
            await self._escalate_to_court(node_id, report)
        
        # 4. Registrazione dell'evento nell'Aegis e nel Lab Audit
        event_entry = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "agent": "AD-007",
            "action": "ADVERSARIAL_CHALLENGE",
            "node_id": node_id,
            "target_id": node_id,
            "reasoning": f"Il Sospettoso ha rilevato {len(report.get('weaknesses', []))} debolezze logiche nell'ipotesi.",
            "motivation": report.get("counter_argument", ""),
            "metadata": report,
            "wisdom_recorded": False
        }
        
        # Log to Aegis
        self.engine._prefilter.log_event(
            event_type="ADVERSARIAL_CHALLENGE",
            node_id=node_id,
            description=event_entry["reasoning"],
            metadata=report
        )
        
        # Log to Lab Orchestrator (Supreme Court UI)
        if self.orchestrator and hasattr(self.orchestrator, 'mission_history'):
            self.orchestrator.mission_history.insert(0, event_entry)
        
        self.status = "Hunting for inconsistencies..."
        return report

    async def _escalate_to_court(self, node_id: str, report: Dict):
        """Invia il report alla Corte Suprema per il Quorum Decisionale."""
        event_data = {
            "node_id": node_id,
            "adversary_report": report,
            "urgency": "HIGH",
            "timestamp": time.time()
        }
        await self.engine.events.emit(
            NeuralEventType.COURT_REQUIRED,
            event_data
        )
        logger.warning(f"⚖️ [Adversary] Case escalated to Supreme Court for node {node_id}")

    def calculate_movement(self, nodes: Dict):
        """Movimento orbitale e saltellante per indicare attività di scansione."""
        if not nodes: return None
        
        # Effetto "Orbitante" attorno al centro della Nebula
        t = time.time() * 0.2
        radius = 8000000.0
        tx = math.cos(t) * radius
        ty = math.sin(t * 0.5) * 2000000.0
        tz = math.sin(t) * radius
        
        self.pos['x'] += (tx - self.pos['x']) * 0.1
        self.pos['y'] += (ty - self.pos['y']) * 0.1
        self.pos['z'] += (tz - self.pos['z']) * 0.1
        
        return None

import math
