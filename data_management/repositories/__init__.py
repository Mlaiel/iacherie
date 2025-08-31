""" Data Repositories Module - IA Influencer Agent Platform Enterprise
======================================================================
Module: backend/data_management/repositories/__init__.py
Author: Fahed Mlaiel (mlaiel@live.de)
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + IA Prompt Engineer
Type: Industrial Data Repositories - Enterprise Production-Ready
Responsibility: Couche d'accès aux données avec patterns Repository avancés
========================================================================

  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL 
© 2025 Fahed Mlaiel. Tous droits réservés.
Usage non autorisé strictement interdit et passible de poursuites judiciaires.
Email: mlaiel@live.de

LOGIQUE MÉTIER REPOSITORIES:
Model → Repository Interface → DB Adapter → Connection Pool → 
Query Optimization → Cache Layer → Result Mapping → Business Logic

ARCHITECTURE COMPLETE:
 BaseRepository - Pattern abstraction avec audit et cache
 ContentRepository - Multi-format avec AI processing
 CreatorRepository - Gestion profils et collaborations
 ProtectionRepository - AI monitoring et violations
 AnalyticsRepository - Métriques avancées et insights
 MonetizationRepository - Revenue tracking et paiements
 CollaborationRepository - Matching et partnerships
 FingerprintRepository - AI identification et duplicates
"""
__version__ = "3.1.0"
__author__ = "Fahed Mlaiel <mlaiel@live.de>"
__team__ = "Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + IA Prompt Engineer"

# Import repository classes for easy access
from .base_repository import BaseRepository, AsyncBaseRepository
from .content_repository import ContentRepository, AsyncContentRepository
from .creator_repository import CreatorRepository, AsyncCreatorRepository
from .analytics_repository import AnalyticsRepository, AsyncAnalyticsRepository
from .fingerprint_repository import FingerprintRepository, AsyncFingerprintRepository
from .protection_repository import ProtectionRepository, AsyncProtectionRepository
from .monetization_repository import MonetizationRepository, AsyncMonetizationRepository
from .collaboration_repository import CollaborationRepository, AsyncCollaborationRepository
from .licensing_repository import LicensingRepository, AsyncLicensingRepository
from .platform_repository import PlatformRepository, AsyncPlatformRepository
from .ai_processing_repository import AIProcessingRepository, AsyncAIProcessingRepository
from .performance_repository import PerformanceRepository, AsyncPerformanceRepository
from .revenue_repository import RevenueRepository, AsyncRevenueRepository
from .web_crawler_repository import WebCrawlerRepository, AsyncWebCrawlerRepository
from .seo_repository import SEORepository, AsyncSEORepository
from .distribution_repository import DistributionRepository, AsyncDistributionRepository
from .audience_repository import AudienceRepository, AsyncAudienceRepository
from .notification_repository import NotificationRepository, AsyncNotificationRepository
from .workflow_repository import WorkflowRepository, AsyncWorkflowRepository

# Repository registry for factory pattern
REPOSITORY_REGISTRY = {
    'base': BaseRepository,
    'content': ContentRepository,
    'creator': CreatorRepository,
    'analytics': AnalyticsRepository,
    'fingerprint': FingerprintRepository,
    'protection': ProtectionRepository,
    'monetization': MonetizationRepository,
    'collaboration': CollaborationRepository,
    'licensing': LicensingRepository,
    'platform': PlatformRepository,
    'ai_processing': AIProcessingRepository,
    'performance': PerformanceRepository,
    'revenue': RevenueRepository,
    'web_crawler': WebCrawlerRepository,
    'seo': SEORepository,
    'distribution': DistributionRepository,
    'audience': AudienceRepository,
    'notification': NotificationRepository,
    'workflow': WorkflowRepository,
}

# Async repository registry
ASYNC_REPOSITORY_REGISTRY = {
    'base': AsyncBaseRepository,
    'content': AsyncContentRepository,
    'creator': AsyncCreatorRepository,
    'analytics': AsyncAnalyticsRepository,
    'fingerprint': AsyncFingerprintRepository,
    'protection': AsyncProtectionRepository,
    'monetization': AsyncMonetizationRepository,
    'collaboration': AsyncCollaborationRepository,
    'licensing': AsyncLicensingRepository,
    'platform': AsyncPlatformRepository,
    'ai_processing': AsyncAIProcessingRepository,
    'performance': AsyncPerformanceRepository,
    'revenue': AsyncRevenueRepository,
    'web_crawler': AsyncWebCrawlerRepository,
    'seo': AsyncSEORepository,
    'distribution': AsyncDistributionRepository,
    'audience': AsyncAudienceRepository,
    'notification': AsyncNotificationRepository,
    'workflow': AsyncWorkflowRepository,
}

# Repository Factory Functions
def create_repository(repo_type: str, **kwargs):
    """Create a repository instance with dependency injection"""    if repo_type not in REPOSITORY_REGISTRY:
        raise ValueError(f"Unknown repository type: {repo_type}")
    
    repository_class = REPOSITORY_REGISTRY[repo_type]
    return repository_class(**kwargs)

def create_async_repository(repo_type: str, **kwargs):
    """Create an async repository instance with dependency injection"""    if repo_type not in ASYNC_REPOSITORY_REGISTRY:
        raise ValueError(f"Unknown async repository type: {repo_type}")
    
    repository_class = ASYNC_REPOSITORY_REGISTRY[repo_type]
    return repository_class(**kwargs)

# Repository Configuration
REPOSITORY_CONFIG = {
    'cache_enabled': True,
    'cache_ttl': 3600,  # 1 hour default
    'audit_enabled': True,
    'metrics_enabled': True,
    'batch_size': 1000,
    'connection_pool_size': 20,
    'query_timeout': 30,
    'retry_attempts': 3,
    'performance_monitoring': True
}

# Import index module for factory patterns
from .index import (
    RepositoryFactory,
    RepositoryType,
    RepositoryHealth,
    RepositoryMetrics,
    repository_factory,
    get_repository,
    get_async_repository,
    create_full_repository_suite,
    create_full_async_repository_suite
)

# Export all repository classes for easy import
# Export all repository classes and utilities
__all__ = [
    # Base repositories
    'BaseRepository', 'AsyncBaseRepository',
    
    # Core repositories
    'ContentRepository', 'AsyncContentRepository',
    'CreatorRepository', 'AsyncCreatorRepository',
    'AnalyticsRepository', 'AsyncAnalyticsRepository',
    
    # Protection and security repositories
    'FingerprintRepository', 'AsyncFingerprintRepository',
    'ProtectionRepository', 'AsyncProtectionRepository',
    'WebCrawlerRepository', 'AsyncWebCrawlerRepository',
    
    # Business repositories
    'MonetizationRepository', 'AsyncMonetizationRepository',
    'RevenueRepository', 'AsyncRevenueRepository',
    'CollaborationRepository', 'AsyncCollaborationRepository',
    'LicensingRepository', 'AsyncLicensingRepository',
    'PlatformRepository', 'AsyncPlatformRepository',
    
    # AI and processing repositories
    'AIProcessingRepository', 'AsyncAIProcessingRepository',
    'PerformanceRepository', 'AsyncPerformanceRepository',
    
    # Registry and utilities
    'REPOSITORY_REGISTRY', 'ASYNC_REPOSITORY_REGISTRY',
    'RepositoryFactory',
    'get_repository', 'get_async_repository',
    'create_full_repository_suite', 'create_full_async_repository_suite'
]

# Module Metadata for Documentation
REPOSITORY_MODULES = {
    'base_repository': {
        'description': 'Abstract repository patterns with enterprise features',
        'features': ['Audit trails', 'Caching', 'Performance monitoring', 'Batch operations'],
        'dependencies': ['Database connection', 'Cache manager', 'Audit service']
    },
    'content_repository': {
        'description': 'Multi-format content management with AI processing',
        'features': ['AI fingerprinting', 'SEO optimization', 'Protection registration', 'Format conversion'],
        'dependencies': ['AI processor', 'Fingerprint service', 'Protection service']
    },
    'creator_repository': {
        'description': 'Creator profile and collaboration management',
        'features': ['Skill analysis', 'Collaboration matching', 'Tier management', 'Analytics'],
        'dependencies': ['AI processor', 'Analytics service', 'Collaboration service']
    },
    'protection_repository': {
        'description': 'AI-powered content protection and monitoring',
        'features': ['Violation detection', 'Automated responses', 'Legal documentation', 'Monitoring'],
        'dependencies': ['Fingerprint service', 'Monitoring service', 'Legal service']
    },
    'analytics_repository': {
        'description': 'Advanced analytics and performance metrics',
        'features': ['Real-time metrics', 'Predictive analytics', 'Competitive analysis', 'Visualization'],
        'dependencies': ['AI processor', 'Prediction service', 'Visualization service']
    },
    'monetization_repository': {
        'description': 'Revenue tracking and optimization',
        'features': ['Multi-currency support', 'Subscription management', 'Commission calculation', 'Fraud detection'],
        'dependencies': ['Payment processor', 'Tax service', 'Analytics service', 'Fraud detector']
    },
    'collaboration_repository': {
        'description': 'Creator partnerships and matching',
        'features': ['AI matching', 'Project management', 'Revenue sharing', 'Performance tracking'],
        'dependencies': ['AI matcher', 'Analytics service', 'Notification service', 'Payment service']
    },
    'fingerprint_repository': {
        'description': 'AI-powered content identification',
        'features': ['Multi-modal fingerprints', 'Similarity detection', 'Duplicate prevention', 'Content tracking'],
        'dependencies': ['Fingerprint engine', 'Similarity matcher', 'Vector store', 'Analytics service']
    }
}

# Validation and Health Check
def validate_repository_health():
    """Validate that all repositories are properly configured"""    health_status = {}
    
    for repo_name, repo_class in REPOSITORY_REGISTRY.items():
        try:
            # Basic instantiation test
            repo_instance = repo_class()
            health_status[repo_name] = {
                'status': 'healthy',
                'version': getattr(repo_class, '__version__', 'unknown'),
                'features': REPOSITORY_MODULES.get(f"{repo_name}_repository", {}).get('features', [])
            }
        except Exception as e:
            health_status[repo_name] = {
                'status': 'error',
                'error': str(e),
                'features': []
            }
    
    return health_status

# Performance Metrics
def get_repository_metrics():
    """Get performance metrics for all repositories"""


    return {
        'total_repositories': len(REPOSITORY_REGISTRY),
        'async_repositories': len(ASYNC_REPOSITORY_REGISTRY),
        'features_count': sum(len(module.get('features', [])) for module in REPOSITORY_MODULES.values()),
        'health_status': validate_repository_health()
    }

# Export all repository classes
__all__ = [
    # Base repositories
    'BaseRepository', 'AsyncBaseRepository',
    
    # Core repositories
    'ContentRepository', 'AsyncContentRepository',
    'CreatorRepository', 'AsyncCreatorRepository',
    'AnalyticsRepository', 'AsyncAnalyticsRepository',
    
    # Protection and security repositories
    'FingerprintRepository', 'AsyncFingerprintRepository',
    'ProtectionRepository', 'AsyncProtectionRepository',
    'WebCrawlerRepository', 'AsyncWebCrawlerRepository',
    
    # Business repositories
    'MonetizationRepository', 'AsyncMonetizationRepository',
    'RevenueRepository', 'AsyncRevenueRepository',
    'CollaborationRepository', 'AsyncCollaborationRepository',
    'LicensingRepository', 'AsyncLicensingRepository',
    'PlatformRepository', 'AsyncPlatformRepository',
    
    # AI and processing repositories
    'AIProcessingRepository', 'AsyncAIProcessingRepository',
    'PerformanceRepository', 'AsyncPerformanceRepository',
    
    # New advanced repositories
    'SEORepository', 'AsyncSEORepository',
    'DistributionRepository', 'AsyncDistributionRepository',
    'AudienceRepository', 'AsyncAudienceRepository',
    'NotificationRepository', 'AsyncNotificationRepository',
    'WorkflowRepository', 'AsyncWorkflowRepository',
    
    # Registry and utilities
    'REPOSITORY_REGISTRY', 'ASYNC_REPOSITORY_REGISTRY',
    'RepositoryFactory',
    'get_repository', 'get_async_repository',
    'create_full_repository_suite', 'create_full_async_repository_suite'
]
