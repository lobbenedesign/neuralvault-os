/**
 * 🏺 [v9.1] SOVEREIGN WASM BRIDGE (Client-Side Simulation Core)
 * This module provides high-performance client-side causal simulations.
 * It mimics the behavior of the Rust/WASM engine for instant UI feedback.
 */

window.SovereignWASM = {
    isReady: true,
    version: "9.1.0-stochastic",

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
    }
};
