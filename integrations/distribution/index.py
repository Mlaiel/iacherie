"""
Distribution - Ainflue Integrations
===================================
Point d'entrée principal pour distribution multi-plateformes.
Orchestration 65+ plateformes avec scheduling intelligent.

Author: Fahed Mlaiel (mlaiel@live.de)
Project: Ainflue Integrations  
Version: 1.0 Production
"""

from .multi_platform_distributor import MultiPlatformDistributor
from .intelligent_scheduler import IntelligentScheduler
from .content_optimization_distributor import ContentOptimizationDistributor
from .distribution_analytics import DistributionAnalytics
from .synchronization_manager import SynchronizationManager
from .performance_optimizer import PerformanceOptimizer
from .automated_distribution_pipeline import AutomatedDistributionPipeline

# Configuration logique métier Ainflue
DISTRIBUTION_CONFIG = {
    'supported_platforms': 65,
    'platform_categories': {
        'social_media': 29,
        'music_streaming': 20, 
        'creator_economy': 16
    },
    'content_formats': ['video', 'audio', 'image', 'text', 'stories', 'reels'],
    'scheduling_algorithms': ['optimal_timing', 'audience_overlap', 'platform_algorithms'],
    'optimization_features': ['format_conversion', 'metadata_optimization', 'thumbnail_generation'],
    'analytics_metrics': ['reach', 'engagement', 'conversions', 'revenue', 'growth'],
    'automation_levels': ['manual', 'semi_automated', 'fully_automated'],
    'distribution_strategies': ['simultaneous', 'sequential', 'platform_specific', 'a_b_testing']
}

def get_distribution_manager() -> None:
    """Factory pour créer le gestionnaire principal de distribution."""
    return {
        'distributor': MultiPlatformDistributor(),
        'scheduler': IntelligentScheduler(),
        'optimizer': ContentOptimizationDistributor(),
        'analytics': DistributionAnalytics(),
        'sync': SynchronizationManager(),
        'performance': PerformanceOptimizer(),
        'pipeline': AutomatedDistributionPipeline()
    }