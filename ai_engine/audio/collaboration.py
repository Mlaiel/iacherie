"""
Collaboration - Advanced Artist Collaboration and Matching Engine
Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

WARNING: This code is the proprietary intellectual property of Fahed Mlaiel.
Any unauthorized use, modification, distribution, or theft of this code 
without explicit written permission from the author is strictly prohibited
and will result in severe legal consequences under German and international law.

Email: mlaiel@live.de

This module provides intelligent artist collaboration matching, project management,
and collaborative content creation capabilities for the IA Influencer Agent platform.
"""

import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
import json
import numpy as np

from .music_analysis import MusicAnalysisResult, MusicGenre, MusicKey

logger = logging.getLogger(__name__)

class CollaborationType(Enum):
    """Types of collaboration"""
    REMIX = "remix"
    FEATURE = "feature"
    CO_WRITE = "co_write"
    PRODUCER = "producer"
    VOCALIST = "vocalist"
    INSTRUMENTALIST = "instrumentalist"
    SONGWRITER = "songwriter"
    MIXING_MASTERING = "mixing_mastering"
    LIVE_PERFORMANCE = "live_performance"
    VIDEO_PRODUCTION = "video_production"
    PROMOTIONAL = "promotional"
    LABEL_SIGNING = "label_signing"

class SkillLevel(Enum):
    """Skill level categories"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    PROFESSIONAL = "professional"
    EXPERT = "expert"

class CollaborationStatus(Enum):
    """Collaboration status"""
    PROPOSED = "proposed"
    PENDING = "pending"
    ACCEPTED = "accepted"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    REJECTED = "rejected"

class MatchQuality(Enum):
    """Quality of collaboration match"""
    PERFECT = "perfect"
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"

@dataclass
class ArtistProfile:
    """Artist profile for collaboration matching"""
    artist_id: str
    name: str
    email: str
    genres: List[MusicGenre]
    skills: Dict[str, SkillLevel]  # skill -> level
    preferred_keys: List[MusicKey]
    tempo_preferences: Tuple[int, int]  # min, max BPM
    collaboration_types: List[CollaborationType]
    location: Optional[str] = None
    timezone: str = "UTC"
    languages: List[str] = field(default_factory=lambda: ["en"])
    portfolio_urls: List[str] = field(default_factory=list)
    social_media: Dict[str, str] = field(default_factory=dict)
    equipment: List[str] = field(default_factory=list)
    daw_preferences: List[str] = field(default_factory=list)
    availability: Dict[str, Any] = field(default_factory=dict)
    collaboration_history: List[str] = field(default_factory=list)
    ratings: Dict[str, float] = field(default_factory=dict)  # skill -> rating
    verified: bool = False
    premium_member: bool = False
    open_to_collaborations: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class MatchingCriteria:
    """Criteria for collaboration matching"""
    collaboration_type: Optional[CollaborationType] = None
    genre: Optional[MusicGenre] = None
    key: Optional[MusicKey] = None
    tempo_range: Optional[Tuple[int, int]] = None
    skill_requirements: Dict[str, SkillLevel] = field(default_factory=dict)
    location_preference: Optional[str] = None
    max_distance_km: Optional[int] = None
    language_preference: Optional[str] = None
    budget_range: Optional[Tuple[float, float]] = None
    timeline_days: Optional[int] = None
    experience_level: Optional[SkillLevel] = None
    equipment_requirements: List[str] = field(default_factory=list)
    daw_compatibility: List[str] = field(default_factory=list)
    verified_only: bool = False
    premium_only: bool = False
    custom_filters: Dict[str, Any] = field(default_factory=dict)

@dataclass
class CollaborationMatch:
    """Potential collaboration match"""
    match_id: str
    requester_id: str
    matched_artist: ArtistProfile
    collaboration_type: CollaborationType
    match_quality: MatchQuality
    compatibility_score: float  # 0.0 to 1.0
    matching_factors: Dict[str, float] = field(default_factory=dict)
    suggested_roles: Dict[str, str] = field(default_factory=dict)
    estimated_timeline: Optional[int] = None  # days
    estimated_budget: Optional[Tuple[float, float]] = None
    recommendations: List[str] = field(default_factory=list)
    potential_challenges: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class CollaborationProject:
    """Active collaboration project"""
    project_id: str
    title: str
    description: str
    initiator_id: str
    collaborators: List[ArtistProfile]
    collaboration_type: CollaborationType
    status: CollaborationStatus
    created_at: datetime = field(default_factory=datetime.utcnow)
    deadline: Optional[datetime] = None
    budget: Optional[float] = None
    currency: str = "USD"
    genres: List[MusicGenre] = field(default_factory=list)
    key_signature: Optional[MusicKey] = None
    tempo: Optional[int] = None
    project_files: List[Dict[str, Any]] = field(default_factory=list)
    milestones: List[Dict[str, Any]] = field(default_factory=list)
    messages: List[Dict[str, Any]] = field(default_factory=list)
    rights_split: Dict[str, float] = field(default_factory=dict)  # artist_id -> percentage
    contract_terms: Dict[str, Any] = field(default_factory=dict)
    progress_percentage: float = 0.0
    latest_activity: datetime = field(default_factory=datetime.utcnow)
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class CollaborationInvite:
    """Collaboration invitation"""
    invite_id: str
    project_id: str
    sender_id: str
    recipient_id: str
    collaboration_type: CollaborationType
    proposed_role: str
    message: str = ""
    proposed_rights_percentage: float = 0.0
    proposed_budget: Optional[float] = None
    deadline: Optional[datetime] = None
    status: str = "pending"  # pending, accepted, rejected, expired
    sent_at: datetime = field(default_factory=datetime.utcnow)
    responded_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

class CollaborationMatcher:
    """
    Advanced Artist Collaboration and Matching Engine
    
    Provides intelligent collaboration matching including:
    - AI-powered artist compatibility analysis
    - Skill-based matching algorithms
    - Project management and workflow
    - Rights and revenue splitting
    - Communication and file sharing
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.config = config or {}
        
        # Artist and matching database
        self.artist_profiles: Dict[str, ArtistProfile] = {}
        self.collaboration_matches: Dict[str, List[CollaborationMatch]] = {}
        self.active_projects: Dict[str, CollaborationProject] = {}
        self.collaboration_invites: Dict[str, CollaborationInvite] = {}
        self.collaboration_history: Dict[str, List[str]] = {}
        
        # Matching algorithms
        self.matching_weights = {
            'genre_compatibility': 0.25,
            'skill_complementarity': 0.20,
            'key_harmony': 0.15,
            'tempo_match': 0.10,
            'location_proximity': 0.10,
            'experience_level': 0.10,
            'availability_overlap': 0.10
        }
        
        # Success prediction model (ML-based in production)
        self.success_factors = {
            'communication_quality': 0.30,
            'skill_compatibility': 0.25,
            'timeline_alignment': 0.20,
            'creative_vision_match': 0.15,
            'technical_compatibility': 0.10
        }
        
        self.logger.info("CollaborationMatcher initialized successfully")
    
    async def register_artist(
        self,
        artist_id: str,
        profile_data: Dict[str, Any]
    ) -> ArtistProfile:
        """Register artist profile for collaboration matching"""
        try:
            # Parse genres from strings to enums
            genres = []
            for genre_str in profile_data.get('genres', []):
                try:
                    genres.append(MusicGenre(genre_str.lower()))
                except ValueError:
                    self.logger.warning(f"Unknown genre: {genre_str}")
            
            # Parse skills
            skills = {}
            for skill, level_str in profile_data.get('skills', {}).items():
                try:
                    skills[skill] = SkillLevel(level_str.lower())
                except ValueError:
                    skills[skill] = SkillLevel.INTERMEDIATE  # Default
            
            # Parse collaboration types
            collaboration_types = []
            for type_str in profile_data.get('collaboration_types', []):
                try:
                    collaboration_types.append(CollaborationType(type_str.lower()))
                except ValueError:
                    self.logger.warning(f"Unknown collaboration type: {type_str}")
            
            # Create artist profile
            profile = ArtistProfile(
                artist_id=artist_id,
                name=profile_data.get('name', 'Unknown Artist'),
                email=profile_data.get('email', ''),
                genres=genres,
                skills=skills,
                preferred_keys=[MusicKey(k) for k in profile_data.get('preferred_keys', [])],
                tempo_preferences=tuple(profile_data.get('tempo_preferences', [80, 140])),
                collaboration_types=collaboration_types,
                location=profile_data.get('location'),
                timezone=profile_data.get('timezone', 'UTC'),
                languages=profile_data.get('languages', ['en']),
                portfolio_urls=profile_data.get('portfolio_urls', []),
                social_media=profile_data.get('social_media', {}),
                equipment=profile_data.get('equipment', []),
                daw_preferences=profile_data.get('daw_preferences', []),
                availability=profile_data.get('availability', {}),
                metadata=profile_data.get('metadata', {})
            )
            
            # Store profile
            self.artist_profiles[artist_id] = profile
            self.collaboration_matches[artist_id] = []
            self.collaboration_history[artist_id] = []
            
            self.logger.info(f"Artist profile registered: {artist_id}")
            
            return profile
            
        except Exception as e:
            self.logger.error(f"Artist registration failed: {str(e)}")
            raise
    
    async def find_matches(
        self,
        user_id: str,
        criteria: MatchingCriteria,
        limit: int = 10
    ) -> List[CollaborationMatch]:
        """
        Find collaboration matches based on criteria
        
        Args:
            user_id: Requesting user ID
            criteria: Matching criteria
            limit: Maximum number of matches to return
            
        Returns:
            List of potential collaboration matches
        """
        try:
            requester_profile = self.artist_profiles.get(user_id)
            if not requester_profile:
                raise ValueError("User profile not found")
            
            matches = []
            
            # Search through all artist profiles
            for candidate_id, candidate_profile in self.artist_profiles.items():
                # Skip self and inactive profiles
                if (candidate_id == user_id or 
                    not candidate_profile.open_to_collaborations):
                    continue
                
                # Apply filters
                if not self._meets_basic_criteria(candidate_profile, criteria):
                    continue
                
                # Calculate compatibility score
                compatibility_score = await self._calculate_compatibility(
                    requester_profile,
                    candidate_profile,
                    criteria
                )
                
                # Skip low compatibility matches
                if compatibility_score < 0.3:
                    continue
                
                # Determine match quality
                match_quality = self._determine_match_quality(compatibility_score)
                
                # Generate match details
                match = CollaborationMatch(
                    match_id=str(uuid.uuid4()),
                    requester_id=user_id,
                    matched_artist=candidate_profile,
                    collaboration_type=criteria.collaboration_type or CollaborationType.FEATURE,
                    match_quality=match_quality,
                    compatibility_score=compatibility_score,
                    matching_factors=await self._analyze_matching_factors(
                        requester_profile,
                        candidate_profile,
                        criteria
                    ),
                    suggested_roles=await self._suggest_roles(
                        requester_profile,
                        candidate_profile,
                        criteria
                    ),
                    estimated_timeline=self._estimate_timeline(criteria),
                    estimated_budget=self._estimate_budget(criteria, candidate_profile),
                    recommendations=await self._generate_recommendations(
                        requester_profile,
                        candidate_profile,
                        criteria
                    ),
                    expires_at=datetime.utcnow() + timedelta(days=30)
                )
                
                matches.append(match)
            
            # Sort by compatibility score
            matches.sort(key=lambda m: m.compatibility_score, reverse=True)
            
            # Store matches for user
            self.collaboration_matches[user_id].extend(matches[:limit])
            
            self.logger.info(f"Found {len(matches[:limit])} collaboration matches for {user_id}")
            
            return matches[:limit]
            
        except Exception as e:
            self.logger.error(f"Match finding failed: {str(e)}")
            return []
    
    def _meets_basic_criteria(
        self,
        candidate: ArtistProfile,
        criteria: MatchingCriteria
    ) -> bool:
        """Check if candidate meets basic matching criteria"""
        # Verification requirements
        if criteria.verified_only and not candidate.verified:
            return False
        
        if criteria.premium_only and not candidate.premium_member:
            return False
        
        # Collaboration type compatibility
        if (criteria.collaboration_type and 
            criteria.collaboration_type not in candidate.collaboration_types):
            return False
        
        # Genre compatibility
        if criteria.genre and criteria.genre not in candidate.genres:
            return False
        
        # Skill requirements
        for required_skill, min_level in criteria.skill_requirements.items():
            candidate_level = candidate.skills.get(required_skill)
            if not candidate_level or candidate_level.value < min_level.value:
                return False
        
        # Equipment requirements
        if criteria.equipment_requirements:
            candidate_equipment = [eq.lower() for eq in candidate.equipment]
            for required_eq in criteria.equipment_requirements:
                if required_eq.lower() not in candidate_equipment:
                    return False
        
        return True
    
    async def _calculate_compatibility(
        self,
        requester: ArtistProfile,
        candidate: ArtistProfile,
        criteria: MatchingCriteria
    ) -> float:
        """Calculate overall compatibility score"""
        total_score = 0.0
        
        # Genre compatibility
        genre_score = self._calculate_genre_compatibility(requester, candidate)
        total_score += genre_score * self.matching_weights['genre_compatibility']
        
        # Skill complementarity
        skill_score = self._calculate_skill_complementarity(requester, candidate)
        total_score += skill_score * self.matching_weights['skill_complementarity']
        
        # Musical harmony (key/tempo)
        harmony_score = self._calculate_musical_harmony(requester, candidate)
        total_score += harmony_score * self.matching_weights['key_harmony']
        
        # Location proximity
        location_score = self._calculate_location_proximity(requester, candidate)
        total_score += location_score * self.matching_weights['location_proximity']
        
        # Experience level compatibility
        experience_score = self._calculate_experience_compatibility(requester, candidate)
        total_score += experience_score * self.matching_weights['experience_level']
        
        # Availability overlap
        availability_score = self._calculate_availability_overlap(requester, candidate)
        total_score += availability_score * self.matching_weights['availability_overlap']
        
        return min(total_score, 1.0)  # Cap at 1.0
    
    def _calculate_genre_compatibility(
        self,
        requester: ArtistProfile,
        candidate: ArtistProfile
    ) -> float:
        """Calculate genre compatibility score"""
        if not requester.genres or not candidate.genres:
            return 0.0
        
        # Count overlapping genres
        common_genres = set(requester.genres) & set(candidate.genres)
        total_genres = set(requester.genres) | set(candidate.genres)
        
        if not total_genres:
            return 0.0
        
        # Jaccard similarity
        similarity = len(common_genres) / len(total_genres)
        
        # Boost for complementary genres
        complementary_pairs = {
            (MusicGenre.ROCK, MusicGenre.ELECTRONIC),
            (MusicGenre.HIP_HOP, MusicGenre.R_AND_B),
            (MusicGenre.JAZZ, MusicGenre.CLASSICAL),
            (MusicGenre.COUNTRY, MusicGenre.FOLK)
        }
        
        for req_genre in requester.genres:
            for cand_genre in candidate.genres:
                if (req_genre, cand_genre) in complementary_pairs or (cand_genre, req_genre) in complementary_pairs:
                    similarity += 0.2  # Boost for complementary genres
                    break
        
        return min(similarity, 1.0)
    
    def _calculate_skill_complementarity(
        self,
        requester: ArtistProfile,
        candidate: ArtistProfile
    ) -> float:
        """Calculate skill complementarity score"""
        # Perfect complementarity is when skills don't overlap but complement
        requester_skills = set(requester.skills.keys())
        candidate_skills = set(candidate.skills.keys())
        
        # Complementary skill pairs
        complementary_skills = {
            ('songwriting', 'production'),
            ('vocals', 'instrumental'),
            ('composition', 'arrangement'),
            ('mixing', 'mastering'),
            ('guitar', 'bass'),
            ('drums', 'percussion')
        }
        
        complementarity_score = 0.0
        
        for req_skill in requester_skills:
            for cand_skill in candidate_skills:
                # Check for complementary pairs
                if ((req_skill, cand_skill) in complementary_skills or
                    (cand_skill, req_skill) in complementary_skills):
                    complementarity_score += 0.3
                
                # Avoid skill overlap (unless both are high level)
                if req_skill == cand_skill:
                    req_level = requester.skills[req_skill]
                    cand_level = candidate.skills[cand_skill]
                    
                    if req_level in [SkillLevel.ADVANCED, SkillLevel.PROFESSIONAL, SkillLevel.EXPERT] and \
                       cand_level in [SkillLevel.ADVANCED, SkillLevel.PROFESSIONAL, SkillLevel.EXPERT]:
                        complementarity_score += 0.1  # Both experts can collaborate
                    else:
                        complementarity_score -= 0.1  # Skill overlap might be redundant
        
        return min(complementarity_score, 1.0)
    
    def _calculate_musical_harmony(
        self,
        requester: ArtistProfile,
        candidate: ArtistProfile
    ) -> float:
        """Calculate musical harmony compatibility"""
        harmony_score = 0.0
        
        # Key compatibility
        if requester.preferred_keys and candidate.preferred_keys:
            common_keys = set(requester.preferred_keys) & set(candidate.preferred_keys)
            total_keys = set(requester.preferred_keys) | set(candidate.preferred_keys)
            
            if total_keys:
                key_score = len(common_keys) / len(total_keys)
                harmony_score += key_score * 0.6
        
        # Tempo compatibility
        req_min, req_max = requester.tempo_preferences
        cand_min, cand_max = candidate.tempo_preferences
        
        # Calculate overlap
        overlap_start = max(req_min, cand_min)
        overlap_end = min(req_max, cand_max)
        
        if overlap_end > overlap_start:
            overlap_range = overlap_end - overlap_start
            total_range = max(req_max, cand_max) - min(req_min, cand_min)
            
            if total_range > 0:
                tempo_score = overlap_range / total_range
                harmony_score += tempo_score * 0.4
        
        return harmony_score
    
    def _calculate_location_proximity(
        self,
        requester: ArtistProfile,
        candidate: ArtistProfile
    ) -> float:
        """Calculate location proximity score"""
        if not requester.location or not candidate.location:
            return 0.5  # Neutral score if location unknown
        
        # Simple location matching (in production, use geolocation)
        if requester.location.lower() == candidate.location.lower():
            return 1.0
        
        # Check for same country/region
        req_parts = requester.location.split(',')
        cand_parts = candidate.location.split(',')
        
        if len(req_parts) > 1 and len(cand_parts) > 1:
            if req_parts[-1].strip().lower() == cand_parts[-1].strip().lower():
                return 0.7  # Same country
        
        return 0.2  # Different locations
    
    def _calculate_experience_compatibility(
        self,
        requester: ArtistProfile,
        candidate: ArtistProfile
    ) -> float:
        """Calculate experience level compatibility"""
        # Get average skill levels
        req_levels = [skill.value for skill in requester.skills.values()]
        cand_levels = [skill.value for skill in candidate.skills.values()]
        
        if not req_levels or not cand_levels:
            return 0.5
        
        req_avg = sum(req_levels) / len(req_levels)
        cand_avg = sum(cand_levels) / len(cand_levels)
        
        # Similar levels work well together
        level_diff = abs(req_avg - cand_avg)
        
        if level_diff <= 1:
            return 1.0
        elif level_diff <= 2:
            return 0.7
        else:
            return 0.3
    
    def _calculate_availability_overlap(
        self,
        requester: ArtistProfile,
        candidate: ArtistProfile
    ) -> float:
        """Calculate availability overlap score"""
        # Simplified availability check
        req_avail = requester.availability
        cand_avail = candidate.availability
        
        if not req_avail or not cand_avail:
            return 0.5  # Neutral if no availability info
        
        # Check timezone compatibility
        if req_avail.get('timezone') and cand_avail.get('timezone'):
            req_tz = req_avail['timezone']
            cand_tz = cand_avail['timezone']
            
            # Simple timezone check (in production, use proper timezone library)
            if req_tz == cand_tz:
                return 1.0
            else:
                return 0.6  # Different timezones but manageable
        
        return 0.5
    
    def _determine_match_quality(self, compatibility_score: float) -> MatchQuality:
        """Determine match quality based on compatibility score"""
        if compatibility_score >= 0.9:
            return MatchQuality.PERFECT
        elif compatibility_score >= 0.75:
            return MatchQuality.EXCELLENT
        elif compatibility_score >= 0.6:
            return MatchQuality.GOOD
        elif compatibility_score >= 0.4:
            return MatchQuality.FAIR
        else:
            return MatchQuality.POOR
    
    async def _analyze_matching_factors(
        self,
        requester: ArtistProfile,
        candidate: ArtistProfile,
        criteria: MatchingCriteria
    ) -> Dict[str, float]:
        """Analyze specific matching factors"""
        return {
            'genre_compatibility': self._calculate_genre_compatibility(requester, candidate),
            'skill_complementarity': self._calculate_skill_complementarity(requester, candidate),
            'musical_harmony': self._calculate_musical_harmony(requester, candidate),
            'location_proximity': self._calculate_location_proximity(requester, candidate),
            'experience_compatibility': self._calculate_experience_compatibility(requester, candidate),
            'availability_overlap': self._calculate_availability_overlap(requester, candidate)
        }
    
    async def _suggest_roles(
        self,
        requester: ArtistProfile,
        candidate: ArtistProfile,
        criteria: MatchingCriteria
    ) -> Dict[str, str]:
        """Suggest roles for collaboration"""
        roles = {}
        
        # Analyze skills to suggest roles
        req_strongest_skill = max(requester.skills.items(), key=lambda x: x[1].value) if requester.skills else ('unknown', SkillLevel.BEGINNER)
        cand_strongest_skill = max(candidate.skills.items(), key=lambda x: x[1].value) if candidate.skills else ('unknown', SkillLevel.BEGINNER)
        
        # Map skills to roles
        skill_to_role = {
            'vocals': 'Lead Vocalist',
            'guitar': 'Guitarist',
            'piano': 'Pianist',
            'drums': 'Drummer',
            'bass': 'Bassist',
            'production': 'Producer',
            'songwriting': 'Songwriter',
            'mixing': 'Mix Engineer',
            'mastering': 'Mastering Engineer'
        }
        
        roles['requester'] = skill_to_role.get(req_strongest_skill[0], 'Collaborator')
        roles['candidate'] = skill_to_role.get(cand_strongest_skill[0], 'Collaborator')
        
        return roles
    
    def _estimate_timeline(self, criteria: MatchingCriteria) -> Optional[int]:
        """Estimate collaboration timeline in days"""
        if criteria.timeline_days:
            return criteria.timeline_days
        
        # Default timelines by collaboration type
        timeline_estimates = {
            CollaborationType.REMIX: 14,
            CollaborationType.FEATURE: 21,
            CollaborationType.CO_WRITE: 30,
            CollaborationType.PRODUCER: 45,
            CollaborationType.MIXING_MASTERING: 7,
            CollaborationType.LIVE_PERFORMANCE: 60
        }
        
        return timeline_estimates.get(criteria.collaboration_type, 30)
    
    def _estimate_budget(
        self,
        criteria: MatchingCriteria,
        candidate: ArtistProfile
    ) -> Optional[Tuple[float, float]]:
        """Estimate collaboration budget range"""
        if criteria.budget_range:
            return criteria.budget_range
        
        # Base estimates by collaboration type and skill level
        base_rates = {
            CollaborationType.REMIX: (100, 500),
            CollaborationType.FEATURE: (200, 1000),
            CollaborationType.CO_WRITE: (300, 1500),
            CollaborationType.PRODUCER: (500, 2500),
            CollaborationType.MIXING_MASTERING: (200, 800),
            CollaborationType.LIVE_PERFORMANCE: (300, 2000)
        }
        
        base_min, base_max = base_rates.get(criteria.collaboration_type, (100, 500))
        
        # Adjust for skill level
        if candidate.skills:
            avg_skill_level = sum(skill.value for skill in candidate.skills.values()) / len(candidate.skills)
            skill_multiplier = 1.0 + (avg_skill_level - 2) * 0.3  # Scale from beginner to expert
            
            return (base_min * skill_multiplier, base_max * skill_multiplier)
        
        return (base_min, base_max)
    
    async def _generate_recommendations(
        self,
        requester: ArtistProfile,
        candidate: ArtistProfile,
        criteria: MatchingCriteria
    ) -> List[str]:
        """Generate collaboration recommendations"""
        recommendations = []
        
        # Skill-based recommendations
        req_skills = set(requester.skills.keys())
        cand_skills = set(candidate.skills.keys())
        
        if 'songwriting' in req_skills and 'production' in cand_skills:
            recommendations.append("Perfect songwriter-producer collaboration opportunity")
        
        if 'vocals' in req_skills and 'instrumental' in cand_skills:
            recommendations.append("Excellent vocalist-instrumentalist pairing")
        
        # Genre recommendations
        common_genres = set(requester.genres) & set(candidate.genres)
        if common_genres:
            recommendations.append(f"Strong genre alignment in {', '.join([g.value for g in common_genres])}")
        
        # Experience recommendations
        req_levels = [skill.value for skill in requester.skills.values()]
        cand_levels = [skill.value for skill in candidate.skills.values()]
        
        if req_levels and cand_levels:
            req_avg = sum(req_levels) / len(req_levels)
            cand_avg = sum(cand_levels) / len(cand_levels)
            
            if abs(req_avg - cand_avg) <= 1:
                recommendations.append("Well-matched experience levels for smooth collaboration")
        
        # Default recommendation
        if not recommendations:
            recommendations.append("Consider starting with a small project to test compatibility")
        
        return recommendations
    
    async def create_collaboration_project(
        self,
        initiator_id: str,
        project_data: Dict[str, Any],
        invited_artists: List[str] = None
    ) -> CollaborationProject:
        """Create new collaboration project"""
        project_id = str(uuid.uuid4())
        
        try:
            initiator_profile = self.artist_profiles.get(initiator_id)
            if not initiator_profile:
                raise ValueError("Initiator profile not found")
            
            # Parse collaboration type
            collaboration_type = CollaborationType(project_data.get('collaboration_type', 'feature'))
            
            # Create project
            project = CollaborationProject(
                project_id=project_id,
                title=project_data.get('title', 'Untitled Collaboration'),
                description=project_data.get('description', ''),
                initiator_id=initiator_id,
                collaborators=[initiator_profile],
                collaboration_type=collaboration_type,
                status=CollaborationStatus.PROPOSED,
                deadline=datetime.fromisoformat(project_data['deadline']) if project_data.get('deadline') else None,
                budget=project_data.get('budget'),
                currency=project_data.get('currency', 'USD'),
                genres=[MusicGenre(g) for g in project_data.get('genres', [])],
                key_signature=MusicKey(project_data['key_signature']) if project_data.get('key_signature') else None,
                tempo=project_data.get('tempo'),
                rights_split={initiator_id: project_data.get('initiator_rights_percentage', 50.0)},
                tags=project_data.get('tags', []),
                metadata=project_data.get('metadata', {})
            )
            
            # Store project
            self.active_projects[project_id] = project
            
            # Send invitations if artists specified
            if invited_artists:
                for artist_id in invited_artists:
                    await self.send_collaboration_invite(
                        project_id=project_id,
                        sender_id=initiator_id,
                        recipient_id=artist_id,
                        collaboration_type=collaboration_type,
                        message=project_data.get('invite_message', '')
                    )
            
            self.logger.info(f"Collaboration project created: {project_id}")
            
            return project
            
        except Exception as e:
            self.logger.error(f"Project creation failed: {str(e)}")
            raise
    
    async def send_collaboration_invite(
        self,
        project_id: str,
        sender_id: str,
        recipient_id: str,
        collaboration_type: CollaborationType,
        message: str = "",
        proposed_role: str = "Collaborator",
        proposed_rights_percentage: float = 25.0,
        proposed_budget: Optional[float] = None,
        deadline: Optional[datetime] = None
    ) -> CollaborationInvite:
        """Send collaboration invitation"""
        invite_id = str(uuid.uuid4())
        
        try:
            invite = CollaborationInvite(
                invite_id=invite_id,
                project_id=project_id,
                sender_id=sender_id,
                recipient_id=recipient_id,
                collaboration_type=collaboration_type,
                proposed_role=proposed_role,
                message=message,
                proposed_rights_percentage=proposed_rights_percentage,
                proposed_budget=proposed_budget,
                deadline=deadline,
                expires_at=datetime.utcnow() + timedelta(days=7)  # 7 days to respond
            )
            
            # Store invite
            self.collaboration_invites[invite_id] = invite
            
            self.logger.info(f"Collaboration invite sent: {invite_id}")
            
            return invite
            
        except Exception as e:
            self.logger.error(f"Invite sending failed: {str(e)}")
            raise
    
    async def respond_to_invite(
        self,
        invite_id: str,
        recipient_id: str,
        response: str,  # "accepted" or "rejected"
        message: str = ""
    ) -> bool:
        """Respond to collaboration invitation"""
        try:
            invite = self.collaboration_invites.get(invite_id)
            if not invite:
                raise ValueError("Invitation not found")
            
            if invite.recipient_id != recipient_id:
                raise ValueError("Unauthorized to respond to this invitation")
            
            if invite.status != "pending":
                raise ValueError("Invitation already responded to")
            
            # Update invite
            invite.status = response
            invite.responded_at = datetime.utcnow()
            invite.metadata['response_message'] = message
            
            # If accepted, add to project
            if response == "accepted":
                project = self.active_projects.get(invite.project_id)
                if project:
                    recipient_profile = self.artist_profiles.get(recipient_id)
                    if recipient_profile:
                        project.collaborators.append(recipient_profile)
                        project.rights_split[recipient_id] = invite.proposed_rights_percentage
                        project.status = CollaborationStatus.IN_PROGRESS
                        project.latest_activity = datetime.utcnow()
            
            self.logger.info(f"Invite response recorded: {invite_id}, Response: {response}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Invite response failed: {str(e)}")
            return False
    
    def get_user_matches(self, user_id: str) -> List[CollaborationMatch]:
        """Get collaboration matches for user"""
        return self.collaboration_matches.get(user_id, [])
    
    def get_user_projects(
        self,
        user_id: str,
        status_filter: Optional[CollaborationStatus] = None
    ) -> List[CollaborationProject]:
        """Get user's collaboration projects"""
        user_projects = []
        
        for project in self.active_projects.values():
            # Check if user is involved in project
            is_involved = (project.initiator_id == user_id or 
                          any(collab.artist_id == user_id for collab in project.collaborators))
            
            if is_involved:
                if status_filter is None or project.status == status_filter:
                    user_projects.append(project)
        
        return user_projects
    
    def get_pending_invites(self, user_id: str) -> List[CollaborationInvite]:
        """Get pending invitations for user"""
        return [
            invite for invite in self.collaboration_invites.values()
            if invite.recipient_id == user_id and invite.status == "pending"
        ]
    
    async def update_project_progress(
        self,
        project_id: str,
        user_id: str,
        progress_data: Dict[str, Any]
    ) -> bool:
        """Update project progress"""
        try:
            project = self.active_projects.get(project_id)
            if not project:
                return False
            
            # Verify user is part of project
            is_collaborator = (project.initiator_id == user_id or 
                             any(collab.artist_id == user_id for collab in project.collaborators))
            
            if not is_collaborator:
                return False
            
            # Update progress
            if 'progress_percentage' in progress_data:
                project.progress_percentage = progress_data['progress_percentage']
            
            if 'status' in progress_data:
                project.status = CollaborationStatus(progress_data['status'])
            
            if 'milestones' in progress_data:
                project.milestones.extend(progress_data['milestones'])
            
            project.latest_activity = datetime.utcnow()
            
            self.logger.info(f"Project progress updated: {project_id}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Project update failed: {str(e)}")
            return False
