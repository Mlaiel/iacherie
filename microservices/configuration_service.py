"""
🎯 Configuration Management Microservice
Centralized configuration management service with environment support, secrets management, and real-time updates.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import json
import os
import time
import logging
from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
import yaml
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class ConfigurationType(str, Enum):
    """Configuration value types"""
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    JSON = "json"
    SECRET = "secret"
    LIST = "list"
    DICT = "dict"


class ConfigurationScope(str, Enum):
    """Configuration scopes"""
    GLOBAL = "global"
    SERVICE = "service"
    ENVIRONMENT = "environment"
    USER = "user"
    TENANT = "tenant"


class ConfigurationSource(str, Enum):
    """Configuration sources"""
    FILE = "file"
    ENVIRONMENT = "environment"
    DATABASE = "database"
    CONSUL = "consul"
    ETCD = "etcd"
    VAULT = "vault"
    AWS_PARAMETER_STORE = "aws_parameter_store"
    AZURE_KEY_VAULT = "azure_key_vault"


@dataclass
class ConfigurationEntry:
    """Configuration entry"""
    key: str
    value: Any
    type: ConfigurationType
    scope: ConfigurationScope
    source: ConfigurationSource
    description: str = ""
    is_secret: bool = False
    is_encrypted: bool = False
    last_updated: datetime = field(default_factory=datetime.utcnow)
    version: int = 1
    tags: List[str] = field(default_factory=list)
    validation_rules: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ConfigurationProfile:
    """Configuration profile for environments"""
    name: str
    environment: str
    configurations: Dict[str, ConfigurationEntry] = field(default_factory=dict)
    parent_profile: Optional[str] = None
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)


class ConfigurationValidator:
    """Configuration validation"""
    
    @staticmethod
    def validate_value(value: Any, config_type: ConfigurationType, rules: Dict[str, Any] = None) -> bool:
        """Validate configuration value"""
        rules = rules or {}
        
        try:
            if config_type == ConfigurationType.STRING:
                if not isinstance(value, str):
                    return False
                if 'min_length' in rules and len(value) < rules['min_length']:
                    return False
                if 'max_length' in rules and len(value) > rules['max_length']:
                    return False
                if 'pattern' in rules:
                    import re
                    if not re.match(rules['pattern'], value):
                        return False
                        
            elif config_type == ConfigurationType.INTEGER:
                if not isinstance(value, int):
                    try:
                        int(value)
                    except (ValueError, TypeError):
                        return False
                int_value = int(value)
                if 'min_value' in rules and int_value < rules['min_value']:
                    return False
                if 'max_value' in rules and int_value > rules['max_value']:
                    return False
                    
            elif config_type == ConfigurationType.FLOAT:
                if not isinstance(value, (int, float)):
                    try:
                        float(value)
                    except (ValueError, TypeError):
                        return False
                float_value = float(value)
                if 'min_value' in rules and float_value < rules['min_value']:
                    return False
                if 'max_value' in rules and float_value > rules['max_value']:
                    return False
                    
            elif config_type == ConfigurationType.BOOLEAN:
                if not isinstance(value, bool):
                    if isinstance(value, str):
                        return value.lower() in ['true', 'false', '1', '0', 'yes', 'no']
                    return False
                    
            elif config_type == ConfigurationType.JSON:
                if isinstance(value, str):
                    try:
                        json.loads(value)
                    except json.JSONDecodeError:
                        return False
                        
            elif config_type == ConfigurationType.LIST:
                if not isinstance(value, list):
                    return False
                if 'min_items' in rules and len(value) < rules['min_items']:
                    return False
                if 'max_items' in rules and len(value) > rules['max_items']:
                    return False
                    
            elif config_type == ConfigurationType.DICT:
                if not isinstance(value, dict):
                    return False
                if 'required_keys' in rules:
                    for required_key in rules['required_keys']:
                        if required_key not in value:
                            return False
                            
            return True
            
        except Exception as e:
            logger.error(f"Validation error: {str(e)}")
            return False


class EncryptionManager:
    """Configuration encryption manager"""
    
    def __init__(self, encryption_key: str = None):
        self.encryption_key = encryption_key or self._generate_key()
        
    def _generate_key(self) -> str:
        """Generate encryption key"""
        import secrets
        return secrets.token_urlsafe(32)
        
    def encrypt(self, value: str) -> str:
        """Encrypt configuration value"""
        try:
            from cryptography.fernet import Fernet
            import base64
            
            # Generate key from string
            key = base64.urlsafe_b64encode(self.encryption_key.encode()[:32].ljust(32, b'0'))
            f = Fernet(key)
            
            return f.encrypt(value.encode()).decode()
        except ImportError:
            logger.warning("cryptography library not available, using base64 encoding")
            import base64
            return base64.b64encode(value.encode()).decode()
        except Exception as e:
            logger.error(f"Encryption error: {str(e)}")
            return value
            
    def decrypt(self, encrypted_value: str) -> str:
        """Decrypt configuration value"""
        try:
            from cryptography.fernet import Fernet
            import base64
            
            # Generate key from string
            key = base64.urlsafe_b64encode(self.encryption_key.encode()[:32].ljust(32, b'0'))
            f = Fernet(key)
            
            return f.decrypt(encrypted_value.encode()).decode()
        except ImportError:
            logger.warning("cryptography library not available, using base64 decoding")
            import base64
            return base64.b64decode(encrypted_value.encode()).decode()
        except Exception as e:
            logger.error(f"Decryption error: {str(e)}")
            return encrypted_value


class ConfigurationProvider(ABC):
    """Abstract configuration provider"""
    
    @abstractmethod
    async def load_configurations(self, profile: str = None) -> Dict[str, ConfigurationEntry]:
        """Load configurations from source"""
        pass
        
    @abstractmethod
    async def save_configuration(self, config: ConfigurationEntry) -> bool:
        """Save configuration to source"""
        pass
        
    @abstractmethod
    async def delete_configuration(self, key: str, scope: ConfigurationScope = ConfigurationScope.GLOBAL) -> bool:
        """Delete configuration from source"""
        pass


class FileConfigurationProvider(ConfigurationProvider):
    """File-based configuration provider"""
    
    def __init__(self, config_dir: str = "./config"):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)
        
    async def load_configurations(self, profile: str = None) -> Dict[str, ConfigurationEntry]:
        """Load configurations from files"""
        configurations = {}
        
        # Load global configuration
        global_file = self.config_dir / "global.yaml"
        if global_file.exists():
            configurations.update(await self._load_file(global_file, ConfigurationScope.GLOBAL))
            
        # Load profile-specific configuration
        if profile:
            profile_file = self.config_dir / f"{profile}.yaml"
            if profile_file.exists():
                configurations.update(await self._load_file(profile_file, ConfigurationScope.ENVIRONMENT))
                
        return configurations
        
    async def _load_file(self, file_path: Path, scope: ConfigurationScope) -> Dict[str, ConfigurationEntry]:
        """Load configuration from a file"""
        configurations = {}
        
        try:
            with open(file_path, 'r') as f:
                data = yaml.safe_load(f) or {}
                
            for key, config_data in data.items():
                if isinstance(config_data, dict):
                    configurations[key] = ConfigurationEntry(
                        key=key,
                        value=config_data.get('value'),
                        type=ConfigurationType(config_data.get('type', 'string')),
                        scope=scope,
                        source=ConfigurationSource.FILE,
                        description=config_data.get('description', ''),
                        is_secret=config_data.get('is_secret', False),
                        is_encrypted=config_data.get('is_encrypted', False),
                        tags=config_data.get('tags', []),
                        validation_rules=config_data.get('validation_rules', {})
                    )
                else:
                    configurations[key] = ConfigurationEntry(
                        key=key,
                        value=config_data,
                        type=ConfigurationType.STRING,
                        scope=scope,
                        source=ConfigurationSource.FILE
                    )
                    
        except Exception as e:
            logger.error(f"Error loading configuration file {file_path}: {str(e)}")
            
        return configurations
        
    async def save_configuration(self, config: ConfigurationEntry) -> bool:
        """Save configuration to file"""
        try:
            file_path = self.config_dir / f"{config.scope.value}.yaml"
            
            # Load existing configurations
            data = {}
            if file_path.exists():
                with open(file_path, 'r') as f:
                    data = yaml.safe_load(f) or {}
                    
            # Update configuration
            data[config.key] = {
                'value': config.value,
                'type': config.type.value,
                'description': config.description,
                'is_secret': config.is_secret,
                'is_encrypted': config.is_encrypted,
                'tags': config.tags,
                'validation_rules': config.validation_rules
            }
            
            # Save file
            with open(file_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False)
                
            return True
            
        except Exception as e:
            logger.error(f"Error saving configuration {config.key}: {str(e)}")
            return False
            
    async def delete_configuration(self, key: str, scope: ConfigurationScope = ConfigurationScope.GLOBAL) -> bool:
        """Delete configuration from file"""
        try:
            file_path = self.config_dir / f"{scope.value}.yaml"
            
            if not file_path.exists():
                return False
                
            # Load existing configurations
            with open(file_path, 'r') as f:
                data = yaml.safe_load(f) or {}
                
            # Remove configuration
            if key in data:
                del data[key]
                
                # Save file
                with open(file_path, 'w') as f:
                    yaml.dump(data, f, default_flow_style=False)
                    
                return True
                
            return False
            
        except Exception as e:
            logger.error(f"Error deleting configuration {key}: {str(e)}")
            return False


class EnvironmentConfigurationProvider(ConfigurationProvider):
    """Environment variables configuration provider"""
    
    def __init__(self, prefix: str = "AINFLUE_"):
        self.prefix = prefix
        
    async def load_configurations(self, profile: str = None) -> Dict[str, ConfigurationEntry]:
        """Load configurations from environment variables"""
        configurations = {}
        
        for key, value in os.environ.items():
            if key.startswith(self.prefix):
                config_key = key[len(self.prefix):].lower()
                configurations[config_key] = ConfigurationEntry(
                    key=config_key,
                    value=value,
                    type=self._infer_type(value),
                    scope=ConfigurationScope.ENVIRONMENT,
                    source=ConfigurationSource.ENVIRONMENT,
                    description=f"Environment variable: {key}"
                )
                
        return configurations
        
    def _infer_type(self, value: str) -> ConfigurationType:
        """Infer configuration type from string value"""
        # Try boolean
        if value.lower() in ['true', 'false']:
            return ConfigurationType.BOOLEAN
            
        # Try integer
        try:
            int(value)
            return ConfigurationType.INTEGER
        except ValueError:
            pass
            
        # Try float
        try:
            float(value)
            return ConfigurationType.FLOAT
        except ValueError:
            pass
            
        # Try JSON
        try:
            json.loads(value)
            return ConfigurationType.JSON
        except json.JSONDecodeError:
            pass
            
        # Default to string
        return ConfigurationType.STRING
        
    async def save_configuration(self, config: ConfigurationEntry) -> bool:
        """Save configuration to environment (runtime only)"""
        env_key = f"{self.prefix}{config.key.upper()}"
        os.environ[env_key] = str(config.value)
        return True
        
    async def delete_configuration(self, key: str, scope: ConfigurationScope = ConfigurationScope.GLOBAL) -> bool:
        """Delete configuration from environment"""
        env_key = f"{self.prefix}{key.upper()}"
        if env_key in os.environ:
            del os.environ[env_key]
            return True
        return False


class ConfigurationService:
    """Centralized Configuration Management Service"""
    
    def __init__(self, name: str = "configuration_service"):
        self.name = name
        self.profiles: Dict[str, ConfigurationProfile] = {}
        self.active_profile: Optional[str] = None
        self.providers: List[ConfigurationProvider] = []
        self.validator = ConfigurationValidator()
        self.encryption_manager = EncryptionManager()
        self.change_listeners: List[Callable] = []
        self.cache: Dict[str, ConfigurationEntry] = {}
        self.cache_ttl = 300  # 5 minutes
        self.last_cache_update = 0
        
        # Add default providers
        self.add_provider(FileConfigurationProvider())
        self.add_provider(EnvironmentConfigurationProvider())
        
    def add_provider(self, provider: ConfigurationProvider):
        """Add configuration provider"""
        self.providers.append(provider)
        logger.info(f"Added configuration provider: {type(provider).__name__}")
        
    def add_change_listener(self, listener: Callable[[str, ConfigurationEntry, ConfigurationEntry], None]):
        """Add configuration change listener"""
        self.change_listeners.append(listener)
        
    async def load_profile(self, profile_name: str, environment: str = "production") -> ConfigurationProfile:
        """Load configuration profile"""
        if profile_name in self.profiles:
            return self.profiles[profile_name]
            
        # Create new profile
        profile = ConfigurationProfile(name=profile_name, environment=environment)
        
        # Load configurations from all providers
        for provider in self.providers:
            try:
                configurations = await provider.load_configurations(profile_name)
                profile.configurations.update(configurations)
            except Exception as e:
                logger.error(f"Error loading from provider {type(provider).__name__}: {str(e)}")
                
        self.profiles[profile_name] = profile
        logger.info(f"Loaded configuration profile: {profile_name} ({len(profile.configurations)} configs)")
        
        return profile
        
    async def set_active_profile(self, profile_name: str):
        """Set active configuration profile"""
        if profile_name not in self.profiles:
            await self.load_profile(profile_name)
            
        self.active_profile = profile_name
        self._invalidate_cache()
        logger.info(f"Set active profile: {profile_name}")
        
    async def get_configuration(self, key: str, default: Any = None, profile: str = None) -> Any:
        """Get configuration value"""
        profile_name = profile or self.active_profile or "default"
        
        # Check cache first
        cache_key = f"{profile_name}:{key}"
        if self._is_cache_valid() and cache_key in self.cache:
            config = self.cache[cache_key]
            return self._convert_value(config.value, config.type)
            
        # Load from profile
        if profile_name not in self.profiles:
            await self.load_profile(profile_name)
            
        profile_obj = self.profiles.get(profile_name)
        if not profile_obj:
            return default
            
        config = profile_obj.configurations.get(key)
        if not config:
            return default
            
        # Cache the result
        self.cache[cache_key] = config
        
        # Decrypt if needed
        value = config.value
        if config.is_encrypted and config.is_secret:
            value = self.encryption_manager.decrypt(value)
            
        return self._convert_value(value, config.type)
        
    async def set_configuration(self, key: str, value: Any, config_type: ConfigurationType = ConfigurationType.STRING,
                              scope: ConfigurationScope = ConfigurationScope.GLOBAL,
                              description: str = "", is_secret: bool = False,
                              validation_rules: Dict[str, Any] = None,
                              profile: str = None) -> bool:
        """Set configuration value"""
        validation_rules = validation_rules or {}
        profile_name = profile or self.active_profile or "default"
        
        # Validate value
        if not self.validator.validate_value(value, config_type, validation_rules):
            logger.error(f"Invalid configuration value for {key}")
            return False
            
        # Encrypt if secret
        actual_value = value
        is_encrypted = False
        if is_secret:
            actual_value = self.encryption_manager.encrypt(str(value))
            is_encrypted = True
            
        # Get old configuration for change notification
        old_config = None
        if profile_name in self.profiles:
            old_config = self.profiles[profile_name].configurations.get(key)
            
        # Create configuration entry
        config = ConfigurationEntry(
            key=key,
            value=actual_value,
            type=config_type,
            scope=scope,
            source=ConfigurationSource.FILE,  # Default to file
            description=description,
            is_secret=is_secret,
            is_encrypted=is_encrypted,
            validation_rules=validation_rules,
            last_updated=datetime.utcnow(),
            version=(old_config.version + 1) if old_config else 1
        )
        
        # Ensure profile exists
        if profile_name not in self.profiles:
            await self.load_profile(profile_name)
            
        # Update profile
        self.profiles[profile_name].configurations[key] = config
        
        # Save to providers
        for provider in self.providers:
            try:
                await provider.save_configuration(config)
            except Exception as e:
                logger.error(f"Error saving to provider {type(provider).__name__}: {str(e)}")
                
        # Invalidate cache
        self._invalidate_cache()
        
        # Notify listeners
        for listener in self.change_listeners:
            try:
                await asyncio.create_task(asyncio.coroutine(listener)(key, old_config, config))
            except Exception as e:
                logger.error(f"Error in change listener: {str(e)}")
                
        logger.info(f"Set configuration: {key} = {value if not is_secret else '***'}")
        return True
        
    async def delete_configuration(self, key: str, profile: str = None) -> bool:
        """Delete configuration"""
        profile_name = profile or self.active_profile or "default"
        
        # Get old configuration for change notification
        old_config = None
        if profile_name in self.profiles and key in self.profiles[profile_name].configurations:
            old_config = self.profiles[profile_name].configurations[key]
            
        # Delete from profile
        if profile_name in self.profiles:
            self.profiles[profile_name].configurations.pop(key, None)
            
        # Delete from providers
        for provider in self.providers:
            try:
                await provider.delete_configuration(key, old_config.scope if old_config else ConfigurationScope.GLOBAL)
            except Exception as e:
                logger.error(f"Error deleting from provider {type(provider).__name__}: {str(e)}")
                
        # Invalidate cache
        self._invalidate_cache()
        
        # Notify listeners
        for listener in self.change_listeners:
            try:
                await asyncio.create_task(asyncio.coroutine(listener)(key, old_config, None))
            except Exception as e:
                logger.error(f"Error in change listener: {str(e)}")
                
        logger.info(f"Deleted configuration: {key}")
        return True
        
    def _convert_value(self, value: Any, config_type: ConfigurationType) -> Any:
        """Convert configuration value to appropriate type"""
        if value is None:
            return None
            
        try:
            if config_type == ConfigurationType.STRING:
                return str(value)
            elif config_type == ConfigurationType.INTEGER:
                return int(value)
            elif config_type == ConfigurationType.FLOAT:
                return float(value)
            elif config_type == ConfigurationType.BOOLEAN:
                if isinstance(value, bool):
                    return value
                if isinstance(value, str):
                    return value.lower() in ['true', '1', 'yes', 'on']
                return bool(value)
            elif config_type == ConfigurationType.JSON:
                if isinstance(value, str):
                    return json.loads(value)
                return value
            elif config_type == ConfigurationType.LIST:
                if isinstance(value, str):
                    return json.loads(value)
                return list(value) if value else []
            elif config_type == ConfigurationType.DICT:
                if isinstance(value, str):
                    return json.loads(value)
                return dict(value) if value else {}
            else:
                return value
                
        except Exception as e:
            logger.error(f"Error converting value {value} to type {config_type}: {str(e)}")
            return value
            
    def _is_cache_valid(self) -> bool:
        """Check if cache is still valid"""
        return time.time() - self.last_cache_update < self.cache_ttl
        
    def _invalidate_cache(self):
        """Invalidate configuration cache"""
        self.cache.clear()
        self.last_cache_update = 0
        
    async def reload_configurations(self, profile: str = None):
        """Reload configurations from sources"""
        profile_name = profile or self.active_profile
        if profile_name and profile_name in self.profiles:
            del self.profiles[profile_name]
            await self.load_profile(profile_name)
            self._invalidate_cache()
            logger.info(f"Reloaded configurations for profile: {profile_name}")
            
    def get_all_configurations(self, profile: str = None) -> Dict[str, ConfigurationEntry]:
        """Get all configurations for a profile"""
        profile_name = profile or self.active_profile or "default"
        profile_obj = self.profiles.get(profile_name)
        return profile_obj.configurations if profile_obj else {}
        
    def get_configurations_by_scope(self, scope: ConfigurationScope, profile: str = None) -> Dict[str, ConfigurationEntry]:
        """Get configurations by scope"""
        all_configs = self.get_all_configurations(profile)
        return {k: v for k, v in all_configs.items() if v.scope == scope}
        
    def get_secret_configurations(self, profile: str = None) -> Dict[str, ConfigurationEntry]:
        """Get secret configurations"""
        all_configs = self.get_all_configurations(profile)
        return {k: v for k, v in all_configs.items() if v.is_secret}
        
    def get_status(self) -> Dict[str, Any]:
        """Get service status"""
        total_configs = sum(len(profile.configurations) for profile in self.profiles.values())
        secret_configs = sum(
            len([c for c in profile.configurations.values() if c.is_secret])
            for profile in self.profiles.values()
        )
        
        return {
            "name": self.name,
            "status": "running",
            "active_profile": self.active_profile,
            "profiles_count": len(self.profiles),
            "total_configurations": total_configs,
            "secret_configurations": secret_configs,
            "providers_count": len(self.providers),
            "cache_size": len(self.cache),
            "cache_valid": self._is_cache_valid(),
            "timestamp": datetime.utcnow().isoformat()
        }


def create_configuration_service(config: Dict[str, Any] = None) -> ConfigurationService:
    """Factory function to create Configuration service"""
    config = config or {}
    service_name = config.get('name', 'configuration_service')
    
    service = ConfigurationService(service_name)
    
    # Configure cache TTL
    if 'cache_ttl' in config:
        service.cache_ttl = config['cache_ttl']
        
    # Configure encryption key
    if 'encryption_key' in config:
        service.encryption_manager.encryption_key = config['encryption_key']
        
    # Add additional providers if specified
    if 'providers' in config:
        for provider_config in config['providers']:
            # This would need to be extended based on provider types
            pass
            
    return service


__all__ = [
    'ConfigurationService', 'ConfigurationEntry', 'ConfigurationProfile',
    'ConfigurationType', 'ConfigurationScope', 'ConfigurationSource',
    'FileConfigurationProvider', 'EnvironmentConfigurationProvider',
    'create_configuration_service'
]