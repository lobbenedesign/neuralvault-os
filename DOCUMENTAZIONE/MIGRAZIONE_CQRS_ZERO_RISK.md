# 🔄 PIANO DI MIGRAZIONE "ZERO-RISK": CQRS & EVENT SOURCING

Questo documento delinea la strategia per trasformare NeuralVault in un sistema ad Eventi Immutabili (Event Sourced), isolando le scritture dalle letture (CQRS), garantendo che l'applicazione attuale continui a funzionare senza interruzioni durante l'intera transizione.

---

## 🛡️ LA REGOLA D'ORO DEL ROLLBACK
Fino alla conclusione della FASE 4, il tuo attuale sistema di salvataggio su DuckDB rimarrà intatto e attivo. Tutte le nuove funzionalità CQRS verranno costruite "in parallelo" (Shadow Mode). In caso di bug o problemi di performance, basterà disattivare l'EventBus e il software tornerà immediatamente allo stato precedente, senza che nessun dato originale venga compromesso.

---

## 🟢 FASE 1: "Shadow Logging" (L'Osservatore Silenzioso)
**Obiettivo:** Iniziare a registrare la storia del Vault senza toccare un singolo meccanismo di lettura o scrittura esistente. Nessuna modifica strutturale.

1. **Creazione Modulo Core (`core/event_bus.py`)**: Svilupperemo la classe `AegisEventBus`. Il suo compito è ricevere dati e incapsularli in uno schema rigido contenente una **Sequence Monotòna Thread-Safe**, un `correlation_id` e un **Checksum SHA256** contro il bit-rot. Scriverà i dati in un file Append-Only (`aegis_event_log.jsonl`).
2. **Iniezione degli "Hook" (Spie)**: Nei file attuali (`api.py` o nei gestori del database), **non cancelleremo nulla**. Aggiungeremo solo una riga alla fine del salvataggio di un nodo: `EventBus.publish("NODE_CREATED", payload)`.
3. **Validazione della Fase 1**: Il Vault funzionerà esattamente come oggi. Ma in background, creeremo finalmente una traccia storica perfettamente deterministica e a prova di multi-agente concorrente.

---

## 🟡 FASE 2: "Snapshot Engine & Automated Disaster Recovery"
**Obiettivo:** Evitare il collasso da Cold Start ed assicurare determinismo a lungo termine.

1. **Sviluppo del `SnapshotDaemon`**: Un processo leggero che scatta una "foto" allo stato attuale del Vault e salva un mega-evento speciale di tipo `SNAPSHOT_CREATED` nell'Event Log, permettendo al server di riavviarsi istantaneamente senza rileggere anni di eventi.
2. **Test di Ricostruzione Automatizzato (CI/CD)**: Invece di un test "una tantum", creeremo una pipeline automatizzata (`tests/test_event_sourcing.py`). Genererà N eventi, costruirà la proiezione, la distruggerà e la ricostruirà dal log. Controllerà che il Checksum finale sia identico.
3. **Validazione della Fase 2**: Questo test girerà in background per garantire che nessuna nuova feature futura rompa mai la ricostruzione del database.

---

## 🟠 FASE 3: Dual-Write Interception & "Read-Your-Own-Writes"
**Obiettivo:** Addestrare il sistema a dividere Comandi (Scritture) dalle Query (Letture).

1. **Routing delle Scritture (Commands)**: Le API di `POST /nodes` invieranno un Comando all'EventBus invece di scrivere direttamente nelle tabelle DuckDB.
2. **I Projection Builders (Listener)**: "Workers" asincroni in ascolto sull'EventBus intercetteranno gli eventi per aggiornare le proiezioni relazionali/a grafo.
3. **Read-Your-Own-Writes Consistency**: Abbandoniamo il vecchio concetto di acknowledge globale sincrono. L'EventBus garantirà che *l'agente che ha scritto un nodo* debba attendere che la proiezione arrivi alla sua "Sequence", mentre gli altri agenti continueranno a leggere i dati a velocità massima (Eventual Consistency pura) senza bloccarsi.

---

## 🔴 FASE 4: Lo Switch Definitivo e il Time-Travel
**Obiettivo:** NeuralVault diventa ufficialmente un'architettura CQRS pura. Addio al vecchio mondo.

1. **Switch delle Letture (Queries)**: Le API di `GET` e la Dashboard 3D non interrogheranno più il vecchio database monolitico, ma leggeranno esclusivamente dalle Proiezioni ottimizzate (DuckDB/KùzuDB).
2. **Sblocco Feature: Epistemic Time-Travel**: Poiché ora la "Verità" risiede nell'Event Log, creeremo un'API per la Wiki 4.0: `GET /vault?timestamp=2026-01-01`. Il Projection Builder riprodurrà gli eventi fino a quella data e fornirà un grafo nel passato, aprendo la strada alla verifica retro-causale.
3. **Pulizia (Deprecation)**: Rimozione del codice di scrittura legacy ormai bypassato.

---

### Prossimo Passo Immediato
Per avviare la **Fase 1** in modo sicuro, creeremo il modulo `event_bus.py` e definiremo lo schema del JSON (Envelope) senza toccare i file operativi correnti.
