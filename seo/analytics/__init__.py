"""SEO Analytics Package
Analytics and intelligence for SEO performance.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

# Core analytics modules with correct imports
from .seo_intelligence_engine import AdvancedSEOAnalytics as SEOIntelligenceEngine
from .ranking_monitor import RankingMonitor as SearchRankingMonitor
from .organic_traffic_analyzer import OrganicTrafficAnalyzer
from .conversion_tracking_seo import SEOConversionTracker, ConversionReportGenerator
from .seo_roi_calculator import SEOROICalculator, ROIOptimizer

# New competitive intelligence modules  
from .market_gap_analyzer import MarketGapAnalyzer
from .backlink_analyzer import BacklinkAnalyzer
from .content_gap_identifier import ContentGapIdentifier
from .serp_feature_tracker import SERPFeatureTracker
from .competitor_keyword_spy import CompetitorKeywordSpy

# New trending & insights modules
from .viral_content_predictor import ViralContentPredictor
from .seasonal_trend_analyzer import SeasonalTrendAnalyzer

# Language validation function
from .language_validation import validate_644_language_support

__all__ = [
    "SEOIntelligenceEngine",
    "SearchRankingMonitor",
    "OrganicTrafficAnalyzer",
    "SEOConversionTracker",
    "ConversionReportGenerator",
    "SEOROICalculator",
    "ROIOptimizer",
    "MarketGapAnalyzer",
    "BacklinkAnalyzer",
    "ContentGapIdentifier",
    "SERPFeatureTracker",
    "CompetitorKeywordSpy",
    "ViralContentPredictor",
    "SeasonalTrendAnalyzer",
    "validate_644_language_support"
]
