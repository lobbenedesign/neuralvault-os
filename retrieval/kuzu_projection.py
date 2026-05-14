import kuzu
import os
import time
import logging
from typing import Dict, Any, List

logger = logging.getLogger("KuzuProjection")

class KuzuProjection:
    """
    KùzuDB Projection for NeuralVault [v9.0].
    Provides a high-performance graph view of the event-sourced vault.
    """
    
    def __init__(self, db_path: str = "vault_data/kuzudb"):
        self.db_path = db_path
        parent = os.path.dirname(db_path)
        if parent:
            os.makedirs(parent, exist_ok=True)
        
        self.db = kuzu.Database(db_path)
        self.conn = kuzu.Connection(self.db)
        self._initialize_schema()
        logger.info(f"🦆 [Kùzu] Graph Projection Initialized: {db_path}")

    def _initialize_schema(self):
        """Initialize the Graph Schema if not exists."""
        try:
            # Nodes Table
            self.conn.execute("""
                CREATE NODE TABLE IF NOT EXISTS KnowledgeNode (
                    id STRING PRIMARY KEY,
                    title STRING,
                    type STRING,
                    created_at DOUBLE
                )
            """)
            
            # Causal Edges Table
            self.conn.execute("""
                CREATE REL TABLE IF NOT EXISTS CausalEdge (
                    FROM KnowledgeNode TO KnowledgeNode,
                    relation_type STRING,
                    weight DOUBLE,
                    MANY_MANY
                )
            """)
            # 🌌 [v9.0] Hyper-Graph Tables
            self.conn.execute("""
                CREATE NODE TABLE IF NOT EXISTS HyperLink (
                    id STRING PRIMARY KEY,
                    logic_type STRING
                )
            """)
            
            self.conn.execute("""
                CREATE REL TABLE IF NOT EXISTS PartOf (
                    FROM KnowledgeNode TO HyperLink,
                    MANY_MANY
                )
            """)
            
            self.conn.execute("""
                CREATE REL TABLE IF NOT EXISTS Influences (
                    FROM HyperLink TO KnowledgeNode,
                    weight DOUBLE,
                    MANY_MANY
                )
            """)
            logger.debug("Kùzu Schema verified.")
        except Exception as e:
            # Table might already exist, ignore errors for now or handle specific ones
            if "already exists" not in str(e).lower():
                logger.error(f"Kùzu Schema Error: {e}")

    def handle_event(self, event_type: str, payload: Dict[str, Any]):
        """Consumes Aegis events and updates the Kùzu Graph."""
        try:
            if event_type == "NODE_CREATED":
                self.conn.execute(
                    "CREATE (:KnowledgeNode {id: $id, title: $title, type: $type, created_at: $ts})",
                    {"id": payload['id'], "title": payload.get('title', 'Untitled'), "type": payload.get('type', 'generic'), "ts": payload.get('timestamp', 0.0)}
                )
                
            elif event_type == "CAUSAL_EDGE_ADDED":
                self.conn.execute(
                    "MATCH (a:KnowledgeNode {id: $src}), (b:KnowledgeNode {id: $tgt}) "
                    "CREATE (a)-[:CausalEdge {relation_type: $rel, weight: $w}]->(b)",
                    {"src": payload['source'], "tgt": payload['target'], "rel": payload['type'], "w": payload.get('weight', 1.0)}
                )
                
            elif event_type == "HYPER_EDGE_CREATED":
                # {sources: [], target: id, logic: "AND/OR"}
                h_id = f"hyper_{payload['target']}_{time.time()}"
                self.conn.execute("CREATE (:HyperLink {id: $id, logic_type: $logic})", {"id": h_id, "logic": payload.get('logic', 'AND')})
                
                # Connect sources to HyperLink
                for src_id in payload.get('sources', []):
                    self.conn.execute(
                        "MATCH (a:KnowledgeNode {id: $src}), (h:HyperLink {id: $hid}) "
                        "CREATE (a)-[:PartOf]->(h)",
                        {"src": src_id, "hid": h_id}
                    )
                
                # Connect HyperLink to Target
                self.conn.execute(
                    "MATCH (h:HyperLink {id: $hid}), (b:KnowledgeNode {id: $tgt}) "
                    "CREATE (h)-[:Influences {weight: $w}]->(b)",
                    {"hid": h_id, "tgt": payload['target'], "w": payload.get('weight', 1.0)}
                )
                logger.info(f"🌌 [Hyper-Graph] Created Hyper-Edge {h_id}")

            elif event_type == "SITREP_GENERATED":
                # Mark nodes mentioned in SITREP as 'active' or update metadata
                pass
                
        except Exception as e:
            logger.error(f"Kùzu Event Processing Error ({event_type}): {e}")

    def query_causal_path(self, start_id: str, end_id: str) -> List[Dict]:
        """Find the causal path between two nodes using Cypher."""
        try:
            result = self.conn.execute(
                "MATCH (a:KnowledgeNode)-[:CausalEdge]->(b:KnowledgeNode) WHERE a.id = $start RETURN a.id",
                {"start": start_id}
            )
            paths = []
            while result.has_next():
                paths.append(result.get_next())
            return paths
        except Exception as e:
            logger.error(f"Kùzu Query Error: {e}")
            return []
