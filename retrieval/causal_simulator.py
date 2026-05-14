import logging
import json
from typing import List, Dict, Any, Optional
from index.node import RelationType
import numpy as np
from enum import Enum
from utils.qmc_sampler import QuasiMonteCarloSampler

class SimulationMode(str, Enum):
    STANDARD = "standard"
    ANTIFRAGILITY = "antifragility"    # Trova nodi che beneficiano del caos
    CONFLICT = "conflict"              # Scontro tra agenti (Game Theory)
    EROSION = "erosion"                # Impatto di info false (Poisoning)
    RETRO_CAUSAL = "retro_causal"      # Dagli effetti alle cause
    BLACK_SWAN = "black_swan"          # Eventi estremi

class CausalSimulator:
    """
    🧪 [v8.3] Phase 8: The Sovereign Oracle.
    Simula scenari complessi: Antifragilità, Conflitto, Erosione e Retro-Causalità.
    """
    def __init__(self, engine):
        self.engine = engine
        self.logger = logging.getLogger("CausalSimulator")
        from retrieval.scenario_writer import SovereignScenarioWriter
        self.writer = SovereignScenarioWriter(engine)
        self._local_node_cache = {}

    async def generate_causal_scenario(self, 
                                     simulation_results: Dict[str, Any], 
                                     lens_id: str = "musk",
                                     horizon: str = "immediate",
                                     parent_scenario_id: Optional[str] = None) -> Dict[str, Any]:
        """
        🚀 [v8.2] Genera un report narrativo avanzato usando la E2P Pipeline e le Lenti Cognitive.
        """
        return await self.writer.generate_causal_chapter(
            simulation_results=simulation_results, 
            lens_id=lens_id,
            horizon=horizon,
            parent_scenario_id=parent_scenario_id
        )

    async def simulate_intervention(self, 
                                     start_node_id: str, 
                                     intervention_value: float = 1.0, 
                                     depth: int = 3, 
                                     iterations: int = 1000, 
                                     lens_ids: List[str] = ["standard"],
                                     mode: SimulationMode = SimulationMode.STANDARD,
                                     adversary_node_id: Optional[str] = None,
                                     max_nodes: int = 200) -> Dict[str, Any]:
        """
        🚀 [v8.4] Sovereign Oracle Engine (Optimized).
        Esegue simulazioni avanzate con Targeted Subgraph Extraction.
        """
        self.logger.info(f"Avvio simulazione {mode} su {start_node_id} (Max Nodes: {max_nodes})")
        
        combined_weights = self._fuse_lenses(lens_ids)
        subgraph = self._get_relevant_subgraph(start_node_id, depth, max_nodes=max_nodes)

        
        if mode == SimulationMode.ANTIFRAGILITY:
            return await self._run_antifragility_test(start_node_id, subgraph, depth, iterations, combined_weights)
        
        if mode == SimulationMode.CONFLICT and adversary_node_id:
            return await self._run_conflict_simulation(start_node_id, adversary_node_id, subgraph, depth, iterations, combined_weights)
            
        if mode == SimulationMode.EROSION:
            return await self._run_erosion_simulation(start_node_id, subgraph, depth, iterations, combined_weights)

        if mode == SimulationMode.RETRO_CAUSAL:
            return await self._run_retro_causal_search(start_node_id, depth)

        # Default: Standard Monte Carlo (Accelerato Rust)
        return await self._run_deep_monte_carlo(start_node_id, intervention_value, subgraph, depth, iterations, combined_weights)

    def _fuse_lenses(self, lens_ids: List[str]) -> Dict[str, float]:
        """Combina i pesi di più lenti cognitive."""
        from retrieval.cognitive_lenses import CognitiveLens
        lenses = CognitiveLens()
        
        fused = {"risk": 1.0, "opportunity": 1.0, "disruption": 1.0, "stability": 1.0}
        
        for lid in lens_ids:
            l_weights = lenses.get_lens_weights(lid)
            for k, v in l_weights.items():
                fused[k] = fused.get(k, 1.0) * v
                
        return fused

    def _run_analytical_pass(self, start_id: str, start_val: float, subgraph: Dict, depth: int, lens_weights: Dict) -> Dict[str, Any]:
        """Propagazione analitica deterministica per feedback immediato."""
        impacts = {start_id: start_val}
        queue = [(start_id, start_val, 0)]
        
        while queue:
            nid, val, d = queue.pop(0)
            if d >= depth: continue
            
            edges = subgraph.get(nid, [])
            for edge in edges:
                # Applica i pesi della lente al legame
                l_mod = lens_weights.get("stability", 1.0) if str(edge.relation) == "prevents" else lens_weights.get("disruption", 1.0)
                effective_weight = (edge.weight or 0.5) * l_mod
                
                # [v8.4] Robust string comparison to avoid Enum sync issues
                rel_val = str(edge.relation).split('.')[-1]
                effect = val * effective_weight if rel_val != "prevents" else -val * effective_weight
                if abs(effect) > 0.01:
                    impacts[edge.target_id] = impacts.get(edge.target_id, 0.0) + effect
                    queue.append((edge.target_id, effect, d + 1))
        
        return self._format_results(start_id, impacts, 1, subgraph=subgraph)

    async def _run_deep_monte_carlo(self, start_id: str, val: float, subgraph: Dict, depth: int, iterations: int, lens_weights: Dict) -> Dict[str, Any]:
        """Esegue il calcolo stocastico pesante, con accelerazione Rust se disponibile."""
        try:
            from neuralvault_rs import run_stochastic_simulation_rs
            
            # Formattazione dati per Rust: HashMap<String, Vec<(String, f32)>>
            rust_graph = {}
            for nid, edges in subgraph.items():
                rust_graph[nid] = []
                for e in edges:
                    # Applica lens weights già qui per semplicità o passa al Rust
                    rel_val = str(e.relation).split('.')[-1]
                    l_mod = lens_weights.get("stability", 1.0) if rel_val == "prevents" else lens_weights.get("disruption", 1.0)
                    w = (e.weight or 0.5) * l_mod
                    if rel_val == "prevents":
                        w = -w
                    rust_graph[nid].append((e.target_id, w))
            
            self.logger.info(f"🏎️ [Accelerazione Rust] Avvio simulazione Monte Carlo ({iterations} iterazioni)...")
            stats = run_stochastic_simulation_rs(
                start_id, 
                val, 
                rust_graph, 
                iterations, 
                depth, 
                0.1 # Noise level
            )
            
            return self._format_rust_results(start_id, stats, iterations, subgraph=subgraph)
            
        except ImportError:
            self.logger.warning("⚠️ Rust extension not found. Falling back to Python (Sobol Optimized).")
            all_outcomes = []
            
            # [v9.0] Phase D: Sobol-Owen Optimization
            # Generate QMC noise for all iterations upfront to ensure low-discrepancy coverage
            qmc_sampler = QuasiMonteCarloSampler(dimension=1)
            sobol_noise = qmc_sampler.get_samples(iterations).flatten()
            
            for i in range(iterations):
                # We pass the i-th Sobol sample to the pass
                outcome = self._run_single_stochastic_pass(start_id, val, subgraph, depth, lens_weights, noise_seed=sobol_noise[i])
                all_outcomes.append(outcome)
            return self._format_results(start_id, all_outcomes, iterations, subgraph=subgraph)

    def _format_rust_results(self, root_id: str, stats: Dict, iterations: int, subgraph: Dict = None) -> Dict[str, Any]:
        formatted = []
        for nid, (mean, std, prob_pos) in stats.items():
            node = self.engine.get_node(nid)
            formatted.append({
                "id": nid,
                "title": node.title if node else nid,
                "impact": round(float(mean), 3),
                "std": round(float(std), 3),
                "probability_positive": round(float(prob_pos), 2),
                "type": node.metadata.get("type", "concept") if node else "concept"
            })
        
        # [v8.4] Export edges for UI Graph
        formatted_edges = []
        if subgraph:
            for source_id, edges in subgraph.items():
                for e in edges:
                    formatted_edges.append({
                        "source": source_id,
                        "target": e.target_id,
                        "relation": str(e.relation).split('.')[-1]
                    })

        return {
            "root_node": root_id,
            "iterations": iterations,
            "affected_nodes": sorted(formatted, key=lambda x: abs(x["impact"]), reverse=True),
            "edges": formatted_edges
        }


    def _format_results(self, root_id: str, data: Any, iterations: int, subgraph: Dict = None) -> Dict[str, Any]:
        """Analisi statistica e formattazione standard dei risultati."""
        results = []
        
        if isinstance(data, list): # Monte Carlo
            affected_ids = set().union(*[o.keys() for o in data])
            for nid in affected_ids:
                impacts = [o.get(nid, 0.0) for o in data]
                mean_impact = np.mean(impacts)
                node = self.engine.get_node(nid)
                results.append({
                    "id": nid,
                    "title": node.title if node else nid,
                    "impact": round(float(mean_impact), 3),
                    "std": round(float(np.std(impacts)), 3),
                    "worst_case": round(float(np.percentile(impacts, 5)), 3),
                    "best_case": round(float(np.percentile(impacts, 95)), 3),
                    "probability_positive": round(float(np.mean([i > 0 for i in impacts])), 3),
                    "intensity": abs(float(mean_impact))
                })
        else: # Analytical
            for nid, val in data.items():
                node = self.engine.get_node(nid)
                results.append({
                    "id": nid,
                    "title": node.title if node else nid,
                    "impact": round(float(val), 3),
                    "std": 0.0,
                    "worst_case": round(float(val), 3),
                    "best_case": round(float(val), 3),
                    "probability_positive": 1.0 if val > 0 else 0.0,
                    "intensity": abs(float(val))
                })
                
        # [v8.4] Export edges for UI Graph
        formatted_edges = []
        if subgraph:
            for source_id, edges in subgraph.items():
                for e in edges:
                    formatted_edges.append({
                        "source": source_id,
                        "target": e.target_id,
                        "relation": str(e.relation).split('.')[-1]
                    })

        return {
            "root_id": root_id,
            "iterations": iterations,
            "affected_nodes": sorted(results, key=lambda x: x["intensity"], reverse=True),
            "edges": formatted_edges
        }


    def _get_relevant_subgraph(self, start_id: str, depth: int, max_nodes: int = 200) -> Dict[str, List[Any]]:
        """
        [v8.4] Targeted Subgraph Extraction.
        Estrae i nodi e gli archi nel raggio d'azione limitando la dimensione per efficienza.
        """
        subgraph = {}
        queue = [(start_id, 0)]
        visited = {start_id}
        node_count = 0
        
        while queue and node_count < max_nodes:
            nid, d = queue.pop(0)
            if d >= depth: continue
            
            node = self._local_node_cache.get(nid) or self.engine.get_node(nid)
            if not node: continue
            self._local_node_cache[nid] = node
            
            subgraph[nid] = node.edges
            node_count += 1
            
            for edge in node.edges:
                if edge.target_id not in visited:
                    visited.add(edge.target_id)
                    queue.append((edge.target_id, d + 1))
                    
        self.logger.info(f"📊 [Subgrafo] Estratti {len(subgraph)} nodi per la simulazione.")
        return subgraph


    async def interview_node(self, node_id: str, simulation_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        🧪 [v12.7] Sovereign Interview (PG-RAG): Intervista identitaria certificata.
        Spostiamo il focus dalla narrativa alla causalità documentale.
        """
        node = self.engine.get_node(node_id)
        if not node: return {"error": "Nodo non trovato"}
        
        # 🎭 [PG-RAG] Recupero evidenze comportamentali (Lexicon, Obligations, Precedents)
        persona_data = {"OBLIGATIONS": [], "PRECEDENTS": [], "LEXICON": []}
        if hasattr(self.engine, 'agent007'):
            res = self.engine.agent007.execute("SELECT category, content FROM agent007_personas WHERE entity_id = ?", (node.title or node_id,)).fetchall()
            for cat, content in res:
                if cat in persona_data: persona_data[cat].append(content)

        impact_data = next((n for n in simulation_context.get("affected_nodes", []) if n["id"] == node_id), None)
        impact_val = impact_data["impact"] if impact_data else 0.0
        
        prompt = f"""
        ### IDENTITY PROTOCOL: PG-RAG
        ### SUBJECT: "{node.title or node_id}"
        ### BEHAVIORAL ANCHORS:
        - OBLIGATIONS: {persona_data['OBLIGATIONS']}
        - PRECEDENTS: {persona_data['PRECEDENTS']}
        - LEXICON: {persona_data['LEXICON']}
        
        ### CONTEXT:
        Contenuto: {node.text[:500]}
        Impatto Simulato: {impact_val} (Target: {simulation_context.get('root_id')})
        
        ### TASK:
        Reagisci all'impatto mantenendo la coerenza con i tuoi vincoli contrattuali e precedenti storici.
        Usa lo STILE SITREP: Conciso, professionale, zero aggettivi emotivi, focus su impatto e probabilità.
        Rispondi in prima persona come se fossi l'entità.
        """
        
        # Utilizziamo lo sciame per generare la risposta
        response = await self.engine.orchestrator.get_consensus_response(prompt, f"Node Interview: {node.title or node_id}")
        
        return {
            "node_id": node_id,
            "title": node.title or node_id,
            "impact": impact_val,
            "response": response
        }

    async def generate_strategic_report(self, simulation_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        🏺 [v12.7] SITREP Intelligence Report.
        Genera un report deterministico, ancorato alle prove e privo di narrativa "fiction".
        """
        affected = simulation_results.get('affected_nodes', [])
        summary = f"SOURCE_TRIGGER: {simulation_results.get('root_id')}\n"
        summary += f"RELEVANT_SUBGRAPH_SIZE: {len(affected)}\n\n"
        
        evidence_ids = [n['id'] for n in affected[:10]]
        
        for n in affected[:5]:
            summary += f"ENTITY: {n['title']} (ID: {n['id']}) | IMPACT: {n['impact']} | CONFIDENCE: {n.get('probability_positive', 0.5)*100}%\n"
            
        prompt = f"""
        ### PROTOCOL: SOVEREIGN SITREP (v12.7)
        ### DATA_STREAM:
        {summary}
        
        ### GUIDELINES:
        1. Stile Intelligence Militare: Linguaggio passivo, conciso, assenza di aggettivi emotivi.
        2. Focus su Soglie di Attivazione Causale (Trigger Thresholds).
        3. Identifica impatti di 2° e 3° grado (Cascading Failures).
        4. OGNI affermazione o entità citata DEVE essere seguita dal suo [ID] (es: "Aumento dei tassi [node_123]").
        5. Ogni conclusione deve essere ancorata ai dati forniti.
        
        ### STRUCTURE:
        1. SITUATION (Overview deterministica)
        2. OPERATIONAL IMPACTS (Grado 1, 2, 3)
        3. THREATS & VULNERABILITIES
        4. RECOMMENDED ACTIONABLE STEPS
        """
        
        report = await self.engine.orchestrator.get_consensus_response(prompt, "Sovereign SITREP Engine")
        
        # [v12.7] Emit Aegis Event for Audit-Grade Tracking
        from retrieval.aegis_bus import aegis_bus
        aegis_bus.emit("SITREP_GENERATED", {
            "root_id": simulation_results.get('root_id'),
            "affected_nodes_count": len(affected),
            "evidence_ids": evidence_ids
        })
        
        return {
            "report": report,
            "evidence_ids": evidence_ids
        }

    def _run_single_stochastic_pass(self, start_id: str, start_val: float, subgraph: Dict, depth: int, lens_weights: Dict, noise_seed: float = None) -> Dict[str, float]:
        """Esegue un singolo passaggio di propagazione con rumore (Sobol/Pseudo) e lenti."""
        # Se noise_seed è presente (0-1), lo usiamo per determinare il rumore iniziale
        if noise_seed is not None:
            initial_noise = (noise_seed - 0.5) * 0.1 # Scostamento [-0.05, 0.05]
            noisy_start = start_val + initial_noise
        else:
            noisy_start = start_val + np.random.normal(0, 0.05)
            
        impacts = {start_id: noisy_start}
        queue = [(start_id, noisy_start, 0)]
        
        while queue:
            nid, val, d = queue.pop(0)
            if d >= depth: continue
            
            edges = subgraph.get(nid, [])
            for edge in edges:
                # Applica rumore stocastico (Usa noise_seed per coerenza se disponibile)
                if noise_seed is not None:
                    # Deriviamo un rumore locale deterministico dal seed globale
                    # In una versione più avanzata useremmo una dimensione Sobol per ogni arco
                    edge_noise = (hashlib.md5(f"{nid}_{edge.target_id}_{noise_seed}".encode()).digest()[0] / 255.0 - 0.5) * 0.2
                else:
                    edge_noise = np.random.normal(0, 0.1)
                
                # [v8.4] Defensive relation check
                rel_str = str(edge.relation).split('.')[-1].lower()
                
                l_mod = lens_weights.get("stability", 1.0) if rel_str == "prevents" else lens_weights.get("disruption", 1.0)
                effective_weight = max(0, min(1, ((edge.weight or 0.5) + edge_noise) * l_mod))
                
                effect = 0
                if rel_str == "causes":
                    effect = val * effective_weight
                elif rel_str == "prevents":
                    effect = -val * effective_weight
                elif rel_str == "enhances":
                    effect = val * (effective_weight * 0.5)
                
                if effect != 0:
                    impacts[edge.target_id] = impacts.get(edge.target_id, 0.0) + effect
                    queue.append((edge.target_id, effect, d + 1))
                    
        return impacts

    async def _run_antifragility_test(self, start_id: str, subgraph: Dict, depth: int, iterations: int, weights: Dict) -> Dict[str, Any]:
        """[v8.3] Cerca nodi che hanno un impatto POSITIVO quando il nodo radice subisce un colpo NEGATIVO."""
        negative_res = await self._run_deep_monte_carlo(start_id, -1.0, subgraph, depth, iterations, weights)
        antifragile_nodes = []
        for n in negative_res["affected_nodes"]:
            if n["impact"] > 0.05: # Guadagna dal disastro
                n["antifragility_score"] = round(n["impact"] * (1 - n["std"]), 3)
                antifragile_nodes.append(n)
        
        negative_res["affected_nodes"] = sorted(antifragile_nodes, key=lambda x: x["antifragility_score"], reverse=True)
        negative_res["mode"] = "ANTIFRAGILITY"
        return negative_res

    async def _run_conflict_simulation(self, start_id: str, adversary_id: str, subgraph: Dict, depth: int, iterations: int, weights: Dict) -> Dict[str, Any]:
        """[v8.3] Simula lo scontro tra due volontà nel grafo."""
        # 1. Recupero sottografo allargato che includa entrambi gli attori
        full_subgraph = self._get_relevant_subgraph(start_id, depth)
        full_subgraph.update(self._get_relevant_subgraph(adversary_id, depth))
        
        # 2. Esecuzione simultanea (o sequenziale accelerata)
        res_a = await self._run_deep_monte_carlo(start_id, 1.0, full_subgraph, depth, iterations, weights)
        res_b = await self._run_deep_monte_carlo(adversary_id, 1.0, full_subgraph, depth, iterations, weights)
        
        # 3. Conflict Kernel: Sottrazione degli impatti
        conflict_map = {n["id"]: n for n in res_a["affected_nodes"]}
        for n_b in res_b["affected_nodes"]:
            if n_b["id"] in conflict_map:
                conflict_map[n_b["id"]]["impact"] -= n_b["impact"]
                conflict_map[n_b["id"]]["conflict_intensity"] = abs(n_b["impact"])
            else:
                n_b["impact"] = -n_b["impact"] # L'avversario rema contro
                conflict_map[n_b["id"]] = n_b
        
        res_a["affected_nodes"] = sorted(conflict_map.values(), key=lambda x: abs(x["impact"]), reverse=True)
        res_a["mode"] = "CONFLICT"
        res_a["adversary"] = adversary_id
        return res_a

    async def _run_erosion_simulation(self, start_id: str, subgraph: Dict, depth: int, iterations: int, weights: Dict) -> Dict[str, Any]:
        """[v8.3] Simula la propagazione di una informazione 'tossica' o falsa."""
        # In modalità erosione aumentiamo l'incertezza (noise)
        weights["disruption"] = weights.get("disruption", 1.0) * 2.0 
        res = await self._run_deep_monte_carlo(start_id, 1.0, subgraph, depth, iterations, weights)
        
        for n in res["affected_nodes"]:
            n["contamination_risk"] = round(abs(n["impact"]) * (1 + n["std"]), 3)
            
        res["affected_nodes"] = sorted(res["affected_nodes"], key=lambda x: x["contamination_risk"], reverse=True)
        res["mode"] = "EROSION"
        return res

    async def _run_retro_causal_search(self, target_id: str, depth: int) -> Dict[str, Any]:
        """[v8.3] Analisi a ritroso: quali nodi devono essere attivati per influenzare il target?"""
        # Dobbiamo invertire il grafo (reverse edges)
        reverse_impacts = {}
        queue = [(target_id, 1.0, 0)]
        
        while queue:
            nid, weight, d = queue.pop(0)
            if d >= depth: continue
            
            # Cerchiamo chi punta a nid
            # Nota: in un grafo reale dovremmo avere un indice inverso. 
            # Qui cerchiamo tra tutti i nodi caricati (approssimazione)
            for potential_cause_id, node in self._local_node_cache.items():
                for edge in getattr(node, 'edges', []):
                    if edge.target_id == nid:
                        rev_weight = weight * edge.weight
                        reverse_impacts[potential_cause_id] = reverse_impacts.get(potential_cause_id, 0.0) + rev_weight
                        queue.append((potential_cause_id, rev_weight, d + 1))
        
        formatted = []
        for nid, imp in reverse_impacts.items():
            node = self.engine.get_node(nid)
            formatted.append({
                "id": nid,
                "title": node.title if node else nid,
                "strategic_relevance": round(imp, 3),
                "type": "required_cause"
            })
            
        return {
            "target_node": target_id,
            "mode": "RETRO_CAUSAL",
            "affected_nodes": sorted(formatted, key=lambda x: x["strategic_relevance"], reverse=True)
        }

    async def simulate_across_time(self, start_id: str, val: float) -> Dict[str, Any]:
        """[v8.1] Simula l'impatto su 3 orizzonti temporali (1m, 6m, 12m)."""
        horizons = {
            "immediate": 1.0,
            "mid_term": 0.7,  # Decadimento semantico
            "long_term": 0.4
        }
        
        results = {}
        for h_name, decay in horizons.items():
            # Eseguiamo una simulazione Monte Carlo per ogni orizzonte con decadimento
            results[h_name] = await self.simulate_intervention(start_id, val * decay, iterations=50)
            
        return results

    async def calculate_causal_gradient(self, target_id: str, desired_impact: float = 1.0) -> Dict[str, Any]:
        """
        📐 [v9.1] CAUSAL GRADIENT DESCENT.
        Trova la minima variazione necessaria per influenzare il target verso il valore desiderato.
        """
        self.logger.info(f"📐 Calcolo Causal Gradient per Target: {target_id} (Desired: {desired_impact})")
        
        # 1. Identifica i potenziali driver (nodi che influenzano il target)
        drivers = await self._run_retro_causal_search(target_id, depth=3)
        potential_drivers = drivers.get("affected_nodes", [])[:10] # Top 10 driver
        
        gradients = []
        for driver in potential_drivers:
            did = driver["id"]
            # Calcoliamo la sensibilità: delta_target / delta_driver
            # Eseguiamo due micro-simulazioni per calcolare il gradiente locale
            s1 = await self.simulate_intervention(did, intervention_value=0.1, iterations=100)
            s2 = await self.simulate_intervention(did, intervention_value=0.2, iterations=100)
            
            impact1 = next((n["impact"] for n in s1["affected_nodes"] if n["id"] == target_id), 0.0)
            impact2 = next((n["impact"] for n in s2["affected_nodes"] if n["id"] == target_id), 0.0)
            
            # Gradiente = (d_target) / (d_driver)
            local_gradient = (impact2 - impact1) / 0.1
            
            if abs(local_gradient) > 0.001:
                # Intervento necessario = Desired / Gradiente
                required_intervention = desired_impact / local_gradient
                gradients.append({
                    "driver_id": did,
                    "driver_title": driver["driver_title"] if "driver_title" in driver else driver["title"],
                    "sensitivity": round(local_gradient, 4),
                    "suggested_intervention": round(required_intervention, 3),
                    "efficiency_score": round(abs(local_gradient), 3)
                })
        
        return {
            "target_id": target_id,
            "desired_impact": desired_impact,
            "optimal_interventions": sorted(gradients, key=lambda x: x["efficiency_score"], reverse=True)
        }
