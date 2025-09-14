"""
Creator Recommendation Service module
Enterprise implementation for Ainflue platform
"""

#!/usr/bin/env python3
"""
Enterprise Creator Recommendation Service
AI-powered creator recommendation engine for microservices architecture

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ STRICT COPYRIGHT WARNING ⚠️
This implementation is proprietary and confidential. Unauthorized use, reproduction,
distribution, or modification without written permission from Fahed Mlaiel
(mlaiel@live.de) is strictly prohibited and will be prosecuted to the full extent
of the law. All rights reserved.
"""

import asyncio
import time
import logging
import numpy as np
from typing import Dict, Any, Optional, List, Callable, Awaitable, Set, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import threading
from datetime import datetime, timedelta
import json
from collections import defaultdict
import math
import random

logger = logging.getLogger(__name__)

class RecommendationType(Enum):
    """Recommendation type enumeration"""
    COLLABORATION = "collaboration"
    CONTENT_SIMILAR = "content_similar"
    AUDIENCE_OVERLAP = "audience_overlap"
    SKILL_COMPLEMENT = "skill_complement"
    TREND_BASED = "trend_based"
    PERFORMANCE_BASED = "performance_based"
    GEOGRAPHIC = "geographic"
    NICHE_SIMILAR = "niche_similar"

class CreatorCategory(Enum):
    """Creator category enumeration"""
    MUSICIAN = "musician"
    BLOGGER = "blogger"
    PHOTOGRAPHER = "photographer"
    INFLUENCER = "influencer"
    COMEDIAN = "comedian"
    ARTIST = "artist"
    EDUCATOR = "educator"
    GAMER = "gamer"
    CHEF = "chef"
    FITNESS = "fitness"
    TECH = "tech"
    LIFESTYLE = "lifestyle"

class RecommendationStrategy(Enum):
    """Recommendation strategy enumeration"""
    COLLABORATIVE_FILTERING = "collaborative_filtering"
    CONTENT_BASED = "content_based"
    HYBRID = "hybrid"
    MATRIX_FACTORIZATION = "matrix_factorization"
    DEEP_LEARNING = "deep_learning"
    GRAPH_BASED = "graph_based"

@dataclass
class CreatorProfile:
    """Creator profile data"""
    creator_id: str
    name: str
    category: CreatorCategory
    skills: List[str] = field(default_factory=list)
    genres: List[str] = field(default_factory=list)
    location: str = "unknown"
    follower_count: int = 0
    engagement_rate: float = 0.0
    content_frequency: float = 0.0  # posts per week
    quality_score: float = 0.0
    collaboration_history: List[str] = field(default_factory=list)
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    audience_demographics: Dict[str, float] = field(default_factory=dict)
    content_tags: List[str] = field(default_factory=list)
    preferences: Dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)
    last_active: float = field(default_factory=time.time)

@dataclass
class RecommendationRequest:
    """Recommendation request parameters"""
    target_creator_id: str
    recommendation_type: RecommendationType
    max_results: int = 10
    min_score: float = 0.1
    exclude_creators: List[str] = field(default_factory=list)
    filters: Dict[str, Any] = field(default_factory=dict)
    boost_factors: Dict[str, float] = field(default_factory=dict)
    context: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Recommendation:
    """Individual recommendation result"""
    creator_id: str
    score: float
    confidence: float
    reason: str
    recommendation_type: RecommendationType
    explanation: str
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class RecommendationResult:
    """Complete recommendation result"""
    target_creator_id: str
    recommendations: List[Recommendation]
    total_candidates: int
    processing_time: float
    strategy_used: RecommendationStrategy
    timestamp: float = field(default_factory=time.time)

class CreatorRecommendationService:
    """
    Enterprise Creator Recommendation Service
    
    Provides AI-powered creator recommendations with:
    - Multiple recommendation algorithms
    - Content-based filtering
    - Collaborative filtering
    - Hybrid approaches
    - Real-time updates
    - Performance tracking
    """
    
    def __init__(self) -> None:
        """Initialize creator recommendation service"""
        self.creators: Dict[str, CreatorProfile] = {}
        self.interaction_matrix: Dict[str, Dict[str, float]] = defaultdict(dict)
        self.content_similarity_matrix: Dict[str, Dict[str, float]] = defaultdict(dict)
        self.collaboration_network: Dict[str, Set[str]] = defaultdict(set)
        
        # Feature vectors for content-based filtering
        self.creator_features: Dict[str, np.ndarray] = {}
        self.skill_embeddings: Dict[str, np.ndarray] = {}
        self.genre_embeddings: Dict[str, np.ndarray] = {}
        
        # Performance tracking
        self.recommendation_stats: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
            "total_requests": 0,
            "avg_processing_time": 0.0,
            "avg_score": 0.0,
            "click_through_rate": 0.0,
            "conversion_rate": 0.0
        })
        
        # Configuration
        self.config = {
            "feature_dimension": 128,
            "similarity_threshold": 0.1,
            "collaboration_weight": 0.3,
            "content_weight": 0.4,
            "performance_weight": 0.3,
            "freshness_decay": 0.95,
            "update_interval": 3600.0,  # 1 hour
            "min_interactions": 5,
            "enable_deep_learning": False
        }
        
        self.shutdown_event = asyncio.Event()
        self._lock = asyncio.Lock()
        
        # Background tasks
        self.update_task: Optional[asyncio.Task] = None
        
        logger.info("CreatorRecommendationService initialized")
    
    async def start(self) -> None:
        """Start the recommendation service"""
        try:
            # Initialize embeddings
            await self._initialize_embeddings()
            
            # Start background update task
            self.update_task = asyncio.create_task(self._update_loop())
            
            logger.info("CreatorRecommendationService started successfully")
        except Exception as e:
            logger.error("Failed to start CreatorRecommendationService: %s", e)
            raise
    
    async def stop(self) -> None:
        """Stop the recommendation service"""
        try:
            self.shutdown_event.set()
            
            # Stop update task
            if self.update_task:
                self.update_task.cancel()
                try:
                    await self.update_task
                except asyncio.CancelledError:
                    pass
            
            logger.info("CreatorRecommendationService stopped successfully")
        except Exception as e:
            logger.error("Error stopping CreatorRecommendationService: %s", e)
    
    async def register_creator(self, profile -> None: CreatorProfile) -> None:
        """Register a new creator profile"""
        async with self._lock:
            self.creators[profile.creator_id] = profile
            
            # Generate feature vector
            await self._generate_creator_features(profile)
            
            # Update similarity matrices
            await self._update_similarity_matrices(profile.creator_id)
        
        logger.info("Registered creator: %s", profile.creator_id)
    
    async def update_creator(self, creator_id -> None: str, updates -> None: Dict[str, Any]) -> None:
        """Update creator profile"""
        async with self._lock:
            if creator_id not in self.creators:
                logger.warning("Creator %s not found for update", creator_id)
                return
            
            profile = self.creators[creator_id]
            
            # Apply updates
            for key, value in updates.items():
                if hasattr(profile, key):
                    setattr(profile, key, value)
            
            profile.last_active = time.time()
            
            # Regenerate features
            await self._generate_creator_features(profile)
            await self._update_similarity_matrices(creator_id)
        
        logger.info("Updated creator: %s", creator_id)
    
    async def record_interaction(
        self,
        creator1_id -> None: str,
        creator2_id -> None: str,
        interaction_type -> None: str,
        strength -> None: float = 1.0
    ) -> None:
        """Record interaction between creators"""
        async with self._lock:
            # Update interaction matrix
            if creator2_id not in self.interaction_matrix[creator1_id]:
                self.interaction_matrix[creator1_id][creator2_id] = 0.0
            
            self.interaction_matrix[creator1_id][creator2_id] += strength
            
            # For symmetric interactions (like collaborations)
            if interaction_type in ["collaboration", "mutual_follow"]:
                if creator1_id not in self.interaction_matrix[creator2_id]:
                    self.interaction_matrix[creator2_id][creator1_id] = 0.0
                self.interaction_matrix[creator2_id][creator1_id] += strength
                
                # Update collaboration network
                self.collaboration_network[creator1_id].add(creator2_id)
                self.collaboration_network[creator2_id].add(creator1_id)
        
        logger.debug("Recorded interaction: %s -> %s (%s)", creator1_id, creator2_id, interaction_type)
    
    async def get_recommendations(self, request: RecommendationRequest) -> RecommendationResult:
        """Get creator recommendations"""
        start_time = time.time()
        
        async with self._lock:
            if request.target_creator_id not in self.creators:
                logger.warning("Target creator %s not found", request.target_creator_id)
                return RecommendationResult(
                    target_creator_id=request.target_creator_id,
                    recommendations=[],
                    total_candidates=0,
                    processing_time=0.0,
                    strategy_used=RecommendationStrategy.CONTENT_BASED
                )
            
            target_profile = self.creators[request.target_creator_id]
            
            # Select recommendation strategy
            strategy = await self._select_strategy(request)
            
            # Get candidate creators
            candidates = await self._get_candidates(request)
            
            # Generate recommendations based on strategy
            recommendations = await self._generate_recommendations(
                target_profile, candidates, request, strategy
            )
            
            # Sort by score and apply limits
            recommendations.sort(key=lambda r: r.score, reverse=True)
            recommendations = recommendations[:request.max_results]
            
            processing_time = time.time() - start_time
            
            # Update stats
            await self._update_stats(request, recommendations, processing_time)
            
            result = RecommendationResult(
                target_creator_id=request.target_creator_id,
                recommendations=recommendations,
                total_candidates=len(candidates),
                processing_time=processing_time,
                strategy_used=strategy
            )
            
            logger.info(
                "Generated %d recommendations for %s in %.3fs",
                len(recommendations), request.target_creator_id, processing_time
            )
            
            return result
    
    async def get_trending_creators(
        self,
        category: Optional[CreatorCategory] = None,
        location: Optional[str] = None,
        limit: int = 20
    ) -> List[CreatorProfile]:
        """Get trending creators"""
        async with self._lock:
            creators = list(self.creators.values())
            
            # Apply filters
            if category:
                creators = [c for c in creators if c.category == category]
            
            if location:
                creators = [c for c in creators if c.location == location]
            
            # Calculate trending score
            current_time = time.time()
            for creator in creators:
                # Trending score based on recent activity, engagement, and growth
                time_factor = max(0, 1 - (current_time - creator.last_active) / (7 * 24 * 3600))  # Week decay
                engagement_factor = min(1.0, creator.engagement_rate / 0.1)  # Normalize to 10%
                follower_factor = math.log(max(1, creator.follower_count)) / 20  # Log scale
                
                creator.trending_score = (
                    time_factor * 0.4 +
                    engagement_factor * 0.4 +
                    follower_factor * 0.2
                )
            
            # Sort by trending score
            creators.sort(key=lambda c: getattr(c, 'trending_score', 0), reverse=True)
            
            return creators[:limit]
    
    async def get_collaboration_suggestions(
        self,
        creator_id: str,
        project_type: str = "general",
        max_results: int = 10
    ) -> List[Recommendation]:
        """Get collaboration suggestions for a creator"""
        request = RecommendationRequest(
            target_creator_id=creator_id,
            recommendation_type=RecommendationType.COLLABORATION,
            max_results=max_results,
            context={"project_type": project_type}
        )
        
        result = await self.get_recommendations(request)
        return result.recommendations
    
    async def get_similar_creators(
        self,
        creator_id: str,
        similarity_type: str = "content",
        max_results: int = 10
    ) -> List[Recommendation]:
        """Get creators similar to the target creator"""
        rec_type = (RecommendationType.CONTENT_SIMILAR if similarity_type == "content"
                   else RecommendationType.AUDIENCE_OVERLAP)
        
        request = RecommendationRequest(
            target_creator_id=creator_id,
            recommendation_type=rec_type,
            max_results=max_results
        )
        
        result = await self.get_recommendations(request)
        return result.recommendations
    
    async def get_service_status(self) -> Dict[str, Any]:
        """Get service status and metrics"""
        async with self._lock:
            total_creators = len(self.creators)
            total_interactions = sum(
                len(interactions) for interactions in self.interaction_matrix.values()
            )
            
            avg_stats = {}
            if self.recommendation_stats:
                avg_stats = {
                    "avg_processing_time": sum(
                        stats["avg_processing_time"] for stats in self.recommendation_stats.values()
                    ) / len(self.recommendation_stats),
                    "total_requests": sum(
                        stats["total_requests"] for stats in self.recommendation_stats.values()
                    )
                }
            
            return {
                "total_creators": total_creators,
                "total_interactions": total_interactions,
                "active_collaboration_networks": len(self.collaboration_network),
                "feature_vectors_generated": len(self.creator_features),
                "recommendation_stats": avg_stats,
                "config": dict(self.config)
            }
    
    async def _select_strategy(self, request: RecommendationRequest) -> RecommendationStrategy:
        """Select the best recommendation strategy"""
        target_profile = self.creators[request.target_creator_id]
        
        # Check if enough interaction data for collaborative filtering
        interaction_count = len(self.interaction_matrix.get(request.target_creator_id, {}))
        
        if interaction_count >= self.config["min_interactions"]:
            return RecommendationStrategy.HYBRID
        elif request.recommendation_type == RecommendationType.COLLABORATION:
            return RecommendationStrategy.GRAPH_BASED
        else:
            return RecommendationStrategy.CONTENT_BASED
    
    async def _get_candidates(self, request: RecommendationRequest) -> List[CreatorProfile]:
        """Get candidate creators for recommendation"""
        candidates = []
        
        for creator_id, profile in self.creators.items():
            # Skip target creator
            if creator_id == request.target_creator_id:
                continue
            
            # Skip excluded creators
            if creator_id in request.exclude_creators:
                continue
            
            # Apply filters
            if not await self._matches_filters(profile, request.filters):
                continue
            
            candidates.append(profile)
        
        return candidates
    
    async def _matches_filters(self, profile: CreatorProfile, filters: Dict[str, Any]) -> bool:
        """Check if profile matches filters"""
        for key, value in filters.items():
            if key == "category" and profile.category != value:
                return False
            elif key == "location" and profile.location != value:
                return False
            elif key == "min_followers" and profile.follower_count < value:
                return False
            elif key == "max_followers" and profile.follower_count > value:
                return False
            elif key == "min_engagement" and profile.engagement_rate < value:
                return False
            elif key == "skills" and not any(skill in profile.skills for skill in value):
                return False
            elif key == "genres" and not any(genre in profile.genres for genre in value):
                return False
        
        return True
    
    async def _generate_recommendations(
        self,
        target_profile: CreatorProfile,
        candidates: List[CreatorProfile],
        request: RecommendationRequest,
        strategy: RecommendationStrategy
    ) -> List[Recommendation]:
        """Generate recommendations using specified strategy"""
        recommendations = []
        
        for candidate in candidates:
            score = 0.0
            confidence = 0.0
            reason = ""
            explanation = ""
            
            if strategy == RecommendationStrategy.CONTENT_BASED:
                score, confidence, reason, explanation = await self._content_based_score(
                    target_profile, candidate, request
                )
            
            elif strategy == RecommendationStrategy.COLLABORATIVE_FILTERING:
                score, confidence, reason, explanation = await self._collaborative_filtering_score(
                    target_profile, candidate, request
                )
            
            elif strategy == RecommendationStrategy.HYBRID:
                content_score, content_conf, content_reason, content_exp = await self._content_based_score(
                    target_profile, candidate, request
                )
                collab_score, collab_conf, collab_reason, collab_exp = await self._collaborative_filtering_score(
                    target_profile, candidate, request
                )
                
                score = (content_score * self.config["content_weight"] +
                        collab_score * self.config["collaboration_weight"])
                confidence = (content_conf + collab_conf) / 2
                reason = f"Hybrid: {content_reason} + {collab_reason}"
                explanation = f"{content_exp} {collab_exp}"
            
            elif strategy == RecommendationStrategy.GRAPH_BASED:
                score, confidence, reason, explanation = await self._graph_based_score(
                    target_profile, candidate, request
                )
            
            # Apply boost factors
            for boost_key, boost_value in request.boost_factors.items():
                if boost_key in candidate.metadata:
                    score *= boost_value
            
            # Check minimum score threshold
            if score >= request.min_score:
                recommendation = Recommendation(
                    creator_id=candidate.creator_id,
                    score=score,
                    confidence=confidence,
                    reason=reason,
                    recommendation_type=request.recommendation_type,
                    explanation=explanation,
                    metadata={
                        "strategy": strategy.value,
                        "candidate_profile": {
                            "name": candidate.name,
                            "category": candidate.category.value,
                            "follower_count": candidate.follower_count,
                            "engagement_rate": candidate.engagement_rate
                        }
                    }
                )
                recommendations.append(recommendation)
        
        return recommendations
    
    async def _content_based_score(
        self,
        target_profile: CreatorProfile,
        candidate: CreatorProfile,
        request: RecommendationRequest
    ) -> Tuple[float, float, str, str]:
        """Calculate content-based similarity score"""
        score = 0.0
        confidence = 0.8
        
        # Skill similarity
        skill_overlap = len(set(target_profile.skills) & set(candidate.skills))
        skill_score = skill_overlap / max(1, len(target_profile.skills)) if target_profile.skills else 0
        
        # Genre similarity
        genre_overlap = len(set(target_profile.genres) & set(candidate.genres))
        genre_score = genre_overlap / max(1, len(target_profile.genres)) if target_profile.genres else 0
        
        # Category bonus
        category_score = 1.0 if target_profile.category == candidate.category else 0.5
        
        # Performance compatibility
        performance_diff = abs(target_profile.quality_score - candidate.quality_score)
        performance_score = max(0, 1 - performance_diff)
        
        # Calculate weighted score
        score = (
            skill_score * 0.3 +
            genre_score * 0.3 +
            category_score * 0.2 +
            performance_score * 0.2
        )
        
        reason = f"Content similarity (skills: {skill_score:.2f}, genres: {genre_score:.2f})"
        explanation = f"Shares {skill_overlap} skills and {genre_overlap} genres with compatible performance level."
        
        return score, confidence, reason, explanation
    
    async def _collaborative_filtering_score(
        self,
        target_profile: CreatorProfile,
        candidate: CreatorProfile,
        request: RecommendationRequest
    ) -> Tuple[float, float, str, str]:
        """Calculate collaborative filtering score"""
        target_id = target_profile.creator_id
        candidate_id = candidate.creator_id
        
        # Get interaction history
        target_interactions = self.interaction_matrix.get(target_id, {})
        
        if not target_interactions:
            return 0.0, 0.0, "No interaction history", "Insufficient collaboration data"
        
        # Find similar creators (those who interacted with similar creators)
        similar_creators = []
        for other_id, interaction_strength in target_interactions.items():
            if other_id in self.interaction_matrix:
                other_interactions = self.interaction_matrix[other_id]
                if candidate_id in other_interactions:
                    similar_creators.append((other_id, interaction_strength, other_interactions[candidate_id]))
        
        if not similar_creators:
            return 0.0, 0.0, "No mutual connections", "No creators with mutual interactions found"
        
        # Calculate weighted score
        total_weight = 0.0
        weighted_score = 0.0
        
        for similar_id, target_strength, candidate_strength in similar_creators:
            weight = target_strength
            weighted_score += weight * candidate_strength
            total_weight += weight
        
        score = weighted_score / total_weight if total_weight > 0 else 0.0
        confidence = min(1.0, len(similar_creators) / 5)  # Higher confidence with more connections
        
        reason = f"Collaborative filtering ({len(similar_creators)} mutual connections)"
        explanation = f"Recommended based on {len(similar_creators)} creators with similar interaction patterns."
        
        return score, confidence, reason, explanation
    
    async def _graph_based_score(
        self,
        target_profile: CreatorProfile,
        candidate: CreatorProfile,
        request: RecommendationRequest
    ) -> Tuple[float, float, str, str]:
        """Calculate graph-based recommendation score"""
        target_id = target_profile.creator_id
        candidate_id = candidate.creator_id
        
        # Direct connection
        if candidate_id in self.collaboration_network.get(target_id, set()):
            return 0.0, 0.0, "Already connected", "Already in collaboration network"
        
        # Find shortest path and mutual connections
        target_network = self.collaboration_network.get(target_id, set())
        candidate_network = self.collaboration_network.get(candidate_id, set())
        
        # Mutual connections (distance 2)
        mutual_connections = target_network & candidate_network
        mutual_score = len(mutual_connections) / 10  # Normalize
        
        # Network size compatibility
        target_network_size = len(target_network)
        candidate_network_size = len(candidate_network)
        
        size_ratio = min(target_network_size, candidate_network_size) / max(1, max(target_network_size, candidate_network_size))
        size_score = size_ratio
        
        # Calculate overall score
        score = mutual_score * 0.7 + size_score * 0.3
        confidence = 0.6
        
        reason = f"Network proximity ({len(mutual_connections)} mutual connections)"
        explanation = f"Connected through {len(mutual_connections)} mutual collaborators with compatible network size."
        
        return score, confidence, reason, explanation
    
    async def _generate_creator_features(self, profile -> None: CreatorProfile) -> None:
        """Generate feature vector for a creator"""
        # Create feature vector from profile attributes
        features = []
        
        # Category one-hot encoding
        category_features = [0.0] * len(CreatorCategory)
        category_features[list(CreatorCategory).index(profile.category)] = 1.0
        features.extend(category_features)
        
        # Numerical features
        features.extend([
            profile.follower_count / 1000000,  # Normalize followers
            profile.engagement_rate,
            profile.content_frequency / 10,  # Normalize frequency
            profile.quality_score
        ])
        
        # Pad to desired dimension
        while len(features) < self.config["feature_dimension"]:
            features.append(0.0)
        
        self.creator_features[profile.creator_id] = np.array(features[:self.config["feature_dimension"]])
    
    async def _update_similarity_matrices(self, creator_id -> None: str) -> None:
        """Update similarity matrices for a creator"""
        if creator_id not in self.creator_features:
            return
        
        target_features = self.creator_features[creator_id]
        
        for other_id, other_features in self.creator_features.items():
            if other_id == creator_id:
                continue
            
            # Calculate cosine similarity
            similarity = np.dot(target_features, other_features) / (
                np.linalg.norm(target_features) * np.linalg.norm(other_features) + 1e-8
            )
            
            self.content_similarity_matrix[creator_id][other_id] = float(similarity)
    
    async def _initialize_embeddings(self) -> None:
        """Initialize skill and genre embeddings"""
        # This would normally load pre-trained embeddings
        # For now, create random embeddings
        all_skills = set()
        all_genres = set()
        
        for profile in self.creators.values():
            all_skills.update(profile.skills)
            all_genres.update(profile.genres)
        
        embedding_dim = 50
        
        for skill in all_skills:
            self.skill_embeddings[skill] = np.random.normal(0, 0.1, embedding_dim)
        
        for genre in all_genres:
            self.genre_embeddings[genre] = np.random.normal(0, 0.1, embedding_dim)
    
    async def _update_stats(
        self,
        request -> None: RecommendationRequest,
        recommendations -> None: List[Recommendation],
        processing_time -> None: float
    ) -> None:
        """Update recommendation statistics"""
        rec_type = request.recommendation_type.value
        stats = self.recommendation_stats[rec_type]
        
        stats["total_requests"] += 1
        
        # Update average processing time
        old_avg = stats["avg_processing_time"]
        stats["avg_processing_time"] = (
            (old_avg * (stats["total_requests"] - 1) + processing_time) /
            stats["total_requests"]
        )
        
        # Update average score
        if recommendations:
            avg_score = sum(r.score for r in recommendations) / len(recommendations)
            old_score_avg = stats["avg_score"]
            stats["avg_score"] = (
                (old_score_avg * (stats["total_requests"] - 1) + avg_score) /
                stats["total_requests"]
            )
    
    async def _update_loop(self) -> None:
        """Background update loop"""
        while not self.shutdown_event.is_set():
            try:
                await asyncio.sleep(self.config["update_interval"])
                await self._update_recommendations()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("Error in update loop: %s", e)
    
    async def _update_recommendations(self) -> None:
        """Update recommendation models and matrices"""
        async with self._lock:
            # Update embeddings
            await self._initialize_embeddings()
            
            # Regenerate all feature vectors
            for profile in self.creators.values():
                await self._generate_creator_features(profile)
            
            # Update similarity matrices
            for creator_id in self.creators.keys():
                await self._update_similarity_matrices(creator_id)
        
        logger.info("Updated recommendation models and similarity matrices")

# Global recommendation service instance
_recommendation_service: Optional[CreatorRecommendationService] = None

async def get_recommendation_service() -> CreatorRecommendationService:
    """Get global recommendation service instance"""
    global _recommendation_service
    if _recommendation_service is None:
        _recommendation_service = CreatorRecommendationService()
        await _recommendation_service.start()
    return _recommendation_service

async def shutdown_recommendation_service() -> None:
    """Shutdown global recommendation service"""
    global _recommendation_service
    if _recommendation_service:
        await _recommendation_service.stop()
        _recommendation_service = None

if __name__ == "__main__":
    async def test_recommendation_service() -> None:
        """Test recommendation service functionality"""
        service = CreatorRecommendationService()
        await service.start()
        
        try:
            # Create test creators
            creators = [
                CreatorProfile(
                    creator_id="creator_1",
                    name="John Musician",
                    category=CreatorCategory.MUSICIAN,
                    skills=["guitar", "vocals", "songwriting"],
                    genres=["rock", "indie"],
                    follower_count=10000,
                    engagement_rate=0.05
                ),
                CreatorProfile(
                    creator_id="creator_2",
                    name="Jane Singer",
                    category=CreatorCategory.MUSICIAN,
                    skills=["vocals", "piano", "composition"],
                    genres=["pop", "rock"],
                    follower_count=15000,
                    engagement_rate=0.07
                ),
                CreatorProfile(
                    creator_id="creator_3",
                    name="Bob Photographer",
                    category=CreatorCategory.PHOTOGRAPHER,
                    skills=["portrait", "landscape", "editing"],
                    genres=["art", "nature"],
                    follower_count=8000,
                    engagement_rate=0.04
                )
            ]
            
            # Register creators
            for creator in creators:
                await service.register_creator(creator)
            
            # Record some interactions
            await service.record_interaction("creator_1", "creator_2", "collaboration", 1.0)
            await service.record_interaction("creator_1", "creator_3", "mutual_follow", 0.5)
            
            # Get recommendations
            request = RecommendationRequest(
                target_creator_id="creator_1",
                recommendation_type=RecommendationType.COLLABORATION,
                max_results=5
            )
            
            result = await service.get_recommendations(request)
            print(f"Recommendations for creator_1:")
            for rec in result.recommendations:
                print(f"  {rec.creator_id}: score={rec.score:.3f}, reason={rec.reason}")
            
            # Get similar creators
            similar = await service.get_similar_creators("creator_1", "content", 3)
            print(f"\nSimilar creators:")
            for rec in similar:
                print(f"  {rec.creator_id}: score={rec.score:.3f}")
            
            # Get service status
            status = await service.get_service_status()
            print(f"\nService status: {status}")
            
        finally:
            await service.stop()
    
    # Run test
    asyncio.run(test_recommendation_service())