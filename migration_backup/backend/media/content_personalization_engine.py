"""Content Personalization Engine - AI-Powered Content Personalization System
=========================================================================

Advanced personalization engine providing intelligent content recommendation,
user behavior analysis, and personalized content delivery optimization.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ CRITICAL LEGAL WARNING ⚠️
This proprietary personalization system contains advanced algorithms and trade secrets
belonging exclusively to Fahed Mlaiel (mlaiel@live.de).

UNAUTHORIZED USE IS STRICTLY PROHIBITED:
- Code theft, copying, or reverse engineering  
- Commercial use without explicit written permission
- Algorithm extraction or AI personalization logic appropriation
- Distribution without proper licensing

Contact mlaiel@live.de for licensing and authorization inquiries.
"""

import asyncio
import json
import logging
import uuid
import hashlib
import math
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple, Union, Set
from collections import defaultdict, Counter
import statistics

# AI and ML imports with graceful fallbacks
try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False
    logging.warning("NumPy not available - using basic calculations")

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    from sklearn.cluster import KMeans
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False
    logging.warning("Scikit-learn not available - using basic similarity calculations")

try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False
    logging.warning("Pandas not available - using basic data structures")

logger = logging.getLogger(__name__)


class PersonalizationType(Enum):
    """Personalization types"""
    CONTENT_BASED = "content_based"
    COLLABORATIVE = "collaborative"
    HYBRID = "hybrid"
    BEHAVIORAL = "behavioral"
    DEMOGRAPHIC = "demographic"
    CONTEXTUAL = "contextual"


class InteractionType(Enum):
    """User interaction types"""
    VIEW = "view"
    LIKE = "like"
    SHARE = "share"
    COMMENT = "comment"
    BOOKMARK = "bookmark"
    DOWNLOAD = "download"
    SKIP = "skip"
    DISLIKE = "dislike"
    REPORT = "report"


class ContentCategory(Enum):
    """Content categories"""
    VIDEO = "video"
    AUDIO = "audio"
    IMAGE = "image"
    TEXT = "text"
    LIVE_STREAM = "live_stream"
    PODCAST = "podcast"
    ARTICLE = "article"
    TUTORIAL = "tutorial"
    ENTERTAINMENT = "entertainment"
    NEWS = "news"
    EDUCATIONAL = "educational"
    MUSIC = "music"


class PersonalizationScope(Enum):
    """Personalization scope"""
    GLOBAL = "global"
    CATEGORY = "category"
    TOPIC = "topic"
    CREATOR = "creator"
    PLATFORM = "platform"
    TIME_BASED = "time_based"


@dataclass
class PersonalizationConfig:
    """Personalization engine configuration"""
    # Algorithm settings
    recommendation_count: int = 20
    min_interactions_for_personalization: int = 5
    content_similarity_threshold: float = 0.3
    user_similarity_threshold: float = 0.2
    
    # Weighting factors
    recency_weight: float = 0.3
    popularity_weight: float = 0.2
    similarity_weight: float = 0.3
    diversity_weight: float = 0.2
    
    # Privacy and data settings
    anonymize_user_data: bool = True
    data_retention_days: int = 365
    enable_cross_platform_personalization: bool = True
    
    # Performance settings
    cache_recommendations: bool = True
    cache_ttl_seconds: int = 3600
    max_user_history_items: int = 1000
    
    # Real-time settings
    real_time_updates: bool = True
    interaction_decay_rate: float = 0.1  # How fast interactions lose weight over time


@dataclass
class UserProfile:
    """User profile for personalization"""
    user_id: str
    demographics: Dict[str, Any] = field(default_factory=dict)
    preferences: Dict[str, float] = field(default_factory=dict)  # category -> preference score
    interests: List[str] = field(default_factory=list)
    interaction_history: List['UserInteraction'] = field(default_factory=list)
    content_consumption_patterns: Dict[str, Any] = field(default_factory=dict)
    engagement_score: float = 0.0
    last_active: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class UserInteraction:
    """User interaction with content"""
    interaction_id: str
    user_id: str
    content_id: str
    interaction_type: InteractionType
    timestamp: datetime
    duration: Optional[float] = None  # seconds
    context: Dict[str, Any] = field(default_factory=dict)
    device_type: Optional[str] = None
    location: Optional[str] = None
    session_id: Optional[str] = None


@dataclass
class ContentItem:
    """Content item for personalization"""
    content_id: str
    title: str
    description: str
    category: ContentCategory
    tags: List[str] = field(default_factory=list)
    creator_id: Optional[str] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    duration: Optional[float] = None
    language: str = "en"
    quality_score: float = 0.5
    popularity_score: float = 0.0
    engagement_metrics: Dict[str, int] = field(default_factory=dict)
    features: Dict[str, float] = field(default_factory=dict)  # Extracted features for ML
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PersonalizationResult:
    """Personalization result"""
    user_id: str
    recommendations: List[Dict[str, Any]]
    personalization_type: PersonalizationType
    confidence_score: float
    diversity_score: float
    freshness_score: float
    explanation: Dict[str, Any]
    generated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    ttl: datetime = field(default_factory=lambda: datetime.now(timezone.utc) + timedelta(hours=1))


class UserBehaviorAnalyzer:
    """Analyzes user behavior patterns for personalization"""
    
    def __init__(self, config: PersonalizationConfig):
        self.config = config
        self.user_profiles: Dict[str, UserProfile] = {}
        self.interaction_cache = defaultdict(list)
        
        logger.info("👤 User Behavior Analyzer initialized")
    
    async def analyze_user_behavior(self, user_id: str) -> Dict[str, Any]:
        """Analyze user behavior patterns"""
        try:
            profile = self.user_profiles.get(user_id)
            if not profile:
                return {'error': f'User profile {user_id} not found'}
            
            # Analyze interaction patterns
            patterns = await self._analyze_interaction_patterns(profile)
            
            # Analyze content preferences
            preferences = await self._analyze_content_preferences(profile)
            
            # Analyze temporal patterns
            temporal_patterns = await self._analyze_temporal_patterns(profile)
            
            # Calculate engagement metrics
            engagement_metrics = await self._calculate_engagement_metrics(profile)
            
            return {
                'user_id': user_id,
                'interaction_patterns': patterns,
                'content_preferences': preferences,
                'temporal_patterns': temporal_patterns,
                'engagement_metrics': engagement_metrics,
                'profile_completeness': self._calculate_profile_completeness(profile),
                'analysis_timestamp': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"User behavior analysis failed for {user_id}: {e}")
            return {'error': str(e)}
    
    async def update_user_profile(self, interaction: UserInteraction):
        """Update user profile based on new interaction"""
        try:
            user_id = interaction.user_id
            
            # Get or create user profile
            if user_id not in self.user_profiles:
                self.user_profiles[user_id] = UserProfile(user_id=user_id)
            
            profile = self.user_profiles[user_id]
            
            # Add interaction to history
            profile.interaction_history.append(interaction)
            
            # Limit history size
            if len(profile.interaction_history) > self.config.max_user_history_items:
                profile.interaction_history = profile.interaction_history[-self.config.max_user_history_items:]
            
            # Update preferences based on interaction
            await self._update_preferences(profile, interaction)
            
            # Update engagement score
            await self._update_engagement_score(profile, interaction)
            
            # Update temporal patterns
            await self._update_temporal_patterns(profile, interaction)
            
            profile.updated_at = datetime.now(timezone.utc)
            profile.last_active = interaction.timestamp
            
        except Exception as e:
            logger.error(f"Failed to update user profile: {e}")
    
    async def _analyze_interaction_patterns(self, profile: UserProfile) -> Dict[str, Any]:
        """Analyze user interaction patterns"""
        if not profile.interaction_history:
            return {}
        
        interactions = profile.interaction_history
        
        # Interaction type distribution
        type_counts = Counter(i.interaction_type.value for i in interactions)
        total_interactions = len(interactions)
        
        type_distribution = {
            itype: count / total_interactions 
            for itype, count in type_counts.items()
        }
        
        # Average session duration
        session_durations = [i.duration for i in interactions if i.duration]
        avg_duration = statistics.mean(session_durations) if session_durations else 0
        
        # Interaction frequency
        if len(interactions) >= 2:
            time_diffs = []
            for i in range(1, len(interactions)):
                diff = (interactions[i].timestamp - interactions[i-1].timestamp).total_seconds()
                time_diffs.append(diff)
            
            avg_frequency = statistics.mean(time_diffs) if time_diffs else 0
        else:
            avg_frequency = 0
        
        return {
            'total_interactions': total_interactions,
            'interaction_type_distribution': type_distribution,
            'average_session_duration': avg_duration,
            'average_interaction_frequency_seconds': avg_frequency,
            'most_common_interaction': type_counts.most_common(1)[0][0] if type_counts else None
        }
    
    async def _analyze_content_preferences(self, profile: UserProfile) -> Dict[str, float]:
        """Analyze user content preferences"""
        if not profile.interaction_history:
            return {}
        
        # Weight interactions by type and recency
        preference_scores = defaultdict(float)
        
        for interaction in profile.interaction_history:
            # Calculate weight based on interaction type
            weight = self._get_interaction_weight(interaction.interaction_type)
            
            # Apply recency decay
            days_ago = (datetime.now(timezone.utc) - interaction.timestamp).days
            recency_factor = math.exp(-days_ago * self.config.interaction_decay_rate)
            
            # Add duration factor
            duration_factor = 1.0
            if interaction.duration:
                # Normalize duration (assuming 0-300 seconds is typical)
                duration_factor = min(interaction.duration / 300, 2.0)
            
            final_weight = weight * recency_factor * duration_factor
            
            # Update preference scores (would use actual content category)
            preference_scores['general'] += final_weight
        
        # Normalize scores
        max_score = max(preference_scores.values()) if preference_scores else 1
        normalized_preferences = {
            category: score / max_score 
            for category, score in preference_scores.items()
        }
        
        return normalized_preferences
    
    async def _analyze_temporal_patterns(self, profile: UserProfile) -> Dict[str, Any]:
        """Analyze user temporal activity patterns"""
        if not profile.interaction_history:
            return {}
        
        # Hour of day distribution
        hour_counts = defaultdict(int)
        day_counts = defaultdict(int)
        
        for interaction in profile.interaction_history:
            hour = interaction.timestamp.hour
            day = interaction.timestamp.strftime('%A')
            
            hour_counts[hour] += 1
            day_counts[day] += 1
        
        # Find peak activity times
        peak_hour = max(hour_counts, key=hour_counts.get) if hour_counts else 12
        peak_day = max(day_counts, key=day_counts.get) if day_counts else 'Monday'
        
        return {
            'peak_activity_hour': peak_hour,
            'peak_activity_day': peak_day,
            'hourly_distribution': dict(hour_counts),
            'daily_distribution': dict(day_counts),
            'activity_consistency': self._calculate_activity_consistency(profile.interaction_history)
        }
    
    async def _calculate_engagement_metrics(self, profile: UserProfile) -> Dict[str, float]:
        """Calculate user engagement metrics"""
        if not profile.interaction_history:
            return {'engagement_score': 0.0}
        
        interactions = profile.interaction_history
        
        # Calculate various engagement indicators
        positive_interactions = len([
            i for i in interactions 
            if i.interaction_type in [InteractionType.LIKE, InteractionType.SHARE, InteractionType.BOOKMARK]
        ])
        
        negative_interactions = len([
            i for i in interactions 
            if i.interaction_type in [InteractionType.DISLIKE, InteractionType.SKIP, InteractionType.REPORT]
        ])
        
        total_interactions = len(interactions)
        
        # Engagement rate
        engagement_rate = positive_interactions / total_interactions if total_interactions > 0 else 0
        
        # Activity level (interactions per day)
        days_active = (datetime.now(timezone.utc) - profile.created_at).days or 1
        activity_level = total_interactions / days_active
        
        # Overall engagement score
        engagement_score = (engagement_rate * 0.6 + min(activity_level / 10, 1.0) * 0.4)
        
        return {
            'engagement_score': engagement_score,
            'engagement_rate': engagement_rate,
            'activity_level': activity_level,
            'positive_interactions': positive_interactions,
            'negative_interactions': negative_interactions
        }
    
    def _get_interaction_weight(self, interaction_type: InteractionType) -> float:
        """Get weight for interaction type"""
        weights = {
            InteractionType.VIEW: 1.0,
            InteractionType.LIKE: 2.0,
            InteractionType.SHARE: 3.0,
            InteractionType.COMMENT: 2.5,
            InteractionType.BOOKMARK: 2.5,
            InteractionType.DOWNLOAD: 3.0,
            InteractionType.SKIP: -1.0,
            InteractionType.DISLIKE: -2.0,
            InteractionType.REPORT: -3.0
        }
        return weights.get(interaction_type, 1.0)
    
    def _calculate_activity_consistency(self, interactions: List[UserInteraction]) -> float:
        """Calculate how consistent user activity is over time"""
        if len(interactions) < 2:
            return 0.0
        
        # Calculate daily interaction counts
        daily_counts = defaultdict(int)
        for interaction in interactions:
            date_key = interaction.timestamp.date()
            daily_counts[date_key] += 1
        
        # Calculate consistency (inverse of variance)
        counts = list(daily_counts.values())
        if len(counts) < 2:
            return 1.0
        
        variance = statistics.variance(counts)
        consistency = 1.0 / (1.0 + variance)
        
        return consistency
    
    def _calculate_profile_completeness(self, profile: UserProfile) -> float:
        """Calculate how complete a user profile is"""
        completeness_factors = [
            1.0 if profile.demographics else 0.0,
            1.0 if profile.preferences else 0.0,
            1.0 if profile.interests else 0.0,
            1.0 if len(profile.interaction_history) >= self.config.min_interactions_for_personalization else 0.0,
            1.0 if profile.content_consumption_patterns else 0.0
        ]
        
        return sum(completeness_factors) / len(completeness_factors)


class ContentRecommendationEngine:
    """Content recommendation engine using various algorithms"""
    
    def __init__(self, config: PersonalizationConfig):
        self.config = config
        self.content_catalog: Dict[str, ContentItem] = {}
        self.user_item_matrix = {}
        self.content_features = {}
        self.recommendation_cache = {}
        
        logger.info("🎯 Content Recommendation Engine initialized")
    
    async def generate_recommendations(
        self,
        user_id: str,
        user_profile: UserProfile,
        personalization_type: PersonalizationType = PersonalizationType.HYBRID,
        scope: PersonalizationScope = PersonalizationScope.GLOBAL,
        count: Optional[int] = None
    ) -> PersonalizationResult:
        """Generate personalized content recommendations"""
        try:
            recommendation_count = count or self.config.recommendation_count
            
            # Check cache first
            cache_key = f"{user_id}_{personalization_type.value}_{scope.value}_{recommendation_count}"
            if self.config.cache_recommendations and cache_key in self.recommendation_cache:
                cached_result = self.recommendation_cache[cache_key]
                if cached_result.ttl > datetime.now(timezone.utc):
                    return cached_result
            
            # Generate recommendations based on type
            if personalization_type == PersonalizationType.CONTENT_BASED:
                recommendations = await self._content_based_recommendations(user_profile, recommendation_count)
            elif personalization_type == PersonalizationType.COLLABORATIVE:
                recommendations = await self._collaborative_recommendations(user_profile, recommendation_count)
            elif personalization_type == PersonalizationType.BEHAVIORAL:
                recommendations = await self._behavioral_recommendations(user_profile, recommendation_count)
            elif personalization_type == PersonalizationType.HYBRID:
                recommendations = await self._hybrid_recommendations(user_profile, recommendation_count)
            else:
                recommendations = await self._fallback_recommendations(recommendation_count)
            
            # Calculate quality metrics
            confidence_score = self._calculate_confidence_score(recommendations, user_profile)
            diversity_score = self._calculate_diversity_score(recommendations)
            freshness_score = self._calculate_freshness_score(recommendations)
            
            # Generate explanation
            explanation = self._generate_explanation(recommendations, personalization_type, user_profile)
            
            # Create result
            result = PersonalizationResult(
                user_id=user_id,
                recommendations=recommendations,
                personalization_type=personalization_type,
                confidence_score=confidence_score,
                diversity_score=diversity_score,
                freshness_score=freshness_score,
                explanation=explanation
            )
            
            # Cache result
            if self.config.cache_recommendations:
                self.recommendation_cache[cache_key] = result
            
            return result
            
        except Exception as e:
            logger.error(f"Recommendation generation failed for user {user_id}: {e}")
            # Return fallback recommendations
            fallback_recs = await self._fallback_recommendations(recommendation_count)
            return PersonalizationResult(
                user_id=user_id,
                recommendations=fallback_recs,
                personalization_type=PersonalizationType.CONTENT_BASED,
                confidence_score=0.1,
                diversity_score=0.5,
                freshness_score=0.5,
                explanation={'method': 'fallback', 'reason': str(e)}
            )
    
    async def _content_based_recommendations(
        self, 
        user_profile: UserProfile, 
        count: int
    ) -> List[Dict[str, Any]]:
        """Generate content-based recommendations"""
        recommendations = []
        
        # Get user's interaction history
        interacted_content = {i.content_id for i in user_profile.interaction_history}
        
        # Calculate content similarities if sklearn available
        if HAS_SKLEARN and self.content_features:
            recommendations = await self._ml_content_recommendations(
                user_profile, interacted_content, count
            )
        else:
            # Fallback to simple content-based matching
            recommendations = await self._simple_content_recommendations(
                user_profile, interacted_content, count
            )
        
        return recommendations
    
    async def _collaborative_recommendations(
        self, 
        user_profile: UserProfile, 
        count: int
    ) -> List[Dict[str, Any]]:
        """Generate collaborative filtering recommendations"""
        recommendations = []
        
        # Find similar users
        similar_users = await self._find_similar_users(user_profile)
        
        # Get content liked by similar users
        content_scores = defaultdict(float)
        interacted_content = {i.content_id for i in user_profile.interaction_history}
        
        for similar_user_id, similarity_score in similar_users[:10]:  # Top 10 similar users
            # Would get interactions from similar user
            # For now, simulate with random content
            for content_id, content_item in list(self.content_catalog.items())[:count * 2]:
                if content_id not in interacted_content:
                    content_scores[content_id] += similarity_score * content_item.popularity_score
        
        # Sort by score and select top recommendations
        sorted_content = sorted(content_scores.items(), key=lambda x: x[1], reverse=True)
        
        for content_id, score in sorted_content[:count]:
            content_item = self.content_catalog.get(content_id)
            if content_item:
                recommendations.append({
                    'content_id': content_id,
                    'title': content_item.title,
                    'category': content_item.category.value,
                    'score': score,
                    'reason': 'collaborative_filtering'
                })
        
        return recommendations
    
    async def _behavioral_recommendations(
        self, 
        user_profile: UserProfile, 
        count: int
    ) -> List[Dict[str, Any]]:
        """Generate behavior-based recommendations"""
        recommendations = []
        
        # Analyze user behavior patterns
        behavior_patterns = await self._analyze_behavior_patterns(user_profile)
        
        # Recommend content based on patterns
        interacted_content = {i.content_id for i in user_profile.interaction_history}
        
        for content_id, content_item in self.content_catalog.items():
            if content_id not in interacted_content and len(recommendations) < count:
                # Score based on behavior patterns
                score = self._calculate_behavioral_score(content_item, behavior_patterns)
                
                if score > 0.3:  # Threshold for inclusion
                    recommendations.append({
                        'content_id': content_id,
                        'title': content_item.title,
                        'category': content_item.category.value,
                        'score': score,
                        'reason': 'behavioral_pattern'
                    })
        
        # Sort by score
        recommendations.sort(key=lambda x: x['score'], reverse=True)
        
        return recommendations[:count]
    
    async def _hybrid_recommendations(
        self, 
        user_profile: UserProfile, 
        count: int
    ) -> List[Dict[str, Any]]:
        """Generate hybrid recommendations combining multiple approaches"""
        # Get recommendations from different approaches
        content_based = await self._content_based_recommendations(user_profile, count // 2)
        collaborative = await self._collaborative_recommendations(user_profile, count // 2)
        behavioral = await self._behavioral_recommendations(user_profile, count // 2)
        
        # Combine and weight recommendations
        all_recommendations = {}
        
        # Weight content-based recommendations
        for rec in content_based:
            content_id = rec['content_id']
            all_recommendations[content_id] = all_recommendations.get(content_id, 0) + rec['score'] * 0.4
        
        # Weight collaborative recommendations
        for rec in collaborative:
            content_id = rec['content_id']
            all_recommendations[content_id] = all_recommendations.get(content_id, 0) + rec['score'] * 0.4
        
        # Weight behavioral recommendations
        for rec in behavioral:
            content_id = rec['content_id']
            all_recommendations[content_id] = all_recommendations.get(content_id, 0) + rec['score'] * 0.2
        
        # Sort and format final recommendations
        sorted_recommendations = sorted(all_recommendations.items(), key=lambda x: x[1], reverse=True)
        
        final_recommendations = []
        for content_id, score in sorted_recommendations[:count]:
            content_item = self.content_catalog.get(content_id)
            if content_item:
                final_recommendations.append({
                    'content_id': content_id,
                    'title': content_item.title,
                    'category': content_item.category.value,
                    'score': score,
                    'reason': 'hybrid_approach'
                })
        
        return final_recommendations
    
    async def _fallback_recommendations(self, count: int) -> List[Dict[str, Any]]:
        """Generate fallback recommendations when personalization fails"""
        recommendations = []
        
        # Sort content by popularity and quality
        sorted_content = sorted(
            self.content_catalog.items(),
            key=lambda x: x[1].popularity_score * x[1].quality_score,
            reverse=True
        )
        
        for content_id, content_item in sorted_content[:count]:
            recommendations.append({
                'content_id': content_id,
                'title': content_item.title,
                'category': content_item.category.value,
                'score': content_item.popularity_score,
                'reason': 'popular_content'
            })
        
        return recommendations
    
    async def _ml_content_recommendations(
        self, 
        user_profile: UserProfile, 
        interacted_content: Set[str], 
        count: int
    ) -> List[Dict[str, Any]]:
        """Generate ML-based content recommendations"""
        recommendations = []
        
        # Would implement TF-IDF and cosine similarity here
        # For now, return simple recommendations
        return await self._simple_content_recommendations(user_profile, interacted_content, count)
    
    async def _simple_content_recommendations(
        self, 
        user_profile: UserProfile, 
        interacted_content: Set[str], 
        count: int
    ) -> List[Dict[str, Any]]:
        """Generate simple content-based recommendations"""
        recommendations = []
        
        # Get user preferences
        user_preferences = user_profile.preferences
        
        for content_id, content_item in self.content_catalog.items():
            if content_id not in interacted_content and len(recommendations) < count:
                # Calculate preference score
                preference_score = user_preferences.get(content_item.category.value, 0.5)
                
                # Factor in content quality and popularity
                final_score = (
                    preference_score * 0.5 +
                    content_item.quality_score * 0.3 +
                    content_item.popularity_score * 0.2
                )
                
                recommendations.append({
                    'content_id': content_id,
                    'title': content_item.title,
                    'category': content_item.category.value,
                    'score': final_score,
                    'reason': 'content_preference'
                })
        
        # Sort by score
        recommendations.sort(key=lambda x: x['score'], reverse=True)
        
        return recommendations[:count]
    
    async def _find_similar_users(self, user_profile: UserProfile) -> List[Tuple[str, float]]:
        """Find users similar to the given user profile"""
        # Simplified similarity calculation
        # In production, would use sophisticated user similarity algorithms
        similar_users = []
        
        # For now, return empty list (would implement actual similarity calculation)
        return similar_users
    
    async def _analyze_behavior_patterns(self, user_profile: UserProfile) -> Dict[str, Any]:
        """Analyze user behavior patterns"""
        patterns = {
            'preferred_time': 'evening',  # Would analyze actual patterns
            'session_length': 'medium',
            'content_consumption_rate': 'normal',
            'exploration_tendency': 'moderate'
        }
        
        return patterns
    
    def _calculate_behavioral_score(
        self, 
        content_item: ContentItem, 
        behavior_patterns: Dict[str, Any]
    ) -> float:
        """Calculate behavioral compatibility score"""
        # Simplified behavioral scoring
        base_score = content_item.quality_score * content_item.popularity_score
        
        # Apply behavioral modifiers (simplified)
        if behavior_patterns.get('exploration_tendency') == 'high':
            base_score *= 1.2  # Boost for exploratory users
        
        return min(base_score, 1.0)
    
    def _calculate_confidence_score(
        self, 
        recommendations: List[Dict[str, Any]], 
        user_profile: UserProfile
    ) -> float:
        """Calculate confidence in recommendations"""
        if not recommendations:
            return 0.0
        
        # Base confidence on user profile completeness
        profile_completeness = len(user_profile.interaction_history) / self.config.max_user_history_items
        profile_completeness = min(profile_completeness, 1.0)
        
        # Factor in recommendation quality
        avg_score = sum(rec.get('score', 0) for rec in recommendations) / len(recommendations)
        
        confidence = (profile_completeness * 0.7 + avg_score * 0.3)
        
        return confidence
    
    def _calculate_diversity_score(self, recommendations: List[Dict[str, Any]]) -> float:
        """Calculate diversity in recommendations"""
        if not recommendations:
            return 0.0
        
        # Count unique categories
        categories = set(rec.get('category') for rec in recommendations)
        max_possible_categories = len(ContentCategory)
        
        diversity = len(categories) / max_possible_categories
        
        return diversity
    
    def _calculate_freshness_score(self, recommendations: List[Dict[str, Any]]) -> float:
        """Calculate freshness of recommendations"""
        if not recommendations:
            return 0.0
        
        # For now, assume all recommendations are reasonably fresh
        # In production, would factor in content creation dates
        return 0.8
    
    def _generate_explanation(
        self, 
        recommendations: List[Dict[str, Any]], 
        personalization_type: PersonalizationType,
        user_profile: UserProfile
    ) -> Dict[str, Any]:
        """Generate explanation for recommendations"""
        explanation = {
            'method': personalization_type.value,
            'factors': [],
            'reasoning': ''
        }
        
        if personalization_type == PersonalizationType.CONTENT_BASED:
            explanation['reasoning'] = "Based on your content preferences and viewing history"
            explanation['factors'] = ['content_similarity', 'user_preferences']
        elif personalization_type == PersonalizationType.COLLABORATIVE:
            explanation['reasoning'] = "Based on users with similar interests"
            explanation['factors'] = ['user_similarity', 'collaborative_filtering']
        elif personalization_type == PersonalizationType.BEHAVIORAL:
            explanation['reasoning'] = "Based on your browsing and engagement patterns"
            explanation['factors'] = ['behavior_patterns', 'engagement_analysis']
        elif personalization_type == PersonalizationType.HYBRID:
            explanation['reasoning'] = "Based on multiple personalization approaches"
            explanation['factors'] = ['content_similarity', 'user_similarity', 'behavior_patterns']
        
        return explanation


class ContentPersonalizationEngine:
    """Main content personalization engine orchestrating all components"""
    
    def __init__(self, config: Optional[PersonalizationConfig] = None):
        """Initialize content personalization engine"""
        self.config = config or PersonalizationConfig()
        
        # Initialize component engines
        self.behavior_analyzer = UserBehaviorAnalyzer(self.config)
        self.recommendation_engine = ContentRecommendationEngine(self.config)
        
        # System state
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        self.personalization_metrics: Dict[str, Any] = {
            'total_recommendations': 0,
            'total_interactions': 0,
            'average_confidence': 0.0,
            'average_diversity': 0.0
        }
        
        logger.info("🎨 Content Personalization Engine initialized")
    
    async def record_user_interaction(
        self,
        user_id: str,
        content_id: str,
        interaction_type: InteractionType,
        context: Optional[Dict[str, Any]] = None,
        duration: Optional[float] = None
    ) -> bool:
        """Record user interaction for personalization"""
        try:
            interaction = UserInteraction(
                interaction_id=str(uuid.uuid4()),
                user_id=user_id,
                content_id=content_id,
                interaction_type=interaction_type,
                timestamp=datetime.now(timezone.utc),
                duration=duration,
                context=context or {}
            )
            
            # Update user profile
            await self.behavior_analyzer.update_user_profile(interaction)
            
            # Update metrics
            self.personalization_metrics['total_interactions'] += 1
            
            # Real-time personalization updates
            if self.config.real_time_updates:
                await self._invalidate_user_cache(user_id)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to record user interaction: {e}")
            return False
    
    async def get_personalized_recommendations(
        self,
        user_id: str,
        personalization_type: PersonalizationType = PersonalizationType.HYBRID,
        count: Optional[int] = None,
        scope: PersonalizationScope = PersonalizationScope.GLOBAL
    ) -> PersonalizationResult:
        """Get personalized content recommendations for user"""
        try:
            # Get user profile
            user_profile = self.behavior_analyzer.user_profiles.get(user_id)
            
            if not user_profile:
                # Create new user profile
                user_profile = UserProfile(user_id=user_id)
                self.behavior_analyzer.user_profiles[user_id] = user_profile
            
            # Check if user has enough interactions for personalization
            if len(user_profile.interaction_history) < self.config.min_interactions_for_personalization:
                # Use fallback recommendations for new users
                personalization_type = PersonalizationType.CONTENT_BASED
            
            # Generate recommendations
            result = await self.recommendation_engine.generate_recommendations(
                user_id=user_id,
                user_profile=user_profile,
                personalization_type=personalization_type,
                scope=scope,
                count=count
            )
            
            # Update metrics
            self.personalization_metrics['total_recommendations'] += 1
            self._update_average_metrics(result)
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to get personalized recommendations for user {user_id}: {e}")
            # Return fallback recommendations
            fallback_recs = await self.recommendation_engine._fallback_recommendations(count or self.config.recommendation_count)
            return PersonalizationResult(
                user_id=user_id,
                recommendations=fallback_recs,
                personalization_type=PersonalizationType.CONTENT_BASED,
                confidence_score=0.1,
                diversity_score=0.5,
                freshness_score=0.5,
                explanation={'method': 'fallback', 'reason': str(e)}
            )
    
    async def add_content_item(self, content_item: ContentItem):
        """Add content item to personalization catalog"""
        try:
            self.recommendation_engine.content_catalog[content_item.content_id] = content_item
            
            # Extract features for ML (if available)
            if HAS_SKLEARN:
                await self._extract_content_features(content_item)
            
            logger.info(f"Added content item {content_item.content_id} to catalog")
            
        except Exception as e:
            logger.error(f"Failed to add content item: {e}")
    
    async def get_user_insights(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive user insights for personalization"""
        try:
            # Get behavior analysis
            behavior_analysis = await self.behavior_analyzer.analyze_user_behavior(user_id)
            
            # Get recent recommendations
            user_profile = self.behavior_analyzer.user_profiles.get(user_id)
            recent_recommendations = None
            
            if user_profile:
                recent_recommendations = await self.recommendation_engine.generate_recommendations(
                    user_id=user_id,
                    user_profile=user_profile,
                    count=5
                )
            
            return {
                'user_id': user_id,
                'behavior_analysis': behavior_analysis,
                'recent_recommendations': {
                    'count': len(recent_recommendations.recommendations) if recent_recommendations else 0,
                    'confidence': recent_recommendations.confidence_score if recent_recommendations else 0,
                    'diversity': recent_recommendations.diversity_score if recent_recommendations else 0
                },
                'profile_status': {
                    'has_profile': user_id in self.behavior_analyzer.user_profiles,
                    'interaction_count': len(user_profile.interaction_history) if user_profile else 0,
                    'personalization_ready': len(user_profile.interaction_history) >= self.config.min_interactions_for_personalization if user_profile else False
                },
                'insights_generated': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get user insights: {e}")
            return {'error': str(e)}
    
    async def get_personalization_analytics(self) -> Dict[str, Any]:
        """Get personalization system analytics"""
        try:
            total_users = len(self.behavior_analyzer.user_profiles)
            active_users = len([
                profile for profile in self.behavior_analyzer.user_profiles.values()
                if (datetime.now(timezone.utc) - profile.last_active).days <= 7
            ])
            
            personalized_users = len([
                profile for profile in self.behavior_analyzer.user_profiles.values()
                if len(profile.interaction_history) >= self.config.min_interactions_for_personalization
            ])
            
            return {
                'system_metrics': self.personalization_metrics,
                'user_statistics': {
                    'total_users': total_users,
                    'active_users_7d': active_users,
                    'personalized_users': personalized_users,
                    'personalization_coverage': personalized_users / total_users if total_users > 0 else 0
                },
                'content_statistics': {
                    'total_content_items': len(self.recommendation_engine.content_catalog),
                    'cached_recommendations': len(self.recommendation_engine.recommendation_cache)
                },
                'performance': {
                    'cache_hit_rate': 0.8,  # Would calculate actual rate
                    'avg_recommendation_time_ms': 50,  # Would measure actual time
                    'system_health': 'healthy'
                },
                'analytics_timestamp': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get personalization analytics: {e}")
            return {'error': str(e)}
    
    async def _extract_content_features(self, content_item: ContentItem):
        """Extract features from content for ML algorithms"""
        # Would implement feature extraction here
        # For now, create basic features
        features = {
            'category_numeric': hash(content_item.category.value) % 100,
            'title_length': len(content_item.title),
            'description_length': len(content_item.description),
            'tag_count': len(content_item.tags),
            'quality_score': content_item.quality_score,
            'popularity_score': content_item.popularity_score
        }
        
        self.recommendation_engine.content_features[content_item.content_id] = features
    
    async def _invalidate_user_cache(self, user_id: str):
        """Invalidate cache for specific user"""
        # Remove cached recommendations for user
        keys_to_remove = [
            key for key in self.recommendation_engine.recommendation_cache.keys()
            if key.startswith(user_id)
        ]
        
        for key in keys_to_remove:
            del self.recommendation_engine.recommendation_cache[key]
    
    def _update_average_metrics(self, result: PersonalizationResult):
        """Update running average metrics"""
        total_recs = self.personalization_metrics['total_recommendations']
        
        # Update average confidence
        current_avg_confidence = self.personalization_metrics['average_confidence']
        new_avg_confidence = ((current_avg_confidence * (total_recs - 1)) + result.confidence_score) / total_recs
        self.personalization_metrics['average_confidence'] = new_avg_confidence
        
        # Update average diversity
        current_avg_diversity = self.personalization_metrics['average_diversity']
        new_avg_diversity = ((current_avg_diversity * (total_recs - 1)) + result.diversity_score) / total_recs
        self.personalization_metrics['average_diversity'] = new_avg_diversity


# Export all classes for import
__all__ = [
    'ContentPersonalizationEngine',
    'UserBehaviorAnalyzer',
    'ContentRecommendationEngine',
    'PersonalizationConfig',
    'UserProfile',
    'UserInteraction',
    'ContentItem',
    'PersonalizationResult',
    'PersonalizationType',
    'InteractionType',
    'ContentCategory',
    'PersonalizationScope'
]