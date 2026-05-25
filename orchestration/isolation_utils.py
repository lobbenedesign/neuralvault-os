import functools
from orchestration.executor_pool import EXECUTOR_POOL

def sovereign_compute(func):
    """Decorator to mark a function as CPU-bound and run it in the ProcessPool."""
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        return await EXECUTOR_POOL.run_cpu(func, *args, **kwargs)
    return wrapper

def sovereign_io(func):
    """Decorator to mark a function as I/O-bound and run it in the ThreadPool."""
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        return await EXECUTOR_POOL.run_io(func, *args, **kwargs)
    return wrapper

def detect_task_affinity(task_name: str) -> str:
    """Rileva se un task dovrebbe essere CPU o IO bound in base al nome."""
    cpu_bound_keywords = ["train", "compress", "encrypt", "parse", "embed"]
    if any(k in task_name.lower() for k in cpu_bound_keywords):
        return "cpu"
    return "io"
