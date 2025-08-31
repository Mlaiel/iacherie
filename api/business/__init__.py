"""Business services package for IA Influencer Agent platform.

This package contains all business logic services for multi-format content 
creation, protection, and monetization.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution 
of this code without explicit written permission from Fahed Mlaiel is strictly prohibited.

WARNING: This code is proprietary intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, modification, or distribution is strictly
prohibited and will result in legal action.
Contact: mlaiel@live.de for licensing inquiries.
"""
from .user_service import UserService
from .content_service import ContentService
from .ai_processing_service import AIProcessingService
from .protection_service import ProtectionService
from .collaboration_service import CollaborationService
from .matching_service import MatchingService
from .notification_service import NotificationService
from .monetization_service import MonetizationService
from .analytics_service import AnalyticsService
from .seo_service import SEOService
from .distribution_service import DistributionService
from .vector_search_service import VectorSearchService, get_vector_search_service

# Service registry and orchestrator
from .index import (
    BusinessServiceRegistry,
    BusinessServiceOrchestrator,
    service_registry,
    service_orchestrator,
    get_user_service,
    get_content_service,
    get_ai_processing_service,
    get_protection_service,
    get_collaboration_service,
    get_matching_service,
    get_notification_service,
    get_monetization_service,
    get_analytics_service,
    get_seo_service,
    get_distribution_service,
    get_service_orchestrator
)

__all__ = [
    # Core services
    "UserService",
    "ContentService", 
    "AIProcessingService",
    "ProtectionService",
    "CollaborationService",
    "MatchingService",
    "NotificationService",
    "MonetizationService",
    "AnalyticsService",
    "SEOService", 
    "DistributionService",
    "VectorSearchService",
    "get_vector_search_service",
    
    # Service management
    "BusinessServiceRegistry",
    "BusinessServiceOrchestrator",
    "service_registry",
    "service_orchestrator",
    
    # Service factory functions
    "get_user_service",
    "get_content_service",
    "get_ai_processing_service",
    "get_protection_service",
    "get_collaboration_service",
    "get_matching_service",
    "get_notification_service",
    "get_monetization_service",
    "get_analytics_service",
    "get_seo_service",
    "get_distribution_service",
    "get_service_orchestrator"
]

# Version and metadata
__version__ = "2.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__license__ = "Proprietary - All Rights Reserved"

# Service initialization helper
async def initialize_business_services():
    """Initialize all business services."""    await service_registry.initialize_services()

# Service shutdown helper  
async def shutdown_business_services():
    """Shutdown all business services gracefully."""    await service_registry.shutdown_services()

# Health check helper
def get_business_services_health():
    """Get health status of all business services."""


    return service_registry.get_service_health()

# Metrics helper
def get_business_services_metrics():
    """Get performance metrics for all business services."""


    return service_registry.get_service_metrics()
