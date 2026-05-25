"""
security/mesh_crypto.py
───────────────────────
Implementazione della crittografia X25519 ed Ed25519 per la Mesh di NeuralVault.
Gestisce lo scambio di chiavi (X25519), la cifratura simmetrica (AES-GCM) per i tunnel 
e la firma digitale asimmetrica (Ed25519) per il Consenso Epistemico 2.0.
"""

import os
import json
import base64
import time
from pathlib import Path
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import x25519, ed25519
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

class SovereignMeshCrypto:
    def __init__(self, data_dir: Path, force_rotate: bool = False):
        self.keys_path = data_dir / "mesh_keys.json"
        self._private_key = None
        self.public_key_bytes = None
        
        # Chiavi per firme digitali asimmetriche Ed25519 (Sovereign Vault Key)
        self._ed25519_private_key = None
        
        self._load_or_generate_keys(force_rotate=force_rotate)

    def _load_or_generate_keys(self, force_rotate: bool = False):
        if self.keys_path.exists() and not force_rotate:
            try:
                with open(self.keys_path, "r") as f:
                    data = json.load(f)
                    
                    # 1. Carica X25519 Key Agreement
                    if "private_key" in data:
                        priv_bytes = base64.b64decode(data["private_key"])
                        self._private_key = x25519.X25519PrivateKey.from_private_bytes(priv_bytes)
                        
                    # 2. Carica Ed25519 Signature Key
                    if "signature_private_key" in data:
                        sig_priv_bytes = base64.b64decode(data["signature_private_key"])
                        self._ed25519_private_key = ed25519.Ed25519PrivateKey.from_private_bytes(sig_priv_bytes)
            except Exception as e:
                print(f"⚠️ [Crypto] Errore caricamento chiavi: {e}. Rigenerazione...")
        
        # Rigenerazione / Generazione chiavi mancanti
        needs_save = False
        
        if not self._private_key:
            self._private_key = x25519.X25519PrivateKey.generate()
            needs_save = True
            
        if not self._ed25519_private_key:
            self._ed25519_private_key = ed25519.Ed25519PrivateKey.generate()
            needs_save = True
            
        if needs_save:
            priv_bytes = self._private_key.private_bytes_raw()
            sig_priv_bytes = self._ed25519_private_key.private_bytes_raw()
            
            self.keys_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.keys_path, "w") as f:
                json.dump({
                    "private_key": base64.b64encode(priv_bytes).decode('utf-8'),
                    "signature_private_key": base64.b64encode(sig_priv_bytes).decode('utf-8'),
                    "created_at": time.time()
                }, f)

        self.public_key_bytes = self._private_key.public_key().public_bytes_raw()

    def get_public_key_base64(self) -> str:
        return base64.b64encode(self.public_key_bytes).decode('utf-8')

    def derive_shared_key(self, peer_public_key_base64: str) -> bytes:
        """Deriva una chiave simmetrica da 256 bit usando X25519 + HKDF."""
        peer_public_bytes = base64.b64decode(peer_public_key_base64)
        peer_public_key = x25519.X25519PublicKey.from_public_bytes(peer_public_bytes)
        
        shared_secret = self._private_key.exchange(peer_public_key)
        
        # HKDF per estrarre una chiave robusta dal segreto condiviso
        derived_key = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=None,
            info=b"neuralvault-mesh-sync",
        ).derive(shared_secret)
        
        return derived_key

    def encrypt(self, data: str, shared_key: bytes) -> str:
        """Cifra i dati usando AES-GCM."""
        aesgcm = AESGCM(shared_key)
        nonce = os.urandom(12)
        ciphertext = aesgcm.encrypt(nonce, data.encode('utf-8'), None)
        # Formato: nonce + ciphertext (base64)
        return base64.b64encode(nonce + ciphertext).decode('utf-8')

    def decrypt(self, encrypted_data: str, shared_key: bytes) -> str:
        """Decifra i dati usando AES-GCM."""
        aesgcm = AESGCM(shared_key)
        raw_data = base64.b64decode(encrypted_data)
        nonce = raw_data[:12]
        ciphertext = raw_data[12:]
        decrypted = aesgcm.decrypt(nonce, ciphertext, None)
        return decrypted.decode('utf-8')

    # --- ED25519 SIGNATURES & VERIFICATION (Epistemic Consensus 2.0) ---

    def get_signature_public_key_base64(self) -> str:
        """Ritorna la chiave pubblica Ed25519 codificata in Base64 (Sovereign Vault Key)."""
        pub_bytes = self._ed25519_private_key.public_key().public_bytes_raw()
        return base64.b64encode(pub_bytes).decode('utf-8')

    def sign_message(self, message: str) -> str:
        """Firma asimmetricamente un messaggio stringa con Ed25519."""
        signature = self._ed25519_private_key.sign(message.encode('utf-8'))
        return base64.b64encode(signature).decode('utf-8')

    @staticmethod
    def verify_signature(public_key_base64: str, signature_base64: str, message: str) -> bool:
        """Verifica una firma digitale Ed25519 contro una chiave pubblica e il messaggio originale."""
        try:
            pub_bytes = base64.b64decode(public_key_base64)
            sig_bytes = base64.b64decode(signature_base64)
            pub_key = ed25519.Ed25519PublicKey.from_public_bytes(pub_bytes)
            pub_key.verify(sig_bytes, message.encode('utf-8'))
            return True
        except Exception:
            return False

