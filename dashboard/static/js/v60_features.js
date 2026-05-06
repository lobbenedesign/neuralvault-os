// 🎙️ SOVEREIGN VOICE INTERFACE (v6.0)
let voiceRecorder = null;
let voiceStream = null;
let isListening = false;

window.toggleVoiceListen = async () => {
    const btn = document.getElementById('voice-listen-btn');
    if (!btn) return;

    if (!isListening) {
        try {
            voiceStream = await navigator.mediaDevices.getUserMedia({ audio: true });
            voiceRecorder = new MediaRecorder(voiceStream);
            const chunks = [];

            voiceRecorder.ondataavailable = e => chunks.push(e.data);
            voiceRecorder.onstop = async () => {
                const blob = new Blob(chunks, { type: 'audio/wav' });
                const formData = new FormData();
                formData.append('file', blob, 'voice.wav');

                log("🎙️ [Voice] Trascrizione in corso...", "#a855f7");
                const r = await fetch('/api/voice/transcribe?api_key=' + VAULT_KEY, {
                    method: 'POST',
                    body: formData
                });
                const d = await r.json();
                if (d.status === 'success' && d.text) {
                    const input = document.getElementById('floating-url-input').style.display !== 'none' ? 
                                 document.getElementById('floating-url-input') : 
                                 document.getElementById('floating-query-input');
                    input.value = d.text;
                    log(`✅ [Voice] Riconosciuto: "${d.text}"`, "#4ade80");
                }
            };

            voiceRecorder.start();
            isListening = true;
            btn.style.color = "#4ade80";
            btn.style.boxShadow = "0 0 15px #4ade80";
            log("🎙️ [Voice] Ascolto attivo...", "#4ade80");
        } catch (e) {
            log(`❌ [Voice] Errore microfono: ${e.message}`, "#ef4444");
        }
    } else {
        if (voiceRecorder) voiceRecorder.stop();
        if (voiceStream) voiceStream.getTracks().forEach(t => t.stop());
        isListening = false;
        btn.style.color = "#ef4444";
        btn.style.boxShadow = "none";
        log("🎙️ [Voice] Elaborazione terminata.", "#3b82f6");
    }
};

window.toggleVoiceSpeak = async () => {
    const input = document.getElementById('floating-url-input').style.display !== 'none' ? 
                 document.getElementById('floating-url-input') : 
                 document.getElementById('floating-query-input');
    const text = input.value || document.getElementById('neural-chat-answer')?.innerText;

    if (!text || text === "...") return;

    log("🔊 [Voice] Sintesi vocale avviata...", "#3b82f6");
    try {
        await fetch('/api/voice/speak?api_key=' + VAULT_KEY, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text })
        });
    } catch (e) {
        log(`❌ [Voice] Errore sintesi: ${e.message}`, "#ef4444");
    }
};

// 🌌 H-RAG UI Logic
window.refreshGalaxiesList = async () => {
    const container = document.getElementById('galaxies-container');
    if (!container) return;

    try {
        const resp = await fetch('/api/communities/list', {
            headers: { 'X-API-KEY': VAULT_KEY }
        });
        const data = await resp.json();
        
        if (data.status === 'success' && data.communities.length > 0) {
            container.innerHTML = data.communities.map(c => `
                <div class="galaxy-card" style="background: rgba(0,0,0,0.4); border: 1px solid rgba(0,242,254,0.1); border-radius: 16px; padding: 1.5rem; transition: 0.3s; position: relative; overflow: hidden;">
                    <div style="position: absolute; top: -20px; right: -20px; width: 100px; height: 100px; background: radial-gradient(circle, rgba(0,242,254,0.1) 0%, transparent 70%); z-index: 0;"></div>
                    
                    <div style="position: relative; z-index: 1;">
                        <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 1rem;">
                            <span style="font-size: 0.5rem; color: #00f2fe; background: rgba(0,242,254,0.1); padding: 2px 8px; border-radius: 10px; font-weight: 800; text-transform: uppercase;">LEVEL ${c.level} GALAXY</span>
                            <span style="font-size: 0.6rem; color: #94a3b8;"><i class="fas fa-nodes-connect"></i> ${c.nodes} Atomic Nodes</span>
                        </div>
                        
                        <h3 style="color: #fff; font-size: 1rem; margin: 0 0 0.5rem 0; font-weight: 800;">${c.title}</h3>
                        <p style="font-size: 0.65rem; color: #94a3b8; line-height: 1.5; margin-bottom: 1rem;">${c.summary}</p>
                        
                        <div style="display: flex; flex-wrap: wrap; gap: 0.4rem;">
                            ${c.id.startsWith('comm_') ? `<span style="font-size: 0.5rem; color: #8b949e; border: 1px solid rgba(255,255,255,0.1); padding: 2px 6px; border-radius: 4px;">ID: ${c.id}</span>` : ''}
                        </div>
                    </div>
                </div>
            `).join('');
        } else {
            container.innerHTML = `
                <div style="grid-column: 1/-1; text-align: center; padding: 3rem; color: #64748b; font-size: 0.7rem; border: 1px dashed rgba(255,255,255,0.1); border-radius: 12px;">
                    <i class="fas fa-atom" style="font-size: 2rem; margin-bottom: 1rem; display: block; opacity: 0.3; color: #94a3b8;"></i>
                    Mappatura Silenziosa... Nessuna Galassia identificata. 
                    <br><p style="margin-top:10px; opacity:0.6;">L'Archivista richiede nodi interconnessi per formare una costellazione. Prova ad aggiungere più documenti o clicca su RECLUSTER.</p>
                </div>
            `;
        }
    } catch (e) {
        console.error("Failed to load galaxies", e);
        container.innerHTML = `<div style="grid-column: 1/-1; color: #ef4444; text-align: center;">Errore nel collegamento alle Galassie.</div>`;
    }
};

window.triggerReclustering = async () => {
    log("🌌 [H-RAG] Avvio mappatura Galassie Concettuali...", "#00f2fe");
    if (typeof window.triggerSemanticShockwave === 'function') window.triggerSemanticShockwave();
    try {
        const resp = await fetch('/api/communities/recluster', {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                'X-API-KEY': VAULT_KEY
            }
        });
        const data = await resp.json();
        if (data.status === 'success') {
            log("🚀 [H-RAG] Clustering avviato in background.", "#00f2fe");
            const btn = document.getElementById('recluster-btn');
            if (btn) {
                btn.innerHTML = '<i class="fas fa-sync fa-spin"></i> CLUSTERING...';
                btn.disabled = true;
            }
            setTimeout(() => {
                if (btn) {
                    btn.innerHTML = '<i class="fas fa-project-diagram"></i> RECLUSTER';
                    btn.disabled = false;
                }
                window.refreshGalaxiesList();
            }, 5000);
        }
    } catch (e) {
        log("❌ [H-RAG] Errore durante il clustering: " + e, "#ef4444");
    }
};

window.triggerSummarization = async () => {
    log("🧠 [H-RAG] L'Archivista sta preparando i riassunti...", "#a855f7");
    if (typeof window.triggerSynapticSparks === 'function') window.triggerSynapticSparks();
    try {
        const resp = await fetch('/api/communities/summarize', {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                'X-API-KEY': VAULT_KEY
            }
        });
        const data = await resp.json();
        if (data.status === 'success') {
            log("📄 [H-RAG] Analisi descrittiva avviata.", "#a855f7");
            const btn = document.getElementById('summarize-btn');
            if (btn) {
                btn.innerHTML = '<i class="fas fa-sync fa-spin"></i> SUMMARIZING...';
                btn.disabled = true;
            }
            setTimeout(() => {
                if (btn) {
                    btn.innerHTML = '<i class="fas fa-brain"></i> SUMMARIZE';
                    btn.disabled = false;
                }
                window.refreshGalaxiesList();
            }, 8000);
        }
    } catch (e) {
        log("❌ [H-RAG] Errore durante la sintesi: " + e, "#ef4444");
    }
};
// 🏛️ SOVEREIGN WIKI ENGINE (v6.1)
window.generateWiki = async () => {
    const input = document.getElementById('floating-query-input');
    if (!input) return;
    const topic = input.value;
    
    if (!topic) {
        if (typeof log === 'function') log("⚠️ Inserisci un tema per la Wiki.", "#f59e0b");
        return;
    }

    if (typeof log === 'function') log(`🏛️ [Wiki] Generazione in corso per: ${topic}...`, "#a855f7");
    
    const wikiView = document.getElementById('neural-wiki-view');
    if (!wikiView) return;
    
    wikiView.style.display = 'block';
    wikiView.innerHTML = '<div style="text-align:center; padding:3rem;"><i class="fas fa-book-open fa-spin" style="font-size:2rem; color:#a855f7; margin-bottom:1rem;"></i><br>L\'Archivista sta assemblando la conoscenza...</div>';

    try {
        const resp = await fetch('/api/wiki/generate', {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                'X-API-KEY': VAULT_KEY
            },
            body: JSON.stringify({ topic })
        });
        const data = await resp.json();
        
        if (data.status === 'success') {
            if (typeof log === 'function') log(`✅ [Wiki] Pagina generata: ${data.title}`, "#4ade80");
            renderWiki(data);
        } else {
            if (typeof log === 'function') log(`❌ [Wiki Error] ${data.message}`, "#ef4444");
            wikiView.innerHTML = `<div style="color:#ef4444; padding:20px; text-align:center; border:1px solid rgba(239,68,68,0.2); border-radius:12px;">${data.message}</div>`;
        }
    } catch (e) {
        if (typeof log === 'function') log(`❌ [Wiki Error] ${e.message}`, "#ef4444");
        wikiView.innerHTML = `<div style="color:#ef4444; padding:20px; text-align:center;">Errore di connessione con il Sovereign Engine.</div>`;
    }
};

function renderWiki(data) {
    const container = document.getElementById('neural-wiki-view');
    if (!container) return;

    // [v6.1] Freshness Check
    fetch(`/api/wiki/status/${encodeURIComponent(data.title)}`, { headers: { 'X-API-KEY': VAULT_KEY }})
        .then(r => r.json())
        .then(status => {
            if (status.is_stale) {
                const badgeContainer = document.getElementById('wiki-freshness-badge');
                if (badgeContainer) {
                    badgeContainer.innerHTML = `
                        <div style="background: rgba(245, 158, 11, 0.1); color: #f59e0b; padding: 4px 12px; border-radius: 20px; font-size: 0.6rem; font-weight: 800; border: 1px solid rgba(245, 158, 11, 0.3); animation: pulse 2s infinite;">
                            <i class="fas fa-exclamation-triangle"></i> AGGIORNAMENTO DISPONIBILE (${status.stale_nodes} nuovi dati)
                        </div>
                    `;
                }
            }
        });

    const globalConfidence = data.sections && data.sections.length > 0 
        ? Math.round((data.sections.reduce((acc, s) => acc + s.confidence, 0) / data.sections.length) * 100)
        : 75;

    let html = `
        <div class="wiki-container" style="animation: fadeIn 0.8s ease-out; background: rgba(13,17,23,0.8); backdrop-filter: blur(10px); border-radius: 20px; border: 1px solid rgba(168,85,247,0.2); padding: 2rem; max-width: 900px; margin: 0 auto; box-shadow: 0 10px 50px rgba(0,0,0,0.5);">
            <div class="wiki-header" style="border-bottom: 1px solid rgba(168,85,247,0.3); padding-bottom: 1.5rem; margin-bottom: 2rem;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <h1 style="color: #fff; font-size: 2.2rem; margin: 0; font-weight: 900; letter-spacing: -0.5px; text-shadow: 0 0 20px rgba(168,85,247,0.3);">${data.title}</h1>
                    <div id="wiki-freshness-badge" style="text-align: right; display: flex; flex-direction: column; gap: 5px; align-items: flex-end;">
                        <span style="background: rgba(168,85,247,0.1); color: #d8b4fe; padding: 4px 12px; border-radius: 20px; font-size: 0.6rem; font-weight: 800; border: 1px solid rgba(168,85,247,0.3);">VERIFIED KNOWLEDGE</span>
                        ${data.metadata && data.metadata.mesh_verification && Object.keys(data.metadata.mesh_verification).length > 0 ? `
                            <span style="background: rgba(16, 185, 129, 0.1); color: #4ade80; padding: 4px 12px; border-radius: 20px; font-size: 0.55rem; font-weight: 800; border: 1px solid rgba(16, 185, 129, 0.3);">
                                <i class="fas fa-network-wired"></i> MESH CONSENSUS (v7.5)
                            </span>
                        ` : ''}
                    </div>
                </div>
                <div style="font-size: 0.7rem; color: #8b949e; margin-top: 10px; display: flex; gap: 15px; align-items: center;">
                    <span><i class="fas fa-atom" style="color:#a855f7;"></i> ${data.total_nodes} Nodi</span>
                    <span><i class="fas fa-bookmark" style="color:#a855f7;"></i> ${data.citations.length} Citazioni</span>
                    <div style="display: flex; align-items: center; gap: 8px; margin-left: 10px; padding-left: 15px; border-left: 1px solid rgba(255,255,255,0.1);">
                        <span style="font-weight: 800; color: #fff;">CONFIDENCE</span>
                        <div style="width: 100px; height: 6px; background: rgba(255,255,255,0.1); border-radius: 3px; overflow: hidden;">
                            <div style="width: ${globalConfidence}%; height: 100%; background: linear-gradient(90deg, #ef4444, #f59e0b, #4ade80); border-radius: 3px;"></div>
                        </div>
                        <span style="color: #4ade80; font-weight: 800;">${globalConfidence}%</span>
                    </div>
                </div>
            </div>
            
            <div class="wiki-content" style="line-height: 1.8; color: #cbd5e1; font-size: 1rem; font-family: 'Inter', sans-serif;">
                ${processWikiMarkdown(data.markdown, data.citations)}
            </div>

            ${data.metadata && data.metadata.proposals && data.metadata.proposals.length > 0 ? `
                <div class="wiki-proposals" style="margin-top: 3rem; background: rgba(16, 185, 129, 0.05); border: 1px solid rgba(16, 185, 129, 0.2); border-radius: 12px; padding: 1.5rem;">
                    <h4 style="font-size: 0.75rem; color: #10b981; text-transform: uppercase; letter-spacing: 1px; font-weight: 800; margin-bottom: 1.5rem;">
                        <i class="fas fa-lightbulb"></i> Proposte Operative (Actionable Intelligence)
                    </h4>
                    <div style="display: flex; flex-direction: column; gap: 12px;">
                        ${data.metadata.proposals.map(p => `
                            <div class="wiki-proposal-item" style="display: flex; justify-content: space-between; align-items: center; background: rgba(0,0,0,0.3); padding: 12px 20px; border-radius: 10px; border: 1px solid rgba(255,255,255,0.05); transition: 0.3s;">
                                <div style="flex: 1;">
                                    <div style="color: #fff; font-size: 0.85rem; font-weight: 700;">${p.title}</div>
                                    <div style="color: #94a3b8; font-size: 0.65rem; margin-top: 2px;">${p.reason}</div>
                                </div>
                                <button onclick="window.proposeWikiMission('${p.title.replace(/'/g, "\\'")}')" 
                                        class="wiki-tag-btn" 
                                        style="background: rgba(16, 185, 129, 0.2); color: #4ade80; border-color: rgba(16, 185, 129, 0.4); margin-left: 20px; padding: 6px 18px; font-weight: 800;">
                                    ESERSE
                                </button>
                            </div>
                        `).join('')}
                    </div>
                </div>
            ` : ''}
            
            ${data.related && data.related.length > 0 ? `
                <div class="wiki-footer" style="margin-top: 3rem; padding-top: 1.5rem; border-top: 1px dashed rgba(168,85,247,0.2);">
                    <h4 style="font-size: 0.75rem; color: #a855f7; text-transform: uppercase; letter-spacing: 1px; font-weight: 800; margin-bottom: 1rem;">Esplorazione Correlata</h4>
                    <div style="display: flex; gap: 0.7rem; flex-wrap: wrap;">
                        ${data.related.map(r => `
                            <button class="wiki-tag-btn" onclick="document.getElementById('floating-query-input').value='${r}'; generateWiki();" 
                                    style="background: rgba(168,85,247,0.05); color: #d8b4fe; padding: 5px 14px; border-radius: 20px; font-size: 0.7rem; border: 1px solid rgba(168,85,247,0.2); cursor: pointer; transition: 0.2s; font-weight: 600;">
                                ${r}
                            </button>
                        `).join('')}
                    </div>
                </div>
            ` : ''}
            
            <div style="margin-top: 2rem; text-align: center; opacity: 0.4; font-size: 0.55rem; color: #8b949e;">
                Sovereign Wiki Engine v6.1 | © NeuralVault Collective Intelligence
            </div>
        </div>
    `;
    
    container.innerHTML = html;
    
    // Add custom animation styles if not present
    if (!document.getElementById('wiki-styles')) {
        const style = document.createElement('style');
        style.id = 'wiki-styles';
        style.innerHTML = `
            @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
            @keyframes hud-glow { 0% { box-shadow: 0 0 5px rgba(168,85,247,0.2); } 50% { box-shadow: 0 0 15px rgba(168,85,247,0.5); } 100% { box-shadow: 0 0 5px rgba(168,85,247,0.2); } }
            
            .wiki-tag-btn:hover { background: rgba(168,85,247,0.2) !important; color: #fff !important; border-color: #a855f7 !important; transform: scale(1.05); }
            .wiki-proposal-item:hover { transform: translateX(5px); border-color: rgba(16, 185, 129, 0.4); background: rgba(16, 185, 129, 0.1) !important; }
            
            .wiki-citation { 
                position: relative; 
                display: inline-block; 
                padding: 1px 8px;
                border-radius: 4px;
                background: rgba(168, 85, 247, 0.1);
                border: 1px solid rgba(168, 85, 247, 0.3);
                color: #d8b4fe;
                font-weight: 800;
                cursor: help;
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                font-family: 'JetBrains Mono', monospace;
                font-size: 0.65rem;
                text-decoration: none;
            }
            
            .wiki-citation:hover { 
                background: rgba(168, 85, 247, 0.25);
                border-color: #a855f7;
                color: #fff;
                transform: translateY(-1px);
                box-shadow: 0 4px 12px rgba(168, 85, 247, 0.2);
            }
            
            .wiki-citation.conflict {
                background: rgba(239, 68, 68, 0.1);
                border-color: rgba(239, 68, 68, 0.4);
                color: #fca5a5;
            }
            
            .wiki-citation.conflict:hover {
                background: rgba(239, 68, 68, 0.2);
                border-color: #ef4444;
                box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3);
            }
            
            /* Premium HUD Tooltip */
            .wiki-citation-tooltip {
                position: absolute;
                bottom: 140%;
                left: 50%;
                transform: translateX(-50%) translateY(10px);
                width: 300px;
                background: rgba(15, 23, 42, 0.95);
                backdrop-filter: blur(12px);
                border: 1px solid rgba(168, 85, 247, 0.5);
                border-radius: 12px;
                padding: 0;
                color: #e2e8f0;
                font-size: 0.75rem;
                z-index: 2000;
                opacity: 0;
                visibility: hidden;
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                box-shadow: 0 20px 50px rgba(0,0,0,0.6), 0 0 20px rgba(168,85,247,0.1);
                pointer-events: none;
                overflow: hidden;
                text-align: left;
                line-height: 1.4;
            }
            
            .wiki-citation:hover .wiki-citation-tooltip {
                opacity: 1;
                visibility: visible;
                transform: translateX(-50%) translateY(0);
            }
            
            .tooltip-header {
                background: linear-gradient(90deg, rgba(168, 85, 247, 0.2), transparent);
                padding: 10px 15px;
                border-bottom: 1px solid rgba(168, 85, 247, 0.2);
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            
            .tooltip-body {
                padding: 15px;
            }
            
            .tooltip-excerpt {
                font-style: italic;
                color: #94a3b8;
                border-left: 2px solid #a855f7;
                padding-left: 10px;
                margin-top: 10px;
                font-size: 0.7rem;
                line-height: 1.4;
            }
            
            .tooltip-meta {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 8px;
                margin-top: 12px;
                font-size: 0.6rem;
                color: #64748b;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            
            .confidence-bar-wrap {
                height: 4px;
                background: rgba(255,255,255,0.05);
                border-radius: 2px;
                margin-top: 5px;
                overflow: hidden;
            }
            
            .confidence-bar-fill {
                height: 100%;
                background: #a855f7;
                border-radius: 2px;
            }
        `;
        document.head.appendChild(style);
    }
}

window.executeWikiCode = (encodedCode, lang) => {
    try {
        const code = atob(encodedCode);
        if (lang === 'bash' || lang === 'sh' || code.trim().startsWith('$')) {
            const cleanCmd = code.replace(/^\$ /, '').trim();
            if (typeof log === 'function') log(`🚀 [Wiki] Esecuzione comando: ${cleanCmd}`, "#3b82f6");
            if (typeof window.sendDirectCommand === 'function') {
                window.sendDirectCommand(cleanCmd);
            } else {
                navigator.clipboard.writeText(cleanCmd);
                if (typeof showFloatingNotification === 'function') showFloatingNotification("Comando copiato! Incollalo nel terminale.", "success");
            }
        } else {
            navigator.clipboard.writeText(code);
            if (typeof showFloatingNotification === 'function') showFloatingNotification("Codice copiato negli appunti!", "success");
        }
    } catch (e) { console.error("Wiki Action Error:", e); }
};

window.proposeWikiMission = (title) => {
    if (typeof log === 'function') log(`🏛️ [Wiki] Proposta missione: ${title}`, "#10b981");
    const input = document.getElementById('floating-query-input');
    if (input) {
        input.value = `Approfondimento richiesto su: ${title}`;
        if (typeof toggleCommandMode === 'function') {
            const badge = document.getElementById('mode-badge');
            if (badge && badge.innerText !== "QUERY") toggleCommandMode();
        }
    }
    if (typeof showFloatingNotification === 'function') showFloatingNotification("Missione proposta allo Swarm!", "success");
};

// 🏺 [Wiki Mode] UI Toggle
window.toggleWikiMode = () => {
    const wikiBtn = document.getElementById('wiki-action-btn');
    const mainBtn = document.getElementById('main-action-btn');
    const wikiView = document.getElementById('neural-wiki-view');
    const answerView = document.getElementById('neural-chat-answer');
    
    if (!wikiBtn || !mainBtn || !wikiView || !answerView) return;

    if (wikiBtn.style.display === 'none') {
        wikiBtn.style.display = 'block';
        mainBtn.style.display = 'none';
        wikiView.style.display = 'block';
        answerView.style.display = 'none';
        if (typeof log === 'function') log("🏺 [Wiki Mode] Interfaccia enciclopedica attivata.", "#a855f7");
    } else {
        wikiBtn.style.display = 'none';
        mainBtn.style.display = 'block';
        wikiView.style.display = 'none';
        answerView.style.display = 'block';
        if (typeof log === 'function') log("🛡️ [Standard Mode] Ripristinato.", "#3b82f6");
    }
};

function processWikiMarkdown(md, citations) {
    let html = md;

    // 0. Handle Code Blocks (Technical Sections)
    html = html.replace(/```(.*?)\n([\s\S]*?)```/g, (match, lang, code) => {
        const cleanCode = code.trim();
        const isCommand = cleanCode.startsWith('$') || lang === 'bash' || lang === 'sh';
        const actionLabel = isCommand ? 'RUN' : 'COPY';
        const actionIcon = isCommand ? 'fa-terminal' : 'fa-copy';
        
        return `
            <div class="wiki-code-block" style="position: relative; margin: 20px 0; background: #010409; border-radius: 10px; border: 1px solid rgba(168,85,247,0.2); overflow: hidden;">
                <div style="background: rgba(168,85,247,0.1); padding: 6px 15px; font-size: 0.6rem; color: #a855f7; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(168,85,247,0.1);">
                    <span style="font-weight: 800; letter-spacing: 1px;">${(lang || 'CODE').toUpperCase()}</span>
                    <button onclick="window.executeWikiCode('${btoa(unescape(encodeURIComponent(cleanCode)))}', '${lang}')" 
                            style="background: rgba(168,85,247,0.1); border: 1px solid rgba(168,85,247,0.3); color: #fff; cursor: pointer; font-weight: 800; font-size: 0.55rem; padding: 2px 10px; border-radius: 4px; transition: 0.2s;">
                        <i class="fas ${actionIcon}" style="margin-right: 5px;"></i> ${actionLabel}
                    </button>
                </div>
                <pre style="margin: 0; padding: 15px; overflow-x: auto; font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; color: #e6edf3; line-height: 1.5;">${cleanCode}</pre>
            </div>
        `;
    });

    // 1. Convert simple Markdown to HTML
    html = html
        .replace(/^# (.*$)/gim, '<h1 style="color:#fff; margin-top:30px; font-weight:800; border-bottom:2px solid rgba(168,85,247,0.2); padding-bottom:10px;">$1</h1>')
        .replace(/^## (.*$)/gim, '<h2 style="color:#fff; border-left: 4px solid #a855f7; padding-left: 15px; margin-top:35px; font-weight:800;">$1</h2>')
        .replace(/^### (.*$)/gim, '<h3 style="color:#fff; margin-top:20px; font-weight:700;">$1</h3>')
        .replace(/\*\*(.*?)\*\*/g, '<strong style="color:#fff; font-weight:700;">$1</strong>')
        .replace(/\*(.*?)\*/g, '<em style="color:#e2e8f0; opacity:0.9;">$1</em>')
        .replace(/^> (.*$)/gim, '<blockquote style="border-left: 4px solid rgba(168,85,247,0.5); padding: 10px 20px; background: rgba(168,85,247,0.05); border-radius: 0 8px 8px 0; font-style: italic; color: #94a3b8; margin: 20px 0;">$1</blockquote>')
        .replace(/---/g, '<hr style="border: none; border-top: 1px solid rgba(255,255,255,0.1); margin: 30px 0;">');

    // 2. Interactive Citation Replacement (Supports [ID: node_id], [CITE:node_id], and [node_id])
    html = html.replace(/\[(?:ID: |CITE:)?([a-f0-9\-]{4,})\]/gi, (match, nodeId) => {
        const cite = citations.find(c => c.node_id.startsWith(nodeId));
        if (!cite) return `<span style="color:#64748b; font-size:0.7rem; font-family:'JetBrains Mono';">[${nodeId.slice(0,4)}]</span>`;
        
        const isConflict = cite.is_contradictory;
        const icon = isConflict ? 'fa-balance-scale-right' : 'fa-certificate';
        const colorClass = isConflict ? 'conflict' : '';
        
        const confidencePct = Math.round(cite.confidence * 100);
        const confidenceColor = cite.confidence > 0.8 ? '#4ade80' : (cite.confidence > 0.5 ? '#f59e0b' : '#ef4444');
        
        const tooltipHtml = `
            <div class="wiki-citation-tooltip">
                <div class="tooltip-header">
                    <span style="font-weight: 900; color: #fff; font-size: 0.65rem; letter-spacing: 1px;">SOURCE VERIFICATION</span>
                    <i class="fas ${icon}" style="color: ${isConflict ? '#ef4444' : '#a855f7'};"></i>
                </div>
                <div class="tooltip-body">
                    <div style="color: #fff; font-weight: 700; margin-bottom: 4px;">${cite.source_title}</div>
                    <div style="font-size: 0.6rem; color: #8b949e; margin-bottom: 10px;">${cite.source_url ? cite.source_url : 'Internal Vault Node'}</div>
                    
                    <div class="tooltip-excerpt">"${cite.excerpt}..."</div>
                    
                    <div class="tooltip-meta">
                        <div>
                            <span>Freshness</span>
                            <div style="color: #fff; font-weight: 800; margin-top: 2px;">${cite.source_date}</div>
                        </div>
                        <div>
                            <span>Confidence</span>
                            <div style="color: ${confidenceColor}; font-weight: 800; margin-top: 2px;">${confidencePct}%</div>
                            <div class="confidence-bar-wrap">
                                <div class="confidence-bar-fill" style="width: ${confidencePct}%; background: ${confidenceColor};"></div>
                            </div>
                        </div>
                    </div>
                    
                    ${isConflict ? `
                        <div style="margin-top: 15px; padding: 10px; background: rgba(239,68,68,0.1); border: 1px solid rgba(239,68,68,0.3); border-radius: 8px;">
                            <div style="color: #ef4444; font-weight: 900; font-size: 0.6rem; text-transform: uppercase; margin-bottom: 8px;">🚨 Contradiction Detected</div>
                            <div style="display: flex; gap: 5px;">
                                <button onclick="event.stopPropagation(); window.resolveConflict('${cite.node_id}', '${cite.conflict_node_id}', 'KEEP_A')" style="flex:1; background: rgba(239,68,68,0.2); color:#fff; border:1px solid #ef4444; font-size:0.5rem; padding:4px; border-radius:4px; cursor:pointer;">KEEP A</button>
                                <button onclick="event.stopPropagation(); window.resolveConflict('${cite.node_id}', '${cite.conflict_node_id}', 'KEEP_B')" style="flex:1; background: rgba(239,68,68,0.2); color:#fff; border:1px solid #ef4444; font-size:0.5rem; padding:4px; border-radius:4px; cursor:pointer;">KEEP B</button>
                                <button onclick="event.stopPropagation(); window.resolveConflict('${cite.node_id}', '${cite.conflict_node_id}', 'MERGE')" style="flex:1; background: rgba(168,85,247,0.2); color:#fff; border:1px solid #a855f7; font-size:0.5rem; padding:4px; border-radius:4px; cursor:pointer;">MERGE</button>
                            </div>
                        </div>
                    ` : ''}
                </div>
            </div>
        `;

        return `<span class="wiki-citation ${colorClass}" 
                      onclick="window.selectNode('${cite.node_id}')">
                   <i class="fas ${icon}" style="font-size: 0.55rem; margin-right: 4px; vertical-align: middle;"></i>CITE:${nodeId.slice(0, 4)}
                   ${tooltipHtml}
                </span>`;
    });

    // Cleanup extra BRs around titles and code blocks
    html = html.replace(/<\/h2><br>/g, '</h2>');
    html = html.replace(/<\/h1><br>/g, '</h1>');
    html = html.replace(/<\/div><br>/g, '</div>');

    return html;
}

// [v7.0] Causal Logic Extraction
window.extractCausalLogic = async () => {
    if (!window.currentInspectedNodeId) return;
    
    const auditArea = document.getElementById('audit-result-area');
    const auditText = document.getElementById('audit-text');
    const extractBtn = document.getElementById('extract-causal-btn');

    if (auditArea) auditArea.style.display = 'block';
    if (auditText) auditText.innerText = "Lo sciame sta mappando le relazioni causali...";
    if (extractBtn) {
        extractBtn.disabled = true;
        extractBtn.style.opacity = "0.5";
    }

    try {
        const r = await fetch('/api/causal/extract', {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                'X-API-KEY': VAULT_KEY 
            },
            body: JSON.stringify({ id: window.currentInspectedNodeId })
        });
        const d = await r.json();
        
        if (d.causal_links > 0) {
            auditText.innerHTML = '<span style="color: #f59e0b;">[LOGIC_FOUND]</span> Individuati ' + d.causal_links + ' nuovi archi causali.<br>Relazioni: ' + d.relations.join(', ');
            if (typeof log === 'function') log('✨ [Causal] Estratti ' + d.causal_links + ' archi logici.', "#f59e0b");
            // Forza rinfresco scena 3D
            if (window.refreshNebula) window.refreshNebula();
        } else {
            auditText.innerText = "Nessuna relazione causale esplicita individuata in questo frammento.";
        }
    } catch(e) {
        if (auditText) auditText.innerText = "Errore durante l'estrazione logica.";
    } finally {
        if (extractBtn) {
            extractBtn.disabled = false;
            extractBtn.style.opacity = "1";
        }
    }
};

window.resolveConflict = async (id_a, id_b, strategy) => {
    if (typeof log === 'function') log(`⚖️ [Corte Suprema] Risoluzione conflitto avviata: ${strategy}`, "#a855f7");
    try {
        const resp = await fetch('/api/contradictions/resolve', {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                'X-API-KEY': VAULT_KEY
            },
            body: JSON.stringify({ id_a, id_b, strategy })
        });
        const data = await resp.json();
        if (data.status === 'success') {
            if (typeof log === 'function') log(`✅ [Risoluzione] ${data.message}`, "#4ade80");
            if (typeof showFloatingNotification === 'function') showFloatingNotification(data.message, "success");
            // Refresh wiki after a short delay
            setTimeout(() => { if (typeof generateWiki === 'function') generateWiki(); }, 2000);
        }
    } catch (e) {
        if (typeof log === 'function') log(`❌ [Risoluzione Error] ${e.message}`, "#ef4444");
    }
};
