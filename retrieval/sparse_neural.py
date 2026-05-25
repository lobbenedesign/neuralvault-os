"""
retrieval/sparse_neural.py
──────────────────────────
Sovereign SPLADE & Hybrid Neural Expansion (v2.0)
Supporta sia l'espansione via LLM (leggera) che il modello SPLADE nativo (pesante).
"""

import json
import re
import asyncio
import logging
import os
from typing import Dict, List, Optional

class SparseNeuralEncoder:
    """
    Gestore ibrido dell'espansione sparsa.
    Switcha tra simulazione LLM e modello SPLADE (Naver) in base alle impostazioni.
    """
    def __init__(self, engine):
        self.engine = engine
        self.bm25_encoder = getattr(engine, '_sparse', None)
        self.logger = logging.getLogger("SparseNeural")
        
        # Stato del modello pesante (Lazy Loading)
        self.real_splade_active = False
        self._tokenizer = None
        self._model = None
        self._device = "mps" if os.uname().sysname == "Darwin" else "cpu"

    async def encode(self, text: str) -> Dict[int, float]:
        """
        Espande il testo in un vettore sparso {token_id: weight}.
        """
        # Carica impostazione dal vault
        use_real = self.engine.settings.get('use_real_splade', False)
        
        if use_real:
            return await self._encode_real_splade(text)
        else:
            return await self._encode_llm_expansion(text)

    async def _encode_llm_expansion(self, text: str) -> Dict[int, float]:
        """Metodo originale: Espansione semantica via LLM Ollama."""
        if not text: return {}
        
        model_llm = "llama3.2:3b"
        prompt = f"[SPLADE EXPANSION PROTOCOL]\nAnalizza: {text[:1000]}\nRestituisci JSON {{termine: peso}} (max 20 termini)."

        try:
            if not self.engine.orchestrator: return {}
            res_raw = await self.engine.orchestrator.get_consensus_response(prompt, "Sparse Expansion", target_model=model_llm)
            match = re.search(r'\{.*\}', res_raw, re.DOTALL)
            if match:
                token_weights = json.loads(match.group(0))
                return self._tokens_to_ids(token_weights)
        except Exception as e:
            self.logger.error(f"Errore LLM Expansion: {e}")
        return {}

    async def _encode_real_splade(self, text: str) -> Dict[int, float]:
        """Metodo Pesante: SPLADE nativo via Transformers."""
        try:
            if not self._model:
                await self._init_real_model()
            
            import torch
            with torch.no_grad():
                inputs = self._tokenizer(text, return_tensors="pt").to(self._device)
                outputs = self._model(**inputs)
                # Calcolo SPLADE log(1 + ReLU(w))
                logits = outputs.logits
                weights = torch.max(torch.log1p(torch.relu(logits)) * inputs.attention_mask.unsqueeze(-1), dim=1).values.squeeze()
                
                # Estrazione termini con peso > 0
                cols = torch.nonzero(weights).squeeze()
                if cols.dim() == 0: cols = cols.unsqueeze(0)
                
                res = {}
                for idx in cols:
                    token = self._tokenizer.decode([idx]).strip()
                    if token and len(token) > 2:
                        res[token] = float(weights[idx])
                
                return self._tokens_to_ids(res)
        except Exception as e:
            self.logger.error(f"Errore Real SPLADE: {e}")
            return await self._encode_llm_expansion(text) # Fallback

    async def _init_real_model(self):
        """Inizializzazione lazy del modello Naver."""
        self.logger.info("🚀 [SPLADE] Inizializzazione Real SPLADE Core (Naver)...")
        from transformers import AutoModelForMaskedLM, AutoTokenizer
        import torch
        
        model_id = "naver/splade-cocondenser-ensemble-distil"
        self._tokenizer = AutoTokenizer.from_pretrained(model_id)
        self._model = AutoModelForMaskedLM.from_pretrained(model_id).to(self._device)
        self._model.eval()
        self.logger.info("✅ [SPLADE] Core caricato correttamente.")

    def _tokens_to_ids(self, token_weights: Dict[str, float]) -> Dict[int, float]:
        """Mappa i token agli ID del vocabolario interno."""
        if not self.bm25_encoder: return {}
        sparse_id_vector = {}
        for token, weight in token_weights.items():
            clean_token = token.lower().replace("##", "").strip()
            if len(clean_token) < 2: continue
            tid = self.bm25_encoder._get_or_add_token(clean_token)
            sparse_id_vector[tid] = float(weight)
        return sparse_id_vector
