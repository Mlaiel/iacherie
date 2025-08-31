"""
🤝 Collaboration Matcher - IA Influencer Agent
============================================

Advanced collaboration matching system for creators to find optimal partnerships
based on audience compatibility, content synergy, and mutual growth potential.

  PROPRIETARY SOFTWARE - UNAUTHORIZED USE PROHIBITED
====================================================
Author: Fahed Mlaiel <mlaiel@live.de>
Copyright © 2025 Fahed Mlaiel - All rights reserved
WARNING: Any unauthorized copying, modification, distribution or use of this code
without explicit written permission from Fahed Mlaiel is strictly prohibited.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
from datetime import datetime, timedelta
import json
import hashlib

# ML/AI Libraries
import torch
import torch.nn as nn
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans
from transformers import AutoModel, AutoTokenizer
import networkx as nx

# Core Dependencies
from ..analytics.audience_analytics import AudienceAnalytics
from ..processors.social_processor import SocialProcessor
from ..storage.graph_storage import GraphStorage
from ..cache.redis_cache import RedisCache


class CollaborationType(Enum):
    """Types of collaborations"""
    CONTENT_CREATION = "content_creation"
    CROSS_PROMOTION = "cross_promotion"
    JOINT_PRODUCT = "joint_product"
    EVENT_HOSTING = "event_hosting"
    SKILL_EXCHANGE = "skill_exchange"
    BRAND_PARTNERSHIP = "brand_partnership"
    MENTORSHIP = "mentorship"
    COMMUNITY_BUILDING = "community_building"


class CompatibilityFactor(Enum):
    """Factors for collaboration compatibility"""
    AUDIENCE_OVERLAP = "audience_overlap"
    CONTENT_SYNERGY = "content_synergy"
    ENGAGEMENT_COMPATIBILITY = "engagement_compatibility"
    BRAND_ALIGNMENT = "brand_alignment"
    GROWTH_POTENTIAL = "growth_potential"
    SCHEDULING_COMPATIBILITY = "scheduling_compatibility"
    GEOGRAPHIC_ALIGNMENT = "geographic_alignment"
    VALUES_ALIGNMENT = "values_alignment"


@dataclass
class CollaborationMatch:
    """Collaboration match data structure"""
    match_id: str
    creator_a_id: str
    creator_b_id: str
    collaboration_type: CollaborationType
    compatibility_score: float
    mutual_benefit_score: float
    audience_overlap_percentage: float
    content_synergy_score: float
    growth_potential_score: float
    recommended_format: str
    suggested_timeline: str
    success_probability: float
    potential_reach: int
    estimated_engagement_boost: float
    risk_factors: List[str]
    success_factors: List[str]
    collaboration_ideas: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class CreatorProfile:
    """Creator profile for matching"""
    creator_id: str
    name: str
    platform_handles: Dict[str, str]
    content_categories: List[str]
    audience_demographics: Dict[str, Any]
    engagement_metrics: Dict[str, float]
    content_style: str
    collaboration_preferences: Dict[str, Any]
    availability: Dict[str, Any]
    past_collaborations: List[str]
    brand_values: List[str]
    expertise_areas: List[str]
    growth_metrics: Dict[str, float]
    geographic_location: str
    language_preferences: List[str]
    last_updated: datetime = field(default_factory=datetime.now)


@dataclass
class CollaborationOpportunity:
    """Collaboration opportunity details"""
    opportunity_id: str
    collaboration_type: CollaborationType
    title: str
    description: str
    target_creators: List[str]
    requirements: List[str]
    benefits: List[str]
    timeline: str
    compensation_model: str
    application_deadline: datetime
    created_by: str
    status: str = "open"


class CollaborationMatcher:
    """
    Advanced collaboration matching engine for creators
    
    Matches creators based on:
    - Audience compatibility and overlap analysis
    - Content synergy and complementary strengths
    - Engagement patterns and timing alignment
    - Brand values and messaging consistency
    - Growth objectives and mutual benefits
    - Geographic and cultural considerations
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize collaboration matcher"""
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.audience_analytics = AudienceAnalytics(config.get('audience_analytics', {}))
        self.social_processor = SocialProcessor(config.get('social', {}))
        self.graph_storage = GraphStorage(config.get('graph_storage', {}))
        self.cache = RedisCache(config.get('redis', {}))
        
        # ML Models
        self.creator_embedder = None
        self.compatibility_predictor = None
        self.success_predictor = None
        
        # Matching parameters
        self.min_compatibility_score = config.get('min_compatibility_score', 0.6)
        self.max_matches = config.get('max_matches', 20)
        self.audience_overlap_weight = config.get('audience_overlap_weight', 0.25)
        self.content_synergy_weight = config.get('content_synergy_weight', 0.25)
        self.engagement_weight = config.get('engagement_weight', 0.20)
        self.brand_alignment_weight = config.get('brand_alignment_weight', 0.15)
        self.growth_potential_weight = config.get('growth_potential_weight', 0.15)
        
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize ML models for collaboration matching"""



        try:
            # Creator embedding model
            self.creator_embedder = AutoModel.from_pretrained(
                self.config.get('embedding_model', 'sentence-transformers/all-MiniLM-L6-v2')
            )
            
            # Compatibility prediction model
            class CompatibilityPredictor(nn.Module):
                def __init__(self, input_size: int = 200, hidden_size: int = 128):
                    super().__init__()
                    self.fc1 = nn.Linear(input_size, hidden_size)
                    self.fc2 = nn.Linear(hidden_size, 64)
                    self.fc3 = nn.Linear(64, 32)
                    self.fc4 = nn.Linear(32, 1)
                    self.dropout = nn.Dropout(0.3)
                    self.relu = nn.ReLU()
                    self.sigmoid = nn.Sigmoid()
                
                def forward(self, x):
                    x = self.dropout(self.relu(self.fc1(x)))
                    x = self.dropout(self.relu(self.fc2(x)))
                    x = self.dropout(self.relu(self.fc3(x)))
                    x = self.sigmoid(self.fc4(x))
                    return x
            
            self.compatibility_predictor = CompatibilityPredictor()
            
            # Success prediction model
            class SuccessPredictor(nn.Module):
                def __init__(self, input_size: int = 150, hidden_size: int = 100):
                    super().__init__()
                    self.fc1 = nn.Linear(input_size, hidden_size)
                    self.fc2 = nn.Linear(hidden_size, 50)
                    self.fc3 = nn.Linear(50, 25)
                    self.fc4 = nn.Linear(25, 1)
                    self.dropout = nn.Dropout(0.2)
                    self.relu = nn.ReLU()
                    self.sigmoid = nn.Sigmoid()
                
                def forward(self, x):
                    x = self.dropout(self.relu(self.fc1(x)))
                    x = self.dropout(self.relu(self.fc2(x)))
                    x = self.dropout(self.relu(self.fc3(x)))
                    x = self.sigmoid(self.fc4(x))
                    return x
            
            self.success_predictor = SuccessPredictor()
            
            self.logger.info("Collaboration matching models initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Error initializing models: {e}")
            raise
    
    async def find_collaboration_matches(
        self,
        creator_id: str,
        collaboration_type: CollaborationType = None,
        target_audience_size: Tuple[int, int] = None,
        content_categories: List[str] = None,
        geographic_preference: str = None,
        limit: int = 10
    ) -> List[CollaborationMatch]:
        """
        Find optimal collaboration matches for a creator
        
        Args:
            creator_id: Creator seeking collaborations
            collaboration_type: Specific type of collaboration desired
            target_audience_size: Min/max audience size range
            content_categories: Preferred content categories
            geographic_preference: Geographic preference for collaborations
            limit: Maximum number of matches to return
            
        Returns:
            List of ranked collaboration matches
        """



        try:
            self.logger.info(f"Finding collaboration matches for creator {creator_id}")
            
            # Get creator profile
            creator_profile = await self._get_creator_profile(creator_id)
            if not creator_profile:
                self.logger.warning(f"Creator profile not found for {creator_id}")
                return []
            
            # Get potential collaboration candidates
            candidates = await self._get_collaboration_candidates(
                creator_profile,
                collaboration_type,
                target_audience_size,
                content_categories,
                geographic_preference
            )
            
            # Calculate compatibility scores
            matches = []
            for candidate in candidates:
                match = await self._calculate_collaboration_compatibility(
                    creator_profile, candidate, collaboration_type
                )
                if match and match.compatibility_score >= self.min_compatibility_score:
                    matches.append(match)
            
            # Sort by compatibility and potential
            matches.sort(
                key=lambda x: (x.compatibility_score * x.mutual_benefit_score),
                reverse=True
            )
            
            # Limit results
            final_matches = matches[:limit]
            
            # Cache results
            cache_key = f"collaboration_matches:{creator_id}:{collaboration_type or 'all'}"
            await self.cache.set(cache_key, final_matches, ttl=1800)
            
            self.logger.info(f"Found {len(final_matches)} collaboration matches")
            return final_matches
            
        except Exception as e:
            self.logger.error(f"Error finding collaboration matches: {e}")
            return []
    
    async def _get_collaboration_candidates(
        self,
        creator_profile: CreatorProfile,
        collaboration_type: CollaborationType = None,
        target_audience_size: Tuple[int, int] = None,
        content_categories: List[str] = None,
        geographic_preference: str = None
    ) -> List[CreatorProfile]:
        """Get potential collaboration candidates"""



        try:
            # Build search criteria
            criteria = {}
            
            # Audience size filter
            if target_audience_size:
                criteria['audience_size_min'] = target_audience_size[0]
                criteria['audience_size_max'] = target_audience_size[1]
            
            # Content categories filter
            if content_categories:
                criteria['content_categories'] = content_categories
            elif creator_profile.content_categories:
                # Find complementary or similar categories
                criteria['content_categories'] = await self._get_compatible_categories(
                    creator_profile.content_categories
                )
            
            # Geographic filter
            if geographic_preference:
                criteria['geographic_location'] = geographic_preference
            
            # Collaboration type filter
            if collaboration_type:
                criteria['collaboration_preferences'] = collaboration_type.value
            
            # Get candidates from database
            candidates = await self._search_creators(criteria)
            
            # Filter out the requesting creator
            candidates = [c for c in candidates if c.creator_id != creator_profile.creator_id]
            
            # Remove creators with recent collaborations (avoid spam)
            candidates = await self._filter_recent_collaborations(
                creator_profile.creator_id, candidates
            )
            
            return candidates
            
        except Exception as e:
            self.logger.error(f"Error getting collaboration candidates: {e}")
            return []
    
    async def _calculate_collaboration_compatibility(
        self,
        creator_a: CreatorProfile,
        creator_b: CreatorProfile,
        collaboration_type: CollaborationType = None
    ) -> Optional[CollaborationMatch]:
        """Calculate compatibility between two creators"""



        try:
            # Calculate individual compatibility factors
            audience_compatibility = await self._calculate_audience_compatibility(creator_a, creator_b)
            content_synergy = await self._calculate_content_synergy(creator_a, creator_b)
            engagement_compatibility = await self._calculate_engagement_compatibility(creator_a, creator_b)
            brand_alignment = await self._calculate_brand_alignment(creator_a, creator_b)
            growth_potential = await self._calculate_growth_potential(creator_a, creator_b)
            
            # Calculate weighted compatibility score
            compatibility_score = (
                audience_compatibility * self.audience_overlap_weight +
                content_synergy * self.content_synergy_weight +
                engagement_compatibility * self.engagement_weight +
                brand_alignment * self.brand_alignment_weight +
                growth_potential * self.growth_potential_weight
            )
            
            # Calculate mutual benefit score
            mutual_benefit = await self._calculate_mutual_benefit(creator_a, creator_b)
            
            # Predict collaboration success
            success_probability = await self._predict_collaboration_success(
                creator_a, creator_b, compatibility_score
            )
            
            # Determine collaboration type if not specified
            if not collaboration_type:
                collaboration_type = await self._suggest_collaboration_type(creator_a, creator_b)
            
            # Generate collaboration ideas
            collaboration_ideas = await self._generate_collaboration_ideas(
                creator_a, creator_b, collaboration_type
            )
            
            # Calculate potential reach and engagement boost
            potential_reach = await self._calculate_potential_reach(creator_a, creator_b)
            engagement_boost = await self._calculate_engagement_boost(creator_a, creator_b)
            
            # Identify risk and success factors
            risk_factors = await self._identify_risk_factors(creator_a, creator_b)
            success_factors = await self._identify_success_factors(creator_a, creator_b)
            
            match = CollaborationMatch(
                match_id=self._generate_id(),
                creator_a_id=creator_a.creator_id,
                creator_b_id=creator_b.creator_id,
                collaboration_type=collaboration_type,
                compatibility_score=compatibility_score,
                mutual_benefit_score=mutual_benefit,
                audience_overlap_percentage=audience_compatibility * 100,
                content_synergy_score=content_synergy,
                growth_potential_score=growth_potential,
                recommended_format=await self._recommend_collaboration_format(creator_a, creator_b),
                suggested_timeline=await self._suggest_timeline(creator_a, creator_b),
                success_probability=success_probability,
                potential_reach=potential_reach,
                estimated_engagement_boost=engagement_boost,
                risk_factors=risk_factors,
                success_factors=success_factors,
                collaboration_ideas=collaboration_ideas
            )
            
            return match
            
        except Exception as e:
            self.logger.error(f"Error calculating collaboration compatibility: {e}")
            return None
    
    async def _calculate_audience_compatibility(
        self,
        creator_a: CreatorProfile,
        creator_b: CreatorProfile
    ) -> float:
        """Calculate audience compatibility and overlap"""



        try:
            # Get audience demographics for both creators
            audience_a = creator_a.audience_demographics
            audience_b = creator_b.audience_demographics
            
            compatibility_score = 0.0
            factors = 0
            
            # Age group compatibility
            if 'age_groups' in audience_a and 'age_groups' in audience_b:
                age_overlap = self._calculate_demographic_overlap(
                    audience_a['age_groups'], audience_b['age_groups']
                )
                compatibility_score += age_overlap * 0.3
                factors += 0.3
            
            # Gender distribution compatibility
            if 'gender' in audience_a and 'gender' in audience_b:
                gender_compatibility = self._calculate_gender_compatibility(
                    audience_a['gender'], audience_b['gender']
                )
                compatibility_score += gender_compatibility * 0.2
                factors += 0.2
            
            # Geographic overlap
            if 'locations' in audience_a and 'locations' in audience_b:
                geo_overlap = self._calculate_demographic_overlap(
                    audience_a['locations'], audience_b['locations']
                )
                compatibility_score += geo_overlap * 0.25
                factors += 0.25
            
            # Interest overlap
            if 'interests' in audience_a and 'interests' in audience_b:
                interest_overlap = self._calculate_demographic_overlap(
                    audience_a['interests'], audience_b['interests']
                )
                compatibility_score += interest_overlap * 0.25
                factors += 0.25
            
            # Normalize score
            if factors > 0:
                compatibility_score = compatibility_score / factors
            
            return min(compatibility_score, 1.0)
            
        except Exception as e:
            self.logger.error(f"Error calculating audience compatibility: {e}")
            return 0.5
    
    async def _calculate_content_synergy(
        self,
        creator_a: CreatorProfile,
        creator_b: CreatorProfile
    ) -> float:
        """Calculate content synergy between creators"""



        try:
            categories_a = set(creator_a.content_categories)
            categories_b = set(creator_b.content_categories)
            
            # Calculate category overlap and complementarity
            overlap = len(categories_a & categories_b)
            total_unique = len(categories_a | categories_b)
            
            # Sweet spot: some overlap but also complementary content
            overlap_ratio = overlap / len(categories_a) if categories_a else 0
            
            # Optimal synergy is around 30-60% overlap
            if 0.3 <= overlap_ratio <= 0.6:
                synergy_score = 0.8 + (overlap_ratio - 0.3) * 0.2 / 0.3
            elif overlap_ratio < 0.3:
                synergy_score = overlap_ratio / 0.3 * 0.8
            else:
                synergy_score = 0.8 - (overlap_ratio - 0.6) * 0.3 / 0.4
            
            # Boost for complementary expertise
            expertise_a = set(creator_a.expertise_areas)
            expertise_b = set(creator_b.expertise_areas)
            
            if expertise_a and expertise_b:
                expertise_complementarity = len(expertise_a - expertise_b) / len(expertise_a | expertise_b)
                synergy_score += expertise_complementarity * 0.2
            
            return min(synergy_score, 1.0)
            
        except Exception as e:
            self.logger.error(f"Error calculating content synergy: {e}")
            return 0.5
    
    async def _calculate_engagement_compatibility(
        self,
        creator_a: CreatorProfile,
        creator_b: CreatorProfile
    ) -> float:
        """Calculate engagement pattern compatibility"""



        try:
            engagement_a = creator_a.engagement_metrics
            engagement_b = creator_b.engagement_metrics
            
            compatibility_score = 0.0
            factors = 0
            
            # Engagement rate compatibility (similar levels work better)
            if 'engagement_rate' in engagement_a and 'engagement_rate' in engagement_b:
                rate_a = engagement_a['engagement_rate']
                rate_b = engagement_b['engagement_rate']
                
                # Similar engagement rates are better for collaboration
                rate_similarity = 1 - abs(rate_a - rate_b) / max(rate_a, rate_b, 0.01)
                compatibility_score += rate_similarity * 0.4
                factors += 0.4
            
            # Posting frequency compatibility
            if 'posting_frequency' in engagement_a and 'posting_frequency' in engagement_b:
                freq_compatibility = self._calculate_frequency_compatibility(
                    engagement_a['posting_frequency'], engagement_b['posting_frequency']
                )
                compatibility_score += freq_compatibility * 0.3
                factors += 0.3
            
            # Audience responsiveness compatibility
            if 'response_rate' in engagement_a and 'response_rate' in engagement_b:
                response_compatibility = self._calculate_response_compatibility(
                    engagement_a['response_rate'], engagement_b['response_rate']
                )
                compatibility_score += response_compatibility * 0.3
                factors += 0.3
            
            # Normalize score
            if factors > 0:
                compatibility_score = compatibility_score / factors
            
            return min(compatibility_score, 1.0)
            
        except Exception as e:
            self.logger.error(f"Error calculating engagement compatibility: {e}")
            return 0.5
    
    async def _calculate_brand_alignment(
        self,
        creator_a: CreatorProfile,
        creator_b: CreatorProfile
    ) -> float:
        """Calculate brand values and messaging alignment"""



        try:
            values_a = set(creator_a.brand_values)
            values_b = set(creator_b.brand_values)
            
            if not values_a or not values_b:
                return 0.5  # Neutral if no brand values specified
            
            # Calculate values overlap
            overlap = len(values_a & values_b)
            total_unique = len(values_a | values_b)
            
            if total_unique == 0:
                return 0.5
            
            # High brand alignment is important for successful collaborations
            alignment_score = overlap / len(values_a) if values_a else 0
            
            # Boost for content style compatibility
            style_a = creator_a.content_style
            style_b = creator_b.content_style
            
            style_compatibility = self._calculate_style_compatibility(style_a, style_b)
            
            # Combine values and style alignment
            final_score = (alignment_score * 0.7 + style_compatibility * 0.3)
            
            return min(final_score, 1.0)
            
        except Exception as e:
            self.logger.error(f"Error calculating brand alignment: {e}")
            return 0.5
    
    async def _calculate_growth_potential(
        self,
        creator_a: CreatorProfile,
        creator_b: CreatorProfile
    ) -> float:
        """Calculate mutual growth potential from collaboration"""



        try:
            growth_a = creator_a.growth_metrics
            growth_b = creator_b.growth_metrics
            
            potential_score = 0.0
            factors = 0
            
            # Growth rate compatibility
            if 'growth_rate' in growth_a and 'growth_rate' in growth_b:
                rate_a = growth_a['growth_rate']
                rate_b = growth_b['growth_rate']
                
                # Both growing creators have higher potential
                avg_growth = (rate_a + rate_b) / 2
                potential_score += min(avg_growth, 1.0) * 0.4
                factors += 0.4
            
            # Audience size complementarity
            if 'follower_count' in growth_a and 'follower_count' in growth_b:
                followers_a = growth_a['follower_count']
                followers_b = growth_b['follower_count']
                
                # Different audience sizes can be beneficial
                size_ratio = min(followers_a, followers_b) / max(followers_a, followers_b, 1)
                size_benefit = 0.5 + (1 - size_ratio) * 0.5  # Inverse relationship
                potential_score += size_benefit * 0.3
                factors += 0.3
            
            # Cross-platform potential
            platforms_a = set(creator_a.platform_handles.keys())
            platforms_b = set(creator_b.platform_handles.keys())
            
            unique_platforms = len(platforms_a | platforms_b)
            cross_platform_potential = min(unique_platforms / 5, 1.0)  # Max 5 platforms
            potential_score += cross_platform_potential * 0.3
            factors += 0.3
            
            # Normalize score
            if factors > 0:
                potential_score = potential_score / factors
            
            return min(potential_score, 1.0)
            
        except Exception as e:
            self.logger.error(f"Error calculating growth potential: {e}")
            return 0.5
    
    async def _calculate_mutual_benefit(
        self,
        creator_a: CreatorProfile,
        creator_b: CreatorProfile
    ) -> float:
        """Calculate mutual benefit score for collaboration"""



        try:
            # Analyze what each creator can offer the other
            benefit_score = 0.0
            
            # Audience reach benefit
            followers_a = creator_a.engagement_metrics.get('follower_count', 0)
            followers_b = creator_b.engagement_metrics.get('follower_count', 0)
            
            # Both benefit from exposure to new audiences
            reach_benefit = min(followers_a + followers_b, 1000000) / 1000000
            benefit_score += reach_benefit * 0.3
            
            # Skill complementarity benefit
            skills_a = set(creator_a.expertise_areas)
            skills_b = set(creator_b.expertise_areas)
            
            if skills_a and skills_b:
                unique_skills = len(skills_a - skills_b) + len(skills_b - skills_a)
                skill_benefit = min(unique_skills / 10, 1.0)  # Max 10 unique skills
                benefit_score += skill_benefit * 0.3
            
            # Platform diversification benefit
            platforms_a = set(creator_a.platform_handles.keys())
            platforms_b = set(creator_b.platform_handles.keys())
            
            unique_platforms = len(platforms_a | platforms_b) - len(platforms_a & platforms_b)
            platform_benefit = min(unique_platforms / 5, 1.0)
            benefit_score += platform_benefit * 0.2
            
            # Content variety benefit
            categories_a = set(creator_a.content_categories)
            categories_b = set(creator_b.content_categories)
            
            content_variety = len(categories_a | categories_b)
            variety_benefit = min(content_variety / 8, 1.0)  # Max 8 categories
            benefit_score += variety_benefit * 0.2
            
            return min(benefit_score, 1.0)
            
        except Exception as e:
            self.logger.error(f"Error calculating mutual benefit: {e}")
            return 0.5
    
    async def _predict_collaboration_success(
        self,
        creator_a: CreatorProfile,
        creator_b: CreatorProfile,
        compatibility_score: float
    ) -> float:
        """Predict collaboration success probability using ML"""



        try:
            # Extract features for success prediction
            features = self._extract_collaboration_features(creator_a, creator_b, compatibility_score)
            
            if self.success_predictor:
                with torch.no_grad():
                    features_tensor = torch.tensor(features).float().unsqueeze(0)
                    success_prob = float(self.success_predictor(features_tensor).item())
                    return success_prob
            
            # Fallback: rule-based prediction
            return self._rule_based_success_prediction(creator_a, creator_b, compatibility_score)
            
        except Exception as e:
            self.logger.error(f"Error predicting collaboration success: {e}")
            return compatibility_score  # Fallback to compatibility score
    
    def _rule_based_success_prediction(
        self,
        creator_a: CreatorProfile,
        creator_b: CreatorProfile,
        compatibility_score: float
    ) -> float:
        """Rule-based success prediction"""
        success_factors = []
        
        # High compatibility
        if compatibility_score > 0.8:
            success_factors.append(0.2)
        elif compatibility_score > 0.6:
            success_factors.append(0.1)
        
        # Active creators (recent content)
        if (datetime.now() - creator_a.last_updated).days < 7:
            success_factors.append(0.1)
        if (datetime.now() - creator_b.last_updated).days < 7:
            success_factors.append(0.1)
        
        # Previous collaboration experience
        if creator_a.past_collaborations:
            success_factors.append(0.1)
        if creator_b.past_collaborations:
            success_factors.append(0.1)
        
        # Similar audience sizes (easier coordination)
        followers_a = creator_a.engagement_metrics.get('follower_count', 0)
        followers_b = creator_b.engagement_metrics.get('follower_count', 0)
        
        if followers_a > 0 and followers_b > 0:
            size_ratio = min(followers_a, followers_b) / max(followers_a, followers_b)
            if size_ratio > 0.5:  # Similar sizes
                success_factors.append(0.15)
        
        base_probability = 0.3  # Base success rate
        boost = sum(success_factors)
        
        return min(base_probability + boost, 1.0)
    
    def _extract_collaboration_features(
        self,
        creator_a: CreatorProfile,
        creator_b: CreatorProfile,
        compatibility_score: float
    ) -> List[float]:
        """Extract features for ML models"""
        features = []
        
        # Compatibility score
        features.append(compatibility_score)
        
        # Creator metrics
        features.append(creator_a.engagement_metrics.get('engagement_rate', 0.05))
        features.append(creator_b.engagement_metrics.get('engagement_rate', 0.05))
        features.append(creator_a.engagement_metrics.get('follower_count', 0) / 1000000)  # Normalized
        features.append(creator_b.engagement_metrics.get('follower_count', 0) / 1000000)
        
        # Content diversity
        features.append(len(creator_a.content_categories) / 10)  # Normalized
        features.append(len(creator_b.content_categories) / 10)
        
        # Platform presence
        features.append(len(creator_a.platform_handles) / 5)  # Normalized
        features.append(len(creator_b.platform_handles) / 5)
        
        # Experience
        features.append(len(creator_a.past_collaborations) / 10)  # Normalized
        features.append(len(creator_b.past_collaborations) / 10)
        
        # Growth metrics
        features.append(creator_a.growth_metrics.get('growth_rate', 0.1))
        features.append(creator_b.growth_metrics.get('growth_rate', 0.1))
        
        # Pad to fixed size
        while len(features) < 150:
            features.append(0.0)
        
        return features[:150]
    
    async def _suggest_collaboration_type(
        self,
        creator_a: CreatorProfile,
        creator_b: CreatorProfile
    ) -> CollaborationType:
        """Suggest optimal collaboration type"""



        try:
            # Analyze creator profiles to suggest best collaboration type
            content_overlap = len(set(creator_a.content_categories) & set(creator_b.content_categories))
            
            # High content overlap -> cross-promotion or joint content
            if content_overlap >= 2:
                return CollaborationType.CONTENT_CREATION
            
            # Different expertise -> skill exchange
            if (set(creator_a.expertise_areas) - set(creator_b.expertise_areas)):
                return CollaborationType.SKILL_EXCHANGE
            
            # Similar audience sizes -> cross-promotion
            followers_a = creator_a.engagement_metrics.get('follower_count', 0)
            followers_b = creator_b.engagement_metrics.get('follower_count', 0)
            
            if followers_a > 0 and followers_b > 0:
                ratio = min(followers_a, followers_b) / max(followers_a, followers_b)
                if ratio > 0.7:
                    return CollaborationType.CROSS_PROMOTION
            
            # Default to content creation
            return CollaborationType.CONTENT_CREATION
            
        except Exception as e:
            self.logger.error(f"Error suggesting collaboration type: {e}")
            return CollaborationType.CONTENT_CREATION
    
    async def _generate_collaboration_ideas(
        self,
        creator_a: CreatorProfile,
        creator_b: CreatorProfile,
        collaboration_type: CollaborationType
    ) -> List[str]:
        """Generate specific collaboration ideas"""
        ideas = []
        
        try:
            common_categories = set(creator_a.content_categories) & set(creator_b.content_categories)
            
            if collaboration_type == CollaborationType.CONTENT_CREATION:
                for category in common_categories:
                    ideas.extend([
                        f"Co-create {category} content series",
                        f"Challenge collaboration in {category}",
                        f"Tutorial exchange in {category}"
                    ])
            
            elif collaboration_type == CollaborationType.CROSS_PROMOTION:
                ideas.extend([
                    "Feature each other in stories/posts",
                    "Host joint live sessions",
                    "Create audience introduction videos",
                    "Run coordinated giveaways"
                ])
            
            elif collaboration_type == CollaborationType.SKILL_EXCHANGE:
                unique_skills_a = set(creator_a.expertise_areas) - set(creator_b.expertise_areas)
                unique_skills_b = set(creator_b.expertise_areas) - set(creator_a.expertise_areas)
                
                for skill in unique_skills_a:
                    ideas.append(f"{creator_a.name} teaches {skill} to {creator_b.name}")
                for skill in unique_skills_b:
                    ideas.append(f"{creator_b.name} teaches {skill} to {creator_a.name}")
            
            elif collaboration_type == CollaborationType.JOINT_PRODUCT:
                ideas.extend([
                    "Co-develop online course",
                    "Create collaborative digital product",
                    "Launch joint merchandise line",
                    "Develop shared subscription service"
                ])
            
            # Generic ideas if none generated
            if not ideas:
                ideas.extend([
                    "Instagram takeover exchange",
                    "Podcast guest appearances",
                    "YouTube collaboration video",
                    "Joint social media campaign"
                ])
            
            return ideas[:5]  # Limit to 5 ideas
            
        except Exception as e:
            self.logger.error(f"Error generating collaboration ideas: {e}")
            return ["Basic content collaboration", "Cross-promotion exchange"]
    
    async def _recommend_collaboration_format(
        self,
        creator_a: CreatorProfile,
        creator_b: CreatorProfile
    ) -> str:
        """Recommend collaboration format"""



        try:
            # Analyze platform preferences
            platforms_a = set(creator_a.platform_handles.keys())
            platforms_b = set(creator_b.platform_handles.keys())
            common_platforms = platforms_a & platforms_b
            
            if 'youtube' in common_platforms:
                return "YouTube collaboration video"
            elif 'instagram' in common_platforms:
                return "Instagram Stories/Reels collaboration"
            elif 'tiktok' in common_platforms:
                return "TikTok duet/collaboration"
            elif 'podcast' in common_platforms:
                return "Podcast guest exchange"
            else:
                return "Multi-platform content series"
            
        except Exception as e:
            self.logger.error(f"Error recommending collaboration format: {e}")
            return "Social media collaboration"
    
    async def _suggest_timeline(
        self,
        creator_a: CreatorProfile,
        creator_b: CreatorProfile
    ) -> str:
        """Suggest collaboration timeline"""



        try:
            # Analyze posting frequencies
            freq_a = creator_a.engagement_metrics.get('posting_frequency', 1)
            freq_b = creator_b.engagement_metrics.get('posting_frequency', 1)
            
            avg_frequency = (freq_a + freq_b) / 2
            
            if avg_frequency >= 5:  # Daily posters
                return "1-2 weeks"
            elif avg_frequency >= 3:  # Regular posters
                return "2-3 weeks"
            else:  # Occasional posters
                return "3-4 weeks"
            
        except Exception as e:
            self.logger.error(f"Error suggesting timeline: {e}")
            return "2-3 weeks"
    
    async def _calculate_potential_reach(
        self,
        creator_a: CreatorProfile,
        creator_b: CreatorProfile
    ) -> int:
        """Calculate potential reach from collaboration"""



        try:
            followers_a = creator_a.engagement_metrics.get('follower_count', 0)
            followers_b = creator_b.engagement_metrics.get('follower_count', 0)
            
            # Estimate audience overlap (20% default)
            overlap_rate = 0.2
            unique_reach = followers_a + followers_b - (min(followers_a, followers_b) * overlap_rate)
            
            # Factor in engagement rates
            engagement_a = creator_a.engagement_metrics.get('engagement_rate', 0.05)
            engagement_b = creator_b.engagement_metrics.get('engagement_rate', 0.05)
            
            avg_engagement = (engagement_a + engagement_b) / 2
            effective_reach = int(unique_reach * avg_engagement * 2)  # Collaboration boost
            
            return effective_reach
            
        except Exception as e:
            self.logger.error(f"Error calculating potential reach: {e}")
            return 0
    
    async def _calculate_engagement_boost(
        self,
        creator_a: CreatorProfile,
        creator_b: CreatorProfile
    ) -> float:
        """Calculate estimated engagement boost from collaboration"""



        try:
            # Base boost from collaboration novelty
            base_boost = 0.25  # 25% base boost
            
            # Boost from audience crossover
            followers_a = creator_a.engagement_metrics.get('follower_count', 0)
            followers_b = creator_b.engagement_metrics.get('follower_count', 0)
            
            if followers_a > 0 and followers_b > 0:
                audience_factor = min(followers_b / followers_a, 2.0)  # Cap at 2x
                crossover_boost = (audience_factor - 1) * 0.1
            else:
                crossover_boost = 0
            
            # Boost from content variety
            categories_a = set(creator_a.content_categories)
            categories_b = set(creator_b.content_categories)
            unique_categories = len(categories_a | categories_b) - len(categories_a & categories_b)
            variety_boost = min(unique_categories * 0.05, 0.15)  # Max 15% boost
            
            total_boost = base_boost + crossover_boost + variety_boost
            return min(total_boost, 1.0)  # Cap at 100% boost
            
        except Exception as e:
            self.logger.error(f"Error calculating engagement boost: {e}")
            return 0.25
    
    async def _identify_risk_factors(
        self,
        creator_a: CreatorProfile,
        creator_b: CreatorProfile
    ) -> List[str]:
        """Identify potential risk factors for collaboration"""
        risks = []
        
        try:
            # Brand misalignment risks
            values_a = set(creator_a.brand_values)
            values_b = set(creator_b.brand_values)
            
            if values_a and values_b:
                overlap = len(values_a & values_b) / len(values_a | values_b)
                if overlap < 0.3:
                    risks.append("Low brand values alignment")
            
            # Audience mismatch risks
            engagement_a = creator_a.engagement_metrics.get('engagement_rate', 0.05)
            engagement_b = creator_b.engagement_metrics.get('engagement_rate', 0.05)
            
            if abs(engagement_a - engagement_b) > 0.03:
                risks.append("Significant engagement rate differences")
            
            # Experience disparity
            collabs_a = len(creator_a.past_collaborations)
            collabs_b = len(creator_b.past_collaborations)
            
            if abs(collabs_a - collabs_b) > 5:
                risks.append("Experience level mismatch")
            
            # Platform dependency
            platforms_a = set(creator_a.platform_handles.keys())
            platforms_b = set(creator_b.platform_handles.keys())
            
            if len(platforms_a & platforms_b) < 2:
                risks.append("Limited shared platform presence")
            
            # Add generic risks if none identified
            if not risks:
                risks.extend(["Creative differences", "Scheduling conflicts"])
            
            return risks[:3]  # Limit to 3 risk factors
            
        except Exception as e:
            self.logger.error(f"Error identifying risk factors: {e}")
            return ["Coordination challenges", "Audience reception uncertainty"]
    
    async def _identify_success_factors(
        self,
        creator_a: CreatorProfile,
        creator_b: CreatorProfile
    ) -> List[str]:
        """Identify success factors for collaboration"""
        success_factors = []
        
        try:
            # Strong engagement rates
            engagement_a = creator_a.engagement_metrics.get('engagement_rate', 0.05)
            engagement_b = creator_b.engagement_metrics.get('engagement_rate', 0.05)
            
            if engagement_a > 0.05 and engagement_b > 0.05:
                success_factors.append("High audience engagement rates")
            
            # Complementary content
            categories_a = set(creator_a.content_categories)
            categories_b = set(creator_b.content_categories)
            
            overlap = len(categories_a & categories_b)
            unique = len(categories_a | categories_b) - overlap
            
            if unique >= overlap:
                success_factors.append("Complementary content categories")
            
            # Similar growth trajectories
            growth_a = creator_a.growth_metrics.get('growth_rate', 0.1)
            growth_b = creator_b.growth_metrics.get('growth_rate', 0.1)
            
            if abs(growth_a - growth_b) < 0.1 and min(growth_a, growth_b) > 0.1:
                success_factors.append("Similar growth momentum")
            
            # Previous collaboration experience
            if creator_a.past_collaborations and creator_b.past_collaborations:
                success_factors.append("Proven collaboration experience")
            
            # Strong brand alignment
            values_a = set(creator_a.brand_values)
            values_b = set(creator_b.brand_values)
            
            if values_a and values_b:
                overlap = len(values_a & values_b) / len(values_a | values_b)
                if overlap > 0.6:
                    success_factors.append("Strong brand values alignment")
            
            # Multi-platform presence
            platforms_a = set(creator_a.platform_handles.keys())
            platforms_b = set(creator_b.platform_handles.keys())
            
            if len(platforms_a & platforms_b) >= 3:
                success_factors.append("Multi-platform collaboration potential")
            
            return success_factors[:4]  # Limit to 4 success factors
            
        except Exception as e:
            self.logger.error(f"Error identifying success factors: {e}")
            return ["Audience compatibility", "Content synergy"]
    
    # Helper methods for compatibility calculations
    def _calculate_demographic_overlap(self, demo_a: Dict[str, float], demo_b: Dict[str, float]) -> float:
        """Calculate overlap between demographic distributions"""
        if not demo_a or not demo_b:
            return 0.0
        
        overlap = 0.0
        total_a = sum(demo_a.values())
        total_b = sum(demo_b.values())
        
        if total_a == 0 or total_b == 0:
            return 0.0
        
        # Normalize distributions
        norm_a = {k: v / total_a for k, v in demo_a.items()}
        norm_b = {k: v / total_b for k, v in demo_b.items()}
        
        # Calculate overlap
        for key in norm_a:
            if key in norm_b:
                overlap += min(norm_a[key], norm_b[key])
        
        return overlap
    
    def _calculate_gender_compatibility(self, gender_a: Dict[str, float], gender_b: Dict[str, float]) -> float:
        """Calculate gender distribution compatibility"""
        # For gender, we want similar distributions rather than exact overlap
        if not gender_a or not gender_b:
            return 0.5
        
        # Get percentages
        male_a = gender_a.get('male', 0.5)
        male_b = gender_b.get('male', 0.5)
        
        # Similar distributions are better for collaboration
        similarity = 1 - abs(male_a - male_b)
        return similarity
    
    def _calculate_frequency_compatibility(self, freq_a: float, freq_b: float) -> float:
        """Calculate posting frequency compatibility"""
        if freq_a == 0 or freq_b == 0:
            return 0.3
        
        # Similar frequencies are better for coordination
        ratio = min(freq_a, freq_b) / max(freq_a, freq_b)
        return ratio
    
    def _calculate_response_compatibility(self, response_a: float, response_b: float) -> float:
        """Calculate audience response compatibility"""
        # Similar response rates indicate compatible audiences
        if response_a == 0 or response_b == 0:
            return 0.3
        
        similarity = 1 - abs(response_a - response_b) / max(response_a, response_b)
        return similarity
    
    def _calculate_style_compatibility(self, style_a: str, style_b: str) -> float:
        """Calculate content style compatibility"""
        # Define style compatibility matrix
        style_matrix = {
            'professional': {'professional': 1.0, 'creative': 0.7, 'casual': 0.5, 'humorous': 0.6},
            'creative': {'professional': 0.7, 'creative': 1.0, 'casual': 0.8, 'humorous': 0.9},
            'casual': {'professional': 0.5, 'creative': 0.8, 'casual': 1.0, 'humorous': 0.8},
            'humorous': {'professional': 0.6, 'creative': 0.9, 'casual': 0.8, 'humorous': 1.0}
        }
        
        return style_matrix.get(style_a, {}).get(style_b, 0.5)
    
    async def _get_compatible_categories(self, categories: List[str]) -> List[str]:
        """Get compatible content categories"""
        # Define category compatibility mapping
        category_compatibility = {
            'music': ['entertainment', 'lifestyle', 'dance', 'art'],
            'lifestyle': ['fashion', 'travel', 'food', 'fitness'],
            'tech': ['gaming', 'education', 'business', 'science'],
            'fitness': ['health', 'nutrition', 'lifestyle', 'motivation'],
            'fashion': ['beauty', 'lifestyle', 'shopping', 'art'],
            'education': ['science', 'tech', 'business', 'personal_development']
        }
        
        compatible = set(categories)  # Include original categories
        
        for category in categories:
            if category in category_compatibility:
                compatible.update(category_compatibility[category])
        
        return list(compatible)
    
    async def _search_creators(self, criteria: Dict[str, Any]) -> List[CreatorProfile]:
        """Search for creators based on criteria"""
        # This would query your creator database
        # For now, return mock data
        return []
    
    async def _filter_recent_collaborations(
        self,
        creator_id: str,
        candidates: List[CreatorProfile]
    ) -> List[CreatorProfile]:
        """Filter out creators with recent collaborations"""
        # Check collaboration history and filter recent ones
        filtered = []
        
        for candidate in candidates:
            # Skip if collaborated in last 90 days
            recent_collaboration = False
            for collab_id in candidate.past_collaborations:
                # This would check actual collaboration dates
                # For now, allow all
                pass
            
            if not recent_collaboration:
                filtered.append(candidate)
        
        return filtered
    
    async def _get_creator_profile(self, creator_id: str) -> Optional[CreatorProfile]:
        """Get creator profile from storage"""



        try:
            # Try cache first
            cache_key = f"creator_profile:{creator_id}"
            cached_profile = await self.cache.get(cache_key)
            
            if cached_profile:
                return CreatorProfile(**cached_profile)
            
            # Get from database
            profile_data = await self._fetch_creator_data(creator_id)
            
            if profile_data:
                profile = CreatorProfile(**profile_data)
                # Cache for 1 hour
                await self.cache.set(cache_key, profile.__dict__, ttl=3600)
                return profile
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting creator profile: {e}")
            return None
    
    async def _fetch_creator_data(self, creator_id: str) -> Optional[Dict[str, Any]]:
        """Fetch creator data from database"""
        # This would query your creator database
        # For now, return mock data
        return {
            'creator_id': creator_id,
            'name': f'Creator {creator_id}',
            'platform_handles': {'instagram': f'@creator{creator_id}'},
            'content_categories': ['music', 'lifestyle'],
            'audience_demographics': {
                'age_groups': {'18-24': 0.3, '25-34': 0.4, '35-44': 0.3},
                'gender': {'male': 0.4, 'female': 0.6},
                'locations': {'US': 0.5, 'UK': 0.2, 'CA': 0.3},
                'interests': {'music': 0.8, 'lifestyle': 0.6, 'fashion': 0.4}
            },
            'engagement_metrics': {
                'engagement_rate': 0.06,
                'follower_count': 25000,
                'posting_frequency': 4,
                'response_rate': 0.15
            },
            'content_style': 'creative',
            'collaboration_preferences': {
                'types': ['content_creation', 'cross_promotion'],
                'frequency': 'monthly'
            },
            'availability': {'timezone': 'UTC', 'preferred_days': ['weekdays']},
            'past_collaborations': [],
            'brand_values': ['authenticity', 'creativity', 'community'],
            'expertise_areas': ['music_production', 'content_creation'],
            'growth_metrics': {'growth_rate': 0.15},
            'geographic_location': 'US',
            'language_preferences': ['english']
        }
    
    def _generate_id(self) -> str:
        """Generate unique match ID"""



        return hashlib.md5(f"{datetime.now().isoformat()}{hash(self)}".encode()).hexdigest()[:12]


class CreatorMatchingEngine:
    """
    Enhanced creator matching with machine learning optimization
    
    Uses advanced algorithms to continuously improve matching accuracy
    based on collaboration success feedback.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize creator matching engine"""
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # ML Models
        self.matching_model = None
        self.feedback_model = None
        
        self._initialize_matching_models()
    
    def _initialize_matching_models(self):
        """Initialize ML models for enhanced matching"""



        try:
            # Advanced matching neural network
            class AdvancedMatchingModel(nn.Module):
                def __init__(self, input_size: int = 300, hidden_size: int = 256):
                    super().__init__()
                    self.fc1 = nn.Linear(input_size, hidden_size)
                    self.fc2 = nn.Linear(hidden_size, 128)
                    self.fc3 = nn.Linear(128, 64)
                    self.fc4 = nn.Linear(64, 32)
                    self.fc5 = nn.Linear(32, 1)
                    self.dropout = nn.Dropout(0.3)
                    self.relu = nn.ReLU()
                    self.sigmoid = nn.Sigmoid()
                    self.batch_norm1 = nn.BatchNorm1d(hidden_size)
                    self.batch_norm2 = nn.BatchNorm1d(128)
                
                def forward(self, x):
                    x = self.batch_norm1(self.relu(self.fc1(x)))
                    x = self.dropout(x)
                    x = self.batch_norm2(self.relu(self.fc2(x)))
                    x = self.dropout(x)
                    x = self.relu(self.fc3(x))
                    x = self.dropout(x)
                    x = self.relu(self.fc4(x))
                    x = self.sigmoid(self.fc5(x))
                    return x
            
            self.matching_model = AdvancedMatchingModel()
            
            self.logger.info("Enhanced matching models initialized")
            
        except Exception as e:
            self.logger.error(f"Error initializing matching models: {e}")
            raise
    
    async def learn_from_collaboration_feedback(
        self,
        collaboration_id: str,
        success_score: float,
        feedback_data: Dict[str, Any]
    ) -> bool:
        """Learn from collaboration outcomes to improve matching"""



        try:
            # Process feedback to improve future matching
            # This would involve retraining or updating the models
            
            self.logger.info(f"Processing feedback for collaboration {collaboration_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error processing collaboration feedback: {e}")
            return False
