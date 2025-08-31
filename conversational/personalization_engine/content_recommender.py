"""Content Recommender
==================

Industrial-grade ML-powered content recommendation engine for IA Influencer Agent.
Provides intelligent content recommendations, collaborative filtering, content-based filtering,
hybrid recommendations, and real-time personalized content discovery.

Business Logic:
User (musician/blogger/photographer/influencer/comedian) → Upload multi-format → AI rights protection → Professional SEO → Collaboration matching → Multi-platform distribution

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.
License: Proprietary - Unauthorized use strictly prohibited

WARNING: Any attempt to steal, copy, or use the concept, idea, or code without explicit written permission from Fahed Mlaiel (mlaiel@live.de) is strictly prohibited and will be prosecuted.
"""import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
import tensorflow as tf
import faiss
import json

from ..core.base_service import BaseService
from ..core.exceptions import RecommendationError, ValidationError
from ..database.mongodb import MongoDBHandler
from ..database.vector_store import VectorStore
from ..cache.redis_cache import RedisCache
from ..ml.embedding_models import ContentEmbeddingModel
from ..ml.recommendation_models import CollaborativeFilteringModel, ContentBasedModel

logger = logging.getLogger(__name__)


class RecommendationType(str, Enum):
    """Types of recommendations"""    CONTENT_DISCOVERY = "content_discovery"
    COLLABORATION_MATCHING = "collaboration_matching"
    TRENDING_CONTENT = "trending_content"
    SIMILAR_CREATORS = "similar_creators"
    LEARNING_RESOURCES = "learning_resources"
    TOOLS_AND_SERVICES = "tools_and_services"
    INSPIRATION = "inspiration"


class RecommendationStrategy(str, Enum):
    """Recommendation generation strategies"""    COLLABORATIVE_FILTERING = "collaborative_filtering"
    CONTENT_BASED = "content_based"
    HYBRID = "hybrid"
    DEEP_LEARNING = "deep_learning"
    POPULARITY_BASED = "popularity_based"
    TRENDING = "trending"
    PERSONALIZED_RANKING = "personalized_ranking"


class ContentCategory(str, Enum):
    """Content categories for recommendations"""    AUDIO_MUSIC = "audio_music"
    VIDEO_CONTENT = "video_content"
    IMAGE_PHOTOGRAPHY = "image_photography"
    TEXT_BLOG = "text_blog"
    EDUCATIONAL = "educational"
    ENTERTAINMENT = "entertainment"
    TOOLS_SOFTWARE = "tools_software"
    COLLABORATION = "collaboration"


@dataclass
class RecommendationRequest:
    """Request for content recommendations"""    user_id: str
    recommendation_type: RecommendationType
    strategy: Optional[RecommendationStrategy] = None
    content_categories: Optional[List[ContentCategory]] = None
    max_recommendations: int = 20
    include_explanations: bool = False
    filter_criteria: Dict[str, Any] = field(default_factory=dict)
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RecommendationItem:
    """Individual recommendation item"""    item_id: str
    item_type: str
    title: str
    description: str
    category: ContentCategory
    creator_id: Optional[str] = None
    creator_name: Optional[str] = None
    relevance_score: float = 0.0
    confidence_score: float = 0.0
    reasoning: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)


@dataclass
class RecommendationResponse:
    """Response containing recommendations"""    request_id: str
    user_id: str
    recommendation_type: RecommendationType
    strategy_used: RecommendationStrategy
    recommendations: List[RecommendationItem]
    total_available: int
    personalization_factors: Dict[str, float]
    explanation: Optional[str] = None
    generated_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class UserProfile:
    """User profile for recommendations"""    user_id: str
    content_preferences: Dict[str, float]
    creator_affinities: Dict[str, float]
    genre_preferences: Dict[str, float]
    platform_preferences: Dict[str, float]
    collaboration_interests: List[str]
    skill_level: str
    creative_goals: List[str]
    interaction_history: List[Dict[str, Any]]
    last_updated: datetime


class ContentRecommender(BaseService):
    """    Enterprise-grade content recommendation engine
    """    
    def __init__(
        self,
        mongodb_handler: MongoDBHandler,
        vector_store: VectorStore,
        redis_cache: RedisCache,
        embedding_model: ContentEmbeddingModel,
        collaborative_model: CollaborativeFilteringModel,
        content_based_model: ContentBasedModel
    ):
        super().__init__()
        self.mongodb = mongodb_handler
        self.vector_store = vector_store
        self.redis_cache = redis_cache
        self.embedding_model = embedding_model
        self.collaborative_model = collaborative_model
        self.content_based_model = content_based_model
        
        # Configuration
        self.cache_ttl = 1800  # 30 minutes
        self.min_relevance_score = 0.3
        self.max_recommendations_per_strategy = 50
        self.diversity_factor = 0.3
        self.freshness_factor = 0.2
        
        # Model weights for hybrid recommendations
        self.strategy_weights = {
            RecommendationStrategy.COLLABORATIVE_FILTERING: 0.4,
            RecommendationStrategy.CONTENT_BASED: 0.3,
            RecommendationStrategy.DEEP_LEARNING: 0.2,
            RecommendationStrategy.TRENDING: 0.1
        }
        
        # Internal state
        self._user_profiles = {}
        self._content_features = {}
        self._similarity_cache = {}
        
        logger.info("ContentRecommender initialized successfully")

    async def initialize(self) -> None:
        """Initialize content recommender"""        try:
            # Initialize ML models
            await self.embedding_model.initialize()
            await self.collaborative_model.initialize()
            await self.content_based_model.initialize()
            
            # Load content features
            await self._load_content_features()
            
            # Initialize vector store
            await self.vector_store.initialize()
            
            logger.info("ContentRecommender initialization completed")
            
        except Exception as e:
            logger.error(f"Failed to initialize ContentRecommender: {e}")
            raise RecommendationError(f"Initialization failed: {e}")

    async def get_recommendations(
        self,
        request: RecommendationRequest
    ) -> RecommendationResponse:
        """        Generate personalized content recommendations
        
        Args:
            request: Recommendation request with user context
            
        Returns:
            Personalized recommendations response
        """        try:
            request_id = f"rec_{int(datetime.now().timestamp())}"
            
            # Validate request
            await self._validate_recommendation_request(request)
            
            # Get user profile
            user_profile = await self._get_user_profile(request.user_id)
            
            # Check cache
            cache_key = await self._generate_cache_key(request, user_profile)
            cached_result = await self.redis_cache.get(cache_key)
            if cached_result:
                cached_response = RecommendationResponse(**json.loads(cached_result))
                cached_response.request_id = request_id
                return cached_response
            
            # Determine strategy
            strategy = request.strategy or await self._select_optimal_strategy(
                user_profile, request
            )
            
            # Generate recommendations based on strategy
            recommendations = await self._generate_recommendations_by_strategy(
                strategy, user_profile, request
            )
            
            # Apply filters
            filtered_recommendations = await self._apply_filters(
                recommendations, request.filter_criteria
            )
            
            # Diversify recommendations
            diversified_recommendations = await self._diversify_recommendations(
                filtered_recommendations, request.max_recommendations
            )
            
            # Calculate personalization factors
            personalization_factors = await self._calculate_personalization_factors(
                user_profile, diversified_recommendations, strategy
            )
            
            # Generate explanation if requested
            explanation = None
            if request.include_explanations:
                explanation = await self._generate_recommendation_explanation(
                    user_profile, diversified_recommendations, strategy
                )
            
            # Create response
            response = RecommendationResponse(
                request_id=request_id,
                user_id=request.user_id,
                recommendation_type=request.recommendation_type,
                strategy_used=strategy,
                recommendations=diversified_recommendations,
                total_available=len(recommendations),
                personalization_factors=personalization_factors,
                explanation=explanation,
                metadata={
                    "processing_time_ms": 0,  # Calculate actual time
                    "user_profile_confidence": user_profile.get("confidence", 0.0) if isinstance(user_profile, dict) else 0.0,
                    "cache_hit": False,
                    "filter_criteria_applied": bool(request.filter_criteria)
                }
            )
            
            # Cache response
            await self.redis_cache.setex(
                cache_key, self.cache_ttl, json.dumps(response.__dict__, default=str)
            )
            
            # Track recommendation interaction
            await self._track_recommendation_served(request, response)
            
            logger.info(f"Recommendations generated for user {request.user_id}")
            return response
            
        except Exception as e:
            logger.error(f"Failed to generate recommendations: {e}")
            raise RecommendationError(f"Recommendation generation failed: {e}")

    async def update_user_feedback(
        self,
        user_id: str,
        item_id: str,
        feedback_type: str,
        feedback_value: float,
        context: Optional[Dict[str, Any]] = None
    ) -> bool:
        """        Update user feedback for recommendation improvement
        
        Args:
            user_id: User identifier
            item_id: Item that received feedback
            feedback_type: Type of feedback (like, dislike, click, view, etc.)
            feedback_value: Numerical feedback value
            context: Additional context information
            
        Returns:
            Success status
        """        try:
            # Store feedback
            feedback_data = {
                "user_id": user_id,
                "item_id": item_id,
                "feedback_type": feedback_type,
                "feedback_value": feedback_value,
                "context": context or {},
                "timestamp": datetime.now().isoformat()
            }
            
            await self.mongodb.insert_one("recommendation_feedback", feedback_data)
            
            # Update user profile
            await self._update_user_profile_from_feedback(
                user_id, item_id, feedback_type, feedback_value
            )
            
            # Update ML models
            await self._update_models_from_feedback(feedback_data)
            
            # Invalidate relevant caches
            await self._invalidate_user_caches(user_id)
            
            logger.info(f"User feedback updated for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update user feedback: {e}")
            return False

    async def get_trending_content(
        self,
        category: Optional[ContentCategory] = None,
        time_window: int = 24,  # hours
        max_results: int = 50
    ) -> List[RecommendationItem]:
        """        Get trending content based on recent interactions
        
        Args:
            category: Content category filter
            time_window: Time window in hours for trending calculation
            max_results: Maximum number of results
            
        Returns:
            List of trending content items
        """        try:
            # Calculate trending period
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=time_window)
            
            # Get interaction data
            trending_data = await self._calculate_trending_scores(
                start_time, end_time, category
            )
            
            # Convert to recommendation items
            trending_items = []
            for item_data in trending_data[:max_results]:
                trending_item = await self._create_recommendation_item_from_data(
                    item_data, "trending"
                )
                trending_items.append(trending_item)
            
            logger.info(f"Retrieved {len(trending_items)} trending items")
            return trending_items
            
        except Exception as e:
            logger.error(f"Failed to get trending content: {e}")
            return []

    async def get_similar_creators(
        self,
        user_id: str,
        max_results: int = 20
    ) -> List[Dict[str, Any]]:
        """        Find creators similar to the given user
        
        Args:
            user_id: Target user identifier
            max_results: Maximum number of similar creators
            
        Returns:
            List of similar creators with similarity scores
        """        try:
            # Get user profile
            user_profile = await self._get_user_profile(user_id)
            
            # Calculate user embedding
            user_embedding = await self._calculate_user_embedding(user_profile)
            
            # Find similar users using vector similarity
            similar_user_ids = await self.vector_store.find_similar(
                "user_embeddings", user_embedding, max_results + 1
            )
            
            # Remove self from results
            similar_user_ids = [uid for uid in similar_user_ids if uid != user_id]
            
            # Get creator information
            similar_creators = []
            for similar_user_id in similar_user_ids[:max_results]:
                creator_info = await self._get_creator_info(similar_user_id)
                if creator_info:
                    similarity_score = await self._calculate_creator_similarity(
                        user_profile, creator_info
                    )
                    creator_info["similarity_score"] = similarity_score
                    similar_creators.append(creator_info)
            
            # Sort by similarity score
            similar_creators.sort(key=lambda x: x["similarity_score"], reverse=True)
            
            logger.info(f"Found {len(similar_creators)} similar creators for user {user_id}")
            return similar_creators
            
        except Exception as e:
            logger.error(f"Failed to get similar creators: {e}")
            return []

    # Private helper methods
    
    async def _validate_recommendation_request(
        self,
        request: RecommendationRequest
    ) -> None:
        """Validate recommendation request"""        if not request.user_id:
            raise ValidationError("User ID is required")
        
        if request.max_recommendations <= 0 or request.max_recommendations > 100:
            raise ValidationError("Max recommendations must be between 1 and 100")
        
        if request.content_categories:
            for category in request.content_categories:
                if category not in ContentCategory:
                    raise ValidationError(f"Invalid content category: {category}")

    async def _get_user_profile(self, user_id: str) -> UserProfile:
        """Get user profile for recommendations"""        try:
            # Check cache
            cache_key = f"user_profile:{user_id}"
            cached_profile = await self.redis_cache.get(cache_key)
            if cached_profile:
                profile_data = json.loads(cached_profile)
                return UserProfile(**profile_data)
            
            # Load from database
            profile_data = await self.mongodb.find_one(
                "user_profiles", {"user_id": user_id}
            )
            
            if not profile_data:
                # Create basic profile
                profile_data = await self._create_basic_user_profile(user_id)
            
            # Create UserProfile object
            user_profile = UserProfile(
                user_id=user_id,
                content_preferences=profile_data.get("content_preferences", {}),
                creator_affinities=profile_data.get("creator_affinities", {}),
                genre_preferences=profile_data.get("genre_preferences", {}),
                platform_preferences=profile_data.get("platform_preferences", {}),
                collaboration_interests=profile_data.get("collaboration_interests", []),
                skill_level=profile_data.get("skill_level", "beginner"),
                creative_goals=profile_data.get("creative_goals", []),
                interaction_history=profile_data.get("interaction_history", []),
                last_updated=datetime.fromisoformat(
                    profile_data.get("last_updated", datetime.now().isoformat())
                )
            )
            
            # Cache profile
            await self.redis_cache.setex(
                cache_key, self.cache_ttl, json.dumps(user_profile.__dict__, default=str)
            )
            
            return user_profile
            
        except Exception as e:
            logger.error(f"Failed to get user profile: {e}")
            # Return basic profile as fallback
            return await self._create_basic_user_profile(user_id)

    async def _generate_recommendations_by_strategy(
        self,
        strategy: RecommendationStrategy,
        user_profile: UserProfile,
        request: RecommendationRequest
    ) -> List[RecommendationItem]:
        """Generate recommendations using specified strategy"""        try:
            if strategy == RecommendationStrategy.COLLABORATIVE_FILTERING:
                return await self._generate_collaborative_recommendations(
                    user_profile, request
                )
            elif strategy == RecommendationStrategy.CONTENT_BASED:
                return await self._generate_content_based_recommendations(
                    user_profile, request
                )
            elif strategy == RecommendationStrategy.HYBRID:
                return await self._generate_hybrid_recommendations(
                    user_profile, request
                )
            elif strategy == RecommendationStrategy.DEEP_LEARNING:
                return await self._generate_deep_learning_recommendations(
                    user_profile, request
                )
            elif strategy == RecommendationStrategy.POPULARITY_BASED:
                return await self._generate_popularity_based_recommendations(
                    user_profile, request
                )
            elif strategy == RecommendationStrategy.TRENDING:
                return await self._generate_trending_recommendations(
                    user_profile, request
                )
            elif strategy == RecommendationStrategy.PERSONALIZED_RANKING:
                return await self._generate_personalized_ranking_recommendations(
                    user_profile, request
                )
            else:
                # Default to hybrid
                return await self._generate_hybrid_recommendations(
                    user_profile, request
                )
                
        except Exception as e:
            logger.error(f"Failed to generate recommendations with strategy {strategy}: {e}")
            return []

    async def _generate_collaborative_recommendations(
        self,
        user_profile: UserProfile,
        request: RecommendationRequest
    ) -> List[RecommendationItem]:
        """Generate collaborative filtering recommendations"""        try:
            # Get user interaction matrix
            user_item_matrix = await self._build_user_item_matrix(user_profile.user_id)
            
            # Generate collaborative filtering predictions
            recommendations = await self.collaborative_model.predict(
                user_profile.user_id, user_item_matrix, request.max_recommendations
            )
            
            # Convert to RecommendationItem objects
            recommendation_items = []
            for rec in recommendations:
                item = await self._create_recommendation_item(
                    rec["item_id"], rec["score"], "collaborative_filtering"
                )
                if item:
                    recommendation_items.append(item)
            
            return recommendation_items
            
        except Exception as e:
            logger.error(f"Failed to generate collaborative recommendations: {e}")
            return []

    async def _generate_content_based_recommendations(
        self,
        user_profile: UserProfile,
        request: RecommendationRequest
    ) -> List[RecommendationItem]:
        """Generate content-based filtering recommendations"""        try:
            # Get user content preferences
            content_preferences = user_profile.content_preferences
            
            # Generate content-based predictions
            recommendations = await self.content_based_model.predict(
                content_preferences, request.max_recommendations
            )
            
            # Convert to RecommendationItem objects
            recommendation_items = []
            for rec in recommendations:
                item = await self._create_recommendation_item(
                    rec["item_id"], rec["score"], "content_based"
                )
                if item:
                    recommendation_items.append(item)
            
            return recommendation_items
            
        except Exception as e:
            logger.error(f"Failed to generate content-based recommendations: {e}")
            return []

    async def _generate_hybrid_recommendations(
        self,
        user_profile: UserProfile,
        request: RecommendationRequest
    ) -> List[RecommendationItem]:
        """Generate hybrid recommendations combining multiple strategies"""        try:
            # Generate recommendations from multiple strategies
            collaborative_recs = await self._generate_collaborative_recommendations(
                user_profile, request
            )
            content_based_recs = await self._generate_content_based_recommendations(
                user_profile, request
            )
            trending_recs = await self._generate_trending_recommendations(
                user_profile, request
            )
            
            # Combine and weight recommendations
            all_recommendations = {}
            
            # Add collaborative filtering recommendations
            for rec in collaborative_recs:
                weight = self.strategy_weights[RecommendationStrategy.COLLABORATIVE_FILTERING]
                all_recommendations[rec.item_id] = {
                    "item": rec,
                    "score": rec.relevance_score * weight,
                    "sources": ["collaborative"]
                }
            
            # Add content-based recommendations
            for rec in content_based_recs:
                weight = self.strategy_weights[RecommendationStrategy.CONTENT_BASED]
                weighted_score = rec.relevance_score * weight
                
                if rec.item_id in all_recommendations:
                    all_recommendations[rec.item_id]["score"] += weighted_score
                    all_recommendations[rec.item_id]["sources"].append("content_based")
                else:
                    all_recommendations[rec.item_id] = {
                        "item": rec,
                        "score": weighted_score,
                        "sources": ["content_based"]
                    }
            
            # Add trending recommendations
            for rec in trending_recs:
                weight = self.strategy_weights[RecommendationStrategy.TRENDING]
                weighted_score = rec.relevance_score * weight
                
                if rec.item_id in all_recommendations:
                    all_recommendations[rec.item_id]["score"] += weighted_score
                    all_recommendations[rec.item_id]["sources"].append("trending")
                else:
                    all_recommendations[rec.item_id] = {
                        "item": rec,
                        "score": weighted_score,
                        "sources": ["trending"]
                    }
            
            # Sort by combined score
            sorted_recommendations = sorted(
                all_recommendations.values(),
                key=lambda x: x["score"],
                reverse=True
            )
            
            # Update scores and return items
            hybrid_recommendations = []
            for rec_data in sorted_recommendations[:request.max_recommendations]:
                item = rec_data["item"]
                item.relevance_score = rec_data["score"]
                item.reasoning = f"Hybrid recommendation from: {', '.join(rec_data['sources'])}"
                hybrid_recommendations.append(item)
            
            return hybrid_recommendations
            
        except Exception as e:
            logger.error(f"Failed to generate hybrid recommendations: {e}")
            return []


# Factory functions and utilities

def create_content_recommender(
    mongodb_handler: MongoDBHandler,
    vector_store: VectorStore,
    redis_cache: RedisCache,
    embedding_model: ContentEmbeddingModel,
    collaborative_model: CollaborativeFilteringModel,
    content_based_model: ContentBasedModel
) -> ContentRecommender:
    """Create content recommender instance"""    return ContentRecommender(
        mongodb_handler=mongodb_handler,
        vector_store=vector_store,
        redis_cache=redis_cache,
        embedding_model=embedding_model,
        collaborative_model=collaborative_model,
        content_based_model=content_based_model
    )


def validate_recommendation_request(request: RecommendationRequest) -> bool:
    """Validate recommendation request"""    if not request.user_id or not isinstance(request.user_id, str):
        return False
    
    if not isinstance(request.recommendation_type, RecommendationType):
        return False
    
    if request.max_recommendations <= 0 or request.max_recommendations > 100:
        return False
    
    return True
