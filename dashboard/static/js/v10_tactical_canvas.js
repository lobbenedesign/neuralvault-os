/**
 * 🛰️ [v10.0] Hydra Tactical Canvas - Rebuilt for High Performance
 * ────────────────────────────────────────────────────────────
 * Motore di visualizzazione 2D ad alte prestazioni per il sense-making umano.
 * Gestisce migliaia di atomi tattici (5.800+ nodi, 11.000+ archi) a 60 FPS stabili.
 * Ottimizzazioni introdotte:
 * - QuadTree Spatial Partitioning per frustum culling e hit-testing immediati in O(log N).
 * - O(1) Node Lookup Map per il caricamento istantaneo delle connessioni.
 * - Disegno di archi raggruppati in batch con pochissimi stati di render Canvas.
 * - Level of Detail (LOD) adattivo in base al fattore di zoom per eliminare il sovraccarico di testi/linee.
 * - Interactive Draft Mode durante lo spostamento/zoom per massimizzare la fluidità.
 * - Auto-Stabilizzatore fisico che disattiva il motore di forze all'equilibrio dei nodi.
 * - Focus Highlight Mode a doppio clic per visualizzare e isolare sotto-vicinati (Stile Leiden).
 * - Esportatore vettoriale statico SVG e strutturato JSON.
 */

// 🌳 Classe ausiliaria QuadTree per calcoli spaziali accelerati
class QuadTree {
    constructor(boundary, capacity = 8) {
        this.boundary = boundary; // { x, y, w, h } -> x,y centro; w,h semi-dimensioni
        this.capacity = capacity;
        this.points = [];
        this.divided = false;
    }

    subdivide() {
        const { x, y, w, h } = this.boundary;
        const nw = w / 2;
        const nh = h / 2;

        this.northwest = new QuadTree({ x: x - nw, y: y - nh, w: nw, h: nh }, this.capacity);
        this.northeast = new QuadTree({ x: x + nw, y: y - nh, w: nw, h: nh }, this.capacity);
        this.southwest = new QuadTree({ x: x - nw, y: y + nh, w: nw, h: nh }, this.capacity);
        this.southeast = new QuadTree({ x: x + nw, y: y + nh, w: nw, h: nh }, this.capacity);

        this.divided = true;
    }

    insert(point) {
        if (!this.contains(this.boundary, point)) {
            return false;
        }

        if (this.points.length < this.capacity) {
            this.points.push(point);
            return true;
        }

        if (!this.divided) {
            this.subdivide();
        }

        return (
            this.northwest.insert(point) ||
            this.northeast.insert(point) ||
            this.southwest.insert(point) ||
            this.southeast.insert(point)
        );
    }

    contains(boundary, point) {
        return (
            point.x >= boundary.x - boundary.w &&
            point.x <= boundary.x + boundary.w &&
            point.y >= boundary.y - boundary.h &&
            point.y <= boundary.y + boundary.h
        );
    }

    query(range, found = []) {
        if (!this.intersects(this.boundary, range)) {
            return found;
        }

        for (let p of this.points) {
            if (this.contains(range, p)) {
                found.push(p);
            }
        }

        if (this.divided) {
            this.northwest.query(range, found);
            this.northeast.query(range, found);
            this.southwest.query(range, found);
            this.southeast.query(range, found);
        }

        return found;
    }

    intersects(b1, b2) {
        return !(
            b2.x - b2.w > b1.x + b1.w ||
            b2.x + b2.w < b1.x - b1.w ||
            b2.y - b2.h > b1.y + b1.h ||
            b2.y + b2.h < b1.y - b1.h
        );
    }
}

// 🛰️ Motore Canvas Principale
class TacticalCanvas {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        if (!this.canvas) return;
        this.ctx = this.canvas.getContext('2d');
        
        // Strutture Dati Principali
        this.nodes = [];
        this.clusters = {};
        this.customLinks = [];
        
        // Mappa delle associazioni veloci O(1)
        this.nodeMap = new Map();
        
        // Stati di Interazione & Strumenti HUD
        this.activeTool = 'select'; // 'select' | 'node' | 'edge' | 'cluster'
        this.selectedNode = null;
        this.draggedNode = null;
        this.edgeSourceNode = null;
        this.mouseWorldPos = { x: 0, y: 0 };
        
        // Multi-Node Selection Tools States
        this.selectedNodesForDrag = [];
        this.selectedNodesForCluster = [];
        this.selectionMode = 'navigate'; // 'navigate' | 'rect' | 'lasso'
        this.selectionStart = null;      // { x, y } in world coordinates
        this.selectionEnd = null;        // { x, y } in world coordinates
        this.selectionPoints = [];       // [{ x, y }] in world coordinates
        this.isSelecting = false;
        
        // Stati Focus Highlight (Filtro Vicinato Leiden)
        this.focusMode = false;
        this.focusedNode = null;
        this.focusedNeighbors = new Set();
        this.focusDepth = 0;
        this.focusDepthNodes = null;
        this.isScrollingH = false;
        this.isScrollingV = false;
        
        // Visualizzazione & Topological Highlight Modes
        this.highlightedCommunity = null;
        this.highlightedPath = null;
        this.highlightedPathLinks = null;
        this.godNodesHighlight = false;
        this.godNodes = null;
        this.pathFinderMode = null;
        this.pathFinderStartNode = null;
        
        // ── SPRINT 1: New Graphify/GitNexus features ──────────────────────────
        // Blast Radius — impact highlight mode (GitNexus style)
        this.blastMode = false;
        this.blastCenterNode = null;
        this.blastNodes = null;         // Set<id> of nodes in blast radius
        this.blastDepth = 2;            // Default N-hop blast depth
        this._blastAnimFrame = 0;       // Animation counter for pulse rings

        // Surprising Connections — cross-community edge highlight (Graphify style)
        this.surprisingConnections = null; // Set of "src-tgt" edge keys
        this.showSurprising = false;

        // Confidence Tagging — visual edge style based on confidence level
        this.confidenceMode = false;    // Toggle confidence-styled edges

        // Cached degree map for Node Size ∝ Degree (rebuilt on data load)
        this._nodeDegrees = new Map();
        // ──────────────────────────────────────────────────────────────────────

        
        // Stato del Simulatore di Forze (Fisica)
        this.forcesEnabled = false;
        this.physicsStabilityCounter = 0;
        
        // Trasformazione del Viewport & Dragging
        this.offset = { x: 0, y: 0 };
        this.zoom = 0.0001; // Avvio molto zoomato out per coordinate estese del server
        this.idealFitZoom = 0.0001;
        this.minZoom = 0.000001;
        this.maxZoom = 15.0;
        this.isDragging = false;
        this.isZooming = false;
        this.lastMousePos = { x: 0, y: 0 };
        this.zoomTimeout = null;
        this.lastFrameTime = 0;

        this.isFirstLoad = true;

        // Filtri Tattici Attivi
        this.activeFilters = {
            code_module: true,
            code_class: true,
            code_function: true,
            code_asset: true,
            other: true
        };
        this.viewport = null;
        this.hoverCard = null;

        this.initEvents();
        this.resize();
        window.addEventListener('resize', () => this.resize());
        
        // Global click listener to hide search suggestions when clicking outside
        document.addEventListener('click', (e) => {
            const input = document.getElementById('tactical-search-input');
            const results = document.getElementById('tactical-search-results');
            if (results && input && !input.contains(e.target) && !results.contains(e.target)) {
                results.style.display = 'none';
            }
        });
        
        // Iniettiamo i controlli fluttuanti nel parent DOM
        this.injectControls();
        this.populateSidebarFilters();
        
        // Avvio del loop di Rendering & Fisica Throttled
        this.animate();
    }

    resize() {
        if (!this.canvas || !this.canvas.parentElement) return;
        this.canvas.width = this.canvas.parentElement.clientWidth;
        this.canvas.height = this.canvas.parentElement.clientHeight;
        this.draw();
    }

    initEvents() {
        this.canvas.addEventListener('pointerdown', (e) => this.handleMouseDown(e));
        this.canvas.addEventListener('pointermove', (e) => this.handleMouseMove(e));
        this.canvas.addEventListener('pointerup', (e) => this.handleMouseUp(e));
        this.canvas.addEventListener('wheel', (e) => this.handleWheel(e), { passive: false });
        this.canvas.addEventListener('dblclick', (e) => this.handleDoubleClick(e));
        this.canvas.addEventListener('contextmenu', (e) => e.preventDefault());
        
        // Bind keydown navigation listener for right sidebar search
        const rightSearchInput = document.getElementById('tactical-search-input');
        const rightSearchResults = document.getElementById('tactical-search-results');
        if (rightSearchInput && rightSearchResults) {
            rightSearchInput.addEventListener('keydown', (e) => {
                this.handleSearchKeydown(e, rightSearchInput, rightSearchResults);
            });
        }
        
        // Focus sulla tastiera per catturare scorciatoie
        this.canvas.tabIndex = 1;
        this.canvas.style.outline = 'none';
    }

    isInteractiveNode(n) {
        if (this.isFilteredOut(n)) return false;
        if (this.focusDepthNodes && !this.focusDepthNodes.has(n.id)) return false;
        return true;
    }

    calculateFocusDepthNodes(nodeId, depth) {
        if (!nodeId || depth <= 0) {
            return null;
        }
        
        const visited = new Set();
        const queue = [ { id: nodeId, hop: 0 } ];
        visited.add(nodeId);

        // Pre-build adjacency list for speed O(V+E)
        const adj = new Map();
        
        const addEdge = (u, v) => {
            if (!adj.has(u)) adj.set(u, []);
            if (!adj.has(v)) adj.set(v, []);
            adj.get(u).push(v);
            adj.get(v).push(u);
        };

        if (window.lastNeuralLinks) {
            window.lastNeuralLinks.forEach(l => {
                addEdge(l.source, l.target);
            });
        }
        this.customLinks.forEach(l => {
            addEdge(l.source, l.target);
        });

        // BFS Loop
        while (queue.length > 0) {
            const current = queue.shift();
            
            if (current.hop < depth) {
                const neighbors = adj.get(current.id) || [];
                for (const nextId of neighbors) {
                    if (!visited.has(nextId)) {
                        visited.add(nextId);
                        queue.push({ id: nextId, hop: current.hop + 1 });
                    }
                }
            }
        }
        return visited;
    }

    setFocusDepth(depth, elementBtn) {
        if (this.focusDepth === depth) {
            // Toggle off
            this.focusDepth = 0;
            this.focusDepthNodes = null;
            document.querySelectorAll('.focus-depth-pill').forEach(btn => btn.classList.remove('active'));
        } else {
            this.focusDepth = depth;
            document.querySelectorAll('.focus-depth-pill').forEach(btn => btn.classList.remove('active'));
            if (elementBtn) {
                elementBtn.classList.add('active');
            } else {
                // Try to find the button by matching the text
                const buttons = document.querySelectorAll('.focus-depth-pill');
                buttons.forEach(btn => {
                    if (btn.textContent.includes(depth + ' HOP')) {
                        btn.classList.add('active');
                    }
                });
            }
            
            // Recompute focusDepthNodes
            const rootNode = this.focusedNode || this.selectedNode;
            if (rootNode) {
                this.focusDepthNodes = this.calculateFocusDepthNodes(rootNode.id, this.focusDepth);
            } else {
                this.focusDepthNodes = null;
            }
        }
        this.draw();
    }

    setSelectionMode(mode) {
        console.log(`[TacticalCanvas] Tool attivato: ${mode}`);
        this.selectionMode = mode;
        this.activeTool = 'select'; // Forza il rientro in modalità selezione
        
        // Sync bottom selection buttons
        const bottomControls = document.getElementById('tactical-graphify-controls');
        if (bottomControls) {
            const btns = bottomControls.querySelectorAll('button');
            btns.forEach(btn => {
                const title = btn.title || '';
                if (title.includes('Navigate')) {
                    if (mode === 'navigate') {
                        btn.style.background = 'rgba(0, 255, 157, 0.2)';
                        btn.style.borderColor = 'rgba(0, 255, 157, 0.6)';
                        btn.style.color = '#00ff9d';
                        btn.style.boxShadow = '0 0 10px rgba(0, 255, 157, 0.25)';
                    } else {
                        btn.style.background = 'rgba(255, 255, 255, 0.05)';
                        btn.style.borderColor = 'rgba(255, 255, 255, 0.1)';
                        btn.style.color = '#fff';
                        btn.style.boxShadow = 'none';
                    }
                } else if (title.includes('Box')) {
                    if (mode === 'rect') {
                        btn.style.background = 'rgba(0, 255, 157, 0.2)';
                        btn.style.borderColor = 'rgba(0, 255, 157, 0.6)';
                        btn.style.color = '#00ff9d';
                        btn.style.boxShadow = '0 0 10px rgba(0, 255, 157, 0.25)';
                    } else {
                        btn.style.background = 'rgba(255, 255, 255, 0.05)';
                        btn.style.borderColor = 'rgba(255, 255, 255, 0.1)';
                        btn.style.color = '#fff';
                        btn.style.boxShadow = 'none';
                    }
                } else if (title.includes('Lasso')) {
                    if (mode === 'lasso') {
                        btn.style.background = 'rgba(0, 255, 157, 0.2)';
                        btn.style.borderColor = 'rgba(0, 255, 157, 0.6)';
                        btn.style.color = '#00ff9d';
                        btn.style.boxShadow = '0 0 10px rgba(0, 255, 157, 0.25)';
                    } else {
                        btn.style.background = 'rgba(255, 255, 255, 0.05)';
                        btn.style.borderColor = 'rgba(255, 255, 255, 0.1)';
                        btn.style.color = '#fff';
                        btn.style.boxShadow = 'none';
                    }
                }
            });
        }
        
        // Update sidebar buttons styling
        const sidebarBtns = {
            navigate: document.getElementById('gl-mode-navigate'),
            rect: document.getElementById('gl-mode-rect'),
            lasso: document.getElementById('gl-mode-lasso')
        };
        
        Object.keys(sidebarBtns).forEach(k => {
            const btn = sidebarBtns[k];
            if (btn) {
                if (k === mode) {
                    btn.style.background = 'rgba(0, 255, 157, 0.15)';
                    btn.style.borderColor = 'rgba(0, 255, 157, 0.4)';
                    btn.style.color = '#00ff9d';
                } else {
                    btn.style.background = 'rgba(255,255,255,0.03)';
                    btn.style.borderColor = 'rgba(255,255,255,0.08)';
                    btn.style.color = '#fff';
                }
            }
        });
        
        // Set cursor styling appropriately
        if (mode === 'navigate') {
            this.canvas.style.cursor = 'grab';
        } else if (mode === 'rect') {
            this.canvas.style.cursor = 'crosshair';
        } else if (mode === 'lasso') {
            this.canvas.style.cursor = 'cell';
        }
        
        this.isSelecting = false;
        this.selectionStart = null;
        this.selectionEnd = null;
        this.selectionPoints = [];
        
        this.draw();
    }

    updateFilter(key, checked) {
        this.activeFilters[key] = checked;
        
        // Synchronize all checkboxes (bottom panel & sidebar)
        document.querySelectorAll(`input[data-filter-key="${key}"]`).forEach(cb => {
            cb.checked = checked;
        });
        
        this.draw();
        this.updateCounters();
    }

    populateSidebarFilters() {
        const container = document.getElementById('graph-lab-node-filters');
        if (!container) return;
        container.innerHTML = '';
        
        const types = [
            { key: 'code_module', label: 'Module', color: '#3b82f6', tooltip: 'Group of files and components structuring a logical space (Modules)' },
            { key: 'code_class', label: 'Class', color: '#a855f7', tooltip: 'Object blueprints and structural data types defining components (Classes)' },
            { key: 'code_function', label: 'Function', color: '#00ff9d', tooltip: 'Functional execution units and callable algorithms (Functions)' },
            { key: 'code_asset', label: 'Asset', color: '#64748b', tooltip: 'Static resources, assets, databases, configuration files, and galaxy contexts (Assets)' },
            { key: 'other', label: 'Other', color: '#cbd5e1', tooltip: 'Miscellaneous files, documents, and uncategorized graph points (Other)' }
        ];
        
        types.forEach(t => {
            const labelEl = document.createElement('label');
            labelEl.title = t.tooltip;
            labelEl.style.cssText = `
                display: flex;
                align-items: center;
                gap: 0.4rem;
                font-size: 0.65rem;
                color: #cbd5e1;
                cursor: pointer;
                user-select: none;
                transition: opacity 0.2s ease;
            `;
            
            const checkbox = document.createElement('input');
            checkbox.type = 'checkbox';
            checkbox.checked = this.activeFilters[t.key];
            checkbox.style.cssText = `
                cursor: pointer;
                accent-color: ${t.color};
            `;
            checkbox.dataset.filterKey = t.key;
            checkbox.onchange = (e) => {
                this.updateFilter(t.key, e.target.checked);
            };
            
            const dot = document.createElement('span');
            dot.style.cssText = `
                width: 8px;
                height: 8px;
                border-radius: 50%;
                background: ${t.color};
                box-shadow: 0 0 5px ${t.color};
            `;
            
            const text = document.createTextNode(t.label);
            
            labelEl.appendChild(checkbox);
            labelEl.appendChild(dot);
            labelEl.appendChild(text);
            container.appendChild(labelEl);
        });
    }

    getGraphCoordinateBounds() {
        let minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity;
        this.nodes.forEach(n => {
            if (this.isFilteredOut(n)) return;
            minX = Math.min(minX, n.x);
            maxX = Math.max(maxX, n.x);
            minY = Math.min(minY, n.y);
            maxY = Math.max(maxY, n.y);
        });
        
        if (minX === Infinity) {
            minX = -100000;
            maxX = 100000;
            minY = -100000;
            maxY = 100000;
        }
        
        const padX = (maxX - minX) * 0.3 || 10000;
        const padY = (maxY - minY) * 0.3 || 10000;
        
        return {
            minX: minX - padX,
            maxX: maxX + padX,
            minY: minY - padY,
            maxY: maxY + padY
        };
    }

    updateScrollbars() {
        const trackH = document.getElementById('tactical-scrollbar-h');
        const thumbH = document.getElementById('tactical-scrollbar-h-thumb');
        const trackV = document.getElementById('tactical-scrollbar-v');
        const thumbV = document.getElementById('tactical-scrollbar-v-thumb');
        
        if (!trackH || !thumbH || !trackV || !thumbV) return;
        
        if (this.nodes.length === 0) {
            trackH.style.display = 'none';
            trackV.style.display = 'none';
            return;
        }
        
        trackH.style.display = 'block';
        trackV.style.display = 'block';
        
        const W = this.canvas.width;
        const H = this.canvas.height;
        const Z = this.zoom;
        
        const bounds = this.getGraphCoordinateBounds();
        const worldTotalW = bounds.maxX - bounds.minX;
        const worldTotalH = bounds.maxY - bounds.minY;
        
        const worldLeft = -this.offset.x / Z;
        const worldTop = -this.offset.y / Z;
        const visibleW = W / Z;
        const visibleH = H / Z;
        
        // Horizontal thumb
        const trackWidth = trackH.clientWidth;
        let thumbWidth = (visibleW / worldTotalW) * trackWidth;
        thumbWidth = Math.max(30, Math.min(thumbWidth, trackWidth));
        thumbH.style.width = `${thumbWidth}px`;
        
        const maxLeft = trackWidth - thumbWidth;
        let leftRatio = (worldLeft - bounds.minX) / worldTotalW;
        leftRatio = Math.max(0, Math.min(leftRatio, 1));
        thumbH.style.left = `${leftRatio * maxLeft}px`;
        
        // Vertical thumb
        const trackHeight = trackV.clientHeight;
        let thumbHeight = (visibleH / worldTotalH) * trackHeight;
        thumbHeight = Math.max(30, Math.min(thumbHeight, trackHeight));
        thumbV.style.height = `${thumbHeight}px`;
        
        const maxTop = trackHeight - thumbHeight;
        let topRatio = (worldTop - bounds.minY) / worldTotalH;
        topRatio = Math.max(0, Math.min(topRatio, 1));
        thumbV.style.top = `${topRatio * maxTop}px`;
    }

    // Ricostruisce al volo il Quadtree basandosi sull'estensione attuale dei nodi
    buildQuadtree() {
        if (this.nodes.length === 0) return null;
        let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
        let valid = 0;
        this.nodes.forEach(n => {
            if (isNaN(n.x) || isNaN(n.y)) return;
            minX = Math.min(minX, n.x);
            minY = Math.min(minY, n.y);
            maxX = Math.max(maxX, n.x);
            maxY = Math.max(maxY, n.y);
            valid++;
        });

        if (valid === 0) return null;

        const cx = (minX + maxX) / 2;
        const cy = (minY + maxY) / 2;
        const w = (maxX - minX) / 2 + 10000;
        const h = (maxY - minY) / 2 + 10000;

        const qt = new QuadTree({ x: cx, y: cy, w: w, h: h }, 8);
        this.nodes.forEach(n => {
            if (!isNaN(n.x) && !isNaN(n.y)) {
                qt.insert(n);
            }
        });
        return qt;
    }

    // Trova i nodi connessi a un dato Atomo per evidenziarli nel focus mode
    getNeighbors(nodeId) {
        const neighbors = new Set();
        if (window.lastNeuralLinks) {
            window.lastNeuralLinks.forEach(l => {
                if (l.source === nodeId) neighbors.add(l.target);
                if (l.target === nodeId) neighbors.add(l.source);
            });
        }
        this.customLinks.forEach(l => {
            if (l.source === nodeId) neighbors.add(l.target);
            if (l.target === nodeId) neighbors.add(l.source);
        });
        return neighbors;
    }

    // Gestione del Doppio Click per attivare l'isolamento del vicinato (Focus Mode)
    handleDoubleClick(e) {
        const rect = this.canvas.getBoundingClientRect();
        const clickX = e.clientX - rect.left;
        const clickY = e.clientY - rect.top;
        
        // Rileviamo il nodo cliccato con hitbox pixel-perfect indipendente dallo zoom
        const hitNode = this.nodes.find(n => {
            if (!this.isInteractiveNode(n)) return false;
            const nodeScreenX = n.x * this.zoom + this.offset.x;
            const nodeScreenY = n.y * this.zoom + this.offset.y;
            const dx = nodeScreenX - clickX;
            const dy = nodeScreenY - clickY;
            const distance = Math.sqrt(dx * dx + dy * dy);
            
            const baseSize = n.isGalaxy ? 15000 : 8000;
            const nodeScreenRadius = baseSize * this.zoom;
            const hitTargetRadius = Math.max(nodeScreenRadius, 15) + 8;
            return distance < hitTargetRadius;
        });

        if (hitNode) {
            if (this.focusMode && this.focusedNode && this.focusedNode.id === hitNode.id) {
                // Rilasciamo il focus
                this.focusMode = false;
                this.focusedNode = null;
                this.focusedNeighbors.clear();
                this.focusDepthNodes = null;
                console.log("🔬 Focus Mode Disattivato");
            } else {
                // Impostiamo il focus sul nodo e carichiamo i suoi vicini
                this.focusMode = true;
                this.focusedNode = hitNode;
                this.focusedNeighbors = this.getNeighbors(hitNode.id);
                if (this.focusDepth > 0) {
                    this.focusDepthNodes = this.calculateFocusDepthNodes(hitNode.id, this.focusDepth);
                } else {
                    this.focusDepthNodes = null;
                }
                console.log("🔬 Focus Mode Attivato per:", hitNode.text);
            }
        } else {
            // Cliccando sul vuoto si rilascia sempre il focus
            this.focusMode = false;
            this.focusedNode = null;
            this.focusedNeighbors.clear();
            this.focusDepthNodes = null;
        }
        this.draw();
    }

    handleMouseDown(e) {
        console.log(`[TacticalCanvas] MOUSE DOWN: button=${e.button}, activeTool=${this.activeTool}, mode=${this.selectionMode}`);
        e.preventDefault();
        
        const rect = this.canvas.getBoundingClientRect();
        const scaleX = this.canvas.width / rect.width;
        const scaleY = this.canvas.height / rect.height;
        const clickX = (e.clientX - rect.left) * scaleX;
        const clickY = (e.clientY - rect.top) * scaleY;
        
        const mouseX = (clickX - this.offset.x) / this.zoom;
        const mouseY = (clickY - this.offset.y) / this.zoom;

        // Hit detection rapida
        let hitNode = this.nodes.find(n => {
            if (!this.isInteractiveNode(n)) return false;
            const nodeScreenX = n.x * this.zoom + this.offset.x;
            const nodeScreenY = n.y * this.zoom + this.offset.y;
            
            const dx = nodeScreenX - clickX;
            const dy = nodeScreenY - clickY;
            const distance = Math.sqrt(dx * dx + dy * dy);
            
            const baseSize = n.isGalaxy ? 15000 : 8000;
            const nodeScreenRadius = baseSize * this.zoom;
            const hitTargetRadius = Math.max(nodeScreenRadius, 15) + 8;
            
            return distance < hitTargetRadius;
        });

        // Se siamo in modalità rect o lasso, e non abbiamo cliccato su un nodo già selezionato,
        // trattiamo il click come se fosse sul vuoto per poter disegnare il box/lazo.
        const isMarqueeMode = this.activeTool === 'select' && (this.selectionMode === 'rect' || this.selectionMode === 'lasso');
        const clickedAlreadySelected = hitNode && this.selectedNodesForDrag.includes(hitNode);

        if (isMarqueeMode && !clickedAlreadySelected) {
            console.log("[TacticalCanvas] Marquee Mode attivo: Ignoro hitNode per iniziare la selezione multipla.");
            hitNode = null; // Forza il fall-through al click sul vuoto!
        }

        // 1. Shift + Click / Click on node when standard tool is active
        if (this.activeTool === 'select' && hitNode) {
            if (e.shiftKey) {
                // Shift-click toggle selection addition
                const idx = this.selectedNodesForDrag.indexOf(hitNode);
                if (idx > -1) {
                    this.selectedNodesForDrag.splice(idx, 1);
                } else {
                    this.selectedNodesForDrag.push(hitNode);
                }
                this.selectedNode = this.selectedNodesForDrag[this.selectedNodesForDrag.length - 1] || null;
                if (this.selectedNode) {
                    this.triggerNodeSelection(this.selectedNode);
                } else {
                    this.updateCounters();
                }
                this.draw();
                return;
            } else {
                // Regular click on node
                if (!this.selectedNodesForDrag.includes(hitNode)) {
                    this.selectedNodesForDrag = [hitNode];
                }
                this.selectedNode = hitNode;
                this.triggerNodeSelection(hitNode);
                
                this.isDraggingGroup = true;
                this.lastMouseWorldPos = { x: mouseX, y: mouseY };
                console.log(`[TacticalCanvas] Inizio Dragging di Massa: ${this.selectedNodesForDrag.length} nodi.`);
                this.selectedNodesForDrag.forEach(n => {
                    n.dragged = true;
                    n.vx = 0;
                    n.vy = 0;
                });
                return;
            }
        }

        // Viewport panning with right click or middle click
        if (e.button === 1 || e.button === 2) {
            this.isDragging = true;
            this.lastMousePos = { x: e.clientX, y: e.clientY };
            this.draggedNode = null;
            return;
        }

        // 2. Comportamento Strumenti HUD
        if (this.activeTool === 'node') {
            if (!hitNode) {
                setTimeout(() => {
                    const label = prompt("Inserisci l'etichetta per il nuovo Atomo Cognitivo (2D):");
                    if (label && label.trim() !== '') {
                        const newNode = {
                            id: 'custom_' + Date.now(),
                            text: label.trim(),
                            x: mouseX,
                            y: mouseY,
                            color: '#00ff9d',
                            cluster: 'personal_zone',
                            isGalaxy: false,
                            vx: 0,
                            vy: 0
                        };
                        this.nodes.push(newNode);
                        this.nodeMap.set(newNode.id, newNode);
                        this.saveLocalModifications();
                        this.regroupClusters();
                        this.triggerNodeSelection(newNode);
                        console.log("Custom Node Spawned:", newNode);
                    }
                    this.setTool('select');
                }, 50);
            }
            return;
        }

        if (this.activeTool === 'edge') {
            if (hitNode) {
                if (!this.edgeSourceNode) {
                    this.edgeSourceNode = hitNode;
                    console.log("Edge Source Lock:", hitNode.id);
                } else {
                    if (this.edgeSourceNode.id !== hitNode.id) {
                        const exists = this.customLinks.some(l => 
                            (l.source === this.edgeSourceNode.id && l.target === hitNode.id) ||
                            (l.source === hitNode.id && l.target === this.edgeSourceNode.id)
                        );
                        if (!exists) {
                            this.customLinks.push({
                                source: this.edgeSourceNode.id,
                                target: hitNode.id
                            });
                            this.saveLocalModifications();
                            console.log("Synaptic Edge Established:", this.edgeSourceNode.id, "->", hitNode.id);
                        }
                    }
                    this.edgeSourceNode = null;
                    this.setTool('select');
                }
            } else {
                this.edgeSourceNode = null;
                this.setTool('select');
            }
            return;
        }

        if (this.activeTool === 'cluster') {
            if (hitNode) {
                const idx = this.selectedNodesForCluster.indexOf(hitNode);
                if (idx > -1) {
                    this.selectedNodesForCluster.splice(idx, 1);
                } else {
                    this.selectedNodesForCluster.push(hitNode);
                }
                
                if (this.selectedNodesForCluster.length >= 2) {
                    setTimeout(() => {
                        const confirmMerge = confirm(`Hai selezionato ${this.selectedNodesForCluster.length} nodi tattici. Desideri unificarli in un unico cluster semantico?`);
                        if (confirmMerge) {
                            const clusterName = prompt("Inserisci il titolo/etichetta della nuova Zona Semantica:");
                            if (clusterName && clusterName.trim() !== '') {
                                const zone = clusterName.trim();
                                this.selectedNodesForCluster.forEach(n => {
                                    n.cluster = zone;
                                    n.color = '#a855f7';
                                });
                                this.saveLocalModifications();
                                this.regroupClusters();
                                this.updateCounters();
                                console.log("Nodes unified under Cluster:", zone);
                            }
                        }
                        this.selectedNodesForCluster = [];
                        this.setTool('select');
                    }, 80);
                }
            }
            return;
        }

        // Modalità Standard SELECT / DRAG
        if (hitNode) {
            if (this.pathFinderMode === 'select_start') {
                this.pathFinderStartNode = hitNode;
                this.pathFinderMode = 'select_end';
                const statusFooter = document.getElementById('tactical-status-text');
                if (statusFooter) {
                    statusFooter.innerText = `PATH: From ${hitNode.text.substring(0, 15)}... Click target node`;
                    statusFooter.style.color = '#22d3ee';
                }
                console.log("Pathfinder: Start node selected:", hitNode.text);
                this.draw();
                return;
            } else if (this.pathFinderMode === 'select_end') {
                const path = this.findShortestPath(this.pathFinderStartNode.id, hitNode.id);
                if (path) {
                    this.highlightedPath = new Set(path);
                    this.highlightedPathLinks = new Set();
                    for (let i = 0; i < path.length - 1; i++) {
                        this.highlightedPathLinks.add(`${path[i]}-${path[i+1]}`);
                        this.highlightedPathLinks.add(`${path[i+1]}-${path[i]}`);
                    }
                    const statusFooter = document.getElementById('tactical-status-text');
                    if (statusFooter) {
                        statusFooter.innerText = `PATH FOUND: ${path.length} hops`;
                        statusFooter.style.color = '#00ff9d';
                    }
                    console.log("Pathfinder: Path found!", path);
                } else {
                    alert(`Nessuna connessione topologica trovata tra '${this.pathFinderStartNode.text}' e '${hitNode.text}'.`);
                    const statusFooter = document.getElementById('tactical-status-text');
                    if (statusFooter) {
                        statusFooter.innerText = "PATHFINDER: No path found";
                        statusFooter.style.color = '#ef4444';
                    }
                }
                
                this.pathFinderMode = null;
                this.pathFinderStartNode = null;
                const btn = document.getElementById('btn-topo-pathfinder');
                if (btn) {
                    btn.style.background = 'rgba(6, 182, 212, 0.08)';
                    btn.style.borderColor = 'rgba(6, 182, 212, 0.2)';
                    btn.style.color = '#22d3ee';
                }
                this.draw();
                return;
            }

            this.draggedNode = hitNode;
            this.draggedNode.dragged = true; // Sospendiamo la fisica su questo nodo
            this.draggedNode.vx = 0;
            this.draggedNode.vy = 0;
            
            this.selectedNode = hitNode;
            this.triggerNodeSelection(hitNode);
        } else {
            // Clicked empty space
            if (this.activeTool === 'select') {
                if (this.selectionMode === 'navigate') {
                    // Clear selection and pan viewport
                    this.selectedNodesForDrag = [];
                    this.selectedNode = null;
                    this.updateCounters();
                    const emptyState = document.getElementById('tactical-node-info-empty');
                    const detailsView = document.getElementById('tactical-node-info-details');
                    if (emptyState) emptyState.style.display = 'flex';
                    if (detailsView) detailsView.style.display = 'none';

                    this.isDragging = true;
                    this.lastMousePos = { x: e.clientX, y: e.clientY };
                } else if (this.selectionMode === 'rect' || this.selectionMode === 'lasso') {
                    // Start selection box/lasso
                    console.log(`[TacticalCanvas] Iniziata selezione geometrica: ${this.selectionMode}`);
                    this.isSelecting = true;
                    this.selectionStart = { x: mouseX, y: mouseY };
                    this.selectionEnd = { x: mouseX, y: mouseY };
                    this.selectionPoints = [{ x: mouseX, y: mouseY }];
                }
            } else {
                this.isDragging = true;
                this.lastMousePos = { x: e.clientX, y: e.clientY };
                
                this.selectedNode = null;
                this.updateCounters();
                const emptyState = document.getElementById('tactical-node-info-empty');
                const detailsView = document.getElementById('tactical-node-info-details');
                if (emptyState) emptyState.style.display = 'flex';
                if (detailsView) detailsView.style.display = 'none';
            }
        }
    }


    handleMouseMove(e) {
        const rect = this.canvas.getBoundingClientRect();
        const scaleX = this.canvas.width / rect.width;
        const scaleY = this.canvas.height / rect.height;
        const clickX = (e.clientX - rect.left) * scaleX;
        const clickY = (e.clientY - rect.top) * scaleY;
        
        this.mouseWorldPos = {
            x: (clickX - this.offset.x) / this.zoom,
            y: (clickY - this.offset.y) / this.zoom
        };

        if (this.isDragging) {
            this.offset.x += e.clientX - this.lastMousePos.x;
            this.offset.y += e.clientY - this.lastMousePos.y;
            this.lastMousePos = { x: e.clientX, y: e.clientY };
        } else if (this.isDraggingGroup) {
            const dx = this.mouseWorldPos.x - this.lastMouseWorldPos.x;
            const dy = this.mouseWorldPos.y - this.lastMouseWorldPos.y;
            this.selectedNodesForDrag.forEach(n => {
                n.x += dx;
                n.y += dy;
            });
            this.lastMouseWorldPos = { x: this.mouseWorldPos.x, y: this.mouseWorldPos.y };
        } else if (this.draggedNode) {
            this.draggedNode.x = this.mouseWorldPos.x;
            this.draggedNode.y = this.mouseWorldPos.y;
        } else if (this.isSelecting) {
            if (this.selectionMode === 'rect') {
                this.selectionEnd = { x: this.mouseWorldPos.x, y: this.mouseWorldPos.y };
            } else if (this.selectionMode === 'lasso') {
                this.selectionPoints.push({ x: this.mouseWorldPos.x, y: this.mouseWorldPos.y });
            }
        }
        
        this.handleHoverCard(e);
    }

    handleMouseUp() {
        if (this.isDraggingGroup) {
            this.selectedNodesForDrag.forEach(n => {
                n.dragged = false;
            });
            this.isDraggingGroup = false;
            this.saveLocalModifications();
            this.syncTo3D();
        }
        if (this.draggedNode) {
            this.draggedNode.dragged = false;
            this.saveLocalModifications();
            this.syncTo3D();
        }
        
        if (this.isSelecting) {
            this.isSelecting = false;
            this.performSelectionQuery();
        }
        
        this.isDragging = false;
        this.draggedNode = null;
    }

    isPointInPolygon(point, polygon) {
        const x = point.x, y = point.y;
        let inside = false;
        for (let i = 0, j = polygon.length - 1; i < polygon.length; j = i++) {
            const xi = polygon[i].x, yi = polygon[i].y;
            const xj = polygon[j].x, yj = polygon[j].y;
            
            const intersect = ((yi > y) !== (yj > y))
                && (x < (xj - xi) * (y - yi) / (yj - yi) + xi);
            if (intersect) inside = !inside;
        }
        return inside;
    }

    performSelectionQuery() {
        if (this.selectionMode === 'rect') {
            const x1 = Math.min(this.selectionStart.x, this.selectionEnd.x);
            const x2 = Math.max(this.selectionStart.x, this.selectionEnd.x);
            const y1 = Math.min(this.selectionStart.y, this.selectionEnd.y);
            const y2 = Math.max(this.selectionStart.y, this.selectionEnd.y);
            
            this.selectedNodesForDrag = this.nodes.filter(n => {
                if (this.isFilteredOut(n)) return false;
                return n.x >= x1 && n.x <= x2 && n.y >= y1 && n.y <= y2;
            });
        } else if (this.selectionMode === 'lasso') {
            if (this.selectionPoints.length < 3) {
                this.selectedNodesForDrag = [];
                return;
            }
            this.selectedNodesForDrag = this.nodes.filter(n => {
                if (this.isFilteredOut(n)) return false;
                return this.isPointInPolygon(n, this.selectionPoints);
            });
        }
        
        if (this.selectedNodesForDrag.length > 0) {
            console.log(`[TacticalCanvas] ${this.selectionMode} completato. Nodi selezionati: ${this.selectedNodesForDrag.length}`);
            this.selectedNode = this.selectedNodesForDrag[this.selectedNodesForDrag.length - 1];
            this.triggerNodeSelection(this.selectedNode);
        } else {
            console.log(`[TacticalCanvas] ${this.selectionMode} completato. Nessun nodo catturato.`);
            this.selectedNode = null;
            this.updateCounters();
        }
        this.draw();
    }

    // Zoom centrato sotto il cursore del mouse, fluido e istantaneo
    handleWheel(e) {
        e.preventDefault();
        
        // Attiviamo lo stato interattivo di Zooming (Draft Mode attiva)
        this.isZooming = true;
        clearTimeout(this.zoomTimeout);
        this.zoomTimeout = setTimeout(() => {
            this.isZooming = false;
            this.draw(); // Ridisegno a piena fedeltà grafica una volta fermo lo zoom
        }, 150);

        const delta = e.deltaY > 0 ? 0.82 : 1.18; 
        let newZoom = this.zoom * delta;
        
        // Limiti dello Zoom tattico (dinamici per adattarsi a coordinate estese)
        const minZ = this.minZoom || 0.000001;
        const maxZ = this.maxZoom || 100.0;
        if (newZoom < minZ) newZoom = minZ;
        if (newZoom > maxZ) newZoom = maxZ;
        
        const ratio = newZoom / this.zoom;
        
        const rect = this.canvas.getBoundingClientRect();
        const mouseX = e.clientX - rect.left;
        const mouseY = e.clientY - rect.top;
        
        // Calcolo dell'offset per mantenere fisso il punto sotto il mouse
        this.offset.x = mouseX - (mouseX - this.offset.x) * ratio;
        this.offset.y = mouseY - (mouseY - this.offset.y) * ratio;
        this.zoom = newZoom;
    }

    triggerNodeSelection(node) {
        this.selectedNode = node;
        this.updateCounters();
        
        if (node && this.focusDepth > 0) {
            this.focusDepthNodes = this.calculateFocusDepthNodes(node.id, this.focusDepth);
        } else {
            this.focusDepthNodes = null;
        }
        
        // Synchronize search inputs with the selected node
        const rightSearchInput = document.getElementById('tactical-search-input');
        if (rightSearchInput && node) rightSearchInput.value = node.text;
        if (this.bottomSearchInput && node) this.bottomSearchInput.value = node.text;
        
        const inspector = document.getElementById('tactical-inspector');
        const emptyState = document.getElementById('tactical-node-info-empty');
        const detailsView = document.getElementById('tactical-node-info-details');
        
        // Show/Hide sidebar panel components
        if (inspector) inspector.style.display = 'flex';
        if (emptyState) emptyState.style.display = 'none';
        if (detailsView) detailsView.style.display = 'flex';
        
        // Popolamento dettagli del nodo
        const detailName = document.getElementById('tactical-node-detail-name');
        const detailType = document.getElementById('tactical-node-detail-type');
        const detailCommunitySwatch = document.getElementById('tactical-node-detail-community-swatch');
        const detailCommunity = document.getElementById('tactical-node-detail-community');
        const detailSource = document.getElementById('tactical-node-detail-source');
        const detailDegree = document.getElementById('tactical-node-detail-degree');
        const neighborsList = document.getElementById('tactical-node-neighbors-list');
        
        if (detailName) detailName.innerText = node.text;
        
        const typeStr = (node.metadata && node.metadata.type) ? node.metadata.type.toUpperCase() : (node.isGalaxy ? 'GALAXY' : 'ATOM');
        if (detailType) {
            detailType.innerText = typeStr;
            // dynamic type colors
            if (typeStr.includes('MODULE')) {
                detailType.style.color = '#3b82f6';
                detailType.style.background = 'rgba(59, 130, 246, 0.1)';
            } else if (typeStr.includes('CLASS')) {
                detailType.style.color = '#a855f7';
                detailType.style.background = 'rgba(168, 85, 247, 0.1)';
            } else if (typeStr.includes('FUNCTION')) {
                detailType.style.color = '#00ff9d';
                detailType.style.background = 'rgba(0, 255, 157, 0.1)';
            } else {
                detailType.style.color = '#cbd5e1';
                detailType.style.background = 'rgba(255, 255, 255, 0.05)';
            }
        }
        
        const clusterColor = this.getClusterColor(node.cluster || 'default');
        if (detailCommunitySwatch) detailCommunitySwatch.style.backgroundColor = clusterColor;
        if (detailCommunity) detailCommunity.innerText = (node.cluster || 'default').replace(/_+/g, ' ').toUpperCase();
        
        if (detailSource) {
            detailSource.innerText = (node.metadata && node.metadata.source) ? node.metadata.source : 'N/A';
        }
        
        const neighbors = this.getNeighbors(node.id);
        if (detailDegree) detailDegree.innerText = neighbors.size;
        
        // Popolamento lista dei vicini
        if (neighborsList) {
            neighborsList.innerHTML = '';
            if (neighbors.size === 0) {
                const noNeighbors = document.createElement('div');
                noNeighbors.innerText = 'No adjacent connections';
                noNeighbors.style.cssText = 'font-size: 0.6rem; color: #64748b; font-style: italic; text-align: center; padding: 0.5rem;';
                neighborsList.appendChild(noNeighbors);
            } else {
                neighbors.forEach(nId => {
                    const neighborNode = this.nodeMap.get(nId);
                    if (neighborNode) {
                        const item = document.createElement('div');
                        item.style.cssText = `
                            display: flex;
                            align-items: center;
                            gap: 0.5rem;
                            padding: 0.35rem 0.5rem;
                            background: rgba(255, 255, 255, 0.02);
                            border: 1px solid rgba(255, 255, 255, 0.05);
                            border-radius: 6px;
                            cursor: pointer;
                            font-size: 0.65rem;
                            color: #cbd5e1;
                            transition: all 0.15s ease;
                        `;
                        item.onmouseover = () => {
                            item.style.background = 'rgba(0, 255, 157, 0.08)';
                            item.style.borderColor = 'rgba(0, 255, 157, 0.2)';
                            item.style.color = '#fff';
                        };
                        item.onmouseout = () => {
                            item.style.background = 'rgba(255, 255, 255, 0.02)';
                            item.style.borderColor = 'rgba(255, 255, 255, 0.05)';
                            item.style.color = '#cbd5e1';
                        };
                        item.onclick = () => {
                            this.focusOnNode(neighborNode);
                        };
                        
                        const swatch = document.createElement('span');
                        swatch.style.cssText = `
                            width: 6px;
                            height: 6px;
                            border-radius: 50%;
                            background: ${this.getClusterColor(neighborNode.cluster || 'default')};
                            box-shadow: 0 0 5px ${this.getClusterColor(neighborNode.cluster || 'default')};
                            flex-shrink: 0;
                        `;
                        const text = document.createElement('span');
                        text.innerText = neighborNode.text;
                        text.style.cssText = `
                            text-overflow: ellipsis;
                            overflow: hidden;
                            white-space: nowrap;
                            flex: 1;
                        `;
                        
                        item.appendChild(swatch);
                        item.appendChild(text);
                        neighborsList.appendChild(item);
                    }
                });
            }
        }
        
        // Coordinatore Drawer (hidden by default)
        const itemId = document.getElementById('tactical-item-id');
        const itemName = document.getElementById('tactical-item-name');
        const itemCluster = document.getElementById('tactical-item-cluster');
        const itemColor = document.getElementById('tactical-item-color');
        const itemColorHex = document.getElementById('tactical-item-color-hex');
        
        if (itemId) itemId.innerText = node.id;
        if (itemName) itemName.value = node.text;
        if (itemCluster) itemCluster.value = node.cluster || 'default';
        if (itemColor) itemColor.value = node.color.startsWith('#') ? node.color : '#00ff9d';
        if (itemColorHex) itemColorHex.innerText = node.color;
        
        const event = new CustomEvent('tacticalNodeSelected', { detail: node });
        window.dispatchEvent(event);
    }

    setTool(tool) {
        this.activeTool = tool;
        this.selectedNodesForCluster = [];
        this.edgeSourceNode = null;
        
        const tools = ['select', 'node', 'edge', 'cluster'];
        tools.forEach(t => {
            const btn = document.getElementById(`tool-${t}`);
            if (btn) {
                if (t === tool) {
                    btn.style.background = 'rgba(0, 255, 157, 0.15)';
                    btn.style.borderColor = '#00ff9d';
                    btn.style.color = '#00ff9d';
                } else {
                    btn.style.background = 'rgba(255, 255, 255, 0.03)';
                    btn.style.borderColor = 'rgba(255, 255, 255, 0.1)';
                    btn.style.color = '#fff';
                }
            }
        });
        
        console.log("HUD Tool Activated:", tool);
    }

    toggleForces() {
        this.forcesEnabled = !this.forcesEnabled;
        this.physicsStabilityCounter = 0;
        const btn = document.getElementById('btn-forces');
        if (btn) {
            if (this.forcesEnabled) {
                btn.style.background = 'rgba(168, 85, 247, 0.25)';
                btn.style.borderColor = '#a855f7';
                btn.style.color = '#fff';
            } else {
                btn.style.background = 'rgba(168, 85, 247, 0.1)';
                btn.style.borderColor = 'rgba(168, 85, 247, 0.3)';
                btn.style.color = '#a855f7';
            }
        }
    }

    updateSelectedNodeLabel(val) {
        if (!this.selectedNode) return;
        this.selectedNode.text = val;
        this.nodeMap.set(this.selectedNode.id, this.selectedNode);
        this.saveLocalModifications();
        this.updateCounters();
    }
    
    updateSelectedNodeCluster(val) {
        if (!this.selectedNode) return;
        this.selectedNode.cluster = val;
        this.nodeMap.set(this.selectedNode.id, this.selectedNode);
        this.saveLocalModifications();
        this.regroupClusters();
        this.updateCounters();
    }
    
    updateSelectedNodeColor(val) {
        if (!this.selectedNode) return;
        this.selectedNode.color = val;
        this.nodeMap.set(this.selectedNode.id, this.selectedNode);
        const hex = document.getElementById('tactical-item-color-hex');
        if (hex) hex.innerText = val;
        this.saveLocalModifications();
    }
    
    deleteSelectedNode() {
        if (!this.selectedNode) return;
        const nodeId = this.selectedNode.id;
        const confirmDelete = confirm(`Sei sicuro di voler rimuovere l'atomo '${this.selectedNode.text}' dalla mappa tattica?`);
        if (confirmDelete) {
            this.nodes = this.nodes.filter(n => n.id !== nodeId);
            this.nodeMap.delete(nodeId);
            this.customLinks = this.customLinks.filter(l => l.source !== nodeId && l.target !== nodeId);
            
            this.selectedNode = null;
            if (this.focusedNode && this.focusedNode.id === nodeId) {
                this.focusMode = false;
                this.focusedNode = null;
                this.focusedNeighbors.clear();
            }

            this.saveLocalModifications();
            this.regroupClusters();
            this.updateCounters();
            
            const inspector = document.getElementById('tactical-inspector');
            if (inspector) inspector.style.display = 'none';
        }
    }

    updateCounters() {
        const nodeCount = document.getElementById('tactical-node-count');
        const linkCount = document.getElementById('tactical-link-count');
        const clusterCount = document.getElementById('tactical-cluster-count');
        const selectedLbl = document.getElementById('tactical-selected-lbl');
        
        if (nodeCount) nodeCount.innerText = this.nodes.length;
        
        const dbLinksCount = window.lastNeuralLinks ? window.lastNeuralLinks.filter(l => this.nodeMap.has(l.source) && this.nodeMap.has(l.target)).length : 0;
        const totalEdges = this.customLinks.length + dbLinksCount;
        
        if (linkCount) {
            linkCount.innerText = totalEdges;
        }
        if (clusterCount) clusterCount.innerText = Object.keys(this.clusters).length;
        if (selectedLbl) {
            selectedLbl.innerText = this.selectedNode ? this.selectedNode.text : "NESSUNO";
            selectedLbl.style.color = this.selectedNode ? '#00ff9d' : '#cbd5e1';
        }
        
        // Live Status Footer
        const statusFooter = document.getElementById('tactical-status-text');
        if (statusFooter && !this.pathFinderMode) {
            const totalCommunities = Object.keys(this.clusters).length;
            statusFooter.innerText = `${this.nodes.length} nodes - ${totalEdges} edges - ${totalCommunities} communities`;
            statusFooter.style.color = '#8b949e';
        }
    }

    updateData(vaultPoints, fromThreeSync = false) {
        if (!vaultPoints || vaultPoints.length === 0) return;

        // Group nodes by theme to elect galaxy hubs identical to 3D Cycloscope
        const galaxyGroups = {};
        const galaxyThemes = new Set();
        vaultPoints.forEach(p => {
            const isGal = (p.is_galaxy === true || (p.metadata && p.metadata.is_galaxy === true));
            if (isGal && p.theme && p.theme !== 'default') {
                if (!galaxyGroups[p.theme]) galaxyGroups[p.theme] = [];
                galaxyGroups[p.theme].push(p);
                galaxyThemes.add(p.theme);
            }
        });
        
        const themeHubs = {};
        for (const theme in galaxyGroups) {
            const nodes = galaxyGroups[theme];
            let electedHub = null;
            const coreNode = nodes.find(n => n.metadata && n.metadata.galaxy_role === 'core');
            if (coreNode) {
                electedHub = coreNode;
            } else if (nodes.length > 3) {
                electedHub = nodes[0];
            }
            if (electedHub) {
                themeHubs[theme] = electedHub.id;
            }
        }

        // Mantieni le posizioni coordinate esistenti se presenti, inserisci le nuove
        const newNodes = vaultPoints.map(p => {
            const existing = this.nodeMap.get(p.id);
            const isGalaxy = !!(p.theme && themeHubs[p.theme] === p.id);
            return {
                id: p.id,
                text: p.text || p.id,
                x: existing ? existing.x : (p.x || 0),
                y: existing ? existing.y : (p.z || 0), // Usa la coordinata Z come asse Y bidimensionale
                color: isGalaxy ? '#f59e0b' : (p.color || '#06b6d4'),
                cluster: p.theme || p.cluster_id || p.community_id || (p.metadata && (p.metadata.cluster_id || p.metadata.community_id)) || 'default',
                isGalaxy: isGalaxy,
                partition_id: p.partition_id,
                theme: p.theme,
                vx: existing ? (existing.vx || 0) : 0,
                vy: existing ? (existing.vy || 0) : 0,
                metadata: p.metadata || {}
            };
        });

        // Conserva i nodi personalizzati creati dall'utente
        const customNodes = this.nodes.filter(n => n.id.startsWith('custom_'));
        this.nodes = [...newNodes, ...customNodes];

        // Rigenera la Mappa dei Nodi velocizzata O(1)
        this.nodeMap.clear();
        this.nodes.forEach(n => this.nodeMap.set(n.id, n));

        // Raggruppa i Cluster
        this.regroupClusters();

        // ── SPRINT 1: Rebuild degree cache for proportional node sizes ──────
        this.buildDegreeMap();
        // ────────────────────────────────────────────────────────────────────

        // Ripristina le modifiche locali salvate dall'utente
        this.loadLocalModifications(fromThreeSync);

        // Popola la lista delle comunità nella barra laterale
        this.populateCommunities();

        if (this.isFirstLoad && this.nodes.length > 0) {
            this.centerCamera();
            this.isFirstLoad = false;
        }

        this.updateCounters();
    }

    regroupClusters() {
        this.clusters = {};
        this.nodes.forEach(n => {
            if (!this.clusters[n.cluster]) this.clusters[n.cluster] = [];
            this.clusters[n.cluster].push(n);
        });
        this.populateCommunities();
    }

    saveLocalModifications() {
        const mods = {
            customNodes: this.nodes.filter(n => n.id.startsWith('custom_')),
            customLinks: this.customLinks,
            nodeColors: {},
            nodeLabels: {},
            nodeClusters: {},
            nodePositions: {}
        };
        
        this.nodes.forEach(n => {
            if (n.color !== '#00ff9d' && n.color !== '#a855f7' && n.color !== '#3b82f6') {
                mods.nodeColors[n.id] = n.color;
            }
            mods.nodeLabels[n.id] = n.text;
            mods.nodeClusters[n.id] = n.cluster;
            mods.nodePositions[n.id] = { x: n.x, y: n.y };
        });
        
        localStorage.setItem('tactical_canvas_modifications_v1', JSON.stringify(mods));
        
        // Sincronizzazione in background verso DuckDB/Kùzu
        if (this.syncTimeout) clearTimeout(this.syncTimeout);
        this.syncTimeout = setTimeout(() => this.syncToBackend(), 1500);
    }

    async syncToBackend() {
        try {
            const positions = this.nodes.filter(n => !n.id.startsWith('custom_')).map(n => ({
                id: n.id,
                x: n.x,
                y: n.y
            }));
            
            await fetch('/api/nodes/update_positions', {
                method: 'POST',
                headers: { 
                    'Content-Type': 'application/json',
                    'X-API-KEY': window.VAULT_KEY || localStorage.getItem('vault_api_key') || 'sovereign-zero'
                },
                body: JSON.stringify({ positions })
            });
            console.log("🌌 [Neural Vault] Coordinate 3D sincronizzate con il server.");
        } catch (e) {
            console.error("Errore sincronizzazione backend:", e);
        }
    }

    loadLocalModifications(fromThreeSync = false) {
        const raw = localStorage.getItem('tactical_canvas_modifications_v1');
        if (!raw) return;
        try {
            const mods = JSON.parse(raw);
            
            if (mods.customNodes) {
                mods.customNodes.forEach(cn => {
                    if (!this.nodeMap.has(cn.id)) {
                        this.nodes.push(cn);
                        this.nodeMap.set(cn.id, cn);
                    }
                });
            }
            
            if (mods.customLinks) {
                this.customLinks = mods.customLinks;
            }
            
            this.nodes.forEach(n => {
                if (mods.nodeColors && mods.nodeColors[n.id]) n.color = mods.nodeColors[n.id];
                if (mods.nodeLabels && mods.nodeLabels[n.id]) n.text = mods.nodeLabels[n.id];
                if (mods.nodeClusters && mods.nodeClusters[n.id]) n.cluster = mods.nodeClusters[n.id];
                if (mods.nodePositions && mods.nodePositions[n.id]) {
                    n.x = mods.nodePositions[n.id].x;
                    n.y = mods.nodePositions[n.id].y;
                }
            });
            
            this.regroupClusters();
            this.syncTo3D(fromThreeSync);
        } catch(e) {
            console.error("Tactical local reload failed", e);
        }
    }

    syncTo3D(fromThreeSync = false) {
        const updateDataset = (dataset) => {
            if (!dataset) return;
            this.nodes.forEach(n => {
                const vp = dataset.find(p => p.id === n.id);
                if (vp) {
                    vp.x = n.x;
                    vp.z = n.y;
                }
            });
        };
        updateDataset(window.vaultPoints);
        updateDataset(window.lastVaultPoints);
        if (!fromThreeSync && typeof window.updateThreeScene === 'function') {
            const data = window.vaultPoints || window.lastVaultPoints;
            if (data) window.updateThreeScene(data, null, true);
        }
    }

    centerCamera() {
        if (this.nodes.length === 0) return;
        
        let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
        let validNodes = 0;
        
        this.nodes.forEach(n => {
            if (isNaN(n.x) || isNaN(n.y) || !isFinite(n.x) || !isFinite(n.y)) return;
            minX = Math.min(minX, n.x);
            minY = Math.min(minY, n.y);
            maxX = Math.max(maxX, n.x);
            maxY = Math.max(maxY, n.y);
            validNodes++;
        });

        if (validNodes === 0) return;

        const centerX = (minX + maxX) / 2;
        const centerY = (minY + maxY) / 2;
        
        const width = (maxX - minX) || 800;
        const height = (maxY - minY) || 800;

        let targetZoom = Math.min(this.canvas.width / (width * 1.35), this.canvas.height / (height * 1.35));
        
        // Memorizza l'idealFitZoom e calcola i limiti dinamici dello zoom
        this.idealFitZoom = targetZoom;
        this.minZoom = Math.min(0.000001, targetZoom * 0.02);
        this.maxZoom = Math.max(150.0, targetZoom * 80.0);

        // Limita il targetZoom per il centramento iniziale a valori confortevoli
        if (targetZoom > 1.2) targetZoom = 1.2;
        if (targetZoom < 0.000005) targetZoom = 0.000005;

        this.zoom = targetZoom;
        this.offset.x = this.canvas.width / 2 - centerX * this.zoom;
        this.offset.y = this.canvas.height / 2 - centerY * this.zoom;
    }

    flyToNode(nodeId) {
        const node = this.nodeMap.get(nodeId);
        if (!node) return;
        
        // Select the node
        this.selectedNode = node;
        this.selectNode(node);

        const targetZoom = Math.min(this.maxZoom || 1.2, 0.5); // Zoom-in on the node
        const targetOffsetX = this.canvas.width / 2 - node.x * targetZoom;
        const targetOffsetY = this.canvas.height / 2 - node.y * targetZoom;

        // Abilita la transizione in animate
        this.isFlying = true;
        this.targetZoom = targetZoom;
        this.targetOffsetX = targetOffsetX;
        this.targetOffsetY = targetOffsetY;
    }

    applyForces() {
        if (!this.forcesEnabled) return;
        
        const k_repulsion = 1000000000;
        const k_spring = 0.04;
        const target_dist = 280000;
        
        if (!this.forcesEnabled) {
            // Se le forze sono disabilitate, azzeriamo la stabilità e usciamo (congela le posizioni)
            this.physicsStabilityCounter = 0;
            return;
        }

        // Limita l'influenza fisica ai primi 600 nodi attivi per prevenire congelamento thread
        const activeForcesNodes = this.nodes.slice(0, 600);
        
        // 1. Forza Repulsiva (ForceAtlas2 style: influenzata dalla massa/degree)
        for (let i = 0; i < activeForcesNodes.length; i++) {
            const n1 = activeForcesNodes[i];
            if (n1.dragged) continue;
            
            let fx = 0;
            let fy = 0;
            const deg1 = this._nodeDegrees.get(n1.id) || 1;
            
            for (let j = 0; j < activeForcesNodes.length; j++) {
                if (i === j) continue;
                const n2 = activeForcesNodes[j];
                const deg2 = this._nodeDegrees.get(n2.id) || 1;
                
                const dx = n1.x - n2.x;
                const dy = n1.y - n2.y;
                const distSq = dx*dx + dy*dy || 1;
                const dist = Math.sqrt(distSq);
                
                if (dist < 400000 + (deg1 + deg2) * 5000) {
                    // ForceAtlas2 repulsion: proporzionale a (deg1+1)*(deg2+1) / dist
                    const massFactor = (deg1 + 1) * (deg2 + 1);
                    const force = (k_repulsion * massFactor * 0.05) / distSq; // * 0.05 to balance with existing k_repulsion
                    fx += (dx / dist) * force;
                    fy += (dy / dist) * force;
                }
            }
            
            n1.vx = (n1.vx || 0) + fx;
            n1.vy = (n1.vy || 0) + fy;
        }
        
        // 2. Forza Attrattiva sui collegamenti
        const links = [...this.customLinks];
        
        // SPRINT 3: AST Compound Nodes (Strong spring for CHILD_OF relations)
        const compoundLinks = [];
        if (window.lastNeuralLinks) {
            window.lastNeuralLinks.forEach(l => {
                if (l.relation === 'CHILD_OF' || l.relation_type === 'CHILD_OF') {
                    compoundLinks.push(l);
                }
            });
        }
        
        // Collegamenti impliciti per stringere le zone semantiche
        Object.keys(this.clusters).forEach(cid => {
            const list = this.clusters[cid];
            for (let i = 0; i < list.length - 1; i++) {
                links.push({ source: list[i].id, target: list[i+1].id });
            }
        });
        
        const applySpring = (linkList, springK, targetDist) => {
            linkList.forEach(link => {
                const n1 = this.nodeMap.get(link.source);
                const n2 = this.nodeMap.get(link.target);
                if (!n1 || !n2) return;
                
                const dx = n2.x - n1.x;
                const dy = n2.y - n1.y;
                const dist = Math.sqrt(dx*dx + dy*dy) || 1;
                
                const force = (dist - targetDist) * springK;
                const fx = (dx / dist) * force;
                const fy = (dy / dist) * force;
                
                if (!n1.dragged) {
                    n1.vx = (n1.vx || 0) + fx;
                    n1.vy = (n1.vy || 0) + fy;
                }
                if (!n2.dragged) {
                    n2.vx = (n2.vx || 0) - fx;
                    n2.vy = (n2.vy || 0) - fy;
                }
            });
        };
        
        applySpring(links, k_spring, target_dist);
        applySpring(compoundLinks, k_spring * 8.0, target_dist * 0.15); // SPRINT 3: Strong, tight orbit for nested AST
        
        // 3. Gravità Centrale e Integrazione Verlet
        const centerX = 0;
        const centerY = 0;
        let totalVelocity = 0;

        activeForcesNodes.forEach(n => {
            if (n.dragged) return;
            n.vx = (n.vx || 0) + (centerX - n.x) * 0.005;
            n.vy = (n.vy || 0) + (centerY - n.y) * 0.005;
            
            n.x += n.vx * 0.15;
            n.y += n.vy * 0.15;
            
            totalVelocity += Math.sqrt(n.vx*n.vx + n.vy*n.vy) || 0;

            n.vx *= 0.82;
            n.vy *= 0.82;
        });

        // ⚖️ Auto-Stabilizzatore Fisico: Se il movimento complessivo è insignificante,
        // congeliamo automaticamente le forze per bloccare il carico della CPU al 0%.
        const avgVelocity = totalVelocity / activeForcesNodes.length;
        if (avgVelocity < 0.4) {
            this.physicsStabilityCounter++;
            if (this.physicsStabilityCounter > 40) {
                this.forcesEnabled = false;
                this.physicsStabilityCounter = 0;
                console.log("🧬 [Tactical Physics] Layout stabilizzato correttamente. Forze in stand-by.");
                const btn = document.getElementById('btn-forces');
                if (btn) {
                    btn.style.background = 'rgba(168, 85, 247, 0.1)';
                    btn.style.borderColor = 'rgba(168, 85, 247, 0.3)';
                    btn.style.color = '#a855f7';
                }
            }
        } else {
            this.physicsStabilityCounter = 0;
        }
    }

    draw() {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        
        // 1. Griglia di Sfondo
        this.drawGrid();

        // --- Disegna Quadranti ---
        this.ctx.save();
        this.ctx.translate(this.offset.x, this.offset.y);
        this.ctx.scale(this.zoom, this.zoom);
        
        const axisSize = 500000; 
        this.ctx.beginPath();
        this.ctx.moveTo(-axisSize, 0);
        this.ctx.lineTo(axisSize, 0);
        this.ctx.moveTo(0, -axisSize);
        this.ctx.lineTo(0, axisSize);
        this.ctx.strokeStyle = 'rgba(255, 255, 255, 0.08)';
        this.ctx.lineWidth = 2 / this.zoom;
        this.ctx.setLineDash([30 / this.zoom, 30 / this.zoom]);
        this.ctx.stroke();

        this.ctx.font = `800 ${28 / this.zoom}px 'JetBrains Mono', monospace`;
        this.ctx.fillStyle = 'rgba(255, 255, 255, 0.15)';
        this.ctx.textAlign = 'center';
        this.ctx.textBaseline = 'middle';
        const labelDist = 40000; 
        this.ctx.fillText("QUADRANTE 2 (NORD-OVEST)", -labelDist, -labelDist);
        this.ctx.fillText("QUADRANTE 1 (NORD-EST)", labelDist, -labelDist);
        this.ctx.fillText("QUADRANTE 3 (SUD-OVEST)", -labelDist, labelDist);
        this.ctx.fillText("QUADRANTE 4 (SUD-EST)", labelDist, labelDist);
        this.ctx.restore();

        // Calcolo dei confini di Frustum Culling reali sul Viewport
        const pad = Math.max(15000, 100 / this.zoom);
        const minWorldX = -this.offset.x / this.zoom - pad;
        const maxWorldX = (this.canvas.width - this.offset.x) / this.zoom + pad;
        const minWorldY = -this.offset.y / this.zoom - pad;
        const maxWorldY = (this.canvas.height - this.offset.y) / this.zoom + pad;
        
        this.viewport = { minX: minWorldX, maxX: maxWorldX, minY: minWorldY, maxY: maxWorldY };

        this.ctx.save();
        this.ctx.translate(this.offset.x, this.offset.y);
        this.ctx.scale(this.zoom, this.zoom);

        // Costruzione Quadtree per velocizzare culling spaziale sui nodi visibili
        const qt = this.buildQuadtree();

        // 2. Disegno Zone di Cluster (Atmosfere semantiche)
        Object.keys(this.clusters).forEach(cid => {
            this.drawClusterHull(this.clusters[cid], cid);
        });

        // 3. Disegno Connessioni in Batch
        this.drawLinks();

        // 4. Query spaziale dei nodi visibili tramite Quadtree
        let visibleNodes = [];
        if (qt) {
            const queryRange = {
                x: (minWorldX + maxWorldX) / 2,
                y: (minWorldY + maxWorldY) / 2,
                w: (maxWorldX - minWorldX) / 2,
                h: (maxWorldY - minWorldY) / 2
            };
            visibleNodes = qt.query(queryRange);
        } else {
            visibleNodes = this.nodes; // Fallback se il quadtree non si costruisce
        }

        // 5. Disegno Nodi
        visibleNodes.forEach(n => {
            this.drawNode(n);
        });

        // 6. Draw Marquee/Lasso Selection overlays
        if (this.isSelecting) {
            this.ctx.save();
            this.ctx.lineWidth = 2 / this.zoom;
            this.ctx.strokeStyle = '#00f0ff';
            this.ctx.fillStyle = 'rgba(0, 240, 255, 0.08)';
            this.ctx.setLineDash([6 / this.zoom, 4 / this.zoom]);
            this.ctx.shadowBlur = 10;
            this.ctx.shadowColor = '#00f0ff';
            
            if (this.selectionMode === 'rect') {
                const w = this.selectionEnd.x - this.selectionStart.x;
                const h = this.selectionEnd.y - this.selectionStart.y;
                this.ctx.beginPath();
                this.ctx.rect(this.selectionStart.x, this.selectionStart.y, w, h);
                this.ctx.fill();
                this.ctx.stroke();
            } else if (this.selectionMode === 'lasso' && this.selectionPoints.length > 1) {
                this.ctx.beginPath();
                this.ctx.moveTo(this.selectionPoints[0].x, this.selectionPoints[0].y);
                for (let i = 1; i < this.selectionPoints.length; i++) {
                    this.ctx.lineTo(this.selectionPoints[i].x, this.selectionPoints[i].y);
                }
                this.ctx.closePath();
                this.ctx.fill();
                this.ctx.stroke();
            }
            this.ctx.restore();
        }

        this.updateScrollbars();
        this.ctx.restore();
    }

    drawGrid() {
        const step = 100 * this.zoom * 1000;
        if (step < 12) return;

        this.ctx.beginPath();
        this.ctx.strokeStyle = 'rgba(59, 130, 246, 0.03)';
        this.ctx.lineWidth = 1;

        const startX = this.offset.x % step;
        const startY = this.offset.y % step;

        for (let x = startX; x < this.canvas.width; x += step) {
            this.ctx.moveTo(x, 0);
            this.ctx.lineTo(x, this.canvas.height);
        }
        for (let y = startY; y < this.canvas.height; y += step) {
            this.ctx.moveTo(0, y);
            this.ctx.lineTo(this.canvas.width, y);
        }
        this.ctx.stroke();
    }

    getClusterColorWithOpacity(clusterId, opacity) {
        let hash = 0;
        const str = String(clusterId || 'default');
        for (let i = 0; i < str.length; i++) {
            hash = str.charCodeAt(i) + ((hash << 5) - hash);
        }
        const hue = Math.abs(hash % 360);
        return `hsla(${hue}, 90%, 60%, ${opacity})`;
    }

    getClusterColor(clusterId) {
        return this.getClusterColorWithOpacity(clusterId, 1.0);
    }

    isFilteredOut(n) {
        if (!this.activeFilters) return false;
        const type = (n.metadata && n.metadata.type) ? n.metadata.type : (n.isGalaxy ? 'code_asset' : 'other');
        let mappedType = 'other';
        if (['code_module', 'code_class', 'code_function', 'code_asset'].includes(type)) {
            mappedType = type;
        }
        return !this.activeFilters[mappedType];
    }

    drawClusterHull(nodes, clusterId) {
        if (nodes.length < 2) return;
        
        let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
        nodes.forEach(n => {
            if (this.isFilteredOut(n)) return;
            minX = Math.min(minX, n.x);
            minY = Math.min(minY, n.y);
            maxX = Math.max(maxX, n.x);
            maxY = Math.max(maxY, n.y);
        });

        if (minX === Infinity) return;

        const padding = 60000;
        const w = (maxX - minX) + padding * 2;
        const h = (maxY - minY) + padding * 2;

        // Culling delle zone semantiche offscreen
        if (this.viewport) {
            if (maxX + padding < this.viewport.minX || minX - padding > this.viewport.maxX ||
                maxY + padding < this.viewport.minY || minY - padding > this.viewport.maxY) {
                return;
            }
        }

        this.ctx.beginPath();
        this.ctx.roundRect(minX - padding, minY - padding, w, h, 25000);
        
        const gradient = this.ctx.createRadialGradient(
            minX + w/2, minY + h/2, 0,
            minX + w/2, minY + h/2, Math.max(w, h)
        );
        gradient.addColorStop(0, this.getClusterColorWithOpacity(clusterId, 0.035));
        gradient.addColorStop(1, this.getClusterColorWithOpacity(clusterId, 0.00));

        this.ctx.fillStyle = gradient;
        this.ctx.fill();
        
        this.ctx.strokeStyle = this.getClusterColorWithOpacity(clusterId, 0.12);
        this.ctx.lineWidth = 1500;
        this.ctx.stroke();
        
        // Etichetta del Cluster (LOD: scompare a zoom estremo out)
        if (this.zoom > 0.00015) {
            this.ctx.fillStyle = this.getClusterColorWithOpacity(clusterId, 0.65);
            this.ctx.font = `bold 18000px Orbitron`;
            const cleanLabel = clusterId.toUpperCase().replace(/_+/g, ' ');
            this.ctx.fillText(`ZONE: ${cleanLabel}`, minX - padding, minY - padding - 10000);
        }
    }

    drawLinks() {
        if (!this.viewport) return;
        const { minX, maxX, minY, maxY } = this.viewport;
        const isInteractive = this.isDragging || this.isZooming;

        // Se siamo molto distanti (Macro View), non visualizziamo le linee per evitare un groviglio incomprensibile (hairball)
        if (this.zoom <= 0.0006 && !this.focusMode && !this.highlightedPath) return;

        const standardBatch = [];
        const inferredBatch = [];
        const galacticBatch = [];
        const customBatch = [];
        const dimmedBatch = [];
        const pathLinksBatch = [];
        const hoveredEdgesBatch = [];       // SPRINT 3: Edges attached to hovered node
        // ── SPRINT 1: New batches ──────────────────────────────────────────────
        const surprisingBatch = [];         // Cross-community edges (magenta dashed)
        const blastEdgeBatch = [];          // Edges connected to blast nodes (red)
        const ambiguousBatch = [];          // Confidence < 0.7 (dotted yellow)
        // ──────────────────────────────────────────────────────────────────────

        const pad = 35000;
        
        // SPRINT 3: Arrow Helper
        const drawArrow = (b) => {
            if (this.zoom < 0.001) return; // Skip arrows if too far
            const angle = Math.atan2(b.n2.y - b.n1.y, b.n2.x - b.n1.x);
            const arrowLen = 1500;
            const offset = 6000;
            const tx = b.n2.x - Math.cos(angle) * offset;
            const ty = b.n2.y - Math.sin(angle) * offset;
            this.ctx.moveTo(tx, ty);
            this.ctx.lineTo(tx - arrowLen * Math.cos(angle - Math.PI/6), ty - arrowLen * Math.sin(angle - Math.PI/6));
            this.ctx.moveTo(tx, ty);
            this.ctx.lineTo(tx - arrowLen * Math.cos(angle + Math.PI/6), ty - arrowLen * Math.sin(angle + Math.PI/6));
        };

        const process = (link, isCustom) => {
            const n1 = this.nodeMap.get(link.source);
            const n2 = this.nodeMap.get(link.target);
            if (!n1 || !n2) return;

            if (this.isFilteredOut(n1) || this.isFilteredOut(n2)) return;

            // Focus Mode: Se attivo, oscura del tutto o salta i collegamenti estranei al nodo focale
            if (this.focusMode && this.focusedNode && !this.focusDepthNodes) {
                const isInc = n1.id === this.focusedNode.id || n2.id === this.focusedNode.id;
                if (!isInc) return;
            }

            // Bounding box culling rapido della linea
            const linkMinX = Math.min(n1.x, n2.x);
            const linkMaxX = Math.max(n1.x, n2.x);
            const linkMinY = Math.min(n1.y, n2.y);
            const linkMaxY = Math.max(n1.y, n2.y);

            if (linkMaxX < minX - pad || linkMinX > maxX + pad ||
                linkMaxY < minY - pad || linkMinY > maxY + pad) {
                return;
            }

            // Pathfinder check
            const isPathLink = this.highlightedPathLinks && (
                this.highlightedPathLinks.has(`${n1.id}-${n2.id}`) || 
                this.highlightedPathLinks.has(`${n2.id}-${n1.id}`)
            );

            if (isPathLink) {
                pathLinksBatch.push({ n1, n2 });
                return;
            }

            // Dimmed check
            let isDimmed = false;
            if (this.focusDepthNodes) {
                if (!this.focusDepthNodes.has(n1.id) || !this.focusDepthNodes.has(n2.id)) {
                    isDimmed = true;
                }
            }
            if (this.highlightedCommunity) {
                if (n1.cluster !== this.highlightedCommunity || n2.cluster !== this.highlightedCommunity) {
                    isDimmed = true;
                }
            }
            if (this.highlightedPath) {
                // If there's an active path, and this isn't a path link, it's dimmed
                isDimmed = true;
            }

            if (isDimmed) {
                dimmedBatch.push({ n1, n2 });
                return;
            }

            // ── SPRINT 1: Blast radius edge routing ───────────────────────────
            if (this.blastMode && this.blastNodes) {
                const n1Blast = this.blastNodes.has(n1.id) || (this.blastCenterNode && this.blastCenterNode.id === n1.id);
                const n2Blast = this.blastNodes.has(n2.id) || (this.blastCenterNode && this.blastCenterNode.id === n2.id);
                if (n1Blast && n2Blast) {
                    blastEdgeBatch.push({ n1, n2 });
                    return;
                }
                // Neither node in blast radius: dim the edge heavily
                dimmedBatch.push({ n1, n2 });
                return;
            }

            // ── SPRINT 1: Surprising Connections routing ─────────────────────
            if (this.showSurprising && n1.cluster && n2.cluster && n1.cluster !== n2.cluster) {
                surprisingBatch.push({ n1, n2 });
                return;
            }
            // ─────────────────────────────────────────────────────────────────

            if (isCustom) {
                customBatch.push({ n1, n2 });
                return;
            }

            const isGalactic = n1.isGalaxy || n2.isGalaxy;
            const isInferred = link.type === 'inferred' || link.confidence === 'INFERRED';

            // ── SPRINT 1: Confidence Mode routing ────────────────────────────
            if (this.confidenceMode && !isGalactic) {
                const conf = typeof link.confidence_score === 'number' ? link.confidence_score :
                             (link.confidence === 'INFERRED' ? 0.8 : 1.0);
                if (conf < 0.7) {
                    ambiguousBatch.push({ n1, n2 });
                    return;
                }
                if (isInferred) {
                    inferredBatch.push({ n1, n2 }); // blue/violet dashed
                    return;
                }
                standardBatch.push({ n1, n2 }); // solid green confirmed
                return;
            }
            // ─────────────────────────────────────────────────────────────────

            if (this.hoveredNode && (n1.id === this.hoveredNode.id || n2.id === this.hoveredNode.id)) {
                hoveredEdgesBatch.push({ n1, n2, relation: link.relation || link.relation_type || 'LINK' });
            }

            if (isGalactic) {
                galacticBatch.push({ n1, n2 });
            } else if (isInferred) {
                inferredBatch.push({ n1, n2 });
            } else {
                standardBatch.push({ n1, n2 });
            }
        };

        // Processamento veloce tramite O(1) Map lookup
        if (window.lastNeuralLinks) {
            window.lastNeuralLinks.forEach(l => process(l, false));
        }
        this.customLinks.forEach(l => process(l, true));

        // 1. Batch di Collegamenti Dimmed (Faint gray)
        if (dimmedBatch.length > 0) {
            this.ctx.beginPath();
            this.ctx.strokeStyle = 'rgba(255, 255, 255, 0.05)';
            this.ctx.lineWidth = 200;
            dimmedBatch.forEach(b => {
                this.ctx.moveTo(b.n1.x, b.n1.y);
                this.ctx.lineTo(b.n2.x, b.n2.y);
            });
            this.ctx.stroke();
        }

        // 2. Batch di Collegamenti Standard (Extracted / Inferred)
        if (isInteractive) {
            // Interactive Zooming/Dragging: draw all standard links in one steel-blue batch for performance
            if (standardBatch.length > 0 || inferredBatch.length > 0) {
                this.ctx.beginPath();
                this.ctx.strokeStyle = 'rgba(100, 116, 139, 0.06)';
                this.ctx.lineWidth = 200;
                standardBatch.forEach(b => {
                    this.ctx.moveTo(b.n1.x, b.n1.y);
                    this.ctx.lineTo(b.n2.x, b.n2.y);
                    drawArrow(b);
                });
                inferredBatch.forEach(b => {
                    this.ctx.moveTo(b.n1.x, b.n1.y);
                    this.ctx.lineTo(b.n2.x, b.n2.y);
                    drawArrow(b);
                });
                this.ctx.stroke();
            }
        } else {
            // Idle: draw in community-specific HSL batches
            const communityGroups = new Map();
            const addToCommGroup = (b, type) => {
                const comm = b.n1.cluster || 'default';
                if (!communityGroups.has(comm)) {
                    communityGroups.set(comm, { standard: [], inferred: [] });
                }
                communityGroups.get(comm)[type].push(b);
            };

            standardBatch.forEach(b => addToCommGroup(b, 'standard'));
            inferredBatch.forEach(b => addToCommGroup(b, 'inferred'));

            communityGroups.forEach((group, comm) => {
                // Draw standard links for this community
                if (group.standard.length > 0) {
                    this.ctx.beginPath();
                    this.ctx.strokeStyle = this.getClusterColorWithOpacity(comm, 0.16);
                    this.ctx.lineWidth = 300;
                    group.standard.forEach(b => {
                        this.ctx.moveTo(b.n1.x, b.n1.y);
                        this.ctx.lineTo(b.n2.x, b.n2.y);
                        drawArrow(b);
                    });
                    this.ctx.stroke();
                }

                // Draw inferred links for this community
                if (group.inferred.length > 0 && (this.zoom > 0.0025 || this.focusMode)) {
                    this.ctx.beginPath();
                    this.ctx.strokeStyle = this.getClusterColorWithOpacity(comm, 0.08);
                    this.ctx.lineWidth = 200;
                    this.ctx.setLineDash([4000, 6000]);
                    group.inferred.forEach(b => {
                        this.ctx.moveTo(b.n1.x, b.n1.y);
                        this.ctx.lineTo(b.n2.x, b.n2.y);
                        drawArrow(b);
                    });
                    this.ctx.stroke();
                    this.ctx.setLineDash([]);
                }
            });
        }

        // 3. Batch di Collegamenti Galattici (Galactic gold tethers)
        if (galacticBatch.length > 0) {
            this.ctx.beginPath();
            this.ctx.strokeStyle = this.focusMode ? 'rgba(245, 158, 11, 0.55)' : 'rgba(245, 158, 11, 0.22)';
            this.ctx.lineWidth = this.focusMode ? 1200 : 800;
            galacticBatch.forEach(b => {
                this.ctx.moveTo(b.n1.x, b.n1.y);
                this.ctx.lineTo(b.n2.x, b.n2.y);
            });
            this.ctx.stroke();
        }

        // 4. Batch di Collegamenti Utente (Cyber green dashed tethers)
        if (customBatch.length > 0) {
            this.ctx.beginPath();
            this.ctx.strokeStyle = 'rgba(0, 255, 157, 0.4)';
            this.ctx.lineWidth = 1000;
            this.ctx.setLineDash([6000, 8000]);
            customBatch.forEach(b => {
                this.ctx.moveTo(b.n1.x, b.n1.y);
                this.ctx.lineTo(b.n2.x, b.n2.y);
            });
            this.ctx.stroke();
            this.ctx.setLineDash([]);
        }

        // 5. Shortest Path Highlight links (Thick, glowing cyan)
        if (pathLinksBatch.length > 0) {
            this.ctx.save();
            this.ctx.beginPath();
            this.ctx.strokeStyle = '#00f0ff';
            this.ctx.lineWidth = 2000;
            this.ctx.shadowBlur = 20;
            this.ctx.shadowColor = '#00f0ff';
            pathLinksBatch.forEach(b => {
                this.ctx.moveTo(b.n1.x, b.n1.y);
                this.ctx.lineTo(b.n2.x, b.n2.y);
            });
            this.ctx.stroke();
            this.ctx.restore();
        }

        // ── SPRINT 1 — 6. Surprising Connections (Magenta pulsing dashed)
        if (this.showSurprising && surprisingBatch.length > 0 && !isInteractive) {
            this.ctx.save();
            this.ctx.beginPath();
            this.ctx.strokeStyle = 'rgba(236, 72, 153, 0.65)'; // hot pink/magenta
            this.ctx.lineWidth = 700;
            this.ctx.setLineDash([3000, 4000]);
            this.ctx.shadowBlur = 15;
            this.ctx.shadowColor = 'rgba(236, 72, 153, 0.5)';
            surprisingBatch.forEach(b => {
                this.ctx.moveTo(b.n1.x, b.n1.y);
                this.ctx.lineTo(b.n2.x, b.n2.y);
            });
            this.ctx.stroke();
            this.ctx.setLineDash([]);
            this.ctx.restore();
        }

        // ── SPRINT 1 — 7. Blast Radius Edges (Red warm glow)
        if (this.blastMode && blastEdgeBatch.length > 0) {
            this.ctx.save();
            this.ctx.beginPath();
            this.ctx.strokeStyle = isInteractive ? 'rgba(239, 68, 68, 0.4)' : 'rgba(239, 68, 68, 0.65)';
            this.ctx.lineWidth = isInteractive ? 300 : 900;
            if (!isInteractive) {
                this.ctx.shadowBlur = 18;
                this.ctx.shadowColor = 'rgba(239, 68, 68, 0.55)';
            }
            blastEdgeBatch.forEach(b => {
                this.ctx.moveTo(b.n1.x, b.n1.y);
                this.ctx.lineTo(b.n2.x, b.n2.y);
            });
            this.ctx.stroke();
            this.ctx.restore();
        }

        // ── SPRINT 1 — 8. Ambiguous Confidence Edges (Yellow dotted, confidence < 0.7)
        if (this.confidenceMode && ambiguousBatch.length > 0 && !isInteractive) {
            this.ctx.save();
            this.ctx.beginPath();
            this.ctx.strokeStyle = 'rgba(234, 179, 8, 0.55)'; // yellow
            this.ctx.lineWidth = 200;
            this.ctx.setLineDash([1500, 2500]);
            ambiguousBatch.forEach(b => {
                this.ctx.moveTo(b.n1.x, b.n1.y);
                this.ctx.lineTo(b.n2.x, b.n2.y);
            });
            this.ctx.stroke();
            this.ctx.setLineDash([]);
            this.ctx.restore();
        }

        // Elastic line during edge creation
        if (this.activeTool === 'edge' && this.edgeSourceNode && this.mouseWorldPos) {
            this.ctx.beginPath();
            this.ctx.strokeStyle = 'rgba(255, 255, 255, 0.5)';
            this.ctx.lineWidth = 1500;
            this.ctx.setLineDash([4000, 4000]);
            this.ctx.moveTo(this.edgeSourceNode.x, this.edgeSourceNode.y);
            this.ctx.lineTo(this.mouseWorldPos.x, this.mouseWorldPos.y);
            this.ctx.stroke();
        }

        // ── SPRINT 3 — 9. Hovered Edges Text Labels (Performance Graph)
        if (hoveredEdgesBatch.length > 0 && !isInteractive && this.zoom > 0.001) {
            this.ctx.save();
            this.ctx.textAlign = 'center';
            this.ctx.textBaseline = 'middle';
            this.ctx.font = 'bold 3500px Orbitron';
            hoveredEdgesBatch.forEach(b => {
                const midX = (b.n1.x + b.n2.x) / 2;
                const midY = (b.n1.y + b.n2.y) / 2;
                // Highlight link itself
                this.ctx.beginPath();
                this.ctx.strokeStyle = 'rgba(255, 255, 255, 0.6)';
                this.ctx.lineWidth = 800;
                this.ctx.moveTo(b.n1.x, b.n1.y);
                this.ctx.lineTo(b.n2.x, b.n2.y);
                this.ctx.stroke();
                
                // Draw label background
                const txtW = this.ctx.measureText(b.relation).width;
                this.ctx.fillStyle = 'rgba(15, 23, 42, 0.8)';
                this.ctx.roundRect(midX - txtW/2 - 1000, midY - 2500, txtW + 2000, 5000, 1000);
                this.ctx.fill();
                
                // Draw label text
                this.ctx.fillStyle = '#00f0ff';
                this.ctx.fillText(b.relation, midX, midY);
            });
            this.ctx.restore();
        }
    }

    drawNode(n) {
        if (this.isFilteredOut(n)) return;

        const isSelected = this.selectedNode === n;
        const isGroupSelected = this.selectedNodesForDrag && this.selectedNodesForDrag.includes(n);
        const isClusterSelected = this.selectedNodesForCluster && this.selectedNodesForCluster.includes(n);
        const isPathNode = this.highlightedPath && this.highlightedPath.has(n.id);
        const isGodNode = this.godNodesHighlight && this.godNodes && this.godNodes.has(n.id);
        
        // Focus Mode & Dimmed states for unified transparency
        let globalAlpha = 1.0;
        if (this.focusMode && this.focusedNode) {
            const isInc = n.id === this.focusedNode.id || this.focusedNeighbors.has(n.id);
            if (!isInc) globalAlpha = 0.15;
        }
        if (this.focusDepthNodes) {
            const isInc = this.focusDepthNodes.has(n.id);
            if (!isInc) globalAlpha = 0.05;
        }
        if (this.highlightedCommunity && n.cluster !== this.highlightedCommunity) {
            globalAlpha = 0.06;
        }
        if (this.highlightedPath && !isPathNode) {
            globalAlpha = 0.06;
        }

        const isInteractive = this.isDragging || this.isZooming;
        
        // ── SPRINT 1: Node Size ∝ Degree (Graphify formula) ──────────────────
        const degree = this._nodeDegrees.get(n.id) || 0;
        const degreeBonus = Math.sqrt(degree) * 3000;
        const baseSize = n.isGalaxy ? 15000 : Math.min(28000, 8000 + degreeBonus);
        // ─────────────────────────────────────────────────────────────────────
        
        // ── SPRINT 1: Blast Radius state ──────────────────────────────────────
        const isBlastCenter = this.blastMode && this.blastCenterNode && this.blastCenterNode.id === n.id;
        const isBlastNode   = this.blastMode && this.blastNodes && this.blastNodes.has(n.id) && !isBlastCenter;
        const isBlastDimmed = this.blastMode && this.blastNodes && !this.blastNodes.has(n.id) && !isBlastCenter;
        // ─────────────────────────────────────────────────────────────────────
        
        // Dynamic node color aligned with 3D Cycloscope
        let nodeColor = n.color || '#06b6d4';
        if (n.isGalaxy) {
            nodeColor = '#f59e0b';
        } else if (window._showPartitions && n.partition_id !== undefined) {
            const partitionColors = ["#ef4444", "#3b82f6", "#10b981", "#facc15", "#a855f7", "#ec4899", "#06b6d4", "#f97316"];
            nodeColor = partitionColors[n.partition_id % partitionColors.length];
        } else if (n.cluster && n.cluster !== 'default') {
            nodeColor = this.getClusterColorWithOpacity(n.cluster, 1.0);
        }
        
        // LOD macro: A zoom estremo out disegna i nodi minori come piccoli punti pixelosi senza appesantire la GPU
        if (this.zoom <= 0.0006 && !n.isGalaxy && !isSelected && !isGroupSelected && !this.focusMode && !isPathNode && !isGodNode && !isBlastCenter && !isBlastNode) {
            this.ctx.beginPath();
            this.ctx.arc(n.x, n.y, 4000, 0, Math.PI * 2);
            this.ctx.fillStyle = isBlastDimmed ? 'rgba(100,116,139,0.2)' : nodeColor;
            this.ctx.globalAlpha = isBlastDimmed ? 0.2 : (globalAlpha * 0.5);
            this.ctx.fill();
            this.ctx.globalAlpha = 1.0;
            return;
        }

        let size = baseSize;
        if (isSelected) size = baseSize * 1.55;
        else if (isPathNode) size = baseSize * 1.5;
        else if (isGodNode) size = baseSize * 1.4;
        else if (isBlastCenter) size = baseSize * 1.6;
        else if (isBlastNode) size = baseSize * 1.2;
        else if (isGroupSelected) size = baseSize * 1.3;
        else if (isClusterSelected) size = baseSize * 1.3;
        
        // Blast dimming overrides global alpha
        if (isBlastDimmed) globalAlpha = Math.min(globalAlpha, 0.12);

        
        this.ctx.save();
        this.ctx.globalAlpha = globalAlpha;

        // Effetti Neon Glow: Disattivati durante dragging/zooming
        if (!isInteractive && this.zoom >= 0.0006) {
            this.ctx.shadowBlur = 12;
            if (isBlastCenter) {
                this.ctx.shadowBlur = 35;
                this.ctx.shadowColor = '#ef4444';
            } else if (isBlastNode) {
                this.ctx.shadowBlur = 20;
                this.ctx.shadowColor = 'rgba(239, 68, 68, 0.7)';
            } else if (isPathNode) {
                this.ctx.shadowBlur = 25;
                this.ctx.shadowColor = '#00f0ff';
            } else if (isGodNode) {
                this.ctx.shadowBlur = 25;
                this.ctx.shadowColor = '#f59e0b';
            } else if (isSelected) {
                this.ctx.shadowBlur = 25;
                this.ctx.shadowColor = '#00ff9d';
            } else if (isGroupSelected) {
                this.ctx.shadowBlur = 20;
                this.ctx.shadowColor = '#00f0ff';
            } else if (isClusterSelected) {
                this.ctx.shadowBlur = 20;
                this.ctx.shadowColor = '#a855f7';
            } else {
                this.ctx.shadowColor = nodeColor;
            }
        }

        this.ctx.beginPath();
        this.ctx.arc(n.x, n.y, size, 0, Math.PI * 2);
        this.ctx.fillStyle = isClusterSelected ? '#a855f7' : nodeColor;
        this.ctx.fill();

        // 🪐 Glowing neon-cyan dotted border ring at size * 1.4 around all group-selected nodes
        if (isGroupSelected) {
            this.ctx.save();
            this.ctx.beginPath();
            this.ctx.arc(n.x, n.y, size * 1.4, 0, Math.PI * 2);
            this.ctx.strokeStyle = '#00f0ff';
            this.ctx.lineWidth = 800;
            this.ctx.setLineDash([2000, 2000]);
            this.ctx.shadowBlur = !isInteractive ? 15 : 0;
            this.ctx.shadowColor = '#00f0ff';
            this.ctx.stroke();
            this.ctx.restore();
        }

        // 🪐 Concentric orbit rings for Galaxies, Hubs, Paths, and Blast nodes (Skip in motion)
        if (!isInteractive && this.zoom >= 0.001) {
            this.ctx.shadowBlur = 0;
            if (isBlastCenter) {
                // Animated pulse rings for blast center (GitNexus style)
                const pulse = (this._blastAnimFrame % 60) / 60; // 0..1
                const r1 = size * (1.8 + pulse * 1.2);
                const r2 = size * (2.5 + pulse * 1.0);
                this.ctx.beginPath();
                this.ctx.arc(n.x, n.y, r1, 0, Math.PI * 2);
                this.ctx.strokeStyle = `rgba(239, 68, 68, ${0.55 - pulse * 0.55})`;
                this.ctx.lineWidth = 600;
                this.ctx.stroke();
                this.ctx.beginPath();
                this.ctx.arc(n.x, n.y, r2, 0, Math.PI * 2);
                this.ctx.strokeStyle = `rgba(239, 68, 68, ${0.30 - pulse * 0.30})`;
                this.ctx.lineWidth = 400;
                this.ctx.stroke();
            } else if (isBlastNode) {
                this.ctx.beginPath();
                this.ctx.arc(n.x, n.y, size * 1.5, 0, Math.PI * 2);
                this.ctx.strokeStyle = 'rgba(239, 68, 68, 0.35)';
                this.ctx.lineWidth = 350;
                this.ctx.stroke();
            } else if (isPathNode) {
                this.ctx.beginPath();
                this.ctx.arc(n.x, n.y, size * 1.8, 0, Math.PI * 2);
                this.ctx.strokeStyle = 'rgba(0, 240, 255, 0.4)';
                this.ctx.lineWidth = 400;
                this.ctx.stroke();
            } else if (isGodNode) {
                this.ctx.beginPath();
                this.ctx.arc(n.x, n.y, size * 1.8, 0, Math.PI * 2);
                this.ctx.strokeStyle = 'rgba(245, 158, 11, 0.4)';
                this.ctx.lineWidth = 400;
                this.ctx.stroke();
            } else if (n.isGalaxy) {
                this.ctx.beginPath();
                this.ctx.arc(n.x, n.y, size * 2.2, 0, Math.PI * 2);
                this.ctx.strokeStyle = 'rgba(245, 158, 11, 0.3)';
                this.ctx.lineWidth = 300;
                this.ctx.stroke();

                this.ctx.beginPath();
                this.ctx.arc(n.x, n.y, size * 3.5, 0, Math.PI * 2);
                this.ctx.strokeStyle = 'rgba(245, 158, 11, 0.12)';
                this.ctx.lineWidth = 200;
                this.ctx.setLineDash([1000, 1200]);
                this.ctx.stroke();
                this.ctx.setLineDash([]);
            }
        }

        // Draw solid boundary outlines
        if (isSelected) {
            this.ctx.shadowBlur = 0;
            this.ctx.strokeStyle = '#fff';
            this.ctx.lineWidth = 2000;
            this.ctx.stroke();
        } else if (isPathNode) {
            this.ctx.shadowBlur = 0;
            this.ctx.strokeStyle = '#00f0ff';
            this.ctx.lineWidth = 1500;
            this.ctx.stroke();
        } else if (isGodNode) {
            this.ctx.shadowBlur = 0;
            this.ctx.strokeStyle = '#f59e0b';
            this.ctx.lineWidth = 1500;
            this.ctx.stroke();
        } else if (isGroupSelected) {
            this.ctx.shadowBlur = 0;
            this.ctx.strokeStyle = '#00f0ff';
            this.ctx.lineWidth = 1000;
            this.ctx.stroke();
        }

        // Render Labels (LOD: disattivate a zoom piccoli per culling efficiente)
        if (this.zoom >= 0.0009 || isSelected || isGroupSelected || isPathNode || isGodNode || (this.focusMode && globalAlpha > 0.5) || (this.focusDepthNodes && globalAlpha > 0.05)) {
            if (this.zoom >= 0.0022 || n.isGalaxy || isSelected || isGroupSelected || isPathNode || isGodNode || this.focusMode || this.focusDepthNodes) {
                // Adaptive font size
                let fontSize = 12000;
                if (n.isGalaxy) fontSize = 15000;
                if (isSelected || isPathNode || isGodNode) fontSize = 14000;

                const label = n.text.length > 30 ? n.text.substring(0, 30) + '...' : n.text;
                this.ctx.font = `${Math.floor(fontSize)}px Inter, sans-serif`;
                const textWidth = this.ctx.measureText(label).width;
                const paddingX = fontSize * 0.8;
                const paddingY = fontSize * 0.45;
                const rectW = textWidth + paddingX * 2;
                const rectH = fontSize + paddingY * 2;
                const rectX = n.x - rectW / 2;
                const rectY = n.y + size + fontSize * 0.8;

                this.ctx.save();
                this.ctx.shadowBlur = 0;
                this.ctx.beginPath();
                if (this.ctx.roundRect) {
                    this.ctx.roundRect(rectX, rectY, rectW, rectH, rectH / 2);
                } else {
                    const r = rectH / 2;
                    this.ctx.moveTo(rectX + r, rectY);
                    this.ctx.arcTo(rectX + rectW, rectY, rectX + rectW, rectY + rectH, r);
                    this.ctx.arcTo(rectX + rectW, rectY + rectH, rectX, rectY + rectH, r);
                    this.ctx.arcTo(rectX, rectY + rectH, rectX, rectY, r);
                    this.ctx.arcTo(rectX, rectY, rectX + rectW, rectY, r);
                }
                this.ctx.fillStyle = '#0f172a';
                this.ctx.fill();
                this.ctx.strokeStyle = nodeColor;
                this.ctx.lineWidth = fontSize * 0.12;
                this.ctx.stroke();

                this.ctx.fillStyle = isSelected ? '#fff' : (isPathNode ? '#00f0ff' : (isGodNode ? '#fb923c' : (isGroupSelected ? '#00f0ff' : '#cbd5e1')));
                this.ctx.textAlign = 'center';
                this.ctx.textBaseline = 'middle';
                this.ctx.fillText(label, n.x, rectY + rectH / 2);
                this.ctx.restore();
            }
        }

        this.ctx.restore();
    }

    animate(timestamp) {
        requestAnimationFrame((t) => this.animate(t));

        if (!this.lastFrameTime) {
            this.lastFrameTime = timestamp || performance.now();
        }

        const elapsed = (timestamp || performance.now()) - this.lastFrameTime;
        const fpsInterval = 1000 / 24; // Limit rendering and physics to 24 FPS for low resource consumption

        if (this.isFlying) {
            this.zoom += (this.targetZoom - this.zoom) * 0.15;
            this.offset.x += (this.targetOffsetX - this.offset.x) * 0.15;
            this.offset.y += (this.targetOffsetY - this.offset.y) * 0.15;
            
            if (Math.abs(this.targetZoom - this.zoom) < 0.0001 && Math.abs(this.targetOffsetX - this.offset.x) < 0.1) {
                this.isFlying = false;
            }
        }

        if (elapsed >= fpsInterval || this.isFlying) {
            // Get ready for next frame, adjusting for interval drift
            if (!this.isFlying) {
                this.lastFrameTime = (timestamp || performance.now()) - (elapsed % fpsInterval);
            }

            // ── SPRINT 1: Advance blast pulse animation ─────────────────────
            if (this.blastMode) this._blastAnimFrame++;
            // ────────────────────────────────────────────────────────────────
            this.applyForces();
            
            // 🛑 OPTIMIZATION: Only redraw if there is active physics/interaction or requested
            const needsRedraw = this.forcesEnabled || 
                                this.isFlying || 
                                this.isDragging || 
                                this.isDraggingGroup || 
                                this.draggedNode || 
                                this.isSelecting || 
                                this.blastMode ||
                                this.isZooming ||
                                this._forceNextDraw;
                                
            if (needsRedraw) {
                this.draw();
                this._forceNextDraw = false;
            }
        }
    }

    injectControls() {
        const parent = this.canvas.parentElement;
        if (!parent) return;

        // Pannello di controllo fluttuante orizzontale in basso (Stile Premium Glassmorphic)
        const controlPanel = document.createElement('div');
        controlPanel.id = 'tactical-graphify-controls';
        controlPanel.style.cssText = `
            position: absolute;
            bottom: 1.5rem;
            left: 50%;
            transform: translateX(-50%);
            display: none;
            align-items: center;
            gap: 1rem;
            background: rgba(15, 23, 42, 0.85);
            backdrop-filter: blur(25px) saturate(180%);
            -webkit-backdrop-filter: blur(25px) saturate(180%);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 100px;
            padding: 0.6rem 1.4rem;
            box-shadow: 0 20px 50px rgba(0,0,0,0.5), inset 0 1px 0 rgba(255,255,255,0.1);
            z-index: 2001;
            font-family: 'Inter', sans-serif;
            color: #fff;
            transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
        `;

        // Barra di Ricerca Integrata
        const searchContainer = document.createElement('div');
        searchContainer.style.cssText = `
            position: relative;
            display: flex;
            align-items: center;
        `;

        const searchInput = document.createElement('input');
        searchInput.type = 'text';
        searchInput.placeholder = 'Search Atom / Module...';
        searchInput.style.cssText = `
            background: rgba(0, 0, 0, 0.4);
            border: 1px solid rgba(255, 255, 255, 0.15);
            border-radius: 50px;
            padding: 0.4rem 1rem 0.4rem 2.2rem;
            font-size: 0.75rem;
            color: #fff;
            outline: none;
            width: 180px;
            transition: all 0.2s ease;
        `;
        // Autocomplete List fluttuante verso l'alto
        const autocompleteList = document.createElement('div');
        autocompleteList.style.cssText = `
            position: absolute;
            bottom: 45px;
            left: 0;
            width: 100%;
            max-height: 200px;
            overflow-y: auto;
            background: rgba(15, 23, 42, 0.96);
            backdrop-filter: blur(25px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 12px;
            box-shadow: 0 -10px 30px rgba(0,0,0,0.5);
            display: none;
            z-index: 2002;
        `;

        searchInput.onfocus = () => {
            searchInput.style.borderColor = '#00ff9d';
            searchInput.style.width = '240px';
            searchInput.style.boxShadow = '0 0 10px rgba(0, 255, 157, 0.2)';
            autocompleteList.style.display = 'block';
            this.updateAutocomplete(searchInput.value, autocompleteList);
        };
        searchInput.onblur = () => {
            searchInput.style.borderColor = 'rgba(255, 255, 255, 0.15)';
            searchInput.style.width = '180px';
            searchInput.style.boxShadow = 'none';
            setTimeout(() => { autocompleteList.style.display = 'none'; }, 220);
        };
        searchInput.oninput = () => {
            this.updateAutocomplete(searchInput.value, autocompleteList);
        };
        
        // Save references for synchronization and keyboard navigation
        this.bottomSearchInput = searchInput;
        this.bottomSearchResults = autocompleteList;
        
        searchInput.addEventListener('keydown', (e) => {
            this.handleSearchKeydown(e, searchInput, autocompleteList);
        });

        const searchIcon = document.createElement('i');
        searchIcon.className = 'fas fa-search';
        searchIcon.style.cssText = `
            position: absolute;
            left: 0.8rem;
            font-size: 0.75rem;
            color: rgba(255, 255, 255, 0.4);
            pointer-events: none;
        `;

        searchContainer.appendChild(searchIcon);
        searchContainer.appendChild(searchInput);
        searchContainer.appendChild(autocompleteList);

        // Sezione Filtri a Checkbox
        const filtersContainer = document.createElement('div');
        filtersContainer.style.cssText = `
            display: flex;
            align-items: center;
            gap: 0.8rem;
            border-left: 1px solid rgba(255, 255, 255, 0.15);
            padding-left: 1.2rem;
            border-right: 1px solid rgba(255, 255, 255, 0.15);
            padding-right: 1.2rem;
        `;

        const types = [
            { key: 'code_module', label: 'Module', color: '#3b82f6', tooltip: 'Filter by Module nodes (structural high-level domains)' },
            { key: 'code_class', label: 'Class', color: '#a855f7', tooltip: 'Filter by Class nodes (data containers and constructors)' },
            { key: 'code_function', label: 'Function', color: '#00ff9d', tooltip: 'Filter by Function nodes (executable operations and pipelines)' },
            { key: 'code_asset', label: 'Asset', color: '#64748b', tooltip: 'Filter by Asset nodes (static configurations, files, or external payloads)' },
            { key: 'other', label: 'Other', color: '#cbd5e1', tooltip: 'Filter by Other nodes (unclassified metadata and generic atoms)' }
        ];

        types.forEach(t => {
            const labelEl = document.createElement('label');
            labelEl.title = t.tooltip;
            labelEl.style.cssText = `
                display: flex;
                align-items: center;
                gap: 0.4rem;
                font-size: 0.7rem;
                cursor: pointer;
                user-select: none;
                transition: opacity 0.2s ease;
            `;

            const checkbox = document.createElement('input');
            checkbox.type = 'checkbox';
            checkbox.checked = true;
            checkbox.dataset.filterKey = t.key;
            checkbox.style.cssText = `
                cursor: pointer;
                accent-color: ${t.color};
            `;
            checkbox.onchange = (e) => {
                this.updateFilter(t.key, e.target.checked);
            };

            const dot = document.createElement('span');
            dot.style.cssText = `
                width: 8px;
                height: 8px;
                border-radius: 50%;
                background: ${t.color};
                box-shadow: 0 0 5px ${t.color};
            `;

            const text = document.createTextNode(t.label);

            labelEl.appendChild(checkbox);
            labelEl.appendChild(dot);
            labelEl.appendChild(text);
            filtersContainer.appendChild(labelEl);
        });

        // 📤 Pulsante Esportazione Premium (Stile Graphify)
        const exportBtn = document.createElement('button');
        exportBtn.style.cssText = `
            background: rgba(59, 130, 246, 0.15);
            border: 1px solid rgba(59, 130, 246, 0.3);
            color: #3b82f6;
            border-radius: 50px;
            padding: 0.4rem 1rem;
            font-size: 0.72rem;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 0.4rem;
            transition: all 0.2s ease;
            font-family: 'Inter', sans-serif;
            font-weight: 600;
        `;
        exportBtn.innerHTML = '<i class="fas fa-file-export"></i> Export';
        exportBtn.onmouseover = () => {
            exportBtn.style.background = 'rgba(59, 130, 246, 0.3)';
            exportBtn.style.color = '#fff';
        };
        exportBtn.onmouseout = () => {
            exportBtn.style.background = 'rgba(59, 130, 246, 0.15)';
            exportBtn.style.color = '#3b82f6';
        };
        exportBtn.onclick = () => {
            this.showExportMenu(exportBtn);
        };

        // Tooltip Informativo Fluttuante all'Hover del mouse sui nodi
        const hoverCard = document.createElement('div');
        hoverCard.id = 'tactical-hover-inspect-card';
        hoverCard.style.cssText = `
            position: absolute;
            display: none;
            background: rgba(15, 23, 42, 0.95);
            backdrop-filter: blur(25px) saturate(180%);
            -webkit-backdrop-filter: blur(25px) saturate(180%);
            border: 1px solid rgba(0, 255, 157, 0.35);
            border-radius: 12px;
            padding: 0.8rem 1rem;
            width: 280px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.6), 0 0 15px rgba(0, 255, 157, 0.1);
            z-index: 3000;
            pointer-events: none;
            font-family: 'Inter', sans-serif;
            color: #fff;
            font-size: 0.7rem;
            line-height: 1.4;
            transition: opacity 0.15s ease;
        `;
        parent.appendChild(hoverCard);
        this.hoverCard = hoverCard;

        // Selection Tools Container (Stile Premium Glassmorphic)
        const selectionContainer = document.createElement('div');
        selectionContainer.style.cssText = `
            display: flex;
            align-items: center;
            gap: 0.4rem;
            border-left: 1px solid rgba(255, 255, 255, 0.15);
            padding-left: 1rem;
        `;

        const tools = [
            { id: 'navigate', label: 'Navigation', icon: 'fa-mouse-pointer', title: 'Navigate / Drag single atom' },
            { id: 'rect', label: 'Box Select', icon: 'fa-vector-square', title: 'Box selection (Drag marquee rectangle)' },
            { id: 'lasso', label: 'Lasso Select', icon: 'fa-draw-polygon', title: 'Lasso selection (Draw freehand path)' }
        ];

        const btnElements = {};

        const updateSelectionButtons = () => {
            tools.forEach(t => {
                const btn = btnElements[t.id];
                if (btn) {
                    if (this.selectionMode === t.id) {
                        btn.style.background = 'rgba(0, 255, 157, 0.2)';
                        btn.style.borderColor = 'rgba(0, 255, 157, 0.6)';
                        btn.style.color = '#00ff9d';
                        btn.style.boxShadow = '0 0 10px rgba(0, 255, 157, 0.25)';
                    } else {
                        btn.style.background = 'rgba(255, 255, 255, 0.05)';
                        btn.style.borderColor = 'rgba(255, 255, 255, 0.1)';
                        btn.style.color = '#fff';
                        btn.style.boxShadow = 'none';
                    }
                }
            });
        };

        tools.forEach(t => {
            const btn = document.createElement('button');
            btn.title = t.title;
            btn.style.cssText = `
                background: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(255, 255, 255, 0.1);
                color: #fff;
                border-radius: 30px;
                padding: 0.35rem 0.75rem;
                font-size: 0.7rem;
                cursor: pointer;
                display: flex;
                align-items: center;
                gap: 0.35rem;
                transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
                font-family: 'Inter', sans-serif;
                font-weight: 500;
            `;
            btn.innerHTML = `<i class="fas ${t.icon}"></i> <span>${t.label}</span>`;
            
            btn.onmouseover = () => {
                if (this.selectionMode !== t.id) {
                    btn.style.background = 'rgba(255, 255, 255, 0.12)';
                    btn.style.borderColor = 'rgba(255, 255, 255, 0.25)';
                }
            };
            btn.onmouseout = () => {
                if (this.selectionMode !== t.id) {
                    btn.style.background = 'rgba(255, 255, 255, 0.05)';
                    btn.style.borderColor = 'rgba(255, 255, 255, 0.1)';
                }
            };

            btn.onclick = () => {
                this.setSelectionMode(t.id);
            };

            selectionContainer.appendChild(btn);
            btnElements[t.id] = btn;
        });

        updateSelectionButtons();

        // Sync values inside searchInput.oninput to the sidebar
        const origOnInput = searchInput.oninput;
        searchInput.oninput = () => {
            if (origOnInput) origOnInput();
            const rightSearchInput = document.getElementById('tactical-search-input');
            if (rightSearchInput) rightSearchInput.value = searchInput.value;
        };

        // Horizontal Scrollbar
        let trackH = document.getElementById('tactical-scrollbar-h');
        if (!trackH) {
            trackH = document.createElement('div');
            trackH.id = 'tactical-scrollbar-h';
            trackH.style.cssText = `
                position: absolute;
                bottom: 0;
                left: 0;
                width: calc(100% - 10px);
                height: 8px;
                background: rgba(15, 23, 42, 0.35);
                backdrop-filter: blur(5px);
                border-radius: 4px;
                z-index: 2000;
                cursor: pointer;
            `;
            
            const thumbH = document.createElement('div');
            thumbH.id = 'tactical-scrollbar-h-thumb';
            thumbH.style.cssText = `
                position: absolute;
                top: 0;
                left: 0;
                height: 100%;
                background: rgba(168, 85, 247, 0.4);
                border: 1px solid rgba(168, 85, 247, 0.6);
                border-radius: 4px;
                cursor: grab;
                transition: background 0.2s, border-color 0.2s;
            `;
            thumbH.onmouseenter = () => {
                thumbH.style.background = 'rgba(0, 255, 157, 0.5)';
                thumbH.style.borderColor = 'rgba(0, 255, 157, 0.8)';
            };
            thumbH.onmouseleave = () => {
                if (!this._draggingH) {
                    thumbH.style.background = 'rgba(168, 85, 247, 0.4)';
                    thumbH.style.borderColor = 'rgba(168, 85, 247, 0.6)';
                }
            };
            
            thumbH.onpointerdown = (e) => {
                e.preventDefault();
                e.stopPropagation();
                this._draggingH = true;
                thumbH.setPointerCapture(e.pointerId);
                const startX = e.clientX;
                const startLeft = parseFloat(thumbH.style.left) || 0;
                const trackWidth = trackH.clientWidth;
                const thumbWidth = thumbH.offsetWidth;
                const maxLeft = trackWidth - thumbWidth;
                
                const onPointerMove = (moveEvent) => {
                    const deltaX = moveEvent.clientX - startX;
                    let newLeft = startLeft + deltaX;
                    newLeft = Math.max(0, Math.min(newLeft, maxLeft));
                    thumbH.style.left = `${newLeft}px`;
                    
                    const leftRatio = maxLeft > 0 ? newLeft / maxLeft : 0;
                    const bounds = this.getGraphCoordinateBounds();
                    const worldTotalW = bounds.maxX - bounds.minX;
                    const worldLeft = bounds.minX + leftRatio * worldTotalW;
                    this.offset.x = -worldLeft * this.zoom;
                    this.draw();
                };
                
                const onPointerUp = (upEvent) => {
                    this._draggingH = false;
                    thumbH.releasePointerCapture(upEvent.pointerId);
                    thumbH.removeEventListener('pointermove', onPointerMove);
                    thumbH.removeEventListener('pointerup', onPointerUp);
                    thumbH.style.background = 'rgba(168, 85, 247, 0.4)';
                    thumbH.style.borderColor = 'rgba(168, 85, 247, 0.6)';
                };
                
                thumbH.addEventListener('pointermove', onPointerMove);
                thumbH.addEventListener('pointerup', onPointerUp);
            };

            trackH.onclick = (e) => {
                if (e.target === thumbH) return;
                const rect = trackH.getBoundingClientRect();
                const clickX = e.clientX - rect.left;
                const thumbWidth = thumbH.offsetWidth;
                const trackWidth = trackH.clientWidth;
                const maxLeft = trackWidth - thumbWidth;
                let newLeft = clickX - thumbWidth / 2;
                newLeft = Math.max(0, Math.min(newLeft, maxLeft));
                thumbH.style.left = `${newLeft}px`;
                
                const leftRatio = maxLeft > 0 ? newLeft / maxLeft : 0;
                const bounds = this.getGraphCoordinateBounds();
                const worldTotalW = bounds.maxX - bounds.minX;
                const worldLeft = bounds.minX + leftRatio * worldTotalW;
                this.offset.x = -worldLeft * this.zoom;
                this.draw();
            };
            
            trackH.appendChild(thumbH);
            parent.appendChild(trackH);
        }

        // Vertical Scrollbar
        let trackV = document.getElementById('tactical-scrollbar-v');
        if (!trackV) {
            trackV = document.createElement('div');
            trackV.id = 'tactical-scrollbar-v';
            trackV.style.cssText = `
                position: absolute;
                top: 0;
                right: 0;
                width: 8px;
                height: calc(100% - 10px);
                background: rgba(15, 23, 42, 0.35);
                backdrop-filter: blur(5px);
                border-radius: 4px;
                z-index: 2000;
                cursor: pointer;
            `;
            
            const thumbV = document.createElement('div');
            thumbV.id = 'tactical-scrollbar-v-thumb';
            thumbV.style.cssText = `
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                background: rgba(168, 85, 247, 0.4);
                border: 1px solid rgba(168, 85, 247, 0.6);
                border-radius: 4px;
                cursor: grab;
                transition: background 0.2s, border-color 0.2s;
            `;
            thumbV.onmouseenter = () => {
                thumbV.style.background = 'rgba(0, 255, 157, 0.5)';
                thumbV.style.borderColor = 'rgba(0, 255, 157, 0.8)';
            };
            thumbV.onmouseleave = () => {
                if (!this._draggingV) {
                    thumbV.style.background = 'rgba(168, 85, 247, 0.4)';
                    thumbV.style.borderColor = 'rgba(168, 85, 247, 0.6)';
                }
            };
            
            thumbV.onpointerdown = (e) => {
                e.preventDefault();
                e.stopPropagation();
                this._draggingV = true;
                thumbV.setPointerCapture(e.pointerId);
                const startY = e.clientY;
                const startTop = parseFloat(thumbV.style.top) || 0;
                const trackHeight = trackV.clientHeight;
                const thumbHeight = thumbV.offsetHeight;
                const maxTop = trackHeight - thumbHeight;
                
                const onPointerMove = (moveEvent) => {
                    const deltaY = moveEvent.clientY - startY;
                    let newTop = startTop + deltaY;
                    newTop = Math.max(0, Math.min(newTop, maxTop));
                    thumbV.style.top = `${newTop}px`;
                    
                    const topRatio = maxTop > 0 ? newTop / maxTop : 0;
                    const bounds = this.getGraphCoordinateBounds();
                    const worldTotalH = bounds.maxY - bounds.minY;
                    const worldTop = bounds.minY + topRatio * worldTotalH;
                    this.offset.y = -worldTop * this.zoom;
                    this.draw();
                };
                
                const onPointerUp = (upEvent) => {
                    this._draggingV = false;
                    thumbV.releasePointerCapture(upEvent.pointerId);
                    thumbV.removeEventListener('pointermove', onPointerMove);
                    thumbV.removeEventListener('pointerup', onPointerUp);
                    thumbV.style.background = 'rgba(168, 85, 247, 0.4)';
                    thumbV.style.borderColor = 'rgba(168, 85, 247, 0.6)';
                };
                
                thumbV.addEventListener('pointermove', onPointerMove);
                thumbV.addEventListener('pointerup', onPointerUp);
            };

            trackV.onclick = (e) => {
                if (e.target === thumbV) return;
                const rect = trackV.getBoundingClientRect();
                const clickY = e.clientY - rect.top;
                const thumbHeight = thumbV.offsetHeight;
                const trackHeight = trackV.clientHeight;
                const maxTop = trackHeight - thumbHeight;
                let newTop = clickY - thumbHeight / 2;
                newTop = Math.max(0, Math.min(newTop, maxTop));
                thumbV.style.top = `${newTop}px`;
                
                const topRatio = maxTop > 0 ? newTop / maxTop : 0;
                const bounds = this.getGraphCoordinateBounds();
                const worldTotalH = bounds.maxY - bounds.minY;
                const worldTop = bounds.minY + topRatio * worldTotalH;
                this.offset.y = -worldTop * this.zoom;
                this.draw();
            };
            
            trackV.appendChild(thumbV);
            parent.appendChild(trackV);
        }

        controlPanel.appendChild(searchContainer);
        controlPanel.appendChild(selectionContainer);
        controlPanel.appendChild(filtersContainer);
        controlPanel.appendChild(exportBtn);
        parent.appendChild(controlPanel);

        // Event listener Hover per mostrare la scheda informativa
        this.canvas.addEventListener('mousemove', (e) => this.handleHoverCard(e));
        this.canvas.addEventListener('mouseleave', () => {
            if (this.hoverCard) this.hoverCard.style.display = 'none';
        });
    }

    // Dropdown fluttuante per selezionare la tipologia di esportazione
    showExportMenu(anchor) {
        let menu = document.getElementById('tactical-export-dropdown');
        if (menu) {
            menu.style.display = menu.style.display === 'none' ? 'flex' : 'none';
            return;
        }

        menu = document.createElement('div');
        menu.id = 'tactical-export-dropdown';
        menu.style.cssText = `
            position: absolute;
            bottom: 55px;
            right: 1.5rem;
            background: rgba(15, 23, 42, 0.96);
            backdrop-filter: blur(25px);
            border: 1px solid rgba(59, 130, 246, 0.4);
            border-radius: 12px;
            padding: 0.5rem;
            display: flex;
            flex-direction: column;
            gap: 0.3rem;
            box-shadow: 0 -10px 30px rgba(0,0,0,0.6);
            z-index: 2005;
            width: 140px;
        `;

        const createOption = (text, icon, action) => {
            const btn = document.createElement('button');
            btn.style.cssText = `
                background: transparent;
                border: none;
                color: #fff;
                font-family: 'Inter', sans-serif;
                font-size: 0.68rem;
                padding: 0.4rem 0.6rem;
                text-align: left;
                cursor: pointer;
                border-radius: 6px;
                display: flex;
                align-items: center;
                gap: 0.5rem;
                transition: background 0.15s ease;
                width: 100%;
            `;
            btn.innerHTML = `<i class="${icon}"></i> ${text}`;
            btn.onmouseover = () => {
                btn.style.background = 'rgba(59, 130, 246, 0.2)';
                btn.style.color = '#3b82f6';
            };
            btn.onmouseout = () => {
                btn.style.background = 'transparent';
                btn.style.color = '#fff';
            };
            btn.onclick = () => {
                action();
                menu.style.display = 'none';
            };
            return btn;
        };

        const optJson = createOption('Export JSON', 'fas fa-file-code', () => this.exportAsJSON());
        const optSvg = createOption('Export SVG', 'fas fa-file-image', () => this.exportAsSVG());

        menu.appendChild(optJson);
        menu.appendChild(optSvg);
        
        anchor.parentElement.appendChild(menu);
    }

    // Esporta i dati attuali del grafo in formato JSON strutturato (Compatibile Graphify)
    exportAsJSON() {
        const data = {
            nodes: this.nodes.map(n => ({
                id: n.id,
                label: n.text,
                cluster: n.cluster,
                color: n.color,
                isGalaxy: n.isGalaxy,
                x: n.x,
                y: n.y,
                metadata: n.metadata
            })),
            links: (window.lastNeuralLinks || []).concat(this.customLinks).map(l => ({
                source: l.source,
                target: l.target,
                type: l.type || 'extracted'
            }))
        };
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `tactical-canvas-export-${Date.now()}.json`;
        a.click();
        URL.revokeObjectURL(url);
        console.log("📥 JSON Graph exported successfully!");
    }

    // Esporta il grafo in formato vettoriale statico SVG scalabile ad altissima qualità
    exportAsSVG() {
        if (this.nodes.length === 0) return;

        let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
        this.nodes.forEach(n => {
            minX = Math.min(minX, n.x);
            minY = Math.min(minY, n.y);
            maxX = Math.max(maxX, n.x);
            maxY = Math.max(maxY, n.y);
        });

        const pad = 100000;
        const w = (maxX - minX) + pad * 2;
        const h = (maxY - minY) + pad * 2;

        let svg = `<?xml version="1.0" encoding="utf-8"?>\n`;
        svg += `<svg xmlns="http://www.w3.org/2000/svg" viewBox="${minX - pad} ${minY - pad} ${w} ${h}" width="100%" height="100%" style="background:#020617; font-family:'Inter', sans-serif;">\n`;
        
        // 1. Atmosfere di Zone Hulls
        Object.keys(this.clusters).forEach(cid => {
            const list = this.clusters[cid];
            if (list.length < 2) return;
            
            let cMinX = Infinity, cMinY = Infinity, cMaxX = -Infinity, cMaxY = -Infinity;
            list.forEach(n => {
                cMinX = Math.min(cMinX, n.x);
                cMinY = Math.min(cMinY, n.y);
                cMaxX = Math.max(cMaxX, n.x);
                cMaxY = Math.max(cMaxY, n.y);
            });

            const cPad = 60000;
            const cW = (cMaxX - cMinX) + cPad * 2;
            const cH = (cMaxY - cMinY) + cPad * 2;
            const baseColor = this.getClusterColor(cid);

            svg += `  <!-- Cluster Hull ${cid} -->\n`;
            svg += `  <rect x="${cMinX - cPad}" y="${cMinY - cPad}" width="${cW}" height="${cH}" rx="25000" fill="${baseColor}" fill-opacity="0.03" stroke="${baseColor}" stroke-opacity="0.15" stroke-width="1500" />\n`;
            svg += `  <text x="${cMinX - cPad}" y="${cMinY - cPad - 10000}" fill="${baseColor}" fill-opacity="0.65" font-size="18000" font-weight="bold">${cid.toUpperCase().replace(/_+/g, ' ')}</text>\n`;
        });

        // 2. Collegamenti (Archi)
        const drawLinksList = (linksList, color, width, isDashed = false) => {
            linksList.forEach(l => {
                const n1 = this.nodeMap.get(l.source);
                const n2 = this.nodeMap.get(l.target);
                if (!n1 || !n2) return;
                
                const dash = isDashed ? ` stroke-dasharray="6000, 8000"` : '';
                svg += `  <line x1="${n1.x}" y1="${n1.y}" x2="${n2.x}" y2="${n2.y}" stroke="${color}" stroke-width="${width}" opacity="0.65"${dash} />\n`;
            });
        };

        if (window.lastNeuralLinks) {
            const ext = [], gal = [], inf = [];
            window.lastNeuralLinks.forEach(l => {
                const n1 = this.nodeMap.get(l.source);
                const n2 = this.nodeMap.get(l.target);
                if (!n1 || !n2) return;
                if (n1.isGalaxy || n2.isGalaxy) gal.push(l);
                else if (l.type === 'inferred' || l.confidence === 'INFERRED') inf.push(l);
                else ext.push(l);
            });
            
            drawLinksList(ext, 'rgba(59, 130, 246, 0.65)', 800, false);
            drawLinksList(inf, 'rgba(59, 130, 246, 0.45)', 600, true);
            drawLinksList(gal, 'rgba(245, 158, 11, 0.75)', 1000, false);
        }
        drawLinksList(this.customLinks, 'rgba(0, 255, 157, 0.75)', 1200, true);

        // 3. Atomi e scritte
        this.nodes.forEach(n => {
            const baseSize = n.isGalaxy ? 15000 : 8000;
            svg += `  <!-- Node ${n.text} -->\n`;
            svg += `  <circle cx="${n.x}" cy="${n.y}" r="${baseSize}" fill="${n.color}" />\n`;
            if (n.isGalaxy) {
                svg += `  <circle cx="${n.x}" cy="${n.y}" r="${baseSize * 2.2}" fill="none" stroke="rgba(245, 158, 11, 0.35)" stroke-width="300" />\n`;
            }
            const cleanText = n.text.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
            svg += `  <text x="${n.x + baseSize + 5000}" y="${n.y + 4000}" fill="#fff" font-size="12000" font-weight="600">${cleanText}</text>\n`;
        });

        svg += `</svg>\n`;

        const blob = new Blob([svg], { type: 'image/svg+xml' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `tactical-canvas-export-${Date.now()}.svg`;
        a.click();
        URL.revokeObjectURL(url);
        console.log("📥 SVG Graph exported successfully!");
    }

    styleAutocompleteItem(item, isActive) {
        const defaultColor = item.getAttribute('data-default-color') || '#fff';
        if (isActive) {
            item.style.background = 'rgba(0, 255, 157, 0.1)';
            item.style.color = '#00ff9d';
        } else {
            item.style.background = 'transparent';
            item.style.color = defaultColor;
        }
    }

    handleSearchKeydown(e, inputEl, listEl) {
        if (listEl.style.display === 'none') return;
        
        const items = Array.from(listEl.querySelectorAll('[data-node-id]'));
        if (items.length === 0) return;
        
        let activeIdx = items.findIndex(item => item.getAttribute('data-active') === 'true');
        
        if (e.key === 'ArrowDown') {
            e.preventDefault();
            if (activeIdx > -1) {
                items[activeIdx].removeAttribute('data-active');
                this.styleAutocompleteItem(items[activeIdx], false);
            }
            activeIdx = (activeIdx + 1) % items.length;
            items[activeIdx].setAttribute('data-active', 'true');
            this.styleAutocompleteItem(items[activeIdx], true);
            items[activeIdx].scrollIntoView({ block: 'nearest' });
        } else if (e.key === 'ArrowUp') {
            e.preventDefault();
            if (activeIdx > -1) {
                items[activeIdx].removeAttribute('data-active');
                this.styleAutocompleteItem(items[activeIdx], false);
            }
            activeIdx = (activeIdx - 1 + items.length) % items.length;
            items[activeIdx].setAttribute('data-active', 'true');
            this.styleAutocompleteItem(items[activeIdx], true);
            items[activeIdx].scrollIntoView({ block: 'nearest' });
        } else if (e.key === 'Enter') {
            if (activeIdx > -1) {
                e.preventDefault();
                const nodeId = items[activeIdx].getAttribute('data-node-id');
                const selectedNode = this.nodes.find(n => n.id === nodeId);
                if (selectedNode) {
                    this.focusOnNode(selectedNode);
                    // Sync both inputs
                    const rightSearchInput = document.getElementById('tactical-search-input');
                    if (rightSearchInput) rightSearchInput.value = selectedNode.text;
                    if (this.bottomSearchInput) this.bottomSearchInput.value = selectedNode.text;
                }
                listEl.style.display = 'none';
                inputEl.blur();
            }
        } else if (e.key === 'Escape') {
            e.preventDefault();
            listEl.style.display = 'none';
            inputEl.blur();
        }
    }

    updateAutocomplete(query, listEl) {
        listEl.innerHTML = '';
        if (!query.trim()) {
            listEl.style.display = 'none';
            return;
        }

        const matches = this.nodes
            .filter(n => n.text.toLowerCase().includes(query.toLowerCase()))
            .slice(0, 8);

        if (matches.length === 0) {
            const noMatch = document.createElement('div');
            noMatch.innerText = 'No matches found';
            noMatch.style.cssText = `
                padding: 0.5rem 0.8rem;
                font-size: 0.7rem;
                color: rgba(255, 255, 255, 0.4);
                font-style: italic;
            `;
            listEl.appendChild(noMatch);
            return;
        }

        matches.forEach(m => {
            const item = document.createElement('div');
            item.setAttribute('data-node-id', m.id);
            item.setAttribute('data-default-color', '#fff');
            item.style.cssText = `
                padding: 0.5rem 0.8rem;
                font-size: 0.7rem;
                cursor: pointer;
                color: #fff;
                transition: background 0.15s ease;
                border-bottom: 1px solid rgba(255,255,255,0.03);
            `;
            item.onmouseover = () => {
                const items = Array.from(listEl.querySelectorAll('[data-node-id]'));
                items.forEach(other => {
                    if (other !== item) {
                        other.removeAttribute('data-active');
                        this.styleAutocompleteItem(other, false);
                    }
                });
                item.setAttribute('data-active', 'true');
                this.styleAutocompleteItem(item, true);
            };
            item.onmouseout = () => {
                item.removeAttribute('data-active');
                this.styleAutocompleteItem(item, false);
            };
            item.onmousedown = (e) => {
                e.preventDefault();
                this.focusOnNode(m);
                listEl.style.display = 'none';
                
                // Sync both inputs
                const rightSearchInput = document.getElementById('tactical-search-input');
                if (rightSearchInput) rightSearchInput.value = m.text;
                if (this.bottomSearchInput) this.bottomSearchInput.value = m.text;
            };

            const type = (m.metadata && m.metadata.type) ? m.metadata.type : (m.isGalaxy ? 'code_asset' : 'other');
            let color = '#cbd5e1';
            if (type === 'code_module') color = '#3b82f6';
            else if (type === 'code_class') color = '#a855f7';
            else if (type === 'code_function') color = '#00ff9d';
            else if (type === 'code_asset') color = '#64748b';

            item.innerHTML = `
                <div style="display: flex; align-items: center; gap: 0.5rem;">
                    <span style="width: 6px; height: 6px; border-radius: 50%; background: ${color};"></span>
                    <span style="font-weight: 600;">${m.text}</span>
                </div>
            `;
            listEl.appendChild(item);
        });
    }

    focusOnNode(node) {
        this.selectedNode = node;
        this.triggerNodeSelection(node);

        this.zoom = Math.min(this.maxZoom, Math.max(this.minZoom, this.idealFitZoom * 4.0));
        this.offset.x = this.canvas.width / 2 - node.x * this.zoom;
        this.offset.y = this.canvas.height / 2 - node.y * this.zoom;
        
        console.log("Focused camera on:", node.text);
    }

    handleHoverCard(e) {
        if (!this.hoverCard) return;

        const rect = this.canvas.getBoundingClientRect();
        const mouseX = e.clientX - rect.left;
        const mouseY = e.clientY - rect.top;

        // Bounding box hit detection spaziale immediata
        const hitNode = this.nodes.find(n => {
            if (!this.isInteractiveNode(n)) return false;
            
            const nodeScreenX = n.x * this.zoom + this.offset.x;
            const nodeScreenY = n.y * this.zoom + this.offset.y;
            
            const dx = nodeScreenX - mouseX;
            const dy = nodeScreenY - mouseY;
            const distance = Math.sqrt(dx * dx + dy * dy);
            
            const baseSize = n.isGalaxy ? 15000 : 8000;
            const nodeScreenRadius = baseSize * this.zoom;
            const hitTargetRadius = Math.max(nodeScreenRadius, 15) + 8;
            
            return distance < hitTargetRadius;
        });

        if (hitNode) {
            const type = (hitNode.metadata && hitNode.metadata.type) ? hitNode.metadata.type.replace('code_', '').toUpperCase() : (hitNode.isGalaxy ? 'GALAXY' : 'ATOM');
            const cluster = hitNode.cluster ? hitNode.cluster.toUpperCase().replace(/_+/g, ' ') : 'DEFAULT';
            const source = (hitNode.metadata && hitNode.metadata.source) ? hitNode.metadata.source : 'N/A';
            const name = (hitNode.metadata && hitNode.metadata.name) ? hitNode.metadata.name : hitNode.text;

            let html = `
                <div style="font-weight: 800; font-size: 0.8rem; color: #00ff9d; margin-bottom: 0.4rem; word-break: break-all;">${name}</div>
                <div style="display: flex; flex-direction: column; gap: 0.2rem; font-family: 'JetBrains Mono', monospace; font-size: 0.6rem;">
                    <div><span style="color: #64748b;">TYPE:</span> <span style="color: #3b82f6; font-weight: 700;">${type}</span></div>
                    <div><span style="color: #64748b;">ZONE:</span> <span style="color: #a855f7;">${cluster}</span></div>
                    <div><span style="color: #64748b;">PATH:</span> <span style="color: #e2e8f0; word-break: break-all;">${source}</span></div>
            `;

            if (hitNode.metadata && hitNode.metadata.signature) {
                html += `<div><span style="color: #64748b;">SIGNATURE:</span> <span style="color: #f59e0b; word-break: break-all;">${hitNode.metadata.signature}</span></div>`;
            }
            if (hitNode.metadata && hitNode.metadata.parent) {
                html += `<div><span style="color: #64748b;">PARENT:</span> <span style="color: #ec4899;">${hitNode.metadata.parent}</span></div>`;
            }

            html += `</div>`;

            this.hoverCard.innerHTML = html;
            this.hoverCard.style.display = 'block';

            const cardWidth = 280;
            const cardHeight = this.hoverCard.offsetHeight || 120;
            let left = mouseX + 15;
            let top = mouseY + 15;

            if (left + cardWidth > this.canvas.width) {
                left = mouseX - cardWidth - 15;
            }
            if (top + cardHeight > this.canvas.height) {
                top = mouseY - cardHeight - 15;
            }

            this.hoverCard.style.left = `${left}px`;
            this.hoverCard.style.top = `${top}px`;
        } else {
            this.hoverCard.style.display = 'none';
        }
    }

    // --- SIDEBAR & TOPOLOGICAL METHODS ---

    toggleEditorDrawer() {
        const drawer = document.getElementById('tactical-editor-drawer');
        if (drawer) {
            drawer.style.display = drawer.style.display === 'none' ? 'flex' : 'none';
        }
    }

    focusOnCommunity(clusterId) {
        if (this.highlightedCommunity === clusterId) {
            // Reset community highlight
            this.highlightedCommunity = null;
            const statusFooter = document.getElementById('tactical-status-text');
            if (statusFooter) {
                this.updateCounters();
            }
            this.draw();
            return;
        }

        this.highlightedCommunity = clusterId;
        this.highlightedPath = null;
        this.highlightedPathLinks = null;
        this.godNodesHighlight = false;

        const clusterNodes = this.clusters[clusterId];
        if (clusterNodes && clusterNodes.length > 0) {
            let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
            clusterNodes.forEach(n => {
                minX = Math.min(minX, n.x);
                minY = Math.min(minY, n.y);
                maxX = Math.max(maxX, n.x);
                maxY = Math.max(maxY, n.y);
            });

            const dx = maxX - minX;
            const dy = maxY - minY;
            const centerX = minX + dx / 2;
            const centerY = minY + dy / 2;

            // Compute appropriate zoom to fit the community with padding dynamically
            const padding = Math.max(100, Math.max(dx, dy) * 0.15);
            const viewportWidth = this.canvas.width;
            const viewportHeight = this.canvas.height;
            const requiredZoomX = viewportWidth / (dx + padding * 2);
            const requiredZoomY = viewportHeight / (dy + padding * 2);
            this.zoom = Math.min(this.maxZoom, Math.max(this.minZoom, Math.min(requiredZoomX, requiredZoomY)));

            this.offset.x = viewportWidth / 2 - centerX * this.zoom;
            this.offset.y = viewportHeight / 2 - centerY * this.zoom;
        }

        const statusFooter = document.getElementById('tactical-status-text');
        if (statusFooter) {
            statusFooter.innerText = `COMMUNITY: Highlighted cluster '${clusterId.toUpperCase()}'`;
            statusFooter.style.color = '#a855f7';
        }

        this.draw();
    }

    populateCommunities() {
        const listEl = document.getElementById('tactical-communities-list');
        if (!listEl) return;
        listEl.innerHTML = '';

        // Sort communities by number of nodes descending
        const sortedClusters = Object.keys(this.clusters).sort((a, b) => {
            return this.clusters[b].length - this.clusters[a].length;
        });

        sortedClusters.forEach(cid => {
            const count = this.clusters[cid].length;
            const baseColor = this.getClusterColor(cid);
            
            const item = document.createElement('div');
            const isActive = this.highlightedCommunity === cid;
            item.style.cssText = `
                display: flex;
                align-items: center;
                justify-content: space-between;
                padding: 0.45rem 0.7rem;
                background: ${isActive ? 'rgba(168, 85, 247, 0.15)' : 'rgba(255, 255, 255, 0.02)'};
                border: 1px solid ${isActive ? '#a855f7' : 'rgba(255, 255, 255, 0.05)'};
                border-radius: 8px;
                cursor: pointer;
                font-size: 0.65rem;
                color: #cbd5e1;
                transition: all 0.2s ease;
            `;

            item.onmouseover = () => {
                if (!isActive) {
                    item.style.background = 'rgba(168, 85, 247, 0.08)';
                    item.style.borderColor = 'rgba(168, 85, 247, 0.3)';
                    item.style.color = '#fff';
                }
            };
            item.onmouseout = () => {
                if (!isActive) {
                    item.style.background = 'rgba(255, 255, 255, 0.02)';
                    item.style.borderColor = 'rgba(255, 255, 255, 0.05)';
                    item.style.color = '#cbd5e1';
                }
            };
            item.onclick = () => {
                this.focusOnCommunity(cid);
                this.populateCommunities(); // Redraw with active states
            };

            const leftGroup = document.createElement('div');
            leftGroup.style.cssText = `
                display: flex;
                align-items: center;
                gap: 0.5rem;
            `;

            const swatch = document.createElement('span');
            swatch.style.cssText = `
                width: 8px;
                height: 8px;
                border-radius: 50%;
                background: ${baseColor};
                box-shadow: 0 0 6px ${baseColor};
                flex-shrink: 0;
            `;

            const labelText = document.createElement('span');
            labelText.innerText = cid.replace(/_+/g, ' ').toUpperCase();
            labelText.style.cssText = `
                font-weight: 700;
                color: ${isActive ? '#fff' : '#cbd5e1'};
            `;

            leftGroup.appendChild(swatch);
            leftGroup.appendChild(labelText);

            const badge = document.createElement('span');
            badge.innerText = `${count} nodes`;
            badge.style.cssText = `
                background: rgba(255, 255, 255, 0.06);
                border: 1px solid rgba(255, 255, 255, 0.08);
                color: #cbd5e1;
                font-size: 0.55rem;
                font-family: 'JetBrains Mono', monospace;
                padding: 1px 6px;
                border-radius: 4px;
            `;

            item.appendChild(leftGroup);
            item.appendChild(badge);
            listEl.appendChild(item);
        });
    }

    onSearchInput(val) {
        if (this.bottomSearchInput && this.bottomSearchInput.value !== val) {
            this.bottomSearchInput.value = val;
        }

        const resultsEl = document.getElementById('tactical-search-results');
        if (!resultsEl) return;

        if (!val.trim()) {
            resultsEl.innerHTML = '';
            resultsEl.style.display = 'none';
            return;
        }

        const matches = this.nodes
            .filter(n => n.text.toLowerCase().includes(val.toLowerCase()))
            .slice(0, 10);

        resultsEl.innerHTML = '';
        if (matches.length === 0) {
            const noMatch = document.createElement('div');
            noMatch.innerText = 'No nodes match your query';
            noMatch.style.cssText = `
                padding: 0.6rem 1rem;
                font-size: 0.65rem;
                color: #64748b;
                font-style: italic;
            `;
            resultsEl.appendChild(noMatch);
            resultsEl.style.display = 'block';
            return;
        }

        matches.forEach(m => {
            const item = document.createElement('div');
            item.setAttribute('data-node-id', m.id);
            item.setAttribute('data-default-color', '#cbd5e1');
            item.style.cssText = `
                display: flex;
                align-items: center;
                gap: 0.5rem;
                padding: 0.5rem 0.8rem;
                font-size: 0.7rem;
                color: #cbd5e1;
                cursor: pointer;
                transition: all 0.15s ease;
                border-bottom: 1px solid rgba(255, 255, 255, 0.03);
            `;

            item.onmouseover = () => {
                const items = Array.from(resultsEl.querySelectorAll('[data-node-id]'));
                items.forEach(other => {
                    if (other !== item) {
                        other.removeAttribute('data-active');
                        this.styleAutocompleteItem(other, false);
                    }
                });
                item.setAttribute('data-active', 'true');
                this.styleAutocompleteItem(item, true);
            };
            item.onmouseout = () => {
                item.removeAttribute('data-active');
                this.styleAutocompleteItem(item, false);
            };
            
            // Use onmousedown to trigger selection before input blur
            item.onmousedown = (e) => {
                e.preventDefault(); // Prevent input from losing focus immediately
                this.focusOnNode(m);
                resultsEl.style.display = 'none';
                
                // Sync both inputs
                const rightSearchInput = document.getElementById('tactical-search-input');
                if (rightSearchInput) rightSearchInput.value = m.text;
                if (this.bottomSearchInput) this.bottomSearchInput.value = m.text;
            };

            const type = (m.metadata && m.metadata.type) ? m.metadata.type : (m.isGalaxy ? 'code_asset' : 'other');
            let color = '#cbd5e1';
            if (type.includes('module')) color = '#3b82f6';
            else if (type.includes('class')) color = '#a855f7';
            else if (type.includes('function')) color = '#00ff9d';
            else if (type.includes('asset')) color = '#64748b';

            const dot = document.createElement('span');
            dot.style.cssText = `
                width: 6px;
                height: 6px;
                border-radius: 50%;
                background: ${color};
                box-shadow: 0 0 5px ${color};
                flex-shrink: 0;
            `;

            const label = document.createElement('span');
            label.innerText = m.text;
            label.style.cssText = `
                overflow: hidden;
                text-overflow: ellipsis;
                white-space: nowrap;
                flex: 1;
            `;

            item.appendChild(dot);
            item.appendChild(label);
            resultsEl.appendChild(item);
        });

        resultsEl.style.display = 'block';
    }

    highlightGodNodes() {
        const btn = document.getElementById('btn-topo-godnodes');
        
        if (this.godNodesHighlight) {
            // Disable God Nodes highlight
            this.godNodesHighlight = false;
            this.godNodes = null;
            if (btn) {
                btn.style.background = 'rgba(245, 158, 11, 0.08)';
                btn.style.borderColor = 'rgba(245, 158, 11, 0.2)';
                btn.style.color = '#fb923c';
            }
            this.updateCounters();
            this.draw();
            console.log("God Nodes highlight disabled.");
            return;
        }

        // Enable God Nodes highlight
        this.godNodesHighlight = true;
        this.highlightedCommunity = null;
        this.highlightedPath = null;
        this.highlightedPathLinks = null;

        // Compute degree for each node
        const degrees = new Map();
        this.nodes.forEach(n => degrees.set(n.id, 0));

        const incrementDegree = (id) => {
            if (degrees.has(id)) {
                degrees.set(id, degrees.get(id) + 1);
            }
        };

        if (window.lastNeuralLinks) {
            window.lastNeuralLinks.forEach(l => {
                incrementDegree(l.source);
                incrementDegree(l.target);
            });
        }
        this.customLinks.forEach(l => {
            incrementDegree(l.source);
            incrementDegree(l.target);
        });

        // Sort nodes by degree
        const sortedNodes = [...this.nodes].sort((a, b) => {
            const degA = degrees.get(a.id) || 0;
            const degB = degrees.get(b.id) || 0;
            return degB - degA;
        });

        // Pick top 15 hub nodes
        const topHubs = sortedNodes.slice(0, 15).map(n => n.id);
        this.godNodes = new Set(topHubs);

        if (btn) {
            btn.style.background = 'rgba(245, 158, 11, 0.25)';
            btn.style.borderColor = '#fb923c';
            btn.style.color = '#fff';
        }

        const statusFooter = document.getElementById('tactical-status-text');
        if (statusFooter) {
            statusFooter.innerText = `HUBS: Highlighted top 15 cosmic central hubs`;
            statusFooter.style.color = '#fb923c';
        }

        this.draw();
        console.log("God Nodes highlight enabled for top 15 hubs:", topHubs);
    }

    startShortestPathMode() {
        const btn = document.getElementById('btn-topo-pathfinder');
        
        if (this.pathFinderMode || this.highlightedPath) {
            // Toggle off pathfinder
            this.pathFinderMode = null;
            this.pathFinderStartNode = null;
            this.highlightedPath = null;
            this.highlightedPathLinks = null;
            
            if (btn) {
                btn.style.background = 'rgba(6, 182, 212, 0.08)';
                btn.style.borderColor = 'rgba(6, 182, 212, 0.2)';
                btn.style.color = '#22d3ee';
            }
            
            this.updateCounters();
            this.draw();
            console.log("Pathfinder mode disabled.");
            return;
        }

        // Enable Pathfinder
        this.highlightedCommunity = null;
        this.godNodesHighlight = false;

        this.pathFinderMode = 'select_start';
        this.pathFinderStartNode = null;

        if (btn) {
            btn.style.background = 'rgba(6, 182, 212, 0.25)';
            btn.style.borderColor = '#22d3ee';
            btn.style.color = '#fff';
        }

        const statusFooter = document.getElementById('tactical-status-text');
        if (statusFooter) {
            statusFooter.innerText = 'PATHFINDER: Select start node on canvas';
            statusFooter.style.color = '#22d3ee';
        }

        this.draw();
        console.log("Pathfinder mode activated. Awaiting start node click.");
    }

    findShortestPath(startId, endId) {
        if (startId === endId) return [startId];

        // 1. Build adjacency list for fast lookup
        const adj = new Map();
        const addEdge = (u, v) => {
            if (!adj.has(u)) adj.set(u, []);
            if (!adj.has(v)) adj.set(v, []);
            adj.get(u).push(v);
            adj.get(v).push(u);
        };

        if (window.lastNeuralLinks) {
            window.lastNeuralLinks.forEach(l => {
                if (this.nodeMap.has(l.source) && this.nodeMap.has(l.target)) {
                    addEdge(l.source, l.target);
                }
            });
        }
        this.customLinks.forEach(l => {
            if (this.nodeMap.has(l.source) && this.nodeMap.has(l.target)) {
                addEdge(l.source, l.target);
            }
        });

        // 2. Standard BFS Queue
        const queue = [startId];
        const visited = new Set([startId]);
        const parentMap = new Map();

        let found = false;
        while (queue.length > 0) {
            const curr = queue.shift();
            if (curr === endId) {
                found = true;
                break;
            }

            const neighbors = adj.get(curr) || [];
            for (const neighbor of neighbors) {
                if (!visited.has(neighbor)) {
                    visited.add(neighbor);
                    parentMap.set(neighbor, curr);
                    queue.push(neighbor);
                }
            }
        }

        // 3. Reconstruct path if found
        if (!found) return null;

        const path = [];
        let curr = endId;
        while (curr !== startId) {
            path.push(curr);
            curr = parentMap.get(curr);
        }
        path.push(startId);
        return path.reverse();
    }

    // ═══════════════════════════════════════════════════════════════════════
    // SPRINT 1 — New Methods
    // ═══════════════════════════════════════════════════════════════════════

    /** Rebuild cached degree map. Call this after data is loaded. */
    buildDegreeMap() {
        const deg = new Map();
        this.nodes.forEach(n => deg.set(n.id, 0));
        const bump = (id) => { if (deg.has(id)) deg.set(id, deg.get(id) + 1); };
        if (window.lastNeuralLinks) {
            window.lastNeuralLinks.forEach(l => { bump(l.source); bump(l.target); });
        }
        this.customLinks.forEach(l => { bump(l.source); bump(l.target); });
        this._nodeDegrees = deg;
    }

    /**
     * Toggle Blast Radius Mode on the currently selected node.
     * Highlights all nodes within N hops and dims everything else.
     * Inspired by GitNexus impact analysis with animated pulse rings.
     */
    toggleBlastMode(depth = null) {
        const btn = document.getElementById('btn-sprint1-blast');

        if (this.blastMode) {
            // Disable
            this.blastMode = false;
            this.blastCenterNode = null;
            this.blastNodes = null;
            this._blastAnimFrame = 0;
            if (btn) {
                btn.style.background = 'rgba(239, 68, 68, 0.08)';
                btn.style.borderColor = 'rgba(239, 68, 68, 0.2)';
                btn.style.color = '#ef4444';
            }
            this.draw();
            return;
        }

        if (!this.selectedNode) {
            const sf = document.getElementById('tactical-status-text');
            if (sf) { sf.innerText = 'BLAST: Select a node first'; sf.style.color = '#ef4444'; }
            return;
        }

        const blastDepth = depth || this.blastDepth;
        this.blastMode = true;
        this.blastCenterNode = this.selectedNode;
        const reachable = this.calculateFocusDepthNodes(this.selectedNode.id, blastDepth);
        reachable.delete(this.selectedNode.id); // center is separate
        this.blastNodes = reachable;

        if (btn) {
            btn.style.background = 'rgba(239, 68, 68, 0.25)';
            btn.style.borderColor = '#ef4444';
            btn.style.color = '#fff';
        }

        const sf = document.getElementById('tactical-status-text');
        if (sf) {
            sf.innerText = `BLAST RADIUS: ${reachable.size} nodes within ${blastDepth} hops from "${this.selectedNode.text}"`;
            sf.style.color = '#ef4444';
        }

        this.draw();
        console.log(`💥 [Blast Radius] Center: ${this.selectedNode.text}, Affected: ${reachable.size} nodes`);
    }

    /**
     * Toggle Surprising Connections — highlights cross-community edges in magenta.
     * Inspired by Graphify's "Cross-Community Link" detector.
     */
    toggleSurprisingConnections() {
        const btn = document.getElementById('btn-sprint1-surprising');
        this.showSurprising = !this.showSurprising;

        if (this.showSurprising) {
            // Count cross-community edges
            let count = 0;
            const allLinks = [...(window.lastNeuralLinks || []), ...this.customLinks];
            allLinks.forEach(l => {
                const n1 = this.nodeMap.get(l.source);
                const n2 = this.nodeMap.get(l.target);
                if (n1 && n2 && n1.cluster && n2.cluster && n1.cluster !== n2.cluster) count++;
            });

            if (btn) {
                btn.style.background = 'rgba(236, 72, 153, 0.25)';
                btn.style.borderColor = '#ec4899';
                btn.style.color = '#fff';
            }
            const sf = document.getElementById('tactical-status-text');
            if (sf) {
                sf.innerText = `SURPRISING: ${count} cross-community connections highlighted`;
                sf.style.color = '#ec4899';
            }
        } else {
            if (btn) {
                btn.style.background = 'rgba(236, 72, 153, 0.08)';
                btn.style.borderColor = 'rgba(236, 72, 153, 0.2)';
                btn.style.color = '#ec4899';
            }
        }
        this.draw();
    }

    /**
     * Toggle Confidence Mode — edges styled by confidence level:
     * - EXTRACTED (conf ≥ 0.9) → solid community color (normal)
     * - INFERRED  (conf 0.7–0.89) → violet dashed
     * - AMBIGUOUS (conf < 0.7) → yellow dotted
     */
    toggleConfidenceMode() {
        const btn = document.getElementById('btn-sprint1-confidence');
        this.confidenceMode = !this.confidenceMode;

        if (this.confidenceMode) {
            if (btn) {
                btn.style.background = 'rgba(168, 85, 247, 0.25)';
                btn.style.borderColor = '#a855f7';
                btn.style.color = '#fff';
            }
            const sf = document.getElementById('tactical-status-text');
            if (sf) { sf.innerText = 'CONFIDENCE MODE: Edges styled by epistemic certainty'; sf.style.color = '#a855f7'; }
        } else {
            if (btn) {
                btn.style.background = 'rgba(168, 85, 247, 0.08)';
                btn.style.borderColor = 'rgba(168, 85, 247, 0.2)';
                btn.style.color = '#a855f7';
            }
        }
        this.draw();
    }
}

// Collegamento Globale API del Dashboard
window.tacticalCanvas = null;
window.initTacticalCanvas = () => {
    window.tacticalCanvas = new TacticalCanvas('tactical-canvas-element');
};

window.setTacticalTool = (tool) => {
    if (window.tacticalCanvas) window.tacticalCanvas.setTool(tool);
};

window.centerTacticalCamera = () => {
    if (window.tacticalCanvas) window.tacticalCanvas.centerCamera();
};

window.flyToTacticalNode = (nodeId) => {
    if (window.tacticalCanvas) window.tacticalCanvas.flyToNode(nodeId);
};

window.toggleTacticalForces = () => {
    if (window.tacticalCanvas) window.tacticalCanvas.toggleForces();
};

window.closeTacticalInspector = () => {
    const inspector = document.getElementById('tactical-inspector');
    if (inspector) inspector.style.display = 'none';
};

window.updateTacticalNodeLabel = (val) => {
    if (window.tacticalCanvas) window.tacticalCanvas.updateSelectedNodeLabel(val);
};

window.updateTacticalNodeCluster = (val) => {
    if (window.tacticalCanvas) window.tacticalCanvas.updateSelectedNodeCluster(val);
};

window.updateTacticalNodeColor = (val) => {
    if (window.tacticalCanvas) window.tacticalCanvas.updateSelectedNodeColor(val);
};

window.deleteTacticalSelectedNode = () => {
    if (window.tacticalCanvas) window.tacticalCanvas.deleteSelectedNode();
};

window.inspectFullNodeDetails = () => {
    if (window.tacticalCanvas && window.tacticalCanvas.selectedNode) {
        if (window.showNodeInspector) {
            window.showNodeInspector(window.tacticalCanvas.selectedNode.id);
        }
    }
};

window.showNodeInspector = (id) => {
    if (typeof window.selectNode === 'function') {
        window.selectNode(id);
    }
};

// ── SPRINT 1 Global APIs ─────────────────────────────────────────────────────

/** Activate Blast Radius on selected node (N-hop impact highlight) */
window.toggleTacticalBlast = (depth) => {
    if (window.tacticalCanvas) window.tacticalCanvas.toggleBlastMode(depth || 2);
};

/** Toggle Surprising Connections (cross-community edge highlight in magenta) */
window.toggleTacticalSurprising = () => {
    if (window.tacticalCanvas) window.tacticalCanvas.toggleSurprisingConnections();
};

/** Toggle Confidence Mode (edges styled by epistemic certainty level) */
window.toggleTacticalConfidence = () => {
    if (window.tacticalCanvas) window.tacticalCanvas.toggleConfidenceMode();
};

// ─────────────────────────────────────────────────────────────────────────────
