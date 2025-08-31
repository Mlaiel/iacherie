"""Content Protection Core Module for IA Influencer Agent Platform

This module provides comprehensive content protection services including:
- AI-powered fingerprinting for multi-format content (audio, video, image, text)
- Real-time content monitoring and surveillance
- Automated violation detection and alerts
- DMCA takedown request automation
- Content verification and validation systems
- Revenue tracking and monetization
- Platform crawlers and web surveillance
- Legal automation and document generation
- Advanced analytics and reporting
- Multi-channel notification system

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

WARNING: This code is proprietary and confidential. Unauthorized use, reproduction,
or distribution is strictly prohibited and will result in legal action.
Contact: mlaiel@live.de for licensing inquiries.
"""

from .fingerprint_engine import FingerprintEngine

from .content_monitor import ContentMonitor

from .violation_detector import ViolationDetector

from .protection_manager import ProtectionManager

from .verification_service import VerificationService

from .alert_manager import AlertManager

from .dmca_handler import DMCAHandler

from .evidence_collector import EvidenceCollector

from .revenue_tracker import RevenueTracker

from .platform_crawlers import PlatformCrawler, CrawlerManager
from .legal_automation import LegalAutomation

from .analytics_engine import ProtectionAnalytics

from .notification_system import NotificationManager

__all__ = [
    'FingerprintEngine',
    'ContentMonitor', 
    'ViolationDetector',
    'ProtectionManager',
    'VerificationService',
    'AlertManager',
    'DMCAHandler',
    'EvidenceCollector',
    'RevenueTracker',
    'PlatformCrawler',
    'CrawlerManager',
    'LegalAutomation',
    'ProtectionAnalytics',
    'NotificationManager'
]

__version__ = '2.0.0'
__author__ = 'Fahed Mlaiel'
__email__ = 'mlaiel@live.de'
