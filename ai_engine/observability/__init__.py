"""Observability Module - Complete Enterprise Observability Suite

Comprehensive monitoring, analytics, reporting, and predictive capabilities
for the IA Influencer Agent platform with advanced AI-powered insights.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

  AVERTISSEMENT LÉGAL / LEGAL WARNING 
Ce code est la propriété intellectuelle exclusive de Fahed Mlaiel.
This code is the exclusive intellectual property of Fahed Mlaiel.
Toute utilisation non autorisée est strictement interdite.
Any unauthorized use is strictly prohibited.
"""
# Essential Analytics Components
from .analytics import (
    RealTimeAnalytics,
    HistoricalAnalytics, 
    PredictiveAnalytics,
    ContentAnalytics,
    UserAnalytics,
    PerformanceAnalytics,
    AnalyticsTimeframe,
    AnalyticsMetricType,
    AnalyticsDataPoint,
    AnalyticsResult
)

# Business Process Monitoring Components (New)
from .business_process_monitoring import (
    ContentType,
    CreatorType,
    ProcessStage,
    ProcessStatus,
    DistributionPlatform,
    ContentProcessingMetric,
    BusinessProcessInsight,
    ContentProcessingMonitor,
    CollaborationMonitor,
    MonetizationMonitor,
    BusinessProcessOrchestrator
)

# Advanced Analytics Components (integrated in analytics.py)
# All advanced analytics features are available through the main analytics module

# Enterprise Reporting Components
from .enterprise_reporting import (
    ReportType,
    ReportFormat,
    ReportFrequency,
    KPICategory,
    KPI,
    ReportTemplate,
    VisualizationEngine,
    ReportGenerator,
    AutomatedReportingEngine
)

# Intelligent Monitoring Components
from .intelligent_monitoring import (
    AlertSeverity,
    MonitoringScope,
    PredictionType,
    IncidentStatus,
    MonitoringMetric,
    PredictiveAlert,
    Incident,
    AnomalyDetector,
    PredictiveEngine,
    IncidentManager,
    IntelligentMonitoringSystem
)

# Essential Visualization Components  
from .visualization import (
    VisualizationEngine as BaseVisualizationEngine,
    BusinessVisualization,
    TechnicalVisualization,
    VisualizationResult
)

# Essential Dashboard Components
from .dashboards import (
    Dashboard,
    DashboardEngine, 
    DashboardTemplates,
    DashboardType
)

# Essential Quality Components
from .quality import (
    QualityAssuranceEngine,
    BaseQualityTest,
    QualityMetric,
    QualityMetricType
)

# Essential Monitoring Components
from .monitoring import (
    SystemMonitor,
    PerformanceMonitor,
    ResourceMonitor
)

# Essential Metrics Components
from .metrics import (
    MetricsCollector,
    BusinessMetrics,
    TechnicalMetrics,
    MetricsAggregator,
    MetricsAnalyzer,
    CustomMetrics
)

# Essential Logging Components
from .observability_logging import (
    StructuredLogger,
    SecurityLogger,
    AuditLogger,
    ComplianceLogger
)

# Essential Tracing Components
from .tracing import (
    DistributedTracer,
    PerformanceTracer,
    AIOperationTracer
)

# Essential Health Components
from .health import (
    HealthMonitor,
    BaseHealthCheck,
    DatabaseHealthCheck,
    AIModelHealthCheck,
    SystemResourceHealthCheck,
    NetworkHealthCheck,
    HealthStatus,
    HealthCheckResult
)

# Essential Alerting Components
from .alerting import (
    AlertManager,
    AlertEvaluator,
    AlertRule,
    IntelligentAlerting,
    StandardAlertRules
)

# AI Observability Components  
from .ai_observability import (
    AIObservabilityManager,
    AIModelMonitor,
    AgentPerformanceTracker,
    WorkflowAnalytics,
    MLPipelineMonitor,
    ContentProtectionMonitor,
    ModelType,
    ModelFramework,
    ModelStatus,
    DriftType,
    BiasType,
    ModelMetrics,
    DriftDetectionResult,
    BiasDetectionResult,
    ModelExplainabilityResult
)

__version__ = "3.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"

# Export comprehensive classes for easy import
__all__ = [
    # Core Analytics
    "RealTimeAnalytics",
    "HistoricalAnalytics", 
    "PredictiveAnalytics",
    "ContentAnalytics",
    "UserAnalytics",
    "PerformanceAnalytics",
    "AnalyticsTimeframe",
    "AnalyticsMetricType",
    
    # Advanced Analytics
    "BusinessMetricType",
    "ContentCategory", 
    "UserSegmentType",
    "BusinessInsight",
    "PredictiveModel",
    "ContentPerformanceAnalyzer",
    "UserBehaviorAnalytics",
    "ROIOptimizer",
    "AdvancedAnalyticsManager",
    
    # Enterprise Reporting
    "ReportType",
    "ReportFormat",
    "ReportFrequency",
    "KPICategory",
    "KPI",
    "ReportTemplate",
    "VisualizationEngine",
    "ReportGenerator",
    "AutomatedReportingEngine",
    
    # Intelligent Monitoring
    "AlertSeverity",
    "MonitoringScope",
    "PredictionType", 
    "IncidentStatus",
    "MonitoringMetric",
    "PredictiveAlert",
    "Incident",
    "AnomalyDetector",
    "PredictiveEngine",
    "IncidentManager",
    "IntelligentMonitoringSystem",
    
    # Visualization
    "BaseVisualizationEngine",
    "BusinessVisualization", 
    "TechnicalVisualization",
    "VisualizationResult",
    
    # Dashboards
    "Dashboard",
    "DashboardEngine",
    "DashboardTemplates",
    "DashboardType",
    
    # Quality Assurance
    "QualityAssuranceEngine",
    "BaseQualityTest",
    "QualityMetric",
    "QualityMetricType",
    
    # System Monitoring
    "SystemMonitor",
    "PerformanceMonitor",
    "ResourceMonitor",
    
    # Metrics Collection
    "MetricsCollector",
    "BusinessMetrics", 
    "TechnicalMetrics",
    "MetricsAggregator",
    "MetricsAnalyzer",
    "CustomMetrics",
    
    # Structured Logging
    "StructuredLogger",
    "SecurityLogger",
    "AuditLogger",
    "ComplianceLogger",
    
    # Distributed Tracing
    "DistributedTracer",
    "PerformanceTracer",
    "AIOperationTracer",
    
    # Health Monitoring
    "HealthMonitor",
    "BaseHealthCheck",
    "DatabaseHealthCheck",
    "AIModelHealthCheck",
    "SystemResourceHealthCheck",
    "NetworkHealthCheck",
    "HealthStatus",
    "HealthCheckResult",
    
    # Alert Management
    "AlertManager",
    "AlertEvaluator",
    "AlertRule",
    "IntelligentAlerting",
    "StandardAlertRules",
    
    # AI Model Observability
    "AIObservabilityManager",
    "AIModelMonitor",
    "AgentPerformanceTracker",
    "WorkflowAnalytics",
    "MLPipelineMonitor",
    "ContentProtectionMonitor",
    "ModelType",
    "ModelFramework", 
    "ModelStatus",
    "DriftType",
    "BiasType",
    "ModelMetrics",
    "DriftDetectionResult",
    "BiasDetectionResult",
    "ModelExplainabilityResult"
]

# Module metadata
__module_info__ = {
    "name": "AI Observability Suite",
    "description": "Enterprise-grade observability, monitoring, and analytics platform",
    "version": __version__,
    "author": __author__,
    "email": __email__,
    "capabilities": [
        "Real-time monitoring and alerting",
        "Predictive analytics and anomaly detection", 
        "Advanced business intelligence reporting",
        "AI model performance tracking",
        "Automated incident management",
        "Content performance optimization",
        "User behavior analytics",
        "ROI optimization and forecasting",
        "Compliance and audit logging",
        "Multi-dimensional data visualization"
    ],
    "integrations": [
        "Machine Learning frameworks (TensorFlow, PyTorch, Scikit-learn)",
        "Visualization libraries (Plotly, Matplotlib, Seaborn)",
        "Database systems (PostgreSQL, MongoDB, Redis)",
        "Cloud platforms (AWS, Azure, GCP)",
        "Monitoring tools (Prometheus, Grafana)",
        "Business intelligence platforms"
    ],
    "business_logic_flow": [
        "Content Creator Upload → AI Processing → Protection Analysis",
        "User Engagement → Behavior Analytics → Personalization",
        "Performance Monitoring → Predictive Analysis → Optimization",
        "Revenue Tracking → ROI Analysis → Strategic Planning",
        "Anomaly Detection → Incident Management → Resolution"
    ]
}
from .monitoring import (
    SystemMonitor,
    PerformanceMonitor,
    ResourceMonitor
)

# Essential Metrics Components
from .metrics import (
    MetricsCollector,
    BusinessMetrics,
    TechnicalMetrics,
    MetricsAggregator,
    MetricsAnalyzer,
    CustomMetrics
)

# Essential Logging Components
from .observability_logging import (
    StructuredLogger,
    SecurityLogger,
    AuditLogger,
    ComplianceLogger
)

# Essential Tracing Components
from .tracing import (
    DistributedTracer,
    PerformanceTracer,
    AIOperationTracer
)

# Essential Health Components
from .health import (
    HealthMonitor,
    BaseHealthCheck,
    DatabaseHealthCheck,
    AIModelHealthCheck,
    SystemResourceHealthCheck,
    NetworkHealthCheck,
    HealthStatus,
    HealthCheckResult
)

# Essential Alerting Components
from .alerting import (
    AlertManager,
    AlertEvaluator,
    AlertRule,
    IntelligentAlerting,
    StandardAlertRules
)

# Essential AI Observability Components  
# from .ai_observability import (
#     AIObservabilityManager,
#     AIModelMonitor,
#     AgentPerformanceTracker,
#     WorkflowAnalytics,
#     MLPipelineMonitor,
#     ContentProtectionMonitor
# )

__version__ = "2.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"

# Export essential classes for easy import
__all__ = [
    # Analytics
    "RealTimeAnalytics",
    "HistoricalAnalytics", 
    "PredictiveAnalytics",
    "ContentAnalytics",
    "UserAnalytics",
    "PerformanceAnalytics",
    
    # Visualization
    "VisualizationEngine",
    "BusinessVisualization", 
    "TechnicalVisualization",
    
    # Dashboards
    "Dashboard",
    "DashboardEngine",
    "DashboardTemplates",
    
    # Quality
    "QualityAssuranceEngine",
    "BaseQualityTest",
    "QualityMetric",
    
    # Monitoring
    "SystemMonitor",
    "PerformanceMonitor",
    "ResourceMonitor",
    
    # Metrics
    "MetricsCollector",
    "BusinessMetrics", 
    "TechnicalMetrics",
    
    # Logging
    "StructuredLogger",
    "SecurityLogger",
    "AuditLogger",
    
    # Tracing
    "DistributedTracer",
    "PerformanceTracer",
    "AIOperationTracer",
    
    # Health
    "HealthMonitor",
    "BaseHealthCheck",
    "DatabaseHealthCheck",
    
    # Alerting
    "AlertManager",
    "AlertEvaluator",
    "AlertRule",
    
    # AI Observability
    "AIObservabilityManager",
    "AIModelMonitor",
    "AgentPerformanceTracker"
]
