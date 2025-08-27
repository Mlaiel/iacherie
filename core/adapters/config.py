"""
Adapter Configuration Management

This module handles configuration loading, validation, and management for all
platform adapters. It provides a centralized way to configure adapters with
support for environment variables, configuration files, and runtime updates.

Author: Fahed Mlaiel
Email: mlaiel@live.de
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution
of this code is strictly prohibited without explicit written permission.

Features:
- Environment-based configuration
- Configuration file support (JSON, YAML)
- Runtime configuration updates
- Configuration validation and schema enforcement
- Secure credential management
- Multi-environment support (dev, staging, prod)
"""

import os
import json
import yaml
import logging
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, field, asdict
from pathlib import Path
from enum import Enum
from cryptography.fernet import Fernet
import base64

logger = logging.getLogger(__name__)

class Environment(str, Enum):
    """Supported deployment environments."""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"

@dataclass
class RateLimitConfig:
    """Rate limiting configuration."""
    max_requests: int = 100
    time_window: int = 60  # seconds
    burst_limit: int = 10
    retry_after: int = 60

@dataclass
class SecurityConfig:
    """Security configuration for adapters."""
    use_ssl: bool = True
    verify_certificates: bool = True
    timeout: int = 30
    max_retries: int = 3
    backoff_factor: float = 1.0
    encrypt_credentials: bool = True

@dataclass
class HealthCheckConfig:
    """Health check configuration."""
    enabled: bool = True
    interval: int = 300  # seconds
    timeout: int = 10
    retry_attempts: int = 3
    alert_threshold: int = 3  # consecutive failures

@dataclass
class AdapterBaseConfig:
    """Base configuration for all adapters."""
    name: str
    platform_type: str
    enabled: bool = True
    priority: int = 1
    rate_limit: RateLimitConfig = field(default_factory=RateLimitConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    health_check: HealthCheckConfig = field(default_factory=HealthCheckConfig)
    custom_settings: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SocialMediaAdapterConfig(AdapterBaseConfig):
    """Configuration for social media adapters."""
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    access_token: Optional[str] = None
    access_token_secret: Optional[str] = None
    webhook_url: Optional[str] = None
    webhook_secret: Optional[str] = None
    max_posts_per_day: int = 50
    auto_publish: bool = False

@dataclass
class AIAdapterConfig(AdapterBaseConfig):
    """Configuration for AI platform adapters."""
    api_key: Optional[str] = None
    api_endpoint: Optional[str] = None
    model_name: str = "gpt-3.5-turbo"
    max_tokens: int = 4000
    temperature: float = 0.7
    max_requests_per_minute: int = 60
    cost_per_token: float = 0.002
    enable_caching: bool = True

@dataclass
class ContentProtectionConfig(AdapterBaseConfig):
    """Configuration for content protection adapters."""
    api_key: Optional[str] = None
    content_id_system: str = "youtube"
    auto_claim: bool = False
    auto_takedown: bool = False
    monitoring_interval: int = 3600  # seconds
    notification_email: Optional[str] = None
    minimum_match_duration: int = 30  # seconds

@dataclass
class EmailMarketingConfig(AdapterBaseConfig):
    """Configuration for email marketing adapters."""
    api_key: Optional[str] = None
    list_id: Optional[str] = None
    sender_email: Optional[str] = None
    sender_name: Optional[str] = None
    webhook_url: Optional[str] = None
    double_optin: bool = True
    track_opens: bool = True
    track_clicks: bool = True

@dataclass
class SEOPlatformConfig(AdapterBaseConfig):
    """Configuration for SEO platform adapters."""
    api_key: Optional[str] = None
    site_url: Optional[str] = None
    country_code: str = "US"
    language_code: str = "en"
    update_frequency: str = "daily"
    track_keywords: List[str] = field(default_factory=list)
    competitor_domains: List[str] = field(default_factory=list)

class CredentialManager:
    """Manages secure credential storage and retrieval."""
    
    def __init__(self, encryption_key: Optional[str] = None):
        if encryption_key:
            self.cipher = Fernet(encryption_key.encode() if isinstance(encryption_key, str) else encryption_key)
        else:
            # Generate or load encryption key
            key = os.getenv('ADAPTER_ENCRYPTION_KEY')
            if not key:
                key = Fernet.generate_key()
                logger.warning("No encryption key provided, generated new key. Store this securely!")
                logger.warning(f"Generated key: {key.decode()}")
            else:
                key = key.encode()
            self.cipher = Fernet(key)
    
    def encrypt_credential(self, value: str) -> str:
        """Encrypt a credential value."""
        if not value:
            return value
        encrypted = self.cipher.encrypt(value.encode())
        return base64.b64encode(encrypted).decode()
    
    def decrypt_credential(self, encrypted_value: str) -> str:
        """Decrypt a credential value."""
        if not encrypted_value:
            return encrypted_value
        try:
            decoded = base64.b64decode(encrypted_value.encode())
            decrypted = self.cipher.decrypt(decoded)
            return decrypted.decode()
        except Exception as e:
            logger.error(f"Failed to decrypt credential: {str(e)}")
            return encrypted_value  # Return as-is if decryption fails

class ConfigurationManager:
    """Manages adapter configurations across different environments."""
    
    def __init__(self, config_dir: Optional[Path] = None, environment: Environment = Environment.DEVELOPMENT):
        self.config_dir = config_dir or Path(__file__).parent
        self.environment = environment
        self.credential_manager = CredentialManager()
        self.configurations: Dict[str, AdapterBaseConfig] = {}
        self._load_configurations()
    
    def _load_configurations(self):
        """Load configurations from files and environment variables."""
        # Load base configuration
        base_config_file = self.config_dir / f"adapters_config.yaml"
        if base_config_file.exists():
            self._load_from_file(base_config_file)
        else:
            self._create_default_config_file(base_config_file)
        
        # Override with environment variables
        self._load_from_environment()
    
    def _load_from_file(self, config_file: Path):
        """Load configuration from a YAML or JSON file."""
        try:
            with open(config_file, 'r') as f:
                if config_file.suffix.lower() == '.yaml' or config_file.suffix.lower() == '.yml':
                    config_data = yaml.safe_load(f)
                else:
                    config_data = json.load(f)
            
            # Parse configurations
            for adapter_name, adapter_config in config_data.get('adapters', {}).items():
                self._parse_adapter_config(adapter_name, adapter_config)
            
            logger.info(f"Loaded configuration from {config_file}")
        
        except Exception as e:
            logger.error(f"Failed to load configuration from {config_file}: {str(e)}")
    
    def _parse_adapter_config(self, adapter_name: str, config_data: Dict[str, Any]):
        """Parse adapter configuration data into appropriate config object."""
        platform_type = config_data.get('platform_type', '').lower()
        
        # Decrypt sensitive fields
        sensitive_fields = ['api_key', 'api_secret', 'access_token', 'access_token_secret', 'webhook_secret']
        for field in sensitive_fields:
            if field in config_data and config_data[field]:
                config_data[field] = self.credential_manager.decrypt_credential(config_data[field])
        
        # Create appropriate config object based on platform type
        if 'social' in platform_type:
            config = SocialMediaAdapterConfig(**config_data)
        elif 'ai' in platform_type:
            config = AIAdapterConfig(**config_data)
        elif 'content_protection' in platform_type:
            config = ContentProtectionConfig(**config_data)
        elif 'email' in platform_type:
            config = EmailMarketingConfig(**config_data)
        elif 'seo' in platform_type:
            config = SEOPlatformConfig(**config_data)
        else:
            config = AdapterBaseConfig(**config_data)
        
        self.configurations[adapter_name] = config
    
    def _load_from_environment(self):
        """Load configuration overrides from environment variables."""
        # Look for environment variables with pattern: ADAPTER_{ADAPTER_NAME}_{SETTING}
        for key, value in os.environ.items():
            if key.startswith('ADAPTER_'):
                parts = key.split('_', 2)
                if len(parts) >= 3:
                    adapter_name = parts[1].lower()
                    setting_name = parts[2].lower()
                    
                    if adapter_name in self.configurations:
                        # Update the configuration
                        config = self.configurations[adapter_name]
                        if hasattr(config, setting_name):
                            setattr(config, setting_name, self._convert_env_value(value))
                            logger.debug(f"Override {adapter_name}.{setting_name} from environment")
    
    def _convert_env_value(self, value: str) -> Union[str, int, float, bool]:
        """Convert environment variable string to appropriate type."""
        # Try boolean
        if value.lower() in ('true', 'false'):
            return value.lower() == 'true'
        
        # Try integer
        try:
            return int(value)
        except ValueError:
            pass
        
        # Try float
        try:
            return float(value)
        except ValueError:
            pass
        
        # Return as string
        return value
    
    def _create_default_config_file(self, config_file: Path):
        """Create a default configuration file."""
        default_config = {
            'environment': self.environment.value,
            'adapters': {
                'youtube_adapter': {
                    'name': 'youtube_adapter',
                    'platform_type': 'social_media',
                    'enabled': True,
                    'api_key': '${YOUTUBE_API_KEY}',
                    'max_posts_per_day': 10
                },
                'openai_adapter': {
                    'name': 'openai_adapter',
                    'platform_type': 'ai_platform',
                    'enabled': True,
                    'api_key': '${OPENAI_API_KEY}',
                    'model_name': 'gpt-3.5-turbo',
                    'max_tokens': 4000
                },
                'mailchimp_adapter': {
                    'name': 'mailchimp_adapter',
                    'platform_type': 'email_marketing',
                    'enabled': True,
                    'api_key': '${MAILCHIMP_API_KEY}',
                    'double_optin': True
                }
            }
        }
        
        try:
            with open(config_file, 'w') as f:
                yaml.dump(default_config, f, default_flow_style=False, indent=2)
            logger.info(f"Created default configuration file: {config_file}")
        except Exception as e:
            logger.error(f"Failed to create default configuration file: {str(e)}")
    
    def get_adapter_config(self, adapter_name: str) -> Optional[AdapterBaseConfig]:
        """Get configuration for a specific adapter."""
        return self.configurations.get(adapter_name)
    
    def update_adapter_config(self, adapter_name: str, config: AdapterBaseConfig):
        """Update configuration for an adapter."""
        self.configurations[adapter_name] = config
        logger.info(f"Updated configuration for adapter: {adapter_name}")
    
    def save_configuration(self, config_file: Optional[Path] = None):
        """Save current configurations to file."""
        if not config_file:
            config_file = self.config_dir / f"adapters_config.yaml"
        
        # Prepare data for saving
        config_data = {
            'environment': self.environment.value,
            'adapters': {}
        }
        
        for adapter_name, config in self.configurations.items():
            adapter_data = asdict(config)
            
            # Encrypt sensitive fields before saving
            sensitive_fields = ['api_key', 'api_secret', 'access_token', 'access_token_secret', 'webhook_secret']
            for field in sensitive_fields:
                if field in adapter_data and adapter_data[field]:
                    adapter_data[field] = self.credential_manager.encrypt_credential(adapter_data[field])
            
            config_data['adapters'][adapter_name] = adapter_data
        
        try:
            with open(config_file, 'w') as f:
                yaml.dump(config_data, f, default_flow_style=False, indent=2)
            logger.info(f"Saved configuration to {config_file}")
        except Exception as e:
            logger.error(f"Failed to save configuration: {str(e)}")
    
    def list_adapters(self) -> List[str]:
        """List all configured adapters."""
        return list(self.configurations.keys())
    
    def validate_configuration(self, adapter_name: str) -> Dict[str, Any]:
        """Validate adapter configuration and return validation results."""
        config = self.configurations.get(adapter_name)
        if not config:
            return {'valid': False, 'errors': [f'Adapter {adapter_name} not found']}
        
        errors = []
        warnings = []
        
        # Basic validation
        if not config.name:
            errors.append('Adapter name is required')
        
        if not config.platform_type:
            errors.append('Platform type is required')
        
        # Platform-specific validation
        if isinstance(config, SocialMediaAdapterConfig):
            if not config.api_key and not config.access_token:
                errors.append('API key or access token is required for social media adapters')
        
        elif isinstance(config, AIAdapterConfig):
            if not config.api_key:
                errors.append('API key is required for AI adapters')
            if config.max_tokens <= 0:
                errors.append('Max tokens must be positive')
        
        elif isinstance(config, ContentProtectionConfig):
            if not config.api_key:
                errors.append('API key is required for content protection adapters')
        
        elif isinstance(config, EmailMarketingConfig):
            if not config.api_key:
                errors.append('API key is required for email marketing adapters')
            if not config.sender_email:
                warnings.append('Sender email not configured')
        
        elif isinstance(config, SEOPlatformConfig):
            if not config.api_key:
                errors.append('API key is required for SEO platform adapters')
            if not config.site_url:
                warnings.append('Site URL not configured')
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
    
    def get_environment_info(self) -> Dict[str, Any]:
        """Get information about the current environment configuration."""
        return {
            'environment': self.environment.value,
            'config_dir': str(self.config_dir),
            'total_adapters': len(self.configurations),
            'enabled_adapters': sum(1 for config in self.configurations.values() if config.enabled),
            'platform_types': list(set(config.platform_type for config in self.configurations.values()))
        }

# Global configuration manager instance
_config_manager: Optional[ConfigurationManager] = None

def get_configuration_manager(environment: Optional[Environment] = None) -> ConfigurationManager:
    """Get the global configuration manager instance."""
    global _config_manager
    if _config_manager is None or (environment and _config_manager.environment != environment):
        env = environment or Environment(os.getenv('ADAPTER_ENVIRONMENT', 'development'))
        _config_manager = ConfigurationManager(environment=env)
    return _config_manager

def get_adapter_config(adapter_name: str) -> Optional[AdapterBaseConfig]:
    """Get configuration for a specific adapter."""
    manager = get_configuration_manager()
    return manager.get_adapter_config(adapter_name)

def validate_adapter_config(adapter_name: str) -> Dict[str, Any]:
    """Validate configuration for a specific adapter."""
    manager = get_configuration_manager()
    return manager.validate_configuration(adapter_name)

# Export all public classes and functions
__all__ = [
    'Environment', 'RateLimitConfig', 'SecurityConfig', 'HealthCheckConfig',
    'AdapterBaseConfig', 'SocialMediaAdapterConfig', 'AIAdapterConfig',
    'ContentProtectionConfig', 'EmailMarketingConfig', 'SEOPlatformConfig',
    'CredentialManager', 'ConfigurationManager',
    'get_configuration_manager', 'get_adapter_config', 'validate_adapter_config'
]
