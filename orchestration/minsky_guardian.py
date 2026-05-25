import os
import psutil
import logging
import gc
import time
from typing import Dict, Any, Optional

class MinskyGuardian:
    """
    Minsky Guardian (v11.0 - Step 2 Sovereign Consolidation)
    Enforces strict CPU & GPU RAM Budget Contracts on all active modules.
    Implements a Graceful Eviction Engine for Apple Silicon (MPS) and NVIDIA (CUDA),
    protecting 3D Nebula rendering performance by suspending K-Means background training.
    """
    
    # Class-level flag to coordinate background tasks suspension across threads
    training_suspended = False
    
    def __init__(self, ram_budget_mb: Optional[int] = None):
        self.logger = logging.getLogger("Sovereign.MinskyGuardian")
        self.process = psutil.Process(os.getpid())
        
        # Dynamic RAM Budget Contract (v10.2): 15% di RAM fisica, min 1GB, max 4GB
        try:
            total_ram_bytes = psutil.virtual_memory().total
            total_ram_mb = total_ram_bytes / (1024 * 1024)
            detected_gb = total_ram_bytes / (1024**3)
            calculated_budget = max(1024, min(4096, int(total_ram_mb * 0.15)))
            self.logger.info(
                f"🧠 [Minsky Guardian] Hardware RAM detected: {detected_gb:.2f} GB. "
                f"Dynamic Budget calculated (15%): {calculated_budget} MB."
            )
        except Exception as e:
            calculated_budget = 2048
            self.logger.warning(f"⚠️ [Minsky Guardian] RAM auto-detection failed: {e}. Defaulting to 2048 MB.")
            
        self.ram_budget_mb = ram_budget_mb if ram_budget_mb is not None else calculated_budget
        
        # GPU Acceleration Auto-detection
        self.has_torch = False
        self.device_type = "cpu"
        try:
            import torch
            self.has_torch = True
            if torch.backends.mps.is_available():
                self.device_type = "mps"
            elif torch.cuda.is_available():
                self.device_type = "cuda"
        except ImportError:
            pass
        self.logger.info(f"[Minsky Guardian] Active device acceleration for memory tracing: {self.device_type.upper()}")

    def enforce_contract(self, engine) -> bool:
        """
        Controlla l'uso di memoria CPU RSS e della memoria unificata/dedicata GPU (MPS o CUDA).
        Se supera la soglia critica del 60%, sospende il training K-Means in background
        ed esegue l'eviction dei tensori freddi sulla RAM CPU.
        """
        mem_info = self.process.memory_info()
        rss_mb = mem_info.rss / (1024 * 1024)
        
        gpu_mb = 0.0
        gpu_limit_mb = self.ram_budget_mb * 0.60 # Soglia critica del 60% del budget RAM
        
        if self.has_torch:
            import torch
            try:
                if self.device_type == "mps":
                    # Tracciamento della memoria GPU unificata del Mac Apple Silicon
                    gpu_mb = torch.mps.current_allocated_memory() / (1024 * 1024)
                elif self.device_type == "cuda":
                    # Tracciamento della memoria GPU dedicata Nvidia
                    gpu_mb = torch.cuda.memory_allocated() / (1024 * 1024)
            except Exception as e:
                self.logger.debug(f"Failed to query GPU memory: {e}")

        cpu_exceeded = rss_mb > self.ram_budget_mb
        gpu_exceeded = gpu_mb > gpu_limit_mb
        
        if cpu_exceeded or gpu_exceeded:
            reason = []
            if cpu_exceeded:
                reason.append(f"CPU RSS: {rss_mb:.2f}MB > {self.ram_budget_mb}MB")
            if gpu_exceeded:
                reason.append(f"GPU Unified ({self.device_type.upper()}): {gpu_mb:.2f}MB > {gpu_limit_mb:.2f}MB (60% Threshold)")
                
            self.logger.warning(
                f"🚨 [Minsky Guardian] RAM budget exceeded! {', '.join(reason)}. "
                f"Activating Graceful Eviction Engine and suspending background training."
            )
            
            # Attiva la sospensione del training globale
            MinskyGuardian.training_suspended = True
            
            # Esegue lo svuotamento e l'eviction dei tensori
            self._execute_graceful_eviction(engine)
            self._notify_blackboard(engine, rss_mb, gpu_mb, True)
            return False
        else:
            # Se la memoria rientra nei parametri, revoca la sospensione
            if MinskyGuardian.training_suspended:
                self.logger.info("✅ [Minsky Guardian] Memory parameters normalized. Resuming background processes.")
                MinskyGuardian.training_suspended = False
                self._notify_blackboard(engine, rss_mb, gpu_mb, False)
            
        return True
        
    def _execute_graceful_eviction(self, engine):
        """
        Graceful Eviction Protocol:
        1. Forza l'eviction dei tensori semantici e pesanti di TurboQuant dalla GPU alla CPU RAM.
        2. Scarica le cache semantiche fredde del motore di prefiltro.
        3. Libera le cache della formal logic.
        4. Esegue il Garbage Collection per rilasciare la memoria di Python.
        5. Invocazione di empty_cache() su MPS/CUDA per rilasciare blocchi inutilizzati.
        """
        # 1. Eviction dei tensori caldi di TurboQuant verso la CPU RAM
        if hasattr(engine, 'index') and engine.index:
            idx = engine.index
            evicted = False
            if hasattr(idx, 'centroids') and idx.centroids is not None:
                if idx.centroids.device.type != 'cpu':
                    idx.centroids = idx.centroids.cpu()
                    evicted = True
            if hasattr(idx, 'pq_store') and idx.pq_store is not None:
                if idx.pq_store.device.type != 'cpu':
                    idx.pq_store = idx.pq_store.cpu()
                    evicted = True
            if evicted:
                idx.device = 'cpu'
                self.logger.info("🧠 [Minsky Eviction] Successfully evicted cold semantic tensors from GPU to CPU RAM.")

        # 2. Svuota la cache semantica del prefiltro dell'engine
        if hasattr(engine, '_prefilter') and hasattr(engine._prefilter, 'clear_cache'):
            try:
                engine._prefilter.clear_cache()
                self.logger.debug("[Minsky Eviction] Cleared Engine Prefilter cache.")
            except Exception as e:
                self.logger.error(f"Error purging prefilter cache: {e}")
            
        # 3. Svuota la cache di formal logic
        if hasattr(engine, 'orchestrator') and hasattr(engine.orchestrator, 'formal_logic'):
            fl = engine.orchestrator.formal_logic
            if hasattr(fl, 'clear_cache'):
                try:
                    fl.clear_cache()
                    self.logger.debug("[Minsky Eviction] Cleared Formal Logic cache.")
                except Exception as e:
                    self.logger.error(f"Error purging formal logic cache: {e}")
                    
        # 4. Garbage Collection forzato
        gc.collect()
        
        # 5. Rilascio fisico della cache allocata su GPU (Apple Silicon o NVIDIA)
        if self.has_torch:
            import torch
            try:
                if self.device_type == "mps":
                    torch.mps.empty_cache()
                    self.logger.info("🧠 [Minsky Guardian] Executed torch.mps.empty_cache() successfully.")
                elif self.device_type == "cuda":
                    torch.cuda.empty_cache()
                    self.logger.info("🧠 [Minsky Guardian] Executed torch.cuda.empty_cache() successfully.")
            except Exception as e:
                self.logger.error(f"Failed to empty GPU cache: {e}")

    def _notify_blackboard(self, engine, cpu_mb: float, gpu_mb: float, active: bool):
        """Notifica in tempo reale l'HUD e il cockpit della Blackboard della variazione di stato."""
        try:
            if hasattr(engine, 'orchestrator') and engine.orchestrator:
                from neural_lab import SynapticSignal, AgentRole, SignalType
                
                if active:
                    msg = (
                        f"⚠️ [Minsky Guardian] MEMORY LIMIT EXCEEDED! CPU RSS: {cpu_mb:.1f}MB, "
                        f"GPU: {gpu_mb:.1f}MB. Background K-Means PAUSED. Evicting Tensors to CPU RAM."
                    )
                    sig = SynapticSignal("GUARDIAN", AgentRole.GUARDIAN, msg, SignalType.SYSTEM_HEALING)
                else:
                    msg = f"✅ [Minsky Guardian] Memory stabilized (CPU: {cpu_mb:.1f}MB, GPU: {gpu_mb:.1f}MB). Background Swarm Resumed."
                    sig = SynapticSignal("GUARDIAN", AgentRole.GUARDIAN, msg, SignalType.SYSTEM_NOTIFICATION)
                    
                engine.orchestrator.blackboard.post(sig)
        except Exception as e:
            self.logger.debug(f"Failed to post guardian notification to blackboard: {e}")

    @classmethod
    def is_suspended(cls) -> bool:
        """Ritorna se il training in background è attualmente sospeso dal Guardiano."""
        return cls.training_suspended


