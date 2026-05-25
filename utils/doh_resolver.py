import asyncio
import time
import logging
from typing import List, Optional, Dict
import curl_cffi.requests as requests

logger = logging.getLogger("Aegis")

class SovereignDNSResolver:
    """
    🔒 SovereignDNSResolver v1.0
    Risolve i nomi di dominio via HTTPS (DoH) per prevenire il DNS Leakage.
    Include cache locale con TTL per minimizzare la latenza.
    """
    DOH_PROVIDERS = {
        "cloudflare": "https://1.1.1.1/dns-query",
        "cloudflare_backup": "https://1.0.0.1/dns-query",
        "google": "https://8.8.8.8/resolve",
        "google_backup": "https://8.8.4.4/resolve"
    }

    def __init__(self):
        self.cache: Dict[str, Dict] = {}
        self.current_provider = "cloudflare"
        self.session: Optional[requests.AsyncSession] = None
        self._session_loop: Optional[asyncio.AbstractEventLoop] = None
        self.doh_suspended_until = 0.0

    async def resolve(self, hostname: str, force_refresh: bool = False) -> Optional[List[str]]:
        """Risolve un hostname in una lista di IP via DoH."""
        now = time.time()
        
        if not force_refresh and hostname in self.cache:
            entry = self.cache[hostname]
            if entry["expires_at"] > now:
                return entry["ips"]

        # Check if DoH is temporarily suspended
        if now < self.doh_suspended_until:
            logger.info(f"🌐 [DNS/Bypass] DoH is temporarily suspended. Using standard DNS for {hostname}...")
            return await self._resolve_standard(hostname, now)

        logger.info(f"🌐 [DNS/DoH] Resolving {hostname} via {self.current_provider}...")
        
        consecutive_failures = 0
        for _ in range(len(self.DOH_PROVIDERS)):
            try:
                ips = await self._query_doh(hostname)
                if ips:
                    self.cache[hostname] = {
                        "ips": ips,
                        "expires_at": now + 300 # 5 min TTL
                    }
                    return ips
                else:
                    raise Exception("Empty or invalid DoH response")
            except Exception as e:
                logger.warning(f"⚠️ [DNS/DoH] Provider {self.current_provider} failed: {e}")
                consecutive_failures += 1
                self._rotate_provider()
        
        # Suspend DoH for 10 minutes if all providers failed
        if consecutive_failures >= len(self.DOH_PROVIDERS):
            logger.error(f"🚨 [DNS/DoH] All DoH providers failed. Suspending DoH for 10 minutes.")
            self.doh_suspended_until = now + 600

        # Immediate fallback to standard DNS
        return await self._resolve_standard(hostname, now)

    async def _query_doh(self, hostname: str) -> Optional[List[str]]:
        # Initialize or recreate session dynamically based on the active asyncio event loop
        loop = asyncio.get_running_loop()
        if self.session is None or self._session_loop != loop:
            self.session = requests.AsyncSession()
            self._session_loop = loop

        url = self.DOH_PROVIDERS[self.current_provider]
        params = {"name": hostname, "type": "A"}
        headers = {"Accept": "application/dns-json"}
        
        resp = await self.session.get(
            url, 
            params=params, 
            headers=headers, 
            impersonate="chrome120", 
            http_version="v1",
            timeout=5.0
        )
        
        if resp.status_code == 200:
            data = resp.json()
            ips = [ans["data"] for ans in data.get("Answer", []) if ans.get("type") == 1]
            return ips if ips else None
        return None

    async def _resolve_standard(self, hostname: str, now: float) -> Optional[List[str]]:
        try:
            import socket
            loop = asyncio.get_running_loop()
            addrinfo = await loop.run_in_executor(None, socket.getaddrinfo, hostname, None)
            ips = list(set([info[4][0] for info in addrinfo]))
            if ips:
                logger.info(f"🟢 [DNS/Fallback] Standard DNS resolution succeeded for {hostname}: {ips}")
                self.cache[hostname] = {
                    "ips": ips,
                    "expires_at": now + 600 # 10 min TTL
                }
                return ips
        except Exception as e:
            logger.error(f"❌ [DNS/Fallback] Standard DNS fallback failed for {hostname}: {e}")
        return None

    def _rotate_provider(self):
        providers = list(self.DOH_PROVIDERS.keys())
        idx = (providers.index(self.current_provider) + 1) % len(providers)
        self.current_provider = providers[idx]

# Singleton Instance
DNS_RESOLVER = SovereignDNSResolver()
