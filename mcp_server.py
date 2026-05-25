import asyncio
import os
import sys
import json
import httpx
try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool, TextContent
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    class Server:
        def __init__(self, *args, **kwargs): pass
        def list_tools(self):
            return lambda f: f
        def call_tool(self):
            return lambda f: f
    class Tool: pass
    class TextContent: pass
    def stdio_server(): pass

from typing import Any, Dict, List, Optional
from pathlib import Path

# [v1.2] Caricamento dinamico configurazione
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Configurazione Bridge
API_BASE_URL = os.getenv("NEURALVAULT_API_URL", "http://127.0.0.1:8001")
VAULT_KEY = os.getenv("NEURAL_VAULT_KEY", "sovereign_vault_alpha_2026_secure_core")

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
                    name="wiki_list",
                    description="Elenca tutte le pagine della Wiki organizzate per Namespace.",
                    inputSchema={"type": "object", "properties": {}}
                ),
                Tool(
                    name="sync_agents",
                    description="Sincronizza le sessioni di agenti esterni (Cursor, Claude) nel Vault.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "provider": {"type": "string", "enum": ["auto", "cursor", "claude"]}
                        }
                    }
                ),
                Tool(
                    name="get_vault_status",
                    description="Ritorna statistiche sullo stato di salute e dimensione del NeuralVault.",
                    inputSchema={"type": "object", "properties": {}}
                ),
                Tool(
                    name="what_if_forecast",
                    description="Esegue un'analisi causale predittiva su uno scenario ipotetico. Ritorna impatti probabilistici e una narrazione strategica.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "Lo scenario da simulare (es. 'Cosa succede se smetto di usare Python?')"},
                            "mode": {"type": "string", "enum": ["FAST", "DEEP"], "default": "FAST"}
                        },
                        "required": ["query"]
                    }
                ),
                Tool(
                    name="track_active_document",
                    description="Registra il file attualmente aperto/attivo sull'editor Cursor/VS Code e ritorna dinamicamente la Wiki o i nodi correlati.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "file_path": {"type": "string", "description": "Il percorso assoluto del file attivo"},
                            "content_preview": {"type": "string", "description": "Un'anteprima o estratto del contenuto del file"}
                        },
                        "required": ["file_path"]
                    }
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

                    elif name == "wiki_list":
                        resp = await client.get(f"{API_BASE_URL}/api/wiki/list", headers=headers)
                        resp.raise_for_status()
                        pages = resp.json().get("pages", [])
                        text = "📚 Pagine Wiki Disponibili:\n" + "\n".join([f"- [{p['namespace']}] {p['title']} ({p['file_name']})" for p in pages])
                        return [TextContent(type="text", text=text)]

                    elif name == "sync_agents":
                        provider = arguments.get("provider", "auto")
                        payload = {"provider": provider}
                        resp = await client.post(f"{API_BASE_URL}/api/sync/agents", json=payload, headers=headers)
                        resp.raise_for_status()
                        count = resp.json().get("synced", 0)
                        return [TextContent(type="text", text=f"🔄 Sincronizzazione {provider} completata: {count} sessioni acquisite.")]

                    elif name == "get_vault_status":
                        resp = await client.get(f"{API_BASE_URL}/api/debug/stats", headers=headers)
                        resp.raise_for_status()
                        stats = resp.json()
                        return [TextContent(type="text", text=f"📊 Status Vault:\n{json.dumps(stats, indent=2)}")]

                    elif name == "what_if_forecast":
                        query = arguments.get("query")
                        mode = arguments.get("mode", "FAST")
                        payload = {"query": query, "mode": mode, "lenses": ["standard"]}
                        resp = await client.post(f"{API_BASE_URL}/api/wiki/simulate/nl", json=payload, headers=headers)
                        resp.raise_for_status()
                        data = resp.json()
                        
                        narrative = data.get("narrative", "Simulazione completata.")
                        grade = data.get("oracle_grade", "B")
                        conf = data.get("overall_confidence", 0.0)
                        
                        return [TextContent(type="text", text=f"🔮 FORECAST (Grade: {grade}, Conf: {conf*100}%)\n\n{narrative}")]

                    elif name == "track_active_document":
                        file_path = arguments.get("file_path")
                        preview = arguments.get("content_preview", "")
                        query_term = os.path.basename(file_path)
                        if preview:
                            query_term += " " + preview[:200]
                        
                        payload = {"query": query_term, "top_k": 3, "modality": "text"}
                        resp = await client.post(f"{API_BASE_URL}/api/chat", json=payload, headers=headers)
                        resp.raise_for_status()
                        
                        data = resp.json()
                        response_text = data.get("response", "Nessun contesto correlato.")
                        
                        hydration_msg = f"💡 [NeuralVault Context Hydration]\nIl file attivo '{os.path.basename(file_path)}' è semanticamente correlato a:\n\n{response_text}"
                        return [TextContent(type="text", text=hydration_msg)]

                except httpx.ConnectError:
                    return [TextContent(type="text", text="❌ Errore: Impossibile connettersi a NeuralVault. Assicurati che api.py sia in esecuzione sulla porta 8001.")]
                except Exception as e:
                    return [TextContent(type="text", text=f"❌ Errore durante la chiamata API: {str(e)}")]

            return [TextContent(type="text", text=f"Tool {name} non riconosciuto.")]

    async def run(self):
        if not MCP_AVAILABLE:
            print("\n❌ [MCP Error] Il pacchetto SDK 'mcp' non è installato in questo ambiente Python.")
            print("Per abilitare il Bridge MCP con Claude Desktop/Cursor, installalo con:")
            print("👉  .venv/bin/pip install mcp")
            sys.exit(1)
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="NeuralVault MCP Bridge / Workspace Utility")
    subparsers = parser.add_subparsers(dest="command")
    
    # Subcommand: mcp-init
    init_parser = subparsers.add_parser("mcp-init", help="Inizializza un nuovo workspace locale di NeuralVault.")
    init_parser.add_argument("directory", type=str, help="La directory da configurare come workspace")
    
    args = parser.parse_args()
    
    if args.command == "mcp-init":
        from pathlib import Path
        target_path = Path(args.directory).resolve()
        target_path.mkdir(parents=True, exist_ok=True)
        
        nv_dir = target_path / ".neuralvault"
        nv_dir.mkdir(exist_ok=True)
        
        config_data = {
            "mcp_port": 8001,
            "api_port": 8000,
            "vault_key": VAULT_KEY,
            "workspace_path": str(target_path)
        }
        
        with open(nv_dir / "config.json", "w") as f:
            json.dump(config_data, f, indent=4)
            
        claudeproj_content = {
            "mcpServers": {
                "neuralvault": {
                    "command": "python3",
                    "args": [os.path.abspath(__file__)],
                    "env": {
                        "NEURALVAULT_API_URL": API_BASE_URL,
                        "NEURAL_VAULT_KEY": VAULT_KEY,
                        "NEURALVAULT_WORKSPACE": str(target_path)
                    }
                }
            }
        }
        with open(target_path / ".claudeproj", "w") as f:
            json.dump(claudeproj_content, f, indent=4)
            
        claude_desktop_cfg = {
            "mcpServers": {
                "neuralvault": {
                    "command": "python3",
                    "args": [os.path.abspath(__file__)],
                    "env": {
                        "NEURALVAULT_API_URL": "http://127.0.0.1:8001",
                        "NEURAL_VAULT_KEY": VAULT_KEY,
                        "NEURALVAULT_WORKSPACE": str(target_path)
                    }
                }
            }
        }
        
        print(f"\n✅ [MCP INIT] Workspace inizializzato in: {target_path}")
        print(f"📂 Creata directory nascosta: {nv_dir}")
        print(f"📄 Creato file di progetto: {target_path / '.claudeproj'}")
        print("\n🖥️ Aggiungi questa configurazione a 'claude_desktop_config.json' per integrare Claude Desktop:")
        print(json.dumps(claude_desktop_cfg, indent=4))
    else:
        bridge = NeuralVaultMCPBridge()
        asyncio.run(bridge.run())
