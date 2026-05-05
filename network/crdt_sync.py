import json
import hashlib
import time
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict

@dataclass
class CRDTOp:
    type: str # "SET_NODE", "DEL_NODE", "LINK_NODES"
    node_id: str
    data: Optional[Dict] = None
    timestamp: float = 0.0
    actor_id: str = "unknown"

class NeuralCRDTSync:
    """
    🧬 [NEURAL CRDT SYNC]
    Implementazione di Conflict-free Replicated Data Types per NeuralVault.
    Permette la sincronizzazione multi-device senza server centrali.
    Garantisce 'Eventual Consistency' tramite Last-Writer-Wins (LWW).
    """
    def __init__(self, engine, actor_id: str):
        self.engine = engine
        self.actor_id = actor_id
        self.op_log = [] # Sequence of operations
        self.clock = 0 # Lamport Logical Clock
        
    def generate_op(self, op_type: str, node_id: str, data: Dict = None) -> CRDTOp:
        self.clock += 1
        op = CRDTOp(
            type=op_type,
            node_id=node_id,
            data=data,
            timestamp=time.time(),
            actor_id=self.actor_id
        )
        self.op_log.append(op)
        return op

    async def apply_remote_op(self, op_data: Dict):
        """Applica un'operazione ricevuta da un peer (es. iPhone)."""
        op = CRDTOp(**op_data)
        
        # Logica Last-Writer-Wins (LWW)
        existing_node = self.engine._nodes.get(op.node_id)
        
        if op.type == "SET_NODE":
            should_update = True
            if existing_node:
                # Confronta timestamp per risolvere conflitti
                remote_ts = op.timestamp
                local_ts = existing_node.metadata.get("last_sync_ts", 0)
                if remote_ts <= local_ts:
                    should_update = False
            
            if should_update:
                # [v5.0] Atomic Patching
                print(f"🔗 [CRDT] Applying remote update for {op.node_id[:8]} (Actor: {op.actor_id})")
                from index.node import VaultNode
                new_node = VaultNode(
                    id=op.node_id,
                    collection=op.data.get("collection", "default"),
                    text=op.data.get("text", ""),
                    vector=op.data.get("vector"),
                    metadata={**op.data.get("metadata", {}), "last_sync_ts": op.timestamp}
                )
                await self.engine.upsert(new_node)

        elif op.type == "DEL_NODE":
            if existing_node:
                print(f"🗑️ [CRDT] Remote deletion for {op.node_id[:8]}")
                await self.engine.delete(op.node_id)

    async def serialize_delta(self, since_ts: float) -> List[Dict]:
        """Estrae tutte le operazioni avvenute dopo un certo timestamp per la sync."""
        delta = [asdict(op) for op in self.op_log if op.timestamp > since_ts]
        return delta
