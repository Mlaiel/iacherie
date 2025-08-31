"""
End-to-End Encryption Module
Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

End-to-end encryption for secure communications between clients and servers.
"""

import os
import json
import base64
import secrets
from typing import Dict, Optional, Tuple, Any, List
from datetime import datetime, timedelta
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey, X25519PublicKey
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import logging

logger = logging.getLogger(__name__)


class KeyExchange:
    """
    Elliptic Curve Diffie-Hellman (ECDH) key exchange using X25519.
    Provides forward secrecy for end-to-end encryption.
    """
    
    def __init__(self):
        self.private_key = X25519PrivateKey.generate()
        self.public_key = self.private_key.public_key()
    
    def get_public_key_bytes(self) -> bytes:
        """Get public key as bytes for transmission."""
        return self.public_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw
        )
    
    def get_public_key_b64(self) -> str:
        """Get public key as base64 string."""
        return base64.b64encode(self.get_public_key_bytes()).decode('utf-8')
    
    def derive_shared_secret(self, peer_public_key_bytes: bytes) -> bytes:
        """
        Derive shared secret from peer's public key.
        
        Args:
            peer_public_key_bytes: Peer's public key bytes
            
        Returns:
            Derived shared secret
        """
        try:
            peer_public_key = X25519PublicKey.from_public_bytes(peer_public_key_bytes)
            shared_key = self.private_key.exchange(peer_public_key)
            
            # Derive encryption key using HKDF
            hkdf = HKDF(
                algorithm=hashes.SHA256(),
                length=32,
                salt=None,
                info=b'Ainflue E2E Encryption v1.0',
                backend=default_backend()
            )
            
            return hkdf.derive(shared_key)
            
        except Exception as e:
            logger.error(f"Key derivation failed: {str(e)}")
            raise
    
    @staticmethod
    def from_public_key_b64(public_key_b64: str) -> bytes:
        """Convert base64 public key to bytes."""
        return base64.b64decode(public_key_b64)


class E2ESession:
    """
    End-to-end encryption session with key rotation support.
    """
    
    def __init__(self, session_id: Optional[str] = None):
        self.session_id = session_id or secrets.token_urlsafe(32)
        self.key_exchange = KeyExchange()
        self.shared_secret: Optional[bytes] = None
        self.message_counter = 0
        self.created_at = datetime.utcnow()
        self.last_key_rotation = self.created_at
        self.max_messages_per_key = 1000
        self.key_rotation_interval = timedelta(hours=1)
    
    def establish_session(self, peer_public_key_b64: str) -> Dict[str, Any]:
        """
        Establish E2E session with peer.
        
        Args:
            peer_public_key_b64: Peer's public key in base64
            
        Returns:
            Session establishment response
        """
        try:
            peer_public_key_bytes = KeyExchange.from_public_key_b64(peer_public_key_b64)
            self.shared_secret = self.key_exchange.derive_shared_secret(peer_public_key_bytes)
            
            return {
                'session_id': self.session_id,
                'public_key': self.key_exchange.get_public_key_b64(),
                'established': True,
                'created_at': self.created_at.isoformat(),
                'algorithm': 'X25519+AES-256-GCM'
            }
            
        except Exception as e:
            logger.error(f"Session establishment failed: {str(e)}")
            return {
                'session_id': self.session_id,
                'established': False,
                'error': str(e)
            }
    
    def should_rotate_keys(self) -> bool:
        """Check if keys should be rotated."""
        time_based = datetime.utcnow() - self.last_key_rotation > self.key_rotation_interval
        message_based = self.message_counter >= self.max_messages_per_key
        return time_based or message_based
    
    def rotate_keys(self) -> Dict[str, str]:
        """
        Rotate encryption keys for forward secrecy.
        
        Returns:
            New public key for peer
        """
        try:
            # Generate new key pair
            self.key_exchange = KeyExchange()
            self.message_counter = 0
            self.last_key_rotation = datetime.utcnow()
            
            logger.info(f"Keys rotated for session {self.session_id}")
            
            return {
                'session_id': self.session_id,
                'new_public_key': self.key_exchange.get_public_key_b64(),
                'rotated_at': self.last_key_rotation.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Key rotation failed: {str(e)}")
            raise
    
    def encrypt_message(self, plaintext: str, additional_data: Optional[str] = None) -> Dict[str, Any]:
        """
        Encrypt message with current session key.
        
        Args:
            plaintext: Message to encrypt
            additional_data: Additional authenticated data
            
        Returns:
            Encrypted message data
        """
        try:
            if not self.shared_secret:
                raise ValueError("Session not established")
            
            # Check if key rotation is needed
            if self.should_rotate_keys():
                rotation_info = self.rotate_keys()
            else:
                rotation_info = None
            
            # Generate message-specific nonce
            nonce = secrets.token_bytes(12)
            
            # Create cipher with shared secret
            cipher = Cipher(
                algorithms.AES(self.shared_secret),
                modes.GCM(nonce),
                backend=default_backend()
            )
            encryptor = cipher.encryptor()
            
            # Add authenticated data
            auth_data = f"session:{self.session_id}:counter:{self.message_counter}"
            if additional_data:
                auth_data += f":additional:{additional_data}"
            
            encryptor.authenticate_additional_data(auth_data.encode('utf-8'))
            
            # Encrypt message
            ciphertext = encryptor.update(plaintext.encode('utf-8')) + encryptor.finalize()
            
            # Increment counter
            self.message_counter += 1
            
            result = {
                'session_id': self.session_id,
                'ciphertext': base64.b64encode(ciphertext).decode('utf-8'),
                'nonce': base64.b64encode(nonce).decode('utf-8'),
                'tag': base64.b64encode(encryptor.tag).decode('utf-8'),
                'counter': self.message_counter - 1,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            if rotation_info:
                result['key_rotation'] = rotation_info
            
            return result
            
        except Exception as e:
            logger.error(f"Message encryption failed: {str(e)}")
            raise
    
    def decrypt_message(self, encrypted_data: Dict[str, Any]) -> str:
        """
        Decrypt message with current session key.
        
        Args:
            encrypted_data: Encrypted message data
            
        Returns:
            Decrypted plaintext message
        """
        try:
            if not self.shared_secret:
                raise ValueError("Session not established")
            
            # Extract encrypted components
            ciphertext = base64.b64decode(encrypted_data['ciphertext'])
            nonce = base64.b64decode(encrypted_data['nonce'])
            tag = base64.b64decode(encrypted_data['tag'])
            counter = encrypted_data['counter']
            
            # Create cipher
            cipher = Cipher(
                algorithms.AES(self.shared_secret),
                modes.GCM(nonce, tag),
                backend=default_backend()
            )
            decryptor = cipher.decryptor()
            
            # Authenticate additional data
            auth_data = f"session:{self.session_id}:counter:{counter}"
            decryptor.authenticate_additional_data(auth_data.encode('utf-8'))
            
            # Decrypt message
            plaintext = decryptor.update(ciphertext) + decryptor.finalize()
            
            return plaintext.decode('utf-8')
            
        except Exception as e:
            logger.error(f"Message decryption failed: {str(e)}")
            raise


class E2EManager:
    """
    Manager for multiple end-to-end encryption sessions.
    """
    
    def __init__(self):
        self.sessions: Dict[str, E2ESession] = {}
        self.session_timeout = timedelta(hours=24)
    
    def create_session(self) -> Dict[str, Any]:
        """
        Create new E2E encryption session.
        
        Returns:
            Session creation response with public key
        """
        try:
            session = E2ESession()
            self.sessions[session.session_id] = session
            
            return {
                'session_id': session.session_id,
                'public_key': session.key_exchange.get_public_key_b64(),
                'created_at': session.created_at.isoformat(),
                'expires_at': (session.created_at + self.session_timeout).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Session creation failed: {str(e)}")
            raise
    
    def establish_session(self, session_id: str, peer_public_key_b64: str) -> Dict[str, Any]:
        """
        Establish E2E session with peer's public key.
        
        Args:
            session_id: Session identifier
            peer_public_key_b64: Peer's public key
            
        Returns:
            Session establishment response
        """
        try:
            if session_id not in self.sessions:
                raise ValueError(f"Session {session_id} not found")
            
            session = self.sessions[session_id]
            return session.establish_session(peer_public_key_b64)
            
        except Exception as e:
            logger.error(f"Session establishment failed: {str(e)}")
            raise
    
    def encrypt_message(self, session_id: str, plaintext: str, 
                       additional_data: Optional[str] = None) -> Dict[str, Any]:
        """
        Encrypt message for specific session.
        
        Args:
            session_id: Session identifier
            plaintext: Message to encrypt
            additional_data: Additional authenticated data
            
        Returns:
            Encrypted message data
        """
        try:
            if session_id not in self.sessions:
                raise ValueError(f"Session {session_id} not found")
            
            session = self.sessions[session_id]
            return session.encrypt_message(plaintext, additional_data)
            
        except Exception as e:
            logger.error(f"Message encryption failed: {str(e)}")
            raise
    
    def decrypt_message(self, session_id: str, encrypted_data: Dict[str, Any]) -> str:
        """
        Decrypt message for specific session.
        
        Args:
            session_id: Session identifier
            encrypted_data: Encrypted message data
            
        Returns:
            Decrypted plaintext message
        """
        try:
            if session_id not in self.sessions:
                raise ValueError(f"Session {session_id} not found")
            
            session = self.sessions[session_id]
            return session.decrypt_message(encrypted_data)
            
        except Exception as e:
            logger.error(f"Message decryption failed: {str(e)}")
            raise
    
    def cleanup_expired_sessions(self):
        """Remove expired sessions."""
        try:
            current_time = datetime.utcnow()
            expired_sessions = []
            
            for session_id, session in self.sessions.items():
                if current_time - session.created_at > self.session_timeout:
                    expired_sessions.append(session_id)
            
            for session_id in expired_sessions:
                del self.sessions[session_id]
                logger.info(f"Removed expired session {session_id}")
            
            return len(expired_sessions)
            
        except Exception as e:
            logger.error(f"Session cleanup failed: {str(e)}")
            return 0
    
    def get_session_info(self, session_id: str) -> Dict[str, Any]:
        """
        Get session information.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Session information
        """
        try:
            if session_id not in self.sessions:
                raise ValueError(f"Session {session_id} not found")
            
            session = self.sessions[session_id]
            
            return {
                'session_id': session.session_id,
                'created_at': session.created_at.isoformat(),
                'last_key_rotation': session.last_key_rotation.isoformat(),
                'message_counter': session.message_counter,
                'has_shared_secret': session.shared_secret is not None,
                'should_rotate_keys': session.should_rotate_keys()
            }
            
        except Exception as e:
            logger.error(f"Get session info failed: {str(e)}")
            raise


class WebSocketE2E:
    """
    End-to-end encryption for WebSocket connections.
    """
    
    def __init__(self, e2e_manager: E2EManager):
        self.e2e_manager = e2e_manager
        self.websocket_sessions: Dict[str, str] = {}  # websocket_id -> session_id
    
    async def handle_websocket_connection(self, websocket_id: str) -> Dict[str, Any]:
        """
        Handle new WebSocket connection with E2E encryption.
        
        Args:
            websocket_id: WebSocket connection identifier
            
        Returns:
            Connection establishment response
        """
        try:
            # Create new E2E session for WebSocket
            session_info = self.e2e_manager.create_session()
            session_id = session_info['session_id']
            
            # Associate WebSocket with session
            self.websocket_sessions[websocket_id] = session_id
            
            return {
                'websocket_id': websocket_id,
                'session_id': session_id,
                'public_key': session_info['public_key'],
                'handshake_required': True
            }
            
        except Exception as e:
            logger.error(f"WebSocket E2E setup failed: {str(e)}")
            raise
    
    async def complete_handshake(self, websocket_id: str, 
                                peer_public_key_b64: str) -> Dict[str, Any]:
        """
        Complete E2E handshake for WebSocket.
        
        Args:
            websocket_id: WebSocket connection identifier
            peer_public_key_b64: Client's public key
            
        Returns:
            Handshake completion response
        """
        try:
            if websocket_id not in self.websocket_sessions:
                raise ValueError(f"WebSocket {websocket_id} not found")
            
            session_id = self.websocket_sessions[websocket_id]
            return self.e2e_manager.establish_session(session_id, peer_public_key_b64)
            
        except Exception as e:
            logger.error(f"WebSocket handshake failed: {str(e)}")
            raise
    
    async def encrypt_websocket_message(self, websocket_id: str, 
                                       message: str) -> Dict[str, Any]:
        """
        Encrypt message for WebSocket transmission.
        
        Args:
            websocket_id: WebSocket connection identifier
            message: Message to encrypt
            
        Returns:
            Encrypted message data
        """
        try:
            if websocket_id not in self.websocket_sessions:
                raise ValueError(f"WebSocket {websocket_id} not found")
            
            session_id = self.websocket_sessions[websocket_id]
            return self.e2e_manager.encrypt_message(session_id, message, f"websocket:{websocket_id}")
            
        except Exception as e:
            logger.error(f"WebSocket message encryption failed: {str(e)}")
            raise
    
    async def decrypt_websocket_message(self, websocket_id: str, 
                                       encrypted_data: Dict[str, Any]) -> str:
        """
        Decrypt message from WebSocket.
        
        Args:
            websocket_id: WebSocket connection identifier
            encrypted_data: Encrypted message data
            
        Returns:
            Decrypted message
        """
        try:
            if websocket_id not in self.websocket_sessions:
                raise ValueError(f"WebSocket {websocket_id} not found")
            
            session_id = self.websocket_sessions[websocket_id]
            return self.e2e_manager.decrypt_message(session_id, encrypted_data)
            
        except Exception as e:
            logger.error(f"WebSocket message decryption failed: {str(e)}")
            raise
    
    def cleanup_websocket(self, websocket_id: str):
        """Clean up WebSocket E2E session."""
        if websocket_id in self.websocket_sessions:
            del self.websocket_sessions[websocket_id]
            logger.info(f"Cleaned up WebSocket E2E session for {websocket_id}")


# Global instances
e2e_manager = E2EManager()
websocket_e2e = WebSocketE2E(e2e_manager)


def get_e2e_manager() -> E2EManager:
    """Get E2E encryption manager instance."""
    return e2e_manager


def get_websocket_e2e() -> WebSocketE2E:
    """Get WebSocket E2E encryption instance."""
    return websocket_e2e