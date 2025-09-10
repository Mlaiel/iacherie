"""
Ainflue Core Infrastructure - Configuration Manager Core
========================================================

Enterprise-grade configuration management system with multi-environment support,
encrypted secrets management, hot-reload capabilities, and validation schemas.
Provides centralized configuration for all Ainflue core components.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import json
import logging
import os
import yaml
from typing import Dict, List, Optional, Any, Union, Type, Callable
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import hashlib
import base64
from datetime import datetime
import threading
import time

# Third-party imports (with fallbacks)
try:
    from pydantic import BaseModel, ValidationError, validator
    PYDANTIC_AVAILABLE = True
except ImportError:
    PYDANTIC_AVAILABLE = False

try:
    from cryptography.fernet import Fernet
    CRYPTOGRAPHY_AVAILABLE = True
except ImportError:
    CRYPTOGRAPHY_AVAILABLE = False

logger = logging.getLogger(__name__)

class ConfigLevel(str, Enum):
    """Configuration complexity levels"""
    BASIC = "basic"
    STANDARD = "standard" 
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"

class ConfigEnvironment(str, Enum):
    """Configuration environments"""
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"

class ConfigSource(str, Enum):
    """Configuration data sources"""
    FILE = "file"
    ENVIRONMENT = "environment"
    DATABASE = "database"
    VAULT = "vault"
    CONSUL = "consul"
    ETCD = "etcd"

@dataclass
class ConfigChange:
    """Configuration change tracking"""
    key: str
    old_value: Any
    new_value: Any
    timestamp: datetime
    source: str
    user: Optional[str] = None

@dataclass
class ConfigMetrics:
    """Configuration system metrics"""
    total_configs: int = 0
    encrypted_configs: int = 0
    hot_reloads: int = 0
    validation_errors: int = 0
    last_reload: Optional[datetime] = None
    config_sources: Dict[str, int] = field(default_factory=dict)

class ConfigSchema:
    """Configuration validation schema"""
    
    def __init__(self):
        self.validators: Dict[str, Callable] = {}
        self.required_keys: List[str] = []
        self.optional_keys: List[str] = []
        self.type_hints: Dict[str, Type] = {}

    def add_validator(self, key: str, validator: Callable[[Any], bool]):
        """Add custom validator for configuration key"""
        self.validators[key] = validator

    def validate(self, config: Dict[str, Any]) -> List[str]:
        """Validate configuration against schema"""
        errors = []
        
        # Check required keys
        for key in self.required_keys:
            if key not in config:
                errors.append(f"Required configuration key missing: {key}")
        
        # Validate types and values
        for key, value in config.items():
            if key in self.type_hints:
                expected_type = self.type_hints[key]
                if not isinstance(value, expected_type):
                    errors.append(f"Configuration key '{key}' should be {expected_type.__name__}, got {type(value).__name__}")
            
            if key in self.validators:
                try:
                    if not self.validators[key](value):
                        errors.append(f"Validation failed for configuration key: {key}")
                except Exception as e:
                    errors.append(f"Validator error for key '{key}': {str(e)}")
        
        return errors

class ConfigurationManagerCore:
    """Enterprise configuration management system"""
    
    def __init__(self, level: str = "enterprise"):
        """Initialize configuration manager"""
        self.level = ConfigLevel.ENTERPRISE if level == "enterprise" else ConfigLevel.STANDARD
        self.environment = ConfigEnvironment.PRODUCTION
        self.config_data: Dict[str, Any] = {}
        self.encrypted_keys: set = set()
        self.change_history: List[ConfigChange] = []
        self.metrics = ConfigMetrics()
        self.schemas: Dict[str, ConfigSchema] = {}
        self.watchers: List[Callable] = []
        self.encryption_key: Optional[bytes] = None
        self.cipher_suite = None
        
        # File watching
        self._file_mtimes: Dict[str, float] = {}
        self._watch_thread: Optional[threading.Thread] = None
        self._stop_watching = threading.Event()
        
        # Configuration paths
        self.config_paths = [
            "/etc/ainflue/config",
            os.path.expanduser("~/.ainflue"),
            os.path.join(os.getcwd(), "config"),
            os.path.join(os.getcwd(), "core", "config")
        ]
        
        # Default configuration
        self._setup_default_config()
        
        # Initialize encryption
        self._initialize_encryption()
        
        # Load configurations
        self._load_configurations()
        
        # Start file watching
        if self.level == ConfigLevel.ENTERPRISE:
            self._start_file_watching()
        
        logger.info(f"⚙️ Configuration Manager Core initialized - Level: {self.level}")

    def _setup_default_config(self):
        """Setup default configuration values"""
        self.config_data = {
            # Core system configuration
            "core": {
                "service_name": "ainflue-core",
                "service_version": "1.0.0",
                "environment": self.environment.value,
                "debug": False,
                "log_level": "INFO"
            },
            
            # Database configuration
            "database": {
                "host": "localhost",
                "port": 5432,
                "database": "ainflue",
                "username": "ainflue_user",
                "password": "",  # To be encrypted
                "pool_size": 10,
                "max_overflow": 20,
                "ssl_mode": "prefer"
            },
            
            # Cache configuration
            "cache": {
                "type": "redis",
                "host": "localhost",
                "port": 6379,
                "database": 0,
                "password": "",  # To be encrypted
                "max_connections": 100,
                "ttl_seconds": 3600
            },
            
            # Security configuration
            "security": {
                "jwt_secret": "",  # To be encrypted
                "jwt_expiry_hours": 24,
                "bcrypt_rounds": 12,
                "rate_limit_requests": 1000,
                "rate_limit_window": 3600,
                "cors_origins": ["*"],
                "allowed_hosts": ["*"]
            },
            
            # AI configuration
            "ai": {
                "model_path": "/var/lib/ainflue/models",
                "max_batch_size": 32,
                "inference_timeout": 30,
                "gpu_enabled": True,
                "model_cache_size": "2GB"
            },
            
            # Payment configuration
            "payments": {
                "stripe_api_key": "",  # To be encrypted
                "paypal_client_id": "",  # To be encrypted
                "paypal_client_secret": "",  # To be encrypted
                "webhook_secret": "",  # To be encrypted
                "default_currency": "USD"
            },
            
            # Platform configuration
            "platform": {
                "api_version": "v1",
                "max_upload_size": "100MB",
                "allowed_file_types": [".jpg", ".png", ".mp4", ".mp3", ".pdf"],
                "cdn_base_url": "https://cdn.ainflue.com",
                "websocket_timeout": 300
            }
        }

    def _initialize_encryption(self):
        """Initialize encryption for sensitive configuration values"""
        if not CRYPTOGRAPHY_AVAILABLE:
            logger.warning("Cryptography not available, sensitive configs will not be encrypted")
            return
        
        try:
            # Try to load existing key
            key_file = os.path.join(self.config_paths[0], ".config_key")
            if os.path.exists(key_file):
                with open(key_file, 'rb') as f:
                    self.encryption_key = f.read()
            else:
                # Generate new key
                self.encryption_key = Fernet.generate_key()
                
                # Save key securely
                os.makedirs(os.path.dirname(key_file), exist_ok=True)
                with open(key_file, 'wb') as f:
                    f.write(self.encryption_key)
                os.chmod(key_file, 0o600)  # Restrict access
            
            self.cipher_suite = Fernet(self.encryption_key)
            logger.info("🔒 Configuration encryption initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize encryption: {str(e)}")

    def _load_configurations(self):
        """Load configurations from all sources"""
        # Load from files
        self._load_from_files()
        
        # Load from environment variables
        self._load_from_environment()
        
        # Validate configuration
        self._validate_configuration()
        
        # Update metrics
        self._update_metrics()

    def _load_from_files(self):
        """Load configuration from files"""
        for config_path in self.config_paths:
            if not os.path.exists(config_path):
                continue
            
            # Load YAML files
            for yaml_file in Path(config_path).glob("*.yaml"):
                self._load_yaml_file(yaml_file)
            
            # Load JSON files
            for json_file in Path(config_path).glob("*.json"):
                self._load_json_file(json_file)
            
            # Load environment-specific files
            env_file = Path(config_path) / f"{self.environment.value}.yaml"
            if env_file.exists():
                self._load_yaml_file(env_file)

    def _load_yaml_file(self, file_path: Path):
        """Load configuration from YAML file"""
        try:
            with open(file_path, 'r') as f:
                data = yaml.safe_load(f)
                if data:
                    self._merge_config(data, str(file_path))
                    self._file_mtimes[str(file_path)] = os.path.getmtime(file_path)
                    logger.info(f"📄 Loaded configuration from {file_path}")
        except Exception as e:
            logger.error(f"Failed to load YAML file {file_path}: {str(e)}")

    def _load_json_file(self, file_path: Path):
        """Load configuration from JSON file"""
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                if data:
                    self._merge_config(data, str(file_path))
                    self._file_mtimes[str(file_path)] = os.path.getmtime(file_path)
                    logger.info(f"📄 Loaded configuration from {file_path}")
        except Exception as e:
            logger.error(f"Failed to load JSON file {file_path}: {str(e)}")

    def _load_from_environment(self):
        """Load configuration from environment variables"""
        env_prefix = "AINFLUE_"
        
        for key, value in os.environ.items():
            if key.startswith(env_prefix):
                config_key = key[len(env_prefix):].lower().replace('_', '.')
                
                # Convert string values to appropriate types
                converted_value = self._convert_env_value(value)
                
                # Set nested configuration
                self._set_nested_config(config_key, converted_value)
                
                self.metrics.config_sources["environment"] = self.metrics.config_sources.get("environment", 0) + 1

    def _convert_env_value(self, value: str) -> Any:
        """Convert environment variable string to appropriate type"""
        # Boolean conversion
        if value.lower() in ('true', 'false'):
            return value.lower() == 'true'
        
        # Integer conversion
        if value.isdigit():
            return int(value)
        
        # Float conversion
        try:
            return float(value)
        except ValueError:
            pass
        
        # JSON conversion
        if value.startswith(('{', '[')):
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                pass
        
        return value

    def _merge_config(self, new_config: Dict[str, Any], source: str):
        """Merge new configuration with existing"""
        def merge_dict(base: Dict, update: Dict):
            for key, value in update.items():
                if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                    merge_dict(base[key], value)
                else:
                    old_value = base.get(key)
                    base[key] = value
                    
                    # Track change
                    if old_value != value:
                        self.change_history.append(ConfigChange(
                            key=key,
                            old_value=old_value,
                            new_value=value,
                            timestamp=datetime.utcnow(),
                            source=source
                        ))
        
        merge_dict(self.config_data, new_config)
        self.metrics.config_sources[source] = self.metrics.config_sources.get(source, 0) + 1

    def _set_nested_config(self, key_path: str, value: Any):
        """Set nested configuration value using dot notation"""
        keys = key_path.split('.')
        current = self.config_data
        
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        old_value = current.get(keys[-1])
        current[keys[-1]] = value
        
        if old_value != value:
            self.change_history.append(ConfigChange(
                key=key_path,
                old_value=old_value,
                new_value=value,
                timestamp=datetime.utcnow(),
                source="environment"
            ))

    def _validate_configuration(self):
        """Validate loaded configuration"""
        errors = []
        
        for schema_name, schema in self.schemas.items():
            config_section = self.get(schema_name, {})
            section_errors = schema.validate(config_section)
            errors.extend([f"{schema_name}.{error}" for error in section_errors])
        
        if errors:
            self.metrics.validation_errors += len(errors)
            logger.warning(f"Configuration validation errors: {errors}")

    def _start_file_watching(self):
        """Start watching configuration files for changes"""
        if self._watch_thread and self._watch_thread.is_alive():
            return
        
        self._watch_thread = threading.Thread(target=self._watch_files, daemon=True)
        self._watch_thread.start()
        logger.info("👁️ Started configuration file watching")

    def _watch_files(self):
        """Watch configuration files for changes"""
        while not self._stop_watching.is_set():
            try:
                for file_path, last_mtime in self._file_mtimes.items():
                    if os.path.exists(file_path):
                        current_mtime = os.path.getmtime(file_path)
                        if current_mtime > last_mtime:
                            logger.info(f"🔄 Configuration file changed: {file_path}")
                            self._reload_file(file_path)
                            self._file_mtimes[file_path] = current_mtime
                            self.metrics.hot_reloads += 1
                            
                            # Notify watchers
                            self._notify_watchers(f"file_changed:{file_path}")
                
                time.sleep(5)  # Check every 5 seconds
                
            except Exception as e:
                logger.error(f"File watching error: {str(e)}")
                time.sleep(10)

    def _reload_file(self, file_path: str):
        """Reload specific configuration file"""
        try:
            if file_path.endswith('.yaml'):
                self._load_yaml_file(Path(file_path))
            elif file_path.endswith('.json'):
                self._load_json_file(Path(file_path))
            
            self._validate_configuration()
            self.metrics.last_reload = datetime.utcnow()
            
        except Exception as e:
            logger.error(f"Failed to reload file {file_path}: {str(e)}")

    def _notify_watchers(self, event: str):
        """Notify configuration change watchers"""
        for watcher in self.watchers:
            try:
                watcher(event, self.config_data)
            except Exception as e:
                logger.error(f"Watcher notification error: {str(e)}")

    def _update_metrics(self):
        """Update configuration metrics"""
        self.metrics.total_configs = self._count_nested_keys(self.config_data)
        self.metrics.encrypted_configs = len(self.encrypted_keys)

    def _count_nested_keys(self, data: Dict[str, Any]) -> int:
        """Count total number of configuration keys (including nested)"""
        count = 0
        for key, value in data.items():
            count += 1
            if isinstance(value, dict):
                count += self._count_nested_keys(value)
        return count

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key (supports dot notation)"""
        keys = key.split('.')
        current = self.config_data
        
        try:
            for k in keys:
                current = current[k]
            
            # Decrypt if encrypted
            if key in self.encrypted_keys and self.cipher_suite:
                try:
                    if isinstance(current, str):
                        decrypted = self.cipher_suite.decrypt(base64.b64decode(current))
                        return decrypted.decode('utf-8')
                except Exception as e:
                    logger.error(f"Failed to decrypt config {key}: {str(e)}")
                    return default
            
            return current
            
        except (KeyError, TypeError):
            return default

    def set(self, key: str, value: Any, encrypt: bool = False, source: str = "manual"):
        """Set configuration value"""
        keys = key.split('.')
        current = self.config_data
        
        # Navigate to parent
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]
        
        # Encrypt if requested
        if encrypt and self.cipher_suite:
            try:
                encrypted_value = base64.b64encode(
                    self.cipher_suite.encrypt(str(value).encode('utf-8'))
                ).decode('utf-8')
                value = encrypted_value
                self.encrypted_keys.add(key)
            except Exception as e:
                logger.error(f"Failed to encrypt config {key}: {str(e)}")
        
        # Set value
        old_value = current.get(keys[-1])
        current[keys[-1]] = value
        
        # Track change
        self.change_history.append(ConfigChange(
            key=key,
            old_value=old_value,
            new_value=value,
            timestamp=datetime.utcnow(),
            source=source
        ))
        
        # Notify watchers
        self._notify_watchers(f"config_changed:{key}")

    def delete(self, key: str):
        """Delete configuration key"""
        keys = key.split('.')
        current = self.config_data
        
        try:
            # Navigate to parent
            for k in keys[:-1]:
                current = current[k]
            
            # Delete key
            old_value = current.pop(keys[-1], None)
            self.encrypted_keys.discard(key)
            
            # Track change
            self.change_history.append(ConfigChange(
                key=key,
                old_value=old_value,
                new_value=None,
                timestamp=datetime.utcnow(),
                source="manual"
            ))
            
        except (KeyError, TypeError):
            pass

    def get_section(self, section: str) -> Dict[str, Any]:
        """Get entire configuration section"""
        return self.get(section, {})

    def add_schema(self, name: str, schema: ConfigSchema):
        """Add validation schema for configuration section"""
        self.schemas[name] = schema

    def add_watcher(self, callback: Callable[[str, Dict[str, Any]], None]):
        """Add configuration change watcher"""
        self.watchers.append(callback)

    def reload(self):
        """Manually reload all configurations"""
        logger.info("🔄 Manually reloading configurations")
        self._load_configurations()
        self.metrics.hot_reloads += 1
        self.metrics.last_reload = datetime.utcnow()
        self._notify_watchers("manual_reload")

    def export_config(self, format: str = "yaml") -> str:
        """Export current configuration"""
        if format == "yaml":
            return yaml.dump(self.config_data, default_flow_style=False)
        elif format == "json":
            return json.dumps(self.config_data, indent=2)
        else:
            return str(self.config_data)

    def get_metrics(self) -> ConfigMetrics:
        """Get configuration system metrics"""
        self._update_metrics()
        return self.metrics

    def get_change_history(self, limit: int = 100) -> List[ConfigChange]:
        """Get recent configuration changes"""
        return sorted(self.change_history, key=lambda x: x.timestamp, reverse=True)[:limit]

    async def health_check(self) -> bool:
        """Health check for configuration system"""
        try:
            # Test basic operations
            test_key = "health_check.test"
            test_value = f"test_{time.time()}"
            
            self.set(test_key, test_value)
            retrieved = self.get(test_key)
            self.delete(test_key)
            
            return retrieved == test_value
            
        except Exception as e:
            logger.error(f"Configuration health check failed: {str(e)}")
            return False

    def stop_watching(self):
        """Stop file watching"""
        self._stop_watching.set()
        if self._watch_thread and self._watch_thread.is_alive():
            self._watch_thread.join(timeout=5)

    def __del__(self):
        """Cleanup on destruction"""
        try:
            self.stop_watching()
        except Exception:
            pass

# Module exports
__all__ = [
    "ConfigurationManagerCore", "ConfigLevel", "ConfigEnvironment", 
    "ConfigSource", "ConfigChange", "ConfigMetrics", "ConfigSchema"
]

logger.info("⚙️ Configuration Manager Core module loaded")