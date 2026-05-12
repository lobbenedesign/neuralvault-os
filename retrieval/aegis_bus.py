import json
import time
import uuid
import os
from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional

@dataclass
class AegisEvent:
    """[v9.0] Atomic Immutable Event for NeuralVault Event Sourcing."""
    identity: str       # UUID v4
    timestamp: float    # Unix Epoch
    event_type: str     # Action Type (e.g. NODE_CREATED)
    payload: Dict[str, Any]
    signature: Optional[str] = None # Future: RSA-2048 signing

    @classmethod
    def create(cls, event_type: str, payload: Dict[str, Any]):
        return cls(
            identity=str(uuid.uuid4()),
            timestamp=time.time(),
            event_type=event_type,
            payload=payload
        )

class AegisEventBus:
    """[v9.0] Sovereign Event Bus for CQRS Shadow Logging."""
    def __init__(self, log_path: str = "vault_data/aegis_event_log.jsonl"):
        self.log_path = log_path
        os.makedirs(os.path.dirname(self.log_path), exist_ok=True)
        print(f"🛡️ [Aegis] Event Bus Initialized: {self.log_path}")

    def emit(self, event_type: str, payload: Dict[str, Any]):
        """Emit an event and persist it to the shadow log."""
        event = AegisEvent.create(event_type, payload)
        try:
            with open(self.log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(asdict(event)) + "\n")
            return event.identity
        except Exception as e:
            print(f"⚠️ [Aegis] Event Emission Error: {e}")
            return None

# Global Instance
aegis_bus = AegisEventBus()
