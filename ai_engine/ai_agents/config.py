"""
Configuration Management for AI Agents Module

Centralized configuration system for the IA Influencer AI Agents.
Provides environment-specific settings, security configurations, and performance tuning.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

  LEGAL WARNING 
This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use is strictly prohibited.
"""

import os
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from pathlib import Path
import json
import yaml


@dataclass
class DatabaseConfig:
    """Database configuration settings"""
    host: str = "localhost"
    port: int = 5432
    database: str = "ia_influencer"
    username: str = "postgres"
    password: str = ""
    pool_size: int = 20
    max_overflow: int = 30
    pool_timeout: int = 30
    ssl_mode: str = "prefer"


@dataclass
class RedisConfig:
    """Redis configuration settings"""
    host: str = "localhost"
    port: int = 6379
    database: int = 0
    password: Optional[str] = None
    pool_size: int = 50
    socket_timeout: int = 30
    socket_connect_timeout: int = 30
    socket_keepalive: bool = True
    socket_keepalive_options: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AIConfig:
    """AI/ML configuration settings"""
    openai_api_key: str = ""
    openai_model: str = "gpt-4"
    max_tokens: int = 4000
    temperature: float = 0.7
    
    # TensorFlow/PyTorch settings
    tensorflow_gpu_memory_growth: bool = True
    torch_device: str = "auto"  # auto, cpu, cuda, mps
    
    # Vector database
    vector_db_type: str = "faiss"  # faiss, pinecone, weaviate
    vector_dimension: int = 1536
    
    # Content protection
    fingerprinting_enabled: bool = True
    copyright_detection_enabled: bool = True
    content_similarity_threshold: float = 0.85


@dataclass
class SecurityConfig:
    """Security configuration settings"""
    encryption_key: str = ""
    jwt_secret: str = ""
    jwt_expiration_hours: int = 24
    
    # Rate limiting
    rate_limit_enabled: bool = True
    rate_limit_requests_per_minute: int = 60
    rate_limit_burst_size: int = 100
    
    # API Security
    api_key_required: bool = True
    cors_enabled: bool = True
    cors_origins: list = field(default_factory=lambda: ["*"])
    
    # Content filtering
    content_moderation_enabled: bool = True
    toxic_content_threshold: float = 0.8


@dataclass
class MonitoringConfig:
    """Monitoring and observability settings"""
    enabled: bool = True
    log_level: str = "INFO"
    metrics_enabled: bool = True
    tracing_enabled: bool = True
    
    # Prometheus metrics
    prometheus_enabled: bool = False
    prometheus_port: int = 9090
    
    # Health checks
    health_check_interval: int = 60
    performance_monitoring_interval: int = 300
    
    # Alerting
    alerts_enabled: bool = True
    slack_webhook_url: str = ""
    email_alerts_enabled: bool = False


@dataclass
class PerformanceConfig:
    """Performance optimization settings"""
    # Async settings
    max_concurrent_tasks: int = 100
    task_timeout_seconds: int = 300
    retry_attempts: int = 3
    retry_delay_seconds: int = 5
    
    # Caching
    cache_enabled: bool = True
    cache_ttl_seconds: int = 3600
    
    # Resource limits
    memory_limit_mb: int = 8192
    cpu_cores: int = 0  # 0 = auto-detect
    
    # Queue settings
    message_queue_size: int = 10000
    priority_queue_enabled: bool = True


@dataclass
class PlatformConfig:
    """Social media platform configurations"""
    # Instagram
    instagram_enabled: bool = True
    instagram_client_id: str = ""
    instagram_client_secret: str = ""
    
    # TikTok
    tiktok_enabled: bool = True
    tiktok_client_key: str = ""
    tiktok_client_secret: str = ""
    
    # YouTube
    youtube_enabled: bool = True
    youtube_api_key: str = ""
    youtube_client_id: str = ""
    youtube_client_secret: str = ""
    
    # Twitter/X
    twitter_enabled: bool = True
    twitter_api_key: str = ""
    twitter_api_secret: str = ""
    twitter_access_token: str = ""
    twitter_access_token_secret: str = ""
    
    # LinkedIn
    linkedin_enabled: bool = True
    linkedin_client_id: str = ""
    linkedin_client_secret: str = ""
    
    # Facebook
    facebook_enabled: bool = True
    facebook_app_id: str = ""
    facebook_app_secret: str = ""


@dataclass
class AIAgentsConfig:
    """Complete AI Agents configuration"""
    # Environment
    environment: str = "development"  # development, staging, production
    debug: bool = True
    
    # Core configurations
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    redis: RedisConfig = field(default_factory=RedisConfig)
    ai: AIConfig = field(default_factory=AIConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    monitoring: MonitoringConfig = field(default_factory=MonitoringConfig)
    performance: PerformanceConfig = field(default_factory=PerformanceConfig)
    platforms: PlatformConfig = field(default_factory=PlatformConfig)
    
    # Agent-specific settings
    agents: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    
    # Custom settings
    custom: Dict[str, Any] = field(default_factory=dict)


class ConfigManager:
    """Configuration management system"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path
        self._config: Optional[AIAgentsConfig] = None
        self._config_files = []
    
    def load_config(self, config_path: Optional[str] = None) -> AIAgentsConfig:
        """Load configuration from files and environment variables"""
        if config_path:
            self.config_path = config_path
        
        # Load base configuration
        config = AIAgentsConfig()
        
        # Load from configuration files
        config_files = self._find_config_files()
        for config_file in config_files:
            file_config = self._load_config_file(config_file)
            config = self._merge_configs(config, file_config)
        
        # Override with environment variables
        config = self._load_environment_variables(config)
        
        # Validate configuration
        self._validate_config(config)
        
        self._config = config
        return config
    
    def _find_config_files(self) -> list:
        """Find configuration files in order of priority"""
        config_files = []
        
        # Check specific path first
        if self.config_path and Path(self.config_path).exists():
            config_files.append(self.config_path)
        
        # Check standard locations
        standard_paths = [
            "config/ai_agents.yaml",
            "config/ai_agents.yml", 
            "config/ai_agents.json",
            "ai_agents.yaml",
            "ai_agents.yml",
            "ai_agents.json",
            "/etc/ia-influencer/ai_agents.yaml",
            os.path.expanduser("~/.ia-influencer/ai_agents.yaml")
        ]
        
        for path in standard_paths:
            if Path(path).exists():
                config_files.append(path)
        
        return config_files
    
    def _load_config_file(self, file_path: str) -> Dict[str, Any]:
        """Load configuration from a file"""



        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                if file_path.endswith('.json'):
                    return json.load(f)
                else:  # YAML
                    return yaml.safe_load(f) or {}
        except Exception as e:
            print(f"Warning: Could not load config file {file_path}: {e}")
            return {}
    
    def _merge_configs(self, base_config: AIAgentsConfig, file_config: Dict[str, Any]) -> AIAgentsConfig:
        """Merge file configuration into base configuration"""
        # This is a simplified merge - in production, use deep merge
        for key, value in file_config.items():
            if hasattr(base_config, key):
                if isinstance(value, dict) and hasattr(getattr(base_config, key), '__dict__'):
                    # Merge nested configurations
                    nested_config = getattr(base_config, key)
                    for nested_key, nested_value in value.items():
                        if hasattr(nested_config, nested_key):
                            setattr(nested_config, nested_key, nested_value)
                else:
                    setattr(base_config, key, value)
        
        return base_config
    
    def _load_environment_variables(self, config: AIAgentsConfig) -> AIAgentsConfig:
        """Load configuration from environment variables"""
        # Database
        if os.getenv('IA_DB_HOST'):
            config.database.host = os.getenv('IA_DB_HOST')
        if os.getenv('IA_DB_PORT'):
            config.database.port = int(os.getenv('IA_DB_PORT'))
        if os.getenv('IA_DB_NAME'):
            config.database.database = os.getenv('IA_DB_NAME')
        if os.getenv('IA_DB_USER'):
            config.database.username = os.getenv('IA_DB_USER')
        if os.getenv('IA_DB_PASSWORD'):
            config.database.password = os.getenv('IA_DB_PASSWORD')
        
        # Redis
        if os.getenv('IA_REDIS_HOST'):
            config.redis.host = os.getenv('IA_REDIS_HOST')
        if os.getenv('IA_REDIS_PORT'):
            config.redis.port = int(os.getenv('IA_REDIS_PORT'))
        if os.getenv('IA_REDIS_PASSWORD'):
            config.redis.password = os.getenv('IA_REDIS_PASSWORD')
        
        # AI
        if os.getenv('OPENAI_API_KEY'):
            config.ai.openai_api_key = os.getenv('OPENAI_API_KEY')
        
        # Security
        if os.getenv('IA_ENCRYPTION_KEY'):
            config.security.encryption_key = os.getenv('IA_ENCRYPTION_KEY')
        if os.getenv('IA_JWT_SECRET'):
            config.security.jwt_secret = os.getenv('IA_JWT_SECRET')
        
        # Environment
        if os.getenv('IA_ENVIRONMENT'):
            config.environment = os.getenv('IA_ENVIRONMENT')
        if os.getenv('IA_DEBUG'):
            config.debug = os.getenv('IA_DEBUG').lower() == 'true'
        
        # Platform credentials
        platform_env_mapping = {
            'instagram_client_id': 'IA_INSTAGRAM_CLIENT_ID',
            'instagram_client_secret': 'IA_INSTAGRAM_CLIENT_SECRET',
            'tiktok_client_key': 'IA_TIKTOK_CLIENT_KEY',
            'tiktok_client_secret': 'IA_TIKTOK_CLIENT_SECRET',
            'youtube_api_key': 'IA_YOUTUBE_API_KEY',
            'twitter_api_key': 'IA_TWITTER_API_KEY',
            'twitter_api_secret': 'IA_TWITTER_API_SECRET',
            'linkedin_client_id': 'IA_LINKEDIN_CLIENT_ID',
            'facebook_app_id': 'IA_FACEBOOK_APP_ID'
        }
        
        for attr, env_var in platform_env_mapping.items():
            if os.getenv(env_var):
                setattr(config.platforms, attr, os.getenv(env_var))
        
        return config
    
    def _validate_config(self, config: AIAgentsConfig) -> None:
        """Validate configuration values"""
        errors = []
        
        # Required fields in production
        if config.environment == "production":
            if not config.ai.openai_api_key:
                errors.append("OpenAI API key is required in production")
            if not config.security.encryption_key:
                errors.append("Encryption key is required in production")
            if not config.security.jwt_secret:
                errors.append("JWT secret is required in production")
        
        # Validate numeric ranges
        if config.performance.max_concurrent_tasks <= 0:
            errors.append("max_concurrent_tasks must be positive")
        
        if config.ai.temperature < 0 or config.ai.temperature > 2:
            errors.append("AI temperature must be between 0 and 2")
        
        if errors:
            raise ValueError(f"Configuration validation failed: {'; '.join(errors)}")
    
    def get_config(self) -> AIAgentsConfig:
        """Get the current configuration"""
        if self._config is None:
            self._config = self.load_config()
        return self._config
    
    def reload_config(self) -> AIAgentsConfig:
        """Reload configuration from sources"""
        self._config = None
        return self.load_config()
    
    def save_config(self, file_path: str, format: str = "yaml") -> None:
        """Save current configuration to file"""
        if self._config is None:
            raise ValueError("No configuration loaded")
        
        # Convert dataclass to dict
        config_dict = self._dataclass_to_dict(self._config)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            if format.lower() == "json":
                json.dump(config_dict, f, indent=2)
            else:  # YAML
                yaml.dump(config_dict, f, default_flow_style=False, indent=2)
    
    def _dataclass_to_dict(self, obj) -> Dict[str, Any]:
        """Convert dataclass to dictionary recursively"""
        if hasattr(obj, '__dict__'):
            result = {}
            for key, value in obj.__dict__.items():
                if hasattr(value, '__dict__'):
                    result[key] = self._dataclass_to_dict(value)
                else:
                    result[key] = value
            return result
        else:
            return obj


# Global configuration manager instance
_config_manager: Optional[ConfigManager] = None


def get_config_manager() -> ConfigManager:
    """Get the global configuration manager"""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager


def get_config() -> AIAgentsConfig:
    """Get the current configuration"""



    return get_config_manager().get_config()


def load_config(config_path: Optional[str] = None) -> AIAgentsConfig:
    """Load configuration from files and environment"""



    return get_config_manager().load_config(config_path)


# Default configuration for development
def get_default_config() -> AIAgentsConfig:
    """Get default configuration for development"""
    config = AIAgentsConfig()
    config.environment = "development"
    config.debug = True
    
    # Set development-friendly defaults
    config.database.host = "localhost"
    config.database.database = "ia_influencer_dev"
    config.redis.host = "localhost"
    config.monitoring.log_level = "DEBUG"
    config.security.api_key_required = False
    config.performance.max_concurrent_tasks = 10
    
    return config
