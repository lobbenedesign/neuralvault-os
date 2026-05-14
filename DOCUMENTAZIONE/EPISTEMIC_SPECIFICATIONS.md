# 🏺 EPISTEMIC ENGINE SPECIFICATIONS v9.0.0
**Technical Deep Dive into Epistemic Fingerprinting and Causal Gradient Descent**

---

![Epistemic Engine & Hardware Telemetry](assets/hardware_observatory.png)

## 1. Epistemic Fingerprinting (EF)
L'**Epistemic Fingerprint** è l'identità matematica di una conclusione all'interno di NeuralVault. A differenza di un semplice hash di file, l'EF mappa l'intero albero di supporto di un'idea.

### 1.1 L'Algoritmo
L'EF viene calcolato come un Merkle Root pesato:
1. **Node Hash**: Ogni nodo sorgente contribuisce con il suo contenuto e il suo `Confidence Score`.
2. **Edge Weight**: Il peso della relazione (Causale, Correlativa, Oppositiva) funge da moltiplicatore.
3. **Graph Topology**: La struttura stessa del sub-grafo viene codificata.

### 1.2 Applicazione: Invalidazione Automatica
Se un documento sorgente viene modificato o rimosso, tutti gli Epistemic Fingerprint che dipendono da esso diventano "orfani". Il sistema rileva istantaneamente il mismatch tra l'EF memorizzato nella Wiki e lo stato reale del Grafo, marcando la conoscenza come `[OUTDATED]` o `[UNVERIFIED]`.

---

## 2. Causal Gradient Descent (CGD)
Il **Causal Gradient Descent** è l'algoritmo di ottimizzazione proprietario di NeuralVault per trovare la "Minima Variazione Necessaria" (MVN).

### 2.1 Il Problema
Dato un obiettivo desiderato nel futuro (es. "Aumento della stabilità finanziaria") e un grafo di influenze complesso, quale singola azione o nodo ha il massimo impatto positivo con il minimo sforzo?

### 2.2 Il Metodo
Invece di addestrare una rete neurale, il CGD opera direttamente sulla topologia del Grafo Causale:
1. **Forward Pass**: Si proiettano N simulazioni Sobol-Owen QMC per stabilire una baseline.
2. **Gradient Calculation**: Si calcola la derivata parziale dell'obiettivo rispetto alla variazione di ogni nodo di input.
3. **Step Optimization**: Il sistema suggerisce la variazione nel nodo (es. "Riduci esposizione su X") che muove il sistema verso l'obiettivo seguendo il gradiente di massima influenza causale.

### 2.3 Visualizzazione
Nella Dashboard, il CGD viene visualizzato come un percorso luminoso di nodi (Cognitive Path) che vibrano con intensità proporzionale al loro potenziale di influenza.

---

🏺 **NeuralVault-OS: Turning Orchestration into Sovereign Power.**
