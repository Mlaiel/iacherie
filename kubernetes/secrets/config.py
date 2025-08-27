"""
IA Influencer Agent - Secrets Configuration Management
Enterprise configuration for secrets deployment and management

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved - Unauthorized use prohibited
"""

import os
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from pathlib import Path
import yaml
import json
from enum import Enum


class Environment(Enum):
    """Deployment environments."""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"


class SecretProvider(Enum):
    """Secret provider types."""
    HASHICORP_VAULT = "hashicorp_vault"
    KUBERNETES_SECRETS = "kubernetes_secrets"
    AWS_SECRETS_MANAGER = "aws_secrets_manager"
    AZURE_KEY_VAULT = "azure_key_vault"
    GCP_SECRET_MANAGER = "gcp_secret_manager"


class EncryptionAlgorithm(Enum):
    """Encryption algorithms."""
    AES_256_GCM = "aes_256_gcm"
    FERNET = "fernet"
    RSA_OAEP = "rsa_oaep"
    CHACHA20_POLY1305 = "chacha20_poly1305"


@dataclass
class VaultConfig:
    """HashiCorp Vault configuration."""
    url: str = "https://vault.ia-influencer.com"
    token: Optional[str] = None
    auth_method: str = "kubernetes"
    namespace: Optional[str] = "ia-influencer"
    role: str = "ia-influencer-secrets"
    kv_version: int = 2
    mount_path: str = "secret"
    ca_cert_path: Optional[str] = None
    client_cert_path: Optional[str] = None
    client_key_path: Optional[str] = None
    verify_ssl: bool = True
    timeout: int = 30
    max_retries: int = 3
    retry_delay: float = 1.0


@dataclass
class KubernetesConfig:
    """Kubernetes secrets configuration."""
    namespace: str = "ia-influencer"
    service_account: str = "secrets-manager"
    token_path: str = "/var/run/secrets/kubernetes.io/serviceaccount/token"
    ca_cert_path: str = "/var/run/secrets/kubernetes.io/serviceaccount/ca.crt"
    in_cluster: bool = True
    kubeconfig_path: Optional[str] = None


@dataclass
class AWSConfig:
    """AWS Secrets Manager configuration."""
    region: str = "eu-central-1"
    access_key_id: Optional[str] = None
    secret_access_key: Optional[str] = None
    session_token: Optional[str] = None
    role_arn: Optional[str] = None
    profile_name: Optional[str] = None
    endpoint_url: Optional[str] = None


@dataclass
class AzureConfig:
    """Azure Key Vault configuration."""
    vault_url: str = "https://ia-influencer-kv.vault.azure.net/"
    tenant_id: Optional[str] = None
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    certificate_path: Optional[str] = None
    authority: str = "https://login.microsoftonline.com"


@dataclass
class GCPConfig:
    """Google Cloud Secret Manager configuration."""
    project_id: str = "ia-influencer-platform"
    credentials_path: Optional[str] = None
    location: str = "global"
    endpoint: str = "secretmanager.googleapis.com"


@dataclass
class EncryptionConfig:
    """Encryption configuration."""
    algorithm: EncryptionAlgorithm = EncryptionAlgorithm.AES_256_GCM
    key_size: int = 256
    key_derivation_iterations: int = 100000
    master_key_path: Optional[str] = None
    key_rotation_interval: str = "90d"
    backup_encryption: bool = True


@dataclass
class RotationConfig:
    """Secret rotation configuration."""
    enabled: bool = True
    default_interval: str = "30d"
    max_retries: int = 3
    retry_delay: int = 300
    rollback_timeout: int = 600
    notification_webhooks: List[str] = field(default_factory=list)
    jobs_file: str = "/var/lib/secrets/rotation_jobs.json"
    history_retention: int = 90


@dataclass
class ComplianceConfig:
    """Compliance and audit configuration."""
    audit_enabled: bool = True
    audit_file: str = "/var/log/secrets/audit.log"
    audit_webhook_url: Optional[str] = None
    pci_compliance: bool = True
    sox_compliance: bool = True
    gdpr_compliance: bool = True
    retention_days: int = 2555  # 7 years
    anonymize_after_days: int = 1095  # 3 years


@dataclass
class MonitoringConfig:
    """Monitoring and alerting configuration."""
    metrics_enabled: bool = True
    prometheus_port: int = 9090
    health_check_interval: int = 60
    alert_thresholds: Dict[str, Any] = field(default_factory=lambda: {
        "secret_access_rate": 100,
        "failed_authentications": 5,
        "rotation_failure_rate": 0.1,
        "vault_seal_status": True
    })
    notification_channels: List[str] = field(default_factory=list)


@dataclass
class BackupConfig:
    """Backup and recovery configuration."""
    enabled: bool = True
    schedule: str = "0 2 * * *"  # Daily at 2 AM
    retention_days: int = 30
    encryption_enabled: bool = True
    compression_enabled: bool = True
    storage_path: str = "/var/backups/secrets"
    remote_storage: Dict[str, Any] = field(default_factory=dict)
    verification_enabled: bool = True


class SecretsConfig:
    """
    Comprehensive secrets configuration management for IA Influencer Agent.
    
    Handles configuration for all secret providers, encryption, rotation,
    compliance, monitoring, and backup systems.
    """
    
    def __init__(
        self,
        config_file: Optional[str] = None,
        environment: Union[str, Environment] = Environment.PRODUCTION
    ):
        """
        Initialize secrets configuration.
        
        Args:
            config_file: Path to configuration file
            environment: Deployment environment
        """
        self.environment = Environment(environment) if isinstance(environment, str) else environment
        self.config_file = config_file or self._get_default_config_file()
        
        # Initialize default configurations
        self._init_default_configs()
        
        # Load configuration from file
        self._load_config()
        
        # Override with environment variables
        self._load_env_variables()
        
        # Validate configuration
        self._validate_config()
        
        logger = logging.getLogger(__name__)
        logger.info(f"SecretsConfig initialized for {self.environment.value}")
    
    def _init_default_configs(self) -> None:
        """Initialize default configuration objects."""
        # Core settings
        self.service_account = "ia-influencer-secrets"
        self.log_level = "INFO"
        self.debug_mode = self.environment == Environment.DEVELOPMENT
        
        # Provider configurations
        self.vault = VaultConfig()
        self.kubernetes = KubernetesConfig()
        self.aws = AWSConfig()
        self.azure = AzureConfig()
        self.gcp = GCPConfig()
        
        # Feature configurations
        self.encryption = EncryptionConfig()
        self.rotation = RotationConfig()
        self.compliance = ComplianceConfig()
        self.monitoring = MonitoringConfig()
        self.backup = BackupConfig()
        
        # Provider selection
        self.primary_provider = SecretProvider.HASHICORP_VAULT
        self.fallback_providers = [SecretProvider.KUBERNETES_SECRETS]
        
        # Security settings
        self.require_tls = True
        self.certificate_validation = True
        self.access_logging = True
        self.rate_limiting = True
        self.ip_whitelist: List[str] = []
        
        # Performance settings
        self.connection_pool_size = 10
        self.request_timeout = 30
        self.cache_ttl = 300
        self.max_concurrent_operations = 50
        
        # File paths for encryption keys
        self.master_key_path = "/var/lib/secrets/master.key"
        self.encryption_keys_file = "/var/lib/secrets/encryption_keys.enc"
        
        # Audit and compliance paths
        self.audit_log_file = "/var/log/secrets/audit.log"
        self.audit_export_dir = "/var/exports/secrets"
        self.audit_retention_days = 2555  # 7 years
        self.compliance_reports_dir = "/var/reports/compliance"
        
        # Certificate management
        self.certificates_file = "/var/lib/secrets/certificates.json"
        self.certificate_monitor_interval = 3600  # 1 hour
    
    def _get_default_config_file(self) -> str:
        """Get default configuration file path."""
        base_paths = [
            "/etc/ia-influencer/secrets.yml",
            "/opt/ia-influencer/config/secrets.yml",
            os.path.expanduser("~/.ia-influencer/secrets.yml"),
            "./config/secrets.yml"
        ]
        
        for path in base_paths:
            if os.path.exists(path):
                return path
        
        return base_paths[0]  # Return first path as default
    
    def _load_config(self) -> None:
        """Load configuration from file."""
        try:
            if not os.path.exists(self.config_file):
                self._create_default_config_file()
                return
            
            with open(self.config_file, 'r') as f:
                if self.config_file.endswith('.json'):
                    config_data = json.load(f)
                else:
                    config_data = yaml.safe_load(f)
            
            # Apply environment-specific configuration
            env_config = config_data.get(self.environment.value, {})
            global_config = config_data.get('global', {})
            
            # Merge configurations (environment overrides global)
            merged_config = {**global_config, **env_config}
            
            # Update configuration objects
            self._update_from_dict(merged_config)
            
        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.warning(f"Failed to load config file {self.config_file}: {e}")
    
    def _create_default_config_file(self) -> None:
        """Create default configuration file."""
        try:
            config_data = {
                'global': {
                    'service_account': self.service_account,
                    'log_level': self.log_level,
                    'primary_provider': self.primary_provider.value,
                    'fallback_providers': [p.value for p in self.fallback_providers]
                },
                'development': {
                    'vault': {
                        'url': 'http://localhost:8200',
                        'token': 'dev-token',
                        'verify_ssl': False
                    },
                    'debug_mode': True
                },
                'staging': {
                    'vault': {
                        'url': 'https://vault-staging.ia-influencer.com',
                        'namespace': 'ia-influencer-staging'
                    }
                },
                'production': {
                    'vault': {
                        'url': 'https://vault.ia-influencer.com',
                        'namespace': 'ia-influencer-prod'
                    },
                    'compliance': {
                        'audit_enabled': True,
                        'pci_compliance': True,
                        'sox_compliance': True
                    }
                }
            }
            
            # Ensure directory exists
            config_dir = os.path.dirname(self.config_file)
            os.makedirs(config_dir, exist_ok=True)
            
            with open(self.config_file, 'w') as f:
                yaml.dump(config_data, f, default_flow_style=False, indent=2)
            
            logger = logging.getLogger(__name__)
            logger.info(f"Created default config file: {self.config_file}")
            
        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to create default config file: {e}")
    
    def _update_from_dict(self, config_dict: Dict[str, Any]) -> None:
        """Update configuration from dictionary."""
        # Update basic settings
        if 'service_account' in config_dict:
            self.service_account = config_dict['service_account']
        if 'log_level' in config_dict:
            self.log_level = config_dict['log_level']
        if 'debug_mode' in config_dict:
            self.debug_mode = config_dict['debug_mode']
        
        # Update provider selection
        if 'primary_provider' in config_dict:
            self.primary_provider = SecretProvider(config_dict['primary_provider'])
        if 'fallback_providers' in config_dict:
            self.fallback_providers = [SecretProvider(p) for p in config_dict['fallback_providers']]
        
        # Update provider configurations
        if 'vault' in config_dict:
            self._update_dataclass(self.vault, config_dict['vault'])
        if 'kubernetes' in config_dict:
            self._update_dataclass(self.kubernetes, config_dict['kubernetes'])
        if 'aws' in config_dict:
            self._update_dataclass(self.aws, config_dict['aws'])
        if 'azure' in config_dict:
            self._update_dataclass(self.azure, config_dict['azure'])
        if 'gcp' in config_dict:
            self._update_dataclass(self.gcp, config_dict['gcp'])
        
        # Update feature configurations
        if 'encryption' in config_dict:
            self._update_dataclass(self.encryption, config_dict['encryption'])
        if 'rotation' in config_dict:
            self._update_dataclass(self.rotation, config_dict['rotation'])
        if 'compliance' in config_dict:
            self._update_dataclass(self.compliance, config_dict['compliance'])
        if 'monitoring' in config_dict:
            self._update_dataclass(self.monitoring, config_dict['monitoring'])
        if 'backup' in config_dict:
            self._update_dataclass(self.backup, config_dict['backup'])
        
        # Update security settings
        if 'require_tls' in config_dict:
            self.require_tls = config_dict['require_tls']
        if 'certificate_validation' in config_dict:
            self.certificate_validation = config_dict['certificate_validation']
        if 'ip_whitelist' in config_dict:
            self.ip_whitelist = config_dict['ip_whitelist']
    
    def _update_dataclass(self, instance: Any, data: Dict[str, Any]) -> None:
        """Update dataclass instance with dictionary data."""
        for key, value in data.items():
            if hasattr(instance, key):
                # Handle enum fields
                field_type = type(getattr(instance, key))
                if hasattr(field_type, '__bases__') and Enum in field_type.__bases__:
                    value = field_type(value)
                
                setattr(instance, key, value)
    
    def _load_env_variables(self) -> None:
        """Load configuration from environment variables."""
        # Vault configuration
        if os.getenv('VAULT_ADDR'):
            self.vault.url = os.getenv('VAULT_ADDR')
        if os.getenv('VAULT_TOKEN'):
            self.vault.token = os.getenv('VAULT_TOKEN')
        if os.getenv('VAULT_NAMESPACE'):
            self.vault.namespace = os.getenv('VAULT_NAMESPACE')
        if os.getenv('VAULT_ROLE'):
            self.vault.role = os.getenv('VAULT_ROLE')
        
        # Kubernetes configuration
        if os.getenv('KUBERNETES_NAMESPACE'):
            self.kubernetes.namespace = os.getenv('KUBERNETES_NAMESPACE')
        if os.getenv('KUBERNETES_SERVICE_ACCOUNT'):
            self.kubernetes.service_account = os.getenv('KUBERNETES_SERVICE_ACCOUNT')
        
        # AWS configuration
        if os.getenv('AWS_REGION'):
            self.aws.region = os.getenv('AWS_REGION')
        if os.getenv('AWS_ACCESS_KEY_ID'):
            self.aws.access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
        if os.getenv('AWS_SECRET_ACCESS_KEY'):
            self.aws.secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        if os.getenv('AWS_SESSION_TOKEN'):
            self.aws.session_token = os.getenv('AWS_SESSION_TOKEN')
        
        # Azure configuration
        if os.getenv('AZURE_KEY_VAULT_URL'):
            self.azure.vault_url = os.getenv('AZURE_KEY_VAULT_URL')
        if os.getenv('AZURE_TENANT_ID'):
            self.azure.tenant_id = os.getenv('AZURE_TENANT_ID')
        if os.getenv('AZURE_CLIENT_ID'):
            self.azure.client_id = os.getenv('AZURE_CLIENT_ID')
        if os.getenv('AZURE_CLIENT_SECRET'):
            self.azure.client_secret = os.getenv('AZURE_CLIENT_SECRET')
        
        # GCP configuration
        if os.getenv('GCP_PROJECT_ID'):
            self.gcp.project_id = os.getenv('GCP_PROJECT_ID')
        if os.getenv('GOOGLE_APPLICATION_CREDENTIALS'):
            self.gcp.credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        
        # General settings
        if os.getenv('SECRET_SERVICE_ACCOUNT'):
            self.service_account = os.getenv('SECRET_SERVICE_ACCOUNT')
        if os.getenv('SECRET_LOG_LEVEL'):
            self.log_level = os.getenv('SECRET_LOG_LEVEL')
        if os.getenv('SECRET_DEBUG_MODE'):
            self.debug_mode = os.getenv('SECRET_DEBUG_MODE').lower() == 'true'
    
    def _validate_config(self) -> None:
        """Validate configuration settings."""
        logger = logging.getLogger(__name__)
        
        # Validate primary provider configuration
        if self.primary_provider == SecretProvider.HASHICORP_VAULT:
            if not self.vault.url:
                raise ValueError("Vault URL is required for HashiCorp Vault provider")
            if not self.vault.token and self.vault.auth_method == "token":
                logger.warning("Vault token not configured for token auth method")
        
        elif self.primary_provider == SecretProvider.AWS_SECRETS_MANAGER:
            if not self.aws.region:
                raise ValueError("AWS region is required for AWS Secrets Manager")
        
        elif self.primary_provider == SecretProvider.AZURE_KEY_VAULT:
            if not self.azure.vault_url:
                raise ValueError("Azure Key Vault URL is required")
        
        elif self.primary_provider == SecretProvider.GCP_SECRET_MANAGER:
            if not self.gcp.project_id:
                raise ValueError("GCP project ID is required for Google Secret Manager")
        
        # Validate encryption configuration
        if self.encryption.algorithm == EncryptionAlgorithm.RSA_OAEP and self.encryption.key_size < 2048:
            raise ValueError("RSA key size must be at least 2048 bits")
        
        # Validate compliance settings
        if self.environment == Environment.PRODUCTION:
            if not self.compliance.audit_enabled:
                logger.warning("Audit logging is disabled in production environment")
            if not self.require_tls:
                logger.warning("TLS is disabled in production environment")
    
    def get_provider_config(self, provider: SecretProvider) -> Any:
        """
        Get configuration for specific provider.
        
        Args:
            provider: Secret provider to get config for
            
        Returns:
            Provider configuration object
        """
        provider_configs = {
            SecretProvider.HASHICORP_VAULT: self.vault,
            SecretProvider.KUBERNETES_SECRETS: self.kubernetes,
            SecretProvider.AWS_SECRETS_MANAGER: self.aws,
            SecretProvider.AZURE_KEY_VAULT: self.azure,
            SecretProvider.GCP_SECRET_MANAGER: self.gcp
        }
        
        return provider_configs.get(provider)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            'environment': self.environment.value,
            'service_account': self.service_account,
            'log_level': self.log_level,
            'debug_mode': self.debug_mode,
            'primary_provider': self.primary_provider.value,
            'fallback_providers': [p.value for p in self.fallback_providers],
            'vault': self._dataclass_to_dict(self.vault),
            'kubernetes': self._dataclass_to_dict(self.kubernetes),
            'aws': self._dataclass_to_dict(self.aws),
            'azure': self._dataclass_to_dict(self.azure),
            'gcp': self._dataclass_to_dict(self.gcp),
            'encryption': self._dataclass_to_dict(self.encryption),
            'rotation': self._dataclass_to_dict(self.rotation),
            'compliance': self._dataclass_to_dict(self.compliance),
            'monitoring': self._dataclass_to_dict(self.monitoring),
            'backup': self._dataclass_to_dict(self.backup),
            'require_tls': self.require_tls,
            'certificate_validation': self.certificate_validation,
            'ip_whitelist': self.ip_whitelist
        }
    
    def _dataclass_to_dict(self, instance: Any) -> Dict[str, Any]:
        """Convert dataclass instance to dictionary."""
        result = {}
        for field_name in instance.__dataclass_fields__:
            value = getattr(instance, field_name)
            if hasattr(value, '__dataclass_fields__'):
                # Nested dataclass
                result[field_name] = self._dataclass_to_dict(value)
            elif isinstance(value, Enum):
                result[field_name] = value.value
            else:
                result[field_name] = value
        return result
    
    def save_config(self, file_path: Optional[str] = None) -> bool:
        """
        Save current configuration to file.
        
        Args:
            file_path: Optional path to save config to
            
        Returns:
            bool: True if successful
        """
        try:
            save_path = file_path or self.config_file
            config_data = {
                self.environment.value: self.to_dict()
            }
            
            # Ensure directory exists
            config_dir = os.path.dirname(save_path)
            os.makedirs(config_dir, exist_ok=True)
            
            with open(save_path, 'w') as f:
                if save_path.endswith('.json'):
                    json.dump(config_data, f, indent=2)
                else:
                    yaml.dump(config_data, f, default_flow_style=False, indent=2)
            
            logger = logging.getLogger(__name__)
            logger.info(f"Configuration saved to {save_path}")
            return True
            
        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to save configuration: {e}")
            return False
    
    # Convenience properties for common configurations
    @property
    def vault_url(self) -> str:
        """Get Vault URL."""
        return self.vault.url
    
    @property
    def vault_token(self) -> Optional[str]:
        """Get Vault token."""
        return self.vault.token
    
    @property
    def vault_namespace(self) -> Optional[str]:
        """Get Vault namespace."""
        return self.vault.namespace
    
    @property
    def vault_auth_method(self) -> str:
        """Get Vault auth method."""
        return self.vault.auth_method
    
    @property
    def vault_role(self) -> str:
        """Get Vault role."""
        return self.vault.role
    
    @property
    def vault_kv_version(self) -> int:
        """Get Vault KV version."""
        return self.vault.kv_version
    
    @property
    def kubernetes_namespace(self) -> str:
        """Get Kubernetes namespace."""
        return self.kubernetes.namespace
    
    @property
    def kubernetes_token(self) -> str:
        """Get Kubernetes service account token."""
        try:
            with open(self.kubernetes.token_path, 'r') as f:
                return f.read().strip()
        except Exception:
            return ""
    
    @property
    def ldap_username(self) -> Optional[str]:
        """Get LDAP username from environment."""
        return os.getenv('LDAP_USERNAME')
    
    @property
    def ldap_password(self) -> Optional[str]:
        """Get LDAP password from environment."""
        return os.getenv('LDAP_PASSWORD')
    
    @property
    def rotation_jobs_file(self) -> str:
        """Get rotation jobs file path."""
        return self.rotation.jobs_file
    
    @property
    def audit_webhook_url(self) -> Optional[str]:
        """Get audit webhook URL."""
        return self.compliance.audit_webhook_url
    
    @property
    def is_production(self) -> bool:
        """Check if running in production."""
        return self.environment == Environment.PRODUCTION
    
    @property
    def is_development(self) -> bool:
        """Check if running in development."""
        return self.environment == Environment.DEVELOPMENT


# Global configuration instance
_config_instance: Optional[SecretsConfig] = None


def get_config() -> SecretsConfig:
    """Get global configuration instance."""
    global _config_instance
    if _config_instance is None:
        _config_instance = SecretsConfig()
    return _config_instance


def set_config(config: SecretsConfig) -> None:
    """Set global configuration instance."""
    global _config_instance
    _config_instance = config


# Environment-specific configuration helpers
def load_development_config() -> SecretsConfig:
    """Load development configuration."""
    return SecretsConfig(environment=Environment.DEVELOPMENT)


def load_staging_config() -> SecretsConfig:
    """Load staging configuration."""
    return SecretsConfig(environment=Environment.STAGING)


def load_production_config() -> SecretsConfig:
    """Load production configuration."""
    return SecretsConfig(environment=Environment.PRODUCTION)


def load_testing_config() -> SecretsConfig:
    """Load testing configuration."""
    return SecretsConfig(environment=Environment.TESTING)
