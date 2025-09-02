"""Collaboration Quality Analyzer - Enterprise Creator Matching System

Ultra-advanced collaboration quality analysis and creator matching system
for the IA-Influencer platform with AI-powered compatibility assessment,
collaboration scoring, and strategic partnership recommendations.

Business Logic:
Creator profile → Collaboration analysis → Compatibility scoring →
Matching algorithms → Partnership recommendations → Quality metrics

Created by: Fahed Mlaiel (mlaiel@live.de)
(c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ STRICT COPYRIGHT WARNING ⚠️
This software is proprietary and confidential. 
Unauthorized use, modification, or distribution by any individual or entity 
without explicit written permission from Fahed Mlaiel is strictly prohibited.
Violators will face immediate legal action under German and international law.
Contact: mlaiel@live.de for licensing inquiries.
"""

import asyncio
import logging
import time
from datetime import datetime, timezone, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
import json
import statistics
from decimal import Decimal
import numpy as np

logger = logging.getLogger(__name__)


class CollaborationType(Enum):
    """
Types of creator collaborations"""

    MUSIC_COLLABORATION = "music_collaboration"
    VIDEO_COLLABORATION = "video_collaboration"
    CROSS_PROMOTION = "cross_promotion"
    JOINT_CONTENT = "joint_content"
    BRAND_PARTNERSHIP = "brand_partnership"
    LIVE_STREAM = "live_stream"
    PLAYLIST_FEATURE = "playlist_feature"
    REMIX_PERMISSION = "remix_permission"
    CONTENT_LICENSING = "content_licensing"
    TOUR_COLLABORATION = "tour_collaboration"


class CreatorCategory(Enum):
    """Creator categories for matching"""

    MUSICIAN = "musician"
    VIDEO_CREATOR = "video_creator"
    PHOTOGRAPHER = "photographer"
    BLOGGER = "blogger"
    PODCASTER = "podcaster"
    INFLUENCER = "influencer"
    ARTIST = "artist"
    COMEDIAN = "comedian"
    EDUCATOR = "educator"
    GAMER = "gamer"


class CompatibilityLevel(Enum):
    """Collaboration compatibility levels"""

    EXCELLENT = "excellent"  # 90-100
    GOOD = "good"           # 80-89
    MODERATE = "moderate"   # 60-79
    LOW = "low"             # 40-59
    INCOMPATIBLE = "incompatible"  # 0-39


class CollaborationStage(Enum):
    """Stages of collaboration"""

    DISCOVERY = "discovery"
    INITIAL_CONTACT = "initial_contact"
    NEGOTIATION = "negotiation"
    PLANNING = "planning"
    EXECUTION = "execution"
    PROMOTION = "promotion"
    COMPLETION = "completion"
    FOLLOW_UP = "follow_up"


@dataclass
class CreatorProfile:
    """Comprehensive creator profile for matching"""
    creator_id: str
    name: str
    category: CreatorCategory
    genres: List[str] = field(default_factory=list)
    platforms: List[str] = field(default_factory=list)
    
    # Audience metrics
    total_followers: int = 0
    engagement_rate: float = 0.0
    audience_demographics: Dict[str, Any] = field(default_factory=dict)
    audience_overlap_threshold: float = 0.3
    
    # Content metrics
    content_quality_score: float = 0.0
    posting_frequency: str = "unknown"
    content_themes: List[str] = field(default_factory=list)
    
    # Collaboration history
    past_collaborations: List[Dict[str, Any]] = field(default_factory=list)
    collaboration_success_rate: float = 0.0
    preferred_collaboration_types: List[CollaborationType] = field(default_factory=list)
    
    # Professional metrics
    professionalism_score: float = 0.0
    response_time_hours: float = 24.0
    contract_completion_rate: float = 100.0
    
    # Availability and preferences
    availability_calendar: Dict[str, bool] = field(default_factory=dict)
    collaboration_budget_range: Tuple[Decimal, Decimal] = (Decimal('0'), Decimal('1000'))
    geographical_preferences: List[str] = field(default_factory=list)
    language_preferences: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        try:
            logger.info(f"Executing to_dict")
            
            # Implementation for to_dict
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"to_dict completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"to_dict failed: {e}")
            raise
            'creator_id': self.creator_id,
            'name': self.name,
            'category': self.category.value,
            'genres': self.genres,
            'platforms': self.platforms,
            'total_followers': self.total_followers,
            'engagement_rate': self.engagement_rate,
            'audience_demographics': self.audience_demographics,
            'content_quality_score': self.content_quality_score,
            'posting_frequency': self.posting_frequency,
            'content_themes': self.content_themes,
            'past_collaborations': self.past_collaborations,
            'collaboration_success_rate': self.collaboration_success_rate,
            'preferred_collaboration_types': [ct.value for ct in self.preferred_collaboration_types],
            'professionalism_score': self.professionalism_score,
            'response_time_hours': self.response_time_hours,
            'contract_completion_rate': self.contract_completion_rate,
            'collaboration_budget_range': [float(self.collaboration_budget_range[0]), float(self.collaboration_budget_range[1])],
            'geographical_preferences': self.geographical_preferences,
            'language_preferences': self.language_preferences
        }


@dataclass
class CompatibilityFactors:
    """Factors contributing to collaboration compatibility"""
    audience_alignment_score: float = 0.0
    content_synergy_score: float = 0.0
    brand_compatibility_score: float = 0.0
    schedule_compatibility_score: float = 0.0
    communication_compatibility_score: float = 0.0
    budget_compatibility_score: float = 0.0
    geographic_compatibility_score: float = 0.0
    experience_level_compatibility: float = 0.0
    
    # Detailed breakdowns
    audience_overlap_percentage: float = 0.0
    content_theme_overlap: List[str] = field(default_factory=list)
    platform_overlap: List[str] = field(default_factory=list)
    genre_alignment: List[str] = field(default_factory=list)
    
    def calculate_overall_compatibility(self) -> float:
        """
Calculate weighted overall compatibility score"""
        weights = {
            'audience': 0.25,
            'content': 0.20,
            'brand': 0.15,
            'schedule': 0.10,
            'communication': 0.10,
            'budget': 0.10,
            'geographic': 0.05,
            'experience': 0.05
        }
        
        score = (
            self.audience_alignment_score * weights['audience'] +
            self.content_synergy_score * weights['content'] +
            self.brand_compatibility_score * weights['brand'] +
            self.schedule_compatibility_score * weights['schedule'] +
            self.communication_compatibility_score * weights['communication'] +
            self.budget_compatibility_score * weights['budget'] +
            self.geographic_compatibility_score * weights['geographic'] +
            self.experience_level_compatibility * weights['experience']
        )
        
        return round(score, 2)
    
    def to_dict(self) -> Dict[str, Any]:
        try:
            logger.info(f"Executing to_dict")
            
            # Implementation for to_dict
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"to_dict completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"to_dict failed: {e}")
            raise
            self.content_synergy_score * weights['content'] +
            self.brand_compatibility_score * weights['brand'] +
            self.schedule_compatibility_score * weights['schedule'] +
            self.communication_compatibility_score * weights['communication'] +
            self.budget_compatibility_score * weights['budget'] +
            self.geographic_compatibility_score * weights['geographic'] +
            self.experience_level_compatibility * weights['experience']
        )
        
        return round(score, 2)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'audience_alignment_score': self.audience_alignment_score,
            'content_synergy_score': self.content_synergy_score,
            'brand_compatibility_score': self.brand_compatibility_score,
            'schedule_compatibility_score': self.schedule_compatibility_score,
            'communication_compatibility_score': self.communication_compatibility_score,
        try:
            logger.info(f"Executing to_dict")
            
            # Implementation for to_dict
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"to_dict completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"to_dict failed: {e}")
            raise
            'geographic_compatibility_score': self.geographic_compatibility_score,
            'experience_level_compatibility': self.experience_level_compatibility,
            'overall_compatibility': self.calculate_overall_compatibility(),
            'audience_overlap_percentage': self.audience_overlap_percentage,
            'content_theme_overlap': self.content_theme_overlap,
            'platform_overlap': self.platform_overlap,
            'genre_alignment': self.genre_alignment
        }


@dataclass
class CollaborationOpportunity:
    """
Specific collaboration opportunity recommendation"""
    opportunity_id: str
    collaboration_type: CollaborationType
    partner_creator: CreatorProfile
    compatibility_factors: CompatibilityFactors
    
    # Opportunity details
    estimated_reach: int = 0
    estimated_engagement: int = 0
    revenue_potential: Decimal = Decimal('0.00')
    effort_required: str = "medium"  # low, medium, high
    timeline_estimate: str = "2-4 weeks"
    
    # Success prediction
    success_probability: float = 0.0
    risk_factors: List[str] = field(default_factory=list)
    success_factors: List[str] = field(default_factory=list)
    
    # Actionable recommendations
    collaboration_proposal: str = ""
    suggested_approach: str = ""
    key_talking_points: List[str] = field(default_factory=list)
    content_ideas: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        try:
            logger.info(f"Executing to_dict")
            
            # Implementation for to_dict
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"to_dict completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"to_dict failed: {e}")
            raise
        return {
            'opportunity_id': self.opportunity_id,
            'collaboration_type': self.collaboration_type.value,
            'partner_creator': self.partner_creator.to_dict(),
            'compatibility_factors': self.compatibility_factors.to_dict(),
            'estimated_reach': self.estimated_reach,
            'estimated_engagement': self.estimated_engagement,
            'revenue_potential': float(self.revenue_potential),
            'effort_required': self.effort_required,
            'timeline_estimate': self.timeline_estimate,
            'success_probability': self.success_probability,
            'risk_factors': self.risk_factors,
            'success_factors': self.success_factors,
            'collaboration_proposal': self.collaboration_proposal,
            'suggested_approach': self.suggested_approach,
            'key_talking_points': self.key_talking_points,
            'content_ideas': self.content_ideas
        }


@dataclass
class CollaborationQualityAnalysis:
    """Comprehensive collaboration quality analysis result"""
    creator_id: str
    analysis_timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Creator collaboration profile
    creator_profile: CreatorProfile = field(default_factory=lambda: CreatorProfile("", "", CreatorCategory.INFLUENCER))
    collaboration_readiness_score: float = 0.0
    
    # Collaboration opportunities
    top_opportunities: List[CollaborationOpportunity] = field(default_factory=list)
    total_opportunities_found: int = 0
    
    # Quality metrics
    average_compatibility_score: float = 0.0
    high_quality_matches: int = 0
    potential_revenue_increase: Decimal = Decimal('0.00')
    estimated_audience_growth: int = 0
    
    # Strategic insights
    collaboration_strengths: List[str] = field(default_factory=list)
    improvement_areas: List[str] = field(default_factory=list)
    strategic_recommendations: List[str] = field(default_factory=list)
    
    # Market analysis
    market_position: str = "unknown"
    competitive_advantages: List[str] = field(default_factory=list)
    collaboration_trends: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'creator_id': self.creator_id,
            'analysis_timestamp': self.analysis_timestamp.isoformat(),
            'creator_profile': self.creator_profile.to_dict(),
            'collaboration_readiness_score': self.collaboration_readiness_score,
            'top_opportunities': [opp.to_dict() for opp in self.top_opportunities],
            'total_opportunities_found': self.total_opportunities_found,
            'average_compatibility_score': self.average_compatibility_score,
            'high_quality_matches': self.high_quality_matches,
            'potential_revenue_increase': float(self.potential_revenue_increase),
            'estimated_audience_growth': self.estimated_audience_growth,
            'collaboration_strengths': self.collaboration_strengths,
            'improvement_areas': self.improvement_areas,
            'strategic_recommendations': self.strategic_recommendations,
            'market_position': self.market_position,
            'competitive_advantages': self.competitive_advantages,
            'collaboration_trends': self.collaboration_trends
        }


class CollaborationQualityAnalyzer:
    """
    Ultra-advanced collaboration quality analyzer and creator matching system
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Collaboration type weights for different creator categories
        self.collaboration_weights = {
            CreatorCategory.MUSICIAN: {
                CollaborationType.MUSIC_COLLABORATION: 0.30,
                CollaborationType.CROSS_PROMOTION: 0.20,
                CollaborationType.LIVE_STREAM: 0.15,
                CollaborationType.PLAYLIST_FEATURE: 0.15,
                CollaborationType.REMIX_PERMISSION: 0.10,
                CollaborationType.TOUR_COLLABORATION: 0.10
            },
            CreatorCategory.VIDEO_CREATOR: {
                CollaborationType.VIDEO_COLLABORATION: 0.30,
                CollaborationType.CROSS_PROMOTION: 0.25,
                CollaborationType.JOINT_CONTENT: 0.20,
                CollaborationType.BRAND_PARTNERSHIP: 0.15,
                CollaborationType.LIVE_STREAM: 0.10
            },
            CreatorCategory.INFLUENCER: {
                CollaborationType.CROSS_PROMOTION: 0.30,
                CollaborationType.BRAND_PARTNERSHIP: 0.25,
                CollaborationType.JOINT_CONTENT: 0.20,
                CollaborationType.LIVE_STREAM: 0.15,
                CollaborationType.VIDEO_COLLABORATION: 0.10
            }
        }
        
        # Success probability factors
        self.success_factors = {
            'high_engagement_both': 15,
            'similar_audience_size': 10,
            'complementary_skills': 20,
            'past_collaboration_success': 15,
            'brand_alignment': 10,
            'schedule_alignment': 10,
            'geographic_proximity': 5,
            'language_compatibility': 5,
            'budget_compatibility': 10
        }
    
    async def analyze_collaboration_quality(
        self,
        creator_data: Dict[str, Any],
        potential_partners: List[Dict[str, Any]],
        collaboration_preferences: Optional[Dict[str, Any]] = None,
        market_data: Optional[Dict[str, Any]] = None
    ) -> CollaborationQualityAnalysis:
        """
        Perform comprehensive collaboration quality analysis
        
        Args:
            creator_data: Primary creator data and metrics
            potential_partners: List of potential collaboration partners
            collaboration_preferences: Creator's collaboration preferences
            market_data: Market trends and industry data
            
        Returns:
            CollaborationQualityAnalysis: Comprehensive analysis result
        """
        start_time = time.time()
        creator_id = creator_data.get('creator_id', 'unknown')
        
        try:
            self.logger.info(f"Starting collaboration quality analysis for creator {creator_id}")
            
            # Initialize analysis result
            analysis = CollaborationQualityAnalysis(creator_id=creator_id)
            
            # Build creator profile
            analysis.creator_profile = await self._build_creator_profile(creator_data, collaboration_preferences)
            
            # Calculate collaboration readiness score
            analysis.collaboration_readiness_score = await self._calculate_collaboration_readiness(
                analysis.creator_profile
            )
            
            # Analyze potential partners and find opportunities
            opportunities = await self._analyze_collaboration_opportunities(
                analysis.creator_profile, potential_partners
            )
            
            # Sort and filter top opportunities
            opportunities.sort(
                key=lambda x: x.compatibility_factors.calculate_overall_compatibility(), 
                reverse=True
            )
            
            analysis.top_opportunities = opportunities[:10]  # Top 10 opportunities
            analysis.total_opportunities_found = len(opportunities)
            
            # Calculate quality metrics
            await self._calculate_quality_metrics(analysis, opportunities)
            
            # Generate strategic insights
            await self._generate_strategic_insights(analysis, market_data)
            
            # Market positioning analysis
            await self._analyze_market_position(analysis, market_data)
            
            processing_time = (time.time() - start_time) * 1000
            self.logger.info(
                f"Collaboration quality analysis completed for creator {creator_id} "
                f"in {processing_time:.2f}ms with {len(analysis.top_opportunities)} top opportunities"
            )
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error analyzing collaboration quality for creator {creator_id}: {str(e)}")
            raise
    
    async def _build_creator_profile(
        self,
        creator_data: Dict[str, Any],
        collaboration_preferences: Optional[Dict[str, Any]]
    ) -> CreatorProfile:
        """Build comprehensive creator profile from data"""
        
        profile = CreatorProfile(
            creator_id=creator_data.get('creator_id', ''),
            name=creator_data.get('name', ''),
            category=CreatorCategory(creator_data.get('category', 'influencer'))
        )
        
        # Basic metrics
        profile.genres = creator_data.get('genres', [])
        profile.platforms = creator_data.get('platforms', [])
        profile.total_followers = creator_data.get('total_followers', 0)
        profile.engagement_rate = creator_data.get('engagement_rate', 0.0)
        profile.content_quality_score = creator_data.get('content_quality_score', 0.0)
        profile.posting_frequency = creator_data.get('posting_frequency', 'unknown')
        profile.content_themes = creator_data.get('content_themes', [])
        
        # Audience demographics
        profile.audience_demographics = creator_data.get('audience_demographics', {})
        
        # Collaboration history
        profile.past_collaborations = creator_data.get('past_collaborations', [])
        profile.collaboration_success_rate = await self._calculate_collaboration_success_rate(
            profile.past_collaborations
        )
        
        # Professional metrics
        profile.professionalism_score = creator_data.get('professionalism_score', 75.0)
        profile.response_time_hours = creator_data.get('response_time_hours', 24.0)
        profile.contract_completion_rate = creator_data.get('contract_completion_rate', 100.0)
        
        # Preferences from collaboration_preferences
        if collaboration_preferences:
            profile.preferred_collaboration_types = [
                CollaborationType(ct) for ct in collaboration_preferences.get('preferred_types', [])
            ]
            
            budget_range = collaboration_preferences.get('budget_range', [0, 1000])
            profile.collaboration_budget_range = (Decimal(str(budget_range[0])), Decimal(str(budget_range[1])))
            
            profile.geographical_preferences = collaboration_preferences.get('geographical_preferences', [])
            profile.language_preferences = collaboration_preferences.get('language_preferences', ['en'])
        
        return profile
    
    async def _calculate_collaboration_success_rate(
        self,
        past_collaborations: List[Dict[str, Any]]
    ) -> float:
        """
Calculate collaboration success rate from history"""
        if not past_collaborations:
            return 50.0  # Default neutral score
        
        successful_collaborations = sum(
            1 for collab in past_collaborations 
            if collab.get('outcome', 'unknown') in ['successful', 'excellent']
        )
        
        return (successful_collaborations / len(past_collaborations)) * 100
    
    async def _calculate_collaboration_readiness(
        self,
        creator_profile: CreatorProfile
    ) -> float:
        """
Calculate overall collaboration readiness score"""
        readiness_score = 0.0
        
        # Content quality factor (25%)
        readiness_score += creator_profile.content_quality_score * 0.25
        
        # Audience engagement factor (20%)
        engagement_score = min(100, creator_profile.engagement_rate * 2000)  # Scale engagement rate
        readiness_score += engagement_score * 0.20
        
        # Professionalism factor (20%)
        readiness_score += creator_profile.professionalism_score * 0.20
        
        # Collaboration experience factor (15%)
        experience_score = min(100, len(creator_profile.past_collaborations) * 10)
        readiness_score += experience_score * 0.15
        
        # Success rate factor (10%)
        readiness_score += creator_profile.collaboration_success_rate * 0.10
        
        # Responsiveness factor (5%)
        responsiveness_score = max(0, 100 - (creator_profile.response_time_hours / 24) * 50)
        readiness_score += responsiveness_score * 0.05
        
        # Contract reliability factor (5%)
        readiness_score += creator_profile.contract_completion_rate * 0.05
        
        return round(readiness_score, 2)
    
    async def _analyze_collaboration_opportunities(
        self,
        creator_profile: CreatorProfile,
        potential_partners: List[Dict[str, Any]]
    ) -> List[CollaborationOpportunity]:
        """
Analyze and generate collaboration opportunities"""
        opportunities = []
        
        for partner_data in potential_partners:
            try:
                # Build partner profile
                partner_profile = await self._build_creator_profile(partner_data, None)
                
                # Calculate compatibility factors
                compatibility = await self._calculate_compatibility_factors(
                    creator_profile, partner_profile
                )
                
                # Skip if compatibility is too low
                if compatibility.calculate_overall_compatibility() < 40:
                    continue
                
                # Determine best collaboration types
                best_collaboration_types = await self._suggest_collaboration_types(
                    creator_profile, partner_profile, compatibility
                )
                
                # Create opportunities for each viable collaboration type
                for collab_type in best_collaboration_types[:3]:  # Top 3 types
                    opportunity = await self._create_collaboration_opportunity(
                        collab_type, creator_profile, partner_profile, compatibility
                    )
                    opportunities.append(opportunity)
                
            except Exception as e:
                self.logger.warning(f"Error analyzing partner {partner_data.get('creator_id', 'unknown')}: {str(e)}")
                continue
        
        return opportunities
    
    async def _calculate_compatibility_factors(
        self,
        creator_profile: CreatorProfile,
        partner_profile: CreatorProfile
    ) -> CompatibilityFactors:
        """Calculate detailed compatibility factors between creators"""
        factors = CompatibilityFactors()
        
        # Audience alignment
        factors.audience_alignment_score = await self._calculate_audience_alignment(
            creator_profile, partner_profile
        )
        
        # Content synergy
        factors.content_synergy_score = await self._calculate_content_synergy(
            creator_profile, partner_profile
        )
        
        # Brand compatibility
        factors.brand_compatibility_score = await self._calculate_brand_compatibility(
            creator_profile, partner_profile
        )
        
        # Schedule compatibility (simplified)
        factors.schedule_compatibility_score = 85.0  # Placeholder
        
        # Communication compatibility
        factors.communication_compatibility_score = await self._calculate_communication_compatibility(
            creator_profile, partner_profile
        )
        
        # Budget compatibility
        factors.budget_compatibility_score = await self._calculate_budget_compatibility(
            creator_profile, partner_profile
        )
        
        # Geographic compatibility
        factors.geographic_compatibility_score = await self._calculate_geographic_compatibility(
            creator_profile, partner_profile
        )
        
        # Experience level compatibility
        factors.experience_level_compatibility = await self._calculate_experience_compatibility(
            creator_profile, partner_profile
        )
        
        # Calculate detailed breakdowns
        factors.audience_overlap_percentage = await self._calculate_audience_overlap(
            creator_profile, partner_profile
        )
        factors.content_theme_overlap = list(set(creator_profile.content_themes) & set(partner_profile.content_themes))
        factors.platform_overlap = list(set(creator_profile.platforms) & set(partner_profile.platforms))
        factors.genre_alignment = list(set(creator_profile.genres) & set(partner_profile.genres))
        
        return factors
    
    async def _calculate_audience_alignment(
        self,
        creator_profile: CreatorProfile,
        partner_profile: CreatorProfile
    ) -> float:
        """
Calculate audience alignment score"""
        score = 0.0
        
        # Audience size compatibility
        creator_followers = creator_profile.total_followers
        partner_followers = partner_profile.total_followers
        
        if creator_followers > 0 and partner_followers > 0:
            # Similar audience sizes are better for collaboration
            size_ratio = min(creator_followers, partner_followers) / max(creator_followers, partner_followers)
            score += size_ratio * 40
        
        # Engagement rate alignment
        creator_engagement = creator_profile.engagement_rate
        partner_engagement = partner_profile.engagement_rate
        
        if creator_engagement > 0 and partner_engagement > 0:
            engagement_similarity = 1 - abs(creator_engagement - partner_engagement) / max(creator_engagement, partner_engagement)
            score += engagement_similarity * 30
        
        # Audience demographics overlap (simplified)
        if creator_profile.audience_demographics and partner_profile.audience_demographics:
            # Age group overlap
            creator_ages = set(creator_profile.audience_demographics.get('age_groups', []))
            partner_ages = set(partner_profile.audience_demographics.get('age_groups', []))
            age_overlap = len(creator_ages & partner_ages) / max(1, len(creator_ages | partner_ages))
            score += age_overlap * 20
            
            # Gender distribution similarity
            creator_gender = creator_profile.audience_demographics.get('gender_distribution', {})
            partner_gender = partner_profile.audience_demographics.get('gender_distribution', {})
            
            if creator_gender and partner_gender:
                gender_similarity = 1 - abs(
                    creator_gender.get('female', 0.5) - partner_gender.get('female', 0.5)
                )
                score += gender_similarity * 10
        
        return min(100, score)
    
    async def _calculate_content_synergy(
        self,
        creator_profile: CreatorProfile,
        partner_profile: CreatorProfile
    ) -> float:
        """
Calculate content synergy score"""
        score = 0.0
        
        # Content theme overlap
        creator_themes = set(creator_profile.content_themes)
        partner_themes = set(partner_profile.content_themes)
        
        if creator_themes and partner_themes:
            theme_overlap = len(creator_themes & partner_themes) / len(creator_themes | partner_themes)
            score += theme_overlap * 40
        
        # Genre alignment
        creator_genres = set(creator_profile.genres)
        partner_genres = set(partner_profile.genres)
        
        if creator_genres and partner_genres:
            genre_overlap = len(creator_genres & partner_genres) / len(creator_genres | partner_genres)
            score += genre_overlap * 30
        
        # Platform overlap
        creator_platforms = set(creator_profile.platforms)
        partner_platforms = set(partner_profile.platforms)
        
        if creator_platforms and partner_platforms:
            platform_overlap = len(creator_platforms & partner_platforms) / len(creator_platforms | partner_platforms)
            score += platform_overlap * 20
        
        # Content quality alignment
        quality_difference = abs(creator_profile.content_quality_score - partner_profile.content_quality_score)
        quality_score = max(0, 100 - quality_difference)
        score += quality_score * 0.1
        
        return min(100, score)
    
    async def _calculate_brand_compatibility(
        self,
        creator_profile: CreatorProfile,
        partner_profile: CreatorProfile
    ) -> float:
        """
Calculate brand compatibility score"""
        score = 75.0  # Base compatibility score
        
        # Creator category compatibility
        category_compatibility = {
            (CreatorCategory.MUSICIAN, CreatorCategory.MUSICIAN): 90,
            (CreatorCategory.MUSICIAN, CreatorCategory.VIDEO_CREATOR): 85,
            (CreatorCategory.MUSICIAN, CreatorCategory.INFLUENCER): 80,
            (CreatorCategory.VIDEO_CREATOR, CreatorCategory.VIDEO_CREATOR): 95,
            (CreatorCategory.VIDEO_CREATOR, CreatorCategory.INFLUENCER): 90,
            (CreatorCategory.INFLUENCER, CreatorCategory.INFLUENCER): 85,
        }
        
        category_pair = (creator_profile.category, partner_profile.category)
        reverse_pair = (partner_profile.category, creator_profile.category)
        
        if category_pair in category_compatibility:
            score = category_compatibility[category_pair]
        elif reverse_pair in category_compatibility:
            score = category_compatibility[reverse_pair]
        
        # Professionalism alignment
        professionalism_difference = abs(
            creator_profile.professionalism_score - partner_profile.professionalism_score
        )
        
        if professionalism_difference < 10:
            score += 10
        elif professionalism_difference < 20:
            score += 5
        
        return min(100, score)
    
    async def _calculate_communication_compatibility(
        self,
        creator_profile: CreatorProfile,
        partner_profile: CreatorProfile
    ) -> float:
        """
Calculate communication compatibility score"""
        score = 50.0  # Base score
        
        # Language compatibility
        creator_languages = set(creator_profile.language_preferences)
        partner_languages = set(partner_profile.language_preferences)
        
        if creator_languages & partner_languages:
            score += 30
        
        # Response time compatibility
        avg_response_time = (creator_profile.response_time_hours + partner_profile.response_time_hours) / 2
        
        if avg_response_time <= 12:
            score += 20
        elif avg_response_time <= 24:
            score += 15
        elif avg_response_time <= 48:
            score += 10
        
        return min(100, score)
    
    async def _calculate_budget_compatibility(
        self,
        creator_profile: CreatorProfile,
        partner_profile: CreatorProfile
    ) -> float:
        """
Calculate budget compatibility score"""
        creator_min, creator_max = creator_profile.collaboration_budget_range
        partner_min, partner_max = partner_profile.collaboration_budget_range
        
        # Check for budget overlap
        overlap_min = max(creator_min, partner_min)
        overlap_max = min(creator_max, partner_max)
        
        if overlap_min <= overlap_max:
            # There's budget overlap
            overlap_range = overlap_max - overlap_min
            total_range = max(creator_max, partner_max) - min(creator_min, partner_min)
            
            if total_range > 0:
                overlap_percentage = float(overlap_range / total_range)
                return overlap_percentage * 100
            else:
                return 100.0  # Perfect match
        else:
            # No budget overlap
            gap = float(overlap_min - overlap_max)
            penalty = min(100, gap / 1000 * 50)  # Penalty based on gap size
            return max(0, 50 - penalty)
    
    async def _calculate_geographic_compatibility(
        self,
        creator_profile: CreatorProfile,
        partner_profile: CreatorProfile
    ) -> float:
        """
Calculate geographic compatibility score"""
        creator_geo = set(creator_profile.geographical_preferences)
        partner_geo = set(partner_profile.geographical_preferences)
        
        # If no preferences specified, assume compatible
        if not creator_geo or not partner_geo:
            return 75.0
        
        # Check for geographic overlap
        if creator_geo & partner_geo:
            overlap_percentage = len(creator_geo & partner_geo) / len(creator_geo | partner_geo)
            return overlap_percentage * 100
        else:
            return 25.0  # Low compatibility but not impossible
    
    async def _calculate_experience_compatibility(
        self,
        creator_profile: CreatorProfile,
        partner_profile: CreatorProfile
    ) -> float:
        """
Calculate experience level compatibility"""
        creator_experience = len(creator_profile.past_collaborations)
        partner_experience = len(partner_profile.past_collaborations)
        
        # Similar experience levels work better together
        if creator_experience == 0 and partner_experience == 0:
            return 80.0  # Both new to collaboration
        
        if creator_experience > 0 and partner_experience > 0:
            experience_ratio = min(creator_experience, partner_experience) / max(creator_experience, partner_experience)
            return experience_ratio * 100
        
        # One experienced, one new - can work but requires mentoring
        return 60.0
    
    async def _calculate_audience_overlap(
        self,
        creator_profile: CreatorProfile,
        partner_profile: CreatorProfile
    ) -> float:
        """
Calculate estimated audience overlap percentage"""
        # This would typically use actual audience data analysis
        # For now, use demographic and content similarity as proxy
        
        demographic_similarity = 0.0
        content_similarity = 0.0
        
        # Demographic similarity
        if creator_profile.audience_demographics and partner_profile.audience_demographics:
            creator_ages = set(creator_profile.audience_demographics.get('age_groups', []))
            partner_ages = set(partner_profile.audience_demographics.get('age_groups', []))
            
            if creator_ages and partner_ages:
                age_overlap = len(creator_ages & partner_ages) / len(creator_ages | partner_ages)
                demographic_similarity = age_overlap
        
        # Content similarity
        creator_themes = set(creator_profile.content_themes)
        partner_themes = set(partner_profile.content_themes)
        
        if creator_themes and partner_themes:
            theme_overlap = len(creator_themes & partner_themes) / len(creator_themes | partner_themes)
            content_similarity = theme_overlap
        
        # Estimate overlap based on similarities
        estimated_overlap = (demographic_similarity * 0.6 + content_similarity * 0.4) * 100
        
        # Apply platform-specific modifiers
        creator_platforms = set(creator_profile.platforms)
        partner_platforms = set(partner_profile.platforms)
        
        if creator_platforms & partner_platforms:
            platform_overlap_ratio = len(creator_platforms & partner_platforms) / len(creator_platforms | partner_platforms)
            estimated_overlap *= (0.5 + platform_overlap_ratio * 0.5)
        
        return min(80, estimated_overlap)  # Cap at 80% as 100% overlap is rare
    
    async def _suggest_collaboration_types(
        self,
        creator_profile: CreatorProfile,
        partner_profile: CreatorProfile,
        compatibility: CompatibilityFactors
    ) -> List[CollaborationType]:
        """
Suggest best collaboration types for the creator pair"""
        
        suggestions = []
        compatibility_score = compatibility.calculate_overall_compatibility()
        
        # Get weights for creator categories
        creator_weights = self.collaboration_weights.get(creator_profile.category, {})
        partner_weights = self.collaboration_weights.get(partner_profile.category, {})
        
        # Calculate scores for each collaboration type
        type_scores = {}
        
        for collab_type in CollaborationType:
            score = 0.0
            
            # Base compatibility
            score += compatibility_score * 0.5
            
            # Creator category preferences
            creator_weight = creator_weights.get(collab_type, 0.1)
            partner_weight = partner_weights.get(collab_type, 0.1)
            
            score += (creator_weight + partner_weight) * 50
            
            # Content synergy bonus
            if compatibility.content_synergy_score > 70:
                if collab_type in [CollaborationType.MUSIC_COLLABORATION, CollaborationType.VIDEO_COLLABORATION, CollaborationType.JOINT_CONTENT]:
                    score += 20
            
            # Platform overlap bonus
            if len(compatibility.platform_overlap) > 0:
                if collab_type in [CollaborationType.CROSS_PROMOTION, CollaborationType.LIVE_STREAM]:
                    score += 15
            
            # Budget compatibility requirement
            if compatibility.budget_compatibility_score < 50:
                if collab_type in [CollaborationType.BRAND_PARTNERSHIP, CollaborationType.TOUR_COLLABORATION]:
                    score -= 30
            
            type_scores[collab_type] = score
        
        # Sort by score and return top types
        sorted_types = sorted(type_scores.items(), key=lambda x: x[1], reverse=True)
        
        # Filter types that score above threshold
        threshold = 50.0
        suggestions = [collab_type for collab_type, score in sorted_types if score >= threshold]
        
        return suggestions[:5]  # Return top 5 suggestions
    
    async def _create_collaboration_opportunity(
        self,
        collaboration_type: CollaborationType,
        creator_profile: CreatorProfile,
        partner_profile: CreatorProfile,
        compatibility: CompatibilityFactors
    ) -> CollaborationOpportunity:
        """
Create detailed collaboration opportunity"""
        
        opportunity = CollaborationOpportunity(
            opportunity_id=f"{collaboration_type.value}_{creator_profile.creator_id}_{partner_profile.creator_id}_{int(time.time())}",
            collaboration_type=collaboration_type,
            partner_creator=partner_profile,
            compatibility_factors=compatibility
        )
        
        # Calculate estimated metrics
        opportunity.estimated_reach = int(creator_profile.total_followers + partner_profile.total_followers * 0.7)
        opportunity.estimated_engagement = int(opportunity.estimated_reach * max(creator_profile.engagement_rate, partner_profile.engagement_rate))
        
        # Revenue potential estimation
        base_revenue = Decimal('100.00')
        follower_multiplier = Decimal(str(opportunity.estimated_reach / 10000))
        engagement_multiplier = Decimal(str(max(creator_profile.engagement_rate, partner_profile.engagement_rate) * 100))
        compatibility_multiplier = Decimal(str(compatibility.calculate_overall_compatibility() / 100))
        
        opportunity.revenue_potential = base_revenue * follower_multiplier * engagement_multiplier * compatibility_multiplier
        
        # Effort and timeline estimation
        effort_map = {
            CollaborationType.CROSS_PROMOTION: "low",
            CollaborationType.LIVE_STREAM: "low",
            CollaborationType.PLAYLIST_FEATURE: "low",
            CollaborationType.VIDEO_COLLABORATION: "medium",
            CollaborationType.MUSIC_COLLABORATION: "high",
            CollaborationType.TOUR_COLLABORATION: "high",
            CollaborationType.BRAND_PARTNERSHIP: "medium"
        }
        
        timeline_map = {
            CollaborationType.CROSS_PROMOTION: "1-2 weeks",
            CollaborationType.LIVE_STREAM: "2-3 weeks",
            CollaborationType.PLAYLIST_FEATURE: "1 week",
            CollaborationType.VIDEO_COLLABORATION: "3-6 weeks",
            CollaborationType.MUSIC_COLLABORATION: "6-12 weeks",
            CollaborationType.TOUR_COLLABORATION: "3-6 months",
            CollaborationType.BRAND_PARTNERSHIP: "4-8 weeks"
        }
        
        opportunity.effort_required = effort_map.get(collaboration_type, "medium")
        opportunity.timeline_estimate = timeline_map.get(collaboration_type, "2-4 weeks")
        
        # Success probability calculation
        opportunity.success_probability = await self._calculate_success_probability(
            creator_profile, partner_profile, compatibility, collaboration_type
        )
        
        # Generate risk and success factors
        await self._analyze_collaboration_factors(opportunity, creator_profile, partner_profile)
        
        # Generate actionable content
        await self._generate_collaboration_content(opportunity, creator_profile, partner_profile)
        
        return opportunity
    
    async def _calculate_success_probability(
        self,
        creator_profile: CreatorProfile,
        partner_profile: CreatorProfile,
        compatibility: CompatibilityFactors,
        collaboration_type: CollaborationType
    ) -> float:
        """Calculate probability of collaboration success"""
        
        base_probability = compatibility.calculate_overall_compatibility()
        
        # Factor in past success rates
        avg_success_rate = (creator_profile.collaboration_success_rate + partner_profile.collaboration_success_rate) / 2
        base_probability = (base_probability + avg_success_rate) / 2
        
        # Apply collaboration type modifiers
        type_modifiers = {
            CollaborationType.CROSS_PROMOTION: 1.1,  # Generally easier
            CollaborationType.LIVE_STREAM: 1.0,
            CollaborationType.PLAYLIST_FEATURE: 1.1,
            CollaborationType.VIDEO_COLLABORATION: 0.9,  # More complex
            CollaborationType.MUSIC_COLLABORATION: 0.8,  # Most complex
            CollaborationType.TOUR_COLLABORATION: 0.7,   # Highest complexity
            CollaborationType.BRAND_PARTNERSHIP: 0.9
        }
        
        modifier = type_modifiers.get(collaboration_type, 1.0)
        probability = base_probability * modifier
        
        # Factor in communication and professionalism
        comm_factor = (compatibility.communication_compatibility_score + 
                      creator_profile.professionalism_score + 
                      partner_profile.professionalism_score) / 3
        
        probability = (probability * 0.8) + (comm_factor * 0.2)
        
        return min(95, max(5, probability))  # Cap between 5% and 95%
    
    async def _analyze_collaboration_factors(
        self,
        opportunity: CollaborationOpportunity,
        creator_profile: CreatorProfile,
        partner_profile: CreatorProfile
    ):
        """
Analyze risk and success factors for collaboration"""
        
        compatibility = opportunity.compatibility_factors
        
        # Success factors
        if compatibility.audience_alignment_score > 80:
            opportunity.success_factors.append("High audience alignment - shared target demographic")
        
        if compatibility.content_synergy_score > 75:
            opportunity.success_factors.append("Strong content synergy - complementary skills and themes")
        
        if len(compatibility.platform_overlap) > 1:
            opportunity.success_factors.append(f"Multi-platform presence - shared presence on {', '.join(compatibility.platform_overlap)}")
        
        if creator_profile.collaboration_success_rate > 80 and partner_profile.collaboration_success_rate > 80:
            opportunity.success_factors.append("Both creators have proven collaboration track records")
        
        if compatibility.budget_compatibility_score > 80:
            opportunity.success_factors.append("Aligned budget expectations")
        
        # Risk factors
        if compatibility.communication_compatibility_score < 60:
            opportunity.risk_factors.append("Potential communication challenges")
        
        if abs(creator_profile.total_followers - partner_profile.total_followers) > creator_profile.total_followers * 5:
            opportunity.risk_factors.append("Significant audience size disparity")
        
        if creator_profile.professionalism_score < 70 or partner_profile.professionalism_score < 70:
            opportunity.risk_factors.append("Below-average professionalism scores")
        
        if compatibility.schedule_compatibility_score < 60:
            opportunity.risk_factors.append("Potential scheduling conflicts")
        
        if len(creator_profile.past_collaborations) == 0 or len(partner_profile.past_collaborations) == 0:
            opportunity.risk_factors.append("Limited collaboration experience")
    
    async def _generate_collaboration_content(
        self,
        opportunity: CollaborationOpportunity,
        creator_profile: CreatorProfile,
        partner_profile: CreatorProfile
    ):
        """Generate actionable collaboration content and proposals"""
        
        collaboration_type = opportunity.collaboration_type
        
        # Generate collaboration proposal
        proposals = {
            CollaborationType.MUSIC_COLLABORATION: f"Propose a musical collaboration combining {creator_profile.name}'s style with {partner_profile.name}'s expertise",
            CollaborationType.VIDEO_COLLABORATION: f"Create a joint video project leveraging both creators' audiences and skills",
            CollaborationType.CROSS_PROMOTION: f"Exchange promotional content to reach each other's audiences",
            CollaborationType.LIVE_STREAM: f"Host a joint live stream event featuring both creators",
            CollaborationType.BRAND_PARTNERSHIP: f"Partner on brand collaborations that align with both creators' values"
        }
        
        opportunity.collaboration_proposal = proposals.get(
            collaboration_type, 
            f"Explore {collaboration_type.value.replace('_', ' ')} opportunities together"
        )
        
        # Generate suggested approach
        approaches = {
            CollaborationType.MUSIC_COLLABORATION: "Start with a simple remix or acoustic version, then progress to original compositions",
            CollaborationType.VIDEO_COLLABORATION: "Begin with a cameo appearance or joint interview before planning full collaborative content",
            CollaborationType.CROSS_PROMOTION: "Start with social media shoutouts and story features",
            CollaborationType.LIVE_STREAM: "Plan a Q&A session or casual conversation stream",
            CollaborationType.BRAND_PARTNERSHIP: "Identify mutual brand interests and approach together"
        }
        
        opportunity.suggested_approach = approaches.get(
            collaboration_type,
            "Start small with low-commitment collaboration to build trust and compatibility"
        )
        
        # Generate key talking points
        common_themes = opportunity.compatibility_factors.content_theme_overlap
        common_platforms = opportunity.compatibility_factors.platform_overlap
        
        talking_points = [
            f"Shared audience interests in {', '.join(common_themes[:3])}" if common_themes else "Complementary audience interests",
            f"Combined reach of {opportunity.estimated_reach:,} followers",
            f"Mutual platforms: {', '.join(common_platforms)}" if common_platforms else "Cross-platform expansion opportunity"
        ]
        
        if opportunity.compatibility_factors.calculate_overall_compatibility() > 80:
            talking_points.append("High compatibility score indicates strong collaboration potential")
        
        opportunity.key_talking_points = talking_points
        
        # Generate content ideas
        content_ideas = []
        
        if collaboration_type == CollaborationType.MUSIC_COLLABORATION:
            content_ideas = [
                "Acoustic duet or remix of popular songs",
                "Behind-the-scenes content creation process",
                "Split-screen performance videos",
                "Collaborative playlist curation"
            ]
        elif collaboration_type == CollaborationType.VIDEO_COLLABORATION:
            content_ideas = [
                "Challenge videos featuring both creators",
                "Tutorial or educational content combining expertise",
                "Reaction videos to each other's content",
                "Day-in-the-life collaboration"
            ]
        elif collaboration_type == CollaborationType.CROSS_PROMOTION:
            content_ideas = [
                "Instagram story takeovers",
                "Mutual shoutouts and features",
                "Collaborative giveaways or contests",
                "Cross-posting content with credits"
            ]
        
        opportunity.content_ideas = content_ideas
    
    async def _calculate_quality_metrics(
        self,
        analysis: CollaborationQualityAnalysis,
        all_opportunities: List[CollaborationOpportunity]
    ):
        """Calculate overall quality metrics for the analysis"""
        
        if all_opportunities:
            # Average compatibility score
            compatibility_scores = [
                opp.compatibility_factors.calculate_overall_compatibility() 
                for opp in all_opportunities
            ]
            analysis.average_compatibility_score = statistics.mean(compatibility_scores)
            
            # High quality matches (compatibility > 75)
            analysis.high_quality_matches = sum(
                1 for score in compatibility_scores if score > 75
            )
            
            # Potential revenue increase
            total_revenue_potential = sum(opp.revenue_potential for opp in all_opportunities[:5])  # Top 5
            analysis.potential_revenue_increase = total_revenue_potential
            
            # Estimated audience growth
            unique_audiences = set()
            for opp in all_opportunities[:10]:  # Top 10
                unique_audiences.add(opp.partner_creator.creator_id)
            
            audience_growth = sum(
                opp.partner_creator.total_followers 
                for opp in all_opportunities[:10]
                if opp.partner_creator.creator_id in unique_audiences
            )
            
            # Apply overlap reduction (assume 30% overlap on average)
            analysis.estimated_audience_growth = int(audience_growth * 0.7)
    
    async def _generate_strategic_insights(
        self,
        analysis: CollaborationQualityAnalysis,
        market_data: Optional[Dict[str, Any]]
    ):
        """
Generate strategic insights and recommendations"""
        
        creator_profile = analysis.creator_profile
        
        # Collaboration strengths
        if creator_profile.collaboration_success_rate > 80:
            analysis.collaboration_strengths.append("Proven track record of successful collaborations")
        
        if creator_profile.engagement_rate > 0.05:
            analysis.collaboration_strengths.append("High audience engagement rate")
        
        if creator_profile.professionalism_score > 85:
            analysis.collaboration_strengths.append("High professionalism score")
        
        if len(creator_profile.platforms) > 3:
            analysis.collaboration_strengths.append("Multi-platform presence")
        
        if creator_profile.content_quality_score > 80:
            analysis.collaboration_strengths.append("High-quality content production")
        
        # Improvement areas
        if creator_profile.collaboration_success_rate < 60:
            analysis.improvement_areas.append("Improve collaboration success rate through better partner selection")
        
        if creator_profile.response_time_hours > 48:
            analysis.improvement_areas.append("Reduce response time to improve collaboration efficiency")
        
        if analysis.average_compatibility_score < 60:
            analysis.improvement_areas.append("Focus on finding more compatible collaboration partners")
        
        if len(creator_profile.past_collaborations) < 3:
            analysis.improvement_areas.append("Build collaboration experience through smaller projects")
        
        # Strategic recommendations
        analysis.strategic_recommendations.append(
            f"Focus on {creator_profile.category.value} collaborations for highest success probability"
        )
        
        if analysis.high_quality_matches > 5:
            analysis.strategic_recommendations.append(
                "Prioritize high-compatibility matches for better collaboration outcomes"
            )
        
        if analysis.potential_revenue_increase > Decimal('1000'):
            analysis.strategic_recommendations.append(
                "Strong revenue potential - consider multiple simultaneous collaborations"
            )
        
        if creator_profile.total_followers < 10000:
            analysis.strategic_recommendations.append(
                "Focus on audience growth collaborations to expand reach"
            )
        
        # Market-based recommendations
        if market_data:
            trending_categories = market_data.get('trending_categories', [])
            if creator_profile.category.value in trending_categories:
                analysis.strategic_recommendations.append(
                    f"Leverage current market trend in {creator_profile.category.value} content"
                )
    
    async def _analyze_market_position(
        self,
        analysis: CollaborationQualityAnalysis,
        market_data: Optional[Dict[str, Any]]
    ):
        """Analyze creator's market position for collaboration context"""
        
        creator_profile = analysis.creator_profile
        
        # Basic market position assessment
        if creator_profile.total_followers > 100000:
            analysis.market_position = "established_creator"
        elif creator_profile.total_followers > 10000:
            analysis.market_position = "growing_creator"
        else:
            analysis.market_position = "emerging_creator"
        
        # Competitive advantages
        if creator_profile.engagement_rate > 0.06:
            analysis.competitive_advantages.append("Above-average engagement rate")
        
        if creator_profile.content_quality_score > 85:
            analysis.competitive_advantages.append("Premium content quality")
        
        if len(creator_profile.platforms) > 4:
            analysis.competitive_advantages.append("Strong multi-platform presence")
        
        if creator_profile.collaboration_success_rate > 85:
            analysis.competitive_advantages.append("Excellent collaboration track record")
        
        # Market trends analysis (placeholder)
        analysis.collaboration_trends = {
            "cross_promotion_growth": 25.3,
            "video_collaboration_popularity": 18.7,
            "brand_partnership_demand": 32.1,
            "live_stream_engagement": 41.2
        }


# Export the main analyzer class
__all__ = ['CollaborationQualityAnalyzer', 'CollaborationQualityAnalysis', 'CollaborationType', 'CreatorCategory', 'CompatibilityLevel']
