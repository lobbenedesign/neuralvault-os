# 🏛️ NEURALVAULT SOVEREIGN: ARCHITETTURA v8.0.1
**The Predictive Cognitive Engine & Modular Intelligence Ecosystem**

> "Il potere non risiede nel dato, ma nella sua indipendenza." — Manifesto NeuralVault
> "Power does not reside in the data, but in its independence." — NeuralVault Manifesto

---

## 🚀 QUICK START (INSTANT BOOT)

```bash
# 1. Clone & Setup
git clone https://github.com/lobbenedesign/NeuralVault-OS.git && cd NeuralVault-OS
python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt

# 2. Avvio Sovereign Engine / Start Engine
python3 api.py

# 3. Neural Dashboard -> http://127.0.0.1:8001
```

---

## 🏗️ I. SYSTEM ARCHITECTURE OVERVIEW (v8.0)

**ITA**: NeuralVault-OS non è un semplice database vettoriale. È un **Sovereign Cognitive Engine** progettato per l'evoluzione autonoma della conoscenza. Con la Release v8.0, NeuralVault compie il salto da archivio passivo a simulatore predittivo: non si limita a ricordare il passato, ma simula scenari "What-If" per prevedere l'impatto di nuove informazioni sulla tua base di conoscenza.

```text
[ USER INTERFACE ] <--- SSE Telemetry ---> [ AGENT SMITH FIREWALL ]
        ^                                           |
        |                                           v
[ NEURAL DASHBOARD ] <--- REST API ---> [ PREDICTIVE KERNEL (v8.0) ]
        |               + [WHAT-IF ENGINE]          |
        |               + [WIKI 3.0 ENGINE]         |
        +-------------------------------------------+
        |                                           |
[ KINETIC SWARM ] <--- Neural Event Bus ---> [ 5-TIER STORAGE ]
  (10 Agents incl. NIC)                    (RAM, AOBF, DuckDB, LMDB, NIC)
```

---

## 🎨 II. VISUAL EXPERIENCE (DASHBOARD & WIKI)

### 🌌 Nexus Vault [ITA/EN]
**ITA**: L'interfaccia 3D principale per monitorare l'ingestione dei nodi, le attività dello sciame e lo stato del sistema.
**EN**: The primary 3D interface to monitor real-time node ingestion, swarm activities, and system health.
![Nexus Vault](assets/Screenshot%202026-05-05%20alle%2012.16.13.png)

### 🏺 Sovereign Wiki 3.0 (Il Portale Dedicato) [ITA/EN]
**ITA**: È il cuore visivo della v8.0. Un'esperienza di lettura e studio professionale.
- **Entry Point Dedicato**: Accesso al portale come applicazione standalone (`/wiki`), separata dalla dashboard operativa.
- **Navigazione Semantica**: Una sidebar intelligente che elenca "Galassie di Concetti" auto-organizzanti.
- **Knowledge Versioning**: Sistema "Git-like" per la conoscenza. Permette l'**Epistemic Time-Travel** per confrontare la comprensione attuale con quella passata.
- **Interactive HUD**: Ogni citazione è un portale verso il nodo originale con visualizzazione 3D locale.

**EN**: The visual heart of v8.0. A professional reading and study experience.
- **Dedicated Entry Point**: Standalone application (`/wiki`) separate from the operational dashboard.
- **Semantic Navigation**: Intelligent sidebar listing self-organizing "Concept Galaxies".
- **Knowledge Versioning**: "Git-like" system for knowledge. Enables **Epistemic Time-Travel** to compare current vs past understanding.
- **Interactive HUD**: Every citation is a portal to the original node with local 3D visualization.

### 📊 Generative Multimedia & HUD [ITA/EN]
**ITA**: La Wiki diventa un documento multimediale generato dinamicamente.
- **Visualizzazione Diagrammi**: Integrazione nativa di **Mermaid.js**. Generazione automatica di Flowcharts, Sequence Diagrams e Timeline Storiche cliccabili.
- **Epistemic Weather HUD**: Pannello laterale che mostra il "Meteo Cognitivo": livello di verifica della mesh, incertezza e mancanze di fonti primarie (Confidence & Freshness).

**EN**: The Wiki becomes a dynamically generated multimedia document.
- **Diagram Visualization**: Native **Mermaid.js** integration. Automatic generation of Flowcharts, Sequence Diagrams, and clickable Historical Timelines.
- **Epistemic Weather HUD**: Side panel showing "Cognitive Weather": mesh verification level, uncertainty, and primary source gaps.

---

## 🧪 III. PREDICTIVE COGNITIVE ENGINE (v8.0)

### 🧪 What-If Engine (Causal Simulation) [ITA/EN]
**ITA**: Trasformazione del grafo causale in un motore di simulazione dinamico.
- **Decision Overlays**: Quando esegui una simulazione "What-If", il sistema evidenzia dinamicamente il testo nella Wiki (verde per impatti positivi, rosso per rischi) basandosi sui nodi influenzati.
- **Motore Bayesiano**: Utilizza inferenza su Reti Bayesiane costruite dal Causal Graph per calcolare probabilità di effetti a cascata.
- **Esempio**: Cambiando il parametro "Budget Marketing", il sistema evidenzia quali obiettivi sono ora a rischio basandosi sulla storia intellettuale salvata.

**EN**: Transformation of the causal graph into a dynamic simulation engine.
- **Decision Overlays**: During a "What-If" simulation, the system dynamically highlights Wiki text (green for positive impact, red for risks) based on affected nodes.
- **Bayesian Engine**: Uses inference on Bayesian Networks built from the Causal Graph to calculate cascade effect probabilities.

---

## 💎 IV. I 5 LIVELLI DI PERSISTENZA / 5-TIER STORAGE (v8.0)

**ITA**: Il sistema opera su cinque livelli di astrazione sincronizzati:
1. **L1: Atomic Cache (RAM + Metal)**: Accesso sub-millisecondo.
2. **L2: Aegis LogStore (AOBF)**: Storage binario append-only con **Merkle Integrity**.
3. **L3: Contextual Archive (DuckDB)**: Motore relazionale per metadati.
4. **L4: Evolutionary Ledger (Git-backed)**: Versioning semantico della conoscenza.
5. **L5: Neural Quantized Store (NIC)**: Embedding compressi fino al 90% via VQ-VAE.

**EN**: The system operates on five synchronized layers:
1. **L1: Atomic Cache (RAM + Metal)**: Sub-millisecond access.
2. **L2: Aegis LogStore (AOBF)**: Append-only binary storage with **Merkle Integrity**.
3. **L3: Contextual Archive (DuckDB)**: Relational engine for metadata.
4. **L4: Evolutionary Ledger (Git-backed)**: Semantic versioning of knowledge.
5. **L5: Neural Quantized Store (NIC)**: Embeddings compressed up to 90% via VQ-VAE.

---

## 🧠 V. NEURAL IMPLICIT COMPRESSION (NIC)

**ITA**: Innovazione per la scalabilità estrema (1M+ nodi).
- **Integrazione nel Kernel**: Il `NeuralImplicitCompressor` è integrato direttamente nel metodo `get_node` del core engine.
- **Ricostruzione On-the-fly**: Il sistema supporta nodi "compressi" (senza vettori grezzi su disco). Se richiesto, il motore utilizza la rete NIC per ricostruire l'embedding istantaneamente.
- **Risultato**: Riduzione dello storage fino al 90% e ricerca velocizzata su hardware limitati (MacBook Air 8GB).

**EN**: Innovation for extreme scalability (1M+ nodes).
- **Kernel Integration**: `NeuralImplicitCompressor` integrated directly into the `get_node` method.
- **On-the-fly Reconstruction**: Supports "compressed" nodes. The NIC network reconstructs embeddings instantly upon request.
- **Result**: Up to 90% storage reduction and faster search on limited hardware.

---

## ⚖️ VI. GOVERNANCE: SUPREME COURT & CONSENSUS

### 🏛️ Supreme Court [ITA/EN]
**ITA**: Arbitrato a 3 giudici con caricamento RAM sequenziale per evitare crash su Mac M1/M2/M3.
**EN**: 3-judge arbitration with sequential RAM loading to prevent crashes on Mac M1/M2/M3.

### 🌌 Weighted Mesh Consensus [ITA/EN]
**ITA**: Meritocrazia Epistemica: il voto di un vault peer pesa in base alla sua densità di prove (Paper, Nodi, Freschezza).
**EN**: Epistemic Meritocracy: a peer vault's vote is weighted by its evidence density (Papers, Nodes, Freshness).

---

## 🛡️ VII. AGENT SMITH FIREWALL

**ITA**: Difesa proattiva con feedback visivo (laser/fulmini) nella Nebula 3D. Monitoraggio costante dell'integrità dei claim.
**EN**: Proactive defense with visual feedback in the 3D Nebula. Constant monitoring of claim integrity.
![Agent Smith Defense](assets/Screenshot%202026-05-05%20alle%2012.19.04.png)

---

## 🐝 VIII. THE KINETIC SWARM: I 10 AGENTI CORE

1. **🛡️ SE-007 (Sentinel)**: Security & Coherence.
2. **🐍 SN-008 (Snake)**: Semantic Sprouting.
3. **📡 FS-77 (SkyWalker)**: Proactive Foraging & Mesh Verification.
4. **🏗️ QA-101 (Quantum)**: Graph Urbanism (Golden Clusters).
5. **✨ SY-009 (Synth)**: Creative Sparks.
6. **⚕️ RP-001 (Reaper)**: AOBF Compression.
7. **🔗 CB-003 (Bridger)**: Code-Knowledge Sync.
8. **🕵️ DI-007 (Distiller)**: Semantic Pruning.
9. **🎭 JA-001 (Janitron)**: Entropic Cleaning.
10. **🦾 NC-001 (Compressor)**: [NEW v8.0] Neural Quantization (NIC).

---

## 🔌 IX. MCP BRIDGE (Model Context Protocol)

**ITA**: Integra modelli esterni (Claude, Cursor) come "ponti" verso il tuo Vault locale.
**EN**: Integrates external models (Claude, Cursor) as "bridges" to your local Vault.

---

## 👤 X. ABOUT THE AUTHOR

**Giuseppe Lobbene** — Software architect e costruttore appassionato.
NeuralVault è un testamento tecnico dedicato a mio figlio **Oliver**: la prova che le proprie passioni vanno coltivate anche lì dove lo spazio non c'è, un nodo alla volta. 🏺

---

## 🗺️ ROADMAP: STATUS REPORT

### 🛡️ Phase 5 & 6 (COMPLETED v7.5)
- **Autonomous Red Teaming** & **Weighted Mesh Consensus**.

### 🧠 Phase 7: Predictive Cognitive Engine (COMPLETED v8.0.1)
- **What-If Engine**, **Neural Wiki 3.0**, **Neural Implicit Compression**.
- **Stabilizzazione HUD** e integrazione NIC nel recupero nodi.

---

🏺 **NeuralVault-OS: Turning Information into Active Wisdom.**
*Official Documentation Sovereign Maturity v8.0.1*