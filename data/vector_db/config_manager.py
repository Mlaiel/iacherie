"""
Configuration Manager - Dynamic Configuration System
===================================================

Enterprise-grade configuration management for Vector Database Module.
Supports environment-based config, dynamic reconfiguration, validation,
and A/B testing with feature flags.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

⚠️ CRITICAL COPYRIGHT WARNING ⚠️
This code is the intellectual property of Fahed Mlaiel and is protected by 
international copyright law. Any unauthorized use, reproduction, distribution 
or modification is strictly prohibited and will result in legal action.

For licensing inquiries: mlaiel@live.de
"""

import os
import yaml
import json
import asyncio
import logging
from typing import Any, Dict, List, Optional, Union, Set
from pathlib import Path
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import hashlib
from functools import lru_cache

logger = logging.getLogger(__name__)


@dataclass
class BackendConfig:
    """Configuration for vector backends."""
    type: str
    index_type: Optional[str] = None
    dimension: int = 768
    use_gpu: bool = False
    memory_limit: str = "4GB"
    batch_size: int = 1000
    custom_params: Optional[Dict[str, Any]] = None


@dataclass
class SecurityConfig:
    """Security configuration settings."""
    encryption: str = "AES-256-GCM"
    access_control: str = "RBAC"
    key_rotation_interval: int = 86400  # seconds
    audit_logging: bool = True
    compliance_mode: str = "GDPR"
    max_failed_attempts: int = 3
    session_timeout: int = 3600


@dataclass
class PerformanceConfig:
    """Performance optimization settings."""
    cache_size: str = "2GB"
    cache_ttl: int = 3600
    max_concurrent_queries: int = 100
    query_timeout: int = 30
    batch_size: int = 1000
    enable_prefetch: bool = True
    memory_threshold: float = 0.85


@dataclass
class MonitoringConfig:
    """Monitoring and observability settings."""
    enabled: bool = True
    metrics_interval: int = 60
    log_level: str = "INFO"
    alert_thresholds: Optional[Dict[str, float]] = None
    export_format: str = "prometheus"
    retention_days: int = 30


@dataclass
class VectorDBConfig:
    """Complete Vector Database configuration."""
    backend: BackendConfig
    security: SecurityConfig
    performance: PerformanceConfig
    monitoring: MonitoringConfig
    environment: str = "production"
    version: str = "1.0.0"
    feature_flags: Optional[Dict[str, bool]] = None


class ConfigValidator:
    """Validates configuration parameters."""
    
    @staticmethod
    def validate_backend_config(config: BackendConfig) -> List[str]:
        """Validate backend configuration."""
        errors = []
        
        # Validate backend type
        valid_backends = ["faiss", "chromadb", "pinecone"]
        if config.type not in valid_backends:
            errors.append(f"Invalid backend type: {config.type}. Must be one of {valid_backends}")
        
        # Validate dimension
        if config.dimension <= 0 or config.dimension > 10000:
            errors.append(f"Invalid dimension: {config.dimension}. Must be between 1 and 10000")
        
        # Validate batch size
        if config.batch_size <= 0 or config.batch_size > 10000:
            errors.append(f"Invalid batch size: {config.batch_size}. Must be between 1 and 10000")
        
        # Validate memory limit format
        if not config.memory_limit.endswith(('B', 'KB', 'MB', 'GB', 'TB')):
            errors.append(f"Invalid memory limit format: {config.memory_limit}")
        
        return errors
    
    @staticmethod
    def validate_security_config(config: SecurityConfig) -> List[str]:
        """Validate security configuration."""
        errors = []
        
        # Validate encryption
        valid_encryptions = ["AES-256-GCM", "AES-256-CBC", "ChaCha20-Poly1305"]
        if config.encryption not in valid_encryptions:
            errors.append(f"Invalid encryption: {config.encryption}")
        
        # Validate access control
        valid_access_controls = ["RBAC", "ABAC", "MAC"]
        if config.access_control not in valid_access_controls:
            errors.append(f"Invalid access control: {config.access_control}")
        
        # Validate timeouts
        if config.key_rotation_interval < 3600:  # Minimum 1 hour
            errors.append("Key rotation interval must be at least 1 hour")
        
        if config.session_timeout < 300:  # Minimum 5 minutes
            errors.append("Session timeout must be at least 5 minutes")
        
        return errors
    
    @staticmethod
    def validate_performance_config(config: PerformanceConfig) -> List[str]:
        """Validate performance configuration."""
        errors = []
        
        # Validate cache size format
        if not config.cache_size.endswith(('B', 'KB', 'MB', 'GB', 'TB')):
            errors.append(f"Invalid cache size format: {config.cache_size}")
        
        # Validate thresholds
        if config.memory_threshold <= 0 or config.memory_threshold > 1:
            errors.append("Memory threshold must be between 0 and 1")
        
        # Validate timeouts
        if config.query_timeout <= 0:
            errors.append("Query timeout must be positive")
        
        if config.cache_ttl <= 0:
            errors.append("Cache TTL must be positive")
        
        return errors


class ConfigManager:
    """
    Enterprise-grade configuration manager for Vector Database Module.
    
    Features:
    - Environment-based configuration
    - Dynamic reconfiguration
    - Configuration validation
    - A/B testing support
    - Feature flags
    - Configuration versioning
    - Rollback capabilities
    """
    
    def __init__(self, config_path -> None: Optional[str] = None) -> None:
        """
        Initialize configuration manager.
        
        Args:
            config_path: Path to configuration file
        """
        self.config_path = config_path or "config/vector_db.yaml"
        self.config: Optional[VectorDBConfig] = None
        self.config_history: List[Tuple[datetime, VectorDBConfig]] = []
        self.watchers: Set[callable] = set()
        self.validator = ConfigValidator()
        
        # Default configuration
        self._default_config = self._create_default_config()
        
        # Configuration cache
        self._config_cache = {}
        self._cache_ttl = 300  # 5 minutes
        
        logger.info(f"ConfigManager initialized with path: {self.config_path}")
    
    def _create_default_config(self) -> VectorDBConfig:
        """Create default configuration."""
        return VectorDBConfig(
            backend=BackendConfig(
                type="faiss",
                index_type="IndexIVFFlat",
                dimension=768,
                use_gpu=False,
                memory_limit="4GB",
                batch_size=1000
            ),
            security=SecurityConfig(
                encryption="AES-256-GCM",
                access_control="RBAC",
                audit_logging=True,
                compliance_mode="GDPR"
            ),
            performance=PerformanceConfig(
                cache_size="2GB",
                max_concurrent_queries=100,
                query_timeout=30,
                batch_size=1000
            ),
            monitoring=MonitoringConfig(
                enabled=True,
                metrics_interval=60,
                log_level="INFO",
                export_format="prometheus"
            ),
            environment="production",
            feature_flags={}
        )
    
    async def load_config(self, force_reload: bool = False) -> VectorDBConfig:
        """
        Load configuration from file or environment.
        
        Args:
            force_reload: Force reload even if cached
        
        Returns:
            Loaded configuration
        """
        try:
            # Check cache first
            cache_key = f"config_{self.config_path}"
            if not force_reload and cache_key in self._config_cache:
                cached_config, cached_time = self._config_cache[cache_key]
                if datetime.utcnow() - cached_time < timedelta(seconds=self._cache_ttl):
                    self.config = cached_config
                    return cached_config
            
            # Load from file if exists
            if Path(self.config_path).exists():
                config_dict = await self._load_from_file()
            else:
                logger.warning(f"Config file not found: {self.config_path}, using defaults")
                config_dict = asdict(self._default_config)
            
            # Override with environment variables
            config_dict = self._override_with_env(config_dict)
            
            # Create config object
            self.config = self._dict_to_config(config_dict)
            
            # Validate configuration
            await self._validate_config(self.config)
            
            # Cache configuration
            self._config_cache[cache_key] = (self.config, datetime.utcnow())
            
            # Store in history
            self.config_history.append((datetime.utcnow(), self.config))
            
            # Limit history size
            if len(self.config_history) > 100:
                self.config_history = self.config_history[-50:]
            
            # Notify watchers
            await self._notify_watchers()
            
            logger.info("Configuration loaded successfully")
            return self.config
            
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            # Fallback to default config
            self.config = self._default_config
            return self.config
    
    async def _load_from_file(self) -> Dict[str, Any]:
        """Load configuration from file."""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                if self.config_path.endswith('.yaml') or self.config_path.endswith('.yml'):
                    return yaml.safe_load(f)
                elif self.config_path.endswith('.json'):
                    return json.load(f)
                else:
                    raise ValueError(f"Unsupported config format: {self.config_path}")
        except Exception as e:
            logger.error(f"Failed to load config file: {e}")
            raise
    
    def _override_with_env(self, config_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Override configuration with environment variables."""
        env_mappings = {
            'VECTOR_DB_BACKEND': ['backend', 'type'],
            'VECTOR_DB_DIMENSION': ['backend', 'dimension'],
            'VECTOR_DB_USE_GPU': ['backend', 'use_gpu'],
            'VECTOR_DB_BATCH_SIZE': ['backend', 'batch_size'],
            'VECTOR_DB_CACHE_SIZE': ['performance', 'cache_size'],
            'VECTOR_DB_MAX_QUERIES': ['performance', 'max_concurrent_queries'],
            'VECTOR_DB_ENCRYPTION': ['security', 'encryption'],
            'VECTOR_DB_LOG_LEVEL': ['monitoring', 'log_level'],
            'VECTOR_DB_ENVIRONMENT': ['environment']
        }
        
        for env_var, path in env_mappings.items():
            if env_var in os.environ:
                value = os.environ[env_var]
                
                # Type conversion
                if env_var.endswith('_GPU'):
                    value = value.lower() in ['true', '1', 'yes']
                elif env_var.endswith('_DIMENSION') or env_var.endswith('_SIZE') or env_var.endswith('_QUERIES'):
                    try:
                        value = int(value)
                    except ValueError:
                        continue
                
                # Set nested value
                current = config_dict
                for key in path[:-1]:
                    if key not in current:
                        current[key] = {}
                    current = current[key]
                current[path[-1]] = value
        
        return config_dict
    
    def _dict_to_config(self, config_dict: Dict[str, Any]) -> VectorDBConfig:
        """Convert dictionary to configuration object."""
        try:
            return VectorDBConfig(
                backend=BackendConfig(**config_dict.get('backend', {})),
                security=SecurityConfig(**config_dict.get('security', {})),
                performance=PerformanceConfig(**config_dict.get('performance', {})),
                monitoring=MonitoringConfig(**config_dict.get('monitoring', {})),
                environment=config_dict.get('environment', 'production'),
                version=config_dict.get('version', '1.0.0'),
                feature_flags=config_dict.get('feature_flags', {})
            )
        except Exception as e:
            logger.error(f"Failed to create config object: {e}")
            return self._default_config
    
    async def _validate_config(self, config: VectorDBConfig) -> None:
        """Validate configuration."""
        all_errors = []
        
        # Validate backend
        all_errors.extend(self.validator.validate_backend_config(config.backend))
        
        # Validate security
        all_errors.extend(self.validator.validate_security_config(config.security))
        
        # Validate performance
        all_errors.extend(self.validator.validate_performance_config(config.performance))
        
        if all_errors:
            error_msg = "Configuration validation failed:\n" + "\n".join(all_errors)
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        logger.info("Configuration validation passed")
    
    async def save_config(self, config: Optional[VectorDBConfig] = None) -> bool:
        """
        Save configuration to file.
        
        Args:
            config: Configuration to save, uses current if None
        
        Returns:
            True if saved successfully
        """
        try:
            config_to_save = config or self.config
            if not config_to_save:
                raise ValueError("No configuration to save")
            
            # Convert to dictionary
            config_dict = asdict(config_to_save)
            
            # Ensure directory exists
            Path(self.config_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Save to file
            with open(self.config_path, 'w', encoding='utf-8') as f:
                if self.config_path.endswith('.yaml') or self.config_path.endswith('.yml'):
                    yaml.dump(config_dict, f, default_flow_style=False, indent=2)
                elif self.config_path.endswith('.json'):
                    json.dump(config_dict, f, indent=2)
                else:
                    raise ValueError(f"Unsupported config format: {self.config_path}")
            
            logger.info(f"Configuration saved to: {self.config_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by key path.
        
        Args:
            key: Dot-separated key path (e.g., 'backend.dimension')
            default: Default value if key not found
        
        Returns:
            Configuration value
        """
        if not self.config:
            return default
        
        try:
            keys = key.split('.')
            value = asdict(self.config)
            
            for k in keys:
                value = value[k]
            
            return value
            
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any) -> bool:
        """
        Set configuration value by key path.
        
        Args:
            key: Dot-separated key path
            value: Value to set
        
        Returns:
            True if set successfully
        """
        if not self.config:
            return False
        
        try:
            keys = key.split('.')
            config_dict = asdict(self.config)
            
            # Navigate to parent
            current = config_dict
            for k in keys[:-1]:
                if k not in current:
                    current[k] = {}
                current = current[k]
            
            # Set value
            current[keys[-1]] = value
            
            # Recreate config object
            self.config = self._dict_to_config(config_dict)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to set config value: {e}")
            return False
    
    def is_feature_enabled(self, feature_name: str) -> bool:
        """
        Check if a feature flag is enabled.
        
        Args:
            feature_name: Name of the feature
        
        Returns:
            True if feature is enabled
        """
        if not self.config or not self.config.feature_flags:
            return False
        
        return self.config.feature_flags.get(feature_name, False)
    
    def enable_feature(self, feature_name: str) -> None:
        """Enable a feature flag."""
        if not self.config:
            return
        
        if not self.config.feature_flags:
            self.config.feature_flags = {}
        
        self.config.feature_flags[feature_name] = True
        logger.info(f"Feature enabled: {feature_name}")
    
    def disable_feature(self, feature_name: str) -> None:
        """Disable a feature flag."""
        if not self.config or not self.config.feature_flags:
            return
        
        self.config.feature_flags[feature_name] = False
        logger.info(f"Feature disabled: {feature_name}")
    
    async def rollback(self, steps: int = 1) -> bool:
        """
        Rollback to previous configuration.
        
        Args:
            steps: Number of steps to rollback
        
        Returns:
            True if rollback successful
        """
        try:
            if len(self.config_history) <= steps:
                logger.warning("Not enough history for rollback")
                return False
            
            # Get previous config
            _, previous_config = self.config_history[-(steps + 1)]
            
            # Validate previous config
            await self._validate_config(previous_config)
            
            # Set as current
            self.config = previous_config
            
            # Add to history
            self.config_history.append((datetime.utcnow(), self.config))
            
            # Notify watchers
            await self._notify_watchers()
            
            logger.info(f"Rolled back {steps} configuration steps")
            return True
            
        except Exception as e:
            logger.error(f"Failed to rollback configuration: {e}")
            return False
    
    def add_watcher(self, callback: callable) -> None:
        """
        Add configuration change watcher.
        
        Args:
            callback: Function to call when config changes
        """
        self.watchers.add(callback)
        logger.info("Configuration watcher added")
    
    def remove_watcher(self, callback: callable) -> None:
        """Remove configuration change watcher."""
        self.watchers.discard(callback)
        logger.info("Configuration watcher removed")
    
    async def _notify_watchers(self) -> None:
        """Notify all watchers of configuration changes."""
        for watcher in self.watchers:
            try:
                if asyncio.iscoroutinefunction(watcher):
                    await watcher(self.config)
                else:
                    watcher(self.config)
            except Exception as e:
                logger.error(f"Error notifying config watcher: {e}")
    
    def get_config_hash(self) -> str:
        """Get hash of current configuration for comparison."""
        if not self.config:
            return ""
        
        config_str = json.dumps(asdict(self.config), sort_keys=True)
        return hashlib.sha256(config_str.encode()).hexdigest()
    
    async def health_check(self) -> bool:
        """Perform health check on configuration manager."""
        try:
            # Check if config is loaded
            if not self.config:
                return False
            
            # Validate current config
            await self._validate_config(self.config)
            
            # Check file access if path exists
            if Path(self.config_path).exists():
                if not os.access(self.config_path, os.R_OK):
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Configuration health check failed: {e}")
            return False
    
    async def reload(self) -> bool:
        """Reload configuration from file."""
        try:
            await self.load_config(force_reload=True)
            logger.info("Configuration reloaded successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to reload configuration: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get configuration manager statistics."""
        return {
            "config_loaded": self.config is not None,
            "config_path": self.config_path,
            "history_count": len(self.config_history),
            "watchers_count": len(self.watchers),
            "config_hash": self.get_config_hash(),
            "last_loaded": self.config_history[-1][0] if self.config_history else None
        }
    
    async def shutdown(self) -> None:
        """Shutdown configuration manager."""
        logger.info("Shutting down ConfigManager...")
        
        # Clear watchers
        self.watchers.clear()
        
        # Clear cache
        self._config_cache.clear()
        
        logger.info("ConfigManager shutdown completed")


# Export main class
__all__ = [
    'ConfigManager',
    'VectorDBConfig',
    'BackendConfig',
    'SecurityConfig',
    'PerformanceConfig',
    'MonitoringConfig',
    'ConfigValidator'
]