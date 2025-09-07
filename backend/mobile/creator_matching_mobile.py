"""Mobile Creator Matching Engine

Advanced mobile creator matching system using AI algorithms for intelligent
creator compatibility analysis, skill complementarity assessment, and
mobile-optimized collaboration recommendations.

Business Logic Integration: Mobile Content → IA Processing → Protection → SEO → Creator Matching → Collaboration

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
"""

import asyncio
import logging
import json
import time
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import uuid


logger = logging.getLogger(__name__)


class MatchingStrategy(Enum):
    """Creator matching strategies"""
    SKILL_BASED = "skill_based"
    INTEREST_BASED = "interest_based"
    GEOGRAPHIC = "geographic"
    COLLABORATION_HISTORY = "collaboration_history"
    AI_COMPATIBILITY = "ai_compatibility"
    PROJECT_NEEDS = "project_needs"


class CompatibilityLevel(Enum):
    """Compatibility levels"""
    EXCELLENT = "excellent"
    VERY_GOOD = "very_good"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"


@dataclass
class MobileMatchingConfiguration:
    """Mobile creator matching configuration"""
    matching_strategies: List[MatchingStrategy]
    min_compatibility_score: float = 0.7
    max_matches: int = 10
    geographic_radius_km: Optional[int] = None
    skill_weight: float = 0.4
    interest_weight: float = 0.3
    availability_weight: float = 0.3
    mobile_optimization: bool = True


@dataclass
class CreatorProfile:
    """Creator profile for matching"""
    creator_id: str
    creator_type: str
    skills: List[str]
    interests: List[str]
    experience_level: str
    availability: Dict[str, Any]
    location: Optional[str] = None
    mobile_preferences: Dict[str, Any] = None
    collaboration_history: List[str] = None
    
    def __post_init__(self):
        if self.mobile_preferences is None:
            self.mobile_preferences = {}
        if self.collaboration_history is None:
            self.collaboration_history = []


@dataclass
class MatchResult:
    """Individual creator match result"""
    creator_profile: CreatorProfile
    compatibility_score: float
    compatibility_level: CompatibilityLevel
    matching_factors: Dict[str, float]
    collaboration_potential: str
    recommended_project_types: List[str]
    mobile_collaboration_features: List[str]


@dataclass
class MobileMatchingRequest:
    """Mobile creator matching request"""
    request_id: str
    seeker_profile: CreatorProfile
    project_requirements: Dict[str, Any]
    mobile_config: MobileMatchingConfiguration
    
    def __post_init__(self):
        if not self.request_id:
            self.request_id = str(uuid.uuid4())


@dataclass
class MobileMatchingResult:
    """Mobile creator matching result"""
    request_id: str
    success: bool
    processing_time_ms: int
    matches: List[MatchResult]
    matching_insights: Dict[str, Any]
    mobile_optimizations: List[str]
    analytics_data: Dict[str, Any]
    error_message: Optional[str] = None


class MobileCreatorMatching:
    """Mobile Creator Matching Engine
    
    Advanced mobile creator matching system using AI algorithms for intelligent
    creator compatibility analysis and collaboration recommendations.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Matching engines - placeholders for future integration
        self.ai_matcher = None          # AICompatibilityMatcher()
        self.skill_analyzer = None      # SkillAnalyzer()
        self.interest_matcher = None    # InterestMatcher()
        self.geo_matcher = None         # GeographicMatcher()
        
        # Creator database (simulated)
        self.creator_database = self._initialize_creator_database()
        
        # Performance tracking
        self.matching_metrics = {
            "total_requests": 0,
            "successful_matches": 0,
            "average_compatibility": 0.0,
            "average_processing_time": 0.0
        }
        
        self.logger.info("Mobile Creator Matching Engine initialized")
    
    def _initialize_creator_database(self) -> List[CreatorProfile]:
        """Initialize a sample creator database."""
        return [
            CreatorProfile(
                creator_id="creator_001",
                creator_type="musician",
                skills=["guitar", "songwriting", "audio_production"],
                interests=["rock", "indie", "mobile_recording"],
                experience_level="intermediate",
                availability={"hours_per_week": 20, "flexible": True},
                location="New York",
                mobile_preferences={"prefers_mobile_collaboration": True, "mobile_studio": True}
            ),
            CreatorProfile(
                creator_id="creator_002",
                creator_type="photographer",
                skills=["portrait", "mobile_photography", "editing"],
                interests=["travel", "lifestyle", "mobile_art"],
                experience_level="advanced",
                availability={"hours_per_week": 15, "flexible": False},
                location="Los Angeles",
                mobile_preferences={"mobile_editing": True, "instagram_focused": True}
            ),
            CreatorProfile(
                creator_id="creator_003",
                creator_type="blogger",
                skills=["writing", "seo", "mobile_content"],
                interests=["technology", "mobile_apps", "reviews"],
                experience_level="expert",
                availability={"hours_per_week": 25, "flexible": True},
                location="San Francisco",
                mobile_preferences={"mobile_first_content": True, "responsive_design": True}
            ),
            CreatorProfile(
                creator_id="creator_004",
                creator_type="influencer",
                skills=["social_media", "mobile_marketing", "content_creation"],
                interests=["lifestyle", "fashion", "mobile_trends"],
                experience_level="advanced",
                availability={"hours_per_week": 30, "flexible": True},
                location="Miami",
                mobile_preferences={"mobile_native": True, "stories_expert": True}
            ),
            CreatorProfile(
                creator_id="creator_005",
                creator_type="comedian",
                skills=["standup", "mobile_video", "editing"],
                interests=["humor", "mobile_comedy", "viral_content"],
                experience_level="intermediate",
                availability={"hours_per_week": 18, "flexible": True},
                location="Chicago",
                mobile_preferences={"vertical_video": True, "tiktok_specialist": True}
            )
        ]
    
    async def find_matches(self, request: MobileMatchingRequest) -> MobileMatchingResult:
        """
        Main entry point for mobile creator matching.
        
        Args:
            request: Mobile creator matching request
            
        Returns:
            MobileMatchingResult: Creator matching results
        """
        start_time = time.time()
        self.matching_metrics["total_requests"] += 1
        
        self.logger.info(f"Starting mobile creator matching for {request.seeker_profile.creator_id}")
        
        try:
            # Initialize result
            result = MobileMatchingResult(
                request_id=request.request_id,
                success=False,
                processing_time_ms=0,
                matches=[],
                matching_insights={},
                mobile_optimizations=[],
                analytics_data={}
            )
            
            # Core matching pipeline
            potential_matches = await self._find_potential_matches(request, result)
            await self._calculate_compatibility_scores(request, potential_matches, result)
            await self._rank_and_filter_matches(request, result)
            await self._generate_matching_insights(request, result)
            await self._apply_mobile_optimizations(request, result)
            await self._generate_matching_analytics(request, result)
            
            result.success = len(result.matches) > 0
            
            if result.success:
                self.matching_metrics["successful_matches"] += 1
            
            processing_time = (time.time() - start_time) * 1000
            result.processing_time_ms = int(processing_time)
            
            self.logger.info(f"Mobile creator matching completed for {request.seeker_profile.creator_id} in {processing_time:.2f}ms")
            return result
            
        except Exception as e:
            self.logger.error(f"Mobile creator matching failed: {str(e)}")
            return MobileMatchingResult(
                request_id=request.request_id,
                success=False,
                processing_time_ms=int((time.time() - start_time) * 1000),
                matches=[],
                matching_insights={},
                mobile_optimizations=[],
                analytics_data={},
                error_message=str(e)
            )
    
    async def _find_potential_matches(self, request: MobileMatchingRequest, result: MobileMatchingResult) -> List[CreatorProfile]:
        """Find potential creator matches."""
        potential_matches = []
        
        for creator in self.creator_database:
            # Exclude self
            if creator.creator_id == request.seeker_profile.creator_id:
                continue
            
            # Apply basic filters
            if await self._passes_basic_filters(creator, request):
                potential_matches.append(creator)
        
        self.logger.debug(f"Found {len(potential_matches)} potential matches")
        return potential_matches
    
    async def _passes_basic_filters(self, creator: CreatorProfile, request: MobileMatchingRequest) -> bool:
        """Check if creator passes basic filters."""
        # Geographic filter
        if request.mobile_config.geographic_radius_km:
            # Simplified geographic check (would use real geolocation in production)
            if creator.location and request.seeker_profile.location:
                if creator.location != request.seeker_profile.location:
                    return False
        
        # Mobile preference filter
        if request.mobile_config.mobile_optimization:
            if not creator.mobile_preferences.get("prefers_mobile_collaboration", False):
                # Still allow but with lower priority
                pass
        
        return True
    
    async def _calculate_compatibility_scores(self, request: MobileMatchingRequest, potential_matches: List[CreatorProfile], result: MobileMatchingResult):
        """Calculate compatibility scores for potential matches."""
        matches = []
        
        for creator in potential_matches:
            compatibility_score = await self._calculate_individual_compatibility(
                request.seeker_profile, creator, request
            )
            
            if compatibility_score >= request.mobile_config.min_compatibility_score:
                match_result = await self._create_match_result(creator, compatibility_score, request)
                matches.append(match_result)
        
        result.matches = matches
        self.logger.debug(f"Calculated compatibility for {len(matches)} matches")
    
    async def _calculate_individual_compatibility(self, seeker: CreatorProfile, candidate: CreatorProfile, request: MobileMatchingRequest) -> float:
        """Calculate compatibility score between two creators."""
        scores = {}
        
        # Skill compatibility
        skill_score = await self._calculate_skill_compatibility(seeker, candidate)
        scores["skill"] = skill_score * request.mobile_config.skill_weight
        
        # Interest compatibility
        interest_score = await self._calculate_interest_compatibility(seeker, candidate)
        scores["interest"] = interest_score * request.mobile_config.interest_weight
        
        # Availability compatibility
        availability_score = await self._calculate_availability_compatibility(seeker, candidate)
        scores["availability"] = availability_score * request.mobile_config.availability_weight
        
        # Mobile compatibility bonus
        mobile_score = await self._calculate_mobile_compatibility(seeker, candidate)
        scores["mobile"] = mobile_score * 0.1  # 10% bonus for mobile compatibility
        
        total_score = sum(scores.values())
        return min(total_score, 1.0)
    
    async def _calculate_skill_compatibility(self, seeker: CreatorProfile, candidate: CreatorProfile) -> float:
        """Calculate skill compatibility between creators."""
        seeker_skills = set(seeker.skills)
        candidate_skills = set(candidate.skills)
        
        # Complementary skills are better than overlapping
        complementary_skills = candidate_skills - seeker_skills
        overlapping_skills = seeker_skills & candidate_skills
        
        # Score based on complementary skills (higher) and some overlap (for communication)
        complementary_score = len(complementary_skills) / max(len(candidate_skills), 1)
        overlap_score = len(overlapping_skills) / max(len(seeker_skills), 1)
        
        # Weighted combination favoring complementary skills
        return complementary_score * 0.7 + overlap_score * 0.3
    
    async def _calculate_interest_compatibility(self, seeker: CreatorProfile, candidate: CreatorProfile) -> float:
        """Calculate interest compatibility between creators."""
        seeker_interests = set(seeker.interests)
        candidate_interests = set(candidate.interests)
        
        # Common interests are important for collaboration
        common_interests = seeker_interests & candidate_interests
        total_interests = seeker_interests | candidate_interests
        
        if not total_interests:
            return 0.5  # Neutral score if no interests specified
        
        return len(common_interests) / len(total_interests)
    
    async def _calculate_availability_compatibility(self, seeker: CreatorProfile, candidate: CreatorProfile) -> float:
        """Calculate availability compatibility between creators."""
        seeker_hours = seeker.availability.get("hours_per_week", 20)
        candidate_hours = candidate.availability.get("hours_per_week", 20)
        
        seeker_flexible = seeker.availability.get("flexible", True)
        candidate_flexible = candidate.availability.get("flexible", True)
        
        # Hours compatibility (closer is better)
        hours_diff = abs(seeker_hours - candidate_hours)
        hours_score = max(0, 1 - hours_diff / 40)  # Normalize to 40 hours max difference
        
        # Flexibility bonus
        flexibility_bonus = 0.2 if (seeker_flexible and candidate_flexible) else 0.1 if (seeker_flexible or candidate_flexible) else 0
        
        return min(hours_score + flexibility_bonus, 1.0)
    
    async def _calculate_mobile_compatibility(self, seeker: CreatorProfile, candidate: CreatorProfile) -> float:
        """Calculate mobile-specific compatibility."""
        seeker_mobile = seeker.mobile_preferences or {}
        candidate_mobile = candidate.mobile_preferences or {}
        
        mobile_factors = [
            "prefers_mobile_collaboration",
            "mobile_studio",
            "mobile_editing",
            "mobile_first_content",
            "mobile_native"
        ]
        
        compatibility_count = 0
        total_factors = 0
        
        for factor in mobile_factors:
            seeker_has = seeker_mobile.get(factor, False)
            candidate_has = candidate_mobile.get(factor, False)
            
            if seeker_has or candidate_has:
                total_factors += 1
                if seeker_has and candidate_has:
                    compatibility_count += 1
                elif seeker_has or candidate_has:
                    compatibility_count += 0.5  # Partial compatibility
        
        return compatibility_count / max(total_factors, 1)
    
    async def _create_match_result(self, creator: CreatorProfile, compatibility_score: float, request: MobileMatchingRequest) -> MatchResult:
        """Create a match result object."""
        # Determine compatibility level
        if compatibility_score >= 0.9:
            compatibility_level = CompatibilityLevel.EXCELLENT
        elif compatibility_score >= 0.8:
            compatibility_level = CompatibilityLevel.VERY_GOOD
        elif compatibility_score >= 0.7:
            compatibility_level = CompatibilityLevel.GOOD
        elif compatibility_score >= 0.6:
            compatibility_level = CompatibilityLevel.FAIR
        else:
            compatibility_level = CompatibilityLevel.POOR
        
        # Calculate individual matching factors
        matching_factors = {
            "skill_compatibility": await self._calculate_skill_compatibility(request.seeker_profile, creator),
            "interest_compatibility": await self._calculate_interest_compatibility(request.seeker_profile, creator),
            "availability_compatibility": await self._calculate_availability_compatibility(request.seeker_profile, creator),
            "mobile_compatibility": await self._calculate_mobile_compatibility(request.seeker_profile, creator)
        }
        
        # Determine collaboration potential
        if compatibility_score >= 0.8:
            collaboration_potential = "high"
        elif compatibility_score >= 0.7:
            collaboration_potential = "medium"
        else:
            collaboration_potential = "low"
        
        # Recommend project types
        recommended_projects = await self._recommend_project_types(request.seeker_profile, creator)
        
        # Mobile collaboration features
        mobile_features = await self._recommend_mobile_features(request.seeker_profile, creator)
        
        return MatchResult(
            creator_profile=creator,
            compatibility_score=compatibility_score,
            compatibility_level=compatibility_level,
            matching_factors=matching_factors,
            collaboration_potential=collaboration_potential,
            recommended_project_types=recommended_projects,
            mobile_collaboration_features=mobile_features
        )
    
    async def _recommend_project_types(self, seeker: CreatorProfile, candidate: CreatorProfile) -> List[str]:
        """Recommend project types for creator collaboration."""
        seeker_type = seeker.creator_type
        candidate_type = candidate.creator_type
        
        # Project type recommendations based on creator type combinations
        project_combinations = {
            ("musician", "photographer"): ["music_videos", "album_covers", "live_performance_documentation"],
            ("musician", "blogger"): ["music_reviews", "artist_interviews", "behind_scenes_content"],
            ("photographer", "blogger"): ["photo_essays", "travel_blogs", "product_reviews"],
            ("influencer", "photographer"): ["lifestyle_content", "brand_campaigns", "social_media_content"],
            ("comedian", "musician"): ["comedy_songs", "musical_comedy", "entertainment_content"],
            ("influencer", "blogger"): ["sponsored_content", "lifestyle_blogs", "social_campaigns"]
        }
        
        # Check both directions
        key1 = (seeker_type, candidate_type)
        key2 = (candidate_type, seeker_type)
        
        if key1 in project_combinations:
            return project_combinations[key1]
        elif key2 in project_combinations:
            return project_combinations[key2]
        else:
            return ["creative_collaboration", "content_creation", "cross_platform_project"]
    
    async def _recommend_mobile_features(self, seeker: CreatorProfile, candidate: CreatorProfile) -> List[str]:
        """Recommend mobile collaboration features."""
        features = ["mobile_messaging", "real_time_sync"]
        
        # Add features based on creator preferences
        seeker_mobile = seeker.mobile_preferences or {}
        candidate_mobile = candidate.mobile_preferences or {}
        
        if seeker_mobile.get("mobile_studio") or candidate_mobile.get("mobile_studio"):
            features.append("mobile_audio_collaboration")
        
        if seeker_mobile.get("mobile_editing") or candidate_mobile.get("mobile_editing"):
            features.append("collaborative_mobile_editing")
        
        if seeker_mobile.get("mobile_first_content") or candidate_mobile.get("mobile_first_content"):
            features.append("mobile_content_optimization")
        
        if seeker_mobile.get("vertical_video") or candidate_mobile.get("vertical_video"):
            features.append("vertical_video_collaboration")
        
        return features
    
    async def _rank_and_filter_matches(self, request: MobileMatchingRequest, result: MobileMatchingResult):
        """Rank matches by compatibility score and apply filters."""
        # Sort by compatibility score (descending)
        result.matches.sort(key=lambda x: x.compatibility_score, reverse=True)
        
        # Limit to max matches
        if len(result.matches) > request.mobile_config.max_matches:
            result.matches = result.matches[:request.mobile_config.max_matches]
        
        # Update average compatibility metric
        if result.matches:
            avg_compatibility = sum(match.compatibility_score for match in result.matches) / len(result.matches)
            self.matching_metrics["average_compatibility"] = (
                (self.matching_metrics["average_compatibility"] * (self.matching_metrics["total_requests"] - 1) + 
                 avg_compatibility) / self.matching_metrics["total_requests"]
            )
        
        self.logger.debug(f"Ranked and filtered to {len(result.matches)} final matches")
    
    async def _generate_matching_insights(self, request: MobileMatchingRequest, result: MobileMatchingResult):
        """Generate insights about the matching process."""
        if not result.matches:
            result.matching_insights = {"message": "No compatible creators found"}
            return
        
        # Analyze match distribution
        compatibility_levels = {}
        for match in result.matches:
            level = match.compatibility_level.value
            compatibility_levels[level] = compatibility_levels.get(level, 0) + 1
        
        # Analyze common factors
        strong_factors = []
        weak_factors = []
        
        for match in result.matches:
            for factor, score in match.matching_factors.items():
                if score > 0.8:
                    strong_factors.append(factor)
                elif score < 0.5:
                    weak_factors.append(factor)
        
        # Count factor frequency
        factor_strength = {}
        for factor in strong_factors:
            factor_strength[factor] = factor_strength.get(factor, 0) + 1
        
        result.matching_insights = {
            "total_matches": len(result.matches),
            "compatibility_distribution": compatibility_levels,
            "strongest_matching_factors": factor_strength,
            "average_compatibility": sum(m.compatibility_score for m in result.matches) / len(result.matches),
            "mobile_optimized_matches": sum(1 for m in result.matches if "mobile" in m.mobile_collaboration_features),
            "collaboration_potential_breakdown": {
                "high": sum(1 for m in result.matches if m.collaboration_potential == "high"),
                "medium": sum(1 for m in result.matches if m.collaboration_potential == "medium"),
                "low": sum(1 for m in result.matches if m.collaboration_potential == "low")
            }
        }
    
    async def _apply_mobile_optimizations(self, request: MobileMatchingRequest, result: MobileMatchingResult):
        """Apply mobile-specific optimizations."""
        mobile_optimizations = [
            "battery_efficient_matching_algorithms",
            "compressed_profile_data",
            "mobile_ui_optimized_results",
            "touch_friendly_interface",
            "offline_matching_cache",
            "real_time_availability_sync",
            "mobile_notification_integration",
            "gesture_based_navigation"
        ]
        
        result.mobile_optimizations = mobile_optimizations
    
    async def _generate_matching_analytics(self, request: MobileMatchingRequest, result: MobileMatchingResult):
        """Generate analytics data for matching."""
        analytics = {
            "matching_id": result.request_id,
            "seeker_id": request.seeker_profile.creator_id,
            "seeker_type": request.seeker_profile.creator_type,
            "matches_found": len(result.matches),
            "strategies_used": [strategy.value for strategy in request.mobile_config.matching_strategies],
            "mobile_optimizations_count": len(result.mobile_optimizations),
            "average_compatibility": result.matching_insights.get("average_compatibility", 0),
            "processing_time_ms": result.processing_time_ms,
            "mobile_specific_data": {
                "mobile_optimization_enabled": request.mobile_config.mobile_optimization,
                "geographic_filtering": request.mobile_config.geographic_radius_km is not None,
                "min_compatibility_threshold": request.mobile_config.min_compatibility_score
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
        result.analytics_data = analytics


# Factory function for creating mobile creator matching engine
def create_mobile_creator_matching(config: Optional[Dict[str, Any]] = None) -> MobileCreatorMatching:
    """
    Factory function to create a mobile creator matching engine.
    
    Args:
        config: Optional configuration dictionary
        
    Returns:
        MobileCreatorMatching: Configured mobile creator matching engine
    """
    return MobileCreatorMatching(config)


# Export key classes and functions
__all__ = [
    "MobileCreatorMatching",
    "MobileMatchingRequest", 
    "MobileMatchingResult",
    "MatchResult",
    "CreatorProfile",
    "MobileMatchingConfiguration",
    "MatchingStrategy",
    "CompatibilityLevel",
    "create_mobile_creator_matching"
]