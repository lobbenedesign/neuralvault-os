"""
retrieval/taxonomy.py
─────────────────────
Auto-Taxonomy Builder (v4.3.0)
Crea una gerarchia navigabile dai nodi del vault usando clustering gerarchico.
"""

import numpy as np
from typing import List, Dict, Any
from index.node import VaultNode

class AutoTaxonomyBuilder:
    def __init__(self, engine):
        self.engine = engine
        self.llm = engine.orchestrator if hasattr(engine, 'orchestrator') else None

    async def build_hierarchy(self) -> Dict[str, Any]:
        """
        Costruisce una gerarchia di cluster basata sulla similarità vettoriale.
        """
        print("🗂️ [Taxonomy] Building hierarchical taxonomy...")
        
        # 1. Recupero Nodi
        all_nodes = list(self.engine._nodes.values())
        if len(all_nodes) < 10:
            return {"name": "Sovereign Vault", "children": []}

        # 2. Clustering (Simulato via K-Means o Gerarchico semplificato)
        # Per ora usiamo un raggruppamento per namespace e metadati
        hierarchy = {"name": "Sovereign Vault", "children": []}
        
        namespaces = {}
        for node in all_nodes:
            ns = node.namespace
            if ns not in namespaces: namespaces[ns] = []
            namespaces[ns].append(node)
            
        for ns, nodes in namespaces.items():
            ns_child = {"name": ns.upper(), "children": []}
            
            # Sotto-clustering per topic_type o entità
            topics = {}
            for n in nodes:
                t = n.metadata.get('topic_type', 'general')
                if t not in topics: topics[t] = 0
                topics[t] += 1
                
            for t, count in topics.items():
                ns_child["children"].append({
                    "name": t.capitalize(),
                    "size": count
                })
                
            hierarchy["children"].append(ns_child)
            
        return hierarchy

    async def get_navigation_map(self) -> str:
        """Restituisce una rappresentazione testuale della tassonomia."""
        h = await self.build_hierarchy()
        output = "📚 MAPPA DEL VAULT\n"
        for child in h["children"]:
            output += f"├── {child['name']}\n"
            for sub in child.get('children', []):
                output += f"│   ├── {sub['name']} ({sub['size']} nodi)\n"
        return output
