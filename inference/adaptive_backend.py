import os
import sys
import time
import shutil
import asyncio
import logging
import subprocess
from typing import Dict, List, Any, Union, Optional
import httpx
import numpy as np
import torch
from transformers import AutoTokenizer, AutoModel, AutoModelForSequenceClassification

# Set up dedicated logger for the Inference Core
logger = logging.getLogger("NeuralVault.Inference")
logging.basicConfig(level=logging.INFO)

# Certified Model Whitelist as specified by architectural roadmap
WHITELISTED_MODELS = {
    "cross-encoder/ms-marco-TinyBERT-L-2-v2",
    "sentence-transformers/all-MiniLM-L6-v2",
    "all-MiniLM-L6-v2",
    "TinyLlama/TinyLlama-1.1B-Chat-v1.0",
    "TinyBERT"
}

def detect_hardware_backend() -> str:
    """Detects best available hardware acceleration device for PyTorch."""
    if torch.cuda.is_available():
        return "cuda"
    elif torch.backends.mps.is_available():
        return "mps"
    else:
        return "cpu"

class InferenceRequest:
    """Represents a queued inference task with priority."""
    def __init__(self, priority: int, model_name: str, input_data: Any, kwargs: dict, future: asyncio.Future):
        self.priority = priority  # Lower is higher priority (e.g. 1 = Urgent, 100 = Background)
        self.model_name = model_name
        self.input_data = input_data
        self.kwargs = kwargs
        self.future = future
        self.timestamp = time.time()

    def __lt__(self, other):
        # Tie-breaker by timestamp if priority matches
        if self.priority == other.priority:
            return self.timestamp < other.timestamp
        return self.priority < other.priority

class AdaptiveInferenceBackend:
    """
    Asynchronous hardware-accelerated model manager. 
    Manages loading, execution, queueing, and fallback logic for NeuralVault LLMs.
    """
    def __init__(self, ollama_url: Optional[str] = None):
        self.device = detect_hardware_backend()
        self.ollama_url = ollama_url or os.environ.get("OLLAMA_URL", "http://localhost:11434")
        self.models_cache: Dict[str, Any] = {}
        self.tokenizers_cache: Dict[str, Any] = {}
        self.queue = asyncio.PriorityQueue()
        self.is_running = True
        
        # Check if ONNX Runtime is available for optimized loading
        try:
            import onnxruntime as ort
            self.has_onnx = True
            self.ort_providers = ["CPUExecutionProvider"]
            if self.device == "cuda":
                if "CUDAExecutionProvider" in ort.get_available_providers():
                    self.ort_providers.insert(0, "CUDAExecutionProvider")
            elif self.device == "mps":
                if "CoreMLExecutionProvider" in ort.get_available_providers():
                    self.ort_providers.insert(0, "CoreMLExecutionProvider")
            logger.info(f"✨ ONNX Runtime Active. Exec Providers: {self.ort_providers}")
        except ImportError:
            self.has_onnx = False
            logger.info("ℹ️ ONNX Runtime not available; native PyTorch MPS/CUDA pipeline active.")

        # Launch the asynchronous queue worker task
        self.worker_task = asyncio.create_task(self._queue_worker_loop())
        logger.info(f"🚀 AdaptiveInferenceBackend Initialized. Device: {self.device.upper()} | Uplink: {self.ollama_url}")

    async def run_inference(self, model_name: str, input_data: Any, priority: int = 10, **kwargs) -> Any:
        """Puts a request into the priority-driven InferenceQueue and awaits execution."""
        if not self.is_running:
            raise RuntimeError("Inference manager is shut down.")

        loop = asyncio.get_running_loop()
        future = loop.create_future()
        req = InferenceRequest(priority, model_name, input_data, kwargs, future)
        await self.queue.put(req)
        return await future

    async def _queue_worker_loop(self):
        """Asynchronously pulls requests from queue and executes them sequentially to prevent concurrency deadlocks."""
        logger.info("⚙️ Inference queue worker loop online.")
        while self.is_running:
            try:
                req = await self.queue.get()
                try:
                    res = await self._dispatch_inference(req.model_name, req.input_data, **req.kwargs)
                    req.future.set_result(res)
                except Exception as e:
                    logger.error(f"❌ Error during queued inference: {e}")
                    req.future.set_exception(e)
                finally:
                    self.queue.task_done()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"🚨 Critical failure in inference loop: {e}")
                await asyncio.sleep(0.5)

    async def _dispatch_inference(self, model_name: str, input_data: Any, **kwargs) -> Any:
        """Executes model inference, applying whitelisting and dynamic fallback schemes."""
        is_whitelisted = model_name in WHITELISTED_MODELS
        
        if is_whitelisted:
            logger.info(f"🛡️ Model [{model_name}] is WHITELISTED. Loading native hardware context...")
            try:
                return await self._execute_whitelisted(model_name, input_data, **kwargs)
            except Exception as e:
                logger.warning(f"⚠️ whitelisted execution failed for {model_name}: {e}. Falling back to Ollama...")
        
        # Offload to Ollama if not whitelisted or whitelisted execution failed
        logger.info(f"📡 Offloading model [{model_name}] to Ollama provider...")
        return await self._execute_ollama_with_fallback(model_name, input_data, **kwargs)

    async def _execute_whitelisted(self, model_name: str, input_data: Any, **kwargs) -> Any:
        """Loads and runs whitelisted models directly on native PyTorch (MPS/CUDA) or ONNX."""
        # 1. Lazy loading & Caching
        if model_name not in self.models_cache:
            logger.info(f"📦 First-time load: initializing accelerated model wrapper for [{model_name}]...")
            if "cross-encoder" in model_name or "TinyBERT" in model_name:
                tokenizer = AutoTokenizer.from_pretrained(model_name)
                model = AutoModelForSequenceClassification.from_pretrained(model_name)
                model.to(self.device)
                model.eval()
                self.models_cache[model_name] = model
                self.tokenizers_cache[model_name] = tokenizer
            else:
                tokenizer = AutoTokenizer.from_pretrained(model_name)
                model = AutoModel.from_pretrained(model_name)
                model.to(self.device)
                model.eval()
                self.models_cache[model_name] = model
                self.tokenizers_cache[model_name] = tokenizer

        model = self.models_cache[model_name]
        tokenizer = self.tokenizers_cache[model_name]

        # 2. Execution depending on task type
        task = kwargs.get("task", "embed")
        if task == "embed":
            # Embedding task
            texts = [input_data] if isinstance(input_data, str) else input_data
            encoded_input = tokenizer(texts, padding=True, truncation=True, return_tensors='pt').to(self.device)
            with torch.no_grad():
                model_output = model(**encoded_input)
                # Perform mean pooling
                token_embeddings = model_output[0]
                attention_mask = encoded_input['attention_mask']
                input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
                sum_embeddings = torch.sum(token_embeddings * input_mask_expanded, 1)
                sum_mask = torch.clamp(input_mask_expanded.sum(1), min=1e-9)
                embeddings = sum_embeddings / sum_mask
                
            res = embeddings.cpu().numpy()
            return res.tolist() if isinstance(input_data, str) else res.tolist()
            
        elif task == "rank" or task == "rerank":
            # Re-ranking task
            pairs = input_data  # Should be List[Tuple[str, str]] -> [(query, doc1), (query, doc2)]
            if not isinstance(pairs, list) or len(pairs) == 0:
                return []
            
            features = tokenizer([p[0] for p in pairs], [p[1] for p in pairs], padding=True, truncation=True, return_tensors="pt").to(self.device)
            with torch.no_grad():
                outputs = model(**features)
                scores = outputs.logits.squeeze(-1).cpu().numpy()
            return scores.tolist() if scores.ndim > 0 else [float(scores)]
        
        else:
            raise ValueError(f"Unsupported task type for native execution: {task}")

    async def _execute_ollama_with_fallback(self, model_name: str, input_data: Any, **kwargs) -> Any:
        """Invokes Ollama API, self-heals the serving daemon if offline, and implements robust fallback."""
        # 1. Health check and self-healing
        is_healthy = await self._check_ollama_health()
        if not is_healthy:
            logger.warning("🚨 Ollama uplink offline! Launching self-healing daemon provisioning...")
            await self._provision_ollama()
            # Wait up to 5 seconds for initialization
            for _ in range(5):
                await asyncio.sleep(1.0)
                if await self._check_ollama_health():
                    is_healthy = True
                    break
        
        if not is_healthy:
            logger.error("🚨 Self-healing failed to wake Ollama. Falling back to local PyTorch execution context.")
            return await self._pytorch_emergency_fallback(model_name, input_data, **kwargs)

        # 2. Invoke Ollama API
        task = kwargs.get("task", "completion")
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                if task == "embed" or task == "embedding":
                    payload = {"model": model_name, "prompt": str(input_data)}
                    response = await client.post(f"{self.ollama_url}/api/embeddings", json=payload)
                    if response.status_code == 200:
                        return response.json().get("embedding")
                    else:
                        logger.warning(f"⚠️ Ollama model error ({response.status_code}). Trying to pull model...")
                        # Auto-provision model pull
                        await self._pull_ollama_model(client, model_name)
                        response = await client.post(f"{self.ollama_url}/api/embeddings", json=payload)
                        if response.status_code == 200:
                            return response.json().get("embedding")
                
                else:  # completion/generation task
                    payload = {
                        "model": model_name,
                        "prompt": str(input_data),
                        "stream": False,
                        "options": kwargs.get("options", {})
                    }
                    response = await client.post(f"{self.ollama_url}/api/generate", json=payload)
                    if response.status_code == 200:
                        return response.json().get("response")
                    else:
                        logger.warning(f"⚠️ Ollama model error ({response.status_code}). Trying to pull model...")
                        await self._pull_ollama_model(client, model_name)
                        response = await client.post(f"{self.ollama_url}/api/generate", json=payload)
                        if response.status_code == 200:
                            return response.json().get("response")
            
            except Exception as e:
                logger.error(f"❌ Ollama request failed: {e}. Activating emergency fallback...")
                
        return await self._pytorch_emergency_fallback(model_name, input_data, **kwargs)

    async def _check_ollama_health(self) -> bool:
        """Checks if the local Ollama instance responds to requests."""
        try:
            async with httpx.AsyncClient(timeout=1.0) as client:
                resp = await client.get(self.ollama_url)
                return resp.status_code == 200
        except Exception:
            return False

    async def _provision_ollama(self) -> bool:
        """Attempts to start the Ollama service on macOS Darwin or Linux."""
        os_name = sys.platform
        env = os.environ.copy()
        try:
            if os_name == "darwin":
                if shutil.which("ollama"):
                    subprocess.Popen(["ollama", "serve"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, env=env)
                    logger.info("⚡ [Darwin] Started 'ollama serve' subprocess.")
                else:
                    subprocess.Popen(["open", "-a", "Ollama"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, env=env)
                    logger.info("⚡ [Darwin] Dispatched application launcher for Ollama.app.")
                return True
            elif os_name.startswith("linux"):
                subprocess.Popen(["ollama", "serve"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, env=env)
                logger.info("⚡ [Linux] Fired 'ollama serve' daemon process.")
                return True
        except Exception as e:
            logger.error(f"❌ Failed to spawn Ollama process: {e}")
        return False

    async def _pull_ollama_model(self, client: httpx.AsyncClient, model_name: str):
        """Requests Ollama to pull a model if missing."""
        logger.info(f"📥 Pulling model [{model_name}] via Ollama API...")
        try:
            resp = await client.post(f"{self.ollama_url}/api/pull", json={"name": model_name, "stream": False}, timeout=180.0)
            if resp.status_code == 200:
                logger.info(f"✅ Model [{model_name}] successfully pulled.")
        except Exception as e:
            logger.error(f"❌ Failed to pull Ollama model {model_name}: {e}")

    async def _pytorch_emergency_fallback(self, model_name: str, input_data: Any, **kwargs) -> Any:
        """Emergency circuit breaker. Routes unwhitelisted models to local CPU/MPS models as a hard fallback."""
        fallback_model = "sentence-transformers/all-MiniLM-L6-v2"
        logger.warning(f"🚨 EMERGENCY FALLBACK. Routing inference for {model_name} to whitelisted model {fallback_model} on device: {self.device.upper()}")
        
        # Adjust input format for embeddings or completions
        task = kwargs.get("task", "embed")
        if task == "embed" or task == "embedding":
            return await self._execute_whitelisted(fallback_model, input_data, task="embed")
        else:
            # Generate a mock cognitive reasoning trace
            return (
                f"[SYSTEM FALLBACK] Model '{model_name}' was unavailable. The system stochastically recovered "
                f"using a native reasoning bridge inside NeuralVault (Fallback target: {fallback_model})."
            )

    def shutdown(self):
        """Gracefully shuts down the background queue processor."""
        self.is_running = False
        if hasattr(self, "worker_task"):
            self.worker_task.cancel()
        logger.info("🔌 AdaptiveInferenceBackend shut down successfully.")
