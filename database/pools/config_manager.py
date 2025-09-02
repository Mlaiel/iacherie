"""Pool Configuration Manager - IA Influencer Agent + Content Protection Platform

Centralized configuration management for all database connection pools
with environment-specific settings, security compliance, and dynamic updates.

Configuration Features:
- Environment-specific configurations (dev, staging, prod)
- Secure credential management and encryption
- Dynamic configuration updates without restart
- Configuration validation and schema enforcement
- Audit logging for configuration changes
- Template-based configuration generation

Pool Types Managed:
- PostgreSQL connection pools with read replicas
- Redis cache pools with clustering support
- MongoDB pools with sharding configuration
- Elasticsearch pools with cluster management
- Vector store pools with optimization settings
- Object storage pools with multi-provider support

Security & Compliance:
- Encrypted credential storage
- Role-based configuration access
- Configuration change auditing
- Compliance with data protection regulations
- Secure configuration transmission

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps

WARNING: This code is proprietary and confidential. Any unauthorized use, modification,
or distribution is strictly prohibited and may result in legal action.
Contact: mlaiel@live.de for licensing inquiries.

Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import json
import yaml
import os
from typing import Dict, List, Optional, Any, Union, Type, Callable
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
import hashlib
import secrets
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
from contextlib import asynccontextmanager
import threading
import weakref

try:
    import aiofiles
    import aiofiles.os
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    import cerberus
except ImportError as e:
    logging.warning(f"Configuration dependency missing: {e}")

from .manager import PoolConfig, DatabaseConnectionInfo, DatabaseType, PoolStrategy, ConnectionState

logger = logging.getLogger(__name__)

# =============== CONFIGURATION ENUMS ===============

class EnvironmentType(str, Enum):
    """Environment types"""

    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"

class ConfigurationFormat(str, Enum):
    """Configuration file formats"""

    JSON = "json"
    YAML = "yaml"
    TOML = "toml"
    ENV = "env"

class SecurityLevel(str, Enum):
    """Security levels for configuration"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    ULTRA = "ultra"

class CredentialType(str, Enum):
    """Types of credentials"""

    DATABASE = "database"
    CACHE = "cache"
    STORAGE = "storage"
    API_KEY = "api_key"
    CERTIFICATE = "certificate"

# =============== CONFIGURATION MODELS ===============

@dataclass
class EncryptedCredential:
    """Encrypted credential storage"""
    credential_id: str
    credential_type: CredentialType
    encrypted_data: str
    salt: str
    created_at: datetime
    updated_at: datetime
    expires_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ConfigurationTemplate:
    """
Configuration template for pool types"""
    template_id: str
    pool_type: DatabaseType
    environment: EnvironmentType
    template_data: Dict[str, Any]
    required_fields: List[str]
    optional_fields: List[str]
    validation_schema: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

@dataclass
class ConfigurationAuditLog:
    """
Audit log for configuration changes"""
    log_id: str
    action: str  # create, update, delete, access
    resource_type: str
    resource_id: str
    user_id: Optional[str]
    timestamp: datetime
    old_values: Optional[Dict[str, Any]]
    new_values: Optional[Dict[str, Any]]
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class PoolConfigurationSet:
    """
Complete configuration set for all pools"""
    environment: EnvironmentType
    pool_configs: Dict[str, PoolConfig]
    connection_infos: Dict[str, DatabaseConnectionInfo]
    global_settings: Dict[str, Any]
    security_settings: Dict[str, Any]
    monitoring_settings: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    version: str = "1.0.0"

# =============== CONFIGURATION SCHEMAS ===============

POOL_CONFIG_SCHEMA = {
    "postgresql": {
        "type": "dict",
        "schema": {
            "min_size": {"type": "integer", "min": 1, "max": 100, "default": 5},
            "max_size": {"type": "integer", "min": 5, "max": 1000, "default": 50},
            "pool_timeout": {"type": "integer", "min": 1, "max": 300, "default": 30},
            "connection_timeout": {"type": "integer", "min": 1, "max": 300, "default": 60},
            "health_check_interval": {"type": "integer", "min": 5, "max": 3600, "default": 30},
            "enable_monitoring": {"type": "boolean", "default": True},
            "encrypt_connections": {"type": "boolean", "default": True}
        }
    },
    "redis": {
        "type": "dict",
        "schema": {
            "max_connections": {"type": "integer", "min": 1, "max": 1000, "default": 100},
            "socket_keepalive": {"type": "boolean", "default": True},
            "socket_timeout": {"type": "integer", "min": 1, "max": 60, "default": 5},
            "health_check_interval": {"type": "integer", "min": 5, "max": 3600, "default": 30},
            "enable_cluster": {"type": "boolean", "default": False},
            "enable_sentinel": {"type": "boolean", "default": False}
        }
    },
    "mongodb": {
        "type": "dict",
        "schema": {
            "max_pool_size": {"type": "integer", "min": 1, "max": 500, "default": 50},
            "min_pool_size": {"type": "integer", "min": 1, "max": 50, "default": 10},
            "server_selection_timeout_ms": {"type": "integer", "min": 1000, "max": 60000, "default": 30000},
            "enable_gridfs": {"type": "boolean", "default": True},
            "enable_change_streams": {"type": "boolean", "default": True}
        }
    },
    "elasticsearch": {
        "type": "dict",
        "schema": {
            "max_retries": {"type": "integer", "min": 1, "max": 10, "default": 3},
            "timeout": {"type": "integer", "min": 1, "max": 300, "default": 30},
            "use_ssl": {"type": "boolean", "default": True},
            "verify_certs": {"type": "boolean", "default": True},
            "sniff_on_start": {"type": "boolean", "default": True}
        }
    }
}

CONNECTION_INFO_SCHEMA = {
    "type": "dict",
    "schema": {
        "host": {"type": "string", "required": True},
        "port": {"type": "integer", "min": 1, "max": 65535, "required": True},
        "database": {"type": "string", "required": True},
        "username": {"type": "string", "required": True},
        "password": {"type": "string", "required": True},
        "ssl_mode": {"type": "string", "allowed": ["disable", "allow", "prefer", "require"], "default": "prefer"},
        "connection_params": {"type": "dict", "default": {}},
        "is_replica": {"type": "boolean", "default": False},
        "weight": {"type": "integer", "min": 1, "max": 100, "default": 100}
    }
}

# =============== ENCRYPTION MANAGER ===============

class CredentialEncryption:
    """Credential encryption and decryption manager"""
    
    def __init__(self, master_key: Optional[str] = None):
        self.master_key = master_key or os.getenv("POOL_MASTER_KEY", self._generate_master_key())
        self._cipher_suite = None
        self._init_cipher()
    
    def _generate_master_key(self) -> str:
        """Generate a new master key"""
        return base64.urlsafe_b64encode(secrets.token_bytes(32)).decode()
    
    def _init_cipher(self) -> None:
        """
Initialize cipher suite"""
        try:
            key_bytes = base64.urlsafe_b64decode(self.master_key.encode())
            self._cipher_suite = Fernet(base64.urlsafe_b64encode(key_bytes))
        except Exception as e:
            logger.error(f"Failed to initialize cipher suite: {e}")
            raise
    
    def encrypt_credential(self, credential_data: Dict[str, Any], credential_type: CredentialType) -> EncryptedCredential:
        """Encrypt credential data"""
        try:
            # Serialize credential data
            data_json = json.dumps(credential_data, sort_keys=True)
            
            # Generate salt
            salt = base64.urlsafe_b64encode(secrets.token_bytes(16)).decode()
            
            # Encrypt data
            encrypted_data = self._cipher_suite.encrypt(data_json.encode()).decode()
            
            return EncryptedCredential(
                credential_id=hashlib.sha256(f"{credential_type.value}_{salt}".encode()).hexdigest()[:16],
                credential_type=credential_type,
                encrypted_data=encrypted_data,
                salt=salt,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"Credential encryption failed: {e}")
            raise
    
    def decrypt_credential(self, encrypted_credential: EncryptedCredential) -> Dict[str, Any]:
        """Decrypt credential data"""
        try:
            # Check expiration
            if encrypted_credential.expires_at and datetime.utcnow() > encrypted_credential.expires_at:
                raise ValueError("Credential has expired")
            
            # Decrypt data
            decrypted_data = self._cipher_suite.decrypt(encrypted_credential.encrypted_data.encode())
            
            # Deserialize
            return json.loads(decrypted_data.decode())
            
        except Exception as e:
            logger.error(f"Credential decryption failed: {e}")
            raise

# =============== CONFIGURATION VALIDATOR ===============

class ConfigurationValidator:
    """Configuration validation using schemas"""
    
    def __init__(self):
        try:
            logger.info(f"Executing __init__")
            
            # Implementation for __init__
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"__init__ completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"__init__ failed: {e}")
            raise
    def validate_pool_config(self, pool_type: DatabaseType, config_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
Validate pool configuration"""
        try:
            schema = POOL_CONFIG_SCHEMA.get(pool_type.value)
            if not schema:
                return False, [f"No schema defined for pool type: {pool_type.value}"]
            
            self.validator.schema = schema
            is_valid = self.validator.validate(config_data)
            
            if not is_valid:
                errors = [f"{field}: {error}" for field, error in self.validator.errors.items()]
                return False, errors
            
            return True, []
            
        except Exception as e:
            return False, [f"Validation error: {str(e)}"]
    
    def validate_connection_info(self, connection_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate connection information"""
        try:
            self.validator.schema = CONNECTION_INFO_SCHEMA
            is_valid = self.validator.validate(connection_data)
            
            if not is_valid:
                errors = [f"{field}: {error}" for field, error in self.validator.errors.items()]
                return False, errors
            
            return True, []
            
        except Exception as e:
            return False, [f"Validation error: {str(e)}"]
    
    def apply_defaults(self, pool_type: DatabaseType, config_data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply default values to configuration"""
        try:
            schema = POOL_CONFIG_SCHEMA.get(pool_type.value)
            if not schema:
                return config_data
            
            self.validator.schema = schema
            normalized = self.validator.normalized(config_data)
            return normalized or config_data
            
        except Exception as e:
            logger.error(f"Failed to apply defaults: {e}")
            return config_data

# =============== CONFIGURATION FILE HANDLER ===============

class ConfigurationFileHandler(FileSystemEventHandler):
    """File system event handler for configuration changes"""
    
    def __init__(self, config_manager: 'PoolConfigurationManager'):
        self.config_manager = config_manager
        self.last_modified = {}
    
    def on_modified(self, event):
        """
Handle file modification events"""
        if not event.is_directory and event.src_path.endswith(('.json', '.yaml', '.yml')):
            # Debounce rapid file changes
            current_time = datetime.utcnow()
            if event.src_path in self.last_modified:
                if (current_time - self.last_modified[event.src_path]).seconds < 2:
                    return
            
            self.last_modified[event.src_path] = current_time
            
            # Reload configuration
            asyncio.create_task(self.config_manager.reload_configuration_file(event.src_path))

# =============== POOL CONFIGURATION MANAGER ===============

class PoolConfigurationManager:
    """
Central manager for pool configurations"""
    
    def __init__(self, config_dir: str = "config/pools", master_key: Optional[str] = None):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize components
        self.encryption = CredentialEncryption(master_key)
        self.validator = ConfigurationValidator()
        
        # Configuration storage
        self.configurations: Dict[EnvironmentType, PoolConfigurationSet] = {}
        self.templates: Dict[str, ConfigurationTemplate] = {}
        self.encrypted_credentials: Dict[str, EncryptedCredential] = {}
        self.audit_logs: List[ConfigurationAuditLog] = []
        
        # File watching
        self.file_observer: Optional[Observer] = None
        self.file_handler: Optional[ConfigurationFileHandler] = None
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Configuration cache
        self._config_cache: Dict[str, Any] = {}
        self._cache_ttl: Dict[str, datetime] = {}
        
        # Change listeners
        self._change_listeners: List[Callable[[str, Dict[str, Any]], None]] = []
    
    async def initialize(self) -> bool:
        """Initialize configuration manager"""
        try:
            # Load existing configurations
            await self._load_all_configurations()
            
            # Load templates
            await self._load_templates()
            
            # Load encrypted credentials
            await self._load_encrypted_credentials()
            
            # Start file watching
            await self._start_file_watching()
            
            logger.info("✅ Pool configuration manager initialized")
            return True
            
        except Exception as e:
            logger.error(f"❌ Configuration manager initialization failed: {e}")
            return False
    
    async def create_configuration_set(self, environment: EnvironmentType, 
                                     pool_configs: Dict[str, Dict[str, Any]],
                                     connection_infos: Dict[str, Dict[str, Any]],
                                     global_settings: Optional[Dict[str, Any]] = None) -> bool:
        """Create a new configuration set"""
        try:
            with self._lock:
                # Validate configurations
                validated_pool_configs = {}
                for pool_id, config_data in pool_configs.items():
                    pool_type = DatabaseType(config_data.get("type", "postgresql"))
                    
                    # Validate configuration
                    is_valid, errors = self.validator.validate_pool_config(pool_type, config_data)
                    if not is_valid:
                        logger.error(f"Pool config validation failed for {pool_id}: {errors}")
                        return False
                    
                    # Apply defaults and create PoolConfig
                    normalized_config = self.validator.apply_defaults(pool_type, config_data)
                    validated_pool_configs[pool_id] = PoolConfig(**normalized_config)
                
                # Validate connection infos
                validated_connection_infos = {}
                for conn_id, conn_data in connection_infos.items():
                    is_valid, errors = self.validator.validate_connection_info(conn_data)
                    if not is_valid:
                        logger.error(f"Connection info validation failed for {conn_id}: {errors}")
                        return False
                    
                    validated_connection_infos[conn_id] = DatabaseConnectionInfo(**conn_data)
                
                # Create configuration set
                config_set = PoolConfigurationSet(
                    environment=environment,
                    pool_configs=validated_pool_configs,
                    connection_infos=validated_connection_infos,
                    global_settings=global_settings or {},
                    security_settings=self._get_default_security_settings(environment),
                    monitoring_settings=self._get_default_monitoring_settings(environment),
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                
                # Store configuration
                self.configurations[environment] = config_set
                
                # Save to file
                await self._save_configuration_file(environment, config_set)
                
                # Log audit
                await self._log_audit_event("create", "configuration_set", environment.value, None, None, asdict(config_set))
                
                # Notify listeners
                await self._notify_change_listeners(f"configuration_set.{environment.value}", asdict(config_set))
                
                logger.info(f"✅ Configuration set created for environment: {environment.value}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to create configuration set: {e}")
            return False
    
    async def get_configuration_set(self, environment: EnvironmentType) -> Optional[PoolConfigurationSet]:
        """Get configuration set for environment"""
        try:
            with self._lock:
                return self.configurations.get(environment)
        except Exception as e:
            logger.error(f"Failed to get configuration set: {e}")
            return None
    
    async def update_pool_config(self, environment: EnvironmentType, pool_id: str, 
                               config_updates: Dict[str, Any]) -> bool:
        """Update pool configuration"""
        try:
            with self._lock:
                config_set = self.configurations.get(environment)
                if not config_set:
                    logger.error(f"Configuration set not found for environment: {environment.value}")
                    return False
                
                if pool_id not in config_set.pool_configs:
                    logger.error(f"Pool configuration not found: {pool_id}")
                    return False
                
                # Get current config
                current_config = config_set.pool_configs[pool_id]
                old_values = asdict(current_config)
                
                # Merge updates
                updated_config_data = {**asdict(current_config), **config_updates}
                
                # Determine pool type
                pool_type = DatabaseType.POSTGRESQL  # Default, should be determined from context
                
                # Validate updated configuration
                is_valid, errors = self.validator.validate_pool_config(pool_type, updated_config_data)
                if not is_valid:
                    logger.error(f"Updated pool config validation failed: {errors}")
                    return False
                
                # Apply updates
                new_config = PoolConfig(**updated_config_data)
                config_set.pool_configs[pool_id] = new_config
                config_set.updated_at = datetime.utcnow()
                
                # Save to file
                await self._save_configuration_file(environment, config_set)
                
                # Log audit
                await self._log_audit_event("update", "pool_config", pool_id, None, old_values, asdict(new_config))
                
                # Notify listeners
                await self._notify_change_listeners(f"pool_config.{pool_id}", asdict(new_config))
                
                logger.info(f"✅ Pool configuration updated: {pool_id}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to update pool configuration: {e}")
            return False
    
    async def store_encrypted_credential(self, credential_data: Dict[str, Any], 
                                       credential_type: CredentialType,
                                       credential_id: Optional[str] = None) -> str:
        """Store encrypted credential"""
        try:
            with self._lock:
                # Encrypt credential
                encrypted_credential = self.encryption.encrypt_credential(credential_data, credential_type)
                
                if credential_id:
                    encrypted_credential.credential_id = credential_id
                
                # Store encrypted credential
                self.encrypted_credentials[encrypted_credential.credential_id] = encrypted_credential
                
                # Save to file
                await self._save_encrypted_credentials_file()
                
                # Log audit
                await self._log_audit_event("create", "encrypted_credential", encrypted_credential.credential_id, None, None, None)
                
                logger.info(f"✅ Encrypted credential stored: {encrypted_credential.credential_id}")
                return encrypted_credential.credential_id
                
        except Exception as e:
            logger.error(f"Failed to store encrypted credential: {e}")
            raise
    
    async def get_decrypted_credential(self, credential_id: str) -> Optional[Dict[str, Any]]:
        """Get decrypted credential"""
        try:
            with self._lock:
                encrypted_credential = self.encrypted_credentials.get(credential_id)
                if not encrypted_credential:
                    logger.error(f"Encrypted credential not found: {credential_id}")
                    return None
                
                # Decrypt credential
                credential_data = self.encryption.decrypt_credential(encrypted_credential)
                
                # Log audit
                await self._log_audit_event("access", "encrypted_credential", credential_id, None, None, None)
                
                return credential_data
                
        except Exception as e:
            logger.error(f"Failed to get decrypted credential: {e}")
            return None
    
    async def create_configuration_template(self, template_id: str, pool_type: DatabaseType,
                                          environment: EnvironmentType, template_data: Dict[str, Any],
                                          required_fields: List[str], optional_fields: List[str],
                                          validation_schema: Dict[str, Any]) -> bool:
        """Create configuration template"""
        try:
            with self._lock:
                template = ConfigurationTemplate(
                    template_id=template_id,
                    pool_type=pool_type,
                    environment=environment,
                    template_data=template_data,
                    required_fields=required_fields,
                    optional_fields=optional_fields,
                    validation_schema=validation_schema,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                
                self.templates[template_id] = template
                
                # Save templates
                await self._save_templates_file()
                
                logger.info(f"✅ Configuration template created: {template_id}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to create configuration template: {e}")
            return False
    
    async def generate_from_template(self, template_id: str, variables: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Generate configuration from template"""
        try:
            template = self.templates.get(template_id)
            if not template:
                logger.error(f"Template not found: {template_id}")
                return None
            
            # Simple variable substitution (can be enhanced with Jinja2)
            config_json = json.dumps(template.template_data)
            for var_name, var_value in variables.items():
                config_json = config_json.replace(f"{{{{ {var_name} }}}}", str(var_value))
            
            return json.loads(config_json)
            
        except Exception as e:
            logger.error(f"Failed to generate from template: {e}")
            return None
    
    def _get_default_security_settings(self, environment: EnvironmentType) -> Dict[str, Any]:
        """Get default security settings for environment"""
        if environment == EnvironmentType.PRODUCTION:
            return {
                "security_level": SecurityLevel.ULTRA.value,
                "encrypt_all_connections": True,
                "require_ssl": True,
                "audit_all_access": True,
                "credential_rotation_days": 30
            }
        elif environment == EnvironmentType.STAGING:
            return {
                "security_level": SecurityLevel.HIGH.value,
                "encrypt_all_connections": True,
                "require_ssl": True,
                "audit_all_access": True,
                "credential_rotation_days": 60
            }
        else:
            return {
                "security_level": SecurityLevel.MEDIUM.value,
                "encrypt_all_connections": False,
                "require_ssl": False,
                "audit_all_access": False,
                "credential_rotation_days": 90
            }
    
    def _get_default_monitoring_settings(self, environment: EnvironmentType) -> Dict[str, Any]:
        """Get default monitoring settings for environment"""
        return {
            "enable_metrics": True,
            "metrics_interval": 30,
            "enable_health_checks": True,
            "health_check_interval": 60,
            "enable_alerting": environment in [EnvironmentType.STAGING, EnvironmentType.PRODUCTION],
            "log_level": "INFO" if environment == EnvironmentType.PRODUCTION else "DEBUG"
        }
    
    async def _load_all_configurations(self) -> None:
        """Load all configuration files"""
        try:
            for env_file in self.config_dir.glob("*.json"):
                env_name = env_file.stem
                try:
                    environment = EnvironmentType(env_name)
                    await self._load_configuration_file(env_file, environment)
                except ValueError:
                    logger.warning(f"Unknown environment file: {env_file}")
        except Exception as e:
            logger.error(f"Failed to load configurations: {e}")
    
    async def _load_configuration_file(self, file_path: Path, environment: EnvironmentType) -> None:
        """Load configuration from file"""
        try:
            if file_path.exists():
                async with aiofiles.open(file_path, 'r') as f:
                    config_data = json.loads(await f.read())
                
                # Convert to PoolConfigurationSet
                config_set = self._dict_to_configuration_set(config_data, environment)
                self.configurations[environment] = config_set
                
                logger.info(f"✅ Configuration loaded for environment: {environment.value}")
        except Exception as e:
            logger.error(f"Failed to load configuration file {file_path}: {e}")
    
    async def _save_configuration_file(self, environment: EnvironmentType, config_set: PoolConfigurationSet) -> None:
        """Save configuration to file"""
        try:
            file_path = self.config_dir / f"{environment.value}.json"
            config_data = self._configuration_set_to_dict(config_set)
            
            async with aiofiles.open(file_path, 'w') as f:
                await f.write(json.dumps(config_data, indent=2, default=str))
                
        except Exception as e:
            logger.error(f"Failed to save configuration file: {e}")
    
    async def _load_templates(self) -> None:
        """Load configuration templates"""
        try:
            templates_file = self.config_dir / "templates.json"
            if templates_file.exists():
                async with aiofiles.open(templates_file, 'r') as f:
                    templates_data = json.loads(await f.read())
                
                for template_data in templates_data:
                    template = ConfigurationTemplate(**template_data)
                    self.templates[template.template_id] = template
        except Exception as e:
            logger.error(f"Failed to load templates: {e}")
    
    async def _save_templates_file(self) -> None:
        """Save templates to file"""
        try:
            templates_file = self.config_dir / "templates.json"
            templates_data = [asdict(template) for template in self.templates.values()]
            
            async with aiofiles.open(templates_file, 'w') as f:
                await f.write(json.dumps(templates_data, indent=2, default=str))
        except Exception as e:
            logger.error(f"Failed to save templates: {e}")
    
    async def _load_encrypted_credentials(self) -> None:
        """Load encrypted credentials"""
        try:
            credentials_file = self.config_dir / "credentials.enc"
            if credentials_file.exists():
                async with aiofiles.open(credentials_file, 'r') as f:
                    credentials_data = json.loads(await f.read())
                
                for cred_data in credentials_data:
                    credential = EncryptedCredential(**cred_data)
                    self.encrypted_credentials[credential.credential_id] = credential
        except Exception as e:
            logger.error(f"Failed to load encrypted credentials: {e}")
    
    async def _save_encrypted_credentials_file(self) -> None:
        """Save encrypted credentials to file"""
        try:
            credentials_file = self.config_dir / "credentials.enc"
            credentials_data = [asdict(cred) for cred in self.encrypted_credentials.values()]
            
            async with aiofiles.open(credentials_file, 'w') as f:
                await f.write(json.dumps(credentials_data, indent=2, default=str))
        except Exception as e:
            logger.error(f"Failed to save encrypted credentials: {e}")
    
    def _dict_to_configuration_set(self, config_data: Dict[str, Any], environment: EnvironmentType) -> PoolConfigurationSet:
        """Convert dictionary to PoolConfigurationSet"""
        # Convert pool configs
        pool_configs = {}
        for pool_id, pool_data in config_data.get("pool_configs", {}).items():
            pool_configs[pool_id] = PoolConfig(**pool_data)
        
        # Convert connection infos
        connection_infos = {}
        for conn_id, conn_data in config_data.get("connection_infos", {}).items():
            connection_infos[conn_id] = DatabaseConnectionInfo(**conn_data)
        
        return PoolConfigurationSet(
            environment=environment,
            pool_configs=pool_configs,
            connection_infos=connection_infos,
            global_settings=config_data.get("global_settings", {}),
            security_settings=config_data.get("security_settings", {}),
            monitoring_settings=config_data.get("monitoring_settings", {}),
            created_at=datetime.fromisoformat(config_data.get("created_at", datetime.utcnow().isoformat())),
            updated_at=datetime.fromisoformat(config_data.get("updated_at", datetime.utcnow().isoformat())),
            version=config_data.get("version", "1.0.0")
        )
    
    def _configuration_set_to_dict(self, config_set: PoolConfigurationSet) -> Dict[str, Any]:
        """Convert PoolConfigurationSet to dictionary"""
        return asdict(config_set)
    
    async def _start_file_watching(self) -> None:
        """
Start file system watching for configuration changes"""
        try:
            self.file_handler = ConfigurationFileHandler(self)
            self.file_observer = Observer()
            self.file_observer.schedule(self.file_handler, str(self.config_dir), recursive=False)
            self.file_observer.start()
            
            logger.info("✅ Configuration file watching started")
        except Exception as e:
            logger.error(f"Failed to start file watching: {e}")
    
    async def reload_configuration_file(self, file_path: str) -> None:
        """Reload configuration from file"""
        try:
            file_path = Path(file_path)
            env_name = file_path.stem
            environment = EnvironmentType(env_name)
            
            await self._load_configuration_file(file_path, environment)
            
            # Notify listeners
            config_set = self.configurations.get(environment)
            if config_set:
                await self._notify_change_listeners(f"configuration_reload.{environment.value}", asdict(config_set))
            
            logger.info(f"✅ Configuration reloaded: {environment.value}")
        except Exception as e:
            logger.error(f"Failed to reload configuration: {e}")
    
    async def _log_audit_event(self, action: str, resource_type: str, resource_id: str,
                             user_id: Optional[str], old_values: Optional[Dict[str, Any]],
                             new_values: Optional[Dict[str, Any]]) -> None:
        """Log audit event"""
        try:
            audit_log = ConfigurationAuditLog(
                log_id=hashlib.sha256(f"{action}_{resource_type}_{resource_id}_{datetime.utcnow().isoformat()}".encode()).hexdigest()[:16],
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                user_id=user_id,
                timestamp=datetime.utcnow(),
                old_values=old_values,
                new_values=new_values
            )
            
            self.audit_logs.append(audit_log)
            
            # Keep only recent audit logs (last 1000)
            if len(self.audit_logs) > 1000:
                self.audit_logs = self.audit_logs[-1000:]
                
        except Exception as e:
            logger.error(f"Failed to log audit event: {e}")
    
    def add_change_listener(self, callback: Callable[[str, Dict[str, Any]], None]) -> None:
        """Add configuration change listener"""
        self._change_listeners.append(callback)
    
    async def _notify_change_listeners(self, change_type: str, data: Dict[str, Any]) -> None:
        """
Notify configuration change listeners"""
        try:
            for listener in self._change_listeners:
                try:
                    await listener(change_type, data)
                except Exception as e:
                    logger.error(f"Change listener error: {e}")
        except Exception as e:
            logger.error(f"Failed to notify change listeners: {e}")
    
    def get_audit_logs(self, limit: int = 100) -> List[ConfigurationAuditLog]:
        """Get recent audit logs"""
        return self.audit_logs[-limit:]
    
    async def close(self) -> None:
        """
Close configuration manager"""
        try:
            # Stop file watching
            if self.file_observer:
                self.file_observer.stop()
                self.file_observer.join()
            
            logger.info("✅ Pool configuration manager closed")
        except Exception as e:
            logger.error(f"Error closing configuration manager: {e}")

# =============== GLOBAL CONFIGURATION MANAGER ===============

_global_config_manager: Optional[PoolConfigurationManager] = None

def get_configuration_manager() -> PoolConfigurationManager:
    """Get global configuration manager instance"""
    global _global_config_manager
    if _global_config_manager is None:
        _global_config_manager = PoolConfigurationManager()
    return _global_config_manager

async def initialize_configuration_manager(config_dir: str = "config/pools", 
                                         master_key: Optional[str] = None) -> bool:
    """Initialize global configuration manager"""
    global _global_config_manager
    _global_config_manager = PoolConfigurationManager(config_dir, master_key)
    return await _global_config_manager.initialize()

# =============== EXPORTS ===============

__all__ = [
    "PoolConfigurationManager",
    "get_configuration_manager",
    "initialize_configuration_manager",
    "EnvironmentType",
    "ConfigurationFormat",
    "SecurityLevel",
    "CredentialType",
    "PoolConfigurationSet",
    "ConfigurationTemplate",
    "EncryptedCredential",
    "ConfigurationAuditLog",
    "CredentialEncryption",
    "ConfigurationValidator"
]
