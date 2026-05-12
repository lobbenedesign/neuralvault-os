import logging
import json
import re
import hashlib
from typing import List, Dict, Any, Optional
from datetime import datetime

class IdentityMiner:
    """
    🧬 [v8.2] E2P Pipeline (Entity-to-Persona).
    Estrae identità operative, ruoli e pattern comportamentali dai documenti del Vault.
    """
    
    def __init__(self, db_engine):
        self.db = db_engine
        self.logger = logging.getLogger("IdentityMiner")
        self.persona_kernels = {} # Cache locale dei profili

    async def mine_identities(self, document_id: str, text: str) -> List[Dict[str, Any]]:
        """Scansiona un documento per identificare attori e i loro ruoli."""
        self.logger.info(f"Mining identità nel documento: {document_id}")
        
        # 1. Estrazione Entità Persona (NER Logic)
        # In una versione avanzata useremo spaCy/LayoutLM. Qui usiamo pattern strutturati.
        entities = self._extract_candidate_entities(text)
        
        # 2. Role & Action Mapping
        for entity in entities:
            entity['role'] = self._detect_role(entity['name'], text)
            entity['fingerprint'] = self._analyze_communication_style(entity['name'], text)
            
            # Salvataggio nel Graph DB (Persona Kernel)
            await self._update_persona_kernel(entity)
            
        return entities

    def _extract_candidate_entities(self, text: str) -> List[Dict]:
        """Identifica nomi e organizzazioni basandosi su firme e metadati."""
        candidates = []
        # Pattern per firme: "Cordiali saluti, [Nome] [Cognome]" o "Responsabile: [Nome]"
        signature_patterns = [
            r"(?:Saluti|Cordiali saluti|Firma|Responsabile|Ing\.|Dott\.)\s*([A-Z][a-z]+\s[A-Z][a-z]+)",
            r"([A-Z][a-z]+\s[A-Z][a-z]+)\s*(?:Responsabile|Direttore|Manager)"
        ]
        
        for pattern in signature_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                name = match.group(1).strip()
                if name not in [c['name'] for c in candidates]:
                    candidates.append({"name": name, "type": "PERSON"})
        
        return candidates

    def _detect_role(self, name: str, text: str) -> str:
        """Determina il ruolo formale dell'entità nel contesto del documento."""
        role_keywords = ["GSE", "Responsabile", "Direttore", "Committente", "Subappaltatore", "Legale"]
        context = text[max(0, text.find(name)-100) : text.find(name)+100]
        
        for role in role_keywords:
            if role.lower() in context.lower():
                return role
        return "Unknown"

    def _analyze_communication_style(self, name: str, text: str) -> Dict[str, Any]:
        """🧬 [v8.2] Analizza il DNA stilistico e comportamentale (Action Histograms & Lexicon)."""
        # 1. Lexicon Profile: Estrazione parole chiave ricorrenti
        keywords = ["penale", "contestazione", "diffida", "ritardo", "proroga", "approvazione", "conformità"]
        lexicon = {w: text.lower().count(w) for w in keywords if text.lower().count(w) > 0}
        
        # 2. Action Histogram: Mappatura azioni intraprese
        actions = {
            "DISPUTE": text.lower().count("contestazione") + text.lower().count("diffida"),
            "APPROVAL": text.lower().count("approvato") + text.lower().count("accettato"),
            "DELAY_REQUEST": text.lower().count("proroga") + text.lower().count("ritardo")
        }
        
        # 3. Tone & Formality
        is_formal = any(word in text.lower() for word in ["spett.le", "egregio", "distinti saluti"])
        
        return {
            "tone": "Formal" if is_formal else "Casual",
            "action_histogram": actions,
            "lexicon_profile": lexicon,
            "risk_aversion_score": round(actions["DISPUTE"] / (sum(actions.values()) + 1), 2)
        }

    async def _update_persona_kernel(self, entity: Dict):
        """Aggiorna o crea il nodo Persona nel Grafo Causale via DuckDB."""
        # Unificazione Identità (Coreference Resolution semplificata)
        clean_name = re.sub(r"^(Ing\.|Dott\.|Arch\.|Avv\.)\s*", "", entity['name'])
        entity_id = hashlib.sha256(clean_name.encode()).hexdigest()[:12]
        
        try:
            # Recupera fingerprint esistente per merge (Action Histogram)
            existing = self.get_persona(clean_name)
            if existing:
                # Merge degli istogrammi delle azioni
                new_actions = entity['fingerprint']['action_histogram']
                old_actions = existing['fingerprint'].get('action_histogram', {})
                for k, v in new_actions.items():
                    entity['fingerprint']['action_histogram'][k] = v + old_actions.get(k, 0)
            
            self.db.execute("""
                INSERT OR REPLACE INTO persona_kernels 
                (entity_id, canonical_name, roles, behavioral_fingerprint, last_seen)
                VALUES (?, ?, ?, ?, now())
            """, (
                entity_id, 
                clean_name, 
                json.dumps([entity['role']]), 
                json.dumps(entity['fingerprint'])
            ))
            self.logger.info(f"Persona Kernel aggiornato: {clean_name} (ID: {entity_id})")
        except Exception as e:
            self.logger.error(f"Errore persistenza Persona Kernel: {e}")

    def get_persona(self, name: str) -> Optional[Dict]:
        """Recupera un profilo persona dal database (supporta nomi puliti)."""
        clean_name = re.sub(r"^(Ing\.|Dott\.|Arch\.|Avv\.)\s*", "", name)
        res = self.db.execute("SELECT * FROM persona_kernels WHERE canonical_name = ?", (clean_name,)).fetchone()
        if res:
            return {
                "id": res[0],
                "name": res[1],
                "roles": json.loads(res[2]) if isinstance(res[2], str) else res[2],
                "fingerprint": json.loads(res[3]) if isinstance(res[3], str) else res[3]
            }
        return None
