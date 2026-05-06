import numpy as np
import logging
import json
import os
from pathlib import Path

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

    def train_on_vault(self, vectors: np.ndarray):
        """Addestra il codebook neurale sulla distribuzione specifica del Vault dell'utente."""
        if len(vectors) < self.codebook_size:
            self.logger.warning("Vault troppo piccolo per NIC. Richiesto almeno 1024 nodi.")
            return

        self.logger.info(f"🧠 [NIC] Inizio addestramento su {len(vectors)} vettori...")
        # Utilizziamo un approccio K-Means per simulare la quantizzazione neurale (VQ-VAE style)
        from sklearn.cluster import MiniBatchKMeans
        kmeans = MiniBatchKMeans(n_clusters=self.codebook_size, random_state=42, batch_size=256)
        kmeans.fit(vectors)
        self.codebook = kmeans.cluster_centers_.astype(np.float32)
        self.is_trained = True
        self.logger.info("✅ [NIC] Addestramento completato. Compressione attiva.")

    def compress(self, vector: np.ndarray) -> int:
        """Trasforma un vettore ad alta dimensione in un singolo indice neurale (uint16)."""
        if not self.is_trained: return -1
        # Calcolo distanza euclidea minima dal codebook
        distances = np.linalg.norm(self.codebook - vector, axis=1)
        return int(np.argmin(distances))

    def decompress(self, code_index: int) -> np.ndarray:
        """Ricostruisce il vettore approssimato partendo dall'indice del codebook."""
        if not self.is_trained or code_index < 0: return None
        return self.codebook[code_index]

    def save(self, path: str):
        if self.is_trained:
            np.save(path, self.codebook)

    def load(self, path: str):
        if os.path.exists(path):
            self.codebook = np.load(path)
            self.is_trained = True
            self.codebook_size = len(self.codebook)
            self.dimension = self.codebook.shape[1]
