import numpy as np
import logging
import json
import os
from pathlib import Path
from typing import Optional

class NeuralImplicitCompressor:
    """
    🧠 [v8.0] Phase 7: Neural Implicit Compression (NIC).
    Riduce il footprint degli embedding fino al 90% tramite quantizzazione neurale 
    e rappresentazione implicita delle distribuzioni semantiche.
    """
    def __init__(self, dimension: int = 768, codebook_size: int = 1024):
        self.dimension = dimension
        self.codebook_size = codebook_size
        self.codebook = None
        self.logger = logging.getLogger("NIC")
        self.is_trained = False
        self.is_training = False
        self.training_progress = 0.0

    def train_on_vault_async(self, vectors: np.ndarray, on_complete=None):
        """Addestra il codebook neurale in background aggiornando il progresso."""
        if len(vectors) < self.codebook_size or self.is_training:
            return

        self.is_training = True
        self.training_progress = 0.0

        def _train():
            self.logger.info(f"🧠 [NIC] Inizio addestramento su {len(vectors)} vettori...")
            import time
            from sklearn.cluster import MiniBatchKMeans
            
            # Use partial_fit to simulate training epochs and provide progress updates
            kmeans = MiniBatchKMeans(n_clusters=self.codebook_size, random_state=42, batch_size=256, max_iter=1, n_init=1)
            total_epochs = 20
            
            for i in range(total_epochs):
                kmeans.partial_fit(vectors)
                self.training_progress = ((i + 1) / total_epochs) * 100
                time.sleep(0.3) # Ritardo per feedback visivo fluido
                
            self.codebook = kmeans.cluster_centers_.astype(np.float32)
            self.is_trained = True
            self.is_training = False
            self.training_progress = 100.0
            self.logger.info("✅ [NIC] Addestramento completato. Compressione attiva.")
            if on_complete: on_complete()
            
        import threading
        threading.Thread(target=_train, daemon=True).start()

    def train_on_vault(self, vectors: np.ndarray) -> np.ndarray:
        """Addestra il codebook neurale in sincrono e restituisce i centri."""
        if len(vectors) < self.codebook_size:
            self.logger.warning("Vault troppo piccolo per NIC. Richiesto almeno 1024 nodi.")
            return None

        self.logger.info(f"🧠 [NIC] Inizio addestramento su {len(vectors)} vettori...")
        from sklearn.cluster import MiniBatchKMeans
        kmeans = MiniBatchKMeans(n_clusters=self.codebook_size, random_state=42, batch_size=256, n_init=3)
        kmeans.fit(vectors)
        self.codebook = kmeans.cluster_centers_.astype(np.float32)
        self.is_trained = True
        self.logger.info("✅ [NIC] Addestramento completato. Compressione attiva.")
        return self.codebook

    @staticmethod
    def _isolated_train(vectors: np.ndarray, codebook_size: int):
        """Metodo statico per l'addestramento in un processo separato."""
        from sklearn.cluster import MiniBatchKMeans
        kmeans = MiniBatchKMeans(n_clusters=codebook_size, random_state=42, batch_size=256, n_init=3)
        kmeans.fit(vectors)
        return kmeans.cluster_centers_.astype(np.float32)

    def compress(self, vector: np.ndarray) -> int:
        """Trasforma un vettore ad alta dimensione in un singolo indice neurale (uint16)."""
        if not self.is_trained: return -1
        # Calcolo distanza euclidea minima dal codebook
        distances = np.linalg.norm(self.codebook - vector, axis=1)
        return int(np.argmin(distances))

    def decompress(self, code_index: int) -> np.ndarray:
        """Ricostruisce il vettore approssimato partendo dall'indice del codebook."""
        if not self.is_trained or self.codebook is None or code_index < 0 or code_index >= len(self.codebook): 
            return None
        return self.codebook[code_index]

    def reconstruct(self, node_id: str, metadata: dict = None) -> Optional[np.ndarray]:
        """
        [v8.1] Reconstructs a vector from its compressed index stored in metadata.
        Used by NeuralVaultEngine.get_node for transparent decompression.
        """
        if not self.is_trained or metadata is None:
            return None
            
        code_index = metadata.get("nic_idx")
        if code_index is not None:
            return self.decompress(int(code_index))
        return None

    def save(self, path: str):
        if self.is_trained:
            np.save(path, self.codebook)

    def load(self, path: str):
        if os.path.exists(path):
            self.codebook = np.load(path)
            self.is_trained = True
            self.codebook_size = len(self.codebook)
            self.dimension = self.codebook.shape[1]
