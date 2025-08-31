"""Platform Agent Configuration - Enterprise Configuration Management

Centralized configuration management for all Platform Agent components
with environment-specific settings and security best practices.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  IMPORTANT LEGAL NOTICE:
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
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import json
from pathlib import Path

from .platform_agent import PlatformType


class Environment(Enum):
    """Deployment environments"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"


@dataclass
class PlatformCredentials:
    """Platform-specific credentials configuration"""
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    api_key: Optional[str] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    webhook_secret: Optional[str] = None
    additional_config: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DatabaseConfig:
    """Database configuration"""
    url: str = "postgresql://localhost:5432/ia_influencer"
    pool_size: int = 20
    max_overflow: int = 30
    pool_timeout: int = 30
    pool_recycle: int = 3600
    echo: bool = False
    enable_ssl: bool = True


@dataclass
class RedisConfig:
    """Redis configuration"""
    url: str = "redis://localhost:6379/0"
    max_connections: int = 50
    socket_timeout: int = 5
    socket_connect_timeout: int = 5
    retry_on_timeout: bool = True
    health_check_interval: int = 30


@dataclass
class SecurityConfig:
    """Security configuration"""
    secret_key: str = os.getenv("PLATFORM_AGENT_SECRET_KEY", "change-me-in-production")
    encryption_key: str = os.getenv("PLATFORM_AGENT_ENCRYPTION_KEY", "change-me-in-production")
    jwt_expiration: int = 3600
    max_login_attempts: int = 5
    session_timeout: int = 7200
    enable_2fa: bool = False
    password_policy: Dict[str, Any] = field(default_factory=lambda: {
        "min_length": 8,
        "require_uppercase": True,
        "require_lowercase": True,
        "require_numbers": True,
        "require_special_chars": True
    })


@dataclass
class AIConfig:
    """AI services configuration"""
    enable_ai_optimization: bool = True
    enable_content_enhancement: bool = True
    enable_auto_translation: bool = True
    model_cache_size: int = 10
    max_concurrent_ai_tasks: int = 5
    ai_processing_timeout: int = 300
    gpu_enabled: bool = False
    gpu_memory_limit: Optional[int] = None


@dataclass
class MonitoringConfig:
    """Monitoring and observability configuration"""
    enable_metrics: bool = True
    enable_tracing: bool = True
    enable_logging: bool = True
    metrics_port: int = 9090
    log_level: str = "INFO"
    log_format: str = "json"
    retention_days: int = 30
    alert_email: Optional[str] = None
    slack_webhook: Optional[str] = None


@dataclass
class PlatformAgentGlobalConfig:
    """Global configuration for Platform Agent module"""
    
    # Environment
    environment: Environment = Environment.DEVELOPMENT
    debug: bool = False
    
    # Database
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    
    # Redis/Cache
    redis: RedisConfig = field(default_factory=RedisConfig)
    
    # Security
    security: SecurityConfig = field(default_factory=SecurityConfig)
    
    # AI Configuration
    ai: AIConfig = field(default_factory=AIConfig)
    
    # Monitoring
    monitoring: MonitoringConfig = field(default_factory=MonitoringConfig)
    
    # Platform Credentials
    platform_credentials: Dict[str, PlatformCredentials] = field(default_factory=dict)
    
    # Platform Agent Settings
    max_concurrent_uploads: int = 10
    retry_attempts: int = 3
    cache_duration: int = 3600
    rate_limit_requests: int = 1000
    rate_limit_window: int = 3600
    enable_real_time_sync: bool = True
    enable_content_protection: bool = True
    enable_revenue_tracking: bool = True
    quality_threshold: float = 0.8
    backup_enabled: bool = True
    
    # Content Distribution Settings
    default_optimization_level: str = "advanced"
    enable_auto_scheduling: bool = True
    enable_collaboration_matching: bool = True
    enable_seo_optimization: bool = True
    
    # Performance Settings
    worker_processes: int = 4
    worker_connections: int = 1000
    keepalive_timeout: int = 75
    client_max_body_size: int = 100 * 1024 * 1024  # 100MB
    
    # File Storage
    upload_path: str = "/tmp/uploads"
    max_file_size: int = 500 * 1024 * 1024  # 500MB
    allowed_file_types: List[str] = field(default_factory=lambda: [
        "mp3", "wav", "flac", "aac", "ogg",  # Audio
        "mp4", "mov", "avi", "mkv", "webm",  # Video
        "jpg", "jpeg", "png", "gif", "bmp", "webp"  # Image
    ])


class ConfigManager:
    """Configuration manager for Platform Agent"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or os.getenv("PLATFORM_AGENT_CONFIG_PATH", "config/platform_agent.json")
        self._config: Optional[PlatformAgentGlobalConfig] = None
        self._load_config()
    
    def _load_config(self):
        """Load configuration from file and environment"""
        # Start with defaults
        self._config = PlatformAgentGlobalConfig()
        
        # Load from file if exists
        if Path(self.config_path).exists():
            with open(self.config_path, 'r') as f:
                file_config = json.load(f)
                self._update_config_from_dict(file_config)
        
        # Override with environment variables
        self._load_from_environment()
        
        # Load platform credentials
        self._load_platform_credentials()
    
    def _update_config_from_dict(self, config_dict: Dict[str, Any]):
        """Update configuration from dictionary"""
        for key, value in config_dict.items():
            if hasattr(self._config, key):
                if isinstance(getattr(self._config, key), dict):
                    getattr(self._config, key).update(value)
                else:
                    setattr(self._config, key, value)
    
    def _load_from_environment(self):
        """Load configuration from environment variables"""
        # Database
        if db_url := os.getenv("DATABASE_URL"):
            self._config.database.url = db_url
        
        # Redis
        if redis_url := os.getenv("REDIS_URL"):
            self._config.redis.url = redis_url
        
        # Environment
        if env := os.getenv("ENVIRONMENT"):
            self._config.environment = Environment(env.lower())
        
        # Debug
        if debug := os.getenv("DEBUG"):
            self._config.debug = debug.lower() == "true"
        
        # Security
        if secret_key := os.getenv("SECRET_KEY"):
            self._config.security.secret_key = secret_key
        
        if encryption_key := os.getenv("ENCRYPTION_KEY"):
            self._config.security.encryption_key = encryption_key
        
        # AI Config
        if ai_enabled := os.getenv("ENABLE_AI_OPTIMIZATION"):
            self._config.ai.enable_ai_optimization = ai_enabled.lower() == "true"
        
        if gpu_enabled := os.getenv("GPU_ENABLED"):
            self._config.ai.gpu_enabled = gpu_enabled.lower() == "true"
        
        # Performance
        if workers := os.getenv("WORKER_PROCESSES"):
            self._config.worker_processes = int(workers)
        
        if max_uploads := os.getenv("MAX_CONCURRENT_UPLOADS"):
            self._config.max_concurrent_uploads = int(max_uploads)
    
    def _load_platform_credentials(self):
        """Load platform credentials from environment or secure store"""
        for platform in PlatformType:
            platform_name = platform.value.upper()
            
            credentials = PlatformCredentials(
                client_id=os.getenv(f"{platform_name}_CLIENT_ID"),
                client_secret=os.getenv(f"{platform_name}_CLIENT_SECRET"),
                api_key=os.getenv(f"{platform_name}_API_KEY"),
                access_token=os.getenv(f"{platform_name}_ACCESS_TOKEN"),
                refresh_token=os.getenv(f"{platform_name}_REFRESH_TOKEN"),
                webhook_secret=os.getenv(f"{platform_name}_WEBHOOK_SECRET")
            )
            
            # Only add if at least one credential is provided
            if any([credentials.client_id, credentials.client_secret, 
                   credentials.api_key, credentials.access_token]):
                self._config.platform_credentials[platform.value] = credentials
    
    @property
    def config(self) -> PlatformAgentGlobalConfig:
        """Get current configuration"""
        return self._config
    
    def get_platform_credentials(self, platform: PlatformType) -> Optional[PlatformCredentials]:
        """Get credentials for specific platform"""
        return self._config.platform_credentials.get(platform.value)
    
    def save_config(self, path: Optional[str] = None):
        """Save current configuration to file"""
        save_path = path or self.config_path
        
        # Create directory if it doesn't exist
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Convert to dictionary (excluding sensitive data)
        config_dict = self._config_to_dict(include_credentials=False)
        
        with open(save_path, 'w') as f:
            json.dump(config_dict, f, indent=2, default=str)
    
    def _config_to_dict(self, include_credentials: bool = False) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        config_dict = {
            "environment": self._config.environment.value,
            "debug": self._config.debug,
            "database": {
                "url": self._config.database.url if include_credentials else "***",
                "pool_size": self._config.database.pool_size,
                "max_overflow": self._config.database.max_overflow,
                "pool_timeout": self._config.database.pool_timeout,
                "pool_recycle": self._config.database.pool_recycle,
                "echo": self._config.database.echo,
                "enable_ssl": self._config.database.enable_ssl
            },
            "redis": {
                "url": self._config.redis.url if include_credentials else "***",
                "max_connections": self._config.redis.max_connections,
                "socket_timeout": self._config.redis.socket_timeout,
                "socket_connect_timeout": self._config.redis.socket_connect_timeout,
                "retry_on_timeout": self._config.redis.retry_on_timeout,
                "health_check_interval": self._config.redis.health_check_interval
            },
            "ai": {
                "enable_ai_optimization": self._config.ai.enable_ai_optimization,
                "enable_content_enhancement": self._config.ai.enable_content_enhancement,
                "enable_auto_translation": self._config.ai.enable_auto_translation,
                "model_cache_size": self._config.ai.model_cache_size,
                "max_concurrent_ai_tasks": self._config.ai.max_concurrent_ai_tasks,
                "ai_processing_timeout": self._config.ai.ai_processing_timeout,
                "gpu_enabled": self._config.ai.gpu_enabled,
                "gpu_memory_limit": self._config.ai.gpu_memory_limit
            },
            "monitoring": {
                "enable_metrics": self._config.monitoring.enable_metrics,
                "enable_tracing": self._config.monitoring.enable_tracing,
                "enable_logging": self._config.monitoring.enable_logging,
                "metrics_port": self._config.monitoring.metrics_port,
                "log_level": self._config.monitoring.log_level,
                "log_format": self._config.monitoring.log_format,
                "retention_days": self._config.monitoring.retention_days
            },
            "platform_agent": {
                "max_concurrent_uploads": self._config.max_concurrent_uploads,
                "retry_attempts": self._config.retry_attempts,
                "cache_duration": self._config.cache_duration,
                "rate_limit_requests": self._config.rate_limit_requests,
                "rate_limit_window": self._config.rate_limit_window,
                "enable_real_time_sync": self._config.enable_real_time_sync,
                "enable_content_protection": self._config.enable_content_protection,
                "enable_revenue_tracking": self._config.enable_revenue_tracking,
                "quality_threshold": self._config.quality_threshold,
                "backup_enabled": self._config.backup_enabled
            },
            "content_distribution": {
                "default_optimization_level": self._config.default_optimization_level,
                "enable_auto_scheduling": self._config.enable_auto_scheduling,
                "enable_collaboration_matching": self._config.enable_collaboration_matching,
                "enable_seo_optimization": self._config.enable_seo_optimization
            },
            "performance": {
                "worker_processes": self._config.worker_processes,
                "worker_connections": self._config.worker_connections,
                "keepalive_timeout": self._config.keepalive_timeout,
                "client_max_body_size": self._config.client_max_body_size
            },
            "file_storage": {
                "upload_path": self._config.upload_path,
                "max_file_size": self._config.max_file_size,
                "allowed_file_types": self._config.allowed_file_types
            }
        }
        
        if include_credentials:
            config_dict["platform_credentials"] = {
                platform: {
                    "client_id": creds.client_id,
                    "client_secret": creds.client_secret,
                    "api_key": creds.api_key,
                    "access_token": creds.access_token,
                    "refresh_token": creds.refresh_token,
                    "webhook_secret": creds.webhook_secret,
                    "additional_config": creds.additional_config
                }
                for platform, creds in self._config.platform_credentials.items()
            }
        
        return config_dict
    
    def validate_config(self) -> Dict[str, List[str]]:
        """Validate configuration and return any errors"""
        errors = {
            "critical": [],
            "warning": [],
            "info": []
        }
        
        # Validate required settings
        if self._config.security.secret_key in ["change-me-in-production", ""]:
            errors["critical"].append("SECRET_KEY must be set for production")
        
        if self._config.security.encryption_key in ["change-me-in-production", ""]:
            errors["critical"].append("ENCRYPTION_KEY must be set for production")
        
        if self._config.environment == Environment.PRODUCTION and self._config.debug:
            errors["warning"].append("Debug mode should be disabled in production")
        
        # Validate database connection
        if not self._config.database.url:
            errors["critical"].append("Database URL is required")
        
        # Validate platform credentials
        if not self._config.platform_credentials:
            errors["warning"].append("No platform credentials configured")
        
        # Validate performance settings
        if self._config.max_concurrent_uploads > 50:
            errors["warning"].append("High concurrent upload limit may impact performance")
        
        return errors
    
    def get_environment_template(self) -> str:
        """Generate environment variable template"""
        return """# Platform Agent Environment Configuration Template
# Copy this file to .env and update values

# Environment
ENVIRONMENT=development
DEBUG=true

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/ia_influencer

# Redis
REDIS_URL=redis://localhost:6379/0

# Security
SECRET_KEY=your-secret-key-here
ENCRYPTION_KEY=your-encryption-key-here

# AI Configuration
ENABLE_AI_OPTIMIZATION=true
GPU_ENABLED=false

# Performance
WORKER_PROCESSES=4
MAX_CONCURRENT_UPLOADS=10

# Platform Credentials
# Spotify
SPOTIFY_CLIENT_ID=your-spotify-client-id
SPOTIFY_CLIENT_SECRET=your-spotify-client-secret

# YouTube
YOUTUBE_API_KEY=your-youtube-api-key

# Instagram
INSTAGRAM_CLIENT_ID=your-instagram-client-id
INSTAGRAM_CLIENT_SECRET=your-instagram-client-secret

# TikTok
TIKTOK_CLIENT_ID=your-tiktok-client-id
TIKTOK_CLIENT_SECRET=your-tiktok-client-secret

# Twitter
TWITTER_API_KEY=your-twitter-api-key
TWITTER_API_SECRET=your-twitter-api-secret

# Facebook
FACEBOOK_CLIENT_ID=your-facebook-client-id
FACEBOOK_CLIENT_SECRET=your-facebook-client-secret

# LinkedIn
LINKEDIN_CLIENT_ID=your-linkedin-client-id
LINKEDIN_CLIENT_SECRET=your-linkedin-client-secret

# Monitoring
ENABLE_METRICS=true
METRICS_PORT=9090
LOG_LEVEL=INFO
"""
# Global configuration instance
config_manager = ConfigManager()
config = config_manager.config

# Helper functions for easy access
def get_config() -> PlatformAgentGlobalConfig:
    """Get global configuration"""
    return config

def get_platform_credentials(platform: PlatformType) -> Optional[PlatformCredentials]:
    """Get platform credentials"""
    return config_manager.get_platform_credentials(platform)

def is_production() -> bool:
    """Check if running in production environment"""
    return config.environment == Environment.PRODUCTION

def is_development() -> bool:
    """Check if running in development environment"""
    return config.environment == Environment.DEVELOPMENT
