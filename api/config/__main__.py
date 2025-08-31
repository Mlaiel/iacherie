"""Main Configuration Module - IA Influencer Agent Platform
Comprehensive configuration system with all components

Author: Fahed Mlaiel <mlaiel@live.de>
WARNING: This code is protected by copyright. Any unauthorized use, reproduction,
or distribution without written permission from Fahed Mlaiel is strictly prohibited.
"""# Core Configuration Classes
from .app_config import AppConfig
from .database_config import (
    DatabaseConfig,
    RedisConfig,
    MongoDBConfig,
    ElasticsearchConfig,
    VectorDatabaseConfig,
    DatabaseManager
)
from .security_config import (
    SecurityConfig,
    AuthenticationConfig,
    EncryptionConfig,
    CorsConfig,
    CSPConfig,
    RateLimitConfig,
    OAuth2Config,
    SecurityManager
)
from .blockchain_config import (
    BlockchainConfig,
    NetworkConfig,
    ContractConfig,
    WalletConfig,
    GasConfig,
    BlockchainManager
)
from .monitoring_config import (
    MonitoringConfig,
    PrometheusConfig,
    GrafanaConfig,
    JaegerConfig,
    AlertConfig,
    MetricConfig,
    DashboardConfig,
    MonitoringManager
)
from .logging_config import (
    LoggingConfig,
    FileLogConfig,
    ConsoleLogConfig,
    SyslogConfig,
    ElasticsearchLogConfig,
    WebhookLogConfig,
    StructuredLogConfig,
    LoggingManager
)

# Environment-Specific Configurations
from .environments import (
    DevelopmentConfig,
    TestingConfig,
    StagingConfig,
    ProductionConfig,
    get_environment_config,
    validate_environment_config
)

# Configuration Management
from .config_manager import (
    ConfigManager,
    EnvironmentManager,
    SecretManager,
    FeatureToggleManager,
    ConfigurationError,
    ValidationError,
    LoaderError
)

# Configuration Validation
from .validators import (
    BaseValidator,
    ConfigValidator,
    DatabaseConfigValidator,
    SecurityConfigValidator,
    BlockchainConfigValidator,
    MonitoringConfigValidator,
    LoggingConfigValidator,
    ValidationResult,
    ValidationError as ValidatorError
)

# Configuration Loaders
from .loaders import (
    ConfigurationLoader,
    YAMLConfigLoader,
    JSONConfigLoader,
    TOMLConfigLoader,
    INIConfigLoader,
    EnvironmentConfigLoader,
    S3ConfigLoader,
    HTTPConfigLoader,
    RedisConfigLoader,
    DatabaseConfigLoader,
    ConfigLoaderRegistry,
    load_configuration,
    register_custom_loader,
    create_config_from_dict,
    loader_registry
)

# Main index module
from .index import (
    COPYRIGHT_NOTICE,
    TEAM_SPECIALTIES,
    print_copyright_notice,
    get_all_config_classes,
    create_default_config,
    load_config_from_environment,
    validate_all_configs,
    export_config_schema
)

import os
import logging
from typing import Dict, Any, Optional, Type, Union, List
from pathlib import Path

logger = logging.getLogger(__name__)

# Version information
__version__ = "1.0.0"
__author__ = "Fahed Mlaiel <mlaiel@live.de>"
__copyright__ = "Copyright (c) 2025 Fahed Mlaiel. All rights reserved."
__license__ = "Proprietary - All rights reserved"

# Configuration constants
DEFAULT_CONFIG_PATHS = [
    "/workspaces/Achiri/IA-Influencer-Agent/config/app.yaml",
    "/workspaces/Achiri/IA-Influencer-Agent/config/app.json",
    "/workspaces/Achiri/IA-Influencer-Agent/config/app.toml",
    "./config/app.yaml",
    "./config/app.json",
    "./config/app.toml",
    "~/.ia-influencer/config.yaml",
    "~/.ia-influencer/config.json"
]

ENVIRONMENT_CONFIG_MAP = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "staging": StagingConfig,
    "production": ProductionConfig
}

# Global configuration instance
_global_config: Optional[AppConfig] = None
_config_manager: Optional[ConfigManager] = None


def get_config() -> AppConfig:
    """Get global configuration instance"""    global _global_config
    
    if _global_config is None:
        _global_config = initialize_configuration()
    
    return _global_config


def set_config(config: AppConfig):
    """Set global configuration instance"""    global _global_config
    _global_config = config


def get_config_manager() -> ConfigManager:
    """Get global configuration manager instance"""    global _config_manager
    
    if _config_manager is None:
        _config_manager = ConfigManager()
    
    return _config_manager


def initialize_configuration(
    config_sources: Optional[List[str]] = None,
    environment: Optional[str] = None,
    validate: bool = True
) -> AppConfig:
    """    Initialize application configuration
    
    Args:
        config_sources: List of configuration sources to load from
        environment: Environment name (development, testing, staging, production)
        validate: Whether to validate configuration
    
    Returns:
        Configured AppConfig instance
    """    try:
        # Print copyright notice
        print_copyright_notice()
        
        # Determine environment
        if environment is None:
            environment = os.getenv('IA_ENVIRONMENT', 'development')
        
        logger.info(f"Initializing configuration for environment: {environment}")
        
        # Get base configuration class for environment
        config_class = ENVIRONMENT_CONFIG_MAP.get(environment, DevelopmentConfig)
        
        # Load configuration from sources
        if config_sources is None:
            config_sources = _get_default_config_sources()
        
        # Add environment variables as a source
        config_sources.append("environment")
        
        # Load merged configuration
        config_dict = load_configuration(config_sources)
        
        # Create configuration instance
        config = create_config_from_dict(config_dict, config_class)
        
        # Validate configuration if requested
        if validate:
            validation_result = validate_configuration(config)
            if not validation_result.is_valid:
                logger.error(f"Configuration validation failed: {validation_result.errors}")
                raise ValidationError(f"Configuration validation failed: {validation_result.errors}")
        
        logger.info("Configuration initialized successfully")
        return config
        
    except Exception as e:
        logger.error(f"Failed to initialize configuration: {e}")
        raise ConfigurationError(f"Configuration initialization failed: {e}")


def _get_default_config_sources() -> List[str]:
    """Get default configuration sources"""    sources = []
    
    # Check for existing config files
    for config_path in DEFAULT_CONFIG_PATHS:
        path = Path(config_path).expanduser()
        if path.exists():
            sources.append(str(path))
            logger.debug(f"Found configuration file: {path}")
    
    # Check for remote sources
    s3_config = os.getenv('IA_CONFIG_S3_URL')
    if s3_config:
        sources.append(s3_config)
        logger.debug(f"Using S3 configuration: {s3_config}")
    
    http_config = os.getenv('IA_CONFIG_HTTP_URL')
    if http_config:
        sources.append(http_config)
        logger.debug(f"Using HTTP configuration: {http_config}")
    
    redis_config = os.getenv('IA_CONFIG_REDIS_URL')
    if redis_config:
        sources.append(redis_config)
        logger.debug(f"Using Redis configuration: {redis_config}")
    
    return sources


def validate_configuration(config: AppConfig) -> 'ValidationResult':
    """Validate application configuration"""    try:
        validator = ConfigValidator()
        return validator.validate(config)
    except Exception as e:
        logger.error(f"Configuration validation error: {e}")
        return ValidationResult(
            is_valid=False,
            errors=[f"Validation error: {e}"],
            warnings=[]
        )


def reload_configuration(validate: bool = True) -> AppConfig:
    """Reload global configuration"""    global _global_config
    _global_config = None
    return initialize_configuration(validate=validate)


def export_configuration_schema(output_path: str, format: str = "json"):
    """Export configuration schema to file"""    try:
        schema = export_config_schema(format)
        
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(schema)
        
        logger.info(f"Configuration schema exported to: {output_path}")
        
    except Exception as e:
        logger.error(f"Failed to export configuration schema: {e}")
        raise


def create_configuration_template(output_path: str, environment: str = "development"):
    """Create a configuration template file"""    try:
        config_class = ENVIRONMENT_CONFIG_MAP.get(environment, DevelopmentConfig)
        config = config_class()
        
        # Convert to dictionary
        config_dict = {}
        if hasattr(config, '__dict__'):
            for key, value in config.__dict__.items():
                if not key.startswith('_'):
                    config_dict[key] = value
        
        # Export as YAML template
        import yaml
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            yaml.dump(config_dict, f, default_flow_style=False, indent=2)
        
        logger.info(f"Configuration template created: {output_path}")
        
    except Exception as e:
        logger.error(f"Failed to create configuration template: {e}")
        raise


def get_configuration_info() -> Dict[str, Any]:
    """Get information about current configuration"""    config = get_config()
    
    return {
        "version": __version__,
        "environment": config.environment,
        "debug_mode": config.debug,
        "config_sources": _get_default_config_sources(),
        "database_config": {
            "postgresql_enabled": bool(config.database.host),
            "redis_enabled": bool(config.redis.host),
            "mongodb_enabled": bool(config.mongodb.host),
            "elasticsearch_enabled": bool(config.elasticsearch.host)
        },
        "security_config": {
            "authentication_enabled": config.security.enable_authentication,
            "encryption_enabled": config.security.encryption.enable_encryption,
            "cors_enabled": config.security.cors.enable_cors
        },
        "blockchain_config": {
            "enabled": config.blockchain.enabled,
            "networks": list(config.blockchain.networks.keys()) if config.blockchain.networks else []
        },
        "monitoring_config": {
            "prometheus_enabled": config.monitoring.prometheus.enabled,
            "grafana_enabled": config.monitoring.grafana.enabled,
            "jaeger_enabled": config.monitoring.jaeger.enabled
        }
    }


# Configuration decorators
def require_config(config_key: str):
    """Decorator to ensure configuration value is set"""    def decorator(func):
        def wrapper(*args, **kwargs):
            config = get_config()
            if not hasattr(config, config_key) or getattr(config, config_key) is None:
                raise ConfigurationError(f"Required configuration '{config_key}' is not set")
            return func(*args, **kwargs)
        return wrapper
    return decorator


def with_config(func):
    """Decorator to inject configuration as first argument"""    def wrapper(*args, **kwargs):
        config = get_config()
        return func(config, *args, **kwargs)
    return wrapper


# Export all public symbols
__all__ = [
    # Core classes
    'AppConfig',
    'DatabaseConfig', 'RedisConfig', 'MongoDBConfig', 'ElasticsearchConfig', 'VectorDatabaseConfig',
    'SecurityConfig', 'AuthenticationConfig', 'EncryptionConfig', 'CorsConfig', 'CSPConfig',
    'BlockchainConfig', 'NetworkConfig', 'ContractConfig', 'WalletConfig', 'GasConfig',
    'MonitoringConfig', 'PrometheusConfig', 'GrafanaConfig', 'JaegerConfig',
    'LoggingConfig', 'FileLogConfig', 'ConsoleLogConfig',
    
    # Environment configs
    'DevelopmentConfig', 'TestingConfig', 'StagingConfig', 'ProductionConfig',
    
    # Managers
    'ConfigManager', 'EnvironmentManager', 'SecretManager', 'FeatureToggleManager',
    'DatabaseManager', 'SecurityManager', 'BlockchainManager', 'MonitoringManager', 'LoggingManager',
    
    # Validators
    'ConfigValidator', 'DatabaseConfigValidator', 'SecurityConfigValidator',
    'BlockchainConfigValidator', 'MonitoringConfigValidator', 'LoggingConfigValidator',
    
    # Loaders
    'YAMLConfigLoader', 'JSONConfigLoader', 'TOMLConfigLoader', 'INIConfigLoader',
    'EnvironmentConfigLoader', 'S3ConfigLoader', 'HTTPConfigLoader', 'RedisConfigLoader',
    'ConfigLoaderRegistry', 'load_configuration', 'register_custom_loader',
    
    # Main functions
    'get_config', 'set_config', 'get_config_manager',
    'initialize_configuration', 'validate_configuration', 'reload_configuration',
    'export_configuration_schema', 'create_configuration_template', 'get_configuration_info',
    
    # Decorators
    'require_config', 'with_config',
    
    # Constants
    'DEFAULT_CONFIG_PATHS', 'ENVIRONMENT_CONFIG_MAP',
    
    # Exceptions
    'ConfigurationError', 'ValidationError', 'LoaderError'
]
