# 🏺 SOVEREIGN SKILLS: AGENT INTEGRATION GUIDE
**Connetti la tua AI preferita al cervello di NeuralVault**

NeuralVault v6.0.1 non è un'isola. È un **Global Knowledge Layer** progettato per potenziare ogni agente AI con cui lavori. Questa guida spiega come integrare il Vault con i principali assistenti di coding e agenti autonomi.

---

## ⚡ 1. Il Ponte Universale: `nv-link.py`
Nella cartella `integrations/` trovi lo script `nv-link.py`. È il connettore universale che permette a qualsiasi software di parlare con il Vault tramite l'API locale (porta 8001).

**Comandi base:**
- `python3 integrations/nv-link.py query "Cosa sai del progetto X?"`
- `python3 integrations/nv-link.py ingest "Salva questa nuova regola di stile"`

---

## 🤖 2. Google Antigravity Integration
Antigravity è progettato per essere il "partner neurale" di NeuralVault.
- **Configurazione**: Antigravity legge automaticamente i file `.md` nella sua cartella di sistema.
- **Utilizzo**: Chiedi ad Antigravity: *"Usa lo script nv-link per cercare nel Vault i miei appunti su H-RAG"*. Lui eseguirà il comando e userà la risposta per contestualizzare la sessione di coding.

---

## 🎭 3. Claude Code (Anthropic CLI)
L'agente CLI di Anthropic può usare NeuralVault come una memoria esterna persistente.
- **Integrazione**: Quando avvii `claude` nel terminale, puoi passargli il contesto del Vault.
- **Workflow**: 
  1. Esegui `python3 integrations/nv-link.py query "Refactoring GraphRAG" > context.txt`
  2. Avvia Claude: `claude "Aiutami con il refactoring usando questo contesto: $(cat context.txt)"`

---

## 💻 4. Codex & Opencode Integration (Nativa)

### 🧩 Codex
Per integrare NeuralVault in Codex:
1.  Carica il file `integrations/codex_vault_plugin.json` nel manager estensioni di Codex.
2.  Ora puoi usare i comandi `neuralvault.query` direttamente dalla command palette.

### 🐚 Opencode
Per attivare il Vault in Opencode:
1.  Nel terminale di Opencode, digita: `source integrations/opencode_init.sh`
2.  Questo attiverà gli alias rapidi `nv-query` e `nv-save` nel tuo workspace.

---

## 🛠️ Requisiti per tutte le integrazioni
Perché il bridge funzioni, devono essere soddisfatte due condizioni:
1.  **Engine Online**: Il file `api.py` deve essere in esecuzione (`python3 api.py`).
2.  **Httpx**: L'ambiente dell'agente deve avere la libreria `httpx` installata (`pip install httpx`).

---
🏺 **NeuralVault: Espandi la tua intelligenza, ovunque tu sia.**
