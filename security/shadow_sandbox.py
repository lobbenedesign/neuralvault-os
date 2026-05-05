import time
import json
import logging
import traceback
import psutil
import os
import sys
import uuid
from typing import Any, Dict, List, Callable
from pathlib import Path

class ShadowAuditResult:
    """Contenitore per i risultati dell'audit in Sandbox."""
    def __init__(self, success: bool, metrics: Dict, logs: List[str], error: str = None, result: Any = None):
        self.success = success
        self.metrics = metrics
        self.logs = logs
        self.error = error
        self.result = result

class SovereignShadowSandbox:
    """
    🛡️ NeuralVault v6.0: Shadow Execution Sandbox.
    Permette l'esecuzione sicura e il benchmarking di nuove logiche agentiche.
    """
    def __init__(self, engine):
        self.engine = engine
        self.logger = logging.getLogger("ShadowSandbox")
        self.shadow_data_dir = Path(engine.data_dir) / "shadow_lab"
        self.shadow_data_dir.mkdir(parents=True, exist_ok=True)

    def run_simulation(self, task_name: str, task_fn: Callable, *args, **kwargs) -> ShadowAuditResult:
        """
        Esegue un compito in ambiente isolato e audita i risultati.
        """
        logs = []
        logs.append(f"🧪 Starting Shadow Simulation: {task_name}")
        
        # 1. Baseline Metrics (Performance Audit)
        process = psutil.Process(os.getpid())
        start_mem = process.memory_info().rss
        start_time = time.time()
        
        try:
            # 2. Execution (In questa fase l'isolamento è logico, usando dati clonati se necessario)
            # Nota: In futuro useremo subprocess o container per l'isolamento del codice.
            result = task_fn(*args, **kwargs)
            
            # 3. End Metrics
            end_time = time.time()
            end_mem = process.memory_info().rss
            
            latency = end_time - start_time
            mem_delta = (end_mem - start_mem) / (1024 * 1024) # MB
            
            metrics = {
                "latency_sec": round(latency, 4),
                "memory_delta_mb": round(mem_delta, 2),
                "status": "completed"
            }
            
            # 4. Integrity & Performance Validation (v6.0.1 Adjusted for H-RAG)
            is_valid = True
            if latency > 120.0: # Soglia estesa per clustering pesante
                logs.append("⚠️ PERFORMANCE WARNING: Latency exceeded 120s threshold.")
                is_valid = False
            
            if mem_delta > 1024: # Protezione contro memory leak (Soglia 1GB)
                logs.append("🚨 INTEGRITY ALERT: Memory spike too high (>1024MB).")
                is_valid = False
                
            logs.append(f"✅ Simulation finished. Latency: {metrics['latency_sec']}s | Mem: {metrics['memory_delta_mb']}MB")
            
            return ShadowAuditResult(success=is_valid, metrics=metrics, logs=logs, result=result)

        except Exception as e:
            error_trace = traceback.format_exc()
            self.logger.error(f"❌ Shadow Crash: {e}\n{error_trace}")
            return ShadowAuditResult(
                success=False, 
                metrics={"status": "crashed"}, 
                logs=logs, 
                error=str(e)
            )

    def test_code_snippet(self, name: str, code: str, timeout: int = 15) -> ShadowAuditResult:
        """
        Esegue un frammento di codice in un sottoprocesso isolato per testarne la stabilità.
        """
        import subprocess
        import tempfile

        logs = [f"🧪 Shadow Code Audit: {name}"]
        temp_file = self.shadow_data_dir / f"test_{uuid.uuid4().hex[:6]}.py"
        
        with open(temp_file, 'w') as f:
            f.write(code)

        start_time = time.time()
        try:
            # Esecuzione in sottoprocesso isolato
            res = subprocess.run(
                [sys.executable, str(temp_file)],
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            latency = time.time() - start_time
            success = res.returncode == 0
            
            metrics = {
                "latency_sec": round(latency, 4),
                "exit_code": res.returncode,
                "stdout_len": len(res.stdout),
                "stderr_len": len(res.stderr)
            }

            if not success:
                logs.append(f"❌ CODE CRASHED: {res.stderr[:200]}")
            else:
                logs.append(f"✅ CODE STABLE. Latency: {metrics['latency_sec']}s")

            return ShadowAuditResult(success=success, metrics=metrics, logs=logs, error=res.stderr if not success else None)

        except subprocess.TimeoutExpired:
            logs.append(f"🚨 TIMEOUT: Code took longer than {timeout}s")
            return ShadowAuditResult(success=False, metrics={"status": "timeout"}, logs=logs, error="Timeout")
        finally:
            if temp_file.exists(): temp_file.unlink()

    def audit_simulation_and_promote(self, name: str, task_fn: Callable, promotion_fn: Callable, *args, **kwargs):
        """
        Esegue una simulazione e, se ha successo, promuove i cambiamenti al sistema reale.
        """
        audit = self.run_simulation(name, task_fn, *args, **kwargs)
        if audit.success:
            self.logger.info(f"🏆 Promotion Approved for {name}. Applying changes...")
            return promotion_fn(*args, **kwargs)
        else:
            self.logger.warning(f"🛑 Promotion Denied for {name}. Issues: {audit.logs}")
            return None
