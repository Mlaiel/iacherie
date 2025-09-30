"""
Ainflue Platform - Enterprise Notifications System
==================================================

A comprehensive, AI-powered notification system for the Ainflue platform.
Supports multi-channel delivery, intelligent personalization, and enterprise-grade scalability.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

WARNING: This code is proprietary and confidential. Unauthorized use, copying, or distribution
is strictly prohibited and will result in legal action. All intellectual property rights
belong exclusively to Fahed Mlaiel.
"""

# Core notification modules that are working
from .config import settings, MetricsCollector, metrics
from .push import PushNotifier, PushMessage, PushContent, PushDeliveryResult, PushPlatform, NotificationPriority

# Notification orchestrators (all modules)
from .analytics import AnalyticsNotificationsOrchestrator, AnalyticsNotificationContext, NotificationPriority as AnalyticsNotificationPriority, AnalyticsNotificationChannel
from .collaboration import CollaborationNotificationsOrchestrator
from .gamification import GamificationNotificationsOrchestrator
from .monetization import MonetizationNotificationsOrchestrator
from .security import SecurityNotificationOrchestrator
from .distribution import DistributionNotificationOrchestrator

__version__ = "3.1.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"

__all__ = [
    # Configuration
    "settings", "MetricsCollector", "metrics",
    
    # Core notifiers (working modules)
    "PushNotifier", "PushMessage", "PushContent", "PushDeliveryResult", "PushPlatform", "NotificationPriority",
    
    # Orchestrators (all modules working)
    "AnalyticsNotificationsOrchestrator", "AnalyticsNotificationContext", "AnalyticsNotificationPriority", "AnalyticsNotificationChannel",
    "CollaborationNotificationsOrchestrator",
    "GamificationNotificationsOrchestrator", 
    "MonetizationNotificationsOrchestrator",
    "SecurityNotificationOrchestrator",
    "DistributionNotificationOrchestrator",
    
    # Metadata
    "__version__", "__author__", "__email__"
]

# Initialize logging
import logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)
logger.info(f"Ainflue Notifications System v{__version__} initialized successfully")
logger.info(f"6 notification orchestrators loaded: Analytics, Collaboration, Gamification, Monetization, Security, Distribution")
logger.info(f"AI Personalization: {'Enabled' if settings.ai_personalization_enabled else 'Disabled'}")
logger.info(f"Metrics Collection: {'Enabled' if settings.metrics_enabled else 'Disabled'}")