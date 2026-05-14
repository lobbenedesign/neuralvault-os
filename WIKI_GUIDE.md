# 🏛️ Sovereign Wiki 4.0: The Decision Oracle (v9.0.0)
**Technical Report & Operational Manual — Sovereign Hegemony: Compounding Release**

NeuralVault v9.5 introduce il pattern **Compounding Writes**. La Wiki non è più un archivio statico, ma un organismo vivente che cresce e si aggiorna automaticamente ogni volta che nuova conoscenza entra nel Vault.

---

## 📊 1. Il Ciclo del Compounding (Pattern di Karpathy)

A differenza dei sistemi tradizionali, NeuralVault non lascia che le pagine wiki invecchino. Abbiamo implementato un ciclo ricorsivo:
1.  **Ingestion**: Un nuovo documento (Paper, Nota, URL) entra nel Vault.
2.  **X-Ref Detection**: Il `CompoundingWikiManager` interroga il `Cross-Reference Index` (DuckDB) per trovare tutte le wiki esistenti che citano argomenti correlati.
3.  **Incremental Update**: Durante il "Neural Dreaming", il sistema non riscrive le pagine, ma le *estende* o *corregge* aggiungendo nuovi paragrafi con citazioni aggiornate.
4.  **Standard llms.txt**: La struttura della conoscenza è esposta via `/llms.txt`, permettendo ad agenti esterni (Claude Desktop, Cursor) di navigare il Vault con precisione millimetrica.

![Sovereign Wiki Context - Dashboard](assets/Screenshot%202026-05-10%20alle%2016.42.08.png)

---

## ⚙️ 2. Architettura & Standard

### Sovereign Wiki Schema
Tutte le generazioni seguono il file canonico `vault_data/wiki/SOVEREIGN_WIKI_SCHEMA.md`. Questo garantisce che ogni pagina abbia:
- **Z3 Formal Audit**: Badges di consistenza logica.
- **Epistemic Fingerprinting**: Validazione della base di supporto.
- **Causal Dynamics**: Mappatura delle influenze (Attiva/Inibisce).
- **Tactical Playbooks**: Step azionabili immediati.

### llms.txt Standard (v9.0.0)
NeuralVault espone un endpoint `/llms.txt` che funge da mappa per le AI. Contiene:
- Stato di salute del Vault.
- Indice delle galassie di concetti.
- Link diretti alle pagine wiki verificate (🛡️).

---

## 🛠️ 3. Guida Operativa

### Per l'Utente
- **Generazione**: Usa la dashboard per creare la "base" di un concetto.
- **Evoluzione**: Non devi fare nulla. Man mano che aggiungi documenti al Vault, vedrai le tue pagine wiki arricchirsi di nuove sezioni "Aggiornamento [Data]" e nuovi badge Z3.
- **Audit**: Se vedi un badge **[CONFLICT]**, significa che un nuovo documento ha contraddetto una wiki esistente. Il sistema ti inviterà a risolvere il conflitto logico.

### Per gli Agenti AI (via MCP)
Gli agenti che si connettono a NeuralVault leggeranno prima `llms.txt`. Questo permette loro di:
1. Capire quali sono i concetti "core" (in `concepts/`).
2. Sapere quali pagine sono state verificate formalmente via Z3.
3. Navigare le relazioni causali per suggerire simulazioni What-If.

---

## ✅ Checklist Compounding v9.0.0
- [x] **SOVEREIGN_WIKI_SCHEMA**: Implementato e attivo.
- [x] **llms.txt Generator**: Operativo su `/llms.txt`.
- [x] **Cross-Reference Index**: Tabella DuckDB `wiki_xref` attiva e popolata in tempo reale.
- [ ] **Compounding Auto-Updater**: (Fase 3 - In Sviluppo) Demone di background per aggiornamenti incrementali.
- [ ] **Wiki Linter**: (Fase 4 - In Sviluppo) Check globale di link rotti e integrità Z3.

**NeuralVault Sovereign Wiki: Turning Static Data into a Compounding Brain.** 🏺🚀🦾
