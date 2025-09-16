#!/usr/bin/env python3
"""
⚙️ UNIFIED CONFIGURATION SERVICE - Enterprise Infrastructure Configuration
=========================================================================

Comprehensive unified configuration service consolidating:
- Centralized configuration management with environment support
- Dynamic configuration watcher with real-time monitoring
- Secrets management and hot reloading capabilities
- Configuration validation and versioning

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved

⚠️ STRICT COPYRIGHT WARNING ⚠️
This code is proprietary and confidential. Unauthorized use, reproduction,
distribution, or modification is strictly prohibited and will be prosecuted
to the full extent of the law.
"""

import asyncio
import json
import os
import time
import logging
from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
import yaml
from pydantic import BaseModel, Field
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import structlog

# Configure structured logging
logger = structlog.get_logger(__name__)


class ConfigurationType(str, Enum):
    """Configuration value types"""
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    LIST = "list"
    DICT = "dict"
    SECRET = "secret"
    JSON = "json"


class ConfigurationScope(str, Enum):
    """Configuration scope levels"""
    GLOBAL = "global"
    SERVICE = "service"
    ENVIRONMENT = "environment"
    USER = "user"
    SESSION = "session"


class ConfigurationSource(str, Enum):
    """Configuration source types"""
    FILE = "file"
    ENVIRONMENT = "environment"
    DATABASE = "database"
    REMOTE = "remote"
    VAULT = "vault"
    KUBERNETES = "kubernetes"


class ChangeType(str, Enum):
    """Configuration change types"""
    CREATED = "created"
    MODIFIED = "modified"
    DELETED = "deleted"
    MOVED = "moved"


@dataclass
class ConfigurationItem:
    """Individual configuration item"""
    key: str
    value: Any
    type: ConfigurationType
    scope: ConfigurationScope
    source: ConfigurationSource
    description: str = ""
    required: bool = False
    default_value: Any = None
    validation_rules: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    version: int = 1
    checksum: str = field(init=False)
    
    def __post_init__(self):
        """Calculate checksum after initialization"""
        self.checksum = self._calculate_checksum()
    
    def _calculate_checksum(self) -> str:
        """Calculate configuration item checksum"""
        content = f"{self.key}:{self.value}:{self.type}:{self.scope}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]


@dataclass
class ConfigurationChange:
    """Configuration change data structure"""
    change_id: str
    change_type: ChangeType
    file_path: str
    key: Optional[str] = None
    old_value: Optional[Any] = None
    new_value: Optional[Any] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    source: ConfigurationSource = ConfigurationSource.FILE
    validated: bool = False
    applied: bool = False
    error: Optional[str] = None


@dataclass
class WatcherConfig:
    """Configuration watcher settings"""
    watch_directories: List[str] = field(default_factory=lambda: ["./config"])
    file_patterns: List[str] = field(default_factory=lambda: ["*.yaml", "*.yml", "*.json", "*.env"])
    ignore_patterns: List[str] = field(default_factory=lambda: [".*", "__pycache__", "*.pyc"])
    recursive: bool = True
    debounce_seconds: float = 1.0
    validation_enabled: bool = True
    hot_reload_enabled: bool = True
    backup_enabled: bool = True
    max_backup_files: int = 10


@dataclass
class UnifiedConfigurationConfig:
    """Unified configuration service settings"""
    config_directories: List[str] = field(default_factory=lambda: ["./config"])
    environment: str = "development"
    secrets_backend: str = "file"  # file, vault, kubernetes
    cache_enabled: bool = True
    cache_ttl: int = 3600
    encryption_enabled: bool = True
    encryption_key: Optional[str] = None
    validation_enabled: bool = True
    versioning_enabled: bool = True
    backup_enabled: bool = True
    watcher_config: WatcherConfig = field(default_factory=WatcherConfig)
    
    # Database settings for remote configuration
    database_url: Optional[str] = None
    
    # Vault settings
    vault_url: Optional[str] = None
    vault_token: Optional[str] = None
    
    # Kubernetes settings
    kubernetes_namespace: Optional[str] = None
    kubernetes_config_map: Optional[str] = None


class ConfigurationValidator:
    """Configuration validation engine"""
    
    @staticmethod
    def validate_item(item: ConfigurationItem) -> tuple[bool, Optional[str]]:
        """Validate a configuration item"""
        try:
            # Type validation
            if not ConfigurationValidator._validate_type(item.value, item.type):
                return False, f"Invalid type for {item.key}: expected {item.type}, got {type(item.value).__name__}"
            
            # Required validation
            if item.required and (item.value is None or item.value == ""):
                return False, f"Required configuration {item.key} is missing or empty"
            
            # Custom validation rules
            if item.validation_rules:
                is_valid, error = ConfigurationValidator._validate_rules(item.value, item.validation_rules)
                if not is_valid:
                    return False, f"Validation failed for {item.key}: {error}"
            
            return True, None
            
        except Exception as e:
            return False, f"Validation error for {item.key}: {str(e)}"
    
    @staticmethod
    def _validate_type(value: Any, expected_type: ConfigurationType) -> bool:
        """Validate value type"""
        if value is None:
            return True
        
        type_map = {
            ConfigurationType.STRING: str,
            ConfigurationType.INTEGER: int,
            ConfigurationType.FLOAT: (int, float),
            ConfigurationType.BOOLEAN: bool,
            ConfigurationType.LIST: list,
            ConfigurationType.DICT: dict,
            ConfigurationType.SECRET: str,
            ConfigurationType.JSON: (dict, list, str)
        }
        
        expected = type_map.get(expected_type)
        if expected is None:
            return True
        
        return isinstance(value, expected)
    
    @staticmethod
    def _validate_rules(value: Any, rules: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """Validate custom rules"""
        try:
            # Min/max length for strings
            if isinstance(value, str):
                if 'min_length' in rules and len(value) < rules['min_length']:
                    return False, f"Minimum length {rules['min_length']} required"
                if 'max_length' in rules and len(value) > rules['max_length']:
                    return False, f"Maximum length {rules['max_length']} exceeded"
            
            # Min/max value for numbers
            if isinstance(value, (int, float)):
                if 'min_value' in rules and value < rules['min_value']:
                    return False, f"Minimum value {rules['min_value']} required"
                if 'max_value' in rules and value > rules['max_value']:
                    return False, f"Maximum value {rules['max_value']} exceeded"
            
            # Allowed values
            if 'allowed_values' in rules and value not in rules['allowed_values']:
                return False, f"Value must be one of {rules['allowed_values']}"
            
            # Pattern validation for strings
            if 'pattern' in rules and isinstance(value, str):
                import re
                if not re.match(rules['pattern'], value):
                    return False, f"Value must match pattern {rules['pattern']}"
            
            return True, None
            
        except Exception as e:
            return False, str(e)


class ConfigurationFileHandler(FileSystemEventHandler):
    """File system event handler for configuration changes"""
    
    def __init__(self, config_service: 'UnifiedConfigurationService'):
        self.config_service = config_service
        self.debounce_map = {}
        
    def on_modified(self, event):
        """Handle file modification events"""
        if not event.is_directory:
            self._handle_file_change(event.src_path, ChangeType.MODIFIED)
    
    def on_created(self, event):
        """Handle file creation events"""
        if not event.is_directory:
            self._handle_file_change(event.src_path, ChangeType.CREATED)
    
    def on_deleted(self, event):
        """Handle file deletion events"""
        if not event.is_directory:
            self._handle_file_change(event.src_path, ChangeType.DELETED)
    
    def on_moved(self, event):
        """Handle file move events"""
        if not event.is_directory:
            self._handle_file_change(event.dest_path, ChangeType.MOVED)
    
    def _handle_file_change(self, file_path: str, change_type: ChangeType):
        """Handle file change with debouncing"""
        try:
            # Check if file matches patterns
            if not self._should_handle_file(file_path):
                return
            
            # Debounce changes
            current_time = time.time()
            debounce_time = self.config_service.config.watcher_config.debounce_seconds
            
            if file_path in self.debounce_map:
                if current_time - self.debounce_map[file_path] < debounce_time:
                    return
            
            self.debounce_map[file_path] = current_time
            
            # Create change event
            change = ConfigurationChange(
                change_id=f"{change_type.value}_{int(current_time)}",
                change_type=change_type,
                file_path=file_path,
                timestamp=datetime.utcnow(),
                source=ConfigurationSource.FILE
            )
            
            # Queue change for processing
            asyncio.create_task(self.config_service._process_file_change(change))
            
        except Exception as e:
            logger.error("Error handling file change", 
                        file_path=file_path, 
                        change_type=change_type.value, 
                        error=str(e))
    
    def _should_handle_file(self, file_path: str) -> bool:
        """Check if file should be handled based on patterns"""
        import fnmatch
        
        file_name = os.path.basename(file_path)
        watcher_config = self.config_service.config.watcher_config
        
        # Check ignore patterns
        for pattern in watcher_config.ignore_patterns:
            if fnmatch.fnmatch(file_name, pattern):
                return False
        
        # Check file patterns
        for pattern in watcher_config.file_patterns:
            if fnmatch.fnmatch(file_name, pattern):
                return True
        
        return False


class UnifiedConfigurationService:
    """
    Unified configuration service consolidating configuration management,
    dynamic watching, secrets management, and hot reloading.
    """
    
    def __init__(self, config: UnifiedConfigurationConfig = None):
        """Initialize unified configuration service"""
        self.config = config or UnifiedConfigurationConfig()
        self.logger = logger.bind(service="unified_configuration")
        
        # Configuration storage
        self.configurations: Dict[str, ConfigurationItem] = {}
        self.configuration_cache: Dict[str, Any] = {}
        self.configuration_versions: Dict[str, List[ConfigurationItem]] = {}
        
        # Change tracking
        self.pending_changes: List[ConfigurationChange] = []
        self.change_history: List[ConfigurationChange] = []
        
        # File watching
        self.file_observer: Optional[Observer] = None
        self.file_handler: Optional[ConfigurationFileHandler] = None
        
        # State management
        self.is_running = False
        self.last_reload_time = datetime.utcnow()
        
        # Callbacks
        self.change_callbacks: List[Callable[[str, Any], None]] = []
        
        # Encryption
        self.encryption_key = self.config.encryption_key
        
        self.logger.info("Unified configuration service initialized", 
                        environment=self.config.environment)
    
    async def start(self):
        """Start the unified configuration service"""
        if self.is_running:
            self.logger.warning("Configuration service is already running")
            return
        
        try:
            # Load initial configurations
            await self._load_configurations()
            
            # Start file watcher if enabled
            if self.config.watcher_config.hot_reload_enabled:
                await self._start_file_watcher()
            
            # Start background tasks
            asyncio.create_task(self._configuration_maintenance_loop())
            
            self.is_running = True
            self.logger.info("Unified configuration service started successfully")
            
        except Exception as e:
            self.logger.error("Failed to start configuration service", error=str(e))
            raise
    
    async def stop(self):
        """Stop the unified configuration service"""
        if not self.is_running:
            self.logger.warning("Configuration service is not running")
            return
        
        try:
            # Stop file watcher
            if self.file_observer:
                self.file_observer.stop()
                self.file_observer.join()
            
            # Save any pending changes
            await self._save_pending_changes()
            
            self.is_running = False
            self.logger.info("Unified configuration service stopped successfully")
            
        except Exception as e:
            self.logger.error("Error stopping configuration service", error=str(e))
    
    async def _load_configurations(self):
        """Load configurations from all sources"""
        try:
            # Load from files
            await self._load_from_files()
            
            # Load from environment variables
            await self._load_from_environment()
            
            # Load from remote sources if configured
            if self.config.database_url:
                await self._load_from_database()
            
            if self.config.vault_url:
                await self._load_from_vault()
            
            if self.config.kubernetes_namespace:
                await self._load_from_kubernetes()
            
            # Validate all configurations
            if self.config.validation_enabled:
                await self._validate_all_configurations()
            
            # Update cache
            await self._update_cache()
            
            self.logger.info("Configurations loaded successfully", 
                           count=len(self.configurations))
            
        except Exception as e:
            self.logger.error("Error loading configurations", error=str(e))
            raise
    
    async def _load_from_files(self):
        """Load configurations from files"""
        for config_dir in self.config.config_directories:
            config_path = Path(config_dir)
            if not config_path.exists():
                self.logger.warning("Configuration directory not found", path=str(config_path))
                continue
            
            for file_path in config_path.rglob("*"):
                if file_path.is_file() and self._is_config_file(file_path):
                    await self._load_config_file(file_path)
    
    async def _load_config_file(self, file_path: Path):
        """Load configuration from a single file"""
        try:
            content = file_path.read_text()
            
            # Parse based on file extension
            if file_path.suffix in ['.yaml', '.yml']:
                data = yaml.safe_load(content)
            elif file_path.suffix == '.json':
                data = json.loads(content)
            elif file_path.suffix == '.env':
                data = self._parse_env_file(content)
            else:
                self.logger.warning("Unsupported file format", file=str(file_path))
                return
            
            # Process configuration data
            if isinstance(data, dict):
                await self._process_config_data(data, file_path)
            
            self.logger.debug("Configuration file loaded", file=str(file_path))
            
        except Exception as e:
            self.logger.error("Error loading configuration file", 
                            file=str(file_path), 
                            error=str(e))
    
    def _parse_env_file(self, content: str) -> Dict[str, str]:
        """Parse .env file content"""
        data = {}
        for line in content.splitlines():
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                data[key.strip()] = value.strip().strip('"\'')
        return data
    
    async def _process_config_data(self, data: Dict[str, Any], source_path: Path):
        """Process configuration data and create ConfigurationItem objects"""
        def _flatten_dict(d: Dict[str, Any], parent_key: str = '', sep: str = '.') -> Dict[str, Any]:
            """Flatten nested dictionary"""
            items = []
            for k, v in d.items():
                new_key = f"{parent_key}{sep}{k}" if parent_key else k
                if isinstance(v, dict):
                    items.extend(_flatten_dict(v, new_key, sep=sep).items())
                else:
                    items.append((new_key, v))
            return dict(items)
        
        flattened_data = _flatten_dict(data)
        
        for key, value in flattened_data.items():
            # Determine configuration type
            config_type = self._detect_type(value)
            
            # Determine scope based on key or file path
            scope = self._determine_scope(key, source_path)
            
            # Create configuration item
            config_item = ConfigurationItem(
                key=key,
                value=value,
                type=config_type,
                scope=scope,
                source=ConfigurationSource.FILE,
                description=f"Loaded from {source_path.name}"
            )
            
            # Store configuration
            self.configurations[key] = config_item
            
            # Store version if versioning is enabled
            if self.config.versioning_enabled:
                if key not in self.configuration_versions:
                    self.configuration_versions[key] = []
                self.configuration_versions[key].append(config_item)
    
    def _detect_type(self, value: Any) -> ConfigurationType:
        """Detect configuration type from value"""
        if isinstance(value, bool):
            return ConfigurationType.BOOLEAN
        elif isinstance(value, int):
            return ConfigurationType.INTEGER
        elif isinstance(value, float):
            return ConfigurationType.FLOAT
        elif isinstance(value, list):
            return ConfigurationType.LIST
        elif isinstance(value, dict):
            return ConfigurationType.DICT
        elif isinstance(value, str):
            # Check if it's a secret (contains 'password', 'key', 'secret', etc.)
            secret_indicators = ['password', 'key', 'secret', 'token', 'credential']
            if any(indicator in value.lower() for indicator in secret_indicators):
                return ConfigurationType.SECRET
            return ConfigurationType.STRING
        else:
            return ConfigurationType.STRING
    
    def _determine_scope(self, key: str, source_path: Path) -> ConfigurationScope:
        """Determine configuration scope"""
        key_lower = key.lower()
        
        if 'global' in key_lower or 'system' in key_lower:
            return ConfigurationScope.GLOBAL
        elif 'service' in key_lower or source_path.parent.name == 'services':
            return ConfigurationScope.SERVICE
        elif 'env' in key_lower or self.config.environment in str(source_path):
            return ConfigurationScope.ENVIRONMENT
        elif 'user' in key_lower:
            return ConfigurationScope.USER
        else:
            return ConfigurationScope.SERVICE
    
    async def _load_from_environment(self):
        """Load configurations from environment variables"""
        for key, value in os.environ.items():
            if key.startswith('AINFLUE_'):
                # Remove prefix and convert to lowercase with dots
                config_key = key[8:].lower().replace('_', '.')
                
                config_item = ConfigurationItem(
                    key=config_key,
                    value=value,
                    type=self._detect_type(value),
                    scope=ConfigurationScope.ENVIRONMENT,
                    source=ConfigurationSource.ENVIRONMENT,
                    description=f"Environment variable {key}"
                )
                
                self.configurations[config_key] = config_item
    
    async def _load_from_database(self):
        """Load configurations from database (placeholder)"""
        # Implement database loading logic here
        pass
    
    async def _load_from_vault(self):
        """Load configurations from HashiCorp Vault (placeholder)"""
        # Implement Vault loading logic here
        pass
    
    async def _load_from_kubernetes(self):
        """Load configurations from Kubernetes ConfigMaps (placeholder)"""
        # Implement Kubernetes loading logic here
        pass
    
    async def _validate_all_configurations(self):
        """Validate all loaded configurations"""
        validation_errors = []
        
        for key, config_item in self.configurations.items():
            is_valid, error = ConfigurationValidator.validate_item(config_item)
            if not is_valid:
                validation_errors.append(f"{key}: {error}")
        
        if validation_errors:
            error_msg = "Configuration validation failed:\n" + "\n".join(validation_errors)
            self.logger.error("Configuration validation failed", errors=validation_errors)
            raise ValueError(error_msg)
        
        self.logger.info("All configurations validated successfully")
    
    async def _update_cache(self):
        """Update configuration cache"""
        if not self.config.cache_enabled:
            return
        
        self.configuration_cache = {
            key: config_item.value 
            for key, config_item in self.configurations.items()
        }
        
        self.logger.debug("Configuration cache updated", 
                         cache_size=len(self.configuration_cache))
    
    def _is_config_file(self, file_path: Path) -> bool:
        """Check if file is a configuration file"""
        return file_path.suffix in ['.yaml', '.yml', '.json', '.env']
    
    async def _start_file_watcher(self):
        """Start file system watcher"""
        try:
            self.file_handler = ConfigurationFileHandler(self)
            self.file_observer = Observer()
            
            for watch_dir in self.config.watcher_config.watch_directories:
                if os.path.exists(watch_dir):
                    self.file_observer.schedule(
                        self.file_handler,
                        watch_dir,
                        recursive=self.config.watcher_config.recursive
                    )
                    self.logger.info("Watching configuration directory", directory=watch_dir)
            
            self.file_observer.start()
            self.logger.info("File watcher started successfully")
            
        except Exception as e:
            self.logger.error("Failed to start file watcher", error=str(e))
            raise
    
    async def _process_file_change(self, change: ConfigurationChange):
        """Process a file change event"""
        try:
            self.logger.info("Processing configuration file change", 
                           file=change.file_path, 
                           change_type=change.change_type.value)
            
            if change.change_type == ChangeType.DELETED:
                # Handle file deletion
                await self._handle_file_deletion(change.file_path)
            else:
                # Reload file
                await self._reload_config_file(Path(change.file_path))
            
            # Mark change as processed
            change.applied = True
            self.change_history.append(change)
            
            # Notify callbacks
            await self._notify_change_callbacks()
            
            self.last_reload_time = datetime.utcnow()
            
        except Exception as e:
            change.error = str(e)
            self.logger.error("Error processing file change", 
                            file=change.file_path, 
                            error=str(e))
    
    async def _handle_file_deletion(self, file_path: str):
        """Handle configuration file deletion"""
        # Remove configurations that came from this file
        keys_to_remove = [
            key for key, config in self.configurations.items()
            if config.source == ConfigurationSource.FILE and file_path in str(config.source)
        ]
        
        for key in keys_to_remove:
            del self.configurations[key]
            if key in self.configuration_cache:
                del self.configuration_cache[key]
        
        self.logger.info("Removed configurations from deleted file", 
                        file=file_path, 
                        removed_count=len(keys_to_remove))
    
    async def _reload_config_file(self, file_path: Path):
        """Reload a specific configuration file"""
        if file_path.exists() and self._is_config_file(file_path):
            await self._load_config_file(file_path)
            await self._update_cache()
    
    async def _configuration_maintenance_loop(self):
        """Background maintenance loop"""
        while self.is_running:
            try:
                # Clean up old versions if versioning is enabled
                if self.config.versioning_enabled:
                    await self._cleanup_old_versions()
                
                # Process pending changes
                if self.pending_changes:
                    await self._save_pending_changes()
                
                # Cache cleanup
                if self.config.cache_enabled:
                    await self._cleanup_cache()
                
                await asyncio.sleep(300)  # Run every 5 minutes
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error("Error in maintenance loop", error=str(e))
                await asyncio.sleep(60)
    
    async def _cleanup_old_versions(self):
        """Clean up old configuration versions"""
        for key, versions in self.configuration_versions.items():
            if len(versions) > 10:  # Keep last 10 versions
                self.configuration_versions[key] = versions[-10:]
    
    async def _save_pending_changes(self):
        """Save pending changes"""
        if not self.pending_changes:
            return
        
        # Process pending changes
        for change in self.pending_changes:
            self.change_history.append(change)
        
        self.pending_changes.clear()
        self.logger.debug("Pending changes saved")
    
    async def _cleanup_cache(self):
        """Cleanup expired cache entries"""
        # For now, just refresh the entire cache
        await self._update_cache()
    
    async def _notify_change_callbacks(self):
        """Notify registered change callbacks"""
        for callback in self.change_callbacks:
            try:
                # Call callback for each changed configuration
                for key, config in self.configurations.items():
                    if (datetime.utcnow() - config.updated_at).total_seconds() < 60:
                        callback(key, config.value)
            except Exception as e:
                self.logger.error("Error in change callback", error=str(e))
    
    # Public API methods
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        if self.config.cache_enabled and key in self.configuration_cache:
            return self.configuration_cache[key]
        
        config_item = self.configurations.get(key)
        if config_item:
            return config_item.value
        
        return default
    
    def get_all(self, scope: ConfigurationScope = None) -> Dict[str, Any]:
        """Get all configurations, optionally filtered by scope"""
        if scope:
            return {
                key: config.value 
                for key, config in self.configurations.items()
                if config.scope == scope
            }
        
        return {key: config.value for key, config in self.configurations.items()}
    
    async def set(self, key: str, value: Any, scope: ConfigurationScope = ConfigurationScope.SERVICE):
        """Set configuration value"""
        config_item = ConfigurationItem(
            key=key,
            value=value,
            type=self._detect_type(value),
            scope=scope,
            source=ConfigurationSource.DATABASE,  # Programmatically set
            description="Programmatically set value"
        )
        
        # Validate if enabled
        if self.config.validation_enabled:
            is_valid, error = ConfigurationValidator.validate_item(config_item)
            if not is_valid:
                raise ValueError(f"Configuration validation failed: {error}")
        
        # Store configuration
        old_value = self.configurations.get(key)
        self.configurations[key] = config_item
        
        # Update cache
        if self.config.cache_enabled:
            self.configuration_cache[key] = value
        
        # Store version
        if self.config.versioning_enabled:
            if key not in self.configuration_versions:
                self.configuration_versions[key] = []
            self.configuration_versions[key].append(config_item)
        
        # Create change record
        change = ConfigurationChange(
            change_id=f"set_{key}_{int(time.time())}",
            change_type=ChangeType.MODIFIED if old_value else ChangeType.CREATED,
            file_path="programmatic",
            key=key,
            old_value=old_value.value if old_value else None,
            new_value=value,
            source=ConfigurationSource.DATABASE,
            validated=True,
            applied=True
        )
        
        self.change_history.append(change)
        
        # Notify callbacks
        await self._notify_change_callbacks()
        
        self.logger.info("Configuration updated", key=key, value=value)
    
    async def delete(self, key: str):
        """Delete configuration"""
        if key in self.configurations:
            old_config = self.configurations[key]
            del self.configurations[key]
            
            if key in self.configuration_cache:
                del self.configuration_cache[key]
            
            # Create change record
            change = ConfigurationChange(
                change_id=f"delete_{key}_{int(time.time())}",
                change_type=ChangeType.DELETED,
                file_path="programmatic",
                key=key,
                old_value=old_config.value,
                source=ConfigurationSource.DATABASE,
                applied=True
            )
            
            self.change_history.append(change)
            
            self.logger.info("Configuration deleted", key=key)
    
    def exists(self, key: str) -> bool:
        """Check if configuration exists"""
        return key in self.configurations
    
    def get_info(self, key: str) -> Optional[Dict[str, Any]]:
        """Get configuration metadata"""
        config_item = self.configurations.get(key)
        if not config_item:
            return None
        
        return {
            'key': config_item.key,
            'type': config_item.type.value,
            'scope': config_item.scope.value,
            'source': config_item.source.value,
            'description': config_item.description,
            'required': config_item.required,
            'created_at': config_item.created_at,
            'updated_at': config_item.updated_at,
            'version': config_item.version,
            'checksum': config_item.checksum
        }
    
    def get_versions(self, key: str) -> List[Dict[str, Any]]:
        """Get configuration version history"""
        if not self.config.versioning_enabled or key not in self.configuration_versions:
            return []
        
        return [
            {
                'version': i + 1,
                'value': config.value,
                'updated_at': config.updated_at,
                'checksum': config.checksum
            }
            for i, config in enumerate(self.configuration_versions[key])
        ]
    
    def register_change_callback(self, callback: Callable[[str, Any], None]):
        """Register a callback for configuration changes"""
        self.change_callbacks.append(callback)
        self.logger.info("Change callback registered")
    
    async def reload(self):
        """Manually reload all configurations"""
        self.logger.info("Manual configuration reload triggered")
        await self._load_configurations()
        await self._notify_change_callbacks()
        self.last_reload_time = datetime.utcnow()
    
    def get_status(self) -> Dict[str, Any]:
        """Get service status"""
        return {
            'is_running': self.is_running,
            'configuration_count': len(self.configurations),
            'cache_enabled': self.config.cache_enabled,
            'cache_size': len(self.configuration_cache),
            'watcher_enabled': self.config.watcher_config.hot_reload_enabled,
            'last_reload_time': self.last_reload_time,
            'change_history_count': len(self.change_history),
            'pending_changes_count': len(self.pending_changes),
            'environment': self.config.environment
        }
    
    def get_changes(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent configuration changes"""
        recent_changes = self.change_history[-limit:] if self.change_history else []
        return [
            {
                'change_id': change.change_id,
                'change_type': change.change_type.value,
                'file_path': change.file_path,
                'key': change.key,
                'old_value': change.old_value,
                'new_value': change.new_value,
                'timestamp': change.timestamp,
                'source': change.source.value,
                'validated': change.validated,
                'applied': change.applied,
                'error': change.error
            }
            for change in recent_changes
        ]


# Service factory
async def create_unified_configuration_service(config: Dict[str, Any] = None) -> UnifiedConfigurationService:
    """Create and configure a unified configuration service"""
    service_config = UnifiedConfigurationConfig(**(config or {}))
    service = UnifiedConfigurationService(service_config)
    return service


# Main execution
if __name__ == "__main__":
    async def main():
        """Main execution function"""
        # Create configuration service
        service = await create_unified_configuration_service()
        
        try:
            # Start the service
            await service.start()
            
            # Example usage
            await service.set("app.name", "Ainflue")
            await service.set("app.version", "1.0.0")
            
            print(f"App name: {service.get('app.name')}")
            print(f"App version: {service.get('app.version')}")
            print(f"Status: {service.get_status()}")
            
            # Run indefinitely
            while True:
                await asyncio.sleep(1)
                
        except KeyboardInterrupt:
            logger.info("Shutting down configuration service")
        finally:
            await service.stop()
    
    # Run the service
    asyncio.run(main())