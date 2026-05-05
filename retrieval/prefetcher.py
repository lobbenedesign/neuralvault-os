import time
import logging
from collections import deque, Counter
from typing import List, Dict, Optional

logger = logging.getLogger("NeuralVault-Prefetcher")

class AnticipatoryPrefetcher:
    """
    🔮 [ANTICIPATORY PREFETCHER]
    Prevede le future query dell'utente basandosi su catene di Markov 
    e vicinanza semantica, pre-caricando i nodi nella Hot RAM.
    """
    def __init__(self, engine, history_size: int = 15):
        self.engine = engine
        self.history = deque(maxlen=history_size)
        self.transition_matrix = {} # State transition probabilities
        self.hot_cache = {} # Pre-loaded nodes [id] -> node_object
        self.prediction_depth = 3
        
        # 🧬 [v4.3.1] Query DNA Fingerprint
        self.topic_affinity = Counter()
        self.query_dna = [] # Sequence of interaction vectors
        self.knowledge_gaps = [] # Identified areas with low density

    def record_interaction(self, node_id: str, topic: str = None):
        """Registra un accesso a un nodo per aggiornare il modello predittivo."""
        state = topic if topic else node_id
        
        if self.history:
            prev_state = self.history[-1]
            if prev_state not in self.transition_matrix:
                self.transition_matrix[prev_state] = Counter()
            self.transition_matrix[prev_state][state] += 1
            
        self.history.append(state)
        
        # Dopo ogni registrazione, tenta di prevedere il prossimo passo
        self._trigger_prefetch(state)

    def _trigger_prefetch(self, current_state: str):
        """Identifica i prossimi probabili nodi e li carica in RAM."""
        if current_state not in self.transition_matrix:
            return
            
        # Trova i top 3 stati più probabili
        predictions = self.transition_matrix[current_state].most_common(self.prediction_depth)
        
        for next_state, count in predictions:
            logger.info(f"🔮 [Prefetch] Predicting next move: {next_state} (Confidence based on {count} hits)")
            
            # Se lo stato è un topic, pre-carichiamo i nodi top per quel topic
            if len(next_state) > 15: # Probabilmente un ID nodo
                self._hydrate_node(next_state)
            else:
                # Esegue una query silenziosa per scaldare il cluster
                import asyncio
                asyncio.create_task(self._warm_topic(next_state))

    async def _warm_topic(self, topic: str):
        """Esegue una ricerca preventiva senza restituire risultati, solo per scaldare la cache HNSW."""
        try:
            # Una query a k=10 per 'scaldare' i dati nel Tier L2/L3
            await self.engine.query(topic, top_k=10)
        except: pass

    def _hydrate_node(self, node_id: str):
        """Carica fisicamente il nodo in una cache ad accesso immediato."""
        node = self.engine._nodes.get(node_id)
        if node:
            self.hot_cache[node_id] = node
            # Pre-carica anche i vicini (1-hop)
            for edge in node.edges[:3]:
                neighbor = self.engine._nodes.get(edge.target_id)
                if neighbor: self.hot_cache[neighbor.id] = neighbor

    def get_cached_node(self, node_id: str) -> Optional[object]:
        """Restituisce un nodo dalla cache istantanea se presente (L1 Tier)."""
        return self.hot_cache.get(node_id)

    def clear_cache(self):
        self.hot_cache.clear()

    async def build_cognitive_profile(self) -> Dict:
        """
        🧠 Analizza il 'DNA delle Query' per mappare interessi e lacune.
        """
        dominant = self.topic_affinity.most_common(5)
        
        # Identifica gap (topic meno frequentati ma presenti nel vault)
        # Questa è una versione semplificata
        profile = {
            "dominant_interests": [t[0] for t in dominant],
            "query_dna_depth": len(self.query_dna),
            "interaction_velocity": len(self.history) / 60 if self.history else 0, # queries per minute
            "system_affinity": "technical" if any("python" in t[0].lower() for t in dominant) else "general"
        }
        return profile
