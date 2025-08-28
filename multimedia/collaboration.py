"""
Professional Creator Collaboration and Intelligent Matching System
Enterprise-grade creator matching with AI-powered collaboration recommendations

Project Team: Lead AI Developer + Backend Senior Engineer + ML Engineer + 
              Database Administrator + Security Expert + Microservices Architect +
              Multimedia Processing Specialist + DevOps Engineer + AI Prompt Engineer

Created by: Fahed Mlaiel <mlaiel@live.de>

⚠️ STRICT COPYRIGHT WARNING ⚠️
This code is proprietary and confidential. Any unauthorized use, reproduction, 
distribution, or modification without written permission from Fahed Mlaiel 
(mlaiel@live.de) is strictly prohibited and will be prosecuted to the full 
extent of the law. All rights reserved.

Contact: mlaiel@live.de for licensing and authorization inquiries.
"""

import asyncio
import logging
import json
import numpy as np
from typing import Dict, List, Optional, Any, Union, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum
from abc import ABC, abstractmethod
import torch
from transformers import AutoTokenizer, AutoModel, pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans
import networkx as nx
from sqlalchemy import select, insert, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.exceptions import CollaborationError, MatchingError
from ..core.config import get_settings
from ..core.database import get_session
from ..utils.caching import cache_result
from ..utils.notifications import NotificationService
from ..utils.recommendations import RecommendationEngine

logger = logging.getLogger(__name__)
settings = get_settings()


class CreatorType(Enum):
    """Types of content creators"""
    MUSICIAN = "musician"
    PHOTOGRAPHER = "photographer"
    VIDEOGRAPHER = "videographer"
    BLOGGER = "blogger"
    INFLUENCER = "influencer"
    COMEDIAN = "comedian"
    PODCASTER = "podcaster"
    ANIMATOR = "animator"
    DESIGNER = "designer"
    WRITER = "writer"
    VOICE_ACTOR = "voice_actor"
    PRODUCER = "producer"


class CollaborationType(Enum):
    """Types of collaboration"""
    CREATIVE_PARTNERSHIP = "creative_partnership"
    SKILL_EXCHANGE = "skill_exchange"
    CONTENT_CREATION = "content_creation"
    CROSS_PROMOTION = "cross_promotion"
    REVENUE_SHARE = "revenue_share"
    LICENSING_DEAL = "licensing_deal"
    MENTORSHIP = "mentorship"
    PROJECT_BASED = "project_based"
    LONG_TERM_PARTNERSHIP = "long_term_partnership"


class SkillLevel(Enum):
    """Skill proficiency levels"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"
    PROFESSIONAL = "professional"


class CollaborationStatus(Enum):
    """Status of collaboration requests"""
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


@dataclass
class CreatorProfile:
    """Comprehensive creator profile"""
    user_id: str
    username: str
    creator_types: List[CreatorType]
    bio: str
    location: Optional[str] = None
    languages: List[str] = field(default_factory=list)
    
    # Skills and expertise
    skills: Dict[str, SkillLevel] = field(default_factory=dict)
    specializations: List[str] = field(default_factory=list)
    genres: List[str] = field(default_factory=list)
    
    # Portfolio and metrics
    portfolio_urls: List[str] = field(default_factory=list)
    total_followers: int = 0
    average_engagement: float = 0.0
    content_quality_score: float = 0.0
    
    # Collaboration preferences
    preferred_collaboration_types: List[CollaborationType] = field(default_factory=list)
    availability_hours: Dict[str, List[str]] = field(default_factory=dict)  # day -> hours
    budget_range: Tuple[Decimal, Decimal] = (Decimal("0"), Decimal("1000"))
    open_to_new_creators: bool = True
    minimum_follower_count: int = 0
    
    # Professional info
    years_of_experience: int = 0
    professional_rate: Optional[Decimal] = None
    timezone: str = "UTC"
    verified: bool = False
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    last_active: datetime = field(default_factory=datetime.utcnow)


@dataclass
class CollaborationRequest:
    """Collaboration request details"""
    request_id: str
    requester_id: str
    target_creator_id: str
    collaboration_type: CollaborationType
    title: str
    description: str
    
    # Project details
    project_timeline: Optional[Tuple[datetime, datetime]] = None
    budget_offered: Optional[Decimal] = None
    revenue_split: Optional[Dict[str, float]] = None
    deliverables: List[str] = field(default_factory=list)
    
    # Requirements
    required_skills: List[str] = field(default_factory=list)
    preferred_experience: Optional[SkillLevel] = None
    location_preference: Optional[str] = None
    
    # Status and metadata
    status: CollaborationStatus = CollaborationStatus.PENDING
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    
    # Messages and negotiations
    messages: List[Dict[str, Any]] = field(default_factory=list)
    contract_terms: Optional[Dict[str, Any]] = None


@dataclass
class MatchScore:
    """Creator matching score details"""
    creator_id: str
    overall_score: float
    compatibility_scores: Dict[str, float] = field(default_factory=dict)
    reasons: List[str] = field(default_factory=list)
    potential_synergies: List[str] = field(default_factory=list)
    collaboration_suggestions: List[CollaborationType] = field(default_factory=list)


@dataclass
class CollaborationOpportunity:
    """Recommended collaboration opportunity"""
    opportunity_id: str
    creators: List[str]  # User IDs
    collaboration_type: CollaborationType
    title: str
    description: str
    estimated_value: Decimal
    success_probability: float
    synergy_score: float
    recommended_timeline: int  # days
    
    # AI-generated insights
    market_analysis: Dict[str, Any] = field(default_factory=dict)
    trend_alignment: List[str] = field(default_factory=list)
    audience_overlap: float = 0.0
    content_complementarity: float = 0.0


class CreatorMatcher:
    """AI-powered creator matching system"""
    
    def __init__(self):
        self.tokenizer = None
        self.model = None
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        self.profile_vectors = {}
        self.creator_graph = nx.Graph()
        
    async def initialize_models(self):
        """Initialize AI models for matching"""
        try:
            # Load sentence transformer for profile embeddings
            self.tokenizer = AutoTokenizer.from_pretrained('sentence-transformers/all-MiniLM-L6-v2')
            self.model = AutoModel.from_pretrained('sentence-transformers/all-MiniLM-L6-v2')
            
            logger.info("Creator matching models initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize matching models: {str(e)}")
            raise MatchingError(f"Model initialization failed: {str(e)}")
    
    async def analyze_creator_profile(self, profile: CreatorProfile) -> Dict[str, Any]:
        """Analyze creator profile and generate embeddings"""
        try:
            if not self.model:
                await self.initialize_models()
            
            # Create profile text for embedding
            profile_text = self._create_profile_text(profile)
            
            # Generate text embedding
            inputs = self.tokenizer(profile_text, return_tensors='pt', padding=True, truncation=True)
            with torch.no_grad():
                outputs = self.model(**inputs)
                embedding = outputs.last_hidden_state.mean(dim=1).squeeze().numpy()
            
            # Calculate profile metrics
            activity_score = await self._calculate_activity_score(profile)
            quality_score = await self._calculate_quality_score(profile)
            collaboration_readiness = await self._assess_collaboration_readiness(profile)
            
            analysis = {
                "profile_embedding": embedding.tolist(),
                "activity_score": activity_score,
                "quality_score": quality_score,
                "collaboration_readiness": collaboration_readiness,
                "skill_diversity": len(profile.skills),
                "specialization_focus": await self._calculate_specialization_focus(profile),
                "market_position": await self._analyze_market_position(profile),
                "growth_potential": await self._estimate_growth_potential(profile)
            }
            
            # Cache the analysis
            self.profile_vectors[profile.user_id] = embedding
            
            return analysis
            
        except Exception as e:
            logger.error(f"Profile analysis failed: {str(e)}")
            raise MatchingError(f"Profile analysis failed: {str(e)}")
    
    def _create_profile_text(self, profile: CreatorProfile) -> str:
        """Create text representation of profile for embedding"""
        text_parts = [
            profile.bio,
            f"Creator types: {', '.join([ct.value for ct in profile.creator_types])}",
            f"Skills: {', '.join(profile.skills.keys())}",
            f"Specializations: {', '.join(profile.specializations)}",
            f"Genres: {', '.join(profile.genres)}",
            f"Experience: {profile.years_of_experience} years",
            f"Location: {profile.location or 'Remote'}",
            f"Languages: {', '.join(profile.languages)}"
        ]
        
        return " ".join(filter(None, text_parts))
    
    async def _calculate_activity_score(self, profile: CreatorProfile) -> float:
        """Calculate creator activity score"""
        try:
            # Time since last activity
            days_since_active = (datetime.utcnow() - profile.last_active).days
            activity_recency = max(0, 1 - (days_since_active / 30))  # Decay over 30 days
            
            # Engagement metrics
            engagement_score = min(1.0, profile.average_engagement / 10.0)  # Normalize to 0-1
            
            # Portfolio completeness
            portfolio_score = min(1.0, len(profile.portfolio_urls) / 5.0)  # Up to 5 URLs
            
            # Combine scores
            activity_score = (activity_recency * 0.4 + engagement_score * 0.4 + portfolio_score * 0.2)
            
            return float(activity_score)
            
        except Exception as e:
            logger.error(f"Activity score calculation failed: {str(e)}")
            return 0.5
    
    async def _calculate_quality_score(self, profile: CreatorProfile) -> float:
        """Calculate content quality score"""
        try:
            # Use existing content quality score if available
            base_quality = profile.content_quality_score
            
            # Adjust based on verification status
            verification_bonus = 0.1 if profile.verified else 0.0
            
            # Experience factor
            experience_factor = min(1.0, profile.years_of_experience / 10.0) * 0.2
            
            # Skill level factor
            skill_levels = [skill.value for skill in profile.skills.values()]
            advanced_skills = sum(1 for level in skill_levels if level in ['advanced', 'expert', 'professional'])
            skill_factor = min(1.0, advanced_skills / len(skill_levels)) * 0.1 if skill_levels else 0.0
            
            quality_score = base_quality + verification_bonus + experience_factor + skill_factor
            
            return min(1.0, float(quality_score))
            
        except Exception as e:
            logger.error(f"Quality score calculation failed: {str(e)}")
            return 0.5
    
    async def _assess_collaboration_readiness(self, profile: CreatorProfile) -> float:
        """Assess how ready creator is for collaboration"""
        try:
            readiness_factors = []
            
            # Open to new creators
            readiness_factors.append(1.0 if profile.open_to_new_creators else 0.5)
            
            # Has collaboration preferences set
            has_preferences = len(profile.preferred_collaboration_types) > 0
            readiness_factors.append(0.8 if has_preferences else 0.3)
            
            # Has availability schedule
            has_schedule = len(profile.availability_hours) > 0
            readiness_factors.append(0.7 if has_schedule else 0.4)
            
            # Professional rate set (indicates serious about collaboration)
            has_rate = profile.professional_rate is not None
            readiness_factors.append(0.6 if has_rate else 0.8)  # Not having rate can be good too
            
            # Budget range set
            has_budget = profile.budget_range[1] > Decimal("0")
            readiness_factors.append(0.5 if has_budget else 0.3)
            
            return float(np.mean(readiness_factors))
            
        except Exception as e:
            logger.error(f"Collaboration readiness assessment failed: {str(e)}")
            return 0.5
    
    async def _calculate_specialization_focus(self, profile: CreatorProfile) -> float:
        """Calculate how specialized vs generalist the creator is"""
        try:
            total_skills = len(profile.skills)
            if total_skills == 0:
                return 0.0
            
            # Count high-level skills
            high_level_skills = sum(
                1 for skill_level in profile.skills.values() 
                if skill_level in [SkillLevel.ADVANCED, SkillLevel.EXPERT, SkillLevel.PROFESSIONAL]
            )
            
            # Specialization is high when few skills but high level
            if total_skills <= 3 and high_level_skills >= 2:
                return 0.8  # Specialist
            elif total_skills <= 5 and high_level_skills >= 3:
                return 0.6  # Focused
            elif total_skills > 8:
                return 0.2  # Generalist
            else:
                return 0.4  # Balanced
                
        except Exception as e:
            logger.error(f"Specialization focus calculation failed: {str(e)}")
            return 0.5
    
    async def _analyze_market_position(self, profile: CreatorProfile) -> str:
        """Analyze creator's market position"""
        try:
            follower_tiers = {
                "micro": (1000, 10000),
                "mid_tier": (10000, 100000),
                "macro": (100000, 1000000),
                "mega": (1000000, float('inf'))
            }
            
            for tier, (min_followers, max_followers) in follower_tiers.items():
                if min_followers <= profile.total_followers < max_followers:
                    return f"{tier}_influencer"
            
            return "emerging_creator"
            
        except Exception as e:
            logger.error(f"Market position analysis failed: {str(e)}")
            return "unknown"
    
    async def _estimate_growth_potential(self, profile: CreatorProfile) -> float:
        """Estimate creator's growth potential"""
        try:
            growth_factors = []
            
            # Engagement rate factor (high engagement = growth potential)
            if profile.total_followers > 0:
                engagement_rate = profile.average_engagement / profile.total_followers * 100
                growth_factors.append(min(1.0, engagement_rate / 5.0))  # 5% is excellent
            
            # Experience vs follower ratio (undervalued creators have high potential)
            if profile.years_of_experience > 0 and profile.total_followers > 0:
                experience_per_follower = profile.total_followers / (profile.years_of_experience * 1000)
                # Lower ratio = undervalued = higher growth potential
                growth_factors.append(max(0.2, 1.0 - min(1.0, experience_per_follower)))
            
            # Skill diversity (more skills = more opportunities)
            skill_diversity = min(1.0, len(profile.skills) / 10.0)
            growth_factors.append(skill_diversity * 0.7)
            
            # Activity score (active creators grow faster)
            activity_score = await self._calculate_activity_score(profile)
            growth_factors.append(activity_score)
            
            return float(np.mean(growth_factors)) if growth_factors else 0.5
            
        except Exception as e:
            logger.error(f"Growth potential estimation failed: {str(e)}")
            return 0.5
    
    async def find_compatible_creators(
        self,
        creator_profile: CreatorProfile,
        collaboration_type: Optional[CollaborationType] = None,
        max_results: int = 20
    ) -> List[MatchScore]:
        """Find compatible creators for collaboration"""
        try:
            if not self.model:
                await self.initialize_models()
            
            # Get all creator profiles
            potential_matches = await self._get_potential_matches(
                creator_profile, collaboration_type
            )
            
            match_scores = []
            
            for candidate in potential_matches:
                try:
                    score = await self._calculate_compatibility_score(
                        creator_profile, candidate, collaboration_type
                    )
                    
                    if score.overall_score >= 0.6:  # Minimum compatibility threshold
                        match_scores.append(score)
                        
                except Exception as e:
                    logger.warning(f"Match scoring failed for candidate {candidate.user_id}: {str(e)}")
                    continue
            
            # Sort by overall score
            match_scores.sort(key=lambda x: x.overall_score, reverse=True)
            
            return match_scores[:max_results]
            
        except Exception as e:
            logger.error(f"Compatible creator search failed: {str(e)}")
            return []
    
    async def _get_potential_matches(
        self,
        creator_profile: CreatorProfile,
        collaboration_type: Optional[CollaborationType]
    ) -> List[CreatorProfile]:
        """Get potential creator matches from database"""
        try:
            async with get_session() as session:
                query = select("creator_profiles").where(
                    "user_id" != creator_profile.user_id,  # Exclude self
                    "open_to_new_creators" == True,  # Open to collaboration
                    "last_active" >= datetime.utcnow() - timedelta(days=90)  # Active in last 90 days
                )
                
                # Filter by collaboration type if specified
                if collaboration_type:
                    query = query.where(
                        "preferred_collaboration_types.like(f'%{collaboration_type.value}%')"
                    )
                
                # Filter by location if specified
                if creator_profile.location:
                    query = query.where(
                        ("location" == creator_profile.location) |
                        ("location" == None)  # Remote creators
                    )
                
                result = await session.execute(query)
                potential_matches = []
                
                for row in result.fetchall():
                    profile_data = dict(row)
                    # Convert to CreatorProfile object
                    profile = CreatorProfile(
                        user_id=profile_data["user_id"],
                        username=profile_data["username"],
                        creator_types=[CreatorType(ct) for ct in json.loads(profile_data.get("creator_types", "[]"))],
                        bio=profile_data["bio"],
                        location=profile_data.get("location"),
                        skills={k: SkillLevel(v) for k, v in json.loads(profile_data.get("skills", "{}")).items()},
                        specializations=json.loads(profile_data.get("specializations", "[]")),
                        total_followers=profile_data.get("total_followers", 0),
                        average_engagement=profile_data.get("average_engagement", 0.0),
                        years_of_experience=profile_data.get("years_of_experience", 0),
                        # ... other fields
                    )
                    potential_matches.append(profile)
                
                return potential_matches
                
        except Exception as e:
            logger.error(f"Failed to get potential matches: {str(e)}")
            return []
    
    async def _calculate_compatibility_score(
        self,
        creator1: CreatorProfile,
        creator2: CreatorProfile,
        collaboration_type: Optional[CollaborationType]
    ) -> MatchScore:
        """Calculate detailed compatibility score between two creators"""
        try:
            compatibility_scores = {}
            reasons = []
            synergies = []
            
            # 1. Skill Complementarity (30%)
            skill_score = await self._calculate_skill_compatibility(creator1, creator2)
            compatibility_scores["skill_compatibility"] = skill_score
            
            if skill_score > 0.7:
                reasons.append("Highly complementary skills")
                synergies.append("Skills create strong synergy for joint projects")
            
            # 2. Audience Overlap/Complementarity (25%)
            audience_score = await self._calculate_audience_compatibility(creator1, creator2)
            compatibility_scores["audience_compatibility"] = audience_score
            
            if audience_score > 0.6:
                reasons.append("Compatible target audiences")
                synergies.append("Audiences can cross-pollinate effectively")
            
            # 3. Experience Level Match (15%)
            experience_score = await self._calculate_experience_compatibility(creator1, creator2)
            compatibility_scores["experience_compatibility"] = experience_score
            
            # 4. Creative Style Alignment (15%)
            style_score = await self._calculate_style_compatibility(creator1, creator2)
            compatibility_scores["style_compatibility"] = style_score
            
            # 5. Practical Compatibility (15%) - budget, schedule, location
            practical_score = await self._calculate_practical_compatibility(creator1, creator2)
            compatibility_scores["practical_compatibility"] = practical_score
            
            if practical_score > 0.8:
                reasons.append("Excellent practical alignment (schedule, budget, location)")
            
            # Calculate weighted overall score
            weights = {
                "skill_compatibility": 0.30,
                "audience_compatibility": 0.25,
                "experience_compatibility": 0.15,
                "style_compatibility": 0.15,
                "practical_compatibility": 0.15
            }
            
            overall_score = sum(
                compatibility_scores[key] * weight 
                for key, weight in weights.items()
            )
            
            # Generate collaboration suggestions
            collaboration_suggestions = await self._suggest_collaboration_types(
                creator1, creator2, compatibility_scores
            )
            
            return MatchScore(
                creator_id=creator2.user_id,
                overall_score=overall_score,
                compatibility_scores=compatibility_scores,
                reasons=reasons,
                potential_synergies=synergies,
                collaboration_suggestions=collaboration_suggestions
            )
            
        except Exception as e:
            logger.error(f"Compatibility score calculation failed: {str(e)}")
            return MatchScore(
                creator_id=creator2.user_id,
                overall_score=0.0,
                compatibility_scores={},
                reasons=["Error in compatibility calculation"],
                potential_synergies=[],
                collaboration_suggestions=[]
            )
    
    async def _calculate_skill_compatibility(
        self,
        creator1: CreatorProfile,
        creator2: CreatorProfile
    ) -> float:
        """Calculate skill compatibility score"""
        try:
            skills1 = set(creator1.skills.keys())
            skills2 = set(creator2.skills.keys())
            
            if not skills1 or not skills2:
                return 0.0
            
            # Complementary skills (different but synergistic)
            complementary_pairs = {
                "music_production": ["vocal_recording", "mixing", "mastering"],
                "photography": ["photo_editing", "video_editing", "graphic_design"],
                "writing": ["editing", "proofreading", "content_strategy"],
                "video_production": ["audio_recording", "color_grading", "motion_graphics"]
            }
            
            complementary_score = 0.0
            total_pairs = 0
            
            for skill1 in skills1:
                for skill2 in skills2:
                    total_pairs += 1
                    if skill1 in complementary_pairs and skill2 in complementary_pairs[skill1]:
                        complementary_score += 1.0
                    elif skill2 in complementary_pairs and skill1 in complementary_pairs[skill2]:
                        complementary_score += 1.0
                    elif skill1 != skill2:  # Different skills are good for diversity
                        complementary_score += 0.3
            
            if total_pairs > 0:
                complementary_score /= total_pairs
            
            # Overlapping skills (can work together on same tasks)
            overlap_skills = skills1 & skills2
            overlap_score = len(overlap_skills) / max(len(skills1), len(skills2))
            
            # Balance complementary and overlap (70% complementary, 30% overlap)
            final_score = complementary_score * 0.7 + overlap_score * 0.3
            
            return min(1.0, final_score)
            
        except Exception as e:
            logger.error(f"Skill compatibility calculation failed: {str(e)}")
            return 0.0
    
    async def _calculate_audience_compatibility(
        self,
        creator1: CreatorProfile,
        creator2: CreatorProfile
    ) -> float:
        """Calculate audience compatibility score"""
        try:
            # Similar follower counts work well together
            follower_ratio = min(creator1.total_followers, creator2.total_followers) / max(
                creator1.total_followers, creator2.total_followers, 1
            )
            
            # Genre overlap indicates similar audiences
            genres1 = set(creator1.genres)
            genres2 = set(creator2.genres)
            
            if genres1 and genres2:
                genre_overlap = len(genres1 & genres2) / len(genres1 | genres2)
            else:
                genre_overlap = 0.0
            
            # Similar engagement rates indicate similar audience quality
            engagement_similarity = 1.0 - abs(creator1.average_engagement - creator2.average_engagement) / max(
                creator1.average_engagement, creator2.average_engagement, 1.0
            )
            
            # Combine factors
            audience_score = (follower_ratio * 0.4 + genre_overlap * 0.4 + engagement_similarity * 0.2)
            
            return float(audience_score)
            
        except Exception as e:
            logger.error(f"Audience compatibility calculation failed: {str(e)}")
            return 0.0
    
    async def _calculate_experience_compatibility(
        self,
        creator1: CreatorProfile,
        creator2: CreatorProfile
    ) -> float:
        """Calculate experience level compatibility"""
        try:
            exp1 = creator1.years_of_experience
            exp2 = creator2.years_of_experience
            
            if exp1 == 0 and exp2 == 0:
                return 1.0  # Both beginners
            
            # Similar experience levels work well together
            exp_diff = abs(exp1 - exp2)
            
            if exp_diff <= 2:
                return 1.0  # Very similar experience
            elif exp_diff <= 5:
                return 0.8  # Somewhat similar
            elif exp_diff <= 10:
                return 0.6  # Different but workable
            else:
                return 0.3  # Very different experience levels
                
        except Exception as e:
            logger.error(f"Experience compatibility calculation failed: {str(e)}")
            return 0.5
    
    async def _calculate_style_compatibility(
        self,
        creator1: CreatorProfile,
        creator2: CreatorProfile
    ) -> float:
        """Calculate creative style compatibility using embeddings"""
        try:
            if creator1.user_id not in self.profile_vectors or creator2.user_id not in self.profile_vectors:
                # Generate embeddings if not available
                await self.analyze_creator_profile(creator1)
                await self.analyze_creator_profile(creator2)
            
            if creator1.user_id in self.profile_vectors and creator2.user_id in self.profile_vectors:
                vec1 = np.array(self.profile_vectors[creator1.user_id])
                vec2 = np.array(self.profile_vectors[creator2.user_id])
                
                # Cosine similarity
                similarity = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
                return float((similarity + 1) / 2)  # Convert from [-1,1] to [0,1]
            
            return 0.5
            
        except Exception as e:
            logger.error(f"Style compatibility calculation failed: {str(e)}")
            return 0.5
    
    async def _calculate_practical_compatibility(
        self,
        creator1: CreatorProfile,
        creator2: CreatorProfile
    ) -> float:
        """Calculate practical compatibility (schedule, budget, location)"""
        try:
            compatibility_factors = []
            
            # Location compatibility
            if creator1.location and creator2.location:
                if creator1.location == creator2.location:
                    compatibility_factors.append(1.0)  # Same location
                else:
                    compatibility_factors.append(0.5)  # Different locations
            else:
                compatibility_factors.append(0.8)  # At least one is remote-friendly
            
            # Budget compatibility
            if creator1.budget_range and creator2.budget_range:
                # Check if budget ranges overlap
                range1_min, range1_max = creator1.budget_range
                range2_min, range2_max = creator2.budget_range
                
                overlap_min = max(range1_min, range2_min)
                overlap_max = min(range1_max, range2_max)
                
                if overlap_max >= overlap_min:
                    overlap_size = overlap_max - overlap_min
                    total_range = max(range1_max, range2_max) - min(range1_min, range2_min)
                    budget_score = overlap_size / total_range if total_range > 0 else 1.0
                    compatibility_factors.append(float(budget_score))
                else:
                    compatibility_factors.append(0.2)  # No budget overlap
            else:
                compatibility_factors.append(0.6)  # One doesn't have budget set
            
            # Schedule compatibility (simplified)
            if creator1.availability_hours and creator2.availability_hours:
                overlapping_days = set(creator1.availability_hours.keys()) & set(creator2.availability_hours.keys())
                if overlapping_days:
                    compatibility_factors.append(0.8)
                else:
                    compatibility_factors.append(0.3)
            else:
                compatibility_factors.append(0.5)  # Unknown schedules
            
            return float(np.mean(compatibility_factors)) if compatibility_factors else 0.5
            
        except Exception as e:
            logger.error(f"Practical compatibility calculation failed: {str(e)}")
            return 0.5
    
    async def _suggest_collaboration_types(
        self,
        creator1: CreatorProfile,
        creator2: CreatorProfile,
        compatibility_scores: Dict[str, float]
    ) -> List[CollaborationType]:
        """Suggest best collaboration types based on compatibility"""
        suggestions = []
        
        try:
            # High skill compatibility suggests content creation or partnerships
            if compatibility_scores.get("skill_compatibility", 0) > 0.7:
                suggestions.extend([
                    CollaborationType.CONTENT_CREATION,
                    CollaborationType.CREATIVE_PARTNERSHIP
                ])
            
            # High audience compatibility suggests cross-promotion
            if compatibility_scores.get("audience_compatibility", 0) > 0.6:
                suggestions.append(CollaborationType.CROSS_PROMOTION)
            
            # Different skill levels suggest mentorship
            exp_diff = abs(creator1.years_of_experience - creator2.years_of_experience)
            if exp_diff >= 5:
                suggestions.append(CollaborationType.MENTORSHIP)
            
            # High practical compatibility suggests long-term partnerships
            if compatibility_scores.get("practical_compatibility", 0) > 0.8:
                suggestions.append(CollaborationType.LONG_TERM_PARTNERSHIP)
            
            # Complementary skills suggest skill exchange
            if compatibility_scores.get("skill_compatibility", 0) > 0.6:
                suggestions.append(CollaborationType.SKILL_EXCHANGE)
            
            # Remove duplicates and return
            return list(set(suggestions))
            
        except Exception as e:
            logger.error(f"Collaboration type suggestion failed: {str(e)}")
            return [CollaborationType.PROJECT_BASED]  # Default suggestion


class CollaborationManager:
    """Manage collaboration requests and projects"""
    
    def __init__(self):
        self.matcher = CreatorMatcher()
        self.notification_service = NotificationService()
        
    async def create_collaboration_request(
        self,
        requester_profile: CreatorProfile,
        target_creator_id: str,
        collaboration_details: Dict[str, Any]
    ) -> CollaborationRequest:
        """Create a new collaboration request"""
        try:
            request_id = f"collab_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{requester_profile.user_id[:8]}"
            
            # Validate target creator exists and is available for collaboration
            target_profile = await self._get_creator_profile(target_creator_id)
            if not target_profile or not target_profile.open_to_new_creators:
                raise CollaborationError("Target creator is not available for collaboration")
            
            # Create collaboration request
            request = CollaborationRequest(
                request_id=request_id,
                requester_id=requester_profile.user_id,
                target_creator_id=target_creator_id,
                collaboration_type=CollaborationType(collaboration_details["type"]),
                title=collaboration_details["title"],
                description=collaboration_details["description"],
                budget_offered=Decimal(str(collaboration_details.get("budget", 0))),
                deliverables=collaboration_details.get("deliverables", []),
                required_skills=collaboration_details.get("required_skills", []),
                expires_at=datetime.utcnow() + timedelta(days=7)  # Default 7-day expiry
            )
            
            # Store in database
            await self._store_collaboration_request(request)
            
            # Send notification to target creator
            await self.notification_service.send_collaboration_request_notification(
                target_creator_id, request
            )
            
            logger.info(f"Collaboration request {request_id} created successfully")
            return request
            
        except Exception as e:
            logger.error(f"Failed to create collaboration request: {str(e)}")
            raise CollaborationError(f"Request creation failed: {str(e)}")
    
    async def respond_to_collaboration_request(
        self,
        request_id: str,
        response: str,  # "accept", "reject", "negotiate"
        response_data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Respond to a collaboration request"""
        try:
            request = await self._get_collaboration_request(request_id)
            if not request:
                raise CollaborationError("Collaboration request not found")
            
            if request.status != CollaborationStatus.PENDING:
                raise CollaborationError("Request is no longer pending")
            
            response_data = response_data or {}
            
            if response == "accept":
                request.status = CollaborationStatus.ACCEPTED
                # Create collaboration project
                project_id = await self._create_collaboration_project(request)
                
                # Notify requester
                await self.notification_service.send_collaboration_accepted_notification(
                    request.requester_id, request, project_id
                )
                
            elif response == "reject":
                request.status = CollaborationStatus.REJECTED
                
                # Notify requester
                await self.notification_service.send_collaboration_rejected_notification(
                    request.requester_id, request, response_data.get("reason", "")
                )
                
            elif response == "negotiate":
                # Add negotiation message
                negotiation_message = {
                    "sender_id": request.target_creator_id,
                    "message": response_data.get("message", ""),
                    "counter_offer": response_data.get("counter_offer", {}),
                    "timestamp": datetime.utcnow().isoformat()
                }
                request.messages.append(negotiation_message)
                
                # Notify requester
                await self.notification_service.send_collaboration_negotiation_notification(
                    request.requester_id, request, negotiation_message
                )
            
            # Update request in database
            await self._update_collaboration_request(request)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to respond to collaboration request: {str(e)}")
            raise CollaborationError(f"Response failed: {str(e)}")
    
    async def discover_collaboration_opportunities(
        self,
        creator_profile: CreatorProfile,
        max_opportunities: int = 10
    ) -> List[CollaborationOpportunity]:
        """Discover AI-generated collaboration opportunities"""
        try:
            opportunities = []
            
            # Find compatible creators
            compatible_creators = await self.matcher.find_compatible_creators(
                creator_profile, max_results=50
            )
            
            # Generate collaboration opportunities
            for match in compatible_creators[:max_opportunities]:
                try:
                    opportunity = await self._generate_collaboration_opportunity(
                        creator_profile, match
                    )
                    if opportunity:
                        opportunities.append(opportunity)
                except Exception as e:
                    logger.warning(f"Failed to generate opportunity for {match.creator_id}: {str(e)}")
                    continue
            
            # Sort by success probability and value
            opportunities.sort(
                key=lambda x: (x.success_probability * float(x.estimated_value)),
                reverse=True
            )
            
            return opportunities
            
        except Exception as e:
            logger.error(f"Collaboration opportunity discovery failed: {str(e)}")
            return []
    
    async def _generate_collaboration_opportunity(
        self,
        creator_profile: CreatorProfile,
        match: MatchScore
    ) -> Optional[CollaborationOpportunity]:
        """Generate a specific collaboration opportunity"""
        try:
            target_profile = await self._get_creator_profile(match.creator_id)
            if not target_profile:
                return None
            
            # Choose best collaboration type
            collaboration_type = match.collaboration_suggestions[0] if match.collaboration_suggestions else CollaborationType.PROJECT_BASED
            
            # Generate opportunity details
            opportunity_id = f"opp_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{creator_profile.user_id[:4]}{match.creator_id[:4]}"
            
            # Estimate project value based on creator metrics
            estimated_value = await self._estimate_collaboration_value(
                creator_profile, target_profile, collaboration_type
            )
            
            # Calculate success probability based on compatibility
            success_probability = min(0.95, match.overall_score * 1.2)  # Cap at 95%
            
            # Generate title and description
            title, description = await self._generate_opportunity_content(
                creator_profile, target_profile, collaboration_type
            )
            
            opportunity = CollaborationOpportunity(
                opportunity_id=opportunity_id,
                creators=[creator_profile.user_id, match.creator_id],
                collaboration_type=collaboration_type,
                title=title,
                description=description,
                estimated_value=estimated_value,
                success_probability=success_probability,
                synergy_score=match.overall_score,
                recommended_timeline=await self._estimate_timeline(collaboration_type),
                audience_overlap=match.compatibility_scores.get("audience_compatibility", 0.0),
                content_complementarity=match.compatibility_scores.get("skill_compatibility", 0.0)
            )
            
            return opportunity
            
        except Exception as e:
            logger.error(f"Opportunity generation failed: {str(e)}")
            return None
    
    async def _estimate_collaboration_value(
        self,
        creator1: CreatorProfile,
        creator2: CreatorProfile,
        collaboration_type: CollaborationType
    ) -> Decimal:
        """Estimate the financial value of a collaboration"""
        try:
            # Base value on combined follower count and engagement
            combined_reach = creator1.total_followers + creator2.total_followers
            avg_engagement = (creator1.average_engagement + creator2.average_engagement) / 2
            
            # Collaboration type multipliers
            type_multipliers = {
                CollaborationType.CREATIVE_PARTNERSHIP: 1.5,
                CollaborationType.CONTENT_CREATION: 1.2,
                CollaborationType.CROSS_PROMOTION: 1.0,
                CollaborationType.REVENUE_SHARE: 2.0,
                CollaborationType.LICENSING_DEAL: 1.8,
                CollaborationType.LONG_TERM_PARTNERSHIP: 2.5,
                CollaborationType.PROJECT_BASED: 1.0,
                CollaborationType.SKILL_EXCHANGE: 0.8,
                CollaborationType.MENTORSHIP: 0.5
            }
            
            multiplier = type_multipliers.get(collaboration_type, 1.0)
            
            # Estimate based on industry standards
            # Rough calculation: $1-5 per engaged follower for collaborations
            engagement_value = combined_reach * (avg_engagement / 100) * 3  # $3 per engaged follower
            estimated_value = Decimal(str(engagement_value * multiplier))
            
            # Cap the value at reasonable limits
            return min(estimated_value, Decimal("50000.00"))
            
        except Exception as e:
            logger.error(f"Value estimation failed: {str(e)}")
            return Decimal("1000.00")
    
    async def _generate_opportunity_content(
        self,
        creator1: CreatorProfile,
        creator2: CreatorProfile,
        collaboration_type: CollaborationType
    ) -> Tuple[str, str]:
        """Generate title and description for collaboration opportunity"""
        try:
            # Get creator types
            type1 = creator1.creator_types[0].value if creator1.creator_types else "creator"
            type2 = creator2.creator_types[0].value if creator2.creator_types else "creator"
            
            # Generate titles based on collaboration type
            title_templates = {
                CollaborationType.CREATIVE_PARTNERSHIP: f"{type1.title()} x {type2.title()} Creative Partnership",
                CollaborationType.CONTENT_CREATION: f"Joint Content Creation: {type1.title()} + {type2.title()}",
                CollaborationType.CROSS_PROMOTION: f"Cross-Promotion Opportunity: {creator1.username} x {creator2.username}",
                CollaborationType.SKILL_EXCHANGE: f"Skill Exchange: {type1.title()} ↔ {type2.title()}",
                CollaborationType.MENTORSHIP: f"Mentorship Program: {type1.title()} → {type2.title()}",
                CollaborationType.PROJECT_BASED: f"Collaborative Project: {type1.title()} & {type2.title()}"
            }
            
            title = title_templates.get(
                collaboration_type, 
                f"Collaboration Opportunity: {creator1.username} x {creator2.username}"
            )
            
            # Generate description
            skill_synergies = []
            creator1_skills = list(creator1.skills.keys())[:3]
            creator2_skills = list(creator2.skills.keys())[:3]
            
            description = f"Exciting collaboration opportunity between {creator1.username} ({type1}) and {creator2.username} ({type2}). "
            
            if creator1_skills and creator2_skills:
                description += f"Combining {', '.join(creator1_skills)} with {', '.join(creator2_skills)} "
                description += f"creates unique synergies for {collaboration_type.value.replace('_', ' ')}."
            
            # Add audience benefit
            if creator1.total_followers > 0 or creator2.total_followers > 0:
                total_reach = creator1.total_followers + creator2.total_followers
                description += f" Combined reach of {total_reach:,} followers with complementary audiences."
            
            return title, description
            
        except Exception as e:
            logger.error(f"Content generation failed: {str(e)}")
            return "Collaboration Opportunity", "Join forces for an exciting creative partnership."
    
    async def _estimate_timeline(self, collaboration_type: CollaborationType) -> int:
        """Estimate timeline in days for collaboration type"""
        timelines = {
            CollaborationType.CREATIVE_PARTNERSHIP: 90,
            CollaborationType.CONTENT_CREATION: 30,
            CollaborationType.CROSS_PROMOTION: 14,
            CollaborationType.SKILL_EXCHANGE: 60,
            CollaborationType.REVENUE_SHARE: 180,
            CollaborationType.LICENSING_DEAL: 7,
            CollaborationType.MENTORSHIP: 120,
            CollaborationType.PROJECT_BASED: 45,
            CollaborationType.LONG_TERM_PARTNERSHIP: 365
        }
        
        return timelines.get(collaboration_type, 30)
    
    async def _get_creator_profile(self, user_id: str) -> Optional[CreatorProfile]:
        """Get creator profile from database"""
        try:
            async with get_session() as session:
                stmt = select("creator_profiles").where("user_id" == user_id)
                result = await session.execute(stmt)
                row = result.fetchone()
                
                if row:
                    data = dict(row)
                    return CreatorProfile(
                        user_id=data["user_id"],
                        username=data["username"],
                        creator_types=[CreatorType(ct) for ct in json.loads(data.get("creator_types", "[]"))],
                        bio=data["bio"],
                        # ... populate other fields
                    )
                
                return None
                
        except Exception as e:
            logger.error(f"Failed to get creator profile: {str(e)}")
            return None
    
    async def _store_collaboration_request(self, request: CollaborationRequest):
        """Store collaboration request in database"""
        try:
            async with get_session() as session:
                request_data = {
                    "request_id": request.request_id,
                    "requester_id": request.requester_id,
                    "target_creator_id": request.target_creator_id,
                    "collaboration_type": request.collaboration_type.value,
                    "title": request.title,
                    "description": request.description,
                    "budget_offered": str(request.budget_offered) if request.budget_offered else None,
                    "deliverables": json.dumps(request.deliverables),
                    "required_skills": json.dumps(request.required_skills),
                    "status": request.status.value,
                    "created_at": request.created_at,
                    "expires_at": request.expires_at
                }
                
                stmt = insert("collaboration_requests").values(**request_data)
                await session.execute(stmt)
                await session.commit()
                
        except Exception as e:
            logger.error(f"Failed to store collaboration request: {str(e)}")
            raise
    
    async def _get_collaboration_request(self, request_id: str) -> Optional[CollaborationRequest]:
        """Get collaboration request from database"""
        try:
            async with get_session() as session:
                stmt = select("collaboration_requests").where("request_id" == request_id)
                result = await session.execute(stmt)
                row = result.fetchone()
                
                if row:
                    data = dict(row)
                    return CollaborationRequest(
                        request_id=data["request_id"],
                        requester_id=data["requester_id"],
                        target_creator_id=data["target_creator_id"],
                        collaboration_type=CollaborationType(data["collaboration_type"]),
                        title=data["title"],
                        description=data["description"],
                        status=CollaborationStatus(data["status"]),
                        # ... populate other fields
                    )
                
                return None
                
        except Exception as e:
            logger.error(f"Failed to get collaboration request: {str(e)}")
            return None
    
    async def _update_collaboration_request(self, request: CollaborationRequest):
        """Update collaboration request in database"""
        try:
            async with get_session() as session:
                stmt = update("collaboration_requests").where(
                    "request_id" == request.request_id
                ).values(
                    status=request.status.value,
                    messages=json.dumps([msg for msg in request.messages]),
                    updated_at=datetime.utcnow()
                )
                await session.execute(stmt)
                await session.commit()
                
        except Exception as e:
            logger.error(f"Failed to update collaboration request: {str(e)}")
            raise
    
    async def _create_collaboration_project(self, request: CollaborationRequest) -> str:
        """Create a collaboration project from accepted request"""
        try:
            project_id = f"proj_{request.request_id}"
            
            # Store project details in database
            async with get_session() as session:
                project_data = {
                    "project_id": project_id,
                    "collaboration_request_id": request.request_id,
                    "participants": json.dumps([request.requester_id, request.target_creator_id]),
                    "project_title": request.title,
                    "project_description": request.description,
                    "status": "active",
                    "created_at": datetime.utcnow()
                }
                
                stmt = insert("collaboration_projects").values(**project_data)
                await session.execute(stmt)
                await session.commit()
            
            return project_id
            
        except Exception as e:
            logger.error(f"Failed to create collaboration project: {str(e)}")
            raise
