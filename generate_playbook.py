import os
import json
from datetime import datetime
from vault_sdk import NeuralVaultClient

def generate_graph_report():
    print("🚀 [Synth-Muse] Avvio Generazione Code Playbook (GRAPH_REPORT.md)...")
    client = NeuralVaultClient()
    
    # In a real scenario we could use a custom Kuzu query.
    # For now, let's fetch all nodes via the API and filter them.
    try:
        # Assuming there's a search endpoint we can hit, or we just grab recent nodes
        # If the API has /api/search, let's try an empty query to get everything
        response = client.search_vault("", limit=1000)
    except Exception as e:
        print(f"❌ Error fetching from Vault: {e}")
        return

    nodes = response.get("results", [])
    
    modules = []
    classes = []
    functions = []
    
    for n in nodes:
        t = n.get("metadata", {}).get("type", "")
        if t == "code_module": modules.append(n)
        elif t == "code_class": classes.append(n)
        elif t == "code_function": functions.append(n)

    report = f"# 🪐 NeuralVault Code Playbook (GRAPH_REPORT)\n"
    report += f"*Generato il: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n"
    report += "Questo documento è stato autogenerato dall'Agente SYNTH_MUSE analizzando il NeuralVault.\n\n"
    
    report += "## 📊 Statistiche Architetturali\n"
    report += f"- Moduli tracciati: **{len(modules)}**\n"
    report += f"- Classi identificate: **{len(classes)}**\n"
    report += f"- Funzioni/Metodi registrati: **{len(functions)}**\n\n"
    
    report += "## 🧩 Moduli Principali\n"
    for m in modules:
        meta = m.get("metadata", {})
        report += f"### 📄 `{meta.get('source', m.get('id'))}`\n"
        # Find classes in this module
        mod_id = m.get("id")
        mod_classes = [c for c in classes if c.get("metadata", {}).get("parent_id") == mod_id or mod_id in str(c.get("edges", []))]
        
        if mod_classes:
            report += "  - **Classi contenute:**\n"
            for c in mod_classes:
                report += f"    - `{c.get('metadata', {}).get('name', c.get('id'))}`\n"
        
        report += "\n"
        
    report += "---\n*NeuralVault Graph-Lab Engine*"
    
    with open("GRAPH_REPORT.md", "w", encoding="utf-8") as f:
        f.write(report)
        
    print(f"✅ [Synth-Muse] Code Playbook generato con successo: {os.path.abspath('GRAPH_REPORT.md')}")

if __name__ == "__main__":
    generate_graph_report()
