"""
Business Platform Module - Core Platform Management System

This module handles the core platform orchestration, multi-format content processing,
AI-powered protection, and cross-platform distribution for the IA Influencer Agent ecosystem.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.
"""

from .platform_orchestrator import PlatformOrchestrator
from .content_processor import ContentProcessor
from .distribution_manager import DistributionManager
from .platform_analytics import PlatformAnalytics
from .integration_hub import IntegrationHub
from .platform_security import PlatformSecurity
from .monetization_controller import MonetizationController
from .collaboration_engine import CollaborationEngine
from .notification_dispatcher import NotificationDispatcher
from .quality_assurance import QualityAssurance

__all__ = [
    'PlatformOrchestrator',
    'ContentProcessor',
    'DistributionManager', 
    'PlatformAnalytics',
    'IntegrationHub',
    'PlatformSecurity',
    'MonetizationController',
    'CollaborationEngine',
    'NotificationDispatcher',
    'QualityAssurance'
]

__version__ = "2.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
