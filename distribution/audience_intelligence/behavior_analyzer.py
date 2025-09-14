"""
Advanced Audience Behavior Analysis Engine for Ainflue Distribution Platform

This module provides sophisticated behavioral analysis capabilities using machine learning
to understand user patterns, preferences, and engagement behaviors across platforms.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

logger = logging.getLogger(__name__)


class BehaviorPattern(Enum):
    """User behavior patterns identified by analysis"""
    PASSIVE_CONSUMER = "passive_consumer"
    ACTIVE_ENGAGER = "active_engager"
    CONTENT_CREATOR = "content_creator"
    TREND_FOLLOWER = "trend_follower"
    EARLY_ADOPTER = "early_adopter"
    LOYAL_FAN = "loyal_fan"
    CASUAL_BROWSER = "casual_browser"
    POWER_USER = "power_user"


@dataclass
class BehaviorMetrics:
    """Comprehensive behavior metrics for users"""
    user_id: str
    platform: str
    engagement_rate: float
    session_duration: float
    interaction_frequency: float
    content_preference_score: float
    viral_participation_rate: float
    sharing_propensity: float
    comment_engagement: float
    like_ratio: float
    time_spent_categories: Dict[str, float]
    peak_activity_hours: List[int]
    behavior_pattern: BehaviorPattern
    confidence_score: float
    last_updated: datetime


@dataclass
class BehaviorInsight:
    """Actionable insights from behavior analysis"""
    insight_type: str
    description: str
    confidence: float
    impact_score: float
    recommendations: List[str]
    target_segments: List[str]


class AdvancedBehaviorAnalyzer:
    """
    AI-powered behavior analysis engine for audience intelligence
    
    Features:
    - Real-time behavior pattern recognition
    - ML-based user segmentation
    - Predictive engagement analysis
    - Cross-platform behavior tracking
    - Personalized content recommendations
    """

    def __init__(self) -> None:
        self.scaler = StandardScaler()
        self.pca = PCA(n_components=10)
        self.kmeans = KMeans(n_clusters=8, random_state=42)
        self.behavior_patterns = {}
        self.insights_cache = {}
        
    async def analyze_user_behavior(
        self,
        user_id: str,
        platform: str,
        interaction_data: Dict[str, Any],
        timeframe_days: int = 30
    ) -> BehaviorMetrics:
        """
        Analyze comprehensive user behavior patterns
        
        Args:
            user_id: Unique user identifier
            platform: Platform being analyzed
            interaction_data: Raw interaction data
            timeframe_days: Analysis timeframe in days
            
        Returns:
            Comprehensive behavior metrics
        """
        try:
            # Extract behavior features
            features = await self._extract_behavior_features(
                user_id, platform, interaction_data, timeframe_days
            )
            
            # Calculate engagement metrics
            engagement_metrics = await self._calculate_engagement_metrics(features)
            
            # Identify behavior pattern
            pattern = await self._identify_behavior_pattern(features)
            
            # Calculate confidence score
            confidence = await self._calculate_confidence_score(features, pattern)
            
            return BehaviorMetrics(
                user_id=user_id,
                platform=platform,
                engagement_rate=engagement_metrics.get('engagement_rate', 0.0),
                session_duration=engagement_metrics.get('avg_session_duration', 0.0),
                interaction_frequency=engagement_metrics.get('interaction_frequency', 0.0),
                content_preference_score=engagement_metrics.get('content_preference', 0.0),
                viral_participation_rate=engagement_metrics.get('viral_participation', 0.0),
                sharing_propensity=engagement_metrics.get('sharing_propensity', 0.0),
                comment_engagement=engagement_metrics.get('comment_engagement', 0.0),
                like_ratio=engagement_metrics.get('like_ratio', 0.0),
                time_spent_categories=features.get('category_time', {}),
                peak_activity_hours=features.get('peak_hours', []),
                behavior_pattern=pattern,
                confidence_score=confidence,
                last_updated=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"Error analyzing user behavior: {e}")
            raise

    async def _extract_behavior_features(
        self,
        user_id: str,
        platform: str,
        data: Dict[str, Any],
        timeframe_days: int
    ) -> Dict[str, Any]:
        """Extract comprehensive behavior features from raw data"""
        
        features = {
            'total_sessions': len(data.get('sessions', [])),
            'total_interactions': sum(data.get('daily_interactions', [])),
            'avg_session_duration': np.mean(data.get('session_durations', [0])),
            'content_types_engaged': len(set(data.get('content_types', []))),
            'unique_creators_followed': len(set(data.get('creators_followed', []))),
            'sharing_frequency': len(data.get('shares', [])),
            'comment_frequency': len(data.get('comments', [])),
            'like_frequency': len(data.get('likes', [])),
            'time_of_day_activity': self._analyze_temporal_patterns(data),
            'content_category_preferences': self._analyze_content_preferences(data),
            'engagement_velocity': self._calculate_engagement_velocity(data),
            'social_connectivity': self._calculate_social_connectivity(data),
            'content_discovery_method': self._analyze_discovery_patterns(data),
            'retention_indicators': self._calculate_retention_indicators(data, timeframe_days)
        }
        
        return features

    async def _calculate_engagement_metrics(self, features: Dict[str, Any]) -> Dict[str, float]:
        """Calculate comprehensive engagement metrics"""
        
        total_content_viewed = features.get('total_sessions', 1)
        total_interactions = features.get('total_interactions', 0)
        
        metrics = {
            'engagement_rate': total_interactions / max(total_content_viewed, 1),
            'avg_session_duration': features.get('avg_session_duration', 0),
            'interaction_frequency': total_interactions / max(features.get('total_sessions', 1), 1),
            'content_preference': self._calculate_content_affinity(features),
            'viral_participation': self._calculate_viral_participation(features),
            'sharing_propensity': features.get('sharing_frequency', 0) / max(total_content_viewed, 1),
            'comment_engagement': features.get('comment_frequency', 0) / max(total_interactions, 1),
            'like_ratio': features.get('like_frequency', 0) / max(total_interactions, 1)
        }
        
        return metrics

    async def _identify_behavior_pattern(self, features: Dict[str, Any]) -> BehaviorPattern:
        """Identify user behavior pattern using ML classification"""
        
        # Create feature vector for ML classification
        feature_vector = np.array([
            features.get('total_sessions', 0),
            features.get('avg_session_duration', 0),
            features.get('total_interactions', 0),
            features.get('sharing_frequency', 0),
            features.get('comment_frequency', 0),
            features.get('content_types_engaged', 0),
            features.get('engagement_velocity', 0),
            features.get('social_connectivity', 0)
        ]).reshape(1, -1)
        
        # Simple rule-based classification (can be enhanced with trained ML model)
        sessions = features.get('total_sessions', 0)
        interactions = features.get('total_interactions', 0)
        duration = features.get('avg_session_duration', 0)
        sharing = features.get('sharing_frequency', 0)
        
        if sessions > 50 and interactions > 500:
            return BehaviorPattern.POWER_USER
        elif sharing > 20 and interactions > 200:
            return BehaviorPattern.CONTENT_CREATOR
        elif interactions > 100 and duration > 300:
            return BehaviorPattern.ACTIVE_ENGAGER
        elif sessions > 20 and interactions < 50:
            return BehaviorPattern.PASSIVE_CONSUMER
        elif sharing > 10:
            return BehaviorPattern.TREND_FOLLOWER
        elif duration > 600:
            return BehaviorPattern.LOYAL_FAN
        elif features.get('content_types_engaged', 0) > 5:
            return BehaviorPattern.EARLY_ADOPTER
        else:
            return BehaviorPattern.CASUAL_BROWSER

    async def _calculate_confidence_score(
        self,
        features: Dict[str, Any],
        pattern: BehaviorPattern
    ) -> float:
        """Calculate confidence score for behavior pattern identification"""
        
        # Base confidence on data completeness and consistency
        data_completeness = min(1.0, len([v for v in features.values() if v > 0]) / len(features))
        
        # Pattern-specific confidence adjustments
        pattern_confidence = {
            BehaviorPattern.POWER_USER: 0.9,
            BehaviorPattern.CONTENT_CREATOR: 0.85,
            BehaviorPattern.ACTIVE_ENGAGER: 0.8,
            BehaviorPattern.LOYAL_FAN: 0.8,
            BehaviorPattern.TREND_FOLLOWER: 0.75,
            BehaviorPattern.EARLY_ADOPTER: 0.7,
            BehaviorPattern.PASSIVE_CONSUMER: 0.7,
            BehaviorPattern.CASUAL_BROWSER: 0.6
        }.get(pattern, 0.5)
        
        return data_completeness * pattern_confidence

    def _analyze_temporal_patterns(self, data: Dict[str, Any]) -> Dict[str, float]:
        """Analyze temporal activity patterns"""
        
        timestamps = data.get('interaction_timestamps', [])
        if not timestamps:
            return {}
        
        hours = [datetime.fromisoformat(ts).hour for ts in timestamps if ts]
        hour_distribution = np.bincount(hours, minlength=24) / len(hours)
        
        return {f"hour_{i}": freq for i, freq in enumerate(hour_distribution)}

    def _analyze_content_preferences(self, data: Dict[str, Any]) -> Dict[str, float]:
        """Analyze content category preferences"""
        
        categories = data.get('content_categories', [])
        if not categories:
            return {}
        
        category_counts = {}
        for category in categories:
            category_counts[category] = category_counts.get(category, 0) + 1
        
        total = sum(category_counts.values())
        return {cat: count/total for cat, count in category_counts.items()}

    def _calculate_engagement_velocity(self, data: Dict[str, Any]) -> float:
        """Calculate how quickly user engages with new content"""
        
        timestamps = data.get('interaction_timestamps', [])
        if len(timestamps) < 2:
            return 0.0
        
        time_diffs = []
        for i in range(1, len(timestamps)):
            try:
                t1 = datetime.fromisoformat(timestamps[i-1])
                t2 = datetime.fromisoformat(timestamps[i])
                time_diffs.append((t2 - t1).total_seconds())
            except:
                continue
        
        return 1.0 / (np.mean(time_diffs) + 1) if time_diffs else 0.0

    def _calculate_social_connectivity(self, data: Dict[str, Any]) -> float:
        """Calculate user's social connectivity score"""
        
        follows = len(data.get('creators_followed', []))
        interactions = len(data.get('social_interactions', []))
        network_size = len(data.get('network_connections', []))
        
        return (follows + interactions + network_size) / 3.0

    def _analyze_discovery_patterns(self, data: Dict[str, Any]) -> Dict[str, float]:
        """Analyze how user discovers content"""
        
        discovery_methods = data.get('discovery_sources', [])
        if not discovery_methods:
            return {}
        
        method_counts = {}
        for method in discovery_methods:
            method_counts[method] = method_counts.get(method, 0) + 1
        
        total = sum(method_counts.values())
        return {method: count/total for method, count in method_counts.items()}

    def _calculate_retention_indicators(self, data: Dict[str, Any], timeframe_days: int) -> Dict[str, float]:
        """Calculate user retention indicators"""
        
        sessions = data.get('sessions', [])
        if not sessions:
            return {'retention_score': 0.0, 'consistency_score': 0.0}
        
        # Calculate session frequency consistency
        daily_sessions = {}
        for session in sessions:
            try:
                date = datetime.fromisoformat(session.get('timestamp', '')).date()
                daily_sessions[date] = daily_sessions.get(date, 0) + 1
            except:
                continue
        
        active_days = len(daily_sessions)
        retention_score = active_days / timeframe_days
        
        # Calculate consistency (how evenly distributed sessions are)
        if daily_sessions:
            session_counts = list(daily_sessions.values())
            consistency_score = 1.0 - (np.std(session_counts) / (np.mean(session_counts) + 1))
        else:
            consistency_score = 0.0
        
        return {
            'retention_score': retention_score,
            'consistency_score': max(0.0, consistency_score)
        }

    def _calculate_content_affinity(self, features: Dict[str, Any]) -> float:
        """Calculate user's affinity for different content types"""
        
        content_prefs = self._analyze_content_preferences({
            'content_categories': features.get('content_category_preferences', {}).keys()
        })
        
        if not content_prefs:
            return 0.0
        
        # Calculate entropy-based diversity score
        entropy = -sum(p * np.log2(p + 1e-10) for p in content_prefs.values())
        max_entropy = np.log2(len(content_prefs))
        
        return entropy / max_entropy if max_entropy > 0 else 0.0

    def _calculate_viral_participation(self, features: Dict[str, Any]) -> float:
        """Calculate user's participation in viral content"""
        
        total_shares = features.get('sharing_frequency', 0)
        total_interactions = features.get('total_interactions', 1)
        
        return min(1.0, total_shares / total_interactions)

    async def generate_behavior_insights(
        self,
        behavior_metrics: BehaviorMetrics
    ) -> List[BehaviorInsight]:
        """Generate actionable insights from behavior analysis"""
        
        insights = []
        
        # Engagement optimization insights
        if behavior_metrics.engagement_rate < 0.1:
            insights.append(BehaviorInsight(
                insight_type="engagement_opportunity",
                description="Low engagement rate suggests content mismatch with user preferences",
                confidence=0.8,
                impact_score=0.9,
                recommendations=[
                    "Analyze user's content category preferences",
                    "Adjust content recommendation algorithm",
                    "Test different content formats",
                    "Optimize posting times for user's active hours"
                ],
                target_segments=[behavior_metrics.behavior_pattern.value]
            ))
        
        # Viral potential insights
        if behavior_metrics.viral_participation_rate > 0.3:
            insights.append(BehaviorInsight(
                insight_type="viral_amplification",
                description="High viral participation indicates strong amplification potential",
                confidence=0.85,
                impact_score=0.95,
                recommendations=[
                    "Prioritize this user for viral content distribution",
                    "Include in early access programs",
                    "Target with trend-based content",
                    "Leverage for organic reach amplification"
                ],
                target_segments=[behavior_metrics.behavior_pattern.value]
            ))
        
        # Retention optimization
        if behavior_metrics.session_duration < 120:  # Less than 2 minutes
            insights.append(BehaviorInsight(
                insight_type="retention_risk",
                description="Short session duration indicates potential retention risk",
                confidence=0.75,
                impact_score=0.8,
                recommendations=[
                    "Implement progressive content revelation",
                    "Add interactive elements to increase engagement",
                    "Personalize content feed more aggressively",
                    "A/B test different content presentation formats"
                ],
                target_segments=[behavior_metrics.behavior_pattern.value]
            ))
        
        return insights