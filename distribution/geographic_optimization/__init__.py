"""Geographic Optimization Engine

Geographic targeting and localization optimization system for the Ainflue platform.
Optimizes content distribution based on geographic regions, cultural preferences,
and local market dynamics.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from .geo_targeting_engine import GeoTargetingEngine, TargetingStrategy
from .cultural_adapter import CulturalAdapter, CulturalOptimization
from .timezone_optimizer import TimezoneOptimizer, TimezoneStrategy
from .localization_manager import LocalizationManager, LocalizationPlan
from .regional_trends_analyzer import RegionalTrendsAnalyzer, RegionalTrends
from .language_optimizer import LanguageOptimizer, LanguageStrategy
from .compliance_checker import ComplianceChecker, RegionalCompliance
from .market_penetration_analyzer import MarketPenetrationAnalyzer, MarketInsights

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"

__all__ = [
    "GeoTargetingEngine", "TargetingStrategy", "CulturalAdapter", "CulturalOptimization",
    "TimezoneOptimizer", "TimezoneStrategy", "LocalizationManager", "LocalizationPlan",
    "RegionalTrendsAnalyzer", "RegionalTrends", "LanguageOptimizer", "LanguageStrategy",
    "ComplianceChecker", "RegionalCompliance", "MarketPenetrationAnalyzer", "MarketInsights"
]