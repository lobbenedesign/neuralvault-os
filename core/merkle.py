"""
core/merkle.py
───────────────
Sovereign Merkle Tree Engine (v11.0 - Step 3)
Implementazione crittografica di un Albero di Merkle con doppio hashing SHA256
per generare e validare prove crittografiche (Merkle Proofs) in O(log N).
"""

import hashlib
from typing import List, Tuple, Optional

class SovereignMerkleTree:
    """
    Gestore matematico e crittografico per alberi di Merkle.
    Consente il consolidamento di transazioni ed eventi di conoscenza in un unico root hash.
    """
    def __init__(self, leaves: List[str]):
        """
        Inizializza l'albero a partire da una lista di foglie.
        Le foglie devono essere stringhe hash (es. SHA256 dei payload).
        """
        self.leaves = leaves
        self.tree: List[List[str]] = []
        if leaves:
            self._build_tree()

    def _build_tree(self):
        """Costruisce i livelli dell'albero in modo bottom-up."""
        current_level = list(self.leaves)
        self.tree.append(current_level)
        
        while len(current_level) > 1:
            next_level = []
            for i in range(0, len(current_level), 2):
                left = current_level[i]
                if i + 1 < len(current_level):
                    right = current_level[i+1]
                else:
                    # In caso di numero dispari, duplica l'ultimo elemento (standard Merkle)
                    right = left
                    
                parent = self._hash_pair(left, right)
                next_level.append(parent)
            current_level = next_level
            self.tree.append(current_level)

    def _hash_pair(self, left: str, right: str) -> str:
        """Applica la concatenazione e il doppio SHA256 per impedire attacchi di estensione."""
        raw = (left + right).encode('utf-8')
        h1 = hashlib.sha256(raw).digest()
        return hashlib.sha256(h1).hexdigest()

    @property
    def root(self) -> Optional[str]:
        """Ritorna l'hash radice (Merkle Root) dell'albero, o None se vuoto."""
        if not self.tree:
            return None
        return self.tree[-1][0]

    def get_proof(self, index: int) -> List[Tuple[str, bool]]:
        """
        Genera una prova di inclusione (Merkle Proof) per una specifica foglia.
        Ritorna una lista di tuple: (sibling_hash, is_right_sibling)
        """
        if index < 0 or index >= len(self.leaves):
            return []
            
        proof = []
        curr_idx = index
        
        # Scorri i livelli bottom-up escludendo il root level
        for level in self.tree[:-1]:
            if curr_idx % 2 == 0:
                # Il sibling è a destra
                if curr_idx + 1 < len(level):
                    sibling = level[curr_idx + 1]
                else:
                    # Se non c'è sibling a destra, è se stesso duplicato
                    sibling = level[curr_idx]
                is_right = True
            else:
                # Il sibling è a sinistra
                sibling = level[curr_idx - 1]
                is_right = False
                
            proof.append((sibling, is_right))
            curr_idx //= 2
            
        return proof

    @staticmethod
    def verify_proof(leaf_hash: str, proof: List[Tuple[str, bool]], expected_root: str) -> bool:
        """
        Verifica la validità di una Merkle Proof in tempo O(log N).
        Ricostruisce il percorso di hashing e controlla se il root finale coincide.
        """
        current_hash = leaf_hash
        for sibling_hash, is_right in proof:
            if is_right:
                raw = (current_hash + sibling_hash).encode('utf-8')
            else:
                raw = (sibling_hash + current_hash).encode('utf-8')
                
            h1 = hashlib.sha256(raw).digest()
            current_hash = hashlib.sha256(h1).hexdigest()
            
        return current_hash == expected_root
