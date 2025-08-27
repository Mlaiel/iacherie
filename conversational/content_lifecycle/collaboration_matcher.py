"""
Collaboration Matcher Module - AI-Powered Creator Collaboration System

Enterprise-grade collaboration matching system implementing AI-powered creator discovery,
intelligent matching algorithms, and automated collaboration opportunity generation.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  LEGAL WARNING ⚠️
This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution without explicit written 
permission is strictly prohibited and will result in legal action.
Contact: mlaiel@live.de
"""

import asyncio
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Union, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
import logging
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer

from ...core.database import get_db_session
from ...core.exceptions import BusinessLogicError, ValidationError
from ...utils.cache_manager import CacheManager
from ...utils.event_emitter import EventEmitter
from ...ai.ml.recommendation_engine import RecommendationEngine
from ...ai.ml.similarity_matcher import SimilarityMatcher
from ...ai.content_generation.profile_analyzer import ProfileAnalyzer

logger = logging.getLogger(__name__)


class CollaborationType(Enum):
    """Types of collaborations"""
    CROSS_PROMOTION = "cross_promotion"
    CONTENT_REMIX = "content_remix"
    JOINT_CREATION = "joint_creation"
    GUEST_FEATURE = "guest_feature"
    SERIES_COLLABORATION = "series_collaboration"
    SKILL_EXCHANGE = "skill_exchange"
    MENTORSHIP = "mentorship"
    BRAND_PARTNERSHIP = "brand_partnership"


class MatchingCriteria(Enum):
    """Matching criteria for collaborations"""
    CONTENT_SIMILARITY = "content_similarity"
    AUDIENCE_OVERLAP = "audience_overlap"
    COMPLEMENTARY_SKILLS = "complementary_skills"
    GEOGRAPHIC_PROXIMITY = "geographic_proximity"
    ENGAGEMENT_COMPATIBILITY = "engagement_compatibility"
    BRAND_ALIGNMENT = "brand_alignment"
    SCHEDULE_COMPATIBILITY = "schedule_compatibility"
    BUDGET_COMPATIBILITY = "budget_compatibility"


class CollaborationStatus(Enum):
    """Collaboration status types"""
    SUGGESTED = "suggested"
    PENDING_INVITATION = "pending_invitation"
    ACCEPTED = "accepted"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    DECLINED = "declined"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


class MatchingConfidence(Enum):
    """Matching confidence levels"""
    LOW = "low"          # 0.3-0.5
    MEDIUM = "medium"    # 0.5-0.7
    HIGH = "high"        # 0.7-0.85
    EXCELLENT = "excellent"  # 0.85-1.0


@dataclass
class CreatorProfile:
    """Creator profile for collaboration matching"""
    profile_id: str
    user_id: str
    creator_name: str
    content_formats: List[str]
    genres_categories: List[str]
    skills_expertise: List[str]
    audience_demographics: Dict[str, Any]
    engagement_metrics: Dict[str, float]
    collaboration_preferences: Dict[str, Any]
    availability_schedule: Dict[str, Any]
    geographic_location: Dict[str, str]
    portfolio_highlights: List[Dict[str, Any]]
    social_media_presence: Dict[str, Dict[str, Any]]
    collaboration_history: List[Dict[str, Any]]
    reputation_score: float
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class CollaborationOpportunity:
    """Collaboration opportunity structure"""
    opportunity_id: str
    creator_id: str  # Primary creator
    content_id: str
    collaboration_type: CollaborationType
    description: str
    requirements: Dict[str, Any]
    compensation_model: Dict[str, Any]
    timeline: Dict[str, datetime]
    target_demographics: Dict[str, Any]
    success_metrics: Dict[str, Any]
    collaboration_terms: Dict[str, Any]
    geographic_scope: List[str]
    budget_range: Dict[str, float]
    skills_needed: List[str]
    status: CollaborationStatus = CollaborationStatus.SUGGESTED
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class CollaborationMatch:
    """Collaboration match result"""
    match_id: str
    opportunity_id: str
    matched_creator_id: str
    primary_creator_id: str
    match_score: float
    confidence_level: MatchingConfidence
    matching_factors: Dict[str, float]
    compatibility_analysis: Dict[str, Any]
    potential_outcomes: Dict[str, Any]
    recommended_terms: Dict[str, Any]
    risk_assessment: Dict[str, float]
    success_probability: float
    mutual_benefits: List[str]
    collaboration_roadmap: List[Dict[str, Any]]
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class CollaborationProposal:
    """Collaboration proposal structure"""
    proposal_id: str
    match_id: str
    proposer_id: str
    recipient_id: str
    opportunity_id: str
    proposal_terms: Dict[str, Any]
    compensation_offer: Dict[str, Any]
    timeline_proposal: Dict[str, datetime]
    deliverables: List[Dict[str, Any]]
    rights_distribution: Dict[str, float]
    communication_plan: Dict[str, Any]
    success_metrics: Dict[str, Any]
    contract_template: Dict[str, Any]
    status: CollaborationStatus = CollaborationStatus.PENDING_INVITATION
    created_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: datetime = field(default_factory=lambda: datetime.utcnow() + timedelta(days=7))


class CollaborationMatcher:
    """
    Enterprise-grade collaboration matching system for creator economy,
    implementing AI-powered matching and collaboration opportunity generation.
    """
    
    def __init__(self, cache_manager: CacheManager, event_emitter: EventEmitter):
        self.cache_manager = cache_manager
        self.event_emitter = event_emitter
        self.recommendation_engine = RecommendationEngine()
        self.similarity_matcher = SimilarityMatcher()
        self.profile_analyzer = ProfileAnalyzer()
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        self.creator_profiles = {}
        self.active_opportunities = {}
        self.matching_weights = self._initialize_matching_weights()
        
    def _initialize_matching_weights(self) -> Dict[MatchingCriteria, float]:
        """Initialize weights for different matching criteria"""
        return {
            MatchingCriteria.CONTENT_SIMILARITY: 0.25,
            MatchingCriteria.AUDIENCE_OVERLAP: 0.20,
            MatchingCriteria.COMPLEMENTARY_SKILLS: 0.15,
            MatchingCriteria.ENGAGEMENT_COMPATIBILITY: 0.15,
            MatchingCriteria.BRAND_ALIGNMENT: 0.10,
            MatchingCriteria.GEOGRAPHIC_PROXIMITY: 0.05,
            MatchingCriteria.SCHEDULE_COMPATIBILITY: 0.05,
            MatchingCriteria.BUDGET_COMPATIBILITY: 0.05
        }
    
    async def find_collaboration_opportunities(
        self,
        content_id: str,
        user_id: str,
        content_data: Dict[str, Any],
        collaboration_preferences: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Find and generate collaboration opportunities for content
        
        Business Logic Integration:
        Content Upload → AI Processing → Protection → SEO → COLLABORATION MATCHING → Distribution
        """
        try:
            # Step 1: Analyze content for collaboration potential
            content_analysis = await self._analyze_content_collaboration_potential(
                content_data, user_id
            )
            
            # Step 2: Get or create creator profile
            creator_profile = await self._get_or_create_creator_profile(
                user_id, content_data, collaboration_preferences
            )
            
            # Step 3: Generate collaboration opportunities
            opportunities = await self._generate_collaboration_opportunities(
                content_id, creator_profile, content_analysis
            )
            
            # Step 4: Find matching creators for each opportunity
            collaboration_matches = []
            for opportunity in opportunities:
                matches = await self._find_matching_creators(opportunity, creator_profile)
                collaboration_matches.extend(matches)
            
            # Step 5: Rank and filter matches
            ranked_matches = await self._rank_collaboration_matches(
                collaboration_matches, creator_profile, content_analysis
            )
            
            # Step 6: Generate collaboration proposals
            proposals = await self._generate_collaboration_proposals(
                ranked_matches[:10], creator_profile  # Top 10 matches
            )
            
            # Step 7: Create collaboration roadmaps
            roadmaps = await self._create_collaboration_roadmaps(
                proposals, content_data
            )
            
            # Store collaboration data
            await self._store_collaboration_data(
                content_id, opportunities, collaboration_matches, proposals
            )
            
            # Emit collaboration matching completed event
            await self.event_emitter.emit("collaboration_matching_completed", {
                "content_id": content_id,
                "user_id": user_id,
                "opportunities_found": len(opportunities),
                "matches_found": len(ranked_matches),
                "proposals_generated": len(proposals)
            })
            
            return {
                "collaboration_ready": True,
                "content_id": content_id,
                "collaboration_components": {
                    "content_analysis": content_analysis,
                    "creator_profile": creator_profile,
                    "opportunities": opportunities,
                    "top_matches": ranked_matches[:10],
                    "proposals": proposals,
                    "collaboration_roadmaps": roadmaps
                },
                "collaboration_score": self._calculate_collaboration_score(
                    content_analysis, opportunities, ranked_matches
                ),
                "recommended_actions": await self._generate_collaboration_recommendations(
                    creator_profile, ranked_matches
                ),
                "next_stage": "distribution_preparation"
            }
            
        except Exception as e:
            logger.error(f"Collaboration matching failed: {str(e)}")
            await self.event_emitter.emit("collaboration_matching_failed", {
                "content_id": content_id,
                "user_id": user_id,
                "error": str(e)
            })
            raise BusinessLogicError(f"Collaboration matching failed: {str(e)}")
    
    async def _analyze_content_collaboration_potential(
        self,
        content_data: Dict[str, Any],
        user_id: str
    ) -> Dict[str, Any]:
        """Analyze content for collaboration potential"""
        try:
            # Analyze content characteristics
            content_features = await self.profile_analyzer.analyze_content_features(content_data)
            
            # Determine collaboration types suitable for this content
            suitable_collaboration_types = await self._determine_suitable_collaboration_types(
                content_data, content_features
            )
            
            # Analyze skill requirements
            skill_requirements = await self._analyze_skill_requirements(
                content_data, content_features
            )
            
            # Calculate collaboration potential score
            collaboration_potential = await self._calculate_collaboration_potential(
                content_features, suitable_collaboration_types
            )
            
            return {
                "content_features": content_features,
                "suitable_collaboration_types": suitable_collaboration_types,
                "skill_requirements": skill_requirements,
                "collaboration_potential": collaboration_potential,
                "target_demographics": content_features.get("target_demographics", {}),
                "engagement_predictions": content_features.get("engagement_predictions", {}),
                "viral_potential": content_features.get("viral_potential", 0.0),
                "monetization_potential": content_features.get("monetization_potential", 0.0)
            }
            
        except Exception as e:
            logger.error(f"Content collaboration analysis failed: {str(e)}")
            return {
                "content_features": {},
                "suitable_collaboration_types": [],
                "collaboration_potential": 0.5,
                "error": str(e)
            }
    
    async def _get_or_create_creator_profile(
        self,
        user_id: str,
        content_data: Dict[str, Any],
        collaboration_preferences: Dict[str, Any] = None
    ) -> CreatorProfile:
        """Get existing creator profile or create new one"""
        try:
            # Try to get existing profile from cache
            cached_profile = await self.cache_manager.get(f"creator_profile:{user_id}")
            if cached_profile:
                profile_data = json.loads(cached_profile)
                return CreatorProfile(**profile_data)
            
            # Get user data from database
            user_data = await self._get_user_data(user_id)
            
            # Analyze user's content history
            content_history = await self._analyze_user_content_history(user_id)
            
            # Extract skills and expertise
            skills_expertise = await self._extract_skills_and_expertise(
                user_data, content_history, content_data
            )
            
            # Analyze audience demographics
            audience_demographics = await self._analyze_audience_demographics(user_id)
            
            # Calculate engagement metrics
            engagement_metrics = await self._calculate_engagement_metrics(user_id)
            
            # Set default collaboration preferences
            default_preferences = collaboration_preferences or {
                "preferred_collaboration_types": [
                    CollaborationType.CROSS_PROMOTION.value,
                    CollaborationType.CONTENT_REMIX.value
                ],
                "geographic_scope": "global",
                "budget_range": {"min": 0, "max": 1000},
                "timeline_preferences": {"min_days": 7, "max_days": 30}
            }
            
            # Create creator profile
            creator_profile = CreatorProfile(
                profile_id=str(uuid.uuid4()),
                user_id=user_id,
                creator_name=user_data.get("display_name", f"Creator_{user_id[:8]}"),
                content_formats=[content_data.get("content_format", "text")],
                genres_categories=content_history.get("genres", []),
                skills_expertise=skills_expertise,
                audience_demographics=audience_demographics,
                engagement_metrics=engagement_metrics,
                collaboration_preferences=default_preferences,
                availability_schedule={},
                geographic_location=user_data.get("location", {}),
                portfolio_highlights=[],
                social_media_presence={},
                collaboration_history=[],
                reputation_score=0.75  # Default reputation
            )
            
            # Cache the profile
            await self.cache_manager.set(
                f"creator_profile:{user_id}",
                json.dumps(creator_profile.__dict__, default=str),
                ttl=86400  # 24 hours
            )
            
            return creator_profile
            
        except Exception as e:
            logger.error(f"Creator profile creation failed: {str(e)}")
            # Return minimal profile
            return CreatorProfile(
                profile_id=str(uuid.uuid4()),
                user_id=user_id,
                creator_name=f"Creator_{user_id[:8]}",
                content_formats=[],
                genres_categories=[],
                skills_expertise=[],
                audience_demographics={},
                engagement_metrics={},
                collaboration_preferences={},
                availability_schedule={},
                geographic_location={},
                portfolio_highlights=[],
                social_media_presence={},
                collaboration_history=[],
                reputation_score=0.5
            )
    
    async def _generate_collaboration_opportunities(
        self,
        content_id: str,
        creator_profile: CreatorProfile,
        content_analysis: Dict[str, Any]
    ) -> List[CollaborationOpportunity]:
        """Generate collaboration opportunities based on content and profile"""
        try:
            opportunities = []
            suitable_types = content_analysis.get("suitable_collaboration_types", [])
            
            for collab_type in suitable_types:
                opportunity = await self._create_collaboration_opportunity(
                    content_id, creator_profile, CollaborationType(collab_type), content_analysis
                )
                opportunities.append(opportunity)
            
            return opportunities
            
        except Exception as e:
            logger.error(f"Opportunity generation failed: {str(e)}")
            return []
    
    async def _create_collaboration_opportunity(
        self,
        content_id: str,
        creator_profile: CreatorProfile,
        collaboration_type: CollaborationType,
        content_analysis: Dict[str, Any]
    ) -> CollaborationOpportunity:
        """Create a specific collaboration opportunity"""
        # Generate opportunity details based on collaboration type
        opportunity_templates = {
            CollaborationType.CROSS_PROMOTION: {
                "description": "Cross-promotional collaboration to expand audience reach",
                "requirements": {"min_followers": 1000, "engagement_rate": 0.03},
                "compensation_model": {"type": "mutual_promotion", "cost": 0},
                "timeline": {"duration_days": 14},
                "skills_needed": ["content_creation", "social_media_management"]
            },
            CollaborationType.CONTENT_REMIX: {
                "description": "Remix and enhance existing content with fresh perspective",
                "requirements": {"technical_skills": True, "portfolio_quality": 0.7},
                "compensation_model": {"type": "revenue_share", "percentage": 0.3},
                "timeline": {"duration_days": 21},
                "skills_needed": ["content_editing", "creative_direction"]
            },
            CollaborationType.JOINT_CREATION: {
                "description": "Collaborative content creation from concept to completion",
                "requirements": {"collaboration_experience": True, "time_commitment": "high"},
                "compensation_model": {"type": "equal_split", "percentage": 0.5},
                "timeline": {"duration_days": 30},
                "skills_needed": ["project_management", "creative_collaboration"]
            }
        }
        
        template = opportunity_templates.get(collaboration_type, opportunity_templates[CollaborationType.CROSS_PROMOTION])
        
        return CollaborationOpportunity(
            opportunity_id=str(uuid.uuid4()),
            creator_id=creator_profile.user_id,
            content_id=content_id,
            collaboration_type=collaboration_type,
            description=template["description"],
            requirements=template["requirements"],
            compensation_model=template["compensation_model"],
            timeline={
                "start_date": datetime.utcnow() + timedelta(days=3),
                "end_date": datetime.utcnow() + timedelta(days=template["timeline"]["duration_days"])
            },
            target_demographics=content_analysis.get("target_demographics", {}),
            success_metrics={"engagement_increase": 0.2, "reach_expansion": 0.3},
            collaboration_terms={"exclusivity": False, "attribution_required": True},
            geographic_scope=["global"],
            budget_range={"min": 0, "max": 500},
            skills_needed=template["skills_needed"]
        )
    
    async def _find_matching_creators(
        self,
        opportunity: CollaborationOpportunity,
        primary_creator: CreatorProfile
    ) -> List[CollaborationMatch]:
        """Find creators that match the collaboration opportunity"""
        try:
            # Get potential creators from database
            potential_creators = await self._get_potential_creators(
                opportunity, primary_creator
            )
            
            matches = []
            for creator in potential_creators:
                # Calculate match score
                match_score = await self._calculate_match_score(
                    opportunity, primary_creator, creator
                )
                
                if match_score > 0.3:  # Minimum threshold
                    # Analyze compatibility
                    compatibility_analysis = await self._analyze_creator_compatibility(
                        primary_creator, creator, opportunity
                    )
                    
                    # Assess risks
                    risk_assessment = await self._assess_collaboration_risks(
                        primary_creator, creator, opportunity
                    )
                    
                    # Calculate success probability
                    success_probability = await self._calculate_success_probability(
                        match_score, compatibility_analysis, risk_assessment
                    )
                    
                    # Generate mutual benefits
                    mutual_benefits = await self._identify_mutual_benefits(
                        primary_creator, creator, opportunity
                    )
                    
                    match = CollaborationMatch(
                        match_id=str(uuid.uuid4()),
                        opportunity_id=opportunity.opportunity_id,
                        matched_creator_id=creator.user_id,
                        primary_creator_id=primary_creator.user_id,
                        match_score=match_score,
                        confidence_level=self._determine_confidence_level(match_score),
                        matching_factors=await self._calculate_matching_factors(
                            opportunity, primary_creator, creator
                        ),
                        compatibility_analysis=compatibility_analysis,
                        potential_outcomes=await self._predict_collaboration_outcomes(
                            primary_creator, creator, opportunity
                        ),
                        recommended_terms=await self._generate_recommended_terms(
                            primary_creator, creator, opportunity
                        ),
                        risk_assessment=risk_assessment,
                        success_probability=success_probability,
                        mutual_benefits=mutual_benefits,
                        collaboration_roadmap=await self._create_collaboration_roadmap(
                            primary_creator, creator, opportunity
                        )
                    )
                    
                    matches.append(match)
            
            return matches
            
        except Exception as e:
            logger.error(f"Creator matching failed: {str(e)}")
            return []
    
    async def _calculate_match_score(
        self,
        opportunity: CollaborationOpportunity,
        primary_creator: CreatorProfile,
        potential_creator: CreatorProfile
    ) -> float:
        """Calculate overall match score between creators for opportunity"""
        try:
            scores = {}
            
            # Content similarity score
            scores[MatchingCriteria.CONTENT_SIMILARITY] = await self._calculate_content_similarity(
                primary_creator, potential_creator
            )
            
            # Audience overlap score
            scores[MatchingCriteria.AUDIENCE_OVERLAP] = await self._calculate_audience_overlap(
                primary_creator, potential_creator
            )
            
            # Complementary skills score
            scores[MatchingCriteria.COMPLEMENTARY_SKILLS] = await self._calculate_skill_complementarity(
                primary_creator, potential_creator, opportunity
            )
            
            # Engagement compatibility score
            scores[MatchingCriteria.ENGAGEMENT_COMPATIBILITY] = await self._calculate_engagement_compatibility(
                primary_creator, potential_creator
            )
            
            # Brand alignment score
            scores[MatchingCriteria.BRAND_ALIGNMENT] = await self._calculate_brand_alignment(
                primary_creator, potential_creator
            )
            
            # Geographic proximity score
            scores[MatchingCriteria.GEOGRAPHIC_PROXIMITY] = await self._calculate_geographic_proximity(
                primary_creator, potential_creator
            )
            
            # Schedule compatibility score
            scores[MatchingCriteria.SCHEDULE_COMPATIBILITY] = await self._calculate_schedule_compatibility(
                primary_creator, potential_creator
            )
            
            # Budget compatibility score
            scores[MatchingCriteria.BUDGET_COMPATIBILITY] = await self._calculate_budget_compatibility(
                primary_creator, potential_creator, opportunity
            )
            
            # Calculate weighted average
            weighted_score = sum(
                scores.get(criteria, 0.0) * weight 
                for criteria, weight in self.matching_weights.items()
            )
            
            return min(weighted_score, 1.0)
            
        except Exception as e:
            logger.error(f"Match score calculation failed: {str(e)}")
            return 0.0
    
    def _determine_confidence_level(self, match_score: float) -> MatchingConfidence:
        """Determine confidence level based on match score"""
        if match_score >= 0.85:
            return MatchingConfidence.EXCELLENT
        elif match_score >= 0.7:
            return MatchingConfidence.HIGH
        elif match_score >= 0.5:
            return MatchingConfidence.MEDIUM
        else:
            return MatchingConfidence.LOW
    
    async def _rank_collaboration_matches(
        self,
        matches: List[CollaborationMatch],
        creator_profile: CreatorProfile,
        content_analysis: Dict[str, Any]
    ) -> List[CollaborationMatch]:
        """Rank collaboration matches by relevance and potential"""
        try:
            # Sort by match score and success probability
            ranked_matches = sorted(
                matches,
                key=lambda m: (m.match_score * 0.6 + m.success_probability * 0.4),
                reverse=True
            )
            
            # Apply additional filtering based on creator preferences
            filtered_matches = await self._filter_matches_by_preferences(
                ranked_matches, creator_profile
            )
            
            return filtered_matches
            
        except Exception as e:
            logger.error(f"Match ranking failed: {str(e)}")
            return matches
    
    def _calculate_collaboration_score(
        self,
        content_analysis: Dict[str, Any],
        opportunities: List[CollaborationOpportunity],
        matches: List[CollaborationMatch]
    ) -> float:
        """Calculate overall collaboration score"""
        try:
            # Base score from content collaboration potential
            base_score = content_analysis.get("collaboration_potential", 0.5)
            
            # Opportunities bonus
            opportunities_bonus = min(len(opportunities) * 0.1, 0.3)
            
            # Matches quality bonus
            if matches:
                avg_match_score = sum(m.match_score for m in matches) / len(matches)
                matches_bonus = avg_match_score * 0.4
            else:
                matches_bonus = 0
            
            return min(base_score + opportunities_bonus + matches_bonus, 1.0)
            
        except Exception as e:
            logger.error(f"Collaboration score calculation failed: {str(e)}")
            return 0.5
    
    # Helper methods (implementation details)
    async def _get_user_data(self, user_id: str) -> Dict[str, Any]:
        """Get user data from database"""
        # Implementation for retrieving user data
        return {"display_name": f"Creator_{user_id[:8]}", "location": {}}
    
    async def _analyze_user_content_history(self, user_id: str) -> Dict[str, Any]:
        """Analyze user's content history"""
        # Implementation for content history analysis
        return {"genres": [], "performance_metrics": {}}
    
    async def _extract_skills_and_expertise(
        self, 
        user_data: Dict[str, Any], 
        content_history: Dict[str, Any], 
        content_data: Dict[str, Any]
    ) -> List[str]:
        """Extract skills and expertise from user data"""
        # Implementation for skill extraction
        return ["content_creation", "social_media"]
    
    # Additional helper methods would be implemented here...


# Factory function for creating collaboration matcher
def create_collaboration_matcher(
    cache_manager: CacheManager,
    event_emitter: EventEmitter
) -> CollaborationMatcher:
    """Factory function to create collaboration matcher instance"""
    return CollaborationMatcher(cache_manager, event_emitter)
