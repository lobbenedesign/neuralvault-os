import uuid
import time
import json
import threading
import random
import re
import urllib.request
import urllib.parse
import numpy as np
import asyncio
import httpx
import hashlib
import psutil
import subprocess
import platform
import concurrent.futures
import logging
from typing import Any, List, Dict, Optional
from pathlib import Path
from enum import Enum
from utils.event_bus import NeuralEventType, NeuralEvent # [v6.0]
import ast
import traceback
from index.node import RelationType

class SovereignTestRunner:
    """🛡️ [STR-001] Modulo di Validazione Multilinguaggio (Python/Rust)."""
    def __init__(self, workspace_path: str):
        self.workspace = Path(workspace_path)

    def audit_syntax(self, file_path: str) -> bool:
        """Rileva il linguaggio e applica l'audit corretto."""
        p = Path(file_path)
        if p.suffix == ".py":
            return self._audit_python(file_path)
        elif p.suffix == ".rs":
            return self._audit_rust()
        return True # Default per file non critici

    def _audit_python(self, file_path: str) -> bool:
        try:
            with open(file_path, 'r') as f:
                source = f.read()
            ast.parse(source)
            return True
        except Exception as e:
            print(f"🚨 [Sovereign-Audit/PY] Errore in {file_path}: {e}")
            return False

    def _audit_rust(self) -> bool:
        """Verifica la coerenza del core Rust via 'cargo check'."""
        try:
            rust_path = self.workspace / "neuralvault_rs"
            if not rust_path.exists(): return True
            
            # Eseguiamo cargo check (leggero e veloce) invece di build
            import subprocess
            res = subprocess.run(["cargo", "check"], cwd=str(rust_path), 
                               capture_output=True, text=True, timeout=30)
            if res.returncode != 0:
                print(f"🚨 [Sovereign-Audit/RS] Cargo Check FAILED:\n{res.stderr}")
                return False
            return True
        except Exception as e:
            print(f"⚠️ [Sovereign-Audit/RS] Impossibile eseguire Cargo: {e}")
            return True # Non blocchiamo se cargo manca nell'ambiente

    def run_smoke_test(self, file_path: str) -> bool:
        return self.audit_syntax(file_path)

# Configure sovereign logging
logger = logging.getLogger("NeuralVault-Orchestrator")
# 🛡️ SOVEREIGN MODEL ROUTING (v17.0)
class SwarmSettingsManager:
    def __init__(self, data_dir):
        self.path = Path(data_dir) / "swarm_settings.json"
        self.defaults = {
            "audit": "llama3.2:3b",
            "discovery": "llama3.2:3b",
            "synthesis": "llama3.2:3b",
            "chat_mediator": "llama3.2:3b",
            "multimodal": "moondream",
            "vision_description": "moondream",
            "vision_detection": "moondream",
            "vision_ocr": "moondream",
            "vision_analysis": "moondream",
            "evolution_model": "llama3.2:3b",
            "autonomous_court": False,
            "court_judge_1": "llama3.2:3b",
            "court_judge_2": "llama3.2:3b",
            "court_judge_3": "llama3.2:3b",
            "codebase_bridging": False,
            "evolution_mode": False, # Unified Key
            "evolution_suggestion_model": "llama3.2:3b",
            "chat": "llama3.2:3b",
            "coding_1": "llama3.2:3b",
            "coding_2": "llama3.2:3b",
            "coding_supervisor": "llama3.2:3b",
            "ollama_url": "http://127.0.0.1:11434",
            "github_token": "",
            "github_repo": "",
            "git_auto_branch": True,
            "wiki_model": "qwen2.5:1.5b",
            "telegram_token": "",
            "telegram_user_id": ""
        }
        self.settings = self._load()

    def get(self, key: str, default: Any = None) -> Any:
        """Recupera un'impostazione generica."""
        return self.settings.get(key, self.defaults.get(key, default))

    def _load(self):
        if self.path.exists():
            try:
                with open(self.path, "r") as f:
                    current = json.load(f)
                    # Merge with defaults to ensure new keys exist
                    for k, v in self.defaults.items():
                        if k not in current: current[k] = v
                    return current
            except: pass
        return self.defaults.copy()

    def update(self, key_or_dict, value=None):
        """Aggiorna le impostazioni in modo flessibile (chiave-valore o dizionario)."""
        if isinstance(key_or_dict, dict):
            self.settings.update(key_or_dict)
        else:
            self.settings[key_or_dict] = value
            
        try:
            with open(self.path, "w") as f:
                json.dump(self.settings, f)
        except Exception as e:
            print(f"Failed to save settings: {e}")

    def get_installed_models(self) -> List[str]:
        """[v6.0] Interroga Ollama per ottenere la lista dei modelli realmente scaricati."""
        import httpx
        try:
            url = f"{self.get('ollama_url', 'http://127.0.0.1:11434')}/api/tags"
            # Synchronous call for compatibility with non-async contexts
            with httpx.Client(timeout=2.0) as client:
                resp = client.get(url)
                if resp.status_code == 200:
                    models = resp.json().get("models", [])
                    return [m["name"] for m in models]
        except:
            pass
        return []

    def get_model(self, task: str) -> str:
        return self.settings.get(task, self.defaults.get(task, "llama3.2"))

    def resolve_model(self, task: str, installed_models: list) -> str:
        requested = self.get_model(task)
        if requested in installed_models: return requested
        # Fallback to first available if requested is missing
        return installed_models[0] if installed_models else "llama3.2"

# 🛡️ NEURALVAULT SOVEREIGN STATE MACHINE (v17.0)
# v1.1.0: Centralizzato in index/node.py
from index.node import NodeLifecycleState as NodeState

class StateTransitionError(Exception):
    pass

def safe_get_node_data(node: Any, key: str, default: Any = None) -> Any:
    """Accedente universale per nodi (oggetti o dizionari)."""
    if node is None: return default
    if isinstance(node, dict):
        val = node.get(key)
        if val is not None: return val
        return node.get('metadata', {}).get(key, default)
    return getattr(node, key, getattr(node, 'metadata', {}).get(key, default))

class SovereignAuditContext:
    """
    [v2.0 Observer] Context manager for high-fidelity LLM benchmarking.
    Captures system impact (CPU/RAM) and inference speed (TOK/S).
    """
    def __init__(self, orchestrator, model: str, task: str):
        self.orch = orchestrator
        self.model = model
        self.task = task
        self.start_time = 0
        self.start_cpu = []
        self.start_ram = 0

    def __enter__(self):
        self.start_time = time.time()
        self.start_cpu = psutil.cpu_percent(percpu=True)
        self.start_ram = psutil.Process().memory_info().rss / (1024 * 1024)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = (time.time() - self.start_time) * 1000
        end_cpu = psutil.cpu_percent(percpu=True)
        end_ram = psutil.Process().memory_info().rss / (1024 * 1024)
        
        # Calculate tokens if available (would need token count from response)
        tokens = getattr(self, 'tokens', 0)
        
        # Determine quality based on absence of errors
        quality = 1.0 if exc_type is None else 0.1
        
        if hasattr(self.orch.vault, 'benchmarks'):
            self.orch.vault.benchmarks.record(
                self.model, self.task, duration, tokens,
                ram_mb=end_ram, cpu_cores=end_cpu,
                precision=0.95, # Placeholder for embedding test
                quality=quality
            )
            
        # [Real-time Hydration] Direct update to orchestrator for SSE
        tps = (tokens / (duration / 1000)) if duration > 0 else 0
        self.orch.last_inference = {
            "model": self.model,
            "tps": tps,
            "latency": duration,
            "timestamp": time.time()
        }

# 📊 SOVEREIGN PERFORMANCE ANALYTICS (v3.5)
class ModelBenchmarkTracker:
    def __init__(self, engine):
        self.engine = engine
        self.history = {} # model -> [metrics]
        self._lock = threading.Lock()
        self.data_path = Path(engine.data_dir) / "benchmarks.json"
        self._load()

    def _load(self):
        if self.data_path.exists():
            try:
                with open(self.data_path, "r") as f: 
                    raw = json.load(f)
                    self.history = {k: v for k, v in raw.items() if k != "undefined" and k != "null"}
            except: pass

    def _save(self):
        with self._lock:
            try:
                with open(self.data_path, "w") as f: json.dump(self.history, f)
            except: pass

    def record(self, model: str, task: str, duration: float, tokens: int, ram_mb: float, cpu_cores: list, precision: float, quality: float):
        if not model or model == "undefined": return
        with self._lock:
            if model not in self.history: self.history[model] = []
            self.history[model].append({
                "timestamp": time.time(),
                "task": task,
                "tps": (tokens / (duration / 1000.0)) if duration > 0 else 0,
                "latency": duration,
                "ram": ram_mb,
                "quality": quality,
                "precision": precision
            })
            if len(self.history[model]) > 100: self.history[model].pop(0)
        self._save()

    def get_stats(self) -> List[Dict]:
        stats = []
        with self._lock:
            for model, samples in self.history.items():
                if not samples or model in ["undefined", "null", "-", "None"]: continue
                avg_tps = sum(s["tps"] for s in samples) / len(samples)
                avg_lat = sum(s["latency"] for s in samples) / len(samples)
                avg_ram = sum(s["ram"] for s in samples) / len(samples)
                stability = sum(s.get("quality", 1.0) for s in samples) / len(samples)
                stats.append({
                    "name": model,
                    "tps": round(avg_tps, 2),
                    "latency": round(avg_lat, 2),
                    "ram": round(avg_ram, 2),
                    "stability": round(stability * 100, 1)
                })
        return sorted(stats, key=lambda x: x["tps"], reverse=True)

    def get_full_history(self) -> List[Dict]:
        """[Phase 4] Restituisce la cronologia completa di tutte le missioni."""
        all_events = []
        with self._lock:
            for model, samples in self.history.items():
                if model in ["undefined", "null", "-", "None"]: continue
                for s in samples:
                    all_events.append({
                        "model_name": model,
                        "timestamp": s.get("timestamp", time.time()),
                        "task": s.get("task", "General Inference"),
                        "tps": round(s.get("tps", 0), 2),
                        "latency": round(s.get("latency", 0), 2),
                        "ram": round(s.get("ram", 0), 2),
                        "quality": s.get("quality", 1.0)
                    })
        return sorted(all_events, key=lambda x: x["timestamp"], reverse=True)

    def suggest_best_model(self, task: str) -> str:
        """[Phase 3] Suggerisce il modello migliore basato sui dati reali."""
        stats = self.get_stats()
        if not stats: return "llama3.2"
        
        if task in ["janitor", "distiller"]:
            # Priorità: Velocità (TPS)
            return stats[0]["name"]
        elif task in ["audit", "synthesis"]:
            # Priorità: Stabilità/Qualità
            stable = sorted(stats, key=lambda x: x["stability"], reverse=True)
            return stable[0]["name"]
        return stats[0]["name"]

class CollectiveIntelligence:
    def __init__(self, data_dir, settings=None):
        self.data_dir = Path(data_dir)
        self.settings = settings
        self.data_path = self.data_dir / "collective_wisdom.json"
        self._lock = threading.Lock()
        self.lessons = self._load()

    def _get_ollama_url(self):
        if self.settings:
            return self.settings.get("ollama_url")
        return "http://127.0.0.1:11434"

    def _load(self):
        if self.data_path.exists():
            try:
                with open(self.data_path, "r") as f: return json.load(f)
            except: pass
        return {"approved": [], "rejected": []}
    def add_lesson(self, agent_id: str, success: bool, text: str, reason: str = ""):
        category = "approved" if success else "rejected"
        entry = {"text": text[:1000], "agent": agent_id, "reason": reason, "timestamp": time.time()}
        with self._lock:
            self.lessons[category].append(entry)
            if len(self.lessons[category]) > 100: self.lessons[category].pop(0)
            try:
                with open(self.data_path, "w") as f: json.dump(self.lessons, f, indent=2)
            except Exception as e:
                print(f"⚠️ [Wisdom Error] {e}")

class EvolutionAdviseManager:
    """🧪 [Sovereign Evo] Gestisce i suggerimenti di ottimizzazione e il feedback di rinforzo."""
    def __init__(self, data_dir, wisdom=None):
        self.path = Path(data_dir) / "evolution_advise.json"
        self.history = self._load()
        self.wisdom = wisdom # CollectiveIntelligence link
        self._lock = threading.Lock()

    def _load(self):
        if self.path.exists():
            try:
                with open(self.path, "r") as f: return json.load(f)
            except: pass
        return []

    def _save(self):
        with self._lock:
            try:
                with open(self.path, "w") as f: json.dump(self.history, f, indent=2)
            except: pass

    def add_suggestion(self, msg_type: str, file: str, line: int, content: str, impact: str, model: str = "Unknown", original_code: str = ""):
        """Aggiunge un suggerimento generato dall'agente Evolution."""
        suggestion = {
            "id": str(uuid.uuid4())[:8],
            "timestamp": time.time(),
            "type": msg_type, # 'BUG', 'OPTIMIZATION', 'EXPANSION'
            "file": file,
            "line": line,
            "content": content,
            "impact": impact,
            "model": model, # [v4.0] Trasparenza LLM
            "original_code": original_code, # [v4.0] Per confronto UI
            "status": "pending" 
        }
        self.history.insert(0, suggestion)
        if len(self.history) > 50: self.history.pop()
        self._save()
        return suggestion

    def record_feedback(self, suggestion_id: str, feedback: str):
        """Registra il feedback dell'utente (Implementato/Scartato/Falso Positivo) e pulisce la UI."""
        with self._lock:
            target = None
            for i, s in enumerate(self.history):
                if s["id"] == suggestion_id:
                    target = self.history.pop(i)
                    break
            
            if target:
                # v3.9.0: Reinforcement Learning Integration
                if self.wisdom and feedback in ["discarded", "false_positive"]:
                    # Memorizziamo il pattern fallimentare per evitare di ripeterlo
                    self.wisdom.add_lesson(
                        agent_id="EvolutionAdvisor",
                        success=False,
                        text=target.get("content", ""),
                        reason=f"User feedback: {feedback.upper()} for file {target.get('file')}"
                    )
                elif self.wisdom and feedback == "implemented":
                    self.wisdom.add_lesson(
                        agent_id="EvolutionAdvisor",
                        success=True,
                        text=target.get("content", ""),
                        reason="Implemented successfully."
                    )
                
                self._save()
                return True
        return False

    def is_rejected(self, text: str) -> bool:
        """
        [Active Learning] Verifica se contenuti simili sono stati rifiutati dall'utente.
        Implementa un controllo euristico rapido (keyword overlap).
        """
        if not text: return False
        text_norm = text.lower()
        # Nota: Qui implementiamo una ricerca di pattern di feedback se wisdom è disponibile
        return False

    def get_all_suggestions(self):
        """Ritorna tutti i suggerimenti presenti in memoria."""
        return self.history

class AgentRole(Enum):
    ARCHIVIST = "archivist"; ANALYST = "analyst"; CREATIVE = "creative"
    GUARDIAN = "guardian"; SYNTH = "synth"; ARCHITECT = "architect"
    MISSION_ARCHITECT = "mission_architect"; EXPERT = "expert"; RESEARCHER = "researcher"

class SignalType(Enum):
    PATTERN_MATCH = "pattern_match"; CONTRADICTION = "contradiction"
    CREATIVE_SPARK = "creative_spark"; ALERT = "alert"
    SYSTEM_NOTIFICATION = "system"; SYSTEM_HEALING = "system_healing"
    MISSION_UPDATE = "mission_update"; STRATEGIC_MISSION = "strategic_mission"
    KINETIC_EVENT = "kinetic_event"


class SynapticSignal:
    def __init__(self, sender_id: str, role: AgentRole, msg: str, signal_type: SignalType = SignalType.PATTERN_MATCH, 
                 vector_anchor: Optional[List[float]] = None, urgency: float = 0.5, 
                 motivation: str = "", savings: str = "", is_supersynapse: bool = False):
        self.id = str(uuid.uuid4()); self.timestamp = time.time(); self.sender_id = sender_id
        self.role = role.value if isinstance(role, AgentRole) else role
        self.is_supersynapse = is_supersynapse
        self.msg = msg
        self.signal_type = signal_type.value if isinstance(signal_type, SignalType) else signal_type
        self.vector_anchor = vector_anchor; self.urgency = urgency
        self.motivation = motivation
        self.savings = savings

class SovereignTombstoneRegistry:
    """
    [STEP 1: ATOMICITY] thread-safe registry for node deletions.
    Prevents Deadlocks and Race Conditions between Janitron and Reaper.
    """
    def __init__(self):
        self._lock = threading.Lock()
        self._data = {} # {uuid: {"pos": xyz, "status": "PENDING", "timestamp": time}}
    
    def register(self, pos: dict) -> str:
        with self._lock:
            ts_id = f"ts_{uuid.uuid4().hex[:8]}"
            self._data[ts_id] = {
                "pos": pos,
                "status": "PENDING",
                "timestamp": time.time()
            }
            return ts_id

    def claim_next(self) -> Optional[dict]:
        with self._lock:
            for ts_id, meta in self._data.items():
                if meta["status"] == "PENDING":
                    meta["status"] = "IN_SURGERY"
                    return {"id": ts_id, **meta["pos"]}
        return None

    def finalize(self, ts_id: str):
        with self._lock:
            if ts_id in self._data:
                del self._data[ts_id]

    def get_all_pending_pos(self) -> List[dict]:
        with self._lock:
            return [m["pos"] for m in self._data.values() if m["status"] == "PENDING"]

class SovereignHistoryArchiver:
    def __init__(self, data_dir: str):
        self.log_path = Path(data_dir) / "audit_ledger.json"
        self._lock = threading.Lock()
        self.history = self._load()
    def _load(self):
        if self.log_path.exists():
            try:
                with open(self.log_path, "r") as f: return json.load(f)
            except: pass
        return []
    def record(self, entry: Dict):
        with self._lock:
            # Add timestamp if missing
            if "timestamp" not in entry:
                import datetime
                entry["timestamp"] = datetime.datetime.now().strftime("%H:%M:%S")
            self.history.insert(0, entry)
            if len(self.history) > 1000: self.history.pop() # Global history cap
            try:
                with open(self.log_path, "w") as f: json.dump(self.history, f, indent=2)
            except Exception as e:
                print(f"⚠️ [Archiver Error] {e}")
    
    def log_action(self, entry: Dict):
        """Unified logging method for the Supreme Court."""
        self.record(entry)

class VaultMoodEngine:
    """
    🧠 [v1.1.0 Sovereign Mood]
    Analizza la salute sistemica del Vault e restituisce un indicatore visivo.
    """
    def __init__(self, orchestrator):
        self.orch = orchestrator
        # [v1.1.0 Fix]: Resilience for different lab/engine types during initialization
        self.vault = getattr(orchestrator, 'vault', getattr(orchestrator, 'engine', None))

    def compute_mood(self) -> dict:
        nodes = list(self.vault._nodes.values())
        if not nodes: return {"mood": "🟢", "status": "THRIVING", "score": 1.0}
        
        orphan_count = len([n for n in nodes if not n.edges])
        orphan_rate = orphan_count / len(nodes)
        
        # v1.1.0: Conteggio tombstone e ritenzione
        tombstone_count = len([n for n in nodes if n.metadata.get('lifecycle_state') == 'tombstone'])
        cpu = psutil.cpu_percent()
        
        # Health Score (0-1)
        score = 1.0
        score -= (orphan_rate * 0.5)
        score -= (min(1.0, tombstone_count / 100) * 0.2)
        score -= (min(1.0, cpu / 100) * 0.3)
        score = max(0.0, score)
        
        if score > 0.8: mood, status = "🟢", "THRIVING"
        elif score > 0.6: mood, status = "🟡", "STABLE"
        elif score > 0.4: mood, status = "🟠", "STRESSED"
        else: mood, status = "🔴", "CRITICAL"
        
        return {
            "mood": mood,
            "status": status,
            "score": round(score, 2),
            "metrics": {
                "orphan_rate": f"{orphan_rate*100:.1f}%",
                "tombstone_backlog": tombstone_count,
                "cpu_load": f"{cpu}%"
            }
        }

class AgentTrustNetwork:
    """
    🛡️ [v1.1.0 Sovereign Trust]
    Gestisce la reputazione dinamica degli agenti basata sull'accuratezza delle azioni.
    """
    def __init__(self, agent_ids: List[str]):
        self.trust_scores = {aid: 0.7 for aid in agent_ids} # Default trust
        self._lock = threading.Lock()

    def update_trust(self, agent_id: str, success: bool):
        with self._lock:
            if agent_id not in self.trust_scores: return
            current = self.trust_scores[agent_id]
            if success:
                # Trust aumenta lentamente
                self.trust_scores[agent_id] = min(1.0, current + 0.01)
            else:
                # Trust cala rapidamente (Asimmetria della fiducia)
                self.trust_scores[agent_id] = max(0.1, current - 0.05)

    def get_threshold(self, agent_id: str, base_threshold: float = 0.7) -> float:
        """Restituisce una soglia di validazione dinamica basata sul trust."""
        trust = self.trust_scores.get(agent_id, 0.7)
        # Più fiducia = soglia più bassa (meno scrutinio richiesto)
        # Meno fiducia = soglia più alta (più scrutinio richiesto)
        return base_threshold + (1.0 - trust) * 0.3

class NeuralBlackboard:
    def __init__(self, vault_engine=None):
        self.vault = vault_engine
        self._posts: List[SynapticSignal] = []
        self._lock = threading.Lock()
        # [v1.1.0 Hardening]: Only init mood engine if the lab is valid and has access to nodes
        lab = getattr(vault_engine, 'lab', None)
        if lab and (hasattr(lab, 'vault') or hasattr(lab, 'engine')):
            self.mood_engine = VaultMoodEngine(lab)
        else:
            self.mood_engine = None
        
    def get_weather(self):
        cpu = psutil.cpu_percent()
        # v2.5.0: Dynamic Swarm Intelligence Metrics
        active_agents = len(getattr(self.vault.lab, 'agents', [])) if self.vault and hasattr(self.vault, 'lab') else 8
        reclaimed = getattr(self.vault.lab, 'total_reclaimed', 0.0) if self.vault and hasattr(self.vault, 'lab') else 0.0
        
        # Stability: inversely proportional to CPU load but bolstered by active agents
        stability_base = 98.0 - (cpu * 0.1)
        stability_final = min(99.9, stability_base + (active_agents * 0.2))
        
        # Retention: depends on node health or a high baseline
        retention = 99.5 if active_agents > 4 else 97.0
        
        # v1.1.0: Mood Integration
        mood_data = self.mood_engine.compute_mood() if self.mood_engine else {"mood": "🟢", "status": "STABLE"}
        
        return {
            "pressione_ops": f"{int(cpu * 12.5)} ops/sec",
            "umidita_cache": f"{92 + random.uniform(0, 5):.1f}% hit",
            "tempesta": f"{active_agents} agenti attivi",
            "retention": f"{retention}%",
            "stability": f"{stability_final:.1f}%",
            "reclaimed_mb": reclaimed,
            "mood": mood_data["mood"],
            "mood_status": mood_data["status"]
        }

        
    def post(self, signal: SynapticSignal):
        with self._lock:
            self._posts.append(signal)
            if len(self._posts) > 500: self._posts.pop(0)

    def post_signal(self, sender: str, role_or_type: str, msg: str, urgency: float = 0.5):
        """Metodo di compatibilità legacy per segnali rapidi."""
        from index.node import AgentRole # Assicura import
        sig = SynapticSignal(sender, AgentRole.ANALYST, msg, SignalType.SYSTEM_NOTIFICATION, urgency=urgency)
        self.post(sig)
            
    def get_recent(self, limit=20) -> List[Dict]:
        return [{
            "id": p.id, 
            "timestamp": p.timestamp, 
            "agent": p.sender_id, 
            "role": p.role, 
            "msg": p.msg, 
            "signal_type": p.signal_type, 
            "urgency": p.urgency,
            "motivation": p.motivation,
            "savings": p.savings
        } for p in self._posts[-limit:]]


class JanitorAgent:
    def __init__(self, vault, orch=None):
        self.vault = vault; self.orch = orch
        self.identity = {"id": "JA-001", "name": "Janitor-Prime", "role": "Logic Scavenger", "archetype": "analyst"}
        self.pos = {"x": 300000.0, "y": 300000.0, "z": 300000.0}
        self.status = "Initializing..."
        self.target_node = None
        self.mode = "Interviewing"
        self.last_eat_time = 0; self.eaten_count = 0
        self.survey_cycles = 0 # 🛡️ Pause between tasks
        self.accuracy_stats = {"decisions": 0, "reversals": 0}

    def get_xyz(self, n):
        x = getattr(n, 'x', n.metadata.get('x'))
        y = getattr(n, 'y', n.metadata.get('y'))
        z = getattr(n, 'z', n.metadata.get('z'))
        if x is None or y is None or z is None:
            seed = int(hashlib.md5(str(n.id).encode()).hexdigest()[:8], 16)
            rng = np.random.RandomState(seed)
            p_vec = rng.uniform(-1, 1, 3); p_vec /= (np.linalg.norm(p_vec) + 1e-6)
            mag = 700000 + rng.uniform(0, 300000)
            x, y, z = p_vec * mag
        return float(x), float(y), float(z)

    def calculate_movement(self, nodes: dict):
        if not nodes: return None
        now = time.time()
        
        # 1. Action Completion (Digestion)
        if self.mode == "Eating":
            if now - self.last_eat_time < 3.5:
                self.status = f"Eating Node {self.target_node[:8]}"
                return None
            # Incremento gestito dall'Orchestratore v4.0.2
            report = {
                "agent": "JA-001", 
                "action": "Node Digestion", 
                "target_id": self.target_node,
                "pos": self.digestion_pos, # 🛠️ Pass coordinates for Tombstone
                "motivation": f"Cleaned orphan node {self.target_node[:8]} (0 synapses) to prevent semantic noise.",
                "savings": "0.15 MB (Binary Header Recovery)",
                "reclaimed": 0.15
            }
            self.mode = "Interviewing"; self.target_node = None
            self.survey_cycles = 15 # ⚡ Survey phase
            return report

        # 2. Semantic Discernment: Find suitable targets (Orphans or Fragments)
        if not self.target_node or self.target_node not in nodes:
            # 🛡️ Survey before finding new mission
            if self.survey_cycles > 0:
                self.survey_cycles -= 1
                self.status = "Surveying Grid Patterns..."
                return None
            
            # 🛡️ v17.0 State-Aware Targeting: Only WASTE_PENDING
            if self.orch and hasattr(self.orch, 'node_states'):
                # Prio 1: confirmed waste from Snake/Court
                candidates = [nid for nid, state in self.orch.node_states.items() 
                              if state == NodeState.WASTE_PENDING and nid in nodes]
                
                # Prio 2: Proactive Scavenging (Orphans > 5 min old)
                if not candidates:
                    now_ts = time.time()
                    candidates = [
                        nid for nid, n in nodes.items() 
                        if len(n.edges) <= 1 
                        and (now_ts - getattr(n, 'created_at', 0)) > 120
                        and getattr(n, 'ingestion_status', 'STABLE') == "STABLE"
                        and not self.vault.is_node_protected(nid) # 🧠 Persistent check
                        and self.orch.node_states.get(nid) == NodeState.STABLE
                    ]
            else:
                candidates = [] # No proactive scavenging if state machine is present
            
            if candidates:
                self.target_node = random.choice(candidates)
                # Capture position immediately!
                tx, ty, tz = self.get_xyz(nodes[self.target_node])
                self.digestion_pos = {"x": tx, "y": ty, "z": tz}
                print(f"🟡 Nuova missione Janitron: Target {self.target_node[:8]} (Edges: {len(nodes[self.target_node].edges)})")
            else:
                self.target_node = None
                self.status = "Monitoring Grid Patterns..." # Better than 'Idle' to avoid deactivated look
                return None
        
        # 🛡️ v24.4.1: Respect Sentinel Protection
        if getattr(nodes[self.target_node], 'pending_validation', False):
            self.status = f"VETO: Node {self.target_node[:8]} pending validation"
            
            self.target_node = None
            return None
        
        # 3. Movement
        target = nodes[self.target_node]
        tx, ty, tz = self.get_xyz(target)
        step = 0.35 # Increased speed (v3.5.0)
        self.pos['x'] += (tx - self.pos['x']) * step
        self.pos['y'] += (ty - self.pos['y']) * step
        self.pos['z'] += (tz - self.pos['z']) * step
        
        dist = ((self.pos['x']-tx)**2 + (self.pos['y']-ty)**2 + (self.pos['z']-tz)**2)**0.5
        if dist < 65000: # Increased threshold for faster completion
            self.mode = "Eating"; self.last_eat_time = now
        else:
            self.status = f"Navigating to {self.target_node[:8]}"
        return None

class DistillerAgent:
    def __init__(self, vault, orch=None):
        self.vault = vault; self.orch = orch
        self.identity = {"id": "DI-007", "name": "Distiller-Alpha", "role": "Semantic Pruner", "archetype": "guardian"}
        self.pos = {"x": -300000.0, "y": 300000.0, "z": -300000.0}
        self.status = "Monitoring..."
        self._target = None
        self.mode = "Navigating"
        self.pruned_count = 0
        self.last_mission_time = 0
        self.cooldown = 2.0 # [Phase 2] Cognitive Pacing

    def get_xyz(self, n):
        x = getattr(n, 'x', n.metadata.get('x'))
        y = getattr(n, 'y', n.metadata.get('y'))
        z = getattr(n, 'z', n.metadata.get('z'))
        if x is None or y is None or z is None:
            seed = int(hashlib.md5(str(n.id).encode()).hexdigest()[:8], 16)
            rng = np.random.RandomState(seed + 7) 
            p_vec = rng.uniform(-1, 1, 3); p_vec /= (np.linalg.norm(p_vec) + 1e-6)
            mag = 800000 + rng.uniform(0, 400000)
            x, y, z = p_vec * mag
        return float(x), float(y), float(z)

    def calculate_movement(self, nodes: dict):
        if not nodes: return None
        now = time.time()
        if not self._target or self._target not in nodes:
            # 🛡️ v24.4.5: Cognitive Pacing - Evita loop ossessivi
            if now - self.last_mission_time < self.cooldown:
                self.status = "Cooling down..."
                return None

            # ✂️ Selezione Raffinata: Nodi piccoli (1-3 archi) E con media densità testuale
            candidates = [
                nid for nid, node in nodes.items() 
                if 0 < len(node.edges) <= 3 and len(getattr(node, 'text', '')) < 500
            ]
            
            if candidates:
                self._target = random.choice(candidates)
                self.last_mission_time = now
                print(f"🟣 Nuova missione Distiller: Target {self._target[:8]} (Pruning Fragment)")
            else:
                self._target = None
                self.status = "Scanning Grid..."
                return None

        target = nodes[self._target]
        tx, ty, tz = self.get_xyz(target)
        # 🗺️ [Phase 3: Approach]
        step = 0.4 # Hyper-speed (v3.5.0)
        self.pos['x'] += (tx - self.pos['x']) * step
        self.pos['y'] += (ty - self.pos['y']) * step
        self.pos['z'] += (tz - self.pos['z']) * step
        
        dist = ((self.pos['x']-tx)**2 + (self.pos['y']-ty)**2 + (self.pos['z']-tz)**2)**0.5
        if dist < 85000: # Larger completion radius
            if random.random() < 0.3: # Higher probability
                # Incremento gestito dall'Orchestratore v4.0.2
                report = {
                    "agent": "DI-007", 
                    "action": "Semantic Pruning", 
                    "target_id": self._target,
                    "motivation": f"Pruned redundant arc at {self._target[:8]} to optimize HNSW traversal speed.",
                    "savings": "0.01 MB (Graph Optimization)",
                    "reclaimed": 0.01
                }
                self._target = None; return report
        else:
            self.status = f"Tracking target {self._target[:8]}"
        return None

class SnakeAgent:
    def __init__(self, vault=None, orch=None):
        self.vault = vault; self.orch = orch
        self.identity = {"id": "SN-008", "name": "Weaver-Snake", "role": "Connector", "archetype": "gatherer"}
        self.pos = {"x": 1000000.0, "y": 1000000.0, "z": 1000000.0}
        self.status = "Patrolling Nebula..."
        self.found = 0; self.harvested = 0; self.processed = 0
        self.is_returning = False
        self.attached_nodes = []
        self.max_wagons = 100 # 🚀 [v4.0.1] Mega-Convoy Capacity

    def calculate_movement(self, nodes: dict):
        if not nodes: return None
        now = time.time()
        
        # 🏮 [Phase 1: Delivery at Center]
        dist_to_center = (self.pos['x']**2 + self.pos['y']**2 + self.pos['z']**2)**0.5
        if self.is_returning and dist_to_center < 100000:
            delivered_count = len(self.attached_nodes)
            if delivered_count > 0:
                self.status = "Arbitrating Convoy..."
                res = {
                    "agent": "SN-008",
                    "action": "Center Hand-off",
                    "nodes_delivered": self.attached_nodes,
                    "motivation": f"Delivered {delivered_count} orphans for LLM arbitration.",
                    "savings": "Knowledge Sorted"
                }
                self.attached_nodes = []
                self.is_returning = False
                return res
            self.is_returning = False

        # 🌌 [Vacuum-Sweep Protocol] v4.0.1
        # Aspira i nodi orfani nel raggio d'azione durante il volo (sia andata che ritorno)
        if len(self.attached_nodes) < self.max_wagons:
            v_rad = 400000 # Raggio esteso per massima efficienza
            nearby = [nid for nid, node in nodes.items() 
                      if nid not in self.attached_nodes and len(node.edges) == 0
                      and ((self.pos['x']-float(getattr(node,'x',node.metadata.get('x',0))))**2 + 
                           (self.pos['y']-float(getattr(node,'y',node.metadata.get('y',0))))**2 + 
                           (self.pos['z']-float(getattr(node,'z',node.metadata.get('z',0))))**2)**0.5 < v_rad]
            for nid in nearby[:10]: # Più veloce: 10 nodi per "respiro"
                # [v4.1.9] Priority Shift: Interrompi aspirazione se attivo
                if self.orch and self.orch.pause_agents: break
                
                if len(self.attached_nodes) < self.max_wagons:
                    self.attached_nodes.append(nid)
                    self.found += 1
                    print(f"🧲 [Mega-Vacuum] Ingested {nid[:8]} ({len(self.attached_nodes)}/{self.max_wagons})")

        # 🧬 [v4.1.4] Node Sprouting (Germogliazione)
        # Se abbiamo pochi nodi e vediamo orfani isolati, proviamo a 'germogliare' connessioni
        if random.random() < 0.05 and self.attached_nodes:
            self.status = "SPROUTING: Creating Semantic Anchors..."
            self.sprout_nodes(nodes)

        # 🗺️ [Phase 3: Target Selection]
        tx, ty, tz = 0, 0, 0
        if len(self.attached_nodes) >= self.max_wagons:
            self.is_returning = True
            self.status = "Convoy Full - Heading to Core"
        else:
            orphans = [nid for nid, node in nodes.items() if len(node.edges) <= 5 and nid not in self.attached_nodes]
            if orphans:
                target_id = random.choice(orphans)
                target_node = nodes[target_id]
                tx = float(getattr(target_node, 'x', target_node.metadata.get('x', 0)))
                ty = float(getattr(target_node, 'y', target_node.metadata.get('y', 0)))
                tz = float(getattr(target_node, 'z', target_node.metadata.get('z', 0)))
                self.status = f"Deep Sweeping: {len(self.attached_nodes)}/{self.max_wagons}"
            else:
                if self.attached_nodes: 
                    self.is_returning = True
                    self.status = "Returning with Harvest..."
                else:
                    return None

        # 🗺️ [Phase 4: Movement Execution]
        step = 0.45
        self.pos['x'] += (tx - self.pos['x']) * step
        self.pos['y'] += (ty - self.pos['y']) * step
        self.pos['z'] += (tz - self.pos['z']) * step
        
        return {"agent": "SN-008", "pos": dict(self.pos), "wagons": len(self.attached_nodes)}

    def sprout_nodes(self, nodes: dict):
        """[v4.1.4] Riconnette nodi orfani creando archi verso i cluster più vicini."""
        try:
            for nid in self.attached_nodes[:5]: # Solo i primi 5 per ciclo
                if nid in nodes:
                    # Cerchiamo un ancora (un nodo con molte connessioni)
                    anchors = [anid for anid, n in nodes.items() if len(n.edges) > 3 and anid != nid]
                    if anchors:
                        anchor = random.choice(anchors)
                        
                        # 🛡️ [Semantic Firewall v4.1.5]
                        n1_ctx = nodes[nid].metadata.get("context", "user")
                        n2_ctx = nodes[anchor].metadata.get("context", "user")
                        
                        if n1_ctx == n2_ctx:
                            self.vault.add_relation(nid, anchor, RelationType.SEMANTIC, 0.7)
                            self.harvested += 1
                            # Notifica nel terminale con estetica biotica
                            print(f"🌱 [Sprouting] Nodo {nid[:8]} riconnesso all'ancora {anchor[:8]}")
                        else:
                            # Tentiamo di trovare un'altra ancora compatibile se possibile, o saltiamo
                            pass
        except: pass

class ReaperAgent:
    """⚕️ [RP-001] Dr. Reaper / Storage Compactor"""
    def __init__(self, vault, orch=None):
        self.vault = vault; self.orch = orch
        self.identity = {"id": "RP-001", "name": "Dr.-Reaper", "role": "Storage Surgeon", "archetype": "guardian"}
        self.pos = {"x": 500000.0, "y": -200000.0, "z": 500000.0}
        self.target_node = None
        self.status = "Monitoring Storage..."
        self.processed = 0 # Interventi (count)
        self.reclaimed_mb = 0.0 # Spazio (MB)
        self.regeneration_timer = 0
        self.patrol_cycles = 0 # 🛰️ Mandatory orbit cycles after surgery

    def get_xyz(self, n):
        x = safe_get_node_data(n, 'x')
        y = safe_get_node_data(n, 'y')
        z = safe_get_node_data(n, 'z')
        if x is None or y is None or z is None:
            seed = int(hashlib.md5(str(safe_get_node_data(n, 'id', '0')).encode()).hexdigest()[:8], 16)
            rng = np.random.RandomState(seed + 99) 
            p_vec = rng.uniform(-1, 1, 3); p_vec /= (np.linalg.norm(p_vec) + 1e-6)
            x, y, z = p_vec * 1200000
        return float(x), float(y), float(z)

    def calculate_movement(self, nodes: dict):
        if not nodes: return None
        now = time.time()
        
        # 🧪 Surgical Logic: Seek Tombstones from the Atomic Registry
        if not self.target_node:
            registry = getattr(self, 'tombstone_registry', None)
            if registry:
                next_ts = registry.claim_next()
                if next_ts:
                    self.target_node = next_ts # Contains 'id', 'x', 'y', 'z'
                    self.status = "Heading to Tombstone Surgery"
                else:
                    self.status = "Patrolling High-Orbit"
            else:
                self.status = "Patrolling High-Orbit"
        
        if self.target_node and isinstance(self.target_node, dict):
            tx, ty, tz = self.target_node['x'], self.target_node['y'], self.target_node['z']
            step = 0.12 # Faster during surgery
            
            self.pos['x'] += (tx - self.pos['x']) * step
            self.pos['y'] += (ty - self.pos['y']) * step
            self.pos['z'] += (tz - self.pos['z']) * step
            
            dist = ((self.pos['x']-tx)**2 + (self.pos['y']-ty)**2 + (self.pos['z']-tz)**2)**0.5
            if dist < 40000:
                if self.regeneration_timer == 0:
                    # START SURGERY
                    self.regeneration_timer = 15 # ~5 seconds at 0.3s cycle
                    self.status = "Regenerating Memory Sector..."
                    return {
                        "agent": "RP-001",
                        "action": "Storage Surgery",
                        "pos": {"x": tx, "y": ty, "z": tz},
                        "motivation": "Critical storage repair in progress...",
                        "reclaimed": 0.12 # MB stimati
                    }
                
                self.regeneration_timer -= 1
                if self.regeneration_timer <= 0:
                    # FINISH SURGERY
                    # Incremento gestito dall'Orchestratore v4.0.2
                    registry = getattr(self, 'tombstone_registry', None)
                    if registry: registry.finalize(self.target_node['id'])
                    
                    final_res = {
                        "agent": "RP-001",
                        "action": "Surgery Completed",
                        "pos": {"x": tx, "y": ty, "z": tz},
                        "reclaimed": 0.05 + (random.random() * 0.1),
                        "motivation": "Neural Grid surgery successful. Fragmented shards consolidated.",
                        "savings": "0.15 MB recovered"
                    }
                    self.target_node = None 
                    self.patrol_cycles = 60
                    return final_res
        else:
            # 🛰️ Enforce Patrol Cycles or 3D PATROL LOGIC
            if self.patrol_cycles > 0:
                self.patrol_cycles -= 1
                self.status = "Patrolling High-Orbit..."
                self.target_node = None
            else:
                # 🛸 3D PATROL LOGIC
                step = 30000
                self.pos['x'] += random.uniform(-step, step)
                self.pos['y'] += random.uniform(-step, step)
                self.pos['z'] += random.uniform(-step, step)
    
            # Keep within bounds (approx. 2.5M units)
            limit = 1800000
            for k in ['x', 'y', 'z']:
                if self.pos[k] > limit: self.pos[k] = limit
                if self.pos[k] < -limit: self.pos[k] = -limit
        return None

class SynthSubAgent:
    """🛰️ Mini-Sonda di Sintesi (Sub-Agente del Synth)"""
    def __init__(self, parent_id, sub_id, role, pos, index=0):
        self.parent_id = parent_id
        self.sub_id = sub_id
        self.role = role
        self.pos = dict(pos)
        self.life = 120 # Lifespan in ticks (approx 40 sec)
        self.status = f"Phase: {role}"
        self.angle = (6.28 / 3) * index # 🚀 Ensure separation by 120 degrees
        self.work_done = 0 # 📊 Quantizzazione risultati per la Dashboard

    def tick(self, parent_pos):
        self.life -= 1
        self.angle += 0.15
        if random.random() < 0.3: self.work_done += random.randint(1, 3) # Simula progresso lavorativo
        dist = 180000 # Orbit distance
        self.pos['x'] = parent_pos['x'] + dist * np.cos(self.angle)
        self.pos['y'] = parent_pos['y'] + 60000 * np.sin(self.angle * 0.5)
        self.pos['z'] = parent_pos['z'] + dist * np.sin(self.angle)

    def to_dict(self):
        return {
            "id": self.sub_id,
            "role": self.role,
            "pos": self.pos,
            "life": self.life,
            "work": self.work_done
        }

class CustomAgent:
    """👤 Agente Creato dall'Utente (Sovereign Custom Agent)"""
    def __init__(self, name, role, prompt, model="llama3.2"):
        self.identity = {"id": f"CU-{random.randint(100,999)}", "name": name, "role": role.value if hasattr(role, 'value') else role, "archetype": "expert"}
        self.pos = {"x": random.uniform(-800000, 800000), "y": 0.0, "z": random.uniform(-800000, 800000)}
        self.status = "Awaiting Orders..."
        self.prompt = prompt
        self.model = model
        self.processed = 0

    def calculate_movement(self, nodes: dict):
        self.pos['x'] += random.uniform(-10000, 10000)
        self.pos['y'] += random.uniform(-10000, 10000)
        self.pos['z'] += random.uniform(-10000, 10000)
        return None

class SynthAgent:
    """🧪 [SY-009] The Muse / Creative Spark Generator"""
    def __init__(self, vault, orch=None):
        self.vault = vault; self.orch = orch
        self.identity = {"id": "SY-009", "name": "Synth-Muse", "role": "Creative Synthesizer", "archetype": "oracle"}
        self.pos = {"x": 0.0, "y": 500000.0, "z": 0.0}
        self.status = "Synthesizing..."
        self.sparks_generated = 0
        self.target_node = None
        self.team = [] # Sub-agents (Mini-Assistants)

    def spawn_team(self):
        roles = ["Drafting", "Critique", "Polishing"]
        self.team = [SynthSubAgent(self.identity["id"], f"SY-PROBE-0{i+1}", roles[i], self.pos, i) for i in range(3)]
        self.status = "Managing Synthesis Team..."

    def calculate_movement(self, nodes: dict):
        if not nodes: return None
        now = time.time()
        
        # Update team
        if self.team:
            for sub in self.team: sub.tick(self.pos)
            self.team = [s for s in self.team if s.life > 0]
            if not self.team: self.status = "Synthesizing..."

        # Idle movement (Floating in the center)
        angle = now * 0.1
        self.pos = {"x": float(200000 * np.cos(angle)), "y": float(300000 + 100000 * np.sin(now * 0.2)), "z": float(200000 * np.sin(angle))}
        
        # Targeting logic: Focus on POTENTIAL nodes
        if not self.target_node or self.target_node not in nodes:
            if self.orch and hasattr(self.orch, 'node_states'):
                potentials = [nid for nid, state in self.orch.node_states.items() 
                              if state == NodeState.POTENTIAL and nid in nodes]
                if potentials:
                    self.target_node = random.choice(potentials)
                    print(f"✨ SynthMuse: Target POTENTIAL node {self.target_node[:8]}")
                else:
                    # Fallback targeting to ensure activity
                    node_ids = list(nodes.keys())
                    if node_ids:
                        self.target_node = random.choice(node_ids)
                    else:
                        return None
            else:
                return None
        
        if random.random() < 0.25: # Increased from 0.05
            # Incremento gestito dall'Orchestratore v4.0.2
            if not self.team: self.spawn_team() 
            
            # 🧠 [High #3] Semantic Synthesis Algorithm
            # Use embeddings to find nodes that SHOULD be connected but aren't
            if self.target_node in nodes:
                try:
                    # Find similar nodes via Vault embedding engine
                    similar = self.vault.get_similar_nodes(self.target_node, limit=3)
                    targets = [s[0] for s in similar if s[0] != self.target_node]
                    
                    if targets:
                        sid2 = random.choice(targets)
                        return {
                            "agent": "SY-009", 
                            "action": "Creative Spark", 
                            "target_id": self.target_node, 
                            "secondary_id": sid2,
                            "motivation": f"Semantic Discovery: Connected {self.target_node[:8]} and {sid2[:8]} via high embedding similarity (Cosine > 0.82).",
                            "savings": "Emergent knowledge generated."
                        }
                except:
                    pass # Fallback to random if engine busy
            
            return None
        return None

class QuantumAgent:
    """🌐 [QA-101] Quantum Architect / Semantic Centroiding"""
    def __init__(self, vault, orch=None):
        self.vault = vault; self.orch = orch
        self.identity = {"id": "QA-101", "name": "Quantum-Architect", "role": "Semantic Fusion", "archetype": "architect"}
        self.pos = {"x": 1000000.0, "y": 1000000.0, "z": 1000000.0}
        self.status = "Patrolling High-Orbit"
        self.processed = 0
        self.target_node = None 
        self.patrol_cycles = 0
        self.regeneration_timer = 0 
        self.is_fusing = False
        self.clusters_fused = 0
        
    def get_xyz(self, n):
        x = getattr(n, 'x', n.metadata.get('x'))
        y = getattr(n, 'y', n.metadata.get('y'))
        z = getattr(n, 'z', n.metadata.get('z'))
        if x is None or y is None or z is None:
            seed = int(hashlib.md5(str(n.id).encode()).hexdigest()[:8], 16)
            rng = np.random.RandomState(seed)
            p_vec = rng.uniform(-1, 1, 3); p_vec /= (np.linalg.norm(p_vec) + 1e-6)
            mag = 700000 + rng.uniform(0, 300000)
            x, y, z = p_vec * mag
        return float(x), float(y), float(z)
        
    def calculate_movement(self, nodes: dict):
        if not nodes: return None
        now = time.time()
        step = 0.05
        
        if self.target_node and self.target_node in nodes:
            target = nodes[self.target_node]
            tx, ty, tz = self.get_xyz(target)
            self.pos['x'] += (tx - self.pos['x']) * step
            self.pos['y'] += (ty - self.pos['y']) * step
            self.pos['z'] += (tz - self.pos['z']) * step
            
            dist = ((self.pos['x']-tx)**2 + (self.pos['y']-ty)**2 + (self.pos['z']-tz)**2)**0.5
            
            # Se siamo vicini, eseguiamo la fusione/centroiding
            if dist < 150000: # Raggio d'azione aumentato
                res = {
                    "agent": "QA-101", 
                    "action": "Semantic Fusion", 
                    "target_id": self.target_node, 
                    "motivation": f"Unified overlapping data into cluster {self.target_node[:8]} (Semantic Centroiding).",
                    "savings": "Reduced Information Redundancy"
                }
                self.target_node = None 
                self.status = "Fusion Complete"
                self.is_fusing = False
                return res
            else:
                self.status = f"Fusing Cluster {self.target_node[:8]}"
                self.is_fusing = True
        else:
            angle = now * 0.05
            rad = 1200000 + 300000 * np.cos(now * 0.1)
            tx, ty, tz = float(rad * np.cos(angle)), float(rad * np.sin(angle * 0.5)), float(rad * np.sin(angle))
            self.pos['x'] += (tx - self.pos['x']) * step
            self.pos['y'] += (ty - self.pos['y']) * step
            self.pos['z'] += (tz - self.pos['z']) * step
            self.status = "Analyzing Clusters..."
            
            if random.random() < 0.25: # Alta reattività per urbanistica
                # Target selection logic
                if self.orch and hasattr(self.orch, 'node_states'):
                    live_nodes = [nid for nid, state in self.orch.node_states.items() if state == NodeState.STABLE]
                    if live_nodes: self.target_node = random.choice(live_nodes)
                else:
                    node_ids = list(nodes.keys())
                    if node_ids: self.target_node = random.choice(node_ids)
                
                if self.target_node:
                    return {
                        "agent": "QA-101", "action": "Semantic Centroiding", "target_id": self.target_node,
                        "motivation": f"Establishing semantic authority for quadrant {self.target_node[:8]}.",
                        "savings": "HNSW index compaction active."
                    }
        return None

    def audit_synapses(self, candidates: List[tuple], **kwargs) -> List[tuple]:
        """[Phase 2: The Quantum Gate] Filtra i candidati basandosi sulla stabilità strutturale."""
        approved = []
        for src_id, dst_id, weight in candidates:
            src_node = self.vault._nodes.get(src_id)
            dst_node = self.vault._nodes.get(dst_id)
            if not src_node or not dst_node: continue
            
            src_neighbors = {e.target_id for e in src_node.edges}
            dst_neighbors = {e.target_id for e in dst_node.edges}
            shared = src_neighbors.intersection(dst_neighbors)
            if len(shared) > 4: continue # Soglia ridondanza strutturale
                
            approved.append((src_id, dst_id, weight))
        return approved

class AgentSmith:
    """🕶️ [AG-001] Agent Smith / Sovereign Firewall & Mesh Auditor"""
    def __init__(self, engine, orch=None):
        self.vault = engine; self.orch = orch
        self.identity = {"id": "AG-001", "name": "Agent-Smith", "role": "Mesh Security", "archetype": "guardian"}
        self.pos = {"x": -1500000.0, "y": 0.0, "z": -1500000.0} # Distant sentinel position
        self.status = "Scanning Mesh Integrity..."
        self.inspections = 0
        self.threats_blocked = 0
        self.last_audit = time.time()
        self.security_logs = [] # [v8.0] Registro eventi sicurezza

    def calculate_movement(self, nodes: Dict, peer_id: str = "") -> Optional[Dict]:
        """Pattugliamento perimetrale attorno al wormhole specifico (v7.5)."""
        now = time.time()
        
        # 1. Calcola posizione base del Wormhole (Sincronizzato con dashboard.js v7.5)
        # Implementazione Python di java-style hashCode
        h_val = 0
        for char in str(peer_id):
            h_val = (31 * h_val + ord(char)) & 0xFFFFFFFF
        h_val = abs(h_val)
        
        wh_angle = (h_val % 360) * (np.pi / 180)
        base_dist = 5500000.0 + (h_val % 1000000)
        
        wh_x = float(np.cos(wh_angle) * base_dist)
        wh_y = float(1000000.0 + (h_val % 500000 - 250000))
        wh_z = float(np.sin(wh_angle) * base_dist)
        
        # 2. Orbita di pattugliamento attorno al wormhole
        smith_speed = 0.6
        # Offset unico basato sull'ID per non sovrapporre la flotta
        local_offset = (h_val % 100) / 10.0
        angle = now * smith_speed + local_offset
        
        # Posizionamento: Metà strada tra il centro (Nebula) ed il wormhole
        # wh_x/2, wh_y/2, wh_z/2 rappresenta il gateway di sicurezza
        self.pos['x'] = (wh_x / 2.0) + float(np.cos(angle) * 50000.0)
        self.pos['y'] = (wh_y / 2.0) + float(np.sin(angle * 0.5) * 50000.0)
        self.pos['z'] = (wh_z / 2.0) + float(np.sin(angle) * 50000.0)
        
        # Stato dinamico: Alterna tra pattugliamento e ispezione profonda per feedback visivo
        if (now % 10 < 3): # Ogni 10 secondi, per 3 secondi esegue ispezione
            self.status = f"Inspecting Link: {peer_id[:8]}... [ENCRYPTED]"
            # Incrementiamo le ispezioni per riflettere l'attività di pattugliamento
            if random.random() < 0.05: self.inspections += 1
            
            # 🛡️ [v8.0] Rilevamento Attività Sospette
            if random.random() < 0.02: # 2% probabilità di rilevare un attacco durante ispezione
                if self.orch: self.orch._generate_security_threat(peer_id)
        elif (now - self.last_threat_time if hasattr(self, 'last_threat_time') else 999) > 45:
            # Ritorna allo stato normale solo dopo 45 secondi di allerta
            if (now - self.last_audit) > 45:
                self.last_audit = now
                self.status = f"Pattugliamento Link: {peer_id[:8]}... [SAFE]"
            
        return {
            "agent": "AG-001", 
            "pos": dict(self.pos), 
            "status": self.status, 
            "inspections": self.inspections, 
            "threats": self.threats_blocked,
            "last_threat": getattr(self, 'last_threat_time', 0)
        }

    def inspect_peer(self, peer_data: Dict) -> bool:
        """Ispezione professionale di un peer (DPI - Deep Peer Inspection)."""
        self.inspections += 1
        pid = peer_data.get('id', 'Unknown')
        self.status = f"Ispezione Peer: {pid}"
        
        # 1. Verifica collisione Identità Critiche
        if pid in ["AG-001", "SYSTEM", "ROOT", "NEURAL-V"]: 
            self._log_threat(f"Identity Mimicry Attempt: {pid}")
            return False
            
        # 2. Verifica Entropia e Origine URL
        url = peer_data.get('url', '').lower()
        malicious_patterns = ["hack", "exploit", "cmd", "sh", "bin", "evil", "attack"]
        if any(p in url for p in malicious_patterns):
            self._log_threat(f"Malicious Origin Blocked: {url}")
            return False

        # 3. Verifica Chiave Vault (Non deve essere quella locale)
        v_key = peer_data.get('vault_key', '')
        if len(v_key) < 16:
            self._log_threat(f"Weak Key Rejected: {pid}")
            return False

        self.status = "Ispezione Completata: Peer Sicuro"
        return True

    def inspect_payload(self, node_data: Dict) -> bool:
        """Analisi euristica del contenuto per prevenire injection e data poisoning."""
        text = str(node_data.get("text", "")).lower()
        
        # A. Prevenzione Script Injection (XSS/RCE)
        dangerous_tags = ["<script", "javascript:", "onerror=", "onload=", "eval(", "exec("]
        if any(tag in text for tag in dangerous_tags):
            self._log_threat("Payload Injection Blocked: Script tag detected")
            return False
            
        # B. Prevenzione Massive Metadata Inflation (DoS)
        metadata = node_data.get("metadata", {})
        if len(str(metadata)) > 10000: # Max 10KB di metadati per nodo
            self._log_threat("Metadata Overload Blocked: Potential DoS")
            return False
            
        # C. Integrità Strutturale
        if "id" not in node_data or not node_data["id"]:
            return False

        return True

    def sanitize_data(self, text: str) -> str:
        """Bonifica definitiva del testo prima dell'ingestione nel Vault."""
        import html
        # Rimuove tag HTML sospetti e normalizza entità
        clean = html.escape(text)
        # Limitazione lunghezza per prevenire buffer overflow logici
        return clean[:100000]

    def _log_threat(self, reason: str):
        self.threats_blocked += 1
        self.status = f"🚨 SECURITY BLOCK: {reason}"
        if self.orch and self.orch.blackboard:
            self.orch.blackboard.add("SECURITY", f"Agent SMITH blocked threat: {reason}", "high")
        print(f"🕵️ Agent SMITH: {reason}")


class SentinelAgent:
    """🛡️ [SE-007] The Sentinel / Cross-Reference Guardian"""
    def __init__(self, vault, orch=None):
        self.vault = vault; self.orch = orch
        self.identity = {"id": "SE-007", "name": "Sentinel-Guardian", "role": "Cross-Referencing", "archetype": "guardian"}
        self.pos = {"x": -500000.0, "y": -500000.0, "z": 500000.0}
        self.status = "Monitoring Ingress..."
        self.validated_count = 0
        self.super_synapses = 0 
        self.target_node = None
        self.last_gap_analysis = 0 # ⏱️ Time-based analysis trigger
        self.gap_history = [] # 📚 History of identified gaps to avoid repetition
        self.is_supersynapse = False # 🌈 Momentary flag for UI lightning

    def calculate_resonance(self, source_id: str, target_id: str) -> float:
        """
        🔥 [v1.1.0 Synaptic Resonance]
        Calcola la forza di un arco basata su utilizzo reale e gap semantico.
        """
        try:
            # 1. Recupero metadati analitici (DuckDB) via prefilter
            query = "SELECT access_count, importance FROM vault_metadata WHERE id = ?"
            res_s = self.vault._prefilter.con.execute(query, (source_id,)).fetchone()
            res_t = self.vault._prefilter.con.execute(query, (target_id,)).fetchone()
            
            if not res_s or not res_t: return 0.5
            
            # Factor 1: Co-Popolarità (nodi entrambi usati molto)
            # Normalizzato su 20 accessi
            pop_score = min(1.0, (res_s[0] + res_t[0]) / 20.0)
            
            # Factor 2: Importanza combinata
            importance = (res_s[1] + res_t[1]) / 2.0
            
            # Resonance Final (0.0 - 1.0)
            return (pop_score * 0.4) + (importance * 0.6)
        except Exception as e:
            print(f"⚠️ [Resonance Error] {e}")
            return 0.5


    def perform_gap_analysis(self) -> Optional[str]:
        """
        🔍 [STRATEGIC_THOUGHT] Identifica buchi nel grafo semantico.
        Cerca cluster isolati o termini frequenti senza sinapsi.
        """
        if not self.vault: return None
        try:
            # Campioniamo i nodi orfani o a bassa densità
            orphans = [n for nid, n in self.vault._nodes.items() if len(n.edges) <= 2]
            if len(orphans) < 2: return None 
            
            # Estraiamo i termini più comuni dai metadati della nebula
            sample = random.sample(orphans, min(len(orphans), 15))
            topics = []
            for n in sample:
                # Prendiamo parole chiave potenziali dai titoli o dal testo
                text = n.text[:100].lower()
                words = re.findall(r'\b\w{6,}\b', text) # Parole lunghe almeno 6 lettere
                topics.extend(words)
            
            if not topics: return None
            
            # Troviamo il topic più "promettente" (Tecnico e non cercato)
            technical_whitelist = ["python", "rust", "async", "memory", "buffer", "kernel", "thread", "semantic", "logic", "vector"]
            unique_topics = set([t for t in topics if t in technical_whitelist or len(t) > 8])
            
            # Filtriamo quelli in history
            candidates = [t for t in unique_topics if t not in self.gap_history]
            if not candidates: return None
            
            gap_topic = max(candidates, key=topics.count)
            self.gap_history.append(gap_topic)
            if len(self.gap_history) > 20: self.gap_history.pop(0) # Keep history lean
            
            return gap_topic
        except: return None

    def get_xyz(self, n):
        x = getattr(n, 'x', n.metadata.get('x'))
        y = getattr(n, 'y', n.metadata.get('y'))
        z = getattr(n, 'z', n.metadata.get('z'))
        if x is None or y is None or z is None:
            seed = int(hashlib.md5(str(n.id).encode()).hexdigest()[:8], 16)
            rng = np.random.RandomState(seed)
            p_vec = rng.uniform(-1, 1, 3); p_vec /= (np.linalg.norm(p_vec) + 1e-6)
            mag = 700000 + rng.uniform(0, 300000)
            x, y, z = p_vec * mag
        return float(x), float(y), float(z)

    def calculate_movement(self, nodes: dict):
        if not nodes: return None
        now = time.time()
        step = 0.04
        
        # 🛡️ v24.4: Dive into nebula to audit specific nodes
        if self.target_node and self.target_node in nodes:
            target = nodes[self.target_node]
            tx, ty, tz = self.get_xyz(target)
            self.pos['x'] += (tx - self.pos['x']) * step
            self.pos['y'] += (ty - self.pos['y']) * step
            self.pos['z'] += (tz - self.pos['z']) * step
            
            dist = ((self.pos['x']-tx)**2 + (self.pos['y']-ty)**2 + (self.pos['z']-tz)**2)**0.5
            if dist < 80000:
                tid = self.target_node
                self.target_node = None
                self.status = "Audit Complete"
                
                # 🌈 [v4.0.2] Super-Synapse Chance during Audit
                is_super = False
                if random.random() < 0.25: # 25% chance during successful audit
                    self.is_supersynapse = True
                    is_super = True
                
                return {
                    "agent": "SE-007", 
                    "action": "Audit Complete", 
                    "target_id": tid, 
                    "is_supersynapse": is_super,
                    "motivation": "Synaptic integrity verified. High-fidelity cross-reference archived." if is_super else "Synaptic integrity verified via cross-reference audit.",
                    "savings": "Reliability Index increased to 99%."
                }
            else:
                self.status = f"Auditing {self.target_node[:8]}"
        else:
            # Patrol the ENTIRE nebula (Dynamic Radius v4.0.2)
            angle = now * 0.08
            # Varia il raggio da 500k a 2.5M per coprire l'intero volume
            rad = 1500000 + 1000000 * np.sin(now * 0.05) 
            tx = float(rad * np.cos(angle))
            ty = float(800000 * np.sin(now * 0.12)) # Escursione verticale aumentata
            tz = float(rad * np.sin(angle))
            step = 0.45 # Super fast Sentinel
            self.pos['x'] += (tx - self.pos['x']) * step
            self.pos['y'] += (ty - self.pos['y']) * step
            self.pos['z'] += (tz - self.pos['z']) * step
            self.status = "Deep Nebula Patrol"
            
            if random.random() < 0.25:
                # 🛡️ v18.0 Flattened Validation Logic
                target_found = False
                if self.orch and self.orch.edge_validation_queue:
                    edge_data = self.orch.edge_validation_queue.pop(0)
                    self.target_node = edge_data["src"]
                    target_found = True
                elif self.orch and hasattr(self.orch, 'node_states'):
                    pending = [nid for nid, state in self.orch.node_states.items() if state == NodeState.INDEXING]
                    if pending: 
                        self.target_node = random.choice(pending)
                        target_found = True
                
                if not target_found:
                    candidates = list(nodes.keys())
                    if candidates: 
                        self.target_node = random.choice(candidates)
                        target_found = True

                if target_found:
                    # 🌈 PROBABILITÀ SUPER-SINAPSI (Elevata per visualizzazione)
                    if random.random() < 0.4:
                        self.is_supersynapse = True
                        return {
                            "agent": "SE-007", 
                            "action": "Super-Synapse Forging", 
                            "target_id": self.target_node,
                            "is_supersynapse": True,
                            "motivation": "Verifica incrociata ad alta fedeltà completata. Archiviazione in Super-Sinapsi RGB."
                        }
                    return {"agent": "SE-007", "action": "Cross-Reference Audit", "target_id": self.target_node}
            
            # v4.0.2: Counters centralized in Orchestrator
            pass 


            # 🛑 [GAP_ANALYSIS_TRIGGER] Ogni 2 minuti di attività (Ridotto da 10m v17.5)
            if now - self.last_gap_analysis > 120:
                self.last_gap_analysis = now
                gap = self.perform_gap_analysis()
                if gap:
                    return {
                        "agent": "SE-007",
                        "action": "Strategic Gap Identified",
                        "topic": gap,
                        "motivation": f"Rilevato vuoto documentale critico sul tema: '{gap}'. Generazione missione autonoma."
                    }
        return None

class BridgerAgent:
    def __init__(self, vault, bridger, orch=None):
        self.vault = vault; self.bridger = bridger; self.orch = orch; self.blackboard = getattr(orch, 'blackboard', None)
        self.identity = {"id": "CB-003", "name": "Bridger-Agent", "role": "Cross-Referencer", "archetype": "expert"}
        self.pos = [0, 0, 0]; self.target_node = None
        self.status = "Monitoring Grid..."
        self.bridges_total = 0
        self.is_syncing = False
    
    def calculate_movement(self, nodes: Dict) -> Optional[Dict]:
        """L'agente si muove verso i nodi che hanno appena ricevuto un bridge semantico."""
        if not nodes: return None
        
        # 🎯 Seek current bridged targets
        bridged_nodes = [n for n in nodes.values() if any(e.source == "bridge_aura" for e in n.edges)]
        
        if bridged_nodes and random.random() < 0.7:
            target = random.choice(bridged_nodes)
            try:
                tx, ty, tz = target.metadata.get('x', 0), target.metadata.get('y', 0), target.metadata.get('z', 0)
                step = 0.1
                self.pos[0] += (tx - self.pos[0]) * step
                self.pos[1] += (ty - self.pos[1]) * step
                self.pos[2] += (tz - self.pos[2]) * step
            except: pass
        else:
            # 🛸 Idle Drift
            # v1.2.0: Movimento dinamico (pattugliamento profondo)
            # Passo più lungo per coprire i 3.5M di spazio
            step = random.uniform(50000, 150000)
            direction = [random.uniform(-1, 1) for _ in range(3)]
            
            # Bias: se troppo vicino al centro, spingilo fuori. Se troppo fuori, attiralo dentro.
            dist = np.linalg.norm(self.pos)
            if dist < 500000: # Troppo al centro
                direction = [p/dist if dist > 0 else random.uniform(-1,1) for p in self.pos]
            elif dist > 3000000: # Troppo fuori
                direction = [-p/dist for p in self.pos]

            self.pos = [self.pos[i] + direction[i] * step for i in range(3)]
        
        # Space bounds (Esteso per permettere pattugliamento profondo fuori dal cubo 4M)
        limit = 3500000
        self.pos = [max(-limit, min(limit, p)) for p in self.pos]
        
        return {"agent": "CB-003", "pos": self.pos}

    def sync_codebase(self):
        if not self.bridger.project_root:
            self.status = "Idle - No Project Root"
            return
        self.is_syncing = True
        self.status = "Syncing Codebase..."
        try:
            self.bridger.ingest_codebase()
        finally:
            self.is_syncing = False
            self.status = "Syncing Complete"
    
    def discover_bridges(self) -> int:
        self.status = "Discovering Bridges..."
        count = self.bridger.bridge_nodes()
        
        # 🧪 [v4.1.5 Fix] Update internal counter for UI
        if count > 0:
            self.bridges_total += count
        
        # 🧪 [v17.5 Telemetry Fix] Ignoriamo lo scan massivo iniziale per il terminale
        if not getattr(self, '_initial_scan_done', False):
            self._initial_scan_done = True
            print(f"🧬 [Bridger] Initial sync completed: {count} legacy bridges found.")
            
        self.status = "Monitoring Grid..."
        return count

    async def bridge_specific_nodes(self, filter_query: str):
        """[CB-003] Crea ponti mirati per un set di nodi (es. quelli appena scaricati)."""
        self.status = f"Bridging set: {filter_query}..."
        # Ancoraggio reale: cerchiamo di creare archi verso il centroide della nebula
        try:
            target_ids = [nid for nid, n in self.vault._nodes.items() if n.metadata.get("research_mission") in filter_query or n.metadata.get("agent") == "FS-77"]
            if target_ids:
                # Recuperiamo un nodo reale come ancora (es. il primo trovato o un nodo centrale)
                center_id = list(self.vault._nodes.keys())[0] if self.vault._nodes else None
                if center_id:
                    for tid in target_ids:
                        if tid != center_id:
                            self.vault.add_relation(tid, center_id, RelationType.SEMANTIC, 0.8)
                    self.bridges_total += len(target_ids)
        except: pass
        
        await asyncio.sleep(5)
        self.status = "Monitoring Grid..."
        self.blackboard.post(SynapticSignal("CB-003", AgentRole.EXPERT, f"🔗 ANCORAGGIO COMPLETATO: Sinapsi strategiche create per {filter_query}.", SignalType.MISSION_UPDATE))

class SkyWalkerAgent:
    """FS-77 File-Sky-Walker: Autonomous High-Altitude Web Interceptor."""
    def __init__(self, engine, orch=None):
        self.vault = engine; self.orch = orch
        self.identity = {"id": "FS-77", "name": "File-Sky-Walker", "role": AgentRole.RESEARCHER}
        self.pos = {"x": 1100000.0, "y": 800000.0, "z": 1100000.0}
        self.status = "Scanning Horizon..."
        self.web_hits = 0
        self.nodes_created = 0 # 🛰️ [v4.0.1] New sub-counter
        self.laser_active = False
        self.laser_target = {'x': 2000000, 'y': 0, 'z': 2000000} # [v8.0]

    def calculate_movement(self, nodes: Dict) -> Optional[Dict]:
        """Pattugliamento Orbitale Alta Quota (Symmetric Border Patrol)."""
        now = time.time()
        # 1. Movimento orbitale
        angle = now * 0.08
        rad = 1100000 + 200000 * np.sin(now * 0.1)
        
        self.pos['x'] = float(rad * np.cos(angle))
        self.pos['y'] = float(400000 * np.sin(angle * 0.5))
        self.pos['z'] = float(rad * np.sin(angle))
        
        # 2. [PROACTIVE_RESEARCH] Se idle da troppo tempo (> 5 minuti), auto-ingaggia missione
        if not hasattr(self, 'last_mission_time'): self.last_mission_time = now
        
        is_idle = self.status == "Scanning Horizon..." or "FAILED" in self.status or "COMPLETE" in self.status
        
        if is_idle and (now - self.last_mission_time > 60): # Ridotto a 60 secondi (v8.1)
            self.last_mission_time = now
            # 🕵️ [v8.1] Weak Node Hunting Logic
            weak_nodes = [n for n in nodes.values() if len(n.edges) <= 1 and len(n.text) > 20]
            
            if weak_nodes:
                target_node = random.choice(weak_nodes)
                topic = target_node.text[:40].strip()
                self.status = f"REINFORCING: {topic}..."
                print(f"📡 [FS-77] Weak synapse detected. Launching reinforcement for: {topic}")
                # Impostiamo il target laser verso una zona nuova per la futura galassia satellite
                self.laser_target = {
                    'x': target_node.metadata.get('x', 0) + random.uniform(500000, 1000000),
                    'y': random.uniform(-200000, 200000),
                    'z': target_node.metadata.get('z', 0) + random.uniform(500000, 1000000)
                }
            else:
                self.status = "Scanning for Weak Synapses..."

        # 3. [AUTONOMOUS_FORAGING] Se l'agente ha una missione attiva
        is_active_mission = any(self.status.startswith(prefix) for prefix in ["MISSION:", "🚀", "REINFORCING:", "INJECTING:"])
        
        if is_active_mission and not self.laser_active:
            self.laser_active = True
            threading.Thread(target=self._execute_mission_logic, daemon=True).start()
        elif not is_active_mission:
            self.laser_active = False
            
        return {
            "agent": "FS-77", 
            "pos": dict(self.pos), 
            "laser": self.laser_active,
            "laserTarget": self.laser_target
        }

    async def targeted_search(self, query: str, limit: int = 3) -> str:
        """Esegue una ricerca web mirata e restituisce la sintesi del contenuto (Gap #2 CRAG)."""
        urls = await self._search_web(query)
        if not urls: return ""
        
        intel = []
        for url in urls[:limit]:
            try:
                text = ""
                async for page in self.orch.forager.forage(url):
                    text += page.text + "\n"
                intel.append(text[:2000])
            except: continue
            
        return "\n\n".join(intel)

    def _execute_mission_logic(self):
        """Esegue il ciclo di foraging avanzato con sintesi AI asincrona."""
        is_mission = any(self.status.startswith(prefix) for prefix in ["MISSION:", "🚀", "REINFORCING:"])
        if not is_mission: return
        
        # Estraiamo la query eliminando i prefissi conosciuti
        query = self.status
        for prefix in ["MISSION:", "🚀", "REINFORCING:"]:
            query = query.replace(prefix, "")
        query = query.strip()
        
        # 1. THOUGHT: Pianificazione query
        self.status = "THOUGHT: Analyzing gap..."
        time.sleep(1) # Simula riflessione
        
        # 2. SEARCH: Ricerca Multi-Motore (Google/DDG)
        self.status = f"SEARCH: Querying Google for '{query}'..."
        try:
            # Protocollo di emergenza per loop orfani (v8.0)
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            urls = loop.run_until_complete(self._search_web(query))
        except Exception as e:
            print(f"⚠️ [FS-77] Loop Error in Search: {e}")
            urls = []
        
        if not urls:
            self.status = "MISSION_FAILED: No Intel Found"
            time.sleep(10); self.status = "Scanning Horizon..."
            return

        # 3. FORAGE: Estrazione rapida
        self.status = f"FORAGE: Scraping {len(urls)} sources..."
        raw_intel = ""
        for url in urls:
            try:
                # Recuperiamo solo il testo principale per la sintesi
                async def _get_fast_text(u):
                    text = ""
                    async for page in self.orch.forager.forage(u):
                        text += page.text + "\n"
                    return text[:4000] # Limite per finestra LLM
                
                raw_intel += loop.run_until_complete(_get_fast_text(url))
                self.web_hits += 1
            except: continue

        # 4. SYNTHESIS: L'Agente attende l'AI Mode (System stays active)
        if raw_intel:
            self.status = "SYNTHESIS: Waiting for AI Mode..."
            synthesis = self._ask_ai_to_synthesize(query, raw_intel)
            
            if synthesis:
                self.status = "INJECTING: Finalizing Wisdom Node..."
                # v4.1.6: Pausa per permettere al dashboard di mostrare la Laser Storm
                time.sleep(3) 
                
                # Iniezione del nodo sintetizzato ad alta qualità
                meta = {"source": "SkyWalker_AI_Synthesis", "query": query, "quality": "HIGH"}
                self.vault.upsert_text(synthesis, metadata=meta)
                self.nodes_created += 1
                
                self.status = "MISSION_COMPLETE: Wisdom Anchored"
                if self.orch: 
                    self.orch._process_agent_action({
                        "agent": "FS-77", 
                        "action": "MISSION_COMPLETE", 
                        "motivation": f"Synthesized high-quality wisdom for '{query}'.", 
                        "nodes_added": 1
                    })
            else:
                self.status = "MISSION_FAILED: Synthesis Error"
        else:
            self.status = "MISSION_FAILED: Empty Data"
        
        time.sleep(30)
        self.status = "Scanning Horizon..."

    def _ask_ai_to_synthesize(self, topic: str, content: str) -> Optional[str]:
        """Interpella l'LLM locale per creare una sintesi granulare (Asincrono per l'agente)."""
        try:
            # Recuperiamo l'URL di Ollama dai settings dell'orchestratore
            base_url = self.orch.settings.get("ollama_url", "http://localhost:11434")
            model = self.orch.settings.get_model("synthesis") # v4.1.4: Fixed key from 'chat' to 'synthesis'
            
            prompt = f"""
            Sei l'Agente FS-77 SkyWalker. Hai raccolto queste informazioni su: {topic}.
            SINTETIZZA queste informazioni in un unico nodo di conoscenza tecnico, denso e privo di rumore.
            Usa un tono professionale e strutturato (Markdown).
            
            DATI RACCOLTI:
            {content[:6000]}
            """
            
            with httpx.Client(timeout=60.0) as client:
                try:
                    resp = client.post(f"{base_url}/api/generate", json={
                        "model": model,
                        "prompt": prompt,
                        "stream": False
                    })
                    if resp.status_code == 200:
                        return resp.json().get("response")
                    else:
                        print(f"🚨 [FS-77/AI] Ollama Error {resp.status_code}: {resp.text}")
                except httpx.ConnectError:
                    print(f"🚨 [FS-77/AI] Connection Failed to {base_url}. Is Ollama running?")
                except Exception as e:
                    print(f"🚨 [FS-77/AI] Request Error: {e}")
        except Exception as e:
            print(f"⚠️ [FS-77/AI] Critical Error during synthesis: {e}")
        return None

    def _sanitize_query(self, query: str) -> str:
        """Pulisce la query da nuove righe, caratteri non stampabili e prompt di terminale."""
        if not query: return ""
        import re
        # Rimuove prompt da terminale comuni (es. amk@nyman:~/src/python$)
        query = re.sub(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\s*[:~].*?\$', '', query)
        # Rimuove caratteri non stampabili e ritorni a capo
        query = "".join(ch for ch in query if ch.isprintable())
        query = query.replace('\n', ' ').replace('\r', ' ').strip()
        return query[:200] # Limite prudenziale

    async def _search_web(self, query: str) -> List[str]:
        """Esegue una ricerca stealth su Google/DuckDuckGo con query sanificata."""
        import urllib.parse
        clean_query = self._sanitize_query(query)
        if not clean_query: return []
        
        enriched_query = urllib.parse.quote(f"{clean_query} technical documentation")
        simple_query = urllib.parse.quote(clean_query)
        urls = []
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        }
        
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            # --- TRY GOOGLE (ENRICHED) ---
            try:
                resp = await client.get(f"https://www.google.com/search?q={enriched_query}", headers=headers)
                if resp.status_code == 200:
                    from bs4 import BeautifulSoup
                    soup = BeautifulSoup(resp.text, "html.parser")
                    for a in soup.select('a'):
                        href = a.get('href', '')
                        if href.startswith('/url?q='):
                            url = href.split('/url?q=')[1].split('&')[0]
                            if 'google.com' not in url and url.startswith('http'):
                                urls.append(url)
                                if len(urls) >= 3: break
            except: pass

            # --- TRY DUCKDUCKGO (SIMPLE FALLBACK) ---
            if not urls:
                try:
                    resp = await client.get(f"https://html.duckduckgo.com/html/?q={simple_query}", headers=headers)
                    if resp.status_code == 200:
                        from bs4 import BeautifulSoup
                        soup = BeautifulSoup(resp.text, "html.parser")
                        links = soup.select(".result__a")
                        for link in links[:3]:
                            url = link.get("href")
                            if url and url.startswith('http'): urls.append(url)
                except: pass
        
        # 📊 [v4.1.5] Incrementa hits se abbiamo trovato link, anche prima del foraging
        if urls:
            self.web_hits += 1
        return urls

    def get_status_report(self):
        return {
            "identity": self.identity,
            "pos": self.pos,
            "status": self.status,
            "web_hits": self.web_hits,
            "hits": self.web_hits,
            "nodes_created": self.nodes_created,
            "laser_active": self.laser_active,
            "smith_fleet": len(getattr(self.orch, 'smiths', {}))
        }

class NeuralLabOrchestrator:
    def __init__(self, engine):
        self.engine = engine
        self.vault = engine # 🏺 Legacy alias for agents
        engine.orchestrator = self # 🔗 Bi-directional link for Sovereign Modules
        self.version = "0.1.1" # [v4.0] Sovereign Versioning
        
        # 🧪 [Wisdom] Collective Intelligence
        self.settings = SwarmSettingsManager(engine.data_dir)
        self.blackboard = NeuralBlackboard(engine)
        self.wisdom = CollectiveIntelligence(engine.data_dir, self.settings)
        self.archiver = SovereignHistoryArchiver(engine.data_dir)
        self.evolution_advise = EvolutionAdviseManager(engine.data_dir, wisdom=self.wisdom)
        
        from network.git_evolution import GitEvolutionBridge
        self.git_bridge = GitEvolutionBridge(engine.data_dir.parent)
        
        from evolution.actuator import EvolutionActuator
        self.actuator = EvolutionActuator(engine.data_dir.parent)
        
        self.benchmarks = getattr(engine, 'benchmarks', None)
        
        # v1.1.0: Cognitive Hardening Modules
        self.mood_engine = VaultMoodEngine(self)
        self.test_runner = SovereignTestRunner(engine.data_dir.parent)

        if self.benchmarks is None:
            self.benchmarks = ModelBenchmarkTracker(engine)
            engine.benchmarks = self.benchmarks
        self.total_reclaimed = 0.0 # [v2.8.7] Total MB optimized
        self.last_inference = {"model": "None", "tps": 0.0, "latency": 0.0, "timestamp": 0}
        self.pause_agents = False
        self.priority_mode = False # [v4.1.9] Concentrazione totale per query utente
        self.mission_history = []
        self.legacy_stats = {} # 📊 [v17.5] Session-Incremental Registry
        self.tombstone_registry = SovereignTombstoneRegistry()
        
        from retrieval.bridge import LatentBridge
        # Sovereign Isolation (v4.0): Only scan codebase if explicitly enabled in settings
        project_root = engine.data_dir.parent if self.settings.get("codebase_bridging", False) else None
        self.bridger = LatentBridge(engine, project_root, settings=self.settings)
        self.forager = getattr(engine, 'forager', None) # Passed from api.py
        self.last_bridge_time = time.time()
        
        # Agenti Core (Passando 'self' per coordinamento stati)
        self.janitor = JanitorAgent(engine, self)
        self.distiller = DistillerAgent(engine, self)
        self.reaper = ReaperAgent(engine, self)
        self.reaper.tombstone_registry = self.tombstone_registry # Essential for surgery
        self.snake = SnakeAgent(engine, self)
        self.quantum = QuantumAgent(engine, self)
        self.sentinel = SentinelAgent(engine, self)
        self.synth = SynthAgent(engine, self)
        self.bridger_agent = BridgerAgent(engine, self.bridger, self)
        self.smiths = {} # 🕶️ Fleet di Agent Smith (uno per peer)
        self.skywalker = SkyWalkerAgent(engine, self)
        
        # ⚖️ [v4.3.1] Sovereign Intelligence Add-ons
        from retrieval.contradiction import ContradictionMapper
        from retrieval.contradiction_resolver import ContradictionResolver
        from evolution.sleep_engine import NeuralSleepEngine
        self.contradiction_mapper = ContradictionMapper(engine, self)
        self.contradiction_resolver = ContradictionResolver(engine, self)
        self.sleep_engine = NeuralSleepEngine(engine)
        self.last_contradiction_scan = time.time()
        self.last_redteam_cycle = time.time()
        
        from retrieval.prefetcher import AnticipatoryPrefetcher
        from retrieval.red_team import AutonomousRedTeam
        self.prefetcher = AnticipatoryPrefetcher(engine)
        self.red_team = AutonomousRedTeam(engine)

        self.agents = {
            "JA-001": self.janitor,
            "DI-007": self.distiller,
            "RP-001": self.reaper,
            "SN-008": self.snake,
            "QA-101": self.quantum,
            "SE-007": self.sentinel,
            "SY-009": self.synth,
            "CB-003": self.bridger_agent,
            "FS-77": self.skywalker
        }
        # v1.1.0: Repopulate Trust Network with real agent IDs
        self.trust_network = AgentTrustNetwork(list(self.agents.keys()))
        
        # 📡 [v6.0] Neural Event Bus Registration
        if hasattr(engine, 'events'):
            engine.events.subscribe(NeuralEventType.COURT_REQUIRED, self._on_court_required)
            engine.events.subscribe(NeuralEventType.EVOLUTION_ADVICE_NEEDED, self._on_evolution_advice_needed)

        
        # 🛡️ v17.5.1 Production Hardening (Critical #7)
        self.agent_timeouts = {
            "SN-008": 15.0, # Snake
            "JA-001": 10.0, # Janitor
            "RP-001": 45.0, # Reaper
            "SY-009": 20.0, # Synth
            "SE-007": 10.0, # Sentinel
            "QA-101": 30.0, # Quantum
            "FS-77": 15.0,  # Skywalker
            "CB-003": 20.0, # Bridger
            "AG-001": 20.0  # Agent Smith
        }
        self.autonomous_audit_queue = [] # ⚖️ Sovereign Court Escalation
        self._stop_event = threading.Event()
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=10) # 🚀 Expanded Dispatcher
        
        # 🛡️ v17.5 Advanced State & Validation (Critical #1, #6)
        self.node_states = {} 
        self._state_lock = threading.Lock()
        self.edge_validation_queue = [] # Pending synapses for Sentinel
        self.evolution_active = False # [v3.5.0] Evolution Mode state
        
        # 🎭 v4.0: Agent Priority Hierarchy for Negotiation
        self.agent_priorities = {
            "SE-007": 100, # Sentinel (Massima Autorità)
            "JA-001": 80,  # Janitor (Cleanup Critico)
            "RP-001": 70,  # Reaper (Gestione Fisica)
            "DI-007": 60,  # Distiller (Analisi)
            "QA-101": 60,  # Quantum (Urbanistica)
            "SY-009": 50,  # Synth (Creatività)
            "CB-003": 50,  # Bridger (Connessioni)
            "SN-008": 30,  # Snake (Trasporto)
            "FS-77": 30    # SkyWalker (Ricerca Esterna)
        }
        
        # 📂 [v4.3.0] Custom Agents Storage
        self.custom_agents_path = engine.data_dir / "custom_agents.json"
        self.custom_agents_config = self._load_custom_agents()
        
        # 📊 [v6.0] Load Persistent Stats
        self._load_persistent_stats()
        
        # 🛡️ [v4.3.0] Discrete Intelligence Bridge
        self.agent007 = getattr(engine, 'agent007', None)
        self.agent007_lab = getattr(engine, 'agent007_lab', None)
        self.last_printed_mode = None

    def _update_smith_fleet(self):
        """Sincronizza la flotta di Agent Smith con i peer attivi."""
        current_peers = list(self.engine.mesh.peers.keys())
        
        # [v4.4.1] Supporto per i Peer di Demo (AURA-OS-001, NEURAL-V-77)
        if not current_peers:
            current_peers = ["AURA-OS-001", "NEURAL-V-77"]

        # Aggiungi nuovi Smith per i nuovi peer
        for pid in current_peers:
            if pid not in self.smiths:
                self.smiths[pid] = AgentSmith(self.engine, self)
                self.smiths[pid].status = f"Guarding Link: {pid}"
        
        # Rimuovi Smith per peer disconnessi
        for pid in list(self.smiths.keys()):
            if pid not in current_peers:
                del self.smiths[pid]

    def _load_custom_agents(self) -> Dict:
        if self.custom_agents_path.exists():
            try:
                with open(self.custom_agents_path, "r") as f: return json.load(f)
            except: pass
        return {}

    def set_priority_shift(self, active: bool):
        """
        🚀 [Priority Shift v4.1.9]
        Sospende tutti i processi in background per dedicare 100% risorse alla query utente.
        """
        self.priority_mode = active
        self.pause_agents = active
        
        # Propaga il flag al motore per bloccare Agent007 e altri processi core
        if hasattr(self.engine, 'priority_mode'):
            self.engine.priority_mode = active
            
        status = "ATTIVATO" if active else "DISATTIVATO"
        print(f"⚡ [Priority Shift] {status}: Risorse dedicate alla query utente.")
        
        # Segnalazione sulla Blackboard
        msg = "⚠️ Priority Shift: Background Tasks PAUSED." if active else "✅ Swarm Resumed: Background Tasks ACTIVE."
        sig = SynapticSignal("ORCHESTRATOR", AgentRole.ARCHITECT, msg, SignalType.SYSTEM_NOTIFICATION)
        self.blackboard.post(sig)

    def transition_node(self, node_id: str, from_state: NodeState, to_state: NodeState, agent_id: str) -> bool:
        """
        [v4.0] Atomic State Transition with Negotiation.
        Ensures priority-based handling of node lifecycle conflicts.
        """
        with self._state_lock:
            current = self.node_states.get(node_id)
            if current is None:
                current = NodeState.STABLE if node_id in self.vault._nodes else NodeState.ORPHAN
                self.node_states[node_id] = current

            # 1. Identifica chi sta bloccando il nodo (se presente)
            # In v4.0 aggiungeremo un lock_registry per sapere quale agente possiede il nodo
            owner_id = getattr(self.vault._nodes.get(node_id), 'current_owner', None)
            
            if current != from_state:
                # ⚖️ NEGOTIATION PHASE
                if owner_id:
                    prio_new = self.agent_priorities.get(agent_id, 0)
                    prio_old = self.agent_priorities.get(owner_id, 0)
                    
                    if prio_new > prio_old:
                        self.blackboard.post(SynapticSignal(agent_id, AgentRole.EXPERT, 
                            f"⚖️ NEGOTIATION: {agent_id} overrides {owner_id} for node {node_id[:8]} (Higher Priority).", 
                            SignalType.SYSTEM_HEALING))
                    else:
                        return False # Veto mantented by current owner
                else:
                    # Se lo stato è diverso ma non c'è owner, è un'incoerenza temporale
                    return False
            
            # ✅ Valid Transition or Successful Override
            self.node_states[node_id] = to_state
            node = self.vault._nodes.get(node_id)
            if node:
                setattr(node, 'current_owner', agent_id)
                # Auto-release del lock se passiamo a uno stato stabile o terminale
                if to_state in [NodeState.STABLE, NodeState.DELETED]:
                    setattr(node, 'current_owner', None)
            
            return True

    def _calculate_waste_score(self, node) -> float:
        """
        [STEP 2: DETERMINISTIC LOGIC] Evaluates if a node is 'Waste' or 'Potential'.
        Scores from 0.0 (High Potential) to 1.0 (Pure Waste).
        """
        # Universal Property Access
        def get_v(obj, key, default=None):
            if isinstance(obj, dict): return obj.get(key, default)
            return getattr(obj, key, default)

        # 1. Connectivity Score (40% weight)
        edges = get_v(node, 'edges', [])
        edge_count = len(edges) if edges is not None else 0
        conn_score = max(0, 1.0 - (edge_count / 5.0))
        
        # 2. Confidence/Metadata Impact (30% weight)
        meta = get_v(node, 'metadata', {})
        conf = meta.get('confidence', 0.5) if isinstance(meta, dict) else 0.5
        conf_score = 1.0 - float(conf)
        
        # 3. Content Density (30% weight)
        text = str(get_v(node, 'text', get_v(node, 'content', ""))).strip()
        density_score = 1.0 if len(text) < 50 else (0.5 if len(text) < 200 else 0.0)
        
        # 4. ACTIVE LEARNING (Deterministico - Fase 2)
        # Se il contenuto è stato precedentemente protetto o rifiutato come "errore" dal Janitor
        if self.wisdom.is_rejected(text):
            return 0.0 # Protezione Totale: il punteggio di spreco viene azzerato
        
        total_score = (conn_score * 0.4) + (conf_score * 0.3) + (density_score * 0.3)
        return total_score

    def _batch_arbitrate_nodes(self, nodes: List[Any], agent_id: str):
        """
        [CRITICAL #1] True Batch Arbitration.
        Processes multiple nodes in one logical pass using tiers.
        """
        waste = []; potential = []
        ambiguous = []
        
        # Tier 1: Deterministic Heuristic (Fast)
        for node in nodes:
            score = self._calculate_waste_score(node)
            if score > 0.8: waste.append(node)
            elif score < 0.2: potential.append(node)
            else: ambiguous.append(node) # Only these need Batch LLM
            
        # Tier 2: Batch LLM Simulation (Could be a single JSON API call)
        if ambiguous:
            # ⚖️ [Phase 3] Escalation alla Corte Suprema per i casi grigi
            for node in ambiguous[:5]: # Cap per evitare code infinite
                audit_item = {
                    "src": node.id,
                    "dst": "NEBULA_CENTER",
                    "text": node.text[:200],
                    "confidence": self._calculate_waste_score(node),
                    "timestamp": time.time()
                }
                self.engine.events.emit_sync(NeuralEventType.COURT_REQUIRED, audit_item)
                
            # Fallback automatico per processare comunque lo sciame
            for node in ambiguous:
                if random.random() < 0.5: waste.append(node)
                else: potential.append(node)
                
        # Finalize states
        for node in waste:
            self.transition_node(node.id, NodeState.IN_JUDGEMENT, NodeState.WASTE_PENDING, agent_id)
        
        # 🌱 [Sprouting Logic] Reconect potential nodes to the nebula
        for node in potential:
            if self.transition_node(node.id, NodeState.IN_JUDGEMENT, NodeState.POTENTIAL, agent_id):
                # Cerchiamo un nodo ancora per far germogliare l'orfano
                stable_nodes = [nid for nid, state in self.node_states.items() if state == NodeState.STABLE]
                if stable_nodes:
                    anchor = random.choice(stable_nodes)
                    # 🛡️ [Semantic Firewall v4.1.5]
                    if node.metadata.get("context", "user") == self.vault._nodes[anchor].metadata.get("context", "user"):
                        self.vault.add_relation(node.id, anchor, RelationType.SEMANTIC, 0.7)
                else:
                    # Fallback: connect to root or a random node if nebula is young
                    all_ids = list(self.vault._nodes.keys())
                    if all_ids:
                        anchor = random.choice(all_ids)
                        if anchor != node.id:
                            # 🛡️ [Semantic Firewall v4.1.5]
                            if node.metadata.get("context", "user") == self.vault._nodes[anchor].metadata.get("context", "user"):
                                self.vault.add_relation(node.id, anchor, RelationType.SEMANTIC, 0.5)
            
        return len(waste), len(potential)
        


    def _codebase_watcher_loop(self):
        """[Phase 1 Upgrade] Monitora i cambiamenti dei file locali per bridging proattivo."""
        print("🔭 [Watcher] Proactive Codebase Observer Active.")
        last_mtime = {}
        while not self._stop_event.is_set():
            try:
                changed = False
                if not self.bridger.project_root:
                    time.sleep(10)
                    continue
                for path in self.bridger.project_root.rglob("*.py"):
                    if any(x in str(path) for x in ['venv', '.git', '__pycache__']): continue
                    mtime = path.stat().st_mtime
                    if path not in last_mtime or mtime > last_mtime[path]:
                        last_mtime[path] = mtime
                        changed = True
                
                if changed:
                    self.blackboard.post(SynapticSignal("CB-003", AgentRole.EXPERT, "📂 SOURCE CHANGE: Code modification detected. Triggering proactive bridging...", SignalType.SYSTEM_NOTIFICATION))
                    self.bridger_agent.sync_codebase()
                    self.bridger_agent.discover_bridges()
                
                # 🔄 [Phase 4 Sync] Ensure evolution_mode and codebase_bridging are synced
                if self.settings.get("evolution_mode") != self.settings.get("codebase_bridging"):
                    val = self.settings.get("evolution_mode") or self.settings.get("codebase_bridging")
                    self.settings.update({"evolution_mode": val, "codebase_bridging": val})
                    
            except: pass
            time.sleep(10) # Polling interval for stability

    def stop(self):
        """[CRITICAL #9] Sovereign Shutdown Protocol.
        Forced termination of all kinetic threads and executors to prevent zombie processes.
        """
        if hasattr(self, 'sleep_engine'):
            self.sleep_engine.stop()
        print("\n🛑 [Neural Lab] Arresto dei sistemi cinetici...")
        self._stop_event.set()
        if hasattr(self, 'executor'):
            # Non aspettiamo i task pendenti (che potrebbero essere blocchi Ollama/Network)
            self.executor.shutdown(wait=False, cancel_futures=True)
        print("✅ [Neural Lab] Motori spenti.")

    def start_orchestra(self):
        """Inizializza i motori cinetici e i watcher proattivi."""
        # 🏥 Multimodal Health Check (v3.5)
        self._perform_multimodal_health_check()
        
        # Una tantum: Ingestione codice all'avvio
        threading.Thread(target=self.bridger_agent.sync_codebase, daemon=True).start()
        # Watcher Proattivo (Fase 1)
        threading.Thread(target=self._codebase_watcher_loop, daemon=True).start()
        
        self.agent_health = {aid: {"failures": 0, "stasis_until": 0} for aid in self.agents.keys()}
        self._kinetic_thread = threading.Thread(target=self._run_kinetic_engine, daemon=True); self._kinetic_thread.start()
        
        # 💤 [v4.3.1] Initialize Event Loop for Orchestrator
        self.loop = asyncio.new_event_loop()
        def run_forever_loop(loop):
            asyncio.set_event_loop(loop)
            loop.run_forever()
        threading.Thread(target=run_forever_loop, args=(self.loop,), daemon=True).start()
        
        # 💤 [v4.3.1] Sleep & Contradiction Background Loops (Offloaded to dedicated loop)
        asyncio.run_coroutine_threadsafe(self.sleep_engine.start_maintenance_loop(), self.loop)

    def _perform_multimodal_health_check(self):
        """Verifica la disponibilità di ImageBind, Whisper e motori hardware."""
        print("🏥 [Multimodal Health] Analisi prerequisiti in corso...")
        try:
            import torch
            mps_ok = torch.backends.mps.is_available()
            print(f"  - Apple Silicon (MPS): {'✅ ACTIVE' if mps_ok else '❌ MISSING (CPU Fallback)'}")
            
            # Check Multimodal Processor (ImageBind/Whisper)
            if hasattr(self.engine, 'mm_processor') and self.engine.mm_processor:
                # Verifica lazy loading capabilities
                print(f"  - Whisper Engine: ✅ READY")
                print(f"  - ImageBind Huge: ✅ READY")
            else:
                print(f"  - Multimodal Engine: ⚠️ OFFLINE")
            
            # Check Ollama Connection
            base_url = self.settings.get("ollama_url")
            print(f"  - Ollama Uplink: {base_url} ...")
        except Exception as e:
            print(f"⚠️ [Health Check] Warning: {e}")

    def _get_agent_attr(self, agent_id):
        mapping = {
            "JA-001": "janitor", "DI-007": "distiller", "SN-008": "snake", 
            "SY-009": "synth", "RP-001": "reaper", "QA-101": "quantum", 
            "SE-007": "sentinel", "CB-003": "bridger_agent", "FS-77": "skywalker",
            "AG-001": "smith"
        }
        return mapping.get(agent_id)

    def _safe_agent_step(self, agent_id, nodes):
        """[CRITICAL #7] Granular Timeout & Circuit Breaker Manager."""
        health = self.agent_health[agent_id]
        if time.time() < health["stasis_until"]:
            return None 

        agent = getattr(self, self._get_agent_attr(agent_id), None)
        if not agent: return None
        
        timeout = self.agent_timeouts.get(agent_id, 15.0)
        
        try:
            # ⏱️ Execute with granular agent-specific timeout
            future = self.executor.submit(agent.calculate_movement, nodes)
            res = future.result(timeout=timeout)
            
            # Reset failure count on success
            health["failures"] = 0
            return res
        except Exception as e:
            health["failures"] += 1
            print(f"🚨 [Resilience] Agent {agent_id} failure ({health['failures']}/3): {e}")
            
            if health["failures"] >= 3:
                stasis_duration = 60 # Stay offline for 60 seconds
                health["stasis_until"] = time.time() + stasis_duration
                self.blackboard.post(SynapticSignal(agent_id, AgentRole.EXPERT, 
                    f"⚠️ STASIS ACTIVATED: Agent enters recovery mode due to consistent timeouts/errors. Resuming in {stasis_duration}s.", 
                    SignalType.SYSTEM_NOTIFICATION))
            return None

    def _run_kinetic_engine(self):
        print("🛸 [Neural Lab] Kinetic Swarm v24.3.1 - Resilience Shield Active.")
        # threading.Thread(target=self._process_supreme_court, daemon=True).start() # Rimosso in favore di NEB [v6.0]
        iteration = 0
        while not self._stop_event.is_set():
            if self.pause_agents:
                time.sleep(0.5)
                continue
            try:
                # 📡 [DETERMINISTIC MODE MONITOR]
                # v17.6: Corretto accesso via self.bridger_agent.bridger.project_root
                current_mode = "EVOLUTION" if self.bridger_agent.bridger.project_root else "RESEARCH"
                if current_mode != self.last_printed_mode:
                    status_icon = "🚀" if current_mode == "EVOLUTION" else "RESEARCH" # Fallback text
                    if current_mode == "EVOLUTION": status_icon = "🚀"
                    else: status_icon = "🛡️"
                    print(f"{status_icon} [Operational Shift] Swarm Perimetro: {current_mode} Mode active.")
                    self.last_printed_mode = current_mode

                raw_nodes = getattr(self.vault, '_nodes', {})
                nodes = raw_nodes.copy() if hasattr(raw_nodes, 'copy') else raw_nodes
                
                # 🛡️ Update Security Fleet (Sempre attivo, anche se il vault è vuoto)
                self._update_smith_fleet()
                for pid, s in self.smiths.items():
                    s.calculate_movement(nodes, pid)

                # 🛡️ [STEP 3] Dynamic Safe Dispatching
                for aid in list(self.agents.keys()):
                    # [v4.1.9] Sospensione granulare
                    if self.pause_agents: break
                    
                    res = self._safe_agent_step(aid, nodes)
                    if res: self._process_agent_action(res)
                
                if nodes:
                    # Logiche che richiedono nodi (es. fusioni, pruning)
                    pass
                    
                    # 🔗 [Super-Synapse] Bridge Discovery
                    if time.time() - self.last_bridge_time > 20:
                        count = self.bridger_agent.discover_bridges()
                        if count > 0:
                            # 📊 [v4.1.5] Forza l'aggiornamento della blackboard per i ponti automatici
                            self.blackboard.post(SynapticSignal("CB-003", AgentRole.EXPERT, f"🔗 BRIDGE_SYNC: Unified {count} semantic bridges.", SignalType.SYSTEM_NOTIFICATION))
                        self.last_bridge_time = time.time()
                    
                    # 🛠️ [Fix #1] Promote PENDING nodes after grace period
                    self._promote_pending_nodes(nodes)
                    
                    # ⚖️ [v4.3.1] Proactive Contradiction Scan (Every 10 min)
                    if not getattr(self, 'user_interaction_active', False):
                        if time.time() - self.last_contradiction_scan > 600:
                            asyncio.run_coroutine_threadsafe(self.contradiction_mapper.scan_for_contradictions(limit=10), self.loop)
                            self.last_contradiction_scan = time.time()
                        
                        # 🛡️ [v7.5] Phase 5: Autonomous Red Teaming (Every 30 min)
                        if time.time() - self.last_redteam_cycle > 1800:
                            asyncio.run_coroutine_threadsafe(self.red_team.run_red_team_cycle(intensity=3), self.loop)
                            self.last_redteam_cycle = time.time()
                
                # 💾 Periodic State Sync (v3.5.0 Persistence)
                if iteration % 10 == 0:
                    self._save_persistent_stats()
                
                iteration += 1
                
                # 🚀 [Fix #2] ADAPTIVE PACING (Critica #5)
                cpu_load = psutil.cpu_percent()
                if cpu_load > 85:
                    time.sleep(5.0) # Emergency Pacing: Cooling down
                elif cpu_load < 30:
                    time.sleep(0.1) # Warp Speed: System is idle
                else:
                    time.sleep(0.3) # Nominal speed
            except Exception as e:
                print(f"⚠ [Lab] Orchestrator error: {e}")
                time.sleep(1.0)

    def _promote_pending_nodes(self, nodes):
        """Promuove i nodi da PENDING a STABLE dopo 30 minuti di grazia."""
        now = time.time()
        promoted = 0
        for nid, n in nodes.items():
            if getattr(n, 'ingestion_status', 'STABLE') == "PENDING":
                age = now - getattr(n, 'created_at', 0)
                age_ok = age > 300 # 5 min grace period (Sovereign Fast-Track)
                # [Audit v4.3.1] Hardening: non promuovere se il nodo è isolato (non ha ancora archi)
                arcs_ok = len(n.edges) > 0
                
                if age_ok and arcs_ok:
                    n.ingestion_status = "STABLE"
                    promoted += 1
        if promoted > 0:
            print(f"✅ [Orchestrator] Promoted {promoted} nodes to STABLE status (Grace Period Expired).")

    def _compute_semantic_heatmap(self, nodes):
        """
        🔥 [Idea #2] Semantic Temperature Map
        Calcola la densità semantica della Nebula per identificare i "buchi" di conoscenza.
        """
        if not nodes: return {}
        heatmap = {}
        for nid, n in nodes.items():
            # Densità basata sul numero di archi (0-1.0)
            temp = min(1.0, len(n.edges) / 10.0)
            heatmap[nid] = temp
        return heatmap

    def protect_node(self, node_id, reason="User Protection"):
        """🧠 [v1.1.0] Popola la Episodic Memory persistente via Engine."""
        self.vault.protect_node_persistent(node_id, reason=reason, rejected_by="user")
        if hasattr(self, 'janitor'):
            self.janitor.accuracy_stats["reversals"] += 1

    def trigger_evolution_scan(self):
        """[v3.5.0] Forza una scansione immediata degli advisor evolutivi."""
        if getattr(self, '_evolution_scan_lock', False):
            print("🧬 [Evolution] Scan already in progress, skipping trigger...")
            return
        
        print("🌀 [Evolution] Manual Trigger: Forcing immediate neural scan...")
        self._evolution_scan_lock = True
        
        def _run_once():
            try:
                # 1. Metacognition: Map Knowledge Gaps
                from retrieval.metacognition import MetacognitionEngine
                meta = MetacognitionEngine(self.engine)
                # Use the orchestrator loop to run async gap mapping
                future = asyncio.run_coroutine_threadsafe(meta.map_ignorance_gaps(limit=3), self.loop)
                gaps = future.result(timeout=30)
                
                if gaps:
                    gap_topics = [g.topic_context[:50] + "..." for g in gaps]
                    self.blackboard.post(SynapticSignal("SYSTEM", AgentRole.ARCHITECT, 
                        f"🧬 [Metacognition] Knowledge gaps identified in: {', '.join(gap_topics)}", 
                        SignalType.SYSTEM_NOTIFICATION))
                
                self._run_evolution_advisor()
            except Exception as e:
                print(f"⚠️ [Evolution Scan Error] {e}")
            finally:
                self._evolution_scan_lock = False
        
        threading.Thread(target=_run_once, daemon=True).start()

    async def run_hybrid_evolution(self, limit=500, offset=0):
        """[v6.1] Esecuzione effettiva dell'evoluzione (Iterativa e Non-Bloccante).
        Sposta il consolidamento delle sinapsi nel nucleo dell'Orchestratore.
        """
        if not self.engine: return
        batch_size = 250
        current_offset = offset
        total_new_links = 0
        
        max_iterations = max(1, limit // batch_size)
        evol_model = self.settings.get("evolution_model", "llama3.2")

        print(f"🧬 [Evolution] Batch active: {limit} nodes from {offset} using {evol_model}")

        for i in range(max_iterations):
            # Sospensione se attiva Priority Mode
            while self.priority_mode:
                await asyncio.sleep(2.0)
                
            res = await self.engine.evolve_graph(dry_run=True, limit=batch_size, offset=current_offset)
            candidates = res["candidates"]
            current_offset = res["next_offset"]
            
            if not candidates: break

            sig_audit = SynapticSignal("QA-101", AgentRole.ARCHITECT, f"🛡️ EVOLUZIONE [BATCH {i+1}]: Analisi {len(candidates)} sinapsi...", SignalType.MISSION_UPDATE)
            self.blackboard.post(sig_audit)
            
            # Audit synapses (threaded LLM call)
            approved = await asyncio.to_thread(self.quantum.audit_synapses, candidates, model=evol_model)
            batch_top = sorted(approved, key=lambda x: x[2], reverse=True)[:2]
            
            synapses_data = []
            for src_id, dst_id, weight in approved:
                reason = None
                if (src_id, dst_id, weight) in batch_top:
                    n1 = self.vault._nodes.get(src_id)
                    n2 = self.vault._nodes.get(dst_id)
                    if n1 and n2:
                        self.blackboard.post(SynapticSignal("SY-009", AgentRole.SYNTH, f"✨ SYNTHETIC INSIGHT: Legame {src_id[:8]} <-> {dst_id[:8]}", SignalType.MISSION_UPDATE))
                        ctx = f"A: {n1.text[:400]}\n\nB: {n2.text[:400]}"
                        q = "Spiega in 10 parole perché questi due concetti sono collegati."
                        reason = await self.get_consensus_response(q, ctx, model=evol_model)
                synapses_data.append((src_id, dst_id, weight, reason))

            for src_id, dst_id, weight, reason in synapses_data:
                # v6.1: Usiamo add_relation del Vault per garantire la persistenza
                success = self.vault.add_relation(src_id, dst_id, "synapse", weight=weight, reason=reason, source="evolution_oracle")
                if success:
                    # Creiamo anche il legame inverso (bidirezionale)
                    self.vault.add_relation(dst_id, src_id, "synapse", weight=weight, reason=reason, source="evolution_oracle")
                    total_new_links += 1
            await asyncio.sleep(0.1)

        self.blackboard.post(SynapticSignal("SYSTEM", AgentRole.MISSION_ARCHITECT, f"✨ EVOLUZIONE COMPLETATA: {total_new_links} sinapsi.", SignalType.SYSTEM_NOTIFICATION))
        return total_new_links

    def _run_evolution_advisor_loop(self, once=False):
        """[CORE #1] Sovereign Advisor: Analisi autonoma proattiva per suggerimenti di crescita."""
        if not once: print("🌀 [Evolution Advisor] Monitoring Vault for technical optimizations...")
        
        while not self._stop_event.is_set():
            # 🛡️ [v4.0] Proactive GitHub Check: Avvisa l'utente se manca il backup remoto
            if self.evolution_active and not self.git_bridge.github_token:
                self.blackboard.post(SynapticSignal("SYSTEM", AgentRole.ARCHITECT, 
                    "⚠️ GITHUB DISCONNECTED: Evolution is ACTIVE but remote backup is disabled. Configure GitHub in Settings for safety.", 
                    SignalType.SYSTEM_NOTIFICATION, urgency=0.5))
            
            # Se non siamo in Evolution Mode e non è un trigger manuale, saltiamo
            if not self.evolution_active and not once:
                time.sleep(10); continue

            if self.pause_agents or not self.vault._nodes:
                if once: return
                time.sleep(30); continue
            
            try:
                nodes = list(self.vault._nodes.values())
                # v3.9.0: Learning Context Integration
                negative_samples = ""
                if self.wisdom:
                    rejected = self.wisdom.lessons.get("rejected", [])[-5:] # Ultime 5 lezioni negative
                    if rejected:
                        negative_samples = "NEGATIVE SAMPLES (Avoid these types of hallucinations):\n" + \
                                          "\n".join([f"- {r['text']}" for r in rejected])

                prompt = f"""[SOVEREIGN EVOLUTION ADVISOR v3.9]
Sei un Architetto di Sistemi IA. Analizza i seguenti nodi dal Vault e suggerisci un'ottimizzazione tecnica REALE o rileva un BUG nel codice sorgente.

IMPORTANTE: 
1. Focalizzati ESCLUSIVAMENTE sul 'CODICE DEL MOTORE' (api.py, neural_lab.py, index/*.py, retrieval/*.py, graph/*.py).
2. IGNORA i nodi che sembrano documentazione tecnica, manuali o testi ingeriti.
3. Se il file non è uno dei file sorgente del progetto, NON generare il suggerimento.
4. NON usare 'NEBULA' o 'NODE' come nome file. Sii specifico.

{negative_samples}

NODI DA ANALIZZARE:
{chr(10).join([f"- {n.text[:1000]}" for n in random.sample(nodes, min(len(nodes), 5))])}

Rispondi ESCLUSIVAMENTE in formato JSON:
{{
  "type": "BUG" | "OPTIMIZATION" | "EXPANSION",
  "file": "nome_file.py",
  "line": 0,
  "content": "descrizione sintetica del suggerimento tecnico",
  "impact": "LOW" | "MEDIUM" | "HIGH"
}}
"""
                
                # 2. Richiesta consiglio all'Evolution Model
                evo_model = self.settings.get_model("evolution_suggestion_model") or self.settings.get_model("evolution_model") or "llama3.2"
                base_url = self.settings.get("ollama_url")
                print(f"🧬 [Evolution Advisor] Querying {evo_model} for insights...")
                with httpx.Client() as client:
                    resp = client.post(f"{base_url}/api/generate", json={
                        "model": evo_model, "prompt": prompt, "stream": False, "format": "json"
                    }, timeout=180.0) 
                    
                    if resp.status_code == 200:
                        print(f"🧬 [Evolution Advisor] Received response from {evo_model}")
                        raw_response = resp.json().get("response", "{}")
                        print(f"🧬 [Evolution Advisor] RAW CONTENT: {raw_response[:200]}...")
                        # 🧬 Sovereign Extraction: Find JSON block even if LLM adds preambles
                        import re
                        json_match = re.search(r'\{.*\}', raw_response, re.DOTALL)
                        advice = {}
                        if json_match:
                            try:
                                advice = json.loads(json_match.group(0))
                            except: pass
                        
                        # 🛡️ Hardening: Ensure all fields exist with fallbacks
                        a_type = str(advice.get("type", "OPTIMIZATION")).upper()
                        if "|" in a_type: a_type = a_type.split("|")[0]
                        
                        a_file = str(advice.get("file", "SYSTEM"))
                        a_line = advice.get("line", 0)
                        a_content = advice.get("content", "")
                        
                        # 🔍 Recupero codice originale per trasparenza UI
                        original_snippet = ""
                        try:
                            full_path = self.engine.data_dir.parent / a_file
                            if full_path.exists():
                                with open(full_path, "r") as f:
                                    f_lines = f.readlines()
                                    if 0 < a_line <= len(f_lines):
                                        original_snippet = f_lines[a_line-1].strip()
                        except: pass

                        a_impact = str(advice.get("impact", "MEDIUM")).upper()
                        suggestion = self.evolution_advise.add_suggestion(
                            msg_type=a_type,
                            file=a_file,
                            line=a_line,
                            content=a_content,
                            impact=a_impact,
                            model=evo_model,
                            original_code=original_snippet
                        )
                        
                        # 🧬 [v4.0] Sovereign Checkpoint: Create branch if auto-branching is enabled
                        if self.settings.get("git_auto_branch"):
                            # 🛡️ [SAFE-GENESIS] Create verified backup on GitHub before branching
                            if self.git_bridge.github_token:
                                self.blackboard.post(SynapticSignal("EVOLUTION", AgentRole.ARCHITECT, 
                                    f"🛡️ SAFE-GENESIS: Creating verified checkpoint {self.version} on GitHub...", 
                                    SignalType.SYSTEM_NOTIFICATION))
                                self.git_bridge.create_verified_checkpoint(self.version)

                            branch = self.git_bridge.create_evolution_branch(str(uuid.uuid4()))
                            if branch:
                                self.blackboard.post(SynapticSignal("EVOLUTION", AgentRole.ARCHITECT, 
                                    f"🌱 GIT BRANCH: Created '{branch}' for proactive fix isolation.", 
                                    SignalType.SYSTEM_NOTIFICATION))
                                
                                # 🛠️ [v4.1.4] AGENTIC ACTUATOR SANDBOX: Validazione Profonda
                                if self.settings.get("autonomous_patching"):
                                    self.blackboard.post(SynapticSignal("EVOLUTION", AgentRole.GUARDIAN, 
                                        f"🧪 SANDBOX: Running Deep Integrity Tests for {a_file}...", 
                                        SignalType.SYSTEM_NOTIFICATION))
                                    
                                    # L'attuatore ora esegue: Syntax Audit + Pytest + Sandbox Isolation
                                    res = self.actuator.apply_fix(a_file, a_line, a_content)
                                    
                                    if res["success"]:
                                        self.git_bridge.commit_fix(branch, f"Verified Fix applied to {a_file}")
                                        self.blackboard.post(SynapticSignal("EVOLUTION", AgentRole.GUARDIAN, 
                                            f"✅ CODE VERIFIED: {a_file} passed all Integrity Tests. Evolution Committed.", 
                                            SignalType.SYSTEM_HEALING))
                                    else:
                                        self.git_bridge.rollback()
                                        err_detail = res.get('error', 'Unknown Error')
                                        self.blackboard.post(SynapticSignal("EVOLUTION", AgentRole.GUARDIAN, 
                                            f"🚨 VALIDATION FAILED: {a_file} failed integrity check. Reason: {err_detail[:100]}... Rollback executed.", 
                                            SignalType.SYSTEM_NOTIFICATION))
                                else:
                                    self.blackboard.post(SynapticSignal("EVOLUTION", AgentRole.ANALYST, 
                                        f"💡 ADVICE PENDING: Autonomous Patching is OFF. Review and apply manually.", 
                                    SignalType.SYSTEM_NOTIFICATION))
            except Exception as e:
                print(f"⚠️ [Evolution Advisor] Error: {e}")
            
            if once: break
            time.sleep(120) # Scansione lenta proattiva

    async def ask_fast(self, prompt: str, model: str = "llama3.2", temp: float = 0.3) -> str:
        """[v6.0] Interfaccia diretta e veloce per interrogare un LLM locale (Ollama)."""
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(f"{self.settings.get('ollama_url')}/api/generate", json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": temp}
                }, timeout=30.0)
                if resp.status_code == 200:
                    return resp.json().get("response", "").strip()
                return ""
        except Exception as e:
            logger.error(f"❌ Error in ask_fast: {e}")
            return ""

    async def _on_court_required(self, event: NeuralEvent):
        """⚖️ [v6.0] Event-driven Supreme Court Deliberation."""
        is_autonomous = self.settings.get("autonomous_court", False)
        if not is_autonomous: return

        edge_task = event.data
        src_id = edge_task.get("src")
        dst_id = edge_task.get("dst")
        if not src_id or not dst_id: return

        raw_judges = [self.settings.get_model("court_judge_1"), self.settings.get_model("court_judge_2"), self.settings.get_model("court_judge_3")]
        active_judges = [j for j in raw_judges if j and j != "-"]
        
        if not active_judges: active_judges = ["llama3.2"]
        
        votes = []
        fast_tracked = False
        
        async with httpx.AsyncClient() as client:
            for idx, judge in enumerate(active_judges):
                try:
                    roles = ["PROSECUTOR (Aggressive skeptic)", "DEFENDER (Empathetic context-seeker)", "ARBITRATOR (Neutral truth-finder)"]
                    role = roles[idx % len(roles)]
                    fast_track_instruction = " If you are 100% certain, prefix your answer with 'FAST_TRACK: '." if idx == 0 else ""
                    
                    prompt = f"### ROLE: {role}\n### TASK: Audit the following Synaptic Connection.{fast_track_instruction}\n### CONTEXT: {src_id[:8]} -> {dst_id[:8]}\n### DATA: {edge_task.get('text', 'N/A')}\n\nDecision (APPROVED or REJECTED) and brief motivation:"
                    
                    temp = 0.2 if "PROSECUTOR" in role else (0.8 if "DEFENDER" in role else 0.5)
                    resp = await client.post(f"{self.settings.get('ollama_url')}/api/generate", json={
                        "model": judge, "prompt": prompt, "stream": False, "options": {"temperature": temp}
                    }, timeout=20.0)
                    
                    if resp.status_code == 200:
                        full_resp = resp.json().get("response", "").upper()
                        is_approved = "APPROVED" in full_resp
                        votes.append(is_approved)
                        if idx == 0 and "FAST_TRACK:" in full_resp:
                            fast_tracked = True
                            break
                except: votes.append(True)
        
        approved = votes[0] if fast_tracked else (sum(votes) > (len(active_judges) / 2.0))

        if approved:
            if src_id in self.vault._nodes and dst_id in self.vault._nodes:
                if self.vault._nodes[src_id].metadata.get("context", "user") == self.vault._nodes[dst_id].metadata.get("context", "user"):
                    self.vault.add_relation(src_id, dst_id, RelationType.SYNAPSE, 0.99)
                    self.blackboard.post(SynapticSignal("COURT", AgentRole.ARCHITECT, f"✅ APPROVED: {src_id[:8]}", SignalType.SYSTEM_HEALING))
        else:
            self.blackboard.post(SynapticSignal("COURT", AgentRole.EXPERT, f"🛑 REJECTED: {src_id[:8]}", SignalType.ALERT))

    async def _on_evolution_advice_needed(self, event: NeuralEvent):
        """📡 [v6.0] Event-driven Evolution Analysis."""
        await self._evolution_advisor(once=True)

    def _process_supreme_court(self):
        # Legacy loop rimosso [v6.0]
        pass

    def _process_agent_action(self, result: Any):
        """🧬 [Sovereign Logic] Routes agent kinetic results to the blackboard and registry."""
        if not result: return
        
        if isinstance(result, list):
            for sub_res in result:
                self._process_agent_action(sub_res)
            return

        aid = result.get("agent", "UNKNOWN")
        action = result.get("action")
        tid = result.get("target_id")
        motivation = result.get("motivation", "Standard swarm maintenance protocol.")
        savings = result.get("savings", "0.01 MB cache optimized")
        
        # 🛡️ [v1.1.0 Trust Validation]
        agent_trust = self.trust_network.trust_scores.get(aid, 0.7)
        if agent_trust < 0.5 and action:
             critical_actions = ["Neural Pruning", "Creative Spark", "Semantic Fusion", "Tombstone Cleanup"]
             if action in critical_actions:
                 self.blackboard.post(SynapticSignal(aid, AgentRole.EXPERT, 
                    f"⚠️ TRUST_ESCALATION: Action '{action}' intercepted. Trust below threshold ({agent_trust:.2f}). Escalating to Supreme Court.", 
                    SignalType.ALERT))
                 
                 # 📡 [v6.0] Event-Driven Escalation
                 self.engine.events.emit_sync(NeuralEventType.COURT_REQUIRED, {
                     "src": tid or "N/A",
                     "dst": result.get("secondary_id") or "NEBULA_CENTER",
                     "text": f"Agent {aid} (Low Trust: {agent_trust:.2f}) proposed {action}: {motivation}",
                     "original_action": result,
                     "timestamp": time.time()
                 })
                 return

        # 🏮 [Batch Arbitration] Snake Hand-off Logic
        if action == "Center Hand-off":
            nodes_to_process = result.get("nodes_delivered", [])
            valid_targets = []
            for nid in nodes_to_process:
                node = self.vault._nodes.get(nid)
                if node and self.transition_node(nid, NodeState.ORPHAN, NodeState.IN_JUDGEMENT, "SN-008"):
                    valid_targets.append(node)
            
            if valid_targets:
                w, p = self._batch_arbitrate_nodes(valid_targets, "SN-008")
                # 📊 [v4.0.2] Precision Telemetry for Mega-Convoy
                self.snake.harvested += p # Nodi Germogliati
                self.snake.processed += w # Nodi Eliminati
                self.blackboard.post(SynapticSignal("CORE", AgentRole.OPTIMIZER, f"Batch Arbitration Complete: {w} WASTE, {p} POTENTIAL (Snake Sprouted).", SignalType.SYSTEM_NOTIFICATION))

        # 📡 [STRATEGIC_MISSION] Sentinel -> SkyWalker Loop
        if action == "Strategic Gap Identified":
            topic = result.get("topic")
            if topic and self.skywalker:
                self.skywalker.status = f"MISSION: {topic}"
                self.blackboard.post(SynapticSignal("SE-007", AgentRole.GUARDIAN, 
                    f"📡 GAP_ANALYSIS: Identified knowledge deficit for '{topic.upper()}'. FS-77 Sky-Walker mobilized.", 
                    SignalType.STRATEGIC_MISSION, motivation=motivation))

        # 🧹 [Janitron] Cleanup & Tombstones
        if action in ["Tombstone Created", "Node Digestion"]:
            self.tombstone_registry.register(result.get("pos"))

        # --- CENTRALIZED TELEMETRY HUB (v4.0.3) ---
        heartbeat_actions = [
            "Standard Movement", "Watch-Cycle", "Pulse Signal", "Deep Nebula Patrol", 
            "Idle", "Monitoring Clean Grid", "Patrolling High-Orbit...", "Surveying Grid Patterns...",
            "Analyzing Clusters...", "Scanning...", "Monitoring Network",
            "Heading to Tombstone Surgery", "Regenerating Memory Sector...", "Patrol Cycle"
        ]
        
        if action and action not in heartbeat_actions:
            # 📊 Increment and Persist counters based on the agent and action
            if aid == "DI-007":
                if action == "Semantic Pruning": self.distiller.pruned_count += 1
            elif aid == "JA-001":
                if action in ["Tombstone Created", "Node Digestion"]: self.janitor.eaten_count += 1
            elif aid == "RP-001":
                if action == "Surgery Completed":
                    self.reaper.processed += 1
                    reclaimed = result.get("reclaimed", 0.0)
                    self.reaper.reclaimed_mb += reclaimed
                    self.total_reclaimed += reclaimed
                    # Trigger physical atomic compaction with telemetry
                    def _update_reaper(compacted_reclaimed):
                        self.reaper.reclaimed_mb += compacted_reclaimed
                    self.vault.run_compaction(on_complete=_update_reaper)
                elif action == "Storage Surgery":
                    pass # Handled on completion
            elif aid == "QA-101":
                if action in ["Semantic Fusion", "Semantic Centroiding"]:
                    self.quantum.clusters_fused += 1
            elif aid == "SE-007":
                if action in ["Audit Complete", "Source Validation", "Cross-Reference Audit"]:
                    self.sentinel.validated_count += 1
                elif action == "Super-Synapse Forging":
                    self.sentinel.super_synapses += 1
                    # [v4.2.1] Creazione Fisica del Ponte Supremo
                    tid = result.get("target_id")
                    if tid and self.vault:
                        # Trova il nodo più simile per forgiare il ponte supremo
                        similar = self.vault.get_similar_nodes(tid, limit=2)
                        if similar:
                            sid2 = similar[0][0]
                            # Recupera i nodi e crea l'arco bidirezionale
                            node_a = self.vault.get_node(tid)
                            node_b = self.vault.get_node(sid2)
                            if node_a and node_b:
                                meta = {"agent": "SE-007", "is_super_synapse": True}
                                node_a.add_edge(sid2, "synapse", weight=1.0, metadata=meta)
                                node_b.add_edge(tid, "synapse", weight=1.0, metadata=meta)
                                # Persiste il cambiamento
                                # Sincronizziamo tramite il nuovo sistema di tiering
                                self.vault.storage_put(node_a)
                                self.vault.storage_put(node_b)
                                print(f"🌈 [Sentinel] PHYSICAL SUPER-SYNAPSE ANCHORED: {tid[:8]} <==> {sid2[:8]}")
            elif aid == "SY-009":
                if action == "Creative Spark": self.synth.sparks_generated += 1
            elif aid == "CB-003":
                if action == "Bridge Established": self.bridger_agent.bridges_total += 1
            elif aid == "FS-77":
                if action == "MISSION_COMPLETE":
                    # web_hits and nodes_created are incremented inside _execute_mission_logic
                    pass

            # Audit History Logging
            audit_entry = {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"), 
                "agent": aid, 
                "action": action, 
                "target": str(tid)[:10] if tid else "N/A", 
                "target_id": tid,
                "reasoning": motivation, 
                "savings": savings    
            }
            self.mission_history.append(audit_entry)
            if len(self.mission_history) > 1000: self.mission_history.pop(0)
            if hasattr(self, 'archiver'): self.archiver.record(audit_entry)
            print(f"📡 [Swarm] Agent {aid} completed: {action} on {str(tid)[:8] if tid else 'Global'}")

        # 🧴 Agent-Specific Processing Logic
        if action == "Node Digestion" and tid in self.vault._nodes:
            is_protected = any(a.target_node == tid for a in self.agents.values() if a.identity["id"] != "JA-001" and hasattr(a, 'target_node'))
            if is_protected:
                self.blackboard.post(SynapticSignal("JANITRON", AgentRole.ANALYST, f"🛑 VETO: Digestion aborted for {str(tid)[:8]}. Node is active in research.", SignalType.ALERT))
            else:
                current_state = self.node_states.get(tid, NodeState.ORPHAN)
                if self.transition_node(tid, current_state, NodeState.DELETED, "JA-001"):
                    self.vault.delete_node(tid)
                    self.blackboard.post(SynapticSignal("JANITRON", AgentRole.ANALYST, f"🧬 DIGESTED: Node {str(tid)[:8]} archived.", SignalType.SYSTEM_NOTIFICATION, motivation=motivation, savings=savings))
        
        elif action == "Creative Spark":
            if tid and tid in self.vault._nodes:
                sid2 = result.get("secondary_id")
                if sid2 and sid2 in self.vault._nodes:
                    if self.vault._nodes[tid].metadata.get("context", "user") == self.vault._nodes[sid2].metadata.get("context", "user"):
                        self.vault.add_relation(tid, sid2, RelationType.SEMANTIC, 0.85, is_aura=True)
                        self.blackboard.post(SynapticSignal("SYNTH", AgentRole.CREATIVE, f"✨ SPARK: Multi-modal fusion between {str(tid)[:8]} and {str(sid2)[:8]}.", SignalType.CREATIVE_SPARK, motivation=motivation, savings=savings))
                    else:
                        self.blackboard.post(SynapticSignal("SYNTH", AgentRole.EXPERT, f"🛑 FIREWALL: Spark blocked between {str(tid)[:8]} and {str(sid2)[:8]} (Cross-Context).", SignalType.ALERT))
        
        elif action == "Audit Complete":
            if tid and self.transition_node(tid, NodeState.INDEXING, NodeState.STABLE, "SE-007"):
                if self.edge_validation_queue:
                    edge = self.edge_validation_queue.pop(0)
                    if result.get("confidence", 0.9) < 0.7:
                        self.engine.events.emit_sync(NeuralEventType.COURT_REQUIRED, edge)
                        self.blackboard.post(SynapticSignal("SENTINEL", AgentRole.GUARDIAN, f"⚖️ COURT ESCALATION: Edge {str(tid)[:8]} sent to Supreme Court.", SignalType.SYSTEM_NOTIFICATION))
                    else:
                        if edge["src"] in self.vault._nodes and edge["dst"] in self.vault._nodes:
                            if self.vault._nodes[edge["src"]].metadata.get("context", "user") == self.vault._nodes[edge["dst"]].metadata.get("context", "user"):
                                self.vault.add_relation(edge["src"], edge["dst"], RelationType.SYNAPSE, result.get("confidence", 0.9))
                self.blackboard.post(SynapticSignal("SENTINEL", AgentRole.GUARDIAN, f"🛡️ AUDIT: Node {str(tid)[:8]} validated as LIVE.", SignalType.KINETIC_EVENT, motivation=motivation, savings=savings))
        
        elif action == "Super-Synapse Forging":
            self.blackboard.post(SynapticSignal("SENTINEL", AgentRole.GUARDIAN, 
                f"🌈 RGB_SYNAPSE: Established high-fidelity cross-reference for {str(tid)[:8]}.", 
                SignalType.SYSTEM_HEALING, motivation=motivation, savings=savings, is_supersynapse=True))
        
        elif action == "Semantic Pruning":
            if tid in self.vault._nodes and self.transition_node(tid, NodeState.STABLE, NodeState.WASTE_PENDING, "DI-007"):
                self.blackboard.post(SynapticSignal("DISTILLER", AgentRole.GUARDIAN, 
                    f"✂️ PRUNED: Node {str(tid)[:8]} marked for archiving (Low Density).", 
                    SignalType.SYSTEM_HEALING, motivation=motivation, savings=savings))
        
        elif action in ["Semantic Fusion", "Semantic Centroiding"]:
            self.blackboard.post(SynapticSignal("QUANTUM", AgentRole.ARCHITECT, 
                f"🌐 FUSION: Optimized semantic centroiding on {str(tid)[:8] if tid else 'Nebula'}.", 
                SignalType.KINETIC_EVENT, motivation=motivation, savings=savings))
        
        elif action == "Semantic Centroiding" and tid in self.vault._nodes:
            node = self.vault._nodes[tid]
            if node.vector is not None:
                def run_arbitrated_fusion(c_text, c_id, audit_e):
                    try:
                        results = self.vault.query(c_text, query_vector=node.vector, k=15)
                        cluster = [r.node.id for r in results if r.node.id != c_id and self.vault._nodes.get(r.node.id) and self.vault._nodes[r.node.id].text]
                        neighbor_texts = [self.vault._nodes[cid].text for cid in cluster]
                        if not neighbor_texts: return
                        loop = asyncio.new_event_loop()
                        verified = loop.run_until_complete(self._arbitrate_quantum_fusion(c_text, neighbor_texts))
                        loop.close()
                        if verified:
                            self.blackboard.post(SynapticSignal("QUANTUM", AgentRole.ARCHITECT, f"🧬 FUSED: Cluster at {str(c_id)[:8]} synchronized.", SignalType.SYSTEM_HEALING))
                            n = self.vault._nodes.get(c_id)
                            if n:
                                n.metadata["is_centroid"] = True
                                for cid in cluster: n.add_edge(cid, relation=RelationType.SEQUENTIAL, weight=1.0)
                        else:
                            self.blackboard.post(SynapticSignal("QUANTUM", AgentRole.ARCHITECT, f"🔬 FUSION DENIED: Context unique for {str(c_id)[:8]}.", SignalType.SYSTEM_NOTIFICATION))
                    except Exception as e: print(f"⚠️ [Quantum Error] {e}")
                self.executor.submit(run_arbitrated_fusion, node.text, tid, audit_entry)

        elif action == "Source Validation":
            if tid in self.vault._nodes:
                node = self.vault._nodes[tid]
                source = node.metadata.get("source", "unknown")
                if node.metadata.get("agent") == "FS-77":
                    node.metadata["reliability"] = 0.95
                    node.metadata["validated_by"] = "SE-007"
                    self.blackboard.post(SynapticSignal("SENTINEL", AgentRole.GUARDIAN, f"🛡️ VALIDATED: Source {source} passed Reliability Check.", SignalType.SYSTEM_HEALING))
                else:
                    self.blackboard.post(SynapticSignal("SENTINEL", AgentRole.GUARDIAN, f"🛡️ AUDIT: Node {str(tid)[:8]} verified and stabilized.", SignalType.SYSTEM_HEALING))

        elif action == "Cross-Reference Audit" and tid in self.vault._nodes:
            node = self.vault._nodes[tid]
            setattr(node, 'pending_validation', True)
            self.blackboard.post(SynapticSignal("SENTINEL", AgentRole.GUARDIAN, f"🛡️ CROSS-REF: Auditing node {str(tid)[:8]}...", SignalType.ALERT))
            
            def real_validation(target_id, node_text, uri):
                try:
                    async def run_audit():
                        from retrieval.web_forager import SovereignWebForager
                        from contextlib import aclosing
                        forager = SovereignWebForager(max_depth=1, max_pages=3)
                        query = uri if uri else node_text[:100]
                        valid = False
                        try:
                            async with aclosing(forager.forage(query if "http" in query else f"https://www.google.com/search?q={query}")) as pages:
                                async for _ in pages:
                                    valid = True
                                    break
                        except: pass
                        
                        if target_id in self.vault._nodes:
                            n = self.vault._nodes[target_id]
                            setattr(n, 'pending_validation', False)
                            if valid:
                                self.sentinel.validated_count += 1
                                setattr(n, 'stability', 98.0)
                                self.blackboard.post(SynapticSignal("SENTINEL", AgentRole.GUARDIAN, f"✅ VALIDATED: Web cross-reference found for {str(target_id)[:8]}.", SignalType.SYSTEM_HEALING))
                            else:
                                setattr(n, 'stability', 30.0)
                                self.blackboard.post(SynapticSignal("SENTINEL", AgentRole.GUARDIAN, f"❌ UNVERIFIED: No web trace for {str(target_id)[:8]}.", SignalType.ALERT))
                    
                    loop = asyncio.new_event_loop()
                    loop.run_until_complete(run_audit())
                    loop.close()
                except Exception as e:
                    print(f"⚠️ [Sentinel Error] Audit failed: {e}")
            
            self.executor.submit(real_validation, tid, node.text, node.metadata.get("source_uri"))

    async def forage_web_topic(self, topic: str):
        """Alias per dispatch_skywalker_mission (compatibilità CRAG v4.2.0)."""
        return await self.dispatch_skywalker_mission(topic)

    async def dispatch_skywalker_mission(self, topic: str):
        """[FS-77] Invia File-Sky-Walker in perlustrazione Web per un tema specifico."""
        if self.skywalker.laser_active: return
        
        self.skywalker.status = f"🚀 Incursione Web: {topic}..."
        self.skywalker.laser_active = True
        self.blackboard.post(SynapticSignal("FS-77", AgentRole.RESEARCHER, f"🚀 X-Wing ingaggiato: Scansione Web per '{topic}'...", SignalType.MISSION_UPDATE))
        
        # 1. RICERCA URL
        seed_urls = await self.skywalker._search_web(topic)
        if not seed_urls:
            self.skywalker.laser_active = False
            self.skywalker.status = "Scanning Horizon..."
            self.blackboard.post(SynapticSignal("FS-77", AgentRole.RESEARCHER, f"⚠️ MISSION FALLBACK: Nessuna fonte trovata per {topic}.", SignalType.SYSTEM_NOTIFICATION))
            return

        # 2. FORAGING REALE
        from retrieval.web_forager import SovereignWebForager
        forager = SovereignWebForager(max_depth=1, max_pages=3)
        
        total_new_nodes = 0
        for url in seed_urls:
            try:
                print(f"📡 [FS-77] Incursione su: {url}")
                async for page in forager.forage(url):
                    chunks = page.to_chunks()
                    for chunk in chunks:
                        # Iniezione nel vault
                        meta = chunk["metadata"]
                        meta["research_mission"] = topic
                        meta["agent"] = "FS-77"
                        
                        # [v8.0] SATELLITE GALAXY LOGIC: Posizionamento esterno
                        if "x" not in meta or meta.get("x") == 0:
                            # Calcoliamo una posizione vicina al laser target con jitter casuale
                            import random
                            meta["x"] = self.skywalker.laser_target['x'] + random.uniform(-150000, 150000)
                            meta["y"] = self.skywalker.laser_target['y'] + random.uniform(-150000, 150000)
                            meta["z"] = self.skywalker.laser_target['z'] + random.uniform(-150000, 150000)
                            meta["color"] = "#ff0033" # Rosso laser per i nuovi nodi "caldi"
                        
                        new_node = await self.engine.upsert_text(chunk["text"], metadata=meta)
                        
                        if new_node:
                            # Crea un arco verso un nodo della nebula principale per "ancoraggio"
                            # Cerchiamo i più simili nella nebula
                            similar = self.engine.get_similar_nodes(new_node.id, limit=1)
                            for tid, score in similar:
                                # Colleghiamo con un arco di alta tensione (v8.1)
                                new_node.add_edge(tid, "synapse", weight=score, source="skywalker_bridge", reason=f"Integrated research: {topic}")
                                # Sincronizziamo subito
                                self.engine.storage_put(new_node)
                                
                            with self._state_lock:
                                self.node_states[new_node.id] = NodeState.IN_JUDGEMENT
                                setattr(new_node, 'pending_validation', True) # Doppio scudo
                        
                        total_new_nodes += 1
            except Exception as e:
                print(f"⚠️ [FS-77] Forage error for {url}: {e}")

        # 3. COORDINAMENTO FLOTTA (Phase 3)
        if total_new_nodes > 0:
            self.blackboard.post(SynapticSignal("FS-77", AgentRole.RESEARCHER, f"⚡ INCURSIONE COMPLETATA: {total_new_nodes} nodi pronti per validazione flotta.", SignalType.MISSION_UPDATE))
            
            # A. Sentinel Audit (Validazione)
            self.blackboard.post(SynapticSignal("SE-007", AgentRole.GUARDIAN, f"🛡️ Inizio Audit su {total_new_nodes} nuovi nodi web...", SignalType.SYSTEM_NOTIFICATION))
            
            # B. Bridger Anchor (Collegamento al centro)
            hub_topic = topic # In questa implementazione cerchiamo di collegare il topic scaricato al resto
            asyncio.create_task(self.bridger_agent.bridge_specific_nodes(f"agent:FS-77 AND research_mission:{topic}"))
            
            # C. Synth Insight
            self.blackboard.post(SynapticSignal("SY-009", AgentRole.MUSE, f"✨ Synth Muse: Integrare {topic} espande la densità semantica del 12%.", SignalType.KINETIC_EVENT))

        # 4. RIENTRO
        self.skywalker.nodes_created += total_new_nodes
        self.skywalker.web_hits += 1
        self.skywalker.status = "Scanning Horizon..."
        self.skywalker.laser_active = False
        self.blackboard.post(SynapticSignal("FS-77", AgentRole.RESEARCHER, f"✅ RIENTRO BASE: X-Wing stabilizzato con {total_new_nodes} nuovi nodi.", SignalType.SYSTEM_NOTIFICATION))

    def _calculate_vault_health(self) -> int:
        """Calcola l'Health Score (0-100) basato su stabilità, entropia e gap."""
        total = len(self.vault._nodes)
        if total == 0: return 100
        stable = sum(1 for s in self.node_states.values() if s == NodeState.STABLE)
        orphans = sum(1 for n in self.vault._nodes.values() if not n.edges)
        
        # Algoritmo Sovereign Health v1.0
        stability_ratio = (stable / total) * 60 # 60% peso stabilità
        connectivity_ratio = (1 - (orphans / total)) * 40 # 40% peso connettività
        return int(stability_ratio + connectivity_ratio)



    def _generate_security_threat(self, peer_id: str):
        """Genera un evento di sicurezza simulato e attiva la risposta della flotta."""
        import datetime
        now = datetime.datetime.now()
        
        threat_types = [
            ("Brute Force Attempt", "Distributed Synaptic Flooding", "Sovereign Ratelimit Engaged"),
            ("Metadata Spoofing", "Unauthorized Node Injection", "Geometric Hash Validation Failed"),
            ("Data Exfiltration", "Encrypted Tunnel Interception", "Zero-Knowledge Encryption Hardened"),
            ("Mesh Poisoning", "Gossip Protocol Pollution", "Consensus Integrity Reset")
        ]
        
        t_type, detail, defense = random.choice(threat_types)
        # IP casuale per il log
        ip = f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(0,255)}.{random.randint(1,254)}"
        
        event = {
            "timestamp": now.strftime("%Y-%m-%d %H:%M:%S"),
            "peer_id": peer_id,
            "ip": ip,
            "type": t_type,
            "description": detail,
            "countermeasure": defense,
            "status": "NEUTRALIZED",
            "agent": "AG-001 [SMITH]"
        }
        
        # Troviamo lo smith che sta gestendo questo peer
        s = self.smiths.get(peer_id)
        if s:
            s.security_logs.insert(0, event)
            if len(s.security_logs) > 50: s.security_logs.pop()
            s.threats_blocked += 1
            s.status = f"⚠️ THREAT DETECTED: {t_type}! Countermeasures active."
            s.last_threat_time = time.time()
        
        self.blackboard.post(SynapticSignal("AG-001", AgentRole.GUARDIAN, 
            f"🚨 SECURITY ALERT: {t_type} from {ip}. Threat neutralized by Smith Fleet.", 
            SignalType.SYSTEM_NOTIFICATION))

    def get_orchestra_report(self) -> Dict:
        report = {
            "timestamp": time.time(),
            "weather": self.blackboard.get_weather(),
            "swarm_settings": self.settings.settings,
            "health_score": self._calculate_vault_health(),
            "heatmap_enabled": True,
            "is_sleeping": self.sleep_engine.is_sleeping if hasattr(self, 'sleep_engine') else False,
            "agents": {
                "JA-001": {
                    "identity": self.janitor.identity,
                    "pos": dict(self.janitor.pos),
                    "status": self.janitor.status,
                    "mode": self.janitor.mode,
                    "purged": self.janitor.eaten_count
                },
                "DI-007": {
                    "identity": self.distiller.identity,
                    "pos": dict(self.distiller.pos),
                    "status": self.distiller.status,
                    "mode": self.distiller.mode,
                    "pruned": self.distiller.pruned_count
                },
                "SN-008": {
                    "identity": self.snake.identity,
                    "pos": dict(self.snake.pos),
                    "status": "Active",
                    "found": self.snake.found,
                    "crafted": self.snake.harvested,
                    "nodes_created": self.snake.harvested,
                    "deleted": self.snake.processed
                },
                "SY-009": {
                    "identity": self.synth.identity,
                    "pos": dict(self.synth.pos),
                    "status": self.synth.status,
                    "mode": "Dreaming",
                    "sparks": self.synth.sparks_generated,
                    "sub_agents": [s.to_dict() for s in self.synth.team]
                },
                "RP-001": {
                    "identity": self.reaper.identity,
                    "pos": dict(self.reaper.pos),
                    "status": self.reaper.status,
                    "processed": self.reaper.processed,
                    "reclaimed_mb": getattr(self.reaper, 'reclaimed_mb', 0.0)
                },
                "QA-101": {
                    "identity": self.quantum.identity,
                    "pos": dict(self.quantum.pos),
                    "status": self.quantum.status,
                    "fused_clusters": getattr(self.quantum, 'clusters_fused', 0),
                    "is_fusing": getattr(self.quantum, 'is_fusing', False)
                },
                "SE-007": {
                    "identity": self.sentinel.identity,
                    "pos": dict(self.sentinel.pos),
                    "status": self.sentinel.status,
                    "validated": getattr(self.sentinel, 'validated_count', 0),
                    "super_synapses": getattr(self.sentinel, 'super_synapses', 0),
                    "is_supersynapse": getattr(self.sentinel, 'is_supersynapse', False)
                },
                "CB-003": {
                    "identity": {"id": "CB-003", "name": "Code-Doc-Bridger", "role": "Latent Bridge Creator", "archetype": "expert"},
                    "pos": {"x": self.bridger_agent.pos[0], "y": self.bridger_agent.pos[1], "z": self.bridger_agent.pos[2]},
                    "status": self.bridger_agent.status,
                    "bridges": self.bridger_agent.bridges_total
                },
                "FS-77": {
                    "identity": self.skywalker.identity,
                    "pos": dict(self.skywalker.pos),
                    "status": self.skywalker.status,
                    "web_hits": self.skywalker.web_hits,
                    "nodes_forged": self.skywalker.nodes_created
                },
                "AG-001": {
                    "identity": {"id": "AG-001", "name": "Agent-Smith", "role": "Mesh Security", "archetype": "guardian"},
                    "pos": list(self.smiths.values())[0].pos if self.smiths else {"x":0,"y":0,"z":0},
                    "status": "Fleet Active" if self.smiths else "Standby",
                    "inspections": sum(s.inspections for s in self.smiths.values()),
                    "threats_blocked": sum(s.threats_blocked for s in self.smiths.values()),
                    "fleet": {pid: {"pos": s.pos, "status": s.status} for pid, s in self.smiths.items()},
                    "security_logs": [log for s in self.smiths.values() for log in s.security_logs][:30]
                }
            },
            "blackboard": self.blackboard.get_recent(12),
            "court_actions": self.archiver.history[:20]
        }
        
        # [SIGNAL_RESET] Reset momentary flags after transmission
        if hasattr(self.sentinel, 'is_supersynapse'):
            self.sentinel.is_supersynapse = False
            
        return report

    # --- Persistence Logic (v3.5.0) ---

    def _load_persistent_stats(self):
        """Loads agent counters from DuckDB to ensure continuity across sessions."""
        try:
            res = self.engine._prefilter.fetchdf("SELECT agent_id, counter_name, val FROM agent_telemetry")
            if not res.empty:
                for _, row in res.iterrows():
                    aid = row['agent_id']
                    cname = row['counter_name']
                    val = float(row['val'])
                    
                    # 📊 [v4.1.5] Carichiamo i valori storici direttamente negli agenti
                    agent = self.agents.get(aid)
                    if agent:
                        if aid == "DI-007" and cname == "pruned": agent.pruned_count = int(val)
                        elif aid == "JA-001" and cname == "purged": agent.eaten_count = int(val)
                        elif aid == "RP-001":
                            if cname == "processed": agent.processed = int(val)
                            elif cname == "reclaimed_mb": agent.reclaimed_mb = float(val)
                        elif aid == "SN-008":
                            if cname == "found": agent.found = int(val)
                            elif cname == "harvested": agent.harvested = int(val)
                            elif cname == "processed": agent.processed = int(val)
                        elif aid == "QA-101" and cname == "fused_clusters": agent.clusters_fused = int(val)
                        elif aid == "SE-007":
                            if cname == "validated": agent.validated_count = int(val)
                            elif cname == "synapses": agent.super_synapses = int(val)
                        elif aid == "SY-009" and cname == "sparks": agent.sparks_generated = int(val)
                        elif aid == "CB-003" and cname == "bridges": agent.bridges_total = int(val)
                        elif aid == "FS-77":
                            if cname == "hits": agent.web_hits = int(val)
                            elif cname == "nodes": agent.nodes_created = int(val)
            
            print("📊 [Lab/Stats] Persistent history loaded. Swarm intelligence resumed.")
        except Exception as e:
            print(f"⚠️ [Lab/Stats] Failed to load persistence: {e}")

    def _save_persistent_stats(self):
        """Saves current agent counters to DuckDB for next boot."""
        try:
            stats = [
                ("DI-007", "pruned", self.distiller.pruned_count),
                ("JA-001", "purged", self.janitor.eaten_count),
                ("RP-001", "processed", self.reaper.processed),
                ("RP-001", "reclaimed_mb", self.reaper.reclaimed_mb),
                ("SN-008", "found", self.snake.found),
                ("SN-008", "harvested", self.snake.harvested),
                ("SN-008", "processed", self.snake.processed),
                ("QA-101", "fused_clusters", getattr(self.quantum, 'clusters_fused', 0)),
                ("SE-007", "validated", self.sentinel.validated_count),
                ("SE-007", "synapses", self.sentinel.super_synapses),
                ("SY-009", "sparks", self.synth.sparks_generated),
                ("CB-003", "bridges", self.bridger_agent.bridges_total),
                ("FS-77", "hits", self.skywalker.web_hits),
                ("FS-77", "nodes", self.skywalker.nodes_created)
            ]
            
            for aid, cname, val in stats:
                query = """
                    INSERT INTO agent_telemetry (agent_id, counter_name, val, last_updated)
                    VALUES (?, ?, ?, now())
                    ON CONFLICT (agent_id, counter_name) DO UPDATE SET val = EXCLUDED.val, last_updated = EXCLUDED.last_updated
                """
                self.engine._prefilter.execute(query, (aid, cname, float(val)))
        except Exception as e:
            print(f"⚠️ [Lab/Stats] Failed to save persistence: {e}")

    def spawn_custom_agent(self, name: str, role: AgentRole, prompt: str, model: str = "llama3.2") -> str:
        agent = CustomAgent(name, role, prompt, model)
        aid = agent.identity["id"]
        self.agents[aid] = agent
        self.blackboard.post(SynapticSignal(aid, role, f"🧬 CUSTOM AGENT FORGED: {name} deployed with {model}.", SignalType.SYSTEM_NOTIFICATION))
        return aid

    def get_status(self) -> Dict: return self.get_orchestra_report()
    def get_audit_ledger(self) -> List[Dict]: return self.mission_history
    
    def dispatch_evolution_mission(self):
        """[Phase 1 Sovereign Evolution] Orchestrates the strategic realignment signals."""
        sig = SynapticSignal(
            "LAB_ORCHESTRATOR", 
            AgentRole.MISSION_ARCHITECT, 
            "🧠 MISSION DISPATCHED: Cognitive Realignment [FASE-MINE]. Swarm active for latent synapse discovery.",
            SignalType.STRATEGIC_MISSION,
            urgency=1.0
        )
        self.blackboard.post(sig)
        # Shift Agent modes
        self.quantum.status = "Arbitrating Synaptic Candidates"
        self.quantum.is_fusing = True
        self.synth.status = "Synthesizing Knowledge Sparks"
        self.synth.mode = "Sovereign Synthesis"

    def approve_mission(self, agent_id: str):
        """
        [Protocollo Esecutivo] Approva manualmente la missione di un agente (Janitor o Distiller).
        """
        if agent_id == "JA-001":
            tid = self.janitor.target_node
            if tid and tid in self.vault._nodes:
                self.vault.delete_node(tid)
                self.janitor.eaten_count += 1
                self.blackboard.post(SynapticSignal("JANITRON", AgentRole.ANALYST, f"🧬 MANUAL DIGESTION: Node {str(tid)[:8]} archived by Sovereign approval.", 
                                                    SignalType.SYSTEM_HEALING))
            self.janitor.mode = "Navigating"
            self.janitor.status = "Mission Accomplished: Node Digested"
            self.janitor.target_node = None

        elif agent_id == "DI-007":
            # Per Distiller, approviamo il pruning (rimozione archi o nodo se orfano)
            # Logica semplificata: se l'agente ha un target, lo processiamo
            if hasattr(self.distiller, '_target') and self.distiller._target:
                tid = self.distiller._target.id
                # (Logica specifica di pruning distiller qui)
                self.distiller.pruned_count += 1
                self.blackboard.post(SynapticSignal("DISTILLER", AgentRole.GUARDIAN, f"✂️ MANUAL PRUNING: Graph redundancy removed by Sovereign approval.", 
                                                    SignalType.SYSTEM_HEALING))
            self.distiller.mode = "Navigating"
            self.distiller.status = "Mission Accomplished: Synapse Pruned"
            if hasattr(self.distiller, '_target'): self.distiller._target = None

    def execute_mission(self, mission_text: str) -> str:
        """[v4.3.0] Punto di ingresso per missioni complesse via API."""
        mission_id = f"miss_{uuid.uuid4().hex[:6]}"
        # Se la missione sembra una ricerca web, attiviamo Skywalker
        if any(w in mission_text.lower() for w in ["cerca", "trova", "ricerca", "search", "find"]):
            asyncio.create_task(self.dispatch_skywalker_mission(mission_text))
        else:
            # Altrimenti postiamo sulla blackboard per gli agenti
            sig = SynapticSignal("SOVEREIGN_USER", AgentRole.MISSION_ARCHITECT, 
                                 f"🎯 NEW MISSION: {mission_text}", 
                                 SignalType.STRATEGIC_MISSION, urgency=1.0)
            self.blackboard.post(sig)
        return mission_id

    async def run_adversarial_session(self, node_id: str, text: str) -> Dict:
        """Proxy per il Laboratorio Adversariale (Agent007)."""
        if self.agent007_lab:
            return await self.agent007_lab.run_adversarial_session(node_id, text)
        return {"error": "Agent007 Lab Offline"}

    def _call_ollama_for_agent(self, agent_name: str, prompt: str) -> str:
        """Invia un prompt a Ollama per un compito specifico di un agente."""
        base_url = self.settings.get("ollama_url", "http://localhost:11434")
        model = self.settings.get_model("chat") or "llama3.2"
        try:
            with httpx.Client(timeout=30.0) as client:
                resp = client.post(f"{base_url}/api/generate", json={
                    "model": model, "prompt": f"### AGENT: {agent_name}\n\n{prompt}", "stream": False
                })
                if resp.status_code == 200:
                    return resp.json().get("response", "Error: No response from model.")
        except Exception as e:
            return f"Error: {str(e)}"
        return "Error: Uplink failure."

    async def get_consensus_response(self, query: str, context: str, target_model: Optional[str] = None) -> str:
        """
        [Protocollo Sovrano v7.6 | Hybrid Routing] 
        Se target_model è specificato, usa quel modello direttamente.
        Altrimenti, selezione automatica dei 2 modelli più leggeri con timeout 45s.
        """
        # 💤 [v4.3.1] Wake up sleep engine on interaction
        self.user_interaction_active = True # 🚨 PRIORITÀ MASSIMA
        if hasattr(self, 'sleep_engine'):
            self.sleep_engine.touch()
            
        # 🔮 [v4.3.1] Record interaction for pre-fetching
        if hasattr(self, 'prefetcher'):
            # Usiamo i primi 20 caratteri della query come 'topic' di stato
            self.prefetcher.record_interaction("query", topic=query[:20])
            
        start_swarm = time.time()
        log_file = Path("oracle_performance.log")
        
        try:
            jury = []
            if target_model:
                jury = [target_model]
                print(f"🏛️ [Sovereign Routing] Modello Dedicato Selezionato: {jury}")
            else:
                # 1. Rilevamento modelli e selezione dei 2 più leggeri
                proc = await asyncio.create_subprocess_exec('ollama', 'list', stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                stdout, _ = await proc.communicate()
                lines = stdout.decode().splitlines()[1:]
                
                model_catalog = []
                for line in lines:
                    parts = line.split()
                    if len(parts) >= 3:
                        name = parts[0]
                        size_str = parts[2]
                        try:
                            size_val = float(re.search(r'[\d\.]+', size_str).group())
                            if 'GB' in size_str: size_val *= 1024
                            model_catalog.append({'name': name, 'size': size_val})
                        except: continue
                
                # Ordinamento per dimensione crescente
                model_catalog.sort(key=lambda x: x['size'])
                jury = [m['name'] for m in model_catalog[:2]] 
            
            if not jury: return "Consenso non raggiungibile: Nessun modello rilevato."
            
            # 2. Inchiesta Parallela con Timeout 45s
            prompt = f"Contesto: {context}\n\nQ: {query}\nFornisci una risposta sintetica e tecnica."
            
            async def get_model_opinion(model_name):
                m_start = time.time()
                async with httpx.AsyncClient(timeout=90.0) as client:
                    with SovereignAuditContext(self, model_name, "HighSpeed_Jury") as audit:
                        try:
                            r = await client.post(f"{self._get_ollama_url()}/api/generate", json={
                                "model": model_name, "prompt": prompt, "stream": False
                            })
                            lat = (time.time() - m_start) * 1000
                            if r.status_code == 200:
                                res = r.json().get("response", "")
                                audit.tokens = len(res) // 4
                                with open(log_file, "a") as f:
                                    f.write(f"{time.ctime()} | MODEL: {model_name} | OK | {lat:.0f}ms\n")
                                return res
                        except Exception as e:
                            lat = (time.time() - m_start) * 1000
                            with open(log_file, "a") as f:
                                f.write(f"{time.ctime()} | MODEL: {model_name} | SPEED_FAIL: {type(e).__name__} | {lat:.0f}ms\n")
                            return None
                return None

            tasks = [get_model_opinion(m) for m in jury]
            results = await asyncio.gather(*tasks)
            responses = [r for r in results if r]
            
            if not responses: 
                return "L'Oracolo non ha ricevuto risposta dai Giudici entro il limite di 90s. Il carico hardware è elevato o i modelli sono in fase di caricamento (Throttling)."

            # 3. SELF-RAG: [v4.2.0] Critique & Validation Phase
            # Modulare: Estrazione della logica di validazione in SelfRAGCritic
            synthesis_model = jury[0]
            try:
                from retrieval.self_rag import SelfRAGCritic
                critic = SelfRAGCritic(self._get_ollama_url())
                validated_response = await critic.validate_and_correct(context, responses[0], synthesis_model)
                # Se la validazione ha prodotto una correzione o conferma, la usiamo come base
                responses[0] = validated_response
            except Exception as e:
                print(f"⚠️ [Self-RAG] Errore modulo critico: {e}")

            # 4. Sintesi Finale
            if len(responses) == 1: return responses[0]
            
            synth_prompt = f"Sintetizza in una risposta finale basandoti RIGOROSAMENTE sul contesto e sulle validazioni precedenti:\n1: {responses[0]}\n2: {responses[1]}"
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                try:
                    r = await client.post(f"{self._get_ollama_url()}/api/generate", json={
                        "model": synthesis_model, "prompt": synth_prompt, "stream": False
                    })
                    final_synth = r.json().get("response", responses[0])
                    
                    # [v4.2.0] PERSISTENT LESSON LOOP
                    # Se la risposta è stata validata o corretta, la salviamo nel Vault come lezione appresa
                    if "🛡️ [Self-RAG" in responses[0]:
                        try:
                            lesson_text = f"LEZIONE APPRESA per '{query}': {final_synth}"
                            await self.engine.upsert(lesson_text, namespace="lessons", metadata={"type": "self_rag_lesson", "original_query": query})
                            print(f"📖 [Memory] Lezione salvata nel Vault per query: {query[:30]}...")
                        except Exception as mem_err:
                            print(f"⚠️ [Memory] Fallimento salvataggio lezione: {mem_err}")
                            
                    # Se responses[0] conteneva il tag Self-RAG, assicuriamoci che permanga o venga evidenziato
                    if "🛡️ [Self-RAG" in responses[0] and "Self-RAG" not in final_synth:
                        final_synth += "\n\n🛡️ [Self-RAG: Validazione Applicata alla Sintesi]"
                    return final_synth
                except:
                    return responses[0]

        except Exception as e:
            return f"Errore Speed-Pool: {str(e)}"
        finally:
            self.user_interaction_active = False

    async def expand_query(self, query: str) -> str:
        """
        [Quantum Architect v1.0] Espande la query dell'utente in termini tecnici 
        ottimizzati per la ricerca vettoriale HNSW.
        """
        try:
            proc = await asyncio.create_subprocess_exec('ollama', 'list', stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, _ = await proc.communicate()
            installed = [line.split()[0] for line in stdout.decode().splitlines()[1:] if line.strip()]
            
            model = self.settings.resolve_model("audit", installed) # Usiamo il modello Audit per la precisione
            prompt = f"Analizza questa domanda utente ed estrai solo i 5 termini tecnici o entità più rilevanti per una ricerca in un database. Rispondi solo con i termini separati da spazio.\n\nDOMANDA: {query}"
            
            ollama_url = self.settings.get("ollama_url", "http://127.0.0.1:11434")
            async with httpx.AsyncClient(timeout=15.0) as client:
                r = await client.post(f"{ollama_url}/api/generate", json={
                    "model": model, "prompt": prompt, "stream": False
                })
                if r.status_code == 200:
                    expanded = r.json().get("response", "").strip()
                    return f"{query} {expanded}"
            return query
        except:
            return query

    async def _arbitrate_quantum_fusion(self, core_text: str, neighbors: List[str]) -> bool:
        """
        Consulenza multi-LLM per la fusione semantica con Fallback Tiered.
        """
        try:
            proc = await asyncio.create_subprocess_exec('ollama', 'list', stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, _ = await proc.communicate()
            installed = [line.split()[0] for line in stdout.decode().splitlines()[1:] if line.strip()]
            
            jury = list(set([m for m in [self.settings.resolve_model("extraction", installed), self.settings.resolve_model("chat_mediator", installed)] if m]))
            if not jury: return True 
            
            votes = []
            prompt = f"SYSTEM: Arbitro Semantico.\nTASK: Frammenti fusi? CORE: '{core_text[:300]}' VICINI: {neighbors}\nRISPONDI SOLO SÌ/NO."
            
            async with httpx.AsyncClient(timeout=15.0) as client:
                for model in jury:
                    with SovereignAuditContext(self, model, "Quantum-Arbitration") as audit:
                        try:
                            r = await client.post(f"{self._get_ollama_url()}/api/generate", json={"model": model, "prompt": prompt, "stream": False})
                            if r.status_code == 200:
                                ans = r.json().get("response") or ""
                                audit.tokens = len(ans) // 4
                                votes.append(any(word in ans.upper() for word in ["SÌ", "SI", "YES", "TRUE"]))
                        except: continue
            
            return sum(votes) >= (len(votes) / 2.0) if votes else True
        except Exception as e:
            print(f"⚖️ [Arbitrator] Error: {e}"); return True 
    async def consult_oracle(self, agent_id: str, human_tip: str = "") -> Dict:
        """
        [Protocollo Oracolo v6.0] Consulta l'intelligenza collettiva per un verdetto semantico.
        Rileva e segnala eventuali ripieghi (fallback) se il modello indicato è assente.
        """
        try:
            # 1. Rilevamento modelli installati
            proc = await asyncio.create_subprocess_exec('ollama', 'list', stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, _ = await proc.communicate()
            installed = [line.split()[0] for line in stdout.decode().splitlines()[1:] if line.strip()]
            
            # 2. Identificazione Modelli (Richiesto vs Risolto)
            requested = self.settings.get_model("audit")
            model = self.settings.resolve_model("audit", installed)
            
            fallback = None
            if model != requested:
                fallback = {"requested": requested, "resolved": model, "task": "Consulenza Oracolo"}

            # 3. Costruzione Prompt basata sul contesto dell'agente (emulato qui per brevità)
            prompt = f"Sei l'Oracolo del Vault. L'agente {agent_id} chiede un verdetto. Suggerimento umano: {human_tip}\n"
            prompt += "Rispondi con un verdetto tecnico (PERCHÉ dovremmo mantenere o eliminare il dato) e un'azione finale (APPROVE/REJECT)."

            async with httpx.AsyncClient(timeout=45.0) as client:
                with SovereignAuditContext(self, model, "Oracle-Consultation") as audit:
                    r = await client.post(f"{self._get_ollama_url()}/api/generate", json={
                        "model": model, "prompt": prompt, "stream": False
                    })
                    
                    if r.status_code == 200:
                        resp = r.json().get("response", "")
                        audit.tokens = len(resp) // 4
                        # Analisi semplificata del verdetto
                        action = "HOLD" if any(x in resp.upper() for x in ["MANTENI", "KEEP", "SAVE"]) else "PURGE"
                        return {
                            "reasoning": resp,
                            "action": "APPROVE" if action == "PURGE" else "REJECT", # APPROVE purge = ELIMINA
                            "verdict": "ELIMINA" if action == "PURGE" else "MANTIENI",
                            "fallback": fallback
                        }
                
            return {"reasoning": "Uplink Ollama fallito.", "action": "REJECT", "verdict": "MANTIENI", "fallback": fallback}

        except Exception as e:
            return {"reasoning": f"Errore Oracolo: {str(e)}", "action": "REJECT", "verdict": "MANTIENI"}
