"""
IA Influencer Agent - Configuration Management
Enterprise configuration and secrets management

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved - Unauthorized use prohibited

Features:
- Centralized configuration management
- Secrets encryption and rotation
- Environment-specific configurations
- Configuration versioning and rollback
- Integration with Kubernetes ConfigMaps and Secrets
"""

import asyncio
import logging
import json
import yaml
import base64
from typing import Dict, List, Optional, Any, Union, Set
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta
import hashlib
from cryptography.fernet import Fernet
import os

import prometheus_client
from kubernetes import client

# Note: Import paths adjusted for actual deployment structure
from .base_manager import BaseDeploymentManager

# Mock classes for standalone operation
class EncryptionManager:
    """Mock encryption manager."""
    def __init__(self):
        pass
    
    async def initialize(self):
        return True
    
    async def encrypt_data(self, data: str):
        # Mock encryption - just base64 encode for demo
        import base64
        return base64.b64encode(data.encode()).decode()
    
    async def decrypt_data(self, encrypted_data: str):
        # Mock decryption - just base64 decode for demo
        import base64
        return base64.b64decode(encrypted_data.encode()).decode()

class MetricsCollector:
    """Mock metrics collector."""
    def __init__(self):
        pass


class ConfigType(Enum):
    """Configuration types."""
    APPLICATION = "application"
    DATABASE = "database"
    API_KEYS = "api_keys"
    CERTIFICATES = "certificates"
    FEATURE_FLAGS = "feature_flags"
    MONITORING = "monitoring"
    LOGGING = "logging"
    NETWORKING = "networking"


class SecretType(Enum):
    """Secret types."""
    PASSWORD = "password"
    API_KEY = "api_key"
    TOKEN = "token"
    CERTIFICATE = "certificate"
    DATABASE_CONNECTION = "database_connection"
    OAUTH_CLIENT = "oauth_client"
    ENCRYPTION_KEY = "encryption_key"


class Environment(Enum):
    """Environment types."""
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"
    DR = "disaster_recovery"


@dataclass
class ConfigEntry:
    """Configuration entry."""
    key: str
    value: Any
    config_type: ConfigType
    environment: Environment
    namespace: str
    description: str
    created_at: datetime
    updated_at: datetime
    version: int = 1
    encrypted: bool = False


@dataclass
class SecretEntry:
    """Secret entry."""
    key: str
    value: str
    secret_type: SecretType
    environment: Environment
    namespace: str
    description: str
    created_at: datetime
    updated_at: datetime
    expires_at: Optional[datetime]
    rotation_interval_days: Optional[int]
    version: int = 1
    encrypted: bool = True


@dataclass
class ConfigTemplate:
    """Configuration template."""
    name: str
    config_type: ConfigType
    template: Dict[str, Any]
    variables: List[str]
    environments: List[Environment]
    description: str


class ConfigurationManager(BaseDeploymentManager):
    """
    Enterprise configuration and secrets management.
    
    Manages application configurations, secrets, and environment-specific
    settings with encryption, versioning, and rotation capabilities.
    """

    def __init__(
        self,
        encryption_manager: Optional[EncryptionManager] = None,
        metrics_collector: Optional[MetricsCollector] = None,
        kubernetes_client: Optional[client.CoreV1Api] = None
    ):
        super().__init__()
        self.encryption_manager = encryption_manager or EncryptionManager()
        self.metrics_collector = metrics_collector or MetricsCollector()
        self.k8s_client = kubernetes_client
        
        # Configuration storage
        self.configurations: Dict[str, Dict[str, ConfigEntry]] = {}  # environment -> key -> config
        self.secrets: Dict[str, Dict[str, SecretEntry]] = {}  # environment -> key -> secret
        self.templates: Dict[str, ConfigTemplate] = {}
        
        # Configuration history for versioning
        self.config_history: Dict[str, List[ConfigEntry]] = {}  # key -> versions
        self.secret_history: Dict[str, List[SecretEntry]] = {}  # key -> versions
        
        # Default configurations for IA Influencer Agent platform
        self.platform_configs = self._get_platform_configurations()
        
        # Metrics
        self.config_operations_metrics = prometheus_client.Counter(
            'config_operations_total',
            'Total number of configuration operations',
            ['operation', 'environment', 'type']
        )
        
        self.secret_rotations_metrics = prometheus_client.Counter(
            'secret_rotations_total',
            'Total number of secret rotations',
            ['environment', 'secret_type']
        )

    def _get_platform_configurations(self) -> Dict[str, Dict[str, Any]]:
        """Get default platform configurations."""
        return {
            "api_gateway": {
                "port": 8000,
                "max_connections": 1000,
                "request_timeout": 30,
                "cors_enabled": True,
                "cors_origins": ["*"],
                "rate_limiting": {
                    "requests_per_minute": 1000,
                    "burst_size": 100
                },
                "ssl": {
                    "enabled": True,
                    "redirect_http": True
                }
            },
            "ai_engine": {
                "model_cache_size": "2GB",
                "inference_timeout": 30,
                "batch_size": 32,
                "gpu_enabled": True,
                "model_versions": {
                    "fingerprinting": "v2.1.0",
                    "content_analysis": "v1.5.0",
                    "protection": "v1.3.0"
                },
                "performance": {
                    "max_concurrent_requests": 50,
                    "queue_size": 200
                }
            },
            "database": {
                "postgresql": {
                    "host": "postgres-service",
                    "port": 5432,
                    "database": "ia_influencer_agent",
                    "pool_size": 20,
                    "max_overflow": 30,
                    "connection_timeout": 10,
                    "ssl_mode": "require"
                },
                "redis": {
                    "host": "redis-service",
                    "port": 6379,
                    "database": 0,
                    "pool_size": 10,
                    "connection_timeout": 5,
                    "ssl_enabled": True
                },
                "elasticsearch": {
                    "hosts": ["elasticsearch-service:9200"],
                    "timeout": 30,
                    "max_retries": 3,
                    "ssl_enabled": True,
                    "verify_certs": True
                }
            },
            "monitoring": {
                "prometheus": {
                    "scrape_interval": 15,
                    "evaluation_interval": 15,
                    "retention": "30d"
                },
                "grafana": {
                    "theme": "dark",
                    "timezone": "UTC",
                    "refresh_intervals": ["5s", "10s", "30s", "1m", "5m"]
                },
                "alerting": {
                    "enabled": True,
                    "webhook_url": "",
                    "slack_channel": "#alerts",
                    "email_recipients": []
                }
            },
            "logging": {
                "level": "INFO",
                "format": "json",
                "rotation": {
                    "max_size": "100MB",
                    "max_files": 10,
                    "compression": True
                },
                "destinations": ["stdout", "file", "elasticsearch"]
            }
        }

    async def initialize(self) -> bool:
        """
        Initialize configuration manager.
        
        Returns:
            True if initialization successful, False otherwise
        """
        try:
            # Initialize encryption manager
            encryption_init = await self.encryption_manager.initialize()
            if not encryption_init:
                return False
            
            # Initialize Kubernetes client if not provided
            if not self.k8s_client:
                from kubernetes import config
                try:
                    config.load_incluster_config()
                except:
                    config.load_kube_config()
                self.k8s_client = client.CoreV1Api()
            
            # Initialize default configurations
            await self._initialize_platform_configurations()
            
            self.logger.info("Configuration manager initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize configuration manager: {e}")
            return False

    async def _initialize_platform_configurations(self) -> None:
        """Initialize platform configurations for all environments."""
        try:
            for env in Environment:
                # Initialize configuration storage for environment
                if env.value not in self.configurations:
                    self.configurations[env.value] = {}
                if env.value not in self.secrets:
                    self.secrets[env.value] = {}
                
                # Set platform configurations
                for service_name, config_data in self.platform_configs.items():
                    config_key = f"platform.{service_name}"
                    
                    # Adjust configuration based on environment
                    env_config = self._adjust_config_for_environment(config_data, env)
                    
                    config_entry = ConfigEntry(
                        key=config_key,
                        value=env_config,
                        config_type=ConfigType.APPLICATION,
                        environment=env,
                        namespace="ia-influencer-agent",
                        description=f"Platform configuration for {service_name}",
                        created_at=datetime.now(),
                        updated_at=datetime.now(),
                        version=1,
                        encrypted=False
                    )
                    
                    self.configurations[env.value][config_key] = config_entry
            
        except Exception as e:
            self.logger.error(f"Failed to initialize platform configurations: {e}")

    def _adjust_config_for_environment(self, config: Dict[str, Any], env: Environment) -> Dict[str, Any]:
        """Adjust configuration values based on environment."""
        env_config = config.copy()
        
        # Environment-specific adjustments
        if env == Environment.DEVELOPMENT:
            # Development settings
            if "ssl" in env_config:
                env_config["ssl"]["enabled"] = False
            if "rate_limiting" in env_config:
                env_config["rate_limiting"]["requests_per_minute"] = 10000
        
        elif env == Environment.PRODUCTION:
            # Production settings
            if "ssl" in env_config:
                env_config["ssl"]["enabled"] = True
            if "performance" in env_config:
                env_config["performance"]["max_concurrent_requests"] *= 2
        
        elif env == Environment.TESTING:
            # Testing settings
            if "database" in env_config:
                env_config["database"] = f"{config.get('database', 'test')}_test"
            if "rate_limiting" in env_config:
                env_config["rate_limiting"]["requests_per_minute"] = 5000
        
        return env_config

    async def set_configuration(
        self,
        key: str,
        value: Any,
        config_type: ConfigType,
        environment: Environment,
        namespace: str = "ia-influencer-agent",
        description: str = "",
        encrypt: bool = False
    ) -> bool:
        """
        Set configuration value.
        
        Args:
            key: Configuration key
            value: Configuration value
            config_type: Configuration type
            environment: Target environment
            namespace: Kubernetes namespace
            description: Configuration description
            encrypt: Whether to encrypt the value
            
        Returns:
            True if configuration set successfully, False otherwise
        """
        try:
            # Encrypt value if requested
            final_value = value
            if encrypt:
                if isinstance(value, dict):
                    final_value = await self.encryption_manager.encrypt_data(json.dumps(value))
                else:
                    final_value = await self.encryption_manager.encrypt_data(str(value))
            
            # Create configuration entry
            config_entry = ConfigEntry(
                key=key,
                value=final_value,
                config_type=config_type,
                environment=environment,
                namespace=namespace,
                description=description,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                version=1,
                encrypted=encrypt
            )
            
            # Check if configuration already exists
            env_key = environment.value
            if env_key in self.configurations and key in self.configurations[env_key]:
                existing_config = self.configurations[env_key][key]
                config_entry.version = existing_config.version + 1
                config_entry.created_at = existing_config.created_at
                
                # Store previous version in history
                if key not in self.config_history:
                    self.config_history[key] = []
                self.config_history[key].append(existing_config)
            
            # Store configuration
            if env_key not in self.configurations:
                self.configurations[env_key] = {}
            
            self.configurations[env_key][key] = config_entry
            
            # Create or update Kubernetes ConfigMap
            await self._sync_config_to_kubernetes(config_entry)
            
            # Update metrics
            self.config_operations_metrics.labels(
                operation='set',
                environment=environment.value,
                type=config_type.value
            ).inc()
            
            self.logger.info(f"Configuration '{key}' set for environment '{environment.value}'")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to set configuration '{key}': {e}")
            return False

    async def get_configuration(
        self,
        key: str,
        environment: Environment,
        decrypt: bool = True
    ) -> Optional[Any]:
        """
        Get configuration value.
        
        Args:
            key: Configuration key
            environment: Target environment
            decrypt: Whether to decrypt encrypted values
            
        Returns:
            Configuration value or None if not found
        """
        try:
            env_key = environment.value
            
            if env_key not in self.configurations or key not in self.configurations[env_key]:
                return None
            
            config_entry = self.configurations[env_key][key]
            value = config_entry.value
            
            # Decrypt if needed
            if config_entry.encrypted and decrypt:
                decrypted_data = await self.encryption_manager.decrypt_data(value)
                
                # Try to parse as JSON if it looks like structured data
                try:
                    value = json.loads(decrypted_data)
                except json.JSONDecodeError:
                    value = decrypted_data
            
            # Update metrics
            self.config_operations_metrics.labels(
                operation='get',
                environment=environment.value,
                type=config_entry.config_type.value
            ).inc()
            
            return value
            
        except Exception as e:
            self.logger.error(f"Failed to get configuration '{key}': {e}")
            return None

    async def set_secret(
        self,
        key: str,
        value: str,
        secret_type: SecretType,
        environment: Environment,
        namespace: str = "ia-influencer-agent",
        description: str = "",
        expires_at: Optional[datetime] = None,
        rotation_interval_days: Optional[int] = None
    ) -> bool:
        """
        Set secret value.
        
        Args:
            key: Secret key
            value: Secret value
            secret_type: Secret type
            environment: Target environment
            namespace: Kubernetes namespace
            description: Secret description
            expires_at: Optional expiration date
            rotation_interval_days: Optional automatic rotation interval
            
        Returns:
            True if secret set successfully, False otherwise
        """
        try:
            # Encrypt secret value
            encrypted_value = await self.encryption_manager.encrypt_data(value)
            
            # Create secret entry
            secret_entry = SecretEntry(
                key=key,
                value=encrypted_value,
                secret_type=secret_type,
                environment=environment,
                namespace=namespace,
                description=description,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                expires_at=expires_at,
                rotation_interval_days=rotation_interval_days,
                version=1,
                encrypted=True
            )
            
            # Check if secret already exists
            env_key = environment.value
            if env_key in self.secrets and key in self.secrets[env_key]:
                existing_secret = self.secrets[env_key][key]
                secret_entry.version = existing_secret.version + 1
                secret_entry.created_at = existing_secret.created_at
                
                # Store previous version in history
                if key not in self.secret_history:
                    self.secret_history[key] = []
                self.secret_history[key].append(existing_secret)
            
            # Store secret
            if env_key not in self.secrets:
                self.secrets[env_key] = {}
            
            self.secrets[env_key][key] = secret_entry
            
            # Create or update Kubernetes Secret
            await self._sync_secret_to_kubernetes(secret_entry)
            
            # Update metrics
            self.config_operations_metrics.labels(
                operation='set',
                environment=environment.value,
                type='secret'
            ).inc()
            
            self.logger.info(f"Secret '{key}' set for environment '{environment.value}'")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to set secret '{key}': {e}")
            return False

    async def get_secret(
        self,
        key: str,
        environment: Environment,
        decrypt: bool = True
    ) -> Optional[str]:
        """
        Get secret value.
        
        Args:
            key: Secret key
            environment: Target environment
            decrypt: Whether to decrypt the value
            
        Returns:
            Secret value or None if not found
        """
        try:
            env_key = environment.value
            
            if env_key not in self.secrets or key not in self.secrets[env_key]:
                return None
            
            secret_entry = self.secrets[env_key][key]
            
            # Check if secret has expired
            if secret_entry.expires_at and secret_entry.expires_at < datetime.now():
                self.logger.warning(f"Secret '{key}' has expired")
                return None
            
            value = secret_entry.value
            
            # Decrypt if needed
            if decrypt:
                value = await self.encryption_manager.decrypt_data(value)
            
            # Update metrics
            self.config_operations_metrics.labels(
                operation='get',
                environment=environment.value,
                type='secret'
            ).inc()
            
            return value
            
        except Exception as e:
            self.logger.error(f"Failed to get secret '{key}': {e}")
            return None

    async def delete_configuration(self, key: str, environment: Environment) -> bool:
        """
        Delete configuration.
        
        Args:
            key: Configuration key
            environment: Target environment
            
        Returns:
            True if deletion successful, False otherwise
        """
        try:
            env_key = environment.value
            
            if env_key not in self.configurations or key not in self.configurations[env_key]:
                self.logger.warning(f"Configuration '{key}' not found in environment '{environment.value}'")
                return False
            
            config_entry = self.configurations[env_key][key]
            
            # Move to history before deletion
            if key not in self.config_history:
                self.config_history[key] = []
            self.config_history[key].append(config_entry)
            
            # Delete from storage
            del self.configurations[env_key][key]
            
            # Delete Kubernetes ConfigMap
            await self._delete_config_from_kubernetes(key, config_entry.namespace)
            
            # Update metrics
            self.config_operations_metrics.labels(
                operation='delete',
                environment=environment.value,
                type=config_entry.config_type.value
            ).inc()
            
            self.logger.info(f"Configuration '{key}' deleted from environment '{environment.value}'")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to delete configuration '{key}': {e}")
            return False

    async def delete_secret(self, key: str, environment: Environment) -> bool:
        """
        Delete secret.
        
        Args:
            key: Secret key
            environment: Target environment
            
        Returns:
            True if deletion successful, False otherwise
        """
        try:
            env_key = environment.value
            
            if env_key not in self.secrets or key not in self.secrets[env_key]:
                self.logger.warning(f"Secret '{key}' not found in environment '{environment.value}'")
                return False
            
            secret_entry = self.secrets[env_key][key]
            
            # Move to history before deletion
            if key not in self.secret_history:
                self.secret_history[key] = []
            self.secret_history[key].append(secret_entry)
            
            # Delete from storage
            del self.secrets[env_key][key]
            
            # Delete Kubernetes Secret
            await self._delete_secret_from_kubernetes(key, secret_entry.namespace)
            
            # Update metrics
            self.config_operations_metrics.labels(
                operation='delete',
                environment=environment.value,
                type='secret'
            ).inc()
            
            self.logger.info(f"Secret '{key}' deleted from environment '{environment.value}'")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to delete secret '{key}': {e}")
            return False

    async def rotate_secret(self, key: str, environment: Environment, new_value: str) -> bool:
        """
        Rotate secret value.
        
        Args:
            key: Secret key
            environment: Target environment
            new_value: New secret value
            
        Returns:
            True if rotation successful, False otherwise
        """
        try:
            env_key = environment.value
            
            if env_key not in self.secrets or key not in self.secrets[env_key]:
                self.logger.error(f"Secret '{key}' not found in environment '{environment.value}'")
                return False
            
            secret_entry = self.secrets[env_key][key]
            
            # Update secret with new value
            rotation_success = await self.set_secret(
                key=key,
                value=new_value,
                secret_type=secret_entry.secret_type,
                environment=environment,
                namespace=secret_entry.namespace,
                description=secret_entry.description,
                expires_at=secret_entry.expires_at,
                rotation_interval_days=secret_entry.rotation_interval_days
            )
            
            if rotation_success:
                # Update metrics
                self.secret_rotations_metrics.labels(
                    environment=environment.value,
                    secret_type=secret_entry.secret_type.value
                ).inc()
                
                self.logger.info(f"Secret '{key}' rotated successfully in environment '{environment.value}'")
                return True
            else:
                return False
            
        except Exception as e:
            self.logger.error(f"Failed to rotate secret '{key}': {e}")
            return False

    async def auto_rotate_secrets(self) -> int:
        """
        Automatically rotate secrets that are due for rotation.
        
        Returns:
            Number of secrets rotated
        """
        try:
            rotated_count = 0
            current_time = datetime.now()
            
            for env_key, secrets in self.secrets.items():
                for secret_key, secret_entry in secrets.items():
                    # Check if secret needs rotation
                    if secret_entry.rotation_interval_days:
                        days_since_update = (current_time - secret_entry.updated_at).days
                        
                        if days_since_update >= secret_entry.rotation_interval_days:
                            # Generate new secret value based on type
                            new_value = await self._generate_new_secret_value(secret_entry.secret_type)
                            
                            if new_value:
                                rotation_success = await self.rotate_secret(
                                    secret_key,
                                    Environment(env_key),
                                    new_value
                                )
                                
                                if rotation_success:
                                    rotated_count += 1
                                    self.logger.info(f"Auto-rotated secret '{secret_key}' in environment '{env_key}'")
            
            return rotated_count
            
        except Exception as e:
            self.logger.error(f"Failed to auto-rotate secrets: {e}")
            return 0

    async def _generate_new_secret_value(self, secret_type: SecretType) -> Optional[str]:
        """Generate new secret value based on type."""
        try:
            if secret_type in [SecretType.PASSWORD, SecretType.API_KEY, SecretType.TOKEN]:
                # Generate random string
                import secrets
                import string
                alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
                return ''.join(secrets.choice(alphabet) for _ in range(32))
            
            elif secret_type == SecretType.ENCRYPTION_KEY:
                # Generate new Fernet key
                return Fernet.generate_key().decode()
            
            else:
                # For other types, manual rotation is required
                return None
                
        except Exception as e:
            self.logger.error(f"Failed to generate new secret value for type '{secret_type.value}': {e}")
            return None

    async def _sync_config_to_kubernetes(self, config_entry: ConfigEntry) -> bool:
        """Sync configuration to Kubernetes ConfigMap."""
        try:
            if not self.k8s_client:
                return True  # Skip if Kubernetes client not available
            
            configmap_name = f"config-{config_entry.key.replace('.', '-').replace('_', '-')}"
            
            # Prepare data
            config_data = {
                config_entry.key: json.dumps(config_entry.value) if isinstance(config_entry.value, dict) else str(config_entry.value)
            }
            
            # Create ConfigMap metadata
            metadata = client.V1ObjectMeta(
                name=configmap_name,
                namespace=config_entry.namespace,
                labels={
                    "managed-by": "ia-influencer-agent",
                    "config-type": config_entry.config_type.value,
                    "environment": config_entry.environment.value
                },
                annotations={
                    "description": config_entry.description,
                    "version": str(config_entry.version),
                    "created-at": config_entry.created_at.isoformat(),
                    "updated-at": config_entry.updated_at.isoformat()
                }
            )
            
            # Create ConfigMap
            configmap = client.V1ConfigMap(
                api_version="v1",
                kind="ConfigMap",
                metadata=metadata,
                data=config_data
            )
            
            try:
                # Try to create new ConfigMap
                self.k8s_client.create_namespaced_config_map(
                    namespace=config_entry.namespace,
                    body=configmap
                )
            except client.ApiException as e:
                if e.status == 409:  # ConfigMap already exists
                    # Update existing ConfigMap
                    self.k8s_client.patch_namespaced_config_map(
                        name=configmap_name,
                        namespace=config_entry.namespace,
                        body=configmap
                    )
                else:
                    raise
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to sync configuration to Kubernetes: {e}")
            return False

    async def _sync_secret_to_kubernetes(self, secret_entry: SecretEntry) -> bool:
        """Sync secret to Kubernetes Secret."""
        try:
            if not self.k8s_client:
                return True  # Skip if Kubernetes client not available
            
            secret_name = f"secret-{secret_entry.key.replace('.', '-').replace('_', '-')}"
            
            # Prepare data (Kubernetes secrets need base64 encoding)
            secret_data = {
                secret_entry.key: base64.b64encode(secret_entry.value.encode()).decode()
            }
            
            # Create Secret metadata
            metadata = client.V1ObjectMeta(
                name=secret_name,
                namespace=secret_entry.namespace,
                labels={
                    "managed-by": "ia-influencer-agent",
                    "secret-type": secret_entry.secret_type.value,
                    "environment": secret_entry.environment.value
                },
                annotations={
                    "description": secret_entry.description,
                    "version": str(secret_entry.version),
                    "created-at": secret_entry.created_at.isoformat(),
                    "updated-at": secret_entry.updated_at.isoformat(),
                    "expires-at": secret_entry.expires_at.isoformat() if secret_entry.expires_at else "",
                    "rotation-interval-days": str(secret_entry.rotation_interval_days) if secret_entry.rotation_interval_days else ""
                }
            )
            
            # Create Secret
            secret = client.V1Secret(
                api_version="v1",
                kind="Secret",
                metadata=metadata,
                type="Opaque",
                data=secret_data
            )
            
            try:
                # Try to create new Secret
                self.k8s_client.create_namespaced_secret(
                    namespace=secret_entry.namespace,
                    body=secret
                )
            except client.ApiException as e:
                if e.status == 409:  # Secret already exists
                    # Update existing Secret
                    self.k8s_client.patch_namespaced_secret(
                        name=secret_name,
                        namespace=secret_entry.namespace,
                        body=secret
                    )
                else:
                    raise
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to sync secret to Kubernetes: {e}")
            return False

    async def _delete_config_from_kubernetes(self, key: str, namespace: str) -> bool:
        """Delete configuration from Kubernetes ConfigMap."""
        try:
            if not self.k8s_client:
                return True  # Skip if Kubernetes client not available
            
            configmap_name = f"config-{key.replace('.', '-').replace('_', '-')}"
            
            try:
                self.k8s_client.delete_namespaced_config_map(
                    name=configmap_name,
                    namespace=namespace
                )
                return True
            except client.ApiException as e:
                if e.status == 404:  # ConfigMap not found
                    return True
                else:
                    raise
            
        except Exception as e:
            self.logger.error(f"Failed to delete configuration from Kubernetes: {e}")
            return False

    async def _delete_secret_from_kubernetes(self, key: str, namespace: str) -> bool:
        """Delete secret from Kubernetes Secret."""
        try:
            if not self.k8s_client:
                return True  # Skip if Kubernetes client not available
            
            secret_name = f"secret-{key.replace('.', '-').replace('_', '-')}"
            
            try:
                self.k8s_client.delete_namespaced_secret(
                    name=secret_name,
                    namespace=namespace
                )
                return True
            except client.ApiException as e:
                if e.status == 404:  # Secret not found
                    return True
                else:
                    raise
            
        except Exception as e:
            self.logger.error(f"Failed to delete secret from Kubernetes: {e}")
            return False

    async def list_configurations(
        self,
        environment: Optional[Environment] = None,
        config_type: Optional[ConfigType] = None,
        namespace: Optional[str] = None
    ) -> List[ConfigEntry]:
        """
        List configurations.
        
        Args:
            environment: Optional environment filter
            config_type: Optional configuration type filter
            namespace: Optional namespace filter
            
        Returns:
            List of configuration entries
        """
        results = []
        
        for env_key, configs in self.configurations.items():
            if environment and env_key != environment.value:
                continue
            
            for config_entry in configs.values():
                if config_type and config_entry.config_type != config_type:
                    continue
                
                if namespace and config_entry.namespace != namespace:
                    continue
                
                results.append(config_entry)
        
        return sorted(results, key=lambda c: (c.environment.value, c.key))

    async def list_secrets(
        self,
        environment: Optional[Environment] = None,
        secret_type: Optional[SecretType] = None,
        namespace: Optional[str] = None,
        include_values: bool = False
    ) -> List[Dict[str, Any]]:
        """
        List secrets (without values by default for security).
        
        Args:
            environment: Optional environment filter
            secret_type: Optional secret type filter
            namespace: Optional namespace filter
            include_values: Whether to include secret values (dangerous!)
            
        Returns:
            List of secret information
        """
        results = []
        
        for env_key, secrets in self.secrets.items():
            if environment and env_key != environment.value:
                continue
            
            for secret_entry in secrets.values():
                if secret_type and secret_entry.secret_type != secret_type:
                    continue
                
                if namespace and secret_entry.namespace != namespace:
                    continue
                
                secret_info = {
                    "key": secret_entry.key,
                    "secret_type": secret_entry.secret_type.value,
                    "environment": secret_entry.environment.value,
                    "namespace": secret_entry.namespace,
                    "description": secret_entry.description,
                    "created_at": secret_entry.created_at.isoformat(),
                    "updated_at": secret_entry.updated_at.isoformat(),
                    "expires_at": secret_entry.expires_at.isoformat() if secret_entry.expires_at else None,
                    "rotation_interval_days": secret_entry.rotation_interval_days,
                    "version": secret_entry.version
                }
                
                if include_values:
                    secret_info["value"] = await self.get_secret(
                        secret_entry.key,
                        secret_entry.environment,
                        decrypt=True
                    )
                
                results.append(secret_info)
        
        return sorted(results, key=lambda s: (s["environment"], s["key"]))

    async def export_configuration(
        self,
        environment: Environment,
        output_format: str = "json",
        include_secrets: bool = False
    ) -> Optional[str]:
        """
        Export configuration for environment.
        
        Args:
            environment: Target environment
            output_format: Output format ('json' or 'yaml')
            include_secrets: Whether to include secrets
            
        Returns:
            Exported configuration string or None if failed
        """
        try:
            export_data = {
                "environment": environment.value,
                "exported_at": datetime.now().isoformat(),
                "configurations": {},
                "secrets": {} if include_secrets else "excluded_for_security"
            }
            
            # Export configurations
            env_key = environment.value
            if env_key in self.configurations:
                for key, config_entry in self.configurations[env_key].items():
                    export_data["configurations"][key] = {
                        "value": config_entry.value,
                        "type": config_entry.config_type.value,
                        "namespace": config_entry.namespace,
                        "description": config_entry.description,
                        "version": config_entry.version,
                        "encrypted": config_entry.encrypted
                    }
            
            # Export secrets if requested
            if include_secrets and env_key in self.secrets:
                for key, secret_entry in self.secrets[env_key].items():
                    secret_value = await self.get_secret(key, environment, decrypt=True)
                    export_data["secrets"][key] = {
                        "value": secret_value,
                        "type": secret_entry.secret_type.value,
                        "namespace": secret_entry.namespace,
                        "description": secret_entry.description,
                        "version": secret_entry.version,
                        "expires_at": secret_entry.expires_at.isoformat() if secret_entry.expires_at else None,
                        "rotation_interval_days": secret_entry.rotation_interval_days
                    }
            
            # Format output
            if output_format.lower() == "yaml":
                return yaml.dump(export_data, default_flow_style=False)
            else:
                return json.dumps(export_data, indent=2)
            
        except Exception as e:
            self.logger.error(f"Failed to export configuration: {e}")
            return None

    async def import_configuration(
        self,
        data: str,
        environment: Environment,
        input_format: str = "json",
        overwrite: bool = False
    ) -> bool:
        """
        Import configuration for environment.
        
        Args:
            data: Configuration data string
            environment: Target environment
            input_format: Input format ('json' or 'yaml')
            overwrite: Whether to overwrite existing configurations
            
        Returns:
            True if import successful, False otherwise
        """
        try:
            # Parse input data
            if input_format.lower() == "yaml":
                import_data = yaml.safe_load(data)
            else:
                import_data = json.loads(data)
            
            # Import configurations
            if "configurations" in import_data:
                for key, config_data in import_data["configurations"].items():
                    # Check if configuration exists and overwrite is not allowed
                    if not overwrite:
                        existing_config = await self.get_configuration(key, environment)
                        if existing_config is not None:
                            self.logger.warning(f"Configuration '{key}' already exists, skipping")
                            continue
                    
                    # Set configuration
                    await self.set_configuration(
                        key=key,
                        value=config_data["value"],
                        config_type=ConfigType(config_data["type"]),
                        environment=environment,
                        namespace=config_data.get("namespace", "ia-influencer-agent"),
                        description=config_data.get("description", ""),
                        encrypt=config_data.get("encrypted", False)
                    )
            
            # Import secrets
            if "secrets" in import_data and isinstance(import_data["secrets"], dict):
                for key, secret_data in import_data["secrets"].items():
                    # Check if secret exists and overwrite is not allowed
                    if not overwrite:
                        existing_secret = await self.get_secret(key, environment)
                        if existing_secret is not None:
                            self.logger.warning(f"Secret '{key}' already exists, skipping")
                            continue
                    
                    # Parse expiration date
                    expires_at = None
                    if secret_data.get("expires_at"):
                        expires_at = datetime.fromisoformat(secret_data["expires_at"])
                    
                    # Set secret
                    await self.set_secret(
                        key=key,
                        value=secret_data["value"],
                        secret_type=SecretType(secret_data["type"]),
                        environment=environment,
                        namespace=secret_data.get("namespace", "ia-influencer-agent"),
                        description=secret_data.get("description", ""),
                        expires_at=expires_at,
                        rotation_interval_days=secret_data.get("rotation_interval_days")
                    )
            
            self.logger.info(f"Configuration imported successfully for environment '{environment.value}'")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to import configuration: {e}")
            return False

    async def cleanup(self) -> bool:
        """
        Cleanup configuration manager.
        
        Returns:
            True if cleanup successful, False otherwise
        """
        try:
            # Clear all configurations and secrets
            self.configurations.clear()
            self.secrets.clear()
            self.templates.clear()
            self.config_history.clear()
            self.secret_history.clear()
            
            self.logger.info("Configuration manager cleaned up successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to cleanup configuration manager: {e}")
            return False
