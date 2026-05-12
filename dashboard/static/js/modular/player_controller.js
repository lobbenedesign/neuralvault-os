/**
 * 🕹️ Star Wars: Neural Combat Engine - FS-77 X-Wing Edition
 * Player Controller Manuale (WASD)
 * Design ispirato al T-65B X-Wing Starfighter.
 */

class PlayerController {
    constructor(scene, camera, controls) {
        this.scene = scene;
        this.camera = camera;
        this.controls = controls;
        this.active = false;
        this.viewMode = 0; // 0: 3rd, 1: 1st
        this.keys = { w: false, a: false, s: false, d: false, p: false };
        
        // Ship state
        this.position = new THREE.Vector3(0, 1000000, 150000); 
        this.velocity = new THREE.Vector3(0, 0, 0);
        this.rotation = new THREE.Euler(0, 0, 0, 'YXZ');
        
        // Configs
        this.speed = 2500; 
        this.hyperSpeedMultiplier = 6; 
        this.turnSpeed = 0.03;
        this.friction = 0.96;

        this.thrusters = []; 

        this.initInput();
        this.initShipMesh();
        
        console.log("🚀 PlayerController Ready. Press 'F' to pilot.");
    }

    initInput() {
        this.lastPPress = 0;
        this.doubleBoostActive = false;

        const handleKey = (e, isDown) => {
            if (!this.active) return;
            const key = e.key.toLowerCase();
            
            if (isDown && e.key === 'Escape') {
                if (typeof log === 'function') log(`🛑 PILOT MODE DISENGAGED (ESC)`, "#ef4444");
                this.setPilotMode(false);
                return;
            }
            
            if (isDown) {
                if (['w', 'a', 's', 'd'].includes(key) && !this.keys[key]) {
                    if (typeof log === 'function') log(`🕹️ MANEUVER: [${key.toUpperCase()}]`, "#0ea5e9");
                }
                if (key === 'p' && !this.keys.p) {
                    const now = Date.now();
                    if (now - this.lastPPress < 400) {
                        this.doubleBoostActive = true;
                        if (typeof log === 'function') log(`⚡ QUANTUM-DRIVE (3x BOOST) ENGAGED!`, "#a855f7");
                    } else {
                        this.doubleBoostActive = false;
                        if (typeof log === 'function') log(`🔥 HYPER-DRIVE ENGAGED!`, "#f59e0b");
                    }
                    this.lastPPress = now;
                }
                if (key === '1') {
                    this.viewMode = 1;
                    if (typeof log === 'function') log(`📷 VIEW: COCKPIT MODE (FULLSCREEN)`, "#10b981");
                    
                    const col = document.getElementById('overview-view');
                    if (col && document.fullscreenElement !== col) {
                        col.requestFullscreen().catch(e => console.warn(e));
                    }
                    
                    let overlay = document.getElementById('arcade-cockpit-overlay');
                    if (!overlay) {
                        overlay = document.createElement('img');
                        overlay.id = 'arcade-cockpit-overlay';
                        overlay.src = '/static/img/cockpit.png';
                        overlay.style.position = 'absolute';
                        overlay.style.top = '0';
                        overlay.style.left = '0';
                        overlay.style.width = '100%';
                        overlay.style.height = '100%';
                        overlay.style.objectFit = 'fill';
                        overlay.style.pointerEvents = 'none';
                        overlay.style.zIndex = '9000';
                        const container = document.getElementById('memory-graph-container');
                        if (container) container.appendChild(overlay);
                    }
                    if (overlay) overlay.style.display = 'block';
                }
                if (key === '2') {
                    this.viewMode = 0;
                    if (typeof log === 'function') log(`📷 VIEW: 3RD PERSON`, "#10b981");
                    
                    const overlay = document.getElementById('arcade-cockpit-overlay');
                    if (overlay) overlay.style.display = 'none';
                    
                    if (document.fullscreenElement) {
                        document.exitFullscreen().catch(e => console.warn(e));
                    }
                }
            }
            
            if (this.keys.hasOwnProperty(key)) {
                this.keys[key] = isDown;
            }
        };

        // Usa la 'Capture Phase' (true) per scavalcare ogni altro componente che potrebbe fermare l'evento
        window.addEventListener('keydown', (e) => handleKey(e, true), true);
        window.addEventListener('keyup', (e) => handleKey(e, false), true);
    }

    showFlightModal() {
        // Rimuovi eventuali modali precedenti
        const existing = document.getElementById('flight-modal-nv');
        if (existing) existing.remove();

        const modal = document.createElement('div');
        modal.id = 'flight-modal-nv';
        modal.style.cssText = `
            position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%);
            background: rgba(2, 6, 23, 0.9); backdrop-filter: blur(20px);
            border: 2px solid #ef4444; border-radius: 24px; padding: 2.5rem 5rem;
            z-index: 9999999; text-align: center; color: white;
            box-shadow: 0 0 60px rgba(239, 68, 68, 0.5), inset 0 0 20px rgba(239, 68, 68, 0.2);
            font-family: 'Inter', sans-serif; animation: modalPulse 4s infinite alternate;
        `;
        
        modal.innerHTML = `
            <div style="font-size: 0.7rem; color: #ef4444; font-weight: 900; letter-spacing: 5px; margin-bottom: 1.5rem; text-transform: uppercase;">Uplink Established</div>
            <div style="font-size: 2.2rem; font-weight: 900; margin-bottom: 0.8rem; background: linear-gradient(to bottom, #fff, #94a3b8); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">MANUAL PILOT ENGAGED</div>
            <div style="font-size: 0.9rem; color: #4ade80; font-weight: 600;">Skywalker FS-77 is under your control.</div>
            <div style="margin-top: 1.5rem; display: flex; gap: 1rem; justify-content: center;">
                <div style="font-size: 0.6rem; background: rgba(255,255,255,0.1); padding: 5px 10px; border-radius: 5px;">WASD: Maneuver</div>
                <div style="font-size: 0.6rem; background: rgba(255,255,255,0.1); padding: 5px 10px; border-radius: 5px;">P: Afterburners</div>
            </div>
        `;
        
        const style = document.createElement('style');
        style.innerHTML = `
            @keyframes modalPulse { 
                0% { transform: translate(-50%, -50%) scale(1); opacity: 1; }
                100% { transform: translate(-50%, -50%) scale(1.02); opacity: 0.95; }
            }
        `;
        document.head.appendChild(style);
        document.body.appendChild(modal);
        
        setTimeout(() => {
            modal.style.transition = 'all 1s cubic-bezier(0.19, 1, 0.22, 1)';
            modal.style.opacity = '0';
            modal.style.transform = 'translate(-50%, -40%) scale(0.9)';
            setTimeout(() => { modal.remove(); style.remove(); }, 1000);
        }, 4000);
    }

    setPilotMode(state) {
        if (this.active === state) return;
        this.active = state;
        
        const toggle = document.getElementById('flight-toggle');
        if (toggle) {
            toggle.checked = this.active;
            toggle.blur();
        }
        window.focus();
        
        if (this.controls) {
            this.controls.enabled = !this.active;
        }
        
        window.isFlightModeActive = this.active;
        fetch('/api/flight-mode', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'X-API-KEY': typeof VAULT_KEY !== 'undefined' ? VAULT_KEY : '' },
            body: JSON.stringify({ active: this.active })
        }).catch(e => console.warn("Flight mode telemetry error:", e));
        
        if (this.shipMesh) {
            this.shipMesh.visible = this.active;
        }
        
        if (this.active) {
            // Initial positioning for the new ship
            if (!this.initialized) {
                this.position.set(0, 500000, 2000000); 
                this.initialized = true;
            }
            this.shipMesh.position.copy(this.position);
            
            // Snap camera
            const relativeCameraOffset = new THREE.Vector3(0, 2000, 9000); 
            const cameraOffset = relativeCameraOffset.applyMatrix4(this.shipMesh.matrixWorld);
            this.camera.position.copy(cameraOffset);
            this.camera.lookAt(this.shipMesh.position);

            this.showFlightModal();
            if (typeof log === 'function') log("🚀 NEURAL_NAVIGATOR ACTIVE: Manual Pilot Engaged.", "#0ea5e9");
        } else {
            if (typeof log === 'function') log("🛑 PILOT MODE DISENGAGED.", "#3b82f6");
            this.viewMode = 0; 
            const overlay = document.getElementById('arcade-cockpit-overlay');
            if (overlay) overlay.style.display = 'none';
            if (document.fullscreenElement) {
                document.exitFullscreen().catch(e => console.warn(e));
            }
        }
    }

    toggleActive() {
        this.setPilotMode(!this.active);
    }

    initShipMesh() {
        const group = new THREE.Group();
        
        // Materiali Starship White-Grey-Azure
        const bodyMat = new THREE.MeshStandardMaterial({ color: 0xffffff, metalness: 0.3, roughness: 0.4 }); // Pure White
        const greyMat = new THREE.MeshStandardMaterial({ color: 0x64748b, metalness: 0.6, roughness: 0.3 }); // Technical Grey
        const azureMat = new THREE.MeshStandardMaterial({ color: 0x0ea5e9, emissive: 0x0369a1, emissiveIntensity: 0.5 }); // Azure Accents
        const cockpitMat = new THREE.MeshPhongMaterial({ color: 0x0ea5e9, transparent: true, opacity: 0.4, shininess: 120 });
        const engineMat = new THREE.MeshStandardMaterial({ color: 0x1e293b, metalness: 0.8, roughness: 0.2 });
        const glowMat = new THREE.MeshBasicMaterial({ color: 0x38bdf8, transparent: true, opacity: 0.9 });

        // 1. Fusoliera Centrale
        const nose = new THREE.Mesh(new THREE.CylinderGeometry(50, 400, 3000, 8), bodyMat);
        nose.rotateX(Math.PI / 2); nose.position.z = 1500;
        group.add(nose);

        const mainBody = new THREE.Mesh(new THREE.BoxGeometry(700, 600, 2500), bodyMat);
        mainBody.position.z = -1250;
        group.add(mainBody);

        const details = new THREE.Mesh(new THREE.BoxGeometry(720, 100, 1500), azureMat);
        details.position.set(0, 300, -1250);
        group.add(details);

        const cockpit = new THREE.Mesh(new THREE.SphereGeometry(300, 16, 16), cockpitMat);
        cockpit.scale.set(1, 0.7, 2); cockpit.position.set(0, 300, 500);
        this.cockpitGlass = cockpit;
        group.add(cockpit);

        this.cockpitInternal = new THREE.Group();
        const frameMat = new THREE.MeshBasicMaterial({ color: 0x3b82f6, wireframe: true, transparent: true, opacity: 0.8 });
        const dashMat = new THREE.MeshBasicMaterial({ color: 0x1e293b, transparent: true, opacity: 0.9 });
        
        const dash = new THREE.Mesh(new THREE.BoxGeometry(600, 300, 200), dashMat);
        dash.position.set(0, 250, 750);
        this.cockpitInternal.add(dash);
        
        for(let side of [-1, 1]) {
            const pillar = new THREE.Mesh(new THREE.BoxGeometry(40, 600, 40), frameMat);
            pillar.position.set(side * 250, 550, 600);
            pillar.rotation.z = side * 0.4;
            this.cockpitInternal.add(pillar);
        }
        const topFrame = new THREE.Mesh(new THREE.BoxGeometry(600, 40, 40), frameMat);
        topFrame.position.set(0, 750, 550);
        this.cockpitInternal.add(topFrame);
        
        this.cockpitInternal.visible = false;
        group.add(this.cockpitInternal);

        const wingWidth = 4500; const wingDepth = 1800;
        const thrusterMat = new THREE.MeshBasicMaterial({ 
            color: 0xffffff, transparent: true, opacity: 0.8, blending: THREE.AdditiveBlending
        });

        for(let i=0; i<4; i++) {
            const wingGroup = new THREE.Group();
            const wing = new THREE.Mesh(new THREE.BoxGeometry(wingWidth, 100, wingDepth), bodyMat);
            wing.position.x = wingWidth / 2; wingGroup.add(wing);
            const stripe = new THREE.Mesh(new THREE.BoxGeometry(600, 120, wingDepth + 20), azureMat);
            stripe.position.x = wingWidth * 0.6; wingGroup.add(stripe);
            
            const engine = new THREE.Mesh(new THREE.CylinderGeometry(250, 300, 1500, 12), engineMat);
            engine.rotateX(Math.PI / 2); engine.position.set(300, 0, -wingDepth/2);
            wingGroup.add(engine);
            
            const glow = new THREE.Mesh(new THREE.CircleGeometry(220, 16), glowMat);
            glow.position.set(300, 0, -wingDepth/2 - 751); glow.rotateY(Math.PI);
            wingGroup.add(glow);

            const thrusterGeo = new THREE.ConeGeometry(200, 1, 12);
            thrusterGeo.translate(0, 0.5, 0); 
            const thruster = new THREE.Mesh(thrusterGeo, thrusterMat);
            thruster.rotateX(-Math.PI / 2);
            thruster.position.set(300, 0, -wingDepth/2 - 750);
            thruster.visible = false;
            wingGroup.add(thruster);
            this.thrusters.push(thruster);

            const cannon = new THREE.Mesh(new THREE.CylinderGeometry(50, 50, 3000), greyMat);
            cannon.rotateX(Math.PI / 2); cannon.position.set(wingWidth - 200, 0, 500);
            wingGroup.add(cannon);
            const tip = new THREE.Mesh(new THREE.CylinderGeometry(20, 20, 400), azureMat);
            tip.rotateX(Math.PI / 2); tip.position.set(wingWidth - 200, 0, 2100);
            wingGroup.add(tip);
            
            wingGroup.rotation.z = (Math.PI / 4) + (i * Math.PI / 2);
            group.add(wingGroup);
        }

        const r2 = new THREE.Mesh(new THREE.CylinderGeometry(100, 100, 200), new THREE.MeshStandardMaterial({color: 0xffffff}));
        r2.position.set(0, 350, -300); group.add(r2);
        const r2Head = new THREE.Mesh(new THREE.SphereGeometry(100, 8, 8), new THREE.MeshStandardMaterial({color: 0x3b82f6}));
        r2Head.position.set(0, 450, -300); group.add(r2Head);

        const container = new THREE.Group();
        group.rotation.y = Math.PI;
        container.add(group);

        this.shipMesh = container;
        this.shipMesh.position.copy(this.position);
        this.shipMesh.visible = this.active;
        this.scene.add(this.shipMesh);
    }

    update(delta) {
        if(!this.active || !this.shipMesh) return;

        if (this.keys.w) this.rotation.x -= this.turnSpeed;
        if (this.keys.s) this.rotation.x += this.turnSpeed;
        if (this.keys.a) this.rotation.y += this.turnSpeed;
        if (this.keys.d) this.rotation.y -= this.turnSpeed;
        
        this.rotation.z *= 0.95; 
        this.shipMesh.setRotationFromEuler(this.rotation);

        const forward = new THREE.Vector3(0, 0, -1);
        forward.applyEuler(this.rotation);

        let accel = this.speed;
        const isBoosting = this.keys.p;
        if (isBoosting) {
            accel *= this.hyperSpeedMultiplier;
            if (this.doubleBoostActive) {
                accel *= 3; // Quantum 3x Boost
                if (this.camera) this.camera.fov = THREE.MathUtils.lerp(this.camera.fov, 120, 0.1);
            } else {
                if (this.camera) this.camera.fov = THREE.MathUtils.lerp(this.camera.fov, 100, 0.1);
            }
        } else {
            this.doubleBoostActive = false;
            if (this.camera) this.camera.fov = THREE.MathUtils.lerp(this.camera.fov, 75, 0.1);
        }
        if (this.camera) this.camera.updateProjectionMatrix();

        this.thrusters.forEach(t => {
            if (isBoosting) {
                t.visible = true;
                if (this.doubleBoostActive) {
                    t.scale.y = 4000 + Math.random() * 1000; 
                    // Red-Orange fire for Quantum Boost
                    t.material.color.setHSL(0.05 + Math.random() * 0.05, 1.0, 0.5); 
                } else {
                    t.scale.y = 2000 + Math.random() * 500; 
                    // Blue flame for normal Hyper-Drive
                    t.material.color.setHSL(0.55, 1.0, 0.5 + Math.random() * 0.5); 
                }
            } else {
                t.visible = true;
                t.scale.y = 100 + Math.random() * 50;
                // Idle blue engine glow
                t.material.color.setHSL(0.55, 1.0, 0.8);
            }
        });

        // Always apply base forward thrust, WASD is for steering
        this.velocity.add(forward.clone().multiplyScalar(accel * delta));

        this.velocity.multiplyScalar(this.friction);
        this.position.add(this.velocity);
        this.shipMesh.position.copy(this.position);

        if (this.viewMode === 0) {
            // [v8.4] Aumentata la distanza della telecamera (200% più lontana) come richiesto
            const relativeCameraOffset = new THREE.Vector3(0, 1800, 10500); 
            const cameraOffset = relativeCameraOffset.applyMatrix4(this.shipMesh.matrixWorld);
            this.camera.position.copy(cameraOffset);
            this.camera.lookAt(this.shipMesh.position);
            
            this.shipMesh.visible = true; // Ripristina la nave
            if (this.cockpitGlass) this.cockpitGlass.visible = true;
            if (this.cockpitInternal) this.cockpitInternal.visible = false;
        } else {
            // [v8.5] Arcade Cockpit PNG Overlay - Telecamera al centro esatto
            const cockpitOffset = new THREE.Vector3(0, 0, 0); 
            const cameraPos = cockpitOffset.applyMatrix4(this.shipMesh.matrixWorld);
            this.camera.position.copy(cameraPos);
            this.camera.quaternion.copy(this.shipMesh.quaternion);
            
            // Nasconde completamente la mesh 3D della nave
            this.shipMesh.visible = false;
        }
    }
}
