"""Recommendation Engine Module

Advanced recommendation system for content discovery, creator collaboration,
and personalized content delivery in the IA Influencer platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  LEGAL WARNING ⚠️
This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use is strictly prohibited.
Contact: mlaiel@live.de
"""import asyncio
import numpy as np
import pandas as pd
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Union, Any, Tuple, Set
import logging
from pathlib import Path
import json
import pickle
from scipy.sparse import csr_matrix
from scipy.spatial.distance import cosine, euclidean
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import TruncatedSVD, NMF
from sklearn.neighbors import NearestNeighbors
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
import networkx as nx
import torch
import torch.nn as nn
import torch.nn.functional as F
from collections import defaultdict, Counter
import heapq
import random

logger = logging.getLogger(__name__)


class RecommendationType(Enum):
    """Types of recommendations"""    CONTENT = "content"
    CREATOR = "creator"
    COLLABORATION = "collaboration"
    TRENDING = "trending"
    SIMILAR = "similar"
    PERSONALIZED = "personalized"
    CROSS_PLATFORM = "cross_platform"


class RecommendationStrategy(Enum):
    """Recommendation strategies"""    COLLABORATIVE_FILTERING = "collaborative_filtering"
    CONTENT_BASED = "content_based"
    HYBRID = "hybrid"
    MATRIX_FACTORIZATION = "matrix_factorization"
    DEEP_LEARNING = "deep_learning"
    GRAPH_BASED = "graph_based"
    TRENDING_BASED = "trending_based"


class InteractionType(Enum):
    """User interaction types"""    VIEW = "view"
    LIKE = "like"
    SHARE = "share"
    COMMENT = "comment"
    FOLLOW = "follow"
    COLLABORATE = "collaborate"
    SAVE = "save"
    DOWNLOAD = "download"


@dataclass
class UserInteraction:
    """User interaction data"""    user_id: str
    item_id: str
    interaction_type: InteractionType
    rating: Optional[float] = None
    timestamp: datetime = field(default_factory=datetime.now)
    context: Dict[str, Any] = field(default_factory=dict)
    duration_seconds: Optional[float] = None
    platform: Optional[str] = None


@dataclass
class RecommendationItem:
    """Item to be recommended"""    item_id: str
    item_type: str
    title: str
    creator_id: str
    category: str
    tags: List[str] = field(default_factory=list)
    features: Dict[str, Any] = field(default_factory=dict)
    metrics: Dict[str, float] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class UserProfile:
    """User profile for recommendations"""    user_id: str
    demographics: Dict[str, Any] = field(default_factory=dict)
    preferences: Dict[str, float] = field(default_factory=dict)
    interests: List[str] = field(default_factory=list)
    behavior_patterns: Dict[str, Any] = field(default_factory=dict)
    interaction_history: List[UserInteraction] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class RecommendationResult:
    """Result from recommendation engine"""    recommendations: List[Tuple[str, float]]  # (item_id, score)
    strategy_used: RecommendationStrategy
    confidence_score: float
    explanation: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    generated_at: datetime = field(default_factory=datetime.now)


@dataclass
class RecommendationConfig:
    """Configuration for recommendation engine"""    max_recommendations: int = 10
    min_score_threshold: float = 0.1
    diversity_weight: float = 0.2
    novelty_weight: float = 0.1
    popularity_weight: float = 0.3
    recency_weight: float = 0.2
    enable_cold_start: bool = True
    enable_diversity: bool = True
    enable_explanation: bool = True
    cache_ttl_seconds: int = 3600
    batch_size: int = 1000
    model_update_interval_hours: int = 24


class RecommendationEngine(ABC):
    """Abstract base class for recommendation engines"""    
    def __init__(self, config: RecommendationConfig):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.is_trained = False
        self.model = None
        self.feature_matrix = None
        self.item_features = {}
        self.user_profiles = {}
        
    @abstractmethod
    async def fit(self, interactions: List[UserInteraction], items: List[RecommendationItem]):
        """Train the recommendation model"""        pass
    
    @abstractmethod
    async def recommend(
        self,
        user_id: str,
        user_profile: Optional[UserProfile] = None,
        exclude_items: Set[str] = None
    ) -> RecommendationResult:
        """Generate recommendations for a user"""        pass
    
    def _calculate_diversity_score(self, recommendations: List[str]) -> float:
        """Calculate diversity score of recommendations"""        if len(recommendations) < 2:
            return 1.0
        
        total_similarity = 0
        pairs = 0
        
        for i in range(len(recommendations)):
            for j in range(i + 1, len(recommendations)):
                item1_features = self.item_features.get(recommendations[i], {})
                item2_features = self.item_features.get(recommendations[j], {})
                
                # Simple category-based diversity
                if item1_features.get('category') == item2_features.get('category'):
                    total_similarity += 1
                
                pairs += 1
        
        avg_similarity = total_similarity / pairs if pairs > 0 else 0
        return 1.0 - avg_similarity
    
    def _apply_business_rules(
        self,
        recommendations: List[Tuple[str, float]],
        user_profile: UserProfile
    ) -> List[Tuple[str, float]]:
        """Apply business rules to filter/rerank recommendations"""        filtered = []
        
        for item_id, score in recommendations:
            item_features = self.item_features.get(item_id, {})
            
            # Content safety filter
            if item_features.get('safety_score', 1.0) < 0.5:
                continue
            
            # Age-appropriate content
            user_age = user_profile.demographics.get('age', 18)
            content_rating = item_features.get('content_rating', 'G')
            
            if user_age < 18 and content_rating in ['R', 'MA']:
                continue
            
            # Quality threshold
            if item_features.get('quality_score', 0.0) < 0.3:
                continue
            
            filtered.append((item_id, score))
        
        return filtered


class CollaborativeFiltering(RecommendationEngine):
    """Collaborative filtering recommendation engine"""    
    def __init__(self, config: RecommendationConfig):
        super().__init__(config)
        self.user_item_matrix = None
        self.item_similarity_matrix = None
        self.user_similarity_matrix = None
        self.svd_model = None
        self.user_to_idx = {}
        self.item_to_idx = {}
        self.idx_to_user = {}
        self.idx_to_item = {}
    
    async def fit(self, interactions: List[UserInteraction], items: List[RecommendationItem]):
        """Train collaborative filtering model"""        self.logger.info("Training collaborative filtering model")
        
        try:
            # Build user-item interaction matrix
            await self._build_interaction_matrix(interactions, items)
            
            # Train SVD for matrix factorization
            await self._train_matrix_factorization()
            
            # Calculate similarity matrices
            await self._calculate_similarity_matrices()
            
            self.is_trained = True
            self.logger.info("Collaborative filtering model trained successfully")
            
        except Exception as e:
            self.logger.error(f"Training failed: {e}")
            raise
    
    async def _build_interaction_matrix(
        self,
        interactions: List[UserInteraction],
        items: List[RecommendationItem]
    ):
        """Build user-item interaction matrix"""        # Create mappings
        users = set(interaction.user_id for interaction in interactions)
        item_ids = set(interaction.item_id for interaction in interactions)
        
        self.user_to_idx = {user: idx for idx, user in enumerate(users)}
        self.item_to_idx = {item: idx for idx, item in enumerate(item_ids)}
        self.idx_to_user = {idx: user for user, idx in self.user_to_idx.items()}
        self.idx_to_item = {idx: item for item, idx in self.item_to_idx.items()}
        
        # Store item features
        for item in items:
            self.item_features[item.item_id] = {
                'category': item.category,
                'tags': item.tags,
                'features': item.features,
                'metrics': item.metrics
            }
        
        # Build matrix
        n_users = len(users)
        n_items = len(item_ids)
        
        # Use implicit feedback with weighted ratings
        interaction_weights = {
            InteractionType.VIEW: 1.0,
            InteractionType.LIKE: 3.0,
            InteractionType.SHARE: 5.0,
            InteractionType.COMMENT: 4.0,
            InteractionType.FOLLOW: 6.0,
            InteractionType.COLLABORATE: 8.0,
            InteractionType.SAVE: 4.0,
            InteractionType.DOWNLOAD: 5.0
        }
        
        # Build sparse matrix
        row_indices = []
        col_indices = []
        data = []
        
        user_item_scores = defaultdict(lambda: defaultdict(float))
        
        for interaction in interactions:
            if (interaction.user_id in self.user_to_idx and 
                interaction.item_id in self.item_to_idx):
                
                user_idx = self.user_to_idx[interaction.user_id]
                item_idx = self.item_to_idx[interaction.item_id]
                
                # Calculate interaction score
                base_score = interaction_weights.get(interaction.interaction_type, 1.0)
                
                # Apply time decay
                days_ago = (datetime.now() - interaction.timestamp).days
                time_decay = np.exp(-days_ago / 30.0)  # 30-day half-life
                
                # Apply duration bonus for views
                duration_bonus = 1.0
                if (interaction.interaction_type == InteractionType.VIEW and 
                    interaction.duration_seconds):
                    duration_bonus = min(interaction.duration_seconds / 60.0, 3.0)  # Cap at 3x
                
                final_score = base_score * time_decay * duration_bonus
                user_item_scores[user_idx][item_idx] += final_score
        
        # Convert to sparse matrix format
        for user_idx, items_dict in user_item_scores.items():
            for item_idx, score in items_dict.items():
                row_indices.append(user_idx)
                col_indices.append(item_idx)
                data.append(score)
        
        self.user_item_matrix = csr_matrix(
            (data, (row_indices, col_indices)),
            shape=(n_users, n_items)
        )
    
    async def _train_matrix_factorization(self):
        """Train SVD model for matrix factorization"""        if self.user_item_matrix is None:
            raise ValueError("User-item matrix not built")
        
        # Use TruncatedSVD for sparse matrices
        n_components = min(50, min(self.user_item_matrix.shape) - 1)
        self.svd_model = TruncatedSVD(n_components=n_components, random_state=42)
        self.svd_model.fit(self.user_item_matrix)
        
        self.logger.info(f"SVD model trained with {n_components} components")
    
    async def _calculate_similarity_matrices(self):
        """Calculate user and item similarity matrices"""        # Item-item similarity
        item_features_matrix = self.user_item_matrix.T  # Items x Users
        
        # Use cosine similarity
        self.item_similarity_matrix = cosine_similarity(item_features_matrix)
        
        # User-user similarity (compute only if needed and feasible)
        if self.user_item_matrix.shape[0] < 10000:  # Limit for performance
            self.user_similarity_matrix = cosine_similarity(self.user_item_matrix)
        
        self.logger.info("Similarity matrices calculated")
    
    async def recommend(
        self,
        user_id: str,
        user_profile: Optional[UserProfile] = None,
        exclude_items: Set[str] = None
    ) -> RecommendationResult:
        """Generate collaborative filtering recommendations"""        if not self.is_trained:
            raise ValueError("Model not trained")
        
        exclude_items = exclude_items or set()
        
        try:
            if user_id in self.user_to_idx:
                # Existing user - use collaborative filtering
                recommendations = await self._recommend_for_existing_user(user_id, exclude_items)
                strategy = RecommendationStrategy.COLLABORATIVE_FILTERING
                confidence = 0.8
            else:
                # New user - use popularity-based recommendations
                recommendations = await self._recommend_for_new_user(user_profile, exclude_items)
                strategy = RecommendationStrategy.TRENDING_BASED
                confidence = 0.4
            
            # Apply business rules
            if user_profile:
                recommendations = self._apply_business_rules(recommendations, user_profile)
            
            # Ensure diversity
            if self.config.enable_diversity:
                recommendations = await self._ensure_diversity(recommendations)
            
            # Limit results
            recommendations = recommendations[:self.config.max_recommendations]
            
            return RecommendationResult(
                recommendations=recommendations,
                strategy_used=strategy,
                confidence_score=confidence,
                explanation=f"Based on {strategy.value} with {len(recommendations)} items"
            )
            
        except Exception as e:
            self.logger.error(f"Recommendation generation failed: {e}")
            return RecommendationResult(
                recommendations=[],
                strategy_used=RecommendationStrategy.COLLABORATIVE_FILTERING,
                confidence_score=0.0,
                explanation=f"Error: {str(e)}"
            )
    
    async def _recommend_for_existing_user(
        self,
        user_id: str,
        exclude_items: Set[str]
    ) -> List[Tuple[str, float]]:
        """Generate recommendations for existing user"""        user_idx = self.user_to_idx[user_id]
        
        # Get user's interaction vector
        user_vector = self.user_item_matrix[user_idx].toarray().flatten()
        
        # Use SVD for prediction if available
        if self.svd_model:
            # Transform user vector using SVD
            user_factors = self.svd_model.transform(self.user_item_matrix[user_idx])
            
            # Reconstruct preferences for all items
            all_items_factors = self.svd_model.components_
            predictions = np.dot(user_factors, all_items_factors).flatten()
        else:
            # Fall back to item-item collaborative filtering
            predictions = np.zeros(len(self.item_to_idx))
            
            for item_idx in range(len(self.item_to_idx)):
                if user_vector[item_idx] > 0:  # User has interacted with this item
                    continue
                
                # Find similar items that user has interacted with
                similar_items = self.item_similarity_matrix[item_idx]
                weighted_score = np.dot(similar_items, user_vector) / (np.sum(np.abs(similar_items)) + 1e-8)
                predictions[item_idx] = weighted_score
        
        # Convert to recommendations
        recommendations = []
        for item_idx, score in enumerate(predictions):
            item_id = self.idx_to_item[item_idx]
            
            # Skip if already interacted or excluded
            if user_vector[item_idx] > 0 or item_id in exclude_items:
                continue
            
            if score > self.config.min_score_threshold:
                recommendations.append((item_id, float(score)))
        
        # Sort by score
        recommendations.sort(key=lambda x: x[1], reverse=True)
        
        return recommendations
    
    async def _recommend_for_new_user(
        self,
        user_profile: Optional[UserProfile],
        exclude_items: Set[str]
    ) -> List[Tuple[str, float]]:
        """Generate recommendations for new user (cold start)"""        recommendations = []
        
        # Use popularity-based recommendations
        item_popularity = {}
        
        for item_idx in range(self.user_item_matrix.shape[1]):
            item_id = self.idx_to_item[item_idx]
            if item_id in exclude_items:
                continue
            
            # Calculate popularity score
            item_vector = self.user_item_matrix[:, item_idx].toarray().flatten()
            popularity = np.sum(item_vector)
            
            # Apply recency boost
            item_features = self.item_features.get(item_id, {})
            created_at = item_features.get('created_at', datetime.now())
            if isinstance(created_at, str):
                created_at = datetime.fromisoformat(created_at)
            
            days_old = (datetime.now() - created_at).days
            recency_boost = np.exp(-days_old / 7.0)  # 7-day half-life
            
            final_score = popularity * recency_boost
            recommendations.append((item_id, float(final_score)))
        
        # Sort by score
        recommendations.sort(key=lambda x: x[1], reverse=True)
        
        return recommendations
    
    async def _ensure_diversity(self, recommendations: List[Tuple[str, float]]) -> List[Tuple[str, float]]:
        """Ensure diversity in recommendations using MMR (Maximal Marginal Relevance)"""        if len(recommendations) <= 1:
            return recommendations
        
        diverse_recommendations = []
        remaining = recommendations.copy()
        
        # Add the highest scored item first
        if remaining:
            diverse_recommendations.append(remaining.pop(0))
        
        # Add remaining items considering diversity
        while remaining and len(diverse_recommendations) < self.config.max_recommendations:
            best_mmr_score = -float('inf')
            best_item = None
            best_idx = -1
            
            for idx, (item_id, score) in enumerate(remaining):
                # Calculate MMR score
                relevance = score
                
                # Calculate diversity (1 - max similarity to already selected items)
                max_similarity = 0
                for selected_item_id, _ in diverse_recommendations:
                    similarity = self._calculate_item_similarity(item_id, selected_item_id)
                    max_similarity = max(max_similarity, similarity)
                
                diversity = 1 - max_similarity
                
                # MMR formula
                mmr_score = (1 - self.config.diversity_weight) * relevance + self.config.diversity_weight * diversity
                
                if mmr_score > best_mmr_score:
                    best_mmr_score = mmr_score
                    best_item = (item_id, score)
                    best_idx = idx
            
            if best_item:
                diverse_recommendations.append(best_item)
                remaining.pop(best_idx)
        
        return diverse_recommendations
    
    def _calculate_item_similarity(self, item1_id: str, item2_id: str) -> float:
        """Calculate similarity between two items"""        if item1_id not in self.item_to_idx or item2_id not in self.item_to_idx:
            return 0.0
        
        item1_idx = self.item_to_idx[item1_id]
        item2_idx = self.item_to_idx[item2_id]
        
        if self.item_similarity_matrix is not None:
            return float(self.item_similarity_matrix[item1_idx, item2_idx])
        
        # Fallback to feature-based similarity
        item1_features = self.item_features.get(item1_id, {})
        item2_features = self.item_features.get(item2_id, {})
        
        # Category similarity
        if item1_features.get('category') == item2_features.get('category'):
            return 0.8
        
        # Tag similarity
        tags1 = set(item1_features.get('tags', []))
        tags2 = set(item2_features.get('tags', []))
        
        if tags1 and tags2:
            jaccard_similarity = len(tags1.intersection(tags2)) / len(tags1.union(tags2))
            return jaccard_similarity
        
        return 0.0


class ContentBasedFiltering(RecommendationEngine):
    """Content-based filtering recommendation engine"""    
    def __init__(self, config: RecommendationConfig):
        super().__init__(config)
        self.tfidf_vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        self.content_features_matrix = None
        self.item_to_idx = {}
        self.idx_to_item = {}
        self.knn_model = None
    
    async def fit(self, interactions: List[UserInteraction], items: List[RecommendationItem]):
        """Train content-based filtering model"""        self.logger.info("Training content-based filtering model")
        
        try:
            # Build content features
            await self._build_content_features(items)
            
            # Train similarity model
            await self._train_similarity_model()
            
            # Build user preferences from interactions
            await self._build_user_preferences(interactions)
            
            self.is_trained = True
            self.logger.info("Content-based filtering model trained successfully")
            
        except Exception as e:
            self.logger.error(f"Training failed: {e}")
            raise
    
    async def _build_content_features(self, items: List[RecommendationItem]):
        """Build content feature matrix from items"""        # Create item mappings
        self.item_to_idx = {item.item_id: idx for idx, item in enumerate(items)}
        self.idx_to_item = {idx: item.item_id for item_id, idx in self.item_to_idx.items()}
        
        # Store item features
        for item in items:
            self.item_features[item.item_id] = {
                'title': item.title,
                'category': item.category,
                'tags': item.tags,
                'features': item.features,
                'metrics': item.metrics,
                'creator_id': item.creator_id
            }
        
        # Build text features from title, category, and tags
        text_features = []
        for item in items:
            combined_text = f"{item.title} {item.category} {' '.join(item.tags)}"
            text_features.append(combined_text)
        
        # Create TF-IDF matrix
        if text_features:
            tfidf_matrix = self.tfidf_vectorizer.fit_transform(text_features)
            self.content_features_matrix = tfidf_matrix.toarray()
        else:
            self.content_features_matrix = np.array([])
    
    async def _train_similarity_model(self):
        """Train k-NN model for similarity search"""        if self.content_features_matrix.size > 0:
            self.knn_model = NearestNeighbors(
                n_neighbors=min(20, self.content_features_matrix.shape[0]),
                metric='cosine'
            )
            self.knn_model.fit(self.content_features_matrix)
    
    async def _build_user_preferences(self, interactions: List[UserInteraction]):
        """Build user preference profiles from interactions"""        user_preferences = defaultdict(lambda: defaultdict(float))
        
        # Weight different interaction types
        interaction_weights = {
            InteractionType.VIEW: 1.0,
            InteractionType.LIKE: 3.0,
            InteractionType.SHARE: 5.0,
            InteractionType.COMMENT: 4.0,
            InteractionType.SAVE: 4.0
        }
        
        for interaction in interactions:
            if interaction.item_id in self.item_to_idx:
                user_id = interaction.user_id
                item_features = self.item_features[interaction.item_id]
                weight = interaction_weights.get(interaction.interaction_type, 1.0)
                
                # Update category preferences
                category = item_features['category']
                user_preferences[user_id]['categories'][category] += weight
                
                # Update tag preferences
                for tag in item_features['tags']:
                    user_preferences[user_id]['tags'][tag] += weight
                
                # Update creator preferences
                creator_id = item_features['creator_id']
                user_preferences[user_id]['creators'][creator_id] += weight
        
        # Normalize preferences
        for user_id, prefs in user_preferences.items():
            for pref_type, values in prefs.items():
                total = sum(values.values())
                if total > 0:
                    for key in values:
                        values[key] /= total
        
        # Store in user profiles
        for user_id, prefs in user_preferences.items():
            if user_id not in self.user_profiles:
                self.user_profiles[user_id] = UserProfile(user_id=user_id)
            
            self.user_profiles[user_id].preferences = dict(prefs)
            self.user_profiles[user_id].updated_at = datetime.now()
    
    async def recommend(
        self,
        user_id: str,
        user_profile: Optional[UserProfile] = None,
        exclude_items: Set[str] = None
    ) -> RecommendationResult:
        """Generate content-based recommendations"""        if not self.is_trained:
            raise ValueError("Model not trained")
        
        exclude_items = exclude_items or set()
        
        try:
            # Get user preferences
            if user_profile:
                preferences = user_profile.preferences
            elif user_id in self.user_profiles:
                preferences = self.user_profiles[user_id].preferences
            else:
                # New user - use popular content
                return await self._recommend_popular_content(exclude_items)
            
            # Generate recommendations based on content similarity
            recommendations = await self._generate_content_recommendations(preferences, exclude_items)
            
            # Apply business rules
            if user_profile:
                recommendations = self._apply_business_rules(recommendations, user_profile)
            
            # Ensure diversity
            if self.config.enable_diversity:
                recommendations = await self._ensure_content_diversity(recommendations)
            
            # Limit results
            recommendations = recommendations[:self.config.max_recommendations]
            
            return RecommendationResult(
                recommendations=recommendations,
                strategy_used=RecommendationStrategy.CONTENT_BASED,
                confidence_score=0.7,
                explanation=f"Based on your content preferences with {len(recommendations)} items"
            )
            
        except Exception as e:
            self.logger.error(f"Content-based recommendation failed: {e}")
            return RecommendationResult(
                recommendations=[],
                strategy_used=RecommendationStrategy.CONTENT_BASED,
                confidence_score=0.0,
                explanation=f"Error: {str(e)}"
            )
    
    async def _generate_content_recommendations(
        self,
        preferences: Dict[str, Any],
        exclude_items: Set[str]
    ) -> List[Tuple[str, float]]:
        """Generate recommendations based on content preferences"""        recommendations = []
        
        # Score items based on preference match
        for item_id, features in self.item_features.items():
            if item_id in exclude_items:
                continue
            
            score = 0.0
            
            # Category preference
            category_prefs = preferences.get('categories', {})
            category = features['category']
            category_score = category_prefs.get(category, 0.0)
            score += category_score * 0.4
            
            # Tag preferences
            tag_prefs = preferences.get('tags', {})
            tag_score = sum(tag_prefs.get(tag, 0.0) for tag in features['tags'])
            score += tag_score * 0.4
            
            # Creator preferences
            creator_prefs = preferences.get('creators', {})
            creator_id = features['creator_id']
            creator_score = creator_prefs.get(creator_id, 0.0)
            score += creator_score * 0.2
            
            if score > self.config.min_score_threshold:
                recommendations.append((item_id, float(score)))
        
        # Sort by score
        recommendations.sort(key=lambda x: x[1], reverse=True)
        
        return recommendations
    
    async def _recommend_popular_content(self, exclude_items: Set[str]) -> RecommendationResult:
        """Recommend popular content for new users"""        recommendations = []
        
        # Use simple popularity metrics
        for item_id, features in self.item_features.items():
            if item_id in exclude_items:
                continue
            
            # Use engagement metrics as popularity proxy
            metrics = features.get('metrics', {})
            popularity_score = (
                metrics.get('views', 0) * 0.1 +
                metrics.get('likes', 0) * 0.3 +
                metrics.get('shares', 0) * 0.4 +
                metrics.get('comments', 0) * 0.2
            )
            
            if popularity_score > 0:
                recommendations.append((item_id, popularity_score))
        
        # Normalize scores
        if recommendations:
            max_score = max(score for _, score in recommendations)
            recommendations = [(item_id, score / max_score) 
                             for item_id, score in recommendations]
        
        recommendations.sort(key=lambda x: x[1], reverse=True)
        recommendations = recommendations[:self.config.max_recommendations]
        
        return RecommendationResult(
            recommendations=recommendations,
            strategy_used=RecommendationStrategy.TRENDING_BASED,
            confidence_score=0.5,
            explanation="Popular content recommendations for new users"
        )
    
    async def _ensure_content_diversity(
        self,
        recommendations: List[Tuple[str, float]]
    ) -> List[Tuple[str, float]]:
        """Ensure diversity in content-based recommendations"""        if len(recommendations) <= 1:
            return recommendations
        
        diverse_recommendations = []
        remaining = recommendations.copy()
        
        # Add the highest scored item first
        if remaining:
            diverse_recommendations.append(remaining.pop(0))
        
        # Add remaining items considering content diversity
        while remaining and len(diverse_recommendations) < self.config.max_recommendations:
            best_diversity_score = -float('inf')
            best_item = None
            best_idx = -1
            
            for idx, (item_id, relevance_score) in enumerate(remaining):
                # Calculate content diversity
                min_similarity = float('inf')
                
                for selected_item_id, _ in diverse_recommendations:
                    similarity = self._calculate_content_similarity(item_id, selected_item_id)
                    min_similarity = min(min_similarity, similarity)
                
                diversity = 1 - min_similarity if min_similarity != float('inf') else 1.0
                
                # Combine relevance and diversity
                diversity_score = (1 - self.config.diversity_weight) * relevance_score + \
                                self.config.diversity_weight * diversity
                
                if diversity_score > best_diversity_score:
                    best_diversity_score = diversity_score
                    best_item = (item_id, relevance_score)
                    best_idx = idx
            
            if best_item:
                diverse_recommendations.append(best_item)
                remaining.pop(best_idx)
        
        return diverse_recommendations
    
    def _calculate_content_similarity(self, item1_id: str, item2_id: str) -> float:
        """Calculate content similarity between two items"""        if (item1_id not in self.item_to_idx or 
            item2_id not in self.item_to_idx or 
            self.content_features_matrix.size == 0):
            return 0.0
        
        item1_idx = self.item_to_idx[item1_id]
        item2_idx = self.item_to_idx[item2_id]
        
        # Calculate cosine similarity between content features
        features1 = self.content_features_matrix[item1_idx]
        features2 = self.content_features_matrix[item2_idx]
        
        similarity = cosine_similarity([features1], [features2])[0][0]
        return float(similarity)


class HybridRecommendationEngine(RecommendationEngine):
    """Hybrid recommendation engine combining multiple strategies"""    
    def __init__(self, config: RecommendationConfig):
        super().__init__(config)
        self.collaborative_engine = CollaborativeFiltering(config)
        self.content_engine = ContentBasedFiltering(config)
        self.weights = {
            'collaborative': 0.5,
            'content': 0.3,
            'trending': 0.2
        }
    
    async def fit(self, interactions: List[UserInteraction], items: List[RecommendationItem]):
        """Train all sub-engines"""        self.logger.info("Training hybrid recommendation engine")
        
        try:
            # Train collaborative filtering
            await self.collaborative_engine.fit(interactions, items)
            
            # Train content-based filtering
            await self.content_engine.fit(interactions, items)
            
            # Combine item features
            self.item_features.update(self.collaborative_engine.item_features)
            self.item_features.update(self.content_engine.item_features)
            
            self.is_trained = True
            self.logger.info("Hybrid recommendation engine trained successfully")
            
        except Exception as e:
            self.logger.error(f"Hybrid training failed: {e}")
            raise
    
    async def recommend(
        self,
        user_id: str,
        user_profile: Optional[UserProfile] = None,
        exclude_items: Set[str] = None
    ) -> RecommendationResult:
        """Generate hybrid recommendations"""        if not self.is_trained:
            raise ValueError("Model not trained")
        
        try:
            # Get recommendations from each engine
            collaborative_result = await self.collaborative_engine.recommend(
                user_id, user_profile, exclude_items
            )
            
            content_result = await self.content_engine.recommend(
                user_id, user_profile, exclude_items
            )
            
            # Combine recommendations with weighted scores
            combined_scores = defaultdict(float)
            
            # Add collaborative filtering scores
            for item_id, score in collaborative_result.recommendations:
                combined_scores[item_id] += score * self.weights['collaborative']
            
            # Add content-based scores
            for item_id, score in content_result.recommendations:
                combined_scores[item_id] += score * self.weights['content']
            
            # Add trending boost for recent popular items
            trending_boost = await self._calculate_trending_boost(exclude_items or set())
            for item_id, boost in trending_boost.items():
                combined_scores[item_id] += boost * self.weights['trending']
            
            # Convert to recommendations list
            recommendations = [(item_id, score) for item_id, score in combined_scores.items()
                             if score > self.config.min_score_threshold]
            
            # Sort by combined score
            recommendations.sort(key=lambda x: x[1], reverse=True)
            
            # Apply business rules
            if user_profile:
                recommendations = self._apply_business_rules(recommendations, user_profile)
            
            # Ensure diversity
            if self.config.enable_diversity:
                recommendations = await self._ensure_hybrid_diversity(recommendations)
            
            # Limit results
            recommendations = recommendations[:self.config.max_recommendations]
            
            # Calculate confidence based on available data
            confidence = min(
                collaborative_result.confidence_score * self.weights['collaborative'] +
                content_result.confidence_score * self.weights['content'] +
                0.6 * self.weights['trending'],  # Base trending confidence
                1.0
            )
            
            return RecommendationResult(
                recommendations=recommendations,
                strategy_used=RecommendationStrategy.HYBRID,
                confidence_score=confidence,
                explanation=f"Hybrid recommendations combining collaborative filtering, "
                          f"content analysis, and trending data with {len(recommendations)} items"
            )
            
        except Exception as e:
            self.logger.error(f"Hybrid recommendation failed: {e}")
            return RecommendationResult(
                recommendations=[],
                strategy_used=RecommendationStrategy.HYBRID,
                confidence_score=0.0,
                explanation=f"Error: {str(e)}"
            )
    
    async def _calculate_trending_boost(self, exclude_items: Set[str]) -> Dict[str, float]:
        """Calculate trending boost for items based on recent activity"""        trending_scores = {}
        
        # Simple trending calculation based on recent metrics
        current_time = datetime.now()
        
        for item_id, features in self.item_features.items():
            if item_id in exclude_items:
                continue
            
            metrics = features.get('metrics', {})
            
            # Calculate recency factor
            created_at = features.get('created_at', current_time)
            if isinstance(created_at, str):
                created_at = datetime.fromisoformat(created_at)
            
            hours_old = (current_time - created_at).total_seconds() / 3600
            recency_factor = np.exp(-hours_old / 24.0)  # 24-hour half-life
            
            # Calculate engagement velocity (simplified)
            engagement_score = (
                metrics.get('views', 0) * 0.1 +
                metrics.get('likes', 0) * 0.3 +
                metrics.get('shares', 0) * 0.4 +
                metrics.get('comments', 0) * 0.2
            )
            
            # Trending score
            trending_score = engagement_score * recency_factor
            
            if trending_score > 0:
                trending_scores[item_id] = trending_score
        
        # Normalize trending scores
        if trending_scores:
            max_score = max(trending_scores.values())
            trending_scores = {item_id: score / max_score 
                             for item_id, score in trending_scores.items()}
        
        return trending_scores
    
    async def _ensure_hybrid_diversity(
        self,
        recommendations: List[Tuple[str, float]]
    ) -> List[Tuple[str, float]]:
        """Ensure diversity in hybrid recommendations"""        # Use the content-based engine's diversity method as it's more sophisticated
        return await self.content_engine._ensure_content_diversity(recommendations)
    
    def update_weights(self, new_weights: Dict[str, float]):
        """Update the weights for different recommendation strategies"""        total_weight = sum(new_weights.values())
        if abs(total_weight - 1.0) > 0.01:
            # Normalize weights
            new_weights = {k: v / total_weight for k, v in new_weights.items()}
        
        self.weights.update(new_weights)
        self.logger.info(f"Updated hybrid weights: {self.weights}")


# Export main classes
__all__ = [
    'RecommendationEngine',
    'CollaborativeFiltering',
    'ContentBasedFiltering',
    'HybridRecommendationEngine',
    'UserInteraction',
    'RecommendationItem',
    'UserProfile',
    'RecommendationResult',
    'RecommendationConfig',
    'RecommendationType',
    'RecommendationStrategy',
    'InteractionType'
]
