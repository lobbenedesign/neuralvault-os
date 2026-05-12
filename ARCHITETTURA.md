# 🏛️ NEURALVAULT SOVEREIGN: ARCHITETTURA v8.4.0
**The Sovereign Oracle — Strategic Forecasting, Epistemic Immunity & Decision Command Center**


> "Il potere non risiede nel dato, ma nella sua indipendenza e nella capacità di dominarne le conseguenze." — Manifesto NeuralVault v8.3
> "Power does not reside in the data, but in its independence and the ability to dominate its consequences." — NeuralVault Manifesto v8.3

---

## 🚀 QUICK START (INSTANT BOOT)

\`\`\`bash
# 1. Clone & Setup
git clone https://github.com/lobbenedesign/NeuralVault-OS.git && cd NeuralVault-OS
python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt

# 2. Avvio Sovereign Engine / Start Engine
python3 api.py

# 3. Neural Dashboard -> http://127.0.0.1:8001
\`\`\`

---

## 🏗️ I. SYSTEM ARCHITECTURE OVERVIEW (v8.3 "Total Eclipse")

**ITA**: NeuralVault-OS v8.3 "Total Eclipse" evolve l'architettura da un archivio passivo a un **Simulatore Cognitivo Stocastico Accelerato**. Il sistema non si limita a ricordare il passato, ma simula scenari "What-If" con precisione matematica in Rust, garantendo coerenza cronologica tramite Chrono-Lock e integrando il DNA delle entità reali (E2P).

\`\`\`text
[ USER INTERFACE ] <--- SSE Telemetry ---> [ AGENT SMITH FIREWALL ]
        ^                                           |
        |                                           v
[ NEURAL DASHBOARD ] <--- REST API ---> [ SOVEREIGN KERNEL (v8.3) ]
        |               + [RUST MONTE CARLO]        |
        |               + [CHRONO-LOCK SNAPSHOTS]   |
        |               + [SOVEREIGN ORACLE]        |
        +-------------------------------------------+
        |                                           |
[ KINETIC SWARM ] <--- Neural Event Bus ---> [ 5-TIER STORAGE ]
  (10 Agents incl. NIC)                    (RAM, AOBF, DuckDB, NIC-LRU)
\`\`\`

---

## 🎨 II. VISUAL EXPERIENCE & ADAPTIVE INTERFACE (WIKI 3.0)

### 🌌 Nexus Vault (3D Nebula) [ITA/EN]
L'interfaccia 3D principale per monitorare l'ingestione dei nodi, le attività dello sciame e lo stato del sistema. Le **Concept Galaxies** si riorganizzano dinamicamente in base alla densità semantica.

### 🏺 Sovereign Wiki 4.0 (The Hyper-Reader) [ITA/EN]
- **Entry Point Standalone**: Accesso al portale come applicazione separata (/wiki) per uno studio immersivo.
- **Streaming Generation (SSE)**: [v8.4] I contenuti vengono visualizzati progressivamente mentre vengono generati dall'LLM, riducendo la latenza percepita a zero.
- **Adaptive Reading Protocol**: Supporta modalità **EXECUTIVE** (sintesi), **TECHNICAL** (deep dive) e **RESEARCH** (fonti).
- **Causal Click-Through**: Ogni entità citata è un link interattivo. Cliccando, si apre un preview del nodo con il suo grafo causale locale.
- **Vim-like Navigation**: Supporto nativo per power users (`j/k` per scorrere, `gg/G` per inizio/fine, `e/t/r` per cambiare modalità).
- **Lazy Mermaid 2.0**: I diagrammi (Flowchart, Sequence, Timeline) vengono renderizzati via Intersection Observer solo quando entrano nel campo visivo, risparmiando CPU/GPU.
- **Knowledge Versioning**: Sistema "Git-like" per l'**Epistemic Time-Travel**, confrontando la conoscenza attuale con quella passata.
- **Epistemic Weather HUD**: Pannello laterale che mostra il "Meteo Cognitivo": livello di verifica della mesh, incertezza e mancanze di fonti primarie.


---

## 🧪 III. PREDICTIVE COGNITIVE ENGINE (v8.3)

### 🧠 5. Sovereign Oracle (Total Eclipse)
Trasformazione del grafo causale in un motore di intelligence predittiva deterministica.

#### 5.1 Motore Ibrido Accelerato (Rust/WASM)
- **Adaptive Monte Carlo**: [v8.4] Supporto per modalità **FAST** (100 iterazioni per feedback istantaneo) e **DEEP** (2000 iterazioni per analisi di precisione).
- **Targeted Subgraph Extraction**: Estrazione intelligente dei nodi rilevanti (max 200/500) invece dell'intero grafo, ottimizzando il calcolo su hardware M1.
- **Client-Side Simulation (WASM)**: Porting del motore in WebAssembly per eseguire simulazioni direttamente nel browser del cliente, eliminando la latenza di rete.
- **Noise Injection**: Campionamento gaussiano nativo per gestire l'incertezza del mondo reale.


#### 5.2 Antifragility Test (Chaos Engineering)
Identifica i nodi che traggono vantaggio dalla disruption. Il sistema evidenzia le opportunità emergenti in scenari di crisi, trasformando il rischio in actionable intelligence.

#### 5.3 Competitive Game Theory (Conflict Mode)
Simula lo scontro tra due volontà. Permette di inserire un "Adversary Node" per calcolare come le contromisure di un concorrente influenzano la propria strategia.

#### 5.4 Epistemic Erosion (Poisoning Simulation)
Misura la resilienza della verità. Simula l'impatto di un "Deepfake Informativo" per calcolare il rischio di contaminazione del Vault.

#### 5.5 Retro-Causal Analysis (Goal Seeking)
Algoritmo di back-propagation semantica. Permette di definire un effetto desiderato e calcola a ritroso i nodi da attivare oggi per garantirne la realizzazione.

---

## 💎 IV. I 5 LIVELLI DI PERSISTENZA (5-TIER STORAGE)
*Garantisce coerenza atomica tramite Event Sourcing [v9.0 Prep]*

1. **L1: Atomic Cache (RAM + Metal)**: Accesso sub-millisecondo ai nodi caldi via Hardware Pinning.
2. **L2: Aegis LogStore (AOBF / Event Log)**: Unica fonte di verità. Ogni cambiamento è un evento immutabile con **Tombstone Paradox** per rollback istantaneo e **Merkle Integrity** contro il Bit-Rot.
3. **L3: Contextual Projections (DuckDB / KùzuDB)**: Viste relazionali e grafi proiettati in tempo reale dall'Event Log con **Chrono-Lock Snapshots**.
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
- **Judge Ensemble**: Utilizzo di 3 giudici (Llama-3, DeepSeek-R1) per eliminare bias e allucinazioni.
- **Weighted Mesh Consensus**: Meritocrazia Epistemica: il voto di un vault peer pesa in base alla sua densità di prove (Paper, Nodi, Freschezza).

---

## 🚀 VII. LE 6 FRONTIERE DEL DISTACCO COMPETITIVO

1. **🔥 PROACTIVE WIKI**: Lo sciame anticipa il bisogno di conoscenza, scrivendo documentazione durante il *Neural Dreaming*.
2. **🧠 FLARE**: Active Retrieval During Generation. Il sistema si ferma se la confidenza cala, recupera dati e riprende.
3. **🔗 CAUSAL KNOWLEDGE GRAPH**: Mappatura di relazioni logiche (**CAUSES, PREVENTS, REQUIRES**) invece di semplice similarità.
4. **🌫️ MAPPA DELL'IGNORANZA**: Identifica la "Terra Incognita" del Vault e guida Skywalker per colmare i gap reali.
5. **🛠️ EXECUTABLE WIKI**: Knowledge Cells per eseguire codice o query di verifica (ESERSE) direttamente dagli articoli.
6. **💎 PERSONAL FINE-TUNING**: LoRA 4-bit locale per calibrare il linguaggio del sistema sui tuoi termini tecnici specifici.

---

## 🛡️ VIII. AGENT SMITH FIREWALL (Security Intelligence)

- **Security Threat Engine**: Rileva brute-force e flooding assegnando un Threat Score.
- **Retaliation Response**: Lock proattivo segnalato da fulmini e laser verdi nella Nebula 3D.
- **Sovereign Handshake**: Identità decentralizzata `.nvvault` cifrata X25519.

---

## 🐝 IX. THE KINETIC SWARM: I 10 AGENTI CORE

1. **🛡️ SE-007 (Sentinel)**: Sicurezza e Coerenza.
2. **🐍 SN-008 (Snake)**: Riconnessione semantica (Sprouting).
3. **📡 FS-77 (SkyWalker)**: Foraging web proattivo e verifica mesh.
4. **🏗️ QA-101 (Quantum)**: Urbanistica del grafo (Golden Clusters).
5. **✨ SY-009 (Synth)**: Scintille creative e sogni neurali.
6. **⚕️ RP-001 (Reaper)**: Compattazione storage AOBF.
7. **🔗 CB-003 (Bridger)**: Sincronizzazione Codice-Conoscenza.
8. **🕵️ DI-007 (Distiller)**: Potatura semantica e raffinazione.
9. **🎭 JA-001 (Janitron)**: Pulizia entropica e orfani.
10. **🦾 NC-001 (Compressor)**: Quantizzazione Neurale (NIC).

---

## 🔌 X. MCP BRIDGE & INTEGRATIONS

- **MCP Bridge**: Accesso nativo per Claude e Cursor tramite architettura stabile sulla porta 8001.
- **Sovereign Voice Interface**: Whisper (STT) + TTS locale per ascolto e risposta privata.
- **nv-link.py (CLI Bridge)**: Connettore universale per operazioni via terminale.

---

## 📊 XI. ANALYTICAL COMPARISON

| Feature | Pinecone / Zilliz | Mem0 (Agentic) | Microsoft GraphRAG | **NeuralVault v8.3** |
| :--- | :---: | :---: | :---: | :---: |
| **Data Sovereignty** | ❌ (Cloud) | ⚠️ (Partial) | ❌ (Enterprise) | **✅ Absolute (Local-Locked)** |
| **3D Visualization** | ❌ No | ❌ No | ❌ No | **✅ Native (3D Nebula)** |
| **Causal Logic** | ❌ No | ❌ No | ❌ No | **✅ Logic Arcs** |
| **Monte Carlo Rust** | ❌ No | ❌ No | ❌ No | **✅ <10ms Oracle** |
| **Metacognition** | ❌ No | ❌ No | ❌ No | **✅ Ignorance Map** |

---

## 👤 XII. ABOUT THE AUTHOR

**Giuseppe Lobbene** — Software architect, visionario e costruttore appassionato, spinto dal bisogno di conoscere sempre meglio il mondo dell'informatica che si evolve velocemente. Ho guidato la crescita tecnica di una startup informatica aiutando a scalare il fatturato di 10 volte in pochi mesi, ricoprendo in contemporanea più ruoli: dal configuratore di gestionali cloud a programmatore, tester di app mobile e web, grafico, ed infine commerciale gestendo il 60% della clientela B2B e tutta la clientela B2C. Nonostante in Italia le realtà aziendali spesso non siano pronte a riconoscere e far crescere i dipendenti con progettualità e vision, ho continuato a portare il mio know-how realizzando soluzioni software innovative anche in settori lontani dall'informatica pura.

NeuralVault è il mio manifesto: la prova che anche di notte, durante le poppate del mio piccolo **Oliver** in cui la mia presenza non è richiesta, dopo lunghe giornate di lavoro fisico, è possibile ricavare tempo per imparare, progettare e dar sfogo alla creatività. È un testamento tecnico dedicato ad Oliver: la prova che le proprie passioni vanno coltivate anche lì dove lo spazio o il tempo scarseggiano, un nodo alla volta, anche quando il tempo è il nemico più grande e il desiderio di risolvere bug o leggere paper scientifici in gergo tecnico non ti fa dormire, finché il cervello non crea nuovi archi semantici ampliando il proprio grafo di conoscenze, soltato raggiungendo risultati ai propri obiettivi si riacquista un pò di serenità per riposare.

La mia missione è trasformare NeuralVault nello strumento definitivo per il **Decision Making**: non chiederai più all'AI "Cos'è scritto nei miei documenti?", ma le chiederai **"Cosa succede se prendo questa decisione?"**. Il sistema simulerà l'impatto basandosi sulla tua intera storia intellettuale, garantendo che chi possiede il codice della propria conoscenza sia realmente libero. 🏺🚀🦾


---

## 🏛️ CORE DECISION ENGINE: DETTAGLI OPERATIVI (v8.4)

### 🌓 1. Vault Digital Twin (Il "Gemello Digitale")
- **A cosa serve**: È la tua **Sandbox di Sicurezza**. Immagina di voler aggiungere al tuo Vault un libro o un report che contiene informazioni controverse o molto dense. Invece di "sporcare" subito la tua base di conoscenza permanente, la testi nel Digital Twin.
- **Come opera**: Crea uno snapshot istantaneo di tutti i tuoi nodi e delle tue connessioni in una memoria temporanea (RAM), isolata dal database reale.
- **Come lo usa l'utente**: Carichi un file o incolli un testo dicendo al sistema: *"Simula l'ingestione in modalità Twin"*.
- **Cosa mostra all'utente**:
    - **Mappa degli Impatti**: Ti mostra quali nodi esistenti verrebbero "toccati" o influenzati dalla nuova informazione.
    - **Audit delle Contraddizioni**: Ti avvisa se la nuova informazione nega qualcosa che avevi già validato in precedenza.
    - **Pre-visualizzazione**: Vedi come cambierebbe il tuo grafo 3D prima di confermare l'aggiunta definitiva (Commit).

### 🧪 2. Natural Language What-If (Simulazione Conversazionale)
- **A cosa serve**: Serve a fare **Strategia d'Impatto** tramite linguaggio naturale, eliminando le barriere tecniche tra intenzione e calcolo stocastico.
- **Interactive Causal Sandbox**: [v8.4] Interfaccia drag-and-drop basata su **Cytoscape.js** che permette di manipolare visivamente i nodi del subgrafo, regolare le intensità e vedere i collegamenti causali emergere in tempo reale.
- **Guided What-If Wizard**: Un flusso guidato a 3 step (Azione -> Target -> Intensità) per utenti che preferiscono un approccio strutturato rispetto alla barra di comando libera.
- **Temporal Scrubber**: Uno slider temporale che permette di proiettare i risultati della simulazione a diversi orizzonti: **Immediato**, **Medio Termine (6m)** e **Lungo Termine (1 anno+)**, con algoritmi di decadimento dell'intensità.
- **Plain-Language Results**: [v8.4] Traduzione automatica delle metriche probabilistiche (Mean, Std, Prob+) in un report narrativo strutturato per decision-maker (Esito, Effetti Collaterali, Mitigazione Rischio).
- **Oracle Accuracy**: Sistema di feedback integrato nel Decision Journal per calcolare l'accuratezza predittiva dell'Oracolo nel tempo.


### ⚖️ 3. Perché usarli insieme?
L'utente usa il Digital Twin per proteggere l'integrità del passato (non far entrare "spazzatura" nel Vault) e il What-If per esplorare le possibilità del futuro.

**Esempio d'uso reale:**
1. Ricevi una proposta di investimento complessa.
2. La carichi nel **Digital Twin** per vedere se contraddice i tuoi principi finanziari archiviati.
3. Se il Twin dà il via libera, usi il **NL What-If** per chiedere: *"Se accettassi questa proposta, come cambierebbe la mia esposizione al rischio nel lungo termine?"*.
4. **🛠️ Sovereign Patching Protocol (v9.2.1)**
*Protocollo di Auto-Evoluzione Protetta e Validazione Umana*

## 1. Il Ciclo di Vita della Patch
NeuralVault non si limita a proporre codice; lo forgia in un ambiente isolato prima di sottoporlo all'utente.

1.  **Sandbox Generation**: Le patch vengono scritte e testate in un ambiente sandbox isolato.
2.  **Test Suite Validation**: Solo le patch che superano i test funzionali e di sintassi vengono promosse alla **Stack List**.
3.  **Human-in-the-Loop Review**: L'utente visualizza una card dettagliata che spiega:
    - **COSA**: L'obiettivo della patch (es. "Fix lock contention on DuckDB").
    - **COME**: Il dettaglio tecnico delle modifiche.
4.  **Click-to-Apply & Atomic Backup**: Al momento del click, il sistema esegue un backup istantaneo dei file originali in `vault_data/backups/patches/`.

## 2. Emergency Fallback (Blackout Protocol)
Se una patch causa un crash critico che impedisce il riavvio della Dashboard:

- **Localizzazione Backup**: I file originali sono archiviati in: `vault_data/backups/patches/[TIMESTAMP]_PRE_PATCH/`.
- **Ripristino Manuale**: È sufficiente copiare i file dalla cartella di backup alla root del progetto tramite terminale.
- **Sovereign Recovery CLI**: In caso di emergenza, l'utility `python3 nv-link.py --rollback` esegue il ripristino dell'ultimo stato stabile conosciuto.

---
*Questa documentazione traccia i limiti operativi dell'evoluzione autoguidata. Istruisci l'Oracolo e i Giudici per mantenere i permessi di sovrascrittura entro i recinti del Sovereign Perimeter.*

---



---

## 🗺️ ROADMAP: STATUS REPORT

### 🛡️ Phase 5 & 6 (COMPLETED v7.5)
- **Autonomous Red Teaming** & **Weighted Mesh Consensus**.

### 🧠 Phase 7 & 8: Sovereign Oracle (COMPLETED v8.3.0)
- **Math-First Stochastic Engine (Rust Acceleration)**.
- **Chronological State Locking (Chrono-Lock)**.
- **Advanced Scenario Kernels (Antifragility, Conflict, Retro-Causal)**.

### 🚀 Phase 9: Sovereign Orchestrator & Decision Intelligence (v8.4 - COMPLETATO ✅)
- **Vault Digital Twin**: [COMPLETATO] Implementazione di una Sandbox cognitiva (Twin Vault) per simulare l'impatto di nuova conoscenza senza alterare il vault reale.
- **Natural Language What-If 2.0**: [COMPLETATO] Interfaccia avanzata con **Guided Wizard**, **Temporal Scrubber** e **Plain-Language Results**.
- **Adaptive UX / Wiki 4.0**: [COMPLETATO] Streaming SSE, Causal Click-Through e Lazy Mermaid Rendering per un'esperienza a zero latenza.
- **WASM Simulation Core**: [COMPLETATO] Porting del core di simulazione per esecuzione locale nel browser.
- **Decision Journal & Oracle Accuracy**: [COMPLETATO] Registro immutabile DuckDB delle simulazioni con sistema di feedback per calcolare l'accuratezza predittiva.
- **Learning Path Generator**: [IN CORSO] Evoluzione della Wiki con mappatura automatica dei prerequisiti cognitivi.

### 🏺 Phase 9.2: Sovereign Hardening (v9.2 - COMPLETATO ✅)
- **Environment Isolation**: Spostamento di `VAULT_KEY` in `.env` per eliminare l'esposizione di segreti nel codice.
- **Lock-Free Reads**: Ottimizzazione del kernel per permettere letture concorrenti su DuckDB, eliminando il collo di bottiglia del mutex globale per le consultazioni.
- **Autonomous Patching Guard**: [v9.2.1] Introduzione del protocollo di separazione tra generazione e applicazione delle patch (Worker isolato).

### 🚀 Phase 10: Sovereign Hegemony (v9.1 - IN PIANIFICAZIONE 🚀)
*L'evoluzione da Vault Intelligente a Decision Command Center Autonomo.*

#### 🏗️ 1. Neural Kernel v2 (Performance & Formal Logic)
- **Epistemic Fingerprinting**: Invalidazione automatica delle conclusioni se i nodi di supporto cambiano o decadono.
- **Causal Gradient Descent**: Algoritmo per trovare la minima variazione necessaria in un nodo per influenzare l'intero grafo verso un obiettivo desiderato.
- **KùzuDB & Event Sourcing (CQRS)**: L'Aegis Event Log diventa l'unica fonte di verità.

#### 🐝 2. Swarm OS (Stability & Meritocracy)
- **PBC (Semantic Agent Profiling)**: Service discovery basato su `capability.json-ld`.
- **Agent Reward System**: Gli agenti guadagnano "token di merito" in base all'accuratezza delle previsioni.
- **Merit-based Priority**: Priorità di esecuzione basata sui reward; gli SLM (1.5B/3B) gestiscono il 90% del traffico locale.
- **Cognitive Presets**: Preset specializzati (es. "Analista Minsky", "Creativo De Bono") per guidare lo stile dell'orchestrazione.
- **Chrysalis Worker Isolation**: Patching autonomo testato in sandbox isolate prima del merge nel core.

#### 🛡️ 3. Governance: Epistemic Integrity & Red Teaming
- **Epistemic Proof-of-Work (PoW)**: Confidence score matematico basato sulla coerenza multi-sorgente e verifica formale Z3.
- **Predictive Health Alerts**: Monitoraggio della degradazione (Ebbinghaus Decay) con suggerimenti di review mirate.
- **Sovereign Adversary**: Funzione "Avvocato del Diavolo" nel Digital Twin per falsificare attivamente le proprie ipotesi.
- **Differential Twin (Copy-on-Write)**: Sandbox ad impatto zero che salvano solo le differenze rispetto al vault principale.
- **Biomimetic Knowledge Decay**: Implementazione della curva di Ebbinghaus per mantenere il Vault "fresco".

#### 🎨 4. Cognitive Cockpit (UX & Action)
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

## XIV. REPORT DI CONSOLIDAMENTO & HARDENING (Transizione v8.4 -> v9.0)

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
- **Consistenza**: Verifica della propagazione della `VAULT_KEY` (`vault_secret_aura_2026`) attraverso gli header `X-API-KEY`, risolvendo i residui errori `403 Forbidden` nelle sezioni dinamiche della dashboard.

### 5. Telemetria Sky-Walker (FS-77)
- **Risoluzione Contatori**: Correzione del bug dei contatori a zero nella Dashboard.
- **Log Forensi**: Implementazione di print granulari nel terminale per il monitoraggio in tempo reale delle fasi di *Search, Forage, Synthesis e Injection*.

### 6. NeuralWiki 3.0 & Memory HUD Consolidation (v9.1.x)
- **UI/UX (v9.1.1)**: Implementazione sidebar collassabile dinamica con animazioni fluide e tasto di ripristino. Ottimizzazione della ricerca tramite pulsante INVIO dedicato e supporto nativo per tastiera.
- **Deep-Z Visibility (v9.1.2)**: Risoluzione critica dei problemi di visibilità dei tooltip nella Memory Overview. Rimozione dei vincoli di overflow sui container principali e innalzamento dello Z-index a 9.9M per una leggibilità assoluta sopra ogni layer della dashboard.

### 7. Skywalker Research Hardening (v9.2.7)
- **Espansione Orizzonte**:
    - **Profondità**: Aumentata la profondità di crawling da 1 a **3 livelli**.
    - **Volume**: Aumentato il limite di pagine per missione da 10 a **50 pagine**.
    - **Cross-Domain**: Disabilitato il vincolo del dominio unico (`same_domain_only=False`). Skywalker può ora seguire link verso fonti esterne per corroborare le informazioni.
- **Stealth Search Upgrade**:
    - Skywalker ora utilizza il motore di fetch avanzato del `SovereignWebForager` anche per i risultati di ricerca.
    - Questo garantisce l'uso di **browser-like headers** e il **fallback automatico su Playwright** (browser reale) se Google o DuckDuckGo dovessero bloccare la richiesta standard.
- **Risoluzione Anomalia 'python'**:
    - Migliorata la gestione degli errori nelle ricerche; i fallimenti ora vengono loggati in modo più granulare invece di restituire silenziosamente un "nessun risultato". Skywalker è ora in grado di condurre ricerche "High-Altitude" molto più profonde e resilienti ai blocchi. 🏺🚀🦾

### 8. NeuralVault Sovereign v9.2.8 – Yoda Deployment & Skywalker Hardening (v9.2.8)
**Stato: OPERATIVO ✅**

*   **Skywalker Fix (FS-77)**: Risolto il `SyntaxError` (indentazione errata del blocco `try...finally`) che impediva l'avvio del server. Ora Skywalker è resiliente ai crash di missione e resetta correttamente lo stato su `Scanning Horizon...`.
*   **Heartbeat Diagnostico**: Integrato il log 💓 `[FS-77/Heartbeat]` per monitorare l'attività proattiva nel terminale.
*   **Yoda File Searcher (YO-001) – Implementazione Completa**:
    *   **Cervello (Backend)**: Implementato in `neural_lab.py`. Yoda esegue un "Pellegrinaggio" esaminando 1000 nodi alla volta (anche nodi orfani) prima di lanciare missioni di espansione galattica.
    *   **Corpo (Cycloscope 3D)**: Creata la mesh della navicella Yoda con colori Verde Smeraldo, Arancio e Grigio.
    *   **Arsenale Visivo**: Laser Gialli a 4 cannoni (`spawnYodaLaser`) attivi durante l'iniezione di conoscenza.
    *   **Sprite Retro**: Sprite Yoda pixel art in CSS (box-shadow) integrato nell'HUD.
*   **Integrazione UI/UX**: Slot HUD Yoda abilitato con telemetria in tempo reale e supporto `toggleFollow`.

### 9. NeuralVault v8.4.1: Sovereign Swarm Evolution & R2-D2 Deployment (v8.4.1 - OGGI ✅)
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

### 10. NeuralVault v10.0: Sovereign Modular Dashboard Architecture (v10.0 - COMPLETATO ✅)
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
*   **Cycloscope Camera Fix**: Ottimizzato l'algoritmo di aggancio degli agenti nella barra laterale. Il sistema ora garantisce un inseguimento fluido e centrato su ogni sprite dello sciame.
*   **Asset Orientation**: Corretto l'orientamento delle navicelle Yoda e Skywalker per una navigazione coerente nello spazio tridimensionale.

### 11. NeuralVault v10.5: Immersive Flight Mechanics & Combat Simulator (COMPLETATO ✅)
**Stato: OPERATIVO ✅**

> 🌌 **Filosofia di Esplorazione**: L'introduzione delle meccaniche di volo spaziale e del simulatore immersivo non nasce come un vezzo puramente videoludico, ma come una **metafora d'esplorazione cognitiva**. Il modulo "Flight & Combat" è stato concepito esclusivamente per permettere all'utente di compiere un vero e proprio viaggio interstellare attraverso la propria base di conoscenza: pilotare la nave significa navigare fisicamente tra le costellazioni di documenti, sfrecciare attraverso le galassie di dati vettoriali e perlustrare le nebule semantiche generate organicamente all'interno del proprio Vault personale.

*   **Navigazione Avanzata WASD**: Superamento dei conflitti di 'Event Bubbling' della Dashboard UI tramite listener di tastiera ad altissima priorità (`Capture Phase: true`), che garantisce il pieno controllo della navicella nello spazio 3D ignorando i focus lock di altri widget.
*   **Quantum Boost & Hyper-Drive (Tasto P)**: Sviluppo del sistema di propulsione dinamico. Singola pressione per l'Hyper-Drive. Sistema 'Double-Tap' (<400ms) per l'innesco del Quantum Boost (velocità 3x, FOV dinamico a 120° per effetto tunnel-warp, e post-bruciatori reattivi con palette HSL Rosso Fuoco/Arancione Magma).
*   **Arcade Cockpit Overlay (Tasto 1)**: Riprogettazione totale della Visuale in prima persona. Aggancio automatico delle API Fullscreen del browser, mascheramento (hide) in tempo reale del modello 3D, e iniezione diretta di overlay 2D in formato immagine (`cockpit.png`) ancorato alla telecamera per il massimo feeling Arcade.
*   **Tactical Chase Cam (Tasto 2)**: Incremento del 200% dell'offset sull'asse Z per l'inseguimento in terza persona, finalizzato alla godibilità visiva della propulsione e dello sciame neurale circostante.

---

🏺 **NeuralVault-OS: Turning Orchestration into Sovereign Power.**
*Official Documentation Sovereign Maturity v10.5.0 -> Roadmap Phase 10 Integrated & Hardened*
