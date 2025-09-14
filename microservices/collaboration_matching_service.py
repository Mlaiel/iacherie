"""
Collaboration Matching Service module
Enterprise implementation for Ainflue platform
"""

#!/usr/bin/env python3
"""
Enterprise Collaboration Matching Service
AI-powered creator matching and compatibility for microservices architecture

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ STRICT COPYRIGHT WARNING ⚠️
This implementation is proprietary and confidential. Unauthorized use, reproduction,
distribution, or modification without written permission from Fahed Mlaiel
(mlaiel@live.de) is strictly prohibited and will be prosecuted to the full extent
of the law. All rights reserved.
"""

import asyncio
import time
import logging
import json
import math
from typing import Dict, Any, Optional, List, Callable, Awaitable, Set, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import threading
from datetime import datetime, timedelta
from collections import defaultdict
import numpy as np

logger = logging.getLogger(__name__)

class CollaborationType(Enum):
    """Collaboration type enumeration"""
    CONTENT_CREATION = "content_creation"
    SKILL_EXCHANGE = "skill_exchange"
    AUDIENCE_SHARING = "audience_sharing"
    CROSS_PROMOTION = "cross_promotion"
    JOINT_PROJECT = "joint_project"
    MENTORSHIP = "mentorship"
    PARTNERSHIP = "partnership"
    SPONSORSHIP = "sponsorship"

class CompatibilityFactor(Enum):
    """Compatibility factor enumeration"""
    SKILL_COMPLEMENT = "skill_complement"
    AUDIENCE_OVERLAP = "audience_overlap"
    BRAND_ALIGNMENT = "brand_alignment"
    SCHEDULE_COMPATIBILITY = "schedule_compatibility"
    COMMUNICATION_STYLE = "communication_style"
    GOALS_ALIGNMENT = "goals_alignment"
    EXPERIENCE_LEVEL = "experience_level"
    GEOGRAPHIC_PROXIMITY = "geographic_proximity"

class CollaborationStatus(Enum):
    """Collaboration status enumeration"""
    PROPOSED = "proposed"
    PENDING = "pending"
    ACCEPTED = "accepted"
    ACTIVE = "active"
    COMPLETED = "completed"
    DECLINED = "declined"
    CANCELLED = "cancelled"

@dataclass
class CreatorProfile:
    """Creator profile for collaboration matching"""
    creator_id: str
    name: str
    skills: List[str] = field(default_factory=list)
    expertise_level: Dict[str, float] = field(default_factory=dict)  # skill -> proficiency (0-1)
    interests: List[str] = field(default_factory=list)
    collaboration_preferences: List[CollaborationType] = field(default_factory=list)
    availability: Dict[str, List[str]] = field(default_factory=dict)  # day -> time_slots
    location: str = "unknown"
    timezone: str = "UTC"
    language_preferences: List[str] = field(default_factory=list)
    communication_style: str = "flexible"  # formal, casual, flexible
    target_audience: Dict[str, Any] = field(default_factory=dict)
    brand_values: List[str] = field(default_factory=list)
    collaboration_history: List[str] = field(default_factory=list)
    success_metrics: Dict[str, float] = field(default_factory=dict)
    goals: List[str] = field(default_factory=list)
    budget_range: Dict[str, float] = field(default_factory=dict)  # min/max
    portfolio_urls: List[str] = field(default_factory=list)
    social_media_stats: Dict[str, int] = field(default_factory=dict)
    last_active: float = field(default_factory=time.time)

@dataclass
class CollaborationRequest:
    """Collaboration request details"""
    request_id: str
    requester_id: str
    collaboration_type: CollaborationType
    description: str
    required_skills: List[str] = field(default_factory=list)
    preferred_skills: List[str] = field(default_factory=list)
    target_audience_size: Optional[int] = None
    budget_range: Dict[str, float] = field(default_factory=dict)
    timeline: Dict[str, str] = field(default_factory=dict)  # start_date, end_date
    deliverables: List[str] = field(default_factory=list)
    location_preference: str = "remote"
    language_requirement: str = "en"
    experience_level: str = "any"  # beginner, intermediate, advanced, expert, any
    brand_alignment_required: bool = True
    max_candidates: int = 10
    filters: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)

@dataclass
class CompatibilityScore:
    """Compatibility score breakdown"""
    total_score: float
    factor_scores: Dict[CompatibilityFactor, float] = field(default_factory=dict)
    explanation: str = ""
    strengths: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)

@dataclass
class CollaborationMatch:
    """Collaboration match result"""
    match_id: str
    creator1_id: str
    creator2_id: str
    collaboration_type: CollaborationType
    compatibility_score: CompatibilityScore
    suggested_terms: Dict[str, Any] = field(default_factory=dict)
    success_probability: float = 0.0
    risk_factors: List[str] = field(default_factory=list)
    recommended_next_steps: List[str] = field(default_factory=list)
    match_timestamp: float = field(default_factory=time.time)

@dataclass
class CollaborationProposal:
    """Collaboration proposal"""
    proposal_id: str
    match_id: str
    proposer_id: str
    recipient_id: str
    collaboration_type: CollaborationType
    proposal_details: Dict[str, Any] = field(default_factory=dict)
    terms: Dict[str, Any] = field(default_factory=dict)
    timeline: Dict[str, str] = field(default_factory=dict)
    status: CollaborationStatus = CollaborationStatus.PROPOSED
    response_deadline: Optional[float] = None
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)

class CollaborationMatchingService:
    """
    Enterprise Collaboration Matching Service
    
    Provides AI-powered creator matching and compatibility analysis with:
    - Multi-dimensional compatibility scoring
    - Smart matching algorithms
    - Collaboration proposal management
    - Success prediction modeling
    - Risk assessment
    - Performance tracking
    """
    
    def __init__(self) -> None:
        """Initialize collaboration matching service"""
        # Creator database
        self.creator_profiles: Dict[str, CreatorProfile] = {}
        
        # Matching data
        self.compatibility_cache: Dict[str, CompatibilityScore] = {}
        self.collaboration_matches: Dict[str, CollaborationMatch] = {}
        self.collaboration_proposals: Dict[str, CollaborationProposal] = {}
        self.collaboration_history: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        
        # Machine learning models (simplified for demo)
        self.compatibility_weights: Dict[CompatibilityFactor, float] = {
            CompatibilityFactor.SKILL_COMPLEMENT: 0.25,
            CompatibilityFactor.AUDIENCE_OVERLAP: 0.20,
            CompatibilityFactor.BRAND_ALIGNMENT: 0.15,
            CompatibilityFactor.SCHEDULE_COMPATIBILITY: 0.10,
            CompatibilityFactor.COMMUNICATION_STYLE: 0.10,
            CompatibilityFactor.GOALS_ALIGNMENT: 0.10,
            CompatibilityFactor.EXPERIENCE_LEVEL: 0.05,
            CompatibilityFactor.GEOGRAPHIC_PROXIMITY: 0.05
        }
        
        # Performance tracking
        self.matching_stats = {
            "total_matches": 0,
            "successful_collaborations": 0,
            "avg_compatibility_score": 0.0,
            "avg_success_rate": 0.0,
            "popular_collaboration_types": defaultdict(int),
            "avg_matching_time": 0.0
        }
        
        # Configuration
        self.config = {
            "min_compatibility_score": 0.6,
            "max_matches_per_request": 20,
            "cache_ttl": 3600.0,  # 1 hour
            "auto_proposal_threshold": 0.85,
            "success_prediction_enabled": True,
            "risk_assessment_enabled": True,
            "learning_enabled": True,
            "notification_enabled": True
        }
        
        self.shutdown_event = asyncio.Event()
        self._lock = asyncio.Lock()
        
        # Background tasks
        self.optimization_task: Optional[asyncio.Task] = None
        
        logger.info("CollaborationMatchingService initialized")
    
    async def start(self) -> None:
        """Start the collaboration matching service"""
        try:
            # Start background optimization task
            self.optimization_task = asyncio.create_task(self._optimization_loop())
            
            logger.info("CollaborationMatchingService started successfully")
        except Exception as e:
            logger.error("Failed to start CollaborationMatchingService: %s", e)
            raise
    
    async def stop(self) -> None:
        """Stop the collaboration matching service"""
        try:
            self.shutdown_event.set()
            
            # Stop background task
            if self.optimization_task:
                self.optimization_task.cancel()
                try:
                    await self.optimization_task
                except asyncio.CancelledError:
                    pass
            
            logger.info("CollaborationMatchingService stopped successfully")
        except Exception as e:
            logger.error("Error stopping CollaborationMatchingService: %s", e)
    
    async def register_creator(self, profile -> None: CreatorProfile) -> None:
        """Register or update a creator profile"""
        async with self._lock:
            self.creator_profiles[profile.creator_id] = profile
            
            # Clear compatibility cache for this creator
            cache_keys_to_remove = [
                key for key in self.compatibility_cache.keys()
                if profile.creator_id in key
            ]
            for key in cache_keys_to_remove:
                del self.compatibility_cache[key]
        
        logger.info("Registered creator profile: %s", profile.creator_id)
    
    async def find_matches(self, request: CollaborationRequest) -> List[CollaborationMatch]:
        """Find collaboration matches for a request"""
        start_time = time.time()
        
        async with self._lock:
            requester_profile = self.creator_profiles.get(request.requester_id)
            if not requester_profile:
                raise ValueError(f"Requester profile not found: {request.requester_id}")
            
            # Get candidate creators
            candidates = await self._get_candidates(request, requester_profile)
            
            # Calculate compatibility scores
            matches = []
            for candidate in candidates:
                try:
                    compatibility = await self._calculate_compatibility(
                        requester_profile, candidate, request.collaboration_type
                    )
                    
                    if compatibility.total_score >= self.config["min_compatibility_score"]:
                        # Create match
                        match = await self._create_match(
                            requester_profile, candidate, request, compatibility
                        )
                        matches.append(match)
                        
                except Exception as e:
                    logger.warning("Failed to calculate compatibility for %s: %s", candidate.creator_id, e)
            
            # Sort by compatibility score
            matches.sort(key=lambda m: m.compatibility_score.total_score, reverse=True)
            
            # Limit results
            matches = matches[:request.max_candidates]
            
            # Store matches
            for match in matches:
                self.collaboration_matches[match.match_id] = match
            
            # Update statistics
            processing_time = time.time() - start_time
            await self._update_matching_stats(matches, processing_time)
            
            # Auto-propose for high-compatibility matches
            if self.config["auto_proposal_threshold"]:
                await self._handle_auto_proposals(matches, request)
        
        logger.info("Found %d matches for request %s", len(matches), request.request_id)
        return matches
    
    async def calculate_compatibility(
        self,
        creator1_id: str,
        creator2_id: str,
        collaboration_type: CollaborationType
    ) -> CompatibilityScore:
        """Calculate compatibility between two creators"""
        async with self._lock:
            profile1 = self.creator_profiles.get(creator1_id)
            profile2 = self.creator_profiles.get(creator2_id)
            
            if not profile1 or not profile2:
                raise ValueError("One or both creator profiles not found")
            
            # Check cache
            cache_key = f"{creator1_id}_{creator2_id}_{collaboration_type.value}"
            if cache_key in self.compatibility_cache:
                cached_score = self.compatibility_cache[cache_key]
                if time.time() - cached_score.factor_scores.get("timestamp", 0) < self.config["cache_ttl"]:
                    return cached_score
            
            # Calculate compatibility
            compatibility = await self._calculate_compatibility(profile1, profile2, collaboration_type)
            
            # Cache result
            compatibility.factor_scores["timestamp"] = time.time()
            self.compatibility_cache[cache_key] = compatibility
            
            return compatibility
    
    async def create_proposal(
        self,
        match_id: str,
        proposer_id: str,
        proposal_details: Dict[str, Any],
        terms: Dict[str, Any],
        timeline: Dict[str, str]
    ) -> str:
        """Create a collaboration proposal"""
        async with self._lock:
            match = self.collaboration_matches.get(match_id)
            if not match:
                raise ValueError(f"Match not found: {match_id}")
            
            # Determine recipient
            recipient_id = (match.creator2_id if match.creator1_id == proposer_id 
                          else match.creator1_id)
            
            if recipient_id == proposer_id:
                raise ValueError("Cannot propose to yourself")
            
            # Create proposal
            proposal_id = f"prop_{int(time.time())}_{proposer_id[:8]}"
            
            proposal = CollaborationProposal(
                proposal_id=proposal_id,
                match_id=match_id,
                proposer_id=proposer_id,
                recipient_id=recipient_id,
                collaboration_type=match.collaboration_type,
                proposal_details=proposal_details,
                terms=terms,
                timeline=timeline,
                response_deadline=time.time() + (7 * 24 * 3600)  # 7 days
            )
            
            self.collaboration_proposals[proposal_id] = proposal
        
        logger.info("Created collaboration proposal: %s", proposal_id)
        return proposal_id
    
    async def respond_to_proposal(
        self,
        proposal_id: str,
        responder_id: str,
        response: str,  # accept, decline, counter
        counter_terms: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Respond to a collaboration proposal"""
        async with self._lock:
            proposal = self.collaboration_proposals.get(proposal_id)
            if not proposal:
                raise ValueError(f"Proposal not found: {proposal_id}")
            
            if proposal.recipient_id != responder_id:
                raise ValueError("Only the recipient can respond to this proposal")
            
            if proposal.status != CollaborationStatus.PROPOSED:
                raise ValueError(f"Proposal already responded to: {proposal.status}")
            
            # Update proposal status
            if response == "accept":
                proposal.status = CollaborationStatus.ACCEPTED
                # Record successful collaboration
                await self._record_collaboration_start(proposal)
                
            elif response == "decline":
                proposal.status = CollaborationStatus.DECLINED
                
            elif response == "counter" and counter_terms:
                # Create counter-proposal (simplified)
                proposal.terms.update(counter_terms)
                proposal.status = CollaborationStatus.PENDING
                
            else:
                raise ValueError(f"Invalid response: {response}")
            
            proposal.updated_at = time.time()
        
        logger.info("Proposal %s response: %s", proposal_id, response)
        return True
    
    async def get_collaboration_suggestions(
        self,
        creator_id: str,
        collaboration_type: Optional[CollaborationType] = None,
        max_suggestions: int = 10
    ) -> List[CollaborationMatch]:
        """Get proactive collaboration suggestions for a creator"""
        async with self._lock:
            creator_profile = self.creator_profiles.get(creator_id)
            if not creator_profile:
                raise ValueError(f"Creator profile not found: {creator_id}")
            
            suggestions = []
            
            # Create a mock request for suggestions
            request = CollaborationRequest(
                request_id=f"suggestion_{creator_id}_{int(time.time())}",
                requester_id=creator_id,
                collaboration_type=collaboration_type or CollaborationType.CONTENT_CREATION,
                description="Proactive collaboration suggestion",
                max_candidates=max_suggestions
            )
            
            # Get matches
            matches = await self.find_matches(request)
            
            # Filter for proactive suggestions (higher threshold)
            suggestions = [
                match for match in matches
                if match.compatibility_score.total_score >= 0.75
            ]
        
        return suggestions[:max_suggestions]
    
    async def get_creator_compatibility_matrix(
        self,
        creator_ids: List[str],
        collaboration_type: CollaborationType
    ) -> Dict[str, Dict[str, float]]:
        """Get compatibility matrix for a group of creators"""
        matrix = {}
        
        for i, creator1_id in enumerate(creator_ids):
            matrix[creator1_id] = {}
            
            for j, creator2_id in enumerate(creator_ids):
                if i == j:
                    matrix[creator1_id][creator2_id] = 1.0  # Self-compatibility
                elif creator2_id in matrix and creator1_id in matrix[creator2_id]:
                    # Use existing score (symmetric)
                    matrix[creator1_id][creator2_id] = matrix[creator2_id][creator1_id]
                else:
                    try:
                        compatibility = await self.calculate_compatibility(
                            creator1_id, creator2_id, collaboration_type
                        )
                        matrix[creator1_id][creator2_id] = compatibility.total_score
                    except Exception as e:
                        logger.warning("Failed to calculate compatibility between %s and %s: %s", 
                                     creator1_id, creator2_id, e)
                        matrix[creator1_id][creator2_id] = 0.0
        
        return matrix
    
    async def get_collaboration_analytics(
        self,
        creator_id: Optional[str] = None,
        time_period: str = "30d"
    ) -> Dict[str, Any]:
        """Get collaboration analytics"""
        async with self._lock:
            analytics = {
                "total_matches": len(self.collaboration_matches),
                "total_proposals": len(self.collaboration_proposals),
                "proposal_success_rate": 0.0,
                "avg_compatibility_score": 0.0,
                "collaboration_type_distribution": dict(self.matching_stats["popular_collaboration_types"]),
                "matching_stats": dict(self.matching_stats)
            }
            
            # Calculate proposal success rate
            if self.collaboration_proposals:
                successful_proposals = len([
                    p for p in self.collaboration_proposals.values()
                    if p.status == CollaborationStatus.ACCEPTED
                ])
                analytics["proposal_success_rate"] = successful_proposals / len(self.collaboration_proposals)
            
            # Calculate average compatibility score
            if self.collaboration_matches:
                total_score = sum(
                    match.compatibility_score.total_score 
                    for match in self.collaboration_matches.values()
                )
                analytics["avg_compatibility_score"] = total_score / len(self.collaboration_matches)
            
            # Creator-specific analytics
            if creator_id:
                creator_matches = [
                    match for match in self.collaboration_matches.values()
                    if creator_id in [match.creator1_id, match.creator2_id]
                ]
                
                creator_proposals = [
                    prop for prop in self.collaboration_proposals.values()
                    if creator_id in [prop.proposer_id, prop.recipient_id]
                ]
                
                analytics["creator_stats"] = {
                    "total_matches": len(creator_matches),
                    "total_proposals": len(creator_proposals),
                    "avg_compatibility": (
                        sum(m.compatibility_score.total_score for m in creator_matches) / 
                        len(creator_matches) if creator_matches else 0.0
                    ),
                    "collaboration_history": self.collaboration_history.get(creator_id, [])
                }
            
            return analytics
    
    async def _get_candidates(
        self,
        request: CollaborationRequest,
        requester_profile: CreatorProfile
    ) -> List[CreatorProfile]:
        """Get candidate creators for collaboration"""
        candidates = []
        
        for creator_id, profile in self.creator_profiles.items():
            # Skip requester
            if creator_id == request.requester_id:
                continue
            
            # Check basic filters
            if not await self._matches_basic_filters(profile, request):
                continue
            
            # Check collaboration preferences
            if (request.collaboration_type not in profile.collaboration_preferences and
                profile.collaboration_preferences):  # If preferences are set
                continue
            
            # Check skill requirements
            if request.required_skills:
                if not all(skill in profile.skills for skill in request.required_skills):
                    continue
            
            # Check experience level
            if request.experience_level != "any":
                if not await self._matches_experience_level(profile, request.experience_level):
                    continue
            
            # Check availability
            if not await self._check_availability_overlap(requester_profile, profile):
                continue
            
            candidates.append(profile)
        
        return candidates
    
    async def _matches_basic_filters(self, profile: CreatorProfile, request: CollaborationRequest) -> bool:
        """Check if profile matches basic filters"""
        filters = request.filters
        
        for key, value in filters.items():
            if key == "min_followers" and profile.social_media_stats.get("followers", 0) < value:
                return False
            elif key == "max_followers" and profile.social_media_stats.get("followers", 0) > value:
                return False
            elif key == "location" and profile.location != value:
                return False
            elif key == "languages" and not any(lang in profile.language_preferences for lang in value):
                return False
            elif key == "brand_values" and not any(val in profile.brand_values for val in value):
                return False
        
        return True
    
    async def _matches_experience_level(self, profile: CreatorProfile, required_level: str) -> bool:
        """Check if profile matches experience level requirement"""
        # Simplified experience level matching
        experience_mapping = {
            "beginner": (0.0, 0.3),
            "intermediate": (0.3, 0.7),
            "advanced": (0.7, 0.9),
            "expert": (0.9, 1.0)
        }
        
        if required_level not in experience_mapping:
            return True
        
        min_exp, max_exp = experience_mapping[required_level]
        
        # Calculate average expertise level
        if profile.expertise_level:
            avg_expertise = sum(profile.expertise_level.values()) / len(profile.expertise_level)
            return min_exp <= avg_expertise <= max_exp
        
        return True  # No expertise data available
    
    async def _check_availability_overlap(
        self,
        profile1: CreatorProfile,
        profile2: CreatorProfile
    ) -> bool:
        """Check if two creators have overlapping availability"""
        # Simplified availability check
        if not profile1.availability or not profile2.availability:
            return True  # Assume flexible if no availability data
        
        # Check for any overlapping days
        common_days = set(profile1.availability.keys()) & set(profile2.availability.keys())
        
        for day in common_days:
            slots1 = set(profile1.availability[day])
            slots2 = set(profile2.availability[day])
            
            if slots1 & slots2:  # Any overlapping time slots
                return True
        
        return len(common_days) > 0  # At least some common days
    
    async def _calculate_compatibility(
        self,
        profile1: CreatorProfile,
        profile2: CreatorProfile,
        collaboration_type: CollaborationType
    ) -> CompatibilityScore:
        """Calculate comprehensive compatibility score"""
        factor_scores = {}
        
        # Skill complementarity
        factor_scores[CompatibilityFactor.SKILL_COMPLEMENT] = await self._calculate_skill_complement(
            profile1, profile2
        )
        
        # Audience overlap
        factor_scores[CompatibilityFactor.AUDIENCE_OVERLAP] = await self._calculate_audience_overlap(
            profile1, profile2
        )
        
        # Brand alignment
        factor_scores[CompatibilityFactor.BRAND_ALIGNMENT] = await self._calculate_brand_alignment(
            profile1, profile2
        )
        
        # Schedule compatibility
        factor_scores[CompatibilityFactor.SCHEDULE_COMPATIBILITY] = await self._calculate_schedule_compatibility(
            profile1, profile2
        )
        
        # Communication style
        factor_scores[CompatibilityFactor.COMMUNICATION_STYLE] = await self._calculate_communication_compatibility(
            profile1, profile2
        )
        
        # Goals alignment
        factor_scores[CompatibilityFactor.GOALS_ALIGNMENT] = await self._calculate_goals_alignment(
            profile1, profile2
        )
        
        # Experience level compatibility
        factor_scores[CompatibilityFactor.EXPERIENCE_LEVEL] = await self._calculate_experience_compatibility(
            profile1, profile2
        )
        
        # Geographic proximity
        factor_scores[CompatibilityFactor.GEOGRAPHIC_PROXIMITY] = await self._calculate_geographic_proximity(
            profile1, profile2
        )
        
        # Calculate weighted total score
        total_score = sum(
            factor_scores[factor] * weight
            for factor, weight in self.compatibility_weights.items()
        )
        
        # Generate explanation
        explanation = await self._generate_compatibility_explanation(factor_scores, collaboration_type)
        
        # Identify strengths and weaknesses
        strengths = [
            factor.value for factor, score in factor_scores.items()
            if score >= 0.8
        ]
        
        weaknesses = [
            factor.value for factor, score in factor_scores.items()
            if score <= 0.4
        ]
        
        # Generate recommendations
        recommendations = await self._generate_compatibility_recommendations(
            factor_scores, profile1, profile2, collaboration_type
        )
        
        return CompatibilityScore(
            total_score=total_score,
            factor_scores=factor_scores,
            explanation=explanation,
            strengths=strengths,
            weaknesses=weaknesses,
            recommendations=recommendations
        )
    
    async def _calculate_skill_complement(self, profile1: CreatorProfile, profile2: CreatorProfile) -> float:
        """Calculate skill complementarity score"""
        skills1 = set(profile1.skills)
        skills2 = set(profile2.skills)
        
        # Skill overlap (some overlap is good, but not too much)
        overlap = len(skills1 & skills2)
        total_skills = len(skills1 | skills2)
        
        if total_skills == 0:
            return 0.5  # Neutral if no skills data
        
        overlap_ratio = overlap / total_skills
        
        # Optimal overlap is around 30-50%
        if 0.3 <= overlap_ratio <= 0.5:
            return 1.0
        elif overlap_ratio < 0.3:
            # Too little overlap
            return 0.6 + (overlap_ratio / 0.3) * 0.4
        else:
            # Too much overlap
            return 1.0 - ((overlap_ratio - 0.5) / 0.5) * 0.4
    
    async def _calculate_audience_overlap(self, profile1: CreatorProfile, profile2: CreatorProfile) -> float:
        """Calculate audience overlap score"""
        # Mock audience overlap calculation
        # In production, this would analyze actual audience data
        
        # Use follower counts as a proxy
        followers1 = profile1.social_media_stats.get("followers", 0)
        followers2 = profile2.social_media_stats.get("followers", 0)
        
        if followers1 == 0 or followers2 == 0:
            return 0.5  # Neutral if no data
        
        # Similarity in audience size
        ratio = min(followers1, followers2) / max(followers1, followers2)
        
        # Prefer similar or complementary audience sizes
        return ratio * 0.7 + 0.3
    
    async def _calculate_brand_alignment(self, profile1: CreatorProfile, profile2: CreatorProfile) -> float:
        """Calculate brand alignment score"""
        values1 = set(profile1.brand_values)
        values2 = set(profile2.brand_values)
        
        if not values1 or not values2:
            return 0.7  # Neutral if no brand values specified
        
        # Calculate overlap in brand values
        overlap = len(values1 & values2)
        total_unique = len(values1 | values2)
        
        if total_unique == 0:
            return 0.7
        
        return overlap / total_unique
    
    async def _calculate_schedule_compatibility(self, profile1: CreatorProfile, profile2: CreatorProfile) -> float:
        """Calculate schedule compatibility score"""
        if not profile1.availability or not profile2.availability:
            return 0.8  # Assume flexible if no schedule data
        
        total_overlap = 0
        total_slots = 0
        
        all_days = set(profile1.availability.keys()) | set(profile2.availability.keys())
        
        for day in all_days:
            slots1 = set(profile1.availability.get(day, []))
            slots2 = set(profile2.availability.get(day, []))
            
            if slots1 and slots2:
                overlap = len(slots1 & slots2)
                total = len(slots1 | slots2)
                
                total_overlap += overlap
                total_slots += total
        
        if total_slots == 0:
            return 0.5
        
        return total_overlap / total_slots
    
    async def _calculate_communication_compatibility(self, profile1: CreatorProfile, profile2: CreatorProfile) -> float:
        """Calculate communication style compatibility"""
        style1 = profile1.communication_style
        style2 = profile2.communication_style
        
        # Compatibility matrix for communication styles
        compatibility_matrix = {
            ("formal", "formal"): 1.0,
            ("formal", "flexible"): 0.8,
            ("formal", "casual"): 0.4,
            ("casual", "casual"): 1.0,
            ("casual", "flexible"): 0.8,
            ("casual", "formal"): 0.4,
            ("flexible", "flexible"): 0.9,
            ("flexible", "formal"): 0.8,
            ("flexible", "casual"): 0.8
        }
        
        return compatibility_matrix.get((style1, style2), 0.7)
    
    async def _calculate_goals_alignment(self, profile1: CreatorProfile, profile2: CreatorProfile) -> float:
        """Calculate goals alignment score"""
        goals1 = set(profile1.goals)
        goals2 = set(profile2.goals)
        
        if not goals1 or not goals2:
            return 0.6  # Neutral if no goals specified
        
        # Calculate overlap in goals
        overlap = len(goals1 & goals2)
        total_unique = len(goals1 | goals2)
        
        if total_unique == 0:
            return 0.6
        
        return overlap / total_unique
    
    async def _calculate_experience_compatibility(self, profile1: CreatorProfile, profile2: CreatorProfile) -> float:
        """Calculate experience level compatibility"""
        if not profile1.expertise_level or not profile2.expertise_level:
            return 0.7  # Neutral if no expertise data
        
        # Calculate average expertise levels
        avg_exp1 = sum(profile1.expertise_level.values()) / len(profile1.expertise_level)
        avg_exp2 = sum(profile2.expertise_level.values()) / len(profile2.expertise_level)
        
        # Prefer balanced but not identical experience levels
        diff = abs(avg_exp1 - avg_exp2)
        
        if diff <= 0.2:
            return 1.0  # Very similar levels
        elif diff <= 0.4:
            return 0.8  # Complementary levels
        else:
            return 0.5  # Very different levels
    
    async def _calculate_geographic_proximity(self, profile1: CreatorProfile, profile2: CreatorProfile) -> float:
        """Calculate geographic proximity score"""
        if profile1.location == "unknown" or profile2.location == "unknown":
            return 0.7  # Neutral if location unknown
        
        # Simplified geographic scoring
        if profile1.location == profile2.location:
            return 1.0  # Same location
        elif profile1.location.split(",")[-1].strip() == profile2.location.split(",")[-1].strip():
            return 0.8  # Same country/region
        else:
            return 0.4  # Different regions
    
    async def _generate_compatibility_explanation(
        self,
        factor_scores: Dict[CompatibilityFactor, float],
        collaboration_type: CollaborationType
    ) -> str:
        """Generate human-readable compatibility explanation"""
        top_factors = sorted(factor_scores.items(), key=lambda x: x[1], reverse=True)[:3]
        
        explanations = []
        for factor, score in top_factors:
            if score >= 0.8:
                explanations.append(f"Excellent {factor.value.replace('_', ' ')}")
            elif score >= 0.6:
                explanations.append(f"Good {factor.value.replace('_', ' ')}")
        
        base_explanation = f"Strong compatibility for {collaboration_type.value.replace('_', ' ')}"
        
        if explanations:
            return f"{base_explanation} due to: {', '.join(explanations)}"
        else:
            return base_explanation
    
    async def _generate_compatibility_recommendations(
        self,
        factor_scores: Dict[CompatibilityFactor, float],
        profile1: CreatorProfile,
        profile2: CreatorProfile,
        collaboration_type: CollaborationType
    ) -> List[str]:
        """Generate compatibility improvement recommendations"""
        recommendations = []
        
        # Check weak factors and suggest improvements
        for factor, score in factor_scores.items():
            if score <= 0.4:
                if factor == CompatibilityFactor.SCHEDULE_COMPATIBILITY:
                    recommendations.append("Consider using asynchronous collaboration methods")
                elif factor == CompatibilityFactor.COMMUNICATION_STYLE:
                    recommendations.append("Establish clear communication preferences early")
                elif factor == CompatibilityFactor.BRAND_ALIGNMENT:
                    recommendations.append("Discuss brand guidelines and shared values")
                elif factor == CompatibilityFactor.SKILL_COMPLEMENT:
                    recommendations.append("Focus on leveraging unique skill differences")
        
        # Add general recommendations
        if factor_scores[CompatibilityFactor.GOALS_ALIGNMENT] >= 0.8:
            recommendations.append("Strong goal alignment suggests long-term partnership potential")
        
        return recommendations[:5]  # Limit to top 5 recommendations
    
    async def _create_match(
        self,
        requester_profile: CreatorProfile,
        candidate_profile: CreatorProfile,
        request: CollaborationRequest,
        compatibility: CompatibilityScore
    ) -> CollaborationMatch:
        """Create a collaboration match"""
        match_id = f"match_{int(time.time())}_{requester_profile.creator_id[:8]}_{candidate_profile.creator_id[:8]}"
        
        # Calculate success probability
        success_probability = await self._calculate_success_probability(
            requester_profile, candidate_profile, request, compatibility
        )
        
        # Identify risk factors
        risk_factors = await self._identify_risk_factors(
            requester_profile, candidate_profile, compatibility
        )
        
        # Generate suggested terms
        suggested_terms = await self._generate_suggested_terms(
            requester_profile, candidate_profile, request
        )
        
        # Generate next steps
        next_steps = await self._generate_next_steps(request, compatibility)
        
        return CollaborationMatch(
            match_id=match_id,
            creator1_id=requester_profile.creator_id,
            creator2_id=candidate_profile.creator_id,
            collaboration_type=request.collaboration_type,
            compatibility_score=compatibility,
            suggested_terms=suggested_terms,
            success_probability=success_probability,
            risk_factors=risk_factors,
            recommended_next_steps=next_steps
        )
    
    async def _calculate_success_probability(
        self,
        profile1: CreatorProfile,
        profile2: CreatorProfile,
        request: CollaborationRequest,
        compatibility: CompatibilityScore
    ) -> float:
        """Calculate collaboration success probability"""
        if not self.config["success_prediction_enabled"]:
            return 0.5
        
        # Base probability from compatibility score
        base_prob = compatibility.total_score
        
        # Adjust based on collaboration history
        history_factor = 1.0
        if profile1.collaboration_history and profile2.collaboration_history:
            # Creators with collaboration experience have higher success rates
            history_factor = 1.1
        
        # Adjust based on brand alignment for certain collaboration types
        brand_factor = 1.0
        if request.collaboration_type in [CollaborationType.PARTNERSHIP, CollaborationType.SPONSORSHIP]:
            brand_score = compatibility.factor_scores.get(CompatibilityFactor.BRAND_ALIGNMENT, 0.5)
            brand_factor = 0.8 + (brand_score * 0.4)
        
        # Adjust based on communication compatibility
        comm_score = compatibility.factor_scores.get(CompatibilityFactor.COMMUNICATION_STYLE, 0.5)
        comm_factor = 0.9 + (comm_score * 0.2)
        
        probability = base_prob * history_factor * brand_factor * comm_factor
        return min(1.0, probability)
    
    async def _identify_risk_factors(
        self,
        profile1: CreatorProfile,
        profile2: CreatorProfile,
        compatibility: CompatibilityScore
    ) -> List[str]:
        """Identify potential risk factors"""
        if not self.config["risk_assessment_enabled"]:
            return []
        
        risk_factors = []
        
        # Check low compatibility factors
        for factor, score in compatibility.factor_scores.items():
            if score <= 0.3:
                if factor == CompatibilityFactor.COMMUNICATION_STYLE:
                    risk_factors.append("Potential communication conflicts")
                elif factor == CompatibilityFactor.SCHEDULE_COMPATIBILITY:
                    risk_factors.append("Limited schedule overlap")
                elif factor == CompatibilityFactor.BRAND_ALIGNMENT:
                    risk_factors.append("Brand value conflicts")
                elif factor == CompatibilityFactor.GOALS_ALIGNMENT:
                    risk_factors.append("Misaligned objectives")
        
        # Check experience level mismatches
        exp_score = compatibility.factor_scores.get(CompatibilityFactor.EXPERIENCE_LEVEL, 0.5)
        if exp_score <= 0.4:
            risk_factors.append("Significant experience level differences")
        
        # Check for first-time collaborators
        if not profile1.collaboration_history or not profile2.collaboration_history:
            risk_factors.append("Limited collaboration experience")
        
        return risk_factors
    
    async def _generate_suggested_terms(
        self,
        profile1: CreatorProfile,
        profile2: CreatorProfile,
        request: CollaborationRequest
    ) -> Dict[str, Any]:
        """Generate suggested collaboration terms"""
        terms = {
            "collaboration_type": request.collaboration_type.value,
            "duration": "4-6 weeks",
            "communication_frequency": "weekly",
            "deliverables": request.deliverables or ["joint content piece"],
            "responsibilities": {
                profile1.creator_id: "content strategy and creation",
                profile2.creator_id: "promotion and distribution"
            }
        }
        
        # Add budget suggestions if both have budget info
        if profile1.budget_range and profile2.budget_range:
            min_budget = max(profile1.budget_range.get("min", 0), profile2.budget_range.get("min", 0))
            max_budget = min(profile1.budget_range.get("max", 10000), profile2.budget_range.get("max", 10000))
            
            if min_budget <= max_budget:
                terms["suggested_budget_range"] = {"min": min_budget, "max": max_budget}
        
        return terms
    
    async def _generate_next_steps(
        self,
        request: CollaborationRequest,
        compatibility: CompatibilityScore
    ) -> List[str]:
        """Generate recommended next steps"""
        steps = []
        
        if compatibility.total_score >= 0.8:
            steps.append("Send collaboration proposal")
            steps.append("Schedule introductory video call")
        else:
            steps.append("Review compatibility factors")
            steps.append("Consider addressing potential concerns")
        
        steps.extend([
            "Share portfolio examples",
            "Discuss project timeline",
            "Establish communication preferences"
        ])
        
        return steps
    
    async def _handle_auto_proposals(self, matches -> None: List[CollaborationMatch], request -> None: CollaborationRequest) -> None:
        """Handle automatic proposal generation for high-compatibility matches"""
        threshold = self.config["auto_proposal_threshold"]
        if not threshold:
            return
        
        high_compatibility_matches = [
            match for match in matches
            if match.compatibility_score.total_score >= threshold
        ]
        
        for match in high_compatibility_matches[:3]:  # Limit to top 3
            try:
                # Auto-generate proposal
                await self.create_proposal(
                    match.match_id,
                    request.requester_id,
                    {
                        "message": f"Auto-generated proposal based on high compatibility score ({match.compatibility_score.total_score:.2f})",
                        "collaboration_type": request.collaboration_type.value,
                        "description": request.description
                    },
                    match.suggested_terms,
                    request.timeline
                )
                
                logger.info("Auto-generated proposal for high-compatibility match: %s", match.match_id)
                
            except Exception as e:
                logger.error("Failed to auto-generate proposal for match %s: %s", match.match_id, e)
    
    async def _update_matching_stats(self, matches -> None: List[CollaborationMatch], processing_time -> None: float) -> None:
        """Update matching statistics"""
        self.matching_stats["total_matches"] += len(matches)
        
        if matches:
            total_compatibility = sum(match.compatibility_score.total_score for match in matches)
            avg_compatibility = total_compatibility / len(matches)
            
            # Update running average
            current_avg = self.matching_stats["avg_compatibility_score"]
            total_count = self.matching_stats["total_matches"]
            
            if total_count == len(matches):  # First batch
                self.matching_stats["avg_compatibility_score"] = avg_compatibility
            else:
                self.matching_stats["avg_compatibility_score"] = (
                    (current_avg * (total_count - len(matches)) + total_compatibility) / total_count
                )
            
            # Update collaboration type popularity
            for match in matches:
                self.matching_stats["popular_collaboration_types"][match.collaboration_type.value] += 1
        
        # Update processing time
        current_avg_time = self.matching_stats["avg_matching_time"]
        total_requests = len(matches) if current_avg_time == 0 else self.matching_stats["total_matches"]
        
        self.matching_stats["avg_matching_time"] = (
            (current_avg_time * (total_requests - 1) + processing_time) / total_requests
            if total_requests > 0 else processing_time
        )
    
    async def _record_collaboration_start(self, proposal -> None: CollaborationProposal) -> None:
        """Record the start of a successful collaboration"""
        collaboration_record = {
            "proposal_id": proposal.proposal_id,
            "collaboration_type": proposal.collaboration_type.value,
            "participants": [proposal.proposer_id, proposal.recipient_id],
            "start_date": time.time(),
            "terms": proposal.terms,
            "status": "active"
        }
        
        # Add to collaboration history for both participants
        self.collaboration_history[proposal.proposer_id].append(collaboration_record)
        self.collaboration_history[proposal.recipient_id].append(collaboration_record)
        
        # Update success statistics
        self.matching_stats["successful_collaborations"] += 1
        
        logger.info("Recorded collaboration start: %s", proposal.proposal_id)
    
    async def _optimization_loop(self) -> None:
        """Background optimization loop"""
        while not self.shutdown_event.is_set():
            try:
                await asyncio.sleep(3600)  # Run every hour
                await self._optimize_matching_weights()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("Error in optimization loop: %s", e)
    
    async def _optimize_matching_weights(self) -> None:
        """Optimize compatibility weights based on success data"""
        if not self.config["learning_enabled"]:
            return
        
        # This would implement machine learning optimization in production
        # For now, just log the optimization attempt
        logger.info("Optimizing compatibility weights based on %d successful collaborations", 
                   self.matching_stats["successful_collaborations"])

# Global collaboration matching service instance
_collaboration_service: Optional[CollaborationMatchingService] = None

async def get_collaboration_service() -> CollaborationMatchingService:
    """Get global collaboration matching service instance"""
    global _collaboration_service
    if _collaboration_service is None:
        _collaboration_service = CollaborationMatchingService()
        await _collaboration_service.start()
    return _collaboration_service

async def shutdown_collaboration_service() -> None:
    """Shutdown global collaboration matching service"""
    global _collaboration_service
    if _collaboration_service:
        await _collaboration_service.stop()
        _collaboration_service = None

if __name__ == "__main__":
    async def test_collaboration_service() -> None:
        """Test collaboration matching service functionality"""
        service = CollaborationMatchingService()
        await service.start()
        
        try:
            # Create test creator profiles
            creator1 = CreatorProfile(
                creator_id="creator_1",
                name="Alice Musician",
                skills=["guitar", "vocals", "songwriting"],
                collaboration_preferences=[CollaborationType.CONTENT_CREATION, CollaborationType.CROSS_PROMOTION],
                brand_values=["creativity", "authenticity"],
                goals=["grow_audience", "create_music"],
                social_media_stats={"followers": 10000}
            )
            
            creator2 = CreatorProfile(
                creator_id="creator_2",
                name="Bob Photographer",
                skills=["photography", "video_editing", "marketing"],
                collaboration_preferences=[CollaborationType.CONTENT_CREATION, CollaborationType.SKILL_EXCHANGE],
                brand_values=["creativity", "quality"],
                goals=["grow_audience", "learn_music"],
                social_media_stats={"followers": 8000}
            )
            
            # Register creators
            await service.register_creator(creator1)
            await service.register_creator(creator2)
            
            # Calculate compatibility
            compatibility = await service.calculate_compatibility(
                "creator_1", "creator_2", CollaborationType.CONTENT_CREATION
            )
            print(f"Compatibility score: {compatibility.total_score:.2f}")
            print(f"Strengths: {compatibility.strengths}")
            print(f"Recommendations: {compatibility.recommendations}")
            
            # Create collaboration request
            request = CollaborationRequest(
                request_id="req_1",
                requester_id="creator_1",
                collaboration_type=CollaborationType.CONTENT_CREATION,
                description="Looking for visual content creator for music video",
                preferred_skills=["photography", "video_editing"],
                max_candidates=5
            )
            
            # Find matches
            matches = await service.find_matches(request)
            print(f"\nFound {len(matches)} matches:")
            for match in matches:
                print(f"  Match: {match.creator2_id} (Score: {match.compatibility_score.total_score:.2f})")
            
            # Get collaboration suggestions
            suggestions = await service.get_collaboration_suggestions("creator_1")
            print(f"\nCollaboration suggestions: {len(suggestions)}")
            
            # Get analytics
            analytics = await service.get_collaboration_analytics()
            print(f"\nAnalytics: {analytics}")
            
        finally:
            await service.stop()
    
    # Run test
    asyncio.run(test_collaboration_service())