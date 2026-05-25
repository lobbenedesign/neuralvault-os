import platform
import psutil
import torch
import os
import logging

logger = logging.getLogger("Aegis")

class SovereignHardwareAdvisor:
    """
    💎 Hardware Advisor v1.0 (2026 Ready)
    Auto-detects system architecture and optimizes NeuralVault's compute strategy.
    Supports Apple Silicon (MPS), Nvidia (CUDA/TensorRT), and generic CPU.
    """
    
    def __init__(self):
        self.os_type = platform.system() # Windows, Darwin (Mac), Linux
        self.arch = platform.machine()   # x86_64, arm64
        self.cpu_count = psutil.cpu_count(logical=False) or 4
        self.total_ram_gb = psutil.virtual_memory().total / (1024**3)
        
        self.device = self._detect_best_device()
        self.compute_tier = self._determine_compute_tier()
        
    def _detect_best_device(self):
        """Identifica la migliore unità di calcolo disponibile."""
        if torch.backends.mps.is_available():
            return "mps"
        if torch.cuda.is_available():
            return "cuda"
        return "cpu"

    def _determine_compute_tier(self):
        """
        Classifica l'hardware per scalare le operazioni.
        - TIER 1: High-End (Nvidia 2026 / Apple M3+)
        - TIER 2: Mid-Range (Standard M1/M2 / Nvidia RTX)
        - TIER 3: Low-End (Intel/AMD CPU / Celeron)
        """
        if self.device in ["cuda", "mps"]:
            if self.total_ram_gb >= 32 or (self.device == "cuda" and torch.cuda.get_device_properties(0).total_memory / (1024**3) > 12):
                return "TIER_1"
            return "TIER_2"
        return "TIER_3"

    def get_orchestration_config(self):
        """Restituisce la configurazione ottimale per l'Orchestrator."""
        config = {
            "device": self.device,
            "tier": self.compute_tier,
            "max_search_workers": 2, # Default conservativo per I/O
            "max_compute_workers": 1,
            "use_process_pool": True,
            "model_precision": "float16" if self.compute_tier != "TIER_3" else "int4"
        }
        
        if self.compute_tier == "TIER_1":
            config["max_search_workers"] = 8
            config["max_compute_workers"] = 4
        elif self.compute_tier == "TIER_2":
            config["max_search_workers"] = 4
            config["max_compute_workers"] = 2
        else:
            config["max_search_workers"] = 2
            config["max_compute_workers"] = 1
            config["use_process_pool"] = False # Su Celeron meglio non abusare di Fork/Spawn
            
        return config

    def log_sitrep(self):
        """Stampa un SITREP hardware per il log di Aegis."""
        sitrep = (
            f"🛡️ [Aegis] Hardware SITREP:\n"
            f"   - OS: {self.os_type} ({self.arch})\n"
            f"   - Device: {self.device.upper()}\n"
            f"   - Tier: {self.compute_tier}\n"
            f"   - RAM: {self.total_ram_gb:.1f} GB\n"
            f"   - Cores: {self.cpu_count}"
        )
        print(sitrep)
        return sitrep

# Singleton instance
ADVISOR = SovereignHardwareAdvisor()
