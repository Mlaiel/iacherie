"""
Ainflue Core AI - Recommendation Engine Core
============================================

Enterprise-grade recommendation system with collaborative filtering, content-based
filtering, hybrid approaches, and real-time personalization. Provides intelligent
content and creator recommendations for the Ainflue platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import numpy as np
import time
from typing import Dict, List, Optional, Any, Union, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import json
import hashlib

# Third-party imports (with fallbacks)
try:
    from sklearn.metrics.pairwise import cosine_similarity
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.decomposition import NMF
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

logger = logging.getLogger(__name__)

class RecommendationType(str, Enum):
    """Types of recommendations"""
    CONTENT = "content"
    CREATOR = "creator"
    COLLABORATION = "collaboration"
    TREND = "trend"
    SIMILAR_USER = "similar_user"
    CROSS_PLATFORM = "cross_platform"

class RecommendationAlgorithm(str, Enum):
    """Recommendation algorithms"""
    COLLABORATIVE_FILTERING = "collaborative_filtering"
    CONTENT_BASED = "content_based"
    HYBRID = "hybrid"
    MATRIX_FACTORIZATION = "matrix_factorization"
    DEEP_LEARNING = "deep_learning"
    KNOWLEDGE_BASED = "knowledge_based"

class InteractionType(str, Enum):
    """User interaction types"""
    VIEW = "view"
    LIKE = "like"
    SHARE = "share"
    COMMENT = "comment"
    FOLLOW = "follow"
    COLLABORATE = "collaborate"
    PURCHASE = "purchase"
    DOWNLOAD = "download"

@dataclass
class UserInteraction:
    """User interaction data"""
    user_id: str
    item_id: str
    interaction_type: InteractionType
    rating: float = 0.0
    timestamp: datetime = field(default_factory=datetime.utcnow)
    context: Dict[str, Any] = field(default_factory=dict)
    duration: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ContentItem:
    """Content item for recommendations"""
    item_id: str
    title: str
    description: str
    creator_id: str
    content_type: str
    tags: List[str] = field(default_factory=list)
    categories: List[str] = field(default_factory=list)
    features: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    popularity_score: float = 0.0
    quality_score: float = 0.0

@dataclass
class UserProfile:
    """User profile for personalization"""
    user_id: str
    preferences: Dict[str, float] = field(default_factory=dict)
    interests: List[str] = field(default_factory=list)
    demographic: Dict[str, Any] = field(default_factory=dict)
    behavior_patterns: Dict[str, Any] = field(default_factory=dict)
    interaction_history: List[UserInteraction] = field(default_factory=list)
    last_active: datetime = field(default_factory=datetime.utcnow)

@dataclass
class Recommendation:
    """Recommendation result"""
    item_id: str
    user_id: str
    score: float
    algorithm: RecommendationAlgorithm
    recommendation_type: RecommendationType
    explanation: str = ""
    confidence: float = 0.0
    context: Dict[str, Any] = field(default_factory=dict)
    generated_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class RecommendationMetrics:
    """Recommendation system metrics"""
    total_recommendations: int = 0
    successful_recommendations: int = 0
    clicked_recommendations: int = 0
    conversion_rate: float = 0.0
    precision_at_k: Dict[int, float] = field(default_factory=dict)
    recall_at_k: Dict[int, float] = field(default_factory=dict)
    diversity_score: float = 0.0
    novelty_score: float = 0.0
    coverage: float = 0.0
    avg_response_time: float = 0.0

class RecommendationEngineCore:
    """Enterprise recommendation engine system"""
    
    def __init__(self, level: str = "enterprise"):
        """Initialize recommendation engine core"""
        self.level = level
        self.user_profiles: Dict[str, UserProfile] = {}
        self.content_items: Dict[str, ContentItem] = {}
        self.interactions: List[UserInteraction] = []
        self.metrics = RecommendationMetrics()
        
        # Algorithm configurations
        self.algorithms = {
            RecommendationAlgorithm.COLLABORATIVE_FILTERING: self._collaborative_filtering,
            RecommendationAlgorithm.CONTENT_BASED: self._content_based_filtering,
            RecommendationAlgorithm.HYBRID: self._hybrid_filtering,
            RecommendationAlgorithm.MATRIX_FACTORIZATION: self._matrix_factorization,
            RecommendationAlgorithm.KNOWLEDGE_BASED: self._knowledge_based_filtering
        }
        
        # Similarity matrices (cached)
        self._user_similarity_matrix: Optional[np.ndarray] = None
        self._item_similarity_matrix: Optional[np.ndarray] = None
        self._content_features_matrix: Optional[np.ndarray] = None
        
        # Caching
        self._recommendation_cache: Dict[str, List[Recommendation]] = {}
        self._cache_ttl = 3600  # 1 hour
        self._last_model_update = time.time()
        
        # Real-time learning
        self.online_learning_enabled = level == "enterprise"
        self.learning_rate = 0.01
        
        # Configuration
        self.config = {
            "max_recommendations": 50,
            "min_interactions_for_cf": 5,
            "similarity_threshold": 0.1,
            "diversity_lambda": 0.1,
            "novelty_decay": 0.9,
            "recency_weight": 0.8,
            "popularity_weight": 0.2
        }
        
        logger.info(f"🎯 Recommendation Engine Core initialized - Level: {level}")

    async def add_user_interaction(self, interaction: UserInteraction):
        """Add user interaction for learning"""
        
        # Store interaction
        self.interactions.append(interaction)
        
        # Update user profile
        await self._update_user_profile(interaction)
        
        # Update item popularity
        await self._update_item_popularity(interaction)
        
        # Invalidate cache for user
        cache_key = f"user_{interaction.user_id}"
        self._recommendation_cache.pop(cache_key, None)
        
        # Online learning update
        if self.online_learning_enabled:
            await self._online_learning_update(interaction)
        
        logger.debug(f"Added interaction: {interaction.user_id} -> {interaction.item_id}")

    async def _update_user_profile(self, interaction: UserInteraction):
        """Update user profile based on interaction"""
        
        user_id = interaction.user_id
        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = UserProfile(user_id=user_id)
        
        profile = self.user_profiles[user_id]
        profile.interaction_history.append(interaction)
        profile.last_active = interaction.timestamp
        
        # Update preferences based on interaction type
        weight_map = {
            InteractionType.VIEW: 1.0,
            InteractionType.LIKE: 2.0,
            InteractionType.SHARE: 3.0,
            InteractionType.COMMENT: 3.0,
            InteractionType.FOLLOW: 4.0,
            InteractionType.COLLABORATE: 5.0,
            InteractionType.PURCHASE: 5.0
        }
        
        weight = weight_map.get(interaction.interaction_type, 1.0)
        
        # Update content type preferences
        if interaction.item_id in self.content_items:
            content = self.content_items[interaction.item_id]
            
            # Content type preference
            content_type = content.content_type
            current_pref = profile.preferences.get(content_type, 0.0)
            profile.preferences[content_type] = current_pref + (weight * self.learning_rate)
            
            # Category preferences
            for category in content.categories:
                cat_key = f"category_{category}"
                current_pref = profile.preferences.get(cat_key, 0.0)
                profile.preferences[cat_key] = current_pref + (weight * self.learning_rate)
            
            # Tag interests
            for tag in content.tags:
                if tag not in profile.interests:
                    profile.interests.append(tag)

    async def _update_item_popularity(self, interaction: UserInteraction):
        """Update item popularity score"""
        
        if interaction.item_id in self.content_items:
            item = self.content_items[interaction.item_id]
            
            # Popularity boost based on interaction type
            boost_map = {
                InteractionType.VIEW: 0.1,
                InteractionType.LIKE: 0.3,
                InteractionType.SHARE: 0.5,
                InteractionType.COMMENT: 0.4,
                InteractionType.FOLLOW: 0.2,
                InteractionType.COLLABORATE: 0.7,
                InteractionType.PURCHASE: 1.0
            }
            
            boost = boost_map.get(interaction.interaction_type, 0.1)
            item.popularity_score += boost
            
            # Apply time decay
            time_diff = (datetime.utcnow() - item.created_at).days
            decay_factor = self.config["novelty_decay"] ** time_diff
            item.popularity_score *= decay_factor

    async def _online_learning_update(self, interaction: UserInteraction):
        """Perform online learning update"""
        
        # This is a simplified online learning approach
        # In a production system, you'd use more sophisticated algorithms
        
        try:
            # Update similarity matrices if needed
            if time.time() - self._last_model_update > 3600:  # Update every hour
                await self._rebuild_similarity_matrices()
                self._last_model_update = time.time()
                
        except Exception as e:
            logger.error(f"Online learning update failed: {str(e)}")

    async def get_recommendations(
        self,
        user_id: str,
        recommendation_type: RecommendationType = RecommendationType.CONTENT,
        algorithm: RecommendationAlgorithm = RecommendationAlgorithm.HYBRID,
        count: int = 10,
        context: Optional[Dict[str, Any]] = None
    ) -> List[Recommendation]:
        """Get recommendations for user"""
        
        start_time = time.time()
        
        # Check cache
        cache_key = f"{user_id}_{recommendation_type.value}_{algorithm.value}_{count}"
        if cache_key in self._recommendation_cache:
            cached_recs = self._recommendation_cache[cache_key]
            # Check if cache is still valid
            if cached_recs and (time.time() - cached_recs[0].generated_at.timestamp()) < self._cache_ttl:
                return cached_recs[:count]
        
        try:
            # Get user profile
            if user_id not in self.user_profiles:
                # Create basic profile for new user
                self.user_profiles[user_id] = UserProfile(user_id=user_id)
            
            profile = self.user_profiles[user_id]
            
            # Generate recommendations using specified algorithm
            algorithm_func = self.algorithms.get(algorithm)
            if not algorithm_func:
                logger.warning(f"Algorithm {algorithm.value} not available")
                algorithm_func = self.algorithms[RecommendationAlgorithm.CONTENT_BASED]
            
            recommendations = await algorithm_func(
                user_id, recommendation_type, count * 2, context or {}
            )
            
            # Post-process recommendations
            recommendations = await self._post_process_recommendations(
                recommendations, user_id, count, context or {}
            )
            
            # Cache results
            self._recommendation_cache[cache_key] = recommendations
            
            # Update metrics
            self.metrics.total_recommendations += len(recommendations)
            self.metrics.avg_response_time = (
                self.metrics.avg_response_time * 0.9 + (time.time() - start_time) * 0.1
            )
            
            return recommendations[:count]
            
        except Exception as e:
            logger.error(f"Failed to generate recommendations: {str(e)}")
            return []

    async def _collaborative_filtering(
        self, 
        user_id: str, 
        rec_type: RecommendationType, 
        count: int, 
        context: Dict[str, Any]
    ) -> List[Recommendation]:
        """Collaborative filtering recommendations"""
        
        recommendations = []
        
        try:
            # Build user-item interaction matrix
            if not SKLEARN_AVAILABLE:
                logger.warning("Scikit-learn not available for collaborative filtering")
                return []
            
            # Get similar users
            similar_users = await self._find_similar_users(user_id)
            
            if not similar_users:
                logger.warning(f"No similar users found for {user_id}")
                return []
            
            # Get items liked by similar users
            candidate_items = set()
            user_interactions = {i.item_id for i in self.user_profiles[user_id].interaction_history}
            
            for similar_user_id, similarity_score in similar_users[:10]:
                if similar_user_id in self.user_profiles:
                    similar_user_profile = self.user_profiles[similar_user_id]
                    for interaction in similar_user_profile.interaction_history:
                        if (interaction.item_id not in user_interactions and 
                            interaction.interaction_type in [InteractionType.LIKE, InteractionType.SHARE]):
                            candidate_items.add(interaction.item_id)
            
            # Score candidate items
            for item_id in candidate_items:
                score = await self._calculate_cf_score(user_id, item_id, similar_users)
                
                if score > 0:
                    recommendation = Recommendation(
                        item_id=item_id,
                        user_id=user_id,
                        score=score,
                        algorithm=RecommendationAlgorithm.COLLABORATIVE_FILTERING,
                        recommendation_type=rec_type,
                        explanation=f"Users with similar taste also liked this",
                        confidence=min(score, 1.0)
                    )
                    recommendations.append(recommendation)
            
            # Sort by score
            recommendations.sort(key=lambda x: x.score, reverse=True)
            
        except Exception as e:
            logger.error(f"Collaborative filtering failed: {str(e)}")
        
        return recommendations

    async def _content_based_filtering(
        self, 
        user_id: str, 
        rec_type: RecommendationType, 
        count: int, 
        context: Dict[str, Any]
    ) -> List[Recommendation]:
        """Content-based filtering recommendations"""
        
        recommendations = []
        
        try:
            profile = self.user_profiles[user_id]
            
            # Get user preferences
            user_preferences = profile.preferences
            user_interests = set(profile.interests)
            
            # Score all available items
            user_interactions = {i.item_id for i in profile.interaction_history}
            
            for item_id, content in self.content_items.items():
                if item_id in user_interactions:
                    continue  # Skip already interacted items
                
                score = await self._calculate_content_score(content, user_preferences, user_interests)
                
                if score > 0:
                    recommendation = Recommendation(
                        item_id=item_id,
                        user_id=user_id,
                        score=score,
                        algorithm=RecommendationAlgorithm.CONTENT_BASED,
                        recommendation_type=rec_type,
                        explanation=f"Based on your interest in {content.content_type}",
                        confidence=min(score, 1.0)
                    )
                    recommendations.append(recommendation)
            
            # Sort by score
            recommendations.sort(key=lambda x: x.score, reverse=True)
            
        except Exception as e:
            logger.error(f"Content-based filtering failed: {str(e)}")
        
        return recommendations

    async def _hybrid_filtering(
        self, 
        user_id: str, 
        rec_type: RecommendationType, 
        count: int, 
        context: Dict[str, Any]
    ) -> List[Recommendation]:
        """Hybrid recommendation approach"""
        
        try:
            # Get recommendations from different algorithms
            cf_recs = await self._collaborative_filtering(user_id, rec_type, count, context)
            cb_recs = await self._content_based_filtering(user_id, rec_type, count, context)
            
            # Combine recommendations with weighted scores
            cf_weight = 0.6
            cb_weight = 0.4
            
            # If user has few interactions, favor content-based
            profile = self.user_profiles[user_id]
            if len(profile.interaction_history) < self.config["min_interactions_for_cf"]:
                cf_weight = 0.3
                cb_weight = 0.7
            
            # Merge recommendations
            item_scores = {}
            
            for rec in cf_recs:
                item_scores[rec.item_id] = item_scores.get(rec.item_id, 0) + (rec.score * cf_weight)
            
            for rec in cb_recs:
                item_scores[rec.item_id] = item_scores.get(rec.item_id, 0) + (rec.score * cb_weight)
            
            # Create hybrid recommendations
            recommendations = []
            for item_id, score in item_scores.items():
                recommendation = Recommendation(
                    item_id=item_id,
                    user_id=user_id,
                    score=score,
                    algorithm=RecommendationAlgorithm.HYBRID,
                    recommendation_type=rec_type,
                    explanation="Based on similar users and your preferences",
                    confidence=min(score, 1.0)
                )
                recommendations.append(recommendation)
            
            # Sort by score
            recommendations.sort(key=lambda x: x.score, reverse=True)
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Hybrid filtering failed: {str(e)}")
            return []

    async def _matrix_factorization(
        self, 
        user_id: str, 
        rec_type: RecommendationType, 
        count: int, 
        context: Dict[str, Any]
    ) -> List[Recommendation]:
        """Matrix factorization recommendations"""
        
        if not SKLEARN_AVAILABLE:
            logger.warning("Scikit-learn not available for matrix factorization")
            return await self._content_based_filtering(user_id, rec_type, count, context)
        
        try:
            # Build user-item matrix
            user_item_matrix, user_mapping, item_mapping = await self._build_user_item_matrix()
            
            if user_item_matrix.shape[0] < 2 or user_item_matrix.shape[1] < 2:
                return await self._content_based_filtering(user_id, rec_type, count, context)
            
            # Apply NMF
            n_factors = min(10, min(user_item_matrix.shape) - 1)
            nmf = NMF(n_components=n_factors, random_state=42)
            user_factors = nmf.fit_transform(user_item_matrix)
            item_factors = nmf.components_
            
            # Get user index
            if user_id not in user_mapping:
                return await self._content_based_filtering(user_id, rec_type, count, context)
            
            user_idx = user_mapping[user_id]
            user_vector = user_factors[user_idx]
            
            # Calculate scores for all items
            item_scores = np.dot(user_vector, item_factors)
            
            # Get recommendations
            recommendations = []
            reverse_item_mapping = {v: k for k, v in item_mapping.items()}
            
            # Get user's interacted items
            user_interactions = {i.item_id for i in self.user_profiles[user_id].interaction_history}
            
            sorted_indices = np.argsort(item_scores)[::-1]
            
            for idx in sorted_indices:
                item_id = reverse_item_mapping.get(idx)
                if item_id and item_id not in user_interactions:
                    score = float(item_scores[idx])
                    
                    if score > 0:
                        recommendation = Recommendation(
                            item_id=item_id,
                            user_id=user_id,
                            score=score,
                            algorithm=RecommendationAlgorithm.MATRIX_FACTORIZATION,
                            recommendation_type=rec_type,
                            explanation="Based on latent factor analysis",
                            confidence=min(score, 1.0)
                        )
                        recommendations.append(recommendation)
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Matrix factorization failed: {str(e)}")
            return await self._content_based_filtering(user_id, rec_type, count, context)

    async def _knowledge_based_filtering(
        self, 
        user_id: str, 
        rec_type: RecommendationType, 
        count: int, 
        context: Dict[str, Any]
    ) -> List[Recommendation]:
        """Knowledge-based filtering recommendations"""
        
        recommendations = []
        
        try:
            profile = self.user_profiles[user_id]
            
            # Rule-based recommendations
            user_interactions = {i.item_id for i in profile.interaction_history}
            
            for item_id, content in self.content_items.items():
                if item_id in user_interactions:
                    continue
                
                score = 0.0
                explanations = []
                
                # Trending content
                if content.popularity_score > 10:
                    score += 0.3
                    explanations.append("trending")
                
                # High quality content
                if content.quality_score > 0.8:
                    score += 0.2
                    explanations.append("high quality")
                
                # Recent content
                days_old = (datetime.utcnow() - content.created_at).days
                if days_old < 7:
                    score += 0.2
                    explanations.append("recent")
                
                # Category matching
                for category in content.categories:
                    if category in profile.interests:
                        score += 0.1
                        explanations.append(f"matches {category}")
                
                if score > 0:
                    explanation = f"Recommended because it's {', '.join(explanations)}"
                    
                    recommendation = Recommendation(
                        item_id=item_id,
                        user_id=user_id,
                        score=score,
                        algorithm=RecommendationAlgorithm.KNOWLEDGE_BASED,
                        recommendation_type=rec_type,
                        explanation=explanation,
                        confidence=min(score, 1.0)
                    )
                    recommendations.append(recommendation)
            
            # Sort by score
            recommendations.sort(key=lambda x: x.score, reverse=True)
            
        except Exception as e:
            logger.error(f"Knowledge-based filtering failed: {str(e)}")
        
        return recommendations

    async def _find_similar_users(self, user_id: str, top_k: int = 10) -> List[Tuple[str, float]]:
        """Find users similar to the given user"""
        
        if not SKLEARN_AVAILABLE:
            return []
        
        try:
            target_profile = self.user_profiles[user_id]
            target_preferences = target_profile.preferences
            
            similarities = []
            
            for other_user_id, other_profile in self.user_profiles.items():
                if other_user_id == user_id:
                    continue
                
                # Calculate similarity based on preferences
                similarity = self._calculate_user_similarity(target_preferences, other_profile.preferences)
                
                if similarity > self.config["similarity_threshold"]:
                    similarities.append((other_user_id, similarity))
            
            # Sort by similarity
            similarities.sort(key=lambda x: x[1], reverse=True)
            
            return similarities[:top_k]
            
        except Exception as e:
            logger.error(f"Finding similar users failed: {str(e)}")
            return []

    def _calculate_user_similarity(self, prefs1: Dict[str, float], prefs2: Dict[str, float]) -> float:
        """Calculate similarity between two user preference vectors"""
        
        # Get common keys
        common_keys = set(prefs1.keys()) & set(prefs2.keys())
        
        if not common_keys:
            return 0.0
        
        # Calculate cosine similarity
        vec1 = [prefs1[key] for key in common_keys]
        vec2 = [prefs2[key] for key in common_keys]
        
        # Normalize vectors
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return np.dot(vec1, vec2) / (norm1 * norm2)

    async def _calculate_cf_score(
        self, 
        user_id: str, 
        item_id: str, 
        similar_users: List[Tuple[str, float]]
    ) -> float:
        """Calculate collaborative filtering score for an item"""
        
        score = 0.0
        total_weight = 0.0
        
        for similar_user_id, similarity in similar_users:
            if similar_user_id in self.user_profiles:
                similar_profile = self.user_profiles[similar_user_id]
                
                # Check if similar user interacted with the item
                for interaction in similar_profile.interaction_history:
                    if interaction.item_id == item_id:
                        # Weight by interaction type and similarity
                        interaction_weight = {
                            InteractionType.VIEW: 1.0,
                            InteractionType.LIKE: 2.0,
                            InteractionType.SHARE: 3.0,
                            InteractionType.COMMENT: 2.5,
                            InteractionType.FOLLOW: 1.5,
                            InteractionType.COLLABORATE: 4.0,
                            InteractionType.PURCHASE: 5.0
                        }.get(interaction.interaction_type, 1.0)
                        
                        weight = similarity * interaction_weight
                        score += weight * (interaction.rating if interaction.rating > 0 else 1.0)
                        total_weight += weight
                        break
        
        return score / total_weight if total_weight > 0 else 0.0

    async def _calculate_content_score(
        self, 
        content: ContentItem, 
        user_preferences: Dict[str, float], 
        user_interests: Set[str]
    ) -> float:
        """Calculate content-based score for an item"""
        
        score = 0.0
        
        # Content type preference
        content_type_pref = user_preferences.get(content.content_type, 0.0)
        score += content_type_pref * 0.4
        
        # Category preferences
        for category in content.categories:
            cat_key = f"category_{category}"
            category_pref = user_preferences.get(cat_key, 0.0)
            score += category_pref * 0.3
        
        # Tag interests
        matching_tags = len(set(content.tags) & user_interests)
        if content.tags:
            tag_score = matching_tags / len(content.tags)
            score += tag_score * 0.2
        
        # Quality and popularity boost
        score += content.quality_score * 0.1
        score += min(content.popularity_score / 100, 1.0) * 0.1
        
        return score

    async def _build_user_item_matrix(self) -> Tuple[np.ndarray, Dict[str, int], Dict[str, int]]:
        """Build user-item interaction matrix"""
        
        # Create mappings
        users = list(self.user_profiles.keys())
        items = list(self.content_items.keys())
        
        user_mapping = {user_id: idx for idx, user_id in enumerate(users)}
        item_mapping = {item_id: idx for idx, item_id in enumerate(items)}
        
        # Create matrix
        matrix = np.zeros((len(users), len(items)))
        
        for interaction in self.interactions:
            if interaction.user_id in user_mapping and interaction.item_id in item_mapping:
                user_idx = user_mapping[interaction.user_id]
                item_idx = item_mapping[interaction.item_id]
                
                # Weight by interaction type
                weight = {
                    InteractionType.VIEW: 1.0,
                    InteractionType.LIKE: 3.0,
                    InteractionType.SHARE: 4.0,
                    InteractionType.COMMENT: 3.0,
                    InteractionType.FOLLOW: 2.0,
                    InteractionType.COLLABORATE: 5.0,
                    InteractionType.PURCHASE: 5.0
                }.get(interaction.interaction_type, 1.0)
                
                matrix[user_idx, item_idx] += weight
        
        return matrix, user_mapping, item_mapping

    async def _post_process_recommendations(
        self, 
        recommendations: List[Recommendation], 
        user_id: str, 
        count: int, 
        context: Dict[str, Any]
    ) -> List[Recommendation]:
        """Post-process recommendations for diversity and quality"""
        
        if not recommendations:
            return []
        
        # Apply diversity
        diverse_recs = await self._apply_diversity(recommendations, user_id)
        
        # Apply business rules
        filtered_recs = await self._apply_business_rules(diverse_recs, user_id, context)
        
        return filtered_recs[:count]

    async def _apply_diversity(self, recommendations: List[Recommendation], user_id: str) -> List[Recommendation]:
        """Apply diversity to recommendations"""
        
        if not recommendations:
            return recommendations
        
        diverse_recs = []
        selected_categories = set()
        selected_creators = set()
        
        # Sort by score first
        recommendations.sort(key=lambda x: x.score, reverse=True)
        
        for rec in recommendations:
            if rec.item_id in self.content_items:
                content = self.content_items[rec.item_id]
                
                # Check diversity constraints
                category_diversity = len(set(content.categories) & selected_categories) == 0
                creator_diversity = content.creator_id not in selected_creators
                
                if category_diversity or creator_diversity or len(diverse_recs) < 3:
                    diverse_recs.append(rec)
                    selected_categories.update(content.categories)
                    selected_creators.add(content.creator_id)
                    
                    if len(diverse_recs) >= len(recommendations) * 0.8:
                        break
        
        # Fill remaining slots with highest scored items
        remaining_count = min(len(recommendations), 50) - len(diverse_recs)
        if remaining_count > 0:
            for rec in recommendations:
                if rec not in diverse_recs:
                    diverse_recs.append(rec)
                    remaining_count -= 1
                    if remaining_count == 0:
                        break
        
        return diverse_recs

    async def _apply_business_rules(
        self, 
        recommendations: List[Recommendation], 
        user_id: str, 
        context: Dict[str, Any]
    ) -> List[Recommendation]:
        """Apply business rules to filter recommendations"""
        
        filtered_recs = []
        
        for rec in recommendations:
            if rec.item_id in self.content_items:
                content = self.content_items[rec.item_id]
                
                # Quality threshold
                if content.quality_score < 0.3:
                    continue
                
                # Recency filter (don't recommend very old content unless it's highly rated)
                days_old = (datetime.utcnow() - content.created_at).days
                if days_old > 90 and content.popularity_score < 5:
                    continue
                
                filtered_recs.append(rec)
        
        return filtered_recs

    async def add_content_item(self, content: ContentItem):
        """Add content item to the system"""
        self.content_items[content.item_id] = content
        logger.debug(f"Added content item: {content.item_id}")

    async def record_recommendation_feedback(
        self, 
        user_id: str, 
        item_id: str, 
        feedback: str,
        context: Optional[Dict[str, Any]] = None
    ):
        """Record feedback on recommendations"""
        
        if feedback == "clicked":
            self.metrics.clicked_recommendations += 1
            
            # Create implicit positive interaction
            interaction = UserInteraction(
                user_id=user_id,
                item_id=item_id,
                interaction_type=InteractionType.VIEW,
                rating=1.0,
                context=context or {}
            )
            await self.add_user_interaction(interaction)
        
        # Update conversion rate
        if self.metrics.total_recommendations > 0:
            self.metrics.conversion_rate = (
                self.metrics.clicked_recommendations / self.metrics.total_recommendations
            )

    async def _rebuild_similarity_matrices(self):
        """Rebuild similarity matrices for collaborative filtering"""
        
        if not SKLEARN_AVAILABLE:
            return
        
        try:
            # Build user-item matrix
            user_item_matrix, _, _ = await self._build_user_item_matrix()
            
            if user_item_matrix.shape[0] > 1:
                # User similarity matrix
                self._user_similarity_matrix = cosine_similarity(user_item_matrix)
            
            if user_item_matrix.shape[1] > 1:
                # Item similarity matrix
                self._item_similarity_matrix = cosine_similarity(user_item_matrix.T)
            
            logger.info("✅ Similarity matrices rebuilt")
            
        except Exception as e:
            logger.error(f"Failed to rebuild similarity matrices: {str(e)}")

    def get_metrics(self) -> RecommendationMetrics:
        """Get recommendation system metrics"""
        return self.metrics

    async def health_check(self) -> bool:
        """Health check for recommendation system"""
        try:
            # Test basic recommendation generation
            if self.user_profiles:
                user_id = list(self.user_profiles.keys())[0]
                recommendations = await self.get_recommendations(user_id, count=5)
                return True
            
            return True  # No users yet, but system is healthy
            
        except Exception as e:
            logger.error(f"Recommendation engine health check failed: {str(e)}")
            return False

# Module exports
__all__ = [
    "RecommendationEngineCore", "RecommendationType", "RecommendationAlgorithm",
    "InteractionType", "UserInteraction", "ContentItem", "UserProfile",
    "Recommendation", "RecommendationMetrics"
]

logger.info("🎯 Recommendation Engine Core module loaded")