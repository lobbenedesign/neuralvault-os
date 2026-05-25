import logging
import json
import uuid
import copy
import time
from typing import Dict, Any, List, Optional, Set
from index.node import VaultNode

class SovereignVaultTwin:
    """
    🌓 [v9.1] Sovereign Differential Twin (Copy-on-Write).
    Cognitive sandbox with near-zero initial memory impact.
    Uses deltas instead of full deep copies.
    """
    def __init__(self, engine):
        self.engine = engine
        self.logger = logging.getLogger("VaultTwin")
        self.active_twins = {} # twin_id -> TwinState

    async def create_twin(self) -> str:
        """
        🚀 [v9.1 CoW] Creates a differential twin.
        Instead of deep copying, it references the parent engine and tracks deltas.
        """
        twin_id = f"TWIN-{uuid.uuid4().hex[:6]}"
        
        # Inizializzazione Differenziale
        self.active_twins[twin_id] = {
            "parent_nodes": self.engine._nodes, # Reference (Read-only)
            "delta_nodes": {},                   # Nodes added or modified in the twin
            "deleted_ids": set(),                # Nodes deleted in the twin
            "mutations": [],
            "created_at": time.time()
        }
        
        self.logger.info(f"🌓 CoW Twin Created: {twin_id}. Initial impact: 0 nodes.")
        return twin_id

    def get_node(self, twin_id: str, node_id: str) -> Optional[VaultNode]:
        """Recupera un nodo dal twin (CoW logic)."""
        twin = self.active_twins.get(twin_id)
        if not twin: return None
        
        # 1. Check if deleted
        if node_id in twin["deleted_ids"]: return None
        
        # 2. Check in deltas (modified/added)
        if node_id in twin["delta_nodes"]:
            return twin["delta_nodes"][node_id]
            
        # 3. Check in parent
        return twin["parent_nodes"].get(node_id)

    async def simulate_ingestion(self, twin_id: str, text: str, source: str) -> Dict[str, Any]:
        """Simula l'ingestione nel Twin Differenziale."""
        if twin_id not in self.active_twins:
            return {"error": "Twin non trovato."}
            
        twin = self.active_twins[twin_id]
        vector = self.engine._embed_text(text)
        
        sim_node = VaultNode(
            id=f"SIM-{uuid.uuid4().hex[:6]}",
            text=text,
            vector=vector,
            metadata={"source": source, "simulated": True}
        )
        
        # Calcolo impatto combinando Parent + Delta (Ignorando Deleted)
        potential_links = []
        
        # Scan parent (filtered)
        for nid, node in twin["parent_nodes"].items():
            if nid in twin["deleted_ids"] or nid in twin["delta_nodes"]: continue
            if self._quick_sim_check(vector, node, potential_links): break

        # Scan delta
        for nid, node in twin["delta_nodes"].items():
            self._quick_sim_check(vector, node, potential_links)
        
        # Registrazione Delta
        twin["delta_nodes"][sim_node.id] = sim_node
        twin["mutations"].append({"action": "ADD", "node_id": sim_node.id})
        
        return {
            "twin_id": twin_id,
            "new_node_id": sim_node.id,
            "potential_links": potential_links[:10],
            "status": "Simulated (Differential)"
        }

    def _quick_sim_check(self, vector, node, links):
        if node.vector is not None and len(node.vector) > 0:
            sim = self._cosine_similarity(vector, node.vector)
            if sim > 0.75:
                links.append({"id": node.id, "title": node.metadata.get("title", "Nodo"), "similarity": float(sim)})
        return len(links) > 20 # Cap per performance

    def _cosine_similarity(self, v1, v2):
        import numpy as np
        return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-9)

    async def commit_twin(self, twin_id: str):
        """Applica i delta del twin al vault reale."""
        if twin_id not in self.active_twins: return False
        
        twin = self.active_twins[twin_id]
        
        # 1. Applica cancellazioni
        for nid in twin["deleted_ids"]:
            self.engine.remove_node(nid)
            
        # 2. Applica aggiunte/modifiche
        for nid, node in twin["delta_nodes"].items():
            await self.engine.add_node(node.id, node.text, node.metadata, vector=node.vector)
        
        del self.active_twins[twin_id]
        return True

    async def discard_twin(self, twin_id: str):
        if twin_id in self.active_twins:
            del self.active_twins[twin_id]
            return True
        return False
