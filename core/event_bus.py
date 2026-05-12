import uuid
import json
import time
import hashlib
import threading
import os
from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional

@dataclass
class AegisEvent:
    """Il DNA Immutabile di ogni modifica al sistema"""
    event_id: str
    event_type: str
    timestamp: str
    sequence: int
    source: Dict[str, Any]
    payload: Dict[str, Any]
    correlation_id: str
    causation_id: Optional[str]
    checksum: str

class AegisEventBus:
    """
    Singleton Event Bus thread-safe per l'Event Sourcing (L2 Aegis LogStore).
    Implementa Append-Only Logging con Sequential Ordering e Checksum Validation.
    """
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if not cls._instance:
                cls._instance = super(AegisEventBus, cls).__new__(cls)
                cls._instance._init_bus()
            return cls._instance

    def _init_bus(self):
        # Il file fisico dell'Event Log
        self.log_file = os.path.join(os.path.dirname(__file__), '..', 'aegis_event_log.jsonl')
        self.sequence_counter = self._recover_sequence()
        self.seq_lock = threading.Lock()
        
    def _recover_sequence(self) -> int:
        """Legge l'ultimo evento registrato per ripristinare il contatore di sequenza al riavvio."""
        if not os.path.exists(self.log_file):
            return 0
        try:
            with open(self.log_file, 'rb') as f:
                # Cerca l'ultima riga in modo efficiente senza caricare tutto in RAM
                try:
                    f.seek(-2, os.SEEK_END)
                    while f.read(1) != b'\n':
                        f.seek(-2, os.SEEK_CUR)
                except OSError:
                    f.seek(0)
                last_line = f.readline().decode('utf-8').strip()
                if last_line:
                    last_event = json.loads(last_line)
                    return last_event.get('sequence', 0)
        except Exception as e:
            print(f"⚠️ [AegisEventBus] Errore nel recupero sequenza: {e}")
        return 0

    def _generate_checksum(self, event_id: str, timestamp: str, sequence: int, payload: dict) -> str:
        """Genera un hash crittografico per garantire l'immutabilità e rilevare bit-rot."""
        payload_str = json.dumps(payload, sort_keys=True)
        raw_data = f"{event_id}|{timestamp}|{sequence}|{payload_str}"
        return hashlib.sha256(raw_data.encode('utf-8')).hexdigest()

    def publish(self, event_type: str, payload: Dict[str, Any], source: Dict[str, Any], 
                correlation_id: Optional[str] = None, causation_id: Optional[str] = None) -> AegisEvent:
        """Pubblica un evento. Genera l'id, il timestamp, la sequenza e scrive su disco."""
        
        event_id = str(uuid.uuid4()) # In un sistema enterprise si potrebbe usare un UUIDv7
        # Timestamp ISO 8601 con microsecondi reali
        timestamp = time.strftime('%Y-%m-%dT%H:%M:%S.') + f"{int(time.time() * 1000000) % 1000000:06d}Z"
        
        # Incremento atomico del contatore (risolve le collisioni multi-agente)
        with self.seq_lock:
            self.sequence_counter += 1
            seq = self.sequence_counter
            
        if correlation_id is None:
            # Un gruppo di eventi correlati (es. Node creato + 3 Edge) condividerà questo ID
            correlation_id = str(uuid.uuid4())
            
        checksum = self._generate_checksum(event_id, timestamp, seq, payload)
        
        event = AegisEvent(
            event_id=event_id,
            event_type=event_type,
            timestamp=timestamp,
            sequence=seq,
            source=source,
            payload=payload,
            correlation_id=correlation_id,
            causation_id=causation_id,
            checksum=checksum
        )
        
        # Scrittura Append-Only protetta da Lock Globale per integrità del file
        with self._lock:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(asdict(event)) + '\n')
                
        # [FASE 3 PREP]: Qui in futuro aggiungeremo: self._update_projection_sync(event)
        
        return event

# --- DEMO DI UTILIZZO ---
if __name__ == "__main__":
    print("🚀 Test Inizializzazione Aegis Event Bus...")
    bus = AegisEventBus()
    
    print("📝 Simulazione Scrittura Eventi da Agente...")
    evt1 = bus.publish(
        event_type="NODE_CREATED",
        source={"agent": "FS-77", "session": "test_1"},
        payload={"id": "node_01", "label": "Singolarità Tecnologica", "confidence": 0.95}
    )
    
    evt2 = bus.publish(
        event_type="EDGE_CREATED",
        source={"agent": "FS-77", "session": "test_1"},
        correlation_id=evt1.correlation_id, # Fa parte della stessa transazione logica
        causation_id=evt1.event_id, # Conseguenza dell'evento 1
        payload={"from": "node_01", "to": "node_02", "relation": "CAUSES"}
    )
    
    print(f"✅ Eventi registrati in {bus.log_file}")
    print(f"Ultima Sequenza: {bus.sequence_counter}")
    print(f"Checksum Evento 1: {evt1.checksum}")
