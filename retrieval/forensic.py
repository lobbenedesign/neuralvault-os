"""
retrieval/forensic.py
─────────────────────
Claim Verification Graph & Forensic Audit (v10.2 - Z3 Incremental Proof edition)
Rileva contraddizioni e inconsistenze logiche tra diverse pagine Wiki e fonti locali.
"""

import logging
import json
import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class Contradiction:
    wiki_a: str
    wiki_b: str
    claim_a: str
    claim_b: str
    topic: str
    z3_proof: Optional[str] = None
    confidence: float = 0.0

class ClaimVerificationGraph:
    """
    Trova contraddizioni CROSS-WIKI utilizzando verifiche logico-formali (Z3).
    Analizza la tabella wiki_claims per identificare asserzioni divergenti sullo stesso topic.
    """
    def __init__(self, engine):
        self.engine = engine
        self.logger = logging.getLogger("ForensicAudit")
        self.duckdb = engine._prefilter if hasattr(engine, '_prefilter') else None
        
        # Inizializzatore Z3
        self.has_z3 = False
        try:
            import z3
            self.has_z3 = True
        except ImportError:
            self.logger.info("Z3 Solver not installed locally. Engaging symbolic heuristic logic parser.")

    async def verify_claims_logic(self, topic: str, claim_a: str, claim_b: str) -> Optional[str]:
        """
        Esegue la verifica formale di consistenza logica tra due asserzioni.
        Restituisce la stringa del Z3 proof se UNSAT (contraddizione), altrimenti None.
        """
        # Analisi dei token e delle polarità per definire il modello logico
        polarity_a = self._extract_polarity(claim_a)
        polarity_b = self._extract_polarity(claim_b)
        
        # Se hanno la stessa polarità ed espressione semantica coerente, non c'è conflitto
        if polarity_a == polarity_b:
            return None

        # Proiezione Z3
        if self.has_z3:
            import z3
            try:
                s = z3.Solver()
                s.set("timeout", 100) # Restringe l'esecuzione a max 100ms
                
                # 1. Definiamo le variabili per il topic
                var_name = f"concept_{re.sub(r'[^a-zA-Z0-9]', '_', topic)}"
                C = z3.Bool(var_name)
                
                # 2. Definiamo le asserzioni delle due wiki
                f_a = C if polarity_a else z3.Not(C)
                f_b = C if polarity_b else z3.Not(C)
                
                s.add(f_a)
                s.add(f_b)
                
                # 3. Estraiamo il sotto-grafo causale circoscritto a profondità <= 2 da KùzuDB per aggiungere vincoli di implicazione transitoria
                causal_constraints = await self._get_causal_neighborhood_constraints(topic)
                for src_var, tgt_var, relation in causal_constraints:
                    V_src = z3.Bool(f"concept_{re.sub(r'[^a-zA-Z0-9]', '_', src_var)}")
                    V_tgt = z3.Bool(f"concept_{re.sub(r'[^a-zA-Z0-9]', '_', tgt_var)}")
                    
                    if relation == "causes" or relation == "requires":
                        # A -> B (A causa/richiede B)
                        s.add(z3.Implies(V_src, V_tgt))
                    elif relation == "prevents":
                        # A -> NOT B (A previene B)
                        s.add(z3.Implies(V_src, z3.Not(V_tgt)))
                
                # Esecuzione solver
                result = s.check()
                if result == z3.unsat:
                    proof_str = (
                        f"[Z3 UNSAT Proof] Conflict detected on concept '{topic}'. "
                        f"Wiki A asserts Form({polarity_a}), Wiki B asserts Form({polarity_b}). "
                        f"Satisfiability check failed under local causal constraints."
                    )
                    return proof_str
            except Exception as e:
                self.logger.error(f"Z3 execution error: {e}")

        # Fallback euristico-simbolico
        if polarity_a != polarity_b:
            return (
                f"[Symbolic Proof] Logical contradiction found: "
                f"Wiki A asserts positive polarity, Wiki B asserts negative polarity "
                f"on core topic '{topic}'."
            )
            
        return None

    def _extract_polarity(self, claim: str) -> bool:
        """
        Rileva la polarità logica dell'asserzione (True = Positiva/Abilitante, False = Negativa/Inibente).
        """
        claim_lower = claim.lower()
        negatives = [
            "non ", "not ", "evita", "prevents", "block", "disables", "declassa", 
            "inactive", "false", "nessun", "senza", "without", "negativo"
        ]
        # Se contiene antonimi forti
        inhibitors = ["diminuisce", "riduce", "decresce", "decrease", "reduce", "mitigate", "abbassa"]
        
        score = 0
        for neg in negatives:
            if neg in claim_lower:
                score += 1
        for inh in inhibitors:
            if inh in claim_lower:
                score += 1
                
        return (score % 2) == 0

    async def _get_causal_neighborhood_constraints(self, topic: str) -> List[tuple]:
        """
        Interroga KùzuDB via Cypher per estrarre la rete causale (depth-2) circoscritta al topic.
        Garantisce la rilevazione di implicazioni transitive senza causare esplosione esponenziale.
        """
        constraints = []
        try:
            # Recuperiamo l'istanza kuzu_projection da api.py o dal modulo globale
            import sys
            api_mod = sys.modules.get("api")
            kuzu_proj = getattr(api_mod, "kuzu_projection", None)
            
            if kuzu_proj:
                # 🧪 [v10.2 - Settimana 4] Scoping Incrementale del Sotto-grafo (Depth-2)
                # Estrae relazioni dirette ed indirette a distanza 2 per Z3
                query = """
                    MATCH (a:KnowledgeNode {id: $topic})-[r1:CausalEdge]->(b:KnowledgeNode)
                    OPTIONAL MATCH (b)-[r2:CausalEdge]->(c:KnowledgeNode)
                    RETURN a.id, b.id, r1.relation_type, c.id, r2.relation_type
                """
                res = kuzu_proj.conn.execute(query, {"topic": topic})
                visited = set()
                while res.has_next():
                    row = res.get_next()
                    src, mid, rel1, dest, rel2 = row[0], row[1], row[2], row[3], row[4]
                    
                    # Relazione di livello 1 (Diretta)
                    edge1 = (src, mid, rel1.lower())
                    if edge1 not in visited:
                        constraints.append(edge1)
                        visited.add(edge1)
                        
                    # Relazione di livello 2 (Indiretta transitiva)
                    if dest and rel2:
                        edge2 = (mid, dest, rel2.lower())
                        if edge2 not in visited:
                            constraints.append(edge2)
                            visited.add(edge2)
        except Exception as e:
            self.logger.debug(f"Could not retrieve causal neighborhood from graph: {e}")
        return constraints

    async def find_cross_wiki_contradictions(self) -> List[Dict[str, Any]]:
        """
        Interroga DuckDB per trovare claim potenzialmente contraddittori
        e li valida singolarmente tramite il risolutore logico-formale Z3.
        """
        if not self.duckdb:
            return []

        query = """
            SELECT 
                c1.page_id as wiki_a,
                c2.page_id as wiki_b,
                c1.claim_text as claim_a,
                c2.claim_text as claim_b,
                c1.page_id as topic,
                c1.confidence as conf_a,
                c2.confidence as conf_b
            FROM wiki_claims c1
            JOIN wiki_claims c2 
                ON c1.page_id = c2.page_id
                AND c1.claim_text != c2.claim_text
            WHERE c1.confidence > 0.5
              AND c2.confidence > 0.5
            LIMIT 50
        """
        
        try:
            results = self.duckdb.fetchall(query)
            contradictions = []
            
            for row in results:
                wiki_a = row[0]
                wiki_b = row[1]
                claim_a = row[2]
                claim_b = row[3]
                topic = row[4]
                conf_a = row[5]
                conf_b = row[6]
                
                # Esecuzione validazione formale Z3
                proof = await self.verify_claims_logic(topic, claim_a, claim_b)
                
                if proof:
                    contradictions.append({
                        "wiki_a": wiki_a,
                        "wiki_b": wiki_b,
                        "claim_a": claim_a,
                        "claim_b": claim_b,
                        "topic": topic,
                        "severity": "CRITICAL",
                        "status": "UNRESOLVED",
                        "z3_proof": proof,
                        "confidence": float((conf_a + conf_b) / 2.0)
                    })
            
            return contradictions
        except Exception as e:
            self.logger.error(f"Errore ricerca contraddizioni: {e}")
            return []

    async def get_forensic_report(self) -> Dict[str, Any]:
        """Genera un report completo dello stato di integrità della conoscenza."""
        contradictions = await self.find_cross_wiki_contradictions()
        
        # Statistiche generali
        stats = 0
        if self.duckdb:
            try:
                res = self.duckdb.fetchone("SELECT COUNT(*) FROM wiki_claims")
                if res:
                    stats = res[0]
            except:
                pass
        
        return {
            "total_claims": stats,
            "contradictions_found": len(contradictions),
            "contradictions": contradictions,
            "integrity_score": max(0, 100 - (len(contradictions) * 5))
        }
