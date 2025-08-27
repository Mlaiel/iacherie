"""
Collaboration & Partnership Intelligence Module

Advanced AI system for intelligent creator matching, partnership optimization,
and collaborative opportunity identification for maximum synergy and growth.

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.

⚠️ UNAUTHORIZED USE STRICTLY PROHIBITED ⚠️
This cutting-edge collaboration intelligence system is protected proprietary technology.
Any unauthorized use, copying, or distribution will trigger immediate legal action.

Business Logic: Profile Analysis → Compatibility Assessment → Partnership Discovery → Collaboration Optimization → Synergy Maximization → Growth Amplification
"""

import asyncio
import json
import uuid
import hashlib
from typing import Dict, List, Any, Optional, Set, Tuple, Union, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import logging
from collections import defaultdict
import math
import statistics

# NLP and similarity analysis
try:
    import spacy
    from transformers import AutoTokenizer, AutoModel
    import torch
    import numpy as np
    from sklearn.metrics.pairwise import cosine_similarity
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.cluster import KMeans
    NLP_SIMILARITY_AVAILABLE = True
except ImportError:
    NLP_SIMILARITY_AVAILABLE = False

# Network analysis
try:
    import networkx as nx
    from community import community_louvain
    NETWORK_ANALYSIS_AVAILABLE = True
except ImportError:
    NETWORK_ANALYSIS_AVAILABLE = False

from .exceptions import OptimizationError, ConfigurationError
from .metrics import metrics_collector
from .performance import performance_monitor
from .content_types import ContentType
from .multi_platform_intelligence import Platform

logger = logging.getLogger(__name__)


class CollaborationType(Enum):
    """Types of collaborations"""
    CONTENT_EXCHANGE = "content_exchange"
    JOINT_PROJECT = "joint_project"
    CROSS_PROMOTION = "cross_promotion"
    GUEST_APPEARANCE = "guest_appearance"
    SPONSORED_COLLABORATION = "sponsored_collaboration"
    SKILL_EXCHANGE = "skill_exchange"
    AUDIENCE_SHARING = "audience_sharing"
    BRAND_PARTNERSHIP = "brand_partnership"
    MENTORSHIP = "mentorship"
    CO_CREATION = "co_creation"
    EVENT_COLLABORATION = "event_collaboration"
    RESOURCE_SHARING = "resource_sharing"


class CreatorCategory(Enum):
    """Creator categories for matching"""
    MUSICIAN = "musician"
    BLOGGER = "blogger"
    PHOTOGRAPHER = "photographer"
    INFLUENCER = "influencer"
    COMEDIAN = "comedian"
    CHEF = "chef"
    FITNESS_TRAINER = "fitness_trainer"
    TRAVEL_CREATOR = "travel_creator"
    TECH_REVIEWER = "tech_reviewer"
    BEAUTY_GURU = "beauty_guru"
    GAMER = "gamer"
    EDUCATOR = "educator"
    ARTIST = "artist"
    ENTREPRENEUR = "entrepreneur"
    LIFESTYLE_CREATOR = "lifestyle_creator"


class CompatibilityFactor(Enum):
    """Factors for compatibility assessment"""
    AUDIENCE_OVERLAP = "audience_overlap"
    CONTENT_SYNERGY = "content_synergy"
    BRAND_ALIGNMENT = "brand_alignment"
    ENGAGEMENT_SIMILARITY = "engagement_similarity"
    PLATFORM_COMPATIBILITY = "platform_compatibility"
    SCHEDULE_COMPATIBILITY = "schedule_compatibility"
    VALUE_ALIGNMENT = "value_alignment"
    SKILL_COMPLEMENTARITY = "skill_complementarity"
    GEOGRAPHIC_PROXIMITY = "geographic_proximity"
    LANGUAGE_COMPATIBILITY = "language_compatibility"


class PartnershipStatus(Enum):
    """Partnership status"""
    DISCOVERED = "discovered"
    CONTACTED = "contacted"
    NEGOTIATING = "negotiating"
    ACTIVE = "active"
    COMPLETED = "completed"
    PAUSED = "paused"
    CANCELLED = "cancelled"


@dataclass
class CreatorProfile:
    """Comprehensive creator profile for matching"""
    creator_id: str
    name: str
    category: CreatorCategory
    platforms: List[Platform]
    
    # Audience data
    total_followers: int = 0
    engagement_rate: float = 0.0
    audience_demographics: Dict[str, Any] = field(default_factory=dict)
    audience_interests: List[str] = field(default_factory=list)
    audience_locations: List[str] = field(default_factory=list)
    
    # Content data
    content_themes: List[str] = field(default_factory=list)
    content_formats: List[str] = field(default_factory=list)
    posting_frequency: str = "weekly"
    content_quality_score: float = 0.8
    
    # Brand & values
    brand_keywords: List[str] = field(default_factory=list)
    values: List[str] = field(default_factory=list)
    collaboration_interests: List[CollaborationType] = field(default_factory=list)
    
    # Performance metrics
    average_views: int = 0
    average_engagement: int = 0
    growth_rate: float = 0.0
    
    # Collaboration history
    past_collaborations: List[str] = field(default_factory=list)
    collaboration_success_rate: float = 0.5
    
    # Preferences
    preferred_collaboration_types: List[CollaborationType] = field(default_factory=list)
    collaboration_budget: Optional[float] = None
    availability: Dict[str, Any] = field(default_factory=dict)
    
    # Contact & social
    contact_info: Dict[str, str] = field(default_factory=dict)
    social_links: Dict[str, str] = field(default_factory=dict)
    location: Optional[str] = None
    timezone: Optional[str] = None
    languages: List[str] = field(default_factory=list)
    
    # AI-generated insights
    personality_traits: List[str] = field(default_factory=list)
    collaboration_style: str = "flexible"
    influence_score: float = 0.5
    
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "creator_id": self.creator_id,
            "name": self.name,
            "category": self.category.value,
            "platforms": [p.value for p in self.platforms],
            "audience": {
                "total_followers": self.total_followers,
                "engagement_rate": self.engagement_rate,
                "demographics": self.audience_demographics,
                "interests": self.audience_interests,
                "locations": self.audience_locations
            },
            "content": {
                "themes": self.content_themes,
                "formats": self.content_formats,
                "frequency": self.posting_frequency,
                "quality_score": self.content_quality_score
            },
            "brand": {
                "keywords": self.brand_keywords,
                "values": self.values,
                "collaboration_interests": [c.value for c in self.collaboration_interests]
            },
            "performance": {
                "average_views": self.average_views,
                "average_engagement": self.average_engagement,
                "growth_rate": self.growth_rate
            },
            "collaboration": {
                "past_collaborations": self.past_collaborations,
                "success_rate": self.collaboration_success_rate,
                "preferred_types": [c.value for c in self.preferred_collaboration_types],
                "budget": self.collaboration_budget,
                "availability": self.availability
            },
            "contact": {
                "info": self.contact_info,
                "social_links": self.social_links,
                "location": self.location,
                "timezone": self.timezone,
                "languages": self.languages
            },
            "insights": {
                "personality_traits": self.personality_traits,
                "collaboration_style": self.collaboration_style,
                "influence_score": self.influence_score
            },
            "timestamps": {
                "created_at": self.created_at.isoformat(),
                "updated_at": self.updated_at.isoformat()
            }
        }


@dataclass
class CompatibilityScore:
    """Compatibility assessment between creators"""
    compatibility_id: str
    creator_1_id: str
    creator_2_id: str
    overall_score: float
    
    # Factor-specific scores
    factor_scores: Dict[CompatibilityFactor, float] = field(default_factory=dict)
    
    # Detailed analysis
    strengths: List[str] = field(default_factory=list)
    potential_challenges: List[str] = field(default_factory=list)
    synergy_opportunities: List[str] = field(default_factory=list)
    
    # Recommendations
    recommended_collaboration_types: List[CollaborationType] = field(default_factory=list)
    optimal_collaboration_timing: Optional[datetime] = None
    suggested_platforms: List[Platform] = field(default_factory=list)
    
    # Success prediction
    predicted_success_rate: float = 0.5
    confidence_level: float = 0.7
    risk_factors: List[str] = field(default_factory=list)
    
    calculated_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: datetime = field(default=datetime.utcnow() + timedelta(days=30))
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "compatibility_id": self.compatibility_id,
            "creator_1_id": self.creator_1_id,
            "creator_2_id": self.creator_2_id,
            "overall_score": self.overall_score,
            "factor_scores": {k.value: v for k, v in self.factor_scores.items()},
            "analysis": {
                "strengths": self.strengths,
                "challenges": self.potential_challenges,
                "opportunities": self.synergy_opportunities
            },
            "recommendations": {
                "collaboration_types": [c.value for c in self.recommended_collaboration_types],
                "optimal_timing": self.optimal_collaboration_timing.isoformat() if self.optimal_collaboration_timing else None,
                "suggested_platforms": [p.value for p in self.suggested_platforms]
            },
            "prediction": {
                "success_rate": self.predicted_success_rate,
                "confidence": self.confidence_level,
                "risk_factors": self.risk_factors
            },
            "timestamps": {
                "calculated_at": self.calculated_at.isoformat(),
                "expires_at": self.expires_at.isoformat()
            }
        }


@dataclass
class CollaborationOpportunity:
    """Identified collaboration opportunity"""
    opportunity_id: str
    primary_creator_id: str
    partner_creator_ids: List[str]
    collaboration_type: CollaborationType
    
    # Opportunity details
    title: str
    description: str
    estimated_reach: int
    estimated_engagement: float
    potential_roi: float
    
    # Requirements
    required_resources: Dict[str, Any] = field(default_factory=dict)
    timeline: Dict[str, datetime] = field(default_factory=dict)
    budget_requirements: Optional[float] = None
    
    # Benefits analysis
    benefits_primary: List[str] = field(default_factory=list)
    benefits_partners: List[str] = field(default_factory=list)
    mutual_benefits: List[str] = field(default_factory=list)
    
    # Execution plan
    suggested_steps: List[Dict[str, Any]] = field(default_factory=list)
    platform_strategy: Dict[Platform, Dict[str, Any]] = field(default_factory=dict)
    content_plan: List[Dict[str, Any]] = field(default_factory=list)
    
    # Success metrics
    kpis: Dict[str, float] = field(default_factory=dict)
    success_criteria: List[str] = field(default_factory=list)
    
    # Status tracking
    status: PartnershipStatus = PartnershipStatus.DISCOVERED
    priority: str = "medium"  # "low", "medium", "high", "urgent"
    
    created_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: datetime = field(default=datetime.utcnow() + timedelta(days=60))
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "opportunity_id": self.opportunity_id,
            "primary_creator_id": self.primary_creator_id,
            "partner_creator_ids": self.partner_creator_ids,
            "collaboration_type": self.collaboration_type.value,
            "details": {
                "title": self.title,
                "description": self.description,
                "estimated_reach": self.estimated_reach,
                "estimated_engagement": self.estimated_engagement,
                "potential_roi": self.potential_roi
            },
            "requirements": {
                "resources": self.required_resources,
                "timeline": {k: v.isoformat() for k, v in self.timeline.items()},
                "budget": self.budget_requirements
            },
            "benefits": {
                "primary": self.benefits_primary,
                "partners": self.benefits_partners,
                "mutual": self.mutual_benefits
            },
            "execution": {
                "steps": self.suggested_steps,
                "platform_strategy": {p.value: strategy for p, strategy in self.platform_strategy.items()},
                "content_plan": self.content_plan
            },
            "success": {
                "kpis": self.kpis,
                "criteria": self.success_criteria
            },
            "meta": {
                "status": self.status.value,
                "priority": self.priority,
                "created_at": self.created_at.isoformat(),
                "expires_at": self.expires_at.isoformat()
            }
        }


@dataclass
class PartnershipTracker:
    """Track active partnership performance"""
    partnership_id: str
    opportunity_id: str
    creators: List[str]
    collaboration_type: CollaborationType
    
    # Performance tracking
    launch_date: datetime
    performance_metrics: Dict[str, List[float]] = field(default_factory=dict)
    milestone_achievements: List[Dict[str, Any]] = field(default_factory=list)
    
    # Real-time stats
    current_reach: int = 0
    current_engagement: float = 0.0
    roi_tracking: float = 0.0
    
    # Health indicators
    partnership_health: float = 0.8
    creator_satisfaction: Dict[str, float] = field(default_factory=dict)
    content_performance: Dict[str, float] = field(default_factory=dict)
    
    # Issues and resolutions
    reported_issues: List[Dict[str, Any]] = field(default_factory=list)
    resolutions: List[Dict[str, Any]] = field(default_factory=list)
    
    status: PartnershipStatus = PartnershipStatus.ACTIVE
    last_updated: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "partnership_id": self.partnership_id,
            "opportunity_id": self.opportunity_id,
            "creators": self.creators,
            "collaboration_type": self.collaboration_type.value,
            "performance": {
                "launch_date": self.launch_date.isoformat(),
                "metrics": self.performance_metrics,
                "milestones": self.milestone_achievements
            },
            "current_stats": {
                "reach": self.current_reach,
                "engagement": self.current_engagement,
                "roi": self.roi_tracking
            },
            "health": {
                "partnership_health": self.partnership_health,
                "creator_satisfaction": self.creator_satisfaction,
                "content_performance": self.content_performance
            },
            "issues": {
                "reported": self.reported_issues,
                "resolutions": self.resolutions
            },
            "status": self.status.value,
            "last_updated": self.last_updated.isoformat()
        }


class CreatorCompatibilityEngine:
    """Engine for assessing creator compatibility and synergy"""
    
    def __init__(self):
        self.compatibility_cache = {}
        self.nlp_processor = None
        self.similarity_models = {}
        self._initialize_nlp()
    
    def _initialize_nlp(self):
        """Initialize NLP processing capabilities"""
        if NLP_SIMILARITY_AVAILABLE:
            try:
                # Initialize spaCy model for semantic analysis
                self.nlp_processor = spacy.load("en_core_web_sm")
                
                # Initialize TF-IDF vectorizer for content similarity
                self.tfidf_vectorizer = TfidfVectorizer(
                    max_features=5000,
                    stop_words='english',
                    ngram_range=(1, 2)
                )
                
                logger.info("NLP compatibility analysis initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize NLP: {e}")
    
    async def calculate_compatibility(self, 
                                    creator1: CreatorProfile,
                                    creator2: CreatorProfile,
                                    collaboration_type: Optional[CollaborationType] = None) -> CompatibilityScore:
        """Calculate comprehensive compatibility between creators"""
        try:
            # Check cache
            cache_key = f"{creator1.creator_id}_{creator2.creator_id}_{collaboration_type.value if collaboration_type else 'general'}"
            if cache_key in self.compatibility_cache:
                cached_result = self.compatibility_cache[cache_key]
                if cached_result.expires_at > datetime.utcnow():
                    return cached_result
            
            # Calculate individual factor scores
            factor_scores = {}
            
            # Audience overlap analysis
            factor_scores[CompatibilityFactor.AUDIENCE_OVERLAP] = await self._calculate_audience_overlap(creator1, creator2)
            
            # Content synergy analysis
            factor_scores[CompatibilityFactor.CONTENT_SYNERGY] = await self._calculate_content_synergy(creator1, creator2)
            
            # Brand alignment analysis
            factor_scores[CompatibilityFactor.BRAND_ALIGNMENT] = await self._calculate_brand_alignment(creator1, creator2)
            
            # Engagement similarity
            factor_scores[CompatibilityFactor.ENGAGEMENT_SIMILARITY] = self._calculate_engagement_similarity(creator1, creator2)
            
            # Platform compatibility
            factor_scores[CompatibilityFactor.PLATFORM_COMPATIBILITY] = self._calculate_platform_compatibility(creator1, creator2)
            
            # Value alignment
            factor_scores[CompatibilityFactor.VALUE_ALIGNMENT] = await self._calculate_value_alignment(creator1, creator2)
            
            # Skill complementarity
            factor_scores[CompatibilityFactor.SKILL_COMPLEMENTARITY] = self._calculate_skill_complementarity(creator1, creator2)
            
            # Geographic proximity (if applicable)
            factor_scores[CompatibilityFactor.GEOGRAPHIC_PROXIMITY] = self._calculate_geographic_compatibility(creator1, creator2)
            
            # Language compatibility
            factor_scores[CompatibilityFactor.LANGUAGE_COMPATIBILITY] = self._calculate_language_compatibility(creator1, creator2)
            
            # Calculate overall score with weights
            overall_score = self._calculate_weighted_score(factor_scores, collaboration_type)
            
            # Generate insights and recommendations
            strengths, challenges, opportunities = self._analyze_compatibility_insights(creator1, creator2, factor_scores)
            recommended_types = self._recommend_collaboration_types(creator1, creator2, factor_scores)
            suggested_platforms = self._suggest_optimal_platforms(creator1, creator2, factor_scores)
            
            # Predict success rate
            success_prediction = self._predict_collaboration_success(creator1, creator2, factor_scores, collaboration_type)
            
            # Create compatibility score object
            compatibility = CompatibilityScore(
                compatibility_id=str(uuid.uuid4()),
                creator_1_id=creator1.creator_id,
                creator_2_id=creator2.creator_id,
                overall_score=overall_score,
                factor_scores=factor_scores,
                strengths=strengths,
                potential_challenges=challenges,
                synergy_opportunities=opportunities,
                recommended_collaboration_types=recommended_types,
                suggested_platforms=suggested_platforms,
                predicted_success_rate=success_prediction["success_rate"],
                confidence_level=success_prediction["confidence"],
                risk_factors=success_prediction["risk_factors"]
            )
            
            # Cache result
            self.compatibility_cache[cache_key] = compatibility
            
            return compatibility
            
        except Exception as e:
            logger.error(f"Compatibility calculation failed: {e}")
            raise OptimizationError(f"Failed to calculate compatibility: {str(e)}")
    
    async def _calculate_audience_overlap(self, creator1: CreatorProfile, creator2: CreatorProfile) -> float:
        """Calculate audience overlap score"""
        try:
            overlap_score = 0.0
            
            # Demographics overlap
            demo1 = creator1.audience_demographics
            demo2 = creator2.audience_demographics
            
            if demo1 and demo2:
                # Age group overlap
                age1 = set(demo1.get("age_groups", []))
                age2 = set(demo2.get("age_groups", []))
                age_overlap = len(age1.intersection(age2)) / max(len(age1.union(age2)), 1)
                
                # Gender overlap
                gender1 = demo1.get("gender_distribution", {})
                gender2 = demo2.get("gender_distribution", {})
                gender_similarity = self._calculate_distribution_similarity(gender1, gender2)
                
                overlap_score += (age_overlap + gender_similarity) / 2 * 0.3
            
            # Interest overlap
            interests1 = set(creator1.audience_interests)
            interests2 = set(creator2.audience_interests)
            
            if interests1 and interests2:
                interest_overlap = len(interests1.intersection(interests2)) / max(len(interests1.union(interests2)), 1)
                overlap_score += interest_overlap * 0.4
            
            # Location overlap
            locations1 = set(creator1.audience_locations)
            locations2 = set(creator2.audience_locations)
            
            if locations1 and locations2:
                location_overlap = len(locations1.intersection(locations2)) / max(len(locations1.union(locations2)), 1)
                overlap_score += location_overlap * 0.3
            
            # Adjust for follower count similarity (similar sizes work better together)
            follower_ratio = min(creator1.total_followers, creator2.total_followers) / max(creator1.total_followers, creator2.total_followers, 1)
            if follower_ratio > 0.1:  # Avoid division by zero and too large disparities
                overlap_score *= (1 + follower_ratio) / 2
            
            return min(1.0, overlap_score)
            
        except Exception as e:
            logger.error(f"Audience overlap calculation failed: {e}")
            return 0.5
    
    async def _calculate_content_synergy(self, creator1: CreatorProfile, creator2: CreatorProfile) -> float:
        """Calculate content synergy potential"""
        try:
            synergy_score = 0.0
            
            # Theme compatibility
            themes1 = set(creator1.content_themes)
            themes2 = set(creator2.content_themes)
            
            if themes1 and themes2:
                # Perfect overlap might indicate competition, moderate overlap indicates synergy
                theme_overlap = len(themes1.intersection(themes2)) / max(len(themes1.union(themes2)), 1)
                # Optimal overlap is around 0.3-0.7 for synergy
                if 0.2 <= theme_overlap <= 0.8:
                    synergy_score += 0.4 * (1 - abs(theme_overlap - 0.5) * 2)
                else:
                    synergy_score += theme_overlap * 0.2
            
            # Format complementarity
            formats1 = set(creator1.content_formats)
            formats2 = set(creator2.content_formats)
            
            if formats1 and formats2:
                format_diversity = len(formats1.union(formats2)) / max(len(formats1), len(formats2), 1)
                synergy_score += min(format_diversity * 0.3, 0.3)
            
            # Quality alignment
            quality_diff = abs(creator1.content_quality_score - creator2.content_quality_score)
            quality_alignment = 1 - quality_diff
            synergy_score += quality_alignment * 0.3
            
            # Use NLP for semantic similarity if available
            if NLP_SIMILARITY_AVAILABLE and self.nlp_processor:
                try:
                    content_text1 = " ".join(creator1.content_themes + creator1.brand_keywords)
                    content_text2 = " ".join(creator2.content_themes + creator2.brand_keywords)
                    
                    if content_text1 and content_text2:
                        doc1 = self.nlp_processor(content_text1)
                        doc2 = self.nlp_processor(content_text2)
                        
                        semantic_similarity = doc1.similarity(doc2)
                        synergy_score += semantic_similarity * 0.2
                except Exception as e:
                    logger.warning(f"NLP similarity calculation failed: {e}")
            
            return min(1.0, synergy_score)
            
        except Exception as e:
            logger.error(f"Content synergy calculation failed: {e}")
            return 0.5
    
    async def _calculate_brand_alignment(self, creator1: CreatorProfile, creator2: CreatorProfile) -> float:
        """Calculate brand alignment score"""
        try:
            alignment_score = 0.0
            
            # Keyword similarity
            keywords1 = set(creator1.brand_keywords)
            keywords2 = set(creator2.brand_keywords)
            
            if keywords1 and keywords2:
                keyword_similarity = len(keywords1.intersection(keywords2)) / max(len(keywords1.union(keywords2)), 1)
                alignment_score += keyword_similarity * 0.4
            
            # Values alignment
            values1 = set(creator1.values)
            values2 = set(creator2.values)
            
            if values1 and values2:
                values_alignment = len(values1.intersection(values2)) / max(len(values1.union(values2)), 1)
                alignment_score += values_alignment * 0.6
            
            return min(1.0, alignment_score)
            
        except Exception as e:
            logger.error(f"Brand alignment calculation failed: {e}")
            return 0.5
    
    def _calculate_engagement_similarity(self, creator1: CreatorProfile, creator2: CreatorProfile) -> float:
        """Calculate engagement rate similarity"""
        try:
            if creator1.engagement_rate == 0 and creator2.engagement_rate == 0:
                return 1.0
            
            max_engagement = max(creator1.engagement_rate, creator2.engagement_rate)
            min_engagement = min(creator1.engagement_rate, creator2.engagement_rate)
            
            if max_engagement == 0:
                return 1.0
            
            similarity = min_engagement / max_engagement
            return similarity
            
        except Exception as e:
            logger.error(f"Engagement similarity calculation failed: {e}")
            return 0.5
    
    def _calculate_platform_compatibility(self, creator1: CreatorProfile, creator2: CreatorProfile) -> float:
        """Calculate platform compatibility"""
        try:
            platforms1 = set(creator1.platforms)
            platforms2 = set(creator2.platforms)
            
            if not platforms1 or not platforms2:
                return 0.5
            
            # Shared platforms enable easier collaboration
            shared_platforms = len(platforms1.intersection(platforms2))
            total_platforms = len(platforms1.union(platforms2))
            
            compatibility = shared_platforms / total_platforms if total_platforms > 0 else 0
            
            # Bonus for having at least one shared major platform
            major_platforms = {Platform.YOUTUBE, Platform.INSTAGRAM, Platform.TIKTOK}
            shared_major = len(platforms1.intersection(platforms2).intersection(major_platforms))
            
            if shared_major > 0:
                compatibility += 0.2
            
            return min(1.0, compatibility)
            
        except Exception as e:
            logger.error(f"Platform compatibility calculation failed: {e}")
            return 0.5
    
    async def _calculate_value_alignment(self, creator1: CreatorProfile, creator2: CreatorProfile) -> float:
        """Calculate value alignment using NLP"""
        try:
            values1 = creator1.values
            values2 = creator2.values
            
            if not values1 or not values2:
                return 0.5
            
            # Simple overlap calculation
            values_set1 = set([v.lower() for v in values1])
            values_set2 = set([v.lower() for v in values2])
            
            overlap = len(values_set1.intersection(values_set2)) / max(len(values_set1.union(values_set2)), 1)
            
            # Use NLP for semantic similarity if available
            if NLP_SIMILARITY_AVAILABLE and self.nlp_processor:
                try:
                    values_text1 = " ".join(values1)
                    values_text2 = " ".join(values2)
                    
                    doc1 = self.nlp_processor(values_text1)
                    doc2 = self.nlp_processor(values_text2)
                    
                    semantic_similarity = doc1.similarity(doc2)
                    alignment = (overlap + semantic_similarity) / 2
                except Exception as e:
                    logger.warning(f"Values NLP similarity failed: {e}")
                    alignment = overlap
            else:
                alignment = overlap
            
            return alignment
            
        except Exception as e:
            logger.error(f"Value alignment calculation failed: {e}")
            return 0.5
    
    def _calculate_skill_complementarity(self, creator1: CreatorProfile, creator2: CreatorProfile) -> float:
        """Calculate skill complementarity"""
        try:
            # Different categories often bring complementary skills
            if creator1.category != creator2.category:
                base_complementarity = 0.7
            else:
                base_complementarity = 0.3
            
            # Content format diversity adds complementarity
            formats1 = set(creator1.content_formats)
            formats2 = set(creator2.content_formats)
            
            if formats1 and formats2:
                format_diversity = len(formats1.union(formats2)) / max(len(formats1), len(formats2), 1)
                base_complementarity += format_diversity * 0.3
            
            return min(1.0, base_complementarity)
            
        except Exception as e:
            logger.error(f"Skill complementarity calculation failed: {e}")
            return 0.5
    
    def _calculate_geographic_compatibility(self, creator1: CreatorProfile, creator2: CreatorProfile) -> float:
        """Calculate geographic compatibility"""
        try:
            loc1 = creator1.location
            loc2 = creator2.location
            
            if not loc1 or not loc2:
                return 0.7  # Neutral score for unknown locations
            
            # Simple string matching (in real implementation, use geo-location services)
            if loc1.lower() == loc2.lower():
                return 1.0
            
            # Check if in same country (simplified)
            if any(word in loc1.lower() and word in loc2.lower() for word in ['usa', 'uk', 'canada', 'australia', 'germany']):
                return 0.8
            
            return 0.5  # Default for different locations
            
        except Exception as e:
            logger.error(f"Geographic compatibility calculation failed: {e}")
            return 0.7
    
    def _calculate_language_compatibility(self, creator1: CreatorProfile, creator2: CreatorProfile) -> float:
        """Calculate language compatibility"""
        try:
            langs1 = set([lang.lower() for lang in creator1.languages])
            langs2 = set([lang.lower() for lang in creator2.languages])
            
            if not langs1 or not langs2:
                return 0.8  # Assume English by default
            
            shared_languages = len(langs1.intersection(langs2))
            
            if shared_languages > 0:
                return 1.0
            else:
                return 0.2  # Low score for no shared languages
            
        except Exception as e:
            logger.error(f"Language compatibility calculation failed: {e}")
            return 0.8
    
    def _calculate_weighted_score(self, 
                                factor_scores: Dict[CompatibilityFactor, float],
                                collaboration_type: Optional[CollaborationType]) -> float:
        """Calculate weighted overall compatibility score"""
        try:
            # Default weights
            weights = {
                CompatibilityFactor.AUDIENCE_OVERLAP: 0.2,
                CompatibilityFactor.CONTENT_SYNERGY: 0.2,
                CompatibilityFactor.BRAND_ALIGNMENT: 0.15,
                CompatibilityFactor.ENGAGEMENT_SIMILARITY: 0.1,
                CompatibilityFactor.PLATFORM_COMPATIBILITY: 0.15,
                CompatibilityFactor.VALUE_ALIGNMENT: 0.1,
                CompatibilityFactor.SKILL_COMPLEMENTARITY: 0.05,
                CompatibilityFactor.GEOGRAPHIC_PROXIMITY: 0.025,
                CompatibilityFactor.LANGUAGE_COMPATIBILITY: 0.025
            }
            
            # Adjust weights based on collaboration type
            if collaboration_type:
                if collaboration_type == CollaborationType.CONTENT_EXCHANGE:
                    weights[CompatibilityFactor.CONTENT_SYNERGY] *= 1.5
                    weights[CompatibilityFactor.PLATFORM_COMPATIBILITY] *= 1.3
                
                elif collaboration_type == CollaborationType.BRAND_PARTNERSHIP:
                    weights[CompatibilityFactor.BRAND_ALIGNMENT] *= 1.5
                    weights[CompatibilityFactor.VALUE_ALIGNMENT] *= 1.3
                
                elif collaboration_type == CollaborationType.CROSS_PROMOTION:
                    weights[CompatibilityFactor.AUDIENCE_OVERLAP] *= 0.8  # Less overlap preferred
                    weights[CompatibilityFactor.SKILL_COMPLEMENTARITY] *= 1.5
            
            # Normalize weights to sum to 1
            total_weight = sum(weights.values())
            normalized_weights = {k: v/total_weight for k, v in weights.items()}
            
            # Calculate weighted score
            weighted_score = sum(
                factor_scores.get(factor, 0.5) * weight
                for factor, weight in normalized_weights.items()
            )
            
            return min(1.0, max(0.0, weighted_score))
            
        except Exception as e:
            logger.error(f"Weighted score calculation failed: {e}")
            return 0.5
    
    def _analyze_compatibility_insights(self, 
                                      creator1: CreatorProfile,
                                      creator2: CreatorProfile,
                                      factor_scores: Dict[CompatibilityFactor, float]) -> Tuple[List[str], List[str], List[str]]:
        """Analyze compatibility and generate insights"""
        strengths = []
        challenges = []
        opportunities = []
        
        try:
            # Analyze each factor
            for factor, score in factor_scores.items():
                if score >= 0.8:
                    if factor == CompatibilityFactor.AUDIENCE_OVERLAP:
                        strengths.append("Strong audience overlap indicates shared target market")
                    elif factor == CompatibilityFactor.CONTENT_SYNERGY:
                        strengths.append("Excellent content synergy for collaborative projects")
                    elif factor == CompatibilityFactor.BRAND_ALIGNMENT:
                        strengths.append("Strong brand alignment supports authentic partnerships")
                    elif factor == CompatibilityFactor.PLATFORM_COMPATIBILITY:
                        strengths.append("Shared platforms enable seamless collaboration")
                
                elif score <= 0.3:
                    if factor == CompatibilityFactor.AUDIENCE_OVERLAP:
                        opportunities.append("Low audience overlap offers cross-promotion potential")
                    elif factor == CompatibilityFactor.CONTENT_SYNERGY:
                        challenges.append("Content styles may require careful coordination")
                    elif factor == CompatibilityFactor.BRAND_ALIGNMENT:
                        challenges.append("Brand differences need to be addressed")
                    elif factor == CompatibilityFactor.ENGAGEMENT_SIMILARITY:
                        challenges.append("Different engagement levels may create imbalance")
            
            # Cross-factor insights
            if (factor_scores.get(CompatibilityFactor.SKILL_COMPLEMENTARITY, 0) > 0.7 and
                factor_scores.get(CompatibilityFactor.AUDIENCE_OVERLAP, 0) < 0.5):
                opportunities.append("Complementary skills with distinct audiences ideal for knowledge exchange")
            
            if (creator1.category != creator2.category and
                factor_scores.get(CompatibilityFactor.BRAND_ALIGNMENT, 0) > 0.6):
                opportunities.append("Different creator types with aligned values offer unique collaboration angles")
            
            return strengths, challenges, opportunities
            
        except Exception as e:
            logger.error(f"Compatibility insights analysis failed: {e}")
            return [], [], []
    
    def _recommend_collaboration_types(self, 
                                     creator1: CreatorProfile,
                                     creator2: CreatorProfile,
                                     factor_scores: Dict[CompatibilityFactor, float]) -> List[CollaborationType]:
        """Recommend optimal collaboration types"""
        recommendations = []
        
        try:
            audience_overlap = factor_scores.get(CompatibilityFactor.AUDIENCE_OVERLAP, 0.5)
            content_synergy = factor_scores.get(CompatibilityFactor.CONTENT_SYNERGY, 0.5)
            brand_alignment = factor_scores.get(CompatibilityFactor.BRAND_ALIGNMENT, 0.5)
            skill_complementarity = factor_scores.get(CompatibilityFactor.SKILL_COMPLEMENTARITY, 0.5)
            platform_compatibility = factor_scores.get(CompatibilityFactor.PLATFORM_COMPATIBILITY, 0.5)
            
            # Content exchange works well with high content synergy and platform compatibility
            if content_synergy > 0.7 and platform_compatibility > 0.6:
                recommendations.append(CollaborationType.CONTENT_EXCHANGE)
            
            # Cross-promotion works well with low-medium audience overlap and high skill complementarity
            if 0.2 <= audience_overlap <= 0.6 and skill_complementarity > 0.6:
                recommendations.append(CollaborationType.CROSS_PROMOTION)
            
            # Joint projects require high brand alignment and content synergy
            if brand_alignment > 0.7 and content_synergy > 0.7:
                recommendations.append(CollaborationType.JOINT_PROJECT)
            
            # Guest appearances work with medium-high audience overlap
            if audience_overlap > 0.5:
                recommendations.append(CollaborationType.GUEST_APPEARANCE)
            
            # Skill exchange works with high skill complementarity
            if skill_complementarity > 0.8:
                recommendations.append(CollaborationType.SKILL_EXCHANGE)
            
            # Brand partnerships require excellent brand alignment
            if brand_alignment > 0.8 and platform_compatibility > 0.6:
                recommendations.append(CollaborationType.BRAND_PARTNERSHIP)
            
            return recommendations[:3]  # Return top 3 recommendations
            
        except Exception as e:
            logger.error(f"Collaboration type recommendation failed: {e}")
            return [CollaborationType.CROSS_PROMOTION]
    
    def _suggest_optimal_platforms(self, 
                                 creator1: CreatorProfile,
                                 creator2: CreatorProfile,
                                 factor_scores: Dict[CompatibilityFactor, float]) -> List[Platform]:
        """Suggest optimal platforms for collaboration"""
        try:
            shared_platforms = list(set(creator1.platforms).intersection(set(creator2.platforms)))
            
            # Sort by popularity and reach potential
            platform_priority = [
                Platform.YOUTUBE,
                Platform.INSTAGRAM,
                Platform.TIKTOK,
                Platform.TWITTER,
                Platform.FACEBOOK,
                Platform.LINKEDIN
            ]
            
            suggested = []
            for platform in platform_priority:
                if platform in shared_platforms:
                    suggested.append(platform)
            
            # Add remaining shared platforms
            for platform in shared_platforms:
                if platform not in suggested:
                    suggested.append(platform)
            
            return suggested[:3]  # Return top 3 platforms
            
        except Exception as e:
            logger.error(f"Platform suggestion failed: {e}")
            return []
    
    def _predict_collaboration_success(self, 
                                     creator1: CreatorProfile,
                                     creator2: CreatorProfile,
                                     factor_scores: Dict[CompatibilityFactor, float],
                                     collaboration_type: Optional[CollaborationType]) -> Dict[str, Any]:
        """Predict collaboration success probability"""
        try:
            # Base success rate from overall compatibility
            overall_score = sum(factor_scores.values()) / len(factor_scores)
            base_success_rate = overall_score * 0.8  # Conservative estimate
            
            # Adjust based on historical performance
            historical_factor = (creator1.collaboration_success_rate + creator2.collaboration_success_rate) / 2
            success_rate = (base_success_rate + historical_factor) / 2
            
            # Confidence based on data completeness
            data_completeness = self._calculate_data_completeness(creator1, creator2)
            confidence = data_completeness * 0.8
            
            # Identify risk factors
            risk_factors = []
            
            if factor_scores.get(CompatibilityFactor.BRAND_ALIGNMENT, 0.5) < 0.4:
                risk_factors.append("Brand misalignment may cause conflicts")
            
            if factor_scores.get(CompatibilityFactor.ENGAGEMENT_SIMILARITY, 0.5) < 0.3:
                risk_factors.append("Significant engagement rate differences")
            
            if abs(creator1.total_followers - creator2.total_followers) > creator1.total_followers * 5:
                risk_factors.append("Large follower count disparity")
            
            if not set(creator1.platforms).intersection(set(creator2.platforms)):
                risk_factors.append("No shared platforms for collaboration")
            
            return {
                "success_rate": min(1.0, success_rate),
                "confidence": confidence,
                "risk_factors": risk_factors
            }
            
        except Exception as e:
            logger.error(f"Success prediction failed: {e}")
            return {
                "success_rate": 0.5,
                "confidence": 0.5,
                "risk_factors": ["Prediction analysis unavailable"]
            }
    
    def _calculate_data_completeness(self, creator1: CreatorProfile, creator2: CreatorProfile) -> float:
        """Calculate data completeness for confidence assessment"""
        try:
            required_fields = [
                'total_followers', 'engagement_rate', 'audience_demographics',
                'content_themes', 'brand_keywords', 'platforms'
            ]
            
            completeness1 = sum(1 for field in required_fields if getattr(creator1, field, None))
            completeness2 = sum(1 for field in required_fields if getattr(creator2, field, None))
            
            avg_completeness = (completeness1 + completeness2) / (2 * len(required_fields))
            return avg_completeness
            
        except Exception as e:
            logger.error(f"Data completeness calculation failed: {e}")
            return 0.5
    
    def _calculate_distribution_similarity(self, dist1: Dict, dist2: Dict) -> float:
        """Calculate similarity between two distributions"""
        try:
            if not dist1 or not dist2:
                return 0.5
            
            all_keys = set(dist1.keys()).union(set(dist2.keys()))
            
            similarity = 0.0
            for key in all_keys:
                val1 = dist1.get(key, 0)
                val2 = dist2.get(key, 0)
                similarity += 1 - abs(val1 - val2)
            
            return similarity / len(all_keys) if all_keys else 0.5
            
        except Exception as e:
            logger.error(f"Distribution similarity calculation failed: {e}")
            return 0.5


# Global collaboration intelligence system
collaboration_engine = CreatorCompatibilityEngine()
