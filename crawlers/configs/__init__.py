"""Crawler Configurations Module
============================

Comprehensive configuration system for the IA Influencer Agent crawler infrastructure.
Provides centralized management for platform-specific settings, surveillance configurations,
content protection, network optimization, and storage management.

Author: Fahed Mlaiel <mlaiel@live.de>
Team: Lead Dev IA + Backend Senior + ML Engineer + Audio Engineer + DevOps + DBA + Security + Microservices Expert
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

Project: IA Influencer Agent - Advanced Content Protection Platform
Contact: mlaiel@live.de | www.fahed-mlaiel.de

WARNING: This code and concept are protected by intellectual property rights.
Any unauthorized use, reproduction, modification, or distribution is strictly prohibited.
Legal action will be taken against violators.

Project Specifications:
- Multi-platform content surveillance and protection
- AI-powered fingerprinting and violation detection  
- Real-time monitoring and alerting system
- Advanced content protection for creators
- Automated monetization and revenue tracking
- Enterprise-grade security and compliance
"""
import os
import logging
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

# Import all configuration modules
from .platform_configs import (
    PlatformConfigManager,
    platform_config_manager,
    PlatformType,
    PlatformConfig,
    ContentType,
    AuthMethod,
    ScrapeMethod
)

from .surveillance_configs import (
    SurveillanceConfigManager,
    surveillance_config_manager,
    SurveillanceConfig,
    SurveillanceType,
    MonitoringMode,
    DetectionMethod
)

from .network_configs import (
    NetworkConfigManager,
    network_config_manager,
    ProxyType,
    UserAgentType,
    RateLimitStrategy,
    ProxyServerConfig,
    ProxyRotationConfig
)

from .protection_configs import (
    ProtectionConfigManager,
    protection_config_manager,
    ProtectionConfig,
    ProtectionLevel,
    ContentProtectionType
)

from .storage_configs import (
    StorageConfigManager,
    storage_config_manager,
    StorageConfig,
    StorageType,
    StorageProvider
)

from .ai_configs import (
    AIConfigManager,
    ai_config_manager,
    ModelConfig,
    AIModelType,
    AIProvider,
    ProcessingMode,
    ContentAnalysisConfig,
    SmartCrawlConfig,
    ViolationDetectionConfig
)

from .security_configs import (
    SecurityConfigManager,
    security_config_manager,
    SecurityLevel,
    ThreatLevel,
    EncryptionConfig,
    AccessControlConfig,
    ThreatProtectionConfig,
    ComplianceConfig
)

from .quality_configs import (
    QualityConfigManager,
    quality_config_manager,
    QualityLevel,
    ValidationSeverity,
    DataQualityMetric,
    ValidationRule,
    QualityMetric,
    ValidationRuleConfig,
    ContentQualityConfig
)

from .analytics_configs import (
    AnalyticsConfigManager,
    analytics_config_manager,
    MetricType,
    AggregationType,
    TimeGranularity,
    DashboardType,
    MetricDefinition,
    AnalyticsConfig,
    DashboardConfig
)

from .notification_configs import (
    NotificationConfigManager,
    notification_config_manager,
    NotificationChannel,
    NotificationPriority,
    ChannelConfig,
    RecipientConfig,
    NotificationTemplate,
    EscalationPolicy
)

# Global configuration managers instances
__all__ = [
    # Platform configurations
    "PlatformConfigManager", "platform_config_manager",
    "PlatformType", "PlatformConfig", "ContentType", "AuthMethod", "ScrapeMethod",
    
    # Surveillance configurations  
    "SurveillanceConfigManager", "surveillance_config_manager",
    "SurveillanceConfig", "SurveillanceType", "MonitoringMode", "DetectionMethod",
    
    # Network configurations
    "NetworkConfigManager", "network_config_manager",
    "ProxyType", "UserAgentType", "RateLimitStrategy", "ProxyServerConfig", "ProxyRotationConfig",
    
    # Protection configurations
    "ProtectionConfigManager", "protection_config_manager", 
    "ProtectionConfig", "ProtectionLevel", "ContentProtectionType",
    
    # Storage configurations
    "StorageConfigManager", "storage_config_manager",
    "StorageConfig", "StorageType", "StorageProvider",
    
    # AI configurations
    "AIConfigManager", "ai_config_manager",
    "ModelConfig", "AIModelType", "AIProvider", "ProcessingMode",
    "ContentAnalysisConfig", "SmartCrawlConfig", "ViolationDetectionConfig",
    
    # Security configurations
    "SecurityConfigManager", "security_config_manager",
    "SecurityLevel", "ThreatLevel", "EncryptionConfig", "AccessControlConfig",
    "ThreatProtectionConfig", "ComplianceConfig",
    
    # Quality configurations
    "QualityConfigManager", "quality_config_manager",
    "QualityLevel", "ValidationSeverity", "DataQualityMetric", "ValidationRule",
    "QualityMetric", "ValidationRuleConfig", "ContentQualityConfig",
    
    # Analytics configurations
    "AnalyticsConfigManager", "analytics_config_manager",
    "MetricType", "AggregationType", "TimeGranularity", "DashboardType",
    "MetricDefinition", "AnalyticsConfig", "DashboardConfig",
    
    # Notification configurations
    "NotificationConfigManager", "notification_config_manager",
    "NotificationChannel", "NotificationPriority", "ChannelConfig",
    "RecipientConfig", "NotificationTemplate", "EscalationPolicy",
    
    # Unified config manager
    "CrawlerConfigurationManager", "crawler_config_manager",
    
    # Legacy compatibility
    "MasterConfigManager", "master_config_manager"
]

class CrawlerConfigurationManager:
    """
    Unified configuration manager for all crawler subsystems.
    Provides centralized access to all configuration modules.
    """
    
    def __init__(self):
        """Initialize unified configuration manager."""
        self.platform = platform_config_manager
        self.surveillance = surveillance_config_manager
        self.network = network_config_manager
        self.protection = protection_config_manager
        self.storage = storage_config_manager
        self.ai = ai_config_manager
        self.security = security_config_manager
        self.quality = quality_config_manager
        self.analytics = analytics_config_manager
        self.notification = notification_config_manager
        
        # Configuration metadata
        self.version = "2.0.0"
        self.last_updated = datetime.now()
        self.author = "Fahed Mlaiel <mlaiel@live.de>"
        
        logger.info(f"Crawler Configuration Manager v{self.version} initialized")
    
    def validate_all_configurations(self) -> Dict[str, Any]:
        """Validate all configuration modules."""
        validation_results = {
            "overall_status": "valid",
            "modules": {},
            "errors": [],
            "warnings": [],
            "recommendations": []
        }
        
        # Validate each configuration module
        modules_to_validate = [
            ("platform", self.platform),
            ("surveillance", self.surveillance),
            ("network", self.network),
            ("protection", self.protection),
            ("storage", self.storage),
            ("ai", self.ai),
            ("security", self.security),
            ("quality", self.quality),
            ("analytics", self.analytics),
            ("notification", self.notification)
        ]
        
        total_errors = 0
        total_warnings = 0
        
        for module_name, config_manager in modules_to_validate:
            try:
                if hasattr(config_manager, 'validate_configuration'):
                    module_result = config_manager.validate_configuration()
                    validation_results["modules"][module_name] = module_result
                    
                    errors = module_result.get("errors", [])
                    warnings = module_result.get("warnings", [])
                    
                    total_errors += len(errors)
                    total_warnings += len(warnings)
                    
                    validation_results["errors"].extend([f"{module_name}: {err}" for err in errors])
                    validation_results["warnings"].extend([f"{module_name}: {warn}" for warn in warnings])
                else:
                    validation_results["modules"][module_name] = {"status": "no_validation"}
                    
            except Exception as e:
                validation_results["errors"].append(f"{module_name}: Validation failed - {str(e)}")
                total_errors += 1
        
        # Determine overall status
        if total_errors > 0:
            validation_results["overall_status"] = "invalid"
        elif total_warnings > 0:
            validation_results["overall_status"] = "warnings"
        
        # Add general recommendations
        if total_errors == 0 and total_warnings == 0:
            validation_results["recommendations"].append("All configurations are valid and optimal")
        elif total_warnings > 5:
            validation_results["recommendations"].append("Consider addressing warnings to improve system reliability")
        
        return validation_results
    
    def get_configuration_summary(self) -> Dict[str, Any]:
        """Get comprehensive configuration summary."""
        summary = {
            "version": self.version,
            "last_updated": self.last_updated.isoformat(),
            "author": self.author,
            "modules": {
                "platform": {
                    "enabled_platforms": len([p for p in self.platform.platforms.values() if p.enabled]),
                    "total_platforms": len(self.platform.platforms)
                },
                "surveillance": {
                    "active_configs": len([s for s in self.surveillance.configs.values() if s.enabled]),
                    "total_configs": len(self.surveillance.configs)
                },
                "ai": {
                    "registered_models": len(self.ai.models),
                    "enabled_models": len(self.ai.get_enabled_models())
                },
                "security": {
                    "encryption_enabled": self.security.encryption.enabled,
                    "mfa_enabled": self.security.access_control.mfa_enabled,
                    "threat_protection": self.security.threat_protection.enabled
                },
                "quality": {
                    "quality_metrics": len(self.quality.get_quality_metrics()),
                    "validation_rules": len(self.quality.get_validation_rules())
                },
                "analytics": {
                    "active_metrics": len(self.analytics.get_metrics()),
                    "dashboards": len(self.analytics.dashboards)
                },
                "notification": {
                    "enabled_channels": len(self.notification.get_enabled_channels()),
                    "recipients": len(self.notification.recipients)
                }
            }
        }
        
        return summary
    
    def export_configurations(self, export_path: Optional[str] = None) -> str:
        """Export all configurations to JSON file."""
        if export_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            export_path = f"crawler_configs_export_{timestamp}.json"
        
        export_data = {
            "metadata": {
                "export_timestamp": datetime.now().isoformat(),
                "version": self.version,
                "author": self.author
            },
            "configurations": self.get_configuration_summary(),
            "validation": self.validate_all_configurations()
        }
        
        try:
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False, default=str)
            
            logger.info(f"Configurations exported to: {export_path}")
            return export_path
        except Exception as e:
            logger.error(f"Failed to export configurations: {e}")
            raise

# Global unified configuration manager instance
crawler_config_manager = CrawlerConfigurationManager()
)

from .network_configs import (
    NetworkConfigManager,
    network_config_manager,
    ProxyType,
    UserAgentType,
    RateLimitStrategy,
    ProxyServerConfig,
    ProxyRotationConfig
)

from .protection_configs import (
    ProtectionConfigManager,
    protection_config_manager,
    ProtectionConfig,
    ProtectionLevel,
    ContentProtectionType
)

from .storage_configs import (
    StorageConfigManager,
    storage_config_manager,
    StorageConfig,
    StorageType,
    StorageProvider
)

from .ai_configs import (
    AIConfigManager,
    ai_config_manager,
    ModelConfig,
    AIModelType,
    AIProvider,
    ProcessingMode,
    ContentAnalysisConfig,
    SmartCrawlConfig,
    ViolationDetectionConfig
)

from .security_configs import (
    SecurityConfigManager,
    security_config_manager,
    SecurityLevel,
    ThreatLevel,
    EncryptionConfig,
    AccessControlConfig,
    ThreatProtectionConfig,
    ComplianceConfig
)

from .quality_configs import (
    QualityConfigManager,
    quality_config_manager,
    QualityLevel,
    ValidationSeverity,
    DataQualityMetric,
    ValidationRule,
    QualityMetric,
    ValidationRuleConfig,
    ContentQualityConfig
)

from .analytics_configs import (
    AnalyticsConfigManager,
    analytics_config_manager,
    MetricType,
    AggregationType,
    TimeGranularity,
    DashboardType,
    MetricDefinition,
    AnalyticsConfig,
    DashboardConfig
)

from .notification_configs import (
    NotificationConfigManager,
    notification_config_manager,
    NotificationChannel,
    NotificationPriority,
    ChannelConfig,
    RecipientConfig,
    NotificationTemplate,
    EscalationPolicy
    SurveillanceMode,
    MonitoringType,
    AlertSeverity,
    AlertChannel,
    FingerprintEngine
)

from .protection_configs import (
    ProtectionConfigManager,
    protection_config_manager,
    ProtectionConfig,
    ProtectionLevel,
    ViolationType,
    ProtectionMethod,
    AudioProtectionConfig,
    VideoProtectionConfig,
    ImageProtectionConfig,
    TextProtectionConfig
)

from .network_configs import (
    NetworkConfigManager,
    network_config_manager,
    NetworkConfig,
    ProxyType,
    UserAgentType,
    RateLimitStrategy,
    LoadBalancingStrategy,
    CacheStrategy
)

from .storage_configs import (
    StorageConfigManager,
    storage_config_manager,
    StorageConfig,
    StorageBackend,
    DatabaseType,
    CompressionType,
    EncryptionType
)

logger = logging.getLogger(__name__)

@dataclass
class GlobalCrawlerConfig:
    """Global crawler system configuration."""
    # System identification
    system_name: str = "IA Influencer Agent - Content Protection Platform"
    version: str = "2.0.0"
    environment: str = "production"  # development, staging, production
    
    # Core settings
    enabled: bool = True
    debug_mode: bool = False
    verbose_logging: bool = False
    
    # Feature flags
    platform_crawling_enabled: bool = True
    surveillance_enabled: bool = True
    protection_enabled: bool = True
    fingerprinting_enabled: bool = True
    violation_detection_enabled: bool = True
    real_time_monitoring_enabled: bool = True
    automated_takedown_enabled: bool = False  # Requires manual approval
    
    # Performance settings
    max_concurrent_crawlers: int = 50
    max_concurrent_platforms: int = 10
    processing_queue_size: int = 10000
    worker_pool_size: int = 20
    
    # Resource limits
    max_memory_usage_gb: int = 8
    max_disk_usage_gb: int = 100
    max_network_bandwidth_mbps: int = 1000
    
    # Monitoring settings
    health_check_interval_seconds: int = 30
    metrics_collection_enabled: bool = True
    performance_monitoring_enabled: bool = True
    error_tracking_enabled: bool = True
    
    # Security settings
    security_mode: str = "strict"  # relaxed, standard, strict, paranoid
    encryption_required: bool = True
    audit_logging_enabled: bool = True
    compliance_mode: str = "gdpr"  # gdpr, ccpa, both
    
    # Integration settings
    api_enabled: bool = True
    webhook_enabled: bool = True
    dashboard_enabled: bool = True
    mobile_app_enabled: bool = True
    
    # Legal and compliance
    dmca_compliance: bool = True
    copyright_enforcement: bool = True
    evidence_collection: bool = True
    legal_documentation: bool = True

class MasterConfigManager:
    """Master configuration manager for the entire crawler system."""
    
    def __init__(self, config_dir: Optional[str] = None):
        """Initialize master config manager."""
        self.config_dir = Path(config_dir or os.getenv("CRAWLER_CONFIG_DIR", "./configs"))
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize global configuration
        self.global_config = self._load_global_config()
        
        # Initialize sub-managers
        self.platform_manager = platform_config_manager
        self.surveillance_manager = surveillance_config_manager
        self.protection_manager = protection_config_manager
        self.network_manager = network_config_manager
        self.storage_manager = storage_config_manager
        
        # Setup logging
        self._setup_logging()
        
        logger.info(f"Master Config Manager initialized for {self.global_config.system_name}")
        logger.info(f"Environment: {self.global_config.environment}")
        logger.info(f"Version: {self.global_config.version}")
    
    def _load_global_config(self) -> GlobalCrawlerConfig:
        """Load global configuration."""
        config_file = self.config_dir / "global_config.json"
        if config_file.exists():
            try:
                import json
                with open(config_file, 'r') as f:
                    data = json.load(f)
                    return GlobalCrawlerConfig(**data)
            except Exception as e:
                logger.warning(f"Failed to load global config: {e}, using defaults")
        
        return GlobalCrawlerConfig()
    
    def _setup_logging(self) -> None:
        """Setup logging configuration."""
        log_level = logging.DEBUG if self.global_config.debug_mode else logging.INFO
        
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler(self.config_dir / 'crawler_system.log')
            ]
        )
    
    def get_global_config(self) -> GlobalCrawlerConfig:
        """Get global configuration."""
        return self.global_config
    
    def get_platform_config(self, platform: PlatformType) -> Optional[PlatformConfig]:
        """Get configuration for specific platform."""
        return self.platform_manager.get_config(platform)
    
    def get_surveillance_config(self) -> SurveillanceConfig:
        """Get surveillance configuration."""
        return self.surveillance_manager.get_config()
    
    def get_protection_config(self) -> ProtectionConfig:
        """Get protection configuration."""
        return self.protection_manager.get_config()
    
    def get_network_config(self) -> NetworkConfig:
        """Get network configuration."""
        return self.network_manager.get_config()
    
    def get_storage_config(self) -> StorageConfig:
        """Get storage configuration."""
        return self.storage_manager.get_config()
    
    def get_enabled_platforms(self) -> List[PlatformType]:
        """Get list of enabled platforms."""
        if not self.global_config.platform_crawling_enabled:
            return []
        
        enabled_configs = self.platform_manager.get_enabled_configs()
        return list(enabled_configs.keys())
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status."""
        return {
            "system_name": self.global_config.system_name,
            "version": self.global_config.version,
            "environment": self.global_config.environment,
            "enabled": self.global_config.enabled,
            "enabled_platforms": len(self.get_enabled_platforms()),
            "surveillance_enabled": self.global_config.surveillance_enabled,
            "protection_enabled": self.global_config.protection_enabled,
            "security_mode": self.global_config.security_mode,
            "timestamp": datetime.now().isoformat()
        }
    
    def validate_all_configurations(self) -> Dict[str, List[str]]:
        """Validate all configurations."""
        validation_results = {}
        
        # Validate platform configurations
        platform_errors = []
        for platform_type in PlatformType:
            config = self.platform_manager.get_config(platform_type)
            if config and config.enabled:
                errors = self.platform_manager.validate_config(config)
                if errors:
                    platform_errors.extend([f"{platform_type.value}: {error}" for error in errors])
        validation_results["platform"] = platform_errors
        
        # Validate surveillance configuration
        validation_results["surveillance"] = self.surveillance_manager.validate_config()
        
        # Validate protection configuration
        validation_results["protection"] = self.protection_manager.validate_config()
        
        # Validate network configuration
        validation_results["network"] = self.network_manager.validate_config()
        
        # Validate storage configuration
        validation_results["storage"] = self.storage_manager.validate_config()
        
        return validation_results

    def get_configuration_summary(self) -> Dict[str, Any]:
        """Get summary of all configurations."""
        enabled_platforms = self.get_enabled_platforms()
        surveillance_config = self.get_surveillance_config()
        protection_config = self.get_protection_config()
        network_config = self.get_network_config()
        storage_config = self.get_storage_config()
        
        return {
            "global": {
                "system_enabled": self.global_config.enabled,
                "environment": self.global_config.environment,
                "version": self.global_config.version,
                "max_concurrent_crawlers": self.global_config.max_concurrent_crawlers
            },
            "platforms": {
                "enabled_count": len(enabled_platforms),
                "enabled_platforms": [p.value for p in enabled_platforms],
                "total_configured": len(PlatformType)
            },
            "surveillance": {
                "enabled": surveillance_config.enabled,
                "mode": surveillance_config.mode.value,
                "monitoring_types": len(surveillance_config.monitoring_types),
                "fingerprinting_engines": len(surveillance_config.fingerprinting.engines)
            },
            "protection": {
                "enabled": protection_config.enabled,
                "level": protection_config.protection_level.value,
                "audio_protection": protection_config.audio.enabled,
                "video_protection": protection_config.video.enabled,
                "image_protection": protection_config.image.enabled,
                "text_protection": protection_config.text.enabled
            },
            "network": {
                "proxy_rotation": network_config.proxy_rotation.enabled,
                "user_agent_rotation": network_config.user_agent_rotation.enabled,
                "rate_limiting": network_config.rate_limiting.strategy.value,
                "caching": network_config.caching.enabled
            },
            "storage": {
                "file_backend": storage_config.file_storage.backend.value,
                "database_type": storage_config.database.primary_db.value,
                "cache_enabled": storage_config.cache.enabled,
                "backup_enabled": storage_config.backup.enabled,
                "encryption_enabled": storage_config.encryption.enabled
            }
        }

# Global master config manager instance
master_config_manager = MasterConfigManager()

# Convenience functions for easy access
def get_platform_config(platform: PlatformType) -> Optional[PlatformConfig]:
    """Get platform configuration."""
    return master_config_manager.get_platform_config(platform)

def get_surveillance_config() -> SurveillanceConfig:
    """Get surveillance configuration."""
    return master_config_manager.get_surveillance_config()

def get_protection_config() -> ProtectionConfig:
    """Get protection configuration."""
    return master_config_manager.get_protection_config()

def get_network_config() -> NetworkConfig:
    """Get network configuration."""
    return master_config_manager.get_network_config()

def get_storage_config() -> StorageConfig:
    """Get storage configuration."""
    return master_config_manager.get_storage_config()

def get_system_status() -> Dict[str, Any]:
    """Get system status."""
    return master_config_manager.get_system_status()

def validate_all_configs() -> Dict[str, List[str]]:
    """Validate all configurations."""
    return master_config_manager.validate_all_configurations()

# Export all configuration classes and managers
__all__ = [
    # Master manager
    'MasterConfigManager',
    'master_config_manager',
    'GlobalCrawlerConfig',
    
    # Platform configs
    'PlatformConfigManager',
    'platform_config_manager',
    'PlatformConfig',
    'PlatformType',
    'ContentType',
    'AuthMethod',
    'ScrapeMethod',
    
    # Surveillance configs
    'SurveillanceConfigManager',
    'surveillance_config_manager',
    'SurveillanceConfig',
    'SurveillanceMode',
    'MonitoringType',
    'AlertSeverity',
    'AlertChannel',
    'FingerprintEngine',
    
    # Protection configs
    'ProtectionConfigManager',
    'protection_config_manager',
    'ProtectionConfig',
    'ProtectionLevel',
    'ViolationType',
    'ProtectionMethod',
    'AudioProtectionConfig',
    'VideoProtectionConfig',
    'ImageProtectionConfig',
    'TextProtectionConfig',
    
    # Network configs
    'NetworkConfigManager',
    'network_config_manager',
    'NetworkConfig',
    'ProxyType',
    'UserAgentType',
    'RateLimitStrategy',
    'LoadBalancingStrategy',
    'CacheStrategy',
    
    # Storage configs
    'StorageConfigManager',
    'storage_config_manager',
    'StorageConfig',
    'StorageBackend',
    'DatabaseType',
    'CompressionType',
    'EncryptionType',
    
    # Convenience functions
    'get_platform_config',
    'get_surveillance_config',
    'get_protection_config',
    'get_network_config',
    'get_storage_config',
    'get_system_status',
    'validate_all_configs'
]
