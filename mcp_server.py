import asyncio
import os
import sys
import json
import httpx
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
from typing import Any, Dict, List, Optional

# Configurazione Bridge
API_BASE_URL = "http://127.0.0.1:8001"
VAULT_KEY = "vault_secret_aura_2026"

class NeuralVaultMCPBridge:
    def __init__(self):
        self.server = Server("neuralvault")
        self._register_tools()

    def _register_tools(self):
        @self.server.list_tools()
        async def handle_list_tools() -> list[Tool]:
            return [
                Tool(
                    name="search_vault",
                    description="Cerca nel NeuralVault personale. Utile per recuperare conoscenze tecniche, appunti o fatti salvati dall'utente.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "La domanda o i termini di ricerca"},
                            "k": {"type": "integer", "description": "Numero di risultati da restituire", "default": 5}
                        },
                        "required": ["query"]
                    }
                ),
                Tool(
                    name="ingest_knowledge",
                    description="Aggiunge nuova conoscenza al NeuralVault. Usa questo strumento quando l'utente ti chiede di ricordare qualcosa.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "content": {"type": "string", "description": "Il testo da salvare"},
                            "source": {"type": "string", "description": "La fonte (es. 'Conversazione Claude')", "default": "mcp_bridge"}
                        },
                        "required": ["content"]
                    }
                ),
                Tool(
                    name="get_wiki_summary",
                    description="Genera una sintesi enciclopedica su un argomento basandosi sulla conoscenza locale.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "topic": {"type": "string", "description": "L'argomento della Wiki"}
                        },
                        "required": ["topic"]
                    }
                ),
                Tool(
                    name="get_vault_status",
                    description="Ritorna statistiche sullo stato di salute e dimensione del NeuralVault.",
                    inputSchema={"type": "object", "properties": {}}
                )
            ]

        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: dict | None) -> list[TextContent]:
            headers = {"X-API-KEY": VAULT_KEY}
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                try:
                    if name == "search_vault":
                        query = arguments.get("query")
                        k = arguments.get("k", 5)
                        payload = {"query": query, "top_k": k, "modality": "text"}
                        resp = await client.post(f"{API_BASE_URL}/api/chat", json=payload, headers=headers)
                        resp.raise_for_status()
                        
                        data = resp.json()
                        response_text = data.get("response", "Nessun risultato trovato.")
                        # Estraiamo le fonti se presenti
                        sources = data.get("context_used", [])
                        source_info = "\n\nFonti:\n" + "\n".join([f"- {s[:200]}..." for s in sources]) if sources else ""
                        
                        return [TextContent(type="text", text=f"{response_text}{source_info}")]

                    elif name == "ingest_knowledge":
                        content = arguments.get("content")
                        source = arguments.get("source", "mcp_bridge")
                        payload = {"text": content, "metadata": {"source": source, "agent": "MCP_Bridge"}}
                        resp = await client.post(f"{API_BASE_URL}/api/ingest", json=payload, headers=headers)
                        resp.raise_for_status()
                        return [TextContent(type="text", text=f"✅ Conoscenza archiviata con successo nel Vault.")]

                    elif name == "get_wiki_summary":
                        topic = arguments.get("topic")
                        payload = {"topic": topic}
                        resp = await client.post(f"{API_BASE_URL}/api/wiki/generate", json=payload, headers=headers)
                        resp.raise_for_status()
                        wiki_text = resp.json().get("markdown", "Errore nella generazione Wiki.")
                        return [TextContent(type="text", text=wiki_text)]

                    elif name == "get_vault_status":
                        resp = await client.get(f"{API_BASE_URL}/api/debug/stats", headers=headers)
                        resp.raise_for_status()
                        stats = resp.json()
                        return [TextContent(type="text", text=f"📊 Status Vault:\n{json.dumps(stats, indent=2)}")]

                except httpx.ConnectError:
                    return [TextContent(type="text", text="❌ Errore: Impossibile connettersi a NeuralVault. Assicurati che api.py sia in esecuzione sulla porta 8001.")]
                except Exception as e:
                    return [TextContent(type="text", text=f"❌ Errore durante la chiamata API: {str(e)}")]

            return [TextContent(type="text", text=f"Tool {name} non riconosciuto.")]

    async def run(self):
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )

if __name__ == "__main__":
    bridge = NeuralVaultMCPBridge()
    asyncio.run(bridge.run())
