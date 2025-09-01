"""Extractors Configuration - Industrial IA Configuration System
=============================================================

Ultra-advanced professional configuration system for all extraction modules.
Implements enterprise-grade configuration management with environment-specific settings.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

WARNING: This code is protected by copyright law. Any unauthorized copying, 
distribution, or modification is strictly prohibited and will result in 
legal action. Contact mlaiel@live.de for licensing.

⚠️ STRICT COPYRIGHT PROTECTION ⚠️
This code is the intellectual property of Fahed Mlaiel (mlaiel@live.de).
UNAUTHORIZED USE STRICTLY PROHIBITED - Legal action will be taken.

Technical Team Expertise:
- Lead IA Developer: Advanced AI/ML algorithms and neural networks
- Backend Senior: Enterprise architecture and microservices
- ML Engineer: Machine learning pipelines and model optimization
- Database Administrator: Data architecture and optimization
- Security Specialist: Cybersecurity and data protection
- Microservices Architect: Distributed systems and scalability
- Audio Engineer: Digital signal processing and audio analysis
- DevOps Engineer: Infrastructure automation and deployment
- IA Prompt Engineer: Prompt optimization and AI interaction

Project Owner: Fahed Mlaiel - mlaiel@live.de
"""

import os
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import timedelta
from enum import Enum
from pathlib import Path

class Environment(Enum):
    """
Deployment environments"""

    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"

class PerformanceTier(Enum):
    """Performance tier configurations"""

    BASIC = "basic"
    STANDARD = "standard"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"

@dataclass
class ExtractionConfig:
    """Main extraction configuration"""
    
    # Environment settings
    environment: Environment = Environment.DEVELOPMENT
    performance_tier: PerformanceTier = PerformanceTier.STANDARD
    debug_mode: bool = False
    
    # Core engine settings
    max_workers: int = 10
    max_concurrent_extractions: int = 50
    default_timeout: int = 300
    retry_attempts: int = 3
    
    # AI features
    enable_ai_features: bool = True
    ai_models_path: str = "/app/models"
    use_gpu_acceleration: bool = False
    model_cache_size: int = 5
    
    # Protection settings
    enable_protection: bool = True
    protection_level: str = "standard"
    monitoring_interval: int = 3600  # seconds
    evidence_storage_path: str = "/app/evidence"
    
    # Analytics settings
    enable_analytics: bool = True
    analytics_retention_days: int = 90
    enable_predictions: bool = True
    prediction_models_path: str = "/app/prediction_models"
    
    # Platform API settings
    platform_apis: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    api_rate_limits: Dict[str, int] = field(default_factory=dict)
    
    # Storage and caching
    cache_enabled: bool = True
    cache_ttl: int = 3600  # seconds
    storage_backend: str = "filesystem"  # filesystem, s3, gcp
    storage_config: Dict[str, Any] = field(default_factory=dict)
    
    # Database settings
    database_url: str = "postgresql://localhost/ia_influencer"
    redis_url: str = "redis://localhost:6379"
    elasticsearch_url: str = "http://localhost:9200"
    
    # Security settings
    encryption_key: Optional[str] = None
    jwt_secret: Optional[str] = None
    api_key_header: str = "X-API-Key"
    rate_limit_enabled: bool = True
    
    # Monitoring and logging
    log_level: str = "INFO"
    monitoring_enabled: bool = True
    metrics_endpoint: str = "/metrics"
    health_check_endpoint: str = "/health"
    
    # Feature flags
    feature_flags: Dict[str, bool] = field(default_factory=dict)


# Environment-specific configurations
DEVELOPMENT_CONFIG = ExtractionConfig(
    environment=Environment.DEVELOPMENT,
    performance_tier=PerformanceTier.BASIC,
    debug_mode=True,
    max_workers=5,
    max_concurrent_extractions=20,
    default_timeout=120,
    log_level="DEBUG",
    feature_flags={
        "enable_experimental_features": True,
        "detailed_logging": True,
        "mock_external_apis": True
    }
)

TESTING_CONFIG = ExtractionConfig(
    environment=Environment.TESTING,
    performance_tier=PerformanceTier.BASIC,
    debug_mode=True,
    max_workers=3,
    max_concurrent_extractions=10,
    default_timeout=60,
    enable_ai_features=False,  # Disable for faster tests
    cache_enabled=False,
    log_level="WARNING",
    feature_flags={
        "enable_test_mode": True,
        "mock_external_apis": True,
        "disable_rate_limiting": True
    }
)

STAGING_CONFIG = ExtractionConfig(
    environment=Environment.STAGING,
    performance_tier=PerformanceTier.STANDARD,
    debug_mode=False,
    max_workers=8,
    max_concurrent_extractions=40,
    default_timeout=300,
    log_level="INFO",
    feature_flags={
        "enable_beta_features": True,
        "enhanced_monitoring": True
    }
)

PRODUCTION_CONFIG = ExtractionConfig(
    environment=Environment.PRODUCTION,
    performance_tier=PerformanceTier.ENTERPRISE,
    debug_mode=False,
    max_workers=20,
    max_concurrent_extractions=100,
    default_timeout=600,
    retry_attempts=5,
    log_level="WARNING",
    monitoring_enabled=True,
    rate_limit_enabled=True,
    feature_flags={
        "high_availability": True,
        "advanced_security": True,
        "performance_optimization": True
    }
)

# Platform-specific API configurations
PLATFORM_API_CONFIGS = {
    "youtube": {
        "api_key_env": "YOUTUBE_API_KEY",
        "base_url": "https://www.googleapis.com/youtube/v3",
        "rate_limit": 10000,  # requests per day
        "timeout": 30,
        "features": ["video_data", "channel_data", "analytics", "comments"]
    },
    "instagram": {
        "api_key_env": "INSTAGRAM_ACCESS_TOKEN",
        "base_url": "https://graph.instagram.com",
        "rate_limit": 4800,  # requests per hour
        "timeout": 30,
        "features": ["media_data", "insights", "user_data"]
    },
    "tiktok": {
        "api_key_env": "TIKTOK_ACCESS_TOKEN",
        "base_url": "https://open-api.tiktok.com",
        "rate_limit": 1000,  # requests per hour
        "timeout": 30,
        "features": ["video_data", "user_data", "analytics"]
    },
    "spotify": {
        "client_id_env": "SPOTIFY_CLIENT_ID",
        "client_secret_env": "SPOTIFY_CLIENT_SECRET",
        "base_url": "https://api.spotify.com/v1",
        "rate_limit": 100,  # requests per second
        "timeout": 30,
        "features": ["track_data", "artist_data", "analytics", "playlists"]
    },
    "twitter": {
        "bearer_token_env": "TWITTER_BEARER_TOKEN",
        "base_url": "https://api.twitter.com/2",
        "rate_limit": 300,  # requests per 15 minutes
        "timeout": 30,
        "features": ["tweet_data", "user_data", "analytics", "trends"]
    }
}

# AI Model configurations
AI_MODEL_CONFIGS = {
    "clip": {
        "model_name": "openai/clip-vit-base-patch32",
        "cache_dir": "/app/models/clip",
        "device": "cuda" if os.getenv("USE_GPU", "false").lower() == "true" else "cpu",
        "batch_size": 32,
        "features": ["image_embedding", "text_embedding", "similarity"]
    },
    "sentence_transformer": {
        "model_name": "all-MiniLM-L6-v2",
        "cache_dir": "/app/models/sentence_transformer",
        "device": "cpu",
        "batch_size": 64,
        "features": ["text_embedding", "semantic_similarity"]
    },
    "whisper": {
        "model_name": "openai/whisper-base",
        "cache_dir": "/app/models/whisper",
        "device": "cuda" if os.getenv("USE_GPU", "false").lower() == "true" else "cpu",
        "language": "auto",
        "features": ["speech_to_text", "language_detection"]
    },
    "yolo": {
        "model_name": "yolov8n.pt",
        "cache_dir": "/app/models/yolo",
        "device": "cuda" if os.getenv("USE_GPU", "false").lower() == "true" else "cpu",
        "confidence": 0.5,
        "features": ["object_detection", "segmentation"]
    }
}

# Storage configurations
STORAGE_CONFIGS = {
    "filesystem": {
        "base_path": "/app/storage",
        "create_directories": True,
        "permissions": 0o755
    },
    "s3": {
        "bucket": os.getenv("AWS_S3_BUCKET", "ia-influencer-storage"),
        "region": os.getenv("AWS_REGION", "eu-west-1"),
        "access_key": os.getenv("AWS_ACCESS_KEY_ID"),
        "secret_key": os.getenv("AWS_SECRET_ACCESS_KEY"),
        "encryption": "AES256"
    },
    "gcp": {
        "bucket": os.getenv("GCP_STORAGE_BUCKET", "ia-influencer-storage"),
        "project_id": os.getenv("GCP_PROJECT_ID"),
        "credentials_path": os.getenv("GCP_CREDENTIALS_PATH")
    }
}

# Security configurations
SECURITY_CONFIGS = {
    "encryption": {
        "algorithm": "AES-256-GCM",
        "key_rotation_days": 90,
        "backup_keys": 3
    },
    "authentication": {
        "jwt_algorithm": "HS256",
        "token_expiry_hours": 24,
        "refresh_token_days": 30
    },
    "rate_limiting": {
        "default_limit": "100/hour",
        "burst_limit": "10/minute",
        "premium_multiplier": 5
    },
    "content_protection": {
        "watermark_strength": "medium",
        "fingerprint_sensitivity": 0.85,
        "monitoring_frequency": "hourly"
    }
}

def get_config(environment: str = None) -> ExtractionConfig:
    """Get configuration for specified environment"""
    env = environment or os.getenv("ENVIRONMENT", "development").lower()
    
    config_map = {
        "development": DEVELOPMENT_CONFIG,
        "testing": TESTING_CONFIG,
        "staging": STAGING_CONFIG,
        "production": PRODUCTION_CONFIG
    }
    
    base_config = config_map.get(env, DEVELOPMENT_CONFIG)
    
    # Override with environment variables
    return _override_with_env_vars(base_config)

def _override_with_env_vars(config: ExtractionConfig) -> ExtractionConfig:
    """Override configuration with environment variables"""
    
    # Core settings
    config.max_workers = int(os.getenv("MAX_WORKERS", config.max_workers))
    config.max_concurrent_extractions = int(os.getenv("MAX_CONCURRENT_EXTRACTIONS", config.max_concurrent_extractions))
    config.default_timeout = int(os.getenv("DEFAULT_TIMEOUT", config.default_timeout))
    
    # Database URLs
    config.database_url = os.getenv("DATABASE_URL", config.database_url)
    config.redis_url = os.getenv("REDIS_URL", config.redis_url)
    config.elasticsearch_url = os.getenv("ELASTICSEARCH_URL", config.elasticsearch_url)
    
    # Security
    config.encryption_key = os.getenv("ENCRYPTION_KEY", config.encryption_key)
    config.jwt_secret = os.getenv("JWT_SECRET", config.jwt_secret)
    
    # AI features
    config.use_gpu_acceleration = os.getenv("USE_GPU", "false").lower() == "true"
    config.ai_models_path = os.getenv("AI_MODELS_PATH", config.ai_models_path)
    
    # Storage
    config.storage_backend = os.getenv("STORAGE_BACKEND", config.storage_backend)
    
    # Platform APIs
    for platform, platform_config in PLATFORM_API_CONFIGS.items():
        if platform not in config.platform_apis:
            config.platform_apis[platform] = {}
        
        # Load API credentials from environment
        for key, env_var in platform_config.items():
            if key.endswith("_env"):
                credential_key = key.replace("_env", "")
                config.platform_apis[platform][credential_key] = os.getenv(env_var)
    
    return config

def load_config_from_file(config_path: str) -> ExtractionConfig:
    """Load configuration from JSON file"""
    try:
        with open(config_path, 'r') as f:
            config_data = json.load(f)
        
        # Convert dict to ExtractionConfig
        config = ExtractionConfig(**config_data)
        return _override_with_env_vars(config)
        
    except Exception as e:
        raise ValueError(f"Failed to load config from {config_path}: {e}")

def save_config_to_file(config: ExtractionConfig, config_path: str):
    """Save configuration to JSON file"""
    try:
        config_dict = {
            field.name: getattr(config, field.name)
            for field in config.__dataclass_fields__.values()
        }
        
        # Convert enums to strings
        for key, value in config_dict.items():
            if isinstance(value, Enum):
                config_dict[key] = value.value
        
        with open(config_path, 'w') as f:
            json.dump(config_dict, f, indent=2, default=str)
            
    except Exception as e:
        raise ValueError(f"Failed to save config to {config_path}: {e}")

def validate_config(config: ExtractionConfig) -> List[str]:
    """Validate configuration and return list of issues"""
    issues = []
    
    # Check required fields
    if config.max_workers <= 0:
        issues.append("max_workers must be positive")
    
    if config.max_concurrent_extractions <= 0:
        issues.append("max_concurrent_extractions must be positive")
    
    if config.default_timeout <= 0:
        issues.append("default_timeout must be positive")
    
    # Check database URLs
    if not config.database_url:
        issues.append("database_url is required")
    
    # Check platform API credentials in production
    if config.environment == Environment.PRODUCTION:
        for platform, platform_config in config.platform_apis.items():
            if not platform_config:
                issues.append(f"Platform API credentials missing for {platform}")
    
    # Check storage configuration
    if config.storage_backend not in STORAGE_CONFIGS:
        issues.append(f"Unsupported storage backend: {config.storage_backend}")
    
    return issues

# Export current configuration
current_config = get_config()

__all__ = [
    'ExtractionConfig',
    'Environment',
    'PerformanceTier',
    'DEVELOPMENT_CONFIG',
    'TESTING_CONFIG',
    'STAGING_CONFIG',
    'PRODUCTION_CONFIG',
    'PLATFORM_API_CONFIGS',
    'AI_MODEL_CONFIGS',
    'STORAGE_CONFIGS',
    'SECURITY_CONFIGS',
    'get_config',
    'load_config_from_file',
    'save_config_to_file',
    'validate_config',
    'current_config'
]
