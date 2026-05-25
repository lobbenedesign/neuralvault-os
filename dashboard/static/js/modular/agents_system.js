function provisionAgents() {
    janitronGroup = new THREE.Group();
    const jaMat = new THREE.MeshPhongMaterial({ color: 0xfacc15, emissive: 0x422006, shininess: 80 });
    const jaBlackMat = new THREE.MeshBasicMaterial({ color: 0x000000 });

    // Emisfero Superiore (Calotta Nord)
    const topGeo = new THREE.SphereGeometry(45000, 32, 16, 0, Math.PI * 2, 0, Math.PI / 2);
    janitronTop = new THREE.Mesh(topGeo, jaMat);
    // Orientamento iniziale neutro (chiuso verso Z)
    
    // 👀 OCCHI GIGANTI 3D (Stile Q-bert)
    const eyeWhite = new THREE.MeshBasicMaterial({ color: 0xffffff });
    const eyeBlack = new THREE.MeshBasicMaterial({ color: 0x000000 });
    
    for(let side of [-1, 1]) {
        const e = new THREE.Mesh(new THREE.SphereGeometry(15000, 16, 16), eyeWhite);
        e.position.set(side * 22000, 25000, 25000);
        janitronTop.add(e);
        const p = new THREE.Mesh(new THREE.SphereGeometry(6000, 8, 8), eyeBlack);
        p.position.set(side * 22000, 25000, 35000);
        janitronTop.add(p);
    }
    
    // Emisfero Inferiore (Calotta Sud)
    const botGeo = new THREE.SphereGeometry(45000, 32, 16, 0, Math.PI * 2, Math.PI / 2, Math.PI / 2);
    janitronBottom = new THREE.Mesh(botGeo, jaMat);
    
    // Interno Bocca (Sfera interna nera per profondità totale)
    const insideGeo = new THREE.SphereGeometry(43000, 16, 16);
    const inside = new THREE.Mesh(insideGeo, jaBlackMat);
    
    janitronGroup.add(janitronTop, janitronBottom, inside);
    janitronGroup.userData = { mat: jaMat };
    // 🔄 Orientamento Default
    janitronGroup.rotation.y = 0;

    janitronLabel = createTextSprite("JA-001 JANITRON", "#facc15");
    janitronLabel.position.y = 100000;
    janitronGroup.add(janitronLabel);
    if (!agentsContainer) {
        console.warn("⚠️ agentsContainer undefined. Creating fallback.");
        agentsContainer = new THREE.Group();
        if (scene) scene.add(agentsContainer);
    }
    agentsContainer.add(janitronGroup);

    distillerGroup = new THREE.Group();
    const invMat = new THREE.MeshLambertMaterial({ color: 0xa855f7 });
    const pixels = [[0,0,1,0,0,0,1,0,0],[0,0,0,1,0,1,0,0,0],[0,0,1,1,1,1,1,0,0],[0,1,1,0,1,0,1,1,0],[1,1,1,1,1,1,1,1,1],[1,0,1,1,1,1,1,0,1],[1,0,1,0,0,0,1,0,1],[0,0,0,1,0,1,0,0,0]];
    const vSize = 8000;
    pixels.forEach((row, y) => row.forEach((p, x) => {
        if(p) {
            const v = new THREE.Mesh(new THREE.BoxGeometry(vSize, vSize, vSize), invMat);
            v.position.set((x - 4) * vSize, (4 - y) * vSize, 0);
            distillerGroup.add(v);
        }
    }));
    distillerLabel = createTextSprite("DI-007 DISTILLER", "#a855f7");
    distillerLabel.position.y = 80000;
    distillerGroup.add(distillerLabel);
    agentsContainer.add(distillerGroup);

    reaperGroup = new THREE.Group();
    const mats = [null, new THREE.MeshLambertMaterial({ color: 0xffffff }), new THREE.MeshLambertMaterial({ color: 0xffdbac }), new THREE.MeshLambertMaterial({ color: 0x5d4037 }), new THREE.MeshLambertMaterial({ color: 0xef4444 }), new THREE.MeshLambertMaterial({ color: 0x2196f3 }), new THREE.MeshLambertMaterial({ color: 0x3e2723 }), new THREE.MeshLambertMaterial({ color: 0xef4444 })];
    const rVsize = 6000;
    const mario = [[0,0,7,7,7,7,0,0,0,0],[0,7,7,7,7,7,7,7,7,0],[0,2,2,2,1,2,2,2,0,0],[2,2,2,2,1,1,2,2,2,0],[4,4,5,5,0,2,2,2,2,0],[0,2,2,2,2,2,2,2,0,0],[1,1,1,1,1,1,1,1,1,0],[0,1,1,1,1,1,1,1,0,0],[0,0,1,1,0,1,1,0,0,0],[0,6,6,6,0,6,6,6,0,0]];
    mario.forEach((row, r) => row.forEach((v, c) => {
        if (v > 0) {
            for (let z = -1; z <= 1; z++) {
                const voxel = new THREE.Mesh(new THREE.BoxGeometry(rVsize, rVsize, rVsize), mats[v]);
                voxel.position.set((c - 5) * rVsize, (10 - r) * rVsize, z * rVsize);
                reaperGroup.add(voxel);
            }
        }
    }));
    reaperLabel = createTextSprite("DR. REAPER", "#00ffcc");
    reaperLabel.position.y = 100000;
    reaperGroup.add(reaperLabel);
    agentsContainer.add(reaperGroup);

    snakeGroup = new THREE.Group();
    const sMat = new THREE.MeshLambertMaterial({ color: 0x10b981 });
    snakeGroup.add(new THREE.Mesh(new THREE.BoxGeometry(32500, 32500, 32500), sMat));
    snakeLabel = createTextSprite("SN-008 SNAKE", "#10b981");
    snakeLabel.position.y = 80000;
    snakeGroup.add(snakeLabel);
    agentsContainer.add(snakeGroup);
    snakeSegments = [];
    const baseBody = 3; // 🚂 3 Body segments
    const baseTail = 4; // 🧨 4 Tapering tail segments
    for(let i=1; i <= (baseBody + baseTail); i++) {
        let size;
        if (i <= baseBody) {
            size = 30000; // Constant body size
        } else {
            size = 30000 - (i - baseBody) * 4500; // Tapering tail
        }
        const seg = new THREE.Mesh(new THREE.BoxGeometry(size, size, size), sMat);
        seg.position.set(0, 0, -i * 35000);
        agentsContainer.add(seg); // [Fix] Add to agentsContainer to match Y offset
        snakeSegments.push(seg);
    }

    // 🟠 QA-101 Q-BERT: High-Fidelity 3D Model
    quantumGroup = new THREE.Group();
    const qOrange = new THREE.MeshPhongMaterial({ color: 0xff6600, shininess: 50 });
    const qYellow = new THREE.MeshPhongMaterial({ color: 0xffcc00 });
    const qWhite = new THREE.MeshBasicMaterial({ color: 0xffffff });
    const qBlack = new THREE.MeshBasicMaterial({ color: 0x000000 });
    const qRed = new THREE.MeshPhongMaterial({ color: 0xcc0000 });

    // Body (Main Sphere)
    quantumCore = new THREE.Mesh(new THREE.SphereGeometry(35000, 32, 32), qOrange);
    quantumCore.position.y = 35000;
    quantumGroup.add(quantumCore);

    // Nose (The iconic long snout)
    const qNose = new THREE.Mesh(new THREE.CylinderGeometry(8000, 12000, 30000, 16), qOrange);
    qNose.rotation.x = Math.PI / 2;
    qNose.position.set(0, -5000, 35000);
    quantumCore.add(qNose);

    // Eyes
    for(let side of [-1, 1]) {
        const e = new THREE.Mesh(new THREE.SphereGeometry(10000, 16, 16), qWhite);
        e.position.set(side * 15000, 15000, 25000);
        quantumCore.add(e);
        const p = new THREE.Mesh(new THREE.SphereGeometry(4000, 8, 8), qBlack);
        p.position.set(side * 15000, 15000, 33000);
        quantumCore.add(p);
    }
    
    // Feet (Big Red Shoes) - ANCHORED TO BODY BOTTOM
    for(let side of [-1, 1]) {
        const f = new THREE.Mesh(new THREE.SphereGeometry(15000, 16, 16), qRed);
        f.position.set(side * 20000, -30000, 10000);
        quantumCore.add(f);
    }

    quantumLabel = createTextSprite("QA-101 Q-BERT", "#ff6600");
    quantumLabel.position.y = 100000;
    quantumGroup.add(quantumLabel);
    agentsContainer.add(quantumGroup);

    // SE-007 SENTINEL: Sovereign Metallic Shield
    sentinelGroup = new THREE.Group();
    const shieldShape = new THREE.Shape();
    // Modellazione profilo scudo (premium curve)
    shieldShape.moveTo(0, 50000);
    shieldShape.quadraticCurveTo(20000, 60000, 45000, 50000); // Top Right arch
    shieldShape.quadraticCurveTo(45000, 10000, 45000, 0);      // Right Side
    shieldShape.quadraticCurveTo(45000, -40000, 0, -65000);    // Point Bottom
    shieldShape.quadraticCurveTo(-45000, -40000, -45000, 0);   // Left Side
    shieldShape.quadraticCurveTo(-45000, 10000, -45000, 50000); // Top Left arch
    shieldShape.quadraticCurveTo(-20000, 60000, 0, 50000);

    const extrudeSettings = { depth: 12000, bevelEnabled: true, bevelThickness: 4000, bevelSize: 4000, bevelSegments: 5 };
    const shieldGeo = new THREE.ExtrudeGeometry(shieldShape, extrudeSettings);
    
    // Materiale Satin Chrome (Massima resa sotto luce)
    const shieldMat = new THREE.MeshPhysicalMaterial({ 
        color: 0xffffff, 
        metalness: 0.85, 
        roughness: 0.35, 
        clearcoat: 1.0, 
        clearcoatRoughness: 0.1,
        emissive: 0x332211,
        emissiveIntensity: 0.6
    });
    
    sentinelShield = new THREE.Mesh(shieldGeo, shieldMat);
    // Orientamento raddrizzato: 90° su Y e azzeramento X per posizione verticale
    sentinelShield.rotation.x = 0; 
    sentinelShield.rotation.y = Math.PI / 2; 
    
    // 💡 Aura Light dedicata
    const shieldPointLight = new THREE.PointLight(0xffffff, 2, 250000);
    shieldPointLight.position.set(0, 50000, 50000);
    
    sentinelGroup.add(sentinelShield, shieldPointLight);
    sentinelGroup.userData = { mat: shieldMat };

    sentinelLabel = createTextSprite("SE-007 SENTINEL", "#9de9ff");
    sentinelLabel.position.y = 130000;
    sentinelGroup.add(sentinelLabel);
    agentsContainer.add(sentinelGroup);

    // 🤖 R2-D2: CYLINDER + HEMISPHERE (High-Detail Premium Model)
    r2d2Group = new THREE.Group();
    const rLightGray = new THREE.MeshPhongMaterial({ color: 0xe2e8f0, shininess: 60 }); // Body Light Gray
    const rDarkGray = new THREE.MeshPhongMaterial({ color: 0x475569, shininess: 120 }); // Head & Details Slate Gray (True Gray)
    const rBlue = new THREE.MeshPhongMaterial({ color: 0x2563eb, emissive: 0x1e3a8a, emissiveIntensity: 0.2 });
    const rBlack = new THREE.MeshBasicMaterial({ color: 0x000000 });
    const rIndicator = new THREE.MeshBasicMaterial({ color: 0x94a3b8 }); // Default Slate Gray LED

    // 1. Main Body (Cylinder)
    const bodyGeo = new THREE.CylinderGeometry(25000, 25000, 60000, 32);
    const body = new THREE.Mesh(bodyGeo, rLightGray); // Changed from rWhite to rLightGray
    body.position.y = 35000;
    r2d2Group.add(body);

    // 2. Head (Hemisphere)
    const headGeo = new THREE.SphereGeometry(25000, 32, 16, 0, Math.PI * 2, 0, Math.PI / 2);
    const head = new THREE.Mesh(headGeo, rDarkGray); // Changed from rGray to rDarkGray
    head.position.y = 30000;
    body.add(head);

    // [v15.0] RED EYE LED (Logic Core)
    const eyeLEDGeo = new THREE.SphereGeometry(3200, 16, 16);
    const eyeLEDMat = new THREE.MeshBasicMaterial({ color: 0xff0000, transparent: true, opacity: 0.9 });
    const eyeLED = new THREE.Mesh(eyeLEDGeo, eyeLEDMat);
    eyeLED.position.set(0, 12000, 24000);
    head.add(eyeLED);
    r2d2Group.eyeLED = eyeLED; // Reference for animation

    // 3. Eye & Details
    const eye = new THREE.Mesh(new THREE.CylinderGeometry(6000, 6000, 5000, 16), rBlack);
    eye.rotation.x = Math.PI / 2;
    eye.position.set(0, 12000, 22000);
    head.add(eye);

    const statusLight = new THREE.Mesh(new THREE.SphereGeometry(3000, 8, 8), rIndicator);
    statusLight.position.set(10000, 5000, 22000);
    head.add(statusLight);
    r2d2Group.statusLED = statusLight;
    // 🎨 R2-D2 BODY DETAILS (Blue Chest Panels)
    const panelGeo = new THREE.BoxGeometry(20000, 5000, 2000);
    for(let i=0; i<2; i++) {
        const p = new THREE.Mesh(panelGeo, rBlue);
        p.position.set(0, 15000 - i*8000, 24000);
        body.add(p);
    }
    
    const ventGeo = new THREE.CylinderGeometry(4000, 4000, 2000, 16);
    for(let i=0; i<2; i++) {
        const v = new THREE.Mesh(ventGeo, rDarkGray);
        v.rotation.x = Math.PI / 2;
        v.position.set(-10000, 0 - i*10000, 24000);
        body.add(v);
    }

    // 4. Legs (Lateral)
    for(let side of [-1, 1]) {
        const legGroup = new THREE.Group();
        const legMain = new THREE.Mesh(new THREE.BoxGeometry(10000, 50000, 20000), rLightGray); // Use light gray for legs
        legGroup.add(legMain);
        
        const foot = new THREE.Mesh(new THREE.BoxGeometry(20000, 15000, 35000), rDarkGray);
        foot.position.y = -30000;
        legGroup.add(foot);
        
        legGroup.position.set(side * 35000, 35000, 0);
        r2d2Group.add(legGroup);
    }

    // 5. Middle Foot
    const midFoot = new THREE.Mesh(new THREE.BoxGeometry(15000, 12000, 25000), rDarkGray);
    midFoot.position.set(0, 5000, 15000);
    r2d2Group.add(midFoot);

    r2d2Label = createTextSprite("R2-D2 WAREHOUSE", "#3b82f6");
    r2d2Label.position.y = 120000;
    r2d2Group.add(r2d2Label);
    agentsContainer.add(r2d2Group);

    // SY-009 SYNTH: KIRBY-FIED CORE
    synthGroup = new THREE.Group();
    // 🌸 Enhanced Kirby Pink (More saturated to avoid appearing white)
    const syMat = new THREE.MeshPhongMaterial({ color: 0xff4d94, emissive: 0xff0066, emissiveIntensity: 0.5, shininess: 200 }); 
    window.synthMat = syMat;
    const redMatKirby = new THREE.MeshPhongMaterial({ color: 0xef4444 }); // Kirby Feet
    const blackMatKirby = new THREE.MeshBasicMaterial({ color: 0x000000 });
    const whiteMatKirby = new THREE.MeshBasicMaterial({ color: 0xffffff });

    const synthCore = new THREE.Mesh(new THREE.SphereGeometry(40000, 32, 32), syMat);
    synthCore.name = "synth_core";
    window.synthMesh = synthCore;
    synthGroup.add(synthCore);
    
    window.synthSparkGroup = new THREE.Group();
    synthCore.add(window.synthSparkGroup);
    
    for(let i=0; i<8; i++) {
        const beamGeom = new THREE.CylinderGeometry(0, 15000, 300000, 8);
        const beamMat = new THREE.MeshBasicMaterial({ color: 0xffffff, transparent: true, opacity: 0.8, blending: THREE.AdditiveBlending });
        const beam = new THREE.Mesh(beamGeom, beamMat);
        beam.rotation.x = Math.PI / 2;
        beam.position.z = 150000;
        beam.visible = false;
        window.synthSparkGroup.add(beam);
    }

    // Eyes
    for(let side of [-1, 1]) {
        const eye = new THREE.Mesh(new THREE.SphereGeometry(6000, 16, 16), blackMatKirby);
        eye.position.set(side*12000, 15000, 35000);
        eye.scale.set(0.6, 1.4, 0.2); // Oval shape for Kirby eyes
        const pupil = new THREE.Mesh(new THREE.SphereGeometry(2000, 8, 8), whiteMatKirby);
        pupil.position.set(0, 4000, 1000);
        eye.add(pupil);
        synthCore.add(eye);
    }
    // Mouth
    const mouth = new THREE.Mesh(new THREE.SphereGeometry(5000, 16, 8, 0, Math.PI), redMatKirby);
    window.synthMouth = mouth;
    mouth.position.set(0, 0, 38000);
    mouth.rotation.x = Math.PI/2;
    synthCore.add(mouth);

    // Feet
    for(let side of [-1, 1]) {
        const foot = new THREE.Mesh(new THREE.SphereGeometry(15000, 16, 16), redMatKirby);
        foot.name = "synth_foot";
        foot.position.set(side*25000, -35000, 0);
        foot.scale.set(1.5, 0.8, 1.2); // Flat oval shape for Kirby feet
        synthCore.add(foot); // Parented to core for sync movement
    }
    // Hands
    for(let side of [-1, 1]) {
        const hand = new THREE.Mesh(new THREE.SphereGeometry(12000, 16, 16), syMat);
        hand.name = "synth_hand";
        hand.position.set(side*45000, 0, 0);
        synthCore.add(hand); // Parented to core for sync movement
    }
    
    // Sub-Agents with Specific Roles & Colors
    synthSubAgents = [];
    const subRoles = ["Drafting", "Critique", "Polishing"];
    const subColors = [0x22d3ee, 0xf59e0b, 0x10b981]; 
    for(let i=0; i<3; i++) {
        const sub = new THREE.Mesh(new THREE.BoxGeometry(12000, 12000, 12000), new THREE.MeshPhongMaterial({ color: subColors[i], emissive: subColors[i], emissiveIntensity: 0 }));
        sub.name = "synth_sub";
        sub.role = subRoles[i];
        sub.baseColor = subColors[i];
        synthGroup.add(sub);
        synthSubAgents.push(sub);
    }

    synthLabel = createTextSprite("SY-009 SYNTH", "#a855f7");
    synthLabel.position.y = 100000;
    synthGroup.add(synthLabel);
    agentsContainer.add(synthGroup);

    // 🛸 [STAR WARS ENGINE] Helper per creare navi High-Fidelity
    function createXWingMesh(hullColor, stripeColor, canopyColor) {
        const group = new THREE.Group();
        const hullMat = new THREE.MeshPhongMaterial({ color: hullColor, shininess: 50 });
        const stripeMat = new THREE.MeshPhongMaterial({ color: stripeColor });
        const engineMat = new THREE.MeshPhongMaterial({ color: 0x334155 });
        const canopyMat = new THREE.MeshPhongMaterial({ color: canopyColor, transparent: true, opacity: 0.5 });
        const glowMat = new THREE.MeshBasicMaterial({ color: 0x60a5fa, transparent: true, opacity: 0.8 });

        // 1. Fusoliera (Puntata verso +Z)
        const body = new THREE.Mesh(new THREE.CylinderGeometry(500, 3000, 20000, 8), hullMat);
        body.rotation.x = Math.PI / 2;
        group.add(body);
        
        const nose = new THREE.Mesh(new THREE.CylinderGeometry(100, 500, 8000, 8), hullMat);
        nose.rotation.x = Math.PI / 2; nose.position.z = 14000;
        group.add(nose);

        const cockpit = new THREE.Mesh(new THREE.SphereGeometry(2500, 16, 16), canopyMat);
        cockpit.scale.set(1, 0.6, 2); cockpit.position.set(0, 1500, 4000);
        group.add(cockpit);

        // 2. Ali a X
        for(let i=0; i<4; i++) {
            const wGroup = new THREE.Group();
            const wing = new THREE.Mesh(new THREE.BoxGeometry(15000, 500, 6000), hullMat);
            wing.position.x = 7500; wGroup.add(wing);
            
            const stripe = new THREE.Mesh(new THREE.BoxGeometry(2000, 600, 6200), stripeMat);
            stripe.position.x = 11000; wGroup.add(stripe);

            const eng = new THREE.Mesh(new THREE.CylinderGeometry(1500, 1800, 8000, 12), engineMat);
            eng.rotation.x = Math.PI / 2; eng.position.set(1000, 0, -3000);
            wGroup.add(eng);

            const glow = new THREE.Mesh(new THREE.CircleGeometry(1400, 12), glowMat);
            glow.position.set(1000, 0, -7001); glow.rotateY(Math.PI);
            wGroup.add(glow);

            const cannon = new THREE.Mesh(new THREE.CylinderGeometry(200, 200, 12000), hullMat);
            cannon.rotateX(Math.PI / 2); cannon.position.set(14500, 0, 4000);
            wGroup.add(cannon);

            wGroup.rotation.z = (Math.PI / 4) + (i * Math.PI / 2);
            group.add(wGroup);
        }
        return group;
    }

    // FS-77 FILE-SKY-WALKER: High-Fidelity X-Wing
    skywalkerGroup = createXWingMesh(0xd1d5db, 0xef4444, 0x3b82f6);
    skywalkerGroup.rotation.order = 'YXZ';
    
    skywalkerLabel = createTextSprite("FS-77 SKY-WALKER", "#ef4444");
    skywalkerLabel.position.y = 60000;
    skywalkerGroup.add(skywalkerLabel);
    agentsContainer.add(skywalkerGroup);

    // YO-001 YODA: High-Fidelity Jedi X-Wing (Green)
    yodaGroup = createXWingMesh(0xecfdf5, 0x10b981, 0x059669);
    yodaGroup.rotation.order = 'YXZ';
    
    yodaLabel = createTextSprite("YO-001 YODA-FILE-SEARCHER", "#4ade80");
    yodaLabel.position.y = 60000;
    yodaGroup.add(yodaLabel);
    agentsContainer.add(yodaGroup);

    // DN-099 MANDALORIAN: N-1 Starfighter (Chrome / Yellow)
    mandalorianGroup = new THREE.Group();
    mandalorianGroup.rotation.order = 'YXZ';
    const chromeMat = new THREE.MeshStandardMaterial({ color: 0xc0c0c0, metalness: 0.9, roughness: 0.1 });
    const mandoYellowMat = new THREE.MeshBasicMaterial({ color: 0xfacc15 });
    const mandoDarkMat = new THREE.MeshStandardMaterial({ color: 0x27272a });

    // 1. Sleek Fuselage
    const mandoBody = new THREE.Mesh(new THREE.CylinderGeometry(2000, 3500, 25000, 8), chromeMat);
    mandoBody.rotation.x = Math.PI / 2;
    const mandoNose = new THREE.Mesh(new THREE.ConeGeometry(2000, 10000, 8), chromeMat);
    mandoNose.rotation.x = Math.PI / 2;
    mandoNose.position.z = 17500;
    const mandoTail = new THREE.Mesh(new THREE.ConeGeometry(1500, 45000, 8), chromeMat);
    mandoTail.rotation.x = -Math.PI / 2;
    mandoTail.position.z = -35000;
    mandalorianGroup.add(mandoBody, mandoNose, mandoTail);

    // 2. Engines (N-1 specific large pods)
    for(let i=0; i<2; i++) {
        const side = i === 0 ? 1 : -1;
        const engineContainer = new THREE.Group();
        const engBody = new THREE.Mesh(new THREE.CylinderGeometry(3500, 3500, 18000, 12), chromeMat);
        engBody.rotation.x = Math.PI/2;
        const engNose = new THREE.Mesh(new THREE.ConeGeometry(3500, 8000, 12), mandoDarkMat);
        engNose.rotation.x = Math.PI/2;
        engNose.position.z = 13000;
        const engTail = new THREE.Mesh(new THREE.CylinderGeometry(800, 3500, 12000, 12), chromeMat);
        engTail.rotation.x = Math.PI/2;
        engTail.position.z = -15000;
        
        // Yellow stripe
        const stripe = new THREE.Mesh(new THREE.TorusGeometry(3600, 400, 8, 24), mandoYellowMat);
        stripe.position.z = 5000;
        stripe.rotation.x = Math.PI/2;

        engineContainer.add(engBody, engNose, engTail, stripe);
        
        // [v18.0] Mando Thruster Glow
        const thrusterGeo = new THREE.CylinderGeometry(800, 2500, 5000, 8);
        const thrusterMat = new THREE.MeshPhongMaterial({ color: 0x3b82f6, emissive: 0x3b82f6, emissiveIntensity: 2.0, transparent: true, opacity: 0.8 });
        const thruster = new THREE.Mesh(thrusterGeo, thrusterMat);
        thruster.name = "mando_thruster";
        thruster.rotation.x = Math.PI / 2;
        thruster.position.z = -20000;
        engineContainer.add(thruster);

        engineContainer.position.x = side * 15000;
        engineContainer.position.z = 5000;
        mandalorianGroup.add(engineContainer);
        
        // Wing connector
        const connector = new THREE.Mesh(new THREE.BoxGeometry(15000, 1000, 8000), chromeMat);
        connector.position.set(side * 7500, 0, 5000);
        mandalorianGroup.add(connector);
    }
    
    mandalorianLabel = createTextSprite("DN-099 MANDALORIAN", "#facc15");
    mandalorianLabel.position.y = 40000;
    mandalorianGroup.add(mandalorianLabel);
    agentsContainer.add(mandalorianGroup);

    // AG-001 fleet is now dynamic in syncMeshWormholes
    smithLabel = createTextSprite("AG-001 SECURITY FLEET", "#00ff41");
    window.smithLasers = [];

    bridgerGroup = new THREE.Group();
    const bMat = new THREE.MeshPhongMaterial({ color: 0x3b82f6, emissive: 0x1e40af, shininess: 100, wireframe: false });
    const diamondGeo = new THREE.OctahedronGeometry(35000);
    const bridgeArch = new THREE.Mesh(diamondGeo, bMat);
    bridgeArch.rotation.z = Math.PI / 4;
    const ringGeo = new THREE.TorusGeometry(50000, 2000, 16, 100);
    const ringMat = new THREE.MeshPhongMaterial({ color: 0x00ffff, emissive: 0x00ffff, transparent: true, opacity: 0.4 });
    const ring1 = new THREE.Mesh(ringGeo, ringMat);
    const ring2 = new THREE.Mesh(ringGeo, ringMat);
    ring2.rotation.x = Math.PI / 2;
    const bridgeCore = new THREE.Mesh(new THREE.IcosahedronGeometry(12000), new THREE.MeshPhongMaterial({ color: 0xffffff, emissive: 0xffffff }));
    bridgerGroup.bridgeCore = bridgeCore;
    bridgerGroup.rings = [ring1, ring2];
    bridgerGroup.add(bridgeArch, bridgeCore, ring1, ring2);
    bridgerLabel = createTextSprite("CB-003 BRIDGER", "#3b82f6");
    bridgerLabel.position.y = 100000;
    bridgerGroup.add(bridgerLabel);
    agentsContainer.add(bridgerGroup);

    // 🖨️ PB-404 PRESSMAN: The Sovereign Paperboy (v10.0 - Retro Pixel Edition)
    pressmanGroup = new THREE.Group();
    const pbTexture = new THREE.TextureLoader().load('/static/img/paperboy_sprite.gif', 
        (tex) => { console.log("✅ [PB-404] Paperboy Animated Sprite Loaded Successfully"); },
        undefined,
        (err) => { console.error("❌ [PB-404] Paperboy Sprite LOAD ERROR:", err); }
    );
    pbTexture.magFilter = THREE.NearestFilter;
    pbTexture.minFilter = THREE.NearestFilter;
    
    const pbMat = new THREE.SpriteMaterial({ 
        map: pbTexture, 
        transparent: true, 
        opacity: 1.0,
        color: 0xffffff,
        depthTest: false, // Ensure it's visible through the nebula cloud
        sizeAttenuation: true
    });
    const pbSprite = new THREE.Sprite(pbMat);
    pbSprite.scale.set(160000, 160000, 1); // Extra large for impact
    pressmanGroup.add(pbSprite);
    pressmanGroup.pbSprite = pbSprite;
    pressmanGroup.pbTexture = pbTexture;

    // [v9.8] Visibility Helper: Add a powerful glow point
    const glow = new THREE.PointLight(0xffffff, 5, 400000);
    pressmanGroup.add(glow);
    
    // Add a circular glow halo behind the sprite
    const haloGeo = new THREE.CircleGeometry(90000, 32);
    const haloMat = new THREE.MeshBasicMaterial({ 
        color: 0xffffff, 
        transparent: true, 
        opacity: 0.15,
        depthWrite: false
    });
    const halo = new THREE.Mesh(haloGeo, haloMat);
    pressmanGroup.add(halo);

    // Newspaper Throwing Pool
    pressmanNewspapers = new THREE.Group();
    agentsContainer.add(pressmanNewspapers);

    pressmanLabel = createTextSprite("PB-404 PAPERBOY", "#ffffff");
    pressmanLabel.position.y = 110000;
    pressmanGroup.add(pressmanLabel);

    // [v9.8] Initial Positioning for visibility
    pressmanGroup.position.set(1200000, 400000, 1200000);
    agentsContainer.add(pressmanGroup);
    
    // Orbiting papers (The "Rotary Press" effect)
    pressmanPapers = [];
    for(let i=0; i<3; i++) {
        const pGeo = new THREE.PlaneGeometry(15000, 20000);
        const pMat = new THREE.MeshBasicMaterial({ color: 0xffffff, side: THREE.DoubleSide, transparent: true });
        const p = new THREE.Mesh(pGeo, pMat);
        pressmanGroup.add(p);
        pressmanPapers.push(p);
    }
    
    agentsContainer.add(pressmanGroup);

    // [v9.8] Internal Helper: Throw Newspaper
    window.spawnPaperboyNews = function(pos) {
        const pGeo = new THREE.PlaneGeometry(8000, 11000);
        const pMat = new THREE.MeshBasicMaterial({ color: 0xffffff, side: THREE.DoubleSide, transparent: true });
        const news = new THREE.Mesh(pGeo, pMat);
        news.position.copy(pos);
        
        // Random trajectory
        const angle = Math.random() * Math.PI * 2;
        news.userData.velocity = new THREE.Vector3(Math.cos(angle) * 15000, (Math.random() - 0.5) * 10000, Math.sin(angle) * 15000);
        news.userData.rotSpeed = new THREE.Vector3(Math.random(), Math.random(), Math.random()).multiplyScalar(0.2);
        news.userData.birth = Date.now();
        
        pressmanNewspapers.add(news);

        const arts = document.getElementById('val-pressman-artifacts');
        if (arts) {
            let count = parseInt(arts.innerText) || 0;
            arts.innerText = count + 1;
        }
    };
}
function updateAgentPhysics() {
    // [v12.0] NERD MODE Check: Hide/Show all agents in Cycloscope
    if (agentsContainer) {
        agentsContainer.visible = (window.NERD_MODE_ACTIVE !== false);
    }
    if (window.NERD_MODE_ACTIVE === false) return;

    const now = Date.now();
    const time = now * 0.001;
    const exp = 1.0; 

    // 🧹 [JANITRON] Logic (Always Patrolling)
    if (janitronGroup) {
        const isPurging = (janitronFlashTime > 0);
        if (isPurging) {
            janitronFlashTime--;
            const loopStage = (time * 6) % 3; 
            let loopColor = 0x3b82f6; 
            if (loopStage > 2) loopColor = 0xef4444; 
            else if (loopStage > 1) loopColor = 0xf97316; 
            janitronGroup.userData.mat.emissive.setHex(loopColor);
            janitronGroup.userData.mat.color.setHex(loopColor);
            janitronGroup.userData.mat.emissiveIntensity = 3.0 + Math.sin(time * 25) * 1.5;
            const pulse = 1.0 + Math.sin(time * 25) * 0.15;
            janitronGroup.scale.set(pulse, pulse, pulse);
        } else {
            janitronGroup.userData.mat.emissive.setHex(0x422006);
            janitronGroup.userData.mat.color.setHex(0xfacc15); 
            janitronGroup.userData.mat.emissiveIntensity = 0.5;
            janitronGroup.scale.set(1, 1, 1);
        }

        const mouthSpeed = isPurging ? 15 : 6;
        const mouthOpen = Math.abs(Math.sin(time * mouthSpeed)) * 0.7;
        janitronTop.rotation.x = -mouthOpen;
        janitronBottom.rotation.x = mouthOpen;

        if (janitronGroup.position.distanceTo(janitronTargetPos) < 100000 * exp) {
            const scope = 1500000 * exp;
            janitronTargetPos.set((Math.random() - 0.5) * scope * 2, (Math.random() - 0.5) * 600000 * exp, (Math.random() - 0.5) * scope * 2);
        }
        const orbitX = Math.cos(time * 0.5) * 80000 * exp;
        const orbitZ = Math.sin(time * 0.5) * 80000 * exp;
        const nextPos = new THREE.Vector3(janitronTargetPos.x + orbitX, janitronTargetPos.y, janitronTargetPos.z + orbitZ);
        const lookDir = nextPos.clone().sub(janitronGroup.position);
        if (lookDir.length() > 1000) janitronGroup.rotation.y = Math.atan2(lookDir.x, lookDir.z); 
        janitronGroup.position.lerp(nextPos, 0.05);
    }

    // 🧪 [DISTILLER]
    if (distillerGroup) {
        if (distillerFlashTime > 0) distillerFlashTime--;
        distillerGroup.position.lerp(distillerTargetPos, 0.03);
        distillerGroup.position.y += Math.sin(time * 2) * 800 * exp;
        distillerGroup.rotation.y += 0.02;
    }

    // ☦️ [REAPER]
    if (reaperGroup) {
        reaperGroup.position.lerp(reaperTargetPos, 0.04);
        // Always face camera but stay upright (Billboarding)
        reaperGroup.quaternion.copy(camera.quaternion);
        reaperGroup.rotation.x = 0; 
        reaperGroup.rotation.z = 0;
        reaperGroup.position.y += Math.cos(time * 1.5) * 500 * exp;
    }

    // 🐍 [SNAKE]
    if (snakeGroup && now - lastSnakeStep > 125) {
        lastSnakeStep = now;
        let prevPos = snakeGroup.position.clone();
        const diff = snakeCurrentTarget.clone().sub(snakeGroup.position);
        if (diff.length() < 100000 * exp) {
            snakeCurrentTarget.set((Math.random()-0.5)*3000000 * exp, (Math.random()-0.5)*1500000 * exp, (Math.random()-0.5)*3000000 * exp);
        }
        if (Math.abs(diff.x) > Math.abs(diff.y) && Math.abs(diff.x) > Math.abs(diff.z)) snakeDirection.set(Math.sign(diff.x), 0, 0);
        else if (Math.abs(diff.y) > Math.abs(diff.z)) snakeDirection.set(0, Math.sign(diff.y), 0);
        else snakeDirection.set(0, 0, Math.sign(diff.z));
        
        snakeGroup.position.add(snakeDirection.clone().multiplyScalar(35000 * exp));
        snakeGroup.lookAt(snakeGroup.position.clone().add(snakeDirection));
        
        // Ensure segments follow correctly
        snakeSegments.forEach((seg, idx) => { 
            let t = seg.position.clone(); 
            seg.position.lerp(prevPos, 0.8); 
            prevPos = t; 
        });
    }

    // ⚛️ [QUANTUM] (Q-Bert)
    if (quantumGroup && quantumCore) {
        const distToTarget = quantumGroup.position.distanceTo(quantumTargetPos);
        if (distToTarget > 1000 * exp) {
            quantumGroup.position.lerp(quantumTargetPos, 0.05);
            // Q-Bert Jumping Logic
            const jumpHeight = 60000 * exp;
            quantumCore.position.y = Math.abs(Math.sin(time * 8.0)) * jumpHeight;
            quantumCore.rotation.x = -0.2; // Tilt forward
        } else {
            quantumCore.position.y = 0;
            quantumCore.rotation.x = 0;
        }

        quantumCore.rotation.y += 0.04;
        const isFusing = (quantumFlashTime > 0);
        if (quantumFlashTime > 0) quantumFlashTime--; 
        const pulse = 1.0 + Math.sin(time * 10) * (isFusing ? 0.4 : 0.05);
        quantumCore.scale.setScalar(pulse);
    }

    // 🛡️ [SENTINEL] - Infinity Orbit (Lemniscate)
    if (sentinelGroup && sentinelShield) {
        const orbitRadius = 1800000 * exp;
        const t = time * 0.15; // Slow, majestic speed
        
        // Lemniscate of Gerono (Figura a 8 / Infinito)
        const targetX = orbitRadius * Math.cos(t);
        const targetZ = orbitRadius * Math.sin(t) * Math.cos(t);
        const targetY = 1000000 + Math.sin(t * 0.4) * 300000 * exp;
        
        const targetPos = new THREE.Vector3(targetX, targetY, targetZ);
        sentinelGroup.position.lerp(targetPos, 0.05);
        
        // Orientamento: guarda sempre avanti nel percorso
        const nextT = t + 0.01;
        const nextX = orbitRadius * Math.cos(nextT);
        const nextZ = orbitRadius * Math.sin(nextT) * Math.cos(nextT);
        const nextY = 1000000 + Math.sin(nextT * 0.4) * 300000 * exp;
        const lookDir = new THREE.Vector3(nextX, nextY, nextZ).sub(sentinelGroup.position);
        if (lookDir.length() > 100) {
            const angle = Math.atan2(lookDir.x, lookDir.z);
            sentinelGroup.rotation.y = angle;
        }
        
        sentinelShield.rotation.y += 0.03;
        if (sentinelFlashTime > 0) sentinelFlashTime--;
        if (sentinelLightningTime > 0) sentinelLightningTime--;
    }

    // 🎹 [SYNTH]
    if (synthGroup && window.synthMesh) {
        // Jumping Movement
        const distToTarget = synthGroup.position.distanceTo(synthTargetPos);
        if (distToTarget > 1000 * exp) {
            synthGroup.position.lerp(synthTargetPos, 0.05);
            // Hop animation: sin wave for Y offset
            const jumpHeight = 80000 * exp;
            window.synthMesh.position.y = Math.abs(Math.sin(time * 8.0)) * jumpHeight;
            // Slight tilt forward when jumping
            window.synthMesh.rotation.x = -0.2;
        } else {
            window.synthMesh.position.y = 0;
            window.synthMesh.rotation.x = 0;
        }

        // 🌟 RAINBOW SPARK ANIMATION (15s = approx 900 frames at 60fps)
        if (window.synthSparkTime > 0) {
            window.synthSparkTime--;
            
            // 1. Pulsing Body (Unified Core + Hands + Feet)
            const pulse = 1.0 + Math.sin(time * 15.0) * 0.3;
            window.synthMesh.scale.setScalar(pulse);
            // Hands and feet are children of core, but we might want to emphasize their pulse
            window.synthMesh.children.forEach(child => {
                if (child.isMesh && (child.name === "synth_foot" || child.name === "synth_hand")) {
                    child.scale.setScalar(1.0); // They already inherit core's pulse
                    if (child.name === "synth_foot") {
                        child.scale.x = 1.5; child.scale.y = 0.8; child.scale.z = 1.2;
                    }
                }
            });
            
            // 2. Color Vibration (HSL Shimmer)
            const hue = (time * 2.0) % 1;
            window.synthMat.emissive.setHSL(hue, 1.0, 0.6);
            window.synthMat.emissiveIntensity = 2.0 + Math.sin(time * 20.0) * 1.5;
            
            // 3. Mouth Wide Open
            window.synthMouth.scale.setScalar(2.0 + Math.sin(time * 30.0) * 0.5);
            
            // 4. Rainbow Beams
            window.synthSparkGroup.visible = true;
            window.synthSparkGroup.children.forEach((beam, i) => {
                beam.visible = true;
                const beamHue = (hue + i * 0.125) % 1;
                beam.material.color.setHSL(beamHue, 1.0, 0.5);
                beam.rotation.z = time * 5.0 + (i * Math.PI / 4);
                beam.scale.x = 0.5 + Math.sin(time * 10 + i) * 0.5;
                beam.scale.y = 1.0 + Math.sin(time * 5 + i) * 0.5;
            });

            // If sparking, stop the jump height (stay on node)
            window.synthMesh.position.y = 0;
        } else {
            window.synthMouth.scale.setScalar(1.0);
            window.synthSparkGroup.visible = false;
            
            // 🌟 Restore Baseline Appearance
            window.synthMat.emissive.setHex(0xff0066);
            window.synthMat.emissiveIntensity = 0.5;
            
            // Reset scale for all body parts
            window.synthMesh.children.forEach(child => {
                if (child.isMesh && (child.name === "synth_foot" || child.name === "synth_hand")) {
                    if (child.name === "synth_foot") child.scale.set(1.5, 0.8, 1.2);
                    else child.scale.setScalar(1.0);
                }
            });
            window.synthMesh.scale.setScalar(1.0);
        }

        synthSubAgents.forEach((sub, i) => {
            const angle = (time * 2.0) + (i * Math.PI * 2 / 3);
            sub.position.set(Math.cos(angle) * 65000 * exp, Math.sin(angle) * 65000 * exp, Math.sin(angle * 0.5) * 20000 * exp);
            sub.rotation.y += 0.05;
        });
        if (synthFlashTime > 0) synthFlashTime--;
    }

    // 🤖 [R2-D2]
    if (r2d2Group) {
        if (!r2d2Group.userData.localTarget) r2d2Group.userData.localTarget = r2d2TargetPos.clone();
        
        const distToMain = r2d2Group.position.distanceTo(r2d2TargetPos);
        
        if (distToMain > 300000 * exp) {
            // Se il target backend è lontano, vola verso la destinazione (Warehouse Sweep)
            r2d2Group.userData.localTarget.copy(r2d2TargetPos);
            r2d2Group.position.lerp(r2d2TargetPos, 0.04);
        } else {
            // Pattugliamento attivo locale (Micro-Sweep)
            if (r2d2Group.position.distanceTo(r2d2Group.userData.localTarget) < 50000 * exp) {
                const patrolRadius = 400000 * exp;
                r2d2Group.userData.localTarget.set(
                    r2d2TargetPos.x + (Math.random() - 0.5) * patrolRadius,
                    r2d2TargetPos.y + (Math.random() - 0.5) * patrolRadius,
                    r2d2TargetPos.z + (Math.random() - 0.5) * patrolRadius
                );
            }
            r2d2Group.position.lerp(r2d2Group.userData.localTarget, 0.02);
        }

        // Smooth rotation verso la direzione di marcia
        const lookDir = r2d2Group.userData.localTarget.clone().sub(r2d2Group.position);
        if (lookDir.length() > 1000) {
            const targetY = Math.atan2(lookDir.x, lookDir.z);
            let diff = targetY - r2d2Group.rotation.y;
            // Normalizzazione angolo per non fargli fare giri strani
            while (diff < -Math.PI) diff += Math.PI * 2;
            while (diff > Math.PI) diff -= Math.PI * 2;
            r2d2Group.rotation.y += diff * 0.05;
        }

        // [v15.0] RED LED GLOW PULSE & STATUS LIGHT
        if (r2d2Group.eyeLED && r2d2Group.statusLED) {
            const isOperating = r2d2Group.userData.isOperating;
            if (isOperating) {
                // High-frequency color cycling (25Hz) for active operations
                const colors = [0x94a3b8, 0xff0000, 0x00d9ff, 0xffaa00, 0xff0000, 0x00d9ff, 0xffaa00];
                const colorIdx = Math.floor(time * 25) % colors.length;
                const activeColor = colors[colorIdx];
                
                r2d2Group.statusLED.material.color.setHex(activeColor);
                const pulse = 0.6 + Math.abs(Math.sin(time * 25)) * 0.4;
                r2d2Group.statusLED.scale.setScalar(1.2 + pulse * 0.8);

                r2d2Group.eyeLED.material.opacity = pulse;
                r2d2Group.eyeLED.scale.setScalar(1.0 + pulse * 0.3);
                
                // --- COLOR NEARBY NODES (Thematic Grouping Effect) ---
                if (window.pointsMesh) {
                    const r2Pos = r2d2Group.position;
                    const effectRadius = 500000 * exp;
                    const targetColor = new THREE.Color(activeColor);
                    
                    if (window.pointsMesh.isInstancedMesh) {
                        const matrix = new THREE.Matrix4();
                        const pos = new THREE.Vector3();
                        let needsColorUpdate = false;
                        const pCount = Math.min(window.pointsMesh.count, 30000);
                        
                        for (let i = 0; i < pCount; i++) {
                            window.pointsMesh.getMatrixAt(i, matrix);
                            pos.setFromMatrixPosition(matrix);
                            const distSq = (pos.x - r2Pos.x)**2 + (pos.y - r2Pos.y)**2 + (pos.z - r2Pos.z)**2;
                            
                            if (distSq < effectRadius * effectRadius) {
                                window.pointsMesh.setColorAt(i, targetColor);
                                needsColorUpdate = true;
                            }
                        }
                        if (needsColorUpdate && window.pointsMesh.instanceColor) {
                            window.pointsMesh.instanceColor.needsUpdate = true;
                        }
                    } else if (window.pointsMesh.geometry && window.pointsMesh.geometry.attributes.color) {
                        const posAttr = window.pointsMesh.geometry.attributes.position;
                        const colAttr = window.pointsMesh.geometry.attributes.color;
                        let needsColorUpdate = false;
                        const pCount = Math.min(posAttr.count, 30000);
                        
                        for (let i = 0; i < pCount; i++) {
                            const px = posAttr.getX(i);
                            const py = posAttr.getY(i);
                            const pz = posAttr.getZ(i);
                            const distSq = (px - r2Pos.x)**2 + (py - r2Pos.y)**2 + (pz - r2Pos.z)**2;
                            
                            if (distSq < effectRadius * effectRadius) {
                                colAttr.setXYZ(i, targetColor.r, targetColor.g, targetColor.b);
                                needsColorUpdate = true;
                            }
                        }
                        if (needsColorUpdate) colAttr.needsUpdate = true;
                    }
                }
            } else {
                r2d2Group.statusLED.material.color.setHex(0x808080);
                r2d2Group.statusLED.scale.setScalar(1.0);
                
                r2d2Group.eyeLED.material.opacity = 0.2;
                r2d2Group.eyeLED.scale.setScalar(1.0);
            }
        }
    }

    // 🖨️ [PRESSMAN / PAPERBOY] - Logic consolidated below


    // 🕶️ [SMITH] - Frenetic Upgrade + Wormhole Proximity
    Object.keys(smithFleetGroups).forEach(pid => {
        const group = smithFleetGroups[pid];
        let target = smithTargetPositions[pid] ? smithTargetPositions[pid].clone() : new THREE.Vector3(0,0,0);
        
        // 🕶️ [v10.6] Smith-Positioning Sync: 3000 from Bullet Origin (Forward Path)
        if (window.meshWormholes && window.meshWormholes[pid]) {
            const wh = window.meshWormholes[pid];
            if (wh.group) {
                // [v10.7] Ricalibrazione dinamica: Smith avanza all'80% dell'espansione
                const exp = (window.nebulaExpansionFactor || 1.0);
                const advanceDist = exp * 1500000 * 0.8;
                const bulletOriginLocal = new THREE.Vector3(0, 0, advanceDist); 
                const smithPosLocal = bulletOriginLocal.clone().add(new THREE.Vector3((Math.random()-0.5)*40000, (Math.random()-0.5)*40000, -5000)); 
                target = smithPosLocal.clone().applyMatrix4(wh.group.matrixWorld);
            }
        } else if (window.meshWormholes) {
            // Fallback: nearest wormhole if explicit ID map fails
            let nearestW = null, minDist = Infinity;
            Object.values(window.meshWormholes).forEach(w => {
                const d = group.position.distanceTo(w.group.position);
                if (d < minDist) { minDist = d; nearestW = w; }
            });
            if (nearestW && minDist < 800000 * exp) {
                target.lerp(nearestW.group.position, 0.4);
            }
        }

        group.position.lerp(target, 0.05);
        
        // 🛠️ [Fix v7.1] Update Shader Uniforms for Matrix Rain
        group.children.forEach(child => {
            if (child.material && child.material.uniforms) {
                child.material.uniforms.time.value = time;
            }
        });
        
        const isLightningActive = (window.smithLightningTime && window.smithLightningTime[pid] > 0);
        if (isLightningActive) {
            window.smithLightningTime[pid]--;
            group.position.x += (Math.random()-0.5)*15000;
            group.position.y += (Math.random()-0.5)*15000;
            const glitchHue = (now * 0.01) % 1;
            group.children.forEach(child => {
                if (child.material && child.material.emissive) {
                    child.material.emissive.setHSL(glitchHue, 1.0, 0.6);
                    child.material.emissiveIntensity = 4.0 + Math.sin(time*50)*2.0;
                }
            });
            if (Math.random() > 0.7) spawnSmithLightning(group, target.clone().add(new THREE.Vector3((Math.random()-0.5)*500000, (Math.random()-0.5)*500000, (Math.random()-0.5)*500000)), true);
        } else {
            group.children.forEach(child => {
                if (child.material && child.material.emissive) {
                    child.material.emissive.setHex(0x00ff41);
                    child.material.emissiveIntensity = 0.5;
                }
            });
        }
        group.quaternion.copy(camera.quaternion);
    });

    // 🛰️ [SKYWALKER]
    if (skywalkerGroup) {
        skywalkerGroup.scale.setScalar(1.0); 
        skywalkerGroup.up.set(0, 1, 0);
        
        // --- Realistic Fighter Dynamics ---
        const distToTarget = skywalkerGroup.position.distanceTo(skywalkerTargetPos);
        const patrolTime = time * 0.25;
        const sweepRadius = 350000 * exp;
        
        const effectiveTarget = skywalkerTargetPos.clone();
        if (distToTarget < sweepRadius * 1.5) {
            // Wide sweeping patrols through and around the nebula
            effectiveTarget.x += Math.sin(patrolTime) * sweepRadius * 1.2;
            effectiveTarget.y += Math.sin(patrolTime * 1.5) * sweepRadius * 0.4;
            effectiveTarget.z += Math.sin(patrolTime * 0.8) * sweepRadius * 0.9;
        }

        skywalkerGroup.position.lerp(effectiveTarget, 0.015);
        
        const dir = effectiveTarget.clone().sub(skywalkerGroup.position).normalize();
        if (dir.lengthSq() > 0.0001) {
            const targetYaw = Math.atan2(dir.x, dir.z);
            const horizontalDist = Math.sqrt(dir.x * dir.x + dir.z * dir.z);
            const targetPitch = Math.atan2(-dir.y, horizontalDist);
            
            let yawDiff = targetYaw - skywalkerGroup.rotation.y;
            while (yawDiff > Math.PI) yawDiff -= Math.PI * 2;
            while (yawDiff < -Math.PI) yawDiff += Math.PI * 2;
            
            const targetRoll = -Math.max(-0.85, Math.min(0.85, yawDiff * 2.5));
            
            skywalkerGroup.rotation.order = 'YXZ';
            skywalkerGroup.rotation.x = THREE.MathUtils.lerp(skywalkerGroup.rotation.x, targetPitch, 0.08);
            skywalkerGroup.rotation.y += yawDiff * 0.06;
            skywalkerGroup.rotation.z = THREE.MathUtils.lerp(skywalkerGroup.rotation.z, targetRoll, 0.08);
        }
        
        if (skywalkerLasers.length > 0) {
            skywalkerLasers.forEach(l => {
                l.scale.x += 1.0;
                l.material.opacity -= 0.02;
                if(l.material.opacity <= 0) {
                    if (typeof safeDispose === 'function') safeDispose(l);
                    else scene.remove(l);
                }
            });
            skywalkerLasers = skywalkerLasers.filter(l => l.material.opacity > 0);
        }
    }

    // 🌌 [YODA]
    if (yodaGroup) {
        yodaGroup.scale.setScalar(1.0); 
        yodaGroup.up.set(0, 1, 0);

        // --- Agile Jedi Starfighter Dynamics ---
        const distToTarget = yodaGroup.position.distanceTo(yodaTargetPos);
        const patrolTime = time * 0.4;
        const sweepRadius = 250000 * exp;

        const effectiveTarget = yodaTargetPos.clone();
        if (distToTarget < sweepRadius * 1.5) {
            // Tight, erratic weaving and chasing
            effectiveTarget.x += Math.sin(patrolTime * 1.2) * sweepRadius * 0.8;
            effectiveTarget.y += Math.sin(patrolTime * 2.5) * sweepRadius * 0.5;
            effectiveTarget.z += Math.cos(patrolTime * 0.9) * sweepRadius * 0.7;
        }

        yodaGroup.position.lerp(effectiveTarget, 0.035);
        
        const dir = effectiveTarget.clone().sub(yodaGroup.position).normalize();
        if (dir.lengthSq() > 0.0001) {
            const targetYaw = Math.atan2(dir.x, dir.z);
            const horizontalDist = Math.sqrt(dir.x * dir.x + dir.z * dir.z);
            const targetPitch = Math.atan2(-dir.y, horizontalDist);
            
            let yawDiff = targetYaw - yodaGroup.rotation.y;
            while (yawDiff > Math.PI) yawDiff -= Math.PI * 2;
            while (yawDiff < -Math.PI) yawDiff += Math.PI * 2;
            
            const targetRoll = -Math.max(-1.2, Math.min(1.2, yawDiff * 3.0));
            
            yodaGroup.rotation.order = 'YXZ';
            yodaGroup.rotation.x = THREE.MathUtils.lerp(yodaGroup.rotation.x, targetPitch, 0.12);
            yodaGroup.rotation.y += yawDiff * 0.10;
            yodaGroup.rotation.z = THREE.MathUtils.lerp(yodaGroup.rotation.z, targetRoll, 0.12);
        }
        
        if (window.yodaAura) {
            window.yodaAura.position.copy(yodaGroup.position);
            window.yodaAura.rotation.y += 0.02;
        }

        if (yodaGroup.userData.laser && yodaGroup.userData.laserTarget) {
            if (Math.random() > 0.85) {
                const target = yodaGroup.userData.laserTarget;
                spawnYodaBullet(yodaGroup.position.clone(), new THREE.Vector3(target.x * exp, target.y * exp, target.z * exp));
            }
        }
    }

    // ⚔️ [MANDALORIAN]
    if (mandalorianGroup) {
        mandalorianGroup.scale.setScalar(1.0); 
        mandalorianGroup.up.set(0, 1, 0);
        
        const status = mandalorianGroup.userData.status || "";
        const lerpFactor = (status.includes("TRAVELING") || status.includes("RETURNING")) ? 0.25 : 0.06;

        // --- Idle Patrol Logic (Telemetry Centered) ---
        const distToTarget = mandalorianGroup.position.distanceTo(mandalorianTargetPos);
        const driftX = Math.sin(time * 0.4) * 60000 * exp;
        const driftY = Math.cos(time * 0.3) * 50000 * exp;
        const driftZ = Math.sin(time * 0.5) * 60000 * exp;

        const effectiveTarget = mandalorianTargetPos.clone();
        if (distToTarget < 400000 * exp && !status.includes("SCANNING") && !status.includes("MERGING")) {
            effectiveTarget.x += driftX;
            effectiveTarget.y += driftY;
            effectiveTarget.z += driftZ;
        }

        mandalorianGroup.position.lerp(effectiveTarget, lerpFactor);
        
        const dir = mandalorianTargetPos.clone().sub(mandalorianGroup.position);
        if (dir.length() > 500) {
            // [v17.0] Stable Directional Orientation (Yaw Only)
            const angle = Math.atan2(dir.x, dir.z);
            mandalorianGroup.rotation.set(0, angle, 0, 'YXZ');
        }
        
        if (window.mandoPulse) {
            window.mandoPulse.position.copy(mandalorianGroup.position);
            const pScale = 2.0 + Math.sin(Date.now() * 0.005) * 1.5;
            window.mandoPulse.scale.setScalar(pScale);
        }
        
        if (status.includes("SCANNING") && mandalorianGroup.userData.laserTarget) {
            if (typeof window.updateMandoScanner === 'function') {
                window.updateMandoScanner(mandalorianGroup.position, mandalorianGroup.userData.laserTarget);
            }
        } else {
            if (typeof window.hideMandoScanner === 'function') window.hideMandoScanner();
        }

        // 🚀 [v18.0] THRUSTER ANIMATION
        const isHighSpeed = status.includes("TRAVELING") || status.includes("RETURNING");
        mandalorianGroup.traverse(child => {
            if (child.name === "mando_thruster") {
                const baseIntensity = isHighSpeed ? 6.0 : 1.5;
                child.material.emissiveIntensity = baseIntensity + Math.sin(time * 40) * (isHighSpeed ? 3.0 : 0.5);
                child.scale.set(1, 1, isHighSpeed ? 2.5 + Math.sin(time*50)*0.5 : 1.0);
            }
        });
        
        if (status.includes("MERGING") && mandalorianGroup.userData.laserTarget) {
            if (typeof window.triggerMandoMergeEffect === 'function') {
                window.triggerMandoMergeEffect(mandalorianGroup.userData.laserTarget);
            }
        }
    }

    if (yodaBullets.length > 0) {
        yodaBullets.forEach((b, idx) => {
            b.progress += 0.02;
            if (b.progress >= 1.0) {
                if (typeof safeDispose === 'function') safeDispose(b.mesh);
                else scene.remove(b.mesh);
                yodaBullets.splice(idx, 1);
            } else {
                b.mesh.position.lerpVectors(b.start, b.end, b.progress);
                b.mesh.lookAt(b.end);
            }
        });
    }

    // 🌉 [BRIDGER] - Node Orbit (Telemetry Follow)
    if (bridgerGroup && bridgerTargetPos) {
        bridgerGroup.position.lerp(bridgerTargetPos, 0.05);
        bridgerGroup.rotation.y += 0.02;
        if (bridgerPulseTime > 0) bridgerPulseTime--;
        if(bridgerGroup.rings) {
            bridgerGroup.rings[0].rotation.y += 0.08;
            bridgerGroup.rings[1].rotation.x += 0.05;
        }
    }

    // 🖨️ [PAPERBOY ANIMATIONS & PATROL]
    if (pressmanGroup) {
        let finalTarget;
        const telemetryTarget = window.pressmanTargetPos;
        const pbSpeed = time * 0.12;
        
        // Se abbiamo dati telemetrici validi e non la posizione di default (2M), seguili
        if (telemetryTarget && Math.abs(telemetryTarget.x) < 1900000) {
            finalTarget = telemetryTarget.clone();
            finalTarget.y += Math.sin(time * 3.0) * 20000; // Bobbing effect
        } else {
            // 🚴 Orbital Patrol (Fallback)
            const pbRadius = (window.nebulaExpansionFactor || 1.0) * 1500000 * 0.9;
            const targetX = Math.cos(pbSpeed) * pbRadius;
            const targetZ = Math.sin(pbSpeed) * pbRadius;
            const targetY = 400000 + Math.sin(time * 0.5) * 200000;
            finalTarget = new THREE.Vector3(targetX, targetY, targetZ);
        }
        
        pressmanGroup.position.lerp(finalTarget, 0.02);
        // Face movement direction
        pressmanGroup.rotation.y = pbSpeed + Math.PI/2;

        // [v10.0] Ensure Animated GIF updates (only if loaded)
        if (pressmanGroup.pbTexture && pressmanGroup.pbTexture.image) {
            pressmanGroup.pbTexture.needsUpdate = true;
        }

        // Papers orbiting
        if (window.pressmanPapers) {
            window.pressmanPapers.forEach((p, i) => {
                const orbitT = time * 2.0 + (i * Math.PI * 2 / 3);
                p.position.set(Math.cos(orbitT) * 60000, Math.sin(orbitT) * 40000, Math.sin(orbitT * 0.5) * 30000);
                p.rotation.y = orbitT;
                
                // "Pressing" effect: papers fly into the cylinder and back out
                const scale = 0.8 + Math.abs(Math.sin(orbitT * 2)) * 0.4;
                p.scale.set(scale, scale, scale);
            });
        }

        if (pressmanGroup.userData.isPressing) {
            pressmanGroup.scale.setScalar(1.2 + Math.sin(time * 20) * 0.1);
        } else {
            pressmanGroup.scale.setScalar(1.0);
        }

        // 🚴 Pedaling Animation (Sine wave tilt & bob)
        if (pressmanGroup.pbSprite) {
            const pedalTime = time * 8; 
            pressmanGroup.pbSprite.position.y = Math.sin(pedalTime) * 8000;
            pressmanGroup.pbSprite.material.rotation = Math.sin(pedalTime * 0.5) * 0.1;
        }

        // 📰 Newspaper Throwing Logic
        if (pressmanGroup.userData.isPressing || Math.random() < 0.005) { // Random throws even if not pressing
            if (!window._lastPaperThrow || (now - window._lastPaperThrow > 2000)) {
                if (window.spawnPaperboyNews) window.spawnPaperboyNews(pressmanGroup.position);
                window._lastPaperThrow = now;
            }
        }
    }

    // Update flying newspapers
    if (window.pressmanNewspapers && window.pressmanNewspapers.children.length > 0) {
        const papers = window.pressmanNewspapers.children;
        for (let i = papers.length - 1; i >= 0; i--) {
            const p = papers[i];
            if (p.userData.velocity) {
                p.position.add(p.userData.velocity.clone().multiplyScalar(0.016));
                p.rotation.x += p.userData.rotSpeed.x;
                p.rotation.y += p.userData.rotSpeed.y;
                p.rotation.z += p.userData.rotSpeed.z;
            }
            
            // Fade out and remove
            const age = now - p.userData.birth;
            if (age > 4000) {
                p.material.opacity -= 0.05;
                if (p.material.opacity <= 0) {
                    window.pressmanNewspapers.remove(p);
                }
            } else if (age > 3000) {
                p.material.opacity = 1 - (age - 3000) / 1000;
            }
        }
    }
}
function spawnMedicalCube(x, y, z) {
    const group = new THREE.Group();
    group.createdAt = Date.now();
    group.userData.posKey = `${Math.round(x)}_${Math.round(y)}_${Math.round(z)}`;
    const boxMat = new THREE.MeshLambertMaterial({ color: 0x4ade80, transparent: true, opacity: 0.25, emissive: 0x4ade80, wireframe: true });
    const cube = new THREE.Mesh(new THREE.BoxGeometry(70000, 70000, 70000), boxMat);
    group.add(cube);
    const crossMat = new THREE.MeshPhongMaterial({ color: 0xff4444, emissive: 0xff0000 });
    const barLong = new THREE.BoxGeometry(45000, 10000, 10000);
    const hBar = new THREE.Mesh(barLong, crossMat);
    const vBar = new THREE.Mesh(barLong, crossMat);
    vBar.rotation.z = Math.PI / 2;
    const dBar = new THREE.Mesh(barLong, crossMat);
    dBar.rotation.y = Math.PI / 2;
    group.add(hBar, vBar, dBar);
    group.position.set(x, y, z);
    scene.add(group);
    medicalCubes.push(group);
    log("⚕️ REASONER_HEAL: Tombstone Sanitized.", "#4ade80");
}

function syncSnakeTail(count) {
    if (!scene) return;
    const sMat = new THREE.MeshLambertMaterial({ color: 0x10b981 });
    const wagonMat = new THREE.MeshPhongMaterial({ color: 0x34d399, transparent: true, opacity: 0.6 });
    const baseLength = 7;
    const targetLength = baseLength + (count || 0);
    while(snakeSegments.length < targetLength) {
        const i = snakeSegments.length;
        let seg;
        if (i < baseLength) {
            const size = (i <= 3) ? 30000 : 30000 - (i-3)*4500;
            seg = new THREE.Mesh(new THREE.BoxGeometry(size, size, size), sMat);
        } else {
            const size = 15000;
            seg = new THREE.Mesh(new THREE.SphereGeometry(size, 8, 8), wagonMat);
        }
        const last = snakeSegments[snakeSegments.length-1] || snakeGroup;
        seg.position.copy(last.position);
        agentsContainer.add(seg); // [Fix] Add to agentsContainer
        snakeSegments.push(seg);
    }
    while(snakeSegments.length > targetLength) {
        const seg = snakeSegments.pop();
        if (typeof safeDispose === 'function') safeDispose(seg);
        else scene.remove(seg);
    }
}

function spawnSkywalkerLaser() {
    if (!skywalkerGroup || !scene) return;
    const mat = new THREE.LineBasicMaterial({ color: 0xff0000, transparent: true, opacity: 1.0 });
    const start = skywalkerGroup.position.clone();
    
    const end = new THREE.Vector3(
        (Math.random() - 0.5) * 2000000,
        (Math.random() - 0.5) * 2000000,
        (Math.random() - 0.5) * 2000000
    );
    
    const geo = new THREE.BufferGeometry().setFromPoints([start, end]);
    const line = new THREE.Line(geo, mat);
    scene.add(line);
    skywalkerLasers.push(line);
}

function spawnYodaBullet(start, end) {
    if (!scene) return;
    const bulletGroup = new THREE.Group();
    
    // Core del proiettile: Cilindro luminoso (tipo dardo laser)
    const geo = new THREE.CylinderGeometry(2000, 2000, 80000, 8);
    geo.rotateX(Math.PI / 2);
    const mat = new THREE.MeshBasicMaterial({ color: 0xfacc15, transparent: true, opacity: 0.9 });
    const mesh = new THREE.Mesh(geo, mat);
    
    // Alone luminoso (Glow)
    const glowGeo = new THREE.CylinderGeometry(6000, 6000, 90000, 8);
    glowGeo.rotateX(Math.PI / 2);
    const glowMat = new THREE.MeshBasicMaterial({ color: 0xfacc15, transparent: true, opacity: 0.3 });
    const glow = new THREE.Mesh(glowGeo, glowMat);
    
    bulletGroup.add(mesh);
    bulletGroup.add(glow);
    bulletGroup.position.copy(start);
    scene.add(bulletGroup);
    
    yodaBullets.push({
        mesh: bulletGroup,
        start: start,
        end: end,
        progress: 0
    });
}

// 🔴 [v8.0] Skywalker Sovereign Quad-Cannon Laser logic
function triggerSkywalkerLaser(agent, controller) {
    if (!window.scene) return;
    
    // Mappatura dei 4 cannoni (Tubi Grigi dello Skywalker)
    const offsets = [
        {x: 6000, y: 3000, z: 0},   // Superiore Destra
        {x: -6000, y: 3000, z: 0},  // Superiore Sinistra
        {x: 6000, y: -3000, z: 0},  // Inferiore Destra
        {x: -6000, y: -3000, z: 0}  // Inferiore Sinistra
    ];
    
    const targetPos = agent.laserTarget || {x: 2000000, y: 0, z: 2000000}; 
    
    // Sequenza rotativa: 1 colpo totale ogni 125ms per avere 2 colpi/sec su 4 cannoni
    if (controller && controller.drawLaser) {
        // [v8.4] Fuoco SIMULTANEO da tutti e 4 i cannoni
        offsets.forEach((off, idx) => {
            const startPos = {
                x: agent.pos.x + off.x,
                y: agent.pos.y + off.y,
                z: agent.pos.z + off.z
            };
            // Laser con Glow Neon Rosso
            controller.drawLaser('FS-77-cannon-' + idx, startPos, targetPos, "#ff0033", 600);
            
            if (window.triggerSynapticSparks) {
                window.triggerSynapticSparks(startPos, 1);
            }
        });
        
        if (window.triggerSynapticSparks) {
            window.triggerSynapticSparks(targetPos, 8); // Più scintille all'impatto
        }
    }
}
// 🔫 v4.1.4: Skywalker Laser Storm Engine
// Spara proiettili laser neon dai cannoni delle ali verso il target
window.triggerSkywalkerLaserStorm = function(targetPos) {
    if (!window.skywalkerSprite || !window.scene) {
        // Return silently when in 2D pages or views where the 3D scene is not initialized, preventing console flood.
        return;
    }
    
    console.log("🚀 [FS-77] LASER STORM TRIGGERED towards:", targetPos);
    if (window.log) window.log("⚡ [FS-77] LASER STORM: INJECTING KNOWLEDGE...", "#ef4444");

    const colors = [0xff4444, 0xff0000, 0xee2222]; // Red Neon Palette
    const exp = 4000; // Expansion factor matches nebula
    
    for (let i = 0; i < 6; i++) { // Aumentati a 6 per più densità
        const laserGeo = new THREE.BufferGeometry().setFromPoints([
            new THREE.Vector3(0, 0, 0),
            new THREE.Vector3(0, 0, 80) // Più lungo per visibilità
        ]);
        
        const laserMat = new THREE.MeshBasicMaterial({ 
            color: colors[Math.floor(Math.random() * colors.length)],
            transparent: true,
            opacity: 1.0, // Massima luminosità
            side: THREE.DoubleSide
        });
        
        const laser = new THREE.Mesh(laserGeo, laserMat);
        
        // Offset dai cannoni delle ali
        const sideOffset = (i < 3 ? -35 : 35);
        const verticalOffset = (i % 3 === 0 ? 15 : (i % 3 === 1 ? 0 : -15));
        
        laser.position.copy(window.skywalkerSprite.position);
        
        const right = new THREE.Vector3(1, 0, 0).applyQuaternion(window.skywalkerSprite.quaternion);
        const up = new THREE.Vector3(0, 1, 0).applyQuaternion(window.skywalkerSprite.quaternion);
        
        laser.position.add(right.multiplyScalar(sideOffset));
        laser.position.add(up.multiplyScalar(verticalOffset));
        
        const finalTarget = new THREE.Vector3(
            targetPos.x * exp + (Math.random() - 0.5) * 150,
            targetPos.y * exp + (Math.random() - 0.5) * 150,
            targetPos.z * exp + (Math.random() - 0.5) * 150
        );
        
        laser.lookAt(finalTarget);
        window.scene.add(laser);
        
        const startTime = Date.now();
        const duration = 500 + Math.random() * 300; // Volo più rapido e aggressivo
        const startPos = laser.position.clone();
        
        function animateLaser() {
            const elapsed = Date.now() - startTime;
            const progress = elapsed / duration;
            
            if (progress < 1) {
                laser.position.lerpVectors(startPos, finalTarget, progress);
                laser.scale.z = 1 + progress * 5;
                requestAnimationFrame(animateLaser);
            } else {
                window.scene.remove(laser);
                laserGeo.dispose();
                laserMat.dispose();
            }
        }
        animateLaser();
    }
    
    // Feedback nel log solo la prima volta per scarica
    if (Math.random() > 0.95 && window.log) {
        window.log("⚡ [FS-77] Injecting Wisdom via Laser Storm.", "#ef4444");
    }
};
