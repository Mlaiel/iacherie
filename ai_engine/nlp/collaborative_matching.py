"""
Collaborative Matching Module for IA Influencer Agent Platform

Advanced AI-powered collaboration matching system for content creators,
influencers, musicians, and multi-format content collaboration opportunities.

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.

 STRICT COPYRIGHT WARNING - Unauthorized use prohibited 
This software is proprietary and confidential. Contact: mlaiel@live.de
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from abc import ABC, abstractmethod
from enum import Enum
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans, DBSCAN
from sklearn.decomposition import PCA
import networkx as nx
from collections import defaultdict, Counter
import json

logger = logging.getLogger(__name__)

class CollaborationType(Enum):
    """Types of collaboration"""
    MUSIC_COLLAB = "music_collaboration"
    CONTENT_CREATION = "content_creation"
    CROSS_PROMOTION = "cross_promotion"
    BRAND_PARTNERSHIP = "brand_partnership"
    SKILL_EXCHANGE = "skill_exchange"
    MENTORSHIP = "mentorship"
    PROJECT_BASED = "project_based"
    LONG_TERM = "long_term_partnership"

class CreatorType(Enum):
    """Types of content creators"""
    MUSICIAN = "musician"
    INFLUENCER = "influencer"
    PHOTOGRAPHER = "photographer"
    VIDEOGRAPHER = "videographer"
    BLOGGER = "blogger"
    PODCASTER = "podcaster"
    COMEDIAN = "comedian"
    ARTIST = "visual_artist"
    DANCER = "dancer"
    ACTOR = "actor"

class MatchingCriteria(Enum):
    """Criteria for collaboration matching"""
    AUDIENCE_OVERLAP = "audience_overlap"
    CONTENT_STYLE = "content_style"
    ENGAGEMENT_RATE = "engagement_rate"
    GENRE_SIMILARITY = "genre_similarity"
    BRAND_VALUES = "brand_values"
    GEOGRAPHIC_PROXIMITY = "geographic_proximity"
    LANGUAGE_COMPATIBILITY = "language_compatibility"
    EXPERIENCE_LEVEL = "experience_level"
    AVAILABILITY = "availability"
    BUDGET_RANGE = "budget_range"

@dataclass
class CreatorProfile:
    """Comprehensive creator profile for matching"""
    user_id: str
    creator_type: CreatorType
    name: str
    description: str
    genres: List[str] = field(default_factory=list)
    skills: List[str] = field(default_factory=list)
    languages: List[str] = field(default_factory=list)
    location: Dict[str, Any] = field(default_factory=dict)
    audience_demographics: Dict[str, Any] = field(default_factory=dict)
    engagement_metrics: Dict[str, float] = field(default_factory=dict)
    content_themes: List[str] = field(default_factory=list)
    brand_values: List[str] = field(default_factory=list)
    collaboration_preferences: Dict[str, Any] = field(default_factory=dict)
    availability: Dict[str, Any] = field(default_factory=dict)
    budget_range: Dict[str, int] = field(default_factory=dict)
    past_collaborations: List[str] = field(default_factory=list)
    portfolio_samples: List[str] = field(default_factory=list)
    social_platforms: Dict[str, Dict] = field(default_factory=dict)
    verification_level: str = "basic"
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class CollaborationOpportunity:
    """Collaboration opportunity definition"""
    opportunity_id: str
    creator_id: str
    title: str
    description: str
    collaboration_type: CollaborationType
    required_skills: List[str] = field(default_factory=list)
    preferred_creator_types: List[CreatorType] = field(default_factory=list)
    budget_range: Dict[str, int] = field(default_factory=dict)
    timeline: Dict[str, datetime] = field(default_factory=dict)
    deliverables: List[str] = field(default_factory=list)
    requirements: Dict[str, Any] = field(default_factory=dict)
    compensation_type: str = "monetary"  # monetary, revenue_share, exposure, barter
    geographic_constraints: List[str] = field(default_factory=list)
    language_requirements: List[str] = field(default_factory=list)
    experience_level: str = "any"  # beginner, intermediate, expert, any
    status: str = "open"  # open, in_progress, completed, cancelled
    applications: List[str] = field(default_factory=list)
    selected_collaborators: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    deadline: datetime = field(default_factory=lambda: datetime.utcnow() + timedelta(days=30))

@dataclass
class MatchResult:
    """Collaboration match result"""
    match_id: str
    creator_1_id: str
    creator_2_id: str
    opportunity_id: Optional[str] = None
    match_score: float = 0.0
    compatibility_breakdown: Dict[str, float] = field(default_factory=dict)
    match_reasoning: List[str] = field(default_factory=list)
    potential_collaboration_types: List[CollaborationType] = field(default_factory=list)
    success_probability: float = 0.0
    mutual_benefits: List[str] = field(default_factory=list)
    potential_challenges: List[str] = field(default_factory=list)
    recommendation_strength: str = "medium"  # low, medium, high, very_high
    timestamp: datetime = field(default_factory=datetime.utcnow)

class CollaborativeMatchingEngine:
    """
    Advanced AI-powered collaborative matching engine
    
    Capabilities:
    - Multi-dimensional creator profile analysis
    - Intelligent opportunity matching
    - Success probability prediction
    - Network effect optimization
    - Collaboration history analysis
    - Real-time compatibility assessment
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or self._get_default_config()
        self.creator_profiles: Dict[str, CreatorProfile] = {}
        self.opportunities: Dict[str, CollaborationOpportunity] = {}
        self.match_history: List[MatchResult] = []
        self.collaboration_network = nx.Graph()
        self.success_patterns = {}
        self.trending_collaborations = []
        
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""



        return {
            'min_match_score': 0.6,
            'max_matches_per_request': 10,
            'enable_ml_scoring': True,
            'consider_past_collaborations': True,
            'weight_audience_overlap': 0.25,
            'weight_content_similarity': 0.20,
            'weight_engagement_compatibility': 0.15,
            'weight_geographic_proximity': 0.10,
            'weight_brand_alignment': 0.15,
            'weight_skill_complementarity': 0.15,
            'success_prediction_threshold': 0.7,
            'network_effect_factor': 0.1
        }
    
    async def register_creator(self, profile: CreatorProfile) -> bool:
        """Register a new creator profile"""



        try:
            # Validate profile completeness
            completeness_score = self._calculate_profile_completeness(profile)
            if completeness_score < 0.5:
                logger.warning(f"Creator profile {profile.user_id} is incomplete (score: {completeness_score})")
            
            # Store profile
            self.creator_profiles[profile.user_id] = profile
            
            # Add to collaboration network
            self.collaboration_network.add_node(
                profile.user_id,
                creator_type=profile.creator_type.value,
                genres=profile.genres,
                location=profile.location,
                engagement_score=profile.engagement_metrics.get('total_score', 0)
            )
            
            # Update network connections based on past collaborations
            await self._update_network_connections(profile)
            
            logger.info(f"Creator {profile.user_id} registered successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error registering creator {profile.user_id}: {e}")
            return False
    
    async def create_collaboration_opportunity(self, opportunity: CollaborationOpportunity) -> bool:
        """Create a new collaboration opportunity"""



        try:
            # Validate opportunity
            if not self._validate_opportunity(opportunity):
                return False
            
            # Store opportunity
            self.opportunities[opportunity.opportunity_id] = opportunity
            
            # Auto-match with suitable creators
            potential_matches = await self._find_opportunity_matches(opportunity)
            
            # Notify relevant creators
            await self._notify_potential_collaborators(opportunity, potential_matches)
            
            logger.info(f"Collaboration opportunity {opportunity.opportunity_id} created")
            return True
            
        except Exception as e:
            logger.error(f"Error creating opportunity {opportunity.opportunity_id}: {e}")
            return False
    
    async def find_collaboration_matches(
        self,
        creator_id: str,
        collaboration_type: Optional[CollaborationType] = None,
        max_matches: Optional[int] = None
    ) -> List[MatchResult]:
        """Find collaboration matches for a creator"""



        try:
            if creator_id not in self.creator_profiles:
                raise ValueError(f"Creator {creator_id} not found")
            
            creator_profile = self.creator_profiles[creator_id]
            max_matches = max_matches or self.config['max_matches_per_request']
            
            # Find potential matches
            potential_matches = []
            
            for other_id, other_profile in self.creator_profiles.items():
                if other_id == creator_id:
                    continue
                
                # Calculate compatibility score
                match_score = await self._calculate_match_score(creator_profile, other_profile)
                
                if match_score >= self.config['min_match_score']:
                    # Generate detailed match result
                    match_result = await self._generate_match_result(
                        creator_profile,
                        other_profile,
                        match_score,
                        collaboration_type
                    )
                    potential_matches.append(match_result)
            
            # Sort by match score and return top matches
            potential_matches.sort(key=lambda x: x.match_score, reverse=True)
            return potential_matches[:max_matches]
            
        except Exception as e:
            logger.error(f"Error finding matches for creator {creator_id}: {e}")
            return []
    
    async def predict_collaboration_success(
        self,
        creator_1_id: str,
        creator_2_id: str,
        collaboration_type: CollaborationType
    ) -> Dict[str, Any]:
        """Predict success probability of a collaboration"""



        try:
            if creator_1_id not in self.creator_profiles or creator_2_id not in self.creator_profiles:
                raise ValueError("One or both creators not found")
            
            creator_1 = self.creator_profiles[creator_1_id]
            creator_2 = self.creator_profiles[creator_2_id]
            
            # Calculate various success factors
            success_factors = await self._analyze_success_factors(
                creator_1,
                creator_2,
                collaboration_type
            )
            
            # Predict success probability using ML model
            success_probability = await self._predict_success_probability(success_factors)
            
            # Generate recommendations
            recommendations = await self._generate_collaboration_recommendations(
                creator_1,
                creator_2,
                success_factors,
                collaboration_type
            )
            
            return {
                'success_probability': success_probability,
                'success_factors': success_factors,
                'recommendations': recommendations,
                'risk_factors': await self._identify_risk_factors(creator_1, creator_2),
                'optimal_collaboration_structure': await self._suggest_collaboration_structure(
                    creator_1,
                    creator_2,
                    collaboration_type
                )
            }
            
        except Exception as e:
            logger.error(f"Error predicting collaboration success: {e}")
            return {'success_probability': 0.0, 'error': str(e)}
    
    async def get_trending_collaborations(self, time_window: timedelta = None) -> List[Dict[str, Any]]:
        """Get trending collaboration patterns and opportunities"""



        try:
            time_window = time_window or timedelta(days=30)
            cutoff_time = datetime.utcnow() - time_window
            
            # Analyze recent successful collaborations
            recent_matches = [
                match for match in self.match_history
                if match.timestamp >= cutoff_time and match.match_score > 0.8
            ]
            
            # Identify trending collaboration types
            trending_types = Counter(
                collab_type for match in recent_matches
                for collab_type in match.potential_collaboration_types
            )
            
            # Identify trending creator combinations
            trending_combinations = Counter(
                (self.creator_profiles[match.creator_1_id].creator_type,
                 self.creator_profiles[match.creator_2_id].creator_type)
                for match in recent_matches
            )
            
            # Identify trending genres/themes
            trending_themes = self._analyze_trending_themes(recent_matches)
            
            return {
                'trending_collaboration_types': dict(trending_types.most_common(10)),
                'trending_creator_combinations': dict(trending_combinations.most_common(10)),
                'trending_themes': trending_themes,
                'success_rate_by_type': await self._calculate_success_rates_by_type(),
                'market_opportunities': await self._identify_market_opportunities(),
                'timestamp': datetime.utcnow()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing trending collaborations: {e}")
            return {}
    
    async def _calculate_match_score(
        self,
        creator_1: CreatorProfile,
        creator_2: CreatorProfile
    ) -> float:
        """Calculate comprehensive match score between two creators"""
        
        # Audience overlap score
        audience_score = self._calculate_audience_overlap(creator_1, creator_2)
        
        # Content similarity score
        content_score = self._calculate_content_similarity(creator_1, creator_2)
        
        # Engagement compatibility score
        engagement_score = self._calculate_engagement_compatibility(creator_1, creator_2)
        
        # Geographic proximity score
        geographic_score = self._calculate_geographic_proximity(creator_1, creator_2)
        
        # Brand alignment score
        brand_score = self._calculate_brand_alignment(creator_1, creator_2)
        
        # Skill complementarity score
        skill_score = self._calculate_skill_complementarity(creator_1, creator_2)
        
        # Weighted average
        weights = self.config
        total_score = (
            audience_score * weights['weight_audience_overlap'] +
            content_score * weights['weight_content_similarity'] +
            engagement_score * weights['weight_engagement_compatibility'] +
            geographic_score * weights['weight_geographic_proximity'] +
            brand_score * weights['weight_brand_alignment'] +
            skill_score * weights['weight_skill_complementarity']
        )
        
        # Apply network effect bonus
        network_bonus = self._calculate_network_effect(creator_1.user_id, creator_2.user_id)
        total_score += network_bonus * weights['network_effect_factor']
        
        return min(total_score, 1.0)
    
    def _calculate_audience_overlap(
        self,
        creator_1: CreatorProfile,
        creator_2: CreatorProfile
    ) -> float:
        """Calculate audience demographic overlap"""



        try:
            if not creator_1.audience_demographics or not creator_2.audience_demographics:
                return 0.5  # Default score if demographics not available
            
            overlap_score = 0.0
            total_factors = 0
            
            # Age group overlap
            age_1 = set(creator_1.audience_demographics.get('age_groups', []))
            age_2 = set(creator_2.audience_demographics.get('age_groups', []))
            if age_1 and age_2:
                age_overlap = len(age_1.intersection(age_2)) / len(age_1.union(age_2))
                overlap_score += age_overlap
                total_factors += 1
            
            # Gender distribution similarity
            gender_1 = creator_1.audience_demographics.get('gender_distribution', {})
            gender_2 = creator_2.audience_demographics.get('gender_distribution', {})
            if gender_1 and gender_2:
                # Calculate similarity using cosine similarity
                gender_sim = self._calculate_distribution_similarity(gender_1, gender_2)
                overlap_score += gender_sim
                total_factors += 1
            
            # Geographic overlap
            geo_1 = set(creator_1.audience_demographics.get('top_countries', []))
            geo_2 = set(creator_2.audience_demographics.get('top_countries', []))
            if geo_1 and geo_2:
                geo_overlap = len(geo_1.intersection(geo_2)) / len(geo_1.union(geo_2))
                overlap_score += geo_overlap
                total_factors += 1
            
            # Interest overlap
            interests_1 = set(creator_1.audience_demographics.get('interests', []))
            interests_2 = set(creator_2.audience_demographics.get('interests', []))
            if interests_1 and interests_2:
                interest_overlap = len(interests_1.intersection(interests_2)) / len(interests_1.union(interests_2))
                overlap_score += interest_overlap
                total_factors += 1
            
            return overlap_score / max(total_factors, 1)
            
        except Exception as e:
            logger.error(f"Error calculating audience overlap: {e}")
            return 0.5
    
    def _calculate_content_similarity(
        self,
        creator_1: CreatorProfile,
        creator_2: CreatorProfile
    ) -> float:
        """Calculate content style and theme similarity"""



        try:
            similarity_score = 0.0
            total_factors = 0
            
            # Genre similarity
            genres_1 = set(creator_1.genres)
            genres_2 = set(creator_2.genres)
            if genres_1 and genres_2:
                genre_similarity = len(genres_1.intersection(genres_2)) / len(genres_1.union(genres_2))
                similarity_score += genre_similarity
                total_factors += 1
            
            # Content theme similarity
            themes_1 = set(creator_1.content_themes)
            themes_2 = set(creator_2.content_themes)
            if themes_1 and themes_2:
                theme_similarity = len(themes_1.intersection(themes_2)) / len(themes_1.union(themes_2))
                similarity_score += theme_similarity
                total_factors += 1
            
            # Creator type compatibility
            type_compatibility = self._calculate_creator_type_compatibility(
                creator_1.creator_type,
                creator_2.creator_type
            )
            similarity_score += type_compatibility
            total_factors += 1
            
            return similarity_score / max(total_factors, 1)
            
        except Exception as e:
            logger.error(f"Error calculating content similarity: {e}")
            return 0.5
    
    def _calculate_engagement_compatibility(
        self,
        creator_1: CreatorProfile,
        creator_2: CreatorProfile
    ) -> float:
        """Calculate engagement rate and quality compatibility"""



        try:
            if not creator_1.engagement_metrics or not creator_2.engagement_metrics:
                return 0.5
            
            # Compare engagement rates
            rate_1 = creator_1.engagement_metrics.get('engagement_rate', 0)
            rate_2 = creator_2.engagement_metrics.get('engagement_rate', 0)
            
            # Calculate similarity (closer rates = better compatibility)
            if rate_1 == 0 or rate_2 == 0:
                rate_similarity = 0.5
            else:
                rate_diff = abs(rate_1 - rate_2) / max(rate_1, rate_2)
                rate_similarity = 1.0 - rate_diff
            
            # Compare audience sizes (similar sizes often work better)
            size_1 = creator_1.engagement_metrics.get('follower_count', 0)
            size_2 = creator_2.engagement_metrics.get('follower_count', 0)
            
            if size_1 == 0 or size_2 == 0:
                size_compatibility = 0.5
            else:
                size_ratio = min(size_1, size_2) / max(size_1, size_2)
                size_compatibility = 0.5 + 0.5 * size_ratio  # Favor similar sizes
            
            # Average the scores
            return (rate_similarity + size_compatibility) / 2
            
        except Exception as e:
            logger.error(f"Error calculating engagement compatibility: {e}")
            return 0.5
    
    def _calculate_geographic_proximity(
        self,
        creator_1: CreatorProfile,
        creator_2: CreatorProfile
    ) -> float:
        """Calculate geographic proximity score"""



        try:
            if not creator_1.location or not creator_2.location:
                return 0.5  # Neutral score if location not available
            
            # Same country = high score
            country_1 = creator_1.location.get('country', '')
            country_2 = creator_2.location.get('country', '')
            
            if country_1 and country_2:
                if country_1 == country_2:
                    # Same city = highest score
                    city_1 = creator_1.location.get('city', '')
                    city_2 = creator_2.location.get('city', '')
                    if city_1 and city_2 and city_1 == city_2:
                        return 1.0
                    else:
                        return 0.8  # Same country, different city
                else:
                    # Different countries - check if same region/continent
                    region_1 = creator_1.location.get('region', '')
                    region_2 = creator_2.location.get('region', '')
                    if region_1 and region_2 and region_1 == region_2:
                        return 0.6  # Same region
                    else:
                        return 0.3  # Different regions
            
            return 0.5  # Default if countries not specified
            
        except Exception as e:
            logger.error(f"Error calculating geographic proximity: {e}")
            return 0.5
    
    def _calculate_brand_alignment(
        self,
        creator_1: CreatorProfile,
        creator_2: CreatorProfile
    ) -> float:
        """Calculate brand values and vision alignment"""



        try:
            values_1 = set(creator_1.brand_values)
            values_2 = set(creator_2.brand_values)
            
            if not values_1 or not values_2:
                return 0.5  # Neutral score if brand values not specified
            
            # Calculate overlap
            overlap = len(values_1.intersection(values_2))
            union = len(values_1.union(values_2))
            
            if union == 0:
                return 0.5
            
            alignment_score = overlap / union
            
            # Bonus for complementary values (not just overlap)
            complementary_bonus = self._calculate_complementary_values_bonus(values_1, values_2)
            
            return min(alignment_score + complementary_bonus, 1.0)
            
        except Exception as e:
            logger.error(f"Error calculating brand alignment: {e}")
            return 0.5
    
    def _calculate_skill_complementarity(
        self,
        creator_1: CreatorProfile,
        creator_2: CreatorProfile
    ) -> float:
        """Calculate skill complementarity score"""



        try:
            skills_1 = set(creator_1.skills)
            skills_2 = set(creator_2.skills)
            
            if not skills_1 or not skills_2:
                return 0.5
            
            # Complementarity is better than overlap for skills
            overlap = len(skills_1.intersection(skills_2))
            unique_1 = len(skills_1 - skills_2)
            unique_2 = len(skills_2 - skills_1)
            
            # Perfect complementarity: no overlap, many unique skills on both sides
            total_unique = unique_1 + unique_2
            total_skills = len(skills_1.union(skills_2))
            
            if total_skills == 0:
                return 0.5
            
            # High score for high complementarity, penalty for too much overlap
            complementarity_score = total_unique / total_skills
            overlap_penalty = overlap / total_skills * 0.3
            
            return max(complementarity_score - overlap_penalty, 0.1)
            
        except Exception as e:
            logger.error(f"Error calculating skill complementarity: {e}")
            return 0.5
    
    def _calculate_network_effect(self, creator_1_id: str, creator_2_id: str) -> float:
        """Calculate network effect bonus based on mutual connections"""



        try:
            if not self.collaboration_network.has_node(creator_1_id) or \
               not self.collaboration_network.has_node(creator_2_id):
                return 0.0
            
            # Find mutual connections
            neighbors_1 = set(self.collaboration_network.neighbors(creator_1_id))
            neighbors_2 = set(self.collaboration_network.neighbors(creator_2_id))
            mutual_connections = neighbors_1.intersection(neighbors_2)
            
            # Calculate network bonus based on mutual connections
            if len(mutual_connections) == 0:
                return 0.0
            
            # More mutual connections = higher bonus
            network_bonus = min(len(mutual_connections) * 0.1, 0.3)
            
            return network_bonus
            
        except Exception as e:
            logger.error(f"Error calculating network effect: {e}")
            return 0.0
    
    async def _generate_match_result(
        self,
        creator_1: CreatorProfile,
        creator_2: CreatorProfile,
        match_score: float,
        collaboration_type: Optional[CollaborationType] = None
    ) -> MatchResult:
        """Generate detailed match result"""



        try:
            match_id = f"match_{creator_1.user_id}_{creator_2.user_id}_{int(datetime.utcnow().timestamp())}"
            
            # Calculate detailed compatibility breakdown
            compatibility_breakdown = {
                'audience_overlap': self._calculate_audience_overlap(creator_1, creator_2),
                'content_similarity': self._calculate_content_similarity(creator_1, creator_2),
                'engagement_compatibility': self._calculate_engagement_compatibility(creator_1, creator_2),
                'geographic_proximity': self._calculate_geographic_proximity(creator_1, creator_2),
                'brand_alignment': self._calculate_brand_alignment(creator_1, creator_2),
                'skill_complementarity': self._calculate_skill_complementarity(creator_1, creator_2)
            }
            
            # Generate match reasoning
            match_reasoning = self._generate_match_reasoning(compatibility_breakdown)
            
            # Suggest potential collaboration types
            potential_types = self._suggest_collaboration_types(creator_1, creator_2)
            
            # Predict success probability
            success_probability = await self._predict_success_probability({
                'match_score': match_score,
                'compatibility_breakdown': compatibility_breakdown,
                'creator_1_experience': len(creator_1.past_collaborations),
                'creator_2_experience': len(creator_2.past_collaborations)
            })
            
            # Generate mutual benefits and challenges
            mutual_benefits = self._identify_mutual_benefits(creator_1, creator_2)
            potential_challenges = self._identify_potential_challenges(creator_1, creator_2)
            
            # Determine recommendation strength
            recommendation_strength = self._determine_recommendation_strength(match_score, success_probability)
            
            return MatchResult(
                match_id=match_id,
                creator_1_id=creator_1.user_id,
                creator_2_id=creator_2.user_id,
                match_score=match_score,
                compatibility_breakdown=compatibility_breakdown,
                match_reasoning=match_reasoning,
                potential_collaboration_types=potential_types,
                success_probability=success_probability,
                mutual_benefits=mutual_benefits,
                potential_challenges=potential_challenges,
                recommendation_strength=recommendation_strength
            )
            
        except Exception as e:
            logger.error(f"Error generating match result: {e}")
            return None
    
    def _calculate_profile_completeness(self, profile: CreatorProfile) -> float:
        """Calculate profile completeness score"""
        required_fields = [
            'name', 'description', 'creator_type', 'genres', 'skills',
            'languages', 'location', 'audience_demographics'
        ]
        
        completeness = 0.0
        for field in required_fields:
            value = getattr(profile, field, None)
            if value:
                if isinstance(value, (list, dict)):
                    if len(value) > 0:
                        completeness += 1
                else:
                    if str(value).strip():
                        completeness += 1
        
        return completeness / len(required_fields)
    
    async def get_collaboration_insights(self, creator_id: str) -> Dict[str, Any]:
        """Get collaboration insights and recommendations for a creator"""



        try:
            if creator_id not in self.creator_profiles:
                raise ValueError(f"Creator {creator_id} not found")
            
            creator = self.creator_profiles[creator_id]
            
            # Analyze current collaboration network
            network_analysis = self._analyze_creator_network(creator_id)
            
            # Find potential collaboration gaps
            collaboration_gaps = self._identify_collaboration_gaps(creator)
            
            # Get trending opportunities
            trending_ops = await self._find_trending_opportunities_for_creator(creator)
            
            # Calculate collaboration readiness score
            readiness_score = self._calculate_collaboration_readiness(creator)
            
            return {
                'collaboration_readiness_score': readiness_score,
                'network_analysis': network_analysis,
                'collaboration_gaps': collaboration_gaps,
                'trending_opportunities': trending_ops,
                'recommendations': self._generate_creator_recommendations(creator),
                'optimal_collaboration_strategy': self._suggest_collaboration_strategy(creator),
                'timestamp': datetime.utcnow()
            }
            
        except Exception as e:
            logger.error(f"Error generating collaboration insights: {e}")
            return {}
