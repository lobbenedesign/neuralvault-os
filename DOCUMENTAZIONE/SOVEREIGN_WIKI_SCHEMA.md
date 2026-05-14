# 🏛️ SOVEREIGN WIKI SCHEMA v9.0.0
**Canonical Specification for Autonomous Knowledge Generation & Persistent Synthesis**

---

## 1. Overview
Il **Sovereign Wiki Schema** definisce lo standard strutturale per ogni pagina generata o aggiornata dal `CompoundingWikiManager`. L'obiettivo è trasformare il Markdown statico in un oggetto di conoscenza "vivo", verificabile formalmente e pronto per l'analisi causale.

![Sovereign Wiki Implementation Context](assets/Screenshot%202026-05-10%20alle%2016.42.08.png)

## 2. Frontmatter (YAML Metadata)
Ogni file Wiki DEVE iniziare con il seguente blocco di metadati per permettere l'indicizzazione nel `Cross-Reference Index` (DuckDB):

```yaml
---
id: "concept_uuid"
title: "Concept Name"
namespace: "concepts/tech/ai"
version: "9.0.0"
epistemic_fingerprint: "hash_sha256"
z3_verified: true
last_compounding: "2026-05-14T08:00:00Z"
confidence_score: 0.98
source_nodes: ["node_id_1", "node_id_2"]
---
```

## 3. Struttura della Pagina

### 3.1 Epistemic HUD (Header)
Tutte le pagine includono un HUD visuale (tramite badge o testo formattato) che indica:
- **[🛡️ VERIFIED]**: Se la pagina ha superato il Z3 Formal Audit.
- **[🌡️ WEATHER]**: Stato di freschezza (☀️ Clear, 🌩️ Stormy if contradictions exist).
- **[🧬 LINEAGE]**: Link rapido alla radice causale nel Nexus Vault.

### 3.2 Executive Summary
Sintesi ad alto livello per il decision-maker.

### 3.3 Causal Dynamics (The Heart)
Sezione dedicata alle relazioni attive nel grafo:
- **Pre-requisites**: Cosa deve essere vero perché questo concetto sia valido.
- **Influences**: Quali altri nodi vengono attivati/inibiti da questo concetto.
- **Counter-Arguments**: Collegamenti diretti a nodi con arco `CONTRADICTS`.

### 3.4 Tactical Playbook
Converte la conoscenza in azione. Una lista di 5 step concreti derivati dal `PlaybookGenerator`.

### 3.5 Citations & Evidence
Ogni paragrafo critico deve contenere tag `[CITE:node_id]`. Questi tag sono interattivi nella dashboard e mostrano il documento originale al passaggio del mouse.

---

## 4. Compounding Rules (Auto-Evolution)
1. **Incrementalism**: Il sistema non sovrascrive mai la sezione "Fondamenti". Aggiunge sezioni "Update [Timestamp]" quando nuovi dati contraddicono o espandono il concetto.
2. **Pruning**: Se il `Confidence Score` scende sotto 0.4, la pagina viene marcata come `[DEPRECATED]` e Skywalker viene attivato per una missione di recupero.
3. **Z3 Conflict Resolution**: In caso di contraddizione logica rilevata da Z3, la pagina inserisce automaticamente un blocco `> [!CAUTION] CONFLICT DETECTED` in testa alla pagina.

---

🏺 **NeuralVault-OS: Turning Static Data into a Compounding Brain.**
