import random
import time
import asyncio
import logging
from typing import Optional, Dict, List
from curl_cffi import requests as curl_requests

logger = logging.getLogger("Aegis")

class SovereignProxyManager:
    """
    🛡️ Sovereign Proxy Manager v1.0
    Gestisce la rotazione degli IP, l'integrazione Tor e lo shielding delle identità.
    """
    
    def __init__(self, tor_proxy: str = "socks5://127.0.0.1:9050", tor_control_port: int = 9051):
        self.tor_proxy = tor_proxy
        self.tor_control_port = tor_control_port
        self.use_tor = False
        self._check_tor_presence()
        
        # Pool di identità (Sessioni con fingerprint diversi)
        self.identities = ["chrome120", "chrome124", "safari17_0"]
        self.current_identity_idx = 0
        
    def _check_tor_presence(self):
        """Verifica se Tor è attivo localmente."""
        import socket
        try:
            # Controllo veloce della porta socks
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1)
            # Analizziamo l'host e la porta dall'URL
            host = "127.0.0.1"
            port = 9050
            if ":" in self.tor_proxy:
                parts = self.tor_proxy.split(":")
                port = int(parts[-1])
                host = parts[-2].replace("//", "")
                
            result = s.connect_ex((host, port))
            if result == 0:
                self.use_tor = True
                logger.info("📡 [ProxyManager] Tor detected and enabled for Extreme Fallback.")
            s.close()
        except Exception:
            self.use_tor = False

    async def rotate_tor_identity(self):
        """Invia il segnale NEWNYM a Tor per cambiare IP."""
        if not self.use_tor:
            return False
            
        try:
            # Implementazione light via socket per non dipendere da 'stem' se non presente
            import socket
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect(("127.0.0.1", self.tor_control_port))
                s.sendall(b'AUTHENTICATE ""\r\n')
                s.sendall(b'SIGNAL NEWNYM\r\n')
                s.sendall(b'QUIT\r\n')
            logger.info("🔄 [ProxyManager] Tor Identity Rotated (NEWNYM sent).")
            await asyncio.sleep(2) # Grace period per il nuovo circuito
            return True
        except Exception as e:
            logger.error(f"❌ [ProxyManager] Failed to rotate Tor: {e}")
            return False

    def get_session_config(self, force_tor: bool = False) -> Dict:
        """Restituisce la configurazione per una nuova sessione curl_cffi."""
        config = {
            "impersonate": random.choice(self.identities),
            "timeout": 30,
            "proxies": None
        }
        
        if force_tor and self.use_tor:
            config["proxies"] = {"http": self.tor_proxy, "https": self.tor_proxy}
            
        return config

# Singleton
PROXY_MGR = SovereignProxyManager()
