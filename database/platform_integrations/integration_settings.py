"""Integration Settings Management Module

Gestion des paramètres d'intégration pour les plateformes externes
dans la plateforme IA Influencer Agent.

Ce module fournit:
- Configuration personnalisable des intégrations par plateforme
- Profils d'intégration pour différents cas d'usage
- Health checks et monitoring des intégrations
- Gestion des capacités par plateforme
- Paramètres par défaut et templates

Auteur: Fahed Mlaiel <mlaiel@live.de>
Email: mlaiel@live.de
Équipe: Lead AI Developer, Backend Senior, Platform Integration Specialist, DevOps Engineer

⚠️  AVERTISSEMENT LEGAL ⚠️
Ce code et concept sont la propriété intellectuelle exclusive de Fahed Mlaiel.
Toute utilisation, copie, modification ou distribution sans autorisation 
écrite explicite est strictement interdite et fera l'objet de poursuites 
judiciaires selon le droit allemand et international.

Contact pour autorisation: mlaiel@live.de
"""from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, JSON, Enum as SQLEnum, Float
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from typing import Dict, List, Any, Optional, Union
import uuid
import logging
from datetime import datetime, timedelta
from enum import Enum
import json

from backend.database.models.base import BaseModel

logger = logging.getLogger(__name__)


class IntegrationSettingType(Enum):
    """Types de paramètres d'intégration."""    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    JSON = "json"
    URL = "url"
    EMAIL = "email"
    PHONE = "phone"
    PASSWORD = "password"
    API_KEY = "api_key"
    ENUM = "enum"
    ARRAY = "array"
    OBJECT = "object"


class IntegrationStatus(Enum):
    """Statuts d'intégration."""    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"
    SUSPENDED = "suspended"
    ERROR = "error"
    MAINTENANCE = "maintenance"
    DEPRECATED = "deprecated"


class CapabilityType(Enum):
    """Types de capacités des plateformes."""    READ_CONTENT = "read_content"
    WRITE_CONTENT = "write_content"
    DELETE_CONTENT = "delete_content"
    READ_ANALYTICS = "read_analytics"
    READ_PROFILE = "read_profile"
    WRITE_PROFILE = "write_profile"
    UPLOAD_MEDIA = "upload_media"
    DOWNLOAD_MEDIA = "download_media"
    STREAM_CONTENT = "stream_content"
    MONETIZATION = "monetization"
    COLLABORATION = "collaboration"
    REAL_TIME_EVENTS = "real_time_events"
    WEBHOOK_SUPPORT = "webhook_support"
    BATCH_OPERATIONS = "batch_operations"
    SEARCH = "search"
    RECOMMENDATION = "recommendation"


class PlatformIntegrationSetting(BaseModel):
    """    Modèle pour les paramètres de configuration des intégrations plateformes.
    
    Stocke les configurations personnalisables par utilisateur et par plateforme,
    avec validation et valeurs par défaut.
    """    
    __tablename__ = "platform_integration_settings"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    platform_name = Column(String(50), nullable=False, index=True)
    
    # Identification du paramètre
    setting_key = Column(String(100), nullable=False, index=True)
    setting_name = Column(String(255), nullable=False)
    setting_description = Column(Text)
    setting_type = Column(SQLEnum(IntegrationSettingType), nullable=False)
    
    # Valeur du paramètre
    setting_value = Column(JSONB)
    default_value = Column(JSONB)
    previous_value = Column(JSONB)
    
    # Validation et contraintes
    validation_rules = Column(JSONB, default=dict)
    enum_values = Column(JSONB, default=list)  # Pour les settings de type ENUM
    min_value = Column(Float)
    max_value = Column(Float)
    required = Column(Boolean, default=False)
    
    # Catégorisation
    category = Column(String(50), default="general")  # general, sync, auth, advanced, etc.
    subcategory = Column(String(50))
    display_order = Column(Integer, default=0)
    
    # Comportement
    is_sensitive = Column(Boolean, default=False)  # Si la valeur est sensible (passwords, keys)
    is_readonly = Column(Boolean, default=False)
    requires_restart = Column(Boolean, default=False)
    
    # Métadonnées
    last_modified_by = Column(UUID(as_uuid=True))
    modification_reason = Column(String(255))
    tags = Column(JSONB, default=list)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<PlatformIntegrationSetting(platform={self.platform_name}, key={self.setting_key})>"
    
    def validate_value(self, value: Any) -> bool:
        """Valide une valeur selon le type et les règles de validation."""        if self.required and (value is None or value == ""):
            return False
        
        if value is None:
            return not self.required
        
        # Validation par type
        if self.setting_type == IntegrationSettingType.STRING:
            if not isinstance(value, str):
                return False
            if self.validation_rules.get("min_length") and len(value) < self.validation_rules["min_length"]:
                return False
            if self.validation_rules.get("max_length") and len(value) > self.validation_rules["max_length"]:
                return False
            if self.validation_rules.get("pattern"):
                import re
                if not re.match(self.validation_rules["pattern"], value):
                    return False
        
        elif self.setting_type == IntegrationSettingType.INTEGER:
            if not isinstance(value, int):
                return False
            if self.min_value is not None and value < self.min_value:
                return False
            if self.max_value is not None and value > self.max_value:
                return False
        
        elif self.setting_type == IntegrationSettingType.FLOAT:
            if not isinstance(value, (int, float)):
                return False
            if self.min_value is not None and value < self.min_value:
                return False
            if self.max_value is not None and value > self.max_value:
                return False
        
        elif self.setting_type == IntegrationSettingType.BOOLEAN:
            if not isinstance(value, bool):
                return False
        
        elif self.setting_type == IntegrationSettingType.ENUM:
            if value not in self.enum_values:
                return False
        
        elif self.setting_type == IntegrationSettingType.URL:
            if not isinstance(value, str):
                return False
            # Validation URL basique
            if not value.startswith(('http://', 'https://')):
                return False
        
        elif self.setting_type == IntegrationSettingType.EMAIL:
            if not isinstance(value, str):
                return False
            import re
            if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', value):
                return False
        
        return True
    
    def set_value(self, value: Any, modified_by: str = None, reason: str = None) -> bool:
        """Définit une nouvelle valeur après validation."""        if not self.validate_value(value):
            return False
        
        self.previous_value = self.setting_value
        self.setting_value = value
        self.last_modified_by = modified_by
        self.modification_reason = reason
        self.updated_at = datetime.utcnow()
        
        return True
    
    def reset_to_default(self):
        """Remet la valeur par défaut."""        self.previous_value = self.setting_value
        self.setting_value = self.default_value
        self.updated_at = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit le setting en dictionnaire."""        return {
            "key": self.setting_key,
            "name": self.setting_name,
            "description": self.setting_description,
            "type": self.setting_type.value,
            "value": self.setting_value,
            "default_value": self.default_value,
            "category": self.category,
            "required": self.required,
            "readonly": self.is_readonly,
            "sensitive": self.is_sensitive
        }


class IntegrationProfile(BaseModel):
    """    Modèle pour les profils d'intégration prédéfinis.
    
    Permet de définir des templates de configuration
    pour différents cas d'usage et types d'utilisateurs.
    """    
    __tablename__ = "integration_profiles"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    profile_name = Column(String(100), nullable=False, unique=True)
    display_name = Column(String(255), nullable=False)
    description = Column(Text)
    
    # Cible du profil
    target_user_type = Column(String(50))  # musician, blogger, photographer, influencer, etc.
    target_platform_types = Column(JSONB, default=list)  # Types de plateformes ciblées
    target_use_cases = Column(JSONB, default=list)  # content_creation, analytics, monetization, etc.
    
    # Configuration du profil
    profile_settings = Column(JSONB, default=dict)  # Settings par plateforme
    enabled_features = Column(JSONB, default=list)
    disabled_features = Column(JSONB, default=list)
    
    # Recommandations
    recommended_platforms = Column(JSONB, default=list)
    integration_priority = Column(JSONB, default=dict)  # Priorité d'intégration par plateforme
    
    # Métadonnées
    is_default = Column(Boolean, default=False)
    is_premium = Column(Boolean, default=False)
    popularity_score = Column(Integer, default=0)
    usage_count = Column(Integer, default=0)
    
    created_by = Column(UUID(as_uuid=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<IntegrationProfile(name={self.profile_name}, type={self.target_user_type})>"
    
    def get_platform_settings(self, platform_name: str) -> Dict[str, Any]:
        """Récupère les settings pour une plateforme spécifique."""        return self.profile_settings.get(platform_name, {})
    
    def is_compatible_with_user(self, user_type: str, platforms: List[str]) -> bool:
        """Vérifie si le profil est compatible avec un utilisateur."""        if self.target_user_type and self.target_user_type != user_type:
            return False
        
        if self.target_platform_types:
            # Vérifie si au moins une plateforme correspond
            for platform in platforms:
                # Cette logique devrait être enrichie avec un mapping plateforme -> type
                if any(pt in platform.lower() for pt in self.target_platform_types):
                    return True
            return False
        
        return True


class PlatformCapability(BaseModel):
    """    Modèle pour les capacités disponibles par plateforme.
    
    Définit quelles fonctionnalités sont supportées
    par chaque plateforme et leurs limitations.
    """    
    __tablename__ = "platform_capabilities"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    platform_name = Column(String(50), nullable=False, index=True)
    capability_type = Column(SQLEnum(CapabilityType), nullable=False, index=True)
    
    # Informations sur la capacité
    capability_name = Column(String(100), nullable=False)
    capability_description = Column(Text)
    
    # Disponibilité
    is_available = Column(Boolean, default=True)
    is_beta = Column(Boolean, default=False)
    is_deprecated = Column(Boolean, default=False)
    deprecation_date = Column(DateTime(timezone=True))
    
    # Limitations
    rate_limits = Column(JSONB, default=dict)
    size_limits = Column(JSONB, default=dict)
    format_restrictions = Column(JSONB, default=list)
    
    # Prérequis
    required_scopes = Column(JSONB, default=list)
    required_plan = Column(String(50))  # free, basic, premium, enterprise
    required_verification = Column(Boolean, default=False)
    
    # Métadonnées de support
    api_endpoints = Column(JSONB, default=list)
    documentation_url = Column(Text)
    examples = Column(JSONB, default=list)
    
    # Métriques
    success_rate = Column(Float, default=100.0)
    average_response_time = Column(Integer, default=0)  # ms
    last_tested = Column(DateTime(timezone=True))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<PlatformCapability(platform={self.platform_name}, capability={self.capability_type.value})>"
    
    def is_functional(self) -> bool:
        """Vérifie si la capacité est fonctionnelle."""        return (
            self.is_available and 
            not self.is_deprecated and 
            self.success_rate > 50.0
        )


class IntegrationHealthCheck(BaseModel):
    """    Modèle pour les vérifications de santé des intégrations.
    
    Enregistre les résultats des tests de connectivité
    et de fonctionnement des intégrations.
    """    
    __tablename__ = "integration_health_checks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    platform_name = Column(String(50), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), index=True)  # Null pour les checks système
    
    # Type de vérification
    check_type = Column(String(50), nullable=False)  # connectivity, auth, permissions, functionality
    check_category = Column(String(50), default="system")  # system, user, automated, manual
    
    # Résultats du check
    check_status = Column(String(20), nullable=False, index=True)  # success, warning, error, critical
    response_time_ms = Column(Integer)
    
    # Détails
    checks_performed = Column(JSONB, default=list)
    successful_checks = Column(Integer, default=0)
    failed_checks = Column(Integer, default=0)
    warning_checks = Column(Integer, default=0)
    
    # Messages et erreurs
    summary_message = Column(Text)
    error_details = Column(JSONB, default=dict)
    warnings = Column(JSONB, default=list)
    recommendations = Column(JSONB, default=list)
    
    # Contexte
    triggered_by = Column(String(50))  # system, user, monitor, schedule
    check_configuration = Column(JSONB, default=dict)
    
    # Timing
    started_at = Column(DateTime(timezone=True), nullable=False)
    completed_at = Column(DateTime(timezone=True))
    next_check_at = Column(DateTime(timezone=True))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<IntegrationHealthCheck(platform={self.platform_name}, status={self.check_status})>"
    
    @property
    def duration_ms(self) -> int:
        """Calcule la durée du check en millisecondes."""        if not self.completed_at or not self.started_at:
            return 0
        
        duration = self.completed_at - self.started_at
        return int(duration.total_seconds() * 1000)
    
    @property
    def success_rate(self) -> float:
        """Calcule le taux de succès du check."""        total_checks = self.successful_checks + self.failed_checks + self.warning_checks
        if total_checks == 0:
            return 100.0
        
        return (self.successful_checks / total_checks) * 100


# Paramètres par défaut pour chaque plateforme
DEFAULT_PLATFORM_SETTINGS = {
    "spotify": {
        "sync_frequency": "daily",
        "auto_sync_enabled": True,
        "include_private_playlists": False,
        "include_saved_tracks": True,
        "include_followed_artists": True,
        "include_recently_played": True,
        "max_tracks_per_sync": 1000,
        "notification_enabled": True,
        "backup_enabled": True
    },
    "youtube": {
        "sync_frequency": "daily",
        "auto_sync_enabled": True,
        "include_uploads": True,
        "include_liked_videos": True,
        "include_playlists": True,
        "include_subscriptions": False,
        "max_videos_per_sync": 500,
        "quality_preference": "hd720",
        "thumbnail_download": True,
        "metadata_extraction": True
    },
    "instagram": {
        "sync_frequency": "hourly",
        "auto_sync_enabled": True,
        "include_posts": True,
        "include_stories": False,
        "include_reels": True,
        "include_igtv": True,
        "max_posts_per_sync": 100,
        "download_media": True,
        "extract_hashtags": True,
        "analyze_engagement": True
    },
    "tiktok": {
        "sync_frequency": "hourly",
        "auto_sync_enabled": True,
        "include_videos": True,
        "include_likes": False,
        "max_videos_per_sync": 50,
        "download_videos": False,
        "extract_sounds": True,
        "analyze_trends": True
    },
    "twitter": {
        "sync_frequency": "realtime",
        "auto_sync_enabled": True,
        "include_tweets": True,
        "include_likes": False,
        "include_retweets": True,
        "include_mentions": True,
        "max_tweets_per_sync": 200,
        "sentiment_analysis": True,
        "trend_tracking": True
    }
}


def create_default_settings_for_platform(
    user_id: str,
    platform_name: str
) -> List[PlatformIntegrationSetting]:
    """    Crée les paramètres par défaut pour une plateforme et un utilisateur.
    
    Args:
        user_id: ID de l'utilisateur
        platform_name: Nom de la plateforme
        
    Returns:
        Liste des settings créés
    """    if platform_name not in DEFAULT_PLATFORM_SETTINGS:
        raise ValueError(f"No default settings defined for platform: {platform_name}")
    
    default_settings = DEFAULT_PLATFORM_SETTINGS[platform_name]
    settings = []
    
    for key, value in default_settings.items():
        # Détermine le type de setting
        if isinstance(value, bool):
            setting_type = IntegrationSettingType.BOOLEAN
        elif isinstance(value, int):
            setting_type = IntegrationSettingType.INTEGER
        elif isinstance(value, float):
            setting_type = IntegrationSettingType.FLOAT
        elif isinstance(value, str):
            setting_type = IntegrationSettingType.STRING
        else:
            setting_type = IntegrationSettingType.JSON
        
        setting = PlatformIntegrationSetting(
            user_id=user_id,
            platform_name=platform_name,
            setting_key=key,
            setting_name=key.replace('_', ' ').title(),
            setting_type=setting_type,
            setting_value=value,
            default_value=value
        )
        
        settings.append(setting)
    
    return settings

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Float
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from typing import Dict, List, Any, Optional, Union
import uuid
import json
import logging
from datetime import datetime, timedelta
from enum import Enum

from backend.database.models.base import BaseModel

logger = logging.getLogger(__name__)


class IntegrationSettingType(str, Enum):
    """Types de paramètres d'intégration."""    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    JSON = "json"
    ARRAY = "array"
    SECRET = "secret"


class IntegrationStatus(str, Enum):
    """Statuts d'intégration."""    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"
    ERROR = "error"
    MAINTENANCE = "maintenance"
    DEPRECATED = "deprecated"


class PlatformIntegrationSetting(BaseModel):
    """    Modèle pour les paramètres d'intégration des plateformes.
    
    Stocke la configuration personnalisable pour chaque intégration
    de plateforme par utilisateur ou globalement.
    """    
    __tablename__ = "platform_integration_settings"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), index=True)  # NULL pour paramètres globaux
    platform_name = Column(String(50), nullable=False, index=True)
    
    # Identification du paramètre
    setting_key = Column(String(100), nullable=False, index=True)
    setting_category = Column(String(50), nullable=False)  # sync, content, analytics, etc.
    setting_type = Column(String(20), nullable=False)
    
    # Valeurs du paramètre
    string_value = Column(Text)
    integer_value = Column(Integer)
    float_value = Column(Float)
    boolean_value = Column(Boolean)
    json_value = Column(JSONB)
    
    # Métadonnées du paramètre
    display_name = Column(String(255))
    description = Column(Text)
    is_required = Column(Boolean, default=False)
    is_user_configurable = Column(Boolean, default=True)
    
    # Validation
    validation_rules = Column(JSONB, default=dict)
    default_value = Column(Text)
    
    # Statut
    is_active = Column(Boolean, default=True)
    is_sensitive = Column(Boolean, default=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<PlatformIntegrationSetting(platform={self.platform_name}, key={self.setting_key})>"
    
    def get_value(self) -> Union[str, int, float, bool, dict, list]:
        """Récupère la valeur du paramètre selon son type."""        if self.setting_type == IntegrationSettingType.STRING:
            return self.string_value
        elif self.setting_type == IntegrationSettingType.INTEGER:
            return self.integer_value
        elif self.setting_type == IntegrationSettingType.FLOAT:
            return self.float_value
        elif self.setting_type == IntegrationSettingType.BOOLEAN:
            return self.boolean_value
        elif self.setting_type in [IntegrationSettingType.JSON, IntegrationSettingType.ARRAY]:
            return self.json_value
        else:
            return self.string_value
    
    def set_value(self, value: Union[str, int, float, bool, dict, list]):
        """Définit la valeur du paramètre selon son type."""        # Réinitialise toutes les valeurs
        self.string_value = None
        self.integer_value = None
        self.float_value = None
        self.boolean_value = None
        self.json_value = None
        
        if self.setting_type == IntegrationSettingType.STRING:
            self.string_value = str(value)
        elif self.setting_type == IntegrationSettingType.INTEGER:
            self.integer_value = int(value)
        elif self.setting_type == IntegrationSettingType.FLOAT:
            self.float_value = float(value)
        elif self.setting_type == IntegrationSettingType.BOOLEAN:
            self.boolean_value = bool(value)
        elif self.setting_type in [IntegrationSettingType.JSON, IntegrationSettingType.ARRAY]:
            self.json_value = value if isinstance(value, (dict, list)) else json.loads(value)
        else:
            self.string_value = str(value)
    
    def validate_value(self) -> bool:
        """Valide la valeur selon les règles définies."""        if not self.validation_rules:
            return True
        
        value = self.get_value()
        rules = self.validation_rules
        
        # Validation de type
        if "type" in rules and type(value).__name__ != rules["type"]:
            return False
        
        # Validation de plage pour les nombres
        if isinstance(value, (int, float)):
            if "min" in rules and value < rules["min"]:
                return False
            if "max" in rules and value > rules["max"]:
                return False
        
        # Validation de longueur pour les chaînes
        if isinstance(value, str):
            if "min_length" in rules and len(value) < rules["min_length"]:
                return False
            if "max_length" in rules and len(value) > rules["max_length"]:
                return False
            if "pattern" in rules:
                import re
                if not re.match(rules["pattern"], value):
                    return False
        
        # Validation de valeurs autorisées
        if "allowed_values" in rules and value not in rules["allowed_values"]:
            return False
        
        return True


class IntegrationProfile(BaseModel):
    """    Modèle pour les profils d'intégration.
    
    Groupe de paramètres prédéfinis pour différents cas d'usage
    ou types d'utilisateurs.
    """    
    __tablename__ = "integration_profiles"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    profile_name = Column(String(100), nullable=False, unique=True)
    platform_name = Column(String(50), nullable=False, index=True)
    
    # Description du profil
    display_name = Column(String(255))
    description = Column(Text)
    target_audience = Column(String(100))  # beginner, advanced, enterprise
    
    # Configuration du profil
    settings_template = Column(JSONB, nullable=False)
    is_default = Column(Boolean, default=False)
    is_recommended = Column(Boolean, default=False)
    
    # Métadonnées
    usage_count = Column(Integer, default=0)
    success_rate = Column(Float, default=0.0)
    
    # Statut
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<IntegrationProfile(name={self.profile_name}, platform={self.platform_name})>"
    
    def apply_to_user(self, user_id: str) -> List[PlatformIntegrationSetting]:
        """Applique ce profil à un utilisateur spécifique."""        settings = []
        
        for setting_key, setting_config in self.settings_template.items():
            setting = PlatformIntegrationSetting(
                user_id=user_id,
                platform_name=self.platform_name,
                setting_key=setting_key,
                setting_category=setting_config.get("category", "general"),
                setting_type=setting_config.get("type", "string")
            )
            setting.set_value(setting_config.get("value"))
            settings.append(setting)
        
        return settings


class PlatformCapability(BaseModel):
    """    Modèle pour les capacités des plateformes.
    
    Définit les fonctionnalités disponibles et leurs limitations
    pour chaque plateforme intégrée.
    """    
    __tablename__ = "platform_capabilities"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    platform_name = Column(String(50), nullable=False, index=True)
    
    # Identification de la capacité
    capability_name = Column(String(100), nullable=False)
    capability_category = Column(String(50), nullable=False)  # content, analytics, user_management
    
    # Description
    display_name = Column(String(255))
    description = Column(Text)
    
    # Disponibilité
    is_available = Column(Boolean, default=True)
    requires_premium = Column(Boolean, default=False)
    minimum_api_version = Column(String(20))
    
    # Limitations
    rate_limits = Column(JSONB, default=dict)
    data_limits = Column(JSONB, default=dict)
    feature_restrictions = Column(JSONB, default=dict)
    
    # Formats supportés
    supported_content_types = Column(JSONB, default=list)
    supported_file_formats = Column(JSONB, default=list)
    
    # Configuration technique
    endpoint_mapping = Column(JSONB, default=dict)
    required_scopes = Column(JSONB, default=list)
    
    # Statut
    is_beta = Column(Boolean, default=False)
    is_deprecated = Column(Boolean, default=False)
    deprecation_date = Column(DateTime(timezone=True))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<PlatformCapability(platform={self.platform_name}, capability={self.capability_name})>"
    
    def is_supported_for_user(self, user_tier: str = "free") -> bool:
        """Vérifie si la capacité est supportée pour un niveau d'utilisateur."""        if not self.is_available:
            return False
        
        if self.requires_premium and user_tier == "free":
            return False
        
        if self.is_deprecated:
            return False
        
        return True


class IntegrationHealthCheck(BaseModel):
    """    Modèle pour les vérifications de santé des intégrations.
    
    Stocke les résultats des tests de connectivité et de performance
    pour chaque intégration.
    """    
    __tablename__ = "integration_health_checks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    platform_name = Column(String(50), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), index=True)  # NULL pour vérifications globales
    
    # Type de vérification
    check_type = Column(String(50), nullable=False)  # connectivity, performance, quota, auth
    check_name = Column(String(100), nullable=False)
    
    # Résultats
    status = Column(String(20), nullable=False)  # healthy, warning, critical, unknown
    success = Column(Boolean, nullable=False)
    
    # Métriques
    response_time_ms = Column(Integer)
    error_count = Column(Integer, default=0)
    warning_count = Column(Integer, default=0)
    
    # Détails
    check_details = Column(JSONB, default=dict)
    error_message = Column(Text)
    recommendations = Column(JSONB, default=list)
    
    # Métadonnées
    check_metadata = Column(JSONB, default=dict)
    
    # Timing
    check_started = Column(DateTime(timezone=True), nullable=False)
    check_completed = Column(DateTime(timezone=True), nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<IntegrationHealthCheck(platform={self.platform_name}, type={self.check_type}, status={self.status})>"
    
    @property
    def duration_ms(self) -> int:
        """Calcule la durée de la vérification en millisecondes."""        if not self.check_completed or not self.check_started:
            return 0
        
        delta = self.check_completed - self.check_started
        return int(delta.total_seconds() * 1000)
    
    def get_health_score(self) -> float:
        """Calcule un score de santé (0-100) basé sur les résultats."""        base_score = 100.0 if self.success else 0.0
        
        # Pénalités pour les warnings et erreurs
        if self.warning_count > 0:
            base_score -= min(20.0, self.warning_count * 5)
        
        if self.error_count > 0:
            base_score -= min(50.0, self.error_count * 10)
        
        # Pénalité pour la performance
        if self.response_time_ms and self.response_time_ms > 5000:  # > 5 secondes
            base_score -= 20.0
        elif self.response_time_ms and self.response_time_ms > 2000:  # > 2 secondes
            base_score -= 10.0
        
        return max(0.0, min(100.0, base_score))


# Configuration par défaut des paramètres par plateforme
DEFAULT_PLATFORM_SETTINGS = {
    "spotify": {
        "sync_frequency": {
            "type": "string",
            "default": "daily",
            "category": "sync",
            "allowed_values": ["realtime", "hourly", "daily", "weekly"],
            "description": "Fréquence de synchronisation des données"
        },
        "auto_playlist_sync": {
            "type": "boolean",
            "default": True,
            "category": "content",
            "description": "Synchronisation automatique des playlists"
        },
        "analytics_retention_days": {
            "type": "integer",
            "default": 365,
            "category": "analytics",
            "min": 30,
            "max": 730,
            "description": "Durée de rétention des analytics en jours"
        }
    },
    "youtube": {
        "video_quality_preference": {
            "type": "string",
            "default": "1080p",
            "category": "content",
            "allowed_values": ["720p", "1080p", "1440p", "2160p"],
            "description": "Qualité vidéo préférée pour les uploads"
        },
        "auto_thumbnail_generation": {
            "type": "boolean",
            "default": True,
            "category": "content",
            "description": "Génération automatique de thumbnails"
        },
        "comment_moderation": {
            "type": "string",
            "default": "automatic",
            "category": "moderation",
            "allowed_values": ["none", "automatic", "manual"],
            "description": "Mode de modération des commentaires"
        }
    },
    "instagram": {
        "story_auto_archive": {
            "type": "boolean",
            "default": True,
            "category": "content",
            "description": "Archivage automatique des stories"
        },
        "hashtag_suggestions": {
            "type": "boolean",
            "default": True,
            "category": "content",
            "description": "Suggestions automatiques de hashtags"
        },
        "engagement_tracking": {
            "type": "boolean",
            "default": True,
            "category": "analytics",
            "description": "Suivi de l'engagement sur les posts"
        }
    }
}


def create_default_settings_for_platform(platform_name: str, user_id: str = None) -> List[PlatformIntegrationSetting]:
    """    Crée les paramètres par défaut pour une plateforme.
    
    Args:
        platform_name: Nom de la plateforme
        user_id: ID de l'utilisateur (optionnel pour paramètres globaux)
    
    Returns:
        List[PlatformIntegrationSetting]: Liste des paramètres créés
    """    if platform_name not in DEFAULT_PLATFORM_SETTINGS:
        return []
    
    settings = []
    platform_config = DEFAULT_PLATFORM_SETTINGS[platform_name]
    
    for setting_key, setting_config in platform_config.items():
        setting = PlatformIntegrationSetting(
            user_id=user_id,
            platform_name=platform_name,
            setting_key=setting_key,
            setting_category=setting_config.get("category", "general"),
            setting_type=setting_config.get("type", "string"),
            description=setting_config.get("description"),
            validation_rules={
                k: v for k, v in setting_config.items() 
                if k in ["min", "max", "allowed_values", "pattern", "min_length", "max_length"]
            }
        )
        
        setting.set_value(setting_config.get("default"))
        settings.append(setting)
    
    return settings


# Index pour optimisation des performances
from sqlalchemy import Index

platform_integration_setting_user_platform_idx = Index(
    'idx_platform_integration_settings_user_platform',
    PlatformIntegrationSetting.user_id,
    PlatformIntegrationSetting.platform_name
)

platform_capability_platform_available_idx = Index(
    'idx_platform_capabilities_platform_available',
    PlatformCapability.platform_name,
    PlatformCapability.is_available
)

integration_health_check_platform_status_idx = Index(
    'idx_integration_health_checks_platform_status',
    IntegrationHealthCheck.platform_name,
    IntegrationHealthCheck.status
)
