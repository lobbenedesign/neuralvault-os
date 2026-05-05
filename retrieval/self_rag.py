"""
retrieval/self_rag.py
─────────────────────
Modular Self-RAG Validation Core (v4.2.0)
Isola la logica di valutazione e correzione per evitare accoppiamento stretto
con la generazione asincrona principale. Basato sul framework Self-RAG.
"""

import json
import httpx
import logging

class SelfRAGCritic:
    """
    Self-RAG Validator Modulare.
    Valuta [ISSUP] (Is Supported) e corregge eventuali allucinazioni generate.
    """
    def __init__(self, ollama_url: str = "http://127.0.0.1:11434"):
        self.ollama_url = ollama_url

    async def validate_and_correct(self, context: str, response: str, model_name: str, timeout: float = 30.0) -> str:
        """
        Valuta se la risposta è supportata dal contesto (ISSUP) e se ci sono allucinazioni.
        Restituisce la risposta corretta (se ci sono correzioni) o l'originale.
        """
        validation_prompt = f"""
        CONTESTO: {context}
        RISPOSTA PROPOSTA: {response}
        
        VALUTAZIONE (Rispondi solo con un JSON valido):
        {{
            "supported": true/false,
            "hallucination_detected": true/false,
            "improvement": "testo per correggere eventuali errori o 'None'"
        }}
        """
        
        async with httpx.AsyncClient(timeout=timeout) as client:
            try:
                v_res = await client.post(f"{self.ollama_url}/api/generate", json={
                    "model": model_name, "prompt": validation_prompt, "stream": False, "format": "json"
                })
                
                if v_res.status_code == 200:
                    try:
                        critique = json.loads(v_res.json().get("response", "{}"))
                    except json.JSONDecodeError:
                        return response # Fallback se l'LLM non rispetta il JSON
                    
                    if critique.get("hallucination_detected") or not critique.get("supported"):
                        print("⚠️ [Self-RAG] Rilevata possibile allucinazione. Applicazione correzione...")
                        improvement = critique.get("improvement")
                        if improvement and improvement != "None":
                            return f"{improvement}\n\n🛡️ [Self-RAG: Risposta Corretta e Validata]"
                return response
            except Exception as e:
                print(f"Errore in SelfRAGCritic: {e}")
                return response
