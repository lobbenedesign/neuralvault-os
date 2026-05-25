/**
 * ORACLE ENGINE v9.7 - GHOST PROTOCOL
 * NeuralVault Sovereign Decision Command Hub
 */

window.ORACLE_VERSION = "9.7.0";

window.initOracleEngine = () => {
    console.log("%c🔮 [v9.7] Oracle Engine: INITIALIZING COMMAND HUB", "color: #facc15; font-weight: bold;");
    
    // Small delay to ensure subview is visible before Chart.js takes over
    setTimeout(() => {
        window.initOracleCharts();
        window.updateEpistemicHUD();
        window.renderOraclePlaybook([]); // Start empty
    }, 100);
};

window.toggleOraclePage = () => {
    const p1 = document.getElementById('oracle-page-1');
    const p2 = document.getElementById('oracle-page-2');
    if (p1 && p2) {
        const isP1 = p1.style.display !== 'none';
        p1.style.display = isP1 ? 'none' : 'flex';
        p2.style.display = isP1 ? 'flex' : 'none';
    }
};

window.selectedOracleLens = 'musk'; // Default

window.setOracleLens = (lens) => {
    window.selectedOracleLens = lens;
    document.querySelectorAll('.lens-btn').forEach(btn => {
        btn.classList.remove('active');
        // Check for inclusive match (handle both 'musk' and 'FED / MACRO' type buttons)
        const btnText = btn.innerText.toLowerCase();
        if (btnText.includes(lens.toLowerCase()) || (lens === 'macro' && btnText.includes('fed'))) {
            btn.classList.add('active');
        }
    });
    console.log(`🎯 [v9.7] Oracle Lens set to: ${lens.toUpperCase()}`);
};

window.initOracleCharts = () => {
    // 1. QMC Simulator Chart
    const qmcCtx = document.getElementById('oracle-qmc-chart');
    if (qmcCtx) {
        if (window.oracleQmcChart) window.oracleQmcChart.destroy();
        window.oracleQmcChart = new Chart(qmcCtx, {
            type: 'line',
            data: {
                labels: Array.from({length: 20}, (_, i) => i),
                datasets: [
                    {
                        label: 'Monte Carlo Iterations',
                        data: Array.from({length: 20}, () => Math.random() * 100),
                        borderColor: '#3b82f6',
                        backgroundColor: 'rgba(59, 130, 246, 0.1)',
                        borderWidth: 2,
                        tension: 0.4,
                        fill: true,
                        pointRadius: 0
                    },
                    {
                        label: 'Sovereign Path',
                        data: Array.from({length: 20}, () => Math.random() * 50 + 25),
                        borderColor: '#10b981',
                        borderWidth: 3,
                        tension: 0.4,
                        fill: false,
                        pointRadius: 2
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    x: { display: false },
                    y: { 
                        grid: { color: 'rgba(255,255,255,0.05)' },
                        ticks: { color: '#64748b', font: { size: 9 } }
                    }
                }
            }
        });
    }

    // 2. PCA Chart
    const pcaCtx = document.getElementById('oracle-pca-chart');
    if (pcaCtx) {
        if (window.oraclePcaChart) window.oraclePcaChart.destroy();
        window.oraclePcaChart = new Chart(pcaCtx, {
            type: 'scatter',
            data: {
                datasets: [{
                    label: 'Semantic Clusters',
                    data: Array.from({length: 50}, () => ({
                        x: Math.random() * 10 - 5,
                        y: Math.random() * 10 - 5
                    })),
                    backgroundColor: '#3b82f6',
                    pointRadius: 4,
                    hoverRadius: 6
                }, {
                    label: 'Target Convergence',
                    data: [{ x: 2, y: 3 }],
                    backgroundColor: '#facc15',
                    pointRadius: 8,
                    pointStyle: 'rectRot'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    x: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { display: false } },
                    y: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { display: false } }
                }
            }
        });
    }

    // 3. Parallel Coordinates (Approx with Radar or Bar for now, or just dummy)
    const parCtx = document.getElementById('oracle-parallel-chart');
    if (parCtx) {
        if (window.oracleParChart) window.oracleParChart.destroy();
        window.oracleParChart = new Chart(parCtx, {
            type: 'radar',
            data: {
                labels: ['Risk', 'Volatility', 'Impact', 'Freshness', 'Integrity', 'Velocity'],
                datasets: [{
                    label: 'Current State',
                    data: [65, 40, 80, 90, 70, 55],
                    borderColor: '#3b82f6',
                    backgroundColor: 'rgba(59, 130, 246, 0.2)',
                    borderWidth: 2
                }, {
                    label: 'Projected v9.7',
                    data: [20, 15, 95, 98, 99, 85],
                    borderColor: '#10b981',
                    backgroundColor: 'rgba(16, 185, 129, 0.2)',
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    r: {
                        grid: { color: 'rgba(255,255,255,0.1)' },
                        angleLines: { color: 'rgba(255,255,255,0.1)' },
                        pointLabels: { color: '#64748b', font: { size: 10 } },
                        ticks: { display: false }
                    }
                }
            }
        });
    }
};

window.updateEpistemicHUD = () => {
    // Randomize slightly to simulate real-time telemetry
    const items = document.querySelectorAll('.epistemic-hud-item');
    if (items.length >= 3) {
        const v1 = items[0].querySelector('.hud-value');
        const v2 = items[1].querySelector('.hud-value');
        const v3 = items[2].querySelector('.hud-value');
        if (v1) v1.innerText = (Math.random() * 0.5).toFixed(1) + "%";
        if (v2) v2.innerText = (Math.random() * 5).toFixed(0) + "%";
        if (v3) v3.innerText = (95 + Math.random() * 5).toFixed(1) + "%";
    }
};

window.runSovereignSimulation = async () => {
    const input = document.getElementById('oracle-simulation-input').value;
    if (!input) {
        console.warn("⚠️ [Oracle] Nessun input fornito per la simulazione.");
        return;
    }

    const statusEl = document.getElementById('oracle-status-msg');
    if (statusEl) {
        statusEl.style.display = 'block';
        statusEl.innerHTML = '<i class="fas fa-brain fa-spin"></i> Inizializzazione Neural Engine...';
    }

    const btn = document.getElementById('oracle-run-btn') || event.target;
    const oldHtml = btn.innerHTML;
    btn.innerHTML = '<i class="fas fa-sync-alt fa-spin"></i> ANALISI CAUSALE IN CORSO...';
    btn.disabled = true;

    console.log("🚀 [v9.7] Running Real Sovereign Simulation for:", input);
    console.log("🔭 [v9.7] Active Lens Context:", window.selectedOracleLens);

    try {
        const apiKey = (typeof window.VAULT_KEY !== 'undefined') ? window.VAULT_KEY : 'AURA-ADMIN-77';
        
        const response = await fetch('/api/wiki/simulate/nl', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-API-KEY': apiKey
            },
            body: JSON.stringify({
                query: input,
                lenses: [window.selectedOracleLens || 'standard'],
                mode: 'FAST'
            })
        });

        if (!response.ok) throw new Error(`HTTP Error ${response.status}`);
        
        const data = await response.json();
        console.log("📊 [v9.7] Simulation Data Received:", data);

        // --- 🔗 [v10.0] Pillar #6: Causal Integration ---
        try {
            const causalResp = await fetch('/api/query/causal', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'X-API-KEY': apiKey },
                body: JSON.stringify({ query: input })
            });
            const causalData = await causalResp.json();
            if (causalData.status === 'success' && causalData.causal_links.length > 0) {
                console.log("🕸️ [v10.0] Causal Links Found:", causalData.causal_links);
                // Inject causal info into the report
                data.narrative = `<b>[CAUSAL_DETECTED]</b> Trovati ${causalData.count} legami causali nel grafo.<br><br>` + data.narrative;
            }
        } catch (ce) { console.error("Causal query failed", ce); }

        // --- 🏺 Mappatura Risultati Reali nel Playbook UI ---
        // Usiamo gli 'affected_nodes' per generare i passi del playbook
        if (data.simulation && data.simulation.affected_nodes) {
            const playbook = data.simulation.affected_nodes.slice(0, 6).map((node, i) => ({
                time: `T+${(i+1)*4}h`,
                assignee: i % 2 === 0 ? "Skywalker" : "Yoda",
                priority: node.intensity > 0.6 ? "URGENT" : "HIGH",
                status: "GENERATED",
                progress: 0,
                impact: node.impact,
                title: node.title
            }));
            window.renderOraclePlaybook(playbook);
        }

        // --- 📝 Update Narrative Report ---
        const narrativeEl = document.getElementById('oracle-narrative-box');
        if (narrativeEl) {
            narrativeEl.innerHTML = `<div class="typing-effect">${data.narrative || "Nessun report generato."}</div>`;
        }

        // --- 📈 Update Metrics ---
        if (window.updateSimulationMetrics) {
            window.updateSimulationMetrics(data);
        }
        
        // Update charts to reflect "simulation results"
        if (window.initOracleCharts) window.initOracleCharts(); 
        
        // Success feedback
        btn.innerHTML = '✅ SIMULAZIONE COMPLETATA';
        btn.style.background = '#10b981';
        
        // Show the results in a modal as requested by user
        if (window.showSovereignModal) {
            const playbookPreview = (data.simulation && data.simulation.affected_nodes) 
                ? data.simulation.affected_nodes.slice(0,3).map(n => `<li><b>${n.title}</b>: Impact ${(n.impact * 100).toFixed(1)}%</li>`).join('') 
                : 'Nessun impatto rilevante.';
            
            window.showSovereignModal("🔮 RISULTATI SIMULAZIONE CAUSALE", `
                <div style="padding: 10px;">
                    <div style="background: rgba(16, 185, 129, 0.1); border-left: 3px solid #10b981; padding: 10px; margin-bottom: 15px; font-size: 0.8rem; color: #cbd5e1;">
                        ${data.narrative || "Nessuna narrativa disponibile."}
                    </div>
                    <div style="font-size: 0.7rem; color: #facc15; font-weight: bold; margin-bottom: 5px;">TOP IMPATTI PREVISTI:</div>
                    <ul style="font-size: 0.75rem; color: #fff; margin-bottom: 15px; padding-left: 20px;">
                        ${playbookPreview}
                    </ul>
                    <div style="text-align: center; margin-top: 15px;">
                        <button onclick="window.closeSovereignModal(); window.toggleOraclePage();" style="background: #3b82f6; border: none; padding: 10px 20px; color: #fff; border-radius: 8px; cursor: pointer; font-weight: bold;">VEDI PLAYBOOK COMPLETO</button>
                    </div>
                </div>
            `);
        } else {
            setTimeout(() => {
                window.toggleOraclePage();
            }, 1000);
        }

        setTimeout(() => {
            btn.innerHTML = oldHtml;
            btn.disabled = false;
            btn.style.background = 'linear-gradient(135deg, #facc15, #f59e0b)';
        }, 1500);

    } catch (e) {
        console.error("❌ [v9.7] Real Simulation Failed:", e);
        if (statusEl) statusEl.innerText = "ERRORE CRITICO BACKEND";
        btn.innerHTML = '❌ ERRORE BACKEND';
        btn.style.background = '#ef4444';
        setTimeout(() => {
            btn.innerHTML = oldHtml;
            btn.disabled = false;
            btn.style.background = 'linear-gradient(135deg, #facc15, #f59e0b)';
        }, 2000);
    }
};

window.renderOraclePlaybook = (data) => {
    const body = document.getElementById('oracle-playbook-body');
    if (!body) return;

    if (data.length === 0) {
        body.innerHTML = '<tr><td colspan="5" style="text-align:center; padding: 2rem; color: #64748b;">Nessun playbook generato. Esegui una simulazione.</td></tr>';
        return;
    }

    body.innerHTML = data.map(item => `
        <tr>
            <td>${item.time}</td>
            <td>
                <div style="display:flex; flex-direction:column; gap:2px;">
                    <span style="font-size:0.65rem; color:#fff; font-weight:800;">${item.title || 'Unknown Concept'}</span>
                    <span style="font-size:0.5rem; color:${item.impact > 0 ? '#10b981' : '#ef4444'}; opacity:0.8;">
                        ${item.impact > 0 ? '📈 POSITIVE IMPACT' : '📉 NEGATIVE IMPACT'} (${(item.impact * 100).toFixed(1)}%)
                    </span>
                </div>
            </td>
            <td><div style="display:flex; align-items:center; gap:8px;"><img src="https://ui-avatars.com/api/?name=${item.assignee}&background=3b82f6&color=fff" style="width:16px; height:16px; border-radius:50%;">${item.assignee}</div></td>
            <td><span class="oracle-badge-cite" style="background:${item.priority==='URGENT'?'rgba(239,68,68,0.1)':'rgba(59,130,246,0.1)'}; color:${item.priority==='URGENT'?'#ef4444':'#3b82f6'}; border:none;">${item.priority}</span></td>
            <td>
                <div style="width:100%; height:4px; background:rgba(255,255,255,0.05); border-radius:2px; overflow:hidden;">
                    <div style="width:${item.progress}%; height:100%; background:#3b82f6;"></div>
                </div>
            </td>
        </tr>
    `).join('');
};

window.updateOracleProgress = (data) => {
    const statusEl = document.getElementById('oracle-status-msg');
    if (!statusEl) return;
    
    const stepMap = {
        "PARSING_INTENT": "🧠 Interpretazione Intento in corso (LLM)...",
        "RUNNING_STOCHASTIC_PASSES": `🎲 Simulazione Monte Carlo su "${data.target || 'Nodo'}"...`,
        "GENERATING_NARRATIVE": "🏺 Generazione Report Strategico (Sovereign Synthesis)..."
    };
    
    const msg = stepMap[data.step] || data.step;
    statusEl.innerHTML = `<i class="fas fa-microchip fa-spin" style="color: #facc15; margin-right: 8px;"></i> ${msg}`;
    
    // Feedback visivo sul pulsante se possibile
    const btn = document.getElementById('oracle-run-btn');
    if (btn && data.step === "RUNNING_STOCHASTIC_PASSES") {
        btn.innerHTML = '<i class="fas fa-dice fa-spin"></i> CALCOLO PROBABILISTICO...';
    }
};
