import os
import sqlite3
import hashlib
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

class SearchMirrorManager:
    """
    [v1.0.0 Sovereign Search Mirror]
    Gestore della memoria locale dei risultati di ricerca web.
    Implementa la logica di 'Local-First' ispirata a PrintingPress.
    """
    
    def __init__(self, db_path: str = "vault_data/search_mirror.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()

    def _init_db(self):
        """Inizializza il database e le tabelle FTS5."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabella principale per i metadati e il caching
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS search_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query_hash TEXT,
                query_text TEXT,
                engine TEXT,
                url TEXT,
                title TEXT,
                snippet TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(query_hash, engine, url)
            )
        """)
        
        # Tabella Virtuale FTS5 per ricerca full-text ultra-rapida
        try:
            cursor.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS search_fts USING fts5(
                    title,
                    snippet,
                    content='search_cache',
                    content_rowid='id'
                )
            """)
            
            # Triggers per mantenere FTS sincronizzato
            cursor.execute("""
                CREATE TRIGGER IF NOT EXISTS bu_search_cache_ai AFTER INSERT ON search_cache BEGIN
                    INSERT INTO search_fts(rowid, title, snippet) VALUES (new.id, new.title, new.snippet);
                END;
            """)
        except sqlite3.OperationalError as e:
            print(f"⚠️ [SearchMirror] FTS5 non supportato o errore: {e}")
            
        conn.commit()
        conn.close()

    def _get_hash(self, text: str) -> str:
        return hashlib.sha256(text.lower().strip().encode()).hexdigest()

    def add_results(self, query: str, engine: str, results: List[Dict[str, str]]):
        """Aggiunge risultati di ricerca al mirror locale."""
        query_hash = self._get_hash(query)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for res in results:
            url = res.get("url", "")
            title = res.get("title", "")
            snippet = res.get("snippet", "")
            
            cursor.execute("""
                INSERT OR REPLACE INTO search_cache (query_hash, query_text, engine, url, title, snippet, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (query_hash, query, engine, url, title, snippet))
            
        conn.commit()
        conn.close()

    def get_cached_results(self, query: str, max_age_hours: int = 48) -> List[Dict[str, Any]]:
        """Recupera risultati recenti dallo stack locale."""
        query_hash = self._get_hash(query)
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cutoff = (datetime.now() - timedelta(hours=max_age_hours)).isoformat()
        
        cursor.execute("""
            SELECT engine, url, title, snippet, timestamp 
            FROM search_cache 
            WHERE query_hash = ? AND timestamp > ?
            ORDER BY timestamp DESC
        """, (query_hash, cutoff))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(r) for r in rows]

    def sovereign_search(self, text: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Esegue una ricerca Full-Text puramente locale sui dati foraggiati in passato.
        Questo permette agli agenti di trovare risposte senza toccare il web.
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            # Query FTS5 con ranking BM25
            cursor.execute("""
                SELECT c.engine, c.url, c.title, c.snippet, c.timestamp, f.rank
                FROM search_fts f
                JOIN search_cache c ON f.rowid = c.id
                WHERE search_fts MATCH ?
                ORDER BY rank
                LIMIT ?
            """, (text, limit))
            rows = cursor.fetchall()
        except sqlite3.OperationalError:
            # Fallback se FTS5 fallisce o la query è malformata
            cursor.execute("""
                SELECT engine, url, title, snippet, timestamp
                FROM search_cache
                WHERE title LIKE ? OR snippet LIKE ?
                LIMIT ?
            """, (f"%{text}%", f"%{text}%", limit))
            rows = cursor.fetchall()
            
        conn.close()
        return [dict(r) for r in rows]

    def get_stats(self) -> Dict[str, Any]:
        """Restituisce statistiche sull'occupazione del mirror."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*), COUNT(DISTINCT query_hash) FROM search_cache")
        total_res, unique_queries = cursor.fetchone()
        
        cursor.execute("SELECT engine, COUNT(*) FROM search_cache GROUP BY engine")
        engines = dict(cursor.fetchall())
        
        conn.close()
        return {
            "total_results": total_res,
            "unique_queries": unique_queries,
            "engines_coverage": engines,
            "db_size_kb": os.path.getsize(self.db_path) // 1024 if os.path.exists(self.db_path) else 0
        }
