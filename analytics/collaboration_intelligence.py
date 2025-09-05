"""Collaboration Intelligence
=========================

Advanced creator collaboration and matching analytics system.
Analyzes collaboration patterns, success rates, and optimization opportunities.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: Fahed Mlaiel - All rights reserved
License: Proprietary - Unauthorized use prohibited

WARNING: This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution without explicit written
permission is strictly prohibited and will result in legal action.
Contact: mlaiel@live.de
"""

import asyncio
import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
import statistics
from collections import defaultdict, deque
import redis
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor


class CollaborationType(Enum):
    """Types of collaborations between creators"""
    MUSIC_COLLABORATION = "music_collaboration"
    VIDEO_COLLABORATION = "video_collaboration"
    CONTENT_CROSSOVER = "content_crossover"
    JOINT_CAMPAIGN = "joint_campaign"
    GUEST_APPEARANCE = "guest_appearance"
    CHALLENGE_PARTICIPATION = "challenge_participation"
    BRAND_PARTNERSHIP = "brand_partnership"
    LIVE_STREAM_COLLAB = "live_stream_collab"
    PODCAST_GUEST = "podcast_guest"
    REMIX_COLLABORATION = "remix_collaboration"


class CollaborationStatus(Enum):
    """Status of collaboration projects"""
    PROPOSED = "proposed"
    IN_NEGOTIATION = "in_negotiation"
    ACCEPTED = "accepted"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"


class MatchingCriteria(Enum):
    """Criteria for creator matching"""
    AUDIENCE_OVERLAP = "audience_overlap"
    CONTENT_SIMILARITY = "content_similarity"
    ENGAGEMENT_COMPATIBILITY = "engagement_compatibility"
    BRAND_ALIGNMENT = "brand_alignment"
    GENRE_COMPATIBILITY = "genre_compatibility"
    SCHEDULING_AVAILABILITY = "scheduling_availability"
    BUDGET_COMPATIBILITY = "budget_compatibility"
    GEOGRAPHIC_PROXIMITY = "geographic_proximity"


@dataclass
class CollaborationProject:
    """Individual collaboration project data"""
    project_id: str
    collaboration_type: CollaborationType
    primary_creator: str
    secondary_creators: List[str]
    status: CollaborationStatus
    proposed_date: datetime
    start_date: Optional[datetime] = None
    completion_date: Optional[datetime] = None
    target_metrics: Dict[str, float] = field(default_factory=dict)
    actual_metrics: Dict[str, float] = field(default_factory=dict)
    revenue_share: Dict[str, float] = field(default_factory=dict)
    success_score: Optional[float] = None
    feedback_scores: Dict[str, float] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CreatorProfile:
    """Creator profile for collaboration matching"""
    creator_id: str
    creator_type: str
    follower_count: int
    engagement_rate: float
    content_categories: List[str]
    target_demographics: Dict[str, Any]
    collaboration_history: List[str]
    success_rate: float
    availability_score: float
    brand_safety_score: float
    communication_score: float
    reliability_score: float
    preferred_collaboration_types: List[CollaborationType]
    geographic_location: str
    timezone: str
    languages: List[str]


@dataclass
class MatchingScore:
    """Collaboration matching score between creators"""
    creator_a: str
    creator_b: str
    overall_score: float
    criteria_scores: Dict[str, float]
    compatibility_factors: Dict[str, Any]
    success_probability: float
    recommended_collaboration_types: List[CollaborationType]
    potential_audience_reach: int
    estimated_engagement_boost: float
    revenue_potential: float
    calculated_at: datetime


@dataclass
class CollaborationAnalytics:
    """Comprehensive collaboration analytics"""
    time_period: Tuple[datetime, datetime]
    total_collaborations: int = 0
    successful_collaborations: int = 0
    failed_collaborations: int = 0
    average_success_rate: float = 0.0
    average_project_duration: float = 0.0  # days
    total_revenue_generated: float = 0.0
    average_revenue_per_collaboration: float = 0.0
    top_collaboration_types: Dict[str, int] = field(default_factory=dict)
    most_active_creators: List[Dict[str, Any]] = field(default_factory=list)
    success_factors: Dict[str, float] = field(default_factory=dict)
    platform_distribution: Dict[str, int] = field(default_factory=dict)
    geographic_distribution: Dict[str, int] = field(default_factory=dict)
    collaboration_trends: Dict[str, Any] = field(default_factory=dict)


class CollaborationIntelligence:
    """
    Advanced collaboration intelligence and matching analytics engine.
    
    Provides comprehensive creator matching, collaboration analytics,
    and optimization recommendations for successful partnerships.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Data storage
        self.collaboration_projects = deque(maxlen=10000)
        self.creator_profiles: Dict[str, CreatorProfile] = {}
        self.matching_scores = deque(maxlen=50000)
        self.analytics_history = deque(maxlen=1000)
        
        # ML models for collaboration optimization
        self.success_predictor = None
        self.matching_engine = None
        self.engagement_predictor = None
        
        # Redis for real-time matching
        self.redis_client = None
        self._initialize_redis()
        
        # Collaboration matching algorithms
        self.matching_algorithms = {
            "audience_overlap": self._calculate_audience_overlap,
            "content_similarity": self._calculate_content_similarity,
            "engagement_compatibility": self._calculate_engagement_compatibility,
            "brand_alignment": self._calculate_brand_alignment,
            "success_probability": self._predict_collaboration_success
        }
        
        # Success factors weights
        self.success_weights = {
            "audience_overlap": 0.25,
            "content_similarity": 0.20,
            "engagement_compatibility": 0.15,
            "brand_alignment": 0.15,
            "communication_score": 0.10,
            "reliability_score": 0.10,
            "availability_score": 0.05
        }
        
        # Initialize ML models
        self._ml_models_initialized = False
    
    def _initialize_redis(self):
        """Initialize Redis connection"""
        try:
            redis_host = self.config.get("redis_host", "localhost")
            redis_port = self.config.get("redis_port", 6379)
            self.redis_client = redis.Redis(
                host=redis_host, 
                port=redis_port, 
                decode_responses=True
            )
        except Exception as e:
            self.logger.warning(f"Redis connection failed: {e}")
    
    async def _initialize_ml_models(self):
        """Initialize ML models for collaboration optimization"""
        try:
            if self._ml_models_initialized:
                return
            
            # Success prediction model
            self.success_predictor = RandomForestClassifier(
                n_estimators=100, 
                random_state=42
            )
            
            # Engagement prediction model
            self.engagement_predictor = RandomForestRegressor(
                n_estimators=100, 
                random_state=42
            )
            
            # Creator clustering for matching
            self.matching_engine = KMeans(
                n_clusters=10, 
                random_state=42
            )
            
            self._ml_models_initialized = True
            self.logger.info("Collaboration ML models initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize ML models: {e}")
    
    async def register_creator_profile(
        self,
        creator_id: str,
        creator_type: str,
        follower_count: int,
        engagement_rate: float,
        content_categories: List[str],
        target_demographics: Dict[str, Any],
        geographic_location: str = "Unknown",
        timezone: str = "UTC",
        languages: List[str] = None
    ) -> CreatorProfile:
        """Register or update creator profile for collaboration matching"""
        try:
            # Calculate derived scores
            collaboration_history = await self._get_collaboration_history(creator_id)
            success_rate = await self._calculate_creator_success_rate(creator_id)
            
            profile = CreatorProfile(
                creator_id=creator_id,
                creator_type=creator_type,
                follower_count=follower_count,
                engagement_rate=engagement_rate,
                content_categories=content_categories,
                target_demographics=target_demographics,
                collaboration_history=collaboration_history,
                success_rate=success_rate,
                availability_score=0.8,  # Would be calculated from calendar/activity data
                brand_safety_score=0.9,  # Would be calculated from content analysis
                communication_score=0.85,  # Would be from feedback systems
                reliability_score=0.88,  # Would be from past performance
                preferred_collaboration_types=[CollaborationType.CONTENT_CROSSOVER],  # Default
                geographic_location=geographic_location,
                timezone=timezone,
                languages=languages or ["en"]
            )
            
            self.creator_profiles[creator_id] = profile
            
            # Cache in Redis
            if self.redis_client:
                await self._cache_creator_profile(profile)
            
            self.logger.info(f"Creator profile registered: {creator_id}")
            return profile
            
        except Exception as e:
            self.logger.error(f"Error registering creator profile: {e}")
            raise
    
    async def create_collaboration_project(
        self,
        collaboration_type: CollaborationType,
        primary_creator: str,
        secondary_creators: List[str],
        target_metrics: Dict[str, float] = None,
        revenue_share: Dict[str, float] = None,
        metadata: Dict[str, Any] = None
    ) -> CollaborationProject:
        """Create a new collaboration project"""
        try:
            project_id = f"collab_{int(datetime.now().timestamp())}_{hash(primary_creator) % 10000}"
            
            project = CollaborationProject(
                project_id=project_id,
                collaboration_type=collaboration_type,
                primary_creator=primary_creator,
                secondary_creators=secondary_creators,
                status=CollaborationStatus.PROPOSED,
                proposed_date=datetime.now(),
                target_metrics=target_metrics or {},
                revenue_share=revenue_share or {},
                metadata=metadata or {}
            )
            
            self.collaboration_projects.append(project)
            
            # Cache in Redis
            if self.redis_client:
                await self._cache_collaboration_project(project)
            
            self.logger.info(f"Collaboration project created: {project_id}")
            return project
            
        except Exception as e:
            self.logger.error(f"Error creating collaboration project: {e}")
            raise
    
    async def find_collaboration_matches(
        self,
        creator_id: str,
        collaboration_type: Optional[CollaborationType] = None,
        max_matches: int = 10,
        min_score_threshold: float = 0.6
    ) -> List[MatchingScore]:
        """Find potential collaboration matches for a creator"""
        try:
            if not self._ml_models_initialized:
                await self._initialize_ml_models()
            
            if creator_id not in self.creator_profiles:
                raise ValueError(f"Creator profile not found: {creator_id}")
            
            primary_creator = self.creator_profiles[creator_id]
            matches = []
            
            # Calculate matching scores with all other creators
            for other_creator_id, other_creator in self.creator_profiles.items():
                if other_creator_id == creator_id:
                    continue
                
                # Skip if collaboration type doesn't match preferences
                if collaboration_type and collaboration_type not in other_creator.preferred_collaboration_types:
                    continue
                
                # Calculate comprehensive matching score
                matching_score = await self._calculate_matching_score(
                    primary_creator, other_creator, collaboration_type
                )
                
                if matching_score.overall_score >= min_score_threshold:
                    matches.append(matching_score)
            
            # Sort by overall score and return top matches
            matches.sort(key=lambda x: x.overall_score, reverse=True)
            top_matches = matches[:max_matches]
            
            # Cache results
            for match in top_matches:
                self.matching_scores.append(match)
            
            # Store in Redis
            if self.redis_client:
                await self._cache_matching_results(creator_id, top_matches)
            
            return top_matches
            
        except Exception as e:
            self.logger.error(f"Error finding collaboration matches: {e}")
            return []
    
    async def _calculate_matching_score(
        self,
        creator_a: CreatorProfile,
        creator_b: CreatorProfile,
        collaboration_type: Optional[CollaborationType] = None
    ) -> MatchingScore:
        """Calculate comprehensive matching score between two creators"""
        try:
            # Calculate individual criteria scores
            criteria_scores = {}
            
            # Audience overlap score
            criteria_scores["audience_overlap"] = await self._calculate_audience_overlap(creator_a, creator_b)
            
            # Content similarity score
            criteria_scores["content_similarity"] = await self._calculate_content_similarity(creator_a, creator_b)
            
            # Engagement compatibility score
            criteria_scores["engagement_compatibility"] = await self._calculate_engagement_compatibility(creator_a, creator_b)
            
            # Brand alignment score
            criteria_scores["brand_alignment"] = await self._calculate_brand_alignment(creator_a, creator_b)
            
            # Communication and reliability scores
            criteria_scores["communication"] = (creator_a.communication_score + creator_b.communication_score) / 2
            criteria_scores["reliability"] = (creator_a.reliability_score + creator_b.reliability_score) / 2
            criteria_scores["availability"] = (creator_a.availability_score + creator_b.availability_score) / 2
            
            # Calculate weighted overall score
            overall_score = sum(
                criteria_scores.get(factor, 0) * weight
                for factor, weight in self.success_weights.items()
            )
            
            # Predict success probability
            success_probability = await self._predict_collaboration_success(creator_a, creator_b, collaboration_type)
            
            # Estimate potential metrics
            potential_reach = creator_a.follower_count + creator_b.follower_count
            engagement_boost = (creator_a.engagement_rate + creator_b.engagement_rate) / 2 * 1.2  # Collaboration boost
            revenue_potential = await self._estimate_revenue_potential(creator_a, creator_b, collaboration_type)
            
            # Recommend collaboration types
            recommended_types = await self._recommend_collaboration_types(creator_a, creator_b)
            
            # Compatibility factors
            compatibility_factors = {
                "timezone_compatible": abs(self._parse_timezone_offset(creator_a.timezone) - 
                                         self._parse_timezone_offset(creator_b.timezone)) <= 6,
                "language_overlap": bool(set(creator_a.languages) & set(creator_b.languages)),
                "content_category_overlap": bool(set(creator_a.content_categories) & set(creator_b.content_categories)),
                "follower_ratio": min(creator_a.follower_count, creator_b.follower_count) / max(creator_a.follower_count, creator_b.follower_count)
            }
            
            return MatchingScore(
                creator_a=creator_a.creator_id,
                creator_b=creator_b.creator_id,
                overall_score=overall_score,
                criteria_scores=criteria_scores,
                compatibility_factors=compatibility_factors,
                success_probability=success_probability,
                recommended_collaboration_types=recommended_types,
                potential_audience_reach=potential_reach,
                estimated_engagement_boost=engagement_boost,
                revenue_potential=revenue_potential,
                calculated_at=datetime.now()
            )
            
        except Exception as e:
            self.logger.error(f"Error calculating matching score: {e}")
            return MatchingScore(
                creator_a=creator_a.creator_id,
                creator_b=creator_b.creator_id,
                overall_score=0.0,
                criteria_scores={},
                compatibility_factors={},
                success_probability=0.0,
                recommended_collaboration_types=[],
                potential_audience_reach=0,
                estimated_engagement_boost=0.0,
                revenue_potential=0.0,
                calculated_at=datetime.now()
            )
    
    async def _calculate_audience_overlap(self, creator_a: CreatorProfile, creator_b: CreatorProfile) -> float:
        """Calculate audience overlap score between creators"""
        # This would analyze actual audience demographics
        # For simulation, use demographic similarity
        
        demo_a = creator_a.target_demographics
        demo_b = creator_b.target_demographics
        
        overlap_score = 0.0
        
        # Age group overlap
        if "age_groups" in demo_a and "age_groups" in demo_b:
            overlap_age = len(set(demo_a["age_groups"]) & set(demo_b["age_groups"]))
            total_age = len(set(demo_a["age_groups"]) | set(demo_b["age_groups"]))
            overlap_score += (overlap_age / total_age) * 0.4 if total_age > 0 else 0
        
        # Gender overlap
        if "genders" in demo_a and "genders" in demo_b:
            overlap_gender = len(set(demo_a["genders"]) & set(demo_b["genders"]))
            total_gender = len(set(demo_a["genders"]) | set(demo_b["genders"]))
            overlap_score += (overlap_gender / total_gender) * 0.3 if total_gender > 0 else 0
        
        # Geographic overlap
        if "locations" in demo_a and "locations" in demo_b:
            overlap_loc = len(set(demo_a["locations"]) & set(demo_b["locations"]))
            total_loc = len(set(demo_a["locations"]) | set(demo_b["locations"]))
            overlap_score += (overlap_loc / total_loc) * 0.3 if total_loc > 0 else 0
        
        return min(1.0, overlap_score)
    
    async def _calculate_content_similarity(self, creator_a: CreatorProfile, creator_b: CreatorProfile) -> float:
        """Calculate content similarity score between creators"""
        # Content category overlap
        categories_a = set(creator_a.content_categories)
        categories_b = set(creator_b.content_categories)
        
        if not categories_a or not categories_b:
            return 0.0
        
        overlap = len(categories_a & categories_b)
        union = len(categories_a | categories_b)
        
        similarity = overlap / union if union > 0 else 0.0
        
        # Adjust for creator type compatibility
        type_compatibility = 1.0
        if creator_a.creator_type == creator_b.creator_type:
            type_compatibility = 0.9  # Same type might be less complementary
        elif (creator_a.creator_type, creator_b.creator_type) in [
            ("musician", "podcaster"), ("blogger", "video_creator"), 
            ("photographer", "influencer"), ("comedian", "video_creator")
        ]:
            type_compatibility = 1.2  # Highly complementary types
        
        return min(1.0, similarity * type_compatibility)
    
    async def _calculate_engagement_compatibility(self, creator_a: CreatorProfile, creator_b: CreatorProfile) -> float:
        """Calculate engagement compatibility score"""
        # Engagement rate similarity (closer rates often work better)
        rate_a = creator_a.engagement_rate
        rate_b = creator_b.engagement_rate
        
        rate_similarity = 1 - abs(rate_a - rate_b) / max(rate_a, rate_b) if max(rate_a, rate_b) > 0 else 0
        
        # Follower count compatibility (balanced vs. very imbalanced)
        followers_a = creator_a.follower_count
        followers_b = creator_b.follower_count
        
        follower_ratio = min(followers_a, followers_b) / max(followers_a, followers_b) if max(followers_a, followers_b) > 0 else 0
        
        # Combined score
        compatibility = (rate_similarity * 0.6) + (follower_ratio * 0.4)
        
        return compatibility
    
    async def _calculate_brand_alignment(self, creator_a: CreatorProfile, creator_b: CreatorProfile) -> float:
        """Calculate brand alignment score"""
        # Brand safety compatibility
        safety_score = (creator_a.brand_safety_score + creator_b.brand_safety_score) / 2
        
        # Content category alignment for brand purposes
        categories_a = set(creator_a.content_categories)
        categories_b = set(creator_b.content_categories)
        
        # Certain category combinations work well for brands
        brand_friendly_combinations = [
            ("lifestyle", "fashion"), ("tech", "gaming"), ("fitness", "nutrition"),
            ("travel", "photography"), ("music", "entertainment")
        ]
        
        alignment_bonus = 0.0
        for cat_a in categories_a:
            for cat_b in categories_b:
                if (cat_a, cat_b) in brand_friendly_combinations or (cat_b, cat_a) in brand_friendly_combinations:
                    alignment_bonus = 0.2
                    break
        
        return min(1.0, safety_score + alignment_bonus)
    
    async def _predict_collaboration_success(
        self,
        creator_a: CreatorProfile,
        creator_b: CreatorProfile,
        collaboration_type: Optional[CollaborationType] = None
    ) -> float:
        """Predict collaboration success probability using ML"""
        try:
            # In a real implementation, this would use trained ML models
            # For simulation, use heuristic-based prediction
            
            success_factors = []
            
            # Historical success rates
            success_factors.append(creator_a.success_rate)
            success_factors.append(creator_b.success_rate)
            
            # Reliability and communication scores
            success_factors.append(creator_a.reliability_score)
            success_factors.append(creator_b.reliability_score)
            success_factors.append(creator_a.communication_score)
            success_factors.append(creator_b.communication_score)
            
            # Availability scores
            success_factors.append(creator_a.availability_score)
            success_factors.append(creator_b.availability_score)
            
            # Calculate weighted average
            base_probability = statistics.mean(success_factors)
            
            # Adjust based on collaboration type
            type_adjustments = {
                CollaborationType.MUSIC_COLLABORATION: 0.85,  # More complex
                CollaborationType.VIDEO_COLLABORATION: 0.9,
                CollaborationType.CONTENT_CROSSOVER: 0.95,    # Easier
                CollaborationType.JOINT_CAMPAIGN: 0.88,
                CollaborationType.GUEST_APPEARANCE: 0.98,     # Simplest
                CollaborationType.LIVE_STREAM_COLLAB: 0.92
            }
            
            type_adjustment = type_adjustments.get(collaboration_type, 0.9) if collaboration_type else 0.9
            
            return min(1.0, base_probability * type_adjustment)
            
        except Exception as e:
            self.logger.error(f"Error predicting collaboration success: {e}")
            return 0.5  # Default moderate probability
    
    async def _recommend_collaboration_types(
        self,
        creator_a: CreatorProfile,
        creator_b: CreatorProfile
    ) -> List[CollaborationType]:
        """Recommend best collaboration types for creator pair"""
        recommendations = []
        
        # Analyze creator types and content categories
        type_a = creator_a.creator_type
        type_b = creator_b.creator_type
        categories_a = set(creator_a.content_categories)
        categories_b = set(creator_b.content_categories)
        
        # Type-based recommendations
        type_combinations = {
            ("musician", "musician"): [CollaborationType.MUSIC_COLLABORATION, CollaborationType.REMIX_COLLABORATION],
            ("musician", "podcaster"): [CollaborationType.PODCAST_GUEST, CollaborationType.CONTENT_CROSSOVER],
            ("blogger", "video_creator"): [CollaborationType.VIDEO_COLLABORATION, CollaborationType.CONTENT_CROSSOVER],
            ("photographer", "influencer"): [CollaborationType.JOINT_CAMPAIGN, CollaborationType.CONTENT_CROSSOVER],
            ("comedian", "video_creator"): [CollaborationType.VIDEO_COLLABORATION, CollaborationType.GUEST_APPEARANCE]
        }
        
        key = (type_a, type_b) if (type_a, type_b) in type_combinations else (type_b, type_a)
        if key in type_combinations:
            recommendations.extend(type_combinations[key])
        
        # Category-based recommendations
        if "gaming" in categories_a and "gaming" in categories_b:
            recommendations.append(CollaborationType.LIVE_STREAM_COLLAB)
        
        if "fitness" in categories_a or "fitness" in categories_b:
            recommendations.append(CollaborationType.CHALLENGE_PARTICIPATION)
        
        # Default recommendations if none found
        if not recommendations:
            recommendations = [CollaborationType.CONTENT_CROSSOVER, CollaborationType.GUEST_APPEARANCE]
        
        return list(set(recommendations))  # Remove duplicates
    
    async def _estimate_revenue_potential(
        self,
        creator_a: CreatorProfile,
        creator_b: CreatorProfile,
        collaboration_type: Optional[CollaborationType] = None
    ) -> float:
        """Estimate revenue potential for collaboration"""
        # Base revenue calculation from combined audience
        base_revenue_a = creator_a.follower_count * creator_a.engagement_rate * 0.01  # €0.01 per engaged follower
        base_revenue_b = creator_b.follower_count * creator_b.engagement_rate * 0.01
        
        combined_base = base_revenue_a + base_revenue_b
        
        # Collaboration multipliers
        collaboration_multipliers = {
            CollaborationType.BRAND_PARTNERSHIP: 2.5,
            CollaborationType.JOINT_CAMPAIGN: 2.0,
            CollaborationType.MUSIC_COLLABORATION: 1.8,
            CollaborationType.VIDEO_COLLABORATION: 1.6,
            CollaborationType.LIVE_STREAM_COLLAB: 1.4,
            CollaborationType.CONTENT_CROSSOVER: 1.3,
            CollaborationType.GUEST_APPEARANCE: 1.2
        }
        
        multiplier = collaboration_multipliers.get(collaboration_type, 1.3) if collaboration_type else 1.3
        
        # Audience overlap penalty (some audience might be shared)
        overlap_penalty = 0.9  # Assume 10% overlap reduction
        
        return combined_base * multiplier * overlap_penalty
    
    def _parse_timezone_offset(self, timezone: str) -> int:
        """Parse timezone to get UTC offset in hours"""
        timezone_offsets = {
            "UTC": 0, "EST": -5, "PST": -8, "CET": 1, "JST": 9,
            "GMT": 0, "PDT": -7, "EDT": -4, "CST": -6, "MST": -7
        }
        return timezone_offsets.get(timezone, 0)
    
    async def update_collaboration_status(
        self,
        project_id: str,
        status: CollaborationStatus,
        actual_metrics: Dict[str, float] = None,
        feedback_scores: Dict[str, float] = None
    ) -> bool:
        """Update collaboration project status and metrics"""
        try:
            # Find the project
            project = None
            for proj in self.collaboration_projects:
                if proj.project_id == project_id:
                    project = proj
                    break
            
            if not project:
                self.logger.warning(f"Collaboration project not found: {project_id}")
                return False
            
            # Update status and timestamps
            project.status = status
            
            if status == CollaborationStatus.IN_PROGRESS and not project.start_date:
                project.start_date = datetime.now()
            elif status in [CollaborationStatus.COMPLETED, CollaborationStatus.FAILED, CollaborationStatus.CANCELLED]:
                project.completion_date = datetime.now()
            
            # Update metrics
            if actual_metrics:
                project.actual_metrics.update(actual_metrics)
            
            if feedback_scores:
                project.feedback_scores.update(feedback_scores)
            
            # Calculate success score for completed projects
            if status == CollaborationStatus.COMPLETED:
                project.success_score = await self._calculate_project_success_score(project)
            
            # Cache updated project
            if self.redis_client:
                await self._cache_collaboration_project(project)
            
            self.logger.info(f"Collaboration status updated: {project_id} -> {status.value}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating collaboration status: {e}")
            return False
    
    async def _calculate_project_success_score(self, project: CollaborationProject) -> float:
        """Calculate success score for completed collaboration project"""
        try:
            success_score = 0.0
            
            # Compare actual vs target metrics
            if project.target_metrics and project.actual_metrics:
                metric_scores = []
                for metric, target in project.target_metrics.items():
                    actual = project.actual_metrics.get(metric, 0)
                    if target > 0:
                        achievement_ratio = actual / target
                        metric_scores.append(min(1.0, achievement_ratio))
                
                if metric_scores:
                    success_score += statistics.mean(metric_scores) * 0.6
            
            # Feedback scores
            if project.feedback_scores:
                feedback_avg = statistics.mean(project.feedback_scores.values())
                success_score += (feedback_avg / 5.0) * 0.3  # Assuming 5-point scale
            
            # Completion within reasonable time
            if project.start_date and project.completion_date:
                duration_days = (project.completion_date - project.start_date).days
                if duration_days <= 30:  # Completed within 30 days
                    success_score += 0.1
            
            return min(1.0, success_score)
            
        except Exception as e:
            self.logger.error(f"Error calculating project success score: {e}")
            return 0.5
    
    async def analyze_collaboration_performance(
        self,
        time_range: Tuple[datetime, datetime],
        creator_id: Optional[str] = None
    ) -> CollaborationAnalytics:
        """Analyze collaboration performance metrics"""
        try:
            start_time, end_time = time_range
            
            # Filter projects by time range and creator
            filtered_projects = [
                proj for proj in self.collaboration_projects
                if start_time <= proj.proposed_date <= end_time
                and (not creator_id or creator_id in [proj.primary_creator] + proj.secondary_creators)
            ]
            
            if not filtered_projects:
                return CollaborationAnalytics(time_period=time_range)
            
            # Basic metrics
            total_collaborations = len(filtered_projects)
            successful_collaborations = len([p for p in filtered_projects if p.status == CollaborationStatus.COMPLETED and (p.success_score or 0) >= 0.7])
            failed_collaborations = len([p for p in filtered_projects if p.status in [CollaborationStatus.FAILED, CollaborationStatus.CANCELLED]])
            
            average_success_rate = successful_collaborations / total_collaborations if total_collaborations > 0 else 0.0
            
            # Duration analysis
            completed_projects = [p for p in filtered_projects if p.start_date and p.completion_date]
            durations = [(p.completion_date - p.start_date).days for p in completed_projects]
            average_duration = statistics.mean(durations) if durations else 0.0
            
            # Revenue analysis
            total_revenue = sum(
                sum(p.actual_metrics.get("revenue", 0) for p in filtered_projects if isinstance(p.actual_metrics.get("revenue", 0), (int, float)))
            )
            avg_revenue = total_revenue / total_collaborations if total_collaborations > 0 else 0.0
            
            # Collaboration type breakdown
            type_breakdown = {}
            for project in filtered_projects:
                ctype = project.collaboration_type.value
                type_breakdown[ctype] = type_breakdown.get(ctype, 0) + 1
            
            # Most active creators
            creator_activity = defaultdict(int)
            for project in filtered_projects:
                creator_activity[project.primary_creator] += 1
                for secondary in project.secondary_creators:
                    creator_activity[secondary] += 1
            
            most_active = [
                {"creator_id": creator, "collaborations": count}
                for creator, count in sorted(creator_activity.items(), key=lambda x: x[1], reverse=True)[:10]
            ]
            
            # Success factors analysis
            success_factors = await self._analyze_success_factors(filtered_projects)
            
            # Platform and geographic distribution (would come from project metadata)
            platform_dist = {"youtube": 40, "instagram": 25, "tiktok": 20, "other": 15}  # Simulated
            geographic_dist = {"US": 35, "EU": 30, "Asia": 20, "Other": 15}  # Simulated
            
            # Trends analysis
            trends = await self._analyze_collaboration_trends(filtered_projects)
            
            return CollaborationAnalytics(
                time_period=time_range,
                total_collaborations=total_collaborations,
                successful_collaborations=successful_collaborations,
                failed_collaborations=failed_collaborations,
                average_success_rate=average_success_rate,
                average_project_duration=average_duration,
                total_revenue_generated=total_revenue,
                average_revenue_per_collaboration=avg_revenue,
                top_collaboration_types=type_breakdown,
                most_active_creators=most_active,
                success_factors=success_factors,
                platform_distribution=platform_dist,
                geographic_distribution=geographic_dist,
                collaboration_trends=trends
            )
            
        except Exception as e:
            self.logger.error(f"Error analyzing collaboration performance: {e}")
            return CollaborationAnalytics(time_period=time_range)
    
    async def _analyze_success_factors(self, projects: List[CollaborationProject]) -> Dict[str, float]:
        """Analyze factors that contribute to collaboration success"""
        success_factors = {}
        
        successful_projects = [p for p in projects if p.status == CollaborationStatus.COMPLETED and (p.success_score or 0) >= 0.7]
        
        if not successful_projects:
            return success_factors
        
        # Communication quality impact
        communication_scores = []
        for project in successful_projects:
            if "communication_quality" in project.feedback_scores:
                communication_scores.append(project.feedback_scores["communication_quality"])
        
        if communication_scores:
            success_factors["communication_quality"] = statistics.mean(communication_scores) / 5.0
        
        # Project duration impact
        durations = []
        for project in successful_projects:
            if project.start_date and project.completion_date:
                duration = (project.completion_date - project.start_date).days
                durations.append(duration)
        
        if durations:
            avg_duration = statistics.mean(durations)
            success_factors["optimal_duration"] = max(0, 1 - (avg_duration - 14) / 30)  # 14 days optimal
        
        # Collaboration type success rates
        type_success_rates = {}
        for ctype in CollaborationType:
            type_projects = [p for p in projects if p.collaboration_type == ctype]
            type_successful = [p for p in type_projects if p.status == CollaborationStatus.COMPLETED and (p.success_score or 0) >= 0.7]
            
            if type_projects:
                type_success_rates[ctype.value] = len(type_successful) / len(type_projects)
        
        success_factors.update(type_success_rates)
        
        return success_factors
    
    async def _analyze_collaboration_trends(self, projects: List[CollaborationProject]) -> Dict[str, Any]:
        """Analyze collaboration trends over time"""
        trends = {}
        
        # Monthly collaboration counts
        monthly_counts = defaultdict(int)
        for project in projects:
            month_key = project.proposed_date.strftime("%Y-%m")
            monthly_counts[month_key] += 1
        
        trends["monthly_activity"] = dict(monthly_counts)
        
        # Success rate trends
        monthly_success = defaultdict(list)
        for project in projects:
            if project.success_score is not None:
                month_key = project.proposed_date.strftime("%Y-%m")
                monthly_success[month_key].append(project.success_score)
        
        success_trends = {}
        for month, scores in monthly_success.items():
            success_trends[month] = statistics.mean(scores) if scores else 0
        
        trends["success_rate_trends"] = success_trends
        
        # Popular collaboration types over time
        type_trends = defaultdict(lambda: defaultdict(int))
        for project in projects:
            month_key = project.proposed_date.strftime("%Y-%m")
            type_trends[month_key][project.collaboration_type.value] += 1
        
        trends["type_popularity_trends"] = {month: dict(types) for month, types in type_trends.items()}
        
        return trends
    
    async def generate_collaboration_recommendations(
        self,
        creator_id: str
    ) -> Dict[str, Any]:
        """Generate personalized collaboration recommendations for a creator"""
        try:
            if creator_id not in self.creator_profiles:
                return {"error": "Creator profile not found"}
            
            creator = self.creator_profiles[creator_id]
            
            # Find potential matches
            matches = await self.find_collaboration_matches(creator_id, max_matches=5)
            
            # Analyze creator's collaboration history
            history_analysis = await self._analyze_creator_collaboration_history(creator_id)
            
            # Generate strategy recommendations
            strategy_recommendations = await self._generate_collaboration_strategy(creator, history_analysis)
            
            # Suggest optimal timing
            timing_suggestions = await self._suggest_collaboration_timing(creator_id)
            
            return {
                "creator_id": creator_id,
                "top_matches": [
                    {
                        "partner_id": match.creator_b,
                        "overall_score": round(match.overall_score, 3),
                        "success_probability": round(match.success_probability, 3),
                        "recommended_types": [t.value for t in match.recommended_collaboration_types],
                        "revenue_potential": round(match.revenue_potential, 2),
                        "audience_reach": match.potential_audience_reach
                    }
                    for match in matches
                ],
                "collaboration_history": history_analysis,
                "strategy_recommendations": strategy_recommendations,
                "timing_suggestions": timing_suggestions,
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error generating collaboration recommendations: {e}")
            return {"error": str(e)}
    
    async def _get_collaboration_history(self, creator_id: str) -> List[str]:
        """Get collaboration history for a creator"""
        return [
            proj.project_id for proj in self.collaboration_projects
            if creator_id in [proj.primary_creator] + proj.secondary_creators
        ]
    
    async def _calculate_creator_success_rate(self, creator_id: str) -> float:
        """Calculate collaboration success rate for a creator"""
        creator_projects = [
            proj for proj in self.collaboration_projects
            if creator_id in [proj.primary_creator] + proj.secondary_creators
            and proj.status in [CollaborationStatus.COMPLETED, CollaborationStatus.FAILED]
        ]
        
        if not creator_projects:
            return 0.8  # Default for new creators
        
        successful = len([p for p in creator_projects if p.success_score and p.success_score >= 0.7])
        return successful / len(creator_projects)
    
    async def _analyze_creator_collaboration_history(self, creator_id: str) -> Dict[str, Any]:
        """Analyze a creator's collaboration history"""
        history = await self._get_collaboration_history(creator_id)
        creator_projects = [
            proj for proj in self.collaboration_projects
            if proj.project_id in history
        ]
        
        if not creator_projects:
            return {"total_collaborations": 0, "success_rate": 0, "preferred_types": []}
        
        # Calculate metrics
        total = len(creator_projects)
        successful = len([p for p in creator_projects if p.success_score and p.success_score >= 0.7])
        success_rate = successful / total if total > 0 else 0
        
        # Find preferred collaboration types
        type_counts = defaultdict(int)
        for project in creator_projects:
            type_counts[project.collaboration_type.value] += 1
        
        preferred_types = sorted(type_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        
        return {
            "total_collaborations": total,
            "success_rate": round(success_rate, 3),
            "preferred_types": [{"type": t, "count": c} for t, c in preferred_types],
            "average_revenue": round(statistics.mean([
                p.actual_metrics.get("revenue", 0) 
                for p in creator_projects 
                if p.actual_metrics.get("revenue", 0) > 0
            ]), 2) if any(p.actual_metrics.get("revenue", 0) > 0 for p in creator_projects) else 0
        }
    
    async def _generate_collaboration_strategy(
        self,
        creator: CreatorProfile,
        history: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate strategic collaboration recommendations"""
        recommendations = []
        
        # Based on success rate
        if history["success_rate"] < 0.7:
            recommendations.append({
                "category": "success_improvement",
                "priority": "high",
                "title": "Focus on Communication and Planning",
                "description": "Your collaboration success rate can be improved through better planning and communication",
                "actions": [
                    "Set clear expectations before starting",
                    "Use project management tools",
                    "Schedule regular check-ins",
                    "Define success metrics upfront"
                ]
            })
        
        # Based on collaboration count
        if history["total_collaborations"] < 5:
            recommendations.append({
                "category": "experience_building",
                "priority": "medium",
                "title": "Build Collaboration Experience",
                "description": "Start with simpler collaboration types to build experience",
                "actions": [
                    "Begin with guest appearances",
                    "Try content crossovers",
                    "Participate in challenges",
                    "Focus on single-session collaborations"
                ]
            })
        
        # Based on follower count
        if creator.follower_count < 10000:
            recommendations.append({
                "category": "growth_strategy",
                "priority": "high",
                "title": "Collaborate with Larger Creators",
                "description": "Partner with creators who have 2-5x your follower count for growth",
                "actions": [
                    "Offer unique value proposition",
                    "Focus on niche expertise",
                    "Create high-quality content samples",
                    "Be flexible with collaboration terms"
                ]
            })
        
        return recommendations
    
    async def _suggest_collaboration_timing(self, creator_id: str) -> Dict[str, Any]:
        """Suggest optimal timing for collaborations"""
        # This would analyze creator's activity patterns, audience engagement times, etc.
        # For simulation, provide general recommendations
        
        return {
            "best_months": ["March", "September", "November"],
            "avoid_months": ["December", "January"],
            "optimal_project_duration": "2-3 weeks",
            "best_day_to_launch": "Tuesday or Wednesday",
            "preparation_time_needed": "1-2 weeks",
            "reasoning": {
                "best_months": "Higher audience engagement and less competition",
                "avoid_months": "Holiday season distractions",
                "optimal_duration": "Allows quality development without losing momentum",
                "best_launch_day": "Mid-week launches typically see better engagement"
            }
        }
    
    # Redis caching methods
    async def _cache_creator_profile(self, profile: CreatorProfile):
        """Cache creator profile in Redis"""
        if self.redis_client:
            try:
                key = f"creator_profile:{profile.creator_id}"
                data = {
                    "creator_type": profile.creator_type,
                    "follower_count": profile.follower_count,
                    "engagement_rate": profile.engagement_rate,
                    "success_rate": profile.success_rate,
                    "updated_at": datetime.now().isoformat()
                }
                self.redis_client.hset(key, mapping=data)
                self.redis_client.expire(key, 86400)  # 24 hour expiry
            except Exception as e:
                self.logger.error(f"Redis cache error: {e}")
    
    async def _cache_collaboration_project(self, project: CollaborationProject):
        """Cache collaboration project in Redis"""
        if self.redis_client:
            try:
                key = f"collaboration:{project.project_id}"
                data = {
                    "type": project.collaboration_type.value,
                    "status": project.status.value,
                    "primary_creator": project.primary_creator,
                    "secondary_creators": ",".join(project.secondary_creators),
                    "success_score": project.success_score or 0,
                    "updated_at": datetime.now().isoformat()
                }
                self.redis_client.hset(key, mapping=data)
                self.redis_client.expire(key, 604800)  # 7 day expiry
            except Exception as e:
                self.logger.error(f"Redis cache error: {e}")
    
    async def _cache_matching_results(self, creator_id: str, matches: List[MatchingScore]):
        """Cache matching results in Redis"""
        if self.redis_client:
            try:
                key = f"matches:{creator_id}"
                match_data = [
                    {
                        "partner": match.creator_b,
                        "score": match.overall_score,
                        "success_prob": match.success_probability
                    }
                    for match in matches[:5]  # Top 5 matches
                ]
                self.redis_client.set(key, json.dumps(match_data))
                self.redis_client.expire(key, 3600)  # 1 hour expiry
            except Exception as e:
                self.logger.error(f"Redis cache error: {e}")
    
    def get_collaboration_summary(self) -> Dict[str, Any]:
        """Get summary of collaboration system performance"""
        try:
            total_creators = len(self.creator_profiles)
            total_projects = len(self.collaboration_projects)
            completed_projects = len([p for p in self.collaboration_projects if p.status == CollaborationStatus.COMPLETED])
            
            avg_success_score = 0.0
            if completed_projects > 0:
                success_scores = [p.success_score for p in self.collaboration_projects if p.success_score]
                avg_success_score = statistics.mean(success_scores) if success_scores else 0.0
            
            return {
                "system_stats": {
                    "total_creators": total_creators,
                    "total_projects": total_projects,
                    "completed_projects": completed_projects,
                    "average_success_score": round(avg_success_score, 3)
                },
                "recent_activity": {
                    "matches_calculated": len(self.matching_scores),
                    "active_projects": len([p for p in self.collaboration_projects if p.status == CollaborationStatus.IN_PROGRESS])
                },
                "performance_metrics": {
                    "matching_engine_ready": self._ml_models_initialized,
                    "redis_connected": self.redis_client is not None
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error getting collaboration summary: {e}")
            return {"error": str(e)}