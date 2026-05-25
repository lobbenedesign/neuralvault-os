"""
core/obsidian_normalizer.py
───────────────────────────
Sovereign Obsidian Note Normalizer & Semantic Linker (v15.0).
Fornisce normalizzazione local-first delle note Markdown, garantendo la coerenza
del frontmatter, dei tag Obsidian e iniettando link semantici [[WikiPage]] nel Vault.
"""

import os
import re
import json
import time
import threading
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger("NeuralVault-ObsidianNormalizer")

class SovereignObsidianNormalizer:
    """
    🧹 [OBSIDIAN NOTE NORMALIZER]
    Normalizza le note locali degli utenti per Obsidian e vi inietta riferimenti semantici bidirezionali.
    """
    def __init__(self, engine, watch_dir: str = "vault_data/wiki"):
        self.engine = engine
        self.watch_dir = Path(watch_dir).resolve()
        self.watch_dir.mkdir(parents=True, exist_ok=True)
        self.active = False
        self._thread = None
        self._lock = threading.Lock()
        self.normalized_hashes = {}

    def start(self):
        """Avvia il thread di background per il monitoraggio della directory."""
        with self._lock:
            if not self.active:
                self.active = True
                self._thread = threading.Thread(target=self._watcher_loop, daemon=True)
                self._thread.start()
                logger.info(f"🐙 [Obsidian Normalizer] Demone di monitoraggio avviato su: {self.watch_dir}")

    def stop(self):
        """Arresta il thread di monitoraggio."""
        with self._lock:
            self.active = False
            logger.info("🐙 [Obsidian Normalizer] Arresto demone completato.")

    def _watcher_loop(self):
        """Loop di polling di background per rilevare file modificati o nuovi."""
        while self.active:
            try:
                self.normalize_workspace()
            except Exception as e:
                logger.error(f"Error during workspace normalization: {e}")
            time.sleep(10.0) # Esegue i controlli ogni 10 secondi

    def normalize_workspace(self):
        """Scansiona la directory e normalizza tutti i file markdown modificati o privi di frontmatter."""
        md_files = list(self.watch_dir.rglob("*.md"))
        
        # Recupera tutte le entità per iniettare i link bidirezionali
        wiki_topics = []
        for f in md_files:
            # Esclude file di report o speciali
            if f.name not in ["index.md", "purpose.md", "gaps.md"]:
                wiki_topics.append(f.stem)

        for filepath in md_files:
            if filepath.name in ["index.md", "purpose.md", "gaps.md"]:
                continue
                
            try:
                stat = filepath.stat()
                file_hash = f"{stat.st_mtime}_{stat.st_size}"
                
                # Se il file non è cambiato, saltalo
                if self.normalized_hashes.get(str(filepath)) == file_hash:
                    continue
                    
                self._normalize_file(filepath, wiki_topics)
                
                # Aggiorna hash post-modifica
                new_stat = filepath.stat()
                self.normalized_hashes[str(filepath)] = f"{new_stat.st_mtime}_{new_stat.st_size}"
            except Exception as e:
                logger.error(f"Failed to normalize file {filepath.name}: {e}")

    def _normalize_file(self, filepath: Path, wiki_topics: List[str]):
        """Normalizza una singola nota Markdown iniettando frontmatter e wiki link semantici."""
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        # 1. Parsing frontmatter YAML esistente
        frontmatter = {}
        body = content
        
        fm_match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
        if fm_match:
            fm_text = fm_match.group(1)
            body = content[fm_match.end():]
            for line in fm_text.split("\n"):
                if ":" in line:
                    k, v = line.split(":", 1)
                    frontmatter[k.strip()] = v.strip().strip('"').strip("'")

        # 2. Arricchimento dei Metadati del Frontmatter
        modified = False
        if "normalized_at" not in frontmatter:
            frontmatter["normalized_at"] = datetime.now().isoformat()
            modified = True
            
        if "type" not in frontmatter:
            frontmatter["type"] = "obsidian_note"
            modified = True

        if "status" not in frontmatter:
            frontmatter["status"] = "STABLE"
            modified = True

        # 3. Iniezione automatica dei WikiLink [[Topic]] nel testo
        new_body = body
        for topic in wiki_topics:
            if topic.lower() == filepath.stem.lower():
                continue
                
            # Pattern per trovare parole esatte che corrispondono al topic ma che non sono già racchiuse in parentesi quadre
            pattern = rf"\b({re.escape(topic)})\b(?![^\[]*\])"
            
            # Sostituisce la parola con il wikilink nativo di Obsidian
            temp_body, count = re.subn(pattern, r"[[\1]]", new_body, flags=re.IGNORECASE)
            if count > 0:
                new_body = temp_body
                modified = True

        # 4. Riscrittura del file se modificato
        if modified:
            fm_lines = ["---"]
            for k, v in frontmatter.items():
                fm_lines.append(f"{k}: \"{v}\"")
            fm_lines.append("---")
            
            new_content = "\n".join(fm_lines) + "\n\n" + new_body.strip() + "\n"
            
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(new_content)
                
            logger.info(f"🧹 [Normalizer] File '{filepath.name}' normalizzato e aggiornato semanticamente.")
            
            # Commit atomico dello stato modificato nel Git Ledger
            if hasattr(self.engine, 'wiki'):
                self.engine.wiki.commit_vault_state(f"Obsidian Note Normalization: '{filepath.stem}' updated")
