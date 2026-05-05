# 🏛️ NEURALVAULT SOVEREIGN: ARCHITETTURA v6.0.1
**Sovereign Agentic RAG & Modular Intelligence Ecosystem**

> "Il potere non risiede nel dato, ma nella sua indipendenza." — Manifesto NeuralVault

---

## 🚀 QUICK START (INSTANT BOOT)

```bash
# 1. Clone & Setup
git clone https://github.com/giuseppelobbene/neuralvault && cd neuralvault
python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt

# 2. Avvio Sovereign Engine
python3 api.py

# 3. Neural Dashboard -> http://127.0.0.1:8001
```

---

## 🏗️ SYSTEM ARCHITECTURE OVERVIEW

```text
[ USER INTERFACE ] <--- SSE Telemetry ---> [ AGENT SMITH FIREWALL ]
        ^                                           |
        |                                           v
[ NEURAL DASHBOARD ] <--- REST API ---> [ SOVEREIGN KERNEL (v6.0) ]
        |                                           |
        +-------------------------------------------+
        |                                           |
[ KINETIC SWARM ] <--- Neural Event Bus ---> [ 4-TIER STORAGE ]
 (Janitor, Synth, etc.)                    (RAM, AOBF, DuckDB, LMDB)
```

---

## 💎 I. I 4 LIVELLI DI PERSISTENZA (4-TIER)

Il sistema opera su quattro livelli di astrazione sincronizzati per velocità e resilienza:

1.  **L1: Atomic Cache (RAM + Metal)**: Accesso sub-millisecondo ai nodi caldi via **Hardware Pinning**.
2.  **L2: Aegis LogStore (AOBF)**: Storage binario append-only con **Tombstone Paradox** per il rollback istantaneo e **Merkle Integrity** contro il Bit-Rot.
3.  **L3: Contextual Archive (DuckDB)**: Motore relazionale per metadati e Knowledge Timeline con **Two-Stage TurboSearch**.
4.  **L4: Evolutionary Ledger (Git-backed)**: Persistenza della saggezza consolidata e versioning semantico.

---

## ⚙️ II. NODE LIFECYCLE & ADAPTIVE PACING

Ogni informazione segue una State Machine formale: PENDING (Grazia), STABLE (Validato), PROTECTED (Episodico), IN_JUDGEMENT (Audit), TOMBSTONE (Lapide).

### 🌬️ Adaptive Pacing (Warp Speed System)
Lo sciame monitora il carico CPU in tempo reale per non interferire con il lavoro dell'utente:
- **WARP MODE (<30% CPU)**: Cooldown agenti 0.1s (Massima reattività).
- **NOMINAL MODE (30-85% CPU)**: Cooldown 2.0s (Equilibrio termico).
- **COOLING MODE (>85% CPU)**: Cooldown 10s (Risparmio risorse prioritario).

---

## ⚖️ III. GOVERNANCE: SUPREME COURT CONSENSUS (v6.0.1)

Arbitrato critico via Corte Suprema con **Sequential RAM Loading** per stabilità su Mac M1:
- **Judge 1 (Fast-Track)**: `llama3.2:3b`. Se certo al 100%, verdetto istantaneo.
- **Judge 2 (Prosecutor)** & **Judge 3 (Defender)**: Modelli pesanti (`deepseek-r1:8b`) chiamati solo in caso di dubbio.
- **Arbitrator**: Sintetizza la verità finale eliminando le allucinazioni.

---

## 🌌 IV. HIERARCHICAL GRAPHRAG (H-RAG) & CONCEPT GALAXIES

Il sistema organizza gerarchicamente la conoscenza per gestire 100.000+ nodi.
- **Hybrid Clustering Engine**: Combina BFS/Leiden con il fallback **K-Means** vettoriale per unire anche i nodi orfani.
- **Deep Hydration Protocol**: Fetch profondo dal Kernel Aegis (L2) se DuckDB è vuoto, garantendo riassunti perfetti.
- **RECLUSTER**: Crea le Galassie semantiche.
- **SUMMARIZE**: L'AI spiega il contenuto di ogni galassia per una ricerca 10x più veloce.

---

## 🛡️ V. AGENT SMITH FIREWALL (v8.0 Security Intelligence)

L'agente **AG-001 (SMITH)** è una flotta di difesa autonoma.
- **Security Threat Engine**: Rileva brute-force e flooding assegnando un Threat Score.
- **Retaliation Response**: Al raggiungimento della soglia critica, scatta il **Lock di 45s** segnalato da fulmini e laser verdi nella Nebula 3D.
- **Sovereign Handshake**: Identità decentralizzata `.nvvault` cifrata X25519.

---

## 🐝 VI. THE KINETIC SWARM: I 9 AGENTI CORE

1. **🛡️ SE-007 (Sentinel)**: Sicurezza e Coerenza.
2. **🐍 SN-008 (Snake)**: Riconnessione semantica (Sprouting).
3. **📡 FS-77 (SkyWalker)**: Foraging web proattivo (CRAG).
4. **🏗️ QA-101 (Quantum)**: Urbanistica del grafo (Golden Clusters).
5. **✨ SY-009 (Synth)**: Scintille creative e sogni neurali.
6. **⚕️ RP-001 (Reaper)**: Compattazione storage AOBF.
7. **🔗 CB-003 (Bridger)**: Sincronizzazione Codice-Conoscenza.
8. **🕵️ DI-007 (Distiller)**: Potatura semantica e raffinazione.
9. **🎭 JA-001 (Janitron)**: Pulizia entropica e orfani.

---

## 🎙️ VII. SOVEREIGN VOICE & TIME DRIVE (v5.1)

- **Sovereign Voice Interface**: Whisper (STT) + TTS locale. Il Vault ascolta e risponde privatamente.
- **Neural Time Drive**: Slider UI per l'esplorazione storica della Nebula nel tempo.

---

## 📊 VIII. ANALYTICAL COMPARISON & BRUTAL HONESTY

| Feature | Pinecone / Zilliz | Mem0 (Agentic) | Microsoft GraphRAG | **NeuralVault v6.0.1** |
| :--- | :---: | :---: | :---: | :---: |
| **Data Sovereignty** | ❌ (Cloud Only) | ⚠️ (Cloud/Local) | ❌ (Enterprise) | **✅ Absolute (Local-Locked)** |
| **Offline Capacity** | ❌ No (Requires Net) | ❌ No | ⚠️ Partial | **✅ 100% Air-Gapped** |
| **3D Visualization** | ❌ No (API/Admin) | ❌ No | ❌ No (CLI/Lib) | **✅ Native (3D Nebula)** |
| **Agentic Swarm** | ❌ No | ⚠️ Basic | ❌ No | **✅ 9 Kinetic Agents** |
| **Hierarchical RAG** | ❌ No | ❌ No | ✅ Yes (Python) | **✅ Native (H-RAG)** |
| **Multimodal Integration**| ⚠️ Vector Storage | ❌ No | ❌ No | **✅ Voice/Image Engine** |
| **Consensus Governance** | ❌ No | ❌ No | ❌ No | **✅ Supreme Court (3-LLM)** |
| **Setup Complexity** | **✅ Zero (API Key)** | ✅ Low | ⚠️ Medium | **❌ High (Kernel Build)** |
| **UX / Ease of Use** | **✅ High (SaaS)** | ✅ Medium | ❌ Low (Library) | **⚠️ Medium (Local Dash)** |
| **Scalability (Billions)** | **✅ Unlimited (Cloud)**| ⚠️ High | ✅ High | **❌ Limited (Local RAM)** |
| **Infrastructure Cost** | ❌ High (Monthly) | ⚠️ Tiered | ⚠️ Token Heavy | **✅ 0 (Local Hardware)** |
| **Privacy (GDPR/HIPAA)** | ⚠️ Compliant | ⚠️ Dependent | ⚠️ Enterprise | **✅ Beyond Compliance** |

---

## 🔌 IX. MCP BRIDGE (Model Context Protocol)

Il supporto MCP è uno dei "ponti" più potenti della v6.0.1. Permette a modelli esterni (come Anthropic Claude o OpenAI) di "entrare" nel tuo Vault e usarlo come fonte di conoscenza sovrana.

### 🧠 Come funziona: Il Sovereign Bridge
Il file `mcp_server.py` agisce come un interprete universale. A differenza dei sistemi standard, NeuralVault utilizza un'architettura **"API Bridge"**:
- **Stabilità Totale**: Il server MCP non tenta di aprire direttamente il database (evitando conflitti di lock con DuckDB), ma "parla" con l'API già attiva sulla porta 8001.
- **Leggerezza**: Non carica modelli pesanti in RAM, ma sfrutta l'intelligenza dello sciame già operativo nella dashboard.
- **Sincronizzazione**: Usa la stessa memoria e lo stesso stato della tua sessione attiva.

### 📱 App Compatibili
- **Claude Desktop**: L'integrazione principale per trasformare Claude in un esperto del tuo Vault.
- **Cursor**: L'editor AI che può indicizzare la tua documentazione locale tramite MCP.
- **Zed**: Editor ultra-veloce con supporto nativo al protocollo.

### 🚀 Configurazione Claude Desktop (Step-by-Step)
1.  Apri la configurazione: `~/Library/Application Support/Claude/claude_desktop_config.json`
2.  Incolla il bridge (assicurati che il percorso del venv sia corretto):
```json
{
  "mcpServers": {
    "neuralvault": {
      "command": "/Users/giuseppelobbene/Downloads/DATABASE VETTORIALE/venv/bin/python3",
      "args": ["/Users/giuseppelobbene/Downloads/DATABASE VETTORIALE/mcp_server.py"]
    }
  }
}
```
3.  **Riavvia Claude Desktop**. Vedrai l'icona del collegamento attivo. Ora puoi chiedere: *"Cerca nel mio Vault cosa abbiamo deciso per l'H-RAG"* e Claude risponderà usando i tuoi dati locali.

> **Nota di Sicurezza**: Assicurati che `api.py` sia in esecuzione. Il bridge richiede la dashboard attiva per garantire risposte in tempo reale e coerenza dei dati.

---

## 🌐 X. MULTI-AGENT ECOSYSTEM & INTEGRATIONS

NeuralVault v6.0.1 è progettato per essere una risorsa globale, pronta a potenziare qualsiasi AI Agent tu decida di utilizzare. La cartella `integrations/` contiene gli strumenti necessari per questa simbiosi.

### 🛠️ I Componenti della Cartella `integrations/`
- **`nv-link.py` (Universal CLI Bridge)**: È il connettore universale. Permette a qualsiasi AI (o utente tramite terminale) di interrogare (`query`) o nutrire (`ingest`) il Vault con un singolo comando Python. È il "sistema nervoso" che connette il Vault all'esterno.
- **`SOVEREIGN_SKILLS.md` (Integration Guide)**: La guida definitiva che spiega come "insegnare" alle AI esterne ad attingere alla tua banca della conoscenza. Include istruzioni specifiche per Antigravity, Claude Code e altri.
- **`codex_vault_plugin.json` (Codex Manifest)**: Un file di configurazione pronto all'uso che trasforma NeuralVault in un'estensione nativa per l'editor Codex, abilitando comandi di ricerca direttamente nell'interfaccia.
- **`opencode_init.sh` (Opencode Startup Script)**: Uno script di innesco per Opencode che configura istantaneamente gli alias `nv-query` e `nv-save`, rendendo la memoria neurale parte integrante del workflow di sviluppo.

### 🛡️ Visione: Infrastruttura di Conoscenza Sovrana
Grazie a questi strumenti, il tuo Vault non è più solo un archivio, ma una **Sovereign Knowledge Infrastructure**. Può essere consultato simultaneamente dalla dashboard 3D, da Claude Desktop via MCP e da Antigravity tramite il bridge globale, garantendo che ogni tua intuizione sia disponibile ovunque tu stia costruendo.

---

## 🚀 ROADMAP v6.1: THE SOVEREIGN EVOLUTION - PHASE 2

1.  **📦 Zero-Click Installer (.dmg)**: [PRIORITÀ #1] Installazione nativa Apple-Style con Python e Ollama pre-configurati.
2.  **🧠 RAM-Aware Dispatcher**: Selezione dinamica del modello (Tiny vs Reasoning) in base alla RAM libera sul Mac.
3.  **🌌 H-RAG Level 2 (Meta-Galaxies)**: Clustering ricorsivo per milioni di nodi.
4.  **🦀 Rust Core Migration**: Spostamento delle routine di calcolo del grafo in Rust per performance 10x.
5.  **⚓ nv-mesh:// Native Protocol**: Registrazione handler macOS per link mesh cliccabili.

---

## 👤 About the Author
**Giuseppe Lobbene** — Software architect e costruttore appassionato spinto dal bisogno di conoscere sempre meglio il mondo dell'informatica che si evolve velocemente. Ho guidato la crescita tecnica di una startup informatica aiutando a scalare il fatturato di **10 volte in pochi mesi**, ho ricoperto in contemporanea più ruoli partendo dal semplice configuratore di gestionali in cloud, a programmatore e tester di app mobile e web app, a grafico ed infine anche ruolo di commerciale e gestendo il 60% della clientela B2B ed anche tutta la clientela B2C. Ma in Italia né startup né grandi realtà aziendali sono pronti a riconoscere, istruire e far crescere i dipendenti con progettualità, sicurezze contrattuali ed una buona vision per dar futuro e crescita, quindi ora mi ritrovo a lavorare in un settore lontano dal mondo informatico, ma dentro al quale sono riuscito minimamente a portare il mio piccolo know how realizzando soluzioni software.

**NeuralVault è il mio manifesto**: la prova per me stesso che anche di notte, durante le poppate del mio piccolo Oliver in cui la mia presenza non è richiesta, dopo lunghe giornate di lavoro fisico, è possibile comunque ricavare del tempo per imparare cose nuove, progettare, dar sfogo alla creatività e consolidare i propri sforzi e progetti anche grazie al supporto della AI. È un testamento tecnico dedicato al mio piccolo figlio **Oliver**: la prova che le proprie passioni vanno coltivate anche lì dove lo spazio non c'è, un nodo alla volta, anche quando il tempo è il nemico più grande e quel desiderio di buttarsi a capofitto su un progetto, sul risolvere dei bug che non ci fanno dormire, o quel bisogno di leggere e rileggere dei paper scientifici scritti a volte in gergo tecnico troppo lontani da noi finché non diventano parole più sensate, più chiare e finché il nostro cervello non inizia a creare nuovi archi semantici ampliando il nostro grafo di conoscenze. 🏺

---

# 🏺 NeuralVault [ITA]: Manifesto Tecnico

## 📜 Visione: Il Sistema Operativo Cognitivo
NeuralVault-OS v6.0.1 è un **Modular Agentic RAG** autonomo che trasforma dati grezzi in saggezza sovrana.

## 🏗️ Architettura & Ciclo di Vita
- **4-Tier Persistence**: RAM, Aegis Log, DuckDB, Evolutionary Ledger.
- **Adaptive Pacing**: Lo sciame modula la velocità in base al carico CPU del Mac (WARP/NOMINAL/COOLING).
- **Corte Suprema**: Arbitrato a 3 giudici con protocollo Fast-Track per ottimizzare la RAM.
- **MCP Bridge**: Integrazione nativa con Claude Desktop e Cursor tramite protocollo API Bridge (porta 8001).

## 🐝 Lo Sciame Cinetico (I 9 Agenti)
Un team di 9 agenti autonomi (Sentinel, Snake, SkyWalker, Quantum, Synth, Reaper, Bridger, Distiller, Janitron) che gestisce la crescita, la potatura e la coerenza della Nebula 3D in tempo reale.

## 🌌 H-RAG & Concept Galaxies
Il cuore della v6.0.1: raggruppamento semantico ibrido e sintesi automatica delle galassie per una ricerca gerarchica ultra-precisa.

## 🛡️ Agent Smith Firewall
Protezione attiva contro minacce esterne con ritorsione automatica e blocco di sicurezza di 45 secondi.

## 🌐 Ecosistema Multi-Agente
Integrazione universale tramite la cartella `integrations/`. NeuralVault funge da memoria esterna per **Claude Code**, **Antigravity**, **Codex** e **Opencode**, permettendo una simbiosi tra diversi assistenti AI basata sulla tua conoscenza locale.

---
🏺 **NeuralVault-OS: Turning Information into Active Wisdom.**
*Documentazione Ufficiale Sovereign Maturity v6.0.1*