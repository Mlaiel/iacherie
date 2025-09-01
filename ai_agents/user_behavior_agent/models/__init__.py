"""
User Behavior Agent Models
Core data models for user behavior analysis and prediction.
"""

from .behavior_models import (
    BehaviorAnalysisRequest,
    BehaviorAnalysisResult,
    UserSegmentProfile,
    BehaviorPrediction,
    UserSegmentType,
    BehaviorMetrics,
    UserEngagementData
)

__all__ = [
    "BehaviorAnalysisRequest",
    "BehaviorAnalysisResult", 
    "UserSegmentProfile",
    "BehaviorPrediction",
    "UserSegmentType",
    "BehaviorMetrics",
    "UserEngagementData"
]