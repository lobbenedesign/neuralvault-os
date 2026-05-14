import time
import math
from typing import Dict, List, Optional
import logging

logger = logging.getLogger("EpistemicEngine")

class EpistemicCalculator:
    """
    [v9.0] Composite Epistemic Integrity Engine.
    Calculates a multi-dimensional confidence score for knowledge nodes.
    """
    
    def __init__(self, engine=None):
        self.engine = engine
        from retrieval.temporal_decay import TemporalConfidenceEngine
        from retrieval.shadow_twin import ShadowModeTwin
        self.temporal_engine = TemporalConfidenceEngine()
        self.shadow_twin = ShadowModeTwin()

    def calculate_node_score(self, node: Any, web_results: List[Any] = []) -> Dict[str, float]:
        """
        Calcola lo score composito (0.0 - 1.0) per un nodo.
        """
        # 1. Freshness Score (Tempo)
        created_at = node.metadata.get("created_at", 0) if hasattr(node, 'metadata') else 0
        topic = node.metadata.get("topic_type", "general") if hasattr(node, 'metadata') else "general"
        freshness = self.temporal_engine.compute_confidence(datetime.fromtimestamp(created_at), topic)
        
        # 2. Causal Density (Connessioni)
        # Più archi entranti/uscenti ha un nodo, più è 'ancorato' nella conoscenza
        edges_count = len(node.edges) if hasattr(node, 'edges') else 0
        density = min(1.0, edges_count / 10.0) 
        
        # 3. Consensus Score (Modelli)
        # Se abbiamo risultati web, quanto concordano con il testo del nodo?
        consensus = 0.5
        if web_results:
            # Semplificazione: se il forager ha trovato risultati, alziamo la fiducia
            consensus = 0.8
            
        # 4. Formal Verification (Z3)
        # Se il nodo è parte di una contraddizione risolta o verificata
        z3_score = 1.0
        if hasattr(node, 'metadata') and node.metadata.get("z3_verified"):
            z3_score = 1.0
        elif hasattr(node, 'metadata') and node.metadata.get("has_conflict"):
            z3_score = 0.2

        # 5. 🌑 [v9.0] SHADOW CALIBRATION (Closed-Loop Feedback)
        # Applichiamo la correzione basata sulla precisione storica dell'Oracolo
        shadow_stats = self.shadow_twin.get_calibration_report()
        accuracy = shadow_stats.get("accuracy", 1.0)
        # Se l'accuratezza è bassa (es. 0.5), penalizziamo lo score finale per essere più cauti
        shadow_factor = 0.5 + (accuracy * 0.5) 

        # Calcolo Pesato
        final_score = (
            (freshness * 0.3) + 
            (density * 0.2) + 
            (consensus * 0.2) + 
            (z3_score * 0.3)
        ) * shadow_factor
        
        return {
            "final_score": round(final_score, 3),
            "freshness": freshness,
            "density": density,
            "consensus": consensus,
            "z3_verified": z3_score == 1.0,
            "shadow_calibration": round(shadow_factor, 2)
        }

    def batch_audit(self, nodes: List[Dict]) -> List[Dict]:
        """Audits a list of nodes and returns scores."""
        results = []
        for n in nodes:
            score = self.calculate_node_score(
                node_id=n['id'],
                created_at=n.get('created_at', time.time()),
                in_degree=n.get('in_degree', 0),
                is_formally_verified=n.get('is_verified', False),
                agent_consensus=n.get('consensus', 1.0)
            )
            results.append(score)
        return results

    def generate_knowledge_fingerprint(self, node_id: str, supporting_nodes: List[Dict]) -> str:
        """
        🧬 [v9.1] EPISTEMIC FINGERPRINTING.
        Generates a unique hash based on the IDs and timestamps of supporting nodes.
        Used to detect if the knowledge foundation has shifted.
        """
        import hashlib
        # Combine ID and timestamp of each supporting node
        foundation = "|".join([f"{n['id']}_{n.get('updated_at', n.get('created_at', 0))}" for n in sorted(supporting_nodes, key=lambda x: x['id'])])
        fingerprint = hashlib.sha256(f"{node_id}:{foundation}".encode()).hexdigest()
        logger.info(f"🧬 Fingerprint generated for {node_id}: {fingerprint[:8]}...")
        return fingerprint

    def validate_fingerprint(self, current_fingerprint: str, node_id: str, current_supporting_nodes: List[Dict]) -> bool:
        """Checks if the current foundation matches the stored fingerprint."""
        new_fingerprint = self.generate_knowledge_fingerprint(node_id, current_supporting_nodes)
        is_valid = (current_fingerprint == new_fingerprint)
        if not is_valid:
            logger.warning(f"⚠️ [EPISTEMIC BREAK] Fingerprint mismatch for {node_id}! Knowledge foundation has shifted.")
        return is_valid
