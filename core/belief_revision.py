"""
core/belief_revision.py
─────────────────────────
Belief Revision Engine (AGM Policy - Alchourrón, Gärdenfors, Makinson, 1985).
Gestisce l'espansione, la contrazione e la revisione delle credenze nel Vault semantico,
garantendo l'integrità logica tramite transazioni protette e Git Ledger commits.
"""

import logging
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from pathlib import Path

logger = logging.getLogger("NeuralVault-BeliefRevision")

@dataclass
class RevisionPlan:
    nodes_to_stale: List[str]
    nodes_to_add: List[str]
    new_claim: str

class BeliefRevisionEngine:
    """
    ⚖️ [AGM BELIEF REVISION ENGINE]
    Applica le regole logiche per aggiornare le credenze del Vault senza contraddizioni.
    """
    def __init__(self, engine):
        self.engine = engine
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
                logger.info("🐙 [Git Ledger] Inizializzato repository locale in vault_data.")

            subprocess.run(["git", "add", "."], cwd=str(vault_path), capture_output=True)
            res = subprocess.run(["git", "commit", "-m", message], cwd=str(vault_path), capture_output=True, text=True)
            if "nothing to commit" not in res.stdout.lower() and res.returncode == 0:
                logger.info(f"🐙 [Git Ledger] Commit eseguito: {message}")
        except Exception as e:
            logger.error(f"⚠️ [Git Ledger Error] Fallito auto-commit vault_data: {e}")

    async def compute_topological_cost(self, node_id: str) -> float:
        """Calcola la densità sinaptica (peso totale dei collegamenti attivi)."""
        node = self.engine.get_node(node_id)
        if not node:
            return 0.0
        
        # Somma i pesi delle relazioni nel grafo KùzuDB/DuckDB
        weight_sum = sum([getattr(edge, 'weight', 1.0) for edge in getattr(node, 'edges', [])])
        return float(weight_sum)

    async def execute_revision(self, plan: RevisionPlan, require_court_approval: bool = True):
        """Applica la contrazione dei nodi obsoleti ed espande con la nuova credenza."""
        logger.info(f"⚖️ [AGM Revision] Avvio revisione per: {plan.new_claim[:50]}...")
        
        # 1. Rileva i nodi ad alta confidenza che richiedono approvazione
        high_confidence_nodes = []
        for nid in plan.nodes_to_stale:
            try:
                res = self.engine._prefilter.fetchall("SELECT confidence FROM vault_metadata WHERE id = ?", (nid,))
                confidence = res[0][0] if res else 0.5
                if confidence > 0.85:
                    high_confidence_nodes.append(nid)
            except Exception as e:
                logger.warning(f"Failed to check node confidence: {e}")

        # Se ci sono nodi ad altissima confidenza, mandiamo la notifica
        if high_confidence_nodes and require_court_approval:
            logger.warning(f"⚖️ [AGM Revision] Nodi critici {high_confidence_nodes} richiedono arbitrato della Supreme Court.")
            if hasattr(self.engine, 'orchestrator') and hasattr(self.engine.orchestrator, 'supreme_court'):
                await self.engine.orchestrator.supreme_court.submit_revision_case(plan)
                return
            
        # 2. Contrazione: Marcatura come REVISED nel DB dei nodi obsoleti
        for nid in plan.nodes_to_stale:
            try:
                self.engine._prefilter.execute(
                    "UPDATE vault_metadata SET status = 'REVISED', description = ? WHERE id = ?",
                    (f"Rivisto da claim: {plan.new_claim[:100]}", nid)
                )
                logger.info(f"⚖️ Nodo {nid} marcato come REVISED.")
            except Exception as e:
                logger.error(f"Errore durante contrazione nodo {nid}: {e}")

        # 3. Espansione: Ingestione del nuovo claim corretto
        try:
            new_node_id = await self.engine.upsert_text(
                text=plan.new_claim,
                metadata={"topic_type": "belief_revision", "source": "AGM_Engine"}
            )
            logger.info(f"⚖️ Espansione completata. Nuovo nodo inserito: {new_node_id}")
        except Exception as e:
            logger.error(f"Errore durante espansione: {e}")
            
        # 4. L4 Evolutionary Ledger: Git commit automatico del Wiki State
        # Ricostruiamo index.md e committiamo lo stato aggiornato
        if hasattr(self.engine, 'wiki'):
            await self.engine.wiki.rebuild_wiki_thesis()
            self.commit_vault_state(f"AGM Revision executed. New Claim: '{plan.new_claim[:40]}'")
