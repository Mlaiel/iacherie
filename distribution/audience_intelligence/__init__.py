"""Audience Intelligence Engine

Advanced AI-powered audience analysis and intelligence system for the Ainflue platform.
Provides deep insights into audience behavior, preferences, and engagement patterns
using machine learning and real-time analytics.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

# Core audience profiler
from .audience_profiler import (
    AudienceProfiler,
    AudienceProfile,
    AudienceSegment,
    ProfileInsight,
    EngagementPattern,
    DemographicData
)

# Advanced behavior analyzer
from .behavior_analyzer import (
    AdvancedBehaviorAnalyzer,
    BehaviorMetrics,
    BehaviorInsight,
    BehaviorPattern
)

# Preference engine
from .preference_engine import (
    AdvancedPreferenceEngine,
    PreferenceProfile,
    UserPreference,
    PreferenceInsight,
    PreferenceType,
    PreferenceStrength
)

# Demographic mapper
from .demographic_mapper import (
    IntelligentDemographicMapper,
    DemographicProfile,
    DemographicInsight,
    AgeGroup,
    DemographicCategory,
    DeviceType
)

# Engagement predictor
from .engagement_predictor import (
    AdvancedEngagementPredictor,
    EngagementPrediction,
    ComprehensiveEngagementForecast,
    EngagementType,
    PredictionTimeframe,
    ConfidenceLevel
)

# Main intelligence engine
from .index import AudienceIntelligenceEngine

__version__ = "2.0.0"
__author__ = "Fahed Mlaiel"

__all__ = [
    # Main Engine
    "AudienceIntelligenceEngine",
    
    # Audience Profiler
    "AudienceProfiler", "AudienceProfile", "AudienceSegment", 
    "ProfileInsight", "EngagementPattern", "DemographicData",
    
    # Behavior Analyzer
    "AdvancedBehaviorAnalyzer", "BehaviorMetrics", "BehaviorInsight", "BehaviorPattern",
    
    # Preference Engine
    "AdvancedPreferenceEngine", "PreferenceProfile", "UserPreference", 
    "PreferenceInsight", "PreferenceType", "PreferenceStrength",
    
    # Demographic Mapper
    "IntelligentDemographicMapper", "DemographicProfile", "DemographicInsight",
    "AgeGroup", "DemographicCategory", "DeviceType",
    
    # Engagement Predictor
    "AdvancedEngagementPredictor", "EngagementPrediction", "ComprehensiveEngagementForecast",
    "EngagementType", "PredictionTimeframe", "ConfidenceLevel"
]