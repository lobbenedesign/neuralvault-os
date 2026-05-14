function initSSE() {
    if (eventSource) eventSource.close();
    // [v9.0] Initial inventory sync
    if (typeof refreshVaultState === 'function') refreshVaultState();
    
    eventSource = new EventSource(`/events?api_key=${VAULT_KEY}`);
    eventSource.onmessage = (e) => {
        const d = JSON.parse(e.data);
        if (d.points) updateThreeScene(d.points, d.links);
        
        // [v11.5] Update Cycloscope HUD (DNA & Security bars)
        if (typeof window.updateCycloscopeHUD === 'function') {
            window.updateCycloscopeHUD(d);
        }
        
        // --- 🧬 [v12.5] CRITICAL TELEMETRY (Hardware) ---
        // We update this even in flight mode to ensure dashboard integrity
        if (d.hardware) {
            const hw = d.hardware;
            const cpuVal = document.getElementById('hw-cpu-val');
            const cpuBar = document.getElementById('hw-cpu-bar');
            if (cpuVal) cpuVal.innerText = `${Math.round(hw.cpu.percent)}%`;
            if (cpuBar) cpuBar.style.width = `${hw.cpu.percent}%`;

            const ramVal = document.getElementById('hw-ram-val');
            const ramBar = document.getElementById('hw-ram-bar');
            if (ramVal) ramVal.innerText = `${hw.ram.used} / ${hw.ram.total} GB`;
            if (ramBar) ramBar.style.width = `${hw.ram.percent}%`;

            const gpuVal = document.getElementById('hw-gpu-val');
            const gpuBar = document.getElementById('hw-gpu-bar');
            if (gpuVal) gpuVal.innerText = `${Math.round(hw.gpu.percent)}%`;
            if (gpuBar) gpuBar.style.width = `${hw.gpu.percent}%`;

            const diskVal = document.getElementById('hw-disk-val');
            const diskBar = document.getElementById('hw-disk-bar');
            if (diskVal) diskVal.innerText = `${hw.disk.used} / ${hw.disk.total} GB`;
            if (diskBar) diskBar.style.width = `${hw.disk.percent}%`;
        }

        // --- 🚀 FLIGHT PERFORMANCE PROTOCOL ---
        // Durante il volo congeliamo i reflow pesanti (grid, charts) per ottenere 60 FPS stabili,
        // aggiornando SOLO le posizioni 3D visive degli agenti (Yoda, Skywalker, Mando)
        if (window.isFlightModeActive) {
            if (d.lab && d.lab.agents) {
                const a = d.lab.agents;
                for (const id in a) {
                    const exp = window.nebulaExpansionFactor || 1.0;
                    const data = a[id];
                    if (!data.pos) continue;
                    
                    if (id.includes('FS-77') && window.skywalkerTargetPos) {
                        window.skywalkerTargetPos.set(data.pos.x * exp, data.pos.y * exp, data.pos.z * exp);
                    }
                    if (id.includes('YO-001') && window.yodaTargetPos) {
                        window.yodaTargetPos.set(data.pos.x * exp, data.pos.y * exp, data.pos.z * exp);
                    }
                    if (id.includes('DN-099') && window.mandalorianTargetPos) {
                        window.mandalorianTargetPos.set(data.pos.x * exp, data.pos.y * exp, data.pos.z * exp);
                    }
                }
            }
            return; 
        }

        if (d.lab) refreshEvolutionChat(); // [v3.8.5] Real-time Evo Sync
        if (d.nodes_count !== undefined) {
            document.querySelectorAll('.stat-nodes').forEach(el => el.innerText = d.nodes_count);
            ['stat-nodes', 'stat-nodes-2', 'stat-nodes-lab'].forEach(id => {
                const el = document.getElementById(id); if(el) el.innerText = d.nodes_count;
            });
            
            // [v4.1] Update Knowledge Growth Chart
            if (window.growthChart) {
                const data = window.growthChart.data.datasets[0].data;
                data.shift();
                data.push(d.nodes_count);
                window.growthChart.update('none'); // Update without animation for performance
            }
        }
        if (d.edges_count !== undefined) {
            document.querySelectorAll('.stat-synapses').forEach(el => el.innerText = d.edges_count);
            ['stat-synapses', 'stat-synapses-2', 'stat-synapses-lab'].forEach(id => {
                const el = document.getElementById(id); if(el) el.innerText = d.edges_count;
            });
            
            // [v4.1] Update Cognitive Density Chart
            if (window.densityChart && d.nodes_count > 0) {
                const density = (d.edges_count / d.nodes_count).toFixed(2);
                const data = window.densityChart.data.datasets[0].data;
                data.shift();
                data.push(density);
                window.densityChart.update('none');
            }
        }
        if (d.clusters_count !== undefined) {
            document.querySelectorAll('.stat-clusters').forEach(el => el.innerText = d.clusters_count);
            ['stat-clusters', 'stat-clusters-2', 'stat-clusters-lab'].forEach(id => {
                const el = document.getElementById(id); if(el) el.innerText = d.clusters_count;
            });
        }
        if (d.semantic_distance !== undefined) {
            const el = document.getElementById('stat-distance'); if(el) el.innerText = d.semantic_distance;
        }
        if (d.storage && d.storage.total) {
            const el = document.getElementById('stat-storage'); if(el) el.innerText = d.storage.total;
        }
        if (d.agent007) {
            const ent = document.getElementById('stat-agent007-entities'); if(ent) ent.innerText = d.agent007.entities_count || 0;
            const rel = document.getElementById('stat-agent007-relations'); if(rel) rel.innerText = d.agent007.relations_count || 0;
        }
        if (d.cognitive) {
            const el = document.getElementById('metrics-data');
            if (el) el.innerText = `Ret: ${(d.cognitive.retention * 100).toFixed(1)}% | Stab: ${(d.cognitive.stability * 100).toFixed(1)}%`;
        }
        if (d.heatmap) currentHeatmap = d.heatmap;
        
        // 💤 [v7.0] Sleep & Dreaming UI Sync
        const remInd = document.getElementById('rem-phase-indicator');
        if (remInd && d.sleep) {
            if (d.sleep.active) {
                remInd.classList.remove('hidden');
                const remText = remInd.querySelector('span');
                if (remText) {
                    if (d.sleep.dreaming) {
                        remText.innerText = `DREAMING: ${d.sleep.topic.toUpperCase()}`;
                        remInd.style.borderColor = "#f59e0b";
                        remInd.querySelector('.pulse-dot').style.background = "#f59e0b";
                    } else {
                        remText.innerText = "REM PHASE ACTIVE";
                        remInd.style.borderColor = "#a855f7";
                        remInd.querySelector('.pulse-dot').style.background = "#a855f7";
                    }
                }
            } else {
                remInd.classList.add('hidden');
            }
        }

        // 🧬 [v4.0] Sovereign Hardware Telemetry Update
        if (d.hardware) {
            const hw = d.hardware;
            const cpuVal = document.getElementById('hw-cpu-val');
            const cpuBar = document.getElementById('hw-cpu-bar');
            const cpuCores = document.getElementById('hw-cpu-cores');
            if (cpuVal) cpuVal.innerText = `${Math.round(hw.cpu.percent)}%`;
            if (cpuBar) cpuBar.style.width = `${hw.cpu.percent}%`;
            if (cpuCores) cpuCores.innerText = hw.cpu.cores;

            const ramVal = document.getElementById('hw-ram-val');
            const ramBar = document.getElementById('hw-ram-bar');
            const ramFree = document.getElementById('hw-ram-useful');
            if (ramVal) ramVal.innerText = `${hw.ram.used} / ${hw.ram.total} GB`;
            if (ramBar) ramBar.style.width = `${hw.ram.percent}%`;
            if (ramFree) ramFree.innerText = hw.ram.available;

            const gpuVal = document.getElementById('hw-gpu-val');
            const gpuBar = document.getElementById('hw-gpu-bar');
            if (gpuVal) gpuVal.innerText = `${Math.round(hw.gpu.percent)}%`;
            if (gpuBar) gpuBar.style.width = `${hw.gpu.percent}%`;

            const diskVal = document.getElementById('hw-disk-val');
            const diskBar = document.getElementById('hw-disk-bar');
            if (diskVal) diskVal.innerText = `${hw.disk.used} / ${hw.disk.total} GB`;
            if (diskBar) diskBar.style.width = `${hw.disk.percent}%`;

            // [ADVANCED ANALYTICS SYNC]
            const dnaTrace = document.getElementById('hardware-dna-trace');
            if (dnaTrace) dnaTrace.innerText = `${hw.gpu.backend || 'LOCAL-CORE'}`;
            
            const ramFill = document.getElementById('ram-usage-fill');
            const ramText = document.getElementById('ram-usage-text');
            if (ramFill) ramFill.style.width = `${hw.ram.percent}%`;
            if (ramText) ramText.innerText = `${hw.ram.percent}% / ${hw.ram.total} GB`;

            const computeMode = document.getElementById('active-compute-mode');
            if (computeMode) computeMode.innerText = `MODE: ${hw.gpu.backend === 'APPLE METAL' ? 'METAL HYBRID' : 'SOVEREIGN CPU'}`;

            const mpsPressure = document.getElementById('mps-pressure-val');
            if (mpsPressure) mpsPressure.innerText = `MPS: ${Math.round(hw.gpu.percent)}%`;

            // Populate CPU Grid if in Analytics view
            if (document.getElementById('analytics-view')?.style.display !== 'none') {
                updateCPUGrid(hw.cpu);
            }
        }

        if (d.lab) {
            const lab = d.lab;
            // Update Active Model Name
            const modelName = document.getElementById('ai-model-name');
            const modelQuant = document.getElementById('ai-model-quant');
            const activeModel = lab.swarm_settings?.chat_model || lab.swarm_settings?.audit_model || "NEURAL-HUB-CORE";
            if (modelName) modelName.innerText = activeModel.toUpperCase();
            if (modelQuant) modelQuant.innerText = activeModel.includes('q') ? activeModel.split(':').pop() : "8-bit";

            // Update Historical Stats (Simulated or from lab data)
            const wisdom = document.getElementById('hist-wisdom');
            const depth = document.getElementById('hist-depth');
            const yieldVal = document.getElementById('hist-yield');
            const growth = document.getElementById('hist-growth');
            
            if (wisdom) wisdom.innerText = (lab.blackboard?.recent?.length || 0) + (d.nodes_count % 100);
            if (depth) depth.innerText = (d.nodes_count / 100).toFixed(1) + " Layers";
            if (yieldVal) yieldVal.innerText = "98.2%";
            if (growth) growth.innerText = "+" + (d.nodes_count > 0 ? (d.nodes_count/10).toFixed(1) : 0) + " pts";
        }

        const weather = d.weather || (d.lab ? d.lab.weather : null);
        if (weather) {
            const cog = document.getElementById('metrics-data');
            if (cog) {
                const conf = weather.epistemic_metrics?.conflict_rate || '0%';
                cog.innerText = `Ret: ${weather.retention || '0%'} | Stab: ${weather.stability || '0%'} | Confl: ${conf}`;
                if (weather.stability) {
                    cog.style.color = weather.stability.includes('99') ? '#10b981' : weather.stability.includes('98') ? '#3b82f6' : '#f59e0b';
                }
            }
            if (weather.mood) {
                const light = document.getElementById('mood-light');
                const text = document.getElementById('mood-text');
                const container = document.getElementById('vault-mood-container');
                if (light && text) {
                    text.innerText = `${weather.mood} ${weather.mood_status || 'STABLE'}`;
                    let color = '#10b981';
                    if (weather.mood === '☀️') color = '#10b981';
                    if (weather.mood === '🌤️') color = '#4ade80';
                    if (weather.mood === '🌥️') color = '#94a3b8';
                    if (weather.mood === '🌩️') color = '#ef4444';
                    if (weather.mood === '🔴') color = '#ff0000';
                    
                    light.style.background = color;
                    light.style.boxShadow = `0 0 15px ${color}`;

                    // [v8.4] Tooltip for Epistemic Metrics
                    if (container && weather.epistemic_metrics) {
                        const m = weather.epistemic_metrics;
                        container.title = `EPISTEMIC HEALTH:\n- Conflicts: ${m.conflict_rate || '0%'}\n- Freshness: ${m.avg_age || '0d'}\n- Orphans: ${m.orphan_rate || '0%'}\n- Integrity Score: ${Math.round((weather.score || 1) * 100)}%`;
                    }
                }
            }
        }

        if (d.lab && d.lab.agents) {
            if (!window._telemetry_logged) {
                console.log("📊 [Diagnostic] Agent Telemetry Payload:", d.lab.agents);
                window._telemetry_logged = true;
            }
            if (typeof window.renderAgentGrid === 'function') {
                try { window.renderAgentGrid(d.lab); } catch(e) { console.error("Agent Grid Error:", e); }
            }
            const a = d.lab.agents;
            for (const id in a) {
                const agentData = a[id];
                const exp = nebulaExpansionFactor || 1.0;
                const cleanId = id.toLowerCase().includes('di') ? 'distiller' : 
                                id.toLowerCase().includes('ja') ? 'janitron' : 
                                id.toLowerCase().includes('rp') ? 'reaper' : 
                                id.toLowerCase().includes('sn') ? 'snake' : 
                                id.toLowerCase().includes('qt') || id.toLowerCase().includes('qa') ? 'quantum' : 
                                id.toLowerCase().includes('se') ? 'sentinel' : 
                                id.toLowerCase().includes('sy') ? 'synth' : 
                                id.toLowerCase().includes('fs') ? 'skywalker' : 
                                id.toLowerCase().includes('yo') ? 'yoda' : 
                                id.toLowerCase().includes('ag') ? 'smith' : 
                                id.toLowerCase().includes('nc') ? 'compressor' : 
                                id.toLowerCase().includes('dn') ? 'mandalorian' : 
                                id.toLowerCase().includes('r2') ? 'r2-d2' : 
                                id.startsWith('CU-') ? id.toLowerCase() : 'bridger';
                
                let hud = document.getElementById(cleanId + "-hud-icon");
                if (!hud && id.startsWith('CU-')) {
                    if (typeof window.createDynamicAgentHUD === 'function') {
                        hud = window.createDynamicAgentHUD(id, agentData);
                    }
                }
                if (hud) {
                    const hasActivity = (
                        (agentData.processed || 0) > 0 || 
                        (agentData.purged || 0) > 0 || 
                        (agentData.pruned || 0) > 0 || 
                        (agentData.found || 0) > 0 || 
                        (agentData.crafted || 0) > 0 || 
                        (agentData.deleted || 0) > 0 || 
                        (agentData.fused_clusters || 0) > 0 || 
                        (agentData.validated || 0) > 0 || 
                        (agentData.super_synapses || 0) > 0 || 
                        (agentData.sparks || 0) > 0 || 
                        (agentData.bridges || 0) > 0 || 
                        (agentData.web_hits || 0) > 0 || 
                        (agentData.nodes_forged || 0) > 0 ||
                        (agentData.optimized_nodes || 0) > 0 ||
                        (agentData.optimized_nodes_session || 0) > 0 ||
                        agentData.is_training === true
                    );
                    try {
                        const status = (agentData.status || "idle").toLowerCase();
                        const isOperating = !status.includes('idle') && !status.includes('hold') && !status.includes('stasis') && !status.includes('offline');
                        
                        if (isOperating || hasActivity) {
                            hud.classList.remove('inactive-agent');
                            hud.style.opacity = "1";
                            hud.style.filter = "none";
                            hud.style.transform = "scale(1)";
                        } else {
                            hud.classList.add('inactive-agent');
                            hud.style.opacity = "0.45";
                            hud.style.filter = "grayscale(0.8) blur(0.5px)";
                            hud.style.transform = "scale(0.98)";
                        }
                    } catch(err) { console.warn("HUD Update Fail:", id, err); }

                    if (id === 'YO-001') {
                        const eses = document.getElementById('val-yoda-examined-session');
                        const etot = document.getElementById('val-yoda-examined-total');
                        const esearch = document.getElementById('val-yoda-searches');
                        const egalaxies = document.getElementById('val-yoda-galaxies');
                        const eintro = document.getElementById('val-yoda-introduced');
                        const estatus = document.getElementById('val-yoda-status-text');

                        if(eses) eses.innerText = agentData.nodes_examined_session || 0;
                        if(etot) etot.innerText = agentData.nodes_examined_total || 0;
                        if(esearch) esearch.innerText = agentData.web_hits_session || 0;
                        if(egalaxies) egalaxies.innerText = agentData.galaxies_session || 0;
                        if(eintro) eintro.innerText = agentData.nodes_introduced_session || 0;
                        if(estatus) estatus.innerText = agentData.status || "Meditating...";
                        
                        yodaTargetPos.set(agentData.pos.x * exp, agentData.pos.y * exp, agentData.pos.z * exp);
                        if (yodaGroup) {
                            yodaGroup.userData.laser = agentData.laser || false;
                            yodaGroup.userData.laserTarget = agentData.laserTarget || {x:0, y:0, z:0};
                        }
                        
                        if(agentData.laser && yodaGroup) {
                            spawnYodaBullet(yodaGroup.position.clone(), new THREE.Vector3(agentData.laserTarget.x * exp, agentData.laserTarget.y * exp, agentData.laserTarget.z * exp));
                        }

                        if (agentData.status && agentData.status !== (lastAgentStates[id] || "")) {
                            if (agentData.status.includes("EXAMINING")) {
                                showHologram('YODA_PILOT', 'msg_yoda_analyzing');
                            } else if (agentData.status.includes("MISSION_COMPLETE")) {
                                showHologram('YODA', 'msg_yoda_galaxy', { 
                                    g: agentData.galaxies_session || 0, 
                                    n: agentData.nodes_in_last_galaxy || 0,
                                    name: agentData.last_galaxy_name || "Nova",
                                    dist: (agentData.last_galaxy_dist || 0).toFixed(1)
                                });
                            }
                            lastAgentStates[id] = agentData.status;
                        }
                    }
                    if (id === 'DN-099') {
                        const h = document.getElementById('val-mando-herds');
                        if (h) h.innerText = agentData.herds_session || 0;
                        const s = document.getElementById('val-mando-status');
                        if (s) s.innerText = agentData.status || "Patrolling...";
                        mandalorianTargetPos.set(agentData.pos.x * exp, agentData.pos.y * exp, agentData.pos.z * exp);
                        
                        if (mandalorianGroup) {
                            mandalorianGroup.userData.status = agentData.status || "";
                            mandalorianGroup.userData.laserTarget = agentData.laserTarget ? new THREE.Vector3(agentData.laserTarget.x * exp, agentData.laserTarget.y * exp, agentData.laserTarget.z * exp) : null;
                        }

                        if (agentData.status && agentData.status !== (lastAgentStates[id] || "")) {
                            if (agentData.status.includes("MISSION_COMPLETE") || agentData.status.includes("Mission Success")) {
                                showHologram('MANDALORIAN', 'msg_mando_unity', { 
                                    n: agentData.herds_session || 0,
                                    arcs: agentData.optimized_arcs_session || 0
                                });
                            }
                            if (agentData.status.includes("EXPANSION") || agentData.status.includes("Traveling")) {
                                showHologram('MANDALORIAN', 'msg_mando_path', { n: agentData.herds_session || 0 });
                            }
                            if (agentData.status.includes("SCANNING")) {
                                if (mandalorianGroup) spawnMandoScanner(mandalorianGroup);
                            }
                            lastAgentStates[id] = agentData.status;
                        }
                    }
                    if (id === 'RP-001') { 
                        const el = document.getElementById('val-reaper-healed'); 
                        const rmb = document.getElementById('val-reaper-reclaimed');
                        if(el) {
                            const newVal = agentData.processed_session || 0;
                            if (newVal > parseInt(el.innerText || "0")) {
                                showHologram('REAPER', 'msg_reaper_healed', { n: newVal, mb: (agentData.reclaimed_mb_session || 0).toFixed(2) });
                                spawnReaperMonument({
                                    x: agentData.pos.x * exp,
                                    y: agentData.pos.y * exp,
                                    z: agentData.pos.z * exp
                                });
                            }
                            el.innerText = newVal; 
                        }
                        if(rmb) rmb.innerText = (agentData.reclaimed_mb_session || 0).toFixed(2);
                        reaperTargetPos.set(agentData.pos.x * exp, agentData.pos.y * exp, agentData.pos.z * exp);
                    }
                    if (id === 'DI-007') { 
                        const el = document.getElementById('val-distiller-pruned'); 
                        if(el) {
                            const newVal = agentData.pruned_session || 0;
                            if (newVal > parseInt(el.innerText || "0")) {
                                showHologram('DISTILLER', 'msg_distiller_pruning');
                            }
                            el.innerText = newVal;
                        }
                        distillerTargetPos.set(agentData.pos.x * exp, agentData.pos.y * exp, agentData.pos.z * exp);
                    }
                    if (id === 'JA-001') { 
                        const el = document.getElementById('val-janitron-purged'); 
                        if(el) {
                            const newVal = agentData.purged_session || 0;
                            if (newVal > parseInt(el.innerText || "0")) {
                                showHologram('JANITRON', 'msg_janitron_cleaning');
                            }
                            el.innerText = newVal;
                        }
                        janitronTargetPos.set(agentData.pos.x * exp, agentData.pos.y * exp, agentData.pos.z * exp);
                    }
                    if (id === 'SN-008') { 
                        const found = document.getElementById('val-snake-found'); 
                        const crafted = document.getElementById('val-snake-crafted');
                        const deleted = document.getElementById('val-snake-deleted');
                        if(found) found.innerText = agentData.found_session || 0;
                        if(crafted) crafted.innerText = agentData.crafted_session || 0;
                        if(deleted) deleted.innerText = agentData.deleted_session || 0;

                        if (agentData.status && agentData.status !== (lastAgentStates[id] || "")) {
                            if (agentData.status.includes("DISCOVERY")) {
                                showHologram('SNAKE', 'msg_snake_discovery');
                            }
                            if (agentData.status.includes("SPROUTING")) {
                                showHologram('SNAKE', 'msg_snake_connecting');
                            }
                            lastAgentStates[id] = agentData.status;
                        }
                        snakeTargetPos.set(agentData.pos.x * exp, agentData.pos.y * exp, agentData.pos.z * exp);
                    }
                    if (id === 'QT-004' || id === 'QA-101') { 
                        const el = document.getElementById('val-quantum-fused'); 
                        if (agentData.is_fusing && agentData.status !== (lastAgentStates[id] || "")) {
                            showHologram('QBERT', 'msg_quantum_fusion');
                            quantumFlashTime = 120;
                            lastAgentStates[id] = agentData.status;
                        }
                        if(el) {
                            const newVal = agentData.fused_clusters_session || 0;
                            if (newVal > parseInt(el.innerText || "0")) {
                                showHologram('QBERT', 'msg_quantum_fusion');
                            }
                            el.innerText = newVal;
                        }
                        quantumTargetPos.set(agentData.pos.x * exp, agentData.pos.y * exp, agentData.pos.z * exp);
                    }
                    if (id === 'SE-007') { 
                        const el = document.getElementById('val-sentinel-validated'); 
                        const syn = document.getElementById('val-sentinel-synapses');
                        if(el) {
                            const newVal = agentData.validated_session || 0;
                            if (newVal > parseInt(el.innerText || "0")) {
                                showHologram('SENTINEL', 'msg_sentinel_superbridge', { n: agentData.super_synapses_session || 0 });
                            }
                            el.innerText = newVal;
                        }
                        if(syn) syn.innerText = agentData.super_synapses_session || 0;
                        sentinelTargetPos.set(agentData.pos.x * exp, agentData.pos.y * exp, agentData.pos.z * exp);
                    }
                    if (id === 'SY-009') { 
                        const el = document.getElementById('val-synth-sparks'); 
                        if(el) {
                            const newVal = agentData.sparks_session || 0;
                            if (newVal > parseInt(el.innerText || "0")) {
                                showHologram('KIRBY', 'msg_kirby_synthesis');
                                synthFlashTime = 900; 
                                window.synthSparkTime = 900;
                            }
                            el.innerText = newVal;
                        }
                        if (agentData.status && agentData.status.includes("SPARK") && agentData.status !== (lastAgentStates[id] || "")) {
                            showHologram('KIRBY', 'msg_kirby_synthesis');
                            lastAgentStates[id] = agentData.status;
                            window.synthSparkTime = 900; 
                        }
                        synthTargetPos.set(agentData.pos.x * exp, agentData.pos.y * exp, agentData.pos.z * exp);
                    }
                    if (id === 'CB-003') {
                        const b = document.getElementById('val-bridger-bridges'); 
                        if(b) {
                            const newVal = agentData.bridges_session || 0;
                            if (newVal > parseInt(b.innerText || "0")) {
                                showHologram('BRIDGER', 'msg_bridger_link');
                            }
                            b.innerText = newVal;
                        }
                        bridgerTargetPos.set(agentData.pos.x * exp, agentData.pos.y * exp, agentData.pos.z * exp);
                    }
                    if (id === 'R2-D2') {
                        const org = document.getElementById('val-r2d2-organized');
                        const gal = document.getElementById('val-r2d2-galaxies');
                        if (org) org.innerText = agentData.organized_session || 0;
                        if (gal) gal.innerText = agentData.galaxies_session || 0;
                        r2d2TargetPos.set(agentData.pos.x * exp, agentData.pos.y * exp, agentData.pos.z * exp);
                        
                        // 🤖 [v17.9] Sync Operational State for LED Pulse
                        if (window.r2d2Group) {
                            window.r2d2Group.userData.isOperating = agentData.is_operating;
                        }
                        
                        if (agentData.status && agentData.status !== (lastAgentStates[id] || "")) {
                            if (agentData.status.includes("WAREHOUSE") || agentData.status.includes("Organizing")) {
                                showHologram('R2D2', 'msg_r2d2_grouping', { n: agentData.organized_session || 0 });
                            } else if (agentData.status.includes("Complete") || agentData.status.includes("Audit")) {
                                showHologram('R2D2', 'msg_r2d2_audit', { n: agentData.organized_session || 0 });
                            }
                            lastAgentStates[id] = agentData.status;
                        }
                    }
                    if (id.toLowerCase().includes('ag-001') || id.toLowerCase().includes('smith')) {
                        // Update Smith positions for all members of the fleet
                        if (window.smithTargetPositions) {
                            window.smithTargetPositions[id] = new THREE.Vector3(agentData.pos.x * exp, agentData.pos.y * exp, agentData.pos.z * exp);
                        }
                    }
                    if (id === 'FS-77') {
                        const introduced = document.getElementById('val-skywalker-introduced');
                        const searches = document.getElementById('val-skywalker-searches');
                        const stext = document.getElementById('val-skywalker-status-text');
                        if(introduced) introduced.innerText = agentData.nodes_introduced_session || 0;
                        if(searches) searches.innerText = agentData.web_hits_session || 0;
                        if(stext) stext.innerText = agentData.status || "Scanning Horizon...";
                        
                        skywalkerTargetPos.set(agentData.pos.x * exp, agentData.pos.y * exp, agentData.pos.z * exp);

                        if (agentData.status && agentData.status !== (lastAgentStates[id] || "")) {
                            if (agentData.status.includes("FORAGE")) {
                                showHologram('SKYWALKER', 'msg_skywalker_foraging');
                            } else if (agentData.status.includes("MISSION_COMPLETE")) {
                                showHologram('SKYWALKER', 'msg_skywalker_success', { 
                                    n: agentData.nodes_introduced_session || 0,
                                    g: agentData.galaxies_session || 0
                                });
                            } else if (agentData.status.includes("FAILED")) {
                                showHologram('JARJAR', 'msg_jarjar_error');
                            }
                            lastAgentStates[id] = agentData.status;
                        }

                        const statusEl = document.getElementById('skywalker-mission-stat');
                        const cardEl = document.getElementById('skywalker-hud-icon');
                        const isActiveMission = agentData.status && (
                            agentData.status.includes("MISSION") || 
                            agentData.status.includes("REINFORCING") || 
                            agentData.status.includes("INJECTING") || 
                            agentData.status.includes("Building") || 
                            agentData.status.includes("searching")
                        );

                        if (statusEl && agentData.status && agentData.status !== "Idle" && !agentData.status.includes("Idle")) {
                            if (cardEl) cardEl.classList.remove('inactive-agent');
                            statusEl.style.background = isActiveMission ? "rgba(239, 68, 68, 0.4)" : "rgba(239, 68, 68, 0.1)";
                            
                            let statusOverlay = statusEl.querySelector('.status-overlay');
                            if (isActiveMission) {
                                if (!statusOverlay) {
                                    statusOverlay = document.createElement('div');
                                    statusOverlay.className = 'status-overlay';
                                    statusOverlay.style.cssText = "position:absolute; top:0; left:0; width:100%; height:100%; background:inherit; display:flex; align-items:center; justify-content:center; border-radius:inherit; z-index:5;";
                                    statusEl.style.position = 'relative';
                                    statusEl.appendChild(statusOverlay);
                                }
                                statusOverlay.innerHTML = '<span style="font-weight:bold; color:#fff; animation: pulse 1s infinite; text-shadow: 0 0 5px #ef4444; font-size:0.6rem;">' + agentData.status + '</span>';
                                statusOverlay.style.display = 'flex';
                            } else if (statusOverlay) {
                                statusOverlay.style.display = 'none';
                            }

                            document.body.style.boxShadow = "inset 0 0 120px rgba(239, 68, 68, 0.15)";
                            const isInjecting = agentData.status && (agentData.status.includes("INJECTING") || agentData.status.includes("Building"));
                            if (isInjecting) {
                                const now = Date.now();
                                if (!window._lastSkywalkerFire || (now - window._lastSkywalkerFire > 500)) {
                                    triggerSkywalkerLaserStorm(agentData.pos); 
                                    window._lastSkywalkerFire = now;
                                }
                            }
                        } else if (statusEl) {
                            const statusOverlay = statusEl.querySelector('.status-overlay');
                            if (statusOverlay) statusOverlay.style.display = 'none';
                            if (cardEl) cardEl.classList.add('inactive-agent');
                            statusEl.style.background = "rgba(239, 68, 68, 0.1)";
                            document.body.style.boxShadow = "none";
                        }
                    }
                    if (id === 'AG-001') {
                        const currentThreats = agentData.threats_blocked_session || 0;
                        const ins = document.getElementById('val-smith-inspections'); if(ins) ins.innerText = agentData.inspections_session || 0;
                        const thr = document.getElementById('val-smith-threats'); if(thr) thr.innerText = currentThreats;

                        if (currentThreats > (lastAgentStates['AG-001-threats'] || 0)) {
                            showHologram('SMITH', 'msg_smith_threat');
                            lastAgentStates['AG-001-threats'] = currentThreats;
                            
                            if (!window.smithLightningTime) window.smithLightningTime = {};
                            Object.keys(smithFleetGroups).forEach(pid => {
                                window.smithLightningTime[pid] = 900; 
                            });
                        }
                        
                        const logContainer = document.getElementById('smith-security-container');
                        const threatsCounter = document.getElementById('total-threats-count');
                        if (logContainer && agentData.security_logs) {
                            if (threatsCounter) threatsCounter.innerText = agentData.threats_blocked_session || 0;
                            if (agentData.security_logs.length > 0) {
                                logContainer.innerHTML = agentData.security_logs.map(l => {
                                    return '<div style="padding: 8px 0; border-bottom: 1px solid rgba(255,255,255,0.05); animation: fadeIn 0.5s;">' +
                                        '<div style="display: flex; justify-content: space-between; margin-bottom: 2px;">' +
                                            '<span style="color: #ef4444; font-weight: bold;">[' + l.type + ']</span>' +
                                            '<span style="color: #4ade80;">STATUS: ' + l.status + '</span>' +
                                        '</div>' +
                                        '<div style="color: #fff; opacity: 0.8;">' + l.description + '</div>' +
                                        '<div style="display: flex; gap: 15px; margin-top: 2px; font-size: 0.6rem; opacity: 0.6;">' +
                                            '<span>SRC: ' + l.ip + '</span>' +
                                            '<span>TIME: ' + l.timestamp + '</span>' +
                                            '<span style="color: #3b82f6;">DEFENSE: ' + l.countermeasure + '</span>' +
                                        '</div>' +
                                    '</div>';
                                }).join('');
                            }
                        }

                        const fleet = agentData.fleet || {};
                        const now = Date.now();
                        
                        for (const pid in fleet) {
                            const sData = fleet[pid];
                            smithTargetPositions[pid] = new THREE.Vector3(
                                sData.pos.x * exp,
                                sData.pos.y * exp,
                                sData.pos.z * exp
                            );
                            
                            const group = smithFleetGroups[pid];
                            if (group) {
                                const isInspecting = sData.status && sData.status.includes("Inspecting");
                                const isThreatened = (now / 1000 - (agentData.last_threat || 0)) < 45;

                                if (isInspecting || isThreatened) {
                                    const targetWh = window.meshWormholes[pid];
                                    if (targetWh && targetWh.group) {
                                        if (!window["_lastSmithScan_" + pid] || (now - window["_lastSmithScan_" + pid] > 100)) {
                                            spawnSmithScannerRays(group, targetWh.group.position, isThreatened ? 0xef4444 : 0x00ff00);
                                            window["_lastSmithScan_" + pid] = now;
                                        }
                                        if (isThreatened) {
                                            if (!window["_lastSmithFire_" + pid] || (now - window["_lastSmithFire_" + pid] > 250)) {
                                                spawnSmithLightning(group, targetWh.group.position, true); 
                                                window["_lastSmithFire_" + pid] = now;
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                    if (id === 'NC-001') {
                        const r = document.getElementById('val-compressor-ratio'); 
                        if(r) r.innerText = agentData.is_training ? "TRAINING" : (agentData.compression_ratio || "0%");
                        const n = document.getElementById('val-compressor-nodes'); 
                        if(n) n.innerText = agentData.optimized_nodes_session || 0;

                        const progCont = document.getElementById('nic-progress-container');
                        const progBar = document.getElementById('nic-progress-bar');
                        if (progCont && progBar) {
                            if (agentData.is_training) {
                                progCont.style.display = 'block';
                                progBar.style.width = (agentData.training_progress || 0) + '%';
                            } else {
                                progCont.style.display = 'none';
                            }
                        }
                    }
                    if (id === 'R2-D2') {
                        const org = document.getElementById('val-r2d2-organized'); if(org) org.innerText = agentData.organized_session || 0;
                        const gal = document.getElementById('val-r2d2-galaxies'); 
                        if(gal) {
                            const newGals = agentData.galaxies_session || 0;
                            if (newGals > parseInt(gal.innerText || "0")) {
                                showHologram('JABBA_LAUGH', 'msg_jabba_nodes', { n: agentData.nodes_organized_session || 0 });
                            }
                            gal.innerText = newGals;
                        }
                        
                        if (r2d2Group) {
                            r2d2TargetPos.set(agentData.pos.x * exp, agentData.pos.y * exp, agentData.pos.z * exp);
                            r2d2Group.userData.isOperating = agentData.is_operating || false;
                        }

                        const cardEl = document.getElementById('r2-d2-hud-icon');
                        const isWorking = agentData.status && !agentData.status.includes("Idle");
                        if (cardEl) {
                            if (isWorking) cardEl.classList.remove('inactive-agent');
                            else cardEl.classList.add('inactive-agent');
                        }

                                                if (agentData.pos) {
                            r2d2TargetPos.set(agentData.pos.x * exp, agentData.pos.y * exp, agentData.pos.z * exp);
                        }

                        if (agentData.status && agentData.status !== (lastAgentStates[id] || "")) {
                            if (agentData.status.includes("GROUPING")) {
                                showHologram('R2D2', 'msg_r2d2_grouping');
                            } else if (agentData.status.includes("AUDIT")) {
                                log("R2-D2 Status: " + agentData.status, "#3b82f6");
                                showHologram('R2D2', 'msg_r2d2_audit');
                            }
                            lastAgentStates[id] = agentData.status;
                        }
                    }

                    // 🛰️ FS-77 SKY-WALKER
                    if (id.includes('FS-77') || agentData.identity === 'FS-77 SKY-WALKER') {
                        skywalkerTargetPos.set(agentData.pos.x * exp, agentData.pos.y * exp, agentData.pos.z * exp);
                        skywalkerGroup.userData.status = agentData.status || "Patrolling";
                        const h = document.getElementById('val-skywalker-hits'); if(h) h.innerText = agentData.total_hits || 0;
                    }

                    // 🌌 YO-001 YODA
                    if (id.includes('YO-001') || agentData.identity === 'YO-001 YODA-FILE-SEARCHER') {
                        yodaTargetPos.set(agentData.pos.x * exp, agentData.pos.y * exp, agentData.pos.z * exp);
                        yodaGroup.userData.status = agentData.status || "Searching";
                        if (agentData.is_shooting) {
                            yodaGroup.userData.laser = true;
                            yodaGroup.userData.laserTarget = agentData.target_pos;
                        } else {
                            yodaGroup.userData.laser = false;
                        }
                    }

                    // ⚔️ DN-099 MANDALORIAN
                    if (id.includes('DN-099') || agentData.identity === 'DN-099 MANDALORIAN') {
                        mandalorianTargetPos.set(agentData.pos.x * exp, agentData.pos.y * exp, agentData.pos.z * exp);
                        mandalorianGroup.userData.status = agentData.status || "Herding";
                        mandalorianGroup.userData.laserTarget = agentData.target_pos;
                    }

                    // [v12.0] GENERIC HANDLER for Custom Forged Agents (CU-)
                    if (id.startsWith('CU-')) {
                        const valEl = document.getElementById(`val-${id.toLowerCase()}-hud-icon`);
                        if (valEl) {
                            // Map typical counters
                            const val = agentData.processed_session || agentData.crafted_session || agentData.found_session || 0;
                            valEl.innerText = val;
                        }
                    }
                }
            }
        }

        if (d.lab && d.lab.blackboard && d.lab.blackboard.length > 0) {
            const lastSig = d.lab.blackboard.slice(-1)[0];
            const sType = String(lastSig.signal_type || "").toLowerCase();
            if (sType.includes("mission") || sType.includes("system")) {
                const msg = lastSig.msg || "";
                if (msg.includes("[") && msg.includes("%]")) {
                    if (!isEvolving) {
                        showHologram('KIRBY', 'msg_kirby_evolution');
                    }
                    isEvolving = true;
                    const match = msg.match(/\[(\d+)-(\d+)%\]/);
                    if (match) { 
                        evolutionProgress = parseInt(match[2]); 
                        evolutionStep = msg.split("[")[0].trim(); 
                        if (typeof updateEvolutionHUD === 'function') updateEvolutionHUD(); 
                    }
                } else if (msg.includes("COMPLETE") || msg.includes("CONVALIDATE")) {
                    isEvolving = false; 
                    if (typeof refreshVaultState === 'function') refreshVaultState();
                }
            }
        }

        if (d.lab && d.lab.court_actions) {
            const courtList = document.getElementById('court-verdicts-list');
            const activeTab = document.querySelector('.settings-tab.active');
            if (courtList && activeTab && activeTab.id === 'tab-court') {
                if (typeof window.renderCourtVerdicts === 'function') window.renderCourtVerdicts(d.lab.court_actions);
            }
        }
                    if (d.swarm_settings) {
            const s = d.swarm_settings;
            const toggle = document.getElementById('autonomous-court-toggle');
            if (toggle && !toggle.matches(':focus')) toggle.checked = s.autonomous_court;
            
            // Populate and Sync Judge Selects
            ['court-judge-1', 'court-judge-2', 'court-judge-3'].forEach(id => {
                const sel = document.getElementById(id);
                if (sel) {
                    // Populate if empty
                    if (sel.options.length === 0) {
                        // Always provide "-" as the first option
                        const optNone = document.createElement('option');
                        optNone.value = "-"; optNone.innerText = "-";
                        sel.appendChild(optNone);

                        if (installedModels && installedModels.length > 0) {
                            installedModels.forEach(m => {
                                const opt = document.createElement('option');
                                opt.value = m.name; opt.innerText = m.name;
                                sel.appendChild(opt);
                            });
                        }
                    }
                    // Sync value if not being interacted with
                    const serverVal = s[id.replace(/-/g, '_')];
                    if (serverVal && !sel.matches(':focus')) {
                        sel.value = serverVal;
                    }
                }
            });
        }
        if (d.system) {
            const s = d.system;
            const ramFill = document.getElementById('ram-usage-fill');
            const ramText = document.getElementById('ram-usage-text');
            if (ramFill && s.ram) {
                ramFill.style.width = s.ram.used + '%';
                if (ramText) ramText.innerText = `${s.ram.used.toFixed(1)}% / ${(s.ram.total / (1024**3)).toFixed(1)} GB`;
            }
            const cpuGrid = document.getElementById('cpu-core-grid');
            if (cpuGrid && s.cpu && s.cpu.cores) {
                if (cpuGrid.children.length !== s.cpu.cores.length) {
                    cpuGrid.innerHTML = s.cpu.cores.map((_, i) => `<div id="cpu-core-${i}" style="height:30px; background:rgba(255,255,255,0.05); border-radius:4px; border:1px solid rgba(255,255,255,0.05); position:relative; overflow:hidden;"><div class="fill" style="position:absolute; bottom:0; left:0; width:100%; height:0%; background:#3b82f6; transition:height 0.3s;"></div><span style="position:absolute; top:2px; left:2px; font-size:0.4rem; color:rgba(255,255,255,0.3);">C${i}</span></div>`).join('');
                }
                s.cpu.cores.forEach((p, i) => {
                    const fill = cpuGrid.querySelector(`#cpu-core-${i} .fill`);
                    if (fill) {
                        fill.style.height = p + '%';
                        fill.style.background = p > 80 ? '#ef4444' : p > 50 ? '#f59e0b' : '#3b82f6';
                    }
                });
            }
            const dna = document.getElementById('hardware-dna-trace');
            if (dna && s.hardware_dna) dna.innerText = s.hardware_dna;
            
            const engineList = document.getElementById('active-engines-list');
            if (engineList && s.active_engines) {
                engineList.innerHTML = s.active_engines.map(eng => `
                    <div style="display: flex; justify-content: space-between; align-items: center; background: rgba(255,255,255,0.03); padding: 8px 12px; border-radius: 8px; border-left: 3px solid #10b981;">
                        <div style="display: flex; flex-direction: column;">
                            <span style="font-size: 0.8rem; color: #fff; font-weight: 800;">${eng.name}</span>
                            <span style="font-size: 0.55rem; color: #10b981; font-weight: 700; letter-spacing: 1px;">${eng.resource}</span>
                        </div>
                        <div style="font-size: 0.75rem; color: #fff; font-family: 'JetBrains Mono'; font-weight: 900;">${eng.size}</div>
                    </div>
                `).join('');
            }
            
            const mpsVal = document.getElementById('mps-pressure-val');
            if (mpsVal && s.mps_pressure) mpsVal.innerText = `MPS: ${s.mps_pressure}`;
        }
        if (d.nodes_count && d.edges_count && window.densityChart) {
            const density = (d.edges_count / (d.nodes_count || 1)).toFixed(2);
            const timeLabel = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
            window.densityChart.data.labels.push(timeLabel);
            window.densityChart.data.datasets[0].data.push(parseFloat(density));
            if (window.densityChart.data.labels.length > 20) {
                window.densityChart.data.labels.shift();
                window.densityChart.data.datasets[0].data.shift();
            }
            window.densityChart.update('none');
        }
        if (d.nodes_count && window.growthChart) {
            const timeLabel = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
            window.growthChart.data.labels.push(timeLabel);
            window.growthChart.data.datasets[0].data.push(d.nodes_count);
            if (window.growthChart.data.labels.length > 20) {
                window.growthChart.data.labels.shift();
                window.growthChart.data.datasets[0].data.shift();
            }
            window.growthChart.update('none');
        }
    };
}

/**
 * 🔗 [v12.7] SOVEREIGN EVIDENCE BINDING
 * Consente la verifica attiva dei nodi citati nei report SITREP.
 */
window.bindEvidenceLinks = (containerId) => {
    const container = document.getElementById(containerId);
    if (!container) return;

    // Pattern: [node_...] o [ID: node_...]
    const nodePattern = /\[(node_[a-f0-9-]+)\]/gi;
    
    // Trova tutti i nodi di testo nel container e sostituisci il pattern con span cliccabili
    const walker = document.createTreeWalker(container, NodeFilter.SHOW_TEXT, null, false);
    let textNode;
    const nodesToReplace = [];

    while (textNode = walker.nextNode()) {
        if (textNode.nodeValue.match(nodePattern)) {
            nodesToReplace.push(textNode);
        }
    }

    nodesToReplace.forEach(node => {
        const span = document.createElement('span');
        span.innerHTML = node.nodeValue.replace(nodePattern, (match, id) => {
            return `<span class="evidence-tag" onclick="window.selectNode('${id}')" title="Clicca per verificare la fonte nel Vault">${match}</span>`;
        });
        node.parentNode.replaceChild(span, node);
    });

    log(`🔗 [Traceability] Binding evidence links in ${containerId}`, "#10b981");
};

// Global click listener for any dynamically added [node_id] text
document.addEventListener('click', (e) => {
    if (e.target && e.target.classList.contains('evidence-tag')) {
        // Handled by inline onclick, but we can add telemetry here
        if (typeof aegis_bus !== 'undefined') {
            // Future: emit client-side telemetry to Aegis
        }
    }
});

// CSS Injection for Evidence Tags
const style = document.createElement('style');
style.textContent = `
    .evidence-tag {
        color: #3b82f6;
        background: rgba(59, 130, 246, 0.1);
        border: 1px solid rgba(59, 130, 246, 0.3);
        padding: 2px 6px;
        border-radius: 4px;
        cursor: pointer;
        font-family: 'JetBrains Mono', monospace;
        font-weight: 800;
        font-size: 0.8em;
        transition: all 0.2s;
        display: inline-block;
        margin: 0 2px;
    }
    .evidence-tag:hover {
        background: rgba(59, 130, 246, 0.2);
        border-color: #3b82f6;
        box-shadow: 0 0 10px rgba(59, 130, 246, 0.3);
        transform: translateY(-1px);
    }
`;
document.head.appendChild(style);
