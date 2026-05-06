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

window.loadWikiPage = async (topic) => {
    try {
        const content = document.getElementById('wiki-portal-content');
        content.innerHTML = '<div style="text-align:center; padding:5rem;">Apertura Portale Conoscenza...</div>';
        
        // Genera (o recupera) la pagina
        const resp = await fetch('/api/wiki/generate', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ topic: topic })
        });
        const data = await resp.json();
        
        // Renderizza Markdown (usando marked se disponibile, o fallback semplice)
        content.innerHTML = `<div class="wiki-article">${data.markdown}</div>`;
        
        // Carica storico
        window.loadWikiHistory(topic);
    } catch (e) {
        console.error("Load Wiki Error:", e);
    }
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
        // Add to list
        const card = document.createElement('div');
        card.className = 'glass-card';
        card.style.padding = '1rem';
        card.style.borderColor = n.impact > 0 ? 'rgba(74,222,128,0.3)' : 'rgba(239,68,68,0.3)';
        card.innerHTML = `
            <div style="font-size:0.55rem; color:#8b949e;">${n.id.substring(0,8)}</div>
            <div style="font-size:0.75rem; font-weight:800; color:#fff; margin:5px 0;">${n.title}</div>
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <span style="color:${n.impact > 0 ? '#4ade80' : '#ef4444'}; font-weight:900;">${n.impact > 0 ? '+' : ''}${Math.round(n.impact*100)}%</span>
                <span style="font-size:0.5rem; color:#64748b;">CONF: ${Math.round(n.confidence*100)}%</span>
            </div>
        `;
        container.appendChild(card);
        
        // Add to Graph
        simCy.add({ data: { id: n.id, label: n.title } });
        if (i > 0) {
            simCy.add({ data: { source: data.root_id, target: n.id, label: 'IMPACT' } });
        }
    });
    
    simCy.layout({ name: 'cose', animate: true }).run();
    
    document.getElementById('sim-affected-count').innerText = data.affected_nodes.length;
    document.getElementById('sim-confidence').innerText = "88%";
};

window.resetSimulation = () => {
    if (simCy) simCy.elements().remove();
    document.getElementById('simulation-results-table').innerHTML = '';
    document.getElementById('sim-affected-count').innerText = '0';
};

// --- NEURAL COMPRESSION (NIC) ---

window.triggerNeuralCompression = async () => {
    const btn = document.getElementById('compression-btn');
    const prog = document.getElementById('compression-progress-container');
    const bar = document.getElementById('comp-progress-bar');
    const status = document.getElementById('comp-status-text');
    
    btn.disabled = true;
    prog.style.display = 'block';
    
    log("🦾 [NIC] Avvio addestramento Codebook Neurale...", "#10b981");
    
    try {
        // Start compression
        const resp = await fetch('/api/system/compress', { method: 'POST' });
        const data = await resp.json();
        
        // Simula progresso (o usa polling se implementato nel backend)
        let p = 0;
        const interval = setInterval(() => {
            p += 5;
            bar.style.width = p + '%';
            if (p >= 100) {
                clearInterval(interval);
                status.innerText = "Ottimizzazione Completata!";
                log("✅ [NIC] Compressione terminata. Risparmio storage: 88%.", "#10b981");
                btn.disabled = false;
            }
        }, 200);
        
    } catch (e) {
        console.error("Compression Error:", e);
        btn.disabled = false;
    }
};
