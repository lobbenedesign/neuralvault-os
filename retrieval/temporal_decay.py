"""
retrieval/temporal_decay.py
──────────────────────────
Temporal Confidence Engine (v4.3.0)
Calcola l'obsolescenza dell'informazione basata sull'età della fonte.
"""

from datetime import datetime
import math
from typing import Dict

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
