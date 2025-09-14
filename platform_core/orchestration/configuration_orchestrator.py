"""
Configuration Orchestrator module
Enterprise implementation for Ainflue platform
"""

#!/usr/bin/env python3
"""
Configuration Orchestrator - Enterprise Core Component
Centralized configuration management with environment-specific handling

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel. All rights reserved.
Licensed under Enterprise Commercial License.

This module provides comprehensive configuration orchestration including:
- Centralized configuration management
- Environment-specific configuration handling
- Dynamic configuration updates
- Configuration validation and enforcement
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Callable, Set
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import json
import yaml
import os
from pathlib import Path
import hashlib
from abc import ABC, abstractmethod

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ConfigScope(Enum):
    """Configuration scope enumeration"""
    GLOBAL = "global"
    SERVICE = "service"
    TENANT = "tenant"
    USER = "user"
    ENVIRONMENT = "environment"


class ConfigFormat(Enum):
    """Configuration format enumeration"""
    JSON = "json"
    YAML = "yaml"
    PROPERTIES = "properties"
    ENV = "env"


class ConfigStatus(Enum):
    """Configuration status"""
    ACTIVE = "active"
    PENDING = "pending"
    DEPRECATED = "deprecated"
    INVALID = "invalid"


@dataclass
class ConfigValue:
    """Configuration value with metadata"""
    key: str
    value: Any
    scope: ConfigScope
    data_type: str
    description: Optional[str] = None
    default_value: Any = None
    required: bool = False
    sensitive: bool = False
    validation_rules: Dict[str, Any] = field(default_factory=dict)
    tags: Set[str] = field(default_factory=set)
    last_updated: datetime = field(default_factory=datetime.utcnow)
    updated_by: Optional[str] = None


@dataclass
class ConfigEnvironment:
    """Environment configuration definition"""
    environment_id: str
    name: str
    description: str
    base_configs: Dict[str, Any] = field(default_factory=dict)
    overrides: Dict[str, Any] = field(default_factory=dict)
    secrets: Dict[str, str] = field(default_factory=dict)
    active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ConfigProfile:
    """Configuration profile for different deployments"""
    profile_id: str
    name: str
    environment: str
    service_configs: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    feature_flags: Dict[str, bool] = field(default_factory=dict)
    resource_limits: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ConfigChange:
    """Configuration change tracking"""
    change_id: str
    config_key: str
    old_value: Any
    new_value: Any
    scope: ConfigScope
    changed_by: str
    change_reason: Optional[str] = None
    approved_by: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    rollback_available: bool = True


class ConfigProvider(ABC):
    """Abstract configuration provider interface"""
    
    @abstractmethod
    async def get_config(self, key: str, scope: ConfigScope = ConfigScope.GLOBAL) -> Optional[Any]:
        """Get configuration value"""
        pass
    
    @abstractmethod
    async def set_config(self, key: str, value: Any, scope: ConfigScope = ConfigScope.GLOBAL) -> bool:
        """Set configuration value"""
        pass
    
    @abstractmethod
    async def delete_config(self, key: str, scope: ConfigScope = ConfigScope.GLOBAL) -> bool:
        """Delete configuration value"""
        pass
    
    @abstractmethod
    async def list_configs(self, scope: Optional[ConfigScope] = None) -> Dict[str, Any]:
        """List all configurations"""
        pass


class FileConfigProvider(ConfigProvider):
    """File-based configuration provider"""
    
    def __init__(self, config_dir -> None: str = "config") -> None:
        self.config_dir = Path(config_dir)
        self.configs: Dict[str, Dict[str, Any]] = {}
        self._load_configs()
    
    def _load_configs(self) -> None:
        """Load configurations from files"""
        try:
            self.config_dir.mkdir(exist_ok=True)
            
            for scope in ConfigScope:
                config_file = self.config_dir / f"{scope.value}.yaml"
                if config_file.exists():
                    with open(config_file, 'r') as f:
                        self.configs[scope.value] = yaml.safe_load(f) or {}
                else:
                    self.configs[scope.value] = {}
                    
        except Exception as e:
            logger.error(f"Failed to load configurations: {e}")
            for scope in ConfigScope:
                self.configs[scope.value] = {}
    
    def _save_configs(self) -> None:
        """Save configurations to files"""
        try:
            for scope_name, config_data in self.configs.items():
                config_file = self.config_dir / f"{scope_name}.yaml"
                with open(config_file, 'w') as f:
                    yaml.safe_dump(config_data, f, default_flow_style=False)
        except Exception as e:
            logger.error(f"Failed to save configurations: {e}")
    
    async def get_config(self, key: str, scope: ConfigScope = ConfigScope.GLOBAL) -> Optional[Any]:
        """Get configuration value"""
        return self.configs.get(scope.value, {}).get(key)
    
    async def set_config(self, key: str, value: Any, scope: ConfigScope = ConfigScope.GLOBAL) -> bool:
        """Set configuration value"""
        try:
            if scope.value not in self.configs:
                self.configs[scope.value] = {}
            
            self.configs[scope.value][key] = value
            self._save_configs()
            return True
        except Exception as e:
            logger.error(f"Failed to set config {key}: {e}")
            return False
    
    async def delete_config(self, key: str, scope: ConfigScope = ConfigScope.GLOBAL) -> bool:
        """Delete configuration value"""
        try:
            if scope.value in self.configs and key in self.configs[scope.value]:
                del self.configs[scope.value][key]
                self._save_configs()
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to delete config {key}: {e}")
            return False
    
    async def list_configs(self, scope: Optional[ConfigScope] = None) -> Dict[str, Any]:
        """List all configurations"""
        if scope:
            return self.configs.get(scope.value, {})
        return self.configs


class ConfigurationOrchestrator:
    """
    Enterprise Configuration Orchestrator
    
    Provides centralized configuration management with environment-specific
    handling, dynamic updates, validation, and enforcement for enterprise-grade
    configuration orchestration across the entire platform.
    """
    
    def __init__(self, provider -> None: Optional[ConfigProvider] = None, config -> None: Optional[Dict[str, Any]] = None) -> None:
        self.config = config or {}
        self.provider = provider or FileConfigProvider()
        self.environments: Dict[str, ConfigEnvironment] = {}
        self.profiles: Dict[str, ConfigProfile] = {}
        self.config_values: Dict[str, ConfigValue] = {}
        self.change_history: List[ConfigChange] = []
        self.watchers: Dict[str, List[Callable]] = {}
        self.validation_rules: Dict[str, Dict[str, Any]] = {}
        
        # Configuration
        self._refresh_interval = self.config.get('refresh_interval', 60)
        self._change_retention_days = self.config.get('change_retention_days', 90)
        self._validation_enabled = self.config.get('validation_enabled', True)
        self._auto_backup = self.config.get('auto_backup', True)
        self._encryption_enabled = self.config.get('encryption_enabled', True)
        
        # Background tasks
        self._refresh_task: Optional[asyncio.Task] = None
        self._cleanup_task: Optional[asyncio.Task] = None
        self._backup_task: Optional[asyncio.Task] = None
        self._shutdown_event = asyncio.Event()
        
        # Initialize default validation rules
        self._initialize_validation_rules()
        
        logger.info("Configuration Orchestrator initialized")
    
    async def start(self) -> None:
        """Start the configuration orchestrator"""
        try:
            logger.info("Starting Configuration Orchestrator...")
            
            # Load initial configurations
            await self._load_initial_configurations()
            
            # Initialize default environments
            await self._initialize_default_environments()
            
            # Start background tasks
            self._refresh_task = asyncio.create_task(self._refresh_loop())
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())
            if self._auto_backup:
                self._backup_task = asyncio.create_task(self._backup_loop())
            
            logger.info("Configuration Orchestrator started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start Configuration Orchestrator: {e}")
            raise
    
    async def stop(self) -> None:
        """Stop the configuration orchestrator"""
        try:
            logger.info("Stopping Configuration Orchestrator...")
            
            # Signal shutdown
            self._shutdown_event.set()
            
            # Cancel background tasks
            if self._refresh_task:
                self._refresh_task.cancel()
            if self._cleanup_task:
                self._cleanup_task.cancel()
            if self._backup_task:
                self._backup_task.cancel()
            
            # Save final state
            await self._save_configurations()
            
            logger.info("Configuration Orchestrator stopped")
            
        except Exception as e:
            logger.error(f"Error stopping Configuration Orchestrator: {e}")
    
    # Configuration Management
    async def get_config(self, key: str, scope: ConfigScope = ConfigScope.GLOBAL, 
                        environment: Optional[str] = None, default: Any = None) -> Any:
        """Get configuration value with scope and environment consideration"""
        try:
            # Check environment-specific overrides first
            if environment and environment in self.environments:
                env_config = self.environments[environment]
                if key in env_config.overrides:
                    return env_config.overrides[key]
                if key in env_config.base_configs:
                    return env_config.base_configs[key]
            
            # Check scope-specific configuration
            value = await self.provider.get_config(key, scope)
            if value is not None:
                return value
            
            # Check if we have a ConfigValue with default
            if key in self.config_values:
                config_value = self.config_values[key]
                if config_value.default_value is not None:
                    return config_value.default_value
            
            return default
            
        except Exception as e:
            logger.error(f"Failed to get config {key}: {e}")
            return default
    
    async def set_config(self, key: str, value: Any, scope: ConfigScope = ConfigScope.GLOBAL,
                        environment: Optional[str] = None, updated_by: Optional[str] = None,
                        change_reason: Optional[str] = None) -> bool:
        """Set configuration value with validation and change tracking"""
        try:
            # Get current value for change tracking
            current_value = await self.get_config(key, scope, environment)
            
            # Validate new value
            if self._validation_enabled and not await self._validate_config_value(key, value):
                logger.error(f"Configuration validation failed for {key}")
                return False
            
            # Set configuration
            if environment and environment in self.environments:
                # Set in environment overrides
                self.environments[environment].overrides[key] = value
            else:
                # Set in provider
                success = await self.provider.set_config(key, value, scope)
                if not success:
                    return False
            
            # Update config value metadata
            if key not in self.config_values:
                self.config_values[key] = ConfigValue(
                    key=key,
                    value=value,
                    scope=scope,
                    data_type=type(value).__name__
                )
            else:
                self.config_values[key].value = value
                self.config_values[key].last_updated = datetime.utcnow()
                self.config_values[key].updated_by = updated_by
            
            # Track change
            change = ConfigChange(
                change_id=str(uuid.uuid4()),
                config_key=key,
                old_value=current_value,
                new_value=value,
                scope=scope,
                changed_by=updated_by or "system",
                change_reason=change_reason
            )
            
            self.change_history.append(change)
            
            # Notify watchers
            await self._notify_watchers(key, value, current_value)
            
            logger.info(f"Configuration updated: {key} = {value} (scope: {scope.value})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to set config {key}: {e}")
            return False
    
    async def delete_config(self, key: str, scope: ConfigScope = ConfigScope.GLOBAL,
                           environment: Optional[str] = None, deleted_by: Optional[str] = None) -> bool:
        """Delete configuration value"""
        try:
            # Get current value for change tracking
            current_value = await self.get_config(key, scope, environment)
            
            if environment and environment in self.environments:
                # Remove from environment overrides
                self.environments[environment].overrides.pop(key, None)
            else:
                # Remove from provider
                success = await self.provider.delete_config(key, scope)
                if not success:
                    return False
            
            # Remove config value metadata
            if key in self.config_values:
                del self.config_values[key]
            
            # Track change
            change = ConfigChange(
                change_id=str(uuid.uuid4()),
                config_key=key,
                old_value=current_value,
                new_value=None,
                scope=scope,
                changed_by=deleted_by or "system",
                change_reason="Configuration deleted"
            )
            
            self.change_history.append(change)
            
            # Notify watchers
            await self._notify_watchers(key, None, current_value)
            
            logger.info(f"Configuration deleted: {key} (scope: {scope.value})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete config {key}: {e}")
            return False
    
    # Environment Management
    async def create_environment(self, environment: ConfigEnvironment) -> bool:
        """Create a new configuration environment"""
        try:
            self.environments[environment.environment_id] = environment
            logger.info(f"Environment created: {environment.environment_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create environment {environment.environment_id}: {e}")
            return False
    
    async def get_environment(self, environment_id: str) -> Optional[ConfigEnvironment]:
        """Get environment configuration"""
        return self.environments.get(environment_id)
    
    async def list_environments(self) -> List[ConfigEnvironment]:
        """List all environments"""
        return list(self.environments.values())
    
    async def update_environment(self, environment_id: str, updates: Dict[str, Any]) -> bool:
        """Update environment configuration"""
        try:
            if environment_id not in self.environments:
                return False
            
            environment = self.environments[environment_id]
            
            if 'base_configs' in updates:
                environment.base_configs.update(updates['base_configs'])
            if 'overrides' in updates:
                environment.overrides.update(updates['overrides'])
            if 'secrets' in updates:
                environment.secrets.update(updates['secrets'])
            if 'active' in updates:
                environment.active = updates['active']
            
            logger.info(f"Environment updated: {environment_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update environment {environment_id}: {e}")
            return False
    
    # Profile Management
    async def create_profile(self, profile: ConfigProfile) -> bool:
        """Create a configuration profile"""
        try:
            self.profiles[profile.profile_id] = profile
            logger.info(f"Profile created: {profile.profile_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create profile {profile.profile_id}: {e}")
            return False
    
    async def get_profile_config(self, profile_id: str, service_id: Optional[str] = None) -> Dict[str, Any]:
        """Get configuration for a specific profile"""
        try:
            if profile_id not in self.profiles:
                return {}
            
            profile = self.profiles[profile_id]
            config = {}
            
            # Add environment base configs
            if profile.environment in self.environments:
                env = self.environments[profile.environment]
                config.update(env.base_configs)
                config.update(env.overrides)
            
            # Add service-specific configs
            if service_id and service_id in profile.service_configs:
                config.update(profile.service_configs[service_id])
            
            # Add feature flags
            config['feature_flags'] = profile.feature_flags
            
            # Add resource limits
            config['resource_limits'] = profile.resource_limits
            
            return config
            
        except Exception as e:
            logger.error(f"Failed to get profile config {profile_id}: {e}")
            return {}
    
    # Watchers and Notifications
    async def watch_config(self, key: str, callback: Callable[[str, Any, Any], None]) -> bool:
        """Watch for configuration changes"""
        try:
            if key not in self.watchers:
                self.watchers[key] = []
            
            self.watchers[key].append(callback)
            logger.info(f"Watcher registered for config: {key}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register watcher for {key}: {e}")
            return False
    
    async def unwatch_config(self, key: str, callback: Callable) -> bool:
        """Remove configuration watcher"""
        try:
            if key in self.watchers:
                try:
                    self.watchers[key].remove(callback)
                    logger.info(f"Watcher removed for config: {key}")
                    return True
                except ValueError:
                    pass
            return False
            
        except Exception as e:
            logger.error(f"Failed to remove watcher for {key}: {e}")
            return False
    
    # Validation
    def add_validation_rule(self, key: str, rule_type: str, rule_config: Dict[str, Any]) -> None:
        """Add validation rule for a configuration key"""
        if key not in self.validation_rules:
            self.validation_rules[key] = {}
        
        self.validation_rules[key][rule_type] = rule_config
        logger.info(f"Validation rule added for {key}: {rule_type}")
    
    async def _validate_config_value(self, key: str, value: Any) -> bool:
        """Validate configuration value against rules"""
        try:
            if key not in self.validation_rules:
                return True
            
            rules = self.validation_rules[key]
            
            for rule_type, rule_config in rules.items():
                if rule_type == "type":
                    expected_type = rule_config.get("type")
                    if expected_type and not isinstance(value, expected_type):
                        logger.error(f"Type validation failed for {key}: expected {expected_type}, got {type(value)}")
                        return False
                
                elif rule_type == "range":
                    min_val = rule_config.get("min")
                    max_val = rule_config.get("max")
                    if min_val is not None and value < min_val:
                        logger.error(f"Range validation failed for {key}: value {value} < min {min_val}")
                        return False
                    if max_val is not None and value > max_val:
                        logger.error(f"Range validation failed for {key}: value {value} > max {max_val}")
                        return False
                
                elif rule_type == "choices":
                    choices = rule_config.get("choices", [])
                    if choices and value not in choices:
                        logger.error(f"Choice validation failed for {key}: value {value} not in {choices}")
                        return False
                
                elif rule_type == "pattern":
                    import re
                    pattern = rule_config.get("pattern")
                    if pattern and isinstance(value, str):
                        if not re.match(pattern, value):
                            logger.error(f"Pattern validation failed for {key}: value {value} doesn't match {pattern}")
                            return False
            
            return True
            
        except Exception as e:
            logger.error(f"Validation error for {key}: {e}")
            return False
    
    # Change Management
    async def get_change_history(self, key: Optional[str] = None, limit: int = 100) -> List[ConfigChange]:
        """Get configuration change history"""
        try:
            history = self.change_history
            
            if key:
                history = [change for change in history if change.config_key == key]
            
            # Sort by timestamp (newest first) and limit
            history.sort(key=lambda x: x.timestamp, reverse=True)
            return history[:limit]
            
        except Exception as e:
            logger.error(f"Failed to get change history: {e}")
            return []
    
    async def rollback_change(self, change_id: str, rolled_back_by: Optional[str] = None) -> bool:
        """Rollback a configuration change"""
        try:
            # Find the change
            change = None
            for c in self.change_history:
                if c.change_id == change_id:
                    change = c
                    break
            
            if not change or not change.rollback_available:
                logger.error(f"Change {change_id} not found or not rollback-able")
                return False
            
            # Perform rollback
            if change.old_value is not None:
                success = await self.set_config(
                    change.config_key,
                    change.old_value,
                    change.scope,
                    updated_by=rolled_back_by,
                    change_reason=f"Rollback of change {change_id}"
                )
            else:
                success = await self.delete_config(
                    change.config_key,
                    change.scope,
                    deleted_by=rolled_back_by
                )
            
            if success:
                change.rollback_available = False
                logger.info(f"Configuration change rolled back: {change_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to rollback change {change_id}: {e}")
            return False
    
    # Status and Reports
    async def get_configuration_status(self) -> Dict[str, Any]:
        """Get overall configuration status"""
        try:
            status = {
                "total_configs": len(self.config_values),
                "environments": len(self.environments),
                "profiles": len(self.profiles),
                "watchers": sum(len(w) for w in self.watchers.values()),
                "recent_changes": len([c for c in self.change_history 
                                    if (datetime.utcnow() - c.timestamp).days < 7]),
                "validation_enabled": self._validation_enabled,
                "auto_backup": self._auto_backup,
                "configs_by_scope": {},
                "last_updated": datetime.utcnow().isoformat()
            }
            
            # Count configs by scope
            for scope in ConfigScope:
                configs = await self.provider.list_configs(scope)
                status["configs_by_scope"][scope.value] = len(configs)
            
            return status
            
        except Exception as e:
            logger.error(f"Failed to get configuration status: {e}")
            return {"error": str(e)}
    
    # Internal Methods
    def _initialize_validation_rules(self) -> None:
        """Initialize default validation rules"""
        try:
            # Database connection validation
            self.add_validation_rule("database_url", "pattern", {
                "pattern": r"^(postgresql|mysql|sqlite)://.*"
            })
            
            # Port number validation
            self.add_validation_rule("port", "range", {
                "min": 1,
                "max": 65535
            })
            
            # Log level validation
            self.add_validation_rule("log_level", "choices", {
                "choices": ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
            })
            
            # Environment validation
            self.add_validation_rule("environment", "choices", {
                "choices": ["development", "staging", "production"]
            })
            
            logger.info("Default validation rules initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize validation rules: {e}")
    
    async def _load_initial_configurations(self) -> None:
        """Load initial configurations from provider"""
        try:
            for scope in ConfigScope:
                configs = await self.provider.list_configs(scope)
                for key, value in configs.items():
                    self.config_values[key] = ConfigValue(
                        key=key,
                        value=value,
                        scope=scope,
                        data_type=type(value).__name__
                    )
            
            logger.info("Initial configurations loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load initial configurations: {e}")
    
    async def _initialize_default_environments(self) -> None:
        """Initialize default environments"""
        try:
            # Development environment
            dev_env = ConfigEnvironment(
                environment_id="development",
                name="Development Environment",
                description="Local development configuration",
                base_configs={
                    "debug": True,
                    "log_level": "DEBUG",
                    "database_url": "sqlite:///dev.db"
                }
            )
            
            await self.create_environment(dev_env)
            
            # Production environment
            prod_env = ConfigEnvironment(
                environment_id="production",
                name="Production Environment",
                description="Production configuration",
                base_configs={
                    "debug": False,
                    "log_level": "INFO",
                    "database_url": os.getenv("DATABASE_URL", "postgresql://localhost/proddb")
                }
            )
            
            await self.create_environment(prod_env)
            
            logger.info("Default environments initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize default environments: {e}")
    
    async def _notify_watchers(self, key: str, new_value: Any, old_value: Any) -> None:
        """Notify watchers of configuration changes"""
        try:
            if key in self.watchers:
                for callback in self.watchers[key]:
                    try:
                        if asyncio.iscoroutinefunction(callback):
                            await callback(key, new_value, old_value)
                        else:
                            callback(key, new_value, old_value)
                    except Exception as e:
                        logger.error(f"Watcher callback failed for {key}: {e}")
                        
        except Exception as e:
            logger.error(f"Failed to notify watchers for {key}: {e}")
    
    async def _save_configurations(self) -> None:
        """Save current configuration state"""
        try:
            # Save through provider (implementation dependent)
            logger.debug("Configuration state saved")
            
        except Exception as e:
            logger.error(f"Failed to save configurations: {e}")
    
    async def _refresh_loop(self) -> None:
        """Background configuration refresh loop"""
        while not self._shutdown_event.is_set():
            try:
                # Refresh configurations from external sources
                # This could include checking for file changes, database updates, etc.
                await asyncio.sleep(self._refresh_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Refresh loop error: {e}")
                await asyncio.sleep(30)
    
    async def _cleanup_loop(self) -> None:
        """Background cleanup loop for old changes"""
        while not self._shutdown_event.is_set():
            try:
                cutoff_date = datetime.utcnow() - timedelta(days=self._change_retention_days)
                
                # Clean up old change history
                self.change_history = [
                    change for change in self.change_history
                    if change.timestamp > cutoff_date
                ]
                
                await asyncio.sleep(3600)  # Run every hour
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Cleanup loop error: {e}")
                await asyncio.sleep(1800)
    
    async def _backup_loop(self) -> None:
        """Background configuration backup loop"""
        while not self._shutdown_event.is_set():
            try:
                if self._auto_backup:
                    # Create configuration backup
                    backup_data = {
                        "timestamp": datetime.utcnow().isoformat(),
                        "environments": {k: v.__dict__ for k, v in self.environments.items()},
                        "profiles": {k: v.__dict__ for k, v in self.profiles.items()},
                        "config_values": {k: v.__dict__ for k, v in self.config_values.items()}
                    }
                    
                    # Save backup (implementation specific)
                    logger.debug("Configuration backup created")
                
                await asyncio.sleep(86400)  # Daily backup
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Backup loop error: {e}")
                await asyncio.sleep(3600)
    
    # Context Manager Support
    async def __aenter__(self) -> None:
        await self.start()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.stop()


# Factory function
def create_configuration_orchestrator(provider: Optional[ConfigProvider] = None, config: Optional[Dict[str, Any]] = None) -> ConfigurationOrchestrator:
    """Factory function to create a Configuration Orchestrator"""
    return ConfigurationOrchestrator(provider, config)


# Example configuration watcher
async def config_watcher(key: str, new_value: Any, old_value: Any) -> None:
    """Example configuration change watcher"""
    logger.info(f"Configuration changed: {key} = {new_value} (was: {old_value})")


# Example usage
async def main() -> None:
    """Example usage of Configuration Orchestrator"""
    async with create_configuration_orchestrator() as orchestrator:
        # Register a configuration watcher
        await orchestrator.watch_config("database_url", config_watcher)
        
        # Set some configurations
        await orchestrator.set_config("database_url", "postgresql://localhost/mydb", 
                                    ConfigScope.GLOBAL, updated_by="admin")
        
        await orchestrator.set_config("debug", True, ConfigScope.GLOBAL, 
                                    environment="development", updated_by="developer")
        
        # Get configurations
        db_url = await orchestrator.get_config("database_url")
        debug_mode = await orchestrator.get_config("debug", environment="development")
        
        print(f"Database URL: {db_url}")
        print(f"Debug mode (dev): {debug_mode}")
        
        # Create a profile
        profile = ConfigProfile(
            profile_id="web_service_prod",
            name="Web Service Production Profile",
            environment="production",
            service_configs={
                "web_service": {
                    "port": 8080,
                    "workers": 4,
                    "timeout": 30
                }
            },
            feature_flags={
                "new_ui": True,
                "experimental_feature": False
            }
        )
        
        await orchestrator.create_profile(profile)
        
        # Get profile configuration
        profile_config = await orchestrator.get_profile_config("web_service_prod", "web_service")
        print(f"Profile config: {json.dumps(profile_config, indent=2, default=str)}")
        
        # Get configuration status
        status = await orchestrator.get_configuration_status()
        print(f"Configuration status: {json.dumps(status, indent=2, default=str)}")


if __name__ == "__main__":
    asyncio.run(main())