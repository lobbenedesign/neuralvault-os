import json
import time
import os
import logging
from pathlib import Path
from typing import Dict, Optional

logger = logging.getLogger("Aegis")

class SovereignSessionManager:
    """
    🍪 SovereignSessionManager v1.0
    Gestisce la persistenza dei cookie per simulare utenti reali.
    Previene il rilevamento basato su 'statelessness'.
    """
    STORAGE_DIR = Path("vault_data/sessions")
    
    # Cookie pre-configurati per bypassare i popup di consenso
    STARTER_COOKIES = {
        "google.com": {
            "CONSENT": "PENDING+987",
            "SOCS": "CAESEwgDEgk0MjI2OTg5NDgaAmVuIAEaBgiAyYSvBg"
        },
        "duckduckgo.com": {
            "ae": "d", # Accettazione privacy
            "l": "it-it"
        },
        "search.brave.com": {}
    }

    def __init__(self):
        self.STORAGE_DIR.mkdir(parents=True, exist_ok=True)
        self.sessions: Dict[str, dict] = {}
        self._load_all_sessions()

    def _load_all_sessions(self):
        session_file = self.STORAGE_DIR / "swarm_sessions.json"
        if session_file.exists():
            try:
                with open(session_file, "r") as f:
                    self.sessions = json.load(f)
            except:
                self.sessions = {}

    def _save_all_sessions(self):
        session_file = self.STORAGE_DIR / "swarm_sessions.json"
        with open(session_file, "w") as f:
            json.dump(self.sessions, f, indent=2)

    def get_session_cookies(self, domain: str) -> dict:
        """Ritorna i cookie per un dominio, inizializzandoli se necessario."""
        base_domain = ".".join(domain.split(".")[-2:])
        
        if base_domain not in self.sessions:
            self.sessions[base_domain] = {
                "cookies": self.STARTER_COOKIES.get(base_domain, {}).copy(),
                "created_at": time.time(),
                "request_count": 0
            }
        
        self.sessions[base_domain]["request_count"] += 1
        return self.sessions[base_domain]["cookies"]

    def update_session(self, domain: str, response_cookies: dict):
        """Aggiorna la sessione con i nuovi cookie ricevuti dal server."""
        base_domain = ".".join(domain.split(".")[-2:])
        if base_domain in self.sessions:
            self.sessions[base_domain]["cookies"].update(response_cookies)
            self._save_all_sessions()

    def should_rotate(self, domain: str) -> bool:
        """Verifica se la sessione è troppo vecchia o abusata (ogni 100 richieste o 24h)."""
        base_domain = ".".join(domain.split(".")[-2:])
        session = self.sessions.get(base_domain)
        if not session: return False
        
        too_many = session["request_count"] > 100
        too_old = (time.time() - session["created_at"]) > 86400
        return too_many or too_old

    def rotate(self, domain: str):
        """Resetta la sessione per un dominio."""
        base_domain = ".".join(domain.split(".")[-2:])
        if base_domain in self.sessions:
            del self.sessions[base_domain]
            self._save_all_sessions()

# Singleton Instance
SESSION_MGR = SovereignSessionManager()
