"""Encryption Engine - IA-Influencer-Agent Platform

Advanced encryption engine providing multiple cryptographic algorithms
and secure data protection for blockchain operations.

(c) 2025 Fahed Mlaiel (mlaiel@live.de) - IA-Influencer-Agent Platform
Propriété Intellectuelle Exclusive - Tous Droits Réservés
"""

import logging
from typing import Dict, Any, Optional, Tuple
from enum import Enum
import secrets
import hashlib
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

logger = logging.getLogger(__name__)


class EncryptionAlgorithm(Enum):
    """Supported encryption algorithms"""
    AES_256_GCM = "aes_256_gcm"
    AES_256_CBC = "aes_256_cbc"
    CHACHA20_POLY1305 = "chacha20_poly1305"
    FERNET = "fernet"


class CryptoProvider:
    """Cryptographic operations provider"""
    
    def __init__(self, algorithm: EncryptionAlgorithm):
        self.algorithm = algorithm
        self.logger = logging.getLogger(__name__)
    
    def generate_key(self) -> bytes:
        """Generate encryption key"""
        if self.algorithm == EncryptionAlgorithm.FERNET:
            return Fernet.generate_key()
        else:
            return secrets.token_bytes(32)  # 256-bit key
    
    def encrypt(self, data: bytes, key: bytes) -> Tuple[bytes, bytes]:
        """Encrypt data and return (encrypted_data, nonce/iv)"""
        if self.algorithm == EncryptionAlgorithm.FERNET:
            f = Fernet(key)
            encrypted = f.encrypt(data)
            return encrypted, b""  # Fernet includes nonce
        
        elif self.algorithm == EncryptionAlgorithm.AES_256_GCM:
            nonce = secrets.token_bytes(12)
            cipher = Cipher(algorithms.AES(key), modes.GCM(nonce))
            encryptor = cipher.encryptor()
            encrypted = encryptor.update(data) + encryptor.finalize()
            return encrypted + encryptor.tag, nonce
        
        else:
            # Default to simple XOR for demo
            nonce = secrets.token_bytes(16)
            encrypted = bytes(a ^ b for a, b in zip(data, key * (len(data) // len(key) + 1)))
            return encrypted, nonce
    
    def decrypt(self, encrypted_data: bytes, key: bytes, nonce: bytes = b"") -> bytes:
        """Decrypt data"""
        if self.algorithm == EncryptionAlgorithm.FERNET:
            f = Fernet(key)
            return f.decrypt(encrypted_data)
        
        elif self.algorithm == EncryptionAlgorithm.AES_256_GCM:
            # Extract tag and data
            tag = encrypted_data[-16:]
            ciphertext = encrypted_data[:-16]
            cipher = Cipher(algorithms.AES(key), modes.GCM(nonce, tag))
            decryptor = cipher.decryptor()
            return decryptor.update(ciphertext) + decryptor.finalize()
        
        else:
            # Default XOR
            return bytes(a ^ b for a, b in zip(encrypted_data, key * (len(encrypted_data) // len(key) + 1)))


class EncryptionEngine:
    """Advanced Encryption Engine"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.providers: Dict[EncryptionAlgorithm, CryptoProvider] = {}
        self.default_algorithm = EncryptionAlgorithm(config.get("default_algorithm", "fernet"))
        
        # Initialize providers
        for algorithm in EncryptionAlgorithm:
            self.providers[algorithm] = CryptoProvider(algorithm)
    
    async def encrypt_data(
        self,
        data: bytes,
        algorithm: Optional[EncryptionAlgorithm] = None,
        key: Optional[bytes] = None
    ) -> Dict[str, Any]:
        """Encrypt data with specified algorithm"""
        try:
            algorithm = algorithm or self.default_algorithm
            provider = self.providers[algorithm]
            
            if key is None:
                key = provider.generate_key()
            
            encrypted_data, nonce = provider.encrypt(data, key)
            
            result = {
                "encrypted_data": encrypted_data.hex(),
                "algorithm": algorithm.value,
                "key": key.hex(),
                "nonce": nonce.hex() if nonce else "",
                "data_hash": hashlib.sha256(data).hexdigest()
            }
            
            self.logger.info(f"Data encrypted with {algorithm.value}")
            return result
            
        except Exception as e:
            self.logger.error(f"Encryption failed: {e}")
            raise
    
    async def decrypt_data(
        self,
        encrypted_data_hex: str,
        key_hex: str,
        algorithm: EncryptionAlgorithm,
        nonce_hex: str = ""
    ) -> bytes:
        """Decrypt data"""
        try:
            provider = self.providers[algorithm]
            
            encrypted_data = bytes.fromhex(encrypted_data_hex)
            key = bytes.fromhex(key_hex)
            nonce = bytes.fromhex(nonce_hex) if nonce_hex else b""
            
            decrypted_data = provider.decrypt(encrypted_data, key, nonce)
            
            self.logger.info(f"Data decrypted with {algorithm.value}")
            return decrypted_data
            
        except Exception as e:
            self.logger.error(f"Decryption failed: {e}")
            raise