import random
import logging
import re
from typing import List, Dict, Optional

logger = logging.getLogger("Aegis")

class RefererChainManager:
    """Simula una catena di navigazione organica."""
    ENTRY_POINTS = {
        "google.com": ["https://www.google.com/", "https://chrome.google.com/", ""],
        "duckduckgo.com": ["https://duckduckgo.com/", ""],
        "search.brave.com": ["https://search.brave.com/", ""]
    }

    @classmethod
    def get_referer_for_query(cls, domain: str) -> str:
        base_domain = ".".join(domain.split(".")[-2:])
        points = cls.ENTRY_POINTS.get(base_domain, [""])
        return random.choice(points)

class WafSignalDetector:
    """Rileva segnali di degradazione WAF prima del blocco totale."""
    DANGER_SIGNALS = [
        "g-recaptcha", "h-captcha", "cf-challenge", "security check", 
        "prove you're human", "sei umano", "traffico insolito", 
        "unusual traffic", "automated queries", "data-honeypot"
    ]

    @classmethod
    def analyze(cls, html: str, headers: dict, is_search: bool = False) -> dict:
        """Analizza la risposta alla ricerca di bot detection."""
        signals_found = []
        html_lower = html.lower()
        
        # 1. Segnali nel contenuto
        for signal in cls.DANGER_SIGNALS:
            if signal in html_lower:
                signals_found.append(signal)
        
        # 2. Segnali negli Header
        if "cf-mitigated" in headers or "x-robots-tag" in headers:
            signals_found.append("WAF-Header-Detected")
            
        risk_level = "LOW"
        result_count = 0
        
        if is_search:
            # 3. Analisi della qualità (risultati vuoti) solo per pagine di ricerca
            result_count = len(re.findall(r'class="[^"]*(?:tF2Cxc|yuRUbf|result)[^"]*"', html_lower))
            if signals_found or result_count == 0:
                risk_level = "HIGH"
            elif result_count < 3:
                risk_level = "MEDIUM"
        else:
            if signals_found:
                risk_level = "HIGH"
            
        return {
            "risk_level": risk_level,
            "signals": signals_found,
            "result_count": result_count if is_search else None
        }
