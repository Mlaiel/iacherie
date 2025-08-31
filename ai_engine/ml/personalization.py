"""Personalization Engine - Advanced User Experience Personalization
Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

This module provides comprehensive personalization capabilities using machine learning
to create tailored user experiences, content recommendations, and interface adaptations.
"""import logging
import numpy as np
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass
from enum import Enum
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
import json
import random

logger = logging.getLogger(__name__)

class PersonalizationType(Enum):
    """Types of personalization"""    CONTENT_RECOMMENDATION = "content_recommendation"
    UI_ADAPTATION = "ui_adaptation"
    NOTIFICATION_TIMING = "notification_timing"
    CONTENT_FILTERING = "content_filtering"
    INTERACTION_OPTIMIZATION = "interaction_optimization"

class UserSegment(Enum):
    """User segments for personalization"""    MUSIC_CREATOR = "music_creator"
    BLOGGER = "blogger"
    PHOTOGRAPHER = "photographer"
    INFLUENCER = "influencer"
    COMEDIAN = "comedian"
    CASUAL_USER = "casual_user"

class PersonalizationStrategy(Enum):
    """Personalization strategies"""    COLLABORATIVE = "collaborative"
    CONTENT_BASED = "content_based"
    HYBRID = "hybrid"
    DEMOGRAPHIC = "demographic"
    BEHAVIORAL = "behavioral"

@dataclass
class UserProfile:
    """User profile for personalization"""    user_id: str
    segment: UserSegment
    preferences: Dict[str, Any]
    behavior_patterns: Dict[str, Any]
    interaction_history: List[Dict[str, Any]]
    demographics: Dict[str, Any]
    last_updated: datetime

@dataclass
class PersonalizationContext:
    """Context for personalization decisions"""    user_profile: UserProfile
    current_session: Dict[str, Any]
    device_info: Dict[str, Any]
    time_context: Dict[str, Any]
    location_context: Optional[Dict[str, Any]] = None

@dataclass
class PersonalizationResult:
    """Result of personalization operation"""    user_id: str
    personalization_type: PersonalizationType
    recommendations: List[Dict[str, Any]]
    confidence_score: float
    explanation: str
    applied_strategies: List[PersonalizationStrategy]
    timestamp: datetime

class PersonalizationEngine:
    """Main personalization engine"""    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.user_profiles = {}
        self.segment_models = self._initialize_segment_models()
        self.strategy_weights = self._initialize_strategy_weights()
        self.feature_extractors = self._initialize_feature_extractors()
        self.logger.info("PersonalizationEngine initialized successfully")
    
    def _initialize_segment_models(self) -> Dict[str, Any]:
        """Initialize models for different user segments"""        return {
            UserSegment.MUSIC_CREATOR.value: {
                "content_preferences": ["audio", "music_tools", "collaboration"],
                "feature_weights": {"audio_quality": 0.9, "collaboration": 0.8, "monetization": 0.7},
                "interaction_patterns": ["upload_heavy", "collaboration_focused"]
            },
            UserSegment.BLOGGER.value: {
                "content_preferences": ["text_tools", "seo", "analytics"],
                "feature_weights": {"text_quality": 0.9, "seo_optimization": 0.8, "analytics": 0.7},
                "interaction_patterns": ["content_creation", "performance_monitoring"]
            },
            UserSegment.PHOTOGRAPHER.value: {
                "content_preferences": ["image_tools", "portfolio", "rights_protection"],
                "feature_weights": {"image_quality": 0.9, "portfolio": 0.8, "protection": 0.9},
                "interaction_patterns": ["visual_focused", "rights_conscious"]
            },
            UserSegment.INFLUENCER.value: {
                "content_preferences": ["multi_platform", "analytics", "engagement"],
                "feature_weights": {"reach": 0.9, "engagement": 0.9, "analytics": 0.8},
                "interaction_patterns": ["multi_platform", "engagement_driven"]
            },
            UserSegment.COMEDIAN.value: {
                "content_preferences": ["video_tools", "audience_feedback", "timing"],
                "feature_weights": {"humor_analysis": 0.8, "timing": 0.7, "feedback": 0.8},
                "interaction_patterns": ["performance_oriented", "feedback_seeking"]
            }
        }
    
    def _initialize_strategy_weights(self) -> Dict[str, float]:
        """Initialize weights for different personalization strategies"""        return {
            PersonalizationStrategy.COLLABORATIVE.value: 0.3,
            PersonalizationStrategy.CONTENT_BASED.value: 0.3,
            PersonalizationStrategy.BEHAVIORAL.value: 0.2,
            PersonalizationStrategy.DEMOGRAPHIC.value: 0.1,
            PersonalizationStrategy.HYBRID.value: 0.1
        }
    
    def _initialize_feature_extractors(self) -> Dict[str, Any]:
        """Initialize feature extractors for different data types"""        return {
            "behavioral": self._extract_behavioral_features,
            "content": self._extract_content_features,
            "temporal": self._extract_temporal_features,
            "contextual": self._extract_contextual_features
        }
    
    def create_user_profile(self, user_id: str, initial_data: Dict[str, Any]) -> UserProfile:
        """Create a new user profile"""        try:
            # Determine user segment
            segment = self._determine_user_segment(initial_data)
            
            # Extract initial preferences
            preferences = self._extract_initial_preferences(initial_data, segment)
            
            # Initialize behavior patterns
            behavior_patterns = self._initialize_behavior_patterns(segment)
            
            profile = UserProfile(
                user_id=user_id,
                segment=segment,
                preferences=preferences,
                behavior_patterns=behavior_patterns,
                interaction_history=[],
                demographics=initial_data.get('demographics', {}),
                last_updated=datetime.utcnow()
            )
            
            self.user_profiles[user_id] = profile
            self.logger.info(f"Created user profile for {user_id} in segment {segment.value}")
            
            return profile
            
        except Exception as e:
            self.logger.error(f"Failed to create user profile: {e}")
            raise
    
    def update_user_profile(self, user_id: str, interaction_data: Dict[str, Any]) -> UserProfile:
        """Update user profile based on new interaction data"""        try:
            if user_id not in self.user_profiles:
                raise ValueError(f"User profile not found: {user_id}")
            
            profile = self.user_profiles[user_id]
            
            # Add interaction to history
            interaction_data['timestamp'] = datetime.utcnow()
            profile.interaction_history.append(interaction_data)
            
            # Update behavior patterns
            self._update_behavior_patterns(profile, interaction_data)
            
            # Update preferences
            self._update_preferences(profile, interaction_data)
            
            # Update last updated timestamp
            profile.last_updated = datetime.utcnow()
            
            self.logger.info(f"Updated user profile for {user_id}")
            return profile
            
        except Exception as e:
            self.logger.error(f"Failed to update user profile: {e}")
            raise
    
    def personalize(self, context: PersonalizationContext, 
                   personalization_type: PersonalizationType,
                   candidates: List[Dict[str, Any]] = None) -> PersonalizationResult:
        """Generate personalized recommendations"""        try:
            user_profile = context.user_profile
            
            # Extract features for personalization
            features = self._extract_all_features(context)
            
            # Apply different personalization strategies
            strategy_results = {}
            
            if PersonalizationStrategy.COLLABORATIVE in self._get_applicable_strategies(user_profile):
                strategy_results[PersonalizationStrategy.COLLABORATIVE] = \
                    self._apply_collaborative_strategy(context, features, candidates)
            
            if PersonalizationStrategy.CONTENT_BASED in self._get_applicable_strategies(user_profile):
                strategy_results[PersonalizationStrategy.CONTENT_BASED] = \
                    self._apply_content_based_strategy(context, features, candidates)
            
            if PersonalizationStrategy.BEHAVIORAL in self._get_applicable_strategies(user_profile):
                strategy_results[PersonalizationStrategy.BEHAVIORAL] = \
                    self._apply_behavioral_strategy(context, features, candidates)
            
            # Combine strategy results
            combined_recommendations = self._combine_strategy_results(strategy_results)
            
            # Calculate confidence score
            confidence_score = self._calculate_confidence_score(strategy_results, features)
            
            # Generate explanation
            explanation = self._generate_explanation(strategy_results, user_profile, personalization_type)
            
            result = PersonalizationResult(
                user_id=user_profile.user_id,
                personalization_type=personalization_type,
                recommendations=combined_recommendations,
                confidence_score=confidence_score,
                explanation=explanation,
                applied_strategies=list(strategy_results.keys()),
                timestamp=datetime.utcnow()
            )
            
            self.logger.info(f"Generated personalized recommendations for {user_profile.user_id}")
            return result
            
        except Exception as e:
            self.logger.error(f"Personalization failed: {e}")
            raise
    
    def _determine_user_segment(self, initial_data: Dict[str, Any]) -> UserSegment:
        """Determine user segment based on initial data"""        # Simple segment determination based on stated profession/interests
        profession = initial_data.get('profession', '').lower()
        interests = initial_data.get('interests', [])
        
        if 'music' in profession or 'musician' in profession:
            return UserSegment.MUSIC_CREATOR
        elif 'blog' in profession or 'writer' in profession:
            return UserSegment.BLOGGER
        elif 'photo' in profession or 'photographer' in profession:
            return UserSegment.PHOTOGRAPHER
        elif 'influencer' in profession or 'social media' in profession:
            return UserSegment.INFLUENCER
        elif 'comedian' in profession or 'comedy' in profession:
            return UserSegment.COMEDIAN
        else:
            return UserSegment.CASUAL_USER
    
    def _extract_initial_preferences(self, initial_data: Dict[str, Any], segment: UserSegment) -> Dict[str, Any]:
        """Extract initial preferences from user data"""        segment_model = self.segment_models[segment.value]
        
        preferences = {
            'content_types': segment_model['content_preferences'],
            'feature_priorities': segment_model['feature_weights'],
            'notification_frequency': initial_data.get('notification_preference', 'medium'),
            'privacy_level': initial_data.get('privacy_level', 'standard'),
            'ui_complexity': initial_data.get('ui_complexity', 'standard')
        }
        
        return preferences
    
    def _initialize_behavior_patterns(self, segment: UserSegment) -> Dict[str, Any]:
        """Initialize behavior patterns based on segment"""        segment_model = self.segment_models[segment.value]
        
        return {
            'interaction_patterns': segment_model['interaction_patterns'],
            'session_duration': {'mean': 30.0, 'std': 15.0},  # minutes
            'feature_usage': {},
            'content_engagement': {},
            'time_preferences': {'peak_hours': [9, 14, 20]}  # hours of day
        }
    
    def _update_behavior_patterns(self, profile: UserProfile, interaction_data: Dict[str, Any]) -> None:
        """Update behavior patterns based on interaction data"""        patterns = profile.behavior_patterns
        
        # Update feature usage
        features_used = interaction_data.get('features_used', [])
        for feature in features_used:
            patterns['feature_usage'][feature] = patterns['feature_usage'].get(feature, 0) + 1
        
        # Update content engagement
        content_interactions = interaction_data.get('content_interactions', [])
        for interaction in content_interactions:
            content_type = interaction.get('content_type')
            engagement_score = interaction.get('engagement_score', 0)
            
            if content_type:
                if content_type not in patterns['content_engagement']:
                    patterns['content_engagement'][content_type] = []
                patterns['content_engagement'][content_type].append(engagement_score)
        
        # Update session duration
        session_duration = interaction_data.get('session_duration')
        if session_duration:
            current_mean = patterns['session_duration']['mean']
            patterns['session_duration']['mean'] = (current_mean + session_duration) / 2
    
    def _update_preferences(self, profile: UserProfile, interaction_data: Dict[str, Any]) -> None:
        """Update preferences based on interaction data"""        preferences = profile.preferences
        
        # Update content type preferences based on usage
        content_used = interaction_data.get('content_types_used', [])
        for content_type in content_used:
            if content_type not in preferences['content_types']:
                preferences['content_types'].append(content_type)
        
        # Update feature priorities based on usage frequency
        features_used = interaction_data.get('features_used', [])
        for feature in features_used:
            current_weight = preferences['feature_priorities'].get(feature, 0.5)
            # Slightly increase weight for used features
            preferences['feature_priorities'][feature] = min(current_weight + 0.1, 1.0)
    
    def _extract_all_features(self, context: PersonalizationContext) -> Dict[str, Any]:
        """Extract all features for personalization"""        features = {}
        
        for extractor_name, extractor_func in self.feature_extractors.items():
            try:
                features[extractor_name] = extractor_func(context)
            except Exception as e:
                self.logger.warning(f"Failed to extract {extractor_name} features: {e}")
                features[extractor_name] = {}
        
        return features
    
    def _extract_behavioral_features(self, context: PersonalizationContext) -> Dict[str, Any]:
        """Extract behavioral features"""        profile = context.user_profile
        
        # Recent interaction frequency
        recent_interactions = [
            interaction for interaction in profile.interaction_history
            if (datetime.utcnow() - interaction['timestamp']).days <= 7
        ]
        
        # Feature usage patterns
        feature_usage = profile.behavior_patterns.get('feature_usage', {})
        
        # Content engagement patterns
        content_engagement = profile.behavior_patterns.get('content_engagement', {})
        
        return {
            'recent_activity_level': len(recent_interactions),
            'top_features': sorted(feature_usage.items(), key=lambda x: x[1], reverse=True)[:5],
            'content_engagement_scores': {
                content_type: np.mean(scores) if scores else 0
                for content_type, scores in content_engagement.items()
            },
            'session_patterns': profile.behavior_patterns.get('session_duration', {})
        }
    
    def _extract_content_features(self, context: PersonalizationContext) -> Dict[str, Any]:
        """Extract content-based features"""        profile = context.user_profile
        
        return {
            'preferred_content_types': profile.preferences.get('content_types', []),
            'feature_priorities': profile.preferences.get('feature_priorities', {}),
            'segment_preferences': self.segment_models[profile.segment.value]['content_preferences']
        }
    
    def _extract_temporal_features(self, context: PersonalizationContext) -> Dict[str, Any]:
        """Extract temporal features"""        now = datetime.utcnow()
        
        return {
            'hour_of_day': now.hour,
            'day_of_week': now.weekday(),
            'time_since_last_interaction': self._time_since_last_interaction(context.user_profile),
            'session_time': context.current_session.get('duration', 0)
        }
    
    def _extract_contextual_features(self, context: PersonalizationContext) -> Dict[str, Any]:
        """Extract contextual features"""        return {
            'device_type': context.device_info.get('type', 'unknown'),
            'screen_size': context.device_info.get('screen_size', 'medium'),
            'connection_speed': context.device_info.get('connection_speed', 'medium'),
            'location_type': context.location_context.get('type', 'unknown') if context.location_context else 'unknown'
        }
    
    def _get_applicable_strategies(self, profile: UserProfile) -> List[PersonalizationStrategy]:
        """Get applicable strategies for user profile"""        strategies = [PersonalizationStrategy.CONTENT_BASED, PersonalizationStrategy.BEHAVIORAL]
        
        # Add collaborative if enough interaction history
        if len(profile.interaction_history) >= 10:
            strategies.append(PersonalizationStrategy.COLLABORATIVE)
        
        return strategies
    
    def _apply_collaborative_strategy(self, context: PersonalizationContext, 
                                    features: Dict[str, Any], 
                                    candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Apply collaborative filtering strategy"""        # Simulate collaborative filtering
        profile = context.user_profile
        
        # Find similar users (simplified)
        similar_users = self._find_similar_users(profile)
        
        # Get recommendations based on similar users' preferences
        recommendations = []
        if candidates:
            for candidate in candidates[:5]:  # Top 5
                # Simulate collaborative score
                score = random.uniform(0.3, 0.9)
                candidate_copy = candidate.copy()
                candidate_copy['collaborative_score'] = score
                candidate_copy['strategy'] = 'collaborative'
                recommendations.append(candidate_copy)
        
        return recommendations
    
    def _apply_content_based_strategy(self, context: PersonalizationContext,
                                    features: Dict[str, Any],
                                    candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Apply content-based filtering strategy"""        profile = context.user_profile
        content_features = features.get('content', {})
        
        recommendations = []
        if candidates:
            for candidate in candidates[:5]:
                # Calculate content-based score
                score = self._calculate_content_similarity(candidate, content_features)
                candidate_copy = candidate.copy()
                candidate_copy['content_based_score'] = score
                candidate_copy['strategy'] = 'content_based'
                recommendations.append(candidate_copy)
        
        return recommendations
    
    def _apply_behavioral_strategy(self, context: PersonalizationContext,
                                 features: Dict[str, Any],
                                 candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Apply behavioral-based strategy"""        behavioral_features = features.get('behavioral', {})
        
        recommendations = []
        if candidates:
            for candidate in candidates[:5]:
                # Calculate behavioral compatibility score
                score = self._calculate_behavioral_compatibility(candidate, behavioral_features)
                candidate_copy = candidate.copy()
                candidate_copy['behavioral_score'] = score
                candidate_copy['strategy'] = 'behavioral'
                recommendations.append(candidate_copy)
        
        return recommendations
    
    def _combine_strategy_results(self, strategy_results: Dict[PersonalizationStrategy, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """Combine results from different strategies"""        all_recommendations = []
        
        for strategy, recommendations in strategy_results.items():
            weight = self.strategy_weights[strategy.value]
            for rec in recommendations:
                rec['weighted_score'] = rec.get('score', 0.5) * weight
                rec['contributing_strategy'] = strategy.value
                all_recommendations.append(rec)
        
        # Sort by weighted score and return top recommendations
        all_recommendations.sort(key=lambda x: x.get('weighted_score', 0), reverse=True)
        return all_recommendations[:10]
    
    def _calculate_confidence_score(self, strategy_results: Dict[PersonalizationStrategy, List[Dict[str, Any]]], 
                                  features: Dict[str, Any]) -> float:
        """Calculate confidence score for personalization"""        base_confidence = 0.5
        
        # Increase confidence based on number of strategies used
        strategy_bonus = len(strategy_results) * 0.1
        
        # Increase confidence based on user interaction history
        interaction_history_size = len(features.get('behavioral', {}).get('recent_activity_level', 0))
        history_bonus = min(interaction_history_size * 0.05, 0.3)
        
        confidence = base_confidence + strategy_bonus + history_bonus
        return min(confidence, 1.0)
    
    def _generate_explanation(self, strategy_results: Dict[PersonalizationStrategy, List[Dict[str, Any]]],
                            profile: UserProfile, personalization_type: PersonalizationType) -> str:
        """Generate explanation for personalization decisions"""        explanations = []
        
        if PersonalizationStrategy.COLLABORATIVE in strategy_results:
            explanations.append("based on preferences of similar users")
        
        if PersonalizationStrategy.CONTENT_BASED in strategy_results:
            explanations.append("matching your content preferences")
        
        if PersonalizationStrategy.BEHAVIORAL in strategy_results:
            explanations.append("aligned with your usage patterns")
        
        segment_context = f"optimized for {profile.segment.value.replace('_', ' ')} creators"
        
        if explanations:
            return f"Recommendations {', '.join(explanations)} and {segment_context}"
        else:
            return f"Recommendations {segment_context}"
    
    def _find_similar_users(self, profile: UserProfile) -> List[str]:
        """Find users similar to the given profile"""        similar_users = []
        
        for user_id, other_profile in self.user_profiles.items():
            if user_id != profile.user_id and other_profile.segment == profile.segment:
                # Calculate similarity (simplified)
                similarity = self._calculate_user_similarity(profile, other_profile)
                if similarity > 0.7:
                    similar_users.append(user_id)
        
        return similar_users[:10]  # Top 10 similar users
    
    def _calculate_user_similarity(self, profile1: UserProfile, profile2: UserProfile) -> float:
        """Calculate similarity between two user profiles"""        # Simple similarity based on shared preferences
        prefs1 = set(profile1.preferences.get('content_types', []))
        prefs2 = set(profile2.preferences.get('content_types', []))
        
        if not prefs1 and not prefs2:
            return 0.5
        
        intersection = len(prefs1.intersection(prefs2))
        union = len(prefs1.union(prefs2))
        
        return intersection / union if union > 0 else 0.0
    
    def _calculate_content_similarity(self, candidate: Dict[str, Any], content_features: Dict[str, Any]) -> float:
        """Calculate content similarity score"""        # Simulate content similarity calculation
        preferred_types = content_features.get('preferred_content_types', [])
        candidate_type = candidate.get('content_type', 'unknown')
        
        if candidate_type in preferred_types:
            return random.uniform(0.7, 0.95)
        else:
            return random.uniform(0.3, 0.6)
    
    def _calculate_behavioral_compatibility(self, candidate: Dict[str, Any], behavioral_features: Dict[str, Any]) -> float:
        """Calculate behavioral compatibility score"""        # Simulate behavioral compatibility
        activity_level = behavioral_features.get('recent_activity_level', 0)
        
        if activity_level > 10:  # High activity user
            return random.uniform(0.6, 0.9)
        else:  # Low activity user
            return random.uniform(0.4, 0.7)
    
    def _time_since_last_interaction(self, profile: UserProfile) -> int:
        """Calculate time since last interaction in hours"""        if not profile.interaction_history:
            return 24 * 7  # 1 week default
        
        last_interaction = max(profile.interaction_history, key=lambda x: x['timestamp'])
        time_diff = datetime.utcnow() - last_interaction['timestamp']
        return int(time_diff.total_seconds() / 3600)  # Convert to hours
    
    def get_user_insights(self, user_id: str) -> Dict[str, Any]:
        """Get insights about user behavior and preferences"""        if user_id not in self.user_profiles:
            return {"error": "User not found"}
        
        profile = self.user_profiles[user_id]
        
        insights = {
            "user_id": user_id,
            "segment": profile.segment.value,
            "total_interactions": len(profile.interaction_history),
            "top_content_types": list(profile.preferences.get('content_types', [])),
            "engagement_summary": self._calculate_engagement_summary(profile),
            "personalization_effectiveness": self._calculate_personalization_effectiveness(profile),
            "recommendations": {
                "feature_adoption": self._recommend_feature_adoption(profile),
                "content_exploration": self._recommend_content_exploration(profile)
            }
        }
        
        return insights
    
    def _calculate_engagement_summary(self, profile: UserProfile) -> Dict[str, Any]:
        """Calculate engagement summary for user"""        if not profile.interaction_history:
            return {"average_session_duration": 0, "interaction_frequency": 0}
        
        # Calculate average session duration
        sessions = [interaction.get('session_duration', 0) for interaction in profile.interaction_history]
        avg_duration = np.mean(sessions) if sessions else 0
        
        # Calculate interaction frequency (interactions per week)
        recent_interactions = [
            interaction for interaction in profile.interaction_history
            if (datetime.utcnow() - interaction['timestamp']).days <= 7
        ]
        
        return {
            "average_session_duration": avg_duration,
            "interaction_frequency": len(recent_interactions),
            "total_sessions": len(profile.interaction_history)
        }
    
    def _calculate_personalization_effectiveness(self, profile: UserProfile) -> float:
        """Calculate effectiveness of personalization for this user"""        # Simple effectiveness calculation based on interaction patterns
        behavior_patterns = profile.behavior_patterns
        
        # Users with more diverse feature usage indicate good personalization
        feature_diversity = len(behavior_patterns.get('feature_usage', {}))
        
        # Users with consistent engagement indicate effective personalization
        content_engagement = behavior_patterns.get('content_engagement', {})
        avg_engagement = np.mean([
            np.mean(scores) for scores in content_engagement.values() if scores
        ]) if content_engagement else 0.5
        
        # Combine metrics
        effectiveness = (feature_diversity * 0.1 + avg_engagement * 0.9)
        return min(effectiveness, 1.0)
    
    def _recommend_feature_adoption(self, profile: UserProfile) -> List[str]:
        """Recommend features for user to try"""        segment_model = self.segment_models[profile.segment.value]
        recommended_features = segment_model['content_preferences']
        
        used_features = set(profile.behavior_patterns.get('feature_usage', {}).keys())
        available_features = set(recommended_features)
        
        # Recommend unused features from the segment
        unused_features = available_features - used_features
        return list(unused_features)[:3]
    
    def _recommend_content_exploration(self, profile: UserProfile) -> List[str]:
        """Recommend content types for user to explore"""        current_types = set(profile.preferences.get('content_types', []))
        
        # Content types that similar segments also use
        segment_model = self.segment_models[profile.segment.value]
        segment_content = set(segment_model['content_preferences'])
        
        # Recommend unexplored content from segment
        unexplored = segment_content - current_types
        return list(unexplored)[:3]

# Export main class
__all__ = ['PersonalizationEngine', 'UserProfile', 'PersonalizationContext', 'PersonalizationResult']

logger.info("Personalization module loaded successfully")
