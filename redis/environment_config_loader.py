"""
import asyncio

Environment Configuration Loader for Redis Enterprise
Backend Senior Implementation - Multi-Environment Configuration Management

Author: Fahed Mlaiel (mlaiel@live.de)
Multi-Expert Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + Microservices + Audio + DevOps + IA Prompt Engineer
"""

import os
import json
import yaml
import logging
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import redis.asyncio as redis
from config.core.redis import RedisSettings

logger = logging.getLogger(__name__)

class EnvironmentType(Enum):
    """Environment types for configuration"""
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"
    DR = "disaster_recovery"  # Disaster Recovery
    LOAD_TEST = "load_test"

@dataclass
class EnvironmentConfig:
    """Environment-specific configuration"""
    name: str
    environment_type: EnvironmentType
    redis_config: Dict[str, Any] = field(default_factory=dict)
    cache_policies: Dict[str, Any] = field(default_factory=dict)
    security_settings: Dict[str, Any] = field(default_factory=dict)
    performance_settings: Dict[str, Any] = field(default_factory=dict)
    feature_flags: Dict[str, bool] = field(default_factory=dict)
    custom_settings: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self) -> None:
        """Set default values based on environment type"""
        if not self.redis_config:
            self.redis_config = self._get_default_redis_config()
        if not self.cache_policies:
            self.cache_policies = self._get_default_cache_policies()
        if not self.security_settings:
            self.security_settings = self._get_default_security_settings()
        if not self.performance_settings:
            self.performance_settings = self._get_default_performance_settings()
    
    def _get_default_redis_config(self) -> Dict[str, Any]:
        """Get default Redis configuration for environment type"""
        base_config = {
            "host": "localhost",
            "port": 6379,
            "db": 0,
            "max_connections": 50,
            "socket_timeout": 5,
            "socket_connect_timeout": 5,
            "health_check_interval": 30,
            "ssl_enabled": False
        }
        
        if self.environment_type == EnvironmentType.PRODUCTION:
            base_config.update({
                "max_connections": 200,
                "socket_timeout": 10,
                "ssl_enabled": True,
                "cluster_enabled": True,
                "sentinel_enabled": True
            })
        elif self.environment_type == EnvironmentType.STAGING:
            base_config.update({
                "max_connections": 100,
                "ssl_enabled": True,
                "cluster_enabled": True
            })
        elif self.environment_type == EnvironmentType.DEVELOPMENT:
            base_config.update({
                "max_connections": 20,
                "db": 1  # Use different DB for dev
            })
        elif self.environment_type == EnvironmentType.TESTING:
            base_config.update({
                "max_connections": 10,
                "db": 2,  # Use different DB for tests
                "socket_timeout": 1  # Faster timeouts for tests
            })
        elif self.environment_type == EnvironmentType.LOAD_TEST:
            base_config.update({
                "max_connections": 500,
                "socket_timeout": 15,
                "cluster_enabled": True
            })
        
        return base_config
    
    def _get_default_cache_policies(self) -> Dict[str, Any]:
        """Get default cache policies for environment type"""
        base_policies = {
            "default_ttl": 3600,  # 1 hour
            "eviction_policy": "allkeys-lru",
            "max_memory_usage": "80%",
            "compression_enabled": True
        }
        
        if self.environment_type == EnvironmentType.PRODUCTION:
            base_policies.update({
                "default_ttl": 7200,  # 2 hours in prod
                "max_memory_usage": "75%",  # More conservative
                "backup_frequency": "hourly"
            })
        elif self.environment_type == EnvironmentType.DEVELOPMENT:
            base_policies.update({
                "default_ttl": 300,  # 5 minutes in dev
                "eviction_policy": "allkeys-random",  # More aggressive for dev
                "compression_enabled": False  # Easier debugging
            })
        elif self.environment_type == EnvironmentType.TESTING:
            base_policies.update({
                "default_ttl": 60,  # 1 minute for tests
                "eviction_policy": "allkeys-random",
                "compression_enabled": False
            })
        
        return base_policies
    
    def _get_default_security_settings(self) -> Dict[str, Any]:
        """Get default security settings for environment type"""
        base_security = {
            "auth_enabled": True,
            "acl_enabled": False,
            "encryption_at_rest": False,
            "audit_logging": False,
            "rate_limiting": False
        }
        
        if self.environment_type == EnvironmentType.PRODUCTION:
            base_security.update({
                "acl_enabled": True,
                "encryption_at_rest": True,
                "audit_logging": True,
                "rate_limiting": True,
                "key_rotation_enabled": True,
                "threat_detection": True
            })
        elif self.environment_type == EnvironmentType.STAGING:
            base_security.update({
                "acl_enabled": True,
                "encryption_at_rest": True,
                "audit_logging": True
            })
        elif self.environment_type == EnvironmentType.DEVELOPMENT:
            base_security.update({
                "auth_enabled": False,  # Easier for dev
                "audit_logging": False
            })
        elif self.environment_type == EnvironmentType.TESTING:
            base_security.update({
                "auth_enabled": False,
                "audit_logging": False
            })
        
        return base_security
    
    def _get_default_performance_settings(self) -> Dict[str, Any]:
        """Get default performance settings for environment type"""
        base_performance = {
            "memory_optimization": True,
            "query_optimization": True,
            "connection_pooling": True,
            "pipeline_optimization": True,
            "monitoring_enabled": True
        }
        
        if self.environment_type == EnvironmentType.PRODUCTION:
            base_performance.update({
                "advanced_optimization": True,
                "predictive_scaling": True,
                "performance_alerts": True,
                "slow_query_logging": True
            })
        elif self.environment_type == EnvironmentType.LOAD_TEST:
            base_performance.update({
                "advanced_optimization": True,
                "detailed_metrics": True,
                "stress_monitoring": True
            })
        
        return base_performance

class EnvironmentConfigLoader:
    """
    Multi-environment configuration loader for Redis enterprise
    Backend Senior implementation with robust environment management
    """
    
    def __init__(self, redis_settings -> None: Optional[RedisSettings] = None) -> None:
        self.redis_settings = redis_settings or RedisSettings()
        self.redis_client: Optional[redis.Redis] = None
        self.current_environment: Optional[EnvironmentType] = None
        self.environments: Dict[str, EnvironmentConfig] = {}
        self.config_cache: Dict[str, Any] = {}
        self.config_sources: List[str] = []
        
        # Configuration paths
        self.config_dir = Path("/home/runner/work/Ainflue/Ainflue/redis/config")
        self.env_config_key = "ainflue:env:config"
        self.env_override_key = "ainflue:env:override"
        
        # Auto-detect current environment
        self._detect_environment()
    
    def _detect_environment(self) -> None:
        """Auto-detect current environment from various sources"""
        try:
            # Check environment variable
            env_name = os.getenv('AINFLUE_ENV', os.getenv('ENV', 'development')).lower()
            
            # Map common environment names
            env_mapping = {
                'dev': EnvironmentType.DEVELOPMENT,
                'development': EnvironmentType.DEVELOPMENT,
                'test': EnvironmentType.TESTING,
                'testing': EnvironmentType.TESTING,
                'stage': EnvironmentType.STAGING,
                'staging': EnvironmentType.STAGING,
                'prod': EnvironmentType.PRODUCTION,
                'production': EnvironmentType.PRODUCTION,
                'dr': EnvironmentType.DR,
                'disaster_recovery': EnvironmentType.DR,
                'load_test': EnvironmentType.LOAD_TEST,
                'loadtest': EnvironmentType.LOAD_TEST
            }
            
            self.current_environment = env_mapping.get(env_name, EnvironmentType.DEVELOPMENT)
            logger.info(f"Detected environment: {self.current_environment.value}")
            
        except Exception as e:
            logger.warning(f"Error detecting environment, defaulting to development: {e}")
            self.current_environment = EnvironmentType.DEVELOPMENT
    
    async def initialize(self) -> None:
        """Initialize the environment configuration loader"""
        try:
            # Connect to Redis
            self.redis_client = redis.from_url(
                self.redis_settings.redis_dsn,
                encoding='utf-8',
                decode_responses=True,
                max_connections=self.redis_settings.redis_max_connections
            )
            
            # Test connection
            await self.redis_client.ping()
            
            # Load configurations
            await self._load_file_configurations()
            await self._load_redis_configurations()
            await self._apply_environment_overrides()
            
            logger.info(f"Environment Configuration Loader initialized for {self.current_environment.value}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Environment Configuration Loader: {e}")
            raise
    
    async def _load_file_configurations(self) -> None:
        """Load configurations from files"""
        try:
            # Create config directory if it doesn't exist
            self.config_dir.mkdir(parents=True, exist_ok=True)
            
            # Load configurations for each environment
            for env_type in EnvironmentType:
                config_file = self.config_dir / f"{env_type.value}.yaml"
                
                if config_file.exists():
                    await self._load_config_file(config_file, env_type)
                else:
                    # Create default configuration
                    default_config = EnvironmentConfig(
                        name=env_type.value,
                        environment_type=env_type
                    )
                    self.environments[env_type.value] = default_config
                    await self._save_config_file(config_file, default_config)
                    
            self.config_sources.append("file_system")
            
        except Exception as e:
            logger.error(f"Error loading file configurations: {e}")
    
    async def _load_config_file(self, config_file -> None: Path, env_type -> None: EnvironmentType) -> None:
        """Load configuration from YAML file"""
        try:
            with open(config_file, 'r') as f:
                config_data = yaml.safe_load(f)
            
            # Create EnvironmentConfig from loaded data
            config = EnvironmentConfig(
                name=config_data.get('name', env_type.value),
                environment_type=env_type,
                redis_config=config_data.get('redis_config', {}),
                cache_policies=config_data.get('cache_policies', {}),
                security_settings=config_data.get('security_settings', {}),
                performance_settings=config_data.get('performance_settings', {}),
                feature_flags=config_data.get('feature_flags', {}),
                custom_settings=config_data.get('custom_settings', {})
            )
            
            self.environments[env_type.value] = config
            logger.info(f"Loaded configuration for {env_type.value} from file")
            
        except Exception as e:
            logger.error(f"Error loading config file {config_file}: {e}")
            # Create default config as fallback
            self.environments[env_type.value] = EnvironmentConfig(
                name=env_type.value,
                environment_type=env_type
            )
    
    async def _save_config_file(self, config_file -> None: Path, config -> None: EnvironmentConfig) -> None:
        """Save configuration to YAML file"""
        try:
            config_data = {
                'name': config.name,
                'environment_type': config.environment_type.value,
                'redis_config': config.redis_config,
                'cache_policies': config.cache_policies,
                'security_settings': config.security_settings,
                'performance_settings': config.performance_settings,
                'feature_flags': config.feature_flags,
                'custom_settings': config.custom_settings
            }
            
            with open(config_file, 'w') as f:
                yaml.dump(config_data, f, default_flow_style=False, indent=2)
            
            logger.info(f"Saved configuration for {config.name} to file")
            
        except Exception as e:
            logger.error(f"Error saving config file {config_file}: {e}")
    
    async def _load_redis_configurations(self) -> None:
        """Load configurations from Redis"""
        try:
            # Load environment configurations from Redis
            config_data = await self.redis_client.get(self.env_config_key)
            if config_data:
                redis_configs = json.loads(config_data)
                
                for env_name, env_data in redis_configs.items():
                    if env_name in self.environments:
                        # Merge with existing configuration
                        existing_config = self.environments[env_name]
                        self._merge_configurations(existing_config, env_data)
                        
            self.config_sources.append("redis")
            
        except Exception as e:
            logger.error(f"Error loading Redis configurations: {e}")
    
    async def _apply_environment_overrides(self) -> None:
        """Apply environment-specific overrides"""
        try:
            # Check for environment overrides in Redis
            override_key = f"{self.env_override_key}:{self.current_environment.value}"
            override_data = await self.redis_client.get(override_key)
            
            if override_data:
                overrides = json.loads(override_data)
                current_config = self.environments.get(self.current_environment.value)
                
                if current_config:
                    self._merge_configurations(current_config, overrides)
                    logger.info(f"Applied environment overrides for {self.current_environment.value}")
                    
            # Check for environment variable overrides
            self._apply_env_var_overrides()
            
        except Exception as e:
            logger.error(f"Error applying environment overrides: {e}")
    
    def _apply_env_var_overrides(self) -> None:
        """Apply overrides from environment variables"""
        try:
            current_config = self.environments.get(self.current_environment.value)
            if not current_config:
                return
            
            # Redis configuration overrides
            redis_overrides = {}
            for key in ['host', 'port', 'db', 'password', 'username']:
                env_var = f"REDIS_{key.upper()}"
                if env_var in os.environ:
                    value = os.environ[env_var]
                    # Convert port and db to integers
                    if key in ['port', 'db']:
                        value = int(value)
                    redis_overrides[key] = value
            
            if redis_overrides:
                current_config.redis_config.update(redis_overrides)
                logger.info(f"Applied Redis environment variable overrides: {redis_overrides}")
            
            # Security overrides
            if 'REDIS_SSL_ENABLED' in os.environ:
                current_config.security_settings['ssl_enabled'] = os.environ['REDIS_SSL_ENABLED'].lower() == 'true'
            
            if 'REDIS_AUTH_ENABLED' in os.environ:
                current_config.security_settings['auth_enabled'] = os.environ['REDIS_AUTH_ENABLED'].lower() == 'true'
                
        except Exception as e:
            logger.error(f"Error applying environment variable overrides: {e}")
    
    def _merge_configurations(self, base_config -> None: EnvironmentConfig, override_data -> None: Dict[str, Any]) -> None:
        """Merge override data into base configuration"""
        try:
            for section, values in override_data.items():
                if hasattr(base_config, section) and isinstance(values, dict):
                    existing_section = getattr(base_config, section)
                    if isinstance(existing_section, dict):
                        existing_section.update(values)
                    else:
                        setattr(base_config, section, values)
                        
        except Exception as e:
            logger.error(f"Error merging configurations: {e}")
    
    async def get_current_config(self) -> Optional[EnvironmentConfig]:
        """Get configuration for current environment"""
        return self.environments.get(self.current_environment.value)
    
    async def get_environment_config(self, environment: Union[str, EnvironmentType]) -> Optional[EnvironmentConfig]:
        """Get configuration for specific environment"""
        if isinstance(environment, EnvironmentType):
            environment = environment.value
        return self.environments.get(environment)
    
    async def update_environment_config(self, environment: Union[str, EnvironmentType], 
                                      config_updates: Dict[str, Any]) -> bool:
        """Update configuration for specific environment"""
        try:
            if isinstance(environment, EnvironmentType):
                environment = environment.value
            
            config = self.environments.get(environment)
            if not config:
                return False
            
            # Apply updates
            self._merge_configurations(config, config_updates)
            
            # Save to Redis
            await self._save_redis_configuration(environment, config)
            
            # Save to file
            config_file = self.config_dir / f"{environment}.yaml"
            await self._save_config_file(config_file, config)
            
            logger.info(f"Updated configuration for environment: {environment}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating environment configuration: {e}")
            return False
    
    async def _save_redis_configuration(self, environment -> None: str, config -> None: EnvironmentConfig) -> None:
        """Save configuration to Redis"""
        try:
            # Load existing configurations
            existing_configs = {}
            config_data = await self.redis_client.get(self.env_config_key)
            if config_data:
                existing_configs = json.loads(config_data)
            
            # Update with current configuration
            config_dict = {
                'name': config.name,
                'environment_type': config.environment_type.value,
                'redis_config': config.redis_config,
                'cache_policies': config.cache_policies,
                'security_settings': config.security_settings,
                'performance_settings': config.performance_settings,
                'feature_flags': config.feature_flags,
                'custom_settings': config.custom_settings
            }
            
            existing_configs[environment] = config_dict
            
            # Save back to Redis
            await self.redis_client.set(self.env_config_key, json.dumps(existing_configs))
            
        except Exception as e:
            logger.error(f"Error saving Redis configuration: {e}")
    
    async def reload_configurations(self) -> None:
        """Reload all configurations"""
        try:
            self.environments.clear()
            self.config_cache.clear()
            self.config_sources.clear()
            
            await self._load_file_configurations()
            await self._load_redis_configurations()
            await self._apply_environment_overrides()
            
            logger.info("Configurations reloaded successfully")
            
        except Exception as e:
            logger.error(f"Error reloading configurations: {e}")
    
    async def validate_configuration(self, environment: Union[str, EnvironmentType] = None) -> Dict[str, Any]:
        """Validate configuration for environment"""
        try:
            if environment is None:
                environment = self.current_environment.value
            elif isinstance(environment, EnvironmentType):
                environment = environment.value
            
            config = self.environments.get(environment)
            if not config:
                return {"valid": False, "errors": [f"Configuration not found for environment: {environment}"]}
            
            errors = []
            warnings = []
            
            # Validate Redis configuration
            redis_config = config.redis_config
            if not redis_config.get('host'):
                errors.append("Redis host is required")
            
            if not isinstance(redis_config.get('port', 6379), int):
                errors.append("Redis port must be an integer")
            
            # Validate security settings for production
            if config.environment_type == EnvironmentType.PRODUCTION:
                security = config.security_settings
                if not security.get('auth_enabled', False):
                    warnings.append("Authentication should be enabled in production")
                if not security.get('ssl_enabled', False):
                    warnings.append("SSL should be enabled in production")
                if not security.get('encryption_at_rest', False):
                    warnings.append("Encryption at rest recommended for production")
            
            return {
                "valid": len(errors) == 0,
                "errors": errors,
                "warnings": warnings,
                "environment": environment,
                "config_sources": self.config_sources
            }
            
        except Exception as e:
            logger.error(f"Error validating configuration: {e}")
            return {"valid": False, "errors": [str(e)]}
    
    async def get_merged_redis_config(self) -> Dict[str, Any]:
        """Get merged Redis configuration for current environment"""
        try:
            current_config = await self.get_current_config()
            if not current_config:
                return {}
            
            # Start with base Redis settings
            merged_config = self.redis_settings.dict()
            
            # Override with environment-specific settings
            merged_config.update(current_config.redis_config)
            
            return merged_config
            
        except Exception as e:
            logger.error(f"Error getting merged Redis configuration: {e}")
            return {}
    
    async def shutdown(self) -> None:
        """Shutdown the configuration loader"""
        try:
            if self.redis_client:
                await self.redis_client.close()
            logger.info("Environment Configuration Loader shutdown complete")
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")

# Factory function for easy initialization
async def create_environment_config_loader(redis_settings: Optional[RedisSettings] = None) -> EnvironmentConfigLoader:
    """Factory function to create and initialize EnvironmentConfigLoader"""
    loader = EnvironmentConfigLoader(redis_settings)
    await loader.initialize()
    return loader