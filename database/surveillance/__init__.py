"""Enterprise Surveillance Database Module
=====================================

Advanced surveillance system for multi-format content protection.
Provides real-time monitoring, detection, and alert management.

Author: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All Rights Reserved.

WARNING: This code and concept are protected intellectual property.
Any unauthorized use, copying, or distribution without explicit written 
permission from Fahed Mlaiel (mlaiel@live.de) is strictly prohibited.
"""
from .monitoring_engines import *
from .alert_systems import *
from .analytics_repository import *
from .platform_connectors import *
from .evidence_management import *
from .reporting_systems import *
from .audio_detection_engine import *
from .video_detection_engine import *
from .image_detection_engine import *
from .text_detection_engine import *

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__copyright__ = "© 2025 Fahed Mlaiel. All Rights Reserved."

__all__ = [
    # Monitoring Engines
    "ContentMonitoringEngine",
    "WebCrawlingDetector", 
    "RealTimeMonitor",
    "PerformanceMonitor",
    "BaseMonitoringEngine",
    "MonitoringStatus",
    "ContentType",
    "MonitoringTarget",
    "DetectionResult",
    
    # Detection Engines
    "AudioDetectionEngine",
    "VideoDetectionEngine", 
    "ImageDetectionEngine",
    "TextDetectionEngine",
    "AudioFeatureExtractor",
    "VideoFeatureExtractor",
    "ImageFeatureExtractor", 
    "TextFeatureExtractor",
    "AudioSimilarityCalculator",
    "VideoSimilarityCalculator",
    "ImageSimilarityCalculator",
    "TextSimilarityCalculator",
    "AudioFingerprint",
    "VideoFingerprint",
    "ImageFingerprint",
    "TextFingerprint",
    "AudioMatch",
    "VideoMatch", 
    "ImageMatch",
    "TextMatch",
    
    # Alert Systems
    "AlertManager",
    "NotificationDispatcher",
    "EscalationHandler",
    "AlertRepository",
    "BaseNotificationChannel",
    "EmailNotificationChannel",
    "WebhookNotificationChannel",
    "SlackNotificationChannel",
    "TelegramNotificationChannel",
    "AlertSeverity",
    "AlertStatus",
    "AlertChannel",
    "AlertCategory",
    "AlertRule",
    "Alert",
    "NotificationTemplate",
    
    # Analytics Repository
    "SurveillanceAnalytics",
    "MetricsCollector",
    "TrendAnalyzer",
    "ReportGenerator",
    "AnalyticsEngine",
    "MetricDefinition",
    "AnalyticsQuery",
    "AnalyticsResult",
    
    # Platform Connectors
    "YouTubeConnector",
    "InstagramConnector", 
    "TikTokConnector",
    "TwitterConnector",
    "FacebookConnector",
    "LinkedInConnector",
    "GenericWebConnector",
    "BasePlatformConnector",
    "PlatformSearchResult",
    "PlatformContent",
    
    # Evidence Management
    "EvidenceCollector",
    "EvidenceStorage",
    "EvidenceAnalyzer",
    "LegalDocumentGenerator",
    "EvidenceChain",
    "Evidence",
    "EvidenceType",
    "EvidenceStatus",
    "LegalDocument",
    "DMCAGenerator",
    
    # Reporting Systems
    "ViolationReportGenerator",
    "ComplianceReporter",
    "PerformanceReporter",
    "DashboardMetrics",
    "ReportScheduler",
    "ReportTemplate",
    "Report",
    "ReportType",
    "ReportFormat",
    "ReportDelivery",
    
    # Utility Functions
    "get_alert_manager",
    "get_notification_dispatcher",
    "get_platform_connector",
    "get_evidence_collector"
]

# Module metadata
MODULE_INFO = {
    "name": "Surveillance Database Module",
    "description": "Advanced content surveillance and protection system",
    "version": __version__,
    "author": __author__,
    "email": __email__,
    "copyright": __copyright__,
    "license": "Proprietary - All Rights Reserved",
    "features": [
        "Multi-format content detection (audio, video, image, text)",
        "Real-time monitoring and alerts",
        "Advanced fingerprinting algorithms", 
        "Cross-platform surveillance",
        "Automated evidence collection",
        "Legal document generation",
        "Performance analytics and reporting",
        "Escalation management",
        "Multi-channel notifications"
    ],
    "supported_platforms": [
        "YouTube", "Instagram", "TikTok", "Twitter", "Facebook", 
        "LinkedIn", "Spotify", "SoundCloud", "Generic Web"
    ],
    "detection_methods": [
        "Perceptual hashing", "Feature matching", "Semantic analysis",
        "Content fingerprinting", "Behavioral pattern detection"
    ]
}
    "EvidenceCollector",
    "ScreenshotCapture",
    "MetadataExtractor",
    "EvidenceStorage",
    
    # Reporting Systems
    "ComplianceReporter",
    "ViolationReporter",
    "PerformanceReporter",
    "DashboardReporter"
]

from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

# Version du module
__version__ = "1.0.0"

# Modules exportés
__all__ = [
    "surveillance_jobs",
    "detection_alerts",
    "monitoring_targets",
    "violation_reports",
    "automated_responses"
]

def get_module_info() -> Dict[str, Any]:
    """    Retourne les informations du module Surveillance.
    
    Returns:
        Dict[str, Any]: Informations du module
    """    return {
        "name": "Surveillance Database",
        "version": __version__,
        "author": "Fahed Mlaiel",
        "email": "mlaiel@live.de",
        "description": "Base de données surveillance de contenu",
        "modules": __all__
    }
