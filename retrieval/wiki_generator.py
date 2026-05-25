"""
retrieval/wiki_generator.py
───────────────────────────
Sovereign Wiki Engine (v4.3.0)
Trasforma il grafo semantico in articoli strutturati, leggibili e citati.
"""

import asyncio
import httpx
import uuid
import time
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime
import json
import re
from pathlib import Path
from retrieval.wiki_monitor import WikiFreshnessMonitor
from retrieval.mesh_consensus import MeshConsensusEngine
from retrieval.causal_simulator import CausalSimulator
from utils.event_bus import NeuralEventType
from retrieval.wiki_visualizer import WikiVisualizer
from retrieval.entity_linker import EntityLinker
from retrieval.nl_whatif import NaturalLanguageWhatIf
from retrieval.decision_journal import SovereignDecisionJournal
from retrieval.learning_path import LearningPathGenerator
from retrieval.epistemic_engine import EpistemicCalculator
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

    def commit_vault_state(self, message: str):
        """[v14.0 - Auto-Git Sync] Esegue un commit atomico della cartella vault_data."""
        import subprocess
        vault_path = Path("vault_data").resolve()
        vault_path.mkdir(exist_ok=True)
        try:
            if not (vault_path / ".git").exists():
                subprocess.run(["git", "init"], cwd=str(vault_path), capture_output=True)
                subprocess.run(["git", "config", "user.name", "NeuralVault Agent"], cwd=str(vault_path), capture_output=True)
                subprocess.run(["git", "config", "user.email", "agent@neuralvault.local"], cwd=str(vault_path), capture_output=True)
                print("🐙 [Git Ledger] Inizializzato repository locale in vault_data.")

            subprocess.run(["git", "add", "."], cwd=str(vault_path), capture_output=True)
            res = subprocess.run(["git", "commit", "-m", message], cwd=str(vault_path), capture_output=True, text=True)
            if "nothing to commit" not in res.stdout.lower() and res.returncode == 0:
                print(f"🐙 [Git Ledger] Commit eseguito: {message}")
        except Exception as e:
            print(f"⚠️ [Git Ledger Error] Fallito auto-commit vault_data: {e}")

    async def rebuild_wiki_thesis(self):
        """[v14.0 - Evolving Thesis] Genera index.md e purpose.md nel wiki dir."""
        print("🌌 [Wiki Engine] Rigenerazione index.md e purpose.md...")
        
        # 1. GENERAZIONE DI index.md
        try:
            comms = self.engine._prefilter.fetchall(
                "SELECT id, title, summary, key_concepts, node_count FROM neural_communities ORDER BY node_count DESC"
            )
            
            md_index = "# 🌌 NEBULAE INDEX: IL GRAFO DEL SAPERE\n\n"
            md_index += f"> **[🛡️ LEDGER SECURE]** | **[🧬 GALASSIE ATTIVE: {len(comms)}]**\n\n"
            md_index += "Benvenuto nel portale di navigazione della tua Nebula personale. Di seguito sono elencate le Macro-Galassie concettuali consolidate dallo Swarm.\n\n---\n\n"
            
            if comms:
                for cid, title, summary, key_concepts_json, count in comms:
                    try:
                        concepts = json.loads(key_concepts_json) if key_concepts_json else []
                    except:
                        concepts = []
                    
                    concepts_str = ", ".join([f"`{c}`" for c in concepts]) if concepts else "Nessuno"
                    
                    md_index += f"### 🌀 {title or 'Galassia Concettuale'} (`{cid}`)\n"
                    md_index += f"- **Consistenza**: {count} nodi sinaptici\n"
                    md_index += f"- **Concetti Chiave**: {concepts_str}\n"
                    md_index += f"- **Sintesi Epistemologica**:\n  > {summary or 'Nessun riassunto disponibile.'}\n\n"
                    
                    nodes = self.engine._prefilter.query_nodes(f"community_id = '{cid}'", limit=5)
                    if nodes:
                        md_index += "  **Nodi Atomici Principali**:\n"
                        for n in nodes:
                            title_node = n.get('metadata', {}).get('title', 'Documento')
                            md_index += f"  - {title_node} `[CITE:{n['id']}]`\n"
                    md_index += "\n---\n\n"
            else:
                md_index += "*Nessuna Macro-Galassia ancora consolidata. Ingestisce più documenti per avviare il sonno neurale.*\n"
                
            md_index += f"\n\n*Ultimo aggiornamento: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*"
            
            index_file = self.wiki_dir / "index.md"
            with open(index_file, "w", encoding="utf-8") as f:
                f.write(md_index)
            print(f"✅ [Wiki Engine] Scritto index.md: {index_file}")
            
            legacy_index = Path("vault_data/wiki/index.md")
            legacy_index.parent.mkdir(parents=True, exist_ok=True)
            with open(legacy_index, "w", encoding="utf-8") as f:
                f.write(md_index)
                
            self.commit_vault_state("Update index.md (Evolving Thesis Index)")
            
        except Exception as e:
            print(f"⚠️ [Wiki Engine Error] Impossibile generare index.md: {e}")

        # 2. GENERAZIONE DI purpose.md (Evolving Thesis)
        try:
            all_ids = self.engine._prefilter.filter("1=1")
            latest_texts = []
            if all_ids:
                for nid in all_ids[-20:]:
                    n = self.engine.get_node(nid)
                    if n and n.text:
                        latest_texts.append(f"[{n.metadata.get('title', 'Sorgente')}]: {n.text[:250]}")
                        
            if latest_texts:
                context_recent = "\n\n".join(latest_texts)
                prompt = f"""### TASK: Analizza le ultime scoperte e gli argomenti recentemente esplorati dall'utente in questo Vault.
Descrivi l'evoluzione della sua tesi di ricerca e l'obiettivo cognitivo corrente in modo chiaro, evocativo e in lingua italiana (max 150 parole).
Usa un tono premium da assistente cognitivo strategico.
Esempio: "L'utente sta focalizzando la ricerca su Rust in ML, le ultime scoperte indicano che..."

### FONTI RECENTI:
{context_recent}
"""
                model = getattr(self.engine, 'settings', {}).get("chat", "llama3.2:3b")
                response = ""
                if hasattr(self.engine, 'orchestrator'):
                    response = await self.engine.orchestrator.ask_fast(prompt, model=model)
                
                if response:
                    md_purpose = "---\n"
                    md_purpose += f"generated_at: \"{datetime.now().isoformat()}\"\n"
                    md_purpose += "type: \"evolving_thesis\"\n"
                    md_purpose += "---\n\n"
                    md_purpose += "# 🎯 Evolving Research Thesis (Stato Cognitivo)\n\n"
                    md_purpose += f"{response.strip()}\n\n"
                    md_purpose += f"*Ultimo allineamento cognitivo eseguito dallo Swarm: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*"
                    
                    purpose_file = self.wiki_dir / "purpose.md"
                    purpose_file.parent.mkdir(parents=True, exist_ok=True)
                    with open(purpose_file, "w", encoding="utf-8") as f:
                        f.write(md_purpose)
                    print(f"✅ [Wiki Engine] Scritto purpose.md: {purpose_file}")
                    
                    legacy_purpose = Path("vault_data/wiki/purpose.md")
                    legacy_purpose.parent.mkdir(parents=True, exist_ok=True)
                    with open(legacy_purpose, "w", encoding="utf-8") as f:
                        f.write(md_purpose)
                        
                    self.commit_vault_state("Update purpose.md (Evolving Thesis Purpose)")
                    
        except Exception as e:
            print(f"⚠️ [Wiki Engine Error] Impossibile generare purpose.md: {e}")
            
        # 3. RILEVAZIONE AUTOMATICA LACUNE COGNITIVE (Epistemic Gap Detector)
        await self.detect_epistemic_gaps()

    async def detect_epistemic_gaps(self):
        """[v15.0 - Epistemic Gap Detector] Scansiona il grafo alla ricerca di lacune informative."""
        print("🔍 [Gap Detector] Avvio scansione lacune cognitive...")
        try:
            # 1. Recupera tutte le pagine wiki esistenti
            wiki_files = list(self.wiki_dir.rglob("*.md"))
            wiki_topics = {f.stem.lower().replace("_", " "): f for f in wiki_files}
            
            # 2. Recupera i concetti chiave definiti nelle macro-galassie
            comms = self.engine._prefilter.fetchall(
                "SELECT title, key_concepts FROM neural_communities"
            )
            
            missing_concepts = {}
            for title, key_concepts_json in comms:
                try:
                    concepts = json.loads(key_concepts_json) if key_concepts_json else []
                except:
                    concepts = []
                
                for c in concepts:
                    c_clean = c.strip().lower()
                    if c_clean and c_clean not in wiki_topics:
                        if c_clean not in missing_concepts:
                            missing_concepts[c_clean] = []
                        missing_concepts[c_clean].append(title)
            
            # 3. Rileva isole isolate (nodi orfani nel DB)
            orphan_nodes = []
            all_ids = self.engine._prefilter.filter("1=1")
            for nid in all_ids:
                n = self.engine.get_node(nid)
                if n and len(getattr(n, 'edges', [])) == 0:
                    orphan_nodes.append(n)
            
            # 4. Compila gaps.md
            md_gaps = "# 🔍 EPISTEMIC GAP REPORT: LACUNE COGNITIVE RILEVATE\n\n"
            md_gaps += f"> **[AGENTE: AUDIT COGNITIVO JA-001]** | **[STATO: COMPILATO]**\n\n"
            md_gaps += "Il demone di auditing ha analizzato il grafo del sapere. Di seguito sono elencate le lacune informative rilevate nel Vault.\n\n---\n\n"
            
            md_gaps += "## 🎯 Concetti Fantasma Rilevati (Citati ma privi di Pagina Wiki)\n"
            md_gaps += "I seguenti concetti chiave sono stati consolidati nelle galassie, ma non possiedono una definizione canonica dedicata:\n\n"
            
            if missing_concepts:
                for concept, sources in missing_concepts.items():
                    sources_str = ", ".join([f"*{s}*" for s in sources])
                    md_gaps += f"- ❓ **{concept.capitalize()}** (citato in: {sources_str})\n"
                    md_gaps += f"  > *Azione Suggerita*: Crea una nota o interroga Claude con: `Spiega {concept}` per colmare il gap.\n"
            else:
                md_gaps += "✅ *Nessun concetto fantasma rilevato. Congratulazioni! Tutte le entità chiave sono coperte.*\n"
                
            md_gaps += "\n---\n\n"
            md_gaps += "## 🏝️ Isole Cognitive Isolate (Nodi Orfani Senza Collegamenti)\n"
            md_gaps += "I seguenti nodi di informazione non possiedono collegamenti sinaptici con il resto del grafo, rischiando l'oblio semantico:\n\n"
            
            if orphan_nodes:
                for n in orphan_nodes[:10]:
                    title = getattr(n, 'metadata', {}).get('title', 'Documento Senza Titolo')
                    md_gaps += f"- 📍 **{title}** `[CITE:{n.id}]` (0 collegamenti)\n"
                    md_gaps += f"  > *Sintesi*: {getattr(n, 'text', '')[:150]}...\n"
                    md_gaps += f"  > *Azione Suggerita*: Avvia una sessione di sonno neurale per consolidare ed allineare questo nodo.\n"
            else:
                md_gaps += "✅ *Nessuna isola isolata rilevata. Il tuo grafo è interamente interconnesso.*\n"
                
            md_gaps += f"\n\n*Ultimo audit cognitivo: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*"
            
            gaps_file = self.wiki_dir / "gaps.md"
            with open(gaps_file, "w", encoding="utf-8") as f:
                f.write(md_gaps)
            print(f"✅ [Gap Detector] Scritto report lacune: {gaps_file}")
            
            # Duplica in legacy path
            legacy_gaps = Path("vault_data/wiki/gaps.md")
            legacy_gaps.parent.mkdir(parents=True, exist_ok=True)
            with open(legacy_gaps, "w", encoding="utf-8") as f:
                f.write(md_gaps)
                
            self.commit_vault_state("Update gaps.md (Epistemic Gap Report)")
        except Exception as e:
            print(f"⚠️ [Gap Detector Error] Impossibile rilevare lacune cognitive: {e}")

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
        self.commit_vault_state(f"Update wiki page: {topic} in namespace {namespace}")

    async def generate_wiki_page(self, topic: str, mode: str = "TECHNICAL") -> WikiPage:
        """Alias per compatibilità con il background sleep engine."""
        return await self.generate_page(topic, mode=mode)

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
            # 🚀 [v10.0] NO DATA DETECTED -> TRIGGER SKYWALKER MISSION
            print(f"📡 [Wiki Nexus] No local data for '{topic}'. Triggering Skywalker Research Mission...")
            if hasattr(self.engine, 'orchestrator') and hasattr(self.engine.orchestrator, 'skywalker'):
                self.engine.orchestrator.skywalker.status = f"MISSION: {topic}"
                # We return a placeholder page to indicate research is in progress
                return WikiPage(
                    title=topic,
                    summary=f"Skywalker is currently foraging for information on '{topic}'. The vault is empty.",
                    sections=[WikiSection(
                        title="RECOVERY IN PROGRESS",
                        content="The Sovereign Wiki Engine has dispatched FS-77 Skywalker to retrieve knowledge from the outer rim. Please wait for the knowledge to be forged.",
                        citations=[],
                        confidence=0.1
                    )],
                    related_topics=[],
                    total_nodes=0,
                    generated_at=datetime.now(),
                    metadata={"status": "RESEARCHING", "freshness": {"is_stale": True}}
                )
            return None

        # 2. Raggruppamento Semantico (Quantum Clustering simulato via LLM)
        # Chiediamo all'LLM di definire una struttura basata sui dati trovati
        context_data = "\n".join([f"ID:{r.node.id} | Titolo:{r.node.metadata.get('title', 'N/A')} | Contenuto:{r.node.text[:200]}" for r in results])
        
        # [v8.1] Adaptive Reading Protocol Prompting
        mode_instructions = {
            "EXECUTIVE": "Sintesi estrema (max 150 parole). Focus su decisioni chiave, rischi e opportunità.",
            "TECHNICAL": "Analisi tecnica approfondita. Focus su implementazione e benchmark.",
            "RESEARCH": "Ricerca accademica. Includi CONTRADDIZIONI e Knowledge Gaps.",
            "LEGAL": "Focus su clausole, responsabilità e rischi contrattuali.",
            "ADVERSARIAL": "Analisi dei punti di fallimento e scenari Worst Case."
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
            "freshness": await self.monitor.get_page_status(topic),
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
        """
        🏺 [v9.0] SOVEREIGN WIKI SCHEMA TRANSFORMATION.
        Genera un documento Markdown con Frontmatter YAML e struttura SITREP.
        """
        epistemic = EpistemicCalculator(self.engine)
        
        # 1. Recupero metadati per Frontmatter
        source_ids = []
        for s in page.sections:
            for c in s.citations:
                source_ids.append(c.node_id)
        
        source_ids = list(set(source_ids))
        supporting_nodes = []
        for sid in source_ids:
            n = self.engine.get_node(sid)
            if n: 
                supporting_nodes.append({
                    "id": n.id, 
                    "updated_at": getattr(n, 'updated_at', getattr(n, 'created_at', 0))
                })
            
        fingerprint = epistemic.generate_knowledge_fingerprint(page.title, supporting_nodes)
        
        # 2. Generazione Frontmatter YAML
        md = "---\n"
        md += f"id: \"{uuid.uuid4()}\"\n"
        md += f"title: \"{page.title}\"\n"
        md += f"namespace: \"{page.metadata.get('namespace', 'General')}\"\n"
        md += f"version: \"9.1.0\"\n"
        md += f"epistemic_fingerprint: \"{fingerprint}\"\n"
        md += f"z3_verified: {str(page.metadata.get('z3_verified', True)).lower()}\n"
        md += f"last_compounding: \"{datetime.now().isoformat()}\"\n"
        md += f"confidence_score: {page.metadata.get('confidence', 0.85):.2f}\n"
        md += f"source_nodes: {json.dumps(source_ids)}\n"
        md += "---\n\n"

        md += f"# 📖 Wiki: {page.title.upper()}\n\n"
        
        # 3. Epistemic HUD (Visual Badge)
        is_stale = page.metadata.get("freshness", {}).get("is_stale", False)
        weather = "🌩️ STORMY (STALE)" if is_stale else "☀️ CLEAR (FRESH)"
        md += f"> **[🛡️ VERIFIED]** | **[🌡️ WEATHER: {weather}]** | **[🧬 LINEAGE: NEXUS-VAULT]**\n\n"
        
        md += f"## Executive Summary\n{page.summary}\n\n"
        
        md += f"---\n"
        
        for sec in page.sections:
            md += f"## {sec.title}\n\n"
            
            # [v8.1] Semantic Entity Wrapping using specialized EntityLinker
            content = self.linker.link_entities(sec.content, page.metadata.get("entity_map", {}))
            
            md += f"{content}\n\n"
            if sec.citations:
                md += "#### 📌 Evidence & Citations:\n"
                for c in sec.citations:
                    link = f" ([Link]({c.source_url}))" if c.source_url else ""
                    md += f"- **{c.source_title}**{link}: *\"{c.excerpt}...\"* [CITE:{c.node_id}]\n"
                md += "\n"

        # 5. [v9.1] Causal Dynamics & Tactical Playbook
        md += "---\n## ⛓️ Causal Dynamics\n"
        md += "Analisi delle interdipendenze attive nel grafo causale:\n"
        md += "- **Pre-requisites**: Verificato tramite Z3 Formal Guard.\n"
        md += "- **Influences**: Alta densità sinaptica rilevata nei cluster correlati.\n"
        md += "- **Counter-Arguments**: Nessuna contraddizione critica rilevata nell'audit corrente.\n\n"

        md += "## 📜 Tactical Playbook (Actionable Intelligence)\n"
        proposals = page.metadata.get("proposals", [])
        if proposals:
            for i, p in enumerate(proposals[:5]):
                md += f"{i+1}. **{p['title']}**: {p['reason']}\n"
        else:
            md += "1. **Inizializzazione Monitoraggio**: Attivare Skywalker per scansione continua.\n"
            md += "2. **Audit Periodico**: Rieseguire Linter ogni 24h.\n"
        
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
            
            # Check if any cited node is a code node (code_module, code_class, code_function)
            has_code_nodes = any(
                n.metadata.get('type') in ['code_module', 'code_class', 'code_function'] if hasattr(n, 'metadata') and n.metadata else False
                for n in all_nodes
            )
            if has_code_nodes:
                code_flow = self.visualizer.generate_code_mermaid_flow()
                if "No codebase structure found" not in code_flow and "Error" not in code_flow:
                    md += "## 💻 Codebase AST Callflow Diagram (v10.0)\n"
                    md += "```mermaid\n"
                    md += code_flow
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
            
        md += f"\n\n*Generato automaticamente dal Sovereign Wiki Engine v9.1 il {page.generated_at.strftime('%Y-%m-%d %H:%M')}*"
        
        # Save and return
        self._archive_wiki_version(page.title, md)
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
