"""
retrieval/timeline.py
─────────────────────
Knowledge Timeline Engine (v4.3.0)
Traccia l'evoluzione della conoscenza nel tempo via Merkle Ledger.
"""

from datetime import datetime
from typing import List, Dict, Any

class KnowledgeTimeline:
    def __init__(self, engine):
        self.engine = engine
        self.db = engine._prefilter # Usiamo DuckDB per la storia eventi

    async def get_topic_evolution(self, topic: str) -> List[Dict[str, Any]]:
        """
        Recupera la cronologia di come un topic è cresciuto nel vault.
        """
        print(f"📅 [Timeline] Reconstructing evolution for: {topic}")
        
        # Query al ledger degli eventi reale (Gap #5)
        try:
            query = """
                SELECT timestamp, event_type, description, node_id 
                FROM knowledge_events 
                WHERE topic_cluster = ? OR description LIKE ?
                ORDER BY timestamp ASC
            """
            rows = self.db.execute(query, (topic, f"%{topic}%")).fetchall()
            
            if not rows:
                # Fallback: ricostruzione dai nodi se il ledger è vuoto
                results = await self.engine.query(topic, k=20)
                timeline = []
                for r in sorted(results, key=lambda x: x.node.created_at):
                    timeline.append({
                        "date": datetime.fromtimestamp(r.node.created_at).strftime("%Y-%m-%d"),
                        "event": "NODE_INGESTED",
                        "summary": r.node.text[:100] + "...",
                        "node_id": r.node.id
                    })
                return timeline

            return [
                {
                    "date": r[0].strftime("%Y-%m-%d %H:%M") if hasattr(r[0], 'strftime') else str(r[0]),
                    "event": r[1],
                    "summary": r[2],
                    "node_id": r[3]
                } for r in rows
            ]
        except Exception as e:
            print(f"⚠️ [Timeline] Query failed: {e}")
            return []

    def render_markdown(self, timeline: List[Dict[str, Any]]) -> str:
        if not timeline: return "Nessuna evoluzione registrata per questo argomento."
        
        md = "## 📅 EVOLUZIONE DELLA CONOSCENZA\n\n"
        for entry in timeline:
            md += f"- **{entry['date']}**: {entry['event']} - *{entry['summary']}*\n"
        return md
