import logging
import json
import os
import time
from typing import Dict, Any, List
from datetime import datetime

logger = logging.getLogger("ShadowTwin")

class ShadowModeTwin:
    """
    [v9.0] Shadow Mode Calibration Engine.
    Runs in the background to compare simulations with real outcomes.
    """
    
    def __init__(self, journal_path: str = "vault_data/shadow_journal.jsonl"):
        self.journal_path = journal_path
        os.makedirs(os.path.dirname(self.journal_path), exist_ok=True)
        self.stats = {"total_predictions": 0, "verified": 0, "accuracy": 0.0, "avg_error": 0.0}

    def record_simulation(self, simulation_id: str, predictions: List[Dict]):
        """Records a simulation for future calibration."""
        entry = {
            "simulation_id": simulation_id,
            "timestamp": time.time(),
            "predictions": predictions, # List of {node_id: str, expected_impact: float}
            "status": "PENDING"
        }
        with open(self.journal_path, "a") as f:
            f.write(json.dumps(entry) + "\n")
        logger.info(f"🌑 [Shadow Twin] Simulation {simulation_id[:8]} recorded for calibration.")

    def handle_real_outcome(self, node_id: str, real_impact: float):
        """
        Triggered when a real-world event affects a node.
        Compares with the 'most likely' simulation and calculates error.
        """
        if not os.path.exists(self.journal_path): return None
        
        best_match = None
        match_error = 100.0
        
        # Read pending simulations to find the one that predicted this node_id
        pending_sims = []
        try:
            with open(self.journal_path, "r") as f:
                for line in f:
                    sim = json.loads(line)
                    if sim.get("status") == "PENDING":
                        # Check if this simulation had a prediction for our node_id
                        for pred in sim.get("predictions", []):
                            if pred.get("node_id") == node_id:
                                # Calculate error: abs(predicted - real)
                                error = abs(pred.get("expected_impact", 0.0) - real_impact)
                                if error < match_error:
                                    match_error = error
                                    best_match = sim
        except Exception as e:
            logger.error(f"Error reading shadow journal: {e}")

        if best_match:
            logger.info(f"🌑 [Shadow Twin] Calibration Event! Matched {node_id[:8]} with Sim {best_match['simulation_id'][:8]}")
            
            self.stats["total_predictions"] += 1
            if match_error < 0.2: # Threshold for 'accurate'
                self.stats["verified"] += 1
            
            # Update running average error
            n = self.stats["total_predictions"]
            self.stats["avg_error"] = ((self.stats["avg_error"] * (n - 1)) + match_error) / n
            self.stats["accuracy"] = self.stats["verified"] / n
            
            # In a real scenario, we would mark the simulation as 'VERIFIED' in the file
            return {
                "status": "CALIBRATED",
                "accuracy": round(self.stats["accuracy"], 3),
                "error": round(match_error, 3),
                "avg_error": round(self.stats["avg_error"], 3)
            }
        
        return None

    def handle_event(self, event_type: str, payload: Dict[str, Any]):
        """Consumes Aegis events to trigger calibration."""
        if event_type in ["NODE_CREATED", "NODE_UPDATED"]:
            node_id = payload.get("id")
            # For calibration, we assume 'impact' is a proxy for how important a new node is.
            # In a real system, this would be a more complex measure.
            real_impact = 1.0 # Default impact for a newly created node
            self.handle_real_outcome(node_id, real_impact)

    def get_calibration_report(self) -> Dict:
        return self.stats
