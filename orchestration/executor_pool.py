import concurrent.futures
import multiprocessing
import asyncio
import time
import logging
from typing import Callable, Any, Dict
from utils.hardware_advisor import ADVISOR

logger = logging.getLogger("Aegis")

class SovereignExecutorPool:
    """
    🚀 SovereignExecutorPool v1.0
    Orchestra l'esecuzione parallela isolando i task CPU dai task I/O.
    """
    def __init__(self):
        self.config = ADVISOR.get_orchestration_config()
        
        # 🧪 Process Pool per calcoli pesanti (NIC, Crypto, Parsing)
        self.cpu_executor = concurrent.futures.ProcessPoolExecutor(
            max_workers=self.config["max_compute_workers"],
            mp_context=multiprocessing.get_context("spawn") if self.config["device"] != "cpu" else None
        )
        
        # 🌐 Thread Pool per I/O (Networking, Search, Logging)
        self.io_executor = concurrent.futures.ThreadPoolExecutor(
            max_workers=self.config["max_search_workers"] * 2,
            thread_name_prefix="SovereignIO"
        )
        
        self.stats = {"cpu_tasks": 0, "io_tasks": 0, "errors": 0}

    async def run_cpu(self, func: Callable, *args, **kwargs) -> Any:
        """Esegue un task CPU-bound isolato in un processo separato."""
        loop = asyncio.get_running_loop()
        self.stats["cpu_tasks"] += 1
        try:
            return await loop.run_in_executor(self.cpu_executor, func, *args, **kwargs)
        except Exception as e:
            self.stats["errors"] += 1
            logger.error(f"❌ [Executor/CPU] Task failed: {e}")
            raise

    async def run_io(self, func: Callable, *args, **kwargs) -> Any:
        """Esegue un task I/O-bound in un thread pool dedicato."""
        loop = asyncio.get_running_loop()
        self.stats["io_tasks"] += 1
        try:
            return await loop.run_in_executor(self.io_executor, func, *args, **kwargs)
        except Exception as e:
            self.stats["errors"] += 1
            logger.error(f"❌ [Executor/IO] Task failed: {e}")
            raise

    def shutdown(self):
        self.cpu_executor.shutdown(wait=True)
        self.io_executor.shutdown(wait=True)

# Singleton Instance
EXECUTOR_POOL = SovereignExecutorPool()
