"""Configuration Manager - Advanced Configuration Management System

Comprehensive configuration management framework for orchestration systems with
dynamic updates, environment-specific settings, and secure configuration handling.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL WARNING:
This code is the EXCLUSIVE INTELLECTUAL PROPERTY of Fahed Mlaiel.
Unauthorized use, copying, or distribution is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.
"""

import asyncio
import logging
import json
import os
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
import uuid
import yaml
from pathlib import Path

from backend.core.utils.metrics_collector import MetricsCollector
from backend.core.utils.event_dispatcher import EventDispatcher


class ConfigScope(Enum):
    """
Configuration scope levels."""

    GLOBAL = "global"
    ENVIRONMENT = "environment"
    SERVICE = "service"
    COMPONENT = "component"
    USER = "user"


class ConfigType(Enum):
    """Configuration value types."""

    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    JSON = "json"
    YAML = "yaml"
    SECRET = "secret"
    FILE_PATH = "file_path"
    URL = "url"
    EMAIL = "email"


class ConfigSource(Enum):
    """Configuration sources."""

    FILE = "file"
    ENVIRONMENT = "environment"
    DATABASE = "database"
    REMOTE_API = "remote_api"
    VAULT = "vault"
    CONSUL = "consul"
    KUBERNETES = "kubernetes"


class ValidationLevel(Enum):
    """Configuration validation levels."""

    NONE = "none"
    BASIC = "basic"
    STRICT = "strict"
    CUSTOM = "custom"


@dataclass
class ConfigDefinition:
    """Configuration parameter definition."""
    config_id: str
    name: str
    config_type: ConfigType
    scope: ConfigScope
    description: str = ""
    default_value: Any = None
    required: bool = False
    validation_rules: Dict[str, Any] = field(default_factory=dict)
    validation_level: ValidationLevel = ValidationLevel.BASIC
    sensitive: bool = False
    reload_required: bool = False
    tags: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ConfigValue:
    """Configuration value instance."""
    config_id: str
    value: Any
    source: ConfigSource
    scope: ConfigScope
    environment: str = "default"
    service: Optional[str] = None
    component: Optional[str] = None
    user: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    version: int = 1
    checksum: Optional[str] = None
    encrypted: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ConfigSnapshot:
    """Configuration snapshot for versioning."""
    snapshot_id: str
    name: str
    description: str
    configs: Dict[str, ConfigValue]
    created_at: datetime = field(default_factory=datetime.now)
    created_by: str = "system"
    tags: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ConfigWatcher:
    """Configuration change watcher."""
    watcher_id: str
    config_patterns: List[str]
    callback: Callable
    watch_scope: ConfigScope
    environment: Optional[str] = None
    service: Optional[str] = None
    component: Optional[str] = None
    active: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ConfigValidationResult:
    """
Configuration validation result."""
    config_id: str
    valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    validated_at: datetime = field(default_factory=datetime.now)


class ConfigurationManager:
    """
    Advanced configuration management system for orchestration platforms.
    
    Provides comprehensive configuration capabilities including:
    - Multi-source configuration loading (files, environment, remote APIs)
    - Hierarchical configuration with scope-based inheritance
    - Dynamic configuration updates with change notifications
    - Configuration validation and type checking
    - Secure handling of sensitive configuration data
    - Configuration versioning and snapshot management
    - Environment-specific configuration profiles
    """
    
    def __init__(
        self,
        config_dirs: Optional[List[str]] = None,
        default_environment: str = "development",
        encryption_key: Optional[str] = None
    ):
        self.logger = logging.getLogger(__name__)
        self.metrics_collector = MetricsCollector()
        self.event_dispatcher = EventDispatcher()
        
        # Core configuration
        self.config_dirs = config_dirs or ["./config", "/etc/ia-influencer", "~/.config/ia-influencer"]
        self.default_environment = default_environment
        self.current_environment = default_environment
        self.encryption_key = encryption_key
        
        # Configuration storage
        self.config_definitions: Dict[str, ConfigDefinition] = {}
        self.config_values: Dict[str, Dict[str, ConfigValue]] = {}  # scope -> config_id -> value
        self.config_cache: Dict[str, Any] = {}
        self.config_watchers: Dict[str, ConfigWatcher] = {}
        
        # Versioning and snapshots
        self.config_snapshots: Dict[str, ConfigSnapshot] = {}
        self.config_history: List[Dict[str, Any]] = []
        
        # Configuration sources
        self.config_sources: Dict[ConfigSource, Dict[str, Any]] = {
            ConfigSource.FILE: {'enabled': True, 'priority': 1},
            ConfigSource.ENVIRONMENT: {'enabled': True, 'priority': 2},
            ConfigSource.DATABASE: {'enabled': False, 'priority': 3},
            ConfigSource.REMOTE_API: {'enabled': False, 'priority': 4},
            ConfigSource.VAULT: {'enabled': False, 'priority': 5}
        }
        
        # Statistics
        self.manager_stats = {
            'total_configs_defined': 0,
            'total_configs_loaded': 0,
            'configuration_changes': 0,
            'validation_errors': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'watchers_triggered': 0,
            'snapshots_created': 0
        }
        
        # Background tasks
        self._start_background_tasks()
        
        self.logger.info(f"ConfigurationManager initialized for environment: {default_environment}")
    
    def _start_background_tasks(self) -> None:
        """Start background configuration management tasks."""
        asyncio.create_task(self._config_refresh_task())
        asyncio.create_task(self._cache_cleanup_task())
        asyncio.create_task(self._validation_task())
    
    async def register_config_definition(self, definition: ConfigDefinition) -> bool:
        """
        Register configuration parameter definition.
        
        Args:
            definition: Configuration definition to register
            
        Returns:
            bool: Success status
        """
        try:
            # Validate definition
            if not await self._validate_config_definition(definition):
                return False
            
            self.config_definitions[definition.config_id] = definition
            self.manager_stats['total_configs_defined'] += 1
            
            await self.event_dispatcher.emit('config_definition_registered', {
                'config_id': definition.config_id,
                'scope': definition.scope.value,
                'type': definition.config_type.value,
                'required': definition.required
            })
            
            await self.metrics_collector.increment('config_definitions.registered')
            
            self.logger.info(f"Config definition registered: {definition.config_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to register config definition: {e}")
            return False
    
    async def load_configurations(self, environment: Optional[str] = None) -> bool:
        """
        Load configurations from all enabled sources.
        
        Args:
            environment: Environment name (uses current if None)
            
        Returns:
            bool: Success status
        """
        try:
            environment = environment or self.current_environment
            
            # Load from each source in priority order
            sources = sorted(
                [(source, config) for source, config in self.config_sources.items() if config['enabled']],
                key=lambda x: x[1]['priority']
            )
            
            for source, _ in sources:
                await self._load_from_source(source, environment)
            
            # Validate loaded configurations
            await self._validate_all_configurations()
            
            # Update cache
            await self._refresh_cache()
            
            await self.event_dispatcher.emit('configurations_loaded', {
                'environment': environment,
                'sources_loaded': len(sources),
                'configs_loaded': self.manager_stats['total_configs_loaded']
            })
            
            self.logger.info(f"Configurations loaded for environment: {environment}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to load configurations: {e}")
            return False
    
    async def get_config(
        self,
        config_id: str,
        scope: Optional[ConfigScope] = None,
        environment: Optional[str] = None,
        service: Optional[str] = None,
        component: Optional[str] = None,
        user: Optional[str] = None,
        use_cache: bool = True
    ) -> Any:
        """
        Get configuration value with scope hierarchy resolution.
        
        Args:
            config_id: Configuration identifier
            scope: Specific scope to search (searches all if None)
            environment: Environment name
            service: Service name
            component: Component name
            user: User name
            use_cache: Whether to use cached values
            
        Returns:
            Configuration value or None if not found
        """
        try:
            # Check cache first
            cache_key = self._generate_cache_key(config_id, scope, environment, service, component, user)
            if use_cache and cache_key in self.config_cache:
                self.manager_stats['cache_hits'] += 1
                return self.config_cache[cache_key]
            
            self.manager_stats['cache_misses'] += 1
            
            # Search through scope hierarchy
            value = await self._resolve_config_value(config_id, scope, environment, service, component, user)
            
            # Cache the result
            if value is not None:
                self.config_cache[cache_key] = value
            
            return value
            
        except Exception as e:
            self.logger.error(f"Failed to get config: {config_id} - {e}")
            return None
    
    async def set_config(
        self,
        config_id: str,
        value: Any,
        scope: ConfigScope = ConfigScope.COMPONENT,
        environment: Optional[str] = None,
        service: Optional[str] = None,
        component: Optional[str] = None,
        user: Optional[str] = None,
        source: ConfigSource = ConfigSource.DATABASE
    ) -> bool:
        """
        Set configuration value.
        
        Args:
            config_id: Configuration identifier
            value: Configuration value
            scope: Configuration scope
            environment: Environment name
            service: Service name
            component: Component name
            user: User name
            source: Configuration source
            
        Returns:
            bool: Success status
        """
        try:
            # Get or create definition
            definition = self.config_definitions.get(config_id)
            if definition:
                # Validate value
                validation_result = await self._validate_config_value(definition, value)
                if not validation_result.valid:
                    self.logger.error(f"Config validation failed: {config_id} - {validation_result.errors}")
                    return False
            
            # Create config value
            config_value = ConfigValue(
                config_id=config_id,
                value=value,
                source=source,
                scope=scope,
                environment=environment or self.current_environment,
                service=service,
                component=component,
                user=user,
                checksum=self._calculate_checksum(value)
            )
            
            # Encrypt if sensitive
            if definition and definition.sensitive:
                config_value.value = await self._encrypt_value(value)
                config_value.encrypted = True
            
            # Store configuration
            scope_key = self._generate_scope_key(scope, environment, service, component, user)
            if scope_key not in self.config_values:
                self.config_values[scope_key] = {}
            
            # Check if value changed
            existing_value = self.config_values[scope_key].get(config_id)
            value_changed = (not existing_value or 
                           existing_value.checksum != config_value.checksum)
            
            if existing_value:
                config_value.version = existing_value.version + 1
            
            self.config_values[scope_key][config_id] = config_value
            
            if value_changed:
                self.manager_stats['configuration_changes'] += 1
                
                # Clear cache
                await self._invalidate_cache(config_id)
                
                # Notify watchers
                await self._notify_watchers(config_id, config_value)
                
                # Record change
                await self._record_config_change(config_id, config_value, existing_value)
            
            await self.event_dispatcher.emit('config_set', {
                'config_id': config_id,
                'scope': scope.value,
                'environment': environment or self.current_environment,
                'value_changed': value_changed,
                'version': config_value.version
            })
            
            await self.metrics_collector.increment('configs.set')
            
            self.logger.debug(f"Config set: {config_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to set config: {config_id} - {e}")
            return False
    
    async def create_snapshot(self, name: str, description: str = "", created_by: str = "system") -> str:
        """
        Create configuration snapshot.
        
        Args:
            name: Snapshot name
            description: Snapshot description
            created_by: Creator identifier
            
        Returns:
            str: Snapshot ID
        """
        try:
            snapshot_id = str(uuid.uuid4())
            
            # Collect all current configurations
            all_configs = {}
            for scope_values in self.config_values.values():
                all_configs.update(scope_values)
            
            snapshot = ConfigSnapshot(
                snapshot_id=snapshot_id,
                name=name,
                description=description,
                configs=all_configs.copy(),
                created_by=created_by
            )
            
            self.config_snapshots[snapshot_id] = snapshot
            self.manager_stats['snapshots_created'] += 1
            
            await self.event_dispatcher.emit('config_snapshot_created', {
                'snapshot_id': snapshot_id,
                'name': name,
                'config_count': len(all_configs),
                'created_by': created_by
            })
            
            await self.metrics_collector.increment('config_snapshots.created')
            
            self.logger.info(f"Config snapshot created: {snapshot_id}")
            return snapshot_id
            
        except Exception as e:
            self.logger.error(f"Failed to create snapshot: {e}")
            raise
    
    async def restore_snapshot(self, snapshot_id: str) -> bool:
        """
        Restore configuration from snapshot.
        
        Args:
            snapshot_id: Snapshot identifier
            
        Returns:
            bool: Success status
        """
        try:
            if snapshot_id not in self.config_snapshots:
                raise ValueError(f"Snapshot not found: {snapshot_id}")
            
            snapshot = self.config_snapshots[snapshot_id]
            
            # Clear current configurations
            self.config_values.clear()
            self.config_cache.clear()
            
            # Restore configurations from snapshot
            for config_id, config_value in snapshot.configs.items():
                scope_key = self._generate_scope_key(
                    config_value.scope,
                    config_value.environment,
                    config_value.service,
                    config_value.component,
                    config_value.user
                )
                
                if scope_key not in self.config_values:
                    self.config_values[scope_key] = {}
                
                self.config_values[scope_key][config_id] = config_value
            
            # Notify all watchers
            await self._notify_all_watchers()
            
            await self.event_dispatcher.emit('config_snapshot_restored', {
                'snapshot_id': snapshot_id,
                'name': snapshot.name,
                'config_count': len(snapshot.configs)
            })
            
            await self.metrics_collector.increment('config_snapshots.restored')
            
            self.logger.info(f"Config snapshot restored: {snapshot_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to restore snapshot: {e}")
            return False
    
    async def register_watcher(self, watcher: ConfigWatcher) -> bool:
        """
        Register configuration change watcher.
        
        Args:
            watcher: Configuration watcher
            
        Returns:
            bool: Success status
        """
        try:
            self.config_watchers[watcher.watcher_id] = watcher
            
            await self.event_dispatcher.emit('config_watcher_registered', {
                'watcher_id': watcher.watcher_id,
                'patterns': watcher.config_patterns,
                'scope': watcher.watch_scope.value
            })
            
            await self.metrics_collector.increment('config_watchers.registered')
            
            self.logger.info(f"Config watcher registered: {watcher.watcher_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to register watcher: {e}")
            return False
    
    async def validate_configuration(self, config_id: str, value: Any) -> ConfigValidationResult:
        """
        Validate configuration value.
        
        Args:
            config_id: Configuration identifier
            value: Value to validate
            
        Returns:
            ConfigValidationResult: Validation result
        """
        try:
            definition = self.config_definitions.get(config_id)
            if not definition:
                return ConfigValidationResult(
                    config_id=config_id,
                    valid=False,
                    errors=[f"No definition found for config: {config_id}"]
                )
            
            return await self._validate_config_value(definition, value)
            
        except Exception as e:
            return ConfigValidationResult(
                config_id=config_id,
                valid=False,
                errors=[f"Validation error: {str(e)}"]
            )
    
    async def export_configuration(
        self,
        format_type: str = "json",
        scope: Optional[ConfigScope] = None,
        environment: Optional[str] = None,
        include_sensitive: bool = False
    ) -> str:
        """
        Export configuration to string format.
        
        Args:
            format_type: Export format (json, yaml)
            scope: Specific scope to export
            environment: Environment to export
            include_sensitive: Whether to include sensitive values
            
        Returns:
            str: Exported configuration
        """
        try:
            # Collect configurations
            export_data = {}
            
            for scope_key, configs in self.config_values.items():
                for config_id, config_value in configs.items():
                    # Filter by criteria
                    if scope and config_value.scope != scope:
                        continue
                    if environment and config_value.environment != environment:
                        continue
                    
                    # Skip sensitive data if not requested
                    definition = self.config_definitions.get(config_id)
                    if definition and definition.sensitive and not include_sensitive:
                        continue
                    
                    # Decrypt if needed
                    value = config_value.value
                    if config_value.encrypted and include_sensitive:
                        value = await self._decrypt_value(value)
                    
                    export_data[config_id] = {
                        'value': value,
                        'scope': config_value.scope.value,
                        'environment': config_value.environment,
                        'source': config_value.source.value,
                        'version': config_value.version,
                        'timestamp': config_value.timestamp.isoformat()
                    }
            
            # Format output
            if format_type.lower() == "yaml":
                return yaml.dump(export_data, default_flow_style=False)
            else:  # Default to JSON
                return json.dumps(export_data, indent=2, default=str)
            
        except Exception as e:
            self.logger.error(f"Failed to export configuration: {e}")
            return "{}"
    
    async def import_configuration(self, config_data: str, format_type: str = "json") -> bool:
        """
        Import configuration from string format.
        
        Args:
            config_data: Configuration data string
            format_type: Data format (json, yaml)
            
        Returns:
            bool: Success status
        """
        try:
            # Parse data
            if format_type.lower() == "yaml":
                data = yaml.safe_load(config_data)
            else:  # Default to JSON
                data = json.loads(config_data)
            
            import_count = 0
            
            for config_id, config_info in data.items():
                success = await self.set_config(
                    config_id=config_id,
                    value=config_info['value'],
                    scope=ConfigScope(config_info.get('scope', 'component')),
                    environment=config_info.get('environment'),
                    source=ConfigSource(config_info.get('source', 'database'))
                )
                
                if success:
                    import_count += 1
            
            await self.event_dispatcher.emit('configuration_imported', {
                'format': format_type,
                'configs_imported': import_count,
                'total_configs': len(data)
            })
            
            self.logger.info(f"Configuration imported: {import_count}/{len(data)} configs")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to import configuration: {e}")
            return False
    
    async def _load_from_source(self, source: ConfigSource, environment: str) -> None:
        """Load configurations from specific source."""
        try:
            if source == ConfigSource.FILE:
                await self._load_from_files(environment)
            elif source == ConfigSource.ENVIRONMENT:
                await self._load_from_environment()
            elif source == ConfigSource.DATABASE:
                await self._load_from_database(environment)
            # Add other sources as needed
            
        except Exception as e:
            self.logger.error(f"Failed to load from source {source.value}: {e}")
    
    async def _load_from_files(self, environment: str) -> None:
        """Load configurations from files."""
        for config_dir in self.config_dirs:
            config_path = Path(config_dir).expanduser()
            
            if not config_path.exists():
                continue
            
            # Load main config file
            main_config_file = config_path / f"config.{environment}.json"
            if main_config_file.exists():
                await self._load_config_file(main_config_file, environment)
            
            # Load additional config files
            for config_file in config_path.glob(f"*.{environment}.*"):
                if config_file.suffix in ['.json', '.yaml', '.yml']:
                    await self._load_config_file(config_file, environment)
    
    async def _load_config_file(self, file_path: Path, environment: str) -> None:
        """Load configuration from single file."""
        try:
            with open(file_path, 'r') as f:
                if file_path.suffix == '.json':
                    data = json.load(f)
                elif file_path.suffix in ['.yaml', '.yml']:
                    data = yaml.safe_load(f)
                else:
                    return
            
            for config_id, value in data.items():
                await self.set_config(
                    config_id=config_id,
                    value=value,
                    scope=ConfigScope.ENVIRONMENT,
                    environment=environment,
                    source=ConfigSource.FILE
                )
            
            self.manager_stats['total_configs_loaded'] += len(data)
            
        except Exception as e:
            self.logger.error(f"Failed to load config file {file_path}: {e}")
    
    async def _load_from_environment(self) -> None:
        """Load configurations from environment variables."""
        prefix = "IA_INFLUENCER_"
        
        for key, value in os.environ.items():
            if key.startswith(prefix):
                config_id = key[len(prefix):].lower().replace('_', '.')
                
                await self.set_config(
                    config_id=config_id,
                    value=value,
                    scope=ConfigScope.GLOBAL,
                    source=ConfigSource.ENVIRONMENT
                )
                
                self.manager_stats['total_configs_loaded'] += 1
    
    async def _load_from_database(self, environment: str) -> None:
        try:
            logger.info(f"Executing _load_from_database")
            
            # Implementation for _load_from_database
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"_load_from_database completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"_load_from_database failed: {e}")
            raise
    async def _resolve_config_value(
        self,
        config_id: str,
        scope: Optional[ConfigScope],
        environment: Optional[str],
        service: Optional[str],
        component: Optional[str],
        user: Optional[str]
    ) -> Any:
        """
Resolve configuration value through scope hierarchy."""
        # Define search order (most specific to least specific)
        search_scopes = []
        
        if not scope:
            # Search all scopes in hierarchy order
            if user:
                search_scopes.append((ConfigScope.USER, environment, service, component, user))
            if component:
                search_scopes.append((ConfigScope.COMPONENT, environment, service, component, None))
            if service:
                search_scopes.append((ConfigScope.SERVICE, environment, service, None, None))
            if environment:
                search_scopes.append((ConfigScope.ENVIRONMENT, environment, None, None, None))
            search_scopes.append((ConfigScope.GLOBAL, None, None, None, None))
        else:
            search_scopes.append((scope, environment, service, component, user))
        
        # Search through scopes
        for search_scope, env, svc, comp, usr in search_scopes:
            scope_key = self._generate_scope_key(search_scope, env, svc, comp, usr)
            
            if scope_key in self.config_values and config_id in self.config_values[scope_key]:
                config_value = self.config_values[scope_key][config_id]
                
                # Decrypt if needed
                value = config_value.value
                if config_value.encrypted:
                    value = await self._decrypt_value(value)
                
                return value
        
        # Check for default value
        definition = self.config_definitions.get(config_id)
        if definition and definition.default_value is not None:
            return definition.default_value
        
        return None
    
    async def _validate_config_value(self, definition: ConfigDefinition, value: Any) -> ConfigValidationResult:
        """
Validate configuration value against definition."""
        result = ConfigValidationResult(config_id=definition.config_id, valid=True)
        
        try:
            # Type validation
            if not await self._validate_type(definition.config_type, value):
                result.valid = False
                result.errors.append(f"Invalid type: expected {definition.config_type.value}")
            
            # Custom validation rules
            for rule_name, rule_config in definition.validation_rules.items():
                rule_result = await self._apply_validation_rule(rule_name, rule_config, value)
                if not rule_result['valid']:
                    result.valid = False
                    result.errors.extend(rule_result.get('errors', []))
                    result.warnings.extend(rule_result.get('warnings', []))
            
            if not result.valid:
                self.manager_stats['validation_errors'] += 1
            
        except Exception as e:
            result.valid = False
            result.errors.append(f"Validation exception: {str(e)}")
        
        return result
    
    async def _validate_type(self, config_type: ConfigType, value: Any) -> bool:
        """Validate value type."""
        try:
            if config_type == ConfigType.STRING:
                return isinstance(value, str)
            elif config_type == ConfigType.INTEGER:
                return isinstance(value, int)
            elif config_type == ConfigType.FLOAT:
                return isinstance(value, (int, float))
            elif config_type == ConfigType.BOOLEAN:
                return isinstance(value, bool)
            elif config_type == ConfigType.JSON:
                return isinstance(value, (dict, list))
            elif config_type == ConfigType.FILE_PATH:
                return isinstance(value, str) and Path(value).exists()
            elif config_type == ConfigType.URL:
                return isinstance(value, str) and value.startswith(('http://', 'https://'))
            elif config_type == ConfigType.EMAIL:
                return isinstance(value, str) and '@' in value
            else:
                return True  # Unknown type, assume valid
        except Exception:
            return False
    
    async def _apply_validation_rule(self, rule_name: str, rule_config: Any, value: Any) -> Dict[str, Any]:
        """
Apply specific validation rule."""
        result = {'valid': True, 'errors': [], 'warnings': []}
        
        try:
            if rule_name == 'min_length' and isinstance(value, str):
                if len(value) < rule_config:
                    result['valid'] = False
                    result['errors'].append(f"Minimum length is {rule_config}")
            
            elif rule_name == 'max_length' and isinstance(value, str):
                if len(value) > rule_config:
                    result['valid'] = False
                    result['errors'].append(f"Maximum length is {rule_config}")
            
            elif rule_name == 'min_value' and isinstance(value, (int, float)):
                if value < rule_config:
                    result['valid'] = False
                    result['errors'].append(f"Minimum value is {rule_config}")
            
            elif rule_name == 'max_value' and isinstance(value, (int, float)):
                if value > rule_config:
                    result['valid'] = False
                    result['errors'].append(f"Maximum value is {rule_config}")
            
            elif rule_name == 'allowed_values':
                if value not in rule_config:
                    result['valid'] = False
                    result['errors'].append(f"Value must be one of: {rule_config}")
            
            elif rule_name == 'pattern' and isinstance(value, str):
                import re
                if not re.match(rule_config, value):
                    result['valid'] = False
                    result['errors'].append(f"Value must match pattern: {rule_config}")
        
        except Exception as e:
            result['valid'] = False
            result['errors'].append(f"Rule validation error: {str(e)}")
        
        return result
    
    async def _notify_watchers(self, config_id: str, config_value: ConfigValue) -> None:
        """Notify configuration watchers."""
        for watcher in self.config_watchers.values():
            if not watcher.active:
                continue
            
            # Check if config matches watcher patterns
            matches = any(
                pattern in config_id or config_id.startswith(pattern.rstrip('*'))
                for pattern in watcher.config_patterns
            )
            
            if matches:
                try:
                    await watcher.callback(config_id, config_value)
                    self.manager_stats['watchers_triggered'] += 1
                except Exception as e:
                    self.logger.error(f"Watcher callback failed: {watcher.watcher_id} - {e}")
    
    async def _notify_all_watchers(self) -> None:
        """Notify all watchers of configuration restore."""
        for watcher in self.config_watchers.values():
            if watcher.active:
                try:
                    await watcher.callback("*", None)  # Special signal for full restore
                except Exception as e:
                    self.logger.error(f"Watcher callback failed: {watcher.watcher_id} - {e}")
    
    def _generate_cache_key(
        self,
        config_id: str,
        scope: Optional[ConfigScope],
        environment: Optional[str],
        service: Optional[str],
        component: Optional[str],
        user: Optional[str]
    ) -> str:
        """Generate cache key for configuration."""
        parts = [config_id]
        if scope:
            parts.append(scope.value)
        if environment:
            parts.append(environment)
        if service:
            parts.append(service)
        if component:
            parts.append(component)
        if user:
            parts.append(user)
        
        return ":".join(parts)
    
    def _generate_scope_key(
        self,
        scope: ConfigScope,
        environment: Optional[str],
        service: Optional[str],
        component: Optional[str],
        user: Optional[str]
    ) -> str:
        """Generate scope key for configuration storage."""
        parts = [scope.value]
        if environment:
            parts.append(environment)
        if service:
            parts.append(service)
        if component:
            parts.append(component)
        if user:
            parts.append(user)
        
        return ":".join(parts)
    
    def _calculate_checksum(self, value: Any) -> str:
        """Calculate checksum for configuration value."""
        value_str = json.dumps(value, sort_keys=True, default=str)
        return hashlib.md5(value_str.encode()).hexdigest()
    
    async def _encrypt_value(self, value: Any) -> str:
        """
Encrypt sensitive configuration value."""
        # Simple encryption placeholder
        # In production, use proper encryption libraries
        if self.encryption_key:
            import base64
            value_str = json.dumps(value, default=str)
            encoded = base64.b64encode(value_str.encode()).decode()
            return f"encrypted:{encoded}"
        
        return value
    
    async def _decrypt_value(self, encrypted_value: str) -> Any:
        """Decrypt sensitive configuration value."""
        # Simple decryption placeholder
        if isinstance(encrypted_value, str) and encrypted_value.startswith("encrypted:"):
            import base64
            encoded = encrypted_value[10:]  # Remove "encrypted:" prefix
            decoded = base64.b64decode(encoded).decode()
            return json.loads(decoded)
        
        return encrypted_value
    
    async def _invalidate_cache(self, config_id: str) -> None:
        """Invalidate cache entries for configuration."""
        keys_to_remove = [key for key in self.config_cache.keys() if key.startswith(config_id)]
        for key in keys_to_remove:
            del self.config_cache[key]
    
    async def _refresh_cache(self) -> None:
        """
Refresh configuration cache."""
        self.config_cache.clear()
    
    async def _record_config_change(
        self,
        config_id: str,
        new_value: ConfigValue,
        old_value: Optional[ConfigValue]
    ) -> None:
        """
Record configuration change for auditing."""
        change_record = {
            'config_id': config_id,
            'timestamp': datetime.now().isoformat(),
            'new_value': {
                'value': new_value.value if not new_value.encrypted else '[ENCRYPTED]',
                'version': new_value.version,
                'source': new_value.source.value
            },
            'old_value': {
                'value': old_value.value if old_value and not old_value.encrypted else '[ENCRYPTED]',
                'version': old_value.version if old_value else 0,
                'source': old_value.source.value if old_value else 'none'
            } if old_value else None
        }
        
        self.config_history.append(change_record)
        
        # Limit history size
        if len(self.config_history) > 1000:
            self.config_history = self.config_history[-1000:]
    
    async def _validate_all_configurations(self) -> None:
        """
Validate all loaded configurations."""
        for scope_values in self.config_values.values():
            for config_id, config_value in scope_values.items():
                definition = self.config_definitions.get(config_id)
                if definition:
                    result = await self._validate_config_value(definition, config_value.value)
                    if not result.valid:
                        self.logger.warning(f"Config validation failed: {config_id} - {result.errors}")
    
    async def _config_refresh_task(self) -> None:
        """Background task for configuration refresh."""
        while True:
            try:
                # Reload configurations periodically
                await self.load_configurations()
                
                await asyncio.sleep(300)  # Refresh every 5 minutes
                
            except Exception as e:
                self.logger.error(f"Config refresh task failed: {e}")
                await asyncio.sleep(60)
    
    async def _cache_cleanup_task(self) -> None:
        """Background task for cache cleanup."""
        while True:
            try:
                # Clear old cache entries periodically
                if len(self.config_cache) > 10000:  # Arbitrary limit
                    self.config_cache.clear()
                
                await asyncio.sleep(3600)  # Clean every hour
                
            except Exception as e:
                self.logger.error(f"Cache cleanup task failed: {e}")
                await asyncio.sleep(300)
    
    async def _validation_task(self) -> None:
        """Background task for periodic validation."""
        while True:
            try:
                # Validate all configurations periodically
                await self._validate_all_configurations()
                
                await asyncio.sleep(1800)  # Validate every 30 minutes
                
            except Exception as e:
                self.logger.error(f"Validation task failed: {e}")
                await asyncio.sleep(300)
    
    async def _validate_config_definition(self, definition: ConfigDefinition) -> bool:
        """Validate configuration definition."""
        return bool(definition.config_id and definition.name)
    
    async def get_config_summary(self) -> Dict[str, Any]:
        """
Get configuration summary."""
        total_configs = sum(len(configs) for configs in self.config_values.values())
        
        return {
            'total_definitions': len(self.config_definitions),
            'total_values': total_configs,
            'current_environment': self.current_environment,
            'cache_size': len(self.config_cache),
            'watchers_count': len(self.config_watchers),
            'snapshots_count': len(self.config_snapshots),
            'enabled_sources': [
                source.value for source, config in self.config_sources.items()
                if config['enabled']
            ]
        }
    
    async def get_manager_stats(self) -> Dict[str, Any]:
        """
Get configuration manager statistics."""
        return {
            **self.manager_stats,
            'config_definitions': len(self.config_definitions),
            'active_watchers': len([w for w in self.config_watchers.values() if w.active]),
            'cache_size': len(self.config_cache),
            'history_size': len(self.config_history)
        }
