"""Voice Configuration Manager - Advanced Configuration Management System
======================================================================

Comprehensive configuration management system providing centralized settings,
environment configuration, dynamic updates, and configuration analytics
for the Ainflue voice ecosystem.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Union, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import os
import yaml
import toml
from pathlib import Path
import redis
import threading
import time
import hashlib
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

logger = logging.getLogger(__name__)

class ConfigType(Enum):
    """Configuration type enumeration"""
    VOICE_ENGINE = "voice_engine"
    SYNTHESIS = "synthesis"
    PROCESSING = "processing"
    SECURITY = "security"
    ANALYTICS = "analytics"
    COLLABORATION = "collaboration"
    DISTRIBUTION = "distribution"
    PLATFORM = "platform"
    NOTIFICATION = "notification"
    BACKUP = "backup"

class ConfigFormat(Enum):
    """Configuration file formats"""
    JSON = "json"
    YAML = "yaml"
    TOML = "toml"
    ENV = "env"
    INI = "ini"

class ConfigScope(Enum):
    """Configuration scope levels"""
    GLOBAL = "global"
    ENVIRONMENT = "environment"
    SERVICE = "service"
    USER = "user"
    SESSION = "session"

class ConfigStatus(Enum):
    """Configuration status"""
    ACTIVE = "active"
    PENDING = "pending"
    DEPRECATED = "deprecated"
    INVALID = "invalid"
    ARCHIVED = "archived"

@dataclass
class ConfigurationSchema:
    """Configuration schema definition"""
    schema_id: str
    name: str
    config_type: ConfigType
    version: str
    schema_definition: Dict[str, Any]
    validation_rules: Dict[str, Any] = field(default_factory=dict)
    default_values: Dict[str, Any] = field(default_factory=dict)
    required_fields: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class Configuration:
    """Configuration instance"""
    config_id: str
    name: str
    config_type: ConfigType
    scope: ConfigScope
    schema_id: Optional[str]
    values: Dict[str, Any]
    environment: str = "production"
    version: str = "1.0.0"
    encrypted_fields: List[str] = field(default_factory=list)
    status: ConfigStatus = ConfigStatus.ACTIVE
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    created_by: Optional[str] = None
    updated_by: Optional[str] = None

@dataclass
class ConfigurationHistory:
    """Configuration change history"""
    history_id: str
    config_id: str
    action: str  # create, update, delete, activate, deprecate
    old_values: Optional[Dict[str, Any]]
    new_values: Optional[Dict[str, Any]]
    changed_fields: List[str]
    change_reason: Optional[str]
    timestamp: datetime = field(default_factory=datetime.utcnow)
    changed_by: Optional[str] = None

class ConfigurationEngine:
    """Core configuration management engine"""
    
    def __init__(self, config_dir: str = "/config"):
        """Initialize configuration engine"""
        self.config_dir = Path(config_dir)
        self.configurations = {}
        self.schemas = {}
        self.config_cache = {}
        self.history = {}
        self.watchers = {}
        self.redis_client = redis.Redis(decode_responses=True)
        self.encryption_key = None
        
        # Ensure config directory exists
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Load existing configurations
        asyncio.create_task(self._load_configurations())
        
        # Start file watcher
        self._start_file_watcher()
        
        logger.info(f"⚙️ Configuration Engine initialized at {config_dir}")
    
    async def create_schema(
        self,
        name: str,
        config_type: ConfigType,
        schema_definition: Dict[str, Any],
        version: str = "1.0.0"
    ) -> str:
        """Create configuration schema"""
        try:
            schema_id = f"schema_{name}_{config_type.value}_{int(time.time())}"
            
            schema = ConfigurationSchema(
                schema_id=schema_id,
                name=name,
                config_type=config_type,
                version=version,
                schema_definition=schema_definition,
                validation_rules=schema_definition.get("validation", {}),
                default_values=schema_definition.get("defaults", {}),
                required_fields=schema_definition.get("required", [])
            )
            
            self.schemas[schema_id] = schema
            
            # Save schema to file
            await self._save_schema_to_file(schema)
            
            logger.info(f"Created configuration schema: {schema_id}")
            return schema_id
            
        except Exception as e:
            logger.error(f"Failed to create schema: {e}")
            raise
    
    async def create_configuration(
        self,
        name: str,
        config_type: ConfigType,
        scope: ConfigScope,
        values: Dict[str, Any],
        schema_id: Optional[str] = None,
        environment: str = "production"
    ) -> str:
        """Create new configuration"""
        try:
            config_id = f"config_{name}_{config_type.value}_{int(time.time())}"
            
            # Validate against schema if provided
            if schema_id:
                await self._validate_configuration(values, schema_id)
            
            # Encrypt sensitive fields
            encrypted_values, encrypted_fields = await self._encrypt_sensitive_fields(
                values, config_type
            )
            
            configuration = Configuration(
                config_id=config_id,
                name=name,
                config_type=config_type,
                scope=scope,
                schema_id=schema_id,
                values=encrypted_values,
                environment=environment,
                encrypted_fields=encrypted_fields
            )
            
            self.configurations[config_id] = configuration
            
            # Save to file
            await self._save_configuration_to_file(configuration)
            
            # Cache configuration
            await self._cache_configuration(configuration)
            
            # Record history
            await self._record_history(config_id, "create", None, values)
            
            logger.info(f"Created configuration: {config_id}")
            return config_id
            
        except Exception as e:
            logger.error(f"Failed to create configuration: {e}")
            raise
    
    async def get_configuration(
        self,
        config_id: Optional[str] = None,
        name: Optional[str] = None,
        config_type: Optional[ConfigType] = None,
        scope: Optional[ConfigScope] = None,
        environment: str = "production"
    ) -> Optional[Configuration]:
        """Get configuration by ID or criteria"""
        try:
            # Get by ID if provided
            if config_id:
                # Try cache first
                cached = await self._get_cached_configuration(config_id)
                if cached:
                    return cached
                
                # Fallback to memory
                config = self.configurations.get(config_id)
                if config:
                    # Decrypt sensitive fields
                    decrypted_config = await self._decrypt_configuration(config)
                    return decrypted_config
            
            # Search by criteria
            for config in self.configurations.values():
                if name and config.name != name:
                    continue
                if config_type and config.config_type != config_type:
                    continue
                if scope and config.scope != scope:
                    continue
                if config.environment != environment:
                    continue
                
                # Decrypt and return
                decrypted_config = await self._decrypt_configuration(config)
                return decrypted_config
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get configuration: {e}")
            return None
    
    async def update_configuration(
        self,
        config_id: str,
        updates: Dict[str, Any],
        updated_by: Optional[str] = None,
        change_reason: Optional[str] = None
    ) -> bool:
        """Update configuration values"""
        try:
            config = self.configurations.get(config_id)
            if not config:
                raise ValueError(f"Configuration not found: {config_id}")
            
            # Validate updates against schema
            if config.schema_id:
                await self._validate_configuration(updates, config.schema_id)
            
            # Store old values for history
            old_values = config.values.copy()
            
            # Encrypt sensitive fields in updates
            encrypted_updates, new_encrypted_fields = await self._encrypt_sensitive_fields(
                updates, config.config_type
            )
            
            # Update configuration
            config.values.update(encrypted_updates)
            config.encrypted_fields.extend(new_encrypted_fields)
            config.updated_at = datetime.utcnow()
            config.updated_by = updated_by
            
            # Save to file
            await self._save_configuration_to_file(config)
            
            # Update cache
            await self._cache_configuration(config)
            
            # Record history
            changed_fields = list(updates.keys())
            await self._record_history(
                config_id, "update", old_values, config.values,
                changed_fields, change_reason, updated_by
            )
            
            logger.info(f"Updated configuration: {config_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update configuration: {e}")
            return False
    
    async def delete_configuration(
        self,
        config_id: str,
        deleted_by: Optional[str] = None
    ) -> bool:
        """Delete configuration"""
        try:
            config = self.configurations.get(config_id)
            if not config:
                return False
            
            # Record history before deletion
            await self._record_history(
                config_id, "delete", config.values, None,
                changed_by=deleted_by
            )
            
            # Remove from memory
            del self.configurations[config_id]
            
            # Remove from cache
            await self._remove_from_cache(config_id)
            
            # Archive file instead of deleting
            await self._archive_configuration_file(config)
            
            logger.info(f"Deleted configuration: {config_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete configuration: {e}")
            return False
    
    async def get_configuration_value(
        self,
        config_id: str,
        key: str,
        default: Any = None
    ) -> Any:
        """Get specific configuration value"""
        try:
            config = await self.get_configuration(config_id)
            if not config:
                return default
            
            # Support nested keys (e.g., "voice.synthesis.quality")
            keys = key.split('.')
            value = config.values
            
            for k in keys:
                if isinstance(value, dict) and k in value:
                    value = value[k]
                else:
                    return default
            
            return value
            
        except Exception as e:
            logger.error(f"Failed to get configuration value: {e}")
            return default
    
    async def set_configuration_value(
        self,
        config_id: str,
        key: str,
        value: Any,
        updated_by: Optional[str] = None
    ) -> bool:
        """Set specific configuration value"""
        try:
            # Support nested keys
            keys = key.split('.')
            updates = {}
            current = updates
            
            for i, k in enumerate(keys):
                if i == len(keys) - 1:
                    current[k] = value
                else:
                    current[k] = {}
                    current = current[k]
            
            return await self.update_configuration(config_id, updates, updated_by)
            
        except Exception as e:
            logger.error(f"Failed to set configuration value: {e}")
            return False
    
    async def _validate_configuration(
        self,
        values: Dict[str, Any],
        schema_id: str
    ):
        """Validate configuration against schema"""
        try:
            schema = self.schemas.get(schema_id)
            if not schema:
                raise ValueError(f"Schema not found: {schema_id}")
            
            # Check required fields
            for field in schema.required_fields:
                if field not in values:
                    raise ValueError(f"Required field missing: {field}")
            
            # Validate field types and constraints
            for field, value in values.items():
                if field in schema.schema_definition:
                    field_schema = schema.schema_definition[field]
                    await self._validate_field(field, value, field_schema)
            
        except Exception as e:
            logger.error(f"Configuration validation failed: {e}")
            raise
    
    async def _validate_field(
        self,
        field_name: str,
        value: Any,
        field_schema: Dict[str, Any]
    ):
        """Validate individual field"""
        try:
            # Type validation
            expected_type = field_schema.get("type")
            if expected_type and not isinstance(value, eval(expected_type)):
                raise ValueError(f"Field {field_name} must be of type {expected_type}")
            
            # Range validation for numbers
            if isinstance(value, (int, float)):
                min_val = field_schema.get("minimum")
                max_val = field_schema.get("maximum")
                if min_val is not None and value < min_val:
                    raise ValueError(f"Field {field_name} must be >= {min_val}")
                if max_val is not None and value > max_val:
                    raise ValueError(f"Field {field_name} must be <= {max_val}")
            
            # String length validation
            if isinstance(value, str):
                min_len = field_schema.get("minLength")
                max_len = field_schema.get("maxLength")
                if min_len is not None and len(value) < min_len:
                    raise ValueError(f"Field {field_name} must be at least {min_len} characters")
                if max_len is not None and len(value) > max_len:
                    raise ValueError(f"Field {field_name} must be at most {max_len} characters")
            
            # Enum validation
            allowed_values = field_schema.get("enum")
            if allowed_values and value not in allowed_values:
                raise ValueError(f"Field {field_name} must be one of: {allowed_values}")
            
        except Exception as e:
            logger.error(f"Field validation failed for {field_name}: {e}")
            raise
    
    async def _encrypt_sensitive_fields(
        self,
        values: Dict[str, Any],
        config_type: ConfigType
    ) -> Tuple[Dict[str, Any], List[str]]:
        """Encrypt sensitive configuration fields"""
        try:
            encrypted_values = values.copy()
            encrypted_fields = []
            
            # Define sensitive field patterns per config type
            sensitive_patterns = {
                ConfigType.SECURITY: ["password", "secret", "key", "token"],
                ConfigType.PLATFORM: ["api_key", "secret_key", "token"],
                ConfigType.NOTIFICATION: ["smtp_password", "api_key"],
                ConfigType.BACKUP: ["encryption_key", "password"]
            }
            
            patterns = sensitive_patterns.get(config_type, [])
            
            for field, value in values.items():
                if any(pattern in field.lower() for pattern in patterns):
                    if isinstance(value, str):
                        encrypted_values[field] = await self._encrypt_value(value)
                        encrypted_fields.append(field)
            
            return encrypted_values, encrypted_fields
            
        except Exception as e:
            logger.error(f"Failed to encrypt sensitive fields: {e}")
            return values, []
    
    async def _encrypt_value(self, value: str) -> str:
        """Encrypt a single value"""
        try:
            # Simple encryption implementation (would use proper encryption in production)
            if not self.encryption_key:
                self.encryption_key = "default_key_change_in_production"
            
            # This is a placeholder - use proper encryption like Fernet
            import base64
            encoded = base64.b64encode(value.encode()).decode()
            return f"encrypted:{encoded}"
            
        except Exception as e:
            logger.error(f"Failed to encrypt value: {e}")
            return value
    
    async def _decrypt_configuration(self, config: Configuration) -> Configuration:
        """Decrypt sensitive fields in configuration"""
        try:
            decrypted_config = Configuration(**config.__dict__)
            
            for field in config.encrypted_fields:
                if field in decrypted_config.values:
                    encrypted_value = decrypted_config.values[field]
                    decrypted_config.values[field] = await self._decrypt_value(encrypted_value)
            
            return decrypted_config
            
        except Exception as e:
            logger.error(f"Failed to decrypt configuration: {e}")
            return config
    
    async def _decrypt_value(self, encrypted_value: str) -> str:
        """Decrypt a single value"""
        try:
            if encrypted_value.startswith("encrypted:"):
                # Remove prefix and decode
                encoded = encrypted_value[10:]
                import base64
                return base64.b64decode(encoded.encode()).decode()
            
            return encrypted_value
            
        except Exception as e:
            logger.error(f"Failed to decrypt value: {e}")
            return encrypted_value
    
    async def _load_configurations(self):
        """Load configurations from files"""
        try:
            config_files = self.config_dir.glob("**/*.json")
            
            for config_file in config_files:
                try:
                    with open(config_file, 'r') as f:
                        data = json.load(f)
                    
                    # Convert to Configuration object
                    config = Configuration(**data)
                    self.configurations[config.config_id] = config
                    
                except Exception as e:
                    logger.warning(f"Failed to load config file {config_file}: {e}")
            
            logger.info(f"Loaded {len(self.configurations)} configurations")
            
        except Exception as e:
            logger.error(f"Failed to load configurations: {e}")
    
    async def _save_configuration_to_file(self, config: Configuration):
        """Save configuration to file"""
        try:
            config_file = self.config_dir / f"{config.config_type.value}" / f"{config.name}.json"
            config_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Convert to dict and save
            config_data = {
                "config_id": config.config_id,
                "name": config.name,
                "config_type": config.config_type.value,
                "scope": config.scope.value,
                "schema_id": config.schema_id,
                "values": config.values,
                "environment": config.environment,
                "version": config.version,
                "encrypted_fields": config.encrypted_fields,
                "status": config.status.value,
                "metadata": config.metadata,
                "created_at": config.created_at.isoformat(),
                "updated_at": config.updated_at.isoformat(),
                "created_by": config.created_by,
                "updated_by": config.updated_by
            }
            
            with open(config_file, 'w') as f:
                json.dump(config_data, f, indent=2)
            
        except Exception as e:
            logger.error(f"Failed to save configuration to file: {e}")
    
    async def _save_schema_to_file(self, schema: ConfigurationSchema):
        """Save schema to file"""
        try:
            schema_file = self.config_dir / "schemas" / f"{schema.name}.json"
            schema_file.parent.mkdir(parents=True, exist_ok=True)
            
            schema_data = {
                "schema_id": schema.schema_id,
                "name": schema.name,
                "config_type": schema.config_type.value,
                "version": schema.version,
                "schema_definition": schema.schema_definition,
                "validation_rules": schema.validation_rules,
                "default_values": schema.default_values,
                "required_fields": schema.required_fields,
                "created_at": schema.created_at.isoformat()
            }
            
            with open(schema_file, 'w') as f:
                json.dump(schema_data, f, indent=2)
            
        except Exception as e:
            logger.error(f"Failed to save schema to file: {e}")
    
    async def _cache_configuration(self, config: Configuration):
        """Cache configuration in Redis"""
        try:
            cache_key = f"config:{config.config_id}"
            cache_data = json.dumps({
                "config_id": config.config_id,
                "values": config.values,
                "updated_at": config.updated_at.isoformat()
            })
            
            # Cache for 1 hour
            await self.redis_client.setex(cache_key, 3600, cache_data)
            
        except Exception as e:
            logger.warning(f"Failed to cache configuration: {e}")
    
    async def _get_cached_configuration(self, config_id: str) -> Optional[Configuration]:
        """Get configuration from cache"""
        try:
            cache_key = f"config:{config_id}"
            cached_data = await self.redis_client.get(cache_key)
            
            if cached_data:
                data = json.loads(cached_data)
                config = self.configurations.get(config_id)
                if config:
                    return await self._decrypt_configuration(config)
            
            return None
            
        except Exception as e:
            logger.warning(f"Failed to get cached configuration: {e}")
            return None
    
    async def _remove_from_cache(self, config_id: str):
        """Remove configuration from cache"""
        try:
            cache_key = f"config:{config_id}"
            await self.redis_client.delete(cache_key)
            
        except Exception as e:
            logger.warning(f"Failed to remove from cache: {e}")
    
    async def _archive_configuration_file(self, config: Configuration):
        """Archive configuration file"""
        try:
            config_file = self.config_dir / f"{config.config_type.value}" / f"{config.name}.json"
            archive_file = self.config_dir / "archive" / f"{config.name}_{int(time.time())}.json"
            archive_file.parent.mkdir(parents=True, exist_ok=True)
            
            if config_file.exists():
                shutil.move(str(config_file), str(archive_file))
            
        except Exception as e:
            logger.error(f"Failed to archive configuration file: {e}")
    
    async def _record_history(
        self,
        config_id: str,
        action: str,
        old_values: Optional[Dict[str, Any]],
        new_values: Optional[Dict[str, Any]],
        changed_fields: List[str] = None,
        change_reason: Optional[str] = None,
        changed_by: Optional[str] = None
    ):
        """Record configuration change history"""
        try:
            history_id = f"history_{config_id}_{int(time.time())}"
            
            history = ConfigurationHistory(
                history_id=history_id,
                config_id=config_id,
                action=action,
                old_values=old_values,
                new_values=new_values,
                changed_fields=changed_fields or [],
                change_reason=change_reason,
                changed_by=changed_by
            )
            
            if config_id not in self.history:
                self.history[config_id] = []
            
            self.history[config_id].append(history)
            
        except Exception as e:
            logger.error(f"Failed to record history: {e}")
    
    def _start_file_watcher(self):
        """Start file system watcher for configuration changes"""
        try:
            class ConfigFileHandler(FileSystemEventHandler):
                def __init__(self, engine):
                    self.engine = engine
                
                def on_modified(self, event):
                    if not event.is_directory and event.src_path.endswith('.json'):
                        asyncio.create_task(self.engine._reload_configuration_file(event.src_path))
            
            event_handler = ConfigFileHandler(self)
            observer = Observer()
            observer.schedule(event_handler, str(self.config_dir), recursive=True)
            observer.start()
            
            logger.info("Configuration file watcher started")
            
        except Exception as e:
            logger.error(f"Failed to start file watcher: {e}")
    
    async def _reload_configuration_file(self, file_path: str):
        """Reload configuration from modified file"""
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            config = Configuration(**data)
            self.configurations[config.config_id] = config
            
            # Update cache
            await self._cache_configuration(config)
            
            logger.info(f"Reloaded configuration from file: {file_path}")
            
        except Exception as e:
            logger.warning(f"Failed to reload configuration file {file_path}: {e}")

class SettingsManager:
    """Application settings management"""
    
    def __init__(self):
        """Initialize settings manager"""
        self.user_settings = {}
        self.default_settings = {}
        
        logger.info("🔧 Settings Manager initialized")

class VoiceSettings:
    """Voice-specific settings management"""
    
    def __init__(self):
        """Initialize voice settings"""
        self.voice_profiles = {}
        self.synthesis_settings = {}
        
        logger.info("🎤⚙️ Voice Settings initialized")

class ConfigurationAnalytics:
    """Configuration usage analytics"""
    
    def __init__(self):
        """Initialize configuration analytics"""
        self.usage_metrics = {}
        self.performance_stats = {}
        
        logger.info("📊 Configuration Analytics initialized")

class SettingsOptimization:
    """Settings optimization engine"""
    
    def __init__(self):
        """Initialize settings optimization"""
        self.optimization_rules = {}
        
        logger.info("⚡ Settings Optimization initialized")

class ConfigurationManagement:
    """Configuration management system"""
    
    def __init__(self):
        """Initialize configuration management"""
        self.config_policies = {}
        
        logger.info("🛠️ Configuration Management initialized")

class VoiceConfigurationManager:
    """Main voice configuration manager"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize voice configuration manager"""
        self.config = config or {}
        self.configuration_engine = ConfigurationEngine()
        self.settings_manager = SettingsManager()
        self.voice_settings = VoiceSettings()
        self.configuration_analytics = ConfigurationAnalytics()
        self.settings_optimization = SettingsOptimization()
        self.configuration_management = ConfigurationManagement()
        
        # Initialize default voice configurations
        asyncio.create_task(self._initialize_voice_configurations())
        
        logger.info("🎤⚙️ Voice Configuration Manager initialized")
    
    async def create_voice_config(
        self,
        name: str,
        voice_settings: Dict[str, Any],
        environment: str = "production"
    ) -> str:
        """Create voice-specific configuration"""
        try:
            config_id = await self.configuration_engine.create_configuration(
                name=name,
                config_type=ConfigType.VOICE_ENGINE,
                scope=ConfigScope.SERVICE,
                values=voice_settings,
                environment=environment
            )
            
            return config_id
            
        except Exception as e:
            logger.error(f"Failed to create voice config: {e}")
            raise
    
    async def get_voice_config(
        self,
        name: str,
        environment: str = "production"
    ) -> Optional[Configuration]:
        """Get voice configuration by name"""
        try:
            return await self.configuration_engine.get_configuration(
                name=name,
                config_type=ConfigType.VOICE_ENGINE,
                environment=environment
            )
            
        except Exception as e:
            logger.error(f"Failed to get voice config: {e}")
            return None
    
    async def _initialize_voice_configurations(self):
        """Initialize default voice configurations"""
        try:
            # Voice engine configuration
            await self.create_voice_config(
                "voice_engine_default",
                {
                    "voice_bank_path": "/data/voices/bank",
                    "models_path": "/data/voices/models",
                    "temp_path": "/tmp/voice_processing",
                    "max_concurrent_jobs": 10,
                    "default_quality": "high",
                    "cache_enabled": True,
                    "cache_ttl": 3600
                }
            )
            
            # Voice synthesis configuration
            await self.create_voice_config(
                "voice_synthesis_default",
                {
                    "model_type": "transformer",
                    "sample_rate": 44100,
                    "bit_depth": 16,
                    "channels": 1,
                    "emotion_intensity": 0.7,
                    "voice_cloning_enabled": True,
                    "max_synthesis_length": 300
                }
            )
            
            # Voice processing configuration
            await self.create_voice_config(
                "voice_processing_default",
                {
                    "noise_reduction": True,
                    "auto_gain_control": True,
                    "echo_cancellation": True,
                    "compression_enabled": True,
                    "format_conversion": True,
                    "quality_enhancement": True
                }
            )
            
            logger.info("Default voice configurations initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize voice configurations: {e}")
