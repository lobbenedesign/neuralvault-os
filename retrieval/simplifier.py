import logging
from typing import List, Dict

logger = logging.getLogger("Simplifier")

class SimplificationDaemon:
    """
    [v9.0] Complexity Reduction Engine.
    Monitors the swarm and the vault to suggest cleanup or merging of agents/nodes.
    """
    
    def __init__(self, orchestrator):
        self.orch = orchestrator

    def audit_swarm_complexity(self) -> List[Dict]:
        """Identifies redundant agents or low-merit agents."""
        suggestions = []
        if not hasattr(self.orch, 'trust_network'):
            return []
            
        rewards = self.orch.trust_network.reward_manager.rewards
        for agent_id, data in rewards.items():
            if data['merit'] < 0.3:
                suggestions.append({
                    "target": agent_id,
                    "action": "DEACTIVATE",
                    "reason": f"Agent merit ({data['merit']}) below critical threshold. Performance is subpar."
                })
        
        return suggestions

    def audit_graph_redundancy(self, nodes: List[Dict]) -> List[Dict]:
        """Identifies potentially redundant nodes (high semantic similarity > 0.95)."""
        suggestions = []
        if len(nodes) < 2: return []
        
        # Sort nodes by importance or access count to find "master" nodes
        # For simplicity, we just compare all-vs-all in small batches
        processed = set()
        for i, node_a in enumerate(nodes[:100]): # Limit to first 100 for performance
            if node_a.get('id') in processed: continue
            
            for node_b in nodes[i+1:200]:
                if node_b.get('id') in processed: continue
                
                # Use simple keyword overlap or (if available) cosine similarity
                # Here we assume 'nodes' list contains metadata with pre-calculated vectors 
                # or we use the engine to find similar nodes.
                
                # Fallback: simple text overlap for this daemon's audit
                text_a = node_a.get('text', '').lower()
                text_b = node_b.get('text', '').lower()
                
                # Check for high overlap or near identity
                if text_a == text_b or (len(text_a) > 50 and text_a in text_b) or (len(text_b) > 50 and text_b in text_a):
                    suggestions.append({
                        "target_id": node_b.get('id'),
                        "source_id": node_a.get('id'),
                        "action": "MERGE",
                        "reason": "Semantic Redundancy: Content is nearly identical to another node."
                    })
                    processed.add(node_b.get('id'))
        
        return suggestions

    def get_cleanup_plan(self, nodes: List[Dict] = []) -> Dict:
        swarm_cleanup = self.audit_swarm_complexity()
        graph_cleanup = self.audit_graph_redundancy(nodes)
        
        return {
            "status": "READY",
            "swarm_suggestions": swarm_cleanup,
            "graph_suggestions": graph_cleanup,
            "total_issues": len(swarm_cleanup) + len(graph_cleanup),
            "message": f"Simplifier found {len(swarm_cleanup)} swarm issues and {len(graph_cleanup)} graph redundancies."
        }
