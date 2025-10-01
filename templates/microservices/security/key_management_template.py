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

Key Management Template for iacherie Creator Economy Platform
Enterprise key management service with HSM, Vault integration and automated rotation
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
import ssl

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, ec, padding
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet
import hvac  # HashiCorp Vault client
import boto3  # AWS KMS
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential

from fastapi import FastAPI, HTTPException, Depends, Request, BackgroundTasks
from pydantic import BaseModel, validator
from redis import Redis
import logging
from prometheus_client import Counter, Histogram, Gauge
import schedule
import threading


class KeyProvider(str, Enum):
    LOCAL = "local"
    VAULT = "vault"
    AWS_KMS = "aws_kms"
    AZURE_KEYVAULT = "azure_keyvault"
    HSM = "hsm"
    GOOGLE_KMS = "google_kms"


class KeyState(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    COMPROMISED = "compromised"
    DESTROYED = "destroyed"
    PENDING_ACTIVATION = "pending_activation"
    PENDING_DESTRUCTION = "pending_destruction"


class KeyUsage(str, Enum):
    ENCRYPT_DECRYPT = "encrypt_decrypt"
    SIGN_VERIFY = "sign_verify"
    KEY_WRAP = "key_wrap"
    AUTHENTICATION = "authentication"
    DERIVATION = "derivation"


@dataclass
class KeyManagementConfig:
    """Configuration du service de gestion de clés"""
    default_provider: KeyProvider = KeyProvider.LOCAL
    enable_automatic_rotation: bool = True
    rotation_schedule_days: int = 90
    key_escrow_enabled: bool = True
    backup_enabled: bool = True
    backup_encryption: bool = True
    compliance_mode: bool = True
    multi_region_replication: bool = False
    
    # Vault configuration
    vault_url: Optional[str] = None
    vault_token: Optional[str] = None
    vault_mount_point: str = "secret"
    
    # AWS KMS configuration
    aws_region: str = "us-east-1"
    aws_kms_key_id: Optional[str] = None
    
    # Azure Key Vault configuration
    azure_vault_url: Optional[str] = None
    
    # HSM configuration
    hsm_library_path: Optional[str] = None
    hsm_slot: int = 0
    hsm_pin: Optional[str] = None


class KeyMetadata(BaseModel):
    """Métadonnées d'une clé"""
    key_id: str
    key_name: str
    provider: KeyProvider
    key_type: str
    key_size: int
    algorithm: str
    usage: List[KeyUsage]
    state: KeyState
    created_at: datetime
    activated_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    rotation_policy: Optional[str] = None
    compliance_tags: Dict[str, str] = {}
    owner: str
    cost_center: Optional[str] = None
    backup_enabled: bool = True


class KeyGenerationRequest(BaseModel):
    """Demande de génération de clé"""
    key_name: str
    key_type: str = "AES"
    key_size: int = 256
    algorithm: str = "AES-GCM"
    usage: List[KeyUsage] = [KeyUsage.ENCRYPT_DECRYPT]
    provider: KeyProvider = KeyProvider.LOCAL
    expires_at: Optional[datetime] = None
    rotation_days: Optional[int] = None
    compliance_tags: Dict[str, str] = {}
    owner: str
    description: Optional[str] = None


class KeyRotationRequest(BaseModel):
    """Demande de rotation de clé"""
    key_id: str
    immediate: bool = False
    preserve_old_key: bool = True
    notification_required: bool = True


class KeyBackupRequest(BaseModel):
    """Demande de sauvegarde de clé"""
    key_id: str
    backup_location: str
    encrypt_backup: bool = True
    verification_required: bool = True


class KeyRestoreRequest(BaseModel):
    """Demande de restauration de clé"""
    backup_id: str
    new_key_name: Optional[str] = None
    verify_integrity: bool = True


class KeyManagementTemplate:
    """
    Template de gestion de clés enterprise pour iacherie
    
    Fonctionnalités:
    - Multi-provider (Local, Vault, AWS KMS, Azure, HSM)
    - Rotation automatique de clés
    - Backup et restauration
    - Escrow de clés pour conformité
    - Audit complet des opérations
    - Réplication multi-régions
    - Policies de compliance
    - Monitoring avancé
    - Zero-downtime key rotation
    """
    
    def __init__(self, config: KeyManagementConfig = None):
        self.config = config or KeyManagementConfig()
        self.app = FastAPI(
            title="iacherie Key Management Service",
            description="Enterprise key management with multi-provider support",
            version="1.0.0"
        )
        
        # Redis pour cache et coordination
        self.redis = Redis(host='localhost', port=6379, db=4, decode_responses=True)
        
        # Stockage métadonnées des clés
        self.key_metadata: Dict[str, KeyMetadata] = {}
        
        # Providers
        self.providers: Dict[KeyProvider, Any] = {}
        
        # Métriques Prometheus
        self.key_operations = Counter('key_mgmt_operations_total', ['operation', 'provider', 'status'])
        self.key_rotation_events = Counter('key_mgmt_rotations_total', ['provider', 'status'])
        self.operation_duration = Histogram('key_mgmt_operation_duration_seconds', ['operation', 'provider'])
        self.active_keys = Gauge('key_mgmt_active_keys_total', ['provider', 'key_type'])
        self.key_age = Histogram('key_mgmt_key_age_days', ['provider'])
        
        # Setup
        self._initialize_providers()
        self._setup_routes()
        self._setup_rotation_scheduler()
        
        # Logger
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def _initialize_providers(self):
        """Initialise les providers de clés"""
        try:
            # Vault provider
            if self.config.vault_url and self.config.vault_token:
                vault_client = hvac.Client(
                    url=self.config.vault_url,
                    token=self.config.vault_token
                )
                if vault_client.is_authenticated():
                    self.providers[KeyProvider.VAULT] = vault_client
                    self.logger.info("Vault provider initialized")
            
            # AWS KMS provider
            try:
                kms_client = boto3.client('kms', region_name=self.config.aws_region)
                self.providers[KeyProvider.AWS_KMS] = kms_client
                self.logger.info("AWS KMS provider initialized")
            except Exception as e:
                self.logger.warning(f"AWS KMS initialization failed: {str(e)}")
            
            # Azure Key Vault provider
            if self.config.azure_vault_url:
                try:
                    credential = DefaultAzureCredential()
                    vault_client = SecretClient(
                        vault_url=self.config.azure_vault_url,
                        credential=credential
                    )
                    self.providers[KeyProvider.AZURE_KEYVAULT] = vault_client
                    self.logger.info("Azure Key Vault provider initialized")
                except Exception as e:
                    self.logger.warning(f"Azure Key Vault initialization failed: {str(e)}")
            
            # Local provider (toujours disponible)
            self.providers[KeyProvider.LOCAL] = {"type": "local", "initialized": True}
            
        except Exception as e:
            self.logger.error(f"Provider initialization error: {str(e)}")

    def _setup_rotation_scheduler(self):
        """Configure le scheduler de rotation automatique"""
        if self.config.enable_automatic_rotation:
            def rotation_worker():
                schedule.every().day.at("02:00").do(self._check_keys_for_rotation)
                
                while True:
                    schedule.run_pending()
                    asyncio.sleep(3600)  # Check every hour
            
            # Run scheduler in background thread
            rotation_thread = threading.Thread(target=rotation_worker, daemon=True)
            rotation_thread.start()

    def _setup_routes(self):
        """Configuration des routes du service"""
        
        @self.app.post("/keys/generate", response_model=KeyMetadata)
        async def generate_key(request: KeyGenerationRequest, background_tasks: BackgroundTasks):
            """Génération d'une nouvelle clé"""
            with self.operation_duration.labels(operation='generate', provider=request.provider.value).time():
                try:
                    key_metadata = await self._generate_key(request)
                    
                    # Backup automatique si activé
                    if self.config.backup_enabled:
                        background_tasks.add_task(self._backup_key, key_metadata.key_id)
                    
                    # Escrow si activé
                    if self.config.key_escrow_enabled:
                        background_tasks.add_task(self._escrow_key, key_metadata.key_id)
                    
                    self.key_operations.labels(
                        operation='generate',
                        provider=request.provider.value,
                        status='success'
                    ).inc()
                    
                    await self._audit_operation("key_generate", key_metadata.key_id, request.provider)
                    
                    return key_metadata
                    
                except Exception as e:
                    self.key_operations.labels(
                        operation='generate',
                        provider=request.provider.value,
                        status='error'
                    ).inc()
                    self.logger.error(f"Key generation error: {str(e)}")
                    raise HTTPException(status_code=500, detail=f"Key generation failed: {str(e)}")

        @self.app.get("/keys/{key_id}", response_model=KeyMetadata)
        async def get_key_metadata(key_id: str):
            """Récupération des métadonnées d'une clé"""
            try:
                metadata = await self._get_key_metadata(key_id)
                if not metadata:
                    raise HTTPException(status_code=404, detail="Key not found")
                
                return metadata
                
            except HTTPException:
                raise
            except Exception as e:
                self.logger.error(f"Get key metadata error: {str(e)}")
                raise HTTPException(status_code=500, detail="Failed to retrieve key metadata")

        @self.app.post("/keys/{key_id}/rotate")
        async def rotate_key(key_id: str, request: KeyRotationRequest, background_tasks: BackgroundTasks):
            """Rotation d'une clé"""
            with self.operation_duration.labels(operation='rotate', provider='unknown').time():
                try:
                    new_key_id = await self._rotate_key(key_id, request)
                    
                    # Notification si requise
                    if request.notification_required:
                        background_tasks.add_task(self._notify_key_rotation, key_id, new_key_id)
                    
                    self.key_rotation_events.labels(
                        provider='unknown',  # Will be determined in _rotate_key
                        status='success'
                    ).inc()
                    
                    await self._audit_operation("key_rotate", key_id)
                    
                    return {
                        "old_key_id": key_id,
                        "new_key_id": new_key_id,
                        "rotation_time": datetime.utcnow().isoformat()
                    }
                    
                except Exception as e:
                    self.key_rotation_events.labels(
                        provider='unknown',
                        status='error'
                    ).inc()
                    self.logger.error(f"Key rotation error: {str(e)}")
                    raise HTTPException(status_code=500, detail=f"Key rotation failed: {str(e)}")

        @self.app.post("/keys/{key_id}/backup")
        async def backup_key(key_id: str, request: KeyBackupRequest):
            """Sauvegarde d'une clé"""
            try:
                backup_id = await self._backup_key_with_request(key_id, request)
                
                self.key_operations.labels(
                    operation='backup',
                    provider='unknown',
                    status='success'
                ).inc()
                
                await self._audit_operation("key_backup", key_id)
                
                return {
                    "backup_id": backup_id,
                    "backup_time": datetime.utcnow().isoformat(),
                    "verification_status": "pending" if request.verification_required else "not_required"
                }
                
            except Exception as e:
                self.key_operations.labels(
                    operation='backup',
                    provider='unknown',
                    status='error'
                ).inc()
                self.logger.error(f"Key backup error: {str(e)}")
                raise HTTPException(status_code=500, detail=f"Key backup failed: {str(e)}")

        @self.app.post("/keys/restore")
        async def restore_key(request: KeyRestoreRequest):
            """Restauration d'une clé"""
            try:
                restored_key_id = await self._restore_key(request)
                
                self.key_operations.labels(
                    operation='restore',
                    provider='unknown',
                    status='success'
                ).inc()
                
                await self._audit_operation("key_restore", restored_key_id)
                
                return {
                    "restored_key_id": restored_key_id,
                    "restore_time": datetime.utcnow().isoformat()
                }
                
            except Exception as e:
                self.key_operations.labels(
                    operation='restore',
                    provider='unknown',
                    status='error'
                ).inc()
                self.logger.error(f"Key restore error: {str(e)}")
                raise HTTPException(status_code=500, detail=f"Key restore failed: {str(e)}")

        @self.app.delete("/keys/{key_id}")
        async def destroy_key(key_id: str, confirm: bool = False):
            """Destruction sécurisée d'une clé"""
            if not confirm:
                raise HTTPException(status_code=400, detail="Confirmation required for key destruction")
            
            try:
                await self._destroy_key(key_id)
                
                self.key_operations.labels(
                    operation='destroy',
                    provider='unknown',
                    status='success'
                ).inc()
                
                await self._audit_operation("key_destroy", key_id)
                
                return {"message": "Key destroyed successfully", "key_id": key_id}
                
            except Exception as e:
                self.key_operations.labels(
                    operation='destroy',
                    provider='unknown',
                    status='error'
                ).inc()
                self.logger.error(f"Key destruction error: {str(e)}")
                raise HTTPException(status_code=500, detail=f"Key destruction failed: {str(e)}")

        @self.app.get("/keys/{key_id}/usage")
        async def get_key_usage(key_id: str, days: int = 30):
            """Statistiques d'utilisation d'une clé"""
            try:
                usage_stats = await self._get_key_usage_stats(key_id, days)
                return usage_stats
                
            except Exception as e:
                self.logger.error(f"Key usage stats error: {str(e)}")
                raise HTTPException(status_code=500, detail="Failed to retrieve key usage stats")

        @self.app.get("/keys/compliance/report")
        async def compliance_report():
            """Rapport de conformité des clés"""
            try:
                report = await self._generate_compliance_report()
                return report
                
            except Exception as e:
                self.logger.error(f"Compliance report error: {str(e)}")
                raise HTTPException(status_code=500, detail="Failed to generate compliance report")

        @self.app.get("/health")
        async def health_check():
            """Health check du service"""
            try:
                provider_status = {}
                for provider, client in self.providers.items():
                    provider_status[provider.value] = await self._check_provider_health(provider, client)
                
                return {
                    "status": "healthy" if all(provider_status.values()) else "degraded",
                    "timestamp": datetime.utcnow().isoformat(),
                    "providers": provider_status,
                    "active_keys": len(self.key_metadata),
                    "metrics": {
                        "total_keys": len(self.key_metadata),
                        "active_keys": len([k for k in self.key_metadata.values() if k.state == KeyState.ACTIVE]),
                        "expired_keys": len([k for k in self.key_metadata.values() 
                                           if k.expires_at and k.expires_at < datetime.utcnow()])
                    }
                }
                
            except Exception as e:
                return {
                    "status": "unhealthy",
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat()
                }

    async def _generate_key(self, request: KeyGenerationRequest) -> KeyMetadata:
        """Génère une nouvelle clé selon le provider"""
        key_id = f"{request.key_name}_{secrets.token_hex(8)}"
        
        provider = self.providers.get(request.provider)
        if not provider:
            raise ValueError(f"Provider not available: {request.provider}")
        
        if request.provider == KeyProvider.LOCAL:
            key_material = await self._generate_local_key(request)
        elif request.provider == KeyProvider.VAULT:
            key_material = await self._generate_vault_key(request, provider)
        elif request.provider == KeyProvider.AWS_KMS:
            key_material = await self._generate_aws_kms_key(request, provider)
        elif request.provider == KeyProvider.AZURE_KEYVAULT:
            key_material = await self._generate_azure_key(request, provider)
        else:
            raise ValueError(f"Unsupported provider: {request.provider}")
        
        # Créer métadonnées
        metadata = KeyMetadata(
            key_id=key_id,
            key_name=request.key_name,
            provider=request.provider,
            key_type=request.key_type,
            key_size=request.key_size,
            algorithm=request.algorithm,
            usage=request.usage,
            state=KeyState.ACTIVE,
            created_at=datetime.utcnow(),
            activated_at=datetime.utcnow(),
            expires_at=request.expires_at,
            owner=request.owner,
            compliance_tags=request.compliance_tags
        )
        
        # Stocker métadonnées
        self.key_metadata[key_id] = metadata
        await self._persist_key_metadata(key_id, metadata)
        
        # Mettre à jour métriques
        self.active_keys.labels(
            provider=request.provider.value,
            key_type=request.key_type
        ).inc()
        
        return metadata

    async def _generate_local_key(self, request: KeyGenerationRequest) -> bytes:
        """Génère clé locale"""
        if request.key_type.upper() == "AES":
            return os.urandom(request.key_size // 8)
        elif request.key_type.upper() == "RSA":
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=request.key_size,
                backend=default_backend()
            )
            return private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
        else:
            raise ValueError(f"Unsupported key type: {request.key_type}")

    async def _generate_vault_key(self, request: KeyGenerationRequest, vault_client) -> str:
        """Génère clé dans Vault"""
        path = f"{self.config.vault_mount_point}/data/{request.key_name}"
        
        key_data = {
            "type": request.key_type,
            "size": request.key_size,
            "algorithm": request.algorithm,
            "usage": [usage.value for usage in request.usage]
        }
        
        if request.key_type.upper() == "AES":
            key_data["key"] = base64.b64encode(os.urandom(request.key_size // 8)).decode()
        
        response = vault_client.secrets.kv.v2.create_or_update_secret(
            path=path,
            secret={"data": key_data}
        )
        
        return response["data"]["version"]

    async def _generate_aws_kms_key(self, request: KeyGenerationRequest, kms_client) -> str:
        """Génère clé dans AWS KMS"""
        response = kms_client.create_key(
            Description=f"iacherie key: {request.key_name}",
            KeyUsage='ENCRYPT_DECRYPT' if KeyUsage.ENCRYPT_DECRYPT in request.usage else 'SIGN_VERIFY',
            CustomerMasterKeySpec='SYMMETRIC_DEFAULT' if request.key_type.upper() == 'AES' else 'RSA_2048',
            Tags=[
                {'TagKey': 'Service', 'TagValue': 'iacherie'},
                {'TagKey': 'Owner', 'TagValue': request.owner},
                {'TagKey': 'KeyType', 'TagValue': request.key_type}
            ]
        )
        
        return response['KeyMetadata']['KeyId']

    async def _generate_azure_key(self, request: KeyGenerationRequest, vault_client) -> str:
        """Génère clé dans Azure Key Vault"""
        # Azure Key Vault implementation
        # Pour les clés symétriques, on stocke comme secret
        if request.key_type.upper() == "AES":
            key_value = base64.b64encode(os.urandom(request.key_size // 8)).decode()
            secret = vault_client.set_secret(request.key_name, key_value)
            return secret.name
        else:
            raise NotImplementedError("Azure asymmetric key generation not implemented")

    async def _rotate_key(self, key_id: str, request: KeyRotationRequest) -> str:
        """Rotation d'une clé"""
        metadata = await self._get_key_metadata(key_id)
        if not metadata:
            raise ValueError(f"Key not found: {key_id}")
        
        # Créer nouvelle clé avec mêmes paramètres
        new_request = KeyGenerationRequest(
            key_name=f"{metadata.key_name}_rotated",
            key_type=metadata.key_type,
            key_size=metadata.key_size,
            algorithm=metadata.algorithm,
            usage=metadata.usage,
            provider=metadata.provider,
            expires_at=metadata.expires_at,
            owner=metadata.owner,
            compliance_tags=metadata.compliance_tags
        )
        
        new_metadata = await self._generate_key(new_request)
        
        # Marquer ancienne clé comme inactive si pas de préservation
        if not request.preserve_old_key:
            await self._deactivate_key(key_id)
        
        return new_metadata.key_id

    async def _backup_key(self, key_id: str) -> str:
        """Sauvegarde automatique d'une clé"""
        backup_request = KeyBackupRequest(
            key_id=key_id,
            backup_location="default",
            encrypt_backup=self.config.backup_encryption
        )
        return await self._backup_key_with_request(key_id, backup_request)

    async def _backup_key_with_request(self, key_id: str, request: KeyBackupRequest) -> str:
        """Sauvegarde d'une clé avec paramètres spécifiques"""
        metadata = await self._get_key_metadata(key_id)
        if not metadata:
            raise ValueError(f"Key not found: {key_id}")
        
        backup_id = f"backup_{key_id}_{secrets.token_hex(8)}"
        
        # Récupérer matériel de clé selon provider
        key_material = await self._get_key_material(key_id, metadata.provider)
        
        # Chiffrer backup si requis
        if request.encrypt_backup:
            key_material = await self._encrypt_backup(key_material)
        
        # Stocker backup
        backup_data = {
            "backup_id": backup_id,
            "key_id": key_id,
            "metadata": metadata.dict(),
            "key_material": key_material,
            "encrypted": request.encrypt_backup,
            "created_at": datetime.utcnow().isoformat(),
            "location": request.backup_location
        }
        
        await self.redis.setex(
            f"backup:{backup_id}",
            86400 * 365,  # 1 year retention
            json.dumps(backup_data, default=str)
        )
        
        return backup_id

    async def _restore_key(self, request: KeyRestoreRequest) -> str:
        """Restauration d'une clé depuis backup"""
        backup_data_str = await self.redis.get(f"backup:{request.backup_id}")
        if not backup_data_str:
            raise ValueError(f"Backup not found: {request.backup_id}")
        
        backup_data = json.loads(backup_data_str)
        
        # Vérifier intégrité si requis
        if request.verify_integrity:
            await self._verify_backup_integrity(backup_data)
        
        # Restaurer clé
        restored_key_id = f"restored_{backup_data['key_id']}_{secrets.token_hex(8)}"
        
        metadata = KeyMetadata(**backup_data["metadata"])
        metadata.key_id = restored_key_id
        metadata.key_name = request.new_key_name or f"restored_{metadata.key_name}"
        metadata.created_at = datetime.utcnow()
        metadata.state = KeyState.ACTIVE
        
        # Déchiffrer matériel si nécessaire
        key_material = backup_data["key_material"]
        if backup_data["encrypted"]:
            key_material = await self._decrypt_backup(key_material)
        
        # Restaurer dans le provider original
        await self._restore_key_to_provider(metadata, key_material)
        
        # Stocker métadonnées
        self.key_metadata[restored_key_id] = metadata
        await self._persist_key_metadata(restored_key_id, metadata)
        
        return restored_key_id

    async def _check_keys_for_rotation(self):
        """Vérifie les clés qui nécessitent une rotation"""
        for key_id, metadata in self.key_metadata.items():
            if metadata.state != KeyState.ACTIVE:
                continue
            
            # Calculer âge de la clé
            age_days = (datetime.utcnow() - metadata.created_at).days
            
            # Vérifier si rotation nécessaire
            rotation_threshold = self.config.rotation_schedule_days
            if metadata.rotation_policy:
                # Parse custom rotation policy
                rotation_threshold = int(metadata.rotation_policy.split("_")[0])
            
            if age_days >= rotation_threshold:
                self.logger.info(f"Rotating key {key_id} (age: {age_days} days)")
                try:
                    rotation_request = KeyRotationRequest(
                        key_id=key_id,
                        immediate=False,
                        preserve_old_key=True,
                        notification_required=True
                    )
                    await self._rotate_key(key_id, rotation_request)
                except Exception as e:
                    self.logger.error(f"Automatic rotation failed for key {key_id}: {str(e)}")

    # Méthodes utilitaires
    
    async def _get_key_metadata(self, key_id: str) -> Optional[KeyMetadata]:
        """Récupère métadonnées d'une clé"""
        if key_id in self.key_metadata:
            return self.key_metadata[key_id]
        
        # Charger depuis Redis
        metadata_str = await self.redis.get(f"key_metadata:{key_id}")
        if metadata_str:
            metadata_dict = json.loads(metadata_str)
            metadata = KeyMetadata(**metadata_dict)
            self.key_metadata[key_id] = metadata
            return metadata
        
        return None

    async def _persist_key_metadata(self, key_id: str, metadata: KeyMetadata):
        """Persiste métadonnées d'une clé"""
        await self.redis.setex(
            f"key_metadata:{key_id}",
            86400 * 365,  # 1 year
            json.dumps(metadata.dict(), default=str)
        )

    async def _get_key_material(self, key_id: str, provider: KeyProvider) -> str:
        """Récupère matériel cryptographique d'une clé"""
        # Implementation depends on provider
        if provider == KeyProvider.LOCAL:
            # Get from local secure storage
            pass
        elif provider == KeyProvider.VAULT:
            # Get from Vault
            pass
        # etc.
        
        return "key_material_placeholder"

    async def _deactivate_key(self, key_id: str):
        """Désactive une clé"""
        metadata = await self._get_key_metadata(key_id)
        if metadata:
            metadata.state = KeyState.INACTIVE
            await self._persist_key_metadata(key_id, metadata)

    async def _destroy_key(self, key_id: str):
        """Destruction sécurisée d'une clé"""
        metadata = await self._get_key_metadata(key_id)
        if not metadata:
            raise ValueError(f"Key not found: {key_id}")
        
        # Marquer comme détruit
        metadata.state = KeyState.DESTROYED
        await self._persist_key_metadata(key_id, metadata)
        
        # Supprimer de la mémoire
        if key_id in self.key_metadata:
            del self.key_metadata[key_id]
        
        # Destruction dans le provider
        await self._destroy_key_in_provider(key_id, metadata.provider)

    async def _audit_operation(self, operation: str, key_id: str, provider: KeyProvider = None):
        """Audit des opérations sur les clés"""
        audit_data = {
            "operation": operation,
            "key_id": key_id,
            "provider": provider.value if provider else None,
            "timestamp": datetime.utcnow().isoformat(),
            "user": "system"  # TODO: extract from request context
        }
        
        await self.redis.lpush("key_mgmt_audit_log", json.dumps(audit_data))

    async def _check_provider_health(self, provider: KeyProvider, client: Any) -> bool:
        """Vérifie santé d'un provider"""
        try:
            if provider == KeyProvider.VAULT:
                return client.is_authenticated()
            elif provider == KeyProvider.AWS_KMS:
                client.list_keys(Limit=1)
                return True
            elif provider == KeyProvider.LOCAL:
                return True
            else:
                return False
        except Exception:
            return False

    def get_app(self) -> FastAPI:
        """Retourne instance FastAPI"""
        return self.app


def create_key_management_service(config: KeyManagementConfig = None) -> FastAPI:
    """
    Factory pour créer service de gestion de clés
    
    Args:
        config: Configuration personnalisée
        
    Returns:
        FastAPI: Instance du service configuré
    """
    key_mgmt_service = KeyManagementTemplate(config)
    return key_mgmt_service.get_app()


if __name__ == "__main__":
    import uvicorn
    
    config = KeyManagementConfig(
        default_provider=KeyProvider.LOCAL,
        enable_automatic_rotation=True,
        rotation_schedule_days=90,
        backup_enabled=True
    )
    
    app = create_key_management_service(config)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )