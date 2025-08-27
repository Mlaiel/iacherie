"""
Configuration management for audio fingerprinting system.
Professional configuration handling with environment-specific settings.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent - Audio Protection Suite
License: Proprietary - All rights reserved

WARNING: This code is proprietary and protected by copyright.
Any unauthorized use, reproduction, or distribution is strictly prohibited.
Contact: Fahed Mlaiel (mlaiel@live.de) for licensing agreements.
"""

import os
import json
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from pathlib import Path
import yaml
from enum import Enum

logger = logging.getLogger(__name__)


class Environment(Enum):
    """Environment types."""
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"


class ProtectionLevel(Enum):
    """Content protection levels."""
    BASIC = "basic"
    STANDARD = "standard"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"


@dataclass
class AudioProcessingConfig:
    """Configuration for audio processing parameters."""
    
    sample_rate: int = 22050
    hop_length: int = 512
    n_fft: int = 2048
    n_mels: int = 128
    max_duration_seconds: float = 300.0  # 5 minutes max
    min_duration_seconds: float = 1.0    # 1 second min
    supported_formats: List[str] = field(default_factory=lambda: [
        'mp3', 'wav', 'flac', 'm4a', 'aac', 'ogg', 'wma'
    ])
    bit_depth_preference: int = 16
    normalize_audio: bool = True
    remove_silence: bool = False
    apply_pre_emphasis: bool = False


@dataclass
class FingerprintingConfig:
    """Configuration for fingerprinting algorithms."""
    
    hash_size: int = 64
    chromaprint_algorithm: int = 1  # ALGORITHM_DEFAULT
    use_spectral_features: bool = True
    use_perceptual_hash: bool = True
    use_chromaprint: bool = True
    use_mfcc_features: bool = True
    feature_dimensions: int = 256
    enable_compression: bool = True
    compression_level: int = 6
    similarity_threshold: float = 0.80
    adaptive_thresholds: bool = True
    multi_resolution_analysis: bool = True


@dataclass
class MatchingConfig:
    """Configuration for fingerprint matching."""
    
    max_candidates_per_query: int = 10000
    max_results_per_query: int = 100
    default_similarity_threshold: float = 0.80
    enable_temporal_matching: bool = True
    enable_spectral_matching: bool = True
    enable_perceptual_matching: bool = True
    match_timeout_seconds: float = 30.0
    parallel_workers: int = 4
    cache_query_results: bool = True
    cache_ttl_seconds: int = 300


@dataclass
class DatabaseConfig:
    """Configuration for database connections."""
    
    url: str = "postgresql://user:pass@localhost/fingerprints"
    pool_size: int = 20
    max_overflow: int = 30
    pool_timeout: int = 30
    pool_recycle: int = 3600
    enable_query_logging: bool = False
    enable_performance_tracking: bool = True
    batch_insert_size: int = 100
    connection_retry_attempts: int = 3
    connection_retry_delay: float = 1.0


@dataclass
class SecurityConfig:
    """Configuration for security settings."""
    
    enable_user_isolation: bool = True
    require_authentication: bool = True
    rate_limit_per_minute: int = 60
    max_file_size_mb: float = 50.0
    allowed_content_types: List[str] = field(default_factory=lambda: [
        'audio/mpeg', 'audio/wav', 'audio/flac', 'audio/mp4', 
        'audio/aac', 'audio/ogg', 'audio/x-ms-wma'
    ])
    scan_for_malware: bool = True
    encrypt_stored_data: bool = False  # Would be True in production
    audit_all_operations: bool = True


@dataclass
class PerformanceConfig:
    """Configuration for performance optimization."""
    
    enable_caching: bool = True
    cache_size_limit: int = 1000
    enable_async_processing: bool = True
    max_concurrent_fingerprints: int = 10
    enable_batch_processing: bool = True
    batch_processing_delay: float = 5.0
    enable_gpu_acceleration: bool = False  # Would detect GPU availability
    memory_limit_mb: int = 2048
    disk_cache_path: Optional[str] = None


@dataclass
class MonitoringConfig:
    """Configuration for monitoring and metrics."""
    
    enable_metrics_collection: bool = True
    metrics_interval_seconds: int = 60
    enable_performance_profiling: bool = False
    log_level: str = "INFO"
    log_format: str = "json"
    enable_health_checks: bool = True
    health_check_interval: int = 30
    alert_on_errors: bool = True
    alert_threshold_error_rate: float = 0.05


class FingerprintingConfigManager:
    """
    Comprehensive configuration manager for the fingerprinting system.
    Handles environment-specific settings and runtime configuration updates.
    """
    
    def __init__(self, config_path: Optional[str] = None, environment: Optional[str] = None):
        """Initialize the configuration manager."""
        self.config_path = config_path
        self.environment = Environment(environment or os.getenv('ENVIRONMENT', 'development'))
        
        # Configuration components
        self.audio_processing: AudioProcessingConfig = AudioProcessingConfig()
        self.fingerprinting: FingerprintingConfig = FingerprintingConfig()
        self.matching: MatchingConfig = MatchingConfig()
        self.database: DatabaseConfig = DatabaseConfig()
        self.security: SecurityConfig = SecurityConfig()
        self.performance: PerformanceConfig = PerformanceConfig()
        self.monitoring: MonitoringConfig = MonitoringConfig()
        
        # Runtime settings
        self._runtime_overrides: Dict[str, Any] = {}
        self._config_watchers: List = []
        
        # Load configuration
        self._load_configuration()
        
        logger.info("FingerprintingConfigManager initialized for %s environment", 
                   self.environment.value)
    
    def _load_configuration(self):
        """Load configuration from various sources."""
        # Load from environment variables
        self._load_from_environment()
        
        # Load from configuration file if provided
        if self.config_path:
            self._load_from_file(self.config_path)
        
        # Apply environment-specific overrides
        self._apply_environment_overrides()
        
        # Validate configuration
        self._validate_configuration()
    
    def _load_from_environment(self):
        """Load configuration from environment variables."""
        # Audio processing settings
        if os.getenv('AUDIO_SAMPLE_RATE'):
            self.audio_processing.sample_rate = int(os.getenv('AUDIO_SAMPLE_RATE'))
        
        if os.getenv('AUDIO_MAX_DURATION'):
            self.audio_processing.max_duration_seconds = float(os.getenv('AUDIO_MAX_DURATION'))
        
        # Database settings
        if os.getenv('DATABASE_URL'):
            self.database.url = os.getenv('DATABASE_URL')
        
        if os.getenv('DATABASE_POOL_SIZE'):
            self.database.pool_size = int(os.getenv('DATABASE_POOL_SIZE'))
        
        # Security settings
        if os.getenv('MAX_FILE_SIZE_MB'):
            self.security.max_file_size_mb = float(os.getenv('MAX_FILE_SIZE_MB'))
        
        if os.getenv('RATE_LIMIT_PER_MINUTE'):
            self.security.rate_limit_per_minute = int(os.getenv('RATE_LIMIT_PER_MINUTE'))
        
        # Performance settings
        if os.getenv('ENABLE_GPU_ACCELERATION'):
            self.performance.enable_gpu_acceleration = os.getenv('ENABLE_GPU_ACCELERATION').lower() == 'true'
        
        if os.getenv('MEMORY_LIMIT_MB'):
            self.performance.memory_limit_mb = int(os.getenv('MEMORY_LIMIT_MB'))
        
        # Monitoring settings
        if os.getenv('LOG_LEVEL'):
            self.monitoring.log_level = os.getenv('LOG_LEVEL')
        
        logger.debug("Configuration loaded from environment variables")
    
    def _load_from_file(self, config_path: str):
        """Load configuration from YAML or JSON file."""
        try:
            config_file = Path(config_path)
            
            if not config_file.exists():
                logger.warning("Configuration file not found: %s", config_path)
                return
            
            with open(config_file, 'r', encoding='utf-8') as f:
                if config_file.suffix.lower() in ['.yml', '.yaml']:
                    config_data = yaml.safe_load(f)
                else:
                    config_data = json.load(f)
            
            # Apply configuration data to respective components
            self._apply_config_data(config_data)
            
            logger.info("Configuration loaded from file: %s", config_path)
            
        except Exception as e:
            logger.error("Error loading configuration file %s: %s", config_path, str(e))
    
    def _apply_config_data(self, config_data: Dict[str, Any]):
        """Apply configuration data to configuration objects."""
        try:
            # Audio processing configuration
            if 'audio_processing' in config_data:
                audio_config = config_data['audio_processing']
                for key, value in audio_config.items():
                    if hasattr(self.audio_processing, key):
                        setattr(self.audio_processing, key, value)
            
            # Fingerprinting configuration
            if 'fingerprinting' in config_data:
                fp_config = config_data['fingerprinting']
                for key, value in fp_config.items():
                    if hasattr(self.fingerprinting, key):
                        setattr(self.fingerprinting, key, value)
            
            # Matching configuration
            if 'matching' in config_data:
                match_config = config_data['matching']
                for key, value in match_config.items():
                    if hasattr(self.matching, key):
                        setattr(self.matching, key, value)
            
            # Database configuration
            if 'database' in config_data:
                db_config = config_data['database']
                for key, value in db_config.items():
                    if hasattr(self.database, key):
                        setattr(self.database, key, value)
            
            # Security configuration
            if 'security' in config_data:
                sec_config = config_data['security']
                for key, value in sec_config.items():
                    if hasattr(self.security, key):
                        setattr(self.security, key, value)
            
            # Performance configuration
            if 'performance' in config_data:
                perf_config = config_data['performance']
                for key, value in perf_config.items():
                    if hasattr(self.performance, key):
                        setattr(self.performance, key, value)
            
            # Monitoring configuration
            if 'monitoring' in config_data:
                mon_config = config_data['monitoring']
                for key, value in mon_config.items():
                    if hasattr(self.monitoring, key):
                        setattr(self.monitoring, key, value)
            
        except Exception as e:
            logger.error("Error applying configuration data: %s", str(e))
    
    def _apply_environment_overrides(self):
        """Apply environment-specific configuration overrides."""
        if self.environment == Environment.PRODUCTION:
            # Production optimizations
            self.security.encrypt_stored_data = True
            self.security.audit_all_operations = True
            self.monitoring.enable_performance_profiling = False
            self.monitoring.log_level = "WARNING"
            self.database.enable_query_logging = False
            
        elif self.environment == Environment.DEVELOPMENT:
            # Development settings
            self.security.encrypt_stored_data = False
            self.monitoring.enable_performance_profiling = True
            self.monitoring.log_level = "DEBUG"
            self.database.enable_query_logging = True
            
        elif self.environment == Environment.TESTING:
            # Testing optimizations
            self.performance.enable_caching = False
            self.monitoring.log_level = "ERROR"
            self.database.pool_size = 5
            
        logger.debug("Applied %s environment overrides", self.environment.value)
    
    def _validate_configuration(self):
        """Validate configuration settings."""
        errors = []
        
        # Validate audio processing
        if self.audio_processing.sample_rate <= 0:
            errors.append("Invalid sample rate")
        
        if self.audio_processing.max_duration_seconds <= 0:
            errors.append("Invalid max duration")
        
        # Validate fingerprinting
        if self.fingerprinting.hash_size <= 0:
            errors.append("Invalid hash size")
        
        if not (0.0 <= self.fingerprinting.similarity_threshold <= 1.0):
            errors.append("Invalid similarity threshold")
        
        # Validate matching
        if self.matching.max_candidates_per_query <= 0:
            errors.append("Invalid max candidates per query")
        
        # Validate database
        if not self.database.url:
            errors.append("Database URL is required")
        
        # Validate security
        if self.security.max_file_size_mb <= 0:
            errors.append("Invalid max file size")
        
        if errors:
            error_message = "Configuration validation errors: " + ", ".join(errors)
            logger.error(error_message)
            raise ValueError(error_message)
        
        logger.debug("Configuration validation passed")
    
    def get_config_dict(self) -> Dict[str, Any]:
        """Get complete configuration as dictionary."""
        return {
            'environment': self.environment.value,
            'audio_processing': self.audio_processing.__dict__,
            'fingerprinting': self.fingerprinting.__dict__,
            'matching': self.matching.__dict__,
            'database': self.database.__dict__,
            'security': self.security.__dict__,
            'performance': self.performance.__dict__,
            'monitoring': self.monitoring.__dict__
        }
    
    def update_runtime_setting(self, section: str, key: str, value: Any):
        """Update a runtime configuration setting."""
        try:
            config_section = getattr(self, section)
            if hasattr(config_section, key):
                setattr(config_section, key, value)
                
                # Track runtime override
                override_key = f"{section}.{key}"
                self._runtime_overrides[override_key] = value
                
                logger.info("Updated runtime setting %s = %s", override_key, value)
            else:
                logger.warning("Unknown configuration key: %s.%s", section, key)
                
        except Exception as e:
            logger.error("Error updating runtime setting %s.%s: %s", section, key, str(e))
    
    def get_protection_level_config(self, level: ProtectionLevel) -> Dict[str, Any]:
        """Get configuration optimized for specific protection level."""
        base_config = self.get_config_dict()
        
        if level == ProtectionLevel.BASIC:
            # Optimize for speed over accuracy
            base_config['fingerprinting']['use_mfcc_features'] = False
            base_config['fingerprinting']['multi_resolution_analysis'] = False
            base_config['matching']['enable_temporal_matching'] = False
            
        elif level == ProtectionLevel.PREMIUM:
            # Enhanced accuracy
            base_config['fingerprinting']['feature_dimensions'] = 512
            base_config['matching']['enable_temporal_matching'] = True
            base_config['matching']['max_candidates_per_query'] = 20000
            
        elif level == ProtectionLevel.ENTERPRISE:
            # Maximum protection and features
            base_config['fingerprinting']['feature_dimensions'] = 1024
            base_config['fingerprinting']['multi_resolution_analysis'] = True
            base_config['matching']['enable_temporal_matching'] = True
            base_config['matching']['max_candidates_per_query'] = 50000
            base_config['security']['audit_all_operations'] = True
        
        return base_config
    
    def export_config(self, output_path: str, format: str = 'yaml'):
        """Export current configuration to file."""
        try:
            config_dict = self.get_config_dict()
            output_file = Path(output_path)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                if format.lower() == 'yaml':
                    yaml.dump(config_dict, f, default_flow_style=False)
                else:
                    json.dump(config_dict, f, indent=2, default=str)
            
            logger.info("Configuration exported to %s", output_path)
            
        except Exception as e:
            logger.error("Error exporting configuration: %s", str(e))
    
    def get_runtime_overrides(self) -> Dict[str, Any]:
        """Get current runtime configuration overrides."""
        return self._runtime_overrides.copy()
    
    def reset_to_defaults(self):
        """Reset configuration to default values."""
        self.audio_processing = AudioProcessingConfig()
        self.fingerprinting = FingerprintingConfig()
        self.matching = MatchingConfig()
        self.database = DatabaseConfig()
        self.security = SecurityConfig()
        self.performance = PerformanceConfig()
        self.monitoring = MonitoringConfig()
        
        self._runtime_overrides.clear()
        
        # Reapply environment settings
        self._load_from_environment()
        self._apply_environment_overrides()
        
        logger.info("Configuration reset to defaults")


# Global configuration instance
config_manager = FingerprintingConfigManager()


def get_config() -> FingerprintingConfigManager:
    """Get the global configuration manager instance."""
    return config_manager


def get_audio_config() -> AudioProcessingConfig:
    """Get audio processing configuration."""
    return config_manager.audio_processing


def get_fingerprinting_config() -> FingerprintingConfig:
    """Get fingerprinting configuration."""
    return config_manager.fingerprinting


def get_matching_config() -> MatchingConfig:
    """Get matching configuration."""
    return config_manager.matching


def get_database_config() -> DatabaseConfig:
    """Get database configuration."""
    return config_manager.database


def get_security_config() -> SecurityConfig:
    """Get security configuration."""
    return config_manager.security


def get_performance_config() -> PerformanceConfig:
    """Get performance configuration."""
    return config_manager.performance


def get_monitoring_config() -> MonitoringConfig:
    """Get monitoring configuration."""
    return config_manager.monitoring
