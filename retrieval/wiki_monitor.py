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
                    fingerprint VARCHAR,
                    ingested_at TIMESTAMP,
                    PRIMARY KEY (wiki_topic, node_id)
                )
            """)
            # [v9.2] Spaced Repetition: wiki_reviews table
            self.engine._prefilter.execute("""
                CREATE TABLE IF NOT EXISTS wiki_reviews (
                    wiki_topic VARCHAR PRIMARY KEY,
                    last_review TIMESTAMP,
                    review_count INTEGER DEFAULT 0,
                    retention_score DOUBLE DEFAULT 1.0,
                    interval_days INTEGER DEFAULT 1
                )
            """)
        except Exception as e:
            print(f"⚠️ [Wiki Monitor Init] {e}")

    async def track_dependencies(self, topic: str, node_ids: List[str]):
        """Registra i nodi sorgente e i loro fingerprint per un topic Wiki."""
        from retrieval.epistemic_engine import EpistemicCalculator
        epistemic = EpistemicCalculator(self.engine)
        now = datetime.now()
        
        for nid in node_ids:
            node = self.engine.get_node(nid)
            if not node: continue
            
            # Generiamo un fingerprint atomico per questo nodo specifico
            # (ID + timestamp per rilevare mutamenti)
            f_nodes = [{"id": node.id, "updated_at": getattr(node, 'updated_at', getattr(node, 'created_at', 0))}]
            node_fingerprint = epistemic.generate_knowledge_fingerprint(nid, f_nodes)
            
            try:
                self.engine._prefilter.execute(
                    "INSERT OR REPLACE INTO wiki_dependencies (wiki_topic, node_id, fingerprint, ingested_at) VALUES (?, ?, ?, ?)",
                    (topic, nid, node_fingerprint, now)
                )
            except: pass

    async def check_stale_pages(self) -> List[Dict[str, Any]]:
        """
        Trova i topic Wiki che hanno subito cambiamenti strutturali nei nodi sorgente.
        Utilizza il confronto tra fingerprint SHA-256 invece del semplice timestamp.
        """
        from retrieval.epistemic_engine import EpistemicCalculator
        epistemic = EpistemicCalculator(self.engine)
        
        try:
            if getattr(self.engine, 'priority_mode', False):
                return []
            
            # Recuperiamo tutte le dipendenze attuali
            deps = self.engine._prefilter.fetchall("SELECT wiki_topic, node_id, fingerprint FROM wiki_dependencies")
            
            stale_topics = {} # topic -> count
            
            for i, (topic, nid, old_f) in enumerate(deps):
                if i % 10 == 0:
                    import asyncio
                    await asyncio.sleep(0)
                    if getattr(self.engine, 'priority_mode', False):
                        return []
                
                node = self.engine.get_node(nid)
                if not node: continue
                
                # Calcoliamo il nuovo fingerprint
                f_nodes = [{"id": node.id, "updated_at": getattr(node, 'updated_at', getattr(node, 'created_at', 0))}]
                new_f = epistemic.generate_knowledge_fingerprint(nid, f_nodes)
                
                if new_f != old_f:
                    stale_topics[topic] = stale_topics.get(topic, 0) + 1
            
            return [{"topic": t, "stale_nodes": c} for t, c in stale_topics.items()]
        except Exception as e:
            print(f"⚠️ [Wiki Monitor Error] {e}")
            return []

    async def get_review_queue(self) -> List[Dict[str, Any]]:
        """Calcola la Daily Review Queue basata sulla curva dell'oblio."""
        try:
            now = datetime.now()
            rows = self.engine._prefilter.fetchall("SELECT wiki_topic, last_review, retention_score, interval_days FROM wiki_reviews")
            
            queue = []
            for topic, last, score, interval in rows:
                # Se non è mai stata rivista o se l'intervallo è passato
                days_since = (now - last).days if last else 999
                if days_since >= interval:
                    queue.append({"topic": topic, "score": score, "days_since": days_since})
            
            # Se la coda è vuota, aggiungi le pagine più vecchie dalla wiki_dependencies
            if not queue:
                topics = self.engine._prefilter.fetchall("SELECT DISTINCT wiki_topic FROM wiki_dependencies LIMIT 3")
                for (t,) in topics:
                    queue.append({"topic": t, "score": 1.0, "days_since": 0})
                    
            return sorted(queue, key=lambda x: x['score'])[:3] # Max 3 al giorno
        except: return []

    async def record_review(self, topic: str, score: float):
        """Registra una sessione di ripasso e aggiorna l'intervallo (SuperMemo-like)."""
        now = datetime.now()
        row = self.engine._prefilter.fetchone("SELECT review_count, interval_days FROM wiki_reviews WHERE wiki_topic = ?", (topic,))
        
        if not row:
            count, interval = 1, 1
        else:
            count = row[0] + 1
            # Logica semplificata: se il voto è buono (>0.7), raddoppia l'intervallo
            interval = row[1] * 2 if score > 0.7 else 1
            
        self.engine._prefilter.execute(
            "INSERT OR REPLACE INTO wiki_reviews (wiki_topic, last_review, review_count, retention_score, interval_days) VALUES (?, ?, ?, ?, ?)",
            (topic, now, count, score, interval)
        )

    async def get_page_status(self, topic: str) -> Dict[str, Any]:
        """
        [v9.6] Verifica la freschezza di un singolo topic in tempo reale.
        Restituisce un report dettagliato sulla stabilità della conoscenza.
        """
        from retrieval.epistemic_engine import EpistemicCalculator
        epistemic = EpistemicCalculator(self.engine)
        
        try:
            deps = self.engine._prefilter.fetchall(
                "SELECT node_id, fingerprint FROM wiki_dependencies WHERE wiki_topic = ?", 
                (topic,)
            )
            
            if not deps:
                return {"is_stale": False, "stale_nodes": 0, "total_nodes": 0, "last_update": datetime.now().isoformat()}

            stale_nodes = 0
            for nid, old_f in deps:
                node = self.engine.get_node(nid)
                if not node: continue
                
                # Ricalcolo fingerprint atomico
                f_nodes = [{"id": node.id, "updated_at": getattr(node, 'updated_at', getattr(node, 'created_at', 0))}]
                new_f = epistemic.generate_knowledge_fingerprint(nid, f_nodes)
                
                if new_f != old_f:
                    stale_nodes += 1
            
            return {
                "is_stale": stale_nodes > 0,
                "stale_nodes": stale_nodes,
                "total_nodes": len(deps),
                "last_update": datetime.now().isoformat()
            }
        except Exception as e:
            print(f"⚠️ [Freshness Check Error] {topic}: {e}")
            return {"is_stale": False, "stale_nodes": 0, "total_nodes": 0, "error": str(e)}
