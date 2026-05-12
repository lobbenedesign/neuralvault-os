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
            data.pages.forEach(p => {
                const div = document.createElement('div');
                div.className = 'nav-item';
                div.style.padding = '10px';
                div.style.fontSize = '0.7rem';
                div.innerHTML = `<i class="fas fa-file-alt" style="color:#a855f7; margin-right:8px;"></i> ${p.title}`;
                div.title = `Ultima modifica: ${p.last_modified}`;
                div.onclick = () => window.loadWikiPage(p.title, 'TECHNICAL', p.file_name);
                container.appendChild(div);
            });
        } else {
            container.innerHTML = '<div style="padding:10px; font-size:0.6rem; opacity:0.5; color:#ef4444;"><i class="fas fa-exclamation-triangle"></i> Wiki Vault Vuoto.</div>';
        }
    } catch (e) {
        console.error("Wiki List Error:", e);
        container.innerHTML = `<div style="padding:10px; font-size:0.6rem; color:#ef4444;"><i class="fas fa-shield-alt"></i> Errore Accesso: ${e.message}</div>`;
    }
};

window.loadWikiPage = async (topic, mode = 'TECHNICAL', fileName = null) => {
    try {
        const content = document.getElementById('wiki-portal-content');
        const hud = document.getElementById('wiki-epistemic-hud');
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
        window.updateWikiRightSidebar(data);
        
        // Applica classe modalità al body
        document.body.classList.add(`mode-${mode.toLowerCase()}`);
    } catch (e) {
        console.error("Load Wiki Error:", e);
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
                    label: n.title.substring(0, 15), 
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
    document.getElementById('nl-sim-prompt').value = query;
    window.closeSovereignModal();
    log(`🧙‍♂️ [Wizard] Scenario configurato: "${query}"`, "#facc15");
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
    const currentTopic = document.getElementById('wiki-portal-title')?.innerText || "Summary";
    log(`🔄 [v8.4] Switching to ${mode} mode...`, "#3b82f6");
    
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
};

window.loadWikiHistory = async (topic) => {
    try {
        const resp = await fetch(`/api/wiki/history?topic=${encodeURIComponent(topic)}`, {
            headers: { 'X-API-KEY': typeof VAULT_KEY !== 'undefined' ? VAULT_KEY : 'AURA-ADMIN-77' }
        });
        const data = await resp.json();
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
            div.innerHTML = `<div>${v.date}</div><div style="font-size:0.5rem; opacity:0.5;">${v.preview}</div>`;
            container.appendChild(div);
        });
    } catch (e) {
        console.error("Wiki History Error:", e);
    }
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
    container.innerHTML = '';
    
    // [v8.2] Sovereign Causal Scenario Button
    const scenarioBtn = document.createElement('button');
    scenarioBtn.className = 'glass-btn';
    scenarioBtn.style.width = '100%';
    scenarioBtn.style.marginBottom = '1rem';
    scenarioBtn.style.background = 'linear-gradient(135deg, #a855f7, #3b82f6)';
    scenarioBtn.style.color = '#fff';
    scenarioBtn.style.border = 'none';
    scenarioBtn.innerHTML = '🚀 GENERA SCENARIO SOVRANO (v8.2)';
    scenarioBtn.onclick = () => window.generateCausalScenario(data);
    container.appendChild(scenarioBtn);
    
    // [v8.1] Strategic Report Button
    const reportBtn = document.createElement('button');
    reportBtn.className = 'glass-btn';
    reportBtn.style.width = '100%';
    reportBtn.style.marginBottom = '1rem';
    reportBtn.style.border = '1px solid #a855f7';
    reportBtn.style.color = '#a855f7';
    reportBtn.innerHTML = '🏺 GENERA REPORT STRATEGICO';
    reportBtn.onclick = () => window.generateStrategicReport(data);
    container.appendChild(reportBtn);
    
    // Reset & Initialize Graph (v8.4 Sandbox)
    if (window.causalSandbox) {
        window.causalSandbox.init(data.affected_nodes, data.edges);
    }
    
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

            <div style="display:flex; gap:10px; margin-top:12px;">
                <button onclick="window.interviewNode('${n.id}', ${JSON.stringify(data).replace(/"/g, '&quot;')})" style="flex:1; background:rgba(168,85,247,0.1); border:1px solid #a855f7; color:#a855f7; font-size:0.55rem; padding:4px; border-radius:4px; cursor:pointer;">🎤 INTERVISTA</button>
                <button onclick="window.focusNebulaNode('${n.id}')" style="flex:1; background:rgba(255,255,255,0.05); border:1px solid #444; color:#fff; font-size:0.55rem; padding:4px; border-radius:4px; cursor:pointer;">🌌 FOCUS</button>
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

window.interviewNode = async (nodeId, context) => {
    log(`🎤 [Interview] Intervistando il nodo ${nodeId}...`, "#a855f7");
    try {
        const resp = await fetch('/api/wiki/simulate/interview', {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                'X-API-KEY': typeof VAULT_KEY !== 'undefined' ? VAULT_KEY : 'AURA-ADMIN-77' 
            },
            body: JSON.stringify({ node_id: nodeId, context: context })
        });
        const data = await resp.json();
        
        // Show result in a custom modal or alert for now
        window.showSovereignModal(`Intervista: ${data.title}`, data.response);
    } catch (e) {
        console.error("Interview Error:", e);
    }
};

window.runNaturalLanguageSimulation = async () => {
    const prompt = document.getElementById('nl-sim-prompt').value;
    if (!prompt) {
        alert("Inserisci uno scenario da simulare.");
        return;
    }
    
    // [v8.4] Recupero delle lenti selezionate
    const lensSelect = document.getElementById('sim-lens');
    const lensIds = lensSelect ? Array.from(lensSelect.selectedOptions).map(opt => opt.value) : ["standard"];
    
    // [v8.4] UI Feedback: Disabilita il bottone e mostra caricamento
    const btn = document.getElementById('btn-run-nl-sim');
    const btnIcon = document.getElementById('btn-run-nl-sim-icon');
    const btnText = document.getElementById('btn-run-nl-sim-text');
    
    if (btn) {
        btn.disabled = true;
        btn.style.opacity = '0.7';
        btn.style.cursor = 'wait';
        if (btnIcon) btnIcon.className = 'fas fa-circle-notch fa-spin';
        if (btnText) btnText.innerText = 'SIMULAZIONE IN CORSO... ATTENDERE (5-15s)';
    }

    // [v8.4] Recupero orizzonte temporale
    const horizonIdx = document.getElementById('sim-horizon')?.value || 0;
    const horizons = ["immediate", "mid_term", "long_term"];
    const horizon = horizons[horizonIdx];
    
    log(`🧠 [NL-WhatIf] Analisi scenario: "${prompt}" (Lenti: ${lensIds.join(', ')} | Mode: ${mode} | Horizon: ${horizon})...`, "#facc15");
    
    try {
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
                horizon: horizon
            })
        });


        const data = await resp.json();
        
        if (data.error) {
            log(`❌ Errore Simulazione: ${data.error}`, "#ef4444");
            alert(data.error);
            return;
        }

        log(`🎯 [NL-WhatIf] Scenario proiettato con successo.`, "#4ade80");
        renderSimulationResults(data);
        
    } catch (e) {
        console.error("NL Simulation Error:", e);
        log("❌ Errore durante la simulazione NL.", "#ef4444");
    } finally {
        // [v8.4] UI Feedback: Ripristina il bottone
        if (btn) {
            btn.disabled = false;
            btn.style.opacity = '1';
            btn.style.cursor = 'pointer';
            if (btnIcon) btnIcon.className = 'fas fa-bolt';
            if (btnText) btnText.innerText = 'ESEGUI SIMULAZIONE SOVRANA';
        }
    }
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
        
        window.showSovereignModal(`Report Strategico Sovrano`, data.report);
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
    document.getElementById('wiki-search-portal').value = id;
    window.runCausalSimulation();
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
    const topic = document.getElementById('wiki-portal-title')?.innerText || "Wiki_Export";
    const content = document.getElementById('wiki-portal-content').innerText;
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

window.updateWikiRightSidebar = (data) => {
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
    if (graphContainer && window.cytoscape && citations.length > 0) {
        graphContainer.innerHTML = '';
        const elements = [];
        // Root Topic
        elements.push({ data: { id: 'root', label: data.title, color: '#3b82f6' } });
        
        citations.slice(0, 10).forEach(c => {
            elements.push({ data: { id: c.node_id, label: c.node_id.substring(0,4), color: '#4ade80' } });
            elements.push({ data: { source: 'root', target: c.node_id } });
        });

        cytoscape({
            container: graphContainer,
            elements: elements,
            style: [
                { selector: 'node', style: { 'width': 10, 'height': 10, 'label': 'data(label)', 'font-size': '4px', 'color': '#fff', 'background-color': 'data(color)' } },
                { selector: 'edge', style: { 'width': 0.5, 'line-color': 'rgba(255,255,255,0.1)', 'curve-style': 'bezier' } }
            ],
            layout: { name: 'concentric', padding: 5 }
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
