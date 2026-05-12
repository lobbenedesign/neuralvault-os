/**
 * 🛠️ NEURALVAULT UTILS
 */

function log(msg, color = '#4ade80') {
    window.log = log; 
    const consoleDiv = document.getElementById('aura-console');
    if (!consoleDiv) return;
    const line = document.createElement('div');
    line.style.color = color;
    line.innerHTML = `> [${new Date().toLocaleTimeString()}] ${msg}`;
    consoleDiv.prepend(line);
    
    // Backend log sync
    fetch('/api/log', { 
        method: 'POST', 
        headers: { 'Content-Type': 'application/json', 'X-API-KEY': window.VAULT_KEY },
        body: JSON.stringify({ message: msg, level: 'HUD' })
    }).catch(()=>{});
}
window.log = log;

function createTextSprite(text, color) {
    const canvas = document.createElement('canvas');
    canvas.width = 1024; canvas.height = 256;
    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, 1024, 256);
    ctx.font = 'Bold 80px JetBrains Mono';
    ctx.textAlign = 'center';
    ctx.fillStyle = color;
    ctx.fillText(text, 512, 140);
    
    const texture = new THREE.CanvasTexture(canvas);
    const spriteMaterial = new THREE.SpriteMaterial({ map: texture, transparent: true, alphaTest: 0.1, depthWrite: false });
    const sprite = new THREE.Sprite(spriteMaterial);
    sprite.scale.set(200000, 50000, 1);
    return sprite;
}

function spawnReaperMonument(pos) {
    const geo = new THREE.BoxGeometry(80000, 80000, 80000);
    const mat = new THREE.MeshPhongMaterial({ 
        color: 0xffffff, 
        transparent: true, 
        opacity: 0.3,
        shininess: 100
    });
    const cubeMesh = new THREE.Mesh(geo, mat);
    cubeMesh.position.set(pos.x, pos.y, pos.z);
    
    // Add Red Crosses to each face
    const crossSize = 60000;
    const crossGeoH = new THREE.BoxGeometry(crossSize, 10000, 2000);
    const crossGeoV = new THREE.BoxGeometry(10000, crossSize, 2000);
    const crossMat = new THREE.MeshBasicMaterial({ color: 0xff0000 });
    
    const directions = [
        [0, 0, 1], [0, 0, -1], [1, 0, 0], [-1, 0, 0], [0, 1, 0], [0, -1, 0]
    ];
    directions.forEach(d => {
        const h = new THREE.Mesh(crossGeoH, crossMat);
        const v = new THREE.Mesh(crossGeoV, crossMat);
        const group = new THREE.Group();
        group.add(h); group.add(v);
        group.position.set(d[0]*40001, d[1]*40001, d[2]*40001);
        if (d[0] !== 0) group.rotation.y = Math.PI/2;
        if (d[1] !== 0) group.rotation.x = Math.PI/2;
        cubeMesh.add(group);
    });

    scene.add(cubeMesh);
    reaperCubes.push({ mesh: cubeMesh, expiry: Date.now() + 600000 }); // 10 minutes
}

function lerpColor(a, b, amount) {
    const ar = a >> 16, ag = a >> 8 & 0xff, ab = a & 0xff;
    const br = b >> 16, bg = b >> 8 & 0xff, bb = b & 0xff;
    const r = ar + (br - ar) * amount;
    const g = ag + (bg - ag) * amount;
    const bl = ab + (bb - ab) * amount;
    return (r << 16) | (g << 8) | bl;
}
