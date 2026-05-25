import os
import json
import hashlib
from pathlib import Path

class SovereignFileCache:
    """🛡️ [SHA256 Pre-Ingestion Cache]
    Previene l'elaborazione ridondante dei file sorgente non modificati.
    """
    def __init__(self, cache_path: str = "vault_data/file_cache.json"):
        self.cache_path = Path(cache_path)
        self.cache = {}
        self.load()

    def load(self):
        if self.cache_path.exists():
            try:
                with open(self.cache_path, "r", encoding="utf-8") as f:
                    self.cache = json.load(f)
            except Exception as e:
                print(f"⚠️ [File Cache] Load failed: {e}")
                self.cache = {}

    def save(self):
        try:
            self.cache_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.cache_path, "w", encoding="utf-8") as f:
                json.dump(self.cache, f, indent=4)
        except Exception as e:
            print(f"⚠️ [File Cache] Save failed: {e}")

    def get_sha256(self, filepath: Path) -> str:
        try:
            h = hashlib.sha256()
            with open(filepath, "rb") as f:
                for chunk in iter(lambda: f.read(8192), b""):
                    h.update(chunk)
            return h.hexdigest()
        except Exception:
            return ""

    def has_changed(self, filepath: Path) -> bool:
        sha = self.get_sha256(filepath)
        if not sha:
            return False  # Se il file è illeggibile, non considerarlo modificato
        cached_sha = self.cache.get(str(filepath))
        return cached_sha != sha

    def update(self, filepath: Path):
        sha = self.get_sha256(filepath)
        if sha:
            self.cache[str(filepath)] = sha
