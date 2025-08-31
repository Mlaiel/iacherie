"""🚀 Configuration Management Module - IA-Influencer-Agent
==================================================================
Project Creator & Lead Dev IA: Fahed Mlaiel <mlaiel@live.de>
Experts: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security Expert + 
         Microservices Architect + Audio Engineer + DevOps Engineer + IA Prompt Engineer
Date: 2025-08-24

PROPRIÉTAIRE EXCLUSIF: Fahed Mlaiel
⚠️  AVERTISSEMENT LÉGAL STRICT:
Toute tentative de copie, vol, réutilisation sans autorisation
écrite explicite du propriétaire constitue une violation grave
des droits d'auteur et sera poursuivie selon la loi allemande.
Contact: mlaiel@live.de

Enterprise-grade deployment configuration management system.
==================================================================
"""
from .environment_manager import (
    EnvironmentManager,
    EnvironmentConfiguration,
    CloudProvider,
    AIProcessingTier,
    environment_manager
)

from .deployment_orchestrator import (
    DeploymentOrchestrator,
    DeploymentConfiguration,
    DeploymentStrategy,
    RollbackStrategy,
    deployment_orchestrator
)

from .content_protection_config import (
    ContentProtectionConfigManager,
    ContentProtectionConfiguration,
    FingerprintingAlgorithm,
    MonitoringMode,
    TakedownAction,
    content_protection_config_manager
)

from .monetization_config import (
    MonetizationConfigManager,
    MonetizationConfiguration,
    PlatformRevenueConfiguration,
    PaymentConfiguration,
    TaxConfiguration,
    LicensingConfiguration,
    AnalyticsConfiguration,
    FraudPreventionConfiguration,
    RevenueSource,
    PaymentGateway,
    Currency,
    PayoutFrequency,
    TaxRegion,
    LicensingType,
    monetization_config_manager
)

from .secrets_manager import (
    SecretsManager,
    SecretsConfiguration,
    SecretMetadata,
    SecretEntry,
    AccessRequest,
    SecretType,
    AccessLevel,
    SecretScope,
    EncryptionMethod,
    StorageBackend,
    secrets_manager
)

from .scaling_config import (
    ScalingConfigManager,
    ScalingConfiguration,
    ServiceScalingConfiguration,
    ClusterScalingConfiguration,
    ScalingPolicy,
    ScalingMetric,
    ResourceLimits,
    ScalingType,
    ScalingDirection,
    MetricType,
    ServiceTier,
    scaling_config_manager
)

from .backup_config import (
    BackupConfigManager,
    BackupConfiguration,
    BackupSource,
    BackupDestination,
    BackupPolicy,
    RestorePoint,
    BackupType,
    BackupSchedule,
    StorageProvider,
    CompressionMethod,
    RetentionPolicy,
    RecoveryTier,
    backup_config_manager
)

# NOUVEAUX MODULES REQUIS PAR CAHIER DES CHARGES - AI & PROTECTION
from .ai_fingerprinting_config import (
    AIFingerprintingConfigManager,
    AIFingerprintingConfiguration,
    AudioFingerprintingConfig,
    VideoFingerprintingConfig,
    ImageFingerprintingConfig,
    TextFingerprintingConfig,
    VectorMatchingConfig,
    ProcessingConfig,
    QualityAssuranceConfig,
    FingerprintAlgorithm,
    ContentType,
    SimilarityMetric,
    VectorDatabase,
    ProcessingMode,
    ai_fingerprinting_config_manager
)

from .audio_ai_config import (
    AudioAIConfigManager,
    AudioAIProcessingConfiguration,
    AudioProcessingConfig,
    NoiseReductionConfig,
    AudioEnhancementConfig,
    StreamingConfig,
    RealTimeConfig,
    AudioAIConfig,
    AudioFormat,
    AudioQuality,
    ProcessingEngine,
    NoiseReductionAlgorithm,
    AudioEnhancement,
    StreamingProtocol,
    audio_ai_config_manager
)

from .distribution_config import (
    MultiPlatformDistributionConfigManager,
    MultiPlatformDistributionConfiguration,
    PlatformConfiguration,
    ContentOptimizationConfig,
    SchedulingConfig,
    AnalyticsConfig,
    CrossPlatformSyncConfig,
    Platform,
    ContentType as DistributionContentType,
    DistributionStrategy,
    OptimizationLevel,
    PublicationStatus,
    multi_platform_distribution_config_manager
)

from .crawling_config import (
    CrawlingMonitoringConfigManager,
    CrawlingMonitoringConfiguration,
    PlatformCrawlerConfig,
    ContentDetectionConfig,
    AlertingConfig,
    AutomatedActionConfig,
    PerformanceConfig,
    CrawlerType,
    CrawlFrequency,
    DetectionMode,
    AlertLevel,
    ActionType,
    CrawlerEngine,
    crawling_monitoring_config_manager
)

from .legal_licensing_config import (
    LegalLicensingConfigManager,
    LegalLicensingConfiguration,
    LicenseConfiguration,
    DMCAConfiguration,
    ComplianceConfiguration,
    ContractManagementConfig,
    IntellectualPropertyConfig,
    LicenseType,
    LegalJurisdiction,
    ComplianceFramework,
    ContractType,
    LegalDocumentStatus,
    legal_licensing_config_manager
)

# NOUVEAU MODULE GLOBAL DE COORDINATION
from .global_config import (
    GlobalConfigurationManager,
    GlobalConfiguration,
    SystemHealthStatus,
    SystemMode,
    ConfigurationCategory,
    global_configuration_manager
)

# NOUVEAU MODULE WORKFLOW BUSINESS
from .business_workflow_config import (
    BusinessWorkflowConfigManager,
    WorkflowConfiguration,
    UploadConfiguration,
    AIProcessingConfiguration,
    ProtectionConfiguration,
    SEOOptimizationConfiguration,
    CollaborationConfiguration,
    DistributionConfiguration,
    CreatorType,
    ContentFormat,
    WorkflowStage,
    WorkflowStatus,
    OptimizationLevel,
    CollaborationType,
    business_workflow_config_manager
)

# NOUVEAU MODULE INTEGRATIONS EXTERNES
from .external_integrations_config import (
    ExternalIntegrationsConfigManager,
    ExternalIntegrationsConfiguration,
    PlatformIntegrationConfig,
    StreamingPlatformsConfig,
    SocialPlatformsConfig,
    PaymentGatewaysConfig,
    CloudServicesConfig,
    AIServicesConfig,
    IntegrationType,
    AuthenticationMethod,
    IntegrationStatus,
    external_integrations_config_manager
)

# Main configuration manager instances
__all__ = [
    # Environment Management
    "EnvironmentManager",
    "EnvironmentConfiguration", 
    "CloudProvider",
    "AIProcessingTier",
    "environment_manager",
    
    # Deployment Orchestration
    "DeploymentOrchestrator",
    "DeploymentConfiguration",
    "DeploymentStrategy",
    "RollbackStrategy", 
    "deployment_orchestrator",
    
    # Content Protection
    "ContentProtectionConfigManager",
    "ContentProtectionConfiguration",
    "FingerprintingAlgorithm",
    "MonitoringMode",
    "TakedownAction",
    "content_protection_config_manager",
    
    # Monetization
    "MonetizationConfigManager",
    "MonetizationConfiguration",
    "PlatformRevenueConfiguration",
    "PaymentConfiguration",
    "TaxConfiguration",
    "LicensingConfiguration",
    "AnalyticsConfiguration", 
    "FraudPreventionConfiguration",
    "RevenueSource",
    "PaymentGateway",
    "Currency",
    "PayoutFrequency",
    "TaxRegion",
    "LicensingType",
    "monetization_config_manager",
    
    # Secrets Management
    "SecretsManager",
    "SecretsConfiguration",
    "SecretMetadata",
    "SecretEntry",
    "AccessRequest",
    "SecretType",
    "AccessLevel",
    "SecretScope",
    "EncryptionMethod",
    "StorageBackend", 
    "secrets_manager",
    
    # Scaling Configuration
    "ScalingConfigManager",
    "ScalingConfiguration",
    "ServiceScalingConfiguration",
    "ClusterScalingConfiguration",
    "ScalingPolicy",
    "ScalingMetric",
    "ResourceLimits",
    "ScalingType",
    "ScalingDirection",
    "MetricType",
    "ServiceTier",
    "scaling_config_manager",
    
    # Backup Configuration
    "BackupConfigManager",
    "BackupConfiguration",
    "BackupSource",
    "BackupDestination",
    "BackupPolicy",
    "RestorePoint",
    "BackupType",
    "BackupSchedule",
    "StorageProvider",
    "CompressionMethod",
    "RetentionPolicy",
    "RecoveryTier",
    "backup_config_manager",
    
    # NOUVEAUX MODULES AI & PROTECTION - CONFORMES CAHIER DES CHARGES
    # AI Fingerprinting
    "AIFingerprintingConfigManager",
    "AIFingerprintingConfiguration",
    "AudioFingerprintingConfig",
    "VideoFingerprintingConfig",
    "ImageFingerprintingConfig", 
    "TextFingerprintingConfig",
    "VectorMatchingConfig",
    "ProcessingConfig",
    "QualityAssuranceConfig",
    "FingerprintAlgorithm",
    "ContentType",
    "SimilarityMetric",
    "VectorDatabase",
    "ProcessingMode",
    "ai_fingerprinting_config_manager",
    
    # Audio AI Processing
    "AudioAIConfigManager",
    "AudioAIProcessingConfiguration",
    "AudioProcessingConfig",
    "NoiseReductionConfig",
    "AudioEnhancementConfig",
    "StreamingConfig",
    "RealTimeConfig",
    "AudioAIConfig",
    "AudioFormat",
    "AudioQuality",
    "ProcessingEngine",
    "NoiseReductionAlgorithm",
    "AudioEnhancement",
    "StreamingProtocol",
    "audio_ai_config_manager",
    
    # Multi-Platform Distribution
    "MultiPlatformDistributionConfigManager",
    "MultiPlatformDistributionConfiguration",
    "PlatformConfiguration",
    "ContentOptimizationConfig",
    "SchedulingConfig",
    "AnalyticsConfig",
    "CrossPlatformSyncConfig",
    "Platform",
    "DistributionContentType",
    "DistributionStrategy",
    "OptimizationLevel",
    "PublicationStatus",
    "multi_platform_distribution_config_manager",
    
    # Crawling & Monitoring
    "CrawlingMonitoringConfigManager",
    "CrawlingMonitoringConfiguration",
    "PlatformCrawlerConfig",
    "ContentDetectionConfig",
    "AlertingConfig",
    "AutomatedActionConfig",
    "PerformanceConfig",
    "CrawlerType",
    "CrawlFrequency",
    "DetectionMode",
    "AlertLevel",
    "ActionType",
    "CrawlerEngine",
    "crawling_monitoring_config_manager",
    
    # Legal & Licensing
    "LegalLicensingConfigManager",
    "LegalLicensingConfiguration",
    "LicenseConfiguration",
    "DMCAConfiguration",
    "ComplianceConfiguration",
    "ContractManagementConfig",
    "IntellectualPropertyConfig",
    "LicenseType",
    "LegalJurisdiction",
    "ComplianceFramework",
    "ContractType",
    "LegalDocumentStatus",
    "legal_licensing_config_manager",
    
    # Global Configuration Management
    "GlobalConfigurationManager",
    "GlobalConfiguration",
    "SystemHealthStatus",
    "SystemMode",
    "ConfigurationCategory",
    "global_configuration_manager",
    
    # Business Workflow Management
    "BusinessWorkflowConfigManager",
    "WorkflowConfiguration",
    "UploadConfiguration",
    "AIProcessingConfiguration",
    "ProtectionConfiguration",
    "SEOOptimizationConfiguration",
    "CollaborationConfiguration",
    "DistributionConfiguration",
    "CreatorType",
    "ContentFormat",
    "WorkflowStage",
    "WorkflowStatus",
    "OptimizationLevel",
    "CollaborationType",
    "business_workflow_config_manager",
    
    # External Integrations Management
    "ExternalIntegrationsConfigManager",
    "ExternalIntegrationsConfiguration",
    "PlatformIntegrationConfig",
    "StreamingPlatformsConfig",
    "SocialPlatformsConfig",
    "PaymentGatewaysConfig",
    "CloudServicesConfig",
    "AIServicesConfig",
    "IntegrationType",
    "AuthenticationMethod",
    "IntegrationStatus",
    "external_integrations_config_manager"
]

# Configuration management exports
from .base_config import ConfigurationManager, ConfigurationProfile, ConfigurationSection
from .environment_manager import EnvironmentManager, Environment, EnvironmentVariable
from .deployment_orchestrator import DeploymentOrchestrator, DeploymentStrategy, DeploymentPhase
from .security_config import SecurityConfigManager, SecurityPolicy, EncryptionConfig
from .performance_tuning import PerformanceTuningManager, PerformanceProfile, ResourceOptimization
from .monitoring_config import MonitoringConfigManager, MetricsConfig, AlertingRule
from .database_config import DatabaseConfigManager, DatabaseConnection, ConnectionPool
from .network_config import NetworkConfigManager, NetworkPolicy, LoadBalancerConfig
from .secrets_manager import SecretsManager, SecretPolicy, RotationStrategy
from .scaling_config import ScalingConfigManager, ScalingPolicy, AutoScalingMetric
from .backup_config import BackupConfigManager, BackupStrategy, RecoveryPlan
from .compliance_config import ComplianceConfigManager, ComplianceFramework, ControlMapping
from .validation_engine import ValidationEngine, ValidationRule, ValidationReport
from .deployment_templates import DeploymentTemplateManager, DeploymentTemplate, TemplateContext

__all__ = [
    # Base configuration
    "ConfigurationManager",
    "ConfigurationProfile", 
    "ConfigurationSection",
    
    # Environment management
    "EnvironmentManager",
    "Environment",
    "EnvironmentVariable",
    
    # Deployment orchestration
    "DeploymentOrchestrator",
    "DeploymentStrategy",
    "DeploymentPhase",
    
    # Security configuration
    "SecurityConfigManager",
    "SecurityPolicy",
    "EncryptionConfig",
    
    # Performance tuning
    "PerformanceTuningManager",
    "PerformanceProfile",
    "ResourceOptimization",
    
    # Monitoring configuration
    "MonitoringConfigManager",
    "MetricsConfig",
    "AlertingRule",
    
    # Database configuration
    "DatabaseConfigManager",
    "DatabaseConnection",
    "ConnectionPool",
    
    # Network configuration
    "NetworkConfigManager",
    "NetworkPolicy",
    "LoadBalancerConfig",
    
    # Secrets management
    "SecretsManager",
    "SecretPolicy",
    "RotationStrategy",
    
    # Scaling configuration
    "ScalingConfigManager",
    "ScalingPolicy",
    "AutoScalingMetric",
    
    # Backup configuration
    "BackupConfigManager",
    "BackupStrategy",
    "RecoveryPlan",
    
    # Compliance configuration
    "ComplianceConfigManager",
    "ComplianceFramework",
    "ControlMapping",
    
    # Validation engine
    "ValidationEngine",
    "ValidationRule",
    "ValidationReport",
    
    # Deployment templates
    "DeploymentTemplateManager",
    "DeploymentTemplate",
    "TemplateContext",
]

__version__ = "1.0.0"

from typing import Dict, Any, Optional, List, Type, Union
import logging
from datetime import datetime
from enum import Enum

# Core configuration managers
from .base_config import BaseConfigurationManager, ConfigurationError
from .environment_manager import EnvironmentManager, EnvironmentType
from .deployment_orchestrator import DeploymentOrchestrator, DeploymentStrategy
from .security_config import SecurityConfigManager, SecurityLevel
from .performance_tuning import PerformanceTuningManager, ResourceProfile
from .monitoring_config import MonitoringConfigManager, ObservabilityLevel
from .database_config import DatabaseConfigManager, DatabaseCluster
from .network_config import NetworkConfigManager, ServiceDiscovery
from .secrets_manager import SecretsManager, SecretRotationPolicy
from .scaling_config import ScalingConfigManager, AutoScalingPolicy
from .backup_config import BackupConfigManager, BackupStrategy
from .compliance_config import ComplianceConfigManager, ComplianceFramework
from .validation_engine import ConfigurationValidator, ValidationRule
from .deployment_templates import TemplateManager, InfrastructureTemplate

# NOUVEAUX MODULES - IMPORTS DIRECTS
from .ai_fingerprinting_config import AIFingerprintingConfigManager
from .audio_ai_config import AudioAIConfigManager
from .distribution_config import MultiPlatformDistributionConfigManager
from .crawling_config import CrawlingMonitoringConfigManager
from .legal_licensing_config import LegalLicensingConfigManager

# Initialize module logger
logger = logging.getLogger(__name__)

# Module version and metadata
__version__ = "2.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__copyright__ = "© 2025 Fahed Mlaiel. All rights reserved."

class ConfigurationModule:
    """    Master configuration module for deployment management.
    
    Provides unified interface for enterprise-grade configuration management
    across multiple environments, cloud platforms, and deployment strategies.
    
    Features:
    - Multi-environment configuration management
    - Cloud-native deployment orchestration
    - Security and compliance automation
    - Performance optimization and auto-scaling
    - Comprehensive monitoring and observability
    - Database clustering and high availability
    - Network configuration and service discovery
    - Secrets management and rotation
    - Backup and disaster recovery
    - Infrastructure as Code templates
    """    
    def __init__(self):
        """Initialize configuration module with all managers"""        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Core managers
        self.base_config = BaseConfigurationManager()
        self.environment_manager = EnvironmentManager()
        self.deployment_orchestrator = DeploymentOrchestrator()
        self.security_config = SecurityConfigManager()
        self.performance_tuning = PerformanceTuningManager()
        self.monitoring_config = MonitoringConfigManager()
        self.database_config = DatabaseConfigManager()
        self.network_config = NetworkConfigManager()
        self.secrets_manager = SecretsManager()
        self.scaling_config = ScalingConfigManager()
        self.backup_config = BackupConfigManager()
        self.compliance_config = ComplianceConfigManager()
        self.validation_engine = ConfigurationValidator()
        self.template_manager = TemplateManager()
        
        # NOUVEAUX MANAGERS AJOUTÉS - CONFORMES CAHIER DES CHARGES
        self.ai_fingerprinting_config = AIFingerprintingConfigManager()
        self.audio_ai_config = AudioAIConfigManager()
        self.distribution_config = MultiPlatformDistributionConfigManager()
        self.crawling_config = CrawlingMonitoringConfigManager()
        self.legal_licensing_config = LegalLicensingConfigManager()
        
        # Module state
        self.initialized = False
        self.active_environment = None
        self.deployment_history = []
        
        self.logger.info("Configuration module initialized successfully")
    
    async def initialize_configuration(
        self,
        environment: str,
        deployment_strategy: str = "rolling",
        security_level: str = "high",
        enable_monitoring: bool = True
    ) -> bool:
        """        Initialize complete configuration for specified environment.
        
        Args:
            environment: Target environment (development, staging, production)
            deployment_strategy: Deployment strategy (rolling, blue_green, canary)
            security_level: Security configuration level (basic, standard, high, maximum)
            enable_monitoring: Enable monitoring and observability
            
        Returns:
            bool: True if initialization successful
        """        try:
            self.logger.info(f"Initializing configuration for environment: {environment}")
            
            # Initialize all managers
            managers = [
                self.base_config,
                self.environment_manager,
                self.deployment_orchestrator,
                self.security_config,
                self.performance_tuning,
                self.monitoring_config,
                self.database_config,
                self.network_config,
                self.secrets_manager,
                self.scaling_config,
                self.backup_config,
                self.compliance_config,
                self.validation_engine,
                self.template_manager,
                # NOUVEAUX MANAGERS INTÉGRÉS
                self.ai_fingerprinting_config,
                self.audio_ai_config,
                self.distribution_config,
                self.crawling_config,
                self.legal_licensing_config
            ]
            
            for manager in managers:
                if hasattr(manager, 'initialize'):
                    await manager.initialize()
            
            # Set environment
            await self.environment_manager.set_environment(environment)
            self.active_environment = environment
            
            # Configure deployment strategy
            await self.deployment_orchestrator.set_strategy(deployment_strategy)
            
            # Set security level
            await self.security_config.set_security_level(security_level)
            
            # Enable monitoring if requested
            if enable_monitoring:
                await self.monitoring_config.enable_full_monitoring()
            
            # Validate configuration
            validation_result = await self.validation_engine.validate_complete_configuration()
            if not validation_result.is_valid:
                raise ConfigurationError(f"Configuration validation failed: {validation_result.errors}")
            
            self.initialized = True
            self.logger.info("Configuration module initialization completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize configuration: {e}")
            return False
    
    async def deploy_environment(
        self,
        target_environment: str,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """        Deploy complete environment with all configurations.
        
        Args:
            target_environment: Target environment to deploy
            dry_run: If True, only validate without actual deployment
            
        Returns:
            Dict containing deployment results and metrics
        """        try:
            self.logger.info(f"Starting deployment to {target_environment} (dry_run={dry_run})")
            
            deployment_id = f"deploy_{target_environment}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Pre-deployment validation
            validation_result = await self.validation_engine.validate_deployment_readiness(target_environment)
            if not validation_result.is_valid:
                raise ConfigurationError(f"Pre-deployment validation failed: {validation_result.errors}")
            
            # Execute deployment
            deployment_result = await self.deployment_orchestrator.execute_deployment(
                environment=target_environment,
                deployment_id=deployment_id,
                dry_run=dry_run
            )
            
            # Record deployment
            self.deployment_history.append({
                "id": deployment_id,
                "environment": target_environment,
                "timestamp": datetime.now(),
                "result": deployment_result,
                "dry_run": dry_run
            })
            
            self.logger.info(f"Deployment {deployment_id} completed successfully")
            return deployment_result
            
        except Exception as e:
            self.logger.error(f"Deployment failed: {e}")
            raise
    
    async def get_environment_status(self, environment: str) -> Dict[str, Any]:
        """Get comprehensive status of specified environment"""        try:
            status = {
                "environment": environment,
                "timestamp": datetime.now(),
                "components": {}
            }
            
            # Collect status from all managers
            managers = {
                "base_config": self.base_config,
                "deployment": self.deployment_orchestrator,
                "security": self.security_config,
                "performance": self.performance_tuning,
                "monitoring": self.monitoring_config,
                "database": self.database_config,
                "network": self.network_config,
                "secrets": self.secrets_manager,
                "scaling": self.scaling_config,
                "backup": self.backup_config,
                "compliance": self.compliance_config,
                # NOUVEAUX MANAGERS STATUS
                "ai_fingerprinting": self.ai_fingerprinting_config,
                "audio_ai": self.audio_ai_config,
                "distribution": self.distribution_config,
                "crawling": self.crawling_config,
                "legal_licensing": self.legal_licensing_config
            }
            
            for name, manager in managers.items():
                if hasattr(manager, 'get_status'):
                    status["components"][name] = await manager.get_status()
            
            return status
            
        except Exception as e:
            self.logger.error(f"Failed to get environment status: {e}")
            raise
    
    def get_module_info(self) -> Dict[str, Any]:
        """Get module information and metadata"""        return {
            "name": "Deployment Configuration Module",
            "version": __version__,
            "author": __author__,
            "email": __email__,
            "copyright": __copyright__,
            "initialized": self.initialized,
            "active_environment": self.active_environment,
            "deployment_count": len(self.deployment_history),
            "supported_environments": ["development", "staging", "production", "testing"],
            "supported_strategies": ["rolling", "blue_green", "canary", "recreate"],
            "supported_platforms": ["kubernetes", "docker", "aws", "gcp", "azure"],
            "features": [
                "Multi-environment management",
                "Cloud-native deployment",
                "Security automation",
                "Performance optimization",
                "Auto-scaling",
                "Monitoring integration",
                "Database clustering",
                "Service discovery",
                "Secrets management",
                "Backup automation",
                "Compliance validation",
                "Infrastructure as Code",
                # NOUVELLES FONCTIONNALITÉS AJOUTÉES
                "AI Content Fingerprinting",
                "Audio AI Processing",
                "Multi-platform Distribution",
                "Web Crawling & Monitoring",
                "Legal & Licensing Management",
                "Copyright Protection",
                "DMCA Automation",
                "Revenue Tracking",
                "Automated Takedowns",
                "Content Analytics"
            ]
        }

# Create module instance
configuration_module = ConfigurationModule()

# Public API exports
__all__ = [
    # Main module
    "ConfigurationModule",
    "configuration_module",
    
    # Core managers
    "BaseConfigurationManager",
    "EnvironmentManager",
    "DeploymentOrchestrator", 
    "SecurityConfigManager",
    "PerformanceTuningManager",
    "MonitoringConfigManager",
    "DatabaseConfigManager",
    "NetworkConfigManager",
    "SecretsManager",
    "ScalingConfigManager",
    "BackupConfigManager",
    "ComplianceConfigManager",
    "ConfigurationValidator",
    "TemplateManager",
    
    # Enums and types
    "EnvironmentType",
    "DeploymentStrategy",
    "SecurityLevel",
    "ResourceProfile",
    "ObservabilityLevel",
    "DatabaseCluster",
    "ServiceDiscovery",
    "SecretRotationPolicy",
    "AutoScalingPolicy",
    "BackupStrategy",
    "ComplianceFramework",
    "ValidationRule",
    "InfrastructureTemplate",
    
    # Exceptions
    "ConfigurationError",
    
    # Module metadata
    "__version__",
    "__author__",
    "__email__",
    "__copyright__"
]
