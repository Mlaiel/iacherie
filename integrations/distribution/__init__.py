"""
Distribution Module - Ainflue Integrations
==========================================
Module de distribution enterprise pour 65+ plateformes avec
scheduling intelligent, optimization contenu et analytics performance.

Support pour:
- Distribution simultanée 65+ plateformes
- Scheduling intelligent et automation
- Optimization contenu par plateforme
- Analytics performance cross-platform
- Gestion formats et metadata

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

__all__ = [
    'MultiPlatformDistributor',
    'IntelligentScheduler',
    'ContentOptimizationDistributor',
    'DistributionAnalytics',
    'SynchronizationManager',
    'PerformanceOptimizer',
    'AutomatedDistributionPipeline'
]

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__description__ = "Distribution enterprise - 65+ plateformes et scheduling intelligent"