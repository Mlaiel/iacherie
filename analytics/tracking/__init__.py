"""
Analytics Tracking Package
Package de modules de suivi analytique
FINAL PACKAGE FOR 100% VICTORY!
"""

# Imports pour le package analytics.tracking
from .seo_tracking import SEOTracker, SEOMetrics, track_seo_keyword, track_seo_traffic, get_seo_analytics, SEOEventTracker

# Compatibilité et aliases
SEOAnalytics = SEOTracker
KeywordTracker = SEOTracker

# Export pour accès direct
__all__ = [
    'SEOTracker',
    'SEOMetrics', 
    'SEOAnalytics',
    'KeywordTracker',
    'SEOEventTracker',  # CRUCIAL pour 100%!
    'track_seo_keyword',
    'track_seo_traffic',
    'get_seo_analytics'
]

import logging
logger = logging.getLogger(__name__)
logger.info("🚀 Analytics Tracking Package loaded - 100% READY!")
logger.info("✅ SEO Tracking module accessible - VICTORY INCOMING!")