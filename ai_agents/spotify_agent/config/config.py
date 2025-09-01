"""Spotify Agent Configuration - Ultra-Advanced Configuration Management

Industrial-grade configuration management system providing environment-specific settings,
feature flags, performance tuning, security configurations, and operational parameters.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code and concept are the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, copying, distribution, or commercialization without explicit written permission is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.

Team Specialties:
- Lead AI Developer & Backend Senior Engineer
- Machine Learning Engineer & Audio Processing Specialist  
- Database Administrator & Security Expert
- Microservices Architect & DevOps Engineer
- AI Prompt Engineer & Content Protection Specialist
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import yaml
from pathlib import Path

logger = logging.getLogger(__name__)

class Environment(Enum):
    """
Environment types"""

    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"
    ENTERPRISE = "enterprise"

class FeatureFlag(Enum):
    """Feature flags for controlled feature rollout"""

    ADVANCED_ANALYTICS = "advanced_analytics"
    MARKETING_INTELLIGENCE = "marketing_intelligence"
    CONTENT_PROTECTION = "content_protection"
    COLLABORATION_ENGINE = "collaboration_engine"
    PREMIUM_FEATURES = "premium_features"
    ENTERPRISE_FEATURES = "enterprise_features"
    EXPERIMENTAL_ML = "experimental_ml"
    BLOCKCHAIN_INTEGRATION = "blockchain_integration"

@dataclass
class SpotifyAPIConfig:
    """Spotify API configuration"""
    client_id: str = ""
    client_secret: str = ""
    redirect_uri: str = "http://localhost:8000/callback"
    scopes: List[str] = field(default_factory=lambda: [
        "user-read-email",
        "user-read-private",
        "user-library-read",
        "user-top-read",
        "user-read-recently-played",
        "user-follow-read",
        "playlist-read-private",
        "playlist-read-collaborative",
        "playlist-modify-public",
        "playlist-modify-private",
        "user-library-modify",
        "user-follow-modify"
    ])
    rate_limit_per_second: int = 100
    retry_attempts: int = 3
    timeout_seconds: int = 30

@dataclass 
class CacheConfig:
    """Caching configuration"""
    enabled: bool = True
    backend: str = "redis"  # redis, memory, database
    host: str = "localhost"
    port: int = 6379
    password: Optional[str] = None
    database: int = 0
    default_ttl: int = 3600  # 1 hour
    max_connections: int = 100
    key_prefix: str = "spotify_agent"

@dataclass
class DatabaseConfig:
    """Database configuration"""
    host: str = "localhost"
    port: int = 5432
    name: str = "ia_influencer_agent"
    username: str = "postgres"
    password: str = ""
    ssl_mode: str = "prefer"
    pool_size: int = 20
    max_connections: int = 100
    connection_timeout: int = 30

@dataclass
class SecurityConfig:
    """Security configuration"""
    encryption_enabled: bool = True
    encryption_algorithm: str = "AES-256-GCM"
    secret_key: str = ""
    jwt_secret: str = ""
    jwt_expiration_hours: int = 24
    api_key_required: bool = True
    rate_limiting_enabled: bool = True
    content_protection_level: str = "standard"  # basic, standard, premium, enterprise
    audit_logging: bool = True

@dataclass
class PerformanceConfig:
    """Performance optimization configuration"""
    max_concurrent_requests: int = 1000
    request_timeout: int = 30
    batch_processing_size: int = 100
    async_processing: bool = True
    cpu_intensive_tasks_pool_size: int = 4
    memory_limit_mb: int = 1024
    garbage_collection_threshold: int = 700
    profiling_enabled: bool = False

@dataclass
class MonitoringConfig:
    """
Monitoring and observability configuration"""
    enabled: bool = True
    metrics_collection: bool = True
    prometheus_enabled: bool = True
    prometheus_port: int = 9090
    health_check_endpoint: bool = True
    logging_level: str = "INFO"
    structured_logging: bool = True
    tracing_enabled: bool = True
    alerting_enabled: bool = True

@dataclass
class FeatureFlagConfig:
    """Feature flag configuration"""
    flags: Dict[str, bool] = field(default_factory=lambda: {
        FeatureFlag.ADVANCED_ANALYTICS.value: True,
        FeatureFlag.MARKETING_INTELLIGENCE.value: True,
        FeatureFlag.CONTENT_PROTECTION.value: True,
        FeatureFlag.COLLABORATION_ENGINE.value: True,
        FeatureFlag.PREMIUM_FEATURES.value: False,
        FeatureFlag.ENTERPRISE_FEATURES.value: False,
        FeatureFlag.EXPERIMENTAL_ML.value: False,
        FeatureFlag.BLOCKCHAIN_INTEGRATION.value: False
    })
    remote_config_enabled: bool = False
    refresh_interval_seconds: int = 300

@dataclass
class MLConfig:
    """
Machine Learning configuration"""
    model_cache_enabled: bool = True
    model_cache_ttl: int = 86400  # 24 hours
    batch_prediction_size: int = 1000
    feature_store_enabled: bool = True
    auto_model_retraining: bool = False
    gpu_enabled: bool = False
    distributed_training: bool = False
    model_versioning: bool = True

@dataclass
class SpotifyAgentConfig:
    """
Complete Spotify Agent configuration"""
    environment: Environment = Environment.PRODUCTION
    debug: bool = False
    
    # Service configurations
    spotify_api: SpotifyAPIConfig = field(default_factory=SpotifyAPIConfig)
    cache: CacheConfig = field(default_factory=CacheConfig)
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    performance: PerformanceConfig = field(default_factory=PerformanceConfig)
    monitoring: MonitoringConfig = field(default_factory=MonitoringConfig)
    feature_flags: FeatureFlagConfig = field(default_factory=FeatureFlagConfig)
    ml: MLConfig = field(default_factory=MLConfig)
    
    # Custom configurations
    custom_settings: Dict[str, Any] = field(default_factory=dict)

class ConfigurationManager:
    """
Advanced configuration management system"""
    
    def __init__(self, config_path: Optional[str] = None, environment: Optional[Environment] = None):
        self.config_path = config_path
        self.environment = environment or self._detect_environment()
        self._config: Optional[SpotifyAgentConfig] = None
        
        # Configuration sources priority: ENV vars > config files > defaults
        self.config_sources = [
            self._load_environment_variables,
            self._load_config_files,
            self._load_defaults
        ]

    def get_config(self) -> SpotifyAgentConfig:
        """
Get complete configuration with all sources merged"""
        if self._config is None:
            self._config = self._build_configuration()
            self._validate_configuration(self._config)
        return self._config

    def reload_config(self) -> SpotifyAgentConfig:
        """
Reload configuration from all sources"""
        self._config = None
        return self.get_config()

    def _detect_environment(self) -> Environment:
        """
Detect current environment"""
        env = os.getenv("SPOTIFY_AGENT_ENV", "production").lower()
        
        env_mapping = {
            "dev": Environment.DEVELOPMENT,
            "development": Environment.DEVELOPMENT,
            "test": Environment.TESTING,
            "testing": Environment.TESTING,
            "stage": Environment.STAGING,
            "staging": Environment.STAGING,
            "prod": Environment.PRODUCTION,
            "production": Environment.PRODUCTION,
            "enterprise": Environment.ENTERPRISE
        }
        
        return env_mapping.get(env, Environment.PRODUCTION)

    def _build_configuration(self) -> SpotifyAgentConfig:
        """Build configuration by merging all sources"""
        config = SpotifyAgentConfig(environment=self.environment)
        
        # Apply configuration sources in priority order
        for source_loader in reversed(self.config_sources):
            source_config = source_loader()
            if source_config:
                config = self._merge_configurations(config, source_config)
        
        # Apply environment-specific overrides
        config = self._apply_environment_overrides(config)
        
        return config

    def _load_environment_variables(self) -> Dict[str, Any]:
        """
Load configuration from environment variables"""
        env_config = {}
        
        # Spotify API configuration
        if os.getenv("SPOTIFY_CLIENT_ID"):
            env_config.setdefault("spotify_api", {})["client_id"] = os.getenv("SPOTIFY_CLIENT_ID")
        
        if os.getenv("SPOTIFY_CLIENT_SECRET"):
            env_config.setdefault("spotify_api", {})["client_secret"] = os.getenv("SPOTIFY_CLIENT_SECRET")
        
        if os.getenv("SPOTIFY_REDIRECT_URI"):
            env_config.setdefault("spotify_api", {})["redirect_uri"] = os.getenv("SPOTIFY_REDIRECT_URI")
        
        # Database configuration
        if os.getenv("DATABASE_URL"):
            db_url = os.getenv("DATABASE_URL")
            # Parse DATABASE_URL if needed
            env_config.setdefault("database", {})["url"] = db_url
        
        # Cache configuration
        if os.getenv("REDIS_URL"):
            env_config.setdefault("cache", {})["url"] = os.getenv("REDIS_URL")
        
        # Security configuration
        if os.getenv("SECRET_KEY"):
            env_config.setdefault("security", {})["secret_key"] = os.getenv("SECRET_KEY")
        
        if os.getenv("JWT_SECRET"):
            env_config.setdefault("security", {})["jwt_secret"] = os.getenv("JWT_SECRET")
        
        # Debug mode
        if os.getenv("DEBUG"):
            env_config["debug"] = os.getenv("DEBUG").lower() in ("true", "1", "yes")
        
        return env_config

    def _load_config_files(self) -> Dict[str, Any]:
        """Load configuration from files"""
        config_data = {}
        
        # Look for configuration files
        config_paths = [
            self.config_path,
            f"config/spotify_agent_{self.environment.value}.yaml",
            f"config/spotify_agent_{self.environment.value}.json",
            "config/spotify_agent.yaml",
            "config/spotify_agent.json",
            f"spotify_agent_{self.environment.value}.yaml",
            f"spotify_agent_{self.environment.value}.json",
            "spotify_agent.yaml",
            "spotify_agent.json"
        ]
        
        for config_path in config_paths:
            if config_path and os.path.exists(config_path):
                try:
                    config_data = self._load_config_file(config_path)
                    logger.info(f"Loaded configuration from {config_path}")
                    break
                except Exception as e:
                    logger.warning(f"Failed to load config file {config_path}: {e}")
        
        return config_data

    def _load_config_file(self, file_path: str) -> Dict[str, Any]:
        """Load configuration from a specific file"""
        path = Path(file_path)
        
        if not path.exists():
            return {}
        
        with open(path, 'r', encoding='utf-8') as file:
            if path.suffix.lower() in ('.yaml', '.yml'):
                return yaml.safe_load(file) or {}
            elif path.suffix.lower() == '.json':
                return json.load(file) or {}
            else:
                raise ValueError(f"Unsupported config file format: {path.suffix}")

    def _load_defaults(self) -> Dict[str, Any]:
        """Load default configuration"""
        return {
            "environment": self.environment.value,
            "debug": self.environment in (Environment.DEVELOPMENT, Environment.TESTING)
        }

    def _merge_configurations(self, base_config: SpotifyAgentConfig, override_config: Dict[str, Any]) -> SpotifyAgentConfig:
        """Merge configuration dictionaries into SpotifyAgentConfig"""
        # This would implement deep merging logic
        # For now, simplified implementation
        
        if "spotify_api" in override_config:
            api_config = override_config["spotify_api"]
            for key, value in api_config.items():
                if hasattr(base_config.spotify_api, key):
                    setattr(base_config.spotify_api, key, value)
        
        if "cache" in override_config:
            cache_config = override_config["cache"]
            for key, value in cache_config.items():
                if hasattr(base_config.cache, key):
                    setattr(base_config.cache, key, value)
        
        # Continue for other configuration sections...
        
        return base_config

    def _apply_environment_overrides(self, config: SpotifyAgentConfig) -> SpotifyAgentConfig:
        """Apply environment-specific configuration overrides"""
        if config.environment == Environment.DEVELOPMENT:
            config.debug = True
            config.monitoring.logging_level = "DEBUG"
            config.cache.default_ttl = 300  # 5 minutes for faster development
            config.security.audit_logging = False
            
        elif config.environment == Environment.TESTING:
            config.debug = True
            config.cache.enabled = False  # Disable caching in tests
            config.monitoring.enabled = False
            config.security.api_key_required = False
            
        elif config.environment == Environment.STAGING:
            config.monitoring.alerting_enabled = False
            config.feature_flags.flags[FeatureFlag.EXPERIMENTAL_ML.value] = True
            
        elif config.environment == Environment.PRODUCTION:
            config.debug = False
            config.monitoring.profiling_enabled = False
            config.security.encryption_enabled = True
            
        elif config.environment == Environment.ENTERPRISE:
            config.feature_flags.flags[FeatureFlag.ENTERPRISE_FEATURES.value] = True
            config.feature_flags.flags[FeatureFlag.BLOCKCHAIN_INTEGRATION.value] = True
            config.security.content_protection_level = "enterprise"
            config.performance.max_concurrent_requests = 10000
        
        return config

    def _validate_configuration(self, config: SpotifyAgentConfig):
        """Validate configuration for completeness and correctness"""
        # Validate required Spotify API credentials
        if not config.spotify_api.client_id:
            logger.warning("Spotify client_id not configured")
        
        if not config.spotify_api.client_secret:
            logger.warning("Spotify client_secret not configured")
        
        # Validate security configuration
        if config.security.encryption_enabled and not config.security.secret_key:
            logger.warning("Encryption enabled but secret_key not configured")
        
        # Validate performance settings
        if config.performance.max_concurrent_requests <= 0:
            raise ValueError("max_concurrent_requests must be positive")
        
        logger.info("Configuration validation completed")

# Global configuration manager instance
_config_manager: Optional[ConfigurationManager] = None

def get_config_manager(config_path: Optional[str] = None, environment: Optional[Environment] = None) -> ConfigurationManager:
    """Get global configuration manager instance"""
    global _config_manager
    
    if _config_manager is None:
        _config_manager = ConfigurationManager(config_path, environment)
    
    return _config_manager

def get_config() -> SpotifyAgentConfig:
    """
Get current Spotify agent configuration"""
    return get_config_manager().get_config()

def reload_config() -> SpotifyAgentConfig:
    """
Reload configuration from all sources"""
    return get_config_manager().reload_config()

# Export main components
__all__ = [
    'SpotifyAgentConfig',
    'ConfigurationManager',
    'Environment',
    'FeatureFlag',
    'SpotifyAPIConfig',
    'CacheConfig',
    'DatabaseConfig',
    'SecurityConfig',
    'PerformanceConfig',
    'MonitoringConfig',
    'FeatureFlagConfig',
    'MLConfig',
    'get_config_manager',
    'get_config',
    'reload_config'
]

logger.info("Spotify Agent Configuration module loaded successfully")
