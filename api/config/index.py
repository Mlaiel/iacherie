"""Configuration Index - IA Influencer Agent Platform
Main entry point for all configuration management

Author: Fahed Mlaiel <mlaiel@live.de>
WARNING: This code is protected by copyright. Any unauthorized use, reproduction,
or distribution without written permission from Fahed Mlaiel is strictly prohibited.
"""# Core configuration classes
from .app_config import AppConfig
from .database_config import DatabaseConfig
from .blockchain_config import BlockchainConfig
from .security_config import SecurityConfig
from .monitoring_config import MonitoringConfig
from .logging_config import LoggingConfig

# Environment-specific configurations
from .environments import (
    DevelopmentConfig,
    ProductionConfig,
    TestingConfig,
    StagingConfig
)

# Configuration managers
from .config_manager import (
    ConfigManager,
    EnvironmentManager,
    SecretManager,
    FeatureToggleManager
)

# Configuration validators
from .validators import (
    ConfigValidator,
    DatabaseConfigValidator,
    BlockchainConfigValidator,
    SecurityConfigValidator
)

# Configuration loaders
from .loaders import (
    YAMLConfigLoader,
    JSONConfigLoader,
    EnvironmentConfigLoader,
    S3ConfigLoader
)


def get_app_config(environment: str = None) -> AppConfig:
    """
    Get application configuration for the specified environment
    
    Args:
        environment: Target environment (development, production, testing, staging)
        
    Returns:
        AppConfig instance for the specified environment
    """
    if not environment:
        environment = ConfigManager.get_current_environment()
    
    config_map = {
        'development': DevelopmentConfig,
        'production': ProductionConfig,
        'testing': TestingConfig,
        'staging': StagingConfig
    }
    
    config_class = config_map.get(environment, DevelopmentConfig)
    return config_class()


def get_database_config(environment: str = None) -> DatabaseConfig:
    """
    Get database configuration for the specified environment
    
    Args:
        environment: Target environment
        
    Returns:
        DatabaseConfig instance
    """
    app_config = get_app_config(environment)
    return DatabaseConfig(
        host=app_config.database_host,
        port=app_config.database_port,
        name=app_config.database_name,
        username=app_config.database_username,
        password=app_config.database_password,
        ssl_mode=app_config.database_ssl_mode,
        max_connections=app_config.database_max_connections
    )


def get_blockchain_config(environment: str = None) -> BlockchainConfig:
    """
    Get blockchain configuration for the specified environment
    
    Args:
        environment: Target environment
        
    Returns:
        BlockchainConfig instance
    """
    app_config = get_app_config(environment)
    return BlockchainConfig(
        ethereum_rpc_url=app_config.ethereum_rpc_url,
        polygon_rpc_url=app_config.polygon_rpc_url,
        bsc_rpc_url=app_config.bsc_rpc_url,
        avalanche_rpc_url=app_config.avalanche_rpc_url,
        private_key=app_config.blockchain_private_key,
        gas_limit=app_config.gas_limit,
        gas_price=app_config.gas_price,
        contract_addresses=app_config.contract_addresses
    )


def get_security_config(environment: str = None) -> SecurityConfig:
    """
    Get security configuration for the specified environment
    
    Args:
        environment: Target environment
        
    Returns:
        SecurityConfig instance
    """
    app_config = get_app_config(environment)
    return SecurityConfig(
        secret_key=app_config.secret_key,
        jwt_secret=app_config.jwt_secret,
        encryption_key=app_config.encryption_key,
        password_salt=app_config.password_salt,
        session_timeout=app_config.session_timeout,
        max_login_attempts=app_config.max_login_attempts,
        cors_origins=app_config.cors_origins,
        csrf_token_timeout=app_config.csrf_token_timeout
    )


def get_monitoring_config(environment: str = None) -> MonitoringConfig:
    """
    Get monitoring configuration for the specified environment
    
    Args:
        environment: Target environment
        
    Returns:
        MonitoringConfig instance
    """
    app_config = get_app_config(environment)
    return MonitoringConfig(
        prometheus_host=app_config.prometheus_host,
        prometheus_port=app_config.prometheus_port,
        grafana_host=app_config.grafana_host,
        grafana_port=app_config.grafana_port,
        log_level=app_config.log_level,
        metrics_retention=app_config.metrics_retention,
        alerts_webhook=app_config.alerts_webhook
    )


def get_logging_config(environment: str = None) -> LoggingConfig:
    """
    Get logging configuration for the specified environment
    
    Args:
        environment: Target environment
        
    Returns:
        LoggingConfig instance
    """
    app_config = get_app_config(environment)
    return LoggingConfig(
        log_level=app_config.log_level,
        log_format=app_config.log_format,
        log_file_path=app_config.log_file_path,
        log_max_size=app_config.log_max_size,
        log_backup_count=app_config.log_backup_count,
        structured_logging=app_config.structured_logging,
        log_to_console=app_config.log_to_console
    )


def initialize_all_configs(environment: str = None):
    """
    Initialize all configuration components for the application
    
    Args:
        environment: Target environment
        
    Returns:
        Dictionary containing all initialized configurations
    """
    return {
        'app': get_app_config(environment),
        'database': get_database_config(environment),
        'blockchain': get_blockchain_config(environment),
        'security': get_security_config(environment),
        'monitoring': get_monitoring_config(environment),
        'logging': get_logging_config(environment)
    }


def validate_all_configs(environment: str = None) -> bool:
    """
    Validate all configuration components
    
    Args:
        environment: Target environment
        
    Returns:
        True if all configurations are valid, False otherwise
    """
    try:
        configs = initialize_all_configs(environment)
        
        # Validate each configuration
        ConfigValidator.validate_app_config(configs['app'])
        DatabaseConfigValidator.validate(configs['database'])
        BlockchainConfigValidator.validate(configs['blockchain'])
        SecurityConfigValidator.validate(configs['security'])
        
        return True
    except Exception as e:
        print(f"Configuration validation failed: {str(e)}")
        return False


def get_config_manager() -> ConfigManager:
    """
    Get the centralized configuration manager
    
    Returns:
        ConfigManager instance
    """
    return ConfigManager()


def get_environment_manager() -> EnvironmentManager:
    """
    Get the environment management utility
    
    Returns:
        EnvironmentManager instance
    """
    return EnvironmentManager()


def get_secret_manager() -> SecretManager:
    """
    Get the secrets management utility
    
    Returns:
        SecretManager instance
    """
    return SecretManager()


def get_feature_toggle_manager() -> FeatureToggleManager:
    """
    Get the feature toggle management utility
    
    Returns:
        FeatureToggleManager instance
    """
    return FeatureToggleManager()


__all__ = [
    # Configuration Classes
    'AppConfig',
    'DatabaseConfig',
    'BlockchainConfig',
    'SecurityConfig',
    'MonitoringConfig',
    'LoggingConfig',
    
    # Environment Configurations
    'DevelopmentConfig',
    'ProductionConfig',
    'TestingConfig',
    'StagingConfig',
    
    # Configuration Managers
    'ConfigManager',
    'EnvironmentManager',
    'SecretManager',
    'FeatureToggleManager',
    
    # Validators
    'ConfigValidator',
    'DatabaseConfigValidator',
    'BlockchainConfigValidator',
    'SecurityConfigValidator',
    
    # Loaders
    'YAMLConfigLoader',
    'JSONConfigLoader',
    'EnvironmentConfigLoader',
    'S3ConfigLoader',
    
    # Factory Functions
    'get_app_config',
    'get_database_config',
    'get_blockchain_config',
    'get_security_config',
    'get_monitoring_config',
    'get_logging_config',
    'initialize_all_configs',
    'validate_all_configs',
    'get_config_manager',
    'get_environment_manager',
    'get_secret_manager',
    'get_feature_toggle_manager'
]
