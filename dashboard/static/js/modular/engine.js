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

    const MAX_POINTS = 80000; // 🛡️ [v11.1] Optimized Safety Cap
    const MAX_LINKS = 1000000;  // 🕸️ [v11.0] Full Synaptic Fabric Rendering
    const geometry = new THREE.BufferGeometry();
    geometry.setAttribute('position', new THREE.BufferAttribute(new Float32Array(MAX_POINTS * 3), 3));
    geometry.setAttribute('color', new THREE.BufferAttribute(new Float32Array(MAX_POINTS * 3), 3));
    
    pointsMesh = new THREE.Points(geometry, new THREE.PointsMaterial({
        size: 10000, vertexColors: true, transparent: true, opacity: 0.9,
        sizeAttenuation: true, blending: THREE.AdditiveBlending, depthWrite: false
    }));
    pointsMesh.position.y = 1000000;
    pointsMesh.frustumCulled = false; // 🌌 [v10.6] Keep nebula visible during deep space jumps
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
    linksMesh = new THREE.LineSegments(linkGeo, new THREE.LineBasicMaterial({ 
        vertexColors: true, transparent: true, opacity: 0.25, blending: THREE.NormalBlending 
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

function animate() {
    requestAnimationFrame(animate);
    
    const overview = document.getElementById('overview-view');
    if (overview && overview.style.display === 'none') return;
    
    if (!window.isRenderLoopActive) {
        if (typeof log === 'function') log("🔄 Render Loop Engaged", "#a855f7");
        window.isRenderLoopActive = true;
    }
    
    const now = Date.now();
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
        
        // Mantieni una distanza ideale dall'agente
        const idealDist = 250000 * (nebulaExpansionFactor || 1.0);
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
                scene.remove(c);
                return false;
            }
        } else {
            c.scale.setScalar(0.8 + Math.sin(time * 3) * 0.05); 
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
