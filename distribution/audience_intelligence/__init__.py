"""Audience Intelligence Engine

Advanced AI-powered audience analysis and intelligence system for the Ainflue platform.
Provides deep insights into audience behavior, preferences, and engagement patterns
using machine learning and real-time analytics.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from .audience_profiler import AudienceProfiler, AudienceProfile
from .behavior_analyzer import BehaviorAnalyzer, BehaviorPattern
from .preference_engine import PreferenceEngine, UserPreferences
from .demographic_mapper import DemographicMapper, DemographicSegment
from .psychographic_analyzer import PsychographicAnalyzer, PersonalityProfile
from .engagement_predictor import EngagementPredictor, EngagementScore
from .lookalike_finder import LookalikeFinder, LookalikeAudience
from .segment_optimizer import SegmentOptimizer, OptimalSegments

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"

__all__ = [
    "AudienceProfiler", "AudienceProfile", "BehaviorAnalyzer", "BehaviorPattern",
    "PreferenceEngine", "UserPreferences", "DemographicMapper", "DemographicSegment",
    "PsychographicAnalyzer", "PersonalityProfile", "EngagementPredictor", "EngagementScore",
    "LookalikeFinder", "LookalikeAudience", "SegmentOptimizer", "OptimalSegments"
]