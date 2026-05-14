import json
import uuid
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

class DecisionRecord(BaseModel):
    id: str
    timestamp: float
    query: str
    target_node_id: str
    decision_taken: Optional[str] = None
    predicted_impacts: Dict[str, float]
    predicted_confidence: Dict[str, float]
    actual_outcome: Optional[str] = None
    prediction_accuracy: Optional[float] = None
    outcome_recorded_at: Optional[float] = None

class SovereignDecisionJournal:
    """
    ⚖️ [v8.4] Decision Journal Engine.
    Traccia le previsioni dell'Oracolo e le confronta con la realtà.
    """
    def __init__(self, engine):
        self.engine = engine
        self.db = engine._prefilter
        self.logger = logging.getLogger("DecisionJournal")
        self._init_db()
        from retrieval.shadow_twin import ShadowModeTwin
        self.shadow_twin = ShadowModeTwin()

    def _init_db(self):
        """Crea la tabella per il journal se non esiste."""
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS decision_journal (
                id VARCHAR PRIMARY KEY,
                timestamp TIMESTAMP DEFAULT now(),
                query TEXT,
                target_node_id VARCHAR,
                decision_taken TEXT,
                predicted_impacts JSON,
                predicted_confidence JSON,
                actual_outcome TEXT,
                prediction_accuracy FLOAT,
                outcome_recorded_at TIMESTAMP
            )
        """)

    async def record_decision(self, simulation_results: Dict[str, Any], query: str, node_id: str) -> str:
        """Salva una simulazione nel journal."""
        record_id = str(uuid.uuid4())
        
        # Estrazione impatti medi
        impacts = {n['id']: n['impact'] for n in simulation_results.get("affected_nodes", [])}
        confidences = {n['id']: n['probability_positive'] for n in simulation_results.get("affected_nodes", [])}
        
        self.db.execute("""
            INSERT INTO decision_journal 
            (id, query, target_node_id, predicted_impacts, predicted_confidence)
            VALUES (?, ?, ?, ?, ?)
        """, (record_id, query, node_id, json.dumps(impacts), json.dumps(confidences)))
        
        # 🌑 [v9.0] Record for Shadow Mode Calibration
        shadow_preds = [{"node_id": nid, "expected_impact": imp} for nid, imp in impacts.items()]
        self.shadow_twin.record_simulation(record_id, shadow_preds)
        
        self.logger.info(f"⚖️ Decision Recorded: {record_id} for query '{query}'")
        return record_id

    async def update_outcome(self, record_id: str, actual_outcome: str, accuracy: float):
        """Aggiorna un record con l'esito reale e l'accuratezza."""
        self.db.execute("""
            UPDATE decision_journal 
            SET actual_outcome = ?, 
                prediction_accuracy = ?, 
                outcome_recorded_at = now()
            WHERE id = ?
        """, (actual_outcome, accuracy, record_id))
        self.logger.info(f"✅ Outcome Recorded for Decision: {record_id} (Accuracy: {accuracy})")

    async def get_history(self, limit: int = 20) -> List[Dict]:
        """Recupera lo storico delle decisioni."""
        res = self.db.execute("""
            SELECT id, query, target_node_id, prediction_accuracy, actual_outcome, timestamp 
            FROM decision_journal 
            ORDER BY timestamp DESC 
            LIMIT ?
        """, (limit,)).fetchall()
        
        return [
            {
                "id": r[0],
                "query": r[1],
                "target_node_id": r[2],
                "accuracy": r[3],
                "has_outcome": r[4] is not None,
                "date": r[5].strftime("%Y-%m-%d %H:%M")
            } for r in res
        ]

    async def compute_oracle_grade(self) -> Dict[str, Any]:
        """Calcola il voto dell'Oracolo basato sulle previsioni verificate."""
        res = self.db.execute("""
            SELECT AVG(prediction_accuracy), COUNT(*) 
            FROM decision_journal 
            WHERE prediction_accuracy IS NOT NULL
        """).fetchone()
        
        avg_acc = res[0] if res[0] is not None else 0.0
        count = res[1]
        
        grade = "C"
        if avg_acc >= 0.90: grade = "S"
        elif avg_acc >= 0.80: grade = "A"
        elif avg_acc >= 0.65: grade = "B"
        
        return {
            "average_accuracy": round(avg_acc, 2),
            "verified_decisions": count,
            "oracle_grade": grade,
            "status": "In Calibration" if count < 5 else "Stabilized"
        }
