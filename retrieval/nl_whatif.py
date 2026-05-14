import json
import logging
from typing import Dict, Any, Optional, List
from pydantic import BaseModel

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
            model_to_use = self.engine.orchestrator.settings.get("routing", {}).get("extraction", "qwen2.5:7b")
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

    async def run_nl_simulation(self, query: str, lenses: List[str] = ["standard"], mode: str = "FAST", horizon: str = "immediate", twin=None) -> Dict[str, Any]:
        """Esegue l'intero pipeline dalla domanda al report narrativo, includendo le lenti archetipali."""
        # Se viene passato un twin (CoW), usiamo quello per la ricerca dei nodi
        source = twin if twin else self.engine
        # [v8.4 Fix] Mette in pausa il Vault (Priority Shift) per liberare la CPU/RAM per la simulazione
        if hasattr(self.engine.orchestrator, 'set_priority_shift'):
            self.engine.orchestrator.set_priority_shift(True)
            
        import time
        start_time = time.perf_counter()
        
        # [v8.4] Adaptive MC Configuration
        iterations = 2000 if mode == "DEEP" else 100
        max_nodes = 500 if mode == "DEEP" else 150
        
        try:
            # 1. Parsing (Passiamo l'horizon forzato se presente nella query o dallo slider)
            parsed = await self.parse_query(query)
            if not parsed:
                return {"error": "Non sono riuscito a interpretare la tua domanda."}
            
            # Sovrascriviamo l'horizon del parser con quello dello slider se quest'ultimo è stato toccato
            if horizon: parsed.time_horizon = horizon
 
            # 2. Ricerca del nodo target (Usiamo source che può essere il twin CoW)
            search_res = await source.query(parsed.target_concept, k=3)
            if not search_res:
                return {"error": f"Non ho trovato informazioni su '{parsed.target_concept}' nel tuo vault."}
            
            best_node = search_res[0].node
            
            # 3. Mapping magnitudo -> intensità
            mag_map = {"piccolo": 0.2, "medio": 0.5, "grande": 0.8, "radicale": 1.0}
            intensity = mag_map.get(parsed.magnitude, 0.5)
            
            # [v8.4] Temporal Decay based on horizon
            decay_map = {"immediate": 1.0, "mid_term": 0.7, "long_term": 0.4}
            intensity *= decay_map.get(parsed.time_horizon, 1.0)

            if parsed.direction == "decrease":
                intensity = -intensity
                
            # 4. Esecuzione Simulazione
            results = await self.engine.wiki.simulator.simulate_intervention(
                best_node.id, 
                intensity,
                iterations=iterations,
                lens_ids=lenses,
                max_nodes=max_nodes
            )


            
            # 4.1 Registrazione nel Decision Journal (v8.4)
            record_id = await self.engine.wiki.journal.record_decision(results, query, best_node.id)
        
            # 5. Generazione Report Narrativo (Tracking del Modello)
            model_used = self.engine.orchestrator.settings.get("routing", {}).get("synthesis", "qwen2.5:7b")
            report = await self._generate_nl_report(query, parsed, best_node, results)
            
            end_time = time.perf_counter()
            duration = end_time - start_time
            
            # 🚀 LOG TELEMETRIA NEL TERMINALE
            print(f"\n🔮 [What-If] Risposta generata in {duration:.2f}s")
            print(f"🧠 Modello: {model_used}")
            # print(f"🏺 Conoscenza: {len(source._nodes) if hasattr(source, '_nodes') else 'Unknown'} nodi analizzati")
            print(f"📊 Simulazione: 1000 iterazioni stocastiche completate.\n")
        
            return {
                "query": query,
                "decision_record_id": record_id,
                "parsed": parsed.dict(),
                "target_node": {"id": best_node.id, "title": best_node.title},
                "simulation": results,
                "narrative_report": report,
                "telemetry": {
                    "model": model_used,
                    "duration": f"{duration:.2f}s",
                    "nodes_analyzed": k_nodes
                }
            }
        finally:
            # Ripristina sempre le operazioni in background al termine
            if hasattr(self.engine.orchestrator, 'set_priority_shift'):
                self.engine.orchestrator.set_priority_shift(False)

    async def _generate_nl_report(self, query: str, parsed: WhatIfParsedQuery, node: Any, results: Dict) -> str:
        top_impacts = results.get("affected_nodes", [])[:5]
        summary = "\n".join([f"- {n['title']}: {n['impact']} (Prob. Successo: {round(n['probability_positive']*100)}%)" for n in top_impacts])
        
        horizon_map = {"immediate": "Immediato", "mid_term": "Medio Termine (6 mesi)", "long_term": "Lungo Termine (1 anno+)"}
        horizon_str = horizon_map.get(parsed.time_horizon, "Immediato")

        prompt = f"""
        Sei il Sovereign Decision Intelligence Engine. Traduci questi dati tecnici in una narrazione strategica per un decisore.
        
        SCENARIO: "{query}"
        ORIZZONTE TEMPORALE: {horizon_str}
        INTERVENTO TARGET: {parsed.direction} su "{node.title}" ({parsed.magnitude}).
        
        PRINCIPALI IMPATTI RILEVATI:
        {summary}
        
        STRUTTURA DEL REPORT:
        1. 🔮 ESITO PROBABILISTICO: Qual è la tendenza dominante?
        2. ⚡ EFFETTI COLLATERALI: Quali altri concetti vengono trascinati?
        3. 🛡️ RISK MITIGATION: Qual è il "Black Swan" o il rischio di instabilità?
        4. 🏺 RACCOMANDAZIONE: Azione immediata suggerita.
        
        Usa un linguaggio professionale ma senza tecnicismi matematici eccessivi. Sii assertivo e sovrano.
        """
        model_to_use = self.engine.orchestrator.settings.get("routing", {}).get("synthesis", "qwen2.5:7b")
        return await self.engine.orchestrator.ask_fast(prompt, model=model_to_use, temp=0.4)

