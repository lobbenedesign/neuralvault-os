"""
retrieval/prefilter.py
───────────────────────
DuckDB Prefilter: Database relazionale incorporato per pre-filtraggio metadati.
Permette ricerche SQL-like ultra-veloci (Fisicamente pronti per un milione di nodi).
"""

import duckdb
import pandas as pd
import threading
import os
import shutil
import json
import hashlib
from pathlib import Path
from typing import List, Dict, Optional

class DuckDBPrefilter:
    """
    Motore di ricerca su metadati strutturati (v0.2.5).
    Responsabile del routing analitico del Query Planner.
    """
    def __init__(self, db_path: Optional[Path] = None):
        self._lock = threading.Lock()
        if db_path:
            try:
                self.con = duckdb.connect(database=str(db_path / "vault_metadata.db"))
                # [Optimization]: Consolidamento WAL per risparmio spazio
                self.con.execute("PRAGMA checkpoint_threshold = '512MB';")
                self.con.execute("CHECKPOINT;")
                print("🦆 [DuckDB] Hyper-Optimization Active (Checkpoint/WAL consolidation).")
            except Exception as e:
                error_str = str(e).lower()
                print(f"⚠️ [Prefilter] WAL Conflict or Internal Error: {e}")
                db_file = str(db_path / "vault_metadata.db")
                
                # [v4.3.1] Lock Awareness: Do NOT delete DB if it's just a lock conflict
                if "lock" in error_str or "process" in error_str:
                    print(f"🛑 [Prefilter] CRITICAL: Database is LOCKED by another process.")
                    print(f"👉 Please ensure no other instances of NeuralVault are running (Check PID mentioned above).")
                    # In questo caso non resettiamo nulla, lasciamo che il sistema fallisca o aspetti
                    raise e

                import os
                wal_path = f"{db_file}.wal"
                if os.path.exists(wal_path):
                    try: os.remove(wal_path)
                    except: pass
                
                try:
                    self.con = duckdb.connect(db_file)
                except:
                    print(f"☣️ [Prefilter] Recovery failed. Resetting metadata index.")
                    try: os.remove(db_file)
                    except: pass
                    self.con = duckdb.connect(db_file)
        else:
            self.con = duckdb.connect(":memory:")
            
        # Creazione schema iniziale (v0.5.0: Synaptic Pillars)
        self.con.execute("""
            CREATE TABLE IF NOT EXISTS vault_metadata (
                id VARCHAR PRIMARY KEY,
                collection VARCHAR,
                namespace VARCHAR DEFAULT 'default',
                file_type VARCHAR DEFAULT 'text',
                created_at TIMESTAMP,
                last_access TIMESTAMP,
                access_count INTEGER DEFAULT 0,
                importance DOUBLE DEFAULT 1.0,
                modality VARCHAR DEFAULT 'text',
                content_hash VARCHAR,
                lifecycle_state VARCHAR DEFAULT 'stable',
                metadata JSON
            )
        """)

        # Memoria Episodica Persistente (v1.1.0 Sovereign Hardening)
        self.con.execute("""
            CREATE TABLE IF NOT EXISTS episodic_memory (
                node_id VARCHAR PRIMARY KEY,
                protected_at TIMESTAMP DEFAULT now(),
                rejected_by VARCHAR,
                reason VARCHAR,
                protection_level INTEGER DEFAULT 1,
                confidence DOUBLE DEFAULT 1.0
            )
        """)

        # 📊 Telemetria Agenti Persistente (v3.5.0)
        self.con.execute("""
            CREATE TABLE IF NOT EXISTS agent_telemetry (
                agent_id VARCHAR,
                counter_name VARCHAR,
                val DOUBLE DEFAULT 0,
                last_updated TIMESTAMP DEFAULT now(),
                PRIMARY KEY (agent_id, counter_name)
            )
        """)

        # 📅 Sovereign Knowledge Ledger (v4.3.0)
        self.con.execute("""
            CREATE TABLE IF NOT EXISTS knowledge_events (
                timestamp TIMESTAMP DEFAULT now(),
                event_type VARCHAR,
                topic_cluster VARCHAR,
                node_id VARCHAR,
                description TEXT
            )
        """)
        
        # Migrazione schema se necessario (v0.5.5 Deduplication + v1.1.0 Lifecycle)
        # 🌌 Hierarchical GraphRAG: Community Table (v6.0)
        self.con.execute("""
            CREATE TABLE IF NOT EXISTS neural_communities (
                id VARCHAR PRIMARY KEY,
                level INTEGER DEFAULT 1,
                title VARCHAR,
                summary TEXT,
                key_concepts JSON,
                node_count INTEGER,
                created_at TIMESTAMP DEFAULT now(),
                last_updated TIMESTAMP DEFAULT now(),
                metadata JSON
            )
        """)

        # 🎭 [v8.2] Persona Kernels (E2P Pipeline)
        self.con.execute("""
            CREATE TABLE IF NOT EXISTS persona_kernels (
                entity_id VARCHAR PRIMARY KEY,
                canonical_name VARCHAR,
                roles JSON,
                behavioral_fingerprint JSON,
                historical_actions JSON,
                last_seen TIMESTAMP DEFAULT now(),
                metadata JSON
            )
        """)

        try:
            cols = self.con.execute("PRAGMA table_info('vault_metadata')").fetchall()
            col_names = [c[1] for c in cols]
            
            if 'community_id' not in col_names:
                print("🌌 [v6.0] Inizializzazione Gerarchia: Aggiunta colonna Community ID...")
                self.con.execute("ALTER TABLE vault_metadata ADD COLUMN community_id VARCHAR")
                self.con.execute("CREATE INDEX IF NOT EXISTS idx_community ON vault_metadata(community_id)")

            if 'lifecycle_state' not in col_names:
                print("🔄 [v1.1.0] Aggiunta colonna Lifecycle State...")
                self.con.execute("ALTER TABLE vault_metadata ADD COLUMN lifecycle_state VARCHAR DEFAULT 'stable'")

            if 'last_access' not in col_names:
                print("🧠 [v0.5.0] Migrazione schema: Aggiunta pilastri cognitivi...")
                self.con.execute("ALTER TABLE vault_metadata ADD COLUMN last_access TIMESTAMP DEFAULT now()")
                self.con.execute("ALTER TABLE vault_metadata ADD COLUMN access_count INTEGER DEFAULT 1")
                self.con.execute("ALTER TABLE vault_metadata ADD COLUMN importance DOUBLE DEFAULT 1.0")
                self.con.execute("ALTER TABLE vault_metadata ADD COLUMN modality VARCHAR DEFAULT 'text'")
            
            if 'content_hash' not in col_names:
                print("🔒 [v0.5.5] Inizializzazione motore di Deduplicazione...")
                self.con.execute("ALTER TABLE vault_metadata ADD COLUMN content_hash VARCHAR")
                self.con.execute("CREATE INDEX IF NOT EXISTS idx_content_hash ON vault_metadata(content_hash)")

            if 'namespace' not in col_names:
                print("城堡 [v3.6.0] Inizializzazione Logical Namespacing...")
                self.con.execute("ALTER TABLE vault_metadata ADD COLUMN namespace VARCHAR DEFAULT 'default'")
                self.con.execute("CREATE INDEX IF NOT EXISTS idx_namespace ON vault_metadata(namespace)")

            if 'file_type' not in col_names:
                print("📄 [v3.6.0] Inizializzazione Advanced Scalar Filtering...")
                self.con.execute("ALTER TABLE vault_metadata ADD COLUMN file_type VARCHAR DEFAULT 'text'")
                self.con.execute("CREATE INDEX IF NOT EXISTS idx_file_type ON vault_metadata(file_type)")

            # --- [v9.7] Multi-Vector & SPLADE ---
            if 'title_embedding' not in col_names:
                print("📐 [v9.7] Multi-Vector: Inizializzazione Title Embedding...")
                self.con.execute("ALTER TABLE vault_metadata ADD COLUMN title_embedding FLOAT[]")

            if 'code_embedding' not in col_names:
                print("📐 [v9.7] Multi-Vector: Inizializzazione Code Embedding...")
                self.con.execute("ALTER TABLE vault_metadata ADD COLUMN code_embedding FLOAT[]")

            if 'sparse_vector' not in col_names:
                print("📐 [v9.7] Multi-Vector: Inizializzazione Sparse Vector (SPLADE)...")
                self.con.execute("ALTER TABLE vault_metadata ADD COLUMN sparse_vector JSON")

            # --- [v9.7] Semantic LLM Cache Table ---
            self.con.execute("""
                CREATE TABLE IF NOT EXISTS llm_cache (
                    prompt_hash VARCHAR PRIMARY KEY,
                    response TEXT,
                    model VARCHAR,
                    created_at TIMESTAMP DEFAULT now(),
                    metadata JSON
                )
            """)
            # --- [v10.0] Epistemic Custody & Wiki Claims ---
            self.con.execute("""
                CREATE TABLE IF NOT EXISTS wiki_claims (
                    claim_id VARCHAR PRIMARY KEY,
                    page_id VARCHAR,
                    claim_text TEXT,
                    source_node_ids JSON,
                    confidence FLOAT,
                    freshness_score FLOAT,
                    contradiction_score FLOAT DEFAULT 0.0,
                    created_at TIMESTAMP DEFAULT now()
                )
            """)

            # --- [v10.2] Decision OS: Decision Genome & Feedback Loop ---
            self.con.execute("""
                CREATE TABLE IF NOT EXISTS decision_genome (
                    decision_id VARCHAR PRIMARY KEY,
                    created_at TIMESTAMP DEFAULT now(),
                    question TEXT,
                    oracle_prediction JSON,
                    confidence DOUBLE DEFAULT 1.0,
                    causal_snapshot_hash VARCHAR,
                    real_outcome JSON
                )
            """)

        except Exception as e:
            print(f"⚠️ [DuckDB Migration] {e}")

        print("🦆 NeuralVault: DuckDB Analytical Engine online.")

    def record_decision(self, decision_id: str, question: str, oracle_prediction: dict, confidence: float, causal_snapshot_hash: str):
        """[v10.2] Registra immutabilmente uno scenario decisionale nel Decision Genome."""
        prediction_json = json.dumps(oracle_prediction)
        self.execute("""
            INSERT OR REPLACE INTO decision_genome 
            (decision_id, created_at, question, oracle_prediction, confidence, causal_snapshot_hash, real_outcome)
            VALUES (?, now(), ?, ?, ?, ?, NULL)
        """, (decision_id, question, prediction_json, confidence, causal_snapshot_hash))

    def update_decision_outcome(self, decision_id: str, real_outcome: dict):
        """[v10.2] Registra l'esito reale di una decisione passata per abilitare la calibrazione empirica."""
        outcome_json = json.dumps(real_outcome)
        self.execute("UPDATE decision_genome SET real_outcome = ? WHERE decision_id = ?", (outcome_json, decision_id))

    def get_decisions(self) -> List[Dict]:
        """[v10.2] Estrae tutti i genomi decisionali archiviati."""
        try:
            res = self.fetchall("SELECT decision_id, created_at, question, oracle_prediction, confidence, causal_snapshot_hash, real_outcome FROM decision_genome ORDER BY created_at DESC")
            decisions = []
            for r in res:
                decisions.append({
                    "decision_id": r[0],
                    "created_at": str(r[1]),
                    "question": r[2],
                    "oracle_prediction": json.loads(r[3]) if r[3] else {},
                    "confidence": r[4],
                    "causal_snapshot_hash": r[5],
                    "real_outcome": json.loads(r[6]) if r[6] else None
                })
            return decisions
        except Exception as e:
            print(f"⚠️ Errore get_decisions: {e}")
            return []

    def add_node(self, node_id: str, collection: str, metadata: Dict):
        """Indicizza un singolo nodo (Fallback)."""
        self.add_nodes_batch([(node_id, collection, metadata)])

    def add_nodes_batch(self, nodes_data: List[tuple]):
        """Indicizza nodi in batch con supporto cognitivo e transazione atomica (v0.5.2)."""
        
        # Prepariamo i dati per l'inserimento di massa
        data_to_insert = []
        for node_id, collection, metadata in nodes_data:
            meta_json = json.dumps(metadata)
            modality = metadata.get("modality", "text")
            importance = metadata.get("importance", 1.0)
            c_hash = metadata.get("content_hash")
            l_state = metadata.get("lifecycle_state", "stable")
            namespace = metadata.get("namespace", "default")
            file_type = metadata.get("file_type", "text")
            
            # [v9.7] Multi-Vector
            t_vector = metadata.get("title_vector")
            c_vector = metadata.get("code_vector")
            s_vector = metadata.get("sparse_vector")
            if s_vector and not isinstance(s_vector, str):
                s_vector = json.dumps(s_vector)

            data_to_insert.append((node_id, collection, namespace, file_type, importance, modality, c_hash, l_state, t_vector, c_vector, s_vector, meta_json))

        # Esecuzione in una singola transazione (Turbo Mode)
        try:
            self.executemany("""
                INSERT OR REPLACE INTO vault_metadata 
                (id, collection, namespace, file_type, created_at, last_access, access_count, importance, modality, content_hash, lifecycle_state, title_embedding, code_embedding, sparse_vector, metadata)
                VALUES (?, ?, ?, ?, now(), now(), 1, ?, ?, ?, ?, ?, ?, ?, ?)
            """, data_to_insert)
        except Exception as e:
            print(f"⚠️ Errore nel Batch Ingest Prefilter: {e}")

    def check_duplicate(self, content_hash: str) -> Optional[str]:
        """Controlla se esiste già un nodo con questo hash. Restituisce l'ID del primo duplicato."""
        if not content_hash: return None
        res = self.fetchone("SELECT id FROM vault_metadata WHERE content_hash = ? LIMIT 1", (content_hash,))
        return res[0] if res else None

    def hit_node(self, node_id: str):
        """Rinforzo sinaptico: Aggiorna l'ultimo accesso e aumenta il conteggio."""
        self.execute(
            "UPDATE vault_metadata SET last_access = now(), access_count = access_count + 1 WHERE id = ?",
            (node_id,)
        )

    def get_cognitive_metadata(self, node_id: str):
        """Recupera metadati cognitivi in modo thread-safe (v9.0)."""
        with self._lock:
            return self.con.execute(
                "SELECT last_access, access_count, importance FROM vault_metadata WHERE id = ?",
                (node_id,)
            ).fetchone()

    def log_event(self, event_type: str, node_id: str = "system", topic: str = None, description: str = "", topic_cluster: str = None, **kwargs):
        """[v4.3.0] Registra un evento nel ledger temporale per la Knowledge Timeline."""
        # [v4.3.1 Fix] Support both positional 'topic' and keyword 'topic_cluster'
        final_topic = topic_cluster or topic or "general"
        self.execute(
            "INSERT INTO knowledge_events (event_type, node_id, topic_cluster, description) VALUES (?, ?, ?, ?)",
            (event_type, node_id, final_topic, description)
        )

    def delete(self, node_id: str) -> bool:
        """Rimuove permanentemente un nodo dai metadati DuckDB."""
        try:
            self.execute("DELETE FROM vault_metadata WHERE id = ?", (node_id,))
            return True
        except Exception as e:
            print(f"DuckDB Delete Error: {e}")
            return False

    def filter(self, sql_where: str) -> List[str]:
        """Esegue una query SQL per trovare gli ID che soddisfano il filtro."""
        try:
            # Query ultra-veloce (DuckDB vince su tutto per analytics locale)
            query = f"SELECT id FROM vault_metadata WHERE {sql_where}"
            res = self.fetchall(query)
            return [r[0] for r in res]
        except Exception as e:
            print(f"⚠️ Errore nel Prefilter SQL: {e}")
            return []

    def count(self) -> int:
        res = self.fetchone("SELECT count(*) FROM vault_metadata")
        return res[0] if res else 0

    def query_nodes(self, sql_where: str, limit: int = 100) -> List[Dict]:
        """[v5.1] Esegue una query complessa e restituisce i dati completi del nodo (id, text, metadata)."""
        try:
            # Recuperiamo i dati e il testo dal tier EPISODIC (che contiene il backup dei nodi in Limbo)
            query = f"""
                SELECT m.id, m.metadata, m.lifecycle_state 
                FROM vault_metadata m 
                WHERE {sql_where} 
                LIMIT {limit}
            """
            res = self.fetchall(query)
            nodes = []
            for r in res:
                nodes.append({
                    "id": r[0],
                    "metadata": json.loads(r[1]) if isinstance(r[1], str) else r[1],
                    "lifecycle_state": r[2]
                })
            return nodes
        except Exception as e:
            print(f"⚠️ Errore nel query_nodes: {e}")
            return []

    # --- v1.1.0: Lifecycle & Episodic Memory ---
    
    def update_lifecycle_state(self, node_id: str, new_state: str):
        """Aggiorna lo stato del nodo nella macchina a stati (v1.1.0)."""
        self.execute(
            "UPDATE vault_metadata SET lifecycle_state = ? WHERE id = ?",
            (new_state.lower(), node_id)
        )

    def protect_node_persistent(self, node_id: str, rejected_by: str, reason: str, level: int = 1, confidence: float = 1.0):
        """Salva permanentemente un rifiuto utente o un'istruzione di protezione."""
        try:
            self.execute("""
                INSERT OR REPLACE INTO episodic_memory 
                (node_id, protected_at, rejected_by, reason, protection_level, confidence)
                VALUES (?, now(), ?, ?, ?, ?)
            """, (node_id, rejected_by, reason, level, confidence))
            # Promuove il nodo a PROTECTED anche nel lifecycle
            self.update_lifecycle_state(node_id, "protected")
        except Exception as e:
            print(f"⚠️ [Episodic Memory Store] {e}")

    def is_node_protected(self, node_id: str) -> bool:
        """Controlla se un nodo è sotto protezione persistente (Episodic Memory)."""
        res = self.fetchone("SELECT node_id FROM episodic_memory WHERE node_id = ?", (node_id,))
        return res is not None

    def get_protected_nodes(self) -> List[str]:
        """Restituisce tutti gli ID protetti."""
        res = self.fetchall("SELECT node_id FROM episodic_memory")
        return [r[0] for r in res]

    def get_knowledge_sources(self) -> List[Dict]:
        """Raggruppa la conoscenza per sorgente originaria (Analytic Hub)."""
        try:
            # Estraiamo 'source' e 'title' dal JSON dei metadati
            query = """
                SELECT 
                    metadata->>'$.source' as source,
                    metadata->>'$.title' as title,
                    count(*) as node_count,
                    min(created_at) as first_seen,
                    max(created_at) as last_seen
                FROM vault_metadata
                GROUP BY source, title
                ORDER BY first_seen DESC
            """
            res = self.fetchall(query)
            sources = []
            for r in res:
                sources.append({
                    "source": r[0] or "Unknown Source",
                    "title": r[1] or r[0] or "Agent Asset",
                    "nodes": r[2],
                    "date": r[3].strftime("%Y-%m-%d %H:%M:%S") if r[3] else "---",
                    "timestamp": r[3].timestamp() if r[3] else 0
                })
            return sources
        except Exception as e:
            print(f"⚠️ Errore aggregazione Inventory: {e}")
            return []

    def execute(self, query: str, params: tuple = ()):
        """Esegue una query SQL in modo thread-safe (Senza ritorno risultati)."""
        with self._lock:
            self.con.execute(query, params)

    def executemany(self, query: str, params: List[tuple]):
        """Esegue un batch di query SQL in modo thread-safe."""
        with self._lock:
            return self.con.executemany(query, params)

    def fetchone(self, query: str, params: tuple = ()):
        """Esegue e recupera il primo risultato in modo thread-safe."""
        with self._lock:
            return self.con.execute(query, params).fetchone()

    def fetchall(self, query: str, params: tuple = ()):
        """Esegue e recupera tutti i risultati in modo thread-safe."""
        with self._lock:
            return self.con.execute(query, params).fetchall()

    def fetchdf(self, query: str, params: tuple = ()):
        """Recupera un DataFrame in modo thread-safe."""
        with self._lock:
            return self.con.execute(query, params).fetchdf()

    def vector_search(self, vector: List[float], column: str = "title_embedding", limit: int = 10) -> List[tuple]:
        """
        [v9.7] Ricerca vettoriale analitica su colonne Named Vectors.
        Utilizza la similarità coseno nativa di DuckDB.
        """
        with self._lock:
            # DuckDB richiede che il vettore sia passato come lista Python
            query = f"""
                SELECT id, 1 - list_cosine_distance({column}, ?::FLOAT[]) as score
                FROM vault_metadata
                WHERE {column} IS NOT NULL
                ORDER BY score DESC
                LIMIT ?
            """
            return self.con.execute(query, (vector, limit)).fetchall()

    def close(self):
        """Chiude la connessione DuckDB in modo sicuro."""
        if self.con:
            self.con.close()
            self.con = None

    # --- [v9.7] Semantic LLM Cache ---
    def get_llm_cache(self, prompt: str, model: str) -> Optional[str]:
        """Recupera una risposta LLM dalla cache se presente (v9.7)."""
        p_hash = hashlib.sha256(prompt.encode()).hexdigest()
        res = self.fetchone("SELECT response FROM llm_cache WHERE prompt_hash = ? AND model = ?", (p_hash, model))
        if res:
            print(f"🎯 [LLM-Cache] HIT per {model} (hash: {p_hash[:8]})")
            return res[0]
        return None

    def set_llm_cache(self, prompt: str, model: str, response: str, metadata: Dict = None):
        """Salva una risposta LLM nella cache persistente (v9.7)."""
        p_hash = hashlib.sha256(prompt.encode()).hexdigest()
        meta_json = json.dumps(metadata or {})
        self.execute(
            "INSERT OR REPLACE INTO llm_cache (prompt_hash, response, model, metadata) VALUES (?, ?, ?, ?)",
            (p_hash, response, model, meta_json)
        )

    def get_audit_stats(self) -> Dict:
        """Estrae statistiche di integrità e performance dal database analitico."""
        try:
            total_nodes = self.fetchone("SELECT COUNT(*) FROM vault_metadata")[0]
            total_events = self.fetchone("SELECT COUNT(*) FROM knowledge_events")[0]
            last_event = self.fetchone("SELECT MAX(timestamp) FROM knowledge_events")[0]
            namespaces = self.fetchone("SELECT COUNT(DISTINCT namespace) FROM vault_metadata")[0]
            
            # Calcolo densità (esempio: eventi per nodo)
            density = total_events / total_nodes if total_nodes > 0 else 0
            
            # Recupero path del database in modo sicuro
            db_info = self.execute("PRAGMA database_list").fetchall()
            db_path = db_info[0][2]
            
            return {
                "status": "healthy",
                "total_nodes": total_nodes,
                "total_events": total_events,
                "last_sync": str(last_event),
                "namespaces": namespaces,
                "ledger_density": round(density, 2),
                "db_size_kb": os.path.getsize(str(db_path)) // 1024 if db_path else 0
            }
        except Exception as e:
            return {"status": "degraded", "error": str(e)}
