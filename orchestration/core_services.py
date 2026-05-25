import time
import logging
from typing import Dict, Any

class BaseSovereignService:
    """Base class for the 4 Core Services."""
    def __init__(self, engine, orchestrator, name: str):
        self.engine = engine
        self.orchestrator = orchestrator
        self.name = name
        self.logger = logging.getLogger(f"Sovereign.{name}")
        self.last_run = 0

    def execute_cycle(self, nodes: Dict[str, Any]):
        raise NotImplementedError

class IngestionService(BaseSovereignService):
    """Consolidates Skywalker, Yoda, R2D2, Bridger."""
    def execute_cycle(self, nodes: Dict[str, Any]):
        now = time.time()
        if now - self.last_run < 120: return # Throttle (Eco Swarm: 2 minutes)
        self.last_run = now
        
        # Ingestion logic delegated to specific agents for now
        # to maintain UI backward compatibility while saving CPU loops.
        for aid in ["FS-77", "YO-001", "R2-D2", "CB-003"]:
            res = self.orchestrator._safe_agent_step(aid, nodes)
            if res: self.orchestrator._process_agent_action(res)

class MemoryOptimizationService(BaseSovereignService):
    """Consolidates Janitor, Reaper, Compressor."""
    def execute_cycle(self, nodes: Dict[str, Any]):
        now = time.time()
        if now - self.last_run < 240: return # Throttle (Eco Swarm: 4 minutes)
        self.last_run = now
        
        for aid in ["JA-001", "RP-001", "NC-001"]:
            res = self.orchestrator._safe_agent_step(aid, nodes)
            if res: self.orchestrator._process_agent_action(res)

class KnowledgeSynthesisService(BaseSovereignService):
    """Consolidates Synth, Pressman, Distiller, Quantum."""
    def execute_cycle(self, nodes: Dict[str, Any]):
        now = time.time()
        if now - self.last_run < 300: return # Throttle (Eco Swarm: 5 minutes)
        self.last_run = now
        
        for aid in ["SY-009", "PB-404", "DI-007", "QA-101"]:
            res = self.orchestrator._safe_agent_step(aid, nodes)
            if res: self.orchestrator._process_agent_action(res)

class SecurityAuditService(BaseSovereignService):
    """Consolidates Sentinel, AgentSmith, Adversary, Snake, Mandalorian."""
    def execute_cycle(self, nodes: Dict[str, Any]):
        now = time.time()
        if now - self.last_run < 180: return # Throttle (Eco Swarm: 3 minutes)
        self.last_run = now
        
        for aid in ["SE-007", "AG-001", "AD-007", "SN-008", "DN-099"]:
            res = self.orchestrator._safe_agent_step(aid, nodes)
            if res: self.orchestrator._process_agent_action(res)

class CoreServicesManager:
    def __init__(self, engine, orchestrator):
        self.services = [
            IngestionService(engine, orchestrator, "Ingestion"),
            MemoryOptimizationService(engine, orchestrator, "Memory"),
            KnowledgeSynthesisService(engine, orchestrator, "Synthesis"),
            SecurityAuditService(engine, orchestrator, "Security")
        ]
        
    def run_all(self, nodes: Dict[str, Any]):
        for srv in self.services:
            srv.execute_cycle(nodes)
