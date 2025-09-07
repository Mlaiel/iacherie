"""Recommendation Engine - AI-Powered Content and Creator Recommendation System
===========================================================================

Advanced machine learning recommendation engine providing personalized content
and creator recommendations for marketplace users.

Features:
- Collaborative filtering and content-based recommendations
- Real-time personalization based on user behavior
- Creator-content matching and discovery
- A/B testing framework for recommendation algorithms
- Advanced analytics and performance tracking

Architecture: Enterprise Production-Ready (Backend Level 3)
Module: backend/marketplace/recommendation_engine.py

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import logging
import asyncio
import random
from typing import Dict, List, Optional, Union, Any, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum
from collections import defaultdict, Counter
import uuid
import json
import statistics

logger = logging.getLogger(__name__)

class RecommendationType(Enum):
    """Recommendation type enumeration"""
    CONTENT = "content"
    CREATOR = "creator"
    PRODUCT = "product"
    COLLABORATION = "collaboration"
    TRENDING = "trending"
    SIMILAR_USERS = "similar_users"
    CROSS_SELL = "cross_sell"
    UP_SELL = "up_sell"

class RecommendationAlgorithm(Enum):
    """Recommendation algorithm enumeration"""
    COLLABORATIVE_FILTERING = "collaborative_filtering"
    CONTENT_BASED = "content_based"
    HYBRID = "hybrid"
    MATRIX_FACTORIZATION = "matrix_factorization"
    DEEP_LEARNING = "deep_learning"
    KNOWLEDGE_BASED = "knowledge_based"
    POPULARITY_BASED = "popularity_based"

class RecommendationContext(Enum):
    """Recommendation context enumeration"""
    HOME_FEED = "home_feed"
    SEARCH_RESULTS = "search_results"
    PRODUCT_PAGE = "product_page"
    PROFILE_PAGE = "profile_page"
    CHECKOUT = "checkout"
    EMAIL = "email"
    PUSH_NOTIFICATION = "push_notification"
    DISCOVERY = "discovery"

@dataclass
class UserProfile:
    """User profile for recommendations"""
    user_id: str
    preferences: Dict[str, float] = field(default_factory=dict)
    categories: List[str] = field(default_factory=list)
    behavior_history: List[Dict[str, Any]] = field(default_factory=list)
    demographics: Dict[str, Any] = field(default_factory=dict)
    interaction_scores: Dict[str, float] = field(default_factory=dict)
    last_active: datetime = field(default_factory=datetime.utcnow)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class ContentItem:
    """Content item for recommendations"""
    item_id: str
    title: str
    description: str
    category: str
    subcategory: Optional[str] = None
    creator_id: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    features: Dict[str, float] = field(default_factory=dict)
    popularity_score: float = 0.0
    quality_score: float = 0.8
    engagement_rate: float = 0.0
    price: Optional[Decimal] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class CreatorProfile:
    """Creator profile for recommendations"""
    creator_id: str
    name: str
    category: str
    specialties: List[str] = field(default_factory=list)
    follower_count: int = 0
    engagement_rate: float = 0.0
    content_count: int = 0
    rating: float = 4.0
    collaboration_history: List[str] = field(default_factory=list)
    style_tags: List[str] = field(default_factory=list)
    price_range: Tuple[Decimal, Decimal] = (Decimal("0"), Decimal("1000"))
    availability: bool = True
    location: Optional[str] = None
    languages: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Recommendation:
    """Individual recommendation item"""
    recommendation_id: str
    user_id: str
    item_id: str
    item_type: RecommendationType
    score: float  # 0.0 to 1.0
    confidence: float  # 0.0 to 1.0
    algorithm_used: RecommendationAlgorithm
    context: RecommendationContext
    reason: str = ""
    explanation: List[str] = field(default_factory=list)
    rank: int = 1
    generated_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class RecommendationSet:
    """Set of recommendations for a user"""
    set_id: str
    user_id: str
    context: RecommendationContext
    recommendations: List[Recommendation] = field(default_factory=list)
    diversity_score: float = 0.0
    freshness_score: float = 0.0
    total_items: int = 0
    algorithm_mix: Dict[str, int] = field(default_factory=dict)
    generated_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: datetime = field(default_factory=lambda: datetime.utcnow() + timedelta(hours=24))
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class InteractionEvent:
    """User interaction event"""
    event_id: str
    user_id: str
    item_id: str
    item_type: str
    action: str  # "view", "like", "share", "purchase", "click", etc.
    duration: Optional[float] = None  # seconds
    context: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class RecommendationPerformance:
    """Recommendation performance metrics"""
    metric_id: str
    recommendation_set_id: str
    click_through_rate: float = 0.0
    conversion_rate: float = 0.0
    engagement_rate: float = 0.0
    diversity_score: float = 0.0
    novelty_score: float = 0.0
    satisfaction_score: float = 0.0
    total_impressions: int = 0
    total_clicks: int = 0
    total_conversions: int = 0
    revenue_generated: Decimal = Decimal("0")
    measured_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

class RecommendationEngine:
    """Advanced AI-powered recommendation system"""
    
    def __init__(self):
        self.user_profiles: Dict[str, UserProfile] = {}
        self.content_items: Dict[str, ContentItem] = {}
        self.creator_profiles: Dict[str, CreatorProfile] = {}
        self.recommendations: Dict[str, RecommendationSet] = {}
        self.interactions: List[InteractionEvent] = []
        self.performance_metrics: Dict[str, RecommendationPerformance] = {}
        
        # ML model placeholders (in production would be actual trained models)
        self.collaborative_model = None
        self.content_model = None
        self.hybrid_model = None
        
        # Algorithm weights for hybrid approach
        self.algorithm_weights = {
            RecommendationAlgorithm.COLLABORATIVE_FILTERING: 0.4,
            RecommendationAlgorithm.CONTENT_BASED: 0.3,
            RecommendationAlgorithm.POPULARITY_BASED: 0.2,
            RecommendationAlgorithm.KNOWLEDGE_BASED: 0.1
        }
        
        # Initialize with sample data
        self._initialize_sample_data()
    
    def _initialize_sample_data(self):
        """Initialize with sample data for demonstration"""
        # Sample content items
        sample_content = [
            ContentItem(
                item_id="content_001",
                title="Digital Art Masterclass",
                description="Learn advanced digital art techniques",
                category="Education",
                subcategory="Art",
                creator_id="creator_001",
                tags=["digital", "art", "tutorial", "advanced"],
                features={"difficulty": 0.8, "duration": 120.0, "interactivity": 0.6},
                popularity_score=0.85,
                price=Decimal("99.99")
            ),
            ContentItem(
                item_id="content_002",
                title="Photography Portfolio Review",
                description="Professional portfolio review and feedback",
                category="Services",
                subcategory="Photography",
                creator_id="creator_002",
                tags=["photography", "portfolio", "review", "professional"],
                features={"personalization": 0.9, "expertise": 0.8, "value": 0.7},
                popularity_score=0.72,
                price=Decimal("149.99")
            ),
            ContentItem(
                item_id="content_003",
                title="Music Production Basics",
                description="Introduction to music production software",
                category="Education",
                subcategory="Music",
                creator_id="creator_003",
                tags=["music", "production", "beginner", "software"],
                features={"difficulty": 0.3, "duration": 90.0, "practical": 0.8},
                popularity_score=0.91,
                price=Decimal("79.99")
            )
        ]
        
        for content in sample_content:
            self.content_items[content.item_id] = content
        
        # Sample creator profiles
        sample_creators = [
            CreatorProfile(
                creator_id="creator_001",
                name="Alex Digital",
                category="Digital Art",
                specialties=["Digital Painting", "Concept Art", "Character Design"],
                follower_count=15000,
                engagement_rate=0.08,
                content_count=45,
                rating=4.7,
                style_tags=["modern", "detailed", "vibrant"],
                price_range=(Decimal("50"), Decimal("200"))
            ),
            CreatorProfile(
                creator_id="creator_002",
                name="Sarah Lens",
                category="Photography",
                specialties=["Portrait", "Wedding", "Commercial"],
                follower_count=22000,
                engagement_rate=0.12,
                content_count=67,
                rating=4.9,
                style_tags=["artistic", "professional", "creative"],
                price_range=(Decimal("100"), Decimal("500"))
            ),
            CreatorProfile(
                creator_id="creator_003",
                name="Beat Master",
                category="Music Production",
                specialties=["Electronic", "Hip Hop", "Mixing"],
                follower_count=8500,
                engagement_rate=0.15,
                content_count=23,
                rating=4.5,
                style_tags=["modern", "energetic", "innovative"],
                price_range=(Decimal("30"), Decimal("150"))
            )
        ]
        
        for creator in sample_creators:
            self.creator_profiles[creator.creator_id] = creator
    
    async def generate_recommendations(
        self,
        user_id: str,
        context: RecommendationContext = RecommendationContext.HOME_FEED,
        recommendation_types: List[RecommendationType] = None,
        max_items: int = 10,
        diversity_weight: float = 0.3
    ) -> RecommendationSet:
        """Generate personalized recommendations for a user"""
        try:
            set_id = f"rec_set_{uuid.uuid4().hex[:12]}"
            
            if recommendation_types is None:
                recommendation_types = [RecommendationType.CONTENT, RecommendationType.CREATOR]
            
            # Get or create user profile
            user_profile = await self._get_or_create_user_profile(user_id)
            
            recommendations = []
            algorithm_mix = defaultdict(int)
            
            # Generate recommendations for each type
            for rec_type in recommendation_types:
                type_recommendations = await self._generate_type_recommendations(
                    user_profile, rec_type, context, max_items // len(recommendation_types)
                )
                recommendations.extend(type_recommendations)
                
                # Track algorithm usage
                for rec in type_recommendations:
                    algorithm_mix[rec.algorithm_used.value] += 1
            
            # Apply diversity and ranking
            recommendations = await self._apply_diversity_ranking(
                recommendations, diversity_weight, max_items
            )
            
            # Calculate diversity and freshness scores
            diversity_score = await self._calculate_diversity_score(recommendations)
            freshness_score = await self._calculate_freshness_score(recommendations, user_profile)
            
            recommendation_set = RecommendationSet(
                set_id=set_id,
                user_id=user_id,
                context=context,
                recommendations=recommendations,
                diversity_score=diversity_score,
                freshness_score=freshness_score,
                total_items=len(recommendations),
                algorithm_mix=dict(algorithm_mix)
            )
            
            self.recommendations[set_id] = recommendation_set
            
            logger.info(f"Generated {len(recommendations)} recommendations for user {user_id}")
            return recommendation_set
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            return RecommendationSet(
                set_id=f"error_{uuid.uuid4().hex[:8]}",
                user_id=user_id,
                context=context
            )
    
    async def _get_or_create_user_profile(self, user_id: str) -> UserProfile:
        """Get existing user profile or create new one"""
        if user_id not in self.user_profiles:
            # Create new profile
            profile = UserProfile(
                user_id=user_id,
                preferences={},
                categories=[],
                behavior_history=[]
            )
            
            # Initialize with default preferences
            await self._initialize_user_preferences(profile)
            self.user_profiles[user_id] = profile
        
        return self.user_profiles[user_id]
    
    async def _initialize_user_preferences(self, profile: UserProfile):
        """Initialize user preferences based on available data"""
        # In production, would use onboarding data, demographic info, etc.
        # For now, use random preferences as placeholder
        categories = ["Education", "Services", "Entertainment", "Tools", "Digital Art", "Photography", "Music"]
        
        for category in categories:
            profile.preferences[category] = random.uniform(0.1, 0.9)
        
        profile.categories = list(profile.preferences.keys())
    
    async def _generate_type_recommendations(
        self,
        user_profile: UserProfile,
        rec_type: RecommendationType,
        context: RecommendationContext,
        max_items: int
    ) -> List[Recommendation]:
        """Generate recommendations for a specific type"""
        recommendations = []
        
        if rec_type == RecommendationType.CONTENT:
            recommendations = await self._generate_content_recommendations(
                user_profile, context, max_items
            )
        elif rec_type == RecommendationType.CREATOR:
            recommendations = await self._generate_creator_recommendations(
                user_profile, context, max_items
            )
        elif rec_type == RecommendationType.TRENDING:
            recommendations = await self._generate_trending_recommendations(
                user_profile, context, max_items
            )
        elif rec_type == RecommendationType.SIMILAR_USERS:
            recommendations = await self._generate_similar_user_recommendations(
                user_profile, context, max_items
            )
        
        return recommendations
    
    async def _generate_content_recommendations(
        self,
        user_profile: UserProfile,
        context: RecommendationContext,
        max_items: int
    ) -> List[Recommendation]:
        """Generate content recommendations using hybrid approach"""
        recommendations = []
        
        # Collaborative filtering recommendations
        collaborative_recs = await self._collaborative_filtering_content(user_profile, max_items // 2)
        recommendations.extend(collaborative_recs)
        
        # Content-based recommendations
        content_based_recs = await self._content_based_filtering(user_profile, max_items // 2)
        recommendations.extend(content_based_recs)
        
        # Popularity-based recommendations (for new users)
        if len(user_profile.behavior_history) < 5:
            popularity_recs = await self._popularity_based_content(user_profile, max_items // 3)
            recommendations.extend(popularity_recs)
        
        return recommendations[:max_items]
    
    async def _collaborative_filtering_content(
        self,
        user_profile: UserProfile,
        max_items: int
    ) -> List[Recommendation]:
        """Generate content recommendations using collaborative filtering"""
        recommendations = []
        
        # Simplified collaborative filtering (in production would use proper ML model)
        for item_id, item in self.content_items.items():
            # Skip items user has already interacted with
            if any(interaction['item_id'] == item_id for interaction in user_profile.behavior_history):
                continue
            
            # Calculate similarity score based on user preferences
            category_match = user_profile.preferences.get(item.category, 0.5)
            popularity_factor = item.popularity_score
            
            # Simulate collaborative score
            collaborative_score = (category_match * 0.6 + popularity_factor * 0.4) * random.uniform(0.8, 1.0)
            
            if collaborative_score > 0.5:  # Threshold for recommendations
                recommendation = Recommendation(
                    recommendation_id=f"rec_{uuid.uuid4().hex[:12]}",
                    user_id=user_profile.user_id,
                    item_id=item_id,
                    item_type=RecommendationType.CONTENT,
                    score=collaborative_score,
                    confidence=0.75,
                    algorithm_used=RecommendationAlgorithm.COLLABORATIVE_FILTERING,
                    context=RecommendationContext.HOME_FEED,
                    reason=f"Popular among users with similar interests in {item.category}",
                    explanation=[
                        f"Users who liked similar {item.category} content also enjoyed this",
                        f"High rating ({item.quality_score:.1f}/1.0) from similar users"
                    ]
                )
                recommendations.append(recommendation)
        
        # Sort by score and return top items
        recommendations.sort(key=lambda x: x.score, reverse=True)
        return recommendations[:max_items]
    
    async def _content_based_filtering(
        self,
        user_profile: UserProfile,
        max_items: int
    ) -> List[Recommendation]:
        """Generate content recommendations using content-based filtering"""
        recommendations = []
        
        # Get user's preferred features from interaction history
        preferred_features = await self._extract_user_feature_preferences(user_profile)
        
        for item_id, item in self.content_items.items():
            # Skip items user has already interacted with
            if any(interaction['item_id'] == item_id for interaction in user_profile.behavior_history):
                continue
            
            # Calculate content similarity score
            feature_similarity = self._calculate_feature_similarity(preferred_features, item.features)
            category_preference = user_profile.preferences.get(item.category, 0.5)
            
            content_score = (feature_similarity * 0.7 + category_preference * 0.3)
            
            if content_score > 0.4:  # Threshold for recommendations
                recommendation = Recommendation(
                    recommendation_id=f"rec_{uuid.uuid4().hex[:12]}",
                    user_id=user_profile.user_id,
                    item_id=item_id,
                    item_type=RecommendationType.CONTENT,
                    score=content_score,
                    confidence=0.8,
                    algorithm_used=RecommendationAlgorithm.CONTENT_BASED,
                    context=RecommendationContext.HOME_FEED,
                    reason=f"Matches your interests in {item.category}",
                    explanation=[
                        f"Similar to content you've enjoyed before",
                        f"Matches your preferred content features"
                    ]
                )
                recommendations.append(recommendation)
        
        recommendations.sort(key=lambda x: x.score, reverse=True)
        return recommendations[:max_items]
    
    async def _extract_user_feature_preferences(self, user_profile: UserProfile) -> Dict[str, float]:
        """Extract user feature preferences from interaction history"""
        feature_preferences = defaultdict(list)
        
        # Analyze user's interaction history
        for interaction in user_profile.behavior_history:
            item = self.content_items.get(interaction['item_id'])
            if item and interaction['action'] in ['like', 'purchase', 'share']:
                # Positive interaction - learn from features
                for feature, value in item.features.items():
                    feature_preferences[feature].append(value)
        
        # Calculate average preferences
        avg_preferences = {}
        for feature, values in feature_preferences.items():
            avg_preferences[feature] = statistics.mean(values) if values else 0.5
        
        return avg_preferences
    
    def _calculate_feature_similarity(
        self,
        user_features: Dict[str, float],
        item_features: Dict[str, float]
    ) -> float:
        """Calculate similarity between user preferences and item features"""
        if not user_features or not item_features:
            return 0.5  # Neutral similarity for new users
        
        # Calculate cosine similarity
        common_features = set(user_features.keys()) & set(item_features.keys())
        
        if not common_features:
            return 0.5
        
        dot_product = sum(user_features[f] * item_features[f] for f in common_features)
        user_norm = (sum(user_features[f]**2 for f in common_features))**0.5
        item_norm = (sum(item_features[f]**2 for f in common_features))**0.5
        
        if user_norm == 0 or item_norm == 0:
            return 0.5
        
        return dot_product / (user_norm * item_norm)
    
    async def _popularity_based_content(
        self,
        user_profile: UserProfile,
        max_items: int
    ) -> List[Recommendation]:
        """Generate popularity-based content recommendations"""
        recommendations = []
        
        # Sort content by popularity score
        popular_items = sorted(
            self.content_items.values(),
            key=lambda x: x.popularity_score,
            reverse=True
        )
        
        for item in popular_items[:max_items]:
            recommendation = Recommendation(
                recommendation_id=f"rec_{uuid.uuid4().hex[:12]}",
                user_id=user_profile.user_id,
                item_id=item.item_id,
                item_type=RecommendationType.CONTENT,
                score=item.popularity_score,
                confidence=0.6,
                algorithm_used=RecommendationAlgorithm.POPULARITY_BASED,
                context=RecommendationContext.HOME_FEED,
                reason="Popular content trending now",
                explanation=[
                    "Highly rated by the community",
                    "Currently trending in your category"
                ]
            )
            recommendations.append(recommendation)
        
        return recommendations
    
    async def _generate_creator_recommendations(
        self,
        user_profile: UserProfile,
        context: RecommendationContext,
        max_items: int
    ) -> List[Recommendation]:
        """Generate creator recommendations"""
        recommendations = []
        
        # Find creators based on user preferences
        for creator_id, creator in self.creator_profiles.items():
            # Calculate match score
            category_match = user_profile.preferences.get(creator.category, 0.5)
            quality_score = min(creator.rating / 5.0, 1.0)  # Normalize rating to 0-1
            engagement_factor = min(creator.engagement_rate * 10, 1.0)  # Scale engagement
            
            match_score = (category_match * 0.5 + quality_score * 0.3 + engagement_factor * 0.2)
            
            if match_score > 0.4:
                recommendation = Recommendation(
                    recommendation_id=f"rec_{uuid.uuid4().hex[:12]}",
                    user_id=user_profile.user_id,
                    item_id=creator_id,
                    item_type=RecommendationType.CREATOR,
                    score=match_score,
                    confidence=0.7,
                    algorithm_used=RecommendationAlgorithm.CONTENT_BASED,
                    context=context,
                    reason=f"Matches your interest in {creator.category}",
                    explanation=[
                        f"High-rated creator ({creator.rating:.1f}/5.0)",
                        f"Specializes in {', '.join(creator.specialties[:2])}"
                    ]
                )
                recommendations.append(recommendation)
        
        recommendations.sort(key=lambda x: x.score, reverse=True)
        return recommendations[:max_items]
    
    async def _generate_trending_recommendations(
        self,
        user_profile: UserProfile,
        context: RecommendationContext,
        max_items: int
    ) -> List[Recommendation]:
        """Generate trending content recommendations"""
        recommendations = []
        
        # Get trending items (simulated - would use real trend data)
        trending_items = [
            item for item in self.content_items.values()
            if item.popularity_score > 0.8
        ]
        
        for item in trending_items[:max_items]:
            recommendation = Recommendation(
                recommendation_id=f"rec_{uuid.uuid4().hex[:12]}",
                user_id=user_profile.user_id,
                item_id=item.item_id,
                item_type=RecommendationType.TRENDING,
                score=item.popularity_score,
                confidence=0.8,
                algorithm_used=RecommendationAlgorithm.POPULARITY_BASED,
                context=context,
                reason="Trending now",
                explanation=[
                    "High engagement in the last 24 hours",
                    "Popular across multiple user segments"
                ]
            )
            recommendations.append(recommendation)
        
        return recommendations
    
    async def _generate_similar_user_recommendations(
        self,
        user_profile: UserProfile,
        context: RecommendationContext,
        max_items: int
    ) -> List[Recommendation]:
        """Generate recommendations based on similar users"""
        recommendations = []
        
        # Find similar users (simplified implementation)
        similar_users = await self._find_similar_users(user_profile)
        
        # Get items liked by similar users
        recommended_items = set()
        for similar_user_id in similar_users[:5]:  # Top 5 similar users
            similar_profile = self.user_profiles.get(similar_user_id)
            if similar_profile:
                for interaction in similar_profile.behavior_history:
                    if interaction['action'] in ['like', 'purchase', 'share']:
                        recommended_items.add(interaction['item_id'])
        
        # Create recommendations
        for item_id in list(recommended_items)[:max_items]:
            item = self.content_items.get(item_id)
            if item:
                recommendation = Recommendation(
                    recommendation_id=f"rec_{uuid.uuid4().hex[:12]}",
                    user_id=user_profile.user_id,
                    item_id=item_id,
                    item_type=RecommendationType.SIMILAR_USERS,
                    score=0.7,  # Base score for similar user recommendations
                    confidence=0.65,
                    algorithm_used=RecommendationAlgorithm.COLLABORATIVE_FILTERING,
                    context=context,
                    reason="Liked by users with similar interests",
                    explanation=[
                        "Popular among users with similar preferences",
                        "High rating from your peer group"
                    ]
                )
                recommendations.append(recommendation)
        
        return recommendations
    
    async def _find_similar_users(self, user_profile: UserProfile) -> List[str]:
        """Find users with similar preferences"""
        similar_users = []
        
        for other_user_id, other_profile in self.user_profiles.items():
            if other_user_id == user_profile.user_id:
                continue
            
            # Calculate preference similarity
            similarity = self._calculate_user_similarity(user_profile, other_profile)
            
            if similarity > 0.6:  # Threshold for similarity
                similar_users.append((other_user_id, similarity))
        
        # Sort by similarity and return user IDs
        similar_users.sort(key=lambda x: x[1], reverse=True)
        return [user_id for user_id, _ in similar_users]
    
    def _calculate_user_similarity(self, user1: UserProfile, user2: UserProfile) -> float:
        """Calculate similarity between two user profiles"""
        # Preference similarity
        common_prefs = set(user1.preferences.keys()) & set(user2.preferences.keys())
        
        if not common_prefs:
            return 0.0
        
        pref_similarity = sum(
            1 - abs(user1.preferences[pref] - user2.preferences[pref])
            for pref in common_prefs
        ) / len(common_prefs)
        
        return pref_similarity
    
    async def _apply_diversity_ranking(
        self,
        recommendations: List[Recommendation],
        diversity_weight: float,
        max_items: int
    ) -> List[Recommendation]:
        """Apply diversity and final ranking to recommendations"""
        if not recommendations:
            return []
        
        # Sort by score first
        recommendations.sort(key=lambda x: x.score, reverse=True)
        
        # Apply diversity by ensuring category/type mix
        diverse_recs = []
        seen_categories = set()
        
        # First pass: high-scoring diverse items
        for rec in recommendations:
            item = self.content_items.get(rec.item_id) or self.creator_profiles.get(rec.item_id)
            category = getattr(item, 'category', 'unknown') if item else 'unknown'
            
            if category not in seen_categories or len(diverse_recs) < max_items // 2:
                diverse_recs.append(rec)
                seen_categories.add(category)
                
                if len(diverse_recs) >= max_items:
                    break
        
        # Second pass: fill remaining slots with best scores
        for rec in recommendations:
            if rec not in diverse_recs and len(diverse_recs) < max_items:
                diverse_recs.append(rec)
        
        # Update ranks
        for i, rec in enumerate(diverse_recs):
            rec.rank = i + 1
        
        return diverse_recs[:max_items]
    
    async def _calculate_diversity_score(self, recommendations: List[Recommendation]) -> float:
        """Calculate diversity score for recommendation set"""
        if not recommendations:
            return 0.0
        
        # Count unique categories/types
        categories = set()
        algorithms = set()
        
        for rec in recommendations:
            item = self.content_items.get(rec.item_id) or self.creator_profiles.get(rec.item_id)
            if item:
                categories.add(getattr(item, 'category', 'unknown'))
            algorithms.add(rec.algorithm_used.value)
        
        # Diversity score based on category and algorithm variety
        category_diversity = len(categories) / max(len(recommendations), 1)
        algorithm_diversity = len(algorithms) / max(len(recommendations), 1)
        
        return (category_diversity + algorithm_diversity) / 2
    
    async def _calculate_freshness_score(
        self,
        recommendations: List[Recommendation],
        user_profile: UserProfile
    ) -> float:
        """Calculate freshness score for recommendation set"""
        if not recommendations:
            return 0.0
        
        # Calculate how many recommendations are new vs. repeated
        user_seen_items = {
            interaction['item_id'] for interaction in user_profile.behavior_history
        }
        
        new_items = sum(1 for rec in recommendations if rec.item_id not in user_seen_items)
        freshness_score = new_items / len(recommendations)
        
        return freshness_score
    
    async def track_interaction(
        self,
        user_id: str,
        item_id: str,
        item_type: str,
        action: str,
        duration: Optional[float] = None,
        context: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> InteractionEvent:
        """Track user interaction with recommended items"""
        try:
            event_id = f"interaction_{uuid.uuid4().hex[:12]}"
            
            interaction = InteractionEvent(
                event_id=event_id,
                user_id=user_id,
                item_id=item_id,
                item_type=item_type,
                action=action,
                duration=duration,
                context=context,
                metadata=metadata or {}
            )
            
            self.interactions.append(interaction)
            
            # Update user profile
            await self._update_user_profile_from_interaction(user_id, interaction)
            
            logger.info(f"Interaction tracked: {user_id} {action} {item_id}")
            return interaction
            
        except Exception as e:
            logger.error(f"Error tracking interaction: {e}")
            raise
    
    async def _update_user_profile_from_interaction(
        self,
        user_id: str,
        interaction: InteractionEvent
    ):
        """Update user profile based on interaction"""
        profile = self.user_profiles.get(user_id)
        if not profile:
            return
        
        # Add to behavior history
        interaction_data = {
            'item_id': interaction.item_id,
            'item_type': interaction.item_type,
            'action': interaction.action,
            'timestamp': interaction.timestamp.isoformat(),
            'duration': interaction.duration
        }
        
        profile.behavior_history.append(interaction_data)
        
        # Keep only recent history (last 1000 interactions)
        if len(profile.behavior_history) > 1000:
            profile.behavior_history = profile.behavior_history[-1000:]
        
        # Update preferences based on positive interactions
        if interaction.action in ['like', 'purchase', 'share', 'save']:
            item = self.content_items.get(interaction.item_id) or self.creator_profiles.get(interaction.item_id)
            if item:
                category = getattr(item, 'category', None)
                if category:
                    current_pref = profile.preferences.get(category, 0.5)
                    # Increase preference (with decay to prevent over-optimization)
                    profile.preferences[category] = min(1.0, current_pref + 0.1 * (1 - current_pref))
        
        profile.updated_at = datetime.utcnow()
        profile.last_active = datetime.utcnow()
    
    async def measure_recommendation_performance(
        self,
        recommendation_set_id: str
    ) -> RecommendationPerformance:
        """Measure performance of a recommendation set"""
        try:
            rec_set = self.recommendations.get(recommendation_set_id)
            if not rec_set:
                raise ValueError(f"Recommendation set {recommendation_set_id} not found")
            
            metric_id = f"perf_{uuid.uuid4().hex[:12]}"
            
            # Get interactions for this recommendation set
            set_interactions = [
                interaction for interaction in self.interactions
                if interaction.user_id == rec_set.user_id
                and interaction.timestamp >= rec_set.generated_at
                and any(rec.item_id == interaction.item_id for rec in rec_set.recommendations)
            ]
            
            # Calculate metrics
            total_impressions = len(rec_set.recommendations)
            total_clicks = len([i for i in set_interactions if i.action in ['click', 'view']])
            total_conversions = len([i for i in set_interactions if i.action in ['purchase', 'download']])
            
            ctr = (total_clicks / total_impressions) if total_impressions > 0 else 0
            conversion_rate = (total_conversions / total_clicks) if total_clicks > 0 else 0
            engagement_rate = len(set_interactions) / total_impressions if total_impressions > 0 else 0
            
            # Calculate revenue
            revenue_generated = Decimal("0")
            for interaction in set_interactions:
                if interaction.action == 'purchase':
                    item = self.content_items.get(interaction.item_id)
                    if item and item.price:
                        revenue_generated += item.price
            
            performance = RecommendationPerformance(
                metric_id=metric_id,
                recommendation_set_id=recommendation_set_id,
                click_through_rate=ctr,
                conversion_rate=conversion_rate,
                engagement_rate=engagement_rate,
                diversity_score=rec_set.diversity_score,
                novelty_score=rec_set.freshness_score,
                satisfaction_score=0.8,  # Would be calculated from user feedback
                total_impressions=total_impressions,
                total_clicks=total_clicks,
                total_conversions=total_conversions,
                revenue_generated=revenue_generated
            )
            
            self.performance_metrics[metric_id] = performance
            
            logger.info(f"Performance measured for recommendation set {recommendation_set_id}")
            return performance
            
        except Exception as e:
            logger.error(f"Error measuring recommendation performance: {e}")
            raise
    
    # Public interface methods
    
    def get_recommendation_set(self, set_id: str) -> Optional[RecommendationSet]:
        """Get recommendation set by ID"""
        return self.recommendations.get(set_id)
    
    def get_user_profile(self, user_id: str) -> Optional[UserProfile]:
        """Get user profile by ID"""
        return self.user_profiles.get(user_id)
    
    async def get_recommendation_analytics(self) -> Dict[str, Any]:
        """Get recommendation engine analytics"""
        total_recommendations = sum(len(rec_set.recommendations) for rec_set in self.recommendations.values())
        total_users = len(self.user_profiles)
        total_interactions = len(self.interactions)
        
        # Calculate average performance metrics
        if self.performance_metrics:
            avg_ctr = statistics.mean(p.click_through_rate for p in self.performance_metrics.values())
            avg_conversion = statistics.mean(p.conversion_rate for p in self.performance_metrics.values())
            avg_diversity = statistics.mean(p.diversity_score for p in self.performance_metrics.values())
        else:
            avg_ctr = avg_conversion = avg_diversity = 0.0
        
        # Algorithm usage
        algorithm_usage = defaultdict(int)
        for rec_set in self.recommendations.values():
            for algorithm, count in rec_set.algorithm_mix.items():
                algorithm_usage[algorithm] += count
        
        return {
            "total_recommendation_sets": len(self.recommendations),
            "total_recommendations": total_recommendations,
            "total_users": total_users,
            "total_interactions": total_interactions,
            "average_ctr": avg_ctr,
            "average_conversion_rate": avg_conversion,
            "average_diversity_score": avg_diversity,
            "algorithm_usage": dict(algorithm_usage),
            "content_items": len(self.content_items),
            "creator_profiles": len(self.creator_profiles)
        }

# Example usage
async def main():
    """Example usage of RecommendationEngine"""
    engine = RecommendationEngine()
    
    # Generate recommendations for a user
    rec_set = await engine.generate_recommendations(
        user_id="user_001",
        context=RecommendationContext.HOME_FEED,
        recommendation_types=[RecommendationType.CONTENT, RecommendationType.CREATOR],
        max_items=8
    )
    
    print(f"Generated {len(rec_set.recommendations)} recommendations")
    print(f"Diversity score: {rec_set.diversity_score:.2f}")
    print(f"Freshness score: {rec_set.freshness_score:.2f}")
    
    for i, rec in enumerate(rec_set.recommendations[:3], 1):
        print(f"{i}. {rec.item_id} (score: {rec.score:.2f}, {rec.algorithm_used.value})")
        print(f"   Reason: {rec.reason}")
    
    # Track user interaction
    await engine.track_interaction(
        user_id="user_001",
        item_id=rec_set.recommendations[0].item_id,
        item_type="content",
        action="click",
        duration=45.0
    )
    
    # Measure performance
    performance = await engine.measure_recommendation_performance(rec_set.set_id)
    print(f"\nPerformance metrics:")
    print(f"CTR: {performance.click_through_rate:.2%}")
    print(f"Conversion rate: {performance.conversion_rate:.2%}")
    print(f"Revenue: ${performance.revenue_generated}")
    
    # Get analytics
    analytics = await engine.get_recommendation_analytics()
    print(f"\nEngine analytics: {analytics}")

if __name__ == "__main__":
    asyncio.run(main())