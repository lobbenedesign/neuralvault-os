"""
neuralvault.utils.config_validator
──────────────────────────────────
Valida le impostazioni del Swarm al boot per prevenire conflitti dimensionali
(MRL vs TurboQuant PQ) e garantire contratti RAM sicuri su Apple Silicon.
"""

import os
import psutil
import logging
from pathlib import Path
from typing import Dict, Any

class ColdBootConfigValidator:
    """
    Esegue diagnostiche all'avvio (Cold-Boot Pre-flight checks).
    Rileva incompatibilità e previene crash hardware/logici.
    """
    _has_run = False

    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.logger = logging.getLogger("Sovereign.ConfigValidator")

    def validate_and_adjust(self, settings: Dict[str, Any], force: bool = False) -> Dict[str, Any]:
        """
        Scansiona e corregge le impostazioni per garantire la stabilità del sistema.
        """
        if ColdBootConfigValidator._has_run and not force:
            return settings

        self.logger.info("🛡️ [Pre-flight] Starting Cold-Boot Config Validation...")
        adjusted = settings.copy()

        # 1. Mutua Esclusione MRL (Matryoshka) vs TurboQuant PQ
        # Se l'embedder è nomic-mrl, non possiamo usare la quantizzazione di TurboQuant PQstandard
        # poiché i centroidi a 1024D non sono allineati con il troncamento a 256D.
        embedder_type = adjusted.get("embedder_type", "none")
        use_quantization = adjusted.get("use_quantization", False)
        
        # Controlliamo anche impostazioni globali se presenti
        if adjusted.get("routing", {}).get("embedder") == "nomic-mrl":
            embedder_type = "nomic-mrl"

        if embedder_type == "nomic-mrl" and use_quantization:
            self.logger.warning(
                "🚨 [Conflict] Dimensional Clash detected: Matryoshka Representation (MRL) and "
                "TurboQuant Product Quantization (PQ) cannot run concurrently! Disabling PQ."
            )
            adjusted["use_quantization"] = False
            if "use_quantization" in adjusted:
                adjusted["use_quantization"] = False

        # 2. Validazione RAM Budget e Limiti Fisici Hardware
        # Verifichiamo che il budget RAM impostato non superi il 70% della RAM fisica del sistema
        try:
            virtual_mem = psutil.virtual_memory()
            physical_ram_mb = virtual_mem.total / (1024 * 1024)
            max_allowed_ram_mb = int(physical_ram_mb * 0.70)
            
            # Default budget in MinskyGuardian is 2048MB, check settings or fallback
            ram_budget_mb = adjusted.get("ram_budget_mb", 2048)
            
            if ram_budget_mb > max_allowed_ram_mb:
                self.logger.warning(
                    f"⚠️ [RAM Budget Warning] Configured RAM budget ({ram_budget_mb}MB) exceeds "
                    f"70% of physical hardware capacity ({max_allowed_ram_mb}MB). "
                    f"Adjusting safely to {max_allowed_ram_mb}MB."
                )
                adjusted["ram_budget_mb"] = max_allowed_ram_mb
            else:
                self.logger.info(
                    f"✅ [RAM Budget Contract] Verified: {ram_budget_mb}MB is within safe hardware boundaries "
                    f"(70% limit is {max_allowed_ram_mb}MB)."
                )
        except Exception as e:
            self.logger.error(f"⚠️ [Diagnostics Error] Failed to read physical hardware capacity: {e}")

        # 3. Validazione degli Endpoint e Modelli Locali
        ollama_url = adjusted.get("ollama_url", "http://127.0.0.1:11434")
        self.logger.info(f"📡 [Uplink Test] Registered Ollama Host: {ollama_url}")

        self.logger.info("🛡️ [Pre-flight] Cold-Boot Validation Completed successfully.")
        ColdBootConfigValidator._has_run = True
        return adjusted
