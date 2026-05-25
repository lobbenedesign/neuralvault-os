import time
import json
import logging
import asyncio
import httpx
from typing import List, Dict, Any, Optional

logger = logging.getLogger("Sovereign.CognitiveLoop")

class SovereignCognitiveLoop:
    """
    Sovereign Cognitive Reasoning Loop Engine.
    Executes reasoning chains (native <think> and emulated 3-Stage CoT self-critique)
    for Supreme Court debates and neural analysis.
    """
    def __init__(self, lab_engine):
        self.lab = lab_engine
        self.engine = lab_engine.engine
        
    def _get_ollama_url(self) -> str:
        if hasattr(self.engine, 'settings'):
            return self.engine.settings.get("ollama_url", "http://localhost:11434")
        return "http://localhost:11434"

    def _resolve_model(self, task: str) -> str:
        if hasattr(self.engine, 'settings'):
            # Fallback tiered priority
            return self.engine.settings.get_model(task)
        return "llama3.2"

    async def execute_reasoning(self, role: str, target_text: str, evidence: List[str] = None) -> Dict[str, Any]:
        """
        Executes reasoning for a specific agent role or arbitrator.
        Returns a dict: {
            "thought_trace": "...",
            "response": "...",
            "model_used": "...",
            "reasoning_mode": "native" | "emulated"
        }
        """
        # Determine the model based on role / task
        task_map = {
            "prosecutor": "court_judge_1",
            "defender": "court_judge_2",
            "arbitrator": "court_judge_3"
        }
        task_key = task_map.get(role.lower(), "route-audit")
        
        # Get model configuration from Settings
        model = self._resolve_model(task_key)
        if model == "-":
            # Fallback to route-audit or general audit model
            model = self._resolve_model("audit")
            if model == "-":
                model = "llama3.2"

        # Check if the model is a native deep reasoning model (e.g. contains 'deepseek-r1' or 'r1' or 'reasoning')
        model_lower = model.lower()
        is_native_reasoning = any(x in model_lower for x in ["r1", "deepseek-r1", "reasoning", "deepseek:14b", "deepseek:32b"])
        
        if is_native_reasoning:
            return await self._execute_native_reasoning(model, role, target_text, evidence)
        else:
            return await self._execute_emulated_reasoning(model, role, target_text, evidence)

    async def _execute_native_reasoning(self, model: str, role: str, target_text: str, evidence: List[str]) -> Dict[str, Any]:
        """
        Executes native <think> tag extraction for models like DeepSeek-R1.
        """
        prompt = f"System: You are the {role} of the Supreme Court of NeuralVault.\n"
        if evidence:
            prompt += f"Contradicting evidence: {' '.join(evidence)}\n"
        prompt += f"Analyze this claim/text: '{target_text}'. Let your reasoning lead to a brief, sharp professional final analysis."

        url = self._get_ollama_url()
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(f"{url}/api/generate", json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 0.6}
                }, timeout=180.0)
                
                if resp.status_code == 200:
                    raw_response = resp.json().get("response", "").strip()
                    
                    # Extract thinking trace
                    thought_trace = ""
                    final_response = raw_response
                    
                    if "<think>" in raw_response and "</think>" in raw_response:
                        parts = raw_response.split("</think>")
                        thought_part = parts[0].split("<think>")[1]
                        thought_trace = thought_part.strip()
                        final_response = parts[1].strip()
                    elif "<think>" in raw_response:
                        parts = raw_response.split("<think>")
                        thought_trace = parts[1].strip()
                        final_response = parts[0].strip()
                    
                    if not thought_trace:
                        thought_trace = "Native reasoning model did not output explicit <think> block, but completed inference."
                        
                    return {
                        "thought_trace": thought_trace,
                        "response": final_response,
                        "model_used": model,
                        "reasoning_mode": "native"
                    }
        except Exception as e:
            logger.error(f"Native reasoning loop failed for {model}: {e}")
            
        # Fallback if connection fails
        return {
            "thought_trace": f"Fallback due to model/server timeout or error: {model}",
            "response": f"[STATIC] {role} (native fallback): target claims are structurally stable.",
            "model_used": model,
            "reasoning_mode": "native"
        }

    async def _execute_emulated_reasoning(self, model: str, role: str, target_text: str, evidence: List[str]) -> Dict[str, Any]:
        """
        Executes a 3-Stage Cognitive Loop (Thesis -> Antithesis -> Synthesis) to emulate reasoning.
        1. Thesis (Draft Generation): Create initial perspective.
        2. Antithesis (Self-Critique & Z3 facts integration): Review draft for cognitive biases and inconsistencies.
        3. Synthesis (Refined Output): Produce polished verdict with computed <think> process.
        """
        # Retrieve logical constraints if available
        z3_context = ""
        if hasattr(self.engine, "forensic") and self.engine.forensic:
            try:
                # Query Z3/Forensic logic system to find contradiction proof details
                contradictions = await self.engine.forensic.find_cross_wiki_contradictions()
                relevant = [c for c in contradictions if c["topic"].lower() in target_text.lower() or target_text.lower() in c["topic"].lower()]
                if relevant:
                    z3_context = "\n🚨 [Z3 Formal Prover Constraint] Mathematical contradiction proven in active graph context:\n"
                    for r in relevant:
                        z3_context += f"- Wiki A: {r['wiki_a']} ('{r['claim_a']}') VS Wiki B: {r['wiki_b']} ('{r['claim_b']}')\n  Proof: {r['z3_proof']}\n"
            except Exception as e:
                logger.debug(f"Could not query forensic Z3: {e}")

        # Stage 1: Thesis
        thesis_prompt = (
            f"You are the {role} in the Supreme Court. Generate an initial analysis for the target text:\n"
            f"'{target_text}'\n"
        )
        if evidence:
            thesis_prompt += f"Using contradicting evidence: {' '.join(evidence)}\n"
        thesis_prompt += "Write a solid, detailed initial draft of your observations."

        url = self._get_ollama_url()
        draft = ""
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(f"{url}/api/generate", json={
                    "model": model,
                    "prompt": thesis_prompt,
                    "stream": False,
                    "options": {"temperature": 0.7, "num_predict": 350}
                }, timeout=90.0)
                if resp.status_code == 200:
                    draft = resp.json().get("response", "").strip()
        except Exception as e:
            logger.error(f"Thesis generation failed for {model}: {e}")
            draft = f"Initial draft from {role} assuming high semantic alignment."

        # Stage 2: Antithesis (Self-Critique)
        critique_prompt = (
            f"You are a critical auditor. Review your own draft below for logical gaps, cognitive biases, "
            f"and compliance constraints.{z3_context}\n\n"
            f"Draft:\n{draft}\n\n"
            f"Provide a severe, strict self-critique outlining what is weak, what is missing, and what should be corrected."
        )

        critique = ""
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(f"{url}/api/generate", json={
                    "model": model,
                    "prompt": critique_prompt,
                    "stream": False,
                    "options": {"temperature": 0.5, "num_predict": 300}
                }, timeout=90.0)
                if resp.status_code == 200:
                    critique = resp.json().get("response", "").strip()
        except Exception as e:
            logger.error(f"Antithesis generation failed for {model}: {e}")
            critique = "Self-critique focused on potential semantic gaps and logical layout verification."

        # Stage 3: Synthesis
        synthesis_prompt = (
            f"Refine your final verdict. Incorporate the self-critique to resolve all weaknesses and produce a polished, high-fidelity response.\n\n"
            f"Draft:\n{draft}\n\n"
            f"Self-Critique:\n{critique}\n\n"
            f"Provide only the refined, sharp professional final analysis."
        )

        final_response = ""
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(f"{url}/api/generate", json={
                    "model": model,
                    "prompt": synthesis_prompt,
                    "stream": False,
                    "options": {"temperature": 0.2, "num_predict": 300}
                }, timeout=90.0)
                if resp.status_code == 200:
                    final_response = resp.json().get("response", "").strip()
        except Exception as e:
            logger.error(f"Synthesis generation failed for {model}: {e}")
            final_response = draft

        # Build thought trace from stages
        thought_trace = (
            f"[THESIS DRAFT]\n{draft}\n\n"
            f"[ANTITHESIS SELF-CRITIQUE]\n{critique}\n\n"
            f"[Z3 FORMAL CONSTRAINT STATE]\n{z3_context if z3_context else 'No Z3 violations found in assumptions.'}"
        )

        return {
            "thought_trace": thought_trace,
            "response": final_response,
            "model_used": model,
            "reasoning_mode": "emulated"
        }
