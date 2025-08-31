"""High-Performance Enterprise Crawler Database Module

Advanced SQLAlchemy-based database layer for multi-platform content crawling,
real-time monitoring, and intelligent data management.

Author: Fahed Mlaiel <mlaiel@live.de>
Team Specialties: Lead AI Developer + Backend Senior + ML Engineer + DBA + Security + 
                 Microservices + Audio + DevOps + IA Prompt Engineer
Copyright: All rights reserved
"""from .index import CrawlerDatabaseManager
from .analytics import CrawlerAnalyticsManager
from .content_discoveries import ContentDiscoveryManager
from .jobs import CrawlerJobManager
from .platform_configs import PlatformConfigManager
from .proxy_pools import ProxyPoolManager
from .rate_limits import RateLimitManager
from .sessions import CrawlerSessionManager
from .platform_crawlers import PlatformCrawlerManager
from .scheduler import CrawlerSchedulingManager
from .surveillance import ContentSurveillanceManager
from .optimization import CrawlerOptimizationManager
from .data_enrichment import CrawlerDataEnrichmentManager
from .compliance import CrawlerComplianceManager
from .security import CrawlerSecurityManager

__all__ = [
    "CrawlerDatabaseManager",
    "CrawlerAnalyticsManager", 
    "ContentDiscoveryManager",
    "CrawlerJobManager",
    "PlatformConfigManager",
    "ProxyPoolManager",
    "RateLimitManager",
    "CrawlerSessionManager",
    "PlatformCrawlerManager",
    "CrawlerSchedulingManager",
    "ContentSurveillanceManager",
    "CrawlerOptimizationManager",
    "CrawlerDataEnrichmentManager",
    "CrawlerComplianceManager",
    "CrawlerSecurityManager"
]

from .index import CrawlingDatabaseManager
from .sessions import CrawlingSessionManager, SessionPriority
from .jobs import CrawlingJobManager
from .analytics import CrawlingAnalyticsManager
from .rate_limits import RateLimitManager, RateLimitPeriod, PlatformLimits
from .proxy_pools import ProxyPoolManager, ProxyHealthStatus
from .platform_configs import PlatformConfigManager, PlatformType, DefaultConfigurations
from .content_discoveries import ContentDiscoveryManager, DiscoveryCategory, ConfidenceLevel

# NEW ENTERPRISE MODULES - Advanced Crawling Capabilities
from .platform_crawlers import (
    PlatformCrawlerManager, PlatformType as CrawlerPlatformType,
    CrawlerCapability, CrawlerStatus
)
from .scheduler import (
    CrawlerSchedulingManager, SchedulePriority, ScheduleStatus,
    ExecutionMode, QueueType
)
from .surveillance import (
    ContentSurveillanceManager, SurveillanceType, MatchConfidence,
    AlertSeverity, MonitoringStatus
)
from .optimization import (
    CrawlerOptimizationManager, MetricType, OptimizationStrategy,
    ResourceType, PerformanceStatus
)

# Export all managers and utilities
__all__ = [
    # Main manager
    'CrawlingDatabaseManager',
    
    # Core specialized managers  
    'CrawlingSessionManager',
    'CrawlingJobManager', 
    'CrawlingAnalyticsManager',
    'RateLimitManager',
    'ProxyPoolManager',
    'PlatformConfigManager',
    'ContentDiscoveryManager',
    
    # NEW ENTERPRISE MANAGERS
    'PlatformCrawlerManager',
    'CrawlerSchedulingManager',
    'ContentSurveillanceManager', 
    'CrawlerOptimizationManager',
    
    # Core enums and utilities
    'SessionPriority',
    'RateLimitPeriod',
    'PlatformLimits',
    'ProxyHealthStatus',
    'PlatformType',
    'DefaultConfigurations',
    'DiscoveryCategory',
    'ConfidenceLevel',
    
    # NEW ENTERPRISE ENUMS
    'CrawlerPlatformType',
    'CrawlerCapability',
    'CrawlerStatus',
    'SchedulePriority',
    'ScheduleStatus',
    'ExecutionMode',
    'QueueType',
    'SurveillanceType',
    'MatchConfidence',
    'AlertSeverity',
    'MonitoringStatus',
    'MetricType',
    'OptimizationStrategy',
    'ResourceType',
    'PerformanceStatus'
]

# Module metadata
__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__description__ = "Enterprise crawling database module for IA Influencer Agent"

from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

# Version du module
__version__ = "1.0.0"

# Modules exportés
__all__ = [
    "crawler_jobs",
    "scraping_targets",
    "detection_results",
    "web_monitoring",
    "platform_crawlers"
]

def get_module_info() -> Dict[str, Any]:
    """    Get comprehensive module information and capabilities.
    
    Returns:
        Dict containing module metadata, capabilities, and team information
    """    return {
        "module_name": "Enterprise Crawling Database Module",
        "version": "2.0.0",
        "description": "Advanced database layer for multi-platform web surveillance, crawling operations, and content discovery with AI-powered protection",
        "team_specialties": [
            "Lead AI Developer",
            "Backend Senior Engineer", 
            "ML Engineer",
            "Database Administrator",
            "Security Expert",
            "Microservices Architect",
            "Audio Processing Specialist",
            "DevOps Engineer",
            "IA Prompt Engineer"
        ],
        "author": {
            "name": "Fahed Mlaiel",
            "email": "mlaiel@live.de",
            "copyright_notice": "All rights reserved. Unauthorized use, reproduction, or distribution is strictly prohibited."
        },
        "capabilities": [
            "Multi-platform crawler management (YouTube, TikTok, Instagram, Twitter, Spotify)",
            "Advanced scheduling and queue management",
            "Real-time content surveillance and copyright monitoring", 
            "Intelligent performance optimization and scaling",
            "Comprehensive analytics and reporting",
            "Enterprise-grade security and compliance",
            "AI-powered content fingerprinting integration",
            "Automated alert and notification systems"
        ],
        "supported_platforms": [
            "YouTube", "TikTok", "Instagram", "Twitter/X", 
            "Spotify", "SoundCloud", "Generic Web"
        ],
        "core_managers": [
            "CrawlingDatabaseManager", "PlatformCrawlerManager",
            "CrawlerSchedulingManager", "ContentSurveillanceManager", 
            "CrawlerOptimizationManager"
        ],
        "enterprise_features": [
            "Real-time monitoring", "Intelligent scaling", 
            "Performance optimization", "Security compliance",
            "Multi-tenant support", "Advanced analytics"
        ],
        "created_date": "2025-08-26",
        "last_updated": "2025-08-26"
    }
