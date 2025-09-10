"""
Advanced Preference Engine for Ainflue Distribution Platform

This module provides sophisticated user preference analysis and prediction capabilities
using machine learning to understand and predict user content preferences across platforms.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass
from enum import Enum
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import DBSCAN
import json
import hashlib

logger = logging.getLogger(__name__)


class PreferenceType(Enum):
    """Types of user preferences"""
    CONTENT_CATEGORY = "content_category"
    CREATOR_STYLE = "creator_style"
    FORMAT_TYPE = "format_type"
    TOPIC_INTEREST = "topic_interest"
    INTERACTION_MODE = "interaction_mode"
    TEMPORAL_PATTERN = "temporal_pattern"
    PLATFORM_SPECIFIC = "platform_specific"
    SOCIAL_CONTEXT = "social_context"


class PreferenceStrength(Enum):
    """Strength levels for preferences"""
    VERY_STRONG = 0.9
    STRONG = 0.7
    MODERATE = 0.5
    WEAK = 0.3
    VERY_WEAK = 0.1


@dataclass
class UserPreference:
    """Individual user preference item"""
    preference_id: str
    user_id: str
    preference_type: PreferenceType
    preference_value: str
    strength: float
    confidence: float
    last_updated: datetime
    source_interactions: int
    trend_direction: float  # Positive = increasing, Negative = decreasing
    context_tags: List[str]


@dataclass
class PreferenceProfile:
    """Complete user preference profile"""
    user_id: str
    platform: str
    preferences: List[UserPreference]
    preference_clusters: Dict[str, List[str]]
    similarity_scores: Dict[str, float]
    personalization_vector: np.ndarray
    last_updated: datetime
    profile_completeness: float
    prediction_accuracy: float


@dataclass
class PreferenceInsight:
    """Actionable preference insights"""
    insight_type: str
    description: str
    confidence: float
    impact_potential: float
    recommended_actions: List[str]
    target_preferences: List[str]
    expected_outcome: str


class AdvancedPreferenceEngine:
    """
    AI-powered preference analysis and prediction engine
    
    Features:
    - Real-time preference learning
    - Multi-dimensional preference modeling
    - Preference drift detection
    - Collaborative filtering
    - Content-based recommendation
    - Preference clustering and segmentation
    """

    def __init__(self):
        self.preference_models = {}
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        self.rf_classifier = RandomForestClassifier(n_estimators=100, random_state=42)
        self.preference_cache = {}
        self.similarity_cache = {}
        self.user_clusters = {}
        
    async def analyze_user_preferences(
        self,
        user_id: str,
        platform: str,
        interaction_history: List[Dict[str, Any]],
        timeframe_days: int = 90
    ) -> PreferenceProfile:
        """
        Analyze comprehensive user preferences from interaction history
        
        Args:
            user_id: Unique user identifier
            platform: Platform being analyzed
            interaction_history: List of user interactions
            timeframe_days: Analysis timeframe
            
        Returns:
            Complete preference profile
        """
        try:
            # Extract preferences from interactions
            preferences = await self._extract_preferences_from_interactions(
                user_id, interaction_history, timeframe_days
            )
            
            # Cluster preferences
            clusters = await self._cluster_preferences(preferences)
            
            # Calculate similarity scores
            similarity_scores = await self._calculate_preference_similarities(
                user_id, preferences
            )
            
            # Create personalization vector
            personalization_vector = await self._create_personalization_vector(preferences)
            
            # Calculate profile metrics
            completeness = self._calculate_profile_completeness(preferences)
            accuracy = await self._estimate_prediction_accuracy(user_id, preferences)
            
            return PreferenceProfile(
                user_id=user_id,
                platform=platform,
                preferences=preferences,
                preference_clusters=clusters,
                similarity_scores=similarity_scores,
                personalization_vector=personalization_vector,
                last_updated=datetime.utcnow(),
                profile_completeness=completeness,
                prediction_accuracy=accuracy
            )
            
        except Exception as e:
            logger.error(f"Error analyzing user preferences: {e}")
            raise

    async def _extract_preferences_from_interactions(
        self,
        user_id: str,
        interactions: List[Dict[str, Any]],
        timeframe_days: int
    ) -> List[UserPreference]:
        """Extract and score preferences from user interactions"""
        
        preferences = []
        preference_counters = {}
        
        # Analyze each interaction
        for interaction in interactions:
            # Content category preferences
            category = interaction.get('content_category')
            if category:
                key = f"category_{category}"
                preference_counters[key] = preference_counters.get(key, 0) + self._get_interaction_weight(interaction)
            
            # Creator style preferences
            creator_id = interaction.get('creator_id')
            creator_style = interaction.get('creator_style')
            if creator_style:
                key = f"style_{creator_style}"
                preference_counters[key] = preference_counters.get(key, 0) + self._get_interaction_weight(interaction)
            
            # Format preferences
            content_format = interaction.get('content_format')
            if content_format:
                key = f"format_{content_format}"
                preference_counters[key] = preference_counters.get(key, 0) + self._get_interaction_weight(interaction)
            
            # Topic preferences
            topics = interaction.get('topics', [])
            for topic in topics:
                key = f"topic_{topic}"
                preference_counters[key] = preference_counters.get(key, 0) + self._get_interaction_weight(interaction)
            
            # Temporal preferences
            hour = datetime.fromisoformat(interaction.get('timestamp', '')).hour
            key = f"time_{hour}"
            preference_counters[key] = preference_counters.get(key, 0) + self._get_interaction_weight(interaction)
        
        # Convert counters to preference objects
        total_interactions = len(interactions)
        for pref_key, count in preference_counters.items():
            pref_type, pref_value = pref_key.split('_', 1)
            
            # Map preference types
            type_mapping = {
                'category': PreferenceType.CONTENT_CATEGORY,
                'style': PreferenceType.CREATOR_STYLE,
                'format': PreferenceType.FORMAT_TYPE,
                'topic': PreferenceType.TOPIC_INTEREST,
                'time': PreferenceType.TEMPORAL_PATTERN
            }
            
            if pref_type in type_mapping:
                strength = min(1.0, count / total_interactions * 2)  # Normalize and boost
                confidence = min(1.0, count / 10)  # Confidence based on interaction count
                
                preference = UserPreference(
                    preference_id=self._generate_preference_id(user_id, pref_key),
                    user_id=user_id,
                    preference_type=type_mapping[pref_type],
                    preference_value=pref_value,
                    strength=strength,
                    confidence=confidence,
                    last_updated=datetime.utcnow(),
                    source_interactions=count,
                    trend_direction=self._calculate_trend_direction(interactions, pref_key),
                    context_tags=self._extract_context_tags(interactions, pref_key)
                )
                
                preferences.append(preference)
        
        return sorted(preferences, key=lambda p: p.strength * p.confidence, reverse=True)

    def _get_interaction_weight(self, interaction: Dict[str, Any]) -> float:
        """Calculate weight for an interaction based on type and engagement"""
        
        base_weights = {
            'view': 1.0,
            'like': 2.0,
            'comment': 3.0,
            'share': 4.0,
            'save': 3.5,
            'follow': 5.0
        }
        
        interaction_type = interaction.get('type', 'view')
        base_weight = base_weights.get(interaction_type, 1.0)
        
        # Time decay (more recent interactions have higher weight)
        timestamp = interaction.get('timestamp')
        if timestamp:
            days_ago = (datetime.utcnow() - datetime.fromisoformat(timestamp)).days
            time_weight = max(0.1, 1.0 - days_ago / 90.0)  # 90-day decay
        else:
            time_weight = 1.0
        
        # Engagement quality multiplier
        engagement_score = interaction.get('engagement_score', 1.0)
        
        return base_weight * time_weight * engagement_score

    def _generate_preference_id(self, user_id: str, preference_key: str) -> str:
        """Generate unique preference ID"""
        combined = f"{user_id}_{preference_key}"
        return hashlib.md5(combined.encode()).hexdigest()[:16]

    def _calculate_trend_direction(self, interactions: List[Dict[str, Any]], pref_key: str) -> float:
        """Calculate trend direction for a preference"""
        
        # Split interactions into two time periods
        interactions_with_time = [
            i for i in interactions 
            if i.get('timestamp') and pref_key.split('_', 1)[1] in str(i)
        ]
        
        if len(interactions_with_time) < 4:
            return 0.0
        
        # Sort by timestamp
        interactions_with_time.sort(key=lambda x: x['timestamp'])
        
        # Split into early and late periods
        mid_point = len(interactions_with_time) // 2
        early_period = interactions_with_time[:mid_point]
        late_period = interactions_with_time[mid_point:]
        
        early_count = len(early_period)
        late_count = len(late_period)
        
        if early_count == 0:
            return 1.0
        
        # Calculate trend as relative change
        trend = (late_count - early_count) / early_count
        return np.tanh(trend)  # Normalize to [-1, 1]

    def _extract_context_tags(self, interactions: List[Dict[str, Any]], pref_key: str) -> List[str]:
        """Extract context tags for a preference"""
        
        contexts = set()
        pref_value = pref_key.split('_', 1)[1]
        
        for interaction in interactions:
            if pref_value in str(interaction):
                # Add contextual information
                if interaction.get('device_type'):
                    contexts.add(f"device_{interaction['device_type']}")
                if interaction.get('location'):
                    contexts.add(f"location_{interaction['location']}")
                if interaction.get('social_context'):
                    contexts.add(f"social_{interaction['social_context']}")
        
        return list(contexts)

    async def _cluster_preferences(self, preferences: List[UserPreference]) -> Dict[str, List[str]]:
        """Cluster preferences to identify patterns"""
        
        if not preferences:
            return {}
        
        # Create feature matrix for clustering
        features = []
        preference_ids = []
        
        for pref in preferences:
            features.append([
                pref.strength,
                pref.confidence,
                pref.source_interactions,
                pref.trend_direction,
                len(pref.context_tags)
            ])
            preference_ids.append(pref.preference_id)
        
        if len(features) < 3:
            return {"single_cluster": preference_ids}
        
        # Perform DBSCAN clustering
        clustering = DBSCAN(eps=0.3, min_samples=2)
        cluster_labels = clustering.fit_predict(features)
        
        # Organize into clusters
        clusters = {}
        for i, label in enumerate(cluster_labels):
            cluster_name = f"cluster_{label}" if label != -1 else "outliers"
            if cluster_name not in clusters:
                clusters[cluster_name] = []
            clusters[cluster_name].append(preference_ids[i])
        
        return clusters

    async def _calculate_preference_similarities(
        self,
        user_id: str,
        preferences: List[UserPreference]
    ) -> Dict[str, float]:
        """Calculate similarity scores with other users"""
        
        # This would typically involve comparing with other user profiles
        # For now, return similarity based on preference strength distribution
        
        similarities = {}
        
        # Calculate internal consistency score
        if preferences:
            strengths = [p.strength for p in preferences]
            confidences = [p.confidence for p in preferences]
            
            # Higher consistency indicates clearer preferences
            strength_std = np.std(strengths)
            confidence_mean = np.mean(confidences)
            
            similarities['internal_consistency'] = max(0.0, 1.0 - strength_std) * confidence_mean
        
        return similarities

    async def _create_personalization_vector(self, preferences: List[UserPreference]) -> np.ndarray:
        """Create high-dimensional personalization vector"""
        
        # Create 100-dimensional vector representing user preferences
        vector = np.zeros(100)
        
        if not preferences:
            return vector
        
        # Map preference types to vector dimensions
        type_offsets = {
            PreferenceType.CONTENT_CATEGORY: 0,
            PreferenceType.CREATOR_STYLE: 20,
            PreferenceType.FORMAT_TYPE: 40,
            PreferenceType.TOPIC_INTEREST: 60,
            PreferenceType.TEMPORAL_PATTERN: 80
        }
        
        for pref in preferences:
            if pref.preference_type in type_offsets:
                offset = type_offsets[pref.preference_type]
                # Hash preference value to specific dimensions
                hash_val = hash(pref.preference_value) % 20
                dim = offset + hash_val
                
                if dim < 100:
                    vector[dim] += pref.strength * pref.confidence
        
        # Normalize vector
        norm = np.linalg.norm(vector)
        if norm > 0:
            vector = vector / norm
        
        return vector

    def _calculate_profile_completeness(self, preferences: List[UserPreference]) -> float:
        """Calculate how complete the preference profile is"""
        
        if not preferences:
            return 0.0
        
        # Check coverage across preference types
        covered_types = set(p.preference_type for p in preferences)
        total_types = len(PreferenceType)
        type_coverage = len(covered_types) / total_types
        
        # Check strength of top preferences
        top_preferences = sorted(preferences, key=lambda p: p.strength, reverse=True)[:10]
        strength_score = np.mean([p.strength for p in top_preferences]) if top_preferences else 0.0
        
        # Check confidence levels
        confidence_score = np.mean([p.confidence for p in preferences])
        
        return (type_coverage + strength_score + confidence_score) / 3.0

    async def _estimate_prediction_accuracy(
        self,
        user_id: str,
        preferences: List[UserPreference]
    ) -> float:
        """Estimate prediction accuracy based on preference consistency"""
        
        if len(preferences) < 5:
            return 0.5  # Low confidence with few preferences
        
        # Calculate consistency metrics
        strengths = [p.strength for p in preferences]
        confidences = [p.confidence for p in preferences]
        
        # High consistency in top preferences indicates better predictability
        top_10_strengths = sorted(strengths, reverse=True)[:10]
        consistency = 1.0 - np.std(top_10_strengths) if top_10_strengths else 0.5
        
        # High average confidence indicates reliable data
        avg_confidence = np.mean(confidences)
        
        # More preferences with strong signals indicate better model
        strong_preferences = len([p for p in preferences if p.strength > 0.7 and p.confidence > 0.7])
        data_richness = min(1.0, strong_preferences / 10.0)
        
        return (consistency + avg_confidence + data_richness) / 3.0

    async def predict_content_preference(
        self,
        user_id: str,
        content_metadata: Dict[str, Any],
        user_profile: PreferenceProfile
    ) -> Tuple[float, float]:
        """
        Predict user preference for specific content
        
        Returns:
            Tuple of (preference_score, confidence)
        """
        try:
            preference_score = 0.0
            confidence_sum = 0.0
            total_weight = 0.0
            
            # Match content attributes with user preferences
            for preference in user_profile.preferences:
                match_score = self._calculate_content_preference_match(
                    preference, content_metadata
                )
                
                if match_score > 0:
                    weight = preference.strength * preference.confidence
                    preference_score += match_score * weight
                    confidence_sum += preference.confidence * weight
                    total_weight += weight
            
            if total_weight > 0:
                final_score = preference_score / total_weight
                final_confidence = confidence_sum / total_weight
            else:
                final_score = 0.5  # Neutral when no matches
                final_confidence = 0.1  # Low confidence
            
            return final_score, final_confidence
            
        except Exception as e:
            logger.error(f"Error predicting content preference: {e}")
            return 0.5, 0.1

    def _calculate_content_preference_match(
        self,
        preference: UserPreference,
        content_metadata: Dict[str, Any]
    ) -> float:
        """Calculate how well content matches a specific preference"""
        
        match_score = 0.0
        
        if preference.preference_type == PreferenceType.CONTENT_CATEGORY:
            if content_metadata.get('category') == preference.preference_value:
                match_score = 1.0
            elif preference.preference_value in str(content_metadata.get('subcategories', [])):
                match_score = 0.7
        
        elif preference.preference_type == PreferenceType.CREATOR_STYLE:
            if content_metadata.get('creator_style') == preference.preference_value:
                match_score = 1.0
            elif preference.preference_value in str(content_metadata.get('style_tags', [])):
                match_score = 0.6
        
        elif preference.preference_type == PreferenceType.FORMAT_TYPE:
            if content_metadata.get('format') == preference.preference_value:
                match_score = 1.0
        
        elif preference.preference_type == PreferenceType.TOPIC_INTEREST:
            topics = content_metadata.get('topics', [])
            if preference.preference_value in topics:
                match_score = 1.0
            elif any(preference.preference_value in topic for topic in topics):
                match_score = 0.5
        
        elif preference.preference_type == PreferenceType.TEMPORAL_PATTERN:
            # Check if current time matches temporal preference
            current_hour = datetime.utcnow().hour
            preferred_hour = int(preference.preference_value)
            
            hour_diff = abs(current_hour - preferred_hour)
            if hour_diff > 12:
                hour_diff = 24 - hour_diff
            
            match_score = max(0.0, 1.0 - hour_diff / 6.0)  # 6-hour tolerance
        
        return match_score

    async def generate_preference_insights(
        self,
        user_profile: PreferenceProfile
    ) -> List[PreferenceInsight]:
        """Generate actionable insights from preference analysis"""
        
        insights = []
        
        # Analyze preference strength distribution
        strong_preferences = [p for p in user_profile.preferences if p.strength > 0.7]
        if len(strong_preferences) < 3:
            insights.append(PreferenceInsight(
                insight_type="preference_exploration",
                description="Limited strong preferences detected - opportunity for content exploration",
                confidence=0.8,
                impact_potential=0.7,
                recommended_actions=[
                    "Expose user to diverse content categories",
                    "Implement exploration-exploitation strategy",
                    "A/B test different content types",
                    "Monitor engagement to identify emerging preferences"
                ],
                target_preferences=[p.preference_value for p in user_profile.preferences[:5]],
                expected_outcome="Increased engagement and preference clarity"
            ))
        
        # Analyze preference trends
        declining_preferences = [
            p for p in user_profile.preferences 
            if p.trend_direction < -0.3 and p.strength > 0.5
        ]
        if declining_preferences:
            insights.append(PreferenceInsight(
                insight_type="preference_shift",
                description="Declining interest in previously strong preferences detected",
                confidence=0.75,
                impact_potential=0.9,
                recommended_actions=[
                    "Reduce content from declining categories",
                    "Identify emerging preference categories",
                    "Implement preference refresh strategy",
                    "Survey user for explicit feedback"
                ],
                target_preferences=[p.preference_value for p in declining_preferences],
                expected_outcome="Improved content relevance and engagement"
            ))
        
        # Analyze preference clusters
        if len(user_profile.preference_clusters) > 3:
            insights.append(PreferenceInsight(
                insight_type="preference_diversity",
                description="High preference diversity indicates multi-faceted interests",
                confidence=0.85,
                impact_potential=0.8,
                recommended_actions=[
                    "Implement multi-category content strategy",
                    "Create preference-specific content buckets",
                    "Use context-aware recommendation",
                    "Develop preference-based user segments"
                ],
                target_preferences=list(user_profile.preference_clusters.keys()),
                expected_outcome="More personalized and engaging content experience"
            ))
        
        return insights

    async def update_preferences_from_feedback(
        self,
        user_id: str,
        content_id: str,
        feedback_type: str,
        feedback_strength: float,
        content_metadata: Dict[str, Any]
    ) -> bool:
        """Update user preferences based on explicit or implicit feedback"""
        
        try:
            # Extract preference signals from feedback
            if feedback_type in ['like', 'love', 'share']:
                # Positive feedback strengthens preferences
                await self._strengthen_matching_preferences(
                    user_id, content_metadata, feedback_strength
                )
            elif feedback_type in ['dislike', 'hide', 'report']:
                # Negative feedback weakens preferences
                await self._weaken_matching_preferences(
                    user_id, content_metadata, feedback_strength
                )
            elif feedback_type == 'view_duration':
                # Implicit feedback based on engagement time
                if feedback_strength > 0.7:  # High engagement
                    await self._strengthen_matching_preferences(
                        user_id, content_metadata, feedback_strength * 0.5
                    )
                elif feedback_strength < 0.3:  # Low engagement
                    await self._weaken_matching_preferences(
                        user_id, content_metadata, (1 - feedback_strength) * 0.3
                    )
            
            return True
            
        except Exception as e:
            logger.error(f"Error updating preferences from feedback: {e}")
            return False

    async def _strengthen_matching_preferences(
        self,
        user_id: str,
        content_metadata: Dict[str, Any],
        strength_boost: float
    ):
        """Strengthen preferences that match the content"""
        
        # This would update preferences in the database
        # For now, log the update
        logger.info(f"Strengthening preferences for user {user_id} by {strength_boost}")
        
        # Extract content attributes that should be strengthened
        category = content_metadata.get('category')
        topics = content_metadata.get('topics', [])
        format_type = content_metadata.get('format')
        
        # Implementation would update corresponding preference strengths
        
    async def _weaken_matching_preferences(
        self,
        user_id: str,
        content_metadata: Dict[str, Any],
        strength_reduction: float
    ):
        """Weaken preferences that match the content"""
        
        # This would update preferences in the database
        logger.info(f"Weakening preferences for user {user_id} by {strength_reduction}")
        
        # Implementation would reduce corresponding preference strengths