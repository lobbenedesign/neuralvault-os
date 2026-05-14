"""
retrieval/temporal_decay.py
──────────────────────────
Temporal Confidence Engine (v4.3.0)
Calcola l'obsolescenza dell'informazione basata sull'età della fonte.
"""

from datetime import datetime
import math
import logging
from typing import Dict

logger = logging.getLogger("TemporalDecay")

class TemporalConfidenceEngine:
    """
    Ogni nodo ha una confidence che decade basata sull'età dell'informazione.
    Differente dall'Ebbinghaus Decay che si basa sull'uso.
    """
    
    DECAY_RATES = {
        "technology": 0.15,    # Tech cambia veloce: -15%/mese
        "science": 0.03,       # Scienza stabile: -3%/mese
        "history": 0.001,      # Storia non cambia: -0.1%/mese
        "prices": 0.50,        # Prezzi cambiano subito: -50%/mese
        "code": 0.10,          # Codice si evolve: -10%/mese
        "general": 0.05        # Default: -5%/mese
    }
    
    def compute_confidence(self, source_date: datetime, topic_type: str = "general") -> float:
        """
        Calcola la fiducia temporale residua (0.0 - 1.0).
        """
        if not source_date: return 1.0
        
        decay_rate = self.DECAY_RATES.get(topic_type, 0.05)
        
        # Età in mesi
        delta = datetime.now() - source_date
        months_old = delta.days / 30.0
        
        # Confidence decade esponenzialmente: C = e^(-r * t)
        confidence = math.exp(-decay_rate * months_old)
        
        return round(max(0.1, confidence), 3)

    def get_visual_status(self, confidence: float) -> Dict[str, str]:
        """
        [v4.3.1] Dual Decay Visual Mapping.
        Ritorna la configurazione visiva per il nodo (bordo).
        """
        if confidence < 0.3: 
            return {"color": "#ef4444", "status": "EXPIRED", "border": 3}
        if confidence < 0.6: 
            return {"color": "#f59e0b", "status": "STALE", "border": 2}
        if confidence < 0.8:
            return {"color": "#3b82f6", "status": "VERIFIED", "border": 1}
        return {"color": "#10b981", "status": "FRESH", "border": 0}

    def get_warning_label(self, confidence: float) -> str:
        status = self.get_visual_status(confidence)["status"]
        if status == "EXPIRED": return "🔴 OBSOLETO"
        if status == "STALE": return "🟡 POTENZIALMENTE DATATO"
        return "🟢 ATTUALE"

class GlobalHealthScanner:
    """
    [v9.0] Proactive Vault Health Monitor.
    Periodically scans the entire knowledge base to detect epistemic decay.
    """
    def __init__(self, engine, orchestrator=None):
        self.engine = engine
        self.orchestrator = orchestrator
        self.calculator = TemporalConfidenceEngine()
        self.last_scan_time = 0
        self.critical_nodes = []

    async def run_full_scan(self) -> Dict:
        """Scans all nodes and returns a health report."""
        import time
        logger.info("🌡️ [Health Scanner] Starting global epistemic audit...")
        
        nodes = list(self.engine._nodes.values())
        if not nodes: return {"status": "EMPTY"}
        
        total_conf = 0
        expired_count = 0
        stale_count = 0
        self.critical_nodes = []
        
        for node in nodes:
            # Determine topic type from metadata if available
            topic = node.metadata.get("topic_type", "general") if hasattr(node, 'metadata') else "general"
            created_at = node.metadata.get("created_at", time.time()) if hasattr(node, 'metadata') else time.time()
            
            conf = self.calculator.compute_confidence(datetime.fromtimestamp(created_at), topic)
            total_conf += conf
            
            if conf < 0.3:
                expired_count += 1
                self.critical_nodes.append(node.id)
            elif conf < 0.6:
                stale_count += 1
                
        avg_health = total_conf / len(nodes)
        
        report = {
            "timestamp": time.time(),
            "avg_health": round(avg_health, 3),
            "expired_nodes": expired_count,
            "stale_nodes": stale_count,
            "total_nodes": len(nodes),
            "status": "CRITICAL" if avg_health < 0.5 or expired_count > (len(nodes) * 0.1) else "HEALTHY"
        }
        
        # Log to Aegis Event Bus
        self.engine._prefilter.log_event(
            event_type="VAULT_HEALTH_REPORT",
            topic_cluster="System Maintenance",
            description=f"Global Health: {report['avg_health']*100}%. Found {expired_count} expired and {stale_count} stale nodes.",
            metadata=report
        )
        
        # If critical, notify the orchestrator to trigger Skywalker
        if report["status"] == "CRITICAL" and self.orchestrator:
            await self._trigger_emergency_refresh()
            
        return report

    async def _trigger_emergency_refresh(self):
        """Asks Skywalker to prioritize refreshing critical nodes."""
        if not self.critical_nodes: return
        
        target_id = self.critical_nodes[0] # Focus on the first critical node for now
        logger.warning(f"🚨 [Health] Vault health critical! Triggering emergency refresh for {target_id}")
        
        # This will be picked up by Skywalker in the next lab cycle
        if self.orchestrator:
            self.orchestrator.mission_history.insert(0, {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "agent": "SE-007",
                "action": "HEALTH_INTERVENTION_REQUIRED",
                "target_id": target_id,
                "reasoning": "Node confidence below 30%. Epistemic integrity at risk."
            })
