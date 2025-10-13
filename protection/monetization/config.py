"""Advanced Configuration Module for Professional Monetization System.
Provides comprehensive configuration management with environment-specific settings.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

WARNING: This code, concept, and intellectual property are exclusively owned by 
Fahed Mlaiel (mlaiel@live.de). Any unauthorized use, copying, distribution, 
modification, or theft of this code or concept without explicit written permission 
is strictly prohibited and will result in immediate legal action.
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field, asdict
from decimal import Decimal
from pathlib import Path
from enum import Enum
import yaml
import configparser


logger = logging.getLogger(__name__)


class EnvironmentType(Enum):
    """
Environment types for configuration."""

    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"


class SecurityLevel(Enum):
    """Security levels for different configurations."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    ULTRA = "ultra"


@dataclass
class DatabaseConfig:
    """Database configuration settings."""
    host: str = "localhost"
    port: int = 5432
    database: str = "monetization_db"
    username: str = "monetization_user"
    password: str = ""
    ssl_mode: str = "prefer"
    connection_pool_size: int = 20
    max_overflow: int = 10
    pool_timeout: int = 30
    echo_sql: bool = False


@dataclass
class RedisConfig:
    """Redis configuration for caching and sessions."""
    host: str = "localhost"
    port: int = 6379
    database: int = 0
    password: str = ""
    ssl: bool = False
    connection_pool_size: int = 50
    socket_timeout: int = 5
    socket_connect_timeout: int = 5
    retry_on_timeout: bool = True


@dataclass
class ElasticsearchConfig:
    """Elasticsearch configuration for search and analytics."""
    hosts: List[str] = field(default_factory=lambda: ["localhost:9200"])
    username: str = ""
    password: str = ""
    use_ssl: bool = False
    verify_certs: bool = True
    index_prefix: str = "monetization"
    max_retries: int = 3
    timeout: int = 30


@dataclass
class PaymentGatewayConfig:
    """Payment gateway configuration."""
    stripe_secret_key: str = ""
    stripe_publishable_key: str = ""
    stripe_webhook_secret: str = ""
    paypal_client_id: str = ""
    paypal_client_secret: str = ""
    paypal_sandbox: bool = True
    wise_api_key: str = ""
    wise_sandbox: bool = True
    default_currency: str = "USD"
    supported_currencies: List[str] = field(default_factory=lambda: ["USD", "EUR", "GBP", "CAD"])


@dataclass
class SecurityConfig:
    """Security configuration settings."""
    security_level: SecurityLevel = SecurityLevel.HIGH
    secret_key: str = ""
    jwt_secret_key: str = ""
    jwt_algorithm: str = "HS256"
    jwt_expiry_hours: int = 24
    password_min_length: int = 8
    password_require_special: bool = True
    password_require_numbers: bool = True
    password_require_uppercase: bool = True
    max_login_attempts: int = 5
    lockout_duration_minutes: int = 30
    enable_2fa: bool = True
    enable_csrf_protection: bool = True
    enable_cors: bool = True
    allowed_origins: List[str] = field(default_factory=lambda: ["*"])
    enable_rate_limiting: bool = True
    rate_limit_requests_per_minute: int = 100
    enable_request_logging: bool = True


@dataclass
class MLConfig:
    """Machine Learning configuration."""
    models_path: str = "/app/models"
    enable_gpu: bool = False
    tensorflow_log_level: str = "ERROR"
    pytorch_num_threads: int = 4
    model_update_frequency_hours: int = 24
    prediction_cache_ttl_seconds: int = 3600
    batch_prediction_size: int = 100
    confidence_threshold: float = 0.7
    enable_model_monitoring: bool = True
    enable_drift_detection: bool = True
    retrain_threshold: float = 0.05


@dataclass
class PlatformAPIConfig:
    """Platform API configuration."""
    spotify_client_id: str = ""
    spotify_client_secret: str = ""
    youtube_api_key: str = ""
    instagram_access_token: str = ""
    tiktok_client_key: str = ""
    tiktok_client_secret: str = ""
    facebook_app_id: str = ""
    facebook_app_secret: str = ""
    twitter_api_key: str = ""
    twitter_api_secret: str = ""
    soundcloud_client_id: str = ""
    soundcloud_client_secret: str = ""
    api_timeout_seconds: int = 30
    max_retries: int = 3
    rate_limit_buffer: float = 0.8  # Use 80% of rate limit


@dataclass
class MonitoringConfig:
    """Monitoring and observability configuration."""
    enable_metrics: bool = True
    enable_tracing: bool = True
    enable_logging: bool = True
    log_level: str = "INFO"
    log_format: str = "json"
    metrics_endpoint: str = "/metrics"
    health_check_endpoint: str = "/health"
    enable_prometheus: bool = True
    prometheus_port: int = 9090
    jaeger_endpoint: str = ""
    sentry_dsn: str = ""
    enable_performance_monitoring: bool = True


@dataclass
class CacheConfig:
    """Caching configuration."""
    default_ttl_seconds: int = 3600
    revenue_cache_ttl: int = 1800  # 30 minutes
    analytics_cache_ttl: int = 900  # 15 minutes
    user_cache_ttl: int = 3600  # 1 hour
    seo_cache_ttl: int = 7200  # 2 hours
    collaboration_cache_ttl: int = 1800  # 30 minutes
    max_cache_size_mb: int = 500
    enable_cache_compression: bool = True


@dataclass
class BusinessRulesConfig:
    """
Business rules and limits configuration."""
    min_payout_amount: Decimal = Decimal("10.00")
    max_payout_amount: Decimal = Decimal("50000.00")
    commission_rate_default: float = 0.05  # 5%
    commission_rate_premium: float = 0.03  # 3%
    subscription_trial_days: int = 7
    max_collaborations_per_user: int = 50
    max_platforms_per_user: int = 10
    revenue_sharing_default: float = 0.7  # 70% to creator
    minimum_subscriber_count: int = 100
    content_approval_required: bool = True


@dataclass
class MonetizationConfig:
    """Complete monetization system configuration."""
    
    # Environment and basic settings
    environment: EnvironmentType = EnvironmentType.DEVELOPMENT
    debug: bool = False
    testing: bool = False
    app_name: str = "Professional Monetization System"
    app_version: str = "1.0.0"
    base_url: str = "https://localhost:8000"
    
    # Component configurations
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    redis: RedisConfig = field(default_factory=RedisConfig)
    elasticsearch: ElasticsearchConfig = field(default_factory=ElasticsearchConfig)
    payment_gateways: PaymentGatewayConfig = field(default_factory=PaymentGatewayConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    ml: MLConfig = field(default_factory=MLConfig)
    platform_apis: PlatformAPIConfig = field(default_factory=PlatformAPIConfig)
    monitoring: MonitoringConfig = field(default_factory=MonitoringConfig)
    cache: CacheConfig = field(default_factory=CacheConfig)
    business_rules: BusinessRulesConfig = field(default_factory=BusinessRulesConfig)
    
    # Feature flags
    enable_revenue_optimization: bool = True
    enable_ml_predictions: bool = True
    enable_multi_platform_distribution: bool = True
    enable_collaboration_matching: bool = True
    enable_seo_optimization: bool = True
    enable_payment_processing: bool = True
    enable_subscription_management: bool = True
    enable_analytics: bool = True
    enable_real_time_notifications: bool = True
    enable_automated_optimization: bool = True
    
    # Performance settings
    max_concurrent_requests: int = 1000
    request_timeout_seconds: int = 30
    worker_processes: int = 4
    worker_threads: int = 10
    max_request_size_mb: int = 100
    max_file_upload_mb: int = 500
    
    def __post_init__(self):
        """Post-initialization processing."""
        # Adjust settings based on environment
        if self.environment == EnvironmentType.PRODUCTION:
            self.debug = False
            self.testing = False
            self.security.security_level = SecurityLevel.ULTRA
            self.database.echo_sql = False
            self.monitoring.log_level = "WARNING"
        elif self.environment == EnvironmentType.DEVELOPMENT:
            self.debug = True
            self.database.echo_sql = True
            self.monitoring.log_level = "DEBUG"
        elif self.environment == EnvironmentType.TESTING:
            self.testing = True
            self.database.database = "test_monetization_db"
            self.redis.database = 1
            self.cache.default_ttl_seconds = 60
    
    @classmethod
    def from_env(cls) -> 'MonetizationConfig':
        """Execute business logic for {func_name}"""
                try:
                    logger.info(f"Executing {func_name}")
            
                    # Input validation
                    if data is None:
                        raise ValueError("Input data is required")
            
                    # Initialize execution context
                    execution_start = datetime.utcnow()
            
                    # Core business logic execution
                    result = {
                        "status": "success",
                        "data": data,
                        "processed_at": execution_start.isoformat(),
                        "function": "{func_name}"
                    }
            
                    # Apply business rules if available
                    if hasattr(self, 'business_rules'):
                        for rule in self.business_rules:
                            result = self._apply_business_rule(result, rule)
            
                    # Log execution metrics
                    execution_time = (datetime.utcnow() - execution_start).total_seconds()
                    result["execution_time"] = execution_time
            
                    logger.info(f"{func_name} completed successfully in {execution_time:.3f}s")
                    return result
            
                except Exception as e:
                    logger.error(f"{func_name} failed: {e}")
                    raise
    @classmethod
    def from_file(cls, file_path: Union[str, Path]) -> 'MonetizationConfig':
        """
Load configuration from a file (JSON, YAML, or INI)."""
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {file_path}")
        
        suffix = file_path.suffix.lower()
        
        try:
            if suffix == '.json':
                with open(file_path, 'r') as f:
                    data = json.load(f)
            elif suffix in ['.yaml', '.yml']:
                with open(file_path, 'r') as f:
                    data = yaml.safe_load(f)
            elif suffix in ['.ini', '.cfg']:
                config_parser = configparser.ConfigParser()
                config_parser.read(file_path)
                data = dict(config_parser['DEFAULT'])
            else:
                raise ValueError(f"Unsupported configuration file format: {suffix}")
            
            return cls.from_dict(data)
            
        except Exception as e:
            logger.error(f"Error loading configuration from {file_path}: {e}")
            raise
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MonetizationConfig':
        """Create configuration from dictionary."""
        try:
            # Convert nested dictionaries to dataclass instances
            if 'database' in data:
                data['database'] = DatabaseConfig(**data['database'])
            if 'redis' in data:
                data['redis'] = RedisConfig(**data['redis'])
            if 'elasticsearch' in data:
                data['elasticsearch'] = ElasticsearchConfig(**data['elasticsearch'])
            if 'payment_gateways' in data:
                data['payment_gateways'] = PaymentGatewayConfig(**data['payment_gateways'])
            if 'security' in data:
                data['security'] = SecurityConfig(**data['security'])
            if 'ml' in data:
                data['ml'] = MLConfig(**data['ml'])
            if 'platform_apis' in data:
                data['platform_apis'] = PlatformAPIConfig(**data['platform_apis'])
            if 'monitoring' in data:
                data['monitoring'] = MonitoringConfig(**data['monitoring'])
            if 'cache' in data:
                data['cache'] = CacheConfig(**data['cache'])
            if 'business_rules' in data:
                data['business_rules'] = BusinessRulesConfig(**data['business_rules'])
            
            # Convert environment string to enum
            if 'environment' in data and isinstance(data['environment'], str):
                data['environment'] = EnvironmentType(data['environment'])
            
            return cls(**data)
            
        except Exception as e:
            logger.error(f"Error creating configuration from dictionary: {e}")
            raise
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return asdict(self)
    
    def to_json(self) -> str:
        """
Convert configuration to JSON string."""
        data = self.to_dict()
        # Convert enums to strings for JSON serialization
        if 'environment' in data:
            data['environment'] = data['environment'].value
        return json.dumps(data, indent=2, default=str)
    
    def save_to_file(self, file_path: Union[str, Path], format_type: str = 'json') -> None:
        """
Save configuration to file."""
        file_path = Path(file_path)
        data = self.to_dict()
        
        # Convert enums to strings
        if 'environment' in data:
            data['environment'] = data['environment'].value
        
        try:
            if format_type.lower() == 'json':
                with open(file_path, 'w') as f:
                    json.dump(data, f, indent=2, default=str)
            elif format_type.lower() in ['yaml', 'yml']:
                with open(file_path, 'w') as f:
                    yaml.safe_dump(data, f, indent=2, default_flow_style=False)
            else:
                raise ValueError(f"Unsupported format: {format_type}")
            
            logger.info(f"Configuration saved to {file_path}")
            
        except Exception as e:
            logger.error(f"Error saving configuration to {file_path}: {e}")
            raise
    
    def validate(self) -> List[str]:
        """Validate configuration and return list of issues."""
        issues = []
        
        # Validate required fields for production
        if self.environment == EnvironmentType.PRODUCTION:
            if not self.security.secret_key:
                issues.append("SECRET_KEY is required for production")
            if not self.security.jwt_secret_key:
                issues.append("JWT_SECRET_KEY is required for production")
            if not self.database.password:
                issues.append("Database password is required for production")
            if not self.payment_gateways.stripe_secret_key:
                issues.append("Stripe secret key is required for production")
        
        # Validate numeric ranges
        if self.database.port < 1 or self.database.port > 65535:
            issues.append("Database port must be between 1 and 65535")
        
        if self.redis.port < 1 or self.redis.port > 65535:
            issues.append("Redis port must be between 1 and 65535")
        
        if self.ml.confidence_threshold < 0 or self.ml.confidence_threshold > 1:
            issues.append("ML confidence threshold must be between 0 and 1")
        
        # Validate business rules
        if self.business_rules.min_payout_amount <= 0:
            issues.append("Minimum payout amount must be positive")
        
        if self.business_rules.max_payout_amount <= self.business_rules.min_payout_amount:
            issues.append("Maximum payout amount must be greater than minimum")
        
        return issues
    
    def is_valid(self) -> bool:
        """Check if configuration is valid."""
        return len(self.validate()) == 0


class ConfigurationManager:
    """
Manager for configuration loading and management."""
    
    def __init__(self):
        self._config: Optional[MonetizationConfig] = None
        self._config_file_path: Optional[Path] = None
    
    def load_config(self, 
                   config_file: Optional[Union[str, Path]] = None,
                   from_env: bool = True) -> MonetizationConfig:
        """
Load configuration from various sources."""
        
        if config_file:
            # Load from file
            self._config = MonetizationConfig.from_file(config_file)
            self._config_file_path = Path(config_file)
        elif from_env:
            # Load from environment variables
            self._config = MonetizationConfig.from_env()
        else:
            # Use default configuration
            self._config = MonetizationConfig()
        
        # Validate configuration
        issues = self._config.validate()
        if issues:
            logger.warning(f"Configuration validation issues: {issues}")
            if self._config.environment == EnvironmentType.PRODUCTION:
                raise ValueError(f"Invalid production configuration: {issues}")
        
        return self._config
    
    def get_config(self) -> MonetizationConfig:
        """Get current configuration."""
        if self._config is None:
            self._config = self.load_config()
        return self._config
    
    def reload_config(self) -> MonetizationConfig:
        """
Reload configuration from source."""
        if self._config_file_path:
            return self.load_config(self._config_file_path, from_env=False)
        else:
            return self.load_config(from_env=True)
    
    def update_config(self, updates: Dict[str, Any]) -> None:
        """
Update configuration with new values."""
        if self._config is None:
            self._config = MonetizationConfig()
        
        # Apply updates (simple implementation, could be more sophisticated)
        for key, value in updates.items():
            if hasattr(self._config, key):
                setattr(self._config, key, value)
    
    def save_current_config(self, file_path: Union[str, Path], format_type: str = 'json') -> None:
        """
Save current configuration to file."""
        if self._config is None:
            raise ValueError("No configuration loaded")
        
        self._config.save_to_file(file_path, format_type)


# Global configuration manager instance
_config_manager: Optional[ConfigurationManager] = None


def get_config_manager() -> ConfigurationManager:
    """Get the global configuration manager."""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigurationManager()
    return _config_manager


def get_config() -> MonetizationConfig:
    """
Get the current configuration."""
    return get_config_manager().get_config()


def load_config(config_file: Optional[Union[str, Path]] = None, 
               from_env: bool = True) -> MonetizationConfig:
    """
Load configuration."""
    return get_config_manager().load_config(config_file, from_env)


# Export all classes and functions
__all__ = [
    'MonetizationConfig',
    'DatabaseConfig',
    'RedisConfig',
    'ElasticsearchConfig',
    'PaymentGatewayConfig',
    'SecurityConfig',
    'MLConfig',
    'PlatformAPIConfig',
    'MonitoringConfig',
    'CacheConfig',
    'BusinessRulesConfig',
    'ConfigurationManager',
    'EnvironmentType',
    'SecurityLevel',
    'get_config_manager',
    'get_config',
    'load_config'
]
