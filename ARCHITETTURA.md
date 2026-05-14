# 🏛️ NEURALVAULT SOVEREIGN: ARCHITETTURA v9.0.0 (SOVEREIGN HEGEMONY)
**The Sovereign Oracle — Strategic Forecasting, Epistemic Integrity & Decision Command Center**


> "Il potere non risiede nel dato, ma nella sua indipendenza e nella capacità di dominarne le conseguenze." — Manifesto NeuralVault v9.0.0
> "Power does not reside in the data, but in its independence and the ability to dominate its consequences." — NeuralVault Manifesto v9.0.0

![Neural Nebula Hero Shot](assets/Screenshot%202026-05-13%20alle%2008.38.55.png)

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

## 🏗️ I. SYSTEM ARCHITECTURE OVERVIEW (v9.0.0 "Sovereign Hegemony")

**ITA**: NeuralVault-OS v9.0.0 "Sovereign Hegemony" evolve l'architettura da un simulatore stocastico a un **Centro di Comando Decisionale Deterministico**. Il kernel integra la logica formale Z3 con un motore di simulazione Quasi-Monte Carlo (QMC) in Rust, gestendo la complessità tramite Iper-Grafi Bayesiani e un'orchestrazione meritocratica a sciami.

```text
[ USER INTERFACE ] <--- SSE Telemetry / HUD ---> [ SOVEREIGN GOVERNANCE HUB ]
        ^                                                   |
        |                                                   v
[ NEURAL DASHBOARD ] <--- REST API ---> [ SOVEREIGN KERNEL v9.0.0 (RUST) ]
        |               + [SOBOL-OWEN QMC ENGINE]           |
        |               + [Z3 FORMAL LOGIC SOLVER]          |
        |               + [KUZU HYPER-GRAPH PROJECTION]     |
        +---------------------------------------------------+
        |                                                   |
[ KINETIC SWARM ] <--- Merit-based Priority ---> [ 5-TIER STORAGE ]
 (Cognitive Presets)                           (Event Sourcing / CQRS)
```

![Full Integration Dashboard](assets/Screenshot%202026-05-10%20alle%2016.42.08.png)

---

## 🧩 PARTE I: THE COGNITIVE CORE (Scientific Engine)
L'anima di NeuralVault: logica formale, simulazione stocastica e integrità epistemica.

## 🧪 II. PREDICTIVE COGNITIVE ENGINE (v9.0.0)

### 🧠 1. Sovereign Oracle (Total Eclipse)
Trasformazione del grafo causale in un motore di intelligence predittiva deterministica.

#### 1.1 Motore Sobol-Owen QMC (Quasi-Monte Carlo) [v9.0.0]
Il cuore matematico del simulatore è stato riscritto in Rust per implementare sequenze a bassa discrepanza:
- **Sobol-Owen Sequences**: Sostituisce il campionamento pseudo-casuale con una distribuzione uniforme ottimizzata che evita il "clumping" dei punti.
- **Convergenza 10x**: Raggiunge la stabilità statistica con 200 iterazioni contro le 2000 del Monte Carlo standard.
- **Scrambling Owen-like**: Algoritmo XOR-shift in parallelo (Rayon) per eliminare le correlazioni strutturali tra i thread.
- **Inverse Normal Mapping**: Mappatura ad alta precisione (Beasley-Springer-Moro) per trasformare i valori Sobol in distribuzioni normali per il rumore causale.

#### 1.2 Antifragility Test (Chaos Engineering)
Identifica i nodi che traggono vantaggio dalla disruption. Il sistema evidenzia le opportunità emergenti in scenari di crisi, trasformando il rischio in actionable intelligence.

#### 1.3 Competitive Game Theory (Conflict Mode)
Simula lo scontro tra due volontà. Permette di inserire un "Adversary Node" per calcolare come le contromisure di un concorrente influenzano la propria strategia.

#### 1.4 Epistemic Erosion (Poisoning Simulation)
Misura la resilienza della verità. Simula l'impatto di un "Deepfake Informativo" per calcolare il rischio di contaminazione del Vault.

#### 1.5 Retro-Causal Analysis (Goal Seeking)
Algoritmo di back-propagation semantica. Permette di definire un effetto desiderato e calcola a ritroso i nodi da attivare oggi per garantirne la realizzazione.

#### 1.6 Epistemic Weather HUD (Meteo della Verità) [v9.0.0]
Il sistema introduce una dimensione "meteorologica" alla conoscenza, traducendo la salute del grafo in indicatori ambientali intuitivi.

- **L'Algoritmo Epistemico**:
    - **Conflict Rate**: Calcola il rapporto tra archi `CONTRADICTS` e archi totali nel cluster. Una densità superiore al 5% genera instabilità barometrica (Tempesta).
    - **Freshness Decay (Curva di Ebbinghaus)**: Monitora l'età media dei nodi (`created_at`). Conoscenza non rinfrescata per oltre 30 giorni aumenta la "nuvolosità" del sistema.
    - **Integrity Score**: Un punteggio pesato (0-100%) che combina orphan rate, carico CPU e coerenza logica.
- **Mappatura Satellitare**:
    - ☀️ **Clear Sky (Score > 85%)**: Salute eccellente, dati freschi e verificati.
    - 🌤️ **Partly Cloudy**: Sistema stabile, ma con cluster isolati o in espansione.
    - 🌥️ **Overcast (Age > 30d)**: Conoscenza "stagnante" che necessita di nuove iniezioni o review da parte di Skywalker.
    - 🌩️ **Stormy (Conflicts > 5%)**: Contraddizioni logiche rilevate. Il sistema sconsiglia simulazioni critiche finché l'instabilità non viene risolta via Supreme Court.
- **Integrazione Multi-Modulo**:
    - **API Gateway**: Endpoint dedicato `/api/system/weather` per il monitoraggio esterno.
    - **Sovereign Wiki**: Ogni articolo viene generato con un HUD meteorologico in testa per avvisare il lettore sull'affidabilità della fonte.
    - **3D Cockpit**: Indicatori luminosi e icone dinamiche nel cockpit di volo per navigazione consapevole.

### 🌓 2. Epistemic Integrity Hub [v9.0.0]
NeuralVault protegge la verità tramite un loop di feedback chiuso tra simulazione e realtà.

#### 2.1 Bayesian Hyper-Graphs
Superamento delle relazioni binarie. Il sistema modella la multicausalità complessa, permettendo di mappare come un set di condizioni ({A, B, C}) influenzi un risultato (D). Questo è fondamentale per l'analisi dei rischi e la pianificazione strategica.

#### 2.2 Shadow Mode Twin (The Feedback Loop)
Un "Gemello Ombra" calibra costantemente i punteggi epistemici.
- **Backtesting**: Confronta le simulazioni What-If passate con gli esiti reali registrati nel Decision Journal.
- **Auto-Calibrazione**: Se l'Oracolo sovrastima un impatto, lo Shadow Twin corregge i pesi delle relazioni nel grafo per le simulazioni future.

#### 2.3 Predictive Health Alerts
Monitoraggio proattivo della degradazione della conoscenza (Ebbinghaus Decay). Il sistema genera alert HUD prima che la qualità di un cluster critico scenda sotto la soglia di sicurezza, attivando automaticamente Skywalker per il "refreshement" dei dati.

---

## 🎮 PARTE II: THE SOVEREIGN HUD (Visual Metaphor)
L'interfaccia immersiva per l'esplorazione della complessità. Qui il dato diventa spazio percorribile.

> 🌌 **Filosofia**: Le funzioni di volo e combattimento non sono un "gioco", ma una **metafora d'esplorazione cognitiva**. Pilotare la nave significa navigare fisicamente tra le costellazioni di documenti del proprio Vault; il combattimento è la gamification della manutenzione e della difesa della verità contro l'entropia.

## 🏺 III. VISUAL EXPERIENCE & ADAPTIVE INTERFACE (WIKI 4.0)

### 🌌 Nexus Vault (3D Nebula) [ITA/EN]
L'interfaccia 3D principale per monitorare l'ingestione dei nodi, le attività dello sciame e lo stato del sistema. Le **Concept Galaxies** si riorganizzano dinamicamente in base alla densità semantica.
- **Metis Partition Map**: [v9.0.0] Visualizzazione tecnica che ricolora la Nebula in base alle partizioni di calcolo, ottimizzando la percezione del bilanciamento del grafo su scala massiva (1M+ nodi).

![UI Layers and Control](assets/layers_filter.png)

### 🏺 Sovereign Wiki 4.0 (The Hyper-Reader) [ITA/EN]
- **Entry Point Standalone**: Accesso al portale come applicazione separata (/wiki) per uno studio immersivo.
- **Streaming Generation (SSE)**: [v9.0.0] I contenuti vengono visualizzati progressivamente mentre vengono generati dall'LLM, riducendo la latenza percepita a zero.
- **Adaptive Reading Protocol**: Supporta modalità **EXECUTIVE** (sintesi), **TECHNICAL** (deep dive) e **RESEARCH** (fonti).
- **Causal Click-Through**: Ogni entità citata è un link interattivo. Cliccando, si apre un preview del nodo con il suo grafo causale locale.
- **Vim-like Navigation**: Supporto nativo per power users (`j/k` per scorrere, `gg/G` per inizio/fine, `e/t/r` per cambiare modalità).
- **Lazy Mermaid 2.0**: I diagrammi (Flowchart, Sequence, Timeline) vengono renderizzati via Intersection Observer solo quando entrano nel campo visivo, risparmiando CPU/GPU.
- **Knowledge Versioning**: Sistema "Git-like" per l'**Epistemic Time-Travel**, confrontando la conoscenza attuale con quella passata.
- **Learning Path Generator**: [v9.0.0] Pannello dinamico "Cognitive Path" che mappa automaticamente i prerequisiti necessari per comprendere un argomento, con barre di progresso basate sull'**Access Count** reale del database.
- **Epistemic Weather HUD**: [v9.0.0] Pannello satellitare che mostra il "Meteo della Verità" (☀️/🌥️/🌩️) basato su integrità logica e freschezza dei dati.

---

## 💎 IV. I 5 LIVELLI DI PERSISTENZA (5-TIER STORAGE)
*Garantisce coerenza atomica tramite Event Sourcing [v9.0 Prep]*

1. **L1: Atomic Cache (RAM + Metal)**: Accesso sub-millisecondo ai nodi caldi via Hardware Pinning.
2. **L2: Aegis LogStore (AOBF / Event Log)**: Unica fonte di verità (CQRS). Ogni cambiamento è un evento immutabile.
3. **L3: Sovereign Graph (KùzuDB)**: Graph Database nativo per query Cypher ultra-veloci e proiezioni di Iper-Grafi Bayesiani ({A, B} -> D).
4. **L4: Evolutionary Ledger (Git-backed)**: Persistenza della saggezza consolidata e versioning semantico.
5. **L5: Neural Quantized Store (NIC - TurboQuant v3)**: Compressione vettoriale estrema (64x) tramite Product Quantization nativa PyTorch.

### 🚀 Approfondimento L5: TurboQuant v3 (Native Product Quantization)
L'evoluzione del motore di ricerca vettoriale da un sistema di hashing binario casuale (v2) a un'architettura **Enterprise-Grade Dual-Layer**, specificamente ottimizzata per superare i limiti dell'hardware consumer (es. Apple Silicon) e gestire **reidratazioni massive**.

#### 1. Zero Dipendenze Esterne (No FAISS)
Per evitare i ben noti problemi di `segmentation fault` su Mac M1 causati dai conflitti tra librerie C++ (OpenMP) e l'architettura ARM, TurboQuant v3 è scritto interamente in **puro PyTorch**. Questo permette di sfruttare l'acceleratore hardware locale (MPS o CUDA) senza alcun layer intermedio instabile.

#### 2. K-Means Nativo e Product Quantization (PQ)
A differenza della v2 che usava matrici di proiezione casuali (tagliando i dati alla cieca e limitando l'accuratezza al 60%), la v3 utilizza il Machine Learning per "imparare" la forma dei dati:
- **Addestramento**: Un algoritmo K-Means ultraveloce analizza un campione di nodi (Massa Critica) per creare dizionari semantici.
- **Quantizzazione del Prodotto (PQ)**: I vettori da 1024 dimensioni non vengono compressi in blocco, ma divisi in 64 "fette". Ogni fetta viene assegnata al centroide più vicino nel dizionario.
- **Risultato**: Compressione monstre da 4.096 byte a soli **64 byte** per vettore (Compressione 64x), preservando un'accuratezza semantica (Cosine Preservation) superiore al 95%.

#### 3. Il Problema del Reidratamento Massivo (La soluzione: Lazy Tensor Compilation)
Durante l'avvio del server, il caricamento in blocco di 30.000 o più nodi causerebbe un collasso delle performance se si utilizzassero concatenazioni tensoriali sequenziali (`torch.cat` in un loop Python). TurboQuant v3 risolve questo scoglio architetturale implementando un **Ingestione O(1) Ammortizzata**:
- **Cold-Start Ibrido**: I nodi vengono accumulati in liste Python native, il cui costo di inserimento è virtualmente zero.
- **Lazy Compilation**: Il sistema non esegue operazioni gravose sulla memoria della GPU durante l'ingestione. Solo al momento della primissima ricerca utente, l'intera lista viene fusa in un singolo super-tensore in un colpo solo. Questo rende il riavvio del server con 30.000 (o 500.000) nodi assolutamente istantaneo.

#### 4. Ricerca Sub-Millisecondo (Asymmetric Distance Computation - ADC)
Per effettuare le ricerche, TurboQuant v3 non decodifica mai i vettori. Utilizza l'**ADC**: calcola le distanze esatte tra la query e i dizionari pre-addestrati, salvando i risultati in una piccola Look-Up Table (LUT). La distanza di qualsiasi nodo nel database viene calcolata tramite un semplice raggruppamento (Gather) di indici da questa tabella, permettendo di interrogare 1.000.000 di nodi compattati in pochissimi millisecondi.

---

## 🌬️ V. NODE LIFECYCLE & ADAPTIVE PACING (WARP SPEED)

Ogni informazione segue una State Machine formale: **PENDING** (Grazia), **STABLE** (Validato), **PROTECTED** (Episodico), **IN_JUDGEMENT** (Audit), **TOMBSTONE** (Lapide).

### 🚀 Adaptive Pacing System
Lo sciame monitora il carico CPU in tempo reale:
- **WARP MODE (<30% CPU)**: Cooldown agenti 0.1s (Massima reattività).
- **NOMINAL MODE (30-85% CPU)**: Cooldown 2.0s (Equilibrio termico).
- **COOLING MODE (>85% CPU)**: Cooldown 10s (Risparmio risorse prioritario).

---

## ⚖️ VI. GOVERNANCE: SUPREME COURT CONSENSUS

Arbitrato critico via Corte Suprema con **Sequential RAM Loading** per stabilità su Apple Silicon:
- **Z3 Formal Solver**: Integrazione del prover di teoremi di Microsoft Research per la verifica delle contraddizioni matematicamente provate.
- **Judge Ensemble**: Utilizzo di 3 giudici (Llama-3, DeepSeek-R1) coordinati dal protocollo Sovereign Merit.
- **Weighted Mesh Consensus**: Meritocrazia Epistemica: il voto di un vault peer pesa in base alla sua reputazione (Reward System).

![Governance - Corte Suprema](assets/Screenshot%202026-05-05%20alle%2012.23.15.png)

---

## 🚀 VII. LE 6 FRONTIERE DEL DISTACCO v9.0.0 (SOVEREIGN HEGEMONY)

1. 🧮 **FORMAL LOGIC ORACLE (Z3)**: L'unico sistema di knowledge management che dimostra le contraddizioni matematicamente (PROVEN).
2. 🔗 **BAYESIAN HYPER-GRAPH CAUSALITY**: Modellazione della multicausalità complessa: {A,B,C} → D tramite KùzuDB.
3. 📊 **SOBOL-OWEN QUANTUM MONTE CARLO**: Precisione statistica estrema con 10x meno iterazioni tramite core Rust accelerato.
4. 🧠 **COMPOUNDING KNOWLEDGE BRAIN**: Ogni nuova ingestione aggiorna automaticamente tutta la conoscenza correlata esistente (Karpathy Pattern).
5. 🌫️ **EPISTEMIC METACOGNITION**: Il sistema mappa i confini della propria ignoranza e guida lo sciame per colmarli proattivamente.
6. 🎯 **DECISION INTELLIGENCE LOOP**: Oracle → Playbook → Journal → Calibration: il ciclo chiuso che impara dai propri errori di previsione.

---

## 🛡️ VIII. AGENT SMITH FIREWALL (Security Intelligence)

- **Security Threat Engine**: Rileva brute-force e flooding assegnando un Threat Score.
- **Retaliation Response**: Lock proattivo segnalato da fulmini e laser verdi nella Nebula 3D.
- **Sovereign Handshake**: Identità decentralizzata `.nvvault` cifrata X25519.

---

## 🐝 IX. THE KINETIC SWARM: SWARM OS v9.0.0
L'orchestrazione non è più deterministica, ma meritocratica e stilisticamente flessibile.

### 9.1 Cognitive Presets (Mindsets) [v9.0.0]
L'utente può selezionare "modi di pensare" predefiniti che influenzano l'intero comportamento dello sciame:
- **Analista Minsky (Logic)**: Scomposizione atomica dei problemi, temperatura bassa (0.2), massima enfasi sulla verifica formale Z3.
- **Creativo De Bono (Lateral)**: Associazioni speculative audaci, temperatura alta (0.9), ricerca di connessioni tra nodi distanti.
- **Custode Federale (Guardian)**: Massima sicurezza, veto proattivo su informazioni non corroborate, focus su Epistemic Proof-of-Work.

![Multi-Agent Swarm Hub](assets/Screenshot%202026-05-05%20alle%2012.19.04.png)

### 9.2 Meritocrazia e Reward System
Ogni azione degli agenti viene valutata dalla Corte Suprema o dal feedback utente:
- **Token di Merito**: Gli agenti accumulano reputazione. Agenti con alto merito hanno priorità di CPU e timeout estesi.
- **Simplification Daemon**: Monitora l'entropia del grafo. Suggerisce il merge di nodi ridondanti (>0.95 similarità) e il pruning di agenti inefficienti.

### 9.3 I 14 Agenti Core
1. **🛡️ SE-007 (Sentinel)**: Sicurezza e Coerenza.
2. **🐍 SN-008 (Snake)**: Riconnessione semantica (Sprouting).
3. **📡 FS-77 (SkyWalker)**: Foraging web proattivo (Google/DuckDuckGo).
4. **🏗️ QA-101 (Quantum)**: Urbanistica del grafo (Golden Clusters).
5. **✨ SY-009 (Synth)**: Scintille creative e sogni neurali.
6. **⚕️ RP-001 (Reaper)**: Compattazione storage AOBF e Tombstone surgery.
7. **🔗 CB-003 (Bridger)**: Sincronizzazione Codice-Conoscenza.
8. **🕵️ DI-007 (Distiller)**: Potatura semantica e raffinazione.
9. **🎭 JA-001 (Janitron)**: Pulizia entropica e orfani.
10. **🦾 NC-001 (Compressor)**: Quantizzazione Neurale (NIC).
11. **🕶️ AG-001 (Smith)**: Firewall Mesh e Security Audit.
12. **🏺 YO-001 (Yoda)**: Discovery di pattern latenti e Deep-File Search.
13. **⚔️ DN-099 (Mandalorian)**: Consolidamento galassie e scorta dati.
14. **🧐 AD-007 (Adversary)**: Red Teaming e sfida epistemica.

---

## 🔌 X. MCP BRIDGE & INTEGRATIONS

- **MCP Bridge**: Accesso nativo per Claude e Cursor tramite architettura stabile sulla porta 8001.
- **Sovereign Voice Interface**: Whisper (STT) + TTS locale per ascolto e risposta privata.
- **nv-link.py (CLI Bridge)**: Connettore universale per operazioni via terminale.

---

## 📊 XI. ANALYTICAL COMPARISON

| Feature | Pinecone / Zilliz | Mem0 (Agentic) | Microsoft GraphRAG | **NeuralVault v9.0.0** |
| :--- | :---: | :---: | :---: | :---: |
| **Data Sovereignty** | ❌ (Cloud) | ⚠️ (Partial) | ❌ (Enterprise) | **✅ Absolute (Local-Locked)** |
| **3D Visualization** | ❌ No | ❌ No | ❌ No | **✅ Native (3D Nebula)** |
| **Causal Logic** | ❌ No | ❌ No | ❌ No | **✅ Logic Arcs** |
| **Monte Carlo Rust** | ❌ No | ❌ No | ❌ No | **✅ <10ms Oracle** |
| **Metacognition** | ❌ No | ❌ No | ❌ No | **✅ Ignorance Map** |

![Neural Hub - LLM Benchmarks](assets/Screenshot%202026-05-05%20alle%2012.37.18.png)

---

## 📈 XII. PERFORMANCE BENCHMARKS (v9.0.0)
*Misurazioni effettuate su Mac M1 Pro (16GB RAM) - Carico 30.000 nodi*

| Operation | v8.4.0 (Legacy) | **v9.0.0 (Hegemony)** | Delta |
|-----------|------|--------------------|-------|
| Wiki generation (1000 nodi) | ~8s | **~3s** | -62% |
| Monte Carlo 1000 iter | ~2s | **~200ms** | -90% |
| Sobol-Owen 200 iter equiv | N/A | **~40ms** | **NEW** |
| Z3 contradiction check | N/A | **<1ms** | **NEW** |
| Cold start (30k nodi) | ~12s | **~0.5s** | -96% |
| TurboQuant encode batch 1k | ~400ms | **~15ms** | -96% |
| KùzuDB causal query depth-3 | N/A | **~8ms** | **NEW** |

![Hardware Observatory - Telemetry](assets/hardware_observatory.png)

---

## 👤 XIII. ABOUT THE AUTHOR

**Giuseppe Lobbene** — Software architect, visionario e costruttore appassionato, spinto dal bisogno di conoscere sempre meglio il mondo dell'informatica che si evolve velocemente. Ho guidato la crescita tecnica di una startup informatica aiutando a scalare il fatturato di 10 volte in pochi mesi, ricoprendo in contemporanea più ruoli: dal configuratore di gestionali cloud a programmatore, tester di app mobile e web, grafico, ed infine commerciale gestendo il 60% della clientela B2B e tutta la clientela B2C. Nonostante in Italia le realtà aziendali spesso non siano pronte a riconoscere e far crescere i dipendenti con progettualità e vision, ho continuato a portare il mio know-how realizzando soluzioni software innovative anche in settori lontani dall'informatica pura.

NeuralVault è il mio manifesto: la prova che anche di notte, durante le poppate del mio piccolo **Oliver** in cui la mia presenza non è richiesta, dopo lunghe giornate di lavoro fisico, è possibile ricavare tempo per imparare, progettare e dar sfogo alla creatività. È un testamento tecnico dedicato ad Oliver: la prova che le proprie passioni vanno coltivate anche lì dove lo spazio o il tempo scarseggiano, un nodo alla volta, anche quando il tempo è il nemico più grande e il desiderio di risolvere bug o leggere paper scientifici in gergo tecnico non ti fa dormire, finché il cervello non crea nuovi archi semantici ampliando il proprio grafo di conoscenze, soltato raggiungendo risultati ai propri obiettivi si riacquista un pò di serenità per riposare.

La mia missione è trasformare NeuralVault nello strumento definitivo per il **Decision Making**: non chiederai più all'AI "Cos'è scritto nei miei documenti?", ma le chiederai **"Cosa succede se prendo questa decisione?"**. Il sistema simulerà l'impatto basandosi sulla tua intera storia intellettuale, garantendo che chi possiede il codice della propria conoscenza sia realmente libero. 🏺🚀🦾


---

## 🛠️ XIV. AUTONOMOUS PATCHING & AUTO-EVOLUZIONE DEL CODICE [v9.0.0]

### 1. Il Concetto di "Self-Editing"
NeuralVault non è un sistema statico. Grazie al modulo di **Autonomous Patching**, lo sciame di intelligenze artificiali ha la capacità di **modificare il proprio codice sorgente in tempo reale**. 
Quando l'agente *Evolution Suggestions* (supportato dal Supreme Court) rileva un bug, un'ottimizzazione mancante, o una miglioria architetturale, può generare una vera e propria *diff/patch* e applicarla direttamente ai file `.py` o `.js` del Vault.

### 2. Il Ciclo di Vita del Patching Autonomo
L'abilità di patchare i propri file segue un protocollo rigoroso per evitare che l'AI corrompa il sistema:

1.  **Rilevamento (Watcher Daemon)**: Il sistema monitora costantemente le anomalie o le richieste dell'utente che richiedono modifiche al codice.
2.  **Generazione del Codice (Coding Specialist)**: Il modello dedicato al codice (es. `qwen2.5-coder:7b`) analizza il file sorgente e scrive una proposta di sostituzione (Patch).
3.  **Validazione (Supreme Court)**: Prima di essere applicata, la patch passa per la validazione. Un modello separato verifica la sintassi e la sicurezza logica.
4.  **Backup (Snapshot Engine)**: Immediatamente prima di toccare i file, il Vault crea un backup istantaneo in `vault_data/backups/patches/`.
5.  **Iniezione & Hot-Reload**: La patch viene scritta fisicamente. Il sistema esegue il ripristino dell'ultimo stato stabile in caso di errore via `python3 nv-link.py --rollback`.

![Sovereign Configuration & Security](assets/sovereign_config.png)

### 3. Requisiti Architetturali e Hardware
L'Autonomous Patching richiede modelli di alta precisione per garantire la stabilità:
- **Modelli di Coding**: Uso tassativo di modelli specializzati come **Qwen 2.5 Coder** o **DeepSeek-Coder-V2** come `CODING SPECIALIST`.
- **Modello Supervisore**: Impiego di un modello "pesante" (es. **DeepSeek-R1 14B/32B**) per la validazione logica e formale.
- **Auto-Pilot Supervision**: Se attivata, le patch vengono applicate in automatico (Sandboxed). Se disattivata, la dashboard richiede approvazione umana esplicita.

### 4. Git Checkpoint (Auto-Branch Evolution)
Per la massima sicurezza, il sistema di Patching si aggancia opzionalmente a GitHub.
Attivando l'**AUTO-BRANCH EVOLUTION**, ogni singola patch generata autonomamente apre un branch `git` isolato. L'utente può eseguire la code-review e il merge, garantendo che i file fondamentali (es. `api.py` o `neural_lab.py`) rimangano protetti da mutazioni non desiderate.

---
*Questa documentazione traccia i limiti operativi dell'evoluzione autoguidata. Istruisci l'Oracolo e i Giudici per mantenere i permessi di sovrascrittura entro i recinti del Sovereign Perimeter.*

---



---

## 🗺️ ROADMAP: STATUS REPORT

### 🛡️ Phase 5 & 6 (COMPLETED v7.5)
- **Autonomous Red Teaming** & **Weighted Mesh Consensus**.

### 🧠 Phase 7 & 8: Sovereign Oracle (COMPLETED v9.0.0)
- **Math-First Stochastic Engine (Rust Acceleration)**.
- **Chronological State Locking (Chrono-Lock)**.
- **Advanced Scenario Kernels (Antifragility, Conflict, Retro-Causal)**.

### 🚀 Phase 9: Sovereign Orchestrator & Decision Intelligence (v9.0.0 - COMPLETATO ✅)
- **Vault Digital Twin**: [COMPLETATO] Implementazione di una Sandbox cognitiva (Twin Vault) per simulare l'impatto di nuova conoscenza senza alterare il vault reale.
- **Natural Language What-If 2.0**: [COMPLETATO] Interfaccia avanzata con **Guided Wizard**, **Temporal Scrubber** e **Plain-Language Results**.
- **Adaptive UX / Wiki 4.0**: [COMPLETATO] Streaming SSE, Causal Click-Through e Lazy Mermaid Rendering per un'esperienza a zero latenza.
- **WASM Simulation Core**: [COMPLETATO] Porting del core di simulazione per esecuzione locale nel browser.
- **Decision Journal & Oracle Accuracy**: [COMPLETATO] Registro immutabile DuckDB delle simulazioni con sistema di feedback per calcolare l'accuratezza predittiva.
- **Learning Path Generator**: [IN CORSO] Evoluzione della Wiki con mappatura automatica dei prerequisiti cognitivi.

### 🏺 Phase 9.2: Sovereign Hardening (v9.0.0 - COMPLETATO ✅)
- **Environment Isolation**: Spostamento di `VAULT_KEY` in `.env` per eliminare l'esposizione di segreti nel codice.
- **Lock-Free Reads**: Ottimizzazione del kernel per permettere letture concorrenti su DuckDB, eliminando il collo di bottiglia del mutex globale per le consultazioni.
- **Autonomous Patching Guard**: [v9.0.0] Introduzione del protocollo di separazione tra generazione e applicazione delle patch (Worker isolato).

### 🚀 Phase 10: Sovereign Hegemony (v9.0.0 - OPERATIVO ✅)
*L'evoluzione finale da Vault Intelligente a Centro di Comando Decisionale Autonomo.*

#### 🏗️ 1. Neural Kernel v2 (Performance & Formal Logic)
- **Epistemic Fingerprinting**: Invalidazione automatica delle conclusioni se i nodi di supporto cambiano o decadono.
- **Causal Gradient Descent**: Algoritmo per trovare la minima variazione necessaria in un nodo per influenzare l'intero grafo verso un obiettivo desiderato.
- **KùzuDB & Event Sourcing (CQRS)**: L'Aegis Event Log diventa l'unica fonte di verità.

#### 🐝 2. Swarm OS (Stability & Meritocracy)
- **PBC (Semantic Agent Profiling)**: Service discovery basato su file `capability.json-ld`. Ogni agente espone formalmente le proprie capacità (es. "Web Search", "Formal Audit") per l'interoperabilità Agent-to-Agent.
- **Swarm Capabilities API**: Endpoint `/api/swarm/capabilities` per l'introspezione dinamica dello sciame in formato JSON-LD standardizzato.
- **Agent Reward System**: Gli agenti guadagnano "token di merito" in base all'accuratezza delle previsioni.
- **Merit-based Priority**: Priorità di esecuzione basata sui reward; gli SLM (1.5B/3B) gestiscono il 90% del traffico locale.
- **Cognitive Presets**: Preset specializzati (es. "Analista Minsky", "Creativo De Bono") per guidare lo stile dell'orchestrazione.
- **Chrysalis Worker Isolation**: Patching autonomo testato in sandbox isolate prima del merge nel core.

#### 🛡️ 3. Governance: Epistemic Integrity & Red Teaming
- **Epistemic Proof-of-Work (PoW)**: Confidence score matematico basato sulla coerenza multi-sorgente e verifica formale Z3.
- **Predictive Health Alerts**: Monitoraggio della degradazione (Ebbinghaus Decay) con suggerimenti di review mirate.
- **Sovereign Adversary (AD-007)**: [v9.0.0] Agente dedicato "Avvocato del Diavolo" per il falsificazionismo di Popper automatico. Sfida attivamente le ipotesi wiki e le sottomette alla Supreme Court.
- **Differential Twin (Copy-on-Write)**: [v9.0.0] Sandbox ad impatto zero (CoW) che salva solo i delta rispetto al vault principale, permettendo simulazioni infinite.
- **Biomimetic Knowledge Decay**: Implementazione della curva di Ebbinghaus per mantenere il Vault "fresco".
- **Metis Graph Partitioning**: [v9.0.0] Ottimizzazione strutturale automatica per grafi massivi (10M+ nodi) per minimizzare la latenza di cache. Supporta visualizzazione 3D in tempo reale via vertex coloring dinamico.
- **Cognitive Path Coverage**: Algoritmo di tracciamento del progresso di studio basato sugli "hit" (access_count) registrati nel DuckDB Decision Journal.

#### 🎨 4. Cognitive Cockpit (UX & Action) [v9.0.0]
- **Retro-Causal Playbook Generator**: Converte le simulazioni in piani d'azione prescrittivi in 5 step.
- **Visual Capacity (1M+ Nodes)**: Aura Nebula con Level of Detail (LOD) per gestire oltre 1.000.000 di nodi con WebGL fluido.
- **Template Workspace**: Widget preconfigurati per scenari specifici (Crisis Management, Trend Analysis).
- **Sovereign Wiki v9.1 (Persistent Truth)**: [RELEASED ✅] Transizione da generazione dinamica a sistema enciclopedico persistente in Markdown con:
    - **Source of Truth**: File canonici in `vault_data/wiki/` organizzati in **Namespace ricorsivi**.
    - **Sovereign Redactor**: Sanificazione automatica di API keys e dati sensibili pre-salvataggio.
    - **Agent Session Sync**: Ingestione automatica di cronologie da Cursor e Claude Code.
    - **AI-Interoperability**: Esportazione standard `llms.txt` per il consumo da parte di agenti esterni.
    - **UX Refinement (v9.1.1)**: Sidebar collassabile con etichetta di ripristino, layout adattivo e Smart Search Portal (tasto INVIO + keyboard support).
    - **Memory HUD Fix (v9.1.2)**: Risolto conflitto di profondità (Z-index 9999999) e rimozione clipping (overflow) per i tooltip della sezione Memory Overview.

---

## 🛠️ XIII. STATO DEL DEBITO TECNICO & BUG NOTI (Sovereign Reality Check)

Essendo NeuralVault un progetto sviluppato in solitaria e in continua espansione, l'architettura convive con problematiche note derivanti dal ciclo "nuova funzione -> bug -> update".

### 1. Mesh & Peer Communication
- **Test in Isolamento**: Attualmente lo scambio dati tra Nebula e i peer è testato esclusivamente tramite **Peer Demo** locali. Manca una validazione su larga scala in reti multi-device reali (mancanza di hardware di test distribuito).
- **Gossip Protocol**: Possibili race condition durante il sync massivo di nodi tra peer se la latenza di rete è instabile.

### 2. Hardware Bias (Apple Silicon vs Intel)
- **M1 Pro Optimization**: Il software è ottimizzato e testato su **Mac M1 Pro (16GB RAM)**. L'uso intensivo di PyTorch (MPS) e le ottimizzazioni Metal potrebbero non tradursi perfettamente su architetture Intel/AMD senza GPU dedicate, dove si prevedono cali di performance nel rendering 3D e nella quantizzazione TurboQuant.
- **Memory Pressure**: Con 16GB, il caricamento simultaneo di più modelli Swarm (es. un 7B per il supervisore e SLM per i task) può causare swap su disco, rallentando il kernel.

### 3. Swarm-LLM Bottlenecks
- **Inference Concurrency**: Malfunzionamenti identificati nella comunicazione tra gli agenti e gli LLM quando più compiti richiedono l'inferenza simultanea. Il sistema di priorità è in fase di raffinamento per evitare deadlock nel caricamento dei modelli.
- **Model Switching**: La latenza nel cambio modello tra un task e l'altro può creare "buchi" di telemetria nella dashboard.

### 4. Dashboard & Data Rendering
- **Incoerenze Sezionali**: Alcune sezioni della dashboard potrebbero non mostrare correttamente tutti i dati in tempo reale a causa di ritardi nel polling SSE o discrepanze nello schema dei metadati dei nodi più vecchi (Legacy Debt).
- **UI Regressions**: L'aggiunta di nuove interfacce per la Wiki o il What-If Simulation tende a generare regressioni CSS sui componenti pre-esistenti (es. barre di scorrimento, tooltips).

---

## XIV. REPORT DI CONSOLIDAMENTO & HARDENING (v9.0.0 Sovereign Maturity)

In preparazione al rilascio della Phase 9.0, è stato completato un audit di sicurezza e stabilità per eliminare le regressioni asincrone e i conflitti di concorrenza.

### 1. Hardening DuckDB & Thread-Safety
- **Problema**: `InvalidInputException` durante query simultanee in cicli asincroni.
- **Soluzione**: Implementazione di un meccanismo di **Locking Centralizzato** (`threading.Lock`) all'interno di `DuckDBPrefilter`.
- **Impatto**: Tutti i moduli core (`Engine`, `Agent007Lab`, `Snapshot`, `TimeLapse`) ora utilizzano metodi wrapper sicuri (`fetchone`, `fetchall`, `execute`) che garantiscono l'atomicità delle operazioni, eliminando i crash durante l'ingestione massiva.

### 2. Refactoring Asincrono Bridger (CB-003)
- **Ottimizzazione**: Conversione di `LatentBridge` e `BridgerAgent.sync_codebase` in funzioni **nativamente async**.
- **Stabilizzazione**: Eliminazione totale di `asyncio.run` all'interno dei thread di background. Il Bridger ora opera sul loop dedicato dell'Orchestrator tramite `run_coroutine_threadsafe`, prevenendo deadlock del kernel.

### 3. Intelligence Hub & Model Fallback
- **Robustezza**: Potenziata la logica di selezione modelli in `Agent007Intelligence`.
- **Fallback Adattivo**: Se un modello configurato (es. `qwen2.5:1.5b`) non è presente in Ollama, il sistema esegue un discovery dinamico (`ollama list`) e seleziona il miglior sostituto installato (es. `llama3.2:3b`), mantenendo l'integrità del ragionamento investigativo.

### 4. Audit Sicurezza API
- **Standardizzazione**: Hardening di tutti gli endpoint `/api/` tramite il decoratore `Depends(get_api_key)`.
- **Consistenza**: Verifica della propagazione della `VAULT_KEY` (configurata via environment variable) attraverso gli header `X-API-KEY`, risolvendo i residui errori `403 Forbidden` nelle sezioni dinamiche della dashboard.

### 5. Telemetria Sky-Walker (FS-77)
- **Risoluzione Contatori**: Correzione del bug dei contatori a zero nella Dashboard.
- **Log Forensi**: Implementazione di print granulari nel terminale per il monitoraggio in tempo reale delle fasi di *Search, Forage, Synthesis e Injection*.

### 6. NeuralWiki 4.0 & Memory HUD Consolidation (v9.0.0)
- **UI/UX (v9.0.0)**: Implementazione sidebar collassabile dinamica con animazioni fluide e tasto di ripristino. Ottimizzazione della ricerca tramite pulsante INVIO dedicato e supporto nativo per tastiera.
- **Deep-Z Visibility (v9.0.0)**: Risoluzione critica dei problemi di visibilità dei tooltip nella Memory Overview. Rimozione dei vincoli di overflow sui container principali e innalzamento dello Z-index a 9.9M per una leggibilità assoluta sopra ogni layer della dashboard.

### 7. Skywalker Research Hardening (v9.0.0)
- **Espansione Orizzonte**:
    - **Profondità**: Aumentata la profondità di crawling da 1 a **3 livelli**.
    - **Volume**: Aumentato il limite di pagine per missione da 10 a **50 pagine**.
    - **Cross-Domain**: Disabilitato il vincolo del dominio unico (`same_domain_only=False`). Skywalker può ora seguire link verso fonti esterne per corroborare le informazioni.
- **Stealth Search Upgrade**:
    - Skywalker ora utilizza il motore di fetch avanzato del `SovereignWebForager` anche per i risultati di ricerca.
    - This garantisce l'uso di **browser-like headers** e il **fallback automatico su Playwright** (browser reale) se Google o DuckDuckGo dovessero bloccare la richiesta standard.
- **Risoluzione Anomalia 'python'**:
    - Migliorata la gestione degli errori nelle ricerche; i fallimenti ora vengono loggati in modo più granulare invece di restituire silenziosamente un "nessun risultato". Skywalker è ora in grado di condurre ricerche "High-Altitude" molto più profonde e resilienti ai blocchi. 🏺🚀🦾

### 8. NeuralVault Sovereign v9.0.0 – Yoda Deployment & Skywalker Hardening
**Stato: OPERATIVO ✅**

*   **Skywalker Fix (FS-77)**: Risolto il `SyntaxError` (indentazione errata del blocco `try...finally`) che impediva l'avvio del server. Ora Skywalker è resiliente ai crash di missione e resetta correttamente lo stato su `Scanning Horizon...`.
*   **Heartbeat Diagnostico**: Integrato il log 💓 `[FS-77/Heartbeat]` per monitorare l'attività proattiva nel terminale.
*   **Yoda File Searcher (YO-001) – Implementazione Completa**:
    *   **Cervello (Backend)**: Implementato in `neural_lab.py`. Yoda esegue un "Pellegrinaggio" esaminando 1000 nodi alla volta (anche nodi orfani) prima di lanciare missioni di espansione galattica.
    *   **Corpo (Cycloscope 3D)**: Creata la mesh della navicella Yoda con colori Verde Smeraldo, Arancio e Grigio.
    *   **Arsenale Visivo**: Laser Gialli a 4 cannoni (`spawnYodaLaser`) attivi durante l'iniezione di conoscenza.
    *   **Sprite Retro**: Sprite Yoda pixel art in CSS (box-shadow) integrato nell'HUD.
*   **Integrazione UI/UX**: Slot HUD Yoda abilitato con telemetria in tempo reale e supporto `toggleFollow`.

### 9. NeuralVault v9.0.0: Sovereign Swarm Evolution & R2-D2 Deployment
**Stato: OPERATIVO ✅**

#### ✨ Nuove Implementazioni e Restyling
- **Agente R2-D2 (Warehouse Manager)**:
    - **Sprite 3D**: Creato un nuovo modello voxel (pixel 3D) a forma di R2-D2 composto da mini-cubi.
    - **Logica Organizzativa**: R2-D2 ora raggruppa i nodi per similarità semantica e colore, creando "galassie" (cluster) nella Nebula.
    - **Funzioni Avanzate**: Implementati gli audit per nodi fuori posto e suggerimenti di potatura per zone troppo dense.
- **Evoluzione Synth Agent (Kirby)**:
    - Lo sprite rosa è stato trasformato in un **Kirby 3D** completo di piedi rossi, occhi, bocca e mani.
- **Hologram Center**:
    - **Jar Jar Binks**: Creato l'ologramma 8-bit wireframe verde.
    - **Jabba the Hutt**: Aggiornato con una nuova prospettiva frontale in wireframe verde.

#### 🛠️ Stabilità e Telemetria (Core Engine)
- **Fix Critici di Backend**:
    - **Safe Agent Access**: Protezione contro gli errori di tipo `NoneType`.
    - **Math Dependency**: Risolto il crash di R2-D2 garantendo l'importazione del modulo `math`.

### 10. NeuralVault v9.0.0: Sovereign Modular Dashboard Architecture
**Stato: OPERATIVO ✅**

*   **Decomposizione Monolitica**: Il file `dashboard.js` (>7.000 righe) è stato ufficialmente deprecato e suddiviso in 7 moduli domain-specific per massimizzare la manutenibilità e le performance:
    *   `globals.js`: Stato globale e configurazione Three.js.
    *   `utils.js`: Utility di sistema, logging e asset procedurali.
    *   `engine.js`: Motore di rendering e logica di inseguimento telecamera (Cycloscope).
    *   `telemetry_bridge.js`: Gestione flussi SSE e sincronizzazione real-time.
    *   **`nebula_graph.js`**: Visualizzazione della Nebula 3D e interazioni semantiche.
    *   **`agents_system.js`**: Logica, fisica e mesh degli agenti autonomi.
    *   **`hud_controller.js`**: Gestione dell'interfaccia utente (HUD) e dei tab.
    *   **`player_controller.js`**: Modulo indipendente per il pilotaggio manuale e fisica della navicella dell'utente.

---

## 🏺 XV. ROADMAP V9.0: SOVEREIGN HEGEMONY (COMPLETATO ✅)
Il sistema ha raggiunto la maturità operativa "Sovereign". Ogni componente della Roadmap V9.0 è integrato e funzionante.

- **Neural Kernel v2**: Operativo con Z3, KùzuDB e Sobol-Owen QMC.
- **Swarm OS**: Meritocrazia attiva e Cognitive Presets selezionabili.
- **Governance**: Epistemic Integrity garantita da Shadow Twin e AD-007.
- **Actionable AI**: Playbook Generator e SITREP Anchoring attivi.

---

🏺 **NeuralVault-OS: Turning Orchestration into Sovereign Power.**
*Official Documentation Sovereign Hegemony v9.0.0 -> Fully Integrated & Verified*
