"""Platform Services Index - IA Influencer Agent Platform
Main entry point for platform-level services

Author: Fahed Mlaiel <mlaiel@live.de>
WARNING: This code is protected by copyright. Any unauthorized use, reproduction,
or distribution without written permission from Fahed Mlaiel is strictly prohibited.
"""# Platform services
from .analytics import AnalyticsService, MetricsCollector, ReportingEngine
from .collaboration_matching import CollaborationMatchingService, PartnerFinder, CompatibilityEngine
from .content_ingestion import ContentIngestionService, MediaProcessor, ContentValidator
from .distribution import DistributionService, PlatformManager, ContentSynchronizer
from .monetization import MonetizationService, RevenueOptimizer, PaymentGateway
from .rights_protection import RightsProtectionService, CopyrightValidator, ViolationDetector
from .seo_optimizer import SEOOptimizerService, ContentOptimizer, KeywordAnalyzer

# Service registry and coordination
from .registry import ServiceRegistry, ServiceHealthMonitor
from .coordinator import PlatformCoordinator, ServiceOrchestrator


def initialize_platform_services(business_services, core_services):
    """
    Initialize all platform services
    
    Args:
        business_services: Business logic services
        core_services: Core infrastructure services
        
    Returns:
        dict: Initialized platform services
    """
    services = {
        'analytics': AnalyticsService(core_services),
        'collaboration_matching': CollaborationMatchingService(business_services, core_services),
        'content_ingestion': ContentIngestionService(business_services, core_services),
        'distribution': DistributionService(business_services, core_services),
        'monetization': MonetizationService(business_services, core_services),
        'rights_protection': RightsProtectionService(business_services, core_services),
        'seo_optimizer': SEOOptimizerService(business_services, core_services)
    }
    
    # Initialize service registry and coordinator
    services['registry'] = ServiceRegistry(services)
    services['coordinator'] = PlatformCoordinator(services, business_services, core_services)
    
    return services


def get_platform_coordinator(business_services, core_services):
    """
Get platform coordinator with all services initialized"""
    services = initialize_platform_services(business_services, core_services)
    return services['coordinator']


def get_analytics_service(core_services):
    """
Get standalone analytics service"""
    return AnalyticsService(core_services)


def get_collaboration_matching_service(business_services, core_services):
    """
Get standalone collaboration matching service"""
    return CollaborationMatchingService(business_services, core_services)


def get_content_ingestion_service(business_services, core_services):
    """
Get standalone content ingestion service"""
    return ContentIngestionService(business_services, core_services)


def get_distribution_service(business_services, core_services):
    """
Get standalone distribution service"""
    return DistributionService(business_services, core_services)


def get_monetization_service(business_services, core_services):
    """
Get standalone monetization service"""
    return MonetizationService(business_services, core_services)


def get_rights_protection_service(business_services, core_services):
    """
Get standalone rights protection service"""
    return RightsProtectionService(business_services, core_services)


def get_seo_optimizer_service(business_services, core_services):
    """
Get standalone SEO optimizer service"""
    return SEOOptimizerService(business_services, core_services)


# Service factory aliases
create_analytics_service = get_analytics_service
create_collaboration_matching_service = get_collaboration_matching_service
create_content_ingestion_service = get_content_ingestion_service
create_distribution_service = get_distribution_service
create_monetization_service = get_monetization_service
create_rights_protection_service = get_rights_protection_service
create_seo_optimizer_service = get_seo_optimizer_service
create_platform_coordinator = get_platform_coordinator


__all__ = [
    # Core Platform Services
    'AnalyticsService',
    'CollaborationMatchingService',
    'ContentIngestionService',
    'DistributionService',
    'MonetizationService',
    'RightsProtectionService',
    'SEOOptimizerService',
    
    # Specialized Components
    'MetricsCollector',
    'ReportingEngine',
    'PartnerFinder',
    'CompatibilityEngine',
    'MediaProcessor',
    'ContentValidator',
    'PlatformManager',
    'ContentSynchronizer',
    'RevenueOptimizer',
    'PaymentGateway',
    'CopyrightValidator',
    'ViolationDetector',
    'ContentOptimizer',
    'KeywordAnalyzer',
    
    # Service Coordination
    'ServiceRegistry',
    'ServiceHealthMonitor',
    'PlatformCoordinator',
    'ServiceOrchestrator',
    
    # Factory Functions
    'initialize_platform_services',
    'get_platform_coordinator',
    'get_analytics_service',
    'get_collaboration_matching_service',
    'get_content_ingestion_service',
    'get_distribution_service',
    'get_monetization_service',
    'get_rights_protection_service',
    'get_seo_optimizer_service',
    
    # Service Aliases
    'create_analytics_service',
    'create_collaboration_matching_service',
    'create_content_ingestion_service',
    'create_distribution_service',
    'create_monetization_service',
    'create_rights_protection_service',
    'create_seo_optimizer_service',
    'create_platform_coordinator'
]
