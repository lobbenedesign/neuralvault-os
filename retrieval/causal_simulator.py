import logging
import json
from typing import List, Dict, Any, Optional
from index.node import RelationType

class CausalSimulator:
    """
    🧪 [v8.0] Phase 7: The "What-If" Engine.
    Simula l'impatto di interventi sui nodi propagando gli effetti attraverso archi causali.
    """
    def __init__(self, engine):
        self.engine = engine
        self.logger = logging.getLogger("CausalSimulator")

    async def simulate_intervention(self, start_node_id: str, intervention_value: float = 1.0, depth: int = 3) -> Dict[str, Any]:
        """
        Esegue una simulazione di propagazione partendo da un nodo 'intervenuto'.
        intervention_value: 1.0 (Attivazione/Aumento), -1.0 (Inibizione/Diminuzione).
        """
        impact_map = {start_node_id: {"impact": intervention_value, "confidence": 1.0, "reason": "DIRECT_INTERVENTION"}}
        queue = [(start_node_id, intervention_value, 1.0, 0)] # (node_id, value, confidence, current_depth)
        visited = {start_node_id}

        while queue:
            node_id, current_val, current_conf, current_depth = queue.pop(0)
            if current_depth >= depth: continue

            node = self.engine.get_node(node_id)
            if not node: continue

            for edge in node.edges:
                target_id = edge.target_id
                rel_type = edge.relation
                weight = edge.weight or 0.5
                
                # Calcolo effetto basato sul tipo di relazione
                effect = 0
                if rel_type == RelationType.CAUSES:
                    effect = current_val * weight
                elif rel_type == RelationType.PREVENTS:
                    effect = -current_val * weight
                elif rel_type == RelationType.ENHANCES:
                    effect = current_val * (weight * 0.5)
                
                if effect == 0: continue

                # Propagazione confidenza (decade con la distanza)
                new_conf = current_conf * weight * 0.9
                
                if target_id not in impact_map:
                    impact_map[target_id] = {"impact": 0.0, "confidence": 0.0, "reason": []}
                
                # Aggregazione impatti (Somma pesata)
                old_impact = impact_map[target_id]["impact"]
                impact_map[target_id]["impact"] += effect
                impact_map[target_id]["confidence"] = max(impact_map[target_id]["confidence"], new_conf)
                
                # Record the reasoning path
                reason = f"Propagated from {node_id} via {rel_type.value}"
                if isinstance(impact_map[target_id]["reason"], list):
                    impact_map[target_id]["reason"].append(reason)
                else:
                    impact_map[target_id]["reason"] = [reason]

                if target_id not in visited:
                    visited.add(target_id)
                    queue.append((target_id, effect, new_conf, current_depth + 1))

        # Finalizzazione dei risultati
        results = []
        for nid, data in impact_map.items():
            node = self.engine.get_node(nid)
            results.append({
                "id": nid,
                "title": node.title if node else nid,
                "impact": round(data["impact"], 3),
                "confidence": round(data["confidence"], 3),
                "sentiment": "POSITIVE" if data["impact"] > 0 else "NEGATIVE",
                "intensity": abs(data["impact"])
            })

        return {
            "root_id": start_node_id,
            "simulation_depth": depth,
            "affected_nodes": sorted(results, key=lambda x: x["intensity"], reverse=True)
        }
