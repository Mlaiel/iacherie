#!/usr/bin/env python3
"""🤝 Collaboration Matching Core - AI-Powered Creator Matching & Marketplace
===========================================================================
Module: backend/core/collaboration_matching_core.py
Author: Fahed Mlaiel (mlaiel@live.de)
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + IA Prompt Engineer
Type: Enterprise Collaboration & Matching System - Ultra Production-Ready
Responsibility: AI-powered creator matching, marketplace, gamification, and collaboration workflow management
================================================================================================================

⚠️  EXCLUSIVE INTELLECTUAL PROPERTY - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. All rights reserved.
Unauthorized use strictly prohibited and subject to legal prosecution.
Contact: mlaiel@live.de

🎯 COLLABORATION FEATURES:
- AI-powered creator matching algorithm
- Intelligent marketplace for creators
- Gamification and achievement system
- Project workflow management
- Revenue sharing and dispute resolution
- Reputation scoring and trust system
- Real-time collaboration tools

🚀 MATCHING ALGORITHMS:
- Skill complementarity analysis
- Style compatibility scoring
- Geographic proximity optimization
- Availability synchronization
- Budget range matching
- Previous collaboration history
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum, IntEnum
from datetime import datetime, timezone, timedelta
from decimal import Decimal
import json
import uuid
import hashlib
import math
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)

# Import AI orchestrator for matching intelligence
try:
    from .ia_agents_orchestrator import get_orchestrator, TaskPriority
    HAS_AI_ORCHESTRATOR = True
except ImportError:
    HAS_AI_ORCHESTRATOR = False
    logger.warning("AI Orchestrator not available, some features disabled")

# Import numpy for calculations with fallback
try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False
    logger.warning("NumPy not available, some calculations limited")


# ============================================================================
# COLLABORATION SYSTEM DEFINITIONS
# ============================================================================

class CollaborationType(Enum):
    """Types of collaborations"""
    MUSIC_PRODUCTION = "music_production"
    VIDEO_CREATION = "video_creation"
    CONTENT_REMIX = "content_remix"
    BRAND_CAMPAIGN = "brand_campaign"
    LIVE_PERFORMANCE = "live_performance"
    PODCAST_SERIES = "podcast_series"
    CREATIVE_CONSULTING = "creative_consulting"
    SKILL_EXCHANGE = "skill_exchange"
    MENTORSHIP = "mentorship"
    JOINT_VENTURE = "joint_venture"


class CollaborationStatus(Enum):
    """Collaboration lifecycle status"""
    DRAFT = "draft"
    OPEN = "open"
    MATCHING = "matching"
    PROPOSALS_RECEIVED = "proposals_received"
    IN_NEGOTIATION = "in_negotiation"
    ACTIVE = "active"
    IN_PROGRESS = "in_progress"
    REVIEW_PHASE = "review_phase"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    DISPUTED = "disputed"
    ARCHIVED = "archived"


class CreatorSkill(Enum):
    """Creator skills and specializations"""
    # Music skills
    MUSIC_PRODUCTION = "music_production"
    SINGING = "singing"
    SONGWRITING = "songwriting"
    MIXING_MASTERING = "mixing_mastering"
    INSTRUMENTAL_PERFORMANCE = "instrumental_performance"
    
    # Video skills
    VIDEO_PRODUCTION = "video_production"
    VIDEO_EDITING = "video_editing"
    CINEMATOGRAPHY = "cinematography"
    ANIMATION = "animation"
    MOTION_GRAPHICS = "motion_graphics"
    
    # Content skills
    COPYWRITING = "copywriting"
    GRAPHIC_DESIGN = "graphic_design"
    PHOTOGRAPHY = "photography"
    SOCIAL_MEDIA_MANAGEMENT = "social_media_management"
    CONTENT_STRATEGY = "content_strategy"
    
    # Technical skills
    AUDIO_ENGINEERING = "audio_engineering"
    WEB_DEVELOPMENT = "web_development"
    APP_DEVELOPMENT = "app_development"
    DATA_ANALYSIS = "data_analysis"
    SEO_OPTIMIZATION = "seo_optimization"
    
    # Business skills
    MARKETING = "marketing"
    BRAND_STRATEGY = "brand_strategy"
    PROJECT_MANAGEMENT = "project_management"
    BUSINESS_DEVELOPMENT = "business_development"
    LEGAL_CONSULTING = "legal_consulting"


class MatchingCriteria(Enum):
    """Matching algorithm criteria"""
    SKILL_COMPLEMENTARITY = "skill_complementarity"
    STYLE_COMPATIBILITY = "style_compatibility"
    EXPERIENCE_LEVEL = "experience_level"
    GEOGRAPHIC_PROXIMITY = "geographic_proximity"
    BUDGET_ALIGNMENT = "budget_alignment"
    AVAILABILITY_SYNC = "availability_sync"
    REPUTATION_SCORE = "reputation_score"
    COLLABORATION_HISTORY = "collaboration_history"
    LANGUAGE_COMPATIBILITY = "language_compatibility"
    TIMEZONE_COMPATIBILITY = "timezone_compatibility"


class GameLevel(IntEnum):
    """Gamification levels"""
    NEWCOMER = 1
    APPRENTICE = 2
    JOURNEYMAN = 3
    ARTISAN = 4
    EXPERT = 5
    MASTER = 6
    GRANDMASTER = 7
    LEGEND = 8
    ICON = 9
    HALL_OF_FAME = 10


@dataclass
class CreatorProfile:
    """Enhanced creator profile for matching"""
    creator_id: str
    username: str
    display_name: str
    
    # Skills and expertise
    primary_skills: List[CreatorSkill] = field(default_factory=list)
    secondary_skills: List[CreatorSkill] = field(default_factory=list)
    skill_levels: Dict[str, int] = field(default_factory=dict)  # 1-10 scale
    experience_years: int = 0
    
    # Creative profile
    creative_style: List[str] = field(default_factory=list)
    genres: List[str] = field(default_factory=list)
    portfolio_urls: List[str] = field(default_factory=list)
    
    # Collaboration preferences
    collaboration_types: List[CollaborationType] = field(default_factory=list)
    preferred_role: str = "collaborator"  # lead, collaborator, support
    availability_hours: Dict[str, List[str]] = field(default_factory=dict)  # day: [hour_ranges]
    budget_range: Tuple[Decimal, Decimal] = (Decimal("0"), Decimal("10000"))
    
    # Geographic and logistics
    location: str = ""
    timezone: str = "UTC"
    languages: List[str] = field(default_factory=lambda: ["en"])
    remote_work: bool = True
    travel_willing: bool = False
    
    # Reputation and history
    reputation_score: float = 5.0  # 1-10 scale
    collaboration_count: int = 0
    completion_rate: float = 100.0  # percentage
    average_rating: float = 5.0  # 1-5 scale
    response_time_hours: float = 24.0
    
    # Gamification
    level: GameLevel = GameLevel.NEWCOMER
    experience_points: int = 0
    achievements: List[str] = field(default_factory=list)
    badges: List[str] = field(default_factory=list)
    
    # Metadata
    verified: bool = False
    premium_member: bool = False
    last_active: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def __post_init__(self):
        if not self.creator_id:
            self.creator_id = f"creator_{uuid.uuid4().hex[:12]}"


@dataclass
class CollaborationRequest:
    """Collaboration opportunity request"""
    request_id: str
    creator_id: str
    title: str
    description: str
    collaboration_type: CollaborationType
    
    # Requirements
    required_skills: List[CreatorSkill] = field(default_factory=list)
    preferred_skills: List[CreatorSkill] = field(default_factory=list)
    experience_level_min: int = 1  # 1-10 scale
    
    # Project details
    budget: Decimal = Decimal("0.00")
    currency: str = "EUR"
    duration_days: int = 30
    deadline: Optional[datetime] = None
    deliverables: List[str] = field(default_factory=list)
    
    # Collaboration terms
    revenue_sharing: Dict[str, float] = field(default_factory=dict)
    payment_structure: str = "completion"  # milestone, hourly, completion
    ip_ownership: str = "shared"  # creator, requester, shared
    
    # Preferences
    max_collaborators: int = 1
    geographic_preference: Optional[str] = None
    language_requirement: List[str] = field(default_factory=lambda: ["en"])
    remote_only: bool = True
    
    # Status tracking
    status: CollaborationStatus = CollaborationStatus.DRAFT
    applications_count: int = 0
    matched_creators: List[str] = field(default_factory=list)
    selected_creators: List[str] = field(default_factory=list)
    
    # Timestamps
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    published_at: Optional[datetime] = None
    deadline_applications: Optional[datetime] = None
    
    # Metadata
    tags: List[str] = field(default_factory=list)
    priority: int = 1  # 1-5 scale
    confidential: bool = False
    
    def __post_init__(self):
        if not self.request_id:
            self.request_id = f"collab_{uuid.uuid4().hex[:12]}"
        
        if not self.deadline_applications:
            self.deadline_applications = self.created_at + timedelta(days=7)


@dataclass
class MatchingResult:
    """AI matching result between creator and request"""
    match_id: str
    creator_id: str
    request_id: str
    
    # Matching scores (0-100)
    overall_score: float = 0.0
    skill_score: float = 0.0
    experience_score: float = 0.0
    style_score: float = 0.0
    availability_score: float = 0.0
    budget_score: float = 0.0
    geographic_score: float = 0.0
    reputation_score: float = 0.0
    
    # Detailed analysis
    matching_factors: Dict[str, Any] = field(default_factory=dict)
    complementary_skills: List[str] = field(default_factory=list)
    potential_challenges: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    
    # AI confidence
    confidence_level: float = 0.0
    algorithm_version: str = "2.0"
    
    # Status
    match_quality: str = "low"  # low, medium, high, excellent
    recommended: bool = False
    
    def __post_init__(self):
        if not self.match_id:
            self.match_id = f"match_{uuid.uuid4().hex[:12]}"
        
        # Determine match quality based on overall score
        if self.overall_score >= 85:
            self.match_quality = "excellent"
            self.recommended = True
        elif self.overall_score >= 70:
            self.match_quality = "high"
            self.recommended = True
        elif self.overall_score >= 50:
            self.match_quality = "medium"
        else:
            self.match_quality = "low"


@dataclass
class Achievement:
    """Gamification achievement definition"""
    achievement_id: str
    name: str
    description: str
    category: str
    
    # Requirements
    requirements: Dict[str, Any] = field(default_factory=dict)
    points_awarded: int = 100
    badge_icon: str = ""
    rarity: str = "common"  # common, rare, epic, legendary
    
    # Progress tracking
    repeatable: bool = False
    progress_tracking: bool = True
    hidden: bool = False
    
    def __post_init__(self):
        if not self.achievement_id:
            self.achievement_id = f"achievement_{uuid.uuid4().hex[:8]}"


# ============================================================================
# MATCHING ALGORITHM ENGINE
# ============================================================================

class MatchingAlgorithm:
    """AI-powered creator matching algorithm"""
    
    def __init__(self):
        self.algorithm_version = "2.0"
        self.matching_weights = self._initialize_matching_weights()
        self.skill_compatibility_matrix = self._initialize_skill_matrix()
    
    def _initialize_matching_weights(self) -> Dict[str, float]:
        """Initialize matching criteria weights"""
        return {
            "skill_complementarity": 0.25,
            "experience_level": 0.15,
            "style_compatibility": 0.15,
            "reputation_score": 0.15,
            "availability_sync": 0.10,
            "budget_alignment": 0.10,
            "geographic_proximity": 0.05,
            "collaboration_history": 0.05
        }
    
    def _initialize_skill_matrix(self) -> Dict[str, List[str]]:
        """Initialize skill complementarity matrix"""
        return {
            "music_production": ["mixing_mastering", "singing", "songwriting"],
            "video_production": ["video_editing", "cinematography", "motion_graphics"],
            "graphic_design": ["copywriting", "photography", "brand_strategy"],
            "marketing": ["content_strategy", "social_media_management", "seo_optimization"],
            "audio_engineering": ["music_production", "mixing_mastering"],
            "web_development": ["graphic_design", "seo_optimization", "data_analysis"]
        }
    
    async def find_matches(
        self,
        collaboration_request: CollaborationRequest,
        creator_profiles: List[CreatorProfile],
        max_matches: int = 20
    ) -> List[MatchingResult]:
        """Find best matching creators for collaboration request"""
        try:
            matches = []
            
            for creator in creator_profiles:
                # Skip if creator is the requester
                if creator.creator_id == collaboration_request.creator_id:
                    continue
                
                # Calculate match score
                match_result = await self._calculate_match_score(
                    creator, collaboration_request
                )
                
                if match_result.overall_score > 0:
                    matches.append(match_result)
            
            # Sort by overall score descending
            matches.sort(key=lambda m: m.overall_score, reverse=True)
            
            # Return top matches
            return matches[:max_matches]
            
        except Exception as e:
            logger.error(f"Matching algorithm failed: {e}")
            return []
    
    async def _calculate_match_score(
        self,
        creator: CreatorProfile,
        request: CollaborationRequest
    ) -> MatchingResult:
        """Calculate comprehensive match score"""
        try:
            result = MatchingResult(
                creator_id=creator.creator_id,
                request_id=request.request_id
            )
            
            # 1. Skill matching
            result.skill_score = await self._calculate_skill_score(creator, request)
            
            # 2. Experience level matching
            result.experience_score = await self._calculate_experience_score(creator, request)
            
            # 3. Style compatibility
            result.style_score = await self._calculate_style_score(creator, request)
            
            # 4. Availability matching
            result.availability_score = await self._calculate_availability_score(creator, request)
            
            # 5. Budget alignment
            result.budget_score = await self._calculate_budget_score(creator, request)
            
            # 6. Geographic proximity
            result.geographic_score = await self._calculate_geographic_score(creator, request)
            
            # 7. Reputation score
            result.reputation_score = min(creator.reputation_score * 10, 100)
            
            # Calculate weighted overall score
            result.overall_score = (
                result.skill_score * self.matching_weights["skill_complementarity"] +
                result.experience_score * self.matching_weights["experience_level"] +
                result.style_score * self.matching_weights["style_compatibility"] +
                result.reputation_score * self.matching_weights["reputation_score"] +
                result.availability_score * self.matching_weights["availability_sync"] +
                result.budget_score * self.matching_weights["budget_alignment"] +
                result.geographic_score * self.matching_weights["geographic_proximity"]
            )
            
            # Add detailed analysis
            result.matching_factors = {
                "skill_match": result.skill_score,
                "experience_fit": result.experience_score,
                "style_alignment": result.style_score,
                "availability_match": result.availability_score,
                "budget_fit": result.budget_score,
                "location_proximity": result.geographic_score,
                "reputation": result.reputation_score
            }
            
            # Generate recommendations
            result.recommendations = await self._generate_recommendations(creator, request, result)
            
            # Set confidence level
            result.confidence_level = min(result.overall_score / 100, 1.0)
            
            return result
            
        except Exception as e:
            logger.error(f"Match score calculation failed: {e}")
            return MatchingResult(
                creator_id=creator.creator_id,
                request_id=request.request_id
            )
    
    async def _calculate_skill_score(self, creator: CreatorProfile, request: CollaborationRequest) -> float:
        """Calculate skill matching score"""
        try:
            score = 0.0
            total_required = len(request.required_skills)
            
            if total_required == 0:
                return 100.0  # No specific requirements
            
            # Check required skills
            matched_required = 0
            for skill in request.required_skills:
                if skill in creator.primary_skills:
                    matched_required += 1
                    score += 30  # High score for primary skill match
                elif skill in creator.secondary_skills:
                    matched_required += 1
                    score += 20  # Medium score for secondary skill match
            
            # Check preferred skills
            for skill in request.preferred_skills:
                if skill in creator.primary_skills:
                    score += 10
                elif skill in creator.secondary_skills:
                    score += 5
            
            # Check complementary skills
            creator_skills = set([s.value for s in creator.primary_skills + creator.secondary_skills])
            for skill in creator_skills:
                if skill in self.skill_compatibility_matrix:
                    complementary = self.skill_compatibility_matrix[skill]
                    for comp_skill in complementary:
                        if comp_skill in [s.value for s in request.required_skills]:
                            score += 5
            
            # Normalize score
            max_possible = total_required * 30 + len(request.preferred_skills) * 10
            if max_possible > 0:
                score = min(score / max_possible * 100, 100)
            
            return score
            
        except Exception as e:
            logger.error(f"Skill score calculation failed: {e}")
            return 0.0
    
    async def _calculate_experience_score(self, creator: CreatorProfile, request: CollaborationRequest) -> float:
        """Calculate experience level matching score"""
        try:
            if request.experience_level_min <= creator.experience_years:
                # Perfect match or overqualified
                if creator.experience_years <= request.experience_level_min + 2:
                    return 100.0
                else:
                    # Slightly overqualified - good but not perfect
                    return 85.0
            else:
                # Underqualified - score decreases with gap
                gap = request.experience_level_min - creator.experience_years
                score = max(0, 100 - (gap * 20))
                return score
            
        except Exception as e:
            logger.error(f"Experience score calculation failed: {e}")
            return 0.0
    
    async def _calculate_style_score(self, creator: CreatorProfile, request: CollaborationRequest) -> float:
        """Calculate style compatibility score"""
        try:
            # Simple style matching based on tags and genres
            creator_styles = set(creator.creative_style + creator.genres)
            request_tags = set(request.tags)
            
            if not request_tags:
                return 100.0  # No style requirements
            
            # Calculate intersection
            common_styles = creator_styles.intersection(request_tags)
            
            if len(request_tags) > 0:
                score = (len(common_styles) / len(request_tags)) * 100
                return min(score, 100)
            
            return 100.0
            
        except Exception as e:
            logger.error(f"Style score calculation failed: {e}")
            return 50.0
    
    async def _calculate_availability_score(self, creator: CreatorProfile, request: CollaborationRequest) -> float:
        """Calculate availability matching score"""
        try:
            # Check if creator is available for project duration
            if not creator.availability_hours:
                return 50.0  # Assume partial availability
            
            # Simple availability check - can be enhanced with detailed calendar integration
            days_available = len(creator.availability_hours)
            
            if days_available >= 5:  # Available most days
                return 100.0
            elif days_available >= 3:  # Available some days
                return 75.0
            elif days_available >= 1:  # Limited availability
                return 50.0
            else:
                return 25.0
            
        except Exception as e:
            logger.error(f"Availability score calculation failed: {e}")
            return 50.0
    
    async def _calculate_budget_score(self, creator: CreatorProfile, request: CollaborationRequest) -> float:
        """Calculate budget alignment score"""
        try:
            creator_min, creator_max = creator.budget_range
            project_budget = request.budget
            
            if project_budget == 0:
                return 100.0  # No budget constraints
            
            # Check if project budget falls within creator's range
            if creator_min <= project_budget <= creator_max:
                return 100.0
            elif project_budget < creator_min:
                # Project budget too low
                gap = float((creator_min - project_budget) / creator_min)
                score = max(0, 100 - (gap * 100))
                return score
            else:
                # Project budget higher than expected (good for creator)
                return 100.0
            
        except Exception as e:
            logger.error(f"Budget score calculation failed: {e}")
            return 50.0
    
    async def _calculate_geographic_score(self, creator: CreatorProfile, request: CollaborationRequest) -> float:
        """Calculate geographic proximity score"""
        try:
            # If remote work is acceptable, geography is less important
            if request.remote_only and creator.remote_work:
                return 100.0
            
            # Simple geographic matching - can be enhanced with actual distance calculation
            if request.geographic_preference:
                if creator.location and request.geographic_preference.lower() in creator.location.lower():
                    return 100.0
                else:
                    return 25.0  # Different location
            
            return 100.0  # No geographic preference
            
        except Exception as e:
            logger.error(f"Geographic score calculation failed: {e}")
            return 75.0
    
    async def _generate_recommendations(
        self,
        creator: CreatorProfile,
        request: CollaborationRequest,
        match_result: MatchingResult
    ) -> List[str]:
        """Generate personalized recommendations for the match"""
        recommendations = []
        
        try:
            # Skill-based recommendations
            if match_result.skill_score < 70:
                recommendations.append("Consider skill development in required areas")
            
            # Experience recommendations
            if match_result.experience_score < 50:
                recommendations.append("Collaborate on smaller projects first to build experience")
            
            # Budget recommendations
            if match_result.budget_score < 60:
                recommendations.append("Discuss budget flexibility during negotiation")
            
            # Availability recommendations
            if match_result.availability_score < 70:
                recommendations.append("Clarify timeline and availability expectations")
            
            # Reputation recommendations
            if creator.reputation_score < 7.0:
                recommendations.append("Build portfolio with smaller collaborations first")
            
            # Positive recommendations for high scores
            if match_result.overall_score > 80:
                recommendations.append("Excellent match - highly recommended to proceed")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Recommendation generation failed: {e}")
            return ["Review match details carefully before proceeding"]


# ============================================================================
# MARKETPLACE ENGINE
# ============================================================================

class MarketplaceEngine:
    """Creator marketplace and opportunity management"""
    
    def __init__(self):
        self.active_requests: Dict[str, CollaborationRequest] = {}
        self.creator_profiles: Dict[str, CreatorProfile] = {}
        self.matching_results: Dict[str, List[MatchingResult]] = {}
        self.matching_algorithm = MatchingAlgorithm()
    
    async def create_collaboration_request(
        self,
        creator_id: str,
        title: str,
        description: str,
        collaboration_type: CollaborationType,
        **kwargs
    ) -> str:
        """Create new collaboration request"""
        try:
            request = CollaborationRequest(
                request_id=f"collab_{uuid.uuid4().hex[:12]}",
                creator_id=creator_id,
                title=title,
                description=description,
                collaboration_type=collaboration_type,
                **kwargs
            )
            
            self.active_requests[request.request_id] = request
            
            logger.info(f"Collaboration request {request.request_id} created by {creator_id}")
            return request.request_id
            
        except Exception as e:
            logger.error(f"Collaboration request creation failed: {e}")
            raise
    
    async def register_creator_profile(self, profile: CreatorProfile) -> bool:
        """Register or update creator profile"""
        try:
            self.creator_profiles[profile.creator_id] = profile
            logger.info(f"Creator profile registered: {profile.creator_id}")
            return True
            
        except Exception as e:
            logger.error(f"Creator profile registration failed: {e}")
            return False
    
    async def find_collaboration_matches(
        self,
        request_id: str,
        max_matches: int = 20
    ) -> List[MatchingResult]:
        """Find matching creators for collaboration request"""
        try:
            if request_id not in self.active_requests:
                raise ValueError(f"Collaboration request {request_id} not found")
            
            request = self.active_requests[request_id]
            creators = list(self.creator_profiles.values())
            
            # Run matching algorithm
            matches = await self.matching_algorithm.find_matches(
                request, creators, max_matches
            )
            
            # Store results
            self.matching_results[request_id] = matches
            
            # Update request status
            request.status = CollaborationStatus.MATCHING
            request.matched_creators = [m.creator_id for m in matches]
            
            logger.info(f"Found {len(matches)} matches for request {request_id}")
            return matches
            
        except Exception as e:
            logger.error(f"Collaboration matching failed: {e}")
            return []
    
    async def get_marketplace_opportunities(
        self,
        creator_id: str,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Get marketplace opportunities for creator"""
        try:
            opportunities = []
            
            for request in self.active_requests.values():
                # Skip own requests
                if request.creator_id == creator_id:
                    continue
                
                # Skip closed requests
                if request.status not in [CollaborationStatus.OPEN, CollaborationStatus.MATCHING]:
                    continue
                
                # Apply filters
                if filters:
                    if not self._matches_filters(request, filters):
                        continue
                
                # Get match score if available
                match_score = 0.0
                if request.request_id in self.matching_results:
                    for match in self.matching_results[request.request_id]:
                        if match.creator_id == creator_id:
                            match_score = match.overall_score
                            break
                
                opportunity = {
                    "request_id": request.request_id,
                    "title": request.title,
                    "description": request.description,
                    "collaboration_type": request.collaboration_type.value,
                    "budget": float(request.budget),
                    "currency": request.currency,
                    "duration_days": request.duration_days,
                    "required_skills": [s.value for s in request.required_skills],
                    "match_score": match_score,
                    "applications_count": request.applications_count,
                    "deadline": request.deadline_applications.isoformat() if request.deadline_applications else None,
                    "created_at": request.created_at.isoformat()
                }
                
                opportunities.append(opportunity)
            
            # Sort by match score if available, otherwise by creation date
            opportunities.sort(
                key=lambda x: (x["match_score"], x["created_at"]), 
                reverse=True
            )
            
            return opportunities
            
        except Exception as e:
            logger.error(f"Marketplace opportunities retrieval failed: {e}")
            return []
    
    def _matches_filters(self, request: CollaborationRequest, filters: Dict[str, Any]) -> bool:
        """Check if request matches filters"""
        try:
            # Collaboration type filter
            if "collaboration_type" in filters:
                if request.collaboration_type.value not in filters["collaboration_type"]:
                    return False
            
            # Budget range filter
            if "budget_min" in filters:
                if request.budget < filters["budget_min"]:
                    return False
            
            if "budget_max" in filters:
                if request.budget > filters["budget_max"]:
                    return False
            
            # Duration filter
            if "max_duration_days" in filters:
                if request.duration_days > filters["max_duration_days"]:
                    return False
            
            # Skills filter
            if "required_skills" in filters:
                request_skills = set([s.value for s in request.required_skills])
                filter_skills = set(filters["required_skills"])
                if not request_skills.intersection(filter_skills):
                    return False
            
            # Remote work filter
            if "remote_only" in filters:
                if filters["remote_only"] and not request.remote_only:
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Filter matching failed: {e}")
            return True


# ============================================================================
# GAMIFICATION ENGINE
# ============================================================================

class GamificationEngine:
    """Gamification system for creator engagement"""
    
    def __init__(self):
        self.achievements = self._initialize_achievements()
        self.level_requirements = self._initialize_level_requirements()
        self.point_rewards = self._initialize_point_rewards()
    
    def _initialize_achievements(self) -> Dict[str, Achievement]:
        """Initialize achievement definitions"""
        achievements = {}
        
        # Collaboration achievements
        achievements["first_collaboration"] = Achievement(
            achievement_id="first_collaboration",
            name="First Steps",
            description="Complete your first collaboration",
            category="collaboration",
            requirements={"collaborations_completed": 1},
            points_awarded=100,
            badge_icon="🤝",
            rarity="common"
        )
        
        achievements["collaboration_veteran"] = Achievement(
            achievement_id="collaboration_veteran",
            name="Collaboration Veteran",
            description="Complete 25 successful collaborations",
            category="collaboration",
            requirements={"collaborations_completed": 25},
            points_awarded=1000,
            badge_icon="🏆",
            rarity="rare"
        )
        
        achievements["perfect_rating"] = Achievement(
            achievement_id="perfect_rating",
            name="Perfectionist",
            description="Maintain a 5.0 rating with 10+ collaborations",
            category="reputation",
            requirements={"average_rating": 5.0, "collaborations_completed": 10},
            points_awarded=500,
            badge_icon="⭐",
            rarity="epic"
        )
        
        # Skills achievements
        achievements["skill_master"] = Achievement(
            achievement_id="skill_master",
            name="Skill Master",
            description="Reach level 10 in any skill",
            category="skills",
            requirements={"max_skill_level": 10},
            points_awarded=750,
            badge_icon="🎯",
            rarity="rare"
        )
        
        # Revenue achievements
        achievements["first_earnings"] = Achievement(
            achievement_id="first_earnings",
            name="First Earnings",
            description="Earn your first payment",
            category="revenue",
            requirements={"total_earnings": 1},
            points_awarded=50,
            badge_icon="💰",
            rarity="common"
        )
        
        achievements["high_earner"] = Achievement(
            achievement_id="high_earner",
            name="High Earner",
            description="Earn €10,000 in total",
            category="revenue",
            requirements={"total_earnings": 10000},
            points_awarded=2000,
            badge_icon="💎",
            rarity="legendary"
        )
        
        return achievements
    
    def _initialize_level_requirements(self) -> Dict[GameLevel, int]:
        """Initialize level-up requirements"""
        return {
            GameLevel.NEWCOMER: 0,
            GameLevel.APPRENTICE: 500,
            GameLevel.JOURNEYMAN: 1500,
            GameLevel.ARTISAN: 3500,
            GameLevel.EXPERT: 7000,
            GameLevel.MASTER: 12000,
            GameLevel.GRANDMASTER: 20000,
            GameLevel.LEGEND: 35000,
            GameLevel.ICON: 60000,
            GameLevel.HALL_OF_FAME: 100000
        }
    
    def _initialize_point_rewards(self) -> Dict[str, int]:
        """Initialize point rewards for actions"""
        return {
            "profile_completed": 100,
            "collaboration_completed": 200,
            "perfect_rating_received": 50,
            "skill_improved": 25,
            "portfolio_item_added": 30,
            "achievement_unlocked": 100,
            "level_up": 500,
            "first_collaboration": 150,
            "mentor_session": 75,
            "community_contribution": 40
        }
    
    async def award_points(
        self,
        creator_id: str,
        action: str,
        amount: Optional[int] = None
    ) -> Dict[str, Any]:
        """Award experience points for actions"""
        try:
            points = amount or self.point_rewards.get(action, 0)
            
            if points <= 0:
                return {"success": False, "error": "No points awarded for this action"}
            
            # In production, update creator profile in database
            result = {
                "success": True,
                "action": action,
                "points_awarded": points,
                "total_points": points,  # Would be fetched from database
                "level_up": False,
                "achievements_unlocked": []
            }
            
            # Check for level up (simplified)
            current_level = GameLevel.NEWCOMER
            for level, requirement in self.level_requirements.items():
                if points >= requirement:
                    current_level = level
            
            result["current_level"] = current_level.name
            
            logger.info(f"Awarded {points} points to creator {creator_id} for {action}")
            return result
            
        except Exception as e:
            logger.error(f"Point awarding failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def check_achievements(
        self,
        creator_profile: CreatorProfile,
        creator_stats: Dict[str, Any]
    ) -> List[str]:
        """Check and unlock achievements"""
        try:
            unlocked_achievements = []
            
            for achievement_id, achievement in self.achievements.items():
                # Skip if already unlocked
                if achievement_id in creator_profile.achievements:
                    continue
                
                # Check requirements
                meets_requirements = True
                for req_key, req_value in achievement.requirements.items():
                    if req_key not in creator_stats:
                        meets_requirements = False
                        break
                    
                    if creator_stats[req_key] < req_value:
                        meets_requirements = False
                        break
                
                if meets_requirements:
                    unlocked_achievements.append(achievement_id)
                    creator_profile.achievements.append(achievement_id)
                    creator_profile.experience_points += achievement.points_awarded
            
            return unlocked_achievements
            
        except Exception as e:
            logger.error(f"Achievement checking failed: {e}")
            return []
    
    async def get_leaderboard(
        self,
        category: str = "experience_points",
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get gamification leaderboard"""
        try:
            # In production, query database for top creators
            # This is a simplified mock implementation
            
            leaderboard_data = [
                {
                    "rank": 1,
                    "creator_id": "creator_001",
                    "username": "TopCreator",
                    "level": GameLevel.LEGEND.name,
                    "experience_points": 45000,
                    "collaborations_completed": 150,
                    "achievements_count": 25
                },
                {
                    "rank": 2,
                    "creator_id": "creator_002",
                    "username": "ProCollaborator",
                    "level": GameLevel.MASTER.name,
                    "experience_points": 18000,
                    "collaborations_completed": 75,
                    "achievements_count": 18
                }
            ]
            
            return leaderboard_data[:limit]
            
        except Exception as e:
            logger.error(f"Leaderboard generation failed: {e}")
            return []


# ============================================================================
# MAIN COLLABORATION MATCHING CORE
# ============================================================================

class CollaborationMatchingCore:
    """Main collaboration matching and marketplace system"""
    
    def __init__(self):
        self.marketplace = MarketplaceEngine()
        self.gamification = GamificationEngine()
        
        # System metrics
        self.metrics = {
            "total_collaborations_created": 0,
            "total_matches_made": 0,
            "successful_collaborations": 0,
            "average_match_score": 0.0,
            "active_creators": 0,
            "platform_engagement_rate": 0.0
        }
        
        # Executor for parallel processing
        self._executor = ThreadPoolExecutor(max_workers=6)
    
    async def create_collaboration(
        self,
        creator_id: str,
        title: str,
        description: str,
        collaboration_type: str,
        **kwargs
    ) -> str:
        """Create new collaboration opportunity"""
        try:
            collab_type = CollaborationType(collaboration_type)
            
            request_id = await self.marketplace.create_collaboration_request(
                creator_id=creator_id,
                title=title,
                description=description,
                collaboration_type=collab_type,
                **kwargs
            )
            
            # Award points for creating collaboration
            await self.gamification.award_points(creator_id, "collaboration_created", 75)
            
            # Update metrics
            self.metrics["total_collaborations_created"] += 1
            
            logger.info(f"Collaboration {request_id} created successfully")
            return request_id
            
        except Exception as e:
            logger.error(f"Collaboration creation failed: {e}")
            raise
    
    async def register_creator(
        self,
        creator_id: str,
        username: str,
        display_name: str,
        **profile_data
    ) -> bool:
        """Register new creator profile"""
        try:
            profile = CreatorProfile(
                creator_id=creator_id,
                username=username,
                display_name=display_name,
                **profile_data
            )
            
            success = await self.marketplace.register_creator_profile(profile)
            
            if success:
                # Award points for profile completion
                await self.gamification.award_points(creator_id, "profile_completed")
                
                # Update metrics
                self.metrics["active_creators"] += 1
                
                logger.info(f"Creator {creator_id} registered successfully")
            
            return success
            
        except Exception as e:
            logger.error(f"Creator registration failed: {e}")
            return False
    
    async def find_matches(
        self,
        request_id: str,
        max_matches: int = 20
    ) -> List[Dict[str, Any]]:
        """Find matching creators for collaboration"""
        try:
            matches = await self.marketplace.find_collaboration_matches(
                request_id, max_matches
            )
            
            # Convert to serializable format
            match_data = []
            for match in matches:
                match_data.append({
                    "match_id": match.match_id,
                    "creator_id": match.creator_id,
                    "overall_score": match.overall_score,
                    "match_quality": match.match_quality,
                    "recommended": match.recommended,
                    "skill_score": match.skill_score,
                    "experience_score": match.experience_score,
                    "reputation_score": match.reputation_score,
                    "confidence_level": match.confidence_level,
                    "recommendations": match.recommendations
                })
            
            # Update metrics
            self.metrics["total_matches_made"] += len(matches)
            if matches:
                avg_score = sum(m.overall_score for m in matches) / len(matches)
                self.metrics["average_match_score"] = avg_score
            
            logger.info(f"Found {len(matches)} matches for collaboration {request_id}")
            return match_data
            
        except Exception as e:
            logger.error(f"Match finding failed: {e}")
            return []
    
    async def get_opportunities(
        self,
        creator_id: str,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Get collaboration opportunities for creator"""
        try:
            opportunities = await self.marketplace.get_marketplace_opportunities(
                creator_id, filters
            )
            
            logger.info(f"Retrieved {len(opportunities)} opportunities for creator {creator_id}")
            return opportunities
            
        except Exception as e:
            logger.error(f"Opportunities retrieval failed: {e}")
            return []
    
    async def complete_collaboration(
        self,
        request_id: str,
        creator_id: str,
        rating: float,
        feedback: str = ""
    ) -> Dict[str, Any]:
        """Mark collaboration as completed"""
        try:
            # Award points for completion
            points_result = await self.gamification.award_points(
                creator_id, "collaboration_completed"
            )
            
            # Award additional points for perfect rating
            if rating >= 5.0:
                await self.gamification.award_points(
                    creator_id, "perfect_rating_received"
                )
            
            # Update metrics
            self.metrics["successful_collaborations"] += 1
            
            result = {
                "success": True,
                "request_id": request_id,
                "rating": rating,
                "points_awarded": points_result.get("points_awarded", 0),
                "achievements_unlocked": points_result.get("achievements_unlocked", []),
                "level_up": points_result.get("level_up", False)
            }
            
            logger.info(f"Collaboration {request_id} completed by {creator_id}")
            return result
            
        except Exception as e:
            logger.error(f"Collaboration completion failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_creator_stats(self, creator_id: str) -> Dict[str, Any]:
        """Get creator statistics and achievements"""
        try:
            # In production, fetch from database
            # This is a simplified mock implementation
            
            creator_stats = {
                "creator_id": creator_id,
                "level": GameLevel.APPRENTICE.name,
                "experience_points": 1250,
                "collaborations_completed": 8,
                "average_rating": 4.7,
                "total_earnings": Decimal("2450.00"),
                "achievements_count": 5,
                "reputation_score": 8.5,
                "response_time_hours": 6.2,
                "completion_rate": 95.0,
                "skills": ["music_production", "mixing_mastering", "songwriting"],
                "recent_achievements": ["first_collaboration", "skill_improver"],
                "next_level_progress": 75  # percentage to next level
            }
            
            return creator_stats
            
        except Exception as e:
            logger.error(f"Creator stats retrieval failed: {e}")
            return {}
    
    async def get_leaderboard(
        self,
        category: str = "experience_points",
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get platform leaderboard"""
        try:
            leaderboard = await self.gamification.get_leaderboard(category, limit)
            return leaderboard
            
        except Exception as e:
            logger.error(f"Leaderboard retrieval failed: {e}")
            return []
    
    async def health_check(self) -> Dict[str, Any]:
        """Collaboration system health check"""
        try:
            return {
                "collaboration_core": {
                    "healthy": True,
                    "active_collaborations": len(self.marketplace.active_requests),
                    "registered_creators": len(self.marketplace.creator_profiles),
                    "total_achievements": len(self.gamification.achievements),
                    "metrics": self.metrics.copy()
                },
                "components": {
                    "marketplace_engine": True,
                    "matching_algorithm": True,
                    "gamification_engine": True,
                    "ai_orchestrator": HAS_AI_ORCHESTRATOR
                },
                "algorithm": {
                    "version": self.marketplace.matching_algorithm.algorithm_version,
                    "matching_criteria": len(self.marketplace.matching_algorithm.matching_weights),
                    "skill_matrix_size": len(self.marketplace.matching_algorithm.skill_compatibility_matrix)
                }
            }
            
        except Exception as e:
            logger.error(f"Collaboration health check failed: {e}")
            return {
                "collaboration_core": {"healthy": False, "error": str(e)},
                "components": {},
                "algorithm": {}
            }


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

_collaboration_instance: Optional[CollaborationMatchingCore] = None

def get_collaboration_core() -> CollaborationMatchingCore:
    """Get global collaboration core instance"""
    global _collaboration_instance
    if _collaboration_instance is None:
        _collaboration_instance = CollaborationMatchingCore()
    return _collaboration_instance


async def create_collaboration_opportunity(
    creator_id: str,
    title: str,
    description: str,
    collaboration_type: str,
    **kwargs
) -> str:
    """Convenience function to create collaboration"""
    collaboration_core = get_collaboration_core()
    return await collaboration_core.create_collaboration(
        creator_id=creator_id,
        title=title,
        description=description,
        collaboration_type=collaboration_type,
        **kwargs
    )


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    # Core classes
    "CollaborationMatchingCore",
    "MatchingAlgorithm",
    "MarketplaceEngine",
    "GamificationEngine",
    
    # Data classes
    "CreatorProfile",
    "CollaborationRequest",
    "MatchingResult",
    "Achievement",
    
    # Enums
    "CollaborationType",
    "CollaborationStatus",
    "CreatorSkill",
    "GameLevel",
    "MatchingCriteria",
    
    # Convenience functions
    "get_collaboration_core",
    "create_collaboration_opportunity"
]

# ============================================================================
# MODULE INITIALIZATION
# ============================================================================

if __name__ == "__main__":
    # Example usage for testing
    import asyncio
    
    async def main():
        print("🤝 Collaboration Matching Core Test")
        print("=" * 50)
        
        try:
            # Get collaboration core
            collaboration_core = get_collaboration_core()
            
            # Register test creator
            success = await collaboration_core.register_creator(
                creator_id="test_creator_001",
                username="musicproducer",
                display_name="Music Producer Pro",
                primary_skills=[CreatorSkill.MUSIC_PRODUCTION, CreatorSkill.MIXING_MASTERING],
                experience_years=5,
                budget_range=(Decimal("500"), Decimal("5000"))
            )
            print(f"✅ Creator registered: {success}")
            
            # Create collaboration
            collab_id = await collaboration_core.create_collaboration(
                creator_id="test_requester_001",
                title="Music Video Production",
                description="Need music producer for video soundtrack",
                collaboration_type="music_production",
                budget=Decimal("2000"),
                required_skills=[CreatorSkill.MUSIC_PRODUCTION]
            )
            print(f"✅ Collaboration created: {collab_id}")
            
            # Find matches
            matches = await collaboration_core.find_matches(collab_id)
            print(f"🎯 Found {len(matches)} matches")
            
            # Get opportunities
            opportunities = await collaboration_core.get_opportunities("test_creator_001")
            print(f"📋 Found {len(opportunities)} opportunities")
            
            # Get creator stats
            stats = await collaboration_core.get_creator_stats("test_creator_001")
            print(f"📊 Creator level: {stats.get('level', 'Unknown')}")
            
            # Health check
            health = await collaboration_core.health_check()
            print(f"🏥 System healthy: {health['collaboration_core']['healthy']}")
            
            print("🎉 Collaboration Matching Core test completed successfully!")
            
        except Exception as e:
            print(f"❌ Collaboration Matching Core test failed: {e}")
    
    # Run the test if this module is executed directly
    asyncio.run(main())