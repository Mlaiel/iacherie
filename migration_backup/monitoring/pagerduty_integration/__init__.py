"""
PagerDuty Integration Module for IA Chéries Platform
Intelligent alerting and incident management for Creator Economy

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  AVERTISSEMENT LÉGAL:
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques
"""

from .pagerduty_client import PagerDutyClient, IncidentSeverity, IncidentStatus
from .escalation_manager import EscalationManager
from .intelligent_alert_router import IntelligentAlertRouter
from .creator_incident_classifier import (
    CreatorIncidentClassifier, 
    CreatorWorkflowStage, 
    IncidentCategory, 
    BusinessImpactLevel, 
    TeamAssignment
)
from .revenue_impact_calculator import (
    RevenueImpactCalculator,
    RevenueStreamType,
    ImpactSeverity,
    CreatorMetrics,
    IncidentImpactResult
)
from .collaboration_incident_manager import (
    CollaborationIncidentManager,
    CollaborationType,
    StakeholderRole,
    CollaborationIncident
)
from .content_protection_alerting import (
    ContentProtectionAlerting,
    ViolationType,
    ThreatLevel,
    ProtectionViolation
)
from .predictive_incident_engine import (
    PredictiveIncidentEngine,
    PredictionType,
    PredictionConfidence,
    IncidentPrediction,
    MetricData
)
from .multi_channel_notification import (
    MultiChannelNotificationSystem,
    NotificationChannel,
    NotificationPriority,
    NotificationMessage
)
from .incident_analytics_engine import (
    IncidentAnalyticsEngine,
    AnalyticsType,
    IncidentMetrics,
    AnalyticsResult
)
from .automated_runbook_executor import (
    RunbookExecutor,
    ActionType,
    RunbookDefinition,
    ExecutionStatus
)
from .service_mesh_integration import (
    ServiceMeshIntegration,
    ServiceNode,
    ServiceDependency,
    ServiceMeshAlert,
    TraceSpan,
    ServiceHealthStatus,
    TrafficDirection,
    CircuitBreakerState,
    get_service_mesh_integration,
    create_service_mesh_integration
)
from .external_vendor_alerting import (
    ExternalVendorAlerting,
    VendorEndpoint,
    VendorHealthCheck,
    SLAMetrics,
    VendorAlert,
    VendorType,
    ServiceStatus,
    SLABreachSeverity,
    get_external_vendor_alerting,
    create_external_vendor_alerting
)
from .compliance_incident_handler import (
    ComplianceIncidentHandler,
    ComplianceIncident,
    ComplianceRequirement,
    AuditEntry,
    ComplianceAlert,
    ComplianceFramework,
    IncidentSeverity as ComplianceIncidentSeverity,
    ComplianceStatus,
    DataType,
    get_compliance_incident_handler,
    create_compliance_incident_handler
)
from .crisis_communication_manager import (
    CrisisCommunicationManager,
    CrisisEvent,
    CrisisMessage,
    StakeholderGroup,
    SocialMediaPost,
    CrisisLevel,
    CommunicationChannel,
    StakeholderType,
    MessageType,
    get_crisis_communication_manager,
    create_crisis_communication_manager
)
from .incident_lifecycle_tracker import (
    IncidentLifecycleTracker,
    IncidentTimeline,
    StateTransition,
    ResourceAllocation,
    LifecycleMetrics,
    IncidentState,
    StateTransitionTrigger,
    ResourceType,
    IncidentPriority,
    get_incident_lifecycle_tracker,
    create_incident_lifecycle_tracker
)
from .pagerduty_metrics_collector import (
    PagerDutyMetricsCollector,
    MetricDefinition,
    MetricDataPoint,
    MetricSeries,
    TeamPerformanceMetrics,
    BusinessImpactMetrics,
    AlertFatigueAnalysis,
    MetricType,
    MetricGranularity,
    MetricStatus,
    get_pagerduty_metrics_collector,
    create_pagerduty_metrics_collector
)

__all__ = [
    # Core PagerDuty Integration
    'PagerDutyClient',
    'IncidentSeverity',
    'IncidentStatus',
    'EscalationManager',
    'IntelligentAlertRouter',
    
    # Creator-Specific Classification
    'CreatorIncidentClassifier',
    'CreatorWorkflowStage',
    'IncidentCategory',
    'BusinessImpactLevel',
    'TeamAssignment',
    
    # Revenue Impact Assessment
    'RevenueImpactCalculator',
    'RevenueStreamType',
    'ImpactSeverity',
    'CreatorMetrics',
    'IncidentImpactResult',
    
    # Collaboration Management
    'CollaborationIncidentManager',
    'CollaborationType',
    'StakeholderRole',
    'CollaborationIncident',
    
    # Content Protection
    'ContentProtectionAlerting',
    'ViolationType',
    'ThreatLevel',
    'ProtectionViolation',
    
    # Predictive Intelligence
    'PredictiveIncidentEngine',
    'PredictionType',
    'PredictionConfidence',
    'IncidentPrediction',
    'MetricData',
    
    # Multi-Channel Notifications
    'MultiChannelNotificationSystem',
    'NotificationChannel',
    'NotificationPriority',
    'NotificationMessage',
    
    # Incident Analytics
    'IncidentAnalyticsEngine',
    'AnalyticsType',
    'IncidentMetrics',
    'AnalyticsResult',
    
    # Automated Runbooks
    'RunbookExecutor',
    'ActionType',
    'RunbookDefinition',
    'ExecutionStatus',
    
    # Service Mesh Integration
    'ServiceMeshIntegration',
    'ServiceNode',
    'ServiceDependency',
    'ServiceMeshAlert',
    'TraceSpan',
    'ServiceHealthStatus',
    'TrafficDirection',
    'CircuitBreakerState',
    'get_service_mesh_integration',
    'create_service_mesh_integration',
    
    # External Vendor Alerting
    'ExternalVendorAlerting',
    'VendorEndpoint',
    'VendorHealthCheck',
    'SLAMetrics',
    'VendorAlert',
    'VendorType',
    'ServiceStatus',
    'SLABreachSeverity',
    'get_external_vendor_alerting',
    'create_external_vendor_alerting',
    
    # Compliance Incident Handler
    'ComplianceIncidentHandler',
    'ComplianceIncident',
    'ComplianceRequirement',
    'AuditEntry',
    'ComplianceAlert',
    'ComplianceFramework',
    'ComplianceIncidentSeverity',
    'ComplianceStatus',
    'DataType',
    'get_compliance_incident_handler',
    'create_compliance_incident_handler',
    
    # Crisis Communication Manager
    'CrisisCommunicationManager',
    'CrisisEvent',
    'CrisisMessage',
    'StakeholderGroup',
    'SocialMediaPost',
    'CrisisLevel',
    'CommunicationChannel',
    'StakeholderType',
    'MessageType',
    'get_crisis_communication_manager',
    'create_crisis_communication_manager',
    
    # Incident Lifecycle Tracker
    'IncidentLifecycleTracker',
    'IncidentTimeline',
    'StateTransition',
    'ResourceAllocation',
    'LifecycleMetrics',
    'IncidentState',
    'StateTransitionTrigger',
    'ResourceType',
    'IncidentPriority',
    'get_incident_lifecycle_tracker',
    'create_incident_lifecycle_tracker',
    
    # PagerDuty Metrics Collector
    'PagerDutyMetricsCollector',
    'MetricDefinition',
    'MetricDataPoint',
    'MetricSeries',
    'TeamPerformanceMetrics',
    'BusinessImpactMetrics',
    'AlertFatigueAnalysis',
    'MetricType',
    'MetricGranularity',
    'MetricStatus',
    'get_pagerduty_metrics_collector',
    'create_pagerduty_metrics_collector'
]

# Module metadata
__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__description__ = "Enterprise PagerDuty Integration for Creator Economy Platform"