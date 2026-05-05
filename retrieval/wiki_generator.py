"""
retrieval/wiki_generator.py
───────────────────────────
Sovereign Wiki Engine (v4.3.0)
Trasforma il grafo semantico in articoli strutturati, leggibili e citati.
"""

import asyncio
from dataclasses import dataclass
from typing import List, Dict, Optional
from datetime import datetime
import json
import re

@dataclass
class WikiCitation:
    node_id: str
    source_title: str
    source_url: Optional[str]
    confidence: float
    excerpt: str

@dataclass
class WikiSection:
    title: str
    content: str
    citations: List[WikiCitation]
    confidence: float

@dataclass
class WikiPage:
    title: str
    summary: str
    sections: List[WikiSection]
    related_topics: List[str]
    total_nodes: int
    generated_at: datetime

class SovereignWikiGenerator:
    def __init__(self, engine):
        self.engine = engine

    async def generate_page(self, topic: str) -> WikiPage:
        print(f"📖 [Wiki] Generazione pagina per: {topic}")
        
        # 1. Recupero Nodi (Hybrid Search profonda)
        # Usiamo un k più alto per avere una base di conoscenza solida
        results = await self.engine.query(topic, k=20)
        if not results:
            return None

        # 2. Raggruppamento Semantico (Quantum Clustering simulato via LLM)
        # Chiediamo all'LLM di definire una struttura basata sui dati trovati
        context_data = "\n".join([f"ID:{r.node.id} | Titolo:{r.node.metadata.get('title', 'N/A')} | Contenuto:{r.node.text[:200]}" for r in results])
        
        struct_prompt = f"""
        Analizza questi dati estratti dal Vault su '{topic}'.
        Proponi una struttura Wiki (Titoli di sezione) che copra tutte le informazioni disponibili.
        Restituisci solo un JSON: {{"sections": ["Titolo 1", "Titolo 2", ...]}}
        
        DATI:
        {context_data}
        """
        
        try:
            # 🔗 Access settings via Orchestrator
            wiki_model = self.engine.orchestrator.settings.get("wiki_model", "qwen2.5:7b")
            struct_raw = await self.engine.orchestrator.get_consensus_response(struct_prompt, "Wiki Structurer", target_model=wiki_model)
            
            # Pulizia per estrarre JSON se l'LLM aggiunge chiacchiere
            json_match = re.search(r'\{.*\}', struct_raw, re.DOTALL)
            if json_match:
                structure = json.loads(json_match.group(0))
            else:
                # Fallback se non c'è JSON ma la risposta è una lista di titoli
                lines = [l.strip() for l in struct_raw.split("\n") if l.strip() and len(l) < 50]
                structure = {"sections": lines[:5]} if lines else {"sections": ["Introduzione", "Analisi", "Dettagli Tecnici"]}
        except Exception as e:
            print(f"⚠️ [Wiki Structurer Error] {e}")
            structure = {"sections": ["Introduzione", "Analisi", "Conclusione"]}

        # 3. Generazione Sezioni con Citazioni
        sections = []
        for sec_title in structure["sections"]:
            # Filtriamo i nodi più pertinenti per questa sezione
            sec_results = await self.engine.query(f"{topic} {sec_title}", k=5)
            sec_context = "\n".join([f"[{r.node.id}] {r.node.text}" for r in sec_results])
            
            synth_prompt = f"""
            Scrivi la sezione '{sec_title}' per la pagina Wiki su '{topic}'.
            Usa SOLO le fonti fornite. Per ogni affermazione, cita la fonte usando [ID_NODO].
            Sii enciclopedico e preciso.
            
            FONTI:
            {sec_context}
            """
            
            wiki_model = self.engine.orchestrator.settings.get("wiki_model", "qwen2.5:7b")
            content = await self.engine.orchestrator.get_consensus_response(synth_prompt, f"Wiki Writer: {sec_title}", target_model=wiki_model)
            
            # Estrazione Citazioni reali
            citations = []
            for r in sec_results:
                if r.node.id in content:
                    citations.append(WikiCitation(
                        node_id=r.node.id,
                        source_title=r.node.metadata.get('title', 'Documento Locale'),
                        source_url=r.node.metadata.get('source_url'),
                        confidence=r.final_score,
                        excerpt=r.node.text[:150]
                    ))
            
            sections.append(WikiSection(
                title=sec_title,
                content=content,
                citations=citations,
                confidence=sum([c.confidence for c in citations]) / len(citations) if citations else 0.5
            ))

        # 4. Sommario e Correlati
        summary_prompt = f"Scrivi un breve sommario introduttivo (2 frasi) per una pagina wiki su '{topic}' basandoti su: {sections[0].content[:200]}"
        wiki_model = self.engine.orchestrator.settings.get("wiki_model", "qwen2.5:7b")
        summary = await self.engine.orchestrator.get_consensus_response(summary_prompt, "Wiki Summarizer", target_model=wiki_model)

        # [v4.3.0] Log event for Timeline
        self.engine._prefilter.log_event(
            event_type="WIKI_GENERATED",
            node_id="system",
            topic=topic,
            description=f"Generata pagina Wiki strutturata con {len(sections)} sezioni."
        )

        return WikiPage(
            title=topic,
            summary=summary,
            sections=sections,
            related_topics=await self._find_related_topics(topic, results),
            total_nodes=len(results),
            generated_at=datetime.now()
        )

    async def _find_related_topics(self, topic: str, results) -> List[str]:
        # Estraiamo entità o parole chiave dai metadati dei nodi
        topics = set()
        for r in results:
            entities = r.node.metadata.get('entities', [])
            if isinstance(entities, list):
                for e in entities:
                    if e.lower() != topic.lower(): topics.add(e)
        return list(topics)[:5]

    def to_markdown(self, page: WikiPage) -> str:
        md = f"# 📖 Wiki: {page.title.upper()}\n\n"
        md += f"> {page.summary}\n\n"
        md += f"---\n"
        
        for sec in page.sections:
            md += f"## {sec.title}\n\n"
            md += f"{sec.content}\n\n"
            if sec.citations:
                md += "#### 📌 Fonti Verificate:\n"
                for c in sec.citations:
                    link = f" ([Link]({c.source_url}))" if c.source_url else ""
                    md += f"- **{c.source_title}**{link}: *\"{c.excerpt}...\"* [ID: {c.node_id[:8]}]\n"
                md += "\n"
        
        if page.related_topics:
            md += "---\n## 🔗 Argomenti Correlati\n"
            md += ", ".join([f"[[{t}]]" for t in page.related_topics])
            md += "\n"
            
        md += f"\n\n*Generato automaticamente dal Sovereign Wiki Engine il {page.generated_at.strftime('%Y-%m-%d %H:%M')}*"
        return md
