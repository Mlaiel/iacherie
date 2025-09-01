"""Creative Collaboration & Matching Engine
Advanced AI-powered collaboration matching system for content creators and influencers.

Created by: Fahed Mlaiel (mlaiel@live.de)
(c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  STRICT COPYRIGHT WARNING ⚠️ 
This code, concept, and intellectual property belongs exclusively to Fahed Mlaiel.
ANY unauthorized use, reproduction, distribution, or theft of this code/concept 
without explicit written permission from Fahed Mlaiel (mlaiel@live.de) is 
STRICTLY PROHIBITED and will result in immediate legal action.
All rights reserved. Patent pending.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Union, Any, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from pathlib import Path
import json
import numpy as np
from abc import ABC, abstractmethod
import uuid
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import networkx as nx
from geopy.distance import geodesic
import requests
from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict, Counter
import pickle
import redis
from sqlalchemy import create_engine, Column, String, DateTime, Float, Integer, Boolean, Text, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

logger = logging.getLogger(__name__)

Base = declarative_base()


class CreatorType(Enum):
    """
Types of content creators"""

    MUSICIAN = "musician"
    PODCASTER = "podcaster"
    VOICE_ACTOR = "voice_actor"
    AUDIO_PRODUCER = "audio_producer"
    SOUND_DESIGNER = "sound_designer"
    COMPOSER = "composer"
    DJ = "dj"
    AUDIO_ENGINEER = "audio_engineer"
    NARRATOR = "narrator"
    SINGER = "singer"
    INSTRUMENTALIST = "instrumentalist"
    BEATMAKER = "beatmaker"


class CollaborationType(Enum):
    """Types of collaborations"""

    FEATURING = "featuring"
    REMIX = "remix"
    COVER = "cover"
    DUET = "duet"
    JOINT_PROJECT = "joint_project"
    COMPILATION = "compilation"
    CROSS_PROMOTION = "cross_promotion"
    MENTORSHIP = "mentorship"
    PRODUCTION = "production"
    MIXING_MASTERING = "mixing_mastering"
    SONGWRITING = "songwriting"
    GUEST_APPEARANCE = "guest_appearance"


class SkillLevel(Enum):
    """Skill level classifications"""

    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    PROFESSIONAL = "professional"
    EXPERT = "expert"


class CollaborationStatus(Enum):
    """Collaboration status states"""

    PROPOSED = "proposed"
    ACCEPTED = "accepted"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    DISPUTED = "disputed"


class MatchingCriteria(Enum):
    """Criteria for matching creators"""

    GENRE_COMPATIBILITY = "genre_compatibility"
    SKILL_LEVEL = "skill_level"
    GEOGRAPHIC_PROXIMITY = "geographic_proximity"
    AUDIENCE_OVERLAP = "audience_overlap"
    COLLABORATION_HISTORY = "collaboration_history"
    EQUIPMENT_COMPATIBILITY = "equipment_compatibility"
    SCHEDULE_ALIGNMENT = "schedule_alignment"
    PROJECT_TYPE = "project_type"
    BUDGET_RANGE = "budget_range"
    LANGUAGE_COMPATIBILITY = "language_compatibility"


@dataclass
class CreatorProfile:
    """Comprehensive creator profile"""
    creator_id: str
    name: str
    creator_type: CreatorType
    email: str
    
    # Professional Information
    genres: List[str] = field(default_factory=list)
    skills: Dict[str, SkillLevel] = field(default_factory=dict)
    equipment: List[str] = field(default_factory=list)
    daw_software: List[str] = field(default_factory=list)
    years_experience: int = 0
    
    # Location and Availability
    location: Optional[Dict[str, float]] = None  # {"lat": x, "lng": y}
    timezone: str = "UTC"
    availability: Dict[str, List[str]] = field(default_factory=dict)  # {"monday": ["09:00-17:00"]}
    
    # Portfolio and Social
    portfolio_urls: List[str] = field(default_factory=list)
    social_media: Dict[str, str] = field(default_factory=dict)
    samples: List[Dict[str, Any]] = field(default_factory=list)
    
    # Collaboration Preferences
    preferred_collaborations: List[CollaborationType] = field(default_factory=list)
    budget_range: Dict[str, int] = field(default_factory=dict)  # {"min": 0, "max": 1000}
    languages: List[str] = field(default_factory=list)
    collaboration_history: List[str] = field(default_factory=list)
    
    # Metrics
    follower_counts: Dict[str, int] = field(default_factory=dict)
    engagement_rates: Dict[str, float] = field(default_factory=dict)
    average_views: Dict[str, int] = field(default_factory=dict)
    
    # Settings
    is_available: bool = True
    verified: bool = False
    premium_member: bool = False
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class CollaborationRequest:
    """Collaboration request structure"""
    request_id: str
    requester_id: str
    target_id: str
    collaboration_type: CollaborationType
    
    project_title: str
    project_description: str
    project_budget: Optional[Dict[str, int]] = None
    project_timeline: Optional[Dict[str, datetime]] = None
    
    requirements: Dict[str, Any] = field(default_factory=dict)
    compensation: Optional[Dict[str, Any]] = None
    
    status: CollaborationStatus = CollaborationStatus.PROPOSED
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    messages: List[Dict[str, Any]] = field(default_factory=list)
    contracts: List[str] = field(default_factory=list)


@dataclass
class MatchResult:
    """
Creator matching result"""
    matched_creator: CreatorProfile
    compatibility_score: float  # 0.0 to 1.0
    match_reasons: List[str]
    compatibility_breakdown: Dict[MatchingCriteria, float]
    suggested_collaboration_types: List[CollaborationType]
    potential_challenges: List[str] = field(default_factory=list)
    collaboration_ideas: List[str] = field(default_factory=list)


@dataclass
class ProjectOpportunity:
    """
Project opportunity for creators"""
    opportunity_id: str
    title: str
    description: str
    project_type: CollaborationType
    posted_by: str
    creator_requirements: Dict[str, Any]
    
    budget: Optional[Dict[str, int]] = None
    timeline: Optional[Dict[str, datetime]] = None
    location_required: Optional[Dict[str, float]] = None
    remote_friendly: bool = True
    
    applications: List[str] = field(default_factory=list)
    status: str = "open"
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None


class CreatorDatabase(Base):
    """Database model for creator profiles"""
    __tablename__ = 'creators'
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    creator_type = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    profile_data = Column(JSON, nullable=False)
    is_active = Column(Boolean, default=True)
    verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class CollaborationDatabase(Base):
    """
Database model for collaborations"""
    __tablename__ = 'collaborations'
    
    id = Column(String, primary_key=True)
    requester_id = Column(String, ForeignKey('creators.id'), nullable=False)
    target_id = Column(String, ForeignKey('creators.id'), nullable=False)
    collaboration_data = Column(JSON, nullable=False)
    status = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class ProjectDatabase(Base):
    """
Database model for project opportunities"""
    __tablename__ = 'projects'
    
    id = Column(String, primary_key=True)
    posted_by = Column(String, ForeignKey('creators.id'), nullable=False)
    project_data = Column(JSON, nullable=False)
    status = Column(String, default='open')
    created_at = Column(DateTime, default=datetime.now)
    expires_at = Column(DateTime, nullable=True)


class AdvancedMatchingEngine:
    """
AI-powered creator matching engine"""
    
    def __init__(self, database_url: str, redis_host: str = "localhost"):
        # Database setup
        self.engine = create_engine(database_url)
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        
        # Redis for caching
        try:
            self.redis_client = redis.Redis(host=redis_host, decode_responses=True)
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}")
            self.redis_client = None
        
        # ML models for matching
        self.genre_vectorizer = TfidfVectorizer(max_features=1000)
        self.skill_vectorizer = TfidfVectorizer(max_features=500)
        self.collaboration_graph = nx.Graph()
        
        # Initialize models
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize ML models with existing data"""
        try:
            # Load existing creator data for model training
            creators = self.session.query(CreatorDatabase).filter(
                CreatorDatabase.is_active == True
            ).all()
            
            if creators:
                self._train_matching_models([
                    CreatorProfile(**json.loads(creator.profile_data))
                    for creator in creators
                ])
            
            logger.info("Matching models initialized")
            
        except Exception as e:
            logger.error(f"Model initialization failed: {e}")
    
    def _train_matching_models(self, creator_profiles: List[CreatorProfile]):
        """Train ML models for creator matching"""
        try:
            # Prepare genre data
            genre_texts = []
            skill_texts = []
            
            for profile in creator_profiles:
                # Genre text
                genre_text = ' '.join(profile.genres)
                genre_texts.append(genre_text)
                
                # Skill text
                skill_text = ' '.join([
                    f"{skill}_{level.value}" 
                    for skill, level in profile.skills.items()
                ])
                skill_texts.append(skill_text)
                
                # Build collaboration graph
                self.collaboration_graph.add_node(profile.creator_id, **{
                    'type': profile.creator_type.value,
                    'genres': profile.genres,
                    'location': profile.location
                })
                
                # Add collaboration edges
                for collaborator_id in profile.collaboration_history:
                    self.collaboration_graph.add_edge(
                        profile.creator_id, 
                        collaborator_id,
                        weight=1.0
                    )
            
            # Train vectorizers
            if genre_texts:
                self.genre_vectorizer.fit(genre_texts)
            if skill_texts:
                self.skill_vectorizer.fit(skill_texts)
            
            logger.info("Matching models trained successfully")
            
        except Exception as e:
            logger.error(f"Model training failed: {e}")
    
    async def find_matches(self,
                          creator_profile: CreatorProfile,
                          collaboration_type: CollaborationType,
                          max_matches: int = 10,
                          filters: Optional[Dict[str, Any]] = None) -> List[MatchResult]:
        """Find compatible creators for collaboration"""
        try:
            # Check cache first
            cache_key = f"matches_{creator_profile.creator_id}_{collaboration_type.value}_{max_matches}"
            if self.redis_client:
                cached_matches = self.redis_client.get(cache_key)
                if cached_matches:
                    return [MatchResult(**match) for match in json.loads(cached_matches)]
            
            # Get potential matches from database
            potential_matches = await self._get_potential_matches(
                creator_profile, collaboration_type, filters
            )
            
            # Calculate compatibility scores
            match_results = []
            
            for candidate in potential_matches:
                compatibility = await self._calculate_compatibility(
                    creator_profile, candidate, collaboration_type
                )
                
                if compatibility['score'] > 0.3:  # Minimum threshold
                    match_result = MatchResult(
                        matched_creator=candidate,
                        compatibility_score=compatibility['score'],
                        match_reasons=compatibility['reasons'],
                        compatibility_breakdown=compatibility['breakdown'],
                        suggested_collaboration_types=compatibility['suggested_types'],
                        potential_challenges=compatibility['challenges'],
                        collaboration_ideas=compatibility['ideas']
                    )
                    
                    match_results.append(match_result)
            
            # Sort by compatibility score
            match_results.sort(key=lambda x: x.compatibility_score, reverse=True)
            
            # Limit results
            final_matches = match_results[:max_matches]
            
            # Cache results
            if self.redis_client:
                cache_data = json.dumps([
                    {
                        'matched_creator': match.matched_creator.__dict__,
                        'compatibility_score': match.compatibility_score,
                        'match_reasons': match.match_reasons,
                        'compatibility_breakdown': {k.value: v for k, v in match.compatibility_breakdown.items()},
                        'suggested_collaboration_types': [t.value for t in match.suggested_collaboration_types],
                        'potential_challenges': match.potential_challenges,
                        'collaboration_ideas': match.collaboration_ideas
                    }
                    for match in final_matches
                ], default=str)
                
                self.redis_client.setex(cache_key, 3600, cache_data)  # Cache for 1 hour
            
            logger.info(f"Found {len(final_matches)} matches for {creator_profile.creator_id}")
            return final_matches
            
        except Exception as e:
            logger.error(f"Match finding failed: {e}")
            return []
    
    async def _get_potential_matches(self,
                                   creator_profile: CreatorProfile,
                                   collaboration_type: CollaborationType,
                                   filters: Optional[Dict[str, Any]]) -> List[CreatorProfile]:
        """Get potential matches from database with initial filtering"""
        try:
            query = self.session.query(CreatorDatabase).filter(
                CreatorDatabase.is_active == True,
                CreatorDatabase.id != creator_profile.creator_id
            )
            
            # Apply filters
            if filters:
                # Location filter
                if 'max_distance_km' in filters and creator_profile.location:
                    # This would need more sophisticated geographic filtering
                    pass
                
                # Creator type filter
                if 'creator_types' in filters:
                    query = query.filter(
                        CreatorDatabase.creator_type.in_(filters['creator_types'])
                    )
                
                # Verified only
                if filters.get('verified_only'):
                    query = query.filter(CreatorDatabase.verified == True)
            
            # Get results
            db_creators = query.limit(100).all()  # Limit initial set
            
            # Convert to CreatorProfile objects
            creator_profiles = []
            for db_creator in db_creators:
                try:
                    profile_data = json.loads(db_creator.profile_data)
                    profile = CreatorProfile(**profile_data)
                    profile.creator_id = db_creator.id
                    creator_profiles.append(profile)
                except Exception as e:
                    logger.warning(f"Failed to parse creator profile {db_creator.id}: {e}")
                    continue
            
            return creator_profiles
            
        except Exception as e:
            logger.error(f"Potential matches query failed: {e}")
            return []
    
    async def _calculate_compatibility(self,
                                     creator1: CreatorProfile,
                                     creator2: CreatorProfile,
                                     collaboration_type: CollaborationType) -> Dict[str, Any]:
        """Calculate detailed compatibility between two creators"""
        try:
            compatibility_scores = {}
            reasons = []
            challenges = []
            ideas = []
            
            # Genre compatibility
            genre_score = self._calculate_genre_compatibility(creator1, creator2)
            compatibility_scores[MatchingCriteria.GENRE_COMPATIBILITY] = genre_score
            
            if genre_score > 0.7:
                reasons.append(f"Strong genre alignment: {', '.join(set(creator1.genres) & set(creator2.genres))}")
            elif genre_score < 0.3:
                challenges.append("Limited genre overlap - may need creative bridge")
            
            # Skill level compatibility
            skill_score = self._calculate_skill_compatibility(creator1, creator2, collaboration_type)
            compatibility_scores[MatchingCriteria.SKILL_LEVEL] = skill_score
            
            if skill_score > 0.8:
                reasons.append("Complementary skill levels")
            elif skill_score < 0.4:
                challenges.append("Significant skill gap may require mentorship approach")
            
            # Geographic proximity
            geo_score = self._calculate_geographic_proximity(creator1, creator2)
            compatibility_scores[MatchingCriteria.GEOGRAPHIC_PROXIMITY] = geo_score
            
            if geo_score > 0.8:
                reasons.append("Close geographic proximity enables in-person collaboration")
                ideas.append("Consider studio sessions together")
            elif geo_score < 0.3:
                reasons.append("Remote collaboration opportunity")
                ideas.append("Plan virtual collaboration workflow")
            
            # Audience overlap
            audience_score = self._calculate_audience_overlap(creator1, creator2)
            compatibility_scores[MatchingCriteria.AUDIENCE_OVERLAP] = audience_score
            
            if audience_score > 0.6:
                reasons.append("Significant audience overlap for cross-promotion")
                ideas.append("Joint content could reach both audiences effectively")
            
            # Equipment compatibility
            equipment_score = self._calculate_equipment_compatibility(creator1, creator2)
            compatibility_scores[MatchingCriteria.EQUIPMENT_COMPATIBILITY] = equipment_score
            
            if equipment_score > 0.7:
                reasons.append("Compatible equipment and software")
            elif equipment_score < 0.3:
                challenges.append("Equipment differences may require technical coordination")
            
            # Schedule alignment
            schedule_score = self._calculate_schedule_alignment(creator1, creator2)
            compatibility_scores[MatchingCriteria.SCHEDULE_ALIGNMENT] = schedule_score
            
            if schedule_score > 0.6:
                reasons.append("Good schedule alignment for collaboration")
            else:
                challenges.append("Schedule coordination needed")
            
            # Collaboration history
            history_score = self._calculate_collaboration_history_score(creator1, creator2)
            compatibility_scores[MatchingCriteria.COLLABORATION_HISTORY] = history_score
            
            # Budget compatibility
            budget_score = self._calculate_budget_compatibility(creator1, creator2)
            compatibility_scores[MatchingCriteria.BUDGET_RANGE] = budget_score
            
            if budget_score < 0.5:
                challenges.append("Budget expectations may need alignment")
            
            # Calculate overall score (weighted average)
            weights = {
                MatchingCriteria.GENRE_COMPATIBILITY: 0.25,
                MatchingCriteria.SKILL_LEVEL: 0.20,
                MatchingCriteria.AUDIENCE_OVERLAP: 0.15,
                MatchingCriteria.EQUIPMENT_COMPATIBILITY: 0.10,
                MatchingCriteria.SCHEDULE_ALIGNMENT: 0.10,
                MatchingCriteria.GEOGRAPHIC_PROXIMITY: 0.08,
                MatchingCriteria.COLLABORATION_HISTORY: 0.07,
                MatchingCriteria.BUDGET_RANGE: 0.05
            }
            
            overall_score = sum(
                compatibility_scores[criteria] * weight
                for criteria, weight in weights.items()
            )
            
            # Suggest collaboration types
            suggested_types = self._suggest_collaboration_types(
                creator1, creator2, compatibility_scores, collaboration_type
            )
            
            # Generate collaboration ideas
            if not ideas:
                ideas = self._generate_collaboration_ideas(
                    creator1, creator2, collaboration_type
                )
            
            return {
                'score': overall_score,
                'reasons': reasons,
                'breakdown': compatibility_scores,
                'suggested_types': suggested_types,
                'challenges': challenges,
                'ideas': ideas
            }
            
        except Exception as e:
            logger.error(f"Compatibility calculation failed: {e}")
            return {
                'score': 0.0,
                'reasons': [],
                'breakdown': {},
                'suggested_types': [],
                'challenges': [f"Analysis error: {str(e)}"],
                'ideas': []
            }
    
    def _calculate_genre_compatibility(self,
                                     creator1: CreatorProfile,
                                     creator2: CreatorProfile) -> float:
        """Calculate genre compatibility score"""
        if not creator1.genres or not creator2.genres:
            return 0.5  # Neutral if no genre info
        
        # Direct overlap
        overlap = set(creator1.genres) & set(creator2.genres)
        union = set(creator1.genres) | set(creator2.genres)
        
        if not union:
            return 0.5
        
        jaccard_similarity = len(overlap) / len(union)
        
        # Genre compatibility matrix (simplified)
        compatible_genres = {
            'pop': ['rock', 'electronic', 'indie'],
            'rock': ['pop', 'alternative', 'indie'],
            'electronic': ['pop', 'ambient', 'techno'],
            'jazz': ['blues', 'classical', 'fusion'],
            'hip-hop': ['r&b', 'trap', 'pop'],
            'classical': ['orchestral', 'chamber', 'jazz'],
            'folk': ['acoustic', 'country', 'indie'],
            'ambient': ['electronic', 'new age', 'experimental']
        }
        
        # Check for compatible (but not identical) genres
        compatibility_bonus = 0.0
        for genre1 in creator1.genres:
            for genre2 in creator2.genres:
                if genre1.lower() != genre2.lower():
                    compatible_list = compatible_genres.get(genre1.lower(), [])
                    if genre2.lower() in compatible_list:
                        compatibility_bonus += 0.2
        
        final_score = min(jaccard_similarity + compatibility_bonus, 1.0)
        return final_score
    
    def _calculate_skill_compatibility(self,
                                     creator1: CreatorProfile,
                                     creator2: CreatorProfile,
                                     collaboration_type: CollaborationType) -> float:
        """
Calculate skill level compatibility"""
        if not creator1.skills or not creator2.skills:
            return 0.5
        
        # Get relevant skills for collaboration type
        relevant_skills = self._get_relevant_skills_for_collaboration(collaboration_type)
        
        skill_scores = []
        
        for skill in relevant_skills:
            skill1_level = creator1.skills.get(skill)
            skill2_level = creator2.skills.get(skill)
            
            if skill1_level and skill2_level:
                # Calculate compatibility based on collaboration type
                if collaboration_type == CollaborationType.MENTORSHIP:
                    # Mentor should be higher level
                    level_values = {
                        SkillLevel.BEGINNER: 1,
                        SkillLevel.INTERMEDIATE: 2,
                        SkillLevel.ADVANCED: 3,
                        SkillLevel.PROFESSIONAL: 4,
                        SkillLevel.EXPERT: 5
                    }
                    
                    diff = abs(level_values[skill1_level] - level_values[skill2_level])
                    if diff >= 2:  # Good gap for mentorship
                        skill_scores.append(0.9)
                    else:
                        skill_scores.append(0.5)
                
                else:
                    # Similar levels work well for most collaborations
                    if skill1_level == skill2_level:
                        skill_scores.append(1.0)
                    else:
                        level_values = {
                            SkillLevel.BEGINNER: 1,
                            SkillLevel.INTERMEDIATE: 2,
                            SkillLevel.ADVANCED: 3,
                            SkillLevel.PROFESSIONAL: 4,
                            SkillLevel.EXPERT: 5
                        }
                        
                        diff = abs(level_values[skill1_level] - level_values[skill2_level])
                        skill_scores.append(max(0.2, 1.0 - (diff * 0.2)))
            
            elif skill1_level or skill2_level:
                # One has skill, other doesn't - could be complementary
                skill_scores.append(0.6)
        
        return sum(skill_scores) / len(skill_scores) if skill_scores else 0.5
    
    def _get_relevant_skills_for_collaboration(self, collaboration_type: CollaborationType) -> List[str]:
        """
Get relevant skills for collaboration type"""
        skill_mapping = {
            CollaborationType.FEATURING: ['vocals', 'performance', 'songwriting'],
            CollaborationType.REMIX: ['production', 'mixing', 'electronic_music'],
            CollaborationType.PRODUCTION: ['audio_production', 'mixing', 'mastering'],
            CollaborationType.SONGWRITING: ['songwriting', 'composition', 'lyrics'],
            CollaborationType.MIXING_MASTERING: ['mixing', 'mastering', 'audio_engineering'],
            CollaborationType.DUET: ['vocals', 'harmony', 'performance']
        }
        
        return skill_mapping.get(collaboration_type, ['general_music', 'creativity'])
    
    def _calculate_geographic_proximity(self,
                                      creator1: CreatorProfile,
                                      creator2: CreatorProfile) -> float:
        """
Calculate geographic proximity score"""
        if not creator1.location or not creator2.location:
            return 0.5  # Remote collaboration possible
        
        try:
            # Calculate distance using coordinates
            distance = geodesic(
                (creator1.location['lat'], creator1.location['lng']),
                (creator2.location['lat'], creator2.location['lng'])
            ).kilometers
            
            # Score based on distance
            if distance <= 50:  # Same city
                return 1.0
            elif distance <= 200:  # Same region
                return 0.8
            elif distance <= 500:  # Same country/neighboring states
                return 0.6
            elif distance <= 2000:  # Same continent
                return 0.4
            else:  # Different continents
                return 0.2
            
        except Exception:
            return 0.5
    
    def _calculate_audience_overlap(self,
                                  creator1: CreatorProfile,
                                  creator2: CreatorProfile) -> float:
        """
Calculate audience overlap potential"""
        # Simplified calculation based on follower counts and genres
        score = 0.0
        
        # Similar follower counts suggest similar audience levels
        platform_scores = []
        
        for platform in ['youtube', 'spotify', 'instagram', 'tiktok']:
            count1 = creator1.follower_counts.get(platform, 0)
            count2 = creator2.follower_counts.get(platform, 0)
            
            if count1 > 0 and count2 > 0:
                # Calculate similarity in follower counts (logarithmic scale)
                import math
                log1 = math.log10(max(count1, 1))
                log2 = math.log10(max(count2, 1))
                
                diff = abs(log1 - log2)
                platform_score = max(0.0, 1.0 - (diff / 6.0))  # Max diff is ~6 orders of magnitude
                platform_scores.append(platform_score)
        
        if platform_scores:
            score += sum(platform_scores) / len(platform_scores) * 0.5
        
        # Genre overlap suggests audience overlap
        genre_overlap = len(set(creator1.genres) & set(creator2.genres))
        genre_union = len(set(creator1.genres) | set(creator2.genres))
        
        if genre_union > 0:
            score += (genre_overlap / genre_union) * 0.5
        
        return min(score, 1.0)
    
    def _calculate_equipment_compatibility(self,
                                         creator1: CreatorProfile,
                                         creator2: CreatorProfile) -> float:
        """
Calculate equipment and software compatibility"""
        score = 0.0
        
        # DAW compatibility
        if creator1.daw_software and creator2.daw_software:
            common_daws = set(creator1.daw_software) & set(creator2.daw_software)
            if common_daws:
                score += 0.4
            
            # Cross-compatible DAWs
            compatible_pairs = [
                ('pro_tools', 'logic_pro'),
                ('ableton_live', 'fl_studio'),
                ('cubase', 'nuendo')
            ]
            
            for daw1 in creator1.daw_software:
                for daw2 in creator2.daw_software:
                    for pair in compatible_pairs:
                        if (daw1 in pair and daw2 in pair) or (daw2 in pair and daw1 in pair):
                            score += 0.2
                            break
        
        # Equipment compatibility
        if creator1.equipment and creator2.equipment:
            # Similar equipment levels (simplified)
            equipment_overlap = set(creator1.equipment) & set(creator2.equipment)
            equipment_union = set(creator1.equipment) | set(creator2.equipment)
            
            if equipment_union:
                score += (len(equipment_overlap) / len(equipment_union)) * 0.4
        
        # Default compatibility for remote work
        score = max(score, 0.3)
        
        return min(score, 1.0)
    
    def _calculate_schedule_alignment(self,
                                    creator1: CreatorProfile,
                                    creator2: CreatorProfile) -> float:
        """
Calculate schedule compatibility"""
        if not creator1.availability or not creator2.availability:
            return 0.5  # Unknown, assume moderate compatibility
        
        overlap_score = 0.0
        days_checked = 0
        
        for day in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']:
            times1 = creator1.availability.get(day, [])
            times2 = creator2.availability.get(day, [])
            
            if times1 and times2:
                days_checked += 1
                # Simplified overlap calculation
                # In reality, you'd parse time ranges and find actual overlaps
                overlap_hours = self._calculate_time_overlap(times1, times2)
                if overlap_hours > 0:
                    overlap_score += min(overlap_hours / 4.0, 1.0)  # 4+ hours = perfect score for day
        
        if days_checked == 0:
            return 0.5
        
        return overlap_score / days_checked
    
    def _calculate_time_overlap(self, times1: List[str], times2: List[str]) -> float:
        """
Calculate overlapping hours between time ranges"""
        # Simplified implementation - assume format "HH:MM-HH:MM"
        try:
            overlap_minutes = 0
            
            for time_range1 in times1:
                start1, end1 = time_range1.split('-')
                start1_minutes = self._time_to_minutes(start1)
                end1_minutes = self._time_to_minutes(end1)
                
                for time_range2 in times2:
                    start2, end2 = time_range2.split('-')
                    start2_minutes = self._time_to_minutes(start2)
                    end2_minutes = self._time_to_minutes(end2)
                    
                    # Find overlap
                    overlap_start = max(start1_minutes, start2_minutes)
                    overlap_end = min(end1_minutes, end2_minutes)
                    
                    if overlap_end > overlap_start:
                        overlap_minutes += overlap_end - overlap_start
            
            return overlap_minutes / 60.0  # Convert to hours
            
        except Exception:
            return 2.0  # Default assume some overlap
    
    def _time_to_minutes(self, time_str: str) -> int:
        """Convert HH:MM to minutes since midnight"""
        try:
            hours, minutes = map(int, time_str.split(':'))
            return hours * 60 + minutes
        except Exception:
            return 0
    
    def _calculate_collaboration_history_score(self,
                                             creator1: CreatorProfile,
                                             creator2: CreatorProfile) -> float:
        """
Calculate score based on collaboration network"""
        # Check if they've collaborated before
        if creator2.creator_id in creator1.collaboration_history:
            return 1.0  # Perfect if they've worked together
        
        # Check mutual collaborators using graph
        if (self.collaboration_graph.has_node(creator1.creator_id) and 
            self.collaboration_graph.has_node(creator2.creator_id)):
            
            try:
                # Find shortest path (mutual connections)
                path_length = nx.shortest_path_length(
                    self.collaboration_graph,
                    creator1.creator_id,
                    creator2.creator_id
                )
                
                if path_length == 2:  # One mutual collaborator
                    return 0.8
                elif path_length == 3:  # Two degrees of separation
                    return 0.6
                elif path_length <= 4:
                    return 0.4
                
            except nx.NetworkXNoPath:
                pass  # No connection
        
        # Base score for no connection
        return 0.3
    
    def _calculate_budget_compatibility(self,
                                      creator1: CreatorProfile,
                                      creator2: CreatorProfile) -> float:
        """
Calculate budget range compatibility"""
        budget1 = creator1.budget_range
        budget2 = creator2.budget_range
        
        if not budget1 or not budget2:
            return 0.7  # Assume negotiable if not specified
        
        # Check for overlap in budget ranges
        min1, max1 = budget1.get('min', 0), budget1.get('max', float('inf'))
        min2, max2 = budget2.get('min', 0), budget2.get('max', float('inf'))
        
        # Find overlap
        overlap_min = max(min1, min2)
        overlap_max = min(max1, max2)
        
        if overlap_max >= overlap_min:
            # There's overlap
            range1_size = max1 - min1 if max1 != float('inf') else 1000
            range2_size = max2 - min2 if max2 != float('inf') else 1000
            overlap_size = overlap_max - overlap_min
            
            # Score based on how much of each range overlaps
            score1 = overlap_size / range1_size if range1_size > 0 else 1.0
            score2 = overlap_size / range2_size if range2_size > 0 else 1.0
            
            return min((score1 + score2) / 2, 1.0)
        
        else:
            # No overlap - check how close they are
            gap = overlap_min - overlap_max
            avg_budget = (min1 + max1 + min2 + max2) / 4
            
            if gap < avg_budget * 0.2:  # Within 20% of average
                return 0.5
            else:
                return 0.2
    
    def _suggest_collaboration_types(self,
                                   creator1: CreatorProfile,
                                   creator2: CreatorProfile,
                                   compatibility_scores: Dict[MatchingCriteria, float],
                                   original_type: CollaborationType) -> List[CollaborationType]:
        """
Suggest best collaboration types based on compatibility"""
        suggestions = [original_type]  # Always include requested type
        
        # High genre compatibility - good for featuring/duets
        if compatibility_scores.get(MatchingCriteria.GENRE_COMPATIBILITY, 0) > 0.7:
            suggestions.extend([
                CollaborationType.FEATURING,
                CollaborationType.DUET,
                CollaborationType.JOINT_PROJECT
            ])
        
        # High skill level difference - mentorship opportunity
        skill_score = compatibility_scores.get(MatchingCriteria.SKILL_LEVEL, 0.5)
        if skill_score > 0.8:  # Very compatible or very different (for mentorship)
            suggestions.append(CollaborationType.MENTORSHIP)
        
        # High equipment compatibility - production collaboration
        if compatibility_scores.get(MatchingCriteria.EQUIPMENT_COMPATIBILITY, 0) > 0.7:
            suggestions.extend([
                CollaborationType.PRODUCTION,
                CollaborationType.MIXING_MASTERING
            ])
        
        # High audience overlap - cross-promotion
        if compatibility_scores.get(MatchingCriteria.AUDIENCE_OVERLAP, 0) > 0.6:
            suggestions.append(CollaborationType.CROSS_PROMOTION)
        
        # Remote-friendly options for low geographic proximity
        if compatibility_scores.get(MatchingCriteria.GEOGRAPHIC_PROXIMITY, 0) < 0.4:
            suggestions.extend([
                CollaborationType.REMIX,
                CollaborationType.SONGWRITING,
                CollaborationType.CROSS_PROMOTION
            ])
        
        # Remove duplicates and return
        return list(dict.fromkeys(suggestions))
    
    def _generate_collaboration_ideas(self,
                                    creator1: CreatorProfile,
                                    creator2: CreatorProfile,
                                    collaboration_type: CollaborationType) -> List[str]:
        """
Generate specific collaboration ideas"""
        ideas = []
        
        # Genre-specific ideas
        common_genres = set(creator1.genres) & set(creator2.genres)
        if common_genres:
            genre = list(common_genres)[0]
            ideas.append(f"Create a {genre} track that showcases both your styles")
        
        # Creator type specific ideas
        if creator1.creator_type == CreatorType.MUSICIAN and creator2.creator_type == CreatorType.PODCASTER:
            ideas.extend([
                "Create a podcast episode about your music creation process",
                "Compose background music for podcast episodes",
                "Start a music-focused podcast series together"
            ])
        
        elif creator1.creator_type == CreatorType.VOCALIST and creator2.creator_type == CreatorType.PRODUCER:
            ideas.extend([
                "Collaborate on a complete song - vocals over production",
                "Create multiple versions (acoustic, electronic, etc.)",
                "Develop a signature sound together"
            ])
        
        # Collaboration type specific
        if collaboration_type == CollaborationType.REMIX:
            ideas.extend([
                "Remix each other's tracks in your signature styles",
                "Create a remix competition between your audiences",
                "Develop a remix EP together"
            ])
        
        elif collaboration_type == CollaborationType.CROSS_PROMOTION:
            ideas.extend([
                "Feature in each other's social media content",
                "Create joint playlists on streaming platforms",
                "Plan coordinated release campaigns"
            ])
        
        # Default ideas if none generated
        if not ideas:
            ideas.extend([
                f"Combine your unique strengths for a {collaboration_type.value} project",
                "Start with a small collaboration to test creative chemistry",
                "Plan a virtual collaboration session to brainstorm ideas"
            ])
        
        return ideas[:5]  # Limit to top 5 ideas
    
    async def create_collaboration_request(self,
                                         requester_id: str,
                                         target_id: str,
                                         collaboration_type: CollaborationType,
                                         project_details: Dict[str, Any]) -> str:
        """Create a new collaboration request"""
        try:
            request_id = str(uuid.uuid4())
            
            collaboration_request = CollaborationRequest(
                request_id=request_id,
                requester_id=requester_id,
                target_id=target_id,
                collaboration_type=collaboration_type,
                project_title=project_details.get('title', ''),
                project_description=project_details.get('description', ''),
                project_budget=project_details.get('budget'),
                project_timeline=project_details.get('timeline'),
                requirements=project_details.get('requirements', {}),
                compensation=project_details.get('compensation')
            )
            
            # Store in database
            collaboration_record = CollaborationDatabase(
                id=request_id,
                requester_id=requester_id,
                target_id=target_id,
                collaboration_data=json.dumps(collaboration_request.__dict__, default=str),
                status=CollaborationStatus.PROPOSED.value
            )
            
            self.session.add(collaboration_record)
            self.session.commit()
            
            # Send notification (implement notification system)
            await self._send_collaboration_notification(collaboration_request)
            
            logger.info(f"Collaboration request created: {request_id}")
            return request_id
            
        except Exception as e:
            logger.error(f"Collaboration request creation failed: {e}")
            self.session.rollback()
            raise
    
    async def _send_collaboration_notification(self, request: CollaborationRequest):
        """Send notification about collaboration request"""
        # Implement notification system (email, push notifications, etc.)
        logger.info(f"Notification sent for collaboration request {request.request_id}")
    
    async def get_collaboration_recommendations(self,
                                             creator_id: str,
                                             limit: int = 20) -> Dict[str, Any]:
        """Get personalized collaboration recommendations"""
        try:
            # Get creator profile
            creator_db = self.session.query(CreatorDatabase).filter(
                CreatorDatabase.id == creator_id
            ).first()
            
            if not creator_db:
                return {'error': 'Creator not found'}
            
            creator_profile = CreatorProfile(**json.loads(creator_db.profile_data))
            creator_profile.creator_id = creator_id
            
            # Get recommendations for different collaboration types
            recommendations = {}
            
            for collab_type in [CollaborationType.FEATURING, CollaborationType.REMIX, 
                              CollaborationType.JOINT_PROJECT, CollaborationType.CROSS_PROMOTION]:
                matches = await self.find_matches(
                    creator_profile, collab_type, max_matches=5
                )
                
                if matches:
                    recommendations[collab_type.value] = [
                        {
                            'creator_id': match.matched_creator.creator_id,
                            'name': match.matched_creator.name,
                            'creator_type': match.matched_creator.creator_type.value,
                            'compatibility_score': match.compatibility_score,
                            'top_reasons': match.match_reasons[:3],
                            'collaboration_ideas': match.collaboration_ideas[:2]
                        }
                        for match in matches[:3]
                    ]
            
            # Get trending opportunities
            trending_opportunities = await self._get_trending_opportunities(creator_profile)
            
            # Get network recommendations (friends of friends)
            network_recommendations = await self._get_network_recommendations(creator_id)
            
            return {
                'collaboration_matches': recommendations,
                'trending_opportunities': trending_opportunities,
                'network_recommendations': network_recommendations,
                'total_recommendations': sum(len(matches) for matches in recommendations.values())
            }
            
        except Exception as e:
            logger.error(f"Collaboration recommendations failed: {e}")
            return {'error': str(e)}
    
    async def _get_trending_opportunities(self, creator_profile: CreatorProfile) -> List[Dict[str, Any]]:
        """Get trending collaboration opportunities"""
        # This would analyze current trends, popular genres, etc.
        trends = []
        
        # Simulate trend analysis
        if 'pop' in creator_profile.genres:
            trends.append({
                'trend': 'Pop-Electronic Fusion',
                'description': 'Pop artists collaborating with electronic producers',
                'potential_matches': 3,
                'trending_score': 0.85
            })
        
        if 'indie' in creator_profile.genres:
            trends.append({
                'trend': 'Indie Cross-Genre Collaborations',
                'description': 'Indie artists exploring jazz and classical influences',
                'potential_matches': 5,
                'trending_score': 0.78
            })
        
        return trends
    
    async def _get_network_recommendations(self, creator_id: str) -> List[Dict[str, Any]]:
        """
Get recommendations based on collaboration network"""
        network_recs = []
        
        if not self.collaboration_graph.has_node(creator_id):
            return network_recs
        
        # Find creators at distance 2 (friends of friends)
        try:
            for node in self.collaboration_graph.nodes():
                if node != creator_id:
                    try:
                        path_length = nx.shortest_path_length(
                            self.collaboration_graph, creator_id, node
                        )
                        
                        if path_length == 2:  # Friend of friend
                            # Get mutual connections
                            mutual_connections = list(nx.common_neighbors(
                                self.collaboration_graph, creator_id, node
                            ))
                            
                            if mutual_connections:
                                network_recs.append({
                                    'creator_id': node,
                                    'connection_type': 'friend_of_friend',
                                    'mutual_connections': mutual_connections[:3],
                                    'network_score': 0.7
                                })
                        
                    except nx.NetworkXNoPath:
                        continue
            
        except Exception as e:
            logger.error(f"Network analysis failed: {e}")
        
        return network_recs[:5]


# Factory function for creating collaboration system
async def create_collaboration_system(database_url: str, redis_host: str = "localhost") -> AdvancedMatchingEngine:
    """Create configured collaboration matching system"""
    return AdvancedMatchingEngine(database_url, redis_host)


# Utility functions
async def quick_find_collaborators(
    creator_data: Dict[str, Any],
    collaboration_type: str = "featuring",
    database_url: str = "sqlite:///collaborations.db"
) -> List[Dict[str, Any]]:
    """Quick collaborator search"""
    try:
        # Create creator profile
        creator_profile = CreatorProfile(
            creator_id=creator_data.get('id', str(uuid.uuid4())),
            name=creator_data.get('name', ''),
            creator_type=CreatorType(creator_data.get('type', 'musician')),
            email=creator_data.get('email', ''),
            genres=creator_data.get('genres', []),
            skills=creator_data.get('skills', {}),
            location=creator_data.get('location')
        )
        
        # Create matching engine
        engine = AdvancedMatchingEngine(database_url)
        
        # Find matches
        matches = await engine.find_matches(
            creator_profile,
            CollaborationType(collaboration_type),
            max_matches=10
        )
        
        # Return simplified results
        return [
            {
                'name': match.matched_creator.name,
                'type': match.matched_creator.creator_type.value,
                'compatibility': match.compatibility_score,
                'reasons': match.match_reasons[:3],
                'ideas': match.collaboration_ideas[:2]
            }
            for match in matches
        ]
        
    except Exception as e:
        logger.error(f"Quick collaborator search failed: {e}")
        return []
