import time
import logging
import asyncio
from pathlib import Path
from typing import List, Dict

logger = logging.getLogger("NeuralVault-Sleep")

class NeuralSleepEngine:
    """
    💤 [NEURAL SLEEP ENGINE]
    Consolida la memoria e ottimizza il grafo durante i periodi di inattività.
    """
    def __init__(self, engine, idle_threshold_sec: int = 300): # 5 minuti default
        self.engine = engine
        self.idle_threshold = idle_threshold_sec
        self.last_interaction = time.time()
        self.is_sleeping = False
        self.is_dreaming = False
        self.current_dream = ""
        self._stop_event = asyncio.Event()

    def touch(self):
        """Notifica un'attività utente per resettare il timer di inattività."""
        self.last_interaction = time.time()
        if self.is_sleeping:
            logger.info("☀️ [Sleep] Sistema risvegliato dall'attività utente.")
            self.is_sleeping = False

    async def start_maintenance_loop(self):
        """Loop principale che monitora l'idle e avvia il sonno neurale."""
        logger.info(f"🌙 [Sleep] Engine avviato (Threshold: {self.idle_threshold}s)")
        while not self._stop_event.is_set():
            idle_time = time.time() - self.last_interaction
            
            if idle_time > self.idle_threshold and not self.is_sleeping:
                await self._enter_sleep_state()
            
            await asyncio.sleep(30) # Controllo ogni 30s

    async def _enter_sleep_state(self):
        """Avvia le procedure di consolidamento della memoria."""
        self.is_sleeping = True
        logger.info("💤 [Sleep] NeuralVault sta entrando in fase di consolidamento (REM Phase)...")
        
        try:
            # 1. Consolidamento Sinaptico (Rafforzamento archi)
            await self._consolidate_synapses()
            
            # 2. Identificazione e Sintesi di Isole Semantiche
            if not self.is_sleeping: return # Controllo risveglio improvviso
            await self._synthesize_clusters()
            
            # 3. [v4.3.1] Logical Integrity: Scan for Contradictions
            if hasattr(self.engine, 'orchestrator') and hasattr(self.engine.orchestrator, 'contradiction_mapper'):
                logger.info("⚖️ [Sleep] Avvio analisi contraddizioni logiche...")
                await self.engine.orchestrator.contradiction_mapper.scan_for_contradictions(limit=20)
                
                # [v5.0] Autonomous Resolution
                logger.info("⚖️ [Sleep] Tentativo di risoluzione autonoma conflitti...")
                await self.engine.orchestrator.contradiction_resolver.resolve_pending_contradictions()
            
            # 4. [v7.0] Proactive Dreaming: Generazione wiki autonoma su gap identificati
            if not self.is_sleeping: return
            await self._proactive_dreaming()
            
            # 5. Log dell'evento nel Ledger
            self.engine._prefilter.log_event(
                event_type="NEURAL_SLEEP_COMPLETE",
                topic_cluster="System Maintenance",
                node_id="system",
                description="Consolidamento ciclico e Proactive Dreaming completati."
            )
            
            logger.info("✅ [Sleep] Consolidamento e Dreaming completati. Il sistema è più saggio.")
            
        except Exception as e:
            logger.error(f"❌ [Sleep Error] Durante il consolidamento: {e}")
        finally:
            self.is_sleeping = False

    async def _consolidate_synapses(self):
        """Rafforza i collegamenti tra nodi consultati spesso insieme."""
        logger.info("🧠 [Sleep] Rafforzamento sinapsi attive...")
        # Logica: Nodi con alto access_count e vicinanza semantica 
        # ricevono un boost al peso dell'arco.
        nodes = list(self.engine._nodes.values())
        for node in nodes:
            if node.access_count > 5:
                for edge in node.edges:
                    if edge.weight < 1.0:
                        edge.weight = min(1.0, edge.weight + 0.05)
        await asyncio.sleep(1)

    async def _synthesize_clusters(self):
        """Crea Super-Nodi di sintesi e aggiorna le Galassie Concettuali (H-RAG)."""
        logger.info("🧱 [Sleep] Sintesi dei cluster (Hierarchical Clustering)...")
        
        if hasattr(self.engine, 'communities'):
            try:
                # 🌌 1. Avvia il clustering gerarchico (Grafico + Vettoriale)
                # build_graph_and_cluster è sincrono ma gestisce internamente la Sandbox
                self.engine.communities.build_graph_and_cluster()
                
                # 🌌 2. Genera i riassunti per le nuove comunità identificate (Async)
                await self.engine.communities.generate_community_summaries()
                
                logger.info("✅ [Sleep] Galassie Concettuali aggiornate e riassunte.")
            except Exception as e:
                logger.error(f"❌ [Sleep] Errore durante la sintesi gerarchica: {e}")
        else:
            logger.warning("⚠️ [Sleep] CommunityEngine non trovato nell'engine.")
        
        await asyncio.sleep(1)

    def stop(self):
        self._stop_event.set()

    async def _proactive_dreaming(self):
        """[v7.0] Identifica gap o argomenti d'interesse e genera Wiki autonomamente."""
        logger.info("💤 [Dreaming] Analisi gap semantici per generazione proattiva...")
        
        try:
            from retrieval.metacognition import MetacognitionEngine
            from retrieval.wiki_generator import SovereignWikiGenerator
            
            # 1. Hybrid Evolution: Strengthening existing synapses
            if hasattr(self.engine, 'orchestrator'):
                logger.info("🧬 [Dreaming] Avvio batch di evoluzione ibrida (Sinapsi)...")
                await self.engine.orchestrator.run_hybrid_evolution(limit=250)

            # 2. Identificazione Gap (Terra Incognita)
            meta = MetacognitionEngine(self.engine)
            gaps = await meta.map_ignorance_gaps(limit=3)
            
            if not gaps:
                logger.info("💤 [Dreaming] Nessun gap significativo trovato. Cerco argomenti caldi...")
                # Fallback: Skywalker mission su un tema casuale
                if hasattr(self.engine, 'orchestrator'):
                    await self.engine.orchestrator.dispatch_skywalker_mission("Emergent AI Trends")
                return

            # 3. Selezione del Gap più "promettente"
            target_gap = gaps[0]
            dream_topic = target_gap.missing_concepts[0] if target_gap.missing_concepts else "Sintesi Conoscenza"
            
            logger.info(f"✨ [Dreaming] Sognando approfondimento su: '{dream_topic}'")
            self.is_dreaming = True
            self.current_dream = dream_topic
            
            # 4. Generazione Wiki Proattiva
            wiki_gen = SovereignWikiGenerator(self.engine)
            try:
                page = await wiki_gen.generate_wiki_page(dream_topic)
                
                # 5. Skywalker Expansion: Se abbiamo trovato un gap, mandiamo Skywalker a foraggiare
                if page and hasattr(self.engine, 'orchestrator'):
                    logger.info(f"🚀 [Dreaming] Dispatching FS-77 Skywalker for: {dream_topic}")
                    await self.engine.orchestrator.dispatch_skywalker_mission(dream_topic)
                    
            finally:
                self.is_dreaming = False
                self.current_dream = ""
            
            if page:
                logger.info(f"✅ [Dreaming] Nuova pagina Wiki 'sognata' con successo: {dream_topic}")
                self.engine._prefilter.log_event(
                    event_type="WIKI_DREAM_GENERATED",
                    topic_cluster=dream_topic,
                    node_id="system",
                    description=f"Il sistema ha generato autonomamente un approfondimento su '{dream_topic}' per colmare un gap semantico."
                )
        except Exception as e:
            logger.error(f"⚠️ [Dreaming Error] Fallimento durante il sogno: {e}")
