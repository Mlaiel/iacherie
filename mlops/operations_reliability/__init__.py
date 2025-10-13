"""
🛡️ MLOps Operations & Reliability - Enterprise Architecture
===============================================================

⚠️  AVERTISSEMENT LÉGAL OBLIGATOIRE:
==========================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques

🏢 USAGE ENTREPRISE:
- Licence entreprise disponible sur demande
- Support technique inclus avec licence
- Maintenance et mises à jour assurées
- Formation équipe technique fournie

Enterprise operations reliability module for Creator Economy MLOps platform.
Combining expertise: Lead Dev IA + Backend Senior + ML Engineer + DBA + 
Sécurité + Microservices + Audio + DevOps + IA Prompt Engineer

Author: Fahed Mlaiel  
Contact: mlaiel@live.de
"""

# Core existing components
from .cost_optimizer import (
    CostOptimizer,
    CostOptimizationStrategy,
    ResourceType,
    CloudProvider,
    CostMetrics
)

from .feature_flag_manager import (
    FeatureFlagManager,
    FeatureFlagType,
    FeatureFlagStatus,
    TargetingRule
)

# New enterprise components
from .capacity_planning_engine import (
    CapacityPlanningEngine,
    ResourceType as CapacityResourceType,
    CreatorTier,
    PredictionModel,
    CapacityMetrics,
    PredictionResult,
    ScalingRecommendation
)

from .chaos_engineering_platform import (
    ChaosEngineeringPlatform,
    ChaosExperimentType,
    ExperimentStatus,
    ImpactLevel,
    ChaosTarget,
    ExperimentConfig,
    ExperimentResult,
    SafetyGuard
)

from .dependency_health_monitor import (
    DependencyHealthMonitor,
    DependencyType,
    HealthStatus,
    AlertSeverity,
    CheckType,
    DependencyConfig,
    HealthCheckResult,
    DependencyMetrics,
    HealthAlert
)

from .performance_optimization_engine import (
    PerformanceOptimizationEngine,
    OptimizationType,
    CreatorWorkloadType,
    OptimizationPriority,
    MetricType,
    PerformanceMetric,
    OptimizationRule,
    OptimizationResult,
    PerformanceBaseline
)

from .auto_scaling_intelligence import (
    AutoScalingIntelligence,
    ScalingDirection,
    ScalingTrigger,
    ScalingPolicy,
    ScalingMetric,
    ScalingRule,
    ScalingDecision,
    CreatorActivityPattern
)

from .incident_response_automation import (
    IncidentResponseAutomation,
    IncidentSeverity,
    IncidentStatus,
    IncidentCategory,
    ResponseAction,
    CreatorImpactLevel,
    IncidentAlert,
    Incident,
    ResponsePlaybook,
    ResponseExecution
)

from .maintenance_window_scheduler import (
    MaintenanceWindowScheduler,
    MaintenanceType,
    MaintenanceStatus,
    MaintenanceWindow
)

from .service_level_enforcer import (
    ServiceLevelEnforcer,
    SLIType,
    SLOViolationSeverity,
    ServiceTier,
    ComplianceStatus,
    ServiceLevelIndicator,
    ServiceLevelObjective,
    ServiceLevelAgreement,
    SLOViolation,
    ErrorBudget
)

from .operational_dashboard_controller import (
    OperationalDashboardController,
    DashboardType,
    MetricSeverity,
    DashboardUpdateFrequency,
    DashboardMetric,
    DashboardWidget,
    Dashboard,
    AlertSummary
)

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__copyright__ = "© 2025 Fahed Mlaiel - Tous droits réservés"

__all__ = [
    # Cost Optimization
    "CostOptimizer",
    "CostOptimizationStrategy", 
    "ResourceType",
    "CloudProvider",
    "CostMetrics",
    
    # Feature Flags
    "FeatureFlagManager",
    "FeatureFlagType",
    "FeatureFlagStatus",
    "TargetingRule",
    
    # Capacity Planning
    "CapacityPlanningEngine",
    "CapacityResourceType",
    "CreatorTier",
    "PredictionModel",
    "CapacityMetrics",
    "PredictionResult",
    "ScalingRecommendation",
    
    # Chaos Engineering
    "ChaosEngineeringPlatform",
    "ChaosExperimentType",
    "ExperimentStatus",
    "ImpactLevel",
    "ChaosTarget",
    "ExperimentConfig",
    "ExperimentResult",
    "SafetyGuard",
    
    # Dependency Health Monitoring
    "DependencyHealthMonitor",
    "DependencyType",
    "HealthStatus",
    "AlertSeverity",
    "CheckType",
    "DependencyConfig",
    "HealthCheckResult",
    "DependencyMetrics",
    "HealthAlert",
    
    # Performance Optimization
    "PerformanceOptimizationEngine",
    "OptimizationType",
    "CreatorWorkloadType",
    "OptimizationPriority",
    "MetricType",
    "PerformanceMetric",
    "OptimizationRule",
    "OptimizationResult",
    "PerformanceBaseline",
    
    # Auto Scaling Intelligence
    "AutoScalingIntelligence",
    "ScalingDirection",
    "ScalingTrigger",
    "ScalingPolicy",
    "ScalingMetric",
    "ScalingRule",
    "ScalingDecision",
    "CreatorActivityPattern",
    
    # Incident Response Automation
    "IncidentResponseAutomation",
    "IncidentSeverity",
    "IncidentStatus",
    "IncidentCategory",
    "ResponseAction",
    "CreatorImpactLevel",
    "IncidentAlert",
    "Incident",
    "ResponsePlaybook",
    "ResponseExecution",
    
    # Maintenance Window Scheduler
    "MaintenanceWindowScheduler",
    "MaintenanceType",
    "MaintenanceStatus",
    "MaintenanceWindow",
    
    # Service Level Enforcer
    "ServiceLevelEnforcer",
    "SLIType",
    "SLOViolationSeverity",
    "ServiceTier",
    "ComplianceStatus",
    "ServiceLevelIndicator",
    "ServiceLevelObjective",
    "ServiceLevelAgreement",
    "SLOViolation",
    "ErrorBudget",
    
    # Operational Dashboard Controller
    "OperationalDashboardController",
    "DashboardType",
    "MetricSeverity",
    "DashboardUpdateFrequency",
    "DashboardMetric",
    "DashboardWidget",
    "Dashboard",
    "AlertSummary",
    
    # Core metadata
    "__version__",
    "__author__",
    "__email__",
    "__copyright__"
]