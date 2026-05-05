#!/usr/bin/env python3
"""
🏺 NEURALVAULT: UNIVERSAL AGENTIC BRIDGE (v1.0)
-----------------------------------------------
Questo script permette di integrare NeuralVault con qualsiasi AI Agent
(Antigravity, Claude Code, Codex, Opencode, ecc.) tramite riga di comando.

Uso:
  python3 nv-link.py query "Tua domanda"
  python3 nv-link.py ingest "Nuova conoscenza da salvare"
"""

import sys
import json

# Configurazione predefinita
API_URL = "http://127.0.0.1:8001"
VAULT_KEY = "vault_secret_aura_2026"

try:
    import httpx
except ImportError:
    print("\n❌ Errore: Libreria 'httpx' non trovata.")
    print("👉 Installa le dipendenze con: pip install httpx")
    sys.exit(1)

def query_vault(query, k=5):
    """Interroga la memoria neurale del Vault."""
    try:
        with httpx.Client(timeout=60.0) as client:
            resp = client.post(
                f"{API_URL}/api/chat",
                json={"query": query, "top_k": k},
                headers={"X-API-KEY": VAULT_KEY}
            )
            resp.raise_for_status()
            return resp.json()
    except Exception as e:
        return {"error": f"NeuralVault non raggiungibile. Assicurati che 'api.py' sia attivo. {str(e)}"}

def ingest_to_vault(text, source="ExternalAgent"):
    """Archivia nuova conoscenza nel Vault."""
    try:
        with httpx.Client(timeout=60.0) as client:
            resp = client.post(
                f"{API_URL}/api/ingest",
                json={"text": text, "metadata": {"source": source, "agent": "Universal_Bridge"}},
                headers={"X-API-KEY": VAULT_KEY}
            )
            resp.raise_for_status()
            return resp.json()
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    
    cmd = sys.argv[1]
    text = sys.argv[2]
    
    if cmd == "query":
        res = query_vault(text)
        if "error" in res:
            print(res["error"])
        else:
            print(f"\n🏺 Risposta dal Vault:\n{res.get('response', '')}")
            if res.get('context_used'):
                print("\n📚 Fonti consultate:")
                for s in res['context_used']:
                    print(f"- {s[:150]}...")
    
    elif cmd == "ingest":
        res = ingest_to_vault(text)
        if "error" in res:
            print(f"❌ Errore: {res['error']}")
        else:
            print("✅ Conoscenza archiviata con successo nel Vault.")
    else:
        print(f"Comando '{cmd}' non riconosciuto. Usa 'query' o 'ingest'.")
