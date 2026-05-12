import re

class SovereignRedactor:
    """
    Utility per la sanificazione dei contenuti della Wiki.
    Rimuove API keys, credenziali e informazioni sensibili prima della persistenza.
    """
    PATTERNS = {
        "api_key": r'(?:api_key|secret|token|password|auth|key)["\']?\s*[:=]\s*["\']?([a-zA-Z0-9_\-]{16,})["\']?',
        "huggingface_token": r'hf_[a-zA-Z0-9]{34}',
        "openai_key": r'sk-[a-zA-Z0-9]{48}',
        "anthropic_key": r'sk-ant-api03-[a-zA-Z0-9_\-]{95}',
        "email": r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    }

    def redact(self, text: str) -> str:
        if not text: return ""
        redacted = text
        for name, pattern in self.PATTERNS.items():
            redacted = re.sub(pattern, f" [REDACTED_{name.upper()}] ", redacted)
        return redacted

redactor = SovereignRedactor()
