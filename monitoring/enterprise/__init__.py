"""Enterprise Monitoring Suite for Creator Economy Platform
=========================================================

Complete enterprise-grade monitoring, analytics, and intelligence suite
for Creator Economy platform with comprehensive business intelligence,
performance optimization, security monitoring, and compliance automation.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
License: Proprietary - Unauthorized use prohibited
"""

# Core monitoring system
from .comprehensive_monitoring import (
    MonitoringSystem,
    MetricsCollector,
    AlertManager,
    AnomalyDetector
)

# Main orchestrator
from .index import (
    EnterpriseMonitoringOrchestrator,
    EnterpriseMonitoringConfig,
    MonitoringTier,
    CreatorType,
    create_enterprise_monitoring_orchestrator
)

# Creator Economy orchestration
from .creator_economy_enterprise_orchestrator import (
    CreatorEconomyEnterpriseOrchestrator,
    CreatorProfile,
    CreatorMetrics,
    CreatorTier,
    CreatorStatus,
    CollaborationType,
    RevenueStream
)

# Security monitoring
from .enterprise_security_monitoring_center import (
    EnterpriseSecurityMonitoringCenter,
    SecurityThreat,
    SecurityIncident,
    CreatorIPAsset,
    ThreatLevel,
    ThreatType,
    IncidentStatus
)

# Performance optimization
from .enterprise_performance_optimization_engine import (
    EnterprisePerformanceOptimizationEngine,
    PerformanceMetric,
    PerformanceBottleneck,
    OptimizationRecommendation,
    PerformanceMetricType,
    OptimizationStrategy
)

# Scalability intelligence
from .enterprise_scalability_intelligence import (
    EnterpriseScalabilityIntelligence,
    ScalabilityPrediction,
    CapacityPlan,
    ScalingEvent,
    ScalabilityMetric,
    ScalingDirection,
    ResourceType
)

# Compliance automation
from .enterprise_compliance_automation_system import (
    EnterpriseComplianceAutomationSystem,
    ComplianceRule,
    ComplianceViolation,
    AuditTrail,
    DataProtectionRecord,
    ComplianceFramework,
    ComplianceStatus,
    ViolationType
)

# Business intelligence
from .enterprise_business_intelligence_hub import (
    EnterpriseBusinessIntelligenceHub,
    BusinessMetric,
    BusinessInsight,
    BusinessReport,
    KPIDashboard,
    BusinessMetricType,
    AnalyticsCategory,
    InsightType
)

# Creator analytics
from .enterprise_creator_analytics_platform import (
    EnterpriseCreatorAnalyticsPlatform,
    CreatorAnalyticsData,
    CreatorProfile as CreatorAnalyticsProfile,
    ContentAnalytics,
    AudienceAnalytics,
    CreatorAnalyticsMetric,
    ContentType,
    AudienceSegment
)

# Revenue optimization
from .enterprise_revenue_optimization_center import (
    EnterpriseRevenueOptimizationCenter,
    RevenueMetric,
    RevenueOpportunity,
    MonetizationModel,
    RevenueForecast,
    RevenueStream,
    MonetizationStrategy,
    RevenueTrend,
    create_enterprise_revenue_optimization_center
)

# Collaboration intelligence
from .enterprise_collaboration_intelligence_engine import (
    EnterpriseCollaborationIntelligenceEngine,
    CreatorProfile as CollaborationCreatorProfile,
    CollaborationMatch,
    ActiveCollaboration,
    CollaborationAnalytics,
    CollaborationNetwork,
    CollaborationType,
    CollaborationStatus,
    MatchingStrategy,
    CollaborationImpact,
    create_enterprise_collaboration_intelligence_engine
)

# Content quality assurance
from .enterprise_content_quality_assurance_system import (
    EnterpriseContentQualityAssuranceSystem,
    ContentAsset,
    QualityAssessment,
    QualityRule,
    QualityImprovement,
    QualityBenchmark,
    ContentType as QAContentType,
    QualityMetric,
    QualityStatus,
    ComplianceFramework,
    create_enterprise_content_quality_assurance_system
)

# Infrastructure automation
from .enterprise_infrastructure_automation_hub import (
    EnterpriseInfrastructureAutomationHub,
    InfrastructureComponent,
    DeploymentPipeline,
    AutomationScript,
    AutomationExecution,
    InfrastructureMetrics,
    ScalingPolicy,
    InfrastructureType,
    DeploymentStrategy,
    AutomationTrigger,
    InfrastructureStatus,
    CloudProvider,
    create_enterprise_infrastructure_automation_hub
)

# Creator tier management
from .enterprise_creator_tier_management_system import (
    EnterpriseCreatorTierManagementSystem,
    TierCriteria,
    TierBenefit,
    CreatorTierProfile,
    TierProgression,
    TierAnalytics,
    CreatorTier,
    TierCriteriaType,
    BenefitType,
    ProgressionStatus,
    create_enterprise_creator_tier_management_system
)

# Multi-platform integration
from .enterprise_multi_platform_integration_center import (
    EnterpriseMultiPlatformIntegrationCenter,
    PlatformConfiguration,
    ContentDistribution,
    PlatformAnalytics,
    AudienceInsights,
    ContentSyncJob,
    Platform,
    ContentType as PlatformContentType,
    SyncStatus,
    IntegrationType,
    create_enterprise_multi_platform_integration_center
)

# AI/ML monitoring intelligence
from .enterprise_ai_ml_monitoring_intelligence import (
    EnterpriseAIMLMonitoringIntelligence,
    AIModelProfile,
    ModelPerformanceMetrics,
    ModelAlert,
    PredictionLog,
    ModelRetraining,
    ModelType,
    ModelStatus,
    AlertLevel,
    MetricType,
    create_enterprise_ai_ml_monitoring_intelligence
)

# Gamification analytics
from .enterprise_gamification_analytics_engine import (
    EnterpriseGamificationAnalyticsEngine,
    Achievement,
    UserAchievement,
    Challenge,
    ChallengeParticipation,
    GamificationProfile,
    GamificationAnalytics,
    AchievementType,
    RewardType,
    EngagementLevel,
    ChallengeStatus,
    LeaderboardType,
    create_enterprise_gamification_analytics_engine
)

# Real-time operations
from .enterprise_real_time_operations_center import (
    EnterpriseRealTimeOperationsCenter,
    RealTimeMetric,
    SystemAlert,
    Incident,
    AutomatedResponse,
    OperationsTask,
    SystemHealthCheck,
    AlertSeverity,
    IncidentStatus,
    SystemHealth,
    OperationStatus,
    NotificationChannel,
    create_enterprise_real_time_operations_center
)

# Version and metadata
__version__ = "1.0.0"
__author__ = "Fahed Mlaiel <mlaiel@live.de>"
__copyright__ = "© 2025 Fahed Mlaiel. All rights reserved."
__license__ = "Proprietary - Unauthorized use prohibited"

# Enterprise monitoring suite components
__all__ = [
    # Core monitoring system
    "MonitoringSystem",
    "MetricsCollector", 
    "AlertManager",
    "AnomalyDetector",
    
    # Main orchestrator
    "EnterpriseMonitoringOrchestrator",
    "EnterpriseMonitoringConfig",
    "MonitoringTier",
    "CreatorType",
    "create_enterprise_monitoring_orchestrator",
    
    # Creator Economy orchestration
    "CreatorEconomyEnterpriseOrchestrator",
    "CreatorProfile",
    "CreatorMetrics", 
    "CreatorTier",
    "CreatorStatus",
    "CollaborationType",
    "RevenueStream",
    
    # Security monitoring
    "EnterpriseSecurityMonitoringCenter",
    "SecurityThreat",
    "SecurityIncident", 
    "CreatorIPAsset",
    "ThreatLevel",
    "ThreatType",
    "IncidentStatus",
    
    # Performance optimization
    "EnterprisePerformanceOptimizationEngine",
    "PerformanceMetric",
    "PerformanceBottleneck",
    "OptimizationRecommendation",
    "PerformanceMetricType",
    "OptimizationStrategy",
    
    # Scalability intelligence
    "EnterpriseScalabilityIntelligence", 
    "ScalabilityPrediction",
    "CapacityPlan",
    "ScalingEvent",
    "ScalabilityMetric",
    "ScalingDirection",
    "ResourceType",
    
    # Compliance automation
    "EnterpriseComplianceAutomationSystem",
    "ComplianceRule",
    "ComplianceViolation",
    "AuditTrail",
    "DataProtectionRecord",
    "ComplianceFramework",
    "ComplianceStatus",
    "ViolationType",
    
    # Business intelligence
    "EnterpriseBusinessIntelligenceHub",
    "BusinessMetric",
    "BusinessInsight",
    "BusinessReport",
    "KPIDashboard",
    "BusinessMetricType",
    "AnalyticsCategory",
    "InsightType",
    
    # Creator analytics
    "EnterpriseCreatorAnalyticsPlatform",
    "CreatorAnalyticsData",
    "CreatorAnalyticsProfile",
    "ContentAnalytics",
    "AudienceAnalytics",
    "CreatorAnalyticsMetric",
    "ContentType",
    "AudienceSegment",
    
    # Revenue optimization
    "EnterpriseRevenueOptimizationCenter",
    "RevenueMetric",
    "RevenueOpportunity",
    "MonetizationModel",
    "RevenueForecast",
    "RevenueStream",
    "MonetizationStrategy",
    "RevenueTrend",
    "create_enterprise_revenue_optimization_center",
    
    # Collaboration intelligence
    "EnterpriseCollaborationIntelligenceEngine",
    "CollaborationCreatorProfile",
    "CollaborationMatch",
    "ActiveCollaboration",
    "CollaborationAnalytics",
    "CollaborationNetwork",
    "CollaborationType",
    "CollaborationStatus",
    "MatchingStrategy",
    "CollaborationImpact",
    "create_enterprise_collaboration_intelligence_engine",
    
    # Content quality assurance
    "EnterpriseContentQualityAssuranceSystem",
    "ContentAsset",
    "QualityAssessment",
    "QualityRule",
    "QualityImprovement",
    "QualityBenchmark",
    "QAContentType",
    "QualityMetric",
    "QualityStatus",
    "ComplianceFramework",
    "create_enterprise_content_quality_assurance_system",
    
    # Infrastructure automation
    "EnterpriseInfrastructureAutomationHub",
    "InfrastructureComponent",
    "DeploymentPipeline",
    "AutomationScript",
    "AutomationExecution",
    "InfrastructureMetrics",
    "ScalingPolicy",
    "InfrastructureType",
    "DeploymentStrategy",
    "AutomationTrigger",
    "InfrastructureStatus",
    "CloudProvider",
    "create_enterprise_infrastructure_automation_hub",
    
    # Creator tier management
    "EnterpriseCreatorTierManagementSystem",
    "TierCriteria",
    "TierBenefit",
    "CreatorTierProfile",
    "TierProgression",
    "TierAnalytics",
    "CreatorTier",
    "TierCriteriaType",
    "BenefitType",
    "ProgressionStatus",
    "create_enterprise_creator_tier_management_system",
    
    # Multi-platform integration
    "EnterpriseMultiPlatformIntegrationCenter",
    "PlatformConfiguration",
    "ContentDistribution",
    "PlatformAnalytics",
    "AudienceInsights",
    "ContentSyncJob",
    "Platform",
    "PlatformContentType",
    "SyncStatus",
    "IntegrationType",
    "create_enterprise_multi_platform_integration_center",
    
    # AI/ML monitoring intelligence
    "EnterpriseAIMLMonitoringIntelligence",
    "AIModelProfile",
    "ModelPerformanceMetrics",
    "ModelAlert",
    "PredictionLog",
    "ModelRetraining",
    "ModelType",
    "ModelStatus",
    "AlertLevel",
    "MetricType",
    "create_enterprise_ai_ml_monitoring_intelligence",
    
    # Gamification analytics
    "EnterpriseGamificationAnalyticsEngine",
    "Achievement",
    "UserAchievement",
    "Challenge",
    "ChallengeParticipation",
    "GamificationProfile",
    "GamificationAnalytics",
    "AchievementType",
    "RewardType",
    "EngagementLevel",
    "ChallengeStatus",
    "LeaderboardType",
    "create_enterprise_gamification_analytics_engine",
    
    # Real-time operations
    "EnterpriseRealTimeOperationsCenter",
    "RealTimeMetric",
    "SystemAlert",
    "Incident",
    "AutomatedResponse",
    "OperationsTask",
    "SystemHealthCheck",
    "AlertSeverity",
    "IncidentStatus",
    "SystemHealth",
    "OperationStatus",
    "NotificationChannel",
    "create_enterprise_real_time_operations_center",
    
    # Version and metadata
    "__version__",
    "__author__",
    "__copyright__",
    "__license__"
]

