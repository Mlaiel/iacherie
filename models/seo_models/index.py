"""
🔍 SEO MODELS INDEX - ENTERPRISE GRADE
=====================================

Point d'entrée central pour tous les modèles SEO Enterprise
Support complet: Keywords, Ranking, Optimization, Multi-language, Analytics

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
Architecture: Enterprise SEO Models with advanced optimization patterns
"""

from .base_seo_model import BaseSEOModel
from .keyword_model import KeywordModel
from .ranking_model import RankingModel
from .search_optimization_model import SearchOptimizationModel
from .meta_tags_model import MetaTagsModel
from .link_building_model import LinkBuildingModel
from .seo_analytics_model import SEOAnalyticsModel
from .multilingual_seo_model import MultilingualSEOModel
from .mobile_seo_model import MobileSEOModel
from .page_speed_model import PageSpeedModel
from .content_optimization_model import ContentOptimizationModel
from .visibility_tracking_model import VisibilityTrackingModel
from .seo_automation_model import SEOAutomationModel
from .competitor_analysis_model import CompetitorAnalysisModel

# Enterprise SEO Models Collection
__all__ = [
    # Core SEO Models
    'BaseSEOModel',
    'KeywordModel',
    'RankingModel',
    'SearchOptimizationModel',
    
    # Content & Technical SEO
    'MetaTagsModel',
    'LinkBuildingModel',
    'ContentOptimizationModel',
    'PageSpeedModel',
    
    # Specialized SEO Models
    'MultilingualSEOModel',
    'MobileSEOModel',
    'SEOAutomationModel',
    
    # Analytics & Intelligence
    'SEOAnalyticsModel',
    'VisibilityTrackingModel',
    'CompetitorAnalysisModel',
]

# Enterprise SEO Registry
SEO_MODELS_REGISTRY = {
    'core': {
        'base': BaseSEOModel,
        'keywords': KeywordModel,
        'ranking': RankingModel,
        'optimization': SearchOptimizationModel,
    },
    'technical': {
        'meta_tags': MetaTagsModel,
        'link_building': LinkBuildingModel,
        'content_optimization': ContentOptimizationModel,
        'page_speed': PageSpeedModel,
    },
    'specialized': {
        'multilingual': MultilingualSEOModel,
        'mobile': MobileSEOModel,
        'automation': SEOAutomationModel,
    },
    'analytics': {
        'seo_analytics': SEOAnalyticsModel,
        'visibility': VisibilityTrackingModel,
        'competitor': CompetitorAnalysisModel,
    }
}

def get_seo_model(category: str, model_type: str):
    """
    Récupère un modèle SEO Enterprise par catégorie et type
    
    Args:
        category: core, technical, specialized, analytics
        model_type: Type spécifique de modèle SEO
        
    Returns:
        Classe du modèle SEO Enterprise correspondant
    """
    return SEO_MODELS_REGISTRY.get(category, {}).get(model_type)

def list_available_seo_models():
    """Liste tous les modèles SEO Enterprise disponibles"""
    return SEO_MODELS_REGISTRY

# SEO Models Enterprise Stats
SEO_MODELS_STATS = {
    'total_models': 14,
    'categories': 4,
    'core_models': 4,
    'technical_models': 4,
    'specialized_models': 3,
    'analytics_models': 3,
    'enterprise_ready': True,
    'multilingual_support': True,
    'mobile_optimized': True,
    'automation_enabled': True,
    'competitor_tracking': True
}