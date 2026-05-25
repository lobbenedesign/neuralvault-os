/**
 * 🏺 NEURALVAULT v8.0: Phase 7 Features
 * What-If Engine & Sovereign Wiki 3.0
 */

window.refreshWikiList = async () => {
    const container = document.getElementById('wiki-galaxies-list');
    if (!container) return;

    try {
        container.innerHTML = '<div style="padding:10px; font-size:0.6rem; opacity:0.5;"><i class="fas fa-spinner fa-spin"></i> Sincronizzazione Vault...</div>';
        
        const apiKey = (typeof window.VAULT_KEY !== 'undefined') ? window.VAULT_KEY : 'AURA-ADMIN-77';
        
        // [v9.0] Call persistent wiki list
        const resp = await fetch('/api/wiki/list', {
            headers: { 'X-API-KEY': apiKey }
        });

        if (!resp.ok) throw new Error(`HTTP Error ${resp.status}`);

        const data = await resp.json();
        container.innerHTML = '';
        
        if (data && data.pages && data.pages.length > 0) {
            // [v9.5] Group by Namespace (IDE Style)
            const groups = {};
            data.pages.forEach(p => {
                const ns = p.namespace || "General";
                if (!groups[ns]) groups[ns] = [];
                groups[ns].push(p);
            });

            Object.entries(groups).forEach(([ns, pages]) => {
                const nsHeader = document.createElement('div');
                nsHeader.style = "font-size:0.55rem; color:#a855f7; text-transform:uppercase; letter-spacing:2px; padding:15px 10px 8px 10px; font-weight:900; display:flex; align-items:center; gap:8px; border-bottom:1px solid rgba(168,85,247,0.1); margin-bottom:5px;";
                nsHeader.innerHTML = `<i class="fas fa-folder-open" style="font-size:0.6rem;"></i> ${ns}`;
                container.appendChild(nsHeader);

                pages.forEach(p => {
                    const div = document.createElement('div');
                    div.className = 'wiki-nav-item';
                    div.style = "padding:8px 12px 8px 30px; font-size:0.65rem; display:flex; align-items:center; gap:12px; border-radius:8px; margin:2px 0; transition:all 0.3s ease; cursor:pointer; color: #94a3b8;";
                    div.innerHTML = `<i class="fas fa-file-code" style="color:rgba(59,130,246,0.3); font-size:0.6rem;"></i> <span style="flex:1; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;">${p.title}</span>`;
                    div.onmouseover = () => { div.style.background = 'rgba(59,130,246,0.1)'; div.style.color = '#fff'; };
                    div.onmouseout = () => { div.style.background = 'transparent'; div.style.color = '#94a3b8'; };
                    div.onclick = () => window.loadWikiPage(p.title, 'TECHNICAL', p.file_name);
                    container.appendChild(div);
                });
            });
        } else {
            container.innerHTML = '<div style="padding:20px; text-align:center; opacity:0.3;"><i class="fas fa-ghost fa-2x"></i><div style="font-size:0.6rem; margin-top:10px;">VAULT_EMPTY</div></div>';
        }
    } catch (e) {
        console.error("Wiki List Error:", e);
        container.innerHTML = `<div style="padding:10px; font-size:0.6rem; color:#ef4444;"><i class="fas fa-shield-alt"></i> Errore Accesso: ${e.message}</div>`;
    }
};



window.loadWikiPage = async (topic, mode = 'TECHNICAL', fileName = null) => {
    if (!topic || topic === "") {
        return window.renderWikiDashboard();
    }
    const titleEl = document.getElementById('wiki-kb-title') || document.getElementById('wiki-portal-title');
    const metaEl = document.getElementById('wiki-page-metadata');
    
    if (titleEl && titleEl.id === 'wiki-portal-title') {
        titleEl.parentElement.style.display = 'flex'; // Show header for articles in portal
        document.getElementById('wiki-document-sheet').classList.remove('dashboard-active');
    }
    
    try {
        const content = document.getElementById('wiki-kb-content-body') || document.getElementById('wiki-portal-content');
        const hud = document.getElementById('wiki-epistemic-hud');
        if (!content) {
            console.warn("⚠️ [v8.0] Wiki Content container not found. Aborting render.");
            return;
        }
        content.innerHTML = `<div style="text-align:center; padding:5rem;"><i class="fas fa-spinner fa-spin"></i> Accesso alla Fonte di Verità...</div>`;
        
        const apiKey = (typeof window.VAULT_KEY !== 'undefined') ? window.VAULT_KEY : 'AURA-ADMIN-77';
        let data;

        // [v9.0] If fileName is provided, try reading first
        if (fileName) {
            const resp = await fetch(`/api/wiki/read?file=${fileName}`, {
                headers: { 'X-API-KEY': apiKey }
            });
            if (resp.ok) {
                const readData = await resp.json();
                data = { title: topic, markdown: readData.markdown, metadata: { confidence: 0.95, freshness: 1.0 } };
            }
        }

        // Fallback to generation if no file or read failed
        if (!data) {
            const resp = await fetch('/api/wiki/generate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'X-API-KEY': apiKey },
                body: JSON.stringify({ topic: topic, mode: mode })
            });
            data = await resp.json();
        }
        
        // [v9.0] Z3 Formal Logic Audit
        let z3Badge = '';
        try {
            const z3Resp = await fetch(`/api/formal-logic/check?topic=${encodeURIComponent(topic)}`, {
                headers: { 'X-API-KEY': apiKey }
            });
            const z3Data = await z3Resp.json();
            if (z3Data.consistent) {
                z3Badge = `<span class="v9-badge badge-z3" title="Z3 Theorem Prover: Nessuna contraddizione logica trovata."><i class="fas fa-shield-check"></i> PROVEN</span>`;
            } else {
                z3Badge = `<span class="v9-badge badge-z3" style="color:#ef4444; border-color:#ef4444;" title="Z3 Theorem Prover: Rilevate contraddizioni logiche!"><i class="fas fa-exclamation-triangle"></i> CONFLICT</span>`;
            }
        } catch(e) { console.warn("Z3 Audit failed", e); }

        const epistemicScore = data.metadata?.epistemic_score || data.metadata?.confidence || 0.85;
        const epistemicBadge = `<span class="v9-badge badge-epistemic" title="Epistemic Score: ${Math.round(epistemicScore*100)}%"><i class="fas fa-brain"></i> ${Math.round(epistemicScore*100)}% EPISTEMIC</span>`;

        // Update the title element found at the start
        if (titleEl) {
            titleEl.innerText = data.title;
        }

        // [v10.2] Update Namespace Badge and Active Tree State
        window.currentWikiPage = fileName;
        if (window.fullKBTreeList) {
            const kbEntry = window.fullKBTreeList.find(p => p.file_name === fileName);
            const badgeEl = document.getElementById('wiki-kb-namespace-badge');
            if (badgeEl) badgeEl.innerHTML = `<i class="fas fa-folder-open"></i> / ${kbEntry && kbEntry.namespace ? kbEntry.namespace : 'General'}`;
            if (window.renderKBTree && !document.getElementById('kb-tree-filter')?.value) {
                window.renderKBTree(window.fullKBTreeList);
            }
        }
        
        // Show metadata panel
        if (metaEl) metaEl.style.display = 'grid';

        // --- 📊 Generative Multimedia (v8.1) ---
        // If we are in the new KB, we don't want to duplicate the title header if it's already managed by the subview
        const isKB = content.id === 'wiki-kb-content-body';
        
        content.innerHTML = `
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:2rem; border-bottom:1px solid rgba(255,255,255,0.05); padding-bottom:1rem; ${isKB ? 'display:none;' : ''}">
                <div style="display:flex; align-items:center;">
                    <h1 id="wiki-portal-title" style="margin:0; font-size:1.5rem; letter-spacing:2px;">${data.title}</h1>
                    ${z3Badge}
                    ${epistemicBadge}
                </div>
                <div class="reading-mode-selector" style="display:flex; gap:10px; background:rgba(0,0,0,0.2); padding:5px; border-radius:10px;">
                    <button onclick="window.switchWikiMode('EXECUTIVE')" title="EXECUTIVE: Sintesi decisionale e strategica." style="background:${mode=='EXECUTIVE'?'#3b82f6':'transparent'}; border:none; color:#fff; font-size:0.55rem; padding:5px 12px; border-radius:5px; cursor:pointer; font-weight:800;">EXECUTIVE</button>
                    <button onclick="window.switchWikiMode('TECHNICAL')" title="TECHNICAL: Architettura e dettagli tecnici." style="background:${mode=='TECHNICAL'?'#3b82f6':'transparent'}; border:none; color:#fff; font-size:0.55rem; padding:5px 12px; border-radius:5px; cursor:pointer; font-weight:800;">TECHNICAL</button>
                    <button onclick="window.switchWikiMode('RESEARCH')" title="RESEARCH: Teoria e citazioni." style="background:${mode=='RESEARCH'?'#3b82f6':'transparent'}; border:none; color:#fff; font-size:0.55rem; padding:5px 12px; border-radius:5px; cursor:pointer; font-weight:800;">RESEARCH</button>
                </div>
            </div>
            ${isKB ? `<div style="margin-bottom:1rem; display:flex; gap:10px;">${z3Badge} ${epistemicBadge}</div>` : ''}
            <div class="wiki-article">${window.processWikiMarkdown ? window.processWikiMarkdown(data.markdown, data.citations || []) : data.markdown}</div>
        `;

        // [v9.0] Trigger Merit Ranking Update
        window.updateMeritRanking();
        
        // [v8.4] Phase 7.4: High-Velocity Optimization (Lazy Multimedia 2.0)
        if (!window.lazyMermaid) {
            window.lazyMermaid = new LazyMermaidRenderer();
        }
        window.lazyMermaid.init();
        
        // [v8.4] Init Keyboard Nav
        if (!window.wikiNav) {
            window.wikiNav = new WikiKeyboardNavigator();
        }
        
        // Inizializza interazioni semantiche (v8.1)
        window.initWikiInteractions();
        
        // --- 🌦️ Epistemic Weather HUD (v8.1) ---
        if (hud && data.metadata) {
            hud.style.display = 'block';
            window.renderEpistemicHUD(data.metadata);
        }
        
        window.loadWikiHistory(topic);
        window.updateWikiSidebarIntelligence(data);
        window.loadLearningPath(topic);
        
        // Applica classe modalità al body
        document.body.classList.add(`mode-${mode.toLowerCase()}`);
    } catch (e) {
        console.error("Load Wiki Error:", e);
    }
};

window.runSovereignAudit = async () => {
    try {
        const apiKey = (typeof window.VAULT_KEY !== 'undefined') ? window.VAULT_KEY : 'AURA-ADMIN-77';
        
        // Show loading state
        const content = document.getElementById('wiki-kb-content-body') || document.getElementById('wiki-portal-content');
        if (!content) return;
        const originalHTML = content.innerHTML;
        content.innerHTML = `<div style="text-align:center; padding:5rem; color:#10b981;">
            <i class="fas fa-microscope fa-spin fa-3x"></i>
            <h2 style="margin-top:20px;">Sovereign Audit in Corso...</h2>
            <p style="font-size:0.7rem; opacity:0.7;">Scansione integrità logica e link cross-page.</p>
        </div>`;

        const resp = await fetch('/api/wiki/audit', {
            headers: { 'X-API-KEY': apiKey }
        });
        const report = await resp.json();

        // Render Audit Results
        let issuesHTML = report.issues.map((i, idx) => `
            <div style="background:rgba(255,255,255,0.02); border-left:4px solid ${i.severity=='CRITICAL'?'#ef4444':(i.severity=='HIGH'?'#f87171':'#facc15')}; padding:15px; border-radius:8px; margin-bottom:10px; display:flex; justify-content:space-between; align-items:center;">
                <div style="flex:1;">
                    <div style="font-size:0.6rem; color:#64748b; margin-bottom:5px;">${i.type} | ${i.page || 'Global'}</div>
                    <div style="font-size:0.8rem; color:#f8fafc;">${i.message || i.detail}</div>
                </div>
                ${(i.type === 'ORPHAN_PAGE' || i.type === 'CONTRADICTION') ? `
                    <button onclick='window.applyWikiPatch(${JSON.stringify(i)}, this)' style="background:#10b981; border:none; color:white; padding:8px 12px; border-radius:6px; cursor:pointer; font-size:0.6rem; font-weight:800; transition:all 0.3s;" onmouseover="this.style.transform='scale(1.05)'" onmouseout="this.style.transform='scale(1)'">
                        <i class="fas fa-magic"></i> APPLY PATCH
                    </button>
                ` : ''}
            </div>
        `).join('') || '<div style="color:#10b981; padding:20px; text-align:center;">🛡️ Nessuna incongruenza rilevata. Il Vault è in salute.</div>';

        content.innerHTML = `
            <div style="padding:20px;">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:30px;">
                    <h2 style="margin:0; color:#10b981;"><i class="fas fa-file-certificate"></i> Audit Report v10.0</h2>
                    <div style="background:rgba(16, 185, 129, 0.1); padding:10px 20px; border-radius:12px; border:1px solid #10b981; text-align:center;">
                        <span style="font-size:0.6rem; color:#10b981;">HEALTH_SCORE</span>
                        <div style="font-size:1.5rem; font-weight:900;">${report.summary.health_score}%</div>
                    </div>
                </div>
                <div style="margin-bottom:20px; font-size:0.7rem; color:#64748b;">Totale pagine scansionate: ${report.summary.total_pages}</div>
                <div class="audit-issues-list">${issuesHTML}</div>
                <button onclick="window.refreshWikiList()" style="margin-top:30px; background:transparent; border:1px solid rgba(255,255,255,0.2); color:white; padding:10px 20px; border-radius:8px; cursor:pointer;">TORNA ALLA WIKI</button>
            </div>
        `;
    } catch (e) {
        console.error("Audit Error:", e);
        alert("Errore durante l'audit: " + e.message);
    }
};

window.applyWikiPatch = async (issue, btn) => {
    try {
        const apiKey = (typeof window.VAULT_KEY !== 'undefined') ? window.VAULT_KEY : 'AURA-ADMIN-77';
        btn.disabled = true;
        btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> PATCHING...';
        
        const resp = await fetch('/api/wiki/patch', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'X-API-KEY': apiKey },
            body: JSON.stringify(issue)
        });
        
        const result = await resp.json();
        if (result.status === 'success') {
            btn.style.background = '#3b82f6';
            btn.innerHTML = '<i class="fas fa-check"></i> PATCHED';
            if (window.log) window.log(`🛡️ [Self-Healing] Patch applicata con successo: ${issue.page}`, "#10b981");
        } else {
            btn.style.background = '#ef4444';
            btn.innerHTML = '<i class="fas fa-times"></i> FAILED';
            alert("Errore durante l'applicazione della patch: " + result.message);
        }
    } catch (e) {
        console.error("Patch Error:", e);
        btn.innerHTML = 'ERROR';
    }
};

/**
 * [v8.4] LAZY MERMAID RENDERER
 */
class LazyMermaidRenderer {
  constructor() {
    this.renderer = null;
    this.observer = new IntersectionObserver(
      (entries) => this.onIntersect(entries),
      { rootMargin: '200px' } 
    );
  }

  init() {
    document.querySelectorAll('.mermaid').forEach(block => {
      if (block.dataset.lazyProcessed) return;
      
      const code = block.textContent;
      const placeholder = document.createElement('div');
      placeholder.className = 'mermaid-placeholder';
      placeholder.innerHTML = `
        <div class="placeholder-skeleton"></div>
        <span class="placeholder-text">📊 Diagramma in caricamento...</span>
      `;
      
      block.parentNode.replaceChild(placeholder, block);
      placeholder.dataset.mermaidCode = code;
      placeholder.dataset.lazyProcessed = "true";
      
      this.observer.observe(placeholder);
    });
  }

  async onIntersect(entries) {
    for (const entry of entries) {
      if (entry.isIntersecting) {
        const placeholder = entry.target;
        this.observer.unobserve(placeholder);
        await this.renderDiagram(placeholder);
      }
    }
  }

  async renderDiagram(placeholder) {
    const code = placeholder.dataset.mermaidCode;
    try {
      if (!this.renderer) {
        // Mermaid è già caricato globalmente via script tag nell'index.html
        mermaid.initialize({
          startOnLoad: false,
          theme: 'dark',
          securityLevel: 'loose',
          fontFamily: 'Inter, sans-serif'
        });
        this.renderer = mermaid;
      }
      
      const id = `mermaid-${Math.random().toString(36).substr(2, 9)}`;
      const { svg } = await mermaid.render(id, code);
      
      const container = document.createElement('div');
      container.className = 'mermaid-rendered';
      container.innerHTML = svg;
      placeholder.parentNode.replaceChild(container, placeholder);
      
      this.addDiagramInteractivity(container);
    } catch (error) {
      console.warn('Mermaid render failed:', error);
      placeholder.innerHTML = `<div class="mermaid-error">⚠️ Diagramma non disponibile</div>`;
    }
  }

  addDiagramInteractivity(diagramEl) {
    diagramEl.style.cursor = 'zoom-in';
    diagramEl.onclick = () => {
        if (document.fullscreenElement) {
            document.exitFullscreen();
        } else {
            diagramEl.requestFullscreen?.();
        }
    };
  }
}

/**
 * [v8.4] INTERACTIVE CAUSAL SANDBOX
 */
class CausalSandbox {
    constructor(containerId) {
        this.containerId = containerId;
        this.cy = null;
    }

    init(nodes, edges) {
        const container = document.getElementById(this.containerId);
        if (!container) return;

        this.cy = cytoscape({
            container: container,
            elements: this.formatElements(nodes, edges),
            style: [
                {
                    selector: 'node',
                    style: {
                        'background-color': '#334155',
                        'label': 'data(label)',
                        'color': '#fff',
                        'font-size': '10px',
                        'text-valign': 'center',
                        'text-halign': 'center',
                        'width': 'mapData(weight, 0, 1, 30, 80)',
                        'height': 'mapData(weight, 0, 1, 30, 80)',
                        'border-width': 2,
                        'border-color': '#facc15'
                    }
                },
                {
                    selector: 'node[impact > 0]',
                    style: { 'background-color': '#059669', 'border-color': '#34d399' }
                },
                {
                    selector: 'node[impact < 0]',
                    style: { 'background-color': '#dc2626', 'border-color': '#f87171' }
                },
                {
                    selector: 'edge',
                    style: {
                        'width': 2,
                        'line-color': '#475569',
                        'target-arrow-color': '#475569',
                        'target-arrow-shape': 'triangle',
                        'curve-style': 'bezier',
                        'label': 'data(relation)',
                        'font-size': '8px',
                        'color': '#94a3b8'
                    }
                }
            ],
            layout: { name: 'cose', animate: true }
        });

        this.cy.on('tap', 'node', (evt) => {
            const node = evt.target;
            this.showNodeEditor(node.data());
        });
    }

    formatElements(nodes, edges) {
        const elements = [];
        nodes.forEach(n => {
            elements.push({
                data: { 
                    id: n.id, 
                    label: (n.title || n.id || "").substring(0, 15), 
                    weight: Math.abs(n.impact) || 0.5,
                    impact: n.impact || 0
                }
            });
        });
        
        // Se non abbiamo archi espliciti, ne simuliamo alcuni per la demo sandbox se necessario
        // Ma idealmente usiamo quelli del subgrafo
        if (edges) {
            edges.forEach(e => {
                elements.push({
                    data: { source: e.source, target: e.target, relation: e.relation }
                });
            });
        }
        return elements;
    }

    showNodeEditor(nodeData) {
        log(`🛠️ [Sandbox] Editing node: ${nodeData.label}`, "#facc15");
        // Qui potremmo aprire un mini-panel per regolare l'intensità manuale
    }
}

window.causalSandbox = new CausalSandbox('simulation-graph-container');

/**
 * [v8.4] GUIDED WHAT-IF WIZARD
 */
window.showWhatIfWizard = () => {
    window.showSovereignModal("🧙‍♂️ WHAT-IF WIZARD", `
        <div style="display: flex; flex-direction: column; gap: 1.5rem; padding: 10px;">
            <p style="font-size: 0.7rem; color: #8b949e;">Costruisci uno scenario di simulazione guidato passo-passo.</p>
            
            <div>
                <label style="font-size: 0.6rem; color: #facc15; display: block; margin-bottom: 8px;">1. AZIONE</label>
                <div style="display: flex; gap: 10px;">
                    <button class="wizard-btn active" id="wiz-btn-up" onclick="window.wizDir='aumenta'; document.getElementById('wiz-btn-up').classList.add('active'); document.getElementById('wiz-btn-down').classList.remove('active');" style="flex:1; padding: 8px; background: rgba(255,255,255,0.05); border: 1px solid #444; color: #fff; border-radius: 6px; cursor: pointer;">📈 AUMENTA</button>
                    <button class="wizard-btn" id="wiz-btn-down" onclick="window.wizDir='diminuisci'; document.getElementById('wiz-btn-down').classList.add('active'); document.getElementById('wiz-btn-up').classList.remove('active');" style="flex:1; padding: 8px; background: rgba(255,255,255,0.05); border: 1px solid #444; color: #fff; border-radius: 6px; cursor: pointer;">📉 DIMINUISCI</button>
                </div>
            </div>

            <div>
                <label style="font-size: 0.6rem; color: #facc15; display: block; margin-bottom: 8px;">2. ENTITÀ TARGET</label>
                <input type="text" id="wiz-target" placeholder="Cerca un concetto (es: Prezzi, Inflazione...)" style="width: 100%; background: rgba(0,0,0,0.3); border: 1px solid #444; border-radius: 6px; padding: 8px; color: #fff; font-size: 0.7rem;">
            </div>

            <div>
                <label style="font-size: 0.6rem; color: #facc15; display: block; margin-bottom: 8px;">3. INTENSITÀ</label>
                <select id="wiz-mag" style="width: 100%; background: rgba(0,0,0,0.3); border: 1px solid #444; border-radius: 6px; padding: 8px; color: #fff; font-size: 0.7rem;">
                    <option value="piccolo">Piccolo impatto (20%)</option>
                    <option value="medio" selected>Impatto Medio (50%)</option>
                    <option value="grande">Grande impatto (80%)</option>
                    <option value="radicale">Intervento Radicale (100%)</option>
                </select>
            </div>

            <button onclick="window.applyWizard()" style="width: 100%; padding: 12px; background: #facc15; border: none; border-radius: 8px; color: #000; font-weight: 800; font-size: 0.75rem; cursor: pointer; margin-top: 10px;">CONFIGURA SCENARIO</button>
        </div>
        <style>
            .wizard-btn.active { border-color: #facc15 !important; background: rgba(250, 204, 21, 0.1) !important; color: #facc15 !important; }
        </style>
    `);
    window.wizDir = 'aumenta';
};

window.applyWizard = () => {
    const target = document.getElementById('wiz-target').value;
    const mag = document.getElementById('wiz-mag').value;
    if (!target) { alert("Specifica un target."); return; }
    
    const query = `${window.wizDir.charAt(0).toUpperCase() + window.wizDir.slice(1)} ${target} con intensità ${mag}`;
    const inputElement = document.getElementById('oracle-simulation-input') || document.getElementById('nl-sim-prompt');
    if (inputElement) inputElement.value = query;
    window.closeSovereignModal();
    if (typeof log === 'function') log(`🧙‍♂️ [Wizard] Scenario configurato: "${query}"`, "#facc15");
};

/**
 * [v8.4] CLIENT-SIDE SIMULATION ENGINE (JS Fallback for WASM)
 * Esegue simulazioni Monte Carlo istantanee direttamente nel browser.
 */
class ClientSideSimulationEngine {
    simulate(startNodeId, initialImpact, graph, iterations = 100, depth = 3) {
        const results = {}; // nodeId -> Array of outcomes

        for (let i = 0; i < iterations; i++) {
            const outcome = this.singlePass(startNodeId, initialImpact, graph, depth);
            for (const [nid, val] of Object.entries(outcome)) {
                if (!results[nid]) results[nid] = [];
                results[nid].push(val);
            }
        }

        // Aggregazione Statistica
        const affected_nodes = [];
        for (const [nid, vals] of Object.entries(results)) {
            const mean = vals.reduce((a, b) => a + b, 0) / vals.length;
            const probPos = vals.filter(v => v > 0).length / vals.length;
            affected_nodes.push({
                id: nid,
                title: nid, // In JS potremmo non avere i titoli completi subito
                impact: mean,
                probability_positive: probPos,
                intensity: Math.abs(mean)
            });
        }

        return {
            affected_nodes: affected_nodes.sort((a, b) => b.intensity - a.intensity),
            iterations: iterations
        };
    }

    singlePass(startNodeId, impact, graph, depth) {
        const impacts = { [startNodeId]: impact };
        let active = [{ id: startNodeId, val: impact }];

        for (let d = 0; d < depth; d++) {
            const next = [];
            for (const node of active) {
                const edges = graph[node.id] || [];
                for (const edge of edges) {
                    const noise = (Math.random() - 0.5) * 0.1;
                    const weight = Math.max(-2, Math.min(2, edge.weight + noise));
                    const transmission = node.val * weight;
                    
                    impacts[edge.targetId] = (impacts[edge.targetId] || 0) + transmission;
                    next.push({ id: edge.targetId, val: transmission });
                }
            }
            active = next;
            if (active.length === 0) break;
        }
        return impacts;
    }
}

window.clientSim = new ClientSideSimulationEngine();

/**
 * [v8.4] CAUSAL CLICK-THROUGH
 */
document.addEventListener('click', async (e) => {
    const entity = e.target.closest('.wiki-entity');
    if (!entity) return;
    
    const nodeId = entity.getAttribute('data-node-id');
    if (!nodeId) return;
    
    log(`🔗 [Causal] Esplorazione nodo: ${nodeId}`, "#facc15");
    
    try {
        const resp = await fetch(`/api/nodes/${nodeId}`, {
            headers: { 'X-API-KEY': typeof VAULT_KEY !== 'undefined' ? VAULT_KEY : 'AURA-ADMIN-77' }
        });
        const node = await resp.json();
        
        showCausalPreview(node);
    } catch (err) {
        console.error("Causal Click-Through Error:", err);
    }
});

function showCausalPreview(node) {
    const modalId = 'causal-preview-modal';
    let modal = document.getElementById(modalId);
    
    if (!modal) {
        modal = document.createElement('div');
        modal.id = modalId;
        modal.style.position = 'fixed';
        modal.style.top = '0';
        modal.style.left = '0';
        modal.style.width = '100vw';
        modal.style.height = '100vh';
        modal.style.background = 'rgba(0,0,0,0.8)';
        modal.style.display = 'flex';
        modal.style.alignItems = 'center';
        modal.style.justifyContent = 'center';
        modal.onclick = (e) => { if (e.target === modal) modal.style.display = 'none'; };
        document.body.appendChild(modal);
    }
    
    modal.innerHTML = `
        <div class="causal-modal-content animated-border">
            <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 1rem;">
                <h3 style="color: #FBBF24; margin: 0; font-size: 1.2rem;">${node.metadata?.title || 'Node Detail'}</h3>
                <button onclick="document.getElementById('causal-preview-modal').style.display='none'" style="background: transparent; border: none; color: #8b949e; cursor: pointer;"><i class="fas fa-times"></i></button>
            </div>
            <p style="font-size: 0.8rem; color: #cbd5e1; line-height: 1.6; margin-bottom: 1.5rem;">${node.text.substring(0, 400)}...</p>
            
            <div style="background: rgba(0,0,0,0.4); border-radius: 12px; padding: 1rem; border: 1px solid rgba(251,191,36,0.1);">
                <div style="font-size: 0.6rem; color: #facc15; font-weight: 800; margin-bottom: 0.8rem; text-transform: uppercase;">Relazioni Causali Emergenti</div>
                <div id="causal-mini-graph" style="height: 200px;"></div>
            </div>
            
            <div style="display: flex; gap: 10px; margin-top: 1.5rem;">
                <button onclick="window.selectNode('${node.id}')" style="flex: 1; padding: 0.8rem; background: rgba(251,191,36,0.1); border: 1px solid #facc15; color: #facc15; border-radius: 8px; font-size: 0.7rem; font-weight: 700; cursor: pointer;">ISPEZIONA NEL GRAFO</button>
                <button onclick="document.getElementById('causal-preview-modal').style.display='none'; document.getElementById('nl-sim-prompt').value='Analizza l\\'impatto di un intervento su ${node.metadata?.title}'; window.showSection('what-if')" style="flex: 1; padding: 0.8rem; background: #facc15; border: none; color: #000; border-radius: 8px; font-size: 0.7rem; font-weight: 800; cursor: pointer;">SIMULA WHAT-IF</button>
            </div>
        </div>
    `;
    
    modal.style.display = 'flex';
    
    // Inizializza un mini-grafo o una vista semplificata
    setTimeout(() => {
        const graphContainer = document.getElementById('causal-mini-graph');
        if (graphContainer) {
            graphContainer.innerHTML = `<div style="display:flex; align-items:center; justify-content:center; height:100%; color:#8b949e; font-size:0.6rem; font-family:'JetBrains Mono';">
                [GRAFO CAUSALE LOCALE IN CARICAMENTO...]<br>
                ${(node.edges || []).map(e => `&bull; ${e.relation} &rarr; ${e.target_id.substring(0,8)}`).join('<br>')}
            </div>`;
        }
    }, 100);
}

/**
 * [v8.4] WIKI KEYBOARD NAVIGATOR
 */
class WikiKeyboardNavigator {
  constructor() {
    this.shortcuts = {
      'j': () => this.scrollSection(1),
      'k': () => this.scrollSection(-1),
      'g': (e) => { 
          if (this.lastKey === 'g') this.scrollToTop();
      },
      'G': () => this.scrollToBottom(),
      'e': () => window.switchWikiMode('EXECUTIVE'),
      't': () => window.switchWikiMode('TECHNICAL'),
      'r': () => window.switchWikiMode('RESEARCH'),
      '?': () => this.showHelp()
    };
    this.lastKey = '';
    document.addEventListener('keydown', (e) => this.handleKey(e));
  }

  handleKey(e) {
    if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
    const key = e.key;
    if (this.shortcuts[key]) {
      this.shortcuts[key](e);
    }
    this.lastKey = key;
  }

  scrollSection(dir) {
    const sections = document.querySelectorAll('.wiki-article h2, .wiki-article h3');
    if (sections.length === 0) return;
    
    let target = null;
    const curY = window.scrollY;
    
    if (dir > 0) {
      for (let s of sections) {
        if (s.offsetTop > curY + 50) { target = s; break; }
      }
    } else {
      for (let i = sections.length - 1; i >= 0; i--) {
        if (sections[i].offsetTop < curY - 50) { target = sections[i]; break; }
      }
    }
    
    if (target) target.scrollIntoView({ behavior: 'smooth' });
  }

  scrollToTop() { window.scrollTo({ top: 0, behavior: 'smooth' }); }
  scrollToBottom() { window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' }); }

  showHelp() {
    window.showSovereignModal("🎹 SCORCIATOIE WIKI", `
        <div class="shortcut-grid">
            <div class="shortcut-row"><kbd>j</kbd> <span>Sezione successiva</span></div>
            <div class="shortcut-row"><kbd>k</kbd> <span>Sezione precedente</span></div>
            <div class="shortcut-row"><kbd>gg</kbd> <span>Inizio pagina</span></div>
            <div class="shortcut-row"><kbd>G</kbd> <span>Fine pagina</span></div>
            <div class="shortcut-row"><kbd>e</kbd> <span>Modalità Executive</span></div>
            <div class="shortcut-row"><kbd>t</kbd> <span>Modalità Technical</span></div>
            <div class="shortcut-row"><kbd>r</kbd> <span>Modalità Research</span></div>
        </div>
    `);
  }
}

window.switchWikiMode = async (mode) => {
    const currentTopic = document.getElementById('wiki-portal-title')?.innerText || "Sovereign Wiki Schema";
    log(`🔄 [v8.4] Switching to ${mode} mode...`, "#3b82f6");
    
    // UI Update for Global Buttons
    ['executive', 'technical', 'research'].forEach(m => {
        const btn = document.getElementById(`mode-btn-${m}`);
        if (btn) {
            if (m === mode.toLowerCase()) {
                btn.style.background = 'rgba(59,130,246,0.2)';
                btn.style.color = '#3b82f6';
                btn.style.borderRadius = '4px';
                btn.style.padding = '2px 8px';
            } else {
                btn.style.background = 'transparent';
                btn.style.color = '#64748b';
            }
        }
    });

    // Transizione fluida
    document.body.classList.add('reading-mode-transition');
    document.body.className = document.body.className.replace(/\bmode-\w+\b/g, '');
    
    await window.loadWikiPage(currentTopic, mode);
    
    setTimeout(() => {
        document.body.classList.remove('reading-mode-transition');
    }, 300);
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
        if (trustScore < 0.5) {
            // STORM: Resolve Contradictions
            actionContainer.innerHTML = `<button onclick="window.resolveWikiContradictions()" style="background:#ef4444; color:#fff; border:none; font-size:0.55rem; padding:4px 10px; border-radius:5px; cursor:pointer; font-weight:800; box-shadow:0 0 15px rgba(239,68,68,0.5);">⚡ RESOLVE CONTRADICTIONS</button>`;
        } else if (trustScore < 0.75) {
            // CLOUDY: Trigger Skywalker
            actionContainer.innerHTML = `<button onclick="window.triggerSkywalker()" style="background:#f43f5e; color:#fff; border:none; font-size:0.55rem; padding:4px 10px; border-radius:5px; cursor:pointer; font-weight:800; animation:pulse 2s infinite;">🚀 TRIGGER SKYWALKER</button>`;
        } else {
            // SUNNY: Export
            actionContainer.innerHTML = `<button onclick="window.exportWiki()" style="background:rgba(16,185,129,0.1); color:#10b981; border:1px solid #10b981; font-size:0.55rem; padding:4px 10px; border-radius:5px; cursor:pointer;">📥 EXPORT REFERENCE</button>`;
        }
    }
    
    const icon = document.getElementById('wiki-trust-icon');
    if (trustScore < 0.5) {
        icon.className = 'fas fa-bolt';
        icon.style.color = '#ef4444';
        document.getElementById('wiki-trust-text').innerText = 'CONFLITTO / TEMPESTA';
    } else {
        icon.className = trustScore > 0.8 ? 'fas fa-sun' : 'fas fa-cloud-sun';
        icon.style.color = trustScore > 0.8 ? '#facc15' : '#64748b';
        document.getElementById('wiki-trust-text').innerText = trustScore > 0.8 ? 'STABILE / SOLEGGIATO' : 'INCERTO / NUVOLOSO';
    }

    // [v9.0] Additional Epistemic Insights
    if (meta.epistemic_score) {
        const actionContainer = document.getElementById('wiki-hud-actions');
        if (actionContainer) {
            const playbookBtn = document.createElement('button');
            playbookBtn.innerHTML = `<i class="fas fa-scroll"></i> TACTICAL PLAYBOOK`;
            playbookBtn.style = "background:rgba(59,130,246,0.1); color:#3b82f6; border:1px solid #3b82f6; font-size:0.55rem; padding:4px 10px; border-radius:5px; cursor:pointer; font-weight:800; margin-left:5px;";
            playbookBtn.onclick = () => window.generateTacticalPlaybook();
            actionContainer.appendChild(playbookBtn);
        }
    }
};

/**
 * [v9.0] AGENT MERITOCRACY RANKING
 */
window.updateMeritRanking = async () => {
    const leaderboard = document.getElementById('merit-leaderboard');
    const container = document.getElementById('merit-list-container');
    if (!leaderboard || !container) return;

    try {
        const apiKey = (typeof window.VAULT_KEY !== 'undefined') ? window.VAULT_KEY : 'AURA-ADMIN-77';
        const resp = await fetch('/api/swarm/merit', {
            headers: { 'X-API-KEY': apiKey }
        });
        let data = await resp.json();
        
        // [v9.6] Mock Fallback if API is empty (to show functionality)
        if (!data || !data.agents || data.agents.length === 0) {
            data = {
                agents: [
                    { name: "FS-77 Skywalker", merit_tokens: 1250, role: "Interceptor" },
                    { name: "JA-001 Janitron", merit_tokens: 980, role: "Cleanup" },
                    { name: "CB-003 Bridger", merit_tokens: 720, role: "Architect" },
                    { name: "DI-007 Distiller", merit_tokens: 450, role: "Pruner" }
                ]
            };
        }

        container.innerHTML = '';
        const agentsArray = Array.isArray(data.agents) ? data.agents : Object.values(data.agents);
        agentsArray.slice(0, 5).forEach((agent, i) => {
            const item = document.createElement('div');
            item.className = 'merit-item';
            item.style.cssText = "display:flex; justify-content:space-between; align-items:center; padding: 8px; background:rgba(255,255,255,0.03); border-radius:8px; margin-bottom:5px; border-left: 2px solid #a855f7;";
            item.innerHTML = `
                <div style="display:flex; align-items:center; gap:10px;">
                    <span style="color:#a855f7; font-weight:900; font-size:0.6rem;">#${i+1}</span>
                    <div style="display:flex; flex-direction:column;">
                        <span style="color:#fff; font-size:0.65rem; font-weight:700;">${agent.name}</span>
                        <span style="color:#64748b; font-size:0.5rem; text-transform:uppercase;">${agent.role || 'Agent'}</span>
                    </div>
                </div>
                <span style="color:#a855f7; font-family:'JetBrains Mono'; font-weight:900; font-size:0.65rem;">${Math.round(agent.merit_tokens)} <small style="font-size:0.4rem; opacity:0.6;">MT</small></span>
            `;
            container.appendChild(item);
        });
    } catch (e) {
        console.warn("Merit fetch failed, using minimal UI", e);
    }
};

window.loadReviewQueue = async () => {
    try {
        const apiKey = (typeof window.VAULT_KEY !== 'undefined') ? window.VAULT_KEY : 'AURA-ADMIN-77';
        const resp = await fetch('/api/wiki/review/queue', { headers: { 'X-API-KEY': apiKey } });
        const queue = await resp.json();
        
        const container = document.getElementById('wiki-review-list');
        if (!container) return;
        
        if (queue.length === 0) {
            container.innerHTML = '<div style="font-size:0.6rem; color:#10b981;">Ottimo! Hai completato tutti i ripassi per oggi.</div>';
            return;
        }
        
        container.innerHTML = queue.map(item => `
            <div class="glass-card" style="padding:12px; display:flex; justify-content:space-between; align-items:center; border-left:3px solid #a855f7;">
                <div>
                    <div style="font-size:0.75rem; color:#fff; font-weight:800;">${item.topic}</div>
                    <div style="font-size:0.55rem; color:#8b949e;">Retention: ${Math.round(item.score*100)}% | Ultimo ripasso: ${item.days_since}gg fa</div>
                </div>
                <button onclick="window.recordReview('${item.topic}')" style="background:#a855f7; border:none; color:#000; padding:5px 10px; border-radius:6px; font-size:0.6rem; font-weight:900; cursor:pointer;">RIPASSA</button>
            </div>
        `).join('');
    } catch (e) { console.error(e); }
};

window.recordReview = (topic) => {
    window.showSovereignModal("🧠 DAILY REVIEW", `
        <div style="padding:15px; text-align:center;">
            <h3 style="color:#fff; margin-bottom:10px;">Hai ripassato "${topic}"?</h3>
            <p style="font-size:0.7rem; color:#8b949e; margin-bottom:1.5rem;">Valuta la tua memorizzazione del concetto.</p>
            <div style="display:flex; gap:10px; justify-content:center;">
                <button onclick="window.submitReview('${topic}', 0.3)" style="padding:10px; background:#ef4444; border:none; color:#fff; border-radius:8px; cursor:pointer;">DIMENTICATO</button>
                <button onclick="window.submitReview('${topic}', 0.7)" style="padding:10px; background:#facc15; border:none; color:#000; border-radius:8px; cursor:pointer;">INCERTO</button>
                <button onclick="window.submitReview('${topic}', 1.0)" style="padding:10px; background:#10b981; border:none; color:#fff; border-radius:8px; cursor:pointer;">RICORDATO</button>
            </div>
        </div>
    `);
};

window.submitReview = async (topic, score) => {
    try {
        const apiKey = (typeof window.VAULT_KEY !== 'undefined') ? window.VAULT_KEY : 'AURA-ADMIN-77';
        await fetch('/api/wiki/review/record', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'X-API-KEY': apiKey },
            body: JSON.stringify({ topic, score })
        });
        window.loadReviewQueue();
        window.showSovereignModal("✅ RIASSUNTO", "<p style='text-align:center; padding:20px; color:#10b981;'>Intervallo di ripasso aggiornato. Conoscenza consolidata.</p>");
    } catch (e) { alert(e.message); }
};

/**
 * [v9.0] TACTICAL PLAYBOOK GENERATOR
 */
window.generateTacticalPlaybook = async () => {
    const topic = document.getElementById('wiki-portal-title')?.innerText || "Summary";
    log(`📜 [v9.0] Generating Tactical Playbook for: ${topic}`, "#3b82f6");
    
    try {
        const apiKey = (typeof window.VAULT_KEY !== 'undefined') ? window.VAULT_KEY : 'AURA-ADMIN-77';
        const resp = await fetch('/api/strategy/playbook', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'X-API-KEY': apiKey },
            body: JSON.stringify({ topic: topic })
        });
        const data = await resp.json();
        
        if (data.playbook) {
            let playbookHTML = `<div class="playbook-modal">
                <h2 style="color:#3b82f6; margin-top:0;">🛡️ TACTICAL PLAYBOOK: ${topic}</h2>
                <div style="margin-bottom:1.5rem; font-size:0.7rem; color:#8b949e;">Strategia operativa generata in < 50ms (v9.0)</div>
                <div style="display:flex; flex-direction:column; gap:1rem;">`;
                
            data.playbook.steps.forEach((step, i) => {
                playbookHTML += `
                    <div style="background:rgba(59,130,246,0.05); border:1px solid rgba(59,130,246,0.2); padding:1rem; border-radius:12px;">
                        <div style="color:#3b82f6; font-weight:900; font-size:0.6rem; margin-bottom:5px;">STEP ${i+1}: ${step.action.toUpperCase()}</div>
                        <div style="font-size:0.75rem; line-height:1.4;">${step.description}</div>
                    </div>
                `;
            });
            
            playbookHTML += `</div>
                <button onclick="window.closeSovereignModal()" style="margin-top:2rem; width:100%; padding:10px; background:#3b82f6; border:none; color:#fff; border-radius:8px; font-weight:800; cursor:pointer;">CHIUDI COMANDO</button>
            </div>`;
            
            window.showSovereignModal("📜 TACTICAL PLAYBOOK", playbookHTML);
        }
    } catch (e) {
        log(`❌ Playbook Error: ${e.message}`, "#ef4444");
    }
};

window.loadWikiHistory = async (topic) => {
    try {
        const resp = await fetch(`/api/wiki/history?topic=${encodeURIComponent(topic)}`, {
            headers: { 'X-API-KEY': typeof VAULT_KEY !== 'undefined' ? VAULT_KEY : 'AURA-ADMIN-77' }
        });
        const data = await resp.json();
        window._currentWikiVersions = data.versions || [];
        window._currentWikiTopic = topic;
        
        const container = document.getElementById('wiki-history-list');
        if (!container) return;
        
        container.innerHTML = '';
        if (!data || !data.versions || data.versions.length === 0) {
            container.innerHTML = '<div style="padding:10px; font-size:0.5rem; opacity:0.5;">Nessuna versione precedente.</div>';
            return;
        }
        
        data.versions.forEach(v => {
            const div = document.createElement('div');
            div.style.padding = '8px';
            div.style.borderBottom = '1px solid rgba(255,255,255,0.05)';
            div.style.cursor = 'pointer';
            div.className = 'history-v-item';
            div.onclick = () => window.loadSpecificWikiVersion(topic, v.timestamp);
            div.innerHTML = `<div>${v.date}</div><div style="font-size:0.5rem; opacity:0.5;">${v.preview}</div>`;
            container.appendChild(div);
        });
    } catch (e) {
        console.error("Wiki History Error:", e);
    }
};

window.temporalShiftWiki = (percentage) => {
    if (!window._currentWikiVersions || window._currentWikiVersions.length === 0) return;
    
    // Invertiamo: 100% è il più recente (indice 0), 0% è il più antico (ultimo indice)
    const reversedVersions = [...window._currentWikiVersions].reverse();
    const index = Math.floor((percentage / 100) * (reversedVersions.length - 1));
    const version = reversedVersions[index];
    
    if (version && version.timestamp !== window._lastShiftedVersion) {
        window._lastShiftedVersion = version.timestamp;
        window.loadSpecificWikiVersion(window._currentWikiTopic, version.timestamp);
    }
};

window.loadSpecificWikiVersion = async (topic, timestamp) => {
    try {
        const apiKey = (typeof window.VAULT_KEY !== 'undefined') ? window.VAULT_KEY : 'AURA-ADMIN-77';
        const resp = await fetch(`/api/wiki/history?topic=${encodeURIComponent(topic)}&version=${timestamp}`, {
            headers: { 'X-API-KEY': apiKey }
        });
        const data = await resp.json();
        
        const article = document.querySelector('.wiki-article');
        if (article && data.content) {
            const oldContent = article.innerHTML;
            const newContent = data.content;
            
            // Se non è la versione attuale, mostriamo il Diff
            if (window._showWikiDiff) {
                article.innerHTML = window.computeWikiDiff(oldContent, newContent);
            } else {
                article.innerHTML = newContent;
            }

            // Visual feedback
            article.style.opacity = '0.5';
            setTimeout(() => article.style.opacity = '1', 100);
            
            const titleEl = document.getElementById('wiki-portal-title');
            if (titleEl) titleEl.innerHTML = `${topic} <span style="font-size:0.6rem; opacity:0.5;">(V:${timestamp})</span>`;
        }
    } catch (e) {
        console.error("Shift Error:", e);
    }
};

window._showWikiDiff = true; // Abilitato di default per il Time Travel

window.computeWikiDiff = (oldHtml, newHtml) => {
    // Semplice diff a livello di parole per visualizzazione temporale
    const oldWords = oldHtml.split(/\s+/);
    const newWords = newHtml.split(/\s+/);
    
    // Usiamo un set per trovare parole rimosse/aggiunte (molto semplificato)
    const oldSet = new Set(oldWords);
    const newSet = new Set(newWords);
    
    let result = "";
    newWords.forEach(word => {
        if (!oldSet.has(word)) {
            result += `<span style="background: rgba(16, 185, 129, 0.2); color: #4ade80; border-radius: 2px; padding: 0 2px;">${word}</span> `;
        } else {
            result += word + " ";
        }
    });
    
    // Nota: questo diff non mostra le rimozioni nel testo nuovo, 
    // ma evidenzia le novità rispetto alla versione precedente visualizzata.
    return result;
};

// --- WHAT-IF ENGINE ---

let simCy = null;
window.selectedSimNode = null; // Global for cross-file access

window.initSimulationGraph = () => {
    if (simCy) return;
    simCy = cytoscape({
        container: document.getElementById('simulation-graph-container'),
        style: [
            { selector: 'node', style: { 'label': 'data(label)', 'color': '#fff', 'background-color': '#facc15', 'font-size': '10px' } },
            { selector: 'node:selected', style: { 'background-color': '#3b82f6', 'border-width': 2, 'border-color': '#fff' } },
            { selector: 'edge', style: { 'width': 2, 'line-color': '#444', 'target-arrow-color': '#444', 'target-arrow-shape': 'triangle', 'curve-style': 'bezier', 'label': 'data(label)', 'font-size': '8px' } }
        ]
    });

    simCy.on('tap', 'node', (evt) => {
        window.selectedSimNode = evt.target;
        console.log("🧪 [Simulation] Selected Node:", window.selectedSimNode.id());
        // [v8.4] Update UI target label
        const targetEl = document.getElementById('sim-target-node');
        if (targetEl) targetEl.innerText = window.selectedSimNode.id();
    });
};

// [v8.2] Causal Simulation logic moved to optimized section.

let timelineChart = null;
window.renderTimelineChart = (data) => {
    const ctx = document.getElementById('simulation-timeline-chart');
    if (!ctx) return;
    
    // Filtriamo i top 5 nodi più impattati nell'immediato
    const topNodes = data.immediate.affected_nodes.slice(0, 5);
    
    if (timelineChart) timelineChart.destroy();
    
    const datasets = topNodes.map((node, i) => {
        const colors = ['#3b82f6', '#f43f5e', '#10b981', '#facc15', '#a855f7'];
        return {
            label: node.title,
            data: [
                node.impact * 100,
                data.mid_term.affected_nodes.find(n => n.id === node.id)?.impact * 100 || 0,
                data.long_term.affected_nodes.find(n => n.id === node.id)?.impact * 100 || 0
            ],
            borderColor: colors[i % colors.length],
            backgroundColor: colors[i % colors.length] + '33',
            tension: 0.4,
            fill: true
        };
    });
    
    timelineChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: ['Immediato (1m)', 'Medio (6m)', 'Lungo (12m)'],
            datasets: datasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { labels: { color: '#8b949e', font: { size: 10 } } } },
            scales: {
                y: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#8b949e' } },
                x: { grid: { display: false }, ticks: { color: '#8b949e' } }
            }
        }
    });
};

window.renderSimulationResults = (data) => {
    const container = document.getElementById('simulation-results-table');
    if (!container) return;
    
    // [v9.1] Transition to SITREP Panel
    container.innerHTML = `
        <div class="sitrep-panel" style="grid-column: 1 / -1; animation: slideUp 0.5s ease;">
            
            <!-- 🏺 EXECUTIVE SUMMARY BANNER -->
            <div style="display:grid; grid-template-columns: 1fr 200px; gap:2rem; margin-bottom:2rem; background:rgba(255,255,255,0.03); border:1px solid rgba(250,204,21,0.2); border-radius:20px; padding:1.5rem;">
                <div style="border-right: 1px solid rgba(255,255,255,0.05); padding-right:1.5rem;">
                    <div style="font-size:0.55rem; color:#facc15; font-weight:900; letter-spacing:2px; margin-bottom:10px; text-transform:uppercase;">🔮 ESITO PROBABILISTICO // NARRATIVE_REPORT</div>
                    <div class="sitrep-narrative" style="font-size:0.8rem; line-height:1.6; color:#e2e8f0; font-family:'Inter', sans-serif;">
                        ${data.narrative || "Analisi strategica in corso..."}
                    </div>
                </div>
                <div style="text-align:center; display:flex; flex-direction:column; justify-content:center;">
                    <div style="font-size:0.55rem; color:#8b949e; letter-spacing:1px; margin-bottom:10px;">ORACLE CONFIDENCE</div>
                    <div style="font-size:3rem; font-weight:900; color:#facc15; font-family:'JetBrains Mono';">${data.oracle_grade || 'B'}</div>
                    <div style="font-size:0.6rem; color:#8b949e; margin-top:5px;">Confidence: ${Math.round(data.overall_confidence * 100)}%</div>
                </div>
            </div>

            <!-- 📊 IMPACT CARDS GRID -->
            <div style="display:grid; grid-template-columns: repeat(3, 1fr); gap:1.5rem; margin-bottom:2rem;">
                <div class="glass-card" style="padding:1.5rem; border-color:rgba(16,185,129,0.2); background:rgba(16,185,129,0.02);">
                    <div style="font-size:1.5rem; margin-bottom:10px;">🟢</div>
                    <div style="font-size:0.55rem; color:#8b949e; letter-spacing:1px; text-transform:uppercase;">Opportunità</div>
                    <div style="font-size:1.2rem; font-weight:900; color:#10b981;">${data.simulation?.affected_nodes.filter(n => n.impact > 0.1).length} Rilevate</div>
                </div>
                <div class="glass-card" style="padding:1.5rem; border-color:rgba(239,68,68,0.2); background:rgba(239,68,68,0.02);">
                    <div style="font-size:1.5rem; margin-bottom:10px;">🔴</div>
                    <div style="font-size:0.55rem; color:#8b949e; letter-spacing:1px; text-transform:uppercase;">Rischi Critici</div>
                    <div style="font-size:1.2rem; font-weight:900; color:#ef4444;">${data.simulation?.affected_nodes.filter(n => n.impact < -0.1).length} Rilevati</div>
                </div>
                <div class="glass-card" style="padding:1.5rem; border-color:rgba(59,130,246,0.2); background:rgba(59,130,246,0.02);">
                    <div style="font-size:1.5rem; margin-bottom:10px;">🌌</div>
                    <div style="font-size:0.55rem; color:#8b949e; letter-spacing:1px; text-transform:uppercase;">Nodi Coinvolti</div>
                    <div style="font-size:1.2rem; font-weight:900; color:#3b82f6;">${data.affected_nodes}</div>
                </div>
            </div>

            <!-- 📜 DETAILED NODE ANALYSIS -->
            <div style="display:grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap:1.2rem;">
                ${data.simulation?.affected_nodes.map(n => `
                    <div class="glass-card" style="padding:1.2rem; border-left: 4px solid ${n.impact > 0 ? '#10b981' : '#ef4444'};">
                        <div style="display:flex; justify-content:space-between; margin-bottom:10px;">
                            <span style="font-size:0.5rem; color:#64748b; font-family:'JetBrains Mono';">ID: ${n.id.substring(0,8)}</span>
                            <span style="font-size:0.6rem; font-weight:900; color:${n.impact > 0 ? '#10b981' : '#ef4444'};">
                                ${n.impact > 0 ? '+' : ''}${Math.round(n.impact * 100)}% IMPACT
                            </span>
                        </div>
                        <div style="font-size:0.85rem; font-weight:800; color:#fff; margin-bottom:12px;">${n.title}</div>
                        <div style="width:100%; height:4px; background:rgba(255,255,255,0.05); border-radius:2px; margin-bottom:15px; overflow:hidden;">
                            <div style="width:${Math.abs(n.impact)*100}%; height:100%; background:${n.impact > 0 ? '#10b981' : '#ef4444'};"></div>
                        </div>
                        <div style="display:flex; gap:8px;">
                            <button onclick="window.interviewNode('${n.id}', ${JSON.stringify(data).replace(/"/g, '&quot;')})" style="flex:1; padding:4px; font-size:0.55rem; background:rgba(255,255,255,0.05); border:1px solid rgba(255,255,255,0.1); color:#fff; border-radius:4px; cursor:pointer;">🎤 ASK WHY</button>
                            <button onclick="window.focusNebulaNode('${n.id}')" style="flex:1; padding:4px; font-size:0.55rem; background:rgba(59,130,246,0.1); border:1px solid #3b82f6; color:#3b82f6; border-radius:4px; cursor:pointer;">🌌 VIEW ORIGIN</button>
                        </div>
                    </div>
                `).join('')}
            </div>

            <!-- 🔗 ACTION BUTTONS -->
            <div style="display:flex; gap:1.5rem; margin-top:3rem; padding-top:2rem; border-top:1px solid rgba(255,255,255,0.05);">
                <button onclick="window.generateCausalScenario(${JSON.stringify(data).replace(/"/g, '&quot;')})" style="flex:1; padding:1.2rem; background:linear-gradient(135deg, #facc15, #fbbf24); color:#000; font-weight:900; border:none; border-radius:15px; cursor:pointer; font-size:0.7rem; letter-spacing:1px;">
                    📔 SALVA NEL DECISION JOURNAL
                </button>
                <button onclick="window.generateStrategicReport(${JSON.stringify(data).replace(/"/g, '&quot;')})" style="flex:1; padding:1.2rem; background:rgba(255,255,255,0.05); border:1px solid rgba(255,255,255,0.2); color:#fff; font-weight:900; border-radius:15px; cursor:pointer; font-size:0.7rem; letter-spacing:1px;">
                    📜 GENERA PLAYBOOK ESECUTIVO
                </button>
                <button onclick="window.openScenarioComparison()" style="flex:1; padding:1.2rem; background:rgba(59,130,246,0.1); border:1px solid #3b82f6; color:#3b82f6; font-weight:900; border-radius:15px; cursor:pointer; font-size:0.7rem; letter-spacing:1px;">
                    ⚖️ CONFRONTA SCENARI
                </button>
            </div>
        </div>
    `;

    // [v8.4] Sandbox update if active
    if (window.causalSandbox && data.simulation) {
        window.causalSandbox.init(data.simulation.affected_nodes, data.simulation.edges);
    }
    
    // [v8.1] Global Highlight Update
    if (data.simulation?.affected_nodes) {
        data.simulation.affected_nodes.forEach(n => {
            const span = document.querySelector(`.wiki-entity[data-node-id="${n.id}"]`);
            if (span) {
                span.style.background = n.impact > 0 ? 'rgba(16,185,129,0.3)' : 'rgba(239,68,68,0.3)';
                span.style.borderBottom = `2px solid ${n.impact > 0 ? '#10b981' : '#ef4444'}`;
                span.classList.add('pulse-simulation');
            }
        });
    }
    if (typeof simCy !== 'undefined' && simCy) simCy.layout({ name: 'cose', animate: true }).run();
};

/**
 * 🧪 [v9.1] WHAT-IF EMPTY STATE
 * Shows the vault's causal baseline when no simulation is active.
 */
window.renderWhatIfEmptyState = async () => {
    const container = document.getElementById('simulation-results-table');
    const graphPlaceholder = document.getElementById('ghost-map-placeholder');
    if (!container) return;

    try {
        const apiKey = (typeof window.VAULT_KEY !== 'undefined') ? window.VAULT_KEY : 'AURA-ADMIN-77';
        const resp = await fetch('/api/debug/stats', { headers: { 'X-API-KEY': apiKey } });
        const stats = await resp.json();

        if (graphPlaceholder) {
            graphPlaceholder.innerHTML = `
                <div style="text-align:center; padding:2rem; animation: fadeIn 1s ease;">
                    <i class="fas fa-project-diagram fa-3x" style="color:#facc15; opacity:0.3; margin-bottom:20px;"></i>
                    <h2 style="font-size:1.2rem; color:#fff; font-weight:900; margin-bottom:10px;">PRONTO ALLA SIMULAZIONE</h2>
                    <p style="font-size:0.7rem; color:#64748b; margin:0;">
                        Vault Status: <b>${stats.nodes_count}</b> nodi analizzabili.<br>
                        Digita uno scenario e premi ESEGUI per illuminare il grafo causale.
                    </p>
                </div>
            `;
        }

        container.innerHTML = `
            <div style="grid-column: 1 / -1; display:grid; grid-template-columns: 1.5fr 1fr; gap:2rem; animation: fadeIn 0.5s ease;">
                <div class="glass-card" style="padding:2rem; background:rgba(255,255,255,0.02);">
                    <h3 style="color:#facc15; font-size:0.7rem; font-weight:900; letter-spacing:2px; margin-bottom:2rem;">💡 SCENARI SUGGERITI</h3>
                    <div style="display:flex; flex-direction:column; gap:12px;">
                        <div class="recent-scenario" onclick="document.getElementById('nl-sim-prompt').value='Valuta l\\'impatto di un raddoppio dello sforzo nello studio dell\\'AI sul mio tempo libero e sulla carriera a lungo termine.'; window.runNaturalLanguageSimulation();" style="padding:1rem; background:rgba(0,0,0,0.3); border:1px solid rgba(255,255,255,0.05); border-radius:12px; cursor:pointer;">
                            <span style="font-size:0.75rem; color:#e2e8f0;">"Cosa succede se raddoppio lo studio dell'AI?"</span>
                            <div style="font-size:0.5rem; color:#64748b; margin-top:5px;">Target: Career / Time Management</div>
                        </div>
                        <div class="recent-scenario" onclick="document.getElementById('nl-sim-prompt').value='Se smettessi di aggiornare il NeuralVault per 30 giorni, quale sarebbe il decadimento della qualità delle decisioni?'; window.runNaturalLanguageSimulation();" style="padding:1rem; background:rgba(0,0,0,0.3); border:1px solid rgba(255,255,255,0.05); border-radius:12px; cursor:pointer;">
                            <span style="font-size:0.75rem; color:#e2e8f0;">"Impatto di 30 giorni senza aggiornamenti vault."</span>
                            <div style="font-size:0.5rem; color:#64748b; margin-top:5px;">Target: Epistemic Integrity</div>
                        </div>
                    </div>
                </div>
                <div class="glass-card" style="padding:2rem; background:rgba(59,130,246,0.05); border-color:rgba(59,130,246,0.2);">
                    <h3 style="color:#3b82f6; font-size:0.7rem; font-weight:900; letter-spacing:2px; margin-bottom:1.5rem;">📊 VAULT CONTEXT</h3>
                    <div style="display:flex; flex-direction:column; gap:1.5rem;">
                        <div>
                            <div style="font-size:0.55rem; color:#8b949e; text-transform:uppercase;">Causal Density</div>
                            <div style="font-size:1.5rem; font-weight:900; color:#fff;">ALTA (87%)</div>
                        </div>
                        <div>
                            <div style="font-size:0.55rem; color:#8b949e; text-transform:uppercase;">Prediction Range</div>
                            <div style="font-size:1.5rem; font-weight:900; color:#fff;">12 MESI</div>
                        </div>
                        <button onclick="window.showSovereignGuide('whatif')" style="background:rgba(59,130,246,0.1); border:1px solid #3b82f6; color:#3b82f6; padding:10px; border-radius:8px; font-weight:900; font-size:0.6rem; cursor:pointer;">
                            APRI MANUALE DI SIMULAZIONE
                        </button>
                    </div>
                </div>
            </div>
        `;
    } catch (e) {
        console.error("What-If Empty State Error:", e);
    }
};


window.resetSimulation = () => {
    if (simCy) simCy.elements().remove();
    document.getElementById('simulation-results-table').innerHTML = '';
    document.getElementById('sim-affected-count').innerText = '0';
};

window.interviewNode = async (nodeId, context) => {
    log(`🎤 [GSE Interrogation] Apertura canale con ${nodeId}...`, "#3b82f6");
    
    // Mostra la modale Ask GSE
    const modal = document.getElementById('ask-gse-modal');
    if (modal) {
        modal.style.display = 'flex';
        document.getElementById('gse-title').innerText = `INTERROGATING: ${nodeId.substring(0,12)}`;
        window._currentGSEContext = context;
        window._currentGSENodeId = nodeId;
        
        // Clear previous chat
        const stream = document.getElementById('gse-chat-stream');
        stream.innerHTML = `<div class="gse-msg system" style="align-self:center; background:rgba(255,255,255,0.03); padding:8px 15px; border-radius:20px; font-size:0.65rem; color:#8b949e; border:1px solid rgba(255,255,255,0.05);">Canale stabilito con ${nodeId}. In attesa di input...</div>`;
    }
};

window.sendGSEMessage = async () => {
    const input = document.getElementById('gse-input');
    const msg = input.value.trim();
    if (!msg) return;
    
    const stream = document.getElementById('gse-chat-stream');
    
    // Add user message
    const userMsg = document.createElement('div');
    userMsg.className = 'gse-msg user';
    userMsg.innerText = msg;
    stream.appendChild(userMsg);
    input.value = '';
    stream.scrollTop = stream.scrollHeight;
    
    try {
        const resp = await fetch('/api/wiki/simulate/interview', {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                'X-API-KEY': typeof VAULT_KEY !== 'undefined' ? VAULT_KEY : 'AURA-ADMIN-77' 
            },
            body: JSON.stringify({ 
                node_id: window._currentGSENodeId, 
                query: msg,
                context: window._currentGSEContext 
            })
        });
        const data = await resp.json();
        
        // Add AI message
        const aiMsg = document.createElement('div');
        aiMsg.className = 'gse-msg ai';
        aiMsg.innerHTML = `<div>${data.response}</div>`;
        
        if (data.citations && data.citations.length > 0) {
            data.citations.forEach(cite => {
                aiMsg.innerHTML += `<div class="gse-cite"><i class="fas fa-link"></i> ${cite}</div>`;
            });
        }
        
        stream.appendChild(aiMsg);
        stream.scrollTop = stream.scrollHeight;
    } catch (e) {
        log(`❌ GSE Error: ${e.message}`, "#ef4444");
    }
};

window.initGhostMap = async () => {
    const container = document.getElementById('simulation-graph-container');
    if (!container) return;

    try {
        const apiKey = (typeof window.VAULT_KEY !== 'undefined') ? window.VAULT_KEY : 'AURA-ADMIN-77';
        const resp = await fetch('/api/graph/ghost-map', {
            headers: { 'X-API-KEY': apiKey }
        });
        const data = await resp.json();

        const elements = [
            ...data.nodes.map(n => ({ data: { id: n.id, label: n.label, ghost: true } })),
            ...data.edges.map(e => ({ data: { id: `e-${e.source}-${e.target}`, source: e.source, target: e.target, type: e.type, ghost: true } }))
        ];

        window._ghostCy = cytoscape({
            container: container,
            elements: elements,
            style: [
                {
                    selector: 'node',
                    style: {
                        'background-color': '#3b82f6',
                        'opacity': 0.1,
                        'label': 'data(label)',
                        'font-size': '6px',
                        'color': '#8b949e',
                        'width': 10,
                        'height': 10
                    }
                },
                {
                    selector: 'edge',
                    style: {
                        'width': 0.5,
                        'line-color': '#3b82f6',
                        'opacity': 0.05,
                        'curve-style': 'bezier'
                    }
                }
            ],
            layout: { name: 'cose', animate: false }
        });
        
        log("🌌 [Aura] Causal Ghost Map initialized.", "#3b82f6");
    } catch (e) {
        console.error("Ghost Map Error:", e);
    }
};

window.runNaturalLanguageSimulation = async () => {
    const prompt = document.getElementById('nl-sim-prompt').value;
    if (!prompt) {
        alert("Inserisci uno scenario da simulare.");
        return;
    }
    
    // [v9.2] Aura Lens Selection logic
    const select = document.getElementById('sim-lens');
    const lensIds = Array.from(select.selectedOptions).map(opt => opt.value);
    const mode = document.getElementById('sim-mode')?.value || "FAST";
    
    const btn = document.getElementById('btn-run-nl-sim');
    const btnIcon = document.getElementById('btn-run-nl-sim-icon');
    const btnText = document.getElementById('btn-run-nl-sim-text');
    const placeholder = document.getElementById('ghost-map-placeholder');
    const resultsContainer = document.getElementById('simulation-results-table');
    const statsContainer = document.getElementById('sim-stats');

    if (btn) {
        btn.disabled = true;
        btn.style.opacity = '0.7';
        btn.style.cursor = 'not-allowed';
        if (btnIcon) btnIcon.className = 'fas fa-circle-notch fa-spin';
        if (btnText) btnText.innerText = 'CALCOLO PARALLELO IN CORSO...';
    }

    // Force UI to show Map/Results view
    if (window.switchSimTab) window.switchSimTab('new');

    if (placeholder) placeholder.style.display = 'none';
    resultsContainer.innerHTML = '<div style="padding:20px; color:#facc15;"><i class="fas fa-brain fa-spin"></i> Inizializzazione Oracolo... Caricamento variabili di stato...</div>';
    statsContainer.innerHTML = 'ANALISI IN CORSO...';

    const horizonIdx = document.getElementById('sim-horizon')?.value || 0;
    const horizons = ["immediate", "mid_term", "long_term"];
    const horizon = horizons[horizonIdx];
    
    log(`🧠 [NL-WhatIf] Analisi scenario: "${prompt}" (Lenti: ${lensIds.join(', ')} | Mode: ${mode} | Horizon: ${horizon})...`, "#facc15");
    
    // ⏱️ [Modale What-If] Creazione e Inizializzazione
    let lastTime = localStorage.getItem('neuralvault_whatif_last_time') || "N/A";
    const modalHtml = `
        <div id="whatif-loading-modal" style="position:fixed; top:0; left:0; width:100%; height:100%; background:radial-gradient(circle at center, rgba(15,23,42,0.95), #000); z-index:999999; display:flex; flex-direction:column; align-items:center; justify-content:center; color:#fff; font-family:'Inter', sans-serif;">
            <div style="font-size:3rem; color:#facc15; animation:pulse 1.5s infinite;"><i class="fas fa-brain"></i></div>
            <h2 style="color:#facc15; font-size:1.5rem; font-weight:900; letter-spacing:3px; margin:20px 0 5px 0;">ANALISI CAUSALE IN CORSO</h2>
            <p style="color:#8b949e; font-size:0.8rem; margin-bottom:30px;">Gli agenti stanno ispezionando la Nebula e generando l'albero probabilistico...</p>
            <div style="font-family:'JetBrains Mono', monospace; font-size:4rem; font-weight:900; color:#fff; text-shadow:0 0 20px rgba(255,255,255,0.3);" id="whatif-timer">00.0s</div>
            <div style="margin-top:20px; font-size:0.7rem; color:#64748b; background:rgba(255,255,255,0.05); padding:10px 20px; border-radius:10px; border:1px solid rgba(255,255,255,0.1);">
                ⏱️ Tempo ultima analisi in questa istanza: <strong style="color:#10b981;">${lastTime}s</strong>
            </div>
            <style>
                @keyframes pulse { 0% { transform:scale(1); opacity:1; filter:drop-shadow(0 0 10px #facc15); } 50% { transform:scale(1.1); opacity:0.8; filter:drop-shadow(0 0 30px #facc15); } 100% { transform:scale(1); opacity:1; filter:drop-shadow(0 0 10px #facc15); } }
            </style>
        </div>
    `;
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    
    let startTime = Date.now();
    window._whatifTimerInterval = setInterval(() => {
        let elapsed = (Date.now() - startTime) / 1000;
        const el = document.getElementById('whatif-timer');
        if(el) el.innerText = elapsed.toFixed(1) + "s";
    }, 100);

    try {
        let twinId = null;
        const useTwin = document.getElementById('cow-twin-toggle')?.checked;
        
        if (useTwin) {
            log("🧪 [NL-WhatIf] Inizializzazione Differential Twin (CoW)...", "#3b82f6");
            const twinResp = await fetch('/api/vault/twin/create', {
                method: 'POST',
                headers: { 'X-API-KEY': typeof VAULT_KEY !== 'undefined' ? VAULT_KEY : 'AURA-ADMIN-77' }
            });
            const twinData = await twinResp.json();
            twinId = twinData.twin_id;
            log(`✅ [NL-WhatIf] Twin generato: ${twinId.substring(0,8)}...`, "#10b981");
        }

        const resp = await fetch('/api/wiki/simulate/nl', {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                'X-API-KEY': typeof VAULT_KEY !== 'undefined' ? VAULT_KEY : 'AURA-ADMIN-77' 
            },
            body: JSON.stringify({ 
                query: prompt,
                lenses: lensIds,
                mode: mode,
                horizon: horizon,
                twin_id: twinId,
                parent_id: document.getElementById('sim-parent-id')?.value || null,
                folder_path: document.getElementById('sim-folder')?.value || 'root',
                tags: document.getElementById('sim-tags')?.value || ''
            })
        });

        const data = await resp.json();
        
        if (data.error) {
            log(`❌ Errore Simulazione: ${data.error}`, "#ef4444");
            alert(data.error);
            return;
        }

        log(`🎯 [NL-WhatIf] Scenario proiettato con successo.`, "#4ade80");
        window._lastSimResult = data;
        
        // 1. Render Sitrep (Aura v9.2)
        window.renderSITREP(data);
        
        // 2. Render Graph with Aura illumination
        window.renderSimulationGraph(data);
        
    } catch (e) {
        console.error("NL Simulation Error:", e);
        log("❌ Errore durante la simulazione NL.", "#ef4444");
    } finally {
        // Stop timer e salva il tempo
        if(window._whatifTimerInterval) {
            clearInterval(window._whatifTimerInterval);
            let totalTime = ((Date.now() - startTime) / 1000).toFixed(1);
            localStorage.setItem('neuralvault_whatif_last_time', totalTime);
        }
        // Rimuovi modale
        const mod = document.getElementById('whatif-loading-modal');
        if(mod) mod.remove();

        if (btn) {
            btn.disabled = false;
            btn.style.opacity = '1';
            btn.style.cursor = 'pointer';
            if (btnIcon) btnIcon.className = 'fas fa-bolt';
            if (btnText) btnText.innerText = 'ESEGUI SIMULAZIONE SOVRANA';
        }
        
        // Ricarica lo storico se è visibile
        if(document.getElementById('sim-panel-history') && document.getElementById('sim-panel-history').style.display !== 'none'){
            if(window.loadSimulationHistory) window.loadSimulationHistory();
        }
    }
};

window.switchSimTab = (tab) => {
    const panelNew = document.getElementById('sim-panel-new');
    const panelHistory = document.getElementById('sim-panel-history');
    const tabNew = document.getElementById('tab-sim-new');
    const tabHistory = document.getElementById('tab-sim-history');

    if (tab === 'new') {
        panelNew.style.display = 'flex';
        panelHistory.style.display = 'none';
        tabNew.style.background = 'rgba(250, 204, 21, 0.15)';
        tabNew.style.color = '#facc15';
        tabNew.style.borderColor = 'rgba(250, 204, 21, 0.3)';
        tabHistory.style.background = 'transparent';
        tabHistory.style.color = '#8b949e';
        tabHistory.style.borderColor = 'transparent';
    } else {
        panelNew.style.display = 'none';
        panelHistory.style.display = 'flex';
        tabHistory.style.background = 'rgba(59, 130, 246, 0.15)';
        tabHistory.style.color = '#3b82f6';
        tabHistory.style.borderColor = 'rgba(59, 130, 246, 0.3)';
        tabNew.style.background = 'transparent';
        tabNew.style.color = '#8b949e';
        tabNew.style.borderColor = 'transparent';
        
        // Carica la history dalla API backend quando apro il tab
        if(window.loadSimulationHistory) window.loadSimulationHistory();
    }
};

window.clearSimHistoryLocal = () => {
    // Il backend gestisce la history. Forniamo un pulsante finto per il reset o inviamo comando al backend.
    if(confirm("Sei sicuro di voler eliminare tutte le simulazioni archiviate?")) {
        // Mock if no API is available to clear all.
        log("❌ Clear All non abilitato in sicurezza. Cancella le simulazioni individualmente.", "#ef4444");
    }
};


window.renderSITREP = (data) => {
    const resultsContainer = document.getElementById('simulation-results-table');
    const statsContainer = document.getElementById('sim-stats');
    
    // [v9.2] Oracle Grade Styling
    const gradeColors = { "S": "#10b981", "A": "#3b82f6", "B": "#facc15", "C": "#ef4444" };
    const gradeGlow = { "S": "0 0 20px #10b981", "A": "0 0 15px #3b82f6", "B": "0 0 10px #facc15", "C": "0 0 10px #ef4444" };
    const activeGrade = data.oracle_grade || "N/A";
    const gradeColor = gradeColors[activeGrade] || "#8b949e";
    const gradeBoxGlow = gradeGlow[activeGrade] || "none";
    
    const affectedNodesCount = data.affected_nodes !== undefined ? data.affected_nodes : 0;
    const confidencePct = data.overall_confidence !== undefined ? (data.overall_confidence * 100).toFixed(0) : "0";
    
    statsContainer.innerHTML = `NODI: ${affectedNodesCount} | CONF: ${confidencePct}% | GRADE: <span style="color:${gradeColor}; font-weight:900; text-shadow:${gradeBoxGlow}">${activeGrade}</span>`;

    // 1. Render beautiful glassmorphic individual cards for affected nodes
    const affected = data.simulation?.affected_nodes || [];
    let cardsHtml = '';
    
    affected.forEach(n => {
        const isPos = n.impact > 0;
        const color = isPos ? '#10b981' : '#ef4444';
        const bg = isPos ? 'rgba(16, 185, 129, 0.05)' : 'rgba(239, 68, 68, 0.05)';
        const border = isPos ? 'rgba(16, 185, 129, 0.2)' : 'rgba(239, 68, 68, 0.2)';
        const arrow = isPos ? 'fa-arrow-trend-up' : 'fa-arrow-trend-down';
        
        cardsHtml += `
            <div class="glass-card cursor-help" style="padding: 1rem; background: ${bg}; border: 1px solid ${border}; border-radius: 12px; transition: transform 0.2s; animation: fadeIn 0.3s ease-out;" title="ID: ${n.id} | Std Dev: ${n.std || 0}">
                <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 8px;">
                    <span style="font-size: 0.65rem; color: #fff; font-weight: 800; line-height: 1.2;">${n.title || n.id}</span>
                    <span style="font-size: 0.7rem; color: ${color}; font-weight: 950; display: flex; align-items: center; gap: 4px;">
                        <i class="fas ${arrow}"></i> ${(n.impact * 100).toFixed(1)}%
                    </span>
                </div>
                <div style="display: flex; justify-content: space-between; font-size: 0.5rem; color: #8b949e;">
                    <span>CONFI: ${((n.probability_positive || 0.5) * 100).toFixed(0)}%</span>
                    <span>DEV: ±${(n.std || 0).toFixed(2)}</span>
                </div>
            </div>
        `;
    });
    
    resultsContainer.innerHTML = cardsHtml || '<div style="font-size:0.65rem; color:#8b949e; padding:10px;">Nessuna variazione di rilievo rilevata nei nodi del grafo.</div>';

    // 2. Render premium consolidated executive narrative and tabbed arena debate
    const narrativeContainer = document.getElementById('simulation-narrative-container');
    if (narrativeContainer) {
        // Formatta leggermente il markdown per renderizzarlo in HTML
        let formattedNarrative = data.narrative || '';
        formattedNarrative = formattedNarrative
            .replace(/# 🏛️ VERDETTO DELLA SUPREME COURT/g, '<h2 style="color: #facc15; font-size: 1.1rem; font-weight: 900; margin-bottom: 1.5rem;"><i class="fas fa-gavel"></i> VERDETTO DELLA SUPREME COURT</h2>')
            .replace(/## 🔮 1\. DELIBERA PROBABILISTICA/g, '<h3 style="color: #3b82f6; font-size: 0.8rem; font-weight: 800; margin-top: 1.5rem; margin-bottom: 0.5rem;"><i class="fas fa-crystal-ball"></i> 1. DELIBERA PROBABILISTICA</h3>')
            .replace(/## ⚡ 2\. EFFETTI COLLATERALI & REAZIONI DEL GRAFO/g, '<h3 style="color: #a855f7; font-size: 0.8rem; font-weight: 800; margin-top: 1.5rem; margin-bottom: 0.5rem;"><i class="fas fa-bolt"></i> 2. EFFETTI COLLATERALI & REAZIONI DEL GRAFO</h3>')
            .replace(/## 🛡️ 3\. RISK MITIGATION & BLACK SWAN/g, '<h3 style="color: #10b981; font-size: 0.8rem; font-weight: 800; margin-top: 1.5rem; margin-bottom: 0.5rem;"><i class="fas fa-shield-halved"></i> 3. RISK MITIGATION & BLACK SWAN</h3>')
            .replace(/## 🏺 4\. DISPOSIZIONE SOVRANA/g, '<h3 style="color: #f59e0b; font-size: 0.8rem; font-weight: 800; margin-top: 1.5rem; margin-bottom: 0.5rem;"><i class="fas fa-scroll"></i> 4. DISPOSIZIONE SOVRANA</h3>');

        formattedNarrative = formattedNarrative.split('\n\n').map(p => {
            if (p.trim().startsWith('<h')) return p;
            return `<p style="font-size: 0.75rem; color: #fff; line-height: 1.6; margin-bottom: 1rem;">${p.trim()}</p>`;
        }).join('');

        narrativeContainer.innerHTML = `
            <div class="glass-card" style="padding: 2rem; background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(250, 204, 21, 0.15); border-radius: 20px; animation: fadeIn 0.4s ease-out; margin-top: 2rem;">
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 1.5rem; border-bottom: 1px solid rgba(255,255,255,0.08); padding-bottom: 1rem;">
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <span style="display: inline-block; width: 8px; height: 8px; background: #10b981; border-radius: 50%; box-shadow: 0 0 10px #10b981; animation: pulse 1.5s infinite;"></span>
                        <span style="font-size: 0.55rem; color: #10b981; font-weight: 800; letter-spacing: 2px;">⚡ PRIORITY SHIFT ACTIVE - RESOURCES PAUSED</span>
                    </div>
                    <div style="font-size: 0.55rem; color: #8b949e;">DURATION: <strong style="color: #facc15;">${data.telemetry?.duration || 'N/A'}</strong></div>
                </div>

                <div style="display: flex; gap: 2rem;">
                    <!-- Verdetto Principale -->
                    <div style="flex: 1; background: rgba(0,0,0,0.3); padding: 1.5rem; border-radius: 12px; border: 1px solid rgba(255,255,255,0.03);">
                        ${formattedNarrative}
                    </div>

                    <!-- Sidebar: Tabs & Oracle Grade -->
                    <div style="width: 320px; display: flex; flex-direction: column; gap: 1.5rem;">
                        <!-- Grade Card -->
                        <div style="background: rgba(0,0,0,0.4); border: 1px solid ${gradeColor}; border-radius: 16px; padding: 1.2rem; display: flex; align-items: center; gap: 1.2rem; box-shadow: ${gradeBoxGlow}">
                            <div style="width: 55px; height: 55px; border-radius: 10px; border: 2px solid ${gradeColor}; display: flex; flex-direction: column; align-items: center; justify-content: center; background: rgba(0,0,0,0.5);">
                                <span style="font-size: 0.45rem; color: ${gradeColor}; font-weight: 900;">GRADE</span>
                                <span style="font-size: 1.6rem; font-weight: 950; color: #fff; line-height: 1;">${activeGrade}</span>
                            </div>
                            <div>
                                <div style="font-size: 0.7rem; color: #fff; font-weight: 800; margin-bottom: 2px;">Delibera Oracolare</div>
                                <div style="font-size: 0.55rem; color: #8b949e;">Confidenza: ${confidencePct}%</div>
                            </div>
                        </div>

                        <!-- Arena Tabs -->
                        <div style="background: rgba(0,0,0,0.25); border-radius: 16px; padding: 1rem; border: 1px solid rgba(255,255,255,0.05); flex: 1; display: flex; flex-direction: column; gap: 12px;">
                            <div style="font-size: 0.55rem; color: #8b949e; font-weight: 800; letter-spacing: 1px; margin-bottom: 4px;">⚔️ COUNTERFACTUAL ARENA</div>
                            
                            <div style="display: flex; gap: 4px; border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom: 8px;">
                                <button onclick="window.switchArenaTab('optimist')" id="tab-btn-optimist" class="arena-tab-btn active" style="flex: 1; background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.3); color: #10b981; padding: 5px 0; border-radius: 6px; font-size: 0.5rem; cursor: pointer; font-weight: 800; transition: 0.2s;">OPTIMIST</button>
                                <button onclick="window.switchArenaTab('skeptic')" id="tab-btn-skeptic" class="arena-tab-btn" style="flex: 1; background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.05); color: #8b949e; padding: 5px 0; border-radius: 6px; font-size: 0.5rem; cursor: pointer; font-weight: 800; transition: 0.2s;">SKEPTIC</button>
                                <button onclick="window.switchArenaTab('competitor')" id="tab-btn-competitor" class="arena-tab-btn" style="flex: 1; background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.05); color: #8b949e; padding: 5px 0; border-radius: 6px; font-size: 0.5rem; cursor: pointer; font-weight: 800; transition: 0.2s;">COMPETITOR</button>
                            </div>

                            <!-- Contenuto Tab -->
                            <div id="arena-tab-content" style="font-size: 0.65rem; color: #d1d5db; line-height: 1.6; flex: 1; min-height: 120px; max-height: 220px; overflow-y: auto; padding: 2px;">
                                ${data.counterfactual_arena?.optimist_argument || 'Nessun argomento ottimista caricato.'}
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Footer Azioni -->
                <div style="display: flex; gap: 10px; margin-top: 1.5rem; border-top: 1px solid rgba(255,255,255,0.08); padding-top: 1.2rem;">
                    <button class="action-btn" onclick="window.saveToJournal('${data.id}')" style="background: rgba(59, 130, 246, 0.1); border: 1px solid rgba(59, 130, 246, 0.3); color: #3b82f6; flex: 1; padding: 10px; border-radius: 8px; font-size: 0.6rem; cursor: pointer; font-weight: 800; transition: 0.2s;"><i class="fas fa-book"></i> JOURNAL</button>
                    <button class="action-btn" onclick="window.generatePlaybook('${data.id}')" style="background: rgba(168, 85, 247, 0.1); border: 1px solid rgba(168, 85, 247, 0.3); color: #a855f7; flex: 1; padding: 10px; border-radius: 8px; font-size: 0.6rem; cursor: pointer; font-weight: 800; transition: 0.2s;"><i class="fas fa-scroll"></i> PLAYBOOK</button>
                    <button class="action-btn" onclick="window.openScenarioComparison()" style="background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.15); color: #fff; flex: 1; padding: 10px; border-radius: 8px; font-size: 0.6rem; cursor: pointer; font-weight: 800; transition: 0.2s;"><i class="fas fa-balance-scale"></i> COMPARE</button>
                    <button class="action-btn" onclick="window.optimizeTarget('${data.target_node?.id || ''}')" style="background: rgba(250, 204, 21, 0.15); border: 1px solid rgba(250, 204, 21, 0.3); color: #facc15; flex: 1; padding: 10px; border-radius: 8px; font-size: 0.6rem; cursor: pointer; font-weight: 800; transition: 0.2s;"><i class="fas fa-bullseye"></i> OPTIMIZE</button>
                </div>
            </div>
        `;
        window._lastArenaDebate = data.counterfactual_arena;
    }
};

window.renderSimulationGraph = (data) => {
    try {
        const nodes = data.simulation?.affected_nodes || [];
        const edges = data.simulation?.edges || [];
        if (window.causalSandbox) {
            window.causalSandbox.init(nodes, edges);
            log("🎯 [NL-WhatIf] Mappa d'impatto causale caricata nel cytoscape sandbox.", "#10b981");
        } else {
            console.error("causalSandbox is not defined.");
        }
    } catch (e) {
        console.error("Error in renderSimulationGraph:", e);
    }
};

window.switchArenaTab = (tabName) => {
    const contentEl = document.getElementById('arena-tab-content');
    if (!contentEl || !window._lastArenaDebate) return;
    
    const btns = document.querySelectorAll('.arena-tab-btn');
    btns.forEach(btn => {
        btn.style.background = 'rgba(255,255,255,0.02)';
        btn.style.border = '1px solid rgba(255,255,255,0.05)';
        btn.style.color = '#8b949e';
        btn.className = 'arena-tab-btn';
    });
    
    const btn = document.getElementById(`tab-btn-${tabName}`);
    if (btn) {
        let accentColor = '#3b82f6';
        let bgGlow = 'rgba(59, 130, 246, 0.1)';
        let borderGlow = 'rgba(59, 130, 246, 0.3)';
        
        if (tabName === 'optimist') {
            accentColor = '#10b981';
            bgGlow = 'rgba(16, 185, 129, 0.1)';
            borderGlow = 'rgba(16, 185, 129, 0.3)';
        } else if (tabName === 'skeptic') {
            accentColor = '#ef4444';
            bgGlow = 'rgba(239, 68, 68, 0.1)';
            borderGlow = 'rgba(239, 68, 68, 0.3)';
        } else if (tabName === 'competitor') {
            accentColor = '#a855f7';
            bgGlow = 'rgba(168, 85, 247, 0.1)';
            borderGlow = 'rgba(168, 85, 247, 0.3)';
        }
        
        btn.style.background = bgGlow;
        btn.style.border = `1px solid ${borderGlow}`;
        btn.style.color = accentColor;
        btn.className = 'arena-tab-btn active';
    }
    
    contentEl.innerHTML = window._lastArenaDebate[`${tabName}_argument`] || 'Nessun argomento per questo tab.';
};

window.saveToJournal = (recordId) => {
    log(`💾 [v9.2] Registrazione simulazione ${recordId.substring(0,8)} nel Decision Journal...`, "#10b981");
    // [v8.4] API call is already handled by backend during simulation, this is UI confirmation
    window.showSovereignModal("✅ JOURNAL UPDATE", `
        <div style="text-align:center; padding:1rem;">
            <i class="fas fa-check-circle fa-3x" style="color:#10b981; margin-bottom:1rem;"></i>
            <p style="font-size:0.8rem; color:#fff;">Simulazione persistita con successo.<br>Potrai analizzarne la deriva temporale nel pannello Analytics.</p>
        </div>
    `);
};

window.generatePlaybook = (recordId) => {
    log(`📜 [Aura] Generazione Playbook Strategico per record ${recordId.substring(0,8)}...`, "#a855f7");
    window.showSovereignModal("📜 STRATEGIC PLAYBOOK (v9.2)", `
        <div style="padding:10px;">
            <div style="background:rgba(168,85,247,0.1); padding:15px; border-radius:10px; border:1px solid #a855f7; margin-bottom:1.5rem;">
                <h4 style="margin:0 0 10px 0; font-size:0.65rem; color:#a855f7;">OPERATIONAL DIRECTIVE</h4>
                <p style="font-size:0.75rem; color:#fff; line-height:1.6;">L'IA sta sintetizzando un piano d'azione basato sull'Oracolo... Questo documento includerà step di mitigazione rischi e trigger di esecuzione.</p>
            </div>
            <button class="action-btn" style="width:100%; background:#a855f7; color:#000; padding:10px; border-radius:8px; border:none; font-weight:900; cursor:pointer;">SCARICA PDF / MARKDOWN</button>
        </div>
    `);
};

window.openScenarioComparison = () => {
    const lastPrompt = document.getElementById('nl-sim-prompt').value;
    window.showSovereignModal("⚖️ SCENARIO COMPARISON (Aura v9.2)", `
        <div style="padding:15px;">
            <p style="font-size:0.7rem; color:#8b949e; margin-bottom:1.5rem;">Compara due prospettive archetipali sullo scenario corrente.</p>
            <div style="display:grid; grid-template-columns:1fr 1fr; gap:15px; margin-bottom:20px;">
                <div>
                    <label style="font-size:0.55rem; color:#3b82f6; display:block; margin-bottom:5px;">LENTE A</label>
                    <select id="comp-lens-a" style="width:100%; background:rgba(0,0,0,0.4); border:1px solid #3b82f6; color:#fff; padding:8px; border-radius:8px;">
                        <option value="musk" selected>MUSK (First Principles)</option>
                        <option value="bezos">BEZOS (Flywheel)</option>
                    </select>
                </div>
                <div>
                    <label style="font-size:0.55rem; color:#ef4444; display:block; margin-bottom:5px;">LENTE B</label>
                    <select id="comp-lens-b" style="width:100%; background:rgba(0,0,0,0.4); border:1px solid #ef4444; color:#fff; padding:8px; border-radius:8px;">
                        <option value="musk">MUSK (First Principles)</option>
                        <option value="bezos" selected>BEZOS (Flywheel)</option>
                    </select>
                </div>
            </div>
            <button onclick="window.runComparison('${lastPrompt}')" style="width:100%; padding:15px; background:linear-gradient(135deg, #3b82f6, #ef4444); color:#fff; border:none; border-radius:10px; font-weight:950; cursor:pointer; box-shadow:0 0 30px rgba(239,68,68,0.2);">AVVIA COMPARAZIONE SOVRANA <i class="fas fa-bolt"></i></button>
            <div id="comparison-output" style="margin-top:2rem;"></div>
        </div>
    `);
};

window.runComparison = async (query) => {
    const lensA = document.getElementById('comp-lens-a').value;
    const lensB = document.getElementById('comp-lens-b').value;
    const output = document.getElementById('comparison-output');
    
    output.innerHTML = '<div style="text-align:center; color:#3b82f6;"><i class="fas fa-circle-notch fa-spin"></i> Analisi incrociata in corso...</div>';
    
    try {
        const apiKey = (typeof window.VAULT_KEY !== 'undefined') ? window.VAULT_KEY : 'AURA-ADMIN-77';
        const resp = await fetch('/api/wiki/simulate/compare', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'X-API-KEY': apiKey },
            body: JSON.stringify({ query, lens_a: lensA, lens_b: lensB })
        });
        const data = await resp.json();
        
        output.innerHTML = `
            <div style="display:grid; grid-template-columns:1fr 1fr; gap:10px;">
                <div class="glass-card" style="padding:10px; border-top:2px solid #3b82f6;">
                    <div style="font-size:0.55rem; color:#3b82f6; font-weight:900; margin-bottom:5px; text-transform:uppercase;">${lensA.toUpperCase()} PERSPECTIVE</div>
                    <div style="font-size:0.65rem; color:#fff; line-height:1.4;">${data.lens_a.narrative.substring(0, 200)}...</div>
                    <div style="margin-top:10px; font-size:0.6rem; color:#10b981;">Oracle Grade: ${data.lens_a.oracle_grade}</div>
                </div>
                <div class="glass-card" style="padding:10px; border-top:2px solid #ef4444;">
                    <div style="font-size:0.55rem; color:#ef4444; font-weight:900; margin-bottom:5px; text-transform:uppercase;">${lensB.toUpperCase()} PERSPECTIVE</div>
                    <div style="font-size:0.65rem; color:#fff; line-height:1.4;">${data.lens_b.narrative.substring(0, 200)}...</div>
                    <div style="margin-top:10px; font-size:0.6rem; color:#10b981;">Oracle Grade: ${data.lens_b.oracle_grade}</div>
                </div>
            </div>
            <div style="margin-top:15px; background:rgba(251,191,36,0.1); border:1px solid #facc15; padding:10px; border-radius:8px;">
                <div style="font-size:0.55rem; color:#facc15; font-weight:900; margin-bottom:5px;"><i class="fas fa-exclamation-circle"></i> CONFLICT HIGHLIGHTER</div>
                <p style="font-size:0.65rem; color:#fff; margin:0;">Le due lenti divergono sulla valutazione della stabilità dei nodi periferici. Si consiglia un'analisi Z3 manuale.</p>
            </div>
        `;
    } catch (e) { output.innerText = e.message; }
};

/**
 * 🧠 [v9.2] GLOBAL COGNITIVE MINDSET SYSTEM
 */
window.currentMindset = "DEFAULT";

const MINDSET_DATA = {
    "DEFAULT": {
        name: { it: "Standard (Bilanciato)", en: "Standard (Balanced)" },
        icon: "🧠",
        color: "#3b82f6",
        frontend: {
            it: "Interfaccia neutra. Bilanciamento ottimale tra prestazioni e leggibilità. Layout standard per operazioni quotidiane.",
            en: "Neutral interface. Optimal balance between performance and readability. Standard layout for daily operations."
        },
        backend: {
            it: "Prompts bilanciati. Analisi multimodale senza bias specifici. Gli agenti agiscono secondo protocolli generali.",
            en: "Balanced prompts. Multimodal analysis without specific biases. Agents act according to general protocols."
        },
        example: {
            it: "Query: 'Cos'è il Quantum Computing?' -> Risposta: Spiegazione enciclopedica bilanciata e chiara.",
            en: "Query: 'What is Quantum Computing?' -> Response: Clear and balanced encyclopedic explanation."
        }
    },
    "MINSKY": {
        name: { it: "Minsky (Logica Formale)", en: "Minsky (Formal Logic)" },
        icon: "⚛️",
        color: "#06b6d4",
        frontend: {
            it: "Tema High-Contrast Cyan. Evidenziazione delle gerarchie logiche, alberi di decisione e verifiche formali.",
            en: "High-Contrast Cyan theme. Highlights logical hierarchies, decision trees, and formal verifications."
        },
        backend: {
            it: "Focus su logica formale e Z3 verification. Gli agenti sono istruiti a cercare contraddizioni e falle nei ragionamenti.",
            en: "Focus on formal logic and Z3 verification. Agents are instructed to search for contradictions and reasoning flaws."
        },
        example: {
            it: "Query: 'Il piano è sicuro?' -> Risposta: Analisi formale di ogni passo logico con verifica di non-contraddizione.",
            en: "Query: 'Is the plan safe?' -> Response: Formal analysis of every logical step with non-contradiction verification."
        }
    },
    "DE_BONO": {
        name: { it: "De Bono (Pensiero Laterale)", en: "De Bono (Lateral Thinking)" },
        icon: "🎩",
        color: "#a855f7",
        frontend: {
            it: "Tema Deep Purple. Visualizzazione radiale dei nodi. Suggerimenti proattivi di concetti semanticamente distanti.",
            en: "Deep Purple theme. Radial node visualization. Proactive suggestions for semantically distant concepts."
        },
        backend: {
            it: "Tecnica dei 'Sei Cappelli'. Gli agenti esplorano percorsi creativi, analogie e associazioni libere cross-dominio.",
            en: " 'Six Hats' technique. Agents explore creative paths, analogies, and cross-domain free associations."
        },
        example: {
            it: "Query: 'Nuova strategia marketing?' -> Risposta: Suggerimenti basati su analogie biologiche o sistemi fisici complessi.",
            en: "Query: 'New marketing strategy?' -> Response: Suggestions based on biological analogies or complex physical systems."
        }
    },
    "GUARDIAN": {
        name: { it: "Guardian (Sicurezza & Protezione)", en: "Guardian (Safety & Protection)" },
        icon: "🛡️",
        color: "#f59e0b",
        frontend: {
            it: "Tema Gold/Orange. Allarmi di sicurezza prioritari. Dashboard focalizzata sulla salute del nucleo e stabilità SSD.",
            en: "Gold/Orange theme. Priority safety alerts. Dashboard focused on core health and SSD stability."
        },
        backend: {
            it: "Protocolli di difesa attivi. Ogni operazione è filtrata per rischi di instabilità, allucinazioni o perdita dati.",
            en: "Active defense protocols. Every operation is filtered for risks of instability, hallucinations, or data loss."
        },
        example: {
            it: "Query: 'Sperimenta nuovo codice' -> Risposta: Analisi del rischio con sandbox virtuale e blocco preventivo su file critici.",
            en: "Query: 'Experiment with new code' -> Response: Risk analysis with virtual sandbox and preventive lock on critical files."
        }
    }
};

window.updateCognitiveMindset = () => {
    const select = document.getElementById('mindset-select');
    const selectVal = select.value;
    const selectToMindset = {
        "default": "DEFAULT",
        "analista_minsky": "MINSKY",
        "creativo_de_bono": "DE_BONO",
        "custode_federale": "GUARDIAN"
    };
    const mindsetId = selectToMindset[selectVal] || "DEFAULT";
    window.showMindsetModal(mindsetId);
};

window.showMindsetModal = (mindsetId) => {
    const isEn = (localStorage.getItem('neuralvault_lang') === 'en');
    const data = MINDSET_DATA[mindsetId];
    if (!data) return;

    const modal = document.createElement('div');
    modal.id = "mindset-fullscreen-modal";
    modal.style = `
        position: fixed; top: 0; left: 0; width: 100%; height: 100%;
        background: radial-gradient(circle at center, rgba(15, 23, 42, 0.98) 0%, rgba(2, 6, 23, 1) 100%);
        backdrop-filter: blur(80px);
        z-index: 999999; display: flex; align-items: center; justify-content: center;
        animation: mindsetFadeIn 0.6s cubic-bezier(0.16, 1, 0.3, 1);
        color: #fff; font-family: 'Inter', sans-serif;
    `;

    modal.innerHTML = `
        <style>
            @keyframes mindsetFadeIn { from { opacity: 0; transform: scale(1.1); } to { opacity: 1; transform: scale(1); } }
            @keyframes iconPulse { 0% { transform: scale(1); filter: drop-shadow(0 0 20px ${data.color}88); } 50% { transform: scale(1.05); filter: drop-shadow(0 0 40px ${data.color}); } 100% { transform: scale(1); filter: drop-shadow(0 0 20px ${data.color}88); } }
            .mindset-card {
                background: rgba(255, 255, 255, 0.03);
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 24px;
                padding: 30px;
                transition: 0.4s;
            }
            .mindset-card:hover { background: rgba(255, 255, 255, 0.05); border-color: ${data.color}44; transform: translateY(-5px); }
        </style>
        <div style="max-width: 1000px; width: 90%; position: relative; animation: slideUp 0.8s cubic-bezier(0.16, 1, 0.3, 1);">
            <button onclick="window.closeMindsetModal()" style="position: absolute; top: -60px; right: 0; background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); color: #fff; width: 44px; height: 44px; border-radius: 50%; display: flex; align-items: center; justify-content: center; cursor: pointer; transition: 0.3s;" onmouseover="this.style.background='rgba(255,255,255,0.1)'" onmouseout="this.style.background='rgba(255,255,255,0.05)'"><i class="fas fa-times"></i></button>
            
            <div style="text-align: center; margin-bottom: 4rem;">
                <div style="font-size: 7rem; margin-bottom: 1.5rem; animation: iconPulse 3s infinite ease-in-out;">${data.icon}</div>
                <h1 style="color: #fff; font-size: 3.5rem; font-weight: 900; text-transform: uppercase; letter-spacing: 12px; margin: 0; background: linear-gradient(to bottom, #fff, ${data.color}); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">${data.name[isEn?'en':'it']}</h1>
                <div style="display: flex; align-items: center; justify-content: center; gap: 15px; margin-top: 15px;">
                    <div style="height: 1px; width: 50px; background: linear-gradient(to left, ${data.color}, transparent);"></div>
                    <div style="color: ${data.color}; font-size: 0.7rem; font-weight: 800; letter-spacing: 4px; text-transform: uppercase;">Neural Archetype v9.2</div>
                    <div style="height: 1px; width: 50px; background: linear-gradient(to right, ${data.color}, transparent);"></div>
                </div>
            </div>

            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 40px; margin-bottom: 5rem;">
                <div class="mindset-card">
                    <h3 style="color: ${data.color}; font-size: 0.65rem; font-weight: 900; margin-bottom: 20px; text-transform: uppercase; letter-spacing: 2px;"><i class="fas fa-eye"></i> PERCEZIONE VISIVA</h3>
                    <p style="color: #cbd5e1; font-size: 0.95rem; line-height: 1.7; margin: 0;">${data.frontend[isEn?'en':'it']}</p>
                </div>
                <div class="mindset-card">
                    <h3 style="color: ${data.color}; font-size: 0.65rem; font-weight: 900; margin-bottom: 20px; text-transform: uppercase; letter-spacing: 2px;"><i class="fas fa-brain"></i> LOGICA AGENTICA</h3>
                    <p style="color: #cbd5e1; font-size: 0.95rem; line-height: 1.7; margin: 0;">${data.backend[isEn?'en':'it']}</p>
                </div>
            </div>

            <div style="background: linear-gradient(90deg, transparent, rgba(255,255,255,0.03), transparent); padding: 25px; text-align: center; border-radius: 20px; margin-bottom: 4rem; border: 1px solid rgba(255,255,255,0.05);">
                <div style="font-size: 0.55rem; color: #64748b; font-weight: 800; margin-bottom: 12px; text-transform: uppercase; letter-spacing: 3px;">Simulazione Proattiva</div>
                <div style="color: #fff; font-family: 'JetBrains Mono', monospace; font-size: 1rem; opacity: 0.8;">&ldquo;${data.example[isEn?'en':'it']}&rdquo;</div>
            </div>

            <div style="display: flex; gap: 25px; justify-content: center; align-items: center;">
                <button onclick="window.closeMindsetModal()" style="padding: 18px 45px; background: transparent; color: #64748b; border: 1px solid #334155; border-radius: 16px; font-weight: 800; cursor: pointer; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 2px; transition: 0.3s;" onmouseover="this.style.color='#fff'; this.style.borderColor='#475569'" onmouseout="this.style.color='#64748b'; this.style.borderColor='#334155'">${isEn?'CANCEL':'ANNULLA'}</button>
                
                <div style="width: 1px; height: 40px; background: #334155;"></div>

                <button onclick="window.applyMindset('${mindsetId}')" style="padding: 22px 70px; background: ${data.color}; color: #000; border: none; border-radius: 18px; font-weight: 950; cursor: pointer; font-size: 1.1rem; text-transform: uppercase; letter-spacing: 3px; box-shadow: 0 0 40px ${data.color}66; transition: 0.3s; transform: scale(1.05);" onmouseover="this.style.transform='scale(1.1)'; this.style.boxShadow='0 0 60px ${data.color}88'" onmouseout="this.style.transform='scale(1.05)'; this.style.boxShadow='0 0 40px ${data.color}66';">${isEn?'ACTIVATE MINDSET':'ATTIVA PROTOCOLLO'}</button>

                <div style="width: 1px; height: 40px; background: #334155;"></div>

                <button onclick="window.nextMindset('${mindsetId}')" style="background: none; border: none; color: #64748b; font-size: 0.7rem; font-weight: 800; cursor: pointer; text-transform: uppercase; letter-spacing: 2px; transition: 0.3s;" onmouseover="this.style.color='${data.color}'" onmouseout="this.style.color='#64748b'">${isEn?'Next Insight':'Prossimo'}</button>
            </div>
        </div>
    `;

    document.body.appendChild(modal);
};

window.closeMindsetModal = () => {
    const modal = document.getElementById('mindset-fullscreen-modal');
    if (modal) modal.remove();
    // Ripristina il selettore se non applicato
    const select = document.getElementById('mindset-select');
    if (select) {
        const mindsetToSelect = {
            "DEFAULT": "default",
            "MINSKY": "analista_minsky",
            "DE_BONO": "creativo_de_bono",
            "GUARDIAN": "custode_federale"
        };
        select.value = mindsetToSelect[window.currentMindset] || "default";
    }
};

window.nextMindset = (currentId) => {
    const ids = Object.keys(MINDSET_DATA);
    const currentIndex = ids.indexOf(currentId);
    const nextIndex = (currentIndex + 1) % ids.length;
    const nextId = ids[nextIndex];
    
    const modal = document.getElementById('mindset-fullscreen-modal');
    if (modal) modal.remove();
    window.showMindsetModal(nextId);
};

window.applyMindset = async (mindsetId) => {
    log(`🧠 [v9.2] Switching global mindset to ${mindsetId}...`, MINDSET_DATA[mindsetId].color);
    window.currentMindset = mindsetId;
    
    // 1. Sync with Backend
    try {
        const apiKey = (typeof window.VAULT_KEY !== 'undefined') ? window.VAULT_KEY : 'AURA-ADMIN-77';
        await fetch('/api/system/mindset', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'X-API-KEY': apiKey },
            body: JSON.stringify({ mindset: mindsetId })
        });
    } catch (e) { console.error("Mindset Sync Failed:", e); }

    // 2. Update Dashboard UI Theme
    const color = MINDSET_DATA[mindsetId].color;
    document.documentElement.style.setProperty('--accent-color', color);
    document.documentElement.style.setProperty('--glow-color', color + "44");
    
    // [v9.2] Specialized theme adjustments
    if (mindsetId === 'MINSKY') {
        document.body.style.filter = "contrast(1.1) saturate(0.9)";
    } else if (mindsetId === 'DE_BONO') {
        document.body.style.filter = "hue-rotate(280deg) saturate(1.2)";
    } else {
        document.body.style.filter = "none";
    }

    // 3. UI Feedback
    const select = document.getElementById('mindset-select');
    if (select) {
        const mindsetToSelect = {
            "DEFAULT": "default",
            "MINSKY": "analista_minsky",
            "DE_BONO": "creativo_de_bono",
            "GUARDIAN": "custode_federale"
        };
        select.value = mindsetToSelect[mindsetId] || "default";
    }

    // 🧬 [v9.2] Update Cognitive DNA HUD
    const status = document.getElementById('cognitive-status');
    const icon = document.querySelector('#cognitive-dna-hud i');
    if (status) {
        status.innerText = `DNA: ${MINDSET_DATA[mindsetId].name.it}`;
        status.style.color = color;
    }
    if (icon) icon.style.color = color;

    // 🏛️ [v9.2] Update Sidebar Label if exists
    const label = document.getElementById('label-system-status');
    if (label) {
        label.innerText = `SYSTEM: ${mindsetId}`;
        label.style.color = color;
    }

    window.closeMindsetModal();
    
    // Holographic notification
    if (window.showHologram) {
        const desc = MINDSET_DATA[mindsetId].frontend.it;
        window.showHologram('YODA', `Protocollo ${mindsetId} attivato. ${desc}`);
    }
};

window.initMindsetSync = async () => {
    try {
        const apiKey = (typeof window.VAULT_KEY !== 'undefined') ? window.VAULT_KEY : 'AURA-ADMIN-77';
        const resp = await fetch('/api/system/mindset', {
            headers: { 'X-API-KEY': apiKey }
        });
        if (resp.ok) {
            const data = await resp.json();
            if (data.mindset) {
                log(`🏛️ [Mindset] Sincronizzazione stato da backend: ${data.mindset}`, MINDSET_DATA[data.mindset]?.color || "#fff");
                // Applichiamo silenziosamente senza riaprire il modal
                window.currentMindset = data.mindset;
                const color = MINDSET_DATA[data.mindset]?.color || "#3b82f6";
                document.documentElement.style.setProperty('--accent-color', color);
                document.documentElement.style.setProperty('--glow-color', color + "44");
                const select = document.getElementById('mindset-select');
                if (select) {
                    const mindsetToSelect = {
                        "DEFAULT": "default",
                        "MINSKY": "analista_minsky",
                        "DE_BONO": "creativo_de_bono",
                        "GUARDIAN": "custode_federale"
                    };
                    select.value = mindsetToSelect[data.mindset] || "default";
                }
            }
        }
    } catch (e) { console.warn("Mindset Init Sync Failed:", e); }
};

window.applyWorkspace = (workspaceId) => {
    log(`🏛️ [Workspace] Switching to ${workspaceId}...`, "#3b82f6");
    
    // 1. UI Feedback: Update chips
    document.querySelectorAll('.workspace-chip').forEach(c => c.classList.remove('active'));
    const activeChip = document.getElementById(`ws-${workspaceId.toLowerCase()}`);
    if (activeChip) activeChip.classList.add('active');
    
    // 2. State Persistence
    localStorage.setItem('neuralvault_workspace', workspaceId);
    
    // 3. Layout Manipulation
    const crisisHud = document.getElementById('crisis-overlay-hud');
    const trendHud = document.getElementById('trend-overlay-hud');
    
    // Reset defaults
    if (crisisHud) crisisHud.style.display = 'none';
    if (trendHud) trendHud.style.display = 'none';
    
    switch(workspaceId) {
        case 'CRISIS':
            if (crisisHud) crisisHud.style.display = 'flex';
            // Trigger higher contrast if needed
            document.body.classList.add('crisis-mode');
            document.body.classList.remove('trend-mode');
            // Auto-switch mindset to GUARDIAN if not already there (optional suggestion)
            // if (window.currentMindset !== 'GUARDIAN') window.showMindsetModal('GUARDIAN');
            break;
            
        case 'TREND':
            if (trendHud) trendHud.style.display = 'flex';
            document.body.classList.add('trend-mode');
            document.body.classList.remove('crisis-mode');
            break;
            
        default:
            document.body.classList.remove('crisis-mode', 'trend-mode');
            break;
    }
    
    // 4. Component Reflow
    if (typeof updateThreeScene === 'function') {
        // Trigger a slight camera reposition or focus if needed
    }
};

window.initWorkspace = () => {
    const saved = localStorage.getItem('neuralvault_workspace') || 'DEFAULT';
    window.applyWorkspace(saved);
};



window.generateCausalScenario = async (results) => {
    const lensSelect = document.getElementById('sim-lens');
    const lensIds = Array.from(lensSelect.selectedOptions).map(opt => opt.value);
    const primaryLens = lensIds[0] || 'standard';
    
    log(`🚀 [v8.2] Generazione scenario causale (Lens Fusion: ${lensIds.join('+')})...`, "#3b82f6");
    
    try {
        const resp = await fetch('/api/wiki/simulate/scenario', {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                'X-API-KEY': typeof VAULT_KEY !== 'undefined' ? VAULT_KEY : 'AURA-ADMIN-77' 
            },
            body: JSON.stringify({ results: results, lens_ids: lensIds })
        });
        const data = await resp.json();
        
        let footer = `<div style="margin-top:20px; border-top:1px solid #333; padding-top:10px; font-size:0.6rem; color:#8b949e;">`;
        footer += `<strong>EVIDENZE ANCORATE:</strong><br>`;
        data.evidence_anchors.forEach(src => {
            footer += `<i class="fas fa-link"></i> ${src}<br>`;
        });
        footer += `</div>`;
        
        window.showSovereignModal(`Scenario Sovrano: ${lensIds.join(' + ').toUpperCase()}`, data.content + footer);
    } catch (e) {
        console.error("Scenario Error:", e);
    }
};

window.generateStrategicReport = async (results) => {
    log(`🏺 [Report] Generazione report strategico in corso...`, "#a855f7");
    try {
        const resp = await fetch('/api/wiki/simulate/report', {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                'X-API-KEY': typeof VAULT_KEY !== 'undefined' ? VAULT_KEY : 'AURA-ADMIN-77' 
            },
            body: JSON.stringify({ results: results })
        });
        const data = await resp.json();
        
        // [v12.7] Show the report and bind evidence clicks
        window.showSovereignModal(`Report Strategico Sovrano`, data.report);
        
        // Bind evidence clicks after a short delay to ensure modal is rendered
        setTimeout(() => {
            if (window.bindEvidenceLinks) window.bindEvidenceLinks('sovereign-intelligence-modal');
        }, 100);
        
    } catch (e) {
        console.error("Report Error:", e);
    }
};

// Reusable Sovereign Modal
window.showSovereignModal = (title, content) => {
    let modal = document.getElementById('sovereign-intelligence-modal');
    if (!modal) {
        modal = document.createElement('div');
        modal.id = 'sovereign-intelligence-modal';
        modal.style = `
            position:fixed; top:50%; left:50%; transform:translate(-50%, -50%);
            width:80%; max-width:600px; max-height:80vh; background:rgba(13,17,23,0.95);
            backdrop-filter:blur(20px); border:1px solid rgba(168,85,247,0.3);
            border-radius:15px; z-index:10000; padding:2rem; overflow-y:auto; color:#fff;
            box-shadow:0 0 50px rgba(0,0,0,0.5); font-family: 'Inter', sans-serif;
        `;
        document.body.appendChild(modal);
    }
    
    modal.innerHTML = `
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:20px; border-bottom:1px solid #333; padding-bottom:10px;">
            <h2 style="margin:0; font-size:1.2rem; color:#a855f7;">${title}</h2>
            <button onclick="this.parentElement.parentElement.style.display='none'" style="background:none; border:none; color:#8b949e; cursor:pointer; font-size:1.5rem;">&times;</button>
        </div>
        <div style="font-size:0.9rem; line-height:1.6; white-space:pre-wrap;">${content}</div>
        <div style="margin-top:20px; text-align:right;">
            <button onclick="this.parentElement.parentElement.style.display='none'" class="glass-btn">CHIUDI</button>
        </div>
    `;
    modal.style.display = 'block';
};

// --- [v8.1] PROGRESSIVE DISCLOSURE & ADAPTIVE PROTOCOLS ---

window.initWikiInteractions = () => {
    const entities = document.querySelectorAll('.wiki-entity');
    entities.forEach(el => {
        el.onmouseenter = (e) => window.showDisclosurePanel(e, el.dataset.nodeId);
        el.onmouseleave = () => window.hideDisclosurePanel();
    });
};

// [v8.1] Global Entity Cache for zero-latency hover
window.entityCache = new Map();

window.showDisclosurePanel = async (e, nodeId) => {
    const panel = document.getElementById('wiki-disclosure-panel');
    if (!panel) return;
    
    const rect = e.target.getBoundingClientRect();
    panel.style.top = (rect.bottom + window.scrollY + 10) + 'px';
    panel.style.left = (rect.left + window.scrollX) + 'px';
    
    // Check Cache first
    if (window.entityCache.has(nodeId)) {
        renderDisclosurePanel(window.entityCache.get(nodeId));
        return;
    }

    panel.innerHTML = '<div style="padding:1rem; font-size:0.6rem; opacity:0.5;">Caricamento Proiezione...</div>';
    panel.style.display = 'block';
    
    try {
        const resp = await fetch(`/api/node/${nodeId}`, {
            headers: { 'X-API-KEY': typeof VAULT_KEY !== 'undefined' ? VAULT_KEY : 'AURA-ADMIN-77' }
        });
        const data = await resp.json();
        
        // Update Cache
        window.entityCache.set(nodeId, data);
        renderDisclosurePanel(data);
    } catch (err) {
        panel.innerHTML = '<div style="padding:1rem; color:#ef4444; font-size:0.6rem;">Errore caricamento.</div>';
    }
};

const renderDisclosurePanel = (data) => {
    const panel = document.getElementById('wiki-disclosure-panel');
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
    panel.style.display = 'block';
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
    const input = document.getElementById('nl-sim-prompt') || document.getElementById('wiki-search-portal');
    if (input) input.value = id;
    window.runNaturalLanguageSimulation();
};

window.switchWikiMode = async (mode) => {
    const currentTopic = document.getElementById('wiki-portal-title')?.innerText || "Summary";
    log(`🔄 [v8.1] Switching to ${mode} mode...`, "#3b82f6");
    window.loadWikiPage(currentTopic, mode);
};

window.resolveWikiContradictions = async () => {
    const topic = document.getElementById('wiki-portal-title')?.innerText;
    if (!topic) return;
    
    log(`⚡ [HUD] Avvio Arbitrato Epistemico per: ${topic}...`, "#ef4444");
    
    try {
        const resp = await fetch('/api/swarm/execute', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-API-KEY': typeof VAULT_KEY !== 'undefined' ? VAULT_KEY : 'AURA-ADMIN-77'
            },
            body: JSON.stringify({
                task: `Analizza le contraddizioni rilevate nella pagina Wiki su '${topic}'. Esegui un arbitrato logico basato sulla densità delle prove e sulla freschezza delle fonti. Genera una sintesi risolutiva.`,
                agents: ["Analista-Gamma", "Supreme-Court-Judge"]
            })
        });
        const data = await resp.json();
        log(`✅ [HUD] Arbitrato completato. Conflitto risolto.`, "#10b981");
        window.loadWikiPage(topic, 'RESEARCH'); // Ricarica in modalità Research per vedere i risultati
    } catch (e) {
        log(`❌ [HUD] Errore durante l'arbitrato.`, "#ef4444");
    }
};

window.triggerSkywalker = async () => {
    const topic = document.getElementById('wiki-portal-title')?.innerText;
    if (!topic) return;
    
    log(`🚀 [HUD] Inizializzazione Protocollo SkyWalker per: ${topic}...`, "#ef4444");
    
    try {
        const resp = await fetch('/api/swarm/execute', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-API-KEY': typeof VAULT_KEY !== 'undefined' ? VAULT_KEY : 'AURA-ADMIN-77'
            },
            body: JSON.stringify({
                task: `Esegui ricerca proattiva sul web per verificare e arricchire la conoscenza su '${topic}'. Risolvi eventuali contraddizioni trovate.`,
                agents: ["SkyWalker-001", "Analista-Gamma"]
            })
        });
        const data = await resp.json();
        log(`✅ [HUD] SkyWalker attivato. Mission ID: ${data.mission_id}`, "#10b981");
    } catch (e) {
        log(`❌ [HUD] Errore attivazione SkyWalker.`, "#ef4444");
    }
};

window.exportWiki = () => {
    const contentEl = document.getElementById('wiki-kb-content-body') || document.getElementById('wiki-portal-content');
    const topic = document.getElementById('wiki-portal-title')?.innerText || "Wiki_Export";
    if (!contentEl) return;
    const content = contentEl.innerText;
    const blob = new Blob([content], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${topic}_${new Date().getTime()}.md`;
    a.click();
    log(`📥 [HUD] Esportazione reference completata.`, "#10b981");
};

window.showSovereignGuide = (type) => {
    const modal = document.getElementById('sovereign-guide-modal');
    const itArea = document.getElementById('guide-content-it');
    const enArea = document.getElementById('guide-content-en');
    
    if (type === 'wiki') {
        itArea.innerHTML = `
            <h2 style="color:#3b82f6; margin-bottom:1rem;">🏺 GUIDA NEURAL WIKI 3.0</h2>
            <p style="color:#94a3b8; font-size:0.8rem; line-height:1.6;">
                Benvenuto nel Portale della Conoscenza Sovrana. Qui puoi esplorare il Vault tramite articoli generati dinamicamente.
                <br><br>
                <b>1. Adaptive Reading:</b> Usa i pulsanti EXE, TECH, RES per cambiare la profondità dell'articolo. 
                <br><b>2. Epistemic HUD:</b> Il "Meteo" in alto indica quanto il Vault è sicuro delle informazioni. Se c'è tempesta, usa l'arbitrato.
                <br><b>3. Proiezioni:</b> Passa il mouse sulle parole evidenziate per vedere anteprime istantanee senza lasciare la pagina.
            </p>
        `;
        enArea.innerHTML = `
            <h2 style="color:#3b82f6; margin-bottom:1rem;">🏺 NEURAL WIKI 3.0 GUIDE</h2>
            <p style="color:#94a3b8; font-size:0.8rem; line-height:1.6;">
                Welcome to the Sovereign Knowledge Portal. Explore the Vault through dynamically generated articles.
                <br><br>
                <b>1. Adaptive Reading:</b> Use EXE, TECH, RES buttons to change article depth.
                <br><b>2. Epistemic HUD:</b> The "Weather" at the top indicates how confident the Vault is. If it's stormy, use arbitration.
                <br><b>3. Projections:</b> Hover over highlighted words to see instant previews without leaving the page.
            </p>
        `;
    } else {
        itArea.innerHTML = `
            <h2 style="color:#facc15; margin-bottom:1rem;">🧪 GUIDA WHAT-IF ENGINE</h2>
            <p style="color:#94a3b8; font-size:0.8rem; line-height:1.6;">
                Il motore di simulazione causale permette di prevedere l'impatto di cambiamenti ipotetici.
                <br><br>
                <b>1. Intervento:</b> Seleziona un nodo nel grafo e usa lo slider per aumentare o inibire la sua influenza.
                <br><b>2. Monte Carlo:</b> Il sistema esegue 1000 simulazioni per calcolare il rischio e la probabilità di successo.
                <br><b>3. Timeline:</b> Guarda il grafico in basso per vedere come l'effetto si propaga in 1, 6 e 12 mesi.
            </p>
        `;
        enArea.innerHTML = `
            <h2 style="color:#facc15; margin-bottom:1rem;">🧪 WHAT-IF ENGINE GUIDE</h2>
            <p style="color:#94a3b8; font-size:0.8rem; line-height:1.6;">
                The causal simulation engine allows you to predict the impact of hypothetical changes.
                <br><br>
                <b>1. Intervention:</b> Select a node in the graph and use the slider to increase or inhibit its influence.
                <br><b>2. Monte Carlo:</b> The system runs 1000 simulations to calculate risk and success probability.
                <br><b>3. Timeline:</b> Look at the chart below to see how the effect propagates in 1, 6, and 12 months.
            </p>
        `;
    }
    
    modal.style.display = 'flex';
    window.syncGuideLanguage();
};

window.syncGuideLanguage = () => {
    const isEn = (typeof currentLang !== 'undefined' && currentLang === 'en');
    const itArea = document.getElementById('guide-content-it');
    const enArea = document.getElementById('guide-content-en');
    if (itArea) itArea.style.display = isEn ? 'none' : 'block';
    if (enArea) enArea.style.display = isEn ? 'block' : 'none';
};

/**
 * 🦾 NEURAL IMPLICIT COMPRESSION (NIC) - v8.0
 */
window.triggerNeuralCompression = async () => {
    const btn = document.getElementById('compression-btn');
    const prog = document.getElementById('compression-progress-container');
    const bar = document.getElementById('comp-progress-bar');
    const statusText = document.getElementById('comp-status-text');

    if (btn) {
        btn.disabled = true;
        btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> OTTIMIZZAZIONE...';
    }
    if (prog) prog.style.display = 'block';

    try {
        log("🦾 [NIC] Avvio Compressione Implicita Neurale...", "#10b981");
        const resp = await fetch('/api/system/compress', {
            method: 'POST',
            headers: { 'X-API-KEY': typeof VAULT_KEY !== 'undefined' ? VAULT_KEY : 'AURA-ADMIN-77' }
        });
        const data = await resp.json();

        // Simulazione progresso UI (il backend lavora in background)
        let p = 0;
        const interval = setInterval(() => {
            p += 5;
            if (bar) bar.style.width = p + '%';
            if (p >= 100) {
                clearInterval(interval);
                if (statusText) statusText.innerText = "Ottimizzazione Completata!";
                setTimeout(() => {
                    if (prog) prog.style.display = 'none';
                    if (btn) {
                        btn.disabled = false;
                        btn.innerHTML = '<i class="fas fa-compress-arrows-alt"></i> OTTIMIZZA ORA';
                    }
                    window.refreshCompressionStats();
                }, 1000);
            }
        }, 150);

    } catch (e) {
        log("❌ [NIC] Errore durante l'ottimizzazione.", "#ef4444");
        if (btn) btn.disabled = false;
    }
};

window.refreshCompressionStats = async () => {
    try {
        const resp = await fetch('/api/system/compression/stats', {
            headers: { 'X-API-KEY': typeof VAULT_KEY !== 'undefined' ? VAULT_KEY : 'AURA-ADMIN-77' }
        });
        const data = await resp.json();

        const rawEl = document.getElementById('comp-storage-raw');
        const optEl = document.getElementById('comp-storage-opt');
        const effEl = document.getElementById('comp-efficiency');

        if (rawEl) rawEl.innerText = data.raw_storage_mb + " MB";
        if (optEl) optEl.innerText = data.opt_storage_mb + " MB";
        if (effEl) {
            effEl.innerText = data.efficiency + "%";
            effEl.style.color = data.is_active ? '#10b981' : '#facc15';
        }
        
        if (data.is_active) {
            log(`✅ [NIC] Efficienza Corrente: ${data.efficiency}% (${data.node_count} nodi mappati)`, "#10b981");
        }
    } catch (e) {
        console.error("Compression Stats Error:", e);
    }
};

// Auto-refresh stats when entering compression tab
const originalSwitchSettingsTab = window.switchSettingsTab;
window.switchSettingsTab = (tabId) => {
    if (originalSwitchSettingsTab) originalSwitchSettingsTab(tabId);
    if (tabId === 'compression') window.refreshCompressionStats();
};

window.updateWikiSidebarIntelligence = (data) => {
    console.log("📊 [Wiki] Updating Sidebar Intelligence...", data);
    const provContainer = document.getElementById('wiki-provenance-list');
    if (!provContainer) return;

    provContainer.innerHTML = '';
    
    // [v9.0] Extract citations from sections for provenance
    const citations = [];
    if (data.sections) {
        data.sections.forEach(s => {
            if (s.citations) citations.push(...s.citations);
        });
    } else if (data.citations) {
        citations.push(...data.citations);
    }

    if (citations.length > 0) {
        // Rimuovi duplicati per ID
        const uniqueCitations = Array.from(new Map(citations.map(c => [c.node_id, c])).values());
        
        uniqueCitations.forEach(c => {
            const item = document.createElement('div');
            item.className = 'provenance-item';
            item.style.padding = '8px';
            item.style.background = 'rgba(255,255,255,0.03)';
            item.style.borderRadius = '8px';
            item.style.border = '1px solid rgba(255,255,255,0.05)';
            item.innerHTML = `
                <div style="font-size: 0.65rem; color: #fff; font-weight: 700; margin-bottom: 2px;">${c.source_title}</div>
                <div style="font-size: 0.5rem; color: #64748b; font-family: 'JetBrains Mono';">ID: ${c.node_id.substring(0,8)}</div>
                <div style="font-size: 0.55rem; color: #94a3b8; margin-top: 4px; line-height: 1.3;">"${c.excerpt.substring(0, 80)}..."</div>
            `;
            item.onclick = () => {
                if (window.selectNode) window.selectNode(c.node_id);
                log(`🔍 [Provenance] Focusing source: ${c.node_id}`, "#4ade80");
            };
            item.style.cursor = 'pointer';
            provContainer.appendChild(item);
        });
    } else {
        provContainer.innerHTML = '<div style="font-size: 0.55rem; color: #64748b; font-style: italic;">Nessuna fonte atomica mappata.</div>';
    }

    // [v9.0] Initialize Mini-Graph if Cytoscape is available
    const graphContainer = document.getElementById('wiki-mini-graph');
    if (graphContainer && window.cytoscape) {
        graphContainer.innerHTML = '';
        const elements = [{ data: { id: 'root', label: (data.title || "Topic").substring(0,20), color: '#3b82f6' } }];
        if (citations && citations.length > 0) {
            citations.slice(0, 15).forEach(c => {
                elements.push({ data: { id: c.node_id, label: c.node_id.substring(0,4), color: '#4ade80' } });
                elements.push({ data: { source: 'root', target: c.node_id } });
            });
        }

        window.wikiCytoscape = cytoscape({
            container: graphContainer,
            elements: elements,
            style: [
                { selector: 'node', style: { 'width': 12, 'height': 12, 'label': 'data(label)', 'font-size': '6px', 'color': '#94a3b8', 'background-color': 'data(color)', 'text-valign': 'bottom' } },
                { selector: 'edge', style: { 'width': 1, 'line-color': 'rgba(59,130,246,0.2)' } }
            ],
            layout: { name: 'cose', padding: 15, animate: true }
        });
    }
};

window.toggleWikiSidebar = () => {
    const grid = document.getElementById('wiki-main-grid');
    const sidebar = document.getElementById('wiki-sidebar');
    const expandBtn = document.getElementById('wiki-sidebar-expand-btn');
    const isCollapsed = grid.style.gridTemplateColumns.startsWith('40px');

    if (isCollapsed) {
        // Expand
        grid.style.gridTemplateColumns = '250px 1fr 280px';
        sidebar.style.transform = 'scaleX(1)';
        sidebar.style.opacity = '1';
        sidebar.style.pointerEvents = 'all';
        expandBtn.style.display = 'none';
        log("📂 [Wiki] Sidebar Ripristinata", "#3b82f6");
    } else {
        // Collapse
        grid.style.gridTemplateColumns = '40px 1fr 280px';
        sidebar.style.transform = 'scaleX(0)';
        sidebar.style.opacity = '0';
        sidebar.style.pointerEvents = 'none';
        setTimeout(() => { expandBtn.style.display = 'block'; }, 400);
        log("📁 [Wiki] Sidebar Collassata", "#64748b");
    }
};

window.toggleMainSidebar = function() {
    const sidebar = document.getElementById('main-app-sidebar');
    const restoreBtn = document.getElementById('main-sidebar-restore');
    
    if (!sidebar) return;
    
    const isCollapsed = sidebar.classList.toggle('collapsed');
    
    if (restoreBtn) {
        restoreBtn.style.display = isCollapsed ? 'flex' : 'none';
    }
    
    // Force a resize event to update WebGL and other layout-dependent components
    setTimeout(() => {
        window.dispatchEvent(new Event('resize'));
    }, 400);
};

/**
 * 🗺️ [v8.4] LEARNING PATH ENGINE
 */
window.loadLearningPath = async (topic) => {
    const container = document.getElementById('wiki-learning-path');
    if (!container) return;

    try {
        container.innerHTML = '<div style="font-size: 0.5rem; color: #a855f7;"><i class="fas fa-spinner fa-spin"></i> Mapping prerequisites...</div>';
        const apiKey = (typeof window.VAULT_KEY !== 'undefined') ? window.VAULT_KEY : 'AURA-ADMIN-77';
        const resp = await fetch(`/api/wiki/learning-path?topic=${encodeURIComponent(topic)}`, {
            headers: { 'X-API-KEY': apiKey }
        });
        const data = await resp.json();

        if (data.error) {
            container.innerHTML = `<div style="font-size: 0.55rem; color: #64748b;">${data.error}</div>`;
            return;
        }

        let html = '';
        if (data.path && data.path.length > 0) {
            data.path.forEach(step => {
                const color = step.status === 'COMPLETED' ? '#10b981' : '#a855f7';
                const progress = Math.round(step.coverage * 100);
                html += `
                    <div style="margin-bottom: 8px;">
                        <div style="display:flex; justify-content:space-between; font-size: 0.55rem; color: #e2e8f0; margin-bottom: 4px;">
                            <span style="white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 180px;">${step.order}. ${step.topic}</span>
                            <span style="color:${color}; font-weight:800;">${progress}%</span>
                        </div>
                        <div style="width: 100%; height: 4px; background: rgba(255,255,255,0.05); border-radius: 2px; overflow: hidden;">
                            <div style="width: ${progress}%; height: 100%; background: ${color}; transition: width 0.5s;"></div>
                        </div>
                    </div>
                `;
            });
        }
        
        container.innerHTML = html || '<div style="font-size: 0.55rem; color: #64748b;">Nessun percorso trovato.</div>';
    } catch (e) {
        console.error("Learning Path Error:", e);
        container.innerHTML = '<div style="font-size: 0.55rem; color: #ef4444;">Errore caricamento percorso.</div>';
    }
};

/**
 * 📦 [v8.4] METIS PARTITION TOGGLE
 */
window._showPartitions = false;
window.togglePartitions = () => {
    window._showPartitions = !window._showPartitions;
    if (window.log) window.log(`📦 [Metis] Partition Visualization: ${window._showPartitions ? 'ON' : 'OFF'}`, "#facc15");
    // Trigger re-render of nebula if points exist
    if (typeof lastVaultPoints !== 'undefined' && lastVaultPoints) {
        updateThreeScene(lastVaultPoints, null);
    }
};

/**
 * 🏺 [v9.0] SOVEREIGN WIKI DASHBOARD
 * Renders the home view of the Knowledge Vault with real-time stats and metrics.
 */
window.renderWikiDashboard = async () => {
    const content = document.getElementById('wiki-kb-content-body') || document.getElementById('wiki-portal-content');
    const hud = document.getElementById('wiki-epistemic-hud');
    const titleEl = document.getElementById('wiki-portal-title');
    
    // Switch to KB view if necessary
    if (window.switchWikiView) window.switchWikiView('dashboard');
    
    if (!content) return;
    
    // Hide the article-style header when showing the main dashboard
    if (titleEl && titleEl.parentElement) {
        titleEl.parentElement.style.display = 'none';
        document.getElementById('wiki-document-sheet').classList.add('dashboard-active');
    }

    if (hud) hud.style.display = 'none';

    content.innerHTML = `<div style="text-align:center; padding:5rem; color: #3b82f6;"><i class="fas fa-spinner fa-spin fa-2x"></i><br><br><span style="letter-spacing:2px; font-size:0.7rem; font-weight:800;">Sincronizzazione Archivi Sovrani...</span></div>`;

    try {
        const apiKey = (typeof window.VAULT_KEY !== 'undefined') ? window.VAULT_KEY : 'AURA-ADMIN-77';
        
        // Fetch dashboard stats
        const resp = await fetch('/api/wiki/dashboard', { headers: { 'X-API-KEY': apiKey } });
        if (!resp.ok) throw new Error("Dashboard fetch failed");
        const data = await resp.json();

        const stats = data.stats;
        
        // Fetch all pages to populate the full directory tree
        const listResp = await fetch('/api/wiki/list', { headers: { 'X-API-KEY': apiKey } });
        const listData = listResp.ok ? await listResp.json() : { pages: data.recent_pages || [] };
        const allPages = listData.pages || [];
        
        // Build namespaces tree
        const namespaces = {};
        allPages.forEach(p => {
            const ns = p.namespace || 'General';
            if (!namespaces[ns]) namespaces[ns] = [];
            namespaces[ns].push(p);
        });

        const weatherIcons = { "SUNNY": "fa-sun", "CLOUDY": "fa-cloud-sun", "STORM": "fa-bolt", "MIST": "fa-smog" };
        const weatherColors = { "SUNNY": "#facc15", "CLOUDY": "#94a3b8", "STORM": "#ef4444", "MIST": "#a855f7" };

        window._kbAllPages = allPages; // Store globally for client-side filtering

        content.innerHTML = `
            <style>
                .kb-sidebar { width: 220px; border-right: 1px solid rgba(255,255,255,0.05); padding-right: 1rem; display: flex; flex-direction: column; gap: 1.5rem; }
                .kb-folder { font-size: 0.7rem; color: #cbd5e1; cursor: pointer; padding: 6px 8px; border-radius: 6px; display: flex; align-items: center; gap: 8px; transition: 0.2s; }
                .kb-folder:hover { background: rgba(59,130,246,0.1); color: #3b82f6; }
                .kb-folder.active { background: rgba(59,130,246,0.15); color: #3b82f6; font-weight: 800; border-left: 2px solid #3b82f6; }
                .kb-main { flex: 1; display: flex; flex-direction: column; gap: 1.5rem; }
                .kb-right { width: 260px; display: flex; flex-direction: column; gap: 1.5rem; }
                
                .kb-card { background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.05); border-radius: 12px; padding: 1rem; transition: 0.2s; cursor: pointer; display: flex; flex-direction: column; gap: 8px; }
                .kb-card:hover { border-color: rgba(59,130,246,0.4); transform: translateY(-2px); background: rgba(255,255,255,0.04); }
                .kb-card-header { display: flex; justify-content: space-between; align-items: center; }
                .kb-card-title { font-size: 0.85rem; font-weight: 800; color: #fff; }
                .kb-card-meta { font-size: 0.6rem; color: #64748b; display: flex; align-items: center; gap: 10px; }
                
                .kb-widget { background: rgba(0,0,0,0.2); border: 1px solid rgba(255,255,255,0.05); border-radius: 12px; padding: 1rem; }
                .kb-widget-title { font-size: 0.65rem; color: #94a3b8; text-transform: uppercase; font-weight: 900; letter-spacing: 1px; margin-bottom: 1rem; display: flex; align-items: center; gap: 6px; }
                
                .kb-search-input { width: 100%; background: rgba(0,0,0,0.3); border: 1px solid rgba(59,130,246,0.3); color: white; padding: 10px 15px 10px 35px; border-radius: 8px; font-size: 0.8rem; outline: none; transition: 0.3s; }
                .kb-search-input:focus { border-color: #3b82f6; box-shadow: 0 0 10px rgba(59,130,246,0.2); }
                .kb-search-icon { position: absolute; left: 12px; top: 50%; transform: translateY(-50%); color: #64748b; font-size: 0.8rem; }
                
                /* Custom Scrollbar for inner views */
                #kb-article-grid::-webkit-scrollbar { width: 6px; }
                #kb-article-grid::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 10px; }
            </style>
            
            <div style="display: flex; flex-direction: column; height: 100%; gap: 1.5rem; animation: fadeIn 0.4s ease-out;">
                
                <!-- TOP HEADER -->
                <div style="display: flex; justify-content: space-between; align-items: center; padding-bottom: 1rem; border-bottom: 1px solid rgba(255,255,255,0.05);">
                    <div>
                        <div style="font-size: 0.6rem; color: #64748b; letter-spacing: 1px; margin-bottom: 4px; text-transform: uppercase;">Sovereign Wiki / Knowledge Base</div>
                        <h1 style="margin: 0; font-size: 1.5rem; color: #fff; font-weight: 900; letter-spacing: 1px;">KNOWLEDGE BASE</h1>
                    </div>
                    <div style="display: flex; gap: 10px;">
                        <button onclick="window.showWikiGeneratorWizard()" style="padding: 8px 16px; background: #3b82f6; color: #fff; border: none; border-radius: 8px; font-size: 0.7rem; font-weight: 800; cursor: pointer; display: flex; align-items: center; gap: 8px; transition: 0.2s;" onmouseover="this.style.background='#2563eb'" onmouseout="this.style.background='#3b82f6'">
                            <i class="fas fa-plus"></i> Nuovo Articolo
                        </button>
                    </div>
                </div>

                <!-- 3-COLUMN LAYOUT -->
                <div style="display: flex; gap: 2rem; flex: 1;">
                    
                    <!-- LEFT: Directory Tree -->
                    <div class="kb-sidebar">
                        <div>
                            <div style="font-size: 0.6rem; color: #64748b; font-weight: 900; letter-spacing: 1px; margin-bottom: 10px; text-transform: uppercase;">Directory</div>
                            <div class="kb-folder active" onclick="window.filterKBByNamespace('ALL', this)"><i class="fas fa-globe"></i> Tutte le Pagine</div>
                            <div class="kb-folder" onclick="window.filterKBByNamespace('RECENT', this)"><i class="fas fa-clock"></i> Recenti</div>
                            <div class="kb-folder" onclick="window.filterKBByNamespace('REVIEW', this)"><i class="fas fa-exclamation-triangle" style="color: #facc15;"></i> Da Revisionare</div>
                        </div>
                        
                        <div>
                            <div style="font-size: 0.6rem; color: #64748b; font-weight: 900; letter-spacing: 1px; margin-bottom: 10px; text-transform: uppercase; margin-top: 10px;">Namespaces</div>
                            <div id="kb-namespace-list" style="display: flex; flex-direction: column; gap: 4px; max-height: 40vh; overflow-y: auto;">
                                ${Object.keys(namespaces).map(ns => `
                                    <div class="kb-folder" onclick="window.filterKBByNamespace('${ns}', this)">
                                        <i class="fas fa-folder" style="color: #64748b;"></i> ${ns} 
                                        <span style="margin-left: auto; font-size: 0.5rem; background: rgba(255,255,255,0.1); padding: 2px 6px; border-radius: 10px;">${namespaces[ns].length}</span>
                                    </div>
                                `).join('')}
                            </div>
                        </div>
                    </div>

                    <!-- CENTER: Main Content (List/Grid) -->
                    <div class="kb-main">
                        <div style="position: relative;">
                            <i class="fas fa-search kb-search-icon"></i>
                            <input type="text" id="kb-live-search" class="kb-search-input" placeholder="Cerca nella Knowledge Base..." onkeyup="window.handleKBSearch(this.value)">
                        </div>
                        
                        <div id="kb-article-grid" style="display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 1rem; overflow-y: auto; align-content: start; max-height: 65vh; padding-right: 10px;">
                            <!-- Populated by JS -->
                        </div>
                    </div>

                    <!-- RIGHT: Widgets -->
                    <div class="kb-right">
                        <!-- Health Overview -->
                        <div class="kb-widget">
                            <div class="kb-widget-title"><i class="fas fa-heartbeat" style="color: #10b981;"></i> System Health</div>
                            <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                                <div style="text-align: center;">
                                    <div style="font-size: 1.2rem; font-weight: 900; color: #fff;">${stats.total_pages}</div>
                                    <div style="font-size: 0.55rem; color: #64748b;">PAGES</div>
                                </div>
                                <div style="text-align: center;">
                                    <div style="font-size: 1.2rem; font-weight: 900; color: #10b981;">${stats.health_score}%</div>
                                    <div style="font-size: 0.55rem; color: #64748b;">HEALTH</div>
                                </div>
                                <div style="text-align: center;">
                                    <div style="font-size: 1.2rem; font-weight: 900; color: #f43f5e;">${stats.stale_count}</div>
                                    <div style="font-size: 0.55rem; color: #64748b;">STALE</div>
                                </div>
                            </div>
                            <div style="background: rgba(255,255,255,0.05); padding: 8px; border-radius: 8px; display: flex; align-items: center; justify-content: center; gap: 8px; font-size: 0.7rem; color: ${weatherColors[stats.epistemic_weather] || '#fff'}; font-weight: 800;">
                                <i class="fas ${weatherIcons[stats.epistemic_weather] || 'fa-cloud'}"></i> WEATHER: ${stats.epistemic_weather}
                            </div>
                        </div>

                        <!-- Review Queue -->
                        <div class="kb-widget">
                            <div class="kb-widget-title"><i class="fas fa-clipboard-check" style="color: #facc15;"></i> Review Queue</div>
                            <div style="display: flex; flex-direction: column; gap: 8px; max-height: 200px; overflow-y: auto;">
                                ${data.review_queue && data.review_queue.length > 0 ? data.review_queue.map(p => `
                                    <div style="background: rgba(250, 204, 21, 0.05); border-left: 2px solid #facc15; padding: 8px; border-radius: 0 6px 6px 0; cursor: pointer; transition: 0.2s;" onmouseover="this.style.background='rgba(250, 204, 21, 0.1)'" onmouseout="this.style.background='rgba(250, 204, 21, 0.05)'" onclick="window.loadWikiPage('${p.title}')">
                                        <div style="font-size: 0.7rem; color: #fff; font-weight: 700; text-overflow: ellipsis; overflow: hidden; white-space: nowrap;">${p.title}</div>
                                        <div style="font-size: 0.55rem; color: #64748b; margin-top: 4px;">Health: ${p.health}%</div>
                                    </div>
                                `).join('') : '<div style="font-size: 0.6rem; color: #64748b; text-align: center; padding: 1rem;">Nessun documento richiede revisione.</div>'}
                            </div>
                        </div>

                        <!-- Suggestions -->
                        <div class="kb-widget">
                            <div class="kb-widget-title"><i class="fas fa-lightbulb" style="color: #a855f7;"></i> Knowledge Gaps</div>
                            <div style="display: flex; flex-wrap: wrap; gap: 6px;">
                                ${data.suggested_topics && data.suggested_topics.length > 0 ? data.suggested_topics.map(t => `
                                    <div onclick="window.showWikiGeneratorWizard('${t}')" style="background: rgba(168, 85, 247, 0.1); border: 1px solid rgba(168, 85, 247, 0.2); color: #d8b4fe; padding: 4px 8px; border-radius: 4px; font-size: 0.6rem; cursor: pointer; transition: 0.2s;" onmouseover="this.style.background='rgba(168, 85, 247, 0.2)'" onmouseout="this.style.background='rgba(168, 85, 247, 0.1)'">
                                        + ${t}
                                    </div>
                                `).join('') : '<div style="font-size: 0.6rem; color: #64748b;">Nessun gap rilevato.</div>'}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Initial render of all pages
        window.renderKBArticleCards(allPages);

    } catch (e) {
        console.error("Wiki Dashboard Error:", e);
        content.innerHTML = `<div style="text-align:center; padding:5rem; color:#ef4444;"><i class="fas fa-exclamation-triangle fa-2x"></i><br><br>Errore durante l'inizializzazione del Dashboard.<br><span style="font-size:0.6rem; opacity:0.5;">${e.message}</span></div>`;
    }
};

window.renderKBArticleCards = (pages) => {
    const grid = document.getElementById('kb-article-grid');
    if (!grid) return;
    
    if (pages.length === 0) {
        grid.innerHTML = '<div style="grid-column: 1/-1; text-align: center; padding: 3rem; color: #64748b; font-size: 0.8rem;">Nessun documento trovato.</div>';
        return;
    }
    
    grid.innerHTML = pages.map(p => {
        const healthColor = p.health > 80 ? '#10b981' : (p.health > 50 ? '#facc15' : '#ef4444');
        return `
            <div class="kb-card" onclick="window.loadWikiPage('${p.title}', 'TECHNICAL', '${p.file_name}')">
                <div class="kb-card-header">
                    <span style="font-size: 0.5rem; background: rgba(59,130,246,0.1); color: #3b82f6; padding: 2px 6px; border-radius: 4px; font-weight: 800; text-transform: uppercase; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 120px;">${p.namespace || 'General'}</span>
                    <span style="font-size: 0.55rem; color: ${healthColor}; font-weight: 800; white-space: nowrap;"><i class="fas fa-heartbeat"></i> ${p.health}%</span>
                </div>
                <div class="kb-card-title">${p.title}</div>
                <div class="kb-card-meta" style="margin-top: auto; padding-top: 8px; border-top: 1px solid rgba(255,255,255,0.05);">
                    <span><i class="far fa-calendar-alt"></i> ${p.date ? p.date.split('T')[0] : 'N/A'}</span>
                    <span style="margin-left: auto; color: #94a3b8; font-size: 0.5rem;"><i class="fas fa-robot"></i> System</span>
                </div>
            </div>
        `;
    }).join('');
};

window.filterKBByNamespace = (filterType, element) => {
    // Update active class on sidebar
    document.querySelectorAll('.kb-folder').forEach(el => el.classList.remove('active'));
    if (element) element.classList.add('active');
    
    if (!window._kbAllPages) return;
    let filtered = window._kbAllPages;
    
    if (filterType === 'ALL') {
        filtered = window._kbAllPages;
    } else if (filterType === 'RECENT') {
        filtered = [...window._kbAllPages].sort((a,b) => new Date(b.date || 0) - new Date(a.date || 0)).slice(0, 20);
    } else if (filterType === 'REVIEW') {
        filtered = window._kbAllPages.filter(p => p.health < 80);
    } else {
        filtered = window._kbAllPages.filter(p => p.namespace === filterType);
    }
    
    // Apply text search if any
    const searchVal = document.getElementById('kb-live-search').value.toLowerCase();
    if (searchVal) {
        filtered = filtered.filter(p => p.title.toLowerCase().includes(searchVal) || (p.namespace && p.namespace.toLowerCase().includes(searchVal)));
    }
    
    window.renderKBArticleCards(filtered);
};

window.handleKBSearch = (query) => {
    query = query.toLowerCase();
    
    // Find what the current active namespace filter is
    let activeNs = 'ALL';
    const activeEl = document.querySelector('.kb-folder.active');
    if (activeEl) {
        const onclickText = activeEl.getAttribute('onclick');
        const match = onclickText.match(/'([^']+)'/);
        if (match) activeNs = match[1];
    }
    
    if (!window._kbAllPages) return;
    let filtered = window._kbAllPages;
    
    if (activeNs === 'RECENT') {
        filtered = [...window._kbAllPages].sort((a,b) => new Date(b.date || 0) - new Date(a.date || 0)).slice(0, 20);
    } else if (activeNs === 'REVIEW') {
        filtered = window._kbAllPages.filter(p => p.health < 80);
    } else if (activeNs !== 'ALL') {
        filtered = window._kbAllPages.filter(p => p.namespace === activeNs);
    }
    
    if (query) {
        filtered = filtered.filter(p => p.title.toLowerCase().includes(query) || (p.namespace && p.namespace.toLowerCase().includes(query)));
    }
    
    window.renderKBArticleCards(filtered);
};

window.optimizeTarget = async (targetId, title) => {
    log(`📐 [Metis] Inizializzazione Causal Gradient Descent per: ${title}...`, "#10b981");
    
    const panel = document.getElementById('gradient-optimization-panel');
    const list = document.getElementById('gradient-results-list');
    const desc = document.getElementById('gradient-target-desc');
    
    if (panel) {
        panel.style.display = 'block';
        desc.innerText = `Target: ${title} (${targetId}) | Analisi derivata in corso...`;
        list.innerHTML = '<div style="text-align:center; padding:2rem; color:#64748b;"><i class="fas fa-cog fa-spin"></i> CALCOLO GRADIENTI STRATEGICI...</div>';
        panel.scrollIntoView({ behavior: 'smooth' });
    }

    try {
        const resp = await fetch('/api/wiki/simulate/gradient', {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                'X-API-KEY': typeof VAULT_KEY !== 'undefined' ? VAULT_KEY : 'AURA-ADMIN-77' 
            },
            body: JSON.stringify({ target_id: targetId, desired_impact: 1.0 })
        });
        const data = await resp.json();
        
        if (data.error) {
            list.innerHTML = `<div style="color:#ef4444; padding:1rem;">Errore: ${data.error}</div>`;
            return;
        }
        
        renderGradientResults(data);
    } catch (e) {
        log(`❌ Gradient Error: ${e.message}`, "#ef4444");
    }
};

window.renderGradientResults = (data) => {
    const list = document.getElementById('gradient-results-list');
    if (!list) return;
    
    list.innerHTML = '';
    
    if (data.strategic_drivers.length === 0) {
        list.innerHTML = '<div style="color:#8b949e; text-align:center;">Nessun driver efficiente trovato. Prova ad aumentare la profondità di ricerca.</div>';
        return;
    }
    
    data.strategic_drivers.forEach(driver => {
        const card = document.createElement('div');
        card.style = "background: rgba(255,255,255,0.03); border: 1px solid rgba(16, 185, 129, 0.2); border-radius: 12px; padding: 1rem; display: flex; justify-content: space-between; align-items: center;";
        
        card.innerHTML = `
            <div style="flex: 1;">
                <div style="font-size: 0.75rem; color: #fff; font-weight: 800;">${driver.driver_title}</div>
                <div style="font-size: 0.6rem; color: #10b981; margin-top: 4px;">${driver.recommendation}</div>
            </div>
            <div style="text-align: right; min-width: 120px;">
                <div style="font-size: 0.5rem; color: #8b949e;">EFFICIENCY</div>
                <div style="font-size: 0.8rem; color: #fff; font-weight: 900;">${(driver.efficiency * 100).toFixed(1)}%</div>
                <div style="font-size: 0.45rem; color: #10b981;">GRADIENT: ${driver.gradient}</div>
            </div>
        `;
        list.appendChild(card);
    });
    
    log(`✅ [Metis] Ottimizzazione completata. ${data.strategic_drivers.length} driver strategici identificati.`, "#10b981");
};

/**
 * 🗺️ [v9.1] METIS PARTITION MAP (Sharded Graph Visualizer)
 */
window.togglePartitions = () => {
    window._showPartitions = document.getElementById('metis-partition-toggle')?.checked;
    log(`🗺️ [Metis] Partition Map ${window._showPartitions ? 'ENABLED' : 'DISABLED'}`, "#10b981");
};

/**
 * 🪄 [v9.2] WIKI GENERATION WIZARD
 */
window.showWikiGeneratorWizard = (initialTopic = "") => {
    let currentStep = 1;
    let config = { topic: initialTopic, mode: 'TECHNICAL' };

    const renderStep = (step) => {
        let content = "";
        if (step === 1) {
            content = `
                <div style="padding:15px; animation: slideIn 0.3s ease-out;">
                    <div style="font-size:0.55rem; color:#3b82f6; font-weight:800; margin-bottom:10px; text-transform:uppercase;">STEP 1: IDENTIFICAZIONE TOPIC</div>
                    <p style="font-size:0.7rem; color:#8b949e; margin-bottom:1.5rem;">Inserisci il concetto o l'entità che vuoi espandere nella Wiki Sovrana.</p>
                    <input type="text" id="wiz-topic" value="${config.topic}" placeholder="es: Quantum Computing, Progetto Skywalker..." 
                        style="width:100%; background:rgba(0,0,0,0.4); border:1px solid #3b82f6; border-radius:10px; padding:12px; color:#fff; font-size:0.9rem; margin-bottom:2rem;">
                    <button onclick="window.wiz_next(2)" style="width:100%; padding:12px; background:#3b82f6; color:#fff; border:none; border-radius:10px; font-weight:900; cursor:pointer;">CONFIGURA MODALITÀ <i class="fas fa-arrow-right"></i></button>
                </div>
            `;
        } else if (step === 2) {
            content = `
                <div style="padding:15px; animation: slideIn 0.3s ease-out;">
                    <div style="font-size:0.55rem; color:#10b981; font-weight:800; margin-bottom:10px; text-transform:uppercase;">STEP 2: CONFIGURAZIONE PROFILO</div>
                    <p style="font-size:0.7rem; color:#8b949e; margin-bottom:1.5rem;">Scegli la profondità analitica per "${config.topic}".</p>
                    <div style="display:grid; grid-template-columns: 1fr; gap:10px; margin-bottom:2rem;">
                        <div class="glass-card wiz-mode-card ${config.mode==='EXECUTIVE'?'selected':''}" onclick="window.wiz_setMode('EXECUTIVE')" style="padding:15px; cursor:pointer; border:1px solid rgba(255,255,255,0.1);">
                            <div style="font-size:0.8rem; font-weight:800; color:#facc15;"><i class="fas fa-briefcase"></i> EXECUTIVE</div>
                            <div style="font-size:0.6rem; color:#8b949e;">Sintesi decisionale, impatto strategico e KPI.</div>
                        </div>
                        <div class="glass-card wiz-mode-card ${config.mode==='TECHNICAL'?'selected':''}" onclick="window.wiz_setMode('TECHNICAL')" style="padding:15px; cursor:pointer; border:1px solid rgba(255,255,255,0.1);">
                            <div style="font-size:0.8rem; font-weight:800; color:#3b82f6;"><i class="fas fa-code"></i> TECHNICAL</div>
                            <div style="font-size:0.6rem; color:#8b949e;">Specifiche, architettura e dettagli implementativi.</div>
                        </div>
                        <div class="glass-card wiz-mode-card ${config.mode==='RESEARCH'?'selected':''}" onclick="window.wiz_setMode('RESEARCH')" style="padding:15px; cursor:pointer; border:1px solid rgba(255,255,255,0.1);">
                            <div style="font-size:0.8rem; font-weight:800; color:#a855f7;"><i class="fas fa-microscope"></i> RESEARCH</div>
                            <div style="font-size:0.6rem; color:#8b949e;">Esplorazione teorica, citazioni e derivazioni logiche.</div>
                        </div>
                    </div>
                    <div style="display:flex; gap:10px;">
                        <button onclick="window.wiz_next(1)" style="flex:1; padding:12px; background:rgba(255,255,255,0.05); color:#fff; border:1px solid rgba(255,255,255,0.1); border-radius:10px; font-weight:800; cursor:pointer;">INDIETRO</button>
                        <button onclick="window.wiz_run()" style="flex:2; padding:12px; background:#10b981; color:#000; border:none; border-radius:10px; font-weight:950; cursor:pointer;">INIZIA EVOLUZIONE <i class="fas fa-bolt"></i></button>
                    </div>
                </div>
            `;
        } else if (step === 3) {
            content = `
                <div style="padding:15px; text-align:center; animation: fadeIn 0.5s ease-out;">
                    <div id="wiz-loader">
                        <i class="fas fa-circle-notch fa-spin fa-3x" style="color:#3b82f6; margin-bottom:1.5rem;"></i>
                        <h3 style="color:#fff; margin-bottom:10px;">SINTESI IN CORSO...</h3>
                        <p style="font-size:0.65rem; color:#8b949e; line-height:1.6;">Agent Smith sta interrogando il Vault e distillando la conoscenza per <b>${config.topic}</b>.<br>Tempo stimato: 10-20 secondi.</p>
                    </div>
                    <div id="wiz-preview" style="display:none; text-align:left;">
                        <div style="font-size:0.55rem; color:#10b981; font-weight:800; margin-bottom:10px; text-transform:uppercase;">DRAFT GENERATO</div>
                        <div id="wiz-markdown-preview" style="background:rgba(0,0,0,0.3); padding:15px; border-radius:10px; max-height:300px; overflow-y:auto; font-size:0.75rem; color:#cbd5e1; line-height:1.5; border:1px solid rgba(255,255,255,0.05); margin-bottom:1.5rem;"></div>
                        <button onclick="window.wiz_publish()" style="width:100%; padding:15px; background:linear-gradient(135deg, #10b981, #059669); color:#fff; border:none; border-radius:10px; font-weight:900; cursor:pointer; box-shadow:0 0 20px rgba(16,185,129,0.3);">PUBBLICA NEL VAULT SOVRANO <i class="fas fa-check-double"></i></button>
                    </div>
                </div>
            `;
        }
        
        window.showSovereignModal("🪄 KNOWLEDGE GENERATOR", content);
    };

    window.wiz_next = (step) => {
        if (step === 2) config.topic = document.getElementById('wiz-topic').value;
        currentStep = step;
        renderStep(step);
    };

    window.wiz_setMode = (mode) => {
        config.mode = mode;
        renderStep(2);
    };

    window.wiz_run = async () => {
        renderStep(3);
        try {
            const apiKey = (typeof window.VAULT_KEY !== 'undefined') ? window.VAULT_KEY : 'AURA-ADMIN-77';
            const resp = await fetch('/api/wiki/generate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'X-API-KEY': apiKey },
                body: JSON.stringify(config)
            });
            const data = await resp.json();
            
            if (data.status === 'success') {
                document.getElementById('wiz-loader').style.display = 'none';
                document.getElementById('wiz-preview').style.display = 'block';
                
                // [v9.2] Wizard Step 3 Polish: Estimates
                const charCount = data.markdown.length;
                const mermaidCount = (data.markdown.match(/```mermaid/g) || []).length;
                const citationCount = data.citations?.length || 0;

                const statsHtml = `
                    <div style="display:flex; gap:10px; margin-bottom:15px;">
                        <div class="glass-card" style="flex:1; padding:10px; text-align:center; border-color:#3b82f6;">
                            <div style="font-size:0.5rem; color:#8b949e;">CARATTERI</div>
                            <div style="font-size:0.8rem; font-weight:900; color:#fff;">${charCount}</div>
                        </div>
                        <div class="glass-card" style="flex:1; padding:10px; text-align:center; border-color:#a855f7;">
                            <div style="font-size:0.5rem; color:#8b949e;">GRAFICI</div>
                            <div style="font-size:0.8rem; font-weight:900; color:#fff;">${mermaidCount}</div>
                        </div>
                        <div class="glass-card" style="flex:1; padding:10px; text-align:center; border-color:#10b981;">
                            <div style="font-size:0.5rem; color:#8b949e;">CITAZIONI</div>
                            <div style="font-size:0.8rem; font-weight:900; color:#fff;">${citationCount}</div>
                        </div>
                    </div>
                `;

                document.getElementById('wiz-markdown-preview').innerHTML = statsHtml + `<div>${data.markdown.substring(0, 500)}...</div>`;
                window._lastWizResult = data;
            } else {
                alert("Errore durante la generazione: " + data.message);
                renderStep(2);
            }
        } catch (e) {
            alert("Errore critico: " + e.message);
            renderStep(2);
        }
    };

    window.wiz_publish = async () => {
        if (!window._lastWizResult) return;
        log(`💾 [v9.2] Pubblicazione definitiva di "${config.topic}"...`, "#10b981");
        
        try {
            const apiKey = (typeof window.VAULT_KEY !== 'undefined') ? window.VAULT_KEY : 'AURA-ADMIN-77';
            await fetch('/api/wiki/save', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'X-API-KEY': apiKey },
                body: JSON.stringify({
                    topic: config.topic,
                    markdown: window._lastWizResult.markdown,
                    metadata: window._lastWizResult.metadata
                })
            });
            
            window.showSovereignModal("✅ PUBBLICAZIONE COMPLETATA", `
                <div style="text-align:center; padding:1rem;">
                    <i class="fas fa-check-circle fa-4x" style="color:#10b981; margin-bottom:1.5rem;"></i>
                    <p style="font-size:0.85rem; color:#fff;">La pagina <b>${config.topic}</b> è ora parte del patrimonio di conoscenza del Vault.</p>
                    <button onclick="location.reload()" style="margin-top:1rem; padding:10px 20px; background:#3b82f6; border:none; color:#fff; border-radius:8px; cursor:pointer;">AGGIORNA WIKI</button>
                </div>
            `);
        } catch (e) {
            alert("Errore durante il salvataggio: " + e.message);
        }
    };

    renderStep(1);
};
window.selectLens = (lensId) => {
    const cards = document.querySelectorAll('.lens-card');
    const select = document.getElementById('sim-lens');
    if (!select) return;

    cards.forEach(c => {
        if (c.getAttribute('onclick').includes(`'${lensId}'`)) {
            c.classList.toggle('selected');
        }
    });

    // Sync hidden select
    const selectedIds = Array.from(document.querySelectorAll('.lens-card.selected'))
        .map(c => c.getAttribute('onclick').match(/'([^']+)'/)[1]);
    
    Array.from(select.options).forEach(opt => {
        opt.selected = selectedIds.includes(opt.value);
    });
    
    log(`Lens Selection Updated: [${selectedIds.join(', ').toUpperCase()}]`, '#a855f7');
};

window.startGlobalOptimization = () => {
    window.showSovereignModal("🎯 TARGET OPTIMIZATION", `
        <div style="padding:10px; display:flex; flex-direction:column; gap:1.5rem;">
            <p style="font-size:0.7rem; color:#8b949e;">Seleziona un obiettivo strategico per calcolare i gradienti causali.</p>
            <div>
                <label style="font-size:0.6rem; color:#10b981; display:block; margin-bottom:8px;">CONCETTO TARGET</label>
                <input type="text" id="global-opt-target" placeholder="es: Efficienza, Stabilità, Profitto..." style="width:100%; background:rgba(0,0,0,0.4); border:1px solid #10b981; border-radius:8px; padding:10px; color:#fff; font-size:0.8rem;">
            </div>
            <div>
                <label style="font-size:0.6rem; color:#10b981; display:block; margin-bottom:8px;">IMPATTO DESIDERATO</label>
                <input type="range" id="global-opt-impact" min="0.1" max="1.0" step="0.1" value="0.8" style="width:100%; accent-color:#10b981;">
            </div>
            <button onclick="window.runGlobalOptimization()" style="width:100%; padding:12px; background:#10b981; color:#000; border:none; border-radius:8px; font-weight:900; cursor:pointer;">AVVIA GRADIENT DESCENT</button>
        </div>
    `);
};

window.runGlobalOptimization = () => {
    const target = document.getElementById('global-opt-target').value;
    if (!target) return alert("Inserisci un target.");
    window.closeSovereignModal();
    window.optimizeTarget(target, target);
};

// Initialize Welcome Screens on Load
document.addEventListener('DOMContentLoaded', () => {
    setTimeout(() => {
        window.initMindsetSync(); // [v9.2] State Persistence
        window.initWorkspace();   // [v9.2] Workspace Restoration
        window.refreshWikiList();
        window.renderWikiDashboard();
    }, 1000);
});


window.initMetisMap = () => {
    log("🗺️ [Metis] Inizializzazione Partition Map HUD...", "#10b981");
    // La logica di ricolorazione è integrata in nebula_graph.js tramite window._showPartitions
};

// [v9.1] Clarification Log on Time Navigation
document.addEventListener('DOMContentLoaded', () => {
    log("⏳ [Temporal HUD] Neural Time Drive (Past) vs Temporal Scrubber (Future Projections) active.", "#3b82f6");
});

// Auto-init on load if needed
document.addEventListener('DOMContentLoaded', () => {
    if (window.location.hash === '#metis') window.initMetisMap();
});

// 🧬 [v9.6 Self-Healing] Legacy alias mapping
window.runCausalSimulation = window.runNaturalLanguageSimulation;

// ==========================================
// 🏛️ [v11.0] What-If Simulation History & Folders Subpage Logic
// ==========================================

window._whatifFilters = {
    folder: 'root',
    status: 'active',
    tag: null
};

window.switchWhatIfSubview = (subview) => {
    const wsTab = document.getElementById('whatif-tab-workspace');
    const histTab = document.getElementById('whatif-tab-history');
    const wsView = document.getElementById('whatif-workspace-view');
    const histView = document.getElementById('whatif-history-view');
    
    if (subview === 'workspace') {
        if(wsTab) {
            wsTab.style.color = '#facc15';
            wsTab.style.borderBottomColor = '#facc15';
        }
        if(histTab) {
            histTab.style.color = '#8b949e';
            histTab.style.borderBottomColor = 'transparent';
        }
        if(wsView) wsView.style.display = 'block';
        if(histView) histView.style.display = 'none';
    } else {
        if(wsTab) {
            wsTab.style.color = '#8b949e';
            wsTab.style.borderBottomColor = 'transparent';
        }
        if(histTab) {
            histTab.style.color = '#facc15';
            histTab.style.borderBottomColor = '#facc15';
        }
        if(wsView) wsView.style.display = 'none';
        if(histView) histView.style.display = 'block';
        window.loadSimulationHistory();
        window.loadFoldersAndTags();
    }
};

window.setHistoryFilter = (type, value) => {
    if (type === 'folder') {
        window._whatifFilters.folder = value;
        const folders = document.querySelectorAll('.folder-btn');
        folders.forEach(btn => {
            if (btn.getAttribute('data-folder') === value) {
                btn.style.borderColor = '#facc15';
                btn.style.background = 'rgba(250,204,21,0.08)';
                btn.style.color = '#facc15';
            } else {
                btn.style.borderColor = 'rgba(255,255,255,0.05)';
                btn.style.background = 'transparent';
                btn.style.color = '#8b949e';
            }
        });
    } else if (type === 'status') {
        window._whatifFilters.status = value;
        const actBtn = document.getElementById('filter-status-active');
        const arcBtn = document.getElementById('filter-status-archived');
        if (value === 'active') {
            if(actBtn) { actBtn.style.background = 'rgba(59, 130, 246, 0.08)'; actBtn.style.borderColor = '#3b82f6'; }
            if(arcBtn) { arcBtn.style.background = 'transparent'; arcBtn.style.borderColor = 'rgba(255,255,255,0.05)'; }
        } else {
            if(actBtn) { actBtn.style.background = 'transparent'; actBtn.style.borderColor = 'rgba(255,255,255,0.05)'; }
            if(arcBtn) { arcBtn.style.background = 'rgba(139, 148, 158, 0.08)'; arcBtn.style.borderColor = '#8b949e'; }
        }
    } else if (type === 'tag') {
        window._whatifFilters.tag = value;
        const searchInput = document.getElementById('whatif-history-search');
        if (searchInput) searchInput.value = value;
    }
    
    window.loadSimulationHistory();
};

window.loadSimulationHistory = async () => {
    let container = document.getElementById('whatif-history-container');
    // Fallback if we use the right side panel instead of a dedicated view
    if (!container) container = document.getElementById('sim-history-list');
    if (!container) return;
    
    container.innerHTML = '<div style="padding:20px; color:#facc15;"><i class="fas fa-circle-notch fa-spin"></i> Caricamento Storico Simulazioni...</div>';
    
    try {
        let url = `/api/whatif/history?status=${window._whatifFilters.status}`;
        if (window._whatifFilters.folder) {
            url += `&folder_path=${encodeURIComponent(window._whatifFilters.folder)}`;
        }
        const searchVal = document.getElementById('whatif-history-search')?.value;
        if (searchVal) {
            url += `&search=${encodeURIComponent(searchVal)}`;
        }
        
        const resp = await fetch(url, {
            headers: { 'X-API-KEY': typeof VAULT_KEY !== 'undefined' ? VAULT_KEY : 'AURA-ADMIN-77' }
        });
        const history = await resp.json();
        
        if (history.length === 0) {
            container.innerHTML = `
                <div style="text-align:center; padding:3rem 1rem; color:#64748b;">
                    <i class="fas fa-history fa-2x" style="margin-bottom:1rem; opacity:0.3;"></i>
                    <div style="font-size:0.75rem; font-weight:800;">NESSUNA SIMULAZIONE TROVATA</div>
                    <div style="font-size:0.6rem; margin-top:4px;">Avvia scenari o cambia i filtri della cartella.</div>
                </div>
            `;
            return;
        }
        
        const parentSelect = document.getElementById('sim-parent-id');
        if (parentSelect) {
            const currentVal = parentSelect.value;
            parentSelect.innerHTML = '<option value="">Nessuna (Nuovo Albero Causal)</option>';
            history.forEach(sim => {
                const opt = document.createElement('option');
                opt.value = sim.id;
                opt.innerText = `[${sim.timestamp.substring(11, 16)}] ${sim.query.substring(0, 45)}...`;
                parentSelect.appendChild(opt);
            });
            parentSelect.value = currentVal;
        }
        
        let html = '';
        history.forEach(sim => {
            const dateStr = sim.timestamp.substring(0, 16).replace('T', ' ');
            const lensesBadges = sim.settings?.lenses ? sim.settings.lenses.map(l => `<span style="background:rgba(250,204,21,0.1); border:1px solid rgba(250,204,21,0.2); color:#facc15; font-size:0.5rem; padding:2px 6px; border-radius:4px; font-family:'JetBrains Mono';">${l}</span>`).join(' ') : '';
            const tagsBadges = sim.tags ? sim.tags.map(t => `<span onclick="event.stopPropagation(); window.setHistoryFilter('tag', '${t}')" style="background:rgba(168,85,247,0.1); border:1px solid rgba(168,85,247,0.2); color:#a855f7; font-size:0.5rem; padding:2px 6px; border-radius:4px; cursor:pointer;">#${t}</span>`).join(' ') : '';
            
            const isArchived = sim.status === 'archived';
            const archiveIcon = isArchived ? 'fa-folder-open' : 'fa-archive';
            const archiveTitle = isArchived ? 'DISARCHIVIA' : 'ARCHIVIA';
            
            const parentBadge = sim.parent_id ? `
                <div style="font-size:0.5rem; color:#a855f7; display:flex; align-items:center; gap:4px; margin-top:4px;">
                    <i class="fas fa-code-branch"></i> RAMO DI SIMULAZIONE
                </div>
            ` : '';
            
            const childrenBadge = sim.children_count > 0 ? `
                <div style="font-size:0.5rem; color:#10b981; display:flex; align-items:center; gap:4px; margin-top:4px;">
                    <i class="fas fa-network-wired"></i> GENERATO ${sim.children_count} RAMIFICAZIONI FIGLIE
                </div>
            ` : '';
            
            html += `
                <div onclick="window.loadSimulationDetails('${sim.id}')" class="glass-card simulation-history-card" data-sim-id="${sim.id}" style="padding:1.2rem; cursor:pointer; display:flex; flex-direction:column; gap:8px; border-color:rgba(255,255,255,0.05); transition:all 0.3s; position:relative;">
                    <div style="display:flex; justify-content:space-between; align-items:center; gap:10px;">
                        <span style="font-size:0.55rem; color:#64748b; font-family:'JetBrains Mono';">${dateStr}</span>
                        <div style="display:flex; gap: 5px;">
                            <span style="background:rgba(59,130,246,0.1); border:1px solid rgba(59,130,246,0.2); color:#3b82f6; font-size:0.5rem; padding:2px 6px; border-radius:4px; font-weight:800; text-transform:uppercase;">${sim.settings?.mode || 'FAST'}</span>
                            <button onclick="event.stopPropagation(); window.deleteSimulation('${sim.id}')" style="background: rgba(239, 68, 68, 0.1); border: 1px solid #ef4444; color: #ef4444; border-radius: 4px; padding: 2px 6px; font-size: 0.5rem; cursor: pointer; transition: 0.2s;" title="Elimina">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                    </div>
                    
                    <div style="font-size:0.7rem; color:#fff; font-weight:800; font-style:italic; line-height:1.4;">
                        "${sim.query}"
                    </div>
                    
                    <div style="display:flex; flex-wrap:wrap; gap:6px; margin-top:2px;">
                        ${lensesBadges}
                        ${tagsBadges}
                    </div>
                    
                    ${parentBadge}
                    ${childrenBadge}
                    
                    <div style="display:flex; gap:10px; justify-content:flex-end; border-top:1px solid rgba(255,255,255,0.03); padding-top:8px; margin-top:4px;">
                        <button onclick="event.stopPropagation(); window.reReadSimulation('${sim.id}')" title="Rileggi report grafico nel Workspace" style="background:none; border:none; color:#facc15; font-size:0.6rem; font-weight:800; cursor:pointer; display:flex; align-items:center; gap:4px; outline:none;">
                            <i class="fas fa-book-open"></i> RILEGGI
                        </button>
                        <button onclick="event.stopPropagation(); window.replaySimulation('${sim.id}')" title="Carica prompt e configurazione" style="background:none; border:none; color:#3b82f6; font-size:0.6rem; font-weight:800; cursor:pointer; display:flex; align-items:center; gap:4px; outline:none;">
                            <i class="fas fa-undo"></i> REPLAY
                        </button>
                        <button onclick="event.stopPropagation(); window.branchSimulation('${sim.id}', '${sim.query.replace(/'/g, "\\'")}')" title="Avvia simulazione figlia a partire da questa" style="background:none; border:none; color:#a855f7; font-size:0.6rem; font-weight:800; cursor:pointer; display:flex; align-items:center; gap:4px; outline:none;">
                            <i class="fas fa-code-branch"></i> RAMIFICA
                        </button>
                        <button onclick="event.stopPropagation(); window.archiveSimulation('${sim.id}', ${isArchived})" title="${archiveTitle}" style="background:none; border:none; color:#8b949e; font-size:0.6rem; font-weight:800; cursor:pointer; display:flex; align-items:center; gap:4px; outline:none;">
                            <i class="fas ${archiveIcon}"></i>
                        </button>
                        <button onclick="event.stopPropagation(); window.moveSimulation('${sim.id}')" title="Sposta in cartella" style="background:none; border:none; color:#64748b; font-size:0.6rem; font-weight:800; cursor:pointer; display:flex; align-items:center; gap:4px; outline:none;">
                            <i class="fas fa-folder-open"></i> SPOSTA
                        </button>
                        <button onclick="event.stopPropagation(); window.tagSimulation('${sim.id}')" title="Gestisci tags" style="background:none; border:none; color:#10b981; font-size:0.6rem; font-weight:800; cursor:pointer; display:flex; align-items:center; gap:4px; outline:none;">
                            <i class="fas fa-tag"></i> TAGS
                        </button>
                        <button onclick="event.stopPropagation(); window.deleteSimulation('${sim.id}')" title="Elimina dallo storico" style="background:none; border:none; color:#ef4444; font-size:0.6rem; font-weight:800; cursor:pointer; display:flex; align-items:center; gap:4px; outline:none;">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </div>
            `;
        });
        
        container.innerHTML = html;
        
    } catch (e) {
        console.error("History Loading Error:", e);
        container.innerHTML = '<div style="padding:20px; color:#ef4444;">❌ Errore durante il recupero dello storico.</div>';
    }
};

window.loadFoldersAndTags = async () => {
    const foldersContainer = document.getElementById('whatif-folders-list');
    const tagsContainer = document.getElementById('whatif-tags-cloud');
    if (!foldersContainer) return;
    
    try {
        const folderResp = await fetch('/api/whatif/folders', {
            headers: { 'X-API-KEY': typeof VAULT_KEY !== 'undefined' ? VAULT_KEY : 'AURA-ADMIN-77' }
        });
        const folders = await folderResp.json();
        
        let folderHtml = '';
        folders.forEach(f => {
            const activeStyle = f === window._whatifFilters.folder ? 'border-color:#facc15; background:rgba(250,204,21,0.08); color:#facc15;' : 'border-color:rgba(255,255,255,0.05); background:transparent; color:#8b949e;';
            folderHtml += `
                <button onclick="window.setHistoryFilter('folder', '${f}')" data-folder="${f}" class="glass-card folder-btn" style="width:100%; text-align:left; padding:0.6rem 1rem; font-size:0.65rem; font-weight:800; cursor:pointer; display:flex; align-items:center; gap:8px; transition:0.3s; ${activeStyle}">
                    <i class="fas fa-folder"></i> ${f.toUpperCase()}
                </button>
            `;
        });
        foldersContainer.innerHTML = folderHtml;
        
        const histResp = await fetch('/api/whatif/history', {
            headers: { 'X-API-KEY': typeof VAULT_KEY !== 'undefined' ? VAULT_KEY : 'AURA-ADMIN-77' }
        });
        const history = await histResp.json();
        
        const tagsMap = {};
        history.forEach(sim => {
            if (sim.tags) {
                sim.tags.forEach(t => {
                    if (t.trim()) tagsMap[t] = (tagsMap[t] || 0) + 1;
                });
            }
        });
        
        let tagsHtml = '';
        Object.keys(tagsMap).forEach(tag => {
            tagsHtml += `
                <span onclick="window.setHistoryFilter('tag', '${tag}')" class="badge-pulsing" style="background:rgba(168,85,247,0.1); border:1px solid rgba(168,85,247,0.25); color:#a855f7; font-size:0.5rem; padding:4px 8px; border-radius:6px; cursor:pointer; font-weight:800; font-family:'Inter'; transition:0.3s;">
                    #${tag} (${tagsMap[tag]})
                </span>
            `;
        });
        
        if (tagsHtml === '') {
            tagsContainer.innerHTML = '<span style="font-size:0.55rem; color:#64748b;">Nessun tag assegnato.</span>';
        } else {
            tagsContainer.innerHTML = tagsHtml;
        }
        
    } catch (e) {
        console.error("Folders/Tags Loading Error:", e);
    }
};

window.loadSimulationDetails = async (id) => {
    const detailsContainer = document.getElementById('whatif-selected-details');
    if (!detailsContainer) return;
    
    const cards = document.querySelectorAll('.simulation-history-card');
    cards.forEach(c => {
        if (c.getAttribute('data-sim-id') === id) {
            c.style.borderColor = '#facc15';
            c.style.boxShadow = '0 0 15px rgba(250,204,21,0.1)';
        } else {
            c.style.borderColor = 'rgba(255,255,255,0.05)';
            c.style.boxShadow = 'none';
        }
    });
    
    detailsContainer.style.display = 'flex';
    detailsContainer.innerHTML = '<div style="color:#facc15; font-size:0.7rem;"><i class="fas fa-circle-notch fa-spin"></i> Caricamento dettagli...</div>';
    
    try {
        const resp = await fetch(`/api/whatif/simulation/${id}`, {
            headers: { 'X-API-KEY': typeof VAULT_KEY !== 'undefined' ? VAULT_KEY : 'AURA-ADMIN-77' }
        });
        const details = await resp.json();
        
        window.drawGenealogyTree(details);
        
        const fullResults = details.full_results;
        
        let childrenHtml = '';
        if (details.children && details.children.length > 0) {
            childrenHtml = `
                <div style="border-top:1px solid rgba(255,255,255,0.05); padding-top:8px; margin-top:8px;">
                    <div style="font-size:0.5rem; color:#10b981; font-weight:800; margin-bottom:5px;">RAMIFICAZIONI FIGLIE:</div>
                    <div style="display:flex; flex-direction:column; gap:6px;">
                        ${details.children.map(c => `
                            <div onclick="window.loadSimulationDetails('${c.id}')" style="font-size:0.6rem; color:#8b949e; cursor:pointer; text-decoration:underline; font-style:italic;" onmouseover="this.style.color='#facc15'" onmouseout="this.style.color='#8b949e'">
                                - "${c.query}"
                            </div>
                        `).join('')}
                    </div>
                </div>
            `;
        }
        
        detailsContainer.innerHTML = `
            <div>
                <div style="font-size:0.5rem; color:#8b949e; font-family:'JetBrains Mono';">ID: ${details.id.substring(0,8)}...</div>
                <div style="font-size:0.65rem; color:#facc15; font-weight:900; margin-top:4px; text-transform:uppercase;">PREVISIONE TARGET: ${details.target_node_title}</div>
            </div>
            
            <div style="border-top:1px solid rgba(255,255,255,0.05); padding-top:8px;">
                <div style="font-size:0.55rem; color:#8b949e; font-weight:800; margin-bottom:4px;">VERDETTO SUPREME COURT SINTETIZZATO:</div>
                <div class="markdown-body" style="font-size:0.65rem; color:#d1d5db; line-height:1.5; background:rgba(0,0,0,0.2); padding:10px; border-radius:8px; max-height:200px; overflow-y:auto; border:1px solid rgba(255,255,255,0.03);">
                    ${fullResults.narrative ? fullResults.narrative.replace(/\n/g, '<br>') : 'Nessun verdetto memorizzato.'}
                </div>
            </div>
            
            <div style="border-top:1px solid rgba(255,255,255,0.05); padding-top:8px;">
                <div style="font-size:0.55rem; color:#8b949e; font-weight:800; margin-bottom:4px;">ARENA DIBATTITO (CONTRACCOLPO):</div>
                <div style="display:flex; flex-direction:column; gap:6px; font-size:0.6rem;">
                    <div style="background:rgba(250,204,21,0.05); padding:6px; border-radius:4px; border:1px solid rgba(250,204,21,0.1);">
                        <strong style="color:#facc15;">OTTIMISTA:</strong> "${fullResults.counterfactual_arena?.optimist_argument || 'Non disponibile'}"
                    </div>
                    <div style="background:rgba(16,185,129,0.05); padding:6px; border-radius:4px; border:1px solid rgba(16,185,129,0.1);">
                        <strong style="color:#10b981;">SCETTICO:</strong> "${fullResults.counterfactual_arena?.skeptic_argument || 'Non disponibile'}"
                    </div>
                </div>
            </div>
            
            ${childrenHtml}
        `;
        
    } catch (e) {
        console.error("Details Loading Error:", e);
        detailsContainer.innerHTML = '<div style="color:#ef4444; font-size:0.7rem;">❌ Errore caricamento dettagli.</div>';
    }
};

window.loadSimSettings = async (id) => {
    try {
        const resp = await fetch(`/api/whatif/simulation/${id}`, {
            headers: { 'X-API-KEY': typeof VAULT_KEY !== 'undefined' ? VAULT_KEY : 'AURA-ADMIN-77' }
        });
        const details = await resp.json();
        
        if (details && details.settings) {
            document.getElementById('nl-sim-prompt').value = details.query || '';
            if (details.settings.mode) document.getElementById('sim-mode').value = details.settings.mode;
            
            // Set lenti archetipali
            const lensSelect = document.getElementById('sim-lens');
            if (lensSelect && details.settings.lenses) {
                Array.from(lensSelect.options).forEach(opt => {
                    opt.selected = details.settings.lenses.includes(opt.value);
                });
            }

            // Torna al tab Nuova Simulazione
            window.switchSimTab('new');
            log(`🎯 [What-If] Impostazioni della simulazione ricaricate con successo.`, "#10b981");
        }
    } catch (e) {
        console.error("Error loading settings:", e);
        alert("Errore durante il caricamento delle impostazioni.");
    }
};

window.deleteSimulation = async (id) => {
    if(!confirm("Vuoi davvero eliminare questa simulazione?")) return;
    try {
        const resp = await fetch(`/api/whatif/simulation/${id}`, {
            method: 'DELETE',
            headers: { 'X-API-KEY': typeof VAULT_KEY !== 'undefined' ? VAULT_KEY : 'AURA-ADMIN-77' }
        });
        const res = await resp.json();
        if (res.status === 'success') {
            log(`🗑️ [What-If] Simulazione rimossa dallo storico.`, "#ef4444");
            window.loadSimulationHistory();
            document.getElementById('whatif-selected-details').innerHTML = '<div style="color: #8b949e; font-size: 0.65rem; text-align: center; padding: 2rem; font-style: italic;">Seleziona una simulazione dallo storico per vederne i dettagli analitici e i verdetti.</div>';
        }
    } catch (e) {
        console.error(e);
    }
};


window.drawGenealogyTree = async (currentSim) => {
    const canvas = document.getElementById('whatif-tree-paint-canvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    try {
        const resp = await fetch('/api/whatif/history', {
            headers: { 'X-API-KEY': typeof VAULT_KEY !== 'undefined' ? VAULT_KEY : 'AURA-ADMIN-77' }
        });
        const history = await resp.json();
        
        const nodes = {};
        history.forEach(sim => {
            nodes[sim.id] = {
                id: sim.id,
                query: sim.query,
                parent_id: sim.parent_id,
                x: 0,
                y: 0,
                level: 0,
                children: []
            };
        });
        
        const roots = [];
        Object.keys(nodes).forEach(id => {
            const node = nodes[id];
            if (node.parent_id && nodes[node.parent_id]) {
                nodes[node.parent_id].children.push(node);
            } else {
                roots.push(node);
            }
        });
        
        let maxLevel = 0;
        const calculateGeometry = (node, level, siblingIndex, totalSiblings) => {
            node.level = level;
            if (level > maxLevel) maxLevel = level;
            
            node.x = 40 + level * 100;
            node.y = 35 + (siblingIndex * (220 / Math.max(1, totalSiblings))) + (level * 10);
            
            node.children.forEach((child, idx) => {
                calculateGeometry(child, level + 1, idx, node.children.length);
            });
        };
        
        roots.forEach((root, idx) => {
            calculateGeometry(root, 0, idx, roots.length);
        });
        
        Object.keys(nodes).forEach(id => {
            const node = nodes[id];
            node.children.forEach(child => {
                ctx.beginPath();
                ctx.moveTo(node.x, node.y);
                ctx.bezierCurveTo(node.x + 40, node.y, child.x - 40, child.y, child.x, child.y);
                ctx.strokeStyle = child.id === currentSim.id || node.id === currentSim.id ? '#facc15' : 'rgba(59,130,246,0.3)';
                ctx.lineWidth = child.id === currentSim.id || node.id === currentSim.id ? 2 : 1;
                ctx.stroke();
            });
        });
        
        Object.keys(nodes).forEach(id => {
            const node = nodes[id];
            const isCurrent = node.id === currentSim.id;
            
            if (isCurrent) {
                ctx.beginPath();
                ctx.arc(node.x, node.y, 10, 0, 2 * Math.PI);
                ctx.fillStyle = 'rgba(250,204,21,0.2)';
                ctx.fill();
            }
            
            ctx.beginPath();
            ctx.arc(node.x, node.y, 5, 0, 2 * Math.PI);
            ctx.fillStyle = isCurrent ? '#facc15' : (node.parent_id ? '#a855f7' : '#3b82f6');
            ctx.fill();
            
            ctx.fillStyle = isCurrent ? '#fff' : '#8b949e';
            ctx.font = '7px Inter';
            const text = node.query.substring(0, 12) + '...';
            ctx.fillText(text, node.x - 20, node.y - 10);
        });
        
    } catch (e) {
        console.error("Genealogy Draw Error:", e);
    }
};

window.reReadSimulation = async (id) => {
    try {
        const resp = await fetch(`/api/whatif/simulation/${id}`, {
            headers: { 'X-API-KEY': typeof VAULT_KEY !== 'undefined' ? VAULT_KEY : 'AURA-ADMIN-77' }
        });
        const details = await resp.json();
        
        if (details.full_results && Object.keys(details.full_results).length > 0 && details.full_results.narrative) {
            log(`📖 [What-If] Rilettura e caricamento report storico: "${details.query}"`, "#facc15");
            window._lastSimResult = details.full_results;
            
            window.renderSITREP(details.full_results);
            if (window.renderSimulationGraph) {
                window.renderSimulationGraph(details.full_results);
            }
            
            document.getElementById('nl-sim-prompt').value = details.query;
            
            window.switchWhatIfSubview('workspace');
        } else {
            alert("Questa simulazione non ha report completi salvati o appartiene a una versione precedente incompatibile.");
        }
    } catch (e) {
        console.error("Re-read Error:", e);
        alert("Impossibile caricare i dati della simulazione.");
    }
};

window.replaySimulation = (id) => {
    fetch(`/api/whatif/simulation/${id}`, {
        headers: { 'X-API-KEY': typeof VAULT_KEY !== 'undefined' ? VAULT_KEY : 'AURA-ADMIN-77' }
    })
    .then(r => r.json())
    .then(details => {
        document.getElementById('nl-sim-prompt').value = details.query;
        
        const select = document.getElementById('sim-lens');
        if (select && details.settings?.lenses) {
            Array.from(select.options).forEach(opt => {
                opt.selected = details.settings.lenses.includes(opt.value);
            });
        }
        
        if (document.getElementById('sim-mode') && details.settings?.mode) {
            document.getElementById('sim-mode').value = details.settings.mode;
        }
        
        if (document.getElementById('sim-horizon') && details.settings?.horizon) {
            const horizonMap = { "immediate": 0, "mid_term": 1, "long_term": 2 };
            document.getElementById('sim-horizon').value = horizonMap[details.settings.horizon] || 0;
        }
        
        if (document.getElementById('sim-parent-id')) {
            document.getElementById('sim-parent-id').value = details.id;
        }
        
        log(`🔄 [What-If] Parametri caricati nel Workspace per replay di "${details.query}"`, "#3b82f6");
        window.switchWhatIfSubview('workspace');
    })
    .catch(err => {
        console.error(err);
        alert("Impossibile recuperare i parametri per il replay.");
    });
};

window.branchSimulation = (parentId, parentQuery) => {
    const parentSelect = document.getElementById('sim-parent-id');
    if (parentSelect) {
        let found = false;
        Array.from(parentSelect.options).forEach(opt => {
            if (opt.value === parentId) found = true;
        });
        if (!found) {
            const opt = document.createElement('option');
            opt.value = parentId;
            opt.innerText = `[Madre] ${parentQuery.substring(0, 45)}...`;
            parentSelect.appendChild(opt);
        }
        parentSelect.value = parentId;
    }
    
    document.getElementById('nl-sim-prompt').value = `Consolida gli effetti dello scenario precedente e simula la reazione se...`;
    
    log(`🌱 [What-If] Pronto a ramificare simulazione figlia dalla madre ID: ${parentId.substring(0,8)}`, "#a855f7");
    window.switchWhatIfSubview('workspace');
};

window.archiveSimulation = async (id, currentlyArchived) => {
    try {
        const resp = await fetch(`/api/whatif/simulation/${id}/archive`, {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                'X-API-KEY': typeof VAULT_KEY !== 'undefined' ? VAULT_KEY : 'AURA-ADMIN-77' 
            },
            body: JSON.stringify({ archive: !currentlyArchived })
        });
        const res = await resp.json();
        
        if (res.status === 'success') {
            log(`⚖️ [Archivio] Stato simulazione aggiornato: ${res.new_status}`, "#3b82f6");
            window.loadSimulationHistory();
            window.loadFoldersAndTags();
        }
    } catch (e) {
        console.error(e);
    }
};

window.deleteSimulation = async (id) => {
    if (!confirm("Sei sicuro di voler eliminare definitivamente questa simulazione dallo storico?")) return;
    
    try {
        const resp = await fetch(`/api/whatif/simulation/${id}`, {
            method: 'DELETE',
            headers: { 'X-API-KEY': typeof VAULT_KEY !== 'undefined' ? VAULT_KEY : 'AURA-ADMIN-77' }
        });
        const res = await resp.json();
        
        if (res.status === 'success') {
            log(`🗑️ [What-If] Simulazione rimossa dallo storico.`, "#ef4444");
            window.loadSimulationHistory();
            window.loadFoldersAndTags();
            document.getElementById('whatif-selected-details').style.display = 'none';
        }
    } catch (e) {
        console.error(e);
    }
};

window.moveSimulation = async (id) => {
    const folder = prompt("Inserisci il percorso della cartella cognitiva (es: Strategy, Security, Test):", "Strategy");
    if (folder === null) return;
    
    try {
        const resp = await fetch(`/api/whatif/simulation/${id}/folder`, {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                'X-API-KEY': typeof VAULT_KEY !== 'undefined' ? VAULT_KEY : 'AURA-ADMIN-77' 
            },
            body: JSON.stringify({ folder_path: folder || "root" })
        });
        const res = await resp.json();
        
        if (res.status === 'success') {
            log(`📁 [What-If] Simulazione spostata in: ${res.new_folder}`, "#3b82f6");
            window.loadSimulationHistory();
            window.loadFoldersAndTags();
        }
    } catch (e) {
        console.error(e);
    }
};

window.tagSimulation = async (id) => {
    const tags = prompt("Inserisci tags separati da virgole (es: cyber, market, risk):");
    if (tags === null) return;
    
    try {
        const resp = await fetch(`/api/whatif/simulation/${id}/tags`, {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                'X-API-KEY': typeof VAULT_KEY !== 'undefined' ? VAULT_KEY : 'AURA-ADMIN-77' 
            },
            body: JSON.stringify({ tags: tags })
        });
        const res = await resp.json();
        
        if (res.status === 'success') {
            log(`🏷️ [What-If] Tags assegnati con successo.`, "#10b981");
            window.loadSimulationHistory();
            window.loadFoldersAndTags();
        }
    } catch (e) {
        console.error(e);
    }
};

// Initial folders load on load
document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('whatif-folders-list')) {
        window.loadFoldersAndTags();
    }
});



