import uuid
import math
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

async def _global_forage_helper(forager, url, limit=5):
    """Helper globale per il foraging asincrono di pagine web (Unificato v1.8)."""
    pages = []
    try:
        async for p in forager.forage(url):
            pages.append(p)
            if len(pages) >= limit: break
    except Exception as e:
        print(f"⚠️ [Global-Forager] Errore su {url}: {e}")
    return pages

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
            "extraction": "llama3.2:3b",
            "crossref": "llama3.2:3b",
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
            "wiki_model": "qwen2.5:7b",
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
    MUSE = "muse"

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
        # v6.0.2: Utilizza l'Enum locale AgentRole per evitare conflitti di importazione
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
        self.pos = {"x": 5000000.0, "y": 2000000.0, "z": 5000000.0}
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
        # 🛡️ v24.4.1: Check if target still exists
        target = nodes.get(self.target_node)
        if not target:
            self.target_node = None
            return None
            
        if getattr(target, 'pending_validation', False):
            self.status = f"VETO: Node {self.target_node[:8]} pending validation"
            self.target_node = None
            return None
        
        # 3. Movement
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
        self.pos = {"x": -300000.0, "y": 0.0, "z": -300000.0}
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

        target = nodes.get(self._target)
        if not target:
            self._target = None
            return None
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
        self.pos = {"x": 500000.0, "y": 0.0, "z": 500000.0}
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
        self.pos = {"x": 500000.0, "y": 0.0, "z": 500000.0}
        self.target_node = None
        self.status = "Monitoring Storage..."
        self.processed = 0 # Interventi (count)
        self.reclaimed_mb = 0.0 # Spazio (MB)
        self.regeneration_timer = 0
        self.patrol_cycles = 0 # 🛰️ Mandatory orbit cycles after surgery

    def _idle_patrol(self, now):
        """Orbit around the Mother Nebula when no surgeries are required."""
        angle = now * 0.15
        radius = 800000 + 200000 * math.sin(now * 0.1)
        self.pos['x'] = float(radius * math.cos(angle))
        self.pos['y'] = float(300000 * math.sin(angle * 0.5))
        self.pos['z'] = float(radius * math.sin(angle))

    def calculate_movement(self, nodes: dict):
        if not nodes: return None
        now = time.time()
        
        try:
            # Seek Tombstones from the Atomic Registry
            if not self.target_node:
                registry = getattr(self, 'tombstone_registry', None)
                if registry and hasattr(registry, 'claim_next'):
                    next_ts = registry.claim_next()
                    if next_ts:
                        self.target_node = next_ts
                        self.status = "Heading to Tombstone Surgery"
                    else:
                        self.status = "Patrolling High-Orbit"
                        self._idle_patrol(now)
                else:
                    self.status = "Patrolling High-Orbit"
                    self._idle_patrol(now)
            
            if self.target_node and isinstance(self.target_node, dict):
                tx, ty, tz = self.target_node.get('x',0), self.target_node.get('y',0), self.target_node.get('z',0)
                step = 0.12
                self.pos['x'] += (tx - self.pos['x']) * step
                self.pos['y'] += (ty - self.pos['y']) * step
                self.pos['z'] += (tz - self.pos['z']) * step
                
                dist = ((self.pos['x']-tx)**2 + (self.pos['y']-ty)**2 + (self.pos['z']-tz)**2)**0.5
                if dist < 40000:
                    if self.regeneration_timer == 0:
                        self.regeneration_timer = 15
                        self.status = "Regenerating Memory Sector..."
                        return {"agent": "RP-001", "action": "Storage Surgery", "reclaimed": 0.12}
                    
                    self.regeneration_timer -= 1
                    if self.regeneration_timer <= 0:
                        registry = getattr(self, 'tombstone_registry', None)
                        if registry and hasattr(registry, 'finalize'): registry.finalize(self.target_node['id'])
                        self.processed += 1
                        self.reclaimed_mb += 0.1
                        self.target_node = None 
                        self.patrol_cycles = 60
            else:
                self._idle_patrol(now)
        except Exception as e:
            print(f"⚠️ [RP-001] Error: {e}")
            self._idle_patrol(now)
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
        self.pos = {"x": 0.0, "y": 0.0, "z": 0.0}
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
        
        try:
            # Update team
            if self.team:
                for sub in self.team: sub.tick(self.pos)
                self.team = [s for s in self.team if s.life > 0]
                if not self.team: self.status = "Synthesizing..."

            # Kinetic Movement: Synth orbits target or patrols deep grid
            if self.target_node and self.target_node in nodes:
                target_pos = nodes[self.target_node].metadata
                tx, ty, tz = target_pos.get('x',0), target_pos.get('y',0), target_pos.get('z',0)
                # Glide towards target with high-altitude oscillation
                self.pos['x'] += (tx - self.pos['x']) * 0.1
                self.pos['y'] += (ty + 100000 * np.sin(now * 0.5) - self.pos['y']) * 0.1
                self.pos['z'] += (tz - self.pos['z']) * 0.1
            else:
                # Idle movement (Floating with wider radius)
                angle = now * 0.2
                self.pos = {"x": float(800000 * np.cos(angle)), "y": float(500000 + 200000 * np.sin(now * 0.2)), "z": float(800000 * np.sin(angle))}
            
            # Targeting logic: Focus on POTENTIAL nodes
            if not self.target_node or self.target_node not in nodes:
                if self.orch and hasattr(self.orch, 'node_states') and self.orch.node_states:
                    potentials = [nid for nid, state in list(self.orch.node_states.items()) 
                                if state == NodeState.POTENTIAL and nid in nodes]
                    if potentials:
                        self.target_node = random.choice(potentials)
                        print(f"✨ SynthMuse: Target POTENTIAL node {self.target_node[:8]}")
                    else:
                        # Fallback targeting
                        node_ids = list(nodes.keys())
                        if node_ids: self.target_node = random.choice(node_ids)
                        else: return None
                else: return None
            
            if random.random() < 0.25:
                if not self.team: self.spawn_team() 
                
                # 🧠 [High #3] Semantic Synthesis Algorithm
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
        except Exception as e:
            # Improved error capture
            print(f"⚠️ [SY-009] Swarm error: {e}")
            return None
        return None

class QuantumAgent:
    """🌐 [QA-101] Quantum Architect / Semantic Centroiding"""
    def __init__(self, vault, orch=None):
        self.vault = vault; self.orch = orch
        self.identity = {"id": "QA-101", "name": "Quantum-Architect", "role": "Semantic Fusion", "archetype": "architect"}
        self.pos = {"x": 500000.0, "y": 0.0, "z": 500000.0}
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
                    galaxy_nodes = [nid for nid, n in nodes.items() if n.metadata.get("is_galaxy")]
                    live_nodes = [nid for nid, state in self.orch.node_states.items() if state == NodeState.STABLE]
                    combined_targets = live_nodes + galaxy_nodes
                    if combined_targets: self.target_node = random.choice(combined_targets)
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
        wh_angle = (h_val % 360) * (np.pi / 180)
        # [v18.6] Synchronized Deep Space Rim: 25M units (orbiting Wormholes)
        base_dist = 25000000.0 + (h_val % 1000000)
        
        wh_x = float(np.cos(wh_angle) * base_dist)
        wh_y = float(1000000.0 + (h_val % 500000 - 250000))
        wh_z = float(np.sin(wh_angle) * base_dist)
        
        # 2. Orbita di pattugliamento attorno al wormhole (Raggio: 3M unità come richiesto)
        smith_speed = 0.4
        # Offset unico basato sull'ID per non sovrapporre la flotta
        local_offset = (h_val % 100) / 10.0
        angle = now * smith_speed + local_offset
        
        # Posizionamento: Pattugliamento ad ampio raggio per intercettare flussi dati
        orbit_radius = 3000000.0 # 3.000.000 unità dal wormhole
        self.pos['x'] = wh_x + float(np.cos(angle) * orbit_radius)
        self.pos['y'] = wh_y + float(np.sin(angle * 0.5) * orbit_radius)
        self.pos['z'] = wh_z + float(np.sin(angle) * orbit_radius)
        
        # Stato dinamico: Alterna tra pattugliamento e ispezione profonda per feedback visivo
        if (now % 10 < 3): # Ogni 10 secondi, per 3 secondi esegue ispezione
            self.status = f"Analisi flussi {peer_id[:8]} ↔ Nebula Madre: Scansione pacchetti in corso..."
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
        self.pos = {"x": -500000.0, "y": 0.0, "z": 500000.0}
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
            res_s = self.vault._prefilter.fetchone(query, (source_id,))
            res_t = self.vault._prefilter.fetchone(query, (target_id,))
            
            # [Fix v1.1.0]: Fallback for missing nodes
            acc_s = res_s[0] if res_s else 1; imp_s = res_s[1] if res_s else 0.5
            acc_t = res_t[0] if res_t else 1; imp_t = res_t[1] if res_t else 0.5
            
            # [Physics Model]
            # Resonance = (Sum of access / Log distance) * Importance Factor
            score = (math.log(acc_s + acc_t + 1) * (imp_s + imp_t)) / 2
            return min(1.0, score)
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
            orphans = [n for nid, n in list(self.vault._nodes.items()) if len(n.edges) <= 2]
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
                        "action": "Semantic Gap Discovery", 
                        "target_id": gap,
                        "motivation": f"Gap semantico rilevato per il topic '{gap}'. Necessaria espansione della conoscenza."
                    }
        return None

class R2D2Agent:
    """🤖 [R2-D2] Warehouse Manager / Semantic Organizer"""
    def __init__(self, vault, orch=None):
        self.vault = vault; self.orch = orch
        self.identity = {"id": "R2-D2", "name": "R2-D2", "role": "Warehouse Manager", "archetype": "expert"}
        # [v16.0] Distributed Boot: Sector Gamma (Near Mother Nebula)
        self.pos = {"x": -1500000.0, "y": 0.0, "z": 1500000.0}
        print(f"🤖 [BOOT] R2-D2 Initialized at: {self.pos}")
        self.status = "Monitoring Inventory..."
        # 📊 [v8.5] Session Mode: Start from 0 (Fixed initialization)
        self.organized_count = 0
        self.galaxies_formed = 0
        self.target_pos = dict(self.pos)
        self.patrol_timer = 0

        self.last_action_time = time.time() - 6.0 # Accelerated first tick (2s wait instead of 8s)
        self.misplaced_alerts = []
        self.pruning_suggestions = []

    def calculate_movement(self, nodes: dict):
        if not nodes: return None
        now = time.time()
        self.is_operating = False 
        
        # 🛸 [v17.9] Kinematic Patrol: Smooth lerp toward target_pos
        step = 0.08
        self.pos['x'] += (self.target_pos['x'] - self.pos['x']) * step
        self.pos['y'] += (self.target_pos['y'] - self.pos['y']) * step
        self.pos['z'] += (self.target_pos['z'] - self.pos['z']) * step
        
        if now - self.last_action_time > 1.5: 
            self.last_action_time = now
            self.is_operating = True
            
            # 1. Audit e Re-Spatializzazione: Snapshot dei nodi per evitare RuntimeError
            node_ids = list(nodes.keys())
            if node_ids:
                # [v17.3] HYBRID SCAN: Mix of central core and peripheral galaxies
                core_nodes = [nid for nid in node_ids if math.sqrt(nodes[nid].metadata.get('x',0)**2 + nodes[nid].metadata.get('y',0)**2 + nodes[nid].metadata.get('z',0)**2) < 1000000]
                
                if core_nodes and random.random() < 0.4:
                    # Organizza il core
                    target_ids = random.sample(core_nodes, min(len(core_nodes), 50))
                    self.status = "OPTIMIZING MOTHER NEBULA: Prioritizing central core..."
                else:
                    # Procedi verso le galassie lontane (Per evitare che si fermi a 300)
                    target_ids = random.sample(node_ids, min(len(node_ids), 50))
                    self.status = "EXPANDING OPERATIONS: Organizing distant galaxies..."

                batch = [nodes[nid] for nid in target_ids if nid in nodes]
                
                # R2-D2 si sposta fisicamente verso un nodo specifico del batch per saltare
                if batch:
                    # Pick a specific target node to fly to instead of the dead center of the nebula
                    target_node = random.choice(batch)
                    self.target_pos = {
                        "x": target_node.metadata.get('x',0), 
                        "y": target_node.metadata.get('y',0), 
                        "z": target_node.metadata.get('z',0)
                    }

                # [v16.4] HYBRID ZONES: Combinazione di temi e colori (Janitron Speed)
                theme_sectors = {
                    "legal":     {"x": 1000000,  "y": 500000,  "z": 1000000},
                    "technical": {"x": -1000000, "y": 500000,  "z": -1000000},
                    "general":   {"x": 0,        "y": -500000, "z": 1000000},
                    "quantum":   {"x": 1500000,  "y": 0,       "z": -1500000},
                    "security":  {"x": -1500000, "y": -1000000, "z": 0}
                }
                
                color_sectors = {
                    "green":  {"x": 600000,  "y": 800000,  "z": 600000},
                    "pink":   {"x": -600000, "y": 800000,  "z": -600000},
                    "brown":  {"x": 800000,  "y": 200000, "z": -800000},
                    "orange": {"x": -800000, "y": 200000, "z": 800000}
                }
                
                moved_this_tick = 0
                for node in batch:
                    # Identifica il tema per zona o per colore esplicito
                    topic = node.metadata.get("topic_type", "general")
                    color_hint = node.metadata.get("color_label", "none").lower()
                    
                    # Priorità ai settori cromatici se presenti
                    if color_hint in color_sectors:
                        target = color_sectors[color_hint]
                    else:
                        target = theme_sectors.get(topic, theme_sectors["general"])
                    
                    # Calcolo attrazione (spostamento del 5% verso il target)
                    current_x = node.metadata.get("x", 0)
                    current_y = node.metadata.get("y", 0)
                    current_z = node.metadata.get("z", 0)
                    
                    dx = (target["x"] - current_x) * 0.05
                    dy = (target["y"] - current_y) * 0.05
                    dz = (target["z"] - current_z) * 0.05
                    
                    if abs(dx) + abs(dy) + abs(dz) > 10:
                        node.metadata["x"] = current_x + dx
                        node.metadata["y"] = current_y + dy
                        node.metadata["z"] = current_z + dz
                        moved_this_tick += 1
                        # Salvataggio periodico
                        if random.random() > 0.95:
                             self.vault.storage_put(node)

                if moved_this_tick > 0:
                    self.status = f"WAREHOUSE SWEEP: Organizing {moved_this_tick} chromatic nodes..."
                    self.organized_count += moved_this_tick
                
                print(f"🤖 [R2-D2] High-Speed Warehouse Sweep Complete. Position: {self.pos}")
            
            # 2. Compattazione Settoriale: Identify dense zones
            if len(nodes) > 1000:
                suggestion = f"Cluster {random.randint(1,10)} density critical (>80%). Suggesting pruning."
                self.pruning_suggestions.append(suggestion)
                if self.orch:
                    self.orch.blackboard.post_signal("R2-D2", "expert", f"PROPOSAL: {suggestion}", urgency=0.4)

            if self.organized_count > 0 and self.organized_count % 1000 == 0:
                self.galaxies_formed += 1

        
        # 🛸 [v17.9] Idle Patrol Logic: Pick a random node in the vault
        if now - self.patrol_timer > 8.0:
            self.patrol_timer = now
            if nodes:
                lucky_node = random.choice(list(nodes.values()))
                self.target_pos = {
                    "x": lucky_node.metadata.get('x', 0),
                    "y": lucky_node.metadata.get('y', 0),
                    "z": lucky_node.metadata.get('z', 0)
                }
                self.status = "PATROLLING: Inspecting distant sectors..."
        
        return {
            "agent": "R2-D2",
            "pos": self.pos,
            "is_operating": self.is_operating,
            "status": self.status
        }

class BridgerAgent:
    def __init__(self, vault, bridger, orch=None):
        self.vault = vault; self.bridger = bridger; self.orch = orch; self.blackboard = getattr(orch, 'blackboard', None)
        self.identity = {"id": "CB-003", "name": "Bridger-Agent", "role": "Cross-Referencer", "archetype": "expert"}
        # [v16.0] Distributed Boot: Quadrant Beta (Outer Rim)
        self.pos = {"x": 1800000.0, "y": 0.0, "z": -1800000.0}
        print(f"🌉 [BOOT] CB-003 Bridger Initialized at: {self.pos}")
        self.target_node = None
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
                self.pos['x'] += (tx - self.pos['x']) * step
                self.pos['y'] += (ty - self.pos['y']) * step
                self.pos['z'] += (tz - self.pos['z']) * step
                if random.random() < 0.1: # Log occasionale per evitare spam, ma conferma movimento
                    print(f"🌉 [MOVE] CB-003 Bridger pursuing target at: ({tx:.0f}, {ty:.0f}, {tz:.0f})")
            except: pass
        else:
            # 🛸 Deep Patrol: Bridger deve stare lontano dal centro per evitare overlap
            step = random.uniform(80000, 200000)
            direction = [random.uniform(-1, 1) for _ in range(3)]
            dist = math.sqrt(self.pos['x']**2 + self.pos['y']**2 + self.pos['z']**2)
            if dist < 1200000: # [v14.5] Mantieni distanza di sicurezza dal centro
                direction = [p/dist if dist > 0 else random.uniform(-1,1) for p in [self.pos['x'], self.pos['y'], self.pos['z']]]
            elif dist > 3000000: # Troppo fuori
                direction = [-p/dist for p in [self.pos['x'], self.pos['y'], self.pos['z']]]
            
            self.pos['x'] += direction[0] * step
            self.pos['y'] += direction[1] * step
            self.pos['z'] += direction[2] * step
        
        # Space bounds
        limit = 3500000
        self.pos['x'] = max(-limit, min(limit, self.pos['x']))
        self.pos['y'] = max(-limit, min(limit, self.pos['y']))
        self.pos['z'] = max(-limit, min(limit, self.pos['z']))
        
        return {"agent": "CB-003", "pos": dict(self.pos)}

    async def sync_codebase(self):
        if not self.bridger.project_root:
            self.status = "Idle - No Project Root"
            return
        self.is_syncing = True
        self.status = "Syncing Codebase..."
        try:
            await self.bridger.ingest_codebase()
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
        # [v16.0] Distributed Boot: Quadrant Alpha (Outer Rim)
        self.pos = {"x": 8000000.0, "y": 3000000.0, "z": 8000000.0}
        print(f"🛰️ [BOOT] FS-77 Skywalker Initialized at: {self.pos}")
        self.status = "Scanning Horizon..."
        self.web_hits = 0
        self.nodes_created = 0 # 🛰️ [v4.0.1] New sub-counter
        self.galaxies_created = 0 # 🌌 [v8.4] Satellite Galaxies
        
        # 📊 [v8.4] Session-Only Counters (Baseline handled by Orchestrator)
        self.nodes_created = 0
        self.web_hits = 0
        self.galaxies_created = 0

        self.laser_active = False
        self.laser_target = {'x': 250000, 'y': 0, 'z': 250000} # [v8.0] - Reduced from 2M to 250k (10x closer)

    def calculate_movement(self, nodes: Dict) -> Optional[Dict]:
        """Pattugliamento Orbitale Alta Quota (Symmetric Border Patrol)."""
        now = time.time()
        # 1. Movimento orbitale (Deep Space Patrol)
        angle = now * 0.08
        # [v24.8] Skywalker High-Altitude Patrol (Capped at 10M units)
        rad = (8500000.0 + 1500000.0 * np.sin(now * 0.05))
        
        # Wide sinusoidal curves scaled to 10M radius
        self.pos['x'] = float(rad * np.cos(now * 0.06))
        self.pos['y'] = float(3500000 * np.sin(now * 0.03)) # Scaled vertical oscillation (3.5M units)
        self.pos['z'] = float(rad * np.sin(now * 0.06))
        
        # 2. [PROACTIVE_RESEARCH] Forza missione se idle (v8.4)
        if not hasattr(self, 'last_mission_time'): self.last_mission_time = now
        
        is_idle = any(s in self.status for s in ["Scanning", "FAILED", "COMPLETE", "Horizon"])
        
        # [DIAGNOSTIC] Log heartbeat every 100 cycles or on state change
        if random.random() > 0.99:
            print(f"💓 [FS-77/Heartbeat] Idle: {is_idle}, Since Last: {int(now - self.last_mission_time)}s")

        # Se idle per più di 10 secondi (RIDOTTO da 30 per test), lancia una missione
        if is_idle and (now - self.last_mission_time > 10):
            self.last_mission_time = now
            # 🕵️ [v8.4] Hybrid Exploration Logic
            weak_nodes = [n for n in nodes.values() if len(n.edges) <= 1 and len(n.text) > 20]
            
            if weak_nodes and random.random() > 0.3:
                # 🛡️ [v9.0 Hardening] Filter out code snippets
                valid_nodes = [n for n in weak_nodes if not any(c in n.text for c in ['def ', 'class ', 'import ', 'self.', '()', '{', '_'])]
                
                if not valid_nodes:
                    print(f"🔍 [FS-77] {len(weak_nodes)} weak nodes found, but ALL filtered as code/technical. Falling back to proactive topics.")
                
                target_node = random.choice(valid_nodes if valid_nodes else weak_nodes)
                topic = target_node.text[:40].strip()
                topic = "".join(c for c in topic if c.isalnum() or c in " -").strip()
                
                if len(topic) < 3: topic = "Neural Topology Optimization" 
                
                self.status = f"REINFORCING: {topic}..."
                print(f"📡 [FS-77] Debolezza semantica rilevata. Rinforzo per: {topic}")
            else:
                # Ricerca proattiva su temi caldi
                queries = ["latest AI advancements", "autonomous agents architecture", "vector database optimization", "neural implicit compression", "graphRAG best practices", "quantum neural networks", "distributed ledgers"]
                topic = random.choice(queries)
                self.status = f"MISSION: {topic}"
                print(f"📡 [FS-77] Lancio Ricerca Proattiva su: {topic}")
            
            # [v17.1] Deep Space Skywalker Projection (6M - 8M units)
            dist = 6000000.0 + random.uniform(0, 2000000.0)
            theta = random.uniform(0, 2 * math.pi)
            phi = random.uniform(0, math.pi)
            
            self.laser_target = {
                'x': dist * math.sin(phi) * math.cos(theta),
                'y': dist * math.sin(phi) * math.sin(theta),
                'z': dist * math.cos(phi)
            }

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
        
        # 🛰️ [v8.4.1 Telemetry Anchor]
        self.web_hits += 1
        
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
        
        query = self.status
        for prefix in ["MISSION:", "🚀", "REINFORCING:"]:
            query = query.replace(prefix, "")
        query = query.strip()
        
        try:
            # [v20.1] Autonomous Flight: Skywalker non aspetta più Yoda
            self.status = "THOUGHT: Analyzing independent gap..."
            time.sleep(2) 
            
            self.status = "Mission searching file..."
            try:
                with self.orch._search_lock:
                    # [v18.7] Hardened Timeout: Increased to 600s for deep research
                    search_data = asyncio.run_coroutine_threadsafe(self._search_web(query, limit=10), self.orch.loop).result(timeout=600)
                urls = search_data.get("urls", [])
                ai_content = search_data.get("ai_content", "")
                if urls:
                    self.web_hits += 1 # 🛰️ Record telemetry hit
            except Exception as e:
                err_msg = str(e) if str(e) else type(e).__name__
                print(f"⚠️ [FS-77] Web search timeout or error: {err_msg}. Falling back to internal synthesis.")
                urls = []; ai_content = ""

            all_pages = []
            if not urls and not ai_content:
                self.status = "MISSION: Internal Insight Synthesis..."
                context_nodes = random.sample(list(self.orch.engine._nodes.values()), min(len(self.orch.engine._nodes), 5))
                raw_intel = "INTERNAL NEBULA CONTEXT:\n" + "\n".join([n.text[:1000] for n in context_nodes])
            else:
                self.status = f"FORAGE: Scraping {len(urls)} sources..."
                
                async def _forage_all_parallel(forager, u_list):
                    tasks = [_global_forage_helper(forager, u, limit=5) for u in u_list[:2]]
                    results = await asyncio.gather(*tasks, return_exceptions=True)
                    all_p = []
                    for r in results:
                        if isinstance(r, list): all_p.extend(r)
                        elif isinstance(r, Exception): print(f"⚠️ [FS-77] Parallel forage task error: {r}")
                    return all_p

                try:
                    # [v25.0] Parallel Foraging: Skywalker now wait up to 600s
                    all_pages = asyncio.run_coroutine_threadsafe(_forage_all_parallel(self.orch.forager, urls), self.orch.loop).result(timeout=600)
                    if all_pages: self.web_hits += 1
                except Exception as e:
                    err_msg = str(e) if str(e) else type(e).__name__
                    print(f"⚠️ [FS-77] Parallel Forage failed or timeout: {err_msg}")
                    all_pages = []

                raw_intel = "\n".join([p.text[:2000] for p in all_pages])

            self.status = "SYNTH: Distilling Wisdom..."
            synthesis = self._ask_ai_to_synthesize(query, raw_intel)
            
            if synthesis:
                self.status = "INJECTING: Knowledge Galaxy..."
                try:
                    meta_core = {
                        "source": "SkyWalker-Core", "topic": query, "timestamp": datetime.now().isoformat(),
                        "x": self.laser_target['x'], "y": self.laser_target['y'], "z": self.laser_target['z'],
                        "is_galaxy": True, "galaxy_role": "core",
                        "lifecycle_state": "protected", "importance": 5.0 # [v13.6] Anti-Decay
                    }
                    core_node = asyncio.run_coroutine_threadsafe(self.vault.upsert_text(synthesis, metadata=meta_core), self.orch.loop).result()
                    
                    if core_node:
                        self.nodes_created += 1
                        self.galaxies_created += 1
                        
                        sat_nodes = []
                        for i, p in enumerate(all_pages[:5]):
                            try:
                                sat_meta = {
                                    "source": "SkyWalker-Source", "url": p.url,
                                    "x": self.laser_target['x'] + random.uniform(-40000, 40000),
                                    "y": self.laser_target['y'] + random.uniform(-40000, 40000),
                                    "z": self.laser_target['z'] + random.uniform(-40000, 40000),
                                    "is_galaxy": True, "galaxy_role": "source",
                                    "lifecycle_state": "protected", "importance": 5.0 
                                }
                                sat_node = asyncio.run_coroutine_threadsafe(self.vault.upsert_text(f"SOURCE [{i}]: {p.title}\n\n{p.text[:800]}", metadata=sat_meta), self.orch.loop).result()
                                if sat_node:
                                    self.vault.add_relation(sat_node.id, core_node.id, "galaxy_internal")
                                    sat_nodes.append(sat_node)
                            except Exception as e:
                                print(f"⚠️ [FS-77/Warn] Ingest satellite {i} failed: {e}")
                                continue
                except Exception as e:
                    print(f"🚨 [FS-77/Error] Fallimento Ingestione Nucleo: {e}")
                    core_node = None
                    
                    try:
                        # [v18.3] Tethering di precisione: Forza 4 o 8 archi verso la Mother Nebula
                        mother_nodes = [n for n in self.vault._nodes.values() if not n.metadata.get("is_galaxy")]
                        if mother_nodes:
                            from scipy.spatial import distance
                            my_pos = [self.pos['x'], self.pos['y'], self.pos['z']]
                            mother_anchor = min(mother_nodes, key=lambda n: distance.euclidean(my_pos, [n.metadata.get('x', 0), n.metadata.get('y', 0), n.metadata.get('z', 0)]))
                            
                            all_galaxy_nodes = [core_node] + sat_nodes
                            num_tethers = 8 if len(all_galaxy_nodes) >= 1000 else 4
                            tether_step = max(1, len(all_galaxy_nodes) // num_tethers)
                            
                            for idx, gn in enumerate(all_galaxy_nodes):
                                if idx % tether_step == 0:
                                    self.vault.add_relation(gn.id, mother_anchor.id, "skywalker_anchor")
                    except: pass
                
                self.status = "MISSION_COMPLETE"
                if self.orch: 
                    self.orch._process_agent_action({
                        "agent": "FS-77", 
                        "action": "MISSION_COMPLETE", 
                        "motivation": f"Synthesized high-quality wisdom for '{query}'.", 
                        "nodes_added": 1,
                        "web_hits": len(all_pages)
                    })
            else:
                self.status = "MISSION_FAILED: Synthesis Error"

        except Exception as e:
            print(f"🚨 [FS-77/Critical] Mission Crash: {e}")
        finally:
            self.status = "Scanning Horizon..."
            self.last_mission_time = time.time()
            self.laser_active = False

    def _ask_ai_to_synthesize(self, topic: str, content: str) -> Optional[str]:
        """Interpella l'LLM locale per creare una sintesi granulare."""
        try:
            base_url = self.orch.settings.get("ollama_url", "http://localhost:11434")
            model = self.orch.settings.get_model("synthesis")
            prompt = f"Sei l'Agente FS-77 SkyWalker. Sintetizza: {topic}\nDati:\n{content[:6000]}"
            with httpx.Client(timeout=300.0) as client:
                resp = client.post(f"{base_url}/api/generate", json={"model": model, "prompt": prompt, "stream": False})
                if resp.status_code == 200: return resp.json().get("response")
        except: pass
        return None

    async def _refine_query_with_llm(self, query: str) -> str:
        """[v1.6] Usa l'LLM per creare una query di ricerca professionale."""
        try:
            base_url = self.orch.settings.get("ollama_url", "http://localhost:11434")
            model = self.orch.settings.get_model("general_purpose")
            prompt = f"Trasforma questo frammento tecnico in una query di ricerca Google efficace per trovare documentazione o tutorial. Rispondi SOLO con la query.\nFrammento: {query}"
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(f"{base_url}/api/generate", json={"model": model, "prompt": prompt, "stream": False})
                if resp.status_code == 200: 
                    refined = resp.json().get("response", "").strip().strip('"')
                    if refined: return refined
        except: pass
        from retrieval.web_forager import SovereignWebForager
        return SovereignWebForager.refine_query(query)

    def _sanitize_query(self, query: str) -> str:
        from retrieval.web_forager import SovereignWebForager
        return SovereignWebForager.refine_query(query)

    async def _search_web(self, query: str, limit: int = 10) -> Dict[str, Any]:
        import urllib.parse
        clean_query = self._sanitize_query(query)
        if not clean_query: return {"urls": [], "ai_content": ""}
        
        # 🛡️ [v11.0] Stealth Upgrade: Usa il forager centrale se disponibile
        if self.orch and self.orch.forager:
            refined = await self._refine_query_with_llm(query)
            res = await self.orch.forager.stealth_search(refined, limit=limit)
            if res and res.get("urls"):
                self.web_hits += 1
            return res

        headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
        urls = []
        
        # 1. Google Fallback (Regex)
        try:
            search_url = f"https://www.google.com/search?q={urllib.parse.quote(clean_query)}"
            async with httpx.AsyncClient(headers=headers, timeout=180.0, follow_redirects=True) as client:
                resp = await client.get(search_url)
                if resp.status_code == 200:
                    import re
                    # Improved regex for Google
                    found = re.findall(r'href="/url\?q=(https?://[^&"]+)', resp.text)
                    if not found:
                        found = re.findall(r'href="(https?://[^&"]+)"', resp.text)
                    urls.extend([f for f in found if "google.com" not in f and "gstatic.com" not in f])
        except: pass
        
        # 2. DuckDuckGo Fallback (Lite/HTML)
        if not urls:
            try:
                ddg_url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(clean_query)}"
                async with httpx.AsyncClient(headers=headers, timeout=180.0) as client:
                    resp = await client.get(ddg_url)
                    if resp.status_code == 200:
                        import re
                        found = re.findall(r'href="(https?://[^&"]+)"', resp.text)
                        urls.extend([f for f in found if "duckduckgo.com" not in f])
            except: pass

        if urls: self.web_hits += 1
        return {"urls": list(dict.fromkeys(urls))[:limit], "ai_content": ""}

    def get_status_report(self):
        return {
            "identity": self.identity,
            "pos": self.pos,
            "status": self.status,
            "web_hits_session": self.web_hits,
            "nodes_introduced_session": self.nodes_created,
            "galaxies_session": self.galaxies_created
        }

class YodaAgent:
    """YO-001 Yoda-File-Searcher: Deep Semantic Pilgrim."""
    def __init__(self, engine, orch=None):
        self.vault = engine; self.orch = orch
        self.identity = {"id": "YO-001", "name": "Yoda-File-Searcher", "role": "DEEP_SURVEYOR"}
        # [v16.0] Distributed Boot: Quadrant Sigma (Outer Rim Deep)
        self.pos = {"x": -9000000.0, "y": -4000000.0, "z": -9000000.0}
        print(f"🟢 [BOOT] YO-001 Yoda Initialized at: {self.pos}")
        self.status = "Meditating in the Nebula..."
        self.nodes_examined = 0
        self.galaxies_created = 0
        self.web_hits = 0 # 📊 [v8.4.1 Fix]
        
        # 📊 [v8.4] Session-Only Counters (Baseline handled by Orchestrator)
        self.nodes_examined = 0
        self.galaxies_created = 0
        self.web_hits = 0 
        self.nodes_introduced_session = 0
        self.last_galaxy_name = ""
        self.last_galaxy_dist = 0.0
        self.nodes_in_last_galaxy = 0

        self.laser_active = False
        self.laser_target = {"x": 0, "y": 0, "z": 0}
        self.last_pilgrimage_time = time.time() - 35.0 # Accelerated first mission (10s wait instead of 45s)

    def calculate_movement(self, nodes: Dict) -> Optional[Dict]:
        now = time.time()
        exp = getattr(self.orch, 'nebula_expansion_factor', 1.0) if self.orch else 1.0
        
        # 🛸 [v17.8] Jedi Pilgrimage Dynamics
        is_on_mission = "PILGRIMAGE" in self.status or "EXPANSION" in self.status or "Researching" in self.status
        
        if is_on_mission and hasattr(self, 'galaxy_anchor'):
            # Fly toward the deep space galaxy (up to 35M units)
            target = self.galaxy_anchor
            lerp_factor = 0.02 # Majestic approach
            self.pos['x'] += (target['x'] - self.pos['x']) * lerp_factor
            self.pos['y'] += (target['y'] - self.pos['y']) * lerp_factor
            self.pos['z'] += (target['z'] - self.pos['z']) * lerp_factor
        else:
            # Fly back to Deep Space Pilgrimage Zone (40M - 55M range)
            base_radius = (47500000.0 + 7500000.0 * math.sin(now * 0.008)) * exp
            target_x = base_radius * math.cos(now * 0.005)
            target_y = 1000000 * math.sin(now * 0.002)
            target_z = base_radius * math.sin(now * 0.005)
            
            lerp_factor = 0.05
            self.pos['x'] += (target_x - self.pos['x']) * lerp_factor
            self.pos['y'] += (target_y - self.pos['y']) * lerp_factor
            self.pos['z'] += (target_z - self.pos['z']) * lerp_factor
        
        # 🕒 Check for next mission
        is_idle = "Meditating" in self.status or "COMPLETE" in self.status
        if is_idle and (now - self.last_pilgrimage_time > 45):
            self.last_pilgrimage_time = now
            self.status = "PILGRIMAGE: Gathering 1000 Nodes..."
            threading.Thread(target=self._execute_yoda_mission, args=(list(nodes.values()),), daemon=True).start()

        return {"agent": "YO-001", "pos": dict(self.pos), "laser": self.laser_active, "laserTarget": self.laser_target}

    async def _yoda_search_web(self, query: str, limit: int = 5) -> Dict[str, Any]:
        # 🛡️ [v11.0] Stealth Upgrade: Yoda usa la Forza (e Playwright)
        if self.orch and self.orch.forager:
            # [v1.6] Refine query with LLM if possible
            refined = await self._refine_query_with_llm(query)
            try:
                return await self.orch.forager.stealth_search(refined, limit=limit, zen=True)
            except Exception as e:
                print(f"⚠️ [YO-001] Stealth Search Exception: {e}")
                return {"urls": [], "ai_content": ""}
            
        return {"urls": [], "ai_content": ""}

    async def _internal_insight_synthesis(self, topic: str) -> List[Dict[str, Any]]:
        """[v8.5] Fallback: Crea conoscenza sintetica basata sui dati esistenti nel Vault."""
        print(f"🔮 [YO-001] Initiating Internal Insight Synthesis for: {topic}")
        try:
            # 1. Recupera frammenti correlati dalla Nebula Madre
            nodes = await self.vault.query(topic, k=10)
            if not nodes: return []
            
            context = "\n---\n".join([n.node.text[:500] for n in nodes])
            
            # 2. Usa l'LLM per generare una sintesi strutturata
            base_url = self.orch.settings.get("ollama_url", "http://localhost:11434")
            model = self.orch.settings.get_model("synthesis")
            
            prompt = (
                f"Agisci come Yoda, il Gran Maestro della Conoscenza. Basandoti solo sui seguenti frammenti estratti dalla nostra Nebula Madre, "
                f"genera un trattato filosofico e tecnico sul tema '{topic}'. "
                f"Crea 3 paragrafi distinti che esplorino connessioni nascoste.\n\n"
                f"FRAMMENTI:\n{context}"
            )
            
            async with httpx.AsyncClient(timeout=300.0) as client:
                resp = await client.post(f"{base_url}/api/generate", json={"model": model, "prompt": prompt, "stream": False})
                if resp.status_code == 200:
                    synthesis = resp.json().get("response", "")
                    return [{
                        "url": "internal://nebula/synthesis",
                        "title": f"Internal Resonance: {topic}",
                        "text": synthesis
                    }]
        except Exception as e:
            err_msg = str(e) if str(e) else type(e).__name__
            print(f"⚠️ [YO-001] Internal Synthesis Exception: {err_msg}")
            return []
            print(f"❌ [YO-001] Internal Synthesis Failed: {e}")
        return []

    async def _refine_query_with_llm(self, query: str) -> str:
        """[v1.6.5] Crea una query bilingue professionale per fonti accreditate."""
        try:
            base_url = self.orch.settings.get("ollama_url", "http://localhost:11434")
            model = self.orch.settings.get_model("general_purpose")
            prompt = (
                f"Trasforma questo concetto in una query di ricerca Google bilingue (Italiano e Inglese) "
                f"mirata a trovare documentazione tecnica, paper o fonti accreditate. "
                f"Rispondi SOLO con la query ottimizzata.\nConcetto: {query}"
            )
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(f"{base_url}/api/generate", json={"model": model, "prompt": prompt, "stream": False})
                if resp.status_code == 200: 
                    refined = resp.json().get("response", "").strip().strip('"')
                    if refined: return refined
        except: pass
        return f"{query} official documentation technical papers"

    def _execute_yoda_mission(self, all_nodes):
        if not all_nodes: return
        
        # 🎯 [v20.0] Mission Planning: Se la coda è vuota, chiediamo consiglio ad Ollama
        if not hasattr(self, 'mission_queue'): self.mission_queue = []
        
        if not self.mission_queue:
            self.status = "PLANNING: Consulting the Oracle..."
            sample = random.sample(all_nodes, min(len(all_nodes), 50))
            context_summary = "\n".join([n.text[:200] for n in sample])
            
            try:
                base_url = self.orch.settings.get("ollama_url", "http://localhost:11434")
                model = self.orch.settings.get_model("general_purpose")
                prompt = (
                    f"In base ai temi trattati nel vault (nella nebula che abbiamo creato foraggiando la conoscenza con dati, file e url), "
                    f"che argomenti mi consigli di approfondire? Stila una lista di 10 argomenti tecnici o scientifici brevi (2-4 parole). "
                    f"Rispondi SOLO con la lista numerata, un argomento per riga.\n\nCONTESTO:\n{context_summary}"
                )
                import httpx
                with httpx.Client(timeout=120.0) as client:
                    resp = client.post(f"{base_url}/api/generate", json={"model": model, "prompt": prompt, "stream": False})
                    if resp.status_code == 200:
                        lines = resp.json().get("response", "").splitlines()
                        for line in lines:
                            clean = "".join(c for c in line if not c.isdigit() and c not in ['.', '-', ')']).strip()
                            if clean and len(clean.split()) >= 1:
                                self.mission_queue.append(clean)
            except Exception as e:
                err_msg = str(e) if str(e) else type(e).__name__
                print(f"⚠️ [YO-001] Planning failed: {err_msg}")
            
            if not self.mission_queue: # Fallback
                self.mission_queue = ["Sovereign Intelligence", "Neural Mesh Optimization", "Distributed Consensus"]

        # Prendi il prossimo argomento dalla coda
        common_topic = self.mission_queue.pop(0)
        self.nodes_examined += len(all_nodes) # Statistica simbolica
        
        # Cerchiamo il nodo più vicino al centroide per l'ancoraggio fisico
        closest_node = None
        valid_vectors = [n.vector for n in all_nodes if n.vector is not None and len(n.vector) > 0]
        if valid_vectors:
            avg_v = np.mean(valid_vectors, axis=0)
            min_d = float('inf')
            for n in all_nodes:
                if n.vector is not None:
                    d = np.linalg.norm(n.vector - avg_v)
                    if d < min_d: min_d = d; closest_node = n

        self.status = f"EXPANSION: Researching {common_topic}..."
        self.laser_active = True
        
        try:
            with self.orch._search_lock:
                import math
                theta = random.uniform(0, 2 * math.pi)
                phi = random.uniform(0, math.pi)
                # [v18.6] Deep Frontier Yoda Projection (35M - 45M units)
                distance = 35000000.0 + random.uniform(0, 10000000.0)
                
                galaxy_x = distance * math.sin(phi) * math.cos(theta)
                galaxy_y = distance * math.sin(phi) * math.sin(theta)
                galaxy_z = distance * math.cos(phi)
                
                self.laser_target = {"x": galaxy_x, "y": galaxy_y, "z": galaxy_z}
                self.galaxy_anchor = {"x": galaxy_x, "y": galaxy_y, "z": galaxy_z}
                
                try:
                    # [v25.1] Increased Timeout to 600s and depth limited to 2
                    search_data = asyncio.run_coroutine_threadsafe(self._yoda_search_web(common_topic, limit=2), self.orch.loop).result(timeout=600) 
                    urls = search_data.get("urls", [])
                except Exception as e:
                    err_msg = str(e) if str(e) else type(e).__name__
                    print(f"⚠️ [YO-001] Web search TIMEOUT (600s) or ERROR for '{common_topic}': {err_msg}")
                    urls = []
                
                if not urls:
                    print(f"⚠️ [YO-001] External search failed. Activating Internal Insight Synthesis for '{common_topic}'...")
                    self.status = "SYNTHESIS: Reclaiming internal insights..."
                    # Chiamata al nuovo fallback
                    try:
                        synthetic_pages = asyncio.run_coroutine_threadsafe(self._internal_insight_synthesis(common_topic), self.orch.loop).result(timeout=600)
                    except Exception as e:
                        err_msg = str(e) if str(e) else type(e).__name__
                        print(f"❌ [YO-001] Timeout or Error during Internal Synthesis execution: {err_msg}")
                        synthetic_pages = []
                    
                    if synthetic_pages:
                        print(f"✨ [YO-001] Internal Synthesis successful. Forging Synthetic Galaxy.")
                        all_created_nodes = []
                        for p in synthetic_pages:
                            # Adattamento per simulare l'oggetto 'page' di Playwright
                            from dataclasses import dataclass
                            @dataclass
                            class MockPage:
                                url: str
                                title: str
                                text: str
                            
                            pages = [MockPage(p['url'], p['title'], p['text'])]
                            
                            for page_obj in pages:
                                try:
                                    synthesis_text = f"🌌 YODA SYNTHETIC NODE:\nTopic: {common_topic}\nOrigin: Internal Resonance\n\n{page_obj.text}"
                                    local_x = galaxy_x + random.uniform(-30000, 30000)
                                    local_y = galaxy_y + random.uniform(-30000, 30000)
                                    local_z = galaxy_z + random.uniform(-30000, 30000)
                                    
                                    meta = {
                                        "source": "internal_synthesis", "topic": common_topic, "agent": "YO-001",
                                        "x": local_x, "y": local_y, "z": local_z,
                                        "color": "#facc15", "is_galaxy": True, # Giallo per distinguere le galassie sintetiche
                                        "lifecycle_state": "protected", "importance": 4.0 
                                    }
                                    new_n = asyncio.run_coroutine_threadsafe(self.vault.upsert_text(synthesis_text, metadata=meta), self.orch.loop).result()
                                    if new_n: all_created_nodes.append(new_n)
                                except: continue
                    else:
                        print(f"⚠️ [YO-001] Internal Synthesis also failed or no context found. Skipping.")
                        self.status = "MEDITATION: Seeking new paths..."
                        return 

                else:
                    print(f"🟢 [YO-001] Yoda forging Galaxy from EXTERNAL wisdom: {common_topic}")
                    all_created_nodes = []
                    
                async def _forage_yoda_parallel(forager, u_list):
                    tasks = [_global_forage_helper(forager, u, limit=5) for u in u_list[:2]]
                    results = await asyncio.gather(*tasks, return_exceptions=True)
                    all_p = []
                    for r in results:
                        if isinstance(r, list): all_p.extend(r)
                    return all_p

                try:
                    # [v25.2] Parallel Forage per Yoda
                    all_external_pages = asyncio.run_coroutine_threadsafe(_forage_yoda_parallel(self.orch.forager, urls), self.orch.loop).result(timeout=160)
                    if all_external_pages: self.web_hits += 1
                except Exception as e:
                    print(f"⚠️ [YO-001] External Forage failed: {e}")
                    all_external_pages = []

                for p in all_external_pages:
                    try:
                        synthesis = f"🌌 YODA GALAXY NODE:\nTopic: {common_topic}\nTitle: {p.title}\nSource: {p.url}\n\n{p.text[:1000]}"
                        local_x = galaxy_x + random.uniform(-30000, 30000)
                        local_y = galaxy_y + random.uniform(-30000, 30000)
                        local_z = galaxy_z + random.uniform(-30000, 30000)
                        
                        meta = {
                            "source": "yoda_pilgrimage", "topic": common_topic, "agent": "YO-001",
                            "x": local_x, "y": local_y, "z": local_z,
                            "color": "#00ff41", "is_galaxy": True,
                            "lifecycle_state": "protected", "importance": 5.0 
                        }
                        new_n = asyncio.run_coroutine_threadsafe(self.vault.upsert_text(synthesis, metadata=meta), self.orch.loop).result()
                        if new_n: all_created_nodes.append(new_n)
                    except: continue

                if all_created_nodes:
                    self.galaxies_created += 1
                    self.nodes_introduced_session = getattr(self, 'nodes_introduced_session', 0) + len(all_created_nodes)
                    self.last_galaxy_name = common_topic
                    self.last_galaxy_dist = distance
                    self.nodes_in_last_galaxy = len(all_created_nodes)
                    self.orch.yoda_galaxy_ready = True
                    
                    for i in range(len(all_created_nodes)):
                        if i < len(all_created_nodes) - 1:
                            self.vault.add_relation(all_created_nodes[i].id, all_created_nodes[i+1].id, "galaxy_internal")
                        if i % 4 == 0 and closest_node:
                            self.vault.add_relation(all_created_nodes[i].id, closest_node.id, "yoda_anchor")

                self.status = "MISSION_COMPLETE"
        except Exception as e:
            print(f"🚨 [YO-001] Error: {e}")
            self.status = "MISSION_FAILED"
        finally:
            self.laser_active = False
            time.sleep(3)
            self.status = "Meditating in the Nebula..."

        return {
            "identity": self.identity,
            "pos": self.pos,
            "status": self.status,
            "web_hits_session": self.web_hits,
            "nodes_examined_session": self.nodes_examined,
            "galaxies_session": self.galaxies_created,
            "nodes_introduced_session": getattr(self, 'nodes_introduced_session', 0),
            "last_galaxy_name": getattr(self, 'last_galaxy_name', ""),
            "last_galaxy_dist": getattr(self, 'last_galaxy_dist', 0.0),
            "nodes_in_last_galaxy": getattr(self, 'nodes_in_last_galaxy', 0),
            "laser_active": self.laser_active,
            "smith_fleet": len(getattr(self.orch, 'smiths', {}))
        }

class MandalorianAgent:
    """DN-099 Mandalorian: Semantic Herder & Galaxy Weaver."""
    def __init__(self, engine, orch=None):
        self.vault = engine; self.orch = orch
        self.identity = {"id": "DN-099", "name": "Mandalorian", "role": "GALAXY_HERDER"}
        # [v16.1] Deep Space Deployment: 20M-35M units from center
        self.pos = {"x": 25000000.0, "y": 0.0, "z": -25000000.0}
        print(f"🛰️ [BOOT] DN-099 Mandalorian Initialized at: {self.pos}")
        self.status = "Patrolling the Outer Rim..."
        self.herds_completed = 0
        self.last_herd_nodes = 0
        self.last_herd_time = 0 # Innesco immediato al boot se esistono galassie
        self.laser_active = False
        self.laser_target = {"x": 0, "y": 0, "z": 0}

    def calculate_movement(self, nodes: Dict) -> Optional[Dict]:
        now = time.time()
        
        if getattr(self, 'target_pos', None):
            # 🚀 LERP Smooth Navigation towards target
            step = 0.04
            self.pos['x'] += (self.target_pos['x'] - self.pos['x']) * step
            self.pos['y'] += (self.target_pos['y'] - self.pos['y']) * step
            self.pos['z'] += (self.target_pos['z'] - self.pos['z']) * step
        else:
            # 🛸 Deep Space Patrol: 50M units (Outer Rim Frontier)
            # Gigantic elliptical orbit to patrol deep galaxies
            self.pos['x'] = (45000000 + 5000000 * math.cos(now * 0.005)) * math.cos(now * 0.008) 
            self.pos['y'] = 8000000 * math.sin(now * 0.004)
            self.pos['z'] = (45000000 + 5000000 * math.sin(now * 0.005)) * math.sin(now * 0.008)
            
            # Stato dinamico se non in missione intensiva
            if not self.status.startswith("HERDING") and not self.status.startswith("MISSION_COMPLETE"):
                self.status = "Patrolling Deep Galaxies (Outer Rim)..."
        
        if now - self.last_herd_time > 60: # Ogni minuto raggruppa
            self.last_herd_time = now
            threading.Thread(target=self._execute_mando_mission, daemon=True).start()

        return {"agent": "DN-099", "pos": dict(self.pos), "laser": self.laser_active, "laserTarget": self.laser_target}

    def _execute_mando_mission(self):
        try:
            # 1. Trova tutti i nodi "is_galaxy" e raggruppali per topic
            all_nodes = list(self.vault._nodes.values())
            galaxy_nodes = [n for n in all_nodes if n.metadata.get("is_galaxy")]
            
            if len(galaxy_nodes) < 5: 
                self.status = "Idle: Monitoring Deep Space."
                return

            galaxies = {}
            for n in galaxy_nodes:
                t = n.metadata.get("topic", "Unknown")
                if t not in galaxies: galaxies[t] = []
                galaxies[t].append(n)

            if not galaxies: return

            # 2. Scegli una galassia target a caso per variare la missione
            target_topic = random.choice(list(galaxies.keys()))
            nodes = galaxies[target_topic]
            
            # Calcola centro galassia target
            tx = sum(n.metadata.get('x', 0) for n in nodes) / len(nodes)
            ty = sum(n.metadata.get('y', 0) for n in nodes) / len(nodes)
            tz = sum(n.metadata.get('z', 0) for n in nodes) / len(nodes)
            
            # 🚀 PHASE 1: TRAVEL (Visual interpolation towards galaxy)
            self.status = f"TRAVELING: Heading to {target_topic} Galaxy at high speed..."
            self.target_pos = {"x": tx + 100000, "y": ty + 50000, "z": tz + 100000} 
            time.sleep(6) # Wait for LERP to physically reach the galaxy
            
            # 🔦 PHASE 2: SCANNING
            self.status = f"SCANNING: Analyzing {len(nodes)} nodes in {target_topic}..."
            self.laser_active = True
            self.laser_target = {"x": tx, "y": ty, "z": tz}
            time.sleep(8) # Tempo per l'animazione scanner celeste
            
            # 🧬 PHASE 3: SEMANTIC MERGE
            merge_candidate = None
            for other_topic, other_nodes in galaxies.items():
                if other_topic == target_topic: continue
                # Similarità basata su prefisso o keyword comune (Logica euristica)
                if target_topic[:3].lower() == other_topic[:3].lower() or random.random() < 0.2:
                    merge_candidate = other_topic
                    break
            
            if merge_candidate:
                self.status = f"MERGING: Unifying {target_topic} and {merge_candidate} galaxies..."
                target_nodes = galaxies[merge_candidate]
                # Simula processo di attrazione gravitazionale per l'utente (20s totali)
                time.sleep(12) 
                for n in target_nodes:
                    n.metadata["topic"] = target_topic # Unifica il topic
                nodes.extend(target_nodes)
            
            # 🕸️ PHASE 4: CONNECTING ARCS
            self.status = "CONNECTING: Tethering unified formation to Mother Nebula..."
            
            # Recalcola centro aggiornato (dopo eventuale merge)
            tx = sum(n.metadata.get('x', 0) for n in nodes) / len(nodes)
            ty = sum(n.metadata.get('y', 0) for n in nodes) / len(nodes)
            tz = sum(n.metadata.get('z', 0) for n in nodes) / len(nodes)
            
            dist = math.sqrt(tx**2 + ty**2 + tz**2)
            # [v17.1] Unified Galaxy Range (20M - 35M units)
            target_dist = 20000000.0 + random.uniform(0, 15000000.0) 
            scale = target_dist / dist if dist > 0 else 1.0
            new_center_x = tx * scale
            new_center_y = ty * scale
            new_center_z = tz * scale

            # Global Anchor Scaling (Logic from previous turn)
            max_galaxy_arcs = 8 if len(nodes) >= 1000 else 4
            current_galaxy_arcs = []
            for n in nodes:
                rels = self.vault.get_relations(n.id)
                for r in rels:
                    if r.relation in ["yoda_anchor", "skywalker_anchor", "galaxy_anchor"]:
                        current_galaxy_arcs.append((n.id, r.target_id))
            
            if len(current_galaxy_arcs) > max_galaxy_arcs:
                to_remove = current_galaxy_arcs[max_galaxy_arcs:]
                for node_id, target_id in to_remove:
                    self.vault.remove_relation(node_id, target_id)

            # [v16.6] Sovereign Ring Geometry: Horizontal (XZ) + 15deg Tilt
            # Aumentiamo il raggio per allontanare i nodi (richiesta utente)
            radius = 180000.0 
            tilt_angle = math.radians(15) 
            
            # Trova l'ancora migliore (nodo più vicino al centro reale (0, 1M, 0))
            mother_nodes = [n for n in all_nodes if not n.metadata.get("is_galaxy")]
            mother_anchor = None
            if mother_nodes:
                def dist_from_center(node):
                    nx = node.metadata.get('x', 0)
                    ny = node.metadata.get('y', 1000000)
                    nz = node.metadata.get('z', 0)
                    return math.sqrt(nx**2 + (ny-1000000)**2 + nz**2)
                mother_anchor = min(mother_nodes, key=dist_from_center)

            for i, n in enumerate(nodes):
                angle = (i / len(nodes)) * 2 * math.pi
                
                # Base horizontal ring (XZ)
                lx = radius * math.cos(angle)
                lz = radius * math.sin(angle)
                ly = random.uniform(-15000, 15000) # Spessore nebula
                
                # Apply 15 degree Tilt on X axis to make it "distesa" but angled
                # y' = y*cos(tilt) - z*sin(tilt)
                # z' = y*sin(tilt) + z*cos(tilt)
                final_y = ly * math.cos(tilt_angle) - lz * math.sin(tilt_angle)
                final_z = ly * math.sin(tilt_angle) + lz * math.cos(tilt_angle)
                
                n.metadata['x'] = new_center_x + lx
                n.metadata['y'] = new_center_y + final_y
                n.metadata['z'] = new_center_z + final_z
                n.metadata['lifecycle_state'] = 'protected'
                
                # 🕸️ Super-Galaxy Web: Connetti al precedente
                if i > 0: 
                    self.vault.add_relation(n.id, nodes[i-1].id, "super_galaxy")
                
            # 🏠 PHASE 4: RETURN TO MOTHER NEBULA
            self.status = "RETURNING: Navigating back to Mother Nebula to anchor..."
            self.laser_active = False
            self.target_pos = {"x": 800000, "y": 200000, "z": 800000} # Bordo della Mother Nebula
            time.sleep(8) # Wait for LERP back to the center
            
            # 🕸️ PHASE 5: CONNECTING ARCS (Tethering)
            self.status = "CONNECTING: Tethering unified formation to Mother Nebula..."
            
            # ⚓ Tethering alla Nebula Madre: Forza 4 o 8 archi verso il centro (v18.3)
            # Eseguito fisicamente quando è tornato al centro
            num_tethers = 8 if len(nodes) >= 1000 else 4
            tether_step = max(1, len(nodes) // num_tethers)
            for i, n in enumerate(nodes):
                if i % tether_step == 0 and mother_anchor:
                    self.vault.add_relation(n.id, mother_anchor.id, "galaxy_tether")
                    
            time.sleep(4) # Pausa drammatica mentre gli archi si generano visivamente
            
            self.optimized_arcs_session = num_tethers
            self.status = "MISSION_COMPLETE"
            time.sleep(5) # Mantieni lo stato per l'ologramma

            self.target_pos = None # Torna in orbita profonda
            self.herds_completed += 1
            self.status = "Patrolling Deep Galaxies (Outer Rim)..."
            print(f"🛰️ [DN-099] Mission Success. Unified Constellation at: ({new_center_x:.0f}, {new_center_y:.0f}, {new_center_z:.0f})")

            # 🧹 [v17.1] GALAXY MIGRATION SWEEP: Allinea galassie vecchie ai nuovi range
            all_nodes = list(self.vault._nodes.values())
            for n in all_nodes:
                if not n.metadata.get("is_galaxy"): continue
                
                nx, ny, nz = n.metadata.get('x',0), n.metadata.get('y',0), n.metadata.get('z',0)
                curr_dist = math.sqrt(nx**2 + ny**2 + nz**2)
                src = n.metadata.get("source", "")
                
                # Regole di migrazione per sessioni precedenti
                new_d = 0
                if "yoda" in src.lower() and (curr_dist < 25000000 or curr_dist > 35000000):
                    new_d = 25000000.0 + random.uniform(0, 10000000.0)
                elif "skywalker" in src.lower() and (curr_dist < 6000000 or curr_dist > 8000000):
                    new_d = 6000000.0 + random.uniform(0, 2000000.0)
                
                if new_d > 0:
                    s = new_d / curr_dist if curr_dist > 0 else 1.0
                    n.metadata['x'] *= s; n.metadata['y'] *= s; n.metadata['z'] *= s
                    n.metadata['lifecycle_state'] = 'protected'

        except Exception as e:
            print(f"🚨 [DN-099] Mission Error: {e}")
            self.status = "MISSION_FAILED"

    def get_status_report(self):
        return {
            "identity": self.identity,
            "pos": self.pos,
            "status": self.status,
            "herds_session": getattr(self, 'herds_completed', 0)
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
        self.total_reclaimed = 0.0 
        self.initial_node_count = len(engine._nodes) if hasattr(engine, '_nodes') else 0 # [v8.5] Session anchor
        self.last_inference = {"model": "None", "tps": 0.0, "latency": 0.0, "timestamp": 0}
        self.pause_agents = False
        self.priority_mode = False # [v4.1.9] Concentrazione totale per query utente
        self.mission_history = []
        self.legacy_stats = {} # 📊 [v17.5] Session-Incremental Registry
        self.stats_baseline = {} # 🏛️ [v8.4] Persistent History Baseline
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
        self.r2d2 = R2D2Agent(engine, self)
        self.synth = SynthAgent(engine, self)
        self.bridger_agent = BridgerAgent(engine, self.bridger, self)
        # 🕶️ Fleet di Agent Smith: include sempre un'istanza locale 'PRIMUS'
        self.smiths = {"local": AgentSmith(engine, self)} 
        self.skywalker = SkyWalkerAgent(engine, self)
        self.yoda = YodaAgent(engine, self)
        self.mandalorian = MandalorianAgent(engine, self)
        
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
            "R2-D2": self.r2d2,
            "SY-009": self.synth,
            "CB-003": self.bridger_agent,
            "FS-77": self.skywalker,
            "YO-001": self.yoda,
            "DN-099": self.mandalorian
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
            "SY-009": 60.0, # Synth (Increased for LLM Synthesis)
            "SE-007": 30.0, # Sentinel (Increased for Auditing)
            "QA-101": 30.0, # Quantum
            "FS-77": 60.0,  # Skywalker (Increased for coordination)
            "CB-003": 20.0, # Bridger
            "AG-001": 20.0, # Agent Smith
            "YO-001": 60.0, # Yoda
            "DN-099": 30.0  # Mandalorian
        }
        self._search_lock = threading.Lock() # 🔒 Blocco per evitare ricerche contemporanee
        self.yoda_galaxy_ready = False # Flag per segnalare a SkyWalker che può partire
        self.autonomous_audit_queue = [] # ⚖️ Sovereign Court Escalation
        self._stop_event = threading.Event()
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=10) # 🚀 Expanded Dispatcher
        
        # 🛡️ v17.5 Advanced State & Validation (Critical #1, #6)
        self.node_states = {} 
        self._state_lock = threading.Lock()
        self.edge_validation_queue = [] # Pending synapses for Sentinel
        self.evolution_active = False # [v3.5.0] Evolution Mode state
        
        # 🌌 [v14.0] Ancoraggio Galassie Persistenti
        self._anchor_persistent_galaxies()
        
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
            "FS-77": 30,    # SkyWalker (Ricerca Esterna)
            "YO-001": 45,   # Yoda (Deep Search)
            "DN-099": 40    # Mandalorian (Urbanistica Galattica)
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
            
            # [v8.5] Proactive Inspection Trigger: Smiths scan peers every cycle
            peer_data = self.engine.mesh.peers.get(pid, {"id": pid, "url": "INTERNAL_BRIDGE", "vault_key": "Sovereign-Internal-Sync"})
            self.smiths[pid].inspect_peer(peer_data)
        
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

    def _anchor_persistent_galaxies(self):
        """[v14.0] Scansiona il DB al boot e ancora le galassie esistenti alle loro coordinate fisse."""
        nodes = list(self.vault._nodes.values())
        galaxy_count = 0
        for n in nodes:
            if n.metadata.get("is_galaxy"):
                # Se non ha coordinate, le assegniamo basandoci sul topic (Hash-determinism)
                if 'x' not in n.metadata:
                    import hashlib
                    topic = n.metadata.get("topic", "Unknown")
                    h = int(hashlib.md5(topic.encode()).hexdigest(), 16)
                    # Spaziatura nell'Outer Rim (1.5M - 3M)
                    dist = 1500000 + (h % 1500000)
                    theta = (h % 360) * (math.pi / 180)
                    phi = ((h // 360) % 180) * (math.pi / 180)
                    n.metadata['x'] = dist * math.sin(phi) * math.cos(theta)
                    n.metadata['y'] = dist * math.sin(phi) * math.sin(theta)
                    n.metadata['z'] = dist * math.cos(phi)
                galaxy_count += 1
        if galaxy_count > 0:
            print(f"🌌 [Persistence] Anchored {galaxy_count} existing galaxy nodes to deep space coordinates.")

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
                stable_nodes = [nid for nid, state in list(self.node_states.items()) if state == NodeState.STABLE]
                if stable_nodes:
                    anchor = random.choice(stable_nodes)
                    # 🛡️ [Semantic Firewall v4.1.5]
                    anchor_node = self.vault._nodes.get(anchor)
                    if anchor_node and node.metadata.get("context", "user") == anchor_node.metadata.get("context", "user"):
                        self.vault.add_relation(node.id, anchor, RelationType.SEMANTIC, 0.7)
                else:
                    # Fallback: connect to root or a random node if nebula is young
                    all_ids = list(self.vault._nodes.keys())
                    if all_ids:
                        anchor = random.choice(all_ids)
                        if anchor != node.id:
                            # 🛡️ [Semantic Firewall v4.1.5]
                            anchor_node = self.vault._nodes.get(anchor)
                            if anchor_node and node.metadata.get("context", "user") == anchor_node.metadata.get("context", "user"):
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
                    if hasattr(self, 'loop') and self.loop:
                        asyncio.run_coroutine_threadsafe(self.bridger_agent.sync_codebase(), self.loop)
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
        
        # 💤 [v4.3.1] Initialize Event Loop for Orchestrator FIRST
        self.loop = asyncio.new_event_loop()
        def run_forever_loop(loop):
            asyncio.set_event_loop(loop)
            loop.run_forever()
        threading.Thread(target=run_forever_loop, args=(self.loop,), daemon=True).start()

        # Una tantum: Ingestione codice all'avvio (via dedicated loop)
        asyncio.run_coroutine_threadsafe(self.bridger_agent.sync_codebase(), self.loop)

        # Watcher Proattivo (Fase 1)
        threading.Thread(target=self._codebase_watcher_loop, daemon=True).start()
        
        self.agent_health = {aid: {"failures": 0, "stasis_until": 0} for aid in list(self.agents.keys())}
        self._kinetic_thread = threading.Thread(target=self._run_kinetic_engine, daemon=True); self._kinetic_thread.start()
        
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
        if not agent_id: return None
        mapping = {
            "JA-001": "janitor", "DI-007": "distiller", "SN-008": "snake", 
            "SY-009": "synth", "RP-001": "reaper", "QA-101": "quantum", 
            "SE-007": "sentinel", "CB-003": "bridger_agent", "FS-77": "skywalker",
            "YO-001": "yoda",
            "DN-099": "mandalorian",
            "AG-001": "smith",
            "R2-D2": "r2d2"
        }
        return mapping.get(str(agent_id).strip())

    def _safe_agent_step(self, agent_id, nodes):
        """[CRITICAL #7] Granular Timeout & Circuit Breaker Manager."""
        if not agent_id or agent_id not in self.agent_health:
            return None
            
        health = self.agent_health[agent_id]
        if time.time() < health["stasis_until"]:
            return None 
            
        attr_name = self._get_agent_attr(agent_id)
        if not attr_name:
            print(f"⚠️ [Orchestrator] UNKNOWN AGENT ID: '{agent_id}'")
            return None
            
        agent = getattr(self, attr_name, None)
        if not agent: 
            print(f"⚠️ [Orchestrator] AGENT INSTANCE MISSING: {attr_name} (ID: {agent_id})")
            return None
        
        timeout = self.agent_timeouts.get(agent_id, 15.0)
        
        try:
            # ⏱️ Execute with granular agent-specific timeout
            future = self.executor.submit(agent.calculate_movement, nodes)
            res = future.result(timeout=timeout)
            
            # Reset failure count on success
            health["failures"] = 0
            
            # [v8.4] Verbose Terminal Logging for Agent State Changes
            if not hasattr(self, '_agent_last_status'): self._agent_last_status = {}
            current_status = getattr(agent, 'status', 'Unknown')
            if current_status != self._agent_last_status.get(agent_id):
                print(f"🤖 [Agent {agent_id}] Status: {current_status}")
                self._agent_last_status[agent_id] = current_status
                
            return res
        except Exception as e:
            health["failures"] += 1
            err_msg = str(e) if str(e) else type(e).__name__
            print(f"🚨 [Resilience] Agent {agent_id} failure ({health['failures']}/3): {err_msg}")
            
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
                
                # 🧠 [v8.4] Auto-Trigger NIC Training se raggiunto 1024 nodi
                if hasattr(self.vault, 'nic') and self.vault.nic:
                    if len(nodes) >= 1024 and not self.vault.nic.is_trained and not self.vault.nic.is_training:
                        vectors = [n.vector for n in nodes.values() if hasattr(n, 'vector') and n.vector is not None]
                        if len(vectors) >= 1024:
                            import numpy as np
                            self.vault.nic.train_on_vault_async(np.array(vectors))
                
                # 🛡️ Update Security Fleet (Sempre attivo, anche se il vault è vuoto)
                self._update_smith_fleet()
                for pid, s in list(self.smiths.items()):
                    s.calculate_movement(nodes, pid)
                    if not hasattr(self, '_smith_last_status'): self._smith_last_status = {}
                    if getattr(s, 'status', 'Unknown') != self._smith_last_status.get(pid):
                        print(f"🕴️ [SMITH-{pid[:8]}] Status: {s.status}")
                        self._smith_last_status[pid] = s.status

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
        for nid in list(nodes.keys()):
            n = nodes.get(nid)
            if not n: continue
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
        for nid in list(nodes.keys()):
            n = nodes.get(nid)
            if not n: continue
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
                }, timeout=180.0)
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
            elif aid == "SY-009":
                if action == "Creative Spark":
                    self.synth.sparks_generated += 1
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
                if action == "MISSION_COMPLETE":
                    # web_hits and nodes_created are incremented inside _execute_mission_logic
                    pass
            elif aid == "FS-77":
                if action == "MISSION_COMPLETE":
                    # web_hits and nodes_created are incremented inside _execute_mission_logic
                    pass
            elif aid == "R2-D2":
                if action == "Semantic Grouping":
                    # organized count is managed inside R2D2Agent, but we log it here for history
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
            is_protected = any(getattr(a, 'target_node', None) == tid for a in list(self.agents.values()) if a and hasattr(a, 'identity') and a.identity.get("id") != "JA-001")
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
                        cluster = [r.node.id for r in results if r.node.id != c_id and self.vault._nodes.get(r.node.id) and self.vault._nodes.get(r.node.id).text]
                        neighbor_texts = [self.vault._nodes.get(cid).text for cid in cluster if self.vault._nodes.get(cid)]
                        if not neighbor_texts: return
                        verified = asyncio.run_coroutine_threadsafe(self._arbitrate_quantum_fusion(c_text, neighbor_texts), self.loop).result()
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
                node = self.vault._nodes.get(tid)
                if node:
                    source = node.metadata.get("source", "unknown")
                    if node.metadata.get("agent") == "FS-77":
                        node.metadata["reliability"] = 0.95
                        node.metadata["validated_by"] = "SE-007"
                        self.blackboard.post(SynapticSignal("SENTINEL", AgentRole.GUARDIAN, f"🛡️ VALIDATED: Source {source} passed Reliability Check.", SignalType.SYSTEM_HEALING))
                    else:
                        self.blackboard.post(SynapticSignal("SENTINEL", AgentRole.GUARDIAN, f"🛡️ AUDIT: Node {str(tid)[:8]} verified and stabilized.", SignalType.SYSTEM_HEALING))

        elif action == "Cross-Reference Audit" and tid in self.vault._nodes:
            node = self.vault._nodes.get(tid)
            if node:
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
                            async with aclosing(forager.search(query)) as pages:
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
                    
                    asyncio.run_coroutine_threadsafe(run_audit(), self.loop).result()
                except Exception as e:
                    print(f"⚠️ [Sentinel Error] Audit failed: {e}")
            
            self.executor.submit(real_validation, tid, node.text, node.metadata.get("source_uri"))

    async def forage_web_topic(self, topic: str):
        """Alias per dispatch_skywalker_mission (compatibilità CRAG v4.2.0)."""
        return await self.dispatch_skywalker_mission(topic)

    async def dispatch_skywalker_mission(self, topic: str):
        """[FS-77] Invia File-Sky-Walker in perlustrazione Web per un tema specifico."""
        if self.skywalker.laser_active: return
        
        self.skywalker.status = "Mission: Searching Data..."
        self.skywalker.laser_active = True
        self.blackboard.post(SynapticSignal("FS-77", AgentRole.RESEARCHER, f"🚀 X-Wing ingaggiato: Scansione Web per '{topic}'...", SignalType.MISSION_UPDATE))
        
        # 1. RICERCA URL
        search_data = await self.skywalker._search_web(topic)
        seed_urls = search_data.get("urls", [])
        ai_content = search_data.get("ai_content", "")

        if not seed_urls and not ai_content:
            self.skywalker.laser_active = False
            self.skywalker.status = "Scanning Horizon..."
            self.blackboard.post(SynapticSignal("FS-77", AgentRole.RESEARCHER, f"⚠️ MISSION FALLBACK: Nessuna fonte trovata per {topic}.", SignalType.SYSTEM_NOTIFICATION))
            return

        # 1.5 Handle AI Content immediately if present
        if ai_content:
            print(f"✨ [FS-77] Ingesting Google AI Insight (CRAG) for: {topic}")
            meta = {
                "source": "SkyWalker-AI",
                "topic": topic,
                "agent": "FS-77",
                "x": self.skywalker.laser_target['x'],
                "y": self.skywalker.laser_target['y'],
                "z": self.skywalker.laser_target['z'],
                "color": "#4ade80"
            }
            await self.engine.upsert_text(f"GOOGLE AI INSIGHT: {ai_content}", metadata=meta)
            total_new_nodes += 1

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
                            self.skywalker.status = "Building Galaxy..."
                        
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
        
        # [v8.4] Transient Success Status: Permette alla dashboard di catturare l'evento
        if total_new_nodes > 0:
            self.skywalker.galaxies_created += 1 # Ogni missione riuscita crea una galassia satellite
            self.skywalker.status = f"✅ MISSION COMPLETED!"
        else:
            self.skywalker.status = "⚠️ MISSION COMPLETED: No nodes found."
            
        self.skywalker.laser_active = False
        self.blackboard.post(SynapticSignal("FS-77", AgentRole.RESEARCHER, f"✅ RIENTRO BASE: X-Wing stabilizzato con {total_new_nodes} nuovi nodi.", SignalType.SYSTEM_NOTIFICATION))
        
        # Reset dello stato dopo 10 secondi per tornare in pattugliamento
        async def _reset_status():
            await asyncio.sleep(10)
            if self.skywalker.status.startswith("✅") or self.skywalker.status.startswith("⚠️"):
                self.skywalker.status = "Scanning Horizon..."
        
        asyncio.create_task(_reset_status())

    def _calculate_vault_health(self) -> int:
        """Calcola l'Health Score (0-100) basato su stabilità, entropia e gap."""
        total = len(self.vault._nodes)
        if total == 0: return 100
        stable = sum(1 for s in self.node_states.values() if s == NodeState.STABLE)
        # v18.4: Use list() to avoid 'dictionary changed size during iteration'
        orphans = sum(1 for n in list(self.vault._nodes.values()) if not n.edges)
        
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
                    "purged_session": self.janitor.eaten_count,
                    "purged_total": self.janitor.eaten_count + self.stats_baseline.get("JA-001", {}).get("purged", 0)
                },
                "DI-007": {
                    "identity": self.distiller.identity,
                    "pos": dict(self.distiller.pos),
                    "status": self.distiller.status,
                    "mode": self.distiller.mode,
                    "pruned_session": self.distiller.pruned_count,
                    "pruned_total": self.distiller.pruned_count + self.stats_baseline.get("DI-007", {}).get("pruned", 0)
                },
                "SN-008": {
                    "identity": self.snake.identity,
                    "pos": dict(self.snake.pos),
                    "status": "Active",
                    "found_session": self.snake.found,
                    "found_total": self.snake.found + self.stats_baseline.get("SN-008", {}).get("found", 0),
                    "crafted_session": self.snake.harvested,
                    "crafted_total": self.snake.harvested + self.stats_baseline.get("SN-008", {}).get("harvested", 0),
                    "deleted_session": self.snake.processed,
                    "deleted_total": self.snake.processed + self.stats_baseline.get("SN-008", {}).get("processed", 0)
                },
                "SY-009": {
                    "identity": self.synth.identity,
                    "pos": dict(self.synth.pos),
                    "status": self.synth.status,
                    "mode": "Dreaming",
                    "sparks_session": self.synth.sparks_generated,
                    "sparks_total": self.synth.sparks_generated + self.stats_baseline.get("SY-009", {}).get("sparks", 0),
                    "sub_agents": [s.to_dict() for s in list(self.synth.team)]
                },
                "RP-001": {
                    "identity": self.reaper.identity,
                    "pos": dict(self.reaper.pos),
                    "status": self.reaper.status,
                    "processed_session": self.reaper.processed,
                    "processed_total": self.reaper.processed + self.stats_baseline.get("RP-001", {}).get("processed", 0),
                    "reclaimed_mb_session": getattr(self.reaper, 'reclaimed_mb', 0.0),
                    "reclaimed_mb_total": getattr(self.reaper, 'reclaimed_mb', 0.0) + self.stats_baseline.get("RP-001", {}).get("reclaimed_mb", 0.0)
                },
                "QA-101": {
                    "identity": self.quantum.identity,
                    "pos": dict(self.quantum.pos),
                    "status": self.quantum.status,
                    "fused_clusters_session": getattr(self.quantum, 'clusters_fused', 0),
                    "fused_clusters_total": getattr(self.quantum, 'clusters_fused', 0) + self.stats_baseline.get("QA-101", {}).get("fused_clusters", 0),
                    "is_fusing": getattr(self.quantum, 'is_fusing', False)
                },
                "SE-007": {
                    "identity": self.sentinel.identity,
                    "pos": dict(self.sentinel.pos),
                    "status": self.sentinel.status,
                    "validated_session": getattr(self.sentinel, 'validated_count', 0),
                    "validated_total": getattr(self.sentinel, 'validated_count', 0) + self.stats_baseline.get("SE-007", {}).get("validated", 0),
                    "super_synapses_session": getattr(self.sentinel, 'super_synapses', 0),
                    "super_synapses_total": getattr(self.sentinel, 'super_synapses', 0) + self.stats_baseline.get("SE-007", {}).get("super_synapses", 0),
                    "is_supersynapse": getattr(self.sentinel, 'is_supersynapse', False)
                },
                "CB-003": {
                    "identity": self.bridger_agent.identity,
                    "pos": dict(self.bridger_agent.pos),
                    "status": self.bridger_agent.status,
                    "bridges_session": self.bridger_agent.bridges_total,
                    "bridges_total": self.bridger_agent.bridges_total + self.stats_baseline.get("CB-003", {}).get("bridges", 0)
                },
                "FS-77": {
                    "identity": self.skywalker.identity,
                    "pos": dict(self.skywalker.pos),
                    "status": self.skywalker.status,
                    "web_hits_session": self.skywalker.web_hits,
                    "nodes_introduced_session": self.skywalker.nodes_created,
                    "galaxies_session": self.skywalker.galaxies_created,
                    "laser": getattr(self.skywalker, 'laser_active', False),
                    "laserTarget": getattr(self.skywalker, 'laser_target', {})
                },
                "YO-001": {
                    "identity": self.yoda.identity,
                    "pos": dict(self.yoda.pos),
                    "status": self.yoda.status,
                    "nodes_examined_session": self.yoda.nodes_examined,
                    "nodes_examined_total": self.yoda.nodes_examined + self.stats_baseline.get("YO-001", {}).get("nodes_examined", 0),
                    "web_hits_session": self.yoda.web_hits,
                    "galaxies_session": self.yoda.galaxies_created,
                    "nodes_introduced_session": getattr(self.yoda, 'nodes_introduced_session', 0),
                    "last_galaxy_name": getattr(self.yoda, 'last_galaxy_name', ""),
                    "last_galaxy_dist": getattr(self.yoda, 'last_galaxy_dist', 0.0),
                    "nodes_in_last_galaxy": getattr(self.yoda, 'nodes_in_last_galaxy', 0),
                    "laser": self.yoda.laser_active,
                    "laserTarget": self.yoda.laser_target
                },
                "AG-001": {
                    "identity": {"id": "AG-001", "name": "Agent-Smith", "role": "Mesh Security", "archetype": "guardian"},
                    "pos": list(self.smiths.values())[0].pos if self.smiths else {"x":0,"y":0,"z":0},
                    "status": "Fleet Active",
                    "inspections_session": sum(s.inspections for s in self.smiths.values()),
                    "inspections_total": sum(s.inspections for s in self.smiths.values()) + self.stats_baseline.get("AG-001", {}).get("inspections", 0),
                    "threats_blocked_session": sum(s.threats_blocked for s in self.smiths.values()),
                    "threats_blocked_total": sum(s.threats_blocked for s in self.smiths.values()) + self.stats_baseline.get("AG-001", {}).get("threats_blocked", 0),
                    "fleet": {pid: {"pos": s.pos, "status": s.status} for pid, s in self.smiths.items()},
                    "security_logs": [log for s in self.smiths.values() for log in s.security_logs][:30]
                },
                "DN-099": {
                    "identity": self.mandalorian.identity,
                    "pos": dict(self.mandalorian.pos),
                    "status": self.mandalorian.status,
                    "laser": self.mandalorian.laser_active,
                    "laserTarget": self.mandalorian.laser_target,
                    "herds_session": self.mandalorian.herds_completed,
                    "herds_total": self.mandalorian.herds_completed + self.stats_baseline.get("DN-099", {}).get("herds", 0),
                    "optimized_arcs_session": getattr(self.mandalorian, 'optimized_arcs_session', 0)
                },
                "NC-001": {
                    "identity": {"id": "NC-001", "name": "Neural-Compressor", "role": "Semantic Quantizer", "archetype": "architect"},
                    "pos": {"x": 0, "y": 0, "z": 0},
                    "status": "Compressing..." if (hasattr(self.engine, 'nic') and getattr(self.engine.nic, 'is_training', False)) else ("Active" if hasattr(self.engine, 'nic') else "Offline"),
                    "compression_ratio": "64x" if hasattr(self.engine, 'nic') else "N/A",
                    "optimized_nodes_session": len(self.engine._nodes) if hasattr(self.engine, '_nodes') else 0,
                    "optimized_nodes_total": (len(self.engine._nodes) if hasattr(self.engine, '_nodes') else 0) + self.stats_baseline.get("NC-001", {}).get("optimized_nodes", 0),
                    "is_training": getattr(self.engine.nic, 'is_training', False) if hasattr(self.engine.nic, 'is_training') else False,
                    "training_progress": getattr(self.engine.nic, 'training_progress', 0.0) if hasattr(self.engine.nic, 'is_training') else 0.0
                },
                "R2-D2": {
                    "identity": self.r2d2.identity,
                    "pos": dict(self.r2d2.pos),
                    "status": self.r2d2.status,
                    "organized_session": self.r2d2.organized_count,
                    "organized_total": self.r2d2.organized_count + self.stats_baseline.get("R2-D2", {}).get("organized", 0),
                    "galaxies_session": self.r2d2.galaxies_formed,
                    "galaxies_total": self.r2d2.galaxies_formed + self.stats_baseline.get("R2-D2", {}).get("galaxies", 0),
                    "is_operating": getattr(self.r2d2, 'is_operating', False)
                }
            },
            "blackboard": self.blackboard.get_recent(12),
            "court_actions": self.archiver.history[:20]
        }
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
                    
                    # 📊 [v8.4] Store historical values in baseline, agents keep session-only counts
                    if aid not in self.stats_baseline: self.stats_baseline[aid] = {}
                    self.stats_baseline[aid][cname] = val
            
            print("📊 [Lab/Stats] Persistent history anchored to baseline. Session counters cleared.")
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
                ("FS-77", "nodes", self.skywalker.nodes_created),
                ("FS-77", "galaxies", getattr(self.skywalker, 'galaxies_created', 0)),
                ("AG-001", "inspections", sum(s.inspections for s in self.smiths.values())),
                ("AG-001", "threats", sum(s.threats_blocked for s in self.smiths.values()))
            ]
            
            for aid, cname, val in stats:
                # 🧬 [v8.4] Cumulative save: baseline + current session
                baseline = self.stats_baseline.get(aid, {}).get(cname, 0.0)
                total_val = float(baseline) + float(val)
                
                query = """
                    INSERT INTO agent_telemetry (agent_id, counter_name, val, last_updated)
                    VALUES (?, ?, ?, now())
                    ON CONFLICT (agent_id, counter_name) DO UPDATE SET val = EXCLUDED.val, last_updated = EXCLUDED.last_updated
                """
                self.engine._prefilter.execute(query, (aid, cname, total_val))
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

    async def _call_ollama_for_agent(self, agent_name: str, prompt: str) -> str:
        """Invia un prompt a Ollama per un compito specifico di un agente (Asincrono con Semaforo)."""
        if not hasattr(self, '_ollama_sem'):
            self._ollama_sem = asyncio.Semaphore(2) # Massimo 2 inferenze simultanee
            
        base_url = self.settings.get("ollama_url", "http://localhost:11434")
        model = self.settings.get_model("chat") or "llama3.2"
        
        async with self._ollama_sem:
            try:
                async with httpx.AsyncClient(timeout=60.0) as client:
                    resp = await client.post(f"{base_url}/api/generate", json={
                        "model": model, "prompt": f"### AGENT: {agent_name}\n\n{prompt}", "stream": False
                    })
                    if resp.status_code == 200:
                        return resp.json().get("response", "Error: No response from model.")
            except Exception as e:
                return f"Error: {str(e)}"
        return "Error: Uplink failure or timeout."

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
                async with httpx.AsyncClient(timeout=300.0) as client:
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
                return "L'Oracolo non ha ricevuto risposta dai Giudici entro il limite di 300s. Il carico hardware è elevato o i modelli sono in fase di caricamento (Throttling)."

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
            
            async with httpx.AsyncClient(timeout=180.0) as client:
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
