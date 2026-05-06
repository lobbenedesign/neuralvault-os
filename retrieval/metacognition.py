"""
retrieval/metacognition.py
──────────────────────────────
[v7.0] Metacognition Engine
Identifica "Terra Incognita" e vuoti semantici nel grafo della conoscenza.
"""

import numpy as np
from typing import List, Dict
from dataclasses import dataclass

@dataclass
class IgnoranceRegion:
    id: str
    x: float
    y: float
    z: float
    radius: float
    topic_context: str
    missing_concepts: List[str]

class MetacognitionEngine:
    def __init__(self, engine):
        self.engine = engine

    async def map_ignorance_gaps(self, limit=5) -> List[IgnoranceRegion]:
        """
        Analizza la densità dei nodi e identifica cluster 'isolati' o 'vuoti'
        tra galassie conosciute.
        """
        # 1. Recuperiamo tutti i punti correnti (limitate per performance)
        nodes = list(self.engine._nodes.values())
        if len(nodes) < 10: return []

        # 2. Raggruppamento semplice per coordinate (già calcolate dalla proiezione)
        # Nota: Usiamo le coordinate x,y,z memorizzate nei nodi se disponibili
        points = []
        for n in nodes:
            if hasattr(n, 'x') and n.x is not None:
                points.append([n.x, n.y, n.z])
        
        if not points: return []
        
        points = np.array(points)
        centroid = np.mean(points, axis=0)
        std_dev = np.std(points, axis=0)

        # 3. Identificazione Gaps (Aree adiacenti con bassa densità)
        # Algoritmo Euristico: Generiamo punti casuali nel "volume" del Vault
        # e verifichiamo quali sono più lontani da qualsiasi nodo reale.
        gaps = []
        for i in range(limit * 3):
            # Campionamento nel range 1.5x della deviazione standard dal centro
            candidate = centroid + (np.random.randn(3) * std_dev * 1.5)
            
            # Calcolo distanza minima dai nodi reali
            distances = np.linalg.norm(points - candidate, axis=1)
            min_dist = np.min(distances)
            
            # Se la distanza è significativa (un "buco"), è una Terra Incognita
            if min_dist > (np.mean(std_dev) * 0.5):
                gaps.append((candidate, min_dist))

        # Sort per distanza (i buchi più grandi prima)
        gaps.sort(key=lambda x: x[1], reverse=True)
        
        ignorance_regions = []
        for i, (pos, dist) in enumerate(gaps[:limit]):
            # Proiezione del topic basata sui nodi vicini
            # Cerchiamo i 3 nodi più vicini per capire il contesto del vuoto
            idx = np.argsort(np.linalg.norm(points - pos, axis=1))[:3]
            nearby_nodes = [nodes[j] for j in idx]
            
            context = " | ".join([n.metadata.get('title', n.text[:30]) for n in nearby_nodes])
            
            ignorance_regions.append(IgnoranceRegion(
                id=f"gap_{i}",
                x=float(pos[0]),
                y=float(pos[1]),
                z=float(pos[2]),
                radius=float(dist * 0.8),
                topic_context=context,
                missing_concepts=await self._predict_missing_knowledge(context)
            ))
            
        return ignorance_regions

    async def _predict_missing_knowledge(self, context: str) -> List[str]:
        """Usa l'LLM per immaginare cosa manca tra questi concetti."""
        prompt = f"""
        Tra questi concetti della nostra Wiki: {context}.
        Quale argomento o 'ponte mancante' identifichi come gap di conoscenza?
        Rispondi con 2-3 parole chiave separate da virgola.
        """
        model = self.engine.orchestrator.settings.get("wiki_model", "llama3.2:3b")
        res = await self.engine.orchestrator.get_consensus_response(prompt, "Metacognition", target_model=model)
        return [c.strip() for c in res.split(",")][:3]
