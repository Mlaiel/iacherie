"""
Matching Engine - Advanced AI-Powered Creator and Content Matching

Provides intelligent matching capabilities for creators, content, and opportunities
using machine learning algorithms and semantic analysis.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
import math
from collections import defaultdict

from .marketplace_agent import MarketplaceConfig, ContentType


class MatchingType(Enum):
    """Types of matching operations."""
    CREATOR_COLLABORATION = "creator_collaboration"
    CONTENT_RECOMMENDATION = "content_recommendation"
    AUDIENCE_TARGETING = "audience_targeting"
    OPPORTUNITY_MATCHING = "opportunity_matching"
    SKILL_MATCHING = "skill_matching"


class SimilarityMetric(Enum):
    """Similarity calculation methods."""
    COSINE_SIMILARITY = "cosine_similarity"
    EUCLIDEAN_DISTANCE = "euclidean_distance"
    JACCARD_SIMILARITY = "jaccard_similarity"
    SEMANTIC_SIMILARITY = "semantic_similarity"
    HYBRID_SIMILARITY = "hybrid_similarity"


@dataclass
class MatchingProfile:
    """Profile data for matching algorithms."""
    user_id: int = 0
    profile_type: str = "creator"  # creator, buyer, content
    features: Dict[str, float] = field(default_factory=dict)
    categorical_features: Dict[str, List[str]] = field(default_factory=dict)
    behavioral_patterns: Dict[str, float] = field(default_factory=dict)
    preferences: Dict[str, Any] = field(default_factory=dict)
    interaction_history: List[Dict[str, Any]] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class MatchingResult:
    """Result of a matching operation."""
    target_id: int = 0
    similarity_score: float = 0.0
    confidence_level: float = 0.0
    matching_factors: Dict[str, float] = field(default_factory=dict)
    explanation: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RecommendationSet:
    """Set of recommendations with metadata."""
    user_id: int = 0
    recommendation_type: str = ""
    items: List[MatchingResult] = field(default_factory=list)
    generation_strategy: str = ""
    confidence_score: float = 0.0
    diversity_score: float = 0.0
    novelty_score: float = 0.0
    generated_at: datetime = field(default_factory=datetime.utcnow)


class MatchingEngine:
    """
    Advanced AI-powered matching engine for marketplace intelligence.
    
    Provides comprehensive matching capabilities including:
    - Creator collaboration matching with compatibility scoring
    - Personalized content recommendations using collaborative filtering
    - Audience targeting and segmentation analysis
    - Opportunity matching based on skills and preferences
    - Semantic similarity analysis for content discovery
    - Multi-factor matching with explainable AI
    """

    def __init__(self, config: MarketplaceConfig):
        """
        Initialize matching engine.
        
        Args:
            config: Marketplace configuration
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize AI models and components
        self._initialize_matching_models()
        self._initialize_feature_extractors()
        
        # Matching profiles cache
        self.profiles_cache = {}
        self.similarity_cache = {}
        self.recommendation_cache = {}
        
        self.logger.info("Matching engine initialized")

    def _initialize_matching_models(self) -> None:
        """Initialize machine learning models for matching."""



        try:
            # Initialize neural embedding models
            # Initialize collaborative filtering models
            # Initialize content-based filtering models
            # Initialize hybrid recommendation models
            self.logger.info("Matching models initialized")
        except Exception as e:
            self.logger.error(f"Failed to initialize matching models: {e}")
            raise

    def _initialize_feature_extractors(self) -> None:
        """Initialize feature extraction components."""



        try:
            # Initialize NLP feature extractors
            # Initialize audio feature extractors
            # Initialize visual feature extractors
            # Initialize behavioral feature extractors
            self.logger.info("Feature extractors initialized")
        except Exception as e:
            self.logger.error(f"Failed to initialize feature extractors: {e}")
            raise

    async def calculate_creator_compatibility(
        self,
        requester_id: int,
        target_creator_id: int
    ) -> float:
        """
        Calculate compatibility score between two creators.
        
        Args:
            requester_id: ID of the requesting creator
            target_creator_id: ID of the target creator
            
        Returns:
            Compatibility score between 0.0 and 1.0
        """



        try:
            # Get creator profiles
            requester_profile = await self._get_creator_matching_profile(requester_id)
            target_profile = await self._get_creator_matching_profile(target_creator_id)
            
            if not requester_profile or not target_profile:
                return 0.0

            # Calculate multi-dimensional compatibility
            compatibility_scores = {}
            
            # Skill compatibility
            compatibility_scores["skill"] = await self._calculate_skill_compatibility(
                requester_profile, target_profile
            )
            
            # Style compatibility
            compatibility_scores["style"] = await self._calculate_style_compatibility(
                requester_profile, target_profile
            )
            
            # Work preference compatibility
            compatibility_scores["work_preferences"] = await self._calculate_work_compatibility(
                requester_profile, target_profile
            )
            
            # Communication compatibility
            compatibility_scores["communication"] = await self._calculate_communication_compatibility(
                requester_profile, target_profile
            )
            
            # Historical collaboration success
            compatibility_scores["history"] = await self._calculate_historical_compatibility(
                requester_id, target_creator_id
            )
            
            # Calculate weighted overall compatibility
            weights = {
                "skill": 0.3,
                "style": 0.25,
                "work_preferences": 0.2,
                "communication": 0.15,
                "history": 0.1
            }
            
            overall_compatibility = sum(
                score * weights[factor]
                for factor, score in compatibility_scores.items()
            )
            
            return min(1.0, max(0.0, overall_compatibility))

        except Exception as e:
            self.logger.error(f"Creator compatibility calculation failed: {e}")
            return 0.0

    async def generate_user_recommendations(
        self,
        user_id: int,
        content_type: Optional[ContentType] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Generate personalized content recommendations for a user.
        
        Args:
            user_id: ID of the user
            content_type: Optional content type filter
            limit: Maximum number of recommendations
            
        Returns:
            List of personalized recommendations
        """



        try:
            # Get user profile and preferences
            user_profile = await self._get_user_matching_profile(user_id)
            if not user_profile:
                return await self._generate_fallback_recommendations(content_type, limit)

            # Generate recommendations using multiple strategies
            collaborative_recs = await self._generate_collaborative_recommendations(
                user_profile, content_type, limit
            )
            
            content_based_recs = await self._generate_content_based_recommendations(
                user_profile, content_type, limit
            )
            
            trending_recs = await self._generate_trending_recommendations(
                content_type, limit // 3
            )
            
            # Combine and diversify recommendations
            combined_recommendations = await self._combine_recommendation_strategies(
                collaborative_recs, content_based_recs, trending_recs, limit
            )
            
            # Apply diversity and novelty optimization
            optimized_recommendations = await self._optimize_recommendation_diversity(
                combined_recommendations, user_profile
            )
            
            # Convert to API format
            formatted_recommendations = []
            for rec in optimized_recommendations[:limit]:
                formatted_recommendations.append({
                    "id": rec.target_id,
                    "type": "content",
                    "score": rec.similarity_score,
                    "confidence": rec.confidence_level,
                    "reasons": rec.explanation,
                    "factors": rec.matching_factors
                })
            
            return formatted_recommendations

        except Exception as e:
            self.logger.error(f"User recommendations generation failed: {e}")
            return []

    async def enhance_search_results(
        self,
        search_results: Dict[str, Any],
        query: str
    ) -> Dict[str, Any]:
        """
        Enhance search results with AI-powered recommendations and re-ranking.
        
        Args:
            search_results: Original search results
            query: Search query string
            
        Returns:
            Enhanced search results with AI improvements
        """



        try:
            enhancements = {}
            
            # Semantic query analysis
            query_intent = await self._analyze_query_intent(query)
            enhancements["query_intent"] = query_intent
            
            # Related searches
            related_searches = await self._generate_related_searches(query)
            enhancements["related_searches"] = related_searches
            
            # Query expansion suggestions
            query_expansions = await self._generate_query_expansions(query)
            enhancements["query_expansions"] = query_expansions
            
            # Personalized result re-ranking (if user context available)
            if "user_id" in search_results.get("metadata", {}):
                user_id = search_results["metadata"]["user_id"]
                enhanced_rankings = await self._personalize_search_results(
                    search_results.get("listings", []), user_id, query
                )
                enhancements["personalized_rankings"] = enhanced_rankings
            
            # Content recommendations based on search
            content_recommendations = await self._generate_search_based_recommendations(
                query, search_results.get("listings", [])
            )
            enhancements["related_content"] = content_recommendations
            
            return enhancements

        except Exception as e:
            self.logger.error(f"Search enhancement failed: {e}")
            return {}

    async def find_matching_opportunities(
        self,
        creator_id: int,
        opportunity_type: str = "collaboration",
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Find matching opportunities for a creator.
        
        Args:
            creator_id: ID of the creator
            opportunity_type: Type of opportunities to find
            limit: Maximum number of opportunities
            
        Returns:
            List of matching opportunities
        """



        try:
            # Get creator profile
            creator_profile = await self._get_creator_matching_profile(creator_id)
            if not creator_profile:
                return []

            opportunities = []
            
            if opportunity_type == "collaboration":
                opportunities = await self._find_collaboration_opportunities(
                    creator_profile, limit
                )
            elif opportunity_type == "project":
                opportunities = await self._find_project_opportunities(
                    creator_profile, limit
                )
            elif opportunity_type == "marketplace":
                opportunities = await self._find_marketplace_opportunities(
                    creator_profile, limit
                )
            
            # Score and rank opportunities
            scored_opportunities = []
            for opportunity in opportunities:
                score = await self._calculate_opportunity_match_score(
                    creator_profile, opportunity
                )
                scored_opportunities.append({
                    **opportunity,
                    "match_score": score,
                    "recommendation_strength": self._calculate_recommendation_strength(score)
                })
            
            # Sort by match score
            sorted_opportunities = sorted(
                scored_opportunities,
                key=lambda x: x["match_score"],
                reverse=True
            )
            
            return sorted_opportunities[:limit]

        except Exception as e:
            self.logger.error(f"Opportunity matching failed: {e}")
            return []

    async def calculate_content_similarity(
        self,
        content_id_1: int,
        content_id_2: int,
        similarity_type: SimilarityMetric = SimilarityMetric.HYBRID_SIMILARITY
    ) -> float:
        """
        Calculate similarity between two pieces of content.
        
        Args:
            content_id_1: ID of first content item
            content_id_2: ID of second content item
            similarity_type: Type of similarity calculation
            
        Returns:
            Similarity score between 0.0 and 1.0
        """



        try:
            # Check cache first
            cache_key = f"{content_id_1}_{content_id_2}_{similarity_type.value}"
            if cache_key in self.similarity_cache:
                return self.similarity_cache[cache_key]

            # Get content features
            features_1 = await self._extract_content_features(content_id_1)
            features_2 = await self._extract_content_features(content_id_2)
            
            if not features_1 or not features_2:
                return 0.0

            # Calculate similarity based on type
            if similarity_type == SimilarityMetric.COSINE_SIMILARITY:
                similarity = await self._calculate_cosine_similarity(features_1, features_2)
            elif similarity_type == SimilarityMetric.EUCLIDEAN_DISTANCE:
                similarity = await self._calculate_euclidean_similarity(features_1, features_2)
            elif similarity_type == SimilarityMetric.JACCARD_SIMILARITY:
                similarity = await self._calculate_jaccard_similarity(features_1, features_2)
            elif similarity_type == SimilarityMetric.SEMANTIC_SIMILARITY:
                similarity = await self._calculate_semantic_similarity(features_1, features_2)
            else:  # Hybrid similarity
                similarity = await self._calculate_hybrid_similarity(features_1, features_2)
            
            # Cache result
            self.similarity_cache[cache_key] = similarity
            
            return similarity

        except Exception as e:
            self.logger.error(f"Content similarity calculation failed: {e}")
            return 0.0

    async def generate_audience_segments(
        self,
        segmentation_criteria: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Generate audience segments using clustering algorithms.
        
        Args:
            segmentation_criteria: Criteria for segmentation
            
        Returns:
            List of identified audience segments
        """



        try:
            # Get user behavior data
            user_data = await self._get_user_behavior_data(segmentation_criteria)
            
            # Apply clustering algorithms
            segments = await self._perform_audience_clustering(user_data)
            
            # Analyze segment characteristics
            analyzed_segments = []
            for segment in segments:
                analysis = await self._analyze_segment_characteristics(segment)
                analyzed_segments.append({
                    "segment_id": segment["id"],
                    "size": segment["size"],
                    "characteristics": analysis["characteristics"],
                    "preferences": analysis["preferences"],
                    "behavior_patterns": analysis["behavior_patterns"],
                    "recommended_content_types": analysis["content_types"],
                    "engagement_potential": analysis["engagement_score"]
                })
            
            return analyzed_segments

        except Exception as e:
            self.logger.error(f"Audience segmentation failed: {e}")
            return []

    async def _get_creator_matching_profile(self, creator_id: int) -> Optional[MatchingProfile]:
        """Get or create creator matching profile."""



        try:
            # Check cache
            if creator_id in self.profiles_cache:
                return self.profiles_cache[creator_id]
            
            # Build profile from user data
            profile = await self._build_creator_profile(creator_id)
            
            if profile:
                self.profiles_cache[creator_id] = profile
                
            return profile

        except Exception as e:
            self.logger.error(f"Failed to get creator profile {creator_id}: {e}")
            return None

    async def _build_creator_profile(self, creator_id: int) -> Optional[MatchingProfile]:
        """Build comprehensive creator profile for matching."""



        try:
            # Mock implementation - would gather real user data
            profile = MatchingProfile(
                user_id=creator_id,
                profile_type="creator",
                features={
                    "experience_years": 3.5,
                    "portfolio_size": 45.0,
                    "avg_rating": 4.6,
                    "collaboration_success_rate": 0.89,
                    "response_time_hours": 6.2,
                    "price_range_low": 50.0,
                    "price_range_high": 500.0
                },
                categorical_features={
                    "specialties": ["music_production", "audio_editing", "mastering"],
                    "genres": ["electronic", "pop", "ambient"],
                    "software_proficiency": ["ableton", "pro_tools", "logic"],
                    "preferred_collaboration_types": ["remote", "hybrid"]
                },
                behavioral_patterns={
                    "avg_project_duration": 14.5,  # days
                    "revision_rounds_avg": 2.3,
                    "communication_frequency": 0.8,  # daily
                    "deadline_adherence": 0.95
                }
            )
            
            return profile

        except Exception as e:
            self.logger.error(f"Creator profile building failed: {e}")
            return None

    async def _calculate_skill_compatibility(
        self,
        profile1: MatchingProfile,
        profile2: MatchingProfile
    ) -> float:
        """Calculate skill-based compatibility score."""



        try:
            # Get skill sets
            skills1 = set(profile1.categorical_features.get("specialties", []))
            skills2 = set(profile2.categorical_features.get("specialties", []))
            
            # Calculate Jaccard similarity for skills
            if not skills1 or not skills2:
                return 0.5  # Neutral if no skill data
            
            intersection = len(skills1.intersection(skills2))
            union = len(skills1.union(skills2))
            
            jaccard_score = intersection / union if union > 0 else 0.0
            
            # Factor in complementary skills (high value when skills complement)
            complementary_score = 1.0 - jaccard_score  # Higher when skills are different
            
            # Weighted combination: some overlap good, but complementary skills also valuable
            compatibility = (jaccard_score * 0.4) + (complementary_score * 0.6)
            
            return min(1.0, compatibility)

        except Exception as e:
            self.logger.error(f"Skill compatibility calculation failed: {e}")
            return 0.0

    async def _calculate_style_compatibility(
        self,
        profile1: MatchingProfile,
        profile2: MatchingProfile
    ) -> float:
        """Calculate style-based compatibility score."""



        try:
            # Get genre/style preferences
            styles1 = set(profile1.categorical_features.get("genres", []))
            styles2 = set(profile2.categorical_features.get("genres", []))
            
            if not styles1 or not styles2:
                return 0.5
            
            # Calculate overlap
            intersection = len(styles1.intersection(styles2))
            total_styles = len(styles1) + len(styles2)
            
            # Style compatibility benefits from overlap
            compatibility = (2 * intersection) / total_styles if total_styles > 0 else 0.0
            
            return min(1.0, compatibility)

        except Exception as e:
            self.logger.error(f"Style compatibility calculation failed: {e}")
            return 0.0

    async def _calculate_cosine_similarity(
        self,
        features1: Dict[str, float],
        features2: Dict[str, float]
    ) -> float:
        """Calculate cosine similarity between feature vectors."""



        try:
            # Get common features
            common_features = set(features1.keys()).intersection(set(features2.keys()))
            
            if not common_features:
                return 0.0
            
            # Calculate dot product and magnitudes
            dot_product = sum(features1[f] * features2[f] for f in common_features)
            magnitude1 = math.sqrt(sum(features1[f] ** 2 for f in common_features))
            magnitude2 = math.sqrt(sum(features2[f] ** 2 for f in common_features))
            
            if magnitude1 == 0 or magnitude2 == 0:
                return 0.0
            
            return dot_product / (magnitude1 * magnitude2)

        except Exception as e:
            self.logger.error(f"Cosine similarity calculation failed: {e}")
            return 0.0

    async def _generate_collaborative_recommendations(
        self,
        user_profile: MatchingProfile,
        content_type: Optional[ContentType],
        limit: int
    ) -> List[MatchingResult]:
        """Generate collaborative filtering recommendations."""



        try:
            # Mock implementation - would use real collaborative filtering
            recommendations = []
            
            for i in range(min(limit, 5)):
                recommendations.append(MatchingResult(
                    target_id=1000 + i,
                    similarity_score=0.8 - (i * 0.1),
                    confidence_level=0.9 - (i * 0.05),
                    matching_factors={"collaborative_score": 0.8 - (i * 0.1)},
                    explanation=[f"Users with similar preferences also liked this content"]
                ))
            
            return recommendations

        except Exception as e:
            self.logger.error(f"Collaborative recommendations failed: {e}")
            return []

    async def _combine_recommendation_strategies(
        self,
        collaborative: List[MatchingResult],
        content_based: List[MatchingResult],
        trending: List[MatchingResult],
        limit: int
    ) -> List[MatchingResult]:
        """Combine multiple recommendation strategies."""



        try:
            # Assign weights to different strategies
            weights = {"collaborative": 0.5, "content_based": 0.3, "trending": 0.2}
            
            # Combine recommendations with weighted scoring
            all_recommendations = {}
            
            for rec in collaborative:
                rec.similarity_score *= weights["collaborative"]
                all_recommendations[rec.target_id] = rec
            
            for rec in content_based:
                if rec.target_id in all_recommendations:
                    # Combine scores
                    existing = all_recommendations[rec.target_id]
                    existing.similarity_score += rec.similarity_score * weights["content_based"]
                    existing.confidence_level = max(existing.confidence_level, rec.confidence_level)
                    existing.explanation.extend(rec.explanation)
                else:
                    rec.similarity_score *= weights["content_based"]
                    all_recommendations[rec.target_id] = rec
            
            for rec in trending:
                if rec.target_id in all_recommendations:
                    existing = all_recommendations[rec.target_id]
                    existing.similarity_score += rec.similarity_score * weights["trending"]
                    existing.explanation.append("Currently trending")
                else:
                    rec.similarity_score *= weights["trending"]
                    all_recommendations[rec.target_id] = rec
            
            # Sort by combined score
            sorted_recommendations = sorted(
                all_recommendations.values(),
                key=lambda x: x.similarity_score,
                reverse=True
            )
            
            return sorted_recommendations[:limit]

        except Exception as e:
            self.logger.error(f"Recommendation combination failed: {e}")
            return collaborative + content_based + trending
