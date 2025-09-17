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

# Version and metadata
__version__ = "1.0.0"
__author__ = "Fahed Mlaiel <mlaiel@live.de>"
__copyright__ = "© 2025 Fahed Mlaiel. All rights reserved."
__license__ = "Proprietary - Unauthorized use prohibited"

# Enterprise monitoring suite components
__all__ = [
    "MonitoringSystem",
    "MetricsCollector", 
    "AlertManager",
    "AnomalyDetector",
    "EnterpriseMonitoringOrchestrator",
    "EnterpriseMonitoringConfig",
    "MonitoringTier",
    "CreatorType",
    "create_enterprise_monitoring_orchestrator",
    "CreatorEconomyEnterpriseOrchestrator",
    "CreatorProfile",
    "CreatorMetrics", 
    "CreatorTier",
    "CreatorStatus",
    "CollaborationType",
    "RevenueStream",
    "EnterpriseSecurityMonitoringCenter",
    "SecurityThreat",
    "SecurityIncident", 
    "CreatorIPAsset",
    "ThreatLevel",
    "ThreatType",
    "IncidentStatus",
    "EnterprisePerformanceOptimizationEngine",
    "PerformanceMetric",
    "PerformanceBottleneck",
    "OptimizationRecommendation",
    "PerformanceMetricType",
    "OptimizationStrategy",
    "EnterpriseScalabilityIntelligence", 
    "ScalabilityPrediction",
    "CapacityPlan",
    "ScalingEvent",
    "ScalabilityMetric",
    "ScalingDirection",
    "ResourceType",
    "EnterpriseComplianceAutomationSystem",
    "ComplianceRule",
    "ComplianceViolation",
    "AuditTrail",
    "DataProtectionRecord",
    "ComplianceFramework",
    "ComplianceStatus",
    "ViolationType",
    "EnterpriseBusinessIntelligenceHub",
    "BusinessMetric",
    "BusinessInsight",
    "BusinessReport",
    "KPIDashboard",
    "BusinessMetricType",
    "AnalyticsCategory",
    "InsightType",
    "EnterpriseCreatorAnalyticsPlatform",
    "CreatorAnalyticsData",
    "CreatorAnalyticsProfile",
    "ContentAnalytics",
    "AudienceAnalytics",
    "CreatorAnalyticsMetric",
    "ContentType",
    "AudienceSegment",
    "__version__",
    "__author__",
    "__copyright__",
    "__license__"
]

