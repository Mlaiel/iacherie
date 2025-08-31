"""Collaborative Intelligence Module - Advanced Creator Matching & Collaboration AI

Enterprise-grade AI system for intelligent creator matching, collaboration discovery,
and cross-platform partnership optimization.

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.

⚠️ UNAUTHORIZED USE STRICTLY PROHIBITED ⚠️
This innovative AI collaboration system is protected intellectual property.
Any unauthorized copying, distribution, or use will result in immediate legal action.

Business Logic: AI-Driven Creator Discovery → Compatibility Analysis → Collaboration Matching → Revenue Optimization
"""
import asyncio
import json
import uuid
import numpy as np
from typing import Dict, List, Any, Optional, Set, Tuple, Union, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import logging
from collections import defaultdict
import hashlib

# AI/ML imports
try:
    import torch
    import torch.nn as nn
    import torch.nn.functional as F
    from transformers import AutoModel, AutoTokenizer
    from sklearn.metrics.pairwise import cosine_similarity
    from sklearn.cluster import KMeans
    import networkx as nx
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

from .exceptions import CollaborationError, OptimizationError
from .metrics import metrics_collector
from .performance import performance_monitor

logger = logging.getLogger(__name__)


class CollaborationType(Enum):
    """Types of creator collaborations"""    CONTENT_COLLABORATION = "content_collaboration"
    CROSS_PROMOTION = "cross_promotion"
    JOINT_PROJECT = "joint_project"
    SKILL_EXCHANGE = "skill_exchange"
    MENTORSHIP = "mentorship"
    BRAND_PARTNERSHIP = "brand_partnership"
    EVENT_COLLABORATION = "event_collaboration"
    CREATIVE_CHALLENGE = "creative_challenge"
    REMIX_COLLABORATION = "remix_collaboration"
    SERIES_COLLABORATION = "series_collaboration"


class CreatorCategory(Enum):
    """Creator categories for matching"""    MUSICIAN = "musician"
    BLOGGER = "blogger"
    PHOTOGRAPHER = "photographer"
    VIDEOGRAPHER = "videographer"
    INFLUENCER = "influencer"
    COMEDIAN = "comedian"
    ARTIST = "artist"
    PODCASTER = "podcaster"
    DESIGNER = "designer"
    DANCER = "dancer"
    WRITER = "writer"
    CHEF = "chef"
    FITNESS_TRAINER = "fitness_trainer"
    EDUCATOR = "educator"


class CompatibilityFactor(Enum):
    """Factors for creator compatibility analysis"""    CONTENT_STYLE = "content_style"
    AUDIENCE_OVERLAP = "audience_overlap"
    GENRE_SIMILARITY = "genre_similarity"
    QUALITY_LEVEL = "quality_level"
    ENGAGEMENT_RATE = "engagement_rate"
    BRAND_ALIGNMENT = "brand_alignment"
    SCHEDULE_COMPATIBILITY = "schedule_compatibility"
    GEOGRAPHIC_PROXIMITY = "geographic_proximity"
    LANGUAGE_COMPATIBILITY = "language_compatibility"
    PLATFORM_SYNERGY = "platform_synergy"


@dataclass
class CreatorProfile:
    """Comprehensive creator profile for collaboration matching"""    user_id: str
    username: str
    category: CreatorCategory
    bio: str
    tags: List[str] = field(default_factory=list)
    content_types: List[str] = field(default_factory=list)
    platforms: List[str] = field(default_factory=list)
    followers_count: int = 0
    engagement_rate: float = 0.0
    content_quality_score: float = 0.0
    brand_safety_score: float = 0.0
    collaboration_history: List[str] = field(default_factory=list)
    preferred_collaborations: List[CollaborationType] = field(default_factory=list)
    location: Optional[str] = None
    languages: List[str] = field(default_factory=list)
    availability_schedule: Dict[str, Any] = field(default_factory=dict)
    contact_preferences: Dict[str, Any] = field(default_factory=dict)
    portfolio_links: List[str] = field(default_factory=list)
    revenue_sharing_willingness: bool = False
    cross_platform_promotion: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class CollaborationMatch:
    """Collaboration match result"""    match_id: str
    creator_a: str
    creator_b: str
    collaboration_type: CollaborationType
    compatibility_score: float
    factors_analysis: Dict[CompatibilityFactor, float]
    suggested_projects: List[Dict[str, Any]]
    estimated_reach: int
    estimated_engagement: float
    revenue_potential: float
    risk_assessment: Dict[str, float]
    recommended_platforms: List[str]
    timeline_suggestion: Dict[str, Any]
    match_confidence: float
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class CollaborationNetwork:
    """Creator collaboration network representation"""    network_id: str
    creators: List[str]
    connections: List[Tuple[str, str, float]]  # (creator1, creator2, strength)
    clusters: Dict[str, List[str]]
    influence_scores: Dict[str, float]
    network_density: float
    avg_path_length: float
    created_at: datetime = field(default_factory=datetime.utcnow)


class CreatorCompatibilityAnalyzer:
    """Advanced creator compatibility analysis using AI"""    
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self._initialize_ai_models()
    
    def _initialize_ai_models(self):
        """Initialize AI models for compatibility analysis"""        if TORCH_AVAILABLE:
            try:
                self.tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
                self.model = AutoModel.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
                logger.info("Creator compatibility AI models initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize AI models: {e}")
    
    async def analyze_compatibility(self, 
                                  creator_a: CreatorProfile, 
                                  creator_b: CreatorProfile) -> Dict[CompatibilityFactor, float]:
        """Analyze compatibility between two creators"""        try:
            compatibility = {}
            
            # Content style similarity
            compatibility[CompatibilityFactor.CONTENT_STYLE] = await self._analyze_content_style_similarity(
                creator_a, creator_b
            )
            
            # Audience overlap analysis
            compatibility[CompatibilityFactor.AUDIENCE_OVERLAP] = await self._calculate_audience_overlap(
                creator_a, creator_b
            )
            
            # Genre/category similarity
            compatibility[CompatibilityFactor.GENRE_SIMILARITY] = self._calculate_genre_similarity(
                creator_a, creator_b
            )
            
            # Quality level matching
            compatibility[CompatibilityFactor.QUALITY_LEVEL] = self._calculate_quality_compatibility(
                creator_a, creator_b
            )
            
            # Engagement rate compatibility
            compatibility[CompatibilityFactor.ENGAGEMENT_RATE] = self._calculate_engagement_compatibility(
                creator_a, creator_b
            )
            
            # Platform synergy
            compatibility[CompatibilityFactor.PLATFORM_SYNERGY] = self._calculate_platform_synergy(
                creator_a, creator_b
            )
            
            # Geographic proximity
            compatibility[CompatibilityFactor.GEOGRAPHIC_PROXIMITY] = self._calculate_geographic_compatibility(
                creator_a, creator_b
            )
            
            # Language compatibility
            compatibility[CompatibilityFactor.LANGUAGE_COMPATIBILITY] = self._calculate_language_compatibility(
                creator_a, creator_b
            )
            
            # Schedule compatibility
            compatibility[CompatibilityFactor.SCHEDULE_COMPATIBILITY] = self._calculate_schedule_compatibility(
                creator_a, creator_b
            )
            
            # Brand alignment
            compatibility[CompatibilityFactor.BRAND_ALIGNMENT] = await self._analyze_brand_alignment(
                creator_a, creator_b
            )
            
            return compatibility
            
        except Exception as e:
            logger.error(f"Error analyzing creator compatibility: {e}")
            raise CollaborationError(f"Compatibility analysis failed: {str(e)}")
    
    async def _analyze_content_style_similarity(self, 
                                               creator_a: CreatorProfile, 
                                               creator_b: CreatorProfile) -> float:
        """Analyze content style similarity using AI"""        if not self.model or not self.tokenizer:
            return 0.5  # Default neutral score
        
        try:
            # Combine bio and tags for style analysis
            text_a = f"{creator_a.bio} {' '.join(creator_a.tags)}"
            text_b = f"{creator_b.bio} {' '.join(creator_b.tags)}"
            
            # Encode texts
            inputs_a = self.tokenizer(text_a, return_tensors="pt", truncation=True, max_length=512)
            inputs_b = self.tokenizer(text_b, return_tensors="pt", truncation=True, max_length=512)
            
            with torch.no_grad():
                embeddings_a = self.model(**inputs_a).last_hidden_state.mean(dim=1)
                embeddings_b = self.model(**inputs_b).last_hidden_state.mean(dim=1)
            
            # Calculate cosine similarity
            similarity = F.cosine_similarity(embeddings_a, embeddings_b).item()
            return max(0.0, min(1.0, similarity))
            
        except Exception as e:
            logger.warning(f"Content style analysis failed: {e}")
            return 0.5
    
    async def _calculate_audience_overlap(self, 
                                         creator_a: CreatorProfile, 
                                         creator_b: CreatorProfile) -> float:
        """Calculate estimated audience overlap"""        try:
            # Tag-based overlap calculation
            tags_a = set(creator_a.tags)
            tags_b = set(creator_b.tags)
            
            if not tags_a or not tags_b:
                return 0.3  # Default low overlap
            
            overlap = len(tags_a.intersection(tags_b))
            total_unique = len(tags_a.union(tags_b))
            
            jaccard_similarity = overlap / total_unique if total_unique > 0 else 0.0
            
            # Adjust based on follower counts (similar sized audiences likely have more overlap)
            follower_ratio = min(creator_a.followers_count, creator_b.followers_count) / \
                           max(creator_a.followers_count, creator_b.followers_count) if \
                           max(creator_a.followers_count, creator_b.followers_count) > 0 else 0.5
            
            audience_overlap = (jaccard_similarity * 0.7) + (follower_ratio * 0.3)
            return max(0.0, min(1.0, audience_overlap))
            
        except Exception as e:
            logger.warning(f"Audience overlap calculation failed: {e}")
            return 0.3
    
    def _calculate_genre_similarity(self, 
                                  creator_a: CreatorProfile, 
                                  creator_b: CreatorProfile) -> float:
        """Calculate genre/category similarity"""        try:
            # Same category gets high score
            if creator_a.category == creator_b.category:
                return 0.9
            
            # Content type overlap
            types_a = set(creator_a.content_types)
            types_b = set(creator_b.content_types)
            
            if not types_a or not types_b:
                return 0.2
            
            overlap = len(types_a.intersection(types_b))
            total = len(types_a.union(types_b))
            
            return overlap / total if total > 0 else 0.2
            
        except Exception as e:
            logger.warning(f"Genre similarity calculation failed: {e}")
            return 0.2
    
    def _calculate_quality_compatibility(self, 
                                       creator_a: CreatorProfile, 
                                       creator_b: CreatorProfile) -> float:
        """Calculate quality level compatibility"""        try:
            diff = abs(creator_a.content_quality_score - creator_b.content_quality_score)
            # Lower difference = higher compatibility
            compatibility = max(0.0, 1.0 - (diff / 100.0))  # Assuming quality scores are 0-100
            return compatibility
            
        except Exception as e:
            logger.warning(f"Quality compatibility calculation failed: {e}")
            return 0.5
    
    def _calculate_engagement_compatibility(self, 
                                          creator_a: CreatorProfile, 
                                          creator_b: CreatorProfile) -> float:
        """Calculate engagement rate compatibility"""        try:
            # Similar engagement rates indicate compatible audiences
            diff = abs(creator_a.engagement_rate - creator_b.engagement_rate)
            compatibility = max(0.0, 1.0 - (diff / 20.0))  # Assuming max 20% engagement rate
            return compatibility
            
        except Exception as e:
            logger.warning(f"Engagement compatibility calculation failed: {e}")
            return 0.5
    
    def _calculate_platform_synergy(self, 
                                   creator_a: CreatorProfile, 
                                   creator_b: CreatorProfile) -> float:
        """Calculate platform synergy"""        try:
            platforms_a = set(creator_a.platforms)
            platforms_b = set(creator_b.platforms)
            
            # Some overlap is good, but complementary platforms are also valuable
            overlap = len(platforms_a.intersection(platforms_b))
            unique_platforms = len(platforms_a.union(platforms_b))
            
            # Balance between overlap and unique reach
            if unique_platforms == 0:
                return 0.0
            
            synergy = (overlap / len(platforms_a) if platforms_a else 0) * 0.4 + \
                     (unique_platforms / 10.0) * 0.6  # Assuming max 10 major platforms
            
            return max(0.0, min(1.0, synergy))
            
        except Exception as e:
            logger.warning(f"Platform synergy calculation failed: {e}")
            return 0.5
    
    def _calculate_geographic_compatibility(self, 
                                          creator_a: CreatorProfile, 
                                          creator_b: CreatorProfile) -> float:
        """Calculate geographic compatibility"""        try:
            if not creator_a.location or not creator_b.location:
                return 0.5  # Neutral if location unknown
            
            # Simple same-location check (can be enhanced with actual geographic distance)
            if creator_a.location.lower() == creator_b.location.lower():
                return 1.0
            
            # Same country/region logic could be added here
            return 0.3  # Different locations but still possible
            
        except Exception as e:
            logger.warning(f"Geographic compatibility calculation failed: {e}")
            return 0.5
    
    def _calculate_language_compatibility(self, 
                                        creator_a: CreatorProfile, 
                                        creator_b: CreatorProfile) -> float:
        """Calculate language compatibility"""        try:
            langs_a = set(creator_a.languages)
            langs_b = set(creator_b.languages)
            
            if not langs_a or not langs_b:
                return 0.5
            
            overlap = len(langs_a.intersection(langs_b))
            return overlap / min(len(langs_a), len(langs_b)) if overlap > 0 else 0.1
            
        except Exception as e:
            logger.warning(f"Language compatibility calculation failed: {e}")
            return 0.5
    
    def _calculate_schedule_compatibility(self, 
                                        creator_a: CreatorProfile, 
                                        creator_b: CreatorProfile) -> float:
        """Calculate schedule compatibility"""        try:
            # This is a placeholder - in real implementation, would analyze time zones,
            # posting schedules, availability windows, etc.
            return 0.7  # Default good compatibility
            
        except Exception as e:
            logger.warning(f"Schedule compatibility calculation failed: {e}")
            return 0.5
    
    async def _analyze_brand_alignment(self, 
                                      creator_a: CreatorProfile, 
                                      creator_b: CreatorProfile) -> float:
        """Analyze brand alignment and safety"""        try:
            # Brand safety score compatibility
            safety_compatibility = 1.0 - abs(creator_a.brand_safety_score - creator_b.brand_safety_score) / 100.0
            
            # Content alignment through AI analysis (simplified)
            content_alignment = await self._analyze_content_style_similarity(creator_a, creator_b)
            
            # Combine scores
            brand_alignment = (safety_compatibility * 0.6) + (content_alignment * 0.4)
            return max(0.0, min(1.0, brand_alignment))
            
        except Exception as e:
            logger.warning(f"Brand alignment analysis failed: {e}")
            return 0.5


class CollaborationMatchingEngine:
    """Advanced collaboration matching engine with AI"""    
    def __init__(self):
        self.compatibility_analyzer = CreatorCompatibilityAnalyzer()
        self.creator_profiles: Dict[str, CreatorProfile] = {}
        self.collaboration_history: Dict[str, List[Dict]] = defaultdict(list)
        self._initialize_matching_algorithms()
    
    def _initialize_matching_algorithms(self):
        """Initialize AI matching algorithms"""        logger.info("Collaboration matching engine initialized")
    
    async def find_collaboration_matches(self, 
                                        creator_id: str,
                                        collaboration_types: List[CollaborationType],
                                        max_matches: int = 10) -> List[CollaborationMatch]:
        """Find collaboration matches for a creator"""        try:
            if creator_id not in self.creator_profiles:
                raise CollaborationError(f"Creator profile not found: {creator_id}")
            
            creator = self.creator_profiles[creator_id]
            matches = []
            
            # Analyze compatibility with all other creators
            for other_id, other_creator in self.creator_profiles.items():
                if other_id == creator_id:
                    continue
                
                # Check if collaboration types are compatible
                compatible_types = self._get_compatible_collaboration_types(
                    creator, other_creator, collaboration_types
                )
                
                if not compatible_types:
                    continue
                
                # Analyze compatibility
                compatibility_factors = await self.compatibility_analyzer.analyze_compatibility(
                    creator, other_creator
                )
                
                # Calculate overall compatibility score
                overall_score = self._calculate_overall_compatibility_score(compatibility_factors)
                
                if overall_score > 0.3:  # Minimum threshold
                    for collab_type in compatible_types:
                        match = await self._create_collaboration_match(
                            creator, other_creator, collab_type, 
                            overall_score, compatibility_factors
                        )
                        matches.append(match)
            
            # Sort by compatibility score and return top matches
            matches.sort(key=lambda x: x.compatibility_score, reverse=True)
            return matches[:max_matches]
            
        except Exception as e:
            logger.error(f"Error finding collaboration matches: {e}")
            raise CollaborationError(f"Match finding failed: {str(e)}")
    
    def _get_compatible_collaboration_types(self, 
                                          creator_a: CreatorProfile,
                                          creator_b: CreatorProfile,
                                          requested_types: List[CollaborationType]) -> List[CollaborationType]:
        """Determine compatible collaboration types"""        compatible = []
        
        for collab_type in requested_types:
            # Check if both creators support this collaboration type
            if (collab_type in creator_a.preferred_collaborations or 
                not creator_a.preferred_collaborations) and \
               (collab_type in creator_b.preferred_collaborations or 
                not creator_b.preferred_collaborations):
                compatible.append(collab_type)
        
        return compatible
    
    def _calculate_overall_compatibility_score(self, 
                                             factors: Dict[CompatibilityFactor, float]) -> float:
        """Calculate weighted overall compatibility score"""        weights = {
            CompatibilityFactor.CONTENT_STYLE: 0.20,
            CompatibilityFactor.AUDIENCE_OVERLAP: 0.15,
            CompatibilityFactor.GENRE_SIMILARITY: 0.15,
            CompatibilityFactor.QUALITY_LEVEL: 0.15,
            CompatibilityFactor.ENGAGEMENT_RATE: 0.10,
            CompatibilityFactor.BRAND_ALIGNMENT: 0.10,
            CompatibilityFactor.PLATFORM_SYNERGY: 0.08,
            CompatibilityFactor.SCHEDULE_COMPATIBILITY: 0.05,
            CompatibilityFactor.LANGUAGE_COMPATIBILITY: 0.02,
        }
        
        total_score = 0.0
        total_weight = 0.0
        
        for factor, score in factors.items():
            weight = weights.get(factor, 0.0)
            total_score += score * weight
            total_weight += weight
        
        return total_score / total_weight if total_weight > 0 else 0.0
    
    async def _create_collaboration_match(self, 
                                         creator_a: CreatorProfile,
                                         creator_b: CreatorProfile,
                                         collaboration_type: CollaborationType,
                                         compatibility_score: float,
                                         factors: Dict[CompatibilityFactor, float]) -> CollaborationMatch:
        """Create a collaboration match object"""        try:
            # Generate suggested projects based on collaboration type and creator profiles
            suggested_projects = await self._generate_project_suggestions(
                creator_a, creator_b, collaboration_type
            )
            
            # Estimate reach and engagement
            estimated_reach = creator_a.followers_count + creator_b.followers_count
            estimated_engagement = (creator_a.engagement_rate + creator_b.engagement_rate) / 2
            
            # Calculate revenue potential
            revenue_potential = self._calculate_revenue_potential(creator_a, creator_b)
            
            # Risk assessment
            risk_assessment = self._assess_collaboration_risks(creator_a, creator_b)
            
            # Platform recommendations
            recommended_platforms = self._recommend_collaboration_platforms(creator_a, creator_b)
            
            # Timeline suggestion
            timeline_suggestion = self._suggest_collaboration_timeline(collaboration_type)
            
            # Match confidence based on data completeness and score
            match_confidence = self._calculate_match_confidence(
                creator_a, creator_b, compatibility_score
            )
            
            return CollaborationMatch(
                match_id=str(uuid.uuid4()),
                creator_a=creator_a.user_id,
                creator_b=creator_b.user_id,
                collaboration_type=collaboration_type,
                compatibility_score=compatibility_score,
                factors_analysis=factors,
                suggested_projects=suggested_projects,
                estimated_reach=estimated_reach,
                estimated_engagement=estimated_engagement,
                revenue_potential=revenue_potential,
                risk_assessment=risk_assessment,
                recommended_platforms=recommended_platforms,
                timeline_suggestion=timeline_suggestion,
                match_confidence=match_confidence
            )
            
        except Exception as e:
            logger.error(f"Error creating collaboration match: {e}")
            raise CollaborationError(f"Match creation failed: {str(e)}")
    
    async def _generate_project_suggestions(self, 
                                           creator_a: CreatorProfile,
                                           creator_b: CreatorProfile,
                                           collaboration_type: CollaborationType) -> List[Dict[str, Any]]:
        """Generate AI-powered project suggestions"""        suggestions = []
        
        # Base suggestions by collaboration type
        type_suggestions = {
            CollaborationType.CONTENT_COLLABORATION: [
                {"title": "Joint Tutorial Series", "description": "Create a series combining both creators' expertise"},
                {"title": "Challenge Video", "description": "Design a creative challenge showcasing both styles"},
                {"title": "Behind-the-Scenes Collab", "description": "Document the creative process together"}
            ],
            CollaborationType.CROSS_PROMOTION: [
                {"title": "Audience Swap", "description": "Feature each other's content to cross-audiences"},
                {"title": "Guest Appearances", "description": "Appear in each other's regular content"},
                {"title": "Joint Livestream", "description": "Host a collaborative live session"}
            ],
            CollaborationType.JOINT_PROJECT: [
                {"title": "Co-created Content Series", "description": "Launch a new content format together"},
                {"title": "Collaborative Product Launch", "description": "Create and launch a joint product/service"},
                {"title": "Event Collaboration", "description": "Organize and host a joint event or workshop"}
            ]
        }
        
        base_suggestions = type_suggestions.get(collaboration_type, [])
        
        # Customize suggestions based on creator profiles
        for suggestion in base_suggestions:
            customized = suggestion.copy()
            customized["estimated_duration"] = "2-4 weeks"
            customized["required_resources"] = ["Time", "Creative input", "Audience engagement"]
            customized["success_metrics"] = ["Reach", "Engagement", "Follower growth"]
            suggestions.append(customized)
        
        return suggestions[:5]  # Return top 5 suggestions
    
    def _calculate_revenue_potential(self, 
                                   creator_a: CreatorProfile, 
                                   creator_b: CreatorProfile) -> float:
        """Calculate estimated revenue potential"""        try:
            # Simple model based on followers and engagement
            base_revenue_a = creator_a.followers_count * creator_a.engagement_rate * 0.001
            base_revenue_b = creator_b.followers_count * creator_b.engagement_rate * 0.001
            
            # Collaboration multiplier (synergy effect)
            synergy_multiplier = 1.2 if creator_a.cross_platform_promotion and creator_b.cross_platform_promotion else 1.0
            
            revenue_potential = (base_revenue_a + base_revenue_b) * synergy_multiplier
            return min(revenue_potential, 10000.0)  # Cap at reasonable amount
            
        except Exception as e:
            logger.warning(f"Revenue potential calculation failed: {e}")
            return 100.0  # Default low potential
    
    def _assess_collaboration_risks(self, 
                                  creator_a: CreatorProfile, 
                                  creator_b: CreatorProfile) -> Dict[str, float]:
        """Assess potential collaboration risks"""        risks = {
            "brand_mismatch": 1.0 - min(creator_a.brand_safety_score, creator_b.brand_safety_score) / 100.0,
            "quality_gap": abs(creator_a.content_quality_score - creator_b.content_quality_score) / 100.0,
            "audience_reaction": 0.1,  # Base risk for audience reaction
            "schedule_conflict": 0.1,  # Base scheduling risk
            "communication_barrier": 0.05  # Base communication risk
        }
        
        # Adjust based on collaboration history
        if creator_a.collaboration_history or creator_b.collaboration_history:
            risks["collaboration_inexperience"] = 0.1
        else:
            risks["collaboration_inexperience"] = 0.3
        
        return risks
    
    def _recommend_collaboration_platforms(self, 
                                         creator_a: CreatorProfile, 
                                         creator_b: CreatorProfile) -> List[str]:
        """Recommend best platforms for collaboration"""        common_platforms = list(set(creator_a.platforms).intersection(set(creator_b.platforms)))
        unique_platforms = list(set(creator_a.platforms).union(set(creator_b.platforms)))
        
        # Prioritize common platforms for easier collaboration
        recommendations = common_platforms[:3] + [p for p in unique_platforms if p not in common_platforms][:2]
        
        return recommendations[:5]
    
    def _suggest_collaboration_timeline(self, collaboration_type: CollaborationType) -> Dict[str, Any]:
        """Suggest timeline for collaboration"""        timelines = {
            CollaborationType.CONTENT_COLLABORATION: {
                "planning_phase": "1 week",
                "content_creation": "2-3 weeks", 
                "post_production": "1 week",
                "promotion": "1 week",
                "total_duration": "5-6 weeks"
            },
            CollaborationType.CROSS_PROMOTION: {
                "planning_phase": "3 days",
                "execution": "1 week",
                "follow_up": "1 week", 
                "total_duration": "2-3 weeks"
            },
            CollaborationType.JOINT_PROJECT: {
                "planning_phase": "1-2 weeks",
                "development": "4-8 weeks",
                "launch": "1 week",
                "post_launch": "2 weeks",
                "total_duration": "8-13 weeks"
            }
        }
        
        return timelines.get(collaboration_type, {
            "planning_phase": "1 week",
            "execution": "2-4 weeks", 
            "follow_up": "1 week",
            "total_duration": "4-6 weeks"
        })
    
    def _calculate_match_confidence(self, 
                                  creator_a: CreatorProfile,
                                  creator_b: CreatorProfile,
                                  compatibility_score: float) -> float:
        """Calculate confidence level in the match"""        try:
            # Base confidence from compatibility score
            base_confidence = compatibility_score
            
            # Adjust based on profile completeness
            profile_completeness_a = self._calculate_profile_completeness(creator_a)
            profile_completeness_b = self._calculate_profile_completeness(creator_b)
            avg_completeness = (profile_completeness_a + profile_completeness_b) / 2
            
            # Adjust based on collaboration history
            history_factor = 0.1
            if creator_a.collaboration_history or creator_b.collaboration_history:
                history_factor = 0.2
            
            confidence = (base_confidence * 0.7) + (avg_completeness * 0.2) + history_factor
            return max(0.0, min(1.0, confidence))
            
        except Exception as e:
            logger.warning(f"Match confidence calculation failed: {e}")
            return 0.5
    
    def _calculate_profile_completeness(self, creator: CreatorProfile) -> float:
        """Calculate profile completeness score"""        fields_filled = 0
        total_fields = 0
        
        # Check essential fields
        essential_fields = [
            'bio', 'tags', 'content_types', 'platforms', 
            'location', 'languages', 'portfolio_links'
        ]
        
        for field in essential_fields:
            total_fields += 1
            value = getattr(creator, field, None)
            if value and (not isinstance(value, (list, dict)) or len(value) > 0):
                fields_filled += 1
        
        return fields_filled / total_fields if total_fields > 0 else 0.0
    
    async def add_creator_profile(self, profile: CreatorProfile):
        """Add a creator profile to the matching system"""        try:
            self.creator_profiles[profile.user_id] = profile
            logger.info(f"Added creator profile: {profile.username}")
            
        except Exception as e:
            logger.error(f"Error adding creator profile: {e}")
            raise CollaborationError(f"Profile addition failed: {str(e)}")
    
    async def update_creator_profile(self, profile: CreatorProfile):
        """Update a creator profile"""        try:
            if profile.user_id in self.creator_profiles:
                profile.updated_at = datetime.utcnow()
                self.creator_profiles[profile.user_id] = profile
                logger.info(f"Updated creator profile: {profile.username}")
            else:
                await self.add_creator_profile(profile)
                
        except Exception as e:
            logger.error(f"Error updating creator profile: {e}")
            raise CollaborationError(f"Profile update failed: {str(e)}")
    
    async def build_collaboration_network(self, creator_ids: List[str]) -> CollaborationNetwork:
        """Build a collaboration network graph"""        try:
            if TORCH_AVAILABLE and len(creator_ids) > 1:
                # Create network using NetworkX
                import networkx as nx
                
                G = nx.Graph()
                connections = []
                
                # Add nodes
                for creator_id in creator_ids:
                    if creator_id in self.creator_profiles:
                        G.add_node(creator_id)
                
                # Calculate connections between all pairs
                for i, creator_a_id in enumerate(creator_ids):
                    for creator_b_id in creator_ids[i+1:]:
                        if creator_a_id in self.creator_profiles and creator_b_id in self.creator_profiles:
                            creator_a = self.creator_profiles[creator_a_id]
                            creator_b = self.creator_profiles[creator_b_id]
                            
                            compatibility_factors = await self.compatibility_analyzer.analyze_compatibility(
                                creator_a, creator_b
                            )
                            strength = self._calculate_overall_compatibility_score(compatibility_factors)
                            
                            if strength > 0.3:  # Only add meaningful connections
                                G.add_edge(creator_a_id, creator_b_id, weight=strength)
                                connections.append((creator_a_id, creator_b_id, strength))
                
                # Calculate network metrics
                network_density = nx.density(G) if G.number_of_nodes() > 1 else 0.0
                
                try:
                    avg_path_length = nx.average_shortest_path_length(G) if nx.is_connected(G) else 0.0
                except:
                    avg_path_length = 0.0
                
                # Calculate influence scores (centrality)
                influence_scores = {}
                if G.number_of_nodes() > 0:
                    centrality = nx.degree_centrality(G)
                    influence_scores = {node: score for node, score in centrality.items()}
                
                # Detect communities/clusters
                clusters = {}
                if G.number_of_nodes() > 2:
                    try:
                        import community as community_louvain
                        partition = community_louvain.best_partition(G)
                        clusters = defaultdict(list)
                        for node, cluster_id in partition.items():
                            clusters[f"cluster_{cluster_id}"].append(node)
                    except:
                        # Simple fallback clustering
                        clusters["main_cluster"] = list(creator_ids)
                else:
                    clusters["main_cluster"] = list(creator_ids)
                
                return CollaborationNetwork(
                    network_id=str(uuid.uuid4()),
                    creators=creator_ids,
                    connections=connections,
                    clusters=dict(clusters),
                    influence_scores=influence_scores,
                    network_density=network_density,
                    avg_path_length=avg_path_length
                )
            
            else:
                # Fallback simple network
                return CollaborationNetwork(
                    network_id=str(uuid.uuid4()),
                    creators=creator_ids,
                    connections=[],
                    clusters={"main_cluster": creator_ids},
                    influence_scores={creator_id: 0.5 for creator_id in creator_ids},
                    network_density=0.0,
                    avg_path_length=0.0
                )
                
        except Exception as e:
            logger.error(f"Error building collaboration network: {e}")
            raise CollaborationError(f"Network building failed: {str(e)}")


# Global collaborative intelligence instance
collaborative_intelligence = CollaborationMatchingEngine()


class CollaborationRecommendationSystem:
    """Advanced recommendation system for collaboration opportunities"""    
    def __init__(self):
        self.matching_engine = collaborative_intelligence
        self.recommendation_history: Dict[str, List[Dict]] = defaultdict(list)
    
    async def get_personalized_recommendations(self, 
                                             creator_id: str,
                                             preferences: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Get personalized collaboration recommendations"""        try:
            preferences = preferences or {}
            
            # Get collaboration matches
            collaboration_types = preferences.get('collaboration_types', list(CollaborationType))
            matches = await self.matching_engine.find_collaboration_matches(
                creator_id, collaboration_types, max_matches=20
            )
            
            # Convert matches to recommendations with additional context
            recommendations = []
            for match in matches:
                recommendation = {
                    "match_id": match.match_id,
                    "recommended_creator": match.creator_b if match.creator_a == creator_id else match.creator_a,
                    "collaboration_type": match.collaboration_type.value,
                    "compatibility_score": match.compatibility_score,
                    "recommendation_reason": self._generate_recommendation_reason(match),
                    "suggested_first_step": self._suggest_first_step(match),
                    "success_probability": match.match_confidence,
                    "estimated_timeline": match.timeline_suggestion,
                    "recommended_platforms": match.recommended_platforms,
                    "revenue_potential": match.revenue_potential,
                    "risk_level": self._calculate_overall_risk_level(match.risk_assessment)
                }
                recommendations.append(recommendation)
            
            # Store recommendation history
            self.recommendation_history[creator_id].append({
                "timestamp": datetime.utcnow(),
                "recommendations": recommendations
            })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating personalized recommendations: {e}")
            raise CollaborationError(f"Recommendation generation failed: {str(e)}")
    
    def _generate_recommendation_reason(self, match: CollaborationMatch) -> str:
        """Generate human-readable recommendation reason"""        top_factors = sorted(
            match.factors_analysis.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:3]
        
        reasons = []
        for factor, score in top_factors:
            if score > 0.7:
                factor_name = factor.value.replace('_', ' ').title()
                reasons.append(f"High {factor_name}")
        
        if not reasons:
            reasons.append("Compatible creator profiles")
        
        return f"Recommended due to: {', '.join(reasons)}"
    
    def _suggest_first_step(self, match: CollaborationMatch) -> str:
        """Suggest the first step for initiating collaboration"""        suggestions = {
            CollaborationType.CONTENT_COLLABORATION: "Send a direct message introducing yourself and proposing a content idea",
            CollaborationType.CROSS_PROMOTION: "Reach out to propose featuring each other's content",
            CollaborationType.JOINT_PROJECT: "Schedule a video call to discuss project possibilities",
            CollaborationType.SKILL_EXCHANGE: "Propose a skill swap arrangement via private message",
            CollaborationType.MENTORSHIP: "Send a respectful message requesting mentorship opportunity",
        }
        
        return suggestions.get(
            match.collaboration_type,
            "Send a friendly introduction message expressing interest in collaboration"
        )
    
    def _calculate_overall_risk_level(self, risk_assessment: Dict[str, float]) -> str:
        """Calculate overall risk level"""        avg_risk = sum(risk_assessment.values()) / len(risk_assessment) if risk_assessment else 0.0
        
        if avg_risk < 0.3:
            return "Low"
        elif avg_risk < 0.6:
            return "Medium"
        else:
            return "High"


# Global recommendation system instance
recommendation_system = CollaborationRecommendationSystem()

# Global collaboration AI instance
collaboration_ai = CollaborationMatchingEngine()
