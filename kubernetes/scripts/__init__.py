"""
  Init   module
Enterprise implementation for Ainflue platform
"""

#!/usr/bin/env python3
"""IA Influencer Agent - Deployment Scripts Module
Enterprise-grade deployment automation and orchestration scripts for
AI-powered content protection, monetization, and multi-platform integration
"""
__version__ = "2.0.0"
__author__ = "Fahed Mlaiel"
__maintainer__ = "IA Influencer Agent Team"

# Import core deployment managers
from .app_deployment import (
    ApplicationDeployment,
    DeploymentStrategy,
    DeploymentStatus,
    DeploymentConfig
)

from .backup_management import (
    BackupManager,
    BackupType,
    BackupStatus,
    StorageProvider
)

from .database_migration import (
    DatabaseMigration,
    MigrationStatus,
    MigrationDirection
)

from .health_monitoring import (
    HealthMonitor,
    HealthStatus,
    CheckType,
    AlertLevel
)

from .infrastructure_provisioning import (
    InfrastructureProvisioner,
    ProviderType,
    ResourceType,
    ProvisioningStatus
)

from .log_management import (
    LogManager,
    LogLevel,
    LogSource,
    ProcessingStatus
)

from .performance_optimization import (
    PerformanceOptimizer,
    OptimizationType,
    OptimizationStatus,
    PerformanceMetric
)

from .security_hardening import (
    SecurityHardening,
    SecurityLevel,
    ComplianceStandard,
    VulnerabilityLevel,
    SecurityPolicy,
    Vulnerability
)

from .service_orchestration import (
    ServiceOrchestrator,
    ServiceStatus,
    OrchestrationAction,
    ServiceDefinition,
    ServiceInstance
)

from .system_maintenance import (
    SystemMaintenance,
    MaintenanceType,
    MaintenanceStatus,
    Priority,
    MaintenanceTask,
    SystemHealth
)

# Import IA Influencer Agent specific deployment managers
from .content_protection_deployment import (
    ContentProtectionDeploymentManager,
    ProtectionStrategy,
    ProtectionMode,
    FingerprintEngine,
    ProtectionDeploymentConfig,
    FingerprintEngineStatus
)

from .monetization_deployment import (
    MonetizationDeploymentManager,
    PaymentProvider,
    RevenueStream,
    LicensingType,
    MonetizationStrategy,
    MonetizationDeploymentConfig,
    RevenueStreamStatus,
    PaymentProviderStatus
)

from .ai_fingerprinting_deployment import (
    AIFingerprintingDeploymentManager,
    FingerprintingAlgorithm,
    AccuracyLevel,
    ProcessingMode,
    FingerprintingDeploymentConfig,
    FingerprintingEngineMetrics
)

from .platform_integration_deployment import (
    PlatformIntegrationDeploymentManager,
    SupportedPlatform,
    IntegrationType,
    MonitoringMode,
    DataCollectionScope,
    PlatformIntegrationConfig,
    PlatformDeploymentConfig,
    PlatformStatus
)

from .web_crawlers_deployment import (
    WebCrawlersDeploymentManager,
    CrawlerType,
    CrawlingStrategy,
    AntiDetectionMode,
    ContentType,
    PlatformAPI,
    CrawlerConfig,
    ProxyConfig
)

from .metrics_reporting_deployment import (
    MetricsReportingDeploymentManager,
    MetricType,
    DataSource,
    ReportType,
    AlertSeverity,
    MetricConfig,
    DashboardConfig,
    AlertConfig
)

from .backup_recovery_deployment import (
    BackupRecoveryDeploymentManager,
    BackupType,
    StorageTier,
    BackupStatus,
    CompressionType,
    EncryptionType,
    BackupConfig,
    RecoveryConfig,
    BackupMetadata
)

from .metrics_reporting_deployment import (
    MetricsReportingDeploymentManager,
    MetricType,
    DataSource,
    ReportType,
    AlertSeverity,
    MetricConfig,
    DashboardConfig,
    AlertConfig
)

from .backup_recovery_deployment import (
    BackupRecoveryDeploymentManager,
    BackupType,
    StorageTier,
    BackupStatus,
    CompressionType,
    EncryptionType,
    BackupConfig,
    RecoveryConfig,
    BackupMetadata
)

from .web_crawlers_deployment import (
    WebCrawlersDeploymentManager,
    CrawlerType,
    CrawlingStrategy,
    AntiDetectionMode,
    ContentType,
    PlatformAPI,
    CrawlerConfig,
    ProxyConfig
)

from .licensing_rights_deployment import (
    LicensingRightsDeploymentManager,
    LicenseType,
    RightsScope,
    LegalJurisdiction,
    ComplianceStandard,
    ContractStatus,
    PaymentSchedule,
    LicenseTerms,
    PricingModel,
    LicenseContract
)

from .notification_alerts_deployment import (
    NotificationAlertsDeploymentManager,
    NotificationChannel,
    AlertSeverity,
    NotificationPriority,
    NotificationCategory,
    DeliveryStatus,
    TemplateType,
    NotificationTemplate,
    NotificationRule,
    NotificationRequest,
    DeploymentConfig as NotificationDeploymentConfig
)

from .microservices_deployment import (
    MicroservicesDeploymentManager,
    ServiceType,
    CommunicationProtocol,
    ServiceDiscoveryType,
    LoadBalancingStrategy,
    CircuitBreakerState,
    ServiceMeshType,
    ServiceEndpoint,
    ServiceDependency,
    ServiceConfiguration,
    ServiceMeshConfiguration,
    APIGatewayConfiguration
)

# Define public API
__all__ = [
    # Core Application Deployment
    "ApplicationDeployment",
    "DeploymentStrategy", 
    "DeploymentStatus",
    "DeploymentConfig",
    
    # Backup Management
    "BackupManager",
    "BackupType",
    "BackupStatus", 
    "StorageProvider",
    
    # Database Migration
    "DatabaseMigration",
    "MigrationStatus",
    "MigrationDirection",
    
    # Health Monitoring
    "HealthMonitor",
    "HealthStatus",
    "CheckType",
    "AlertLevel",
    
    # Infrastructure Provisioning
    "InfrastructureProvisioner",
    "ProviderType",
    "ResourceType",
    "ProvisioningStatus",
    
    # Log Management
    "LogManager",
    "LogLevel",
    "LogSource",
    "ProcessingStatus",
    
    # Performance Optimization
    "PerformanceOptimizer",
    "OptimizationType",
    "OptimizationStatus",
    "PerformanceMetric",
    
    # Security Hardening
    "SecurityHardening",
    "SecurityLevel",
    "ComplianceStandard",
    "VulnerabilityLevel",
    "SecurityPolicy",
    "Vulnerability",
    
    # Service Orchestration
    "ServiceOrchestrator",
    "ServiceStatus",
    "OrchestrationAction",
    "ServiceDefinition",
    "ServiceInstance",
    
    # System Maintenance
    "SystemMaintenance",
    "MaintenanceType",
    "MaintenanceStatus",
    "Priority",
    "MaintenanceTask",
    "SystemHealth",
    
    # Content Protection Deployment
    "ContentProtectionDeploymentManager",
    "ProtectionStrategy",
    "ProtectionMode",
    "FingerprintEngine",
    "ProtectionDeploymentConfig",
    "FingerprintEngineStatus",
    
    # Monetization Deployment
    "MonetizationDeploymentManager",
    "PaymentProvider",
    "RevenueStream",
    "LicensingType",
    "MonetizationStrategy",
    "MonetizationDeploymentConfig",
    "RevenueStreamStatus",
    "PaymentProviderStatus",
    
    # AI Fingerprinting Deployment
    "AIFingerprintingDeploymentManager",
    "FingerprintingAlgorithm",
    "AccuracyLevel",
    "ProcessingMode",
    "FingerprintingDeploymentConfig",
    "FingerprintingEngineMetrics",
    
    # Platform Integration Deployment
    "PlatformIntegrationDeploymentManager",
    "SupportedPlatform",
    "IntegrationType",
    "MonitoringMode",
    "DataCollectionScope",
    "PlatformIntegrationConfig",
    "PlatformDeploymentConfig",
    "PlatformStatus",
    
    # Web Crawlers Deployment
    "WebCrawlersDeploymentManager",
    "CrawlerType",
    "CrawlingStrategy",
    "AntiDetectionMode",
    "ContentType",
    "PlatformAPI",
    "CrawlerConfig",
    "ProxyConfig",
    
    # Metrics and Reporting Deployment
    "MetricsReportingDeploymentManager",
    "MetricType",
    "DataSource",
    "ReportType",
    "AlertSeverity",
    "MetricConfig",
    "DashboardConfig",
    "AlertConfig",
    
    # Backup and Recovery Deployment
    "BackupRecoveryDeploymentManager",
    "BackupType",
    "StorageTier",
    "BackupStatus",
    "CompressionType",
    "EncryptionType",
    "BackupConfig",
    "RecoveryConfig",
    "BackupMetadata",
    
    # Metrics and Reporting Deployment
    "MetricsReportingDeploymentManager",
    "MetricType",
    "DataSource",
    "ReportType",
    "AlertSeverity",
    "MetricConfig",
    "DashboardConfig",
    "AlertConfig",
    
    # Backup and Recovery Deployment
    "BackupRecoveryDeploymentManager",
    "BackupType",
    "StorageTier",
    "BackupStatus",
    "CompressionType",
    "EncryptionType",
    "BackupConfig",
    "RecoveryConfig",
    "BackupMetadata",
    
    # Web Crawlers Deployment
    "WebCrawlersDeploymentManager",
    "CrawlerType",
    "CrawlingStrategy",
    "AntiDetectionMode",
    "ContentType",
    "PlatformAPI",
    "CrawlerConfig",
    "ProxyConfig",
    
    # Licensing Rights Deployment
    "LicensingRightsDeploymentManager",
    "LicenseType",
    "RightsScope",
    "LegalJurisdiction",
    "ComplianceStandard",
    "ContractStatus",
    "PaymentSchedule",
    "LicenseTerms",
    "PricingModel",
    "LicenseContract",
    
    # Notification Alerts Deployment
    "NotificationAlertsDeploymentManager",
    "NotificationChannel",
    "AlertSeverity",
    "NotificationPriority",
    "NotificationCategory",
    "DeliveryStatus",
    "TemplateType",
    "NotificationTemplate",
    "NotificationRule",
    "NotificationRequest",
    "NotificationDeploymentConfig",
    
    # Microservices Deployment
    "MicroservicesDeploymentManager",
    "ServiceType",
    "CommunicationProtocol",
    "ServiceDiscoveryType",
    "LoadBalancingStrategy",
    "CircuitBreakerState",
    "ServiceMeshType",
    "ServiceEndpoint",
    "ServiceDependency",
    "ServiceConfiguration",
    "ServiceMeshConfiguration",
    "APIGatewayConfiguration"
]
