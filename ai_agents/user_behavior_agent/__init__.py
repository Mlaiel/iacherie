"""User Behavior Agent - Behavioral Analysis for Ainflue Platform

This agent provides comprehensive user behavior analytics including pattern recognition,
segmentation, and predictive insights for user engagement optimization.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from .core.user_behavior_agent import UserBehaviorAgent
from .models.behavior_models import (
    BehaviorAnalysisRequest,
    BehaviorAnalysisResult,
    UserSegmentProfile,
    BehaviorPrediction
)

__all__ = [
    'UserBehaviorAgent',
    'BehaviorAnalysisRequest',
    'BehaviorAnalysisResult',
    'UserSegmentProfile',
    'BehaviorPrediction'
]

__version__ = "1.0.0"