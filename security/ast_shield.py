import ast
import logging

class ASTSafetyShield:
    """
    🛡️ [v4.1.4] AST PARRY SHIELD
    Analizzatore statico per prevenire l'esecuzione di codice pericoloso
    generato autonomamente dagli agenti.
    """
    
    # Comandi e moduli strettamente vietati
    FORBIDDEN_MODULES = {'os', 'shutil', 'subprocess', 'socket', 'requests', 'httpx_inside_eval'}
    FORBIDDEN_FUNCS = {
        'remove', 'rmdir', 'removedirs', 'system', 'popen', 'kill', 
        'terminate', 'rmtree', 'eval', 'exec', 'getattr', 'setattr'
    }

    @staticmethod
    def is_safe(code: str) -> tuple[bool, str]:
        """Analizza il codice e restituisce (is_safe, reason)."""
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            return False, f"Syntax Error: {e}"

        for node in ast.walk(tree):
            # 1. Controllo Import Pericolosi
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name in ASTSafetyShield.FORBIDDEN_MODULES:
                        return False, f"Forbidden import detected: {alias.name}"
            
            if isinstance(node, ast.ImportFrom):
                if node.module in ASTSafetyShield.FORBIDDEN_MODULES:
                    return False, f"Forbidden import from detected: {node.module}"

            # 2. Controllo Chiamate a Funzioni Vietate
            if isinstance(node, ast.Call):
                func = node.func
                # Funzione diretta (es: eval())
                if isinstance(func, ast.Name):
                    if func.id in ASTSafetyShield.FORBIDDEN_FUNCS:
                        return False, f"Forbidden function call: {func.id}"
                
                # Funzione da attributo (es: os.system())
                if isinstance(func, ast.Attribute):
                    if func.attr in ASTSafetyShield.FORBIDDEN_FUNCS:
                        return False, f"Forbidden method call: {func.attr}"

        return True, "Code cleared by AST Shield."
