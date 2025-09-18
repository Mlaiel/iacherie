"""SEO Monitoring Package
Enterprise-grade real-time SEO performance monitoring, alerting, and anomaly detection.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  LEGAL WARNING:
==========================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
ALL RIGHTS RESERVED

🚨 INTELLECTUAL PROPERTY PROTECTION:
- Proprietary code of Fahed Mlaiel
- Commercial use PROHIBITED without written authorization
- Reverse engineering STRICTLY FORBIDDEN
- Distribution PROHIBITED without explicit license
- Violation = Automatic legal prosecution

🏢 ENTERPRISE USAGE:
- Enterprise license available on request
- Technical support included with license
- Maintenance and updates assured
- Technical team training provided
"""

from .real_time_seo_monitor import RealTimeSEOMonitor
from .performance_dashboard_engine import (
    PerformanceDashboardEngine,
    DashboardType,
    ChartType,
    DashboardWidget,
    DashboardLayout
)
from .alert_management_system import (
    AlertManagementSystem,
    AlertRule,
    Alert,
    NotificationConfig,
    EscalationRule,
    AlertSeverity,
    AlertStatus,
    NotificationChannel,
    EscalationAction
)
from .anomaly_detection_engine import (
    AnomalyDetectionEngine,
    AnomalyDetection,
    DetectionModel,
    BehavioralPattern,
    MetricDataPoint,
    AnomalyType,
    AnomalySeverity,
    DetectionMethod,
    AnomalyStatus
)

__all__ = [
    # Core Monitoring
    "RealTimeSEOMonitor",
    
    # Performance Dashboard Engine
    "PerformanceDashboardEngine",
    "DashboardType",
    "ChartType", 
    "DashboardWidget",
    "DashboardLayout",
    
    # Alert Management System
    "AlertManagementSystem",
    "AlertRule",
    "Alert",
    "NotificationConfig", 
    "EscalationRule",
    "AlertSeverity",
    "AlertStatus",
    "NotificationChannel",
    "EscalationAction",
    
    # Anomaly Detection Engine
    "AnomalyDetectionEngine",
    "AnomalyDetection",
    "DetectionModel",
    "BehavioralPattern",
    "MetricDataPoint",
    "AnomalyType",
    "AnomalySeverity", 
    "DetectionMethod",
    "AnomalyStatus"
]