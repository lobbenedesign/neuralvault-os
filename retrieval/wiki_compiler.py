"""
retrieval/wiki_compiler.py
──────────────────────────
WK-401: Semantic Compiler Agent.
Mantiene il Wiki in uno stato di 'Compounded Intelligence' tramite 
compilazione incrementale basata su Atomi Semantici (Agent007).
"""

import json
import re
import asyncio
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

class WikiCompilerAgent:
    """
    [v10.0] Agente responsabile della compilazione semantica (WK-401).
    Trasforma le entità certificate da Agent007 in atomi wiki persistenti.
    """
    def __init__(self, engine):
        self.engine = engine
        self.wiki_dir = Path(engine.data_dir) / "wiki"
        self.wiki_dir.mkdir(exist_ok=True)
        self.entities_dir = self.wiki_dir / "Entities"
        self.entities_dir.mkdir(exist_ok=True)
        self.index_file = self.wiki_dir / "index.md"
        self.log_file = self.wiki_dir / "log.md"
        
        # Inizializza file se non esistono
        if not self.index_file.exists():
            self.index_file.write_text("# 📖 Knowledge Index\n\n*Benvenuto nel centro di controllo neurale del Vault.*\n\n## Pagine Entità\n")
        if not self.log_file.exists():
            self.log_file.write_text("# 📜 Wiki Activity Log\n\nCronologia append-only della compilazione neurale.\n\n")

    async def compile_node_event(self, event):
        """Handler per l'evento ENTITIES_EXTRACTED (v10.0)."""
        node_id = event.data.get("node_id")
        entities = event.data.get("entities", [])
        relations = event.data.get("relations", [])
        
        if not node_id: return
        node = self.engine.get_node(node_id)
        if not node: return
        
        print(f"🧬 [WK-401] Avvio compilazione semantica per nodo: {node_id[:8]}")
        
        # 1. Aggiornamento Pagine Entità (Incremental Merge / Compounding)
        updated_entities = []
        for entity_data in entities:
            entity_name = entity_data.get("name")
            if not entity_name: continue
            
            # Filtriamo relazioni pertinenti a questa entità
            relevant_rels = [r for r in relations if r.get("source") == entity_name or r.get("target") == entity_name]
            
            success = await self._upsert_entity_page(entity_name, node, entity_data, relevant_rels)
            if success:
                updated_entities.append(entity_name)
            
        # 2. Aggiornamento Index e Log
        if updated_entities:
            self._update_index(updated_entities)
            self._append_log(node_id, updated_entities)

    async def _upsert_entity_page(self, entity: str, node, entity_data: Dict, relations: List[Dict]) -> bool:
        """Esegue il merge semantico (WK-401 Protocol)."""
        safe_name = "".join([c if c.isalnum() else "_" for c in entity])
        page_path = self.entities_dir / f"{safe_name}.md"
        
        existing_content = ""
        is_new = True
        if page_path.exists():
            existing_content = page_path.read_text()
            is_new = False
            
        prompt = f"""
        [WK-401: SEMANTIC COMPILATION PROTOCOL]
        Entità: {entity}
        Tipo: {entity_data.get('type', 'Unknown')}
        
        CONTENUTO ATTUALE:
        {existing_content if existing_content else "(Nuovo Atomo Semantico)"}
        
        NUOVA EVIDENZA (ID: {node.id}):
        {node.text[:1000]}
        
        RELAZIONI RILEVATE:
        {json.dumps(relations)}
        
        ISTRUZIONI:
        1. Se è una nuova pagina, crea una struttura: Executive Summary, Attributes, Relations, Evidence.
        2. Se la pagina esiste, esegui un COMPOUNDING UPDATE: aggiungi una sezione '## Aggiornamento {datetime.now().strftime('%d/%m/%Y')}' o integra i dati.
        3. Mantieni lo stile professionale di NeuralVault.
        4. Cita sempre: [CITE:{node.id}].
        5. Restituisci SOLO il Markdown.
        """
        
        try:
            wiki_model = self.engine.orchestrator.settings.get("wiki_model", "qwen2.5:7b")
            new_markdown = await self.engine.orchestrator.get_consensus_response(prompt, f"Wiki Compiler: {entity}", target_model=wiki_model)
            
            # Se è nuova, aggiungiamo il frontmatter
            if is_new:
                header = f"---\nid: \"{node.id}\"\ntitle: \"{entity}\"\nnamespace: \"Entities\"\nversion: \"1.0.0\"\n---\n\n"
                new_markdown = header + new_markdown

            page_path.write_text(new_markdown)
            # Epistemic Hardening
            await self._record_epistemic_claims(entity, new_markdown, node.id)
            return True
        except Exception as e:
            print(f"⚠️ [WK-401] Errore compilazione '{entity}': {e}")
            return False

    async def _extract_entities(self, text: str) -> List[str]:
        """Usa l'LLM locale per identificare le entità dominanti."""
        if not text: return []
        
        prompt = f"""
        Analizza questo frammento di conoscenza ed estrai le 3 entità principali (Persone, Progetti, Tecnologie o Organizzazioni).
        TEXT: {text[:800]}
        
        Restituisci SOLO un array JSON di stringhe.
        Esempio: ["GSE", "Contratto EPC", "Andrej Karpathy"]
        """
        try:
            # Usa il modello veloce per NER
            res = await self.engine.orchestrator.get_consensus_response(prompt, "Entity Extractor", target_model="llama3.2:3b")
            match = re.search(r'\[.*\]', res, re.DOTALL)
            if match:
                return json.loads(match.group(0))
        except: pass
        return []

    async def _upsert_entity_page(self, entity: str, node) -> bool:
        """Esegue il merge semantico della nuova informazione in una pagina esistente."""
        safe_name = "".join([c if c.isalnum() else "_" for c in entity])
        page_path = self.entities_dir / f"{safe_name}.md"
        
        existing_content = ""
        if page_path.exists():
            existing_content = page_path.read_text()
            
        prompt = f"""
        [WK-001: SEMANTIC MERGE PROTOCOL]
        Entità: {entity}
        
        CONTENUTO ATTUALE:
        {existing_content if existing_content else "(Pagina vuota)"}
        
        NUOVA EVIDENZA (ID: {node.id}):
        {node.text}
        
        ISTRUZIONI:
        1. Aggiorna la pagina integrando la nuova evidenza in modo fluido.
        2. Se ci sono nuove date o milestone, aggiorna la cronologia.
        3. Se la nuova evidenza CONTRADDICE il contenuto attuale, evidenzialo in una sezione 'Evoluzione/Contraddizioni'.
        4. Cita sempre la fonte usando [CITE:{node.id}].
        5. Restituisci SOLO il Markdown completo e pulito.
        """
        
        try:
            wiki_model = self.engine.orchestrator.settings.get("wiki_model", "qwen2.5:7b")
            new_markdown = await self.engine.orchestrator.get_consensus_response(prompt, f"Wiki Compiler: {entity}", target_model=wiki_model)
            
            page_path.write_text(new_markdown)
            # [v10.0] Epistemic Hardening: Extract and save claims
            await self._record_epistemic_claims(entity, new_markdown, node.id)
            return True
        except Exception as e:
            print(f"⚠️ [WK-001] Errore merge '{entity}': {e}")
            return False

    def _update_index(self, entities: List[str]):
        """Aggiorna index.md con collegamenti alle nuove pagine."""
        content = self.index_file.read_text()
        for entity in entities:
            safe_name = "".join([c if c.isalnum() else "_" for c in entity])
            link = f"- [[{entity}]] (Entities/{safe_name}.md)"
            if link not in content:
                content += f"{link}\n"
        self.index_file.write_text(content)

    def _append_log(self, node_id: str, entities: List[str]):
        """Cronaca dell'attività di compilazione."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = f"### [{timestamp}] 🧠 Ingestione & Compilazione\n"
        entry += f"- **Nodo Sorgente**: `{node_id}`\n"
        entry += f"- **Entità Elaborate**: {', '.join([f'[[{e}]]' for e in entities])}\n\n"
        
        with open(self.log_file, "a") as f:
            f.write(entry)

    async def _record_epistemic_claims(self, entity: str, markdown: str, node_id: str):
        import uuid
        prompt = f"""
        Estrai 3 affermazioni chiave (claims) da questo markdown wiki. 
        Rispondi in JSON: [ {{ "claim": "...", "confidence": 0.9 }}, ... ]
        
        MKD:
        {markdown[:1000]}
        """
        try:
            res = await self.engine.orchestrator.get_consensus_response(prompt, "Epistemic Extractor", target_model="llama3.2:3b")
            import re
            match = re.search(r"\[.*\]", res, re.DOTALL)
            if match:
                claims = json.loads(match.group(0))
                for c in claims:
                    cid = str(uuid.uuid4())
                    self.engine._prefilter.con.execute(
                        "INSERT INTO wiki_claims (claim_id, page_id, claim_text, source_node_ids, confidence) VALUES (?, ?, ?, ?, ?)",
                        (cid, entity, c["claim"], json.dumps([node_id]), c["confidence"])
                    )
        except Exception as e: 
            print(f"⚠️ [Claims Error] {e}")
