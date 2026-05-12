"""
retrieval/entity_linker.py
─────────────────────────
[v8.1] Sovereign Entity Linker Engine
Gestisce il mapping semantico tra testo generato e nodi del Vault.
Elimina la necessità di Regex fragili tramite Entity Anchor Indexing.
"""

import re
from typing import List, Dict, Any, Optional

class EntityLinker:
    def __init__(self, engine):
        self.engine = engine
        self.anchor_index = {} # Mappa: Anchor Text -> Node ID

    def build_anchor_index(self, nodes: List[Any]):
        """Costruisce un indice locale per il linking veloce su un set di nodi."""
        index = {}
        for r in nodes:
            node = r.node if hasattr(r, 'node') else r
            title = node.metadata.get('title', '').lower().strip()
            if title:
                index[title] = str(node.id)
            
            # Aggiungi alias se presenti
            aliases = node.metadata.get('aliases', [])
            if isinstance(aliases, list):
                for alias in aliases:
                    index[alias.lower().strip()] = str(node.id)
        return index

    def link_entities(self, text: str, anchor_index: Dict[str, str]) -> str:
        """
        Applica il linking semantico al testo.
        Usa un approccio a due passaggi: 
        1. Identificazione termini (ordinati per lunghezza per evitare sovrapposizioni)
        2. Sostituzione sicura con span interattivi.
        """
        if not anchor_index:
            return text

        # Ordina i termini dal più lungo al più corto per evitare che "Neural" linki prima di "NeuralVault"
        sorted_terms = sorted(anchor_index.keys(), key=len, reverse=True)
        
        # [v8.1] Protezione: Sostituiamo temporaneamente i link già esistenti o tag
        linked_text = text
        placeholders = {}
        
        for i, term in enumerate(sorted_terms):
            if not term: continue
            
            # Pattern: parola intera (boundary) non già contenuta in un tag HTML
            # Usiamo una regex che evita di matchare dentro a <...>
            pattern = re.compile(rf'\b({re.escape(term)})\b(?![^<]*>)', re.IGNORECASE)
            
            node_id = anchor_index[term]
            replacement = f'<span class="wiki-entity" data-node-id="{node_id}">\\1</span>'
            
            linked_text = pattern.sub(replacement, linked_text)
            
        return linked_text

    def get_entity_preview(self, node_id: str) -> Dict[str, Any]:
        """Restituisce una preview ottimizzata per il Disclosure Panel."""
        node = self.engine.get_node(node_id)
        if not node:
            return {"error": "Node not found"}
            
        return {
            "id": node_id,
            "title": node.metadata.get('title', 'N/A'),
            "preview": node.text[:250] + "...",
            "confidence": node.metadata.get('confidence', 0.8),
            "freshness": node.metadata.get('freshness', 0.9)
        }
