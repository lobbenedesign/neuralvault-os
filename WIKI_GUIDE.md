# 📖 Sovereign Wiki: Persistent Truth (v9.1)

Benvenuto nel manuale operativo del **NeuralVault Sovereign Wiki**. Questa estensione trasforma il tuo database vettoriale in una enciclopedia persistente, sicura e interconnessa.

---

## 🚀 1. Come Generare e Archiviare Conoscenza

La Wiki v9.1 non è più solo dinamica; ogni pagina generata viene "cristallizzata" come **Source of Truth**.

1.  **Generazione**: Inserisci un argomento nella dashboard. Il sistema estrarrà i dati dal Vault e comporrà un file Markdown canonico.
2.  **Persistenza**: Tutti i file sono salvati fisicamente in `vault_data/wiki/`. Puoi aprirli con Obsidian, VS Code o qualsiasi editor Markdown.
3.  **Namespace (Cartelle)**: Organizza la conoscenza in cartelle logiche (es. `General/`, `Research/`, `Agents/`) per mantenere ordine nel Vault.

---

## 🛡️ 2. Sovereign Redactor (Sicurezza)

Per proteggere la tua privacy, la Wiki v9.1 integra un sistema di redazione automatica pre-salvataggio:
*   **Auto-Sanitize**: API Key, password, token e email vengono oscurati (`[REDACTED]`) prima che il file tocchi il disco.
*   **Safety First**: Puoi esportare la tua Wiki senza temere leak accidentali di credenziali presenti nei tuoi documenti originali.

---

## 🔄 3. Agent Session Sync (Cursor & Claude)

Puoi alimentare la Wiki con il lavoro svolto da agenti esterni:
*   **Sync**: Il sistema può ingerire le cronologie di sessione di **Cursor** e i log di **Claude Code**.
*   **Agent Intelligence**: Queste sessioni vengono trasformate in pagine Wiki che documentano l'evoluzione del tuo codice e le decisioni architettoniche prese.

---

## 🔌 4. Integrazione AI (llms.txt & MCP)

La Wiki è progettata per essere letta da altre AI:
*   **llms.txt**: Un unico endpoint (`/api/wiki/llms.txt`) che aggrega tutta la tua Wiki in un formato ottimizzato per gli LLM esterni.
*   **MCP 2.0**: Usa il protocollo **Model Context Protocol** per permettere a Claude o Cursor di listare, leggere e aggiornare la tua Wiki autonomamente.

---

## 🌌 5. Epistemic HUD & Provenance

Nella visualizzazione Wiki della dashboard troverai due nuovi strumenti critici:
*   **Causal Graph**: Un mini-grafo interattivo che mappa le relazioni logiche della pagina.
*   **Provenance**: La lista esatta dei documenti originali (PDF, Link, Note) usati per ogni affermazione, con link cliccabili per il deep-dive.

---

> [!IMPORTANT]
> Tutte le modifiche fatte manualmente ai file in `vault_data/wiki/` verranno preservate. NeuralVault riconosce i file esistenti e li usa come base per le future riflessioni critiche.
