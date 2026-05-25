import logging
import asyncio
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Contradiction:
    new_claim: str
    existing_node_id: str
    existing_node_text: str
    z3_proof: str

@dataclass
class ImpactReport:
    source: str
    claims_extracted: int
    nodes_affected: int
    contradictions: List[Contradiction]
    recommendation: str
    blast_radius_nodes: List[str]

class PreIngestionImpactAnalyzer:
    """
    Analizza l'impatto PRIMA di ingestare nuovo contenuto.
    Non dopo (come fa Z3 in forensic audit batch).
    """
    def __init__(self, engine):
        self.engine = engine
        self.logger = logging.getLogger("ImpactAnalyzer")
        self.has_z3 = False
        try:
            import z3
            self.has_z3 = True
        except ImportError:
            self.logger.warning("Z3 not found, ImpactAnalyzer will use heuristics.")

    async def extract_claims(self, content: str) -> List[str]:
        """Estrae i claims dal testo."""
        # Splitto by sentences or newlines as a heuristic for claims
        lines = [line.strip() for line in content.split('\n') if len(line.strip()) > 15]
        return lines[:5]  # Limitiamo ai primi 5 per performance durante ingestion

    async def analyze_before_ingest(self, content: str, source: str) -> ImpactReport:
        claims = await self.extract_claims(content)
        
        # Step 2: Trova nodi correlati nel vault
        related_nodes = await self.engine.query(content, k=10)
        
        contradictions = []
        
        # Step 3: Z3 check preventivo
        if self.has_z3:
            try:
                from retrieval.forensic import ClaimVerificationGraph
                forensic = ClaimVerificationGraph(self.engine)
                
                for claim in claims:
                    for n_res in related_nodes:
                        node = n_res.node
                        if len(claim) < 10 or not node.text:
                            continue
                            
                        # Usiamo la verify_claims_logic per testare la contraddizione
                        proof = await forensic.verify_claims_logic(source, claim, node.text)
                        if proof:
                            contradictions.append(Contradiction(
                                new_claim=claim,
                                existing_node_id=node.id,
                                existing_node_text=node.text[:100] + "...",
                                z3_proof=proof
                            ))
            except Exception as e:
                self.logger.error(f"Errore durante l'analisi Z3: {e}")
                
        blast_nodes = [c.existing_node_id for c in contradictions]
        
        return ImpactReport(
            source=source,
            claims_extracted=len(claims),
            nodes_affected=len(related_nodes),
            contradictions=contradictions,
            recommendation="REVIEW" if contradictions else "SAFE",
            blast_radius_nodes=list(set(blast_nodes))
        )
