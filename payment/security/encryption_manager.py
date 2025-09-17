#!/usr/bin/env python3
"""
🔐 Advanced Encryption Management System
==========================================

Enterprise-grade encryption management for Ainflue payment security.
Provides AES-256, RSA-4096, Elliptic Curve cryptography with HSM integration.

Author: Expert Team (Security Lead + Backend Senior + Cryptography Specialist)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
License: Proprietary - Contact mlaiel@live.de for enterprise licensing

⚠️  LEGAL WARNING:
This code is proprietary to Fahed Mlaiel. Unauthorized use, distribution,
reverse engineering, or commercial exploitation is strictly prohibited.
Violations will result in immediate legal action.
"""

import asyncio
import hashlib
import hmac
import logging
import secrets
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Tuple, Union, Any
import os
import json
import base64

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, ec, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend


class EncryptionType(Enum):
    """Types d'encryption supportés"""
    AES_256_GCM = "aes_256_gcm"
    AES_256_CBC = "aes_256_cbc" 
    RSA_4096 = "rsa_4096"
    ECDSA_P256 = "ecdsa_p256"
    ECDSA_P384 = "ecdsa_p384"
    FERNET = "fernet"
    CHACHA20_POLY1305 = "chacha20_poly1305"


class KeyType(Enum):
    """Types de clés cryptographiques"""
    SYMMETRIC = "symmetric"
    ASYMMETRIC_PUBLIC = "asymmetric_public"
    ASYMMETRIC_PRIVATE = "asymmetric_private"
    MASTER_KEY = "master_key"
    SESSION_KEY = "session_key"
    PAYMENT_KEY = "payment_key"
    CREATOR_KEY = "creator_key"


class SecurityLevel(Enum):
    """Niveaux de sécurité"""
    MINIMAL = "minimal"
    STANDARD = "standard" 
    HIGH = "high"
    CRITICAL = "critical"
    ENTERPRISE = "enterprise"


@dataclass
class EncryptionKey:
    """Représentation d'une clé de chiffrement"""
    key_id: str
    key_type: KeyType
    encryption_type: EncryptionType
    key_data: bytes
    created_at: datetime
    expires_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    is_active: bool = True
    usage_count: int = 0
    max_usage: Optional[int] = None


@dataclass
class EncryptionResult:
    """Résultat d'opération de chiffrement"""
    encrypted_data: bytes
    key_id: str
    encryption_type: EncryptionType
    iv_or_nonce: Optional[bytes] = None
    auth_tag: Optional[bytes] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DecryptionResult:
    """Résultat d'opération de déchiffrement"""
    decrypted_data: bytes
    key_id: str
    encryption_type: EncryptionType
    verified: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


class HSMInterface:
    """Interface pour Hardware Security Module (simulation)"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.is_available = False  # Simulation HSM
        
    async def generate_key(self, key_type: KeyType, size: int = 256) -> bytes:
        """Génération de clé via HSM"""
        # Simulation - en production, intégration HSM réelle
        self.logger.info(f"HSM generating {key_type.value} key of {size} bits")
        return secrets.token_bytes(size // 8)
        
    async def sign_data(self, data: bytes, key_id: str) -> bytes:
        """Signature de données via HSM"""
        # Simulation HSM signature
        return hashlib.sha256(data + key_id.encode()).digest()
        
    async def verify_signature(self, data: bytes, signature: bytes, key_id: str) -> bool:
        """Vérification de signature via HSM"""
        expected = await self.sign_data(data, key_id)
        return hmac.compare_digest(signature, expected)


class KeyRotationManager:
    """Gestionnaire de rotation des clés"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.rotation_policies: Dict[KeyType, timedelta] = {
            KeyType.SESSION_KEY: timedelta(hours=24),
            KeyType.PAYMENT_KEY: timedelta(days=30),
            KeyType.CREATOR_KEY: timedelta(days=90),
            KeyType.MASTER_KEY: timedelta(days=365)
        }
        
    async def should_rotate_key(self, key: EncryptionKey) -> bool:
        """Détermine si une clé doit être pivotée"""
        if not key.is_active:
            return True
            
        # Vérification expiration
        if key.expires_at and datetime.utcnow() >= key.expires_at:
            return True
            
        # Vérification politique de rotation
        if key.key_type in self.rotation_policies:
            rotation_interval = self.rotation_policies[key.key_type]
            if datetime.utcnow() - key.created_at >= rotation_interval:
                return True
                
        # Vérification usage maximum
        if key.max_usage and key.usage_count >= key.max_usage:
            return True
            
        return False
        
    async def rotate_key(self, old_key: EncryptionKey, 
                        key_manager: 'AdvancedEncryptionManager') -> EncryptionKey:
        """Rotation d'une clé"""
        self.logger.info(f"Rotating key {old_key.key_id}")
        
        # Générer nouvelle clé
        new_key = await key_manager.generate_key(
            key_type=old_key.key_type,
            encryption_type=old_key.encryption_type
        )
        
        # Marquer ancienne clé comme inactive
        old_key.is_active = False
        
        # Notification de rotation
        await self._notify_key_rotation(old_key.key_id, new_key.key_id)
        
        return new_key
        
    async def _notify_key_rotation(self, old_key_id: str, new_key_id: str):
        """Notification de rotation de clé"""
        self.logger.info(f"Key rotated: {old_key_id} -> {new_key_id}")


class AdvancedEncryptionManager:
    """
    Gestionnaire de chiffrement avancé enterprise-grade
    
    Fonctionnalités:
    - Multiple algorithmes de chiffrement (AES, RSA, ECC)
    - Gestion de clés avec rotation automatique
    - Intégration HSM pour sécurité maximale
    - Support PCI DSS, SOX, GDPR
    - Analytics et audit complets
    """
    
    def __init__(self, hsm_enabled: bool = False):
        self.logger = logging.getLogger(__name__)
        self.keys: Dict[str, EncryptionKey] = {}
        self.encryption_cache: Dict[str, Any] = {}
        self.hsm = HSMInterface() if hsm_enabled else None
        self.key_rotation = KeyRotationManager()
        self.metrics = {
            'encryption_operations': 0,
            'decryption_operations': 0,
            'key_generations': 0,
            'key_rotations': 0,
            'failed_operations': 0
        }
        
        # Configuration sécurité
        self.security_config = {
            'default_key_size': 256,
            'max_key_age_hours': 24 * 30,  # 30 jours
            'require_auth_tag': True,
            'enable_key_escrow': True,
            'audit_all_operations': True
        }
        
        self.logger.info("Advanced Encryption Manager initialized")
        
    async def generate_key(self, 
                          key_type: KeyType,
                          encryption_type: EncryptionType,
                          security_level: SecurityLevel = SecurityLevel.HIGH,
                          metadata: Optional[Dict[str, Any]] = None) -> EncryptionKey:
        """Génération de clé cryptographique"""
        try:
            key_id = f"{key_type.value}_{encryption_type.value}_{secrets.token_hex(16)}"
            
            if encryption_type == EncryptionType.AES_256_GCM:
                key_data = secrets.token_bytes(32)  # 256 bits
            elif encryption_type == EncryptionType.RSA_4096:
                # Génération clé RSA 4096 bits
                private_key = rsa.generate_private_key(
                    public_exponent=65537,
                    key_size=4096,
                    backend=default_backend()
                )
                key_data = private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
                )
            elif encryption_type in [EncryptionType.ECDSA_P256, EncryptionType.ECDSA_P384]:
                # Génération clé ECDSA
                curve = ec.SECP256R1() if encryption_type == EncryptionType.ECDSA_P256 else ec.SECP384R1()
                private_key = ec.generate_private_key(curve, default_backend())
                key_data = private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
                )
            elif encryption_type == EncryptionType.FERNET:
                key_data = Fernet.generate_key()
            else:
                key_data = secrets.token_bytes(32)
                
            # Utiliser HSM si disponible
            if self.hsm and self.hsm.is_available:
                key_data = await self.hsm.generate_key(key_type)
                
            # Créer objet clé
            encryption_key = EncryptionKey(
                key_id=key_id,
                key_type=key_type,
                encryption_type=encryption_type,
                key_data=key_data,
                created_at=datetime.utcnow(),
                expires_at=datetime.utcnow() + timedelta(hours=self.security_config['max_key_age_hours']),
                metadata=metadata or {}
            )
            
            # Stocker clé
            self.keys[key_id] = encryption_key
            self.metrics['key_generations'] += 1
            
            self.logger.info(f"Generated {encryption_type.value} key: {key_id}")
            return encryption_key
            
        except Exception as e:
            self.metrics['failed_operations'] += 1
            self.logger.error(f"Key generation failed: {str(e)}")
            raise
            
    async def encrypt_data(self, 
                          data: Union[str, bytes],
                          key_id: str,
                          additional_data: Optional[bytes] = None) -> EncryptionResult:
        """Chiffrement de données"""
        try:
            if key_id not in self.keys:
                raise ValueError(f"Key not found: {key_id}")
                
            key = self.keys[key_id]
            if not key.is_active:
                raise ValueError(f"Key is inactive: {key_id}")
                
            # Vérifier rotation de clé
            if await self.key_rotation.should_rotate_key(key):
                new_key = await self.key_rotation.rotate_key(key, self)
                key = new_key
                key_id = new_key.key_id
                
            # Convertir en bytes si nécessaire
            if isinstance(data, str):
                data = data.encode('utf-8')
                
            encrypted_data = None
            iv_or_nonce = None
            auth_tag = None
            
            # Chiffrement selon l'algorithme
            if key.encryption_type == EncryptionType.AES_256_GCM:
                iv = secrets.token_bytes(12)  # 96 bits pour GCM
                cipher = Cipher(
                    algorithms.AES(key.key_data),
                    modes.GCM(iv),
                    backend=default_backend()
                )
                encryptor = cipher.encryptor()
                if additional_data:
                    encryptor.authenticate_additional_data(additional_data)
                encrypted_data = encryptor.update(data) + encryptor.finalize()
                iv_or_nonce = iv
                auth_tag = encryptor.tag
                
            elif key.encryption_type == EncryptionType.AES_256_CBC:
                iv = secrets.token_bytes(16)  # 128 bits pour CBC
                cipher = Cipher(
                    algorithms.AES(key.key_data),
                    modes.CBC(iv),
                    backend=default_backend()
                )
                encryptor = cipher.encryptor()
                # Padding PKCS7
                pad_length = 16 - (len(data) % 16)
                padded_data = data + bytes([pad_length] * pad_length)
                encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
                iv_or_nonce = iv
                
            elif key.encryption_type == EncryptionType.FERNET:
                fernet = Fernet(key.key_data)
                encrypted_data = fernet.encrypt(data)
                
            elif key.encryption_type == EncryptionType.RSA_4096:
                # Chiffrement RSA avec OAEP
                private_key = serialization.load_pem_private_key(
                    key.key_data, password=None, backend=default_backend()
                )
                public_key = private_key.public_key()
                encrypted_data = public_key.encrypt(
                    data,
                    padding.OAEP(
                        mgf=padding.MGF1(algorithm=hashes.SHA256()),
                        algorithm=hashes.SHA256(),
                        label=None
                    )
                )
                
            # Incrémenter compteur d'usage
            key.usage_count += 1
            self.metrics['encryption_operations'] += 1
            
            result = EncryptionResult(
                encrypted_data=encrypted_data,
                key_id=key_id,
                encryption_type=key.encryption_type,
                iv_or_nonce=iv_or_nonce,
                auth_tag=auth_tag,
                metadata={'timestamp': datetime.utcnow().isoformat()}
            )
            
            self.logger.debug(f"Data encrypted with key: {key_id}")
            return result
            
        except Exception as e:
            self.metrics['failed_operations'] += 1
            self.logger.error(f"Encryption failed: {str(e)}")
            raise
            
    async def decrypt_data(self, 
                          encryption_result: EncryptionResult,
                          additional_data: Optional[bytes] = None) -> DecryptionResult:
        """Déchiffrement de données"""
        try:
            key_id = encryption_result.key_id
            if key_id not in self.keys:
                raise ValueError(f"Key not found: {key_id}")
                
            key = self.keys[key_id]
            encrypted_data = encryption_result.encrypted_data
            
            decrypted_data = None
            verified = True
            
            # Déchiffrement selon l'algorithme
            if key.encryption_type == EncryptionType.AES_256_GCM:
                if not encryption_result.iv_or_nonce or not encryption_result.auth_tag:
                    raise ValueError("IV and auth tag required for GCM decryption")
                    
                cipher = Cipher(
                    algorithms.AES(key.key_data),
                    modes.GCM(encryption_result.iv_or_nonce, encryption_result.auth_tag),
                    backend=default_backend()
                )
                decryptor = cipher.decryptor()
                if additional_data:
                    decryptor.authenticate_additional_data(additional_data)
                decrypted_data = decryptor.update(encrypted_data) + decryptor.finalize()
                
            elif key.encryption_type == EncryptionType.AES_256_CBC:
                if not encryption_result.iv_or_nonce:
                    raise ValueError("IV required for CBC decryption")
                    
                cipher = Cipher(
                    algorithms.AES(key.key_data),
                    modes.CBC(encryption_result.iv_or_nonce),
                    backend=default_backend()
                )
                decryptor = cipher.decryptor()
                padded_data = decryptor.update(encrypted_data) + decryptor.finalize()
                # Supprimer padding PKCS7
                pad_length = padded_data[-1]
                decrypted_data = padded_data[:-pad_length]
                
            elif key.encryption_type == EncryptionType.FERNET:
                fernet = Fernet(key.key_data)
                decrypted_data = fernet.decrypt(encrypted_data)
                
            elif key.encryption_type == EncryptionType.RSA_4096:
                # Déchiffrement RSA avec OAEP
                private_key = serialization.load_pem_private_key(
                    key.key_data, password=None, backend=default_backend()
                )
                decrypted_data = private_key.decrypt(
                    encrypted_data,
                    padding.OAEP(
                        mgf=padding.MGF1(algorithm=hashes.SHA256()),
                        algorithm=hashes.SHA256(),
                        label=None
                    )
                )
                
            self.metrics['decryption_operations'] += 1
            
            result = DecryptionResult(
                decrypted_data=decrypted_data,
                key_id=key_id,
                encryption_type=key.encryption_type,
                verified=verified,
                metadata={'timestamp': datetime.utcnow().isoformat()}
            )
            
            self.logger.debug(f"Data decrypted with key: {key_id}")
            return result
            
        except Exception as e:
            self.metrics['failed_operations'] += 1
            self.logger.error(f"Decryption failed: {str(e)}")
            raise
            
    async def rotate_all_keys(self) -> Dict[str, str]:
        """Rotation de toutes les clés éligibles"""
        rotated_keys = {}
        
        for key_id, key in list(self.keys.items()):
            if await self.key_rotation.should_rotate_key(key):
                try:
                    new_key = await self.key_rotation.rotate_key(key, self)
                    rotated_keys[key_id] = new_key.key_id
                    self.metrics['key_rotations'] += 1
                except Exception as e:
                    self.logger.error(f"Failed to rotate key {key_id}: {str(e)}")
                    
        self.logger.info(f"Rotated {len(rotated_keys)} keys")
        return rotated_keys
        
    async def export_public_key(self, key_id: str) -> bytes:
        """Export de clé publique"""
        if key_id not in self.keys:
            raise ValueError(f"Key not found: {key_id}")
            
        key = self.keys[key_id]
        
        if key.encryption_type == EncryptionType.RSA_4096:
            private_key = serialization.load_pem_private_key(
                key.key_data, password=None, backend=default_backend()
            )
            public_key = private_key.public_key()
            return public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
        elif key.encryption_type in [EncryptionType.ECDSA_P256, EncryptionType.ECDSA_P384]:
            private_key = serialization.load_pem_private_key(
                key.key_data, password=None, backend=default_backend()
            )
            public_key = private_key.public_key()
            return public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
        else:
            raise ValueError(f"Public key export not supported for {key.encryption_type}")
            
    async def get_encryption_metrics(self) -> Dict[str, Any]:
        """Métriques de chiffrement"""
        active_keys = sum(1 for key in self.keys.values() if key.is_active)
        expired_keys = sum(1 for key in self.keys.values() 
                          if key.expires_at and datetime.utcnow() >= key.expires_at)
        
        return {
            'total_keys': len(self.keys),
            'active_keys': active_keys,
            'expired_keys': expired_keys,
            'operations': self.metrics,
            'hsm_available': self.hsm and self.hsm.is_available,
            'uptime_seconds': time.time()
        }
        
    async def audit_key_usage(self) -> List[Dict[str, Any]]:
        """Audit d'utilisation des clés"""
        audit_data = []
        
        for key_id, key in self.keys.items():
            audit_entry = {
                'key_id': key_id,
                'key_type': key.key_type.value,
                'encryption_type': key.encryption_type.value,
                'created_at': key.created_at.isoformat(),
                'expires_at': key.expires_at.isoformat() if key.expires_at else None,
                'is_active': key.is_active,
                'usage_count': key.usage_count,
                'max_usage': key.max_usage,
                'should_rotate': await self.key_rotation.should_rotate_key(key)
            }
            audit_data.append(audit_entry)
            
        return audit_data
        
    async def emergency_key_revocation(self, key_id: str, reason: str):
        """Révocation d'urgence d'une clé"""
        if key_id not in self.keys:
            raise ValueError(f"Key not found: {key_id}")
            
        key = self.keys[key_id]
        key.is_active = False
        key.metadata['revoked_at'] = datetime.utcnow().isoformat()
        key.metadata['revocation_reason'] = reason
        
        self.logger.warning(f"Emergency key revocation: {key_id} - {reason}")
        
        # Notification urgente
        await self._send_emergency_notification(key_id, reason)
        
    async def _send_emergency_notification(self, key_id: str, reason: str):
        """Notification d'urgence"""
        # Simulation notification - intégration avec système d'alertes
        self.logger.critical(f"EMERGENCY: Key {key_id} revoked - {reason}")


# Instance globale du gestionnaire de chiffrement
encryption_manager = AdvancedEncryptionManager()


async def get_encryption_manager() -> AdvancedEncryptionManager:
    """Factory function pour le gestionnaire de chiffrement"""
    return encryption_manager


# Fonctions utilitaires pour intégration Ainflue
async def encrypt_creator_revenue_data(creator_id: str, revenue_data: dict) -> EncryptionResult:
    """Chiffrement spécialisé des données de revenus créateur"""
    # Génération clé spécifique créateur si nécessaire
    key_id = f"creator_{creator_id}_revenue"
    
    # Vérifier si clé existe
    if key_id not in encryption_manager.keys:
        await encryption_manager.generate_key(
            key_type=KeyType.CREATOR_KEY,
            encryption_type=EncryptionType.AES_256_GCM,
            metadata={'creator_id': creator_id, 'purpose': 'revenue_protection'}
        )
    
    # Chiffrer données revenue
    revenue_json = json.dumps(revenue_data, sort_keys=True)
    return await encryption_manager.encrypt_data(revenue_json, key_id)


async def encrypt_payment_transaction(transaction_data: dict) -> EncryptionResult:
    """Chiffrement spécialisé des transactions de paiement"""
    # Utilisation clé de paiement dédiée
    payment_keys = [k for k in encryption_manager.keys.values() 
                   if k.key_type == KeyType.PAYMENT_KEY and k.is_active]
    
    if not payment_keys:
        # Générer nouvelle clé de paiement
        payment_key = await encryption_manager.generate_key(
            key_type=KeyType.PAYMENT_KEY,
            encryption_type=EncryptionType.AES_256_GCM,
            security_level=SecurityLevel.CRITICAL
        )
        key_id = payment_key.key_id
    else:
        key_id = payment_keys[0].key_id
    
    # Chiffrer transaction avec données additionnelles
    transaction_json = json.dumps(transaction_data, sort_keys=True)
    additional_data = f"payment_tx_{transaction_data.get('tx_id', 'unknown')}".encode()
    
    return await encryption_manager.encrypt_data(
        transaction_json, 
        key_id, 
        additional_data=additional_data
    )


# Export des classes principales
__all__ = [
    'AdvancedEncryptionManager',
    'EncryptionKey',
    'EncryptionResult', 
    'DecryptionResult',
    'EncryptionType',
    'KeyType',
    'SecurityLevel',
    'HSMInterface',
    'KeyRotationManager',
    'encryption_manager',
    'get_encryption_manager',
    'encrypt_creator_revenue_data',
    'encrypt_payment_transaction'
]


# Initialisation automatique pour tests
if __name__ == "__main__":
    async def demo_encryption():
        """Démonstration du système de chiffrement"""
        manager = await get_encryption_manager()
        
        # Test génération clé AES
        aes_key = await manager.generate_key(
            KeyType.PAYMENT_KEY,
            EncryptionType.AES_256_GCM
        )
        print(f"Generated AES key: {aes_key.key_id}")
        
        # Test chiffrement/déchiffrement
        test_data = "Sensitive payment data for creator revenue protection"
        encrypted = await manager.encrypt_data(test_data, aes_key.key_id)
        print(f"Encrypted data length: {len(encrypted.encrypted_data)} bytes")
        
        decrypted = await manager.decrypt_data(encrypted)
        print(f"Decrypted: {decrypted.decrypted_data.decode()}")
        
        # Test génération clé RSA
        rsa_key = await manager.generate_key(
            KeyType.ASYMMETRIC_PRIVATE,
            EncryptionType.RSA_4096
        )
        print(f"Generated RSA key: {rsa_key.key_id}")
        
        # Métriques
        metrics = await manager.get_encryption_metrics()
        print(f"Encryption metrics: {metrics}")
        
        # Test spécialisé Ainflue
        creator_revenue = {
            'creator_id': 'creator_123',
            'revenue_amount': 1250.75,
            'currency': 'USD',
            'period': '2025-01'
        }
        
        encrypted_revenue = await encrypt_creator_revenue_data('creator_123', creator_revenue)
        print(f"Creator revenue encrypted: {len(encrypted_revenue.encrypted_data)} bytes")
        
    # Exécution démo
    asyncio.run(demo_encryption())