"""
Collaboration Matcher - Intelligent Creator Collaboration Matching System

Advanced AI-powered system for identifying optimal creator collaboration
opportunities with compatibility analysis, project matching, and networking.

Author: Fahed Mlaiel <mlaiel@live.de>
"""

import asyncio
import logging
import json
from typing import Dict, List, Optional, Any, Tuple, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import numpy as np

try:
    from core.config import settings
except ImportError:
    # Fallback settings
    settings = type('Settings', (), {'debug': True, 'log_level': 'INFO'})()
try:
    from core.exceptions import CollaborationMatchingError
except ImportError:
    # Fallback exception classes
    class ValidationError(Exception): pass
    class ConfigurationError(Exception): pass
    class ProcessingError(Exception): pass
    CollaborationMatchingError = globals().get('CollaborationMatchingError', Exception)
from ...ml.similarity_models import CreatorSimilarityAnalyzer, ContentSimilarityAnalyzer
from ...utils.performance_metrics import PerformanceMetrics
from ...business.networking import NetworkingManager

logger = logging.getLogger(__name__)

class CollaborationType(Enum):
    """Types of creator collaborations"""
    CONTENT_COLLABORATION = "content_collaboration"
    CROSS_PROMOTION = "cross_promotion"
    JOINT_PROJECT = "joint_project"
    SKILL_EXCHANGE = "skill_exchange"
    MENTORSHIP = "mentorship"
    BRAND_PARTNERSHIP = "brand_partnership"
    EVENT_COLLABORATION = "event_collaboration"
    TECHNICAL_SUPPORT = "technical_support"

class CompatibilityFactor(Enum):
    """Factors influencing collaboration compatibility"""
    CONTENT_STYLE = "content_style"
    AUDIENCE_OVERLAP = "audience_overlap"
    SKILL_COMPLEMENTARITY = "skill_complementarity"
    SCHEDULE_COMPATIBILITY = "schedule_compatibility"
    COMMUNICATION_STYLE = "communication_style"
    PROFESSIONAL_LEVEL = "professional_level"
    GEOGRAPHIC_PROXIMITY = "geographic_proximity"
    BRAND_ALIGNMENT = "brand_alignment"
    PLATFORM_SYNERGY = "platform_synergy"

class MatchingPriority(Enum):
    """Priority levels for collaboration matching"""
    URGENT = "urgent"       # Immediate opportunities
    HIGH = "high"          # Strong potential matches
    MEDIUM = "medium"      # Good potential matches
    LOW = "low"           # Possible matches
    EXPLORATORY = "exploratory"  # Research/learning opportunities

@dataclass
class CreatorProfile:
    """Comprehensive creator profile for matching"""
    user_id: str
    creator_type: str
    
    # Basic Information
    username: str = ""
    display_name: str = ""
    location: Dict[str, Any] = field(default_factory=dict)
    timezone: str = ""
    
    # Content Information
    content_categories: List[str] = field(default_factory=list)
    content_formats: List[str] = field(default_factory=list)
    content_style: Dict[str, float] = field(default_factory=dict)
    quality_metrics: Dict[str, float] = field(default_factory=dict)
    
    # Platform Presence
    platforms: List[str] = field(default_factory=list)
    follower_counts: Dict[str, int] = field(default_factory=dict)
    engagement_rates: Dict[str, float] = field(default_factory=dict)
    
    # Professional Information
    experience_level: str = "beginner"  # beginner, intermediate, advanced, expert
    skills: List[str] = field(default_factory=list)
    equipment: List[str] = field(default_factory=list)
    budget_range: str = "low"  # low, medium, high, premium
    
    # Collaboration Preferences
    collaboration_interests: List[CollaborationType] = field(default_factory=list)
    preferred_collaboration_frequency: str = "occasional"
    availability_schedule: Dict[str, List[str]] = field(default_factory=dict)
    
    # Communication Preferences
    preferred_communication: List[str] = field(default_factory=list)
    language_preferences: List[str] = field(default_factory=list)
    
    # Goals and Objectives
    short_term_goals: List[str] = field(default_factory=list)
    long_term_goals: List[str] = field(default_factory=list)
    target_audience: Dict[str, Any] = field(default_factory=dict)
    
    # Metadata
    profile_completeness: float = 0.0
    last_updated: datetime = field(default_factory=datetime.utcnow)
    verification_status: str = "unverified"

@dataclass
class CollaborationMatch:
    """Detailed collaboration match result"""
    primary_creator_id: str
    matched_creator_id: str
    
    # Match Quality
    overall_compatibility_score: float = 0.0
    match_confidence: float = 0.0
    match_priority: MatchingPriority = MatchingPriority.MEDIUM
    
    # Compatibility Breakdown
    compatibility_scores: Dict[CompatibilityFactor, float] = field(default_factory=dict)
    compatibility_details: Dict[str, Any] = field(default_factory=dict)
    
    # Collaboration Opportunities
    recommended_collaboration_types: List[CollaborationType] = field(default_factory=list)
    collaboration_potential: Dict[CollaborationType, float] = field(default_factory=dict)
    
    # Mutual Benefits
    benefits_for_primary: List[str] = field(default_factory=list)
    benefits_for_matched: List[str] = field(default_factory=list)
    mutual_benefits: List[str] = field(default_factory=list)
    
    # Collaboration Details
    estimated_synergy_boost: float = 0.0
    audience_growth_potential: float = 0.0
    skill_development_opportunities: List[str] = field(default_factory=list)
    
    # Practical Information
    communication_recommendations: List[str] = field(default_factory=list)
    project_suggestions: List[str] = field(default_factory=list)
    timeline_recommendations: Dict[str, str] = field(default_factory=dict)
    
    # Risk Assessment
    potential_challenges: List[str] = field(default_factory=list)
    risk_factors: Dict[str, float] = field(default_factory=dict)
    mitigation_strategies: List[str] = field(default_factory=list)
    
    # Metadata
    match_timestamp: datetime = field(default_factory=datetime.utcnow)
    match_version: str = "2.1.0"
    expiry_date: datetime = field(default_factory=lambda: datetime.utcnow() + timedelta(days=30))

class CollaborationMatcher:
    """
    Advanced AI-powered creator collaboration matching system.
    
    Core Capabilities:
    - Multi-dimensional compatibility analysis
    - Content style and quality matching
    - Audience overlap and synergy analysis
    - Skill complementarity assessment
    - Schedule and communication compatibility
    - Geographic and timezone considerations
    - Brand alignment evaluation
    - Platform synergy optimization
    - Collaboration opportunity identification
    - Risk assessment and mitigation
    - Personalized recommendation generation
    """
    
    def __init__(self):
        # Initialize AI matching models
        self.creator_similarity_analyzer = CreatorSimilarityAnalyzer()
        self.content_similarity_analyzer = ContentSimilarityAnalyzer()
        
        # Business logic components
        self.networking_manager = NetworkingManager()
        
        # Performance tracking
        self.performance_metrics = PerformanceMetrics()
        
        # Matching algorithms configuration
        self.matching_weights = self._initialize_matching_weights()
        
        # Collaboration templates
        self.collaboration_templates = self._initialize_collaboration_templates()
        
        logger.info("CollaborationMatcher initialized successfully")
    
    def _initialize_matching_weights(self) -> Dict[str, Dict[CompatibilityFactor, float]]:
        """Initialize compatibility factor weights by collaboration type."""
        return {
            CollaborationType.CONTENT_COLLABORATION.value: {
                CompatibilityFactor.CONTENT_STYLE: 0.25,
                CompatibilityFactor.AUDIENCE_OVERLAP: 0.20,
                CompatibilityFactor.SKILL_COMPLEMENTARITY: 0.15,
                CompatibilityFactor.PROFESSIONAL_LEVEL: 0.15,
                CompatibilityFactor.PLATFORM_SYNERGY: 0.10,
                CompatibilityFactor.SCHEDULE_COMPATIBILITY: 0.08,
                CompatibilityFactor.COMMUNICATION_STYLE: 0.04,
                CompatibilityFactor.BRAND_ALIGNMENT: 0.03
            },
            CollaborationType.CROSS_PROMOTION.value: {
                CompatibilityFactor.AUDIENCE_OVERLAP: 0.30,
                CompatibilityFactor.PLATFORM_SYNERGY: 0.25,
                CompatibilityFactor.BRAND_ALIGNMENT: 0.15,
                CompatibilityFactor.CONTENT_STYLE: 0.12,
                CompatibilityFactor.PROFESSIONAL_LEVEL: 0.10,
                CompatibilityFactor.COMMUNICATION_STYLE: 0.05,
                CompatibilityFactor.SCHEDULE_COMPATIBILITY: 0.03
            },
            CollaborationType.SKILL_EXCHANGE.value: {
                CompatibilityFactor.SKILL_COMPLEMENTARITY: 0.35,
                CompatibilityFactor.PROFESSIONAL_LEVEL: 0.20,
                CompatibilityFactor.COMMUNICATION_STYLE: 0.15,
                CompatibilityFactor.SCHEDULE_COMPATIBILITY: 0.12,
                CompatibilityFactor.GEOGRAPHIC_PROXIMITY: 0.08,
                CompatibilityFactor.CONTENT_STYLE: 0.05,
                CompatibilityFactor.AUDIENCE_OVERLAP: 0.05
            },
            CollaborationType.MENTORSHIP.value: {
                CompatibilityFactor.PROFESSIONAL_LEVEL: 0.40,
                CompatibilityFactor.SKILL_COMPLEMENTARITY: 0.25,
                CompatibilityFactor.COMMUNICATION_STYLE: 0.15,
                CompatibilityFactor.CONTENT_STYLE: 0.10,
                CompatibilityFactor.SCHEDULE_COMPATIBILITY: 0.10
            }
        }
    
    def _initialize_collaboration_templates(self) -> Dict[CollaborationType, Dict[str, Any]]:
        """Initialize collaboration project templates."""
        return {
            CollaborationType.CONTENT_COLLABORATION: {
                'typical_duration': '2-4 weeks',
                'required_interactions': 'high',
                'success_metrics': ['content_quality', 'audience_engagement', 'cross_pollination'],
                'common_deliverables': ['joint_content', 'social_posts', 'cross_promotion']
            },
            CollaborationType.CROSS_PROMOTION: {
                'typical_duration': '1-2 weeks',
                'required_interactions': 'medium',
                'success_metrics': ['reach_expansion', 'follower_growth', 'engagement_rate'],
                'common_deliverables': ['promotional_posts', 'story_features', 'mention_exchanges']
            },
            CollaborationType.SKILL_EXCHANGE: {
                'typical_duration': '1-3 months',
                'required_interactions': 'high',
                'success_metrics': ['skill_improvement', 'knowledge_transfer', 'technique_mastery'],
                'common_deliverables': ['tutorial_content', 'process_documentation', 'skill_demonstrations']
            },
            CollaborationType.MENTORSHIP: {
                'typical_duration': '3-6 months',
                'required_interactions': 'regular',
                'success_metrics': ['mentee_growth', 'goal_achievement', 'skill_development'],
                'common_deliverables': ['progress_reviews', 'guidance_sessions', 'development_milestones']
            }
        }
    
    async def find_collaboration_matches(self, creator_id: str,
                                       collaboration_types: List[CollaborationType] = None,
                                       max_matches: int = 10,
                                       min_compatibility_score: float = 0.6) -> List[CollaborationMatch]:
        """
        Find optimal collaboration matches for a creator.
        """
        try:
            # Get creator profile
            creator_profile = await self._get_creator_profile(creator_id)
            
            if not creator_profile:
                raise CollaborationMatchingError(f"Creator profile not found for {creator_id}")
            
            # Get potential match candidates
            candidates = await self._get_match_candidates(creator_profile, collaboration_types)
            
            # Perform detailed matching analysis
            matches = []
            for candidate in candidates:
                match = await self._analyze_collaboration_compatibility(
                    creator_profile, candidate, collaboration_types
                )
                
                if match and match.overall_compatibility_score >= min_compatibility_score:
                    matches.append(match)
            
            # Sort by compatibility score and priority
            matches.sort(key=lambda x: (x.match_priority.value, x.overall_compatibility_score), reverse=True)
            
            # Limit results
            final_matches = matches[:max_matches]
            
            # Track performance
            self.performance_metrics.record_matching_session(
                creator_id, len(candidates), len(final_matches)
            )
            
            logger.info(f"Found {len(final_matches)} collaboration matches for creator {creator_id}")
            return final_matches
            
        except Exception as e:
            logger.error(f"Error finding collaboration matches: {str(e)}")
            raise CollaborationMatchingError(f"Match finding failed: {str(e)}")
    
    async def batch_match_creators(self, creator_ids: List[str],
                                 collaboration_types: List[CollaborationType] = None,
                                 concurrent_limit: int = 3) -> Dict[str, List[CollaborationMatch]]:
        """
        Perform batch collaboration matching for multiple creators.
        """
        try:
            semaphore = asyncio.Semaphore(concurrent_limit)
            
            async def match_single(creator_id):
                async with semaphore:
                    return await self.find_collaboration_matches(
                        creator_id, collaboration_types
                    )
            
            # Process all creators concurrently
            tasks = [match_single(creator_id) for creator_id in creator_ids]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Compile results
            batch_results = {}
            for i, creator_id in enumerate(creator_ids):
                if isinstance(results[i], Exception):
                    logger.error(f"Error matching creator {creator_id}: {str(results[i])}")
                    batch_results[creator_id] = []
                else:
                    batch_results[creator_id] = results[i]
            
            logger.info(f"Batch matching completed for {len(creator_ids)} creators")
            return batch_results
            
        except Exception as e:
            logger.error(f"Error in batch matching: {str(e)}")
            raise CollaborationMatchingError(f"Batch matching failed: {str(e)}")
    
    async def _get_creator_profile(self, creator_id: str) -> Optional[CreatorProfile]:
        """Retrieve comprehensive creator profile."""
        try:
            # This would typically fetch from database and AI analysis
            # Simulated implementation
            
            profile = CreatorProfile(
                user_id=creator_id,
                creator_type="musician",  # Would be fetched from DB
                username=f"creator_{creator_id}",
                display_name=f"Creator {creator_id}",
                location={"city": "Berlin", "country": "Germany"},
                timezone="Europe/Berlin",
                content_categories=["music", "entertainment"],
                content_formats=["audio", "video"],
                platforms=["spotify", "youtube", "instagram"],
                experience_level="intermediate",
                skills=["music_production", "audio_mixing", "content_creation"],
                collaboration_interests=[
                    CollaborationType.CONTENT_COLLABORATION,
                    CollaborationType.SKILL_EXCHANGE
                ],
                short_term_goals=["increase_followers", "improve_quality"],
                profile_completeness=0.8
            )
            
            return profile
            
        except Exception as e:
            logger.error(f"Error retrieving creator profile: {str(e)}")
            return None
    
    async def _get_match_candidates(self, creator_profile: CreatorProfile,
                                  collaboration_types: List[CollaborationType] = None) -> List[CreatorProfile]:
        """Get potential collaboration candidates."""
        try:
            # This would typically query database with intelligent filtering
            # Simulated implementation with various candidate profiles
            
            candidates = []
            
            # Generate diverse candidate profiles for demonstration
            candidate_data = [
                {
                    "user_id": "candidate_001",
                    "creator_type": "video_creator",
                    "content_categories": ["music", "tutorial"],
                    "platforms": ["youtube", "tiktok"],
                    "experience_level": "advanced",
                    "skills": ["video_editing", "storytelling"]
                },
                {
                    "user_id": "candidate_002", 
                    "creator_type": "musician",
                    "content_categories": ["music", "acoustic"],
                    "platforms": ["spotify", "soundcloud"],
                    "experience_level": "intermediate",
                    "skills": ["guitar", "songwriting"]
                },
                {
                    "user_id": "candidate_003",
                    "creator_type": "influencer",
                    "content_categories": ["lifestyle", "music"],
                    "platforms": ["instagram", "tiktok"],
                    "experience_level": "expert",
                    "skills": ["photography", "brand_partnerships"]
                }
            ]
            
            for data in candidate_data:
                candidate = CreatorProfile(
                    user_id=data["user_id"],
                    creator_type=data["creator_type"],
                    username=f"user_{data['user_id']}",
                    content_categories=data["content_categories"],
                    platforms=data["platforms"],
                    experience_level=data["experience_level"],
                    skills=data["skills"],
                    profile_completeness=0.7
                )
                candidates.append(candidate)
            
            # Apply initial filtering based on collaboration types
            if collaboration_types:
                filtered_candidates = []
                for candidate in candidates:
                    if any(collab_type in candidate.collaboration_interests or 
                          len(candidate.collaboration_interests) == 0 
                          for collab_type in collaboration_types):
                        filtered_candidates.append(candidate)
                candidates = filtered_candidates
            
            logger.info(f"Found {len(candidates)} potential candidates")
            return candidates
            
        except Exception as e:
            logger.error(f"Error getting match candidates: {str(e)}")
            return []
    
    async def _analyze_collaboration_compatibility(self, creator_profile: CreatorProfile,
                                                 candidate_profile: CreatorProfile,
                                                 collaboration_types: List[CollaborationType] = None) -> Optional[CollaborationMatch]:
        """Perform detailed compatibility analysis between two creators."""
        try:
            match = CollaborationMatch(
                primary_creator_id=creator_profile.user_id,
                matched_creator_id=candidate_profile.user_id
            )
            
            # Analyze each compatibility factor
            await self._analyze_content_style_compatibility(match, creator_profile, candidate_profile)
            await self._analyze_audience_overlap(match, creator_profile, candidate_profile)
            await self._analyze_skill_complementarity(match, creator_profile, candidate_profile)
            await self._analyze_schedule_compatibility(match, creator_profile, candidate_profile)
            await self._analyze_communication_compatibility(match, creator_profile, candidate_profile)
            await self._analyze_professional_level_compatibility(match, creator_profile, candidate_profile)
            await self._analyze_geographic_compatibility(match, creator_profile, candidate_profile)
            await self._analyze_brand_alignment(match, creator_profile, candidate_profile)
            await self._analyze_platform_synergy(match, creator_profile, candidate_profile)
            
            # Calculate overall compatibility score
            self._calculate_overall_compatibility(match, collaboration_types)
            
            # Determine match priority
            self._determine_match_priority(match)
            
            # Generate collaboration recommendations
            await self._generate_collaboration_recommendations(match, creator_profile, candidate_profile)
            
            # Assess risks and benefits
            await self._assess_collaboration_risks_benefits(match, creator_profile, candidate_profile)
            
            return match
            
        except Exception as e:
            logger.error(f"Error analyzing compatibility: {str(e)}")
            return None
    
    async def _analyze_content_style_compatibility(self, match: CollaborationMatch,
                                                 creator: CreatorProfile,
                                                 candidate: CreatorProfile) -> None:
        """Analyze content style compatibility."""
        try:
            # Content category overlap
            creator_categories = set(creator.content_categories)
            candidate_categories = set(candidate.content_categories)
            
            if creator_categories and candidate_categories:
                category_overlap = len(creator_categories.intersection(candidate_categories))
                total_categories = len(creator_categories.union(candidate_categories))
                category_score = category_overlap / total_categories if total_categories > 0 else 0
            else:
                category_score = 0.5  # Neutral when no data
            
            # Format compatibility
            creator_formats = set(creator.content_formats)
            candidate_formats = set(candidate.content_formats)
            
            if creator_formats and candidate_formats:
                format_overlap = len(creator_formats.intersection(candidate_formats))
                format_complementarity = len(creator_formats.symmetric_difference(candidate_formats))
                # Balance between overlap and complementarity
                format_score = (format_overlap * 0.7 + format_complementarity * 0.3) / max(len(creator_formats), len(candidate_formats), 1)
            else:
                format_score = 0.5
            
            # Content quality compatibility
            creator_quality = sum(creator.quality_metrics.values()) / len(creator.quality_metrics) if creator.quality_metrics else 0.6
            candidate_quality = sum(candidate.quality_metrics.values()) / len(candidate.quality_metrics) if candidate.quality_metrics else 0.6
            
            quality_score = 1.0 - abs(creator_quality - candidate_quality)  # Similar quality levels work better
            
            # Combined content style score
            content_style_score = (category_score * 0.4 + format_score * 0.4 + quality_score * 0.2)
            
            match.compatibility_scores[CompatibilityFactor.CONTENT_STYLE] = content_style_score
            match.compatibility_details['content_style'] = {
                'category_overlap': category_score,
                'format_compatibility': format_score,
                'quality_alignment': quality_score,
                'shared_categories': list(creator_categories.intersection(candidate_categories)),
                'complementary_formats': list(creator_formats.symmetric_difference(candidate_formats))
            }
            
        except Exception as e:
            logger.error(f"Error analyzing content style compatibility: {str(e)}")
            match.compatibility_scores[CompatibilityFactor.CONTENT_STYLE] = 0.5
    
    async def _analyze_audience_overlap(self, match: CollaborationMatch,
                                      creator: CreatorProfile,
                                      candidate: CreatorProfile) -> None:
        """Analyze audience overlap and cross-pollination potential."""
        try:
            # Platform audience overlap
            creator_platforms = set(creator.platforms)
            candidate_platforms = set(candidate.platforms)
            
            platform_overlap = len(creator_platforms.intersection(candidate_platforms))
            platform_expansion = len(creator_platforms.symmetric_difference(candidate_platforms))
            
            # Balance overlap (good for collaboration) with expansion (good for growth)
            platform_score = (platform_overlap * 0.6 + platform_expansion * 0.4) / max(len(creator_platforms), len(candidate_platforms), 1)
            
            # Follower count compatibility (similar ranges work better)
            creator_total_followers = sum(creator.follower_counts.values()) if creator.follower_counts else 1000
            candidate_total_followers = sum(candidate.follower_counts.values()) if candidate.follower_counts else 1000
            
            follower_ratio = min(creator_total_followers, candidate_total_followers) / max(creator_total_followers, candidate_total_followers)
            follower_score = follower_ratio  # Higher when follower counts are similar
            
            # Engagement rate compatibility
            creator_avg_engagement = sum(creator.engagement_rates.values()) / len(creator.engagement_rates) if creator.engagement_rates else 0.05
            candidate_avg_engagement = sum(candidate.engagement_rates.values()) / len(candidate.engagement_rates) if candidate.engagement_rates else 0.05
            
            engagement_compatibility = 1.0 - abs(creator_avg_engagement - candidate_avg_engagement) / max(creator_avg_engagement, candidate_avg_engagement)
            
            # Combined audience score
            audience_score = (platform_score * 0.4 + follower_score * 0.35 + engagement_compatibility * 0.25)
            
            match.compatibility_scores[CompatibilityFactor.AUDIENCE_OVERLAP] = audience_score
            match.compatibility_details['audience_overlap'] = {
                'shared_platforms': list(creator_platforms.intersection(candidate_platforms)),
                'expansion_platforms': list(creator_platforms.symmetric_difference(candidate_platforms)),
                'follower_ratio': follower_ratio,
                'engagement_compatibility': engagement_compatibility
            }
            
        except Exception as e:
            logger.error(f"Error analyzing audience overlap: {str(e)}")
            match.compatibility_scores[CompatibilityFactor.AUDIENCE_OVERLAP] = 0.5
    
    async def _analyze_skill_complementarity(self, match: CollaborationMatch,
                                           creator: CreatorProfile,
                                           candidate: CreatorProfile) -> None:
        """Analyze skill complementarity and learning opportunities."""
        try:
            creator_skills = set(creator.skills)
            candidate_skills = set(candidate.skills)
            
            # Skill overlap (good for collaboration on similar tasks)
            skill_overlap = len(creator_skills.intersection(candidate_skills))
            overlap_score = skill_overlap / max(len(creator_skills), len(candidate_skills), 1)
            
            # Complementary skills (good for learning and diverse collaboration)
            complementary_skills = creator_skills.symmetric_difference(candidate_skills)
            complementarity_score = len(complementary_skills) / (len(creator_skills) + len(candidate_skills))
            
            # Experience level complementarity
            experience_levels = ['beginner', 'intermediate', 'advanced', 'expert']
            creator_level = experience_levels.index(creator.experience_level) if creator.experience_level in experience_levels else 1
            candidate_level = experience_levels.index(candidate.experience_level) if candidate.experience_level in experience_levels else 1
            
            # Similar levels work well for peers, different levels good for mentorship
            level_difference = abs(creator_level - candidate_level)
            if level_difference <= 1:
                experience_score = 0.9  # Similar levels
            elif level_difference == 2:
                experience_score = 0.8  # Good mentorship potential
            else:
                experience_score = 0.6  # Large gap may be challenging
            
            # Combined skill score
            skill_score = (overlap_score * 0.3 + complementarity_score * 0.5 + experience_score * 0.2)
            
            match.compatibility_scores[CompatibilityFactor.SKILL_COMPLEMENTARITY] = skill_score
            match.compatibility_details['skill_complementarity'] = {
                'shared_skills': list(creator_skills.intersection(candidate_skills)),
                'complementary_skills': list(complementary_skills),
                'experience_gap': level_difference,
                'learning_opportunities': list(candidate_skills - creator_skills)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing skill complementarity: {str(e)}")
            match.compatibility_scores[CompatibilityFactor.SKILL_COMPLEMENTARITY] = 0.6
    
    async def _analyze_schedule_compatibility(self, match: CollaborationMatch,
                                            creator: CreatorProfile,
                                            candidate: CreatorProfile) -> None:
        """Analyze schedule and timezone compatibility."""
        try:
            # Timezone compatibility
            if creator.timezone and candidate.timezone:
                # Simplified timezone analysis
                creator_tz = creator.timezone
                candidate_tz = candidate.timezone
                
                if creator_tz == candidate_tz:
                    timezone_score = 1.0
                elif 'Europe' in creator_tz and 'Europe' in candidate_tz:
                    timezone_score = 0.9  # Similar time zones
                elif 'America' in creator_tz and 'America' in candidate_tz:
                    timezone_score = 0.8  # Same continent
                else:
                    timezone_score = 0.4  # Different continents
            else:
                timezone_score = 0.7  # Default when no timezone info
            
            # Availability overlap (simplified analysis)
            availability_score = 0.8  # Would be calculated from actual availability data
            
            # Collaboration frequency compatibility
            creator_frequency = creator.preferred_collaboration_frequency
            candidate_frequency = candidate.preferred_collaboration_frequency
            
            frequency_compatibility = {
                ('occasional', 'occasional'): 1.0,
                ('regular', 'regular'): 1.0,
                ('frequent', 'frequent'): 1.0,
                ('occasional', 'regular'): 0.8,
                ('regular', 'frequent'): 0.8,
                ('occasional', 'frequent'): 0.6
            }
            
            frequency_score = frequency_compatibility.get(
                (creator_frequency, candidate_frequency), 0.7
            )
            
            # Combined schedule score
            schedule_score = (timezone_score * 0.4 + availability_score * 0.4 + frequency_score * 0.2)
            
            match.compatibility_scores[CompatibilityFactor.SCHEDULE_COMPATIBILITY] = schedule_score
            match.compatibility_details['schedule_compatibility'] = {
                'timezone_alignment': timezone_score,
                'availability_overlap': availability_score,
                'frequency_compatibility': frequency_score
            }
            
        except Exception as e:
            logger.error(f"Error analyzing schedule compatibility: {str(e)}")
            match.compatibility_scores[CompatibilityFactor.SCHEDULE_COMPATIBILITY] = 0.7
    
    async def _analyze_communication_compatibility(self, match: CollaborationMatch,
                                                 creator: CreatorProfile,
                                                 candidate: CreatorProfile) -> None:
        """Analyze communication style and preference compatibility."""
        try:
            # Language compatibility
            creator_languages = set(creator.language_preferences) if creator.language_preferences else {'english'}
            candidate_languages = set(candidate.language_preferences) if candidate.language_preferences else {'english'}
            
            language_overlap = len(creator_languages.intersection(candidate_languages))
            language_score = language_overlap / max(len(creator_languages), len(candidate_languages), 1)
            
            # Communication method compatibility
            creator_comm = set(creator.preferred_communication) if creator.preferred_communication else {'email', 'chat'}
            candidate_comm = set(candidate.preferred_communication) if candidate.preferred_communication else {'email', 'chat'}
            
            comm_overlap = len(creator_comm.intersection(candidate_comm))
            comm_score = comm_overlap / max(len(creator_comm), len(candidate_comm), 1)
            
            # Professional communication level
            experience_levels = ['beginner', 'intermediate', 'advanced', 'expert']
            creator_level = experience_levels.index(creator.experience_level) if creator.experience_level in experience_levels else 1
            candidate_level = experience_levels.index(candidate.experience_level) if candidate.experience_level in experience_levels else 1
            
            # Similar professional levels usually communicate better
            professional_comm_score = 1.0 - abs(creator_level - candidate_level) * 0.2
            
            # Combined communication score
            communication_score = (language_score * 0.4 + comm_score * 0.4 + professional_comm_score * 0.2)
            
            match.compatibility_scores[CompatibilityFactor.COMMUNICATION_STYLE] = communication_score
            match.compatibility_details['communication_style'] = {
                'shared_languages': list(creator_languages.intersection(candidate_languages)),
                'shared_communication_methods': list(creator_comm.intersection(candidate_comm)),
                'professional_alignment': professional_comm_score
            }
            
        except Exception as e:
            logger.error(f"Error analyzing communication compatibility: {str(e)}")
            match.compatibility_scores[CompatibilityFactor.COMMUNICATION_STYLE] = 0.7
    
    async def _analyze_professional_level_compatibility(self, match: CollaborationMatch,
                                                      creator: CreatorProfile,
                                                      candidate: CreatorProfile) -> None:
        """Analyze professional level and career stage compatibility."""
        try:
            experience_levels = ['beginner', 'intermediate', 'advanced', 'expert']
            creator_level = experience_levels.index(creator.experience_level) if creator.experience_level in experience_levels else 1
            candidate_level = experience_levels.index(candidate.experience_level) if candidate.experience_level in experience_levels else 1
            
            level_difference = abs(creator_level - candidate_level)
            
            # Professional level scoring
            if level_difference == 0:
                professional_score = 1.0  # Same level - excellent peer collaboration
            elif level_difference == 1:
                professional_score = 0.9   # One level apart - great for mentorship/learning
            elif level_difference == 2:
                professional_score = 0.7   # Two levels apart - still workable
            else:
                professional_score = 0.5   # Large gap - challenging but possible
            
            # Portfolio quality alignment
            creator_quality = creator.profile_completeness
            candidate_quality = candidate.profile_completeness
            quality_alignment = 1.0 - abs(creator_quality - candidate_quality)
            
            # Combined professional score
            final_professional_score = (professional_score * 0.7 + quality_alignment * 0.3)
            
            match.compatibility_scores[CompatibilityFactor.PROFESSIONAL_LEVEL] = final_professional_score
            match.compatibility_details['professional_level'] = {
                'experience_gap': level_difference,
                'quality_alignment': quality_alignment,
                'collaboration_type_suitability': 'peer' if level_difference <= 1 else 'mentorship'
            }
            
        except Exception as e:
            logger.error(f"Error analyzing professional level compatibility: {str(e)}")
            match.compatibility_scores[CompatibilityFactor.PROFESSIONAL_LEVEL] = 0.7
    
    async def _analyze_geographic_compatibility(self, match: CollaborationMatch,
                                              creator: CreatorProfile,
                                              candidate: CreatorProfile) -> None:
        """Analyze geographic proximity and cultural compatibility."""
        try:
            creator_location = creator.location
            candidate_location = candidate.location
            
            if creator_location and candidate_location:
                creator_country = creator_location.get('country', '')
                candidate_country = candidate_location.get('country', '')
                creator_city = creator_location.get('city', '')
                candidate_city = candidate_location.get('city', '')
                
                if creator_city == candidate_city:
                    geographic_score = 1.0  # Same city
                elif creator_country == candidate_country:
                    geographic_score = 0.8  # Same country
                elif self._same_region(creator_country, candidate_country):
                    geographic_score = 0.6  # Same region
                else:
                    geographic_score = 0.4  # Different regions
            else:
                geographic_score = 0.6  # Default when location data missing
            
            match.compatibility_scores[CompatibilityFactor.GEOGRAPHIC_PROXIMITY] = geographic_score
            match.compatibility_details['geographic_proximity'] = {
                'proximity_level': self._get_proximity_level(creator_location, candidate_location),
                'collaboration_mode': 'in-person' if geographic_score >= 0.8 else 'remote'
            }
            
        except Exception as e:
            logger.error(f"Error analyzing geographic compatibility: {str(e)}")
            match.compatibility_scores[CompatibilityFactor.GEOGRAPHIC_PROXIMITY] = 0.5
    
    async def _analyze_brand_alignment(self, match: CollaborationMatch,
                                     creator: CreatorProfile,
                                     candidate: CreatorProfile) -> None:
        """Analyze brand values and aesthetic alignment."""
        try:
            # Analyze content categories for brand alignment
            creator_categories = set(creator.content_categories)
            candidate_categories = set(candidate.content_categories)
            
            category_alignment = len(creator_categories.intersection(candidate_categories)) / max(len(creator_categories.union(candidate_categories)), 1)
            
            # Professional level alignment (similar levels often have aligned brands)
            experience_levels = ['beginner', 'intermediate', 'advanced', 'expert']
            creator_level = experience_levels.index(creator.experience_level) if creator.experience_level in experience_levels else 1
            candidate_level = experience_levels.index(candidate.experience_level) if candidate.experience_level in experience_levels else 1
            
            professional_brand_alignment = 1.0 - abs(creator_level - candidate_level) * 0.15
            
            # Target audience alignment
            audience_alignment = 0.7  # Would be calculated from actual audience data
            
            # Combined brand alignment
            brand_score = (category_alignment * 0.4 + professional_brand_alignment * 0.3 + audience_alignment * 0.3)
            
            match.compatibility_scores[CompatibilityFactor.BRAND_ALIGNMENT] = brand_score
            match.compatibility_details['brand_alignment'] = {
                'content_category_overlap': category_alignment,
                'professional_alignment': professional_brand_alignment,
                'audience_alignment': audience_alignment
            }
            
        except Exception as e:
            logger.error(f"Error analyzing brand alignment: {str(e)}")
            match.compatibility_scores[CompatibilityFactor.BRAND_ALIGNMENT] = 0.6
    
    async def _analyze_platform_synergy(self, match: CollaborationMatch,
                                      creator: CreatorProfile,
                                      candidate: CreatorProfile) -> None:
        """Analyze platform synergy and cross-promotion potential."""
        try:
            creator_platforms = set(creator.platforms)
            candidate_platforms = set(candidate.platforms)
            
            # Platform overlap for collaboration
            platform_overlap = len(creator_platforms.intersection(candidate_platforms))
            overlap_score = platform_overlap / max(len(creator_platforms), len(candidate_platforms), 1)
            
            # Platform expansion opportunities
            unique_platforms = len(creator_platforms.symmetric_difference(candidate_platforms))
            expansion_score = unique_platforms / (len(creator_platforms) + len(candidate_platforms))
            
            # Platform-specific synergies
            synergy_scores = []
            
            # Social media synergy
            social_platforms = {'instagram', 'tiktok', 'twitter', 'facebook'}
            social_overlap = len((creator_platforms & candidate_platforms) & social_platforms)
            if social_overlap > 0:
                synergy_scores.append(0.9)  # High synergy for social collaboration
            
            # Content platform synergy
            content_platforms = {'youtube', 'spotify', 'soundcloud', 'twitch'}
            content_overlap = len((creator_platforms & candidate_platforms) & content_platforms)
            if content_overlap > 0:
                synergy_scores.append(0.8)  # Good synergy for content collaboration
            
            # Average synergy
            avg_synergy = sum(synergy_scores) / len(synergy_scores) if synergy_scores else 0.6
            
            # Combined platform synergy score
            platform_synergy_score = (overlap_score * 0.4 + expansion_score * 0.3 + avg_synergy * 0.3)
            
            match.compatibility_scores[CompatibilityFactor.PLATFORM_SYNERGY] = platform_synergy_score
            match.compatibility_details['platform_synergy'] = {
                'shared_platforms': list(creator_platforms.intersection(candidate_platforms)),
                'expansion_opportunities': list(creator_platforms.symmetric_difference(candidate_platforms)),
                'synergy_potential': avg_synergy
            }
            
        except Exception as e:
            logger.error(f"Error analyzing platform synergy: {str(e)}")
            match.compatibility_scores[CompatibilityFactor.PLATFORM_SYNERGY] = 0.6
    
    def _calculate_overall_compatibility(self, match: CollaborationMatch,
                                       collaboration_types: List[CollaborationType] = None) -> None:
        """Calculate overall compatibility score with appropriate weighting."""
        # Determine which weighting scheme to use
        if collaboration_types and len(collaboration_types) == 1:
            weights = self.matching_weights.get(collaboration_types[0].value, {})
        else:
            # Use balanced weights for multiple or unspecified collaboration types
            weights = {
                CompatibilityFactor.CONTENT_STYLE: 0.20,
                CompatibilityFactor.AUDIENCE_OVERLAP: 0.18,
                CompatibilityFactor.SKILL_COMPLEMENTARITY: 0.16,
                CompatibilityFactor.PROFESSIONAL_LEVEL: 0.14,
                CompatibilityFactor.PLATFORM_SYNERGY: 0.12,
                CompatibilityFactor.SCHEDULE_COMPATIBILITY: 0.08,
                CompatibilityFactor.COMMUNICATION_STYLE: 0.06,
                CompatibilityFactor.BRAND_ALIGNMENT: 0.04,
                CompatibilityFactor.GEOGRAPHIC_PROXIMITY: 0.02
            }
        
        # Calculate weighted score
        weighted_score = 0.0
        total_weight = 0.0
        
        for factor, weight in weights.items():
            if factor in match.compatibility_scores:
                weighted_score += match.compatibility_scores[factor] * weight
                total_weight += weight
        
        # Normalize by actual total weight
        if total_weight > 0:
            match.overall_compatibility_score = weighted_score / total_weight
        else:
            match.overall_compatibility_score = 0.5
        
        # Calculate match confidence based on data completeness
        available_factors = len(match.compatibility_scores)
        total_factors = len(CompatibilityFactor)
        match.match_confidence = available_factors / total_factors
    
    def _determine_match_priority(self, match: CollaborationMatch) -> None:
        """Determine match priority based on compatibility and potential."""
        score = match.overall_compatibility_score
        confidence = match.match_confidence
        
        # Adjust score by confidence
        adjusted_score = score * confidence
        
        if adjusted_score >= 0.85:
            match.match_priority = MatchingPriority.URGENT
        elif adjusted_score >= 0.75:
            match.match_priority = MatchingPriority.HIGH
        elif adjusted_score >= 0.65:
            match.match_priority = MatchingPriority.MEDIUM
        elif adjusted_score >= 0.50:
            match.match_priority = MatchingPriority.LOW
        else:
            match.match_priority = MatchingPriority.EXPLORATORY
    
    async def _generate_collaboration_recommendations(self, match: CollaborationMatch,
                                                    creator: CreatorProfile,
                                                    candidate: CreatorProfile) -> None:
        """Generate specific collaboration type recommendations."""
        recommendations = []
        
        # Content Collaboration
        content_style_score = match.compatibility_scores.get(CompatibilityFactor.CONTENT_STYLE, 0)
        skill_complementarity = match.compatibility_scores.get(CompatibilityFactor.SKILL_COMPLEMENTARITY, 0)
        
        if content_style_score >= 0.7 and skill_complementarity >= 0.6:
            recommendations.append(CollaborationType.CONTENT_COLLABORATION)
            match.collaboration_potential[CollaborationType.CONTENT_COLLABORATION] = (content_style_score + skill_complementarity) / 2
        
        # Cross Promotion
        audience_overlap = match.compatibility_scores.get(CompatibilityFactor.AUDIENCE_OVERLAP, 0)
        platform_synergy = match.compatibility_scores.get(CompatibilityFactor.PLATFORM_SYNERGY, 0)
        
        if audience_overlap >= 0.6 and platform_synergy >= 0.7:
            recommendations.append(CollaborationType.CROSS_PROMOTION)
            match.collaboration_potential[CollaborationType.CROSS_PROMOTION] = (audience_overlap + platform_synergy) / 2
        
        # Skill Exchange
        if skill_complementarity >= 0.7:
            recommendations.append(CollaborationType.SKILL_EXCHANGE)
            match.collaboration_potential[CollaborationType.SKILL_EXCHANGE] = skill_complementarity
        
        # Mentorship
        professional_level = match.compatibility_scores.get(CompatibilityFactor.PROFESSIONAL_LEVEL, 0)
        experience_gap = match.compatibility_details.get('professional_level', {}).get('experience_gap', 0)
        
        if 1 <= experience_gap <= 2 and professional_level >= 0.6:
            recommendations.append(CollaborationType.MENTORSHIP)
            match.collaboration_potential[CollaborationType.MENTORSHIP] = professional_level * 0.9
        
        match.recommended_collaboration_types = recommendations
    
    async def _assess_collaboration_risks_benefits(self, match: CollaborationMatch,
                                                 creator: CreatorProfile,
                                                 candidate: CreatorProfile) -> None:
        """Assess potential risks and benefits of collaboration."""
        # Benefits for primary creator
        benefits_primary = []
        if match.compatibility_scores.get(CompatibilityFactor.SKILL_COMPLEMENTARITY, 0) >= 0.7:
            benefits_primary.append("Skill development opportunities")
        if match.compatibility_scores.get(CompatibilityFactor.AUDIENCE_OVERLAP, 0) >= 0.6:
            benefits_primary.append("Audience expansion potential")
        if match.compatibility_scores.get(CompatibilityFactor.PLATFORM_SYNERGY, 0) >= 0.7:
            benefits_primary.append("Platform diversification")
        
        # Benefits for matched creator (reciprocal analysis)
        benefits_matched = []
        if match.compatibility_scores.get(CompatibilityFactor.SKILL_COMPLEMENTARITY, 0) >= 0.7:
            benefits_matched.append("Cross-skill learning")
        if match.compatibility_scores.get(CompatibilityFactor.CONTENT_STYLE, 0) >= 0.7:
            benefits_matched.append("Content quality enhancement")
        
        # Mutual benefits
        mutual_benefits = []
        if match.overall_compatibility_score >= 0.8:
            mutual_benefits.append("High-quality collaborative content")
        if match.compatibility_scores.get(CompatibilityFactor.PROFESSIONAL_LEVEL, 0) >= 0.8:
            mutual_benefits.append("Professional network expansion")
        
        # Potential challenges/risks
        challenges = []
        if match.compatibility_scores.get(CompatibilityFactor.SCHEDULE_COMPATIBILITY, 0) < 0.6:
            challenges.append("Scheduling coordination difficulties")
        if match.compatibility_scores.get(CompatibilityFactor.COMMUNICATION_STYLE, 0) < 0.6:
            challenges.append("Communication style differences")
        if match.compatibility_scores.get(CompatibilityFactor.GEOGRAPHIC_PROXIMITY, 0) < 0.4:
            challenges.append("Remote collaboration logistics")
        
        # Risk factors
        risk_factors = {}
        if match.match_confidence < 0.7:
            risk_factors['insufficient_data'] = 1.0 - match.match_confidence
        if match.overall_compatibility_score < 0.6:
            risk_factors['compatibility_concerns'] = 1.0 - match.overall_compatibility_score
        
        # Store assessments
        match.benefits_for_primary = benefits_primary
        match.benefits_for_matched = benefits_matched
        match.mutual_benefits = mutual_benefits
        match.potential_challenges = challenges
        match.risk_factors = risk_factors
        
        # Mitigation strategies
        mitigation_strategies = []
        if 'scheduling_difficulties' in [c.lower().replace(' ', '_') for c in challenges]:
            mitigation_strategies.append("Use collaborative scheduling tools and establish clear availability windows")
        if 'communication_differences' in [c.lower().replace(' ', '_') for c in challenges]:
            mitigation_strategies.append("Establish communication protocols and preferred channels early")
        if 'remote_logistics' in [c.lower().replace(' ', '_') for c in challenges]:
            mitigation_strategies.append("Utilize cloud-based collaboration tools and regular check-ins")
        
        match.mitigation_strategies = mitigation_strategies
    
    # Helper methods
    def _same_region(self, country1: str, country2: str) -> bool:
        """Check if two countries are in the same region."""
        european_countries = {'germany', 'france', 'italy', 'spain', 'uk', 'netherlands', 'belgium', 'austria', 'switzerland'}
        north_american_countries = {'usa', 'canada', 'mexico'}
        asian_countries = {'japan', 'china', 'korea', 'india', 'singapore', 'thailand'}
        
        country1_lower = country1.lower()
        country2_lower = country2.lower()
        
        if country1_lower in european_countries and country2_lower in european_countries:
            return True
        if country1_lower in north_american_countries and country2_lower in north_american_countries:
            return True
        if country1_lower in asian_countries and country2_lower in asian_countries:
            return True
        
        return False
    
    def _get_proximity_level(self, location1: Dict[str, Any], location2: Dict[str, Any]) -> str:
        """Get proximity level description."""
        if not location1 or not location2:
            return "unknown"
        
        city1 = location1.get('city', '')
        city2 = location2.get('city', '')
        country1 = location1.get('country', '')
        country2 = location2.get('country', '')
        
        if city1 == city2:
            return "same_city"
        elif country1 == country2:
            return "same_country"
        elif self._same_region(country1, country2):
            return "same_region"
        else:
            return "different_regions"
