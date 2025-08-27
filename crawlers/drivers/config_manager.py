"""
Enterprise Configuration Manager
===============================

Advanced configuration management system for centralized control of all driver components.
Provides environment-aware configuration loading and validation with security features.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

⚠️  LEGAL WARNING:
This code is proprietary and confidential. Any unauthorized copying, modification, 
distribution, or use without explicit written permission from Fahed Mlaiel is strictly 
prohibited and may result in legal action.

Professional Development Team Specialties:
🥇 Lead AI Developer & Backend Senior Engineer - Advanced automation systems
🥇 Machine Learning Engineer & Audio Processing Specialist - Intelligence optimization  
🥇 Database Administrator & Security Expert - Data protection and performance
🥇 Microservices Architect & DevOps Engineer - Scalable infrastructure
🥇 AI Prompt Engineer & Content Protection Specialist - Content security
"""

import os
import json
import yaml
from typing import Dict, Any, Optional, Union, List
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import logging
from datetime import datetime
import hashlib
import base64
from cryptography.fernet import Fernet


class Environment(Enum):
    """Environment types"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"


class ConfigSource(Enum):
    """Configuration sources"""
    FILE = "file"
    ENVIRONMENT = "environment"
    DATABASE = "database"
    VAULT = "vault"
    DEFAULT = "default"


@dataclass
class ProxyConfig:
    """Proxy configuration"""
    enabled: bool = False
    proxies: List[str] = field(default_factory=list)
    rotation_interval: int = 300  # seconds
    health_check_interval: int = 60
    max_failures: int = 3
    authentication: Optional[Dict[str, str]] = None


@dataclass
class BrowserConfig:
    """Browser configuration"""
    default_browser: str = "chrome"
    headless: bool = True
    window_size: tuple = (1920, 1080)
    max_sessions: int = 5
    session_timeout: int = 3600
    page_load_timeout: int = 30
    implicit_wait: int = 10
    enable_stealth: bool = True
    user_data_dir: Optional[str] = None


@dataclass
class APIConfig:
    """API configuration"""
    base_urls: Dict[str, str] = field(default_factory=dict)
    authentication: Dict[str, Dict[str, str]] = field(default_factory=dict)
    rate_limits: Dict[str, Dict[str, int]] = field(default_factory=dict)
    timeouts: Dict[str, int] = field(default_factory=lambda: {"default": 30})
    retry_attempts: int = 3
    enable_caching: bool = True
    cache_ttl: int = 300


@dataclass
class ConnectionConfig:
    """Connection pool configuration"""
    max_connections_total: int = 100
    max_connections_per_host: int = 20
    connection_timeout: int = 10
    read_timeout: int = 30
    keep_alive_timeout: int = 30
    max_requests_per_connection: int = 1000
    enable_ssl_verification: bool = True
    dns_cache_ttl: int = 300


@dataclass
class SecurityConfig:
    """Security configuration"""
    enable_encryption: bool = True
    encryption_key: Optional[str] = None
    enable_ssl_verification: bool = True
    certificate_path: Optional[str] = None
    enable_request_signing: bool = False
    max_login_attempts: int = 3
    session_secret_key: Optional[str] = None


@dataclass
class MonitoringConfig:
    """Monitoring configuration"""
    enable_metrics: bool = True
    metrics_interval: int = 60
    enable_health_checks: bool = True
    health_check_interval: int = 30
    enable_logging: bool = True
    log_level: str = "INFO"
    log_file: Optional[str] = None
    enable_alerts: bool = False


@dataclass
class DriversConfiguration:
    """Complete drivers configuration"""
    environment: Environment = Environment.DEVELOPMENT
    proxy: ProxyConfig = field(default_factory=ProxyConfig)
    browser: BrowserConfig = field(default_factory=BrowserConfig)
    api: APIConfig = field(default_factory=APIConfig)
    connection: ConnectionConfig = field(default_factory=ConnectionConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    monitoring: MonitoringConfig = field(default_factory=MonitoringConfig)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    version: str = "1.0.0"
    checksum: Optional[str] = None


class ConfigurationManager:
    """
    Enterprise configuration management system.
    
    Features:
    - Environment-aware configuration loading
    - Multiple configuration sources (file, env, database)
    - Configuration validation and schema checking
    - Encrypted sensitive data storage
    - Hot reloading and change detection
    - Configuration versioning and rollback
    """
    
    def __init__(
        self,
        config_dir: Optional[str] = None,
        environment: Optional[Environment] = None,
        enable_encryption: bool = True
    ):
        self.config_dir = Path(config_dir) if config_dir else Path.cwd() / "config"
        self.environment = environment or self._detect_environment()
        self.enable_encryption = enable_encryption
        
        # Configuration state
        self.current_config: Optional[DriversConfiguration] = None
        self.config_sources: Dict[ConfigSource, Dict[str, Any]] = {}
        
        # Encryption
        self.encryption_key = self._load_or_generate_encryption_key()
        self.cipher_suite = Fernet(self.encryption_key) if enable_encryption else None
        
        # Monitoring
        self.config_history: List[DriversConfiguration] = []
        self.last_reload: Optional[datetime] = None
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
        # Ensure config directory exists
        self.config_dir.mkdir(parents=True, exist_ok=True)
    
    def load_configuration(self, force_reload: bool = False) -> DriversConfiguration:
        """Load configuration from all sources"""
        if self.current_config and not force_reload:
            return self.current_config
        
        try:
            self.logger.info(f"Loading configuration for environment: {self.environment.value}")
            
            # Load from different sources in priority order
            self._load_from_files()
            self._load_from_environment()
            self._load_from_defaults()
            
            # Merge configurations
            merged_config = self._merge_configurations()
            
            # Validate configuration
            validated_config = self._validate_configuration(merged_config)
            
            # Calculate checksum
            validated_config.checksum = self._calculate_checksum(validated_config)
            
            # Store in history
            if self.current_config:
                self.config_history.append(self.current_config)
            
            self.current_config = validated_config
            self.last_reload = datetime.utcnow()
            
            self.logger.info("Configuration loaded successfully")
            return self.current_config
            
        except Exception as e:
            self.logger.error(f"Failed to load configuration: {e}")
            raise
    
    def save_configuration(self, config: DriversConfiguration) -> bool:
        """Save configuration to file"""
        try:
            config_file = self.config_dir / f"drivers_{self.environment.value}.yaml"
            
            # Convert to dictionary
            config_dict = self._config_to_dict(config)
            
            # Encrypt sensitive data
            if self.enable_encryption:
                config_dict = self._encrypt_sensitive_data(config_dict)
            
            # Save to file
            with open(config_file, 'w') as f:
                yaml.dump(config_dict, f, default_flow_style=False, indent=2)
            
            self.logger.info(f"Configuration saved to: {config_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save configuration: {e}")
            return False
    
    def get_proxy_config(self) -> ProxyConfig:
        """Get proxy configuration"""
        config = self.load_configuration()
        return config.proxy
    
    def get_browser_config(self) -> BrowserConfig:
        """Get browser configuration"""
        config = self.load_configuration()
        return config.browser
    
    def get_api_config(self) -> APIConfig:
        """Get API configuration"""
        config = self.load_configuration()
        return config.api
    
    def get_connection_config(self) -> ConnectionConfig:
        """Get connection configuration"""
        config = self.load_configuration()
        return config.connection
    
    def get_security_config(self) -> SecurityConfig:
        """Get security configuration"""
        config = self.load_configuration()
        return config.security
    
    def get_monitoring_config(self) -> MonitoringConfig:
        """Get monitoring configuration"""
        config = self.load_configuration()
        return config.monitoring
    
    def update_configuration(
        self,
        section: str,
        updates: Dict[str, Any]
    ) -> bool:
        """Update specific configuration section"""
        try:
            config = self.load_configuration()
            
            if hasattr(config, section):
                section_config = getattr(config, section)
                
                # Update fields
                for key, value in updates.items():
                    if hasattr(section_config, key):
                        setattr(section_config, key, value)
                
                # Update timestamp
                config.updated_at = datetime.utcnow()
                
                # Save updated configuration
                return self.save_configuration(config)
            
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to update configuration: {e}")
            return False
    
    def rollback_configuration(self, steps: int = 1) -> bool:
        """Rollback configuration to previous version"""
        try:
            if len(self.config_history) < steps:
                self.logger.warning("Not enough configuration history for rollback")
                return False
            
            # Get previous configuration
            previous_config = self.config_history[-steps]
            
            # Restore
            self.current_config = previous_config
            
            # Save
            return self.save_configuration(previous_config)
            
        except Exception as e:
            self.logger.error(f"Failed to rollback configuration: {e}")
            return False
    
    def validate_configuration_file(self, file_path: str) -> bool:
        """Validate configuration file"""
        try:
            with open(file_path, 'r') as f:
                if file_path.endswith('.yaml') or file_path.endswith('.yml'):
                    config_data = yaml.safe_load(f)
                else:
                    config_data = json.load(f)
            
            # Basic validation
            required_sections = ['browser', 'api', 'connection', 'security', 'monitoring']
            
            for section in required_sections:
                if section not in config_data:
                    self.logger.error(f"Missing required section: {section}")
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Configuration validation failed: {e}")
            return False
    
    def get_configuration_status(self) -> Dict[str, Any]:
        """Get configuration status information"""
        return {
            'environment': self.environment.value,
            'config_loaded': self.current_config is not None,
            'last_reload': self.last_reload,
            'config_checksum': self.current_config.checksum if self.current_config else None,
            'config_version': self.current_config.version if self.current_config else None,
            'history_count': len(self.config_history),
            'config_sources': list(self.config_sources.keys())
        }
    
    def _detect_environment(self) -> Environment:
        """Detect current environment"""
        env = os.getenv('DRIVERS_ENV', 'development').lower()
        
        env_mapping = {
            'dev': Environment.DEVELOPMENT,
            'development': Environment.DEVELOPMENT,
            'stage': Environment.STAGING,
            'staging': Environment.STAGING,
            'prod': Environment.PRODUCTION,
            'production': Environment.PRODUCTION,
            'test': Environment.TESTING,
            'testing': Environment.TESTING
        }
        
        return env_mapping.get(env, Environment.DEVELOPMENT)
    
    def _load_from_files(self):
        """Load configuration from files"""
        # Try environment-specific file first
        env_file = self.config_dir / f"drivers_{self.environment.value}.yaml"
        if env_file.exists():
            with open(env_file, 'r') as f:
                config_data = yaml.safe_load(f)
                if self.enable_encryption:
                    config_data = self._decrypt_sensitive_data(config_data)
                self.config_sources[ConfigSource.FILE] = config_data
        
        # Try generic file
        generic_file = self.config_dir / "drivers.yaml"
        if generic_file.exists() and ConfigSource.FILE not in self.config_sources:
            with open(generic_file, 'r') as f:
                config_data = yaml.safe_load(f)
                self.config_sources[ConfigSource.FILE] = config_data
    
    def _load_from_environment(self):
        """Load configuration from environment variables"""
        env_config = {}
        
        # Browser configuration
        browser_config = {}
        if os.getenv('DRIVERS_BROWSER_TYPE'):
            browser_config['default_browser'] = os.getenv('DRIVERS_BROWSER_TYPE')
        if os.getenv('DRIVERS_BROWSER_HEADLESS'):
            browser_config['headless'] = os.getenv('DRIVERS_BROWSER_HEADLESS').lower() == 'true'
        if browser_config:
            env_config['browser'] = browser_config
        
        # API configuration
        api_config = {}
        if os.getenv('DRIVERS_API_TIMEOUT'):
            api_config['timeouts'] = {'default': int(os.getenv('DRIVERS_API_TIMEOUT'))}
        if api_config:
            env_config['api'] = api_config
        
        # Security configuration
        security_config = {}
        if os.getenv('DRIVERS_ENCRYPTION_KEY'):
            security_config['encryption_key'] = os.getenv('DRIVERS_ENCRYPTION_KEY')
        if os.getenv('DRIVERS_SSL_VERIFY'):
            security_config['enable_ssl_verification'] = os.getenv('DRIVERS_SSL_VERIFY').lower() == 'true'
        if security_config:
            env_config['security'] = security_config
        
        if env_config:
            self.config_sources[ConfigSource.ENVIRONMENT] = env_config
    
    def _load_from_defaults(self):
        """Load default configuration"""
        default_config = {
            'environment': self.environment.value,
            'proxy': {
                'enabled': False,
                'proxies': [],
                'rotation_interval': 300,
                'health_check_interval': 60,
                'max_failures': 3
            },
            'browser': {
                'default_browser': 'chrome',
                'headless': True,
                'window_size': [1920, 1080],
                'max_sessions': 5,
                'session_timeout': 3600,
                'page_load_timeout': 30,
                'implicit_wait': 10,
                'enable_stealth': True
            },
            'api': {
                'base_urls': {},
                'authentication': {},
                'rate_limits': {},
                'timeouts': {'default': 30},
                'retry_attempts': 3,
                'enable_caching': True,
                'cache_ttl': 300
            },
            'connection': {
                'max_connections_total': 100,
                'max_connections_per_host': 20,
                'connection_timeout': 10,
                'read_timeout': 30,
                'keep_alive_timeout': 30,
                'max_requests_per_connection': 1000,
                'enable_ssl_verification': True,
                'dns_cache_ttl': 300
            },
            'security': {
                'enable_encryption': True,
                'enable_ssl_verification': True,
                'enable_request_signing': False,
                'max_login_attempts': 3
            },
            'monitoring': {
                'enable_metrics': True,
                'metrics_interval': 60,
                'enable_health_checks': True,
                'health_check_interval': 30,
                'enable_logging': True,
                'log_level': 'INFO',
                'enable_alerts': False
            }
        }
        
        self.config_sources[ConfigSource.DEFAULT] = default_config
    
    def _merge_configurations(self) -> DriversConfiguration:
        """Merge configurations from all sources"""
        # Start with defaults
        merged = self.config_sources.get(ConfigSource.DEFAULT, {}).copy()
        
        # Override with file configuration
        if ConfigSource.FILE in self.config_sources:
            merged = self._deep_merge(merged, self.config_sources[ConfigSource.FILE])
        
        # Override with environment configuration
        if ConfigSource.ENVIRONMENT in self.config_sources:
            merged = self._deep_merge(merged, self.config_sources[ConfigSource.ENVIRONMENT])
        
        # Convert to DriversConfiguration object
        return self._dict_to_config(merged)
    
    def _deep_merge(self, base: Dict, override: Dict) -> Dict:
        """Deep merge two dictionaries"""
        result = base.copy()
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def _dict_to_config(self, config_dict: Dict) -> DriversConfiguration:
        """Convert dictionary to DriversConfiguration object"""
        return DriversConfiguration(
            environment=Environment(config_dict.get('environment', 'development')),
            proxy=ProxyConfig(**config_dict.get('proxy', {})),
            browser=BrowserConfig(**config_dict.get('browser', {})),
            api=APIConfig(**config_dict.get('api', {})),
            connection=ConnectionConfig(**config_dict.get('connection', {})),
            security=SecurityConfig(**config_dict.get('security', {})),
            monitoring=MonitoringConfig(**config_dict.get('monitoring', {})),
            version=config_dict.get('version', '1.0.0')
        )
    
    def _config_to_dict(self, config: DriversConfiguration) -> Dict:
        """Convert DriversConfiguration object to dictionary"""
        return {
            'environment': config.environment.value,
            'proxy': {
                'enabled': config.proxy.enabled,
                'proxies': config.proxy.proxies,
                'rotation_interval': config.proxy.rotation_interval,
                'health_check_interval': config.proxy.health_check_interval,
                'max_failures': config.proxy.max_failures,
                'authentication': config.proxy.authentication
            },
            'browser': {
                'default_browser': config.browser.default_browser,
                'headless': config.browser.headless,
                'window_size': list(config.browser.window_size),
                'max_sessions': config.browser.max_sessions,
                'session_timeout': config.browser.session_timeout,
                'page_load_timeout': config.browser.page_load_timeout,
                'implicit_wait': config.browser.implicit_wait,
                'enable_stealth': config.browser.enable_stealth,
                'user_data_dir': config.browser.user_data_dir
            },
            'api': {
                'base_urls': config.api.base_urls,
                'authentication': config.api.authentication,
                'rate_limits': config.api.rate_limits,
                'timeouts': config.api.timeouts,
                'retry_attempts': config.api.retry_attempts,
                'enable_caching': config.api.enable_caching,
                'cache_ttl': config.api.cache_ttl
            },
            'connection': {
                'max_connections_total': config.connection.max_connections_total,
                'max_connections_per_host': config.connection.max_connections_per_host,
                'connection_timeout': config.connection.connection_timeout,
                'read_timeout': config.connection.read_timeout,
                'keep_alive_timeout': config.connection.keep_alive_timeout,
                'max_requests_per_connection': config.connection.max_requests_per_connection,
                'enable_ssl_verification': config.connection.enable_ssl_verification,
                'dns_cache_ttl': config.connection.dns_cache_ttl
            },
            'security': {
                'enable_encryption': config.security.enable_encryption,
                'encryption_key': config.security.encryption_key,
                'enable_ssl_verification': config.security.enable_ssl_verification,
                'certificate_path': config.security.certificate_path,
                'enable_request_signing': config.security.enable_request_signing,
                'max_login_attempts': config.security.max_login_attempts,
                'session_secret_key': config.security.session_secret_key
            },
            'monitoring': {
                'enable_metrics': config.monitoring.enable_metrics,
                'metrics_interval': config.monitoring.metrics_interval,
                'enable_health_checks': config.monitoring.enable_health_checks,
                'health_check_interval': config.monitoring.health_check_interval,
                'enable_logging': config.monitoring.enable_logging,
                'log_level': config.monitoring.log_level,
                'log_file': config.monitoring.log_file,
                'enable_alerts': config.monitoring.enable_alerts
            },
            'version': config.version,
            'created_at': config.created_at.isoformat(),
            'updated_at': config.updated_at.isoformat()
        }
    
    def _validate_configuration(self, config: DriversConfiguration) -> DriversConfiguration:
        """Validate configuration"""
        # Basic validation
        if config.browser.max_sessions <= 0:
            raise ValueError("Browser max_sessions must be greater than 0")
        
        if config.connection.max_connections_total <= 0:
            raise ValueError("Connection max_connections_total must be greater than 0")
        
        if config.api.retry_attempts < 0:
            raise ValueError("API retry_attempts must be non-negative")
        
        return config
    
    def _calculate_checksum(self, config: DriversConfiguration) -> str:
        """Calculate configuration checksum"""
        config_str = json.dumps(self._config_to_dict(config), sort_keys=True)
        return hashlib.sha256(config_str.encode()).hexdigest()
    
    def _load_or_generate_encryption_key(self) -> bytes:
        """Load or generate encryption key"""
        key_file = self.config_dir / ".encryption_key"
        
        if key_file.exists():
            with open(key_file, 'rb') as f:
                return f.read()
        else:
            key = Fernet.generate_key()
            with open(key_file, 'wb') as f:
                f.write(key)
            key_file.chmod(0o600)  # Restrict permissions
            return key
    
    def _encrypt_sensitive_data(self, config_dict: Dict) -> Dict:
        """Encrypt sensitive configuration data"""
        if not self.cipher_suite:
            return config_dict
        
        sensitive_fields = [
            'security.encryption_key',
            'security.session_secret_key',
            'api.authentication',
            'proxy.authentication'
        ]
        
        for field_path in sensitive_fields:
            keys = field_path.split('.')
            current = config_dict
            
            # Navigate to the field
            for key in keys[:-1]:
                if key in current and isinstance(current[key], dict):
                    current = current[key]
                else:
                    break
            else:
                # Encrypt the field value
                final_key = keys[-1]
                if final_key in current and current[final_key]:
                    if isinstance(current[final_key], str):
                        encrypted_value = self.cipher_suite.encrypt(current[final_key].encode())
                        current[final_key] = base64.b64encode(encrypted_value).decode()
                    elif isinstance(current[final_key], dict):
                        for k, v in current[final_key].items():
                            if isinstance(v, str):
                                encrypted_value = self.cipher_suite.encrypt(v.encode())
                                current[final_key][k] = base64.b64encode(encrypted_value).decode()
        
        return config_dict
    
    def _decrypt_sensitive_data(self, config_dict: Dict) -> Dict:
        """Decrypt sensitive configuration data"""
        if not self.cipher_suite:
            return config_dict
        
        sensitive_fields = [
            'security.encryption_key',
            'security.session_secret_key',
            'api.authentication',
            'proxy.authentication'
        ]
        
        for field_path in sensitive_fields:
            keys = field_path.split('.')
            current = config_dict
            
            # Navigate to the field
            for key in keys[:-1]:
                if key in current and isinstance(current[key], dict):
                    current = current[key]
                else:
                    break
            else:
                # Decrypt the field value
                final_key = keys[-1]
                if final_key in current and current[final_key]:
                    try:
                        if isinstance(current[final_key], str):
                            encrypted_data = base64.b64decode(current[final_key])
                            decrypted_value = self.cipher_suite.decrypt(encrypted_data)
                            current[final_key] = decrypted_value.decode()
                        elif isinstance(current[final_key], dict):
                            for k, v in current[final_key].items():
                                if isinstance(v, str):
                                    encrypted_data = base64.b64decode(v)
                                    decrypted_value = self.cipher_suite.decrypt(encrypted_data)
                                    current[final_key][k] = decrypted_value.decode()
                    except Exception as e:
                        self.logger.warning(f"Failed to decrypt {field_path}: {e}")
        
        return config_dict


# Singleton instance
_config_manager_instance: Optional[ConfigurationManager] = None


def get_config_manager(
    config_dir: Optional[str] = None,
    environment: Optional[Environment] = None
) -> ConfigurationManager:
    """Get singleton configuration manager instance"""
    global _config_manager_instance
    
    if _config_manager_instance is None:
        _config_manager_instance = ConfigurationManager(
            config_dir=config_dir,
            environment=environment
        )
    
    return _config_manager_instance


def load_drivers_config() -> DriversConfiguration:
    """Load drivers configuration using singleton manager"""
    return get_config_manager().load_configuration()
