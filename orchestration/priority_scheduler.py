import asyncio
import heapq
import time
import uuid
import logging
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Optional

logger = logging.getLogger("Aegis")
logger.setLevel(logging.INFO)

@dataclass(order=True)
class SovereignTask:
    priority: int
    timestamp: float # Second field for comparison if priority is equal
    task_id: str = field(compare=False)
    func: Callable = field(compare=False)
    args: tuple = field(compare=False)
    kwargs: dict = field(compare=False)
    retries: int = field(compare=False, default=3)

class SovereignTaskScheduler:
    """
    ⚖️ SovereignTaskScheduler v1.1
    Gestisce la coda di priorità degli agenti.
    """
    def __init__(self, concurrency_limit: int = 12):
        self.queue = [] # Heap per priorità
        self.concurrency_limit = concurrency_limit
        self.active_tasks = 0
        self._loop_active = False
        self._lock = None # Lazy initialization
        self._loop_task = None

    def _get_lock(self):
        if self._lock is None:
            self._lock = asyncio.Lock()
        return self._lock

    async def submit(self, priority: int, func: Callable, *args, **kwargs):
        """Inserisce un nuovo task nella coda di priorità."""
        task_id = str(uuid.uuid4())[:8]
        print(f"DEBUG: submit called for task_id {task_id}")
        task = SovereignTask(
            priority=priority,
            timestamp=time.time(),
            task_id=task_id,
            func=func,
            args=args,
            kwargs=kwargs
        )
        
        lock = self._get_lock()
        print(f"DEBUG: task {task_id} waiting for lock {id(lock)}")
        async with lock:
            heapq.heappush(self.queue, task)
            print(f"📥 [Scheduler] Task {task_id} queued (Priority: {priority}, Queue Size: {len(self.queue)})")
            
            if not self._loop_active:
                self._loop_active = True
                print("⚙️ [Scheduler] Starting process loop...")
                asyncio.create_task(self._process_loop())

    async def _process_loop(self):
        print("⚙️ [Scheduler] Processing loop STARTED.")
        while True:
            lock = self._get_lock()
            async with lock:
                if not self.queue:
                    self._loop_active = False
                    print("⚙️ [Scheduler] Queue empty. Hibernating loop.")
                    break
                
                if self.active_tasks < self.concurrency_limit:
                    task = heapq.heappop(self.queue)
                    self.active_tasks += 1
                    print(f"⚡ [Scheduler] Dispatching {task.task_id} (Active: {self.active_tasks}/{self.concurrency_limit})")
                    asyncio.create_task(self._run_task(task))
                    continue # Try to pop another one immediately
                else:
                    if time.time() % 5 < 0.1: # Throttle logs
                        print(f"⏳ [Scheduler] Full capacity ({self.active_tasks}/{self.concurrency_limit}). Waiting...")
            
            await asyncio.sleep(0.1)

    async def _run_task(self, task: SovereignTask):
        print(f"🚀 [Scheduler] Task {task.task_id} EXECUTION START")
        try:
            if asyncio.iscoroutinefunction(task.func):
                await task.func(*task.args, **task.kwargs)
            else:
                loop = asyncio.get_running_loop()
                await loop.run_in_executor(None, task.func, *task.args, **task.kwargs)
        except Exception as e:
            print(f"❌ [Scheduler] Task {task.task_id} failed: {e}")
            if task.retries > 0:
                task.retries -= 1
                print(f"🔄 [Scheduler] Retrying {task.task_id} ({task.retries} left)")
                lock = self._get_lock()
                async with lock:
                    heapq.heappush(self.queue, task)
        finally:
            lock = self._get_lock()
            async with lock:
                self.active_tasks -= 1
            print(f"🏁 [Scheduler] Task {task.task_id} FINISHED (Active: {self.active_tasks})")

# Singleton
SCHEDULER = SovereignTaskScheduler()
