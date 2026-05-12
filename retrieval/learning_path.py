import logging
from typing import List, Dict, Any

class LearningPathGenerator:
    """
    🗺️ [v8.4] Learning Path Engine.
    Mappa i prerequisiti cognitivi per dominare un nuovo argomento.
    """
    def __init__(self, engine):
        self.engine = engine
        self.logger = logging.getLogger("LearningPath")

    async def generate_path(self, target_topic: str) -> Dict[str, Any]:
        """Genera un curriculum basato sulle dipendenze nel vault."""
        # 1. Trova il nodo principale
        search = await self.engine.query(target_topic, k=1)
        if not search:
            return {"error": "Argomento non trovato nel vault."}
            
        root_node = search[0].node
        
        # 2. Esplora le relazioni 'REQUIRES' o 'DEPENDS_ON'
        # In assenza di relazioni esplicite, usiamo la somiglianza semantica 
        # e la data di creazione per suggerire un ordine.
        prerequisites = []
        for edge in root_node.edges:
            if edge.relation in ["requires", "depends_on", "precedes"]:
                target = self.engine.get_node(edge.target_id)
                if target:
                    prerequisites.append({
                        "id": target.id,
                        "title": target.metadata.get("title", target.id),
                        "type": "Explicit Requirement"
                    })
        
        # 3. Fallback: Vicini Semantici (Galassia Concettuale)
        if not prerequisites:
            neighbors = await self.engine.query(target_topic, k=5)
            for n in neighbors[1:]: # Escludiamo il primo che è il target stesso
                prerequisites.append({
                    "id": n.node.id,
                    "title": n.node.metadata.get("title", n.node.id),
                    "type": "Semantic Prerequisite"
                })
                
        # 4. Calcolo Coverage (Quanto ne sappiamo già?)
        # Simulato: se il nodo ha molta 'wisdom' (riassunto), lo consideriamo noto.
        steps = []
        for i, pre in enumerate(prerequisites):
            node = self.engine.get_node(pre["id"])
            coverage = 0.8 if node and len(node.text) > 500 else 0.3
            steps.append({
                "order": i + 1,
                "topic": pre["title"],
                "coverage": coverage,
                "status": "COMPLETED" if coverage > 0.7 else "GAP"
            })
            
        return {
            "target": target_topic,
            "path": steps,
            "estimated_time_min": len(steps) * 15,
            "total_coverage": sum([s["coverage"] for s in steps]) / len(steps) if steps else 0
        }
