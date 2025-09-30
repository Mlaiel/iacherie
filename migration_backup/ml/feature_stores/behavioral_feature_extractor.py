#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🤖 ML Module - Behavioral Feature Extractor
User behavior feature extraction for engagement prediction

Ersteller: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel. Alle Rechte vorbehalten.
Version: 1.0.0
Letztes Update: Januar 2025

⚠️ WARNUNG: Dieser Code ist urheberrechtlich geschützt und vertraulich.
"""

import asyncio
import logging
import numpy as np
import pandas as pd
from dataclasses import dataclass
from typing import Dict, List, Optional, Any, Union, Tuple
from enum import Enum
import json
import time
from datetime import datetime, timedelta
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.feature_selection import SelectKBest, f_regression
from sklearn.decomposition import PCA
import scipy.stats as stats
from collections import defaultdict, Counter
import math

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BehaviorType(Enum):
    """Types of user behaviors to analyze."""
    ENGAGEMENT = "engagement"
    INTERACTION = "interaction"
    CONSUMPTION = "consumption"
    CREATION = "creation"
    SHARING = "sharing"
    TEMPORAL = "temporal"
    PREFERENCE = "preference"
    SENTIMENT = "sentiment"

class CreatorType(Enum):
    """Creator types for specialized behavior analysis."""
    MUSICIAN = "musician"
    BLOGGER = "blogger"
    PHOTOGRAPHER = "photographer"
    INFLUENCER = "influencer"
    COMEDIAN = "comedian"

class FeatureCategory(Enum):
    """Categories of behavioral features."""
    TEMPORAL_PATTERNS = "temporal_patterns"
    ENGAGEMENT_METRICS = "engagement_metrics"
    INTERACTION_DEPTH = "interaction_depth"
    CONTENT_PREFERENCE = "content_preference"
    SOCIAL_BEHAVIOR = "social_behavior"
    CONSUMPTION_PATTERNS = "consumption_patterns"
    CREATOR_AFFINITY = "creator_affinity"
    PLATFORM_BEHAVIOR = "platform_behavior"

@dataclass
class UserBehaviorData:
    """Container for user behavior data."""
    user_id: str
    timestamp: datetime
    behavior_type: BehaviorType
    content_id: Optional[str] = None
    creator_id: Optional[str] = None
    creator_type: Optional[CreatorType] = None
    platform: Optional[str] = None
    session_id: Optional[str] = None
    duration: Optional[float] = None
    engagement_score: Optional[float] = None
    interaction_data: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class BehavioralFeature:
    """Container for extracted behavioral feature."""
    feature_name: str
    feature_category: FeatureCategory
    feature_value: float
    importance_score: float
    creator_specific: bool = False
    temporal_weight: float = 1.0
    metadata: Optional[Dict[str, Any]] = None

class BehavioralFeatureExtractor:
    """
    🔬 ML ENGINEER - Advanced Behavioral Feature Extraction System
    
    Sophisticated user behavior analysis with creator-specific patterns,
    temporal dynamics, and engagement prediction features.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize behavioral feature extractor."""
        self.config = config or {}
        self.user_behavior_history: Dict[str, List[UserBehaviorData]] = defaultdict(list)
        self.creator_behavior_patterns: Dict[CreatorType, Dict[str, Any]] = {}
        self.feature_importance_scores: Dict[str, float] = {}
        self.extracted_features_cache: Dict[str, List[BehavioralFeature]] = {}
        
        # Feature extraction parameters
        self.temporal_window_days = self.config.get("temporal_window_days", 30)
        self.min_interactions_threshold = self.config.get("min_interactions_threshold", 5)
        self.feature_selection_k = self.config.get("feature_selection_k", 50)
        
        # Initialize logging
        logger.info("🔬 BehavioralFeatureExtractor initialized - ML Engineer expertise")
        
        # Initialize creator behavior patterns
        self._initialize_creator_patterns()
        
        # Setup feature extractors
        self._initialize_feature_extractors()
    
    def _initialize_creator_patterns(self):
        """Initialize creator-specific behavior patterns."""
        self.creator_behavior_patterns = {
            CreatorType.MUSICIAN: {
                "avg_session_duration": 240,  # seconds
                "peak_engagement_hours": [18, 19, 20, 21],
                "content_interaction_patterns": {
                    "listen_through_rate": 0.75,
                    "replay_rate": 0.35,
                    "skip_rate": 0.15,
                    "playlist_add_rate": 0.12
                },
                "engagement_weights": {
                    "likes": 1.0,
                    "shares": 2.5,
                    "comments": 3.0,
                    "saves": 2.0,
                    "follows": 5.0
                },
                "seasonality_factors": {
                    "weekend_boost": 1.3,
                    "evening_boost": 1.4,
                    "holiday_boost": 1.6
                }
            },
            CreatorType.BLOGGER: {
                "avg_session_duration": 180,
                "peak_engagement_hours": [8, 9, 12, 13, 19, 20],
                "content_interaction_patterns": {
                    "read_through_rate": 0.45,
                    "scroll_depth": 0.65,
                    "comment_rate": 0.08,
                    "share_rate": 0.15
                },
                "engagement_weights": {
                    "likes": 1.0,
                    "shares": 3.0,
                    "comments": 4.0,
                    "bookmarks": 2.5,
                    "subscribes": 6.0
                },
                "seasonality_factors": {
                    "weekday_boost": 1.2,
                    "morning_boost": 1.3,
                    "lunch_boost": 1.1
                }
            },
            CreatorType.PHOTOGRAPHER: {
                "avg_session_duration": 90,
                "peak_engagement_hours": [16, 17, 18, 19, 20, 21],
                "content_interaction_patterns": {
                    "view_time_ratio": 0.8,
                    "zoom_rate": 0.25,
                    "download_rate": 0.05,
                    "wallpaper_set_rate": 0.03
                },
                "engagement_weights": {
                    "likes": 1.0,
                    "shares": 2.0,
                    "comments": 2.5,
                    "saves": 3.0,
                    "follows": 4.0
                },
                "seasonality_factors": {
                    "weekend_boost": 1.5,
                    "golden_hour_boost": 1.8,
                    "season_boost": 1.2
                }
            },
            CreatorType.INFLUENCER: {
                "avg_session_duration": 120,
                "peak_engagement_hours": [10, 11, 15, 16, 19, 20, 21],
                "content_interaction_patterns": {
                    "story_completion_rate": 0.60,
                    "swipe_up_rate": 0.08,
                    "dm_rate": 0.02,
                    "tag_rate": 0.12
                },
                "engagement_weights": {
                    "likes": 1.0,
                    "shares": 2.8,
                    "comments": 3.5,
                    "story_replies": 4.0,
                    "follows": 5.5
                },
                "seasonality_factors": {
                    "trending_boost": 2.0,
                    "live_boost": 1.7,
                    "event_boost": 1.4
                }
            },
            CreatorType.COMEDIAN: {
                "avg_session_duration": 150,
                "peak_engagement_hours": [19, 20, 21, 22, 23],
                "content_interaction_patterns": {
                    "laugh_reaction_rate": 0.40,
                    "share_rate": 0.25,
                    "tag_friends_rate": 0.18,
                    "repeat_view_rate": 0.30
                },
                "engagement_weights": {
                    "likes": 1.0,
                    "laughs": 1.5,
                    "shares": 3.5,
                    "comments": 3.0,
                    "tags": 2.5
                },
                "seasonality_factors": {
                    "weekend_boost": 1.6,
                    "evening_boost": 1.8,
                    "friday_boost": 1.4
                }
            }
        }
    
    def _initialize_feature_extractors(self):
        """Initialize feature extraction functions."""
        self.feature_extractors = {
            FeatureCategory.TEMPORAL_PATTERNS: self._extract_temporal_features,
            FeatureCategory.ENGAGEMENT_METRICS: self._extract_engagement_features,
            FeatureCategory.INTERACTION_DEPTH: self._extract_interaction_depth_features,
            FeatureCategory.CONTENT_PREFERENCE: self._extract_content_preference_features,
            FeatureCategory.SOCIAL_BEHAVIOR: self._extract_social_behavior_features,
            FeatureCategory.CONSUMPTION_PATTERNS: self._extract_consumption_pattern_features,
            FeatureCategory.CREATOR_AFFINITY: self._extract_creator_affinity_features,
            FeatureCategory.PLATFORM_BEHAVIOR: self._extract_platform_behavior_features
        }
    
    async def log_user_behavior(
        self,
        user_id: str,
        behavior_type: BehaviorType,
        timestamp: Optional[datetime] = None,
        content_id: Optional[str] = None,
        creator_id: Optional[str] = None,
        creator_type: Optional[CreatorType] = None,
        platform: Optional[str] = None,
        session_id: Optional[str] = None,
        duration: Optional[float] = None,
        engagement_score: Optional[float] = None,
        interaction_data: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Log user behavior data for feature extraction.
        
        Args:
            user_id: Unique user identifier
            behavior_type: Type of behavior being logged
            timestamp: When the behavior occurred
            content_id: ID of content being interacted with
            creator_id: ID of content creator
            creator_type: Type of creator
            platform: Platform where behavior occurred
            session_id: Session identifier
            duration: Duration of interaction in seconds
            engagement_score: Calculated engagement score
            interaction_data: Additional interaction details
            metadata: Additional metadata
        """
        behavior_data = UserBehaviorData(
            user_id=user_id,
            timestamp=timestamp or datetime.now(),
            behavior_type=behavior_type,
            content_id=content_id,
            creator_id=creator_id,
            creator_type=creator_type,
            platform=platform,
            session_id=session_id,
            duration=duration,
            engagement_score=engagement_score,
            interaction_data=interaction_data or {},
            metadata=metadata or {}
        )
        
        self.user_behavior_history[user_id].append(behavior_data)
        
        # Maintain rolling window
        cutoff_date = datetime.now() - timedelta(days=self.temporal_window_days)
        self.user_behavior_history[user_id] = [
            b for b in self.user_behavior_history[user_id]
            if b.timestamp >= cutoff_date
        ]
        
        logger.info(f"📊 Behavior logged for user {user_id}: {behavior_type.value}")
    
    async def extract_user_features(
        self,
        user_id: str,
        feature_categories: Optional[List[FeatureCategory]] = None,
        creator_type: Optional[CreatorType] = None
    ) -> List[BehavioralFeature]:
        """
        Extract behavioral features for a specific user.
        
        Args:
            user_id: User to extract features for
            feature_categories: Specific categories to extract (all if None)
            creator_type: Creator type for specialized extraction
            
        Returns:
            List of extracted behavioral features
        """
        logger.info(f"🔬 Extracting behavioral features for user {user_id}")
        
        if user_id not in self.user_behavior_history:
            logger.warning(f"⚠️ No behavior history found for user {user_id}")
            return []
        
        user_behaviors = self.user_behavior_history[user_id]
        
        if len(user_behaviors) < self.min_interactions_threshold:
            logger.warning(f"⚠️ Insufficient interactions for user {user_id}")
            return []
        
        # Use all categories if none specified
        if feature_categories is None:
            feature_categories = list(FeatureCategory)
        
        # Extract features by category
        all_features = []
        
        for category in feature_categories:
            if category in self.feature_extractors:
                try:
                    features = await self.feature_extractors[category](
                        user_behaviors, creator_type
                    )
                    all_features.extend(features)
                except Exception as e:
                    logger.error(f"Error extracting {category.value} features: {e}")
        
        # Apply feature selection and importance scoring
        all_features = await self._apply_feature_selection(all_features, creator_type)
        
        # Cache features
        cache_key = f"{user_id}_{creator_type.value if creator_type else 'general'}"
        self.extracted_features_cache[cache_key] = all_features
        
        logger.info(f"✅ Extracted {len(all_features)} features for user {user_id}")
        return all_features
    
    async def _extract_temporal_features(
        self,
        user_behaviors: List[UserBehaviorData],
        creator_type: Optional[CreatorType]
    ) -> List[BehavioralFeature]:
        """Extract temporal behavior patterns."""
        features = []
        
        # Extract timestamps and group by patterns
        timestamps = [b.timestamp for b in user_behaviors]
        
        if not timestamps:
            return features
        
        # Hour of day patterns
        hours = [t.hour for t in timestamps]
        hour_distribution = Counter(hours)
        
        # Most active hour
        most_active_hour = hour_distribution.most_common(1)[0][0]
        features.append(BehavioralFeature(
            feature_name="most_active_hour",
            feature_category=FeatureCategory.TEMPORAL_PATTERNS,
            feature_value=float(most_active_hour),
            importance_score=0.8,
            creator_specific=creator_type is not None
        ))
        
        # Activity concentration (entropy of hour distribution)
        hour_probs = np.array(list(hour_distribution.values())) / sum(hour_distribution.values())
        hour_entropy = -np.sum(hour_probs * np.log2(hour_probs + 1e-10))
        features.append(BehavioralFeature(
            feature_name="activity_concentration",
            feature_category=FeatureCategory.TEMPORAL_PATTERNS,
            feature_value=24 - hour_entropy,  # Higher = more concentrated
            importance_score=0.7
        ))
        
        # Day of week patterns
        weekdays = [t.weekday() for t in timestamps]
        weekday_distribution = Counter(weekdays)
        
        # Weekend vs weekday preference
        weekend_count = weekday_distribution.get(5, 0) + weekday_distribution.get(6, 0)
        weekday_count = sum(weekday_distribution.values()) - weekend_count
        weekend_preference = weekend_count / (weekend_count + weekday_count + 1)
        
        features.append(BehavioralFeature(
            feature_name="weekend_preference",
            feature_category=FeatureCategory.TEMPORAL_PATTERNS,
            feature_value=weekend_preference,
            importance_score=0.6
        ))
        
        # Session patterns
        session_data = defaultdict(list)
        for behavior in user_behaviors:
            if behavior.session_id:
                session_data[behavior.session_id].append(behavior)
        
        if session_data:
            session_lengths = []
            for session_behaviors in session_data.values():
                if len(session_behaviors) > 1:
                    session_start = min(b.timestamp for b in session_behaviors)
                    session_end = max(b.timestamp for b in session_behaviors)
                    session_length = (session_end - session_start).total_seconds()
                    session_lengths.append(session_length)
            
            if session_lengths:
                avg_session_length = np.mean(session_lengths)
                features.append(BehavioralFeature(
                    feature_name="avg_session_duration",
                    feature_category=FeatureCategory.TEMPORAL_PATTERNS,
                    feature_value=avg_session_length,
                    importance_score=0.75
                ))
                
                session_consistency = 1.0 / (1.0 + np.std(session_lengths) / np.mean(session_lengths))
                features.append(BehavioralFeature(
                    feature_name="session_consistency",
                    feature_category=FeatureCategory.TEMPORAL_PATTERNS,
                    feature_value=session_consistency,
                    importance_score=0.65
                ))
        
        # Engagement time patterns (for creator-specific analysis)
        if creator_type and creator_type in self.creator_behavior_patterns:
            pattern = self.creator_behavior_patterns[creator_type]
            peak_hours = pattern["peak_engagement_hours"]
            
            peak_hour_activity = sum(1 for h in hours if h in peak_hours) / len(hours)
            features.append(BehavioralFeature(
                feature_name=f"{creator_type.value}_peak_hour_alignment",
                feature_category=FeatureCategory.TEMPORAL_PATTERNS,
                feature_value=peak_hour_activity,
                importance_score=0.85,
                creator_specific=True
            ))
        
        return features
    
    async def _extract_engagement_features(
        self,
        user_behaviors: List[UserBehaviorData],
        creator_type: Optional[CreatorType]
    ) -> List[BehavioralFeature]:
        """Extract engagement-based features."""
        features = []
        
        # Filter engagement behaviors
        engagement_behaviors = [
            b for b in user_behaviors 
            if b.behavior_type == BehaviorType.ENGAGEMENT and b.engagement_score is not None
        ]
        
        if not engagement_behaviors:
            return features
        
        engagement_scores = [b.engagement_score for b in engagement_behaviors]
        
        # Basic engagement statistics
        features.extend([
            BehavioralFeature(
                feature_name="avg_engagement_score",
                feature_category=FeatureCategory.ENGAGEMENT_METRICS,
                feature_value=np.mean(engagement_scores),
                importance_score=0.9
            ),
            BehavioralFeature(
                feature_name="max_engagement_score",
                feature_category=FeatureCategory.ENGAGEMENT_METRICS,
                feature_value=np.max(engagement_scores),
                importance_score=0.8
            ),
            BehavioralFeature(
                feature_name="engagement_consistency",
                feature_category=FeatureCategory.ENGAGEMENT_METRICS,
                feature_value=1.0 / (1.0 + np.std(engagement_scores)),
                importance_score=0.7
            )
        ])
        
        # Engagement growth trend
        if len(engagement_scores) >= 5:
            time_indices = np.arange(len(engagement_scores))
            correlation = np.corrcoef(time_indices, engagement_scores)[0, 1]
            
            features.append(BehavioralFeature(
                feature_name="engagement_growth_trend",
                feature_category=FeatureCategory.ENGAGEMENT_METRICS,
                feature_value=correlation,
                importance_score=0.75
            ))
        
        # High engagement frequency
        high_engagement_threshold = np.percentile(engagement_scores, 75)
        high_engagement_rate = sum(1 for score in engagement_scores if score >= high_engagement_threshold) / len(engagement_scores)
        
        features.append(BehavioralFeature(
            feature_name="high_engagement_frequency",
            feature_category=FeatureCategory.ENGAGEMENT_METRICS,
            feature_value=high_engagement_rate,
            importance_score=0.8
        ))
        
        # Creator-specific engagement patterns
        if creator_type:
            creator_engagement_behaviors = [
                b for b in engagement_behaviors 
                if b.creator_type == creator_type
            ]
            
            if creator_engagement_behaviors:
                creator_scores = [b.engagement_score for b in creator_engagement_behaviors]
                creator_avg = np.mean(creator_scores)
                
                features.append(BehavioralFeature(
                    feature_name=f"{creator_type.value}_engagement_score",
                    feature_category=FeatureCategory.ENGAGEMENT_METRICS,
                    feature_value=creator_avg,
                    importance_score=0.85,
                    creator_specific=True
                ))
                
                # Engagement preference for this creator type
                general_avg = np.mean(engagement_scores)
                preference_ratio = creator_avg / (general_avg + 1e-10)
                
                features.append(BehavioralFeature(
                    feature_name=f"{creator_type.value}_engagement_preference",
                    feature_category=FeatureCategory.ENGAGEMENT_METRICS,
                    feature_value=preference_ratio,
                    importance_score=0.8,
                    creator_specific=True
                ))
        
        return features
    
    async def _extract_interaction_depth_features(
        self,
        user_behaviors: List[UserBehaviorData],
        creator_type: Optional[CreatorType]
    ) -> List[BehavioralFeature]:
        """Extract interaction depth and quality features."""
        features = []
        
        # Filter interaction behaviors
        interaction_behaviors = [
            b for b in user_behaviors 
            if b.behavior_type == BehaviorType.INTERACTION and b.interaction_data
        ]
        
        if not interaction_behaviors:
            return features
        
        # Analyze interaction types and depths
        interaction_types = defaultdict(int)
        interaction_durations = []
        
        for behavior in interaction_behaviors:
            interaction_data = behavior.interaction_data
            
            # Count interaction types
            for interaction_type in interaction_data.keys():
                interaction_types[interaction_type] += 1
            
            # Collect durations
            if behavior.duration:
                interaction_durations.append(behavior.duration)
        
        # Interaction diversity (number of different interaction types)
        interaction_diversity = len(interaction_types)
        features.append(BehavioralFeature(
            feature_name="interaction_diversity",
            feature_category=FeatureCategory.INTERACTION_DEPTH,
            feature_value=float(interaction_diversity),
            importance_score=0.7
        ))
        
        # Most common interaction type frequency
        if interaction_types:
            most_common_freq = max(interaction_types.values()) / sum(interaction_types.values())
            features.append(BehavioralFeature(
                feature_name="primary_interaction_dominance",
                feature_category=FeatureCategory.INTERACTION_DEPTH,
                feature_value=most_common_freq,
                importance_score=0.6
            ))
        
        # Average interaction duration
        if interaction_durations:
            avg_duration = np.mean(interaction_durations)
            features.append(BehavioralFeature(
                feature_name="avg_interaction_duration",
                feature_category=FeatureCategory.INTERACTION_DEPTH,
                feature_value=avg_duration,
                importance_score=0.8
            ))
            
            # Interaction intensity (short vs long interactions)
            long_interaction_threshold = np.percentile(interaction_durations, 75)
            long_interaction_rate = sum(1 for d in interaction_durations if d >= long_interaction_threshold) / len(interaction_durations)
            
            features.append(BehavioralFeature(
                feature_name="deep_interaction_rate",
                feature_category=FeatureCategory.INTERACTION_DEPTH,
                feature_value=long_interaction_rate,
                importance_score=0.75
            ))
        
        # Creator-specific interaction patterns
        if creator_type and creator_type in self.creator_behavior_patterns:
            pattern = self.creator_behavior_patterns[creator_type]
            expected_patterns = pattern.get("content_interaction_patterns", {})
            
            for pattern_name, expected_rate in expected_patterns.items():
                actual_count = interaction_types.get(pattern_name, 0)
                total_interactions = sum(interaction_types.values())
                actual_rate = actual_count / (total_interactions + 1e-10)
                
                # Alignment with expected pattern
                alignment = 1.0 - abs(actual_rate - expected_rate)
                
                features.append(BehavioralFeature(
                    feature_name=f"{creator_type.value}_{pattern_name}_alignment",
                    feature_category=FeatureCategory.INTERACTION_DEPTH,
                    feature_value=max(0.0, alignment),
                    importance_score=0.7,
                    creator_specific=True
                ))
        
        return features
    
    async def _extract_content_preference_features(
        self,
        user_behaviors: List[UserBehaviorData],
        creator_type: Optional[CreatorType]
    ) -> List[BehavioralFeature]:
        """Extract content preference features."""
        features = []
        
        # Analyze content interactions
        content_interactions = defaultdict(list)
        creator_interactions = defaultdict(int)
        platform_interactions = defaultdict(int)
        
        for behavior in user_behaviors:
            if behavior.content_id:
                content_interactions[behavior.content_id].append(behavior)
            
            if behavior.creator_id:
                creator_interactions[behavior.creator_id] += 1
            
            if behavior.platform:
                platform_interactions[behavior.platform] += 1
        
        # Content diversity (number of unique contents interacted with)
        content_diversity = len(content_interactions)
        features.append(BehavioralFeature(
            feature_name="content_diversity",
            feature_category=FeatureCategory.CONTENT_PREFERENCE,
            feature_value=float(content_diversity),
            importance_score=0.7
        ))
        
        # Creator diversity
        creator_diversity = len(creator_interactions)
        features.append(BehavioralFeature(
            feature_name="creator_diversity",
            feature_category=FeatureCategory.CONTENT_PREFERENCE,
            feature_value=float(creator_diversity),
            importance_score=0.75
        ))
        
        # Content loyalty (interactions per content)
        if content_interactions:
            interactions_per_content = [len(interactions) for interactions in content_interactions.values()]
            avg_interactions_per_content = np.mean(interactions_per_content)
            
            features.append(BehavioralFeature(
                feature_name="content_loyalty",
                feature_category=FeatureCategory.CONTENT_PREFERENCE,
                feature_value=avg_interactions_per_content,
                importance_score=0.8
            ))
            
            # Content exploration vs exploitation
            single_interaction_contents = sum(1 for count in interactions_per_content if count == 1)
            exploration_rate = single_interaction_contents / len(interactions_per_content)
            
            features.append(BehavioralFeature(
                feature_name="content_exploration_rate",
                feature_category=FeatureCategory.CONTENT_PREFERENCE,
                feature_value=exploration_rate,
                importance_score=0.65
            ))
        
        # Creator loyalty
        if creator_interactions:
            creator_counts = list(creator_interactions.values())
            most_followed_creator_interactions = max(creator_counts)
            total_creator_interactions = sum(creator_counts)
            
            creator_loyalty = most_followed_creator_interactions / total_creator_interactions
            features.append(BehavioralFeature(
                feature_name="creator_loyalty",
                feature_category=FeatureCategory.CONTENT_PREFERENCE,
                feature_value=creator_loyalty,
                importance_score=0.8
            ))
        
        # Platform preference
        if platform_interactions:
            platform_counts = list(platform_interactions.values())
            total_platform_interactions = sum(platform_counts)
            
            # Platform diversity
            platform_diversity = len(platform_interactions)
            features.append(BehavioralFeature(
                feature_name="platform_diversity",
                feature_category=FeatureCategory.CONTENT_PREFERENCE,
                feature_value=float(platform_diversity),
                importance_score=0.6
            ))
            
            # Primary platform dominance
            primary_platform_dominance = max(platform_counts) / total_platform_interactions
            features.append(BehavioralFeature(
                feature_name="primary_platform_dominance",
                feature_category=FeatureCategory.CONTENT_PREFERENCE,
                feature_value=primary_platform_dominance,
                importance_score=0.7
            ))
        
        return features
    
    async def _extract_social_behavior_features(
        self,
        user_behaviors: List[UserBehaviorData],
        creator_type: Optional[CreatorType]
    ) -> List[BehavioralFeature]:
        """Extract social interaction features."""
        features = []
        
        # Filter sharing behaviors
        sharing_behaviors = [
            b for b in user_behaviors 
            if b.behavior_type == BehaviorType.SHARING
        ]
        
        if sharing_behaviors:
            # Sharing frequency
            total_behaviors = len(user_behaviors)
            sharing_rate = len(sharing_behaviors) / total_behaviors
            
            features.append(BehavioralFeature(
                feature_name="sharing_propensity",
                feature_category=FeatureCategory.SOCIAL_BEHAVIOR,
                feature_value=sharing_rate,
                importance_score=0.8
            ))
            
            # Time-based sharing patterns
            sharing_hours = [b.timestamp.hour for b in sharing_behaviors]
            if sharing_hours:
                sharing_hour_entropy = self._calculate_entropy(sharing_hours, 24)
                features.append(BehavioralFeature(
                    feature_name="sharing_time_diversity",
                    feature_category=FeatureCategory.SOCIAL_BEHAVIOR,
                    feature_value=sharing_hour_entropy,
                    importance_score=0.6
                ))
        
        # Analyze interaction metadata for social signals
        social_interactions = 0
        collaboration_signals = 0
        
        for behavior in user_behaviors:
            if behavior.interaction_data:
                # Count social interaction types
                social_types = ['comment', 'reply', 'mention', 'tag', 'collaborate']
                for social_type in social_types:
                    if social_type in behavior.interaction_data:
                        social_interactions += 1
                
                # Count collaboration signals
                collab_types = ['duet', 'remix', 'collab', 'feature']
                for collab_type in collab_types:
                    if collab_type in behavior.interaction_data:
                        collaboration_signals += 1
        
        if total_behaviors > 0:
            social_interaction_rate = social_interactions / total_behaviors
            collaboration_rate = collaboration_signals / total_behaviors
            
            features.extend([
                BehavioralFeature(
                    feature_name="social_interaction_rate",
                    feature_category=FeatureCategory.SOCIAL_BEHAVIOR,
                    feature_value=social_interaction_rate,
                    importance_score=0.75
                ),
                BehavioralFeature(
                    feature_name="collaboration_propensity",
                    feature_category=FeatureCategory.SOCIAL_BEHAVIOR,
                    feature_value=collaboration_rate,
                    importance_score=0.7
                )
            ])
        
        return features
    
    async def _extract_consumption_pattern_features(
        self,
        user_behaviors: List[UserBehaviorData],
        creator_type: Optional[CreatorType]
    ) -> List[BehavioralFeature]:
        """Extract content consumption pattern features."""
        features = []
        
        # Filter consumption behaviors
        consumption_behaviors = [
            b for b in user_behaviors 
            if b.behavior_type == BehaviorType.CONSUMPTION and b.duration is not None
        ]
        
        if not consumption_behaviors:
            return features
        
        durations = [b.duration for b in consumption_behaviors]
        
        # Basic consumption statistics
        features.extend([
            BehavioralFeature(
                feature_name="avg_consumption_duration",
                feature_category=FeatureCategory.CONSUMPTION_PATTERNS,
                feature_value=np.mean(durations),
                importance_score=0.8
            ),
            BehavioralFeature(
                feature_name="consumption_consistency",
                feature_category=FeatureCategory.CONSUMPTION_PATTERNS,
                feature_value=1.0 / (1.0 + np.std(durations) / (np.mean(durations) + 1e-10)),
                importance_score=0.7
            )
        ])
        
        # Consumption intensity patterns
        short_threshold = np.percentile(durations, 33)
        long_threshold = np.percentile(durations, 67)
        
        short_consumption_rate = sum(1 for d in durations if d <= short_threshold) / len(durations)
        long_consumption_rate = sum(1 for d in durations if d >= long_threshold) / len(durations)
        
        features.extend([
            BehavioralFeature(
                feature_name="quick_consumption_rate",
                feature_category=FeatureCategory.CONSUMPTION_PATTERNS,
                feature_value=short_consumption_rate,
                importance_score=0.6
            ),
            BehavioralFeature(
                feature_name="deep_consumption_rate",
                feature_category=FeatureCategory.CONSUMPTION_PATTERNS,
                feature_value=long_consumption_rate,
                importance_score=0.75
            )
        ])
        
        # Binge consumption detection
        consumption_times = [b.timestamp for b in consumption_behaviors]
        if len(consumption_times) >= 3:
            time_diffs = [
                (consumption_times[i+1] - consumption_times[i]).total_seconds() 
                for i in range(len(consumption_times)-1)
            ]
            
            # Binge sessions (consumptions within 1 hour of each other)
            binge_threshold = 3600  # 1 hour
            binge_count = sum(1 for diff in time_diffs if diff <= binge_threshold)
            binge_rate = binge_count / len(time_diffs)
            
            features.append(BehavioralFeature(
                feature_name="binge_consumption_tendency",
                feature_category=FeatureCategory.CONSUMPTION_PATTERNS,
                feature_value=binge_rate,
                importance_score=0.7
            ))
        
        # Creator-specific consumption patterns
        if creator_type and creator_type in self.creator_behavior_patterns:
            pattern = self.creator_behavior_patterns[creator_type]
            expected_duration = pattern.get("avg_session_duration", 120)
            
            actual_avg_duration = np.mean(durations)
            duration_alignment = 1.0 - abs(actual_avg_duration - expected_duration) / expected_duration
            
            features.append(BehavioralFeature(
                feature_name=f"{creator_type.value}_consumption_alignment",
                feature_category=FeatureCategory.CONSUMPTION_PATTERNS,
                feature_value=max(0.0, duration_alignment),
                importance_score=0.8,
                creator_specific=True
            ))
        
        return features
    
    async def _extract_creator_affinity_features(
        self,
        user_behaviors: List[UserBehaviorData],
        creator_type: Optional[CreatorType]
    ) -> List[BehavioralFeature]:
        """Extract creator affinity and preference features."""
        features = []
        
        # Analyze creator type preferences
        creator_type_interactions = defaultdict(int)
        creator_type_engagement = defaultdict(list)
        
        for behavior in user_behaviors:
            if behavior.creator_type:
                creator_type_interactions[behavior.creator_type] += 1
                
                if behavior.engagement_score is not None:
                    creator_type_engagement[behavior.creator_type].append(behavior.engagement_score)
        
        if creator_type_interactions:
            total_creator_interactions = sum(creator_type_interactions.values())
            
            # Creator type diversity
            creator_type_diversity = len(creator_type_interactions)
            features.append(BehavioralFeature(
                feature_name="creator_type_diversity",
                feature_category=FeatureCategory.CREATOR_AFFINITY,
                feature_value=float(creator_type_diversity),
                importance_score=0.7
            ))
            
            # Specific creator type affinities
            for ctype, count in creator_type_interactions.items():
                affinity_score = count / total_creator_interactions
                
                features.append(BehavioralFeature(
                    feature_name=f"{ctype.value}_affinity",
                    feature_category=FeatureCategory.CREATOR_AFFINITY,
                    feature_value=affinity_score,
                    importance_score=0.8,
                    creator_specific=(ctype == creator_type)
                ))
            
            # Creator type engagement quality
            for ctype, engagement_scores in creator_type_engagement.items():
                if engagement_scores:
                    avg_engagement = np.mean(engagement_scores)
                    
                    features.append(BehavioralFeature(
                        feature_name=f"{ctype.value}_engagement_quality",
                        feature_category=FeatureCategory.CREATOR_AFFINITY,
                        feature_value=avg_engagement,
                        importance_score=0.85,
                        creator_specific=(ctype == creator_type)
                    ))
        
        # Cross-creator behavior analysis
        if creator_type:
            creator_type_behaviors = [
                b for b in user_behaviors 
                if b.creator_type == creator_type
            ]
            
            other_type_behaviors = [
                b for b in user_behaviors 
                if b.creator_type and b.creator_type != creator_type
            ]
            
            if creator_type_behaviors and other_type_behaviors:
                # Loyalty to specific creator type
                loyalty_score = len(creator_type_behaviors) / len(user_behaviors)
                
                features.append(BehavioralFeature(
                    feature_name=f"{creator_type.value}_loyalty",
                    feature_category=FeatureCategory.CREATOR_AFFINITY,
                    feature_value=loyalty_score,
                    importance_score=0.9,
                    creator_specific=True
                ))
                
                # Engagement comparison
                creator_type_engagement_scores = [
                    b.engagement_score for b in creator_type_behaviors 
                    if b.engagement_score is not None
                ]
                other_type_engagement_scores = [
                    b.engagement_score for b in other_type_behaviors 
                    if b.engagement_score is not None
                ]
                
                if creator_type_engagement_scores and other_type_engagement_scores:
                    relative_engagement = (
                        np.mean(creator_type_engagement_scores) / 
                        (np.mean(other_type_engagement_scores) + 1e-10)
                    )
                    
                    features.append(BehavioralFeature(
                        feature_name=f"{creator_type.value}_relative_engagement",
                        feature_category=FeatureCategory.CREATOR_AFFINITY,
                        feature_value=relative_engagement,
                        importance_score=0.85,
                        creator_specific=True
                    ))
        
        return features
    
    async def _extract_platform_behavior_features(
        self,
        user_behaviors: List[UserBehaviorData],
        creator_type: Optional[CreatorType]
    ) -> List[BehavioralFeature]:
        """Extract platform-specific behavior features."""
        features = []
        
        # Analyze platform usage patterns
        platform_interactions = defaultdict(int)
        platform_durations = defaultdict(list)
        platform_engagement = defaultdict(list)
        
        for behavior in user_behaviors:
            if behavior.platform:
                platform_interactions[behavior.platform] += 1
                
                if behavior.duration:
                    platform_durations[behavior.platform].append(behavior.duration)
                
                if behavior.engagement_score is not None:
                    platform_engagement[behavior.platform].append(behavior.engagement_score)
        
        if platform_interactions:
            total_platform_interactions = sum(platform_interactions.values())
            
            # Platform usage distribution
            for platform, count in platform_interactions.items():
                usage_rate = count / total_platform_interactions
                
                features.append(BehavioralFeature(
                    feature_name=f"{platform}_usage_rate",
                    feature_category=FeatureCategory.PLATFORM_BEHAVIOR,
                    feature_value=usage_rate,
                    importance_score=0.7
                ))
            
            # Platform engagement quality
            for platform, engagement_scores in platform_engagement.items():
                if engagement_scores:
                    avg_engagement = np.mean(engagement_scores)
                    
                    features.append(BehavioralFeature(
                        feature_name=f"{platform}_engagement_quality",
                        feature_category=FeatureCategory.PLATFORM_BEHAVIOR,
                        feature_value=avg_engagement,
                        importance_score=0.75
                    ))
            
            # Platform session characteristics
            for platform, durations in platform_durations.items():
                if durations:
                    avg_duration = np.mean(durations)
                    
                    features.append(BehavioralFeature(
                        feature_name=f"{platform}_avg_session_duration",
                        feature_category=FeatureCategory.PLATFORM_BEHAVIOR,
                        feature_value=avg_duration,
                        importance_score=0.65
                    ))
        
        # Cross-platform behavior analysis
        if len(platform_interactions) > 1:
            # Platform switching behavior
            platform_switches = 0
            previous_platform = None
            
            for behavior in sorted(user_behaviors, key=lambda x: x.timestamp):
                if behavior.platform and behavior.platform != previous_platform:
                    if previous_platform is not None:
                        platform_switches += 1
                    previous_platform = behavior.platform
            
            switch_rate = platform_switches / len(user_behaviors) if user_behaviors else 0
            
            features.append(BehavioralFeature(
                feature_name="platform_switching_rate",
                feature_category=FeatureCategory.PLATFORM_BEHAVIOR,
                feature_value=switch_rate,
                importance_score=0.6
            ))
        
        return features
    
    def _calculate_entropy(self, values: List[int], max_value: int) -> float:
        """Calculate entropy of a discrete distribution."""
        if not values:
            return 0.0
        
        counts = Counter(values)
        total = len(values)
        
        entropy = 0.0
        for count in counts.values():
            prob = count / total
            entropy -= prob * math.log2(prob)
        
        # Normalize by maximum possible entropy
        max_entropy = math.log2(max_value)
        return entropy / max_entropy if max_entropy > 0 else 0.0
    
    async def _apply_feature_selection(
        self,
        features: List[BehavioralFeature],
        creator_type: Optional[CreatorType]
    ) -> List[BehavioralFeature]:
        """Apply feature selection and importance scoring."""
        if not features:
            return features
        
        # Sort by importance score
        features.sort(key=lambda f: f.importance_score, reverse=True)
        
        # Apply creator-specific boost
        if creator_type:
            for feature in features:
                if feature.creator_specific:
                    feature.importance_score *= 1.2  # Boost creator-specific features
        
        # Apply temporal weighting (more recent behaviors have higher weight)
        # This would require access to recency information
        
        # Select top K features
        selected_features = features[:self.feature_selection_k]
        
        # Update feature importance scores in global tracker
        for feature in selected_features:
            self.feature_importance_scores[feature.feature_name] = feature.importance_score
        
        return selected_features
    
    async def extract_batch_features(
        self,
        user_ids: List[str],
        feature_categories: Optional[List[FeatureCategory]] = None,
        creator_type: Optional[CreatorType] = None
    ) -> Dict[str, List[BehavioralFeature]]:
        """
        Extract features for multiple users in batch.
        
        Args:
            user_ids: List of user IDs to process
            feature_categories: Feature categories to extract
            creator_type: Creator type for specialized extraction
            
        Returns:
            Dictionary mapping user IDs to their extracted features
        """
        logger.info(f"🔬 Batch feature extraction for {len(user_ids)} users")
        
        # Create batch extraction tasks
        tasks = [
            self.extract_user_features(user_id, feature_categories, creator_type)
            for user_id in user_ids
        ]
        
        # Execute batch extraction
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Compile results
        batch_features = {}
        successful_extractions = 0
        
        for user_id, result in zip(user_ids, results):
            if isinstance(result, Exception):
                logger.error(f"Error extracting features for user {user_id}: {result}")
                batch_features[user_id] = []
            else:
                batch_features[user_id] = result
                successful_extractions += 1
        
        logger.info(f"✅ Batch extraction completed: {successful_extractions}/{len(user_ids)} successful")
        return batch_features
    
    async def generate_feature_importance_report(self) -> Dict[str, Any]:
        """Generate feature importance analysis report."""
        logger.info("📊 Generating feature importance report")
        
        if not self.feature_importance_scores:
            return {"error": "No feature importance data available"}
        
        # Sort features by importance
        sorted_features = sorted(
            self.feature_importance_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        # Analyze feature categories
        category_importance = defaultdict(list)
        for feature_name, importance in sorted_features:
            # Extract category from feature name (simplified)
            category = "unknown"
            for cat in FeatureCategory:
                if cat.value in feature_name:
                    category = cat.value
                    break
            category_importance[category].append(importance)
        
        category_averages = {
            cat: np.mean(scores) 
            for cat, scores in category_importance.items()
        }
        
        report = {
            "report_metadata": {
                "generated_at": datetime.now().isoformat(),
                "total_features_analyzed": len(sorted_features),
                "feature_categories_found": len(category_averages)
            },
            "top_features": [
                {"feature_name": name, "importance_score": score}
                for name, score in sorted_features[:20]
            ],
            "category_importance": category_averages,
            "feature_statistics": {
                "max_importance": max(self.feature_importance_scores.values()),
                "min_importance": min(self.feature_importance_scores.values()),
                "avg_importance": np.mean(list(self.feature_importance_scores.values())),
                "std_importance": np.std(list(self.feature_importance_scores.values()))
            },
            "recommendations": self._generate_feature_recommendations(sorted_features, category_averages)
        }
        
        logger.info("✅ Feature importance report generated")
        return report
    
    def _generate_feature_recommendations(
        self,
        sorted_features: List[Tuple[str, float]],
        category_averages: Dict[str, float]
    ) -> List[str]:
        """Generate recommendations based on feature analysis."""
        recommendations = []
        
        # High importance features
        high_importance_features = [f for f, s in sorted_features if s > 0.8]
        if high_importance_features:
            recommendations.append(
                f"Focus on {len(high_importance_features)} high-impact features for model development"
            )
        
        # Best performing categories
        best_categories = sorted(category_averages.items(), key=lambda x: x[1], reverse=True)[:3]
        recommendations.append(
            f"Top performing feature categories: {', '.join([cat for cat, _ in best_categories])}"
        )
        
        # Feature engineering opportunities
        if category_averages.get("temporal_patterns", 0) < 0.6:
            recommendations.append("Consider enhancing temporal pattern features")
        
        if category_averages.get("creator_affinity", 0) > 0.8:
            recommendations.append("Creator affinity features are highly predictive - expand this category")
        
        return recommendations

# Export main class
__all__ = ['BehavioralFeatureExtractor', 'BehaviorType', 'CreatorType', 'FeatureCategory', 'UserBehaviorData', 'BehavioralFeature']

if __name__ == "__main__":
    # Test the behavioral feature extractor
    async def test_behavioral_feature_extractor():
        extractor = BehavioralFeatureExtractor()
        
        # Simulate user behavior data
        user_id = "test_user_123"
        
        # Log various behaviors
        behaviors_to_log = [
            (BehaviorType.ENGAGEMENT, CreatorType.MUSICIAN, 45.0, 0.8, {"like": True, "share": True}),
            (BehaviorType.CONSUMPTION, CreatorType.MUSICIAN, 180.0, 0.7, {"play_duration": 180}),
            (BehaviorType.INTERACTION, CreatorType.BLOGGER, 30.0, 0.6, {"comment": True, "scroll_depth": 0.8}),
            (BehaviorType.SHARING, CreatorType.PHOTOGRAPHER, 10.0, 0.9, {"platform": "instagram"}),
            (BehaviorType.ENGAGEMENT, CreatorType.INFLUENCER, 25.0, 0.75, {"story_view": True}),
        ]
        
        for i, (behavior_type, creator_type, duration, engagement, interaction_data) in enumerate(behaviors_to_log):
            await extractor.log_user_behavior(
                user_id=user_id,
                behavior_type=behavior_type,
                timestamp=datetime.now() - timedelta(hours=i),
                content_id=f"content_{i}",
                creator_id=f"creator_{i}",
                creator_type=creator_type,
                platform="test_platform",
                session_id=f"session_{i//2}",  # Group behaviors into sessions
                duration=duration,
                engagement_score=engagement,
                interaction_data=interaction_data
            )
        
        # Extract features for musician content
        musician_features = await extractor.extract_user_features(
            user_id=user_id,
            creator_type=CreatorType.MUSICIAN
        )
        
        print(f"✅ Extracted {len(musician_features)} features for musician content")
        
        # Display some features
        for feature in musician_features[:10]:
            print(f"  - {feature.feature_name}: {feature.feature_value:.3f} (importance: {feature.importance_score:.3f})")
        
        # Test batch extraction
        batch_results = await extractor.extract_batch_features(
            user_ids=[user_id, "test_user_456"],
            creator_type=CreatorType.MUSICIAN
        )
        
        print(f"✅ Batch extraction completed for {len(batch_results)} users")
        
        # Generate importance report
        importance_report = await extractor.generate_feature_importance_report()
        
        print(f"📊 Feature importance report: {len(importance_report.get('top_features', []))} top features analyzed")
        
        print("✅ BehavioralFeatureExtractor test completed successfully!")
    
    # Run test
    asyncio.run(test_behavioral_feature_extractor())