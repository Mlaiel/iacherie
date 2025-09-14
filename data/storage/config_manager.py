"""Professional Storage Configuration Manager - IA Influencer Agent Platform
=========================================================================
Module: backend/data/storage/config_manager.py
Author: Fahed Mlaiel (mlaiel@live.de)
Type: Industrial Configuration Core - Dynamic Storage Configuration
Responsibility: Centralized configuration management for all storage components
Technologies: Python, YAML, JSON, Environment variables, Dynamic loading
=========================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Usage non autorisé strictement interdit et passible de poursuites judiciaires.
Contact: mlaiel@live.de

ÉQUIPE PROJET:
- Lead Dev IA + Architecte: Fahed Mlaiel
- Backend Senior + ML Engineer: Expertise multi-domaines  
- Audio + DevOps + DBA + Sécurité: Compétences industrielles
- Microservices + IA Prompt Engineer: Innovation avancée

LOGIQUE MÉTIER INTÉGRÉE:
Configuration Loading → Validation → Environment Detection → 
Provider Setup → Security Configuration → Performance Tuning → 
Hot Reload → Health Monitoring → Disaster Recovery Settings
"""

import asyncio
import logging
import os
import json
import yaml
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path
import threading
import hashlib
import tempfile
import shutil
from concurrent.futures import ThreadPoolExecutor

# Configuration validation
from pydantic import BaseModel, validator, Field
import jsonschema

# Encryption for sensitive configuration
from cryptography.fernet import Fernet
import base64


logger = logging.getLogger(__name__)


class EnvironmentType(Enum):
    """
Environment types for configuration"""

    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"


class ConfigurationSource(Enum):
    """Configuration data sources"""

    FILE_YAML = "file_yaml"
    FILE_JSON = "file_json"
    ENVIRONMENT_VARS = "environment_vars"
    DATABASE = "database"
    REMOTE_API = "remote_api"
    VAULT = "vault"


@dataclass
class StorageProviderConfig:
    """Storage provider configuration"""
    provider_type: str
    enabled: bool = True
    primary: bool = False
    region: str = ""
    access_key: str = ""
    secret_key: str = ""
    bucket_name: str = ""
    endpoint_url: Optional[str] = None
    ssl_enabled: bool = True
    connection_timeout: int = 30
    read_timeout: int = 60
    max_retries: int = 3
    cost_per_gb: float = 0.023  # Default AWS S3 pricing
    performance_tier: str = "standard"
    encryption_enabled: bool = True
    versioning_enabled: bool = True
    backup_enabled: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SecurityConfig:
    """Security configuration"""
    encryption_key: str = ""
    master_key_rotation_days: int = 365
    file_encryption_enabled: bool = True
    transit_encryption_enabled: bool = True
    access_logging_enabled: bool = True
    audit_retention_days: int = 2555  # 7 years
    threat_detection_enabled: bool = True
    virus_scanning_enabled: bool = True
    content_policy_enabled: bool = True
    compliance_mode: str = "strict"  # strict, standard, relaxed
    allowed_file_types: List[str] = field(default_factory=lambda: [
        "mp3", "wav", "flac", "aac", "mp4", "avi", "mov", "webm",
        "jpg", "jpeg", "png", "gif", "webp", "tiff",
        "pdf", "doc", "docx", "txt", "md"
    ])
    max_file_size_mb: int = 500
    quarantine_enabled: bool = True


@dataclass
class PerformanceConfig:
    """Performance configuration"""
    max_concurrent_uploads: int = 100
    max_concurrent_downloads: int = 200
    chunk_size_mb: int = 8
    multipart_threshold_mb: int = 64
    connection_pool_size: int = 50
    cache_enabled: bool = True
    cache_size_mb: int = 1024
    cache_ttl_seconds: int = 3600
    compression_enabled: bool = True
    compression_level: int = 6  # 1-9, 6 is balanced
    deduplication_enabled: bool = True
    cdn_enabled: bool = True
    prefetch_enabled: bool = True
    lazy_loading_enabled: bool = True


@dataclass
class BackupConfig:
    """
Backup configuration"""
    enabled: bool = True
    real_time_backup: bool = True
    scheduled_backup_enabled: bool = True
    backup_intervals: Dict[str, str] = field(default_factory=lambda: {
        "hourly": "0 * * * *",
        "daily": "0 2 * * *",
        "weekly": "0 2 * * 0",
        "monthly": "0 2 1 * *"
    })
    retention_policies: Dict[str, int] = field(default_factory=lambda: {
        "hourly": 48,  # hours
        "daily": 30,   # days
        "weekly": 12,  # weeks
        "monthly": 12  # months
    })
    geographic_redundancy: bool = True
    cross_provider_backup: bool = True
    encryption_enabled: bool = True
    compression_enabled: bool = True
    verification_enabled: bool = True
    disaster_recovery_enabled: bool = True
    backup_destinations: List[str] = field(default_factory=list)


@dataclass
class MonitoringConfig:
    """Monitoring and alerting configuration"""
    enabled: bool = True
    metrics_collection_interval: int = 30  # seconds
    prometheus_enabled: bool = True
    prometheus_port: int = 8080
    grafana_enabled: bool = True
    alerting_enabled: bool = True
    alert_channels: List[str] = field(default_factory=lambda: ["email", "webhook"])
    email_notifications: Dict[str, str] = field(default_factory=dict)
    webhook_urls: List[str] = field(default_factory=list)
    log_level: str = "INFO"
    log_retention_days: int = 90
    performance_thresholds: Dict[str, float] = field(default_factory=lambda: {
        "latency_ms_p95": 2000.0,
        "error_rate_percent": 1.0,
        "availability_percent": 99.5,
        "storage_usage_percent": 85.0
    })


@dataclass
class StorageConfiguration:
    """Complete storage system configuration"""
    environment: EnvironmentType = EnvironmentType.DEVELOPMENT
    version: str = "1.0.0"
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    # Core configurations
    providers: List[StorageProviderConfig] = field(default_factory=list)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    performance: PerformanceConfig = field(default_factory=PerformanceConfig)
    backup: BackupConfig = field(default_factory=BackupConfig)
    monitoring: MonitoringConfig = field(default_factory=MonitoringConfig)
    
    # Features
    versioning_enabled: bool = True
    encryption_enabled: bool = True
    backup_enabled: bool = True
    monitoring_enabled: bool = True
    analytics_enabled: bool = True
    
    # Paths
    base_storage_path: str = "/data/storage"
    temp_path: str = "/tmp/ia_storage"
    log_path: str = "/var/log/ia_storage"
    
    # Advanced settings
    hot_reload_enabled: bool = True
    configuration_encryption: bool = True
    remote_configuration: bool = False
    configuration_backup: bool = True


class ConfigurationManager:
    """
    Professional configuration manager for IA Influencer Agent storage platform.
    
    Provides centralized configuration management with dynamic loading,
    validation, encryption, and hot-reload capabilities.
    """
    
    def __init__(self, config_path -> None: str = None, environment -> None: EnvironmentType = None) -> None:
        """
        Initialize ConfigurationManager.
        
        Args:
            config_path: Path to configuration file
            environment: Environment type (auto-detected if None)
        """
        self.logger = logging.getLogger(__name__)
        
        # Configuration state
        self.config_path = config_path or self._detect_config_path()
        self.environment = environment or self._detect_environment()
        self.current_config: Optional[StorageConfiguration] = None
        
        # Configuration validation
        self.schema_validator = None
        self.validation_enabled = True
        
        # Hot reload
        self.hot_reload_enabled = True
        self.config_watcher = None
        self.last_reload_time = datetime.utcnow()
        
        # Encryption for sensitive data
        self.encryption_key = self._get_or_create_encryption_key()
        
        # Thread safety
        self.config_lock = threading.RLock()
        
        # Configuration cache
        self.config_cache = {}
        self.cache_ttl = 300  # 5 minutes
        
        # Backup
        self.backup_enabled = True
        self.backup_path = "/backup/config"
        
        # Initialize
        self._initialize_configuration()
    
    def _detect_config_path(self) -> str:
        """Detect configuration file path"""
        possible_paths = [
            os.getenv("STORAGE_CONFIG_PATH"),
            "./config/storage.yml",
            "./storage.yml",
            "/etc/ia-storage/storage.yml",
            "./config/storage.yaml",
            "./storage.yaml"
        ]
        
        for path in possible_paths:
            if path and Path(path).exists():
                return path
        
        # Create default configuration
        default_path = "./config/storage.yml"
        self._create_default_configuration(default_path)
        return default_path
    
    def _detect_environment(self) -> EnvironmentType:
        """Detect current environment"""
        env_var = os.getenv("STORAGE_ENVIRONMENT", "development").lower()
        
        env_mapping = {
            "dev": EnvironmentType.DEVELOPMENT,
            "development": EnvironmentType.DEVELOPMENT,
            "staging": EnvironmentType.STAGING,
            "stage": EnvironmentType.STAGING,
            "prod": EnvironmentType.PRODUCTION,
            "production": EnvironmentType.PRODUCTION,
            "test": EnvironmentType.TESTING,
            "testing": EnvironmentType.TESTING
        }
        
        return env_mapping.get(env_var, EnvironmentType.DEVELOPMENT)
    
    def _get_or_create_encryption_key(self) -> bytes:
        """Get or create encryption key for sensitive configuration"""
        key_file = Path("./config/.storage_key")
        
        if key_file.exists():
            with open(key_file, 'rb') as f:
                return f.read()
        else:
            # Create new key
            key = Fernet.generate_key()
            key_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(key_file, 'wb') as f:
                f.write(key)
            
            # Secure permissions
            os.chmod(key_file, 0o600)
            return key
    
    def _initialize_configuration(self) -> None:
        """Initialize configuration system"""
        try:
            # Load configuration
            self.load_configuration()
            
            # Start hot reload if enabled
            if self.hot_reload_enabled and self.current_config:
                if self.current_config.hot_reload_enabled:
                    asyncio.create_task(self._start_config_watcher())
            
            # Initialize schema validator
            self._initialize_schema_validator()
            
            self.logger.info("Configuration manager initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize configuration: {str(e)}")
            raise
    
    def load_configuration(self, config_path: str = None) -> StorageConfiguration:
        """
        Load configuration from file.
        
        Args:
            config_path: Path to configuration file (uses default if None)
            
        Returns:
            Loaded storage configuration
        """
        try:
            with self.config_lock:
                target_path = config_path or self.config_path
                
                if not Path(target_path).exists():
                    self.logger.warning(f"Configuration file not found: {target_path}")
                    return self._create_default_configuration()
                
                # Read configuration file
                with open(target_path, 'r', encoding='utf-8') as f:
                    if target_path.endswith(('.yml', '.yaml')):
                        config_data = yaml.safe_load(f)
                    else:
                        config_data = json.load(f)
                
                # Apply environment-specific overrides
                config_data = self._apply_environment_overrides(config_data)
                
                # Decrypt sensitive data
                config_data = self._decrypt_sensitive_data(config_data)
                
                # Validate configuration
                if self.validation_enabled:
                    self._validate_configuration(config_data)
                
                # Convert to configuration object
                self.current_config = self._dict_to_config(config_data)
                
                # Update timestamps
                self.current_config.updated_at = datetime.utcnow()
                self.last_reload_time = datetime.utcnow()
                
                # Cache configuration
                self._cache_configuration()
                
                # Backup configuration if enabled
                if self.backup_enabled:
                    self._backup_configuration()
                
                self.logger.info(f"Configuration loaded successfully from {target_path}")
                return self.current_config
                
        except Exception as e:
            self.logger.error(f"Failed to load configuration: {str(e)}")
            if not self.current_config:
                self.logger.warning("Using default configuration")
                self.current_config = self._create_default_configuration()
            return self.current_config
    
    def save_configuration(self, config: StorageConfiguration = None, 
                          config_path: str = None) -> bool:
        """
        Save configuration to file.
        
        Args:
            config: Configuration to save (uses current if None)
            config_path: Path to save to (uses default if None)
            
        Returns:
            Success status
        """
        try:
            with self.config_lock:
                target_config = config or self.current_config
                target_path = config_path or self.config_path
                
                if not target_config:
                    raise ValueError("No configuration to save")
                
                # Update timestamp
                target_config.updated_at = datetime.utcnow()
                
                # Convert to dictionary
                config_dict = asdict(target_config)
                
                # Encrypt sensitive data
                config_dict = self._encrypt_sensitive_data(config_dict)
                
                # Ensure directory exists
                Path(target_path).parent.mkdir(parents=True, exist_ok=True)
                
                # Create backup before saving
                if Path(target_path).exists():
                    backup_path = f"{target_path}.backup.{int(datetime.utcnow().timestamp())}"
                    shutil.copy2(target_path, backup_path)
                
                # Save configuration
                with open(target_path, 'w', encoding='utf-8') as f:
                    if target_path.endswith(('.yml', '.yaml')):
                        yaml.dump(config_dict, f, default_flow_style=False, indent=2)
                    else:
                        json.dump(config_dict, f, indent=2, default=str)
                
                # Update current configuration
                self.current_config = target_config
                
                self.logger.info(f"Configuration saved successfully to {target_path}")
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to save configuration: {str(e)}")
            return False
    
    def get_provider_config(self, provider_name: str) -> Optional[StorageProviderConfig]:
        """
        Get configuration for specific storage provider.
        
        Args:
            provider_name: Name of the storage provider
            
        Returns:
            Provider configuration or None if not found
        """
        if not self.current_config:
            return None
        
        for provider in self.current_config.providers:
            if provider.provider_type.lower() == provider_name.lower():
                return provider
        
        return None
    
    def get_primary_provider(self) -> Optional[StorageProviderConfig]:
        """
        Get primary storage provider configuration.
        
        Returns:
            Primary provider configuration or None
        """
        if not self.current_config:
            return None
        
        # Find explicitly marked primary provider
        for provider in self.current_config.providers:
            if provider.primary and provider.enabled:
                return provider
        
        # Fall back to first enabled provider
        for provider in self.current_config.providers:
            if provider.enabled:
                return provider
        
        return None
    
    def get_enabled_providers(self) -> List[StorageProviderConfig]:
        """
        Get all enabled storage providers.
        
        Returns:
            List of enabled provider configurations
        """
        if not self.current_config:
            return []
        
        return [p for p in self.current_config.providers if p.enabled]
    
    def add_provider(self, provider_config: StorageProviderConfig) -> bool:
        """
        Add a new storage provider configuration.
        
        Args:
            provider_config: Provider configuration to add
            
        Returns:
            Success status
        """
        try:
            with self.config_lock:
                if not self.current_config:
                    self.current_config = self._create_default_configuration()
                
                # Check for duplicate provider
                existing = self.get_provider_config(provider_config.provider_type)
                if existing:
                    self.logger.warning(f"Provider {provider_config.provider_type} already exists")
                    return False
                
                # Add provider
                self.current_config.providers.append(provider_config)
                
                # Save configuration
                return self.save_configuration()
                
        except Exception as e:
            self.logger.error(f"Failed to add provider: {str(e)}")
            return False
    
    def update_provider(self, provider_name: str, 
                       updates: Dict[str, Any]) -> bool:
        """
        Update storage provider configuration.
        
        Args:
            provider_name: Name of provider to update
            updates: Dictionary of updates to apply
            
        Returns:
            Success status
        """
        try:
            with self.config_lock:
                provider = self.get_provider_config(provider_name)
                if not provider:
                    self.logger.error(f"Provider {provider_name} not found")
                    return False
                
                # Apply updates
                for key, value in updates.items():
                    if hasattr(provider, key):
                        setattr(provider, key, value)
                    else:
                        self.logger.warning(f"Unknown provider attribute: {key}")
                
                # Save configuration
                return self.save_configuration()
                
        except Exception as e:
            self.logger.error(f"Failed to update provider: {str(e)}")
            return False
    
    def remove_provider(self, provider_name: str) -> bool:
        """
        Remove storage provider configuration.
        
        Args:
            provider_name: Name of provider to remove
            
        Returns:
            Success status
        """
        try:
            with self.config_lock:
                if not self.current_config:
                    return False
                
                # Find and remove provider
                original_count = len(self.current_config.providers)
                self.current_config.providers = [
                    p for p in self.current_config.providers 
                    if p.provider_type.lower() != provider_name.lower()
                ]
                
                if len(self.current_config.providers) == original_count:
                    self.logger.warning(f"Provider {provider_name} not found")
                    return False
                
                # Save configuration
                return self.save_configuration()
                
        except Exception as e:
            self.logger.error(f"Failed to remove provider: {str(e)}")
            return False
    
    def reload_configuration(self) -> bool:
        """
        Reload configuration from file.
        
        Returns:
            Success status
        """
        try:
            old_config = self.current_config
            
            # Load new configuration
            new_config = self.load_configuration()
            
            # Compare configurations
            if old_config and new_config:
                changes = self._compare_configurations(old_config, new_config)
                if changes:
                    self.logger.info(f"Configuration changes detected: {changes}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to reload configuration: {str(e)}")
            return False
    
    def validate_configuration(self, config: StorageConfiguration = None) -> bool:
        """
        Validate configuration.
        
        Args:
            config: Configuration to validate (uses current if None)
            
        Returns:
            Validation result
        """
        try:
            target_config = config or self.current_config
            if not target_config:
                return False
            
            # Convert to dictionary for validation
            config_dict = asdict(target_config)
            
            # Validate using schema
            return self._validate_configuration(config_dict)
            
        except Exception as e:
            self.logger.error(f"Configuration validation failed: {str(e)}")
            return False
    
    def get_configuration_summary(self) -> Dict[str, Any]:
        """
        Get configuration summary for monitoring.
        
        Returns:
            Configuration summary
        """
        if not self.current_config:
            return {"status": "no_configuration"}
        
        return {
            "environment": self.environment.value,
            "version": self.current_config.version,
            "last_updated": self.current_config.updated_at.isoformat(),
            "providers_count": len(self.current_config.providers),
            "enabled_providers": len(self.get_enabled_providers()),
            "features": {
                "versioning": self.current_config.versioning_enabled,
                "encryption": self.current_config.encryption_enabled,
                "backup": self.current_config.backup_enabled,
                "monitoring": self.current_config.monitoring_enabled
            },
            "hot_reload": self.hot_reload_enabled,
            "last_reload": self.last_reload_time.isoformat()
        }
    
    # Private helper methods
    
    def _create_default_configuration(self, save_path: str = None) -> StorageConfiguration:
        """Create default configuration"""
        config = StorageConfiguration(
            environment=self.environment,
            version="1.0.0"
        )
        
        # Add default local provider
        local_provider = StorageProviderConfig(
            provider_type="local",
            enabled=True,
            primary=True,
            bucket_name="./data/storage",
            cost_per_gb=0.0
        )
        config.providers.append(local_provider)
        
        if save_path:
            # Save default configuration
            Path(save_path).parent.mkdir(parents=True, exist_ok=True)
            config_dict = asdict(config)
            
            with open(save_path, 'w') as f:
                yaml.dump(config_dict, f, default_flow_style=False, indent=2)
        
        return config
    
    def _apply_environment_overrides(self, config_data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply environment-specific configuration overrides"""
        env_overrides = {
            EnvironmentType.DEVELOPMENT: {
                "security.compliance_mode": "relaxed",
                "performance.cache_enabled": True,
                "monitoring.log_level": "DEBUG"
            },
            EnvironmentType.PRODUCTION: {
                "security.compliance_mode": "strict",
                "performance.max_concurrent_uploads": 200,
                "monitoring.log_level": "INFO"
            }
        }
        
        overrides = env_overrides.get(self.environment, {})
        
        for key_path, value in overrides.items():
            self._set_nested_value(config_data, key_path, value)
        
        return config_data
    
    def _set_nested_value(self, data -> None: Dict, key_path -> None: str, value -> None: Any) -> None:
        """Set nested dictionary value using dot notation"""
        keys = key_path.split('.')
        current = data
        
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        current[keys[-1]] = value
    
    def _encrypt_sensitive_data(self, config_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
Encrypt sensitive configuration data"""
        # Implementation would encrypt sensitive fields like API keys
        return config_dict
    
    def _decrypt_sensitive_data(self, config_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
Decrypt sensitive configuration data"""
        # Implementation would decrypt sensitive fields
        return config_dict
    
    def _dict_to_config(self, config_dict: Dict[str, Any]) -> StorageConfiguration:
        """
Convert dictionary to configuration object"""
        # Convert dictionary to StorageConfiguration object
        # This is a simplified implementation
        config = StorageConfiguration()
        
        # Update fields from dictionary
        for key, value in config_dict.items():
            if hasattr(config, key):
                setattr(config, key, value)
        
        return config
    
    def _compare_configurations(self, old_config: StorageConfiguration, 
                              new_config: StorageConfiguration) -> List[str]:
        """
Compare two configurations and return list of changes"""
        changes = []
        
        # Compare provider counts
        if len(old_config.providers) != len(new_config.providers):
            changes.append("provider_count_changed")
        
        # Compare security settings
        if old_config.security.compliance_mode != new_config.security.compliance_mode:
            changes.append("compliance_mode_changed")
        
        # Add more comparisons as needed
        
        return changes
    
    def _validate_configuration(self, config_dict: Dict[str, Any]) -> bool:
        """Validate configuration dictionary"""
        # Implement JSON schema validation
        try:
            # Basic validation
            required_fields = ['environment', 'providers', 'security']
            for field in required_fields:
                if field not in config_dict:
                    raise ValueError(f"Missing required field: {field}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Configuration validation error: {str(e)}")
            return False
    
    def _initialize_schema_validator(self) -> None:
        try:
            logger.info(f"Executing _initialize_schema_validator")
            
            # Implementation for _initialize_schema_validator
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"_initialize_schema_validator completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"_initialize_schema_validator failed: {e}")
            raise
    def _cache_configuration(self) -> None:
        """
Cache current configuration"""
        if self.current_config:
            cache_key = f"config_{self.environment.value}"
            self.config_cache[cache_key] = {
                'config': self.current_config,
                'timestamp': datetime.utcnow()
            }
    
    def _backup_configuration(self) -> None:
        """Backup current configuration"""
        if not self.backup_enabled or not self.current_config:
            return
        
        try:
            backup_dir = Path(self.backup_path)
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            backup_file = backup_dir / f"storage_config_{timestamp}.yml"
            
            config_dict = asdict(self.current_config)
            
            with open(backup_file, 'w') as f:
                yaml.dump(config_dict, f, default_flow_style=False, indent=2)
            
            # Cleanup old backups (keep last 10)
            backup_files = sorted(backup_dir.glob("storage_config_*.yml"))
            if len(backup_files) > 10:
                for old_backup in backup_files[:-10]:
                    old_backup.unlink()
            
        except Exception as e:
            self.logger.error(f"Failed to backup configuration: {str(e)}")
    
    async def _start_config_watcher(self) -> None:
        """Start configuration file watcher for hot reload"""
        while self.hot_reload_enabled:
            try:
                if Path(self.config_path).exists():
                    stat = Path(self.config_path).stat()
                    modified_time = datetime.fromtimestamp(stat.st_mtime)
                    
                    if modified_time > self.last_reload_time:
                        self.logger.info("Configuration file changed, reloading...")
                        self.reload_configuration()
                
                await asyncio.sleep(5)  # Check every 5 seconds
                
            except Exception as e:
                self.logger.error(f"Error in config watcher: {str(e)}")
                await asyncio.sleep(5)


# Export the classes for use in other modules
__all__ = [
    'ConfigurationManager',
    'StorageConfiguration',
    'StorageProviderConfig',
    'SecurityConfig',
    'PerformanceConfig',
    'BackupConfig',
    'MonitoringConfig',
    'EnvironmentType',
    'ConfigurationSource'
]
