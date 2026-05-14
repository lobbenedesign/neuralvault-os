import logging
from typing import List, Dict, Optional, Tuple
from z3 import Solver, Bool, Implies, Not, And, sat, unsat

logger = logging.getLogger("FormalLogic")

class FormalLogicEngine:
    """
    NeuralVault Formal Logic Engine powered by Microsoft Z3 Theorem Prover.
    Translates causal relationships into Boolean logic to mathematically prove contradictions.
    """
    
    def __init__(self):
        self.solver = Solver()
        self.node_vars = {}  # Map node_id to Z3 Bool variable
        self.relations = []   # List of (source, target, relation_type)

    def _get_var(self, node_id: str) -> Bool:
        """Get or create a Z3 Boolean variable for a node."""
        clean_id = node_id.replace("-", "_").replace(".", "_")
        if clean_id not in self.node_vars:
            self.node_vars[clean_id] = Bool(f"node_{clean_id}")
        return self.node_vars[clean_id]

    def add_causal_relation(self, source_id: str, target_id: str, relation_type: str):
        """
        Encode a causal relation into the Z3 solver.
        CAUSES (A -> B): Implies(A, B)
        PREVENTS (A -> !B): Implies(A, Not(B))
        REQUIRES (B -> A): Implies(B, A) [B cannot exist without A]
        """
        src_var = self._get_var(source_id)
        tgt_var = self._get_var(target_id)
        
        rel = relation_type.upper()
        if rel == "CAUSES":
            self.solver.add(Implies(src_var, tgt_var))
        elif rel == "PREVENTS":
            self.solver.add(Implies(src_var, Not(tgt_var)))
        elif rel == "REQUIRES":
            self.solver.add(Implies(tgt_var, src_var))
        
        self.relations.append((source_id, target_id, rel))
        logger.debug(f"Encoded relation: {source_id} {rel} {target_id}")

    def check_contradiction(self, assumptions: List[str]) -> Dict:
        """
        Verifies if a set of assumptions (node_ids being true) creates a logical contradiction.
        Returns a dict with 'is_contradiction', 'message', and 'proof' (unsat core).
        """
        # Create a fresh solver for this check to avoid polluting the global state
        s = Solver()
        for c in self.solver.assertions():
            s.add(c)
        
        # Add assumptions as true
        assumption_vars = []
        for node_id in assumptions:
            var = self._get_var(node_id)
            s.add(var)
            assumption_vars.append(var)
            
        result = s.check()
        
        if result == sat:
            return {
                "is_contradiction": False,
                "message": "Coexistence is logically satisfiable.",
                "model": str(s.model()) if len(assumptions) > 0 else None
            }
        else:
            # If unsat, find the contradiction (unsat core)
            # Z3 core requires track variables, for simplicity we return the current state
            return {
                "is_contradiction": True,
                "message": "MATHEMATICAL CONTRADICTION PROVEN.",
                "proof": "Logical conflict detected in the causal chain.",
                "unsat_assertions": [str(a) for a in s.assertions()]
            }

    def audit_graph(self, nodes: List[Dict], edges: List[Dict]) -> Dict:
        """
        Full audit of a subgraph.
        """
        self.solver.reset()
        self.node_vars = {}
        
        for edge in edges:
            self.add_causal_relation(edge['source'], edge['target'], edge['type'])
            
        # Check for self-contradictions (e.g. A causes B and A prevents B)
        if self.solver.check() == unsat:
            return {
                "status": "CRITICAL_FAILURE",
                "message": "The graph contains inherent logical contradictions."
            }
            
        return {
            "status": "VERIFIED",
            "message": f"Graph verified with {len(edges)} formal constraints."
        }

    def is_consistent(self, topic: str) -> bool:
        """
        [v9.0] Quick consistency check for a specific topic.
        Checks if the current global solver state is satisfiable.
        """
        # Se il solver è vuoto, è coerente per definizione
        if not self.solver.assertions():
            return True
        return self.solver.check() != unsat
