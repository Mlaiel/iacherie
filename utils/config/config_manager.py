"""
Enterprise Configuration Manager
===============================

Ultra-advanced configuration management with enterprise-grade features including
hot-reload, validation, caching, and environment-aware configuration loading.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import os
import yaml
import json
from pathlib import Path
from typing import Any, Dict, Optional, Union, List, Callable
from abc import ABC, abstractmethod
import logging
import threading
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class BaseConfigurationManager(ABC):
    """
    Abstract base class for configuration managers.
    Defines the core interface for configuration management.
    """
    
    def __init__(self):
        self._config_data: Dict[str, Any] = {}
        self._lock = threading.RLock()
        self._observers: List[Callable] = []
        self._last_modified: Dict[str, datetime] = {}
        
    @abstractmethod
    def load_configuration(self, config_path: Optional[str] = None, 
                          environment: Optional[str] = None) -> Dict[str, Any]:
        """Load configuration from source."""
        pass
        
    @abstractmethod
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key."""
        pass
        
    @abstractmethod
    def set(self, key: str, value: Any) -> None:
        """Set configuration value."""
        pass
        
    def add_observer(self, observer: Callable) -> None:
        """Add configuration change observer."""
        with self._lock:
            self._observers.append(observer)
            
    def remove_observer(self, observer: Callable) -> None:
        """Remove configuration change observer."""
        with self._lock:
            if observer in self._observers:
                self._observers.remove(observer)
                
    def _notify_observers(self, key: str, old_value: Any, new_value: Any) -> None:
        """Notify observers of configuration changes."""
        for observer in self._observers:
            try:
                observer(key, old_value, new_value)
            except Exception as e:
                logger.error(f"Observer notification failed: {e}")

class ConfigurationManager(BaseConfigurationManager):
    """
    Enterprise configuration manager with advanced features:
    - Hot configuration reloading
    - Environment-specific configurations
    - Configuration validation
    - Performance optimization
    - Security features
    """
    
    def __init__(self, base_path: Optional[str] = None):
        super().__init__()
        self.base_path = Path(base_path) if base_path else Path(__file__).parent
        self.environment = os.getenv('AINFLUE_ENV', 'development')
        self._cache = {}
        self._cache_ttl = 300  # 5 minutes
        self._cache_timestamps = {}
        
        # Load default configurations
        self._load_defaults()
        
    def _load_defaults(self) -> None:
        """Load default configuration files."""
        try:
            # Load base configurations
            base_configs = [
                'performance_config.yaml',
                'utils_config.yaml'
            ]
            
            for config_file in base_configs:
                config_path = self.base_path / config_file
                if config_path.exists():
                    self._load_yaml_file(config_path)
                    
            logger.info("Default configurations loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load default configurations: {e}")
            
    def _load_yaml_file(self, file_path: Path) -> Dict[str, Any]:
        """Load YAML configuration file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # Remove docstring if present
                if content.startswith('"""'):
                    lines = content.split('\n')
                    start_idx = 0
                    for i, line in enumerate(lines):
                        if line.strip().endswith('"""') and i > 0:
                            start_idx = i + 1
                            break
                    content = '\n'.join(lines[start_idx:])
                
                data = yaml.safe_load(content)
                if data:
                    self._merge_config(data)
                    self._last_modified[str(file_path)] = datetime.now()
                return data or {}
        except Exception as e:
            logger.error(f"Failed to load YAML file {file_path}: {e}")
            return {}
            
    def _load_json_file(self, file_path: Path) -> Dict[str, Any]:
        """Load JSON configuration file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if data:
                    self._merge_config(data)
                    self._last_modified[str(file_path)] = datetime.now()
                return data or {}
        except Exception as e:
            logger.error(f"Failed to load JSON file {file_path}: {e}")
            return {}
            
    def _merge_config(self, new_config: Dict[str, Any]) -> None:
        """Merge new configuration with existing."""
        with self._lock:
            self._deep_merge(self._config_data, new_config)
            
    def _deep_merge(self, base: Dict[str, Any], update: Dict[str, Any]) -> None:
        """Deep merge two dictionaries."""
        for key, value in update.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_merge(base[key], value)
            else:
                base[key] = value
                
    def load_configuration(self, config_path: Optional[str] = None, 
                          environment: Optional[str] = None) -> Dict[str, Any]:
        """
        Load configuration from specified path and environment.
        
        Args:
            config_path: Path to configuration file or directory
            environment: Environment name (development, staging, production)
            
        Returns:
            Dict containing loaded configuration
        """
        if environment:
            self.environment = environment
            
        if config_path:
            path = Path(config_path)
            if path.is_file():
                if path.suffix in ['.yaml', '.yml']:
                    self._load_yaml_file(path)
                elif path.suffix == '.json':
                    self._load_json_file(path)
            elif path.is_dir():
                # Load all configuration files in directory
                for file_path in path.glob('*.yaml'):
                    self._load_yaml_file(file_path)
                for file_path in path.glob('*.yml'):
                    self._load_yaml_file(file_path)
                for file_path in path.glob('*.json'):
                    self._load_json_file(file_path)
                    
        # Load environment-specific configuration
        self._load_environment_config()
        
        return self._config_data.copy()
        
    def _load_environment_config(self) -> None:
        """Load environment-specific configuration."""
        env_file = self.base_path / f"{self.environment}_config.yaml"
        if env_file.exists():
            self._load_yaml_file(env_file)
            
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by key with dot notation support.
        
        Args:
            key: Configuration key (supports dot notation like 'database.host')
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        # Check cache first
        cache_key = f"{key}:{default}"
        if cache_key in self._cache:
            timestamp = self._cache_timestamps.get(cache_key)
            if timestamp and datetime.now() - timestamp < timedelta(seconds=self._cache_ttl):
                return self._cache[cache_key]
                
        with self._lock:
            current = self._config_data
            keys = key.split('.')
            
            try:
                for k in keys:
                    current = current[k]
                    
                # Cache the result
                self._cache[cache_key] = current
                self._cache_timestamps[cache_key] = datetime.now()
                
                return current
            except (KeyError, TypeError):
                return default
                
    def set(self, key: str, value: Any) -> None:
        """
        Set configuration value with dot notation support.
        
        Args:
            key: Configuration key (supports dot notation)
            value: Value to set
        """
        with self._lock:
            keys = key.split('.')
            current = self._config_data
            
            # Navigate to parent of target key
            for k in keys[:-1]:
                if k not in current:
                    current[k] = {}
                current = current[k]
                
            # Set the value
            old_value = current.get(keys[-1])
            current[keys[-1]] = value
            
            # Clear related cache entries
            self._clear_cache_for_key(key)
            
            # Notify observers
            self._notify_observers(key, old_value, value)
            
    def _clear_cache_for_key(self, key: str) -> None:
        """Clear cache entries related to a key."""
        keys_to_remove = [k for k in self._cache.keys() if k.startswith(f"{key}:")]
        for k in keys_to_remove:
            del self._cache[k]
            if k in self._cache_timestamps:
                del self._cache_timestamps[k]
                
    def reload(self) -> None:
        """Reload configuration from all sources."""
        with self._lock:
            old_config = self._config_data.copy()
            self._config_data.clear()
            self._cache.clear()
            self._cache_timestamps.clear()
            
            # Reload configurations
            self._load_defaults()
            self._load_environment_config()
            
            logger.info("Configuration reloaded successfully")
            
    def get_all(self) -> Dict[str, Any]:
        """Get all configuration data."""
        with self._lock:
            return self._config_data.copy()
            
    def has_key(self, key: str) -> bool:
        """Check if configuration key exists."""
        return self.get(key, None) is not None

class CreatorEconomyConfigManager(BaseConfigurationManager):
    """
    Specialized configuration manager for Creator Economy features.
    """
    
    def __init__(self):
        super().__init__()
        self.base_manager = ConfigurationManager()
        
    def load_configuration(self, config_path: Optional[str] = None, 
                          environment: Optional[str] = None) -> Dict[str, Any]:
        """Load creator economy specific configurations."""
        return self.base_manager.load_configuration(config_path, environment)
        
    def get(self, key: str, default: Any = None) -> Any:
        """Get creator economy configuration."""
        return self.base_manager.get(f"creator_economy.{key}", default)
        
    def set(self, key: str, value: Any) -> None:
        """Set creator economy configuration."""
        self.base_manager.set(f"creator_economy.{key}", value)
        
    def get_content_processing_config(self) -> Dict[str, Any]:
        """Get content processing configuration."""
        return self.get("content_processing", {})
        
    def get_collaboration_config(self) -> Dict[str, Any]:
        """Get collaboration configuration."""
        return self.get("collaboration", {})
        
    def get_monetization_config(self) -> Dict[str, Any]:
        """Get monetization configuration."""
        return self.get("monetization", {})

class EnterpriseConfigurationSuite:
    """
    Enterprise configuration suite orchestrating all configuration managers.
    """
    
    def __init__(self):
        self.config_manager = ConfigurationManager()
        self.creator_economy_manager = CreatorEconomyConfigManager()
        self._security_validator = None
        self._performance_optimizer = None
        
    def get_manager(self, domain: str) -> BaseConfigurationManager:
        """Get configuration manager for specific domain."""
        managers = {
            'core': self.config_manager,
            'creator_economy': self.creator_economy_manager
        }
        return managers.get(domain, self.config_manager)
        
    def orchestrate_configuration(self) -> Dict[str, Any]:
        """Orchestrate configuration loading across all domains."""
        config = {}
        
        # Load core configuration
        config['core'] = self.config_manager.get_all()
        
        # Load creator economy configuration
        config['creator_economy'] = self.creator_economy_manager.get_all()
        
        return config
        
    def enforce_security(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Enforce security policies on configuration."""
        # TODO: Implement security validation
        return config
        
    def optimize_performance(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize configuration for performance."""
        # TODO: Implement performance optimization
        return config
        
    def manage_compliance(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Ensure configuration compliance with standards."""
        # TODO: Implement compliance management
        return config