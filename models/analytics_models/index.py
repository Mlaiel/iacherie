"""
📊 ANALYTICS MODELS INDEX - ENTERPRISE GRADE
==========================================

Point d'entrée central pour tous les modèles Analytics Enterprise
Support complet: Performance, Audience, Revenue, Predictive Analytics

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
Architecture: Enterprise Analytics Models with advanced BI patterns
"""

from .base_analytics_model import BaseAnalyticsModel
from .performance_analytics_model import PerformanceAnalyticsModel
from .audience_analytics_model import AudienceAnalyticsModel
from .revenue_analytics_model import RevenueAnalyticsModel
from .engagement_analytics_model import EngagementAnalyticsModel
from .geographic_analytics_model import GeographicAnalyticsModel
from .temporal_analytics_model import TemporalAnalyticsModel
from .platform_analytics_model import PlatformAnalyticsModel
from .behavioral_analytics_model import BehavioralAnalyticsModel
from .kpi_tracking_model import KPITrackingModel
from .trend_analysis_model import TrendAnalysisModel
from .conversion_analytics_model import ConversionAnalyticsModel
from .reporting_model import ReportingModel
from .predictive_analytics_model import PredictiveAnalyticsModel

# Enterprise Analytics Models Collection
__all__ = [
    # Core Analytics Models
    'BaseAnalyticsModel',
    'PerformanceAnalyticsModel',
    'ReportingModel',
    'KPITrackingModel',
    
    # Audience & Behavior Analytics
    'AudienceAnalyticsModel',
    'EngagementAnalyticsModel',
    'BehavioralAnalyticsModel',
    'ConversionAnalyticsModel',
    
    # Geographic & Temporal Analytics
    'GeographicAnalyticsModel',
    'TemporalAnalyticsModel',
    'PlatformAnalyticsModel',
    
    # Business Intelligence
    'RevenueAnalyticsModel',
    'TrendAnalysisModel',
    'PredictiveAnalyticsModel',
]

# Enterprise Analytics Registry
ANALYTICS_MODELS_REGISTRY = {
    'performance': {
        'base': BaseAnalyticsModel,
        'performance': PerformanceAnalyticsModel,
        'kpi': KPITrackingModel,
        'reporting': ReportingModel,
    },
    'audience': {
        'audience': AudienceAnalyticsModel,
        'engagement': EngagementAnalyticsModel,
        'behavior': BehavioralAnalyticsModel,
        'conversion': ConversionAnalyticsModel,
    },
    'intelligence': {
        'geographic': GeographicAnalyticsModel,
        'temporal': TemporalAnalyticsModel,
        'platform': PlatformAnalyticsModel,
        'trends': TrendAnalysisModel,
        'predictive': PredictiveAnalyticsModel,
    },
    'business': {
        'revenue': RevenueAnalyticsModel,
    }
}

def get_analytics_model(category: str, model_type: str):
    """
    Récupère un modèle Analytics Enterprise par catégorie et type
    
    Args:
        category: performance, audience, intelligence, business
        model_type: Type spécifique de modèle analytics
        
    Returns:
        Classe du modèle Analytics Enterprise correspondant
    """
    return ANALYTICS_MODELS_REGISTRY.get(category, {}).get(model_type)

def list_available_analytics_models():
    """Liste tous les modèles Analytics Enterprise disponibles"""
    return ANALYTICS_MODELS_REGISTRY

# Analytics Models Enterprise Stats
ANALYTICS_MODELS_STATS = {
    'total_models': 14,
    'categories': 4,
    'performance_models': 4,
    'audience_models': 4,
    'intelligence_models': 5,
    'business_models': 1,
    'enterprise_ready': True,
    'real_time_capable': True,
    'bi_integrated': True
}