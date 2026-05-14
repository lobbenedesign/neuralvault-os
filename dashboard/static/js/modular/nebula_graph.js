/**
 * 🌌 NEURALVAULT NEBULA GRAPH (v11.0: Unlimited Density Edition)
 */
let lastVaultPoints = null;
let currentDensity = 1.0;

window.updateNeuralDensity = function(val) {
    currentDensity = val / 100;
    const el = document.getElementById('density-val');
    if (el) el.innerText = val + '%';
    // Re-render immediately to show changes
    if (lastVaultPoints) updateThreeScene(lastVaultPoints, null);
};

function updateThreeScene(points, links = null) {
    if (!pointsMesh || !neuralLinks) return;
    vaultPoints = points || [];
    lastVaultPoints = points;
    if (links !== null) lastNeuralLinks = links;
    const currentLinks = links !== null ? links : lastNeuralLinks;
    let renderedNodeCount = 0;
    const MAX_RENDER_NODES = 80000; // 🛡️ [v11.1] Safety Cap
    const renderedNodesMap = new Set(); // Registra nodi attivi per archi
    const pos = pointsMesh.geometry.attributes.position.array;
    const col = pointsMesh.geometry.attributes.color.array;
    const pastelPalette = ["#FFB7B2", "#FFDAC1", "#E2F0CB", "#B5EAD7", "#C7CEEA", "#FF9AA2", "#B2E2F2", "#D5AAFF"];
    const isLight = document.body.classList.contains('light-theme');

    for (let i = 0; i < vaultPoints.length; i++) {
        if (renderedNodeCount >= MAX_RENDER_NODES) break;
        
        const p = vaultPoints[i];
        
        // 🚀 [v11.0] Dynamic Neural Density Filtering
        const density = currentDensity;
        const nodeHash = (p.id.charCodeAt(0) + i) % 100;
        if (nodeHash > (density * 100)) continue; 

        renderedNodesMap.add(p.id);

        const exp = nebulaExpansionFactor || 1.0;
        pos[renderedNodeCount*3] = (p.x || 0) * exp; 
        pos[renderedNodeCount*3+1] = (p.y || 0) * exp; 
        pos[renderedNodeCount*3+2] = (p.z || 0) * exp;
        
        let displayColor;
        if (heatmapMode && currentHeatmap[p.id] !== undefined) {
            const temp = currentHeatmap[p.id]; 
            const r = Math.floor(temp * 255);
            const b = Math.floor((1 - temp) * 255);
            displayColor = `rgb(${r}, 50, ${b})`;
        } else if (window._showPartitions && p.partition_id !== undefined) {
             const partitionColors = ["#ef4444", "#3b82f6", "#10b981", "#facc15", "#a855f7", "#ec4899", "#06b6d4", "#f97316"];
             displayColor = partitionColors[p.partition_id % partitionColors.length];
        } else {
            displayColor = p.color || "#06b6d4";
            if (isLight && (displayColor === "#06b6d4" || displayColor === "#ffffff")) {
                displayColor = pastelPalette[i % pastelPalette.length];
            }
            if (!clusterFocus) {
                displayColor = isLight ? "#94a3b8" : "#475569";
            }
        }
        const opacity = p.opacity !== undefined ? p.opacity : 1.0;
        const color = new THREE.Color(displayColor);
        col[renderedNodeCount*3] = color.r * opacity; 
        col[renderedNodeCount*3+1] = color.g * opacity; 
        col[renderedNodeCount*3+2] = color.b * opacity;
        
        renderedNodeCount++;
    }
    pointsMesh.geometry.attributes.position.needsUpdate = true;
    pointsMesh.geometry.attributes.color.needsUpdate = true;
    renderClusters(vaultPoints);
    const drawCount = Math.floor(renderedNodeCount * timeTravelFactor);
    pointsMesh.geometry.setDrawRange(0, drawCount);

    // [v4.1] Optimized Multimodal Rendering: Filter first, then spawn
    multimodalGroup.clear();
    const mediaNodes = vaultPoints.filter(p => p.media_type && multimodalTextures[p.media_type]).slice(0, 100); // Cap sprites
    mediaNodes.forEach(p => {
        const material = new THREE.SpriteMaterial({ 
            map: multimodalTextures[p.media_type],
            transparent: true,
            opacity: 0.9
        });
        const sprite = new THREE.Sprite(material);
        const exp = nebulaExpansionFactor || 1.0;
        sprite.scale.set(60000, 60000, 1);
        sprite.position.set(p.x * exp, p.y * exp, p.z * exp);
        sprite.userData = { id: p.id, type: 'multimodal', media: p.media_type };
        multimodalGroup.add(sprite);
    });

    // 1. Creiamo una mappa rapida dei punti correnti sullo schermo
    const ptsMap = {};
    vaultPoints.forEach(p => ptsMap[p.id] = p);

    // 2. [v8.4] BATCH LINK RENDERING (LineSegments) - Ultra High Performance
    if (layersVisibility.edges && currentLinks && currentLinks.length > 0 && typeof linksMesh !== 'undefined') {
        const linkPos = linksMesh.geometry.attributes.position.array;
        const linkCol = linksMesh.geometry.attributes.color.array;
        const maxBatch = currentLinks.length;
        let linkIdx = 0;
        const galaxyLinkCounts = {}; // Track links per galaxy

        for (let i = 0; i < maxBatch; i++) {
            const l = currentLinks[i];
            
            // 🛑 Sicurezza Apici: Renderizza l'arco SOLO se entrambi i nodi sono visibili
            if (!renderedNodesMap.has(l.source) || !renderedNodesMap.has(l.target)) {
                continue;
            }

            const src = ptsMap[l.source];
            const dst = ptsMap[l.target];
            
            if (src && dst) {
                const rel = (l.relation || "").toLowerCase();
                const srcIsGalaxy = (src.is_galaxy === true || (src.metadata && src.metadata.is_galaxy === true));
                const dstIsGalaxy = (dst.is_galaxy === true || (dst.metadata && dst.metadata.is_galaxy === true));
                const isInterGalactic = (srcIsGalaxy !== dstIsGalaxy);
                
                if (isInterGalactic) {
                    const galNode = srcIsGalaxy ? src : dst;
                    const galName = (galNode.metadata && galNode.metadata.galaxy_name) ? galNode.metadata.galaxy_name : (galNode.cluster_id || 'unknown_galaxy');
                    
                    if (!galaxyLinkCounts[galName]) galaxyLinkCounts[galName] = 0;
                    
                    // [v10.8] Strict Single Anchor: Only 1 link between Mother Nebula and each External Galaxy
                    if (galaxyLinkCounts[galName] >= 1) {
                        continue; 
                    }
                    galaxyLinkCounts[galName]++;
                } else {
                    // [v10.8] Strict 10% Filter for all other standard edges
                    const isSpecial = (rel.includes('anchor') || rel.includes('laser') || rel.includes('bridge') || rel.includes('causes'));
                    if (!isSpecial) {
                        const hash = (src.id.charCodeAt(0) + dst.id.charCodeAt(i % 10) + i) % 100;
                        if (hash > 10) continue; // Show only 10% of standard synapses
                    }
                }

                const exp = nebulaExpansionFactor || 1.0;
                // Source Point
                linkPos[linkIdx*6] = src.x * exp; linkPos[linkIdx*6+1] = src.y * exp; linkPos[linkIdx*6+2] = src.z * exp;
                // Destination Point
                linkPos[linkIdx*6+3] = dst.x * exp; linkPos[linkIdx*6+4] = dst.y * exp; linkPos[linkIdx*6+5] = dst.z * exp;
                
                // Colors based on relation
                const isSpark = l.is_aura === true; 
                const isLightTheme = document.body.classList.contains('light-theme');
                
                let r=isLightTheme ? 0.25 : 0.15, g=r, b=r;
                let r2=r, g2=g, b2=b;

                if (isSpark) { 
                    r=1.0; g=1.0; b=1.0; r2=1.0; g2=1.0; b2=1.0;
                } else if (rel === 'skywalker_anchor') { 
                    r=1.0; g=0.1; b=0.0; r2=1.0; g2=1.0; b2=0.0;
                } else if (rel === 'yoda_anchor' || rel === 'reflection_anchor') { 
                    r=0.0; g=1.0; b=0.2; r2=1.0; g2=1.0; b2=0.0;
                } else if (rel === 'galaxy_tether' || rel === 'super_galaxy') { 
                    r=0.0; g=0.0; b=0.0; r2=1.0; g2=0.8; b2=0.0;
                } else if (rel === 'causes') { r=1.0; g=0.3; b=0.0; r2=r; g2=g; b2=b; }
                else if (rel === 'prevents') { r=0.9; g=0.2; b=0.2; r2=r; g2=g; b2=b; }
                else if (rel === 'requires') { r=0.2; g=0.5; b=1.0; r2=r; g2=g; b2=b; }
                else if (rel === 'synapse') { 
                    r=isLightTheme ? 0.15 : 0.08; g=r; b=r;
                    r2=r; g2=g; b2=b;
                } else if (rel === 'galaxy_internal') {
                    if (isLightTheme) { r=0.25; g=0.25; b=0.25; } 
                    else { r=0.15; g=0.15; b=0.15; }
                    r2=r; g2=g; b2=b;
                }

                linkCol[linkIdx*6] = r; linkCol[linkIdx*6+1] = g; linkCol[linkIdx*6+2] = b;
                linkCol[linkIdx*6+3] = r2; linkCol[linkIdx*6+4] = g2; linkCol[linkIdx*6+5] = b2;
                
                linkIdx++;
            }
        }
        linksMesh.geometry.setDrawRange(0, linkIdx * 2);
        linksMesh.geometry.attributes.position.needsUpdate = true;
        linksMesh.geometry.attributes.color.needsUpdate = true;
    } else if (typeof linksMesh !== 'undefined') {
        linksMesh.geometry.setDrawRange(0, 0);
    }
    
    // Log success to terminal once the nebula is loaded
    if (!window._nebulaLoadedLogged && renderedNodeCount > 1000) {
        log(`La Nebula è caricata e renderizzata con successo nella Dashboard! (Nodi visibili: ${renderedNodeCount})`, "#00ff00");
        window._nebulaLoadedLogged = true;
    }
}

window.refreshIgnoranceGaps = async () => {
    if (typeof ignoranceGroup === 'undefined' || !scene) return;
    try {
        const r = await fetch('/api/metacognition/gaps', { headers: { 'X-API-KEY': VAULT_KEY }});
        const d = await r.json();
        
        ignoranceGroup.clear();
        if (d.status === 'success' && d.gaps) {
            d.gaps.forEach(gap => {
                const geo = new THREE.SphereGeometry(gap.radius, 32, 32);
                const mat = new THREE.MeshBasicMaterial({ 
                    color: 0x94a3b8, 
                    transparent: true, 
                    opacity: 0.15,
                    wireframe: true 
                });
                const sphere = new THREE.Mesh(geo, mat);
                const exp = window.nebulaExpansionFactor || 1.0;
                sphere.position.set(gap.x * exp, gap.y * exp, gap.z * exp);
                
                sphere.userData = { 
                    id: gap.id, 
                    isGap: true, 
                    context: gap.context, 
                    missing: gap.missing 
                };
                ignoranceGroup.add(sphere);
                
                const canvas = document.createElement('canvas');
                canvas.width = 256; canvas.height = 64;
                const ctx = canvas.getContext('2d');
                ctx.fillStyle = "#94a3b8";
                ctx.font = "bold 24px 'JetBrains Mono'";
                ctx.fillText("TERRA INCOGNITA", 10, 40);
                const tex = new THREE.CanvasTexture(canvas);
                const spriteMat = new THREE.SpriteMaterial({ map: tex, transparent: true, opacity: 0.6 });
                const sprite = new THREE.Sprite(spriteMat);
                sprite.position.set(gap.x * exp, gap.y * exp + gap.radius, gap.z * exp);
                sprite.scale.set(gap.radius * 2, gap.radius * 0.5, 1);
                ignoranceGroup.add(sprite);
            });
        }
    } catch(e) { console.error("Metacognition Error:", e); }
};

function renderClusters(points) {
    if (!clusterNodesGroup) return;
    const isLight = document.body.classList.contains('light-theme');
    clusterNodesGroup.clear();
    if (!clusterFocus) return;
    const clusters = {};
    points.forEach(p => {
        const theme = p.theme || 'default';
        if (theme === 'default') return;
        if (!clusters[theme]) clusters[theme] = { x:0, y:0, z:0, count:0, color: p.color };
        clusters[theme].x += p.x;
        clusters[theme].y += p.y;
        clusters[theme].z += p.z;
        clusters[theme].count++;
    });
    for (const theme in clusters) {
        const c = clusters[theme];
        const density = currentDensity;
        const clusterHash = (theme.charCodeAt(0) + theme.length) % 100;
        if (clusterHash > (density * 100)) continue; // Filter clusters too
        if (c.count > 3) {
            const avgX = c.x / c.count;
            const avgY = c.y / c.count;
            const avgZ = c.z / c.count;
            const size = 16000;
            const geo = new THREE.CylinderGeometry(size, size, 4000, 6);
            const mat = new THREE.MeshPhongMaterial({
                color: c.color,
                transparent: true,
                opacity: 0.9,
                shininess: 100
            });
            const hex = new THREE.Mesh(geo, mat);
            
            // Assegniamo l'ID di un nodo rappresentativo al cluster per renderlo ispezionabile!
            const sampleNode = points.find(p => (p.theme || 'default') === theme);
            if (sampleNode) hex.userData = { id: sampleNode.id, isCluster: true };

            hex.rotation.x = Math.PI / 2;
            hex.onBeforeRender = (renderer, scene, camera, geometry, material) => {
                const clock = Date.now() * 0.002;
                const pulse = 0.5 + Math.sin(clock * 2) * 0.5;
                material.emissive.set(c.color);
                material.emissiveIntensity = 0.2 + pulse * 0.3;
            };
            const exp = nebulaExpansionFactor || 1.0;
            hex.position.set(avgX * exp, avgY * exp, avgZ * exp);
            clusterNodesGroup.add(hex);
        }
    }
}

function updateEvolutionHUD() {
    const hud = document.getElementById('evolution-telemetry-hud');
    const bar = document.getElementById('evolution-progress-bar');
    const txt = document.getElementById('evolution-status-text');
    if (!hud || !bar || !txt) return;
    if (isEvolving) {
        hud.style.display = 'flex';
        bar.style.width = `${evolutionProgress}%`;
        txt.innerText = evolutionStep;
    } else {
        bar.style.width = `100%`;
        txt.innerText = "Realignment Stabilized";
        setTimeout(() => { if(!isEvolving) hud.style.display = 'none'; }, 3000);
    }
}

window.exportAuditLedger = function(format) {
    const table = document.getElementById('audit-ledger-body');
    if (!table) return;
    const rows = Array.from(table.rows);
    let content = "";
    let filename = `NeuralVault_Audit_${new Date().toISOString().slice(0,19).replace(/[:T]/g, '_')}.txt`;
    let type = "text/plain";
    if (format === 'json') {
        const data = rows.map(r => ({
            time: r.cells[0].innerText, agent: r.cells[1].innerText, action: r.cells[2].innerText,
            target: r.cells[3].innerText, reason: r.cells[4].innerText, savings: r.cells[5].innerText
        }));
        content = JSON.stringify(data, null, 2); filename = filename.replace('.txt', '.json'); type = "application/json";
    } else if (format === 'csv') {
        content = "TIMESTAMP,AGENTE,AZIONE,TARGET,MOTIVAZIONE,IMPATTO\n" + 
            rows.map(r => Array.from(r.cells).map(c => `"${c.innerText.replace(/"/g, '""')}"`).join(",")).join("\n");
        filename = filename.replace('.txt', '.csv'); type = "text/csv";
    } else {
        content = "--- NEURALVAULT AUDIT LEDGER ---\n\n" + 
            rows.map(r => `[${r.cells[0].innerText}] ${r.cells[1].innerText} -> ${r.cells[2].innerText}\n   Reason: ${r.cells[4].innerText}\n`).join("\n");
    }
    const blob = new Blob([content], { type: type });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a'); a.href = url; a.download = filename; a.click();
    if(document.getElementById('export-dropdown')) document.getElementById('export-dropdown').classList.add('hidden');
};

// 🌌 [v8.0] H-RAG Visual Feedback: Semantic Shockwave
window.triggerSemanticShockwave = function() {
    if (!window.scene) return;
    console.log("🌌 [H-RAG] SEMANTIC SHOCKWAVE TRIGGERED");
    if (window.log) window.log("🌌 [H-RAG] Semantic Shockwave: Re-aligning Conceptual Gravity...", "#00f2fe");

    const waveGeo = new THREE.TorusGeometry(100, 30, 16, 100);
    const waveMat = new THREE.MeshBasicMaterial({ 
        color: 0x00f2fe, 
        transparent: true, 
        opacity: 0.8,
        blending: THREE.AdditiveBlending 
    });
    const wave = new THREE.Mesh(waveGeo, waveMat);
    wave.rotation.x = Math.PI / 2;
    window.scene.add(wave);

    let scale = 1;
    function animateWave() {
        scale += 100;
        wave.scale.set(scale, scale, scale);
        wave.material.opacity -= 0.015;
        
        if (wave.material.opacity > 0) {
            requestAnimationFrame(animateWave);
        } else {
            window.scene.remove(wave);
            waveGeo.dispose();
            waveMat.dispose();
        }
    }
    animateWave();

// 🌪️ [v8.1] Node Shake & Galactic Re-alignment Effect
    if (window.pointsMesh && window.vaultPoints) {
        const originalY = window.pointsMesh.position.y;
        const exp = window.nebulaExpansionFactor || 1.0;
        
        // Calcoliamo i baricentri delle galassie (cluster) per la trazione
        const centers = {};
        window.vaultPoints.forEach(p => {
            const cid = p.cluster_id || 'default';
            if (!centers[cid]) centers[cid] = { x:0, y:0, z:0, count:0 };
            centers[cid].x += p.x * exp;
            centers[cid].y += p.y * exp;
            centers[cid].z += p.z * exp;
            centers[cid].count++;
        });
        Object.keys(centers).forEach(cid => {
            centers[cid].x /= centers[cid].count;
            centers[cid].y /= centers[cid].count;
            centers[cid].z /= centers[cid].count;
        });

        let frame = 0;
        const totalFrames = 120; // Animazione più lunga e fluida (2 secondi a 60fps)
        
        function animateGalacticGravity() {
            frame++;
            const progress = frame / totalFrames;
            const ease = 1 - Math.pow(1 - progress, 3); // Ease out cubic
            
            // 1. Shake verticale (decrescente)
            window.pointsMesh.position.y = originalY + Math.sin(frame * 0.5) * (30000 * (1 - progress));
            
            // 2. Trazione verso il centro della Galassia e Repulsione tra Galassie
            const posAttr = window.pointsMesh.geometry.attributes.position;
            const array = posAttr.array;
            
            for (let i = 0; i < Math.min(window.vaultPoints.length, 30000); i++) {
                const p = window.vaultPoints[i];
                const cid = p.cluster_id || 'default';
                const center = centers[cid];
                
                if (center) {
                    // Spostiamo i punti verso il loro centro galattico
                    const targetX = center.x + (p.x * exp - center.x) * 0.8; // Compressione interna
                    const targetY = center.y + (p.y * exp - center.y) * 0.8;
                    const targetZ = center.z + (p.z * exp - center.z) * 0.8;
                    
                    // Applichiamo una spinta centrifuga alle galassie (repulsione esterna)
                    // Più il centro è lontano dall'origine, più lo spingiamo fuori
                    const repulsionX = center.x * 1.2; 
                    const repulsionY = center.y * 1.2;
                    const repulsionZ = center.z * 1.2;

                    // Interpolazione dinamica
                    const finalX = targetX + (repulsionX - center.x) * ease;
                    const finalY = targetY + (repulsionY - center.y) * ease;
                    const finalZ = targetZ + (repulsionZ - center.z) * ease;

                    array[i*3] += (finalX - array[i*3]) * 0.05 * (1-progress);
                    array[i*3+1] += (finalY - array[i*3+1]) * 0.05 * (1-progress);
                    array[i*3+2] += (finalZ - array[i*3+2]) * 0.05 * (1-progress);
                }
            }
            posAttr.needsUpdate = true;
            
            if (frame < totalFrames) requestAnimationFrame(animateGalacticGravity);
            else window.pointsMesh.position.y = originalY;
        }
        animateGalacticGravity();
    }
};

// 🧠 [v8.0] H-RAG Visual Feedback: Synaptic Sparks
window.triggerSynapticSparks = function() {
    if (!window.scene || !window.lastNeuralLinks || !window.vaultPoints) return;
    console.log("🧠 [H-RAG] SYNAPTIC SPARKS TRIGGERED");
    if (window.log) window.log("🧠 [H-RAG] Synaptic Sparks: Archivist is summarizing cluster intelligence...", "#a855f7");

    const ptsMap = {};
    window.vaultPoints.forEach(p => ptsMap[p.id] = p);
    
    // Prendiamo un campione casuale di link per le scintille
    const links = window.lastNeuralLinks.slice(0, 100).filter(() => Math.random() > 0.7);
    const exp = window.nebulaExpansionFactor || 1.0;

    links.forEach(l => {
        const src = ptsMap[l.source];
        const dst = ptsMap[l.target];
        if (src && dst) {
            const start = new THREE.Vector3(src.x * exp, src.y * exp, src.z * exp);
            const end = new THREE.Vector3(dst.x * exp, dst.y * exp, dst.z * exp);
            
            const sparkGeo = new THREE.SphereGeometry(3000, 8, 8); 
            const sparkMat = new THREE.MeshBasicMaterial({ 
                color: 0xa855f7,
                transparent: true,
                opacity: 1.0,
                blending: THREE.AdditiveBlending
            });
            const spark = new THREE.Mesh(sparkGeo, sparkMat);
            window.scene.add(spark);

            let progress = 0;
            const speed = 0.01 + Math.random() * 0.03;
            function animateSpark() {
                progress += speed;
                spark.position.lerpVectors(start, end, progress);
                spark.material.opacity = Math.sin(progress * Math.PI); // Fade in-out
                
                if (progress < 1) {
                    requestAnimationFrame(animateSpark);
                } else {
                    window.scene.remove(spark);
                    sparkGeo.dispose();
                    sparkMat.dispose();
                }
            }
            animateSpark();
        }
    });
};
// --- 🕸️ MESH WORMHOLE VISUALIZATION (v6.0) ---
class MeshWormhole {
    constructor(peer) {
        this.peerId = peer.id;
        this.url = peer.url;
        this.group = new THREE.Group();
        this.group.visible = layersVisibility.wormholes !== undefined ? layersVisibility.wormholes : true;
        this.initVisuals(peer);
        window.scene.add(this.group);
        if (typeof log === 'function') log(`🕸️ [Bridge] Extradimensional Tunnel Active: ${this.peerId.substring(0,8)}`, (peer && peer.isDemo) ? "#a855f7" : "#3b82f6");
    }

    initVisuals(peer) {
        // 📍 Posizionamento DETERMINISTICO (v7.5) - Sincronizzato con Agent SMITH
        const hashCode = (s) => {
            let h = 0;
            for(let i = 0; i < s.length; i++) h = Math.imul(31, h) + s.charCodeAt(i) | 0;
            return Math.abs(h);
        };
        const h_val = hashCode(this.peerId);
        
        const radius = 25000000 + (h_val % 1000000); // [v18.6] Expanded Deep Space Rim (25M units)
        const angle = (h_val % 360) * (Math.PI / 180);
        const x = Math.cos(angle) * radius;
        const z = Math.sin(angle) * radius;
        const y = 1000000 + (h_val % 500000 - 250000);
        
        this.basePos = new THREE.Vector3(x, y, z);
        this.group.position.copy(this.basePos);
        this.group.lookAt(0, 1000000, 0); 

        // 🎨 [v8.3] Spectral Identity (Unique Bicolor Gradient)
        const hue1 = (h_val % 360);
        const hue2 = (hue1 + 60) % 360; // Colore secondario (analogico/complementare)
        this.color1 = new THREE.Color(`hsl(${hue1}, 100%, 60%)`);
        this.color2 = new THREE.Color(`hsl(${hue2}, 100%, 50%)`);
        const colorHex1 = `#${this.color1.getHexString()}`;
        const colorHex2 = `#${this.color2.getHexString()}`;

        // 🌪️ Geometria Imbuto (Wormhole Bridge)
        const points = [];
        for (let i = 0; i <= 20; i++) {
            const t = i / 20;
            const r = 100000 + Math.pow(t - 1.0, 2) * 1600000; // Radii doubled (50k->100k, 800k->1.6M)
            points.push(new THREE.Vector2(r, (t - 0.5) * 2400000)); // Height doubled (1.2M->2.4M)
        }
        const funnelGeo = new THREE.LatheGeometry(points, 32);
        const funnelMat = new THREE.MeshPhongMaterial({
            color: this.color1,
            emissive: this.color2,
            emissiveIntensity: 0.8,
            transparent: true,
            opacity: 0.4,
            side: THREE.DoubleSide,
            wireframe: true
        });
        this.funnel = new THREE.Mesh(funnelGeo, funnelMat);
        this.funnel.rotation.x = -Math.PI / 2; 
        this.group.add(this.funnel);

        const sprite = createTextSprite(this.peerId.substring(0, 10), colorHex1);
        sprite.position.z = -1600000; // Position doubled (-800k->-1.6M)
        sprite.scale.set(1600000, 400000, 1); // Scale doubled (800k->1.6M, 200k->400k)
        this.group.add(sprite);

        const nebulaGeo = new THREE.BufferGeometry();
        const partCount = 800; // Aumentato per densità
        const posArr = new Float32Array(partCount * 3);
        const colArr = new Float32Array(partCount * 3); // Per vertex colors
        
        for(let i=0; i<partCount; i++) {
            // Posizione (Doubled radii and offset)
            const r = 400000 + Math.random() * 1000000;
            const a = Math.random() * Math.PI * 2;
            posArr[i*3] = Math.cos(a) * r;
            posArr[i*3+1] = Math.sin(a) * r;
            posArr[i*3+2] = -1600000 + (Math.random() - 0.5) * 800000; 
            
            // Colore (interpolazione casuale tra color1 e color2)
            const mix = Math.random();
            const r_col = this.color1.r * (1 - mix) + this.color2.r * mix;
            const g_col = this.color1.g * (1 - mix) + this.color2.g * mix;
            const b_col = this.color1.b * (1 - mix) + this.color2.b * mix;
            colArr[i*3] = r_col;
            colArr[i*3+1] = g_col;
            colArr[i*3+2] = b_col;
        }
        
        nebulaGeo.setAttribute('position', new THREE.BufferAttribute(posArr, 3));
        nebulaGeo.setAttribute('color', new THREE.BufferAttribute(colArr, 3));
        
        // Generazione Texture morbida per effetto gas (Premium Glow)
        const createSoftGlow = () => {
            const canvas = document.createElement('canvas');
            canvas.width = 64; canvas.height = 64;
            const ctx = canvas.getContext('2d');
            const grad = ctx.createRadialGradient(32,32,0, 32,32,32);
            grad.addColorStop(0, 'rgba(255,255,255,1)');
            grad.addColorStop(0.3, 'rgba(255,255,255,0.4)');
            grad.addColorStop(1, 'rgba(255,255,255,0)');
            ctx.fillStyle = grad;
            ctx.fillRect(0,0,64,64);
            const tex = new THREE.CanvasTexture(canvas);
            return tex;
        };

        const nebulaMat = new THREE.PointsMaterial({
            size: 280000, // Size doubled (140k->280k)
            map: createSoftGlow(),
            vertexColors: true, 
            transparent: true,
            opacity: 0.6,
            blending: THREE.AdditiveBlending,
            depthWrite: false
        });
        this.nebulaPoints = new THREE.Points(nebulaGeo, nebulaMat);
        this.group.add(this.nebulaPoints);

        // 🕸️ Archi e Apici
        // 🕸️ Archi connessi alla Nebula Madre (v17.7)
        const motherCenter = new THREE.Vector3(0, 1000000, 0);
        this.apices = [
            motherCenter.clone(),
            motherCenter.clone().add(new THREE.Vector3(200000, 0, 0)),
            motherCenter.clone().add(new THREE.Vector3(-200000, 0, 0)),
            motherCenter.clone().add(new THREE.Vector3(0, 200000, 0)),
            motherCenter.clone().add(new THREE.Vector3(0, -200000, 0)),
            motherCenter.clone().add(new THREE.Vector3(0, 0, 200000)),
            motherCenter.clone().add(new THREE.Vector3(0, 0, -200000))
        ];

        this.arcs = [];
        this.curves = [];
        this.apices.forEach(apex => {
            const start = new THREE.Vector3(0, 0, 600000);
            const end = apex.clone().sub(this.group.position);
            const quat = this.group.quaternion.clone().invert();
            end.applyQuaternion(quat);

            const mid = start.clone().lerp(end, 0.5);
            mid.x += (Math.random() - 0.5) * 1500000;

            const curve = new THREE.QuadraticBezierCurve3(start, mid, end);
            this.curves.push(curve);
            
            const points = curve.getPoints(40);
            const geo = new THREE.BufferGeometry().setFromPoints(points);
            const mat = new THREE.LineBasicMaterial({ color: this.color2, transparent: true, opacity: 0.2 });
            const arc = new THREE.Line(geo, mat);
            this.group.add(arc);
            this.arcs.push(arc);
        });

        const flowGeo = new THREE.BufferGeometry();
        this.flowCount = 80; 
        this.flowPositions = new Float32Array(this.flowCount * 3);
        this.flowProgress = new Float32Array(this.flowCount); 
        for(let i=0; i<this.flowCount; i++) {
            this.flowProgress[i] = Math.random();
        }
        flowGeo.setAttribute('position', new THREE.BufferAttribute(this.flowPositions, 3));
        const flowMat = new THREE.PointsMaterial({
            color: this.color1,
            size: 80000, // Size doubled (40k->80k)
            transparent: true,
            opacity: 1.0,
            blending: THREE.AdditiveBlending,
            depthWrite: false
        });
        this.flowSystem = new THREE.Points(flowGeo, flowMat);
        this.group.add(this.flowSystem);
    }

    update() {
        const time = Date.now() * 0.001;
        const exp = window.nebulaExpansionFactor || 1.0;
        const center = new THREE.Vector3(0, 1000000, 0);

        // 🔴 [v8.2] Skywalker Sovereign Laser Fire logic
        const isSkywalkerFiring = (this.agents && this.agents['FS-77'] && 
            (this.agents['FS-77'].status.startsWith("MISSION:") || 
             this.agents['FS-77'].status.startsWith("🚀") ||
             this.agents['FS-77'].status.startsWith("REINFORCING:") ||
             this.agents['FS-77'].status.startsWith("INJECTING:")));

        this.group.position.copy(this.basePos)
            .sub(center)
            .multiplyScalar(exp)
            .add(center);

        // Manteniamo l'orientamento radiale verso il centro (bocca rivolta al cubo)
        this.group.lookAt(center);

        if (this.nebulaPoints) {
            this.nebulaPoints.rotation.z += 0.01;
        }
        if (this.funnel) {
            this.funnel.rotation.y += 0.02;
            this.funnel.material.emissiveIntensity = 0.5 + Math.sin(time*3)*0.3;
        }

        // Ricalcolo archi per riflettere il movimento del wormhole rispetto al cubo fisso
        const quatInv = this.group.quaternion.clone().invert();
        this.curves.forEach((curve, idx) => {
            // 🔴 [v8.0] Skywalker Sovereign Laser Fire logic
            if (this.agents && this.agents['FS-77'] && this.agents['FS-77'].laser) {
                const now = Date.now();
                if (!this.lastSkywalkerShot) this.lastSkywalkerShot = 0;
                
                // Raffica quad-cannon: 1 proiettile ogni 125ms per un totale di 8 colpi/sec
                if (now - this.lastSkywalkerShot > 125) {
                    if (typeof triggerSkywalkerLaser === 'function') {
                        triggerSkywalkerLaser(this.agents['FS-77'], this);
                    }
                    this.lastSkywalkerShot = now;
                }
            } else if (this.agents && this.agents['FS-77'] && !this.agents['FS-77'].laser) {
                // Se il laser non è attivo, disegna solo lo sprite (o nulla se già gestito)
            }
            const start = new THREE.Vector3(0, 0, 600000);
            const endWorld = this.apices[idx];
            const endLocal = endWorld.clone().sub(this.group.position).applyQuaternion(quatInv);
            
            curve.v0.copy(start);
            curve.v2.copy(endLocal);
            // v1 (mid) può rimanere interpolato o essere ricalcolato per fluidità
            curve.v1.copy(start).lerp(endLocal, 0.5);
            
            const points = curve.getPoints(40);
            this.arcs[idx].geometry.setFromPoints(points);
        });

        const posAttr = this.flowSystem.geometry.attributes.position;
        for (let i = 0; i < this.flowCount; i++) {
            this.flowProgress[i] += 0.005; 
            if (this.flowProgress[i] > 1) this.flowProgress[i] = 0;

            const curveIdx = i % this.curves.length;
            const p = this.curves[curveIdx].getPoint(this.flowProgress[i]);
            posAttr.setXYZ(i, p.x, p.y, p.z);
        }
        posAttr.needsUpdate = true;

        this.arcs.forEach(arc => {
            arc.material.opacity = 0.1 + Math.sin(time*2)*0.1;
        });
    }

    destroy() {
        window.scene.remove(this.group);
    }

    destroy() {
        window.scene.remove(this.group);
    }
}

window.meshWormholes = {};
window.syncMeshWormholes = async () => {
    try {
        const r = await fetch('/api/mesh/peers', { headers: { 'X-API-KEY': VAULT_KEY }});
        const d = await r.json();
        let peers = d.peers || [];

        // Includiamo i demo peers nella sincronizzazione 3D
        if (window.demoPeers) {
            peers = [...peers, ...window.demoPeers];
        }
        
        const currentIds = peers.filter(p => !p.paused).map(p => p.id);
        Object.keys(window.meshWormholes).forEach(id => {
            if (!currentIds.includes(id)) {
                window.meshWormholes[id].destroy();
                delete window.meshWormholes[id];
            }
        });

        peers.forEach(p => {
            if (p.paused) return; // 🛡️ Non renderizzare peer in pausa
            if (!window.meshWormholes[p.id]) {
                console.log("🕸️ [Mesh] Inizializzazione Wormhole per:", p.id);
                window.meshWormholes[p.id] = new MeshWormhole(p);
                
                // 🕶️ [v7.0] Initialize Matrix-Smith Shader Mesh
                const group = new THREE.Group();
                const smithTex = new THREE.TextureLoader().load('/static/img/agent_smith_v7.png');
                
                // Custom Shader for "Matrix Rain" effect (v7.1 Stable)
                const smithMat = new THREE.ShaderMaterial({
                    uniforms: {
                        map: { value: smithTex },
                        time: { value: 0 }
                    },
                    vertexShader: `
                        varying vec2 vUv;
                        void main() {
                            vUv = uv;
                            gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
                        }
                    `,
                    fragmentShader: `
                        uniform sampler2D map;
                        uniform float time;
                        varying vec2 vUv;
                        void main() {
                            vec4 texColor = texture2D(map, vUv);
                            
                            // v7.2: Luma-based transparency fallback (per immagini senza alpha reale)
                            float brightness = dot(texColor.rgb, vec3(0.299, 0.587, 0.114));
                            if (texColor.a < 0.1 || brightness < 0.05) discard;
                            
                            // Effetto pioggia Matrix dinamica sulla faccia
                            float rain = fract(vUv.y * 1.5 + time * 0.7);
                            rain = pow(rain, 3.0); 
                            
                            // Colore bilanciato
                            vec3 color = texColor.rgb * (0.85 + rain * 0.8);
                            gl_FragColor = vec4(color, 1.0);
                        }
                    `,
                    transparent: true,
                    blending: THREE.NormalBlending,
                    side: THREE.DoubleSide,
                    alphaTest: 0.3
                });

                const geometry = new THREE.PlaneGeometry(1, 1);
                const mesh = new THREE.Mesh(geometry, smithMat);
                mesh.scale.set(600000, 600000, 1); // Imponente
                group.add(mesh);
                
                const label = createTextSprite(`AGENT-SMITH [FIREWALL]`, "#00ff41");
                label.position.y = 350000;
                group.add(label);
                
                scene.add(group);
                smithFleetGroups[p.id] = group;
            }
        });
        
        // Cleanup Smith Fleet
        Object.keys(smithFleetGroups).forEach(pid => {
            if (!currentIds.includes(pid)) {
                scene.remove(smithFleetGroups[pid]);
                delete smithFleetGroups[pid];
                delete smithTargetPositions[pid];
            }
        });
    } catch(e) {
        console.error("🚨 [Mesh] Errore Sincronizzazione Wormholes:", e);
    }
};

// --- 🧪 DEMO MODE PEERS (v6.0) ---
window.demoPeers = [
    { id: "AURA-OS-001", url: "http://10.0.0.45:8001", source: "zeroconf", last_seen: Date.now()/1000 - 15, isDemo: true },
    { id: "NEURAL-V-77", url: "http://192.168.1.22:8001", source: "manual", last_seen: Date.now()/1000 - 450, isDemo: true }
];

// Inizializzazione cicli sync
setInterval(window.syncMeshWormholes, 10000);
setTimeout(window.syncMeshWormholes, 3000); // Primo avvio rapido

// 🛡️ [v6.1] Global Handshake Initializer
document.addEventListener('DOMContentLoaded', () => {
    // Caricamento immediato identità sovrana
    window.refreshSovereignIdentity();

    const checkInterval = setInterval(() => {
        const handshakeInput = document.getElementById('handshake-token-input');
        if (handshakeInput) {
            handshakeInput.addEventListener('dragover', (e) => { e.preventDefault(); handshakeInput.style.borderColor = '#a855f7'; });
            handshakeInput.addEventListener('dragleave', () => { handshakeInput.style.borderColor = 'rgba(168,85,247,0.2)'; });
            handshakeInput.addEventListener('drop', (e) => {
                e.preventDefault();
                handshakeInput.style.borderColor = 'rgba(168,85,247,0.2)';
                const file = e.dataTransfer.files[0];
                if (file && file.name.endsWith('.nvvault')) {
                    window.importVaultIdentity(file);
                } else {
                    showFloatingNotification("File non valido. Trascina un file .nvvault ⚠️", "error");
                }
            });
            clearInterval(checkInterval);
        }
    }, 1000);

    // [v9.1] Wiki Search Enter Key Support
    const wikiSearchCheck = setInterval(() => {
        const wikiSearch = document.getElementById('wiki-search-portal');
        if (wikiSearch) {
            wikiSearch.addEventListener('keyup', (e) => {
                if (e.key === 'Enter') window.loadWikiPage(wikiSearch.value);
            });
            clearInterval(wikiSearchCheck);
        }
    }, 1000);
});

// [v8.0] Security Log Helpers
window.clearSecurityLogs = () => {
    const log = document.getElementById('security-audit-log');
    if (log) log.innerHTML = '<div class="audit-entry">🛡️ Logs cleared. Monitoring resumed...</div>';
};

// --- 🛰️ [DN-099] Mandalorian Advanced Animations (v16.5) ---
let mandoScanner = null;
let mandoMergeEffect = null;

window.updateMandoScanner = function(start, end) {
    if (!scene) return;
    if (!mandoScanner) {
        // Creazione dello scanner celeste (cono di luce volumetrica)
        const geometry = new THREE.CylinderGeometry(5000, 150000, 1000000, 32, 1, true);
        geometry.rotateX(Math.PI / 2);
        geometry.translate(0, 0, 500000); 
        const material = new THREE.MeshBasicMaterial({
            color: 0x00f2ff,
            transparent: true,
            opacity: 0.15,
            side: THREE.DoubleSide,
            blending: THREE.AdditiveBlending,
            depthWrite: false
        });
        mandoScanner = new THREE.Mesh(geometry, material);
        
        // Aggiungi un raggio centrale più intenso
        const beamGeo = new THREE.CylinderGeometry(2000, 2000, 1000000, 8);
        beamGeo.rotateX(Math.PI / 2);
        beamGeo.translate(0, 0, 500000);
        const beamMat = new THREE.MeshBasicMaterial({ color: 0x00f2ff, transparent: true, opacity: 0.6, blending: THREE.AdditiveBlending });
        const beam = new THREE.Mesh(beamGeo, beamMat);
        mandoScanner.add(beam);
        scene.add(mandoScanner);
    }
    
    mandoScanner.visible = true;
    mandoScanner.position.copy(start);
    mandoScanner.lookAt(end);
    
    // Effetto pulsazione scanner
    mandoScanner.material.opacity = 0.1 + Math.sin(Date.now() * 0.01) * 0.05;
};

window.hideMandoScanner = function() {
    if (mandoScanner) mandoScanner.visible = false;
};

window.triggerMandoMergeEffect = function(pos) {
    if (!pos || !scene) return;
    // Crea un'onda d'urto semantica persistente
    if (mandoMergeEffect && Date.now() - mandoMergeEffect.createdAt < 20000) return; 
    
    const geometry = new THREE.SphereGeometry(10000, 32, 32);
    const material = new THREE.MeshBasicMaterial({
        color: 0x4ade80,
        transparent: true,
        opacity: 0.6,
        blending: THREE.AdditiveBlending,
        wireframe: true
    });
    const shockwave = new THREE.Mesh(geometry, material);
    shockwave.position.copy(pos);
    scene.add(shockwave);
    
    mandoMergeEffect = { mesh: shockwave, createdAt: Date.now() };
    
    // Animazione di espansione e dissolvenza (20 secondi di cooldown/visibilità)
    let scale = 1.0;
    const interval = setInterval(() => {
        scale += 12.0;
        shockwave.scale.set(scale, scale, scale);
        shockwave.rotation.y += 0.01;
        shockwave.material.opacity -= 0.0015;
        
        if (shockwave.material.opacity <= 0) {
            clearInterval(interval);
            scene.remove(shockwave);
            geometry.dispose();
            material.dispose();
        }
    }, 50);
};
window.onNebulaClick = (event) => {
    const container = document.getElementById('memory-graph-container');
    if (!container) return;
    const rect = container.getBoundingClientRect();
    mouse.x = ((event.clientX - rect.left) / container.clientWidth) * 2 - 1;
    mouse.y = -((event.clientY - rect.top) / container.clientHeight) * 2 + 1;
    raycaster.setFromCamera(mouse, camera);
    
    // Controlliamo collisioni su tutte le entità: Nodi, Cluster e Sprite
    const intersectsNodes = raycaster.intersectObject(pointsMesh);
    const intersectsMultimodal = raycaster.intersectObjects(multimodalGroup.children);
    const intersectsClusters = raycaster.intersectObjects(clusterNodesGroup.children);
    const intersectsGaps = raycaster.intersectObjects(ignoranceGroup.children);
    
    let hitNodeId = null;

    if (intersectsGaps.length > 0) {
        const gap = intersectsGaps[0].object.userData;
        if (gap && gap.isGap) {
            log(`🌌 [Metacognition] Terra Incognita rilevata!`, "#94a3b8");
            log(`🧠 Gap tra: ${gap.context}`, "#94a3b8");
            log(`🔍 Argomenti suggeriti: ${gap.missing.join(', ')}`, "#3b82f6");
            if (confirm(`Terra Incognita rilevata: ${gap.missing.join(', ')}. Vuoi inviare lo sciame a colmare questo gap?`)) {
                log(`🚀 [Metacognition] Missione di recupero avviata per: ${gap.missing[0]}`, "#10b981");
                const queryInput = document.getElementById('floating-query-input');
                if (queryInput) {
                    queryInput.value = `Indaga e recupera informazioni approfondite su: ${gap.missing.join(' e ')}`;
                    const badge = document.getElementById('mode-badge');
                    if (badge && badge.innerText !== "QUERY") window.toggleCommandMode();
                    window.queryNeuralVault();
                }
            }
            return; // Non ispezioniamo nodi se colpiamo un gap
        }
    } else if (intersectsMultimodal.length > 0) {
        hitNodeId = intersectsMultimodal[0].object.userData.id;
    } else if (intersectsClusters.length > 0) {
        hitNodeId = intersectsClusters[0].object.userData.id;
    } else if (intersectsNodes.length > 0) {
        const nodeIdx = intersectsNodes[0].index;
        if (nodeIdx !== undefined && vaultPoints && vaultPoints[nodeIdx]) {
            hitNodeId = vaultPoints[nodeIdx].id;
        } else {
            console.warn("⚠️ [Nebula Interaction] Raycaster hit unpopulated point index:", nodeIdx);
        }
    }

    if (hitNodeId) {
        console.log("🎯 Nebula Interaction - ID colpito:", hitNodeId);
        
        // Auto-Override UX: se l'utente clicca, vuole ispezionare. Forziamo l'interruttore.
        const probeToggle = document.getElementById('probe-toggle');
        if (probeToggle && !probeToggle.checked) {
            probeToggle.checked = true;
            console.log("⚡ Auto-enabled Neural Probe for manual inspection.");
        }
        
        console.log("🕵️ Inspecting Node:", hitNodeId);
        selectNode(hitNodeId);
        
        // [v8.4] Sync with What-If Engine
        window.selectedSimNode = hitNodeId;
        const targetEl = document.getElementById('sim-target-node');
        if (targetEl) targetEl.innerText = hitNodeId;
    }
};
window.uploadMediaSynapse = async (file) => {
    if (!file) return;
    
    log(`☁️ [Multimodal] Ingestione avviata: ${file.name}...`, '#3b82f6');
    
    // Mostriamo progresso finto nel HUD (vettorializzazione locale)
    const hud = document.getElementById('forage-telemetry-hud');
    const bar = document.getElementById('forage-progress-bar');
    const stats = document.getElementById('forage-telemetry-stats');
    
    if (hud) hud.style.display = 'flex';
    if (bar) bar.style.set = '0%';
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        const response = await fetch('/api/multimodal/upload', {
            method: 'POST',
            headers: { 'X-API-KEY': VAULT_KEY },
            body: formData
        });
        
        const result = await response.json();
        
        if (response.ok) {
            log(`✅ [Multimodal] Ingestione completata: ${result.ingested_nodes} segmenti sincronizzati.`, '#4ade80');
            if (bar) bar.style.width = '100%';
            setTimeout(() => { if(hud) hud.style.display = 'none'; }, 2000);
        } else {
            log(`❌ [Multimodal] Errore: ${result.detail || 'Ingestione fallita'}`, '#ef4444');
        }
    } catch (e) {
        log(`❌ [Multimodal] Errore di rete: ${e.message}`, '#ef4444');
    }
};

window.triggerShardClone = async () => {
    log("🏺 [ShardGuard] Avvio clonazione shard manuale...", "#a855f7");
    try {
        const r = await fetch('/api/sharding/clone', {
            method: 'POST',
            headers: { 'X-API-KEY': VAULT_KEY }
        });
        const res = await r.json();
        if (r.ok) log(`✅ [ShardGuard] Clone creato: ${res.shard_id}`, "#4ade80");
        else log(`❌ [ShardGuard] Errore: ${res.detail}`, "#ef4444");
    } catch (e) { log(`❌ [ShardGuard] Errore di rete: ${e.message}`, "#ef4444"); }
};

window.triggerShardBackup = async () => {
    log("📦 [ShardGuard] Avvio backup fisico manuale...", "#3b82f6");
    try {
        const r = await fetch('/api/sharding/backup', {
            method: 'POST',
            headers: { 'X-API-KEY': VAULT_KEY }
        });
        const res = await r.json();
        if (r.ok) log("✅ [ShardGuard] Backup fisico completato con successo.", "#4ade80");
        else log(`❌ [ShardGuard] Errore: ${res.detail}`, "#ef4444");
    } catch (e) { log(`❌ [ShardGuard] Errore di rete: ${e.message}`, "#ef4444"); }
};

window.toggleCommandMode = () => {
    const badge = document.getElementById('mode-badge');
    const urlInput = document.getElementById('floating-url-input');
    const queryInput = document.getElementById('floating-query-input');
    const actionBtn = document.getElementById('main-action-btn');
    if (badge.innerText === "FORAGING") {
        badge.innerText = "QUERY";
        badge.style.color = "#3b82f6";
        badge.style.background = "rgba(59, 130, 246, 0.1)";
        urlInput.style.display = "none";
        queryInput.style.display = "block";
        actionBtn.innerText = "CHIEDI";
        actionBtn.onclick = queryNeuralVault;
    } else {
        badge.innerText = "FORAGING";
        badge.style.color = "#a855f7";
        badge.style.background = "rgba(168, 85, 247, 0.1)";
        urlInput.style.display = "block";
        queryInput.style.display = "none";
        actionBtn.innerText = "SINAPSI";
        actionBtn.onclick = forageWebFloating;
    }
};

window.forageWebFloating = async () => {
    const input = document.getElementById('floating-url-input');
    const url = input.value.trim();
    if (!url) {
        log(`⚠️ URL mancante. Inserisci un link per iniziare il Foraging.`, "#f59e0b");
        input.classList.add('error-shake');
        setTimeout(() => input.classList.remove('error-shake'), 500);
        return;
    }
    log(`🌐 Foraging initiated for: ${url}`, "#a855f7");
    try {
        const r = await fetch('/api/forage', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'X-API-KEY': VAULT_KEY },
            body: JSON.stringify({ url, max_depth: 3 })
        });
        const d = await r.json();
        if (d.status === "foraging_started") {
            document.getElementById('floating-url-input').value = "";
            log(`✅ Job ID: ${d.job_id.slice(0,8)}... Running in background.`, "#4ade80");
        }
    } catch(e) { log(`❌ Forage Error: ${e.message}`, "#ef4444"); }
};

window.queryNeuralVault = async () => {
    const q = document.getElementById('floating-query-input').value;
    if (!q) return;
    const hud = document.getElementById('oracle-response-hud');
    const ans = document.getElementById('oracle-answer');
    const src = document.getElementById('oracle-sources');
    hud.style.display = 'flex';
    ans.innerText = "L'Oracolo sta interrogando la Nebula...";
    src.innerText = "Sorgenti attivate: [Ricerca in corso]";
    try {
        const r = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'X-API-KEY': VAULT_KEY },
            body: JSON.stringify({ query: q, consensus: true })
        });
        const d = await r.json();
        ans.innerText = d.answer;
        src.innerText = `Sorgenti attivate: [${d.context_nodes.length}] nodi analizzati.`;
        document.getElementById('floating-query-input').value = "";
    } catch(e) { 
        ans.innerText = `Errore Neurale: ${e.message}`; 
    }
};

window.updateHardwareStrategy = (dna) => {
    const container = document.getElementById('strategy-advisor-content');
    if (!container) return;
    let ram = dna?.ram_total || "8.0GB";
    container.innerHTML = `<div style="padding:1rem; background:rgba(255,255,255,0.05); border-radius:12px;">DNA: ${dna?.accel || 'CPU'} | RAM: ${ram}</div>`;
};
