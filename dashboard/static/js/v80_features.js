/**
 * 🏺 NEURALVAULT v8.0: Phase 7 Features
 * What-If Engine & Sovereign Wiki 3.0
 */

window.refreshWikiList = async () => {
    try {
        const resp = await fetch('/api/communities/list');
        const data = await resp.json();
        const container = document.getElementById('wiki-galaxies-list');
        if (!container) return;
        
        container.innerHTML = '';
        data.communities.forEach(c => {
            const div = document.createElement('div');
            div.className = 'nav-item';
            div.style.padding = '10px';
            div.style.fontSize = '0.7rem';
            div.innerHTML = `<i class="fas fa-galaxy"></i> ${c.title || 'Galassia Incompleta'}`;
            div.onclick = () => window.loadWikiPage(c.title);
            container.appendChild(div);
        });
    } catch (e) {
        console.error("Wiki List Error:", e);
    }
};

window.loadWikiPage = async (topic, mode = 'TECHNICAL') => {
    try {
        const content = document.getElementById('wiki-portal-content');
        const hud = document.getElementById('wiki-epistemic-hud');
        content.innerHTML = `<div style="text-align:center; padding:5rem;"><i class="fas fa-spinner fa-spin"></i> Inizializzazione Protocollo ${mode}...</div>`;
        
        const resp = await fetch('/api/wiki/generate', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ topic: topic, mode: mode })
        });
        const data = await resp.json();
        
        // --- 📊 Generative Multimedia (v8.1) ---
        content.innerHTML = `
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:2rem; border-bottom:1px solid rgba(255,255,255,0.05); padding-bottom:1rem;">
                <h1 id="wiki-portal-title" style="margin:0; font-size:1.5rem; letter-spacing:2px;">${data.title}</h1>
                <div class="reading-mode-selector" style="display:flex; gap:10px; background:rgba(0,0,0,0.2); padding:5px; border-radius:10px;">
                    <button onclick="window.switchWikiMode('EXECUTIVE')" style="background:${mode=='EXECUTIVE'?'#3b82f6':'transparent'}; border:none; color:#fff; font-size:0.5rem; padding:5px 10px; border-radius:5px; cursor:pointer;">⚡ EXE</button>
                    <button onclick="window.switchWikiMode('TECHNICAL')" style="background:${mode=='TECHNICAL'?'#3b82f6':'transparent'}; border:none; color:#fff; font-size:0.5rem; padding:5px 10px; border-radius:5px; cursor:pointer;">🔧 TECH</button>
                    <button onclick="window.switchWikiMode('RESEARCH')" style="background:${mode=='RESEARCH'?'#3b82f6':'transparent'}; border:none; color:#fff; font-size:0.5rem; padding:5px 10px; border-radius:5px; cursor:pointer;">🔬 RES</button>
                </div>
            </div>
            <div class="wiki-article">${data.markdown}</div>
        `;
        
        // Inizializza Mermaid per i diagrammi generati
        if (window.mermaid) {
            mermaid.init(undefined, ".mermaid");
        }
        
        // Inizializza interazioni semantiche (v8.1)
        window.initWikiInteractions();
        
        // --- 🌦️ Epistemic Weather HUD (v8.1) ---
        if (hud && data.metadata) {
            hud.style.display = 'block';
            window.renderEpistemicHUD(data.metadata);
        }
        
        window.loadWikiHistory(topic);
    } catch (e) {
        console.error("Load Wiki Error:", e);
    }
};

window.renderEpistemicHUD = (meta) => {
    const hud = document.getElementById('wiki-epistemic-hud');
    const trustScore = meta.confidence || 0.85;
    const freshScore = meta.freshness || 0.9;
    
    document.getElementById('wiki-trust-bar').style.width = (trustScore * 100) + '%';
    document.getElementById('wiki-trust-text').innerText = trustScore > 0.8 ? 'STABILE / SOLEGGIATO' : 'INCERTO / NUVOLOSO';
    
    // [v8.1] Actionable HUD Logic
    const actionContainer = document.getElementById('wiki-hud-actions');
    if (actionContainer) {
        if (trustScore < 0.7) {
            actionContainer.innerHTML = `<button onclick="window.triggerSkywalker()" style="background:#f43f5e; color:#fff; border:none; font-size:0.55rem; padding:4px 10px; border-radius:5px; cursor:pointer; font-weight:800; animation:pulse 2s infinite;">🚀 TRIGGER SKYWALKER</button>`;
        } else {
            actionContainer.innerHTML = `<button onclick="window.exportWiki()" style="background:rgba(16,185,129,0.1); color:#10b981; border:1px solid #10b981; font-size:0.55rem; padding:4px 10px; border-radius:5px; cursor:pointer;">📥 EXPORT REFERENCE</button>`;
        }
    }
    
    const icon = document.getElementById('wiki-trust-icon');
    icon.className = trustScore > 0.8 ? 'fas fa-sun' : 'fas fa-cloud-sun';
    icon.style.color = trustScore > 0.8 ? '#facc15' : '#64748b';
};

window.loadWikiHistory = async (topic) => {
    try {
        const resp = await fetch(`/api/wiki/history?topic=${encodeURIComponent(topic)}`);
        const data = await resp.json();
        const container = document.getElementById('wiki-history-list');
        if (!container) return;
        
        container.innerHTML = '';
        if (data.versions.length === 0) {
            container.innerHTML = 'Nessuna versione precedente.';
            return;
        }
        
        data.versions.forEach(v => {
            const div = document.createElement('div');
            div.style.padding = '8px';
            div.style.borderBottom = '1px solid rgba(255,255,255,0.05)';
            div.style.cursor = 'pointer';
            div.innerHTML = `<div>${v.date}</div><div style="font-size:0.5rem; opacity:0.5;">${v.preview}</div>`;
            container.appendChild(div);
        });
    } catch (e) {
        console.error("Wiki History Error:", e);
    }
};

// --- WHAT-IF ENGINE ---

let simCy = null;

window.initSimulationGraph = () => {
    if (simCy) return;
    simCy = cytoscape({
        container: document.getElementById('simulation-graph-container'),
        style: [
            { selector: 'node', style: { 'label': 'data(label)', 'color': '#fff', 'background-color': '#facc15', 'font-size': '10px' } },
            { selector: 'edge', style: { 'width': 2, 'line-color': '#444', 'target-arrow-color': '#444', 'target-arrow-shape': 'triangle', 'curve-style': 'bezier', 'label': 'data(label)', 'font-size': '8px' } }
        ]
    });
};

window.runCausalSimulation = async () => {
    const topic = document.getElementById('wiki-search-portal')?.value || "Current Context";
    const intensity = document.getElementById('sim-intensity').value;
    
    log(`🧪 [What-If] Avvio simulazione con intensità ${intensity}%...`, "#facc15");
    
    try {
        const resp = await fetch(`/api/wiki/simulate?topic=${encodeURIComponent(topic)}`);
        const data = await resp.json();
        
        window.renderSimulationResults(data);
    } catch (e) {
        console.error("Simulation Error:", e);
    }
};

window.renderSimulationResults = (data) => {
    const container = document.getElementById('simulation-results-table');
    container.innerHTML = '';
    
    // Reset Graph
    window.initSimulationGraph();
    simCy.elements().remove();
    
    data.affected_nodes.forEach((n, i) => {
        // --- 📊 [v8.1] MONTE CARLO PROBABILISTIC UI ---
        const card = document.createElement('div');
        card.className = 'glass-card';
        card.style.padding = '1.2rem';
        card.style.borderLeft = `4px solid ${n.impact > 0 ? '#4ade80' : '#ef4444'}`;
        
        const probPos = Math.round(n.probability_positive * 100);
        
        card.innerHTML = `
            <div style="display:flex; justify-content:space-between; align-items:start;">
                <div style="font-size:0.55rem; color:#8b949e;">${n.id.substring(0,8)}</div>
                <div style="font-size:0.55rem; color:${n.impact > 0 ? '#4ade80' : '#ef4444'}; font-weight:800;">
                    ${probPos}% PROBABILITY
                </div>
            </div>
            <div style="font-size:0.85rem; font-weight:800; color:#fff; margin:8px 0;">${n.title}</div>
            
            <!-- Monte Carlo Range Bar -->
            <div style="margin: 10px 0;">
                <div style="display:flex; justify-content:space-between; font-size:0.5rem; color:#64748b; margin-bottom:4px;">
                    <span>Worst: ${Math.round(n.worst_case*100)}%</span>
                    <span>Best: ${Math.round(n.best_case*100)}%</span>
                </div>
                <div style="height:6px; background:rgba(255,255,255,0.05); border-radius:10px; position:relative; overflow:hidden;">
                    <div style="position:absolute; left:${Math.max(0, (n.worst_case+1)*50)}%; width:${Math.abs(n.best_case - n.worst_case)*50}%; height:100%; background:${n.impact > 0 ? 'rgba(74,222,128,0.3)' : 'rgba(239,68,68,0.3)'};"></div>
                    <div style="position:absolute; left:${Math.max(0, (n.impact+1)*50)}%; width:2px; height:100%; background:#fff; box-shadow:0 0 10px #fff;"></div>
                </div>
            </div>

            <div style="display:flex; justify-content:space-between; align-items:center; margin-top:10px;">
                <span style="color:${n.impact > 0 ? '#4ade80' : '#ef4444'}; font-weight:900; font-size:1rem;">
                    ${n.impact > 0 ? '+' : ''}${Math.round(n.impact*100)}%
                </span>
                <span style="font-size:0.55rem; color:#8b949e;">STD: ${n.std}</span>
            </div>
        `;
        container.appendChild(card);
        
        // --- 🧪 [v8.1] SEMANTIC WIKI OVERLAY ---
        // Usiamo l'ID del nodo per un highlight preciso invece del Regex
        const entitySpan = document.querySelector(`.wiki-entity[data-node-id="${n.id}"]`);
        if (entitySpan) {
            const color = n.impact > 0 ? 'rgba(74,222,128,0.4)' : 'rgba(239,68,68,0.4)';
            const border = n.impact > 0 ? '#4ade80' : '#ef4444';
            entitySpan.style.background = color;
            entitySpan.style.borderBottom = `2px solid ${border}`;
            entitySpan.title = `Simulated Impact: ${Math.round(n.impact*100)}% (${probPos}% Prob)`;
            entitySpan.classList.add('pulse-simulation');
        }

        // Add to Graph
        simCy.add({ data: { id: n.id, label: n.title } });
        if (i > 0) {
            simCy.add({ data: { source: data.root_id, target: n.id, label: 'IMPACT' } });
        }
    });
    
    simCy.layout({ name: 'cose', animate: true }).run();
    document.getElementById('sim-affected-count').innerText = data.affected_nodes.length;
    document.getElementById('sim-confidence').innerText = "90% (MC)";
};

window.resetSimulation = () => {
    if (simCy) simCy.elements().remove();
    document.getElementById('simulation-results-table').innerHTML = '';
    document.getElementById('sim-affected-count').innerText = '0';
};

// --- [v8.1] PROGRESSIVE DISCLOSURE & ADAPTIVE PROTOCOLS ---

window.initWikiInteractions = () => {
    const entities = document.querySelectorAll('.wiki-entity');
    entities.forEach(el => {
        el.onmouseenter = (e) => window.showDisclosurePanel(e, el.dataset.nodeId);
        el.onmouseleave = () => window.hideDisclosurePanel();
    });
};

let disclosureTimer = null;
window.showDisclosurePanel = async (e, nodeId) => {
    const panel = document.getElementById('wiki-disclosure-panel');
    if (!panel) return;
    
    const rect = e.target.getBoundingClientRect();
    panel.style.top = (rect.bottom + window.scrollY + 10) + 'px';
    panel.style.left = (rect.left + window.scrollX) + 'px';
    
    panel.innerHTML = '<div style="padding:1rem; font-size:0.6rem; opacity:0.5;">Caricamento Proiezione...</div>';
    panel.style.display = 'block';
    
    try {
        const resp = await fetch(`/api/node/${nodeId}`);
        const data = await resp.json();
        
        panel.innerHTML = `
            <div style="padding:1rem; min-width:250px; max-width:350px;">
                <div style="display:flex; justify-content:space-between; margin-bottom:8px;">
                    <span style="font-size:0.5rem; color:#8b949e; text-transform:uppercase;">${data.id.substring(0,8)}</span>
                    <span style="font-size:0.5rem; color:#4ade80;">READY</span>
                </div>
                <div style="font-weight:800; font-size:0.8rem; margin-bottom:8px; color:#fff;">${data.metadata.title || 'Nodo Atomico'}</div>
                <div style="font-size:0.65rem; color:#8b949e; line-height:1.4; margin-bottom:12px;">${data.text.substring(0, 150)}...</div>
                <div style="display:flex; gap:10px;">
                    <button onclick="window.focusNebulaNode('${data.id}')" style="flex:1; background:rgba(59,130,246,0.1); border:1px solid #3b82f6; color:#3b82f6; font-size:0.55rem; padding:4px; border-radius:4px; cursor:pointer;">🌌 NEBULA</button>
                    <button onclick="window.startWikiSimulation('${data.id}')" style="flex:1; background:rgba(244,63,94,0.1); border:1px solid #f43f5e; color:#f43f5e; font-size:0.55rem; padding:4px; border-radius:4px; cursor:pointer;">🧪 WHAT-IF</button>
                </div>
            </div>
        `;
    } catch (err) {
        panel.innerHTML = '<div style="padding:1rem; color:#ef4444;">Errore Proiezione.</div>';
    }
};

window.hideDisclosurePanel = () => {
    const panel = document.getElementById('wiki-disclosure-panel');
    if (panel) panel.style.display = 'none';
};

window.focusNebulaNode = (id) => {
    window.showSection('overview');
    if (window.highlightNode) window.highlightNode(id);
};

window.startWikiSimulation = (id) => {
    window.showSection('simulation');
    document.getElementById('wiki-search-portal').value = id;
    window.runCausalSimulation();
};

window.switchWikiMode = async (mode) => {
    const currentTopic = document.getElementById('wiki-portal-title')?.innerText || "Summary";
    log(`🔄 [v8.1] Switching to ${mode} mode...`, "#3b82f6");
    window.loadWikiPage(currentTopic, mode);
};
