"""
retrieval/sovereign_aligner.py
───────────────────────────────
SovereignAligner v1.0: Modulo per la migrazione lineare degli embedding.
Permette di evolvere la Nebula verso nuovi modelli senza ri-foraggiare.
"""

import numpy as np
import torch
import torch.nn as nn
import json
import os
from pathlib import Path
from typing import List, Dict, Optional

class AlignerNet(nn.Module):
    def __init__(self, input_dim: int, output_dim: int):
        super().__init__()
        self.aligner = nn.Linear(input_dim, output_dim, bias=False)
        
    def forward(self, x):
        return self.aligner(x)

class SovereignAligner:
    """
    Gestisce la transizione tra diverse generazioni di modelli di embedding.
    Utilizza una mappatura lineare (Procrustes-like) per allineare i vecchi vettori
    ai nuovi, minimizzando la perdita di informazione.
    """
    def __init__(self, engine=None):
        self.engine = engine
        self.model_path = None
        if engine:
            self.model_path = engine.data_dir / "sovereign_aligner.pt"

    def train_mapping(self, source_vectors: np.ndarray, target_vectors: np.ndarray, epochs: int = 100):
        """
        Addestra un mappatore lineare tra due set di embedding.
        Utile quando si ha un subset di dati ri-processati con il nuovo modello.
        """
        in_dim = source_vectors.shape[1]
        out_dim = target_vectors.shape[1]
        
        device = "cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu"
        model = AlignerNet(in_dim, out_dim).to(device)
        optimizer = torch.optim.Adam(model.parameters(), lr=0.01)
        criterion = nn.MSELoss()
        
        X = torch.tensor(source_vectors, dtype=torch.float32).to(device)
        Y = torch.tensor(target_vectors, dtype=torch.float32).to(device)
        
        print(f"🧠 [SovereignAligner] Training mapping {in_dim} -> {out_dim}...")
        for epoch in range(epochs):
            optimizer.zero_grad()
            output = model(X)
            loss = criterion(output, Y)
            loss.backward()
            optimizer.step()
            if epoch % 20 == 0:
                print(f"   Epoch {epoch}: Loss = {loss.item():.6f}")
                
        if self.model_path:
            torch.save(model.state_dict(), self.model_path)
            print(f"✅ Mapping salvato in {self.model_path}")
            
        return model

    def migrate_nebula(self, target_dim: int):
        """
        Migrazione di massa della Nebula Madre.
        """
        if not self.engine: return
        
        print("🚀 [SovereignAligner] Inizio migrazione lineare della Nebula...")
        # 1. Recupera tutti i nodi
        all_ids = list(self.engine._nodes.keys())
        
        # 2. Applica la trasformazione se il modello esiste
        if self.model_path and os.path.exists(self.model_path):
             # Logica di caricamento e proiezione
             pass
        else:
             print("⚠️ Nessun modello di allineamento trovato. La migrazione richiede un set di calibrazione.")

    def auto_calibrate(self, sample_size: int = 100):
        """
        Prende un campione di nodi e li ri-embedda con il nuovo modello 
        per creare il set di calibrazione.
        """
        # Da implementare quando avremo il selettore del nuovo modello
        pass
