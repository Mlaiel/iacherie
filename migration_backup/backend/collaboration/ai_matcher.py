"""AI Matcher - AI-Powered Creator Matching Engine

Advanced creator matching system using machine learning, behavioral analysis,
and content similarity for optimal collaboration recommendations.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json

logger = logging.getLogger(__name__)


class CreatorType(Enum):
    """Types of creators"""
    MUSICIAN = "musician"
    BLOGGER = "blogger"
    PHOTOGRAPHER = "photographer"
    INFLUENCER = "influencer"
    COMEDIAN = "comedian"
    VIDEO_CREATOR = "video_creator"
    PODCASTER = "podcaster"
    ARTIST = "artist"
    DESIGNER = "designer"
    WRITER = "writer"


class CollaborationType(Enum):
    """Types of collaborations"""
    CONTENT_CREATION = "content_creation"
    CROSS_PROMOTION = "cross_promotion"
    JOINT_PROJECT = "joint_project"
    SPONSORSHIP = "sponsorship"
    GUEST_APPEARANCE = "guest_appearance"
    REMIX_COLLABORATION = "remix_collaboration"
    TUTORIAL_EXCHANGE = "tutorial_exchange"
    LIVE_COLLABORATION = "live_collaboration"


class MatchStatus(Enum):
    """Status of matching process"""
    PENDING = "pending"
    MATCHED = "matched"
    REJECTED = "rejected"
    ACCEPTED = "accepted"
    EXPIRED = "expired"


@dataclass
class CreatorProfile:
    """Comprehensive creator profile"""
    creator_id: str
    username: str
    creator_type: CreatorType
    genres: List[str]
    content_categories: List[str]
    audience_size: int
    engagement_rate: float
    average_views: int
    collaboration_history: List[str]
    skills: List[str]
    equipment: List[str]
    location: Optional[str] = None
    languages: List[str] = field(default_factory=lambda: ['en'])
    collaboration_preferences: Dict[str, Any] = field(default_factory=dict)
    availability: Dict[str, Any] = field(default_factory=dict)
    pricing: Dict[str, float] = field(default_factory=dict)
    social_platforms: Dict[str, str] = field(default_factory=dict)
    content_style: Dict[str, float] = field(default_factory=dict)
    reputation_score: float = 0.0
    verification_status: bool = False


@dataclass
class MatchRequest:
    """Collaboration match request"""
    request_id: str
    requester_id: str
    collaboration_type: CollaborationType
    desired_creator_types: List[CreatorType]
    project_description: str
    budget_range: Tuple[float, float]
    timeline: str
    required_skills: List[str]
    preferred_location: Optional[str] = None
    content_requirements: Dict[str, Any] = field(default_factory=dict)
    audience_requirements: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None


@dataclass
class MatchResult:
    """AI matching result"""
    match_id: str
    requester_id: str
    matched_creator_id: str
    compatibility_score: float
    match_confidence: float
    collaboration_type: CollaborationType
    predicted_success_rate: float
    skill_alignment: Dict[str, float]
    audience_compatibility: float
    content_synergy: float
    logistics_feasibility: float
    financial_alignment: float
    recommended_collaboration_format: str
    potential_challenges: List[str]
    success_factors: List[str]
    next_steps: List[str]
    match_timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class MatchAnalysis:
    """Comprehensive match analysis result"""
    request_id: str
    top_matches: List[MatchResult]
    alternative_matches: List[MatchResult]
    match_statistics: Dict[str, Any]
    market_insights: Dict[str, Any]
    optimization_suggestions: List[str]
    analysis_timestamp: datetime = field(default_factory=datetime.now)


class AIMatcher:
    """AI-powered creator matching engine"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.matching_algorithm = self.config.get('matching_algorithm', 'hybrid_ml')
        self.min_compatibility_score = self.config.get('min_compatibility_score', 0.6)
        self.max_matches_per_request = self.config.get('max_matches_per_request', 10)
        
        # Matching weights for different factors
        self.matching_weights = {
            'skill_compatibility': 0.25,
            'audience_alignment': 0.20,
            'content_synergy': 0.15,
            'logistics_feasibility': 0.15,
            'financial_alignment': 0.10,
            'reputation_compatibility': 0.10,
            'collaboration_history': 0.05
        }
        
        # Creator database (in real implementation, this would be a database)
        self.creator_profiles = {}
        
        # Matching history for learning
        self.matching_history = []
        
        logger.info("AIMatcher initialized with AI-powered matching capabilities")
    
    async def find_matches(
        self,
        match_request: MatchRequest,
        creator_pool: Optional[List[CreatorProfile]] = None
    ) -> MatchAnalysis:
        """Find optimal creator matches for a collaboration request"""
        try:
            logger.info(f"Finding matches for request {match_request.request_id}")
            
            # Get available creator pool
            if not creator_pool:
                creator_pool = await self._get_available_creators(match_request)
            
            # Filter creators by basic requirements
            filtered_creators = await self._filter_creators_by_requirements(
                creator_pool, match_request
            )
            
            # Calculate compatibility scores
            match_results = []
            for creator in filtered_creators:
                compatibility = await self._calculate_comprehensive_compatibility(
                    match_request, creator
                )
                
                if compatibility.compatibility_score >= self.min_compatibility_score:
                    match_results.append(compatibility)
            
            # Sort by compatibility score
            match_results.sort(key=lambda x: x.compatibility_score, reverse=True)
            
            # Categorize matches
            top_matches = match_results[:self.max_matches_per_request]
            alternative_matches = match_results[self.max_matches_per_request:self.max_matches_per_request*2]
            
            # Generate match statistics
            match_statistics = await self._generate_match_statistics(
                match_request, match_results, creator_pool
            )
            
            # Generate market insights
            market_insights = await self._generate_market_insights(
                match_request, creator_pool
            )
            
            # Generate optimization suggestions
            optimization_suggestions = await self._generate_optimization_suggestions(
                match_request, match_results
            )
            
            analysis = MatchAnalysis(
                request_id=match_request.request_id,
                top_matches=top_matches,
                alternative_matches=alternative_matches,
                match_statistics=match_statistics,
                market_insights=market_insights,
                optimization_suggestions=optimization_suggestions
            )
            
            logger.info(f"Found {len(top_matches)} top matches for request {match_request.request_id}")
            return analysis
            
        except Exception as e:
            logger.error(f"Match finding failed for request {match_request.request_id}: {e}")
            raise
    
    async def _get_available_creators(self, match_request: MatchRequest) -> List[CreatorProfile]:
        """Get available creators from database (simulated)"""
        # In real implementation, query database with availability filters
        creators = []
        
        # Simulate creator database
        creator_types = list(CreatorType)
        
        for i in range(50):  # Generate 50 sample creators
            creator = await self._generate_sample_creator(i, creator_types)
            creators.append(creator)
        
        return creators
    
    async def _generate_sample_creator(self, creator_id: int, creator_types: List[CreatorType]) -> CreatorProfile:
        """Generate sample creator profile for demonstration"""
        import random
        
        creator_type = random.choice(creator_types)
        
        # Generate realistic data based on creator type
        if creator_type == CreatorType.MUSICIAN:
            genres = random.sample(['pop', 'rock', 'jazz', 'electronic', 'hip-hop', 'classical'], k=random.randint(1, 3))
            skills = ['music_production', 'songwriting', 'performance', 'mixing']
            equipment = ['microphone', 'audio_interface', 'daw', 'instruments']
        elif creator_type == CreatorType.PHOTOGRAPHER:
            genres = random.sample(['portrait', 'landscape', 'fashion', 'wildlife', 'street'], k=random.randint(1, 3))
            skills = ['photo_editing', 'lighting', 'composition', 'post_processing']
            equipment = ['camera', 'lenses', 'lighting_kit', 'editing_software']
        elif creator_type == CreatorType.VIDEO_CREATOR:
            genres = random.sample(['tutorial', 'entertainment', 'review', 'vlog', 'documentary'], k=random.randint(1, 3))
            skills = ['video_editing', 'cinematography', 'storytelling', 'animation']
            equipment = ['camera', 'microphone', 'editing_software', 'lighting']
        else:
            genres = ['general']
            skills = ['content_creation', 'social_media', 'writing']
            equipment = ['computer', 'software']
        
        return CreatorProfile(
            creator_id=f"creator_{creator_id}",
            username=f"creator_{creator_id}",
            creator_type=creator_type,
            genres=genres,
            content_categories=genres,
            audience_size=random.randint(1000, 1000000),
            engagement_rate=random.uniform(0.02, 0.12),
            average_views=random.randint(500, 100000),
            collaboration_history=[f"collab_{random.randint(1, 100)}" for _ in range(random.randint(0, 5))],
            skills=skills,
            equipment=equipment,
            location=random.choice(['US', 'UK', 'CA', 'AU', 'DE', None]),
            languages=['en'] + random.sample(['es', 'fr', 'de', 'it'], k=random.randint(0, 2)),
            collaboration_preferences={
                'preferred_collaboration_types': random.sample(list(CollaborationType), k=random.randint(1, 3)),
                'max_travel_distance': random.randint(0, 500),
                'min_budget': random.randint(100, 1000)
            },
            availability={
                'available_days': random.sample(['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'], k=random.randint(3, 7)),
                'timezone': 'UTC',
                'hours_per_week': random.randint(10, 40)
            },
            pricing={
                'hourly_rate': random.uniform(25, 200),
                'project_minimum': random.uniform(100, 2000),
                'collaboration_rate': random.uniform(500, 5000)
            },
            social_platforms={
                'instagram': f"@creator_{creator_id}",
                'youtube': f"creator_{creator_id}",
                'tiktok': f"@creator_{creator_id}"
            },
            content_style={
                'creativity': random.uniform(0.3, 1.0),
                'professionalism': random.uniform(0.5, 1.0),
                'humor': random.uniform(0.0, 0.8),
                'educational': random.uniform(0.2, 0.9),
                'entertainment': random.uniform(0.3, 1.0)
            },
            reputation_score=random.uniform(3.5, 5.0),
            verification_status=random.choice([True, False])
        )
    
    async def _filter_creators_by_requirements(
        self,
        creators: List[CreatorProfile],
        match_request: MatchRequest
    ) -> List[CreatorProfile]:
        """Filter creators by basic requirements"""
        filtered = []
        
        for creator in creators:
            # Check creator type
            if creator.creator_type not in match_request.desired_creator_types:
                continue
            
            # Check required skills
            if match_request.required_skills:
                if not any(skill in creator.skills for skill in match_request.required_skills):
                    continue
            
            # Check location if specified
            if match_request.preferred_location and creator.location:
                if creator.location != match_request.preferred_location:
                    continue
            
            # Check budget alignment
            creator_min_budget = creator.pricing.get('project_minimum', 0)
            if creator_min_budget > match_request.budget_range[1]:
                continue
            
            # Check audience requirements
            audience_reqs = match_request.audience_requirements
            if audience_reqs.get('min_audience_size'):
                if creator.audience_size < audience_reqs['min_audience_size']:
                    continue
            
            if audience_reqs.get('min_engagement_rate'):
                if creator.engagement_rate < audience_reqs['min_engagement_rate']:
                    continue
            
            filtered.append(creator)
        
        return filtered
    
    async def _calculate_comprehensive_compatibility(
        self,
        match_request: MatchRequest,
        creator: CreatorProfile
    ) -> MatchResult:
        """Calculate comprehensive compatibility between request and creator"""
        # Calculate individual compatibility scores
        skill_alignment = await self._calculate_skill_alignment(match_request, creator)
        audience_compatibility = await self._calculate_audience_compatibility(match_request, creator)
        content_synergy = await self._calculate_content_synergy(match_request, creator)
        logistics_feasibility = await self._calculate_logistics_feasibility(match_request, creator)
        financial_alignment = await self._calculate_financial_alignment(match_request, creator)
        reputation_compatibility = await self._calculate_reputation_compatibility(creator)
        collaboration_history_score = await self._calculate_collaboration_history_score(creator)
        
        # Calculate weighted overall compatibility score
        compatibility_score = (
            skill_alignment['overall_score'] * self.matching_weights['skill_compatibility'] +
            audience_compatibility * self.matching_weights['audience_alignment'] +
            content_synergy * self.matching_weights['content_synergy'] +
            logistics_feasibility * self.matching_weights['logistics_feasibility'] +
            financial_alignment * self.matching_weights['financial_alignment'] +
            reputation_compatibility * self.matching_weights['reputation_compatibility'] +
            collaboration_history_score * self.matching_weights['collaboration_history']
        )
        
        # Calculate match confidence
        match_confidence = await self._calculate_match_confidence(
            compatibility_score, skill_alignment, creator
        )
        
        # Predict success rate
        predicted_success_rate = await self._predict_collaboration_success(
            compatibility_score, match_request, creator
        )
        
        # Generate recommendations and insights
        collaboration_format = await self._recommend_collaboration_format(match_request, creator)
        challenges = await self._identify_potential_challenges(match_request, creator)
        success_factors = await self._identify_success_factors(match_request, creator)
        next_steps = await self._generate_next_steps(match_request, creator)
        
        return MatchResult(
            match_id=f"match_{match_request.request_id}_{creator.creator_id}",
            requester_id=match_request.requester_id,
            matched_creator_id=creator.creator_id,
            compatibility_score=round(compatibility_score, 3),
            match_confidence=round(match_confidence, 3),
            collaboration_type=match_request.collaboration_type,
            predicted_success_rate=round(predicted_success_rate, 3),
            skill_alignment=skill_alignment,
            audience_compatibility=round(audience_compatibility, 3),
            content_synergy=round(content_synergy, 3),
            logistics_feasibility=round(logistics_feasibility, 3),
            financial_alignment=round(financial_alignment, 3),
            recommended_collaboration_format=collaboration_format,
            potential_challenges=challenges,
            success_factors=success_factors,
            next_steps=next_steps
        )
    
    async def _calculate_skill_alignment(
        self,
        match_request: MatchRequest,
        creator: CreatorProfile
    ) -> Dict[str, float]:
        """Calculate skill alignment between request and creator"""
        required_skills = set(match_request.required_skills)
        creator_skills = set(creator.skills)
        
        # Calculate skill overlap
        overlapping_skills = required_skills.intersection(creator_skills)
        missing_skills = required_skills - creator_skills
        additional_skills = creator_skills - required_skills
        
        # Calculate alignment scores
        if required_skills:
            skill_coverage = len(overlapping_skills) / len(required_skills)
        else:
            skill_coverage = 1.0
        
        # Bonus for additional relevant skills
        additional_skill_bonus = min(0.2, len(additional_skills) * 0.05)
        
        # Overall skill score
        overall_score = min(1.0, skill_coverage + additional_skill_bonus)
        
        return {
            'overall_score': overall_score,
            'skill_coverage': skill_coverage,
            'overlapping_skills': list(overlapping_skills),
            'missing_skills': list(missing_skills),
            'additional_skills': list(additional_skills),
            'skill_match_details': {
                skill: 1.0 if skill in creator_skills else 0.0
                for skill in required_skills
            }
        }
    
    async def _calculate_audience_compatibility(
        self,
        match_request: MatchRequest,
        creator: CreatorProfile
    ) -> float:
        """Calculate audience compatibility"""
        audience_reqs = match_request.audience_requirements
        
        if not audience_reqs:
            return 0.8  # Default good compatibility if no specific requirements
        
        compatibility_factors = []
        
        # Audience size compatibility
        if 'target_audience_size' in audience_reqs:
            target_size = audience_reqs['target_audience_size']
            size_ratio = min(creator.audience_size / target_size, target_size / creator.audience_size)
            compatibility_factors.append(size_ratio)
        
        # Engagement rate compatibility
        if 'min_engagement_rate' in audience_reqs:
            min_engagement = audience_reqs['min_engagement_rate']
            if creator.engagement_rate >= min_engagement:
                engagement_score = min(1.0, creator.engagement_rate / min_engagement)
            else:
                engagement_score = creator.engagement_rate / min_engagement
            compatibility_factors.append(engagement_score)
        
        # Demographics compatibility (simplified)
        if 'target_demographics' in audience_reqs:
            demographics_match = 0.7  # Simplified assumption
            compatibility_factors.append(demographics_match)
        
        if compatibility_factors:
            return sum(compatibility_factors) / len(compatibility_factors)
        else:
            return 0.8
    
    async def _calculate_content_synergy(
        self,
        match_request: MatchRequest,
        creator: CreatorProfile
    ) -> float:
        """Calculate content synergy potential"""
        content_reqs = match_request.content_requirements
        
        if not content_reqs:
            return 0.7  # Default moderate synergy
        
        synergy_factors = []
        
        # Genre/category alignment
        if 'preferred_genres' in content_reqs:
            preferred_genres = set(content_reqs['preferred_genres'])
            creator_genres = set(creator.genres)
            genre_overlap = len(preferred_genres.intersection(creator_genres))
            
            if preferred_genres:
                genre_score = genre_overlap / len(preferred_genres)
            else:
                genre_score = 0.5
            
            synergy_factors.append(genre_score)
        
        # Content style compatibility
        if 'content_style_preferences' in content_reqs:
            style_prefs = content_reqs['content_style_preferences']
            style_compatibility = 0.0
            style_count = 0
            
            for style, importance in style_prefs.items():
                if style in creator.content_style:
                    creator_style_score = creator.content_style[style]
                    compatibility = 1.0 - abs(importance - creator_style_score)
                    style_compatibility += compatibility
                    style_count += 1
            
            if style_count > 0:
                style_score = style_compatibility / style_count
                synergy_factors.append(style_score)
        
        # Quality alignment
        quality_score = min(1.0, creator.reputation_score / 4.0)  # Normalize 5-star rating
        synergy_factors.append(quality_score)
        
        if synergy_factors:
            return sum(synergy_factors) / len(synergy_factors)
        else:
            return 0.7
    
    async def _calculate_logistics_feasibility(
        self,
        match_request: MatchRequest,
        creator: CreatorProfile
    ) -> float:
        """Calculate logistics feasibility"""
        feasibility_factors = []
        
        # Location compatibility
        if match_request.preferred_location and creator.location:
            if match_request.preferred_location == creator.location:
                location_score = 1.0
            else:
                # Could add distance calculation here
                location_score = 0.3  # Assume some compatibility for different locations
        else:
            location_score = 0.7  # Remote work assumption
        
        feasibility_factors.append(location_score)
        
        # Timeline compatibility
        timeline_score = 0.8  # Simplified assumption
        feasibility_factors.append(timeline_score)
        
        # Availability compatibility
        if creator.availability:
            available_hours = creator.availability.get('hours_per_week', 20)
            # Estimate required hours (simplified)
            required_hours = 10  # Default assumption
            
            if available_hours >= required_hours:
                availability_score = 1.0
            else:
                availability_score = available_hours / required_hours
        else:
            availability_score = 0.6
        
        feasibility_factors.append(availability_score)
        
        return sum(feasibility_factors) / len(feasibility_factors)
    
    async def _calculate_financial_alignment(
        self,
        match_request: MatchRequest,
        creator: CreatorProfile
    ) -> float:
        """Calculate financial alignment"""
        budget_min, budget_max = match_request.budget_range
        
        # Creator's minimum requirements
        creator_min = creator.pricing.get('project_minimum', 0)
        creator_rate = creator.pricing.get('collaboration_rate', creator_min)
        
        # Check if budgets are compatible
        if creator_min > budget_max:
            return 0.0  # No alignment possible
        
        if creator_rate <= budget_min:
            return 1.0  # Perfect alignment
        
        # Calculate proportional alignment
        if creator_rate <= budget_max:
            # Creator's rate is within budget range
            alignment = 1.0 - ((creator_rate - budget_min) / (budget_max - budget_min)) * 0.3
        else:
            # Creator's rate exceeds budget
            overage = creator_rate - budget_max
            max_acceptable_overage = budget_max * 0.2  # 20% overage tolerance
            
            if overage <= max_acceptable_overage:
                alignment = 0.7 - (overage / max_acceptable_overage) * 0.7
            else:
                alignment = 0.0
        
        return max(0.0, alignment)
    
    async def _calculate_reputation_compatibility(self, creator: CreatorProfile) -> float:
        """Calculate reputation compatibility"""
        # Normalize reputation score (assuming 5-star scale)
        reputation_score = creator.reputation_score / 5.0
        
        # Verification bonus
        verification_bonus = 0.1 if creator.verification_status else 0.0
        
        # Collaboration history bonus
        history_bonus = min(0.1, len(creator.collaboration_history) * 0.02)
        
        total_score = min(1.0, reputation_score + verification_bonus + history_bonus)
        
        return total_score
    
    async def _calculate_collaboration_history_score(self, creator: CreatorProfile) -> float:
        """Calculate collaboration history score"""
        history_count = len(creator.collaboration_history)
        
        if history_count == 0:
            return 0.3  # New creators get some benefit of doubt
        elif history_count <= 2:
            return 0.5
        elif history_count <= 5:
            return 0.7
        elif history_count <= 10:
            return 0.8
        else:
            return 0.9  # Experienced collaborators
    
    async def _calculate_match_confidence(
        self,
        compatibility_score: float,
        skill_alignment: Dict[str, float],
        creator: CreatorProfile
    ) -> float:
        """Calculate confidence in the match"""
        confidence_factors = []
        
        # Base confidence from compatibility score
        base_confidence = compatibility_score
        confidence_factors.append(base_confidence)
        
        # Skill coverage confidence
        skill_confidence = skill_alignment['skill_coverage']
        confidence_factors.append(skill_confidence)
        
        # Experience confidence
        experience_factor = min(1.0, len(creator.collaboration_history) / 5)
        confidence_factors.append(experience_factor)
        
        # Reputation confidence
        reputation_factor = creator.reputation_score / 5.0
        confidence_factors.append(reputation_factor)
        
        # Verification confidence
        verification_factor = 1.0 if creator.verification_status else 0.7
        confidence_factors.append(verification_factor)
        
        # Calculate weighted average
        weights = [0.4, 0.25, 0.15, 0.15, 0.05]
        confidence = sum(factor * weight for factor, weight in zip(confidence_factors, weights))
        
        return confidence
    
    async def _predict_collaboration_success(
        self,
        compatibility_score: float,
        match_request: MatchRequest,
        creator: CreatorProfile
    ) -> float:
        """Predict collaboration success rate using ML-like approach"""
        # Success factors
        success_factors = []
        
        # Compatibility contribution
        success_factors.append(compatibility_score * 0.4)
        
        # Experience contribution
        experience_score = min(1.0, len(creator.collaboration_history) / 3)
        success_factors.append(experience_score * 0.2)
        
        # Reputation contribution
        reputation_score = creator.reputation_score / 5.0
        success_factors.append(reputation_score * 0.2)
        
        # Engagement rate contribution (proxy for creator quality)
        engagement_score = min(1.0, creator.engagement_rate / 0.08)  # 8% is excellent
        success_factors.append(engagement_score * 0.1)
        
        # Budget alignment contribution
        budget_alignment = await self._calculate_financial_alignment(match_request, creator)
        success_factors.append(budget_alignment * 0.1)
        
        predicted_success = sum(success_factors)
        
        # Add some randomness to simulate ML prediction uncertainty
        import random
        uncertainty = random.uniform(-0.05, 0.05)
        
        return max(0.0, min(1.0, predicted_success + uncertainty))
    
    async def _recommend_collaboration_format(
        self,
        match_request: MatchRequest,
        creator: CreatorProfile
    ) -> str:
        """Recommend optimal collaboration format"""
        collaboration_type = match_request.collaboration_type
        creator_type = creator.creator_type
        
        format_recommendations = {
            (CollaborationType.CONTENT_CREATION, CreatorType.MUSICIAN): "Joint music production and cross-platform release",
            (CollaborationType.CONTENT_CREATION, CreatorType.VIDEO_CREATOR): "Collaborative video series with shared editing",
            (CollaborationType.CONTENT_CREATION, CreatorType.PHOTOGRAPHER): "Joint photo project with shared portfolio",
            (CollaborationType.CROSS_PROMOTION, CreatorType.INFLUENCER): "Mutual promotion campaign across social platforms",
            (CollaborationType.GUEST_APPEARANCE, CreatorType.PODCASTER): "Guest appearance on podcast with reciprocal feature",
            (CollaborationType.REMIX_COLLABORATION, CreatorType.MUSICIAN): "Remix exchange with dual release strategy"
        }
        
        recommendation = format_recommendations.get(
            (collaboration_type, creator_type),
            f"Collaborative {collaboration_type.value} project optimized for both creators' strengths"
        )
        
        return recommendation
    
    async def _identify_potential_challenges(
        self,
        match_request: MatchRequest,
        creator: CreatorProfile
    ) -> List[str]:
        """Identify potential collaboration challenges"""
        challenges = []
        
        # Budget challenges
        budget_alignment = await self._calculate_financial_alignment(match_request, creator)
        if budget_alignment < 0.7:
            challenges.append("Budget alignment may require negotiation")
        
        # Location challenges
        if match_request.preferred_location and creator.location:
            if match_request.preferred_location != creator.location:
                challenges.append("Geographic distance may impact collaboration logistics")
        
        # Experience level challenges
        if len(creator.collaboration_history) < 2:
            challenges.append("Limited collaboration experience may require additional support")
        
        # Timeline challenges
        if creator.availability.get('hours_per_week', 40) < 20:
            challenges.append("Limited availability may affect project timeline")
        
        # Skill gap challenges
        required_skills = set(match_request.required_skills)
        creator_skills = set(creator.skills)
        missing_skills = required_skills - creator_skills
        
        if missing_skills:
            challenges.append(f"Skill development needed in: {', '.join(missing_skills)}")
        
        return challenges[:5]  # Limit to top 5 challenges
    
    async def _identify_success_factors(
        self,
        match_request: MatchRequest,
        creator: CreatorProfile
    ) -> List[str]:
        """Identify collaboration success factors"""
        success_factors = []
        
        # Strong skill alignment
        skill_alignment = await self._calculate_skill_alignment(match_request, creator)
        if skill_alignment['skill_coverage'] > 0.8:
            success_factors.append("Excellent skill alignment ensures project capability")
        
        # Strong reputation
        if creator.reputation_score > 4.5:
            success_factors.append("High reputation indicates reliable collaboration partner")
        
        # Good engagement rate
        if creator.engagement_rate > 0.06:
            success_factors.append("Strong audience engagement suggests quality content creation")
        
        # Collaboration experience
        if len(creator.collaboration_history) > 3:
            success_factors.append("Proven collaboration experience reduces project risk")
        
        # Verification status
        if creator.verification_status:
            success_factors.append("Verified creator status ensures authenticity and professionalism")
        
        # Audience size
        if creator.audience_size > 50000:
            success_factors.append("Large audience provides significant reach potential")
        
        return success_factors[:5]  # Limit to top 5 factors
    
    async def _generate_next_steps(
        self,
        match_request: MatchRequest,
        creator: CreatorProfile
    ) -> List[str]:
        """Generate recommended next steps for the collaboration"""
        next_steps = [
            f"Send collaboration proposal to {creator.username}",
            "Schedule initial video call to discuss project details",
            "Review and align on project timeline and deliverables",
            "Establish communication channels and project management tools"
        ]
        
        # Budget-related steps
        budget_alignment = await self._calculate_financial_alignment(match_request, creator)
        if budget_alignment < 0.8:
            next_steps.append("Negotiate budget and payment terms")
        
        # Contract steps
        next_steps.append("Draft collaboration agreement and contracts")
        
        # Platform-specific steps
        if creator.creator_type == CreatorType.MUSICIAN:
            next_steps.append("Discuss music rights and distribution strategy")
        elif creator.creator_type == CreatorType.VIDEO_CREATOR:
            next_steps.append("Plan video production schedule and equipment sharing")
        
        next_steps.append("Begin collaboration with clearly defined milestones")
        
        return next_steps[:8]  # Limit to 8 steps
    
    async def _generate_match_statistics(
        self,
        match_request: MatchRequest,
        match_results: List[MatchResult],
        creator_pool: List[CreatorProfile]
    ) -> Dict[str, Any]:
        """Generate match statistics"""
        total_creators = len(creator_pool)
        qualified_matches = len(match_results)
        
        if match_results:
            avg_compatibility = sum(match.compatibility_score for match in match_results) / len(match_results)
            max_compatibility = max(match.compatibility_score for match in match_results)
            min_compatibility = min(match.compatibility_score for match in match_results)
        else:
            avg_compatibility = max_compatibility = min_compatibility = 0.0
        
        # Creator type distribution
        creator_type_dist = {}
        for creator in creator_pool:
            creator_type = creator.creator_type.value
            creator_type_dist[creator_type] = creator_type_dist.get(creator_type, 0) + 1
        
        return {
            'total_creators_analyzed': total_creators,
            'qualified_matches_found': qualified_matches,
            'match_rate': round(qualified_matches / max(total_creators, 1), 3),
            'average_compatibility_score': round(avg_compatibility, 3),
            'highest_compatibility_score': round(max_compatibility, 3),
            'lowest_compatibility_score': round(min_compatibility, 3),
            'creator_type_distribution': creator_type_dist,
            'analysis_timestamp': datetime.now().isoformat()
        }
    
    async def _generate_market_insights(
        self,
        match_request: MatchRequest,
        creator_pool: List[CreatorProfile]
    ) -> Dict[str, Any]:
        """Generate market insights for the collaboration request"""
        # Calculate market metrics
        total_creators = len(creator_pool)
        desired_types = match_request.desired_creator_types
        
        # Availability by creator type
        type_availability = {}
        for creator_type in desired_types:
            count = sum(1 for creator in creator_pool if creator.creator_type == creator_type)
            type_availability[creator_type.value] = count
        
        # Budget analysis
        budget_min, budget_max = match_request.budget_range
        budget_compatible_creators = 0
        avg_creator_rate = 0
        
        for creator in creator_pool:
            creator_rate = creator.pricing.get('collaboration_rate', 1000)
            avg_creator_rate += creator_rate
            
            if creator_rate <= budget_max:
                budget_compatible_creators += 1
        
        avg_creator_rate = avg_creator_rate / max(total_creators, 1)
        
        # Skills availability
        required_skills = match_request.required_skills
        skill_availability = {}
        
        for skill in required_skills:
            count = sum(1 for creator in creator_pool if skill in creator.skills)
            skill_availability[skill] = {
                'available_creators': count,
                'availability_rate': round(count / max(total_creators, 1), 3)
            }
        
        return {
            'market_size': total_creators,
            'creator_type_availability': type_availability,
            'budget_compatibility_rate': round(budget_compatible_creators / max(total_creators, 1), 3),
            'average_market_rate': round(avg_creator_rate, 2),
            'budget_position': 'competitive' if budget_max >= avg_creator_rate else 'below_market',
            'skill_availability': skill_availability,
            'market_competitiveness': 'high' if total_creators > 20 else 'moderate'
        }
    
    async def _generate_optimization_suggestions(
        self,
        match_request: MatchRequest,
        match_results: List[MatchResult]
    ) -> List[str]:
        """Generate optimization suggestions for better matches"""
        suggestions = []
        
        if not match_results:
            suggestions.extend([
                "Consider expanding creator type requirements",
                "Review budget range - may need to increase for better matches",
                "Broaden geographic preferences to include remote collaboration",
                "Reduce required skills to essential items only"
            ])
            return suggestions
        
        # Analyze match quality
        if match_results:
            avg_score = sum(match.compatibility_score for match in match_results) / len(match_results)
            
            if avg_score < 0.7:
                suggestions.append("Consider adjusting requirements for higher compatibility scores")
            
            # Budget analysis
            financial_scores = [match.financial_alignment for match in match_results]
            avg_financial = sum(financial_scores) / len(financial_scores)
            
            if avg_financial < 0.6:
                suggestions.append("Consider increasing budget range for better creator options")
            
            # Skill analysis
            skill_issues = 0
            for match in match_results[:5]:  # Check top 5 matches
                if any('Skill development needed' in challenge for challenge in match.potential_challenges):
                    skill_issues += 1
            
            if skill_issues > 2:
                suggestions.append("Consider prioritizing essential skills over nice-to-have skills")
            
            # Location analysis
            location_issues = sum(1 for match in match_results[:5] 
                                 if any('Geographic distance' in challenge for challenge in match.potential_challenges))
            
            if location_issues > 2:
                suggestions.append("Consider remote collaboration options to expand creator pool")
        
        # General optimization suggestions
        suggestions.extend([
            "Provide more detailed project description to attract better matches",
            "Consider offering non-monetary benefits (exposure, portfolio pieces)",
            "Build relationships with creators before formal collaboration requests"
        ])
        
        return suggestions[:6]  # Limit to 6 suggestions


# Export main class
__all__ = ['AIMatcher', 'CreatorProfile', 'MatchRequest', 'MatchResult', 'MatchAnalysis', 'CreatorType', 'CollaborationType']