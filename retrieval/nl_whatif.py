import json
import logging
from typing import Dict, Any, Optional, List
from pydantic import BaseModel
from retrieval.aegis_bus import aegis_bus

class WhatIfParsedQuery(BaseModel):
    intervention_description: str
    target_concept: str
    direction: str # increase, decrease, change
    magnitude: str # piccolo, medio, grande, radicale
    time_horizon: str # immediate, mid_term, long_term

class NaturalLanguageWhatIf:
    """
    🧪 [v8.4] NL What-If Engine.
    Converte domande in linguaggio naturale in simulazioni stocastiche.
    """
    def __init__(self, engine):
        self.engine = engine
        self.logger = logging.getLogger("NL_WhatIf")
        self._cache = {} # 🧠 [v9.5] Semantic Cache per query identiche/simili

    async def parse_query(self, query: str) -> Optional[WhatIfParsedQuery]:
        """Usa lo sciame per estrarre i parametri della simulazione."""
        prompt = f"""
        Sei il NeuralVault Intent Parser. Converti questa domanda What-If in JSON.
        
        Domanda: "{query}"
        
        Rispondi SOLO con il JSON:
        {{
            "intervention_description": "descrizione sintetica del cambiamento",
            "target_concept": "concetto/nodo principale da modificare",
            "direction": "increase" | "decrease" | "change",
            "magnitude": "piccolo" | "medio" | "grande" | "radicale",
            "time_horizon": "immediate" | "mid_term" | "long_term"
        }}
        """
        try:
            # [v8.4 Fix] Usiamo ask_fast per evitare il blocco della Corte Suprema / Self-RAG per una banale estrazione JSON
            model_to_use = self.engine.orchestrator.settings.get("extraction") or self.engine.orchestrator.settings.get("routing", {}).get("entity_extraction") or self.engine.orchestrator.settings.get("routing", {}).get("extraction", "qwen2.5:3b")
            response = await self.engine.orchestrator.ask_fast(prompt, model=model_to_use, temp=0.1)
            
            if not response or "Error:" in response or "L'Oracolo" in response:
                self.logger.error(f"LLM Response error or timeout: {response}")
                return None
                
            # Pulizia per evitare tag markdown se presenti
            clean_res = response.strip()
            if "```json" in clean_res:
                clean_res = clean_res.split("```json")[1].split("```")[0].strip()
            elif "```" in clean_res:
                clean_res = clean_res.split("```")[1].split("```")[0].strip()
            
            # Trova l'inizio e la fine del JSON se c'è testo extra
            start_idx = clean_res.find("{")
            end_idx = clean_res.rfind("}")
            if start_idx != -1 and end_idx != -1:
                clean_res = clean_res[start_idx:end_idx+1]
            
            data = json.loads(clean_res)
            return WhatIfParsedQuery(**data)
        except Exception as e:
            self.logger.error(f"Errore nel parsing della query NL: {e} | Response: {response[:100] if 'response' in locals() else 'None'}...")
            return None

    async def run_nl_simulation(self, query: str, lenses: List[str] = ["standard"], mode: str = "FAST", horizon: str = "immediate", twin=None, parent_id: str = None, folder_path: str = None, tags: str = None) -> Dict[str, Any]:
        """Esegue l'intero pipeline dalla domanda al report narrativo, includendo le lenti archetipali."""
        source = twin if twin else self.engine
        if hasattr(self.engine.orchestrator, 'set_priority_shift'):
            self.engine.orchestrator.set_priority_shift(True)
            
        import time
        start_time = time.perf_counter()
        
        # [v8.4] Adaptive MC Configuration
        iterations = 2000 if mode == "DEEP" else 100
        max_nodes = 500 if mode == "DEEP" else 150
        
        # --- 🚀 [v11.0] PERFORMANCE BOOST: ASYNC CONSOLIDATED EXECUTION ---
        try:
            aegis_bus.emit("SIMULATION_PROGRESS", {"step": "PARSING_INTENT", "query": query})
            # 1. Parsing
            parsed = await self.parse_query(query)
            if not parsed:
                return {"error": "Non sono riuscito a interpretare la tua domanda."}
            
            # 🧠 [CACHE CHECK]
            cache_key = f"{query}_{mode}_{horizon}_{lenses}"
            if cache_key in self._cache:
                self.logger.info(f"♻️ [Cache] Hit per query: {query}")
                return self._cache[cache_key]
 
            # 2. Ricerca del nodo target
            search_res = await source.query(parsed.target_concept, k=3)
            if not search_res:
                return {"error": f"Non ho trovato informazioni su '{parsed.target_concept}' nel tuo vault."}
            
            best_node = search_res[0].node
            
            # 3. Mapping magnitudo -> intensità
            mag_map = {"piccolo": 0.2, "medio": 0.5, "grande": 0.8, "radicale": 1.0}
            base_intensity = mag_map.get(parsed.magnitude, 0.5)
            if parsed.direction == "decrease": base_intensity = -base_intensity
            
            aegis_bus.emit("SIMULATION_PROGRESS", {"step": "RUNNING_STOCHASTIC_PASSES", "target": best_node.title, "intensity": base_intensity})
            
            # 4. Multi-Horizon Execution (Parallelized v9.5)
            horizons_to_run = ["immediate", "mid_term", "long_term"] if mode == "DEEP" else [horizon]
            
            async def run_single_horizon(h):
                decay_map = {"immediate": 1.0, "mid_term": 0.7, "long_term": 0.4}
                intensity = base_intensity * decay_map.get(h, 1.0)
                return h, await self.engine.wiki.simulator.simulate_intervention(
                    best_node.id, 
                    intensity,
                    iterations=iterations // (3 if mode == "DEEP" else 1),
                    lens_ids=lenses,
                    max_nodes=max_nodes
                )

            import asyncio
            horizon_tasks = [run_single_horizon(h) for h in horizons_to_run]
            horizon_results = await asyncio.gather(*horizon_tasks)
            time_series = {h: res for h, res in horizon_results}

            # Principal result for backward compatibility
            results = time_series.get(horizon, time_series[horizons_to_run[0]])
                
            # 5. Generazione Report Narrativo via Counterfactual Arena (Consolidated v11.0)
            aegis_bus.emit("SIMULATION_PROGRESS", {"step": "COUNTERFACTUAL_ARENA", "query": query})
            
            # Chiamata Unificata all'Oracolo Decisionale (Sotto il cofano evita 3 chiamate Ollama parallele)
            unified_debate = await self.run_unified_narrative_generation(query, parsed, best_node, results)
            
            report = unified_debate.get("narrative", "")
            arena_debate = {
                "optimist_argument": unified_debate.get("optimist_argument", ""),
                "skeptic_argument": unified_debate.get("skeptic_argument", ""),
                "competitor_argument": unified_debate.get("competitor_argument", "")
            }
            
            # 6. Oracle Grade Calculation [v9.2]
            conf = results.get("overall_confidence", 0.8)
            grade = "B"
            if conf > 0.9: grade = "S"
            elif conf > 0.8: grade = "A"
            elif conf > 0.6: grade = "B"
            else: grade = "C"

            end_time = time.perf_counter()
            duration = end_time - start_time
            
            import uuid
            record_id = str(uuid.uuid4())
            
            final_res = {
                "id": record_id,
                "query": query,
                "decision_record_id": record_id,
                "parsed": parsed.dict(),
                "target_node": {"id": best_node.id, "title": best_node.title},
                "simulation": results,
                "mean_impact": results.get("mean_impact", {}),
                "affected_nodes": results.get("affected_nodes_count", len(results.get("affected_nodes", []))),
                "overall_confidence": conf,
                "oracle_grade": grade,
                "nodes": results.get("nodes", {}),
                "time_series": time_series,
                "narrative": report,
                "counterfactual_arena": arena_debate,
                "telemetry": {
                    "model": self.engine.orchestrator.settings.get("routing", {}).get("synthesis", "qwen2.5:7b"),
                    "duration": f"{duration:.2f}s",
                    "optimized": True,
                    "printing_press_v1": True
                }
            }
            
            # Avviamo la registrazione della decisione con tutti i metadata v11.0
            settings_used = {
                "lenses": lenses,
                "mode": mode,
                "horizon": horizon
            }
            await self.engine.wiki.journal.record_decision(
                final_res, 
                query, 
                best_node.id,
                settings_used=settings_used,
                parent_id=parent_id,
                folder_path=folder_path,
                tags=tags,
                record_id=record_id
            )
            
            # 🏺 [Printing Press] Persistenza dei risultati (Pre-Printing)
            try:
                self.engine.db.execute("""
                    CREATE TABLE IF NOT EXISTS preprinted_insights (
                        query_hash TEXT PRIMARY KEY,
                        results JSON,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                self.engine.db.execute(
                    "INSERT OR REPLACE INTO preprinted_insights (query_hash, results) VALUES (?, ?)",
                    (cache_key, json.dumps(final_res))
                )
            except Exception as db_e:
                self.logger.warning(f"⚠️ [Printing Press] Fallita persistenza insight: {db_e}")

            # Popolamento Cache RAM
            if len(self._cache) > 50: self._cache.clear()
            self._cache[cache_key] = final_res
            
            aegis_bus.emit("SIMULATION_COMPLETE", {"query": query, "node": best_node.title, "impacts": final_res["affected_nodes"]})
            
            return final_res
        finally:
            if hasattr(self.engine.orchestrator, 'set_priority_shift'):
                self.engine.orchestrator.set_priority_shift(False)

    async def run_unified_narrative_generation(self, query: str, parsed: WhatIfParsedQuery, node: Any, results: Dict) -> Dict[str, str]:
        """
        ⚔️ [v11.0 Performance Engine] Unified Supreme Court Deliberation
        Esegue un singolo LLM call strutturato per simulare l'arena counterfactual
        e sintetizzare il verdetto finale. Riduce la latenza del 60%.
        """
        model_used = self.engine.orchestrator.settings.get("routing", {}).get("synthesis", "qwen2.5:7b")
        top_impacts = results.get("affected_nodes", [])[:5]
        summary = "\n".join([f"- {n['title']}: {n['impact']} (Prob: {round(n['probability_positive']*100)}%)" for n in top_impacts])
        
        prompt = f"""
        ### TASK: UNIFIED DECISION SUPREME COURT CONTEXT (v11.0)
        Genera il dibattito dell'Arena Counterfactual (Ottimista, Scettico, Competitore) e il Verdetto finale in un singolo formato JSON strutturato.
        
        SCENARIO UTENTE: "{query}"
        TARGET INTERVENTO: {parsed.direction} su "{node.title}" ({parsed.magnitude}).
        ORIZZONTE TEMPORALE: {parsed.time_horizon}
        
        DATI PREVISTI DAL GRAFO CAUSALE:
        {summary}
        
        ### ISTRUZIONI RIGIDE PER IL FORMATTO:
        Rispondi ESCLUSIVAMENTE con un blocco JSON valido e strutturato esattamente come segue, senza alcun commento o testo extra prima/dopo:
        {{
            "optimist_argument": "Sintesi strategica positiva e audace (max 100 parole) focalizzata su opportunità e crescita ideale.",
            "skeptic_argument": "Sintesi di avvertimento cauta e allarmante (max 100 parole) focalizzata su rischi nascosti e cigni neri.",
            "competitor_argument": "Analisi competitiva di equilibrio strategico (max 100 parole) basata sulla teoria dei giochi e attriti di mercato.",
            "narrative": "La delibera sovrana strutturata in markdown elegante con i seguenti titoli rigorosi:\\n# 🏛️ VERDETTO DELLA SUPREME COURT\\n\\n## 🔮 1. DELIBERA PROBABILISTICA\\n[Analisi autorevole del dibattito e sintesi probabilistica dell'esito]\\n\\n## ⚡ 2. EFFETTI COLLATERALI & REAZIONI DEL GRAFO\\n[Discussione degli impatti collaterali e cascate semantiche]\\n\\n## 🛡️ 3. RISK MITIGATION & BLACK SWAN\\n[Misure preventive e gestione cigni neri]\\n\\n## 🏺 4. DISPOSIZIONE SOVRANA\\n[Raccomandazione finale azionabile per il decisore]"
        }}
        """
        
        try:
            response = await self.engine.orchestrator.ask_fast(prompt, model=model_used, temp=0.4)
            clean_res = response.strip()
            
            # Pulizia markdown tag
            if clean_res.startswith("```json"):
                clean_res = clean_res[7:-3].strip()
            elif clean_res.startswith("```"):
                clean_res = clean_res[3:-3].strip()
                
            start_idx = clean_res.find("{")
            end_idx = clean_res.rfind("}")
            if start_idx != -1 and end_idx != -1:
                clean_res = clean_res[start_idx:end_idx+1]
                
            data = json.loads(clean_res)
            return data
        except Exception as e:
            self.logger.error(f"⚠️ [Unified Narrative] Errore unificazione o parsing JSON: {e}")
            return {
                "optimist_argument": "Simulazione ottimista fallita.",
                "skeptic_argument": f"Errore locale: {e}",
                "competitor_argument": "Simulazione competitiva fallita.",
                "narrative": f"# 🏛️ VERDETTO DELLA SUPREME COURT\n\n## 🔮 1. ERROR\nNon è stato possibile completare il verdetto della corte: {e}"
            }

    async def run_counterfactual_arena(self, query: str, parsed: WhatIfParsedQuery, node: Any, results: Dict) -> Dict[str, str]:
        """[Backward Compatibility Wrapper]"""
        unified = await self.run_unified_narrative_generation(query, parsed, node, results)
        return {
            "optimist_argument": unified.get("optimist_argument", ""),
            "skeptic_argument": unified.get("skeptic_argument", ""),
            "competitor_argument": unified.get("competitor_argument", "")
        }

    async def _generate_nl_report(self, query: str, parsed: WhatIfParsedQuery, node: Any, results: Dict, arena_debate: Dict[str, str]) -> str:
        """[Backward Compatibility Wrapper]"""
        unified = await self.run_unified_narrative_generation(query, parsed, node, results)
        return unified.get("narrative", "")


