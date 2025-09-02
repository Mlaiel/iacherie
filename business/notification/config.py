# -*- coding: utf-8 -*-
"""IA Influencer Agent - Advanced Business Models Configuration

This module provides comprehensive configuration management for the notification system,
including business rules, templates, channels, and performance settings.

LEGAL WARNING:
This code is protected by copyright and proprietary rights. 
Any unauthorized reproduction, distribution, or commercial use is strictly prohibited.
Violations will be prosecuted to the full extent of the law.
Developed by Mlaiel for IA Influencer Agent Platform.

Architecture Pattern: Configuration Management with Business Rules
Processing Level: Enterprise Configuration Management
Business Logic Integration: Complete Configuration Control
Configuration Design: Multi-Environment with Business Context
"""

import os
import json
import yaml
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path


class EnvironmentType(Enum):
    """
Environment types for configuration."""

    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"
    SANDBOX = "sandbox"


class ConfigurationCategory(Enum):
    """Configuration categories."""

    BUSINESS_RULES = "business_rules"
    NOTIFICATION_SETTINGS = "notification_settings"
    CHANNEL_CONFIG = "channel_config"
    TEMPLATE_CONFIG = "template_config"
    SECURITY_CONFIG = "security_config"
    PERFORMANCE_CONFIG = "performance_config"
    INTEGRATION_CONFIG = "integration_config"
    ANALYTICS_CONFIG = "analytics_config"


@dataclass
class ConfigurationSource:
    """Configuration source information."""
    source_type: str  # file, database, api, environment
    source_path: str
    priority: int = 100
    is_encrypted: bool = False
    last_updated: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    checksum: Optional[str] = None
    version: str = "1.0.0"


@dataclass
class BusinessRuleConfig:
    """Business rule configuration."""
    rule_name: str
    rule_category: str
    rule_priority: int
    conditions: Dict[str, Any]
    actions: List[Dict[str, Any]]
    enabled: bool = True
    environment_specific: bool = False
    applicable_environments: List[str] = field(default_factory=list)
    effective_date: Optional[datetime] = None
    expiration_date: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ChannelConfiguration:
    """
Channel-specific configuration."""
    channel_name: str
    provider: str
    enabled: bool = True
    
    # Connection Settings
    connection_config: Dict[str, Any] = field(default_factory=dict)
    authentication: Dict[str, str] = field(default_factory=dict)
    endpoints: Dict[str, str] = field(default_factory=dict)
    
    # Performance Settings
    rate_limit: Dict[str, int] = field(default_factory=dict)
    timeout_seconds: int = 30
    max_retries: int = 3
    retry_delay_seconds: int = 5
    
    # Message Settings
    max_message_size: int = 10000
    supported_formats: List[str] = field(default_factory=list)
    template_support: bool = True
    
    # Business Settings
    cost_per_message: float = 0.0
    priority_support: bool = True
    delivery_confirmation: bool = True
    
    # Monitoring Settings
    health_check_enabled: bool = True
    health_check_interval: int = 300
    alert_thresholds: Dict[str, float] = field(default_factory=dict)


@dataclass
class TemplateConfiguration:
    """
Template system configuration."""
    template_engine: str = "jinja2"
    template_directory: str = "templates"
    cache_enabled: bool = True
    cache_ttl_seconds: int = 3600
    
    # Multi-language Support
    default_language: str = "en"
    supported_languages: List[str] = field(default_factory=lambda: ["en", "de", "fr"])
    fallback_language: str = "en"
    
    # Template Categories
    template_categories: Dict[str, List[str]] = field(default_factory=dict)
    template_inheritance: bool = True
    
    # Personalization Settings
    personalization_enabled: bool = True
    personalization_rules: Dict[str, Any] = field(default_factory=dict)
    
    # Security Settings
    template_sandboxing: bool = True
    allowed_functions: List[str] = field(default_factory=list)
    blocked_functions: List[str] = field(default_factory=list)


@dataclass
class SecurityConfiguration:
    """Security configuration for notifications."""
    
    # Authentication & Authorization
    require_authentication: bool = True
    api_key_required: bool = True
    jwt_enabled: bool = True
    oauth_enabled: bool = False
    
    # Data Protection
    encrypt_sensitive_data: bool = True
    encryption_algorithm: str = "AES-256-GCM"
    key_rotation_enabled: bool = True
    key_rotation_days: int = 90
    
    # Access Control
    role_based_access: bool = True
    permission_levels: List[str] = field(default_factory=lambda: ["read", "write", "admin"])
    ip_whitelist_enabled: bool = False
    ip_whitelist: List[str] = field(default_factory=list)
    
    # Content Security
    content_filtering: bool = True
    spam_detection: bool = True
    malware_scanning: bool = True
    
    # Audit & Logging
    audit_logging: bool = True
    detailed_logging: bool = True
    log_retention_days: int = 365
    
    # Rate Limiting
    global_rate_limit: Dict[str, int] = field(default_factory=dict)
    user_rate_limit: Dict[str, int] = field(default_factory=dict)
    ip_rate_limit: Dict[str, int] = field(default_factory=dict)


@dataclass
class PerformanceConfiguration:
    """Performance optimization configuration."""
    
    # Processing Settings
    max_concurrent_notifications: int = 1000
    batch_processing_enabled: bool = True
    batch_size: int = 100
    processing_timeout_seconds: int = 300
    
    # Queue Settings
    queue_type: str = "redis"  # redis, rabbitmq, kafka
    queue_size_limit: int = 100000
    dead_letter_queue_enabled: bool = True
    priority_queue_enabled: bool = True
    
    # Cache Settings
    cache_enabled: bool = True
    cache_type: str = "redis"
    cache_ttl_seconds: int = 3600
    cache_max_size: int = 10000
    
    # Database Settings
    connection_pool_size: int = 20
    connection_timeout_seconds: int = 30
    query_timeout_seconds: int = 60
    
    # Monitoring Settings
    metrics_collection: bool = True
    performance_monitoring: bool = True
    alert_on_degradation: bool = True
    
    # Thresholds
    warning_thresholds: Dict[str, float] = field(default_factory=dict)
    critical_thresholds: Dict[str, float] = field(default_factory=dict)


@dataclass
class IntegrationConfiguration:
    """External integration configuration."""
    
    # AI Services
    ai_personalization_enabled: bool = True
    ai_priority_classification: bool = True
    ai_content_optimization: bool = True
    
    # Analytics Services
    analytics_enabled: bool = True
    analytics_provider: str = "internal"
    analytics_api_key: Optional[str] = None
    
    # Business Intelligence
    bi_integration: bool = True
    bi_dashboard_enabled: bool = True
    bi_reporting_enabled: bool = True
    
    # External APIs
    external_apis: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    webhook_endpoints: List[str] = field(default_factory=list)
    
    # Third-party Services
    crm_integration: bool = False
    crm_provider: Optional[str] = None
    
    marketing_automation: bool = False
    marketing_provider: Optional[str] = None


class NotificationConfigurationManager:
    """
    Advanced configuration management for the notification system.
    
    Provides comprehensive configuration loading, validation, and management
    with support for multiple environments, business rules, and real-time updates.
    """
    
    def __init__(
        self,
        environment: EnvironmentType = EnvironmentType.DEVELOPMENT,
        config_directory: Optional[str] = None
    ):
        self.environment = environment
        self.config_directory = Path(config_directory) if config_directory else Path.cwd() / "config"
        self._configurations: Dict[str, Any] = {}
        self._sources: Dict[str, ConfigurationSource] = {}
        self._watchers: Dict[str, Any] = {}
        self._validators: Dict[str, callable] = {}
        
        # Initialize default configurations
        self._initialize_default_configurations()
    
    def _initialize_default_configurations(self):
        """Initialize default configuration values."""
        
        # Business Rules Configuration
        self._configurations[ConfigurationCategory.BUSINESS_RULES.value] = {
            "content_protection_rules": [
                BusinessRuleConfig(
                    rule_name="urgent_copyright_alert",
                    rule_category="content_protection",
                    rule_priority=100,
                    conditions={
                        "notification_type": "copyright_infringement",
                        "confidence_score": {"$gte": 0.8}
                    },
                    actions=[
                        {"type": "set_priority", "value": "critical"},
                        {"type": "add_channels", "channels": ["sms", "push", "email"]},
                        {"type": "set_escalation", "escalate_after": 300}
                    ]
                ),
                BusinessRuleConfig(
                    rule_name="monetization_opportunity",
                    rule_category="monetization",
                    rule_priority=80,
                    conditions={
                        "notification_type": "monetization_opportunity",
                        "revenue_potential": {"$gte": 1000}
                    },
                    actions=[
                        {"type": "set_priority", "value": "urgent"},
                        {"type": "add_personalization", "level": "high"},
                        {"type": "track_conversion", "enabled": True}
                    ]
                )
            ],
            "collaboration_rules": [
                BusinessRuleConfig(
                    rule_name="collaboration_match_quality",
                    rule_category="collaboration",
                    rule_priority=60,
                    conditions={
                        "notification_type": "collaboration_match",
                        "match_score": {"$gte": 0.7}
                    },
                    actions=[
                        {"type": "set_priority", "value": "high"},
                        {"type": "add_follow_up", "delay_hours": 48}
                    ]
                )
            ]
        }
        
        # Channel Configurations
        self._configurations[ConfigurationCategory.CHANNEL_CONFIG.value] = {
            "email": ChannelConfiguration(
                channel_name="email",
                provider="sendgrid",
                connection_config={
                    "api_key": "${SENDGRID_API_KEY}",
                    "from_email": "noreply@ia-influencer.com",
                    "from_name": "IA Influencer Agent"
                },
                rate_limit={"per_second": 10, "per_minute": 600, "per_hour": 10000},
                max_message_size=50000,
                supported_formats=["text", "html", "markdown"],
                cost_per_message=0.001
            ),
            "sms": ChannelConfiguration(
                channel_name="sms",
                provider="twilio",
                connection_config={
                    "account_sid": "${TWILIO_ACCOUNT_SID}",
                    "auth_token": "${TWILIO_AUTH_TOKEN}",
                    "from_number": "${TWILIO_FROM_NUMBER}"
                },
                rate_limit={"per_second": 1, "per_minute": 60, "per_hour": 1000},
                max_message_size=1600,
                supported_formats=["text"],
                cost_per_message=0.01
            ),
            "push": ChannelConfiguration(
                channel_name="push",
                provider="fcm",
                connection_config={
                    "server_key": "${FCM_SERVER_KEY}",
                    "project_id": "${FCM_PROJECT_ID}"
                },
                rate_limit={"per_second": 100, "per_minute": 6000, "per_hour": 100000},
                max_message_size=4096,
                supported_formats=["json"],
                cost_per_message=0.0001
            )
        }
        
        # Template Configuration
        self._configurations[ConfigurationCategory.TEMPLATE_CONFIG.value] = TemplateConfiguration(
            template_categories={
                "content_protection": [
                    "copyright_alert",
                    "protection_notice",
                    "rights_violation"
                ],
                "monetization": [
                    "revenue_opportunity",
                    "payment_confirmation",
                    "earnings_report"
                ],
                "collaboration": [
                    "partnership_invitation",
                    "collaboration_match",
                    "project_proposal"
                ]
            },
            personalization_rules={
                "creator_type_adaptation": True,
                "language_localization": True,
                "timezone_optimization": True,
                "engagement_history": True
            }
        )
        
        # Security Configuration
        self._configurations[ConfigurationCategory.SECURITY_CONFIG.value] = SecurityConfiguration(
            global_rate_limit={"per_minute": 1000, "per_hour": 10000},
            user_rate_limit={"per_minute": 60, "per_hour": 500},
            ip_rate_limit={"per_minute": 100, "per_hour": 1000}
        )
        
        # Performance Configuration
        self._configurations[ConfigurationCategory.PERFORMANCE_CONFIG.value] = PerformanceConfiguration(
            warning_thresholds={
                "processing_time": 5.0,
                "queue_size": 1000,
                "error_rate": 0.02,
                "delivery_rate": 0.95
            },
            critical_thresholds={
                "processing_time": 30.0,
                "queue_size": 10000,
                "error_rate": 0.10,
                "delivery_rate": 0.85
            }
        )
        
        # Integration Configuration
        self._configurations[ConfigurationCategory.INTEGRATION_CONFIG.value] = IntegrationConfiguration(
            external_apis={
                "content_analysis": {
                    "endpoint": "${CONTENT_ANALYSIS_API_URL}",
                    "api_key": "${CONTENT_ANALYSIS_API_KEY}",
                    "timeout": 30
                },
                "collaboration_matching": {
                    "endpoint": "${COLLABORATION_API_URL}",
                    "api_key": "${COLLABORATION_API_KEY}",
                    "timeout": 15
                }
            }
        )
    
    def get_configuration(self, category: ConfigurationCategory) -> Dict[str, Any]:
        """Get configuration for specified category."""
        return self._configurations.get(category.value, {})
    
    def export_configuration(
        self,
        category: Optional[ConfigurationCategory] = None,
        format: str = "yaml"
    ) -> str:
        """Export configuration as string in specified format."""
        if category:
            data = {category.value: self.get_configuration(category)}
        else:
            data = self._configurations
        
        if format == "yaml":
            return yaml.safe_dump(data, default_flow_style=False)
        elif format == "json":
            return json.dumps(data, indent=2)
        else:
            raise ValueError(f"Unsupported export format: {format}")


# Global configuration manager instance
config_manager = NotificationConfigurationManager()


# Configuration constants for easy access
DEFAULT_CONFIG = {
    "MAX_RETRY_ATTEMPTS": 3,
    "DEFAULT_TIMEOUT": 30,
    "RATE_LIMIT_PER_MINUTE": 1000,
    "BATCH_SIZE": 100,
    "CACHE_TTL": 3600,
    "DEFAULT_LANGUAGE": "en",
    "SUPPORTED_LANGUAGES": ["en", "de", "fr", "es", "it"],
    "DEFAULT_PRIORITY": "medium",
    "BUSINESS_HOURS_START": "09:00",
    "BUSINESS_HOURS_END": "18:00"
}

from typing import Dict, List, Optional, Any, Union
import os
import json
import logging
from dataclasses import dataclass, field
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class ChannelConfig:
    """Channel-specific configuration."""
    enabled: bool = True
    provider: Optional[str] = None
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    endpoint_url: Optional[str] = None
    rate_limit: int = 100  # requests per minute
    retry_attempts: int = 3
    retry_delay: float = 1.0  # seconds
    timeout: int = 30  # seconds
    cost_per_notification: Optional[float] = None
    priority_multiplier: float = 1.0
    batch_size: int = 10
    health_check_enabled: bool = True
    health_check_interval: int = 300  # seconds
    fallback_channels: Optional[List[str]] = None
    custom_headers: Optional[Dict[str, str]] = None
    webhook_config: Optional[Dict[str, Any]] = None


@dataclass
class AIConfig:
    """
AI features configuration."""
    enabled: bool = True
    priority_classification_enabled: bool = True
    personalization_enabled: bool = True
    template_optimization_enabled: bool = True
    delivery_optimization_enabled: bool = True
    model_version: str = "2.0"
    confidence_threshold: float = 0.75
    fallback_to_manual: bool = True
    learning_enabled: bool = True
    model_update_interval: int = 86400  # seconds
    batch_processing_enabled: bool = True
    batch_size: int = 100
    performance_monitoring: bool = True
    a_b_testing_enabled: bool = True
    personalization_cache_ttl: int = 3600  # seconds


@dataclass
class SecurityConfig:
    """Security and authentication configuration."""
    encryption_enabled: bool = True
    encryption_algorithm: str = "AES-256"
    jwt_secret: Optional[str] = None
    jwt_expiry: int = 3600  # seconds
    api_key_required: bool = True
    rate_limiting_enabled: bool = True
    rate_limit_requests: int = 1000  # per hour
    rate_limit_burst: int = 50
    audit_logging_enabled: bool = True
    data_retention_days: int = 90
    pii_anonymization: bool = True
    gdpr_compliance: bool = True
    access_control_enabled: bool = True
    allowed_origins: List[str] = field(default_factory=list)
    webhook_signature_validation: bool = True


@dataclass
class AnalyticsConfig:
    """Analytics and monitoring configuration."""
    enabled: bool = True
    real_time_tracking: bool = True
    performance_monitoring: bool = True
    business_intelligence: bool = True
    metrics_retention_days: int = 365
    detailed_logging: bool = True
    export_enabled: bool = True
    dashboard_enabled: bool = True
    alerting_enabled: bool = True
    custom_metrics: bool = True
    data_warehouse_sync: bool = False
    streaming_analytics: bool = True
    ml_insights: bool = True
    predictive_analytics: bool = True


@dataclass
class WorkflowConfig:
    """
Workflow orchestration configuration."""
    enabled: bool = True
    max_workflow_steps: int = 20
    step_timeout: int = 300  # seconds
    workflow_timeout: int = 3600  # seconds
    retry_failed_workflows: bool = True
    max_workflow_retries: int = 3
    parallel_execution: bool = True
    max_parallel_workflows: int = 10
    persistence_enabled: bool = True
    recovery_enabled: bool = True
    monitoring_enabled: bool = True
    conditional_logic: bool = True
    dynamic_routing: bool = True


@dataclass
class PerformanceConfig:
    """
Performance optimization configuration."""
    caching_enabled: bool = True
    cache_ttl: int = 3600  # seconds
    cache_max_size: int = 10000
    connection_pooling: bool = True
    connection_pool_size: int = 20
    max_concurrent_deliveries: int = 100
    batch_processing: bool = True
    optimal_batch_size: int = 50
    queue_monitoring: bool = True
    load_balancing: bool = True
    auto_scaling: bool = True
    memory_optimization: bool = True
    compression_enabled: bool = True
    cdn_enabled: bool = False


class NotificationConfig:
    """
    Enterprise notification system configuration.
    
    Provides comprehensive configuration management for all aspects of the
    notification system including channels, AI features, security, analytics,
    and performance optimization.
    """
    
    def __init__(self, config_data: Optional[Dict[str, Any]] = None):
        """
        Initialize notification configuration.
        
        Args:
            config_data: Optional configuration dictionary
        """
        # Load configuration from various sources
        self._load_configuration(config_data)
        
        # Initialize component configurations
        self._initialize_component_configs()
        
        # Validate configuration
        self._validate_configuration()
        
        logger.info(f"NotificationConfig initialized for environment: {self.environment}")
    
    def _load_configuration(self, config_data: Optional[Dict[str, Any]]):
        """Load configuration from multiple sources."""
        # Default configuration
        self._config = self._get_default_config()
        
        # Load from environment variables
        self._load_from_environment()
        
        # Load from config file if exists
        self._load_from_file()
        
        # Apply provided config data
        if config_data:
            self._apply_config_override(config_data)
        
        # Set environment-specific settings
        self.environment = self._config.get("environment", "development")
        self.debug = self._config.get("debug", self.environment == "development")
        self.log_level = self._config.get("log_level", "DEBUG" if self.debug else "INFO")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration values."""
        return {
            "environment": "development",
            "debug": True,
            "log_level": "DEBUG",
            "version": "2.0.0",
            
            # Core system settings
            "system": {
                "max_notifications_per_minute": 1000,
                "queue_size": 10000,
                "worker_threads": 10,
                "health_check_interval": 60,
                "graceful_shutdown_timeout": 30
            },
            
            # Database settings
            "database": {
                "url": os.getenv("DATABASE_URL", "postgresql://user:pass@localhost/notifications"),
                "pool_size": 20,
                "max_overflow": 30,
                "pool_timeout": 30,
                "echo": False
            },
            
            # Redis settings
            "redis": {
                "url": os.getenv("REDIS_URL", "redis://localhost:6379/0"),
                "pool_size": 10,
                "socket_timeout": 5,
                "retry_on_timeout": True
            },
            
            # Channel configurations
            "channels": {
                "email": {
                    "enabled": True,
                    "provider": "sendgrid",
                    "api_key": os.getenv("SENDGRID_API_KEY"),
                    "rate_limit": 600,  # per minute
                    "retry_attempts": 3,
                    "timeout": 30
                },
                "sms": {
                    "enabled": True,
                    "provider": "twilio",
                    "api_key": os.getenv("TWILIO_API_KEY"),
                    "api_secret": os.getenv("TWILIO_API_SECRET"),
                    "rate_limit": 100,
                    "retry_attempts": 2,
                    "timeout": 15
                },
                "push": {
                    "enabled": True,
                    "provider": "fcm",
                    "api_key": os.getenv("FCM_API_KEY"),
                    "rate_limit": 500,
                    "retry_attempts": 2,
                    "timeout": 10
                },
                "webhook": {
                    "enabled": True,
                    "rate_limit": 200,
                    "retry_attempts": 3,
                    "timeout": 30,
                    "signature_validation": True
                }
            },
            
            # AI configuration
            "ai": {
                "enabled": True,
                "priority_classification_enabled": True,
                "personalization_enabled": True,
                "template_optimization_enabled": True,
                "delivery_optimization_enabled": True,
                "model_version": "2.0",
                "confidence_threshold": 0.75,
                "batch_processing_enabled": True,
                "a_b_testing_enabled": True
            },
            
            # Business rules
            "business_rules": {
                "content_protection": {
                    "priority": "high",
                    "escalation_threshold": 2,
                    "notification_channels": ["email", "sms", "push"],
                    "immediate_delivery": True,
                    "mandatory": True
                },
                "collaboration_matching": {
                    "priority": "medium",
                    "personalization_level": "high",
                    "ab_testing_enabled": True,
                    "delivery_optimization": True,
                    "batch_processing": True
                },
                "monetization_opportunities": {
                    "priority": "high",
                    "time_sensitive": True,
                    "revenue_threshold": 100,
                    "personalization_level": "high",
                    "immediate_delivery": True
                },
                "seo_optimization": {
                    "priority": "medium",
                    "batch_processing": True,
                    "analytics_enabled": True,
                    "aggregation_period": "daily"
                },
                "distribution_status": {
                    "priority": "low",
                    "batch_processing": True,
                    "digest_enabled": True,
                    "digest_frequency": "daily"
                }
            },
            
            # Security settings
            "security": {
                "encryption_enabled": True,
                "jwt_secret": os.getenv("JWT_SECRET", "default_secret_change_in_production"),
                "api_key_required": True,
                "rate_limiting_enabled": True,
                "audit_logging_enabled": True,
                "gdpr_compliance": True
            },
            
            # Analytics configuration
            "analytics": {
                "enabled": True,
                "real_time_tracking": True,
                "performance_monitoring": True,
                "business_intelligence": True,
                "detailed_logging": True,
                "metrics_retention_days": 365
            },
            
            # Workflow configuration
            "workflows": {
                "enabled": True,
                "max_workflow_steps": 20,
                "workflow_timeout": 3600,
                "parallel_execution": True,
                "monitoring_enabled": True
            },
            
            # Performance settings
            "performance": {
                "caching_enabled": True,
                "cache_ttl": 3600,
                "max_concurrent_deliveries": 100,
                "batch_processing": True,
                "optimal_batch_size": 50,
                "load_balancing": True
            }
        }
    
    def _load_from_environment(self):
        """Load configuration from environment variables."""
        env_mappings = {
            "NOTIFICATION_DEBUG": ("debug", bool),
            "NOTIFICATION_LOG_LEVEL": ("log_level", str),
            "NOTIFICATION_ENVIRONMENT": ("environment", str),
            "NOTIFICATION_MAX_WORKERS": ("system.worker_threads", int),
            "NOTIFICATION_QUEUE_SIZE": ("system.queue_size", int),
            "NOTIFICATION_AI_ENABLED": ("ai.enabled", bool),
            "NOTIFICATION_ANALYTICS_ENABLED": ("analytics.enabled", bool),
            "NOTIFICATION_WORKFLOWS_ENABLED": ("workflows.enabled", bool)
        }
        
        for env_var, (config_path, data_type) in env_mappings.items():
            value = os.getenv(env_var)
            if value is not None:
                try:
                    # Convert to appropriate type
                    if data_type == bool:
                        value = value.lower() in ("true", "1", "yes", "on")
                    elif data_type == int:
                        value = int(value)
                    elif data_type == float:
                        value = float(value)
                    
                    # Set nested configuration value
                    self._set_nested_config(config_path, value)
                    
                except (ValueError, TypeError) as e:
                    logger.warning(f"Invalid environment variable {env_var}: {e}")
    
    def _load_from_file(self):
        """Load configuration from file."""
        config_files = [
            "notification_config.json",
            "config/notification.json",
            "/etc/notification/config.json"
        ]
        
        for config_file in config_files:
            if os.path.exists(config_file):
                try:
                    with open(config_file, 'r') as f:
                        file_config = json.load(f)
                    
                    self._apply_config_override(file_config)
                    logger.info(f"Loaded configuration from {config_file}")
                    break
                    
                except (json.JSONDecodeError, IOError) as e:
                    logger.warning(f"Failed to load config from {config_file}: {e}")
    
    def _apply_config_override(self, override_config: Dict[str, Any]):
        """Apply configuration override."""
        def deep_merge(base: Dict, override: Dict):
        try:
            logger.info(f"Executing deep_merge")
            
            # Implementation for deep_merge
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"deep_merge completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"deep_merge failed: {e}")
            raise
                if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                    deep_merge(base[key], value)
                else:
                    base[key] = value
        
        deep_merge(self._config, override_config)
    
    def _set_nested_config(self, path: str, value: Any):
        """
Set nested configuration value using dot notation."""
        keys = path.split('.')
        current = self._config
        
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        current[keys[-1]] = value
    
    def _initialize_component_configs(self):
        """
Initialize typed configuration objects for components."""
        # Channel configurations
        self.channels = {}
        for channel_name, channel_config in self._config.get("channels", {}).items():
            self.channels[channel_name] = ChannelConfig(**channel_config)
        
        # AI configuration
        ai_config = self._config.get("ai", {})
        self.ai = AIConfig(**ai_config)
        
        # Security configuration
        security_config = self._config.get("security", {})
        self.security = SecurityConfig(**security_config)
        
        # Analytics configuration
        analytics_config = self._config.get("analytics", {})
        self.analytics = AnalyticsConfig(**analytics_config)
        
        # Workflow configuration
        workflow_config = self._config.get("workflows", {})
        self.workflows = WorkflowConfig(**workflow_config)
        
        # Performance configuration
        performance_config = self._config.get("performance", {})
        self.performance = PerformanceConfig(**performance_config)
    
    def _validate_configuration(self):
        """Validate configuration for consistency and required values."""
        errors = []
        
        # Validate required API keys for enabled channels
        for channel_name, channel_config in self.channels.items():
            if channel_config.enabled and not channel_config.api_key:
                if channel_name in ["email", "sms", "push"]:
                    errors.append(f"Missing API key for enabled channel: {channel_name}")
        
        # Validate security settings
        if self.security.jwt_secret == "default_secret_change_in_production" and self.environment == "production":
            errors.append("JWT secret must be changed in production environment")
        
        # Validate database connection
        if not self._config.get("database", {}).get("url"):
            errors.append("Database URL is required")
        
        # Log validation errors
        if errors:
            for error in errors:
                logger.error(f"Configuration validation error: {error}")
            
            if self.environment == "production":
                raise ValueError(f"Configuration validation failed: {'; '.join(errors)}")
        else:
            logger.info("Configuration validation passed")
    
    # Public methods for accessing configuration
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key path."""
        keys = key.split('.')
        current = self._config
        
        try:
            for k in keys:
                current = current[k]
            return current
        except (KeyError, TypeError):
            return default
    
    def get_channel_config(self, channel: str) -> Optional[ChannelConfig]:
        """
Get configuration for specific channel."""
        return self.channels.get(channel)
    
    def get_business_rules(self) -> Dict[str, Any]:
        """
Get business rules configuration."""
        return self._config.get("business_rules", {})
    
    def get_business_rule(self, rule_name: str) -> Dict[str, Any]:
        """Get specific business rule configuration."""
        return self._config.get("business_rules", {}).get(rule_name, {})
    
    def is_channel_enabled(self, channel: str) -> bool:
        """Check if channel is enabled."""
        channel_config = self.get_channel_config(channel)
        return channel_config.enabled if channel_config else False
    
    def is_ai_enabled(self) -> bool:
        """
Check if AI features are enabled."""
        return self.ai.enabled
    
    def is_analytics_enabled(self) -> bool:
        """
Check if analytics are enabled."""
        return self.analytics.enabled
    
    def is_workflows_enabled(self) -> bool:
        try:
            logger.info(f"Executing export_config")
            
            # Implementation for export_config
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"export_config completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"export_config failed: {e}")
            raise
            def remove_sensitive(obj):
                if isinstance(obj, dict):
                    return {
                        k: "***REDACTED***" if any(sens in k.lower() for sens in sensitive_keys)
                        else remove_sensitive(v)
                        for k, v in obj.items()
                    }
                return obj
            
            config_copy = remove_sensitive(config_copy)
        
        return config_copy
    
    def get_health_check_config(self) -> Dict[str, Any]:
        """Get health check configuration."""
        return {
            "enabled": True,
            "interval": self.get("system.health_check_interval", 60),
            "checks": {
                "database": True,
                "redis": True,
                "channels": list(self.channels.keys()),
                "ai_services": self.ai.enabled,
                "analytics": self.analytics.enabled
            }
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return self._config.copy()
    
    def __str__(self) -> str:
        """
String representation of configuration."""
        return f"NotificationConfig(environment={self.environment}, channels={len(self.channels)}, ai_enabled={self.ai.enabled})"
