# 📖 Sovereign Wiki & Visual Singularity (v4.3.1)

Benvenuto nel manuale operativo del **NeuralVault Sovereign Wiki**. Questa estensione trasforma il tuo database vettoriale in una enciclopedia dinamica e navigabile in 3D.

---

## 🚀 1. Come Generare una Pagina Wiki

Esistono tre modi per popolare la Wiki:

1.  **Dalla Dashboard**: Inserisci un argomento nel campo di ricerca principale e clicca su "Generate Wiki".
2.  **Tramite API**: Invia una richiesta POST a `/api/wiki/generate` con il corpo:
    ```json
    { "topic": "Storia dell'Intelligenza Artificiale", "recursive": true }
    ```
3.  **Cross-Linking**: All'interno di una pagina Wiki, le parole evidenziate in **viola** sono link. Cliccandoci, il sistema cercherà o genererà automaticamente una nuova pagina correlata.

---

## 🌌 2. Visual Singularity: Leggere la Nebula

Con l'integrazione del **Cycloscope v4.3**, la nebula non è più solo estetica:

### 🕸️ Synaptic Layers (Linee di Luce)
Quando leggi una pagina Wiki, vedrai apparire delle linee dorate/neon tra i nodi. Queste sono le **Sinapsi Sovrane**: rappresentano le relazioni reali che il sistema ha estratto dai tuoi dati per scrivere quell'articolo.
*   **Focus**: La telecamera si sposterà automaticamente sul cluster di conoscenza principale.

### 🔥 Temporal Heatmap (Confidence Mapping)
Attiva il layer Heatmap per vedere la "freschezza" della conoscenza:
*   **Verde Neon**: Informazioni recenti, verificate e ad alta confidenza.
*   **Viola/Opaco**: Informazioni vecchie o in decadimento (Cognitive Decay). Il sistema ti avvisa che questi dati potrebbero necessitare di un aggiornamento o di una riflessione critica.

---

## 🏛️ 3. Sovereign Ledger & Audit

Ogni operazione della Wiki viene registrata nel **Ledger**. Puoi verificare lo stato di integrità del sistema in qualsiasi momento:
*   **Endpoint**: `/api/system/audit-verify`
*   **Significato**: Se il `ledger_density` è alto, significa che la tua Wiki è densamente connessa e affidabile.

---

## 🧠 4. Riflessione Critica

Sotto ogni articolo Wiki troverai il pulsante **"AVVIA RIFLESSIONE CRITICA"**. 
Questo attiva la **Triple-Judge Supreme Court**: tre istanze diverse del modello analizzeranno il contenuto per trovare contraddizioni, allucinazioni o lacune nella tua base di conoscenza.

---

> [!TIP]
> Se la nebula sembra troppo densa, usa lo slider **Nebula Expansion** nelle impostazioni per distanziare i nodi e vedere meglio le sinapsi Wiki.
