"""
core/network/mesh_core.py
───────────────────────────
🏺 NEURALVAULT v11.3.0: Sovereign Mesh Network Layer
Decentralised Peer-to-Peer network stack incorporating:
1. P2P Multiplexed TCP Server & Client Connections.
2. Noise Encryption Handshake (X25519 Diffie-Hellman + AES-256-GCM).
3. mDNS Local Peering Discovery (via ZeroConf).
4. Kademlia-inspired DHT Routing Table utilizing XOR distance metric.
"""

import asyncio
import hashlib
import json
import logging
import os
import socket
import struct
from typing import Dict, List, Optional, Tuple, Set

from cryptography.hazmat.primitives.asymmetric import x25519
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes
from zeroconf import IPVersion, ServiceInfo, Zeroconf, ServiceBrowser, ServiceListener

# Configure logging
logger = logging.getLogger("Mesh-Core")


class PeerInfo:
    """Represents a discovered or connected peer."""
    def __init__(self, peer_id: str, host: str, port: int, pub_key_bytes: bytes = b""):
        self.peer_id = peer_id
        self.host = host
        self.port = port
        self.pub_key_bytes = pub_key_bytes
        self.distance: int = 0  # Calculated dynamically based on target node query

    def __repr__(self) -> str:
        return f"PeerInfo({self.peer_id[:8]}@{self.host}:{self.port})"


class NoiseSession:
    """Manages an encrypted session between two peers using Noise-like protocol."""
    def __init__(self, aes_key: bytes):
        self.aes_key = aes_key
        self.aes_gcm = AESGCM(aes_key)
        self.encrypt_nonce_counter = 0
        self.decrypt_nonce_counter = 0

    def _next_nonce(self, is_encrypt: bool) -> bytes:
        counter = self.encrypt_nonce_counter if is_encrypt else self.decrypt_nonce_counter
        # Format counter as 12-byte big-endian nonce
        nonce = struct.pack(">Q", counter).rjust(12, b"\x00")
        if is_encrypt:
            self.encrypt_nonce_counter += 1
        else:
            self.decrypt_nonce_counter += 1
        return nonce

    def encrypt(self, plaintext: bytes) -> bytes:
        nonce = self._next_nonce(is_encrypt=True)
        ciphertext = self.aes_gcm.encrypt(nonce, plaintext, None)
        return nonce + ciphertext

    def decrypt(self, encrypted_payload: bytes) -> bytes:
        if len(encrypted_payload) < 12:
            raise ValueError("Payload too short to extract nonce.")
        nonce = encrypted_payload[:12]
        ciphertext = encrypted_payload[12:]
        return self.aes_gcm.decrypt(nonce, ciphertext, None)


class KademliaRoutingTable:
    """
    Kademlia routing table based on XOR metric.
    Organizes peers into distance-based buckets.
    """
    def __init__(self, local_peer_id: str, k: int = 20):
        self.local_peer_id = local_peer_id
        self.local_int = int(hashlib.sha256(local_peer_id.encode()).hexdigest(), 16)
        self.k = k
        # Buckets represent logarithmic distance bands from 0 to 256
        self.buckets: List[List[PeerInfo]] = [[] for _ in range(256)]

    def _xor_distance(self, peer_id: str) -> int:
        peer_int = int(hashlib.sha256(peer_id.encode()).hexdigest(), 16)
        return self.local_int ^ peer_int

    def _get_bucket_index(self, distance: int) -> int:
        if distance == 0:
            return 0
        return min(distance.bit_length() - 1, 255)

    def add_peer(self, peer: PeerInfo) -> bool:
        if peer.peer_id == self.local_peer_id:
            return False
        dist = self._xor_distance(peer.peer_id)
        idx = self._get_bucket_index(dist)
        bucket = self.buckets[idx]

        # Check if already present
        for existing in bucket:
            if existing.peer_id == peer.peer_id:
                # Update connection details and move to end (recently seen)
                bucket.remove(existing)
                bucket.append(peer)
                return True

        if len(bucket) < self.k:
            bucket.append(peer)
            return True
        else:
            # Bucket is full, standard Kademlia would ping the oldest, 
            # here we just return False for simplicity
            return False

    def remove_peer(self, peer_id: str) -> None:
        dist = self._xor_distance(peer_id)
        idx = self._get_bucket_index(dist)
        self.buckets[idx] = [p for p in self.buckets[idx] if p.peer_id != peer_id]

    def get_closest_peers(self, target_peer_id: str, limit: int = 10) -> List[PeerInfo]:
        target_int = int(hashlib.sha256(target_peer_id.encode()).hexdigest(), 16)
        
        all_peers: List[PeerInfo] = []
        for bucket in self.buckets:
            all_peers.extend(bucket)

        # Calculate absolute XOR distance from target
        for peer in all_peers:
            peer_int = int(hashlib.sha256(peer.peer_id.encode()).hexdigest(), 16)
            peer.distance = target_int ^ peer_int

        all_peers.sort(key=lambda x: x.distance)
        return all_peers[:limit]


class SovereignMeshNode:
    """
    Decentralised Peer-to-Peer node powered by ZeroConf mDNS discovery,
    Noise cryptography, and Kademlia DHT routing.
    """
    def __init__(self, host: str = "127.0.0.1", port: int = 0, node_id: Optional[str] = None, enable_mdns: bool = True):
        self.host = host
        self.port = port
        self.node_id = node_id or f"peer_{hashlib.sha256(os.urandom(16)).hexdigest()[:12]}"
        self.enable_mdns = enable_mdns
        
        # Crypto key generation (Noise keypair)
        self.noise_private_key = x25519.X25519PrivateKey.generate()
        self.noise_public_bytes = self.noise_private_key.public_key().public_bytes_raw()

        # Routing and Session management
        self.routing_table = KademliaRoutingTable(self.node_id)
        self.sessions: Dict[str, NoiseSession] = {}
        self.active_connections: Dict[str, Tuple[asyncio.StreamReader, asyncio.StreamWriter]] = {}

        # mDNS
        self.zeroconf: Optional[Zeroconf] = None
        self.browser: Optional[ServiceBrowser] = None
        self.service_info: Optional[ServiceInfo] = None
        
        self._server: Optional[asyncio.AbstractServer] = None
        self.is_running = False

    async def start(self) -> int:
        """Starts the P2P listener server and registers mDNS discovery service."""
        # 1. Bind P2P server
        self._server = await asyncio.start_server(
            self._handle_incoming_connection, self.host, self.port
        )
        # Update bound port if 0 was passed
        self.port = self._server.sockets[0].getsockname()[1]
        
        self.is_running = True
        logger.info(f"🔮 [Mesh Node] Listening on tcp://{self.host}:{self.port} (ID: {self.node_id})")

        # Start task to run server
        asyncio.create_task(self._server.serve_forever())

        # 2. Initialize mDNS Local Discovery
        if self.enable_mdns:
            try:
                self.zeroconf = Zeroconf(ip_version=IPVersion.V4Only)
                desc = {
                    "node_id": self.node_id,
                    "pub_key": self.noise_public_bytes.hex(),
                    "version": "11.3.0"
                }
                self.service_info = ServiceInfo(
                    "_neuralvault-p2p._tcp.local.",
                    f"{self.node_id}._neuralvault-p2p._tcp.local.",
                    addresses=[socket.inet_aton(self.host)],
                    port=self.port,
                    properties=desc,
                    server=f"{self.node_id}.local."
                )
                self.zeroconf.register_service(self.service_info)
                logger.info(f"📡 [mDNS] Registered local P2P service: {self.node_id} on port {self.port}")

                # Start searching for peers
                listener = mDNSMeshListener(self)
                self.browser = ServiceBrowser(self.zeroconf, "_neuralvault-p2p._tcp.local.", listener)
            except Exception as e:
                logger.warning(f"⚠️ [mDNS] Discovery initialization failed (perhaps offline): {e}")

        return self.port

    async def stop(self) -> None:
        """Gracefully shuts down the P2P server and unregisters local service."""
        self.is_running = False
        
        # Unregister mDNS
        if self.zeroconf:
            try:
                if self.service_info:
                    self.zeroconf.unregister_service(self.service_info)
            except Exception as e:
                logger.debug(f"mDNS unregister failed: {e}")
            try:
                self.zeroconf.close()
            except Exception as e:
                logger.debug(f"mDNS close failed: {e}")
            self.zeroconf = None
        
        # Close active connections
        for peer_id, (_, writer) in list(self.active_connections.items()):
            try:
                writer.close()
                await writer.wait_closed()
            except Exception:
                pass
        self.active_connections.clear()
        self.sessions.clear()

        # Stop server
        if self._server:
            self._server.close()
            await self._server.wait_closed()
            self._server = None

        logger.info(f"🛑 [Mesh Node] Node tcp://{self.host}:{self.port} stopped.")

    async def connect_to_peer(self, host: str, port: int) -> Optional[str]:
        """Connects to a remote peer and performs the secure Noise cryptographic handshake."""
        try:
            reader, writer = await asyncio.open_connection(host, port)
            
            # Execute Handshake
            peer_id, session = await self._perform_outbound_handshake(reader, writer)
            if peer_id and session:
                self.active_connections[peer_id] = (reader, writer)
                self.sessions[peer_id] = session
                
                # Add peer info to Kademlia routing table
                peer_info = PeerInfo(peer_id, host, port, pub_key_bytes=b"")
                self.routing_table.add_peer(peer_info)
                
                # Launch message listener for this connection
                asyncio.create_task(self._listen_to_peer(peer_id, reader))
                logger.info(f"🔒 [Noise Handshake] Connection secure with {peer_id[:8]} at {host}:{port}")
                return peer_id
        except Exception as e:
            logger.debug(f"⚠️ Failed to connect to peer at {host}:{port}: {e}")
        return None

    async def send_secure_message(self, peer_id: str, message: Dict) -> bool:
        """Sends an encrypted frame-length prefixed message to a connected peer."""
        conn = self.active_connections.get(peer_id)
        session = self.sessions.get(peer_id)
        if not conn or not session:
            logger.warning(f"⚠️ Cannot send message: No active session for {peer_id[:8]}")
            return False

        _, writer = conn
        try:
            serialized = json.dumps(message).encode("utf-8")
            encrypted = session.encrypt(serialized)
            
            # Prefix with length header (4 bytes big-endian)
            header = struct.pack(">I", len(encrypted))
            writer.write(header + encrypted)
            await writer.drain()
            return True
        except Exception as e:
            logger.error(f"❌ Error sending P2P message to {peer_id[:8]}: {e}")
            self._handle_peer_disconnection(peer_id)
            return False

    async def _handle_incoming_connection(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        """Invoked when a remote peer initiates a connection to our TCP server."""
        try:
            peer_id, session = await self._perform_inbound_handshake(reader, writer)
            if peer_id and session:
                self.active_connections[peer_id] = (reader, writer)
                self.sessions[peer_id] = session
                
                # Add to routing table
                addr = writer.get_extra_info("peername")
                peer_info = PeerInfo(peer_id, addr[0], addr[1], pub_key_bytes=b"")
                self.routing_table.add_peer(peer_info)

                # Launch message listener
                asyncio.create_task(self._listen_to_peer(peer_id, reader))
                logger.info(f"🔒 [Noise Handshake] Secure session established by inbound peer {peer_id[:8]}")
        except Exception as e:
            logger.debug(f"⚠️ Secure handshake failed on inbound connection: {e}")
            writer.close()
            await writer.wait_closed()

    async def _perform_outbound_handshake(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> Tuple[Optional[str], Optional[NoiseSession]]:
        """
        Executes outbound cryptographic Noise handshake.
        We send our NodeID, local Port, and Ephemeral Public Key.
        We expect the remote peer's NodeID, Port, and Ephemeral Public Key.
        """
        # 1. Send Handshake Init Frame
        handshake_data = {
            "node_id": self.node_id,
            "listening_port": self.port,
            "ephemeral_key": self.noise_public_bytes.hex()
        }
        raw_send = json.dumps(handshake_data).encode("utf-8")
        writer.write(struct.pack(">I", len(raw_send)) + raw_send)
        await writer.drain()

        # 2. Read Response Init Frame
        header = await reader.readexactly(4)
        frame_len = struct.unpack(">I", header)[0]
        raw_recv = await reader.readexactly(frame_len)
        resp_data = json.loads(raw_recv.decode("utf-8"))

        peer_id = resp_data["node_id"]
        peer_ephemeral_key_hex = resp_data["ephemeral_key"]
        
        # 3. Compute Diffie-Hellman Ephemeral Secret
        peer_pub_bytes = bytes.fromhex(peer_ephemeral_key_hex)
        peer_pub_key = x25519.X25519PublicKey.from_public_bytes(peer_pub_bytes)
        shared_secret = self.noise_private_key.exchange(peer_pub_key)

        # 4. Derive AES Key via HKDF
        hkdf = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=None,
            info=b"neuralvault-noise-handshake",
        )
        aes_key = hkdf.derive(shared_secret)
        
        return peer_id, NoiseSession(aes_key)

    async def _perform_inbound_handshake(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> Tuple[Optional[str], Optional[NoiseSession]]:
        """
        Executes inbound cryptographic Noise handshake.
        Processes connection request and exchanges Ephemeral Keys.
        """
        # 1. Read Remote Init Frame
        header = await reader.readexactly(4)
        frame_len = struct.unpack(">I", header)[0]
        raw_recv = await reader.readexactly(frame_len)
        req_data = json.loads(raw_recv.decode("utf-8"))

        peer_id = req_data["node_id"]
        peer_ephemeral_key_hex = req_data["ephemeral_key"]

        # 2. Send Local Response Handshake Frame
        handshake_data = {
            "node_id": self.node_id,
            "listening_port": self.port,
            "ephemeral_key": self.noise_public_bytes.hex()
        }
        raw_send = json.dumps(handshake_data).encode("utf-8")
        writer.write(struct.pack(">I", len(raw_send)) + raw_send)
        await writer.drain()

        # 3. Compute Shared Secret & Key Derivation
        peer_pub_bytes = bytes.fromhex(peer_ephemeral_key_hex)
        peer_pub_key = x25519.X25519PublicKey.from_public_bytes(peer_pub_bytes)
        shared_secret = self.noise_private_key.exchange(peer_pub_key)

        hkdf = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=None,
            info=b"neuralvault-noise-handshake",
        )
        aes_key = hkdf.derive(shared_secret)

        return peer_id, NoiseSession(aes_key)

    async def _listen_to_peer(self, peer_id: str, reader: asyncio.StreamReader) -> None:
        """Asynchronously listens to frame payloads on a specific peer socket."""
        session = self.sessions.get(peer_id)
        if not session:
            return

        try:
            while self.is_running:
                # Read 4-byte header length
                header = await reader.readexactly(4)
                frame_len = struct.unpack(">I", header)[0]
                
                # Read dynamic encrypted frame
                encrypted_payload = await reader.readexactly(frame_len)
                
                # Decrypt payload
                decrypted = session.decrypt(encrypted_payload)
                message = json.loads(decrypted.decode("utf-8"))
                
                # Handle received protocol messages
                await self._handle_protocol_message(peer_id, message)
        except asyncio.IncompleteReadError:
            logger.debug(f"ℹ️ Peer {peer_id[:8]} disconnected (EOF reached).")
        except Exception as e:
            logger.debug(f"⚠️ Connection read error from {peer_id[:8]}: {e}")
        finally:
            self._handle_peer_disconnection(peer_id)

    async def _handle_protocol_message(self, peer_id: str, message: Dict) -> None:
        """Processes structured P2P protocol RPC commands."""
        msg_type = message.get("type")
        logger.debug(f"📩 [Protocol Message] Received {msg_type} from {peer_id[:8]}")

        if msg_type == "DHT_FIND_NODE":
            target = message.get("target")
            closest = self.routing_table.get_closest_peers(target, limit=5)
            
            # Format closest peers as list of dicts
            serialized_peers = [
                {"peer_id": p.peer_id, "host": p.host, "port": p.port} for p in closest
            ]
            response = {
                "type": "DHT_FIND_NODE_RESPONSE",
                "request_id": message.get("request_id"),
                "peers": serialized_peers
            }
            await self.send_secure_message(peer_id, response)

        elif msg_type == "PING":
            await self.send_secure_message(peer_id, {"type": "PONG", "request_id": message.get("request_id")})

    def _handle_peer_disconnection(self, peer_id: str) -> None:
        """Cleans up structures when a peer connection goes offline."""
        conn = self.active_connections.pop(peer_id, None)
        if conn:
            _, writer = conn
            try:
                writer.close()
            except Exception:
                pass
        self.sessions.pop(peer_id, None)
        self.routing_table.remove_peer(peer_id)


class mDNSMeshListener(ServiceListener):
    """ZeroConf Listener responding to found NeuralVault P2P peer instances."""
    def __init__(self, node: SovereignMeshNode):
        self.node = node

    def add_service(self, zc: Zeroconf, type_: str, name: str) -> None:
        info = zc.get_service_info(type_, name)
        if info:
            node_id = info.properties.get(b"node_id", b"").decode("utf-8")
            if node_id and node_id != self.node.node_id:
                # Add to routing table and connect in background
                addresses = [socket.inet_ntoa(addr) for addr in info.addresses]
                if addresses:
                    host = addresses[0]
                    port = info.port
                    logger.info(f"✨ [mDNS Discovery] Discovered local peer {node_id[:8]} at {host}:{port}")
                    
                    # Establish secure session in the background
                    asyncio.create_task(self.node.connect_to_peer(host, port))

    def update_service(self, zc: Zeroconf, type_: str, name: str) -> None:
        pass

    def remove_service(self, zc: Zeroconf, type_: str, name: str) -> None:
        pass
