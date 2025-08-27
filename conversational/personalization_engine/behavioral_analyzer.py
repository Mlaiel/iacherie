"""
Behavioral Analyzer
==================

Industrial-grade behavioral analysis engine for IA Influencer Agent.
Analyzes user behavior patterns, engagement metrics, content consumption patterns, 
and provides deep insights for personalization optimization.

Business Logic:
User (musician/blogger/photographer/influencer/comedian) → Upload multi-format → AI rights protection → Professional SEO → Collaboration matching → Multi-platform distribution

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.
License: Proprietary - Unauthorized use strictly prohibited

WARNING: Any attempt to steal, copy, or use the concept, idea, or code without explicit written permission from Fahed Mlaiel (mlaiel@live.de) is strictly prohibited and will be prosecuted.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
import pandas as pd
from collections import defaultdict, Counter
import json

from ..core.base_service import BaseService
from ..core.exceptions import BehavioralAnalysisError, ValidationError
from ..database.mongodb import MongoDBHandler
from ..cache.redis_cache import RedisCache
from ..analytics.metrics_calculator import MetricsCalculator
from ..ml.clustering_models import UserClusteringModel

logger = logging.getLogger(__name__)


class BehaviorType(str, Enum):
    """Types of user behaviors to analyze"""
    CONTENT_CONSUMPTION = "content_consumption"
    CREATION_PATTERN = "creation_pattern"
    ENGAGEMENT_STYLE = "engagement_style"
    COLLABORATION_BEHAVIOR = "collaboration_behavior"
    PLATFORM_USAGE = "platform_usage"
    TEMPORAL_PATTERN = "temporal_pattern"
    CONTENT_INTERACTION = "content_interaction"


class EngagementLevel(str, Enum):
    """User engagement levels"""
    HIGH_ENGAGED = "high_engaged"
    MODERATELY_ENGAGED = "moderately_engaged"
    LOW_ENGAGED = "low_engaged"
    DORMANT = "dormant"
    NEW_USER = "new_user"


class ContentInteractionType(str, Enum):
    """Types of content interactions"""
    VIEW = "view"
    LIKE = "like"
    SHARE = "share"
    COMMENT = "comment"
    DOWNLOAD = "download"
    BOOKMARK = "bookmark"
    COLLABORATE = "collaborate"
    REMIX = "remix"


@dataclass
class BehaviorPattern:
    """User behavior pattern data"""
    pattern_id: str
    user_id: str
    behavior_type: BehaviorType
    pattern_data: Dict[str, Any]
    frequency: float
    confidence_score: float
    temporal_distribution: Dict[str, float]
    platform_distribution: Dict[str, float]
    created_at: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EngagementMetrics:
    """User engagement metrics"""
    user_id: str
    engagement_level: EngagementLevel
    session_duration_avg: float
    interaction_frequency: float
    content_creation_rate: float
    collaboration_index: float
    platform_diversity: float
    retention_score: float
    value_score: float
    last_activity: datetime
    metrics_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BehavioralInsight:
    """Behavioral insight for personalization"""
    insight_id: str
    user_id: str
    insight_type: str
    description: str
    confidence: float
    actionable_recommendations: List[str]
    supporting_data: Dict[str, Any]
    generated_at: datetime


class BehavioralAnalyzer(BaseService):
    """
    Advanced behavioral analysis engine for user personalization
    """
    
    def __init__(
        self,
        mongodb_handler: MongoDBHandler,
        redis_cache: RedisCache,
        metrics_calculator: MetricsCalculator,
        clustering_model: UserClusteringModel
    ):
        super().__init__()
        self.mongodb = mongodb_handler
        self.redis_cache = redis_cache
        self.metrics_calculator = metrics_calculator
        self.clustering_model = clustering_model
        
        # Configuration
        self.analysis_window_days = 30
        self.min_interactions_threshold = 10
        self.pattern_confidence_threshold = 0.7
        self.cache_ttl = 1800  # 30 minutes
        
        # Pattern detection models
        self._temporal_patterns = {}
        self._content_patterns = {}
        self._engagement_patterns = {}
        
        logger.info("BehavioralAnalyzer initialized successfully")

    async def initialize(self) -> None:
        """Initialize behavioral analyzer"""
        try:
            # Load pre-trained pattern models
            await self._load_pattern_models()
            
            # Initialize clustering models
            await self.clustering_model.initialize()
            
            logger.info("BehavioralAnalyzer initialization completed")
            
        except Exception as e:
            logger.error(f"Failed to initialize BehavioralAnalyzer: {e}")
            raise BehavioralAnalysisError(f"Initialization failed: {e}")

    async def analyze_user_behavior(
        self,
        user_id: str,
        analysis_period: Optional[Tuple[datetime, datetime]] = None,
        behavior_types: Optional[List[BehaviorType]] = None
    ) -> Dict[str, Any]:
        """
        Comprehensive behavioral analysis for a user
        
        Args:
            user_id: User identifier
            analysis_period: Time period for analysis
            behavior_types: Specific behavior types to analyze
            
        Returns:
            Complete behavioral analysis results
        """
        try:
            # Set default analysis period
            if not analysis_period:
                end_date = datetime.now()
                start_date = end_date - timedelta(days=self.analysis_window_days)
                analysis_period = (start_date, end_date)
            
            # Set default behavior types
            if not behavior_types:
                behavior_types = list(BehaviorType)
            
            # Check cache
            cache_key = f"behavior_analysis:{user_id}:{hash(str(analysis_period))}"
            cached_result = await self.redis_cache.get(cache_key)
            if cached_result:
                return json.loads(cached_result)
            
            # Collect user interaction data
            interaction_data = await self._collect_interaction_data(
                user_id, analysis_period
            )
            
            # Analyze different behavior types
            behavior_analysis = {}
            for behavior_type in behavior_types:
                behavior_analysis[behavior_type.value] = await self._analyze_behavior_type(
                    user_id, behavior_type, interaction_data, analysis_period
                )
            
            # Generate engagement metrics
            engagement_metrics = await self._calculate_engagement_metrics(
                user_id, interaction_data, analysis_period
            )
            
            # Detect behavioral patterns
            patterns = await self._detect_behavioral_patterns(
                user_id, interaction_data, analysis_period
            )
            
            # Generate behavioral insights
            insights = await self._generate_behavioral_insights(
                user_id, behavior_analysis, engagement_metrics, patterns
            )
            
            # User clustering analysis
            cluster_info = await self._analyze_user_cluster(
                user_id, behavior_analysis, engagement_metrics
            )
            
            # Compile results
            analysis_result = {
                "user_id": user_id,
                "analysis_period": {
                    "start": analysis_period[0].isoformat(),
                    "end": analysis_period[1].isoformat()
                },
                "behavior_analysis": behavior_analysis,
                "engagement_metrics": engagement_metrics.__dict__ if engagement_metrics else None,
                "behavioral_patterns": [pattern.__dict__ for pattern in patterns],
                "insights": [insight.__dict__ for insight in insights],
                "cluster_info": cluster_info,
                "analysis_summary": await self._generate_analysis_summary(
                    behavior_analysis, engagement_metrics, patterns, insights
                ),
                "generated_at": datetime.now().isoformat()
            }
            
            # Cache results
            await self.redis_cache.setex(
                cache_key, self.cache_ttl, json.dumps(analysis_result, default=str)
            )
            
            logger.info(f"Behavioral analysis completed for user {user_id}")
            return analysis_result
            
        except Exception as e:
            logger.error(f"Behavioral analysis failed for user {user_id}: {e}")
            raise BehavioralAnalysisError(f"Analysis failed: {e}")

    async def track_real_time_behavior(
        self,
        user_id: str,
        interaction: Dict[str, Any]
    ) -> None:
        """
        Track real-time user behavior for immediate insights
        
        Args:
            user_id: User identifier
            interaction: Real-time interaction data
        """
        try:
            # Validate interaction data
            await self._validate_interaction_data(interaction)
            
            # Store interaction
            await self._store_interaction(user_id, interaction)
            
            # Update real-time metrics
            await self._update_real_time_metrics(user_id, interaction)
            
            # Check for immediate pattern changes
            await self._check_pattern_changes(user_id, interaction)
            
            # Update user cluster if needed
            await self._update_user_clustering(user_id, interaction)
            
            logger.debug(f"Real-time behavior tracked for user {user_id}")
            
        except Exception as e:
            logger.error(f"Failed to track real-time behavior: {e}")
            raise BehavioralAnalysisError(f"Real-time tracking failed: {e}")

    async def get_behavioral_predictions(
        self,
        user_id: str,
        prediction_horizon: int = 7  # days
    ) -> Dict[str, Any]:
        """
        Generate behavioral predictions for user
        
        Args:
            user_id: User identifier
            prediction_horizon: Days to predict ahead
            
        Returns:
            Behavioral predictions and recommendations
        """
        try:
            # Get recent behavioral data
            recent_behavior = await self.analyze_user_behavior(user_id)
            
            # Predict future engagement
            engagement_prediction = await self._predict_engagement(
                user_id, recent_behavior, prediction_horizon
            )
            
            # Predict content preferences
            content_predictions = await self._predict_content_preferences(
                user_id, recent_behavior, prediction_horizon
            )
            
            # Predict collaboration likelihood
            collaboration_prediction = await self._predict_collaboration_likelihood(
                user_id, recent_behavior, prediction_horizon
            )
            
            # Predict churn risk
            churn_risk = await self._predict_churn_risk(
                user_id, recent_behavior, prediction_horizon
            )
            
            # Generate optimization recommendations
            optimization_recommendations = await self._generate_optimization_recommendations(
                user_id, recent_behavior, engagement_prediction, content_predictions
            )
            
            predictions = {
                "user_id": user_id,
                "prediction_horizon_days": prediction_horizon,
                "engagement_prediction": engagement_prediction,
                "content_preferences_prediction": content_predictions,
                "collaboration_likelihood": collaboration_prediction,
                "churn_risk": churn_risk,
                "optimization_recommendations": optimization_recommendations,
                "confidence_scores": await self._calculate_prediction_confidence(
                    user_id, recent_behavior
                ),
                "generated_at": datetime.now().isoformat()
            }
            
            logger.info(f"Behavioral predictions generated for user {user_id}")
            return predictions
            
        except Exception as e:
            logger.error(f"Failed to generate behavioral predictions: {e}")
            raise BehavioralAnalysisError(f"Prediction generation failed: {e}")

    # Private helper methods
    
    async def _collect_interaction_data(
        self,
        user_id: str,
        period: Tuple[datetime, datetime]
    ) -> List[Dict[str, Any]]:
        """Collect user interaction data for the specified period"""
        try:
            # Query interaction data from MongoDB
            interactions = await self.mongodb.find_many(
                "user_interactions",
                {
                    "user_id": user_id,
                    "timestamp": {
                        "$gte": period[0],
                        "$lte": period[1]
                    }
                },
                sort=[("timestamp", 1)]
            )
            
            return interactions
            
        except Exception as e:
            logger.error(f"Failed to collect interaction data: {e}")
            return []

    async def _analyze_behavior_type(
        self,
        user_id: str,
        behavior_type: BehaviorType,
        interaction_data: List[Dict[str, Any]],
        period: Tuple[datetime, datetime]
    ) -> Dict[str, Any]:
        """Analyze specific behavior type"""
        try:
            if behavior_type == BehaviorType.CONTENT_CONSUMPTION:
                return await self._analyze_content_consumption(interaction_data)
            elif behavior_type == BehaviorType.CREATION_PATTERN:
                return await self._analyze_creation_pattern(interaction_data)
            elif behavior_type == BehaviorType.ENGAGEMENT_STYLE:
                return await self._analyze_engagement_style(interaction_data)
            elif behavior_type == BehaviorType.COLLABORATION_BEHAVIOR:
                return await self._analyze_collaboration_behavior(interaction_data)
            elif behavior_type == BehaviorType.PLATFORM_USAGE:
                return await self._analyze_platform_usage(interaction_data)
            elif behavior_type == BehaviorType.TEMPORAL_PATTERN:
                return await self._analyze_temporal_pattern(interaction_data)
            elif behavior_type == BehaviorType.CONTENT_INTERACTION:
                return await self._analyze_content_interaction(interaction_data)
            else:
                return {}
                
        except Exception as e:
            logger.error(f"Failed to analyze behavior type {behavior_type}: {e}")
            return {}

    async def _calculate_engagement_metrics(
        self,
        user_id: str,
        interaction_data: List[Dict[str, Any]],
        period: Tuple[datetime, datetime]
    ) -> Optional[EngagementMetrics]:
        """Calculate comprehensive engagement metrics"""
        try:
            if not interaction_data:
                return None
            
            # Calculate session duration
            session_durations = await self._calculate_session_durations(interaction_data)
            avg_session_duration = np.mean(session_durations) if session_durations else 0
            
            # Calculate interaction frequency
            total_interactions = len(interaction_data)
            period_days = (period[1] - period[0]).days
            interaction_frequency = total_interactions / max(period_days, 1)
            
            # Calculate content creation rate
            creation_interactions = [
                i for i in interaction_data 
                if i.get("interaction_type") in ["create", "upload", "publish"]
            ]
            content_creation_rate = len(creation_interactions) / max(period_days, 1)
            
            # Calculate collaboration index
            collaboration_interactions = [
                i for i in interaction_data 
                if i.get("interaction_type") in ["collaborate", "share", "remix"]
            ]
            collaboration_index = len(collaboration_interactions) / max(total_interactions, 1)
            
            # Calculate platform diversity
            platforms = set(i.get("platform", "unknown") for i in interaction_data)
            platform_diversity = len(platforms)
            
            # Calculate retention score
            retention_score = await self._calculate_retention_score(user_id, interaction_data)
            
            # Calculate value score
            value_score = await self._calculate_value_score(user_id, interaction_data)
            
            # Determine engagement level
            engagement_level = await self._determine_engagement_level(
                avg_session_duration, interaction_frequency, content_creation_rate
            )
            
            # Get last activity
            last_activity = max(
                (datetime.fromisoformat(i["timestamp"]) for i in interaction_data),
                default=datetime.now()
            )
            
            return EngagementMetrics(
                user_id=user_id,
                engagement_level=engagement_level,
                session_duration_avg=avg_session_duration,
                interaction_frequency=interaction_frequency,
                content_creation_rate=content_creation_rate,
                collaboration_index=collaboration_index,
                platform_diversity=platform_diversity,
                retention_score=retention_score,
                value_score=value_score,
                last_activity=last_activity,
                metrics_data={
                    "total_interactions": total_interactions,
                    "unique_platforms": list(platforms),
                    "session_count": len(session_durations),
                    "creation_interactions": len(creation_interactions),
                    "collaboration_interactions": len(collaboration_interactions)
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to calculate engagement metrics: {e}")
            return None

    async def _detect_behavioral_patterns(
        self,
        user_id: str,
        interaction_data: List[Dict[str, Any]],
        period: Tuple[datetime, datetime]
    ) -> List[BehaviorPattern]:
        """Detect behavioral patterns from interaction data"""
        try:
            patterns = []
            
            # Temporal patterns
            temporal_patterns = await self._detect_temporal_patterns(interaction_data)
            patterns.extend(temporal_patterns)
            
            # Content preference patterns
            content_patterns = await self._detect_content_patterns(interaction_data)
            patterns.extend(content_patterns)
            
            # Engagement patterns
            engagement_patterns = await self._detect_engagement_patterns(interaction_data)
            patterns.extend(engagement_patterns)
            
            # Collaboration patterns
            collaboration_patterns = await self._detect_collaboration_patterns(interaction_data)
            patterns.extend(collaboration_patterns)
            
            # Filter patterns by confidence threshold
            high_confidence_patterns = [
                p for p in patterns 
                if p.confidence_score >= self.pattern_confidence_threshold
            ]
            
            return high_confidence_patterns
            
        except Exception as e:
            logger.error(f"Failed to detect behavioral patterns: {e}")
            return []

    async def _generate_behavioral_insights(
        self,
        user_id: str,
        behavior_analysis: Dict[str, Any],
        engagement_metrics: Optional[EngagementMetrics],
        patterns: List[BehaviorPattern]
    ) -> List[BehavioralInsight]:
        """Generate actionable behavioral insights"""
        try:
            insights = []
            
            # Engagement insights
            if engagement_metrics:
                engagement_insights = await self._generate_engagement_insights(
                    user_id, engagement_metrics
                )
                insights.extend(engagement_insights)
            
            # Pattern-based insights
            pattern_insights = await self._generate_pattern_insights(
                user_id, patterns
            )
            insights.extend(pattern_insights)
            
            # Content optimization insights
            content_insights = await self._generate_content_insights(
                user_id, behavior_analysis
            )
            insights.extend(content_insights)
            
            # Collaboration insights
            collaboration_insights = await self._generate_collaboration_insights(
                user_id, behavior_analysis
            )
            insights.extend(collaboration_insights)
            
            return insights
            
        except Exception as e:
            logger.error(f"Failed to generate behavioral insights: {e}")
            return []

    async def _analyze_content_consumption(
        self,
        interaction_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze content consumption patterns"""
        content_interactions = [
            i for i in interaction_data 
            if i.get("interaction_type") in ["view", "download", "bookmark"]
        ]
        
        if not content_interactions:
            return {}
        
        # Analyze content types
        content_types = Counter(i.get("content_type", "unknown") for i in content_interactions)
        
        # Analyze consumption times
        consumption_times = [
            datetime.fromisoformat(i["timestamp"]).hour 
            for i in content_interactions
        ]
        
        # Analyze duration patterns
        durations = [
            i.get("duration", 0) for i in content_interactions 
            if i.get("duration")
        ]
        
        return {
            "total_consumption_events": len(content_interactions),
            "content_type_preferences": dict(content_types),
            "preferred_consumption_hours": Counter(consumption_times),
            "average_consumption_duration": np.mean(durations) if durations else 0,
            "consumption_frequency": len(content_interactions) / max(len(interaction_data), 1)
        }

    async def _analyze_creation_pattern(
        self,
        interaction_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze content creation patterns"""
        creation_interactions = [
            i for i in interaction_data 
            if i.get("interaction_type") in ["create", "upload", "publish", "edit"]
        ]
        
        if not creation_interactions:
            return {}
        
        # Analyze creation frequency
        creation_days = set(
            datetime.fromisoformat(i["timestamp"]).date() 
            for i in creation_interactions
        )
        
        # Analyze content types created
        created_types = Counter(i.get("content_type", "unknown") for i in creation_interactions)
        
        # Analyze creation times
        creation_hours = Counter(
            datetime.fromisoformat(i["timestamp"]).hour 
            for i in creation_interactions
        )
        
        return {
            "total_creation_events": len(creation_interactions),
            "active_creation_days": len(creation_days),
            "creation_frequency": len(creation_interactions) / max(len(creation_days), 1),
            "content_type_distribution": dict(created_types),
            "preferred_creation_hours": dict(creation_hours),
            "creation_consistency": len(creation_days) / 30 if creation_days else 0  # 30-day window
        }

    async def _analyze_engagement_style(
        self,
        interaction_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze user engagement style"""
        engagement_interactions = [
            i for i in interaction_data 
            if i.get("interaction_type") in ["like", "share", "comment", "follow"]
        ]
        
        if not engagement_interactions:
            return {}
        
        # Analyze engagement types
        engagement_types = Counter(i.get("interaction_type") for i in engagement_interactions)
        
        # Analyze engagement depth
        comment_interactions = [i for i in engagement_interactions if i.get("interaction_type") == "comment"]
        share_interactions = [i for i in engagement_interactions if i.get("interaction_type") == "share"]
        
        return {
            "total_engagement_events": len(engagement_interactions),
            "engagement_type_distribution": dict(engagement_types),
            "comment_to_like_ratio": len(comment_interactions) / max(engagement_types.get("like", 1), 1),
            "share_to_view_ratio": len(share_interactions) / max(len(interaction_data), 1),
            "engagement_rate": len(engagement_interactions) / max(len(interaction_data), 1)
        }


# Factory functions and utilities

def create_behavioral_analyzer(
    mongodb_handler: MongoDBHandler,
    redis_cache: RedisCache,
    metrics_calculator: MetricsCalculator,
    clustering_model: UserClusteringModel
) -> BehavioralAnalyzer:
    """Create behavioral analyzer instance"""
    return BehavioralAnalyzer(
        mongodb_handler=mongodb_handler,
        redis_cache=redis_cache,
        metrics_calculator=metrics_calculator,
        clustering_model=clustering_model
    )


def validate_behavior_analysis_request(
    user_id: str,
    analysis_period: Optional[Tuple[datetime, datetime]] = None
) -> bool:
    """Validate behavior analysis request"""
    if not user_id or not isinstance(user_id, str):
        return False
    
    if analysis_period and len(analysis_period) != 2:
        return False
    
    if analysis_period and analysis_period[0] >= analysis_period[1]:
        return False
    
    return True
