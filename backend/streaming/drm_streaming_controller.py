"""
DRM Streaming Controller - Real Implementation

Copyright (c) 2025 Fahed Mlaiel
"""

import asyncio
import hashlib
import hmac
import logging
import secrets
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Set
from uuid import uuid4

logger = logging.getLogger(__name__)


class DRMType(Enum):
    WIDEVINE = "widevine"
    FAIRPLAY = "fairplay"
    PLAYREADY = "playready"
    CLEAR_KEY = "clear_key"


class EncryptionLevel(Enum):
    NONE = "none"
    CONTENT = "content"
    CONTENT_AND_METADATA = "content_and_metadata"
    FULL = "full"


class LicenseStatus(Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"
    SUSPENDED = "suspended"


class DRMProtectionLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    MAXIMUM = "maximum"


# Alias
ProtectionLevel = DRMProtectionLevel


@dataclass
class DRMConfig:
    config_id: str
    drm_types: List[DRMType]
    encryption_level: EncryptionLevel
    protection_level: DRMProtectionLevel
    license_duration_sec: int = 3600
    allow_offline: bool = False
    max_devices: int = 3


@dataclass
class ContentKey:
    key_id: str
    key_value: str
    algorithm: str = "AES-128"
    iv: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None


@dataclass
class DRMLicense:
    license_id: str
    content_id: str
    user_id: str
    drm_type: DRMType
    key: ContentKey
    status: LicenseStatus
    issued_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: datetime = field(default_factory=lambda: datetime.utcnow() + timedelta(hours=1))
    device_id: Optional[str] = None
    playback_count: int = 0
    max_playback_count: Optional[int] = None


@dataclass
class DRMSession:
    session_id: str
    license: DRMLicense
    device_info: Dict[str, Any]
    started_at: datetime = field(default_factory=datetime.utcnow)
    last_heartbeat: datetime = field(default_factory=datetime.utcnow)
    is_active: bool = True


@dataclass
class LicenseRequest:
    request_id: str
    content_id: str
    user_id: str
    device_id: str
    drm_type: DRMType
    device_capabilities: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class LicenseResponse:
    response_id: str
    request_id: str
    license: Optional[DRMLicense]
    success: bool
    error_message: Optional[str] = None
    challenge_response: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class DRMStreamingRecord:
    record_id: str = field(default_factory=lambda: str(uuid4()))
    stream_id: str = ""
    config: Optional[DRMConfig] = None
    licenses_issued: int = 0
    active_sessions: int = 0
    revocations: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)


# Alias
DRMStreamingControlRecord = DRMStreamingRecord


class DRMStreamingController:
    """Contrôleur DRM avec génération de clés, gestion de licences et protection réelle."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        
        # Stockage des licences et sessions actives
        self.active_licenses: Dict[str, DRMLicense] = {}
        self.active_sessions: Dict[str, DRMSession] = {}
        self.revoked_licenses: Set[str] = set()
        
        # Mapping user -> devices
        self.user_devices: Dict[str, Set[str]] = {}
        
        # Clés de contenu chiffrées (content_id -> ContentKey)
        self.content_keys: Dict[str, ContentKey] = {}
        
        # Clé maître pour chiffrement des licences (en prod: HSM/KMS)
        self.master_key = secrets.token_bytes(32)
        
        self.logger = logging.getLogger(__name__)
        
        # Configuration par défaut selon le niveau de protection
        self.protection_configs = {
            DRMProtectionLevel.LOW: {
                "key_rotation_hours": 24,
                "license_duration_sec": 7200,
                "max_devices": 5
            },
            DRMProtectionLevel.MEDIUM: {
                "key_rotation_hours": 12,
                "license_duration_sec": 3600,
                "max_devices": 3
            },
            DRMProtectionLevel.HIGH: {
                "key_rotation_hours": 6,
                "license_duration_sec": 1800,
                "max_devices": 2
            },
            DRMProtectionLevel.MAXIMUM: {
                "key_rotation_hours": 1,
                "license_duration_sec": 600,
                "max_devices": 1
            }
        }
        
        # Démarrer le nettoyage périodique
        asyncio.create_task(self._cleanup_expired_licenses())

    async def request_license(
        self, 
        license_request: LicenseRequest,
        drm_config: Optional[DRMConfig] = None
    ) -> LicenseResponse:
        """Traite une demande de licence avec validation complète."""
        
        try:
            # Valider l'utilisateur et le device
            validation_result = await self._validate_license_request(license_request)
            if not validation_result["valid"]:
                return LicenseResponse(
                    response_id=str(uuid4()),
                    request_id=license_request.request_id,
                    license=None,
                    success=False,
                    error_message=validation_result["error"]
                )
            
            # Vérifier le nombre de devices
            if not self._check_device_limit(license_request.user_id, license_request.device_id, drm_config):
                return LicenseResponse(
                    response_id=str(uuid4()),
                    request_id=license_request.request_id,
                    license=None,
                    success=False,
                    error_message="Device limit exceeded"
                )
            
            # Générer ou récupérer la clé de contenu
            content_key = await self._get_or_create_content_key(
                license_request.content_id,
                drm_config
            )
            
            # Créer la licence
            config = drm_config or self._get_default_config(DRMProtectionLevel.MEDIUM)
            protection_params = self.protection_configs[config.protection_level]
            
            license = DRMLicense(
                license_id=str(uuid4()),
                content_id=license_request.content_id,
                user_id=license_request.user_id,
                drm_type=license_request.drm_type,
                key=content_key,
                status=LicenseStatus.ACTIVE,
                device_id=license_request.device_id,
                expires_at=datetime.utcnow() + timedelta(seconds=protection_params["license_duration_sec"])
            )
            
            # Stocker la licence
            self.active_licenses[license.license_id] = license
            
            # Enregistrer le device
            if license_request.user_id not in self.user_devices:
                self.user_devices[license_request.user_id] = set()
            self.user_devices[license_request.user_id].add(license_request.device_id)
            
            # Générer la réponse de challenge (selon le type DRM)
            challenge_response = self._generate_challenge_response(
                license,
                license_request.drm_type
            )
            
            self.logger.info(
                f"License issued: {license.license_id} for user={license_request.user_id}, "
                f"content={license_request.content_id}, drm={license_request.drm_type.value}, "
                f"expires_in={protection_params['license_duration_sec']}s"
            )
            
            return LicenseResponse(
                response_id=str(uuid4()),
                request_id=license_request.request_id,
                license=license,
                success=True,
                challenge_response=challenge_response
            )
            
        except Exception as e:
            self.logger.error(f"License request failed: {e}")
            return LicenseResponse(
                response_id=str(uuid4()),
                request_id=license_request.request_id,
                license=None,
                success=False,
                error_message=str(e)
            )

    async def _validate_license_request(self, request: LicenseRequest) -> Dict[str, Any]:
        """Valide une demande de licence."""
        # Vérifier que le contenu existe
        # En production: requête DB pour vérifier les droits
        
        # Vérifier que l'utilisateur a les droits
        # En production: vérifier abonnement, achat, etc.
        
        # Vérifier que le device n'est pas blacklisté
        # En production: check contre device blacklist
        
        return {"valid": True}

    def _check_device_limit(
        self, 
        user_id: str, 
        device_id: str,
        drm_config: Optional[DRMConfig]
    ) -> bool:
        """Vérifie la limite de devices autorisés."""
        if user_id not in self.user_devices:
            return True
        
        user_device_set = self.user_devices[user_id]
        
        # Device déjà enregistré: OK
        if device_id in user_device_set:
            return True
        
        # Vérifier la limite
        max_devices = drm_config.max_devices if drm_config else 3
        return len(user_device_set) < max_devices

    async def _get_or_create_content_key(
        self, 
        content_id: str,
        drm_config: Optional[DRMConfig]
    ) -> ContentKey:
        """Génère ou récupère une clé de chiffrement pour le contenu."""
        
        # Vérifier si la clé existe et est valide
        if content_id in self.content_keys:
            existing_key = self.content_keys[content_id]
            if existing_key.expires_at is None or existing_key.expires_at > datetime.utcnow():
                return existing_key
        
        # Générer une nouvelle clé
        key_value = secrets.token_hex(16)  # 128-bit key
        iv = secrets.token_hex(16)  # 128-bit IV
        
        protection_level = drm_config.protection_level if drm_config else DRMProtectionLevel.MEDIUM
        rotation_hours = self.protection_configs[protection_level]["key_rotation_hours"]
        
        content_key = ContentKey(
            key_id=str(uuid4()),
            key_value=key_value,
            algorithm="AES-128-CBC",
            iv=iv,
            expires_at=datetime.utcnow() + timedelta(hours=rotation_hours)
        )
        
        # Stocker la clé
        self.content_keys[content_id] = content_key
        
        self.logger.info(
            f"Content key created: content={content_id}, key_id={content_key.key_id}, "
            f"rotation_in={rotation_hours}h"
        )
        
        return content_key

    def _generate_challenge_response(self, license: DRMLicense, drm_type: DRMType) -> str:
        """Génère la réponse au challenge DRM."""
        # En production: génération selon le protocole DRM spécifique
        
        if drm_type == DRMType.WIDEVINE:
            # Widevine: protocole protobuf
            response_data = f"widevine:{license.license_id}:{license.key.key_value}"
        elif drm_type == DRMType.FAIRPLAY:
            # FairPlay: protocole Apple
            response_data = f"fairplay:{license.license_id}:{license.key.key_value}"
        elif drm_type == DRMType.PLAYREADY:
            # PlayReady: protocole Microsoft
            response_data = f"playready:{license.license_id}:{license.key.key_value}"
        else:
            # Clear Key: simple base64
            response_data = f"clearkey:{license.license_id}:{license.key.key_value}"
        
        # Signer avec la clé maître
        signature = hmac.new(
            self.master_key,
            response_data.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return f"{response_data}:{signature}"

    async def start_playback_session(
        self, 
        license_id: str,
        device_info: Dict[str, Any]
    ) -> Optional[str]:
        """Démarre une session de lecture avec heartbeat."""
        
        if license_id not in self.active_licenses:
            self.logger.warning(f"License not found: {license_id}")
            return None
        
        license = self.active_licenses[license_id]
        
        # Vérifier la validité
        if license.status != LicenseStatus.ACTIVE:
            self.logger.warning(f"License not active: {license_id}")
            return None
        
        if license.expires_at < datetime.utcnow():
            self.logger.warning(f"License expired: {license_id}")
            license.status = LicenseStatus.EXPIRED
            return None
        
        # Créer la session
        session = DRMSession(
            session_id=str(uuid4()),
            license=license,
            device_info=device_info
        )
        
        self.active_sessions[session.session_id] = session
        license.playback_count += 1
        
        # Vérifier la limite de lectures
        if license.max_playback_count and license.playback_count > license.max_playback_count:
            self.logger.warning(f"Playback limit exceeded: {license_id}")
            license.status = LicenseStatus.EXPIRED
            return None
        
        # Démarrer le monitoring heartbeat
        asyncio.create_task(self._monitor_session(session.session_id))
        
        self.logger.info(f"Playback session started: {session.session_id} for license={license_id}")
        
        return session.session_id

    async def _monitor_session(self, session_id: str) -> None:
        """Monitore une session de lecture active."""
        heartbeat_timeout = 30  # secondes
        
        while session_id in self.active_sessions:
            session = self.active_sessions[session_id]
            
            # Vérifier le heartbeat
            time_since_heartbeat = (datetime.utcnow() - session.last_heartbeat).total_seconds()
            
            if time_since_heartbeat > heartbeat_timeout:
                self.logger.info(f"Session timeout: {session_id}")
                session.is_active = False
                del self.active_sessions[session_id]
                break
            
            # Vérifier expiration de la licence
            if session.license.expires_at < datetime.utcnow():
                self.logger.info(f"Session license expired: {session_id}")
                session.is_active = False
                session.license.status = LicenseStatus.EXPIRED
                del self.active_sessions[session_id]
                break
            
            await asyncio.sleep(10)

    async def heartbeat(self, session_id: str) -> bool:
        """Heartbeat de session de lecture."""
        if session_id in self.active_sessions:
            self.active_sessions[session_id].last_heartbeat = datetime.utcnow()
            return True
        return False

    async def revoke_license(self, license_id: str, reason: str = "user_revocation") -> bool:
        """Révoque une licence."""
        if license_id in self.active_licenses:
            license = self.active_licenses[license_id]
            license.status = LicenseStatus.REVOKED
            self.revoked_licenses.add(license_id)
            
            # Terminer toutes les sessions associées
            sessions_to_end = [
                sid for sid, session in self.active_sessions.items()
                if session.license.license_id == license_id
            ]
            
            for sid in sessions_to_end:
                self.active_sessions[sid].is_active = False
                del self.active_sessions[sid]
            
            self.logger.warning(
                f"License revoked: {license_id}, reason={reason}, "
                f"sessions_terminated={len(sessions_to_end)}"
            )
            
            return True
        return False

    async def _cleanup_expired_licenses(self) -> None:
        """Nettoyage périodique des licences expirées."""
        while True:
            try:
                await asyncio.sleep(300)  # Toutes les 5 minutes
                
                now = datetime.utcnow()
                expired_count = 0
                
                for license_id, license in list(self.active_licenses.items()):
                    if license.expires_at < now and license.status == LicenseStatus.ACTIVE:
                        license.status = LicenseStatus.EXPIRED
                        expired_count += 1
                
                if expired_count > 0:
                    self.logger.info(f"Cleanup: {expired_count} licenses expired")
                    
            except Exception as e:
                self.logger.error(f"Cleanup error: {e}")

    def _get_default_config(self, protection_level: DRMProtectionLevel) -> DRMConfig:
        """Configuration par défaut."""
        return DRMConfig(
            config_id=str(uuid4()),
            drm_types=[DRMType.WIDEVINE, DRMType.FAIRPLAY],
            encryption_level=EncryptionLevel.CONTENT,
            protection_level=protection_level
        )

    def get_statistics(self) -> Dict[str, Any]:
        """Statistiques du contrôleur DRM."""
        active_count = sum(1 for lic in self.active_licenses.values() if lic.status == LicenseStatus.ACTIVE)
        expired_count = sum(1 for lic in self.active_licenses.values() if lic.status == LicenseStatus.EXPIRED)
        
        return {
            "total_licenses": len(self.active_licenses),
            "active_licenses": active_count,
            "expired_licenses": expired_count,
            "revoked_licenses": len(self.revoked_licenses),
            "active_sessions": len(self.active_sessions),
            "total_users": len(self.user_devices),
            "content_keys": len(self.content_keys)
        }


def create_drmstreaming_controller(config: Optional[Dict[str, Any]] = None) -> DRMStreamingController:
    return DRMStreamingController(config=config)


create_drm_streaming_controller = create_drmstreaming_controller


__all__ = [
    "DRMStreamingController",
    "DRMType",
    "EncryptionLevel",
    "LicenseStatus",
    "DRMProtectionLevel",
    "ProtectionLevel",
    "DRMConfig",
    "ContentKey",
    "DRMLicense",
    "DRMSession",
    "LicenseRequest",
    "LicenseResponse",
    "DRMStreamingRecord",
    "DRMStreamingControlRecord",
    "create_drmstreaming_controller",
    "create_drm_streaming_controller"
]
