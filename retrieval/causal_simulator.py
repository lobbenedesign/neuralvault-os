import logging
import json
from typing import List, Dict, Any, Optional
from index.node import RelationType

import numpy as np

class CausalSimulator:
    """
    🧪 [v8.1] Phase 7: The Predictive Sovereign Engine.
    Simula l'impatto di interventi tramite simulazioni probabilistiche Monte Carlo.
    """
    def __init__(self, engine):
        self.engine = engine
        self.logger = logging.getLogger("CausalSimulator")

    async def simulate_intervention(self, start_node_id: str, intervention_value: float = 1.0, depth: int = 3, iterations: int = 100) -> Dict[str, Any]:
        """
        [v8.1] Esegue una simulazione Monte Carlo per calcolare la distribuzione di probabilità degli impatti.
        """
        all_outcomes = []
        
        # 1. Recupera il sottografo interessato una volta sola per efficienza
        subgraph = self._get_relevant_subgraph(start_node_id, depth)
        
        # 2. Esegui N iterazioni stocastiche
        for _ in range(iterations):
            outcome = self._run_single_stochastic_pass(start_node_id, intervention_value, subgraph, depth)
            all_outcomes.append(outcome)
            
        # 3. Analisi statistica degli outcomes
        node_stats = {}
        affected_node_ids = set().union(*[o.keys() for o in all_outcomes])
        
        results = []
        for nid in affected_node_ids:
            impacts = [o.get(nid, 0.0) for o in all_outcomes]
            mean_impact = np.mean(impacts)
            std_impact = np.std(impacts)
            
            # Confidence Intervals (90%)
            worst_case = np.percentile(impacts, 5)
            best_case = np.percentile(impacts, 95)
            prob_positive = np.mean([i > 0 for i in impacts]) if mean_impact != 0 else 0.5
            
            node = self.engine.get_node(nid)
            results.append({
                "id": nid,
                "title": node.title if node else nid,
                "impact": round(float(mean_impact), 3),
                "std": round(float(std_impact), 3),
                "worst_case": round(float(worst_case), 3),
                "best_case": round(float(best_case), 3),
                "probability_positive": round(float(prob_positive), 3),
                "confidence": 0.9, # Placeholder for structural confidence
                "intensity": abs(float(mean_impact))
            })
            
        return {
            "root_id": start_node_id,
            "iterations": iterations,
            "affected_nodes": sorted(results, key=lambda x: x["intensity"], reverse=True)
        }

    def _get_relevant_subgraph(self, start_id: str, depth: int) -> Dict[str, List[Any]]:
        """Estrae i nodi e gli archi nel raggio d'azione."""
        subgraph = {}
        queue = [(start_id, 0)]
        visited = {start_id}
        
        while queue:
            nid, d = queue.pop(0)
            if d >= depth: continue
            
            node = self.engine.get_node(nid)
            if not node: continue
            
            subgraph[nid] = node.edges
            for edge in node.edges:
                if edge.target_id not in visited:
                    visited.add(edge.target_id)
                    queue.append((edge.target_id, d + 1))
        return subgraph

    def _run_single_stochastic_pass(self, start_id: str, start_val: float, subgraph: Dict, depth: int) -> Dict[str, float]:
        """Esegue un singolo passaggio di propagazione con rumore stocastico."""
        # Aggiungiamo rumore all'intervento iniziale
        noisy_start = start_val + np.random.normal(0, 0.05)
        impacts = {start_id: noisy_start}
        queue = [(start_id, noisy_start, 0)]
        
        while queue:
            nid, val, d = queue.pop(0)
            if d >= depth: continue
            
            edges = subgraph.get(nid, [])
            for edge in edges:
                # Rumore stocastico sul peso dell'arco (incertezza del legame)
                edge_noise = np.random.normal(0, 0.1)
                effective_weight = max(0, min(1, (edge.weight or 0.5) + edge_noise))
                
                effect = 0
                if edge.relation == RelationType.CAUSES:
                    effect = val * effective_weight
                elif edge.relation == RelationType.PREVENTS:
                    effect = -val * effective_weight
                elif edge.relation == RelationType.ENHANCES:
                    effect = val * (effective_weight * 0.5)
                
                if effect != 0:
                    impacts[edge.target_id] = impacts.get(edge.target_id, 0.0) + effect
                    queue.append((edge.target_id, effect, d + 1))
                    
        return impacts
