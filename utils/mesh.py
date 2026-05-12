"""
utils/mesh.py
─────────────
NeuralVault Mesh Protocol (v3.8.0)
P2P Synchronization using CRDTs and secure peer discovery.
"""

import time
import json
import logging
import threading
import httpx
from typing import List, Dict, Any, Optional, Set
from utils.crdt import GSet, LWWMap

class MeshNode:
    """Rappresentazione di un peer nella rete Mesh."""
    def __init__(self, node_id: str, base_url: str, api_key: str):
        self.node_id = node_id
        self.base_url = base_url
        self.api_key = api_key
        self.last_seen = 0.0
        self.paused = False

class MeshSyncManager:
    """
    Il cuore del protocollo Mesh.
    Gestisce la sincronizzazione P2P senza server centrale.
    """
    def __init__(self, engine: Any, local_node_id: str):
        self.engine = engine
        self.local_node_id = local_node_id
        self.peers: Dict[str, MeshNode] = {}
        
        # CRDT State: Grow-only Set di ID dei nodi conosciuti
        self.known_nodes = GSet()
        
        self.running = False
        self._thread: Optional[threading.Thread] = None
        self.logger = logging.getLogger("MeshSync")

    def toggle_pause(self, node_id: str, paused: bool):
        if node_id in self.peers:
            self.peers[node_id].paused = paused
            state = "SOSPESA" if paused else "ATTIVA"
            self.logger.info(f"⏸️ Sincronizzazione con {node_id} {state}.")

    def add_peer(self, node_id: str, url: str, api_key: str):
        self.peers[node_id] = MeshNode(node_id, url, api_key)
        self.logger.info(f"🌐 Peer aggiunto alla Mesh: {node_id} ({url})")

    def remove_peer(self, node_id: str):
        if node_id in self.peers:
            del self.peers[node_id]
            self.logger.info(f"🗑️ Peer rimosso dalla Mesh: {node_id}")

    def rename_peer(self, node_id: str, new_id: str):
        if node_id in self.peers:
            node = self.peers.pop(node_id)
            node.node_id = new_id
            self.peers[new_id] = node
            self.logger.info(f"✏️ Peer rinominato: {node_id} -> {new_id}")

    def start(self):
        self.running = True
        self._thread = threading.Thread(target=self._sync_loop, daemon=True)
        self._thread.start()
        self.logger.info("📡 Mesh Sync Engine AVVIATO.")

    def stop(self):
        self.running = False

    def _sync_loop(self):
        """Loop di sincronizzazione anti-entropia."""
        while self.running:
            # 1. Aggiorna lo stato locale dei nodi conosciuti
            local_ids = set(self.engine._nodes.keys())
            for nid in local_ids:
                self.known_nodes.add(nid)

            # 2. Tenta la sincronizzazione con ogni peer
            for peer_id, peer in self.peers.items():
                if peer.paused: continue # 🛡️ Salta i peer in pausa
                
                try:
                    self._sync_with_peer(peer)
                    peer.last_seen = time.time()
                except Exception as e:
                    self.logger.warning(f"⚠️ Errore sincronizzazione con peer {peer_id}: {e}")
            
            time.sleep(30) # Sincronizzazione ogni 30 secondi

    def _sync_with_peer(self, peer: MeshNode):
        """Protocollo di scambio: Diff -> Pull."""
        headers = {"X-API-Key": peer.api_key}
        
        # A. Scarica l'elenco degli ID dal peer (Inventory)
        # Assumiamo l'esistenza di un endpoint /api/mesh/inventory
        with httpx.Client(timeout=10.0) as client:
            r = client.get(f"{peer.base_url}/api/mesh/inventory", headers=headers)
            if r.status_code != 200: return
            
            peer_ids = set(r.json().get("ids", []))
            
            # B. Calcola la differenza (cosa ha lui che io non ho?)
            missing_ids = peer_ids - self.known_nodes.elements
            
            if not missing_ids:
                return

            self.logger.info(f"🔄 Mesh: Rilevati {len(missing_ids)} nuovi nodi dal peer {peer.node_id}")

            # C. Pull dei nodi mancanti (batch)
            # [v4.3.5] Ottimizzazione: Aumentato batch size a 150 per performance elevate su reti veloci
            batch_size = 150
            missing_list = list(missing_ids)
            
            for i in range(0, len(missing_list), batch_size):
                chunk = missing_list[i:i+batch_size]
                r_pull = client.post(
                    f"{peer.base_url}/api/mesh/pull", 
                    headers=headers,
                    json={"ids": chunk}
                )
                
                if r_pull.status_code == 200:
                    new_data = r_pull.json().get("nodes", [])
                    
                    # 🕶️ Agent SMITH: Firewall di Perimetro
                    smith = None
                    if hasattr(self.engine, 'lab') and hasattr(self.engine.lab, 'smiths'):
                        smith = self.engine.lab.smiths.get(peer.node_id)
                        if smith: smith.status = f"Ispezione Traffico: {peer.node_id}"

                    for node_data in new_data:
                        # Audit SMITH: Se il payload è sospetto, viene scartato prima del Vault
                        if smith:
                            if not smith.inspect_payload(node_data):
                                continue 
                            node_data["text"] = smith.sanitize_data(node_data["text"])

                        # Ingestione atomica nel Vault locale
                        import asyncio
                        asyncio.run(self.engine.add_node(
                            node_id=node_data["id"],
                            text=node_data["text"],
                            metadata={**node_data.get("metadata", {}), "mesh_origin": peer.node_id}
                        ))
                        self.known_nodes.add(node_data["id"])
                    
                    self.logger.info(f"✅ Mesh: Sincronizzati {len(new_data)} nodi da {peer.node_id} (Batch {i//batch_size + 1})")

    def force_sync(self):
        """Trigger immediato del ciclo di sincronizzazione (es. dopo import identity)."""
        threading.Thread(target=self._sync_loop_once, daemon=True).start()

    def _sync_loop_once(self):
        """Esegue un singolo ciclo di sync senza attendere il timer."""
        for peer_id, peer in self.peers.items():
            if peer.paused: continue
            try:
                self._sync_with_peer(peer)
                peer.last_seen = time.time()
            except: pass
