import logging
import json
from typing import List, Dict, Any, Optional
from datetime import datetime

class SovereignScenarioWriter:
    """
    🏺 [v8.2] The Causal World-Builder Engine.
    Genera narrazioni vincolate alla logica causale e agli stati temporali (Chrono-Lock).
    """
    
    def __init__(self, engine):
        self.engine = engine
        self.logger = logging.getLogger("ScenarioWriter")
        # Inizializzazione storage persistente per gli stati temporali via DuckDB
        self._init_state_vault()

    def _init_state_vault(self):
        """Crea la tabella per il locking degli stati se non esiste."""
        self.engine._prefilter.execute("""
            CREATE TABLE IF NOT EXISTS scenario_snapshots (
                scenario_id VARCHAR,
                horizon VARCHAR,
                state_blob JSON,
                content TEXT,
                timestamp TIMESTAMP DEFAULT now()
            )
        """)

    async def generate_causal_chapter(self, 
                                     simulation_results: Dict[str, Any], 
                                     horizon: str = "immediate", 
                                     lens_id: Optional[str] = None,
                                     parent_scenario_id: Optional[str] = None) -> Dict[str, Any]:
        """
        🚀 [v8.2] Genera un report narrativo con 'State Locking' per continuità cronologica.
        """
        self.logger.info(f"Generazione scenario per orizzonte: {horizon}")
        
        # 1. Recupero stato precedente (Causal Chaining)
        past_context = ""
        if parent_scenario_id:
            past_context = self._get_previous_state(parent_scenario_id)
        
        # 2. Recupero Lente Cognitiva e DNA Identità (E2P)
        from retrieval.cognitive_lenses import CognitiveLens
        lens_sys = CognitiveLens()
        lens_prompt = lens_sys.get_lens_prompt(lens_id or "standard")
        
        from retrieval.identity_miner import IdentityMiner
        miner = IdentityMiner(self.engine._prefilter)
        nodes = simulation_results.get("affected_nodes", [])
        
        persona_context = "DNA IDENTITÀ COINVOLTE:\n"
        for n in nodes[:5]:
            persona = miner.get_persona(n['title'])
            if persona:
                persona_context += f"- {n['title']}: {json.dumps(persona['fingerprint'])}\n"
        
        # 3. Costruzione Prompt con Chaining e Rails
        rails = self._build_narrative_rails(nodes)
        prompt = self._build_sovereign_prompt(nodes, rails, lens_prompt, persona_context, horizon, past_context)
        
        # 4. Generazione e Locking
        content = await self.engine.orchestrator.get_consensus_response(prompt, f"Causal Chapter: {horizon}")
        scenario_id = f"SCEN-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        self._lock_state(scenario_id, horizon, simulation_results, content)
        
        return {
            "scenario_id": scenario_id,
            "horizon": horizon,
            "content": content,
            "evidence_anchors": list(set([n.get("source", "Vault") for n in nodes if "source" in n]))[:10]
        }

    def _build_sovereign_prompt(self, nodes, rails, lens, style, horizon, past_context):
        evidence_list = "\n".join([f"- [{n['id']}] {n['title']} (Sorgente: {n.get('source', 'Vault')})" for n in nodes[:10]])
        
        chaining_clause = f"CONTESTO CRONOLOGICO PRECEDENTE (NON CONTRADDIRE):\n{past_context}" if past_context else "Questo è l'inizio della linea temporale."
        
        return f"""
        Sei il Sovereign Scenario Writer. Scrivi un report SITREP deterministico.
        
        ORIZZONTE: {horizon}
        {chaining_clause}
        
        {lens}
        {style}
        {rails}
        
        EVIDENZE DOCUMENTALI:
        {evidence_list}
        
        REGOLE:
        1. RISPETTA IL PASSATO: Integra le informazioni del contesto cronologico precedente.
        2. ANCORAGGIO: Usa solo i dati dei nodi citati. Ogni affermazione deve avere un [ID].
        3. STILE: Intelligence Strategica professionale. No aggettivi emotivi.
        """

    def _get_previous_state(self, scenario_id: str) -> str:
        """Recupera l'ultimo contenuto bloccato per garantire continuità."""
        res = self.engine._prefilter.execute(
            "SELECT content FROM scenario_snapshots WHERE scenario_id = ? ORDER BY timestamp DESC LIMIT 1", 
            (scenario_id,)
        ).fetchone()
        return res[0] if res else ""

    def _lock_state(self, scenario_id, horizon, results, content):
        """Effettua il lock persistente dello stato nel DB."""
        self.engine._prefilter.execute("""
            INSERT INTO scenario_snapshots (scenario_id, horizon, state_blob, content)
            VALUES (?, ?, ?, ?)
        """, (scenario_id, horizon, json.dumps(results), content))
        self.logger.info(f"🔒 State Locked: {scenario_id} ({horizon})")

    def _build_narrative_rails(self, nodes: List[Dict]) -> str:
        rails = "VINCOLI MATEMATICI (MATH-FIRST):\n"
        for n in nodes[:10]:
            rails += f"- {n['title']}: Impatto {round(n['impact']*100, 1)}% | Incertezza (Std): {n.get('std', 0)}\n"
        return rails
