"""Collaboration Finder - Advanced AI-Powered Creator Partnership Engine
===================================================================

This module provides intelligent creator matching, collaboration opportunity
discovery, and partnership optimization for content creators and influencers.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

WARNING: Proprietary code - Unauthorized use prohibited and legally prosecuted.
"""
import asyncio
import logging
from typing import Dict, List, Optional, Union, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime, timezone, timedelta
import json
import statistics
from collections import defaultdict, Counter

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import networkx as nx

from backend.core.config import get_settings
from backend.core.logging import get_logger
from backend.analytics.creator_analytics import CreatorAnalyticsService
from backend.ai.ml.collaboration_predictor import CollaborationPredictionEngine
from backend.integrations.social_graph import SocialGraphAnalyzer

logger = get_logger(__name__)
settings = get_settings()


class CollaborationType(Enum):
    """Types of creator collaborations."""
    DUET = "duet"                    # TikTok duets, Instagram collaborations
    GUEST_APPEARANCE = "guest_appearance"  # Podcast/video guests
    JOINT_CONTENT = "joint_content"   # Shared content creation
    CROSS_PROMOTION = "cross_promotion"  # Mutual promotion
    CHALLENGE = "challenge"          # Joint challenges/trends
    BRAND_CAMPAIGN = "brand_campaign"  # Brand partnership collaboration
    COURSE_COLLAB = "course_collab"   # Educational content collaboration
    TOUR_COLLAB = "tour_collab"      # Joint tours/events
    REMIX = "remix"                  # Music remixes, content remixes
    PLAYLIST = "playlist"            # Collaborative playlists


class MatchingCriteria(Enum):
    """Criteria for creator matching."""
    AUDIENCE_OVERLAP = "audience_overlap"
    CONTENT_SIMILARITY = "content_similarity"
    ENGAGEMENT_COMPATIBILITY = "engagement_compatibility"
    BRAND_ALIGNMENT = "brand_alignment"
    GEOGRAPHIC_PROXIMITY = "geographic_proximity"
    COMPLEMENTARY_SKILLS = "complementary_skills"
    MUTUAL_BENEFIT = "mutual_benefit"
    AUTHENTICITY_FIT = "authenticity_fit"


class CollaborationStatus(Enum):
    """Status of collaboration opportunities."""
    POTENTIAL = "potential"
    RECOMMENDED = "recommended"
    CONTACTED = "contacted"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    DECLINED = "declined"


@dataclass
class CreatorProfile:
    """Comprehensive creator profile for matching."""
    creator_id: str
    display_name: str
    platforms: List[str]
    primary_platform: str
    content_categories: List[str]
    audience_size: Dict[str, int]
    engagement_rates: Dict[str, float]
    demographics: Dict[str, Any]
    content_style: Dict[str, Any]
    brand_partnerships: List[str]
    collaboration_history: List[str]
    availability: Dict[str, Any]
    rates: Dict[str, float]
    location: Dict[str, str]
    languages: List[str]
    verified_status: Dict[str, bool]


@dataclass
class MatchingScore:
    """Detailed matching score between creators."""
    overall_score: float
    criteria_scores: Dict[MatchingCriteria, float]
    confidence_level: str
    explanation: List[str]
    potential_synergies: List[str]
    risk_factors: List[str]
    recommended_collab_types: List[CollaborationType]


@dataclass
class CollaborationOpportunity:
    """Detailed collaboration opportunity."""
    opportunity_id: str
    creator_a: CreatorProfile
    creator_b: CreatorProfile
    collaboration_type: CollaborationType
    matching_score: MatchingScore
    estimated_reach: int
    estimated_engagement: float
    mutual_benefit_score: float
    effort_required: str
    timeline: Dict[str, str]
    success_probability: float
    revenue_potential: Dict[str, float]
    content_ideas: List[str]
    next_steps: List[str]
    generated_at: datetime


@dataclass
class CollaborationCampaign:
    """Multi-creator collaboration campaign."""
    campaign_id: str
    campaign_name: str
    campaign_type: str
    participating_creators: List[CreatorProfile]
    collaboration_opportunities: List[CollaborationOpportunity]
    expected_outcomes: Dict[str, Any]
    budget_requirements: Dict[str, float]
    timeline: Dict[str, datetime]
    performance_metrics: Dict[str, float]
    status: CollaborationStatus
    created_at: datetime


class InfluencerMatchingEngine:
    """
    Advanced AI-powered influencer matching engine that finds optimal
    collaboration opportunities between creators.
    """
    
    def __init__(self):
        """Initialize the influencer matching engine."""
        self.analytics_service = CreatorAnalyticsService()
        self.prediction_engine = CollaborationPredictionEngine()
        self.social_graph = SocialGraphAnalyzer()
        
        # ML models for matching
        self.similarity_model = RandomForestClassifier(n_estimators=100)
        self.content_vectorizer = TfidfVectorizer(max_features=1000)
        self.clustering_model = KMeans(n_clusters=20)
        self.scaler = StandardScaler()
        
        # Matching weights for different criteria
        self.matching_weights = {
            MatchingCriteria.AUDIENCE_OVERLAP: 0.25,
            MatchingCriteria.CONTENT_SIMILARITY: 0.20,
            MatchingCriteria.ENGAGEMENT_COMPATIBILITY: 0.15,
            MatchingCriteria.BRAND_ALIGNMENT: 0.15,
            MatchingCriteria.GEOGRAPHIC_PROXIMITY: 0.05,
            MatchingCriteria.COMPLEMENTARY_SKILLS: 0.10,
            MatchingCriteria.MUTUAL_BENEFIT: 0.10
        }
        
        # Collaboration type compatibility matrix
        self.content_type_compatibility = self._initialize_compatibility_matrix()
        
        # Platform-specific collaboration preferences
        self.platform_collab_preferences = self._initialize_platform_preferences()
        
        # Load and train models
        self._load_and_train_models()
        
        logger.info("Influencer matching engine initialized successfully")
    
    def _initialize_compatibility_matrix(self) -> Dict[str, Dict[CollaborationType, float]]:
        """Initialize content type compatibility matrix for collaborations."""
        
        return {
            'music': {
                CollaborationType.DUET: 0.9,
                CollaborationType.REMIX: 0.95,
                CollaborationType.PLAYLIST: 0.8,
                CollaborationType.JOINT_CONTENT: 0.7,
                CollaborationType.TOUR_COLLAB: 0.85,
                CollaborationType.BRAND_CAMPAIGN: 0.6,
                CollaborationType.CHALLENGE: 0.75
            },
            'comedy': {
                CollaborationType.DUET: 0.85,
                CollaborationType.JOINT_CONTENT: 0.9,
                CollaborationType.CHALLENGE: 0.8,
                CollaborationType.GUEST_APPEARANCE: 0.7,
                CollaborationType.CROSS_PROMOTION: 0.75,
                CollaborationType.BRAND_CAMPAIGN: 0.6
            },
            'educational': {
                CollaborationType.GUEST_APPEARANCE: 0.9,
                CollaborationType.COURSE_COLLAB: 0.95,
                CollaborationType.JOINT_CONTENT: 0.8,
                CollaborationType.CROSS_PROMOTION: 0.7,
                CollaborationType.BRAND_CAMPAIGN: 0.75
            },
            'lifestyle': {
                CollaborationType.JOINT_CONTENT: 0.85,
                CollaborationType.BRAND_CAMPAIGN: 0.9,
                CollaborationType.CROSS_PROMOTION: 0.8,
                CollaborationType.CHALLENGE: 0.7,
                CollaborationType.GUEST_APPEARANCE: 0.6
            },
            'gaming': {
                CollaborationType.JOINT_CONTENT: 0.9,
                CollaborationType.CHALLENGE: 0.85,
                CollaborationType.GUEST_APPEARANCE: 0.7,
                CollaborationType.BRAND_CAMPAIGN: 0.8,
                CollaborationType.CROSS_PROMOTION: 0.75
            },
            'fitness': {
                CollaborationType.CHALLENGE: 0.9,
                CollaborationType.JOINT_CONTENT: 0.8,
                CollaborationType.BRAND_CAMPAIGN: 0.85,
                CollaborationType.CROSS_PROMOTION: 0.7,
                CollaborationType.COURSE_COLLAB: 0.75
            },
            'food': {
                CollaborationType.JOINT_CONTENT: 0.9,
                CollaborationType.BRAND_CAMPAIGN: 0.85,
                CollaborationType.CHALLENGE: 0.8,
                CollaborationType.CROSS_PROMOTION: 0.7,
                CollaborationType.GUEST_APPEARANCE: 0.6
            },
            'beauty': {
                CollaborationType.JOINT_CONTENT: 0.85,
                CollaborationType.BRAND_CAMPAIGN: 0.9,
                CollaborationType.CHALLENGE: 0.8,
                CollaborationType.CROSS_PROMOTION: 0.75,
                CollaborationType.GUEST_APPEARANCE: 0.65
            }
        }
    
    def _initialize_platform_preferences(self) -> Dict[str, Dict[CollaborationType, float]]:
        """Initialize platform-specific collaboration preferences."""
        
        return {
            'tiktok': {
                CollaborationType.DUET: 0.95,
                CollaborationType.CHALLENGE: 0.9,
                CollaborationType.REMIX: 0.85,
                CollaborationType.JOINT_CONTENT: 0.8,
                CollaborationType.CROSS_PROMOTION: 0.7
            },
            'instagram': {
                CollaborationType.JOINT_CONTENT: 0.9,
                CollaborationType.BRAND_CAMPAIGN: 0.85,
                CollaborationType.CROSS_PROMOTION: 0.8,
                CollaborationType.CHALLENGE: 0.75,
                CollaborationType.GUEST_APPEARANCE: 0.7
            },
            'youtube': {
                CollaborationType.GUEST_APPEARANCE: 0.9,
                CollaborationType.JOINT_CONTENT: 0.85,
                CollaborationType.COURSE_COLLAB: 0.8,
                CollaborationType.BRAND_CAMPAIGN: 0.75,
                CollaborationType.CROSS_PROMOTION: 0.7
            },
            'spotify': {
                CollaborationType.REMIX: 0.95,
                CollaborationType.PLAYLIST: 0.9,
                CollaborationType.JOINT_CONTENT: 0.8,
                CollaborationType.TOUR_COLLAB: 0.75,
                CollaborationType.BRAND_CAMPAIGN: 0.6
            },
            'twitter': {
                CollaborationType.CROSS_PROMOTION: 0.9,
                CollaborationType.CHALLENGE: 0.8,
                CollaborationType.JOINT_CONTENT: 0.7,
                CollaborationType.BRAND_CAMPAIGN: 0.65,
                CollaborationType.GUEST_APPEARANCE: 0.6
            }
        }
    
    def _load_and_train_models(self):
        """Load historical data and train ML models for creator matching."""
        try:
            # Generate synthetic training data for creator matching
            n_samples = 15000
            
            # Features: audience overlap, content similarity, engagement compatibility, etc.
            features = np.random.rand(n_samples, 12)
            
            # Add realistic patterns to synthetic data
            for i in range(n_samples):
                # Simulate audience overlap patterns
                features[i][0] = np.random.beta(2, 5)  # Audience overlap (typically low)
                features[i][1] = np.random.normal(0.7, 0.2)  # Content similarity
                features[i][2] = np.random.normal(0.6, 0.15)  # Engagement compatibility
                
                # Add correlation between features
                if features[i][0] > 0.7:  # High audience overlap
                    features[i][1] *= 0.8  # Might reduce content similarity need
                
                if features[i][1] > 0.8:  # High content similarity
                    features[i][2] *= 1.2  # Likely better engagement compatibility
            
            # Generate binary targets (successful collaboration or not)
            # Based on combination of features
            collaboration_success = (
                features[:, 0] * 0.3 +  # Audience overlap
                features[:, 1] * 0.25 + # Content similarity
                features[:, 2] * 0.2 +  # Engagement compatibility
                np.random.rand(n_samples) * 0.25  # Random factors
            ) > 0.6
            
            # Train similarity model
            self.similarity_model.fit(features, collaboration_success)
            
            # Train clustering model on creator features
            creator_features = features[:, :8]  # First 8 features represent creator characteristics
            self.clustering_model.fit(creator_features)
            
            # Fit scaler
            self.scaler.fit(features)
            
            logger.info("Creator matching ML models trained successfully")
            
        except Exception as e:
            logger.error(f"Failed to train creator matching models: {e}")
            # Continue with default models
    
    async def find_collaboration_matches(
        self,
        target_creator: CreatorProfile,
        candidate_creators: List[CreatorProfile],
        collaboration_types: List[CollaborationType] = None,
        max_matches: int = 10
    ) -> List[CollaborationOpportunity]:
        """
        Find optimal collaboration matches for a target creator.
        
        Args:
            target_creator: The creator seeking collaborations
            candidate_creators: List of potential collaboration partners
            collaboration_types: Preferred collaboration types
            max_matches: Maximum number of matches to return
            
        Returns:
            List of ranked collaboration opportunities
        """
        
        try:
            opportunities = []
            
            for candidate in candidate_creators:
                if candidate.creator_id == target_creator.creator_id:
                    continue
                
                # Calculate matching score
                matching_score = await self._calculate_matching_score(
                    target_creator, candidate
                )
                
                # Skip low-scoring matches
                if matching_score.overall_score < 0.3:
                    continue
                
                # Determine best collaboration types
                best_collab_types = self._determine_best_collaboration_types(
                    target_creator, candidate, collaboration_types
                )
                
                for collab_type in best_collab_types[:2]:  # Top 2 types
                    # Generate collaboration opportunity
                    opportunity = await self._generate_collaboration_opportunity(
                        target_creator, candidate, collab_type, matching_score
                    )
                    
                    opportunities.append(opportunity)
            
            # Sort by overall potential and return top matches
            opportunities.sort(
                key=lambda x: x.matching_score.overall_score * x.success_probability,
                reverse=True
            )
            
            return opportunities[:max_matches]
            
        except Exception as e:
            logger.error(f"Failed to find collaboration matches: {e}")
            return []
    
    async def _calculate_matching_score(
        self, creator_a: CreatorProfile, creator_b: CreatorProfile
    ) -> MatchingScore:
        """Calculate comprehensive matching score between two creators."""
        
        criteria_scores = {}
        explanations = []
        synergies = []
        risks = []
        
        # 1. Audience Overlap Analysis
        audience_overlap = self._calculate_audience_overlap(creator_a, creator_b)
        criteria_scores[MatchingCriteria.AUDIENCE_OVERLAP] = audience_overlap
        
        if audience_overlap > 0.7:
            risks.append("High audience overlap may limit growth potential")
        elif audience_overlap < 0.1:
            risks.append("Very low audience overlap may reduce collaboration impact")
        else:
            synergies.append(f"Optimal audience overlap ({audience_overlap:.1%}) for cross-pollination")
        
        # 2. Content Similarity
        content_similarity = self._calculate_content_similarity(creator_a, creator_b)
        criteria_scores[MatchingCriteria.CONTENT_SIMILARITY] = content_similarity
        
        if content_similarity > 0.8:
            synergies.append("High content alignment enables seamless collaboration")
        elif content_similarity < 0.3:
            synergies.append("Complementary content styles offer unique collaboration potential")
        
        # 3. Engagement Compatibility
        engagement_compatibility = self._calculate_engagement_compatibility(creator_a, creator_b)
        criteria_scores[MatchingCriteria.ENGAGEMENT_COMPATIBILITY] = engagement_compatibility
        
        if engagement_compatibility > 0.7:
            synergies.append("Compatible engagement patterns support mutual growth")
        
        # 4. Brand Alignment
        brand_alignment = self._calculate_brand_alignment(creator_a, creator_b)
        criteria_scores[MatchingCriteria.BRAND_ALIGNMENT] = brand_alignment
        
        if brand_alignment > 0.8:
            synergies.append("Strong brand alignment supports authentic partnerships")
        elif brand_alignment < 0.4:
            risks.append("Brand misalignment may affect collaboration authenticity")
        
        # 5. Geographic Proximity (less important for digital collaborations)
        geographic_score = self._calculate_geographic_proximity(creator_a, creator_b)
        criteria_scores[MatchingCriteria.GEOGRAPHIC_PROXIMITY] = geographic_score
        
        # 6. Complementary Skills
        skills_complement = self._calculate_complementary_skills(creator_a, creator_b)
        criteria_scores[MatchingCriteria.COMPLEMENTARY_SKILLS] = skills_complement
        
        if skills_complement > 0.7:
            synergies.append("Complementary skills create valuable learning opportunities")
        
        # 7. Mutual Benefit Potential
        mutual_benefit = self._calculate_mutual_benefit(creator_a, creator_b)
        criteria_scores[MatchingCriteria.MUTUAL_BENEFIT] = mutual_benefit
        
        # Calculate weighted overall score
        overall_score = sum(
            score * self.matching_weights.get(criteria, 0.1)
            for criteria, score in criteria_scores.items()
        )
        
        # Determine confidence level
        score_variance = np.var(list(criteria_scores.values()))
        if score_variance < 0.05 and overall_score > 0.7:
            confidence = "high"
        elif score_variance < 0.1 and overall_score > 0.5:
            confidence = "medium"
        else:
            confidence = "low"
        
        # Generate explanations
        explanations = self._generate_matching_explanations(criteria_scores, overall_score)
        
        # Recommend collaboration types
        recommended_types = self._recommend_collaboration_types(
            creator_a, creator_b, criteria_scores
        )
        
        return MatchingScore(
            overall_score=overall_score,
            criteria_scores=criteria_scores,
            confidence_level=confidence,
            explanation=explanations,
            potential_synergies=synergies,
            risk_factors=risks,
            recommended_collab_types=recommended_types
        )
    
    def _calculate_audience_overlap(
        self, creator_a: CreatorProfile, creator_b: CreatorProfile
    ) -> float:
        """Calculate audience overlap between two creators."""
        
        # Analyze demographic overlap
        demo_a = creator_a.demographics
        demo_b = creator_b.demographics
        
        overlap_scores = []
        
        # Age overlap
        age_a = demo_a.get('age_distribution', {})
        age_b = demo_b.get('age_distribution', {})
        age_overlap = self._calculate_distribution_overlap(age_a, age_b)
        overlap_scores.append(age_overlap)
        
        # Gender overlap
        gender_a = demo_a.get('gender_distribution', {})
        gender_b = demo_b.get('gender_distribution', {})
        gender_overlap = self._calculate_distribution_overlap(gender_a, gender_b)
        overlap_scores.append(gender_overlap)
        
        # Location overlap
        location_a = demo_a.get('location_distribution', {})
        location_b = demo_b.get('location_distribution', {})
        location_overlap = self._calculate_distribution_overlap(location_a, location_b)
        overlap_scores.append(location_overlap)
        
        # Interest overlap (based on content categories)
        interests_a = set(creator_a.content_categories)
        interests_b = set(creator_b.content_categories)
        
        if interests_a and interests_b:
            interest_overlap = len(interests_a & interests_b) / len(interests_a | interests_b)
        else:
            interest_overlap = 0
        
        overlap_scores.append(interest_overlap)
        
        # Calculate weighted average
        weights = [0.3, 0.2, 0.2, 0.3]  # Age, gender, location, interests
        
        return sum(score * weight for score, weight in zip(overlap_scores, weights))
    
    def _calculate_distribution_overlap(
        self, dist_a: Dict[str, float], dist_b: Dict[str, float]
    ) -> float:
        """Calculate overlap between two probability distributions."""
        
        if not dist_a or not dist_b:
            return 0
        
        # Get all keys
        all_keys = set(dist_a.keys()) | set(dist_b.keys())
        
        # Calculate overlap using minimum values
        overlap = 0
        for key in all_keys:
            val_a = dist_a.get(key, 0)
            val_b = dist_b.get(key, 0)
            overlap += min(val_a, val_b)
        
        return overlap
    
    def _calculate_content_similarity(
        self, creator_a: CreatorProfile, creator_b: CreatorProfile
    ) -> float:
        """Calculate content similarity between two creators."""
        
        # Content category similarity
        categories_a = set(creator_a.content_categories)
        categories_b = set(creator_b.content_categories)
        
        if categories_a and categories_b:
            category_similarity = len(categories_a & categories_b) / len(categories_a | categories_b)
        else:
            category_similarity = 0
        
        # Content style similarity
        style_a = creator_a.content_style
        style_b = creator_b.content_style
        
        style_scores = []
        
        # Compare style attributes
        style_attributes = ['tone', 'format_preferences', 'posting_frequency', 'content_length']
        
        for attr in style_attributes:
            val_a = style_a.get(attr, '')
            val_b = style_b.get(attr, '')
            
            if isinstance(val_a, str) and isinstance(val_b, str):
                # String similarity (simple)
                similarity = 1.0 if val_a == val_b else 0.5 if val_a and val_b else 0.0
            elif isinstance(val_a, (int, float)) and isinstance(val_b, (int, float)):
                # Numeric similarity
                if val_a == 0 and val_b == 0:
                    similarity = 1.0
                elif val_a == 0 or val_b == 0:
                    similarity = 0.0
                else:
                    similarity = 1 - abs(val_a - val_b) / max(val_a, val_b)
            else:
                similarity = 0.0
            
            style_scores.append(similarity)
        
        style_similarity = np.mean(style_scores) if style_scores else 0
        
        # Platform overlap
        platforms_a = set(creator_a.platforms)
        platforms_b = set(creator_b.platforms)
        
        if platforms_a and platforms_b:
            platform_overlap = len(platforms_a & platforms_b) / len(platforms_a | platforms_b)
        else:
            platform_overlap = 0
        
        # Weighted combination
        return (
            category_similarity * 0.4 +
            style_similarity * 0.4 +
            platform_overlap * 0.2
        )
    
    def _calculate_engagement_compatibility(
        self, creator_a: CreatorProfile, creator_b: CreatorProfile
    ) -> float:
        """Calculate engagement rate compatibility between creators."""
        
        # Get engagement rates for common platforms
        common_platforms = set(creator_a.platforms) & set(creator_b.platforms)
        
        if not common_platforms:
            return 0.5  # Neutral score for no common platforms
        
        compatibility_scores = []
        
        for platform in common_platforms:
            rate_a = creator_a.engagement_rates.get(platform, 0)
            rate_b = creator_b.engagement_rates.get(platform, 0)
            
            if rate_a > 0 and rate_b > 0:
                # Calculate similarity (closer rates = better compatibility)
                ratio = min(rate_a, rate_b) / max(rate_a, rate_b)
                compatibility_scores.append(ratio)
        
        if compatibility_scores:
            return np.mean(compatibility_scores)
        else:
            return 0.5
    
    def _calculate_brand_alignment(
        self, creator_a: CreatorProfile, creator_b: CreatorProfile
    ) -> float:
        """Calculate brand alignment between creators."""
        
        # Check for common brand partnerships
        brands_a = set(creator_a.brand_partnerships)
        brands_b = set(creator_b.brand_partnerships)
        
        if brands_a and brands_b:
            common_brands = len(brands_a & brands_b)
            total_brands = len(brands_a | brands_b)
            brand_overlap = common_brands / total_brands
        else:
            brand_overlap = 0.5  # Neutral if no brand data
        
        # Check content category alignment for brand safety
        categories_a = set(creator_a.content_categories)
        categories_b = set(creator_b.content_categories)
        
        # Define compatible category pairs
        compatible_categories = {
            ('fitness', 'nutrition'), ('beauty', 'fashion'), ('gaming', 'tech'),
            ('music', 'entertainment'), ('education', 'productivity'), ('travel', 'lifestyle')
        }
        
        category_compatibility = 0
        for cat_a in categories_a:
            for cat_b in categories_b:
                if cat_a == cat_b or (cat_a, cat_b) in compatible_categories or (cat_b, cat_a) in compatible_categories:
                    category_compatibility = 1
                    break
        
        return (brand_overlap * 0.6 + category_compatibility * 0.4)
    
    def _calculate_geographic_proximity(
        self, creator_a: CreatorProfile, creator_b: CreatorProfile
    ) -> float:
        """Calculate geographic proximity score."""
        
        location_a = creator_a.location
        location_b = creator_b.location
        
        if not location_a or not location_b:
            return 0.5  # Neutral score for missing location data
        
        # Check for same country
        country_a = location_a.get('country', '')
        country_b = location_b.get('country', '')
        
        if country_a == country_b and country_a:
            # Same country - check for same region/state
            region_a = location_a.get('region', '')
            region_b = location_b.get('region', '')
            
            if region_a == region_b and region_a:
                return 1.0  # Same region
            else:
                return 0.7  # Same country, different region
        else:
            # Different countries - check for same continent/timezone
            # This would use actual geographic data in production
            return 0.3  # Different countries
    
    def _calculate_complementary_skills(
        self, creator_a: CreatorProfile, creator_b: CreatorProfile
    ) -> float:
        """Calculate complementary skills score."""
        
        # Analyze content categories for complementarity
        categories_a = set(creator_a.content_categories)
        categories_b = set(creator_b.content_categories)
        
        # Define complementary skill pairs
        complementary_pairs = {
            ('music', 'video_editing'), ('writing', 'design'), ('comedy', 'acting'),
            ('fitness', 'nutrition'), ('tech', 'education'), ('beauty', 'photography')
        }
        
        complement_score = 0
        for cat_a in categories_a:
            for cat_b in categories_b:
                if (cat_a, cat_b) in complementary_pairs or (cat_b, cat_a) in complementary_pairs:
                    complement_score = 1
                    break
        
        # Analyze audience size complementarity (larger creator helping smaller)
        total_audience_a = sum(creator_a.audience_size.values())
        total_audience_b = sum(creator_b.audience_size.values())
        
        if total_audience_a > 0 and total_audience_b > 0:
            size_ratio = min(total_audience_a, total_audience_b) / max(total_audience_a, total_audience_b)
            # Sweet spot is when one creator is 2-5x larger than the other
            if 0.2 <= size_ratio <= 0.5:
                size_complement = 0.8
            elif 0.5 < size_ratio <= 0.8:
                size_complement = 0.6
            else:
                size_complement = 0.4
        else:
            size_complement = 0.5
        
        return (complement_score * 0.6 + size_complement * 0.4)
    
    def _calculate_mutual_benefit(
        self, creator_a: CreatorProfile, creator_b: CreatorProfile
    ) -> float:
        """Calculate mutual benefit potential."""
        
        # Analyze potential benefits for each creator
        benefit_a = self._calculate_individual_benefit(creator_a, creator_b)
        benefit_b = self._calculate_individual_benefit(creator_b, creator_a)
        
        # Mutual benefit is the minimum of individual benefits
        # (collaboration should benefit both parties)
        return min(benefit_a, benefit_b)
    
    def _calculate_individual_benefit(
        self, beneficiary: CreatorProfile, partner: CreatorProfile
    ) -> float:
        """Calculate benefit for individual creator from collaboration."""
        
        benefits = []
        
        # Audience growth potential
        partner_audience = sum(partner.audience_size.values())
        beneficiary_audience = sum(beneficiary.audience_size.values())
        
        if partner_audience > beneficiary_audience:
            audience_benefit = min(0.9, (partner_audience - beneficiary_audience) / beneficiary_audience * 0.1)
        else:
            audience_benefit = 0.3  # Still benefits from exposure
        
        benefits.append(audience_benefit)
        
        # Content variety benefit
        partner_categories = set(partner.content_categories)
        beneficiary_categories = set(beneficiary.content_categories)
        
        new_categories = len(partner_categories - beneficiary_categories)
        content_benefit = min(0.8, new_categories / max(len(beneficiary_categories), 1) * 0.5)
        benefits.append(content_benefit)
        
        # Platform expansion benefit
        partner_platforms = set(partner.platforms)
        beneficiary_platforms = set(beneficiary.platforms)
        
        new_platforms = len(partner_platforms - beneficiary_platforms)
        platform_benefit = min(0.7, new_platforms / max(len(beneficiary_platforms), 1) * 0.3)
        benefits.append(platform_benefit)
        
        return np.mean(benefits)
    
    def _generate_matching_explanations(
        self, criteria_scores: Dict[MatchingCriteria, float], overall_score: float
    ) -> List[str]:
        """Generate human-readable explanations for matching scores."""
        
        explanations = []
        
        # Overall score explanation
        if overall_score > 0.8:
            explanations.append("Excellent collaboration potential with strong alignment across key metrics")
        elif overall_score > 0.6:
            explanations.append("Good collaboration potential with solid compatibility")
        elif overall_score > 0.4:
            explanations.append("Moderate collaboration potential with some challenges to address")
        else:
            explanations.append("Limited collaboration potential due to misalignment in key areas")
        
        # Specific criteria explanations
        for criteria, score in criteria_scores.items():
            if score > 0.8:
                explanations.append(f"Strong {criteria.value.replace('_', ' ')}: {score:.1%}")
            elif score < 0.3:
                explanations.append(f"Improvement needed in {criteria.value.replace('_', ' ')}: {score:.1%}")
        
        return explanations
    
    def _recommend_collaboration_types(
        self,
        creator_a: CreatorProfile,
        creator_b: CreatorProfile,
        criteria_scores: Dict[MatchingCriteria, float]
    ) -> List[CollaborationType]:
        """Recommend specific collaboration types based on compatibility."""
        
        recommendations = []
        
        # Analyze creator characteristics
        primary_category_a = creator_a.content_categories[0] if creator_a.content_categories else 'general'
        primary_category_b = creator_b.content_categories[0] if creator_b.content_categories else 'general'
        
        # Get compatibility matrix for content types
        compat_a = self.content_type_compatibility.get(primary_category_a, {})
        compat_b = self.content_type_compatibility.get(primary_category_b, {})
        
        # Score each collaboration type
        type_scores = []
        
        for collab_type in CollaborationType:
            score = 0
            
            # Content compatibility
            content_score = (compat_a.get(collab_type, 0.5) + compat_b.get(collab_type, 0.5)) / 2
            score += content_score * 0.4
            
            # Platform compatibility
            common_platforms = set(creator_a.platforms) & set(creator_b.platforms)
            if common_platforms:
                platform_scores = []
                for platform in common_platforms:
                    platform_prefs = self.platform_collab_preferences.get(platform, {})
                    platform_score = platform_prefs.get(collab_type, 0.5)
                    platform_scores.append(platform_score)
                
                avg_platform_score = np.mean(platform_scores)
                score += avg_platform_score * 0.3
            
            # Audience compatibility
            audience_overlap = criteria_scores.get(MatchingCriteria.AUDIENCE_OVERLAP, 0.5)
            
            # Different types work better with different overlap levels
            if collab_type in [CollaborationType.CROSS_PROMOTION, CollaborationType.GUEST_APPEARANCE]:
                # Lower overlap better for cross-promotion
                audience_factor = 1 - audience_overlap
            else:
                # Higher overlap better for joint content
                audience_factor = audience_overlap
            
            score += audience_factor * 0.3
            
            type_scores.append((collab_type, score))
        
        # Sort by score and return top recommendations
        type_scores.sort(key=lambda x: x[1], reverse=True)
        
        return [collab_type for collab_type, score in type_scores[:5] if score > 0.4]
    
    def _determine_best_collaboration_types(
        self,
        target_creator: CreatorProfile,
        candidate: CreatorProfile,
        preferred_types: List[CollaborationType] = None
    ) -> List[CollaborationType]:
        """Determine best collaboration types for a creator pair."""
        
        # Get recommended types
        recommended = self._recommend_collaboration_types(target_creator, candidate, {})
        
        # Filter by preferred types if specified
        if preferred_types:
            recommended = [t for t in recommended if t in preferred_types]
        
        return recommended[:3]  # Return top 3
    
    async def _generate_collaboration_opportunity(
        self,
        creator_a: CreatorProfile,
        creator_b: CreatorProfile,
        collaboration_type: CollaborationType,
        matching_score: MatchingScore
    ) -> CollaborationOpportunity:
        """Generate detailed collaboration opportunity."""
        
        # Calculate estimated reach
        reach_a = sum(creator_a.audience_size.values())
        reach_b = sum(creator_b.audience_size.values())
        
        # Account for audience overlap
        overlap = matching_score.criteria_scores.get(MatchingCriteria.AUDIENCE_OVERLAP, 0.3)
        estimated_reach = int(reach_a + reach_b * (1 - overlap))
        
        # Calculate estimated engagement
        avg_engagement_a = np.mean(list(creator_a.engagement_rates.values())) if creator_a.engagement_rates else 0.05
        avg_engagement_b = np.mean(list(creator_b.engagement_rates.values())) if creator_b.engagement_rates else 0.05
        
        # Collaboration typically boosts engagement
        collaboration_boost = 1.2
        estimated_engagement = (avg_engagement_a + avg_engagement_b) / 2 * collaboration_boost
        
        # Calculate mutual benefit score
        mutual_benefit_score = matching_score.criteria_scores.get(MatchingCriteria.MUTUAL_BENEFIT, 0.5)
        
        # Determine effort required
        effort_mapping = {
            CollaborationType.CROSS_PROMOTION: "Low",
            CollaborationType.CHALLENGE: "Low",
            CollaborationType.DUET: "Medium",
            CollaborationType.JOINT_CONTENT: "Medium",
            CollaborationType.GUEST_APPEARANCE: "Medium",
            CollaborationType.REMIX: "Medium",
            CollaborationType.BRAND_CAMPAIGN: "High",
            CollaborationType.COURSE_COLLAB: "High",
            CollaborationType.TOUR_COLLAB: "High",
            CollaborationType.PLAYLIST: "Low"
        }
        
        effort_required = effort_mapping.get(collaboration_type, "Medium")
        
        # Create timeline
        timeline = self._generate_collaboration_timeline(collaboration_type)
        
        # Calculate success probability
        success_probability = min(0.9, matching_score.overall_score * 0.8 + 0.2)
        
        # Calculate revenue potential
        revenue_potential = self._calculate_revenue_potential(
            creator_a, creator_b, collaboration_type, estimated_reach
        )
        
        # Generate content ideas
        content_ideas = self._generate_content_ideas(
            creator_a, creator_b, collaboration_type
        )
        
        # Generate next steps
        next_steps = self._generate_next_steps(collaboration_type)
        
        return CollaborationOpportunity(
            opportunity_id=f"collab_{creator_a.creator_id}_{creator_b.creator_id}_{int(datetime.now().timestamp())}",
            creator_a=creator_a,
            creator_b=creator_b,
            collaboration_type=collaboration_type,
            matching_score=matching_score,
            estimated_reach=estimated_reach,
            estimated_engagement=estimated_engagement,
            mutual_benefit_score=mutual_benefit_score,
            effort_required=effort_required,
            timeline=timeline,
            success_probability=success_probability,
            revenue_potential=revenue_potential,
            content_ideas=content_ideas,
            next_steps=next_steps,
            generated_at=datetime.now(timezone.utc)
        )
    
    def _generate_collaboration_timeline(self, collaboration_type: CollaborationType) -> Dict[str, str]:
        """Generate timeline for collaboration type."""
        
        timeline_templates = {
            CollaborationType.CROSS_PROMOTION: {
                "planning": "1 week",
                "execution": "2 weeks",
                "total_duration": "3 weeks"
            },
            CollaborationType.DUET: {
                "planning": "3 days",
                "execution": "1 week",
                "total_duration": "10 days"
            },
            CollaborationType.JOINT_CONTENT: {
                "planning": "1 week",
                "execution": "2 weeks",
                "total_duration": "3 weeks"
            },
            CollaborationType.GUEST_APPEARANCE: {
                "planning": "1 week",
                "execution": "1 day",
                "post_production": "1 week",
                "total_duration": "2-3 weeks"
            },
            CollaborationType.BRAND_CAMPAIGN: {
                "planning": "2 weeks",
                "execution": "1 month",
                "total_duration": "6-8 weeks"
            }
        }
        
        return timeline_templates.get(collaboration_type, {
            "planning": "1 week",
            "execution": "2 weeks",
            "total_duration": "3 weeks"
        })
    
    def _calculate_revenue_potential(
        self,
        creator_a: CreatorProfile,
        creator_b: CreatorProfile,
        collaboration_type: CollaborationType,
        estimated_reach: int
    ) -> Dict[str, float]:
        """Calculate revenue potential for collaboration."""
        
        # Base rates (would come from creator profiles in production)
        base_rate_a = creator_a.rates.get('collaboration', 1000)
        base_rate_b = creator_b.rates.get('collaboration', 1000)
        
        # Collaboration multipliers
        type_multipliers = {
            CollaborationType.BRAND_CAMPAIGN: 2.0,
            CollaborationType.COURSE_COLLAB: 1.5,
            CollaborationType.TOUR_COLLAB: 3.0,
            CollaborationType.JOINT_CONTENT: 1.2,
            CollaborationType.GUEST_APPEARANCE: 1.1,
            CollaborationType.CROSS_PROMOTION: 0.8
        }
        
        multiplier = type_multipliers.get(collaboration_type, 1.0)
        
        # Calculate potential revenue streams
        direct_revenue = (base_rate_a + base_rate_b) * multiplier
        
        # Sponsorship potential based on reach
        sponsorship_rate = estimated_reach * 0.01  # $0.01 per reach
        sponsorship_potential = sponsorship_rate * multiplier
        
        # Merchandise/product sales potential
        conversion_rate = 0.02  # 2% conversion
        avg_order_value = 25
        product_potential = estimated_reach * conversion_rate * avg_order_value
        
        return {
            "direct_collaboration": direct_revenue,
            "sponsorship_potential": sponsorship_potential,
            "product_sales": product_potential,
            "total_potential": direct_revenue + sponsorship_potential + product_potential
        }
    
    def _generate_content_ideas(
        self,
        creator_a: CreatorProfile,
        creator_b: CreatorProfile,
        collaboration_type: CollaborationType
    ) -> List[str]:
        """Generate specific content ideas for collaboration."""
        
        category_a = creator_a.content_categories[0] if creator_a.content_categories else 'general'
        category_b = creator_b.content_categories[0] if creator_b.content_categories else 'general'
        
        # Content idea templates by collaboration type and category
        idea_templates = {
            (CollaborationType.DUET, 'music'): [
                "Duet performance of trending song",
                "Original song collaboration",
                "Genre-fusion experiment",
                "Acoustic vs electronic version comparison"
            ],
            (CollaborationType.JOINT_CONTENT, 'comedy'): [
                "Comedy skit collaboration",
                "Roast battle or friendly competition",
                "Reaction video to each other's content",
                "Comedy challenge series"
            ],
            (CollaborationType.GUEST_APPEARANCE, 'educational'): [
                "Expert interview on specialized topic",
                "Q&A session with audience questions",
                "Tutorial collaboration combining expertise",
                "Debate on industry trends"
            ],
            (CollaborationType.CHALLENGE, 'fitness'): [
                "30-day fitness challenge",
                "Workout routine exchange",
                "Healthy recipe cook-off",
                "Transformation journey documentation"
            ]
        }
        
        # Get specific ideas for this combination
        key = (collaboration_type, category_a)
        if key in idea_templates:
            return idea_templates[key]
        
        # Fallback to generic ideas
        generic_ideas = {
            CollaborationType.CROSS_PROMOTION: [
                "Mutual shoutouts on Instagram Stories",
                "Feature each other in content captions",
                "Cross-platform promotion campaign",
                "Audience exchange initiative"
            ],
            CollaborationType.JOINT_CONTENT: [
                "Behind-the-scenes collaboration video",
                "Split-screen content comparison",
                "Joint tutorial or educational content",
                "Collaborative live stream"
            ],
            CollaborationType.CHALLENGE: [
                "Create custom challenge for audiences",
                "Participate in trending challenge together",
                "Week-long collaborative challenge",
                "Skills-based competition"
            ]
        }
        
        return generic_ideas.get(collaboration_type, [
            "Collaborative content creation",
            "Cross-promotional campaign",
            "Joint audience engagement",
            "Shared creative project"
        ])
    
    def _generate_next_steps(self, collaboration_type: CollaborationType) -> List[str]:
        """Generate actionable next steps for collaboration."""
        
        common_steps = [
            "Reach out with collaboration proposal",
            "Schedule initial discussion call",
            "Define collaboration scope and expectations",
            "Agree on timeline and deliverables"
        ]
        
        type_specific_steps = {
            CollaborationType.BRAND_CAMPAIGN: [
                "Identify compatible brands for partnership",
                "Create joint media kit",
                "Negotiate collaboration terms and compensation"
            ],
            CollaborationType.JOINT_CONTENT: [
                "Brainstorm content concepts",
                "Plan production logistics",
                "Coordinate posting schedule"
            ],
            CollaborationType.GUEST_APPEARANCE: [
                "Prepare interview questions",
                "Schedule recording session",
                "Plan promotion strategy"
            ]
        }
        
        specific_steps = type_specific_steps.get(collaboration_type, [])
        
        return common_steps + specific_steps


class CollaborationFinder:
    """
    Master collaboration finder that coordinates all collaboration discovery
    and management operations.
    """
    
    def __init__(self):
        """Initialize the collaboration finder."""
        self.matching_engine = InfluencerMatchingEngine()
        self.analytics_service = CreatorAnalyticsService()
        
        logger.info("Collaboration finder initialized successfully")
    
    async def discover_collaboration_opportunities(
        self,
        creator_id: str,
        preferences: Dict[str, Any] = None,
        max_opportunities: int = 20
    ) -> List[CollaborationOpportunity]:
        """
        Discover collaboration opportunities for a creator.
        
        Args:
            creator_id: Target creator identifier
            preferences: Creator's collaboration preferences
            max_opportunities: Maximum opportunities to return
            
        Returns:
            List of collaboration opportunities
        """
        
        try:
            # Get creator profile
            creator_profile = await self._get_creator_profile(creator_id)
            
            # Get potential collaboration partners
            candidates = await self._find_potential_partners(creator_profile, preferences)
            
            # Find collaboration matches
            opportunities = await self.matching_engine.find_collaboration_matches(
                creator_profile, candidates, max_matches=max_opportunities
            )
            
            logger.info(f"Discovered {len(opportunities)} collaboration opportunities for creator {creator_id}")
            return opportunities
            
        except Exception as e:
            logger.error(f"Failed to discover collaboration opportunities: {e}")
            return []
    
    async def _get_creator_profile(self, creator_id: str) -> CreatorProfile:
        """Get comprehensive creator profile for matching."""
        
        # This would fetch real creator data from various sources
        # For now, return a sample profile
        
        return CreatorProfile(
            creator_id=creator_id,
            display_name=f"Creator {creator_id}",
            platforms=['instagram', 'tiktok', 'youtube'],
            primary_platform='instagram',
            content_categories=['lifestyle', 'fashion'],
            audience_size={'instagram': 50000, 'tiktok': 75000, 'youtube': 25000},
            engagement_rates={'instagram': 0.04, 'tiktok': 0.06, 'youtube': 0.03},
            demographics={
                'age_distribution': {'18-24': 0.4, '25-34': 0.35, '35-44': 0.25},
                'gender_distribution': {'female': 0.7, 'male': 0.3},
                'location_distribution': {'US': 0.6, 'UK': 0.2, 'CA': 0.2}
            },
            content_style={
                'tone': 'casual',
                'format_preferences': ['short_video', 'image'],
                'posting_frequency': 5,
                'content_length': 'short'
            },
            brand_partnerships=['nike', 'sephora'],
            collaboration_history=[],
            availability={'weekdays': True, 'weekends': True},
            rates={'collaboration': 2000, 'sponsored_post': 1500},
            location={'country': 'US', 'region': 'CA'},
            languages=['en'],
            verified_status={'instagram': True, 'tiktok': False, 'youtube': False}
        )
    
    async def _find_potential_partners(
        self, creator_profile: CreatorProfile, preferences: Dict[str, Any] = None
    ) -> List[CreatorProfile]:
        """Find potential collaboration partners."""
        
        # This would query a database of creators
        # For now, return sample candidates
        
        candidates = []
        
        for i in range(50):  # Generate 50 sample candidates
            candidate = CreatorProfile(
                creator_id=f"creator_{i}",
                display_name=f"Creator {i}",
                platforms=['instagram', 'tiktok'],
                primary_platform='instagram',
                content_categories=['beauty', 'lifestyle'],
                audience_size={'instagram': 30000 + i * 1000, 'tiktok': 40000 + i * 1500},
                engagement_rates={'instagram': 0.03 + i * 0.001, 'tiktok': 0.05 + i * 0.001},
                demographics={
                    'age_distribution': {'18-24': 0.3 + i * 0.01, '25-34': 0.4, '35-44': 0.3 - i * 0.01},
                    'gender_distribution': {'female': 0.8, 'male': 0.2},
                    'location_distribution': {'US': 0.7, 'UK': 0.3}
                },
                content_style={
                    'tone': 'professional' if i % 2 == 0 else 'casual',
                    'format_preferences': ['image', 'short_video'],
                    'posting_frequency': 3 + i % 5,
                    'content_length': 'medium'
                },
                brand_partnerships=['target', 'ulta'],
                collaboration_history=[],
                availability={'weekdays': True, 'weekends': i % 3 == 0},
                rates={'collaboration': 1000 + i * 100, 'sponsored_post': 800 + i * 80},
                location={'country': 'US', 'region': 'NY' if i % 2 == 0 else 'CA'},
                languages=['en'],
                verified_status={'instagram': i % 5 == 0, 'tiktok': False, 'youtube': False}
            )
            candidates.append(candidate)
        
        return candidates
