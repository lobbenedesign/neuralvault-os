/**
 * 🏺 NeuralVault v5.1 Alpha: Limbo Governance & Intelligence
 * Manages nodes in WASTE_PENDING state with AI-driven evaluation.
 */

window.refreshLimboList = async () => {
    const container = document.getElementById('limbo-container');
    if (!container) return;

    container.innerHTML = `<div style="grid-column: 1/-1; text-align: center; padding: 3rem; color: #facc15;"><i class="fas fa-spinner fa-spin"></i> Sincronizzazione Limbo...</div>`;

    try {
        const r = await fetch('/api/limbo/list', {
            headers: { 'X-API-KEY': VAULT_KEY }
        });
        const data = await r.json();

        if (!data.nodes || data.nodes.length === 0) {
            container.innerHTML = `
                <div style="grid-column: 1/-1; text-align: center; padding: 3rem; color: #64748b; font-size: 0.7rem; border: 1px dashed rgba(255,255,255,0.1); border-radius: 12px;">
                    <i class="fas fa-box-open" style="font-size: 2rem; margin-bottom: 1rem; display: block; opacity: 0.3;"></i>
                    Limbo Vuoto. Nessuna traccia di frammenti in decadimento.
                    <br><p style="margin-top:10px; opacity:0.6;">L'oblio è sereno. Il sistema è in equilibrio semantico perfetto.</p>
                </div>
            `;
            return;
        }

        container.innerHTML = data.nodes.map(node => {
            const decayDate = node.decayed_at ? new Date(node.decayed_at * 1000).toLocaleString() : "Data ignota";
            const safeText = node.text || "Nessun contenuto rilevato.";
            
            return `
            <div id="limbo-card-${node.id}" class="glass-card" style="padding: 1.5rem; border: 1px solid rgba(250,204,21,0.2); border-left: 4px solid #facc15; background: rgba(0,0,0,0.2); display: flex; flex-direction: column; gap: 12px; transition: 0.3s;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-size: 0.6rem; color: #facc15; font-weight: 800;">ID: ${node.id.slice(0, 8)}</span>
                    <span style="font-size: 0.5rem; color: #8b949e;">DECAY: ${decayDate}</span>
                </div>
                
                <div style="font-size: 0.75rem; color: #e2e8f0; line-height: 1.5; max-height: 120px; overflow-y: auto; background: rgba(0,0,0,0.3); padding: 10px; border-radius: 8px;">
                    ${safeText}
                </div>

                <div id="eval-${node.id}" style="font-size: 0.65rem; color: #8b949e; padding: 10px; border-radius: 8px; background: rgba(255,255,255,0.02); min-height: 40px; display: flex; align-items: center; justify-content: center;">
                    <button onclick="evaluateLimboNode('${node.id}')" style="background: none; border: 1px solid rgba(255,255,255,0.2); color: #fff; font-size: 0.55rem; padding: 4px 10px; border-radius: 6px; cursor: pointer;">🔍 CHIEDI VALUTAZIONE IA</button>
                </div>

                <div style="display: flex; flex-wrap: wrap; gap: 8px; margin-top: 10px;">
                    <button onclick="restoreLimboNode('${node.id}')" class="evo-btn btn-green" style="flex: 1; min-width: 100px;"><i class="fas fa-redo"></i> RIPRISTINA</button>
                    <button onclick="window.mergeLimboNode('${node.id}')" class="evo-btn" style="flex: 1; min-width: 100px; background: rgba(168, 85, 247, 0.2); border: 1px solid #a855f7; color: #fff;"><i class="fas fa-object-group"></i> FONDERE (MERGE)</button>
                    <button onclick="purgeLimboNode('${node.id}')" class="evo-btn btn-red" style="flex: 1; min-width: 100px;"><i class="fas fa-trash-alt"></i> ELIMINA</button>
                </div>
            </div>
        `;
        }).join('');

    } catch (e) {
        container.innerHTML = `<div style="grid-column: 1/-1; color: #ef4444; text-align: center;">Errore nel caricamento del Limbo.</div>`;
    }
};

window.evaluateLimboNode = async (id) => {
    const evalDiv = document.getElementById(`eval-${id}`);
    evalDiv.innerHTML = `<i class="fas fa-robot fa-spin"></i> Analisi semantica in corso...`;

    try {
        const r = await fetch(`/api/limbo/evaluate/${id}`, {
            method: 'POST',
            headers: { 'X-API-KEY': VAULT_KEY }
        });
        const data = await r.json();

        const colors = { 'GREEN': '#10b981', 'YELLOW': '#f59e0b', 'RED': '#ef4444' };
        const color = colors[data.recommendation] || '#fff';

        evalDiv.style.border = `1px solid ${color}33`;
        evalDiv.style.background = `${color}0D`;
        evalDiv.innerHTML = `
            <div>
                <div style="color: ${color}; font-weight: 900; margin-bottom: 4px; display: flex; align-items: center; gap: 8px;">
                    <span style="width: 10px; height: 10px; border-radius: 50%; background: ${color}; box-shadow: 0 0 10px ${color};"></span>
                    ${data.recommendation}
                </div>
                <div style="color: #cbd5e1; font-style: italic;">"${data.reason}"</div>
            </div>
        `;
    } catch (e) {
        evalDiv.innerHTML = `<span style="color: #ef4444;">Valutazione fallita.</span>`;
    }
};

window.restoreLimboNode = async (id) => {
    try {
        const r = await fetch(`/api/limbo/restore/${id}`, {
            method: 'POST',
            headers: { 'X-API-KEY': VAULT_KEY }
        });
        if (r.ok) {
            document.getElementById(`limbo-card-${id}`).style.transform = 'scale(0.8)';
            document.getElementById(`limbo-card-${id}`).style.opacity = '0';
            setTimeout(() => window.refreshLimboList(), 300);
            log(`♻️ NODE_RESTORED: ${id.slice(0,8)} reintegrato nella RAM attiva.`, '#10b981');
        }
    } catch (e) { console.error(e); }
};

window.purgeLimboNode = async (id) => {
    if (!confirm("Questa azione è irreversibile. Confermi l'eliminazione fisica del nodo?")) return;
    try {
        const r = await fetch(`/api/limbo/purge/${id}`, {
            method: 'DELETE',
            headers: { 'X-API-KEY': VAULT_KEY }
        });
        if (r.ok) {
            document.getElementById(`limbo-card-${id}`).style.transform = 'scale(0.8)';
            document.getElementById(`limbo-card-${id}`).style.opacity = '0';
            setTimeout(() => window.refreshLimboList(), 300);
            log(`🗑️ NODE_PURGED: ${id.slice(0,8)} eliminato fisicamente dal disco.`, '#ef4444');
        }
    } catch (e) { console.error(e); }
};

window.mergeLimboNode = async (id) => {
    const target = prompt("Specifica il concetto o ID del nodo target verso cui fondere questa conoscenza (es: 'Python Strings', 'Quantum Physics'):");
    if (!target) return;

    try {
        log(`🧠 [v5.1] Inizio procedura di fusione (Merge) per il nodo ${id.slice(0,8)}...`, "#a855f7");
        const r = await fetch(`/api/limbo/merge/${id}`, {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                'X-API-KEY': VAULT_KEY 
            },
            body: JSON.stringify({ target_concept: target })
        });
        
        const data = await r.json();
        if (r.ok) {
            document.getElementById(`limbo-card-${id}`).style.transform = 'scale(0.8) rotate(-5deg)';
            document.getElementById(`limbo-card-${id}`).style.opacity = '0';
            setTimeout(() => window.refreshLimboList(), 400);
            log(`🔮 NODE_MERGED: ${id.slice(0,8)} fuso con successo in '${target}'.`, '#a855f7');
        } else {
            alert("Errore durante la fusione: " + (data.error || "Sconosciuto"));
        }
    } catch (e) { 
        console.error(e);
        alert("Fallimento critico nella pipeline di fusione.");
    }
};
