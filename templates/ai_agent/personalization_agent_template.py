"""{{agent_name}} Personalization Agent for Ainflue Platform
{{agent_description}}

Author: {{author_name}} ({{author_email}})
Created: {{created_date}}
"""

import logging
from typing import Dict, Any, Optional, List, Union, Tuple, Set
from datetime import datetime, timedelta
from abc import ABC, abstractmethod
from enum import Enum
import asyncio
import json
import uuid

import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import NMF, PCA
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import torch
import torch.nn as nn
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModel
from pydantic import BaseModel, Field, validator

from ai.base_agent import BaseAIAgent
from ai.models import PersonalizationModelManager
from recommendation.collaborative_filtering import CollaborativeFilter
from recommendation.content_based import ContentBasedFilter
from recommendation.deep_learning import DeepRecommender
from user_modeling.profile_builder import UserProfileBuilder
from user_modeling.behavior_analyzer import BehaviorAnalyzer
from user_modeling.preference_learner import PreferenceLearner
from core.config import get_settings
from utils.exceptions import PersonalizationException
from monitoring.personalization_metrics import PersonalizationMetricsCollector

logger = logging.getLogger(__name__)
settings = get_settings()


class PersonalizationType(Enum):
    """Types of personalization"""
    CONTENT_RECOMMENDATION = "content_recommendation"
    CREATOR_DISCOVERY = "creator_discovery"
    FEED_CURATION = "feed_curation"
    AD_TARGETING = "ad_targeting"
    NOTIFICATION_TIMING = "notification_timing"
    UI_CUSTOMIZATION = "ui_customization"
    SEARCH_RANKING = "search_ranking"
    COLLABORATION_MATCHING = "collaboration_matching"


class RecommendationStrategy(Enum):
    """Recommendation strategies"""
    COLLABORATIVE_FILTERING = "collaborative_filtering"
    CONTENT_BASED = "content_based"
    HYBRID = "hybrid"
    DEEP_LEARNING = "deep_learning"
    POPULARITY_BASED = "popularity_based"
    TRENDING = "trending"
    DIVERSIFIED = "diversified"


class UserSegment(Enum):
    """User segments for personalization"""
    NEW_USER = "new_user"
    CASUAL_USER = "casual_user"
    ACTIVE_USER = "active_user"
    POWER_USER = "power_user"
    CREATOR = "creator"
    BRAND = "brand"
    INACTIVE_USER = "inactive_user"


class PersonalizationRequest(BaseModel):
    """Personalization request model"""
    user_id: str
    personalization_type: PersonalizationType
    strategy: RecommendationStrategy = RecommendationStrategy.HYBRID
    count: int = Field(default=10, ge=1, le=100)
    context: Dict[str, Any] = Field(default_factory=dict)
    filters: Dict[str, Any] = Field(default_factory=dict)
    diversification: float = Field(default=0.3, ge=0.0, le=1.0)
    freshness_weight: float = Field(default=0.2, ge=0.0, le=1.0)
    include_explanations: bool = False
    metadata: Dict[str, Any] = Field(default_factory=dict)

    @validator('user_id')
    def validate_user_id(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('User ID cannot be empty')
        return v.strip()


class UserProfile(BaseModel):
    """User profile model"""
    user_id: str
    segment: UserSegment
    demographics: Dict[str, Any] = Field(default_factory=dict)
    interests: List[str] = Field(default_factory=list)
    preferences: Dict[str, float] = Field(default_factory=dict)
    behavior_patterns: Dict[str, Any] = Field(default_factory=dict)
    interaction_history: List[Dict[str, Any]] = Field(default_factory=list)
    embedding: Optional[List[float]] = None
    last_updated: datetime = Field(default_factory=datetime.utcnow)


class RecommendationItem(BaseModel):
    """Recommendation item model"""
    item_id: str
    item_type: str
    title: str
    score: float = Field(ge=0.0, le=1.0)
    relevance_score: float = Field(ge=0.0, le=1.0)
    novelty_score: float = Field(ge=0.0, le=1.0)
    diversity_score: float = Field(ge=0.0, le=1.0)
    features: Dict[str, Any] = Field(default_factory=dict)
    explanation: Optional[str] = None


class PersonalizationResult(BaseModel):
    """Personalization result model"""
    user_id: str
    personalization_type: PersonalizationType
    strategy: RecommendationStrategy
    items: List[RecommendationItem]
    user_profile: UserProfile
    context: Dict[str, Any] = Field(default_factory=dict)
    performance_metrics: Dict[str, float] = Field(default_factory=dict)
    processing_time: float
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class PersonalizationConfig(BaseModel):
    """Personalization configuration"""
    enable_deep_learning: bool = True
    enable_real_time_learning: bool = True
    enable_cold_start_handling: bool = True
    enable_diversity_optimization: bool = True
    min_interactions_for_cf: int = 5
    max_profile_age_days: int = 30
    embedding_dimension: int = 128
    learning_rate: float = 0.001
    batch_size: int = 32
    cache_duration_minutes: int = 60


class DeepPersonalizationModel(nn.Module):
    """Deep neural network for personalization"""
    
    def __init__(
        self,
        user_features: int,
        item_features: int,
        embedding_dim: int = 128,
        hidden_dims: List[int] = [256, 128, 64]
    ):
        super(DeepPersonalizationModel, self).__init__()
        
        self.user_embedding = nn.Embedding(user_features, embedding_dim)
        self.item_embedding = nn.Embedding(item_features, embedding_dim)
        
        # MLP layers
        input_dim = embedding_dim * 2
        layers = []
        
        for hidden_dim in hidden_dims:
            layers.extend([
                nn.Linear(input_dim, hidden_dim),
                nn.ReLU(),
                nn.Dropout(0.2),
                nn.BatchNorm1d(hidden_dim)
            ])
            input_dim = hidden_dim
        
        layers.append(nn.Linear(input_dim, 1))
        layers.append(nn.Sigmoid())
        
        self.mlp = nn.Sequential(*layers)
        
    def forward(self, user_ids, item_ids):
        user_emb = self.user_embedding(user_ids)
        item_emb = self.item_embedding(item_ids)
        
        # Concatenate embeddings
        concat_emb = torch.cat([user_emb, item_emb], dim=1)
        
        # Pass through MLP
        output = self.mlp(concat_emb)
        
        return output.squeeze()


class {{agent_class_name}}(BaseAIAgent):
    """
    Advanced personalization agent for Ainflue platform.
    
    Features:
    - Multi-strategy recommendation system
    - Real-time user profiling and learning
    - Deep learning-based personalization
    - Cold start problem handling
    - Diversity and novelty optimization
    - Context-aware recommendations
    - A/B testing and performance monitoring
    - Privacy-preserving personalization
    """
    
    def __init__(
        self,
        name: str = "{{agent_name}}",
        config: Optional[PersonalizationConfig] = None,
        **kwargs
    ):
        super().__init__(name=name, **kwargs)
        self.config = config or PersonalizationConfig()
        
        # Initialize components
        self.model_manager = PersonalizationModelManager()
        self.collaborative_filter = CollaborativeFilter()
        self.content_filter = ContentBasedFilter()
        self.deep_recommender = DeepRecommender()
        self.profile_builder = UserProfileBuilder()
        self.behavior_analyzer = BehaviorAnalyzer()
        self.preference_learner = PreferenceLearner()
        
        # Initialize scalers and models
        self.feature_scaler = StandardScaler()
        self.user_clusterer = KMeans(n_clusters=8, random_state=42)
        
        # User profile cache
        self.profile_cache: Dict[str, UserProfile] = {}
        self.cache_timestamps: Dict[str, datetime] = {}
        
        # Initialize metrics collector
        self.metrics = PersonalizationMetricsCollector()
        
        # Load models and embeddings
        self._load_models()
        
        logger.info(f"Personalization agent '{name}' initialized successfully")

    def _load_models(self) -> None:
        """Load and initialize personalization models"""
        try:
            # Initialize deep personalization model
            if self.config.enable_deep_learning:
                self.deep_model = DeepPersonalizationModel(
                    user_features=10000,  # Will be updated based on actual data
                    item_features=50000,  # Will be updated based on actual data
                    embedding_dim=self.config.embedding_dimension
                )
                
                if torch.cuda.is_available():
                    self.deep_model = self.deep_model.cuda()
                
                self.optimizer = torch.optim.Adam(
                    self.deep_model.parameters(),
                    lr=self.config.learning_rate
                )
                self.criterion = nn.BCELoss()
            
            # Load content embeddings model
            self.content_tokenizer = AutoTokenizer.from_pretrained(
                "sentence-transformers/all-MiniLM-L6-v2"
            )
            self.content_model = AutoModel.from_pretrained(
                "sentence-transformers/all-MiniLM-L6-v2"
            )
            
            logger.info("All personalization models loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading personalization models: {str(e)}")
            raise PersonalizationException(f"Model loading failed: {str(e)}")

    async def personalize(
        self,
        request: PersonalizationRequest
    ) -> PersonalizationResult:
        """
        Generate personalized recommendations for user.
        
        Args:
            request: Personalization request
            
        Returns:
            PersonalizationResult with recommendations
        """
        start_time = datetime.utcnow()
        
        try:
            # Get or build user profile
            user_profile = await self._get_user_profile(request.user_id)
            
            # Update profile with current context
            await self._update_profile_context(user_profile, request.context)
            
            # Generate recommendations based on strategy
            if request.strategy == RecommendationStrategy.COLLABORATIVE_FILTERING:
                items = await self._collaborative_filtering(request, user_profile)
            elif request.strategy == RecommendationStrategy.CONTENT_BASED:
                items = await self._content_based_filtering(request, user_profile)
            elif request.strategy == RecommendationStrategy.DEEP_LEARNING:
                items = await self._deep_learning_recommendations(request, user_profile)
            elif request.strategy == RecommendationStrategy.HYBRID:
                items = await self._hybrid_recommendations(request, user_profile)
            elif request.strategy == RecommendationStrategy.POPULARITY_BASED:
                items = await self._popularity_based_recommendations(request, user_profile)
            elif request.strategy == RecommendationStrategy.TRENDING:
                items = await self._trending_recommendations(request, user_profile)
            elif request.strategy == RecommendationStrategy.DIVERSIFIED:
                items = await self._diversified_recommendations(request, user_profile)
            else:
                items = await self._hybrid_recommendations(request, user_profile)
            
            # Apply post-processing
            items = await self._post_process_recommendations(items, request, user_profile)
            
            # Generate explanations if requested
            if request.include_explanations:
                await self._add_explanations(items, user_profile, request)
            
            # Calculate performance metrics
            performance_metrics = await self._calculate_performance_metrics(
                items, user_profile, request
            )
            
            # Calculate processing time
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            # Create result
            result = PersonalizationResult(
                user_id=request.user_id,
                personalization_type=request.personalization_type,
                strategy=request.strategy,
                items=items,
                user_profile=user_profile,
                context=request.context,
                performance_metrics=performance_metrics,
                processing_time=processing_time,
                metadata={
                    "total_candidates": len(items),
                    "strategy_used": request.strategy.value,
                    "diversification_applied": request.diversification > 0
                }
            )
            
            # Record metrics
            await self.metrics.record_personalization(request, result)
            
            # Update user profile based on recommendations
            if self.config.enable_real_time_learning:
                await self._update_profile_with_recommendations(user_profile, items)
            
            return result
            
        except Exception as e:
            logger.error(f"Personalization failed: {str(e)}")
            raise PersonalizationException(f"Personalization failed: {str(e)}")

    async def _get_user_profile(self, user_id: str) -> UserProfile:
        """Get or create user profile"""
        try:
            # Check cache first
            if user_id in self.profile_cache:
                cache_time = self.cache_timestamps.get(user_id, datetime.min)
                cache_age = (datetime.utcnow() - cache_time).total_seconds() / 60
                
                if cache_age < self.config.cache_duration_minutes:
                    return self.profile_cache[user_id]
            
            # Build or refresh profile
            profile = await self.profile_builder.build_profile(user_id)
            
            # Update cache
            self.profile_cache[user_id] = profile
            self.cache_timestamps[user_id] = datetime.utcnow()
            
            return profile
            
        except Exception as e:
            logger.error(f"Error getting user profile: {str(e)}")
            # Return default profile for new users
            return UserProfile(
                user_id=user_id,
                segment=UserSegment.NEW_USER,
                interests=[],
                preferences={},
                behavior_patterns={}
            )

    async def _collaborative_filtering(
        self,
        request: PersonalizationRequest,
        user_profile: UserProfile
    ) -> List[RecommendationItem]:
        """Generate recommendations using collaborative filtering"""
        try:
            # Check if user has enough interactions
            if len(user_profile.interaction_history) < self.config.min_interactions_for_cf:
                # Fall back to content-based for cold start
                return await self._content_based_filtering(request, user_profile)
            
            # Get similar users
            similar_users = await self.collaborative_filter.find_similar_users(
                user_profile.user_id, top_k=50
            )
            
            # Get recommendations from similar users
            candidate_items = await self.collaborative_filter.get_recommendations(
                user_profile.user_id, similar_users, count=request.count * 3
            )
            
            # Convert to RecommendationItem objects
            items = []
            for item_data in candidate_items[:request.count]:
                item = RecommendationItem(
                    item_id=item_data['item_id'],
                    item_type=item_data.get('item_type', 'content'),
                    title=item_data.get('title', ''),
                    score=item_data.get('score', 0.5),
                    relevance_score=item_data.get('score', 0.5),
                    novelty_score=0.5,  # Will be calculated later
                    diversity_score=0.5,  # Will be calculated later
                    features=item_data.get('features', {})
                )
                items.append(item)
            
            return items
            
        except Exception as e:
            logger.error(f"Collaborative filtering failed: {str(e)}")
            return []

    async def _content_based_filtering(
        self,
        request: PersonalizationRequest,
        user_profile: UserProfile
    ) -> List[RecommendationItem]:
        """Generate recommendations using content-based filtering"""
        try:
            # Extract user interests and preferences
            user_interests = user_profile.interests
            user_preferences = user_profile.preferences
            
            # Get candidate items based on interests
            candidate_items = await self.content_filter.get_items_by_interests(
                user_interests, count=request.count * 5
            )
            
            # Calculate content similarity scores
            scored_items = []
            for item_data in candidate_items:
                # Calculate similarity based on content features
                similarity_score = await self._calculate_content_similarity(
                    user_profile, item_data
                )
                
                item = RecommendationItem(
                    item_id=item_data['item_id'],
                    item_type=item_data.get('item_type', 'content'),
                    title=item_data.get('title', ''),
                    score=similarity_score,
                    relevance_score=similarity_score,
                    novelty_score=0.5,
                    diversity_score=0.5,
                    features=item_data.get('features', {})
                )
                scored_items.append(item)
            
            # Sort by score and return top items
            scored_items.sort(key=lambda x: x.score, reverse=True)
            return scored_items[:request.count]
            
        except Exception as e:
            logger.error(f"Content-based filtering failed: {str(e)}")
            return []

    async def _deep_learning_recommendations(
        self,
        request: PersonalizationRequest,
        user_profile: UserProfile
    ) -> List[RecommendationItem]:
        """Generate recommendations using deep learning model"""
        try:
            if not self.config.enable_deep_learning:
                return await self._hybrid_recommendations(request, user_profile)
            
            # Get candidate items
            candidate_items = await self._get_candidate_items(
                request, user_profile, count=request.count * 10
            )
            
            # Prepare data for deep model
            user_id_tensor = torch.tensor([hash(user_profile.user_id) % 10000])
            item_ids = [hash(item['item_id']) % 50000 for item in candidate_items]
            item_ids_tensor = torch.tensor(item_ids)
            
            if torch.cuda.is_available():
                user_id_tensor = user_id_tensor.cuda()
                item_ids_tensor = item_ids_tensor.cuda()
            
            # Get predictions
            self.deep_model.eval()
            with torch.no_grad():
                user_ids_expanded = user_id_tensor.repeat(len(item_ids))
                scores = self.deep_model(user_ids_expanded, item_ids_tensor)
                scores = scores.cpu().numpy()
            
            # Create recommendation items
            items = []
            for i, (item_data, score) in enumerate(zip(candidate_items, scores)):
                item = RecommendationItem(
                    item_id=item_data['item_id'],
                    item_type=item_data.get('item_type', 'content'),
                    title=item_data.get('title', ''),
                    score=float(score),
                    relevance_score=float(score),
                    novelty_score=0.5,
                    diversity_score=0.5,
                    features=item_data.get('features', {})
                )
                items.append(item)
            
            # Sort by score and return top items
            items.sort(key=lambda x: x.score, reverse=True)
            return items[:request.count]
            
        except Exception as e:
            logger.error(f"Deep learning recommendations failed: {str(e)}")
            return []

    async def _hybrid_recommendations(
        self,
        request: PersonalizationRequest,
        user_profile: UserProfile
    ) -> List[RecommendationItem]:
        """Generate recommendations using hybrid approach"""
        try:
            # Get recommendations from different strategies
            cf_items = await self._collaborative_filtering(request, user_profile)
            cb_items = await self._content_based_filtering(request, user_profile)
            
            if self.config.enable_deep_learning:
                dl_items = await self._deep_learning_recommendations(request, user_profile)
            else:
                dl_items = []
            
            # Combine and weight recommendations
            combined_items = {}
            
            # Collaborative filtering (weight: 0.4)
            for item in cf_items:
                if item.item_id not in combined_items:
                    combined_items[item.item_id] = item
                    combined_items[item.item_id].score *= 0.4
                else:
                    combined_items[item.item_id].score += item.score * 0.4
            
            # Content-based (weight: 0.3)
            for item in cb_items:
                if item.item_id not in combined_items:
                    combined_items[item.item_id] = item
                    combined_items[item.item_id].score *= 0.3
                else:
                    combined_items[item.item_id].score += item.score * 0.3
            
            # Deep learning (weight: 0.3)
            for item in dl_items:
                if item.item_id not in combined_items:
                    combined_items[item.item_id] = item
                    combined_items[item.item_id].score *= 0.3
                else:
                    combined_items[item.item_id].score += item.score * 0.3
            
            # Convert to list and sort
            hybrid_items = list(combined_items.values())
            hybrid_items.sort(key=lambda x: x.score, reverse=True)
            
            return hybrid_items[:request.count]
            
        except Exception as e:
            logger.error(f"Hybrid recommendations failed: {str(e)}")
            return []

    async def _popularity_based_recommendations(
        self,
        request: PersonalizationRequest,
        user_profile: UserProfile
    ) -> List[RecommendationItem]:
        """Generate recommendations based on popularity"""
        try:
            # Get popular items
            popular_items = await self._get_popular_items(
                request.personalization_type,
                count=request.count * 2
            )
            
            # Filter based on user preferences
            filtered_items = []
            for item_data in popular_items:
                # Simple relevance scoring based on user interests
                relevance = 0.5  # Base relevance
                
                if user_profile.interests:
                    item_categories = item_data.get('categories', [])
                    overlap = set(user_profile.interests) & set(item_categories)
                    relevance += len(overlap) * 0.1
                
                item = RecommendationItem(
                    item_id=item_data['item_id'],
                    item_type=item_data.get('item_type', 'content'),
                    title=item_data.get('title', ''),
                    score=item_data.get('popularity_score', 0.5),
                    relevance_score=relevance,
                    novelty_score=0.2,  # Popular items are less novel
                    diversity_score=0.5,
                    features=item_data.get('features', {})
                )
                filtered_items.append(item)
            
            return filtered_items[:request.count]
            
        except Exception as e:
            logger.error(f"Popularity-based recommendations failed: {str(e)}")
            return []

    async def _trending_recommendations(
        self,
        request: PersonalizationRequest,
        user_profile: UserProfile
    ) -> List[RecommendationItem]:
        """Generate recommendations based on trending content"""
        try:
            # Get trending items
            trending_items = await self._get_trending_items(
                request.personalization_type,
                count=request.count * 2
            )
            
            # Score based on user preferences and trend strength
            scored_items = []
            for item_data in trending_items:
                # Calculate trend-adjusted score
                trend_score = item_data.get('trend_score', 0.5)
                user_interest_score = await self._calculate_user_interest_score(
                    user_profile, item_data
                )
                
                final_score = (trend_score * 0.6 + user_interest_score * 0.4)
                
                item = RecommendationItem(
                    item_id=item_data['item_id'],
                    item_type=item_data.get('item_type', 'content'),
                    title=item_data.get('title', ''),
                    score=final_score,
                    relevance_score=user_interest_score,
                    novelty_score=0.8,  # Trending items are novel
                    diversity_score=0.5,
                    features=item_data.get('features', {})
                )
                scored_items.append(item)
            
            # Sort by final score
            scored_items.sort(key=lambda x: x.score, reverse=True)
            return scored_items[:request.count]
            
        except Exception as e:
            logger.error(f"Trending recommendations failed: {str(e)}")
            return []

    async def _diversified_recommendations(
        self,
        request: PersonalizationRequest,
        user_profile: UserProfile
    ) -> List[RecommendationItem]:
        """Generate diversified recommendations"""
        try:
            # Get initial recommendations using hybrid approach
            initial_items = await self._hybrid_recommendations(request, user_profile)
            
            # Apply diversification algorithm
            diversified_items = await self._apply_diversification(
                initial_items, request.diversification
            )
            
            return diversified_items[:request.count]
            
        except Exception as e:
            logger.error(f"Diversified recommendations failed: {str(e)}")
            return []

    async def _post_process_recommendations(
        self,
        items: List[RecommendationItem],
        request: PersonalizationRequest,
        user_profile: UserProfile
    ) -> List[RecommendationItem]:
        """Post-process recommendations"""
        try:
            # Calculate novelty scores
            for item in items:
                item.novelty_score = await self._calculate_novelty_score(
                    item, user_profile
                )
            
            # Calculate diversity scores
            await self._calculate_diversity_scores(items)
            
            # Apply freshness weighting
            if request.freshness_weight > 0:
                await self._apply_freshness_weighting(items, request.freshness_weight)
            
            # Apply diversification if requested
            if request.diversification > 0:
                items = await self._apply_diversification(items, request.diversification)
            
            # Apply filters
            if request.filters:
                items = await self._apply_filters(items, request.filters)
            
            # Re-rank based on final scores
            for item in items:
                item.score = (
                    item.relevance_score * 0.5 +
                    item.novelty_score * 0.3 +
                    item.diversity_score * 0.2
                )
            
            items.sort(key=lambda x: x.score, reverse=True)
            
            return items[:request.count]
            
        except Exception as e:
            logger.error(f"Post-processing failed: {str(e)}")
            return items

    async def _calculate_content_similarity(
        self,
        user_profile: UserProfile,
        item_data: Dict[str, Any]
    ) -> float:
        """Calculate content similarity between user profile and item"""
        try:
            # Simple similarity based on interests and features
            similarity = 0.0
            
            # Interest overlap
            item_categories = item_data.get('categories', [])
            user_interests = user_profile.interests
            
            if user_interests and item_categories:
                overlap = set(user_interests) & set(item_categories)
                similarity += len(overlap) / len(set(user_interests) | set(item_categories))
            
            # Feature-based similarity (simplified)
            item_features = item_data.get('features', {})
            user_preferences = user_profile.preferences
            
            if user_preferences and item_features:
                for feature, value in item_features.items():
                    if feature in user_preferences:
                        # Simple feature matching
                        if isinstance(value, (int, float)) and isinstance(user_preferences[feature], (int, float)):
                            similarity += 1.0 - abs(value - user_preferences[feature])
                        elif value == user_preferences[feature]:
                            similarity += 1.0
            
            return min(similarity, 1.0)
            
        except Exception:
            return 0.5  # Default similarity

    async def _calculate_novelty_score(
        self,
        item: RecommendationItem,
        user_profile: UserProfile
    ) -> float:
        """Calculate novelty score for an item"""
        try:
            # Check if user has interacted with similar items
            interaction_history = user_profile.interaction_history
            
            # Simple novelty: based on how different this item is from past interactions
            novelty = 1.0
            
            for interaction in interaction_history[-50:]:  # Last 50 interactions
                if interaction.get('item_type') == item.item_type:
                    # Reduce novelty if similar items were recently interacted with
                    novelty *= 0.95
            
            # Boost novelty for items from categories user hasn't explored
            item_categories = item.features.get('categories', [])
            user_categories = set()
            
            for interaction in interaction_history:
                user_categories.update(interaction.get('categories', []))
            
            if item_categories and not (set(item_categories) & user_categories):
                novelty = min(novelty * 1.2, 1.0)
            
            return novelty
            
        except Exception:
            return 0.5

    async def _calculate_diversity_scores(self, items: List[RecommendationItem]) -> None:
        """Calculate diversity scores for items"""
        try:
            # Simple diversity: based on feature differences
            for i, item in enumerate(items):
                diversity = 0.0
                count = 0
                
                for j, other_item in enumerate(items):
                    if i != j:
                        # Calculate dissimilarity
                        dissimilarity = await self._calculate_item_dissimilarity(
                            item, other_item
                        )
                        diversity += dissimilarity
                        count += 1
                
                if count > 0:
                    item.diversity_score = diversity / count
                else:
                    item.diversity_score = 1.0
                    
        except Exception:
            # Set default diversity scores
            for item in items:
                item.diversity_score = 0.5

    async def _calculate_item_dissimilarity(
        self,
        item1: RecommendationItem,
        item2: RecommendationItem
    ) -> float:
        """Calculate dissimilarity between two items"""
        try:
            if item1.item_type != item2.item_type:
                return 1.0  # Different types are completely dissimilar
            
            # Compare features
            features1 = item1.features
            features2 = item2.features
            
            if not features1 or not features2:
                return 0.5  # Default dissimilarity
            
            # Simple feature-based dissimilarity
            dissimilarity = 0.0
            common_features = set(features1.keys()) & set(features2.keys())
            
            if common_features:
                for feature in common_features:
                    val1 = features1[feature]
                    val2 = features2[feature]
                    
                    if isinstance(val1, (int, float)) and isinstance(val2, (int, float)):
                        dissimilarity += abs(val1 - val2) / max(abs(val1), abs(val2), 1)
                    elif val1 != val2:
                        dissimilarity += 1.0
                
                dissimilarity /= len(common_features)
            else:
                dissimilarity = 0.5
            
            return min(dissimilarity, 1.0)
            
        except Exception:
            return 0.5

    async def _apply_diversification(
        self,
        items: List[RecommendationItem],
        diversification_factor: float
    ) -> List[RecommendationItem]:
        """Apply diversification to recommendation list"""
        try:
            if diversification_factor <= 0 or len(items) <= 1:
                return items
            
            # Greedy diversification algorithm
            diversified = [items[0]]  # Start with top item
            remaining = items[1:]
            
            while remaining and len(diversified) < len(items):
                best_item = None
                best_score = -1
                
                for item in remaining:
                    # Calculate diversification score
                    min_similarity = 1.0
                    for selected_item in diversified:
                        similarity = 1.0 - await self._calculate_item_dissimilarity(
                            item, selected_item
                        )
                        min_similarity = min(min_similarity, similarity)
                    
                    # Combined score: relevance + diversity
                    combined_score = (
                        item.score * (1 - diversification_factor) +
                        (1 - min_similarity) * diversification_factor
                    )
                    
                    if combined_score > best_score:
                        best_score = combined_score
                        best_item = item
                
                if best_item:
                    diversified.append(best_item)
                    remaining.remove(best_item)
                else:
                    break
            
            return diversified
            
        except Exception as e:
            logger.error(f"Diversification failed: {str(e)}")
            return items

    async def _apply_freshness_weighting(
        self,
        items: List[RecommendationItem],
        freshness_weight: float
    ) -> None:
        """Apply freshness weighting to items"""
        try:
            current_time = datetime.utcnow()
            
            for item in items:
                # Get item creation time (simplified)
                created_at = item.features.get('created_at')
                if created_at:
                    if isinstance(created_at, str):
                        created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    
                    # Calculate age in days
                    age_days = (current_time - created_at).total_seconds() / (24 * 3600)
                    
                    # Freshness score (newer items get higher scores)
                    freshness_score = max(0, 1.0 - (age_days / 30.0))  # 30-day decay
                    
                    # Apply freshness weighting
                    item.score = (
                        item.score * (1 - freshness_weight) +
                        freshness_score * freshness_weight
                    )
                    
        except Exception as e:
            logger.error(f"Freshness weighting failed: {str(e)}")

    async def _apply_filters(
        self,
        items: List[RecommendationItem],
        filters: Dict[str, Any]
    ) -> List[RecommendationItem]:
        """Apply filters to recommendation items"""
        try:
            filtered_items = []
            
            for item in items:
                include_item = True
                
                for filter_key, filter_value in filters.items():
                    item_value = item.features.get(filter_key)
                    
                    if item_value is None:
                        continue
                    
                    # Simple filter matching
                    if isinstance(filter_value, list):
                        if item_value not in filter_value:
                            include_item = False
                            break
                    elif item_value != filter_value:
                        include_item = False
                        break
                
                if include_item:
                    filtered_items.append(item)
            
            return filtered_items
            
        except Exception as e:
            logger.error(f"Filtering failed: {str(e)}")
            return items

    async def _get_candidate_items(
        self,
        request: PersonalizationRequest,
        user_profile: UserProfile,
        count: int
    ) -> List[Dict[str, Any]]:
        """Get candidate items for recommendation"""
        # Placeholder implementation - would integrate with item catalog
        candidates = []
        
        for i in range(count):
            candidate = {
                'item_id': f'item_{i}',
                'item_type': 'content',
                'title': f'Content Item {i}',
                'categories': ['music', 'video', 'art'][i % 3],
                'features': {
                    'popularity': np.random.random(),
                    'quality_score': np.random.random(),
                    'categories': [['music'], ['video'], ['art']][i % 3]
                }
            }
            candidates.append(candidate)
        
        return candidates

    async def _get_popular_items(
        self,
        personalization_type: PersonalizationType,
        count: int
    ) -> List[Dict[str, Any]]:
        """Get popular items"""
        # Placeholder implementation
        return await self._get_candidate_items(None, None, count)

    async def _get_trending_items(
        self,
        personalization_type: PersonalizationType,
        count: int
    ) -> List[Dict[str, Any]]:
        """Get trending items"""
        # Placeholder implementation
        items = await self._get_candidate_items(None, None, count)
        for item in items:
            item['trend_score'] = np.random.random()
        return items

    async def _calculate_user_interest_score(
        self,
        user_profile: UserProfile,
        item_data: Dict[str, Any]
    ) -> float:
        """Calculate user interest score for an item"""
        # Simplified interest calculation
        item_categories = item_data.get('categories', [])
        user_interests = user_profile.interests
        
        if not user_interests or not item_categories:
            return 0.5
        
        overlap = set(user_interests) & set(item_categories)
        return len(overlap) / len(set(user_interests) | set(item_categories))

    async def _update_profile_context(
        self,
        user_profile: UserProfile,
        context: Dict[str, Any]
    ) -> None:
        """Update user profile with current context"""
        try:
            # Update behavior patterns based on context
            if 'session_time' in context:
                user_profile.behavior_patterns['last_session_time'] = context['session_time']
            
            if 'device_type' in context:
                user_profile.behavior_patterns['preferred_device'] = context['device_type']
            
            if 'location' in context:
                user_profile.behavior_patterns['current_location'] = context['location']
                
        except Exception as e:
            logger.error(f"Profile context update failed: {str(e)}")

    async def _update_profile_with_recommendations(
        self,
        user_profile: UserProfile,
        items: List[RecommendationItem]
    ) -> None:
        """Update user profile based on recommendations shown"""
        try:
            # Track recommended items for future feedback learning
            recommendation_record = {
                'timestamp': datetime.utcnow(),
                'recommended_items': [item.item_id for item in items],
                'personalization_type': 'recommendation_display'
            }
            
            user_profile.interaction_history.append(recommendation_record)
            
            # Keep only recent interactions
            if len(user_profile.interaction_history) > 1000:
                user_profile.interaction_history = user_profile.interaction_history[-1000:]
            
            user_profile.last_updated = datetime.utcnow()
            
        except Exception as e:
            logger.error(f"Profile update failed: {str(e)}")

    async def _add_explanations(
        self,
        items: List[RecommendationItem],
        user_profile: UserProfile,
        request: PersonalizationRequest
    ) -> None:
        """Add explanations to recommendation items"""
        try:
            for item in items:
                explanation_parts = []
                
                # Explain based on strategy
                if request.strategy == RecommendationStrategy.COLLABORATIVE_FILTERING:
                    explanation_parts.append("Recommended because similar users liked this")
                elif request.strategy == RecommendationStrategy.CONTENT_BASED:
                    explanation_parts.append("Matches your interests")
                elif request.strategy == RecommendationStrategy.POPULARITY_BASED:
                    explanation_parts.append("Popular among all users")
                elif request.strategy == RecommendationStrategy.TRENDING:
                    explanation_parts.append("Currently trending")
                
                # Add interest-based explanation
                item_categories = item.features.get('categories', [])
                user_interests = user_profile.interests
                
                if item_categories and user_interests:
                    common_interests = set(item_categories) & set(user_interests)
                    if common_interests:
                        explanation_parts.append(
                            f"Related to your interests: {', '.join(common_interests)}"
                        )
                
                item.explanation = "; ".join(explanation_parts) if explanation_parts else "Recommended for you"
                
        except Exception as e:
            logger.error(f"Explanation generation failed: {str(e)}")

    async def _calculate_performance_metrics(
        self,
        items: List[RecommendationItem],
        user_profile: UserProfile,
        request: PersonalizationRequest
    ) -> Dict[str, float]:
        """Calculate performance metrics for recommendations"""
        try:
            if not items:
                return {"coverage": 0.0, "diversity": 0.0, "novelty": 0.0}
            
            # Coverage: how many user interests are covered
            covered_interests = set()
            user_interests = set(user_profile.interests)
            
            for item in items:
                item_categories = set(item.features.get('categories', []))
                covered_interests.update(item_categories & user_interests)
            
            coverage = len(covered_interests) / len(user_interests) if user_interests else 0.0
            
            # Average diversity
            diversity = sum(item.diversity_score for item in items) / len(items)
            
            # Average novelty
            novelty = sum(item.novelty_score for item in items) / len(items)
            
            # Average relevance
            relevance = sum(item.relevance_score for item in items) / len(items)
            
            return {
                "coverage": coverage,
                "diversity": diversity,
                "novelty": novelty,
                "relevance": relevance
            }
            
        except Exception as e:
            logger.error(f"Performance metrics calculation failed: {str(e)}")
            return {"error": 1.0}

    async def train_personalization_model(
        self,
        training_data: List[Dict[str, Any]]
    ) -> Dict[str, float]:
        """Train personalization model with user feedback data"""
        try:
            if not self.config.enable_deep_learning or not training_data:
                return {"status": "skipped"}
            
            # Prepare training data
            user_ids = []
            item_ids = []
            labels = []
            
            for data_point in training_data:
                user_ids.append(hash(data_point['user_id']) % 10000)
                item_ids.append(hash(data_point['item_id']) % 50000)
                labels.append(float(data_point.get('rating', 0) > 0.5))
            
            # Convert to tensors
            user_tensor = torch.tensor(user_ids, dtype=torch.long)
            item_tensor = torch.tensor(item_ids, dtype=torch.long)
            label_tensor = torch.tensor(labels, dtype=torch.float32)
            
            if torch.cuda.is_available():
                user_tensor = user_tensor.cuda()
                item_tensor = item_tensor.cuda()
                label_tensor = label_tensor.cuda()
            
            # Training loop
            self.deep_model.train()
            total_loss = 0.0
            
            for epoch in range(10):  # Simple training
                self.optimizer.zero_grad()
                
                predictions = self.deep_model(user_tensor, item_tensor)
                loss = self.criterion(predictions, label_tensor)
                
                loss.backward()
                self.optimizer.step()
                
                total_loss += loss.item()
            
            avg_loss = total_loss / 10
            
            return {
                "training_loss": avg_loss,
                "samples_trained": len(training_data),
                "status": "completed"
            }
            
        except Exception as e:
            logger.error(f"Model training failed: {str(e)}")
            return {"status": "failed", "error": str(e)}

    def get_capabilities(self) -> Dict[str, Any]:
        """Get agent capabilities"""
        return {
            "personalization_types": [t.value for t in PersonalizationType],
            "recommendation_strategies": [s.value for s in RecommendationStrategy],
            "user_segments": [s.value for s in UserSegment],
            "supports_real_time_learning": self.config.enable_real_time_learning,
            "supports_deep_learning": self.config.enable_deep_learning,
            "supports_cold_start": self.config.enable_cold_start_handling,
            "supports_diversification": self.config.enable_diversity_optimization,
            "embedding_dimension": self.config.embedding_dimension
        }

    def get_metrics(self) -> Dict[str, Any]:
        """Get personalization metrics"""
        return self.metrics.get_summary()