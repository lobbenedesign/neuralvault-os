# 🛸 Deep Dive: Neural Wiki & What-If Engine (v8.4)

Questa guida tecnica esplora l'integrazione end-to-end tra il nucleo neurale (Backend) e l'interfaccia cognitiva (Frontend) delle due funzioni più avanzate di Neural Vault.

---

## 🏛️ 1. NEURAL WIKI: Il Portale della Conoscenza Sovrana

### 🔹 Scopo e Funzioni
La Neural Wiki non è un semplice lettore di documenti; è un **Ambiente di Studio Immersivo**. Trasforma dati grezzi in articoli strutturati, verificati e pronti per il decision-making.
- **Synthetizer**: Riassume e connette nodi correlati.
- **Epistemic Auditor**: Verifica la solidità delle fonti e segnala le lacune.
- **Adaptive Reading**: Cambia il livello di dettaglio in base al profilo utente selezionato (Executive, Technical, Research).

### ⚙️ Cosa succede nel Backend
1. **RAG (Retrieval Augmented Generation)**: Quando apri un articolo, il backend interroga DuckDB e la cache NIC per recuperare non solo il testo, ma i metadati di connessione (Archi Causali).
2. **Confidence Scoring**: Il sistema assegna un punteggio di confidenza (0.0 - 1.0). Se il punteggio è basso (<0.3), viene attivato automaticamente il modulo **FLARE** per recuperare conoscenza aggiuntiva.
3. **Chrono-Lock Versioning**: Ogni modifica alla Wiki viene salvata con un timestamp immutabile. Il backend gestisce i "viaggi nel tempo" cognitivi permettendo di vedere come la tua comprensione di un concetto è cambiata nel tempo.
4. **Mermaid Generation**: L'LLM analizza i nodi e genera codice Mermaid.js al volo per visualizzare flowchart e timeline.

### 🎨 Cosa succede nel Frontend
1. **Interactive HUD**: Le citazioni `[CITE:id]` sono pulsanti attivi. Passandoci sopra, il frontend apre un mini-tooltip con il contenuto del nodo originale.
2. **3D Nebula Focus**: Nella barra laterale, il grafo 3D ruota e zooma automaticamente sul nodo che stai leggendo, mostrandone visivamente i vicini semantici.
3. **Epistemic Weather HUD**: Un componente visuale che indica lo stato della conoscenza (es. "Incertezza Alta", "Mesh Sincronizzata", "Fonti mancanti").

---

## 🧪 2. WHAT-IF ENGINE: Il Simulatore di Futuri Probabili

### 🔹 Scopo e Funzioni
Il What-If Engine permette di testare ipotesi nel passato o nel futuro. È il "laboratorio di strategia" del Vault.
- **NL Parser**: Converte domande umane in variabili matematiche.
- **Impact Predictor**: Calcola la propagazione a cascata di un cambiamento.
- **Risk Assessor**: Evidenzia i nodi che potrebbero subire danni collaterali.

### ⚙️ Cosa succede nel Backend
1. **Intent Extraction**: La query naturale dell'utente viene inviata a un LLM (es. *Qwen 2.5 Coder*) che estrae un JSON contenente: `target_node`, `intensity`, `direction` e `time_horizon`.
2. **Monte Carlo Simulation (Rust Core)**: Il simulatore esegue 1000 iterazioni stocastiche in meno di 10ms. Utilizza un algoritmo di **Causal Graph Traversal** per calcolare come una variazione sul nodo A influenzi i nodi B, C e D in base ai pesi delle relazioni.
3. **Stochastic Noise**: Viene iniettato del "rumore" gaussiano per simulare l'imprevedibilità del mondo reale (caos engineering).
4. **Natural Language SITREP**: Un secondo LLM (es. *DeepSeek-R1*) prende i dati tabellari della simulazione e li trasforma in un report narrativo per l'utente.

### 🎨 Cosa succede nel Frontend
1. **Interactive Simulation Bar**: L'utente può regolare la "magnitudo" dell'evento tramite slider dinamici che inviano segnali al backend.
2. **Graph Highlighting**: Durante la simulazione, i nodi influenzati nel grafo 3D iniziano a "pulsare" o a cambiare colore (Rosso per impatto negativo, Verde per positivo).
3. **SITREP Panel**: Una finestra modale mostra il report finale con grafici a barre che indicano la probabilità di successo dell'intervento.

---

## 🤝 3. INTEGRAZIONE UTENTE & RISULTATI

### Flusso di Lavoro Ideale
1. **Input**: L'utente chiede: *"Che succede se aumentiamo il focus sulla cybersicurezza del 50%?"*.
2. **Elaborazione**: Il sistema sospende i task non prioritari (**Priority Shift**), analizza 3-5 nodi chiave e avvia la simulazione.
3. **Riscontro Log**: Nel terminale appare la telemetria (LLM usato, tempo di calcolo, nodi analizzati).
4. **Output**:
    - **Narrativo**: *"La cybersicurezza aumenterà la stabilità ma rallenterà la velocità di sviluppo del 15%"*.
    - **Visuale**: Il grafo 3D illumina i nodi "Firewall" e "Encryption" come nuovi centri di gravità.
    - **Decisionale**: L'esito viene salvato nel **Decision Journal** per un confronto futuro tra previsione e realtà.

---
*Documentazione redatta per l'evoluzione Sovrana di NeuralVault. Ispirata dalla visione di Giuseppe Lobbene per un futuro di libertà cognitiva e decisionale.*
