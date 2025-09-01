"""Creator Matching Database Module

AI-powered creator matching system for intelligent collaboration recommendations.
Utilizes machine learning, vector embeddings, and behavioral analysis.

Author: Fahed Mlaiel <mlaiel@live.de>
Team: Lead AI Developer + Backend Senior + ML Engineer + DBA + Security + Microservices
"""

from typing import List, Dict, Any, Optional, Union, Tuple, Set
from datetime import datetime, timedelta
from enum import Enum
import json
import uuid
import logging
import numpy as np
from sqlalchemy import (
    Column, Integer, String, DateTime, Boolean, Text, 
    ForeignKey, DECIMAL, ARRAY, JSON, Index, Float
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.dialects.postgresql import UUID, JSONB, ENUM
import asyncio
import aioredis
from dataclasses import dataclass, asdict
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
import faiss
import pickle
import hashlib

logger = logging.getLogger(__name__)

Base = declarative_base()

class MatchingCriteria(Enum):
    """
Creator matching criteria enumeration"""

    CONTENT_TYPE = "content_type"
    SKILL_COMPLEMENT = "skill_complement"
    AUDIENCE_OVERLAP = "audience_overlap"
    COLLABORATION_HISTORY = "collaboration_history"
    LOCATION_PROXIMITY = "location_proximity"
    AVAILABILITY_SYNC = "availability_sync"
    BUDGET_COMPATIBILITY = "budget_compatibility"
    STYLE_SIMILARITY = "style_similarity"

class MatchingStatus(Enum):
    """Matching status enumeration"""

    PENDING = "pending"
    SUGGESTED = "suggested"
    CONTACTED = "contacted"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    EXPIRED = "expired"

class CreatorProfile(Base):
    """
    Comprehensive creator profile for AI-powered matching.
    Stores skills, preferences, history, and vector embeddings.
    """
    __tablename__ = 'creator_profiles'
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), unique=True, nullable=False)
    profile_name = Column(String(255), nullable=False)
    bio = Column(Text)
    
    # Creator specialization
    primary_content_types = Column(ARRAY(String))  # music, video, photo, blog, comedy
    secondary_content_types = Column(ARRAY(String))
    skills = Column(JSONB)  # Detailed skills with proficiency levels
    tools_software = Column(ARRAY(String))
    languages = Column(ARRAY(String))
    
    # Experience and portfolio
    experience_years = Column(Integer)
    portfolio_links = Column(JSONB)
    achievement_badges = Column(ARRAY(String))
    certifications = Column(JSONB)
    notable_collaborations = Column(JSONB)
    
    # Style and preferences
    style_tags = Column(ARRAY(String))
    genre_preferences = Column(ARRAY(String))
    collaboration_preferences = Column(JSONB)
    working_style = Column(JSONB)
    
    # Audience and reach
    follower_counts = Column(JSONB)  # Per platform
    audience_demographics = Column(JSONB)
    engagement_rates = Column(JSONB)
    target_audience = Column(JSONB)
    
    # Availability and logistics
    availability_schedule = Column(JSONB)
    timezone = Column(String(50))
    location = Column(JSONB)  # City, country, coordinates
    remote_work_preference = Column(Boolean, default=True)
    travel_willingness = Column(Boolean, default=False)
    
    # Financial preferences
    rate_ranges = Column(JSONB)  # Per hour, per project, revenue share
    payment_preferences = Column(ARRAY(String))
    budget_flexibility = Column(String(20))
    
    # AI and matching data
    skill_vector = Column(ARRAY(Float))  # Vector embedding for skills
    style_vector = Column(ARRAY(Float))  # Vector embedding for style
    content_vector = Column(ARRAY(Float))  # Vector embedding for content
    collaboration_vector = Column(ARRAY(Float))  # Vector for collaboration history
    
    # Performance metrics
    collaboration_success_rate = Column(Float, default=0.0)
    average_project_rating = Column(Float, default=0.0)
    response_time_hours = Column(Float)
    reliability_score = Column(Float, default=0.0)
    
    # Behavioral analysis
    communication_style = Column(JSONB)
    work_patterns = Column(JSONB)
    collaboration_insights = Column(JSONB)
    ai_personality_profile = Column(JSONB)
    
    # Metadata and tracking
    profile_completeness = Column(Float, default=0.0)
    last_activity = Column(DateTime)
    matching_preferences = Column(JSONB)
    privacy_settings = Column(JSONB)
    verification_status = Column(String(20), default='unverified')
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_creator_content_types', 'primary_content_types'),
        Index('idx_creator_skills', 'skills'),
        Index('idx_creator_location', 'location'),
        Index('idx_creator_availability', 'availability_schedule'),
        Index('idx_creator_last_activity', 'last_activity'),
    )

class MatchingSuggestion(Base):
    """
    AI-generated matching suggestions between creators.
    Stores match scores, reasoning, and interaction history.
    """
    __tablename__ = 'matching_suggestions'
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    suggestion_id = Column(String(100), unique=True, nullable=False)
    
    # Creator pairing
    requester_id = Column(UUID(as_uuid=True), ForeignKey('creator_profiles.id'), nullable=False)
    suggested_creator_id = Column(UUID(as_uuid=True), ForeignKey('creator_profiles.id'), nullable=False)
    project_id = Column(UUID(as_uuid=True), ForeignKey('collaboration_projects.id'))
    
    # Matching analysis
    overall_match_score = Column(Float, nullable=False)
    criteria_scores = Column(JSONB)  # Scores per matching criteria
    matching_reasons = Column(JSONB)  # AI-generated explanations
    potential_synergies = Column(JSONB)
    
    # AI insights
    collaboration_prediction = Column(JSONB)
    success_probability = Column(Float)
    risk_factors = Column(JSONB)
    recommended_project_types = Column(ARRAY(String))
    
    # Interaction tracking
    status = Column(ENUM(MatchingStatus), default=MatchingStatus.PENDING)
    viewed_at = Column(DateTime)
    contacted_at = Column(DateTime)
    response_at = Column(DateTime)
    interaction_history = Column(JSONB)
    
    # Feedback and learning
    requester_feedback = Column(JSONB)
    suggested_creator_feedback = Column(JSONB)
    actual_collaboration_outcome = Column(JSONB)
    model_performance_metrics = Column(JSONB)
    
    # Metadata
    algorithm_version = Column(String(20))
    generated_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_matching_requester', 'requester_id', 'status'),
        Index('idx_matching_suggested', 'suggested_creator_id', 'status'),
        Index('idx_matching_score', 'overall_match_score'),
        Index('idx_matching_project', 'project_id'),
    )

@dataclass
class MatchingRequest:
    """
Data class for creator matching requests"""
    requester_id: str
    project_id: Optional[str] = None
    content_types: List[str] = None
    required_skills: List[str] = None
    budget_range: Tuple[float, float] = None
    timeline: Tuple[datetime, datetime] = None
    location_preference: str = None
    remote_ok: bool = True
    max_suggestions: int = 10
    min_match_score: float = 0.6

@dataclass
class MatchingFilter:
    """
Data class for filtering criteria"""
    content_types: List[str] = None
    experience_min: int = None
    location_radius_km: int = None
    availability_required: bool = False
    verified_only: bool = False
    rating_min: float = None
    exclude_previous_collaborators: bool = False

class CreatorMatchingEngine:
    """
    Enterprise AI-powered creator matching engine.
    Utilizes machine learning, vector similarity, and behavioral analysis.
    """
    
    def __init__(self, db_session, redis_client: aioredis.Redis = None):
        self.db_session = db_session
        self.redis_client = redis_client
        self.cache_ttl = 1800  # 30 minutes cache
        
        # Initialize ML models
        self.sentence_transformer = SentenceTransformer('all-MiniLM-L6-v2')
        self.faiss_index = None
        self.profile_vectors = {}
        
        # Matching weights (can be tuned based on performance)
        self.criteria_weights = {
            MatchingCriteria.CONTENT_TYPE: 0.25,
            MatchingCriteria.SKILL_COMPLEMENT: 0.20,
            MatchingCriteria.AUDIENCE_OVERLAP: 0.15,
            MatchingCriteria.COLLABORATION_HISTORY: 0.10,
            MatchingCriteria.LOCATION_PROXIMITY: 0.05,
            MatchingCriteria.AVAILABILITY_SYNC: 0.10,
            MatchingCriteria.BUDGET_COMPATIBILITY: 0.10,
            MatchingCriteria.STYLE_SIMILARITY: 0.05
        }
    
    async def find_matches(
        self, 
        request: MatchingRequest, 
        filters: MatchingFilter = None
    ) -> List[MatchingSuggestion]:
        """
        Find optimal creator matches using AI algorithms.
        
        Args:
            request: Matching request parameters
            filters: Additional filtering criteria
            
        Returns:
            List of matching suggestions
        """
        try:
            # Get requester profile
            requester_profile = await self._get_creator_profile(request.requester_id)
            if not requester_profile:
                logger.warning(f"Requester profile not found: {request.requester_id}")
                return []
            
            # Get candidate profiles
            candidates = await self._get_candidate_profiles(requester_profile, filters)
            if not candidates:
                logger.info("No suitable candidates found")
                return []
            
            # Initialize/update FAISS index if needed
            await self._ensure_faiss_index()
            
            # Generate matching suggestions
            suggestions = []
            for candidate in candidates:
                match_score, criteria_scores, reasoning = await self._calculate_match_score(
                    requester_profile, candidate, request
                )
                
                if match_score >= request.min_match_score:
                    suggestion = await self._create_matching_suggestion(
                        requester_profile, candidate, match_score, 
                        criteria_scores, reasoning, request
                    )
                    suggestions.append(suggestion)
            
            # Sort by match score and limit results
            suggestions.sort(key=lambda x: x.overall_match_score, reverse=True)
            suggestions = suggestions[:request.max_suggestions]
            
            # Cache results
            if self.redis_client and suggestions:
                await self._cache_suggestions(request.requester_id, suggestions)
            
            logger.info(f"Generated {len(suggestions)} matching suggestions for {request.requester_id}")
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Failed to find matches: {str(e)}")
            return []
    
    async def update_creator_profile(
        self, 
        user_id: str, 
        profile_data: Dict[str, Any]
    ) -> Optional[CreatorProfile]:
        """
        Update creator profile with AI vector generation.
        
        Args:
            user_id: User UUID
            profile_data: Profile update data
            
        Returns:
            Updated profile instance
        """
        try:
            # Get or create profile
            profile = await self.db_session.query(CreatorProfile)\
                .filter(CreatorProfile.user_id == uuid.UUID(user_id))\
                .first()
            
            if not profile:
                profile = CreatorProfile(user_id=uuid.UUID(user_id))
                self.db_session.add(profile)
            
            # Update basic fields
            for field, value in profile_data.items():
                if hasattr(profile, field):
                    setattr(profile, field, value)
            
            # Generate AI vectors
            await self._update_profile_vectors(profile)
            
            # Calculate profile completeness
            profile.profile_completeness = self._calculate_profile_completeness(profile)
            
            # Update timestamp
            profile.updated_at = datetime.utcnow()
            
            # Save changes
            await self.db_session.commit()
            await self.db_session.refresh(profile)
            
            # Update FAISS index
            await self._update_faiss_index(profile)
            
            # Cache profile
            if self.redis_client:
                await self._cache_creator_profile(profile)
            
            logger.info(f"Updated creator profile: {user_id}")
            
            return profile
            
        except Exception as e:
            await self.db_session.rollback()
            logger.error(f"Failed to update creator profile {user_id}: {str(e)}")
            return None
    
    async def get_creator_analytics(self, user_id: str) -> Dict[str, Any]:
        """
        Get comprehensive creator analytics for matching optimization.
        
        Args:
            user_id: User UUID
            
        Returns:
            Analytics data dictionary
        """
        try:
            profile = await self._get_creator_profile(user_id)
            if not profile:
                return {}
            
            # Get matching history
            suggestions_made = await self.db_session.query(MatchingSuggestion)\
                .filter(MatchingSuggestion.requester_id == profile.id)\
                .count()
            
            suggestions_received = await self.db_session.query(MatchingSuggestion)\
                .filter(MatchingSuggestion.suggested_creator_id == profile.id)\
                .count()
            
            successful_matches = await self.db_session.query(MatchingSuggestion)\
                .filter(
                    (MatchingSuggestion.requester_id == profile.id) |
                    (MatchingSuggestion.suggested_creator_id == profile.id),
                    MatchingSuggestion.status == MatchingStatus.ACCEPTED
                ).count()
            
            # Calculate analytics
            analytics = {
                'profile_info': {
                    'completeness': profile.profile_completeness,
                    'verification_status': profile.verification_status,
                    'last_activity': profile.last_activity.isoformat() if profile.last_activity else None,
                    'content_types': profile.primary_content_types or []
                },
                'matching_stats': {
                    'suggestions_made': suggestions_made,
                    'suggestions_received': suggestions_received,
                    'successful_matches': successful_matches,
                    'match_success_rate': (successful_matches / max(suggestions_received, 1)) * 100,
                    'collaboration_success_rate': profile.collaboration_success_rate
                },
                'performance_metrics': {
                    'average_rating': profile.average_project_rating,
                    'response_time_hours': profile.response_time_hours,
                    'reliability_score': profile.reliability_score
                },
                'audience_reach': {
                    'total_followers': sum(profile.follower_counts.values()) if profile.follower_counts else 0,
                    'platforms': list(profile.follower_counts.keys()) if profile.follower_counts else [],
                    'engagement_rates': profile.engagement_rates or {}
                },
                'skills_analysis': {
                    'primary_skills': list(profile.skills.keys()) if profile.skills else [],
                    'skill_levels': profile.skills or {},
                    'tools_software': profile.tools_software or []
                },
                'collaboration_insights': profile.collaboration_insights or {},
                'ai_recommendations': await self._generate_profile_recommendations(profile)
            }
            
            return analytics
            
        except Exception as e:
            logger.error(f"Failed to get creator analytics for {user_id}: {str(e)}")
            return {}
    
    async def provide_matching_feedback(
        self, 
        suggestion_id: str, 
        user_id: str, 
        feedback: Dict[str, Any]
    ) -> bool:
        """
        Provide feedback on matching suggestions for ML model improvement.
        
        Args:
            suggestion_id: Matching suggestion ID
            user_id: User providing feedback
            feedback: Feedback data
            
        Returns:
            Success status
        """
        try:
            suggestion = await self.db_session.query(MatchingSuggestion)\
                .filter(MatchingSuggestion.suggestion_id == suggestion_id)\
                .first()
            
            if not suggestion:
                return False
            
            # Determine if user is requester or suggested creator
            user_profile = await self._get_creator_profile(user_id)
            if not user_profile:
                return False
            
            if user_profile.id == suggestion.requester_id:
                suggestion.requester_feedback = feedback
            elif user_profile.id == suggestion.suggested_creator_id:
                suggestion.suggested_creator_feedback = feedback
            else:
                return False
            
            # Update status based on feedback
            if feedback.get('accepted'):
                suggestion.status = MatchingStatus.ACCEPTED
            elif feedback.get('rejected'):
                suggestion.status = MatchingStatus.REJECTED
            
            # Store learning data for model improvement
            await self._store_feedback_for_learning(suggestion, feedback)
            
            # Update timestamps
            suggestion.updated_at = datetime.utcnow()
            if not suggestion.response_at:
                suggestion.response_at = datetime.utcnow()
            
            await self.db_session.commit()
            
            logger.info(f"Feedback provided for suggestion {suggestion_id}")
            
            return True
            
        except Exception as e:
            await self.db_session.rollback()
            logger.error(f"Failed to provide feedback for suggestion {suggestion_id}: {str(e)}")
            return False
    
    # Private helper methods
    
    async def _get_creator_profile(self, user_id: str) -> Optional[CreatorProfile]:
        """Get creator profile by user ID"""
        try:
            # Check cache first
            if self.redis_client:
                cached_data = await self.redis_client.get(f"creator_profile:{user_id}")
                if cached_data:
                    return self._deserialize_creator_profile(json.loads(cached_data))
            
            # Query database
            profile = await self.db_session.query(CreatorProfile)\
                .filter(CreatorProfile.user_id == uuid.UUID(user_id))\
                .first()
            
            # Cache result
            if profile and self.redis_client:
                await self._cache_creator_profile(profile)
            
            return profile
            
        except Exception as e:
            logger.error(f"Failed to get creator profile {user_id}: {str(e)}")
            return None
    
    async def _get_candidate_profiles(
        self, 
        requester: CreatorProfile, 
        filters: MatchingFilter = None
    ) -> List[CreatorProfile]:
        """Get candidate profiles for matching"""
        try:
            query = self.db_session.query(CreatorProfile)\
                .filter(CreatorProfile.id != requester.id)
            
            # Apply filters
            if filters:
                if filters.content_types:
                    query = query.filter(
                        CreatorProfile.primary_content_types.overlap(filters.content_types)
                    )
                
                if filters.experience_min:
                    query = query.filter(CreatorProfile.experience_years >= filters.experience_min)
                
                if filters.verified_only:
                    query = query.filter(CreatorProfile.verification_status == 'verified')
                
                if filters.rating_min:
                    query = query.filter(CreatorProfile.average_project_rating >= filters.rating_min)
            
            # Order by activity and rating
            candidates = await query\
                .order_by(
                    CreatorProfile.last_activity.desc(),
                    CreatorProfile.average_project_rating.desc()
                )\
                .limit(100)\
                .all()
            
            return candidates
            
        except Exception as e:
            logger.error(f"Failed to get candidate profiles: {str(e)}")
            return []
    
    async def _calculate_match_score(
        self, 
        requester: CreatorProfile, 
        candidate: CreatorProfile, 
        request: MatchingRequest
    ) -> Tuple[float, Dict[str, float], Dict[str, Any]]:
        """Calculate comprehensive match score using multiple criteria"""
        criteria_scores = {}
        reasoning = {}
        
        # Content type compatibility
        content_score = self._calculate_content_type_match(requester, candidate, request)
        criteria_scores[MatchingCriteria.CONTENT_TYPE.value] = content_score
        reasoning['content_type'] = f"Content compatibility: {content_score:.2f}"
        
        # Skill complementarity
        skill_score = self._calculate_skill_complement(requester, candidate)
        criteria_scores[MatchingCriteria.SKILL_COMPLEMENT.value] = skill_score
        reasoning['skill_complement'] = f"Skill synergy: {skill_score:.2f}"
        
        # Audience overlap analysis
        audience_score = self._calculate_audience_overlap(requester, candidate)
        criteria_scores[MatchingCriteria.AUDIENCE_OVERLAP.value] = audience_score
        reasoning['audience_overlap'] = f"Audience synergy: {audience_score:.2f}"
        
        # Collaboration history compatibility
        history_score = self._calculate_collaboration_compatibility(requester, candidate)
        criteria_scores[MatchingCriteria.COLLABORATION_HISTORY.value] = history_score
        reasoning['collaboration_history'] = f"Collaboration fit: {history_score:.2f}"
        
        # Location and availability
        location_score = self._calculate_location_proximity(requester, candidate)
        criteria_scores[MatchingCriteria.LOCATION_PROXIMITY.value] = location_score
        reasoning['location_proximity'] = f"Location compatibility: {location_score:.2f}"
        
        availability_score = self._calculate_availability_sync(requester, candidate)
        criteria_scores[MatchingCriteria.AVAILABILITY_SYNC.value] = availability_score
        reasoning['availability_sync'] = f"Schedule alignment: {availability_score:.2f}"
        
        # Budget compatibility
        budget_score = self._calculate_budget_compatibility(requester, candidate, request)
        criteria_scores[MatchingCriteria.BUDGET_COMPATIBILITY.value] = budget_score
        reasoning['budget_compatibility'] = f"Budget alignment: {budget_score:.2f}"
        
        # Style similarity
        style_score = self._calculate_style_similarity(requester, candidate)
        criteria_scores[MatchingCriteria.STYLE_SIMILARITY.value] = style_score
        reasoning['style_similarity'] = f"Style compatibility: {style_score:.2f}"
        
        # Calculate weighted overall score
        overall_score = sum(
            score * self.criteria_weights[MatchingCriteria(criteria)]
            for criteria, score in criteria_scores.items()
        )
        
        return overall_score, criteria_scores, reasoning
    
    def _calculate_content_type_match(
        self, 
        requester: CreatorProfile, 
        candidate: CreatorProfile, 
        request: MatchingRequest
    ) -> float:
        """Calculate content type compatibility score"""
        requester_types = set(requester.primary_content_types or [])
        candidate_types = set(candidate.primary_content_types or [])
        
        if request.content_types:
            required_types = set(request.content_types)
            # Check if candidate has required types
            if not required_types.intersection(candidate_types):
                return 0.0
        
        # Calculate overlap and complementarity
        overlap = len(requester_types.intersection(candidate_types))
        complementarity = len(requester_types.symmetric_difference(candidate_types))
        
        # Balance between similarity and complementarity
        if len(requester_types) == 0 or len(candidate_types) == 0:
            return 0.5
        
        similarity_score = overlap / len(requester_types.union(candidate_types))
        complement_score = min(complementarity / 3, 1.0)  # Cap at 3 different types
        
        return (similarity_score * 0.6) + (complement_score * 0.4)
    
    def _calculate_skill_complement(
        self, 
        requester: CreatorProfile, 
        candidate: CreatorProfile
    ) -> float:
        """
Calculate skill complementarity score"""
        requester_skills = requester.skills or {}
        candidate_skills = candidate.skills or {}
        
        if not requester_skills or not candidate_skills:
            return 0.5
        
        # Vector similarity for skills
        if requester.skill_vector and candidate.skill_vector:
            similarity = cosine_similarity(
                [requester.skill_vector], 
                [candidate.skill_vector]
            )[0][0]
            
            # Convert similarity to complementarity (skills should complement, not duplicate)
            complementarity = 1.0 - similarity
            return max(0.0, min(1.0, complementarity))
        
        # Fallback to simple skill comparison
        req_skill_set = set(requester_skills.keys())
        cand_skill_set = set(candidate_skills.keys())
        
        overlap = len(req_skill_set.intersection(cand_skill_set))
        total_unique = len(req_skill_set.union(cand_skill_set))
        
        if total_unique == 0:
            return 0.5
        
        # Prefer some overlap but not complete duplication
        overlap_ratio = overlap / total_unique
        optimal_overlap = 0.3  # 30% overlap is ideal
        
        return 1.0 - abs(overlap_ratio - optimal_overlap) / optimal_overlap
    
    def _calculate_audience_overlap(
        self, 
        requester: CreatorProfile, 
        candidate: CreatorProfile
    ) -> float:
        """
Calculate audience overlap and synergy score"""
        req_demographics = requester.audience_demographics or {}
        cand_demographics = candidate.audience_demographics or {}
        
        if not req_demographics or not cand_demographics:
            return 0.5
        
        # Compare age groups, interests, platforms
        age_similarity = self._compare_age_demographics(
            req_demographics.get('age_groups', {}),
            cand_demographics.get('age_groups', {})
        )
        
        interest_overlap = self._compare_interests(
            req_demographics.get('interests', []),
            cand_demographics.get('interests', [])
        )
        
        platform_synergy = self._compare_platforms(
            requester.follower_counts or {},
            candidate.follower_counts or {}
        )
        
        return (age_similarity * 0.3) + (interest_overlap * 0.4) + (platform_synergy * 0.3)
    
    def _calculate_collaboration_compatibility(
        self, 
        requester: CreatorProfile, 
        candidate: CreatorProfile
    ) -> float:
        """
Calculate collaboration style compatibility"""
        req_style = requester.working_style or {}
        cand_style = candidate.working_style or {}
        
        # Communication style compatibility
        comm_compatibility = self._compare_communication_styles(
            req_style.get('communication', {}),
            cand_style.get('communication', {})
        )
        
        # Work schedule compatibility
        schedule_compatibility = self._compare_work_schedules(
            req_style.get('schedule', {}),
            cand_style.get('schedule', {})
        )
        
        # Project approach compatibility
        approach_compatibility = self._compare_project_approaches(
            req_style.get('project_approach', {}),
            cand_style.get('project_approach', {})
        )
        
        return (comm_compatibility * 0.4) + (schedule_compatibility * 0.3) + (approach_compatibility * 0.3)
    
    def _calculate_location_proximity(
        self, 
        requester: CreatorProfile, 
        candidate: CreatorProfile
    ) -> float:
        """
Calculate location proximity score"""
        if requester.remote_work_preference and candidate.remote_work_preference:
            return 1.0
        
        req_location = requester.location or {}
        cand_location = candidate.location or {}
        
        if not req_location or not cand_location:
            return 0.5
        
        # Calculate distance if coordinates available
        if ('lat' in req_location and 'lng' in req_location and
            'lat' in cand_location and 'lng' in cand_location):
            
            distance_km = self._calculate_distance(
                req_location['lat'], req_location['lng'],
                cand_location['lat'], cand_location['lng']
            )
            
            # Score based on distance (closer is better)
            if distance_km <= 50:
                return 1.0
            elif distance_km <= 200:
                return 0.8
            elif distance_km <= 500:
                return 0.6
            else:
                return 0.3
        
        # Fallback to timezone comparison
        if requester.timezone and candidate.timezone:
            req_tz = int(requester.timezone.split('UTC')[1] if 'UTC' in requester.timezone else '0')
            cand_tz = int(candidate.timezone.split('UTC')[1] if 'UTC' in candidate.timezone else '0')
            
            tz_diff = abs(req_tz - cand_tz)
            return max(0.0, 1.0 - (tz_diff / 12))
        
        return 0.5
    
    def _calculate_availability_sync(
        self, 
        requester: CreatorProfile, 
        candidate: CreatorProfile
    ) -> float:
        """
Calculate availability synchronization score"""
        req_schedule = requester.availability_schedule or {}
        cand_schedule = candidate.availability_schedule or {}
        
        if not req_schedule or not cand_schedule:
            return 0.5
        
        # Compare availability by day of week
        overlap_hours = 0
        total_req_hours = 0
        
        for day in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']:
            req_hours = req_schedule.get(day, [])
            cand_hours = cand_schedule.get(day, [])
            
            if req_hours and cand_hours:
                daily_overlap = self._calculate_time_overlap(req_hours, cand_hours)
                overlap_hours += daily_overlap
                total_req_hours += len(req_hours)
        
        if total_req_hours == 0:
            return 0.5
        
        return min(1.0, overlap_hours / total_req_hours)
    
    def _calculate_budget_compatibility(
        self, 
        requester: CreatorProfile, 
        candidate: CreatorProfile, 
        request: MatchingRequest
    ) -> float:
        """
Calculate budget compatibility score"""
        cand_rates = candidate.rate_ranges or {}
        
        if not cand_rates:
            return 0.5
        
        if request.budget_range:
            min_budget, max_budget = request.budget_range
            
            # Check different rate types
            for rate_type in ['hourly', 'project', 'daily']:
                if rate_type in cand_rates:
                    cand_min = cand_rates[rate_type].get('min', 0)
                    cand_max = cand_rates[rate_type].get('max', float('inf'))
                    
                    # Check if there's overlap
                    if max_budget >= cand_min and min_budget <= cand_max:
                        # Calculate overlap percentage
                        overlap_start = max(min_budget, cand_min)
                        overlap_end = min(max_budget, cand_max)
                        overlap_size = overlap_end - overlap_start
                        
                        budget_range_size = max_budget - min_budget
                        candidate_range_size = cand_max - cand_min
                        
                        overlap_score = overlap_size / max(budget_range_size, candidate_range_size)
                        return min(1.0, overlap_score)
        
        return 0.5
    
    def _calculate_style_similarity(
        self, 
        requester: CreatorProfile, 
        candidate: CreatorProfile
    ) -> float:
        """
Calculate style similarity score"""
        if requester.style_vector and candidate.style_vector:
            similarity = cosine_similarity(
                [requester.style_vector], 
                [candidate.style_vector]
            )[0][0]
            return max(0.0, min(1.0, (similarity + 1) / 2))  # Normalize to 0-1
        
        # Fallback to tag comparison
        req_tags = set(requester.style_tags or [])
        cand_tags = set(candidate.style_tags or [])
        
        if not req_tags or not cand_tags:
            return 0.5
        
        intersection = len(req_tags.intersection(cand_tags))
        union = len(req_tags.union(cand_tags))
        
        return intersection / union if union > 0 else 0.0
    
    async def _create_matching_suggestion(
        self,
        requester: CreatorProfile,
        candidate: CreatorProfile,
        match_score: float,
        criteria_scores: Dict[str, float],
        reasoning: Dict[str, Any],
        request: MatchingRequest
    ) -> MatchingSuggestion:
        """
Create a matching suggestion record"""
        suggestion_id = f"MATCH-{datetime.utcnow().strftime('%Y%m%d%H%M')}-{str(uuid.uuid4())[:8]}"
        
        # Generate AI insights
        collaboration_prediction = await self._generate_collaboration_prediction(
            requester, candidate, match_score
        )
        
        suggestion = MatchingSuggestion(
            suggestion_id=suggestion_id,
            requester_id=requester.id,
            suggested_creator_id=candidate.id,
            project_id=uuid.UUID(request.project_id) if request.project_id else None,
            overall_match_score=match_score,
            criteria_scores=criteria_scores,
            matching_reasons=reasoning,
            collaboration_prediction=collaboration_prediction,
            success_probability=self._calculate_success_probability(match_score, requester, candidate),
            risk_factors=self._identify_risk_factors(requester, candidate),
            recommended_project_types=self._recommend_project_types(requester, candidate),
            algorithm_version="v2.1.0",
            expires_at=datetime.utcnow() + timedelta(days=30)
        )
        
        self.db_session.add(suggestion)
        await self.db_session.commit()
        await self.db_session.refresh(suggestion)
        
        return suggestion
    
    # Additional helper methods would continue here...
    # For brevity, I'm including the key structural methods
    
    async def _update_profile_vectors(self, profile: CreatorProfile):
        """Update AI vectors for profile"""
        # Generate skill vector
        if profile.skills:
            skill_text = " ".join(profile.skills.keys())
            profile.skill_vector = self.sentence_transformer.encode(skill_text).tolist()
        
        # Generate style vector
        if profile.style_tags:
            style_text = " ".join(profile.style_tags)
            profile.style_vector = self.sentence_transformer.encode(style_text).tolist()
        
        # Generate content vector
        if profile.primary_content_types:
            content_text = " ".join(profile.primary_content_types)
            profile.content_vector = self.sentence_transformer.encode(content_text).tolist()
    
    async def _ensure_faiss_index(self):
        """Ensure FAISS index is initialized and up-to-date"""
        if self.faiss_index is None:
            # Initialize FAISS index
            dimension = 384  # MiniLM embedding dimension
            self.faiss_index = faiss.IndexFlatIP(dimension)
            
            # Load existing profiles
            profiles = await self.db_session.query(CreatorProfile)\
                .filter(CreatorProfile.skill_vector.isnot(None))\
                .all()
            
            if profiles:
                vectors = np.array([p.skill_vector for p in profiles])
                self.faiss_index.add(vectors)
                
                # Store profile mapping
                self.profile_vectors = {i: str(p.id) for i, p in enumerate(profiles)}
    
    def _calculate_profile_completeness(self, profile: CreatorProfile) -> float:
        """
Calculate profile completeness percentage"""
        total_fields = 20
        completed_fields = 0
        
        # Check essential fields
        if profile.bio: completed_fields += 1
        if profile.primary_content_types: completed_fields += 1
        if profile.skills: completed_fields += 1
        if profile.experience_years: completed_fields += 1
        if profile.portfolio_links: completed_fields += 1
        if profile.style_tags: completed_fields += 1
        if profile.collaboration_preferences: completed_fields += 1
        if profile.follower_counts: completed_fields += 1
        if profile.availability_schedule: completed_fields += 1
        if profile.location: completed_fields += 1
        if profile.rate_ranges: completed_fields += 1
        if profile.tools_software: completed_fields += 1
        if profile.languages: completed_fields += 1
        if profile.genre_preferences: completed_fields += 1
        if profile.working_style: completed_fields += 1
        if profile.audience_demographics: completed_fields += 1
        if profile.timezone: completed_fields += 1
        if profile.payment_preferences: completed_fields += 1
        if profile.certifications: completed_fields += 1
        if profile.notable_collaborations: completed_fields += 1
        
        return (completed_fields / total_fields) * 100
    
    # Cache and utility methods
    async def _cache_creator_profile(self, profile: CreatorProfile):
        """
Cache creator profile data"""
        try:
            profile_data = {
                'id': str(profile.id),
                'user_id': str(profile.user_id),
                'profile_name': profile.profile_name,
                'primary_content_types': profile.primary_content_types or [],
                'skills': profile.skills or {},
                'updated_at': profile.updated_at.isoformat()
            }
            
            await self.redis_client.setex(
                f"creator_profile:{profile.user_id}",
                self.cache_ttl,
                json.dumps(profile_data)
            )
            
        except Exception as e:
            logger.warning(f"Failed to cache creator profile {profile.user_id}: {str(e)}")

# Export main classes
__all__ = [
    'CreatorProfile',
    'MatchingSuggestion',
    'MatchingCriteria',
    'MatchingStatus',
    'MatchingRequest',
    'MatchingFilter',
    'CreatorMatchingEngine'
]
