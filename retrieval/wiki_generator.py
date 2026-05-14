"""
retrieval/wiki_generator.py
───────────────────────────
Sovereign Wiki Engine (v4.3.0)
Trasforma il grafo semantico in articoli strutturati, leggibili e citati.
"""

import asyncio
import httpx
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime
import json
import re
from pathlib import Path
from retrieval.wiki_monitor import WikiFreshnessMonitor
from retrieval.mesh_consensus import MeshConsensusEngine
from retrieval.causal_simulator import CausalSimulator
from retrieval.wiki_visualizer import WikiVisualizer
from retrieval.entity_linker import EntityLinker
from retrieval.nl_whatif import NaturalLanguageWhatIf
from retrieval.decision_journal import SovereignDecisionJournal
from retrieval.learning_path import LearningPathGenerator
from utils.redactor import redactor

@dataclass
class WikiCitation:
    node_id: str
    source_title: str
    source_url: Optional[str]
    source_date: str # [v4.3.1] Data di creazione del nodo sorgente
    confidence: float
    excerpt: str
    is_contradictory: bool = False
    conflict_node_id: str = ""

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
    metadata: Dict = field(default_factory=dict) # [v6.1] Metadati aggiuntivi

class SovereignWikiGenerator:
    def __init__(self, engine):
        self.engine = engine
        self.monitor = WikiFreshnessMonitor(engine)
        self.consensus_engine = MeshConsensusEngine(engine)
        self.simulator = CausalSimulator(engine)
        self.nl_whatif = NaturalLanguageWhatIf(engine)
        self.journal = SovereignDecisionJournal(engine)
        self.learning_path = LearningPathGenerator(engine)
        self.visualizer = WikiVisualizer(engine)
        self.linker = EntityLinker(engine) # [v8.1]
        # 🏺 [v8.0] Knowledge Versioning Path
        self.history_dir = Path(engine.data_dir) / "wiki_history"
        self.history_dir.mkdir(exist_ok=True)
        # 📂 [v9.0] Canonical Persistent Wiki (Source of Truth)
        self.wiki_dir = Path(engine.data_dir) / "wiki"
        self.wiki_dir.mkdir(exist_ok=True)

    def save_canonical_page(self, topic: str, markdown: str, namespace: str = "General"):
        """Salva o aggiorna la versione canonica (Source of Truth) e mantiene la cronologia Aegis."""
        from retrieval.aegis_bus import aegis_bus
        sanitized_md = redactor.redact(markdown)
        
        safe_ns = "".join([c if c.isalnum() else "_" for c in namespace])
        ns_dir = self.wiki_dir / safe_ns
        ns_dir.mkdir(exist_ok=True)
        
        safe_topic = "".join([c if c.isalnum() else "_" for c in topic])
        canonical_file = ns_dir / f"{safe_topic}.md"
        
        # [v9.5] History Tracking
        timestamp = int(time.time())
        history_file = self.history_dir / f"{safe_topic}_{timestamp}.md"
        
        # Salva file fisico
        with open(canonical_file, "w") as f:
            f.write(sanitized_md)
        with open(history_file, "w") as f:
            f.write(sanitized_md)
            
        # [v9.5] Aegis Log for Time Travel
        aegis_bus.emit("WIKI_UPDATE", {
            "topic": topic,
            "namespace": namespace,
            "version": timestamp,
            "file_path": str(canonical_file.relative_to(self.engine.data_dir)),
            "content_preview": sanitized_md[:500]
        })
        
        # [v9.5] Pubblica evento su Bus Neurale per Orchestrator (Sovereign Adversary)
        self.engine.events.emit_sync(NeuralEventType.WIKI_GENERATED, {
            "page_name": topic,
            "namespace": namespace,
            "content": sanitized_md,
            "timestamp": timestamp
        })

        print(f"💾 [Wiki v9.5] Pagina [{namespace}] salvata e versionata: {canonical_file.name}")

    async def generate_page(self, topic: str, mode: str = "TECHNICAL") -> WikiPage:
        print(f"📖 [Wiki v8.1] Generazione pagina {mode} per: {topic}")
        
        # 1. Recupero Nodi (H-RAG: Hierarchical Retrieval)
        # [v4.3.1] Prioritize Concept Galaxies for context
        results = []
        community_summaries = []
        if hasattr(self.engine, 'communities'):
            try:
                # 🌌 Try to find relevant communities first
                comm_results = self.engine.communities.hierarchical_search(topic, limit=3)
                if comm_results:
                    # Collect all nodes from these communities for deep context
                    for comm in comm_results:
                        if comm.get('type') == 'community':
                            community_summaries.append(f"GALASSIA: {comm.get('title')}\nRIASSUNTO: {comm.get('text')}")
                            comm_nodes = await self.engine.query(f"community_id = '{comm['id']}'", k=10)
                            results.extend(comm_nodes)
            except Exception as e:
                print(f"⚠️ [H-RAG Error] {e}. Falling back to standard query.")

        if not results:
            # Fallback to standard Hybrid Search if H-RAG is empty or fails
            results = await self.engine.query(topic, k=25)
            
        if not results:
            return None

        # 2. Raggruppamento Semantico (Quantum Clustering simulato via LLM)
        # Chiediamo all'LLM di definire una struttura basata sui dati trovati
        context_data = "\n".join([f"ID:{r.node.id} | Titolo:{r.node.metadata.get('title', 'N/A')} | Contenuto:{r.node.text[:200]}" for r in results])
        
        # [v8.1] Adaptive Reading Protocol Prompting
        mode_instructions = {
            "EXECUTIVE": "Sintesi estrema (max 150 parole). Focus su decisioni chiave, rischi e opportunità. Usa bullet points. Niente dettagli tecnici profondi.",
            "TECHNICAL": "Analisi tecnica approfondita. Focus su implementazione, benchmark e meccaniche. Prosa dettagliata con riferimenti specifici.",
            "RESEARCH": "Ricerca completa e accademica. Includi storia, stato dell'arte e soprattutto CONTRADDIZIONI tra le fonti. Identifica esplicitamente la 'MAPPA DELL'IGNORANZA' (Knowledge Gaps): cosa non sappiamo ancora e dove mancano i dati."
        }
        
        struct_prompt = f"""
        Analizza questi dati estratti dal Vault su '{topic}'.
        Utilizza il PROTOCOLLO DI LETTURA: {mode} -> {mode_instructions.get(mode, mode_instructions['TECHNICAL'])}
        
        Utilizza le Galassie Concettuali per definire i macro-temi e i Nodi Atomici per i dettagli.

        GALASSIE CONCETTUALI (Punti di riferimento):
        {"---".join(community_summaries) if community_summaries else "Nessuna galassia specifica rilevata."}

        NODI ATOMICI (Dati grezzi):
        {context_data}

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

        # 3. Generazione Sezioni con Protocollo FLARE (Active Integrity)
        sections = []
        for sec_title in structure["sections"]:
            # Filtriamo i nodi più pertinenti per questa sezione
            adaptive_k = 10 if community_summaries else 5
            sec_results = await self.engine.query(f"{topic} {sec_title}", k=adaptive_k)
            sec_context = "\n".join([f"[{r.node.id}] {r.node.text}" for r in sec_results])
            
            synth_prompt = f"Scrivi la sezione '{sec_title}' per la pagina Wiki su '{topic}'. Usa SOLO le fonti fornite. Cita usando [ID_NODO].\n\nFONTI:\n{sec_context}"
            wiki_model = self.engine.orchestrator.settings.get("wiki_model", "qwen2.5:7b")
            content = await self.engine.orchestrator.get_consensus_response(synth_prompt, f"Wiki Writer: {sec_title}", target_model=wiki_model)
            
            # 🛡️ [v7.0] FLARE: Active Uncertainty Audit
            audit_prompt = f"Analizza questo testo su '{topic}'. Identifica un claim incerto o che necessita di più prove. Rispondi in JSON: {{\"claim\": \"...\", \"uncertainty\": 0.0-1.0}}. Se è solido, uncertainty 0.0.\n\nTESTO:\n{content}"
            # Fallback intelligente per il modello di audit
            audit_model = "llama3.2:3b" if "llama3.2:3b" in str(self.engine.orchestrator.settings) else wiki_model
            audit_raw = await self.engine.orchestrator.get_consensus_response(audit_prompt, "FLARE Auditor", target_model=audit_model)
            
            try:
                audit_match = re.search(r'\{.*\}', audit_raw, re.DOTALL)
                if audit_match:
                    audit = json.loads(audit_match.group(0))
                    if audit.get("uncertainty", 0) > 0.6:
                        uncertain_claim = audit.get("claim")
                        print(f"🔍 [FLARE] Incertezza rilevata su: {uncertain_claim[:50]}... Espansione contesto.")
                        
                        # Retrieval mirato per il claim incerto
                        flare_results = await self.engine.query(uncertain_claim, k=3)
                        flare_context = "\n".join([f"[FLARE:{r.node.id}] {r.node.text}" for r in flare_results])
                        
                        # Rigenerazione con contesto aumentato
                        content = await self.engine.orchestrator.get_consensus_response(
                            f"{synth_prompt}\n\nINTELLIGENZA AGGIUNTIVA (FLARE):\n{flare_context}\n\nIntegra queste info per risolvere l'incertezza.",
                            f"Wiki Refiner: {sec_title}",
                            target_model=wiki_model
                        )
                        # Uniamo i risultati per le citazioni
                        sec_results.extend(flare_results)
            except Exception as e:
                print(f"⚠️ [FLARE Audit Error] {e}")

            # Estrazione Citazioni reali e mappatura granulare
            citations = []
            citation_metadata = {}
            seen_ids = set(re.findall(r'\[(?:FLARE:)?([a-f0-9\-]+)\]', content))
            
            for r in sec_results:
                # [v6.1] Contradiction Awareness
                conflict_node = next((e.target_id for e in r.node.edges if e.relation == "contradicts"), "")
                
                citation_metadata[r.node.id] = WikiCitation(
                    node_id=r.node.id,
                    source_title=r.node.metadata.get('title', 'Documento Locale'),
                    source_url=r.node.metadata.get('source_url'),
                    source_date=datetime.fromtimestamp(getattr(r.node, 'created_at', 0)).strftime('%Y-%m-%d'),
                    confidence=r.final_score,
                    excerpt=r.node.text[:150],
                    is_contradictory=bool(conflict_node),
                    conflict_node_id=conflict_node
                )
            
            for node_id in seen_ids:
                if node_id in citation_metadata:
                    citations.append(citation_metadata[node_id])
            
            # [v4.3.1] Knowledge Freshness Check
            sec_confidence = sum([c.confidence for c in citations]) / len(citations) if citations else 0.5
            
            # 🌍 [v7.5] Phase 6: Cross-Vault Weighted Consensus (Epistemic Meritocracy)
            mesh_verifications = []
            if hasattr(self.engine, 'gossip') and self.engine.gossip.peers:
                print(f"🕸️ [Mesh] Avvio Weighted Consensus per: {sec_title}")
                mesh_verifications = await self._mesh_verify_weighted(sec_title, content)
                
                if mesh_verifications:
                    # Se il consenso mesh è forte, aumenta o diminuisce la confidenza
                    mesh_score = mesh_verifications.consensus_score
                    # Shift del 20% basato sul consenso esterno
                    sec_confidence = max(0.0, min(1.0, sec_confidence + (mesh_score * 0.2)))
            
            sections.append(WikiSection(
                title=sec_title,
                content=content,
                citations=citations,
                confidence=sec_confidence
            ))
            # Store mesh verification metadata if any
            if mesh_verifications:
                if "mesh_verification" not in self.metadata_cache: self.metadata_cache["mesh_verification"] = {}
                self.metadata_cache["mesh_verification"][sec_title] = mesh_verifications

        # 4. Sommario e Correlati
        summary_prompt = f"Scrivi un breve sommario introduttivo (2 frasi) per una pagina wiki su '{topic}' basandoti su: {sections[0].content[:200]}"
        wiki_model = self.engine.orchestrator.settings.get("wiki_model", "qwen2.5:7b")
        summary = await self.engine.orchestrator.get_consensus_response(summary_prompt, "Wiki Summarizer", target_model=wiki_model)

        # 5. [v6.1] Discovery of Knowledge Gaps (Phase 3: Actionable Intelligence)
        gap_prompt = f"""
        Analizza la conoscenza corrente su '{topic}'. Identifica 2 'Knowledge Gaps' o 'Next Steps' operativi.
        Restituisci solo un JSON: {{"proposals": [ {{"title": "...", "reason": "..."}}, ... ]}}
        """
        gap_raw = await self.engine.orchestrator.get_consensus_response(gap_prompt, "Gap Detector", target_model=wiki_model)
        try:
            json_match = re.search(r'\{.*\}', gap_raw, re.DOTALL)
            proposals = json.loads(json_match.group(0)).get("proposals", []) if json_match else []
        except:
            proposals = []

        # [v4.3.0] Log event for Timeline
        self.engine._prefilter.log_event(
            event_type="WIKI_GENERATED",
            node_id="system",
            topic=topic,
            description=f"Generata pagina Wiki con {len(sections)} sezioni e {len(proposals)} proposte operative."
        )

        # [v4.3.1] Track dependencies for Freshness Monitor
        all_source_ids = [r.node.id for r in results]
        await self.monitor.track_dependencies(topic, all_source_ids)

        page = WikiPage(
            title=topic,
            summary=summary,
            sections=sections,
            related_topics=await self._find_related_topics(topic, results),
            total_nodes=len(results),
            generated_at=datetime.now()
        )
        # Inseriamo le proposte e la verifica mesh nei metadati per il frontend
        # [v8.1] Build Semantic Entity Map using professional EntityLinker
        entity_map = self.linker.build_anchor_index(results)

        page.metadata = {
            "proposals": proposals,
            "mesh_verification": self.metadata_cache.get("mesh_verification", {}),
            "confidence": sum([s.confidence for s in page.sections]) / len(page.sections) if page.sections else 0.85,
            "freshness": await self.monitor.check_freshness(topic),
            "entity_map": entity_map
        }
        self.metadata_cache = {} # Reset
        return page

    async def generate_page_stream(self, topic: str, mode: str = "TECHNICAL"):
        """[v8.4] Generazione asincrona streaming (SSE friendly)."""
        print(f"📡 [Wiki Stream] Avvio streaming per: {topic} ({mode})")
        
        # 1. Recupero iniziale (rapido)
        results = await self.engine.query(topic, k=25)
        if not results:
            yield json.dumps({"status": "error", "message": "No information found."})
            return

        yield json.dumps({"status": "progress", "step": "PLANNING", "message": "Analisi struttura semantica..."})
        
        # 2. Strutturazione (come prima ma con yield)
        context_data = "\n".join([f"ID:{r.node.id} | Titolo:{r.node.metadata.get('title', 'N/A')} | Contenuto:{r.node.text[:150]}" for r in results])
        mode_instructions = {
            "EXECUTIVE": "Sintesi estrema.",
            "TECHNICAL": "Analisi tecnica approfondita.",
            "RESEARCH": "Ricerca completa e accademica."
        }
        
        struct_prompt = f"Analizza '{topic}' con profilo {mode}. Restituisci solo un JSON: {{\"sections\": [\"Titolo 1\", ...]}}\n\nDATI:\n{context_data}"
        wiki_model = self.engine.orchestrator.settings.get("wiki_model", "qwen2.5:7b")
        struct_raw = await self.engine.orchestrator.get_consensus_response(struct_prompt, "Wiki Structurer", target_model=wiki_model)
        
        try:
            json_match = re.search(r'\{.*\}', struct_raw, re.DOTALL)
            structure = json.loads(json_match.group(0))
        except:
            structure = {"sections": ["Introduzione", "Analisi Detagliata", "Conclusione"]}

        yield json.dumps({"status": "progress", "step": "STRUCTURED", "sections": structure["sections"]})

        # 3. Generazione Progressiva delle Sezioni
        all_sections = []
        for i, sec_title in enumerate(structure["sections"]):
            yield json.dumps({"status": "progress", "step": "GENERATING", "current_section": sec_title, "index": i})
            
            sec_results = await self.engine.query(f"{topic} {sec_title}", k=5)
            sec_context = "\n".join([f"[{r.node.id}] {r.node.text}" for r in sec_results])
            
            synth_prompt = f"Scrivi la sezione '{sec_title}' per '{topic}'. Usa solo le fonti: {sec_context}"
            content = await self.engine.orchestrator.get_consensus_response(synth_prompt, f"Wiki Stream: {sec_title}", target_model=wiki_model)
            
            # Citazioni
            citations = []
            seen_ids = set(re.findall(r'\[([a-f0-9\-]+)\]', content))
            for r in sec_results:
                if r.node.id in seen_ids:
                    citations.append({
                        "node_id": r.node.id,
                        "source_title": r.node.metadata.get('title', 'Documento'),
                        "excerpt": r.node.text[:100]
                    })

            section_data = {
                "title": sec_title,
                "content": self.linker.link_entities(content, {}), # Entity linking basico
                "citations": citations
            }
            all_sections.append(section_data)
            
            yield json.dumps({"status": "section_ready", "section": section_data})

        # 4. Finalizzazione
        yield json.dumps({
            "status": "success", 
            "title": topic,
            "total_sections": len(all_sections),
            "complete": True
        })

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
        
        # 🏺 [v8.4] Epistemic Weather HUD
        sections_meta = [{"confidence": s.confidence} for s in page.sections]
        
        # Fetch real-time system mood for the HUD
        global_mood = {}
        try:
            if hasattr(self.engine, 'orchestrator') and hasattr(self.engine.orchestrator, 'blackboard'):
                global_mood = self.engine.orchestrator.blackboard.get_weather()
        except: pass
        
        md += self.visualizer.generate_confidence_dashboard(sections_meta, global_mood=global_mood)
        
        md += f"---\n"
        
        for sec in page.sections:
            md += f"## {sec.title}\n\n"
            
            # [v8.1] Semantic Entity Wrapping using specialized EntityLinker
            content = self.linker.link_entities(sec.content, page.metadata.get("entity_map", {}))
            
            md += f"{content}\n\n"
            if sec.citations:
                md += "#### 📌 Fonti Verificate:\n"
                for c in sec.citations:
                    link = f" ([Link]({c.source_url}))" if c.source_url else ""
                    md += f"- **{c.source_title}**{link}: *\"{c.excerpt}...\"* [ID: {c.node_id[:8]}]\n"
                md += "\n"
        
        # 📊 [v8.0] Phase 7: Generative Multimedia
        all_nodes = []
        for sec in page.sections:
            for cit in sec.citations:
                n = self.engine.get_node(cit.node_id)
                if n: all_nodes.append(n)
        
        if all_nodes:
            md += "---\n## 🌌 Conceptual Galaxy Visualization (v8.0)\n"
            md += "```mermaid\n"
            md += self.visualizer.generate_mermaid_flow(all_nodes[:15])
            md += "\n```\n\n"
            
            timeline = self.visualizer.generate_knowledge_timeline(all_nodes)
            if timeline:
                md += "## 🕰️ Evolutionary Knowledge Timeline\n"
                md += "```mermaid\n"
                md += timeline
                md += "\n```\n"

        # 🧪 [v8.0] What-If Simulation Entry Point
        md += "\n---\n## 🧪 Decision Simulation (What-If)\n"
        md += "*Simula l'impatto di una modifica a questa conoscenza:*\n"
        md += f"[Avvia Simulazione Causale per {page.title}](/api/wiki/simulate?topic={page.title})\n"

        if page.related_topics:
            md += "---\n## 🔗 Argomenti Correlati\n"
            md += ", ".join([f"[[{t}]]" for t in page.related_topics])
            md += "\n"
            
        md += f"\n\n*Generato automaticamente dal Sovereign Wiki Engine v8.0 il {page.generated_at.strftime('%Y-%m-%d %H:%M')}*"
        
        # 💾 Knowledge Versioning (Phase 7)
        self._archive_wiki_version(page.title, md)
        
        # 📂 [v9.0] Canonical Persistence
        self.save_canonical_page(page.title, md)
        
        return md

    def _archive_wiki_version(self, topic: str, markdown: str):
        """Salva una versione immutabile della conoscenza attuale."""
        import time
        ts = int(time.time())
        safe_topic = "".join([c if c.isalnum() else "_" for c in topic])
        version_file = self.history_dir / f"{safe_topic}_{ts}.md"
        with open(version_file, "w") as f:
            f.write(markdown)

    async def _mesh_verify_weighted(self, section: str, text: str):
        """[v7.5] Query peers and compute weighted consensus."""
        if not hasattr(self.engine, 'gossip'): return None
        
        active_peers = [p for p in self.engine.gossip.peers.values() if p.is_active]
        if not active_peers: return None

        peer_responses = []
        async with httpx.AsyncClient(timeout=4.0) as client:
            for peer in active_peers[:5]:
                try:
                    # Richiediamo un verdetto pesato e statistiche del vault remoto
                    resp = await client.get(f"{peer.address}/api/mesh/verdict", params={
                        "claim": section,
                        "context": text[:300]
                    })
                    if resp.status_code == 200:
                        peer_responses.append(resp.json())
                except: continue
        
        if not peer_responses: return None
        return await self.consensus_engine.run_sovereign_consensus(section, peer_responses)

    metadata_cache = {} # Temporary cache for generation metadata
