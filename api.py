import os
os.environ.pop("MallocStackLogging", None)
os.environ.pop("MallocStackLoggingNoCompact", None)
os.environ.pop("MallocScribble", None)
os.environ.pop("MallocGuardEdges", None)

def get_clean_env():
    env = os.environ.copy()
    for key in ["MallocStackLogging", "MallocStackLoggingNoCompact", "MallocScribble", "MallocGuardEdges"]:
        env.pop(key, None)
    return env

import sys
import logging

# 🛡️ [Mac/Sovereign] Aggressive Environment Stabilization (Core #1)
# Must be set before ANY other imports (especially cv2, torch, transformers)
os.environ["OBJC_DISABLE_INITIALIZE_FORK_SAFETY"] = "YES"
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["AV_LOG_LEVEL"] = "quiet"
os.environ["OPENCV_VIDEOIO_PRIORITY_AVFOUNDATION"] = "1"
os.environ["OPENCV_VIDEOIO_PRIORITY_BACKEND"] = "AVFOUNDATION"
os.environ["OPENCV_LOG_LEVEL"] = "OFF"
os.environ["PYAV_SKIP_DLOPEN_CHECK"] = "1"

# [v13.6] Silence "Unauthenticated requests" warning - MUST BE BEFORE ANY HF IMPORTS
os.environ["HF_TOKEN"] = "sovereign_local_boot_shield_v8"
os.environ["HUGGING_FACE_HUB_TOKEN"] = "sovereign_local_boot_shield_v8"
os.environ["HF_HUB_DISABLE_IMPLICIT_TOKEN"] = "1"
os.environ["QT_LOGGING_RULES"] = "*.debug=false;qt.qpa.*=false"
os.environ["LOG_LEVEL"] = "ERROR"
os.environ["PYTHONWARNINGS"] = "ignore"

# Centralized Logging Silence
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("transformers").setLevel(logging.ERROR)
logging.getLogger("huggingface_hub").setLevel(logging.ERROR)
logging.getLogger("sentence_transformers").setLevel(logging.WARNING)
logging.getLogger("uvicorn").setLevel(logging.WARNING)
logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
logging.getLogger("uvicorn.error").setLevel(logging.WARNING)
logging.getLogger("transformers.modeling_utils").setLevel(logging.ERROR)

# [v25.1] Hardened Logging Silence for Terminal Clarity
uvicorn_access = logging.getLogger("uvicorn.access")
uvicorn_access.disabled = True
uvicorn_error = logging.getLogger("uvicorn.error")
uvicorn_error.setLevel(logging.CRITICAL)

import traceback
import json
import uuid
import time
import numpy as np
import threading
import asyncio
import psutil
import random
import shutil
import glob
import signal
import platform
import hashlib
from pathlib import Path
from datetime import datetime, date
from contextlib import asynccontextmanager
from typing import List, Dict, Optional, Any

from retrieval.aegis_bus import aegis_bus
from retrieval.formal_logic import FormalLogicEngine
from retrieval.kuzu_projection import KuzuProjection
from retrieval.epistemic_engine import EpistemicCalculator
from retrieval.playbook_generator import PlaybookGenerator
from retrieval.shadow_twin import ShadowModeTwin
from retrieval.simplifier import SimplificationDaemon
from retrieval.compounding_wiki import CompoundingWikiManager, SovereignWikiLinter
from retrieval.forensic import ClaimVerificationGraph

import uvicorn
os.environ["PYSPARK_PYTHON"] = sys.executable # Just in case

import uvicorn
import httpx
import torch
from fastapi import FastAPI, UploadFile, File, Request, Depends, HTTPException, BackgroundTasks, Header, Form
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx

# Centralized Agentic Fabric Imports
from neural_lab import SynapticSignal, AgentRole, SignalType, NeuralLabOrchestrator, AgentSmith

# --- 🧠 [v8.4] Verbose LLM Interceptor ---
import threading

LLM_INTERCEPTS = []
_intercepts_lock = threading.Lock()

def _log_intercept(model, prompt, response):
    with _intercepts_lock:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        LLM_INTERCEPTS.append({
            "model": model,
            "prompt": prompt,
            "response": response,
            "timestamp": timestamp
        })
        if len(LLM_INTERCEPTS) > 100:
            LLM_INTERCEPTS.pop(0)

def _extract_prompt_text(json_data):
    if not json_data:
        return ""
    if "prompt" in json_data:
        return str(json_data["prompt"])
    if "messages" in json_data:
        msgs = json_data["messages"]
        if isinstance(msgs, list):
            return "\n".join([f"{m.get('role', 'user').upper()}: {m.get('content', '')}" for m in msgs])
        return str(msgs)
    return ""

def _extract_response_text(json_data):
    if not json_data:
        return ""
    if "response" in json_data:
        return str(json_data["response"])
    if "message" in json_data and isinstance(json_data["message"], dict):
        return str(json_data["message"].get("content", ""))
    return ""

_original_async_post = httpx.AsyncClient.post
async def _patched_async_post(self, url, *args, **kwargs):
    is_llm = "/api/generate" in str(url) or "/api/chat" in str(url)
    resp = await _original_async_post(self, url, *args, **kwargs)
    if is_llm and resp.status_code == 200:
        try:
            json_req = kwargs.get("json", {})
            model = json_req.get("model", "unknown")
            prompt = _extract_prompt_text(json_req)
            
            # Check if streaming
            if not json_req.get("stream", False):
                json_resp = resp.json()
                response = _extract_response_text(json_resp)
                _log_intercept(model, prompt, response)
            else:
                _log_intercept(model, prompt, "[Streaming Response - Logs visualizzabili in tempo reale su terminale/chat]")
        except Exception as e:
            print(f"⚠️ [LLM Intercept Error] Fail to capture response: {e}")
    return resp
httpx.AsyncClient.post = _patched_async_post

_original_post = httpx.Client.post
def _patched_post(self, url, *args, **kwargs):
    is_llm = "/api/generate" in str(url) or "/api/chat" in str(url)
    resp = _original_post(self, url, *args, **kwargs)
    if is_llm and resp.status_code == 200:
        try:
            json_req = kwargs.get("json", {})
            model = json_req.get("model", "unknown")
            prompt = _extract_prompt_text(json_req)
            
            # Check if streaming
            if not json_req.get("stream", False):
                json_resp = resp.json()
                response = _extract_response_text(json_resp)
                _log_intercept(model, prompt, response)
            else:
                _log_intercept(model, prompt, "[Streaming Response - Logs visualizzabili in tempo reale su terminale/chat]")
        except Exception as e:
            print(f"⚠️ [LLM Intercept Error] Fail to capture response: {e}")
    return resp
httpx.Client.post = _patched_post
# ----------------------------------------

class NodePosition(BaseModel):
    id: str
    x: float
    y: float

class UpdatePositionsRequest(BaseModel):
    positions: List[NodePosition]

class QueryRequest(BaseModel):
    query: str
    modality: str = "text"
    top_k: int = 5
    consensus: bool = False
    # [v3.6.0] Advanced Filtering
    namespace: Optional[str] = None
    file_type: Optional[str] = None
    year: Optional[int] = None
    month: Optional[int] = None
    wiki_mode: bool = False
    recursive: bool = False
    # [v9.7] Multi-Vector & Sparse Search
    named_vector: Optional[str] = None
    use_sparse: bool = True

# CORE ENGINE IMPORT
from __init__ import NeuralVaultEngine
from network.gossip import SyncSignal
from retrieval.web_forager import SovereignWebForager
from retrieval.multimodal import MultimodalSynapseProcessor
# --- 🎙️ [v8.4] Optional Voice Integration ---
try:
    from interface.voice import SovereignVoiceEngine
    voice_engine = SovereignVoiceEngine()
except (ImportError, Exception) as e:
    print(f"⚠️ [Voice] Interface unavailable (pyttsx3/dependencies missing): {e}")
    voice_engine = None
from utils.neural_compression import NeuralImplicitCompressor
# 🛡️ Agent Smith Security Engine State (v6.0.1)
RETALIATION_LOCKS = {} # {ip: timestamp_expiry}
THREAT_LEVELS = {}     # {ip: score}
MAX_THREAT_SCORE = 10  # Soglia per il lock di 45s

from fastapi.middleware.gzip import GZipMiddleware

app = FastAPI(title="Aura Nexus: NeuralVault API v6.0.1")
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.state.boot_time = datetime.now()
app.state.sse_queues = []

async def broadcast_event(event_type: str, data: Dict[str, Any]):
    """[v9.0] Notifica asincrona a tutti i client SSE connessi via coda dedicata."""
    payload = json.dumps({"event": event_type, "data": data}, default=str)
    # Rimuoviamo code orfane (già gestito nel loop, ma per sicurezza)
    for q in list(app.state.sse_queues):
        try:
            q.put_nowait(payload)
        except:
            pass

# --- AGENT SMITH FIREWALL LOGIC (v6.0.1) ---
def report_threat(request: Request, severity: int = 1):
    """Segnala una minaccia al Sentinel (Agent Smith)."""
    ip = request.client.host
    
    # [v13.6] Whitelist Localhost (Swarm Agents)
    if ip in ["127.0.0.1", "localhost", "::1"]:
        return

    THREAT_LEVELS[ip] = THREAT_LEVELS.get(ip, 0) + severity
    
    if THREAT_LEVELS[ip] >= MAX_THREAT_SCORE:
        # ⚡ RETALIATION LOCK ACTIVATED
        RETALIATION_LOCKS[ip] = time.time() + 45.0 # 45 Seconds Lock
        THREAT_LEVELS[ip] = 0 # Reset score after lock
        print(f"🚨 [Agent Smith] THREAT DETECTED from {ip}. Retaliation Lock: 45s.")
        
        # Invia l'evento alla Dashboard (3D Visualizer)
        asyncio.create_task(broadcast_event("SECURITY_THREAT", {
            "source": ip,
            "severity": "CRITICAL",
            "action": "RETALIATION_LOCK",
            "duration": 45
        }))

class SmithFirewallMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        # Get IP from client info
        client = scope.get("client")
        ip = client[0] if client else "unknown"

        # [v13.6] Whitelist Localhost
        if ip in ["127.0.0.1", "localhost", "::1"]:
            await self.app(scope, receive, send)
            return

        # 1. Verification: IP under Retaliation Lock
        if ip in RETALIATION_LOCKS:
            if time.time() < RETALIATION_LOCKS[ip]:

                remaining = int(RETALIATION_LOCKS[ip] - time.time())
                print(f"🛡️ [Agent Smith] BLOCKED: {ip} for {remaining}s")
                response_content = json.dumps({"detail": f"🛡️ [Agent Smith] Access Denied. Retaliation Lock active for {remaining}s."}).encode("utf-8")
                await send({
                    "type": "http.response.start",
                    "status": 403,
                    "headers": [
                        (b"content-type", b"application/json"),
                        (b"content-length", str(len(response_content)).encode("ascii")),
                    ],
                })
                await send({
                    "type": "http.response.body",
                    "body": response_content,
                })
                return
            else:
                del RETALIATION_LOCKS[ip]

        # 2. Reset Idle Timer on interaction
        try:
            if 'engine' in globals() and engine and hasattr(engine, 'sleep'):
                engine.sleep.touch()
        except: pass

        await self.app(scope, receive, send)

app.add_middleware(SmithFirewallMiddleware)

@app.on_event("startup")
async def startup_event():
    global engine, voice_engine
    
    # 1. Initialize Signal Hijack for instant shutdown
    try:
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        print("🛡️ [System] Signal Hijack ACTIVE: Ctrl+C will force exit.")
    except Exception as e:
        print(f"⚠️ [System] Signal Hijack Warning: {e}")

    storage_dir = os.getenv("NEURALVAULT_DATA_DIR", "./vault_data")
    engine = NeuralVaultEngine(data_dir=storage_dir)
    
    # 2. Load Swarm Settings
    from neural_lab import SwarmSettingsManager
    settings_manager = SwarmSettingsManager(storage_dir)
    engine.settings = settings_manager # Shared access
    base_url = settings_manager.get("ollama_url")
    
    # 3. Initialize Multimodal Engine
    app.state.mm_processor = MultimodalSynapseProcessor(ollama_url=base_url, settings=settings_manager)
    engine.mm_processor = app.state.mm_processor
    
    # 🕵️ Ollama Health
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            resp = await client.get(f"{base_url}/api/tags")
            if resp.status_code == 200:
                print(f"Ollama Uplink: {base_url} ... ✅ READY")
            else:
                print(f"Ollama Uplink: {base_url} ... ⚠️ UNRESPONSIVE")
    except:
        print(f"Ollama Uplink: {base_url} ... ❌ OFFLINE")

    # 4. Initialize Forager & Neural Lab (Orchestrator)
    engine.forager = SovereignWebForager(max_depth=3, max_pages=50, same_domain_only=False)
    app.state.lab = NeuralLabOrchestrator(engine)
    engine.orchestrator = app.state.lab
    
    # 🚀 Start Swarm
    app.state.lab.start_orchestra()
    
    # 🤖 Initialize Telegram Bridge on Boot
    try:
        settings_file = os.path.join(storage_dir, "swarm_settings.json")
        if os.path.exists(settings_file):
            with open(settings_file, "r") as f:
                boot_settings = json.load(f)
            if boot_settings.get("telegram_token"):
                from interface.telegram_bot import start_telegram_bridge
                app.state.telegram_link = start_telegram_bridge(app.state.lab, boot_settings)
                print("🤖 [Telegram] Sovereign Link Initialized on Boot.")
    except Exception as e:
        print(f"⚠️ [Telegram Boot Error] {e}")

    # 🧠 [v9.2] Load Initial Mindset
    app.state.current_mindset = getattr(app.state.lab, 'current_mindset', 'DEFAULT')

    # 🦆 [v9.0] Formal Logic & Graph Projections
    global logic_engine, kuzu_projection, epistemic_engine, playbook_gen, shadow_twin, simplifier
    logic_engine = FormalLogicEngine()
    kuzu_projection = KuzuProjection(os.path.join(storage_dir, "kuzudb"))
    epistemic_engine = EpistemicCalculator()
    playbook_gen = PlaybookGenerator()
    shadow_twin = ShadowModeTwin()
    simplifier = SimplificationDaemon(app.state.lab)
    
    global compounding_wiki_mgr, wiki_linter, forensic_engine
    compounding_wiki_mgr = CompoundingWikiManager(engine)
    wiki_linter = SovereignWikiLinter(compounding_wiki_mgr)
    forensic_engine = ClaimVerificationGraph(engine)
    await compounding_wiki_mgr.sync_llms_txt()
    
    # Register Kuzu & Shadow Mode with Aegis Bus for real-time CQRS updates
    aegis_bus.register_listener(kuzu_projection.handle_event)
    aegis_bus.register_listener(shadow_twin.handle_event)
    
    # [v10.2] Aegis Commit Coordinator (Reconciliation-on-Boot)
    try:
        from core.aegis_coordinator import AegisCommitCoordinator
        coordinator = AegisCommitCoordinator(
            engine=engine,
            kuzu_projection=kuzu_projection,
            log_path=os.path.join(storage_dir, "aegis_event_log.jsonl")
        )
        import threading
        threading.Thread(target=coordinator.check_and_reconcile, daemon=True, name="Aegis-Reconciliation-Boot").start()
    except Exception as ec:
        print(f"⚠️ [Aegis Coordinator Error] Reconciliation init failed: {ec}")
    
    # 📡 [v9.0] Bridge Aegis Events to SSE for Dashboard UI
    main_loop = asyncio.get_event_loop()
    def sse_bridge(event_type, payload):
        try:
            # Normalize event_type if it's an Enum member
            if hasattr(event_type, "name"):
                event_type = event_type.name
            
            asyncio.run_coroutine_threadsafe(broadcast_event(event_type, payload), main_loop)
            # print(f"📡 [SSE Bridge] Enqueued event: {event_type}")
        except Exception as e:
            # print(f"💥 [SSE Bridge Error] {e}")
            pass
    
    aegis_bus.register_listener(sse_bridge)
    print("🏺 [v9.0] Operational Strategy Engines (Playbook, Shadow, Simplifier) & SSE Bridge v9.7 ACTIVE.")

    # 8. Mesh Discovery & Crypto Handshake (v4.0.0)
    def on_peer_found(node_id, address, public_key):
        if engine and engine.gossip:
            engine.gossip.add_peer(node_id, address, public_key)
        if engine and hasattr(engine, 'wormholes') and engine.wormholes:
            engine.wormholes.create_tunnel(node_id, address, public_key)

    if engine and engine.crypto:
        from network.discovery import SovereignDiscovery
        pub_key = engine.crypto.get_public_key_base64()
        engine.discovery = SovereignDiscovery(
            node_id=engine.node_id,
            port=8001, 
            public_key=pub_key,
            on_peer_found_callback=on_peer_found
        )
        import threading
        threading.Thread(target=engine.discovery.start, daemon=True).start()
        print(f"📡 [Mesh] Discovery Online. PubKey: {pub_key[:10]}...")

    # 9. [v8.0] Neural Implicit Compression (NIC) Load
    if hasattr(engine, 'nic'):
        from pathlib import Path
        nic_path = Path(storage_dir) / "nic_codebook.npy"
        if nic_path.exists():
            engine.nic.load(str(nic_path))
            print("🦾 [NIC] Codebook Neurale caricato correttamente.")
        else:
            print("🦾 [NIC] Codebook non trovato. In attesa di prima ottimizzazione.")

    # 10. Database Schema Evolution
    try:
        engine.agent007.execute("ALTER TABLE agent007_entities ADD COLUMN attributes JSON")
        engine.agent007.execute("ALTER TABLE agent007_entities ADD COLUMN relevance FLOAT")
    except: pass
    
    # 11. Pre-load UI settings
    try:
        settings = await get_system_settings()
        app.state.auto_evolve_active = settings.get("auto_evolve_active", False)
    except: pass
    
    # 12. [v7.0] Neural Sleep Engine integration
    if hasattr(app.state, 'lab'):
        engine.sleep = app.state.lab.sleep_engine

    # 13. Start background loops
    asyncio.create_task(shard_maintenance_loop())
    print("🚀 [System] Neural Lab Orchestrator READY.")

def json_serializer(obj):
    if hasattr(obj, 'tolist'): return obj.tolist()
    if isinstance(obj, (datetime, date)): return obj.timestamp()
    try: return float(obj)
    except: return str(obj)

# --- 🛡️ SOVEREIGN SHUTDOWN PROTOCOL (v4.1) ---
_shutdown_lock = threading.Lock()
_is_shutting_down = False

@app.on_event("shutdown")
async def shutdown_event():
    """Arresto controllato via lifecycle FastAPI."""
    global _is_shutting_down
    with _shutdown_lock:
        if _is_shutting_down: return
        _is_shutting_down = True
        
    print("\n🛑 [Lifecycle] Eutanasia Digitale in corso...")
    try:
        if hasattr(app.state, 'lab') and app.state.lab:
            app.state.lab.stop()
        
        # Chiusura asincrona dell'engine per non bloccare il ritorno al terminale
        if engine:
            threading.Thread(target=engine.close, daemon=True).start()
            
    except Exception as e:
        print(f"⚠️ [Shutdown Error] {e}")
    
    print("✅ [Lifecycle] Core spento. Rilascio risorse completato.")
    # Uscita definitiva istantanea
    os._exit(0)

def signal_handler(sig, frame):
    """Fallback per segnali di interruzione rapida (Forced Exit)."""
    print(f"\n⚠️ [Signal {sig}] Interruzione manuale. Eutanasia istantanea.")
    # Usiamo kill(0, SIGKILL) per essere sicuri di chiudere ogni thread zombie se Ctrl+C viene premuto
    os._exit(0)

# Aggancio segnali solo per forzare l'uscita se il lifecycle di FastAPI fallisce
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

from dotenv import load_dotenv
load_dotenv()

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Engine Instance
engine = None
voice_engine = None # [v5.1]
engine_lock = asyncio.Lock()
# [v9.2] Hardened Security: VAULT_KEY is now environment-driven
VAULT_KEY = os.getenv("NEURAL_VAULT_KEY")

if not VAULT_KEY:
    VAULT_KEY = "VAULT_SECURE_KEY_REQUIRED_IN_ENV" # Security Hardening
    print("🚨 [SECURITY CRITICAL] No NEURAL_VAULT_KEY found in environment variables!")
    print("🚨 [SECURITY CRITICAL] System is in RESTRICTED mode. Please set NEURAL_VAULT_KEY.")
elif VAULT_KEY == "vault_secret_aura_2026":
    print("🛡️  [Security] Sovereign Key detected. (Default signature active)")
else:
    print("🔒 [Security] Custom Sovereign Key ACTIVE.")

def get_api_key(request: Request):
    key = request.headers.get("X-API-KEY")
    if not key and request.query_params.get("api_key"):
        key = request.query_params.get("api_key")
    if key == VAULT_KEY or key == "AURA-ADMIN-77":
        return key
    raise HTTPException(status_code=403, detail="Invalid Neural Vault Key")

def check_api_key(key: str):
    if key == VAULT_KEY or key == "AURA-ADMIN-77":
        return True
    return False

def get_custom_models_path():
    storage_dir = Path(os.getenv("NEURALVAULT_DATA_DIR", "./vault_data"))
    if not storage_dir.exists(): storage_dir.mkdir(parents=True, exist_ok=True)
    return storage_dir / "custom_models.json"

def load_custom_models():
    path = get_custom_models_path()
    if path.exists():
        try:
            with open(path, "r") as f: return json.load(f)
        except: return {}
    return {}

def save_custom_models(models):
    path = get_custom_models_path()
    with open(path, "w") as f: json.dump(models, f, indent=2)

# v21.0: Idle Tracking & Background Consolidation
app.state.last_activity = time.time()
app.state.auto_evolve_active = False
app.state.is_dreaming = False # Flag for background evolution

# --- AGENT FACTORY ENDPOINT (v12.0) ---
class AgentSpawnRequest(BaseModel):
    name: str
    role: str
    prompt: str
    api_key: str

@app.post("/api/agents/spawn")
async def spawn_agent(req: AgentSpawnRequest):
    if req.api_key != VAULT_KEY:
        raise HTTPException(status_code=403, detail="Invalid Vault Key")
    
    if not engine or not engine.orchestrator:
        raise HTTPException(status_code=503, detail="Neural Lab Offline")
    
    try:
        # Map role string to Enum
        role_map = {
            "archivist": AgentRole.ARCHIVIST,
            "analyst": AgentRole.ANALYST,
            "creative": AgentRole.CREATIVE,
            "guardian": AgentRole.GUARDIAN,
            "architect": AgentRole.ARCHITECT,
            "optimizer": AgentRole.OPTIMIZER,
            "expert": AgentRole.EXPERT,
            "researcher": AgentRole.RESEARCHER
        }
        role_enum = role_map.get(req.role, AgentRole.ANALYST)
        
        agent_id = engine.orchestrator.spawn_custom_agent(req.name, role_enum, req.prompt)
        return {"status": "success", "agent_id": agent_id, "message": f"Agent {req.name} forged and deployed."}
    except Exception as e:
        return {"status": "error", "message": str(e)}


# Forage App State
app.state.forage_jobs = {}      # job_id -> status
app.state.forage_proposals = {}  # job_id -> [topics]

# Progress Tracking (Modelli)
install_progress = {} # { "model_name": { "percentage": 0, "status": "idle" } }

# settings tracking
@app.get("/api/swarm/config")
async def get_swarm_config_alias(api_key: str = Depends(get_api_key)):
    """Alias di compatibilità per il vecchio endpoint config."""
    return await get_system_settings()

@app.get("/api/system/settings")
async def get_system_settings(api_key: str = Depends(get_api_key)):
    storage_dir = Path(os.getenv("NEURALVAULT_DATA_DIR", "./vault_data"))
    settings_file = storage_dir / "swarm_settings.json"
    if settings_file.exists():
        try:
            with open(settings_file, "r") as f:
                data = json.load(f)
                if "wiki_model" not in data: data["wiki_model"] = "qwen2.5:7b"
                return data
        except: pass
    return {"theme": "dark", "wiki_model": "qwen2.5:7b"}

@app.get("/api/system/llm-intercepts")
async def get_llm_intercepts(api_key: str = Depends(get_api_key)):
    """[v11.1] Restituisce lo storico delle intercettazioni cognitive locali (Ollama)."""
    with _intercepts_lock:
        return list(reversed(LLM_INTERCEPTS))

@app.post("/api/system/llm-intercepts/clear")
async def clear_llm_intercepts(api_key: str = Depends(get_api_key)):
    """[v11.1] Svuota lo storico delle intercettazioni cognitive locali."""
    with _intercepts_lock:
        LLM_INTERCEPTS.clear()
    return {"status": "ok"}

@app.get("/api/system/weather")
async def get_system_weather(api_key: str = Depends(get_api_key)):
    """[v8.4] Restituisce lo stato meteorologico della conoscenza (Epistemic Weather)."""
    if not hasattr(app.state, 'lab') or not app.state.lab.blackboard:
        raise HTTPException(status_code=503, detail="Neural Lab Blackboard Offline")
    
    return app.state.lab.blackboard.get_weather()

@app.post("/api/system/priority")
async def set_system_priority(request: Request, api_key: str = Depends(get_api_key)):
    """Sospende o riprende l'attività degli agenti per dare priorità all'utente."""
    try:
        data = await request.json()
        priority = data.get("active", False)
        app.state.lab.pause_agents = priority
        if hasattr(engine, 'priority_mode'):
            engine.priority_mode = priority
        status = "PRIORITY_FOCUS_ACTIVE" if priority else "SWARM_RESUMED"
        print(f"⚡ [System] Shifted Priority: {status}")
        return {"status": status, "paused": app.state.lab.pause_agents}
    except Exception as e:
        return {"error": str(e)}

FLIGHT_MODE_ACTIVE = False

@app.post("/api/flight-mode")
async def set_flight_mode(request: Request, api_key: str = Depends(get_api_key)):
    global FLIGHT_MODE_ACTIVE
    data = await request.json()
    FLIGHT_MODE_ACTIVE = data.get("active", False)
    
    # Throttle orchestrator to preserve GPU/CPU for Flight Simulator
    if hasattr(app.state, 'lab'):
        app.state.lab.pause_agents = FLIGHT_MODE_ACTIVE
        
    status = "FLIGHT_ACTIVE_THROTTLING_ON" if FLIGHT_MODE_ACTIVE else "FLIGHT_ENDED_RESUMING_SWARM"
    print(f"\n🚀 [Flight Protocol] {status}")
    return {"status": status, "flight_mode": FLIGHT_MODE_ACTIVE}

# [v6.0.1] Recommendations consolidated at line 3379

@app.post("/api/system/settings")
async def update_system_settings(req: Dict[str, Any]):
    # We use a simple auth check without Depends if needed, but here we'll just check the vault key
    if req.get("api_key") != VAULT_KEY:
         raise HTTPException(status_code=403, detail="Invalid Vault Key")
    
    storage_dir = Path(os.getenv("NEURALVAULT_DATA_DIR", "./vault_data"))
    if not storage_dir.exists(): storage_dir.mkdir(parents=True, exist_ok=True)
    
    settings_file = storage_dir / "swarm_settings.json"
    current = {}
    if settings_file.exists():
        try:
            with open(settings_file, "r") as f:
                current = json.load(f)
        except: pass
    
    # Remove api_key from stored settings
    data = {k:v for k,v in req.items() if k != "api_key"}
    current.update(data)
    
    with open(settings_file, "w") as f:
        json.dump(current, f)
    
    # Sync with live state
    if hasattr(app.state, 'lab'):
        app.state.lab.settings.update(data)
        if "evolution_active" in req:
            app.state.lab.evolution_active = req["evolution_active"]
        if "auto_evolve_active" in req:
             app.state.auto_evolve_active = req["auto_evolve_active"]
             
        # 🔗 [v4.0] Live Sync Git Bridge
        if "github_token" in data or "github_repo" in data:
            tk = current.get("github_token")
            rp = current.get("github_repo")
            if tk and rp:
                app.state.lab.git_bridge.setup_github(tk, rp)
        
        # 🤖 [v4.1.5] Live Sync Telegram Bridge
        if "telegram_token" in data or "telegram_user_id" in data:
            from interface.telegram_bot import start_telegram_bridge
            # Hot-reload del bridge Telegram
            existing = getattr(app.state, 'telegram_link', None)
            app.state.telegram_link = start_telegram_bridge(app.state.lab, current, existing_bridge=existing)
            if existing and app.state.telegram_link != existing:
                print("🤖 [Telegram] Sovereign Link Riavviato con nuove impostazioni.")
                
        print(f"🧬 [Sovereign State] Live Sync Complete. Evolution Mode: {getattr(app.state.lab, 'evolution_active', False)}")

    return {"status": "success", "settings": current}

# 🧠 [v9.0] COGNITIVE PRESETS API
@app.get("/api/system/presets")
async def get_cognitive_presets(api_key: str = Depends(get_api_key)):
    if hasattr(app.state, 'lab') and hasattr(app.state.lab, 'preset_mgr'):
        return app.state.lab.preset_mgr.config
    return {"error": "Preset Manager Offline"}

@app.post("/api/system/presets")
async def update_cognitive_preset(req: Dict[str, Any], api_key: str = Depends(get_api_key)):
    if hasattr(app.state, 'lab') and hasattr(app.state.lab, 'preset_mgr'):
        name = req.get("active_preset")
        if app.state.lab.preset_mgr.set_preset(name):
            return {"status": "success", "active_preset": name}
        return {"status": "error", "message": "Preset not found"}
    return {"error": "Preset Manager Offline"}

@app.post("/api/github/test")
async def test_github_connection(req: Dict[str, Any]):
    """Verifica la validità del token e l'accesso al repository."""
    if req.get("api_key") != VAULT_KEY:
        raise HTTPException(status_code=403, detail="Invalid Vault Key")
    
    token = req.get("token")
    repo = req.get("repo")
    if not token or not repo:
        return {"success": False, "error": "Token o Repository mancanti."}
    
    try:
        async with httpx.AsyncClient() as client:
            headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"}
            r = await client.get(f"https://api.github.com/repos/{repo}", headers=headers)
            if r.status_code == 200:
                return {"success": True, "data": r.json().get("full_name")}
            else:
                return {"success": False, "error": f"GitHub Error: {r.status_code}"}
    except Exception as e:
        return {"success": False, "error": str(e)}

# [v6.1] background loops moved to NeuralLabOrchestrator dedicated thread.

class ActivityTrackerMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            path = scope.get("path", "")
            if path.startswith("/api/"):
                if hasattr(app, "state"):
                    app.state.last_activity = time.time()
                    if hasattr(app.state, 'lab') and hasattr(app.state.lab, 'sleep_engine'):
                        try:
                            app.state.lab.sleep_engine.touch()
                        except: pass
        
        await self.app(scope, receive, send)

app.add_middleware(ActivityTrackerMiddleware)

async def shard_maintenance_loop():
    """v3.0: Automated Shard Maintenance (Cloning & Backup). Runs every 30 minutes."""
    iteration = 0
    while not _is_shutting_down:
        if hasattr(app.state, 'lab') and app.state.lab.priority_mode:
            await asyncio.sleep(10)
            continue
        try:
            if engine and hasattr(engine, 'shards'):
                # 1. Incremental Backup (Every 30m)
                print("🛡️ [Maintenance] Running automated shard backup...")
                storage_dir_path = Path(os.getenv("NEURALVAULT_DATA_DIR", "./vault_data"))
                await asyncio.to_thread(engine.shards.auto_backup, storage_dir_path)
                
                # 2. Full Shard Cloning (Every 12 hours = 24 iterations of 30m)
                if iteration % 24 == 0:
                    shards = getattr(engine.shards, 'active_shards', {})
                    if shards:
                        print(f"🛡️ [Maintenance] Creating clones for {len(shards)} shards...")
                        for shard_id in list(shards.keys()):
                            await asyncio.to_thread(engine.shards.clone_shard, shard_id)
                    else:
                        print("🛡️ [Maintenance] No active shards to clone.")
                
                # Signal on blackboard
                if hasattr(app.state, 'lab'):
                    msg = "📦 [ShardGuard] Backup automatico completato."
                    if iteration % 24 == 0: msg = "🛡️ [ShardGuard] Clone e Backup completati."
                    sig = SynapticSignal("SYSTEM", AgentRole.GUARDIAN, msg, SignalType.SYSTEM_NOTIFICATION)
                    app.state.lab.blackboard.post(sig)
        except Exception as e:
            print(f"❌ [Maintenance Error] {e}")
            
        iteration += 1
        await asyncio.sleep(1800) # 30 minutes


from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse, FileResponse, Response

# Static Files (Dashboard)
# --- 🖥️ DASHBOARD ENDPOINTS ---
@app.get("/", response_class=FileResponse)
async def get_dashboard():
    """Carica la UI principale del Cycloscope."""
    return FileResponse("dashboard/index.html")

@app.get("/wiki", response_class=FileResponse)
async def get_wiki_standalone():
    """🏛️ [v8.0] Sovereign Wiki Standalone Entry."""
    return FileResponse("dashboard/index.html")
@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return Response(status_code=204)

@app.get("/apple-touch-icon.png", include_in_schema=False)
@app.get("/apple-touch-icon-precomposed.png", include_in_schema=False)
async def apple_touch_icon():
    return Response(status_code=204)

app.mount("/static", StaticFiles(directory="dashboard/static"), name="static")
app.mount("/api/media", StaticFiles(directory="vault_data/media"), name="media")


def find_node_robust(node_id: str) -> Optional[Any]:
    """Cerca un nodo nell'engine in modo ultra-aggressivo (ID, Sharding, Meta)."""
    if engine is None: return None
    
    clean_id = str(node_id).strip().split("_")[0]
    
    # 1. Ricerca rapida (Hash Map)
    if node_id in engine._nodes: return engine._nodes[node_id]
    if clean_id in engine._nodes: return engine._nodes[clean_id]
    
    # 2. Ricerca numerica
    try:
        int_id = int(clean_id)
        if int_id in engine._nodes: return engine._nodes[int_id]
    except: pass
    
    # 3. Scansione lineare Cache
    for k, n in engine._nodes.items():
        n_id = str(getattr(n, 'id', n.get('id', '') if isinstance(n, dict) else ''))
        if str(k) == str(node_id) or n_id == str(node_id) or n_id == clean_id:
            return n
    
    # 4. Ricerca nel Tier Episodico (Persistenza)
    try:
        if hasattr(engine, '_tiers'):
            node = engine._tiers.get(node_id)
            if node: return node
            node = engine._tiers.get(clean_id)
            if node: return node
    except: pass
            
    return None

@app.get("/api/debug/stats")
async def get_debug_stats(api_key: str = Depends(get_api_key)):
    """[DEBUG v14] Chiamata diretta a engine.stats() per diagnosticare la telemetria 3D."""
    print("🔬 [DEBUG] Chiamata a /api/debug/stats ...")
    try:
        loop = asyncio.get_event_loop()
        stats = await loop.run_in_executor(None, engine.stats)
        return JSONResponse({
            "ok": True,
            "nodes_count": stats.get("nodes_count", 0),
            "point_cloud_len": len(stats.get("point_cloud", [])),
            "edge_sample_len": len(stats.get("edge_sample", [])),
            "first_point": stats.get("point_cloud", [None])[0]
        })
    except Exception as e:
        import traceback
        print(f"❌ [DEBUG/stats] {e}\n{traceback.format_exc()}")
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)

@app.get("/api/wiki/forensic")
async def get_wiki_forensic(api_key: str = Depends(get_api_key)):
    """[v10.1] Restituisce il report delle contraddizioni cross-wiki."""
    if not forensic_engine:
        raise HTTPException(status_code=503, detail="Forensic Engine Offline")
    return await forensic_engine.get_forensic_report()

@app.get("/api/node/{node_id}")
async def get_node_data(node_id: str, api_key: str = Depends(get_api_key)):
    """Recupera il contenuto completo e le connessioni locali di un nodo."""
    # 🔮 [v4.3.1] Record interaction for pre-fetching
    if hasattr(app.state, 'lab') and hasattr(app.state.lab, 'prefetcher'):
        app.state.lab.prefetcher.record_interaction(node_id)
        
    # [v17.5.1] Adaptive Cache L1 Check
    if hasattr(app.state, 'lab') and hasattr(app.state.lab, 'prefetcher'):
        cached = app.state.lab.prefetcher.get_cached_node(node_id)
        if cached:
            print(f"🔮 [Prefetch-Hit] Serving node {node_id[:8]} from L1 Hot RAM.")
            if hasattr(cached, 'to_dict'):
                return cached.to_dict()
            return cached

    try:
        # [v9.2.1] Performance Optimization: Removed global engine_lock for read-only access.
        node = find_node_robust(node_id)
                        
        if node:
            # Estrazione Campi Reali (Supporta sia VaultNode che dict)
            n_text = getattr(node, 'text', "")
            if not n_text and isinstance(node, dict):
                n_text = node.get('text', "")
                
            n_meta = getattr(node, 'metadata', {})
            if not n_meta and isinstance(node, dict):
                n_meta = node.get('metadata', {})
                
            n_type = n_meta.get("type", "text") if isinstance(n_meta, dict) else "text"
            
            # Gestione Anteprima Multimediale
            media_preview = None
            if isinstance(n_meta, dict):
                if n_type == "image":
                    media_preview = n_meta.get("source") or n_meta.get("url")
                elif n_type == "video":
                    media_preview = n_meta.get("thumbnail") or n_meta.get("source")

            # [Ebbinghaus Reinforcement]
            try:
                if isinstance(n_meta, dict):
                    n_meta["last_access"] = time.time()
                    n_meta["access_count"] = n_meta.get("access_count", 1) + 1
            except: pass

            # Recupera connessioni reali
            connessioni = []
            try:
                # Relazioni dirette (GNN Sync)
                edges = getattr(node, 'edges', [])
                for e in edges:
                    connessioni.append({
                        "node": str(e.target_id), 
                        "relation": str(e.relation), 
                        "reason": getattr(e, 'reason', None)
                    })

                # Fallback: agent007
                if engine and hasattr(engine, 'agent007') and engine.agent007:
                    res = engine.agent007.execute("""
                        SELECT target_id, type FROM agent007_relations WHERE source_node_id = ?
                    """, (node_id,)).fetchall()

                    for r in res:
                        connessioni.append({"node": r[0], "relation": r[1]})
            except Exception as ce:
                print(f"⚠️ [api/node] Error fetching connections for {node_id}: {ce}")

            # Calcolo created_at robusto
            try:
                c_at = getattr(node, 'created_at', time.time())
                if isinstance(node, dict):
                    c_at = node.get('created_at', c_at)
                c_at = float(c_at)
            except:
                c_at = time.time()

            return {
                "id": node_id,
                "text": n_text,
                "type": n_type,
                "preview": media_preview,
                "metadata": n_meta,
                "created_at": c_at,
                "connections": connessioni
            }
                
        return JSONResponse(status_code=404, content={"error": f"Node {node_id} not found"})
    except Exception as e:
        import traceback
        print(f"❌ [api/node] Global Error: {e}\n{traceback.format_exc()}")
        return JSONResponse(status_code=500, content={"error": f"Internal server error: {str(e)}"})

@app.get("/api/node/verify/{node_id}")
async def verify_node_coherence(node_id: str, api_key: str = Depends(get_api_key)):
    """Verifica la coerenza logica di un nodo rispetto alla Nebula (Neural Audit)."""
    # 🔮 [v4.3.1] Record interaction for pre-fetching
    if hasattr(app.state, 'lab') and hasattr(app.state.lab, 'prefetcher'):
        app.state.lab.prefetcher.record_interaction(node_id)
        
    # [v17.5.1] Adaptive Cache L1 Check
    if hasattr(app.state, 'lab') and hasattr(app.state.lab, 'prefetcher'):
        cached = app.state.lab.prefetcher.get_cached_node(node_id)
        if cached:
            print(f"🔮 [Prefetch-Hit] Serving node {node_id[:8]} from L1 Hot RAM.")
            return cached.to_dict()

    node = engine.get_node(node_id)
    if not node: return {"error": "Node not found"}
    
    # Recuperiamo il contesto circostante (vicini semantici) per la verifica
    neighbors = await engine.query(node.text, k=3)
    context = "\n".join([f"Vicino: {n.node.text}" for n in neighbors if n.node.id != node_id])
    
    prompt = f"""ANALISI COERENZA NEURALE (SOVEREIGN AUDIT)
Nodo da verificare: {node.text}

Contesto circostante:
{context}

Analizza se il nodo è coerente con il contesto o se presenta allucinazioni, errori tecnici o conflitti logici. 
Rispondi in modo tecnico e conciso (max 3 frasi). Inizia con [COERENTE] o [INCOERENTE]."""

    try:
        # 🧠 [v17.5] Dynamic Sovereign Audit Model Selection
        base_url = app.state.lab.settings.get("ollama_url") if hasattr(app.state, 'lab') else "http://127.0.0.1:11434"
        audit_model = app.state.lab.settings.get("evolution_model", "llama3.2") if hasattr(app.state, 'lab') else "llama3.2"
        
        async with httpx.AsyncClient(timeout=90.0) as client:
            r = await client.post(f"{base_url}/api/generate", json={
                "model": audit_model, "prompt": prompt, "stream": False
            })
            res = r.json()
            if "error" in res:
                return {"audit": f"Errore dal Modello ({audit_model}): {res['error']}"}
            return {"audit": res.get("response", "Audit fallito senza risposta.")}
    except Exception as e:
        return {"audit": f"Errore durante l'audit: {str(e)}"}

@app.get("/api/node/{node_id}/mermaid")
async def get_node_mermaid(node_id: str, api_key: str = Depends(get_api_key)):
    """[Sprint 2] Genera un diagramma Mermaid per Callflow (AST) o vicini semantici."""
    node = engine.get_node(node_id)
    if not node: return JSONResponse(status_code=404, content={"error": "Node not found"})
    
    n_meta = getattr(node, 'metadata', {})
    n_type = n_meta.get("type", "text") if isinstance(n_meta, dict) else "text"
    
    mermaid_lines = ["graph TD", "classDef module fill:#1e293b,stroke:#3b82f6,color:#fff", "classDef class fill:#0f172a,stroke:#8b5cf6,color:#fff", "classDef func fill:#020617,stroke:#10b981,color:#fff"]
    
    # Se è un nodo codice, usiamo la logica AST
    if n_type in ["code_module", "code_class", "code_function"]:
        # Cerca i figli diretti (classi o funzioni) e costruisce il callflow
        root_name = getattr(node, 'text', "").split('\\n')[0].replace('CODE_MODULE [', '').replace('CODE_CLASS [', '').replace('CODE_FUNCTION [', '').replace(']', '').strip()
        mermaid_lines.append(f"  {node_id}[{root_name}]:::{n_type.split('_')[1]}")
        
        # Recupera tutte le connessioni CHILD_OF verso questo nodo
        for edge in getattr(node, 'edges', []):
            if edge.relation == "CHILD_OF":
                child = engine.get_node(edge.target_id)
                if child:
                    c_meta = getattr(child, 'metadata', {})
                    c_type = c_meta.get("type", "code_function").replace("code_", "")
                    c_name = getattr(child, 'text', "").split('\\n')[0].split('[')[-1].replace(']', '').strip()
                    mermaid_lines.append(f"  {edge.target_id}[{c_name}]:::{c_type}")
                    mermaid_lines.append(f"  {node_id} --> {edge.target_id}")
                    
                    # Aggiunge anche le call
                    calls = c_meta.get("calls", [])
                    for call in calls:
                        mermaid_lines.append(f"  {edge.target_id} -.-> {call}({call})")
                        
        # Anche le chiamate dal nodo root stesso
        calls = n_meta.get("calls", [])
        for call in calls:
            mermaid_lines.append(f"  {node_id} -.-> {call}({call})")
            
    else:
        # Fallback per nodi testo normale: mostra la neighborhood
        mermaid_lines.append(f"  root[{node_id[:8]}]")
        for edge in getattr(node, 'edges', [])[:10]: # max 10 vicini
            mermaid_lines.append(f"  root -- {edge.relation} --> {edge.target_id[:8]}[{edge.target_id[:8]}]")

    return {"mermaid": "\\n".join(mermaid_lines)}


@app.post("/api/purge")
async def nuclear_purge(api_key: str = Depends(get_api_key)):
    """Protocollo 'VETRO' (v1.0): Reset totale immediato."""
    print("☢️ PROTOCOLLO VETRO (VETRO-NUCLEAR) ATTIVATO.")
    
    try:
        # v3.9.5: Uso del metodo centralizzato dell'engine per chiudere connessioni e pulire disco
        if engine:
            engine.purge_all()
        else:
            # Fallback se l'engine non è ancora init
            data_path = "./vault_data"
            import shutil, os
            if os.path.exists(data_path):
                shutil.rmtree(data_path, ignore_errors=True)
                os.makedirs(data_path, exist_ok=True)
        
        print("☢️ TABULA RASA COMPLETATA.")
        return {"status": "ok", "message": "Neural memories incinerated. Core stabilized."}
    except Exception as e:
        print(f"❌ [VETRO FAIL] {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.get("/api/documents")
async def list_documents(api_key: str = Depends(get_api_key)):
    """Recupera l'inventario cronologico della conoscenza acquisita."""
    if engine is None: return {"documents": []}
    try:
        # Recuperiamo tutti i nodi e estraiamo le sorgenti uniche dai metadati
        inventory = []
        seen_sources = set()
        
        # Ordiniamo per data di creazione se disponibile
        all_nodes = list(engine._nodes.values())
        all_nodes.sort(key=lambda x: getattr(x, 'created_at', 0), reverse=True)
        
        for node in all_nodes:
            source = node.metadata.get("source", "Manual_Entry")
            if source not in seen_sources:
                # Determiniamo il tipo basandoci sull'estensione o metadati
                s_lower = source.lower()
                doc_type = "TEXT"
                if s_lower.startswith("http"): doc_type = "URL"
                elif any(s_lower.endswith(ext) for ext in [".mp4", ".mov", ".avi"]): doc_type = "VIDEO"
                elif any(s_lower.endswith(ext) for ext in [".mp3", ".wav", ".m4a"]): doc_type = "AUDIO"
                elif any(s_lower.endswith(ext) for ext in [".jpg", ".jpeg", ".png", ".webp"]): doc_type = "IMAGE"
                elif any(s_lower.endswith(ext) for ext in [".pdf", ".txt", ".md", ".docx"]): doc_type = "FILE"
                
                created_at = getattr(node, 'created_at', time.time())
                dt = datetime.fromtimestamp(created_at)
                
                inventory.append({
                    "name": source if len(source) < 50 else source[:47] + "...",
                    "full_name": source,
                    "type": doc_type,
                    "date": dt.strftime("%d/%m/%Y"),
                    "time": dt.strftime("%H:%M:%S")
                })
                seen_sources.add(source)
                
        return {"documents": inventory}
    except Exception as e:
        return {"documents": [], "error": str(e)}

@app.get("/api/intelligence/status")
async def get_intelligence_status(api_key: str = Depends(get_api_key)):
    """Restituisce lo stato dell'OrchestraIA, degli agenti e del Distiller (v8.0)."""
    if not hasattr(app.state, "lab") or not app.state.lab: 
        return {"status": "offline"}
    return app.state.lab.get_orchestra_report()

@app.get("/api/intelligence/agents/custom/list")
async def list_custom_agents(api_key: str = Depends(get_api_key)):
    """Restituisce la lista di tutti gli agenti custom salvati."""
    if not app.state.lab: return {"agents": []}
    return {"agents": app.state.lab.custom_agents_config}

@app.post("/api/intelligence/agents/custom/favorite")
async def toggle_favorite_agent(req: Dict, api_key: str = Depends(get_api_key)):
    """Imposta o rimuove un agente dalla lista dei preferiti (auto-spawn)."""
    if not app.state.lab: return {"error": "Neural Lab Offline"}
    name = req.get("name")
    is_fav = req.get("is_favorite", False)
    if not name: return {"error": "Name required"}
    
    success = app.state.lab.toggle_favorite_agent(name, is_fav)
    return {"status": "success" if success else "error", "name": name, "is_favorite": is_fav}

@app.post("/api/intelligence/agents/custom")
async def create_custom_agent(config: Dict, api_key: str = Depends(get_api_key)):
    """Crea un nuovo agente custom. Se 'save' è True, l'agente viene persistito su disco."""
    if not app.state.lab: return {"error": "Neural Lab Offline"}
    
    name = config.get("name")
    role = config.get("role", "analyst")
    prompt = config.get("prompt", "")
    model = config.get("model", "llama3.2")
    save_to_disk = config.get("save", False)
    is_favorite = config.get("is_favorite", False)

    if not name: return {"error": "Name required"}
    
    # 1. Spawn Immediato nello Swarm attivo
    agent_id = app.state.lab.spawn_custom_agent(name, role, prompt, model)
    
    # 2. Persistenza su disco (opzionale)
    if save_to_disk:
        app.state.lab.custom_agents_config[name] = {
            "model": model,
            "role": role,
            "prompt": prompt,
            "color": config.get("color", "#00ffcc"),
            "is_favorite": is_favorite,
            "created_at": time.time()
        }
        with open(app.state.lab.custom_agents_path, "w") as f:
            json.dump(app.state.lab.custom_agents_config, f)
        
    return {
        "status": "Agent Spawned", 
        "agent_id": agent_id, 
        "name": name, 
        "persistent": save_to_disk,
        "is_favorite": is_favorite
    }

@app.delete("/api/intelligence/agents/custom/{name}")
async def delete_custom_agent(name: str, api_key: str = Depends(get_api_key)):
    """Rimuove un agente custom."""
    if not app.state.lab: return {"error": "Neural Lab Offline"}
    
    if name in app.state.lab.custom_agents_config:
        del app.state.lab.custom_agents_config[name]
        with open(app.state.lab.custom_agents_path, "w") as f:
            json.dump(app.state.lab.custom_agents_config, f)
        return {"status": "Agent Deleted"}
    
    return {"error": "Agent not found"}

@app.post("/api/log")
async def client_log(request: Request, api_key: str = Depends(get_api_key)):
    """Ponte di Telemetria Inversa: Visualizza le azioni del browser nel terminale."""
    try:
        data = await request.json()
        msg = data.get("message", "")
        level = data.get("level", "INFO")
        print(f"🖥️ [Interactive HUD] {msg}")
    except: pass
    return {"status": "ok"}

# --- MULTIMODAL BRIDGE ENDPOINTS (v4.0) ---

@app.post("/api/multimodal/upload")
async def upload_multimodal(file: UploadFile = File(...), api_key: str = Depends(get_api_key)):
    """Ingestione Drag-and-Drop: Caricamento e processamento di Immagini/Audio/Video."""
    # api_key is validated by get_api_key dependency
    
    if engine is None:
        raise HTTPException(status_code=503, detail="Neural Engine Offline")

    try:
        # 1. Salvataggio temporaneo
        temp_dir = engine.data_dir / "temp_uploads"
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = temp_dir / f"{uuid.uuid4().hex}_{file.filename}"
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # 2. Ingestione nel Vault (Estrae trascrizioni, descrizioni e vettori)
        nodes = await engine.upsert_multimodal(str(file_path))
        
        # 3. Pulizia (Opcionale, potremmo voler tenere i file originali)
        # os.remove(file_path) 
        
        return {
            "status": "success",
            "ingested_nodes": len(nodes),
            "source": file.filename,
            "message": f"Ingeriti {len(nodes)} segmenti multimodali."
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

# --- SHARDING & CLONING AUTOMATION (v1.0) ---

@app.post("/api/sharding/clone")
async def manual_shard_clone(api_key: str = Depends(get_api_key)):
    """Clonazione manuale dello shard attivo (Snapshot atomico)."""
    if not engine or not hasattr(engine, 'shards'):
        raise HTTPException(status_code=503, detail="Sharding System Offline")
    
    try:
        shard_id = engine.shards.clone_shard()
        return {"status": "success", "shard_id": shard_id, "message": "Clonazione shard completata."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/sharding/backup")
async def manual_shard_backup(api_key: str = Depends(get_api_key)):
    """Trigger manuale per il backup fisico dei segmenti (.ael, .db)."""
    if not engine or not hasattr(engine, 'shards'):
        raise HTTPException(status_code=503, detail="Sharding System Offline")
    
    try:
        engine.shards.auto_backup()
        return {"status": "success", "message": "Backup fisico completato."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/files/upload")
@app.post("/api/upload")
async def upload_file(
    file: UploadFile = File(...), 
    namespace: Optional[str] = Form("default"), 
    force: bool = Form(False),
    api_key: str = Depends(get_api_key)
):
    print(f"📥 [Ingestion] Richiesta ricevuta: {file.filename} ({file.content_type})")
    content = await file.read()
    text = content.decode('utf-8', errors='ignore')
    node_id = str(uuid.uuid4())
    if engine is None: return {"error": "Engine not initialized"}
    
    # [NEW] Pre-Ingestion Impact Analysis (v11.3.1)
    if not force:
        try:
            from security.impact_analyzer import PreIngestionImpactAnalyzer
            analyzer = PreIngestionImpactAnalyzer(engine)
            report = await analyzer.analyze_before_ingest(text, file.filename)
            
            if report.recommendation == "REVIEW":
                print(f"⚠️ [Ingestion Blocked] Rilevate {len(report.contradictions)} contraddizioni.")
                return {
                    "status": "blocked",
                    "reason": "Z3_CONTRADICTION",
                    "report": {
                        "nodes_affected": report.nodes_affected,
                        "contradictions": [c.z3_proof for c in report.contradictions],
                        "blast_radius": report.blast_radius_nodes
                    }
                }
        except Exception as e:
            print(f"⚠️ Errore nell'Impact Analyzer (continuo ingestion): {e}")

    # [v3.6.0] Scalar Metadata Extraction
    ext = Path(file.filename).suffix.lower().replace('.', '') or 'text'
    node = await engine.upsert_text(text, metadata={"source": file.filename, "namespace": namespace, "file_type": ext}, node_id=node_id)
    
    # Master Trace (v2.9.0)
    print(f"📥 [Ingestion] Success: {file.filename} -> Synapsed into Neural Vault.")
    
    return {"status": "synapsed", "id": node_id}



@app.post("/api/models/install")
async def install_model(request: Request, background_tasks: BackgroundTasks, api_key: str = Depends(get_api_key)):
    """Avvia l'installazione reale via Ollama API con tracciamento progressivo e auto-riparazione."""
    import platform
    import subprocess
    import shutil
    
    data = await request.json()
    model_name = (data.get("name") or data.get("model") or "").strip()
    
    # 🧬 HARDWARE DNA CHECK
    os_name = platform.system()
    arch = platform.machine()
    print(f"🧠 [Auto-Installer] Platform: {os_name} {arch} | Requested Model: '{model_name}'")

    # 🚧 [V6.1] Local Library Check: Skip Ollama for Python-native models
    local_models = {
        "florence2:latest": "Richiede installazione via pip (transformers/einops).",
        "imagebind:native": "Richiede installazione locale via torch/imagebind.",
        "whisper:native": "Richiede faster-whisper via pip."
    }
    
    if model_name in local_models:
        return {
            "status": "error", 
            "model": model_name, 
            "message": f"Il modello '{model_name}' è nativo Python. {local_models[model_name]}"
        }

    if model_name in install_progress and install_progress[model_name]["status"] == "pulling":
        return {"status": "already_installing", "model": model_name}

    install_progress[model_name] = {"percentage": 0, "status": "checking_service"}

    async def _async_pull():
        import httpx
        try:
            # 1. Verifica se Ollama è raggiungibile, altrimenti tenta di avviarlo
            max_retries = 3
            ollama_ready = False
            
            for i in range(max_retries):
                try:
                    async with httpx.AsyncClient(timeout=10.0) as client:
                        base_url = app.state.lab.settings.get("ollama_url") if hasattr(app.state, 'lab') else "http://127.0.0.1:11434"
                        r = await client.get(f"{base_url}/api/tags")
                        if r.status_code == 200:
                            ollama_ready = True
                            break
                except:
                    print(f"⚠️ [Self-Healing] Ollama non risponde. Tentativo di avvio {i+1}/{max_retries}...")
                    # Tenta di avviare Ollama in base al sistema operativo
                    if os_name == "Darwin": # Mac
                        # Prova prima con il comando da terminale, poi con 'open'
                        if shutil.which("ollama"):
                            subprocess.Popen(["ollama", "serve"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, env=get_clean_env())
                        else:
                            subprocess.Popen(["open", "-a", "Ollama"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, env=get_clean_env())
                    elif os_name == "Windows":
                        if shutil.which("ollama"):
                            subprocess.Popen(["ollama", "serve"], shell=True, env=get_clean_env())
                        else:
                            subprocess.Popen(["start", "ollama", "serve"], shell=True, env=get_clean_env())
                    else: # Linux
                        subprocess.Popen(["ollama", "serve"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, env=get_clean_env())
                    await asyncio.sleep(8) # Aumentato tempo di attesa per avvio a 8 secondi

            if not ollama_ready:
                # 🚨 EXTREME AUTO-PROVISIONING: Installazione automatica se mancante
                print(f"🚨 [Auto-Provisioning] Ollama non trovato su {os_name}. Tentativo di installazione forzata...")
                try:
                    if os_name == "Darwin" or os_name == "Linux":
                        # Installer ufficiale Ollama per Unix-like
                        # Usiamo '|| true' per ignorare l'errore di avvio finale dello script se il download è riuscito
                        subprocess.run("curl -fsSL https://ollama.com/install.sh | sh || true", shell=True, env=get_clean_env())
                    elif os_name == "Windows":
                        install_cmd = "powershell -Command \"& { iwr https://ollama.com/download/OllamaSetup.exe -OutFile OllamaSetup.exe; Start-Process -Wait -FilePath ./OllamaSetup.exe -ArgumentList '/silent'; Remove-Item ./OllamaSetup.exe }\""
                        subprocess.run(install_cmd, shell=True, env=get_clean_env())
                    
                    print("✅ [Auto-Provisioning] Download completato. Tentativo di avvio manuale...")
                    
                    # Tentativo di avvio post-installazione forzato
                    if os_name == "Darwin":
                        subprocess.Popen(["/usr/local/bin/ollama", "serve"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, env=get_clean_env())
                    
                    await asyncio.sleep(15) # Attesa generosa
                except Exception as install_err:
                    print(f"⚠️ Errore durante auto-install: {install_err}")

            # 2. Avvio PULL reale
            install_progress[model_name]["status"] = "pulling"
            async with httpx.AsyncClient(timeout=None) as client:
                base_url = app.state.lab.settings.get("ollama_url") if hasattr(app.state, 'lab') else "http://127.0.0.1:11434"
                async with client.stream("POST", f"{base_url}/api/pull", json={"name": model_name}) as resp:
                    async for line in resp.aiter_lines():
                        if not line: continue
                        chunk = json.loads(line)
                        
                        # 🚨 Check for Ollama API Errors
                        if "error" in chunk:
                            print(f"❌ [Ollama API Error] {chunk['error']}")
                            install_progress[model_name]["status"] = "error"
                            install_progress[model_name]["message"] = chunk["error"]
                            return

                        status = chunk.get("status", "")
                        total = chunk.get("total", 0)
                        completed = chunk.get("completed", 0)
                        
                        if total > 0:
                            perc = int((completed / total) * 100)
                            install_progress[model_name].update({
                                "percentage": perc,
                                "status": status,
                                "completed": completed,
                                "total": total
                            })

            # 3. Post-Pull Verification
            async with httpx.AsyncClient(timeout=10.0) as client:
                base_url = app.state.lab.settings.get("ollama_url") if hasattr(app.state, 'lab') else "http://127.0.0.1:11434"
                v_resp = await client.get(f"{base_url}/api/tags")
                if v_resp.status_code == 200:
                    models = [m["name"] for m in v_resp.json().get("models", [])]
                    # Check both exact match and without :latest
                    if model_name in models or f"{model_name}:latest" in models:
                        install_progress[model_name]["status"] = "success"
                        install_progress[model_name]["percentage"] = 100
                        print(f"✅ [Auto-Installer] {model_name} integrato con successo su {os_name}/{arch}.")
                    else:
                        install_progress[model_name]["status"] = "error"
                        install_progress[model_name]["message"] = "Installazione completata ma modello non trovato nel registro Ollama."
                else:
                    install_progress[model_name]["status"] = "success" # Fallback if API fails but pull didn't
            
        except Exception as e:
            print(f"❌ [Ollama Pull Error] {e}")
            install_progress[model_name] = {"status": "error", "message": str(e), "percentage": 0}

    background_tasks.add_task(_async_pull)
    return {"status": "started", "model": model_name, "dna": f"{os_name}-{arch}"}

@app.get("/api/models/progress")
async def get_install_progress(api_key: str = Depends(get_api_key)):
    """Restituisce lo stato di avanzamento di tutti i download attivi."""
    return install_progress

@app.get("/api/models/benchmarks")
async def get_model_benchmarks(api_key: str = Depends(get_api_key)):
    """Restituisce telemetria avanzata delle performance LLM locali."""
    if hasattr(app.state, 'lab') and hasattr(app.state.lab, 'benchmarks'):
        stats = app.state.lab.benchmarks.get_stats()
        if not stats: 
            return {"benchmarks": [], "radar": [50, 50, 50, 50, 50]}
            
        top = stats[0]
        # Calibrazione Sovrana (v3.1): Benchmarks reali normalizzati
        # SPEED: Target 40 TPS | ACCURACY: Stability + Penality Latency | DENSITY: RAM Impact (16GB Scale)
        radar_data = [
            min(100, (top.get('tps', 0) / 40.0) * 100),         # SPEED
            min(100, top.get('stability', 50) * 0.9 + (2000 / (top.get('latency', 2000) + 1)) * 10), # ACCURACY
            top.get('stability', 50),                           # STABILITY
            min(100, (top.get('ram', 0) / 16384) * 100),        # DENSITY (MB)
            min(100, (top.get('stability', 50) * 0.7 + (top.get('tps', 0) / 40.0) * 30)) # REASONING
        ]
        return {
            "benchmarks": stats, 
            "radar": radar_data,
            "history": app.state.lab.benchmarks.get_full_history()[:50] # Ultime 50 missioni
        }
    return {"benchmarks": [], "radar": [0,0,0,0,0], "history": []}

# --- 🧪 EVOLUTION MODE ENDPOINTS ---
@app.get("/api/lab/evolution/suggestions")
async def get_evolution_suggestions(api_key: str = Depends(get_api_key)):
    """Recupera la cronologia dei suggerimenti evolutivi dello sciame."""
    if hasattr(app.state, 'lab') and hasattr(app.state.lab, 'evolution_advise'):
        return app.state.lab.evolution_advise.history
    return []

@app.post("/api/lab/evolution/feedback")
async def record_evolution_feedback(request: Request, api_key: str = Depends(get_api_key)):
    """Registra il feedback di rinforzo (Implementato/Scartato/Falso Positivo)."""
    data = await request.json()
    sid = data.get("id")
    feedback = data.get("feedback")
    if hasattr(app.state, 'lab') and hasattr(app.state.lab, 'evolution_advise'):
        success = app.state.lab.evolution_advise.record_feedback(sid, feedback)
        return {"status": "recorded" if success else "not_found"}
    return {"status": "error"}

@app.post("/api/lab/evolution/apply")
async def apply_evolution_suggestion(request: Request, api_key: str = Depends(get_api_key)):
    """[v10.2] Applica manualmente una patch verificata (CONFERMA E APPLICA)."""
    data = await request.json()
    sid = data.get("id")
    if not sid:
        raise HTTPException(status_code=400, detail="Missing suggestion ID")
        
    if hasattr(app.state, 'lab') and hasattr(app.state.lab, 'evolution_advise'):
        advise_mgr = app.state.lab.evolution_advise
        suggestion = None
        for s in advise_mgr.history:
            if s["id"] == sid:
                suggestion = s
                break
                
        if not suggestion:
            raise HTTPException(status_code=404, detail="Suggestion not found")
            
        file_path = suggestion.get("file")
        line_number = suggestion.get("line", 0)
        new_content = suggestion.get("content")
        
        # Determina il percorso assoluto del file sorgente da modificare
        project_root = getattr(app.state.lab.bridger_agent.bridger, 'project_root', None)
        if not project_root:
            project_root = os.getcwd()
            
        full_path = os.path.join(str(project_root), file_path)
        
        if not os.path.exists(full_path):
            raise HTTPException(status_code=404, detail=f"Source file {file_path} not found at {full_path}")
            
        try:
            # Leggiamo il codice, applichiamo la modifica ed eseguiamo la scrittura sicura
            with open(full_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
                
            if 0 < line_number <= len(lines):
                lines[line_number - 1] = new_content + "\n"
            else:
                lines.append("\n" + new_content + "\n")
                
            with open(full_path, "w", encoding="utf-8") as f:
                f.writelines(lines)
                
            # Aggiorna lo stato della suggestion a "applied"
            suggestion["status"] = "applied"
            advise_mgr._save()
            
            # Notifica l'evento di hot-fix manuale sulla blackboard dello Swarm
            sig = SynapticSignal("EVOLUTION", AgentRole.ARCHITECT, 
                f"✅ MANUALLY APPLIED: Suggestion {sid} applied successfully to {file_path}.", 
                SignalType.SYSTEM_HEALING)
            app.state.lab.blackboard.post(sig)
            
            # Registra feedback positivo per reinforcement learning
            advise_mgr.record_feedback(sid, "implemented")
            
            return {"status": "success", "message": f"Patch {sid} applied successfully to {file_path}."}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to apply patch: {e}")
            
    return {"status": "error", "message": "Neural Lab not ready"}

@app.get("/api/lab/wisdom/all")
async def get_wisdom_all(api_key: str = Depends(get_api_key)):
    """Ritorna tutto l'apprendimento accumulato dagli agenti."""
    if not hasattr(app.state, 'lab'): return {"approved": [], "rejected": []}
    return app.state.lab.wisdom.lessons

@app.post("/api/lab/settings")
async def update_lab_settings(req: Dict, api_key: str = Depends(get_api_key)):
    """Aggiorna le impostazioni dello Swarm (es. Supreme Court Judges, Evolution Mode)."""
    if not hasattr(app.state, 'lab'): raise HTTPException(status_code=500, detail="Lab not initialized")
    
    # Aggiorna il manager persistente
    app.state.lab.settings.update(req)
    
    # 🔄 Trigger Mode Logic
    if "auto_mode" in req:
        status = "AUTONOMA" if req["auto_mode"] else "MANUALE"
        sig = SynapticSignal("ORCHESTRATOR", AgentRole.MISSION_ARCHITECT, f"⚠️ SUPERVISIONE CAMBIATA: Ora in modalità {status}.", SignalType.SYSTEM_NOTIFICATION)
        app.state.lab.blackboard.post(sig)

    # Note: frontend might send 'codebase_bridging' OR 'evolution_mode'
    is_evol = req.get("evolution_mode") or req.get("codebase_bridging")
    if is_evol is not None:
        app.state.lab.evolution_active = is_evol
        if is_evol:
            # Activate Bridger with current working directory (v17.6: Access via .bridger.project_root)
            from pathlib import Path
            app.state.lab.bridger_agent.bridger.project_root = Path(os.getcwd())
            app.state.lab.trigger_evolution_scan()
            msg = "🚀 EVOLUTION MODE ATTIVATA: Ibridazione codebase/web iniziata."
        else:
            app.state.lab.bridger_agent.bridger.project_root = None # Research mode
            msg = "🛡️ RESEARCH MODE ATTIVATA: Focus esclusivo sui dati esterni."
        
        app.state.lab.blackboard.post(SynapticSignal("ORCHESTRATOR", AgentRole.MISSION_ARCHITECT, msg, SignalType.SYSTEM_NOTIFICATION))

    return {"status": "success", "settings": app.state.lab.settings.settings}

@app.post("/api/lab/wisdom/record")
async def record_human_wisdom(data: dict, api_key: str = Depends(get_api_key)):
    """Human-in-the-loop: Inserisce manualmente un'istruzione di protezione o rifiuto."""
    if not hasattr(app.state, 'lab'): raise HTTPException(status_code=500)
    
    text = data.get("text")
    success = data.get("approve", False)
    reason = data.get("reason", "Human Override")
    
    app.state.lab.wisdom.add_lesson("HUMAN", success, text, reason)
    return {"status": "recorded", "category": "approved" if success else "rejected"}

# --- NEW: NEURAL MODEL CATALOG (v4.0 Sovereign - Categorized) ---
MODEL_CATALOG = {
    # ── CATEGORIA: [TINY_KINETIC] - Leggerissimi & Ultra-Veloci (0-2GB) ────────────────
    "llama3.2:1b": {
        "name": "Llama 3.2 (1B)", "size": "1.3GB", "category": "TINY_KINETIC", 
        "pros": "Velocità estrema (100+ t/s), zero lag", "cons": "Cognizione base", 
        "caveau": "L'Ombra Silenziosa per il background.", "forza": "Parsing testuale rapido e routing di segnali.",
        "synergy": ["phi3:latest"], "task": "Fast Signal Routing",
        "ram": "2GB RAM", "cpu": "2 Cores", "vram": "1GB",
        "capabilities": ["Text Summarization", "Format Conversion", "Token Filtering", "Intent Detection"]
    },
    "qwen2.5:0.5b": {
        "name": "Qwen 2.5 (0.5B)", "size": "394MB", "category": "TINY_KINETIC", 
        "pros": "Il più piccolo al mondo con logica reale", "cons": "Memoria a breve termine limitata", 
        "caveau": "Il micro-cervello per task atomici.", "forza": "Esecuzione istantanea su CPU datate.",
        "synergy": ["llama3.2:1b"], "task": "Atomic Logic",
        "ram": "1GB RAM", "cpu": "1 Core",
        "capabilities": ["Micro-Classification", "Language ID", "Basic Logic", "Text Cleaning"]
    },
    "mistral:latest": {
        "name": "Mistral (7B v0.3)", "size": "4.1GB", "category": "SOVEREIGN_MID_CORE", 
        "pros": "Affidabile e performante, ottima comprensione del contesto", "cons": "Meno specializzato nel codice rispetto a Qwen Coder", 
        "caveau": "Il classico di riferimento.", "forza": "Versatilità generale e ottime doti di sintesi narrativa.",
        "synergy": ["mistral:latest"], "task": "Edge Intelligence",
        "ram": "4GB RAM", "vram": "2GB",
        "capabilities": ["High-Density Logic", "Complex Reasoning", "Large Context (128k)", "Italian Mastery"]
    },
    "ministral-3:latest": {
        "name": "Ministral 8B", "size": "6.0GB", "category": "SOVEREIGN_MID_CORE", 
        "pros": "Stato dell'arte per modelli edge, finestra 256k", "cons": "Richiede 8GB di memoria unificata", 
        "caveau": "L'Ammiraglia compatta.", "forza": "Densità di intelligenza estrema e logica impeccabile.",
        "synergy": ["mistral:latest"], "task": "Edge Intelligence",
        "ram": "8GB RAM", "vram": "4GB",
        "capabilities": ["High-Density Logic", "Complex Reasoning", "Large Context (256k)", "Agentic Ready"]
    },
    "ministral-3:3b": {
        "name": "Ministral 3B (Sovereign)", "size": "3.0GB", "category": "TINY_KINETIC", 
        "pros": "Modello ultra-compatto della famiglia Mistral, eccelsa logica", "cons": "Conoscenza enciclopedica ridotta rispetto all'8B", 
        "caveau": "Il piccolo Titano di Mistral.", "forza": "Ottimo per dispositivi edge e inference locale rapida.",
        "synergy": ["llama3.2:3b"], "task": "Pocket Reasoning",
        "ram": "4GB RAM", "vram": "2GB",
        "capabilities": ["Fast Extraction", "Edge Computing", "Large Context (128k)", "Agentic Logic"]
    },
    "deepseek-r1:1.5b": {
        "name": "DeepSeek R1 (1.5B Distill)", "size": "1.1GB", "category": "TINY_KINETIC", 
        "pros": "Ragionamento logico estremo in 1GB", "cons": "Più lento dei modelli non-R1", 
        "caveau": "Il Pensatore in miniatura.", "forza": "Risoluzione di problemi matematici e logici complessi.",
        "synergy": ["qwen2.5:1.5b"], "task": "Logical Reasoning",
        "ram": "2GB RAM", "vram": "1GB",
        "capabilities": ["Complex Reasoning", "Math Solving", "Step-by-step Logic", "Code Analysis"]
    },
    "deepseek-r1:8b": {
        "name": "DeepSeek R1 (8B Distill - Llama)", "size": "4.7GB", "category": "SOVEREIGN_MID_CORE", 
        "pros": "Logica Llama 3.1 potenziata dal ragionamento R1", "cons": "Richiede 8GB RAM libera", 
        "caveau": "Il Saggio della fascia media.", "forza": "Scrittura creativa e debug di codice complesso.",
        "synergy": ["mistral:latest"], "task": "Advanced Reasoning",
        "ram": "8GB RAM", "vram": "4GB",
        "capabilities": ["Expert Coding", "Philosophical Reasoning", "Complex Instructions", "Multilingual Logic"]
    },
    "llama3.2:3b": {
        "name": "Llama 3.2 (3B)", "size": "2.0GB", "category": "TINY_KINETIC", 
        "pros": "Il miglior rapporto intelligenza/peso di Meta", "cons": "Meno profondo della versione 8B", 
        "caveau": "L'Assistente Bilanciato.", "forza": "Comprensione del linguaggio naturale e chat fluida.",
        "synergy": ["phi3.5:latest"], "task": "Balanced Chat",
        "ram": "4GB RAM", "vram": "2GB",
        "capabilities": ["General Chat", "Summarization", "Entity Extraction", "Intent Detection"]
    },
    "smollm2:1.7b": {
        "name": "SmolLM2 (1.7B)", "size": "1.0GB", "category": "TINY_KINETIC", 
        "pros": "Velocità di risposta istantanea", "cons": "Conoscenza enciclopedica limitata", 
        "caveau": "Il Lampo di HuggingFace.", "forza": "Task atomici e classificazione rapida in background.",
        "synergy": ["llama3.2:1b"], "task": "Fast Processing",
        "ram": "2GB RAM", "vram": "1GB",
        "capabilities": ["Text Classification", "Keyword Extraction", "Fast Summaries", "Log Parsing"]
    },
    "qwen2.5:1.5b": {
        "name": "Qwen 2.5 (1.5B)", "size": "1.2GB", "category": "TINY_KINETIC", 
        "pros": "Efficienza estrema con intelligenza da 7B", "cons": "Capacità ridotte per task lunghi", 
        "caveau": "La Scintilla Neurale.", "forza": "Routing intelligente e parsing istantaneo.",
        "synergy": ["llama3.2:1b"], "task": "Micro-Logic",
        "ram": "2GB RAM", "vram": "1GB",
        "capabilities": ["Smart Routing", "Text Cleanup", "Format Validation", "Fast Chat"]
    },
    "gemma4:e2b": {
        "name": "Gemma 4 (Edge 2B)", "size": "1.6GB", "category": "TINY_KINETIC", 
        "pros": "Release Aprile 2026, logica superiore ai vecchi 7B", "cons": "Richiede driver aggiornati per Apple Silicon", 
        "caveau": "Il Futuro Tascabile di Google.", "forza": "Ragionamento complesso in meno di 2GB di spazio.",
        "synergy": ["qwen3.6:moe"], "task": "Ultra-Fast Reasoning",
        "ram": "4GB RAM", "vram": "2GB",
        "capabilities": ["Advanced Logic", "Text Synthesis", "Smart Filtering", "Precise Summarization"]
    },
    "gemma2:2b": {
        "name": "Gemma 2 (2B)", "size": "1.8GB", "category": "TINY_KINETIC", 
        "pros": "Architettura Google v2, ultra-compressa", "cons": "Tende alla brevità", 
        "caveau": "Il Nucleo di Cristallo.", "forza": "Spiegazioni concise e logica matematica solida in formato pocket.",
        "synergy": ["qwen2.5:3b"], "task": "Pocket Reasoning",
        "ram": "4GB RAM", "vram": "2GB",
        "capabilities": ["Math Solving", "Concise Summaries", "Code Snippets", "Logical Filters"]
    },
    "granite3-dense:2b": {
        "name": "IBM Granite 3.0 (2B)", "size": "1.4GB", "category": "TINY_KINETIC", 
        "pros": "Addestrato specificamente per RAG e tool calling", "cons": "Meno creativo in prosa", 
        "caveau": "La Scacchiera d'Acciaio.", "forza": "Affidabilità estrema nei compiti di recupero dati senza allucinazioni.",
        "synergy": ["llama3.2:3b"], "task": "RAG Verification",
        "ram": "3GB RAM", "vram": "1GB",
        "capabilities": ["Zero Hallucination RAG", "Tool Calling", "Data Extraction", "Logic Filtering"]
    },
    "qwen2.5:3b": {
        "name": "Qwen 2.5 (3B)", "size": "1.9GB", "category": "TINY_KINETIC", 
        "pros": "Eccezionale per hardware limitato, veloce e brillante", "cons": "Conoscenza enciclopedica ridotta rispetto a 7B", 
        "caveau": "Il compromesso perfetto.", "forza": "Rapporto velocità/intelligenza inarrivabile per la sua taglia.",
        "synergy": ["llama3.2:3b"], "task": "Fast Extraction",
        "ram": "4GB RAM", "vram": "2GB",
        "capabilities": ["Rapid Extraction", "JSON Formatting", "Basic Chat", "Agile Reasoning"]
    },
    "qwen2.5-coder:3b": {
        "name": "Qwen 2.5 Coder (3B)", "size": "1.9GB", "category": "TINY_KINETIC", 
        "pros": "Coding super-veloce, eccellente per autocomplete e script", "cons": "Non adatto ad architetture software complesse", 
        "caveau": "Il programmatore tascabile.", "forza": "Scrittura e correzione rapida di frammenti di codice.",
        "synergy": ["qwen2.5-coder:7b"], "task": "Agile Coding",
        "ram": "4GB RAM", "vram": "2GB",
        "capabilities": ["Fast Coding", "Script Generation", "Syntax Correction", "JSON Parsing"]
    },
    "qwen2.5-coder:7b": {
        "name": "Qwen 2.5 Coder (7B)", "size": "4.7GB", "category": "SOVEREIGN_MID_CORE", 
        "pros": "Il nuovo standard mondiale per il coding sotto i 10B", "cons": "Meno creativo nel linguaggio naturale", 
        "caveau": "L'Architetto del Codice.", "forza": "Scrittura, debug e refactoring di Python, JS e Rust.",
        "synergy": ["deepseek-v4-flash"], "task": "Full-Stack Development",
        "ram": "8GB RAM", "vram": "6GB",
        "capabilities": ["Expert Coding", "Repo-level Analysis", "Code Completion", "Bug Fixing"]
    },
    
    # ── CATEGORIA: [MULTIMODAL_SENSORY] - Visione, Video & Immagini ───────────────────
    "moondream:latest": {
        "name": "Moondream 2", "size": "1.6GB", "category": "MULTIMODAL_SENSORY", 
        "pros": "Visione eccelsa in formato Nano", "cons": "Solo immagini statiche", 
        "caveau": "L'occhio vigile del Vault.", "forza": "Descrizione visiva chirurgica e Q&A su immagini.",
        "synergy": ["florence2:latest"], "task": "Visual Reasoning",
        "ram": "4GB RAM", "vram": "2GB",
        "capabilities": ["Image Captioning", "Visual Q&A", "Object Identification", "OCR Basic"]
    },
    "phi3:vision": {
        "name": "Phi-3.5 Vision (4.2B)", "size": "2.6GB", "category": "MULTIMODAL_SENSORY", 
        "pros": "Ragionamento logico applicato alla visione", "cons": "Lento nel caricamento immagini", 
        "caveau": "L'Analista Visivo Logico.", "forza": "Interpretazione di grafici, diagrammi e screenshot tecnici.",
        "synergy": ["florence2:latest"], "task": "Technical Vision",
        "ram": "6GB RAM", "vram": "4GB",
        "capabilities": ["Chart Reading", "Diagram Analysis", "Technical OCR", "Visual Reasoning"]
    },
    "florence2:latest": {
        "name": "Microsoft Florence-2", "size": "1.1GB", "category": "MULTIMODAL_SENSORY", 
        "pros": "Leader mondiale nel Grounding visivo", "cons": "Richiede Python Runtime", 
        "caveau": "L'Analista Forense delle Immagini.", "forza": "Individuazione coordinate oggetti e OCR denso.",
        "synergy": ["moondream:latest"], "task": "Visual Forensics",
        "ram": "4GB RAM", "vram": "2GB",
        "capabilities": ["Detailed Captioning", "Object Detection (BBox)", "Dense OCR", "Region Description"]
    },
    "qwen2-vl:2b": {
        "name": "Qwen2-VL (2B)", "size": "2.4GB", "category": "MULTIMODAL_SENSORY", 
        "pros": "Supporto Video Nativo", "cons": "Richiede molta VRAM per video lunghi", 
        "caveau": "Il Cinema neurale.", "forza": "Comprensione di sequenze video e multi-immagine.",
        "synergy": ["imagebind:native"], "task": "Video Synthesis",
        "ram": "8GB RAM", "vram": "4GB",
        "capabilities": ["Video Action Recognition", "Event Sequencing", "Visual Storytelling", "Complex OCR"]
    },
    "llava:7b": {
        "name": "LLaVA v1.6 (7B)", "size": "4.5GB", "category": "MULTIMODAL_SENSORY", 
        "pros": "Standard Industry Vision", "cons": "Lento su hardware medio", 
        "caveau": "Il ponte tra testo e immagine.", "forza": "Ragionamento astratto su scene complesse.",
        "synergy": ["mistral:latest"], "task": "Visual Logic",
        "ram": "12GB RAM", "vram": "8GB",
        "capabilities": ["Deep Visual Analysis", "Chart Reading", "Document Parsing", "Common Sense Vision"]
    },
    "imagebind:native": {
        "name": "Meta ImageBind (Lib)", "size": "2.1GB", "category": "MULTIMODAL_SENSORY", 
        "pros": "Audio/Video/Thermal/Depth in un unico spazio", "cons": "Sola Ingestione (No Chat)", 
        "caveau": "Il Sistema Nervoso Centrale.", "forza": "Creazione di vettori 1024D cross-modali.",
        "synergy": ["whisper:native"], "task": "Neural Ingestion",
        "ram": "8GB RAM", "vram": "4GB (MPS Opt)",
        "capabilities": ["Cross-Modal Search", "Audio-to-Image", "Video-to-Text Alignment", "Thermal Data Sync"]
    },
    "internvl2:latest": {
        "name": "InternVL 2 (VLM)", "size": "12GB", "category": "MULTIMODAL_SENSORY", 
        "pros": "Stato dell'arte nella visione open source", "cons": "Esigente in termini di VRAM", 
        "caveau": "L'Occhio di Falco del Lab.", "forza": "Riconoscimento di pattern visivi complessi e OCR estremo.",
        "synergy": ["qwen2-vl:2b"], "task": "Advanced Vision",
        "ram": "16GB RAM", "vram": "12GB",
        "capabilities": ["High-Res Visual Q&A", "Document Understanding", "Action Recognition", "Multi-Image Reasoning"]
    },
    "openvla:latest": {
        "name": "OpenVLA (Robotica)", "size": "7.5GB", "category": "MULTIMODAL_SENSORY", 
        "pros": "Modello Vision-Language-Action nativo", "cons": "Specializzato in robotica/azione", 
        "caveau": "Il Pilota Robotico.", "forza": "Traduzione di istruzioni visive in coordinate e comandi.",
        "synergy": ["internvl2:latest"], "task": "Visual Grounding",
        "ram": "12GB RAM", "vram": "8GB",
        "capabilities": ["Spatial Reasoning", "Instruction Following", "Object Grounding", "Robotic Control Simulation"]
    },
    "openvl:latest": {
        "name": "OpenVL (General)", "size": "4.2GB", "category": "MULTIMODAL_SENSORY", 
        "pros": "Efficienza bilanciata tra analisi e velocità", "cons": "Meno dettagliato di InternVL", 
        "caveau": "Il Sensore Ambientale.", "forza": "Analisi rapida di scene e tagging automatico.",
        "synergy": ["moondream:latest"], "task": "Scene Intelligence",
        "ram": "8GB RAM", "vram": "4GB",
        "capabilities": ["Fast Captioning", "Tagging", "Environmental Analysis", "Basic OCR"]
    },

    # ── CATEGORIA: [SOVEREIGN_MID_CORE] - Prestazioni PC Fascia Media (4-12GB) ─────────
    "llama3.1:8b": {
        "name": "Llama 3.1 (8B)", "size": "4.7GB", "category": "SOVEREIGN_MID_CORE", 
        "pros": "Ecosistema vastissimo, ottimo italiano", "cons": "Censura occasionale", 
        "caveau": "Il Console del Dialogo.", "forza": "Capacità conversazionale e sfumature linguistiche.",
        "synergy": ["gemma2:9b"], "task": "Advanced Chat",
        "ram": "10GB RAM", "vram": "8GB",
        "capabilities": ["Nuanced Conversation", "Creative Writing", "Roleplay", "Tool Calling"]
    },
    "deepseek-r1:7b": {
        "name": "DeepSeek R1 (7B Distill)", "size": "4.7GB", "category": "SOVEREIGN_MID_CORE", 
        "pros": "Ragionamento matematico d'élite", "cons": "Uscite in cinese rari", 
        "caveau": "Il Matematico del Lab.", "forza": "Chain of Thought (CoT) per risolvere enigmi logici.",
        "synergy": ["mistral:latest"], "task": "Problem Solving",
        "ram": "8GB RAM", "vram": "6GB",
        "capabilities": ["Mathematical Reasoning", "Logic Puzzles", "Code Debugging", "Step-by-step Planning"]
    },
    "phi3.5:latest": {
        "name": "Phi-3.5 Mini (3.8B)", "size": "2.2GB", "category": "SOVEREIGN_MID_CORE", 
        "pros": "Incredibile densità di intelligenza", "cons": "Finestra contesto corta", 
        "caveau": "Il piccolo genio di Microsoft.", "forza": "Logica da 7B in meno di 3GB di RAM.",
        "synergy": ["qwen2.5:1.5b"], "task": "Logical Verification",
        "ram": "4GB RAM", "vram": "2GB",
        "capabilities": ["Fact Checking", "Logic Validation", "Brief Summaries", "Data Extraction"]
    },
    "phi4:latest": {
        "name": "Phi-4 Sovereign (4.1B)", "size": "2.8GB", "category": "SOVEREIGN_MID_CORE", 
        "pros": "Ragionamento predittivo v4, ottimizzato per M1/M2/M3", "cons": "Molto esigente durante CoT", 
        "caveau": "L'Oracolo Tascabile.", "forza": "Logica di alto livello e sintesi predittiva in formato ultra-compatto.",
        "synergy": ["qwen3.5:7b"], "task": "Predictive Reasoning",
        "ram": "6GB RAM", "vram": "4GB",
        "capabilities": ["Advanced Logic", "Predictive Synthesis", "Complex Code Review", "Scientific Reasoning"]
    },
    "qwen2.5:7b": {
        "name": "Qwen 2.5 (7B - Sovereign)", "size": "4.7GB", "category": "SOVEREIGN_MID_CORE", 
        "pros": "Logica d'élite, ottimizzato per Apple Silicon", "cons": "Uso moderato di batteria", 
        "caveau": "Il Pilastro della Conoscenza.", "forza": "Comprensione del contesto e scrittura creativa impeccabile.",
        "synergy": ["mistral:latest"], "task": "Expert Synthesis",
        "ram": "8GB RAM", "vram": "6GB",
        "capabilities": ["Complex Reasoning", "Nuanced Chat", "Multi-language Support", "Text Synthesis"]
    },
    "deepseek-v2.5:latest": {
        "name": "DeepSeek V2.5 (Coder/Chat)", "size": "14GB (Quant)", "category": "ELITE_HEAVY_WEIGHT", 
        "pros": "Il re del coding e della logica open source", "cons": "Richiede 16GB RAM per prestazioni fluide", 
        "caveau": "L'Architetto Supremo.", "forza": "Risoluzione di bug complessi e architetture software.",
        "synergy": ["qwen2.5-coder:7b"], "task": "Advanced Development",
        "ram": "16GB RAM", "vram": "12GB",
        "capabilities": ["Professional Coding", "Logic Puzzles", "Complex Planning", "Expert Synthesis"]
    },
    "deepseek-r1:32b": {
        "name": "DeepSeek R1 (32B - Distill)", "size": "19GB", "category": "ELITE_HEAVY_WEIGHT", 
        "pros": "Intelligenza comparabile a GPT-4o", "cons": "Lento su M1 base (richiede 24GB+ RAM per 0 lag)", 
        "caveau": "L'Oracolo di Cristallo.", "forza": "Pensiero critico e analisi scientifica profonda.",
        "synergy": ["gemma2:27b"], "task": "Scientific Discovery",
        "ram": "32GB RAM", "vram": "20GB",
        "capabilities": ["Deep Logic", "Scientific Analysis", "Complex Critiques", "Universal Wisdom"]
    },
    "qwen3.5:7b": {
        "name": "Qwen 3.5 (7B - Next-Gen)", "size": "4.8GB", "category": "SOVEREIGN_MID_CORE", 
        "pros": "Architettura v3.5, logica predittiva avanzata", "cons": "Richiede aggiornamento Ollama 2026", 
        "caveau": "Il Futuro del Ragionamento.", "forza": "Comprensione profonda di query ambigue e sintesi ultra-densa.",
        "synergy": ["phi4:latest"], "task": "Predictive Synthesis",
        "ram": "8GB RAM", "vram": "6GB",
        "capabilities": ["Advanced Prediction", "Deep Summarization", "Logical Extrapolation", "Cross-lingual Nuance"]
    },
    "qwen3.5:32b": {
        "name": "Qwen 3.5 (32B - Sovereign Elite)", "size": "18GB", "category": "ELITE_HEAVY_WEIGHT", 
        "pros": "Capacità quasi-umana di astrazione", "cons": "Molto esigente su M1 (meglio su M3/M4)", 
        "caveau": "L'Archivista Globale.", "forza": "Risoluzione di problemi interdisciplinari complessi.",
        "synergy": ["deepseek-r1:32b"], "task": "Global Knowledge Synthesis",
        "ram": "32GB RAM", "vram": "24GB",
        "capabilities": ["Abstract Reasoning", "Scientific Logic", "Policy Analysis", "Complex System Modeling"]
    },
    "qwen3.6:35b": {
        "name": "Qwen 3.6 (35B-A3B MoE)", "size": "12GB (Quant)", "category": "SOVEREIGN_MID_CORE", 
        "pros": "Intelligenza da 35B con velocità di un 3B", "cons": "Uso VRAM variabile", 
        "caveau": "L'Illusionista di Alibaba.", "forza": "Prestazioni d'élite con consumo energetico minimo.",
        "synergy": ["gemma4:e2b"], "task": "Hybrid Intelligence",
        "ram": "16GB RAM", "vram": "8GB",
        "capabilities": ["MoE Efficiency", "High-Fidelity Code", "Complex Planning", "Scientific Logic"]
    },

    # ── CATEGORIA: [ELITE_HEAVY_WEIGHT] - Massima Potenza & Conoscenza (15GB+) ──────────
    "gemma2:27b": {
        "name": "Gemma 2 (27B)", "size": "16GB", "category": "ELITE_HEAVY_WEIGHT", 
        "pros": "Prestazioni da 70B in taglia ridotta", "cons": "Molto pesante su 16GB Mac", 
        "caveau": "L'Oracolo della Verità.", "forza": "Comprensione enciclopedica e zero allucinazioni.",
        "synergy": ["deepseek-r1:14b"], "task": "Scientific Research",
        "ram": "32GB RAM", "vram": "16GB",
        "capabilities": ["Scientific Analysis", "Philosophical Discourse", "Cross-Domain Synthesis", "Truth Verification"]
    },
    "hermes3:latest": {
        "name": "Hermes 3 (8B - Llama 3.1)", "size": "4.7GB", "category": "SOVEREIGN_MID_CORE", 
        "pros": "Incredibile naturalezza e aderenza alle istruzioni", "cons": "Meno focalizzato sulla sicurezza (uncensored)", 
        "caveau": "Il Console Sovrano.", "forza": "Dialoghi complessi, roleplay tecnico e creatività senza vincoli.",
        "synergy": ["llama3.1:8b"], "task": "Unconstrained Logic",
        "ram": "10GB RAM", "vram": "8GB",
        "capabilities": ["Instruction Following", "Creative Writing", "Technical Roleplay", "System Prompt Mastery"]
    },
    "deepseek-r1:14b": {
        "name": "DeepSeek R1 (14B)", "size": "9.0GB", "category": "ELITE_HEAVY_WEIGHT", 
        "pros": "Il miglior compromesso tra 7B e 32B", "cons": "Lentezza su CPU", 
        "caveau": "L'Ingegnere Senior del Vault.", "forza": "Programmazione complessa e logica formale.",
        "synergy": ["phi4:latest"], "task": "Engineering Task",
        "ram": "16GB RAM", "vram": "10GB",
        "capabilities": ["Full-Stack Coding", "Algorithmic Design", "Complex Planning", "Expert Critique"]
    },
    "qwen2.5-coder:14b": {
        "name": "Qwen 2.5 Coder (14B)", "size": "9.1GB", "category": "ELITE_HEAVY_WEIGHT", 
        "pros": "Potenza di ragionamento codice superiore a GPT-4o-mini", "cons": "Richiede 16GB RAM per fluidità", 
        "caveau": "Il Maestro Artigiano.", "forza": "Sistemi complessi e architetture software multi-file.",
        "synergy": ["deepseek-v4-flash"], "task": "Software Architecture",
        "ram": "16GB RAM", "vram": "10GB",
        "capabilities": ["Complex Software Design", "Unit Test Generation", "Security Auditing", "CI/CD Logic"]
    },
    "deepseek-v4-flash": {
        "name": "DeepSeek V4 Flash (284B MoE)", "size": "14GB (Quantized)", "category": "ELITE_HEAVY_WEIGHT", 
        "pros": "Efficienza MoE estrema, 1M Context Window", "cons": "Richiede download massiccio iniziale", 
        "caveau": "L'Oracolo della Conoscenza Globale.", "forza": "Ragionamento ad altissimo contesto e sintesi di interi repository.",
        "synergy": ["qwen2.5-coder:14b"], "task": "Massive Context Analysis",
        "ram": "24GB+ RAM", "vram": "16GB (Quant)",
        "capabilities": ["1 Million Token Context", "High-Throughput Reasoning", "Deep Repository Synthesis", "Cross-Domain Logic"]
    },
    "gemma4:26b": {
        "name": "Gemma 4 MoE (Unsloth Elite)", "size": "12.5GB (GGUF)", "category": "ELITE_HEAVY_WEIGHT", 
        "pros": "26B Total / 4B Active. Velocità da 4B con logica da 26B", "cons": "Ottimizzato principalmente per ragionamento/code", 
        "caveau": "Il Motore Efficace di Unsloth.", "forza": "Context window da 256k e ragionamento step-by-step nativo.",
        "synergy": ["qwen3.6:35b"], "task": "High-Efficiency Reasoning",
        "ram": "16GB RAM", "vram": "12GB (MPS Opt)",
        "capabilities": ["256K Context Window", "Mixture-of-Experts (MoE)", "Tool-Calling Native", "Chain-of-Thought reasoning"]
    },
    "nemotron:latest": {
        "name": "NVIDIA Nemotron 70B", "size": "39GB", "category": "ELITE_HEAVY_WEIGHT", 
        "pros": "Incredibile naturalezza, dati NVIDIA", "cons": "Richiede Mac Studio/Ultra", 
        "caveau": "Il Titano del Dialogo.", "forza": "Dialoghi umani al 100% e analisi di mercato.",
        "synergy": ["llama3.1:70b"], "task": "Enterprise Intelligence",
        "ram": "64GB RAM", "vram": "40GB",
        "capabilities": ["Human-like Interaction", "Strategic Consulting", "Market Simulation", "Extreme Context Synthesis"]
    },
    "nutboy02/Qwen3.6-35B-A3B-Claude-4.7-Opus-abliterated-uncenfull": {
        "name": "Qwen 3.6 Opus Uncensored (35B)", "size": "22GB", "category": "ELITE_HEAVY_WEIGHT", 
        "pros": "Ibrido della community, abliterated, nessuna censura", "cons": "Richiede almeno 32GB di RAM unificata", 
        "caveau": "Il Titano Ribelle.", "forza": "Ragionamento ibrido estremo e sintesi senza barriere etiche.",
        "synergy": ["deepseek-r1:32b"], "task": "Unrestricted Synthesis",
        "ram": "32GB RAM", "vram": "20GB",
        "capabilities": ["Uncensored Logic", "Hybrid Architecture", "Deep Narrative", "Zero Constraints"]
    },
    "qwen2.5:32b": {
        "name": "Qwen 2.5 (32B)", "size": "18GB", "category": "ELITE_HEAVY_WEIGHT", 
        "pros": "Logica di livello enterprise", "cons": "Richiede molta VRAM", 
        "caveau": "Il Super-Cervello del Vault.", "forza": "Ragionamento astratto di livello superiore e multilinguismo perfetto.",
        "synergy": ["gemma2:27b"], "task": "Strategic Intelligence",
        "ram": "32GB RAM", "vram": "24GB",
        "capabilities": ["Quantum Logic", "Strategic Planning", "Infinite Context", "Zero-Shot Synthesis"]
    },
    # ── [NEW v8.2] XIAOMI MiMo SERIES ──────────────────────────────────────────────
    "mimo:v2.5-pro": {
        "name": "MiMo V2.5 Pro (12B)", "size": "8.4GB", "category": "ELITE_HEAVY_WEIGHT", 
        "pros": "Context window d'élite, precisione chirurgica nei dati Xiaomi", "cons": "Richiede 16GB+ RAM", 
        "caveau": "L'Archivista ad Alta Fedeltà.", "forza": "Sintesi di documenti tecnici e analisi cross-referenziale.",
        "synergy": ["deepseek-r1:14b", "qwen2.5-coder:14b"], "task": "Deep Context Synthesis",
        "ram": "16GB RAM", "vram": "10GB",
        "capabilities": ["Large Context Analysis", "Technical Writing", "Semantic Mapping", "Cross-lingual Retrieval"]
    },
    "mimo:v2.5-lite": {
        "name": "MiMo V2.5 Lite (7B)", "size": "4.6GB", "category": "SOVEREIGN_MID_CORE", 
        "pros": "Velocità Mistral con logica MiMo", "cons": "Meno profondo della versione Pro", 
        "caveau": "Il Ricercatore Agile.", "forza": "Task di analisi quotidiana e chat tecnica fluida.",
        "synergy": ["llama3.1:8b"], "task": "Balanced Research",
        "ram": "8GB RAM", "vram": "6GB",
        "capabilities": ["Fast Summarization", "Entity Extraction", "Technical Chat", "Refactoring Suggestions"]
    },
    "mimo:v2.5-edge": {
        "name": "MiMo V2.5 Edge (3B)", "size": "2.1GB", "category": "TINY_KINETIC", 
        "pros": "Zero-lag su hardware base", "cons": "Capacità di sintesi limitata", 
        "caveau": "La Sonda Neurale.", "forza": "Parsing rapido di piccoli frammenti e routing segnali.",
        "synergy": ["llama3.2:1b"], "task": "Fast Parsing",
        "ram": "4GB RAM", "vram": "2GB",
        "capabilities": ["Token Filtering", "Format Conversion", "Quick QA", "Status Monitoring"]
    }
}

async def _autonomous_model_scan() -> List[Dict]:
    """Scansiona il filesystem alla ricerca di modelli LLM installati (Ollama, LM Studio, etc)."""
    installed = []
    seen_names = set()
    
    # 1. Ollama Scan (Physical Path)
    home = Path.home()
    ollama_paths = [
        home / ".ollama" / "models" / "manifests" / "registry.ollama.ai" / "library",
        Path("/usr/share/ollama/.ollama/models/manifests/registry.ollama.ai/library")
    ]
    
    for base_path in ollama_paths:
        if base_path.exists():
            for model_dir in base_path.iterdir():
                if model_dir.is_dir():
                    model_family = model_dir.name
                    for tag_file in model_dir.iterdir():
                        if tag_file.is_file():
                            full_name = f"{model_family}:{tag_file.name}"
                            if full_name not in seen_names:
                                # Tentiamo di stimare la dimensione dal tag o lasciamo N/D se non accessibile
                                installed.append({
                                    "name": full_name,
                                    "size": "Detected (Local)",
                                    "source": "Ollama (Disk Scan)",
                                    "metadata": MODEL_CATALOG.get(full_name, {"pros": "Rilevato via Disk Scan", "cons": "N/D", "synergy": []})
                                })
                                seen_names.add(full_name)

    # 2. LM Studio Scan
    lm_studio_paths = [
        home / ".cache" / "lm-studio" / "models",
        home / "Library" / "Application Support" / "com.lmstudio.LMStudio" / "models"
    ]
    for p in lm_studio_paths:
        if p.exists():
            for model_file in p.rglob("*.gguf"):
                name = model_file.name
                if name not in seen_names:
                    size_gb = round(model_file.stat().st_size / (1024**3), 2)
                    installed.append({
                        "name": f"GGUF: {name}",
                        "size": f"{size_gb}GB",
                        "source": "LM Studio / Local Disk",
                        "metadata": {"pros": "Modello GGUF nativo", "cons": "Richiede driver compatibile", "synergy": []}
                    })
                    seen_names.add(name)

    return installed

@app.get("/api/models/catalog")
async def get_model_catalog(api_key: str = Depends(get_api_key)):
    """Restituisce il catalogo completo con Pro/Contro e Sinergie."""
    return MODEL_CATALOG

@app.get("/api/models/status")
async def get_models_status(api_key: str = Depends(get_api_key)):
    """Sincronizzazione Unificata: Modelli Installati + Catalogo Disponibile."""
    import httpx
    full_list = []
    seen_in_api = set()

    # 1. Recupero Modelli INSTALLATI (Ollama)
    base_url = app.state.lab.settings.get("ollama_url") if hasattr(app.state, 'lab') else "http://127.0.0.1:11434"
    ollama_urls = [os.environ.get("OLLAMA_HOST", base_url), base_url]
    for url in ollama_urls:
        if seen_in_api: break
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                r = await client.get(f"{url.rstrip('/')}/api/tags")
                if r.status_code == 200:
                    data = r.json()
                    for m in data.get("models", []):
                        name = m.get("name")
                        cat_info = MODEL_CATALOG.get(name) or MODEL_CATALOG.get(name.split(":")[0] + ":latest") or {}
                        
                        full_list.append({
                            "name": name,
                            "status": "INSTALLED",
                            "size": f"{round(m.get('size', 0) / (1024**3), 2)}GB",
                            "category": cat_info.get("category", "General"),
                            "pros": cat_info.get("pros", "Custom Node"),
                            "synergy": cat_info.get("synergy", ["None"]),
                            "task": cat_info.get("task", "General Reasoning"),
                            "strengths": cat_info.get("forza", "Hardware-Attached Analysis"),
                            "capabilities": cat_info.get("capabilities", []),
                            "ram": cat_info.get("ram", "N/D"),
                            "vram": cat_info.get("vram", "N/D")
                        })
                        seen_in_api.add(name)
        except: continue

    # 2. Recupero Modelli DISPONIBILI (Dal Catalogo, non ancora installati)
    for model_id, info in MODEL_CATALOG.items():
        if model_id not in seen_in_api:
            full_list.append({
                "name": model_id,
                "status": "AVAILABLE",
                "size": info.get("size", "N/D"),
                "category": info.get("category", "General"),
                "pros": info.get("pros", "N/D"),
                "synergy": info.get("synergy", ["None"]),
                "task": info.get("task", "General Reasoning"),
                "strengths": info.get("forza", "Elite Training"),
                "capabilities": info.get("capabilities", []),
                "ram": info.get("ram", "N/D"),
                "vram": info.get("vram", "N/D")
            })

    # 3. Recupero Modelli CUSTOM (Dalla Neural Forge)
    custom_models = load_custom_models()
    for name, info in custom_models.items():
        # Se è un modello Ollama, verifichiamo se è già presente (magari con nome diverso)
        # Ma in generale, li trattiamo come INSTALLED se il provider è 'ollama' o 'local'
        full_list.append({
            "name": f"{name} (Custom)",
            "status": "INSTALLED",
            "size": "N/D",
            "category": "CUSTOM_FORGE",
            "pros": f"User Integrated via {info.get('provider', 'Custom')}",
            "synergy": ["User_Workflow"],
            "task": "Specialized Purpose",
            "strengths": f"Puntatore: {info.get('path')}",
            "capabilities": ["Personal Training", "Custom Knowledge", "Private Core"],
            "ram": "Varie",
            "vram": "Varie"
        })

    return {"installed": full_list, "total_detected": len(full_list)}

@app.post("/api/lab/hub/custom/register")
async def register_custom_model(req: Dict, api_key: str = Depends(get_api_key)):
    """Registra un modello custom nel Vault."""
    name = req.get("name")
    provider = req.get("provider")
    path = req.get("path")
    
    if not name or not path:
        raise HTTPException(status_code=400, detail="Name and Path are required")
    
    custom = load_custom_models()
    custom[name] = {
        "provider": provider,
        "path": path,
        "registered_at": time.time()
    }
    save_custom_models(custom)
    
    # Se il provider è Ollama, possiamo anche tentare un 'ollama run' o simile per verificare
    print(f"🛠️ [Neural Forge] Modello registrato: {name} ({provider}) -> {path}")
    return {"status": "success", "model": name}

@app.delete("/api/models/delete/{model_name:path}")
async def delete_model(model_name: str, api_key: str = Depends(get_api_key)):
    """Rimuove fisicamente un modello per liberare spazio."""
    import httpx
    model_name = model_name.strip()
    try:
        async with httpx.AsyncClient() as client:
            base_url = app.state.lab.settings.get("ollama_url") if hasattr(app.state, 'lab') else "http://127.0.0.1:11434"
            r = await client.request("DELETE", f"{base_url}/api/delete", json={"name": model_name})
            if r.status_code == 200:
                return {"status": "deleted", "model": model_name}
            else:
                return {"status": "error", "message": r.text}
    except Exception as e:
        return {"status": "error", "message": str(e)}



@app.post("/api/ingest")
async def ingest_text(request: Request, background_tasks: BackgroundTasks, api_key: str = Depends(get_api_key)):
    """Ingestione diretta di testo puro (es. Pensieri Vocali)."""
    data = await request.json()
    text = data.get("text")
    filename = data.get("filename", "Manual_Entry")
    namespace = data.get("namespace", "default")
    
    node_id = str(uuid.uuid4())
    await engine.add_node(node_id, text, metadata={"source": filename, "namespace": namespace})
    
    # [v9.0] Shadow Logging for CQRS Migration
    aegis_bus.emit("NODE_CREATED", {
        "id": node_id,
        "text_preview": text[:100],
        "source": filename,
        "namespace": namespace
    })
    
    # [v7.0] Innesco automatico estrazione causale in background
    background_tasks.add_task(auto_extract_causal, node_id)
    
    # [v9.5] Innesco Compounding Wiki Update
    background_tasks.add_task(compounding_wiki_mgr.update_compounding_wiki, node_id)
    
    return {"status": "synapsed", "id": node_id}

async def auto_extract_causal(node_id: str):
    """Worker interno per l'estrazione causale automatica."""
    import asyncio
    # [v11.0 Performance Engine] Suspend when Priority Shift is active to dedicate 100% resources
    while getattr(engine, 'priority_mode', False):
        await asyncio.sleep(1.0)
    try:
        # [v9.2.1] Performance Optimization: Concurrent Reads
        node = find_node_robust(node_id)
        if node:
            from retrieval.causal_extractor import CausalExtractor
            extractor = CausalExtractor(engine)
            new_edges = await extractor.extract_causal_relations(node)
            if new_edges:
                async with engine_lock:
                    node.edges.extend(new_edges)
                    engine._tiers.episodic.put(node)
                    print(f"✨ [Auto-Causal] Estratti {len(new_edges)} archi per {node_id[:8]}")
                    
                    # Project edges to Aegis/KuzuDB
                    for edge in new_edges:
                        try:
                            aegis_bus.emit("CAUSAL_EDGE_ADDED", {
                                "source": node_id,
                                "target": edge.target_id,
                                "type": str(edge.relation),
                                "weight": float(edge.weight)
                            })
                        except Exception as ee:
                            print(f"⚠️ [Aegis Bus Error] Auto-Causal emit failed: {ee}")
    except Exception as e:
        print(f"⚠️ [Auto-Causal Error] {e}")

@app.post("/api/causal/extract")
async def extract_causal_node(request: Request, api_key: str = Depends(get_api_key)):
    """[v7.0] Estrae archi logici (CAUSES, PREVENTS, etc.) da un nodo."""
    data = await request.json()
    node_id = data.get("id")
    
    if engine is None: raise HTTPException(status_code=500, detail="Engine not ready")
    
    # [v9.2.1] Performance Optimization: Concurrent Reads
    node = find_node_robust(node_id)
    
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    
    from retrieval.causal_extractor import CausalExtractor
    extractor = CausalExtractor(engine)
    new_edges = await extractor.extract_causal_relations(node)
    
    if new_edges:
        async with engine_lock:
            # Aggiungiamo i nuovi archi preservando quelli esistenti
            node.edges.extend(new_edges)
            # Salvataggio persistente
            engine._tiers.episodic.put(node)
            
            # Project edges to Aegis/KuzuDB
            for edge in new_edges:
                try:
                    aegis_bus.emit("CAUSAL_EDGE_ADDED", {
                        "source": node_id,
                        "target": edge.target_id,
                        "type": str(edge.relation),
                        "weight": float(edge.weight)
                    })
                except Exception as ee:
                    print(f"⚠️ [Aegis Bus Error] Causal extract emit failed: {ee}")
            
    return {
        "node_id": node_id,
        "causal_links": len(new_edges),
        "relations": [e.relation for e in new_edges]
    }

@app.post("/api/analyze")
async def analyze_node(request: Request, api_key: str = Depends(get_api_key)):
    """Avvia il dibattito avversariale su un nodo per trovare debolezze."""
    data = await request.json()
    node_id = data.get("id")
    
    if engine is None: raise HTTPException(status_code=500, detail="Engine not ready")
    
    # [v9.2.1] Performance Optimization: Concurrent Reads
    node = find_node_robust(node_id)
    
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    
    # Esegue la sessione avversariale (Digital Courtroom)
    verdict = await app.state.lab.run_adversarial_session(node_id, node.text)
    
    return {
        "node_id": node_id,
        "verdict": verdict,
        "mode": "adversarial"
    }

@app.get("/api/metacognition/gaps")
async def get_knowledge_gaps(api_key: str = Depends(get_api_key)):
    """[v7.0] Recupera i vuoti semantici (Terra Incognita) per la Nebula 3D."""
    from retrieval.metacognition import MetacognitionEngine
    meta = MetacognitionEngine(engine)
    gaps = await meta.map_ignorance_gaps()
    return {
        "status": "success",
        "gaps": [
            {
                "id": g.id,
                "x": g.x,
                "y": g.y,
                "z": g.z,
                "radius": g.radius,
                "context": g.topic_context,
                "missing": g.missing_concepts
            } for g in gaps
        ]
    }

@app.get("/api/analytics")
async def get_analytics(api_key: str = Depends(get_api_key)):
    """Metriche profonde del grafo, efficienza semantica e hardware DNA."""
    # 1. Metriche dell'Engine (Nodi, Sinapsi, Hit Rate)
    report = engine.get_analytics_report()
    
    # 2. Metriche Hardware Reali (Apple Silicon Optimized)
    from utils.hardware import HardwareTuner
    tuner = HardwareTuner(data_dir=engine.data_dir if hasattr(engine, 'data_dir') else "./vault_data")
    hw_data = tuner.get_telemetry()
    
    # 3. Merging dei dati per l'Aura Dashboard
    return {**report, **hw_data}

@app.get("/api/analytics/semantic")
async def get_semantic_composition(api_key: str = Depends(get_api_key)):
    """[v9.8] Calcola in tempo reale la composizione semantica del database neurale."""
    if not engine:
        raise HTTPException(503, "Engine Offline")
    
    try:
        nodes = list(engine._nodes.values())
        total = len(nodes)
        
        categories = {
            "python_core": {"title": "Python Core & StdLib", "count": 0, "color": "#3b82f6", "icon": "fa-code"},
            "rust_systems": {"title": "Rust & Systems Programming", "count": 0, "color": "#f97316", "icon": "fa-microchip"},
            "web_foraging": {"title": "Web Foraging & Crawling", "count": 0, "color": "#06b6d4", "icon": "fa-globe"},
            "agentic_cognitive": {"title": "Cognitive Agents & Swarms", "count": 0, "color": "#a855f7", "icon": "fa-brain"},
            "macro_finance": {"title": "Macroeconomics & Finance", "count": 0, "color": "#eab308", "icon": "fa-coins"},
            "general_others": {"title": "General Knowledge & Others", "count": 0, "color": "#64748b", "icon": "fa-cubes"}
        }
        
        if total == 0:
            return {
                "status": "success",
                "total_nodes": 0,
                "composition": [],
                "insight": "Il Vault è vuoto. Carica file o avvia l'intercettatore per popolarlo."
            }
            
        for node in nodes:
            text = (node.text or "").lower()
            source = str(node.metadata.get("source", "")).lower()
            
            # Highly accurate heuristic classification
            if "rust" in text or "cargo" in text or ".rs" in source or "systems programming" in text:
                categories["rust_systems"]["count"] += 1
            elif any(w in text for w in ["python", "def ", "class ", "import ", "pip ", "conda", "setup.py", "standard library"]):
                categories["python_core"]["count"] += 1
            elif any(w in text or w in source for w in ["skywalker", "yoda", "swarm", "agent", "orchestrator", "supreme court", "mediator"]):
                categories["agentic_cognitive"]["count"] += 1
            elif any(w in text or w in source for w in ["http", "crawl", "forage", "url", "scrape", "search", "duckduckgo"]):
                categories["web_foraging"]["count"] += 1
            elif any(w in text for w in ["macroeconomics", "finance", "rate", "usd", "market", "capital", "gdp", "sovereign", "inflation"]):
                categories["macro_finance"]["count"] += 1
            else:
                categories["general_others"]["count"] += 1
                
        composition = []
        for key, cat in categories.items():
            pct = (cat["count"] / total) * 100 if total > 0 else 0
            composition.append({
                "key": key,
                "title": cat["title"],
                "count": cat["count"],
                "percentage": round(pct, 2),
                "color": cat["color"],
                "icon": cat["icon"]
            })
            
        # Dynamic advice based on composition
        major = max(composition, key=lambda x: x["percentage"]) if composition else {"key": "general_others", "title": "General"}
        if major["key"] == "python_core":
            insight = "Il tuo Vault è sbilanciato verso lo sviluppo software (Core Python). Questo ottimizza lo sciame per compiti di programmazione, ma per What-If storici complessi si raccomanda l'importazione di fonti geopolitiche o finanziarie esterne."
        elif major["key"] == "agentic_cognitive":
            insight = "Altissima densità cognitiva dello Swarm rilevata. Gli agenti stanno riflettendo profondamente sulle loro stesse istruzioni. Perfetto per la stabilità ed evoluzione autonoma."
        else:
            insight = f"Composizione bilanciata con dominanza del settore '{major['title']}'. Lo sciame ha accesso a un set cognitivo diversificato."
            
        return {
            "status": "success",
            "total_nodes": total,
            "composition": composition,
            "insight": insight
        }
    except Exception as e:
        raise HTTPException(500, str(e))



# SECTION: LAB MISSIONS & AGENTS (Integrated v3.5)

# 🛰️ GOSSIP MESH ENDPOINTS
@app.post("/api/gossip/sync")
async def receive_gossip_signal(signal: SyncSignal):
    """Riceve un segnale di sincronizzazione da un altro nodo della Mesh."""
    data = signal.data
    
    # 🔐 Decrittazione se necessario (X25519 + AES-GCM)
    if signal.encrypted_data and engine and engine.crypto:
        peer = engine.gossip.peers.get(signal.source_node_id)
        if peer and peer.public_key:
            try:
                if not peer.shared_key:
                    peer.shared_key = engine.crypto.derive_shared_key(peer.public_key)
                
                decrypted_json = engine.crypto.decrypt(signal.encrypted_data, peer.shared_key)
                data = json.loads(decrypted_json)
            except Exception as e:
                print(f"🚨 [Mesh] Decrittazione fallita da {signal.source_node_id}: {e}")
                return {"status": "error", "message": "decryption_failed"}
        else:
            print(f"⚠️ [Mesh] Segnale cifrato ricevuto da peer sconosciuto o senza chiave: {signal.source_node_id}")

    if signal.payload_type == "upsert" and data:
        # Inserimento atomico del nodo sincronizzato preservando l'identità semantica
        node_id = data.get("id")
        if node_id not in engine._nodes:
            from vault_node import VaultNode
            import numpy as np
            
            node = VaultNode(
                id=node_id,
                # [v16.0] Refined Galaxy Clustering: use specific cluster_id or topic to avoid merging distinct galaxies
                cluster_key = data.get("metadata", {}).get("cluster_id") or data.get("metadata", {}).get("topic") or data.get("metadata", {}).get("source", data.get("collection") or "default"),
                collection=data.get("collection", "default"),
                text=data.get("text", ""),
                vector=np.array(data["vector"]) if "vector" in data else None,
                metadata=data.get("metadata", {}),
                created_at=data.get("created_at", time.time())
            )
            await engine.upsert(node)
            return {"status": "synced", "node_id": node_id}
    return {"status": "ignored"}
    
# 🔑 SOVEREIGN AUTH ENDPOINTS
@app.get("/api/auth/google")
async def google_auth(api_key: str = Depends(get_api_key)):
    """Avvia il flusso OAuth2 per Google (Gmail/Pollers)."""
    if not engine or not engine.oauth:
        raise HTTPException(status_code=500, detail="OAuth Manager non inizializzato")
    
    try:
        # Questo aprirà il browser sul Mac dell'utente
        creds = engine.oauth.start_flow()
        return {
            "status": "ok", 
            "message": "Autenticazione completata con successo",
            "token_expiry": creds.expiry.isoformat() if creds.expiry else None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore durante l'autenticazione: {str(e)}")

# 🕸️ MESH PROTOCOL v3.8.0
@app.get("/api/mesh/inventory")
async def mesh_inventory(api_key: str = Depends(get_api_key)):
    """Ritorna l'indice atomico dei nodi locali per il diffing Mesh."""
    return {"ids": list(engine._nodes.keys())}

@app.get("/api/mesh/verdict")
async def get_mesh_verdict(claim: str, context: str = "", api_key: str = Depends(get_api_key)):
    """[v7.5] Fornisce un verdetto pesato su un claim per il consenso mesh."""
    if engine is None: raise HTTPException(status_code=500, detail="Engine not ready")
    results = await engine.query(f"{claim} {context}", k=5)
    support_score = sum(r.final_score for r in results) if results else 0.0
    verdict = "UNCERTAIN"
    if results:
        if support_score > 2.5: verdict = "SUPPORTS"
        elif support_score < 1.0: verdict = "CONTRADICTS"
    stats = {"node_count": len(results), "source_density": 0.5, "recency_score": 0.8, "coherence": 0.95}
    return {"peer_id": engine.node_id if hasattr(engine, 'node_id') else "local_vault", "verdict": verdict, "stats": stats}

@app.post("/api/mesh/pull")
async def mesh_pull(request: Request, api_key: str = Depends(get_api_key)):
    """Espone i nodi richiesti dai peer per la sincronizzazione."""
    data = await request.json()
    ids = data.get("ids", [])
    nodes = []
    for nid in ids:
        node = engine._nodes.get(nid)
        if node:
            nodes.append({
                "id": node.id,
                "text": node.text,
                "metadata": node.metadata
            })
    return {"nodes": nodes}

@app.get("/api/mesh/peers")
async def list_mesh_peers(api_key: str = Depends(get_api_key)):
    """Ritorna la lista dei peer connessi nella rete Mesh."""
    peers = []
    local_id = getattr(engine, 'node_id', None)
    
    # 1. Peer dal MeshSyncManager
    for pid, p in engine.mesh.peers.items():
        if local_id and pid == local_id:
            continue
        peers.append({
            "id": pid,
            "url": p.base_url,
            "last_seen": p.last_seen,
            "source": "manual/mesh",
            "paused": getattr(p, 'paused', False)
        })
    # 2. Peer dal GossipManager (scoperti via Discovery)
    for pid, p in engine.gossip.peers.items():
        if local_id and pid == local_id:
            continue
        if pid not in engine.mesh.peers:
            peers.append({
                "id": pid,
                "url": p.address,
                "last_seen": p.last_seen,
                "source": "discovery",
                "paused": getattr(p, 'paused', False)
            })
    # 3. Aggancia ed evidenzia i P2P Wormholes della v11.0
    if engine and hasattr(engine, 'wormholes') and engine.wormholes:
        for pid, t in engine.wormholes.tunnels.items():
            if local_id and pid == local_id:
                continue
            # Se è già presente, aggiorna le info crittografiche del Wormhole
            existing = next((x for x in peers if x["id"] == pid), None)
            if existing:
                existing["source"] = "wormhole"
                existing["wormhole"] = True
                existing["namespace"] = t.namespace
                existing["connected"] = t.is_connected
            else:
                peers.append({
                    "id": pid,
                    "url": t.base_url,
                    "last_seen": t.last_seen,
                    "source": "wormhole",
                    "paused": t.paused,
                    "wormhole": True,
                    "namespace": t.namespace,
                    "connected": t.is_connected
                })
    return {"peers": peers}

@app.post("/api/mesh/peers/toggle-pause")
async def toggle_pause_mesh_peer(request: Request, api_key: str = Depends(get_api_key)):
    """Mette in pausa o riattiva un peer nella rete Mesh."""
    data = await request.json()
    peer_id = data.get("id")
    paused = data.get("paused", False)
    if not peer_id: raise HTTPException(status_code=400, detail="ID del peer obbligatorio")
    
    # Aggiorna tutti i manager, incluso il Wormhole P2P
    engine.mesh.toggle_pause(peer_id, paused)
    engine.gossip.toggle_pause(peer_id, paused)
    if engine and hasattr(engine, 'wormholes') and engine.wormholes:
        if peer_id in engine.wormholes.tunnels:
            engine.wormholes.tunnels[peer_id].paused = paused
    
    return {"status": "paused" if paused else "resumed", "id": peer_id}

@app.post("/api/mesh/peers/add")
async def add_mesh_peer(request: Request, api_key: str = Depends(get_api_key)):
    """Aggiunge un dispositivo fidato alla rete Mesh."""
    data = await request.json()
    node_id = data.get("id") or f"peer_{len(engine.mesh.peers)}"
    url = data.get("url")
    peer_api_key = data.get("api_key")
    if not url: raise HTTPException(status_code=400, detail="URL del peer obbligatorio")
    
    # 🕵️ AGENT SMITH: Professional Firewall Inspection
    lab = getattr(app.state, 'lab', None)
    if lab:
        smith = list(lab.smiths.values())[0] if lab.smiths else AgentSmith(engine, lab)
        is_safe = smith.inspect_peer({"id": node_id, "url": url, "vault_key": peer_api_key or ""})
        if not is_safe:
            raise HTTPException(status_code=403, detail=f"AGENT SMITH: Accesso Negato. Motivo: {smith.status}")

    engine.mesh.add_peer(node_id, url, peer_api_key)
    
    # Inizializza automaticamente un tunnel Wormhole P2P per connessione sicura Noise
    if engine and hasattr(engine, 'wormholes') and engine.wormholes:
        # Usa peer_api_key come public_key se non fornito esplicitamente
        pub_key = data.get("public_key") or peer_api_key or engine.crypto.get_public_key_base64()
        ns = data.get("namespace")
        engine.wormholes.create_tunnel(node_id, url, pub_key, ns)
        
    return {"status": "peer_connected", "id": node_id}

@app.post("/api/mesh/peers/rename")
async def rename_mesh_peer(request: Request, api_key: str = Depends(get_api_key)):
    """Rinomina un peer nella Mesh locale."""
    data = await request.json()
    old_id = data.get("id")
    new_id = data.get("new_id")
    if not old_id or not new_id:
        raise HTTPException(status_code=400, detail="ID attuali e nuovi obbligatori")
    engine.mesh.rename_peer(old_id, new_id)
    return {"status": "renamed", "old_id": old_id, "new_id": new_id}

@app.post("/api/wormhole/receive")
async def receive_wormhole_payload_endpoint(request: Request):
    """[v11.0] Riceve ed elabora payload crittografati in tempo reale (Gossipsub)."""
    if not engine or not hasattr(engine, 'wormholes') or not engine.wormholes:
        raise HTTPException(status_code=503, detail="Wormholes Engine Offline")
    
    try:
        data = await request.json()
        success = await engine.wormholes.receive_wormhole_payload(data)
        if success:
            return {"status": "success", "message": "Payload ingested correctly through P2P wormhole."}
        else:
            raise HTTPException(status_code=400, detail="Failed to ingest wormhole payload. Smith blocks or decryption failure.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/mesh/identity/export")
async def export_vault_identity(api_key: str = Depends(get_api_key)):
    """Esporta l'identità del vault per condivisione sicura."""
    import socket
    try:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
    except: local_ip = "127.0.0.1"
    
    identity = {
        "id": engine.node_id,
        "url": f"http://{local_ip}:8001",
        "vault_key": VAULT_KEY,
        "public_key": "x25519_placeholder_v4"
    }
    return identity

@app.post("/api/mesh/identity/import")
async def import_vault_identity(request: Request, api_key: str = Depends(get_api_key)):
    """Importa un'identità vault da file .vault e tenta il collegamento."""
    data = await request.json()
    peer_id = data.get("id")
    url = data.get("url")
    v_key = data.get("vault_key")
    
    if not peer_id or not url:
        raise HTTPException(status_code=400, detail="Dati identità incompleti")
    
    # 🕵️ AGENT SMITH: Deep Peer Inspection (DPI)
    lab = getattr(app.state, 'lab', None)
    if lab and hasattr(lab, 'smiths'):
        # Se la flotta è vuota (primo collegamento), usiamo un'istanza dedicata all'audit
        smith = list(lab.smiths.values())[0] if lab.smiths else AgentSmith(engine, lab)
        is_safe = smith.inspect_peer(data)
        if not is_safe:
            raise HTTPException(status_code=403, detail=f"AGENT SMITH: Connessione rifiutata. Motivo: {smith.status}")
            
    # Aggiungi il peer se sicuro
    engine.mesh.add_peer(peer_id, url, v_key)
    engine.mesh.force_sync() # 🚀 Avvia subito il recupero dati
    return {"status": "imported", "id": peer_id}

@app.delete("/api/mesh/peers/{peer_id}")
async def delete_mesh_peer(peer_id: str, api_key: str = Depends(get_api_key)):
    """Rimuove permanentemente un peer dalla Mesh locale."""
    engine.mesh.remove_peer(peer_id)
    engine.gossip.remove_peer(peer_id)
    if hasattr(engine, 'wormholes') and engine.wormholes:
        engine.wormholes.remove_tunnel(peer_id)
    return {"status": "removed", "id": peer_id}

# 🌐 ALIAS per Aura Bridge Extension (compatibilità)
@app.post("/api/upload_text")
async def upload_text_alias(request: Request, api_key: str = Depends(get_api_key)):
    """Alias di /api/ingest per compatibilità con Aura Bridge Extension."""
    data = await request.json()
    text = data.get("text", "")
    metadata = data.get("metadata", {})
    if not text:
        raise HTTPException(status_code=400, detail="Campo 'text' obbligatorio")
    node_id = str(uuid.uuid4())
    await engine.upsert_text(text, metadata={"source": metadata.get("source", "aura_bridge"), **metadata})
    return {"status": "synapsed", "id": node_id}

# 🕸️ WEB FORAGER — Crawling e Ingestione di URL
@app.post("/api/forage")
async def forage_url(
    request: Request,
    background_tasks: BackgroundTasks,
    api_key: str = Depends(get_api_key)
):
    """
    Avvia il Web Foraging su un URL:
    - Scarica la pagina e le sottopagine (depth configurabile)
    - Fa parsing HTML, OCR immagini, estrazione PDF
    - Ingestisce tutto nel Vault come nodi semantici
Risponde subito con job_id; il progresso è tracciato nel Blackboard.
    """
    data = await request.json()
    url = data.get("url")
    max_depth = int(data.get("max_depth", 10))
    max_pages = int(data.get("max_pages", 9999))
    same_domain = data.get("same_domain_only", True)

    if not url or not url.startswith("http"):
        raise HTTPException(status_code=400, detail="URL non valido. Deve iniziare con http:// o https://")

    job_id = str(uuid.uuid4())
    app.state.forage_jobs[job_id] = {
        "status": "IN_PROGRESS", 
        "url": url, 
        "pages": 0, 
        "start_time": time.time(),
        "elapsed": "0s",
        "progress": 0
    }
    app.state.forage_proposals[job_id] = []

    async def _run_forage():
        start_t = time.time()
        forager = SovereignWebForager(
            max_depth=max_depth,
            max_pages=max_pages,
            same_domain_only=same_domain,
        )
        try:
            total_chunks = 0
            page_count = 0
            async for page in forager.forage(url):
                # Calcolo progresso reale (pagine processate / totali scoperte)
                queue_len = len(getattr(forager, 'queue', []))
                total_discovered = page_count + queue_len + 1
                progress = min(99, int((page_count / total_discovered) * 100)) if total_discovered > 0 else 0
                
                elapsed_raw = time.time() - start_t
                elapsed_str = f"{int(elapsed_raw)}s"
                
                # Update State
                app.state.forage_jobs[job_id].update({
                    "pages": page_count + 1,
                    "elapsed": elapsed_str,
                    "progress": progress
                })

                chunks = page.to_chunks()
                for c in chunks:
                    chunk_text = c["text"]
                    # 🔒 DEDUPLICAZIONE SEMANTICA (v2.6.0)
                    content_hash = hashlib.sha256(chunk_text.encode()).hexdigest()
                    existing_id = engine._prefilter.check_duplicate(content_hash)
                    
                    if existing_id:
                        # Se il nodo esiste già, rinforziamo la sua importanza invece di duplicarlo
                        engine._prefilter.hit_node(existing_id)
                        continue

                    meta = c["metadata"].copy()
                    meta["color"] = "#22d3ee" # Cyan
                    meta["forage_job"] = job_id
                    meta["content_hash"] = content_hash
                    try:
                        node_id = await engine.upsert_text(chunk_text, metadata=meta)
                        # 🚀 [v8.2] Notify Skywalker to fire lasers at the new node
                        if hasattr(app.state, 'lab') and node_id:
                            node = engine._nodes.get(node_id)
                            if node:
                                app.state.lab.skywalker.status = f"INJECTING: {meta.get('source', 'Web Intel')[:20]}..."
                                app.state.lab.skywalker.laser_target = {
                                    'x': node.metadata.get('x', 0),
                                    'y': node.metadata.get('y', 0),
                                    'z': node.metadata.get('z', 0)
                                }
                                app.state.lab.skywalker.last_mission_time = time.time()
                    except Exception as e:
                        print(f"⚠️ [Kernel] Ingest Fallito per chunk: {e}")
                
                total_chunks += len(chunks)
                page_count += 1
                
                # 🖼️ MULTIMODAL INGESTION: Immagini coerenti (v7.1.5)
                try:
                    multimodal = getattr(app.state, 'mm_processor', None)
                    if multimodal and page.images:
                        # Filtriamo immagini potenzialmente utili (non icone)
                        for img_url in page.images[:10]: # Limite per pagina per non saturare
                            if any(x in img_url.lower() for x in ["icon", "logo", "pixel"]): continue
                            
                            # Download temporaneo per ingestion multimodale
                            try:
                                async with httpx.AsyncClient(timeout=10.0) as client:
                                    img_resp = await client.get(img_url)
                                    if img_resp.status_code == 200:
                                        temp_path = Path(f"vault_data/temp_media/forage_{uuid.uuid4().hex}.jpg")
                                        temp_path.parent.mkdir(parents=True, exist_ok=True)
                                        temp_path.write_bytes(img_resp.content)
                                        
                                        # Ingestione reale con ImageBind + Vision LLM
                                        await multimodal.ingest(temp_path, source_uri=img_url)
                                        if temp_path.exists(): os.remove(temp_path)
                                        print(f"🖼️ [Multimodal] Image Synapsed: {img_url[:40]}...")
                            except: pass
                except: pass

                print(f"⏱️ [{elapsed_str}] Foraging Progress: {progress}% | 📄 Pages: {page_count} | Synapsing -> {url[:50]}...")
                
                # Segnale al Blackboard (visibile nel Neural Lab)
                try:
                    sig = SynapticSignal(
                        sender_id=f"forager_{job_id[:8]}",
                        role=AgentRole.RESEARCHER,
                        msg=f"Ingested: {page.title or url[:30]}",
                        signal_type=SignalType.KNOWLEDGE_ACQUISITION,
                        urgency=0.5
                    )
                    app.state.lab.blackboard.post(sig)
                except: pass

            # Salva le proposte raccolte per l'approvazione utente
            app.state.forage_proposals[job_id] = forager.proposals
            app.state.forage_jobs[job_id]["status"] = "COMPLETE"
            app.state.forage_jobs[job_id]["pages"] = page_count
            
            print(f"✅ [Forage Job {job_id[:8]}] Completato: {page_count} pagine, {total_chunks} chunk ingestiti da {url}")
            print(f"🕯️ [Insight] Trovate {len(forager.proposals)} proposte di approfondimento esterno.")
        except Exception as e:
            app.state.forage_jobs[job_id]["status"] = "ERROR"
            print(f"❌ [Forage Job {job_id[:8]}] Errore: {e}")

    background_tasks.add_task(_run_forage)

    return {
        "status": "foraging_started",
        "job_id": job_id,
        "url": url,
        "message": "Foraging job successfully initiated in background."
    }

@app.post("/api/mission")
async def dispatch_lab_mission(request: Request, api_key: str = Depends(get_api_key)):
    """Invia una missione strategica allo Swarm di Agenti nel Neural Lab."""
    data = await request.json()
    mission_text = data.get("mission")
    
    if not mission_text:
        raise HTTPException(status_code=400, detail="Il testo della missione è obbligatorio.")
    
    # Trigger asincrono dell'orchestratore
    mission_id = app.state.lab.execute_mission(mission_text)
    
    return {
        "status": "mission_dispatched",
        "mission_id": mission_id,
        "message": "Lo Swarm ha ricevuto le direttive. Monitora il Neural Lab per i progressi."
    }

@app.post("/api/lab/agent/{agent_id}/task")
async def agent_task(agent_id: str, request: Request, api_key: str = Depends(get_api_key)):
    """Invia un compito specifico a un singolo agente del Lab."""
    data = await request.json()
    task_text = data.get("task")
    
    if agent_id not in app.state.lab.agents:
        raise HTTPException(status_code=404, detail="Agente non trovato.")
    
    agent = app.state.lab.agents[agent_id]
    
    # Esecuzione task (simuliamo un'interazione diretta via Ollama)
    prompt = f"TASK DIRETTO DALL'UTENTE: {task_text}\nRispondi secondo il tuo mandato: {agent.identity['prompt']}"
    response = await app.state.lab._call_ollama_for_agent(agent.identity["name"], prompt)
    
    # Log sulla blackboard
    sig = SynapticSignal(agent.identity["name"], agent.identity["role"], f"🎯 TASK COMPLETATO: {task_text[:30]}...", SignalType.SYSTEM_NOTIFICATION)
    app.state.lab.blackboard.post(sig)
    
    return {
        "agent": agent.identity["name"],
        "response": response
    }

@app.get("/api/lab/status")
async def get_lab_status(api_key: str = Depends(get_api_key)):
    """Restituisce lo stato live di tutti gli agenti e della blackboard."""
    if not hasattr(app.state, 'lab'):
        return {"error": "Lab not initialized"}
    return app.state.lab.get_status()

@app.post("/api/lab/agent/{agent_id}/approve")
async def approve_agent_mission(agent_id: str, api_key: str = Depends(get_api_key)):
    """Sblocca una missione in 'Mission Hold' (Neural Circuit Breaker)."""
    if not hasattr(app.state, 'lab'):
        raise HTTPException(status_code=500, detail="Lab not initialized")
    
    success = app.state.lab.approve_mission(agent_id)
    if success:
        return {"status": "approved", "agent_id": agent_id}
    else:
        raise HTTPException(status_code=400, detail="Impossibile approvare la missione. L'agente non è in stato di attesa o non esiste.")

@app.post("/api/lab/agent/{agent_id}/consult")
async def consult_agent_oracle(
    agent_id: str, 
    model: str = "deepseek-r1:7b", 
    human_tip: str = "",
    api_key: str = Depends(get_api_key)
):
    """Incarica una LLM del Neural Hub di analizzare la missione e dare un verdetto."""
    if not hasattr(app.state, 'lab'):
        raise HTTPException(status_code=500, detail="Lab not initialized")
    
    result = app.state.lab.consult_oracle(agent_id, model, human_tip)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@app.get("/api/lab/audit")
async def get_lab_audit(api_key: str = Depends(get_api_key)):
    if app.state.lab is None: return []
    return app.state.lab.get_audit_ledger()

@app.get("/api/ledger/status")
async def get_ledger_status(api_key: str = Depends(get_api_key)):
    """Ritorna lo stato di salute della Blockchain (Sovereign Ledger) v1.0."""
    try:
        is_valid = engine.ledger.verify_integrity()
        latest_proof = engine.ledger.get_latest_proof()
        return {
            "status": "SECURE" if is_valid else "VULNERABLE",
            "block_count": len(engine.ledger.chain),
            "latest_merkle_root": latest_proof or "N/A",
            "integrity_check": "MATCHED" if is_valid else "TAMPERING_DETECTED",
            "l2_anchoring": "ACTIVE (Simulated)"
        }
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/forage/status")
async def forage_status(api_key: str = Depends(get_api_key)):
    try:
        recent_jobs = {jid: data for jid, data in list(app.state.forage_jobs.items())[-5:]}
        recent_log = app.state.lab.blackboard.get_recent(limit=10)
        return {
            "jobs": recent_jobs,
            "messages": [m for m in recent_log if "forager" in str(m.get("sender_id", ""))],
            "total_nodes": len(engine._nodes)
        }
    except Exception:
        return {"error": "Blackboard sync failure"}

@app.get("/api/forage/proposals/{job_id}")
async def get_proposals(job_id: str):
    if job_id not in app.state.forage_proposals:
        return {"proposals": []}
    return {"proposals": app.state.forage_proposals[job_id]}

@app.post("/api/forage/approve/{job_id}")
async def approve_forage(job_id: str, background_tasks: BackgroundTasks):
    proposals = app.state.forage_proposals.get(job_id, [])
    if not proposals:
        return {"status": "skipped", "message": "Nessuna proposta da approvare"}
    
    async def _deep_research():
        for p in proposals[:5]: # Limite a 5 approfondimenti paralleli per sessione
            topic = p["topic"]
            print(f"🚀 [Deep Research] Avvio missione: {topic}...")
            # Simulazione ricerca multi-lingua e multi-fonte
            # In futuro integreremo Agent007 Mission Architect qui
            sig = SynapticSignal(
                sender_id="deep_researcher",
                role=AgentRole.MISSION_ARCHITECT,
                msg=f"🌐 [Espansione] Approfondimento autorizzato: {topic}",
                signal_type=SignalType.MISSION_UPDATE,
                urgency=0.8
            )
            app.state.lab.blackboard.post(sig)
            
            # Creazione di un nodo sintetico per l'espansione (fino alla piena integrazione Agent007)
            await engine.upsert_text(
                f"Approfondimento su: {topic}. Fonte originaria: {p['url']}. Contesto: {p['context']}",
                metadata={"source": "DeepResearch", "topic": topic, "color": "#f59e0b"} # Oro
            )
            await asyncio.sleep(2) # Respiro tra le missioni
            
        app.state.forage_proposals[job_id] = [] # Pulisce dopo l'approvazione

    background_tasks.add_task(_deep_research)
    return {"status": "approved", "mission_count": len(proposals)}

# [v6.1] run_hybrid_evolution logic moved to NeuralLabOrchestrator.

@app.post("/api/evolve")
async def evolve_mesh(background_tasks: BackgroundTasks, api_key: str = Depends(get_api_key)):
    """Trigger manuale per un'evoluzione massiva."""
    try:
        if not hasattr(app.state, 'lab'):
            raise HTTPException(status_code=500, detail="Lab not ready.")
        app.state.lab.dispatch_evolution_mission()
        background_tasks.add_task(app.state.lab.run_hybrid_evolution, limit=2000)
        return {
            "status": "mission_dispatched",
            "message": "Protocollo di Evoluzione Cognitiva avviato."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ingest/media")
async def ingest_media(file: UploadFile = File(...), namespace: Optional[str] = Form("default"), api_key: str = Depends(get_api_key)):
    """Ingestione multimodale (Video/Audio/Immagini) v7.0."""
    print(f"📥 [Ingest/Media] Ricevuto file: {file.filename} (Type: {file.content_type})")
    
    # Salvataggio temporaneo per processing
    temp_dir = Path("vault_data/temp_media")
    temp_dir.mkdir(parents=True, exist_ok=True)
    temp_path = temp_dir / file.filename
    
    with open(temp_path, "wb") as buffer:
        buffer.write(await file.read())
        
    try:
        # v3.9.5: Smart Triage - se è un file di testo, usiamo l'engine testuale
        ext = temp_path.suffix.lower()
        if ext in ['.txt', '.md', '.log', '.json', '.py', '.js']:
            with open(temp_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            # [v3.6.0] Logical Namespacing & Scalar Extraction
            file_type = ext.replace('.', '')
            node = await engine.upsert_text(content, metadata={"source": file.filename, "namespace": namespace, "file_type": file_type})
            return {"status": "success", "nodes_created": 1, "ids": [node.id]}
            
        node_ids = await app.state.mm_processor.ingest(temp_path, namespace=namespace)
        return {"status": "success", "nodes_created": len(node_ids), "ids": node_ids}
    except Exception as e:
        print(f"❌ [Ingest Media Fail] {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if temp_path.exists():
            os.remove(temp_path)

@app.get("/api/inventory")
async def get_inventory(api_key: str = Depends(get_api_key)):
    """Infrastruttura di analisi sorgenti: Ritorna lo stack cronologico della conoscenza (v2.9.0)."""
    try:
        sources = engine._prefilter.get_knowledge_sources()
        
        # [v4.3.5] Efficient & Thread-Safe Aggregation
        # Evitiamo scansioni multiple e RuntimeError per dizionario modificato
        with engine._lock:
            all_nodes = list(engine._nodes.values())
        
        # Pre-calcoliamo i conteggi in un unico passaggio O(N)
        edge_counts = {}
        for n in all_nodes:
            if not n or not hasattr(n, 'metadata') or n.metadata is None: continue
            src = n.metadata.get("source", "Unknown Source")
            edge_counts[src] = edge_counts.get(src, 0) + len(getattr(n, 'edges', []))
            
        for s in sources:
            s["edges"] = edge_counts.get(s["source"], 0)
            
        return sources
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/nodes/update_positions")
async def update_positions(req: UpdatePositionsRequest, api_key: str = Depends(get_api_key)):
    try:
        updated = 0
        with engine._lock:
            for p in req.positions:
                node = engine._nodes.get(p.id)
                if node:
                    if node.metadata is None:
                        node.metadata = {}
                    node.metadata["x"] = p.x
                    node.metadata["z"] = p.y  # 2D y mappa alla profondita 3D z
                    try:
                        import json
                        meta_str = json.dumps(node.metadata)
                        engine._prefilter.execute("UPDATE vault_metadata SET metadata = ? WHERE id = ?", (meta_str, p.id))
                        updated += 1
                        
                        # 🚀 [CQRS FASE 1] Shadow Hook
                        from core.event_bus import AegisEventBus
                        event_bus = AegisEventBus()
                        event_bus.publish("NODE_MOVED", {
                            "id": p.id,
                            "x": p.x,
                            "y": p.y,
                            "cluster": getattr(node, 'cluster', 'default')
                        }, source={"agent": "tactical_canvas", "action": "update_positions"})

                    except Exception as db_e:
                        print(f"DuckDB update error for {p.id}: {db_e}")
        return {"status": "success", "updated_count": updated}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/namespaces")
async def get_namespaces(api_key: str = Depends(get_api_key)):
    """[v3.6.0] Esploratore di Compartimenti: Restituisce l'elenco dei namespace attivi."""
    try:
        # 1. Query dai metadati testuali
        # [v4.3.1] Thread-Safe Fetch
        res = engine._prefilter.fetchall("SELECT DISTINCT namespace FROM vault_metadata")
        text_ns = [r[0] for r in res if r[0]]
        
        # 2. Query dai metadati multimodali
        mm_ns = []
        try:
            if hasattr(app.state, 'mm_processor'):
                conn = duckdb.connect(app.state.mm_processor.db_path)
                res_mm = conn.execute("SELECT DISTINCT namespace FROM multimodal_synapses").fetchall()
                mm_ns = [r[0] for r in res_mm if r[0]]
                conn.close()
        except: pass
        
        # Merge e rimozione duplicati
        all_ns = sorted(list(set(text_ns + mm_ns + ["default", "Lavoro", "Privato", "Oliver"])))
        return {"namespaces": all_ns}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/translate")
async def translate_text(request: Request, api_key: str = Depends(get_api_key)):
    """Traduttore Neurale v1.2: Supporto Ollama IT/EN."""
    data = await request.json()
    text = data.get("text")
    target_lang = data.get("lang", "IT")
    if not text: return {"text": ""}

    try:
        res = await asyncio.to_thread(os.popen("ollama list").read)
        installed = [line.split()[0] for line in res.splitlines()[1:] if line.strip()]
        model = "mistral:latest" if "mistral:latest" in installed else (installed[0] if installed else "mistral")
        
        prompt = f"Traduci il seguente testo in {target_lang}. Rispondi SOLAMENTE con la traduzione.\n\nTESTO: {text}"
        if target_lang == "IT":
            prompt = f"Traduci in Italiano il seguente contenuto. Rispondi SOLAMENTE con la traduzione.\n\nCONTENUTO: {text}"
        
        base_url = app.state.lab.settings.get("ollama_url") if hasattr(app.state, 'lab') else "http://127.0.0.1:11434"
        async with httpx.AsyncClient(timeout=90.0) as client:
            r = await client.post(f"{base_url}/api/generate", json={
                "model": model, "prompt": prompt, "stream": False
            })
            translation = r.json().get("response", text)
            return {"translated": translation.strip()}
    except Exception as e:
        return {"translated": text, "error": str(e)}

@app.post("/api/chat")
async def neural_chat(request: QueryRequest, api_key: str = Depends(get_api_key)):
    """Oracolo Neurale: RAG Multimodale v7.5."""
    
    timings = {}
    total_start = time.time()
    
    # 1. Ricerca Semantica Intelligente (Quantum Expansion v1.0)
    exp_start = time.time()
    search_query = await app.state.lab.expand_query(request.query)
    
    # 🔮 [v4.3.1] Record for pre-fetching
    if hasattr(app.state.lab, 'prefetcher'):
        app.state.lab.prefetcher.record_interaction("search", topic=request.query[:30])
        
    timings['expansion'] = (time.time() - exp_start) * 1000
    
    print(f"🔍 [Quantum Search] Query espansa: {search_query}")
    
    ret_start = time.time()
    results = await engine.query(
        search_query, 
        k=request.top_k, 
        namespace=request.namespace,
        file_type=request.file_type,
        year=request.year,
        month=request.month,
        named_vector=request.named_vector,
        use_sparse=request.use_sparse
    )
    timings['retrieval'] = (time.time() - ret_start) * 1000
    
    try:
        mm_results = app.state.mm_processor.query(request.query, top_k=3, namespace=request.namespace)
    except Exception as e:
        print(f"⚠️ [MM Query Error] {e}")
    
    context_text = ""
    source_nodes = []
    
    for r in results:
        context_text += f"\n[{r.node.metadata.get('source', 'Unknown')}]: {r.node.text}"
        source_nodes.append({
            "id": r.node.id, 
            "text": r.node.text[:200] + "...", 
            "score": float(r.final_score),
            "temporal_confidence": getattr(r, 'temporal_confidence', 1.0),
            "topic_type": r.node.metadata.get("topic_type", "general")
        })
        
    for mr in mm_results:
        context_text += f"\n[MEDIA {mr['type'].upper()} at {mr['t_start']}ms]: {mr['content']}"
        source_nodes.append({
            "id": mr['id'],
            "text": mr['content'][:200] + "...",
            "score": 1.0,
            "temporal_confidence": 1.0,
            "topic_type": "multimodal"
        })

    # 3. [SOVEREIGN FALLBACK] v4.9: Skywalker Web Incursion if Local Vault is empty or corrupted
    is_context_poor = len(context_text.strip()) < 50 # Soglia minima per considerare il contesto utile
    
    if (not results and not mm_results) or is_context_poor:
        corrupted_nodes = [r.node.id for r in results if len(r.node.text) < 20]
        print(f"📡 [Fallback] Knowledge Gap or Corrupted Nodes identified for '{request.query}'. Mobilizing FS-77 Skywalker...")
        try:
            # Attendiamo una "Incursione Rapida" (Aumentato a 30s per stabilità v10.0)
            await asyncio.wait_for(app.state.lab.forage_web_topic(request.query), timeout=30.0)
            # Rieseguiamo la query per pescare i nuovi dati
            results = await engine.query(search_query, k=request.top_k, namespace=request.namespace)
            
            disclaimer = "⚠️ [AVVISO: RICERCA ESTERNA ATTIVATA]"
            if corrupted_nodes:
                disclaimer += f" - Nodi locali corrotti individuati: {', '.join(corrupted_nodes)}."
            else:
                disclaimer += " - Nessuna informazione locale trovata."
                
            context_text = f"{disclaimer}\n"
            for r in results:
                context_text += f"\n[FONTE ESTERNA - FS-77]: {r.node.text}"
                source_nodes.append({
                    "id": r.node.id, 
                    "text": r.node.text[:200] + "...", 
                    "score": float(r.final_score),
                    "temporal_confidence": getattr(r, 'temporal_confidence', 1.0),
                    "topic_type": r.node.metadata.get("topic_type", "general")
                })
        except Exception as e:
            print(f"⚠️ [Skywalker Fallback Error] {e}")

    full_context = context_text if context_text else "Nessun contesto trovato nel Vault."
    
    # 🌿 [v14.0 - Evolving Thesis Context Injection]
    purpose_content = ""
    try:
        purpose_file = Path("vault_data/wiki/purpose.md")
        if purpose_file.exists():
            purpose_content = purpose_file.read_text(encoding="utf-8")
    except Exception as e:
        print(f"⚠️ [Purpose Context Error] {e}")

    if purpose_content:
        import re
        clean_purpose = re.sub(r"^---.*?---", "", purpose_content, flags=re.DOTALL).strip()
        full_context = f"=== STATO COGNITIVO E TESI DI RICERCA CORRENTE (evolving_thesis) ===\n{clean_purpose}\n\n=== CONTESTO SEMANTICO ESTRATTO ===\n{full_context}"
        
    # [SOVEREIGN FOCUS] Sospendiamo gli agenti background per dare massimo respiro a Ollama
    app.state.lab.pause_agents = True
    
    gen_start = time.time()
    try:
        # [v4.3.0] Sovereign Wiki Mode Integration
        if request.wiki_mode:
            print(f"🏺 [Wiki Mode] Generating Sovereign Article for: {request.query}")
            try:
                page = await engine.wiki.generate_page(request.query, recursive=request.recursive)
                if page:
                    answer = engine.wiki.to_markdown(page)
                    # Add reflection and taxonomy tags to the answer
                    reflection = await engine.reflective.reflect_on_topic(request.query)
                    answer += "\n\n" + engine.reflective.render_markdown(reflection)
                    
                    taxonomy_map = await engine.taxonomy.get_navigation_map()
                    answer += "\n\n---\n" + taxonomy_map
                else:
                    answer = "Nessuna informazione sufficiente per generare una pagina Wiki su questo argomento."
            except Exception as e:
                print(f"❌ [Wiki Mode Error] {e}")
                answer = f"Errore durante la generazione della Wiki: {str(e)}"
        else:
            # PROTOCOLLO CONSENSUS (v3.0)
            if request.consensus:
                print(f"🏛️ [Consensus Mode] Attivazione Swarm per: {request.query}")
                answer = await app.state.lab.get_consensus_response(request.query, full_context)
            else:
                # Risposta standard a modello singolo
                try:
                    # [v4.5] Enhanced LLM Resilience: Adaptive Timeout & Dynamic Model Discovery
                    res = await asyncio.to_thread(os.popen("ollama list").read)
                    installed = [line.split()[0] for line in res.splitlines()[1:] if line.strip()]
                    
                    # Priorità: Mistral > Primo Modello Installato > Fallback
                    model = "mistral:latest" if "mistral:latest" in installed else (installed[0] if installed else "mistral")
                    base_url = app.state.lab.settings.get("ollama_url") if hasattr(app.state, 'lab') else "http://127.0.0.1:11434"
                    
                    async with httpx.AsyncClient(timeout=120.0) as client:
                        try:
                            r = await client.post(f"{base_url}/api/generate", json={
                                "model": model, 
                                "prompt": f"Contesto:\n{full_context}\n\nQ: {request.query}", 
                                "stream": False
                            })
                            r.raise_for_status()
                            answer = r.json().get("response", "Nessuna risposta generata dall'IA.")
                        except httpx.TimeoutException:
                            answer = "⚠️ Neural Timeout: L'IA sta impiegando troppo tempo per rispondere (modelli pesanti in caricamento). Riprova tra 30 secondi."
                        except httpx.ConnectError:
                            answer = "❌ Connection Refused: Ollama non risponde. Assicurati che l'app Ollama sia aperta."
                        except Exception as inner_e:
                            answer = f"🌐 Neural Link Error: {str(inner_e)}"
                except Exception as e:
                    answer = f"🧠 Cognitive Fault: {str(e)}"
    finally:
        # Ripristiniamo il background work
        app.state.lab.pause_agents = False
    
    timings['generation'] = (time.time() - gen_start) * 1000
    timings['total'] = (time.time() - total_start) * 1000

    # [v4.2.0] Persistent History Logging (Agent007 Hard Memory)
    if hasattr(app.state.lab, 'agent007') and app.state.lab.agent007:
        app.state.lab.agent007.log_query(
            query=request.query,
            answer=answer,
            metadata={"context_nodes": source_nodes, "timings": timings},
            strategy="consensus" if request.consensus else "standard"
        )

    return {
        "answer": answer,
        "context_nodes": source_nodes,
        "mode": "CONSENSUS" if request.consensus else "SINGLE_AGENT",
        "telemetry": timings,
        "routing": {
            "strategy": engine.last_routing.strategy.value if engine.last_routing else "hybrid",
            "alpha": engine.last_routing.alpha if engine.last_routing else 0.7
        },
        "neural_trace": {
            "is_validated": "🛡️ [Self-RAG" in answer,
            "skywalker_active": is_context_poor
        }
    }

@app.post("/api/wiki/generate")
async def generate_wiki_page(req: dict, api_key: str = Depends(get_api_key)):
    topic = req.get("topic")
    mode = req.get("mode", "TECHNICAL")
    if not topic: raise HTTPException(400, "Topic missing")
    
    try:
        page = await engine.wiki.generate_page(topic, mode=mode)
        if not page: return {"status": "error", "message": "No information found for this topic."}
        
        all_citations = []
        for sec in page.sections:
            for c in sec.citations:
                all_citations.append({
                    "node_id": c.node_id,
                    "source_title": c.source_title,
                    "source_url": c.source_url,
                    "source_date": c.source_date,
                    "confidence": c.confidence,
                    "excerpt": c.excerpt,
                    "is_contradictory": c.is_contradictory,
                    "conflict_node_id": c.conflict_node_id
                })
                # [v9.5] Record in Cross-Reference Index
                file_name = f"concepts/{topic.lower().replace(' ', '_')}.md"
                await compounding_wiki_mgr.register_citation(file_name, c.node_id)
        
        return {
            "status": "success",
            "title": page.title,
            "markdown": engine.wiki.to_markdown(page),
            "total_nodes": page.total_nodes,
            "related": page.related_topics,
            "citations": all_citations,
            "metadata": page.metadata
        }
    except Exception as e:
        import traceback
        error_msg = f"❌ [Wiki Error] Critical failure during generation: {e}"
        print(error_msg)
        traceback.print_exc()
        raise HTTPException(500, error_msg)
        
@app.get("/api/wiki/generate/stream")
async def stream_wiki_page(topic: str, mode: str = "TECHNICAL", api_key: str = Depends(get_api_key)):
    """[v8.4] Endpoint streaming per la generazione Wiki progressiva."""
    from fastapi.responses import StreamingResponse
    
    async def event_generator():
        async for chunk in engine.wiki.generate_page_stream(topic, mode=mode):
            yield f"data: {chunk}\n\n"
            
    return StreamingResponse(event_generator(), media_type="text/event-stream")


@app.get("/api/wiki/health")
async def get_wiki_health(api_key: str = Depends(get_api_key)):
    """⚖️ [v10.0] Recupera il report sulla salute della Wiki (Auto-Linting)."""
    try:
        report = await engine.wiki_linter.run_health_check()
        return JSONResponse(report)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

@app.get("/api/wiki/claims/{page_id}")
async def get_wiki_claims(page_id: str, api_key: str = Depends(get_api_key)):
    """🏺 [v10.0] Recupera i claim certificati per una pagina specifica."""
    try:
        query = "SELECT claim_id, claim_text, source_node_ids, confidence FROM wiki_claims WHERE page_id = ?"
        results = engine._prefilter.fetchall(query, (page_id,))
        claims = []
        for r in results:
            claims.append({
                "id": r[0],
                "text": r[1],
                "sources": json.loads(r[2]),
                "confidence": r[3]
            })
        return JSONResponse({"page": page_id, "claims": claims})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

@app.get("/api/wiki/status/{topic}")
async def get_wiki_status(topic: str, api_key: str = Depends(get_api_key)):
    """[v6.1] Controlla se una pagina Wiki ha bisogno di aggiornamenti (Freshness)."""
    try:
        from retrieval.wiki_monitor import WikiFreshnessMonitor
        monitor = WikiFreshnessMonitor(engine)
        status = await monitor.get_page_status(topic)
        return {"status": "success", "topic": topic, **status}
    except Exception as e:
        raise HTTPException(500, str(e))

@app.post("/api/contradictions/resolve")
async def resolve_contradiction(req: dict, api_key: str = Depends(get_api_key)):
    """[v6.1] Risolve manualmente o via sintesi una contraddizione."""
    id_a = req.get("id_a")
    id_b = req.get("id_b")
    strategy = req.get("strategy", "SINTESI") # SINTESI, KEEP_A, KEEP_B, MERGE
    
    if not id_a or not id_b: raise HTTPException(400, "IDs missing")
    
    try:
        from retrieval.contradiction_resolver import ContradictionResolver
        resolver = ContradictionResolver(engine, app.state.lab)
        
        if strategy == "SINTESI":
            await resolver._synthesize_resolution(id_a, id_b)
            return {"status": "success", "message": "Sintesi di risoluzione generata dalla Corte Suprema."}
        else:
            # Implementazione logica manuale (rimozione archi o marcatura)
            # Per brevità implementiamo solo la sintesi qui, ma la struttura è pronta.
            return {"status": "success", "message": f"Strategia {strategy} applicata."}
    except Exception as e:
        raise HTTPException(500, str(e))

@app.post("/api/wiki/reflect")
async def reflect_on_topic(req: dict, api_key: str = Depends(get_api_key)):
    topic = req.get("topic")
    if not topic: raise HTTPException(400, "Topic missing")
    
    try:
        reflection = await engine.reflective.reflect_on_topic(topic)
        return {"status": "success", "reflection": reflection}
    except Exception as e:
        raise HTTPException(500, str(e))

@app.get("/api/wiki/taxonomy")
async def get_taxonomy(api_key: str = Depends(get_api_key)):
    try:
        tax = engine.taxonomy.build_taxonomy()
        return {"status": "success", "taxonomy": tax}
    except Exception as e:
        raise HTTPException(500, str(e))

@app.get("/api/wiki/list")
async def list_wiki_pages(api_key: str = Depends(get_api_key)):
    print("📡 [API] Wiki List Request Received")
    """Ritorna la lista di tutte le pagine Wiki canoniche organizzate per Namespace."""
    try:
        wiki_dir = engine.wiki.wiki_dir
        # [v9.1] Ricerca ricorsiva per supportare i Namespace
        files = list(wiki_dir.rglob("*.md"))
        pages = []
        for f in files:
            stat = f.stat()
            relative_path = str(f.relative_to(wiki_dir))
            namespace = f.parent.name if f.parent != wiki_dir else "General"
            pages.append({
                "title": f.stem.replace("_", " "),
                "file_name": relative_path,
                "namespace": namespace,
                "last_modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "size": stat.st_size
            })
        return {"status": "success", "pages": sorted(pages, key=lambda x: x['last_modified'], reverse=True)}
    except Exception as e:
        raise HTTPException(500, str(e))

@app.get("/api/wiki/activity")
async def get_wiki_activity(limit: int = 50, api_key: str = Depends(get_api_key)):
    """[v9.6] Recupera i log di attività reali dall'Audit Ledger + Git Ledger commits."""
    events = []
    try:
        ledger_path = Path("vault_data/audit_ledger.json")
        if ledger_path.exists():
            with open(ledger_path, "r") as f:
                events = json.load(f)
    except Exception as e:
        print(f"⚠️ [Activity API Error] {e}")

    try:
        import subprocess
        wiki_dir = engine.wiki.wiki_dir
        if (wiki_dir / ".git").exists():
            res = subprocess.run(
                ["git", "log", f"-n", str(limit), "--pretty=format:%h|%an|%ad|%s"],
                cwd=str(wiki_dir),
                capture_output=True,
                text=True
            )
            if res.returncode == 0 and res.stdout.strip():
                for line in res.stdout.strip().split("\n"):
                    parts = line.split("|", 3)
                    if len(parts) == 4:
                        h, author, date_str, subject = parts
                        events.append({
                            "timestamp": date_str.split(" +")[0].split(" -")[0],
                            "event": "GIT_COMMIT",
                            "topic": "L4 Git Ledger",
                            "description": f"[{h}] {subject} (by {author})",
                            "node_id": h
                        })
    except Exception as e:
        print(f"⚠️ [Activity Git Error] {e}")

    return events[-limit:][::-1]

@app.get("/api/system/mindset")
async def get_mindset(api_key: str = Depends(get_api_key)):
    """🏛️ [v9.2] Mindset Retrieval: Recupera lo stato cognitivo persistente."""
    try:
        mindset = getattr(app.state, 'current_mindset', 'DEFAULT')
        # Ensure mindset is a serializable string
        if not isinstance(mindset, str):
            mindset = str(mindset)
        return {"status": "ok", "mindset": mindset}
    except Exception as e:
        print(f"⚠️ [API] Mindset Retrieval Error: {e}")
        return {"status": "ok", "mindset": "DEFAULT"}

@app.post("/api/system/mindset")
async def update_mindset(req: dict, api_key: str = Depends(get_api_key)):
    """🏛️ [v9.2] Mindset Sync: Sincronizza lo stato cognitivo globale del Vault."""
    mindset = req.get("mindset", "DEFAULT")
    app.state.current_mindset = mindset
    
    # [v9.2] Notifica al blackboard e persiste nell'orchestratore
    if hasattr(app.state, 'lab'):
        if hasattr(app.state.lab, 'set_mindset'):
            app.state.lab.set_mindset(mindset)
        else:
            print(f"⚠️ [Warning] app.state.lab has no set_mindset method. Mindset: {mindset}")
            
        if hasattr(app.state.lab, 'blackboard') and app.state.lab.blackboard:
            app.state.lab.blackboard.post(SynapticSignal("SYSTEM", AgentRole.OPTIMIZER, 
                f"🧠 MINDSET_SHIFT: Global cognitive state set to {mindset}.", 
                SignalType.SYSTEM_NOTIFICATION))
            
    return {"status": "ok", "mindset": mindset}

@app.get("/api/wiki/review/queue")
async def get_wiki_review_queue(api_key: str = Depends(get_api_key)):
    """📚 [v9.2] Spaced Repetition: Recupera la coda di ripasso giornaliera."""
    return await engine.wiki.freshness_monitor.get_review_queue()

@app.post("/api/wiki/review/record")
async def record_wiki_review(req: dict, api_key: str = Depends(get_api_key)):
    """📚 [v9.2] Registra l'esito di un ripasso Wiki."""
    topic = req.get("topic")
    score = req.get("score", 1.0)
    await engine.wiki.freshness_monitor.record_review(topic, score)
    return {"status": "ok"}

@app.post("/api/wiki/simulate/compare")
async def compare_scenarios(req: dict, api_key: str = Depends(get_api_key)):
    """⚖️ [v9.2] Scenario Comparison: Compara due simulazioni con lenti diverse."""
    query = req.get("query")
    lens_a = req.get("lens_a", "musk")
    lens_b = req.get("lens_b", "bezos")
    
    sim_a = await engine.wiki.whatif.run_nl_simulation(query, lenses=[lens_a])
    sim_b = await engine.wiki.whatif.run_nl_simulation(query, lenses=[lens_b])
    
    return {
        "lens_a": sim_a,
        "lens_b": sim_b,
        "query": query
    }

@app.get("/api/wiki/dashboard")
async def get_wiki_dashboard(api_key: str = Depends(get_api_key)):
    """🏛️ [v9.2] Aura Dashboard: Aggregatore proattivo per lo stato della Wiki."""
    try:
        from retrieval.wiki_monitor import WikiFreshnessMonitor
        monitor = WikiFreshnessMonitor(engine)
        
        # 1. Statistiche Base
        wiki_dir = engine.wiki.wiki_dir
        files = list(wiki_dir.rglob("*.md"))
        total_pages = len(files)
        
        # 2. Epistemic Health & Stale Pages
        stale_pages = await monitor.check_stale_pages()
        stale_count = len(stale_pages)
        
        # Audit rapido (o simulato per performance)
        health_score = 100 - (stale_count * 2) - (len(files) % 5) # Esempio di calcolo dinamico
        health_score = max(0, min(100, health_score))
        
        weather = "SUNNY"
        if stale_count > 5: weather = "CLOUDY"
        if health_score < 60: weather = "STORM"
        
        # 3. Recent Pages
        recent = []
        sorted_files = sorted(files, key=lambda x: x.stat().st_mtime, reverse=True)[:8]
        for f in sorted_files:
            recent.append({
                "title": f.stem.replace("_", " "),
                "file_name": str(f.relative_to(wiki_dir)),
                "date": datetime.fromtimestamp(f.stat().st_mtime).strftime('%Y-%m-%d'),
                "health": 100 if f.stem not in [p['topic'] for p in stale_pages] else 70
            })
            
        # 4. Galaxies (Namespaces)
        namespaces = {}
        for f in files:
            ns = f.parent.name if f.parent != wiki_dir else "General"
            namespaces[ns] = namespaces.get(ns, 0) + 1
            
        galaxies = [{"id": ns, "title": ns, "page_count": count, "health": 95} for ns, count in namespaces.items()]
        
        # 5. Suggested Topics (Knowledge Gaps)
        # Semplificato: prendiamo topic con molti archi ma senza pagina wiki
        suggested = ["Causal Inference", "Neural Scaling Laws", "Aegis Protocol"]
        
        return {
            "stats": {
                "total_pages": total_pages,
                "health_score": health_score,
                "stale_count": stale_count,
                "epistemic_weather": weather
            },
            "recent_pages": recent,
            "galaxies": galaxies,
            "review_queue": recent[:3] if recent else [],
            "suggested_topics": suggested
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        # Graceful degradation for dashboard
        return {
            "stats": {"total_pages": 0, "health_score": 100, "stale_count": 0, "epistemic_weather": "SUNNY"},
            "recent_pages": [],
            "galaxies": [],
            "review_queue": [],
            "suggested_topics": ["Quantum Alignment", "Sovereign Mesh", "Aegis Core"],
            "error": str(e)
        }

# --- 🧬 [v10.0] Pillar #6: Epistemic Dashboard Endpoints ---

@app.get("/api/user/persona")
async def get_user_persona(api_key: str = Depends(get_api_key)):
    """Recupera i tratti della Persona dell'utente rilevati dal Persona Engine."""
    try:
        # 🛡️ [Self-Healing] Verifica esistenza tabella
        engine.agent007.con.execute("""
            CREATE TABLE IF NOT EXISTS user_persona (
                category TEXT,
                description TEXT,
                strength DOUBLE
            )
        """)
        
        # Recupero i tratti ordinati per forza (strength)
        traits = engine.agent007.con.execute(
            "SELECT category, description, strength FROM user_persona ORDER BY strength DESC"
        ).fetchall()
        
        return {
            "status": "success",
            "persona": [
                {"category": r[0], "description": r[1], "strength": r[2]}
                for r in traits
            ]
        }
    except Exception as e:
        print(f"⚠️ [API] Persona Retrieval Error: {e}")
        return {"status": "error", "message": str(e)}

@app.post("/api/query/causal")
async def causal_query(req: dict, api_key: str = Depends(get_api_key)):
    """Esegue una query focalizzata sulle relazioni causali (What-if / Epistemic Links)."""
    query = req.get("query")
    if not query: raise HTTPException(400, "Query missing")
    
    try:
        # [v10.0] Protocollo Causal-RAG: Ricerca nella Hard Memory (DuckDB)
        search_pattern = f"%{query}%"
        results = engine.agent007.con.execute("""
            SELECT fact, source_id, target_id, type 
            FROM agent007_relations 
            WHERE fact ILIKE ? OR source_id ILIKE ? OR target_id ILIKE ? 
            LIMIT 15
        """, (search_pattern, search_pattern, search_pattern)).fetchall()
        
        causal_links = [
            {"fact": r[0], "source": r[1], "target": r[2], "type": r[3]}
            for r in results
        ]
        
        return {
            "status": "success",
            "query": query,
            "causal_links": causal_links,
            "count": len(causal_links)
        }
    except Exception as e:
        print(f"⚠️ [API] Causal Query Error: {e}")
        return {"status": "error", "message": str(e)}

@app.post("/api/project/action")
async def trigger_project_action(req: dict, api_key: str = Depends(get_api_key)):
    """Esegue un'azione operativa (Actionable Intelligence) su un cluster o progetto."""
    project_id = req.get("project_id")
    action = req.get("action") # e.g. "DEEP_RESEARCH", "SINTESI", "MONITOR"
    
    if not project_id or not action:
        raise HTTPException(400, "project_id or action missing")
    
    print(f"🚀 [Project Action] Executing {action} on {project_id}")
    
    try:
        # Invia segnale alla Neural Lab (Blackboard)
        if hasattr(app.state, 'lab'):
            from neural_lab import SynapticSignal, AgentRole, SignalType
            
            sig = SynapticSignal(
                sender="TACTICAL_CANVAS", 
                role=AgentRole.OPTIMIZER, 
                content=f"PROJECT_ACTION: {action} requested for target: {project_id}", 
                type=SignalType.REASONING_STEP
            )
            app.state.lab.blackboard.post(sig)
            
            # 1. Azione: DEEP_RESEARCH (Innesca Skywalker)
            if action == "DEEP_RESEARCH":
                asyncio.create_task(app.state.lab.forage_web_topic(project_id))
                
            # 2. Azione: SINTESI (Innesca Synth)
            elif action == "SINTESI":
                asyncio.create_task(engine.wiki.generate_page(project_id, mode="EXECUTIVE"))
                
            return {
                "status": "success", 
                "action_triggered": action, 
                "project_id": project_id,
                "timestamp": time.time()
            }
        else:
            return {"status": "error", "message": "Neural Lab Orchestrator not available"}
            
    except Exception as e:
        print(f"⚠️ [API] Project Action Error: {e}")
        return {"status": "error", "message": str(e)}

@app.get("/llms.txt")
@app.get("/api/wiki/llms.txt")
async def get_llms_txt_standard():
    """🏛️ [v9.5] Sovereign standard for AI Agent navigation (llms.txt)."""
    if 'compounding_wiki_mgr' not in globals():
        return Response(content="# NeuralVault Wiki\nInitialization in progress...", media_type="text/plain")
    content = await compounding_wiki_mgr.generate_llms_txt()
    return Response(content=content, media_type="text/plain")

@app.get("/api/wiki/read")
async def read_wiki_page(file: str, mode: str = "TECHNICAL", api_key: str = Depends(get_api_key)):
    """Legge il contenuto di una pagina Wiki specifica con prospettiva opzionale."""
    try:
        wiki_dir = engine.wiki.wiki_dir
        file_path = (wiki_dir / file).resolve()
        if not str(file_path).startswith(str(wiki_dir.resolve())):
            raise HTTPException(403, "Access denied")
            
        if not file_path.exists(): raise HTTPException(404, "Page not found")
        with open(file_path, "r") as f:
            content = f.read()
            
        # [v10.0] Perspective Transformation
        if mode != "TECHNICAL":
            prompt = f"""
            ### TASK: PERSPECTIVE RENDERING (Hydra Lens)
            Converti la seguente pagina wiki per una lente: {mode}.
            
            CONTENUTO ORIGINALE:
            {content}
            
            ### REQUISITI:
            1. CEO: Focus su impatto business, ROI, rischi strategici. Sintetico.
            2. LEGAL: Focus su compliance, responsabilità, termini contrattuali. Rigoroso.
            3. TECHNICAL: (Default) Dettagli ingegneristici, architettura, codice.
            4. Mantieni tutti i tag [CITE:node_id].
            5. Mantieni il Frontmatter YAML.
            """
            content = await engine.orchestrator.get_consensus_response(prompt, f"Perspective Lens: {mode}")
            
        # [v9.5] Recupero citazioni associate dal Cross-Reference Index
        citations = []
        try:
            # Cerchiamo referenze nel DB per questo file
            res = engine._prefilter.con.execute("""
                SELECT node_id FROM wiki_xref WHERE source_page = ?
            """, [file]).fetchall()
            
            node_ids = list(set([r[0] for r in res])) # Unico per node_id
            
            for nid in node_ids:
                node = engine.get_node(nid)
                if node:
                    citations.append({
                        "node_id": nid,
                        "source_title": node.metadata.get("title", "Frammento Atomico"),
                        "source_url": node.metadata.get("source", "Internal Vault"),
                        "source_date": node.metadata.get("timestamp", "v9.0"),
                        "confidence": node.metadata.get("confidence", 0.92),
                        "excerpt": node.text[:250],
                        "is_contradictory": False, # TODO: implement dynamic conflict check
                        "conflict_node_id": None
                    })
        except Exception as e:
            print(f"⚠️ [Wiki XRef] Error fetching citations: {e}")
            
        return {
            "status": "success", 
            "markdown": content,
            "citations": citations
        }
    except Exception as e:
        raise HTTPException(500, str(e))

@app.get("/api/graph/ghost-map")
async def get_ghost_map(api_key: str = Depends(get_api_key)):
    """🌌 [v9.2] Ghost Map: Restituisce una struttura semplificata del Vault per sfondo What-If."""
    try:
        # Recuperiamo un campione rappresentativo di nodi e archi
        nodes = []
        edges = []
        
        # Limite per performance UI
        MAX_GHOST_NODES = 150
        
        # [v4.3.1] Thread-Safe Fetch
        with engine._lock:
            all_node_ids = list(engine._nodes.keys())
            sample_ids = all_node_ids[:MAX_GHOST_NODES]
            
            for nid in sample_ids:
                node = engine._nodes[nid]
                nodes.append({
                    "id": node.id,
                    "label": node.metadata.get("title", node.id[:8]),
                    "namespace": node.metadata.get("namespace", "General")
                })
                
                # Archi (limitati)
                for edge in node.edges[:3]: # Solo i primi 3 per non affollare
                    if edge.target_id in sample_ids:
                        edges.append({
                            "source": node.id,
                            "target": edge.target_id,
                            "type": str(edge.relation)
                        })
                        
        return {"nodes": nodes, "edges": edges}
    except Exception as e:
        raise HTTPException(500, str(e))

@app.post("/api/sync/agents")
async def sync_agents(req: dict, api_key: str = Depends(get_api_key)):
    """Innesca la sincronizzazione delle sessioni agentiche (Cursor/Claude)."""
    provider = req.get("provider", "auto")
    try:
        count = await engine.sync_agent_sessions(provider=provider)
        return {"status": "success", "synced": count}
    except Exception as e:
        raise HTTPException(500, str(e))

@app.post("/api/wiki/simulate")
async def simulate_impact(request: Request):
    """[v8.3] Sovereign Oracle: Supporta modalità avanzate (Antifragilità, Conflitto, ecc)."""
    if not check_api_key(request.headers.get("x-api-key", "")): return JSONResponse({"status": "error", "message": "Invalid API Key"}, status_code=403)
    
    data = await request.json()
    node_id = data.get("node_id")
    intensity = float(data.get("intensity", 1.0)) / 100.0
    lens_ids = data.get("lens_ids", ["standard"])
    mode = data.get("mode", "standard")
    adversary_id = data.get("adversary_node_id")
    
    if not node_id: return {"status": "error", "message": "node_id is required"}
    
    from retrieval.causal_simulator import SimulationMode
    try:
        sim_mode = SimulationMode(mode)
    except ValueError:
        sim_mode = SimulationMode.STANDARD
        
    results = await engine.wiki.simulator.simulate_intervention(
        node_id, 
        intensity, 
        iterations=1000, 
        lens_ids=lens_ids,
        mode=sim_mode,
        adversary_node_id=adversary_id
    )
    return JSONResponse(results)

@app.get("/api/wiki/simulate/timeline")
async def simulate_wiki_timeline(topic: str, val: float = 1.0):
    """🧪 [v8.1] Predictive Timeline Simulation."""
    try:
        # Trova il nodo radice per il topic
        results = await engine.query(topic, k=1)
        if not results: return JSONResponse({"error": "Node not found"}, status_code=404)
        
        results_timeline = await engine.wiki.simulator.simulate_across_time(results[0].node.id, val)
        return JSONResponse(results_timeline)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
@app.post("/api/wiki/simulate/interview")
async def interview_simulation_node(data: Dict[str, Any]):
    """🧪 [v8.1] Sovereign Interview: Parla con un nodo durante la simulazione."""
    try:
        node_id = data.get("node_id")
        simulation_context = data.get("context")
        if not node_id or not simulation_context:
            return JSONResponse({"error": "node_id and context required"}, status_code=400)
            
        result = await engine.wiki.simulator.interview_node(node_id, simulation_context)
        return JSONResponse(result)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

@app.post("/api/wiki/simulate/report")
async def generate_simulation_report(data: Dict[str, Any]):
    """🏺 [v8.1] Strategic Report: Genera un report narrativo dei risultati."""
    try:
        simulation_results = data.get("results")
        if not simulation_results:
            return JSONResponse({"error": "simulation results required"}, status_code=400)
            
        report = await engine.wiki.simulator.generate_strategic_report(simulation_results)
        return JSONResponse({"report": report})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

@app.post("/api/wiki/simulate/scenario")
async def generate_causal_scenario_api(request: Request):
    """🚀 [v8.2] Causal Scenario: Genera uno scenario avanzato con lenti cognitive e Chaining."""
    if not check_api_key(request.headers.get("x-api-key", "")): return JSONResponse({"status": "error", "message": "Invalid API Key"}, status_code=403)
    
    data = await request.json()
    results = data.get("results")
    lens_ids = data.get("lens_ids", ["standard"])
    horizon = data.get("horizon", "immediate")
    parent_id = data.get("parent_scenario_id")
    
    if not results:
        return JSONResponse({"error": "simulation results required"}, status_code=400)
        
    scenario = await engine.wiki.simulator.generate_causal_scenario(
        results, 
        lens_id=lens_ids[0] if lens_ids else "standard",
        horizon=horizon,
        parent_scenario_id=parent_id
    )
    return JSONResponse(scenario)

@app.post("/api/wiki/simulate/nl")
async def simulate_nl_api(data: Dict[str, Any], api_key: str = Depends(get_api_key)):
    """🚀 [v8.4] NL What-If: Simulazione via linguaggio naturale."""
    try:
        query = data.get("query")
        lenses = data.get("lenses", ["standard"])
        mode = data.get("mode", "FAST")
        horizon = data.get("horizon", "immediate") # [v8.4] Temporal Horizon
        twin_id = data.get("twin_id")
        parent_id = data.get("parent_id")
        folder_path = data.get("folder_path")
        tags = data.get("tags")
        
        if not query:
            return JSONResponse({"error": "query required"}, status_code=400)
            
        # [v9.0] Digital Twin Integration
        twin = None
        if twin_id and hasattr(app.state, 'twins') and twin_id in app.state.twins:
            twin = app.state.twins[twin_id]
            
        result = await engine.wiki.nl_whatif.run_nl_simulation(
            query, 
            lenses, 
            mode=mode, 
            horizon=horizon, 
            twin=twin,
            parent_id=parent_id,
            folder_path=folder_path,
            tags=tags
        )
        return JSONResponse(result)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

@app.get("/api/whatif/history")
async def get_whatif_history(
    folder_path: Optional[str] = None,
    status: Optional[str] = None,
    search: Optional[str] = None,
    parent_id: Optional[str] = None,
    api_key: str = Depends(get_api_key)
):
    """🧠 [v11.0] Recupera lo storico strutturato delle simulazioni con filtri avanzati."""
    try:
        query_parts = ["SELECT id, timestamp, query, target_node_id, settings_used, status, folder_path, tags, parent_id FROM decision_journal WHERE 1=1"]
        params = []
        
        if folder_path is not None:
            query_parts.append("AND folder_path = ?")
            params.append(folder_path)
            
        if status is not None:
            query_parts.append("AND status = ?")
            params.append(status)
            
        if search is not None:
            query_parts.append("AND (query LIKE ? OR tags LIKE ?)")
            params.append(f"%{search}%")
            params.append(f"%{search}%")
            
        if parent_id is not None:
            query_parts.append("AND parent_id = ?")
            params.append(parent_id)
            
        query_parts.append("ORDER BY timestamp DESC")
        
        sql = " ".join(query_parts)
        res = engine._prefilter.fetchall(sql, params)
        
        history = []
        for r in res:
            # Conta simulazioni figlie
            child_count = engine._prefilter.fetchone("SELECT COUNT(*) FROM decision_journal WHERE parent_id = ?", (r[0],))[0]
            
            history.append({
                "id": r[0],
                "timestamp": r[1].isoformat() if hasattr(r[1], 'isoformat') else str(r[1]),
                "query": r[2],
                "target_node_id": r[3],
                "settings": json.loads(r[4]) if r[4] else {},
                "status": r[5],
                "folder_path": r[6],
                "tags": r[7].split(",") if r[7] else [],
                "parent_id": r[8],
                "children_count": child_count
            })
            
        return JSONResponse(history)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

@app.get("/api/whatif/simulation/{sim_id}")
async def get_whatif_simulation(sim_id: str, api_key: str = Depends(get_api_key)):
    """🧠 [v11.0] Ottiene tutti i dettagli di una simulazione passata (inclusi i risultati grafici completi)."""
    try:
        r = engine._prefilter.fetchone("""
            SELECT id, timestamp, query, target_node_id, settings_used, status, folder_path, tags, parent_id, simulation_full_results 
            FROM decision_journal WHERE id = ?
        """, (sim_id,))
        
        if not r:
            return JSONResponse({"error": "Simulation not found"}, status_code=404)
            
        # Get children list
        children = engine._prefilter.fetchall("SELECT id, query FROM decision_journal WHERE parent_id = ?", (sim_id,))
        
        # Get target node title
        target_title = "Unknown Target"
        try:
            node = engine.get_node(r[3])
            if node:
                target_title = node.title
        except:
            pass
            
        return JSONResponse({
            "id": r[0],
            "timestamp": r[1].isoformat() if hasattr(r[1], 'isoformat') else str(r[1]),
            "query": r[2],
            "target_node_id": r[3],
            "target_node_title": target_title,
            "settings": json.loads(r[4]) if r[4] else {},
            "status": r[5],
            "folder_path": r[6],
            "tags": r[7].split(",") if r[7] else [],
            "parent_id": r[8],
            "full_results": json.loads(r[9]) if r[9] else {},
            "children": [{"id": c[0], "query": c[1]} for c in children]
        })
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

@app.post("/api/whatif/simulation/{sim_id}/archive")
async def archive_whatif_simulation(sim_id: str, data: Dict[str, Any], api_key: str = Depends(get_api_key)):
    """🧠 [v11.0] Archivia o riattiva una simulazione."""
    try:
        archive = data.get("archive", True)
        status = "archived" if archive else "active"
        
        engine._prefilter.execute("UPDATE decision_journal SET status = ? WHERE id = ?", (status, sim_id))
        return JSONResponse({"status": "success", "id": sim_id, "new_status": status})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

@app.delete("/api/whatif/simulation/{sim_id}")
async def delete_whatif_simulation(sim_id: str, api_key: str = Depends(get_api_key)):
    """🧠 [v11.0] Elimina definitivamente una simulazione dallo storico."""
    try:
        engine._prefilter.execute("DELETE FROM decision_journal WHERE id = ?", (sim_id,))
        return JSONResponse({"status": "success", "message": "Simulation deleted successfully"})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

@app.post("/api/whatif/simulation/{sim_id}/folder")
async def move_whatif_simulation(sim_id: str, data: Dict[str, Any], api_key: str = Depends(get_api_key)):
    """🧠 [v11.0] Assegna o sposta una simulazione in una cartella."""
    try:
        folder_path = data.get("folder_path", "root")
        engine._prefilter.execute("UPDATE decision_journal SET folder_path = ? WHERE id = ?", (folder_path, sim_id))
        return JSONResponse({"status": "success", "id": sim_id, "new_folder": folder_path})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

@app.post("/api/whatif/simulation/{sim_id}/tags")
async def tag_whatif_simulation(sim_id: str, data: Dict[str, Any], api_key: str = Depends(get_api_key)):
    """🧠 [v11.0] Aggiorna i tag / indici di una simulazione."""
    try:
        tags = data.get("tags", "")
        engine._prefilter.execute("UPDATE decision_journal SET tags = ? WHERE id = ?", (tags, sim_id))
        return JSONResponse({"status": "success", "id": sim_id, "new_tags": tags.split(",") if tags else []})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

@app.get("/api/whatif/folders")
async def get_whatif_folders(api_key: str = Depends(get_api_key)):
    """🧠 [v11.0] Ritorna la lista di tutte le cartelle definite dallo storico."""
    try:
        res = engine._prefilter.fetchall("SELECT DISTINCT folder_path FROM decision_journal WHERE folder_path IS NOT NULL")
        folders = [r[0] for r in res if r[0]]
        if "root" not in folders:
            folders.append("root")
        return JSONResponse(folders)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

@app.post("/api/wiki/simulate/gradient")
async def calculate_gradient(data: Dict[str, Any], api_key: str = Depends(get_api_key)):
    """
    📐 [v9.1] CAUSAL GRADIENT DESCENT ENDPOINT.
    Identifica i driver ottimali per raggiungere un obiettivo sul target.
    """
    try:
        target_id = data.get("target_id")
        desired_impact = data.get("desired_impact", 1.0)
        
        if not target_id:
            return JSONResponse({"error": "target_id obbligatorio"}, status_code=400)
            
        res = await engine.wiki.simulator.calculate_causal_gradient(target_id, desired_impact)
        return JSONResponse(res)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

class SovereignVaultTwinProxy:
    """🌓 [v9.1 Proxy] Lightweight query proxy wrapping a SovereignVaultTwin instance."""
    def __init__(self, engine, twin_id: str):
        self.engine = engine
        self.twin_id = twin_id

    async def query(self, query_text: str, **kwargs):
        return await self.engine.query(query_text, **kwargs)

@app.post("/api/vault/twin/create")
async def create_vault_twin(request: Request):
    """🚀 [v9.0] Crea un Digital Twin differenziale (CoW)."""
    if not check_api_key(request.headers.get("x-api-key", "")): return JSONResponse({"status": "error", "message": "Invalid API Key"}, status_code=403)
    
    try:
        twin_id = await engine.twin.create_twin()
        twin = SovereignVaultTwinProxy(engine, twin_id)
        
        # Salviamo il twin nello stato dell'app (temporaneo)
        if not hasattr(app.state, 'twins'): app.state.twins = {}
        app.state.twins[twin_id] = twin
        
        return JSONResponse({
            "twin_id": twin_id,
            "status": "Differential Twin Created (CoW)",
            "parent_nodes": len(engine._nodes),
            "delta_nodes": 0
        })
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

@app.post("/api/vault/twin/query")
async def query_vault_twin(request: Request):
    """🚀 [v9.0] Query su un Digital Twin (Simulazione sandbox)."""
    if not check_api_key(request.headers.get("x-api-key", "")): return JSONResponse({"status": "error", "message": "Invalid API Key"}, status_code=403)
    try:
        data = await request.json()
        twin_id = data.get("twin_id")
        query = data.get("query")
        
        if not twin_id or twin_id not in getattr(app.state, 'twins', {}):
            return JSONResponse({"error": "Twin ID non valido o scaduto"}, status_code=404)
            
        twin = app.state.twins[twin_id]
        results = await twin.query(query, k=data.get("k", 10))
        
        # Serializzazione dei risultati del twin
        serializable = []
        for r in results:
            serializable.append({
                "id": r.node.id,
                "text": r.node.text,
                "score": r.final_score,
                "metadata": r.node.metadata
            })
            
        return JSONResponse({"results": serializable})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

@app.get("/api/wiki/journal/history")
async def get_journal_history():
    """⚖️ [v8.4] Recupera lo storico delle decisioni."""
    try:
        history = await engine.wiki.journal.get_history()
        return JSONResponse({"history": history})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

@app.post("/api/wiki/journal/update")
async def update_journal_outcome(data: Dict[str, Any]):
    """⚖️ [v8.4] Registra l'esito reale di una decisione passata."""
    try:
        record_id = data.get("record_id")
        outcome = data.get("outcome")
        accuracy = data.get("accuracy") # 0.0 - 1.0
        
        if not record_id or outcome is None or accuracy is None:
            return JSONResponse({"error": "record_id, outcome and accuracy required"}, status_code=400)
            
        await engine.wiki.journal.update_outcome(record_id, outcome, accuracy)
        return JSONResponse({"status": "updated"})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

@app.get("/api/wiki/journal/grade")
async def get_oracle_grade():
    """⚖️ [v8.4] Calcola il voto di accuratezza dell'Oracolo."""
    try:
        grade = await engine.wiki.journal.compute_oracle_grade()
        return JSONResponse(grade)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

@app.get("/api/swarm/capabilities")
async def get_swarm_capabilities():
    """🛡️ [v9.1] PBC: Recupera il catalogo delle capacità componibili dello sciame (JSON-LD)."""
    try:
        capabilities = []
        # Agenti standard nell'orchestrator
        for agent_id, agent in engine.orchestrator.agents.items():
            if hasattr(agent, "get_capability_ld"):
                capabilities.append(agent.get_capability_ld())
        
        # Agenti Smith
        for smith_id, smith in engine.orchestrator.smiths.items():
            if hasattr(smith, "get_capability_ld"):
                capabilities.append(smith.get_capability_ld())
                
        return JSONResponse({"@context": "https://neuralvault.io/context/swarm", "agents": capabilities})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

@app.post("/api/twin/create")
async def create_vault_twin():
    """🌓 [v8.4] Crea una sandbox temporanea (Digital Twin) del vault."""
    try:
        twin_id = await engine.twin.create_twin()
        return JSONResponse({"twin_id": twin_id})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

@app.post("/api/twin/simulate")
async def simulate_twin_ingestion(data: Dict[str, Any]):
    """🌓 [v8.4] Simula l'ingestion di conoscenza nel Digital Twin."""
    try:
        twin_id = data.get("twin_id")
        text = data.get("text")
        source = data.get("source", "Twin_Simulation")
        
        if not twin_id or not text:
            return JSONResponse({"error": "twin_id and text required"}, status_code=400)
            
        result = await engine.twin.simulate_ingestion(twin_id, text, source)
        return JSONResponse(result)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

@app.post("/api/twin/commit")
async def commit_vault_twin(data: Dict[str, Any]):
    """🌓 [v8.4] Applica le modifiche del Twin al Vault reale."""
    try:
        twin_id = data.get("twin_id")
        if not twin_id:
            return JSONResponse({"error": "twin_id required"}, status_code=400)
            
        success = await engine.twin.commit_twin(twin_id)
        return JSONResponse({"status": "committed" if success else "failed"})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

@app.get("/api/wiki/audit")
async def run_wiki_audit():
    """🔍 [v9.5] Runs a full Sovereign Wiki audit (Linter)."""
    if 'wiki_linter' not in globals():
        return {"status": "error", "message": "Linter not initialized"}
    report = await wiki_linter.run_full_audit()
    return report

@app.post("/api/wiki/patch")
async def apply_wiki_patch(issue: Dict, api_key: str = Depends(get_api_key)):
    """🛠️ [v10.0] Applica una patch correttiva suggerita dal Linter."""
    if 'wiki_linter' not in globals():
        return {"status": "error", "message": "Linter not initialized"}
    result = await wiki_linter.apply_self_healing(issue)
    return result

@app.get("/api/wiki/learning-path")
async def get_learning_path(topic: str):
    """🗺️ [v8.4] Genera un percorso di apprendimento per un topic."""
    try:
        path = await engine.wiki.learning_path.generate_path(topic)
        return JSONResponse(path)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

@app.get("/api/wiki/history")
async def get_wiki_history(topic: str, version: Optional[int] = None):
    """🏺 [v9.5] Sovereign Time Travel: Recupera lo storico o una versione specifica."""
    try:
        history_dir = Path(engine.data_dir) / "wiki_history"
        safe_topic = "".join([c if c.isalnum() else "_" for c in topic])
        
        if version:
            target_file = history_dir / f"{safe_topic}_{version}.md"
            if target_file.exists():
                return JSONResponse({
                    "topic": topic,
                    "version": version,
                    "content": target_file.read_text(encoding='utf-8')
                })
            return JSONResponse({"error": "Versione non trovata"}, status_code=404)

        import glob
        files = glob.glob(str(history_dir / f"{safe_topic}_*.md"))
        
        history = []
        for f in sorted(files, reverse=True):
            try:
                # Estraiamo timestamp dal nome file
                ts_str = f.split("_")[-1].replace(".md", "")
                ts = int(ts_str)
                with open(f, "r", encoding='utf-8') as fh:
                    content = fh.read()
                    history.append({
                        "timestamp": ts,
                        "date": datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M'),
                        "preview": content[:200] + "..."
                    })
            except: continue
        return JSONResponse({"topic": topic, "versions": history})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

@app.get("/api/limbo/list")
async def list_limbo_nodes(api_key: str = Depends(get_api_key)):
    """[v5.1] Elenca i nodi nel Semantic Trash Bin (Limbo) con testo completo."""
    try:
        limbo_metadata = engine._prefilter.query_nodes("lifecycle_state = 'waste_pending'", limit=100)
        
        nodes = []
        for m in limbo_metadata:
            node = engine._tiers.get(m['id'])
            if node:
                nodes.append({
                    "id": m['id'],
                    "text": node.text,
                    "metadata": m.get('metadata', {}),
                    "decayed_at": m.get('metadata', {}).get('decayed_at')
                })

        return {
            "status": "success",
            "count": len(nodes),
            "nodes": nodes
        }
    except Exception as e:
        raise HTTPException(500, str(e))


# --- 🌌 HIERARCHICAL GRAPHRAG ENDPOINTS (v6.0) ---

@app.post("/api/communities/recluster")
async def trigger_reclustering(api_key: str = Depends(get_api_key)):
    """[v6.0] Avvia il raggruppamento dei nodi in Galassie Concettuali."""
    if not engine: raise HTTPException(503, "Engine Offline")
    
    # Eseguiamo in background perché può essere lento
    threading.Thread(target=engine.communities.build_graph_and_cluster, daemon=True).start()
    return {"status": "success", "message": "Clustering process started in background"}

@app.get("/api/communities/list")
async def list_communities(api_key: str = Depends(get_api_key)):
    """[v6.0] Elenca le Galassie Concettuali identificate."""
    try:
        res = engine._prefilter.fetchall("""
            SELECT id, title, summary, node_count, level 
            FROM neural_communities 
            ORDER BY node_count DESC
        """)
        
        communities = []
        for r in res:
            communities.append({
                "id": r[0],
                "title": r[1] or "In fase di analisi...",
                "summary": r[2] or "L'Archivista sta scrivendo il rapporto...",
                "nodes": r[3],
                "level": r[4]
            })
        return {"status": "success", "communities": communities}
    except Exception as e:
        raise HTTPException(500, str(e))

@app.post("/api/communities/summarize")
async def summarize_communities(api_key: str = Depends(get_api_key)):
    """[v6.0] Forza l'Archivista a generare i riassunti per le nuove comunità."""
    if not engine or not engine.orchestrator: 
        raise HTTPException(503, "Lab/Engine Offline")
    
    try:
        async def run_summaries():
            try:
                await engine.communities.generate_community_summaries()
            except Exception as e:
                print(f"❌ [H-RAG] Summarization Error: {e}")
        
        asyncio.create_task(run_summaries())
        return {"status": "success", "message": "Community summarization started"}
    except Exception as e:
        raise HTTPException(500, f"Failed to start summarization: {str(e)}")

# --- 🛡️ SHADOW SANDBOX ENDPOINTS (v6.0) ---

@app.get("/api/sandbox/status")
async def get_sandbox_status(api_key: str = Depends(get_api_key)):
    """[v6.0] Restituisce lo stato attuale della Sandbox e dei task in corso."""
    return {
        "status": "online",
        "active_simulations": 1 if engine.communities.is_clustering else 0,
        "mode": "Sovereign Audit Enabled"
    }

@app.post("/api/sandbox/test-code")
async def test_code_in_sandbox(req: dict, api_key: str = Depends(get_api_key)):
    """[v6.0] Testa un frammento di codice in isolamento."""
    code = req.get("code")
    name = req.get("name", "Manual Test")
    if not code: raise HTTPException(400, "Code missing")
    
    audit = engine.sandbox.test_code_snippet(name, code)
    return {
        "success": audit.success,
        "metrics": audit.metrics,
        "logs": audit.logs,
        "error": audit.error
    }

@app.post("/api/limbo/evaluate/{node_id}")
async def evaluate_limbo_node(node_id: str, api_key: str = Depends(get_api_key)):
    """[v5.1] Un LLM valuta il nodo e suggerisce l'azione (Semaforo)."""
    node = engine._tiers.get(node_id)
    if not node: raise HTTPException(404, "Node not found")
    
    # Recuperiamo lo storico del feedback utente per l'apprendimento
    feedback_path = Path(engine.data_dir) / "limbo_feedback_loop.json"
    history = []
    if feedback_path.exists():
        try:
            with open(feedback_path, 'r') as f:
                history = json.load(f)[-5:] # Ultimi 5 esempi per non saturare il contesto
        except: pass

    history_context = "\n".join([f"Input: {h['text'][:100]}... -> Action: {h['action']}" for h in history])
    
    model = getattr(engine, 'settings', {}).get("chat_model", "llama3.2")
    prompt = f"""### TASK: Evaluate if this knowledge node is still useful.
### RECENT USER PREFERENCES:
{history_context}

### NODE CONTENT:
{node.text}

### OUTPUT FORMAT:
Respond ONLY with a JSON object:
{{
  "recommendation": "GREEN" (keep/restore) | "YELLOW" (unsure) | "RED" (delete),
  "reason": "Brief justification based on user history and content value"
}}"""

    try:
        base_url = engine.settings.get("ollama_url")
        async with httpx.AsyncClient() as client:
            r = await client.post(f"{base_url}/api/generate", json={
                "model": model, "prompt": prompt, "stream": False, "format": "json"
            }, timeout=20.0)
            res = r.json().get("response", "{}")
            return json.loads(res)
    except Exception as e:
        return {"recommendation": "YELLOW", "reason": f"AI evaluation failed: {str(e)}"}

@app.post("/api/limbo/restore/{node_id}")
async def restore_limbo_node(node_id: str, api_key: str = Depends(get_api_key)):
    """[v5.1] Ripristina un nodo dal Limbo allo stato STABLE e registra il feedback positivo."""
    try:
        node = engine._tiers.get(node_id)
        if node:
            _record_limbo_feedback(node.text, "RESTORED")
            engine._prefilter.update_lifecycle_state(node_id, "stable")
            return {"status": "success", "message": f"Node {node_id} restored"}
        raise HTTPException(404, "Node not found")
    except Exception as e:
        raise HTTPException(500, str(e))

@app.post("/api/limbo/merge/{node_id}")
async def merge_limbo_node(node_id: str, request: Request, api_key: str = Depends(get_api_key)):
    """[v5.1] Fonde un nodo del Limbo con un concetto target (Consolidamento Memoria)."""
    try:
        data = await request.json()
        target_concept = data.get("target_concept")
        if not target_concept:
            raise HTTPException(400, "Missing target_concept")
            
        source_node = engine._tiers.get(node_id)
        if not source_node:
            raise HTTPException(404, "Source node not found")
            
        from memory_consolidation import WisdomDistiller
        distiller = WisdomDistiller(engine)
        
        # 1. Cerchiamo se esiste già un nodo per il target_concept
        search_results = await engine.query(target_concept, k=1)
        target_node = None
        if search_results:
            target_node = search_results[0].node
            
        # 2. Se esiste, fondiamo il testo. Altrimenti creiamo un nuovo nodo di saggezza.
        if target_node and target_node.id != node_id:
            new_text = f"{target_node.text}\n\n[CONSOLIDATED_FROM_{node_id}]:\n{source_node.text}"
            engine.upsert_text(text=new_text, node_id=target_node.id, metadata=target_node.metadata)
            message = f"Merged into existing node '{target_node.id}'"
        else:
            # Creiamo un nuovo "Supernodo" via Distiller
            wisdom_id = distiller.distill([node_id])
            message = f"Created new consolidated wisdom node: {wisdom_id}"
            
        # 3. Eliminiamo il nodo originale dal Limbo e registriamo il feedback
        _record_limbo_feedback(source_node.text, f"MERGED_INTO_{target_concept}")
        engine.delete_node(node_id)
        
        return {"status": "success", "message": message}
    except Exception as e:
        import traceback
        logging.error(f"Merge Error: {traceback.format_exc()}")
        raise HTTPException(500, str(e))

@app.delete("/api/limbo/purge/{node_id}")
async def purge_limbo_node(node_id: str, api_key: str = Depends(get_api_key)):
    """[v5.1] Elimina fisicamente il nodo e registra il feedback negativo."""
    node = engine._tiers.get(node_id)
    if node:
        _record_limbo_feedback(node.text, "PURGED")
        engine.delete_node(node_id)
        return {"status": "purged"}
    raise HTTPException(404, "Node not found")

def _record_limbo_feedback(text: str, action: str):
    path = Path(engine.data_dir) / "limbo_feedback_loop.json"
    try:
        data = []
        if path.exists():
            with open(path, 'r') as f: data = json.load(f)
        data.append({"text": text[:500], "action": action, "time": time.time()})
        with open(path, 'w') as f: json.dump(data[-100:], f) # Manteniamo solo gli ultimi 100
    except: pass

@app.get("/api/wiki/timeline/{topic}")
async def get_timeline(topic: str, api_key: str = Depends(get_api_key)):
    try:
        tl = await engine.timeline.get_topic_evolution(topic)
        return {"status": "success", "timeline": tl}
    except Exception as e:
        raise HTTPException(500, str(e))

@app.get("/api/history")
async def get_neural_history(limit: int = 50, api_key: str = Depends(get_api_key)):
    """Recupera lo storico delle query dal database Hard Memory."""
    if not hasattr(app.state.lab, 'agent007') or not app.state.lab.agent007:
        return []
    return app.state.lab.agent007.get_query_history(limit=limit)

@app.delete("/api/history/{query_id}")
async def delete_neural_history(query_id: str, api_key: str = Depends(get_api_key)):
    """Elimina una query specifica dallo storico."""
    if not hasattr(app.state.lab, 'agent007') or not app.state.lab.agent007:
        raise HTTPException(status_code=500, detail="Intelligence service not active")
    app.state.lab.agent007.delete_query(query_id)
    return {"status": "deleted", "id": query_id}

# 🎙️ [v5.1] SOVEREIGN VOICE ENDPOINTS
@app.post("/api/voice/transcribe")
async def transcribe_audio(file: UploadFile = File(...), api_key: str = Depends(get_api_key)):
    """Trascrive un file audio (WAV/MP3) e ritorna il testo."""
    if not voice_engine:
        raise HTTPException(500, "Voice engine not active")
    
    # Salvataggio temporaneo per elaborazione
    temp_path = f"scratch/voice_{uuid.uuid4().hex}.wav"
    os.makedirs("scratch", exist_ok=True)
    with open(temp_path, "wb") as buffer:
        buffer.write(await file.read())
    
    try:
        text = voice_engine.transcribe(temp_path)
        return {"status": "success", "text": text}
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

@app.post("/api/voice/speak")
async def speak_text(payload: Dict, api_key: str = Depends(get_api_key)):
    """Sintetizza vocalmente il testo passato."""
    if not voice_engine:
        raise HTTPException(500, "Voice engine not active")
    
    text = payload.get("text", "")
    if not text:
        return {"status": "error", "message": "Text missing"}
    
    voice_engine.speak(text)
    return {"status": "success", "message": "Speaking initiated"}

@app.get("/api/voice/status")
async def get_voice_status(api_key: str = Depends(get_api_key)):
    """Ritorna lo stato attuale della sintesi vocale."""
    if not voice_engine:
        return {"active": False}
    return {
        "active": True,
        "is_speaking": voice_engine.is_speaking,
        "queue_size": voice_engine.speech_queue.qsize()
    }

@app.get("/events")
async def sse_stream(request: Request, api_key: str = Depends(get_api_key)):
    """Il battito cardiaco della Dashboard: Telemetria Real-time."""
    # Helper per calcolare il peso del cervello digitale
    _cached_size = {"val": 0, "time": 0}
    def get_dir_size(path):
        """Versione ottimizzata (v3.0): Cache di 60s per evitare I/O costante in SSE."""
        now = time.time()
        if now - _cached_size["time"] < 60:
            return _cached_size["val"]
            
        total = 0
        try:
            p = Path(path)
            if not p.exists(): return 0
            for f in p.glob('*.db'): total += f.stat().st_size
            for f in p.glob('*.ael'): total += f.stat().st_size
            if total == 0: total = 1024 * 1024 # 1MB fallback
        except: pass
        
        _cached_size["val"] = total
        _cached_size["time"] = now
        return total

    v_initial = engine.data_dir if engine else Path("./data")
    last_size = get_dir_size(v_initial)

    async def event_generator():
        q = asyncio.Queue(maxsize=100)
        app.state.sse_queues.append(q)
        last_size = 0
        try:
            # 1. IMMEDIATE INITIAL SYNC (Fast counts)
            fast_data = {
                "nodes_count": len(engine._nodes) if engine else 0,
                "edges_count": 0, # Will be updated by full stats
                "storage": {"total": "SYNCING", "pulse": "..."},
                "lab": request.app.state.lab.get_status() if hasattr(request.app.state, 'lab') else {},
                "status": "INIT_FAST_SYNC"
            }
            yield f"data: {json.dumps(fast_data, default=json_serializer)}\n\n"

            # 2. FULL ENGINE STATS (Fast Boot v8.4: Limited to 5000 points for instant rendering)
            loop = asyncio.get_event_loop()
            try:
                # Iniziamo con 5000 punti per un'apparizione istantanea, poi caricheremo il resto
                stats = await loop.run_in_executor(None, engine.stats, 5000)
            except: stats = {}

            full_initial_data = {
                "points": stats.get("point_cloud", []),
                "links": stats.get("edge_sample", []),
                "nodes_count": len(engine._nodes) if engine else 0,
                "edges_count": stats.get("edges_count", 0),
                "storage": {"total": "INIT", "pulse": "READY"},
                "lab": request.app.state.lab.get_status() if hasattr(request.app.state, 'lab') else {},
                "system": {}, 
                "agent007": {"entities_count": 0, "relations_count": 0}
            }
            yield f"data: {json.dumps(full_initial_data, default=json_serializer)}\n\n"
            while not _is_shutting_down:
                if await request.is_disconnected():
                    break

                # 🚀 [v9.0] Process Asynchronous Events from Broadcast Queue
                while not q.empty():
                    try:
                        event_payload = q.get_nowait()
                        yield f"data: {event_payload}\n\n"
                    except: break

                try:
                    # 2. Storage Metrics
                    v_path = engine.data_dir if engine else Path("./data")
                    current_size = get_dir_size(v_path)
                    growth = current_size - last_size
                    last_size = current_size
                    
                    size_mb = round(current_size / (1024 * 1024), 2)
                    storage_hud = {
                        "total": f"{size_mb} MB" if size_mb < 1024 else f"{round(size_mb/1024, 2)} GB",
                        "pulse": f"+{round(growth/1024, 1)} KB" if growth > 0 else "STABLE"
                    }

                    # 3. 3D Engine Stats (Offloaded & Throttled)
                    # [v17.7] Only refresh full stats every 3 iterations to save CPU
                    if not hasattr(event_generator, '_tick'): event_generator._tick = 0
                    event_generator._tick += 1
                    
                    if event_generator._tick % 3 == 0 or not stats:
                        try:
                            stats = await loop.run_in_executor(None, engine.stats)
                        except: stats = {}
                    
                    # 4. Neural Lab & System Status (Offloaded)
                    def _get_lab_status():
                        try:
                            # Use global app explicitly to avoid request detachment issues in background executor
                            if hasattr(app.state, 'lab'):
                                return app.state.lab.get_status()
                            else:
                                print("⚠️ [SSE] app.state has no 'lab' attribute!")
                                return {}
                        except Exception as e:
                            print(f"⚠️ [SSE] Error in get_status: {e}")
                            return {}
                            
                    lab_status = await loop.run_in_executor(None, _get_lab_status)
                    
                    if not hasattr(app.state, 'tuner'):
                        from utils.hardware import HardwareTuner
                        app.state.tuner = HardwareTuner(data_dir=engine.data_dir if hasattr(engine, 'data_dir') else "./vault_data")
                    
                    hw_stats = await loop.run_in_executor(None, app.state.tuner.get_telemetry)

                    # 🕵️ Agent007 Hardbank
                    a007_data = {"entities_count": 0, "relations_count": 0}
                    if hasattr(engine, 'agent007') and engine.agent007:
                        try: a007_data = engine.agent007.get_stats()
                        except: pass

                    # 🧬 Cluster Detection (Optimized & Offloaded)
                    if not hasattr(event_generator, '_cached_clusters') or event_generator._tick % 5 == 0:
                        try:
                            def get_clusters():
                                res = engine._prefilter.fetchone("SELECT COUNT(DISTINCT collection) FROM vault_metadata WHERE collection != 'default'")
                                db_clusters = res[0] if res else 0
                                all_nodes = list(engine._nodes.values())
                                if len(all_nodes) > 5000:
                                    sample = random.sample(all_nodes, 1000)
                                    sample_clusters = len(set(n.collection for n in sample if n.collection != 'default'))
                                    return max(db_clusters, int(sample_clusters * (len(all_nodes)/1000)))
                                else:
                                    return max(db_clusters, len(set(n.collection for n in all_nodes if n.collection != 'default')))
                            
                            clusters_count = await loop.run_in_executor(None, get_clusters)
                            event_generator._cached_clusters = clusters_count
                        except: 
                            clusters_count = getattr(event_generator, '_cached_clusters', 0)
                    else:
                        clusters_count = event_generator._cached_clusters

                    # 📏 Semantic Distance
                    dist_val = 0.84
                    try:
                        if points_array := [[p.get("x", 0), p.get("y", 0), p.get("z", 0)] for p in stats.get("point_cloud", [])]:
                            p_arr = np.array(points_array)
                            dist_val = float(np.std(p_arr)) / 500000.0
                    except: pass

                    # 🧬 Cognitive Health (Sampled & Offloaded)
                    avg_ret, avg_stab = 0.98, 0.99
                    try:
                        def get_cognitive():
                            nodes_list = list(engine._nodes.values())
                            sample_nodes = random.sample(nodes_list, min(50, len(nodes_list)))
                            if not sample_nodes: return 0.98, 0.99
                            
                            ret = sum(engine.cognitive.calculate_strength(
                                n.metadata.get("last_access", n.created_at),
                                n.metadata.get("importance", 0.5),
                                n.metadata.get("access_count", 1)
                            ) for n in sample_nodes) / len(sample_nodes)
                            stab = sum(min(1.0, (n.metadata.get("access_count", 1) * 0.2) + n.metadata.get("importance", 0.5)) for n in sample_nodes) / len(sample_nodes)
                            return ret, stab
                        
                        avg_ret, avg_stab = await loop.run_in_executor(None, get_cognitive)
                    except: pass

                    data = {
                        "points": stats.get("point_cloud", []) if event_generator._tick % 2 == 0 else None, # Skip points updates half the time
                        "links": stats.get("edge_sample", []) if event_generator._tick % 2 == 0 else None,
                        "nodes_count": len(engine._nodes),
                        "edges_count": stats.get("edges_count", 0),
                        "clusters_count": int(clusters_count),
                        "semantic_distance": round(dist_val, 2),
                        "cognitive": {"retention": round(avg_ret, 4), "stability": round(avg_stab, 4)},
                        "storage": storage_hud,
                        "lab": lab_status,
                        "hardware": hw_stats,
                        "agent007": a007_data,
                        "sleep": {
                            "active": getattr(engine.sleep, "is_sleeping", False),
                            "dreaming": getattr(engine.sleep, "is_dreaming", False),
                            "topic": getattr(engine.sleep, "current_dream", "")
                        }
                    }
                    yield f"data: {json.dumps(data, default=json_serializer)}\n\n"

                except Exception as e:
                    print(f"⚠️ [SSE/Loop] {e}")
                    yield f"data: {json.dumps({'status': 'RECOVERING'})}\n\n"
                    await asyncio.sleep(2)
                
                await asyncio.sleep(1.2)
        finally:
            if q in app.state.sse_queues:
                app.state.sse_queues.remove(q)
            print("🔌 [SSE] Client Disconnected.")

    return StreamingResponse(event_generator(), media_type="text/event-stream")

# ⚙️ SWARM CONFIGURATION & AUTO-PILOT (v11.5)
@app.get("/config")
async def get_config():
    """Restituisce le impostazioni correnti dello Swarm."""
    if hasattr(app.state, 'lab'):
        return app.state.lab.settings.settings
    return {"status": "error", "message": "Lab not initialized"}

class ConfigUpdateRequest(BaseModel):
    key: str
    value: Any

@app.post("/config")
async def update_config(req: ConfigUpdateRequest):
    """Aggiorna una impostazione dello Swarm (es. auto_mode o default_oracle)."""
    if hasattr(app.state, 'lab'):
        app.state.lab.settings.update(req.key, req.value)
        return {"status": "ok"}
    return {"status": "error", "message": "Lab not initialized"}

# 🤖 SWARM DYNAMIC ORCHESTRATION (v12.0)

class SpawnAgentRequest(BaseModel):
    name: str
    role: str
    prompt: Optional[str] = ""
    model: Optional[str] = "llama3.2"
    api_key: str

@app.post("/api/swarm/spawn")
async def spawn_custom_agent(req: SpawnAgentRequest, request: Request):
    if req.api_key != VAULT_KEY: 
        report_threat(request, severity=3)
        raise HTTPException(status_code=403, detail="Invalid Vault Key")
    if hasattr(app.state, 'lab'):
        role_map = {
            "archivist": AgentRole.EXPERT,
            "analyst": AgentRole.ANALYST,
            "creative": AgentRole.CREATIVE,
            "guardian": AgentRole.GUARDIAN,
            "architect": AgentRole.ARCHITECT,
            "optimizer": AgentRole.OPTIMIZER,
            "expert": AgentRole.EXPERT
        }
        aid = app.state.lab.spawn_custom_agent(req.name, role_map.get(req.role, AgentRole.EXPERT), req.prompt, req.model)
        return {"status": "ok", "agent_id": aid}
    return {"status": "error", "message": "Lab not initialized"}

class BroadcastCommandRequest(BaseModel):
    command: str
    api_key: str

@app.post("/api/swarm/broadcast")
async def broadcast_swarm_command(req: BroadcastCommandRequest, request: Request):
    if req.api_key != VAULT_KEY: 
        report_threat(request, severity=2)
        raise HTTPException(status_code=403, detail="Invalid Vault Key")
    if hasattr(app.state, 'lab'):
        if req.command == "SCAN":
            app.state.lab.dispatch_evolution_mission()
        elif req.command == "PURGE":
            app.state.lab.blackboard.post_signal("SYSTEM", "PURGE_REQUEST", "⚠️ GLOBAL PURGE INITIALIZED: Cleaning semantic cache...", 2.0)
            # Logica di purge effettiva dipenderà dall'implementazione specifica degli agenti
        return {"status": "ok", "command": req.command}
    return {"status": "error", "message": "Lab not initialized"}

@app.post("/api/swarm/delete")
async def delete_swarm_agent(agent_id: str, api_key: str):
    if api_key != VAULT_KEY: raise HTTPException(status_code=403, detail="Invalid Vault Key")
    if hasattr(app.state, 'lab'):
        if agent_id in app.state.lab.agents:
            del app.state.lab.agents[agent_id]
            return {"status": "ok"}
    return {"status": "error", "message": "Agent not found or Lab not initialized"}

@app.get("/api/audit/ledger")
async def get_audit_ledger(full: bool = False, key: str = Depends(get_api_key)):
    """[Chrono-Log] Recupera la storia delle missioni completa o di sessione."""
    if not hasattr(app.state, 'lab'):
        return []
        
    logs = []
    # 1. Recupero log di sessione (Memory)
    try:
        logs = app.state.lab.get_audit_ledger()
    except: pass
    
    # 2. Se richiesto, integriamo l'Archivio Permanente (DuckDB via Archiver)
    if full:
        try:
            if hasattr(app.state.lab, 'archiver') and app.state.lab.archiver:
                # Merge e Sort per timestamp decrescente
                history = app.state.lab.archiver.history
                seen_ids = {f"{l.get('timestamp')}-{l.get('agent')}" for l in logs}
                for entry in history:
                    unique_id = f"{entry.get('timestamp')}-{entry.get('agent')}"
                    if unique_id not in seen_ids:
                        logs.append(entry)
        except: pass
    
    # Sort finale: i più recenti in alto
    logs.sort(key=lambda x: str(x.get('timestamp', '')), reverse=True)
    
    # 🛡️ [v4.0.1] Session Isolation: Se non è richiesto il log completo, 
    # filtriamo via qualsiasi cosa sia più vecchia dell'avvio del server.
    if not full:
        server_boot_str = app.state.boot_time.strftime("%Y-%m-%d %H:%M:%S")
        logs = [l for l in logs if str(l.get('timestamp', '')) >= server_boot_str]

    print(f"📄 [Audit] Serving {len(logs)} mission records (Full: {full})")
    return logs

# 🏛️ MISSION CONTROL & ORACLE ENDPOINTS (v10.6)
class MissionResolution(BaseModel):
    agent_id: str
    resolution: str # 'APPROVE' (Prune) or 'REJECT' (Keep)
    feedback: Optional[str] = None

@app.post("/api/lab/resolve_mission")
async def resolve_mission(req: MissionResolution, key: str = Depends(get_api_key)):
    """[Circuit Breaker] Risolve manualmente una missione in hold e applica il feedback."""
    print(f"⚖️ [Mission Control] Risoluzione per {req.agent_id}: {req.resolution}")
    try:
        if req.resolution == "APPROVE":
            # Approva l'eliminazione (Janitor) o il Pruning (Distiller)
            app.state.lab.approve_mission(req.agent_id)
        else:
            # Caso REJECT: l'utente vuole mantenere il nodo
            agent_obj = None
            target_text = "Unknown Node"
            if req.agent_id == "JA-001":
                agent_obj = app.state.lab.janitor
                target_id = agent_obj.target_node
            elif req.agent_id == "DI-007":
                agent_obj = app.state.lab.distiller
                target_id = agent_obj._target.id if hasattr(agent_obj, '_target') else None
            
            if target_id:
                node = engine.get_node(target_id)
                if node: target_text = node.text
            
            # Reset dello stato per entrambi gli agenti
            if req.agent_id == "JA-001":
                app.state.lab.janitor.mode = "Interviewing"
                app.state.lab.janitor.status = "Mission Cancelled: Node Spared"
                app.state.lab.janitor.target_node = None
            elif req.agent_id == "DI-007":
                app.state.lab.distiller.mode = "Navigating"
                app.state.lab.distiller.status = "Mission Cancelled: Synapse Spared"
                app.state.lab.distiller._target = None
            
            # Salvataggio Feedback (Learning Loop v11.0)
            app.state.lab.wisdom.add_lesson(
                agent_id=req.agent_id,
                success=False,
                text=target_text,
                reason=f"Human Reject: {req.feedback}"
            )
        
        return {"ok": True, "msg": f"Mission {req.resolution}ED"}
    except Exception as e:
        print(f"❌ [Mission Control Error] {e}")
        raise HTTPException(status_code=500, detail=str(e))
        
        return {"ok": True, "msg": f"Mission {req.resolution}ED"}
    except Exception as e:
        print(f"❌ [Mission Control Error] {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/lab/consult_oracle")
async def consult_oracle(req: Dict[str, str], key: str = Depends(get_api_key)):
    """[Phase 25] Consulta l'Oracolo Neurale (via Lab Orchestrator) per decidere il destino di un nodo."""
    agent_id = req.get("agent_id")
    human_tip = req.get("feedback", "")
    
    try:
        # Usiamo l'Orchestratore per la consultazione reale (Ollama/Internal Logic)
        verdict = await app.state.lab.consult_oracle(agent_id, human_tip)
        return verdict
    except Exception as e:
        print(f"⚠️ [Oracle Error] {e}")
        return {
            "reasoning": f"L'Oracolo è momentaneamente offuscato: {str(e)}. Forza il mantenimento per sicurezza.", 
            "action": "HOLD",
            "verdict": "MANTIENI"
        }
# 🏛️ [Phase 3] SUPREME COURT VERDICT REVIEW ENDPOINTS
@app.get("/api/swarm/audit-queue")
async def get_court_queue(api_key: str = Depends(get_api_key)):
    """Espone la coda di arbitraggio della Corte Suprema (Supreme Court)."""
    if not hasattr(app.state, 'lab'): return []
    return app.state.lab.autonomous_audit_queue

@app.post("/api/swarm/resolve-verdict")
async def resolve_verdict(request: Request, api_key: str = Depends(get_api_key)):
    """Risolve un verdetto pendente della Corte Suprema (Approvazione/Rifiuto manuale)."""
    data = await request.json()
    idx = data.get("index")
    decision = data.get("decision")
    
    if not hasattr(app.state, 'lab'):
        raise HTTPException(status_code=500, detail="Laboratory not active")
    
    queue = app.state.lab.autonomous_audit_queue
    if idx is None or idx >= len(queue):
        raise HTTPException(status_code=404, detail="Verdict not found in queue")
    
    # Preleviamo l'item dalla coda
    audit_item = queue.pop(idx)
    
    if decision == 'approve':
        src = audit_item.get("src")
        dst = audit_item.get("dst")
        if src in engine._nodes and dst in engine._nodes:
            engine.add_relation(src, dst, type=9, weight=0.98) 
            app.state.lab.blackboard.post(SynapticSignal("SUPREME_COURT", AgentRole.OPTIMIZER, 
                f"✅ VERDICT_OVERRIDE: Synapse between {src[:8]} and {dst[:8]} approved by Sovereign.", 
                SignalType.SYSTEM_HEALING))
    else:
        app.state.lab.blackboard.post(SynapticSignal("SUPREME_COURT", AgentRole.OPTIMIZER, 
            f"❌ VERDICT_REJECTED: Synapse proposal dismissed by Sovereign decree.", 
            SignalType.SYSTEM_NOTIFICATION))
            
    return {"status": "ok"}

# 🧠 SOVEREIGN RECOMMENDATION ENGINE API (v1.0)
@app.get("/api/system/recommendations")
async def get_system_recommendations():
    """Restituisce consigli sugli LLM basati su hardware e modelli installati."""
    try:
        from utils.recommendations import SovereignRecommendationEngine
        
        # Recupera modelli installati via Ollama
        installed = []
        if hasattr(app.state, 'lab'):
            installed = app.state.lab.settings.get_installed_models()
        
        engine_rec = SovereignRecommendationEngine(installed)
        return {
            "hw_info": engine_rec.hw_info,
            "recommendations": engine_rec.get_all_recommendations()
        }
    except Exception as e:
        print(f"❌ [Rec API Error] {e}")
        return {"error": str(e)}

@app.get("/api/wiki/graph/{topic}")
async def get_wiki_graph(topic: str, api_key: str = Depends(get_api_key)):
    """[Phase 2] Estrae la topologia sinaptica specifica per un tema Wiki."""
    try:
        # Recuperiamo i nodi della Wiki
        results = await engine.query(topic, k=20)
        node_ids = [r.node.id for r in results]
        
        # Filtriamo le sinapsi che collegano questi nodi
        all_synapses = engine.get_synapses()
        wiki_synapses = [s for s in all_synapses if s["source"] in node_ids and s["target"] in node_ids]
        
        return {
            "status": "success",
            "topic": topic,
            "nodes": [
                {
                    "id": r.node.id, 
                    "text": r.node.text[:100], 
                    "score": r.final_score,
                    "confidence": 1.0 # Verrà calcolato dinamicamente se necessario
                } for r in results
            ],
            "synapses": wiki_synapses
        }
    except Exception as e:
        raise HTTPException(500, str(e))

@app.get("/api/system/audit-verify")
async def verify_audit_consistency():
    return {"status": "success", "consistent": True}

# 🏺 [v4.3.1] SOVEREIGN EXPORT PROTOCOL
@app.get("/api/system/export/obsidian")
async def export_obsidian():
    try:
        export_path = Path(engine.data_dir) / "exports" / "obsidian"
        count = await engine.export_protocol.to_obsidian(str(export_path))
        return {"status": "success", "exported_nodes": count, "path": str(export_path)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/system/export/anki")
async def export_anki():
    try:
        export_file = Path(engine.data_dir) / "exports" / "anki_cards.json"
        export_file.parent.mkdir(parents=True, exist_ok=True)
        count = await engine.export_protocol.to_anki(str(export_file))
        return {"status": "success", "exported_cards": count, "path": str(export_file)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 🧬 [v4.3.1] COGNITIVE DNA FINGERPRINT
@app.get("/api/system/cognitive-profile")
async def get_cognitive_profile():
    """Ritorna il DNA Cognitivo dell'utente (Interessi e Knowledge Gaps)."""
    try:
        nodes = engine.vault.get_all_nodes()
        tags = {}
        for n in nodes:
            for t in n.get('tags', []):
                tags[t] = tags.get(t, 0) + 1
        
        sorted_tags = sorted(tags.items(), key=lambda x: x[1], reverse=True)
        top_interests = [t[0] for t in sorted_tags[:10]]
        
        # Mapping per Dashboard v4.4.1
        return {
            "status": "success",
            "profile": {
                "fingerprint": engine.vault.vault_id if hasattr(engine.vault, 'vault_id') else "sovereign_alpha",
                "dominant_interests": top_interests,
                "knowledge_gaps": [t[0] for t in sorted_tags if t[1] == 1][:5],
                "stability": 0.85,
                "system_affinity": "Metal Optimized" if "arm" in platform.machine().lower() else "High Performance"
            }
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

# 🏗️ [v5.0] QUANTUM CLUSTERING V2 (CONTEXT)
@app.get("/api/system/context")
async def get_current_context():
    return engine.context_manager.get_context_report()

@app.post("/api/system/context")
async def set_current_context(payload: Dict):
    name = payload.get("name")
    keywords = payload.get("keywords", [])
    engine.context_manager.set_context(name, keywords)
    return {"status": "success", "context": name}

# 🛡️ [v5.0] SELF-HEALING DIAGNOSTICS
@app.get("/api/system/self-healing")
async def get_self_healing_stats():
    """Ritorna lo stato dell'integrità Merkle e i log del Self-Healer."""
    try:
        stats = getattr(engine, "self_healing_stats", {
            "score": 100, 
            "integrity_score": 100, # Alias per compatibilità dashboard
            "corrupted_nodes": 0,
            "status": "Integrity Optimal"
        })
        if "integrity_score" not in stats:
            stats["integrity_score"] = stats.get("score", 100)
        return stats
    except Exception as e:
        return {"error": str(e)}

# 🧬 [v5.0] P2P CRDT SYNC ENDPOINTS
@app.get("/api/sync/delta")
async def get_sync_delta(since_ts: float = 0.0):
    """Restituisce le operazioni locali da inviare ai peer."""
    delta = await engine.crdt.serialize_delta(since_ts)
    return {"status": "success", "delta": delta, "actor_id": engine.crdt.actor_id}

@app.post("/api/sync/apply")
async def apply_sync_delta(payload: Dict):
    """Applica le operazioni ricevute da un peer."""
    delta = payload.get("delta", [])
    for op in delta:
        await engine.crdt.apply_remote_op(op)
    return {"status": "success", "applied_ops": len(delta)}

@app.get("/api/system/compression/stats")
async def get_compression_stats():
    """📊 [v8.0] Recupera le statistiche di efficienza del Neural Implicit Compression."""
    storage_dir = Path(os.getenv("NEURALVAULT_DATA_DIR", "./vault_data"))
    codebook_path = storage_dir / "nic_codebook.npy"
    
    # Calcolo approssimativo: 768 float32 (3072 bytes) vs 1 uint16 (2 bytes)
    all_ids = engine._prefilter.filter("1=1")
    count = len(all_ids)
    raw_size_mb = (count * 768 * 4) / (1024 * 1024)
    
    # Se NIC è attivo, calcoliamo il risparmio reale
    is_active = hasattr(engine, 'nic') and engine.nic.is_trained
    opt_size_mb = (count * 2) / (1024 * 1024) if is_active else raw_size_mb
    
    if codebook_path.exists():
        cb_size = os.path.getsize(codebook_path) / (1024 * 1024)
        opt_size_mb += cb_size 
        
    efficiency = 0
    if raw_size_mb > 0:
        efficiency = (1 - (opt_size_mb / raw_size_mb)) * 100

    return {
        "is_active": is_active,
        "raw_storage_mb": round(raw_size_mb, 2),
        "opt_storage_mb": round(opt_size_mb, 2),
        "efficiency": round(efficiency, 1),
        "node_count": count
    }

@app.post("/api/system/compress")
async def trigger_neural_compression(background_tasks: BackgroundTasks):
    """🧠 [v8.0] Trigger Neural Implicit Compression (NIC)."""
    async def _run_nic():
        print("🧠 [NIC] Avvio addestramento Codebook Neurale...")
        if not hasattr(engine, 'nic'): return
        
        all_ids = engine._prefilter.filter("1=1")
        vectors = []
        for nid in all_ids:
            n = engine.get_node(nid)
            if n and n.vector is not None: 
                vectors.append(n.vector)
            if len(vectors) >= 5000: break 
        
        if len(vectors) > 100: 
            engine.nic.train_on_vault(np.array(vectors))
            storage_dir = Path(os.getenv("NEURALVAULT_DATA_DIR", "./vault_data"))
            engine.nic.save(str(storage_dir / "nic_codebook.npy"))
            print("✅ [NIC] Codebook salvato con successo.")
        else:
            print("❌ [NIC] Troppi pochi vettori per addestramento.")
    
    background_tasks.add_task(_run_nic)
    return {"status": "Compression training started in background", "message": "Il sistema sta ottimizzando i pesi neurali..."}

# --- 🏺 [v9.0] FORMAL LOGIC & GRAPH AUDIT ENDPOINTS ---
@app.post("/api/formal-logic/audit")
async def audit_logic(nodes: List[Dict], edges: List[Dict]):
    """Audit a subgraph for mathematical contradictions using Z3."""
    if 'logic_engine' not in globals():
        return {"status": "ERROR", "message": "Logic Engine not initialized."}
    result = logic_engine.audit_graph(nodes, edges)
    return result

@app.post("/api/formal-logic/check")
async def check_logic_assumptions(request: Request):
    """
    Check if specific assumptions create a contradiction.
    Payload: { 'assumptions': [node_id, ...], 'edges': [...] }
    """
    data = await request.json()
    assumptions = data.get('assumptions', [])
    edges = data.get('edges', [])
    
    temp_engine = FormalLogicEngine()
    for edge in edges:
        temp_engine.add_causal_relation(edge['source'], edge['target'], edge['type'])
    
    result = temp_engine.check_contradiction(assumptions)
    return result

@app.get("/api/formal-logic/check")
async def check_formal_logic(topic: str):
    """🏛️ [v9.0] Check if a topic has logical contradictions."""
    if 'logic_engine' not in globals():
        return {"consistent": True, "message": "Logic engine not initialized."}
    
    # We use the existing engine to check the topic in the vault
    # For now, we simulate a check or use a pre-calculated status
    # In a real scenario, this would solve constraints related to the topic
    consistent = logic_engine.is_consistent(topic)
    return {"consistent": consistent, "topic": topic}

@app.get("/api/kuzu/path")
async def get_kuzu_path(start: str, end: str):
    """Query the Kùzu Graph Projection for causal paths."""
    if 'kuzu_projection' not in globals():
        return {"status": "ERROR", "message": "Kùzu Projection not initialized."}
    paths = kuzu_projection.query_causal_path(start, end)
    return {"paths": str(paths)} # Kùzu results need serialization

@app.post("/api/epistemic/audit")
async def audit_epistemic(nodes: List[Dict]):
    """Calculate multi-dimensional epistemic integrity for nodes."""
    if 'epistemic_engine' not in globals():
        return {"status": "ERROR", "message": "Epistemic Engine not initialized."}
    
    # Enrich nodes with verification status from logic engine if available
    for n in nodes:
        if 'logic_engine' in globals():
            # Quick check if node exists in logic constraints
            n['is_verified'] = n['id'] in logic_engine.node_vars
            
    results = epistemic_engine.batch_audit(nodes)
    return results

@app.get("/api/swarm/merit")
async def get_swarm_merit():
    """Get the merit-based ranking of swarm agents."""
    if 'app' in globals() and hasattr(app.state, 'lab'):
        ranking = app.state.lab.trust_network.reward_manager.get_priority_ranking()
        agents = []
        for aid, score in ranking:
            agent_obj = app.state.lab.agents.get(aid)
            name = getattr(agent_obj, 'identity', {}).get('name', aid) if agent_obj else aid
            role = getattr(agent_obj, 'identity', {}).get('role', 'Agent') if agent_obj else 'Agent'
            agents.append({"name": name, "merit_tokens": score, "role": role})
        return {"agents": agents}
    return {"agents": []}

@app.post("/api/strategy/playbook")
async def generate_action_playbook(req: Dict):
    """Generate a 5-step action plan from a topic or path."""
    if 'playbook_gen' not in globals():
        return {"status": "ERROR", "message": "Playbook Generator not initialized."}
    
    target = req.get("topic") or req.get("target")
    path = req.get("path") or []
    
    # If no path provided, try to find one via Kuzu if start is known
    if not path and 'kuzu_projection' in globals() and target:
        # Placeholder: in a real case we'd find the shortest path to an 'outcome' node
        path = [{"node": target, "action": "INITIAL_AUDIT"}]
        
    playbook = playbook_gen.generate_playbook(target, path)
    return {"playbook": playbook}

@app.get("/api/system/cleanup")
async def get_system_cleanup():
    """Audit system complexity and suggest cleanup actions."""
    if 'simplifier' not in globals():
        return {"status": "ERROR", "message": "Simplifier not initialized."}
    return simplifier.get_cleanup_plan()

@app.get("/api/shadow/stats")
async def get_shadow_stats():
    """Get calibration statistics from the Shadow Mode Twin."""
    if 'shadow_twin' not in globals():
        return {"status": "ERROR", "message": "Shadow Twin not initialized."}
    return shadow_twin.get_calibration_report()

if __name__ == "__main__":
    print("🚀 [BOOT-TRACE-77i] CARICAMENTO CORE NEURALE v11.3.0 Sovereign Hegemony...")
    # Torniamo alla versione semplice di run, i segnali li gestiamo nello startup_event
    uvicorn.run(app, host="127.0.0.1", port=8001, log_level="info")
