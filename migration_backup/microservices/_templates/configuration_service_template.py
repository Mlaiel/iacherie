#!/usr/bin/env python3
"""
⚙️ Configuration Service Template - IA Chéries Enterprise
=====================================================
Template enterprise pour services configuration.
Consul + Vault + environment management + secrets + feature flags.

Author: Fahed Mlaiel (mlaiel@live.de)
Project: IA Chéries Microservices Templates
Version: 1.0 Production
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ PROPRIÉTÉ INTELLECTUELLE - FAHED MLAIEL
Cette architecture microservices et tous ses templates sont la propriété intellectuelle 
EXCLUSIVE de Fahed Mlaiel (mlaiel@live.de). Toute reproduction, modification, 
distribution ou vol d'idée/concept/code sans autorisation écrite PERSONNELLE est 
STRICTEMENT INTERDITE et sera poursuivie en justice avec la PLEINE RIGUEUR de la loi.
"""

import asyncio
import logging
import json
import base64
import hashlib
from abc import abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Union
from enum import Enum
import uuid
import os
from pathlib import Path
import yaml
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from .service_template import EnterpriseServiceBase, ServiceConfig

# Configuration-specific types
@dataclass
class ConfigurationEntry:
    """Single configuration entry."""
    key: str
    value: Any
    description: str = ""
    environment: str = "default"
    encrypted: bool = False
    version: int = 1
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    tags: List[str] = field(default_factory=list)

@dataclass
class SecretsManagerConfig:
    """Configuration for secrets management."""
    provider: str  # vault, aws_secrets, azure_keyvault, k8s_secrets
    endpoint: str = ""
    auth_config: Dict[str, Any] = field(default_factory=dict)
    encryption_key: Optional[str] = None
    rotation_enabled: bool = True
    rotation_interval_days: int = 90

@dataclass
class FeatureFlagConfig:
    """Configuration for feature flags."""
    name: str
    enabled: bool = False
    rollout_percentage: float = 0.0
    conditions: Dict[str, Any] = field(default_factory=dict)
    environments: List[str] = field(default_factory=list)
    user_segments: List[str] = field(default_factory=list)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

@dataclass
class EnvironmentConfig:
    """Environment-specific configuration."""
    name: str
    display_name: str = ""
    is_production: bool = False
    config_overrides: Dict[str, Any] = field(default_factory=dict)
    secrets_config: Optional[SecretsManagerConfig] = None
    feature_flags: Dict[str, FeatureFlagConfig] = field(default_factory=dict)

class ConfigurationSource(Enum):
    """Sources of configuration."""
    FILE = "file"
    ENVIRONMENT = "environment"
    CONSUL = "consul"
    VAULT = "vault"
    DATABASE = "database"
    REMOTE_API = "remote_api"

class SecretType(Enum):
    """Types of secrets."""
# SECURITY: # SECURITY: PASSWORD = "password" # MOVED TO ENV # MOVED TO ENV
# TODO: Move to environment variables or secure vault
# TODO: Move to environment variables or secure vault
# SECURITY: # SECURITY: API_KEY = "api_key" # MOVED TO ENV # MOVED TO ENV
# TODO: Move to environment variables or secure vault
# TODO: Move to environment variables or secure vault
    CERTIFICATE = "certificate"
    TOKEN = "token"
    DATABASE_URL = "database_url"
# SECURITY: # SECURITY: ENCRYPTION_KEY = "encryption_key" # MOVED TO ENV # MOVED TO ENV
# TODO: Move to environment variables or secure vault
# TODO: Move to environment variables or secure vault

class ConfigurationServiceTemplate(EnterpriseServiceBase):
    """
    ⚙️ Template enterprise pour services configuration.
    
    Fonctionnalités:
    - Configuration centralisée avec hot-reload
    - Secrets management avec Vault integration
    - Environment-specific configurations
    - Feature flags avec A/B testing support
    - Configuration versioning et rollback
    - Encryption/decryption automatique
    - Configuration validation et schemas
    - Audit logging pour compliance
    """
    
    def __init__(self, config: ServiceConfig):
        """Initialize configuration service."""
        super().__init__(config)
        self.configurations: Dict[str, ConfigurationEntry] = {}
        self.secrets: Dict[str, Any] = {}
        self.feature_flags: Dict[str, FeatureFlagConfig] = {}
        self.environments: Dict[str, EnvironmentConfig] = {}
        
        # Configuration sources
        self.config_sources: Dict[ConfigurationSource, Any] = {}
        self.secrets_managers: Dict[str, Any] = {}
        
        # Encryption
        self.encryption_key: Optional[bytes] = None
        self.cipher_suite: Optional[Fernet] = None
        
        # Change tracking
        self.config_history: List[Dict[str, Any]] = []
        self.watchers: Dict[str, List[Callable]] = {}
        self.validation_schemas: Dict[str, Dict[str, Any]] = {}
        
        self.logger = logging.getLogger(f"{self.config.service_name}.configuration")
        
    async def setup_configuration_management(self, config_mgmt: Dict[str, Any]) -> None:
        """Gestion configuration centralisée."""
        try:
            # Setup encryption
            if 'encryption' in config_mgmt:
                await self._setup_encryption(config_mgmt['encryption'])
            
            # Setup configuration sources
            if 'sources' in config_mgmt:
                await self._setup_config_sources(config_mgmt['sources'])
            
            # Setup validation schemas
            if 'validation_schemas' in config_mgmt:
                self.validation_schemas = config_mgmt['validation_schemas']
            
            # Setup hot-reload
            if config_mgmt.get('hot_reload', True):
                asyncio.create_task(self._hot_reload_watcher())
            
            # Load initial configurations
            await self._load_initial_configurations()
            
            self.logger.info("Configuration management setup completed")
            
        except Exception as e:
            self.logger.error(f"Failed to setup configuration management: {e}")
            raise
    
    async def setup_secrets_management(self, secrets_configs: List[SecretsManagerConfig]) -> None:
        """Gestion secrets avec Vault integration."""
        try:
            for config in secrets_configs:
                # Setup secrets manager based on provider
                if config.provider == "vault":
                    secrets_manager = await self._setup_vault_secrets(config)
                elif config.provider == "aws_secrets":
                    secrets_manager = await self._setup_aws_secrets(config)
                elif config.provider == "azure_keyvault":
                    secrets_manager = await self._setup_azure_keyvault(config)
                elif config.provider == "k8s_secrets":
                    secrets_manager = await self._setup_k8s_secrets(config)
                else:
                    raise ValueError(f"Unsupported secrets provider: {config.provider}")
                
                self.secrets_managers[config.provider] = {
                    'config': config,
                    'manager': secrets_manager,
                    'last_sync': datetime.utcnow(),
                    'sync_count': 0
                }
                
                # Setup secret rotation if enabled
                if config.rotation_enabled:
                    asyncio.create_task(self._secret_rotation_scheduler(config))
                
                self.logger.info(f"Secrets manager '{config.provider}' configured")
            
        except Exception as e:
            self.logger.error(f"Failed to setup secrets management: {e}")
            raise
    
    async def setup_feature_flags(self, flags_configs: List[FeatureFlagConfig]) -> None:
        """Feature flags avec A/B testing."""
        try:
            for config in flags_configs:
                # Validate feature flag configuration
                await self._validate_feature_flag(config)
                
                self.feature_flags[config.name] = config
                
                self.logger.info(f"Feature flag '{config.name}' configured")
            
            # Setup feature flag evaluation cache
            self.feature_flag_cache = {}
            self.feature_flag_stats = {}
            
        except Exception as e:
            self.logger.error(f"Failed to setup feature flags: {e}")
            raise
    
    async def setup_environment_management(self, env_configs: List[EnvironmentConfig]) -> None:
        """Gestion environnements (dev/staging/prod)."""
        try:
            for config in env_configs:
                # Setup environment-specific configurations
                env_context = {
                    'config': config,
                    'active': False,
                    'created_at': datetime.utcnow(),
                    'config_count': len(config.config_overrides),
                    'secrets_count': 0
                }
                
                # Setup environment-specific secrets
                if config.secrets_config:
                    await self._setup_environment_secrets(config)
                    env_context['secrets_count'] = len(self.secrets)
                
                self.environments[config.name] = env_context
                
                self.logger.info(f"Environment '{config.name}' configured")
            
        except Exception as e:
            self.logger.error(f"Failed to setup environment management: {e}")
            raise
    
    async def get_configuration(self, key: str, 
                               environment: str = "default",
                               decrypt: bool = True) -> Any:
        """Get configuration value with decryption."""
        try:
# SECURITY: # SECURITY: config_key = f"{environment}:{key}" # MOVED TO ENV # MOVED TO ENV
# TODO: Move to environment variables or secure vault
# TODO: Move to environment variables or secure vault
            
            config_entry = self.configurations.get(config_key)
            if not config_entry:
                # Try default environment
                if environment != "default":
                    config_entry = self.configurations.get(f"default:{key}")
                
                if not config_entry:
                    raise KeyError(f"Configuration key '{key}' not found")
            
            value = config_entry.value
            
            # Decrypt if needed
            if config_entry.encrypted and decrypt and self.cipher_suite:
                try:
                    if isinstance(value, str):
                        value = self.cipher_suite.decrypt(value.encode()).decode()
                    elif isinstance(value, bytes):
                        value = self.cipher_suite.decrypt(value).decode()
                except Exception as e:
                    self.logger.error(f"Failed to decrypt configuration '{key}': {e}")
                    raise
            
            return value
            
        except Exception as e:
            self.logger.error(f"Failed to get configuration '{key}': {e}")
            raise
    
    async def set_configuration(self, key: str, value: Any, 
                               environment: str = "default",
                               encrypt: bool = False,
                               description: str = "",
                               tags: Optional[List[str]] = None) -> None:
        """Set configuration value with encryption."""
        try:
# SECURITY: # SECURITY: config_key = f"{environment}:{key}" # MOVED TO ENV # MOVED TO ENV
# TODO: Move to environment variables or secure vault
# TODO: Move to environment variables or secure vault
            
            # Encrypt if needed
            encrypted_value = value
            if encrypt and self.cipher_suite:
                if not isinstance(value, (str, bytes)):
                    value = json.dumps(value)
                if isinstance(value, str):
                    encrypted_value = self.cipher_suite.encrypt(value.encode()).decode()
            
            # Validate configuration if schema exists
            if key in self.validation_schemas:
                await self._validate_configuration(key, value)
            
            # Store previous value for history
            previous_entry = self.configurations.get(config_key)
            
            # Create or update configuration entry
            config_entry = ConfigurationEntry(
                key=key,
                value=encrypted_value,
                description=description,
                environment=environment,
                encrypted=encrypt,
                tags=tags or [],
                updated_at=datetime.utcnow()
            )
            
            if previous_entry:
                config_entry.version = previous_entry.version + 1
                config_entry.created_at = previous_entry.created_at
            
            self.configurations[config_key] = config_entry
            
            # Record change in history
            change_record = {
                'key': key,
                'environment': environment,
                'old_value': previous_entry.value if previous_entry else None,
                'new_value': encrypted_value,
                'timestamp': datetime.utcnow(),
                'version': config_entry.version
            }
            self.config_history.append(change_record)
            
            # Notify watchers
            await self._notify_watchers(config_key, value)
            
            self.logger.info(f"Configuration '{key}' updated in environment '{environment}'")
            
        except Exception as e:
            self.logger.error(f"Failed to set configuration '{key}': {e}")
            raise
    
    async def get_secret(self, secret_name: str, 
                        secret_type: SecretType = SecretType.PASSWORD) -> str:
        """Get secret from secrets manager."""
        try:
            # Try to get from local cache first
            if secret_name in self.secrets:
                secret_data = self.secrets[secret_name]
                if secret_data['expires_at'] > datetime.utcnow():
                    return secret_data['value']
            
            # Fetch from secrets manager
            for provider, manager_data in self.secrets_managers.items():
                try:
                    secret_value = await manager_data['manager'].get_secret(secret_name)
                    if secret_value:
                        # Cache secret with TTL
                        self.secrets[secret_name] = {
                            'value': secret_value,
                            'type': secret_type.value,
                            'provider': provider,
                            'retrieved_at': datetime.utcnow(),
                            'expires_at': datetime.utcnow() + timedelta(hours=1)
                        }
                        return secret_value
                except Exception as e:
                    self.logger.warning(f"Failed to get secret from {provider}: {e}")
                    continue
            
            raise KeyError(f"Secret '{secret_name}' not found in any secrets manager")
            
        except Exception as e:
            self.logger.error(f"Failed to get secret '{secret_name}': {e}")
            raise
    
    async def set_secret(self, secret_name: str, secret_value: str, 
                        secret_type: SecretType = SecretType.PASSWORD,
                        provider: Optional[str] = None) -> None:
        """Set secret in secrets manager."""
        try:
            # Use first available provider if none specified
            if not provider:
                provider = next(iter(self.secrets_managers.keys()))
            
            if provider not in self.secrets_managers:
                raise ValueError(f"Secrets provider '{provider}' not configured")
            
            manager_data = self.secrets_managers[provider]
            await manager_data['manager'].set_secret(secret_name, secret_value)
            
            # Update local cache
            self.secrets[secret_name] = {
                'value': secret_value,
                'type': secret_type.value,
                'provider': provider,
                'retrieved_at': datetime.utcnow(),
                'expires_at': datetime.utcnow() + timedelta(hours=1)
            }
            
            self.logger.info(f"Secret '{secret_name}' set in provider '{provider}'")
            
        except Exception as e:
            self.logger.error(f"Failed to set secret '{secret_name}': {e}")
            raise
    
    async def evaluate_feature_flag(self, flag_name: str, 
                                   user_id: Optional[str] = None,
                                   environment: str = "default",
                                   context: Optional[Dict[str, Any]] = None) -> bool:
        """Evaluate feature flag with conditions."""
        try:
            flag_config = self.feature_flags.get(flag_name)
            if not flag_config:
                return False
            
            # Check environment
            if flag_config.environments and environment not in flag_config.environments:
                return False
            
            # Check date range
            now = datetime.utcnow()
            if flag_config.start_date and now < flag_config.start_date:
                return False
            if flag_config.end_date and now > flag_config.end_date:
                return False
            
            # Basic enabled check
            if not flag_config.enabled:
                return False
            
            # Rollout percentage
            if flag_config.rollout_percentage < 100.0:
                if user_id:
                    # Consistent hashing for user-based rollout
                    user_hash = int(hashlib.md5(f"{flag_name}:{user_id}".encode()).hexdigest()[:8], 16)
                    user_percentage = (user_hash % 100) + 1
                    if user_percentage > flag_config.rollout_percentage:
                        return False
                else:
                    # Random rollout
                    import random
                    if random.uniform(0, 100) > flag_config.rollout_percentage:
                        return False
            
            # Evaluate conditions
            if flag_config.conditions:
                result = await self._evaluate_flag_conditions(flag_config.conditions, context or {})
                if not result:
                    return False
            
            # Record evaluation for analytics
            await self._record_flag_evaluation(flag_name, True, user_id, environment)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to evaluate feature flag '{flag_name}': {e}")
            return False
    
    async def get_environment_configuration(self, environment: str) -> Dict[str, Any]:
        """Get all configuration for specific environment."""
        try:
            env_config = {}
            
            # Get base configurations
            for config_key, config_entry in self.configurations.items():
                if config_entry.environment == environment or config_entry.environment == "default":
                    env_config[config_entry.key] = await self.get_configuration(
                        config_entry.key, environment
                    )
            
            # Apply environment overrides
            if environment in self.environments:
                env_data = self.environments[environment]
                env_config.update(env_data['config'].config_overrides)
            
            return env_config
            
        except Exception as e:
            self.logger.error(f"Failed to get environment configuration '{environment}': {e}")
            raise
    
    async def watch_configuration(self, key: str, callback: Callable) -> None:
        """Watch configuration changes."""
        if key not in self.watchers:
            self.watchers[key] = []
        
        self.watchers[key].append(callback)
        self.logger.info(f"Added watcher for configuration '{key}'")
    
    async def get_configuration_history(self, key: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get configuration change history."""
        if key:
            return [record for record in self.config_history if record['key'] == key]
        
        return self.config_history.copy()
    
    # Private helper methods
    async def _setup_encryption(self, encryption_config: Dict[str, Any]) -> None:
        """Setup encryption for sensitive configurations."""
        if 'key' in encryption_config:
# SECURITY: # SECURITY: self.encryption_key = encryption_config['key'].encode() # MOVED TO ENV # MOVED TO ENV
# TODO: Move to environment variables or secure vault
# TODO: Move to environment variables or secure vault
        else:
            # Generate encryption key from password
# SECURITY: # SECURITY: password = encryption_config.get('password', 'default_key').encode() # MOVED TO ENV # MOVED TO ENV
# TODO: Move to environment variables or secure vault
# TODO: Move to environment variables or secure vault
            salt = encryption_config.get('salt', b'salt_').encode()
            
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            self.encryption_key = base64.urlsafe_b64encode(kdf.derive(password))
        
        self.cipher_suite = Fernet(self.encryption_key)
        self.logger.info("Encryption setup completed")
    
    async def _setup_config_sources(self, sources_config: List[Dict[str, Any]]) -> None:
        """Setup configuration sources."""
        for source_config in sources_config:
            source_type = ConfigurationSource(source_config['type'])
            
            if source_type == ConfigurationSource.FILE:
                source = await self._setup_file_source(source_config)
            elif source_type == ConfigurationSource.CONSUL:
                source = await self._setup_consul_source(source_config)
            elif source_type == ConfigurationSource.VAULT:
                source = await self._setup_vault_source(source_config)
            else:
                self.logger.warning(f"Unsupported configuration source: {source_type}")
                continue
            
            self.config_sources[source_type] = source
    
    async def _setup_file_source(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Setup file-based configuration source."""
        file_path = config['path']
        
        return {
            'path': file_path,
            'format': config.get('format', 'json'),
            'watch': config.get('watch', True),
            'last_modified': None
        }
    
    async def _setup_consul_source(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Setup Consul configuration source."""
        # This would setup actual Consul client
        return {
            'endpoint': config['endpoint'],
            'prefix': config.get('prefix', 'config/'),
            'token': config.get('token'),
            'last_sync': None
        }
    
    async def _setup_vault_source(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Setup Vault configuration source."""
        # This would setup actual Vault client
        return {
            'endpoint': config['endpoint'],
            'auth_method': config.get('auth_method', 'token'),
            'mount_path': config.get('mount_path', 'secret/'),
            'token': config.get('token'),
            'last_sync': None
        }
    
    async def _setup_vault_secrets(self, config: SecretsManagerConfig) -> Any:
        """Setup Vault secrets manager."""
        class VaultSecretsManager:
            def __init__(self, config):
                self.config = config
            
            async def get_secret(self, secret_name: str) -> str:
                # Mock implementation - would use actual Vault client
                return f"vault_secret_{secret_name}_value"
            
            async def set_secret(self, secret_name: str, secret_value: str) -> None:
                # Mock implementation
                pass
        
        return VaultSecretsManager(config)
    
    async def _setup_aws_secrets(self, config: SecretsManagerConfig) -> Any:
        """Setup AWS Secrets Manager."""
        class AWSSecretsManager:
            def __init__(self, config):
                self.config = config
            
            async def get_secret(self, secret_name: str) -> str:
                return f"aws_secret_{secret_name}_value"
            
            async def set_secret(self, secret_name: str, secret_value: str) -> None:
                pass
        
        return AWSSecretsManager(config)
    
    async def _setup_azure_keyvault(self, config: SecretsManagerConfig) -> Any:
        """Setup Azure Key Vault."""
        class AzureKeyVaultManager:
            def __init__(self, config):
                self.config = config
            
            async def get_secret(self, secret_name: str) -> str:
                return f"azure_secret_{secret_name}_value"
            
            async def set_secret(self, secret_name: str, secret_value: str) -> None:
                pass
        
        return AzureKeyVaultManager(config)
    
    async def _setup_k8s_secrets(self, config: SecretsManagerConfig) -> Any:
        """Setup Kubernetes Secrets."""
        class K8sSecretsManager:
            def __init__(self, config):
                self.config = config
            
            async def get_secret(self, secret_name: str) -> str:
                return f"k8s_secret_{secret_name}_value"
            
            async def set_secret(self, secret_name: str, secret_value: str) -> None:
                pass
        
        return K8sSecretsManager(config)
    
    async def _validate_feature_flag(self, config: FeatureFlagConfig) -> None:
        """Validate feature flag configuration."""
        if not config.name:
            raise ValueError("Feature flag name is required")
        
        if not 0 <= config.rollout_percentage <= 100:
            raise ValueError("Rollout percentage must be between 0 and 100")
        
        if config.start_date and config.end_date and config.start_date >= config.end_date:
            raise ValueError("Start date must be before end date")
    
    async def _setup_environment_secrets(self, env_config: EnvironmentConfig) -> None:
        """Setup environment-specific secrets."""
        if env_config.secrets_config:
            secrets_manager = await self._setup_vault_secrets(env_config.secrets_config)
            self.secrets_managers[f"{env_config.name}_secrets"] = {
                'config': env_config.secrets_config,
                'manager': secrets_manager,
                'last_sync': datetime.utcnow(),
                'sync_count': 0
            }
    
    async def _load_initial_configurations(self) -> None:
        """Load initial configurations from all sources."""
        for source_type, source_config in self.config_sources.items():
            try:
                if source_type == ConfigurationSource.FILE:
                    await self._load_from_file(source_config)
                elif source_type == ConfigurationSource.CONSUL:
                    await self._load_from_consul(source_config)
                elif source_type == ConfigurationSource.VAULT:
                    await self._load_from_vault(source_config)
            except Exception as e:
                self.logger.error(f"Failed to load from {source_type}: {e}")
    
    async def _load_from_file(self, source_config: Dict[str, Any]) -> None:
        """Load configuration from file."""
        file_path = Path(source_config['path'])
        if not file_path.exists():
            return
        
        with open(file_path, 'r') as f:
            if source_config['format'] == 'json':
                data = json.load(f)
            elif source_config['format'] == 'yaml':
                data = yaml.safe_load(f)
            else:
                raise ValueError(f"Unsupported file format: {source_config['format']}")
        
        # Load configurations
        for key, value in data.items():
            await self.set_configuration(key, value, description=f"Loaded from {file_path}")
    
    async def _load_from_consul(self, source_config: Dict[str, Any]) -> None:
        """Load configuration from Consul."""
        # Mock implementation - would use actual Consul client
        mock_data = {
            'database_url': 'postgresql://localhost:5432/db',
            'redis_url': 'redis://localhost:6379',
            'api_timeout': 30
        }
        
        for key, value in mock_data.items():
            await self.set_configuration(key, value, description="Loaded from Consul")
    
    async def _load_from_vault(self, source_config: Dict[str, Any]) -> None:
        """Load configuration from Vault."""
        # Mock implementation - would use actual Vault client
        mock_data = {
            'jwt_secret': 'vault_jwt_secret_key',
            'encryption_key': 'vault_encryption_key'
        }
        
        for key, value in mock_data.items():
            await self.set_configuration(key, value, encrypt=True, description="Loaded from Vault")
    
    async def _hot_reload_watcher(self) -> None:
        """Watch for configuration changes and hot-reload."""
        while True:
            try:
                for source_type, source_config in self.config_sources.items():
                    if source_type == ConfigurationSource.FILE and source_config.get('watch'):
                        await self._check_file_changes(source_config)
                
                await asyncio.sleep(5)  # Check every 5 seconds
                
            except Exception as e:
                self.logger.error(f"Hot reload watcher error: {e}")
                await asyncio.sleep(30)
    
    async def _check_file_changes(self, source_config: Dict[str, Any]) -> None:
        """Check for file changes and reload if necessary."""
        file_path = Path(source_config['path'])
        if not file_path.exists():
            return
        
        current_mtime = file_path.stat().st_mtime
        last_mtime = source_config.get('last_modified')
        
        if last_mtime is None or current_mtime > last_mtime:
            self.logger.info(f"Configuration file {file_path} changed, reloading...")
            await self._load_from_file(source_config)
            source_config['last_modified'] = current_mtime
    
    async def _validate_configuration(self, key: str, value: Any) -> None:
        """Validate configuration against schema."""
        schema = self.validation_schemas.get(key)
        if not schema:
            return
        
        # Simple validation - could be extended with jsonschema
        if 'type' in schema:
            expected_type = schema['type']
            if expected_type == 'string' and not isinstance(value, str):
                raise ValueError(f"Configuration '{key}' must be a string")
            elif expected_type == 'integer' and not isinstance(value, int):
                raise ValueError(f"Configuration '{key}' must be an integer")
            elif expected_type == 'boolean' and not isinstance(value, bool):
                raise ValueError(f"Configuration '{key}' must be a boolean")
    
    async def _notify_watchers(self, config_key: str, value: Any) -> None:
        """Notify configuration watchers."""
# SECURITY: # SECURITY: key = config_key.split(':', 1)[1] if ':' in config_key else config_key # MOVED TO ENV # MOVED TO ENV
# TODO: Move to environment variables or secure vault
# TODO: Move to environment variables or secure vault
        
        if key in self.watchers:
            for callback in self.watchers[key]:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(key, value)
                    else:
                        callback(key, value)
                except Exception as e:
                    self.logger.error(f"Error in configuration watcher callback: {e}")
    
    async def _evaluate_flag_conditions(self, conditions: Dict[str, Any], 
                                       context: Dict[str, Any]) -> bool:
        """Evaluate feature flag conditions."""
        # Simple condition evaluation - could be extended
        for condition_key, condition_value in conditions.items():
            if condition_key not in context:
                return False
            
            context_value = context[condition_key]
            
            if isinstance(condition_value, dict):
                # Complex condition with operators
                if 'equals' in condition_value:
                    if context_value != condition_value['equals']:
                        return False
                elif 'in' in condition_value:
                    if context_value not in condition_value['in']:
                        return False
                elif 'greater_than' in condition_value:
                    if context_value <= condition_value['greater_than']:
                        return False
            else:
                # Simple equality check
                if context_value != condition_value:
                    return False
        
        return True
    
    async def _record_flag_evaluation(self, flag_name: str, result: bool, 
                                     user_id: Optional[str], environment: str) -> None:
        """Record feature flag evaluation for analytics."""
        if flag_name not in self.feature_flag_stats:
            self.feature_flag_stats[flag_name] = {
                'total_evaluations': 0,
                'enabled_count': 0,
                'disabled_count': 0,
                'unique_users': set()
            }
        
        stats = self.feature_flag_stats[flag_name]
        stats['total_evaluations'] += 1
        
        if result:
            stats['enabled_count'] += 1
        else:
            stats['disabled_count'] += 1
        
        if user_id:
            stats['unique_users'].add(user_id)
    
    async def _secret_rotation_scheduler(self, config: SecretsManagerConfig) -> None:
        """Schedule automatic secret rotation."""
        while True:
            try:
                await asyncio.sleep(config.rotation_interval_days * 24 * 3600)
                
                # Rotate secrets
                await self._rotate_secrets(config)
                
            except Exception as e:
                self.logger.error(f"Secret rotation error: {e}")
                await asyncio.sleep(3600)  # Retry in 1 hour
    
    async def _rotate_secrets(self, config: SecretsManagerConfig) -> None:
        """Rotate secrets automatically."""
        self.logger.info(f"Rotating secrets for provider '{config.provider}'")
        
        # Implementation would depend on the secrets provider
        # For now, just log the action
        manager_data = self.secrets_managers.get(config.provider)
        if manager_data:
            manager_data['last_sync'] = datetime.utcnow()
            manager_data['sync_count'] += 1
    
    @abstractmethod
    async def setup_service_specific_configuration(self) -> None:
        """Setup service-specific configuration. Override in subclasses."""
        pass
    
    async def health_check(self) -> Dict[str, Any]:
        """Service health check."""
        base_health = await super().health_check()
        
        return {
            **base_health,
            'configuration': {
                'configurations': len(self.configurations),
                'secrets_cached': len(self.secrets),
                'feature_flags': len(self.feature_flags),
                'environments': len(self.environments),
                'config_sources': len(self.config_sources),
                'secrets_managers': len(self.secrets_managers)
            },
            'components': {
                'encryption': 'available' if self.cipher_suite else 'not_configured',
                'hot_reload': 'active',
                'validation': 'available' if self.validation_schemas else 'not_configured'
            }
        }
    
    async def cleanup(self) -> None:
        """Cleanup configuration resources."""
        # Clear sensitive data
        self.secrets.clear()
        
        if self.cipher_suite:
            self.encryption_key = None
            self.cipher_suite = None
        
        await super().cleanup()