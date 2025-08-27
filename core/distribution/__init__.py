"""
Distribution System - Advanced Multi-Platform Content Distribution Engine
=========================================================================

Professional-grade distribution system for AI Influencer Agent platform
providing comprehensive multi-platform distribution capabilities with
advanced optimization, analytics, and monitoring features.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.
"""

from .manager import DistributionManager, DistributionRequest, DistributionResult
from .publisher import ContentPublisher, PublishingRequest, PublishingResult
from .scheduler import DistributionScheduler, SchedulingRequest, SchedulingResult
from .adapter import PlatformAdapter, BasePlatformAdapter, YouTubeAdapter, InstagramAdapter
from .tracker import DistributionTracker, TrackingData, PerformanceMetrics
from .analytics import DistributionAnalytics, AnalyticsQuery, AnalyticsResult
from .validator import DistributionValidator, ValidationCheck, ValidationReport
from .optimizer import DistributionOptimizer, OptimizationResult, OptimizationRecommendation
from .gateway import DistributionGateway, APIRequest, APIResponse
from .index import DistributionSystem, create_distribution_system, get_system_health

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__copyright__ = "© 2025 Fahed Mlaiel. All rights reserved."

# Core distribution components
__all__ = [
    # Main distribution classes
    "DistributionManager",
    "ContentPublisher", 
    "DistributionScheduler",
    "PlatformAdapter",
    "DistributionTracker",
    "DistributionAnalytics",
    "DistributionValidator",
    "DistributionOptimizer",
    "DistributionGateway",
    "DistributionSystem",
    
    # Base classes and adapters
    "BasePlatformAdapter",
    "YouTubeAdapter",
    "InstagramAdapter",
    
    # Data structures
    "DistributionRequest",
    "DistributionResult",
    "PublishingRequest",
    "PublishingResult", 
    "SchedulingRequest",
    "SchedulingResult",
    "TrackingData",
    "PerformanceMetrics",
    "AnalyticsQuery",
    "AnalyticsResult",
    "ValidationCheck",
    "ValidationReport",
    "OptimizationResult",
    "OptimizationRecommendation",
    "APIRequest",
    "APIResponse",
    
    # Factory functions
    "create_distribution_system",
    "get_system_health"
]

# Distribution system metadata
DISTRIBUTION_SYSTEM_INFO = {
    "name": "IA Influencer Agent Distribution System",
    "version": __version__,
    "author": __author__,
    "email": __email__,
    "copyright": __copyright__,
    "description": "Professional multi-platform content distribution engine",
    "features": [
        "Multi-platform distribution (YouTube, Instagram, TikTok, Spotify, Twitter, Facebook)",
        "Intelligent scheduling and optimization",
        "Real-time performance tracking and analytics", 
        "Advanced content adaptation and SEO optimization",
        "Comprehensive security and compliance validation",
        "AI-powered distribution optimization",
        "Enterprise-grade monitoring and alerting",
        "Advanced analytics with ML predictions",
        "Multi-level content validation system",
        "Intelligent optimization recommendations",
        "Centralized API gateway with rate limiting"
    ],
    "supported_platforms": [
        "YouTube", "Instagram", "TikTok", "Spotify", 
        "Twitter", "Facebook", "LinkedIn", "Pinterest"
    ],
    "capabilities": {
        "concurrent_distributions": 1000,
        "platforms_per_distribution": 8,
        "real_time_analytics": True,
        "ai_optimization": True,
        "enterprise_security": True,
        "99_9_uptime": True,
        "ml_predictions": True,
        "advanced_validation": True,
        "intelligent_optimization": True,
        "centralized_gateway": True
    }
}

from .manager import DistributionManager
from .publisher import ContentPublisher
from .scheduler import DistributionScheduler
from .adapter import PlatformAdapter
from .tracker import DistributionTracker
from .optimizer import DistributionOptimizer
from .validator import DistributionValidator
from .analytics import DistributionAnalytics
from .synchronizer import PlatformSynchronizer
from .router import ContentRouter
from .monitor import DistributionMonitor
from .controller import DistributionController
from .processor import DistributionProcessor
from .orchestrator import DistributionOrchestrator
from .gateway import PlatformGateway
from .aggregator import DistributionAggregator
from .coordinator import DistributionCoordinator
from .engine import DistributionEngine
from .handler import DistributionHandler
from .bridge import PlatformBridge

# Import the main system interface
from .index import DistributionSystem, DistributionStatus, create_distribution_system

__all__ = [
    'DistributionManager',
    'ContentPublisher',
    'DistributionScheduler',
    'PlatformAdapter',
    'DistributionTracker',
    'DistributionOptimizer',
    'DistributionValidator',
    'DistributionAnalytics',
    'PlatformSynchronizer',
    'ContentRouter',
    'DistributionMonitor',
    'DistributionController',
    'DistributionProcessor',
    'DistributionOrchestrator',
    'PlatformGateway',
    'DistributionAggregator',
    'DistributionCoordinator',
    'DistributionEngine',
    'DistributionHandler',
    'PlatformBridge',
    'DistributionSystem',
    'DistributionStatus',
    'create_distribution_system'
]

# Version and metadata
__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__copyright__ = "© 2025 Fahed Mlaiel. All rights reserved."
