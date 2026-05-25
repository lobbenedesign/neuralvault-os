/**
 * 🚂 NEURALVAULT ENGINE (Three.js Core)
 */

function init3D() {
    if (window.is3DInitialized) return;
    const container = document.getElementById('memory-graph-container');
    const canvas = document.getElementById('isometric-canvas');
    if (!container || !canvas) return;
    
    if (container.clientWidth === 0 || container.clientHeight === 0) {
        requestAnimationFrame(init3D);
        return;
    }

    let gl = null;
    try {
        gl = canvas.getContext('webgl2', { alpha: true, depth: true, antialias: true }) || 
             canvas.getContext('webgl', { alpha: true, depth: true, antialias: true });
    } catch (e) {
        console.error("Critical WebGL Error:", e);
    }
    
    if (!gl) {
        if (typeof log === 'function') log("⚠️ WebGL Failure - Retrying Reset...", "#ef4444");
        setTimeout(init3D, 2000);
        return;
    }

    scene = new THREE.Scene();
    window.scene = scene;
    const isLight = document.body.classList.contains('light-theme');
    scene.background = new THREE.Color(isLight ? 0xf8fafc : 0x020617);

    camera = new THREE.PerspectiveCamera(75, container.clientWidth / container.clientHeight, 1, 300000000);
    camera.position.set(5000000, 5000000, 5000000); 
    camera.lookAt(0, 1000000, 0);
    window.camera = camera;

    renderer = new THREE.WebGLRenderer({ canvas, context: gl, antialias: true, alpha: true, logarithmicDepthBuffer: true });
    renderer.setSize(container.clientWidth, container.clientHeight);
    renderer.setPixelRatio(window.devicePixelRatio > 1 ? 2 : 1);
    window.renderer = renderer;

    scene.add(new THREE.AmbientLight(0xffffff, 0.7));
    const dl = new THREE.DirectionalLight(0xffffff, 1.0);
    dl.position.set(1, 1, 1);
    scene.add(dl);

    // Grid & Guide Cube
    cube = new THREE.Mesh(
        new THREE.BoxGeometry(4000000, 4000000, 4000000),
        new THREE.MeshBasicMaterial({ color: 0x3b82f6, wireframe: true, transparent: true, opacity: 0.4 })
    );
    cube.position.y = 1002000;
    scene.add(cube);

    const grid = new THREE.GridHelper(10000000, 20, isLight ? 0x94a3b8 : 0x3b82f6, isLight ? 0xe2e8f0 : 0x1e293b);
    grid.position.y = -1000000;
    scene.add(grid);

    // Orbital Controls
    if (typeof THREE.OrbitControls === 'function') {
        controls = new THREE.OrbitControls(camera, renderer.domElement);
        controls.target.set(0, 1000000, 0);
        controls.enableDamping = true;
        controls.dampingFactor = 0.05;
        controls.minDistance = 5;
        controls.maxDistance = 300000000;
        controls.addEventListener('start', () => { isUserInteracting = true; });
        controls.addEventListener('end', () => { isUserInteracting = false; });
    }

    raycaster = new THREE.Raycaster();
    raycaster.params.Points.threshold = 150000;
    mouse = new THREE.Vector2();

    // 🤖 Agents Container Initialization
    agentsContainer = new THREE.Group();
    agentsContainer.position.y = 1000000;
    scene.add(agentsContainer);

    // [v16.0] Cluster Visualization Layer
    clusterNodesGroup = new THREE.Group();
    clusterNodesGroup.position.y = 1000000;
    clusterNodesGroup.frustumCulled = false;
    scene.add(clusterNodesGroup);

    const MAX_POINTS = 80000; // 🛡️ [v11.3.0] Optimized Safety Cap
    const MAX_LINKS = 1000000;  // 🕸️ [v11.0] Full Synaptic Fabric Rendering

    const geometry = new THREE.BufferGeometry();
    geometry.setAttribute('position', new THREE.BufferAttribute(new Float32Array(MAX_POINTS * 3), 3));
    geometry.setAttribute('color', new THREE.BufferAttribute(new Float32Array(MAX_POINTS * 3), 3));
    
    pointsMesh = new THREE.Points(geometry, new THREE.PointsMaterial({
        size: 25000, 
        vertexColors: true, 
        transparent: true, 
        opacity: 0.9,
        sizeAttenuation: true, 
        blending: THREE.AdditiveBlending, 
        depthWrite: false
    }));
    pointsMesh.position.y = 1000000;
    pointsMesh.frustumCulled = false; // Prevent points from vanishing when moved
    scene.add(pointsMesh);

    multimodalGroup = new THREE.Group();
    multimodalGroup.position.y = 1000000;
    multimodalGroup.frustumCulled = false;
    scene.add(multimodalGroup);

    // [v4.0] Pre-render Multimodal Textures (Image, Audio, Video)
    const createIconTexture = (icon, color) => {
        const canvas = document.createElement('canvas');
        canvas.width = 128; canvas.height = 128;
        const ctx = canvas.getContext('2d');
        ctx.fillStyle = color;
        ctx.font = '900 80px "Font Awesome 6 Free"';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(icon, 64, 64);
        const tex = new THREE.CanvasTexture(canvas);
        return tex;
    };
    multimodalTextures['image'] = createIconTexture('\uf03e', '#4ade80'); // Photo
    multimodalTextures['audio'] = createIconTexture('\uf6a8', '#3b82f6'); // Waveform
    multimodalTextures['video'] = createIconTexture('\uf03d', '#ef4444'); // Video Camera

    neuralLinks = new THREE.Group(); 
    neuralLinks.position.y = 1000000;
    scene.add(neuralLinks);

    const linkGeo = new THREE.BufferGeometry();
    linkGeo.setAttribute('position', new THREE.BufferAttribute(new Float32Array(MAX_LINKS * 2 * 3), 3));
    linkGeo.setAttribute('color', new THREE.BufferAttribute(new Float32Array(MAX_LINKS * 2 * 3), 3));
    linkGeo.setDrawRange(0, 0); // 🛡️ [Startup Guard] Initialize with 0 lines to prevent millions of ghost lines at startup
    linksMesh = new THREE.LineSegments(linkGeo, new THREE.LineBasicMaterial({ 
        vertexColors: true, 
        transparent: true, 
        opacity: isLight ? 0.2 : 0.35, 
        blending: isLight ? THREE.NormalBlending : THREE.AdditiveBlending,
        depthWrite: false
    }));
    linksMesh.position.y = 1000000;
    linksMesh.frustumCulled = false; // 🕸️ [v10.6] Prevent links from vanishing when approaching clusters
    scene.add(linksMesh);

    ignoranceGroup = new THREE.Group();
    ignoranceGroup.position.y = 1000000;
    scene.add(ignoranceGroup);

    // Init Layers
    if (typeof provisionAgents === 'function') provisionAgents();

    if (!window.playerController && typeof PlayerController !== 'undefined') {
        window.playerController = new PlayerController(scene, camera, controls);
    }

    animate();
    window.is3DInitialized = true;
    
    // 🎯 [v18.2] Dynamic Viewport Adaptation
    window.addEventListener('resize', onWindowResize, false);
    
    if (typeof log === 'function') log("🚀 Neural Cycloscope Ready", "#3b82f6");
}

function onWindowResize() {
    const container = document.getElementById('memory-graph-container');
    if (!container || !camera || !renderer) return;
    
    camera.aspect = container.clientWidth / container.clientHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(container.clientWidth, container.clientHeight);
}

function handleResize() {
    onWindowResize();
}

let lastRenderTime = 0;
const frameDelay = 1000 / 30; // [M1 Thermal Guard] Cap background 3D rendering to 30 FPS to save CPU/GPU resources

function animate() {
    requestAnimationFrame(animate);
    
    // [Battery Saver] Immediately halt rendering and physics updates when app is minimized or tab is hidden
    if (document.hidden) return;
    
    const now = Date.now();
    const elapsed = now - lastRenderTime;
    if (elapsed < frameDelay) return;
    lastRenderTime = now - (elapsed % frameDelay);
    
    const overview = document.getElementById('overview-view');
    if (overview && overview.style.display === 'none') return;
    
    if (!window.isRenderLoopActive) {
        if (typeof log === 'function') log("🔄 Render Loop Engaged", "#a855f7");
        window.isRenderLoopActive = true;
    }
    
    const time = now * 0.001;

    // 🎯 [v17.6] Priority Camera Hook: Update follow logic BEFORE controls.update()
    updateCameraFollow();
    
    if (controls) controls.update();
    
    if (isEvolving) {
        const exp = nebulaExpansionFactor || 1.0;
        const radius = (200000 + 50000 * Math.sin(time * 0.5)) * exp;
        quantumTargetPos.set(Math.cos(time) * radius, Math.sin(time * 0.7) * 100000 * exp, Math.sin(time) * radius);
        synthTargetPos.set(Math.cos(time + Math.PI) * radius, Math.sin(time * 0.7 + Math.PI) * 100000 * exp, Math.sin(time + Math.PI) * radius);
    } else {
        try {
            if (typeof updateAgentPhysics === 'function') updateAgentPhysics();
        } catch (e) {
            console.warn("⚠️ [Physics] Error in agent movement loop:", e);
        }
    }

    // Module updates
    if (window.meshWormholes) {
        Object.values(window.meshWormholes).forEach(w => w.update());
    }
    
    if (window.playerController) {
        window.playerController.update(0.016);
    }
    
    // 🌌 [v11.0] High-Performance Client-Side WASM Physics Layout Engine Step
    if (window.vaultPoints && window.vaultPoints.length > 0 && !isRotationPaused && !window.isFlightModeActive) {
        try {
            if (typeof window.SovereignWASM !== 'undefined' && window.SovereignWASM.physics) {
                window.SovereignWASM.physics.step(window.vaultPoints, window.lastNeuralLinks);
                
                // Update InstancedMesh positions directly on every frame from the WASM physics memory
                if (window.pointsMesh) {
                    const isInst = window.pointsMesh.isInstancedMesh;
                    const exp = window.nebulaExpansionFactor || 1.0;
                    const pMap = window.SovereignWASM.physics.nodeIndexMap;
                    const posArray = window.SovereignWASM.physics.positions;
                    
                    if (isInst && pMap && posArray) {
                        const dummy = new THREE.Object3D();
                        for (let i = 0; i < Math.min(window.vaultPoints.length, 30000); i++) {
                            const p = window.vaultPoints[i];
                            const idx = pMap[p.id];
                            if (idx !== undefined) {
                                const px = posArray[idx * 3] * exp;
                                const py = posArray[idx * 3 + 1] * exp;
                                const pz = posArray[idx * 3 + 2] * exp;
                                dummy.position.set(px, py, pz);
                                
                                // Preserve scale of galaxies
                                const isGalaxy = (p.is_galaxy === true || (p.metadata && p.metadata.is_galaxy === true));
                                if (isGalaxy) {
                                    dummy.scale.setScalar(4.0);
                                } else {
                                    dummy.scale.setScalar(1.0);
                                }
                                
                                dummy.updateMatrix();
                                window.pointsMesh.setMatrixAt(i, dummy.matrix);
                                
                                // Write back positions so other JS components (like clusters) find them
                                p.x = posArray[idx * 3];
                                p.y = posArray[idx * 3 + 1];
                                p.z = posArray[idx * 3 + 2];
                            }
                        }
                        window.pointsMesh.instanceMatrix.needsUpdate = true;
                    } else if (pMap && posArray) {
                        const posAttr = window.pointsMesh.geometry.attributes.position;
                        const array = posAttr.array;
                        for (let i = 0; i < Math.min(window.vaultPoints.length, 30000); i++) {
                            const p = window.vaultPoints[i];
                            const idx = pMap[p.id];
                            if (idx !== undefined) {
                                const px = posArray[idx * 3] * exp;
                                const py = posArray[idx * 3 + 1] * exp;
                                const pz = posArray[idx * 3 + 2] * exp;
                                array[i * 3] = px;
                                array[i * 3 + 1] = py;
                                array[i * 3 + 2] = pz;
                                
                                // Write back positions
                                p.x = posArray[idx * 3];
                                p.y = posArray[idx * 3 + 1];
                                p.z = posArray[idx * 3 + 2];
                            }
                        }
                        posAttr.needsUpdate = true;
                    }

                    // Update majestic rings and labels for galaxies to stay perfectly aligned
                    if (window.galaxyGroup && window.galaxyGroup.children.length > 0 && pMap && posArray) {
                        window.galaxyGroup.children.forEach(child => {
                            if (child.userData && child.userData.galaxyId) {
                                const gid = child.userData.galaxyId;
                                const idx = pMap[gid];
                                if (idx !== undefined) {
                                    const px = posArray[idx * 3] * exp;
                                    const py = posArray[idx * 3 + 1] * exp;
                                    const pz = posArray[idx * 3 + 2] * exp;
                                    if (child.userData.isRing) {
                                        child.position.set(px, py, pz);
                                    } else if (child.userData.isLabel) {
                                        child.position.set(px, py + 45000, pz);
                                    }
                                }
                            }
                        });
                    }
                }
                
                // Sync edge positions and colors dynamically to stay perfectly aligned and beautifully lit
                if (typeof linksMesh !== 'undefined' && window.lastNeuralLinks && layersVisibility.edges) {
                    const linkPos = linksMesh.geometry.attributes.position.array;
                    const linkCol = linksMesh.geometry.attributes.color.array;
                    let linkIdx = 0;
                    const currentLinks = window.lastNeuralLinks;
                    
                    const pMap = window.SovereignWASM.physics.nodeIndexMap;
                    const posArray = window.SovereignWASM.physics.positions;
                    const exp = window.nebulaExpansionFactor || 1.0;
                    const isLightTheme = document.body.classList.contains('light-theme');
                    
                    const activeLinks = window.activeRenderedLinks;
                    if (pMap && posArray && activeLinks && activeLinks.length > 0) {
                        for (let j = 0; j < activeLinks.length; j++) {
                            const link = activeLinks[j];
                            const srcIdx = pMap[link.srcId];
                            const dstIdx = pMap[link.dstId];
                            
                            if (srcIdx !== undefined && dstIdx !== undefined) {
                                // Direct lookup mapping! Zero string allocation, zero color calculation
                                const jIdx = link.linkIdx;
                                linkPos[jIdx*6] = posArray[srcIdx * 3] * exp;
                                linkPos[jIdx*6+1] = posArray[srcIdx * 3 + 1] * exp;
                                linkPos[jIdx*6+2] = posArray[srcIdx * 3 + 2] * exp;
                                linkPos[jIdx*6+3] = posArray[dstIdx * 3] * exp;
                                linkPos[jIdx*6+4] = posArray[dstIdx * 3 + 1] * exp;
                                linkPos[jIdx*6+5] = posArray[dstIdx * 3 + 2] * exp;
                            }
                        }
                        linksMesh.geometry.attributes.position.needsUpdate = true;
                    }
                }
            }
        } catch (e) {
            console.error("⚠️ [WASM Physics Engine Error]", e);
        }
    }

    updateVisualEffects(now, time);
    updateCameraFollow();

    if (renderer) renderer.render(scene, camera);
}

function updateCameraFollow() {
    if (window.playerController && window.playerController.active) return;
    if (followedAgent && controls) {
        const targetWorldPos = new THREE.Vector3();
        followedAgent.getWorldPosition(targetWorldPos);
        
        // 🎯 [v10.5] Improved Camera Hook
        controls.target.lerp(targetWorldPos, 0.1);
        
        // Mantieni una distanza ideale dall'agente (Calibrata per la nuova scala macro)
        const idealDist = Math.min(1000000, 400000 + (nebulaExpansionFactor * 0.2)); 
        const currentDist = camera.position.distanceTo(targetWorldPos);
        
        if (Math.abs(idealDist - currentDist) > 1000) {
            const dir = camera.position.clone().sub(targetWorldPos).normalize();
            const targetCamPos = targetWorldPos.clone().add(dir.multiplyScalar(idealDist));
            camera.position.lerp(targetCamPos, 0.08);
        }
    }
}

function updateVisualEffects(now, time) {
    medicalCubes = medicalCubes.filter(c => {
        const age = now - c.createdAt;
        const isVeryOld = (age > 600000);
        const MIN_VISIBILITY = 120000;
        if (isVeryOld || (c.userData && c.userData.completed && age > MIN_VISIBILITY)) {
            c.scale.setScalar(c.scale.x * 0.95);
            if (c.scale.x < 0.1 || isVeryOld) {
                if (typeof safeDispose === 'function') safeDispose(c);
                else scene.remove(c);
                return false;
            }
        } else {
            c.scale.setScalar(0.8 + Math.sin(time * 3) * 0.05); 
        }
        return true;
    });

    // 🧹 [v11.2] Reaper Cubes Cleanup (Previously Leaking)
    reaperCubes = reaperCubes.filter(item => {
        const isExpired = now > item.expiry;
        if (isExpired) {
            if (typeof safeDispose === 'function') safeDispose(item.mesh);
            else scene.remove(item.mesh);
            return false;
        }
        return true;
    });

    if (!isRotationPaused && !window.isFlightModeActive) {
        const deltaRot = 0.001;
        if (pointsMesh) pointsMesh.rotation.y += deltaRot;
        if (linksMesh) linksMesh.lineSegmentsRotation = (linksMesh.lineSegmentsRotation || 0) + deltaRot; // Track for sync
        if (linksMesh) linksMesh.rotation.y += deltaRot;
        if (clusterNodesGroup) clusterNodesGroup.rotation.y += deltaRot;
        if (multimodalGroup) multimodalGroup.rotation.y += deltaRot;
        if (neuralLinks) {
            neuralLinks.rotation.y += deltaRot;
            updateNeuralLinksAnimation(time);
        }
        
        if (linksMesh && linksMesh.material) {
            const isLight = document.body.classList.contains('light-theme');
            const pulse = Math.sin(time * 2.0) * 0.05;
            linksMesh.material.opacity = (isLight ? 0.2 : 0.35) + pulse;
        }
    
        // 🛡️ [v11.2] Memory Guardian Telemetry Sync (Every ~1s)
        if (Math.floor(time) % 2 === 0 && typeof updateMemoryTelemetry === 'function') {
            updateMemoryTelemetry();
        }
    }
}

function updateNeuralLinksAnimation(time) {
    const isLight = document.body.classList.contains('light-theme');
    neuralLinks.children.forEach(link => {
        if (link.isSpark) {
            const flicker = Math.random() > 0.8 ? 1.0 : 0.4;
            link.material.color.setHex(Math.random() > 0.5 ? 0x00ffff : 0xffffff);
            link.material.opacity = (isLight ? 0.8 : 0.6) * flicker;
            link.material.blending = isLight ? THREE.NormalBlending : THREE.AdditiveBlending;
        } else if (link.isSuper) {
            const hue = (time * 0.1 + (link.id % 20) * 0.05) % 1;
            link.material.color.setHSL(hue, 0.9, isLight ? 0.4 : 0.6);
            link.material.opacity = isLight ? 0.9 : 0.7 + Math.sin(time * 5) * 0.2;
            link.material.blending = isLight ? THREE.NormalBlending : THREE.AdditiveBlending;
        } else if (link.isNew) {
            link.material.opacity = 0.5 + Math.sin(time * 20) * 0.5;
            link.material.blending = isLight ? THREE.NormalBlending : THREE.AdditiveBlending;
        } else {
            if (isLight) {
                link.material.color.set(0x475569); 
                link.material.opacity = 0.25;
            } else {
                link.material.color.set(0xffffff); 
                link.material.opacity = 0.15;
            }
            link.material.blending = THREE.NormalBlending;
        }
    });
}

window.init3D = init3D;
window.animate = animate;
