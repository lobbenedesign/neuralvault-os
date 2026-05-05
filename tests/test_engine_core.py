import unittest
import os
import shutil
import numpy as np
from pathlib import Path
import sys

# Aggiungiamo la root al path per importare NeuralVault
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

try:
    from __init__ import NeuralVaultEngine, VaultNode
except ImportError:
    # Fallback per diverse strutture di import
    from api import NeuralVaultEngine, VaultNode

class TestNeuralVaultCore(unittest.TestCase):
    """
    Sovereign Sanity Suite v1.0
    Test fondamentali per la validazione post-evoluzione.
    """

    def setUp(self):
        self.test_dir = Path("./test_vault_temp")
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
        self.test_dir.mkdir()
        
        # Inizializzazione Engine in modalità ECO per velocità
        self.engine = NeuralVaultEngine(
            dim=1024, 
            data_dir=self.test_dir,
            use_quantization=False
        )

    def tearDown(self):
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)

    def test_ingestion_and_retrieval(self):
        """Testa se il sistema ricorda ciò che ingerisce."""
        node_id = "test_node_001"
        text = "La sovranità digitale è il pilastro di NeuralVault."
        self.engine.add_node(node_id, text, metadata={"type": "test"})
        
        # Retrieval diretto
        node = self.engine.get_node(node_id)
        self.assertIsNotNone(node)
        self.assertEqual(node.text, text)
        
        # Query semantica
        results = self.engine.query("Cos'è NeuralVault?", k=1)
        self.assertGreater(len(results), 0)
        self.assertEqual(results[0].node_id, node_id)

    def test_node_deletion(self):
        """Testa l'eliminazione atomica (Pillar 2)."""
        node_id = "delete_me"
        self.engine.add_node(node_id, "Temporary knowledge", metadata={})
        self.assertTrue(self.engine.delete_node(node_id))
        
        node = self.engine.get_node(node_id)
        self.assertIsNone(node)

    def test_hardware_dna(self):
        """Verifica che il rilevamento hardware funzioni (Agnosticism)."""
        self.assertIn("CUDA:", self.engine.hardware_dna)
        self.assertIn("METAL:", self.engine.hardware_dna)

if __name__ == "__main__":
    unittest.main()
