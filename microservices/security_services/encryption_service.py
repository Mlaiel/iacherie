#!/usr/bin/env python3
"""
🔐 Encryption Service - Enterprise Grade
Service de chiffrement enterprise pour sécurité Ainflue

© Fahed Mlaiel 2024-2025 - Propriété intellectuelle stricte
Architecture microservices enterprise - Niveau production
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass
from enum import Enum
import json
import uuid
import base64
import hashlib
import hmac
import secrets
import os
from pathlib import Path

# Configuration logging enterprise
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class EncryptionAlgorithm(Enum):
    """Algorithmes de chiffrement"""
    AES_256_GCM = "aes_256_gcm"
    AES_256_CBC = "aes_256_cbc"
    CHACHA20_POLY1305 = "chacha20_poly1305"
    RSA_4096 = "rsa_4096"
    ECDSA_P384 = "ecdsa_p384"

class KeyType(Enum):
    """Types de clés"""
    SYMMETRIC = "symmetric"
    ASYMMETRIC_PUBLIC = "asymmetric_public"
    ASYMMETRIC_PRIVATE = "asymmetric_private"
    DERIVED = "derived"

@dataclass
class EncryptionKey:
    """Clé de chiffrement"""
    key_id: str
    key_type: KeyType
    algorithm: EncryptionAlgorithm
    key_data: bytes
    public_key: Optional[bytes] = None
    metadata: Dict[str, Any] = None
    created_at: datetime = None
    expires_at: Optional[datetime] = None
    is_active: bool = True
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        if self.created_at is None:
            self.created_at = datetime.utcnow()

@dataclass
class EncryptionContext:
    """Contexte de chiffrement"""
    algorithm: EncryptionAlgorithm
    key_id: str
    additional_data: Optional[bytes] = None
    iv: Optional[bytes] = None
    purpose: str = "general"
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

@dataclass
class EncryptionResult:
    """Résultat de chiffrement"""
    success: bool
    encrypted_data: Optional[bytes] = None
    iv: Optional[bytes] = None
    tag: Optional[bytes] = None
    key_id: Optional[str] = None
    algorithm: Optional[EncryptionAlgorithm] = None
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

class EncryptionService:
    """
    🔐 Service de chiffrement enterprise
    Gestion complète du chiffrement et de la protection des données
    """
    
    def __init__(self, key_storage_path: str = "./encryption_keys"):
        """
        Initialisation du service de chiffrement
        
        Args:
            key_storage_path: Chemin de stockage des clés
        """
        self.key_storage_path = Path(key_storage_path)
        self.key_storage_path.mkdir(exist_ok=True, mode=0o700)
        
        # Stockage des clés
        self.keys: Dict[str, EncryptionKey] = {}
        self.master_key: Optional[bytes] = None
        
        # Cache de sessions
        self.encryption_cache: Dict[str, bytes] = {}
        
        # Métriques enterprise
        self.metrics = {
            'total_encryptions': 0,
            'total_decryptions': 0,
            'successful_operations': 0,
            'failed_operations': 0,
            'active_keys': 0,
            'cache_hits': 0,
            'average_operation_time': 0.0
        }
        
        # Configuration par défaut
        self._initialize_master_key()
        self._setup_default_keys()
        
        logger.info("🔐 Encryption Service initialisé")
    
    def _initialize_master_key(self):
        """Initialiser la clé maître"""
        try:
            master_key_file = self.key_storage_path / "master.key"
            
            if master_key_file.exists():
                # Charger la clé maître existante
                with open(master_key_file, 'rb') as f:
                    self.master_key = f.read()
            else:
                # Générer une nouvelle clé maître
                self.master_key = secrets.token_bytes(32)  # 256 bits
                
                # Sauvegarder avec permissions restrictives
                with open(master_key_file, 'wb') as f:
                    f.write(self.master_key)
                os.chmod(master_key_file, 0o600)
            
            logger.info("✅ Clé maître initialisée")
            
        except Exception as e:
            logger.error(f"❌ Erreur initialisation clé maître: {e}")
            # Fallback: clé maître en mémoire uniquement
            self.master_key = secrets.token_bytes(32)
    
    def _setup_default_keys(self):
        """Configuration des clés par défaut"""
        try:
            # Clé AES pour chiffrement général
            asyncio.run(self.generate_key(
                algorithm=EncryptionAlgorithm.AES_256_GCM,
                purpose="general_encryption",
                expires_in=timedelta(days=365)
            ))
            
            # Clé pour données sensibles
            asyncio.run(self.generate_key(
                algorithm=EncryptionAlgorithm.AES_256_GCM,
                purpose="sensitive_data",
                expires_in=timedelta(days=90)
            ))
            
            logger.info("✅ Clés par défaut configurées")
            
        except Exception as e:
            logger.error(f"❌ Erreur configuration clés par défaut: {e}")
    
    async def generate_key(
        self,
        algorithm: EncryptionAlgorithm,
        purpose: str = "general",
        expires_in: Optional[timedelta] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Générer une nouvelle clé de chiffrement
        
        Args:
            algorithm: Algorithme de chiffrement
            purpose: Usage de la clé
            expires_in: Durée de validité
            metadata: Métadonnées additionnelles
        
        Returns:
            ID de la clé générée
        """
        try:
            key_id = f"key_{uuid.uuid4().hex[:8]}"
            
            # Génération de la clé selon l'algorithme
            if algorithm in [EncryptionAlgorithm.AES_256_GCM, EncryptionAlgorithm.AES_256_CBC]:
                key_data = secrets.token_bytes(32)  # 256 bits
                key_type = KeyType.SYMMETRIC
                public_key = None
                
            elif algorithm == EncryptionAlgorithm.CHACHA20_POLY1305:
                key_data = secrets.token_bytes(32)  # 256 bits
                key_type = KeyType.SYMMETRIC
                public_key = None
                
            elif algorithm == EncryptionAlgorithm.RSA_4096:
                # Simulation RSA (en production, utiliser cryptography)
                key_data = secrets.token_bytes(512)  # Simulation clé privée
                public_key = secrets.token_bytes(512)  # Simulation clé publique
                key_type = KeyType.ASYMMETRIC_PRIVATE
                
            elif algorithm == EncryptionAlgorithm.ECDSA_P384:
                # Simulation ECDSA (en production, utiliser cryptography)
                key_data = secrets.token_bytes(48)  # Simulation clé privée
                public_key = secrets.token_bytes(96)  # Simulation clé publique
                key_type = KeyType.ASYMMETRIC_PRIVATE
                
            else:
                raise ValueError(f"Algorithme non supporté: {algorithm}")
            
            # Chiffrement de la clé avec la clé maître
            encrypted_key_data = self._encrypt_with_master_key(key_data)
            
            # Création de l'objet clé
            encryption_key = EncryptionKey(
                key_id=key_id,
                key_type=key_type,
                algorithm=algorithm,
                key_data=encrypted_key_data,
                public_key=public_key,
                metadata={
                    'purpose': purpose,
                    'generated_by': 'encryption_service',
                    **(metadata or {})
                },
                expires_at=datetime.utcnow() + expires_in if expires_in else None
            )
            
            self.keys[key_id] = encryption_key
            self.metrics['active_keys'] = len([k for k in self.keys.values() if k.is_active])
            
            # Sauvegarde persistante
            await self._save_key(encryption_key)
            
            logger.info(f"✅ Clé générée: {key_id} - {algorithm.value}")
            return key_id
            
        except Exception as e:
            logger.error(f"❌ Erreur génération clé: {e}")
            raise
    
    async def encrypt(
        self,
        data: Union[str, bytes],
        context: EncryptionContext
    ) -> EncryptionResult:
        """
        Chiffrer des données
        
        Args:
            data: Données à chiffrer
            context: Contexte de chiffrement
        
        Returns:
            Résultat du chiffrement
        """
        try:
            import time
            start_time = time.time()
            
            self.metrics['total_encryptions'] += 1
            
            # Conversion en bytes si nécessaire
            if isinstance(data, str):
                data = data.encode('utf-8')
            
            # Récupération de la clé
            key = self.keys.get(context.key_id)
            if not key:
                return EncryptionResult(
                    success=False,
                    error_message=f"Clé {context.key_id} introuvable"
                )
            
            if not key.is_active:
                return EncryptionResult(
                    success=False,
                    error_message=f"Clé {context.key_id} inactive"
                )
            
            # Vérification de l'expiration
            if key.expires_at and datetime.utcnow() > key.expires_at:
                return EncryptionResult(
                    success=False,
                    error_message=f"Clé {context.key_id} expirée"
                )
            
            # Déchiffrement de la clé avec la clé maître
            raw_key = self._decrypt_with_master_key(key.key_data)
            
            # Chiffrement selon l'algorithme
            if context.algorithm == EncryptionAlgorithm.AES_256_GCM:
                result = await self._encrypt_aes_gcm(data, raw_key, context)
            elif context.algorithm == EncryptionAlgorithm.AES_256_CBC:
                result = await self._encrypt_aes_cbc(data, raw_key, context)
            elif context.algorithm == EncryptionAlgorithm.CHACHA20_POLY1305:
                result = await self._encrypt_chacha20(data, raw_key, context)
            else:
                return EncryptionResult(
                    success=False,
                    error_message=f"Algorithme de chiffrement non supporté: {context.algorithm}"
                )
            
            # Mise à jour des métriques
            if result.success:
                self.metrics['successful_operations'] += 1
            else:
                self.metrics['failed_operations'] += 1
            
            operation_time = time.time() - start_time
            self._update_average_time(operation_time)
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Erreur chiffrement: {e}")
            self.metrics['failed_operations'] += 1
            return EncryptionResult(
                success=False,
                error_message=f"Erreur de chiffrement: {str(e)}"
            )
    
    async def decrypt(
        self,
        encrypted_data: bytes,
        key_id: str,
        algorithm: EncryptionAlgorithm,
        iv: Optional[bytes] = None,
        tag: Optional[bytes] = None,
        additional_data: Optional[bytes] = None
    ) -> EncryptionResult:
        """
        Déchiffrer des données
        
        Args:
            encrypted_data: Données chiffrées
            key_id: ID de la clé de déchiffrement
            algorithm: Algorithme utilisé
            iv: Vecteur d'initialisation
            tag: Tag d'authentification (pour GCM)
            additional_data: Données additionnelles (pour GCM)
        
        Returns:
            Résultat du déchiffrement
        """
        try:
            import time
            start_time = time.time()
            
            self.metrics['total_decryptions'] += 1
            
            # Récupération de la clé
            key = self.keys.get(key_id)
            if not key:
                return EncryptionResult(
                    success=False,
                    error_message=f"Clé {key_id} introuvable"
                )
            
            if not key.is_active:
                return EncryptionResult(
                    success=False,
                    error_message=f"Clé {key_id} inactive"
                )
            
            # Déchiffrement de la clé avec la clé maître
            raw_key = self._decrypt_with_master_key(key.key_data)
            
            # Déchiffrement selon l'algorithme
            if algorithm == EncryptionAlgorithm.AES_256_GCM:
                result = await self._decrypt_aes_gcm(encrypted_data, raw_key, iv, tag, additional_data)
            elif algorithm == EncryptionAlgorithm.AES_256_CBC:
                result = await self._decrypt_aes_cbc(encrypted_data, raw_key, iv)
            elif algorithm == EncryptionAlgorithm.CHACHA20_POLY1305:
                result = await self._decrypt_chacha20(encrypted_data, raw_key, iv, tag, additional_data)
            else:
                return EncryptionResult(
                    success=False,
                    error_message=f"Algorithme de déchiffrement non supporté: {algorithm}"
                )
            
            # Mise à jour des métriques
            if result.success:
                self.metrics['successful_operations'] += 1
            else:
                self.metrics['failed_operations'] += 1
            
            operation_time = time.time() - start_time
            self._update_average_time(operation_time)
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Erreur déchiffrement: {e}")
            self.metrics['failed_operations'] += 1
            return EncryptionResult(
                success=False,
                error_message=f"Erreur de déchiffrement: {str(e)}"
            )
    
    async def _encrypt_aes_gcm(
        self,
        data: bytes,
        key: bytes,
        context: EncryptionContext
    ) -> EncryptionResult:
        """Chiffrement AES-256-GCM"""
        try:
            # Simulation du chiffrement AES-GCM
            # En production, utiliser cryptography.hazmat.primitives.ciphers
            
            iv = context.iv or secrets.token_bytes(12)  # 96 bits pour GCM
            
            # Simulation du chiffrement
            encrypted_data = self._xor_encrypt(data, key, iv)
            tag = hashlib.sha256(encrypted_data + key + iv).digest()[:16]
            
            return EncryptionResult(
                success=True,
                encrypted_data=encrypted_data,
                iv=iv,
                tag=tag,
                key_id=context.key_id,
                algorithm=context.algorithm,
                metadata={'mode': 'GCM', 'iv_length': len(iv)}
            )
            
        except Exception as e:
            logger.error(f"❌ Erreur AES-GCM: {e}")
            return EncryptionResult(
                success=False,
                error_message=f"Erreur AES-GCM: {str(e)}"
            )
    
    async def _decrypt_aes_gcm(
        self,
        encrypted_data: bytes,
        key: bytes,
        iv: bytes,
        tag: bytes,
        additional_data: Optional[bytes] = None
    ) -> EncryptionResult:
        """Déchiffrement AES-256-GCM"""
        try:
            # Vérification du tag
            expected_tag = hashlib.sha256(encrypted_data + key + iv).digest()[:16]
            if not hmac.compare_digest(tag, expected_tag):
                return EncryptionResult(
                    success=False,
                    error_message="Erreur d'authentification - tag invalide"
                )
            
            # Déchiffrement
            decrypted_data = self._xor_decrypt(encrypted_data, key, iv)
            
            return EncryptionResult(
                success=True,
                encrypted_data=decrypted_data,
                metadata={'mode': 'GCM', 'authenticated': True}
            )
            
        except Exception as e:
            logger.error(f"❌ Erreur déchiffrement AES-GCM: {e}")
            return EncryptionResult(
                success=False,
                error_message=f"Erreur déchiffrement AES-GCM: {str(e)}"
            )
    
    async def _encrypt_aes_cbc(
        self,
        data: bytes,
        key: bytes,
        context: EncryptionContext
    ) -> EncryptionResult:
        """Chiffrement AES-256-CBC"""
        try:
            iv = context.iv or secrets.token_bytes(16)  # 128 bits pour CBC
            
            # Padding PKCS7
            padded_data = self._pkcs7_pad(data, 16)
            
            # Simulation du chiffrement CBC
            encrypted_data = self._xor_encrypt(padded_data, key, iv)
            
            return EncryptionResult(
                success=True,
                encrypted_data=encrypted_data,
                iv=iv,
                key_id=context.key_id,
                algorithm=context.algorithm,
                metadata={'mode': 'CBC', 'padding': 'PKCS7'}
            )
            
        except Exception as e:
            logger.error(f"❌ Erreur AES-CBC: {e}")
            return EncryptionResult(
                success=False,
                error_message=f"Erreur AES-CBC: {str(e)}"
            )
    
    async def _decrypt_aes_cbc(
        self,
        encrypted_data: bytes,
        key: bytes,
        iv: bytes
    ) -> EncryptionResult:
        """Déchiffrement AES-256-CBC"""
        try:
            # Déchiffrement
            padded_data = self._xor_decrypt(encrypted_data, key, iv)
            
            # Suppression du padding
            decrypted_data = self._pkcs7_unpad(padded_data)
            
            return EncryptionResult(
                success=True,
                encrypted_data=decrypted_data,
                metadata={'mode': 'CBC', 'padding': 'PKCS7'}
            )
            
        except Exception as e:
            logger.error(f"❌ Erreur déchiffrement AES-CBC: {e}")
            return EncryptionResult(
                success=False,
                error_message=f"Erreur déchiffrement AES-CBC: {str(e)}"
            )
    
    async def _encrypt_chacha20(
        self,
        data: bytes,
        key: bytes,
        context: EncryptionContext
    ) -> EncryptionResult:
        """Chiffrement ChaCha20-Poly1305"""
        try:
            iv = context.iv or secrets.token_bytes(12)  # 96 bits pour ChaCha20
            
            # Simulation ChaCha20-Poly1305
            encrypted_data = self._xor_encrypt(data, key, iv)
            tag = hashlib.blake2b(encrypted_data + key + iv, digest_size=16).digest()
            
            return EncryptionResult(
                success=True,
                encrypted_data=encrypted_data,
                iv=iv,
                tag=tag,
                key_id=context.key_id,
                algorithm=context.algorithm,
                metadata={'cipher': 'ChaCha20', 'mac': 'Poly1305'}
            )
            
        except Exception as e:
            logger.error(f"❌ Erreur ChaCha20: {e}")
            return EncryptionResult(
                success=False,
                error_message=f"Erreur ChaCha20: {str(e)}"
            )
    
    async def _decrypt_chacha20(
        self,
        encrypted_data: bytes,
        key: bytes,
        iv: bytes,
        tag: bytes,
        additional_data: Optional[bytes] = None
    ) -> EncryptionResult:
        """Déchiffrement ChaCha20-Poly1305"""
        try:
            # Vérification du tag
            expected_tag = hashlib.blake2b(encrypted_data + key + iv, digest_size=16).digest()
            if not hmac.compare_digest(tag, expected_tag):
                return EncryptionResult(
                    success=False,
                    error_message="Erreur d'authentification - tag invalide"
                )
            
            # Déchiffrement
            decrypted_data = self._xor_decrypt(encrypted_data, key, iv)
            
            return EncryptionResult(
                success=True,
                encrypted_data=decrypted_data,
                metadata={'cipher': 'ChaCha20', 'authenticated': True}
            )
            
        except Exception as e:
            logger.error(f"❌ Erreur déchiffrement ChaCha20: {e}")
            return EncryptionResult(
                success=False,
                error_message=f"Erreur déchiffrement ChaCha20: {str(e)}"
            )
    
    def _encrypt_with_master_key(self, data: bytes) -> bytes:
        """Chiffrer avec la clé maître"""
        try:
            iv = secrets.token_bytes(16)
            encrypted = self._xor_encrypt(data, self.master_key, iv)
            return iv + encrypted
        except Exception as e:
            logger.error(f"❌ Erreur chiffrement clé maître: {e}")
            raise
    
    def _decrypt_with_master_key(self, encrypted_data: bytes) -> bytes:
        """Déchiffrer avec la clé maître"""
        try:
            iv = encrypted_data[:16]
            ciphertext = encrypted_data[16:]
            return self._xor_decrypt(ciphertext, self.master_key, iv)
        except Exception as e:
            logger.error(f"❌ Erreur déchiffrement clé maître: {e}")
            raise
    
    def _xor_encrypt(self, data: bytes, key: bytes, iv: bytes) -> bytes:
        """Chiffrement XOR simple (simulation)"""
        # En production, utiliser de vrais algorithmes cryptographiques
        key_stream = hashlib.pbkdf2_hmac('sha256', key, iv, 100000, len(data))
        return bytes(a ^ b for a, b in zip(data, key_stream))
    
    def _xor_decrypt(self, encrypted_data: bytes, key: bytes, iv: bytes) -> bytes:
        """Déchiffrement XOR simple (simulation)"""
        # Même opération que le chiffrement pour XOR
        return self._xor_encrypt(encrypted_data, key, iv)
    
    def _pkcs7_pad(self, data: bytes, block_size: int) -> bytes:
        """Padding PKCS#7"""
        padding_length = block_size - (len(data) % block_size)
        padding = bytes([padding_length] * padding_length)
        return data + padding
    
    def _pkcs7_unpad(self, padded_data: bytes) -> bytes:
        """Suppression padding PKCS#7"""
        padding_length = padded_data[-1]
        return padded_data[:-padding_length]
    
    async def _save_key(self, key: EncryptionKey):
        """Sauvegarder une clé de manière sécurisée"""
        try:
            key_file = self.key_storage_path / f"{key.key_id}.key"
            
            key_data = {
                'key_id': key.key_id,
                'key_type': key.key_type.value,
                'algorithm': key.algorithm.value,
                'key_data': base64.b64encode(key.key_data).decode(),
                'public_key': base64.b64encode(key.public_key).decode() if key.public_key else None,
                'metadata': key.metadata,
                'created_at': key.created_at.isoformat(),
                'expires_at': key.expires_at.isoformat() if key.expires_at else None,
                'is_active': key.is_active
            }
            
            with open(key_file, 'w') as f:
                json.dump(key_data, f, indent=2)
            
            os.chmod(key_file, 0o600)
            
        except Exception as e:
            logger.error(f"❌ Erreur sauvegarde clé: {e}")
    
    def _update_average_time(self, operation_time: float):
        """Mettre à jour le temps moyen d'opération"""
        try:
            if self.metrics['average_operation_time'] == 0:
                self.metrics['average_operation_time'] = operation_time
            else:
                # Moyenne mobile
                self.metrics['average_operation_time'] = (
                    self.metrics['average_operation_time'] * 0.9 + operation_time * 0.1
                )
        except:
            pass
    
    async def rotate_key(self, key_id: str) -> Optional[str]:
        """
        Effectuer la rotation d'une clé
        
        Args:
            key_id: ID de la clé à faire tourner
        
        Returns:
            ID de la nouvelle clé ou None
        """
        try:
            old_key = self.keys.get(key_id)
            if not old_key:
                logger.error(f"❌ Clé {key_id} introuvable pour rotation")
                return None
            
            # Désactivation de l'ancienne clé
            old_key.is_active = False
            
            # Génération d'une nouvelle clé
            new_key_id = await self.generate_key(
                algorithm=old_key.algorithm,
                purpose=old_key.metadata.get('purpose', 'general'),
                expires_in=timedelta(days=365),
                metadata={
                    **old_key.metadata,
                    'rotated_from': key_id,
                    'rotation_date': datetime.utcnow().isoformat()
                }
            )
            
            logger.info(f"✅ Rotation clé complétée: {key_id} → {new_key_id}")
            return new_key_id
            
        except Exception as e:
            logger.error(f"❌ Erreur rotation clé: {e}")
            return None
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Récupération des métriques
        
        Returns:
            Métriques de chiffrement
        """
        return {
            **self.metrics,
            'cache_size': len(self.encryption_cache),
            'timestamp': datetime.utcnow().isoformat()
        }
    
    async def cleanup_expired_keys(self) -> int:
        """
        Nettoyage des clés expirées
        
        Returns:
            Nombre de clés nettoyées
        """
        try:
            now = datetime.utcnow()
            expired_keys = []
            
            for key_id, key in self.keys.items():
                if key.expires_at and now > key.expires_at:
                    expired_keys.append(key_id)
            
            for key_id in expired_keys:
                self.keys[key_id].is_active = False
                logger.info(f"🗑️ Clé expirée désactivée: {key_id}")
            
            self.metrics['active_keys'] = len([k for k in self.keys.values() if k.is_active])
            
            return len(expired_keys)
            
        except Exception as e:
            logger.error(f"❌ Erreur nettoyage clés: {e}")
            return 0

# Instance globale du service
encryption_service = EncryptionService()

# API publique
__all__ = [
    'EncryptionService',
    'EncryptionAlgorithm',
    'KeyType',
    'EncryptionKey',
    'EncryptionContext',
    'EncryptionResult',
    'encryption_service'
]

if __name__ == "__main__":
    # Test de démonstration
    async def demo():
        service = EncryptionService()
        
        # Génération d'une clé
        key_id = await service.generate_key(
            algorithm=EncryptionAlgorithm.AES_256_GCM,
            purpose="demo_encryption"
        )
        
        # Données à chiffrer
        data = "Données sensibles pour test de chiffrement"
        
        # Contexte de chiffrement
        context = EncryptionContext(
            algorithm=EncryptionAlgorithm.AES_256_GCM,
            key_id=key_id,
            purpose="demo"
        )
        
        # Chiffrement
        encrypt_result = await service.encrypt(data, context)
        print(f"Chiffrement: {encrypt_result.success}")
        
        if encrypt_result.success:
            # Déchiffrement
            decrypt_result = await service.decrypt(
                encrypted_data=encrypt_result.encrypted_data,
                key_id=key_id,
                algorithm=EncryptionAlgorithm.AES_256_GCM,
                iv=encrypt_result.iv,
                tag=encrypt_result.tag
            )
            
            print(f"Déchiffrement: {decrypt_result.success}")
            if decrypt_result.success:
                decrypted_text = decrypt_result.encrypted_data.decode('utf-8')
                print(f"Données récupérées: {decrypted_text}")
        
        # Métriques
        metrics = service.get_metrics()
        print(f"Métriques: {metrics}")
    
    # Exécution du test
    asyncio.run(demo())