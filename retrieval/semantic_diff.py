import numpy as np
from typing import Optional, Dict, Any
from dataclasses import dataclass

@dataclass
class SemanticDiffResult:
    action: str # "UPDATE_METADATA", "EVOLVED", "SUPERSEDED", "CREATE"
    similarity: float
    existing_node_id: Optional[str] = None

class SemanticDiffEngine:
    """
    🧬 [SEMANTIC DIFF ENGINE]
    Determina se un nuovo contenuto deve aggiornare un nodo esistente 
    o crearne uno nuovo, basandosi sulla similarità vettoriale.
    """
    def __init__(self, engine):
        self.engine = engine
        # Soglie base (Sovereign Default)
        self.base_update = 0.98
        self.base_evolve = 0.85
        self.base_supersede = 0.60
        self._apply_adaptation()

    def _apply_adaptation(self):
        """[v5.0] Adatta le soglie in base alla densità del vault."""
        node_count = len(self.engine._nodes)
        # Se il vault è grande (> 1000 nodi), alziamo leggermente la precisione richiesta
        density_factor = min(0.05, node_count / 50000.0) 
        self.update_threshold = self.base_update
        self.evolve_threshold = self.base_evolve + density_factor
        self.supersede_threshold = self.base_supersede + (density_factor * 0.5)

    def cosine_similarity(self, v1, v2):
        if v1 is None or v2 is None: return 0.0
        return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

    async def analyze(self, new_text: str, new_vector: np.ndarray) -> SemanticDiffResult:
        """Compara il nuovo contenuto con i nodi più simili esistenti."""
        # Trova il nodo più simile nel vault
        results = await self.engine.query_vector(new_vector, k=1)
        if not results:
            return SemanticDiffResult(action="CREATE", similarity=0.0)
        
        best_match = results[0]
        similarity = best_match.score # Supponendo che score sia cosine similarity
        
        if similarity > self.update_threshold:
            return SemanticDiffResult(action="UPDATE_METADATA", similarity=similarity, existing_node_id=best_match.node.id)
        
        elif similarity > self.evolve_threshold:
            return SemanticDiffResult(action="EVOLVED", similarity=similarity, existing_node_id=best_match.node.id)
            
        elif similarity > self.supersede_threshold:
            return SemanticDiffResult(action="SUPERSEDED", similarity=similarity, existing_node_id=best_match.node.id)
            
        return SemanticDiffResult(action="CREATE", similarity=similarity)

    async def apply_diff(self, result: SemanticDiffResult, new_text: str, new_metadata: Dict):
        """Applica la decisione presa dall'analisi."""
        if result.action == "UPDATE_METADATA":
            node = self.engine._nodes.get(result.existing_node_id)
            if node:
                node.metadata.update(new_metadata)
                node.metadata["last_semantic_sync"] = str(np.datetime64('now'))
                self.engine.storage_put(node)
                print(f"♻️ [Semantic-Diff] Updated metadata for node {result.existing_node_id}")

        elif result.action == "EVOLVED":
            node = self.engine._nodes.get(result.existing_node_id)
            if node:
                old_text = node.text
                node.text = new_text
                node.metadata.update(new_metadata)
                node.metadata["evolution_count"] = node.metadata.get("evolution_count", 0) + 1
                self.engine.storage_put(node)
                # Registriamo l'evento nel ledger
                self.engine._prefilter.log_event(
                    "NODE_EVOLVED", 
                    node.id, 
                    node.metadata.get("topic", "general"),
                    f"Contenuto evoluto (Similarità: {result.similarity:.2f})"
                )
                print(f"🧬 [Semantic-Diff] Node {result.existing_node_id} EVOLVED to new version.")

        elif result.action == "SUPERSEDED":
            # Crea un nuovo nodo e collegalo al precedente con un arco "SUPERSEDES"
            new_node = await self.engine.ingest_text(new_text, metadata=new_metadata)
            self.engine.add_edge(new_node.id, result.existing_node_id, edge_type="SUPERSEDES")
            print(f"🔗 [Semantic-Diff] New node {new_node.id} SUPERSEDES {result.existing_node_id}")
