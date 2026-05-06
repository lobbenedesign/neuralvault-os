"""
retrieval/wiki_monitor.py
────────────────────────
Dependency Tracker for Sovereign Wiki.
Tracks which nodes contribute to which Wiki pages to detect obsolescence.
"""

from datetime import datetime
from typing import List, Dict, Any
import json

class WikiFreshnessMonitor:
    def __init__(self, engine):
        self.engine = engine
        self._init_db()

    def _init_db(self):
        """Inizializza le tabelle di dipendenza in DuckDB."""
        try:
            self.engine._prefilter.execute("""
                CREATE TABLE IF NOT EXISTS wiki_dependencies (
                    wiki_topic VARCHAR,
                    node_id VARCHAR,
                    ingested_at TIMESTAMP,
                    PRIMARY KEY (wiki_topic, node_id)
                )
            """)
        except Exception as e:
            print(f"⚠️ [Wiki Monitor Init] {e}")

    async def track_dependencies(self, topic: str, node_ids: List[str]):
        """Registra i nodi sorgente per un topic Wiki."""
        now = datetime.now()
        for nid in node_ids:
            try:
                self.engine._prefilter.execute(
                    "INSERT OR REPLACE INTO wiki_dependencies (wiki_topic, node_id, ingested_at) VALUES (?, ?, ?)",
                    (topic, nid, now)
                )
            except: pass

    async def check_stale_pages(self) -> List[Dict[str, Any]]:
        """
        Trova i topic Wiki che hanno subito cambiamenti nei nodi sorgente.
        Un topic è 'stale' se i nodi collegati hanno un updated_at superiore alla data di generazione Wiki.
        """
        # Nota: Questa è una versione semplificata. 
        # In una vera implementazione confronteremmo con la tabella wiki_pages (se esistesse).
        # Qui verifichiamo se ci sono stati nuovi inserimenti nella stessa galassia del topic.
        try:
            query = """
                SELECT DISTINCT wd.wiki_topic, COUNT(*) as changed_count
                FROM wiki_dependencies wd
                JOIN vault_metadata vm ON wd.node_id = vm.id
                WHERE vm.updated_at > wd.ingested_at
                GROUP BY wd.wiki_topic
            """
            res = self.engine._prefilter.execute(query).fetchall()
            return [{"topic": r[0], "stale_nodes": r[1]} for r in res]
        except:
            return []

    async def get_page_status(self, topic: str) -> Dict[str, Any]:
        """Ritorna lo stato di freschezza di una singola pagina Wiki."""
        stale_pages = await self.check_stale_pages()
        for p in stale_pages:
            if p["topic"] == topic:
                return {"is_stale": True, "stale_nodes": p["stale_nodes"]}
        return {"is_stale": False, "stale_nodes": 0}
