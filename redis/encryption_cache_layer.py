#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🛡️ Encryption Cache Layer - Couche Chiffrement Cache Enterprise
==============================================================

Couche enterprise de chiffrement cache avec chiffrement multi-niveaux,
gestion avancée des clés et protection données sensibles.

**Rôles Experts:**
- **Sécurité**: Chiffrement avancé, gestion clés, protection données
- **Backend Senior**: Architecture chiffrement haute performance
- **DBA**: Optimisation stockage chiffré, indexation sécurisée
- **DevOps**: Monitoring sécurité, rotation clés automatique

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import time
import hashlib
import secrets
import base64
from typing import Dict, Any, Optional, List, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta, timezone
from cryptography.fernet import Fernet, MultiFernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
import json
import os
from collections import defaultdict, deque

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EncryptionLevel(Enum):
    """Niveaux de chiffrement"""
    NONE = "none"
    BASIC = "basic"  # Fernet simple
    STANDARD = "standard"  # Fernet avec rotation
    HIGH = "high"  # AES-256 + authentification
    CRITICAL = "critical"  # RSA + AES hybride

class KeyType(Enum):
    """Types de clés"""
    SYMMETRIC = "symmetric"
    ASYMMETRIC = "asymmetric"
    DERIVED = "derived"
    EPHEMERAL = "ephemeral"

@dataclass
class EncryptionKey:
    """Clé de chiffrement"""
    key_id: str
    key_type: KeyType
    algorithm: str
    key_data: bytes
    created_at: datetime
    expires_at: Optional[datetime] = None
    rotation_count: int = 0
    usage_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class EncryptionMetrics:
    """Métriques chiffrement"""
    key_id: str
    encryption_level: str
    data_size: int
    encrypted_size: int
    encryption_time_ms: float
    decryption_time_ms: float
    overhead_ratio: float

class EncryptionCacheLayer:
    """
    🛡️ Couche Chiffrement Cache Enterprise
    
    **Sécurité**: Chiffrement multi-niveaux et gestion clés avancée
    **Backend Senior**: Architecture chiffrement haute performance
    **DBA**: Stockage chiffré optimisé et indexation sécurisée
    **DevOps**: Monitoring automatisé et rotation clés
    """
    
    def __init__(self, redis_pool, config: Optional[Dict[str, Any]] = None):
        self.redis_pool = redis_pool
        self.config = config or self._get_default_config()
        
        # Gestion des clés
        self.encryption_keys: Dict[str, EncryptionKey] = {}
        self.current_key_id: Optional[str] = None
        self.key_hierarchy: Dict[str, List[str]] = {}  # Parent -> enfants
        
        # Chiffreurs initialisés
        self.fernet_cipher: Optional[Fernet] = None
        self.multi_fernet: Optional[MultiFernet] = None
        self.aes_keys: Dict[str, bytes] = {}
        
        # RSA pour chiffrement hybride
        self.rsa_private_key: Optional[rsa.RSAPrivateKey] = None
        self.rsa_public_key: Optional[rsa.RSAPublicKey] = None
        
        # Cache et métriques
        self.encryption_cache: Dict[str, bytes] = {}
        self.decryption_cache: Dict[str, bytes] = {}
        self.metrics_history: deque = deque(maxlen=5000)
        
        # Tâches background
        self.key_rotation_task: Optional[asyncio.Task] = None
        self.cleanup_task: Optional[asyncio.Task] = None
        
        # Initialisation
        asyncio.create_task(self._initialize_encryption())
        
        logger.info("🛡️ Encryption Cache Layer initialisé")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """**Sécurité**: Configuration sécurisée par défaut"""
        return {
            'default_encryption_level': EncryptionLevel.STANDARD.value,
            'key_rotation_interval': 86400,  # 24h
            'max_key_age_days': 30,
            'key_derivation_iterations': 100000,
            'enable_key_caching': True,
            'cache_encrypted_data': False,  # Sécurité
            'rsa_key_size': 2048,
            'aes_key_size': 32,  # AES-256
            'master_password': None,  # À définir en production
            'salt': b'ainflue_encryption_salt_2025',
            'enable_compression_before_encryption': True,
            'max_cache_size_mb': 100,
            'enable_audit_logging': True,
            'emergency_key_backup': True,
            'key_storage_backend': 'redis'  # redis, vault, hsm
        }
    
    async def _initialize_encryption(self):
        """**Sécurité**: Initialisation systèmes chiffrement"""
        
        try:
            # Initialisation clé maître
            await self._initialize_master_key()
            
            # Génération clés par défaut
            await self._generate_default_keys()
            
            # Initialisation chiffreurs
            await self._setup_ciphers()
            
            # Démarrage tâches background
            await self._start_background_tasks()
            
            logger.info("✅ Systèmes chiffrement initialisés")
            
        except Exception as e:
            logger.error(f"❌ Erreur initialisation chiffrement: {e}")
            raise
    
    async def _initialize_master_key(self):
        """**Sécurité**: Initialisation clé maître sécurisée"""
        
        master_password = self.config.get('master_password')
        if not master_password:
            # Génération mot de passe temporaire pour démo
            master_password = secrets.token_urlsafe(32)
            logger.warning("⚠️ Mot de passe maître généré automatiquement")
        
        # Dérivation clé maître
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.config['salt'],
            iterations=self.config['key_derivation_iterations']
        )
        
        master_key = base64.urlsafe_b64encode(
            kdf.derive(master_password.encode())
        )
        
        # Stockage clé maître
        master_key_obj = EncryptionKey(
            key_id="master",
            key_type=KeyType.DERIVED,
            algorithm="PBKDF2-SHA256",
            key_data=master_key,
            created_at=datetime.now(timezone.utc),
            metadata={'iterations': self.config['key_derivation_iterations']}
        )
        
        self.encryption_keys["master"] = master_key_obj
        self.fernet_cipher = Fernet(master_key)
    
    async def _generate_default_keys(self):
        """**Sécurité**: Génération clés par défaut**"""
        
        # Clé Fernet standard
        standard_key = Fernet.generate_key()
        await self._store_key(
            "standard",
            KeyType.SYMMETRIC,
            "Fernet",
            standard_key,
            expires_at=datetime.now(timezone.utc) + timedelta(days=30)
        )
        
        # Clé AES haute sécurité
        aes_key = os.urandom(32)  # AES-256
        await self._store_key(
            "aes_high",
            KeyType.SYMMETRIC,
            "AES-256-GCM",
            aes_key,
            expires_at=datetime.now(timezone.utc) + timedelta(days=7)
        )
        
        # Paire RSA pour chiffrement critique
        if self.config.get('rsa_key_size', 2048) >= 2048:
            await self._generate_rsa_keypair()
        
        # Clé par défaut
        self.current_key_id = "standard"
    
    async def _generate_rsa_keypair(self):
        """**Sécurité**: Génération paire clés RSA**"""
        
        try:
            # Génération clé privée
            self.rsa_private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=self.config['rsa_key_size'],
            )
            
            self.rsa_public_key = self.rsa_private_key.public_key()
            
            # Sérialisation pour stockage
            private_pem = self.rsa_private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
            
            public_pem = self.rsa_public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
            
            # Stockage clés
            await self._store_key(
                "rsa_private",
                KeyType.ASYMMETRIC,
                "RSA-2048",
                private_pem,
                expires_at=datetime.now(timezone.utc) + timedelta(days=365)
            )
            
            await self._store_key(
                "rsa_public",
                KeyType.ASYMMETRIC,
                "RSA-2048",
                public_pem,
                expires_at=datetime.now(timezone.utc) + timedelta(days=365)
            )
            
            logger.info("🔐 Paire clés RSA générée")
            
        except Exception as e:
            logger.error(f"❌ Erreur génération RSA: {e}")
    
    async def _store_key(
        self,
        key_id: str,
        key_type: KeyType,
        algorithm: str,
        key_data: bytes,
        expires_at: Optional[datetime] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """**DBA**: Stockage sécurisé clé chiffrement**"""
        
        encryption_key = EncryptionKey(
            key_id=key_id,
            key_type=key_type,
            algorithm=algorithm,
            key_data=key_data,
            created_at=datetime.now(timezone.utc),
            expires_at=expires_at,
            metadata=metadata or {}
        )
        
        self.encryption_keys[key_id] = encryption_key
        
        # Stockage persistant chiffré
        if self.config.get('key_storage_backend') == 'redis':
            await self._store_key_in_redis(encryption_key)
        
        logger.debug(f"🔑 Clé stockée: {key_id} ({algorithm})")
    
    async def _store_key_in_redis(self, encryption_key: EncryptionKey):
        """**DBA**: Stockage clé dans Redis**"""
        
        try:
            # Chiffrement clé avec clé maître
            if encryption_key.key_id != "master" and self.fernet_cipher:
                encrypted_key_data = self.fernet_cipher.encrypt(encryption_key.key_data)
            else:
                encrypted_key_data = encryption_key.key_data
            
            # Sérialisation métadonnées
            key_metadata = {
                'key_id': encryption_key.key_id,
                'key_type': encryption_key.key_type.value,
                'algorithm': encryption_key.algorithm,
                'created_at': encryption_key.created_at.isoformat(),
                'expires_at': encryption_key.expires_at.isoformat() if encryption_key.expires_at else None,
                'rotation_count': encryption_key.rotation_count,
                'usage_count': encryption_key.usage_count,
                'metadata': encryption_key.metadata
            }
            
            async with self.redis_pool.get_connection() as redis_conn:
                # Stockage clé chiffrée
                await redis_conn.hset(
                    f"encryption_key:{encryption_key.key_id}",
                    mapping={
                        'encrypted_data': base64.b64encode(encrypted_key_data).decode(),
                        'metadata': json.dumps(key_metadata)
                    }
                )
                
                # TTL si défini
                if encryption_key.expires_at:
                    ttl = int((encryption_key.expires_at - datetime.now(timezone.utc)).total_seconds())
                    await redis_conn.expire(f"encryption_key:{encryption_key.key_id}", ttl)
                
        except Exception as e:
            logger.error(f"❌ Erreur stockage clé Redis {encryption_key.key_id}: {e}")
    
    async def _setup_ciphers(self):
        """**Backend Senior**: Configuration chiffreurs**"""
        
        # Multi-Fernet pour rotation clés
        fernet_keys = []
        for key_id, key_obj in self.encryption_keys.items():
            if key_obj.algorithm == "Fernet":
                fernet_keys.append(Fernet(key_obj.key_data))
        
        if fernet_keys:
            self.multi_fernet = MultiFernet(fernet_keys)
        
        # Préparation clés AES
        for key_id, key_obj in self.encryption_keys.items():
            if "AES" in key_obj.algorithm:
                self.aes_keys[key_id] = key_obj.key_data
    
    async def encrypt_data(
        self,
        data: bytes,
        encryption_level: Optional[EncryptionLevel] = None,
        key_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Tuple[bytes, str, EncryptionMetrics]:
        """**Sécurité**: Chiffrement données avec niveau spécifié**"""
        
        start_time = time.time()
        
        encryption_level = encryption_level or EncryptionLevel(
            self.config.get('default_encryption_level', 'standard')
        )
        
        try:
            if encryption_level == EncryptionLevel.NONE:
                return data, "none", EncryptionMetrics(
                    key_id="none", encryption_level="none",
                    data_size=len(data), encrypted_size=len(data),
                    encryption_time_ms=0, decryption_time_ms=0,
                    overhead_ratio=1.0
                )
            
            # Sélection clé et méthode
            if encryption_level == EncryptionLevel.BASIC:
                encrypted_data, used_key_id = await self._encrypt_basic(data, key_id)
            elif encryption_level == EncryptionLevel.STANDARD:
                encrypted_data, used_key_id = await self._encrypt_standard(data, key_id)
            elif encryption_level == EncryptionLevel.HIGH:
                encrypted_data, used_key_id = await self._encrypt_high(data, key_id)
            elif encryption_level == EncryptionLevel.CRITICAL:
                encrypted_data, used_key_id = await self._encrypt_critical(data, key_id)
            else:
                raise ValueError(f"Niveau chiffrement non supporté: {encryption_level}")
            
            encryption_time = (time.time() - start_time) * 1000
            
            # Métriques
            metrics = EncryptionMetrics(
                key_id=used_key_id,
                encryption_level=encryption_level.value,
                data_size=len(data),
                encrypted_size=len(encrypted_data),
                encryption_time_ms=encryption_time,
                decryption_time_ms=0,  # Sera rempli au déchiffrement
                overhead_ratio=len(encrypted_data) / len(data)
            )
            
            # Mise à jour utilisation clé
            if used_key_id in self.encryption_keys:
                self.encryption_keys[used_key_id].usage_count += 1
            
            # Historique
            self.metrics_history.append({
                'timestamp': time.time(),
                'operation': 'encrypt',
                'level': encryption_level.value,
                'key_id': used_key_id,
                'data_size': len(data),
                'encrypted_size': len(encrypted_data),
                'time_ms': encryption_time,
                'overhead': metrics.overhead_ratio
            })
            
            logger.debug(f"🔐 Chiffré: {encryption_level.value} - {len(data)} -> {len(encrypted_data)} bytes")
            
            return encrypted_data, used_key_id, metrics
            
        except Exception as e:
            logger.error(f"❌ Erreur chiffrement {encryption_level.value}: {e}")
            raise
    
    async def decrypt_data(
        self,
        encrypted_data: bytes,
        key_id: str,
        encryption_level: Optional[EncryptionLevel] = None
    ) -> Tuple[bytes, EncryptionMetrics]:
        """**Sécurité**: Déchiffrement données**"""
        
        start_time = time.time()
        
        try:
            if key_id == "none":
                return encrypted_data, EncryptionMetrics(
                    key_id="none", encryption_level="none",
                    data_size=len(encrypted_data), encrypted_size=len(encrypted_data),
                    encryption_time_ms=0, decryption_time_ms=0,
                    overhead_ratio=1.0
                )
            
            # Déchiffrement selon niveau
            if encryption_level == EncryptionLevel.BASIC:
                decrypted_data = await self._decrypt_basic(encrypted_data, key_id)
            elif encryption_level == EncryptionLevel.STANDARD:
                decrypted_data = await self._decrypt_standard(encrypted_data, key_id)
            elif encryption_level == EncryptionLevel.HIGH:
                decrypted_data = await self._decrypt_high(encrypted_data, key_id)
            elif encryption_level == EncryptionLevel.CRITICAL:
                decrypted_data = await self._decrypt_critical(encrypted_data, key_id)
            else:
                # Auto-détection niveau
                decrypted_data = await self._decrypt_auto(encrypted_data, key_id)
            
            decryption_time = (time.time() - start_time) * 1000
            
            # Métriques
            metrics = EncryptionMetrics(
                key_id=key_id,
                encryption_level=encryption_level.value if encryption_level else "auto",
                data_size=len(decrypted_data),
                encrypted_size=len(encrypted_data),
                encryption_time_ms=0,  # N/A pour déchiffrement
                decryption_time_ms=decryption_time,
                overhead_ratio=len(encrypted_data) / len(decrypted_data)
            )
            
            # Historique
            self.metrics_history.append({
                'timestamp': time.time(),
                'operation': 'decrypt',
                'level': encryption_level.value if encryption_level else "auto",
                'key_id': key_id,
                'encrypted_size': len(encrypted_data),
                'data_size': len(decrypted_data),
                'time_ms': decryption_time,
                'overhead': metrics.overhead_ratio
            })
            
            logger.debug(f"🔓 Déchiffré: {key_id} - {len(encrypted_data)} -> {len(decrypted_data)} bytes")
            
            return decrypted_data, metrics
            
        except Exception as e:
            logger.error(f"❌ Erreur déchiffrement {key_id}: {e}")
            raise
    
    async def _encrypt_basic(self, data: bytes, key_id: Optional[str]) -> Tuple[bytes, str]:
        """**Sécurité**: Chiffrement basique Fernet**"""
        
        key_id = key_id or "master"
        
        if key_id not in self.encryption_keys:
            raise ValueError(f"Clé introuvable: {key_id}")
        
        key_obj = self.encryption_keys[key_id]
        if key_obj.algorithm != "Fernet":
            raise ValueError(f"Clé {key_id} incompatible avec chiffrement basique")
        
        fernet = Fernet(key_obj.key_data)
        encrypted = fernet.encrypt(data)
        
        return encrypted, key_id
    
    async def _encrypt_standard(self, data: bytes, key_id: Optional[str]) -> Tuple[bytes, str]:
        """**Sécurité**: Chiffrement standard avec rotation**"""
        
        if self.multi_fernet:
            encrypted = self.multi_fernet.encrypt(data)
            return encrypted, self.current_key_id or "standard"
        else:
            # Fallback basic
            return await self._encrypt_basic(data, key_id)
    
    async def _encrypt_high(self, data: bytes, key_id: Optional[str]) -> Tuple[bytes, str]:
        """**Sécurité**: Chiffrement AES-256-GCM haute sécurité**"""
        
        key_id = key_id or "aes_high"
        
        if key_id not in self.aes_keys:
            raise ValueError(f"Clé AES introuvable: {key_id}")
        
        # AES-256-GCM
        iv = os.urandom(12)  # 96-bit IV pour GCM
        cipher = Cipher(
            algorithms.AES(self.aes_keys[key_id]),
            modes.GCM(iv)
        )
        
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(data) + encryptor.finalize()
        
        # Format: IV(12) + Tag(16) + Ciphertext
        encrypted = iv + encryptor.tag + ciphertext
        
        return encrypted, key_id
    
    async def _encrypt_critical(self, data: bytes, key_id: Optional[str]) -> Tuple[bytes, str]:
        """**Sécurité**: Chiffrement hybride RSA+AES critique**"""
        
        if not self.rsa_public_key:
            raise ValueError("Clé RSA non disponible pour chiffrement critique")
        
        # Génération clé AES éphémère
        ephemeral_key = os.urandom(32)  # AES-256
        
        # Chiffrement données avec AES
        iv = os.urandom(12)
        cipher = Cipher(algorithms.AES(ephemeral_key), modes.GCM(iv))
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(data) + encryptor.finalize()
        
        # Chiffrement clé AES avec RSA
        encrypted_key = self.rsa_public_key.encrypt(
            ephemeral_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        
        # Format: EncryptedKey(256) + IV(12) + Tag(16) + Ciphertext
        encrypted = encrypted_key + iv + encryptor.tag + ciphertext
        
        return encrypted, "rsa_hybrid"
    
    async def _decrypt_basic(self, encrypted_data: bytes, key_id: str) -> bytes:
        """**Sécurité**: Déchiffrement basique**"""
        
        if key_id not in self.encryption_keys:
            raise ValueError(f"Clé introuvable: {key_id}")
        
        key_obj = self.encryption_keys[key_id]
        fernet = Fernet(key_obj.key_data)
        
        return fernet.decrypt(encrypted_data)
    
    async def _decrypt_standard(self, encrypted_data: bytes, key_id: str) -> bytes:
        """**Sécurité**: Déchiffrement standard avec rotation**"""
        
        if self.multi_fernet:
            return self.multi_fernet.decrypt(encrypted_data)
        else:
            return await self._decrypt_basic(encrypted_data, key_id)
    
    async def _decrypt_high(self, encrypted_data: bytes, key_id: str) -> bytes:
        """**Sécurité**: Déchiffrement AES-256-GCM**"""
        
        if key_id not in self.aes_keys:
            raise ValueError(f"Clé AES introuvable: {key_id}")
        
        # Extraction composants
        if len(encrypted_data) < 28:  # IV(12) + Tag(16)
            raise ValueError("Données chiffrées trop courtes")
        
        iv = encrypted_data[:12]
        tag = encrypted_data[12:28]
        ciphertext = encrypted_data[28:]
        
        # Déchiffrement
        cipher = Cipher(
            algorithms.AES(self.aes_keys[key_id]),
            modes.GCM(iv, tag)
        )
        
        decryptor = cipher.decryptor()
        return decryptor.update(ciphertext) + decryptor.finalize()
    
    async def _decrypt_critical(self, encrypted_data: bytes, key_id: str) -> bytes:
        """**Sécurité**: Déchiffrement hybride RSA+AES**"""
        
        if not self.rsa_private_key:
            raise ValueError("Clé RSA privée non disponible")
        
        # Extraction composants
        if len(encrypted_data) < 284:  # RSAKey(256) + IV(12) + Tag(16)
            raise ValueError("Données chiffrées critiques trop courtes")
        
        encrypted_key = encrypted_data[:256]  # RSA-2048 = 256 bytes
        iv = encrypted_data[256:268]
        tag = encrypted_data[268:284]
        ciphertext = encrypted_data[284:]
        
        # Déchiffrement clé AES
        aes_key = self.rsa_private_key.decrypt(
            encrypted_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        
        # Déchiffrement données
        cipher = Cipher(algorithms.AES(aes_key), modes.GCM(iv, tag))
        decryptor = cipher.decryptor()
        
        return decryptor.update(ciphertext) + decryptor.finalize()
    
    async def _decrypt_auto(self, encrypted_data: bytes, key_id: str) -> bytes:
        """**Backend Senior**: Déchiffrement automatique**"""
        
        # Tentative déchiffrement par niveau
        methods = [
            self._decrypt_standard,
            self._decrypt_high,
            self._decrypt_critical,
            self._decrypt_basic
        ]
        
        for method in methods:
            try:
                return await method(encrypted_data, key_id)
            except:
                continue
        
        raise ValueError("Impossible de déchiffrer avec aucune méthode")
    
    async def rotate_key(self, key_id: str) -> str:
        """**Sécurité**: Rotation clé avec nouvvel ID**"""
        
        if key_id not in self.encryption_keys:
            raise ValueError(f"Clé à faire tourner introuvable: {key_id}")
        
        old_key = self.encryption_keys[key_id]
        new_key_id = f"{key_id}_v{old_key.rotation_count + 1}"
        
        # Génération nouvelle clé
        if old_key.algorithm == "Fernet":
            new_key_data = Fernet.generate_key()
        elif "AES" in old_key.algorithm:
            new_key_data = os.urandom(32)
        else:
            raise ValueError(f"Rotation non supportée pour {old_key.algorithm}")
        
        # Stockage nouvelle clé
        await self._store_key(
            new_key_id,
            old_key.key_type,
            old_key.algorithm,
            new_key_data,
            expires_at=datetime.now(timezone.utc) + timedelta(days=30),
            metadata={'rotated_from': key_id}
        )
        
        # Mise à jour hiérarchie
        if key_id not in self.key_hierarchy:
            self.key_hierarchy[key_id] = []
        self.key_hierarchy[key_id].append(new_key_id)
        
        # Mise à jour clé courante
        if self.current_key_id == key_id:
            self.current_key_id = new_key_id
        
        # Re-configuration chiffreurs
        await self._setup_ciphers()
        
        logger.info(f"🔄 Clé rotée: {key_id} -> {new_key_id}")
        return new_key_id
    
    async def _start_background_tasks(self):
        """**DevOps**: Démarrage tâches background**"""
        
        # Rotation automatique clés
        if not self.key_rotation_task or self.key_rotation_task.done():
            self.key_rotation_task = asyncio.create_task(self._key_rotation_loop())
        
        # Nettoyage caches et clés expirées
        if not self.cleanup_task or self.cleanup_task.done():
            self.cleanup_task = asyncio.create_task(self._cleanup_loop())
        
        logger.info("🚀 Tâches background chiffrement démarrées")
    
    async def _key_rotation_loop(self):
        """**DevOps**: Boucle rotation automatique clés**"""
        
        while True:
            try:
                interval = self.config.get('key_rotation_interval', 86400)
                await asyncio.sleep(interval)
                
                # Rotation clés expirées ou anciennes
                await self._auto_rotate_keys()
                
            except Exception as e:
                logger.error(f"❌ Erreur rotation automatique: {e}")
                await asyncio.sleep(3600)  # Retry dans 1h
    
    async def _auto_rotate_keys(self):
        """**DevOps**: Rotation automatique clés anciennes**"""
        
        current_time = datetime.now(timezone.utc)
        max_age = timedelta(days=self.config.get('max_key_age_days', 30))
        
        keys_to_rotate = []
        
        for key_id, key_obj in self.encryption_keys.items():
            # Skip clés système
            if key_id in ["master", "rsa_private", "rsa_public"]:
                continue
            
            # Vérification âge
            age = current_time - key_obj.created_at
            if age > max_age:
                keys_to_rotate.append(key_id)
            
            # Vérification expiration proche
            elif (key_obj.expires_at and 
                  key_obj.expires_at - current_time < timedelta(days=1)):
                keys_to_rotate.append(key_id)
        
        # Rotation
        for key_id in keys_to_rotate:
            try:
                new_key_id = await self.rotate_key(key_id)
                logger.info(f"🔄 Rotation auto: {key_id} -> {new_key_id}")
            except Exception as e:
                logger.error(f"❌ Erreur rotation auto {key_id}: {e}")
    
    async def _cleanup_loop(self):
        """**DevOps**: Boucle nettoyage**"""
        
        while True:
            try:
                await asyncio.sleep(3600)  # Chaque heure
                await self._cleanup_expired_data()
            except Exception as e:
                logger.error(f"❌ Erreur nettoyage chiffrement: {e}")
    
    async def _cleanup_expired_data(self):
        """**DevOps**: Nettoyage données expirées**"""
        
        current_time = datetime.now(timezone.utc)
        
        # Nettoyage clés expirées
        expired_keys = [
            key_id for key_id, key_obj in self.encryption_keys.items()
            if (key_obj.expires_at and key_obj.expires_at <= current_time)
        ]
        
        for key_id in expired_keys:
            del self.encryption_keys[key_id]
            logger.info(f"🗑️ Clé expirée supprimée: {key_id}")
        
        # Nettoyage caches
        if len(self.encryption_cache) > 1000:
            self.encryption_cache.clear()
        if len(self.decryption_cache) > 1000:
            self.decryption_cache.clear()
    
    async def get_encryption_analytics(self) -> Dict[str, Any]:
        """**DevOps**: Analytics chiffrement détaillées**"""
        
        # Distribution opérations
        op_distribution = defaultdict(int)
        level_distribution = defaultdict(int)
        key_usage = defaultdict(int)
        
        for record in self.metrics_history:
            op_distribution[record['operation']] += 1
            level_distribution[record['level']] += 1
            key_usage[record['key_id']] += 1
        
        # Performance moyenne
        encrypt_times = [r['time_ms'] for r in self.metrics_history if r['operation'] == 'encrypt']
        decrypt_times = [r['time_ms'] for r in self.metrics_history if r['operation'] == 'decrypt']
        overheads = [r['overhead'] for r in self.metrics_history if 'overhead' in r]
        
        return {
            'global_metrics': {
                'total_operations': len(self.metrics_history),
                'total_keys': len(self.encryption_keys),
                'active_keys': len([k for k in self.encryption_keys.values() 
                                  if not k.expires_at or k.expires_at > datetime.now(timezone.utc)]),
                'avg_encryption_time_ms': np.mean(encrypt_times) if encrypt_times else 0,
                'avg_decryption_time_ms': np.mean(decrypt_times) if decrypt_times else 0,
                'avg_overhead_ratio': np.mean(overheads) if overheads else 0
            },
            'operation_distribution': dict(op_distribution),
            'level_distribution': dict(level_distribution),
            'key_usage': dict(key_usage),
            'key_inventory': {
                key_id: {
                    'algorithm': key_obj.algorithm,
                    'key_type': key_obj.key_type.value,
                    'created_at': key_obj.created_at.isoformat(),
                    'expires_at': key_obj.expires_at.isoformat() if key_obj.expires_at else None,
                    'usage_count': key_obj.usage_count,
                    'rotation_count': key_obj.rotation_count
                }
                for key_id, key_obj in self.encryption_keys.items()
            },
            'recent_operations': list(self.metrics_history)[-20:],
            'configuration': {
                'default_level': self.config.get('default_encryption_level'),
                'key_rotation_interval': self.config.get('key_rotation_interval'),
                'max_key_age_days': self.config.get('max_key_age_days'),
                'enable_compression': self.config.get('enable_compression_before_encryption'),
                'audit_logging': self.config.get('enable_audit_logging')
            }
        }

# Factory function
async def create_encryption_cache_layer(redis_pool, config: Optional[Dict[str, Any]] = None):
    """**Sécurité**: Factory création couche chiffrement cache**"""
    layer = EncryptionCacheLayer(redis_pool, config)
    return layer

if __name__ == "__main__":
    async def demo():
        """Démonstration Encryption Cache Layer"""
        
        # Configuration Redis simulée
        class MockRedisPool:
            def get_connection(self):
                from unittest.mock import AsyncMock
                mock = AsyncMock()
                mock.hset.return_value = True
                mock.expire.return_value = True
                return mock
        
        # Création layer
        layer = await create_encryption_cache_layer(MockRedisPool())
        
        # Test données sensibles
        sensitive_data = b"Donnees confidentielles utilisateur: email=alice@example.com, phone=+33123456789"
        
        print("🛡️ Test chiffrement multi-niveaux...")
        
        # Test chaque niveau
        levels = [
            EncryptionLevel.BASIC,
            EncryptionLevel.STANDARD,
            EncryptionLevel.HIGH,
            EncryptionLevel.CRITICAL
        ]
        
        for level in levels:
            print(f"\n--- {level.value.upper()} ---")
            
            try:
                # Chiffrement
                encrypted, key_id, enc_metrics = await layer.encrypt_data(
                    sensitive_data, level
                )
                
                print(f"Clé: {key_id}")
                print(f"Taille: {len(sensitive_data)} -> {len(encrypted)} bytes")
                print(f"Overhead: {enc_metrics.overhead_ratio:.2f}x")
                print(f"Temps: {enc_metrics.encryption_time_ms:.2f}ms")
                
                # Déchiffrement
                decrypted, dec_metrics = await layer.decrypt_data(
                    encrypted, key_id, level
                )
                
                print(f"Déchiffrement: {dec_metrics.decryption_time_ms:.2f}ms")
                print(f"Intégrité: {'✅' if decrypted == sensitive_data else '❌'}")
                
            except Exception as e:
                print(f"❌ Erreur {level.value}: {e}")
        
        # Analytics
        analytics = await layer.get_encryption_analytics()
        print(f"\n📊 Analytics: {analytics['global_metrics']}")
    
    asyncio.run(demo())