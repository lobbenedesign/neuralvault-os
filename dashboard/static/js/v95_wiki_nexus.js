window.WIKI_NEXUS_VERSION = "9.6.0";

console.log("%c🚀 [v9.6] Neural Wiki Nexus: BOOT SEQUENCE STARTED", "color: #3b82f6; font-weight: bold; font-size: 1.2rem;");

window.initWikiNexus = () => {
    console.log("🛠️ [v9.6] Initializing Knowledge Nexus IDE Architecture...");
    try {
        const wikiGrid = document.getElementById('wiki-main-grid');
        if (wikiGrid) {
            wikiGrid.style.display = 'grid';
            wikiGrid.style.opacity = '1';
        }
        
        if (typeof window.refreshWikiList === 'function') {
            window.refreshWikiList();
        }

        const content = document.getElementById('wiki-kb-content-body') || document.getElementById('wiki-portal-content');
        if (content && content.querySelector('.wiki-dashboard-aura')) {
            content.innerHTML = '<div style="opacity:0.1; text-align:center; padding:5rem;"><i class="fas fa-book-open fa-3x"></i></div>';
        }
    } catch (e) {
        console.error("❌ [v9.6] Wiki Nexus Init Failed:", e);
    }
    
    if (!document.getElementById('wiki-agent-console')) {
        const consoleHTML = `
            <div id="wiki-agent-console" style="display:none; position:fixed; bottom:20px; right:20px; width:400px; height:300px; background:rgba(2,6,23,0.95); border:1px solid #3b82f6; border-radius:15px; z-index:10000; flex-direction:column; box-shadow:0 20px 50px rgba(0,0,0,0.8); backdrop-filter:blur(20px); overflow:hidden; font-family:'JetBrains Mono', monospace;">
                <div style="background:rgba(59,130,246,0.1); padding:10px 15px; border-bottom:1px solid rgba(59,130,246,0.3); display:flex; justify-content:space-between; align-items:center;">
                    <span style="font-size:0.6rem; color:#3b82f6; font-weight:900; letter-spacing:1px;"><i class="fas fa-terminal"></i> AGENT_NEXUS_CONSOLE</span>
                    <button onclick="window.closeAgentConsole()" style="background:transparent; border:none; color:#64748b; cursor:pointer;"><i class="fas fa-times"></i></button>
                </div>
                <div id="nexus-console-output" style="flex:1; padding:15px; font-size:0.65rem; color:#a855f7; overflow-y:auto; line-height:1.5;">
                    <div>> Nexus Link Established.</div>
                </div>
                <div style="padding:10px; border-top:1px solid rgba(255,255,255,0.05); display:flex; gap:10px;">
                    <input type="text" id="nexus-console-input" placeholder="Comando per Skywalker..." style="flex:1; background:transparent; border:none; color:#fff; font-size:0.65rem; outline:none;" onkeydown="if(event.key==='Enter') window.sendNexusCommand()">
                    <button onclick="window.sendNexusCommand()" style="background:transparent; border:none; color:#3b82f6; cursor:pointer;"><i class="fas fa-paper-plane"></i></button>
                </div>
            </div>
        `;
        document.body.insertAdjacentHTML('beforeend', consoleHTML);
    }
};

window.toggleWikiIntel = () => {
    const sidebar = document.getElementById('wiki-sidebar-container');
    const grid = document.getElementById('wiki-main-grid');
    
    if (sidebar && grid) {
        const isHidden = sidebar.style.display === 'none';
        sidebar.style.display = isHidden ? 'flex' : 'none';
        
        // Nuovo layout a 2 colonne: Sidebar (320px) | Content (1fr)
        grid.style.gridTemplateColumns = isHidden ? '320px 1fr' : '0px 1fr';
    }
};

window.parseWikiMetadata = (markdown) => {
    const yamlRegex = /^---\n([\s\S]*?)\n---/;
    const match = markdown.match(yamlRegex);
    if (match) {
        const yamlStr = match[1];
        const metadata = {};
        yamlStr.split('\n').forEach(line => {
            const parts = line.split(':');
            if (parts.length >= 2) {
                metadata[parts[0].trim()] = parts.slice(1).join(':').trim().replace(/"/g, '');
            }
        });
        return { 
            metadata, 
            cleanMarkdown: markdown.replace(yamlRegex, '').trim() 
        };
    }
    return { metadata: null, cleanMarkdown: markdown };
};

window.renderCausalGraph = (topic, data) => {
    const container = document.getElementById('wiki-mini-graph');
    if (!container) return;

    let svg = `<svg viewBox="0 0 200 200" style="width:100%; height:100%; filter: drop-shadow(0 0-10px rgba(59,130,246,0.2));">
        <defs>
            <linearGradient id="nodeGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" style="stop-color:#3b82f6;stop-opacity:1" />
                <stop offset="100%" style="stop-color:#a855f7;stop-opacity:1" />
            </linearGradient>
        </defs>
    `;

    const nodes = data.citations ? data.citations.slice(0, 5) : [];
    const centerX = 100, centerY = 100;
    
    svg += `<circle cx="${centerX}" cy="${centerY}" r="12" fill="url(#nodeGrad)" opacity="0.8">
        <animate attributeName="r" values="12;14;12" dur="3s" repeatCount="indefinite" />
    </circle>`;
    
    nodes.forEach((node, i) => {
        const angle = (i / nodes.length) * Math.PI * 2;
        const x = centerX + Math.cos(angle) * 60;
        const y = centerY + Math.sin(angle) * 60;
        svg += `<line x1="${centerX}" y1="${centerY}" x2="${x}" y2="${y}" stroke="rgba(59,130,246,0.2)" stroke-width="1" stroke-dasharray="2,2" />`;
        svg += `<circle cx="${x}" cy="${y}" r="6" fill="#0f172a" stroke="#3b82f6" stroke-width="1">
            <animate attributeName="opacity" values="0.4;1;0.4" dur="${2 + i}s" repeatCount="indefinite" />
        </circle>`;
    });

    svg += `</svg>`;
    container.innerHTML = svg;
};

/**
 * 🛰️ [v10.0] Sovereign Status Modal (SSM-001)
 * Provides real-time feedback on agentic foraging and crystallization.
 */
window.showSovereignStatusModal = (topic, status = "FORAGING") => {
    let modal = document.getElementById('sovereign-status-modal');
    if (!modal) {
        const modalHTML = `
            <div id="sovereign-status-modal" style="position:fixed; top:0; left:0; width:100vw; height:100vh; background:rgba(2,6,23,0.85); backdrop-filter:blur(20px); z-index:99999; display:flex; align-items:center; justify-content:center; opacity:0; transition:all 0.5s cubic-bezier(0.4, 0, 0.2, 1); pointer-events:none; font-family:'Outfit', sans-serif;">
                <div class="glass-card" style="width:500px; padding:40px; border:1px solid rgba(59,130,246,0.3); text-align:center; box-shadow:0 40px 100px rgba(0,0,0,0.8); position:relative; overflow:hidden; border-radius:30px;">
                    <!-- Background Glow -->
                    <div style="position:absolute; top:-50%; left:-50%; width:200%; height:200%; background:radial-gradient(circle, rgba(59,130,246,0.1) 0%, transparent 70%); animation:nexusRotate 20s linear infinite;"></div>
                    
                    <!-- Top-Right Close Button -->
                    <button onclick="window.hideSovereignStatusModal()" style="position:absolute; top:20px; right:20px; background:rgba(255,255,255,0.05); border:1px solid rgba(255,255,255,0.1); color:#64748b; width:30px; height:30px; border-radius:50%; cursor:pointer; display:flex; align-items:center; justify-content:center; font-size:0.8rem; transition:0.3s; z-index:10;" onmouseover="this.style.color='#fff'; this.style.borderColor='rgba(255,255,255,0.3)';" onmouseout="this.style.color='#64748b'; this.style.borderColor='rgba(255,255,255,0.1)';">
                        <i class="fas fa-times"></i>
                    </button>
                    
                    <div id="ssm-icon-container" style="margin-bottom:2rem; position:relative; z-index:1;">
                        <i class="fas fa-brain fa-spin" style="font-size:4rem; color:#3b82f6; filter:drop-shadow(0 0 20px rgba(59,130,246,0.5));"></i>
                    </div>
                    
                    <h2 id="ssm-title" style="letter-spacing:10px; font-weight:900; color:#fff; margin-bottom:1rem; font-size:1.2rem; position:relative; z-index:1;">SKYWALKER DISPATCHED</h2>
                    <div id="ssm-topic" style="font-family:'JetBrains Mono'; font-size:0.7rem; color:#3b82f6; margin-bottom:2rem; opacity:0.8; position:relative; z-index:1;">[UPLINKING]: \${topic.toUpperCase()}</div>
                    
                    <div style="background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.05); border-radius:12px; padding:20px; position:relative; z-index:1;">
                        <div id="ssm-status-bar" style="height:2px; background:rgba(59,130,246,0.2); width:100%; border-radius:1px; margin-bottom:15px; overflow:hidden;">
                            <div id="ssm-progress" style="height:100%; width:30%; background:#3b82f6; box-shadow:0 0 10px #3b82f6; transition:width 1s ease;"></div>
                        </div>
                        <div id="ssm-status-text" style="font-size:0.6rem; color:#94a3b8; text-transform:uppercase; letter-spacing:2px; font-weight:800;">Scanning Outer Rim...</div>
                    </div>
                    
                    <div style="margin-top:2rem; display:flex; justify-content:center; gap:20px; position:relative; z-index:1;">
                        <div style="text-align:center;">
                            <div id="ssm-agent-fs77" style="width:10px; height:10px; border-radius:50%; background:#3b82f6; margin:0 auto 5px; box-shadow:0 0 10px #3b82f6;"></div>
                            <span style="font-size:0.5rem; color:#64748b;">FS-77</span>
                        </div>
                        <div style="text-align:center;">
                            <div id="ssm-agent-pb404" style="width:10px; height:10px; border-radius:50%; background:#64748b; margin:0 auto 5px;"></div>
                            <span style="font-size:0.5rem; color:#64748b;">PB-404</span>
                        </div>
                    </div>
                    
                    <!-- Abort/Dismiss Button -->
                    <button onclick="window.hideSovereignStatusModal()" style="margin-top:2rem; background:rgba(239,68,68,0.1); border:1px solid rgba(239,68,68,0.2); color:#ef4444; padding:10px 20px; border-radius:12px; font-size:0.65rem; font-weight:800; cursor:pointer; text-transform:uppercase; letter-spacing:1px; transition:0.3s; position:relative; z-index:10; font-family:'Outfit';" onmouseover="this.style.background='rgba(239,68,68,0.2)';" onmouseout="this.style.background='rgba(239,68,68,0.1)';">
                        <i class="fas fa-ban"></i> Abort / Close View
                    </button>
                </div>
            </div>
            <style>
                @keyframes nexusRotate { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
            </style>
        `;
        document.body.insertAdjacentHTML('beforeend', modalHTML);
        modal = document.getElementById('sovereign-status-modal');
    }

    modal.style.opacity = '1';
    modal.style.pointerEvents = 'all';
    
    // Update content based on status
    const title = document.getElementById('ssm-title');
    const statusText = document.getElementById('ssm-status-text');
    const progress = document.getElementById('ssm-progress');
    const fs77 = document.getElementById('ssm-agent-fs77');
    const pb404 = document.getElementById('ssm-agent-pb404');
    const icon = document.querySelector('#ssm-icon-container i');

    if (status === "FORAGING") {
        title.innerText = "SKYWALKER DISPATCHED";
        statusText.innerText = "Scanning Outer Rim...";
        progress.style.width = "40%";
        icon.className = "fas fa-brain fa-spin";
        icon.style.color = "#3b82f6";
        fs77.style.background = "#3b82f6";
        fs77.style.boxShadow = "0 0 10px #3b82f6";
        pb404.style.background = "#64748b";
        pb404.style.boxShadow = "none";
    } else if (status === "CRYSTALLIZING") {
        title.innerText = "PRESSMAN ACTIVE";
        statusText.innerText = "Forging Knowledge Dossier...";
        progress.style.width = "80%";
        icon.className = "fas fa-scroll";
        icon.style.color = "#a855f7";
        fs77.style.background = "#10b981";
        pb404.style.background = "#a855f7";
        pb404.style.boxShadow = "0 0 10px #a855f7";
    }
};

window.hideSovereignStatusModal = () => {
    const modal = document.getElementById('sovereign-status-modal');
    if (modal) {
        modal.style.opacity = '0';
        modal.style.pointerEvents = 'none';
    }
};

const originalLoadWikiPage = window.loadWikiPage;
window.loadWikiPage = async (topic, mode = 'TECHNICAL', fileName = null) => {
    if (!topic) return;
    
    // 🚀 [v10.0] Show Sovereign Status Modal
    window.showSovereignStatusModal(topic, "FORAGING");
    
    const content = document.getElementById('wiki-kb-content-body') || document.getElementById('wiki-portal-content');
    const titleEl = document.getElementById('wiki-kb-title') || document.getElementById('wiki-portal-title');
    
    // Switch view to KB if not already there
    window.switchWikiView('kb');

    if (titleEl) titleEl.innerText = topic.toUpperCase();
    
    if (content) {
        content.innerHTML = `
            <div id="nexus-loading-state" style="text-align: center; padding: 5rem; animation: pulse 2s infinite;">
                <i class="fas fa-brain fa-spin" style="font-size: 3rem; color: #3b82f6; margin-bottom: 2rem;"></i>
                <h2 style="letter-spacing: 5px; color: #fff; font-size: 1rem;">SKYWALKER IS FORAGING...</h2>
                <div style="font-family:'JetBrains Mono'; font-size:0.5rem; color:#3b82f6; margin-top:10px;">[UPLINKING]: ${topic}</div>
            </div>
        `;
    }

    try {
        if (typeof originalLoadWikiPage === 'function') {
            await originalLoadWikiPage(topic, mode, fileName);
        }
        
        // [v10.0] Perspective Tracking
        window.currentWikiPage = fileName || topic + '.md';
        window.currentWikiMode = mode;

        // Post-processing: Clean metadata and update sidebars
        const metaHeader = document.getElementById('wiki-page-metadata');
        const resp = await fetch(`/api/wiki/read?file=${encodeURIComponent(window.currentWikiPage)}&mode=${mode}`, { 
            headers: { 'X-API-KEY': window.VAULT_KEY } 
        });
        
        if (resp.ok) {
            const data = await resp.json();
            const { metadata, cleanMarkdown } = window.parseWikiMetadata(data.markdown);
            
            // 🛑 [v10.0] If still researching, keep modal or update it
            if (metadata && metadata.status === "RESEARCHING") {
                window.showSovereignStatusModal(topic, "FORAGING");
            } else {
                window.hideSovereignStatusModal();
            }

            if (metadata) {
                if (metaHeader) metaHeader.innerHTML = `v${metadata.version} | ${metadata.epistemic_fingerprint.substring(0,8)}... | ${metadata.z3_verified === 'true' ? '🛡️ VERIFIED' : '⚠️ UNVERIFIED'}`;
                
                // Re-render main content without YAML if it was leaked
                if (content && content.innerText.includes('epistemic_fingerprint')) {
                    content.innerHTML = window.processWikiMarkdown ? window.processWikiMarkdown(cleanMarkdown, data.citations || []) : cleanMarkdown;
                }

                // Update Article Header and Metadata Fields dynamically
                const authorEl = document.getElementById('wiki-kb-author');
                if (authorEl) authorEl.innerText = metadata.originally_forged_by || metadata.author || 'Yoda';
                
                const verifierEl = document.getElementById('wiki-kb-verifier');
                if (verifierEl) verifierEl.innerText = metadata.confirmed_by || metadata.verifier || 'Skywalker';
                
                const updatedEl = document.getElementById('wiki-kb-updated');
                if (updatedEl) updatedEl.innerText = metadata.last_updated || '3 hours ago';
                
                const domainEl = document.getElementById('wiki-meta-domain');
                if (domainEl) domainEl.innerText = metadata.domain || 'Knowledge Base';
                
                const securityEl = document.getElementById('wiki-meta-security');
                if (securityEl) {
                    securityEl.innerText = metadata.classification || metadata.security_classification || 'Internal';
                    securityEl.style.color = (metadata.classification === 'Public' ? '#10b981' : '#ef4444');
                }
                
                const peersEl = document.getElementById('wiki-meta-peers');
                if (peersEl) peersEl.innerText = metadata.peer_attestations || `${metadata.originally_forged_by || 'Yoda'}, ${metadata.confirmed_by || 'Skywalker'}`;

                // Update Provenance with Metadata
                const provEl = document.getElementById('wiki-provenance-list');
                if (provEl && metadata.source_nodes) {
                    try {
                        const sources = JSON.parse(metadata.source_nodes.replace(/'/g, '"'));
                        provEl.innerHTML = sources.map(s => `
                            <div class="intelligence-section" style="padding: 8px; font-size: 0.55rem; border-left: 2px solid #10b981; margin-bottom: 5px;">
                                <i class="fas fa-link"></i> NODE_${s.substring(0,8)}
                            </div>
                        `).join('');
                    } catch(e) {}
                }
            }
            
            window.renderCausalGraph(topic, data);
            
            // Refresh selection class in split sidebar
            if (window.fullKBList) {
                window.renderKBSplitList(window.fullKBList);
            }
        } else {
            window.hideSovereignStatusModal();
        }
    } catch (e) {
        console.error("Nexus load failed:", e);
        window.hideSovereignStatusModal();
    }
};

window.setWikiPerspective = (mode) => {
    console.log(`🎭 Setting Wiki Perspective to: ${mode}`);
    
    // Update UI buttons
    document.querySelectorAll('.lens-btn').forEach(btn => {
        btn.classList.remove('active');
        btn.style.color = '#64748b';
    });
    
    const activeBtn = document.getElementById(`lens-${mode.toLowerCase().substring(0,4)}`);
    if (activeBtn) {
        activeBtn.classList.add('active');
        activeBtn.style.color = '#3b82f6';
    }

    // Reload current page with new perspective
    if (window.currentWikiPage) {
        const topic = window.currentWikiPage.replace('.md', '');
        window.loadWikiPage(topic, mode, window.currentWikiPage);
    }
};

window.toggleWikiSidebar = () => {
    console.log("↔️ Toggling Wiki Sidebar");
    const wikiSidebar = document.querySelector('.wiki-v3-sidebar');
    if (wikiSidebar) {
        wikiSidebar.classList.toggle('collapsed');
    }
};

window.switchWikiView = (viewId, agentName = null) => {
    console.log(`🔄 Switching Wiki View to: ${viewId}`);
    
    // Redirect any legacy simulation subview requests to the unified global What-If engine section
    if (viewId === 'simulation') {
        if (typeof window.showSection === 'function') {
            window.showSection('simulation');
        }
        return;
    }
    
    // Hide all subviews
    const subviews = [
        'wiki-subview-dashboard', 
        'wiki-subview-agent-profile', 
        'wiki-subview-kb', 
        'wiki-subview-kb-list',
        'wiki-subview-reports', 
        'wiki-subview-activity',
        'wiki-subview-agents',
        'wiki-subview-settings',
        'wiki-subview-forensic',
        'wiki-subview-pure-wiki'
    ];
    
    subviews.forEach(id => {
        const el = document.getElementById(id);
        if (el) el.style.display = 'none';
    });

    // Update nav active state
    document.querySelectorAll('.wiki-nav-item').forEach(item => {
        item.classList.remove('active');
        const itemView = item.getAttribute('data-view');
        const normalizedView = viewId.replace('agent-profile', 'agents');
        if (itemView === normalizedView || itemView === viewId || 
            item.innerText.toLowerCase().includes(normalizedView.replace('pure-wiki', 'pure wiki').replace('kb-list', 'knowledge base').replace('kb', 'knowledge base').replace('forensic', 'forensic audit'))) {
            item.classList.add('active');
        }
    });

    // Ensure wiki sidebar is always displayed
    const wikiSidebar = document.querySelector('.wiki-v3-sidebar');
    if (wikiSidebar) {
        wikiSidebar.style.display = 'flex';
    }

    // Show target view
    const targetId = `wiki-subview-${viewId}`;
    const target = document.getElementById(targetId);
    if (target) {
        target.style.display = 'block';
        target.classList.add('wiki-view-active');
        
        // Specific logic for views
        if (viewId === 'dashboard') {
            window.initWikiDashboardCharts();
            window.refreshWikiDashboardActivity();
        } else if (viewId === 'agent-profile') {
            window.loadAgentProfile(agentName || 'Skywalker');
        } else if (viewId === 'agents') {
            window.initWikiAgentsGrid();
        } else if (viewId === 'settings') {
            window.initWikiSettings();
        } else if (viewId === 'activity') {
            window.initWikiActivityFeed();
        } else if (viewId === 'reports') {
            window.initWikiReportsCharts();
        } else if (viewId === 'kb-list' || viewId === 'kb') {
            window.initWikiKBList();
            window.initWikiGalaxies();
        } else if (viewId === 'pure-wiki') {
            if (window.initPureWiki) window.initPureWiki();
        } else if (viewId === 'forensic') {
            window.initWikiForensic();
        }
    }
    
    // Scroll content hub to top
    const hub = document.getElementById('wiki-content-hub');
    if (hub) hub.scrollTop = 0;
};

window.initWikiDashboardCharts = () => {
    // 📊 Agent Performance Chart (Skywalker & Yoda)
    const perfCtx = document.getElementById('wiki-perf-chart');
    if (perfCtx && !window.wikiPerfChart) {
        window.wikiPerfChart = new Chart(perfCtx, {
            type: 'line',
            data: {
                labels: ['12:00', '14:00', '18:00', '12:00', '18:00', '20:00', '24:00', '24h'],
                datasets: [
                    {
                        label: 'Skywalker',
                        data: [25, 75, 60, 55, 70, 85, 96, 96.3],
                        borderColor: '#3b82f6',
                        backgroundColor: 'rgba(59, 130, 246, 0.1)',
                        fill: true,
                        tension: 0.4
                    },
                    {
                        label: 'Yoda',
                        data: [15, 65, 50, 60, 95, 80, 92, 94.1],
                        borderColor: '#10b981',
                        backgroundColor: 'rgba(16, 185, 129, 0.1)',
                        fill: true,
                        tension: 0.4
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    y: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#64748b' } },
                    x: { grid: { display: false }, ticks: { color: '#64748b' } }
                }
            }
        });
    }

    // 🥧 Source Distribution Pie
    const pieCtx = document.getElementById('wiki-source-pie');
    if (pieCtx && !window.wikiSourcePie) {
        window.wikiSourcePie = new Chart(pieCtx, {
            type: 'doughnut',
            data: {
                datasets: [{
                    data: [22, 28, 35, 10, 5],
                    backgroundColor: ['#3b82f6', '#f97316', '#10b981', '#a855f7', '#64748b'],
                    borderWidth: 0
                }]
            },
            options: {
                cutout: '70%',
                plugins: { legend: { display: false } }
            }
        });
    }
};

window.initWikiReportsCharts = () => {
    // 📊 Foraging Time Analysis
    const forageCtx = document.getElementById('wiki-forage-time-chart');
    if (forageCtx && !window.wikiForageChart) {
        window.wikiForageChart = new Chart(forageCtx, {
            type: 'bar',
            data: {
                labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                datasets: [{
                    label: 'Avg Response (ms)',
                    data: [120, 150, 110, 130, 190, 140, 125],
                    backgroundColor: 'rgba(59, 130, 246, 0.5)',
                    borderColor: '#3b82f6',
                    borderWidth: 1
                }]
            },
            options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } } }
        });
    }

    // 📉 Failure Analysis
    const failCtx = document.getElementById('wiki-failure-chart');
    if (failCtx && !window.wikiFailureChart) {
        window.wikiFailureChart = new Chart(failCtx, {
            type: 'doughnut',
            data: {
                labels: ['429 (Rate Limit)', 'Timeout', 'CAPTCHA', 'Other'],
                datasets: [{
                    data: [45, 25, 20, 10],
                    backgroundColor: ['#ef4444', '#f59e0b', '#a855f7', '#64748b'],
                    borderWidth: 0
                }]
            },
            options: { cutout: '60%', plugins: { legend: { position: 'right', labels: { color: '#64748b', font: { size: 10 } } } } }
        });
    }

    // 📈 Synthesis Progress
    const synthCtx = document.getElementById('wiki-synthesis-chart');
    if (synthCtx && !window.wikiSynthesisChart) {
        window.wikiSynthesisChart = new Chart(synthCtx, {
            type: 'line',
            data: {
                labels: ['W1', 'W2', 'W3', 'W4'],
                datasets: [{
                    label: 'Nodes Created',
                    data: [1200, 2500, 4800, 7200],
                    borderColor: '#10b981',
                    tension: 0.4,
                    fill: true,
                    backgroundColor: 'rgba(16, 185, 129, 0.1)'
                }]
            },
            options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } } }
        });
    }
};

window.refreshWikiDashboardActivity = async () => {
    const body = document.getElementById('wiki-recent-insights-body');
    if (!body) return;

    try {
        const resp = await fetch('/api/wiki/list', { headers: { 'X-API-KEY': window.VAULT_KEY } });
        if (resp.ok) {
            const data = await resp.json();
            const recent = data.pages.slice(0, 5); // Get latest 5
            body.innerHTML = recent.map(p => `
                <tr style="border-bottom: 1px solid rgba(255,255,255,0.02);">
                    <td style="padding: 12px;"><b style="color: #fff;">${p.title}</b><br><span style="color: #64748b; font-size: 0.55rem;">${p.namespace}</span></td>
                    <td style="padding: 12px;"><span style="color: #3b82f6; font-size: 0.6rem;">Vault</span></td>
                    <td style="padding: 12px;">${p.last_modified.split('T')[0]}</td>
                    <td style="padding: 12px; opacity: 0.6; font-size: 0.6rem;">Knowledge node forged via ${p.namespace}.</td>
                </tr>
            `).join('');
        }
    } catch (e) {
        console.error("❌ Error refreshing dashboard activity:", e);
    }
};

window.loadAgentProfile = (name) => {
    console.log(`👤 Loading Profile for Agent: ${name}`);
    const nameEl = document.getElementById('view-agent-name');
    const idEl = document.getElementById('view-agent-id');
    const avatarEl = document.getElementById('view-agent-avatar');
    const roleEl = document.getElementById('view-agent-role');
    const descEl = document.getElementById('view-agent-desc');
    const chartTitleEl = document.getElementById('view-agent-chart-title');
    const metricsContainer = document.getElementById('view-agent-metrics-container');
    const logsContainer = document.getElementById('view-agent-logs-container');
    
    // Default fallback profile
    const defaultProfile = {
        role: 'Autonomous System Swarm Agent',
        avatarBg: '3b82f6',
        desc: 'Agente neurale autonomo specializzato in compiti di routine, sincronizzazione dei metadati ed esecuzione dei job paralleli nel cluster.',
        chartLabel: 'Attività Agente / Carico di Lavoro (24h)',
        chartData: [20, 45, 65, 80, 95, 110],
        chartLabels: ['10:00', '11:00', '12:00', '13:00', '14:00', '15:00'],
        borderColor: '#3b82f6',
        bgColor: 'rgba(59, 130, 246, 0.1)',
        metrics: [
            { label: 'Efficienza Operativa', val: '97.2%', color: '#10b981' },
            { label: 'Task Elaborati', val: '142', color: '#3b82f6' },
            { label: 'Latenza Risposta', val: '42ms', color: '#fbbf24' }
        ],
        logs: [
            '🟢 [System] Inizializzazione agente completata.',
            '🔄 [Sync] Sincronizzazione dei metadati di rete.',
            '⚙️ [Task] Esecuzione job di manutenzione ordinaria.',
            '✅ [Idle] In attesa di nuove disposizioni dall’oracolo.'
        ]
    };

    // Profiles Mapping
    const profiles = {
        'Skywalker': {
            role: 'Autonomous Web Forager (FS-77)',
            avatarBg: '3b82f6',
            desc: 'Specializzato nella raccolta di conoscenza esterna e crawling stealth. Monitora motori di ricerca multipli (Google, Startpage, DuckDuckGo) bypassando i blocchi DNS tramite circuit breaker integrati.',
            chartLabel: 'Ricerche Web / Foraging Rate (24h)',
            chartData: [45, 98, 173, 220, 310, 489],
            chartLabels: ['10:00', '11:00', '12:00', '13:00', '14:00', '15:00'],
            borderColor: '#3b82f6',
            bgColor: 'rgba(59, 130, 246, 0.1)',
            metrics: [
                { label: 'Efficienza Foraging', val: '98.5%', color: '#10b981' },
                { label: 'Ricerche Eseguite', val: '3,842', color: '#3b82f6' },
                { label: 'Bypass DNS Attivi', val: '24/24', color: '#fbbf24' }
            ],
            logs: [
                '🔍 [Stealth] Foraging avviato per keyword "Quantum Regression".',
                '🟢 [DNS/Fallback] Bypass DoH completato con successo.',
                '💾 [IPFS] Salvato blocco cifrato zdj7Wa94be5ba...',
                '⚡ [LaserStorm] Scarica sinaptica iniettata nel database.'
            ]
        },
        'Yoda': {
            role: 'Semantic Consensus Judge (YO-001)',
            avatarBg: '10b981',
            desc: 'Responsabile della validazione dei nodi di conoscenza e della risoluzione dei conflitti epistemici attraverso il protocollo di consenso a Tre Giudici (Supreme Court).',
            chartLabel: 'Conflitti Risolti / Consenso (24h)',
            chartData: [12, 19, 32, 45, 51, 68],
            chartLabels: ['10:00', '11:00', '12:00', '13:00', '14:00', '15:00'],
            borderColor: '#10b981',
            bgColor: 'rgba(16, 185, 129, 0.1)',
            metrics: [
                { label: 'Consenso Raggiunto', val: '99.8%', color: '#10b981' },
                { label: 'Galassie Mappate', val: '142', color: '#a855f7' },
                { label: 'Nodi Esaminati', val: '8,412', color: '#3b82f6' }
            ],
            logs: [
                '🧠 [Consensus] Convocata Corte Suprema per conflitto ID node-4412.',
                '⚖️ [Verdict] Approvata validità epistemica con score 0.94.',
                '🌌 [Galaxy] Mappata nuova costellazione "Financial Regressions".',
                '🟢 [Sync] Allineamento causale dei link completato.'
            ]
        },
        'R2-D2': {
            role: 'Sovereign Graph Organizer',
            avatarBg: 'fbbf24',
            desc: 'Agente di manutenzione e riorganizzazione geometrica del grafo. Rileva nodi orfani, rimuove duplicati e ottimizza il layout del database KùzuDB.',
            chartLabel: 'Compattazione DB / Nodi Riorganizzati',
            chartData: [120, 240, 310, 480, 600, 780],
            chartLabels: ['10:00', '11:00', '12:00', '13:00', '14:00', '15:00'],
            borderColor: '#fbbf24',
            bgColor: 'rgba(251, 191, 36, 0.1)',
            metrics: [
                { label: 'Nodi Riorganizzati', val: '12,940', color: '#fbbf24' },
                { label: 'Deduplicazione', val: '94.2%', color: '#10b981' },
                { label: 'Spazio Guadagnato', val: '412 MB', color: '#3b82f6' }
            ],
            logs: [
                '🤖 [Organizer] Avviata scansione nodi orfani nel namespace General.',
                '🗑️ [Cleanup] Eliminati 42 duplicati semantici obsoleti.',
                '📈 [Compaction] Ottimizzazione database KùzuDB completata.',
                '⚙️ [Layout] Ricalcolato bilanciamento delle forze dinamiche del grafo.'
            ]
        },
        'Paperboy': {
            role: 'Telemetry Broadcaster (PB-404)',
            avatarBg: 'ec4899',
            desc: 'Agente deputato alla sintesi della conoscenza e alla redazione automatica di SITREP, report di telemetria e comunicati per i canali esterni.',
            chartLabel: 'Report Generati / SITREP Finalizzati',
            chartData: [4, 8, 12, 18, 22, 28],
            chartLabels: ['10:00', '11:00', '12:00', '13:00', '14:00', '15:00'],
            borderColor: '#ec4899',
            bgColor: 'rgba(236, 72, 153, 0.1)',
            metrics: [
                { label: 'Artifacts Generati', val: '154', color: '#ec4899' },
                { label: 'SITREPs Finalizzati', val: '32', color: '#10b981' },
                { label: 'Compressione Testo', val: '64%', color: '#3b82f6' }
            ],
            logs: [
                '📰 [Broadcaster] Compilato report SITREP su "Epistemic Security".',
                '📢 [Broadcast] Telemetria distribuita ai canali sottoscritti.',
                '📄 [Artifact] Generato ed esportato roadmap_v13_cognitive_deepcore.md.',
                '🚴 [Cycle] Animazione Paperboy sincronizzata al frame rate.'
            ]
        },
        'Mandalorian': {
            role: 'Dynamic Path Finder (DN-099)',
            avatarBg: '8b5cf6',
            desc: 'Traccia i percorsi ottimali di navigazione tra i concetti della rete neurale, ottimizzando gli archi di congiunzione e gestendo i flussi di transizione dei nodi.',
            chartLabel: 'Archi Ottimizzati / Pathfinding (24h)',
            chartData: [320, 480, 610, 890, 1100, 1429],
            chartLabels: ['10:00', '11:00', '12:00', '13:00', '14:00', '15:00'],
            borderColor: '#8b5cf6',
            bgColor: 'rgba(139, 92, 246, 0.1)',
            metrics: [
                { label: 'Archi Ottimizzati', val: '1,429', color: '#8b5cf6' },
                { label: 'Frequenza Scansione', val: '4.2 Hz', color: '#10b981' },
                { label: 'Connessioni Salve', val: '100%', color: '#3b82f6' }
            ],
            logs: [
                '⚔️ [Pathfinding] Eseguita scansione dello spettro delle galassie.',
                '🟢 [Scanner] Raggi laser di tracciamento agganciati su AURA-OS.',
                '🔄 [Merge] Fusione e semplificazione di 12 archi ridondanti.',
                '🚀 [Thruster] Incremento potenza di posizionamento al 85%.'
            ]
        },
        'Smith': {
            role: 'Aegis Security Sentinel (AG-001)',
            avatarBg: 'ef4444',
            desc: 'Protezione perimetrale e difesa attiva. Isola minacce esterne, valida i pacchetti di transazione sul registro Aegis Ledger e gestisce il firewall di rete.',
            chartLabel: 'Minacce Bloccate / Attacchi Respinti',
            chartData: [2, 5, 14, 28, 37, 49],
            chartLabels: ['10:00', '11:00', '12:00', '13:00', '14:00', '15:00'],
            borderColor: '#ef4444',
            bgColor: 'rgba(239, 68, 68, 0.1)',
            metrics: [
                { label: 'Minacce Bloccate', val: '49', color: '#ef4444' },
                { label: 'Ispezioni Registro', val: '2,841', color: '#3b82f6' },
                { label: 'Integrità Ledger', val: '100%', color: '#10b981' }
            ],
            logs: [
                '🛡️ [Security] Avviata ispezione di routine su aegis_event_log.jsonl.',
                '🔴 [Alert] Rilevato tentativo di intrusione da sorgente non accreditata.',
                '⚡ [Defense] Attivato protocollo Fulmine Smith: minaccia neutralizzata.',
                '🔒 [Ledger] Registro Aegis Ledger validato e sigillato.'
            ]
        },
        'Synth': {
            role: 'Synaptic Spark Generator (SY-009)',
            avatarBg: '06b6d4',
            desc: 'Stimola la creatività di rete generando associazioni non-ovvie e speculazioni cognitive (Sparks) tra nodi distanti per arricchire l’epistemologia del RAG.',
            chartLabel: 'Sparks Creativi Generati (24h)',
            chartData: [45, 92, 156, 210, 290, 380],
            chartLabels: ['10:00', '11:00', '12:00', '13:00', '14:00', '15:00'],
            borderColor: '#06b6d4',
            bgColor: 'rgba(6, 182, 212, 0.1)',
            metrics: [
                { label: 'Scintille Generate', val: '380', color: '#06b6d4' },
                { label: 'Indice Creatività', val: '8.7/10', color: '#10b981' },
                { label: 'Densità Relazionale', val: '+24%', color: '#3b82f6' }
            ],
            logs: [
                '🌟 [Spark] Avviata oscillazione arcobaleno del core energetico.',
                '🧠 [Synthesis] Forgiata associazione causale tra "Medie Mobili" e "Macroeconomia".',
                '⚡ [Synaptic] Attivata scarica neurale su 8 nodi di General.',
                '🌈 [Rainbow] Beams emessi con intensità 2.0. Status: Eccellente.'
            ]
        }
    };

    const p = profiles[name] || defaultProfile;

    // Apply main labels
    if (nameEl) nameEl.innerText = name;
    if (idEl) idEl.innerText = name;
    if (roleEl) roleEl.innerText = p.role;
    if (descEl) descEl.innerText = p.desc;
    if (chartTitleEl) chartTitleEl.innerText = p.chartLabel;
    
    if (avatarEl) {
        avatarEl.src = `https://ui-avatars.com/api/?name=${name}&background=${p.avatarBg}&color=fff`;
        avatarEl.style.borderColor = `#${p.avatarBg}`;
    }

    // Populate Custom Metrics cards
    if (metricsContainer) {
        metricsContainer.innerHTML = p.metrics.map(m => `
            <div class="wiki-widget-card" style="display: flex; justify-content: space-between; align-items: center; padding: 12px 18px; border-left: 4px solid ${m.color}; background: rgba(0,0,0,0.15);">
                <div style="font-size: 0.6rem; color: #94a3b8; font-weight: 800; text-transform: uppercase; font-family: 'Outfit';">${m.label}</div>
                <div style="font-size: 1.15rem; font-weight: 900; color: #fff; font-family: 'JetBrains Mono';">${m.val}</div>
            </div>
        `).join('');
    }

    // Populate Custom Live Logs
    if (logsContainer) {
        logsContainer.innerHTML = p.logs.map(log => {
            let color = '#cbd5e1';
            if (log.includes('🔴') || log.includes('[Alert]')) color = '#f87171';
            else if (log.includes('🟢') || log.includes('[Sync]') || log.includes('✅')) color = '#34d399';
            else if (log.includes('🔍') || log.includes('🤖')) color = '#60a5fa';
            else if (log.includes('⚡') || log.includes('🚨')) color = '#fbbf24';
            return `<div style="color: ${color}; line-height: 1.4; border-bottom: 1px solid rgba(255,255,255,0.02); padding-bottom: 4px;">${log}</div>`;
        }).join('');
        // Scroll to bottom
        logsContainer.scrollTop = logsContainer.scrollHeight;
    }

    // Init Profile specific charts with customized data
    const memCtx = document.getElementById('view-agent-mem-chart');
    if (memCtx) {
        if (window.agentMemChart) window.agentMemChart.destroy();
        window.agentMemChart = new Chart(memCtx, {
            type: 'line',
            data: {
                labels: p.chartLabels,
                datasets: [{
                    label: p.chartLabel,
                    data: p.chartData,
                    borderColor: p.borderColor,
                    tension: 0.4,
                    fill: true,
                    backgroundColor: p.bgColor,
                    borderWidth: 2,
                    pointRadius: 3,
                    pointBackgroundColor: p.borderColor
                }]
            },
            options: { 
                responsive: true, 
                maintainAspectRatio: false, 
                plugins: { 
                    legend: { display: false } 
                },
                scales: {
                    x: {
                        grid: { color: 'rgba(255,255,255,0.03)' },
                        ticks: { color: '#64748b', font: { size: 9, family: 'JetBrains Mono' } }
                    },
                    y: {
                        grid: { color: 'rgba(255,255,255,0.03)' },
                        ticks: { color: '#64748b', font: { size: 9, family: 'JetBrains Mono' } }
                    }
                }
            }
        });
    }
};

window.initWikiAgentsGrid = async () => {
    const grid = document.getElementById('wiki-agents-grid');
    if (!grid) return;

    try {
        const resp = await fetch('/api/intelligence/status', { headers: { 'X-API-KEY': window.VAULT_KEY } });
        if (resp.ok) {
            const data = await resp.json();
            // Data is from get_orchestra_report()
            // Let's assume it has an 'agents' or similar structure
            const agentsRaw = data.agents || data.swarm || [];
            
            // Map raw data or use fallback if empty
            const agents = agentsRaw.length > 0 ? agentsRaw.map(a => ({
                name: a.name || a.id,
                role: a.role || 'Personnel',
                status: a.status || 'Active',
                desc: a.task || 'System-wide coordination.',
                cpu: a.cpu_usage || '0',
                mem: a.memory_usage || '0'
            })) : [
                { name: 'Skywalker', role: 'Forager', status: 'Active', desc: 'Expert in multi-engine web retrieval.', cpu: '12', mem: '45' },
                { name: 'Yoda', role: 'Judge', status: 'Active', desc: 'Evolved wisdom and consensus builder.', cpu: '8', mem: '32' },
                { name: 'Paperboy', role: 'Broadcaster', status: 'Active', desc: 'Real-time telemetry dissemination.', cpu: '5', mem: '20' }
            ];

            grid.innerHTML = agents.map(a => `
                <div class="wiki-widget-card" onclick="window.switchWikiView('agent-profile', '${a.name}')" style="cursor: pointer; transition: 0.3s; hover: border-color: #3b82f6;">
                    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 1rem;">
                        <img src="https://ui-avatars.com/api/?name=${a.name}&background=${a.status==='Active'?'10b981':'64748b'}&color=fff" style="width: 40px; height: 40px; border-radius: 50%;">
                        <div>
                            <div style="font-size: 0.8rem; color: white; font-weight: 800;">${a.name}</div>
                            <div style="font-size: 0.55rem; color: #10b981; font-weight: 800;">${a.status.toUpperCase()}</div>
                        </div>
                    </div>
                    <div style="font-size: 0.6rem; color: #64748b; text-transform: uppercase; margin-bottom: 5px;">Role: ${a.role}</div>
                    <div style="font-size: 0.7rem; color: #94a3b8; line-height: 1.4;">${a.desc}</div>
                    <div style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid rgba(255,255,255,0.05); display: flex; justify-content: space-between;">
                        <span style="font-size: 0.6rem; color: #3b82f6;"><i class="fas fa-microchip"></i> ${a.cpu}% CPU</span>
                        <span style="font-size: 0.6rem; color: #a855f7;"><i class="fas fa-memory"></i> ${a.mem}MB</span>
                    </div>
                </div>
            `).join('');
        }
    } catch (e) {
        console.error("❌ Failed to fetch agents grid:", e);
    }
};

window.initWikiSettings = () => {
    // Populate model selects if not already done
    if (typeof window.populateModelSelectors === 'function') {
        window.populateModelSelectors();
    }
    
    // Load checkboxes from localStorage
    const z3 = document.getElementById('wiki-setting-z3');
    const ds = document.getElementById('wiki-setting-deepsearch');
    if (z3) z3.checked = localStorage.getItem('wiki_z3') === 'true';
    if (ds) ds.checked = localStorage.getItem('wiki_deepsearch') === 'true';

    // Set some defaults
    const chief = document.getElementById('wiki-settings-chief-model');
    if (chief && chief.options.length > 0) {
        chief.selectedIndex = 0;
    }
};

window.initWikiActivityFeed = async () => {
    const list = document.getElementById('wiki-activity-list');
    if (!list) return;

    try {
        const resp = await fetch('/api/wiki/activity', { headers: { 'X-API-KEY': window.VAULT_KEY } });
        if (resp.ok) {
            const logs = await resp.json();
            if (logs.length === 0) {
                list.innerHTML = '<div style="color: #64748b;">No recent activity recorded in the ledger.</div>';
                return;
            }
            list.innerHTML = logs.map(l => `
                <div style="margin-bottom: 1rem; border-bottom: 1px solid rgba(255,255,255,0.02); padding-bottom: 10px;">
                    <div style="display: flex; justify-content: space-between;">
                        <span style="color: #64748b; font-size: 0.6rem;">[${l.timestamp}]</span>
                        <span style="color: #a855f7; font-size: 0.55rem; font-weight: 800;">${l.agent}</span>
                    </div>
                    <div style="color: #e2e8f0; font-size: 0.75rem; margin-top: 5px;">
                        <b style="color: #3b82f6;">${l.action}:</b> ${l.reasoning || l.target || ''}
                    </div>
                    <div style="color: #475569; font-size: 0.55rem; margin-top: 3px;">TARGET: ${l.target_id || 'Global'}</div>
                </div>
            `).join('');
        }
    } catch (e) {
        console.error("❌ Error fetching activity feed:", e);
    }
};

window.saveSwarmSettings = () => {
    console.log("💾 Saving Swarm Settings...");
    const chief = document.getElementById('wiki-settings-chief-model')?.value;
    const audit = document.getElementById('wiki-settings-audit-model')?.value;
    
    // Save checkboxes
    const z3 = document.getElementById('wiki-setting-z3')?.checked;
    const ds = document.getElementById('wiki-setting-deepsearch')?.checked;
    localStorage.setItem('wiki_z3', z3);
    localStorage.setItem('wiki_deepsearch', ds);

    // Visual feedback
    const btn = event.target;
    const oldText = btn.innerText;
    btn.innerText = "CONFIG SAVED!";
    btn.style.background = "#10b981";
    
    setTimeout(() => {
        btn.innerText = oldText;
        btn.style.background = "#3b82f6";
    }, 2000);
    
    if (window.showSovereignNotification) {
        window.showSovereignNotification("Nexus Settings Persisted.", "SUCCESS");
    }
};

window.handleWikiSearch = () => {
    const q = document.getElementById('wiki-global-search')?.value.toLowerCase();
    if (!q) return;

    // Search in KB List if we are there
    if (document.getElementById('wiki-subview-kb-list').style.display === 'block') {
        window.filterKBList(q);
    }
    
    // Logic for global overlay search could go here
    console.log("🔍 Wiki Global Search:", q);
};

window.submitWikiQuery = async () => {
    const q = document.getElementById('wiki-global-search')?.value;
    if (!q) return;

    console.log("🚀 Submitting Wiki Query:", q);
    
    // Feedback visivo immediato
    if (window.showSovereignNotification) {
        window.showSovereignNotification(`UPLINKING QUERY: ${q}`, "INFO");
    }

    // Passiamo alla vista Knowledge Page e carichiamo il topic
    // Questo attiverà automaticamente Skywalker se il topic non esiste nel vault
    window.loadWikiPage(q, 'TECHNICAL');
};

window.initWikiKBList = async () => {
    try {
        const resp = await fetch('/api/wiki/list', { headers: { 'X-API-KEY': window.VAULT_KEY } });
        if (resp.ok) {
            const data = await resp.json();
            window.fullKBTreeList = data.pages || []; // Save original objects for filtering
            window.renderKBTree(window.fullKBTreeList);
        }
    } catch (e) {
        console.error("❌ Failed to fetch KB list:", e);
    }
};

window.renderKBTree = (pages) => {
    const container = document.getElementById('wiki-kb-tree-container');
    if (!container) return;

    if (!pages || pages.length === 0) {
        container.innerHTML = '<div style="color: #64748b; padding: 1rem; text-align: center;">Nessun documento nel Vault.</div>';
        return;
    }

    // Group by Namespace
    const groups = {};
    pages.forEach(p => {
        const ns = p.namespace || "General";
        if (!groups[ns]) groups[ns] = [];
        groups[ns].push(p);
    });

    let html = '';
    // Sort namespaces alphabetically
    const sortedNamespaces = Object.keys(groups).sort();

    sortedNamespaces.forEach(ns => {
        // Create Folder Item
        html += `
            <div class="kb-tree-folder" style="margin-bottom: 2px;">
                <div onclick="this.nextElementSibling.style.display = this.nextElementSibling.style.display === 'none' ? 'block' : 'none'; const icon = this.querySelector('i:last-child'); if(icon.classList.contains('fa-chevron-right')){icon.classList.replace('fa-chevron-right','fa-chevron-down');}else{icon.classList.replace('fa-chevron-down','fa-chevron-right');}" 
                     style="display: flex; justify-content: space-between; align-items: center; padding: 6px 10px; cursor: pointer; border-radius: 6px; color: #a855f7; background: rgba(168, 85, 247, 0.05); transition: background 0.2s;"
                     onmouseover="this.style.background='rgba(168, 85, 247, 0.15)'" onmouseout="this.style.background='rgba(168, 85, 247, 0.05)'">
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <i class="fas fa-folder-open"></i>
                        <span style="font-weight: 800;">${ns}</span>
                    </div>
                    <i class="fas fa-chevron-down" style="font-size: 0.55rem; opacity: 0.7;"></i>
                </div>
                <div class="kb-tree-folder-contents" style="padding-left: 12px; margin-top: 2px; display: block;">
        `;
        
        // Sort files alphabetically within namespace
        groups[ns].sort((a, b) => a.title.localeCompare(b.title)).forEach(p => {
            const isActive = (window.currentWikiPage === p.file_name) ? 'background: rgba(59,130,246,0.15); color: #fff; border-left: 2px solid #3b82f6;' : 'color: #94a3b8; border-left: 2px solid transparent;';
            html += `
                <div onclick="window.loadWikiPage('${p.title}', 'TECHNICAL', '${p.file_name}')"
                     style="padding: 5px 8px 5px 12px; display: flex; align-items: center; gap: 8px; cursor: pointer; border-radius: 4px; transition: all 0.2s; ${isActive}"
                     onmouseover="if(!this.style.borderLeft.includes('#3b82f6')) { this.style.background='rgba(255,255,255,0.05)'; this.style.color='#fff'; }"
                     onmouseout="if(!this.style.borderLeft.includes('#3b82f6')) { this.style.background='transparent'; this.style.color='#94a3b8'; }">
                    <i class="fas fa-file-alt" style="color: #3b82f6; font-size: 0.6rem; opacity: 0.8;"></i>
                    <span style="white-space: nowrap; overflow: hidden; text-overflow: ellipsis; font-size: 0.65rem;">${p.title}</span>
                </div>
            `;
        });
        
        html += `
                </div>
            </div>
        `;
    });

    container.innerHTML = html;
};

window.filterKBTree = () => {
    const q = document.getElementById('kb-tree-filter')?.value.toLowerCase();
    if (!window.fullKBTreeList) return;
    
    if (!q) {
        window.renderKBTree(window.fullKBTreeList);
        return;
    }
    
    const filtered = window.fullKBTreeList.filter(p => p.title.toLowerCase().includes(q) || (p.namespace && p.namespace.toLowerCase().includes(q)));
    window.renderKBTree(filtered);
};

window.initWikiGalaxies = async () => {
    const list = document.getElementById('wiki-galaxies-list');
    if (!list) return;

    try {
        const resp = await fetch('/api/lab/wisdom/all', { headers: { 'X-API-KEY': window.VAULT_KEY } });
        if (resp.ok) {
            const galaxies = await resp.json();
            list.innerHTML = Object.entries(galaxies).map(([id, g]) => `
                <div class="wiki-widget-card" style="padding: 10px; margin-bottom: 5px; cursor: pointer; border-left: 2px solid #a855f7;">
                    <div style="font-size: 0.75rem; color: white; font-weight: 800;">${g.title || id}</div>
                    <div style="font-size: 0.55rem; color: #64748b;">Nodes: ${g.node_count || 0} | Insight: ${g.wisdom_score || 'N/A'}</div>
                </div>
            `).join('');
        }
    } catch (e) {
        console.error("❌ Failed to fetch galaxies:", e);
    }
};

window.initWikiForensic = async () => {
    const list = document.getElementById('forensic-contradictions-list');
    const scoreVal = document.getElementById('integrity-score-value');
    const totalClaims = document.getElementById('forensic-total-claims');
    const totalAnomalies = document.getElementById('forensic-total-anomalies');
    
    if (!list) return;

    list.innerHTML = '<div style="color: #64748b; padding: 2rem; text-align: center;"><i class="fas fa-microscope fa-spin" style="font-size: 2rem; margin-bottom: 1rem;"></i><br>SCANNING CROSS-WIKI CONTRADICTIONS...</div>';

    try {
        const resp = await fetch('/api/wiki/forensic', { headers: { 'X-API-KEY': window.VAULT_KEY } });
        if (resp.ok) {
            const data = await resp.json();
            
            // Update Stats
            if (scoreVal) scoreVal.innerText = `${data.integrity_score}%`;
            if (scoreVal) scoreVal.style.color = data.integrity_score > 80 ? '#10b981' : (data.integrity_score > 50 ? '#facc15' : '#ef4444');
            if (totalClaims) totalClaims.innerText = data.total_claims;
            if (totalAnomalies) totalAnomalies.innerText = data.contradictions_found;

            if (data.contradictions.length === 0) {
                list.innerHTML = `
                    <div style="background: rgba(16, 185, 129, 0.05); border: 1px solid rgba(16, 185, 129, 0.2); padding: 2rem; border-radius: 12px; text-align: center;">
                        <i class="fas fa-shield-check" style="font-size: 3rem; color: #10b981; margin-bottom: 1rem;"></i>
                        <h3 style="color: white;">KNOWLEDGE INTEGRITY VERIFIED</h3>
                        <p style="color: #64748b; font-size: 0.7rem;">No contradictions found across ${data.total_claims} assertions.</p>
                    </div>
                `;
                return;
            }

            list.innerHTML = data.contradictions.map(c => `
                <div class="wiki-widget-card" style="border-left: 4px solid #ef4444; background: rgba(239, 68, 68, 0.02);">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                        <span style="font-size: 0.55rem; color: #ef4444; font-weight: 900; letter-spacing: 1px; text-transform: uppercase;">TOPIC: ${c.topic}</span>
                        <span style="background: rgba(239, 68, 68, 0.2); color: #ef4444; font-size: 0.5rem; padding: 2px 8px; border-radius: 4px; font-weight: 900;">CONTRADICTION</span>
                    </div>
                    
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem;">
                        <div style="background: rgba(0,0,0,0.3); padding: 10px; border-radius: 8px;">
                            <div style="font-size: 0.6rem; color: #3b82f6; font-weight: 800; margin-bottom: 5px;">WIKI: ${c.wiki_a}</div>
                            <div style="color: #e2e8f0; font-size: 0.75rem;">"${c.claim_a}"</div>
                        </div>
                        <div style="background: rgba(0,0,0,0.3); padding: 10px; border-radius: 8px;">
                            <div style="font-size: 0.6rem; color: #a855f7; font-weight: 800; margin-bottom: 5px;">WIKI: ${c.wiki_b}</div>
                            <div style="color: #e2e8f0; font-size: 0.75rem;">"${c.claim_b}"</div>
                        </div>
                    </div>
                    
                    <div style="margin-top: 1rem; display: flex; gap: 10px;">
                        <button onclick="window.loadWikiPage('${c.wiki_a.replace('.md','')}')" style="background: transparent; border: 1px solid rgba(255,255,255,0.1); color: #94a3b8; font-size: 0.55rem; padding: 5px 10px; border-radius: 5px; cursor: pointer;">INSPECT A</button>
                        <button onclick="window.loadWikiPage('${c.wiki_b.replace('.md','')}')" style="background: transparent; border: 1px solid rgba(255,255,255,0.1); color: #94a3b8; font-size: 0.55rem; padding: 5px 10px; border-radius: 5px; cursor: pointer;">INSPECT B</button>
                    </div>
                </div>
            `).join('');

        }
    } catch (e) {
        console.error("❌ Forensic Audit Failed:", e);
        list.innerHTML = `<div style="color: #ef4444;">Error during forensic scan: ${e.message}</div>`;
    }
};

setTimeout(window.initWikiNexus, 500);
setTimeout(() => { if (document.getElementById('wiki-subview-dashboard')) window.initWikiDashboardCharts(); }, 1000);

// ============================================================================
// 🧠 [v11.0] PURE WIKI ENGINE - TRIPLE-PANE IDE & INFRANODUS GRAPH SYSTEM
// ============================================================================
window.pureWikiState = {
    tree: [],
    activeFilePath: ['wiki', 'concepts', 'balance-of-payments.md'],
    activeContent: '',
    activeTab: 'preview',
    collapsedFolders: {},
    draggedNodeId: null
};

// Default Prepopulated State exactly matching the premium IDE design
const PURE_WIKI_DEFAULT_DATA = [
    {
        id: 'f-finance',
        name: 'FINANCE',
        type: 'folder',
        children: [
            {
                id: 'f-strategies',
                name: 'strategies',
                type: 'folder',
                children: [
                    {
                        id: 'p-macro-hedge',
                        name: 'macro-hedge.md',
                        type: 'file',
                        content: '# Macro Hedge Strategy\n\nAnalisi di hedging macroeconomico basata sui flussi BOP e differenziali dei tassi di interesse globali.',
                        unsaved: false
                    }
                ]
            },
            {
                id: 'f-portfolio',
                name: 'portfolio',
                type: 'folder',
                children: [
                    {
                        id: 'p-risk-parity',
                        name: 'risk-parity.md',
                        type: 'file',
                        content: '# Risk Parity Portfolio\n\nAllocazione dinamica basata sulla volatilità implicita degli asset finanziari principali.',
                        unsaved: false
                    }
                ]
            }
        ]
    },
    {
        id: 'f-wiki',
        name: 'wiki',
        type: 'folder',
        children: [
            {
                id: 'f-concepts',
                name: 'concepts',
                type: 'folder',
                children: [
                    {
                        id: 'p-balance-of-payments',
                        name: 'balance-of-payments.md',
                        type: 'file',
                        content: 'where &pi; = asset price inflation (proxied by stock indices) and i = investment income (proxied by bond yields).\n\nThe key insight: currency supply/demand on FOREX is determined by BOP flows. A country with net capital inflows (financial account surplus) sees currency appreciation, while one with current account deficits sees pressure for depreciation - but these forces interact.\n\n## Practical Application\n\n- **FX forecasting**: BOP flows are the fundamental driver of exchange rate movements.\n- **Macro analysis**: Current account deficits signal structural vulnerabilities.\n- **Investment flows**: Financial account data reveals where global capital is flowing.\n\n## Interpretation\n\nFor developed countries, current transfers and capital account (non-financial) are small enough to neglect. The dominant forces are:\n- Trade balance (exports vs imports)\n- Investment income on cross-border assets (driven by interest rate differentials)\n- Portfolio and direct investment flows (capital account)',
                        unsaved: false
                    },
                    {
                        id: 'p-bond-index',
                        name: 'bond-index.md',
                        type: 'file',
                        content: '# Bond Index Analysis\n\nMetriche sui rendimenti dei titoli di stato a lungo termine e relative correlazioni azionarie.',
                        unsaved: false
                    },
                    {
                        id: 'p-ema',
                        name: 'ema.md',
                        type: 'file',
                        content: '# Exponential Moving Average (EMA)\n\nStudio delle medie esponenziali mobili applicate all\'analisi tecnica delle materie prime.',
                        unsaved: false
                    },
                    {
                        id: 'p-economic-cycles',
                        name: 'economic-cycles.md',
                        type: 'file',
                        content: '# Economic Cycles & Growth\n\nCorrelazione tra cicli di debito a breve termine e politiche monetarie espansive.',
                        unsaved: false
                    },
                    {
                        id: 'p-equity-premium',
                        name: 'equity-premium.md',
                        type: 'file',
                        content: '# Equity Risk Premium\n\nIl differenziale teorico atteso tra il rendimento del mercato azionario e i titoli privi di rischio.',
                        unsaved: false
                    }
                ]
            }
        ]
    }
];

// Initialize Pure Wiki Engine
window.initPureWiki = async () => {
    console.log("🚀 [v11.0] Booting Pure Wiki Engine from real workspace...");
    
    try {
        const resp = await fetch('/api/wiki/list', { headers: { 'X-API-KEY': window.VAULT_KEY } });
        if (resp.ok) {
            const data = await resp.json();
            const pages = data.pages || [];
            
            // Build tree from real database namespaces
            const tree = [];
            const namespaceFolders = {};
            
            pages.forEach(p => {
                const ns = p.namespace || "General";
                const folderName = ns.toUpperCase();
                if (!namespaceFolders[folderName]) {
                    namespaceFolders[folderName] = {
                        id: 'f-' + ns.toLowerCase(),
                        name: folderName,
                        type: 'folder',
                        children: []
                    };
                    tree.push(namespaceFolders[folderName]);
                }
                
                namespaceFolders[folderName].children.push({
                    id: 'p-' + p.file_name.replace(/[\/\.]/g, '-'),
                    name: p.file_name.split('/').pop(),
                    type: 'file',
                    content: '', // Will fetch dynamically on demand
                    unsaved: false,
                    filePath: p.file_name // Exact backend path for on-demand fetch
                });
            });
            
            // If tree is empty, ensure at least General folder with empty or default index exists
            if (tree.length === 0) {
                tree.push({
                    id: 'f-general',
                    name: 'GENERAL',
                    type: 'folder',
                    children: [{
                        id: 'p-index-md',
                        name: 'index.md',
                        type: 'file',
                        content: '# Welcome to the sovereign Knowledge Nexus\n\nNo pages currently loaded.',
                        unsaved: false,
                        filePath: 'General/index.md'
                    }]
                });
            }
            
            window.pureWikiState.tree = tree;
            localStorage.setItem('pure_wiki_tree_v1', JSON.stringify(tree));
        } else {
            throw new Error("API responded with error");
        }
    } catch (e) {
        console.error("⚠️ Failed to load real Wiki pages into explorer tree, falling back to defaults:", e);
        const savedData = localStorage.getItem('pure_wiki_tree_v1');
        if (savedData) {
            try {
                window.pureWikiState.tree = JSON.parse(savedData);
            } catch (err) {
                window.pureWikiState.tree = JSON.parse(JSON.stringify(PURE_WIKI_DEFAULT_DATA));
            }
        } else {
            window.pureWikiState.tree = JSON.parse(JSON.stringify(PURE_WIKI_DEFAULT_DATA));
            localStorage.setItem('pure_wiki_tree_v1', JSON.stringify(window.pureWikiState.tree));
        }
    }

    // Set first file as active if current path is default and not present
    let defaultFirstPath = null;
    if (window.pureWikiState.tree.length > 0) {
        const firstFolder = window.pureWikiState.tree[0];
        if (firstFolder.children && firstFolder.children.length > 0) {
            defaultFirstPath = [firstFolder.name, firstFolder.children[0].name];
        }
    }
    
    // If activeFilePath matches the mock balance-of-payments.md or is empty, select the real default first path
    if (window.pureWikiState.activeFilePath.join('/') === 'wiki/concepts/balance-of-payments.md' || window.pureWikiState.activeFilePath.length === 0) {
        if (defaultFirstPath) {
            window.pureWikiState.activeFilePath = defaultFirstPath;
        }
    }

    // Force load the active file
    await window.pureWikiLoadFileByPath(window.pureWikiState.activeFilePath);
    
    // Initial Render Tree
    window.pureWikiRenderTree();
    
    // Init Visual Graph
    window.pureWikiInitGraph();
};

// Tree Helper: Find a node recursively by ID
window.pureWikiFindNodeById = (tree, id) => {
    for (let node of tree) {
        if (node.id === id) return node;
        if (node.type === 'folder' && node.children) {
            const found = window.pureWikiFindNodeById(node.children, id);
            if (found) return found;
        }
    }
    return null;
};

// Tree Helper: Find parent of a node recursively
window.pureWikiFindParentOfNode = (tree, id, parent = null) => {
    for (let node of tree) {
        if (node.id === id) return parent;
        if (node.type === 'folder' && node.children) {
            const found = window.pureWikiFindParentOfNode(node.children, id, node);
            if (found) return found;
        }
    }
    return null;
};

// Load content of a file given its path
window.pureWikiLoadFileByPath = async (pathParts) => {
    if (!pathParts || pathParts.length === 0) return;
    
    const fileName = pathParts[pathParts.length - 1];
    let current = null;
    
    // 1. Recursive search by file name (ultra resilient)
    const findFileNode = (nodes) => {
        for (let n of nodes) {
            if (n.type === 'file' && n.name.toLowerCase() === fileName.toLowerCase()) {
                return n;
            }
            if (n.type === 'folder' && n.children) {
                const found = findFileNode(n.children);
                if (found) return found;
            }
        }
        return null;
    };
    
    current = findFileNode(window.pureWikiState.tree);
    
    if (!current) {
        // 2. Strict path match fallback
        const resolved = window.pureWikiFindNodeByPath(pathParts);
        if (resolved && resolved.type === 'file') {
            current = resolved;
        }
    }
    
    if (current && current.type === 'file') {
        window.pureWikiState.activeFilePath = pathParts;
        
        // Dynamically fetch from backend on-demand if content is empty
        if (!current.content) {
            try {
                const relativePath = current.filePath || pathParts.join('/');
                const resp = await fetch(`/api/wiki/read?file=${encodeURIComponent(relativePath)}&mode=TECHNICAL`, { 
                    headers: { 'X-API-KEY': window.VAULT_KEY } 
                });
                if (resp.ok) {
                    const data = await resp.json();
                    current.content = data.markdown || '';
                } else {
                    current.content = `# ${current.name.replace('.md', '')}\n\nCould not fetch content from backend.`;
                }
            } catch (e) {
                console.error("❌ Failed to fetch page content from backend:", e);
                current.content = `# ${current.name.replace('.md', '')}\n\nError connecting to backend.`;
            }
        }
        
        window.pureWikiState.activeContent = current.content;
        
        // Update Editor Breadcrumbs
        const breadcrumbs = document.getElementById('pure-wiki-breadcrumbs');
        if (breadcrumbs) {
            breadcrumbs.innerText = pathParts.join(' > ');
        }
        
        // Update Tab & Editor Content
        const editorTextarea = document.getElementById('pure-wiki-markdown-editor');
        if (editorTextarea) {
            editorTextarea.value = current.content;
        }
        
        // Render Preview
        window.pureWikiRenderPreview();
        
        // Update save status badge
        window.pureWikiUpdateSaveStatus(current.unsaved);
        
        // Re-render the tree to synchronize the active highlight in the sidebar explorer!
        window.pureWikiRenderTree();
    }
};

// Switch Editor Tab (Preview vs Markdown)
window.pureWikiSetTab = (tabId) => {
    window.pureWikiState.activeTab = tabId;
    
    const previewBtn = document.getElementById('pure-wiki-tab-preview');
    const markdownBtn = document.getElementById('pure-wiki-tab-markdown');
    const previewPanel = document.getElementById('pure-wiki-preview-panel');
    const markdownEditor = document.getElementById('pure-wiki-markdown-editor');
    
    if (tabId === 'preview') {
        if (previewBtn) previewBtn.classList.add('active');
        if (previewBtn) previewBtn.style.background = 'rgba(255,255,255,0.08)';
        if (previewBtn) previewBtn.style.color = '#fff';
        if (markdownBtn) markdownBtn.classList.remove('active');
        if (markdownBtn) markdownBtn.style.background = 'transparent';
        if (markdownBtn) markdownBtn.style.color = '#64748b';
        
        if (previewPanel) previewPanel.style.display = 'block';
        if (markdownEditor) markdownEditor.style.display = 'none';
        
        // Sync editor value back to state before previewing
        if (markdownEditor) {
            window.pureWikiState.activeContent = markdownEditor.value;
        }
        window.pureWikiRenderPreview();
    } else {
        if (markdownBtn) markdownBtn.classList.add('active');
        if (markdownBtn) markdownBtn.style.background = 'rgba(255,255,255,0.08)';
        if (markdownBtn) markdownBtn.style.color = '#fff';
        if (previewBtn) previewBtn.classList.remove('active');
        if (previewBtn) previewBtn.style.background = 'transparent';
        if (previewBtn) previewBtn.style.color = '#64748b';
        
        if (previewPanel) previewPanel.style.display = 'none';
        if (markdownEditor) markdownEditor.style.display = 'block';
    }
};

// Simple Cyber-styled Markdown to HTML parser
window.pureWikiMarkdownToHtml = (markdown) => {
    if (!markdown) return '<div style="opacity: 0.5; font-style: italic;">Nessun contenuto.</div>';
    
    let html = markdown
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;");
        
    // Headers
    html = html.replace(/^### (.*$)/gim, '<h3 style="color: #60a5fa; font-weight: 800; margin-top: 1.2rem; margin-bottom: 0.6rem; letter-spacing: -0.2px;">$1</h3>');
    html = html.replace(/^## (.*$)/gim, '<h2 style="color: #a855f7; font-weight: 900; margin-top: 1.5rem; margin-bottom: 0.8rem; border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom: 5px; letter-spacing: -0.5px;">$1</h2>');
    html = html.replace(/^# (.*$)/gim, '<h1 style="color: #fff; font-weight: 900; margin-top: 2rem; margin-bottom: 1rem; font-size: 1.4rem; letter-spacing: -1px;">$1</h1>');
    
    // Bold / Strong
    html = html.replace(/\*\*(.*?)\*\*/g, '<strong style="color:#fff; font-weight:700;">$1</strong>');
    
    // Inline code
    html = html.replace(/`(.*?)`/g, '<code style="background: rgba(0,0,0,0.3); border:1px solid rgba(255,255,255,0.08); padding: 2px 6px; border-radius: 4px; font-family: \'JetBrains Mono\'; font-size: 0.7rem; color: #f472b6;">$1</code>');
    
    // Unordered lists
    html = html.replace(/^\- (.*$)/gim, '<li style="margin-left: 1.2rem; list-style-type: square; margin-bottom: 6px; color: #cbd5e1;">$1</li>');
    
    // Paragraph breaks
    html = html.split('\n\n').map(p => {
        if (p.trim().startsWith('<h') || p.trim().startsWith('<li')) return p;
        return `<p style="margin-bottom: 1rem; color: #cbd5e1; line-height: 1.7;">${p}</p>`;
    }).join('\n');
    
    return html;
};

// Render Middle Preview Panel
window.pureWikiRenderPreview = () => {
    const previewPanel = document.getElementById('pure-wiki-preview-panel');
    if (previewPanel) {
        previewPanel.innerHTML = window.pureWikiMarkdownToHtml(window.pureWikiState.activeContent);
    }
};

// Track local edits and mark page as unsaved
window.pureWikiHandleContentChange = () => {
    const editorTextarea = document.getElementById('pure-wiki-markdown-editor');
    if (editorTextarea) {
        window.pureWikiState.activeContent = editorTextarea.value;
        
        // Find current node and set unsaved
        const activeFileNode = window.pureWikiFindNodeByPath(window.pureWikiState.activeFilePath);
        if (activeFileNode) {
            activeFileNode.content = editorTextarea.value;
            if (!activeFileNode.unsaved) {
                activeFileNode.unsaved = true;
                window.pureWikiUpdateSaveStatus(true);
                window.pureWikiRenderTree(); // Refresh UI to show badge
            }
        }
    }
};

// Save current active page
window.pureWikiSaveActivePage = () => {
    const activeFileNode = window.pureWikiFindNodeByPath(window.pureWikiState.activeFilePath);
    if (activeFileNode) {
        activeFileNode.content = window.pureWikiState.activeContent;
        activeFileNode.unsaved = false;
        
        // Persist tree to local storage
        localStorage.setItem('pure_wiki_tree_v1', JSON.stringify(window.pureWikiState.tree));
        
        window.pureWikiUpdateSaveStatus(false);
        window.pureWikiRenderTree();
        
        // Custom cyber toast
        window.pureWikiShowToast("Pagina salvata e cifrata con successo!", "SUCCESS");
    }
};

// Update status bar saved/unsaved badge
window.pureWikiUpdateSaveStatus = (unsaved) => {
    const statusLabel = document.getElementById('pure-wiki-save-status');
    if (statusLabel) {
        if (unsaved) {
            statusLabel.innerHTML = `<span style="color: #fbbf24;"><i class="fas fa-exclamation-circle"></i> Modificato (Non Salvato)</span>`;
        } else {
            statusLabel.innerHTML = `<span style="color: #10b981;"><i class="fas fa-check-circle"></i> Salvato in locale</span>`;
        }
    }
};

// Helper: Find node by hierarchical string path array
window.pureWikiFindNodeByPath = (pathParts) => {
    // Translate legacy/mock paths to real namespace folders if they don't exist
    let adjustedParts = [...pathParts];
    if (adjustedParts[0] === 'wiki' && adjustedParts[1] === 'concepts') {
        const hasGeneral = window.pureWikiState.tree.find(c => c.name.toLowerCase() === 'general');
        if (hasGeneral) {
            adjustedParts = [hasGeneral.name];
        }
    }
    
    let current = { children: window.pureWikiState.tree };
    for (let part of adjustedParts) {
        if (!current.children) return null;
        const found = current.children.find(c => c.name.toLowerCase() === part.toLowerCase());
        if (!found) return null;
        current = found;
    }
    return current;
};

// ============================================================================
// 📁 RENDER RECURSIVE TREE EXPLORER (Drag & Drop + Order Control)
// ============================================================================
window.pureWikiNodeClick = (el) => {
    const isFolder = el.getAttribute('data-is-folder') === 'true';
    const id = el.getAttribute('data-id');
    if (isFolder) {
        window.pureWikiToggleFolder(id);
    } else {
        const path = JSON.parse(el.getAttribute('data-path'));
        window.pureWikiLoadFileByPath(path);
    }
};

window.pureWikiRenderTree = () => {
    const container = document.getElementById('pure-wiki-tree-container');
    if (!container) return;
    
    container.innerHTML = '';
    
    // Recursive Tree Builder
    const buildHtml = (nodes, currentPath = []) => {
        let html = '<div class="tree-list" style="display:flex; flex-direction:column; gap:4px; padding-left: 10px;">';
        
        nodes.forEach((node, index) => {
            const nodePath = [...currentPath, node.name];
            const nodePathStr = nodePath.join('/');
            const isActive = window.pureWikiState.activeFilePath.join('/') === nodePathStr;
            const isFolder = node.type === 'folder';
            const isCollapsed = window.pureWikiState.collapsedFolders[node.id] || false;
            
            // Drag-and-drop & sorting handlers
            html += `
                <div class="tree-node" 
                     draggable="true"
                     ondragstart="window.pureWikiDragStart(event, '${node.id}')"
                     ondragover="window.pureWikiDragOver(event)"
                     ondrop="window.pureWikiDrop(event, '${node.id}')"
                     data-id="${node.id}"
                     data-is-folder="${isFolder}"
                     data-path='${JSON.stringify(nodePath)}'
                     style="display: flex; align-items: center; justify-content: space-between; padding: 6px 8px; border-radius: 6px; cursor: pointer; transition: 0.2s; background: ${isActive ? 'rgba(59,130,246,0.1)' : 'transparent'}; border-left: 2px solid ${isActive ? '#3b82f6' : 'transparent'};"
                     onclick="event.stopPropagation(); window.pureWikiNodeClick(this)">
                    
                    <!-- Left Section: Toggle icon + node title -->
                    <div style="display: flex; align-items: center; gap: 8px; min-width: 0; flex: 1;">
                        ${isFolder ? `
                            <i class="fas ${isCollapsed ? 'fa-chevron-right' : 'fa-chevron-down'}" style="font-size: 0.6rem; color: #64748b;"></i>
                            <i class="fas ${isCollapsed ? 'fa-folder' : 'fa-folder-open'}" style="font-size: 0.75rem; color: #f59e0b;"></i>
                        ` : `
                            <i class="fas fa-file-lines" style="font-size: 0.75rem; color: #60a5fa;"></i>
                        `}
                        <span style="font-size: 0.75rem; color: ${isActive ? '#fff' : '#cbd5e1'}; font-weight: ${isActive ? '800' : 'normal'}; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; font-family: 'Outfit';">
                            ${node.name}
                        </span>
                        ${node.unsaved ? `<span style="font-size: 0.55rem; background: #b45309; color: #fff; padding: 1px 4px; border-radius: 4px; font-weight: bold; font-family: 'JetBrains Mono';">U</span>` : ''}
                    </div>
                    
                    <!-- Right Section: Subtle Hover controls for sorting, child additions, deletions -->
                    <div class="tree-controls" onclick="event.stopPropagation()" style="display: flex; gap: 6px; opacity: 0.7; transition: 0.2s;">
                        <button onclick="window.pureWikiMoveIndex('${node.id}', 'up')" title="Sposta Su" style="background: transparent; border: none; color: #64748b; cursor: pointer; font-size: 0.55rem; padding: 2px;"><i class="fas fa-chevron-up"></i></button>
                        <button onclick="window.pureWikiMoveIndex('${node.id}', 'down')" title="Sposta Giù" style="background: transparent; border: none; color: #64748b; cursor: pointer; font-size: 0.55rem; padding: 2px;"><i class="fas fa-chevron-down"></i></button>
                        ${isFolder ? `
                            <button onclick="window.pureWikiCreateChildNode('${node.id}')" title="Aggiungi sotto-pagina" style="background: transparent; border: none; color: #10b981; cursor: pointer; font-size: 0.6rem; padding: 2px;"><i class="fas fa-plus"></i></button>
                        ` : ''}
                        <button onclick="window.pureWikiDeleteNode('${node.id}')" title="Elimina" style="background: transparent; border: none; color: #ef4444; cursor: pointer; font-size: 0.6rem; padding: 2px;"><i class="fas fa-trash-can"></i></button>
                    </div>
                </div>
            `;
            
            // Nested Children rendering
            if (isFolder && !isCollapsed && node.children && node.children.length > 0) {
                html += buildHtml(node.children, nodePath);
            }
        });
        
        html += '</div>';
        return html;
    };
    
    container.innerHTML = buildHtml(window.pureWikiState.tree);
};

// Collapse/Expand Folders
window.pureWikiToggleFolder = (folderId) => {
    window.pureWikiState.collapsedFolders[folderId] = !window.pureWikiState.collapsedFolders[folderId];
    window.pureWikiRenderTree();
};

// ============================================================================
// 🗺️ DIRECTORY EXPLORER INDEX CREATION & MANAGEMENT CONTROLS
// ============================================================================

// Custom Dialog Box helper (Futuristic overlay prompt instead of plain browser prompt)
window.pureWikiPrompt = (title, placeholder, callback) => {
    // Remove existing if any
    const existing = document.getElementById('pure-wiki-prompt-modal');
    if (existing) existing.remove();
    
    const modalHtml = `
        <div id="pure-wiki-prompt-modal" style="position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background: rgba(2,6,23,0.8); backdrop-filter: blur(15px); z-index: 99999; display: flex; align-items: center; justify-content: center; opacity: 1; transition: 0.3s; font-family: 'Outfit';">
            <div class="glass-card" style="width: 400px; padding: 25px; border: 1px solid rgba(59,130,246,0.3); border-radius: 16px; text-align: left; box-shadow: 0 30px 60px rgba(0,0,0,0.6); position: relative;">
                <h3 style="color: white; font-weight: 800; margin-bottom: 0.5rem; letter-spacing: -0.5px; font-size: 1rem;"><i class="fas fa-terminal" style="color:#3b82f6; margin-right:8px;"></i> ${title.toUpperCase()}</h3>
                <div style="background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.05); padding: 10px; border-radius: 8px; margin-bottom: 1rem;">
                    <input type="text" id="pure-wiki-prompt-input" placeholder="${placeholder}" style="width: 100%; background: transparent; border: none; color: white; outline: none; font-size: 0.8rem; font-family: 'JetBrains Mono';">
                </div>
                <div style="display: flex; justify-content: flex-end; gap: 10px;">
                    <button onclick="document.getElementById('pure-wiki-prompt-modal').remove()" style="background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.08); color: #94a3b8; padding: 6px 12px; font-size: 0.65rem; border-radius: 6px; cursor: pointer; font-weight: 800;">ANNULLA</button>
                    <button id="pure-wiki-prompt-submit" style="background: #3b82f6; border: none; color: white; padding: 6px 16px; font-size: 0.65rem; border-radius: 6px; cursor: pointer; font-weight: 800;">CONFERMA</button>
                </div>
            </div>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    
    const input = document.getElementById('pure-wiki-prompt-input');
    if (input) input.focus();
    
    const submitBtn = document.getElementById('pure-wiki-prompt-submit');
    const submitAction = () => {
        const val = input.value.trim();
        if (val) {
            document.getElementById('pure-wiki-prompt-modal').remove();
            callback(val);
        }
    };
    
    if (submitBtn) submitBtn.onclick = submitAction;
    if (input) {
        input.onkeydown = (e) => {
            if (e.key === 'Enter') submitAction();
        };
    }
};

// Create a new folder at root level
window.pureWikiCreateTheme = () => {
    window.pureWikiPrompt("Nuovo Tema / Cartella", "Inserisci nome tema (es. strategies)...", (name) => {
        const cleanName = name.replace(/[^a-zA-Z0-9_\-]/g, '').toLowerCase();
        if (!cleanName) return;
        
        const newFolder = {
            id: 'f-' + Date.now(),
            name: cleanName,
            type: 'folder',
            children: []
        };
        
        window.pureWikiState.tree.push(newFolder);
        localStorage.setItem('pure_wiki_tree_v1', JSON.stringify(window.pureWikiState.tree));
        window.pureWikiRenderTree();
        window.pureWikiShowToast("Tema creato con successo!", "SUCCESS");
        window.pureWikiInitGraph(); // Redraw connections
    });
};

// Create a new wiki page at root level
window.pureWikiCreatePage = () => {
    window.pureWikiPrompt("Nuova Pagina Wiki", "Inserisci nome file (es. inflation.md)...", (name) => {
        let cleanName = name.trim();
        if (!cleanName.endsWith('.md')) cleanName += '.md';
        
        const newFile = {
            id: 'p-' + Date.now(),
            name: cleanName,
            type: 'file',
            content: `# ${cleanName.replace('.md', '').toUpperCase()}\n\nInizia a scrivere la conoscenza qui...`,
            unsaved: false
        };
        
        window.pureWikiState.tree.push(newFile);
        localStorage.setItem('pure_wiki_tree_v1', JSON.stringify(window.pureWikiState.tree));
        window.pureWikiRenderTree();
        
        // Select newly created file
        window.pureWikiLoadFileByPath([cleanName]);
        window.pureWikiShowToast("Pagina creata con successo!", "SUCCESS");
        window.pureWikiInitGraph();
    });
};

// Create nested child sub-page under a specific folder node
window.pureWikiCreateChildNode = (folderId) => {
    const parentFolder = window.pureWikiFindNodeById(window.pureWikiState.tree, folderId);
    if (!parentFolder || parentFolder.type !== 'folder') return;
    
    window.pureWikiPrompt(`Nuova Sotto-pagina sotto '${parentFolder.name}'`, "Inserisci nome file (es. gdp.md)...", (name) => {
        let cleanName = name.trim();
        if (!cleanName.endsWith('.md')) cleanName += '.md';
        
        const newFile = {
            id: 'p-' + Date.now(),
            name: cleanName,
            type: 'file',
            content: `# ${cleanName.replace('.md', '').toUpperCase()}\n\nInizia a scrivere la sotto-pagina qui...`,
            unsaved: false
        };
        
        if (!parentFolder.children) parentFolder.children = [];
        parentFolder.children.push(newFile);
        
        localStorage.setItem('pure_wiki_tree_v1', JSON.stringify(window.pureWikiState.tree));
        window.pureWikiRenderTree();
        
        // Find route path parts to select the child
        const pathParts = [];
        let p = parentFolder;
        while(p) {
            pathParts.unshift(p.name);
            p = window.pureWikiFindParentOfNode(window.pureWikiState.tree, p.id);
        }
        pathParts.push(cleanName);
        
        window.pureWikiLoadFileByPath(pathParts);
        window.pureWikiShowToast(`Sotto-pagina creata in ${parentFolder.name}!`, "SUCCESS");
        window.pureWikiInitGraph();
    });
};

// Delete wiki folder or page
window.pureWikiDeleteNode = (id) => {
    const node = window.pureWikiFindNodeById(window.pureWikiState.tree, id);
    if (!node) return;
    
    const parent = window.pureWikiFindParentOfNode(window.pureWikiState.tree, id);
    const list = parent ? parent.children : window.pureWikiState.tree;
    const index = list.indexOf(node);
    
    if (index > -1) {
        list.splice(index, 1);
        localStorage.setItem('pure_wiki_tree_v1', JSON.stringify(window.pureWikiState.tree));
        window.pureWikiRenderTree();
        window.pureWikiShowToast("Elemento rimosso correttamente.", "INFO");
        window.pureWikiInitGraph();
    }
};

// Sposta Su/Giù: Index Sort Reordering Controls
window.pureWikiMoveIndex = (id, direction) => {
    const node = window.pureWikiFindNodeById(window.pureWikiState.tree, id);
    if (!node) return;
    
    const parent = window.pureWikiFindParentOfNode(window.pureWikiState.tree, id);
    const list = parent ? parent.children : window.pureWikiState.tree;
    const index = list.indexOf(node);
    
    if (index === -1) return;
    
    const targetIndex = direction === 'up' ? index - 1 : index + 1;
    if (targetIndex < 0 || targetIndex >= list.length) return; // Limits
    
    // Swap items in index list
    const temp = list[index];
    list[index] = list[targetIndex];
    list[targetIndex] = temp;
    
    localStorage.setItem('pure_wiki_tree_v1', JSON.stringify(window.pureWikiState.tree));
    window.pureWikiRenderTree();
    window.pureWikiShowToast("Indice riordinato con successo!", "INFO");
    window.pureWikiInitGraph();
};

// ============================================================================
// 🗺️ HTML5 NATIVE DRAG & DROP SUPPORT FOR SIDEBAR REORDERING
// ============================================================================
window.pureWikiDragStart = (event, id) => {
    window.pureWikiState.draggedNodeId = id;
    event.dataTransfer.effectAllowed = "move";
    event.dataTransfer.setData("text/plain", id);
};

window.pureWikiDragOver = (event) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = "move";
};

window.pureWikiDrop = (event, targetId) => {
    event.preventDefault();
    event.stopPropagation();
    
    const draggedId = window.pureWikiState.draggedNodeId || event.dataTransfer.getData("text/plain");
    if (!draggedId || draggedId === targetId) return;
    
    const draggedNode = window.pureWikiFindNodeById(window.pureWikiState.tree, draggedId);
    const targetNode = window.pureWikiFindNodeById(window.pureWikiState.tree, targetId);
    
    if (!draggedNode || !targetNode) return;
    
    const draggedParent = window.pureWikiFindParentOfNode(window.pureWikiState.tree, draggedId);
    const targetParent = window.pureWikiFindParentOfNode(window.pureWikiState.tree, targetId);
    
    // Get lists
    const draggedList = draggedParent ? draggedParent.children : window.pureWikiState.tree;
    const targetList = targetParent ? targetParent.children : window.pureWikiState.tree;
    
    const draggedIndex = draggedList.indexOf(draggedNode);
    let targetIndex = targetList.indexOf(targetNode);
    
    if (draggedIndex === -1 || targetIndex === -1) return;
    
    // Perform Drop: Remove from original place and insert at target position
    draggedList.splice(draggedIndex, 1);
    
    // Adjust target index if removed from same list and shifted
    if (draggedList === targetList && draggedIndex < targetIndex) {
        targetIndex--;
    }
    
    targetList.splice(targetIndex + 1, 0, draggedNode);
    
    // Save & Update
    localStorage.setItem('pure_wiki_tree_v1', JSON.stringify(window.pureWikiState.tree));
    window.pureWikiRenderTree();
    window.pureWikiInitGraph();
    window.pureWikiShowToast("Index drag drop completato!", "SUCCESS");
};

// ============================================================================
// 🎨 REALTIME 2D CANVAS SPRING FORCE-DIRECTED GRAPH PHYSICS MODEL
// ============================================================================
let pureGraphNodes = [];
let pureGraphLinks = [];
let pureGraphCanvas = null;
let pureGraphCtx = null;
let pureGraphAnimationId = null;
let pureGraphDraggedNode = null;
let pureGraphScale = 1;
let pureGraphOffsetX = 0;
let pureGraphOffsetY = 0;

window.pureWikiInitGraph = () => {
    pureGraphCanvas = document.getElementById('pure-wiki-graph-canvas');
    if (!pureGraphCanvas) return;
    
    pureGraphCtx = pureGraphCanvas.getContext('2d');
    
    // Setup Canvas Resolution
    const rect = pureGraphCanvas.getBoundingClientRect();
    pureGraphCanvas.width = rect.width;
    pureGraphCanvas.height = rect.height;
    
    // Reset positions
    pureGraphOffsetX = rect.width / 2;
    pureGraphOffsetY = rect.height / 2;
    
    // Build Graph Dataset based on current wiki tree hierarchy and explicit links
    pureGraphNodes = [];
    pureGraphLinks = [];
    
    const addNodesFromTree = (nodes, parentNode = null) => {
        nodes.forEach(node => {
            const graphNode = {
                id: node.id,
                name: node.name.replace('.md', ''),
                type: node.type,
                x: (Math.random() - 0.5) * 200,
                y: (Math.random() - 0.5) * 200,
                vx: 0,
                vy: 0,
                size: node.type === 'folder' ? 16 : 10
            };
            pureGraphNodes.push(graphNode);
            
            if (parentNode) {
                // Link folder/file to its hierarchical parent
                pureGraphLinks.push({
                    source: parentNode.id,
                    target: node.id,
                    type: 'hierarchy'
                });
            }
            
            if (node.type === 'folder' && node.children) {
                addNodesFromTree(node.children, graphNode);
            }
        });
    };
    
    addNodesFromTree(window.pureWikiState.tree);
    
    // Add custom semantic connections (e.g. Finance concepts linked to portfolio or Cycles)
    const findNodeByName = (name) => pureGraphNodes.find(n => n.name === name);
    
    const linkConcepts = (n1, n2) => {
        const nodeA = findNodeByName(n1);
        const nodeB = findNodeByName(n2);
        if (nodeA && nodeB) {
            pureGraphLinks.push({
                source: nodeA.id,
                target: nodeB.id,
                type: 'semantic'
            });
        }
    };
    
    linkConcepts('balance-of-payments', 'macro-hedge');
    linkConcepts('bond-index', 'risk-parity');
    linkConcepts('economic-cycles', 'balance-of-payments');
    linkConcepts('equity-premium', 'risk-parity');
    
    // Re-check Bridge state
    if (localStorage.getItem('pure_wiki_bridged') === 'true') {
        const bridgeFile = findNodeByName('financial-regression-bridge');
        if (bridgeFile) {
            // Explicitly draw links representing the AI Bridge!
            const flowNode = findNodeByName('balance-of-payments') || findNodeByName('macro-hedge');
            const regNode = findNodeByName('risk-parity') || findNodeByName('equity-premium');
            
            if (flowNode) {
                pureGraphLinks.push({ source: bridgeFile.id, target: flowNode.id, type: 'bridge' });
            }
            if (regNode) {
                pureGraphLinks.push({ source: bridgeFile.id, target: regNode.id, type: 'bridge' });
            }
        }
    }
    
    // Bind Canvas Interaction Events
    pureGraphCanvas.onmousedown = (e) => {
        const mouseX = (e.offsetX - pureGraphOffsetX) / pureGraphScale;
        const mouseY = (e.offsetY - pureGraphOffsetY) / pureGraphScale;
        
        // Find clicked node
        let clicked = null;
        for (let node of pureGraphNodes) {
            const dist = Math.sqrt((node.x - mouseX)**2 + (node.y - mouseY)**2);
            if (dist < node.size + 10) {
                clicked = node;
                break;
            }
        }
        
        if (clicked) {
            pureGraphDraggedNode = clicked;
            clicked.dragged = true;
            pureGraphCanvas.style.cursor = 'grabbing';
        } else {
            // Pan graph
            pureGraphCanvas.onmousemove = (me) => {
                pureGraphOffsetX += me.movementX;
                pureGraphOffsetY += me.movementY;
            };
        }
    };
    
    pureGraphCanvas.onmouseup = () => {
        if (pureGraphDraggedNode) {
            pureGraphDraggedNode.dragged = false;
            pureGraphDraggedNode = null;
        }
        pureGraphCanvas.style.cursor = 'grab';
        pureGraphCanvas.onmousemove = null;
    };
    
    pureGraphCanvas.onmousemove = (e) => {
        if (pureGraphDraggedNode) {
            pureGraphDraggedNode.x = (e.offsetX - pureGraphOffsetX) / pureGraphScale;
            pureGraphDraggedNode.y = (e.offsetY - pureGraphOffsetY) / pureGraphScale;
        }
    };
    
    // Stop previous animation frame loop if active
    if (pureGraphAnimationId) cancelAnimationFrame(pureGraphAnimationId);
    
    // Render loop
    window.pureWikiRenderGraph();
};

window.pureWikiRenderGraph = () => {
    if (!pureGraphCanvas || !pureGraphCtx) return;
    
    // Sliders
    const sizeSlider = document.getElementById('pure-wiki-slider-size');
    const distSlider = document.getElementById('pure-wiki-slider-distance');
    
    const baseNodeSize = sizeSlider ? parseFloat(sizeSlider.value) : 12;
    const targetDistance = distSlider ? parseFloat(distSlider.value) : 100;
    
    // Physics parameters
    const repulsionK = 600;
    const springK = 0.04;
    const gravityK = 0.01;
    const damping = 0.85;
    
    // 60FPS physics integration step
    for (let step = 0; step < 3; step++) { // Multi-step integration for stiffness stability
        // 1. Repulsion (Push nodes away)
        for (let i = 0; i < pureGraphNodes.length; i++) {
            for (let j = i + 1; j < pureGraphNodes.length; j++) {
                let dx = pureGraphNodes[j].x - pureGraphNodes[i].x;
                let dy = pureGraphNodes[j].y - pureGraphNodes[i].y;
                let dist = Math.sqrt(dx*dx + dy*dy) || 1;
                if (dist < 300) {
                    let force = repulsionK / (dist * dist);
                    let fx = (dx / dist) * force;
                    let fy = (dy / dist) * force;
                    
                    pureGraphNodes[j].vx += fx;
                    pureGraphNodes[j].vy += fy;
                    pureGraphNodes[i].vx -= fx;
                    pureGraphNodes[i].vy -= fy;
                }
            }
        }
        
        // 2. Attraction springs (Links pull connected nodes)
        pureGraphLinks.forEach(link => {
            const n1 = pureGraphNodes.find(n => n.id === link.source);
            const n2 = pureGraphNodes.find(n => n.id === link.target);
            if (!n1 || !n2) return;
            
            let dx = n2.x - n1.x;
            let dy = n2.y - n1.y;
            let dist = Math.sqrt(dx*dx + dy*dy) || 1;
            
            let currentTargetDist = link.type === 'hierarchy' ? targetDistance * 0.7 : targetDistance;
            let force = (dist - currentTargetDist) * springK;
            let fx = (dx / dist) * force;
            let fy = (dy / dist) * force;
            if (!n2.dragged) {
                n2.vx -= fx;
                n2.vy -= fy;
            }
            if (!n1.dragged) {
                n1.vx += fx;
                n1.vy += fy;
            }
        });
        
        // 3. Gravity pulling to center & Update Positions
        pureGraphNodes.forEach(node => {
            let dx = 0 - node.x;
            let dy = 0 - node.y;
            node.vx += dx * gravityK;
            node.vy += dy * gravityK;
            
            if (!node.dragged) {
                node.x += node.vx;
                node.y += node.vy;
            }
            
            node.vx *= damping;
            node.vy *= damping;
        });
    }
    
    // DRAW SCENE
    pureGraphCtx.clearRect(0, 0, pureGraphCanvas.width, pureGraphCanvas.height);
    
    pureGraphCtx.save();
    pureGraphCtx.translate(pureGraphOffsetX, pureGraphOffsetY);
    pureGraphCtx.scale(pureGraphScale, pureGraphScale);
    
    // Draw links
    pureGraphLinks.forEach(link => {
        const n1 = pureGraphNodes.find(n => n.id === link.source);
        const n2 = pureGraphNodes.find(n => n.id === link.target);
        if (!n1 || !n2) return;
        
        pureGraphCtx.beginPath();
        pureGraphCtx.moveTo(n1.x, n1.y);
        pureGraphCtx.lineTo(n2.x, n2.y);
        
        if (link.type === 'hierarchy') {
            pureGraphCtx.strokeStyle = 'rgba(255, 255, 255, 0.05)';
            pureGraphCtx.lineWidth = 1;
            pureGraphCtx.setLineDash([2, 2]);
        } else if (link.type === 'bridge') {
            pureGraphCtx.strokeStyle = '#ef4444';
            pureGraphCtx.lineWidth = 2.5;
            pureGraphCtx.setLineDash([]);
            pureGraphCtx.shadowColor = '#ef4444';
            pureGraphCtx.shadowBlur = 10;
        } else {
            pureGraphCtx.strokeStyle = 'rgba(59, 130, 246, 0.2)';
            pureGraphCtx.lineWidth = 1.5;
            pureGraphCtx.setLineDash([]);
        }
        
        pureGraphCtx.stroke();
        pureGraphCtx.shadowBlur = 0; // Reset glow
    });
    pureGraphCtx.setLineDash([]); // Reset dash
    
    // Draw nodes
    pureGraphNodes.forEach(node => {
        const size = node.type === 'folder' ? baseNodeSize * 1.3 : baseNodeSize;
        
        // Draw Outer Glow Circle
        pureGraphCtx.beginPath();
        pureGraphCtx.arc(node.x, node.y, size + 4, 0, Math.PI * 2);
        
        if (node.type === 'folder') {
            pureGraphCtx.fillStyle = 'rgba(245, 158, 11, 0.05)';
            pureGraphCtx.strokeStyle = 'rgba(245, 158, 11, 0.3)';
        } else {
            const isBridge = (node.name === 'financial-regression-bridge');
            pureGraphCtx.fillStyle = isBridge ? 'rgba(239, 68, 68, 0.1)' : 'rgba(59, 130, 246, 0.05)';
            pureGraphCtx.strokeStyle = isBridge ? 'rgba(239, 68, 68, 0.5)' : 'rgba(59, 130, 246, 0.3)';
        }
        pureGraphCtx.lineWidth = 1;
        pureGraphCtx.fill();
        pureGraphCtx.stroke();
        
        // Draw Solid Inner Node
        pureGraphCtx.beginPath();
        pureGraphCtx.arc(node.x, node.y, size, 0, Math.PI * 2);
        
        if (node.type === 'folder') {
            pureGraphCtx.fillStyle = '#f59e0b';
            pureGraphCtx.shadowColor = '#f59e0b';
        } else {
            const isBridge = (node.name === 'financial-regression-bridge');
            pureGraphCtx.fillStyle = isBridge ? '#ef4444' : '#3b82f6';
            pureGraphCtx.shadowColor = isBridge ? '#ef4444' : '#3b82f6';
        }
        pureGraphCtx.shadowBlur = 8;
        pureGraphCtx.fill();
        pureGraphCtx.shadowBlur = 0; // Reset glow
        
        // Draw Text Label
        pureGraphCtx.fillStyle = '#94a3b8';
        pureGraphCtx.font = "8px 'JetBrains Mono', monospace";
        pureGraphCtx.textAlign = 'center';
        pureGraphCtx.fillText(node.name, node.x, node.y - size - 8);
    });
    
    pureGraphCtx.restore();
    
    pureGraphAnimationId = requestAnimationFrame(window.pureWikiRenderGraph);
};

// Reset Graph positions to center
window.pureWikiResetGraph = () => {
    if (!pureGraphCanvas) return;
    const rect = pureGraphCanvas.getBoundingClientRect();
    pureGraphOffsetX = rect.width / 2;
    pureGraphOffsetY = rect.height / 2;
    pureGraphScale = 1;
    
    pureGraphNodes.forEach(node => {
        node.x = (Math.random() - 0.5) * 100;
        node.y = (Math.random() - 0.5) * 100;
        node.vx = 0;
        node.vy = 0;
    });
    
    window.pureWikiShowToast("Layout grafo ripristinato.", "INFO");
};

// ============================================================================
// 🛰️ COGNITIVE PROMPTS & AI AGENTIC DIALOG SYSTEMS
// ============================================================================

// AI Advice Modal Dialog Box
window.pureWikiGetAIAdvice = () => {
    const activeFileNode = window.pureWikiFindNodeByPath(window.pureWikiState.activeFilePath);
    const fileName = activeFileNode ? activeFileNode.name : 'dossier';
    const contentText = activeFileNode ? activeFileNode.content : '';
    
    // Skywalker & Yoda Advice synthesis mock response
    let adviceText = `
        <div style="font-family:'JetBrains Mono'; font-size:0.65rem; color:#10b981; margin-bottom:10px;">[UPLINKING]: SKYWALKER RETRIEVAL PROCESS</div>
        <p style="margin-bottom:12px; line-height:1.5;">Ho analizzato il dossier <b>${fileName}</b> e formulato i seguenti suggerimenti cognitivi:</p>
        <ul style="padding-left:15px; margin-bottom:15px; display:flex; flex-direction:column; gap:8px;">
            <li>🛡️ <b>Miglioramento dell'Epistemica</b>: La formulazione quantitativa nella sezione iniziale ha una coerenza matematica del 94.3%. Suggerisco di collegarla a un'analisi di regressione.</li>
            <li>🔍 <b>Gaps Rilevati</b>: Manca una correlazione diretta tra l'indice obbligazionario (Bond Index) e i flussi di portafoglio di risk-parity descritti nel file.</li>
            <li>🔮 <b>Consiglio Yoda</b>: <i>"Se l'equilibrio dei mercati comprendere vuoi, la forza transitiva dei flussi BOP combinare devi con modelli statistici coerenti."</i></li>
        </ul>
        <div style="font-size:0.6rem; color:#64748b;">Attestazione di Consistenza: FS-77 & Yoda (Consensus: 100%)</div>
    `;
    
    window.pureWikiShowDialog("CONSIGLI AGENTICI - SKYWALKER & YODA", adviceText);
};

// Ask Question custom chatbot drawer modal
window.pureWikiAskQuestion = () => {
    window.pureWikiPrompt("Domanda sulla Knowledge Base", "Chiedi qualcosa (es. qual è il nesso tra BOP e FOREX?)...", (q) => {
        // Semantic retrieval mock answer
        let answer = `
            <div style="font-family:'JetBrains Mono'; font-size:0.65rem; color:#3b82f6; margin-bottom:10px;">[QUERY]: "${q.toUpperCase()}"</div>
            <p style="margin-bottom:12px; line-height:1.5; color:#e2e8f0;">Sulla base delle pagine correnti nel tuo <b>Pure Wiki</b>:</p>
            <blockquote style="border-left: 2px solid #3b82f6; padding-left: 10px; margin-bottom:12px; font-style:italic; color:#94a3b8; font-size:0.7rem;">
                "La supply/demand di valuta sul FOREX è determinata dai flussi di bilancia dei pagamenti (BOP). Un surplus del conto finanziario provoca apprezzamento valutario, mentre deficit correnti mettono pressione per deprezzamento." (Da balance-of-payments.md)
            </blockquote>
            <p style="line-height:1.5;"><b>Sintesi AI Yoda</b>: I flussi BOP sono i veri vettori di spinta del mercato Forex. La comprensione di queste dinamiche consente un FX Forecasting del 30% più accurato rispetto ai semplici indicatori tecnici.</p>
        `;
        window.pureWikiShowDialog("RISPOSTA SEMANTICA NEURAL VAULT", answer);
    });
};

// Universal dialogue box overlay
window.pureWikiShowDialog = (title, contentHtml) => {
    const existing = document.getElementById('pure-wiki-dialog-modal');
    if (existing) existing.remove();
    
    const modalHtml = `
        <div id="pure-wiki-dialog-modal" style="position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background: rgba(2,6,23,0.85); backdrop-filter: blur(20px); z-index: 99999; display: flex; align-items: center; justify-content: center; opacity: 1; transition: 0.3s; font-family: 'Outfit';">
            <div class="glass-card" style="width: 550px; padding: 30px; border: 1px solid rgba(168,85,247,0.3); border-radius: 20px; text-align: left; box-shadow: 0 40px 100px rgba(0,0,0,0.8); position: relative; overflow:hidden;">
                <!-- Glowing background accent -->
                <div style="position:absolute; top:-20%; left:-20%; width:140%; height:140%; background:radial-gradient(circle, rgba(168,85,247,0.05) 0%, transparent 60%); pointer-events:none;"></div>
                
                <h3 style="color: white; font-weight: 900; margin-bottom: 1.2rem; letter-spacing: 1px; font-size: 1rem; position:relative; display:flex; align-items:center; gap:8px;"><i class="fas fa-brain" style="color:#a855f7;"></i> ${title.toUpperCase()}</h3>
                
                <div style="background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.05); padding: 20px; border-radius: 12px; margin-bottom: 1.5rem; font-size:0.75rem; color:#cbd5e1; max-height: 300px; overflow-y:auto; position:relative;">
                    ${contentHtml}
                </div>
                
                <div style="display: flex; justify-content: flex-end; position:relative;">
                    <button onclick="document.getElementById('pure-wiki-dialog-modal').remove()" class="btn-glow" style="background: #a855f7; border: none; color: white; padding: 8px 24px; font-size: 0.65rem; border-radius: 6px; cursor: pointer; font-weight: 800;">CHIUDI</button>
                </div>
            </div>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', modalHtml);
};

// Custom Cyber-styled toast notifier
window.pureWikiShowToast = (text, type = "INFO") => {
    const toastId = 'toast-' + Date.now();
    const color = type === "SUCCESS" ? "#10b981" : (type === "ERROR" ? "#ef4444" : "#3b82f6");
    
    const toastHtml = `
        <div id="${toastId}" style="position: fixed; bottom: 20px; right: 20px; background: rgba(2,6,23,0.9); backdrop-filter: blur(10px); border-left: 4px solid ${color}; border-top: 1px solid rgba(255,255,255,0.05); border-right: 1px solid rgba(255,255,255,0.05); border-bottom: 1px solid rgba(255,255,255,0.05); border-radius: 8px; padding: 12px 20px; color: white; font-family: 'Outfit'; font-size: 0.7rem; z-index: 100000; box-shadow: 0 10px 30px rgba(0,0,0,0.5); display: flex; align-items: center; gap: 10px; transform: translateY(100px); opacity: 0; transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);">
            <i class="fas ${type === "SUCCESS" ? "fa-check-circle" : (type === "ERROR" ? "fa-times-circle" : "fa-info-circle")}" style="color: ${color}; font-size: 0.8rem;"></i>
            <span>${text}</span>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', toastHtml);
    
    const el = document.getElementById(toastId);
    setTimeout(() => {
        el.style.transform = 'translateY(0)';
        el.style.opacity = '1';
    }, 100);
    
    setTimeout(() => {
        el.style.transform = 'translateY(100px)';
        el.style.opacity = '0';
        setTimeout(() => el.remove(), 400);
    }, 3500);
};

// ============================================================================
// ⚡ AUTOMATED AI BRIDGING WORKFLOW: "GAPS TO BRIDGE" PIPELINE
// ============================================================================
window.pureWikiBridgeGap = () => {
    // Stage 1: Animation Sequence and Sovereign Dispact Modal
    window.showSovereignStatusModal("Financial Flow & Regression Analysis Connection", "FORAGING");
    
    setTimeout(() => {
        window.showSovereignStatusModal("Financial Flow & Regression Analysis Connection", "CRYSTALLIZING");
    }, 2000);
    
    setTimeout(() => {
        window.hideSovereignStatusModal();
        
        // Stage 2: Create a beautiful Connecting Page
        const parentFolder = window.pureWikiFindNodeByPath(['wiki', 'concepts']);
        if (parentFolder && parentFolder.type === 'folder') {
            const fileName = 'financial-regression-bridge.md';
            
            // Check if already bridged
            if (parentFolder.children.find(c => c.name === fileName)) {
                window.pureWikiShowToast("I concetti sono già stati uniti con successo!", "INFO");
                return;
            }
            
            const newFile = {
                id: 'p-bridge-' + Date.now(),
                name: fileName,
                type: 'file',
                content: '# Financial Flow & Regression Analysis Bridge Thesis\n\nQuesta tesi cognitivista, compilata autonomamente dal Consenso Giudici Yoda & Skywalker, stabilisce il nesso logico tra flussi di capitale BOP e analisi predittiva statistica.\n\n## 1. Il Modello di Regressione BOP\n\nAttraverso la regressione lineare multivariata, possiamo formulare:\n\n```python\nY_forex = &beta;_0 + &beta;_1 * Financial_Flows + &beta;_2 * Yield_Differentials + &epsilon;\n```\n\nDove:\n- **Y_forex** rappresenta il vettore dei rendimenti del tasso di cambio.\n- **Financial_Flows** cattura il surplus del conto finanziario netto.\n\n## 2. Risultati Epistemici\n\nLa nostra analisi empirica dimostra che l\'introduzione delle regressioni sui flussi BOP riduce l\'errore quadratico medio predittivo del FOREX del 18.7%. Questa integrazione formalizza la convergenza tra macroeconomia teorica e modellazione quantitativa sistematica.',
                unsaved: false
            };
            
            parentFolder.children.push(newFile);
            
            // Set persistence flag & save tree
            localStorage.setItem('pure_wiki_bridged', 'true');
            localStorage.setItem('pure_wiki_tree_v1', JSON.stringify(window.pureWikiState.tree));
            
            // Update UI
            window.pureWikiRenderTree();
            window.pureWikiLoadFileByPath(['wiki', 'concepts', fileName]);
            
            // Hide the Gap Card in Right Panel
            const gapCard = document.getElementById('pure-wiki-gap-bridge-card');
            if (gapCard) {
                gapCard.style.border = '1px solid rgba(16,185,129,0.3)';
                gapCard.style.background = 'rgba(16,185,129,0.02)';
                gapCard.innerHTML = `
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <span style="font-size:0.55rem; color:#10b981; font-weight:bold; text-transform:uppercase;"><i class="fas fa-circle-check"></i> Gaps Bridged Successfully</span>
                        <span style="font-size:0.45rem; color:#10b981; background:rgba(16,185,129,0.1); padding:1px 4px; border-radius:3px; font-weight:bold;">Consistent</span>
                    </div>
                    <div style="font-size:0.6rem; color:#cbd5e1; margin-top:4px; line-height:1.4;">
                        Skywalker & Yoda hanno integrato e consolidato <b>Financial Flow <-> Regression Analysis</b> via <i>financial-regression-bridge.md</i>.
                    </div>
                `;
            }
            
            // Re-draw graph to show newly drawn solid Red connection!
            window.pureWikiInitGraph();
            
            window.pureWikiShowToast("Ponte Cognitivo Creato!", "SUCCESS");
        }
    }, 4000);
};

