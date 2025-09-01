"""
Behavior Models for User Behavior Agent
Core data models and types for user behavior analysis.
"""

from typing import Dict, List, Optional, Any
from enum import Enum
from dataclasses import dataclass
from datetime import datetime


class UserSegmentType(Enum):
    """User segment types for behavior analysis."""
    CREATOR = "creator"
    VIEWER = "viewer"
    BRAND = "brand"
    COLLABORATOR = "collaborator"
    PREMIUM = "premium"
    BASIC = "basic"


class BehaviorPatternType(Enum):
    """Behavior pattern types for analysis."""
    CONTENT_CONSUMPTION = "content_consumption"
    ENGAGEMENT = "engagement"
    MONETIZATION = "monetization"
    COLLABORATION = "collaboration"
    LEARNING = "learning"
    SOCIAL_INTERACTION = "social_interaction"


@dataclass
class BehaviorMetrics:
    """Metrics for user behavior analysis."""
    engagement_rate: float
    content_consumption: float
    interaction_frequency: float
    session_duration: float
    platform_loyalty: float
    content_creation_rate: float
    collaboration_rate: float
    revenue_contribution: float


@dataclass
class UserEngagementData:
    """User engagement data structure."""
    user_id: str
    session_id: str
    platform: str
    timestamp: datetime
    actions: List[Dict[str, Any]]
    content_interactions: List[Dict[str, Any]]
    session_duration: float
    devices_used: List[str]


@dataclass
class BehaviorAnalysisRequest:
    """Request structure for behavior analysis."""
    user_id: str
    analysis_type: str
    time_period: Dict[str, datetime]
    platforms: List[str]
    metrics_requested: List[str]
    include_predictions: bool = True
    segment_analysis: bool = True


@dataclass
class BehaviorPrediction:
    """User behavior prediction results."""
    user_id: str
    prediction_type: str
    confidence_score: float
    predicted_actions: List[Dict[str, Any]]
    risk_factors: List[str]
    opportunities: List[str]
    recommended_strategies: List[str]
    prediction_horizon: int  # days


@dataclass
class UserSegmentProfile:
    """User segment profile definition."""
    segment_id: str
    segment_type: UserSegmentType
    characteristics: Dict[str, Any]
    behavior_patterns: List[str]
    preferences: Dict[str, Any]
    value_metrics: BehaviorMetrics
    segment_size: int
    growth_trend: float


@dataclass
class BehaviorAnalysisResult:
    """Comprehensive behavior analysis results."""
    user_id: str
    analysis_timestamp: datetime
    current_segment: UserSegmentProfile
    behavior_metrics: BehaviorMetrics
    engagement_data: UserEngagementData
    predictions: List[BehaviorPrediction]
    insights: List[str]
    recommendations: List[str]
    anomalies_detected: List[Dict[str, Any]]
    confidence_score: float
    next_analysis_date: datetime