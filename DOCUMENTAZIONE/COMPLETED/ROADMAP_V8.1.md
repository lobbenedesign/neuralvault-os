# 🏛️ Roadmap NeuralVault v8.1: "The Predictive Sovereign"
**Obiettivo**: Elevare Phase 7 da MVP funzionale a standard Enterprise/Sovereign.

---

## 🛰️ Phase 7.1: Probabilistic Intelligence (The Brain)
*Uscire dal determinismo per abbracciare l'incertezza reale.*

### 1. Monte Carlo What-If Engine
- **Backend**: Implementazione di `MonteCarloSimulator` in `causal_simulator.py`. Esecuzione di 1000 iterazioni stocastiche con rumore gaussiano applicato ai pesi degli archi.
- **Frontend**: Sostituzione dei singoli numeri con **Violin Plots** (SVG) e intervalli di confidenza (90% CI).
- **Metriche**: Introduzione di "Worst Case" e "Probability of Success".

### 2. Semantic Entity Linking
- **Backend**: Creazione di un indice di "Entity Anchors" per ogni pagina Wiki generata. Sostituisce la ricerca Regex con un mapping ID-parola chiave sicuro.
- **Frontend**: Highlight del testo basato su mapping semantico. Supporto per sinonimi e contesti semantici.

---

## 🏺 Phase 7.2: Adaptive Knowledge Portal (The Interface)
*La conoscenza che si adatta a chi la consuma.*

### 1. Adaptive Reading Protocol
- **Modalità EXECUTIVE**: Sintesi estrema, focus su Rischi/Opportunità, grafici semplificati.
- **Modalità TECHNICAL**: Deep dive, schemi Mermaid complessi, blocchi di codice, benchmark.
- **Modalità RESEARCH**: Analisi delle contraddizioni, "Mappa dell'ignoranza" (Gaps), bibliografia completa.
- **UI**: Switcher con transizione CSS *Crossfade* professionale.

### 2. Progressive Disclosure (Inline Portal)
- **Hover Action**: Pannello espandibile inline (`DisclosurePanel`) che carica una preview di 80 parole del termine.
- **Direct Actions**: Pulsanti "What-If", "Nebula Focus" e "Full Article" direttamente nel popup di anteprima.

---

## 🌦️ Phase 7.3: Actionable Triage (The Command)
*Dal monitoraggio all'azione sovrana.*

### 1. Epistemic Command HUD
- **Sunny**: Azioni di "Esporta Reference" e "Condividi con Mesh".
- **Cloudy**: Azione "Trigger SkyWalker" (ricerca web proattiva) e "Refresh Stale Nodes".
- **Storm**: Azione "Resolve Contradictions" (LLM-based arbitration) e "Mark as Unverified".
- **UI**: Visualizzazione separata e dettagliata di `Confidence` vs `Freshness`.

### 2. Time-Horizon Simulation
- **Timeline Predittiva**: Visualizzazione degli impatti a 1 mese, 6 mesi e 1 anno tramite Chart.js.
- **Logic**: Integrazione dei fattori di decadimento temporale nel motore causale.

---

## 🦾 Phase 7.4: High-Velocity Optimization (The Engine)
*Fluidità estrema su 1.0M+ di nodi.*

### 1. NIC Virtual Scrolling
- **Implementation**: Caricamento lazy dei nodi ricostruiti. Solo gli elementi visibili vengono passati attraverso il decoder NIC.
- **Caching**: Layer di cache LRU (Least Recently Used) per gli embedding ricostruiti.

---

## 📊 Priorità di Implementazione (Quick Wins)

1. **[LOW EFFORT / HIGH IMPACT]**: Sostituzione Regex -> Semantic Linking + Hover Inline.
2. **[MEDIUM EFFORT / MAX VALUE]**: Monte Carlo What-If (Probabilistico).
3. **[HIGH EFFORT / PREMIUM]**: Adaptive Reading Protocol.

---

🏺 **NeuralVault v8.1: Turning Probabilities into Power.**
