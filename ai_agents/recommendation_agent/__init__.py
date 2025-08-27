"""
Enterprise Recommendation Agent for IA Influencer Platform

Ultra-advanced recommendation system providing personalized content discovery,
collaboration matching, and revenue optimization for multi-modal creators.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or commercialization is strictly prohibited.
"""

from .recommendation_agent import RecommendationAgent
from .engine import HybridRecommendationEngine
from .personalization import PersonalizationEngine
from .content_analyzer import ContentAnalyzer
from .collaboration_matcher import CollaborationMatcher
from .revenue_optimizer import RevenueOptimizer
from .analytics import AnalyticsProcessor

from .models import (
    UserProfile,
    CreatorProfile,
    ContentItem,
    InteractionEvent,
    RecommendationContext,
    CollaborationRequest,
    TrendData,
    RevenueMetrics,
    SimilarityScore,
    PersonalizationVector,
    RecommendationResult,
    ContentType,
    InteractionType,
    RecommendationType,
    CreatorTier,
    MonetizationStrategy
)

from .interfaces import (
    IRecommendationEngine,
    ICollaborationMatcher,
    IContentAnalyzer,
    IPersonalizationEngine,
    IRevenueOptimizer,
    ITrendAnalyzer,
    IMultiModalProcessor,
    IRealtimeRecommendations,
    IRecommendationExplainer,
    IRecommendationStorage,
    IRecommendationMetrics,
    IABTestingFramework
)

__all__ = [
    # Main agent
    'RecommendationAgent',
    
    # Core engines
    'HybridRecommendationEngine',
    'PersonalizationEngine',
    'ContentAnalyzer',
    'CollaborationMatcher',
    'RevenueOptimizer',
    'AnalyticsProcessor',
    
    # Data models
    'UserProfile',
    'CreatorProfile',
    'ContentItem',
    'InteractionEvent',
    'RecommendationContext',
    'CollaborationRequest',
    'TrendData',
    'RevenueMetrics',
    'SimilarityScore',
    'PersonalizationVector',
    'RecommendationResult',
    
    # Enums
    'ContentType',
    'InteractionType',
    'RecommendationType',
    'CreatorTier',
    'MonetizationStrategy',
    
    # Interfaces
    'IRecommendationEngine',
    'ICollaborationMatcher',
    'IContentAnalyzer',
    'IPersonalizationEngine',
    'IRevenueOptimizer',
    'ITrendAnalyzer',
    'IMultiModalProcessor',
    'IRealtimeRecommendations',
    'IRecommendationExplainer',
    'IRecommendationStorage',
    'IRecommendationMetrics',
    'IABTestingFramework'
]

# Version information
__version__ = "1.0.0"
__author__ = "Fahed Mlaiel <mlaiel@live.de>"

from .recommendation_agent import (
    RecommendationAgent,
    RecommendationAgentManager,
    RecommendationLoadBalancer,
    RecommendationPerformanceMonitor,
    RecommendationExplainer,
    RecommendationPrivacyManager,
    RecommendationType,
    RecommendationStrategy,
    PersonalizationLevel,
    RecommendationItem,
    RecommendationSet
)

from .config import (
    get_config,
    validate_config,
    DEVELOPMENT_CONFIG,
    PRODUCTION_CONFIG,
    ENTERPRISE_CONFIG
)

__version__ = "2.1.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__copyright__ = "© 2025 Fahed Mlaiel. All Rights Reserved."

__all__ = [
    # Core Classes
    'RecommendationAgent',
    'RecommendationAgentManager',
    
    # Utility Classes
    'RecommendationLoadBalancer', 
    'RecommendationPerformanceMonitor',
    'RecommendationExplainer',
    'RecommendationPrivacyManager',
    
    # Enums
    'RecommendationType',
    'RecommendationStrategy', 
    'PersonalizationLevel',
    
    # Data Classes
    'RecommendationItem',
    'RecommendationSet',
    
    # Configuration
    'get_config',
    'validate_config',
    'DEVELOPMENT_CONFIG',
    'PRODUCTION_CONFIG', 
    'ENTERPRISE_CONFIG',
    
    # Module Metadata
    '__version__',
    '__author__',
    '__email__',
    '__copyright__'
]

# Module initialization logging
import logging
logger = logging.getLogger(__name__)
logger.info(f"Recommendation Agent Module v{__version__} initialized")
logger.info(f"Author: {__author__} ({__email__})")
logger.info(f"Copyright: {__copyright__}")

# Enterprise configuration validation
def validate_enterprise_config(config: dict) -> bool:
    """Validate enterprise configuration for production deployment"""
    required_keys = [
        'recommendation_models',
        'embedding_configs', 
        'personalization_settings',
        'performance_monitoring'
    ]
    
    for key in required_keys:
        if key not in config:
            logger.warning(f"Missing required config key: {key}")
            return False
    
    logger.info("Enterprise configuration validated successfully")
    return True

# Export validation function
__all__.append('validate_enterprise_config')