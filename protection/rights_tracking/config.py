"""Rights Tracking Configuration - Enterprise Configuration Management System
Configuration centralisée ultra-avancée pour le module de suivi des droits
Système professionnel de gestion des paramètres et constantes

Auteur: Fahed Mlaiel - Lead Developer & AI Architect
Email: mlaiel@live.de
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + IA Prompt Engineer
Copyright: Tous droits réservés (c) 2025 Fahed Mlaiel

AVERTISSEMENT LÉGAL STRICT:
Ce code, concept et propriété intellectuelle appartiennent exclusivement à Fahed Mlaiel.
Toute tentative de vol, copie, redistribution ou utilisation sans autorisation écrite 
explicite de Fahed Mlaiel (mlaiel@live.de) entraînera des actions légales immédiates 
selon le droit allemand et international de la propriété intellectuelle.
"""

import os
from typing import Dict, List, Any, Optional
from enum import Enum
from dataclasses import dataclass
from pydantic import BaseSettings, Field


class RightsTrackingConfig(BaseSettings):
    """
Configuration principale du système de suivi des droits"""
    
    # === Configuration Base de Données ===
    DATABASE_URL: str = Field(
        default="postgresql://user:password@localhost:5432/rights_tracking",
        env="RIGHTS_TRACKING_DATABASE_URL"
    )
    DATABASE_POOL_SIZE: int = Field(default=20, env="DATABASE_POOL_SIZE")
    DATABASE_MAX_OVERFLOW: int = Field(default=30, env="DATABASE_MAX_OVERFLOW")
    DATABASE_POOL_TIMEOUT: int = Field(default=30, env="DATABASE_POOL_TIMEOUT")
    DATABASE_POOL_RECYCLE: int = Field(default=3600, env="DATABASE_POOL_RECYCLE")
    
    # === Configuration Redis ===
    REDIS_URL: str = Field(
        default="redis://localhost:6379/0",
        env="RIGHTS_TRACKING_REDIS_URL"
    )
    REDIS_CACHE_TTL: int = Field(default=3600, env="REDIS_CACHE_TTL")  # 1 heure
    REDIS_SESSION_TTL: int = Field(default=86400, env="REDIS_SESSION_TTL")  # 24 heures
    
    # === Configuration Sécurité ===
    SECRET_KEY: str = Field(
        default="your-secret-key-here-change-in-production",
        env="RIGHTS_TRACKING_SECRET_KEY"
    )
    ENCRYPTION_KEY: str = Field(
        default="your-encryption-key-here-32-bytes-long",
        env="RIGHTS_TRACKING_ENCRYPTION_KEY"
    )
    JWT_ALGORITHM: str = Field(default="HS256", env="JWT_ALGORITHM")
    JWT_EXPIRATION_HOURS: int = Field(default=24, env="JWT_EXPIRATION_HOURS")
    
    # === Configuration Blockchain ===
    BLOCKCHAIN_ENABLED: bool = Field(default=False, env="BLOCKCHAIN_ENABLED")
    BLOCKCHAIN_NETWORK: str = Field(default="ethereum", env="BLOCKCHAIN_NETWORK")
    BLOCKCHAIN_RPC_URL: str = Field(default="", env="BLOCKCHAIN_RPC_URL")
    BLOCKCHAIN_PRIVATE_KEY: str = Field(default="", env="BLOCKCHAIN_PRIVATE_KEY")
    SMART_CONTRACT_ADDRESS: str = Field(default="", env="SMART_CONTRACT_ADDRESS")
    
    # === Configuration API Externes ===
    YOUTUBE_API_KEY: str = Field(default="", env="YOUTUBE_API_KEY")
    TIKTOK_API_KEY: str = Field(default="", env="TIKTOK_API_KEY")
    INSTAGRAM_API_KEY: str = Field(default="", env="INSTAGRAM_API_KEY")
    TWITTER_API_KEY: str = Field(default="", env="TWITTER_API_KEY")
    FACEBOOK_API_KEY: str = Field(default="", env="FACEBOOK_API_KEY")
    
    # === Configuration IA et ML ===
    AI_DETECTION_ENABLED: bool = Field(default=True, env="AI_DETECTION_ENABLED")
    AI_MODEL_PATH: str = Field(default="/models/content_detection", env="AI_MODEL_PATH")
    AI_CONFIDENCE_THRESHOLD: float = Field(default=0.85, env="AI_CONFIDENCE_THRESHOLD")
    SIMILARITY_THRESHOLD: float = Field(default=0.80, env="SIMILARITY_THRESHOLD")
    
    # === Configuration Monitoring ===
    MONITORING_ENABLED: bool = Field(default=True, env="MONITORING_ENABLED")
    MONITORING_INTERVAL_SECONDS: int = Field(default=300, env="MONITORING_INTERVAL_SECONDS")  # 5 minutes
    ALERT_WEBHOOK_URL: str = Field(default="", env="ALERT_WEBHOOK_URL")
    NOTIFICATION_EMAIL_ENABLED: bool = Field(default=True, env="NOTIFICATION_EMAIL_ENABLED")
    
    # === Configuration Performance ===
    MAX_CONCURRENT_SCANS: int = Field(default=50, env="MAX_CONCURRENT_SCANS")
    BATCH_PROCESSING_SIZE: int = Field(default=100, env="BATCH_PROCESSING_SIZE")
    RATE_LIMIT_PER_MINUTE: int = Field(default=1000, env="RATE_LIMIT_PER_MINUTE")
    CACHE_ENABLED: bool = Field(default=True, env="CACHE_ENABLED")
    
    class Config:
    """Config: class implementation"""
        env_file = ".env"
        case_sensitive = True


# Énumérations pour les types de données
class LicenseType(str, Enum):
    """Types de licences disponibles"""

    EXCLUSIVE = "exclusive"
    NON_EXCLUSIVE = "non_exclusive"
    SYNC = "sync"
    MASTER = "master"
    MECHANICAL = "mechanical"
    PERFORMANCE = "performance"
    DIGITAL = "digital"
    CUSTOM = "custom"


class ContentType(str, Enum):
    """Types de contenu supportés"""

    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"
    MULTIMEDIA = "multimedia"
    PODCAST = "podcast"
    LIVESTREAM = "livestream"
    INTERACTIVE = "interactive"


class ViolationType(str, Enum):
    """Types de violations détectées"""

    UNAUTHORIZED_USE = "unauthorized_use"
    COPYRIGHT_INFRINGEMENT = "copyright_infringement"
    TRADEMARK_VIOLATION = "trademark_violation"
    LICENSE_BREACH = "license_breach"
    TERRITORY_VIOLATION = "territory_violation"
    USAGE_QUOTA_EXCEEDED = "usage_quota_exceeded"
    ATTRIBUTION_MISSING = "attribution_missing"
    COMMERCIAL_USE_VIOLATION = "commercial_use_violation"


class Platform(str, Enum):
    """Plateformes de surveillance supportées"""

    YOUTUBE = "youtube"
    TIKTOK = "tiktok"
    INSTAGRAM = "instagram"
    FACEBOOK = "facebook"
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    SNAPCHAT = "snapchat"
    TWITCH = "twitch"
    SPOTIFY = "spotify"
    APPLE_MUSIC = "apple_music"
    DEEZER = "deezer"
    SOUNDCLOUD = "soundcloud"


class ActionType(str, Enum):
    """Types d'actions d'enforcement"""

    DMCA_TAKEDOWN = "dmca_takedown"
    CEASE_DESIST = "cease_desist"
    PLATFORM_REPORT = "platform_report"
    LEGAL_ACTION = "legal_action"
    MONETIZATION_CLAIM = "monetization_claim"
    LICENSE_NEGOTIATION = "license_negotiation"
    WARNING_NOTICE = "warning_notice"


class Currency(str, Enum):
    """Devises supportées"""

    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
    CAD = "CAD"
    AUD = "AUD"
    JPY = "JPY"
    CHF = "CHF"
    CNY = "CNY"
    KRW = "KRW"
    BRL = "BRL"
    INR = "INR"
    BTC = "BTC"  # Bitcoin
    ETH = "ETH"  # Ethereum


class TerritoryCode(str, Enum):
    """Codes de territoires ISO 3166-1"""

    WORLDWIDE = "WW"
    US = "US"
    CA = "CA"
    MX = "MX"
    BR = "BR"
    GB = "GB"
    FR = "FR"
    DE = "DE"
    IT = "IT"
    ES = "ES"
    NL = "NL"
    BE = "BE"
    CH = "CH"
    AT = "AT"
    SE = "SE"
    NO = "NO"
    DK = "DK"
    FI = "FI"
    AU = "AU"
    NZ = "NZ"
    JP = "JP"
    KR = "KR"
    CN = "CN"
    IN = "IN"
    SG = "SG"
    HK = "HK"
    TW = "TW"
    TH = "TH"
    PH = "PH"
    ID = "ID"
    MY = "MY"
    VN = "VN"
    RU = "RU"
    UA = "UA"
    PL = "PL"
    CZ = "CZ"
    HU = "HU"
    RO = "RO"
    BG = "BG"
    HR = "HR"
    SI = "SI"
    SK = "SK"
    LT = "LT"
    LV = "LV"
    EE = "EE"
    ZA = "ZA"
    NG = "NG"
    EG = "EG"
    MA = "MA"
    KE = "KE"
    GH = "GH"
    AR = "AR"
    CL = "CL"
    CO = "CO"
    PE = "PE"
    UY = "UY"
    VE = "VE"
    EC = "EC"
    BO = "BO"
    PY = "PY"


@dataclass
class PlatformConfig:
    """Configuration pour une plateforme spécifique"""
    name: str
    api_endpoint: str
    api_key_required: bool
    rate_limit_per_hour: int
    supports_automated_takedown: bool
    supports_monetization_claims: bool
    detection_capabilities: List[str]
    response_time_sla_hours: int
    cost_per_api_call: float = 0.0


@dataclass
class AIModelConfig:
    """
Configuration pour les modèles d'IA"""
    model_name: str
    model_path: str
    input_formats: List[str]
    confidence_threshold: float
    processing_time_limit_seconds: int
    memory_requirement_gb: float
    gpu_required: bool = False


@dataclass
class NotificationConfig:
    """
Configuration des notifications"""
    channel_type: str  # email, webhook, sms, slack
    endpoint: str
    enabled: bool
    severity_filter: List[str]
    rate_limit_per_hour: int = 100


# Configurations par défaut des plateformes
PLATFORM_CONFIGS: Dict[str, PlatformConfig] = {
    Platform.YOUTUBE: PlatformConfig(
        name="YouTube",
        api_endpoint="https://www.googleapis.com/youtube/v3",
        api_key_required=True,
        rate_limit_per_hour=10000,
        supports_automated_takedown=True,
        supports_monetization_claims=True,
        detection_capabilities=["video", "audio", "metadata"],
        response_time_sla_hours=24
    ),
    Platform.TIKTOK: PlatformConfig(
        name="TikTok",
        api_endpoint="https://open-api.tiktok.com",
        api_key_required=True,
        rate_limit_per_hour=5000,
        supports_automated_takedown=False,
        supports_monetization_claims=False,
        detection_capabilities=["video", "audio"],
        response_time_sla_hours=48
    ),
    Platform.INSTAGRAM: PlatformConfig(
        name="Instagram",
        api_endpoint="https://graph.instagram.com",
        api_key_required=True,
        rate_limit_per_hour=5000,
        supports_automated_takedown=True,
        supports_monetization_claims=False,
        detection_capabilities=["image", "video", "audio"],
        response_time_sla_hours=24
    ),
    Platform.SPOTIFY: PlatformConfig(
        name="Spotify",
        api_endpoint="https://api.spotify.com/v1",
        api_key_required=True,
        rate_limit_per_hour=2000,
        supports_automated_takedown=True,
        supports_monetization_claims=True,
        detection_capabilities=["audio", "metadata"],
        response_time_sla_hours=12
    )
}

# Configurations des modèles d'IA
AI_MODEL_CONFIGS: Dict[str, AIModelConfig] = {
    "audio_fingerprint": AIModelConfig(
        model_name="AudioFingerprintV3",
        model_path="/models/audio_fingerprint_v3.onnx",
        input_formats=["mp3", "wav", "flac", "aac", "ogg"],
        confidence_threshold=0.85,
        processing_time_limit_seconds=30,
        memory_requirement_gb=2.0
    ),
    "video_similarity": AIModelConfig(
        model_name="VideoSimilarityV2",
        model_path="/models/video_similarity_v2.onnx",
        input_formats=["mp4", "avi", "mov", "mkv", "webm"],
        confidence_threshold=0.80,
        processing_time_limit_seconds=120,
        memory_requirement_gb=4.0,
        gpu_required=True
    ),
    "image_hash": AIModelConfig(
        model_name="PerceptualHashV1",
        model_path="/models/perceptual_hash_v1.onnx",
        input_formats=["jpg", "jpeg", "png", "gif", "webp"],
        confidence_threshold=0.90,
        processing_time_limit_seconds=5,
        memory_requirement_gb=1.0
    ),
    "text_similarity": AIModelConfig(
        model_name="TextSimilarityBERT",
        model_path="/models/text_similarity_bert.onnx",
        input_formats=["txt", "md", "html", "json"],
        confidence_threshold=0.75,
        processing_time_limit_seconds=10,
        memory_requirement_gb=3.0
    )
}

# Templates de clauses légales par juridiction
LEGAL_CLAUSE_TEMPLATES: Dict[str, Dict[str, str]] = {
    "US": {
        "copyright_notice": "(c) {year} {owner}. All rights reserved.",
        "fair_use_disclaimer": "This work is protected by copyright. Fair use provisions under 17 USC § 107 may apply.",
        "dmca_notice": "Protected under the Digital Millennium Copyright Act (DMCA).",
        "termination_clause": "This license may be terminated immediately upon breach of any term."
    },
    "EU": {
        "copyright_notice": "(c) {year} {owner}. Tous droits réservés.",
        "gdpr_compliance": "Processing compliant with GDPR Art. 6(1)(f) - legitimate interests.",
        "database_rights": "Protected by EU Database Directive 96/9/EC.",
        "termination_clause": "Cette licence peut être résiliée immédiatement en cas de violation."
    },
    "GB": {
        "copyright_notice": "(c) {year} {owner}. All rights reserved.",
        "uk_copyright_act": "Protected under the Copyright, Designs and Patents Act 1988.",
        "moral_rights": "The author asserts their moral rights under s.77-89 CDPA 1988.",
        "termination_clause": "This licence may be terminated immediately upon breach."
    }
}

# Configuration des taux de change (mise à jour quotidienne recommandée)
DEFAULT_EXCHANGE_RATES: Dict[str, float] = {
    "USD": 1.0,  # Base currency
    "EUR": 0.85,
    "GBP": 0.73,
    "CAD": 1.25,
    "AUD": 1.35,
    "JPY": 110.0,
    "CHF": 0.91,
    "CNY": 6.45,
    "KRW": 1180.0,
    "BRL": 5.2,
    "INR": 74.0,
    "BTC": 0.000025,  # 1 USD = 0.000025 BTC (approximatif)
    "ETH": 0.0004     # 1 USD = 0.0004 ETH (approximatif)
}

# Configuration des royalties par défaut par type de licence
DEFAULT_ROYALTY_RATES: Dict[str, Dict[str, float]] = {
    LicenseType.EXCLUSIVE: {
        "music_streaming": 0.15,
        "video_sync": 0.25,
        "commercial_use": 0.30,
        "broadcast": 0.20
    },
    LicenseType.NON_EXCLUSIVE: {
        "music_streaming": 0.08,
        "video_sync": 0.12,
        "commercial_use": 0.15,
        "broadcast": 0.10
    },
    LicenseType.SYNC: {
        "film": 0.20,
        "tv": 0.15,
        "advertising": 0.25,
        "video_game": 0.18
    }
}

# Configuration des seuils d'alerte
ALERT_THRESHOLDS: Dict[str, Any] = {
    "violation_count_per_hour": 10,
    "similarity_score_critical": 0.95,
    "financial_impact_threshold": 1000.0,  # USD
    "repeat_offender_threshold": 3,
    "platform_response_time_hours": 48,
    "detection_confidence_minimum": 0.75
}

# Configuration du watermarking
WATERMARKING_CONFIG: Dict[str, Any] = {
    "audio": {
        "algorithm": "spread_spectrum",
        "frequency_range": [1000, 8000],  # Hz
        "amplitude_factor": 0.001,
        "synchronization_pattern": True,
        "error_correction": True
    },
    "video": {
        "algorithm": "dct_based",
        "frames_to_watermark": "all",  # ou "keyframes"
        "spatial_redundancy": True,
        "temporal_redundancy": True,
        "imperceptibility_threshold": 0.98
    },
    "image": {
        "algorithm": "dwt_based",
        "robustness_level": "high",
        "payload_capacity_bits": 256,
        "error_correction_enabled": True
    }
}

# Configuration des métriques de performance
PERFORMANCE_METRICS: Dict[str, Any] = {
    "detection_accuracy_target": 0.95,
    "false_positive_rate_max": 0.02,
    "processing_time_target_seconds": {
        "audio": 30,
        "video": 120,
        "image": 5,
        "text": 10
    },
    "availability_target": 0.999,  # 99.9% uptime
    "response_time_target_ms": 500
}

# Configuration de l'archivage des données
DATA_RETENTION_CONFIG: Dict[str, int] = {
    "usage_detections_days": 2555,      # 7 ans
    "license_agreements_days": 3650,    # 10 ans
    "audit_logs_days": 2555,           # 7 ans
    "temporary_files_hours": 24,        # 1 jour
    "cache_data_hours": 24,             # 1 jour
    "analytics_data_days": 365,         # 1 an
    "user_sessions_hours": 168          # 1 semaine
}

# Configuration des backups
BACKUP_CONFIG: Dict[str, Any] = {
    "enabled": True,
    "frequency_hours": 6,               # Toutes les 6 heures
    "retention_days": 30,               # 30 jours de rétention
    "encryption_enabled": True,
    "compression_enabled": True,
    "verification_enabled": True,
    "storage_locations": [
        "s3://backup-bucket/rights-tracking/",
        "gs://backup-bucket-gcp/rights-tracking/"
    ]
}

# Configuration de la haute disponibilité
HIGH_AVAILABILITY_CONFIG: Dict[str, Any] = {
    "enabled": True,
    "replication_factor": 3,
    "failover_timeout_seconds": 30,
    "health_check_interval_seconds": 10,
    "load_balancing_algorithm": "round_robin",
    "auto_scaling_enabled": True,
    "min_instances": 2,
    "max_instances": 20,
    "scale_up_threshold": 0.80,    # CPU utilization
    "scale_down_threshold": 0.30   # CPU utilization
}


def get_config() -> RightsTrackingConfig:
    """Retourne l'instance de configuration globale"""
    return RightsTrackingConfig()


def get_platform_config(platform: Platform) -> Optional[PlatformConfig]:
    """
Retourne la configuration pour une plateforme spécifique"""
    return PLATFORM_CONFIGS.get(platform)


def get_ai_model_config(model_name: str) -> Optional[AIModelConfig]:
    """
Retourne la configuration pour un modèle d'IA spécifique"""
    return AI_MODEL_CONFIGS.get(model_name)


def get_legal_clauses(jurisdiction: str) -> Dict[str, str]:
    """
Retourne les clauses légales pour une juridiction"""
    return LEGAL_CLAUSE_TEMPLATES.get(jurisdiction, LEGAL_CLAUSE_TEMPLATES["US"])


def get_default_royalty_rate(license_type: LicenseType, usage_type: str) -> float:
    """Retourne le taux de royalty par défaut"""
    rates = DEFAULT_ROYALTY_RATES.get(license_type, {})
    return rates.get(usage_type, 0.10)  # 10% par défaut


def validate_territory_code(territory: str) -> bool:
    """
Valide un code de territoire"""
    try:
        TerritoryCode(territory)
        return True
    except ValueError:
        return False


def get_currency_symbol(currency: Currency) -> str:
    """
Retourne le symbole d'une devise"""
    symbols = {
        Currency.USD: "$",
        Currency.EUR: "€",
        Currency.GBP: "£",
        Currency.JPY: "¥",
        Currency.CNY: "¥",
        Currency.KRW: "₩",
        Currency.INR: "₹",
        Currency.BTC: "₿",
        Currency.ETH: "Ξ"
    }
    return symbols.get(currency, currency.value)


# Validation de la configuration au démarrage
def validate_configuration() -> bool:
    """Valide la configuration au démarrage de l'application"""
    config = get_config()
    
    # Vérifications critiques
    if not config.DATABASE_URL:
        raise ValueError("DATABASE_URL is required")
    
    if not config.REDIS_URL:
        raise ValueError("REDIS_URL is required")
    
    if config.BLOCKCHAIN_ENABLED and not config.BLOCKCHAIN_RPC_URL:
        raise ValueError("BLOCKCHAIN_RPC_URL is required when blockchain is enabled")
    
    if config.AI_DETECTION_ENABLED and not os.path.exists(config.AI_MODEL_PATH):
        raise ValueError(f"AI model path does not exist: {config.AI_MODEL_PATH}")
    
    return True


# Export des configurations pour l'utilisation externe
__all__ = [
    "RightsTrackingConfig",
    "LicenseType",
    "ContentType", 
    "ViolationType",
    "Platform",
    "ActionType",
    "Currency",
    "TerritoryCode",
    "PlatformConfig",
    "AIModelConfig",
    "NotificationConfig",
    "PLATFORM_CONFIGS",
    "AI_MODEL_CONFIGS",
    "LEGAL_CLAUSE_TEMPLATES",
    "DEFAULT_EXCHANGE_RATES",
    "DEFAULT_ROYALTY_RATES",
    "ALERT_THRESHOLDS",
    "WATERMARKING_CONFIG",
    "PERFORMANCE_METRICS",
    "DATA_RETENTION_CONFIG",
    "BACKUP_CONFIG",
    "HIGH_AVAILABILITY_CONFIG",
    "get_config",
    "get_platform_config",
    "get_ai_model_config",
    "get_legal_clauses",
    "get_default_royalty_rate",
    "validate_territory_code",
    "get_currency_symbol",
    "validate_configuration"
]
