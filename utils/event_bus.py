import asyncio
import logging
import json
import time
from typing import Any, Dict, List, Callable, Awaitable
from enum import Enum

class NeuralEventType(str, Enum):
    NODE_INGESTED = "NODE_INGESTED"
    QUERY_RECEIVED = "QUERY_RECEIVED"
    COURT_REQUIRED = "COURT_REQUIRED"
    EVOLUTION_ADVICE_NEEDED = "EVOLUTION_ADVICE_NEEDED"
    SYSTEM_ALERT = "SYSTEM_ALERT"
    GALAXY_UPDATE = "GALAXY_UPDATE"
    SHADOW_SIMULATION_COMPLETED = "SHADOW_SIMULATION_COMPLETED"

class NeuralEvent:
    def __init__(self, event_type: NeuralEventType, data: Dict[str, Any], priority: int = 1):
        self.id = f"ev_{int(time.time() * 1000)}"
        self.type = event_type
        self.data = data
        self.priority = priority
        self.timestamp = time.time()

class NeuralEventBus:
    """
    📡 NeuralVault v6.0: Reactive Neural Event Bus (NEB).
    Sostituisce il Polling con una comunicazione asincrona basata su eventi.
    """
    def __init__(self):
        self.subscribers: Dict[NeuralEventType, List[Callable[[NeuralEvent], Awaitable[None]]]] = {
            t: [] for t in NeuralEventType
        }
        self.logger = logging.getLogger("NeuralEventBus")
        self.history: List[Dict] = []
        self.max_history = 100

    def subscribe(self, event_type: NeuralEventType, callback: Callable[[NeuralEvent], Awaitable[None]]):
        """Registra un listener per un tipo di evento."""
        if callback not in self.subscribers[event_type]:
            self.subscribers[event_type].append(callback)
            self.logger.info(f"📡 Subscriber added for {event_type}")

    async def emit(self, event_type: NeuralEventType, data: Dict[str, Any], priority: int = 1):
        """Distribuisce un evento a tutti i sottoscrittori interessati."""
        event = NeuralEvent(event_type, data, priority)
        
        # Logging per telemetria
        self.history.append({
            "id": event.id,
            "type": event.type,
            "timestamp": event.timestamp,
            "priority": event.priority
        })
        if len(self.history) > self.max_history:
            self.history.pop(0)

        self.logger.debug(f"📢 Emitting Event: {event_type} ({event.id})")
        
        # Notifica asincrona
        tasks = []
        for callback in self.subscribers.get(event_type, []):
            tasks.append(asyncio.create_task(callback(event)))
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    def emit_sync(self, event_type: NeuralEventType, data: Dict[str, Any], priority: int = 1):
        """Versione sincrona di emit per componenti legacy o thread-based."""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                loop.create_task(self.emit(event_type, data, priority))
            else:
                loop.run_until_complete(self.emit(event_type, data, priority))
        except Exception as e:
            self.logger.error(f"❌ Error in emit_sync: {e}")

    def get_history(self) -> List[Dict]:
        return self.history
