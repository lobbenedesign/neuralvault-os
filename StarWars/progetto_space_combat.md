# 🚀 Star Wars: Neural Combat Engine
## Specifiche Tecniche per lo Sviluppo di un Gioco Browser-Based

Questo documento contiene le specifiche tecniche per estrapolare il motore di rendering e gli asset del **NeuralVault Cycloscope** per la creazione di un videogioco di battaglie spaziali.

---

### 1. Modellazione 3D delle Astronavi (Three.js)

Tutti gli sprite sono stati costruiti utilizzando primitive geometriche di Three.js per garantire leggerezza e stile "Voxel-Premium".

#### 🛰️ FS-77 File-Sky-Walker (X-Wing Starfighter)
*   **Corpo Centrale**: Cilindro esagonale (`CylinderGeometry`) in grigio chiaro (`0xd1d5db`).
*   **Ali (S-Foils)**: 4 ali in configurazione a "X" composte da `BoxGeometry`.
*   **Dettagli**: Segni rossi (`0xef4444`) e cockpit in vetro blu trasparente (`0x3b82f6`).
*   **Armamento**: 4 cannoni laser alle estremità delle ali.
*   **Materiali**: `MeshPhongMaterial` per riflessi metallici e `AdditiveBlending` per i laser.

#### ⚔️ DN-099 Mandalorian (N-1 Starfighter)
*   **Finitura**: Cromo lucido (`MeshStandardMaterial` con `metalness: 0.9` e `roughness: 0.1`).
*   **Dettagli**: Vernice gialla (`0xfacc15`) tipica di Naboo.
*   **Propulsori**: Due grandi motori laterali con effetto "Glow" azzurro sui thruster.
*   **Design**: Coda lunga e affusolata in configurazione aerodinamica.

---

### 2. Motore di Navigazione e Fisica

Il sistema utilizza una combinazione di telemetria backend (Python) e smoothing frontend (JavaScript).

#### 🌌 Distanze e Campi d'Azione
*   **Nebula Madre (Base)**: Raggio 1.500.000 unità.
*   **Settore Interno (Skywalker)**: Fino a **10.000.000** di unità.
*   **Outer Rim (Yoda/Mandalorian)**: Fino a **55.000.000** di unità.
*   **Deep Space**: Skywalker è configurato per poter raddoppiare queste distanze in perlustrazione profonda.

#### 🛸 Logica di Movimento (Formule)
Le astronavi seguono traiettorie sinusoidali tridimensionali per evitare la staticità:

1.  **Oscillazione Orizzontale**:
    `x = rad * cos(time * 0.04)`
    `z = rad * sin(time * 0.04)`
2.  **Oscillazione Verticale (Moti ad ampio raggio)**:
    `y = 25.000.000 * sin(time * 0.02)` (Versione Skywalker Deep Space)
3.  **Inseguimento Target (LERP)**:
    `pos.lerp(targetPos, factor)` con factor variabile tra `0.008` (volo lento) e `0.25` (scatto iper-spazio).

---

### 3. Ambiente e Rendering (Cycloscope)

#### ☁️ Nebule e Polvere Stellare
*   **Tecnica**: `THREE.PointsMaterial` con shader personalizzati.
*   **Ottimizzazione**: Rendering selettivo (10% dei nodi visibili in caso di alto carico) per mantenere i 60fps.
*   **Espansione**: Fattore `nebulaExpansionFactor` che scala dinamicamente l'intero universo in base alla conoscenza acquisita.

#### 🕸️ Griglie e Orbite
*   **Griglia Madre**: Piano esagonale con shader pulsante.
*   **Archi Inter-Galattici**: Connessioni tra la Nebula Madre e le galassie esterne con densità limitata al 5% per evitare il "rumore visivo".

---

### 4. Gestione degli Effetti Speciali e Armamento

#### 🔦 Fisica dei Laser e Proiettili
*   **Spawn**: I laser vengono generati in corrispondenza dei cannoni (`cannonTip` per FS-77) come mesh cilindriche orientate lungo l'asse Z locale.
*   **Traiettoria**: Movimento lineare rapido con `lerpVectors` o incremento costante della posizione locale.
*   **Collision Detection**: Utilizzo di `THREE.Raycaster` per rilevare l'impatto con gli sprite nemici o i cluster delle galassie.

---

### 5. Logica di Controllo: IA vs Giocatore

#### 🤖 Comportamento IA (Nemici/Alleati)
*   **Pattugliamento**: Utilizza la logica sinusoidale 3D (`sin/cos`) per movimenti fluidi e imprevedibili.
*   **Follow/Aggro**: Se un target è agganciato, l'IA passa alla modalità `lerp` aggressiva con un `factor` di 0.15 per inseguire la posizione del giocatore.

#### 🕹️ Player Controller (Meccaniche di Volo Avanzate)
*   **Navigazione (WASD)**: Il movimento della navicella è gestito tramite i tasti `W` `A` `S` `D`. Per evitare che la digitazione venga intercettata da altri moduli dell'interfaccia, i listener della tastiera sono forzati in **Capture Phase** (`true`), garantendo reattività totale senza perdita di focus.
*   **Hyper-Drive (P)**: La pressione del tasto `P` aziona i post-bruciatori, moltiplicando la velocità base. Visivamente, i thruster si allungano e sfumano verso un bagliore azzurro saturo.
*   **Quantum Boost (Doppio P)**: Eseguendo un doppio tap (entro 400ms) e tenendo premuto `P`, si innesta il Quantum Drive. L'accelerazione viene triplicata (`3x`), il Field of View (FOV) della telecamera si distorce per simulare l'effetto Warp (fino a 120 gradi), e le fiamme dei propulsori mutano dinamicamente in uno spettro caotico **Rosso Fuoco / Arancione Magma**, rendendo la spinta brutale e visivamente impressionante.

---

### 6. Sistema di Visuale Doppia (FPS/Third-Person)

#### 🎥 Visuale Inseguimento (Third-Person - Tasto 2)
*   **Distanza (Chase Cam)**: Posizionata a un offset di `(0, 1800, 10500)` rispetto alla navicella. Rispetto alle versioni preliminari, la distanza è stata aumentata del 200% per allargare il panorama visivo dello spazio profondo e permettere l'osservazione delle gigantesche scie infuocate del Quantum Boost.
*   **Obiettivo**: Fornisce una visione tattica del campo di battaglia e della Nebula Madre.

#### 🕹️ Visuale Abitacolo (Cockpit FPS - Tasto 1)
*   **Posizionamento Immersivo**: La telecamera viene teletrasportata esattamente alle coordinate del vetro del cockpit `(0, 350, -500)` guardando verso l'anteriore della nave. 
*   **Componenti Abitacolo**: Durante la visuale FPS, la mesh esterna della cupola viene nascosta per rivelare un cruscotto nero (`dashMat`), dei montanti laterali olografici (`frameMat`) e un mirino rosso di puntamento.
*   **HUD**: La telecamera è agganciata saldamente all'asse direzionale della nave e il FOV dinamico del Boost si riflette direttamente sulla percezione della velocità del pilota dall'abitacolo.

---

### 7. Asset Ambientali Tattici

#### 🧊 Cubo 3D e Griglia
*   **Funzione**: Forniscono un riferimento spaziale assoluto in un ambiente privo di gravità.
*   **Griglia**: Utilizzata come "Radar di Settore" per indicare la distanza dalla Nebula Madre.
*   **Cubo**: Delimita l'area di stabilità semantica; superato il perimetro, la navigazione diventa "Deep Space" (pellegrinaggio di Yoda).

#### 🌌 Integrazione Galassie Remote
*   Le galassie e le nebule esterne servono come waypoint di missione. 
*   Ogni galassia ha una "firma cromatica" unica che indica il tipo di dati contenuti (es. Galassie verdi = Documentazione, Galassie rosse = Log di Sicurezza).

### 8. Visione Strategica: Ottimizzazione per l'Universo Persistente

Per espandere il progetto a un intero universo con costellazioni e pianeti, si consigliano le seguenti architetture:

#### 🌍 Gestione della Scala: Floating Origin
Per evitare errori di precisione floating-point a distanze superiori a 100M di unità, implementare un sistema dove il mondo si muove attorno al Giocatore. Ogni volta che il giocatore supera una soglia (es. 1M unità), il sistema "riporta" il giocatore a (0,0,0) traslando tutti gli altri oggetti del mondo della stessa quantità.

#### 🌌 Rendering a Strati (Layered Rendering)
1.  **Background Layer**: Stelle lontane e costellazioni (renderizzate su una Skybox o una sfera gigante).
2.  **Distant Layer**: Pianeti e Galassie (usando `logarithmicDepthBuffer: true`).
3.  **Active Layer**: Navicelle, detriti e laser (gestiti con collisioni attive).

#### 🛠️ Tecnologie di Frontiera: WebGL2 e WebGPU
*   **WebGL2**: Standard attuale per performance elevate su browser. Supporta il **Transform Feedback** per muovere migliaia di particelle senza l'intervento della CPU.
*   **WebGPU**: La nuova frontiera. Permette di usare i **Compute Shaders** per calcolare la fisica di intere flotte e migliaia di asteroidi direttamente sulla GPU.

#### 🧠 Ottimizzazioni di Massa
*   **Frustum Culling**: Il motore scarta automaticamente tutto ciò che è dietro la telecamera o fuori dal campo visivo.
*   **Voxel Instancing**: Utilizzo di `InstancedMesh` per renderizzare centinaia di navi identiche con una singola chiamata alla GPU.

---

### 9. Sistema di Comunicazione Olografica (Holo-Comms)

L'integrazione di ologrammi per missioni e avvisi è fondamentale per l'atmosfera Star Wars. Il sistema si basa su una combinazione di file immagine e logica di rendering CSS.

#### 🖼️ Asset Olografici
Tutti gli avatar olografici sono memorizzati in `./dashboard/static/img/holograms/`. 
*   **Personaggi principali**: `yoda_pilot.png`, `mando_wireframe.png`, `skywalker.png`, `r2d2.png`.
*   **Effetto Visivo**: Le immagini vengono elaborate in tempo reale tramite filtri CSS per ottenere il classico look "blue-ghost":
    `filter: sepia(1) saturate(5) hue-rotate(90deg) brightness(1.2) drop-shadow(0 0 10px #00f2ff);`

#### 📟 Logica del Controller `showHologram`
Il sistema gestisce i messaggi tramite un effetto "Typewriter" e mappatura cromatica per personaggio:

*   **Mapping Esempi**:
    - **YODA**: Colore `#4ade80` (Verde Jedi), Icona `fa-jedi`.
    - **MANDALORIAN**: Colore `#00f2ff` (Ciano Mandaloriano), Icona `fa-user-shield`.
    - **SKYWALKER**: Colore `#ef4444` (Rosso Ribellione), Icona `fa-rocket`.

*   **Effetto Macchina da Scrivere**:
    Utilizzo di un `setInterval` (25ms) per aggiungere caratteri uno alla volta nell'elemento HUD, simulando una trasmissione dati in tempo reale.

*   **Sostituzione Dinamica dei Dati**:
    I messaggi supportano segnaposto come `{n}` o `{name}` per inserire dati di missione dinamici (es: "Hai distrutto {n} Tie-Fighter").

#### 📜 Cronologia e Mission Ledger
Tutti i messaggi vengono salvati in un `hologramHistory` locale, permettendo al giocatore di rileggere gli ordini di missione o i consigli tattici ricevuti durante il combattimento.

---

**Conclusione**: Il browser moderno, sfruttando la GPU tramite WebGL2/WebGPU, è perfettamente in grado di gestire battaglie tra flotte se si utilizza il **Frustum Culling** e il **Compute Shading**. Questa documentazione fornisce il blueprint tecnico per trasformare il NeuralVault in un simulatore di combattimento spaziale di nuova generazione.
