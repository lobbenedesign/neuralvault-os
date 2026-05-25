import os
import sys
import py_compile
import logging
from pathlib import Path
from typing import Dict, Optional
from security.ast_shield import ASTSafetyShield

logger = logging.getLogger("NeuralVault-Actuator")

class EvolutionActuator:
    """
    🛠️ [EVOLUTION ACTUATOR]
    Responsabile dell'applicazione fisica delle modifiche al codice sorgente.
    Include meccanismi di validazione sintattica pre-commit.
    """
    def __init__(self, project_root: str):
        self.root = Path(project_root)
        self.pending_dir = self.root / "pending_patches"
        self.pending_dir.mkdir(exist_ok=True)

    def apply_fix(self, file_path: str, line_number: int, new_content: str) -> Dict:
        """
        Applica chirurgicamente una modifica a un file .py e convalida tramite Test Suite.
        """
        # --- [SANDBOX STAGE 0] AST PARRY SHIELD ---
        is_safe, reason = ASTSafetyShield.is_safe(new_content)
        if not is_safe:
            logger.warning(f"🛑 [Security Violation] Agent proposed unsafe code: {reason}")
            return {"success": False, "error": f"Security Shield Violation: {reason}"}

        full_path = self.root / file_path
        if not full_path.exists():
            return {"success": False, "error": f"File {file_path} not found."}

        try:
            with open(full_path, "r") as f:
                lines = f.readlines()

            # Backup temporaneo per validazione
            temp_path = full_path.with_suffix(".py.tmp")
            
            # Applicazione modifica
            if 0 < line_number <= len(lines):
                lines[line_number - 1] = new_content + "\n"
            else:
                lines.append("\n" + new_content + "\n")

            with open(temp_path, "w") as f:
                f.writelines(lines)

            # --- [SANDBOX STAGE 1] VALIDAZIONE SINTATTICA ---
            try:
                py_compile.compile(str(temp_path), doraise=True)
            except py_compile.PyCompileError as e:
                if temp_path.exists(): os.remove(temp_path)
                return {"success": False, "error": f"Syntax Error: {e}"}

            # --- [SANDBOX STAGE 2] INTEGRITY TEST SUITE ---
            # Applichiamo la modifica temporaneamente per far girare i test sul sistema "reale"
            backup_path = full_path.with_suffix(".py.bak")
            os.replace(full_path, backup_path)
            os.replace(temp_path, full_path)
            
            test_results = self.run_integrity_tests()
            
            # [SAFE EVOLUTION V11: HUMAN-IN-THE-LOOP]
            # Ripristiniamo SEMPRE il backup originale, non modifichiamo più i file core direttamente.
            os.replace(backup_path, full_path)
            
            if not test_results["success"]:
                return {"success": False, "error": f"Integrity Test Failed: {test_results['error']}"}
            
            # Se valida, generiamo la patch e la salviamo in pending_patches/
            diff_content = self.dry_run_diff(file_path, line_number, new_content)
            if not diff_content:
                diff_content = f"New content or diff error for {file_path}:\n{new_content}"
                
            import time
            patch_filename = f"patch_{os.path.basename(file_path)}_{int(time.time())}.diff"
            patch_path = self.pending_dir / patch_filename
            
            with open(patch_path, "w") as f:
                f.write(diff_content)
            
            if backup_path.exists(): os.remove(backup_path)
            logger.info(f"🛡️ [Human-in-the-Loop] Fix verified. Patch saved to {patch_path} waiting for manual git merge.")
            return {"success": True, "file": file_path, "patch_path": str(patch_path), "status": "pending_human_review", "test_output": test_results.get("output")}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def run_integrity_tests(self, timeout: int = 30) -> Dict:
        """
        🛡️ [AGENTIC ACTUATOR SANDBOX]
        Esegue la suite di test in un sottoprocesso isolato con timeout.
        Previene loop infiniti o crash del Kernel durante la validazione.
        """
        import subprocess
        try:
            # Cerchiamo di usare pytest se disponibile, altrimenti unittest
            test_file = "tests/test_engine_core.py"
            cmd = [sys.executable, "-m", "pytest", test_file]
            
            logger.info(f"🧪 [Sandbox] Running Integrity Tests: {' '.join(cmd)}")
            
            # Esecuzione isolata con timeout
            process = subprocess.run(
                cmd, 
                cwd=self.root, 
                capture_output=True, 
                text=True, 
                timeout=timeout
            )
            
            if process.returncode == 0:
                return {"success": True, "output": process.stdout}
            else:
                return {"success": False, "error": process.stderr or process.stdout}
                
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Test Suite TIMEOUT: Code modification may have caused an infinite loop."}
        except Exception as e:
            return {"success": False, "error": f"Sandbox Execution Error: {str(e)}"}

    def dry_run_diff(self, file_path: str, line_number: int, new_content: str) -> Optional[str]:
        """Genera un'anteprima (diff) della modifica senza applicarla."""
        full_path = self.root / file_path
        if not full_path.exists(): return None
        
        try:
            with open(full_path, "r") as f:
                old_content = f.readlines()
            
            new_lines = old_content.copy()
            if 0 < line_number <= len(new_lines):
                new_lines[line_number - 1] = new_content + "\n"
            else:
                new_lines.append(new_content + "\n")
                
            import difflib
            diff = difflib.unified_diff(
                old_content, new_lines, 
                fromfile=f"a/{file_path}", tofile=f"b/{file_path}"
            )
            return "".join(diff)
        except:
            return None
