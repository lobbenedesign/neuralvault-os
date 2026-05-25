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
        
        # [v11.0 Performance Engine] Dynamic Schema Upgrade for Folders, Tags, Parent-Child & Full Result Cache
        for col_def in [
            "simulation_full_results JSON",
            "settings_used JSON",
            "status VARCHAR DEFAULT 'active'",
            "folder_path VARCHAR DEFAULT 'root'",
            "tags VARCHAR DEFAULT ''",
            "parent_id VARCHAR"
        ]:
            try:
                self.db.execute(f"ALTER TABLE decision_journal ADD COLUMN {col_def}")
            except Exception:
                pass # Silently pass if column already exists or not supported

    async def record_decision(self, simulation_results: Dict[str, Any], query: str, node_id: str, settings_used: Dict = None, parent_id: str = None, folder_path: str = None, tags: str = None, record_id: str = None) -> str:
        """Salva una simulazione nel journal."""
        import hashlib
        if record_id is None:
            record_id = str(uuid.uuid4())
        
        # Estrazione impatti medi
        impacts = {}
        confidences = {}
        
        # Se stiamo passando i risultati completi final_res
        if "simulation" in simulation_results:
            sim_data = simulation_results["simulation"]
            impacts = {n['id']: n['impact'] for n in sim_data.get("affected_nodes", [])}
            confidences = {n['id']: n['probability_positive'] for n in sim_data.get("affected_nodes", [])}
        else:
            impacts = {n['id']: n['impact'] for n in simulation_results.get("affected_nodes", [])}
            confidences = {n['id']: n['probability_positive'] for n in simulation_results.get("affected_nodes", [])}
        
        if settings_used is None:
            settings_used = {}
        if folder_path is None:
            folder_path = "root"
        if tags is None:
            tags = ""
            
        self.db.execute("""
            INSERT INTO decision_journal 
            (id, query, target_node_id, predicted_impacts, predicted_confidence, simulation_full_results, settings_used, folder_path, tags, parent_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            record_id, 
            query, 
            node_id, 
            json.dumps(impacts), 
            json.dumps(confidences),
            json.dumps(simulation_results),
            json.dumps(settings_used),
            folder_path,
            tags,
            parent_id
        ))
        
        # 🧬 [v10.2 Decision OS] Sync with decision_genome table
        try:
            global_conf = sum(confidences.values()) / len(confidences) if confidences else 1.0
            causal_hash = hashlib.sha256(json.dumps(impacts, sort_keys=True).encode()).hexdigest() if impacts else "sha256-empty"
            
            oracle_pred = {
                "impacts": impacts,
                "confidences": confidences,
                "affected_nodes_count": len(impacts)
            }
            self.db.record_decision(
                decision_id=record_id,
                question=query,
                oracle_prediction=oracle_pred,
                confidence=global_conf,
                causal_snapshot_hash=causal_hash
            )
        except Exception as e:
            self.logger.error(f"⚠️ Failed to record in decision_genome: {e}")
        
        # 🌑 [v9.0] Record for Shadow Mode Calibration
        shadow_preds = [{"node_id": nid, "expected_impact": imp} for nid, imp in impacts.items()]
        self.shadow_twin.record_simulation(record_id, shadow_preds)
        
        self.logger.info(f"⚖️ Decision Recorded: {record_id} for query '{query}'")
        return record_id

    async def recalibrate_causal_weights(self, target_node_id: str, actual_outcome_effect: float):
        """
        🧬 [v10.2 Decision OS] Causal Weight Recalibration
        Ricalibra i pesi delle relazioni causali che partono o arrivano al nodo target.
        formula: edge.weight = edge.weight * 0.9 + actual_outcome_effect * 0.1
        """
        node = self.engine.get_node(target_node_id)
        if not node:
            return
            
        recalibrated_count = 0
        causal_relations = ["causes", "prevents", "requires", "enables", "enhances", "supersedes", "synapse"]
        
        # 1. Ricalibra gli archi in uscita (Out-edges)
        for edge in node.edges:
            if edge.relation in causal_relations or str(edge.relation.value) in causal_relations:
                old_weight = edge.weight
                # Calcola il nuovo peso empirico
                edge.weight = round(old_weight * 0.9 + actual_outcome_effect * 0.1, 4)
                # Assicura il clamp nel range [0, 1.0]
                edge.weight = max(0.0, min(1.0, edge.weight))
                recalibrated_count += 1
                self.logger.info(f"🔄 Recalibrated Out-Edge: {node.id[:8]} --({edge.relation})--> {edge.target_id[:8]} ({old_weight} -> {edge.weight})")

        # 2. Ricalibra gli archi in entrata (In-edges)
        for other_node_id, other_node in list(self.engine._nodes.items()):
            if other_node_id == target_node_id:
                continue
            modified_other = False
            for edge in other_node.edges:
                if edge.target_id == target_node_id and (edge.relation in causal_relations or str(edge.relation.value) in causal_relations):
                    old_weight = edge.weight
                    edge.weight = round(old_weight * 0.9 + actual_outcome_effect * 0.1, 4)
                    edge.weight = max(0.0, min(1.0, edge.weight))
                    recalibrated_count += 1
                    modified_other = True
                    self.logger.info(f"🔄 Recalibrated In-Edge: {other_node.id[:8]} --({edge.relation})--> {node.id[:8]} ({old_weight} -> {edge.weight})")
            if modified_other:
                self.engine.storage_put(other_node)

        if recalibrated_count > 0:
            self.engine.storage_put(node)
            self.logger.info(f"✅ Recalibrated {recalibrated_count} causal edges related to {target_node_id[:8]} based on real outcome effect {actual_outcome_effect}")

    async def update_outcome(self, record_id: str, actual_outcome: str, accuracy: float):
        """Aggiorna un record con l'esito reale e l'accuratezza."""
        # 1. Update legacy decision_journal DuckDB table
        self.db.execute("""
            UPDATE decision_journal 
            SET actual_outcome = ?, 
                prediction_accuracy = ?, 
                outcome_recorded_at = now()
            WHERE id = ?
        """, (actual_outcome, accuracy, record_id))
        
        # 2. Update new v10.2 decision_genome DuckDB table
        try:
            real_outcome_data = {
                "outcome_text": actual_outcome,
                "accuracy": accuracy,
                "timestamp": datetime.utcnow().isoformat()
            }
            self.db.update_decision_outcome(record_id, real_outcome_data)
        except Exception as e:
            self.logger.error(f"⚠️ Failed to update decision_genome table: {e}")

        # 3. Retrieve target_node_id to trigger Causal Recalibration
        target_node_id = None
        try:
            res = self.db.fetchone("SELECT target_node_id FROM decision_journal WHERE id = ?", (record_id,))
            if res:
                target_node_id = res[0]
        except Exception as e:
            self.logger.error(f"⚠️ Failed to fetch target_node_id for recalibration: {e}")
            
        if target_node_id:
            # Assumiamo che l'accuratezza/esito influisca sulla calibrazione
            observed_effect = 1.0 if "success" in actual_outcome.lower() or accuracy >= 0.7 else 0.1
            await self.recalibrate_causal_weights(target_node_id, observed_effect)
            
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

    async def compute_brier_score(self) -> Dict[str, Any]:
        """
        🧭 [v10.2 Decision OS] Oracle Calibration Layer (Brier Score)
        Calcola il Brier Score complessivo sulle previsioni verificate del Decision Genome.
        BS = (1/N) * sum((predicted_confidence - observed_accuracy)^2)
        BS varia da 0.0 (previsione perfetta) a 1.0 (calibrazione pessima).
        Un punteggio < 0.25 indica un Oracolo ben calibrato.
        """
        try:
            decisions = self.db.get_decisions()
            verified = [d for d in decisions if d["real_outcome"] is not None]
            
            if not verified:
                return {
                    "brier_score": 0.0,
                    "calibration_status": "Uncalibrated (No historical data)",
                    "message": "In attesa di dati empirici per la calibrazione."
                }
                
            squared_errors = []
            for d in verified:
                pred_conf = d["confidence"]
                obs_acc = d["real_outcome"].get("accuracy", 1.0)
                squared_errors.append((pred_conf - obs_acc) ** 2)
                
            brier_score = sum(squared_errors) / len(squared_errors)
            
            # Calibrazione dell'Oracolo
            status = "Perfect Calibration"
            if brier_score > 0.40:
                status = "Highly Overconfident (Humility Override Active)"
            elif brier_score > 0.25:
                status = "Moderately Miscalibrated"
            elif brier_score > 0.10:
                status = "Well Calibrated"
                
            return {
                "brier_score": round(brier_score, 4),
                "calibration_status": status,
                "verified_count": len(verified),
                "humility_override_active": brier_score > 0.25
            }
        except Exception as e:
            self.logger.error(f"⚠️ Error computing Brier Score: {e}")
            return {"error": str(e), "brier_score": 1.0}
