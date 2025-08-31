"""🚨 Intelligent Alert System for Ainflue Platform
===============================================

Comprehensive intelligent alert management system providing:
- Business Alerts (Revenue, User Experience)
- Technical Alerts (Infrastructure, Security)
- AI Alerts (Model Drift, Accuracy Degradation)

The system provides unified alert coordination, intelligent correlation,
and automated escalation across all platform components.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""# Core alert management
from .intelligent_alert_manager import (
    IntelligentAlertManager,
    AlertCategory,
    AlertSeverity,
    AlertType,
    AlertRule,
    IntelligentAlert
)

# Business alerts
from .business_alerts import (
    BusinessAlertManager,
    BusinessMetrics,
    BusinessMetric
)

# Technical alerts
from .technical_alerts import (
    TechnicalAlertManager,
    TechnicalMetrics,
    SecurityEvent,
    TechnicalMetric,
    SecurityThreatLevel
)

# AI/ML alerts
from .ai_alerts import (
    AIAlertManager,
    ModelMetrics,
    ModelBaseline,
    DriftDetectionResult,
    AIModelType,
    DriftType,
    ModelHealth
)

# Unified coordinator
from .alert_coordinator import (
    AlertCoordinator,
    UnifiedAlertSummary,
    SystemHealthStatus,
    alert_coordinator  # Global instance
)

# Existing revenue anomaly detection (for compatibility)
try:
    from .revenue_anomaly import (
        RevenueAnomalyDetector,
        RevenueAlert,
        AnomalyType
    )
except ImportError:
    # Fallback if existing module not available
    pass

__version__ = "1.0.0"

__all__ = [
    # Core classes
    "IntelligentAlertManager",
    "AlertCategory",
    "AlertSeverity", 
    "AlertType",
    "AlertRule",
    "IntelligentAlert",
    
    # Business alerts
    "BusinessAlertManager",
    "BusinessMetrics",
    "BusinessMetric",
    
    # Technical alerts  
    "TechnicalAlertManager",
    "TechnicalMetrics",
    "SecurityEvent",
    "TechnicalMetric",
    "SecurityThreatLevel",
    
    # AI/ML alerts
    "AIAlertManager",
    "ModelMetrics",
    "ModelBaseline", 
    "DriftDetectionResult",
    "AIModelType",
    "DriftType",
    "ModelHealth",
    
    # Unified coordination
    "AlertCoordinator",
    "UnifiedAlertSummary",
    "SystemHealthStatus",
    "alert_coordinator",
]


def create_alert_system() -> AlertCoordinator:
    """    Create and configure a complete intelligent alert system
    
    Returns:
        AlertCoordinator: Fully configured alert coordinator
    """    return AlertCoordinator()


def get_alert_system() -> AlertCoordinator:
    """    Get the global alert coordinator instance
    
    Returns:
        AlertCoordinator: Global alert coordinator
    """    return alert_coordinator


# Quick access functions
async def evaluate_business_metrics(metrics: BusinessMetrics):
    """Quick access to business metrics evaluation"""    return await alert_coordinator.evaluate_all_metrics(business_metrics=metrics)


async def evaluate_technical_metrics(metrics: TechnicalMetrics):
    """Quick access to technical metrics evaluation"""    return await alert_coordinator.evaluate_all_metrics(technical_metrics=metrics)


async def evaluate_ai_metrics(metrics: list):
    """Quick access to AI metrics evaluation"""    return await alert_coordinator.evaluate_all_metrics(ai_metrics=metrics)


async def get_system_health():
    """Quick access to system health status"""    return await alert_coordinator.get_comprehensive_status()


# Module initialization
import logging
logger = logging.getLogger(__name__)
logger.info("Intelligent Alert System initialized - Ready for comprehensive monitoring")