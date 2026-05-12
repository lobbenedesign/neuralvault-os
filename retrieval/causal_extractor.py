"""
retrieval/causal_extractor.py
──────────────────────────────
[v7.0] Causal Logic Engine
Estrae relazioni di causa-effetto, prevenzione e requisiti dai nodi del Vault.
"""

import json
import re
from typing import List, Dict
from index.node import RelationType, SemanticEdge

class CausalExtractor:
    def __init__(self, engine):
        self.engine = engine
        self.orchestrator = engine.orchestrator

    async def extract_causal_relations(self, node) -> List[SemanticEdge]:
        """
        Analizza il testo di un nodo e identifica relazioni causali verso altri concetti o nodi.
        """
        prompt = f"""
        Analizza questo testo e identifica relazioni LOGICHE e CAUSALI.
        
        RELAZIONI POSSIBILI:
        - CAUSES: il soggetto provoca o genera l'oggetto.
        - PREVENTS: il soggetto evita o mitiga l'oggetto.
        - REQUIRES: il soggetto necessita dell'oggetto per funzionare.
        - ENABLES: il soggetto abilita o permette l'oggetto.
        - SUPERSEDES: il soggetto sostituisce o migliora una versione precedente (oggetto).
        
        TESTO:
        "{node.text}"
        
        Rispondi SOLO in JSON:
        {{
            "relations": [
                {{
                    "target": "nome del concetto o id",
                    "type": "CAUSES|PREVENTS|REQUIRES|ENABLES|SUPERSEDES",
                    "reason": "breve spiegazione"
                }}
            ]
        }}
        """
        
        # Usiamo un modello veloce per l'estrazione
        model = self.orchestrator.settings.get("extraction_model", "llama3.2:3b")
        raw_response = await self.orchestrator.get_consensus_response(prompt, "Causal Extractor", target_model=model)
        
        causal_edges = []
        try:
            match = re.search(r'\{.*\}', raw_response, re.DOTALL)
            if match:
                data = json.loads(match.group(0))
                for rel in data.get("relations", []):
                    rel_type_str = rel["type"].upper()
                    
                    # Mapping stringa -> Enum
                    rel_type = None
                    if rel_type_str == "CAUSES": rel_type = RelationType.CAUSES
                    elif rel_type_str == "PREVENTS": rel_type = RelationType.PREVENTS
                    elif rel_type_str == "REQUIRES": rel_type = RelationType.REQUIRES
                    elif rel_type_str == "ENABLES": rel_type = RelationType.ENABLES
                    elif rel_type_str == "SUPERSEDES": rel_type = RelationType.SUPERSEDES
                    
                    if rel_type:
                        # Cerchiamo se il target è un ID esistente o un concetto
                        target_id = rel["target"]
                        # Se il target non sembra un ID, facciamo una query rapida per trovare il nodo più vicino
                        if len(target_id) < 20: 
                            search_res = await self.engine.query(target_id, k=1)
                            if search_res:
                                target_id = search_res[0].node.id
                        
                        causal_edges.append(SemanticEdge(
                            target_id=target_id,
                            relation=rel_type,
                            weight=0.9,
                            metadata={"reason": rel["reason"]}
                        ))
        except Exception as e:
            print(f"⚠️ [Causal Extraction Error] {e}")
            
        return causal_edges
