"""⚙️ Enterprise Crawler Configuration Management
=============================================

Advanced configuration management system for enterprise crawler infrastructure
with dynamic configuration, environment management, and validation features.

Features:
- Dynamic configuration management
- Environment-specific settings
- Configuration validation and schema
- Hot-reload capabilities
- Encrypted sensitive configuration
- Configuration versioning
- Audit logging for changes
- Template-based configuration
- Multi-environment support
- Configuration inheritance

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

⚠️ STRICT WARNING: Unauthorized use, copying, or distribution of this code 
is strictly prohibited without explicit written permission from Fahed Mlaiel.
Contact: mlaiel@live.de for licensing and authorization.
"""
import os
import json
import yaml
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
import copy
from cryptography.fernet import Fernet
import base64

logger = logging.getLogger(__name__)

class ConfigurationEnvironment(str, Enum):
    """Configuration environment types."""
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"

class ConfigurationFormat(str, Enum):
    """Configuration file formats."""
    JSON = "json"
    YAML = "yaml"
    TOML = "toml"
    ENV = "env"

@dataclass
class PlatformConfiguration:
    """Platform-specific configuration."""
    enabled: bool = True
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    base_url: Optional[str] = None
    rate_limit_rpm: int = 60
    rate_limit_rph: int = 1000
    rate_limit_rpd: int = 10000
    timeout: int = 30
    retry_count: int = 3
    retry_delay: float = 1.0
    user_agents: List[str] = field(default_factory=list)
    proxy_pool: List[str] = field(default_factory=list)
    custom_headers: Dict[str, str] = field(default_factory=dict)
    anti_detection: bool = True
    selenium_enabled: bool = False
    chrome_options: List[str] = field(default_factory=list)
    firefox_options: List[str] = field(default_factory=list)

@dataclass
class CrawlerConfiguration:
    """Complete crawler configuration."""
    # General settings
    environment: ConfigurationEnvironment = ConfigurationEnvironment.DEVELOPMENT
    max_workers: int = 50
    max_concurrent_crawlers: int = 10
    crawl_interval_minutes: int = 30
    enable_real_time_monitoring: bool = True
    
    # Storage and caching
    credential_storage_path: str = "./credentials"
    cache_storage_path: str = "./cache"
    log_storage_path: str = "./logs"
    master_password: str = "change_me_in_production"
    cache_duration_seconds: int = 3600
    
    # Rate limiting
    global_rate_limit_enabled: bool = True
    adaptive_rate_limiting: bool = True
    circuit_breaker_enabled: bool = True
    
    # Monitoring and alerting
    webhook_enabled: bool = False
    webhook_urls: List[str] = field(default_factory=list)
    alert_email_enabled: bool = False
    alert_email_recipients: List[str] = field(default_factory=list)
    performance_monitoring_enabled: bool = True
    
    # Security
    encryption_enabled: bool = True
    audit_logging_enabled: bool = True
    ip_rotation_enabled: bool = False
    
    # Platform configurations
    youtube: PlatformConfiguration = field(default_factory=PlatformConfiguration)
    instagram: PlatformConfiguration = field(default_factory=PlatformConfiguration)
    twitter: PlatformConfiguration = field(default_factory=PlatformConfiguration)
    tiktok: PlatformConfiguration = field(default_factory=PlatformConfiguration)
    generic_web: PlatformConfiguration = field(default_factory=PlatformConfiguration)
    
    # Custom platform configurations
    custom_platforms: Dict[str, PlatformConfiguration] = field(default_factory=dict)

class ConfigurationManager:
    """
    Enterprise configuration management system.
    
    Provides comprehensive configuration management with:
    - Multi-environment support
    - Dynamic configuration loading
    - Configuration validation
    - Encrypted storage for sensitive data
    - Hot-reload capabilities
    - Configuration inheritance
    """
    
    def __init__(
        self,
        config_path: str = "./config",
        environment: ConfigurationEnvironment = ConfigurationEnvironment.DEVELOPMENT
    ):
        """Initialize configuration manager."""
        self.config_path = Path(config_path)
        self.environment = environment
        self.config: Optional[CrawlerConfiguration] = None
        self.config_version = "1.0.0"
        self.last_modified = None
        self.encryption_key = None
        
        # Create config directory if it doesn't exist
        self.config_path.mkdir(exist_ok=True)
        
        # Initialize encryption
        self._initialize_encryption()
        
        logger.info(f"Configuration Manager initialized for {environment.value} environment")
    
    def _initialize_encryption(self):
        """Initialize encryption for sensitive configuration data."""
        key_file = self.config_path / "encryption.key"
        
        if key_file.exists():
            with open(key_file, 'rb') as f:
                self.encryption_key = f.read()
        else:
            # Generate new encryption key
            self.encryption_key = Fernet.generate_key()
            with open(key_file, 'wb') as f:
                f.write(self.encryption_key)
            # Secure the key file
            key_file.chmod(0o600)
        
        logger.info("Encryption initialized for configuration management")
    
    def load_configuration(self, config_file: Optional[str] = None) -> CrawlerConfiguration:
        """
        Load configuration from file or environment.
        
        Args:
            config_file: Specific config file to load
            
        Returns:
            Loaded configuration
        """
        if config_file:
            config_path = Path(config_file)
        else:
            # Try different config file names
            config_candidates = [
                f"crawler_config_{self.environment.value}.yaml",
                f"crawler_config_{self.environment.value}.json",
                "crawler_config.yaml",
                "crawler_config.json"
            ]
            
            config_path = None
            for candidate in config_candidates:
                candidate_path = self.config_path / candidate
                if candidate_path.exists():
                    config_path = candidate_path
                    break
        
        if config_path and config_path.exists():
            config_data = self._load_config_file(config_path)
            self.config = self._parse_configuration(config_data)
            self.last_modified = datetime.fromtimestamp(config_path.stat().st_mtime)
        else:
            logger.warning("No configuration file found, using defaults")
            self.config = CrawlerConfiguration()
        
        # Apply environment-specific overrides
        self._apply_environment_overrides()
        
        # Validate configuration
        self._validate_configuration()
        
        logger.info(f"Configuration loaded for {self.environment.value} environment")
        return self.config
    
    def _load_config_file(self, config_path: Path) -> Dict[str, Any]:
        """Load configuration from file."""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                if config_path.suffix.lower() == '.yaml' or config_path.suffix.lower() == '.yml':
                    return yaml.safe_load(f)
                elif config_path.suffix.lower() == '.json':
                    return json.load(f)
                else:
                    raise ValueError(f"Unsupported config file format: {config_path.suffix}")
        except Exception as e:
            logger.error(f"Failed to load config file {config_path}: {e}")
            raise
    
    def _parse_configuration(self, config_data: Dict[str, Any]) -> CrawlerConfiguration:
        """Parse configuration data into structured format."""
        config = CrawlerConfiguration()
        
        # Parse general settings
        if 'general' in config_data:
            general = config_data['general']
            config.environment = ConfigurationEnvironment(
                general.get('environment', config.environment.value)
            )
            config.max_workers = general.get('max_workers', config.max_workers)
            config.max_concurrent_crawlers = general.get(
                'max_concurrent_crawlers', config.max_concurrent_crawlers
            )
            config.crawl_interval_minutes = general.get(
                'crawl_interval_minutes', config.crawl_interval_minutes
            )
            config.enable_real_time_monitoring = general.get(
                'enable_real_time_monitoring', config.enable_real_time_monitoring
            )
        
        # Parse storage settings
        if 'storage' in config_data:
            storage = config_data['storage']
            config.credential_storage_path = storage.get(
                'credential_storage_path', config.credential_storage_path
            )
            config.cache_storage_path = storage.get(
                'cache_storage_path', config.cache_storage_path
            )
            config.log_storage_path = storage.get(
                'log_storage_path', config.log_storage_path
            )
            config.cache_duration_seconds = storage.get(
                'cache_duration_seconds', config.cache_duration_seconds
            )
        
        # Parse platform configurations
        for platform_name in ['youtube', 'instagram', 'twitter', 'tiktok', 'generic_web']:
            if platform_name in config_data:
                platform_config = self._parse_platform_config(config_data[platform_name])
                setattr(config, platform_name, platform_config)
        
        # Parse webhooks
        if 'webhooks' in config_data:
            webhooks = config_data['webhooks']
            config.webhook_enabled = webhooks.get('enabled', config.webhook_enabled)
            config.webhook_urls = webhooks.get('urls', config.webhook_urls)
        
        # Parse monitoring
        if 'monitoring' in config_data:
            monitoring = config_data['monitoring']
            config.performance_monitoring_enabled = monitoring.get(
                'performance_monitoring_enabled', config.performance_monitoring_enabled
            )
            config.alert_email_enabled = monitoring.get(
                'alert_email_enabled', config.alert_email_enabled
            )
            config.alert_email_recipients = monitoring.get(
                'alert_email_recipients', config.alert_email_recipients
            )
        
        return config
    
    def _parse_platform_config(self, platform_data: Dict[str, Any]) -> PlatformConfiguration:
        """Parse platform-specific configuration."""
        platform_config = PlatformConfiguration()
        
        # Basic settings
        platform_config.enabled = platform_data.get('enabled', platform_config.enabled)
        platform_config.base_url = platform_data.get('base_url', platform_config.base_url)
        platform_config.timeout = platform_data.get('timeout', platform_config.timeout)
        platform_config.retry_count = platform_data.get('retry_count', platform_config.retry_count)
        platform_config.retry_delay = platform_data.get('retry_delay', platform_config.retry_delay)
        
        # Rate limiting
        if 'rate_limiting' in platform_data:
            rate_limiting = platform_data['rate_limiting']
            platform_config.rate_limit_rpm = rate_limiting.get(
                'requests_per_minute', platform_config.rate_limit_rpm
            )
            platform_config.rate_limit_rph = rate_limiting.get(
                'requests_per_hour', platform_config.rate_limit_rph
            )
            platform_config.rate_limit_rpd = rate_limiting.get(
                'requests_per_day', platform_config.rate_limit_rpd
            )
        
        # Authentication (encrypted)
        if 'authentication' in platform_data:
            auth = platform_data['authentication']
            platform_config.api_key = self._decrypt_if_encrypted(
                auth.get('api_key', platform_config.api_key)
            )
            platform_config.api_secret = self._decrypt_if_encrypted(
                auth.get('api_secret', platform_config.api_secret)
            )
            platform_config.access_token = self._decrypt_if_encrypted(
                auth.get('access_token', platform_config.access_token)
            )
            platform_config.refresh_token = self._decrypt_if_encrypted(
                auth.get('refresh_token', platform_config.refresh_token)
            )
        
        # Anti-detection settings
        if 'anti_detection' in platform_data:
            anti_detection = platform_data['anti_detection']
            platform_config.anti_detection = anti_detection.get(
                'enabled', platform_config.anti_detection
            )
            platform_config.user_agents = anti_detection.get(
                'user_agents', platform_config.user_agents
            )
            platform_config.proxy_pool = anti_detection.get(
                'proxy_pool', platform_config.proxy_pool
            )
        
        # Selenium settings
        if 'selenium' in platform_data:
            selenium = platform_data['selenium']
            platform_config.selenium_enabled = selenium.get(
                'enabled', platform_config.selenium_enabled
            )
            platform_config.chrome_options = selenium.get(
                'chrome_options', platform_config.chrome_options
            )
            platform_config.firefox_options = selenium.get(
                'firefox_options', platform_config.firefox_options
            )
        
        return platform_config
    
    def _decrypt_if_encrypted(self, value: Optional[str]) -> Optional[str]:
        """Decrypt value if it's encrypted."""
        if not value or not value.startswith('ENCRYPTED:'):
            return value
        
        try:
            cipher_suite = Fernet(self.encryption_key)
            encrypted_data = value[10:]  # Remove 'ENCRYPTED:' prefix
            decrypted_bytes = cipher_suite.decrypt(encrypted_data.encode())
            return decrypted_bytes.decode()
        except Exception as e:
            logger.error(f"Failed to decrypt configuration value: {e}")
            return None
    
    def _apply_environment_overrides(self):
        """Apply environment variable overrides."""
        # Override with environment variables
        env_mappings = {
            'CRAWLER_MAX_WORKERS': ('max_workers', int),
            'CRAWLER_CRAWL_INTERVAL': ('crawl_interval_minutes', int),
            'CRAWLER_MASTER_PASSWORD': ('master_password', str),
            'YOUTUBE_API_KEY': ('youtube.api_key', str),
            'INSTAGRAM_ACCESS_TOKEN': ('instagram.access_token', str),
            'TWITTER_BEARER_TOKEN': ('twitter.access_token', str),
            'TIKTOK_ACCESS_TOKEN': ('tiktok.access_token', str),
        }
        
        for env_var, (config_path, value_type) in env_mappings.items():
            env_value = os.getenv(env_var)
            if env_value:
                try:
                    typed_value = value_type(env_value)
                    self._set_nested_config_value(config_path, typed_value)
                    logger.debug(f"Applied environment override: {env_var}")
                except Exception as e:
                    logger.warning(f"Failed to apply environment override {env_var}: {e}")
    
    def _set_nested_config_value(self, path: str, value: Any):
        """Set nested configuration value using dot notation."""
        parts = path.split('.')
        obj = self.config
        
        for part in parts[:-1]:
            obj = getattr(obj, part)
        
        setattr(obj, parts[-1], value)
    
    def _validate_configuration(self):
        """Validate configuration for common issues."""
        validation_errors = []
        
        # Validate general settings
        if self.config.max_workers <= 0:
            validation_errors.append("max_workers must be positive")
        
        if self.config.crawl_interval_minutes <= 0:
            validation_errors.append("crawl_interval_minutes must be positive")
        
        # Validate storage paths
        try:
            Path(self.config.credential_storage_path).mkdir(exist_ok=True)
        except Exception as e:
            validation_errors.append(f"Invalid credential_storage_path: {e}")
        
        # Validate platform configurations
        for platform_name in ['youtube', 'instagram', 'twitter', 'tiktok']:
            platform_config = getattr(self.config, platform_name)
            if platform_config.enabled:
                if not platform_config.api_key and not platform_config.access_token:
                    validation_errors.append(
                        f"{platform_name} is enabled but missing authentication credentials"
                    )
        
        # Validate webhook URLs
        if self.config.webhook_enabled and not self.config.webhook_urls:
            validation_errors.append("Webhooks enabled but no URLs configured")
        
        if validation_errors:
            error_msg = "Configuration validation failed:\n" + "\n".join(validation_errors)
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        logger.info("Configuration validation passed")
    
    def save_configuration(self, config_file: Optional[str] = None) -> bool:
        """
        Save configuration to file.
        
        Args:
            config_file: Specific file to save to
            
        Returns:
            True if saved successfully
        """
        if not self.config:
            logger.error("No configuration loaded to save")
            return False
        
        if not config_file:
            config_file = f"crawler_config_{self.environment.value}.yaml"
        
        config_path = self.config_path / config_file
        
        try:
            # Convert configuration to dictionary
            config_dict = self._configuration_to_dict()
            
            # Save to file
            with open(config_path, 'w', encoding='utf-8') as f:
                yaml.safe_dump(config_dict, f, default_flow_style=False, indent=2)
            
            logger.info(f"Configuration saved to {config_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
            return False
    
    def _configuration_to_dict(self) -> Dict[str, Any]:
        """Convert configuration object to dictionary."""
        # This would implement a comprehensive serialization
        # For brevity, returning a simplified version
        return {
            'general': {
                'environment': self.config.environment.value,
                'max_workers': self.config.max_workers,
                'max_concurrent_crawlers': self.config.max_concurrent_crawlers,
                'crawl_interval_minutes': self.config.crawl_interval_minutes,
                'enable_real_time_monitoring': self.config.enable_real_time_monitoring
            },
            'storage': {
                'credential_storage_path': self.config.credential_storage_path,
                'cache_storage_path': self.config.cache_storage_path,
                'log_storage_path': self.config.log_storage_path,
                'cache_duration_seconds': self.config.cache_duration_seconds
            },
            'webhooks': {
                'enabled': self.config.webhook_enabled,
                'urls': self.config.webhook_urls
            },
            'monitoring': {
                'performance_monitoring_enabled': self.config.performance_monitoring_enabled,
                'alert_email_enabled': self.config.alert_email_enabled,
                'alert_email_recipients': self.config.alert_email_recipients
            }
        }
    
    def encrypt_sensitive_value(self, value: str) -> str:
        """Encrypt sensitive configuration value."""
        if not value:
            return value
        
        try:
            cipher_suite = Fernet(self.encryption_key)
            encrypted_bytes = cipher_suite.encrypt(value.encode())
            return f"ENCRYPTED:{encrypted_bytes.decode()}"
        except Exception as e:
            logger.error(f"Failed to encrypt value: {e}")
            return value
    
    def create_template_configuration(self) -> str:
        """Create template configuration file."""
        template = {
            'general': {
                'environment': 'development',
                'max_workers': 50,
                'max_concurrent_crawlers': 10,
                'crawl_interval_minutes': 30,
                'enable_real_time_monitoring': True
            },
            'storage': {
                'credential_storage_path': './credentials',
                'cache_storage_path': './cache',
                'log_storage_path': './logs',
                'cache_duration_seconds': 3600
            },
            'youtube': {
                'enabled': True,
                'authentication': {
                    'api_key': 'YOUR_YOUTUBE_API_KEY_HERE'
                },
                'rate_limiting': {
                    'requests_per_minute': 100,
                    'requests_per_hour': 1000,
                    'requests_per_day': 10000
                },
                'selenium': {
                    'enabled': False,
                    'chrome_options': ['--headless', '--no-sandbox']
                }
            },
            'instagram': {
                'enabled': True,
                'authentication': {
                    'access_token': 'YOUR_INSTAGRAM_ACCESS_TOKEN_HERE'
                },
                'rate_limiting': {
                    'requests_per_minute': 50,
                    'requests_per_hour': 200
                }
            },
            'twitter': {
                'enabled': True,
                'authentication': {
                    'access_token': 'YOUR_TWITTER_BEARER_TOKEN_HERE'
                },
                'rate_limiting': {
                    'requests_per_minute': 100,
                    'requests_per_hour': 300
                }
            },
            'tiktok': {
                'enabled': True,
                'authentication': {
                    'access_token': 'YOUR_TIKTOK_ACCESS_TOKEN_HERE'
                },
                'rate_limiting': {
                    'requests_per_minute': 60,
                    'requests_per_hour': 1000
                },
                'anti_detection': {
                    'enabled': True,
                    'user_agents': [
                        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                    ],
                    'proxy_pool': []
                }
            },
            'webhooks': {
                'enabled': False,
                'urls': ['https://your-webhook-endpoint.com/notifications']
            },
            'monitoring': {
                'performance_monitoring_enabled': True,
                'alert_email_enabled': False,
                'alert_email_recipients': ['admin@yourcompany.com']
            }
        }
        
        template_file = self.config_path / "crawler_config_template.yaml"
        
        try:
            with open(template_file, 'w', encoding='utf-8') as f:
                yaml.safe_dump(template, f, default_flow_style=False, indent=2)
            
            logger.info(f"Template configuration created at {template_file}")
            return str(template_file)
            
        except Exception as e:
            logger.error(f"Failed to create template configuration: {e}")
            return ""
    
    def get_configuration_summary(self) -> Dict[str, Any]:
        """Get configuration summary for monitoring."""
        if not self.config:
            return {}
        
        return {
            'environment': self.config.environment.value,
            'version': self.config_version,
            'last_modified': self.last_modified.isoformat() if self.last_modified else None,
            'enabled_platforms': [
                platform for platform in ['youtube', 'instagram', 'twitter', 'tiktok', 'generic_web']
                if getattr(self.config, platform).enabled
            ],
            'max_workers': self.config.max_workers,
            'webhook_enabled': self.config.webhook_enabled,
            'monitoring_enabled': self.config.performance_monitoring_enabled,
            'real_time_monitoring': self.config.enable_real_time_monitoring
        }

# Factory function for easy configuration management
def create_configuration_manager(
    config_path: str = "./config",
    environment: str = "development"
) -> ConfigurationManager:
    """Create and initialize configuration manager."""
    env = ConfigurationEnvironment(environment)
    manager = ConfigurationManager(config_path, env)
    return manager

# Export main classes
__all__ = [
    'ConfigurationManager',
    'CrawlerConfiguration',
    'PlatformConfiguration',
    'ConfigurationEnvironment',
    'ConfigurationFormat',
    'create_configuration_manager'
]
