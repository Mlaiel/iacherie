"""Observability Configuration Management

Advanced configuration management for the observability suite
with environment-specific settings, security configurations,
and performance tuning parameters.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  AVERTISSEMENT LÉGAL / LEGAL WARNING ⚠️
Ce code est la propriété intellectuelle exclusive de Fahed Mlaiel.
This code is the exclusive intellectual property of Fahed Mlaiel.
Toute utilisation non autorisée est strictement interdite.
Any unauthorized use is strictly prohibited.
"""
import json
import os
import logging
from dataclasses import dataclass, field, asdict
from datetime import timedelta
from typing import Dict, List, Optional, Any, Union, Callable
from pathlib import Path
from enum import Enum


class Environment(Enum):
    """Environment types"""    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"


class LogLevel(Enum):
    """Logging levels"""    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


@dataclass
class MonitoringConfig:
    """Monitoring configuration"""    enabled: bool = True
    real_time_enabled: bool = True
    predictive_enabled: bool = True
    anomaly_detection_enabled: bool = True
    
    # Intervals (seconds)
    metric_collection_interval: int = 30
    anomaly_detection_interval: int = 300  # 5 minutes
    prediction_interval: int = 3600  # 1 hour
    health_check_interval: int = 60
    
    # Retention periods
    metric_retention_hours: int = 24
    alert_retention_hours: int = 168  # 1 week
    incident_retention_days: int = 365
    
    # Thresholds
    cpu_warning_threshold: float = 70.0
    cpu_critical_threshold: float = 85.0
    memory_warning_threshold: float = 75.0
    memory_critical_threshold: float = 90.0
    disk_warning_threshold: float = 80.0
    disk_critical_threshold: float = 95.0
    response_time_warning: int = 1000  # ms
    response_time_critical: int = 3000  # ms
    error_rate_warning: float = 2.0  # %
    error_rate_critical: float = 5.0  # %
    
    # Buffer sizes
    metric_buffer_size: int = 10000
    alert_buffer_size: int = 1000
    incident_buffer_size: int = 500


@dataclass
class AnalyticsConfig:
    """Analytics configuration"""    enabled: bool = True
    content_analysis_enabled: bool = True
    user_behavior_enabled: bool = True
    roi_optimization_enabled: bool = True
    predictive_analytics_enabled: bool = True
    
    # Processing intervals
    real_time_interval: int = 60  # seconds
    batch_processing_interval: int = 3600  # 1 hour
    reporting_interval: int = 86400  # 1 day
    
    # Data retention
    analytics_data_retention_days: int = 90
    aggregated_data_retention_days: int = 365
    raw_data_retention_days: int = 30
    
    # Analysis parameters
    minimum_sample_size: int = 100
    confidence_threshold: float = 0.8
    anomaly_sensitivity: float = 0.1
    trend_analysis_window_days: int = 30
    
    # Feature flags
    enable_ml_predictions: bool = True
    enable_sentiment_analysis: bool = True
    enable_churn_prediction: bool = True
    enable_virality_prediction: bool = True


@dataclass
class ReportingConfig:
    """Reporting configuration"""    enabled: bool = True
    automated_reports_enabled: bool = True
    
    # Report generation
    executive_reports_enabled: bool = True
    detailed_analytics_enabled: bool = True
    compliance_reports_enabled: bool = True
    
    # Formats
    default_format: str = "pdf"
    supported_formats: List[str] = field(default_factory=lambda: ["pdf", "html", "excel", "json"])
    
    # Distribution
    email_distribution_enabled: bool = True
    dashboard_updates_enabled: bool = True
    api_webhook_enabled: bool = True
    
    # Scheduling
    default_frequency: str = "weekly"
    max_concurrent_reports: int = 5
    report_timeout_minutes: int = 30
    
    # Storage
    report_storage_days: int = 1095  # 3 years
    temp_file_cleanup_hours: int = 24


@dataclass
class SecurityConfig:
    """Security configuration"""    encryption_enabled: bool = True
    audit_logging_enabled: bool = True
    access_control_enabled: bool = True
    
    # Authentication
    require_authentication: bool = True
    session_timeout_minutes: int = 480  # 8 hours
    max_login_attempts: int = 3
    
    # Data protection
    encrypt_sensitive_data: bool = True
    mask_personal_data: bool = True
    gdpr_compliance_enabled: bool = True
    
    # API security
    rate_limiting_enabled: bool = True
    max_requests_per_minute: int = 100
    require_api_keys: bool = True
    
    # Monitoring security
    log_access_attempts: bool = True
    alert_on_suspicious_activity: bool = True
    monitor_data_exports: bool = True


@dataclass
class PerformanceConfig:
    """Performance configuration"""    # Threading
    max_worker_threads: int = 10
    thread_pool_size: int = 20
    
    # Caching
    enable_caching: bool = True
    cache_size_mb: int = 256
    cache_ttl_minutes: int = 60
    
    # Database
    connection_pool_size: int = 20
    query_timeout_seconds: int = 30
    batch_size: int = 1000
    
    # Memory management
    max_memory_usage_mb: int = 2048
    garbage_collection_threshold: float = 0.8
    
    # Processing limits
    max_concurrent_analyses: int = 5
    max_data_points_per_analysis: int = 100000
    analysis_timeout_minutes: int = 30


@dataclass
class IntegrationConfig:
    """Integration configuration"""    # Database integrations
    postgresql_enabled: bool = True
    mongodb_enabled: bool = False
    redis_enabled: bool = True
    
    # Cloud integrations
    aws_enabled: bool = False
    azure_enabled: bool = False
    gcp_enabled: bool = False
    
    # Monitoring tools
    prometheus_enabled: bool = False
    grafana_enabled: bool = False
    elastic_enabled: bool = False
    
    # Notification channels
    slack_enabled: bool = False
    email_enabled: bool = True
    webhook_enabled: bool = True
    
    # API configurations
    api_timeout_seconds: int = 30
    max_retry_attempts: int = 3
    retry_backoff_seconds: int = 5


@dataclass
class ObservabilityConfig:
    """Complete observability configuration"""    environment: Environment = Environment.DEVELOPMENT
    debug_mode: bool = False
    log_level: LogLevel = LogLevel.INFO
    
    # Component configurations
    monitoring: MonitoringConfig = field(default_factory=MonitoringConfig)
    analytics: AnalyticsConfig = field(default_factory=AnalyticsConfig)
    reporting: ReportingConfig = field(default_factory=ReportingConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    performance: PerformanceConfig = field(default_factory=PerformanceConfig)
    integrations: IntegrationConfig = field(default_factory=IntegrationConfig)
    
    # Application-specific settings
    application_name: str = "IA-Influencer-Agent"
    version: str = "3.0.0"
    deployment_region: str = "us-east-1"
    
    # Data sources
    data_sources: Dict[str, str] = field(default_factory=dict)
    
    # Custom settings
    custom_settings: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""        return asdict(self)
    
    def to_json(self) -> str:
        """Convert configuration to JSON string"""        return json.dumps(self.to_dict(), indent=2, default=str)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ObservabilityConfig':
        """Create configuration from dictionary"""        # Handle nested dataclasses
        if 'monitoring' in data and isinstance(data['monitoring'], dict):
            data['monitoring'] = MonitoringConfig(**data['monitoring'])
        
        if 'analytics' in data and isinstance(data['analytics'], dict):
            data['analytics'] = AnalyticsConfig(**data['analytics'])
        
        if 'reporting' in data and isinstance(data['reporting'], dict):
            data['reporting'] = ReportingConfig(**data['reporting'])
        
        if 'security' in data and isinstance(data['security'], dict):
            data['security'] = SecurityConfig(**data['security'])
        
        if 'performance' in data and isinstance(data['performance'], dict):
            data['performance'] = PerformanceConfig(**data['performance'])
        
        if 'integrations' in data and isinstance(data['integrations'], dict):
            data['integrations'] = IntegrationConfig(**data['integrations'])
        
        # Handle enums
        if 'environment' in data and isinstance(data['environment'], str):
            data['environment'] = Environment(data['environment'])
        
        if 'log_level' in data and isinstance(data['log_level'], str):
            data['log_level'] = LogLevel(data['log_level'])
        
        return cls(**data)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'ObservabilityConfig':
        """Create configuration from JSON string"""        data = json.loads(json_str)
        return cls.from_dict(data)
    
    def validate(self) -> List[str]:
        """Validate configuration and return list of issues"""        issues = []
        
        # Validate monitoring thresholds
        if self.monitoring.cpu_warning_threshold >= self.monitoring.cpu_critical_threshold:
            issues.append("CPU warning threshold should be less than critical threshold")
        
        if self.monitoring.memory_warning_threshold >= self.monitoring.memory_critical_threshold:
            issues.append("Memory warning threshold should be less than critical threshold")
        
        if self.monitoring.disk_warning_threshold >= self.monitoring.disk_critical_threshold:
            issues.append("Disk warning threshold should be less than critical threshold")
        
        # Validate intervals
        if self.monitoring.metric_collection_interval <= 0:
            issues.append("Metric collection interval must be positive")
        
        if self.analytics.real_time_interval <= 0:
            issues.append("Analytics real-time interval must be positive")
        
        # Validate buffer sizes
        if self.monitoring.metric_buffer_size <= 0:
            issues.append("Metric buffer size must be positive")
        
        # Validate performance limits
        if self.performance.max_worker_threads <= 0:
            issues.append("Max worker threads must be positive")
        
        if self.performance.connection_pool_size <= 0:
            issues.append("Connection pool size must be positive")
        
        return issues
    
    def apply_environment_overrides(self):
        """Apply environment-specific configuration overrides"""        if self.environment == Environment.PRODUCTION:
            # Production optimizations
            self.debug_mode = False
            self.log_level = LogLevel.WARNING
            self.security.require_authentication = True
            self.security.encrypt_sensitive_data = True
            self.performance.enable_caching = True
            self.monitoring.real_time_enabled = True
            
        elif self.environment == Environment.DEVELOPMENT:
            # Development settings
            self.debug_mode = True
            self.log_level = LogLevel.DEBUG
            self.security.require_authentication = False
            self.monitoring.metric_collection_interval = 10  # More frequent
            
        elif self.environment == Environment.TESTING:
            # Testing optimizations
            self.debug_mode = True
            self.log_level = LogLevel.INFO
            self.monitoring.metric_retention_hours = 1  # Short retention
            self.analytics.minimum_sample_size = 10  # Smaller samples
            
        elif self.environment == Environment.STAGING:
            # Staging - similar to production but with some debugging
            self.debug_mode = False
            self.log_level = LogLevel.INFO
            self.security.require_authentication = True
            self.monitoring.real_time_enabled = True


class ConfigurationManager:
    """Configuration manager for observability suite"""    
    def __init__(self, config_path: Optional[Path] = None):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.config_path = config_path or Path("config/observability.json")
        self._config = None
        self._watchers = []
    
    def load_config(self, config_file: Optional[Path] = None) -> ObservabilityConfig:
        """Load configuration from file or create default"""        try:
            config_file = config_file or self.config_path
            
            if config_file.exists():
                self.logger.info(f"Loading configuration from {config_file}")
                with open(config_file, 'r') as f:
                    config_data = json.load(f)
                config = ObservabilityConfig.from_dict(config_data)
            else:
                self.logger.info("Creating default configuration")
                config = self._create_default_config()
                self.save_config(config, config_file)
            
            # Apply environment overrides
            config.apply_environment_overrides()
            
            # Validate configuration
            issues = config.validate()
            if issues:
                self.logger.warning(f"Configuration issues found: {issues}")
            
            self._config = config
            return config
            
        except Exception as e:
            self.logger.error(f"Failed to load configuration: {str(e)}")
            # Return default configuration on error
            return self._create_default_config()
    
    def save_config(self, config: ObservabilityConfig, config_file: Optional[Path] = None):
        """Save configuration to file"""        try:
            config_file = config_file or self.config_path
            
            # Ensure directory exists
            config_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(config_file, 'w') as f:
                f.write(config.to_json())
            
            self.logger.info(f"Configuration saved to {config_file}")
            
        except Exception as e:
            self.logger.error(f"Failed to save configuration: {str(e)}")
    
    def get_config(self) -> ObservabilityConfig:
        """Get current configuration"""        if self._config is None:
            self._config = self.load_config()
        return self._config
    
    def update_config(self, updates: Dict[str, Any]) -> bool:
        """Update configuration with new values"""        try:
            current_config = self.get_config()
            config_dict = current_config.to_dict()
            
            # Apply updates (nested dictionary update)
            self._deep_update(config_dict, updates)
            
            # Create new configuration
            new_config = ObservabilityConfig.from_dict(config_dict)
            
            # Validate
            issues = new_config.validate()
            if issues:
                self.logger.error(f"Configuration update validation failed: {issues}")
                return False
            
            # Save and apply
            self.save_config(new_config)
            self._config = new_config
            
            # Notify watchers
            self._notify_watchers(new_config)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Configuration update failed: {str(e)}")
            return False
    
    def add_config_watcher(self, callback: Callable[[ObservabilityConfig], None]):
        """Add configuration change watcher"""        self._watchers.append(callback)
    
    def _notify_watchers(self, config: ObservabilityConfig):
        """Notify all configuration watchers"""        for watcher in self._watchers:
            try:
                watcher(config)
            except Exception as e:
                self.logger.error(f"Configuration watcher error: {str(e)}")
    
    def _deep_update(self, target: Dict[str, Any], source: Dict[str, Any]):
        """Recursively update nested dictionary"""        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                self._deep_update(target[key], value)
            else:
                target[key] = value
    
    def _create_default_config(self) -> ObservabilityConfig:
        """Create default configuration"""        config = ObservabilityConfig()
        
        # Set environment from environment variable
        env_name = os.getenv('OBSERVABILITY_ENV', 'development').lower()
        try:
            config.environment = Environment(env_name)
        except ValueError:
            config.environment = Environment.DEVELOPMENT
        
        # Apply data source configurations
        config.data_sources = {
            'postgresql': os.getenv('POSTGRES_URL', 'postgresql://localhost:5432/observability'),
            'redis': os.getenv('REDIS_URL', 'redis://localhost:6379'),
            'mongodb': os.getenv('MONGODB_URL', 'mongodb://localhost:27017/observability')
        }
        
        return config


# Global configuration manager instance
_config_manager = None

def get_config_manager() -> ConfigurationManager:
    """Get global configuration manager"""    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigurationManager()
    return _config_manager

def get_config() -> ObservabilityConfig:
    """Get current observability configuration"""    return get_config_manager().get_config()

def update_config(updates: Dict[str, Any]) -> bool:
    """Update observability configuration"""    return get_config_manager().update_config(updates)

def load_config_from_file(config_file: Path) -> ObservabilityConfig:
    """Load configuration from specific file"""    return get_config_manager().load_config(config_file)

# Export key classes and functions
__all__ = [
    'Environment',
    'LogLevel',
    'MonitoringConfig',
    'AnalyticsConfig', 
    'ReportingConfig',
    'SecurityConfig',
    'PerformanceConfig',
    'IntegrationConfig',
    'ObservabilityConfig',
    'ConfigurationManager',
    'get_config_manager',
    'get_config',
    'update_config',
    'load_config_from_file'
]
