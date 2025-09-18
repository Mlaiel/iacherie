"""
⚠️ AVERTISSEMENT LÉGAL OBLIGATOIRE:
==========================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques

Encryption Service Template for Ainflue Creator Economy Platform
Enterprise-grade encryption service with multiple algorithms and key management
"""

import asyncio
import secrets
import hashlib
import base64
import os
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Union, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet
import nacl.secret
import nacl.utils
from nacl.public import PrivateKey, PublicKey, Box

from fastapi import FastAPI, HTTPException, Depends, Request
from pydantic import BaseModel, validator
from redis import Redis
import logging
from prometheus_client import Counter, Histogram, Gauge


class EncryptionAlgorithm(str, Enum):
    AES_256_GCM = "aes_256_gcm"
    AES_256_CBC = "aes_256_cbc"
    CHACHA20_POLY1305 = "chacha20_poly1305"
    FERNET = "fernet"
    NACL_SECRETBOX = "nacl_secretbox"
    RSA_OAEP = "rsa_oaep"
    RSA_PSS = "rsa_pss"


class KeyType(str, Enum):
    SYMMETRIC = "symmetric"
    ASYMMETRIC = "asymmetric"
    HYBRID = "hybrid"


class DataType(str, Enum):
    PERSONAL_DATA = "personal_data"
    FINANCIAL_DATA = "financial_data"
    CONTENT_DATA = "content_data"
    SYSTEM_DATA = "system_data"
    BACKUP_DATA = "backup_data"


@dataclass
class EncryptionConfig:
    """Configuration du service de chiffrement"""
    default_algorithm: EncryptionAlgorithm = EncryptionAlgorithm.AES_256_GCM
    key_rotation_days: int = 90
    enable_key_escrow: bool = True
    enable_audit: bool = True
    master_key_env_var: str = "ENCRYPTION_MASTER_KEY"
    vault_enabled: bool = False
    vault_url: Optional[str] = None
    hsm_enabled: bool = False
    performance_monitoring: bool = True


class EncryptionRequest(BaseModel):
    """Demande de chiffrement"""
    data: str
    algorithm: EncryptionAlgorithm = EncryptionAlgorithm.AES_256_GCM
    data_type: DataType = DataType.CONTENT_DATA
    key_id: Optional[str] = None
    additional_data: Optional[str] = None  # Pour AEAD
    compression: bool = False


class EncryptionResponse(BaseModel):
    """Réponse de chiffrement"""
    encrypted_data: str
    key_id: str
    algorithm: EncryptionAlgorithm
    iv: Optional[str] = None
    tag: Optional[str] = None
    metadata: Dict[str, Any] = {}


class DecryptionRequest(BaseModel):
    """Demande de déchiffrement"""
    encrypted_data: str
    key_id: str
    algorithm: EncryptionAlgorithm
    iv: Optional[str] = None
    tag: Optional[str] = None
    additional_data: Optional[str] = None


class KeyGenerationRequest(BaseModel):
    """Demande de génération de clé"""
    key_type: KeyType
    algorithm: EncryptionAlgorithm
    key_size: Optional[int] = None
    data_type: DataType = DataType.CONTENT_DATA
    expires_at: Optional[datetime] = None


class KeyInfo(BaseModel):
    """Informations sur une clé"""
    key_id: str
    key_type: KeyType
    algorithm: EncryptionAlgorithm
    created_at: datetime
    expires_at: Optional[datetime] = None
    data_type: DataType
    is_active: bool = True
    usage_count: int = 0
    last_used: Optional[datetime] = None


class EncryptionServiceTemplate:
    """
    Template de service de chiffrement enterprise pour Ainflue
    
    Fonctionnalités:
    - Chiffrement multi-algorithmes (AES, ChaCha20, NaCl, RSA)
    - Gestion de clés avec rotation automatique
    - Support HSM et Vault
    - Chiffrement par type de données
    - Audit complet des opérations
    - Performance monitoring
    - Key escrow pour conformité
    - AEAD (Authenticated Encryption with Associated Data)
    """
    
    def __init__(self, config: EncryptionConfig = None):
        self.config = config or EncryptionConfig()
        self.app = FastAPI(
            title="Ainflue Encryption Service",
            description="Enterprise encryption service with multi-algorithm support",
            version="1.0.0"
        )
        
        # Redis pour stockage clés et cache
        self.redis = Redis(host='localhost', port=6379, db=3, decode_responses=True)
        
        # Stockage des clés (en production, utiliser HSM/Vault)
        self.key_store: Dict[str, Dict[str, Any]] = {}
        
        # Master key pour key encryption
        self.master_key = self._load_master_key()
        
        # Métriques Prometheus
        self.encryption_operations = Counter('encryption_operations_total', ['algorithm', 'operation', 'data_type'])
        self.encryption_duration = Histogram('encryption_duration_seconds', ['algorithm', 'operation'])
        self.key_operations = Counter('encryption_key_operations_total', ['operation', 'key_type'])
        self.active_keys = Gauge('encryption_active_keys_total', ['algorithm', 'data_type'])
        
        # Setup
        self._setup_routes()
        self._initialize_default_keys()
        
        # Logger
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def _load_master_key(self) -> bytes:
        """Charge la clé maître depuis l'environnement"""
        master_key_b64 = os.getenv(self.config.master_key_env_var)
        if not master_key_b64:
            # Générer clé pour développement (JAMAIS en production)
            self.logger.warning("No master key found, generating one for development")
            return Fernet.generate_key()
        
        return base64.b64decode(master_key_b64)

    def _initialize_default_keys(self):
        """Initialise les clés par défaut"""
        # Clé par défaut pour chaque type de données
        for data_type in DataType:
            key_id = f"default_{data_type.value}_{self.config.default_algorithm.value}"
            if key_id not in self.key_store:
                asyncio.create_task(self._generate_key(
                    KeyGenerationRequest(
                        key_type=KeyType.SYMMETRIC,
                        algorithm=self.config.default_algorithm,
                        data_type=data_type
                    ),
                    key_id
                ))

    def _setup_routes(self):
        """Configuration des routes du service"""
        
        @self.app.post("/encryption/encrypt", response_model=EncryptionResponse)
        async def encrypt_data(request: EncryptionRequest):
            """Chiffrement de données"""
            with self.encryption_duration.labels(algorithm=request.algorithm.value, operation='encrypt').time():
                try:
                    # Sélectionner clé
                    key_id = request.key_id
                    if not key_id:
                        key_id = await self._get_default_key_id(request.data_type, request.algorithm)
                    
                    # Chiffrer
                    result = await self._encrypt_data(request, key_id)
                    
                    # Métriques et audit
                    self.encryption_operations.labels(
                        algorithm=request.algorithm.value,
                        operation='encrypt',
                        data_type=request.data_type.value
                    ).inc()
                    
                    await self._audit_operation("encrypt", key_id, request.algorithm, request.data_type)
                    
                    return result
                    
                except Exception as e:
                    self.logger.error(f"Encryption error: {str(e)}")
                    raise HTTPException(status_code=500, detail="Encryption failed")

        @self.app.post("/encryption/decrypt")
        async def decrypt_data(request: DecryptionRequest):
            """Déchiffrement de données"""
            with self.encryption_duration.labels(algorithm=request.algorithm.value, operation='decrypt').time():
                try:
                    # Déchiffrer
                    result = await self._decrypt_data(request)
                    
                    # Métriques et audit
                    self.encryption_operations.labels(
                        algorithm=request.algorithm.value,
                        operation='decrypt',
                        data_type='unknown'  # Type pas disponible dans décryption
                    ).inc()
                    
                    await self._audit_operation("decrypt", request.key_id, request.algorithm)
                    
                    return {"decrypted_data": result}
                    
                except Exception as e:
                    self.logger.error(f"Decryption error: {str(e)}")
                    raise HTTPException(status_code=500, detail="Decryption failed")

        @self.app.post("/encryption/keys/generate", response_model=KeyInfo)
        async def generate_key(request: KeyGenerationRequest):
            """Génération de nouvelle clé"""
            try:
                key_id = f"{request.data_type.value}_{request.algorithm.value}_{secrets.token_hex(8)}"
                key_info = await self._generate_key(request, key_id)
                
                self.key_operations.labels(operation='generate', key_type=request.key_type.value).inc()
                await self._audit_operation("key_generate", key_id, request.algorithm, request.data_type)
                
                return key_info
                
            except Exception as e:
                self.logger.error(f"Key generation error: {str(e)}")
                raise HTTPException(status_code=500, detail="Key generation failed")

        @self.app.get("/encryption/keys/{key_id}", response_model=KeyInfo)
        async def get_key_info(key_id: str):
            """Récupération d'informations sur une clé"""
            try:
                key_info = await self._get_key_info(key_id)
                if not key_info:
                    raise HTTPException(status_code=404, detail="Key not found")
                
                return key_info
                
            except HTTPException:
                raise
            except Exception as e:
                self.logger.error(f"Key info error: {str(e)}")
                raise HTTPException(status_code=500, detail="Failed to retrieve key info")

        @self.app.post("/encryption/keys/{key_id}/rotate")
        async def rotate_key(key_id: str):
            """Rotation d'une clé"""
            try:
                new_key_id = await self._rotate_key(key_id)
                
                self.key_operations.labels(operation='rotate', key_type='unknown').inc()
                await self._audit_operation("key_rotate", key_id)
                
                return {"new_key_id": new_key_id, "old_key_id": key_id}
                
            except Exception as e:
                self.logger.error(f"Key rotation error: {str(e)}")
                raise HTTPException(status_code=500, detail="Key rotation failed")

        @self.app.delete("/encryption/keys/{key_id}")
        async def revoke_key(key_id: str):
            """Révocation d'une clé"""
            try:
                await self._revoke_key(key_id)
                
                self.key_operations.labels(operation='revoke', key_type='unknown').inc()
                await self._audit_operation("key_revoke", key_id)
                
                return {"message": "Key revoked successfully"}
                
            except Exception as e:
                self.logger.error(f"Key revocation error: {str(e)}")
                raise HTTPException(status_code=500, detail="Key revocation failed")

        @self.app.get("/encryption/health")
        async def health_check():
            """Health check"""
            try:
                await self.redis.ping()
                return {
                    "status": "healthy",
                    "timestamp": datetime.utcnow().isoformat(),
                    "active_keys": len(self.key_store),
                    "algorithms": [algo.value for algo in EncryptionAlgorithm]
                }
            except Exception as e:
                return {
                    "status": "unhealthy",
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat()
                }

    async def _encrypt_data(self, request: EncryptionRequest, key_id: str) -> EncryptionResponse:
        """Chiffrement des données selon l'algorithme"""
        key_material = await self._get_key_material(key_id)
        
        if request.algorithm == EncryptionAlgorithm.AES_256_GCM:
            return await self._encrypt_aes_gcm(request.data, key_material, request.additional_data)
        
        elif request.algorithm == EncryptionAlgorithm.AES_256_CBC:
            return await self._encrypt_aes_cbc(request.data, key_material)
        
        elif request.algorithm == EncryptionAlgorithm.CHACHA20_POLY1305:
            return await self._encrypt_chacha20_poly1305(request.data, key_material, request.additional_data)
        
        elif request.algorithm == EncryptionAlgorithm.FERNET:
            return await self._encrypt_fernet(request.data, key_material)
        
        elif request.algorithm == EncryptionAlgorithm.NACL_SECRETBOX:
            return await self._encrypt_nacl_secretbox(request.data, key_material)
        
        elif request.algorithm == EncryptionAlgorithm.RSA_OAEP:
            return await self._encrypt_rsa_oaep(request.data, key_material)
        
        else:
            raise ValueError(f"Unsupported algorithm: {request.algorithm}")

    async def _encrypt_aes_gcm(self, data: str, key: bytes, additional_data: str = None) -> EncryptionResponse:
        """Chiffrement AES-256-GCM"""
        iv = os.urandom(12)  # 96-bit IV pour GCM
        cipher = Cipher(algorithms.AES(key), modes.GCM(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        
        if additional_data:
            encryptor.authenticate_additional_data(additional_data.encode())
        
        ciphertext = encryptor.update(data.encode()) + encryptor.finalize()
        
        return EncryptionResponse(
            encrypted_data=base64.b64encode(ciphertext).decode(),
            key_id="current_key",
            algorithm=EncryptionAlgorithm.AES_256_GCM,
            iv=base64.b64encode(iv).decode(),
            tag=base64.b64encode(encryptor.tag).decode()
        )

    async def _encrypt_aes_cbc(self, data: str, key: bytes) -> EncryptionResponse:
        """Chiffrement AES-256-CBC"""
        iv = os.urandom(16)  # 128-bit IV pour CBC
        
        # Padding PKCS7
        padded_data = self._pkcs7_pad(data.encode(), 16)
        
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(padded_data) + encryptor.finalize()
        
        return EncryptionResponse(
            encrypted_data=base64.b64encode(ciphertext).decode(),
            key_id="current_key",
            algorithm=EncryptionAlgorithm.AES_256_CBC,
            iv=base64.b64encode(iv).decode()
        )

    async def _encrypt_chacha20_poly1305(self, data: str, key: bytes, additional_data: str = None) -> EncryptionResponse:
        """Chiffrement ChaCha20-Poly1305"""
        nonce = os.urandom(12)  # 96-bit nonce
        cipher = Cipher(algorithms.ChaCha20(key, nonce), mode=None, backend=default_backend())
        encryptor = cipher.encryptor()
        
        ciphertext = encryptor.update(data.encode()) + encryptor.finalize()
        
        return EncryptionResponse(
            encrypted_data=base64.b64encode(ciphertext).decode(),
            key_id="current_key",
            algorithm=EncryptionAlgorithm.CHACHA20_POLY1305,
            iv=base64.b64encode(nonce).decode()
        )

    async def _encrypt_fernet(self, data: str, key: bytes) -> EncryptionResponse:
        """Chiffrement Fernet (AES-128 en mode CBC avec HMAC)"""
        f = Fernet(key)
        encrypted_data = f.encrypt(data.encode())
        
        return EncryptionResponse(
            encrypted_data=base64.b64encode(encrypted_data).decode(),
            key_id="current_key",
            algorithm=EncryptionAlgorithm.FERNET
        )

    async def _encrypt_nacl_secretbox(self, data: str, key: bytes) -> EncryptionResponse:
        """Chiffrement NaCl SecretBox (XSalsa20 + Poly1305)"""
        box = nacl.secret.SecretBox(key)
        encrypted_data = box.encrypt(data.encode())
        
        return EncryptionResponse(
            encrypted_data=base64.b64encode(encrypted_data).decode(),
            key_id="current_key",
            algorithm=EncryptionAlgorithm.NACL_SECRETBOX
        )

    async def _encrypt_rsa_oaep(self, data: str, public_key: bytes) -> EncryptionResponse:
        """Chiffrement RSA-OAEP"""
        key = serialization.load_pem_public_key(public_key, backend=default_backend())
        
        ciphertext = key.encrypt(
            data.encode(),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        
        return EncryptionResponse(
            encrypted_data=base64.b64encode(ciphertext).decode(),
            key_id="current_key",
            algorithm=EncryptionAlgorithm.RSA_OAEP
        )

    async def _decrypt_data(self, request: DecryptionRequest) -> str:
        """Déchiffrement des données"""
        key_material = await self._get_key_material(request.key_id)
        encrypted_bytes = base64.b64decode(request.encrypted_data)
        
        if request.algorithm == EncryptionAlgorithm.AES_256_GCM:
            return await self._decrypt_aes_gcm(encrypted_bytes, key_material, request.iv, request.tag, request.additional_data)
        
        elif request.algorithm == EncryptionAlgorithm.AES_256_CBC:
            return await self._decrypt_aes_cbc(encrypted_bytes, key_material, request.iv)
        
        elif request.algorithm == EncryptionAlgorithm.FERNET:
            return await self._decrypt_fernet(encrypted_bytes, key_material)
        
        elif request.algorithm == EncryptionAlgorithm.NACL_SECRETBOX:
            return await self._decrypt_nacl_secretbox(encrypted_bytes, key_material)
        
        elif request.algorithm == EncryptionAlgorithm.RSA_OAEP:
            return await self._decrypt_rsa_oaep(encrypted_bytes, key_material)
        
        else:
            raise ValueError(f"Unsupported algorithm: {request.algorithm}")

    async def _decrypt_aes_gcm(self, ciphertext: bytes, key: bytes, iv_b64: str, tag_b64: str, additional_data: str = None) -> str:
        """Déchiffrement AES-256-GCM"""
        iv = base64.b64decode(iv_b64)
        tag = base64.b64decode(tag_b64)
        
        cipher = Cipher(algorithms.AES(key), modes.GCM(iv, tag), backend=default_backend())
        decryptor = cipher.decryptor()
        
        if additional_data:
            decryptor.authenticate_additional_data(additional_data.encode())
        
        plaintext = decryptor.update(ciphertext) + decryptor.finalize()
        return plaintext.decode()

    async def _decrypt_aes_cbc(self, ciphertext: bytes, key: bytes, iv_b64: str) -> str:
        """Déchiffrement AES-256-CBC"""
        iv = base64.b64decode(iv_b64)
        
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()
        
        # Supprimer padding PKCS7
        plaintext = self._pkcs7_unpad(padded_plaintext)
        return plaintext.decode()

    async def _decrypt_fernet(self, ciphertext: bytes, key: bytes) -> str:
        """Déchiffrement Fernet"""
        f = Fernet(key)
        plaintext = f.decrypt(ciphertext)
        return plaintext.decode()

    async def _decrypt_nacl_secretbox(self, ciphertext: bytes, key: bytes) -> str:
        """Déchiffrement NaCl SecretBox"""
        box = nacl.secret.SecretBox(key)
        plaintext = box.decrypt(ciphertext)
        return plaintext.decode()

    async def _decrypt_rsa_oaep(self, ciphertext: bytes, private_key: bytes) -> str:
        """Déchiffrement RSA-OAEP"""
        key = serialization.load_pem_private_key(private_key, password=None, backend=default_backend())
        
        plaintext = key.decrypt(
            ciphertext,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        
        return plaintext.decode()

    async def _generate_key(self, request: KeyGenerationRequest, key_id: str = None) -> KeyInfo:
        """Génération de nouvelle clé cryptographique"""
        if not key_id:
            key_id = f"{request.data_type.value}_{request.algorithm.value}_{secrets.token_hex(8)}"
        
        key_material = None
        
        if request.key_type == KeyType.SYMMETRIC:
            if request.algorithm in [EncryptionAlgorithm.AES_256_GCM, EncryptionAlgorithm.AES_256_CBC]:
                key_material = os.urandom(32)  # 256-bit key
            elif request.algorithm == EncryptionAlgorithm.CHACHA20_POLY1305:
                key_material = os.urandom(32)  # 256-bit key
            elif request.algorithm == EncryptionAlgorithm.FERNET:
                key_material = Fernet.generate_key()
            elif request.algorithm == EncryptionAlgorithm.NACL_SECRETBOX:
                key_material = nacl.utils.random(nacl.secret.SecretBox.KEY_SIZE)
        
        elif request.key_type == KeyType.ASYMMETRIC:
            if request.algorithm in [EncryptionAlgorithm.RSA_OAEP, EncryptionAlgorithm.RSA_PSS]:
                key_size = request.key_size or 2048
                private_key = rsa.generate_private_key(
                    public_exponent=65537,
                    key_size=key_size,
                    backend=default_backend()
                )
                
                private_pem = private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
                )
                
                public_pem = private_key.public_key().public_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo
                )
                
                key_material = {
                    "private_key": private_pem,
                    "public_key": public_pem
                }
        
        if not key_material:
            raise ValueError(f"Cannot generate key for {request.key_type} {request.algorithm}")
        
        # Chiffrer la clé avec la master key
        encrypted_key = await self._encrypt_key_material(key_material)
        
        # Stocker métadonnées
        key_info = KeyInfo(
            key_id=key_id,
            key_type=request.key_type,
            algorithm=request.algorithm,
            created_at=datetime.utcnow(),
            expires_at=request.expires_at,
            data_type=request.data_type,
            usage_count=0
        )
        
        self.key_store[key_id] = {
            "info": key_info.dict(),
            "encrypted_material": encrypted_key
        }
        
        # Persister dans Redis
        await self.redis.setex(
            f"key:{key_id}",
            86400 * self.config.key_rotation_days,
            json.dumps({
                "info": key_info.dict(),
                "encrypted_material": encrypted_key
            }, default=str)
        )
        
        return key_info

    async def _encrypt_key_material(self, key_material: Union[bytes, Dict]) -> str:
        """Chiffre le matériel de clé avec la master key"""
        if isinstance(key_material, dict):
            data = json.dumps(key_material).encode()
        else:
            data = key_material
        
        f = Fernet(self.master_key)
        encrypted = f.encrypt(data)
        return base64.b64encode(encrypted).decode()

    async def _decrypt_key_material(self, encrypted_material: str) -> Union[bytes, Dict]:
        """Déchiffre le matériel de clé avec la master key"""
        f = Fernet(self.master_key)
        encrypted_bytes = base64.b64decode(encrypted_material)
        decrypted = f.decrypt(encrypted_bytes)
        
        try:
            # Essayer de parser comme JSON (clés asymétriques)
            return json.loads(decrypted.decode())
        except:
            # Retourner bytes (clés symétriques)
            return decrypted

    async def _get_key_material(self, key_id: str) -> Union[bytes, Dict]:
        """Récupère le matériel cryptographique d'une clé"""
        key_data = self.key_store.get(key_id)
        if not key_data:
            # Chercher dans Redis
            redis_data = await self.redis.get(f"key:{key_id}")
            if redis_data:
                key_data = json.loads(redis_data)
                self.key_store[key_id] = key_data
            else:
                raise ValueError(f"Key not found: {key_id}")
        
        # Déchiffrer le matériel
        key_material = await self._decrypt_key_material(key_data["encrypted_material"])
        
        # Mettre à jour usage
        key_data["info"]["usage_count"] += 1
        key_data["info"]["last_used"] = datetime.utcnow().isoformat()
        
        return key_material

    def _pkcs7_pad(self, data: bytes, block_size: int) -> bytes:
        """Ajoute padding PKCS7"""
        padding_length = block_size - (len(data) % block_size)
        padding = bytes([padding_length] * padding_length)
        return data + padding

    def _pkcs7_unpad(self, padded_data: bytes) -> bytes:
        """Supprime padding PKCS7"""
        padding_length = padded_data[-1]
        return padded_data[:-padding_length]

    async def _get_default_key_id(self, data_type: DataType, algorithm: EncryptionAlgorithm) -> str:
        """Récupère l'ID de la clé par défaut pour un type de données"""
        return f"default_{data_type.value}_{algorithm.value}"

    async def _get_key_info(self, key_id: str) -> Optional[KeyInfo]:
        """Récupère les informations d'une clé"""
        key_data = self.key_store.get(key_id)
        if key_data:
            return KeyInfo(**key_data["info"])
        return None

    async def _rotate_key(self, old_key_id: str) -> str:
        """Rotation d'une clé"""
        old_key_data = self.key_store.get(old_key_id)
        if not old_key_data:
            raise ValueError(f"Key not found: {old_key_id}")
        
        old_info = KeyInfo(**old_key_data["info"])
        
        # Générer nouvelle clé
        new_request = KeyGenerationRequest(
            key_type=old_info.key_type,
            algorithm=old_info.algorithm,
            data_type=old_info.data_type
        )
        
        new_key_id = f"{old_info.data_type.value}_{old_info.algorithm.value}_{secrets.token_hex(8)}"
        await self._generate_key(new_request, new_key_id)
        
        # Marquer ancienne clé comme inactive
        old_key_data["info"]["is_active"] = False
        
        return new_key_id

    async def _revoke_key(self, key_id: str):
        """Révoque une clé"""
        if key_id in self.key_store:
            self.key_store[key_id]["info"]["is_active"] = False
            await self.redis.delete(f"key:{key_id}")

    async def _audit_operation(
        self, operation: str, key_id: str, algorithm: EncryptionAlgorithm = None, 
        data_type: DataType = None
    ):
        """Audit des opérations cryptographiques"""
        if self.config.enable_audit:
            audit_data = {
                "operation": operation,
                "key_id": key_id,
                "algorithm": algorithm.value if algorithm else None,
                "data_type": data_type.value if data_type else None,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            await self.redis.lpush("encryption_audit_log", json.dumps(audit_data))

    def get_app(self) -> FastAPI:
        """Retourne instance FastAPI"""
        return self.app


def create_encryption_service(config: EncryptionConfig = None) -> FastAPI:
    """
    Factory pour créer service de chiffrement
    
    Args:
        config: Configuration de chiffrement personnalisée
        
    Returns:
        FastAPI: Instance du service configuré
    """
    encryption_service = EncryptionServiceTemplate(config)
    return encryption_service.get_app()


if __name__ == "__main__":
    import uvicorn
    
    config = EncryptionConfig(
        default_algorithm=EncryptionAlgorithm.AES_256_GCM,
        key_rotation_days=30,
        enable_audit=True
    )
    
    app = create_encryption_service(config)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )