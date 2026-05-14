import logging
from typing import List, Dict, Optional
from datetime import datetime

logger = logging.getLogger("PlaybookGenerator")

class PlaybookGenerator:
    """
    [v9.0] Retro-Causal Playbook Engine.
    Converts causal simulation paths into actionable prescriptive steps.
    """
    
    def __init__(self):
        pass

    def generate_playbook(self, target_outcome: str, causal_path: List[Dict]) -> str:
        """
        Generates a 5-step action playbook based on a causal chain.
        Analyses the dependencies from the desired outcome back to current actions.
        """
        if not causal_path:
            return "### ⚠️ Playbook Generation Failed\nNo valid causal path found to reach the target outcome."

        # Extracting key steps (nodes) from the path
        # Assuming path is a list of relationships or nodes from start to end
        steps = []
        for i, item in enumerate(causal_path):
            # Simplified extraction for now
            node_title = item.get('title', f"Step {i+1}")
            steps.append(node_title)

        playbook = f"## 🏺 SOVEREIGN ACTION PLAYBOOK: {target_outcome}\n"
        playbook += f"*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M')} via Retro-Causal Analysis*\n\n"
        
        playbook += "### 🎯 OBIETTIVO FINALE\n"
        playbook += f"Raggiungere lo stato: **{target_outcome}**\n\n"

        playbook += "### ⚡ SEQUENZA DI AZIONE (Top 5 Priority)\n"
        
        # We take the first 5 critical leverage points
        top_steps = steps[:5]
        for idx, step in enumerate(top_steps):
            playbook += f"{idx+1}. **{step}**\n"
            playbook += "   - *Azione*: Implementare/Verificare questa condizione.\n"
            playbook += "   - *Impatto*: Indispensabile per sbloccare lo step successivo.\n"

        playbook += "\n### 🛡️ MITIGAZIONE RISCHI\n"
        playbook += "- Se un nodo della catena fallisce, ricalcolare immediatamente la rotta tramite il Digital Twin.\n"
        playbook += "- Monitorare i segnali di 'Contraddizione Formale' durante l'esecuzione.\n"
        
        playbook += "\n--- \n*Prescrizione generata autonomamente da NeuralVault v9.0*"
        
        return playbook
