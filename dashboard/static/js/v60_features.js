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
