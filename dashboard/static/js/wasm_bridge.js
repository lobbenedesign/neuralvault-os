/**
 * 🏺 [v11.0] SOVEREIGN WASM BRIDGE (Client-Side Simulation & Physics Core)
 * This module provides high-performance client-side causal simulations and
 * WebAssembly-mimicking Force-Directed physics calculations using pre-allocated Float32Arrays.
 */

window.SovereignWASM = {
    isReady: true,
    version: "11.0.0-stochastic-physics",

    /**
     * Run an instant stochastic simulation directly in the browser.
     * @param {string} rootId - The starting node ID.
     * @param {number} value - The intervention intensity.
     * @param {Object} graph - Local subgraph (adj list).
     * @param {number} iterations - Number of passes.
     */
    runSimulation: function(rootId, value, graph, iterations = 100) {
        console.log(`🏎️ [WASM Bridge] Running client-side simulation (${iterations} iterations)...`);
        const stats = {}; // { node_id: [impacts] }

        for (let i = 0; i < iterations; i++) {
            const outcome = this._singlePass(rootId, value, graph);
            for (const [nid, imp] of Object.entries(outcome)) {
                if (!stats[nid]) stats[nid] = [];
                stats[nid].push(imp);
            }
        }

        // Aggregate results
        const results = Object.entries(stats).map(([id, impacts]) => {
            const mean = impacts.reduce((a, b) => a + b, 0) / impacts.length;
            return {
                id: id,
                impact: Number(mean.toFixed(3)),
                intensity: Math.abs(mean),
                probability_positive: impacts.filter(v => v > 0).length / impacts.length
            };
        });

        return results.sort((a, b) => b.intensity - a.intensity);
    },

    _singlePass: function(rootId, value, graph) {
        const impacts = { [rootId]: value + (Math.random() - 0.5) * 0.1 };
        const queue = [[rootId, impacts[rootId], 0]];
        const depthLimit = 3;

        while (queue.length > 0) {
            const [nid, val, d] = queue.shift();
            if (d >= depthLimit) continue;

            const edges = graph[nid] || [];
            for (const edge of edges) {
                // Stochastic edge weight
                const noise = (Math.random() - 0.5) * 0.2;
                const weight = Math.max(0, Math.min(1, (edge.weight || 0.5) + noise));
                
                let effect = 0;
                const rel = edge.relation ? edge.relation.toLowerCase() : 'causes';
                
                if (rel === 'causes') effect = val * weight;
                else if (rel === 'prevents') effect = -val * weight;
                else if (rel === 'enhances') effect = val * (weight * 0.5);

                if (Math.abs(effect) > 0.01) {
                    impacts[edge.target_id] = (impacts[edge.target_id] || 0) + effect;
                    queue.push([edge.target_id, effect, d + 1]);
                }
            }
        }
        return impacts;
    },

    // 🌌 [v11.0] High-Performance Force-Directed Physics Layout Engine (WASM-Mimicking)
    physics: {
        positions: null,  // Float32Array
        velocities: null, // Float32Array
        forces: null,     // Float32Array
        nodeIndexMap: {}, // Map node.id -> array index
        
        init: function(nodes) {
            const count = nodes.length;
            this.positions = new Float32Array(count * 3);
            this.velocities = new Float32Array(count * 3);
            this.forces = new Float32Array(count * 3);
            this.nodeIndexMap = {};
            
            for (let i = 0; i < count; i++) {
                const node = nodes[i];
                this.nodeIndexMap[node.id] = i;
                this.positions[i * 3] = node.x || 0;
                this.positions[i * 3 + 1] = node.y || 0;
                this.positions[i * 3 + 2] = node.z || 0;
                
                this.velocities[i * 3] = 0;
                this.velocities[i * 3 + 1] = 0;
                this.velocities[i * 3 + 2] = 0;
            }
            console.log(`🧠 [WASM Physics] Initialized physics arrays for ${count} nodes.`);
        },
        
        step: function(nodes, links, options = {}) {
            if (!nodes || nodes.length === 0) return;
            const count = nodes.length;
            
            // Re-initialize flat arrays if dimensions or node indices mismatch
            if (!this.positions || this.positions.length !== count * 3) {
                this.init(nodes);
            }
            
            const pos = this.positions;
            const vel = this.velocities;
            const forces = this.forces;
            const map = this.nodeIndexMap;
            
            const gravity = options.gravity !== undefined ? options.gravity : 0.005;
            const springStrength = options.springStrength !== undefined ? options.springStrength : 0.01;
            const damping = options.damping !== undefined ? options.damping : 0.90;
            const repulsion = options.repulsion !== undefined ? options.repulsion : 20000;
            const restLength = options.restLength !== undefined ? options.restLength : 50000;
            
            // 1. Reset forces
            for (let i = 0; i < count * 3; i++) {
                forces[i] = 0;
            }
            
            // 2. Compute gravity towards cluster centers and group indices by cluster for targeted repulsion
            const centers = {};
            const clusterIndices = {};
            for (let i = 0; i < count; i++) {
                const node = nodes[i];
                const cid = node.cluster_id || 'default';
                if (!centers[cid]) {
                    centers[cid] = { x: 0, y: 0, z: 0, count: 0 };
                    clusterIndices[cid] = [];
                }
                centers[cid].x += pos[i * 3];
                centers[cid].y += pos[i * 3 + 1];
                centers[cid].z += pos[i * 3 + 2];
                centers[cid].count++;
                clusterIndices[cid].push(i);
            }
            for (const cid in centers) {
                centers[cid].x /= centers[cid].count;
                centers[cid].y /= centers[cid].count;
                centers[cid].z /= centers[cid].count;
            }
            
            for (let i = 0; i < count; i++) {
                const node = nodes[i];
                const cid = node.cluster_id || 'default';
                const center = centers[cid];
                if (center) {
                    let localGravity = gravity;
                    const isGalaxyNode = (node.is_galaxy === true || (node.metadata && node.metadata.is_galaxy === true) || (node.theme && node.theme !== 'default'));
                    if (isGalaxyNode) {
                        localGravity = gravity * 0.0; // Completely zero out cluster core gravity to prevent slow inward collapse over time
                    }
                    forces[i * 3] += (center.x - pos[i * 3]) * localGravity;
                    forces[i * 3 + 1] += (center.y - pos[i * 3 + 1]) * localGravity;
                    forces[i * 3 + 2] += (center.z - pos[i * 3 + 2]) * localGravity;
                }
            }
            
            // 3. Compute attractive forces along links/edges
            if (links && links.length > 0) {
                for (let i = 0; i < links.length; i++) {
                    const link = links[i];
                    const srcIdx = map[link.source];
                    const dstIdx = map[link.target];
                    
                    if (srcIdx !== undefined && dstIdx !== undefined) {
                        const dx = pos[dstIdx * 3] - pos[srcIdx * 3];
                        const dy = pos[dstIdx * 3 + 1] - pos[srcIdx * 3 + 1];
                        const dz = pos[dstIdx * 3 + 2] - pos[srcIdx * 3 + 2];
                        
                        const dist = Math.sqrt(dx * dx + dy * dy + dz * dz) || 1.0;
                        
                        let localRestLength = restLength;
                        let localSpringStrength = springStrength;
                        
                        const srcNode = nodes[srcIdx];
                        const dstNode = nodes[dstIdx];
                        const isSrcGal = srcNode.is_galaxy === true || (srcNode.metadata && srcNode.metadata.is_galaxy === true) || (srcNode.theme && srcNode.theme !== 'default');
                        const isDstGal = dstNode.is_galaxy === true || (dstNode.metadata && dstNode.metadata.is_galaxy === true) || (dstNode.theme && dstNode.theme !== 'default');
                        
                        const isSameCluster = (srcNode.theme && srcNode.theme !== 'default' && srcNode.theme === dstNode.theme) || (srcNode.cluster_id && srcNode.cluster_id !== 'default' && srcNode.cluster_id === dstNode.cluster_id);
                        
                        if (isSrcGal && isDstGal && isSameCluster) {
                            localRestLength = restLength * 80.0; // 8000% longer connection rest length to provide an expansive structural cage
                            localSpringStrength = springStrength * 0.02; // Gentle structural cage spring to prevent floating to infinity
                        }
                        
                        const forceStrength = (dist - localRestLength) * localSpringStrength;
                        
                        const fx = (dx / dist) * forceStrength;
                        const fy = (dy / dist) * forceStrength;
                        const fz = (dz / dist) * forceStrength;
                        
                        forces[srcIdx * 3] += fx;
                        forces[srcIdx * 3 + 1] += fy;
                        forces[srcIdx * 3 + 2] += fz;
                        
                        forces[dstIdx * 3] -= fx;
                        forces[dstIdx * 3 + 1] -= fy;
                        forces[dstIdx * 3 + 2] -= fz;
                    }
                }
            }
            
            // 4. Compute local repulsion forces (stochastic sampling to remain O(N) for extreme speed!)
            // Instead of comparing all N^2 pairs, each node repels from 3 nodes in its SAME cluster, and 1 random node from the general population
            for (let i = 0; i < count; i++) {
                const nodeI = nodes[i];
                const cid = nodeI.cluster_id || 'default';
                const isGalI = (nodeI.is_galaxy === true || (nodeI.metadata && nodeI.metadata.is_galaxy === true) || (nodeI.theme && nodeI.theme !== 'default'));
                const sameClusterList = clusterIndices[cid];
                
                for (let r = 0; r < 4; r++) {
                    let j;
                    if (r < 3 && sameClusterList && sameClusterList.length > 1) {
                        // Mathematically guarantee internal galaxy pressure by repelling from own members!
                        const randIdx = Math.floor(Math.random() * sameClusterList.length);
                        j = sameClusterList[randIdx];
                    } else {
                        // General population repulsions
                        j = Math.floor(Math.random() * count);
                    }
                    
                    if (i === j) continue;
                    
                    const nodeJ = nodes[j];
                    const isGalJ = (nodeJ.is_galaxy === true || (nodeJ.metadata && nodeJ.metadata.is_galaxy === true) || (nodeJ.theme && nodeJ.theme !== 'default'));
                    
                    const dx = pos[i * 3] - pos[j * 3];
                    const dy = pos[i * 3 + 1] - pos[j * 3 + 1];
                    const dz = pos[i * 3 + 2] - pos[j * 3 + 2];
                    
                    const distSq = dx * dx + dy * dy + dz * dz || 1.0;
                    
                    let localRepulsion = repulsion;
                    let localThresholdSq = 400000000; // 20,000^2
                    
                    const mult = (window.galaxyRepulsionFactor !== undefined) ? window.galaxyRepulsionFactor : 25.0;
                    const isSameCluster = (nodeI.theme && nodeI.theme !== 'default' && nodeI.theme === nodeJ.theme) || (nodeI.cluster_id && nodeI.cluster_id !== 'default' && nodeI.cluster_id === nodeJ.cluster_id);
                    
                    if (isGalI && isGalJ && isSameCluster) {
                        localRepulsion = repulsion * mult * 1000.0; // Dynamic multiplier based on user's slider input (default 25.0x -> 25,000x repulsion!)
                        localThresholdSq = 1000000000000; // Boost repulsion active range threshold to 1,000,000^2 (1T square)
                    } else if (isGalI || isGalJ) {
                        localRepulsion = repulsion * 15.0; // Boost standard intergalactic repulsion 15x
                        localThresholdSq = 2250000000; // 47,434^2
                    }
                    
                    if (distSq < localThresholdSq) {
                        const dist = Math.sqrt(distSq);
                        const forceStrength = localRepulsion / (distSq + 1.0);
                        
                        forces[i * 3] += (dx / dist) * forceStrength;
                        forces[i * 3 + 1] += (dy / dist) * forceStrength;
                        forces[i * 3 + 2] += (dz / dist) * forceStrength;
                    }
                }
            }
            
            // 5. Update velocities and positions
            for (let i = 0; i < count; i++) {
                vel[i * 3] = (vel[i * 3] + forces[i * 3]) * damping;
                vel[i * 3 + 1] = (vel[i * 3 + 1] + forces[i * 3 + 1]) * damping;
                vel[i * 3 + 2] = (vel[i * 3 + 2] + forces[i * 3 + 2]) * damping;
                
                pos[i * 3] += vel[i * 3];
                pos[i * 3 + 1] += vel[i * 3 + 1];
                pos[i * 3 + 2] += vel[i * 3 + 2];
                
                // Write back to node objects
                nodes[i].x = pos[i * 3];
                nodes[i].y = pos[i * 3 + 1];
                nodes[i].z = pos[i * 3 + 2];
            }
        }
    }
};
