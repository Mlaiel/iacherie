"""Enterprise Matching Module Configuration

Advanced configuration management for the enterprise creator collaboration
matching system with comprehensive settings for AI models, business logic,
performance optimization, and security parameters.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: 2025 Fahed Mlaiel. All rights reserved.

⚠️  INTELLECTUAL PROPERTY WARNING ⚠️
This configuration module contains proprietary settings and algorithms
developed by Fahed Mlaiel. Unauthorized use is prohibited.
"""

import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import timedelta
from enum import Enum
import json
import yaml
from pathlib import Path


class EnvironmentType(Enum):
    """
Environment types for configuration"""

    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"


class AIModelType(Enum):
    """AI model types for matching system"""

    NEURAL_NETWORK = "neural_network"
    RANDOM_FOREST = "random_forest"
    GRADIENT_BOOSTING = "gradient_boosting"
    ENSEMBLE = "ensemble"
    DEEP_LEARNING = "deep_learning"


@dataclass
class DatabaseConfig:
    """Database configuration settings"""
    host: str = "localhost"
    port: int = 5432
    database: str = "ia_influencer_db"
    username: str = "postgres"
    password: str = ""
    pool_size: int = 20
    max_overflow: int = 30
    pool_timeout: int = 30
    ssl_mode: str = "prefer"
    connection_timeout: int = 10


@dataclass
class CacheConfig:
    """Cache configuration settings"""
    backend: str = "redis"
    host: str = "localhost"
    port: int = 6379
    database: int = 0
    password: Optional[str] = None
    default_ttl: timedelta = field(default_factory=lambda: timedelta(hours=1))
    max_connections: int = 50
    socket_timeout: int = 5
    health_check_interval: int = 30


@dataclass
class AIModelConfig:
    """AI model configuration settings"""
    model_type: AIModelType = AIModelType.ENSEMBLE
    model_path: str = "models/"
    enable_gpu: bool = True
    batch_size: int = 32
    max_sequence_length: int = 512
    embedding_dimension: int = 256
    learning_rate: float = 0.001
    dropout_rate: float = 0.1
    regularization_strength: float = 0.01
    early_stopping_patience: int = 10
    model_version: str = "v3.2.1"


@dataclass
class MatchingConfig:
    """Matching algorithm configuration"""
    enable_ai_matching: bool = True
    enable_neural_scoring: bool = True
    enable_business_intelligence: bool = True
    min_compatibility_score: float = 0.65
    max_results_per_request: int = 50
    similarity_threshold: float = 0.7
    diversity_factor: float = 0.3
    novelty_weight: float = 0.2
    strategy_weights: Dict[str, float] = field(default_factory=lambda: {
        "content_synergy": 0.25,
        "audience_compatibility": 0.20,
        "brand_alignment": 0.15,
        "business_potential": 0.15,
        "creative_harmony": 0.10,
        "technical_compatibility": 0.08,
        "risk_assessment": 0.07
    })


@dataclass
class RecommendationConfig:
    """Recommendation engine configuration"""
    enable_personalization: bool = True
    enable_collaborative_filtering: bool = True
    enable_content_based: bool = True
    recommendation_refresh_interval: timedelta = field(default_factory=lambda: timedelta(hours=6))
    max_recommendations_per_user: int = 20
    diversity_threshold: float = 0.3
    min_confidence_score: float = 0.6
    temporal_decay_factor: float = 0.95
    exploration_ratio: float = 0.1
    cold_start_boost: float = 1.2


@dataclass
class SecurityConfig:
    """
Security configuration settings"""
    enable_encryption: bool = True
    encryption_algorithm: str = "AES-256-GCM"
    key_rotation_interval: timedelta = field(default_factory=lambda: timedelta(days=30))
    enable_audit_logging: bool = True
    rate_limit_requests_per_minute: int = 100
    enable_ip_whitelisting: bool = False
    allowed_ips: List[str] = field(default_factory=list)
    jwt_secret_key: str = ""
    jwt_expiration_time: timedelta = field(default_factory=lambda: timedelta(hours=24))
    enable_two_factor_auth: bool = True


@dataclass
class PerformanceConfig:
    """Performance optimization configuration"""
    max_concurrent_requests: int = 100
    request_timeout: timedelta = field(default_factory=lambda: timedelta(minutes=5))
    enable_request_batching: bool = True
    batch_size: int = 10
    enable_async_processing: bool = True
    worker_pool_size: int = 8
    memory_limit_mb: int = 2048
    enable_performance_monitoring: bool = True
    metrics_collection_interval: int = 60
    enable_profiling: bool = False


@dataclass
class BusinessConfig:
    """
Business logic configuration"""
    enable_revenue_optimization: bool = True
    enable_risk_assessment: bool = True
    enable_roi_calculation: bool = True
    default_collaboration_fee_percentage: float = 0.05
    min_creator_audience_size: int = 1000
    max_collaboration_duration_days: int = 180
    enable_geographic_preferences: bool = True
    enable_language_matching: bool = True
    quality_score_weight: float = 0.3
    engagement_rate_weight: float = 0.4
    growth_potential_weight: float = 0.3


@dataclass
class MonitoringConfig:
    """
Monitoring and observability configuration"""
    enable_metrics_collection: bool = True
    enable_error_tracking: bool = True
    enable_performance_tracking: bool = True
    metrics_endpoint: str = "/metrics"
    health_check_endpoint: str = "/health"
    log_level: str = "INFO"
    log_format: str = "json"
    enable_distributed_tracing: bool = True
    tracing_sample_rate: float = 0.1
    alert_thresholds: Dict[str, float] = field(default_factory=lambda: {
        "error_rate": 0.05,
        "response_time_p95": 2000,
        "memory_usage": 0.8,
        "cpu_usage": 0.8
    })


@dataclass
class IntegrationConfig:
    """External integration configuration"""
    enable_social_media_apis: bool = True
    enable_analytics_platforms: bool = True
    enable_payment_gateways: bool = True
    social_media_apis: Dict[str, Dict[str, str]] = field(default_factory=lambda: {
        "youtube": {"api_key": "", "client_id": "", "client_secret": ""},
        "instagram": {"access_token": "", "client_id": "", "client_secret": ""},
        "tiktok": {"app_id": "", "app_secret": "", "access_token": ""},
        "twitter": {"api_key": "", "api_secret": "", "access_token": "", "access_token_secret": ""}
    })
    webhook_endpoints: Dict[str, str] = field(default_factory=dict)
    api_rate_limits: Dict[str, int] = field(default_factory=lambda: {
        "youtube": 10000,
        "instagram": 5000,
        "tiktok": 1000,
        "twitter": 15000
    })


@dataclass
class MatchingModuleConfig:
    """Complete matching module configuration"""
    environment: EnvironmentType = EnvironmentType.DEVELOPMENT
    debug_mode: bool = False
    version: str = "3.2.1"
    
    # Component configurations
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    cache: CacheConfig = field(default_factory=CacheConfig)
    ai_models: AIModelConfig = field(default_factory=AIModelConfig)
    matching: MatchingConfig = field(default_factory=MatchingConfig)
    recommendations: RecommendationConfig = field(default_factory=RecommendationConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    performance: PerformanceConfig = field(default_factory=PerformanceConfig)
    business: BusinessConfig = field(default_factory=BusinessConfig)
    monitoring: MonitoringConfig = field(default_factory=MonitoringConfig)
    integrations: IntegrationConfig = field(default_factory=IntegrationConfig)
    
    # Custom settings
    custom_settings: Dict[str, Any] = field(default_factory=dict)


class ConfigurationManager:
    """Advanced configuration management system"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or self._get_default_config_path()
        self.config = MatchingModuleConfig()
        self._load_configuration()
    
    def _get_default_config_path(self) -> str:
        """
Get default configuration file path"""
        env = os.getenv("ENVIRONMENT", "development")
        return f"config/matching_module_{env}.yaml"
    
    def _load_configuration(self) -> None:
        """Load configuration from files and environment variables"""
        try:
            # Load from YAML file if exists
            if os.path.exists(self.config_path):
                self._load_from_yaml()
            
            # Override with environment variables
            self._load_from_environment()
            
            # Validate configuration
            self._validate_configuration()
            
        except Exception as e:
            print(f"Warning: Could not load configuration: {e}")
            print("Using default configuration")
    
    def _load_from_yaml(self) -> None:
        """Load configuration from YAML file"""
        try:
            with open(self.config_path, 'r') as file:
                config_data = yaml.safe_load(file)
                self._update_config_from_dict(config_data)
        except Exception as e:
            print(f"Error loading YAML configuration: {e}")
    
    def _load_from_environment(self) -> None:
        try:
            logger.info(f"Executing _load_from_environment")
            
            # Implementation for _load_from_environment
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"_load_from_environment completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"_load_from_environment failed: {e}")
            raise
            value = os.getenv(env_var)
            if value is not None:
                self._set_config_value(config_path, value)
    
    def _update_config_from_dict(self, config_data: Dict[str, Any]) -> None:
        """Update configuration from dictionary"""
        for key, value in config_data.items():
            if hasattr(self.config, key):
                if isinstance(value, dict):
                    # Nested configuration
                    nested_config = getattr(self.config, key)
                    for nested_key, nested_value in value.items():
                        if hasattr(nested_config, nested_key):
                            setattr(nested_config, nested_key, nested_value)
                else:
                    setattr(self.config, key, value)
    
    def _set_config_value(self, config_path: tuple, value: str) -> None:
        """
Set configuration value from environment variable"""
        try:
            # Convert string value to appropriate type
            converted_value = self._convert_env_value(value)
            
            # Navigate to the correct configuration object
            config_obj = self.config
            for path_component in config_path[:-1]:
                config_obj = getattr(config_obj, path_component)
            
            # Set the final value
            if len(config_path) > 1:
                setattr(config_obj, config_path[-1], converted_value)
            else:
                setattr(self.config, config_path[0], converted_value)
                
        except Exception as e:
            print(f"Error setting config value {config_path}: {e}")
    
    def _convert_env_value(self, value: str) -> Any:
        """Convert environment variable string to appropriate type"""
        # Boolean conversion
        if value.lower() in ('true', 'false'):
            return value.lower() == 'true'
        
        # Integer conversion
        try:
            return int(value)
        except ValueError:
            pass
        
        # Float conversion
        try:
            return float(value)
        except ValueError:
            pass
        
        # Return as string
        return value
    
    def _validate_configuration(self) -> None:
        try:
            logger.info(f"Executing _convert_env_value")
            
            # Implementation for _convert_env_value
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"_convert_env_value completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"_convert_env_value failed: {e}")
            raise
        if not (0.0 <= self.config.matching.min_compatibility_score <= 1.0):
            errors.append("Minimum compatibility score must be between 0 and 1")
        
        # Validate performance configuration
        if self.config.performance.max_concurrent_requests <= 0:
            errors.append("Max concurrent requests must be positive")
        
        # Validate security configuration
        if self.config.security.enable_encryption and not self.config.security.jwt_secret_key:
            errors.append("JWT secret key required when encryption is enabled")
        
        if errors:
            raise ValueError(f"Configuration validation failed: {'; '.join(errors)}")
    
    def get_config(self) -> MatchingModuleConfig:
        """Get the current configuration"""
        return self.config
    
    def save_configuration(self, file_path: Optional[str] = None) -> None:
        """
Save current configuration to file"""
        output_path = file_path or self.config_path
        
        try:
            # Convert config to dictionary
            config_dict = self._config_to_dict()
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Save to YAML file
            with open(output_path, 'w') as file:
                yaml.dump(config_dict, file, default_flow_style=False, indent=2)
                
            print(f"Configuration saved to {output_path}")
            
        except Exception as e:
            print(f"Error saving configuration: {e}")
    
    def _config_to_dict(self) -> Dict[str, Any]:
        """Convert configuration object to dictionary"""
        config_dict = {}
        
        for field_name, field_value in self.config.__dict__.items():
            if hasattr(field_value, '__dict__'):
                # Nested configuration object
                config_dict[field_name] = field_value.__dict__.copy()
                
                # Convert timedelta objects to strings
                for key, value in config_dict[field_name].items():
                    if isinstance(value, timedelta):
                        config_dict[field_name][key] = str(value)
            else:
                config_dict[field_name] = field_value
                
                # Convert timedelta objects to strings
                if isinstance(field_value, timedelta):
                    config_dict[field_name] = str(field_value)
        
        return config_dict
    
    def update_config(self, updates: Dict[str, Any]) -> None:
        """
Update configuration with new values"""
        self._update_config_from_dict(updates)
        self._validate_configuration()
    
    def get_environment_config(self, environment: EnvironmentType) -> MatchingModuleConfig:
        """
Get configuration optimized for specific environment"""
        env_config = MatchingModuleConfig()
        
        if environment == EnvironmentType.DEVELOPMENT:
            env_config.debug_mode = True
            env_config.monitoring.enable_profiling = True
            env_config.performance.max_concurrent_requests = 20
            
        elif environment == EnvironmentType.TESTING:
            env_config.debug_mode = True
            env_config.database.database = "ia_influencer_test_db"
            env_config.cache.database = 1
            env_config.security.enable_encryption = False
            
        elif environment == EnvironmentType.STAGING:
            env_config.debug_mode = False
            env_config.monitoring.enable_performance_tracking = True
            env_config.security.enable_audit_logging = True
            
        elif environment == EnvironmentType.PRODUCTION:
            env_config.debug_mode = False
            env_config.security.enable_encryption = True
            env_config.security.enable_two_factor_auth = True
            env_config.monitoring.enable_distributed_tracing = True
            env_config.performance.max_concurrent_requests = 200
            
        return env_config
    
    def create_default_config_files(self) -> None:
        """Create default configuration files for all environments"""
        environments = [
            EnvironmentType.DEVELOPMENT,
            EnvironmentType.TESTING,
            EnvironmentType.STAGING,
            EnvironmentType.PRODUCTION
        ]
        
        for env in environments:
            config = self.get_environment_config(env)
            file_path = f"config/matching_module_{env.value}.yaml"
            
            # Temporarily set the config and save
            original_config = self.config
            self.config = config
            self.save_configuration(file_path)
            self.config = original_config


# Global configuration instance
_config_manager: Optional[ConfigurationManager] = None


def get_config_manager() -> ConfigurationManager:
    """Get global configuration manager instance"""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigurationManager()
    return _config_manager


def get_config() -> MatchingModuleConfig:
    """
Get current configuration"""
    return get_config_manager().get_config()


def update_config(updates: Dict[str, Any]) -> None:
    """
Update global configuration"""
    get_config_manager().update_config(updates)


# Configuration presets for common scenarios
DEVELOPMENT_PRESET = {
    "environment": "development",
    "debug_mode": True,
    "performance": {
        "max_concurrent_requests": 20,
        "enable_profiling": True
    },
    "security": {
        "enable_encryption": False,
        "enable_audit_logging": False
    }
}

PRODUCTION_PRESET = {
    "environment": "production",
    "debug_mode": False,
    "performance": {
        "max_concurrent_requests": 200,
        "enable_profiling": False
    },
    "security": {
        "enable_encryption": True,
        "enable_audit_logging": True,
        "enable_two_factor_auth": True
    },
    "monitoring": {
        "enable_distributed_tracing": True,
        "enable_performance_tracking": True
    }
}

HIGH_PERFORMANCE_PRESET = {
    "performance": {
        "max_concurrent_requests": 500,
        "enable_async_processing": True,
        "worker_pool_size": 16,
        "memory_limit_mb": 4096
    },
    "ai_models": {
        "enable_gpu": True,
        "batch_size": 64
    },
    "cache": {
        "max_connections": 100,
        "default_ttl": "30m"
    }
}


if __name__ == "__main__":
    """Create default configuration files"""
    manager = ConfigurationManager()
    manager.create_default_config_files()
    print("Default configuration files created successfully!")
