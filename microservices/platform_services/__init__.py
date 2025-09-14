"""
Ainflue Platform Services Module
Platform Integration & External API Management

This module provides enterprise-grade platform integration services for
the Ainflue ecosystem, handling 65+ external platforms including social media,
music streaming, creator economy platforms, and more.

Architecture: Platform Services (18 services)
- Multi-platform authentication and synchronization
- Real-time data synchronization across platforms
- Webhook management and event streaming
- Platform-specific optimization and compliance
- Unified API abstraction layer

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from .platform_connector_service import PlatformConnectorService
from .platform_authentication_service import PlatformAuthenticationService
from .platform_sync_service import PlatformSyncService
from .platform_monitoring_service import PlatformMonitoringService
from .platform_optimization_service import PlatformOptimizationService
from .platform_reporting_service import PlatformReportingService
from .platform_compliance_service import PlatformComplianceService
from .platform_webhook_service import PlatformWebhookService
from .social_media_service import SocialMediaService

__all__ = [
    'PlatformConnectorService',
    'PlatformAuthenticationService', 
    'PlatformSyncService',
    'PlatformMonitoringService',
    'PlatformOptimizationService',
    'PlatformReportingService',
    'PlatformComplianceService',
    'PlatformWebhookService',
    'SocialMediaService'
]

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"