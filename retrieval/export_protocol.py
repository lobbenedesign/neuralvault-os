import os
import json
from pathlib import Path
from typing import List

class SovereignExportProtocol:
    """
    🏺 [SOVEREIGN EXPORT PROTOCOL]
    Permette l'esportazione della conoscenza in formati aperti (Obsidian, Anki).
    Garantisce che i dati dell'utente siano indipendenti dal sistema.
    """
    def __init__(self, engine):
        self.engine = engine

    async def to_obsidian(self, output_path: str):
        """Esporta il vault come cartella di file Markdown compatibile con Obsidian."""
        out_dir = Path(output_path)
        out_dir.mkdir(parents=True, exist_ok=True)
        
        nodes = list(self.engine._nodes.values())
        exported = 0
        
        for node in nodes:
            # Sanitizzazione titolo per filename
            safe_title = "".join([c for c in node.metadata.get("title", "Untitled") if c.isalnum() or c in " _-"]).strip()
            filename = f"{safe_title}_{node.id[:8]}.md"
            
            content = f"---"
            content += f"\nid: {node.id}"
            content += f"\ncreated: {node.metadata.get('created_at', 'unknown')}"
            content += f"\ntags: {node.metadata.get('tags', [])}"
            content += f"\n---"
            content += f"\n\n# {node.metadata.get('title', 'Untitled')}\n\n"
            content += node.text
            
            if hasattr(node, 'edges') and node.edges:
                content += "\n\n## Connessioni\n"
                for edge in node.edges:
                    target = self.engine._nodes.get(edge.target_id)
                    if target:
                        t_title = target.metadata.get("title", "Untitled")
                        content += f"- [[{t_title}_{target.id[:8]}]]\n"

            # [v5.0] Multi-modal Support
            media_path = node.metadata.get("media_path")
            if media_path:
                ext = media_path.split('.')[-1].lower()
                if ext in ['jpg', 'jpeg', 'png', 'gif']:
                    content += f"\n\n## Media\n![[{media_path}]]\n"
                elif ext in ['mp4', 'mov']:
                    content += f"\n\n## Media\n![[{media_path}]]\n"
            
            with open(out_dir / filename, "w") as f:
                f.write(content)
            exported += 1
            
        return exported

    async def to_anki(self, output_file: str):
        """Esporta nodi con bassa retention come flashcard Anki (Concept)."""
        # Nota: Richiede libreria genanki, qui implementiamo un export JSON compatibile
        weak_nodes = [
            n for n in self.engine._nodes.values()
            if n.metadata.get("retention", 1.0) < 0.7
        ]
        
        cards = []
        for n in weak_nodes:
            cards.append({
                "front": n.metadata.get("title", "Flashcard"),
                "back": n.text[:500] + "...",
                "node_id": n.id
            })
            
        with open(output_file, "w") as f:
            json.dump(cards, f, indent=4)
            
        return len(cards)
