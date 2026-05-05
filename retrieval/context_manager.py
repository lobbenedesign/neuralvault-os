import logging
from typing import List, Dict, Optional

logger = logging.getLogger("NeuralVault-Context")

class ProjectContextManager:
    """
    🏗️ [PROJECT CONTEXT MANAGER]
    Gestisce il Quantum Clustering v2.
    Permette di definire un "Focus Gravitazionale" basato su un progetto specifico.
    I nodi correlati al progetto vengono attirati al centro della Nebula.
    """
    def __init__(self, engine):
        self.engine = engine
        self.current_context = None # e.g. "Python Backend Development"
        self.context_keywords = []

    def set_context(self, context_name: str, keywords: List[str]):
        """Imposta il focus del sistema."""
        self.current_context = context_name
        self.context_keywords = keywords
        logger.info(f"🏗️ [Context] Shift gravitazionale verso: {context_name}")
        
    def calculate_node_attraction(self, node) -> float:
        """Calcola quanto un nodo è attratto dal centro in base al contesto attuale."""
        if not self.current_context:
            return 1.0
            
        text = node.text.lower()
        match_count = sum(1 for kw in self.context_keywords if kw.lower() in text)
        
        # Fattore di attrazione: 1.0 (periferia) -> 5.0 (centro nucleo)
        return 1.0 + (match_count * 0.5)

    def get_context_report(self):
        return {
            "active_project": self.current_context,
            "keywords": self.context_keywords,
            "is_focused": self.current_context is not None
        }
