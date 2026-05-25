import ast
import hashlib
from pathlib import Path
from typing import Dict, List, Any

class SovereignASTExtractor:
    """🔬 [AST Extractor]
    Parser Python standard 'ast' per tradurre moduli, classi, funzioni, import
    e chiamate in relazioni causali e gerarchiche deterministiche.
    """
    def __init__(self, project_root: Path):
        self.project_root = project_root

    def extract_ast(self, filepath: Path) -> Dict[str, Any]:
        """Parsa un file Python ed estrae la struttura gerarchica e le chiamate."""
        try:
            content = filepath.read_text(encoding="utf-8")
            return self.extract_ast_from_text(content, str(filepath.name), str(filepath.relative_to(self.project_root)))
        except Exception as e:
            print(f"⚠️ [AST Extractor] Error reading {filepath}: {e}")
            return {}

    def extract_ast_from_text(self, content: str, filename: str, rel_path: str) -> Dict[str, Any]:
        """Parsa codice Python da stringa."""
        try:
            tree = ast.parse(content, filename=filename)
        except Exception as e:
            print(f"⚠️ [AST Extractor] AST parse failed for {filename}: {e}")
            return {}

        module_hash = hashlib.md5(f"{rel_path}:module".encode()).hexdigest()[:10]
        module_id = f"src_{module_hash}"

        result = {
            "module": {
                "id": module_id,
                "name": filename,
                "path": rel_path,
                "text": f"CODE_MODULE [{filename}]\nPATH: {rel_path}\n\nQuesto modulo rappresenta il file di codice sorgente locale.",
                "type": "code_module"
            },
            "classes": [],
            "functions": [],
            "imports": [],
            "calls": []
        }

        class ASTVisitor(ast.NodeVisitor):
            def __init__(self, rel_path: str, module_id: str):
                self.rel_path = rel_path
                self.module_id = module_id
                self.classes = []
                self.functions = []
                self.imports = []
                self.calls = []
                self.current_class = None

            def visit_ClassDef(self, node):
                class_name = node.name
                class_hash = hashlib.md5(f"{self.rel_path}:{class_name}".encode()).hexdigest()[:10]
                class_id = f"src_{class_hash}"

                body_text = ""
                try:
                    body_text = ast.unparse(node.body[:5])
                except Exception:
                    body_text = f"class {class_name}"

                self.classes.append({
                    "id": class_id,
                    "name": class_name,
                    "parent_id": self.module_id,
                    "text": f"CODE_CLASS [{class_name}]\nMODULE: {self.rel_path}\n\nclass {class_name}:\n{body_text}",
                    "type": "code_class"
                })

                old_class = self.current_class
                self.current_class = class_id
                self.generic_visit(node)
                self.current_class = old_class

            def visit_FunctionDef(self, node):
                self.handle_function(node)

            def visit_AsyncFunctionDef(self, node):
                self.handle_function(node)

            def handle_function(self, node):
                func_name = node.name
                full_name = f"{self.current_class}_{func_name}" if self.current_class else func_name
                func_hash = hashlib.md5(f"{self.rel_path}:{full_name}".encode()).hexdigest()[:10]
                func_id = f"src_{func_hash}"

                body_text = ""
                try:
                    body_text = ast.unparse(node.body[:5])
                except Exception:
                    body_text = f"def {func_name}"

                self.functions.append({
                    "id": func_id,
                    "name": func_name,
                    "parent_id": self.current_class or self.module_id,
                    "text": f"CODE_FUNCTION [{func_name}]\nMODULE: {self.rel_path}\n\ndef {func_name}:\n{body_text}",
                    "type": "code_function"
                })

                # Cerca le chiamate di funzioni all'interno di questa funzione
                for child in ast.walk(node):
                    if isinstance(child, ast.Call) and isinstance(child.func, ast.Name):
                        self.calls.append({
                            "caller_id": func_id,
                            "callee_name": child.func.id
                        })

            def visit_Import(self, node):
                for name in node.names:
                    self.imports.append(name.name)

            def visit_ImportFrom(self, node):
                module = node.module or ""
                for name in node.names:
                    self.imports.append(f"{module}.{name.name}")

        visitor = ASTVisitor(rel_path, module_id)
        visitor.visit(tree)

        result["classes"] = visitor.classes
        result["functions"] = visitor.functions
        result["imports"] = visitor.imports
        result["calls"] = visitor.calls

        return result
