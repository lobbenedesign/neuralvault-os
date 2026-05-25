/**
 * 🕹️ Star Wars: Neural Combat Engine - FS-77 X-Wing Edition
 * Player Controller Manuale (WASD)
 */

class SoundEngine {
    constructor() {
        this.ctx = null;
    }
    init() {
        if (!this.ctx) this.ctx = new (window.AudioContext || window.webkitAudioContext)();
    }
    playLaser() {
        this.init();
        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();
        osc.type = 'square';
        osc.frequency.setValueAtTime(800, this.ctx.currentTime);
        osc.frequency.exponentialRampToValueAtTime(100, this.ctx.currentTime + 0.1);
        gain.gain.setValueAtTime(0.1, this.ctx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.01, this.ctx.currentTime + 0.1);
        osc.connect(gain); gain.connect(this.ctx.destination);
        osc.start(); osc.stop(this.ctx.currentTime + 0.1);
    }
    playExplosion() {
        this.init();
        const bufferSize = this.ctx.sampleRate * 0.3;
        const buffer = this.ctx.createBuffer(1, bufferSize, this.ctx.sampleRate);
        const data = buffer.getChannelData(0);
        for (let i = 0; i < bufferSize; i++) data[i] = Math.random() * 2 - 1;
        const noise = this.ctx.createBufferSource();
        noise.buffer = buffer;
        const filter = this.ctx.createBiquadFilter();
        filter.type = 'lowpass';
        filter.frequency.setValueAtTime(400, this.ctx.currentTime);
        filter.frequency.exponentialRampToValueAtTime(10, this.ctx.currentTime + 0.3);
        const gain = this.ctx.createGain();
        gain.gain.setValueAtTime(0.3, this.ctx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.01, this.ctx.currentTime + 0.3);
        noise.connect(filter); filter.connect(gain); gain.connect(this.ctx.destination);
        noise.start();
    }
    playEngine(speed) {
        this.init();
        if (!this.engineOsc) {
            this.engineOsc = this.ctx.createOscillator();
            this.engineGain = this.ctx.createGain();
            this.engineOsc.type = 'sawtooth';
            this.engineOsc.frequency.setValueAtTime(40, this.ctx.currentTime);
            this.engineGain.gain.setValueAtTime(0, this.ctx.currentTime);
            this.engineOsc.connect(this.engineGain);
            this.engineGain.connect(this.ctx.destination);
            this.engineOsc.start();
        }
        const freq = 40 + (speed * 0.02);
        this.engineOsc.frequency.setTargetAtTime(freq, this.ctx.currentTime, 0.1);
        this.engineGain.gain.setTargetAtTime(0.03, this.ctx.currentTime, 0.1);
    }
    playBoost() {
        this.init();
        const osc = this.ctx.createOscillator();
        osc.type = 'sawtooth';
        osc.frequency.setValueAtTime(100, this.ctx.currentTime);
        osc.frequency.exponentialRampToValueAtTime(1000, this.ctx.currentTime + 0.5);
        const gain = this.ctx.createGain();
        gain.gain.setValueAtTime(0.1, this.ctx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.01, this.ctx.currentTime + 0.5);
        osc.connect(gain); gain.connect(this.ctx.destination);
        osc.start(); osc.stop(this.ctx.currentTime + 0.5);
    }
    stopAll() {
        if (this.engineOsc) {
            try {
                this.engineGain.gain.setTargetAtTime(0, this.ctx.currentTime, 0.1);
                setTimeout(() => {
                    if (this.engineOsc) {
                        this.engineOsc.stop();
                        this.engineOsc = null;
                    }
                }, 200);
            } catch (e) {}
        }
    }

    playShield() {
        this.init();
        const now = this.ctx.currentTime;
        
        // 🛡️ [Premium Shield Startup]
        const osc1 = this.ctx.createOscillator();
        const osc2 = this.ctx.createOscillator();
        const gain = this.ctx.createGain();
        const filter = this.ctx.createBiquadFilter();

        osc1.type = 'sawtooth';
        osc1.frequency.setValueAtTime(60, now);
        osc1.frequency.exponentialRampToValueAtTime(800, now + 0.4);

        osc2.type = 'sine';
        osc2.frequency.setValueAtTime(120, now);
        osc2.frequency.exponentialRampToValueAtTime(1600, now + 0.2);

        filter.type = 'lowpass';
        filter.frequency.setValueAtTime(100, now);
        filter.frequency.exponentialRampToValueAtTime(4000, now + 0.3);
        filter.Q.setValueAtTime(10, now);

        gain.gain.setValueAtTime(0, now);
        gain.gain.linearRampToValueAtTime(0.15, now + 0.05);
        gain.gain.exponentialRampToValueAtTime(0.01, now + 0.6);

        osc1.connect(filter);
        osc2.connect(filter);
        filter.connect(gain);
        gain.connect(this.ctx.destination);

        osc1.start(now);
        osc2.start(now);
        osc1.stop(now + 0.6);
        osc2.stop(now + 0.6);
    }
}

class PlayerController {
    constructor(scene, camera, controls) {
        this.scene = scene;
        this.camera = camera;
        this.controls = controls;
        this.active = false;
        this.viewMode = 0; // 0: 3rd, 1: 1st
        this.keys = { w: false, a: false, s: false, d: false, p: false, space: false, o: false };
        
        // Ship state
        this.position = new THREE.Vector3(0, 1000000, 150000); 
        this.velocity = new THREE.Vector3(0, 0, 0);
        this.rotation = new THREE.Euler(0, 0, 0, 'YXZ');
        
        // Configs
        this.speed = 2500; 
        this.hyperSpeedMultiplier = 6; 
        this.turnSpeed = 0.03;
        this.friction = 0.96;

        // Combat System
        this.combatMode = false;
        this.health = 100;
        this.score = 0;
        this.ultraBlasterAmmo = 0;
        this.lasers = [];
        this.enemies = [];
        this.bosses = [];
        this.powerups = [];
        this.lastShotTime = 0;
        this.enemiesKilled = 0;
        this.nextBossThreshold = 10;
        
        // 🛡️ [v13.5] Defense & Heavy Weapons State
        this.shieldCharges = 3;
        this.shieldActive = false;
        this.heavyBlasterAmmo = 0;
        this.shieldMesh = null;

        this.originalBackground = null;
        this.skyTexture = null;
        
        this.thrusters = []; 
        this.lastDelta = 0.016;

        this.sfx = new SoundEngine();
        
        this.initInput();
        this.initShipMesh();
        
        // 🚀 [v13.0] Ultra-Fast Immersion: Background Preloading
        this.preloadAssets();
        
        console.log("🚀 PlayerController Ready. Press 'F' to pilot.");
    }

    preloadAssets() {
        // 1. Preload Sky Background (GPU memory) - [v13.1] 8K Ultra-High Definition
        const loader = new THREE.TextureLoader();
        this.skyTexture = loader.load('/static/img/space_bg_8k.png', (tex) => {
            tex.mapping = THREE.EquirectangularReflectionMapping;
            tex.encoding = THREE.sRGBEncoding;
        });

        // 2. Preload Cockpit PNG (Browser Cache)
        const cockpitImg = new Image();
        cockpitImg.src = '/static/img/cockpit.png';
        
        if (typeof log === 'function') log("💾 SYSTEM: Preloading Pilot Assets...", "#3b82f6");
    }

    initInput() {
        this.lastPPress = 0;
        this.doubleBoostActive = false;

        const handleKey = (e, isDown) => {
            if (!this.active) return;
            const key = e.key.toLowerCase();
            
            if (isDown && e.key === 'Escape') {
                this.setPilotMode(false);
                return;
            }
            
            if (isDown) {
                if (key === 'p' && !this.keys.p) {
                    const now = Date.now();
                    this.doubleBoostActive = (now - this.lastPPress < 400);
                    this.lastPPress = now;
                }
                if (key === '1') this.viewMode = 1;
                if (key === '2') this.viewMode = 0;
                if (key === ' ' && this.combatMode && !this.keys.space) {
                    e.preventDefault();
                    this.toggleShield(true);
                }
                if (key === 'o' && this.combatMode && !this.keys.o) {
                    this.fireHeavyBlaster();
                }
                if (this.combatMode && (key === 'è' || key === 'e')) {
                    this.fireLaser();
                }
            } else {
                if (key === ' ') this.toggleShield(false);
            }
            
            if (this.keys.hasOwnProperty(key)) {
                this.keys[key] = isDown;
            } else if (key === ' ') {
                this.keys.space = isDown;
            }
        };

        window.addEventListener('keydown', (e) => handleKey(e, true), true);
        window.addEventListener('keyup', (e) => handleKey(e, false), true);
    }

    toggleShield(active) {
        if (!this.combatMode) return;
        if (active && this.shieldCharges > 0) {
            if (!this.shieldActive) {
                if (this.sfx) this.sfx.playShield();
            }
            this.shieldActive = true;
            if (typeof log === 'function') log(`🛡️ SHIELD ACTIVE (${this.shieldCharges} CHARGES LEFT)`, "#38bdf8");
        } else {
            this.shieldActive = false;
        }
    }

    fireHeavyBlaster() {
        if (!this.combatMode || this.heavyBlasterAmmo <= 0) return;
        this.heavyBlasterAmmo--;
        this.fireLaser(true); // Fire ultra laser as heavy blaster
        if (typeof log === 'function') log(`🔥 HEAVY BLASTER FIRED! (${this.heavyBlasterAmmo} LEFT)`, "#f43f5e");
        this.updateCombatHUD();
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
        
        if (this.active) {
            // 🌌 [v12.8] Immersive 360 Background Sync (Preloaded)
            if (!this.originalBackground) {
                this.originalBackground = this.scene.background;
            }
            if (this.skyTexture) {
                this.scene.background = this.skyTexture;
                this.scene.environment = this.skyTexture;
            }

            // 🎯 [v12.5] Initialize position at Skywalker (FS-77) location for a coordinated start
            if (typeof skywalkerGroup !== 'undefined' && skywalkerGroup) {
                const worldPos = new THREE.Vector3();
                skywalkerGroup.getWorldPosition(worldPos);
                this.position.copy(worldPos);
                
                // Copy initial rotation for camera alignment
                this.rotation.setFromQuaternion(skywalkerGroup.quaternion, 'YXZ');
                
                // NOTE: skywalkerGroup remains visible and active as requested!
                if (typeof log === 'function') log("🚀 PILOT MODE ENGAGED - COORDINATING WITH FS-77...", "#10b981");
            }

            if (this.shipMesh) {
                this.shipMesh.position.copy(this.position);
                this.shipMesh.visible = true;
                this.shipMesh.updateMatrixWorld();
                
                // Snap camera immediately
                const relativeCameraOffset = new THREE.Vector3(0, 2000, 9000); 
                const cameraOffset = relativeCameraOffset.applyMatrix4(this.shipMesh.matrixWorld);
                this.camera.position.copy(cameraOffset);
                
                const worldPos = new THREE.Vector3();
                this.shipMesh.getWorldPosition(worldPos);
                this.camera.lookAt(worldPos);
            }

            this.showFlightModal();
            if (typeof log === 'function') log("🚀 NEURAL_NAVIGATOR ACTIVE: Manual Pilot Engaged.", "#0ea5e9");
        } else {
            // 🌌 Restore Original Background
            if (this.originalBackground) {
                this.scene.background = this.originalBackground;
            }

            if (this.shipMesh) {
                this.shipMesh.visible = false;
            }

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

    setCombatMode(state) {
        this.combatMode = state;
        
        if (state) {
            // Force pilot mode on
            if (!this.active) this.setPilotMode(true);
            
            this.health = 100;
            this.score = 0;
            this.enemiesKilled = 0;
            this.nextBossThreshold = 10;
            this.ultraBlasterAmmo = 0;
            this.createCombatHUD();
            document.documentElement.classList.add('combat-mode-active');
            if (typeof log === 'function') log("⚔️ COMBAT MODE ENGAGED. PREPARE TO FIGHT.", "#ef4444");
        } else {
            this.removeCombatHUD();
            this.cleanupCombat();
            document.documentElement.classList.remove('combat-mode-active');
            if (typeof log === 'function') log("🛡️ COMBAT MODE DISENGAGED.", "#3b82f6");
        }
    }

    fireLaser() {
        const now = Date.now();
        if (now - this.lastShotTime < 200) return; // Fire rate limit
        this.lastShotTime = now;

        const isUltra = this.ultraBlasterAmmo > 0;
        if (isUltra) {
            this.ultraBlasterAmmo--;
            this.updateCombatHUD();
        }

        this.sfx.playLaser();

        // Neon Glow Laser Construction
        const createNeonLaser = (isUltra) => {
            const group = new THREE.Group();
            const color = isUltra ? 0xa855f7 : 0x10b981;
            
            // 🏹 [v14.0] Massive Laser Dimensions for Deep Space Visibility
            const coreGeo = new THREE.CylinderGeometry(1500, 1500, isUltra ? 150000 : 100000, 8);
            coreGeo.rotateX(Math.PI / 2);
            const core = new THREE.Mesh(coreGeo, new THREE.MeshBasicMaterial({ color: 0xffffff }));
            
            // Glow Shell (Broader)
            const glowGeo = new THREE.CylinderGeometry(4000, 4000, isUltra ? 155000 : 105000, 8);
            glowGeo.rotateX(Math.PI / 2);
            const glow = new THREE.Mesh(glowGeo, new THREE.MeshBasicMaterial({ 
                color: color, transparent: true, opacity: 0.4 
            }));
            
            group.add(core, glow);
            return group;
        };
        
        const offsets = [new THREE.Vector3(1500, 0, 500), new THREE.Vector3(-1500, 0, 500)];
        
        offsets.forEach(offset => {
            const laser = createNeonLaser(isUltra);
            laser.position.copy(this.shipMesh.position);
            const worldOffset = offset.clone().applyEuler(this.rotation);
            laser.position.add(worldOffset);
            laser.quaternion.copy(this.shipMesh.quaternion);
            
            // 🛡️ [v14.0] Enhanced Laser Visibility & Rendering
            laser.frustumCulled = false;
            laser.traverse(child => { if(child.isMesh) child.frustumCulled = false; });
            
            const forward = new THREE.Vector3(0, 0, -1).applyEuler(this.rotation);
            // 🚀 [v13.9] Projectile Vector Refactoring (Precision Sync)
            const laserSpeed = isUltra ? 25000000 : 12000000;
            // Use the real-time delta to perfectly synchronize the inherited velocity
            const shipVelocityInUnitsPerSec = this.velocity.clone().divideScalar(this.lastDelta || 0.016);
            const velocity = forward.clone().multiplyScalar(laserSpeed).add(shipVelocityInUnitsPerSec);
            
            this.scene.add(laser);
            this.lasers.push({ mesh: laser, velocity: velocity, life: 100, isUltra: isUltra });
        });
    }

    cleanupCombat() {
        this.lasers.forEach(l => this.scene.remove(l.mesh));
        if (this.enemyLasers) this.enemyLasers.forEach(l => this.scene.remove(l.mesh));
        this.enemies.forEach(e => this.scene.remove(e.mesh));
        this.bosses.forEach(b => {
            this.scene.remove(b.mesh);
            if (b.healthBar) this.scene.remove(b.healthBar);
        });
        this.powerups.forEach(p => this.scene.remove(p.mesh));
        if (this.explosions) this.explosions.forEach(exp => exp.particles.forEach(p => this.scene.remove(p.mesh)));
        
        this.lasers = [];
        this.enemyLasers = [];
        this.enemies = [];
        this.bosses = [];
        this.powerups = [];
        this.explosions = [];
        
        // 🔇 [Fix] Total audio silence on exit
        if (this.sfx) this.sfx.stopAll();
    }

    gameOver() {
        this.setCombatMode(false);
        this.setPilotMode(true); // Return to normal pilot

        const modal = document.createElement('div');
        modal.style.cssText = `
            position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%);
            background: rgba(20, 0, 0, 0.95); border: 2px solid #ef4444; border-radius: 20px;
            padding: 40px; z-index: 10000; text-align: center; color: white;
            box-shadow: 0 0 50px rgba(239, 68, 68, 0.8); font-family: 'JetBrains Mono', monospace;
        `;

        modal.innerHTML = `
            <h1 style="color: #ef4444; font-size: 3rem; margin-bottom: 10px; text-shadow: 0 0 10px #ef4444;">GAME OVER</h1>
            <p style="font-size: 1.5rem; color: #38bdf8;">FINAL SCORE: ${this.score}</p>
            <div style="margin: 20px 0;">
                <label style="display:block; margin-bottom:10px; color:#94a3b8;">ENTER RECORD (4 LETTERS):</label>
                <input type="text" id="hs-name" maxlength="4" style="background:rgba(0,0,0,0.5); border:1px solid #ef4444; color:#fff; font-size:2rem; width:120px; text-align:center; text-transform:uppercase;">
            </div>
            <p style="margin-top: 30px; font-size: 1.2rem;">PLAY AGAIN?</p>
            <div style="display: flex; gap: 20px; justify-content: center; margin-top: 10px;">
                <button id="btn-hs-yes" style="background: #10b981; color: #fff; border: none; padding: 10px 30px; font-size: 1.2rem; cursor: pointer; border-radius: 5px;">YES</button>
                <button id="btn-hs-no" style="background: #ef4444; color: #fff; border: none; padding: 10px 30px; font-size: 1.2rem; cursor: pointer; border-radius: 5px;">NO</button>
            </div>
        `;

        document.body.appendChild(modal);

        const saveScore = () => {
            const name = document.getElementById('hs-name').value.toUpperCase() || 'ANON';
            const newScore = { name, score: this.score, date: new Date().toLocaleDateString() };
            
            // 🏆 [v13.1] Persistent Leaderboard Logic
            let scores = JSON.parse(localStorage.getItem('nv_highscores') || '[]');
            scores.push(newScore);
            scores.sort((a, b) => b.score - a.score);
            scores = scores.slice(0, 10); // Top 10
            localStorage.setItem('nv_highscores', JSON.stringify(scores));

            if (typeof log === 'function') log(`🏆 HIGH SCORE SAVED: ${name} - ${this.score}`, "#f59e0b");
            this.showLeaderboard(scores);
        };

        document.getElementById('btn-hs-yes').onclick = () => {
            saveScore();
            modal.remove();
            // Leaderboard will show, play again button inside it
        };
        
        document.getElementById('btn-hs-no').onclick = () => {
            saveScore();
            modal.remove();
            const toggle = document.getElementById('combat-toggle');
            if(toggle) toggle.checked = false;
        };
    }

    showLeaderboard(scores) {
        const modal = document.createElement('div');
        modal.id = 'leaderboard-modal';
        modal.style.cssText = `
            position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%);
            background: rgba(2, 6, 23, 0.95); border: 2px solid #38bdf8; border-radius: 20px;
            padding: 40px; z-index: 10001; text-align: center; color: white; min-width: 400px;
            box-shadow: 0 0 50px rgba(56, 189, 248, 0.5); font-family: 'JetBrains Mono', monospace;
        `;

        let listHTML = '<h2 style="color:#38bdf8; margin-bottom:20px;">🏆 NEURAL HALL OF FAME</h2>';
        listHTML += '<table style="width:100%; border-collapse:collapse; margin-bottom:30px;">';
        listHTML += '<tr style="border-bottom:1px solid #1e293b; color:#94a3b8;"><th style="padding:10px;">POS</th><th style="padding:10px;">PILOT</th><th style="padding:10px;">SCORE</th></tr>';
        
        scores.forEach((s, i) => {
            listHTML += `<tr style="border-bottom:1px solid #0f172a; ${i===0?'color:#f59e0b;':''}">
                <td style="padding:10px;">#${i+1}</td>
                <td style="padding:10px;">${s.name}</td>
                <td style="padding:10px;">${s.score.toLocaleString()}</td>
            </tr>`;
        });
        listHTML += '</table>';
        listHTML += '<button id="btn-lb-close" style="background:#3b82f6; color:#fff; border:none; padding:10px 30px; cursor:pointer; border-radius:5px;">CLOSE</button>';

        modal.innerHTML = listHTML;
        document.body.appendChild(modal);

        document.getElementById('btn-lb-close').onclick = () => {
            modal.remove();
            this.setCombatMode(false);
            this.setPilotMode(true);
        };
    }

    createCombatHUD() {
        this.removeCombatHUD();
        const hud = document.createElement('div');
        hud.id = 'combat-hud-overlay';
        hud.style.cssText = `
            position: absolute; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none; z-index: 9005;
            display: flex; flex-direction: column; justify-content: space-between; padding: 20px;
        `;

        // Top Bar (Deflectors & Score) - Added first to be at the top in flex-column
        const topBar = document.createElement('div');
        topBar.style.cssText = "display:flex; justify-content:space-between; align-items:flex-start; font-family:'JetBrains Mono'; flex-shrink:0; margin-top:100px;";
        
        const healthContainer = document.createElement('div');
        healthContainer.innerHTML = `
            <div style="color:#ef4444; font-weight:bold; font-size:1.2rem; text-shadow:0 0 5px #ef4444;">DEFLECTORS</div>
            <div style="width:300px; height:15px; background:rgba(255,255,255,0.1); border:1px solid #ef4444; margin-top:5px;">
                <div id="combat-health-bar" style="width:100%; height:100%; background:#ef4444; transition:width 0.2s; box-shadow:0 0 10px #ef4444;"></div>
            </div>
        `;
        
        const scoreContainer = document.createElement('div');
        scoreContainer.innerHTML = `
            <div style="color:#38bdf8; font-weight:bold; font-size:1.5rem; text-align:right; text-shadow:0 0 5px #38bdf8;">SCORE: <span id="combat-score-val">0</span></div>
            <div style="color:#f59e0b; font-weight:bold; font-size:1rem; text-align:right; text-shadow:0 0 5px #f59e0b;">KILLS: <span id="combat-kills-val">0</span> / <span id="combat-next-boss-val">10</span></div>
            <div id="combat-ammo-container" style="color:#a855f7; font-weight:bold; font-size:1rem; text-align:right; display:none; text-shadow:0 0 5px #a855f7;">ULTRA BLASTER: <span id="combat-ammo-val">0</span></div>
        `;

        topBar.appendChild(healthContainer);
        topBar.appendChild(scoreContainer);
        hud.appendChild(topBar);

        // Crosshair (Absolute center)
        const crosshair = document.createElement('div');
        crosshair.style.cssText = "position:absolute; top:0; left:0; width:100%; height:100%; pointer-events:none;";
        crosshair.innerHTML = `
            <div style="position:absolute; top:50%; left:50%; transform:translate(-50%, -50%); width:60px; height:60px; border:2px solid rgba(16,185,129,0.8); border-radius:50%; box-shadow: 0 0 10px #10b981;"></div>
            <div style="position:absolute; top:50%; left:50%; transform:translate(-50%, -50%); width:2px; height:20px; background:#10b981; box-shadow: 0 0 5px #10b981;"></div>
            <div style="position:absolute; top:50%; left:50%; transform:translate(-50%, -50%); width:20px; height:2px; background:#10b981; box-shadow: 0 0 5px #10b981;"></div>
        `;
        hud.appendChild(crosshair);

        document.getElementById('overview-view').appendChild(hud);
    }

    removeCombatHUD() {
        const hud = document.getElementById('combat-hud-overlay');
        if (hud) hud.remove();
    }

    updateCombatHUD() {
        const healthBar = document.getElementById('combat-health-bar');
        const scoreVal = document.getElementById('combat-score-val');
        const ammoCont = document.getElementById('combat-ammo-container');
        const ammoVal = document.getElementById('combat-ammo-val');

        if (healthBar) healthBar.style.width = Math.max(0, this.health) + '%';
        if (scoreVal) scoreVal.innerText = this.score;
        const killsVal = document.getElementById('combat-kills-val');
        const nextBossVal = document.getElementById('combat-next-boss-val');
        if (killsVal) killsVal.innerText = this.enemiesKilled;
        if (nextBossVal) nextBossVal.innerText = this.nextBossThreshold;
        if (ammoCont && ammoVal) {
            ammoCont.style.display = 'block';
            ammoCont.innerHTML = `
                <div style="color:#a855f7;">ULTRA BLASTER: ${this.ultraBlasterAmmo}</div>
                <div style="color:#f43f5e;">HEAVY BLASTER (O): ${this.heavyBlasterAmmo}</div>
                <div style="color:#38bdf8;">SHIELDS (SPACE): ${this.shieldCharges}/3</div>
                <div style="color:#94a3b8; font-size:0.7rem; margin-top:5px;">SPACE: SHIELD | O: HEAVY BLASTER | E: SHOOT</div>
            `;
        }
    }

    initShipMesh() {
        const group = new THREE.Group();
        
        // 💎 [v12.6] High-Visibility Basic Materials (Glow effect, ignores dark lighting)
        const bodyMat = new THREE.MeshBasicMaterial({ color: 0xffffff }); // Pure White
        const greyMat = new THREE.MeshBasicMaterial({ color: 0x64748b }); // Technical Grey
        const azureMat = new THREE.MeshBasicMaterial({ color: 0x0ea5e9 }); // Azure Accents
        const cockpitMat = new THREE.MeshBasicMaterial({ color: 0x0ea5e9, transparent: true, opacity: 0.6 });
        const engineMat = new THREE.MeshBasicMaterial({ color: 0x1e293b });
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

        // Wings
        const wingWidth = 4500; const wingDepth = 1800;
        const thrusterMat = new THREE.MeshBasicMaterial({ 
            color: 0xffffff, transparent: true, opacity: 0.8
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
            
            wingGroup.rotation.z = (Math.PI / 4) + (i * Math.PI / 2);
            group.add(wingGroup);
        }

        const r2 = new THREE.Mesh(new THREE.CylinderGeometry(100, 100, 200), new THREE.MeshBasicMaterial({color: 0xffffff}));
        r2.position.set(0, 350, -300); group.add(r2);
        const r2Head = new THREE.Mesh(new THREE.SphereGeometry(100, 8, 8), new THREE.MeshBasicMaterial({color: 0x3b82f6}));
        r2Head.position.set(0, 450, -300); group.add(r2Head);

        const container = new THREE.Group();
        group.rotation.y = Math.PI;
        container.add(group);

        this.shipMesh = container;
        // 🛡️ Disable Frustum Culling to ensure it's ALWAYS rendered
        this.shipMesh.frustumCulled = false;
        this.shipMesh.traverse(child => { if(child.isMesh) child.frustumCulled = false; });
        
        this.shipMesh.position.copy(this.position);
        this.shipMesh.visible = this.active;

        // 🛡️ [v13.5] Shield Bubble Mesh
        const shieldGeo = new THREE.SphereGeometry(6000, 32, 32);
        const shieldMat = new THREE.MeshBasicMaterial({ 
            color: 0x38bdf8, transparent: true, opacity: 0.3, wireframe: true 
        });
        this.shieldMesh = new THREE.Mesh(shieldGeo, shieldMat);
        this.shieldMesh.visible = false;
        this.shieldMesh.scale.setScalar(0.01);
        this.shieldMesh.material.opacity = 0;
        this.shipMesh.add(this.shieldMesh);

        this.scene.add(this.shipMesh);
    }

    update(delta) {
        if(!this.active || !this.shipMesh) return;
        this.lastDelta = delta;

        // 🛡️ [v13.8] Premium Shield Animation & Rotation
        if (this.shieldMesh) {
            if (this.shieldActive) {
                this.shieldMesh.visible = true;
                this.shieldMesh.rotation.y += 0.02;
                this.shieldMesh.rotation.z += 0.01;
                
                // Gradual entry with a "flicker" effect during start
                const targetScale = 1.0 + Math.sin(Date.now() * 0.02) * 0.02; // Subtle pulse
                this.shieldMesh.scale.lerp(new THREE.Vector3(targetScale, targetScale, targetScale), 0.1);
                
                const targetOpacity = 0.4 + Math.random() * 0.1; // Energy flicker
                this.shieldMesh.material.opacity = THREE.MathUtils.lerp(this.shieldMesh.material.opacity, targetOpacity, 0.1);
            } else {
                this.shieldMesh.scale.lerp(new THREE.Vector3(0.01, 0.01, 0.01), 0.15);
                this.shieldMesh.material.opacity = THREE.MathUtils.lerp(this.shieldMesh.material.opacity, 0, 0.15);
                if (this.shieldMesh.scale.x < 0.05) this.shieldMesh.visible = false;
            }
        }

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
        
        // 🛠️ [Fix] Force matrix update before camera calculation
        this.shipMesh.updateMatrixWorld(true);

        // Play engine/boost sounds
        if (this.combatMode) {
            this.sfx.playEngine(this.velocity.length());
            if (isBoosting && !this.keys.p_last) {
                this.sfx.playBoost();
            }
            this.keys.p_last = isBoosting;
        }

        if (this.viewMode === 0) {
            // [v8.4] Aumentata la distanza della telecamera (200% più lontana) come richiesto
            const relativeCameraOffset = new THREE.Vector3(0, 1800, 10500); 
            const cameraOffset = relativeCameraOffset.applyMatrix4(this.shipMesh.matrixWorld);
            this.camera.position.copy(cameraOffset);
            
            // 🎯 [Fix] Usa la posizione assoluta nel mondo (World Space) per il puntamento della telecamera
            const worldPos = new THREE.Vector3();
            this.shipMesh.getWorldPosition(worldPos);
            this.camera.lookAt(worldPos);
            
            this.shipMesh.visible = true; // Ripristina la nave
            if (this.cockpitGlass) this.cockpitGlass.visible = true;
            if (this.cockpitInternal) this.cockpitInternal.visible = false;
            
            const overlay = document.getElementById('arcade-cockpit-overlay');
            if (overlay) overlay.style.display = 'none';
        } else {
            // [v8.5] Arcade Cockpit PNG Overlay - Telecamera al centro esatto
            const cockpitOffset = new THREE.Vector3(0, 0, 0); 
            const cameraPos = cockpitOffset.applyMatrix4(this.shipMesh.matrixWorld);
            this.camera.position.copy(cameraPos);
            this.camera.quaternion.copy(this.shipMesh.quaternion);
            
            // Nasconde completamente la mesh 3D della nave
            this.shipMesh.visible = false;
            
            const overlay = document.getElementById('arcade-cockpit-overlay');
            if (overlay) {
                overlay.style.display = 'block';
                
                // 📊 [v14.0] Update Cockpit Telemetry
                const altVal = document.getElementById('cockpit-alt-val');
                const velVal = document.getElementById('cockpit-vel-val');
                const rpmBar = document.getElementById('cockpit-rpm-bar');
                
                if (altVal) altVal.innerText = Math.floor(this.position.y).toLocaleString();
                if (velVal) velVal.innerText = (this.velocity.length() / delta).toFixed(2);
                if (rpmBar) {
                    const speedRatio = Math.min(1, this.velocity.length() / (this.speed * this.hyperSpeedMultiplier * delta));
                    rpmBar.style.width = (20 + speedRatio * 80) + '%';
                }
            }
        }

        if (this.combatMode) {
            this.updateCombat(delta);
        }
    }

    updateCombat(delta) {
        if (this.health <= 0) {
            this.gameOver();
            return;
        }

        const now = Date.now();
        
        // --- Spawning Logic (Frenetic Escalation) ---
        const currentMaxEnemies = Math.min(50, 15 + Math.floor(this.enemiesKilled / 2));
        const spawnChance = Math.min(0.15, 0.02 + (this.enemiesKilled * 0.0015));
        
        if (Math.random() < spawnChance && this.enemies.length < currentMaxEnemies) {
            this.spawnEnemy();
        }
        
        // Check for boss spawn every 50 kills
        if (this.enemiesKilled >= this.nextBossThreshold) {
            this.spawnBoss();
            this.nextBossThreshold += 10;
        }

        // --- Lasers Physics (Player) ---
        for (let i = this.lasers.length - 1; i >= 0; i--) {
            const l = this.lasers[i];
            l.mesh.position.add(l.velocity.clone().multiplyScalar(delta));
            l.life--;
            if (l.life <= 0) {
                this.scene.remove(l.mesh);
                this.lasers.splice(i, 1);
                continue;
            }

            // Collision with enemies
            let hit = false;
            for (let j = this.enemies.length - 1; j >= 0; j--) {
                const e = this.enemies[j];
                // 🛡️ [v14.0] Broadened Collision Radius (Prevents "tunnelling" at extreme speeds)
                if (l.mesh.position.distanceTo(e.mesh.position) < 150000) {
                    this.scene.remove(e.mesh);
                    this.enemies.splice(j, 1);
                    hit = true;
                    this.score += 100;
                    this.enemiesKilled++;
                    this.spawnExplosion(e.mesh.position, 0xef4444);
                    this.sfx.playExplosion();
                    
                    // 🚀 [v13.5] Diverse Powerup Drops (Increased to 60% total drop rate)
                    const roll = Math.random();
                    if (roll < 0.25) this.spawnPowerup(e.mesh.position.clone(), 'SENTINEL');
                    else if (roll < 0.45) this.spawnPowerup(e.mesh.position.clone(), 'CANNON');
                    else if (roll < 0.60) this.spawnPowerup(e.mesh.position.clone(), 'ULTRA');
                    break;
                }
            }
            if (hit) {
                this.scene.remove(l.mesh);
                this.lasers.splice(i, 1);
                this.updateCombatHUD();
                continue;
            }

            // Collision with Bosses
            for (let j = this.bosses.length - 1; j >= 0; j--) {
                const b = this.bosses[j];
                if (l.mesh.position.distanceTo(b.mesh.position) < 120000) {
                    b.hp -= l.isUltra ? 50 : 5;
                    hit = true;
                    this.spawnExplosion(l.mesh.position, 0xffaa00);
                    
                    if (b.healthBarFill) {
                        b.healthBarFill.scale.x = Math.max(0.01, b.hp / 500);
                    }

                    if (b.hp <= 0) {
                        this.scene.remove(b.mesh);
                        if (b.healthBar) this.scene.remove(b.healthBar);
                        this.bosses.splice(j, 1);
                        this.score += 5000;
                        this.spawnExplosion(b.mesh.position, 0xff0000, 30); // Giant explosion
                    }
                    break;
                }
            }
            if (hit) {
                this.scene.remove(l.mesh);
                this.lasers.splice(i, 1);
                this.updateCombatHUD();
            }
        }

        // --- Enemies Physics & Animation ---
        for (let i = this.enemies.length - 1; i >= 0; i--) {
            const e = this.enemies[i];
            
            // 🐙 [v13.7] Alien "Tentacles" Animation (Space Invader Style)
            const legScale = 1.0 + Math.sin(now * 0.01) * 0.3;
            const wobble = Math.sin(now * 0.005) * 0.2;
            e.mesh.children.forEach((child, idx) => {
                // If it's a leg voxel (bottom rows)
                if (idx > 30) { 
                    child.scale.y = legScale;
                    child.position.y = child.userData.origY * legScale;
                    child.rotation.z = wobble * (idx % 2 === 0 ? 1 : -1);
                }
            });

            e.mesh.lookAt(this.shipMesh.position);
            const dir = new THREE.Vector3().subVectors(this.shipMesh.position, e.mesh.position).normalize();
            e.mesh.position.add(dir.multiplyScalar(20000 * delta)); // Aggressive seeking

            if (e.mesh.position.distanceTo(this.shipMesh.position) < 20000) {
                this.health -= 10;
                this.scene.remove(e.mesh);
                this.enemies.splice(i, 1);
                this.enemiesKilled++;
                this.updateCombatHUD();
                this.sfx.playExplosion();
            } else if (now - e.lastShot > e.shootDelay) {
                // ☄️ [v13.5] Spherical Fireballs from Aliens
                const fireballGeo = new THREE.SphereGeometry(2000, 16, 16);
                const fireballMat = new THREE.MeshBasicMaterial({ color: 0xf97316 }); // Orange Fire
                const fireball = new THREE.Mesh(fireballGeo, fireballMat);
                fireball.position.copy(e.mesh.position);
                fireball.lookAt(this.shipMesh.position);
                
                const velocity = new THREE.Vector3(0, 0, -1).applyQuaternion(fireball.quaternion).multiplyScalar(300000);
                this.scene.add(fireball);
                if (!this.enemyLasers) this.enemyLasers = [];
                this.enemyLasers.push({ mesh: fireball, velocity: velocity, life: 400, isFireball: true });
                
                e.lastShot = now;
                e.shootDelay = 8000 + Math.random() * 10000; // 8-18 seconds random delay
            }
        }

        // --- Bosses Physics & Turret Fire ---
        this.bosses.forEach(b => {
            b.mesh.lookAt(this.shipMesh.position);
            const dir = new THREE.Vector3().subVectors(this.shipMesh.position, b.mesh.position).normalize();
            // 🚀 [v14.1] Aggressive Boss Speed (Matching player base speed)
            b.mesh.position.add(dir.multiplyScalar(12000 * delta)); 

            if (b.healthBar) {
                b.healthBar.position.copy(b.mesh.position);
                b.healthBar.position.y += 120000;
                b.healthBar.lookAt(this.camera.position);
            }

            if (now - b.lastShot > 600) { // Aggressive fire rate
                if (b.mesh.position.distanceTo(this.shipMesh.position) < 1500000) {
                    // 🔫 Fire from a random turret
                    const turret = b.turrets[Math.floor(Math.random() * b.turrets.length)];
                    const turretWorldPos = new THREE.Vector3();
                    turret.getWorldPosition(turretWorldPos);

                    const laserGeo = new THREE.CylinderGeometry(80, 80, 5000, 8);
                    laserGeo.rotateX(Math.PI / 2);
                    const laserMat = new THREE.MeshBasicMaterial({ color: 0xff0000 });
                    const laser = new THREE.Mesh(laserGeo, laserMat);
                    laser.position.copy(turretWorldPos);
                    laser.lookAt(this.shipMesh.position);
                    
                    const velocity = new THREE.Vector3(0, 0, -1).applyQuaternion(laser.quaternion).multiplyScalar(600000);
                    this.scene.add(laser);
                    if (!this.enemyLasers) this.enemyLasers = [];
                    this.enemyLasers.push({ mesh: laser, velocity: velocity, life: 300 });

                    b.lastShot = now;
                    if (this.sfx) this.sfx.playLaser();
                }
            }
        });

        // --- Enemy Lasers Physics ---
        if (this.enemyLasers) {
            for (let i = this.enemyLasers.length - 1; i >= 0; i--) {
                const l = this.enemyLasers[i];
                l.mesh.position.add(l.velocity.clone().multiplyScalar(delta));
                l.life--;
                if (l.life <= 0) {
                    this.scene.remove(l.mesh);
                    this.enemyLasers.splice(i, 1);
                    continue;
                }
                if (l.mesh.position.distanceTo(this.shipMesh.position) < 8000) {
                    // 🛡️ [v13.5] Shield Defense Logic
                    if (this.shieldActive && this.shieldCharges > 0) {
                        this.shieldCharges--;
                        this.spawnExplosion(l.mesh.position, 0x38bdf8, 5); // Blue shield spark
                        if (this.shieldCharges <= 0) {
                            this.toggleShield(false);
                            if (typeof log === 'function') log("⚠️ SHIELD DEPLETED!", "#ef4444");
                        }
                    } else {
                        this.health -= 15;
                        this.spawnExplosion(this.shipMesh.position, 0xef4444, 5);
                    }
                    this.updateCombatHUD();
                    this.scene.remove(l.mesh);
                    this.enemyLasers.splice(i, 1);
                    continue;
                }
            }
        }

        // --- Explosions Physics ---
        if (this.explosions) {
            for (let i = this.explosions.length - 1; i >= 0; i--) {
                const exp = this.explosions[i];
                exp.life -= delta * 1.5;
                if (exp.life <= 0) {
                    exp.particles.forEach(p => this.scene.remove(p.mesh));
                    this.explosions.splice(i, 1);
                    continue;
                }
                exp.particles.forEach(p => {
                    p.mesh.position.add(p.velocity.clone().multiplyScalar(delta));
                    p.mesh.material.opacity = exp.life;
                    p.mesh.scale.setScalar(exp.life);
                });
            }
        }

        // --- Powerups Physics & Collection ---
        for (let i = this.powerups.length - 1; i >= 0; i--) {
            const p = this.powerups[i];
            p.mesh.rotation.y += 0.05;
            p.mesh.rotation.z += 0.02;
            
            if (p.mesh.position.distanceTo(this.shipMesh.position) < 50000) {
                if (p.type === 'SENTINEL') {
                    this.shieldCharges = 3;
                    if (typeof log === 'function') log("🛡️ SENTINEL ACQUIRED: SHIELDS RECHARGED!", "#38bdf8");
                } else if (p.type === 'CANNON') {
                    this.heavyBlasterAmmo = 8;
                    if (typeof log === 'function') log("🚀 HEAVY BLASTER ACQUIRED! (8 ROUNDS - PRESS O)", "#f43f5e");
                } else {
                    this.ultraBlasterAmmo += 8;
                    if (typeof log === 'function') log("⚡ ULTRA BLASTER ACQUIRED!", "#a855f7");
                }
                this.scene.remove(p.mesh);
                this.powerups.splice(i, 1);
                this.updateCombatHUD();
            }
        }
    }

    spawnEnemy() {
        // High-Fidelity Distiller Clone (Matching actual agent size)
        const group = new THREE.Group();
        const colors = [0xef4444, 0xf59e0b, 0xa855f7, 0x10b981, 0x3b82f6]; 
        const color = colors[Math.floor(Math.random() * colors.length)];
        // 🛡️ [v14.0] Self-Illuminated Basic Material for guaranteed visibility
        const mat = new THREE.MeshBasicMaterial({ color: color });
        
        const pixels = [
            [0,0,1,0,0,0,1,0,0],
            [0,0,0,1,0,1,0,0,0],
            [0,0,1,1,1,1,1,0,0],
            [0,1,1,0,1,0,1,1,0],
            [1,1,1,1,1,1,1,1,1],
            [1,0,1,1,1,1,1,0,1],
            [1,0,1,0,0,0,1,0,1],
            [0,0,0,1,0,1,0,0,0]
        ];
        
        const vSize = 8000; // Original Agent Voxel Size
        pixels.forEach((row, y) => row.forEach((p, x) => {
            if(p) {
                const v = new THREE.Mesh(new THREE.BoxGeometry(vSize, vSize, vSize), mat);
                v.position.set((x - 4) * vSize, (4 - y) * vSize, 0);
                v.userData.origY = v.position.y;
                group.add(v);
            }
        }));

        // 📏 [v13.5] Extreme Spawn Distance (Min 5,000,000 between each other)
        let offset;
        let attempts = 0;
        do {
            offset = new THREE.Vector3(
                (Math.random() - 0.5) * 40000000, 
                (Math.random() - 0.5) * 40000000, 
                -(Math.random() * 5000000 + 5000000) // 📏 [v13.9] Min 5M distance from player
            ).applyEuler(this.rotation);
            attempts++;
            
            // Simplified check: only check against existing enemies if we have few
            let tooClose = false;
            if (this.enemies.length > 0 && attempts < 10) {
                const targetPos = this.shipMesh.position.clone().add(offset);
                for (const e of this.enemies) {
                    if (e.mesh.position.distanceTo(targetPos) < 5000000) {
                        tooClose = true; break;
                    }
                }
            }
            if (!tooClose) break;
        } while (attempts < 20);

        group.position.copy(this.shipMesh.position).add(offset);
        this.scene.add(group);
        this.enemies.push({ 
            mesh: group, 
            lastShot: Date.now(),
            shootDelay: 8000 + Math.random() * 10000 // 8-18 seconds random delay
        });
    }

    spawnBoss() {
        console.log("👾 [Combat] BOSS SPAWN TRIGGERED at threshold:", this.nextBossThreshold);
        const group = new THREE.Group();
        
        // 🏛️ [v14.1] MEGA STAR DESTROYER - Ultra Detailed
        const hullMat = new THREE.MeshBasicMaterial({ color: 0x94a3b8 }); // Lighter grey for better contrast
        const darkHullMat = new THREE.MeshBasicMaterial({ color: 0x475569 });
        const engineGlowMat = new THREE.MeshBasicMaterial({ color: 0x38bdf8 });
        
        // 1. Main Wedge (The iconic silhouette)
        const wedgeGeo = new THREE.CylinderGeometry(0, 160000, 500000, 3);
        wedgeGeo.rotateX(Math.PI / 2);
        wedgeGeo.rotateZ(Math.PI / 6);
        const wedge = new THREE.Mesh(wedgeGeo, hullMat);
        wedge.scale.set(1, 0.2, 1);
        group.add(wedge);

        // 2. Lateral Trenches (Depth)
        for(let side of [-1, 1]) {
            const trench = new THREE.Mesh(new THREE.BoxGeometry(10000, 15000, 480000), darkHullMat);
            trench.position.set(side * 40000, 0, 0);
            trench.rotation.y = side * 0.1;
            group.add(trench);
        }

        // 3. Central Superstructure Hierarchy
        const deck1 = new THREE.Mesh(new THREE.BoxGeometry(80000, 10000, 120000), hullMat);
        deck1.position.set(0, 20000, -80000);
        group.add(deck1);

        const deck2 = new THREE.Mesh(new THREE.BoxGeometry(50000, 8000, 80000), darkHullMat);
        deck2.position.set(0, 30000, -100000);
        group.add(deck2);

        const bridge = new THREE.Mesh(new THREE.BoxGeometry(30000, 6000, 20000), hullMat);
        bridge.position.set(0, 38000, -110000);
        group.add(bridge);

        // 4. Iconic Shield Domes (Sensor Arrays)
        const domeGeo = new THREE.SphereGeometry(8000, 16, 16);
        for(let side of [-1, 1]) {
            const dome = new THREE.Mesh(domeGeo, hullMat);
            dome.position.set(side * 15000, 45000, -115000);
            group.add(dome);
        }

        // 5. Massive Engines (Rear Glow)
        const engineGeo = new THREE.CylinderGeometry(20000, 25000, 15000, 16);
        engineGeo.rotateX(Math.PI / 2);
        const enginePositions = [[0, 0, -250000], [50000, 0, -245000], [-50000, 0, -245000]];
        enginePositions.forEach(p => {
            const engine = new THREE.Mesh(engineGeo, darkHullMat);
            engine.position.set(p[0], p[1], p[2]);
            group.add(engine);
            
            const glow = new THREE.Mesh(new THREE.CircleGeometry(22000, 16), engineGlowMat);
            glow.position.set(p[0], p[1], p[2] - 7600);
            glow.rotation.y = Math.PI;
            group.add(glow);
        });

        // 🔫 Automated Heavy Turret Batteries
        const turrets = [];
        const turretGeo = new THREE.BoxGeometry(8000, 6000, 8000);
        const turretMat = new THREE.MeshBasicMaterial({ color: 0xef4444 });
        
        const turretPositions = [
            [-50000, 15000, 50000], [50000, 15000, 50000],
            [-30000, 25000, -20000], [30000, 25000, -20000],
            [-10000, 42000, -110000], [10000, 42000, -110000],
            [0, 10000, 150000] // Front battery
        ];

        turretPositions.forEach(p => {
            const tGroup = new THREE.Group();
            const base = new THREE.Mesh(turretGeo, turretMat);
            tGroup.add(base);
            const barrel = new THREE.Mesh(new THREE.CylinderGeometry(1000, 1000, 15000), turretMat);
            barrel.rotateX(Math.PI / 2); barrel.position.z = 8000;
            tGroup.add(barrel);
            
            tGroup.position.set(p[0], p[1], p[2]);
            group.add(tGroup);
            turrets.push(tGroup);
        });

        // 🏥 Boss Health Bar
        const healthBarGroup = new THREE.Group();
        const bgGeo = new THREE.PlaneGeometry(200000, 10000);
        const bgMesh = new THREE.Mesh(bgGeo, new THREE.MeshBasicMaterial({ color: 0x310000, side: THREE.DoubleSide }));
        
        const fgGeo = new THREE.PlaneGeometry(200000, 10000);
        fgGeo.translate(100000, 0, 0); 
        const fgMat = new THREE.MeshBasicMaterial({ color: 0xff0000, side: THREE.DoubleSide });
        const fgMesh = new THREE.Mesh(fgGeo, fgMat);
        fgMesh.position.x = -100000;
        healthBarGroup.add(bgMesh, fgMesh);

        // Spawn logic - Rescaled distance to 3,000,000 for visibility
        const spawnDist = 3000000;
        const forward = new THREE.Vector3(0, 0, -spawnDist).applyEuler(this.rotation);
        group.position.copy(this.shipMesh.position).add(forward);
        healthBarGroup.position.copy(group.position).add(new THREE.Vector3(0, 120000, 0));
        
        this.scene.add(group);
        this.scene.add(healthBarGroup);
        
        this.bosses.push({ 
            mesh: group, 
            hp: 10000, 
            lastShot: Date.now(), 
            healthBar: healthBarGroup, 
            healthBarFill: fgMesh,
            turrets: turrets
        });

        if (typeof log === 'function') log("🚨 WARNING: IMPERIAL STAR DESTROYER DEPLOYED!", "#ef4444");
    }

    spawnExplosion(pos, colorHex = 0xffa500, particleCount = 60) {
        if (!this.explosions) this.explosions = [];
        const particles = [];
        const mat = new THREE.MeshBasicMaterial({ color: colorHex, transparent: true });
        const geo = new THREE.BoxGeometry(50000, 50000, 50000); // 💥 Massive explosion for deep space visibility
        for(let i=0; i<particleCount; i++) {
            const p = new THREE.Mesh(geo, mat);
            p.position.copy(pos);
            const vel = new THREE.Vector3(
                (Math.random() - 0.5) * 80000,
                (Math.random() - 0.5) * 80000,
                (Math.random() - 0.5) * 80000
            );
            this.scene.add(p);
            particles.push({ mesh: p, velocity: vel });
        }
        this.explosions.push({ particles: particles, life: 2.5 }); // Longer life
    }

    spawnPowerup(pos, type = 'ULTRA') {
        let geo, mat, color;
        if (type === 'SENTINEL') {
            // 🛡️ [v14.2] Normalized Sentinel Sprite (40% of Alien: 32,000 unit diameter)
            geo = new THREE.SphereGeometry(16000, 16, 16);
            color = 0x38bdf8;
        } else if (type === 'CANNON') {
            // 🚀 [v14.2] Normalized Cannon Sprite (40% of Alien: 32,000 unit height)
            geo = new THREE.CylinderGeometry(10000, 10000, 32000);
            geo.rotateX(Math.PI / 2);
            color = 0xf43f5e;
        } else {
            // ⚡ [v14.2] Normalized Ultra Sprite (40% of Alien: 32,000 unit box)
            geo = new THREE.BoxGeometry(32000, 32000, 32000);
            color = 0xa855f7;
        }

        mat = new THREE.MeshBasicMaterial({ color: color, wireframe: type !== 'ULTRA' });
        const mesh = new THREE.Mesh(geo, mat);
        mesh.position.copy(pos);
        this.scene.add(mesh);
        this.powerups.push({ mesh: mesh, type: type });
    }
}

window.toggleCombatMode = function(state) {
    if (window.playerController) {
        window.playerController.setCombatMode(state);
    }
};
