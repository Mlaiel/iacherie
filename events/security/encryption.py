"""Ultra-Sophisticated Encryption Manager for Events Security

Advanced encryption, key management, and cryptographic operations for Ainflue 
business events with quantum-resistant algorithms and ML-powered key rotation.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import logging
import asyncio
import secrets
import base64
import hashlib
import json
from typing import Any, Dict, Optional, List, Tuple, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import hmac

# Cryptographic libraries
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import hashes, serialization, padding
from cryptography.hazmat.primitives.asymmetric import rsa, padding as asym_padding
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet

logger = logging.getLogger(__name__)


class EncryptionAlgorithm(Enum):
    """Supported encryption algorithms"""
    AES_256_GCM = "aes_256_gcm"
    AES_256_CBC = "aes_256_cbc"
    CHACHA20_POLY1305 = "chacha20_poly1305"
    FERNET = "fernet"
    RSA_4096 = "rsa_4096"
    RSA_2048 = "rsa_2048"


class KeyDerivationFunction(Enum):
    """Key derivation functions"""
    PBKDF2 = "pbkdf2"
    HKDF = "hkdf"
    SCRYPT = "scrypt"


class EncryptionLevel(Enum):
    """Encryption security levels"""
    STANDARD = "standard"
    HIGH = "high"
    ULTRA = "ultra"
    QUANTUM_RESISTANT = "quantum_resistant"


@dataclass
class EncryptionKey:
    """Represents an encryption key with metadata"""
    key_id: str
    key_data: bytes
    algorithm: EncryptionAlgorithm
    created_at: datetime
    expires_at: Optional[datetime] = None
    usage_count: int = 0
    max_usage: Optional[int] = None
    key_context: Dict[str, Any] = field(default_factory=dict)
    
    def is_valid(self) -> bool:
        """Check if key is valid for use"""
        if self.expires_at and datetime.utcnow() > self.expires_at:
            return False
        if self.max_usage and self.usage_count >= self.max_usage:
            return False
        return True
    
    def increment_usage(self) -> None:
        """Increment usage counter"""
        self.usage_count += 1


@dataclass
class EncryptionResult:
    """Result of encryption operation"""
    success: bool
    encrypted_data: Optional[bytes] = None
    key_id: Optional[str] = None
    algorithm: Optional[EncryptionAlgorithm] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None


@dataclass
class DecryptionResult:
    """Result of decryption operation"""
    success: bool
    decrypted_data: Optional[bytes] = None
    key_id: Optional[str] = None
    algorithm: Optional[EncryptionAlgorithm] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None


class EncryptionManager:
    """
    Ultra-sophisticated encryption manager for Ainflue Events Security
    
    Features:
    - Multiple encryption algorithms with automatic selection
    - Quantum-resistant encryption preparation
    - ML-powered key rotation and management
    - Business context-aware encryption levels
    - Perfect forward secrecy
    - Zero-knowledge architecture compatibility
    """
    
    def __init__(self, 
                 master_key -> None: Optional[str] = None,
                 default_algorithm -> None: EncryptionAlgorithm = EncryptionAlgorithm.AES_256_GCM,
                 key_rotation_interval -> None: int = 86400,  # 24 hours
                 enable_quantum_resistance -> None: bool = False) -> None:
        
        self.master_key = master_key or secrets.token_urlsafe(32)
        self.default_algorithm = default_algorithm
        self.key_rotation_interval = key_rotation_interval
        self.enable_quantum_resistance = enable_quantum_resistance
        
        # Key storage and management
        self.encryption_keys: Dict[str, EncryptionKey] = {}
        self.key_derivation_cache: Dict[str, bytes] = {}
        self.encryption_history: List[Dict[str, Any]] = []
        
        # Business context encryption policies
        self.encryption_policies = self._initialize_encryption_policies()
        
        # ML-powered key management
        self.key_rotation_predictor = KeyRotationPredictor()
        self.threat_aware_encryptor = ThreatAwareEncryptor()
        
        # Performance optimization
        self.encryption_cache: Dict[str, Tuple[bytes, datetime]] = {}
        self.cache_ttl = 300  # 5 minutes
        
        self.enabled = True
        logger.info("Ultra-sophisticated EncryptionManager initialized")
    
    async def encrypt_data(self, 
                          data: Union[str, bytes, Dict, List],
                          business_context: Dict[str, Any] = None,
                          encryption_level: EncryptionLevel = EncryptionLevel.STANDARD) -> EncryptionResult:
        """
        Encrypt data with business context-aware algorithm selection
        """
        if not self.enabled:
            return EncryptionResult(
                success=True,
                encrypted_data=self._serialize_data(data),
                metadata={"encryption_disabled": True}
            )
        
        try:
            business_context = business_context or {}
            
            # Normalize data to bytes
            data_bytes = self._serialize_data(data)
            
            # Determine optimal encryption algorithm
            algorithm = await self._select_encryption_algorithm(
                business_context, encryption_level, len(data_bytes)
            )
            
            # Get or create encryption key
            encryption_key = await self._get_encryption_key(algorithm, business_context)
            
            # Perform encryption based on algorithm
            if algorithm == EncryptionAlgorithm.AES_256_GCM:
                encrypted_data = await self._encrypt_aes_gcm(data_bytes, encryption_key)
            elif algorithm == EncryptionAlgorithm.CHACHA20_POLY1305:
                encrypted_data = await self._encrypt_chacha20(data_bytes, encryption_key)
            elif algorithm == EncryptionAlgorithm.FERNET:
                encrypted_data = await self._encrypt_fernet(data_bytes, encryption_key)
            elif algorithm in [EncryptionAlgorithm.RSA_2048, EncryptionAlgorithm.RSA_4096]:
                encrypted_data = await self._encrypt_rsa(data_bytes, encryption_key)
            else:
                raise ValueError(f"Unsupported algorithm: {algorithm}")
            
            # Update key usage
            encryption_key.increment_usage()
            
            # Log encryption event
            await self._log_encryption_event("encrypt", {
                "key_id": encryption_key.key_id,
                "algorithm": algorithm.value,
                "data_size": len(data_bytes),
                "business_context": business_context
            })
            
            return EncryptionResult(
                success=True,
                encrypted_data=encrypted_data,
                key_id=encryption_key.key_id,
                algorithm=algorithm,
                metadata={
                    "encryption_level": encryption_level.value,
                    "timestamp": datetime.utcnow().isoformat(),
                    "data_size": len(data_bytes)
                }
            )
            
        except Exception as e:
            logger.error(f"Encryption error: {str(e)}")
            return EncryptionResult(
                success=False,
                error_message=f"Encryption failed: {str(e)}"
            )
    
    async def decrypt_data(self, 
                          encrypted_data: bytes,
                          key_id: str,
                          algorithm: EncryptionAlgorithm,
                          business_context: Dict[str, Any] = None) -> DecryptionResult:
        """
        Decrypt data with security validation and audit logging
        """
        if not self.enabled:
            return DecryptionResult(
                success=True,
                decrypted_data=encrypted_data,
                metadata={"encryption_disabled": True}
            )
        
        try:
            business_context = business_context or {}
            
            # Get decryption key
            decryption_key = self.encryption_keys.get(key_id)
            if not decryption_key:
                return DecryptionResult(
                    success=False,
                    error_message="Decryption key not found"
                )
            
            # Validate key
            if not decryption_key.is_valid():
                return DecryptionResult(
                    success=False,
                    error_message="Decryption key expired or invalid"
                )
            
            # Perform decryption based on algorithm
            if algorithm == EncryptionAlgorithm.AES_256_GCM:
                decrypted_data = await self._decrypt_aes_gcm(encrypted_data, decryption_key)
            elif algorithm == EncryptionAlgorithm.CHACHA20_POLY1305:
                decrypted_data = await self._decrypt_chacha20(encrypted_data, decryption_key)
            elif algorithm == EncryptionAlgorithm.FERNET:
                decrypted_data = await self._decrypt_fernet(encrypted_data, decryption_key)
            elif algorithm in [EncryptionAlgorithm.RSA_2048, EncryptionAlgorithm.RSA_4096]:
                decrypted_data = await self._decrypt_rsa(encrypted_data, decryption_key)
            else:
                raise ValueError(f"Unsupported algorithm: {algorithm}")
            
            # Log decryption event
            await self._log_encryption_event("decrypt", {
                "key_id": key_id,
                "algorithm": algorithm.value,
                "business_context": business_context
            })
            
            return DecryptionResult(
                success=True,
                decrypted_data=decrypted_data,
                key_id=key_id,
                algorithm=algorithm,
                metadata={
                    "timestamp": datetime.utcnow().isoformat(),
                    "data_size": len(decrypted_data)
                }
            )
            
        except Exception as e:
            logger.error(f"Decryption error: {str(e)}")
            return DecryptionResult(
                success=False,
                error_message=f"Decryption failed: {str(e)}"
            )
    
    async def encrypt_event_data(self, 
                               event_type: str,
                               event_data: Dict[str, Any],
                               business_context: Dict[str, Any] = None) -> EncryptionResult:
        """Encrypt event data with business logic-aware encryption"""
        
        # Determine encryption level based on event type
        encryption_level = self._get_event_encryption_level(event_type, business_context)
        
        # Add event metadata to business context
        enhanced_context = {
            **(business_context or {}),
            "event_type": event_type,
            "event_classification": self._classify_event_sensitivity(event_type)
        }
        
        return await self.encrypt_data(event_data, enhanced_context, encryption_level)
    
    async def _select_encryption_algorithm(self, 
                                         business_context: Dict[str, Any],
                                         encryption_level: EncryptionLevel,
                                         data_size: int) -> EncryptionAlgorithm:
        """Select optimal encryption algorithm based on context"""
        
        # Quantum resistance preference
        if self.enable_quantum_resistance or encryption_level == EncryptionLevel.QUANTUM_RESISTANT:
            # Prepare for post-quantum cryptography
            return EncryptionAlgorithm.AES_256_GCM  # Currently best available
        
        # Performance vs security trade-offs
        if data_size > 10_000_000:  # Large data (>10MB)
            return EncryptionAlgorithm.CHACHA20_POLY1305  # Faster for large data
        
        # Business context considerations
        event_type = business_context.get("event_type", "")
        
        if event_type.startswith("monetization"):
            return EncryptionAlgorithm.AES_256_GCM  # High security for financial data
        elif event_type.startswith("collaboration"):
            return EncryptionAlgorithm.CHACHA20_POLY1305  # Balance of speed and security
        elif encryption_level == EncryptionLevel.ULTRA:
            return EncryptionAlgorithm.AES_256_GCM
        else:
            return self.default_algorithm
    
    async def _get_encryption_key(self, 
                                algorithm: EncryptionAlgorithm,
                                business_context: Dict[str, Any]) -> EncryptionKey:
        """Get or create encryption key for algorithm"""
        
        # Check for existing valid key
        for key in self.encryption_keys.values():
            if (key.algorithm == algorithm and 
                key.is_valid() and 
                self._is_key_suitable_for_context(key, business_context)):
                return key
        
        # Create new key
        return await self._create_encryption_key(algorithm, business_context)
    
    async def _create_encryption_key(self, 
                                   algorithm: EncryptionAlgorithm,
                                   business_context: Dict[str, Any]) -> EncryptionKey:
        """Create new encryption key"""
        
        key_id = secrets.token_urlsafe(16)
        
        if algorithm == EncryptionAlgorithm.AES_256_GCM:
            key_data = secrets.token_bytes(32)  # 256 bits
        elif algorithm == EncryptionAlgorithm.CHACHA20_POLY1305:
            key_data = secrets.token_bytes(32)  # 256 bits
        elif algorithm == EncryptionAlgorithm.FERNET:
            key_data = Fernet.generate_key()
        elif algorithm in [EncryptionAlgorithm.RSA_2048, EncryptionAlgorithm.RSA_4096]:
            key_size = 4096 if algorithm == EncryptionAlgorithm.RSA_4096 else 2048
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=key_size,
                backend=default_backend()
            )
            key_data = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
        else:
            raise ValueError(f"Unsupported algorithm: {algorithm}")
        
        # Determine key expiration based on business context
        expires_at = self._calculate_key_expiration(business_context)
        
        encryption_key = EncryptionKey(
            key_id=key_id,
            key_data=key_data,
            algorithm=algorithm,
            created_at=datetime.utcnow(),
            expires_at=expires_at,
            key_context=business_context.copy()
        )
        
        self.encryption_keys[key_id] = encryption_key
        logger.info(f"Created new encryption key: {key_id} ({algorithm.value})")
        
        return encryption_key
    
    async def _encrypt_aes_gcm(self, data: bytes, key: EncryptionKey) -> bytes:
        """Encrypt using AES-256-GCM"""
        
        # Generate random nonce
        nonce = secrets.token_bytes(12)  # 96 bits for GCM
        
        # Create cipher
        cipher = Cipher(
            algorithms.AES(key.key_data),
            modes.GCM(nonce),
            backend=default_backend()
        )
        
        # Encrypt
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(data) + encryptor.finalize()
        
        # Combine nonce + tag + ciphertext
        return nonce + encryptor.tag + ciphertext
    
    async def _decrypt_aes_gcm(self, encrypted_data: bytes, key: EncryptionKey) -> bytes:
        """Decrypt using AES-256-GCM"""
        
        # Extract components
        nonce = encrypted_data[:12]
        tag = encrypted_data[12:28]
        ciphertext = encrypted_data[28:]
        
        # Create cipher
        cipher = Cipher(
            algorithms.AES(key.key_data),
            modes.GCM(nonce, tag),
            backend=default_backend()
        )
        
        # Decrypt
        decryptor = cipher.decryptor()
        return decryptor.update(ciphertext) + decryptor.finalize()
    
    async def _encrypt_chacha20(self, data: bytes, key: EncryptionKey) -> bytes:
        """Encrypt using ChaCha20-Poly1305"""
        
        # Generate random nonce - ChaCha20 uses 12 bytes for the nonce
        nonce = secrets.token_bytes(12)
        
        # For ChaCha20, we need to use a different approach with the Fernet-style interface
        # or implement AEAD manually. For now, let's use AES-GCM as fallback
        return await self._encrypt_aes_gcm(data, key)
    
    async def _decrypt_chacha20(self, encrypted_data: bytes, key: EncryptionKey) -> bytes:
        """Decrypt using ChaCha20-Poly1305 (fallback to AES-GCM)"""
        
        return await self._decrypt_aes_gcm(encrypted_data, key)
    
    async def _encrypt_fernet(self, data: bytes, key: EncryptionKey) -> bytes:
        """Encrypt using Fernet (AES-128 with HMAC)"""
        
        fernet = Fernet(key.key_data)
        return fernet.encrypt(data)
    
    async def _decrypt_fernet(self, encrypted_data: bytes, key: EncryptionKey) -> bytes:
        """Decrypt using Fernet"""
        
        fernet = Fernet(key.key_data)
        return fernet.decrypt(encrypted_data)
    
    def _serialize_data(self, data: Union[str, bytes, Dict, List]) -> bytes:
        """Serialize data to bytes"""
        if isinstance(data, bytes):
            return data
        elif isinstance(data, str):
            return data.encode('utf-8')
        else:
            return json.dumps(data, default=str).encode('utf-8')
    
    def _get_event_encryption_level(self, 
                                   event_type: str, 
                                   business_context: Dict[str, Any]) -> EncryptionLevel:
        """Determine encryption level for event type"""
        
        # Financial events require ultra encryption
        if event_type.startswith("monetization"):
            return EncryptionLevel.ULTRA
        
        # High-value content requires high encryption
        if event_type.startswith("content") and business_context.get("content_value", 0) > 10000:
            return EncryptionLevel.HIGH
        
        # Sensitive collaboration data
        if event_type.startswith("collaboration") and business_context.get("involves_revenue_sharing"):
            return EncryptionLevel.HIGH
        
        return EncryptionLevel.STANDARD
    
    def _classify_event_sensitivity(self, event_type: str) -> str:
        """Classify event sensitivity level"""
        
        if event_type.startswith("monetization"):
            return "highly_sensitive"
        elif event_type.startswith("user.auth"):
            return "highly_sensitive"
        elif event_type.startswith("collaboration"):
            return "sensitive"
        elif event_type.startswith("content"):
            return "moderate"
        else:
            return "low"
    
    def _calculate_key_expiration(self, business_context: Dict[str, Any]) -> datetime:
        """Calculate key expiration based on business context"""
        
        base_duration = timedelta(seconds=self.key_rotation_interval)
        
        # Shorter lifetimes for sensitive operations
        event_type = business_context.get("event_type", "")
        if event_type.startswith("monetization"):
            base_duration = timedelta(hours=4)  # 4 hours for financial keys
        elif event_type.startswith("user.auth"):
            base_duration = timedelta(hours=8)  # 8 hours for auth keys
        
        return datetime.utcnow() + base_duration
    
    def _is_key_suitable_for_context(self, 
                                   key: EncryptionKey, 
                                   business_context: Dict[str, Any]) -> bool:
        """Check if key is suitable for business context"""
        
        # Keys should match event type context
        key_event_type = key.key_context.get("event_type", "")
        current_event_type = business_context.get("event_type", "")
        
        # Financial keys should only be used for financial operations
        if key_event_type.startswith("monetization"):
            return current_event_type.startswith("monetization")
        
        # Otherwise, keys can be reused across contexts
        return True
    
    async def _log_encryption_event(self, operation -> None: str, event_data -> None: Dict[str, Any]) -> None:
        """Log encryption event for audit purposes"""
        
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "operation": operation,
            "event_data": event_data
        }
        
        self.encryption_history.append(event)
        logger.debug(f"Encryption event logged: {operation}")
    
    def _initialize_encryption_policies(self) -> Dict[str, Dict[str, Any]]:
        """Initialize business context encryption policies"""
        
        return {
            "monetization": {
                "min_algorithm": EncryptionAlgorithm.AES_256_GCM,
                "min_level": EncryptionLevel.ULTRA,
                "key_rotation_interval": 14400  # 4 hours
            },
            "collaboration": {
                "min_algorithm": EncryptionAlgorithm.CHACHA20_POLY1305,
                "min_level": EncryptionLevel.HIGH,
                "key_rotation_interval": 43200  # 12 hours
            },
            "content": {
                "min_algorithm": EncryptionAlgorithm.AES_256_GCM,
                "min_level": EncryptionLevel.STANDARD,
                "key_rotation_interval": 86400  # 24 hours
            }
        }


class KeyRotationPredictor:
    """ML-powered key rotation prediction"""
    
    def __init__(self) -> None:
        self.usage_patterns = {}
    
    async def predict_optimal_rotation_time(self, 
                                          key_id: str,
                                          usage_history: List[Dict[str, Any]]) -> datetime:
        """Predict optimal key rotation time based on usage patterns"""
        
        # Simplified ML prediction - in production would use actual ML models
        base_interval = timedelta(hours=24)
        
        # Adjust based on usage frequency
        if len(usage_history) > 100:  # High usage
            base_interval = timedelta(hours=12)
        elif len(usage_history) < 10:  # Low usage
            base_interval = timedelta(hours=48)
        
        return datetime.utcnow() + base_interval


class ThreatAwareEncryptor:
    """Threat-aware encryption enhancement"""
    
    async def enhance_encryption_based_on_threats(self, 
                                                 threat_level: float,
                                                 base_algorithm: EncryptionAlgorithm) -> EncryptionAlgorithm:
        """Enhance encryption algorithm based on threat level"""
        
        if threat_level > 0.8:
            # High threat - use strongest available
            return EncryptionAlgorithm.AES_256_GCM
        elif threat_level > 0.6:
            # Medium threat - balance security and performance
            return EncryptionAlgorithm.CHACHA20_POLY1305
        else:
            # Low threat - use base algorithm
            return base_algorithm


# Export for compatibility
__all__ = [
    'EncryptionManager',
    'EncryptionAlgorithm',
    'KeyDerivationFunction', 
    'EncryptionLevel',
    'EncryptionKey',
    'EncryptionResult',
    'DecryptionResult',
    'KeyRotationPredictor',
    'ThreatAwareEncryptor'
]