import logging
import json
import uuid
import copy
from typing import Dict, Any, List, Optional
from index.node import VaultNode

class SovereignVaultTwin:
    """
    🌓 [v8.4] Vault Digital Twin Engine.
    Sandbox cognitiva per esperimenti sicuri.
    """
    def __init__(self, engine):
        self.engine = engine
        self.logger = logging.getLogger("VaultTwin")
        self.active_twins = {} # twin_id -> TwinState

    async def create_twin(self) -> str:
        """Crea uno snapshot in RAM del vault attuale."""
        twin_id = f"TWIN-{uuid.uuid4().hex[:6]}"
        
        # Deep copy dei nodi in RAM (Neural Grid)
        # Nota: In un sistema reale con milioni di nodi, useremmo un approccio copy-on-write
        twin_nodes = {nid: copy.deepcopy(node) for nid, node in self.engine._nodes.items()}
        
        self.active_twins[twin_id] = {
            "nodes": twin_nodes,
            "mutations": [],
            "created_at": uuid.uuid1().timestamp
        }
        
        self.logger.info(f"🌓 Twin Created: {twin_id} with {len(twin_nodes)} nodes.")
        return twin_id

    async def simulate_ingestion(self, twin_id: str, text: str, source: str) -> Dict[str, Any]:
        """Simula cosa succederebbe se aggiungessimo questo contenuto."""
        if twin_id not in self.active_twins:
            return {"error": "Twin non trovato o scaduto."}
            
        twin = self.active_twins[twin_id]
        
        # 1. Generazione embedding (usiamo l'engine reale per questo)
        vector = self.engine._embed_text(text)
        
        # 2. Creazione nodo simulato
        sim_node = VaultNode(
            id=f"SIM-{uuid.uuid4().hex[:6]}",
            text=text,
            vector=vector,
            metadata={"source": source, "simulated": True}
        )
        
        # 3. Calcolo impatto (connessioni potenziali nel Twin)
        # Cerchiamo i vicini nel Twin invece che nel vault reale
        potential_links = []
        for nid, node in twin["nodes"].items():
            if node.vector is not None and len(node.vector) > 0:
                sim = self._cosine_similarity(vector, node.vector)
                if sim > 0.75:
                    potential_links.append({"id": nid, "title": node.metadata.get("title", "Nodo"), "similarity": sim})
        
        # 4. Analisi contraddizioni (simulata)
        prompt = f"""
        Analizza se questo nuovo contenuto contraddice la conoscenza esistente nel Twin.
        
        NUOVO: {text}
        
        CONTESTO TWIN (Vicini):
        {json.dumps(potential_links[:3])}
        
        Rispondi in 2 frasi: ci sono conflitti?
        """
        contradiction_analysis = await self.engine.orchestrator.get_consensus_response(prompt, "Twin Contradiction Audit")
        
        # 5. Registrazione mutazione nel Twin (non nel vault reale)
        twin["nodes"][sim_node.id] = sim_node
        twin["mutations"].append({"action": "ADD", "node_id": sim_node.id})
        
        return {
            "twin_id": twin_id,
            "new_node_id": sim_node.id,
            "potential_links": potential_links,
            "contradiction_report": contradiction_analysis,
            "status": "Simulated in Twin"
        }

    def _cosine_similarity(self, v1, v2):
        import numpy as np
        return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

    async def commit_twin(self, twin_id: str):
        """Applica le modifiche del twin al vault reale."""
        if twin_id not in self.active_twins: return False
        
        twin = self.active_twins[twin_id]
        for mut in twin["mutations"]:
            if mut["action"] == "ADD":
                node = twin["nodes"][mut["node_id"]]
                await self.engine.add_node(node.id, node.text, node.metadata)
        
        del self.active_twins[twin_id]
        return True

    async def discard_twin(self, twin_id: str):
        """Elimina il twin senza lasciare traccia."""
        if twin_id in self.active_twins:
            del self.active_twins[twin_id]
            return True
        return False
