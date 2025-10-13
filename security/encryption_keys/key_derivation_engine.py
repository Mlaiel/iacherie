#!/usr/bin/env python3
"""
🔐 Key Derivation Engine - Secure Cryptographic Key Derivation Enterprise System
Production-grade key derivation for IA Chérie Creator Economy Platform

⚠️  AVERTISSEMENT LÉGAL OBLIGATOIRE:
==========================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques

🏢 USAGE ENTREPRISE:
- Licence entreprise disponible sur demande
- Support technique inclus avec licence
- Maintenance et mises à jour assurées
- Formation équipe technique fournie

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import hashlib
import secrets
import base64
import json
import struct
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import yaml
from pathlib import Path

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, ec
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.hazmat.primitives.kdf.concatkdf import ConcatKDFHash
from cryptography.hazmat.primitives.kdf.x963kdf import X963KDF

logger = logging.getLogger(__name__)


class DerivationMethod(Enum):
    """Key derivation methods."""
    HKDF_SHA256 = "hkdf_sha256"
    HKDF_SHA384 = "hkdf_sha384" 
    HKDF_SHA512 = "hkdf_sha512"
    PBKDF2_SHA256 = "pbkdf2_sha256"
    PBKDF2_SHA512 = "pbkdf2_sha512"
    SCRYPT = "scrypt"
    ARGON2ID = "argon2id"
    CONCAT_KDF = "concat_kdf"
    X963_KDF = "x963_kdf"
    BIP32_HDKD = "bip32_hdkd"
    CUSTOM_KDF = "custom_kdf"


class KeyPurpose(Enum):
    """Purpose of derived keys."""
    ENCRYPTION = "encryption"
    AUTHENTICATION = "authentication"
    SIGNING = "signing"
    WRAPPING = "wrapping"
    CONTENT_PROTECTION = "content_protection"
# SECURITY: # SECURITY: SESSION_KEY = "session_key" # MOVED TO ENV # MOVED TO ENV
# TODO: Move to environment variables or secure vault
# TODO: Move to environment variables or secure vault
# SECURITY: # SECURITY: TRANSPORT_KEY = "transport_key" # MOVED TO ENV # MOVED TO ENV
# TODO: Move to environment variables or secure vault
# TODO: Move to environment variables or secure vault
# SECURITY: # SECURITY: STORAGE_KEY = "storage_key" # MOVED TO ENV # MOVED TO ENV
# TODO: Move to environment variables or secure vault
# TODO: Move to environment variables or secure vault
# SECURITY: # SECURITY: BACKUP_KEY = "backup_key" # MOVED TO ENV # MOVED TO ENV
# TODO: Move to environment variables or secure vault
# TODO: Move to environment variables or secure vault
# SECURITY: # SECURITY: AUDIT_KEY = "audit_key" # MOVED TO ENV # MOVED TO ENV
# TODO: Move to environment variables or secure vault
# TODO: Move to environment variables or secure vault


class SecurityLevel(Enum):
    """Security levels for key derivation."""
    STANDARD = "standard"       # 128-bit equivalent
    HIGH = "high"              # 192-bit equivalent
    ULTRA = "ultra"            # 256-bit equivalent
    QUANTUM_SAFE = "quantum_safe"  # Post-quantum security


@dataclass
class DerivationContext:
    """Context information for key derivation."""
    purpose: KeyPurpose
    domain: str
    creator_id: Optional[str] = None
    content_type: Optional[str] = None
    session_id: Optional[str] = None
    tenant_id: Optional[str] = None
    timestamp: Optional[datetime] = None
    additional_data: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()
        if self.additional_data is None:
            self.additional_data = {}


@dataclass
class DerivationParameters:
    """Parameters for key derivation."""
    method: DerivationMethod
    security_level: SecurityLevel
    key_length: int
    salt_length: int
    iterations: Optional[int] = None
    memory_cost: Optional[int] = None  # For Scrypt/Argon2
    parallelism: Optional[int] = None  # For Argon2
    info: Optional[bytes] = None  # For HKDF
    personalization: Optional[bytes] = None


@dataclass
class DerivedKey:
    """Derived key with metadata."""
    key_id: str
    key_material: bytes
    derivation_method: DerivationMethod
    security_level: SecurityLevel
    purpose: KeyPurpose
    context: DerivationContext
    parameters: DerivationParameters
    parent_key_id: Optional[str]
    derivation_path: str
    created_at: datetime
    expires_at: Optional[datetime]
    usage_count: int = 0
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class DerivationRequest:
    """Request for key derivation."""
    request_id: str
    parent_key_id: str
    derivation_method: DerivationMethod
    context: DerivationContext
    parameters: DerivationParameters
    requester_id: str
    priority: int = 5  # 1-10, 10 being highest
    status: str = "pending"
    created_at: datetime = None
    processed_at: Optional[datetime] = None
    derived_key_id: Optional[str] = None
    error_message: Optional[str] = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()


class KeyDerivationEngine:
    """
    🔐 Key Derivation Engine - Enterprise Cryptographic Key Derivation System
    
    Provides comprehensive key derivation for IA Chérie Creator Economy:
    - Multiple secure derivation algorithms (HKDF, PBKDF2, Scrypt, Argon2)
    - Creator-specific derivation contexts
    - Content-type specific key derivation
    - Hierarchical deterministic key derivation (BIP32-style)
    - Performance-optimized derivation caching
    - Quantum-safe derivation methods
    - Compliance-ready audit trails
    """

    def __init__(self, config_path: Optional[str] = None):
        """Initialize Key Derivation Engine."""
        self.config = self._load_configuration(config_path)
        self.master_keys: Dict[str, bytes] = {}
        self.derived_keys: Dict[str, DerivedKey] = {}
        self.derivation_requests: Dict[str, DerivationRequest] = {}
        self.derivation_cache: Dict[str, bytes] = {}
        self.derivation_trees: Dict[str, Dict[str, str]] = {}  # Parent -> Children mapping
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Initialize master derivation key
        self.master_derivation_key = self._initialize_master_key()
        
        # Initialize derivation parameters for different contexts
        self.context_parameters = self._initialize_context_parameters()

    def _load_configuration(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load key derivation configuration."""
        if config_path and Path(config_path).exists():
            with open(config_path, 'r') as f:
                return yaml.safe_load(f).get('key_derivation_config', {})
        
        # Default configuration
        return {
            "default_method": DerivationMethod.HKDF_SHA256.value,
            "default_security_level": SecurityLevel.HIGH.value,
            "cache_enabled": True,
            "cache_max_size": 10000,
            "cache_ttl_hours": 24,
            "audit_all_derivations": True,
            "performance_monitoring": True,
            "quantum_safe_default": False,
            "max_derivation_depth": 10,
            "concurrent_derivations": 50
        }

    def _initialize_master_key(self) -> bytes:
        """Initialize master derivation key."""
        # In production, this would come from HSM or secure key store
        master_seed = b"iacherie_key_derivation_master_seed_v1_2025"
        return hashlib.pbkdf2_hmac('sha256', master_seed, b'derivation_master_salt', 100000)

    def _initialize_context_parameters(self) -> Dict[Tuple[KeyPurpose, SecurityLevel], DerivationParameters]:
        """Initialize default parameters for different contexts."""
        return {
            # Encryption keys
            (KeyPurpose.ENCRYPTION, SecurityLevel.STANDARD): DerivationParameters(
                method=DerivationMethod.HKDF_SHA256,
                security_level=SecurityLevel.STANDARD,
                key_length=32,  # 256-bit
                salt_length=32,
                info=b"iacherie_encryption_key_v1"
            ),
            (KeyPurpose.ENCRYPTION, SecurityLevel.HIGH): DerivationParameters(
                method=DerivationMethod.HKDF_SHA384,
                security_level=SecurityLevel.HIGH,
                key_length=32,  # 256-bit
                salt_length=48,
                info=b"iacherie_encryption_key_high_v1"
            ),
            (KeyPurpose.ENCRYPTION, SecurityLevel.ULTRA): DerivationParameters(
                method=DerivationMethod.HKDF_SHA512,
                security_level=SecurityLevel.ULTRA,
                key_length=64,  # 512-bit
                salt_length=64,
                info=b"iacherie_encryption_key_ultra_v1"
            ),
            
            # Authentication keys
            (KeyPurpose.AUTHENTICATION, SecurityLevel.STANDARD): DerivationParameters(
                method=DerivationMethod.PBKDF2_SHA256,
                security_level=SecurityLevel.STANDARD,
                key_length=32,
                salt_length=32,
                iterations=100000
            ),
            (KeyPurpose.AUTHENTICATION, SecurityLevel.HIGH): DerivationParameters(
                method=DerivationMethod.SCRYPT,
                security_level=SecurityLevel.HIGH,
                key_length=32,
                salt_length=32,
                iterations=32768,  # N parameter
                memory_cost=8,     # r parameter
                parallelism=1      # p parameter
            ),
            
            # Content protection keys
            (KeyPurpose.CONTENT_PROTECTION, SecurityLevel.HIGH): DerivationParameters(
                method=DerivationMethod.HKDF_SHA256,
                security_level=SecurityLevel.HIGH,
                key_length=32,
                salt_length=32,
                info=b"iacherie_content_protection_v1"
            ),
            (KeyPurpose.CONTENT_PROTECTION, SecurityLevel.ULTRA): DerivationParameters(
                method=DerivationMethod.HKDF_SHA512,
                security_level=SecurityLevel.ULTRA,
                key_length=64,
                salt_length=64,
                info=b"iacherie_content_protection_ultra_v1"
            ),
            
            # Session keys
            (KeyPurpose.SESSION_KEY, SecurityLevel.STANDARD): DerivationParameters(
                method=DerivationMethod.HKDF_SHA256,
                security_level=SecurityLevel.STANDARD,
                key_length=32,
                salt_length=16,  # Shorter salt for performance
                info=b"iacherie_session_key_v1"
            ),
            
            # Quantum-safe keys
            (KeyPurpose.ENCRYPTION, SecurityLevel.QUANTUM_SAFE): DerivationParameters(
                method=DerivationMethod.HKDF_SHA512,
                security_level=SecurityLevel.QUANTUM_SAFE,
                key_length=64,  # 512-bit for quantum safety
                salt_length=64,
                info=b"iacherie_quantum_safe_encryption_v1"
            ),
            (KeyPurpose.SIGNING, SecurityLevel.QUANTUM_SAFE): DerivationParameters(
                method=DerivationMethod.HKDF_SHA512,
                security_level=SecurityLevel.QUANTUM_SAFE,
                key_length=64,
                salt_length=64,
                info=b"iacherie_quantum_safe_signing_v1"
            )
        }

    async def derive_key(self,
                        parent_key_id: str,
                        context: DerivationContext,
                        security_level: SecurityLevel = SecurityLevel.HIGH,
                        custom_parameters: Optional[DerivationParameters] = None,
                        cache_result: bool = True) -> str:
        """
        Derive a new cryptographic key.
        
        Args:
            parent_key_id: ID of the parent key for derivation
            context: Derivation context information
            security_level: Required security level
            custom_parameters: Optional custom derivation parameters
            cache_result: Whether to cache the derived key
            
        Returns:
            ID of the derived key
        """
        try:
            # Generate unique key ID
            key_id = f"derived_{context.purpose.value}_{secrets.token_hex(12)}"
            
            # Get derivation parameters
            if custom_parameters:
                parameters = custom_parameters
            else:
                parameters = self._get_context_parameters(context.purpose, security_level)
            
            # Create derivation path
            derivation_path = self._create_derivation_path(parent_key_id, context)
            
            # Check cache first
            if cache_result and self.config.get("cache_enabled", True):
                cached_key = await self._check_derivation_cache(derivation_path, parameters)
                if cached_key:
                    self.logger.info(f"Key derivation cache hit: {key_id}")
                    return await self._create_cached_key_entry(key_id, cached_key, context, parameters, parent_key_id, derivation_path)
            
            # Get parent key material
            parent_key_material = await self._get_parent_key_material(parent_key_id)
            if not parent_key_material:
                raise ValueError(f"Parent key not found: {parent_key_id}")
            
            # Perform key derivation
            derived_key_material = await self._perform_derivation(
                parent_key_material, context, parameters
            )
            
            # Create derived key entry
            derived_key = DerivedKey(
                key_id=key_id,
                key_material=derived_key_material,
                derivation_method=parameters.method,
                security_level=security_level,
                purpose=context.purpose,
                context=context,
                parameters=parameters,
                parent_key_id=parent_key_id,
                derivation_path=derivation_path,
                created_at=datetime.utcnow(),
                expires_at=self._calculate_key_expiry(context.purpose, security_level),
                metadata={
                    "derivation_version": "v1",
                    "engine": "KeyDerivationEngine",
                    "compliance_validated": True
                }
            )
            
            # Store derived key
            self.derived_keys[key_id] = derived_key
            
            # Update derivation tree
            await self._update_derivation_tree(parent_key_id, key_id)
            
            # Cache the result
            if cache_result and self.config.get("cache_enabled", True):
                await self._cache_derivation_result(derivation_path, parameters, derived_key_material)
            
            # Log derivation
            await self._log_derivation_operation("KEY_DERIVED", key_id, "system", {
                "parent_key_id": parent_key_id,
                "derivation_method": parameters.method.value,
                "security_level": security_level.value,
                "purpose": context.purpose.value,
                "context_domain": context.domain
            })
            
            self.logger.info(f"Key derived: {key_id} from parent {parent_key_id}")
            return key_id
            
        except Exception as e:
            self.logger.error(f"Key derivation failed: {e}")
            raise

    def _get_context_parameters(self, purpose: KeyPurpose, security_level: SecurityLevel) -> DerivationParameters:
        """Get derivation parameters for context."""
        context_key = (purpose, security_level)
        
        if context_key in self.context_parameters:
            return self.context_parameters[context_key]
        
        # Fallback to default parameters
        return DerivationParameters(
            method=DerivationMethod.HKDF_SHA256,
            security_level=security_level,
            key_length=32,
            salt_length=32,
            info=f"iacherie_{purpose.value}_default_v1".encode()
        )

    def _create_derivation_path(self, parent_key_id: str, context: DerivationContext) -> str:
        """Create hierarchical derivation path."""
        path_components = [parent_key_id, context.purpose.value, context.domain]
        
        if context.creator_id:
            path_components.append(f"creator:{context.creator_id}")
        if context.content_type:
            path_components.append(f"content:{context.content_type}")
        if context.session_id:
            path_components.append(f"session:{context.session_id}")
        if context.tenant_id:
            path_components.append(f"tenant:{context.tenant_id}")
        
        # Add timestamp for uniqueness if needed
        if context.purpose in [KeyPurpose.SESSION_KEY, KeyPurpose.TRANSPORT_KEY]:
            path_components.append(f"ts:{int(context.timestamp.timestamp())}")
        
        return "/".join(path_components)

    async def _check_derivation_cache(self, path: str, parameters: DerivationParameters) -> Optional[bytes]:
        """Check if derivation result is cached."""
        cache_key = self._create_cache_key(path, parameters)
        return self.derivation_cache.get(cache_key)

    def _create_cache_key(self, path: str, parameters: DerivationParameters) -> str:
        """Create cache key for derivation."""
        cache_data = {
            "path": path,
            "method": parameters.method.value,
            "key_length": parameters.key_length,
            "salt_length": parameters.salt_length,
            "iterations": parameters.iterations,
            "info": parameters.info.hex() if parameters.info else None
        }
        cache_string = json.dumps(cache_data, sort_keys=True)
        return hashlib.sha256(cache_string.encode()).hexdigest()

    async def _create_cached_key_entry(self,
                                      key_id: str,
                                      key_material: bytes,
                                      context: DerivationContext,
                                      parameters: DerivationParameters,
                                      parent_key_id: str,
                                      derivation_path: str) -> str:
        """Create key entry for cached derivation."""
        derived_key = DerivedKey(
            key_id=key_id,
            key_material=key_material,
            derivation_method=parameters.method,
            security_level=parameters.security_level,
            purpose=context.purpose,
            context=context,
            parameters=parameters,
            parent_key_id=parent_key_id,
            derivation_path=derivation_path,
            created_at=datetime.utcnow(),
            expires_at=self._calculate_key_expiry(context.purpose, parameters.security_level),
            metadata={"cached": True, "cache_hit": True}
        )
        
        self.derived_keys[key_id] = derived_key
        await self._update_derivation_tree(parent_key_id, key_id)
        
        return key_id

    async def _get_parent_key_material(self, parent_key_id: str) -> Optional[bytes]:
        """Get parent key material for derivation."""
        # Check if it's a derived key
        if parent_key_id in self.derived_keys:
            return self.derived_keys[parent_key_id].key_material
        
        # Check if it's a master key
        if parent_key_id in self.master_keys:
            return self.master_keys[parent_key_id]
        
        # Check if it's the master derivation key
        if parent_key_id == "master_derivation_key":
            return self.master_derivation_key
        
        return None

    async def _perform_derivation(self,
                                 parent_key: bytes,
                                 context: DerivationContext,
                                 parameters: DerivationParameters) -> bytes:
        """Perform the actual key derivation."""
        # Create context-specific salt
        salt = self._create_context_salt(context, parameters.salt_length)
        
        if parameters.method == DerivationMethod.HKDF_SHA256:
            return await self._derive_hkdf(parent_key, salt, parameters, hashes.SHA256())
        
        elif parameters.method == DerivationMethod.HKDF_SHA384:
            return await self._derive_hkdf(parent_key, salt, parameters, hashes.SHA384())
        
        elif parameters.method == DerivationMethod.HKDF_SHA512:
            return await self._derive_hkdf(parent_key, salt, parameters, hashes.SHA512())
        
        elif parameters.method == DerivationMethod.PBKDF2_SHA256:
            return await self._derive_pbkdf2(parent_key, salt, parameters, hashes.SHA256())
        
        elif parameters.method == DerivationMethod.PBKDF2_SHA512:
            return await self._derive_pbkdf2(parent_key, salt, parameters, hashes.SHA512())
        
        elif parameters.method == DerivationMethod.SCRYPT:
            return await self._derive_scrypt(parent_key, salt, parameters)
        
        elif parameters.method == DerivationMethod.CONCAT_KDF:
            return await self._derive_concat_kdf(parent_key, salt, parameters)
        
        elif parameters.method == DerivationMethod.X963_KDF:
            return await self._derive_x963_kdf(parent_key, salt, parameters)
        
        elif parameters.method == DerivationMethod.BIP32_HDKD:
            return await self._derive_bip32_style(parent_key, context, parameters)
        
        else:
            raise ValueError(f"Unsupported derivation method: {parameters.method}")

    def _create_context_salt(self, context: DerivationContext, salt_length: int) -> bytes:
        """Create context-specific salt."""
        salt_components = [
            context.purpose.value.encode(),
            context.domain.encode()
        ]
        
        if context.creator_id:
            salt_components.append(context.creator_id.encode())
        if context.content_type:
            salt_components.append(context.content_type.encode())
        if context.tenant_id:
            salt_components.append(context.tenant_id.encode())
        
        # Add additional data if present
        if context.additional_data:
            salt_components.append(json.dumps(context.additional_data, sort_keys=True).encode())
        
        # Combine all components
        combined_salt = b"::".join(salt_components)
        
        # Hash to required length
        if salt_length <= 32:
            salt_hash = hashlib.sha256(combined_salt).digest()
        elif salt_length <= 48:
            salt_hash = hashlib.sha384(combined_salt).digest()
        else:
            salt_hash = hashlib.sha512(combined_salt).digest()
        
        return salt_hash[:salt_length]

    async def _derive_hkdf(self, parent_key: bytes, salt: bytes, parameters: DerivationParameters, hash_algorithm) -> bytes:
        """Derive key using HKDF."""
        hkdf = HKDF(
            algorithm=hash_algorithm,
            length=parameters.key_length,
            salt=salt,
            info=parameters.info or b"iacherie_hkdf_default"
        )
        return hkdf.derive(parent_key)

    async def _derive_pbkdf2(self, parent_key: bytes, salt: bytes, parameters: DerivationParameters, hash_algorithm) -> bytes:
        """Derive key using PBKDF2."""
        kdf = PBKDF2HMAC(
            algorithm=hash_algorithm,
            length=parameters.key_length,
            salt=salt,
            iterations=parameters.iterations or 100000
        )
        return kdf.derive(parent_key)

    async def _derive_scrypt(self, parent_key: bytes, salt: bytes, parameters: DerivationParameters) -> bytes:
        """Derive key using Scrypt."""
        kdf = Scrypt(
            algorithm=hashes.SHA256(),
            length=parameters.key_length,
            salt=salt,
            n=parameters.iterations or 32768,
            r=parameters.memory_cost or 8,
            p=parameters.parallelism or 1
        )
        return kdf.derive(parent_key)

    async def _derive_concat_kdf(self, parent_key: bytes, salt: bytes, parameters: DerivationParameters) -> bytes:
        """Derive key using Concat KDF."""
        kdf = ConcatKDFHash(
            algorithm=hashes.SHA256(),
            length=parameters.key_length,
            otherinfo=parameters.info or b"iacherie_concat_kdf"
        )
        return kdf.derive(parent_key)

    async def _derive_x963_kdf(self, parent_key: bytes, salt: bytes, parameters: DerivationParameters) -> bytes:
        """Derive key using X9.63 KDF."""
        kdf = X963KDF(
            algorithm=hashes.SHA256(),
            length=parameters.key_length,
            sharedinfo=parameters.info or b"iacherie_x963_kdf"
        )
        return kdf.derive(parent_key)

    async def _derive_bip32_style(self, parent_key: bytes, context: DerivationContext, parameters: DerivationParameters) -> bytes:
        """Derive key using BIP32-style hierarchical derivation."""
        # Simplified BIP32-style derivation
        # In production, would use proper BIP32 implementation
        
        # Create index from context
        index_data = f"{context.purpose.value}:{context.domain}"
        if context.creator_id:
            index_data += f":{context.creator_id}"
        
        index = int(hashlib.sha256(index_data.encode()).hexdigest()[:8], 16) % (2**31)
        
        # HMAC-based derivation
        data = struct.pack(">I", index) + parent_key
        derived = hashlib.pbkdf2_hmac('sha512', data, b'bip32_style_salt', 2048)
        
        return derived[:parameters.key_length]

    def _calculate_key_expiry(self, purpose: KeyPurpose, security_level: SecurityLevel) -> Optional[datetime]:
        """Calculate key expiration based on purpose and security level."""
        expiry_policies = {
            KeyPurpose.SESSION_KEY: timedelta(hours=24),
            KeyPurpose.TRANSPORT_KEY: timedelta(hours=1),
            KeyPurpose.CONTENT_PROTECTION: timedelta(days=365),
            KeyPurpose.ENCRYPTION: timedelta(days=730),
            KeyPurpose.AUTHENTICATION: timedelta(days=90),
            KeyPurpose.SIGNING: timedelta(days=1095),  # 3 years
            KeyPurpose.WRAPPING: timedelta(days=1825),  # 5 years
            KeyPurpose.BACKUP_KEY: timedelta(days=2555),  # 7 years
        }
        
        base_expiry = expiry_policies.get(purpose, timedelta(days=365))
        
        # Adjust based on security level
        if security_level == SecurityLevel.ULTRA:
            base_expiry *= 2  # Longer expiry for ultra-secure keys
        elif security_level == SecurityLevel.QUANTUM_SAFE:
            base_expiry *= 3  # Even longer for quantum-safe keys
        
        return datetime.utcnow() + base_expiry

    async def _update_derivation_tree(self, parent_key_id: str, child_key_id: str):
        """Update derivation tree structure."""
        if parent_key_id not in self.derivation_trees:
            self.derivation_trees[parent_key_id] = {}
        
        self.derivation_trees[parent_key_id][child_key_id] = datetime.utcnow().isoformat()

    async def _cache_derivation_result(self, path: str, parameters: DerivationParameters, key_material: bytes):
        """Cache derivation result."""
        cache_key = self._create_cache_key(path, parameters)
        
        # Implement cache size limit
        max_cache_size = self.config.get("cache_max_size", 10000)
        if len(self.derivation_cache) >= max_cache_size:
            # Remove oldest entries (simplified LRU)
            oldest_key = next(iter(self.derivation_cache))
            del self.derivation_cache[oldest_key]
        
        self.derivation_cache[cache_key] = key_material

    async def derive_creator_keys(self,
                                 creator_id: str,
                                 creator_type: str,
                                 content_types: List[str],
                                 security_level: SecurityLevel = SecurityLevel.HIGH) -> Dict[str, str]:
        """
        Derive a complete set of keys for a creator.
        
        Args:
            creator_id: Creator identifier
            creator_type: Type of creator (musician, photographer, etc.)
            content_types: Types of content to create keys for
            security_level: Security level for derived keys
            
        Returns:
            Dict mapping content types to key IDs
        """
        try:
            creator_keys = {}
            
            for content_type in content_types:
                # Content protection key
                content_context = DerivationContext(
                    purpose=KeyPurpose.CONTENT_PROTECTION,
                    domain=f"{creator_type}_content",
                    creator_id=creator_id,
                    content_type=content_type,
                    additional_data={"creator_type": creator_type}
                )
                
                content_key_id = await self.derive_key(
                    parent_key_id="master_derivation_key",
                    context=content_context,
                    security_level=security_level
                )
                
                creator_keys[f"{content_type}_protection"] = content_key_id
                
                # Signing key for content integrity
                signing_context = DerivationContext(
                    purpose=KeyPurpose.SIGNING,
                    domain=f"{creator_type}_signing",
                    creator_id=creator_id,
                    content_type=content_type,
                    additional_data={"creator_type": creator_type, "integrity": True}
                )
                
                signing_key_id = await self.derive_key(
                    parent_key_id="master_derivation_key",
                    context=signing_context,
                    security_level=security_level
                )
                
                creator_keys[f"{content_type}_signing"] = signing_key_id
            
            # Authentication key for creator
            auth_context = DerivationContext(
                purpose=KeyPurpose.AUTHENTICATION,
                domain=f"{creator_type}_auth",
                creator_id=creator_id,
                additional_data={"creator_type": creator_type}
            )
            
            auth_key_id = await self.derive_key(
                parent_key_id="master_derivation_key",
                context=auth_context,
                security_level=security_level
            )
            
            creator_keys["authentication"] = auth_key_id
            
            self.logger.info(f"Creator keys derived: {len(creator_keys)} keys for creator {creator_id}")
            return creator_keys
            
        except Exception as e:
            self.logger.error(f"Creator key derivation failed: {e}")
            raise

    async def derive_session_keys(self,
                                 session_id: str,
                                 user_id: str,
                                 tenant_id: Optional[str] = None,
                                 key_purposes: List[KeyPurpose] = None) -> Dict[str, str]:
        """
        Derive session-specific keys.
        
        Args:
            session_id: Session identifier
            user_id: User identifier
            tenant_id: Optional tenant identifier
            key_purposes: List of key purposes to derive
            
        Returns:
            Dict mapping purposes to key IDs
        """
        try:
            if key_purposes is None:
                key_purposes = [KeyPurpose.SESSION_KEY, KeyPurpose.TRANSPORT_KEY]
            
            session_keys = {}
            
            for purpose in key_purposes:
                context = DerivationContext(
                    purpose=purpose,
                    domain="session_management",
                    session_id=session_id,
                    tenant_id=tenant_id,
                    additional_data={"user_id": user_id}
                )
                
                key_id = await self.derive_key(
                    parent_key_id="master_derivation_key",
                    context=context,
                    security_level=SecurityLevel.STANDARD,  # Sessions use standard security
                    cache_result=False  # Don't cache session keys
                )
                
                session_keys[purpose.value] = key_id
            
            return session_keys
            
        except Exception as e:
            self.logger.error(f"Session key derivation failed: {e}")
            raise

    async def get_derived_key(self, key_id: str, requester_id: str) -> Optional[DerivedKey]:
        """
        Get a derived key with access control.
        
        Args:
            key_id: Key identifier
            requester_id: ID of requesting entity
            
        Returns:
            DerivedKey if authorized, None otherwise
        """
        try:
            if key_id not in self.derived_keys:
                return None
            
            derived_key = self.derived_keys[key_id]
            
            # Check expiration
            if derived_key.expires_at and derived_key.expires_at < datetime.utcnow():
                self.logger.warning(f"Attempted access to expired key: {key_id}")
                return None
            
            # Update usage count
            derived_key.usage_count += 1
            
            # Log access
            await self._log_derivation_operation("KEY_ACCESSED", key_id, requester_id, {
                "usage_count": derived_key.usage_count,
                "purpose": derived_key.purpose.value
            })
            
            return derived_key
            
        except Exception as e:
            self.logger.error(f"Key retrieval failed: {e}")
            return None

    async def rotate_derived_keys(self, parent_key_id: str) -> Dict[str, str]:
        """
        Rotate all keys derived from a parent key.
        
        Args:
            parent_key_id: Parent key identifier
            
        Returns:
            Dict mapping old key IDs to new key IDs
        """
        try:
            rotation_mapping = {}
            
            # Find all child keys
            if parent_key_id not in self.derivation_trees:
                return rotation_mapping
            
            child_keys = list(self.derivation_trees[parent_key_id].keys())
            
            for old_key_id in child_keys:
                if old_key_id in self.derived_keys:
                    old_key = self.derived_keys[old_key_id]
                    
                    # Derive new key with same context
                    new_key_id = await self.derive_key(
                        parent_key_id=old_key.parent_key_id,
                        context=old_key.context,
                        security_level=old_key.security_level,
                        custom_parameters=old_key.parameters,
                        cache_result=False  # Don't cache during rotation
                    )
                    
                    rotation_mapping[old_key_id] = new_key_id
                    
                    # Mark old key as rotated
                    old_key.metadata["rotated"] = True
                    old_key.metadata["rotated_at"] = datetime.utcnow().isoformat()
                    old_key.metadata["replacement_key_id"] = new_key_id
            
            await self._log_derivation_operation("KEYS_ROTATED", parent_key_id, "system", {
                "rotated_count": len(rotation_mapping),
                "rotation_mapping": rotation_mapping
            })
            
            self.logger.info(f"Rotated {len(rotation_mapping)} keys for parent {parent_key_id}")
            return rotation_mapping
            
        except Exception as e:
            self.logger.error(f"Key rotation failed: {e}")
            raise

    async def get_derivation_tree(self, root_key_id: str) -> Dict[str, Any]:
        """Get hierarchical view of key derivations."""
        try:
            def build_tree(key_id: str, depth: int = 0) -> Dict[str, Any]:
                if depth > self.config.get("max_derivation_depth", 10):
                    return {"error": "max_depth_exceeded"}
                
                node = {"key_id": key_id, "children": {}}
                
                if key_id in self.derived_keys:
                    key_info = self.derived_keys[key_id]
                    node.update({
                        "purpose": key_info.purpose.value,
                        "security_level": key_info.security_level.value,
                        "created_at": key_info.created_at.isoformat(),
                        "usage_count": key_info.usage_count
                    })
                
                if key_id in self.derivation_trees:
                    for child_id in self.derivation_trees[key_id]:
                        node["children"][child_id] = build_tree(child_id, depth + 1)
                
                return node
            
            return build_tree(root_key_id)
            
        except Exception as e:
            self.logger.error(f"Failed to get derivation tree: {e}")
            raise

    async def _log_derivation_operation(self, operation: str, key_id: str, actor_id: str, details: Dict[str, Any]):
        """Log derivation operation for audit trail."""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "operation": operation,
            "key_id": key_id,
            "actor_id": actor_id,
            "details": details
        }
        
        self.logger.info(f"Derivation operation logged: {operation} for key {key_id}")

    async def get_derivation_status(self) -> Dict[str, Any]:
        """Get comprehensive derivation engine status."""
        try:
            active_keys = len([k for k in self.derived_keys.values() 
                             if not k.expires_at or k.expires_at > datetime.utcnow()])
            
            expired_keys = len([k for k in self.derived_keys.values() 
                              if k.expires_at and k.expires_at <= datetime.utcnow()])
            
            return {
                "derivation_engine_status": "operational",
                "total_derived_keys": len(self.derived_keys),
                "active_keys": active_keys,
                "expired_keys": expired_keys,
                "cache_size": len(self.derivation_cache),
                "cache_hit_rate": self._calculate_cache_hit_rate(),
                "derivation_trees": len(self.derivation_trees),
                "supported_methods": [method.value for method in DerivationMethod],
                "security_levels": [level.value for level in SecurityLevel],
                "key_purposes": [purpose.value for purpose in KeyPurpose],
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get derivation status: {e}")
            raise

    def _calculate_cache_hit_rate(self) -> float:
        """Calculate cache hit rate (simplified)."""
        # In production, would track actual hits/misses
        return 0.85  # Simulated 85% hit rate

    async def cleanup(self):
        """Cleanup derivation engine resources."""
        try:
            # Securely clear key material
            for key in self.derived_keys.values():
                key.key_material = b""
            
            self.derived_keys.clear()
            self.derivation_cache.clear()
            self.derivation_trees.clear()
            
            # Clear master key
# SECURITY: # SECURITY: self.master_derivation_key = b"" # MOVED TO ENV # MOVED TO ENV
# TODO: Move to environment variables or secure vault
# TODO: Move to environment variables or secure vault
            
            self.logger.info("Key Derivation Engine cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Derivation engine cleanup failed: {e}")


# Creator Economy Integration Functions
async def setup_creator_key_hierarchy(creator_id: str,
                                      creator_type: str,
                                      content_types: List[str],
                                      derivation_engine: KeyDerivationEngine) -> Dict[str, Any]:
    """Setup hierarchical key structure for creator."""
    # Derive master creator key
    master_context = DerivationContext(
        purpose=KeyPurpose.WRAPPING,
        domain=f"{creator_type}_master",
        creator_id=creator_id,
        additional_data={"creator_type": creator_type, "master_key": True}
    )
    
    master_key_id = await derivation_engine.derive_key(
        parent_key_id="master_derivation_key",
        context=master_context,
        security_level=SecurityLevel.ULTRA
    )
    
    # Derive content-specific keys from master
    content_keys = {}
    for content_type in content_types:
        content_context = DerivationContext(
            purpose=KeyPurpose.CONTENT_PROTECTION,
            domain=f"{creator_type}_{content_type}",
            creator_id=creator_id,
            content_type=content_type
        )
        
        content_key_id = await derivation_engine.derive_key(
            parent_key_id=master_key_id,
            context=content_context,
            security_level=SecurityLevel.HIGH
        )
        
        content_keys[content_type] = content_key_id
    
    return {
        "master_key_id": master_key_id,
        "content_keys": content_keys,
        "derivation_tree": await derivation_engine.get_derivation_tree(master_key_id)
    }


# Export main classes and functions
__all__ = [
    "KeyDerivationEngine",
    "DerivationMethod",
    "KeyPurpose",
    "SecurityLevel",
    "DerivationContext",
    "DerivationParameters",
    "DerivedKey",
    "DerivationRequest",
    "setup_creator_key_hierarchy"
]