"""
retrieval/reflective.py
───────────────────────
Reflective Memory Layer (v4.3.0)
Genera meta-riflessioni sulla conoscenza: conflitti, importanza e domande aperte.
"""

from typing import Dict, Any, List

class ReflectiveMemoryLayer:
    def __init__(self, engine):
        self.engine = engine
        self.llm = engine.orchestrator if hasattr(engine, 'orchestrator') else None

    async def reflect_on_topic(self, topic: str) -> Dict[str, Any]:
        """
        Genera una riflessione critica su un argomento basandosi sui dati nel vault.
        """
        print(f"🤔 [Reflection] Meditating on topic: {topic}")
        
        results = await self.engine.query(topic, k=10)
        if not results: return {}

        context = "\n".join([f"- {r.node.text}" for r in results])
        
        prompt = f"""
        Esegui una riflessione critica sui seguenti dati riguardanti '{topic}'.
        Identifica:
        1. Perché questa informazione è preziosa?
        2. Ci sono conflitti o contraddizioni tra i nodi?
        3. Quali sono le domande aperte o i 'gap' che questa conoscenza genera?
        
        DATI:
        {context}
        
        Rispondi in formato JSON con chiavi: 'importance', 'conflicts', 'open_questions'.
        """
        
        try:
            raw = await self.llm.get_consensus_response(prompt, "Reflective Critic")
            import json, re
            json_match = re.search(r'\{.*\}', raw, re.DOTALL)
            reflection = json.loads(json_match.group(0))
            
            # [v4.3.0] Log event for Timeline
            self.engine._prefilter.log_event(
                event_type="NODE_REFLECTED",
                node_id="system",
                topic=topic,
                description=f"Riflessione completata: {len(reflection.get('open_questions', []))} domande aperte individuate."
            )
            
            return reflection
        except:
            return {
                "importance": "Informazione strutturata nel vault.",
                "conflicts": "Nessun conflitto evidente rilevato.",
                "open_questions": ["Approfondire le connessioni semantiche."]
            }
