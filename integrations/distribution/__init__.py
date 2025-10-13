"""
Distribution Module - IA Chérie Integrations
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
Project: IA Chérie Integrations
Version: 1.0 Production
"""

from .multi_platform_distributor import MultiPlatformDistributor
from .intelligent_scheduler import IntelligentScheduler
from .content_optimization_distributor import ContentOptimizationDistributor
from .performance_optimizer import PerformanceOptimizer
from .synchronization_manager import SynchronizationManager
from .distribution_analytics import DistributionAnalytics
from .audience_intelligence_engine import AudienceIntelligenceEngine
from .viral_prediction_engine import ViralPredictionEngine
from .automated_distribution_pipeline import AutomatedDistributionPipeline
from .regional_distribution_manager import RegionalDistributionManager
from .mobile_distribution_optimizer import MobileDistributionOptimizer
from .creator_monetization_distributor import CreatorMonetizationDistributor

__all__ = [
    'MultiPlatformDistributor',
    'IntelligentScheduler',
    'ContentOptimizationDistributor',
    'PerformanceOptimizer',
    'SynchronizationManager',
    'DistributionAnalytics',
    'AudienceIntelligenceEngine',
    'ViralPredictionEngine',
    'AutomatedDistributionPipeline',
    'RegionalDistributionManager',
    'MobileDistributionOptimizer',
    'CreatorMonetizationDistributor'
]

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__description__ = "Distribution enterprise - 65+ plateformes et scheduling intelligent"