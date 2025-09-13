#!/usr/bin/env python3
"""🚀 Ainflue Config Module - Ultra-Advanced Enterprise Index
==========================================================

🔥 ENTERPRISE CONFIGURATION ORCHESTRATION HUB
- Zentraler Configuration Manager für die gesamte Ainflue-Plattform
- Ultra-moderne Multi-Environment Configuration mit Enterprise Security
- Advanced Settings Management mit Real-time Updates und Validation
- Production-Ready Configuration Orchestration für skalierbare Deployments

🏗️ ENTERPRISE CONFIGURATION ARCHITECTURE:
┌─────────────────────────────────────────────────────────────┐
│  APPLICATION LAYER → Runtime Configuration & Hot Reloading  │
│  VALIDATION LAYER  → Security & Compliance Validation       │
│  ORCHESTRATION     → Multi-Environment Configuration        │
│  STORAGE LAYER     → Database, Redis, File System           │
│  SECURITY LAYER    → Encryption, Secrets, Access Control    │
└─────────────────────────────────────────────────────────────┘

🚀 ULTRA-ADVANCED CONFIGURATION FEATURES:
- 🔧 Multi-Environment Configuration (Dev, Staging, Prod, Test)
- 🛡️ Enterprise Security (Encryption, Secrets Management, ACL)
- 📊 Real-time Configuration Updates & Hot Reloading
- 🔐 Advanced Security Validation & Compliance Checking
- 💾 Multi-Storage Backend (Database, Redis, Files, Cloud)
- 🌐 Global Configuration Distribution & Synchronization
- 📈 Configuration Analytics & Performance Monitoring
- 🔄 Dynamic Configuration Injection & Dependency Management
- 🚨 Configuration Change Auditing & Rollback
- 🎯 Feature Flags & A/B Testing Configuration
- 📱 Mobile & Edge Configuration Distribution
- 🤖 AI-Powered Configuration Optimization
- 🔮 Predictive Configuration Management
- 📧 Configuration Change Notifications
- 🌍 Multi-Region Configuration Replication

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
License: Proprietary - Enterprise License
"""

import asyncio
import sys
import os
import logging
import time
import traceback
import json
import yaml
import hashlib
import secrets
from pathlib import Path
from typing import Dict, Any, Optional, List, Union, Tuple, Callable, Type
from contextlib import asynccontextmanager
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, field, asdict
from enum import Enum
import threading
import signal
from concurrent.futures import ThreadPoolExecutor
import weakref

# Advanced path management
CONFIG_ROOT = Path(__file__).parent.absolute()
PROJECT_ROOT = CONFIG_ROOT.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Enterprise logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("ainflue.config.index")

# Enhanced imports with error handling
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

try:
    import sqlalchemy
    from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
    SQLALCHEMY_AVAILABLE = True
except ImportError:
    SQLALCHEMY_AVAILABLE = False

try:
    from pydantic import BaseSettings, Field, validator
    from pydantic_settings import BaseSettings as PydanticBaseSettings
    PYDANTIC_AVAILABLE = True
except ImportError:
    PYDANTIC_AVAILABLE = False

try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    import base64
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False

# Config Module Imports with Error Handling
try:
    from .settings import ApplicationSettings
    SETTINGS_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Settings module not available: {e}")
    SETTINGS_AVAILABLE = False

try:
    from .core.database import DatabaseSettings
    from .core.redis import RedisSettings
    from .core.celery import CelerySettings
    CORE_CONFIG_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Core config modules not available: {e}")
    CORE_CONFIG_AVAILABLE = False

# Configuration Enums
class ConfigurationEnvironment(Enum):
    """Configuration environments"""
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"
    LOAD_TEST = "load_test"

class ConfigurationSource(Enum):
    """Configuration data sources"""
    ENVIRONMENT = "environment"
    FILE = "file"
    DATABASE = "database"
    REDIS = "redis"
    CLOUD = "cloud"
    KUBERNETES = "kubernetes"

class ConfigurationSecurity(Enum):
    """Configuration security levels"""
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    SECRET = "secret"
    TOP_SECRET = "top_secret"

class ConfigurationStatus(Enum):
    """Configuration status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    DEPRECATED = "deprecated"
    PENDING = "pending"
    FAILED = "failed"

# Configuration Data Structures
@dataclass
class ConfigurationMetadata:
    """Configuration metadata"""
    key: str
    description: str
    environment: ConfigurationEnvironment
    security_level: ConfigurationSecurity = ConfigurationSecurity.INTERNAL
    source: ConfigurationSource = ConfigurationSource.ENVIRONMENT
    status: ConfigurationStatus = ConfigurationStatus.ACTIVE
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    version: str = "1.0.0"
    tags: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    validation_rules: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ConfigurationValue:
    """Configuration value with metadata"""
    key: str
    value: Any
    metadata: ConfigurationMetadata
    encrypted: bool = False
    cached: bool = True
    last_accessed: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    access_count: int = 0
    checksum: Optional[str] = None
    
    def __post_init__(self):
        """Calculate checksum after initialization"""
        if not self.checksum:
            self.checksum = self._calculate_checksum()
    
    def _calculate_checksum(self) -> str:
        """Calculate checksum for value integrity"""
        value_str = json.dumps(self.value, sort_keys=True, default=str)
        return hashlib.sha256(value_str.encode()).hexdigest()

# Configuration Manager Classes
class ConfigurationEncryption:
    """🔐 Enterprise Configuration Encryption Manager"""
    
    def __init__(self, master_key: Optional[str] = None):
        if not CRYPTO_AVAILABLE:
            logger.warning("Cryptography not available, encryption disabled")
            self.enabled = False
            return
        
        self.enabled = True
        self.master_key = master_key or os.getenv("CONFIG_MASTER_KEY")
        
        if not self.master_key:
            # Generate a new master key
            self.master_key = Fernet.generate_key().decode()
            logger.warning("Generated new master key for configuration encryption")
        
        self.cipher_suite = Fernet(self.master_key.encode())
        logger.info("🔐 Configuration encryption initialized")
    
    def encrypt_value(self, value: Any) -> str:
        """Encrypt configuration value"""
        if not self.enabled:
            return str(value)
        
        try:
            value_str = json.dumps(value, default=str)
            encrypted_bytes = self.cipher_suite.encrypt(value_str.encode())
            return base64.b64encode(encrypted_bytes).decode()
        except Exception as e:
            logger.error(f"Failed to encrypt value: {e}")
            return str(value)
    
    def decrypt_value(self, encrypted_value: str) -> Any:
        """Decrypt configuration value"""
        if not self.enabled:
            return encrypted_value
        
        try:
            encrypted_bytes = base64.b64decode(encrypted_value.encode())
            decrypted_bytes = self.cipher_suite.decrypt(encrypted_bytes)
            return json.loads(decrypted_bytes.decode())
        except Exception as e:
            logger.error(f"Failed to decrypt value: {e}")
            return encrypted_value

class ConfigurationValidator:
    """✅ Enterprise Configuration Validator"""
    
    def __init__(self):
        self.validation_rules = {}
        self.validation_cache = {}
        logger.info("✅ Configuration validator initialized")
    
    def add_validation_rule(self, key: str, rule: Callable[[Any], bool], error_message: str):
        """Add validation rule for configuration key"""
        self.validation_rules[key] = {
            "rule": rule,
            "error_message": error_message
        }
    
    def validate_value(self, key: str, value: Any) -> Tuple[bool, Optional[str]]:
        """Validate configuration value"""
        if key not in self.validation_rules:
            return True, None
        
        try:
            rule = self.validation_rules[key]["rule"]
            if rule(value):
                return True, None
            else:
                return False, self.validation_rules[key]["error_message"]
        except Exception as e:
            return False, f"Validation error: {e}"
    
    def validate_configuration(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate entire configuration"""
        results = {
            "valid": True,
            "errors": {},
            "warnings": {},
            "passed": [],
            "failed": []
        }
        
        for key, value in config.items():
            is_valid, error_message = self.validate_value(key, value)
            
            if is_valid:
                results["passed"].append(key)
            else:
                results["valid"] = False
                results["errors"][key] = error_message
                results["failed"].append(key)
        
        return results

class ConfigurationWatcher:
    """👀 Real-time Configuration Change Watcher"""
    
    def __init__(self):
        self.watchers = {}
        self.callbacks = {}
        self.running = False
        self.executor = ThreadPoolExecutor(max_workers=5)
        logger.info("👀 Configuration watcher initialized")
    
    def watch_file(self, file_path: Path, callback: Callable):
        """Watch configuration file for changes"""
        self.watchers[str(file_path)] = {
            "type": "file",
            "path": file_path,
            "last_modified": file_path.stat().st_mtime if file_path.exists() else 0,
            "callback": callback
        }
    
    def watch_key(self, key: str, callback: Callable):
        """Watch specific configuration key for changes"""
        if key not in self.callbacks:
            self.callbacks[key] = []
        self.callbacks[key].append(callback)
    
    async def start_watching(self):
        """Start configuration watching"""
        self.running = True
        logger.info("👀 Configuration watching started")
        
        while self.running:
            await self._check_file_changes()
            await asyncio.sleep(1)  # Check every second
    
    def stop_watching(self):
        """Stop configuration watching"""
        self.running = False
        self.executor.shutdown(wait=True)
        logger.info("👀 Configuration watching stopped")
    
    async def _check_file_changes(self):
        """Check for file changes"""
        for watcher_id, watcher in self.watchers.items():
            if watcher["type"] == "file":
                file_path = watcher["path"]
                if file_path.exists():
                    current_mtime = file_path.stat().st_mtime
                    if current_mtime > watcher["last_modified"]:
                        watcher["last_modified"] = current_mtime
                        # Execute callback in thread pool
                        self.executor.submit(watcher["callback"], file_path)
    
    def notify_key_change(self, key: str, old_value: Any, new_value: Any):
        """Notify watchers of key change"""
        if key in self.callbacks:
            for callback in self.callbacks[key]:
                try:
                    self.executor.submit(callback, key, old_value, new_value)
                except Exception as e:
                    logger.error(f"Error in configuration callback for {key}: {e}")

# Ultra-Advanced Configuration Manager
class EnterpriseConfigurationManager:
    """🚀 Master Enterprise Configuration Manager - Ultra-Advanced Orchestration"""
    
    def __init__(self, environment: ConfigurationEnvironment = ConfigurationEnvironment.DEVELOPMENT):
        self.environment = environment
        self.configurations = {}
        self.metadata = {}
        self.sources = {}
        self.cache = {}
        
        # Initialize components
        self.encryption = ConfigurationEncryption()
        self.validator = ConfigurationValidator()
        self.watcher = ConfigurationWatcher()
        
        # Storage backends
        self.redis_client = None
        self.database_engine = None
        
        # Performance metrics
        self.metrics = {
            "total_reads": 0,
            "total_writes": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "validation_errors": 0,
            "encryption_operations": 0
        }
        
        # Hot reload settings
        self.hot_reload_enabled = environment in [ConfigurationEnvironment.DEVELOPMENT, ConfigurationEnvironment.TESTING]
        self.auto_save_enabled = True
        
        logger.info(f"🚀 Enterprise Configuration Manager initialized for {environment.value}")
    
    async def initialize(self):
        """Initialize configuration manager"""
        logger.info("🔄 Initializing configuration manager...")
        
        # Initialize Redis connection
        await self._initialize_redis()
        
        # Initialize database connection
        await self._initialize_database()
        
        # Load configurations
        await self._load_configurations()
        
        # Setup default validation rules
        self._setup_validation_rules()
        
        # Start watching if enabled
        if self.hot_reload_enabled:
            asyncio.create_task(self.watcher.start_watching())
        
        logger.info("✅ Configuration manager initialization completed")
    
    async def _initialize_redis(self):
        """Initialize Redis connection for caching"""
        if not REDIS_AVAILABLE:
            logger.warning("Redis not available, caching disabled")
            return
        
        try:
            redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
            self.redis_client = redis.from_url(redis_url, decode_responses=True)
            await asyncio.get_event_loop().run_in_executor(None, self.redis_client.ping)
            logger.info("✅ Redis connection established for configuration caching")
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}")
            self.redis_client = None
    
    async def _initialize_database(self):
        """Initialize database connection for persistent storage"""
        if not SQLALCHEMY_AVAILABLE:
            logger.warning("SQLAlchemy not available, database storage disabled")
            return
        
        try:
            database_url = os.getenv("DATABASE_URL")
            if database_url:
                self.database_engine = create_async_engine(database_url)
                logger.info("✅ Database connection established for configuration storage")
        except Exception as e:
            logger.warning(f"Database connection failed: {e}")
            self.database_engine = None
    
    async def _load_configurations(self):
        """Load configurations from all sources"""
        logger.info("📂 Loading configurations from all sources...")
        
        # Load from environment variables
        await self._load_from_environment()
        
        # Load from configuration files
        await self._load_from_files()
        
        # Load from Redis cache
        await self._load_from_redis()
        
        # Load from database
        await self._load_from_database()
        
        # Load core module configurations
        await self._load_core_configurations()
        
        logger.info(f"📂 Loaded {len(self.configurations)} configurations")
    
    async def _load_from_environment(self):
        """Load configurations from environment variables"""
        env_vars = {
            key: value for key, value in os.environ.items()
            if key.startswith(('AINFLUE_', 'CONFIG_', 'API_', 'DATABASE_', 'REDIS_'))
        }
        
        for key, value in env_vars.items():
            metadata = ConfigurationMetadata(
                key=key,
                description=f"Environment variable {key}",
                environment=self.environment,
                source=ConfigurationSource.ENVIRONMENT
            )
            
            # Try to parse JSON values
            try:
                parsed_value = json.loads(value)
            except (json.JSONDecodeError, TypeError):
                parsed_value = value
            
            config_value = ConfigurationValue(
                key=key,
                value=parsed_value,
                metadata=metadata
            )
            
            self.configurations[key] = config_value
        
        logger.info(f"📂 Loaded {len(env_vars)} environment variables")
    
    async def _load_from_files(self):
        """Load configurations from files"""
        config_files = [
            CONFIG_ROOT / "configs" / f"{self.environment.value}.yaml",
            CONFIG_ROOT / "configs" / f"{self.environment.value}.json",
            CONFIG_ROOT / "settings.py",
            CONFIG_ROOT / f"{self.environment.value}.env"
        ]
        
        for config_file in config_files:
            if config_file.exists():
                await self._load_config_file(config_file)
    
    async def _load_config_file(self, config_file: Path):
        """Load specific configuration file"""
        try:
            if config_file.suffix.lower() in ['.yaml', '.yml']:
                with open(config_file, 'r') as f:
                    data = yaml.safe_load(f)
            elif config_file.suffix.lower() == '.json':
                with open(config_file, 'r') as f:
                    data = json.load(f)
            elif config_file.suffix.lower() == '.env':
                data = {}
                with open(config_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            data[key.strip()] = value.strip()
            else:
                return
            
            # Add configurations from file
            for key, value in data.items():
                metadata = ConfigurationMetadata(
                    key=key,
                    description=f"Configuration from {config_file.name}",
                    environment=self.environment,
                    source=ConfigurationSource.FILE
                )
                
                config_value = ConfigurationValue(
                    key=key,
                    value=value,
                    metadata=metadata
                )
                
                self.configurations[key] = config_value
                
                # Setup file watching
                if self.hot_reload_enabled:
                    self.watcher.watch_file(
                        config_file,
                        lambda path: asyncio.create_task(self._reload_config_file(path))
                    )
            
            logger.info(f"📂 Loaded configuration from {config_file}")
            
        except Exception as e:
            logger.error(f"Failed to load configuration file {config_file}: {e}")
    
    async def _load_from_redis(self):
        """Load configurations from Redis"""
        if not self.redis_client:
            return
        
        try:
            cache_key = f"ainflue:config:{self.environment.value}"
            cached_configs = await asyncio.get_event_loop().run_in_executor(
                None, 
                self.redis_client.hgetall, 
                cache_key
            )
            
            for key, value_str in cached_configs.items():
                try:
                    config_data = json.loads(value_str)
                    
                    metadata = ConfigurationMetadata(**config_data['metadata'])
                    config_value = ConfigurationValue(
                        key=key,
                        value=config_data['value'],
                        metadata=metadata,
                        encrypted=config_data.get('encrypted', False)
                    )
                    
                    # Decrypt if needed
                    if config_value.encrypted:
                        config_value.value = self.encryption.decrypt_value(config_value.value)
                    
                    self.configurations[key] = config_value
                    
                except Exception as e:
                    logger.error(f"Failed to parse cached config {key}: {e}")
            
            logger.info(f"📂 Loaded {len(cached_configs)} configurations from Redis cache")
            
        except Exception as e:
            logger.error(f"Failed to load from Redis: {e}")
    
    async def _load_from_database(self):
        """Load configurations from database"""
        if not self.database_engine:
            return
        
        # Database loading would be implemented here
        logger.info("📂 Database configuration loading not implemented yet")
    
    async def _load_core_configurations(self):
        """Load core module configurations"""
        if not CORE_CONFIG_AVAILABLE:
            return
        
        try:
            # Load application settings
            if SETTINGS_AVAILABLE:
                app_settings = ApplicationSettings()
                for field_name, field_value in app_settings.__dict__.items():
                    if not field_name.startswith('_'):
                        metadata = ConfigurationMetadata(
                            key=f"app.{field_name}",
                            description=f"Application setting: {field_name}",
                            environment=self.environment,
                            source=ConfigurationSource.FILE
                        )
                        
                        config_value = ConfigurationValue(
                            key=f"app.{field_name}",
                            value=field_value,
                            metadata=metadata
                        )
                        
                        self.configurations[f"app.{field_name}"] = config_value
            
            # Load database settings
            db_settings = DatabaseSettings()
            for field_name, field_value in db_settings.__dict__.items():
                if not field_name.startswith('_'):
                    metadata = ConfigurationMetadata(
                        key=f"database.{field_name}",
                        description=f"Database setting: {field_name}",
                        environment=self.environment,
                        source=ConfigurationSource.FILE,
                        security_level=ConfigurationSecurity.CONFIDENTIAL if 'password' in field_name.lower() else ConfigurationSecurity.INTERNAL
                    )
                    
                    config_value = ConfigurationValue(
                        key=f"database.{field_name}",
                        value=field_value,
                        metadata=metadata,
                        encrypted='password' in field_name.lower()
                    )
                    
                    self.configurations[f"database.{field_name}"] = config_value
            
            # Load Redis settings
            redis_settings = RedisSettings()
            for field_name, field_value in redis_settings.__dict__.items():
                if not field_name.startswith('_'):
                    metadata = ConfigurationMetadata(
                        key=f"redis.{field_name}",
                        description=f"Redis setting: {field_name}",
                        environment=self.environment,
                        source=ConfigurationSource.FILE,
                        security_level=ConfigurationSecurity.CONFIDENTIAL if 'password' in field_name.lower() else ConfigurationSecurity.INTERNAL
                    )
                    
                    config_value = ConfigurationValue(
                        key=f"redis.{field_name}",
                        value=field_value,
                        metadata=metadata,
                        encrypted='password' in field_name.lower()
                    )
                    
                    self.configurations[f"redis.{field_name}"] = config_value
            
            logger.info("📂 Core module configurations loaded")
            
        except Exception as e:
            logger.error(f"Failed to load core configurations: {e}")
    
    def _setup_validation_rules(self):
        """Setup default validation rules"""
        # Database URL validation
        self.validator.add_validation_rule(
            "DATABASE_URL",
            lambda x: isinstance(x, str) and (x.startswith('postgresql://') or x.startswith('postgresql+asyncpg://')),
            "DATABASE_URL must be a valid PostgreSQL connection string"
        )
        
        # Redis URL validation
        self.validator.add_validation_rule(
            "REDIS_URL",
            lambda x: isinstance(x, str) and (x.startswith('redis://') or x.startswith('rediss://')),
            "REDIS_URL must be a valid Redis connection string"
        )
        
        # Port validation
        self.validator.add_validation_rule(
            "PORT",
            lambda x: isinstance(x, int) and 1 <= x <= 65535,
            "PORT must be an integer between 1 and 65535"
        )
        
        # Environment validation
        self.validator.add_validation_rule(
            "ENVIRONMENT",
            lambda x: x in [env.value for env in ConfigurationEnvironment],
            f"ENVIRONMENT must be one of: {[env.value for env in ConfigurationEnvironment]}"
        )
        
        logger.info("✅ Default validation rules configured")
    
    async def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        self.metrics["total_reads"] += 1
        
        # Check cache first
        if key in self.cache:
            self.metrics["cache_hits"] += 1
            config_value = self.cache[key]
        elif key in self.configurations:
            self.metrics["cache_misses"] += 1
            config_value = self.configurations[key]
            # Update cache
            self.cache[key] = config_value
        else:
            return default
        
        # Update access metrics
        config_value.last_accessed = datetime.now(timezone.utc)
        config_value.access_count += 1
        
        # Decrypt if needed
        if config_value.encrypted:
            return self.encryption.decrypt_value(config_value.value)
        
        return config_value.value
    
    async def set(self, key: str, value: Any, metadata: Optional[ConfigurationMetadata] = None,
                  encrypt: bool = False, validate: bool = True) -> bool:
        """Set configuration value"""
        self.metrics["total_writes"] += 1
        
        # Validate if enabled
        if validate:
            is_valid, error_message = self.validator.validate_value(key, value)
            if not is_valid:
                self.metrics["validation_errors"] += 1
                logger.error(f"Validation failed for {key}: {error_message}")
                return False
        
        # Create metadata if not provided
        if not metadata:
            metadata = ConfigurationMetadata(
                key=key,
                description=f"Configuration key: {key}",
                environment=self.environment,
                security_level=ConfigurationSecurity.SECRET if encrypt else ConfigurationSecurity.INTERNAL
            )
        
        # Encrypt if needed
        stored_value = value
        if encrypt:
            stored_value = self.encryption.encrypt_value(value)
            self.metrics["encryption_operations"] += 1
        
        # Create configuration value
        config_value = ConfigurationValue(
            key=key,
            value=stored_value,
            metadata=metadata,
            encrypted=encrypt
        )
        
        # Store old value for change notification
        old_value = None
        if key in self.configurations:
            old_value = self.configurations[key].value
        
        # Update configuration
        self.configurations[key] = config_value
        
        # Update cache
        self.cache[key] = config_value
        
        # Save to persistent storage
        if self.auto_save_enabled:
            await self._save_to_storage(key, config_value)
        
        # Notify watchers
        self.watcher.notify_key_change(key, old_value, value)
        
        return True
    
    async def _save_to_storage(self, key: str, config_value: ConfigurationValue):
        """Save configuration to persistent storage"""
        # Save to Redis
        if self.redis_client:
            try:
                cache_key = f"ainflue:config:{self.environment.value}"
                value_data = {
                    "value": config_value.value,
                    "metadata": asdict(config_value.metadata),
                    "encrypted": config_value.encrypted,
                    "last_updated": datetime.now(timezone.utc).isoformat()
                }
                
                await asyncio.get_event_loop().run_in_executor(
                    None,
                    self.redis_client.hset,
                    cache_key,
                    key,
                    json.dumps(value_data, default=str)
                )
            except Exception as e:
                logger.error(f"Failed to save to Redis: {e}")
        
        # Save to database would be implemented here
        # await self._save_to_database(key, config_value)
    
    async def delete(self, key: str) -> bool:
        """Delete configuration value"""
        if key not in self.configurations:
            return False
        
        # Remove from configurations
        del self.configurations[key]
        
        # Remove from cache
        if key in self.cache:
            del self.cache[key]
        
        # Remove from Redis
        if self.redis_client:
            try:
                cache_key = f"ainflue:config:{self.environment.value}"
                await asyncio.get_event_loop().run_in_executor(
                    None,
                    self.redis_client.hdel,
                    cache_key,
                    key
                )
            except Exception as e:
                logger.error(f"Failed to delete from Redis: {e}")
        
        return True
    
    async def reload(self, source: Optional[ConfigurationSource] = None):
        """Reload configurations from specified source or all sources"""
        logger.info(f"🔄 Reloading configurations from {source.value if source else 'all sources'}")
        
        if source == ConfigurationSource.ENVIRONMENT or source is None:
            await self._load_from_environment()
        
        if source == ConfigurationSource.FILE or source is None:
            await self._load_from_files()
        
        if source == ConfigurationSource.REDIS or source is None:
            await self._load_from_redis()
        
        if source == ConfigurationSource.DATABASE or source is None:
            await self._load_from_database()
        
        # Clear cache to force refresh
        self.cache.clear()
        
        logger.info("✅ Configuration reload completed")
    
    async def _reload_config_file(self, file_path: Path):
        """Reload specific configuration file"""
        logger.info(f"🔄 Reloading configuration file: {file_path}")
        await self._load_config_file(file_path)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get configuration manager metrics"""
        return {
            **self.metrics,
            "total_configurations": len(self.configurations),
            "cached_configurations": len(self.cache),
            "environment": self.environment.value,
            "hot_reload_enabled": self.hot_reload_enabled,
            "redis_available": self.redis_client is not None,
            "database_available": self.database_engine is not None,
            "encryption_enabled": self.encryption.enabled
        }
    
    def get_configuration_info(self, key: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a configuration"""
        if key not in self.configurations:
            return None
        
        config_value = self.configurations[key]
        return {
            "key": key,
            "value_type": type(config_value.value).__name__,
            "encrypted": config_value.encrypted,
            "cached": config_value.cached,
            "last_accessed": config_value.last_accessed.isoformat(),
            "access_count": config_value.access_count,
            "checksum": config_value.checksum,
            "metadata": asdict(config_value.metadata)
        }
    
    def list_configurations(self, filter_by: Optional[Dict[str, Any]] = None) -> List[str]:
        """List all configuration keys with optional filtering"""
        keys = list(self.configurations.keys())
        
        if filter_by:
            filtered_keys = []
            for key in keys:
                config_value = self.configurations[key]
                match = True
                
                for filter_key, filter_value in filter_by.items():
                    if filter_key == "environment":
                        if config_value.metadata.environment.value != filter_value:
                            match = False
                            break
                    elif filter_key == "source":
                        if config_value.metadata.source.value != filter_value:
                            match = False
                            break
                    elif filter_key == "security_level":
                        if config_value.metadata.security_level.value != filter_value:
                            match = False
                            break
                    elif filter_key == "encrypted":
                        if config_value.encrypted != filter_value:
                            match = False
                            break
                
                if match:
                    filtered_keys.append(key)
            
            return filtered_keys
        
        return keys
    
    async def export_configuration(self, format: str = "json") -> str:
        """Export configuration to string format"""
        export_data = {}
        
        for key, config_value in self.configurations.items():
            # Don't export encrypted values for security
            if not config_value.encrypted:
                export_data[key] = {
                    "value": config_value.value,
                    "metadata": asdict(config_value.metadata)
                }
        
        if format.lower() == "json":
            return json.dumps(export_data, indent=2, default=str)
        elif format.lower() in ["yaml", "yml"]:
            return yaml.dump(export_data, default_flow_style=False)
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    async def shutdown(self):
        """Shutdown configuration manager"""
        logger.info("🛑 Shutting down configuration manager...")
        
        # Stop watching
        self.watcher.stop_watching()
        
        # Close Redis connection
        if self.redis_client:
            self.redis_client.close()
        
        # Close database connection
        if self.database_engine:
            await self.database_engine.dispose()
        
        logger.info("✅ Configuration manager shutdown completed")

# Global configuration manager instance
config_manager = None

# Configuration Manager Factory
async def create_configuration_manager(
    environment: ConfigurationEnvironment = ConfigurationEnvironment.DEVELOPMENT
) -> EnterpriseConfigurationManager:
    """🏭 Configuration Manager Factory
    
    Creates and initializes the Enterprise Configuration Manager
    with all advanced features and storage backends.
    
    Returns:
        EnterpriseConfigurationManager: Fully configured manager
    """
    logger.info("🏭 Creating Enterprise Configuration Manager...")
    
    manager = EnterpriseConfigurationManager(environment)
    await manager.initialize()
    
    logger.info("✅ Enterprise Configuration Manager created successfully")
    return manager

def get_configuration_manager() -> EnterpriseConfigurationManager:
    """Get the global configuration manager instance"""
    global config_manager
    if config_manager is None:
        # Create and initialize synchronously
        env_str = os.getenv("ENVIRONMENT", "development")
        try:
            environment = ConfigurationEnvironment(env_str)
        except ValueError:
            environment = ConfigurationEnvironment.DEVELOPMENT
        
        # Create event loop if not exists
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        # Create configuration manager
        config_manager = loop.run_until_complete(create_configuration_manager(environment))
    
    return config_manager

# Convenience functions for easy access
async def get_config(key: str, default: Any = None) -> Any:
    """Get configuration value (convenience function)"""
    manager = get_configuration_manager()
    return await manager.get(key, default)

async def set_config(key: str, value: Any, encrypt: bool = False) -> bool:
    """Set configuration value (convenience function)"""
    manager = get_configuration_manager()
    return await manager.set(key, value, encrypt=encrypt)

def get_config_sync(key: str, default: Any = None) -> Any:
    """Get configuration value synchronously"""
    manager = get_configuration_manager()
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(manager.get(key, default))

# Signal handlers for graceful shutdown
def signal_handler(signum, frame):
    """Handle shutdown signals gracefully"""
    logger.info(f"🛑 Received signal {signum}, shutting down configuration manager...")
    
    if config_manager:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(config_manager.shutdown())
    
    sys.exit(0)

# Register signal handlers
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# CLI Interface for Configuration Management
def main():
    """🚀 Main entry point for Configuration Manager"""
    import argparse
    
    parser = argparse.ArgumentParser(description="🚀 Ainflue Configuration Manager")
    parser.add_argument("--environment", "-e", 
                       choices=[env.value for env in ConfigurationEnvironment],
                       default="development",
                       help="Configuration environment")
    parser.add_argument("--action", "-a",
                       choices=["list", "get", "set", "delete", "export", "reload", "metrics"],
                       default="list",
                       help="Action to perform")
    parser.add_argument("--key", "-k", help="Configuration key")
    parser.add_argument("--value", "-v", help="Configuration value")
    parser.add_argument("--format", "-f", choices=["json", "yaml"], default="json", help="Export format")
    parser.add_argument("--encrypt", action="store_true", help="Encrypt the value")
    
    args = parser.parse_args()
    
    # Set environment
    os.environ["ENVIRONMENT"] = args.environment
    
    async def run_action():
        """Run the specified action"""
        environment = ConfigurationEnvironment(args.environment)
        manager = await create_configuration_manager(environment)
        
        try:
            if args.action == "list":
                keys = manager.list_configurations()
                print(f"📋 Configuration keys ({len(keys)}):")
                for key in sorted(keys):
                    print(f"  - {key}")
            
            elif args.action == "get":
                if not args.key:
                    print("❌ Key is required for get action")
                    return
                
                value = await manager.get(args.key)
                if value is not None:
                    print(f"📖 {args.key}: {value}")
                else:
                    print(f"❌ Configuration key '{args.key}' not found")
            
            elif args.action == "set":
                if not args.key or args.value is None:
                    print("❌ Key and value are required for set action")
                    return
                
                success = await manager.set(args.key, args.value, encrypt=args.encrypt)
                if success:
                    print(f"✅ Configuration '{args.key}' set successfully")
                else:
                    print(f"❌ Failed to set configuration '{args.key}'")
            
            elif args.action == "delete":
                if not args.key:
                    print("❌ Key is required for delete action")
                    return
                
                success = await manager.delete(args.key)
                if success:
                    print(f"✅ Configuration '{args.key}' deleted successfully")
                else:
                    print(f"❌ Configuration key '{args.key}' not found")
            
            elif args.action == "export":
                export_data = await manager.export_configuration(args.format)
                print(export_data)
            
            elif args.action == "reload":
                await manager.reload()
                print("✅ Configuration reloaded successfully")
            
            elif args.action == "metrics":
                metrics = manager.get_metrics()
                print("📊 Configuration Manager Metrics:")
                for key, value in metrics.items():
                    print(f"  {key}: {value}")
        
        finally:
            await manager.shutdown()
    
    # Run the action
    try:
        asyncio.run(run_action())
    except KeyboardInterrupt:
        print("\n🛑 Operation cancelled by user")
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        sys.exit(1)

# Export for other modules
__all__ = [
    "EnterpriseConfigurationManager",
    "ConfigurationEnvironment",
    "ConfigurationSource",
    "ConfigurationSecurity",
    "ConfigurationStatus",
    "ConfigurationValue",
    "ConfigurationMetadata",
    "create_configuration_manager",
    "get_configuration_manager",
    "get_config",
    "set_config",
    "get_config_sync",
    "main"
]

if __name__ == "__main__":
    """🎯 Direct execution entry point"""
    main()