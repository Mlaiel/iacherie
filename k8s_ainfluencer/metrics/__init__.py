"""IA Influencer Agent - Metrics Deployment Module
Enterprise metrics collection and monitoring deployment

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved - Unauthorized use prohibited

⚠️  AVERTISSEMENT LÉGAL STRICT ⚠️
Ce code est la propriété intellectuelle exclusive de Fahed Mlaiel.
Toute utilisation, copie, modification ou distribution sans autorisation 
écrite explicite est strictement interdite et fera l'objet de poursuites 
judiciaires selon la loi allemande et internationale.

Contact autorisé: mlaiel@live.de

Équipe de développement:
- Lead Developer IA & Architecte: Fahed Mlaiel
- Backend Senior Engineer: Fahed Mlaiel  
- ML Engineer: Fahed Mlaiel
- DBA & Data Engineer: Fahed Mlaiel
- DevOps Engineer: Fahed Mlaiel
- Security Specialist: Fahed Mlaiel
- Audio Processing Expert: Fahed Mlaiel
"""
__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"

from .prometheus_manager import PrometheusManager

from .grafana_manager import GrafanaManager

from .metrics_collector import MetricsCollector

from .alert_manager import AlertManager

from .performance_analytics import PerformanceAnalytics

from .dashboard import MetricsDashboard

from .business_intelligence import BusinessIntelligence

from .config import get_metrics_config, MetricsConfiguration, MetricsEnvironment
from .business_events_collector import BusinessEventsCollector, BusinessEvent, BusinessEventType
from .content_protection_metrics import ContentProtectionMetricsCollector, ContentType, FingerprintAlgorithm
from .revenue_metrics_collector import RevenueMetricsCollector, RevenueSource, Platform, Currency
from .infrastructure_metrics import InfrastructureMetricsCollector, ServiceType, ResourceType
from .ai_model_metrics import AIModelMetricsCollector, ModelType, ModelStage, InferenceStatus

# New advanced metrics collectors according to business requirements
from .web_surveillance_metrics import (
    WebSurveillanceMetricsCollector, 
    CrawlerPlatform, 
    SurveillanceStatus, 
    ThreatLevel,
    CrawlerSession,
    ContentMatch
)
from .licensing_automation_metrics import (
    LicensingAutomationMetricsCollector,
    LicenseType,
    LicenseStatus,
    NegotiationPhase,
    ComplianceLevel,
    LicenseTransaction,
    RightsNegotiation
)
from .fingerprinting_performance_metrics import (
    FingerprintingPerformanceMetricsCollector,
    FingerprintAlgorithm as FingerprintAlgorithmPerf,
    ContentType as ContentTypePerf,
    ProcessingStage,
    MatchQuality,
    FingerprintingJob,
    MatchResult
)
from .platform_integration_metrics import (
    PlatformIntegrationMetricsCollector,
    Platform as IntegrationPlatform,
    IntegrationType,
    APIEndpointType,
    ConnectionStatus,
    PlatformConnection,
    APICall
)

# Central deployment manager
from .index import (
    MetricsDeploymentManager,
    metrics_deployment_context,
    get_metrics_deployment_manager,
    initialize_metrics_deployment,
    start_metrics_deployment,
    stop_metrics_deployment
)

__all__ = [
    # Core managers
    "PrometheusManager",
    "GrafanaManager", 
    "MetricsCollector",
    "AlertManager",
    "PerformanceAnalytics",
    "MetricsDashboard",
    "BusinessIntelligence",
    
    # Configuration
    "get_metrics_config",
    "MetricsConfiguration", 
    "MetricsEnvironment",
    
    # Specialized collectors
    "BusinessEventsCollector",
    "ContentProtectionMetricsCollector",
    "RevenueMetricsCollector", 
    "InfrastructureMetricsCollector",
    "AIModelMetricsCollector",
    
    # Advanced enterprise collectors (new)
    "WebSurveillanceMetricsCollector",
    "LicensingAutomationMetricsCollector",
    "FingerprintingPerformanceMetricsCollector",
    "PlatformIntegrationMetricsCollector",
    
    # Data types and enums - Core
    "BusinessEvent",
    "BusinessEventType",
    "ContentType",
    "FingerprintAlgorithm",
    "RevenueSource",
    "Platform",
    "Currency",
    "ServiceType",
    "ResourceType",
    "ModelType",
    "ModelStage",
    "InferenceStatus",
    
    # Data types and enums - Advanced
    "CrawlerPlatform",
    "SurveillanceStatus",
    "ThreatLevel",
    "CrawlerSession",
    "ContentMatch",
    "LicenseType",
    "LicenseStatus",
    "NegotiationPhase",
    "ComplianceLevel",
    "LicenseTransaction",
    "RightsNegotiation",
    "FingerprintAlgorithmPerf",
    "ContentTypePerf",
    "ProcessingStage",
    "MatchQuality",
    "FingerprintingJob",
    "MatchResult",
    "IntegrationPlatform",
    "IntegrationType",
    "APIEndpointType",
    "ConnectionStatus",
    "PlatformConnection",
    "APICall",
    
    # Central deployment management
    "MetricsDeploymentManager",
    "metrics_deployment_context",
    "get_metrics_deployment_manager",
    "initialize_metrics_deployment",
    "start_metrics_deployment",
    "stop_metrics_deployment"
]
