"""
API Credentials Management Module

Gestion sécurisée des credentials d'API pour les intégrations plateformes
dans la plateforme IA Influencer Agent.

Ce module fournit:
- Stockage sécurisé et chiffré des credentials
- Rotation automatique des clés d'API
- Mapping des credentials par plateforme
- Audit trail des utilisations
- Gestion des quotas et limitations

Auteur: Fahed Mlaiel <mlaiel@live.de>
Email: mlaiel@live.de
Équipe: Lead AI Developer, Backend Senior, Security Specialist, DevOps Engineer

  AVERTISSEMENT LEGAL 
Ce code et concept sont la propriété intellectuelle exclusive de Fahed Mlaiel.
Toute utilisation, copie, modification ou distribution sans autorisation 
écrite explicite est strictement interdite et fera l'objet de poursuites 
judiciaires selon le droit allemand et international.

Contact pour autorisation: mlaiel@live.de
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, JSON, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from typing import Dict, List, Any, Optional, Union
import uuid
import logging
from datetime import datetime, timedelta
from enum import Enum
import hashlib
import secrets
from cryptography.fernet import Fernet
import os

from backend.database.models.base import BaseModel

logger = logging.getLogger(__name__)


class CredentialType(Enum):
    """Types de credentials supportés."""
    API_KEY = "api_key"
    OAUTH2 = "oauth2"
    BEARER_TOKEN = "bearer_token"
    BASIC_AUTH = "basic_auth"
    JWT = "jwt"
    WEBHOOK_SECRET = "webhook_secret"
    CERTIFICATE = "certificate"


class CredentialStatus(Enum):
    """Statuts des credentials."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    EXPIRED = "expired"
    REVOKED = "revoked"
    PENDING_ROTATION = "pending_rotation"
    ROTATING = "rotating"


class PlatformType(Enum):
    """Types de plateformes supportées."""
    SOCIAL_MEDIA = "social_media"
    MUSIC_STREAMING = "music_streaming"
    VIDEO_PLATFORM = "video_platform"
    BLOGGING_PLATFORM = "blogging_platform"
    E_COMMERCE = "e_commerce"
    ANALYTICS = "analytics"
    PAYMENT = "payment"
    STORAGE = "storage"
    AI_SERVICE = "ai_service"
    NOTIFICATION = "notification"


# Plateformes supportées avec leurs configurations
SUPPORTED_PLATFORMS = {
    "spotify": {
        "name": "Spotify",
        "type": PlatformType.MUSIC_STREAMING,
        "auth_type": CredentialType.OAUTH2,
        "scopes": ["user-read-private", "user-read-email", "playlist-read-private", "user-library-read"],
        "api_base_url": "https://api.spotify.com/v1",
        "auth_url": "https://accounts.spotify.com/authorize",
        "token_url": "https://accounts.spotify.com/api/token",
        "rate_limits": {"requests_per_second": 1, "requests_per_hour": 1000}
    },
    "youtube": {
        "name": "YouTube",
        "type": PlatformType.VIDEO_PLATFORM,
        "auth_type": CredentialType.API_KEY,
        "scopes": ["youtube.readonly", "youtube.upload", "youtube.force-ssl"],
        "api_base_url": "https://www.googleapis.com/youtube/v3",
        "rate_limits": {"requests_per_day": 10000, "quota_units_per_day": 10000}
    },
    "instagram": {
        "name": "Instagram",
        "type": PlatformType.SOCIAL_MEDIA,
        "auth_type": CredentialType.OAUTH2,
        "scopes": ["instagram_basic", "instagram_content_publish", "pages_read_engagement"],
        "api_base_url": "https://graph.instagram.com",
        "rate_limits": {"requests_per_hour": 200, "requests_per_user_per_hour": 200}
    },
    "tiktok": {
        "name": "TikTok",
        "type": PlatformType.SOCIAL_MEDIA,
        "auth_type": CredentialType.OAUTH2,
        "scopes": ["user.info.basic", "video.list", "video.publish"],
        "api_base_url": "https://open-api.tiktok.com",
        "rate_limits": {"requests_per_day": 1000}
    },
    "twitter": {
        "name": "Twitter/X",
        "type": PlatformType.SOCIAL_MEDIA,
        "auth_type": CredentialType.BEARER_TOKEN,
        "scopes": ["tweet.read", "users.read", "space.read"],
        "api_base_url": "https://api.twitter.com/2",
        "rate_limits": {"requests_per_15_min": 300}
    },
    "facebook": {
        "name": "Facebook",
        "type": PlatformType.SOCIAL_MEDIA,
        "auth_type": CredentialType.OAUTH2,
        "scopes": ["pages_read_engagement", "pages_manage_posts", "business_management"],
        "api_base_url": "https://graph.facebook.com",
        "rate_limits": {"requests_per_hour": 200}
    },
    "soundcloud": {
        "name": "SoundCloud",
        "type": PlatformType.MUSIC_STREAMING,
        "auth_type": CredentialType.OAUTH2,
        "scopes": ["non-expiring", "read"],
        "api_base_url": "https://api.soundcloud.com",
        "rate_limits": {"requests_per_hour": 15000}
    },
    "bandcamp": {
        "name": "Bandcamp",
        "type": PlatformType.MUSIC_STREAMING,
        "auth_type": CredentialType.API_KEY,
        "api_base_url": "https://bandcamp.com/api",
        "rate_limits": {"requests_per_minute": 120}
    },
    "substack": {
        "name": "Substack",
        "type": PlatformType.BLOGGING_PLATFORM,
        "auth_type": CredentialType.API_KEY,
        "api_base_url": "https://substack.com/api/v1",
        "rate_limits": {"requests_per_hour": 1000}
    },
    "medium": {
        "name": "Medium",
        "type": PlatformType.BLOGGING_PLATFORM,
        "auth_type": CredentialType.BEARER_TOKEN,
        "api_base_url": "https://api.medium.com/v1",
        "rate_limits": {"requests_per_hour": 1000}
    }
}


class APICredential(BaseModel):
    """
    Modèle pour les credentials d'API sécurisés.
    
    Stocke de manière chiffrée les clés d'API, tokens OAuth,
    et autres credentials nécessaires aux intégrations.
    """
    
    __tablename__ = "api_credentials"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    platform_name = Column(String(50), nullable=False, index=True)
    credential_type = Column(SQLEnum(CredentialType), nullable=False)
    credential_status = Column(SQLEnum(CredentialStatus), default=CredentialStatus.ACTIVE, index=True)
    
    # Identifiants et noms
    name = Column(String(100), nullable=False)
    description = Column(Text)
    environment = Column(String(20), default="production")  # development, staging, production
    
    # Credentials chiffrés (utilise Fernet pour le chiffrement symétrique)
    encrypted_client_id = Column(Text)
    encrypted_client_secret = Column(Text)
    encrypted_api_key = Column(Text)
    encrypted_access_token = Column(Text)
    encrypted_refresh_token = Column(Text)
    encrypted_private_key = Column(Text)
    
    # Métadonnées OAuth
    scopes = Column(JSONB, default=list)
    redirect_uri = Column(Text)
    auth_url = Column(Text)
    token_url = Column(Text)
    
    # Gestion des expirations
    expires_at = Column(DateTime(timezone=True))
    refresh_expires_at = Column(DateTime(timezone=True))
    auto_refresh_enabled = Column(Boolean, default=True)
    
    # Quotas et limitations
    daily_quota = Column(Integer, default=10000)
    hourly_quota = Column(Integer, default=1000)
    current_daily_usage = Column(Integer, default=0)
    current_hourly_usage = Column(Integer, default=0)
    quota_reset_at = Column(DateTime(timezone=True))
    
    # Rotation des clés
    rotation_enabled = Column(Boolean, default=True)
    rotation_interval_days = Column(Integer, default=90)
    last_rotated_at = Column(DateTime(timezone=True))
    next_rotation_at = Column(DateTime(timezone=True))
    
    # Sécurité et audit
    created_by = Column(UUID(as_uuid=True))
    last_used_at = Column(DateTime(timezone=True))
    last_used_by = Column(UUID(as_uuid=True))
    usage_count = Column(Integer, default=0)
    
    # Métadonnées et configuration
    metadata = Column(JSONB, default=dict)
    webhook_endpoints = Column(JSONB, default=list)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<APICredential(platform={self.platform_name}, type={self.credential_type.value})>"
    
    @property
    def is_expired(self) -> bool:
        """Vérifie si le credential est expiré."""
        if not self.expires_at:
            return False
        return datetime.utcnow() > self.expires_at
    
    @property
    def needs_rotation(self) -> bool:
        """Vérifie si le credential nécessite une rotation."""
        if not self.rotation_enabled or not self.next_rotation_at:
            return False
        return datetime.utcnow() > self.next_rotation_at
    
    @property
    def daily_quota_remaining(self) -> int:
        """Calcule le quota journalier restant."""



        return max(0, self.daily_quota - self.current_daily_usage)
    
    @property
    def hourly_quota_remaining(self) -> int:
        """Calcule le quota horaire restant."""



        return max(0, self.hourly_quota - self.current_hourly_usage)
    
    def encrypt_credential(self, value: str, field_name: str) -> str:
        """Chiffre une valeur de credential."""
        if not value:
            return None
        
        # Utilise la clé de chiffrement depuis les variables d'environnement
        encryption_key = os.getenv("CREDENTIAL_ENCRYPTION_KEY")
        if not encryption_key:
            raise ValueError("CREDENTIAL_ENCRYPTION_KEY not found in environment variables")
        
        fernet = Fernet(encryption_key.encode())
        encrypted_value = fernet.encrypt(value.encode())
        return encrypted_value.decode()
    
    def decrypt_credential(self, encrypted_value: str) -> str:
        """Déchiffre une valeur de credential."""
        if not encrypted_value:
            return None
        
        encryption_key = os.getenv("CREDENTIAL_ENCRYPTION_KEY")
        if not encryption_key:
            raise ValueError("CREDENTIAL_ENCRYPTION_KEY not found in environment variables")
        
        fernet = Fernet(encryption_key.encode())
        decrypted_value = fernet.decrypt(encrypted_value.encode())
        return decrypted_value.decode()
    
    def set_client_secret(self, secret: str):
        """Définit le client secret de manière chiffrée."""
        self.encrypted_client_secret = self.encrypt_credential(secret, "client_secret")
    
    def get_client_secret(self) -> str:
        """Récupère le client secret déchiffré."""



        return self.decrypt_credential(self.encrypted_client_secret)
    
    def set_api_key(self, api_key: str):
        """Définit la clé API de manière chiffrée."""
        self.encrypted_api_key = self.encrypt_credential(api_key, "api_key")
    
    def get_api_key(self) -> str:
        """Récupère la clé API déchiffrée."""



        return self.decrypt_credential(self.encrypted_api_key)
    
    def increment_usage(self):
        """Incrémente les compteurs d'utilisation."""
        self.usage_count += 1
        self.current_daily_usage += 1
        self.current_hourly_usage += 1
        self.last_used_at = datetime.utcnow()
    
    def reset_daily_quota(self):
        """Remet à zéro le quota journalier."""
        self.current_daily_usage = 0
        self.quota_reset_at = datetime.utcnow() + timedelta(days=1)
    
    def reset_hourly_quota(self):
        """Remet à zéro le quota horaire."""
        self.current_hourly_usage = 0


class CredentialUsageLog(BaseModel):
    """
    Log d'utilisation des credentials pour audit et monitoring.
    """
    
    __tablename__ = "credential_usage_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    credential_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    platform_name = Column(String(50), nullable=False, index=True)
    
    # Détails de l'utilisation
    used_by = Column(UUID(as_uuid=True))  # user_id
    service_name = Column(String(100))  # service qui a utilisé le credential
    endpoint_called = Column(String(255))
    http_method = Column(String(10))
    
    # Résultat de l'utilisation
    success = Column(Boolean, nullable=False, index=True)
    status_code = Column(Integer)
    response_time_ms = Column(Integer)
    error_message = Column(Text)
    
    # Contexte
    user_agent = Column(String(500))
    ip_address = Column(String(45))
    request_id = Column(String(100))
    
    # Métadonnées
    request_size_bytes = Column(Integer)
    response_size_bytes = Column(Integer)
    quota_consumed = Column(Integer, default=1)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<CredentialUsageLog(platform={self.platform_name}, success={self.success})>"


class PlatformAPIMapping(BaseModel):
    """
    Mapping des APIs et endpoints par plateforme.
    
    Définit quels credentials utiliser pour quels endpoints,
    avec les configurations spécifiques.
    """
    
    __tablename__ = "platform_api_mappings"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    platform_name = Column(String(50), nullable=False, index=True)
    api_category = Column(String(50), nullable=False)  # auth, users, content, analytics
    
    # Configuration de l'API
    base_url = Column(Text, nullable=False)
    api_version = Column(String(20), default="v1")
    documentation_url = Column(Text)
    
    # Credentials requis
    required_credential_types = Column(JSONB, default=list)
    fallback_credential_id = Column(UUID(as_uuid=True))
    
    # Endpoints disponibles
    endpoints = Column(JSONB, default=dict)  # {endpoint_name: {method, path, scopes, etc.}}
    
    # Rate limiting
    rate_limits = Column(JSONB, default=dict)
    rate_limit_headers = Column(JSONB, default=list)
    
    # Configuration avancée
    retry_policy = Column(JSONB, default={"max_retries": 3, "backoff_factor": 2})
    timeout_seconds = Column(Integer, default=30)
    custom_headers = Column(JSONB, default=dict)
    
    # Monitoring
    health_check_endpoint = Column(String(255))
    health_check_interval = Column(Integer, default=300)  # secondes
    last_health_check = Column(DateTime(timezone=True))
    is_healthy = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<PlatformAPIMapping(platform={self.platform_name}, category={self.api_category})>"


class CredentialRotationHistory(BaseModel):
    """
    Historique des rotations de credentials pour audit et rollback.
    """
    
    __tablename__ = "credential_rotation_history"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    credential_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    platform_name = Column(String(50), nullable=False, index=True)
    
    # Détails de la rotation
    rotation_type = Column(String(20), nullable=False)  # automatic, manual, emergency
    rotation_reason = Column(String(100))  # scheduled, expired, compromised, user_request
    
    # Credentials précédents (hash pour vérification)
    previous_credential_hash = Column(String(255))
    new_credential_hash = Column(String(255))
    
    # Statut de la rotation
    rotation_status = Column(String(20), nullable=False)  # initiated, in_progress, completed, failed
    rotation_started_at = Column(DateTime(timezone=True), nullable=False)
    rotation_completed_at = Column(DateTime(timezone=True))
    
    # Détails techniques
    initiated_by = Column(UUID(as_uuid=True))  # user_id or system
    rollback_available = Column(Boolean, default=True)
    rollback_expires_at = Column(DateTime(timezone=True))
    
    # Résultats et erreurs
    success = Column(Boolean)
    error_details = Column(JSONB, default=dict)
    affected_services = Column(JSONB, default=list)
    
    # Métadonnées
    metadata = Column(JSONB, default=dict)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<CredentialRotationHistory(platform={self.platform_name}, status={self.rotation_status})>"


def create_platform_credential(
    platform_name: str,
    credential_type: CredentialType,
    credentials: Dict[str, str],
    name: str = None,
    environment: str = "production",
    metadata: Dict[str, Any] = None
) -> APICredential:
    """
    Crée un nouveau credential pour une plateforme.
    
    Args:
        platform_name: Nom de la plateforme
        credential_type: Type de credential
        credentials: Dictionnaire contenant les credentials
        name: Nom du credential
        environment: Environnement (development, staging, production)
        metadata: Métadonnées additionnelles
    
    Returns:
        Instance d'APICredential
    """
    if platform_name not in SUPPORTED_PLATFORMS:
        raise ValueError(f"Platform {platform_name} not supported")
    
    platform_config = SUPPORTED_PLATFORMS[platform_name]
    
    credential = APICredential(
        platform_name=platform_name,
        credential_type=credential_type,
        name=name or f"{platform_config['name']} {credential_type.value}",
        environment=environment,
        metadata=metadata or {},
        scopes=platform_config.get("scopes", []),
        auth_url=platform_config.get("auth_url"),
        token_url=platform_config.get("token_url")
    )
    
    # Définit les credentials en fonction du type
    if credential_type == CredentialType.API_KEY and "api_key" in credentials:
        credential.set_api_key(credentials["api_key"])
    
    elif credential_type == CredentialType.OAUTH2:
        if "client_id" in credentials:
            credential.encrypted_client_id = credential.encrypt_credential(
                credentials["client_id"], "client_id"
            )
        if "client_secret" in credentials:
            credential.set_client_secret(credentials["client_secret"])
        if "access_token" in credentials:
            credential.encrypted_access_token = credential.encrypt_credential(
                credentials["access_token"], "access_token"
            )
        if "refresh_token" in credentials:
            credential.encrypted_refresh_token = credential.encrypt_credential(
                credentials["refresh_token"], "refresh_token"
            )
    
    # Configure les quotas par défaut
    rate_limits = platform_config.get("rate_limits", {})
    if "requests_per_day" in rate_limits:
        credential.daily_quota = rate_limits["requests_per_day"]
    if "requests_per_hour" in rate_limits:
        credential.hourly_quota = rate_limits["requests_per_hour"]
    
    # Configure la rotation automatique
    if credential.rotation_enabled:
        credential.next_rotation_at = datetime.utcnow() + timedelta(
            days=credential.rotation_interval_days
        )
    
    return credential


def generate_encryption_key() -> str:
    """Génère une nouvelle clé de chiffrement Fernet."""



    return Fernet.generate_key().decode()


def hash_credential(credential_value: str) -> str:
    """Génère un hash sécurisé d'un credential pour l'audit."""
    salt = secrets.token_hex(16)
    credential_hash = hashlib.pbkdf2_hmac(
        'sha256',
        credential_value.encode('utf-8'),
        salt.encode('utf-8'),
        100000  # 100k iterations
    )
    return f"{salt}:{credential_hash.hex()}"
    
    # Configuration OAuth2
    authorization_url = Column(Text)
    token_url = Column(Text)
    revoke_url = Column(Text)
    redirect_uri = Column(Text)
    
    # Scopes et permissions par défaut
    default_scopes = Column(JSONB, default=list)
    available_scopes = Column(JSONB, default=list)
    
    # Limites et quotas
    rate_limit_per_minute = Column(Integer, default=60)
    rate_limit_per_hour = Column(Integer, default=1000)
    rate_limit_per_day = Column(Integer, default=10000)
    monthly_quota = Column(Integer)
    
    # Configuration avancée
    base_url = Column(Text)
    api_version = Column(String(20))
    environment = Column(String(20), default="production")  # sandbox, staging, production
    
    # Statut et validation
    is_active = Column(Boolean, default=True)
    is_validated = Column(Boolean, default=False)
    last_validated = Column(DateTime(timezone=True))
    validation_error = Column(Text)
    
    # Métadonnées
    credential_metadata = Column(JSONB, default=dict)
    
    # Rotation des clés
    expires_at = Column(DateTime(timezone=True))
    rotation_frequency_days = Column(Integer, default=90)
    last_rotated = Column(DateTime(timezone=True))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<APICredential(platform={self.platform_name}, type={self.credential_type})>"
    
    @classmethod
    def get_encryption_key(cls) -> bytes:
        """Récupère la clé de chiffrement depuis les variables d'environnement."""
        key = os.environ.get('CREDENTIALS_ENCRYPTION_KEY')
        if not key:
            # Génération d'une nouvelle clé si elle n'existe pas
            key = Fernet.generate_key()
            logger.warning("Nouvelle clé de chiffrement générée - À sauvegarder en sécurité")
        
        if isinstance(key, str):
            key = key.encode()
        
        return key
    
    def encrypt_value(self, value: str) -> bytes:
        """Chiffre une valeur sensible."""
        if not value:
            return None
        
        fernet = Fernet(self.get_encryption_key())
        return fernet.encrypt(value.encode())
    
    def decrypt_value(self, encrypted_value: bytes) -> str:
        """Déchiffre une valeur sensible."""
        if not encrypted_value:
            return None
        
        fernet = Fernet(self.get_encryption_key())
        return fernet.decrypt(encrypted_value).decode()
    
    def set_client_secret(self, secret: str):
        """Définit le client secret de manière chiffrée."""
        self.client_secret = self.encrypt_value(secret)
    
    def get_client_secret(self) -> str:
        """Récupère le client secret déchiffré."""



        return self.decrypt_value(self.client_secret)
    
    def set_api_key(self, key: str):
        """Définit la clé API de manière chiffrée."""
        self.api_key = self.encrypt_value(key)
    
    def get_api_key(self) -> str:
        """Récupère la clé API déchiffrée."""



        return self.decrypt_value(self.api_key)
    
    def set_api_secret(self, secret: str):
        """Définit le secret API de manière chiffré."""
        self.api_secret = self.encrypt_value(secret)
    
    def get_api_secret(self) -> str:
        """Récupère le secret API déchiffré."""



        return self.decrypt_value(self.api_secret)
    
    @property
    def is_expired(self) -> bool:
        """Vérifie si les credentials sont expirés."""
        if not self.expires_at:
            return False
        return datetime.utcnow() > self.expires_at
    
    @property
    def needs_rotation(self) -> bool:
        """Vérifie si les credentials ont besoin d'une rotation."""
        if not self.last_rotated or not self.rotation_frequency_days:
            return False
        
        rotation_due = self.last_rotated + timedelta(days=self.rotation_frequency_days)
        return datetime.utcnow() > rotation_due
    
    def validate_credentials(self) -> bool:
        """Valide les credentials avec une requête test à l'API."""
        # Cette méthode sera implémentée par les services spécifiques
        # pour chaque plateforme
        pass
    
    def to_dict_safe(self) -> Dict[str, Any]:
        """Retourne un dictionnaire sans les données sensibles."""



        return {
            "id": str(self.id),
            "platform_name": self.platform_name,
            "credential_type": self.credential_type,
            "client_id": self.client_id,
            "app_id": self.app_id,
            "is_active": self.is_active,
            "is_validated": self.is_validated,
            "environment": self.environment,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "needs_rotation": self.needs_rotation,
            "created_at": self.created_at.isoformat()
        }


class CredentialUsageLog(BaseModel):
    """
    Modèle pour les logs d'utilisation des credentials.
    
    Trace l'utilisation des credentials pour audit de sécurité
    et monitoring des quotas.
    """
    
    __tablename__ = "credential_usage_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    credential_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # Détails de l'utilisation
    operation = Column(String(50), nullable=False)
    endpoint = Column(String(255))
    user_agent = Column(String(500))
    ip_address = Column(String(45))
    
    # Résultat
    status_code = Column(Integer)
    success = Column(Boolean, default=False)
    error_message = Column(Text)
    
    # Métriques
    response_time_ms = Column(Integer)
    data_transferred_bytes = Column(Integer)
    
    # Quotas utilisés
    quota_used = Column(Integer, default=1)
    quota_remaining = Column(Integer)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<CredentialUsageLog(operation={self.operation}, success={self.success})>"


class PlatformAPIMapping(BaseModel):
    """
    Modèle pour le mapping des APIs des plateformes.
    
    Définit la correspondance entre les opérations internes
    et les endpoints des APIs externes.
    """
    
    __tablename__ = "platform_api_mappings"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    platform_name = Column(String(50), nullable=False, index=True)
    
    # Opération interne
    internal_operation = Column(String(100), nullable=False)
    operation_category = Column(String(50))  # content, analytics, user, auth
    
    # Endpoint externe
    external_endpoint = Column(Text, nullable=False)
    http_method = Column(String(10), default="GET")
    
    # Paramètres de mapping
    parameter_mapping = Column(JSONB, default=dict)
    response_mapping = Column(JSONB, default=dict)
    
    # Transformations des données
    request_transformer = Column(String(255))  # Nom de la fonction de transformation
    response_transformer = Column(String(255))
    
    # Configuration
    requires_pagination = Column(Boolean, default=False)
    pagination_config = Column(JSONB, default=dict)
    
    rate_limit_category = Column(String(50))
    cache_duration_seconds = Column(Integer, default=300)
    
    # Statut
    is_active = Column(Boolean, default=True)
    is_deprecated = Column(Boolean, default=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<PlatformAPIMapping(platform={self.platform_name}, operation={self.internal_operation})>"


class CredentialRotationHistory(BaseModel):
    """
    Modèle pour l'historique de rotation des credentials.
    
    Maintient un audit trail des rotations de credentials
    pour la sécurité et la conformité.
    """
    
    __tablename__ = "credential_rotation_history"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    credential_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # Détails de la rotation
    rotation_type = Column(String(20), nullable=False)  # manual, automatic, forced
    rotation_reason = Column(String(100))
    
    # Ancien et nouveau
    previous_key_hash = Column(String(64))  # Hash SHA-256 pour audit
    new_key_hash = Column(String(64))
    
    # Métadonnées
    rotated_by = Column(String(255))  # User ID ou system
    rotation_metadata = Column(JSONB, default=dict)
    
    # Validation
    validation_success = Column(Boolean)
    validation_error = Column(Text)
    
    # Timing
    rotation_started = Column(DateTime(timezone=True), nullable=False)
    rotation_completed = Column(DateTime(timezone=True))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<CredentialRotationHistory(type={self.rotation_type}, completed={self.rotation_completed is not None})>"


# Configuration des plateformes supportées
SUPPORTED_PLATFORMS = {
    "spotify": {
        "credential_type": "oauth2",
        "base_url": "https://api.spotify.com/v1",
        "authorization_url": "https://accounts.spotify.com/authorize",
        "token_url": "https://accounts.spotify.com/api/token",
        "default_scopes": [
            "user-read-private",
            "user-read-email",
            "user-library-read",
            "user-top-read",
            "playlist-read-private"
        ]
    },
    "youtube": {
        "credential_type": "oauth2",
        "base_url": "https://www.googleapis.com/youtube/v3",
        "authorization_url": "https://accounts.google.com/o/oauth2/auth",
        "token_url": "https://oauth2.googleapis.com/token",
        "default_scopes": [
            "https://www.googleapis.com/auth/youtube.readonly",
            "https://www.googleapis.com/auth/youtube.upload"
        ]
    },
    "instagram": {
        "credential_type": "oauth2",
        "base_url": "https://graph.instagram.com",
        "authorization_url": "https://api.instagram.com/oauth/authorize",
        "token_url": "https://api.instagram.com/oauth/access_token",
        "default_scopes": [
            "user_profile",
            "user_media"
        ]
    },
    "tiktok": {
        "credential_type": "oauth2",
        "base_url": "https://open-api.tiktok.com",
        "authorization_url": "https://www.tiktok.com/auth/authorize",
        "token_url": "https://open-api.tiktok.com/oauth/access_token",
        "default_scopes": [
            "user.info.basic",
            "video.list"
        ]
    },
    "twitter": {
        "credential_type": "oauth2",
        "base_url": "https://api.twitter.com/2",
        "authorization_url": "https://twitter.com/i/oauth2/authorize",
        "token_url": "https://api.twitter.com/2/oauth2/token",
        "default_scopes": [
            "tweet.read",
            "users.read"
        ]
    }
}


def create_platform_credential(platform_name: str, **kwargs) -> APICredential:
    """
    Crée un credential pour une plateforme spécifique.
    
    Args:
        platform_name: Nom de la plateforme
        **kwargs: Paramètres spécifiques au credential
    
    Returns:
        APICredential: Instance du credential créé
    """
    if platform_name not in SUPPORTED_PLATFORMS:
        raise ValueError(f"Plateforme non supportée: {platform_name}")
    
    platform_config = SUPPORTED_PLATFORMS[platform_name]
    
    credential = APICredential(
        platform_name=platform_name,
        credential_type=platform_config["credential_type"],
        base_url=platform_config["base_url"],
        authorization_url=platform_config["authorization_url"],
        token_url=platform_config["token_url"],
        default_scopes=platform_config["default_scopes"],
        **kwargs
    )
    
    return credential


# Index pour optimisation des performances
from sqlalchemy import Index

api_credential_platform_active_idx = Index(
    'idx_api_credentials_platform_active',
    APICredential.platform_name,
    APICredential.is_active
)

credential_usage_log_credential_date_idx = Index(
    'idx_credential_usage_logs_credential_date',
    CredentialUsageLog.credential_id,
    CredentialUsageLog.created_at
)
