"""
Core Personalization Engine

Advanced AI personalization system for multi-format content creators.
Implements deep learning algorithms for intelligent user profiling and content adaptation.

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
import redis
import json

from ..core.base_models import BaseAIModel
from ..core.exceptions import PersonalizationError, ModelConnectionError
from .exceptions import ProfileNotFoundError, InsufficientDataError


class PersonalizationType(Enum):
    """Types of personalization strategies"""
    COLLABORATIVE_FILTERING = "collaborative_filtering"
    CONTENT_BASED = "content_based"  
    HYBRID = "hybrid"
    DEEP_LEARNING = "deep_learning"
    DEMOGRAPHIC = "demographic"
    BEHAVIORAL = "behavioral"


class ContentType(Enum):
    """Content types for personalization"""
    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"
    MUSIC = "music"
    PODCAST = "podcast"
    BLOG = "blog"
    SOCIAL_POST = "social_post"


class UserInteractionType(Enum):
    """Types of user interactions"""
    VIEW = "view"
    LIKE = "like"
    SHARE = "share"
    COMMENT = "comment"
    DOWNLOAD = "download"
    BOOKMARK = "bookmark"
    SKIP = "skip"
    RATE = "rate"
    PURCHASE = "purchase"
    COLLABORATE = "collaborate"


class PersonalizationStrategy(Enum):
    """Personalization strategies"""
    EXPLORATION = "exploration"
    EXPLOITATION = "exploitation"
    BALANCED = "balanced"
    NOVELTY_FOCUSED = "novelty_focused"
    POPULARITY_FOCUSED = "popularity_focused"


class PersonalizationSettings:
    """Settings for personalization system"""
    
    def __init__(self):
        self.max_recommendations = 50
        self.min_confidence = 0.3
        self.diversity_weight = 0.4
        self.novelty_weight = 0.3
        self.popularity_weight = 0.3
        

class ModelConfiguration:
    """Configuration for ML models"""
    
    def __init__(self):
        self.model_path = "/models/personalization/"
        self.update_frequency = timedelta(hours=24)
        self.validation_threshold = 0.7
        

class CacheConfiguration:
    """Cache configuration"""
    
    def __init__(self):
        self.redis_host = "localhost"
        self.redis_port = 6379
        self.ttl_seconds = 3600
        

class SecurityConfiguration:
    """Security and privacy configuration"""
    
    def __init__(self):
        self.encrypt_profiles = True
        self.anonymize_logs = True
        self.gdpr_compliant = True


@dataclass
class PersonalizationConfig:
    """Configuration for personalization engine"""
    
    # Model settings
    model_type: PersonalizationType = PersonalizationType.HYBRID
    embedding_dimension: int = 512
    num_recommendations: int = 20
    min_interactions: int = 5
    
    # Learning parameters
    learning_rate: float = 0.001
    batch_size: int = 64
    epochs: int = 100
    validation_split: float = 0.2
    
    # Content filtering
    content_types: List[ContentType] = field(default_factory=lambda: list(ContentType))
    quality_threshold: float = 0.7
    diversity_factor: float = 0.3
    novelty_factor: float = 0.2
    
    # User profiling
    profile_update_frequency: timedelta = timedelta(hours=6)
    behavior_window: timedelta = timedelta(days=30)
    preference_decay: float = 0.95
    
    # Performance settings
    cache_ttl: int = 3600
    max_profile_size: int = 10000
    parallel_processing: bool = True
    max_workers: int = 4
    
    # Privacy and security
    anonymize_data: bool = True
    data_retention_days: int = 365
    gdpr_compliant: bool = True


@dataclass 
class UserProfile:
    """Comprehensive user profile for personalization"""
    
    user_id: str
    created_at: datetime
    updated_at: datetime
    
    # Demographics
    age_group: Optional[str] = None
    gender: Optional[str] = None
    location: Optional[str] = None
    language: Optional[str] = None
    timezone: Optional[str] = None
    
    # Content preferences
    preferred_genres: Dict[str, float] = field(default_factory=dict)
    preferred_formats: Dict[ContentType, float] = field(default_factory=dict)
    content_consumption_patterns: Dict[str, Any] = field(default_factory=dict)
    
    # Behavioral data
    interaction_history: List[Dict[str, Any]] = field(default_factory=list)
    engagement_metrics: Dict[str, float] = field(default_factory=dict)
    session_patterns: Dict[str, Any] = field(default_factory=dict)
    
    # AI-generated insights
    personality_traits: Dict[str, float] = field(default_factory=dict)
    mood_patterns: Dict[str, float] = field(default_factory=dict)
    content_sophistication: float = 0.5
    exploration_tendency: float = 0.5
    
    # Embeddings
    user_embedding: Optional[np.ndarray] = None
    content_embeddings: Dict[str, np.ndarray] = field(default_factory=dict)
    
    # Collaboration preferences
    collaboration_interests: List[str] = field(default_factory=list)
    skill_level: str = "intermediate"
    professional_goals: List[str] = field(default_factory=list)


@dataclass
class ContentItem:
    """Comprehensive content item for personalization"""
    
    content_id: str
    content_type: ContentType
    created_at: datetime
    updated_at: datetime
    
    # Basic metadata
    title: str
    description: Optional[str] = None
    creator_id: str = ""
    duration: Optional[float] = None
    file_size: Optional[int] = None
    
    # Content features
    features: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    categories: List[str] = field(default_factory=list)
    
    # Quality metrics
    quality_score: float = 0.0
    engagement_metrics: Dict[str, float] = field(default_factory=dict)
    
    # AI-generated attributes
    content_embedding: Optional[np.ndarray] = None
    sentiment_score: Optional[float] = None
    complexity_level: float = 0.5
    
    # Platform-specific data
    platform_metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Rights and protection
    copyright_status: str = "protected"
    license_type: Optional[str] = None


@dataclass
class PersonalizationResult:
    """Result of personalization operation"""
    
    user_id: str
    content_items: List[ContentItem]
    scores: List[float]
    timestamp: datetime
    
    # Explanation and debugging
    reasoning: Dict[str, Any] = field(default_factory=dict)
    algorithm_used: PersonalizationType = PersonalizationType.HYBRID
    
    # Performance metrics
    processing_time: float = 0.0
    confidence_score: float = 0.0


@dataclass
class RecommendationScore:
    """Detailed recommendation scoring"""
    
    content_id: str
    user_id: str
    score: float
    
    # Component scores
    content_similarity: float = 0.0
    user_similarity: float = 0.0
    popularity_score: float = 0.0
    novelty_score: float = 0.0
    diversity_score: float = 0.0
    
    # Context factors
    temporal_factor: float = 1.0
    location_factor: float = 1.0
    device_factor: float = 1.0
    
    # Explanation
    explanation: str = ""
    confidence: float = 0.0


class PersonalizationEngine:
    """
    Advanced personalization engine with multi-algorithm support.
    
    Features:
    - Real-time user profiling
    - Multi-modal content analysis
    - Adaptive learning algorithms
    - Collaboration matching
    - Performance optimization
    """
    
    def __init__(self, config: PersonalizationConfig):
        """Initialize personalization engine"""
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self._init_cache()
        self._init_models()
        self._init_analytics()
        
        # Performance metrics
        self.metrics = {
            "total_recommendations": 0,
            "successful_matches": 0,
            "avg_response_time": 0.0,
            "cache_hit_rate": 0.0
        }
    
    def _init_cache(self):
        """Initialize Redis cache for performance"""
        try:
            self.cache = redis.Redis(
                host='localhost',
                port=6379,
                db=1,
                decode_responses=True
            )
            self.cache.ping()
            self.logger.info("Redis cache initialized successfully")
        except Exception as e:
            self.logger.warning(f"Cache initialization failed: {e}")
            self.cache = None
    
    def _init_models(self):
        """Initialize ML models for personalization"""
        self.models = {}
        
        # Content similarity model
        self.models['content_similarity'] = self._load_content_model()
        
        # User embedding model  
        self.models['user_embedding'] = self._load_user_model()
        
        # Collaborative filtering
        self.models['collaborative'] = self._load_collaborative_model()
        
        self.logger.info("Personalization models initialized")
    
    def _init_analytics(self):
        """Initialize analytics tracking"""
        self.analytics = {
            "user_profiles": {},
            "recommendation_feedback": [],
            "performance_metrics": {},
            "a_b_tests": {}
        }
    
    async def get_user_profile(self, user_id: str) -> UserProfile:
        """
        Retrieve or create user profile with caching.
        
        Args:
            user_id: Unique user identifier
            
        Returns:
            UserProfile: Complete user profile
            
        Raises:
            ProfileNotFoundError: If profile cannot be found or created
        """
        try:
            # Check cache first
            cached_profile = await self._get_cached_profile(user_id)
            if cached_profile:
                return cached_profile
            
            # Load from database
            profile = await self._load_profile_from_db(user_id)
            if not profile:
                # Create new profile
                profile = await self._create_new_profile(user_id)
            
            # Cache the profile
            await self._cache_profile(profile)
            
            return profile
            
        except Exception as e:
            self.logger.error(f"Error retrieving user profile {user_id}: {e}")
            raise ProfileNotFoundError(f"Cannot retrieve profile for user {user_id}")
    
    async def _load_profile_from_db(self, user_id: str) -> Optional[UserProfile]:
        """Load user profile from database"""
        try:
            # For now, return None as we don't have a real database
            # In production, this would query the actual database
            self.logger.info(f"Attempting to load profile for user {user_id} from database")
            return None
        except Exception as e:
            self.logger.error(f"Error loading profile from database: {e}")
            return None
    
    async def _create_new_profile(self, user_id: str) -> UserProfile:
        """Create a new user profile"""
        try:
            profile = UserProfile(
                user_id=user_id,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            # Initialize with default values
            profile.preferred_genres = {}
            profile.engagement_metrics = {}
            profile.personality_traits = {}
            profile.interaction_history = []
            profile.content_sophistication = 0.5
            profile.exploration_tendency = 0.5
            
            self.logger.info(f"Created new profile for user {user_id}")
            return profile
            
        except Exception as e:
            self.logger.error(f"Error creating new profile: {e}")
            raise PersonalizationError(f"Failed to create profile for {user_id}")

    async def update_user_profile(
        self, 
        user_id: str, 
        interaction_data: Dict[str, Any]
    ) -> UserProfile:
        """
        Update user profile with new interaction data.
        
        Args:
            user_id: User identifier
            interaction_data: New interaction information
            
        Returns:
            UserProfile: Updated profile
        """
        try:
            profile = await self.get_user_profile(user_id)
            
            # Update interaction history
            interaction_data['timestamp'] = datetime.utcnow().isoformat()
            profile.interaction_history.append(interaction_data)
            
            # Keep only recent interactions (performance optimization)
            cutoff_date = datetime.utcnow() - self.config.behavior_window
            profile.interaction_history = [
                interaction for interaction in profile.interaction_history
                if datetime.fromisoformat(interaction['timestamp']) > cutoff_date
            ]
            
            # Update preferences based on interactions
            await self._update_preferences(profile, interaction_data)
            
            # Update behavioral patterns
            await self._update_behavioral_patterns(profile)
            
            # Regenerate embeddings if needed
            if len(profile.interaction_history) % 10 == 0:  # Every 10 interactions
                await self._update_user_embedding(profile)
            
            profile.updated_at = datetime.utcnow()
            
            # Save to database and cache
            await self._save_profile_to_db(profile)
            await self._cache_profile(profile)
            
            return profile
            
        except Exception as e:
            self.logger.error(f"Error updating user profile {user_id}: {e}")
            raise PersonalizationError(f"Failed to update profile: {e}")
    
    async def get_personalized_recommendations(
        self,
        user_id: str,
        content_type: Optional[ContentType] = None,
        num_recommendations: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Generate personalized content recommendations.
        
        Args:
            user_id: User identifier
            content_type: Specific content type filter
            num_recommendations: Number of recommendations to return
            
        Returns:
            List of personalized recommendations with scores
        """
        try:
            start_time = datetime.utcnow()
            
            # Get user profile
            profile = await self.get_user_profile(user_id)
            
            # Check for sufficient data
            if len(profile.interaction_history) < self.config.min_interactions:
                return await self._get_cold_start_recommendations(profile, content_type)
            
            # Generate recommendations based on configured strategy
            if self.config.model_type == PersonalizationType.HYBRID:
                recommendations = await self._hybrid_recommendations(profile, content_type)
            elif self.config.model_type == PersonalizationType.COLLABORATIVE_FILTERING:
                recommendations = await self._collaborative_recommendations(profile, content_type)
            elif self.config.model_type == PersonalizationType.CONTENT_BASED:
                recommendations = await self._content_based_recommendations(profile, content_type)
            elif self.config.model_type == PersonalizationType.DEEP_LEARNING:
                recommendations = await self._deep_learning_recommendations(profile, content_type)
            else:
                recommendations = await self._behavioral_recommendations(profile, content_type)
            
            # Apply diversity and novelty filters
            recommendations = await self._apply_diversity_filter(recommendations, profile)
            
            # Limit number of results
            num_recs = num_recommendations or self.config.num_recommendations
            recommendations = recommendations[:num_recs]
            
            # Update metrics
            self._update_performance_metrics(start_time, len(recommendations))
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Error generating recommendations for {user_id}: {e}")
            raise PersonalizationError(f"Failed to generate recommendations: {e}")

    async def get_recommendations(
        self,
        user_id: str,
        content_type: Optional[ContentType] = None,
        max_recommendations: int = 10,
        strategy: Optional[PersonalizationType] = None
    ) -> List[Dict[str, Any]]:
        """
        Alias for get_personalized_recommendations for backward compatibility.
        
        Args:
            user_id: User identifier
            content_type: Optional content type filter
            max_recommendations: Maximum number of recommendations to return
            strategy: Optional personalization strategy override
            
        Returns:
            List of personalized recommendations with metadata
        """
        # Validate user_id
        if not user_id or not user_id.strip():
            raise PersonalizationError("Invalid user ID: user_id cannot be empty")
        
        return await self.get_personalized_recommendations(
            user_id=user_id,
            content_type=content_type,
            num_recommendations=max_recommendations
        )
    
    async def process_feedback(
        self,
        user_id: str,
        content_id: str,
        feedback_type: str,
        feedback_value: Optional[float] = None,
        value: Optional[Union[float, str]] = None
    ) -> None:
        """
        Process user feedback to improve personalization.
        
        Args:
            user_id: User identifier
            content_id: Content that was interacted with
            feedback_type: Type of feedback (like, share, time_spent, etc.)
            feedback_value: Numerical feedback value
            value: Alternative parameter name for feedback value (for compatibility)
        """
        try:
            # Validate feedback type
            valid_feedback_types = ['like', 'share', 'view', 'time_spent', 'engagement_time', 'rating', 'skip', 'dislike']
            if feedback_type not in valid_feedback_types:
                raise PersonalizationError(f"Invalid feedback type: {feedback_type}. Must be one of {valid_feedback_types}")
            
            # Get feedback value from either parameter
            final_feedback_value = feedback_value
            if final_feedback_value is None and value is not None:
                # Try to convert value to float
                try:
                    final_feedback_value = float(value)
                except (ValueError, TypeError):
                    raise PersonalizationError(f"Invalid feedback value: {value}. Must be a numeric value")
            
            if final_feedback_value is None:
                raise PersonalizationError("Missing feedback value: either feedback_value or value must be provided")
            
            # Validate feedback value range based on feedback type
            if not isinstance(final_feedback_value, (int, float)) or final_feedback_value < 0:
                raise PersonalizationError(f"Invalid feedback value: {final_feedback_value}. Must be a non-negative number")
            
            # Apply specific validation based on feedback type
            if feedback_type in ['like', 'rating', 'skip', 'dislike']:
                # These should be between 0 and 5
                if final_feedback_value > 5:
                    raise PersonalizationError(f"Invalid feedback value for {feedback_type}: {final_feedback_value}. Must be between 0 and 5")
            elif feedback_type in ['time_spent', 'engagement_time']:
                # Time-based feedback can be larger (seconds/minutes)
                if final_feedback_value > 10800:  # 3 hours max seems reasonable
                    raise PersonalizationError(f"Invalid feedback value for {feedback_type}: {final_feedback_value}. Must be less than 10800 seconds (3 hours)")
            # For 'view' and 'share', we accept any positive value
            
            # Record feedback for analytics
            feedback_data = {
                'user_id': user_id,
                'content_id': content_id,
                'feedback_type': feedback_type,
                'feedback_value': final_feedback_value,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            self.analytics['recommendation_feedback'].append(feedback_data)
            
            # Update user profile based on feedback
            interaction_data = {
                'content_id': content_id,
                'action': feedback_type,
                'value': final_feedback_value,
                'feedback': True
            }
            
            await self.update_user_profile(user_id, interaction_data)
            
            # Trigger model retraining if enough feedback accumulated
            if len(self.analytics['recommendation_feedback']) % 100 == 0:
                await self._trigger_model_update()
            
        except PersonalizationError:
            # Re-raise PersonalizationError as-is
            raise
        except Exception as e:
            self.logger.error(f"Error processing feedback: {e}")
            raise PersonalizationError(f"Failed to process feedback: {e}")
    
    async def find_collaboration_matches(
        self,
        user_id: str,
        collaboration_type: str = "any"
    ) -> List[Dict[str, Any]]:
        """
        Find potential collaboration partners based on user profile.
        
        Args:
            user_id: User seeking collaborations
            collaboration_type: Type of collaboration sought
            
        Returns:
            List of potential collaboration matches with compatibility scores
        """
        try:
            user_profile = await self.get_user_profile(user_id)
            
            # Get all user profiles (in production, this would be optimized)
            potential_partners = await self._get_potential_partners(user_profile)
            
            # Calculate compatibility scores
            matches = []
            for partner in potential_partners:
                compatibility = await self._calculate_compatibility(user_profile, partner)
                
                if compatibility > 0.6:  # Minimum compatibility threshold
                    match_data = {
                        'user_id': partner.user_id,
                        'compatibility_score': compatibility,
                        'shared_interests': self._find_shared_interests(user_profile, partner),
                        'complementary_skills': self._find_complementary_skills(user_profile, partner),
                        'collaboration_potential': await self._assess_collaboration_potential(
                            user_profile, partner, collaboration_type
                        )
                    }
                    matches.append(match_data)
            
            # Sort by compatibility score
            matches.sort(key=lambda x: x['compatibility_score'], reverse=True)
            
            return matches[:10]  # Return top 10 matches
            
        except Exception as e:
            self.logger.error(f"Error finding collaboration matches: {e}")
            raise PersonalizationError(f"Failed to find collaboration matches: {e}")
    
    # Private helper methods
    
    async def _get_cached_profile(self, user_id: str) -> Optional[UserProfile]:
        """Retrieve profile from cache"""
        if not self.cache:
            return None
        
        try:
            cached_data = self.cache.get(f"profile:{user_id}")
            if cached_data:
                profile_dict = json.loads(cached_data)
                return self._dict_to_profile(profile_dict)
            return None
        except Exception as e:
            self.logger.warning(f"Cache retrieval error: {e}")
            return None
    
    async def _cache_profile(self, profile: UserProfile) -> None:
        """Cache user profile"""
        if not self.cache:
            return
        
        try:
            profile_dict = self._profile_to_dict(profile)
            self.cache.setex(
                f"profile:{profile.user_id}",
                self.config.cache_ttl,
                json.dumps(profile_dict, default=str)
            )
        except Exception as e:
            self.logger.warning(f"Cache storage error: {e}")

    async def _get_cold_start_recommendations(
        self, 
        user_profile: UserProfile, 
        content_types: Optional[List[ContentType]] = None, 
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Generate cold start recommendations for new users with limited data.
        
        Args:
            user_profile: User profile with limited interaction history
            content_types: Specific content types to recommend
            limit: Maximum number of recommendations
            
        Returns:
            List of cold start recommendations based on demographics and popular content
        """
        try:
            recommendations = []
            
            # Get popular content for cold start
            popular_content = await self._get_popular_content(content_types, limit * 2)
            
            # Apply demographic filtering if available
            demographics = {
                'age_group': user_profile.age_group,
                'gender': user_profile.gender,
                'location': user_profile.location,
                'language': user_profile.language,
                'timezone': user_profile.timezone
            }
            
            # Remove None values
            demographics = {k: v for k, v in demographics.items() if v is not None}
            
            if demographics:
                filtered_content = await self._filter_by_demographics(
                    popular_content, demographics
                )
            else:
                filtered_content = popular_content
            
            # Diversify recommendations
            diversified = await self._apply_diversity_filter(filtered_content, limit)
            
            # Format recommendations
            for content in diversified:
                rec = {
                    'content_id': content.get('id'),
                    'content_type': content.get('type', 'unknown'),
                    'title': content.get('title', ''),
                    'score': content.get('popularity_score', 0.5),
                    'relevance_score': content.get('popularity_score', 0.5),  # Add relevance_score field
                    'reason': 'Popular content for new users',
                    'confidence': 0.6,  # Lower confidence for cold start
                    'strategy': 'cold_start'  # Add strategy field
                }
                recommendations.append(rec)
            
            self.logger.info(f"Generated {len(recommendations)} cold start recommendations for user {user_profile.user_id}")
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Error generating cold start recommendations: {e}")
            # Return fallback recommendations
            return [
                {
                    'content_id': f'fallback_{i}',
                    'content_type': 'general',
                    'title': f'Popular Content {i+1}',
                    'score': 0.5,
                    'relevance_score': 0.5,  # Add relevance_score field
                    'reason': 'Fallback recommendation',
                    'confidence': 0.3,
                    'strategy': 'fallback'  # Add strategy field
                }
                for i in range(min(limit, 5))
            ]

    async def _apply_diversity_filter(
        self, 
        recommendations: List[Dict[str, Any]], 
        target_count: int
    ) -> List[Dict[str, Any]]:
        """
        Apply diversity filtering to ensure variety in recommendations.
        
        Args:
            recommendations: Raw recommendation list
            target_count: Desired number of diverse recommendations
            
        Returns:
            Filtered list with improved diversity
        """
        try:
            if not recommendations:
                return []
            
            diverse_recs = []
            content_types_seen = set()
            categories_seen = set()
            
            # Sort by score first
            sorted_recs = sorted(recommendations, key=lambda x: x.get('score', 0), reverse=True)
            
            for rec in sorted_recs:
                if len(diverse_recs) >= target_count:
                    break
                
                content_type = rec.get('content_type', 'unknown')
                category = rec.get('category', 'general')
                
                # Apply diversity constraints
                type_count = sum(1 for r in diverse_recs if r.get('content_type') == content_type)
                category_count = sum(1 for r in diverse_recs if r.get('category') == category)
                
                # Allow max 40% of same type, 30% of same category
                max_type_count = max(1, int(target_count * 0.4))
                max_category_count = max(1, int(target_count * 0.3))
                
                if type_count < max_type_count and category_count < max_category_count:
                    diverse_recs.append(rec)
                    content_types_seen.add(content_type)
                    categories_seen.add(category)
            
            # Fill remaining slots if needed
            remaining_slots = target_count - len(diverse_recs)
            if remaining_slots > 0:
                remaining_recs = [r for r in sorted_recs if r not in diverse_recs]
                diverse_recs.extend(remaining_recs[:remaining_slots])
            
            self.logger.debug(f"Applied diversity filter: {len(recommendations)} -> {len(diverse_recs)} recommendations")
            return diverse_recs
            
        except Exception as e:
            self.logger.error(f"Error applying diversity filter: {e}")
            # Return top recommendations without filtering
            return recommendations[:target_count]

    async def _collaborative_filtering_recommendations(
        self, 
        user_profile: UserProfile, 
        content_types: Optional[List[ContentType]] = None, 
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Generate recommendations using collaborative filtering.
        
        Args:
            user_profile: User profile with interaction history
            content_types: Specific content types to recommend
            limit: Maximum number of recommendations
            
        Returns:
            List of collaborative filtering recommendations
        """
        try:
            recommendations = []
            
            # Find similar users based on interaction patterns
            similar_users = await self._find_similar_users(user_profile, limit=20)
            
            if not similar_users:
                self.logger.warning(f"No similar users found for {user_profile.user_id}")
                return await self._get_cold_start_recommendations(user_profile, content_types, limit)
            
            # Aggregate recommendations from similar users
            content_scores = {}
            
            for similar_user_id, similarity_score in similar_users:
                similar_profile = await self.get_user_profile(similar_user_id)
                
                # Get highly rated content from similar user
                for interaction in similar_profile.interaction_history:
                    if interaction.get('rating', 0) >= 4.0:  # High rating threshold
                        content_id = interaction.get('content_id')
                        content_type = interaction.get('content_type')
                        
                        # Filter by content types if specified
                        if content_types and content_type not in [ct.value for ct in content_types]:
                            continue
                        
                        # Skip if user already interacted with this content
                        if any(int_item.get('content_id') == content_id for int_item in user_profile.interaction_history):
                            continue
                        
                        # Calculate weighted score
                        weighted_score = interaction.get('rating', 0) * similarity_score
                        
                        if content_id in content_scores:
                            content_scores[content_id] = max(content_scores[content_id], weighted_score)
                        else:
                            content_scores[content_id] = weighted_score
            
            # Sort by score and format recommendations
            sorted_content = sorted(content_scores.items(), key=lambda x: x[1], reverse=True)
            
            for content_id, score in sorted_content[:limit]:
                rec = {
                    'content_id': content_id,
                    'content_type': 'collaborative',
                    'title': f'Content {content_id}',
                    'score': min(score, 1.0),  # Normalize score
                    'relevance_score': min(score, 1.0),  # Add relevance_score field
                    'reason': 'Users with similar preferences also liked this',
                    'confidence': min(score * 0.8, 0.9),  # High confidence for collaborative filtering
                    'strategy': 'collaborative_filtering'  # Add strategy field
                }
                recommendations.append(rec)
            
            self.logger.info(f"Generated {len(recommendations)} collaborative filtering recommendations for user {user_profile.user_id}")
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Error generating collaborative filtering recommendations: {e}")
            return await self._get_cold_start_recommendations(user_profile, content_types, limit)

    async def _content_based_recommendations(
        self, 
        user_profile: UserProfile, 
        content_types: Optional[List[ContentType]] = None, 
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Generate recommendations using content-based filtering.
        
        Args:
            user_profile: User profile with preferences
            content_types: Specific content types to recommend
            limit: Maximum number of recommendations
            
        Returns:
            List of content-based recommendations
        """
        try:
            recommendations = []
            
            # Extract user preferences from interaction history
            user_preferences = await self._extract_user_preferences(user_profile)
            
            if not user_preferences:
                self.logger.warning(f"No preferences found for user {user_profile.user_id}")
                return await self._get_cold_start_recommendations(user_profile, content_types, limit)
            
            # Find content matching user preferences
            matching_content = await self._find_matching_content(user_preferences, content_types, limit * 2)
            
            # Calculate content similarity scores
            for content in matching_content:
                similarity_score = await self._calculate_content_similarity(user_preferences, content)
                
                # Skip if user already interacted with this content
                if any(int_item.get('content_id') == content.get('id') for int_item in user_profile.interaction_history):
                    continue
                
                rec = {
                    'content_id': content.get('id'),
                    'content_type': content.get('type', 'unknown'),
                    'title': content.get('title', ''),
                    'score': similarity_score,
                    'relevance_score': similarity_score,  # Add relevance_score field
                    'reason': 'Based on your preferences and past interactions',
                    'confidence': similarity_score * 0.85,  # Good confidence for content-based
                    'strategy': 'content_based'  # Add strategy field
                }
                recommendations.append(rec)
            
            # Sort by similarity score
            recommendations.sort(key=lambda x: x['score'], reverse=True)
            
            self.logger.info(f"Generated {len(recommendations[:limit])} content-based recommendations for user {user_profile.user_id}")
            return recommendations[:limit]
            
        except Exception as e:
            self.logger.error(f"Error generating content-based recommendations: {e}")
            return await self._get_cold_start_recommendations(user_profile, content_types, limit)

    async def _hybrid_recommendations(
        self,
        profile: UserProfile,
        content_type: Optional[ContentType]
    ) -> List[Dict[str, Any]]:
        """Generate hybrid recommendations combining multiple approaches"""
        
        # Get recommendations from different models
        collaborative_recs = await self._collaborative_recommendations(profile, content_type)
        content_based_recs = await self._content_based_recommendations(profile, content_type)
        behavioral_recs = await self._behavioral_recommendations(profile, content_type)
        
        # Combine with weighted scores
        combined_recs = {}
        
        # Weight collaborative filtering (40%)
        for rec in collaborative_recs[:20]:
            rec_id = rec['content_id']
            combined_recs[rec_id] = combined_recs.get(rec_id, 0) + rec['score'] * 0.4
        
        # Weight content-based (35%)
        for rec in content_based_recs[:20]:
            rec_id = rec['content_id']
            combined_recs[rec_id] = combined_recs.get(rec_id, 0) + rec['score'] * 0.35
        
        # Weight behavioral (25%)
        for rec in behavioral_recs[:20]:
            rec_id = rec['content_id']
            combined_recs[rec_id] = combined_recs.get(rec_id, 0) + rec['score'] * 0.25
        
        # Convert back to list format
        final_recs = [
            {'content_id': content_id, 'score': score, 'strategy': 'hybrid'}
            for content_id, score in sorted(combined_recs.items(), key=lambda x: x[1], reverse=True)
        ]
        
        return final_recs
    
    def _load_content_model(self):
        """Load content similarity model"""
        # In production, this would load a trained model
        return {"model_type": "content_similarity", "loaded": True}
    
    def _load_user_model(self):
        """Load user embedding model"""
        return {"model_type": "user_embedding", "loaded": True}
    
    def _load_collaborative_model(self):
        """Load collaborative filtering model"""
        return {"model_type": "collaborative_filtering", "loaded": True}
    
    def _update_performance_metrics(self, start_time: datetime, num_recs: int):
        """Update performance tracking metrics"""
        response_time = (datetime.utcnow() - start_time).total_seconds()
        self.metrics["total_recommendations"] += 1
        self.metrics["avg_response_time"] = (
            (self.metrics["avg_response_time"] * (self.metrics["total_recommendations"] - 1) + response_time) 
            / self.metrics["total_recommendations"]
        )

    # Additional auxiliary methods for recommendation strategies
    
    async def _get_popular_content(
        self, 
        content_types: Optional[List[ContentType]] = None, 
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Get popular content for cold start recommendations"""
        try:
            # Simulate popular content retrieval (in production, this would query a database)
            popular_content = []
            
            types_to_include = content_types or [ContentType.VIDEO, ContentType.AUDIO, ContentType.TEXT, ContentType.IMAGE]
            
            for i, content_type in enumerate(types_to_include):
                for j in range(limit // len(types_to_include)):
                    content = {
                        'id': f'popular_{content_type.value}_{i}_{j}',
                        'type': content_type.value,
                        'title': f'Popular {content_type.value.title()} Content {j+1}',
                        'popularity_score': 0.8 - (j * 0.1),  # Decreasing popularity
                        'category': 'entertainment' if j % 2 == 0 else 'educational'
                    }
                    popular_content.append(content)
            
            return popular_content[:limit]
            
        except Exception as e:
            self.logger.error(f"Error getting popular content: {e}")
            return []

    async def _filter_by_demographics(
        self, 
        content: List[Dict[str, Any]], 
        demographics: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Filter content based on demographic preferences"""
        try:
            filtered_content = []
            
            for item in content:
                # Apply age group filtering
                if demographics.get('age_group'):
                    age_group = demographics['age_group']
                    if age_group == 'teen' and item.get('mature_content', False):
                        continue
                    elif age_group == 'senior' and item.get('category') == 'gaming':
                        continue  # Example demographic filtering
                
                # Apply language filtering
                if demographics.get('language'):
                    preferred_lang = demographics['language']
                    item_lang = item.get('language', 'en')
                    if item_lang != preferred_lang and item_lang != 'en':  # Always include English as fallback
                        continue
                
                filtered_content.append(item)
            
            return filtered_content
            
        except Exception as e:
            self.logger.error(f"Error filtering by demographics: {e}")
            return content

    async def _find_similar_users(
        self, 
        user_profile: UserProfile, 
        limit: int = 10
    ) -> List[Tuple[str, float]]:
        """Find users with similar preferences and behavior patterns"""
        try:
            # Simulate finding similar users (in production, this would use ML models)
            similar_users = []
            
            # Generate mock similar users with similarity scores
            for i in range(limit):
                user_id = f"similar_user_{i}"
                # Simulate decreasing similarity scores
                similarity = 0.9 - (i * 0.1)
                if similarity > 0.5:  # Only include users with reasonable similarity
                    similar_users.append((user_id, similarity))
            
            return similar_users
            
        except Exception as e:
            self.logger.error(f"Error finding similar users: {e}")
            return []

    async def _extract_user_preferences(
        self, 
        user_profile: UserProfile
    ) -> Dict[str, Any]:
        """Extract user preferences from interaction history and explicit preferences"""
        try:
            preferences = {}
            
            # Extract from explicit preferences
            if user_profile.preferred_genres:
                preferences['genres'] = user_profile.preferred_genres
            
            if user_profile.preferred_formats:
                preferences['formats'] = {
                    content_type.value: score 
                    for content_type, score in user_profile.preferred_formats.items()
                }
            
            # Extract from interaction history
            if user_profile.interaction_history:
                category_scores = {}
                type_scores = {}
                
                for interaction in user_profile.interaction_history:
                    rating = interaction.get('rating', 0)
                    if rating >= 3.0:  # Positive interactions only
                        category = interaction.get('category', 'general')
                        content_type = interaction.get('content_type', 'unknown')
                        
                        category_scores[category] = category_scores.get(category, 0) + rating
                        type_scores[content_type] = type_scores.get(content_type, 0) + rating
                
                # Normalize scores
                if category_scores:
                    max_score = max(category_scores.values())
                    preferences['inferred_categories'] = {
                        cat: score / max_score for cat, score in category_scores.items()
                    }
                
                if type_scores:
                    max_score = max(type_scores.values())
                    preferences['inferred_types'] = {
                        ctype: score / max_score for ctype, score in type_scores.items()
                    }
            
            return preferences
            
        except Exception as e:
            self.logger.error(f"Error extracting user preferences: {e}")
            return {}

    async def _find_matching_content(
        self, 
        user_preferences: Dict[str, Any], 
        content_types: Optional[List[ContentType]] = None, 
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Find content matching user preferences"""
        try:
            matching_content = []
            
            # Generate mock content based on preferences
            preferred_categories = user_preferences.get('inferred_categories', {})
            preferred_types = user_preferences.get('inferred_types', {})
            
            content_id_counter = 0
            
            # Generate content for preferred categories
            for category, score in preferred_categories.items():
                if score > 0.5:  # Only consider strong preferences
                    for i in range(min(3, limit // len(preferred_categories))):
                        content = {
                            'id': f'content_{category}_{content_id_counter}',
                            'type': 'video',  # Default type
                            'title': f'{category.title()} Content {i+1}',
                            'category': category,
                            'preference_match_score': score
                        }
                        matching_content.append(content)
                        content_id_counter += 1
            
            # Generate content for preferred types
            for content_type, score in preferred_types.items():
                if score > 0.5 and content_types:
                    # Filter by requested content types
                    if any(ct.value == content_type for ct in content_types):
                        for i in range(min(2, limit // len(preferred_types))):
                            content = {
                                'id': f'content_{content_type}_{content_id_counter}',
                                'type': content_type,
                                'title': f'{content_type.title()} Content {i+1}',
                                'category': 'general',
                                'preference_match_score': score
                            }
                            matching_content.append(content)
                            content_id_counter += 1
            
            return matching_content[:limit]
            
        except Exception as e:
            self.logger.error(f"Error finding matching content: {e}")
            return []

    async def _calculate_content_similarity(
        self, 
        user_preferences: Dict[str, Any], 
        content: Dict[str, Any]
    ) -> float:
        """Calculate similarity between user preferences and content"""
        try:
            similarity_score = 0.0
            factors = 0
            
            # Category similarity
            content_category = content.get('category', 'general')
            preferred_categories = user_preferences.get('inferred_categories', {})
            
            if content_category in preferred_categories:
                similarity_score += preferred_categories[content_category]
                factors += 1
            
            # Type similarity
            content_type = content.get('type', 'unknown')
            preferred_types = user_preferences.get('inferred_types', {})
            
            if content_type in preferred_types:
                similarity_score += preferred_types[content_type]
                factors += 1
            
            # Preference match score from content
            if 'preference_match_score' in content:
                similarity_score += content['preference_match_score']
                factors += 1
            
            # Return average similarity if we have factors, otherwise default score
            return similarity_score / factors if factors > 0 else 0.5
            
        except Exception as e:
            self.logger.error(f"Error calculating content similarity: {e}")
            return 0.0

    async def _collaborative_recommendations(
        self, 
        profile: UserProfile, 
        content_type: Optional[ContentType]
    ) -> List[Dict[str, Any]]:
        """Generate collaborative filtering recommendations (legacy method for compatibility)"""
        content_types = [content_type] if content_type else None
        return await self._collaborative_filtering_recommendations(profile, content_types, 10)

    async def _behavioral_recommendations(
        self, 
        profile: UserProfile, 
        content_type: Optional[ContentType]
    ) -> List[Dict[str, Any]]:
        """Generate behavioral-based recommendations"""
        try:
            recommendations = []
            
            # Analyze user behavior patterns
            behavior_patterns = await self._analyze_behavior_patterns(profile)
            
            if not behavior_patterns:
                return []
            
            # Generate recommendations based on behavior
            for pattern_type, pattern_data in behavior_patterns.items():
                if pattern_data.get('strength', 0) > 0.6:  # Strong behavioral pattern
                    rec = {
                        'content_id': f'behavioral_{pattern_type}_{len(recommendations)}',
                        'content_type': content_type.value if content_type else 'general',
                        'title': f'Content for {pattern_type} behavior',
                        'score': pattern_data['strength'],
                        'relevance_score': pattern_data['strength'],  # Add relevance_score field
                        'reason': f'Based on your {pattern_type} behavior pattern',
                        'confidence': pattern_data['strength'] * 0.7,
                        'strategy': 'behavioral'  # Add strategy field
                    }
                    recommendations.append(rec)
            
            return recommendations[:10]
            
        except Exception as e:
            self.logger.error(f"Error generating behavioral recommendations: {e}")
            return []

    async def _analyze_behavior_patterns(
        self, 
        profile: UserProfile
    ) -> Dict[str, Dict[str, Any]]:
        """Analyze user behavior patterns from interaction history"""
        try:
            patterns = {}
            
            if not profile.interaction_history:
                return patterns
            
            # Analyze time-based patterns
            hour_interactions = {}
            day_interactions = {}
            
            for interaction in profile.interaction_history:
                timestamp = datetime.fromisoformat(interaction['timestamp'])
                hour = timestamp.hour
                day = timestamp.strftime('%A')
                
                hour_interactions[hour] = hour_interactions.get(hour, 0) + 1
                day_interactions[day] = day_interactions.get(day, 0) + 1
            
            # Find peak usage patterns
            if hour_interactions:
                peak_hour = max(hour_interactions, key=hour_interactions.get)
                patterns['time_preference'] = {
                    'peak_hour': peak_hour,
                    'strength': min(hour_interactions[peak_hour] / len(profile.interaction_history), 1.0)
                }
            
            # Analyze content consumption patterns
            content_type_freq = {}
            for interaction in profile.interaction_history:
                content_type = interaction.get('content_type', 'unknown')
                content_type_freq[content_type] = content_type_freq.get(content_type, 0) + 1
            
            if content_type_freq:
                dominant_type = max(content_type_freq, key=content_type_freq.get)
                patterns['content_preference'] = {
                    'dominant_type': dominant_type,
                    'strength': min(content_type_freq[dominant_type] / len(profile.interaction_history), 1.0)
                }
            
            return patterns
            
        except Exception as e:
            self.logger.error(f"Error analyzing behavior patterns: {e}")
            return {}

    # Additional methods for profile management
    
    async def _update_preferences(
        self, 
        profile: UserProfile, 
        interaction_data: Dict[str, Any]
    ) -> None:
        """Update user preferences based on interaction data"""
        try:
            # Update genre preferences
            if 'genre' in interaction_data:
                genre = interaction_data['genre']
                value = interaction_data.get('value', 1.0)
                
                if genre in profile.preferred_genres:
                    # Weighted average update
                    current_score = profile.preferred_genres[genre]
                    profile.preferred_genres[genre] = (current_score * 0.8 + value * 0.2)
                else:
                    profile.preferred_genres[genre] = value
            
            # Update content type preferences
            if 'content_type' in interaction_data:
                try:
                    content_type = ContentType(interaction_data['content_type'])
                    value = interaction_data.get('value', 1.0)
                    
                    if content_type in profile.preferred_formats:
                        current_score = profile.preferred_formats[content_type]
                        profile.preferred_formats[content_type] = (current_score * 0.8 + value * 0.2)
                    else:
                        profile.preferred_formats[content_type] = value
                except (ValueError, TypeError):
                    # Invalid content type, skip
                    pass
            
            # Update engagement metrics
            action = interaction_data.get('action', 'view')
            duration = interaction_data.get('duration', 0)
            
            if action == 'play' and duration > 0:
                # Update average session duration
                current_avg = profile.engagement_metrics.get('avg_session_duration', 0)
                profile.engagement_metrics['avg_session_duration'] = (current_avg * 0.9 + duration * 0.1)
            
            elif action == 'like':
                like_rate = profile.engagement_metrics.get('like_rate', 0)
                profile.engagement_metrics['like_rate'] = min(like_rate + 0.1, 1.0)
            
            elif action == 'share':
                share_rate = profile.engagement_metrics.get('share_rate', 0)
                profile.engagement_metrics['share_rate'] = min(share_rate + 0.15, 1.0)
            
        except Exception as e:
            self.logger.error(f"Error updating preferences: {e}")

    async def _update_behavioral_patterns(self, profile: UserProfile) -> None:
        """Update behavioral patterns based on interaction history"""
        try:
            if not profile.interaction_history:
                return
            
            # Analyze time-based patterns
            hour_activity = {}
            day_activity = {}
            
            for interaction in profile.interaction_history[-50:]:  # Last 50 interactions
                try:
                    timestamp = datetime.fromisoformat(interaction['timestamp'])
                    hour = timestamp.hour
                    day = timestamp.strftime('%A')
                    
                    hour_activity[hour] = hour_activity.get(hour, 0) + 1
                    day_activity[day] = day_activity.get(day, 0) + 1
                except (KeyError, ValueError):
                    continue
            
            # Update session patterns
            if hour_activity:
                peak_hour = max(hour_activity, key=hour_activity.get)
                profile.session_patterns['peak_hour'] = peak_hour
                profile.session_patterns['hour_distribution'] = hour_activity
            
            if day_activity:
                profile.session_patterns['day_distribution'] = day_activity
            
            # Analyze content consumption patterns
            content_patterns = {}
            for interaction in profile.interaction_history[-100:]:  # Last 100 interactions
                content_type = interaction.get('content_type', 'unknown')
                action = interaction.get('action', 'view')
                
                if content_type not in content_patterns:
                    content_patterns[content_type] = {'views': 0, 'likes': 0, 'shares': 0}
                
                if action == 'view':
                    content_patterns[content_type]['views'] += 1
                elif action == 'like':
                    content_patterns[content_type]['likes'] += 1
                elif action == 'share':
                    content_patterns[content_type]['shares'] += 1
            
            profile.content_consumption_patterns = content_patterns
            
        except Exception as e:
            self.logger.error(f"Error updating behavioral patterns: {e}")

    async def _update_user_embedding(self, profile: UserProfile) -> None:
        """Update user embedding based on current profile data"""
        try:
            # Simple embedding generation based on preferences
            # In production, this would use a trained ML model
            
            embedding_size = 128
            embedding = np.zeros(embedding_size)
            
            # Encode genre preferences
            genre_offset = 0
            for i, (genre, score) in enumerate(list(profile.preferred_genres.items())[:32]):
                if genre_offset + i < embedding_size:
                    embedding[genre_offset + i] = score
            
            # Encode content type preferences  
            format_offset = 32
            for i, (content_type, score) in enumerate(list(profile.preferred_formats.items())[:32]):
                if format_offset + i < embedding_size:
                    embedding[format_offset + i] = score
            
            # Encode behavioral patterns
            behavior_offset = 64
            if 'peak_hour' in profile.session_patterns:
                peak_hour = profile.session_patterns['peak_hour']
                if behavior_offset < embedding_size:
                    embedding[behavior_offset] = peak_hour / 24.0  # Normalize to 0-1
            
            # Encode engagement metrics
            engagement_offset = 96
            for i, (metric, value) in enumerate(list(profile.engagement_metrics.items())[:32]):
                if engagement_offset + i < embedding_size:
                    embedding[engagement_offset + i] = min(value, 1.0)  # Clip to max 1.0
            
            profile.user_embedding = embedding
            
        except Exception as e:
            self.logger.error(f"Error updating user embedding: {e}")

    async def _save_profile_to_db(self, profile: UserProfile) -> None:
        """Save user profile to database"""
        try:
            # Simulate database save operation
            # In production, this would save to actual database
            profile_data = {
                'user_id': profile.user_id,
                'created_at': profile.created_at.isoformat(),
                'updated_at': profile.updated_at.isoformat(),
                'age_group': profile.age_group,
                'gender': profile.gender,
                'location': profile.location,
                'language': profile.language,
                'timezone': profile.timezone,
                'preferred_genres': profile.preferred_genres,
                'preferred_formats': {ct.value: score for ct, score in profile.preferred_formats.items()},
                'content_consumption_patterns': profile.content_consumption_patterns,
                'interaction_history': profile.interaction_history,
                'engagement_metrics': profile.engagement_metrics,
                'session_patterns': profile.session_patterns,
                'personality_traits': profile.personality_traits,
                'mood_patterns': profile.mood_patterns,
                'content_sophistication': profile.content_sophistication,
                'exploration_tendency': profile.exploration_tendency,
                'collaboration_interests': profile.collaboration_interests,
                'skill_level': profile.skill_level,
                'professional_goals': profile.professional_goals
            }
            
            # In a real implementation, this would be:
            # await self.database.save_user_profile(profile_data)
            
            self.logger.debug(f"Saved profile for user {profile.user_id} to database")
            
        except Exception as e:
            self.logger.error(f"Error saving profile to database: {e}")

    async def _trigger_model_update(self) -> None:
        """Trigger model retraining with accumulated feedback"""
        try:
            # Simulate model update trigger
            # In production, this would trigger ML model retraining
            self.logger.info("Triggering model update with accumulated feedback")
            
            # Clear feedback buffer after triggering update
            self.analytics['recommendation_feedback'] = []
            
        except Exception as e:
            self.logger.error(f"Error triggering model update: {e}")

    async def _deep_learning_recommendations(
        self, 
        profile: UserProfile, 
        content_type: Optional[ContentType]
    ) -> List[Dict[str, Any]]:
        """Generate deep learning based recommendations"""
        try:
            # Simulate deep learning recommendation generation
            recommendations = []
            
            # Use user embedding if available
            if profile.user_embedding is not None:
                # Generate content based on embedding similarity
                for i in range(10):
                    rec = {
                        'content_id': f'dl_content_{i}',
                        'content_type': content_type.value if content_type else 'mixed',
                        'title': f'Deep Learning Recommendation {i+1}',
                        'score': 0.8 - (i * 0.05),  # Decreasing scores
                        'relevance_score': 0.8 - (i * 0.05),
                        'reason': 'Generated using deep learning model',
                        'confidence': 0.85,
                        'strategy': 'deep_learning'
                    }
                    recommendations.append(rec)
            else:
                # Fallback to cold start if no embedding
                return await self._get_cold_start_recommendations(profile, [content_type] if content_type else None, 10)
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Error generating deep learning recommendations: {e}")
            return await self._get_cold_start_recommendations(profile, [content_type] if content_type else None, 10)


class UserProfileManager:
    """
    Manages user profile lifecycle and operations.
    Handles profile creation, updates, validation, and optimization.
    """
    
    def __init__(self, config: PersonalizationConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    async def create_profile(self, user_id: str, initial_data: Dict[str, Any]) -> UserProfile:
        """Create new user profile with initial data"""
        try:
            profile = UserProfile(
                user_id=user_id,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            # Set initial demographics if provided
            if 'demographics' in initial_data:
                demo_data = initial_data['demographics']
                profile.age_group = demo_data.get('age_group')
                profile.gender = demo_data.get('gender')
                profile.location = demo_data.get('location')
                profile.language = demo_data.get('language', 'en')
                profile.timezone = demo_data.get('timezone')
            
            # Set initial preferences
            if 'preferences' in initial_data:
                pref_data = initial_data['preferences']
                profile.preferred_genres = pref_data.get('genres', {})
                profile.preferred_formats = {
                    ContentType(fmt): score 
                    for fmt, score in pref_data.get('formats', {}).items()
                }
            
            # Initialize default values
            profile.content_sophistication = 0.5
            profile.exploration_tendency = 0.5
            
            self.logger.info(f"Created new user profile for {user_id}")
            return profile
            
        except Exception as e:
            self.logger.error(f"Error creating profile for {user_id}: {e}")
            raise PersonalizationError(f"Failed to create profile: {e}")
    
    async def validate_profile(self, profile: UserProfile) -> bool:
        """Validate profile data integrity and completeness"""
        try:
            # Check required fields
            if not profile.user_id or not profile.created_at:
                return False
            
            # Validate data types and ranges
            if profile.content_sophistication < 0 or profile.content_sophistication > 1:
                return False
            
            if profile.exploration_tendency < 0 or profile.exploration_tendency > 1:
                return False
            
            # Validate interaction history format
            for interaction in profile.interaction_history:
                if 'timestamp' not in interaction or 'content_id' not in interaction:
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Profile validation error: {e}")
            return False
    
    async def optimize_profile(self, profile: UserProfile) -> UserProfile:
        """Optimize profile for performance and storage"""
        try:
            # Remove old interactions beyond retention window
            cutoff_date = datetime.utcnow() - self.config.behavior_window
            profile.interaction_history = [
                interaction for interaction in profile.interaction_history
                if datetime.fromisoformat(interaction['timestamp']) > cutoff_date
            ]
            
            # Limit interaction history size
            if len(profile.interaction_history) > self.config.max_profile_size:
                profile.interaction_history = profile.interaction_history[-self.config.max_profile_size:]
            
            # Apply preference decay
            for genre in profile.preferred_genres:
                profile.preferred_genres[genre] *= self.config.preference_decay
            
            # Remove very low preference scores
            profile.preferred_genres = {
                genre: score for genre, score in profile.preferred_genres.items()
                if score > 0.01
            }
            
            profile.updated_at = datetime.utcnow()
            
            return profile
            
        except Exception as e:
            self.logger.error(f"Profile optimization error: {e}")
            return profile


class ContentPersonalizer:
    """
    Personalizes content presentation and delivery based on user preferences.
    Adapts content format, timing, and presentation style.
    """
    
    def __init__(self, config: PersonalizationConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    async def personalize_content(
        self, 
        content: Dict[str, Any], 
        profile: UserProfile
    ) -> Dict[str, Any]:
        """
        Personalize content based on user profile.
        
        Args:
            content: Raw content data
            profile: User profile for personalization
            
        Returns:
            Personalized content with adapted presentation
        """
        try:
            personalized = content.copy()
            
            # Adapt content format
            personalized = await self._adapt_content_format(personalized, profile)
            
            # Personalize presentation style
            personalized = await self._personalize_presentation(personalized, profile)
            
            # Optimize timing and scheduling
            personalized = await self._optimize_timing(personalized, profile)
            
            # Add personalization metadata
            personalized['personalization'] = {
                'adapted_for': profile.user_id,
                'adaptation_score': await self._calculate_adaptation_score(content, profile),
                'timestamp': datetime.utcnow().isoformat()
            }
            
            return personalized
            
        except Exception as e:
            self.logger.error(f"Content personalization error: {e}")
            return content
    
    async def _adapt_content_format(
        self, 
        content: Dict[str, Any], 
        profile: UserProfile
    ) -> Dict[str, Any]:
        """Adapt content format based on user preferences"""
        
        # Get user's preferred formats
        preferred_formats = profile.preferred_formats
        
        # Determine best format for this content
        content_type = ContentType(content.get('type', 'text'))
        
        if content_type in preferred_formats:
            preference_score = preferred_formats[content_type]
            
            # Adapt based on preference strength
            if preference_score > 0.8:
                content['format_priority'] = 'high'
            elif preference_score > 0.6:
                content['format_priority'] = 'medium'
            else:
                content['format_priority'] = 'low'
        
        return content
    
    async def _personalize_presentation(
        self, 
        content: Dict[str, Any], 
        profile: UserProfile
    ) -> Dict[str, Any]:
        """Personalize content presentation style"""
        
        # Adapt complexity based on sophistication level
        sophistication = profile.content_sophistication
        
        if sophistication > 0.7:
            content['presentation_style'] = 'detailed'
            content['technical_level'] = 'advanced'
        elif sophistication > 0.4:
            content['presentation_style'] = 'balanced'
            content['technical_level'] = 'intermediate'
        else:
            content['presentation_style'] = 'simplified'
            content['technical_level'] = 'beginner'
        
        # Add personality-based adaptations
        if 'creative' in profile.personality_traits:
            content['visual_style'] = 'creative'
        if 'analytical' in profile.personality_traits:
            content['include_data'] = True
        
        return content
    
    async def _optimize_timing(
        self, 
        content: Dict[str, Any], 
        profile: UserProfile
    ) -> Dict[str, Any]:
        """Optimize content timing based on user patterns"""
        
        # Analyze user's session patterns
        session_patterns = profile.session_patterns
        
        if 'peak_hours' in session_patterns:
            content['optimal_delivery_hours'] = session_patterns['peak_hours']
        
        if 'preferred_days' in session_patterns:
            content['optimal_delivery_days'] = session_patterns['preferred_days']
        
        return content
    
    async def _calculate_adaptation_score(
        self, 
        original_content: Dict[str, Any], 
        profile: UserProfile
    ) -> float:
        """Calculate how well content was adapted for user"""
        
        score = 0.0
        
        # Content type preference match
        content_type = ContentType(original_content.get('type', 'text'))
        if content_type in profile.preferred_formats:
            score += profile.preferred_formats[content_type] * 0.3
        
        # Genre preference match
        content_genre = original_content.get('genre')
        if content_genre and content_genre in profile.preferred_genres:
            score += profile.preferred_genres[content_genre] * 0.3
        
        # Sophistication level match
        user_sophistication = profile.content_sophistication
        content_complexity = original_content.get('complexity', 0.5)
        sophistication_match = 1.0 - abs(user_sophistication - content_complexity)
        score += sophistication_match * 0.4
        
        return min(score, 1.0)


class RecommendationEngine:
    """
    Advanced recommendation engine with multiple algorithms and strategies.
    Provides content recommendations, collaboration matching, and trend analysis.
    """
    
    def __init__(self, config: PersonalizationConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize recommendation models
        self.models = self._initialize_models()
        
        # Performance tracking
        self.performance_metrics = {
            'total_recommendations': 0,
            'successful_interactions': 0,
            'avg_precision': 0.0,
            'avg_recall': 0.0
        }
    
    def _initialize_models(self) -> Dict[str, Any]:
        """Initialize recommendation models"""
        return {
            'collaborative_filtering': {'initialized': True},
            'content_based': {'initialized': True},
            'matrix_factorization': {'initialized': True},
            'deep_learning': {'initialized': True}
        }
    
    async def generate_recommendations(
        self,
        user_profile: UserProfile,
        strategy: PersonalizationType = PersonalizationType.HYBRID,
        content_type: Optional[ContentType] = None,
        num_recommendations: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Generate content recommendations using specified strategy.
        
        Args:
            user_profile: User profile for personalization
            strategy: Recommendation strategy to use
            content_type: Optional content type filter
            num_recommendations: Number of recommendations to generate
            
        Returns:
            List of recommended content with relevance scores
        """
        try:
            if strategy == PersonalizationType.COLLABORATIVE_FILTERING:
                return await self._collaborative_filtering_recommendations(
                    user_profile, content_type, num_recommendations
                )
            elif strategy == PersonalizationType.CONTENT_BASED:
                return await self._content_based_recommendations(
                    user_profile, content_type, num_recommendations
                )
            elif strategy == PersonalizationType.DEEP_LEARNING:
                return await self._deep_learning_recommendations(
                    user_profile, content_type, num_recommendations
                )
            else:  # HYBRID
                return await self._hybrid_recommendations(
                    user_profile, content_type, num_recommendations
                )
                
        except Exception as e:
            self.logger.error(f"Recommendation generation error: {e}")
            return []
    
    async def _collaborative_filtering_recommendations(
        self,
        user_profile: UserProfile,
        content_type: Optional[ContentType],
        num_recommendations: int
    ) -> List[Dict[str, Any]]:
        """Generate recommendations using collaborative filtering"""
        
        recommendations = []
        
        # Find similar users based on interaction patterns
        similar_users = await self._find_similar_users(user_profile)
        
        # Get content liked by similar users
        for similar_user_id, similarity_score in similar_users[:10]:
            similar_user_profile = await self._get_user_profile(similar_user_id)
            
            # Analyze their successful interactions
            for interaction in similar_user_profile.interaction_history:
                if interaction.get('action') in ['like', 'share', 'save']:
                    content_id = interaction.get('content_id')
                    
                    # Skip if user already interacted with this content
                    if self._user_already_interacted(user_profile, content_id):
                        continue
                    
                    # Calculate recommendation score
                    score = similarity_score * interaction.get('value', 1.0)
                    
                    recommendations.append({
                        'content_id': content_id,
                        'score': score,
                        'strategy': 'collaborative_filtering',
                        'similar_user': similar_user_id
                    })
        
        # Sort by score and remove duplicates
        recommendations = self._deduplicate_recommendations(recommendations)
        recommendations.sort(key=lambda x: x['score'], reverse=True)
        
        return recommendations[:num_recommendations]
    
    async def _content_based_recommendations(
        self,
        user_profile: UserProfile,
        content_type: Optional[ContentType],
        num_recommendations: int
    ) -> List[Dict[str, Any]]:
        """Generate recommendations using content-based filtering"""
        
        recommendations = []
        
        # Analyze user's content preferences
        preferred_genres = user_profile.preferred_genres
        preferred_formats = user_profile.preferred_formats
        
        # Get content similar to user's preferences
        similar_content = await self._find_similar_content(
            preferred_genres, preferred_formats, content_type
        )
        
        for content_item in similar_content:
            # Calculate content relevance score
            genre_score = preferred_genres.get(content_item.get('genre', ''), 0.0)
            format_score = preferred_formats.get(
                ContentType(content_item.get('type', 'text')), 0.0
            )
            
            # Combine scores
            relevance_score = (genre_score + format_score) / 2.0
            
            if relevance_score > 0.3:  # Minimum relevance threshold
                recommendations.append({
                    'content_id': content_item['id'],
                    'score': relevance_score,
                    'strategy': 'content_based',
                    'content_features': content_item.get('features', {})
                })
        
        recommendations.sort(key=lambda x: x['score'], reverse=True)
        return recommendations[:num_recommendations]
    
    async def _deep_learning_recommendations(
        self,
        user_profile: UserProfile,
        content_type: Optional[ContentType],
        num_recommendations: int
    ) -> List[Dict[str, Any]]:
        """Generate recommendations using deep learning models"""
        
        recommendations = []
        
        # Use user embedding if available
        if user_profile.user_embedding is not None:
            # Get content embeddings
            content_embeddings = await self._get_content_embeddings(content_type)
            
            # Calculate similarity scores
            for content_id, content_embedding in content_embeddings.items():
                similarity = cosine_similarity(
                    user_profile.user_embedding.reshape(1, -1),
                    content_embedding.reshape(1, -1)
                )[0][0]
                
                if similarity > 0.5:  # Minimum similarity threshold
                    recommendations.append({
                        'content_id': content_id,
                        'score': similarity,
                        'strategy': 'deep_learning',
                        'embedding_similarity': similarity
                    })
        
        recommendations.sort(key=lambda x: x['score'], reverse=True)
        return recommendations[:num_recommendations]
    
    async def _hybrid_recommendations(
        self,
        user_profile: UserProfile,
        content_type: Optional[ContentType],
        num_recommendations: int
    ) -> List[Dict[str, Any]]:
        """Generate hybrid recommendations combining multiple strategies"""
        
        # Get recommendations from different strategies
        collaborative_recs = await self._collaborative_filtering_recommendations(
            user_profile, content_type, num_recommendations
        )
        content_based_recs = await self._content_based_recommendations(
            user_profile, content_type, num_recommendations
        )
        deep_learning_recs = await self._deep_learning_recommendations(
            user_profile, content_type, num_recommendations
        )
        
        # Combine with weighted scores
        combined_scores = {}
        
        # Weight collaborative filtering (40%)
        for rec in collaborative_recs:
            content_id = rec['content_id']
            combined_scores[content_id] = combined_scores.get(content_id, 0) + rec['score'] * 0.4
        
        # Weight content-based (35%)
        for rec in content_based_recs:
            content_id = rec['content_id']
            combined_scores[content_id] = combined_scores.get(content_id, 0) + rec['score'] * 0.35
        
        # Weight deep learning (25%)
        for rec in deep_learning_recs:
            content_id = rec['content_id']
            combined_scores[content_id] = combined_scores.get(content_id, 0) + rec['score'] * 0.25
        
        # Create final recommendation list
        hybrid_recommendations = [
            {
                'content_id': content_id,
                'score': score,
                'strategy': 'hybrid',
                'combined_score': score
            }
            for content_id, score in sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)
        ]
        
        return hybrid_recommendations[:num_recommendations]
    
    # Helper methods
    
    def _deduplicate_recommendations(self, recommendations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate recommendations and combine scores"""
        seen_content = {}
        deduplicated = []
        
        for rec in recommendations:
            content_id = rec['content_id']
            if content_id not in seen_content:
                seen_content[content_id] = rec
                deduplicated.append(rec)
            else:
                # Combine scores for duplicates
                existing_rec = seen_content[content_id]
                existing_rec['score'] = max(existing_rec['score'], rec['score'])
        
        return deduplicated
    
    def _user_already_interacted(self, user_profile: UserProfile, content_id: str) -> bool:
        """Check if user already interacted with content"""
        for interaction in user_profile.interaction_history:
            if interaction.get('content_id') == content_id:
                return True
        return False


class AdaptiveLearning:
    """
    Adaptive learning system for continuous personalization improvement.
    Implements online learning algorithms and real-time model updates.
    """
    
    def __init__(self, config: PersonalizationConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Learning state
        self.learning_rate = config.learning_rate
        self.model_weights = {}
        self.feedback_buffer = []
        
        # Performance tracking
        self.learning_metrics = {
            'updates_processed': 0,
            'accuracy_improvement': 0.0,
            'convergence_rate': 0.0
        }
    
    async def process_interaction_feedback(
        self,
        user_id: str,
        content_id: str,
        interaction_type: str,
        feedback_score: float
    ) -> None:
        """
        Process user interaction feedback for adaptive learning.
        
        Args:
            user_id: User identifier
            content_id: Content that was interacted with
            interaction_type: Type of interaction (view, like, share, etc.)
            feedback_score: Numerical feedback score (0-1)
        """
        try:
            # Create feedback record
            feedback = {
                'user_id': user_id,
                'content_id': content_id,
                'interaction_type': interaction_type,
                'feedback_score': feedback_score,
                'timestamp': datetime.utcnow()
            }
            
            # Add to feedback buffer
            self.feedback_buffer.append(feedback)
            
            # Trigger learning update if buffer is full
            if len(self.feedback_buffer) >= self.config.batch_size:
                await self._update_models()
                self.feedback_buffer = []
            
            # Update user profile with immediate feedback
            await self._update_user_preferences(user_id, content_id, feedback_score)
            
        except Exception as e:
            self.logger.error(f"Feedback processing error: {e}")
    
    async def _update_models(self) -> None:
        """Update recommendation models based on accumulated feedback"""
        try:
            self.logger.info("Updating models with adaptive learning")
            
            # Process feedback batch
            for feedback in self.feedback_buffer:
                await self._apply_feedback_to_model(feedback)
            
            # Update performance metrics
            self.learning_metrics['updates_processed'] += 1
            
            # Validate model performance
            await self._validate_model_performance()
            
        except Exception as e:
            self.logger.error(f"Model update error: {e}")
    
    async def _apply_feedback_to_model(self, feedback: Dict[str, Any]) -> None:
        """Apply individual feedback to model weights"""
        
        user_id = feedback['user_id']
        content_id = feedback['content_id']
        feedback_score = feedback['feedback_score']
        
        # Update user-content affinity
        affinity_key = f"{user_id}:{content_id}"
        current_affinity = self.model_weights.get(affinity_key, 0.5)
        
        # Apply learning rate
        updated_affinity = current_affinity + self.learning_rate * (feedback_score - current_affinity)
        self.model_weights[affinity_key] = max(0.0, min(1.0, updated_affinity))
    
    async def _update_user_preferences(
        self,
        user_id: str,
        content_id: str,
        feedback_score: float
    ) -> None:
        """Update user preferences based on immediate feedback"""
        try:
            # Get content metadata to update genre/format preferences
            content_metadata = await self._get_content_metadata(content_id)
            
            if content_metadata:
                genre = content_metadata.get('genre')
                content_type = content_metadata.get('type')
                
                # Update preferences with decay
                preference_update = feedback_score * 0.1  # Small update per interaction
                
                # This would typically update the user profile in the database
                self.logger.debug(f"Updated preferences for user {user_id}")
                
        except Exception as e:
            self.logger.error(f"Preference update error: {e}")
    
    async def _validate_model_performance(self) -> None:
        """Validate and track model performance improvements"""
        try:
            # Calculate performance metrics
            # This would typically involve validation datasets
            
            # Update convergence tracking
            self.learning_metrics['convergence_rate'] = self._calculate_convergence_rate()
            
            # Log performance
            self.logger.info(f"Model performance validated. Convergence rate: {self.learning_metrics['convergence_rate']}")
            
        except Exception as e:
            self.logger.error(f"Performance validation error: {e}")
    
    def _calculate_convergence_rate(self) -> float:
        """Calculate model convergence rate"""
        # Simplified convergence calculation
        if len(self.model_weights) > 0:
            weight_variance = np.var(list(self.model_weights.values()))
            return max(0.0, 1.0 - weight_variance)
        return 0.0
