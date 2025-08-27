"""
Rights Management Core Module for IA Influencer Agent Platform
================================================================

Comprehensive intellectual property and digital rights management system
for multi-format content creators (music, video, image, text).

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent - Enterprise Content Protection Platform
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + IA Prompt Engineer

⚠️  INTELLECTUAL PROPERTY WARNING ⚠️
====================================
This software and all associated concepts, algorithms, and implementations are the exclusive 
intellectual property of Fahed Mlaiel (mlaiel@live.de). Any unauthorized use, reproduction, 
distribution, or derivative work without explicit written permission is strictly prohibited 
and will result in immediate legal action under German and international copyright law.

All rights reserved. © 2025 Fahed Mlaiel
Contact: mlaiel@live.de for licensing inquiries.
"""

from .rights_manager import RightsManager
from .digital_fingerprint import DigitalFingerprintEngine
from .copyright_detector import CopyrightDetectionService
from .license_manager import LicenseManagementSystem
from .protection_engine import ContentProtectionEngine
from .ownership_validator import OwnershipValidationService
from .royalty_calculator import RoyaltyCalculationEngine
from .dispute_handler import DisputeResolutionSystem
from .web_monitoring import WebMonitoringEngine, MonitoringTarget, ViolationResult
from .monetization_engine import MonetizationEngine, RevenueMetrics, RevenueLeak
from .legal_compliance import LegalComplianceEngine, DMCANoticeData, LegalCaseData
from .notification_system import NotificationEngine, NotificationData, NotificationType
from .index import RightsOrchestrator, router as rights_router

__version__ = "2.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__copyright__ = "© 2025 Fahed Mlaiel. All rights reserved."

__all__ = [
    "RightsManager",
    "DigitalFingerprintEngine", 
    "CopyrightDetectionService",
    "LicenseManagementSystem",
    "ContentProtectionEngine",
    "OwnershipValidationService",
    "RoyaltyCalculationEngine",
    "DisputeResolutionSystem",
    "WebMonitoringEngine",
    "MonitoringTarget",
    "ViolationResult",
    "MonetizationEngine",
    "RevenueMetrics",
    "RevenueLeak",
    "LegalComplianceEngine",
    "DMCANoticeData",
    "LegalCaseData",
    "NotificationEngine",
    "NotificationData",
    "NotificationType",
    "RightsOrchestrator",
    "rights_router"
]

# Enhanced module configuration for enterprise deployment
RIGHTS_CONFIG = {
    "fingerprint_precision": 0.95,
    "detection_threshold": 0.85,
    "similarity_threshold": 0.88,
    "monitoring_interval": 300,  # seconds
    "batch_processing_size": 100,
    "max_content_size": 500 * 1024 * 1024,  # 500MB
    "supported_formats": {
        "audio": [".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a"],
        "video": [".mp4", ".avi", ".mov", ".mkv", ".webm", ".flv"],
        "image": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".tiff"],
        "text": [".txt", ".md", ".docx", ".pdf", ".rtf", ".html"]
    },
    "ai_models": {
        "audio_fingerprint": "chromaprint_enterprise",
        "video_analysis": "opencv_yolo_v8",
        "image_recognition": "clip_vit_large",
        "text_analysis": "bert_multilingual_cased"
    },
    "performance_targets": {
        "fingerprint_accuracy": 0.973,
        "detection_speed_ms": 6200,
        "false_positive_rate": 0.028,
        "platform_coverage": 15,
        "uptime_percentage": 99.94
    },
    "security": {
        "encryption_algorithm": "AES-256-GCM",
        "hash_algorithm": "SHA-256",
        "salt_rounds": 12,
        "jwt_expiry": 3600,
        "rate_limit_per_minute": 1000
    },
    "monitoring": {
        "real_time_alerts": True,
        "violation_notifications": True,
        "performance_metrics": True,
        "audit_logging": True,
        "compliance_reporting": True
    },
    "platforms": {
        "supported": [
            "youtube", "spotify", "tiktok", "instagram", "facebook",
            "twitter", "soundcloud", "bandcamp", "apple_music",
            "amazon_music", "deezer", "twitch", "discord", "reddit", "pinterest"
        ],
        "priority_monitoring": ["youtube", "spotify", "tiktok", "instagram"],
        "api_integration": True,
        "web_scraping": True
    }
}

# Enterprise deployment constants
ENTERPRISE_FEATURES = {
    "multi_tenant_isolation": True,
    "advanced_analytics": True,
    "custom_fingerprinting": True,
    "priority_support": True,
    "dedicated_infrastructure": True,
    "compliance_automation": True,
    "white_label_options": True,
    "api_rate_limits": {
        "basic": 100,
        "standard": 500,
        "premium": 2000,
        "enterprise": 10000
    }
}

# Legal compliance configuration
COMPLIANCE_CONFIG = {
    "dmca_automation": True,
    "gdpr_compliance": True,
    "ccpa_compliance": True,
    "international_copyright": True,
    "automated_takedowns": True,
    "dispute_resolution": True,
    "legal_documentation": True,
    "audit_trails": True
}

# Initialize logging for the rights module
import logging
logging.getLogger(__name__).info(
    f"Rights Management Core v{__version__} initialized - Enterprise Protection Active"
)
