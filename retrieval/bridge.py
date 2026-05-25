import os
import hashlib
import time
from pathlib import Path
from typing import List, Dict
import numpy as np

class LatentBridge:
    """🔗 [Super-Synapse] Collega la documentazione web al codice sorgente locale.
    Ridenominato da CodeDocBridger per compatibilità con il Kernel v0.5.0.
    """
    def __init__(self, vault=None, project_root=None, settings=None, **kwargs):
        self.vault = vault
        self.settings = settings
        # Se project_root è None o codebase_bridging è OFF, disattiviamo la scansione
        self.project_root = Path(project_root) if project_root else None
        self.code_signatures = self._scan_codebase() if (self.project_root and self.settings and self.settings.get("codebase_bridging", False)) else {}
        self.unified_dim = kwargs.get("unified_dim", 1024)

    def _scan_codebase(self) -> Dict[str, Path]:
        signatures = {}
        root = self.project_root
        if not root: return signatures
        # Estendiamo le estensioni supportate
        for ext in ['*.py', '*.md', '*.rs', '*.js', '*.ts', '*.html', '*.css']:
            try:
                for path in root.rglob(ext):
                    # Escludiamo cartelle di sistema e build
                    if any(x in str(path) for x in ['venv', '.git', '__pycache__', 'node_modules', 'dist', 'build']):
                        continue
                    try:
                        content = path.read_text()
                        for line in content.splitlines():
                            if 'class ' in line or 'def ' in line or 'function ' in line:
                                parts = line.split('(')
                                if len(parts) > 0:
                                    # Estrazione nome pulito
                                    name = parts[0].replace('class', '').replace('def', '').replace('async', '').replace('function', '').strip()
                                    if len(name) > 3 and not name.startswith('_'):
                                        signatures[name.lower()] = path
                    except: pass
            except: pass
        return signatures

    def _extract_body(self, lines: List[str], start_idx: int) -> str:
        """Estrae il blocco di codice basandosi sull'indentazione (Pythonic)."""
        first_line = lines[start_idx]
        indent = len(first_line) - len(first_line.lstrip())
        body = [first_line]
        for i in range(start_idx + 1, len(lines)):
            line = lines[i]
            if not line.strip(): 
                body.append(line)
                continue
            curr_indent = len(line) - len(line.lstrip())
            if curr_indent <= indent: break
            body.append(line)
        return "\n".join(body[:50]) # Limite per evitare nodi giganteschi legati a file enormi

    async def ingest_codebase(self):
        """Versione v3.0.0: Ingestione proattiva con cache SHA256 e AST Extractor."""
        if not self.vault or not self.project_root: return
        
        # 🛡️ [Proprioception Toggle] Verifica se l'utente vuole che il sistema guardi se stesso
        if self.settings and not self.settings.get("codebase_bridging", False):
            return
            
        from retrieval.file_cache import SovereignFileCache
        from retrieval.ast_extractor import SovereignASTExtractor
        from index.node import RelationType
        
        file_cache = SovereignFileCache()
        ast_extractor = SovereignASTExtractor(self.project_root)
        
        print(f"🏗️ [Bridge] Ingestione codebase granulare da {self.project_root}...")
        nodes_created = 0
        nodes_updated = 0
        
        # Mappa globale per risolvere callee_name -> node_id all'interno dello stesso modulo o in tutta la codebase
        func_map = {}  # {function_name_lowercase: node_id}
        
        # 1. Scansioniamo e leggiamo tutti i file
        all_files = []
        for ext in ['*.py', '*.md', '*.rs', '*.js', '*.ts', '*.html', '*.css']:
            try:
                for path in self.project_root.rglob(ext):
                    if any(x in str(path) for x in ['venv', '.git', '__pycache__', 'node_modules', 'dist', 'build', 'legacy_scratch', 'pending_patches']):
                        continue
                    all_files.append(path)
            except Exception:
                pass
                
        # Scansioniamo prima i file Python per registrare classi/funzioni nella mappa globale
        for path in all_files:
            if path.suffix == '.py':
                try:
                    rel_path = str(path.relative_to(self.project_root))
                    content = path.read_text(encoding="utf-8", errors="ignore")
                    import ast as py_ast
                    tree = py_ast.parse(content)
                    for node in py_ast.walk(tree):
                        if isinstance(node, (py_ast.FunctionDef, py_ast.AsyncFunctionDef)):
                            func_name = node.name
                            func_hash = hashlib.md5(f"{rel_path}:{func_name}".encode()).hexdigest()[:10]
                            func_id = f"src_{func_hash}"
                            func_map[func_name.lower()] = func_id
                except Exception:
                    pass

        # 2. Elaborazione di ciascun file
        for path in all_files:
            try:
                rel_path = str(path.relative_to(self.project_root))
                
                # Controlliamo la cache SHA256
                if not file_cache.has_changed(path):
                    continue
                
                if path.suffix == '.py':
                    ast_data = ast_extractor.extract_ast(path)
                    if not ast_data:
                        continue
                    
                    # A. Ingestiamo il modulo
                    module = ast_data["module"]
                    await self.vault.add_node(
                        module["id"],
                        module["text"],
                        metadata={
                            "source": rel_path,
                            "origin": "local_bridge",
                            "context": "proprioception",
                            "type": "code_module",
                            "name": module["name"],
                            "color": "#3b82f6"
                        }
                    )
                    nodes_created += 1
                    
                    # B. Ingestiamo le classi
                    for cls in ast_data["classes"]:
                        await self.vault.add_node(
                            cls["id"],
                            cls["text"],
                            metadata={
                                "source": rel_path,
                                "origin": "local_bridge",
                                "context": "proprioception",
                                "type": "code_class",
                                "name": cls["name"],
                                "color": "#a855f7"
                            }
                        )
                        # Relazione modulo -> classe
                        self.vault.add_relation(module["id"], cls["id"], RelationType.CHILD)
                        nodes_created += 1
                        
                    # C. Ingestiamo le funzioni/metodi
                    for func in ast_data["functions"]:
                        await self.vault.add_node(
                            func["id"],
                            func["text"],
                            metadata={
                                "source": rel_path,
                                "origin": "local_bridge",
                                "context": "proprioception",
                                "type": "code_function",
                                "name": func["name"],
                                "color": "#00ff9d"
                            }
                        )
                        # Relazione parent -> child
                        self.vault.add_relation(func["parent_id"], func["id"], RelationType.CHILD)
                        nodes_created += 1
                        
                    # D. Creazione delle relazioni di chiamata (Function calls Function)
                    for call in ast_data["calls"]:
                        callee_name = call["callee_name"].lower()
                        if callee_name in func_map:
                            callee_id = func_map[callee_name]
                            self.vault.add_relation(call["caller_id"], callee_id, RelationType.REQUIRES)
                            
                    # E. Creazione delle relazioni di importazione (Module requires Module/Library)
                    for imp in ast_data["imports"]:
                        imp_module_name = imp.split('.')[0].lower()
                        for p in all_files:
                            p_mod_name = p.stem.lower()
                            if p_mod_name == imp_module_name:
                                target_hash = hashlib.md5(f"{str(p.relative_to(self.project_root))}:module".encode()).hexdigest()[:10]
                                target_id = f"src_{target_hash}"
                                self.vault.add_relation(module["id"], target_id, RelationType.REQUIRES)
                                break
                                
                else:
                    # File non Python (legacy signature o markdown/css/html generici)
                    content = path.read_text(encoding="utf-8", errors="ignore")
                    node_id = f"src_{hashlib.md5(f'{rel_path}:{path.name}'.encode()).hexdigest()[:10]}"
                    text_content = f"SOURCE_CODE_ASSET [{path.name}]\nFILE: {path.name}\nPATH: {rel_path}\n\n{content[:2000]}"
                    
                    await self.vault.add_node(
                        node_id, 
                        text_content, 
                        metadata={
                            "source": rel_path,
                            "origin": "local_bridge",
                            "context": "proprioception",
                            "type": "code_asset",
                            "name": path.name,
                            "color": "#64748b" 
                        }
                    )
                    nodes_created += 1
                
                # Aggiorniamo e salviamo la cache
                file_cache.update(path)
                file_cache.save()
                
            except Exception as e:
                print(f"⚠️ [Bridge Ingestion Error] Failed to ingest {path}: {e}")
                
        report = f"✅ [Bridge] Codebase sincronizzata: {nodes_created} nuovi."
        print(report)

    def _bridge_nodes_legacy(self, target_vault) -> int:
        """Fallback: Matching testuale se i vettori non sono disponibili."""
        bridges_created = 0
        web_nodes = [nid for nid, node in list(target_vault._nodes.items()) if node.metadata.get("origin") == "web_forager"]
        src_nodes = [nid for nid, node in list(target_vault._nodes.items()) if node.metadata.get("origin") == "local_bridge"]
        
        # [v4.1.6 Fix] O(N^2) regex search is too slow for 35M iterations. Use exact matching or skip.
        # print(f"⚠️ [Bridge] Skipping legacy O(N^2) text matching to prevent event loop blocking. ({len(web_nodes)}x{len(src_nodes)})")
        return bridges_created

    def bridge_nodes(self, vault=None, threshold=0.75) -> int:
        """🔗 [CB-003 Upgrade] Semantic Bridging: Collega codice e docs tramite similarità vettoriale."""
        target_vault = vault or self.vault
        if not target_vault: return 0

        # 0. [v4.1.4] Proprioception Check: Se il toggle è OFF, non creiamo ponti semantici col codice
        if self.settings and not self.settings.get("codebase_bridging", False):
            return 0

        # 1. Triage dei Nodi (Web vs Local Code) with explicit NIC hydration
        all_vault_nodes = [target_vault.get_node(nid) for nid in list(target_vault._nodes.keys())]
        web_nodes = [n for n in all_vault_nodes if n and n.metadata.get("origin") == "web_forager" and getattr(n, "vector", None) is not None and len(n.vector) > 0]
        src_nodes = [n for n in all_vault_nodes if n and n.metadata.get("origin") == "local_bridge" and getattr(n, "vector", None) is not None and len(n.vector) > 0]
        
        if not web_nodes or not src_nodes:
            return self._bridge_nodes_legacy(target_vault)
        
        # print(f"📡 [Bridge] Analisi Semantica: {len(web_nodes)} documenti web vs {len(src_nodes)} file sorgente...")
        
        # 2. Calcolo Matrice di Similarità (Batch Vector Support)
        # Nodi normalizzati in post_init -> dot product = cosine similarity
        web_vectors = np.array([n.vector for n in web_nodes], dtype=np.float32)
        src_vectors = np.array([n.vector for n in src_nodes], dtype=np.float32)
        
        sim_matrix = np.dot(web_vectors, src_vectors.T)
        max_sim = float(np.max(sim_matrix)) if sim_matrix.size > 0 else 0
        
        # Logghiamo solo se c'è un interesse reale o ogni tanto (frequenza ridotta)
        if max_sim > threshold * 0.8:
            print(f"📊 [Bridge] Similarità Rilevata: {max_sim:.4f} (Threshold: {threshold})")
        matches = np.where(sim_matrix > threshold)
        
        bridges_created = 0
        from index.node import SemanticEdge, RelationType
        
        for w_idx, s_idx in zip(*matches):
            wnode = web_nodes[w_idx]
            snode = src_nodes[s_idx]
            score = float(sim_matrix[w_idx, s_idx])
            
            # 3. [v4.1.5 Fix] Cross-Context Bridging: Permettiamo il legame tra Web e Codice
            w_context = wnode.metadata.get("context", "user")
            s_context = snode.metadata.get("context", "proprioception")
            
            # Consentiamo il bridge se uno è propriocezione (codice) e l'altro è ricerca esterna
            is_valid_bridge = (w_context == s_context) or \
                              (s_context == "proprioception" and w_context in ["user", "yoda_pilgrimage", "SkyWalker-Core"])
            
            if not is_valid_bridge:
                continue

            # Evita duplicati
            if any(e.target_id == snode.id for e in wnode.edges):
                continue
                
            # 3. Creazione Super-Sinapsi (Aura RGB)
            reason = f"Semantic Match ({int(score*100)}%): Code logic correlates with web findings."
            
            # Legame Doc -> Codice
            edge_doc = SemanticEdge(target_id=snode.id, relation=RelationType.SIMILARITY, weight=score, source="bridge_aura")
            setattr(edge_doc, 'is_aura', True)
            setattr(edge_doc, 'reason', reason)
            wnode.edges.append(edge_doc)
            
            # 📝 [v14.5 Fix] Set metadata for engine stats
            if "code_bridges" not in wnode.metadata: wnode.metadata["code_bridges"] = []
            wnode.metadata["code_bridges"].append(snode.metadata.get("name", "unknown"))

            # Legame Codice -> Doc (Bidirezionale)
            edge_code = SemanticEdge(target_id=wnode.id, relation=RelationType.SIMILARITY, weight=score, source="bridge_aura")
            setattr(edge_code, 'is_aura', True)
            setattr(edge_code, 'reason', reason)
            snode.edges.append(edge_code)
            
            bridges_created += 1
            
        # 4. Fallback per precisione nominale
        legacy_count = self._bridge_nodes_legacy(target_vault)
        
        return bridges_created + legacy_count
