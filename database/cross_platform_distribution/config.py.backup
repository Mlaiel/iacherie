"""Configuration Management for Cross-Platform Distribution System

Centralized configuration management for all distribution components.
Provides environment-specific settings, platform credentials, and system parameters.

Author: Fahed Mlaiel (mlaiel@live.de)
Development Team: Lead AI Developer, Senior Backend Engineer, ML Engineer, DBA, Security Expert
Architecture: Enterprise-grade, microservices-ready, production-optimized

⚠️ INTELLECTUAL PROPERTY WARNING ⚠️
This code is the exclusive property of Fahed Mlaiel (mlaiel@live.de).
Any unauthorized use, copying, or distribution is STRICTLY PROHIBITED.
Violations will be prosecuted under international copyright law.
"""
import os
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import json
import logging

logger = logging.getLogger(__name__)

class Environment(str, Enum):
    """Deployment environments"""
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"

@dataclass
class DatabaseConfig:
    """Database configuration"""
    host: str = "localhost"
    port: int = 5432
    database: str = "ia_influencer"
    username: str = "postgres"
    password: str = ""
    ssl_mode: str = "prefer"
    pool_size: int = 10
    max_overflow: int = 20
    connection_timeout: int = 30

@dataclass
class RedisConfig:
    """Redis configuration"""
    host: str = "localhost"
    port: int = 6379
    database: int = 0
    password: Optional[str] = None
    ssl: bool = False
    connection_pool_size: int = 10

@dataclass
class PlatformApiConfig:
    """Platform API configuration"""
    rate_limit_requests: int = 100
    rate_limit_window: int = 3600  # seconds
    timeout: int = 30
    retry_attempts: int = 3
    retry_delay: float = 1.0
    enable_caching: bool = True
    cache_ttl: int = 300  # seconds

@dataclass
class AnalyticsConfig:
    """Analytics configuration"""
    collection_interval: int = 3600  # seconds
    batch_size: int = 1000
    retention_days: int = 365
    enable_real_time: bool = True
    export_formats: list = field(default_factory=lambda: ["json", "csv", "xlsx"])

@dataclass
class SecurityConfig:
    """Security configuration"""
    encryption_key: Optional[str] = None
    jwt_secret: Optional[str] = None
    api_key_length: int = 32
    session_timeout: int = 3600
    max_login_attempts: int = 5
    lockout_duration: int = 900  # seconds

class DistributionConfig:
    """
    Main configuration class for cross-platform distribution system
    """
    
    def __init__(self, environment: Environment = Environment.DEVELOPMENT):
        self.environment = environment
        self.logger = logging.getLogger(__name__)
        
        # Load configuration from environment variables and defaults
        self._load_config()
    
    def _load_config(self):
        """Load configuration from environment variables"""
        
        # Database configuration
        self.database = DatabaseConfig(
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", "5432")),
            database=os.getenv("DB_NAME", "ia_influencer"),
            username=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD", ""),
            ssl_mode=os.getenv("DB_SSL_MODE", "prefer"),
            pool_size=int(os.getenv("DB_POOL_SIZE", "10")),
            max_overflow=int(os.getenv("DB_MAX_OVERFLOW", "20"))
        )
        
        # Redis configuration
        self.redis = RedisConfig(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", "6379")),
            database=int(os.getenv("REDIS_DB", "0")),
            password=os.getenv("REDIS_PASSWORD"),
            ssl=os.getenv("REDIS_SSL", "false").lower() == "true"
        )
        
        # Platform API configuration
        self.platform_api = PlatformApiConfig(
            rate_limit_requests=int(os.getenv("API_RATE_LIMIT", "100")),
            rate_limit_window=int(os.getenv("API_RATE_WINDOW", "3600")),
            timeout=int(os.getenv("API_TIMEOUT", "30")),
            retry_attempts=int(os.getenv("API_RETRY_ATTEMPTS", "3")),
            enable_caching=os.getenv("API_ENABLE_CACHE", "true").lower() == "true"
        )
        
        # Analytics configuration
        self.analytics = AnalyticsConfig(
            collection_interval=int(os.getenv("ANALYTICS_INTERVAL", "3600")),
            batch_size=int(os.getenv("ANALYTICS_BATCH_SIZE", "1000")),
            retention_days=int(os.getenv("ANALYTICS_RETENTION", "365")),
            enable_real_time=os.getenv("ANALYTICS_REAL_TIME", "true").lower() == "true"
        )
        
        # Security configuration
        self.security = SecurityConfig(
            encryption_key=os.getenv("ENCRYPTION_KEY"),
            jwt_secret=os.getenv("JWT_SECRET"),
            session_timeout=int(os.getenv("SESSION_TIMEOUT", "3600")),
            max_login_attempts=int(os.getenv("MAX_LOGIN_ATTEMPTS", "5"))
        )
        
        # Platform credentials (loaded from environment)
        self.platform_credentials = self._load_platform_credentials()
        
        # System settings
        self.system = {
            "debug": os.getenv("DEBUG", "false").lower() == "true",
            "log_level": os.getenv("LOG_LEVEL", "INFO"),
            "max_workers": int(os.getenv("MAX_WORKERS", "4")),
            "enable_metrics": os.getenv("ENABLE_METRICS", "true").lower() == "true",
            "enable_tracing": os.getenv("ENABLE_TRACING", "false").lower() == "true"
        }
    
    def _load_platform_credentials(self) -> Dict[str, Dict[str, str]]:
        """Load platform credentials from environment"""
        
        credentials = {}
        
        # YouTube credentials
        if os.getenv("YOUTUBE_CLIENT_ID"):
            credentials["youtube"] = {
                "client_id": os.getenv("YOUTUBE_CLIENT_ID"),
                "client_secret": os.getenv("YOUTUBE_CLIENT_SECRET"),
                "api_key": os.getenv("YOUTUBE_API_KEY")
            }
        
        # Spotify credentials
        if os.getenv("SPOTIFY_CLIENT_ID"):
            credentials["spotify"] = {
                "client_id": os.getenv("SPOTIFY_CLIENT_ID"),
                "client_secret": os.getenv("SPOTIFY_CLIENT_SECRET")
            }
        
        # Instagram credentials
        if os.getenv("INSTAGRAM_ACCESS_TOKEN"):
            credentials["instagram"] = {
                "access_token": os.getenv("INSTAGRAM_ACCESS_TOKEN"),
                "app_id": os.getenv("INSTAGRAM_APP_ID"),
                "app_secret": os.getenv("INSTAGRAM_APP_SECRET")
            }
        
        # TikTok credentials
        if os.getenv("TIKTOK_CLIENT_KEY"):
            credentials["tiktok"] = {
                "client_key": os.getenv("TIKTOK_CLIENT_KEY"),
                "client_secret": os.getenv("TIKTOK_CLIENT_SECRET")
            }
        
        # Twitter credentials
        if os.getenv("TWITTER_API_KEY"):
            credentials["twitter"] = {
                "api_key": os.getenv("TWITTER_API_KEY"),
                "api_secret": os.getenv("TWITTER_API_SECRET"),
                "access_token": os.getenv("TWITTER_ACCESS_TOKEN"),
                "access_token_secret": os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
            }
        
        return credentials
    
    def get_database_url(self) -> str:
        """Get database connection URL"""
        return (
            f"postgresql://{self.database.username}:{self.database.password}@"
            f"{self.database.host}:{self.database.port}/{self.database.database}"
        )
    
    def get_redis_url(self) -> str:
        """Get Redis connection URL"""
        auth = f":{self.redis.password}@" if self.redis.password else ""
        protocol = "rediss" if self.redis.ssl else "redis"
        return f"{protocol}://{auth}{self.redis.host}:{self.redis.port}/{self.redis.database}"
    
    def get_platform_config(self, platform: str) -> Optional[Dict[str, str]]:
        """Get configuration for specific platform"""
        return self.platform_credentials.get(platform.lower())
    
    def is_platform_configured(self, platform: str) -> bool:
        """Check if platform is properly configured"""
        return platform.lower() in self.platform_credentials
    
    def get_configured_platforms(self) -> list:
        """Get list of configured platforms"""
        return list(self.platform_credentials.keys())
    
    def validate_config(self) -> Dict[str, Any]:
        """Validate configuration and return status"""
        
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "platform_status": {}
        }
        
        # Validate database configuration
        if not self.database.host:
            validation_result["errors"].append("Database host not configured")
            validation_result["valid"] = False
        
        if not self.database.username:
            validation_result["errors"].append("Database username not configured")
            validation_result["valid"] = False
        
        # Validate Redis configuration
        if not self.redis.host:
            validation_result["warnings"].append("Redis host not configured - caching disabled")
        
        # Validate platform configurations
        for platform, config in self.platform_credentials.items():
            if platform == "youtube":
                if not config.get("client_id") or not config.get("client_secret"):
                    validation_result["platform_status"][platform] = "incomplete"
                    validation_result["warnings"].append(f"YouTube credentials incomplete")
                else:
                    validation_result["platform_status"][platform] = "configured"
            
            elif platform == "spotify":
                if not config.get("client_id") or not config.get("client_secret"):
                    validation_result["platform_status"][platform] = "incomplete"
                    validation_result["warnings"].append(f"Spotify credentials incomplete")
                else:
                    validation_result["platform_status"][platform] = "configured"
            
            # Add validation for other platforms...
        
        # Validate security configuration
        if self.environment == Environment.PRODUCTION:
            if not self.security.encryption_key:
                validation_result["errors"].append("Encryption key required for production")
                validation_result["valid"] = False
            
            if not self.security.jwt_secret:
                validation_result["errors"].append("JWT secret required for production")
                validation_result["valid"] = False
        
        return validation_result
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary (excluding sensitive data)"""
        
        return {
            "environment": self.environment.value,
            "database": {
                "host": self.database.host,
                "port": self.database.port,
                "database": self.database.database,
                "username": self.database.username,
                "ssl_mode": self.database.ssl_mode,
                "pool_size": self.database.pool_size
            },
            "redis": {
                "host": self.redis.host,
                "port": self.redis.port,
                "database": self.redis.database,
                "ssl": self.redis.ssl
            },
            "platform_api": {
                "rate_limit_requests": self.platform_api.rate_limit_requests,
                "rate_limit_window": self.platform_api.rate_limit_window,
                "timeout": self.platform_api.timeout,
                "retry_attempts": self.platform_api.retry_attempts,
                "enable_caching": self.platform_api.enable_caching
            },
            "analytics": {
                "collection_interval": self.analytics.collection_interval,
                "batch_size": self.analytics.batch_size,
                "retention_days": self.analytics.retention_days,
                "enable_real_time": self.analytics.enable_real_time
            },
            "system": self.system,
            "configured_platforms": self.get_configured_platforms()
        }

# Global configuration instance
config = DistributionConfig()

# Convenience functions
def get_config() -> DistributionConfig:
    """Get global configuration instance"""
    return config

def load_config(environment: Environment = Environment.DEVELOPMENT) -> DistributionConfig:
    """Load configuration for specific environment"""
    global config
    config = DistributionConfig(environment)
    return config

def get_database_url() -> str:
    """Get database connection URL"""
    return config.get_database_url()

def get_redis_url() -> str:
    """Get Redis connection URL"""
    return config.get_redis_url()

def is_platform_configured(platform: str) -> bool:
    """Check if platform is configured"""
    return config.is_platform_configured(platform)

# Export all configuration classes and functions
__all__ = [
    "DistributionConfig",
    "DatabaseConfig",
    "RedisConfig",
    "PlatformApiConfig",
    "AnalyticsConfig",
    "SecurityConfig",
    "Environment",
    "config",
    "get_config",
    "load_config",
    "get_database_url",
    "get_redis_url",
    "is_platform_configured"
]
