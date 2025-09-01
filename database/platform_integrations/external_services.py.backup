"""External Services Management Module

Gestion des services externes et APIs tierces pour les intégrations plateformes
dans la plateforme IA Influencer Agent.

Ce module fournit:
- Catalogue complet des services externes disponibles
- Configuration et endpoints des APIs tierces
- Gestion des dépendances entre services
- Analytics d'utilisation et monitoring
- Templates d'intégration prêts à l'emploi

Auteur: Fahed Mlaiel <mlaiel@live.de>
Email: mlaiel@live.de
Équipe: Lead AI Developer, Backend Senior, Platform Integration Specialist, DevOps Engineer

⚠️  AVERTISSEMENT LEGAL ⚠️
Ce code et concept sont la propriété intellectuelle exclusive de Fahed Mlaiel.
Toute utilisation, copie, modification ou distribution sans autorisation 
écrite explicite est strictement interdite et fera l'objet de poursuites 
judiciaires selon le droit allemand et international.

Contact pour autorisation: mlaiel@live.de
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, JSON, Enum as SQLEnum, Float
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


class ServiceType(Enum):
    """Types de services externes."""
    SOCIAL_MEDIA_API = "social_media_api"
    MUSIC_STREAMING_API = "music_streaming_api"
    VIDEO_PLATFORM_API = "video_platform_api"
    BLOGGING_PLATFORM_API = "blogging_platform_api"
    ANALYTICS_SERVICE = "analytics_service"
    AI_ML_SERVICE = "ai_ml_service"
    CONTENT_DELIVERY = "content_delivery"
    PAYMENT_GATEWAY = "payment_gateway"
    AUTHENTICATION = "authentication"
    STORAGE_SERVICE = "storage_service"
    NOTIFICATION_SERVICE = "notification_service"
    SEARCH_ENGINE = "search_engine"
    MONITORING_SERVICE = "monitoring_service"
    EMAIL_SERVICE = "email_service"
    SMS_SERVICE = "sms_service"
    WEBHOOK_SERVICE = "webhook_service"
    DATA_ENRICHMENT = "data_enrichment"
    TRANSLATION_SERVICE = "translation_service"
    IMAGE_PROCESSING = "image_processing"
    AUDIO_PROCESSING = "audio_processing"


class ServiceStatus(Enum):
    """Statuts des services externes."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"
    DEPRECATED = "deprecated"
    BETA = "beta"
    ALPHA = "alpha"
    SUSPENDED = "suspended"
    ERROR = "error"
    RATE_LIMITED = "rate_limited"


class IntegrationComplexity(Enum):
    """Niveaux de complexité d'intégration."""
    SIMPLE = "simple"  # Configuration minimale
    MODERATE = "moderate"  # Configuration standard
    COMPLEX = "complex"  # Configuration avancée
    EXPERT = "expert"  # Configuration experte


class ExternalService(BaseModel):
    """
    Modèle pour les services externes disponibles.
    
    Catalogue complet des services tiers avec leurs
    configurations, capacités et métadonnées.
    """
    
    __tablename__ = "external_services"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    service_name = Column(String(100), nullable=False, unique=True, index=True)
    display_name = Column(String(255), nullable=False)
    service_type = Column(SQLEnum(ServiceType), nullable=False, index=True)
    service_status = Column(SQLEnum(ServiceStatus), default=ServiceStatus.ACTIVE, index=True)
    
    # Informations générales
    description = Column(Text)
    provider_name = Column(String(100), nullable=False)
    provider_website = Column(String(500))
    service_website = Column(String(500))
    
    # Documentation et support
    documentation_url = Column(String(500))
    api_documentation_url = Column(String(500))
    support_url = Column(String(500))
    status_page_url = Column(String(500))
    
    # Configuration d'intégration
    integration_complexity = Column(SQLEnum(IntegrationComplexity), default=IntegrationComplexity.MODERATE)
    setup_time_minutes = Column(Integer, default=30)
    requires_approval = Column(Boolean, default=False)
    requires_payment = Column(Boolean, default=False)
    
    # Capacités et limitations
    supported_features = Column(JSONB, default=list)
    supported_regions = Column(JSONB, default=list)
    supported_languages = Column(JSONB, default=list)
    data_retention_days = Column(Integer)
    
    # Rate limiting par défaut
    default_rate_limits = Column(JSONB, default=dict)
    burst_rate_limits = Column(JSONB, default=dict)
    quota_limits = Column(JSONB, default=dict)
    
    # Pricing et plans
    pricing_model = Column(String(50))  # free, freemium, paid, usage_based, subscription
    free_tier_limits = Column(JSONB, default=dict)
    paid_plans = Column(JSONB, default=list)
    
    # Métriques de fiabilité
    uptime_percentage = Column(Float, default=99.9)
    average_response_time_ms = Column(Integer, default=200)
    error_rate_percentage = Column(Float, default=0.1)
    
    # Sécurité
    security_features = Column(JSONB, default=list)
    compliance_certifications = Column(JSONB, default=list)
    data_encryption = Column(Boolean, default=True)
    
    # Configuration technique
    base_url = Column(String(500))
    api_version = Column(String(20), default="v1")
    auth_methods = Column(JSONB, default=list)  # api_key, oauth2, basic_auth, etc.
    content_types = Column(JSONB, default=["application/json"])
    
    # Monitoring
    last_health_check = Column(DateTime(timezone=True))
    health_check_interval = Column(Integer, default=300)  # secondes
    is_healthy = Column(Boolean, default=True)
    
    # Métadonnées
    tags = Column(JSONB, default=list)
    categories = Column(JSONB, default=list)
    popularity_score = Column(Integer, default=0)
    recommendation_score = Column(Float, default=0.0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<ExternalService(name={self.service_name}, type={self.service_type.value})>"


# Catalogue des services externes supportés
EXTERNAL_SERVICES_CATALOG = {
    "spotify_web_api": {
        "service_name": "spotify_web_api",
        "display_name": "Spotify Web API",
        "service_type": ServiceType.MUSIC_STREAMING_API,
        "provider_name": "Spotify",
        "description": "Access to Spotify's music catalog and user data",
        "documentation_url": "https://developer.spotify.com/documentation/web-api/",
        "base_url": "https://api.spotify.com/v1",
        "auth_methods": ["oauth2"],
        "supported_features": ["user_profile", "playlists", "tracks", "artists", "albums", "search"],
        "free_tier_limits": {"requests_per_hour": 1000},
        "integration_complexity": IntegrationComplexity.MODERATE
    },
    "youtube_data_api": {
        "service_name": "youtube_data_api",
        "display_name": "YouTube Data API v3",
        "service_type": ServiceType.VIDEO_PLATFORM_API,
        "provider_name": "Google",
        "description": "Access to YouTube videos, channels, and playlists",
        "documentation_url": "https://developers.google.com/youtube/v3",
        "base_url": "https://www.googleapis.com/youtube/v3",
        "auth_methods": ["api_key", "oauth2"],
        "supported_features": ["videos", "channels", "playlists", "search", "analytics"],
        "free_tier_limits": {"quota_units_per_day": 10000},
        "integration_complexity": IntegrationComplexity.MODERATE
    }
}


def create_external_service_from_catalog(catalog_key: str) -> ExternalService:
    """
    Crée une instance ExternalService à partir du catalogue.
    
    Args:
        catalog_key: Clé du service dans le catalogue
        
    Returns:
        Instance d'ExternalService
        
    Raises:
        ValueError: Si le service n'existe pas dans le catalogue
    """
    if catalog_key not in EXTERNAL_SERVICES_CATALOG:
        raise ValueError(f"Service '{catalog_key}' not found in catalog")
    
    config = EXTERNAL_SERVICES_CATALOG[catalog_key]
    
    service = ExternalService(
        service_name=config["service_name"],
        display_name=config["display_name"],
        service_type=config["service_type"],
        provider_name=config["provider_name"],
        description=config["description"],
        documentation_url=config.get("documentation_url"),
        base_url=config.get("base_url"),
        auth_methods=config.get("auth_methods", []),
        supported_features=config.get("supported_features", []),
        free_tier_limits=config.get("free_tier_limits", {}),
        integration_complexity=config.get("integration_complexity", IntegrationComplexity.MODERATE),
        pricing_model=config.get("pricing_model", "freemium")
    )
    
    return service


def get_services_by_type(service_type: ServiceType) -> List[str]:
    """
    Retourne la liste des services par type.
    
    Args:
        service_type: Type de service recherché
        
    Returns:
        Liste des noms de services
    """
    return [
        key for key, config in EXTERNAL_SERVICES_CATALOG.items()
        if config["service_type"] == service_type
    ]
