import time
import uuid
import json
import logging
import asyncio
import numpy as np
import httpx
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from enum import Enum
from orchestration.cognitive_loops import SovereignCognitiveLoop


@dataclass
class TensionNode:
    node_id: str
    tension: float        # 0.0 -> 1.0
    hop: int              # Distanza dalla sorgente
    relation: str         # "amplifies" | "contradicts" | "cites"

class DebateStance(Enum):
    PROSECUTOR = "prosecutor"   # Cerca debolezze e rischi
    DEFENDER = "defender"       # Cerca punti forti e precedenti
    ARBITRATOR = "arbitrator"   # Sintetizza la verità

@dataclass
class DebateMove:
    move_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    agent_id: str = ""
    stance: DebateStance = DebateStance.ARBITRATOR
    argument: str = ""
    evidence_nodes: List[str] = field(default_factory=list)
    tension_score: float = 0.5

class Agent007Lab:
    """
    IL LABORATORIO DI INTELLIGENZA ADVERSARIALE.
    Qui la memoria diventa dibattito e la verità viene estratta dal conflitto.
    """
    def __init__(self, engine):
        self.engine = engine
        self.logger = logging.getLogger("Agent007Lab")
        # Usiamo l'engine prefilter per le query persistenti (v9.0 thread-safe)
        self.prefilter = engine._prefilter
        self._init_db()
        self.agents = ["Prosecutor", "Defender", "Arbitrator"] # Per analytics report
        self.cognitive_loop = SovereignCognitiveLoop(self)


    def _init_db(self):
        """Prepara le tabelle per la tensione e i dibattiti."""
        self.prefilter.execute("""
            CREATE TABLE IF NOT EXISTS semantic_tension (
                source_id VARCHAR,
                target_id VARCHAR,
                tension DOUBLE,
                relation VARCHAR,
                timestamp DOUBLE
            )
        """)
        self.prefilter.execute("""
            CREATE TABLE IF NOT EXISTS debate_history (
                session_id VARCHAR,
                node_id VARCHAR,
                verdict JSON,
                timestamp DOUBLE
            )
        """)

    async def propagate_tension(self, source_node_id: str, vector: np.ndarray) -> List[TensionNode]:
        """
        Analisi di propagazione reale: calcola la tensione semantica basata sulle distanze vettoriali effettive.
        """
        # Recupero i vicini tramite l'engine (distanza reale)
        results = await self.engine.query("", query_vector=vector, k=10)
        tensions = []
        
        for res in results:
            if res.node.id == source_node_id: continue
            
            # La similarità è già calcolata nell'engine (cosino, o dot product normalizzato)
            # Supponiamo che res.final_score sia la similarità [0, 1]
            sim = res.final_score
            dist = 1.0 - sim
            
            # Classificazione reale della relazione
            if sim > 0.92: relation = "amplifies"
            elif sim > 0.75: relation = "cites"
            else: relation = "contradicts"
            
            # La tensione è alta se sono vicini ma "contradicts" (discrepanza semantica)
            tension = sim if relation != "contradicts" else dist
            
            t_node = TensionNode(node_id=res.node.id, tension=float(tension), hop=1, relation=relation)
            tensions.append(t_node)
            
            # Persistenza
            self.prefilter.execute(
                "INSERT INTO semantic_tension VALUES (?, ?, ?, ?, ?)",
                (source_node_id, res.node.id, float(tension), relation, time.time())
            )
            
        return tensions

    async def run_adversarial_session(self, node_id: str, text: str) -> Dict:
        """
        LA CORTE DIGITALE (SUPREME COURT ENSEMBLE).
        Avvia un dibattito e calcola un verdetto basato su un Quorum matematico.
        """
        session_id = str(uuid.uuid4())
        
        # 1. Recupero evidenze contrastanti reali
        contradictions = self.prefilter.fetchall("""
            SELECT target_id, tension FROM semantic_tension 
            WHERE source_id = ? AND relation = 'contradicts' 
            ORDER BY tension DESC LIMIT 3
        """, (node_id,))
        
        # Recuperiamo il contenuto delle evidenze
        evidence_texts = []
        for cid in contradictions:
            node = self.engine._nodes.get(cid[0])
            if node: evidence_texts.append(node.text)

        # 2. Generazione Argomenti via Sovereign Cognitive Reasoning Loop (Concorrente / Asincrono)
        p_res, d_res = await asyncio.gather(
            self.cognitive_loop.execute_reasoning("Prosecutor", text, evidence_texts),
            self.cognitive_loop.execute_reasoning("Defender", text, [])
        )
        
        p_arg = p_res["response"]
        d_arg = d_res["response"]
        
        # Arbitro (L'arbitro/giudice che emette il verdetto finale)
        v_res = await self.cognitive_loop.execute_reasoning("Arbitrator", text, [p_arg, d_arg])
        v_raw = v_res["response"]
        
        # Parsing strutturato del verdetto dell'arbitro
        v_report = {"score": 5, "risks": ["Ambiguity"], "rec": "Check manual review."}
        try:
            if "{" in v_raw and "}" in v_raw:
                json_part = v_raw[v_raw.find("{"):v_raw.rfind("}")+1]
                v_report = json.loads(json_part)
            else:
                v_report = json.loads(v_raw)
        except Exception as e:
            self.logger.warning(f"Failed to parse verdict JSON: {e}. Raw response: {v_raw}")
            v_report["rec"] = v_raw
            if "risk" in v_raw.lower():
                v_report["risks"] = ["Identified by Arbitrator during reasoning"]

        # 3. --- QUORUM MATEMATICO DETERMINISTICO ---
        # a. LLM Score (0-1)
        llm_score = v_report.get("score", 5) / 10.0
        
        # b. Semantic Integrity (Basato sulla tensione massima)
        max_tension = max([c[1] for c in contradictions]) if contradictions else 0.0
        semantic_integrity = 1.0 - max_tension
        
        # c. Graph Connectivity (Deterministic Rule)
        node = self.engine._nodes.get(node_id)
        edge_count = len(node.edges) if node else 0
        graph_authority = min(1.0, edge_count / 10.0) # Cap a 10 archi
        
        # d. Agent Relevance (Historical)
        agent_relevance = node.agent_relevance_score if node else 0.5
        
        # Quorum Calculation: Weighted Average
        # Pesi: LLM (40%), Semantic (30%), Authority (20%), Relevance (10%)
        final_quorum_score = (
            (llm_score * 0.4) + 
            (semantic_integrity * 0.3) + 
            (graph_authority * 0.2) + 
            (agent_relevance * 0.1)
        )
        
        verdict = {
            "vulnerability_score": v_report.get("score", 5),
            "quorum_score": round(final_quorum_score, 4),
            "integrity_level": "High" if final_quorum_score > 0.7 else "Medium" if final_quorum_score > 0.4 else "Critical",
            "top_risks": v_report.get("risks", ["Ambiguity"]),
            "recommendation": v_report.get("rec", "No recommendation."),
            "debate_log": [p_arg, d_arg],
            "thinking": {
                "prosecutor_thought": p_res["thought_trace"],
                "prosecutor_model": p_res["model_used"],
                "prosecutor_mode": p_res["reasoning_mode"],
                "defender_thought": d_res["thought_trace"],
                "defender_model": d_res["model_used"],
                "defender_mode": d_res["reasoning_mode"],
                "arbitrator_thought": v_res["thought_trace"],
                "arbitrator_model": v_res["model_used"],
                "arbitrator_mode": v_res["reasoning_mode"]
            }
        }
        
        self.prefilter.execute(
            "INSERT INTO debate_history VALUES (?, ?, ?, ?)",
            (session_id, node_id, json.dumps(verdict), time.time())
        )
        
        # Notifica all'Active Learning se il verdetto è troppo basso
        if hasattr(self.engine, 'active_learning') and final_quorum_score < 0.3:
            self.engine.active_learning.process_rejection(node_id, reason="supreme_court_veto")
            
        return verdict



    async def _generate_agent_move(self, role: str, target_text: str, evidence: List[str]) -> str:
        prompt = f"Role: {role}. Analyze this text: '{target_text}'. "
        if evidence:
            prompt += f"Contradicting evidence: {' '.join(evidence)}. "
        prompt += "Provide a short, sharp professional analysis."
        
        try:
            base_url = "http://localhost:11434"
            if hasattr(self.engine, 'settings'):
                base_url = self.engine.settings.get("ollama_url")
                
            async with httpx.AsyncClient() as client:
                resp = await client.post(f"{base_url}/api/generate", json={
                    "model": "phi3", "prompt": prompt, "stream": False
                }, timeout=10.0)
                if resp.status_code == 200:
                    return resp.json().get("response", f"{role} analysis unavailable.")
        except:
            pass
        return f"[STATIC] {role} considers this node " + ("problematic" if role == "Prosecutor" else "stable")

    async def _generate_verdict(self, text: str, arguments: List[str]) -> Dict:
        prompt = f"Arbitrate this debate on the text: '{text}'. Arguments: {arguments}. Return JSON with 'score' (0-10), 'risks' (list), 'rec' (string)."
        try:
            base_url = "http://localhost:11434"
            if hasattr(self.engine, 'settings'):
                base_url = self.engine.settings.get("ollama_url")

            async with httpx.AsyncClient() as client:
                resp = await client.post(f"{base_url}/api/generate", json={
                    "model": "phi3", "prompt": prompt, "stream": False, "format": "json"
                }, timeout=10.0)
                if resp.status_code == 200:
                    return json.loads(resp.json().get("response", "{}"))
        except:
            pass
        return {"score": 5, "risks": ["Manual review needed"], "rec": "Ollama offline."}

    async def ask_fast(self, prompt: str, model: str = "llama3.2:3b") -> str:
        """
        🚀 [v6.1] Bridge veloce per l'Archivista e compiti di sintesi.
        Include auto-resolution del modello per gestire tag mancanti (es. llama3.2 -> llama3.2:3b).
        """
        try:
            base_url = "http://localhost:11434"
            if hasattr(self.engine, 'settings'):
                base_url = self.engine.settings.get("ollama_url", "http://localhost:11434")
            
            # Sanitizzazione del modello
            if not model: model = "llama3.2:3b"
            
            async with httpx.AsyncClient() as client:
                # [v6.1] Tentativo 1: Modello richiesto
                resp = await client.post(f"{base_url}/api/generate", json={
                    "model": model, 
                    "prompt": prompt, 
                    "stream": False,
                    "options": {"num_predict": 300, "temperature": 0.3}
                }, timeout=120.0)
                
                if resp.status_code == 200:
                    return resp.json().get("response", "").strip()
                
                # [v6.1] Tentativo 2: Fallback se il modello non esiste (Ollama error)
                error_msg = resp.json().get("error", "").lower()
                if resp.status_code == 404 or "not found" in error_msg:
                    fallback = "llama3.2:3b" # Default sicuro per questo ambiente
                    if model == "llama3.2:3b": fallback = "qwen2.5:7b" # Secondo fallback
                    
                    self.logger.warning(f"⚠️ Modello {model} non trovato. Provo fallback: {fallback}")
                    
                    resp = await client.post(f"{base_url}/api/generate", json={
                        "model": fallback, 
                        "prompt": prompt, 
                        "stream": False
                    }, timeout=120.0)
                    
                    if resp.status_code == 200:
                        return resp.json().get("response", "").strip()

        except Exception as e:
            print(f"⚠️ [Agent007Lab] ask_fast fallito: {e}")
        return ""

    def get_weakness_report(self, node_id: str) -> Optional[Dict]:
        """Recupera l'ultimo report di vulnerabilità."""
        res = self.prefilter.fetchone(
            "SELECT verdict FROM debate_history WHERE node_id = ? ORDER BY timestamp DESC LIMIT 1",
            (node_id,)
        )
        return json.loads(res[0]) if res else None

    def _compute_semantic_heatmap(self, nodes):
        """
        [v1.1.0] Mappa di calore basata sulla densità semantica (numero di archi).
        Permette alla dashboard di colorare i nodi in base alla loro 'importanza' nel grafo.
        """
        heatmap = {}
        for nid, node in nodes.items():
            # Il colore va da 0.0 (Blu/Freddo) a 1.0 (Rosso/Caldo)
            # Densitá = num_archi / 5 (cap a 1.0)
            density = min(1.0, len(node.edges) / 5.0) if hasattr(node, 'edges') else 0.0
            heatmap[nid] = density
        return heatmap
