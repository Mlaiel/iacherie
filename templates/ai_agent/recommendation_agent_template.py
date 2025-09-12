"""{{agent_name}} Recommendation Agent for Ainflue Platform
{{agent_description}}

Author: {{author_name}} ({{author_email}})
Created: {{created_date}}
"""

import logging
from typing import Dict, Any, Optional, List, Union, Tuple
from datetime import datetime, timedelta
from abc import ABC, abstractmethod
from enum import Enum
import json
import numpy as np
import pandas as pd
from collections import defaultdict

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import TruncatedSVD
from sklearn.cluster import KMeans
import torch
import torch.nn as nn
from transformers import AutoModel, AutoTokenizer
from pydantic import BaseModel, Field, validator

from ai.base_agent import BaseAIAgent
from ai.models import RecommendationModelManager
from ml.collaborative_filtering import CollaborativeFilter
from ml.content_based import ContentBasedFilter
from ml.matrix_factorization import MatrixFactorization
from ml.deep_learning import DeepRecommender
from core.config import get_settings
from utils.exceptions import RecommendationException
from monitoring.recommendation_metrics import RecommendationMetricsCollector

logger = logging.getLogger(__name__)
settings = get_settings()


class RecommendationType(Enum):
    """Recommendation types"""
    CONTENT_BASED = "content_based"
    COLLABORATIVE = "collaborative"
    HYBRID = "hybrid"
    DEEP_LEARNING = "deep_learning"
    TRENDING = "trending"
    PERSONALIZED = "personalized"
    SIMILAR_USERS = "similar_users"
    CROSS_PLATFORM = "cross_platform"


class ContentType(Enum):
    """Content types for recommendations"""
    POST = "post"
    VIDEO = "video"
    IMAGE = "image"
    AUDIO = "audio"
    ARTICLE = "article"
    PRODUCT = "product"
    USER = "user"
    HASHTAG = "hashtag"
    TOPIC = "topic"


class RecommendationStrategy(Enum):
    """Recommendation strategies"""
    POPULARITY = "popularity"
    DIVERSITY = "diversity"
    NOVELTY = "novelty"
    SERENDIPITY = "serendipity"
    EXPLORATION = "exploration"
    EXPLOITATION = "exploitation"
    COLD_START = "cold_start"
    REAL_TIME = "real_time"


class UserProfile(BaseModel):
    """User profile for recommendations"""
    user_id: str = Field(..., description="Unique user identifier")
    preferences: Dict[str, float] = Field(default_factory=dict, description="User preferences")
    demographics: Optional[Dict[str, Any]] = Field(default=None, description="User demographics")
    behavior_history: List[Dict[str, Any]] = Field(default_factory=list, description="User behavior history")
    interests: List[str] = Field(default_factory=list, description="User interests")
    content_interactions: Dict[str, List[str]] = Field(default_factory=dict, description="Content interactions")
    platform_activity: Dict[str, Dict[str, Any]] = Field(default_factory=dict, description="Platform-specific activity")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ContentItem(BaseModel):
    """Content item for recommendations"""
    content_id: str = Field(..., description="Unique content identifier")
    content_type: ContentType = Field(..., description="Type of content")
    title: Optional[str] = Field(default=None, description="Content title")
    description: Optional[str] = Field(default=None, description="Content description")
    features: Dict[str, Any] = Field(default_factory=dict, description="Content features")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Content metadata")
    creator_id: Optional[str] = Field(default=None, description="Content creator ID")
    tags: List[str] = Field(default_factory=list, description="Content tags")
    categories: List[str] = Field(default_factory=list, description="Content categories")
    popularity_score: float = Field(default=0.0, description="Content popularity score")
    quality_score: float = Field(default=0.0, description="Content quality score")
    engagement_metrics: Dict[str, float] = Field(default_factory=dict, description="Engagement metrics")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class RecommendationRequest(BaseModel):
    """Recommendation request"""
    request_id: str = Field(..., description="Unique request identifier")
    user_id: str = Field(..., description="User requesting recommendations")
    recommendation_type: RecommendationType = Field(..., description="Type of recommendation")
    content_type: ContentType = Field(..., description="Type of content to recommend")
    strategy: RecommendationStrategy = Field(default=RecommendationStrategy.EXPLOITATION, description="Recommendation strategy")
    num_recommendations: int = Field(default=10, description="Number of recommendations")
    exclude_items: List[str] = Field(default_factory=list, description="Items to exclude")
    include_explanations: bool = Field(default=True, description="Include recommendation explanations")
    real_time: bool = Field(default=False, description="Real-time recommendations")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Contextual information")
    filters: Optional[Dict[str, Any]] = Field(default=None, description="Content filters")
    diversity_factor: float = Field(default=0.3, description="Diversity factor (0-1)")
    novelty_factor: float = Field(default=0.2, description="Novelty factor (0-1)")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    @validator('num_recommendations')
    def validate_num_recommendations(cls, v):
        if v <= 0 or v > 100:
            raise ValueError('Number of recommendations must be between 1 and 100')
        return v
    
    @validator('diversity_factor', 'novelty_factor')
    def validate_factors(cls, v):
        if not 0 <= v <= 1:
            raise ValueError('Factors must be between 0 and 1')
        return v


class RecommendationItem(BaseModel):
    """Single recommendation item"""
    content_id: str = Field(..., description="Recommended content ID")
    content_type: ContentType = Field(..., description="Content type")
    score: float = Field(..., description="Recommendation score")
    confidence: float = Field(..., description="Confidence in recommendation")
    rank: int = Field(..., description="Recommendation rank")
    explanation: Optional[str] = Field(default=None, description="Recommendation explanation")
    reasoning: Optional[Dict[str, Any]] = Field(default=None, description="Recommendation reasoning")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")


class RecommendationResult(BaseModel):
    """Recommendation result"""
    request_id: str = Field(..., description="Request identifier")
    user_id: str = Field(..., description="User ID")
    success: bool = Field(..., description="Whether recommendation succeeded")
    recommendations: List[RecommendationItem] = Field(default_factory=list, description="Recommended items")
    total_candidates: int = Field(default=0, description="Total candidate items considered")
    algorithm_used: str = Field(..., description="Algorithm used for recommendations")
    diversity_score: float = Field(default=0.0, description="Diversity score of recommendations")
    novelty_score: float = Field(default=0.0, description="Novelty score of recommendations")
    coverage_score: float = Field(default=0.0, description="Coverage score of recommendations")
    processing_time: float = Field(..., description="Processing time in seconds")
    model_version: Optional[str] = Field(default=None, description="Model version used")
    explanation: Optional[str] = Field(default=None, description="Overall explanation")
    error_message: Optional[str] = Field(default=None, description="Error message if failed")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class {{agent_name}}Agent(BaseAIAgent):
    """{{agent_description}} with advanced recommendation capabilities"""
    
    def __init__(
        self,
        agent_id: str,
        model_configs: Dict[str, Dict[str, Any]],
        enable_real_time: bool = True,
        cache_size: int = 10000,
        update_frequency: timedelta = timedelta(hours=1),
        **kwargs
    ):
        super().__init__(agent_id=agent_id, **kwargs)
        self.model_configs = model_configs
        self.enable_real_time = enable_real_time
        self.cache_size = cache_size
        self.update_frequency = update_frequency
        
        # Initialize components
        self.model_manager = RecommendationModelManager()
        self.collaborative_filter = CollaborativeFilter()
        self.content_filter = ContentBasedFilter()
        self.matrix_factorization = MatrixFactorization()
        self.deep_recommender = DeepRecommender()
        self.metrics_collector = RecommendationMetricsCollector()
        
        # Initialize data structures
        self.user_profiles: Dict[str, UserProfile] = {}
        self.content_items: Dict[str, ContentItem] = {}
        self.interaction_matrix = None
        self.content_features = None
        self.user_embeddings = None
        self.item_embeddings = None
        
        # Load models and data
        self._load_models()
        self._initialize_recommenders()
        
        logger.info(f"RecommendationAgent {agent_id} initialized")
    
    def _load_models(self):
        """Load recommendation models"""
        try:
            # Load pre-trained embeddings if available
            if "embedding_model" in self.model_configs:
                config = self.model_configs["embedding_model"]
                self.embedding_model = AutoModel.from_pretrained(config["model_name"])
                self.tokenizer = AutoTokenizer.from_pretrained(config["model_name"])
            
            # Load collaborative filtering model
            if "collaborative_model" in self.model_configs:
                self.collaborative_filter.load_model(self.model_configs["collaborative_model"])
            
            # Load content-based model
            if "content_model" in self.model_configs:
                self.content_filter.load_model(self.model_configs["content_model"])
            
            logger.info("Recommendation models loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load models: {e}")
            raise RecommendationException(f"Model loading failed: {e}")
    
    def _initialize_recommenders(self):
        """Initialize recommendation algorithms"""
        try:
            # Initialize TF-IDF vectorizer for content-based filtering
            self.tfidf_vectorizer = TfidfVectorizer(
                max_features=5000,
                stop_words='english',
                ngram_range=(1, 2)
            )
            
            # Initialize dimensionality reduction
            self.svd = TruncatedSVD(n_components=100, random_state=42)
            
            # Initialize clustering for user segmentation
            self.user_clusters = KMeans(n_clusters=10, random_state=42)
            
            logger.info("Recommendation algorithms initialized")
        except Exception as e:
            logger.error(f"Failed to initialize recommenders: {e}")
            raise RecommendationException(f"Recommender initialization failed: {e}")
    
    async def generate_recommendations(self, request: RecommendationRequest) -> RecommendationResult:
        """Generate recommendations for a user"""
        start_time = datetime.utcnow()
        
        try:
            # Get user profile
            user_profile = await self._get_user_profile(request.user_id)
            
            # Get candidate items
            candidates = await self._get_candidate_items(request, user_profile)
            
            # Apply recommendation algorithm
            recommendations = await self._apply_recommendation_algorithm(
                request, user_profile, candidates
            )
            
            # Apply post-processing
            final_recommendations = await self._post_process_recommendations(
                recommendations, request, user_profile
            )
            
            # Calculate metrics
            diversity_score = self._calculate_diversity_score(final_recommendations)
            novelty_score = self._calculate_novelty_score(final_recommendations, user_profile)
            coverage_score = self._calculate_coverage_score(final_recommendations, candidates)
            
            # Calculate processing time
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            # Create result
            result = RecommendationResult(
                request_id=request.request_id,
                user_id=request.user_id,
                success=True,
                recommendations=final_recommendations,
                total_candidates=len(candidates),
                algorithm_used=request.recommendation_type.value,
                diversity_score=diversity_score,
                novelty_score=novelty_score,
                coverage_score=coverage_score,
                processing_time=processing_time,
                explanation=self._generate_explanation(request, final_recommendations)
            )
            
            # Update user profile with interaction
            await self._update_user_profile(request.user_id, request, result)
            
            # Collect metrics
            await self.metrics_collector.record_recommendation_generation(
                user_id=request.user_id,
                algorithm=request.recommendation_type.value,
                num_recommendations=len(final_recommendations),
                processing_time=processing_time,
                diversity_score=diversity_score,
                success=True
            )
            
            return result
            
        except Exception as e:
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            logger.error(f"Recommendation generation failed for request {request.request_id}: {e}")
            
            # Collect error metrics
            await self.metrics_collector.record_recommendation_generation(
                user_id=request.user_id,
                algorithm=request.recommendation_type.value,
                num_recommendations=0,
                processing_time=processing_time,
                diversity_score=0.0,
                success=False
            )
            
            return RecommendationResult(
                request_id=request.request_id,
                user_id=request.user_id,
                success=False,
                recommendations=[],
                total_candidates=0,
                algorithm_used=request.recommendation_type.value,
                processing_time=processing_time,
                error_message=str(e)
            )
    
    async def _get_user_profile(self, user_id: str) -> UserProfile:
        """Get or create user profile"""
        if user_id in self.user_profiles:
            return self.user_profiles[user_id]
        
        # Create new user profile
        user_profile = UserProfile(user_id=user_id)
        self.user_profiles[user_id] = user_profile
        return user_profile
    
    async def _get_candidate_items(
        self, 
        request: RecommendationRequest, 
        user_profile: UserProfile
    ) -> List[ContentItem]:
        """Get candidate items for recommendation"""
        candidates = []
        
        # Get all content items of requested type
        for content_id, content_item in self.content_items.items():
            if content_item.content_type == request.content_type:
                # Skip excluded items
                if content_id not in request.exclude_items:
                    # Apply filters if specified
                    if self._passes_filters(content_item, request.filters):
                        candidates.append(content_item)
        
        # Apply additional candidate selection strategies
        if request.strategy == RecommendationStrategy.COLD_START:
            candidates = await self._get_cold_start_candidates(candidates, request)
        elif request.strategy == RecommendationStrategy.TRENDING:
            candidates = await self._get_trending_candidates(candidates, request)
        
        return candidates
    
    async def _apply_recommendation_algorithm(
        self,
        request: RecommendationRequest,
        user_profile: UserProfile,
        candidates: List[ContentItem]
    ) -> List[RecommendationItem]:
        """Apply the specified recommendation algorithm"""
        
        if request.recommendation_type == RecommendationType.CONTENT_BASED:
            return await self._content_based_recommendations(user_profile, candidates, request)
        
        elif request.recommendation_type == RecommendationType.COLLABORATIVE:
            return await self._collaborative_recommendations(user_profile, candidates, request)
        
        elif request.recommendation_type == RecommendationType.HYBRID:
            return await self._hybrid_recommendations(user_profile, candidates, request)
        
        elif request.recommendation_type == RecommendationType.DEEP_LEARNING:
            return await self._deep_learning_recommendations(user_profile, candidates, request)
        
        elif request.recommendation_type == RecommendationType.TRENDING:
            return await self._trending_recommendations(candidates, request)
        
        elif request.recommendation_type == RecommendationType.PERSONALIZED:
            return await self._personalized_recommendations(user_profile, candidates, request)
        
        elif request.recommendation_type == RecommendationType.SIMILAR_USERS:
            return await self._similar_users_recommendations(user_profile, candidates, request)
        
        elif request.recommendation_type == RecommendationType.CROSS_PLATFORM:
            return await self._cross_platform_recommendations(user_profile, candidates, request)
        
        else:
            raise RecommendationException(f"Unknown recommendation type: {request.recommendation_type}")
    
    async def _content_based_recommendations(
        self,
        user_profile: UserProfile,
        candidates: List[ContentItem],
        request: RecommendationRequest
    ) -> List[RecommendationItem]:
        """Generate content-based recommendations"""
        recommendations = []
        
        # Get user's content preferences
        user_features = self._extract_user_content_features(user_profile)
        
        for candidate in candidates:
            # Extract content features
            content_features = self._extract_content_features(candidate)
            
            # Calculate similarity score
            similarity_score = self._calculate_content_similarity(user_features, content_features)
            
            # Apply quality and popularity factors
            quality_factor = candidate.quality_score
            popularity_factor = min(1.0, candidate.popularity_score / 100.0)
            
            # Calculate final score
            final_score = (
                similarity_score * 0.6 +
                quality_factor * 0.3 +
                popularity_factor * 0.1
            )
            
            recommendations.append(RecommendationItem(
                content_id=candidate.content_id,
                content_type=candidate.content_type,
                score=final_score,
                confidence=similarity_score,
                rank=0,  # Will be set during sorting
                explanation=f"Based on your interest in {', '.join(user_profile.interests[:3])}"
            ))
        
        # Sort by score and assign ranks
        recommendations.sort(key=lambda x: x.score, reverse=True)
        for i, rec in enumerate(recommendations):
            rec.rank = i + 1
        
        return recommendations[:request.num_recommendations]
    
    async def _collaborative_recommendations(
        self,
        user_profile: UserProfile,
        candidates: List[ContentItem],
        request: RecommendationRequest
    ) -> List[RecommendationItem]:
        """Generate collaborative filtering recommendations"""
        recommendations = []
        
        # Find similar users
        similar_users = await self._find_similar_users(user_profile)
        
        # Get items liked by similar users
        similar_user_preferences = defaultdict(float)
        for similar_user_id, similarity_score in similar_users:
            similar_user = self.user_profiles.get(similar_user_id)
            if similar_user:
                for content_id, preference in similar_user.preferences.items():
                    similar_user_preferences[content_id] += preference * similarity_score
        
        # Score candidates based on similar user preferences
        for candidate in candidates:
            if candidate.content_id in similar_user_preferences:
                score = similar_user_preferences[candidate.content_id]
                
                recommendations.append(RecommendationItem(
                    content_id=candidate.content_id,
                    content_type=candidate.content_type,
                    score=score,
                    confidence=min(1.0, score),
                    rank=0,
                    explanation="Users with similar interests also liked this"
                ))
        
        # Sort and rank
        recommendations.sort(key=lambda x: x.score, reverse=True)
        for i, rec in enumerate(recommendations):
            rec.rank = i + 1
        
        return recommendations[:request.num_recommendations]
    
    async def _hybrid_recommendations(
        self,
        user_profile: UserProfile,
        candidates: List[ContentItem],
        request: RecommendationRequest
    ) -> List[RecommendationItem]:
        """Generate hybrid recommendations combining multiple approaches"""
        
        # Get recommendations from different algorithms
        content_based = await self._content_based_recommendations(user_profile, candidates, request)
        collaborative = await self._collaborative_recommendations(user_profile, candidates, request)
        
        # Combine recommendations with weighted scores
        combined_scores = defaultdict(float)
        content_weight = 0.6
        collaborative_weight = 0.4
        
        # Add content-based scores
        for rec in content_based:
            combined_scores[rec.content_id] += rec.score * content_weight
        
        # Add collaborative scores
        for rec in collaborative:
            combined_scores[rec.content_id] += rec.score * collaborative_weight
        
        # Create final recommendations
        recommendations = []
        for content_id, score in combined_scores.items():
            candidate = next((c for c in candidates if c.content_id == content_id), None)
            if candidate:
                recommendations.append(RecommendationItem(
                    content_id=content_id,
                    content_type=candidate.content_type,
                    score=score,
                    confidence=min(1.0, score),
                    rank=0,
                    explanation="Based on content similarity and user preferences"
                ))
        
        # Sort and rank
        recommendations.sort(key=lambda x: x.score, reverse=True)
        for i, rec in enumerate(recommendations):
            rec.rank = i + 1
        
        return recommendations[:request.num_recommendations]
    
    async def _deep_learning_recommendations(
        self,
        user_profile: UserProfile,
        candidates: List[ContentItem],
        request: RecommendationRequest
    ) -> List[RecommendationItem]:
        """Generate deep learning-based recommendations"""
        recommendations = []
        
        try:
            # Get user embedding
            user_embedding = await self._get_user_embedding(user_profile)
            
            # Score candidates using deep model
            for candidate in candidates:
                item_embedding = await self._get_item_embedding(candidate)
                
                # Calculate deep similarity
                score = torch.cosine_similarity(
                    user_embedding.unsqueeze(0), 
                    item_embedding.unsqueeze(0)
                ).item()
                
                recommendations.append(RecommendationItem(
                    content_id=candidate.content_id,
                    content_type=candidate.content_type,
                    score=score,
                    confidence=abs(score),
                    rank=0,
                    explanation="Based on deep learning user-item embeddings"
                ))
            
            # Sort and rank
            recommendations.sort(key=lambda x: x.score, reverse=True)
            for i, rec in enumerate(recommendations):
                rec.rank = i + 1
            
            return recommendations[:request.num_recommendations]
            
        except Exception as e:
            logger.error(f"Deep learning recommendations failed: {e}")
            # Fallback to content-based
            return await self._content_based_recommendations(user_profile, candidates, request)
    
    async def _trending_recommendations(
        self,
        candidates: List[ContentItem],
        request: RecommendationRequest
    ) -> List[RecommendationItem]:
        """Generate trending content recommendations"""
        recommendations = []
        
        # Calculate trend scores
        current_time = datetime.utcnow()
        for candidate in candidates:
            # Time decay factor
            time_diff = (current_time - candidate.created_at).total_seconds()
            time_decay = np.exp(-time_diff / (24 * 3600))  # Decay over 24 hours
            
            # Engagement velocity
            engagement_velocity = sum(candidate.engagement_metrics.values()) / max(1, time_diff / 3600)
            
            # Trend score
            trend_score = (
                candidate.popularity_score * 0.4 +
                engagement_velocity * 0.4 +
                time_decay * 0.2
            )
            
            recommendations.append(RecommendationItem(
                content_id=candidate.content_id,
                content_type=candidate.content_type,
                score=trend_score,
                confidence=0.8,
                rank=0,
                explanation="Trending content with high engagement"
            ))
        
        # Sort and rank
        recommendations.sort(key=lambda x: x.score, reverse=True)
        for i, rec in enumerate(recommendations):
            rec.rank = i + 1
        
        return recommendations[:request.num_recommendations]
    
    async def _personalized_recommendations(
        self,
        user_profile: UserProfile,
        candidates: List[ContentItem],
        request: RecommendationRequest
    ) -> List[RecommendationItem]:
        """Generate personalized recommendations"""
        # Use hybrid approach with user-specific weights
        hybrid_request = request.copy()
        hybrid_request.recommendation_type = RecommendationType.HYBRID
        
        return await self._hybrid_recommendations(user_profile, candidates, hybrid_request)
    
    async def _similar_users_recommendations(
        self,
        user_profile: UserProfile,
        candidates: List[ContentItem],
        request: RecommendationRequest
    ) -> List[RecommendationItem]:
        """Generate recommendations based on similar users"""
        return await self._collaborative_recommendations(user_profile, candidates, request)
    
    async def _cross_platform_recommendations(
        self,
        user_profile: UserProfile,
        candidates: List[ContentItem],
        request: RecommendationRequest
    ) -> List[RecommendationItem]:
        """Generate cross-platform recommendations"""
        recommendations = []
        
        # Analyze user's cross-platform activity
        platform_preferences = {}
        for platform, activity in user_profile.platform_activity.items():
            platform_preferences[platform] = activity.get('engagement_score', 0.5)
        
        # Score candidates based on cross-platform performance
        for candidate in candidates:
            cross_platform_score = 0.0
            platform_count = 0
            
            # Check if content performed well on other platforms
            for platform, preference in platform_preferences.items():
                if platform in candidate.metadata.get('platform_performance', {}):
                    performance = candidate.metadata['platform_performance'][platform]
                    cross_platform_score += performance * preference
                    platform_count += 1
            
            if platform_count > 0:
                cross_platform_score /= platform_count
            
            recommendations.append(RecommendationItem(
                content_id=candidate.content_id,
                content_type=candidate.content_type,
                score=cross_platform_score,
                confidence=min(1.0, platform_count / 3.0),  # Higher confidence with more platforms
                rank=0,
                explanation="Content that performs well across platforms"
            ))
        
        # Sort and rank
        recommendations.sort(key=lambda x: x.score, reverse=True)
        for i, rec in enumerate(recommendations):
            rec.rank = i + 1
        
        return recommendations[:request.num_recommendations]
    
    async def _post_process_recommendations(
        self,
        recommendations: List[RecommendationItem],
        request: RecommendationRequest,
        user_profile: UserProfile
    ) -> List[RecommendationItem]:
        """Post-process recommendations for diversity and novelty"""
        
        if not recommendations:
            return recommendations
        
        # Apply diversity if requested
        if request.diversity_factor > 0:
            recommendations = self._apply_diversity(recommendations, request.diversity_factor)
        
        # Apply novelty if requested
        if request.novelty_factor > 0:
            recommendations = self._apply_novelty(recommendations, user_profile, request.novelty_factor)
        
        # Re-rank after post-processing
        for i, rec in enumerate(recommendations):
            rec.rank = i + 1
        
        return recommendations[:request.num_recommendations]
    
    def _apply_diversity(
        self, 
        recommendations: List[RecommendationItem], 
        diversity_factor: float
    ) -> List[RecommendationItem]:
        """Apply diversity to recommendations"""
        if not recommendations:
            return recommendations
        
        diversified = [recommendations[0]]  # Start with top recommendation
        remaining = recommendations[1:]
        
        while remaining and len(diversified) < len(recommendations):
            best_candidate = None
            best_score = -1
            
            for candidate in remaining:
                # Calculate diversity score (average distance from selected items)
                diversity_score = 0
                for selected in diversified:
                    # Simple category-based diversity
                    if candidate.content_type != selected.content_type:
                        diversity_score += 1
                
                diversity_score /= len(diversified)
                
                # Combine original score with diversity
                combined_score = (
                    candidate.score * (1 - diversity_factor) +
                    diversity_score * diversity_factor
                )
                
                if combined_score > best_score:
                    best_score = combined_score
                    best_candidate = candidate
            
            if best_candidate:
                diversified.append(best_candidate)
                remaining.remove(best_candidate)
            else:
                break
        
        return diversified
    
    def _apply_novelty(
        self, 
        recommendations: List[RecommendationItem], 
        user_profile: UserProfile,
        novelty_factor: float
    ) -> List[RecommendationItem]:
        """Apply novelty to recommendations"""
        
        # Get user's interaction history
        interacted_items = set()
        for interactions in user_profile.content_interactions.values():
            interacted_items.update(interactions)
        
        # Adjust scores based on novelty
        for rec in recommendations:
            if rec.content_id not in interacted_items:
                # Novel item - boost score
                rec.score = rec.score * (1 + novelty_factor)
            else:
                # Familiar item - reduce score
                rec.score = rec.score * (1 - novelty_factor * 0.5)
        
        # Re-sort by adjusted scores
        recommendations.sort(key=lambda x: x.score, reverse=True)
        return recommendations
    
    # Helper methods
    def _extract_user_content_features(self, user_profile: UserProfile) -> Dict[str, float]:
        """Extract content features from user profile"""
        features = {}
        
        # Interest-based features
        for interest in user_profile.interests:
            features[f"interest_{interest}"] = 1.0
        
        # Preference-based features
        for key, value in user_profile.preferences.items():
            features[key] = value
        
        return features
    
    def _extract_content_features(self, content_item: ContentItem) -> Dict[str, float]:
        """Extract features from content item"""
        features = {}
        
        # Content type feature
        features[f"type_{content_item.content_type.value}"] = 1.0
        
        # Tag-based features
        for tag in content_item.tags:
            features[f"tag_{tag}"] = 1.0
        
        # Category-based features
        for category in content_item.categories:
            features[f"category_{category}"] = 1.0
        
        # Quality and popularity features
        features["quality"] = content_item.quality_score
        features["popularity"] = content_item.popularity_score / 100.0
        
        return features
    
    def _calculate_content_similarity(
        self, 
        user_features: Dict[str, float], 
        content_features: Dict[str, float]
    ) -> float:
        """Calculate similarity between user and content features"""
        
        # Get common features
        common_features = set(user_features.keys()) & set(content_features.keys())
        
        if not common_features:
            return 0.0
        
        # Calculate cosine similarity
        dot_product = sum(user_features[f] * content_features[f] for f in common_features)
        
        user_norm = np.sqrt(sum(v**2 for v in user_features.values()))
        content_norm = np.sqrt(sum(v**2 for v in content_features.values()))
        
        if user_norm == 0 or content_norm == 0:
            return 0.0
        
        return dot_product / (user_norm * content_norm)
    
    async def _find_similar_users(self, user_profile: UserProfile) -> List[Tuple[str, float]]:
        """Find users similar to the given user"""
        similar_users = []
        
        for other_user_id, other_profile in self.user_profiles.items():
            if other_user_id != user_profile.user_id:
                similarity = self._calculate_user_similarity(user_profile, other_profile)
                if similarity > 0.3:  # Threshold for similarity
                    similar_users.append((other_user_id, similarity))
        
        # Sort by similarity and return top 10
        similar_users.sort(key=lambda x: x[1], reverse=True)
        return similar_users[:10]
    
    def _calculate_user_similarity(self, user1: UserProfile, user2: UserProfile) -> float:
        """Calculate similarity between two users"""
        
        # Interest similarity
        interests1 = set(user1.interests)
        interests2 = set(user2.interests)
        
        if not interests1 or not interests2:
            interest_similarity = 0.0
        else:
            intersection = len(interests1 & interests2)
            union = len(interests1 | interests2)
            interest_similarity = intersection / union if union > 0 else 0.0
        
        # Preference similarity
        preference_similarity = self._calculate_content_similarity(
            user1.preferences, user2.preferences
        )
        
        # Combined similarity
        return (interest_similarity * 0.6 + preference_similarity * 0.4)
    
    async def _get_user_embedding(self, user_profile: UserProfile) -> torch.Tensor:
        """Get embedding for user profile"""
        # Simplified user embedding based on interests and preferences
        user_text = " ".join(user_profile.interests) + " " + " ".join(user_profile.preferences.keys())
        
        if hasattr(self, 'embedding_model') and user_text:
            inputs = self.tokenizer(user_text, return_tensors="pt", truncation=True, max_length=512)
            with torch.no_grad():
                outputs = self.embedding_model(**inputs)
                return outputs.last_hidden_state.mean(dim=1).squeeze()
        
        # Fallback to random embedding
        return torch.randn(768)
    
    async def _get_item_embedding(self, content_item: ContentItem) -> torch.Tensor:
        """Get embedding for content item"""
        # Create text representation of item
        item_text = f"{content_item.title or ''} {content_item.description or ''} {' '.join(content_item.tags)}"
        
        if hasattr(self, 'embedding_model') and item_text:
            inputs = self.tokenizer(item_text, return_tensors="pt", truncation=True, max_length=512)
            with torch.no_grad():
                outputs = self.embedding_model(**inputs)
                return outputs.last_hidden_state.mean(dim=1).squeeze()
        
        # Fallback to random embedding
        return torch.randn(768)
    
    def _passes_filters(self, content_item: ContentItem, filters: Optional[Dict[str, Any]]) -> bool:
        """Check if content item passes the specified filters"""
        if not filters:
            return True
        
        # Category filter
        if "categories" in filters:
            required_categories = filters["categories"]
            if not any(cat in content_item.categories for cat in required_categories):
                return False
        
        # Quality filter
        if "min_quality" in filters:
            if content_item.quality_score < filters["min_quality"]:
                return False
        
        # Date filter
        if "max_age_days" in filters:
            max_age = timedelta(days=filters["max_age_days"])
            if datetime.utcnow() - content_item.created_at > max_age:
                return False
        
        return True
    
    async def _get_cold_start_candidates(
        self, 
        candidates: List[ContentItem], 
        request: RecommendationRequest
    ) -> List[ContentItem]:
        """Get candidates for cold start users"""
        # For cold start, prioritize popular and high-quality content
        return sorted(
            candidates,
            key=lambda x: (x.popularity_score, x.quality_score),
            reverse=True
        )[:50]  # Limit candidates for cold start
    
    async def _get_trending_candidates(
        self, 
        candidates: List[ContentItem], 
        request: RecommendationRequest
    ) -> List[ContentItem]:
        """Get trending candidates"""
        # Filter for recent content with high engagement
        recent_threshold = datetime.utcnow() - timedelta(days=7)
        trending_candidates = [
            c for c in candidates 
            if c.created_at > recent_threshold and c.popularity_score > 50
        ]
        
        return sorted(
            trending_candidates,
            key=lambda x: x.popularity_score,
            reverse=True
        )[:100]
    
    def _calculate_diversity_score(self, recommendations: List[RecommendationItem]) -> float:
        """Calculate diversity score of recommendations"""
        if len(recommendations) < 2:
            return 0.0
        
        # Calculate diversity based on content types
        content_types = set(rec.content_type for rec in recommendations)
        return len(content_types) / len(recommendations)
    
    def _calculate_novelty_score(
        self, 
        recommendations: List[RecommendationItem], 
        user_profile: UserProfile
    ) -> float:
        """Calculate novelty score of recommendations"""
        if not recommendations:
            return 0.0
        
        # Check how many recommendations are novel (not in user's history)
        interacted_items = set()
        for interactions in user_profile.content_interactions.values():
            interacted_items.update(interactions)
        
        novel_count = sum(1 for rec in recommendations if rec.content_id not in interacted_items)
        return novel_count / len(recommendations)
    
    def _calculate_coverage_score(
        self, 
        recommendations: List[RecommendationItem], 
        candidates: List[ContentItem]
    ) -> float:
        """Calculate coverage score of recommendations"""
        if not candidates:
            return 0.0
        
        # Coverage is the fraction of candidate space covered
        return len(recommendations) / len(candidates)
    
    def _generate_explanation(
        self, 
        request: RecommendationRequest, 
        recommendations: List[RecommendationItem]
    ) -> str:
        """Generate overall explanation for recommendations"""
        if not recommendations:
            return "No suitable recommendations found."
        
        algorithm_explanations = {
            RecommendationType.CONTENT_BASED: "Based on content you've previously engaged with",
            RecommendationType.COLLABORATIVE: "Based on users with similar preferences",
            RecommendationType.HYBRID: "Based on a combination of content and user preferences",
            RecommendationType.DEEP_LEARNING: "Based on advanced AI analysis of your preferences",
            RecommendationType.TRENDING: "Based on trending and popular content",
            RecommendationType.PERSONALIZED: "Personalized recommendations based on your unique profile"
        }
        
        return algorithm_explanations.get(
            request.recommendation_type, 
            "Based on advanced recommendation algorithms"
        )
    
    async def _update_user_profile(
        self, 
        user_id: str, 
        request: RecommendationRequest, 
        result: RecommendationResult
    ):
        """Update user profile based on recommendation interaction"""
        if user_id in self.user_profiles:
            user_profile = self.user_profiles[user_id]
            user_profile.updated_at = datetime.utcnow()
            
            # Record recommendation request in behavior history
            user_profile.behavior_history.append({
                "timestamp": datetime.utcnow().isoformat(),
                "action": "recommendation_request",
                "request_type": request.recommendation_type.value,
                "content_type": request.content_type.value,
                "num_recommendations": len(result.recommendations)
            })
            
            # Limit history size
            if len(user_profile.behavior_history) > 1000:
                user_profile.behavior_history = user_profile.behavior_history[-1000:]
    
    async def update_content_catalog(self, content_items: List[ContentItem]):
        """Update the content catalog"""
        for item in content_items:
            self.content_items[item.content_id] = item
        
        logger.info(f"Updated content catalog with {len(content_items)} items")
    
    async def update_user_interaction(
        self, 
        user_id: str, 
        content_id: str, 
        interaction_type: str, 
        interaction_value: float = 1.0
    ):
        """Update user interaction with content"""
        user_profile = await self._get_user_profile(user_id)
        
        # Update content interactions
        if interaction_type not in user_profile.content_interactions:
            user_profile.content_interactions[interaction_type] = []
        
        user_profile.content_interactions[interaction_type].append(content_id)
        
        # Update preferences
        if content_id not in user_profile.preferences:
            user_profile.preferences[content_id] = 0.0
        
        # Adjust preference based on interaction type
        interaction_weights = {
            "view": 0.1,
            "like": 0.5,
            "share": 0.8,
            "comment": 0.7,
            "save": 0.9,
            "follow": 1.0
        }
        
        weight = interaction_weights.get(interaction_type, 0.5)
        user_profile.preferences[content_id] += weight * interaction_value
        user_profile.preferences[content_id] = min(1.0, user_profile.preferences[content_id])
        
        user_profile.updated_at = datetime.utcnow()
        
        logger.info(f"Updated user {user_id} interaction with content {content_id}")
    
    async def get_recommendation_capabilities(self) -> Dict[str, List[str]]:
        """Get available recommendation capabilities"""
        return {
            "recommendation_types": [rt.value for rt in RecommendationType],
            "content_types": [ct.value for ct in ContentType],
            "strategies": [rs.value for rs in RecommendationStrategy],
            "features": [
                "Real-time recommendations",
                "Batch processing",
                "Cold start handling",
                "Diversity optimization",
                "Novelty injection",
                "Cross-platform recommendations",
                "A/B testing support",
                "Performance monitoring"
            ]
        }
    
    async def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for the recommendation agent"""
        return await self.metrics_collector.get_metrics_summary()


# Template usage example
def create_recommendation_agent_example():
    """Example of how to create and use a recommendation agent"""
    
    # Define model configurations
    model_configs = {
        "embedding_model": {
            "model_name": "sentence-transformers/all-MiniLM-L6-v2"
        },
        "collaborative_model": {
            "algorithm": "matrix_factorization",
            "factors": 100
        },
        "content_model": {
            "algorithm": "tfidf",
            "max_features": 5000
        }
    }
    
    # Create agent
    rec_agent = RecommendationAgent(
        agent_id="recommendation_001",
        model_configs=model_configs,
        enable_real_time=True
    )
    
    return rec_agent


# Template configuration for code generation
TEMPLATE_CONFIG = {
    "template_name": "recommendation_agent_template",
    "template_version": "1.0.0", 
    "template_description": "Comprehensive recommendation agent with multiple algorithms and strategies",
    "required_parameters": [
        "agent_name",
        "agent_description",
        "author_name",
        "author_email", 
        "created_date"
    ],
    "optional_parameters": [
        "custom_algorithms",
        "recommendation_strategies",
        "evaluation_metrics"
    ],
    "dependencies": [
        "scikit-learn>=1.3.0",
        "torch>=2.0.0",
        "transformers>=4.35.0",
        "pandas>=2.0.0",
        "numpy>=1.24.0"
    ],
    "features": [
        "Multiple recommendation algorithms",
        "Hybrid recommendations",
        "Real-time processing",
        "Cold start handling",
        "Diversity and novelty optimization",
        "Cross-platform recommendations",
        "User profiling",
        "Content analysis",
        "Performance monitoring",
        "A/B testing support"
    ]
}