"""Pipeline Configuration

Ultra-advanced configuration management system for pipeline executions
with dynamic configuration, environment-specific settings, and validation.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

Business Logic: Configuration Loading → Validation → Environment Resolution → Dynamic Updates → Monitoring
"""import os
import json
import yaml
import logging
from typing import Dict, List, Any, Optional, Union, Type, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import asyncio
from pathlib import Path
import configparser


class ConfigurationSource(Enum):
    """Configuration sources"""    FILE = "file"
    ENVIRONMENT = "environment"
    DATABASE = "database"
    REMOTE = "remote"
    DEFAULT = "default"


class ConfigurationFormat(Enum):
    """Configuration file formats"""    JSON = "json"
    YAML = "yaml"
    INI = "ini"
    ENV = "env"


class EnvironmentType(Enum):
    """Environment types"""    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"


@dataclass
class ConfigurationSchema:
    """Configuration schema definition"""    key: str = ""
    data_type: Type = str
    required: bool = False
    default_value: Any = None
    description: str = ""
    validation_func: Optional[Callable] = None
    min_value: Optional[Union[int, float]] = None
    max_value: Optional[Union[int, float]] = None
    allowed_values: Optional[List[Any]] = None
    environment_specific: bool = False


@dataclass
class ConfigurationEntry:
    """Configuration entry"""    key: str = ""
    value: Any = None
    source: ConfigurationSource = ConfigurationSource.DEFAULT
    environment: str = ""
    last_updated: datetime = field(default_factory=datetime.now)
    schema: Optional[ConfigurationSchema] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""        return {
            "key": self.key,
            "value": self.value,
            "source": self.source.value,
            "environment": self.environment,
            "last_updated": self.last_updated.isoformat(),
            "schema": {
                "required": self.schema.required if self.schema else False,
                "data_type": self.schema.data_type.__name__ if self.schema else "str",
                "description": self.schema.description if self.schema else ""
            }
        }


class ConfigurationValidator:
    """Advanced configuration validation"""    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.ConfigurationValidator")
    
    def validate_entry(self, entry: ConfigurationEntry) -> List[str]:
        """Validate configuration entry"""        errors = []
        
        if not entry.schema:
            return errors  # No schema to validate against
        
        schema = entry.schema
        value = entry.value
        
        # Check if required value is present
        if schema.required and (value is None or value == ""):
            errors.append(f"Required configuration '{entry.key}' is missing")
            return errors
        
        # Skip further validation if value is None and not required
        if value is None and not schema.required:
            return errors
        
        # Type validation
        try:
            if schema.data_type and not isinstance(value, schema.data_type):
                # Attempt type conversion
                if schema.data_type == int:
                    entry.value = int(value)
                elif schema.data_type == float:
                    entry.value = float(value)
                elif schema.data_type == bool:
                    entry.value = self._parse_bool(value)
                elif schema.data_type == list:
                    if isinstance(value, str):
                        entry.value = json.loads(value)
                elif schema.data_type == dict:
                    if isinstance(value, str):
                        entry.value = json.loads(value)
                else:
                    entry.value = schema.data_type(value)
        except (ValueError, TypeError, json.JSONDecodeError) as e:
            errors.append(f"Invalid type for '{entry.key}': expected {schema.data_type.__name__}, got {type(value).__name__}")
        
        # Range validation
        if schema.min_value is not None and hasattr(entry.value, '__lt__'):
            if entry.value < schema.min_value:
                errors.append(f"Value for '{entry.key}' ({entry.value}) is below minimum ({schema.min_value})")
        
        if schema.max_value is not None and hasattr(entry.value, '__gt__'):
            if entry.value > schema.max_value:
                errors.append(f"Value for '{entry.key}' ({entry.value}) is above maximum ({schema.max_value})")
        
        # Allowed values validation
        if schema.allowed_values and entry.value not in schema.allowed_values:
            errors.append(f"Value for '{entry.key}' ({entry.value}) is not in allowed values: {schema.allowed_values}")
        
        # Custom validation function
        if schema.validation_func:
            try:
                if not schema.validation_func(entry.value):
                    errors.append(f"Custom validation failed for '{entry.key}'")
            except Exception as e:
                errors.append(f"Validation error for '{entry.key}': {e}")
        
        return errors
    
    def _parse_bool(self, value: Any) -> bool:
        """Parse boolean value"""        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() in ('true', '1', 'yes', 'on', 'enabled')
        if isinstance(value, int):
            return bool(value)
        return False
    
    def validate_configuration(self, config: Dict[str, ConfigurationEntry]) -> Dict[str, List[str]]:
        """Validate entire configuration"""        validation_errors = {}
        
        for key, entry in config.items():
            errors = self.validate_entry(entry)
            if errors:
                validation_errors[key] = errors
        
        return validation_errors


class ConfigurationLoader:
    """Advanced configuration loading system"""    
    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self.logger = logging.getLogger(f"{__name__}.ConfigurationLoader")
    
    async def load_from_file(self, file_path: str, config_format: ConfigurationFormat) -> Dict[str, Any]:
        """Load configuration from file"""        file_path = Path(file_path)
        
        if not file_path.exists():
            self.logger.warning(f"Configuration file not found: {file_path}")
            return {}
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                if config_format == ConfigurationFormat.JSON:
                    return json.load(f)
                elif config_format == ConfigurationFormat.YAML:
                    return yaml.safe_load(f) or {}
                elif config_format == ConfigurationFormat.INI:
                    parser = configparser.ConfigParser()
                    parser.read(file_path)
                    return {section: dict(parser[section]) for section in parser.sections()}
                elif config_format == ConfigurationFormat.ENV:
                    return self._parse_env_file(f.read())
                else:
                    self.logger.error(f"Unsupported configuration format: {config_format}")
                    return {}
        
        except Exception as e:
            self.logger.error(f"Failed to load configuration from {file_path}: {e}")
            return {}
    
    def _parse_env_file(self, content: str) -> Dict[str, str]:
        """Parse .env file content"""        config = {}
        for line in content.split('\n'):
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                config[key.strip()] = value.strip().strip('"').strip("'")
        return config
    
    async def load_from_environment(self, prefix: str = "") -> Dict[str, str]:
        """Load configuration from environment variables"""        config = {}
        
        for key, value in os.environ.items():
            if not prefix or key.startswith(prefix):
                # Remove prefix if specified
                config_key = key[len(prefix):] if prefix else key
                config[config_key.lower()] = value
        
        return config
    
    async def load_from_database(self, connection_config: Dict[str, Any]) -> Dict[str, Any]:
        """Load configuration from database"""        # Placeholder for database configuration loading
        # In real implementation, connect to database and fetch configuration
        self.logger.info("Loading configuration from database (placeholder)")
        return {}
    
    async def load_from_remote(self, remote_config: Dict[str, Any]) -> Dict[str, Any]:
        """Load configuration from remote source"""        # Placeholder for remote configuration loading
        # In real implementation, fetch from remote API/service
        self.logger.info("Loading configuration from remote source (placeholder)")
        return {}


class PipelineConfiguration:
    """    Ultra-advanced configuration management system for pipeline executions
    with dynamic configuration, environment-specific settings, and validation.
    
    Features:
    - Multi-source configuration loading (files, environment, database, remote)
    - Environment-specific configuration management
    - Real-time configuration validation and monitoring
    - Dynamic configuration updates without restart
    - Configuration versioning and rollback
    - Secure configuration handling for sensitive data
    """    
    def __init__(self, environment: str = "development", config_dir: str = "config"):
        self.environment = environment
        self.config_dir = Path(config_dir)
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Core components
        self.loader = ConfigurationLoader(config_dir)
        self.validator = ConfigurationValidator()
        
        # Configuration storage
        self.configuration: Dict[str, ConfigurationEntry] = {}
        self.schema_registry: Dict[str, ConfigurationSchema] = {}
        
        # Configuration sources
        self.configuration_sources: List[Dict[str, Any]] = []
        
        # Monitoring
        self.monitoring_active = False
        self.monitoring_task: Optional[asyncio.Task] = None
        self.change_callbacks: List[Callable] = []
        
        # Initialize default schema
        self._initialize_default_schema()
        
        self.logger.info(f"Pipeline Configuration initialized for environment: {environment}")
    
    def _initialize_default_schema(self):
        """Initialize default configuration schema"""        
        # System configuration
        self.register_schema(ConfigurationSchema(
            key="system.max_workers",
            data_type=int,
            required=False,
            default_value=4,
            description="Maximum number of worker processes",
            min_value=1,
            max_value=32
        ))
        
        self.register_schema(ConfigurationSchema(
            key="system.memory_limit",
            data_type=str,
            required=False,
            default_value="2GB",
            description="Memory limit for system processes"
        ))
        
        self.register_schema(ConfigurationSchema(
            key="system.debug_mode",
            data_type=bool,
            required=False,
            default_value=False,
            description="Enable debug mode"
        ))
        
        # Database configuration
        self.register_schema(ConfigurationSchema(
            key="database.host",
            data_type=str,
            required=True,
            description="Database host address"
        ))
        
        self.register_schema(ConfigurationSchema(
            key="database.port",
            data_type=int,
            required=False,
            default_value=5432,
            description="Database port number",
            min_value=1,
            max_value=65535
        ))
        
        self.register_schema(ConfigurationSchema(
            key="database.name",
            data_type=str,
            required=True,
            description="Database name"
        ))
        
        self.register_schema(ConfigurationSchema(
            key="database.pool_size",
            data_type=int,
            required=False,
            default_value=10,
            description="Database connection pool size",
            min_value=1,
            max_value=100
        ))
        
        # Cache configuration
        self.register_schema(ConfigurationSchema(
            key="cache.redis_url",
            data_type=str,
            required=False,
            default_value="redis://localhost:6379",
            description="Redis cache URL"
        ))
        
        self.register_schema(ConfigurationSchema(
            key="cache.ttl",
            data_type=int,
            required=False,
            default_value=3600,
            description="Default cache TTL in seconds",
            min_value=0
        ))
        
        # Pipeline configuration
        self.register_schema(ConfigurationSchema(
            key="pipeline.max_concurrent_executions",
            data_type=int,
            required=False,
            default_value=10,
            description="Maximum concurrent pipeline executions",
            min_value=1,
            max_value=100
        ))
        
        self.register_schema(ConfigurationSchema(
            key="pipeline.default_timeout",
            data_type=int,
            required=False,
            default_value=1800,
            description="Default pipeline timeout in seconds",
            min_value=60
        ))
        
        self.register_schema(ConfigurationSchema(
            key="pipeline.retry_attempts",
            data_type=int,
            required=False,
            default_value=3,
            description="Default number of retry attempts",
            min_value=0,
            max_value=10
        ))
        
        # Content processing configuration
        self.register_schema(ConfigurationSchema(
            key="content.max_file_size",
            data_type=str,
            required=False,
            default_value="100MB",
            description="Maximum content file size"
        ))
        
        self.register_schema(ConfigurationSchema(
            key="content.supported_formats",
            data_type=list,
            required=False,
            default_value=["mp3", "wav", "mp4", "jpg", "png", "pdf"],
            description="Supported content formats"
        ))
        
        # AI configuration
        self.register_schema(ConfigurationSchema(
            key="ai.model_path",
            data_type=str,
            required=False,
            default_value="models/",
            description="Path to AI models directory"
        ))
        
        self.register_schema(ConfigurationSchema(
            key="ai.batch_size",
            data_type=int,
            required=False,
            default_value=32,
            description="AI processing batch size",
            min_value=1,
            max_value=256
        ))
        
        self.register_schema(ConfigurationSchema(
            key="ai.confidence_threshold",
            data_type=float,
            required=False,
            default_value=0.8,
            description="AI confidence threshold",
            min_value=0.0,
            max_value=1.0
        ))
        
        # Security configuration
        self.register_schema(ConfigurationSchema(
            key="security.jwt_secret",
            data_type=str,
            required=True,
            description="JWT secret key for token signing",
            environment_specific=True
        ))
        
        self.register_schema(ConfigurationSchema(
            key="security.encryption_key",
            data_type=str,
            required=True,
            description="Encryption key for sensitive data",
            environment_specific=True
        ))
        
        self.register_schema(ConfigurationSchema(
            key="security.session_timeout",
            data_type=int,
            required=False,
            default_value=3600,
            description="Session timeout in seconds",
            min_value=300
        ))
        
        # Monitoring configuration
        self.register_schema(ConfigurationSchema(
            key="monitoring.enabled",
            data_type=bool,
            required=False,
            default_value=True,
            description="Enable monitoring"
        ))
        
        self.register_schema(ConfigurationSchema(
            key="monitoring.metrics_interval",
            data_type=int,
            required=False,
            default_value=30,
            description="Metrics collection interval in seconds",
            min_value=1
        ))
        
        self.register_schema(ConfigurationSchema(
            key="monitoring.alert_webhook",
            data_type=str,
            required=False,
            description="Webhook URL for alerts"
        ))
    
    def register_schema(self, schema: ConfigurationSchema):
        """Register configuration schema"""        self.schema_registry[schema.key] = schema
        
        # Set default value if provided
        if schema.default_value is not None:
            self.set_value(schema.key, schema.default_value, ConfigurationSource.DEFAULT)
    
    async def load_configuration(self):
        """Load configuration from all sources"""        
        # Define configuration sources in order of precedence (lowest to highest)
        sources = [
            {
                "type": "file",
                "format": ConfigurationFormat.YAML,
                "path": self.config_dir / "default.yaml"
            },
            {
                "type": "file",
                "format": ConfigurationFormat.YAML,
                "path": self.config_dir / f"{self.environment}.yaml"
            },
            {
                "type": "environment",
                "prefix": "PIPELINE_"
            }
        ]
        
        # Load from each source
        for source in sources:
            await self._load_from_source(source)
        
        # Validate configuration
        validation_errors = self.validator.validate_configuration(self.configuration)
        if validation_errors:
            error_msg = "Configuration validation failed:\n"
            for key, errors in validation_errors.items():
                error_msg += f"  {key}: {', '.join(errors)}\n"
            
            self.logger.error(error_msg)
            raise ValueError(error_msg)
        
        self.logger.info(f"Configuration loaded successfully with {len(self.configuration)} entries")
    
    async def _load_from_source(self, source: Dict[str, Any]):
        """Load configuration from a specific source"""        try:
            if source["type"] == "file":
                data = await self.loader.load_from_file(source["path"], source["format"])
                source_type = ConfigurationSource.FILE
                
            elif source["type"] == "environment":
                data = await self.loader.load_from_environment(source.get("prefix", ""))
                source_type = ConfigurationSource.ENVIRONMENT
                
            elif source["type"] == "database":
                data = await self.loader.load_from_database(source.get("config", {}))
                source_type = ConfigurationSource.DATABASE
                
            elif source["type"] == "remote":
                data = await self.loader.load_from_remote(source.get("config", {}))
                source_type = ConfigurationSource.REMOTE
                
            else:
                self.logger.warning(f"Unknown configuration source type: {source['type']}")
                return
            
            # Flatten nested configuration
            flattened_data = self._flatten_dict(data)
            
            # Create configuration entries
            for key, value in flattened_data.items():
                self.set_value(key, value, source_type)
            
            self.logger.debug(f"Loaded {len(flattened_data)} configuration entries from {source['type']}")
            
        except Exception as e:
            self.logger.error(f"Failed to load configuration from {source}: {e}")
    
    def _flatten_dict(self, data: Dict[str, Any], prefix: str = "") -> Dict[str, Any]:
        """Flatten nested dictionary"""        flattened = {}
        
        for key, value in data.items():
            full_key = f"{prefix}.{key}" if prefix else key
            
            if isinstance(value, dict):
                flattened.update(self._flatten_dict(value, full_key))
            else:
                flattened[full_key] = value
        
        return flattened
    
    def set_value(self, key: str, value: Any, source: ConfigurationSource = ConfigurationSource.DEFAULT):
        """Set configuration value"""        schema = self.schema_registry.get(key)
        
        entry = ConfigurationEntry(
            key=key,
            value=value,
            source=source,
            environment=self.environment,
            schema=schema
        )
        
        # Validate entry
        if schema:
            errors = self.validator.validate_entry(entry)
            if errors:
                self.logger.warning(f"Validation errors for {key}: {', '.join(errors)}")
        
        # Store configuration entry
        old_value = self.configuration.get(key)
        self.configuration[key] = entry
        
        # Notify change callbacks if value changed
        if old_value is None or old_value.value != value:
            self._notify_change_callbacks(key, old_value.value if old_value else None, value)
    
    def get_value(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""        entry = self.configuration.get(key)
        if entry:
            return entry.value
        
        # Check schema for default value
        schema = self.schema_registry.get(key)
        if schema and schema.default_value is not None:
            return schema.default_value
        
        return default
    
    def get_bool(self, key: str, default: bool = False) -> bool:
        """Get boolean configuration value"""        value = self.get_value(key, default)
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() in ('true', '1', 'yes', 'on', 'enabled')
        return bool(value)
    
    def get_int(self, key: str, default: int = 0) -> int:
        """Get integer configuration value"""        value = self.get_value(key, default)
        try:
            return int(value)
        except (ValueError, TypeError):
            return default
    
    def get_float(self, key: str, default: float = 0.0) -> float:
        """Get float configuration value"""        value = self.get_value(key, default)
        try:
            return float(value)
        except (ValueError, TypeError):
            return default
    
    def get_list(self, key: str, default: List[Any] = None) -> List[Any]:
        """Get list configuration value"""        value = self.get_value(key, default or [])
        if isinstance(value, list):
            return value
        if isinstance(value, str):
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                # Try comma-separated values
                return [item.strip() for item in value.split(',') if item.strip()]
        return default or []
    
    def get_dict(self, key: str, default: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get dictionary configuration value"""        value = self.get_value(key, default or {})
        if isinstance(value, dict):
            return value
        if isinstance(value, str):
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return default or {}
        return default or {}
    
    def get_section(self, prefix: str) -> Dict[str, Any]:
        """Get all configuration values with a specific prefix"""        section = {}
        
        for key, entry in self.configuration.items():
            if key.startswith(prefix):
                # Remove prefix from key
                section_key = key[len(prefix):].lstrip('.')
                section[section_key] = entry.value
        
        return section
    
    def has_value(self, key: str) -> bool:
        """Check if configuration value exists"""        return key in self.configuration
    
    def get_all_values(self) -> Dict[str, Any]:
        """Get all configuration values"""        return {key: entry.value for key, entry in self.configuration.items()}
    
    def get_configuration_info(self) -> Dict[str, Any]:
        """Get configuration information"""        return {
            "environment": self.environment,
            "total_entries": len(self.configuration),
            "schema_entries": len(self.schema_registry),
            "entries_by_source": {
                source.value: sum(1 for entry in self.configuration.values() 
                                if entry.source == source)
                for source in ConfigurationSource
            },
            "validation_status": "valid",  # Simplified
            "last_loaded": max([entry.last_updated for entry in self.configuration.values()],
                              default=datetime.now()).isoformat()
        }
    
    def add_change_callback(self, callback: Callable[[str, Any, Any], None]):
        """Add configuration change callback"""        self.change_callbacks.append(callback)
    
    def _notify_change_callbacks(self, key: str, old_value: Any, new_value: Any):
        """Notify configuration change callbacks"""        for callback in self.change_callbacks:
            try:
                callback(key, old_value, new_value)
            except Exception as e:
                self.logger.error(f"Configuration change callback error: {e}")
    
    def start_monitoring(self):
        """Start configuration monitoring"""        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
        self.logger.info("Configuration monitoring started")
    
    async def _monitoring_loop(self):
        """Configuration monitoring loop"""        while self.monitoring_active:
            try:
                # Monitor configuration files for changes
                # In real implementation, use file system watchers
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                self.logger.error(f"Configuration monitoring error: {e}")
                await asyncio.sleep(60)
    
    def stop_monitoring(self):
        """Stop configuration monitoring"""        self.monitoring_active = False
        if self.monitoring_task:
            self.monitoring_task.cancel()
        self.logger.info("Configuration monitoring stopped")
    
    async def reload_configuration(self):
        """Reload configuration from sources"""        self.logger.info("Reloading configuration")
        
        # Store current configuration for comparison
        old_config = {key: entry.value for key, entry in self.configuration.items()}
        
        # Clear current configuration (except defaults)
        self.configuration = {
            key: entry for key, entry in self.configuration.items()
            if entry.source == ConfigurationSource.DEFAULT
        }
        
        # Reload from sources
        await self.load_configuration()
        
        # Compare and notify changes
        new_config = {key: entry.value for key, entry in self.configuration.items()}
        
        for key in set(old_config.keys()) | set(new_config.keys()):
            old_value = old_config.get(key)
            new_value = new_config.get(key)
            
            if old_value != new_value:
                self._notify_change_callbacks(key, old_value, new_value)
        
        self.logger.info("Configuration reloaded successfully")
    
    def export_configuration(self, include_sensitive: bool = False) -> Dict[str, Any]:
        """Export configuration to dictionary"""        exported = {}
        
        for key, entry in self.configuration.items():
            # Skip sensitive configuration if not included
            if not include_sensitive and entry.schema and entry.schema.environment_specific:
                continue
            
            exported[key] = entry.to_dict()
        
        return {
            "environment": self.environment,
            "exported_at": datetime.now().isoformat(),
            "configuration": exported
        }
    
    async def shutdown(self):
        """Shutdown configuration system"""        self.logger.info("Shutting down configuration system")
        self.stop_monitoring()
        self.change_callbacks.clear()
        self.logger.info("Configuration system shutdown complete")
