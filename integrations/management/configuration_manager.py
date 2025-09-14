"""Configuration Manager - Dynamic Integration Configuration System
=============================================================

Advanced configuration management system for dynamic integration settings,
environment-specific configurations, and runtime parameter adjustments.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import json
import yaml
import os
from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import uuid
from pathlib import Path
import hashlib
from collections import defaultdict

import redis.asyncio as redis
from cryptography.fernet import Fernet
import jsonschema
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class ConfigurationSource(Enum):
    """Configuration source types."""
    ENVIRONMENT = "environment"
    FILE = "file"
    DATABASE = "database"
    REDIS = "redis"
    REMOTE_API = "remote_api"
    SECRET_MANAGER = "secret_manager"


class ConfigurationType(Enum):
    """Configuration data types."""
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    LIST = "list"
    DICT = "dict"
    JSON = "json"
    ENCRYPTED = "encrypted"


@dataclass
class ConfigurationRule:
    """Configuration validation rule."""
    key: str
    required: bool = False
    type: ConfigurationType = ConfigurationType.STRING
    default: Any = None
    min_value: Optional[Union[int, float]] = None
    max_value: Optional[Union[int, float]] = None
    allowed_values: Optional[List[Any]] = None
    pattern: Optional[str] = None
    description: str = ""
    sensitive: bool = False
    environment_override: bool = True


@dataclass
class ConfigurationSet:
    """Configuration set for a specific integration or service."""
    name: str
    version: str
    rules: List[ConfigurationRule]
    schema: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    last_updated: datetime = field(default_factory=datetime.now)


@dataclass
class ConfigurationChange:
    """Configuration change event."""
    id: str
    configuration_key: str
    old_value: Any
    new_value: Any
    source: ConfigurationSource
    timestamp: datetime = field(default_factory=datetime.now)
    user: Optional[str] = None
    reason: Optional[str] = None


class ConfigurationWatcher(FileSystemEventHandler):
    """File system watcher for configuration changes."""
    
    def __init__(self, config_manager -> None: 'ConfigurationManager') -> None:
        self.config_manager = config_manager
        self.logger = logging.getLogger(__name__)
    
    def on_modified(self, event) -> None:
        """Handle file modification events."""
        if not event.is_directory and event.src_path.endswith(('.json', '.yaml', '.yml')):
            asyncio.create_task(self.config_manager._reload_file_config(event.src_path))
            self.logger.info(f"Configuration file modified: {event.src_path}")


class ConfigurationManager:
    """Dynamic integration configuration management system."""
    
    def __init__(
        self,
        redis_url -> None: Optional[str] = None,
        config_dir -> None: Optional[str] = None,
        encryption_key -> None: Optional[str] = None,
        config -> None: Optional[Dict[str, Any]] = None
    ) -> None:
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Storage backends
        self.redis_url = redis_url
        self.redis_client = None
        self.config_dir = Path(config_dir) if config_dir else Path("./config")
        
        # Encryption for sensitive data
        self.encryption_key = encryption_key or Fernet.generate_key()
        self.cipher = Fernet(self.encryption_key)
        
        # Configuration state
        self.configurations: Dict[str, Dict[str, Any]] = {}
        self.configuration_sets: Dict[str, ConfigurationSet] = {}
        self.configuration_cache: Dict[str, Any] = {}
        self.cache_ttl = timedelta(minutes=5)
        self.cache_timestamps: Dict[str, datetime] = {}
        
        # Change tracking
        self.change_history: List[ConfigurationChange] = []
        self.change_listeners: Dict[str, List[Callable]] = defaultdict(list)
        
        # File watching
        self.file_observer = Observer()
        self.file_watcher = ConfigurationWatcher(self)
        
        # Environment detection
        self.environment = os.getenv('ENVIRONMENT', 'development')
        self.environment_prefixes = ['AINFLUE_', 'INTEGRATION_']
        
        # Metrics
        self.metrics = {
            'total_configs': 0,
            'cached_configs': 0,
            'config_changes': 0,
            'validation_errors': 0,
            'reload_count': 0
        }
        
    async def initialize(self) -> None:
        """Initialize the configuration manager."""
        # Connect to Redis if configured
        if self.redis_url:
            self.redis_client = redis.from_url(self.redis_url)
        
        # Create config directory
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Load initial configurations
        await self._load_environment_configs()
        await self._load_file_configs()
        
        # Start file watching
        if self.config_dir.exists():
            self.file_observer.schedule(
                self.file_watcher,
                str(self.config_dir),
                recursive=True
            )
            self.file_observer.start()
        
        self.logger.info(f"Configuration manager initialized for environment: {self.environment}")
    
    async def register_configuration_set(self, config_set -> None: ConfigurationSet) -> None:
        """Register a configuration set with validation rules."""
        self.configuration_sets[config_set.name] = config_set
        
        # Validate existing configurations against new rules
        if config_set.name in self.configurations:
            await self._validate_configuration(config_set.name, self.configurations[config_set.name])
        
        self.logger.info(f"Registered configuration set: {config_set.name}")
    
    async def get_configuration(
        self,
        config_name: str,
        key: Optional[str] = None,
        default: Any = None,
        use_cache: bool = True
    ) -> Any:
        """Get configuration value(s)."""
        cache_key = f"{config_name}:{key}" if key else config_name
        
        # Check cache first
        if use_cache and cache_key in self.configuration_cache:
            cache_time = self.cache_timestamps.get(cache_key, datetime.min)
            if datetime.now() - cache_time < self.cache_ttl:
                return self.configuration_cache[cache_key]
        
        # Load configuration if not exists
        if config_name not in self.configurations:
            await self._load_configuration(config_name)
        
        # Get configuration value
        config = self.configurations.get(config_name, {})
        
        if key:
            # Get specific key
            value = self._get_nested_value(config, key, default)
        else:
            # Get entire configuration
            value = config if config else default
        
        # Decrypt if necessary
        if isinstance(value, str) and value.startswith('ENCRYPTED:'):
            try:
                encrypted_data = value[10:]  # Remove 'ENCRYPTED:' prefix
                value = self.cipher.decrypt(encrypted_data.encode()).decode()
            except Exception as e:
                self.logger.error(f"Failed to decrypt configuration value: {e}")
                value = default
        
        # Cache the result
        if use_cache:
            self.configuration_cache[cache_key] = value
            self.cache_timestamps[cache_key] = datetime.now()
        
        return value
    
    async def set_configuration(
        self,
        config_name -> None: str,
        key -> None: str,
        value -> None: Any,
        source -> None: ConfigurationSource = ConfigurationSource.DATABASE,
        user -> None: Optional[str] = None,
        reason -> None: Optional[str] = None,
        persist -> None: bool = True
    ) -> None:
        """Set configuration value."""
        # Get current value for change tracking
        current_value = await self.get_configuration(config_name, key, use_cache=False)
        
        # Validate against configuration set rules
        if config_name in self.configuration_sets:
            await self._validate_single_value(config_name, key, value)
        
        # Ensure configuration exists
        if config_name not in self.configurations:
            self.configurations[config_name] = {}
        
        # Check if value should be encrypted
        if config_name in self.configuration_sets:
            config_set = self.configuration_sets[config_name]
            for rule in config_set.rules:
                if rule.key == key and rule.sensitive:
                    encrypted_value = self.cipher.encrypt(str(value).encode()).decode()
                    value = f"ENCRYPTED:{encrypted_value}"
                    break
        
        # Set the value
        self._set_nested_value(self.configurations[config_name], key, value)
        
        # Clear cache
        cache_keys_to_remove = [
            cache_key for cache_key in self.configuration_cache.keys()
            if cache_key.startswith(f"{config_name}:")
        ]
        for cache_key in cache_keys_to_remove:
            del self.configuration_cache[cache_key]
            del self.cache_timestamps[cache_key]
        
        # Record change
        change = ConfigurationChange(
            id=str(uuid.uuid4()),
            configuration_key=f"{config_name}.{key}",
            old_value=current_value,
            new_value=value,
            source=source,
            user=user,
            reason=reason
        )
        self.change_history.append(change)
        self.metrics['config_changes'] += 1
        
        # Persist if requested
        if persist:
            await self._persist_configuration(config_name)
        
        # Notify listeners
        await self._notify_change_listeners(config_name, key, current_value, value)
        
        self.logger.info(f"Configuration updated: {config_name}.{key}")
    
    async def reload_configuration(self, config_name -> None: str) -> None:
        """Reload configuration from all sources."""
        # Clear cached configuration
        self.configurations.pop(config_name, None)
        
        # Clear related cache entries
        cache_keys_to_remove = [
            cache_key for cache_key in self.configuration_cache.keys()
            if cache_key.startswith(f"{config_name}:")
        ]
        for cache_key in cache_keys_to_remove:
            del self.configuration_cache[cache_key]
            del self.cache_timestamps[cache_key]
        
        # Reload from sources
        await self._load_configuration(config_name)
        self.metrics['reload_count'] += 1
        
        self.logger.info(f"Configuration reloaded: {config_name}")
    
    async def get_configuration_metadata(self, config_name: str) -> Dict[str, Any]:
        """Get configuration metadata and statistics."""
        if config_name not in self.configurations:
            return {}
        
        config = self.configurations[config_name]
        config_set = self.configuration_sets.get(config_name)
        
        metadata = {
            'name': config_name,
            'environment': self.environment,
            'total_keys': len(self._flatten_dict(config)),
            'last_modified': max(
                [change.timestamp for change in self.change_history
                 if change.configuration_key.startswith(f"{config_name}.")],
                default=datetime.min
            ).isoformat() if self.change_history else None,
            'has_validation_rules': config_set is not None,
            'validation_rule_count': len(config_set.rules) if config_set else 0
        }
        
        if config_set:
            metadata.update({
                'version': config_set.version,
                'description': config_set.metadata.get('description', ''),
                'schema': config_set.schema
            })
        
        return metadata
    
    async def validate_all_configurations(self) -> Dict[str, List[str]]:
        """Validate all configurations against their rules."""
        validation_results = {}
        
        for config_name in self.configurations:
            try:
                await self._validate_configuration(config_name, self.configurations[config_name])
                validation_results[config_name] = []
            except Exception as e:
                validation_results[config_name] = [str(e)]
                self.metrics['validation_errors'] += 1
        
        return validation_results
    
    def add_change_listener(self, config_name -> None: str, callback -> None: Callable) -> None:
        """Add listener for configuration changes."""
        self.change_listeners[config_name].append(callback)
        self.logger.info(f"Added change listener for: {config_name}")
    
    def remove_change_listener(self, config_name -> None: str, callback -> None: Callable) -> None:
        """Remove configuration change listener."""
        if config_name in self.change_listeners:
            try:
                self.change_listeners[config_name].remove(callback)
                self.logger.info(f"Removed change listener for: {config_name}")
            except ValueError:
                pass
    
    async def export_configuration(
        self,
        config_name: str,
        format_type: str = "json",
        include_sensitive: bool = False
    ) -> str:
        """Export configuration in specified format."""
        if config_name not in self.configurations:
            await self._load_configuration(config_name)
        
        config = self.configurations.get(config_name, {})
        
        if not include_sensitive:
            # Remove encrypted values
            config = self._remove_sensitive_data(config.copy())
        
        if format_type.lower() == "json":
            return json.dumps(config, indent=2, default=str)
        elif format_type.lower() in ["yaml", "yml"]:
            return yaml.dump(config, default_flow_style=False)
        else:
            raise ValueError(f"Unsupported format: {format_type}")
    
    async def import_configuration(
        self,
        config_name -> None: str,
        data -> None: str,
        format_type -> None: str = "json",
        merge -> None: bool = True,
        validate -> None: bool = True
    ) -> None:
        """Import configuration from data."""
        # Parse data
        if format_type.lower() == "json":
            imported_config = json.loads(data)
        elif format_type.lower() in ["yaml", "yml"]:
            imported_config = yaml.safe_load(data)
        else:
            raise ValueError(f"Unsupported format: {format_type}")
        
        # Validate if requested
        if validate and config_name in self.configuration_sets:
            await self._validate_configuration(config_name, imported_config)
        
        # Merge or replace
        if merge and config_name in self.configurations:
            self._deep_merge(self.configurations[config_name], imported_config)
        else:
            self.configurations[config_name] = imported_config
        
        # Clear cache
        cache_keys_to_remove = [
            cache_key for cache_key in self.configuration_cache.keys()
            if cache_key.startswith(f"{config_name}:")
        ]
        for cache_key in cache_keys_to_remove:
            del self.configuration_cache[cache_key]
            del self.cache_timestamps[cache_key]
        
        # Persist
        await self._persist_configuration(config_name)
        
        self.logger.info(f"Configuration imported: {config_name}")
    
    async def _load_environment_configs(self) -> None:
        """Load configurations from environment variables."""
        env_configs = defaultdict(dict)
        
        for key, value in os.environ.items():
            # Check if it matches our prefixes
            for prefix in self.environment_prefixes:
                if key.startswith(prefix):
                    # Remove prefix and parse
                    config_key = key[len(prefix):].lower()
                    
                    # Split into config_name and key
                    if '.' in config_key:
                        config_name, nested_key = config_key.split('.', 1)
                        self._set_nested_value(env_configs[config_name], nested_key, value)
                    else:
                        env_configs['global'][config_key] = value
        
        # Merge with existing configurations
        for config_name, config in env_configs.items():
            if config_name not in self.configurations:
                self.configurations[config_name] = {}
            self._deep_merge(self.configurations[config_name], config)
    
    async def _load_file_configs(self) -> None:
        """Load configurations from files."""
        if not self.config_dir.exists():
            return
        
        # Load environment-specific configs first
        env_config_file = self.config_dir / f"{self.environment}.json"
        if env_config_file.exists():
            await self._load_file_config(env_config_file)
        
        # Load other config files
        for config_file in self.config_dir.glob("*.json"):
            if config_file.name != f"{self.environment}.json":
                await self._load_file_config(config_file)
        
        for config_file in self.config_dir.glob("*.yaml"):
            await self._load_file_config(config_file)
        
        for config_file in self.config_dir.glob("*.yml"):
            await self._load_file_config(config_file)
    
    async def _load_file_config(self, config_file -> None: Path) -> None:
        """Load configuration from a specific file."""
        try:
            with open(config_file, 'r') as f:
                if config_file.suffix == '.json':
                    file_config = json.load(f)
                elif config_file.suffix in ['.yaml', '.yml']:
                    file_config = yaml.safe_load(f)
                else:
                    return
            
            config_name = config_file.stem
            if config_name not in self.configurations:
                self.configurations[config_name] = {}
            
            self._deep_merge(self.configurations[config_name], file_config)
            self.logger.info(f"Loaded configuration from file: {config_file}")
            
        except Exception as e:
            self.logger.error(f"Failed to load configuration file {config_file}: {e}")
    
    async def _reload_file_config(self, file_path -> None: str) -> None:
        """Reload configuration from a modified file."""
        config_file = Path(file_path)
        if config_file.is_relative_to(self.config_dir):
            await self._load_file_config(config_file)
    
    async def _load_configuration(self, config_name -> None: str) -> None:
        """Load configuration from all sources."""
        if config_name not in self.configurations:
            self.configurations[config_name] = {}
        
        # Load from Redis if available
        if self.redis_client:
            try:
                redis_config = await self.redis_client.get(f"config:{config_name}")
                if redis_config:
                    config_data = json.loads(redis_config)
                    self._deep_merge(self.configurations[config_name], config_data)
            except Exception as e:
                self.logger.warning(f"Failed to load configuration from Redis: {e}")
        
        self.metrics['total_configs'] = len(self.configurations)
    
    async def _persist_configuration(self, config_name -> None: str) -> None:
        """Persist configuration to storage backends."""
        config = self.configurations.get(config_name, {})
        
        # Save to Redis
        if self.redis_client:
            try:
                await self.redis_client.set(
                    f"config:{config_name}",
                    json.dumps(config, default=str),
                    ex=86400  # 24 hours TTL
                )
            except Exception as e:
                self.logger.error(f"Failed to persist configuration to Redis: {e}")
        
        # Save to file
        config_file = self.config_dir / f"{config_name}.json"
        try:
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2, default=str)
        except Exception as e:
            self.logger.error(f"Failed to persist configuration to file: {e}")
    
    async def _validate_configuration(self, config_name -> None: str, config -> None: Dict[str, Any]) -> None:
        """Validate configuration against rules."""
        if config_name not in self.configuration_sets:
            return  # No validation rules defined
        
        config_set = self.configuration_sets[config_name]
        
        # Validate against JSON schema if provided
        if config_set.schema:
            try:
                jsonschema.validate(config, config_set.schema)
            except jsonschema.ValidationError as e:
                raise ValueError(f"Schema validation failed: {e.message}")
        
        # Validate individual rules
        for rule in config_set.rules:
            await self._validate_single_value(config_name, rule.key, 
                                             self._get_nested_value(config, rule.key))
    
    async def _validate_single_value(self, config_name -> None: str, key -> None: str, value -> None: Any) -> None:
        """Validate a single configuration value."""
        if config_name not in self.configuration_sets:
            return
        
        config_set = self.configuration_sets[config_name]
        rule = next((r for r in config_set.rules if r.key == key), None)
        
        if not rule:
            return
        
        # Required check
        if rule.required and value is None:
            raise ValueError(f"Required configuration missing: {key}")
        
        if value is None:
            return  # Optional value not provided
        
        # Type validation
        if rule.type == ConfigurationType.INTEGER and not isinstance(value, int):
            try:
                value = int(value)
            except (ValueError, TypeError):
                raise ValueError(f"Configuration {key} must be an integer")
        
        elif rule.type == ConfigurationType.FLOAT and not isinstance(value, (int, float)):
            try:
                value = float(value)
            except (ValueError, TypeError):
                raise ValueError(f"Configuration {key} must be a number")
        
        elif rule.type == ConfigurationType.BOOLEAN and not isinstance(value, bool):
            if isinstance(value, str):
                value = value.lower() in ('true', '1', 'yes', 'on')
            else:
                raise ValueError(f"Configuration {key} must be a boolean")
        
        # Range validation
        if rule.min_value is not None and value < rule.min_value:
            raise ValueError(f"Configuration {key} must be >= {rule.min_value}")
        
        if rule.max_value is not None and value > rule.max_value:
            raise ValueError(f"Configuration {key} must be <= {rule.max_value}")
        
        # Allowed values validation
        if rule.allowed_values and value not in rule.allowed_values:
            raise ValueError(f"Configuration {key} must be one of: {rule.allowed_values}")
        
        # Pattern validation
        if rule.pattern and isinstance(value, str):
            import re
            if not re.match(rule.pattern, value):
                raise ValueError(f"Configuration {key} does not match pattern: {rule.pattern}")
    
    async def _notify_change_listeners(self, config_name -> None: str, key -> None: str, old_value -> None: Any, new_value -> None: Any) -> None:
        """Notify registered change listeners."""
        if config_name in self.change_listeners:
            for listener in self.change_listeners[config_name]:
                try:
                    if asyncio.iscoroutinefunction(listener):
                        await listener(config_name, key, old_value, new_value)
                    else:
                        listener(config_name, key, old_value, new_value)
                except Exception as e:
                    self.logger.error(f"Change listener failed: {e}")
    
    def _get_nested_value(self, data: Dict[str, Any], key: str, default: Any = None) -> Any:
        """Get nested value using dot notation."""
        keys = key.split('.')
        current = data
        
        for k in keys:
            if isinstance(current, dict) and k in current:
                current = current[k]
            else:
                return default
        
        return current
    
    def _set_nested_value(self, data -> None: Dict[str, Any], key -> None: str, value -> None: Any) -> None:
        """Set nested value using dot notation."""
        keys = key.split('.')
        current = data
        
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]
        
        current[keys[-1]] = value
    
    def _deep_merge(self, target -> None: Dict[str, Any], source -> None: Dict[str, Any]) -> None:
        """Deep merge source into target dictionary."""
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                self._deep_merge(target[key], value)
            else:
                target[key] = value
    
    def _flatten_dict(self, d: Dict[str, Any], parent_key: str = '', sep: str = '.') -> Dict[str, Any]:
        """Flatten nested dictionary."""
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self._flatten_dict(v, new_key, sep).items())
            else:
                items.append((new_key, v))
        return dict(items)
    
    def _remove_sensitive_data(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Remove sensitive data from configuration."""
        for key, value in config.items():
            if isinstance(value, dict):
                config[key] = self._remove_sensitive_data(value)
            elif isinstance(value, str) and value.startswith('ENCRYPTED:'):
                config[key] = "[ENCRYPTED]"
        return config
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get configuration metrics."""
        return {
            'configurations': {
                'total_configs': self.metrics['total_configs'],
                'cached_configs': len(self.configuration_cache),
                'configuration_sets': len(self.configuration_sets)
            },
            'changes': {
                'total_changes': self.metrics['config_changes'],
                'recent_changes': len([
                    c for c in self.change_history 
                    if datetime.now() - c.timestamp < timedelta(hours=24)
                ])
            },
            'performance': {
                'cache_hit_rate': (
                    len(self.configuration_cache) / max(self.metrics['total_configs'], 1)
                ) * 100,
                'reload_count': self.metrics['reload_count']
            },
            'validation': {
                'validation_errors': self.metrics['validation_errors']
            }
        }
    
    async def cleanup(self) -> None:
        """Cleanup resources."""
        # Stop file observer
        if self.file_observer.is_alive():
            self.file_observer.stop()
            self.file_observer.join()
        
        # Close Redis connection
        if self.redis_client:
            await self.redis_client.close()


# Example usage
if __name__ == "__main__":
    async def main() -> None:
        # Initialize configuration manager
        config_manager = ConfigurationManager(
            redis_url="redis://localhost:6379",
            config_dir="./config"
        )
        
        await config_manager.initialize()
        
        # Register configuration set with validation rules
        integration_rules = [
            ConfigurationRule(
                key="api_key",
                required=True,
                type=ConfigurationType.STRING,
                sensitive=True,
                description="API key for integration"
            ),
            ConfigurationRule(
                key="rate_limit",
                required=False,
                type=ConfigurationType.INTEGER,
                default=100,
                min_value=1,
                max_value=1000,
                description="Requests per minute limit"
            ),
            ConfigurationRule(
                key="enabled",
                required=False,
                type=ConfigurationType.BOOLEAN,
                default=True,
                description="Enable/disable integration"
            )
        ]
        
        config_set = ConfigurationSet(
            name="openai_integration",
            version="1.0",
            rules=integration_rules
        )
        
        await config_manager.register_configuration_set(config_set)
        
        # Set configuration values
        await config_manager.set_configuration(
            "openai_integration",
            "api_key",
            "sk-test-123456",
            user="admin",
            reason="Initial setup"
        )
        
        await config_manager.set_configuration(
            "openai_integration",
            "rate_limit",
            50
        )
        
        # Get configuration values
        api_key = await config_manager.get_configuration("openai_integration", "api_key")
        rate_limit = await config_manager.get_configuration("openai_integration", "rate_limit")
        
        print(f"API Key: {api_key}")
        print(f"Rate Limit: {rate_limit}")
        
        # Get metrics
        metrics = config_manager.get_metrics()
        print(f"Metrics: {json.dumps(metrics, indent=2)}")
        
        await config_manager.cleanup()
    
    asyncio.run(main())