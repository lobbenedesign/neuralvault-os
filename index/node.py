"""
neuralvault.core.node
─────────────────────
Unità fondamentale del sistema. v0.2.5 con Versioning (Fase 14).
"""

from __future__ import annotations
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional, Dict, List
import numpy as np


class MemoryTier(str, Enum):
    WORKING  = "working"
    EPISODIC = "episodic"
    SEMANTIC = "semantic"


class NodeLifecycleState(str, Enum):
    """
    🧬 [v1.1.0 Sovereign Lifecycle]
    Definisce gli stati formali di un nodo nel sistema.
    """
    PENDING          = "pending"          # Appena ingerito, in periodo di grazia (30 min)
    ORPHAN           = "orphan"           # Nodo isolato, in attesa di connessioni
    POTENTIAL        = "potential"        # Nodo con alto potenziale semantico (Spark)
    INDEXING         = "indexing"         # Archi semantici in costruzione
    STABLE           = "stable"           # Validato e pronto per gli agenti
    IN_JUDGEMENT     = "in_judgement"     # Sotto scrutinio della Supreme Court
    WASTE_PENDING    = "waste_pending"    # Marcato per l'eliminazione dal Janitron
    PROTECTED        = "protected"        # Memoria Episodica: Protetto permanentemente
    TOMBSTONE        = "tombstone"        # Eliminato, rimane solo la lapide crittografica
    DELETED          = "tombstone"        # Alias per compatibilità con l'Orchestrator
    ARCHIVED         = "archived"         # Memoria sbiadita (Ebbinghaus Decay)

# Alias per compatibilità con il vecchio sistema (v17.0)
NodeState = NodeLifecycleState


class RelationType(str, Enum):
    CITES        = "cites"
    CONTRADICTS  = "contradicts"
    UPDATES      = "updates"
    PREREQUISITE = "prerequisite"
    EXAMPLE_OF   = "example_of"
    SAME_ENTITY  = "same_entity"
    SEQUENTIAL   = "sequential"
    SYNAPSE      = "synapse"
    SIMILARITY   = "similarity"
    EQUIVALENT   = "equivalent"
    PARENT       = "parent"
    CHILD        = "child"
    QUANTUM_LINK = "quantum_link"
    SEMANTIC     = "semantic" 
    RESOLVED_BY  = "resolved_by" 
    CAUSES       = "causes"      # [v7.0] Causal Logic
    PREVENTS     = "prevents"    # [v7.0] Causal Logic
    REQUIRES     = "requires"    # [v7.0] Causal Logic
    ENABLES      = "enables"     # [v7.0] Causal Logic
    ENHANCES     = "enhances"    # [v7.0] Causal Logic
    SUPERSEDES   = "supersedes"  # [v7.0] Causal Logic
    REFLECTION_ANCHOR = "reflection_anchor" # [v12.0] Yoda Reflection
    GALAXY_ANCHOR     = "galaxy_anchor"     # [v12.0] Galaxy connection to Nebula
    SKYWALKER_ANCHOR  = "skywalker_anchor"  # [v13.0] Red Anchor
    YODA_ANCHOR       = "yoda_anchor"       # [v13.0] Green Anchor
    GALAXY_INTERNAL   = "galaxy_internal"   # [v12.0] Links within a Galaxy
    SUPER_GALAXY      = "super_galaxy"      # [v13.6] Mandalorian unified formations
    HERD_CONNECTION   = "herd_connection"   # [v13.6] Mandalorian herding links
    GALAXY_TETHER     = "galaxy_tether"     # [v13.6] Mandalorian galaxy tether
    HYPER_CONVERGENCE = "hyper_convergence" # [v9.0] Bayesian Hyper-Graph
    HYPER_DIVERGENCE  = "hyper_divergence"  # [v9.0] Bayesian Hyper-Graph



@dataclass
class SemanticEdge:
    target_id:        str
    relation:         RelationType
    weight:           float = 1.0
    logic_weight:     float = 1.0  # [v3.0]: Ponderazione logica (Rilevanza per il task)
    emotional_weight: float = 0.5  # [v3.0]: Carica 'emotiva' o urgenza del dato
    bidirectional:    bool  = False
    created_at:       float = field(default_factory=time.time)
    source:           str   = "manual"
    reason:           Optional[str] = None # [Phase 3]: Perché questi nodi sono collegati?
    metadata:         Dict[str, Any] = field(default_factory=dict) # [v8.0] Per attributi extra dell'arco

@dataclass
class HyperEdge:
    """
    🕸️ [v9.0] Bayesian Hyper-Edge.
    Connects a set of source nodes to a set of target nodes.
    Used for multi-causal reasoning ({A, B} -> C).
    """
    source_ids:      List[str]
    target_ids:      List[str]
    relation:        RelationType
    weight:          float = 1.0
    logic_weight:    float = 1.0
    created_at:      float = field(default_factory=time.time)
    metadata:        Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not 0.0 <= self.weight <= 1.0:
            raise ValueError(f"Edge weight must be in [0, 1], got {self.weight}")
        if isinstance(self.relation, str):
            self.relation = RelationType(self.relation)


@dataclass
class VaultNode:
    # ── Identificazione ──────────────────────────────────────
    id:             str
    collection:     str   = "default"
    namespace:      str   = "default"
    version:        int   = 1           # Fase 14: Cache Versioning

    # ── Contenuto ────────────────────────────────────────────
    text:           str   = ""
    vector:         np.ndarray | None = None
    sparse_vector:  dict[int, float] | None = None

    # ── Metadati utente ──────────────────────────────────────
    metadata:       dict[str, Any] = field(default_factory=dict)

    # ── Context graph ────────────────────────────────────────
    edges:          list[SemanticEdge] = field(default_factory=list)
    hyper_edges:    list[HyperEdge]    = field(default_factory=list) # [v9.0]

    # ── Memory management ────────────────────────────────────
    tier:                  MemoryTier = MemoryTier.SEMANTIC
    access_count:          int        = 0
    last_accessed:         float      = field(default_factory=time.time)
    created_at:            float      = field(default_factory=time.time)
    agent_relevance_score: float      = 0.0
    ingestion_status:      str        = "STABLE" # Default per i nodi esistenti

    @property
    def title(self) -> str:
        """[v8.2] Estrae un titolo rappresentativo dal contenuto o metadati."""
        return self.metadata.get("title") or self.text.split("\n")[0][:50] or self.id

    def __post_init__(self):
        if self.vector is not None and not isinstance(self.vector, np.ndarray):
            # Se siamo in float16 mode, convertiamo subito
            self.vector = np.array(self.vector, dtype=self.vector.dtype if hasattr(self.vector, 'dtype') else np.float32)
        
        if self.vector is not None:
            # Assicuriamoci che la normalizzazione avvenga con precisione sufficiente
            # anche se il vettore è float16
            norm = np.linalg.norm(self.vector.astype(np.float32))
            if norm > 0:
                self.vector = self.vector / norm.astype(self.vector.dtype)

    def bump_version(self) -> None:
        """Incrementa la versione del nodo dopo un aggiornamento."""
        self.version += 1
        self.last_accessed = time.time()

    def touch(self) -> None:
        self.access_count += 1
        self.last_accessed = time.time()

    def add_edge(self, target_id: str, relation: RelationType | str, weight: float = 1.0, source: str = "manual", **kwargs) -> SemanticEdge:
        if isinstance(relation, str):
            relation = RelationType(relation)
        
        # Estraiamo i campi validi per SemanticEdge dai kwargs
        edge_data = {
            "target_id": target_id,
            "relation": relation,
            "weight": weight,
            "source": source
        }
        # Mappiamo i campi extra se presenti
        for field_name in ["logic_weight", "emotional_weight", "bidirectional", "reason", "metadata"]:
            if field_name in kwargs:
                edge_data[field_name] = kwargs[field_name]
                
        edge = SemanticEdge(**edge_data)
        
        existing = {(e.target_id, e.relation) for e in self.edges}
        if (target_id, relation) not in existing:
            self.edges.append(edge)
        return edge

    def to_dict(self) -> dict:
        return {
            "id":                    self.id,
            "collection":            self.collection,
            "namespace":             self.namespace,
            "version":               self.version,
            "text":                  self.text,
            "vector":                self.vector.tolist() if self.vector is not None else None,
            "metadata":              self.metadata,
            "edges":                 [
                {
                    "target_id":     e.target_id,
                    "relation":      e.relation.value,
                    "weight":        e.weight,
                    "logic_weight":  e.logic_weight,
                    "emotional_weight": e.emotional_weight,
                    "bidirectional": e.bidirectional,
                    "created_at":    e.created_at,
                    "source":        e.source,
                }
                for e in self.edges
            ],
            "tier":                  self.tier.value,
            "access_count":          self.access_count,
            "last_accessed":         self.last_accessed,
            "created_at":            self.created_at,
            "agent_relevance_score": self.agent_relevance_score,
        }

    @classmethod
    def from_dict(cls, data: dict, vector: np.ndarray | None = None,
                  sparse_vector: dict | None = None) -> "VaultNode":
        edges = [
            SemanticEdge(
                target_id=e["target_id"],
                relation=RelationType(e["relation"]),
                weight=e["weight"],
                logic_weight=e.get("logic_weight", 1.0),
                emotional_weight=e.get("emotional_weight", 0.5),
                bidirectional=e.get("bidirectional", False),
                created_at=e.get("created_at", time.time()),
                source=e.get("source", "manual"),
            )
            for e in data.get("edges", [])
        ]
        node = cls(
            id=data["id"],
            collection=data.get("collection", "default"),
            namespace=data.get("namespace", "default"),
            version=data.get("version", 1),
            text=data.get("text", ""),
            vector=vector,
            sparse_vector=sparse_vector,
            metadata=data.get("metadata", {}),
            edges=edges,
            tier=MemoryTier(data.get("tier", "semantic")),
            access_count=data.get("access_count", 0),
            last_accessed=data.get("last_accessed", time.time()),
            created_at=data.get("created_at", time.time()),
            agent_relevance_score=data.get("agent_relevance_score", 0.0),
        )
        if vector is not None:
            node.vector = vector
        elif "vector" in data and data["vector"] is not None:
            node.vector = np.array(data["vector"], dtype=np.float32)

        return node


    @staticmethod
    def generate_id() -> str:
        return str(uuid.uuid4())


@dataclass
class QueryResult:
    node:         VaultNode
    dense_score:  float = 0.0
    sparse_score: float = 0.0
    graph_score:  float = 0.0
    rerank_score: float = 0.0
    cognitive_score: float = 0.0
    memory_strength: float = 1.0
    final_score:  float = 0.0
    temporal_confidence: float = 1.0 # [v4.3.0] Gap #4
    path:         str   = "direct"

    def __lt__(self, other: "QueryResult") -> bool:
        return self.final_score > other.final_score
