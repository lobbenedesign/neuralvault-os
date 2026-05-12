# 🛠️ Autonomous Patching & Auto-Evoluzione del Codice

## 1. Il Concetto di "Self-Editing"
Neural Vault non è un sistema statico. Grazie al modulo di **Autonomous Patching**, lo sciame di intelligenze artificiali ha la capacità di **modificare il proprio codice sorgente in tempo reale**. 
Quando l'agente *Evolution Suggestions* (supportato dal Supreme Court) rileva un bug, un'ottimizzazione mancante, o una miglioria architetturale, può generare una vera e propria *diff/patch* e applicarla direttamente ai file `.py` o `.js` del Vault.

## 2. Il Ciclo di Vita del Patching Autonomo

L'abilità di patchare i propri file segue un protocollo rigoroso per evitare che l'AI corrompa il sistema causando crash irreversibili:

1. **Rilevamento (Watcher Daemon)**: Il sistema monitora costantemente le anomalie o le richieste dell'utente che richiedono modifiche al codice.
2. **Generazione del Codice (Coding Specialist)**: Il modello dedicato al codice (es. `qwen2.5-coder:7b`) analizza il file sorgente interessato e scrive una proposta di sostituzione (Patch).
3. **Validazione (Coding Supervisor & Giudici)**: Prima di essere applicata, la patch passa per la *Supreme Court*. Un modello separato verifica se la patch rispetta la sintassi di Python/JS e non introduce falle di sicurezza.
4. **Backup (Snapshot Engine)**: Immediatamente prima di toccare i file, il Vault crea un backup istantaneo (Snapshot). Se qualcosa va storto, il sistema può regredire alla versione precedente (Self-Healing).
5. **Iniezione & Hot-Reload**: La patch viene scritta fisicamente nel filesystem. Python ricaricherà i moduli in background ove possibile, oppure la UI si aggiornerà per riflettere le modifiche.

## 3. Requisiti Architetturali e Hardware
L'Autonomous Patching è un'operazione estremamente delicata che richiede modelli di alta precisione:
- **Modelli di Coding**: È tassativo l'uso di modelli specializzati come **Qwen 2.5 Coder** o **DeepSeek-Coder-V2** nel ruolo di `CODING SPECIALIST 1 & 2`.
- **Modello Supervisore**: È consigliato l'uso di un modello "pesante" (es. **DeepSeek-R1 8B/14B/32B**) come supervisore, capace di validare logicamente la patch.
- **Auto-Pilot Supervision**: Se attivata, la patch viene applicata in automatico senza conferma umana. Se disattivata, la dashboard richiederà un click per approvare la diff.

## 4. Git Checkpoint (Auto-Branch Evolution)
Per un livello di sicurezza superiore, il sistema di Patching si aggancia a GitHub.
Attivando l'**AUTO-BRANCH EVOLUTION**, ogni singola patch generata autonomamente dallo Sciame neurale aprirà un branch `git` isolato. L'utente potrà fare la code-review su GitHub e fare un merge, garantendo che nessun file fondamentale (es. `api.py` o `neural_lab.py`) venga distrutto irrimediabilmente.

---
*Questa documentazione traccia i limiti operativi dell'evoluzione autoguidata. Istruisci l'Oracolo e i Giudici per mantenere i permessi di sovrascrittura entro i recinti del Sovereign Perimeter.*
