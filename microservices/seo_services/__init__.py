"""
Ainflue SEO Services Module
Search Engine Optimization & Content Discovery

This module provides comprehensive SEO services for content optimization,
keyword analysis, ranking monitoring, and search visibility enhancement
across multiple platforms and search engines.

Architecture: SEO Services (14 services)
- Real-time SEO optimization and recommendations
- Multi-platform keyword analysis and tracking
- Automated link building and local SEO
- Performance monitoring and ranking analytics
- Content optimization for search discovery

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from .seo_optimization_service import SEOOptimizationService
from .seo_recommendation_service import SEORecommendationService
from .seo_analytics_service import SEOAnalyticsService
from .keyword_analysis_service import KeywordAnalysisService
from .ranking_monitoring_service import RankingMonitoringService
from .link_building_service import LinkBuildingService
from .local_seo_service import LocalSEOService

__all__ = [
    'SEOOptimizationService',
    'SEORecommendationService',
    'SEOAnalyticsService',
    'KeywordAnalysisService',
    'RankingMonitoringService',
    'LinkBuildingService',
    'LocalSEOService'
]

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"