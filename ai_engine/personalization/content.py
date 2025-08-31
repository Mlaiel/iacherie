"""Advanced Multi-Format Content Personalization & Recommendation Engine

Ultra-sophisticated content analysis, matching, and personalization system designed
for multi-format content creators (musicians, bloggers, photographers, influencers, comedians).

Business Logic Integration:
Content Upload → AI Analysis & Feature Extraction → Rights Fingerprinting → 
User Behavior Analysis → Personalized Matching → Collaboration Discovery →
SEO Optimization → Multi-Platform Distribution → Monetization Tracking

Advanced Features:
- Multi-Modal Content Analysis (Audio, Video, Image, Text)
- Semantic Content Understanding & Embedding
- Real-Time Trending Analysis & Virality Prediction
- Intelligent Creator-Brand-Influencer Matching
- Advanced SEO Content Optimization
- Multi-Platform Distribution Strategy
- Revenue Optimization & Monetization Intelligence
- Rights Protection Integration
- Social Graph-Based Recommendations
- Contextual & Temporal Personalization

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.

⚠️ STRICT COPYRIGHT WARNING ⚠️
This code is the intellectual property of Fahed Mlaiel (mlaiel@live.de).
ANY unauthorized use, reproduction, or distribution is STRICTLY PROHIBITED.
Legal action will be taken against violators under German and international law.
Contact mlaiel@live.de for licensing inquiries.

Team Specialists:
- Lead IA Developer: Fahed Mlaiel (mlaiel@live.de)
- Backend Senior Engineer: Advanced microservices architecture
- ML Engineer: Deep learning & personalization algorithms  
- Database Administrator: High-performance data optimization
- Security Expert: Enterprise-grade protection systems
- Microservices Architect: Scalable distributed systems
- Audio Processing Specialist: Advanced audio AI algorithms
- DevOps Engineer: Production-ready infrastructure
- IA Prompt Engineer: Optimized AI model interactions
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple, Union, Set, Generator
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity, euclidean_distances
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import PCA, NMF
from sklearn.cluster import KMeans, DBSCAN
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
import json
import uuid
import re
import hashlib
from collections import Counter, defaultdict
import networkx as nx
from textblob import TextBlob
import redis
import pickle

from .core import UserProfile, ContentType, PersonalizationType, PersonalizationEngine
from .exceptions import RecommendationError, ContentFilteringError, ContentAnalysisError


class RecommendationStrategy(Enum):
    """Content recommendation strategies"""
    SIMILAR_CONTENT = "similar_content"
    TRENDING = "trending"
    COLLABORATIVE = "collaborative"
    NOVELTY = "novelty"
    EXPLORATION = "exploration"
    SOCIAL = "social"
    QUALITY_BASED = "quality_based"
    TIME_BASED = "time_based"


class ContentMatchingType(Enum):
    """Content matching algorithms"""
    SEMANTIC_SIMILARITY = "semantic_similarity"
    GENRE_MATCHING = "genre_matching"
    CREATOR_SIMILARITY = "creator_similarity"
    FORMAT_MATCHING = "format_matching"
    TEMPORAL_MATCHING = "temporal_matching"
    ENGAGEMENT_BASED = "engagement_based"


@dataclass
class ContentItem:
    """Represents a piece of content for recommendation"""
    
    content_id: str
    title: str
    description: str
    content_type: ContentType
    genre: str
    creator_id: str
    creator_name: str
    
    # Content features
    duration: Optional[float] = None  # in seconds
    quality_score: float = 0.0
    complexity_level: float = 0.5
    novelty_score: float = 0.5
    
    # Engagement metrics
    view_count: int = 0
    like_count: int = 0
    share_count: int = 0
    comment_count: int = 0
    engagement_rate: float = 0.0
    
    # Temporal data
    created_at: datetime = field(default_factory=datetime.utcnow)
    published_at: Optional[datetime] = None
    trending_score: float = 0.0
    
    # Content metadata
    tags: List[str] = field(default_factory=list)
    categories: List[str] = field(default_factory=list)
    language: str = "en"
    region: Optional[str] = None
    
    # AI-generated features
    content_embedding: Optional[np.ndarray] = None
    semantic_tags: List[str] = field(default_factory=list)
    mood: Optional[str] = None
    style: Optional[str] = None
    
    # Collaboration metadata
    collaboration_type: Optional[str] = None
    skill_requirements: List[str] = field(default_factory=list)
    collaboration_openness: bool = False


@dataclass
class RecommendationResult:
    """Result of content recommendation"""
    
    content_item: ContentItem
    relevance_score: float
    confidence_score: float
    recommendation_strategy: RecommendationStrategy
    matching_factors: List[str]
    
    # Explanation
    explanation: str
    personalization_factors: Dict[str, float]
    
    # Metadata
    generated_at: datetime = field(default_factory=datetime.utcnow)
    recommendation_id: str = field(default_factory=lambda: str(uuid.uuid4()))


class ContentRecommender:
    """
    Advanced content recommendation engine with multiple strategies.
    
    Features:
    - Multi-strategy recommendations
    - Real-time personalization
    - Content diversity optimization
    - Exploration vs exploitation balance
    - Collaborative filtering integration
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Recommendation models
        self.models = self._initialize_models()
        
        # Content database (in production, this would be a proper database)
        self.content_database = {}
        self.content_embeddings = {}
        
        # Performance tracking
        self.recommendation_stats = {
            'total_recommendations': 0,
            'successful_engagements': 0,
            'avg_relevance_score': 0.0,
            'strategy_performance': {}
        }
    
    def _initialize_models(self) -> Dict[str, Any]:
        """Initialize recommendation models"""
        return {
            'content_similarity': TfidfVectorizer(max_features=5000, stop_words='english'),
            'collaborative_filtering': {'initialized': True},
            'trend_detector': {'initialized': True},
            'diversity_optimizer': {'initialized': True}
        }
    
    async def recommend_content(
        self,
        user_profile: UserProfile,
        num_recommendations: int = 20,
        strategies: Optional[List[RecommendationStrategy]] = None,
        content_type_filter: Optional[ContentType] = None,
        exclude_seen: bool = True
    ) -> List[RecommendationResult]:
        """
        Generate personalized content recommendations.
        
        Args:
            user_profile: User profile for personalization
            num_recommendations: Number of recommendations to generate
            strategies: Specific strategies to use (if None, uses optimal mix)
            content_type_filter: Filter by content type
            exclude_seen: Whether to exclude previously seen content
            
        Returns:
            List of personalized recommendations with scores and explanations
        """
        try:
            # Determine optimal strategies if not specified
            if strategies is None:
                strategies = self._select_optimal_strategies(user_profile)
            
            # Get candidate content
            candidate_content = await self._get_candidate_content(
                user_profile, content_type_filter, exclude_seen
            )
            
            if not candidate_content:
                raise RecommendationError(
                    "No candidate content available for recommendations",
                    user_id=user_profile.user_id
                )
            
            # Generate recommendations using different strategies
            all_recommendations = []
            
            for strategy in strategies:
                strategy_recs = await self._apply_recommendation_strategy(
                    strategy, user_profile, candidate_content
                )
                all_recommendations.extend(strategy_recs)
            
            # Remove duplicates and rank
            unique_recommendations = self._deduplicate_recommendations(all_recommendations)
            
            # Apply diversity optimization
            diverse_recommendations = await self._optimize_diversity(
                unique_recommendations, user_profile
            )
            
            # Final ranking and filtering
            final_recommendations = await self._final_ranking(
                diverse_recommendations, user_profile
            )
            
            # Limit to requested number
            final_recommendations = final_recommendations[:num_recommendations]
            
            # Update statistics
            self._update_recommendation_stats(final_recommendations, strategies)
            
            return final_recommendations
            
        except Exception as e:
            self.logger.error(f"Content recommendation error: {e}")
            raise RecommendationError(f"Failed to generate recommendations: {e}")
    
    async def _apply_recommendation_strategy(
        self,
        strategy: RecommendationStrategy,
        user_profile: UserProfile,
        candidate_content: List[ContentItem]
    ) -> List[RecommendationResult]:
        """Apply a specific recommendation strategy"""
        
        if strategy == RecommendationStrategy.SIMILAR_CONTENT:
            return await self._similar_content_recommendations(user_profile, candidate_content)
        elif strategy == RecommendationStrategy.COLLABORATIVE:
            return await self._collaborative_recommendations(user_profile, candidate_content)
        elif strategy == RecommendationStrategy.TRENDING:
            return await self._trending_recommendations(user_profile, candidate_content)
        elif strategy == RecommendationStrategy.NOVELTY:
            return await self._novelty_recommendations(user_profile, candidate_content)
        elif strategy == RecommendationStrategy.EXPLORATION:
            return await self._exploration_recommendations(user_profile, candidate_content)
        elif strategy == RecommendationStrategy.SOCIAL:
            return await self._social_recommendations(user_profile, candidate_content)
        elif strategy == RecommendationStrategy.QUALITY_BASED:
            return await self._quality_based_recommendations(user_profile, candidate_content)
        elif strategy == RecommendationStrategy.TIME_BASED:
            return await self._time_based_recommendations(user_profile, candidate_content)
        else:
            return []
    
    async def _similar_content_recommendations(
        self,
        user_profile: UserProfile,
        candidate_content: List[ContentItem]
    ) -> List[RecommendationResult]:
        """Generate recommendations based on content similarity"""
        
        recommendations = []
        
        # Get user's preferred content features
        user_genres = user_profile.preferred_genres
        user_formats = user_profile.preferred_formats
        
        for content in candidate_content:
            relevance_score = 0.0
            matching_factors = []
            personalization_factors = {}
            
            # Genre matching
            if content.genre in user_genres:
                genre_score = user_genres[content.genre]
                relevance_score += genre_score * 0.4
                matching_factors.append(f"Genre match: {content.genre}")
                personalization_factors['genre_match'] = genre_score
            
            # Format matching
            if content.content_type in user_formats:
                format_score = user_formats[content.content_type]
                relevance_score += format_score * 0.3
                matching_factors.append(f"Format match: {content.content_type.value}")
                personalization_factors['format_match'] = format_score
            
            # Quality alignment
            quality_diff = abs(content.quality_score - user_profile.content_sophistication)
            quality_match = 1.0 - quality_diff
            relevance_score += quality_match * 0.2
            personalization_factors['quality_alignment'] = quality_match
            
            # Complexity alignment
            complexity_diff = abs(content.complexity_level - user_profile.content_sophistication)
            complexity_match = 1.0 - complexity_diff
            relevance_score += complexity_match * 0.1
            personalization_factors['complexity_alignment'] = complexity_match
            
            if relevance_score > 0.3:  # Minimum threshold
                explanation = f"Recommended based on your preferences for {content.genre} content"
                if matching_factors:
                    explanation += f". Matches: {', '.join(matching_factors[:2])}"
                
                recommendation = RecommendationResult(
                    content_item=content,
                    relevance_score=relevance_score,
                    confidence_score=min(relevance_score * 1.2, 1.0),
                    recommendation_strategy=RecommendationStrategy.SIMILAR_CONTENT,
                    matching_factors=matching_factors,
                    explanation=explanation,
                    personalization_factors=personalization_factors
                )
                recommendations.append(recommendation)
        
        return recommendations
    
    async def _collaborative_recommendations(
        self,
        user_profile: UserProfile,
        candidate_content: List[ContentItem]
    ) -> List[RecommendationResult]:
        """Generate collaborative filtering recommendations"""
        
        recommendations = []
        
        # Find similar users (simplified - in production would use proper CF)
        similar_users = await self._find_similar_users(user_profile)
        
        # Get content liked by similar users
        similar_user_content = await self._get_similar_user_content(similar_users)
        
        for content in candidate_content:
            if content.content_id in similar_user_content:
                similarity_scores = similar_user_content[content.content_id]
                
                # Calculate relevance based on similar user preferences
                relevance_score = sum(similarity_scores) / len(similarity_scores)
                
                explanation = f"Users with similar tastes also liked this {content.content_type.value}"
                
                recommendation = RecommendationResult(
                    content_item=content,
                    relevance_score=relevance_score,
                    confidence_score=relevance_score * 0.9,  # CF has slightly lower confidence
                    recommendation_strategy=RecommendationStrategy.COLLABORATIVE,
                    matching_factors=[f"Liked by {len(similarity_scores)} similar users"],
                    explanation=explanation,
                    personalization_factors={'collaborative_score': relevance_score}
                )
                recommendations.append(recommendation)
        
        return recommendations
    
    async def _trending_recommendations(
        self,
        user_profile: UserProfile,
        candidate_content: List[ContentItem]
    ) -> List[RecommendationResult]:
        """Generate trending content recommendations"""
        
        recommendations = []
        
        # Sort by trending score
        trending_content = sorted(
            candidate_content,
            key=lambda x: x.trending_score,
            reverse=True
        )
        
        for content in trending_content[:50]:  # Top 50 trending
            # Adjust relevance based on user preferences
            base_relevance = content.trending_score
            
            # Boost if matches user preferences
            preference_boost = 0.0
            if content.genre in user_profile.preferred_genres:
                preference_boost += user_profile.preferred_genres[content.genre] * 0.3
            
            if content.content_type in user_profile.preferred_formats:
                preference_boost += user_profile.preferred_formats[content.content_type] * 0.2
            
            relevance_score = min(base_relevance + preference_boost, 1.0)
            
            if relevance_score > 0.4:
                explanation = f"Trending {content.content_type.value} in {content.genre}"
                if preference_boost > 0:
                    explanation += " (matches your preferences)"
                
                recommendation = RecommendationResult(
                    content_item=content,
                    relevance_score=relevance_score,
                    confidence_score=base_relevance,
                    recommendation_strategy=RecommendationStrategy.TRENDING,
                    matching_factors=[f"Trending score: {content.trending_score:.2f}"],
                    explanation=explanation,
                    personalization_factors={
                        'trending_score': base_relevance,
                        'preference_boost': preference_boost
                    }
                )
                recommendations.append(recommendation)
        
        return recommendations
    
    async def _novelty_recommendations(
        self,
        user_profile: UserProfile,
        candidate_content: List[ContentItem]
    ) -> List[RecommendationResult]:
        """Generate novelty-based recommendations for exploration"""
        
        recommendations = []
        
        # Get user's exploration tendency
        exploration_factor = user_profile.exploration_tendency
        
        if exploration_factor < 0.3:
            return recommendations  # User prefers familiar content
        
        # Find content different from user's usual preferences
        for content in candidate_content:
            novelty_score = content.novelty_score
            
            # Check if content is outside user's usual preferences
            genre_novelty = 0.0
            if content.genre not in user_profile.preferred_genres:
                genre_novelty = 0.5
            elif user_profile.preferred_genres[content.genre] < 0.3:
                genre_novelty = 0.7
            
            format_novelty = 0.0
            if content.content_type not in user_profile.preferred_formats:
                format_novelty = 0.4
            elif user_profile.preferred_formats[content.content_type] < 0.3:
                format_novelty = 0.6
            
            combined_novelty = (novelty_score + genre_novelty + format_novelty) / 3.0
            
            # Adjust by user's exploration tendency
            relevance_score = combined_novelty * exploration_factor
            
            if relevance_score > 0.4:
                explanation = f"Something different: {content.content_type.value} in {content.genre}"
                
                recommendation = RecommendationResult(
                    content_item=content,
                    relevance_score=relevance_score,
                    confidence_score=relevance_score * 0.8,  # Lower confidence for novel content
                    recommendation_strategy=RecommendationStrategy.NOVELTY,
                    matching_factors=[f"Novel content (novelty: {combined_novelty:.2f})"],
                    explanation=explanation,
                    personalization_factors={
                        'novelty_score': combined_novelty,
                        'exploration_factor': exploration_factor
                    }
                )
                recommendations.append(recommendation)
        
        return recommendations
    
    def _select_optimal_strategies(self, user_profile: UserProfile) -> List[RecommendationStrategy]:
        """Select optimal recommendation strategies based on user profile"""
        
        strategies = []
        
        # Always include similar content
        strategies.append(RecommendationStrategy.SIMILAR_CONTENT)
        
        # Add collaborative if user has enough interactions
        if len(user_profile.interaction_history) > 20:
            strategies.append(RecommendationStrategy.COLLABORATIVE)
        
        # Add trending for active users
        activity_level = len(user_profile.interaction_history) / 30  # Simplified activity
        if activity_level > 0.5:
            strategies.append(RecommendationStrategy.TRENDING)
        
        # Add novelty for exploratory users
        if user_profile.exploration_tendency > 0.5:
            strategies.append(RecommendationStrategy.NOVELTY)
        
        # Add social for users with social preferences
        social_actions = sum(
            1 for i in user_profile.interaction_history
            if i.get('action') in ['share', 'comment', 'collaborate']
        )
        if social_actions > 5:
            strategies.append(RecommendationStrategy.SOCIAL)
        
        # Add quality-based for quality-focused users
        if user_profile.content_sophistication > 0.7:
            strategies.append(RecommendationStrategy.QUALITY_BASED)
        
        return strategies
    
    def _deduplicate_recommendations(
        self,
        recommendations: List[RecommendationResult]
    ) -> List[RecommendationResult]:
        """Remove duplicate recommendations and combine scores"""
        
        seen_content = {}
        deduplicated = []
        
        for rec in recommendations:
            content_id = rec.content_item.content_id
            
            if content_id not in seen_content:
                seen_content[content_id] = rec
                deduplicated.append(rec)
            else:
                # Combine scores for duplicates (take the higher one)
                existing_rec = seen_content[content_id]
                if rec.relevance_score > existing_rec.relevance_score:
                    existing_rec.relevance_score = rec.relevance_score
                    existing_rec.confidence_score = max(
                        existing_rec.confidence_score, rec.confidence_score
                    )
                    # Combine strategies
                    if rec.recommendation_strategy not in [existing_rec.recommendation_strategy]:
                        existing_rec.matching_factors.extend(rec.matching_factors)
        
        return deduplicated


class ContentMatcher:
    """
    Matches content to user preferences using various algorithms.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.matching_algorithms = {
            ContentMatchingType.SEMANTIC_SIMILARITY: self._semantic_matching,
            ContentMatchingType.GENRE_MATCHING: self._genre_matching,
            ContentMatchingType.CREATOR_SIMILARITY: self._creator_matching,
            ContentMatchingType.FORMAT_MATCHING: self._format_matching,
            ContentMatchingType.TEMPORAL_MATCHING: self._temporal_matching,
            ContentMatchingType.ENGAGEMENT_BASED: self._engagement_matching
        }
    
    async def match_content(
        self,
        user_profile: UserProfile,
        content_items: List[ContentItem],
        matching_types: List[ContentMatchingType] = None
    ) -> List[Tuple[ContentItem, Dict[str, float]]]:
        """
        Match content to user profile using specified algorithms.
        
        Args:
            user_profile: User profile for matching
            content_items: Content items to match
            matching_types: Types of matching to perform
            
        Returns:
            List of (content, scores) tuples
        """
        try:
            if matching_types is None:
                matching_types = list(ContentMatchingType)
            
            matched_content = []
            
            for content in content_items:
                match_scores = {}
                
                # Apply each matching algorithm
                for matching_type in matching_types:
                    if matching_type in self.matching_algorithms:
                        score = await self.matching_algorithms[matching_type](
                            user_profile, content
                        )
                        match_scores[matching_type.value] = score
                
                # Calculate overall match score
                overall_score = sum(match_scores.values()) / len(match_scores)
                match_scores['overall'] = overall_score
                
                if overall_score > 0.3:  # Minimum match threshold
                    matched_content.append((content, match_scores))
            
            # Sort by overall match score
            matched_content.sort(key=lambda x: x[1]['overall'], reverse=True)
            
            return matched_content
            
        except Exception as e:
            self.logger.error(f"Content matching error: {e}")
            raise ContentFilteringError(f"Content matching failed: {e}")
    
    async def _semantic_matching(
        self,
        user_profile: UserProfile,
        content: ContentItem
    ) -> float:
        """Match content based on semantic similarity"""
        
        # Simplified semantic matching
        # In production, this would use proper NLP models
        
        user_interests = list(user_profile.preferred_genres.keys())
        content_tags = content.tags + content.semantic_tags
        
        if not user_interests or not content_tags:
            return 0.0
        
        # Calculate tag overlap
        common_tags = set(user_interests) & set(content_tags)
        overlap_score = len(common_tags) / max(len(user_interests), len(content_tags))
        
        # Use content embedding if available
        if (content.content_embedding is not None and 
            user_profile.user_embedding is not None):
            
            embedding_similarity = cosine_similarity(
                user_profile.user_embedding.reshape(1, -1),
                content.content_embedding.reshape(1, -1)
            )[0][0]
            
            # Combine overlap and embedding similarity
            return (overlap_score + embedding_similarity) / 2.0
        
        return overlap_score
    
    async def _genre_matching(
        self,
        user_profile: UserProfile,
        content: ContentItem
    ) -> float:
        """Match content based on genre preferences"""
        
        return user_profile.preferred_genres.get(content.genre, 0.0)
    
    async def _creator_matching(
        self,
        user_profile: UserProfile,
        content: ContentItem
    ) -> float:
        """Match content based on creator preferences"""
        
        # Check if user has interacted with this creator before
        creator_interactions = [
            i for i in user_profile.interaction_history
            if i.get('creator_id') == content.creator_id
        ]
        
        if not creator_interactions:
            return 0.0
        
        # Calculate average engagement with this creator
        positive_interactions = sum(
            1 for i in creator_interactions
            if i.get('action') in ['like', 'share', 'save', 'follow']
        )
        
        return positive_interactions / len(creator_interactions)
    
    async def _format_matching(
        self,
        user_profile: UserProfile,
        content: ContentItem
    ) -> float:
        """Match content based on format preferences"""
        
        return user_profile.preferred_formats.get(content.content_type, 0.0)
    
    async def _temporal_matching(
        self,
        user_profile: UserProfile,
        content: ContentItem
    ) -> float:
        """Match content based on temporal patterns"""
        
        # Check if content timing matches user's active periods
        content_hour = content.created_at.hour
        user_patterns = user_profile.session_patterns
        
        if 'peak_hours' in user_patterns:
            peak_hours = user_patterns['peak_hours']
            if content_hour in peak_hours:
                return 0.8
            elif abs(content_hour - min(peak_hours)) <= 2:
                return 0.5
        
        return 0.3  # Default temporal score
    
    async def _engagement_matching(
        self,
        user_profile: UserProfile,
        content: ContentItem
    ) -> float:
        """Match content based on engagement patterns"""
        
        # Normalize engagement metrics
        max_views = 1000000  # Simplified normalization
        max_likes = 50000
        max_shares = 10000
        
        normalized_engagement = (
            (content.view_count / max_views) * 0.3 +
            (content.like_count / max_likes) * 0.4 +
            (content.share_count / max_shares) * 0.3
        )
        
        return min(normalized_engagement, 1.0)


class PersonalizedContentGenerator:
    """
    Generates personalized content adaptations and variations.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    async def generate_personalized_version(
        self,
        content: ContentItem,
        user_profile: UserProfile
    ) -> ContentItem:
        """
        Generate a personalized version of content for a specific user.
        
        Args:
            content: Original content item
            user_profile: User profile for personalization
            
        Returns:
            Personalized content version
        """
        try:
            personalized_content = ContentItem(
                content_id=f"{content.content_id}_personalized_{user_profile.user_id}",
                title=await self._personalize_title(content.title, user_profile),
                description=await self._personalize_description(content.description, user_profile),
                content_type=content.content_type,
                genre=content.genre,
                creator_id=content.creator_id,
                creator_name=content.creator_name,
                duration=content.duration,
                quality_score=content.quality_score,
                complexity_level=self._adjust_complexity(content.complexity_level, user_profile),
                novelty_score=content.novelty_score,
                view_count=content.view_count,
                like_count=content.like_count,
                share_count=content.share_count,
                comment_count=content.comment_count,
                engagement_rate=content.engagement_rate,
                created_at=content.created_at,
                published_at=content.published_at,
                trending_score=content.trending_score,
                tags=await self._personalize_tags(content.tags, user_profile),
                categories=content.categories,
                language=user_profile.language or content.language,
                region=user_profile.location or content.region,
                content_embedding=content.content_embedding,
                semantic_tags=content.semantic_tags,
                mood=content.mood,
                style=content.style,
                collaboration_type=content.collaboration_type,
                skill_requirements=content.skill_requirements,
                collaboration_openness=content.collaboration_openness
            )
            
            return personalized_content
            
        except Exception as e:
            self.logger.error(f"Personalized content generation error: {e}")
            return content  # Return original if personalization fails
    
    async def _personalize_title(self, title: str, user_profile: UserProfile) -> str:
        """Personalize content title based on user preferences"""
        
        # Simple personalization - in production would use NLP models
        personalized_title = title
        
        # Add user-relevant context if appropriate
        if user_profile.professional_goals:
            primary_goal = user_profile.professional_goals[0]
            if any(keyword in title.lower() for keyword in ['tutorial', 'guide', 'how to']):
                personalized_title = f"{title} (For {primary_goal})"
        
        return personalized_title
    
    async def _personalize_description(self, description: str, user_profile: UserProfile) -> str:
        """Personalize content description"""
        
        # Add personalized context
        personalized_desc = description
        
        # Add skill level context
        if user_profile.skill_level and 'beginner' in user_profile.skill_level.lower():
            personalized_desc += "\n\nPerfect for beginners - includes step-by-step guidance."
        elif 'advanced' in user_profile.skill_level.lower():
            personalized_desc += "\n\nAdvanced techniques for experienced creators."
        
        return personalized_desc
    
    def _adjust_complexity(self, original_complexity: float, user_profile: UserProfile) -> float:
        """Adjust content complexity based on user sophistication"""
        
        user_sophistication = user_profile.content_sophistication
        
        # Gradually adjust complexity towards user preference
        adjustment_factor = 0.3  # How much to adjust
        adjusted_complexity = (
            original_complexity * (1 - adjustment_factor) +
            user_sophistication * adjustment_factor
        )
        
        return max(0.0, min(1.0, adjusted_complexity))
    
    async def _personalize_tags(self, original_tags: List[str], user_profile: UserProfile) -> List[str]:
        """Personalize content tags based on user interests"""
        
        personalized_tags = original_tags.copy()
        
        # Add relevant tags based on user preferences
        user_interests = list(user_profile.preferred_genres.keys())
        
        for interest in user_interests[:3]:  # Add up to 3 relevant tags
            if interest not in personalized_tags:
                personalized_tags.append(interest)
        
        return personalized_tags


class ContentAdaptationEngine:
    """
    Adapts content presentation and delivery based on user context.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    async def adapt_content_presentation(
        self,
        content: ContentItem,
        user_profile: UserProfile,
        delivery_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Adapt content presentation for specific user and context.
        
        Args:
            content: Content to adapt
            user_profile: User profile for adaptation
            delivery_context: Context information (device, time, etc.)
            
        Returns:
            Adapted content presentation parameters
        """
        try:
            adaptation = {
                'content_id': content.content_id,
                'user_id': user_profile.user_id,
                'adaptations_applied': [],
                'presentation_params': {}
            }
            
            # Device-based adaptations
            if 'device_type' in delivery_context:
                device_adaptations = self._adapt_for_device(
                    content, delivery_context['device_type']
                )
                adaptation['presentation_params'].update(device_adaptations)
                adaptation['adaptations_applied'].append('device_optimization')
            
            # Time-based adaptations
            if 'current_time' in delivery_context:
                time_adaptations = self._adapt_for_time(
                    content, user_profile, delivery_context['current_time']
                )
                adaptation['presentation_params'].update(time_adaptations)
                adaptation['adaptations_applied'].append('temporal_optimization')
            
            # Context-based adaptations
            if 'user_context' in delivery_context:
                context_adaptations = self._adapt_for_context(
                    content, user_profile, delivery_context['user_context']
                )
                adaptation['presentation_params'].update(context_adaptations)
                adaptation['adaptations_applied'].append('contextual_optimization')
            
            # Accessibility adaptations
            accessibility_adaptations = self._adapt_for_accessibility(
                content, user_profile
            )
            adaptation['presentation_params'].update(accessibility_adaptations)
            adaptation['adaptations_applied'].append('accessibility_optimization')
            
            return adaptation
            
        except Exception as e:
            self.logger.error(f"Content adaptation error: {e}")
            return {'error': str(e)}
    
    def _adapt_for_device(self, content: ContentItem, device_type: str) -> Dict[str, Any]:
        """Adapt content for specific device type"""
        
        adaptations = {}
        
        if device_type == 'mobile':
            adaptations.update({
                'thumbnail_size': 'small',
                'description_length': 'short',
                'autoplay': False,
                'quality': 'adaptive'
            })
        elif device_type == 'tablet':
            adaptations.update({
                'thumbnail_size': 'medium',
                'description_length': 'medium',
                'autoplay': True,
                'quality': 'high'
            })
        elif device_type == 'desktop':
            adaptations.update({
                'thumbnail_size': 'large',
                'description_length': 'full',
                'autoplay': True,
                'quality': 'highest'
            })
        
        return adaptations
    
    def _adapt_for_time(
        self,
        content: ContentItem,
        user_profile: UserProfile,
        current_time: datetime
    ) -> Dict[str, Any]:
        """Adapt content based on time of day and user patterns"""
        
        adaptations = {}
        hour = current_time.hour
        
        # Morning adaptations (6-12)
        if 6 <= hour < 12:
            adaptations.update({
                'energy_level': 'high',
                'content_density': 'high',
                'recommended_duration': 'medium'
            })
        # Afternoon adaptations (12-18)
        elif 12 <= hour < 18:
            adaptations.update({
                'energy_level': 'medium',
                'content_density': 'medium',
                'recommended_duration': 'long'
            })
        # Evening adaptations (18-22)
        elif 18 <= hour < 22:
            adaptations.update({
                'energy_level': 'medium',
                'content_density': 'relaxed',
                'recommended_duration': 'variable'
            })
        # Night adaptations (22-6)
        else:
            adaptations.update({
                'energy_level': 'low',
                'content_density': 'light',
                'recommended_duration': 'short'
            })
        
        return adaptations
    
    def _adapt_for_context(
        self,
        content: ContentItem,
        user_profile: UserProfile,
        user_context: str
    ) -> Dict[str, Any]:
        """Adapt content based on user's current context"""
        
        adaptations = {}
        
        if user_context == 'commuting':
            adaptations.update({
                'audio_emphasis': True,
                'visual_complexity': 'low',
                'interaction_requirements': 'minimal'
            })
        elif user_context == 'work_break':
            adaptations.update({
                'duration_limit': 300,  # 5 minutes max
                'energy_boost': True,
                'distraction_level': 'low'
            })
        elif user_context == 'focused_learning':
            adaptations.update({
                'depth_level': 'high',
                'interaction_opportunities': 'many',
                'note_taking_support': True
            })
        elif user_context == 'casual_browsing':
            adaptations.update({
                'engagement_threshold': 'low',
                'variety': 'high',
                'discovery_mode': True
            })
        
        return adaptations
    
    def _adapt_for_accessibility(
        self,
        content: ContentItem,
        user_profile: UserProfile
    ) -> Dict[str, Any]:
        """Adapt content for accessibility needs"""
        
        adaptations = {}
        
        # Default accessibility features
        adaptations.update({
            'captions_available': True,
            'audio_description': content.content_type == ContentType.VIDEO,
            'high_contrast_option': True,
            'keyboard_navigation': True,
            'screen_reader_compatible': True
        })
        
        # Language adaptations
        if user_profile.language and user_profile.language != 'en':
            adaptations.update({
                'translation_available': True,
                'preferred_language': user_profile.language
            })
        
        return adaptations


class ContentRankingEngine:
    """
    Ranks content based on multiple factors and user preferences.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Ranking weights
        self.ranking_weights = {
            'relevance': 0.35,
            'quality': 0.25,
            'freshness': 0.15,
            'engagement': 0.15,
            'diversity': 0.10
        }
    
    async def rank_content(
        self,
        content_items: List[ContentItem],
        user_profile: UserProfile,
        ranking_context: Optional[Dict[str, Any]] = None
    ) -> List[Tuple[ContentItem, float]]:
        """
        Rank content items based on multiple factors.
        
        Args:
            content_items: Content to rank
            user_profile: User profile for personalization
            ranking_context: Additional context for ranking
            
        Returns:
            List of (content, score) tuples sorted by rank
        """
        try:
            ranked_content = []
            
            for content in content_items:
                # Calculate individual scores
                relevance_score = await self._calculate_relevance_score(content, user_profile)
                quality_score = self._calculate_quality_score(content)
                freshness_score = self._calculate_freshness_score(content)
                engagement_score = self._calculate_engagement_score(content)
                diversity_score = await self._calculate_diversity_score(
                    content, content_items, user_profile
                )
                
                # Calculate weighted final score
                final_score = (
                    relevance_score * self.ranking_weights['relevance'] +
                    quality_score * self.ranking_weights['quality'] +
                    freshness_score * self.ranking_weights['freshness'] +
                    engagement_score * self.ranking_weights['engagement'] +
                    diversity_score * self.ranking_weights['diversity']
                )
                
                ranked_content.append((content, final_score))
            
            # Sort by final score
            ranked_content.sort(key=lambda x: x[1], reverse=True)
            
            return ranked_content
            
        except Exception as e:
            self.logger.error(f"Content ranking error: {e}")
            raise ContentFilteringError(f"Content ranking failed: {e}")
    
    async def _calculate_relevance_score(
        self,
        content: ContentItem,
        user_profile: UserProfile
    ) -> float:
        """Calculate content relevance to user"""
        
        relevance = 0.0
        
        # Genre relevance
        if content.genre in user_profile.preferred_genres:
            relevance += user_profile.preferred_genres[content.genre] * 0.4
        
        # Format relevance
        if content.content_type in user_profile.preferred_formats:
            relevance += user_profile.preferred_formats[content.content_type] * 0.3
        
        # Complexity alignment
        complexity_diff = abs(content.complexity_level - user_profile.content_sophistication)
        complexity_score = 1.0 - complexity_diff
        relevance += complexity_score * 0.3
        
        return min(relevance, 1.0)
    
    def _calculate_quality_score(self, content: ContentItem) -> float:
        """Calculate content quality score"""
        return content.quality_score
    
    def _calculate_freshness_score(self, content: ContentItem) -> float:
        """Calculate content freshness score"""
        
        if not content.published_at:
            return 0.5  # Default for content without publish date
        
        days_old = (datetime.utcnow() - content.published_at).days
        
        # Freshness decreases over time
        if days_old <= 1:
            return 1.0
        elif days_old <= 7:
            return 0.8
        elif days_old <= 30:
            return 0.6
        elif days_old <= 90:
            return 0.4
        else:
            return 0.2
    
    def _calculate_engagement_score(self, content: ContentItem) -> float:
        """Calculate content engagement score"""
        
        # Normalize engagement metrics
        # In production, these would be based on platform statistics
        max_views = 1000000
        max_likes = 50000
        max_shares = 10000
        max_comments = 5000
        
        view_score = min(content.view_count / max_views, 1.0)
        like_score = min(content.like_count / max_likes, 1.0)
        share_score = min(content.share_count / max_shares, 1.0)
        comment_score = min(content.comment_count / max_comments, 1.0)
        
        # Weighted engagement score
        engagement_score = (
            view_score * 0.2 +
            like_score * 0.3 +
            share_score * 0.3 +
            comment_score * 0.2
        )
        
        return engagement_score
    
    async def _calculate_diversity_score(
        self,
        content: ContentItem,
        all_content: List[ContentItem],
        user_profile: UserProfile
    ) -> float:
        """Calculate diversity score to avoid too similar content"""
        
        # Simple diversity calculation based on genre distribution
        user_genres = list(user_profile.preferred_genres.keys())
        
        if not user_genres:
            return 0.5  # Default diversity
        
        # Check how different this content is from user's typical preferences
        if content.genre not in user_genres:
            return 0.8  # High diversity for new genres
        else:
            genre_preference = user_profile.preferred_genres[content.genre]
            # Lower diversity score for highly preferred genres
            return 1.0 - (genre_preference * 0.5)


class ContentFilteringEngine:
    """
    Filters content based on various criteria and user preferences.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    async def filter_content(
        self,
        content_items: List[ContentItem],
        user_profile: UserProfile,
        filter_criteria: Dict[str, Any]
    ) -> List[ContentItem]:
        """
        Filter content based on criteria and user preferences.
        
        Args:
            content_items: Content to filter
            user_profile: User profile for personalized filtering
            filter_criteria: Filtering criteria
            
        Returns:
            Filtered content list
        """
        try:
            filtered_content = content_items.copy()
            
            # Apply each filter
            if 'content_types' in filter_criteria:
                filtered_content = self._filter_by_content_type(
                    filtered_content, filter_criteria['content_types']
                )
            
            if 'genres' in filter_criteria:
                filtered_content = self._filter_by_genre(
                    filtered_content, filter_criteria['genres']
                )
            
            if 'quality_threshold' in filter_criteria:
                filtered_content = self._filter_by_quality(
                    filtered_content, filter_criteria['quality_threshold']
                )
            
            if 'duration_range' in filter_criteria:
                filtered_content = self._filter_by_duration(
                    filtered_content, filter_criteria['duration_range']
                )
            
            if 'exclude_seen' in filter_criteria and filter_criteria['exclude_seen']:
                filtered_content = self._filter_exclude_seen(
                    filtered_content, user_profile
                )
            
            if 'language' in filter_criteria:
                filtered_content = self._filter_by_language(
                    filtered_content, filter_criteria['language']
                )
            
            # Apply user-specific filters
            filtered_content = await self._apply_user_filters(
                filtered_content, user_profile
            )
            
            return filtered_content
            
        except Exception as e:
            self.logger.error(f"Content filtering error: {e}")
            raise ContentFilteringError(f"Content filtering failed: {e}")
    
    def _filter_by_content_type(
        self,
        content_items: List[ContentItem],
        allowed_types: List[ContentType]
    ) -> List[ContentItem]:
        """Filter by content type"""
        return [c for c in content_items if c.content_type in allowed_types]
    
    def _filter_by_genre(
        self,
        content_items: List[ContentItem],
        allowed_genres: List[str]
    ) -> List[ContentItem]:
        """Filter by genre"""
        return [c for c in content_items if c.genre in allowed_genres]
    
    def _filter_by_quality(
        self,
        content_items: List[ContentItem],
        quality_threshold: float
    ) -> List[ContentItem]:
        """Filter by quality threshold"""
        return [c for c in content_items if c.quality_score >= quality_threshold]
    
    def _filter_by_duration(
        self,
        content_items: List[ContentItem],
        duration_range: Tuple[float, float]
    ) -> List[ContentItem]:
        """Filter by duration range"""
        min_duration, max_duration = duration_range
        return [
            c for c in content_items
            if c.duration is not None and min_duration <= c.duration <= max_duration
        ]
    
    def _filter_exclude_seen(
        self,
        content_items: List[ContentItem],
        user_profile: UserProfile
    ) -> List[ContentItem]:
        """Exclude previously seen content"""
        seen_content_ids = {
            i.get('content_id') for i in user_profile.interaction_history
            if i.get('content_id')
        }
        
        return [c for c in content_items if c.content_id not in seen_content_ids]
    
    def _filter_by_language(
        self,
        content_items: List[ContentItem],
        preferred_language: str
    ) -> List[ContentItem]:
        """Filter by language preference"""
        return [c for c in content_items if c.language == preferred_language]
    
    async def _apply_user_filters(
        self,
        content_items: List[ContentItem],
        user_profile: UserProfile
    ) -> List[ContentItem]:
        """Apply user-specific filtering rules"""
        
        # Filter by user's minimum quality expectations
        min_quality = user_profile.content_sophistication * 0.7
        content_items = [c for c in content_items if c.quality_score >= min_quality]
        
        # Filter by user's preferred complexity range
        user_complexity = user_profile.content_sophistication
        complexity_tolerance = 0.3
        content_items = [
            c for c in content_items
            if abs(c.complexity_level - user_complexity) <= complexity_tolerance
        ]
        
        return content_items
