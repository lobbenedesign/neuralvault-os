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
    WIKI_GENERATED = "WIKI_GENERATED"
    TEMPORAL_SHIFT = "TEMPORAL_SHIFT"

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
        try:
            self.main_loop = asyncio.get_event_loop()
        except RuntimeError:
            self.main_loop = None

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
            # Tenta di recuperare il loop corrente nel thread chiamante
            try:
                current_loop = asyncio.get_running_loop()
            except RuntimeError:
                current_loop = None

            if current_loop and current_loop.is_running():
                # Se siamo già in un thread con un loop attivo, usiamo quello
                current_loop.create_task(self.emit(event_type, data, priority))
            elif self.main_loop and self.main_loop.is_running():
                # Se siamo in un thread senza loop (es. Kinetic Engine), usiamo il loop principale
                asyncio.run_coroutine_threadsafe(self.emit(event_type, data, priority), self.main_loop)
            else:
                # Fallback: crea un loop temporaneo se possibile (molto raro in produzione)
                asyncio.run(self.emit(event_type, data, priority))
        except Exception as e:
            self.logger.error(f"❌ Error in emit_sync: {e}")

    def get_history(self) -> List[Dict]:
        return self.history
