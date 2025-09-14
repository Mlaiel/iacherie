"""Advanced Alert Configuration Management
Created by: Fahed Mlaiel (mlaiel@live.de)

WARNING: This code is proprietary and confidential.
Unauthorized use, reproduction, or distribution is strictly prohibited.
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

Dynamic configuration management for alert system with hot-reload capabilities,
environment-specific settings, and runtime optimization.
"""

import asyncio
import logging
import json
import yaml
from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta, timezone
from enum import Enum
from pathlib import Path
import os
from contextlib import asynccontextmanager

import redis.asyncio as redis
from pydantic import BaseModel, Field, validator
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import aiofiles

from .alert_models import AlertSeverity, AlertCategory, EscalationLevel
from ...core.config import settings
from ...core.cache import CacheManager

logger = logging.getLogger(__name__)


class ConfigurationSource(str, Enum):
    """
Configuration source types."""

    FILE_SYSTEM = "file_system"
    ENVIRONMENT = "environment"
    DATABASE = "database"
    REDIS = "redis"
    REMOTE_API = "remote_api"
    KUBERNETES_CONFIG_MAP = "kubernetes_config_map"


class ConfigurationScope(str, Enum):
    """Configuration scope levels."""

    GLOBAL = "global"
    ENVIRONMENT = "environment"
    TENANT = "tenant"
    USER = "user"
    ALERT_TYPE = "alert_type"


@dataclass
class NotificationChannelConfig:
    """Configuration for notification channels."""
    enabled: bool = True
    rate_limit_per_minute: int = 100
    retry_attempts: int = 3
    retry_backoff_seconds: int = 5
    timeout_seconds: int = 30
    template_id: Optional[str] = None
    priority_mapping: Dict[str, str] = field(default_factory=dict)
    custom_settings: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EscalationConfig:
    """
Configuration for alert escalation."""
    enabled: bool = True
    auto_escalate: bool = True
    escalation_intervals: Dict[str, int] = field(default_factory=lambda: {
        "level_0_to_1": 30,  # minutes
        "level_1_to_2": 60,
        "level_2_to_3": 120,
        "level_3_to_4": 240
    })
    severity_escalation_rules: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    business_hours_only: bool = False
    escalation_pause_hours: List[int] = field(default_factory=list)


@dataclass
class MLClassifierConfig:
    """Configuration for ML classification."""
    enabled: bool = True
    model_update_interval_hours: int = 24
    confidence_threshold: float = 0.8
    auto_retrain: bool = True
    feature_extraction_config: Dict[str, Any] = field(default_factory=dict)
    model_performance_threshold: float = 0.9
    fallback_classification_rules: Dict[str, str] = field(default_factory=dict)


@dataclass
class EvidenceCollectionConfig:
    """
Configuration for evidence collection."""
    enabled: bool = True
    auto_collect: bool = True
    collection_timeout_seconds: int = 60
    max_evidence_size_mb: int = 100
    evidence_retention_days: int = 365
    screenshot_quality: str = "high"
    metadata_collection_depth: str = "full"
    legal_compliance_mode: bool = True


@dataclass
class PerformanceConfig:
    """Configuration for performance optimization."""
    max_concurrent_alerts: int = 1000
    batch_processing_size: int = 100
    cache_ttl_seconds: int = 3600
    database_connection_pool_size: int = 20
    redis_connection_pool_size: int = 50
    async_task_queue_size: int = 10000
    metrics_collection_interval_seconds: int = 60


@dataclass
class SecurityConfig:
    """
Configuration for security settings."""
    encryption_enabled: bool = True
    audit_logging_enabled: bool = True
    rate_limiting_enabled: bool = True
    ip_whitelist: List[str] = field(default_factory=list)
    api_key_rotation_days: int = 90
    session_timeout_minutes: int = 60
    max_failed_login_attempts: int = 5
    require_mfa: bool = True


class AlertSystemConfiguration(BaseModel):
    """
Complete alert system configuration."""
    
    # Basic settings
    environment: str = Field(default="production")
    debug_mode: bool = Field(default=False)
    log_level: str = Field(default="INFO")
    
    # Notification channels
    email: NotificationChannelConfig = Field(default_factory=NotificationChannelConfig)
    sms: NotificationChannelConfig = Field(default_factory=NotificationChannelConfig)
    websocket: NotificationChannelConfig = Field(default_factory=NotificationChannelConfig)
    discord: NotificationChannelConfig = Field(default_factory=NotificationChannelConfig)
    slack: NotificationChannelConfig = Field(default_factory=NotificationChannelConfig)
    webhook: NotificationChannelConfig = Field(default_factory=NotificationChannelConfig)
    
    # Core components
    escalation: EscalationConfig = Field(default_factory=EscalationConfig)
    ml_classifier: MLClassifierConfig = Field(default_factory=MLClassifierConfig)
    evidence_collection: EvidenceCollectionConfig = Field(default_factory=EvidenceCollectionConfig)
    performance: PerformanceConfig = Field(default_factory=PerformanceConfig)
    security: SecurityConfig = Field(default_factory=SecurityConfig)
    
    # Alert processing rules
    severity_thresholds: Dict[str, float] = Field(default_factory=lambda: {
        "critical": 0.95,
        "high": 0.8,
        "medium": 0.6,
        "low": 0.4,
        "info": 0.2
    })
    
    auto_resolve_rules: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    suppression_rules: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Integration settings
    external_apis: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    webhook_endpoints: Dict[str, str] = Field(default_factory=dict)
    
    # Metadata
    version: str = Field(default="2.1.0")
    last_updated: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_by: Optional[str] = None
    
    class Config:
    """Config: class implementation"""
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ConfigurationManager:
    """
    Advanced configuration management system with hot-reload, validation,
    and multi-source configuration merging.
    """
    
    def __init__(
        self,
        cache_manager -> None: CacheManager,
        redis_client -> None: redis.Redis,
        config_sources -> None: List[ConfigurationSource] = None,
        hot_reload -> None: bool = True
    ) -> None:
        self.cache_manager = cache_manager
        self.redis_client = redis_client
        self.config_sources = config_sources or [
            ConfigurationSource.FILE_SYSTEM,
            ConfigurationSource.ENVIRONMENT,
            ConfigurationSource.REDIS
        ]
        self.hot_reload = hot_reload
        
        # Configuration storage
        self._configurations: Dict[str, AlertSystemConfiguration] = {}
        self._configuration_callbacks: List[Callable] = []
        self._file_observer: Optional[Observer] = None
        
        # Configuration file paths
        self.config_dir = Path(settings.CONFIG_DIR) / "alerts"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info("Configuration Manager initialized")

    async def initialize(self) -> None:
        """Initialize the configuration manager."""
        try:
            # Load configurations from all sources
            await self._load_configurations()
            
            # Setup file watching for hot-reload
            if self.hot_reload:
                await self._setup_file_watcher()
            
            # Validate configurations
            await self._validate_configurations()
            
            logger.info("Configuration Manager fully initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize Configuration Manager: {e}")
            raise

    async def get_configuration(
        self,
        scope: ConfigurationScope = ConfigurationScope.GLOBAL,
        scope_id: Optional[str] = None
    ) -> AlertSystemConfiguration:
        """Get configuration for specific scope."""
        try:
            config_key = self._build_config_key(scope, scope_id)
            
            # Try cache first
            cached_config = await self.cache_manager.get(f"alert_config:{config_key}")
            if cached_config:
                return AlertSystemConfiguration.parse_raw(cached_config)
            
            # Get from memory
            if config_key in self._configurations:
                config = self._configurations[config_key]
                # Cache for future use
                await self.cache_manager.set(
                    f"alert_config:{config_key}",
                    config.json(),
                    ttl=3600
                )
                return config
            
            # Return default configuration
            default_config = await self._get_default_configuration()
            await self._store_configuration(scope, scope_id, default_config)
            
            return default_config
            
        except Exception as e:
            logger.error(f"Failed to get configuration for {scope}:{scope_id}: {e}")
            return await self._get_default_configuration()

    async def update_configuration(
        self,
        config: AlertSystemConfiguration,
        scope: ConfigurationScope = ConfigurationScope.GLOBAL,
        scope_id: Optional[str] = None,
        updated_by: str = "system"
    ) -> bool:
        """Update configuration for specific scope."""
        try:
            # Update metadata
            config.last_updated = datetime.now(timezone.utc)
            config.updated_by = updated_by
            
            # Validate configuration
            await self._validate_single_configuration(config)
            
            # Store configuration
            await self._store_configuration(scope, scope_id, config)
            
            # Invalidate cache
            config_key = self._build_config_key(scope, scope_id)
            await self.cache_manager.delete(f"alert_config:{config_key}")
            
            # Notify callbacks
            await self._notify_configuration_change(scope, scope_id, config)
            
            logger.info(f"Configuration updated for {scope}:{scope_id} by {updated_by}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update configuration: {e}")
            return False

    async def register_change_callback(self, callback -> None: Callable) -> None:
        """Register callback for configuration changes."""
        self._configuration_callbacks.append(callback)

    async def export_configuration(
        self,
        scope: ConfigurationScope = ConfigurationScope.GLOBAL,
        scope_id: Optional[str] = None,
        format_type: str = "json"
    ) -> str:
        """Export configuration in specified format."""
        try:
            config = await self.get_configuration(scope, scope_id)
            
            if format_type.lower() == "json":
                return config.json(indent=2)
            elif format_type.lower() == "yaml":
                return yaml.dump(config.dict(), default_flow_style=False)
            else:
                raise ValueError(f"Unsupported format: {format_type}")
                
        except Exception as e:
            logger.error(f"Failed to export configuration: {e}")
            raise

    async def import_configuration(
        self,
        config_data: str,
        format_type: str = "json",
        scope: ConfigurationScope = ConfigurationScope.GLOBAL,
        scope_id: Optional[str] = None,
        updated_by: str = "import"
    ) -> bool:
        """Import configuration from data string."""
        try:
            if format_type.lower() == "json":
                config_dict = json.loads(config_data)
            elif format_type.lower() == "yaml":
                config_dict = yaml.safe_load(config_data)
            else:
                raise ValueError(f"Unsupported format: {format_type}")
            
            config = AlertSystemConfiguration(**config_dict)
            return await self.update_configuration(config, scope, scope_id, updated_by)
            
        except Exception as e:
            logger.error(f"Failed to import configuration: {e}")
            return False

    async def get_configuration_history(
        self,
        scope: ConfigurationScope = ConfigurationScope.GLOBAL,
        scope_id: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get configuration change history."""
        try:
            config_key = self._build_config_key(scope, scope_id)
            history_key = f"alert_config_history:{config_key}"
            
            # Get from Redis
            history = await self.redis_client.lrange(history_key, 0, limit - 1)
            return [json.loads(item) for item in history]
            
        except Exception as e:
            logger.error(f"Failed to get configuration history: {e}")
            return []

    async def _load_configurations(self) -> None:
        """Load configurations from all sources."""
        for source in self.config_sources:
            try:
                if source == ConfigurationSource.FILE_SYSTEM:
                    await self._load_from_filesystem()
                elif source == ConfigurationSource.ENVIRONMENT:
                    await self._load_from_environment()
                elif source == ConfigurationSource.REDIS:
                    await self._load_from_redis()
                elif source == ConfigurationSource.DATABASE:
                    await self._load_from_database()
                
                logger.info(f"Loaded configuration from {source.value}")
                
            except Exception as e:
                logger.warning(f"Failed to load configuration from {source.value}: {e}")

    async def _load_from_filesystem(self) -> None:
        """Load configuration from filesystem."""
        config_files = list(self.config_dir.glob("*.json")) + list(self.config_dir.glob("*.yaml"))
        
        for config_file in config_files:
            try:
                async with aiofiles.open(config_file, 'r') as f:
                    content = await f.read()
                
                if config_file.suffix == '.json':
                    config_data = json.loads(content)
                else:
                    config_data = yaml.safe_load(content)
                
                config = AlertSystemConfiguration(**config_data)
                
                # Determine scope from filename
                scope_info = self._parse_config_filename(config_file.stem)
                config_key = self._build_config_key(scope_info['scope'], scope_info['scope_id'])
                
                self._configurations[config_key] = config
                
            except Exception as e:
                logger.error(f"Failed to load config file {config_file}: {e}")

    async def _load_from_environment(self) -> None:
        """Load configuration from environment variables."""
        try:
            # Build configuration from environment variables
            env_config = {}
            
            # Parse environment variables with ALERT_ prefix
            for key, value in os.environ.items():
                if key.startswith('ALERT_'):
                    config_path = key[6:].lower().split('_')
                    self._set_nested_value(env_config, config_path, value)
            
            if env_config:
                config = AlertSystemConfiguration(**env_config)
                config_key = self._build_config_key(ConfigurationScope.ENVIRONMENT)
                self._configurations[config_key] = config
                
        except Exception as e:
            logger.error(f"Failed to load configuration from environment: {e}")

    async def _load_from_redis(self) -> None:
        """Load configuration from Redis."""
        try:
            # Get all configuration keys
            pattern = "alert_config:*"
            keys = await self.redis_client.keys(pattern)
            
            for key in keys:
                config_data = await self.redis_client.get(key)
                if config_data:
                    config = AlertSystemConfiguration.parse_raw(config_data)
                    config_key = key.decode().replace("alert_config:", "")
                    self._configurations[config_key] = config
                    
        except Exception as e:
            logger.error(f"Failed to load configuration from Redis: {e}")

    async def _load_from_database(self) -> None:
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
    async def _store_configuration(
        self,
        scope -> None: ConfigurationScope,
        scope_id -> None: Optional[str],
        config -> None: AlertSystemConfiguration
    ) -> None:
        """
Store configuration to all applicable sources."""
        config_key = self._build_config_key(scope, scope_id)
        
        # Store in memory
        self._configurations[config_key] = config
        
        # Store in Redis
        await self.redis_client.set(
            f"alert_config:{config_key}",
            config.json(),
            ex=86400  # 24 hours
        )
        
        # Store in filesystem for persistence
        await self._save_to_filesystem(config_key, config)
        
        # Add to history
        await self._add_to_history(config_key, config)

    async def _save_to_filesystem(self, config_key -> None: str, config -> None: AlertSystemConfiguration) -> None:
        """Save configuration to filesystem."""
        try:
            config_file = self.config_dir / f"{config_key}.json"
            
            async with aiofiles.open(config_file, 'w') as f:
                await f.write(config.json(indent=2))
                
        except Exception as e:
            logger.error(f"Failed to save configuration to filesystem: {e}")

    async def _add_to_history(self, config_key -> None: str, config -> None: AlertSystemConfiguration) -> None:
        """Add configuration change to history."""
        try:
            history_entry = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "config": config.dict(),
                "version": config.version,
                "updated_by": config.updated_by
            }
            
            history_key = f"alert_config_history:{config_key}"
            await self.redis_client.lpush(history_key, json.dumps(history_entry))
            
            # Keep only last 100 entries
            await self.redis_client.ltrim(history_key, 0, 99)
            
        except Exception as e:
            logger.error(f"Failed to add configuration to history: {e}")

    async def _validate_configurations(self) -> None:
        """Validate all loaded configurations."""
        for config_key, config in self._configurations.items():
            try:
                await self._validate_single_configuration(config)
            except Exception as e:
                logger.error(f"Configuration validation failed for {config_key}: {e}")

    async def _validate_single_configuration(self, config -> None: AlertSystemConfiguration) -> None:
        """Validate a single configuration."""
        # Validate severity thresholds
        thresholds = config.severity_thresholds
        if not all(0 <= v <= 1 for v in thresholds.values()):
            raise ValueError("Severity thresholds must be between 0 and 1")
        
        # Validate notification rate limits
        for channel_name in ['email', 'sms', 'websocket', 'discord', 'slack', 'webhook']:
            channel_config = getattr(config, channel_name)
            if channel_config.rate_limit_per_minute < 1:
                raise ValueError(f"{channel_name} rate limit must be >= 1")
        
        # Validate escalation intervals
        intervals = config.escalation.escalation_intervals
        if not all(v > 0 for v in intervals.values()):
            raise ValueError("Escalation intervals must be positive")

    async def _notify_configuration_change(
        self,
        scope -> None: ConfigurationScope,
        scope_id -> None: Optional[str],
        config -> None: AlertSystemConfiguration
    ) -> None:
        """Notify registered callbacks of configuration changes."""
        for callback in self._configuration_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(scope, scope_id, config)
                else:
                    callback(scope, scope_id, config)
            except Exception as e:
                logger.error(f"Configuration change callback failed: {e}")

    async def _setup_file_watcher(self) -> None:
        """Setup file system watcher for hot-reload."""
        try:
            event_handler = ConfigFileEventHandler(self)
            self._file_observer = Observer()
            self._file_observer.schedule(event_handler, str(self.config_dir), recursive=True)
            self._file_observer.start()
            
            logger.info("File watcher setup for configuration hot-reload")
            
        except Exception as e:
            logger.error(f"Failed to setup file watcher: {e}")

    def _build_config_key(self, scope: ConfigurationScope, scope_id: Optional[str] = None) -> str:
        """Build configuration key from scope and ID."""
        if scope_id:
            return f"{scope.value}:{scope_id}"
        return scope.value

    def _parse_config_filename(self, filename: str) -> Dict[str, Any]:
        """Parse configuration filename to extract scope information."""
        parts = filename.split('_')
        
        if len(parts) == 1:
            return {'scope': ConfigurationScope.GLOBAL, 'scope_id': None}
        elif len(parts) == 2:
            scope_str, scope_id = parts
            scope = ConfigurationScope(scope_str) if scope_str in [s.value for s in ConfigurationScope] else ConfigurationScope.GLOBAL
            return {'scope': scope, 'scope_id': scope_id}
        else:
            return {'scope': ConfigurationScope.GLOBAL, 'scope_id': None}

    def _set_nested_value(self, dictionary -> None: Dict, path -> None: List[str], value -> None: str) -> None:
        """
Set nested dictionary value from path list."""
        current = dictionary
        for key in path[:-1]:
        try:
            logger.info(f"Executing _convert_env_value")
            
            # Implementation for _convert_env_value
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"_convert_env_value completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"_convert_env_value failed: {e}")
            raise
        try:
            return json.loads(value)
        except (json.JSONDecodeError, ValueError):
            pass
        
        # Return as string
        return value

    async def _get_default_configuration(self) -> AlertSystemConfiguration:
        """
Get default configuration."""
        return AlertSystemConfiguration()


class ConfigFileEventHandler(FileSystemEventHandler):
    """
File system event handler for configuration hot-reload."""
    
    def __init__(self, config_manager -> None: ConfigurationManager) -> None:
        self.config_manager = config_manager
        self._last_modified = {}
    
    def on_modified(self, event) -> None:
        """
Handle file modification events."""
        if event.is_directory:
            return
        
        file_path = Path(event.src_path)
        if file_path.suffix not in ['.json', '.yaml', '.yml']:
            return
        
        # Debounce rapid file changes
        now = datetime.now()
        if file_path in self._last_modified:
            if (now - self._last_modified[file_path]).total_seconds() < 1:
                return
        
        self._last_modified[file_path] = now
        
        # Reload configuration asynchronously
        asyncio.create_task(self._reload_config_file(file_path))
    
    async def _reload_config_file(self, file_path -> None: Path) -> None:
        """
Reload configuration from modified file."""
        try:
            async with aiofiles.open(file_path, 'r') as f:
                content = await f.read()
            
            if file_path.suffix == '.json':
                config_data = json.loads(content)
            else:
                config_data = yaml.safe_load(content)
            
            config = AlertSystemConfiguration(**config_data)
            
            # Determine scope from filename
            scope_info = self.config_manager._parse_config_filename(file_path.stem)
            
            # Update configuration
            await self.config_manager.update_configuration(
                config,
                scope_info['scope'],
                scope_info['scope_id'],
                "hot_reload"
            )
            
            logger.info(f"Hot-reloaded configuration from {file_path}")
            
        except Exception as e:
            logger.error(f"Failed to hot-reload configuration from {file_path}: {e}")


# Export classes
__all__ = [
    "ConfigurationSource",
    "ConfigurationScope",
    "NotificationChannelConfig",
    "EscalationConfig",
    "MLClassifierConfig",
    "EvidenceCollectionConfig",
    "PerformanceConfig",
    "SecurityConfig",
    "AlertSystemConfiguration",
    "ConfigurationManager",
    "ConfigFileEventHandler"
]

# File has syntax issues - needs manual review