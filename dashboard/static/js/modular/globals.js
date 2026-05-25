/**
 * 🌐 NEURALVAULT GLOBAL STATE
 */

// --- 🏗️ Core Three.js Objects ---
var scene, camera, renderer, pointsMesh, linksMesh, neuralLinks, cube, raycaster, mouse, agentsContainer, ignoranceGroup, clusterNodesGroup, controls;

// --- 🤖 Agent Groups & Labels ---
var janitronGroup, janitronTop, janitronBottom, janitronLabel;
var distillerGroup, distillerLabel;
var reaperGroup, reaperLabel; 
var snakeGroup, snakeSegments = [], snakeLabel;
var quantumGroup, quantumLabel, quantumCore;
var sentinelGroup, sentinelLabel, sentinelShield;
var synthGroup, synthLabel, synthMesh, synthMouth, synthSparkGroup, synthSparkTime = 0, synthSubAgents = [];
var skywalkerGroup, skywalkerLabel, yodaGroup, yodaLabel;
var r2d2Group, r2d2Label, compressorGroup, compressorLabel;
var mandalorianGroup, mandalorianLabel;
var pressmanGroup, pressmanLabel, pressmanPapers = [], pressmanNewspapers;
var smithFleetGroups = {}; // 🕶️ Security fleet by peerId
var smithTargetPositions = {}; 
var smithLabel; 
var bridgerGroup, bridgerLabel;

// --- 🎯 Target Coordinates ---
var skywalkerTargetPos = new THREE.Vector3(250000, 250000, 250000);
var yodaTargetPos = new THREE.Vector3(0, 0, 0);
var mandalorianTargetPos = new THREE.Vector3(200000, 50000, 200000);
var janitronTargetPos = new THREE.Vector3(500000, 200000, 500000);
var distillerTargetPos = new THREE.Vector3(-200000, 200000, -200000);
var reaperTargetPos = new THREE.Vector3(0, 300000, 0);
var snakeTargetPos = new THREE.Vector3(0, 0, 0);
var snakeCurrentTarget = new THREE.Vector3(1200000, 0, 0);
var quantumTargetPos = new THREE.Vector3(800000, 800000, 800000);
var sentinelTargetPos = new THREE.Vector3(-500000, -500000, 500000);
var synthTargetPos = new THREE.Vector3(0, 500000, 0);
var bridgerTargetPos = new THREE.Vector3(0, 0, 0);
var r2d2TargetPos = new THREE.Vector3(-600000, -400000, 600000);
var pressmanTargetPos = new THREE.Vector3(500000 * 4, 500000 * 4, 500000 * 4);

// --- ⏱️ Timing & Animation State ---
let janitronFlashTime = 0;
let distillerFlashTime = 0;
let quantumFlashTime = 0;
let synthFlashTime = 0;
let sentinelFlashTime = 0;
let sentinelLightningTime = 0;
let bridgerPulseTime = 0;
let lastSnakeStep = 0;
let lastReaperProcessed = 0, lastJanitorPurged = 0, lastDistillerPruned = 0;
let lastQuantumClusters = 0, lastSynthSparks = 0;
let snakeDirection = new THREE.Vector3(1, 0, 0);

// --- 📟 System State & Arrays ---
var eventSource, vaultPoints = [], installedModels = [];
var currentHeatmap = {}, heatmapMode = false;
var reaperCubes = []; // {mesh, expiry}
var medicalCubes = [];
var lastAgentStates = {}; 
var skywalkerLasers = [];
var yodaBullets = [];
var smithLasers = [];
var lastNeuralLinks = [];
var multimodalGroup, multimodalTextures = {}; 

// --- ⚙️ User Settings & Flags ---
let isEvolving = false;
let evolutionProgress = 0;
let evolutionStep = "";
var followedAgent = null;
let isRotationPaused = false;
let isUserInteracting = false;
let layersVisibility = { agents: true, orphans: true, nodes: true, linked_nodes: true, edges: true, sparks: true, cube: true, grid: true, nav_guide: true, wormholes: true };
let timeTravelFactor = 1.0;
let nebulaQuality = 'HD';
let clusterFocus = true;
let radarChart = null; 
let nebulaExpansionFactor = 1.0;
let galaxyRepulsionFactor = 25.0; // Dynamic multiplier for galaxy node repulsion
let is3DInitialized = false;
let isRenderLoopActive = false;

// --- 🕹️ UI Toggle Functions (Early Access) ---
window.toggleNavGuide = () => {
    const el = document.getElementById('nav-guide-tab');
    if (el) el.classList.toggle('active');
};



window.toggleMissionControl = () => {
    const el = document.getElementById('mc-wrapper');
    if (el) el.classList.toggle('active');
};

window.toggleSymmetry = () => {
    document.body.classList.toggle('symmetric-layout');
};

// --- 🔑 Authentication ---
var VAULT_KEY = "sovereign_vault_alpha_2026_secure_core";
window.VAULT_KEY = VAULT_KEY;
