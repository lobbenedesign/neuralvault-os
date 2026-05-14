import logging
from typing import List, Dict, Any, Optional

class CognitiveLens:
    """
    🔬 [v8.2] Cognitive Lens System.
    Applica filtri archetipali e analitici alle simulazioni What-If.
    """
    
    ARCHETYPES = {
        "trump": {
            "name": "Donny Trumper View",
            "prompt": "Sei un leader disruptivo, istintivo e anti-istituzionale. Dai priorità al branding personale e alla narrazione di vittoria.",
            "weights": {"disruption": 1.5, "stability": 0.5, "risk": 1.2}
        },
        "musk": {
            "name": "Musk Reasoning",
            "prompt": "Ragiona per 'First Principles'. Scomponi ogni problema fisico/economico alla base. Ambizione estrema.",
            "weights": {"disruption": 1.8, "stability": 0.4, "opportunity": 1.5}
        },
        "bezos": {
            "name": "Bezos Strategy",
            "prompt": "Sei Jeff Bezos: Customer Obsession sopra ogni cosa. Ragiona sul lungo termine (Flywheel Effect).",
            "weights": {"disruption": 1.1, "stability": 1.1, "opportunity": 1.4}
        },
        "black_swan": {
            "name": "Black Swan Hunter",
            "prompt": "Analista di Rischi Catastrofici. Cerca eventi a bassa probabilità ma con impatto sistemico devastante. Pensa all'improponibile.",
            "weights": {"disruption": 2.5, "stability": 0.2, "risk": 2.0}
        },
        "legal": {
            "name": "Legal Eagle",
            "prompt": "Massimo focus sulla compliance legale, contrattuale e regolatoria. Identifica ogni possibile violazione o rischio penale.",
            "weights": {"disruption": 0.3, "stability": 2.0, "risk": 1.8}
        },
        "auditor": {
            "name": "The Auditor (Compliance)",
            "prompt": "Sei un revisore esperto. Cerca violazioni di policy, conflitti contrattuali e rischi di governance. Il tuo obiettivo è l'integrità procedurale.",
            "weights": {"disruption": 0.2, "stability": 2.5, "risk": 2.2}
        },
        "competitor": {
            "name": "The Competitor (Adversarial)",
            "prompt": "Sei un hacker o un concorrente spietato. Guarda la decisione per trovarne i punti deboli e sfruttarli a tuo vantaggio. Cerca di sabotare il piano.",
            "weights": {"disruption": 2.0, "stability": 0.3, "risk": 1.5, "opportunity": 1.8}
        },
        "guardian": {
            "name": "The Guardian (Ethical)",
            "prompt": "Sei il custode della reputazione e dell'etica. Valuta l'impatto a lungo termine sull'immagine e sulla morale. Evita azioni che corrodono la fiducia.",
            "weights": {"disruption": 0.5, "stability": 1.5, "opportunity": 0.8, "risk": 1.2}
        },
        "compliance": {
            "name": "Compliance / Regulatory",
            "prompt": "Valuta lo scenario attraverso le normative vigenti (GDPR, ISO, sicurezza). Identifica illeciti normativi prima di quelli finanziari.",
            "weights": {"disruption": 0.1, "stability": 2.8, "risk": 2.5}
        },
        "bottleneck": {
            "name": "Bottleneck / Resource (PM)",
            "prompt": "Focus sull'attrito interno e burnout. Analizza se il piano B sovraccarica il team oltre i limiti storici registrati.",
            "weights": {"disruption": 0.8, "stability": 1.2, "opportunity": 0.7, "risk": 1.5}
        },
        "competitive_dominance": {
            "name": "Competitive Dominance",
            "prompt": "Simula come un concorrente spietato userebbe questa info o questo ritardo a suo vantaggio per distruggere la nostra posizione.",
            "weights": {"disruption": 1.9, "stability": 0.5, "opportunity": 1.8, "risk": 1.3}
        },
        "cascading_failure": {
            "name": "Cascading Failure (Domino)",
            "prompt": "Analisi sistemica di 2° e 3° grado. Ignora gli impatti immediati e focus solo su blocchi futuri a catena (effetto domino).",
            "weights": {"disruption": 2.2, "stability": 0.3, "risk": 2.8}
        },
        "standard": {
            "name": "Objective Analyst",
            "prompt": "Analisi bilanciata, obiettiva e basata puramente sui fatti. Nessun bias archetipale.",
            "weights": {"disruption": 1.0, "stability": 1.0, "opportunity": 1.0}
        }
    }

    def __init__(self):
        self.logger = logging.getLogger("CognitiveLens")

    def get_lens_prompt(self, lens_id: str) -> str:
        """Recupera il system prompt per una lente specifica."""
        lens = self.ARCHETYPES.get(lens_id.lower())
        if lens:
            return f"LENTE ATTIVA: {lens['name']}\n{lens['prompt']}"
        return ""

    def get_lens_weights(self, lens_id: str) -> Dict[str, float]:
        """Recupera i pesi matematici per una lente specifica."""
        lens = self.ARCHETYPES.get(lens_id.lower())
        if lens:
            return lens.get("weights", {"disruption": 1.0, "stability": 1.0, "opportunity": 1.0})
        return {"disruption": 1.0, "stability": 1.0, "opportunity": 1.0}

    def apply_lens_weights(self, lens_id: str, base_impacts: List[Dict]) -> List[Dict]:
        """Applica i pesi della lente ai risultati della simulazione statistica."""
        weights = self.get_lens_weights(lens_id)
        for node in base_impacts:
            # Esempio: Applica i pesi se i nodi hanno tag specifici
            tags = node.get("metadata", {}).get("tags", [])
            if "risk" in tags:
                node["impact"] *= weights.get("risk", 1.0)
                
        return base_impacts
