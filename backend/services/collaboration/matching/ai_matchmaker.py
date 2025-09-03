"""AI Matchmaker - Advanced Creator Matching Engine

Advanced AI-powered creator matching system using machine learning, behavioral analysis,
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


class AIMatchmaker:
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
        
        logger.info("AIMatchmaker initialized with AI-powered matching capabilities")
    
    async def initialize(self):
        """Initialize the AI matching engine"""
        logger.info("Initializing AI Matchmaker...")
        # Load ML models, connect to databases, etc.
        await self._load_matching_models()
        await self._initialize_creator_database()
        logger.info("AI Matchmaker initialized successfully")
    
    async def shutdown(self):
        """Shutdown the AI matching engine"""
        logger.info("Shutting down AI Matchmaker...")
        # Cleanup resources
        logger.info("AI Matchmaker shutdown complete")
    
    async def find_matches(
        self, 
        match_request: MatchRequest, 
        creator_pool: List[CreatorProfile] = None
    ) -> MatchAnalysis:
        """Find optimal matches for a collaboration request"""
        try:
            logger.info(f"Finding matches for request {match_request.request_id}")
            
            # Use provided creator pool or load from database
            if creator_pool is None:
                creator_pool = await self._load_creator_pool(match_request)
            
            # Calculate compatibility scores for all creators
            match_results = []
            for creator in creator_pool:
                if creator.creator_id != match_request.requester_id:
                    match_result = await self._calculate_compatibility(match_request, creator)
                    if match_result.compatibility_score >= self.min_compatibility_score:
                        match_results.append(match_result)
            
            # Sort by compatibility score
            match_results.sort(key=lambda x: x.compatibility_score, reverse=True)
            
            # Split into top and alternative matches
            top_matches = match_results[:self.max_matches_per_request]
            alternative_matches = match_results[self.max_matches_per_request:self.max_matches_per_request*2]
            
            # Generate analysis
            match_statistics = await self._generate_match_statistics(match_request, match_results)
            market_insights = await self._generate_market_insights(match_request, creator_pool)
            optimization_suggestions = await self._generate_optimization_suggestions(match_request, match_results)
            
            analysis = MatchAnalysis(
                request_id=match_request.request_id,
                top_matches=top_matches,
                alternative_matches=alternative_matches,
                match_statistics=match_statistics,
                market_insights=market_insights,
                optimization_suggestions=optimization_suggestions
            )
            
            # Store for learning
            self.matching_history.append(analysis)
            
            logger.info(f"Found {len(top_matches)} top matches for request {match_request.request_id}")
            return analysis
            
        except Exception as e:
            logger.error(f"Error finding matches: {str(e)}")
            raise
    
    async def _load_matching_models(self):
        """Load ML models for matching"""
        # In real implementation, load trained models
        logger.info("Loading AI matching models...")
    
    async def _initialize_creator_database(self):
        """Initialize creator database connection"""
        # In real implementation, connect to database
        logger.info("Initializing creator database...")
    
    async def _load_creator_pool(self, match_request: MatchRequest) -> List[CreatorProfile]:
        """Load relevant creator pool based on request"""
        # In real implementation, query database
        logger.info(f"Loading creator pool for request {match_request.request_id}")
        return list(self.creator_profiles.values())
    
    async def _calculate_compatibility(
        self, 
        match_request: MatchRequest, 
        creator: CreatorProfile
    ) -> MatchResult:
        """Calculate comprehensive compatibility between request and creator"""
        
        # Calculate individual compatibility factors
        skill_alignment = await self._calculate_skill_alignment(match_request, creator)
        audience_compatibility = await self._calculate_audience_compatibility(match_request, creator)
        content_synergy = await self._calculate_content_synergy(match_request, creator)
        logistics_feasibility = await self._calculate_logistics_feasibility(match_request, creator)
        financial_alignment = await self._calculate_financial_alignment(match_request, creator)
        reputation_compatibility = await self._calculate_reputation_compatibility(match_request, creator)
        
        # Calculate weighted compatibility score
        compatibility_score = (
            skill_alignment.get('overall', 0.0) * self.matching_weights['skill_compatibility'] +
            audience_compatibility * self.matching_weights['audience_alignment'] +
            content_synergy * self.matching_weights['content_synergy'] +
            logistics_feasibility * self.matching_weights['logistics_feasibility'] +
            financial_alignment * self.matching_weights['financial_alignment'] +
            reputation_compatibility * self.matching_weights['reputation_compatibility']
        )
        
        # Generate match result
        match_result = MatchResult(
            match_id=f"match_{match_request.request_id}_{creator.creator_id}",
            requester_id=match_request.requester_id,
            matched_creator_id=creator.creator_id,
            compatibility_score=compatibility_score,
            match_confidence=min(compatibility_score + 0.1, 1.0),
            collaboration_type=match_request.collaboration_type,
            predicted_success_rate=compatibility_score * 0.9,
            skill_alignment=skill_alignment,
            audience_compatibility=audience_compatibility,
            content_synergy=content_synergy,
            logistics_feasibility=logistics_feasibility,
            financial_alignment=financial_alignment,
            recommended_collaboration_format=self._recommend_collaboration_format(match_request, creator),
            potential_challenges=self._identify_potential_challenges(match_request, creator),
            success_factors=self._identify_success_factors(match_request, creator),
            next_steps=self._suggest_next_steps(match_request, creator)
        )
        
        return match_result
    
    async def _calculate_skill_alignment(
        self,
        match_request: MatchRequest,
        creator: CreatorProfile
    ) -> Dict[str, float]:
        """Calculate skill alignment between request and creator"""
        required_skills = set(match_request.required_skills)
        creator_skills = set(creator.skills)
        
        if not required_skills:
            return {'overall': 1.0}
        
        matching_skills = required_skills.intersection(creator_skills)
        alignment_score = len(matching_skills) / len(required_skills)
        
        return {
            'overall': alignment_score,
            'matching_skills': list(matching_skills),
            'missing_skills': list(required_skills - creator_skills)
        }
    
    async def _calculate_audience_compatibility(
        self,
        match_request: MatchRequest,
        creator: CreatorProfile
    ) -> float:
        """Calculate audience compatibility"""
        # Simplified audience compatibility calculation
        audience_requirements = match_request.audience_requirements
        
        if not audience_requirements:
            return 0.8  # Default compatibility
        
        compatibility_score = 0.8  # Base score
        
        # Adjust based on audience size requirements
        if 'min_audience_size' in audience_requirements:
            if creator.audience_size >= audience_requirements['min_audience_size']:
                compatibility_score += 0.1
            else:
                compatibility_score -= 0.2
        
        # Adjust based on engagement rate
        if creator.engagement_rate > 0.05:  # 5% engagement rate threshold
            compatibility_score += 0.1
        
        return max(0.0, min(1.0, compatibility_score))
    
    async def _calculate_content_synergy(
        self,
        match_request: MatchRequest,
        creator: CreatorProfile
    ) -> float:
        """Calculate content synergy potential"""
        # Simplified content synergy calculation
        synergy_score = 0.7  # Base score
        
        # Check content category overlap
        request_categories = set(match_request.content_requirements.get('categories', []))
        creator_categories = set(creator.content_categories)
        
        if request_categories and creator_categories:
            category_overlap = len(request_categories.intersection(creator_categories))
            synergy_score += (category_overlap / len(request_categories)) * 0.2
        
        return max(0.0, min(1.0, synergy_score))
    
    async def _calculate_logistics_feasibility(
        self,
        match_request: MatchRequest,
        creator: CreatorProfile
    ) -> float:
        """Calculate logistics feasibility"""
        feasibility_score = 0.8  # Base score
        
        # Location compatibility
        if match_request.preferred_location and creator.location:
            if match_request.preferred_location.lower() == creator.location.lower():
                feasibility_score += 0.2
            else:
                feasibility_score -= 0.1
        
        return max(0.0, min(1.0, feasibility_score))
    
    async def _calculate_financial_alignment(
        self,
        match_request: MatchRequest,
        creator: CreatorProfile
    ) -> float:
        """Calculate financial alignment"""
        alignment_score = 0.7  # Base score
        
        # Budget compatibility
        min_budget, max_budget = match_request.budget_range
        creator_rate = creator.pricing.get('hourly_rate', 0)
        
        if creator_rate > 0:
            if min_budget <= creator_rate <= max_budget:
                alignment_score += 0.3
            elif creator_rate < min_budget:
                alignment_score += 0.1  # Creator is cheaper than expected
            else:
                alignment_score -= 0.2  # Creator is more expensive
        
        return max(0.0, min(1.0, alignment_score))
    
    async def _calculate_reputation_compatibility(
        self,
        match_request: MatchRequest,
        creator: CreatorProfile
    ) -> float:
        """Calculate reputation compatibility"""
        reputation_score = creator.reputation_score
        
        # Boost for verified creators
        if creator.verification_status:
            reputation_score += 0.1
        
        return max(0.0, min(1.0, reputation_score))
    
    def _recommend_collaboration_format(
        self,
        match_request: MatchRequest,
        creator: CreatorProfile
    ) -> str:
        """Recommend optimal collaboration format"""
        collaboration_type = match_request.collaboration_type
        
        format_recommendations = {
            CollaborationType.CONTENT_CREATION: "Joint content creation with shared creative control",
            CollaborationType.CROSS_PROMOTION: "Mutual promotion across platforms",
            CollaborationType.JOINT_PROJECT: "Collaborative project with defined roles",
            CollaborationType.SPONSORSHIP: "Sponsored content collaboration",
            CollaborationType.GUEST_APPEARANCE: "Guest feature exchange",
            CollaborationType.REMIX_COLLABORATION: "Content remix and adaptation",
            CollaborationType.TUTORIAL_EXCHANGE: "Educational content exchange",
            CollaborationType.LIVE_COLLABORATION: "Real-time collaborative session"
        }
        
        return format_recommendations.get(collaboration_type, "Custom collaboration format")
    
    def _identify_potential_challenges(
        self,
        match_request: MatchRequest,
        creator: CreatorProfile
    ) -> List[str]:
        """Identify potential collaboration challenges"""
        challenges = []
        
        # Location challenges
        if match_request.preferred_location and creator.location:
            if match_request.preferred_location.lower() != creator.location.lower():
                challenges.append("Geographic distance may require remote collaboration")
        
        # Budget challenges
        min_budget, max_budget = match_request.budget_range
        creator_rate = creator.pricing.get('hourly_rate', 0)
        if creator_rate > max_budget:
            challenges.append("Creator rate exceeds budget range")
        
        # Skill gaps
        required_skills = set(match_request.required_skills)
        creator_skills = set(creator.skills)
        missing_skills = required_skills - creator_skills
        if missing_skills:
            challenges.append(f"Missing skills: {', '.join(missing_skills)}")
        
        return challenges
    
    def _identify_success_factors(
        self,
        match_request: MatchRequest,
        creator: CreatorProfile
    ) -> List[str]:
        """Identify factors that contribute to success"""
        success_factors = []
        
        # Skill alignment
        required_skills = set(match_request.required_skills)
        creator_skills = set(creator.skills)
        matching_skills = required_skills.intersection(creator_skills)
        if matching_skills:
            success_factors.append(f"Strong skill alignment: {', '.join(matching_skills)}")
        
        # Reputation
        if creator.reputation_score > 0.8:
            success_factors.append("High reputation score")
        
        # Verification
        if creator.verification_status:
            success_factors.append("Verified creator status")
        
        # Engagement
        if creator.engagement_rate > 0.05:
            success_factors.append("High audience engagement")
        
        return success_factors
    
    def _suggest_next_steps(
        self,
        match_request: MatchRequest,
        creator: CreatorProfile
    ) -> List[str]:
        """Suggest next steps for collaboration"""
        next_steps = [
            "Review creator portfolio and previous work",
            "Schedule initial consultation call",
            "Discuss project timeline and milestones",
            "Negotiate collaboration terms and budget",
            "Draft collaboration agreement",
            "Plan content creation workflow"
        ]
        
        return next_steps
    
    async def _generate_match_statistics(
        self,
        match_request: MatchRequest,
        match_results: List[MatchResult]
    ) -> Dict[str, Any]:
        """Generate matching statistics"""
        if not match_results:
            return {
                'total_matches': 0,
                'average_compatibility': 0.0,
                'match_distribution': {}
            }
        
        compatibility_scores = [result.compatibility_score for result in match_results]
        
        return {
            'total_matches': len(match_results),
            'average_compatibility': sum(compatibility_scores) / len(compatibility_scores),
            'highest_compatibility': max(compatibility_scores),
            'lowest_compatibility': min(compatibility_scores),
            'match_distribution': {
                'excellent': len([s for s in compatibility_scores if s >= 0.9]),
                'good': len([s for s in compatibility_scores if 0.7 <= s < 0.9]),
                'fair': len([s for s in compatibility_scores if 0.5 <= s < 0.7]),
                'poor': len([s for s in compatibility_scores if s < 0.5])
            }
        }
    
    async def _generate_market_insights(
        self,
        match_request: MatchRequest,
        creator_pool: List[CreatorProfile]
    ) -> Dict[str, Any]:
        """Generate market insights for the collaboration request"""
        creator_types = [creator.creator_type for creator in creator_pool]
        type_distribution = {}
        for creator_type in creator_types:
            type_distribution[creator_type.value] = type_distribution.get(creator_type.value, 0) + 1
        
        return {
            'total_creators_available': len(creator_pool),
            'creator_type_distribution': type_distribution,
            'average_audience_size': sum(creator.audience_size for creator in creator_pool) / len(creator_pool) if creator_pool else 0,
            'collaboration_demand': 'high'  # Would be calculated based on historical data
        }
    
    async def _generate_optimization_suggestions(
        self,
        match_request: MatchRequest,
        match_results: List[MatchResult]
    ) -> List[str]:
        """Generate optimization suggestions for better matches"""
        suggestions = []
        
        if not match_results:
            suggestions.append("Consider expanding creator type requirements")
            suggestions.append("Review budget range to attract more creators")
            suggestions.append("Broaden geographic requirements if possible")
        elif len(match_results) < 3:
            suggestions.append("Consider reducing skill requirements to find more matches")
            suggestions.append("Expand collaboration timeline for better availability")
        
        return suggestions


# Export main classes
__all__ = ['AIMatchmaker', 'CreatorProfile', 'MatchRequest', 'MatchResult', 'MatchAnalysis', 'CreatorType', 'CollaborationType', 'MatchStatus']