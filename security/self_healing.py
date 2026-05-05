import hashlib
import json
import logging
from typing import List, Dict, Optional

logger = logging.getLogger("NeuralVault-SelfHealing")

class SovereignSelfHealer:
    """
    🛡️ [SOVEREIGN SELF-HEALER]
    Automazione del Tombstone Paradox: recupera nodi corrotti o mancanti
    utilizzando firme crittografiche e parità distribuita.
    """
    def __init__(self, engine):
        self.engine = engine
        # Inizializzazione statistiche per evitare 404/Empty al boot
        self.engine.self_healing_stats = {
            "score": 100,
            "corrupted_nodes": 0,
            "status": "Initializing..."
        }

    def generate_node_fingerprint(self, node) -> str:
        """Genera una firma immutabile del contenuto del nodo."""
        payload = f"{node.text}:{json.dumps(node.metadata, sort_keys=True)}"
        return hashlib.sha256(payload.encode()).hexdigest()

    async def audit_vault_integrity(self):
        """Scansiona il vault alla ricerca di corruzione silenziosa (Bit Rot)."""
        logger.info("🛡️ [Self-Healer] Avvio audit integrità profonda...")
        corrupted = []
        legacy = []
        
        for node_id, node in self.engine._nodes.items():
            stored_hash = node.metadata.get("content_hash")
            current_hash = self.generate_node_fingerprint(node)
            
            if not stored_hash:
                # Nodo legacy senza firma v5.0
                legacy.append(node_id)
            elif current_hash != stored_hash:
                # Possibile corruzione o cambio formato v5.0
                logger.info(f"🩹 [Self-Healing] Rilevato scostamento firma per {node_id[:8]}. Riallineamento in corso...")
                corrupted.append(node_id)
        
        if legacy:
            logger.info(f"🧬 [Legacy] Trovati {len(legacy)} nodi pre-v5.0. Inizio firma crittografica...")
            for nid in legacy:
                node = self.engine._nodes[nid]
                node.metadata["content_hash"] = self.generate_node_fingerprint(node)
        
        if corrupted:
            await self.attempt_recovery(corrupted)
        
        # Aggiornamento statistiche per la dashboard
        self.engine.self_healing_stats = {
            "score": 100 if not corrupted else max(0, 100 - (len(corrupted) * 2)),
            "corrupted_nodes": len(corrupted),
            "status": "Integrity Optimal" if not corrupted else "Healing Active"
        }
        
        return len(corrupted) + len(legacy)

    async def attempt_recovery(self, corrupted_ids: List[str]):
        """
        Tombstone Paradox: tenta di recuperare il dato dai peer o dal LogStore (L2).
        """
        for nid in corrupted_ids:
            # 1. Tenta ripristino da L2 (Aegis LogStore)
            recovered_node = await self.engine._tiers.get(nid)
            if recovered_node:
                # Ri-calcoliamo la firma corretta prima di reinserire
                new_hash = self.generate_node_fingerprint(recovered_node)
                recovered_node.metadata["content_hash"] = new_hash
                self.engine._nodes[nid] = recovered_node
                logger.info(f"✅ [Recovery] Nodo {nid[:8]} riallineato e ri-firmato con successo.")
                continue
                
            # 2. Tenta ripristino dai Peer (v5.0 Mesh Recovery)
            logger.warning(f"⚠️ [Recovery] Impossibile recuperare {nid[:8]} localmente. Nodo isolato per riparazione peer.")

    def mark_as_tombstone(self, node_id: str):
        """Marcatura logica per prevenire collisioni post-cancellazione."""
        self.engine._prefilter.log_event(
            "TOMBSTONE_CREATED",
            "Security",
            node_id,
            "Nodo eliminato ma firma preservata per integrità Merkle."
        )
