"""
Creator Reputation Service - Enterprise Microservice
==================================================

Advanced reputation management system for creators with dynamic scoring,
behavioral analysis, and community-driven reputation mechanisms.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

⚠️ STRICT COPYRIGHT WARNING ⚠️
This code is proprietary and confidential. Unauthorized use, reproduction,
distribution, or modification is strictly prohibited and will be prosecuted
to the full extent of the law.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from pydantic import BaseModel, Field
import json
import math
from collections import defaultdict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ReputationMetricType(str, Enum):
    """Types of reputation metrics."""
    CONTENT_QUALITY = "content_quality"
    ENGAGEMENT_RATE = "engagement_rate"
    COLLABORATION_SUCCESS = "collaboration_success"
    COMMUNITY_CONTRIBUTION = "community_contribution"
    RELIABILITY = "reliability"
    INNOVATION = "innovation"
    MENTORSHIP = "mentorship"
    PLATFORM_COMPLIANCE = "platform_compliance"
    AUDIENCE_GROWTH = "audience_growth"
    REVENUE_PERFORMANCE = "revenue_performance"


class ReputationEventType(str, Enum):
    """Types of reputation events."""
    CONTENT_PUBLISHED = "content_published"
    CONTENT_LIKED = "content_liked"
    CONTENT_SHARED = "content_shared"
    COLLABORATION_COMPLETED = "collaboration_completed"
    COLLABORATION_CANCELLED = "collaboration_cancelled"
    COMMUNITY_HELP = "community_help"
    GUIDELINE_VIOLATION = "guideline_violation"
    POSITIVE_REVIEW = "positive_review"
    NEGATIVE_REVIEW = "negative_review"
    MILESTONE_ACHIEVED = "milestone_achieved"
    MENTOR_SESSION = "mentor_session"
    INNOVATIVE_CONTENT = "innovative_content"
    CONSISTENT_ACTIVITY = "consistent_activity"


class ReputationLevel(str, Enum):
    """Creator reputation levels."""
    NEWCOMER = "newcomer"          # 0-199 points
    RISING_STAR = "rising_star"    # 200-499 points
    ESTABLISHED = "established"     # 500-999 points
    EXPERT = "expert"              # 1000-1999 points
    MASTER = "master"              # 2000-4999 points
    LEGEND = "legend"              # 5000+ points


class TrustLevel(str, Enum):
    """Trust levels for collaboration."""
    UNVERIFIED = "unverified"
    BASIC = "basic"
    TRUSTED = "trusted"
    VERIFIED = "verified"
    ELITE = "elite"


@dataclass
class ReputationMetric:
    """Individual reputation metric."""
    type: ReputationMetricType
    value: float
    weight: float
    last_updated: datetime
    trend: str  # "increasing", "stable", "decreasing"
    historical_values: List[Tuple[datetime, float]] = field(default_factory=list)


@dataclass
class ReputationEvent:
    """Reputation affecting event."""
    id: str
    creator_id: str
    event_type: ReputationEventType
    impact_score: float
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)
    processed: bool = False


class CreatorReputationProfile(BaseModel):
    """Complete creator reputation profile."""
    creator_id: str = Field(..., description="Creator identifier")
    overall_score: float = Field(default=0.0, description="Overall reputation score")
    reputation_level: ReputationLevel = Field(default=ReputationLevel.NEWCOMER)
    trust_level: TrustLevel = Field(default=TrustLevel.UNVERIFIED)
    metrics: Dict[ReputationMetricType, float] = Field(default_factory=dict)
    badges: List[str] = Field(default_factory=list, description="Earned badges")
    certifications: List[str] = Field(default_factory=list, description="Verified certifications")
    warnings: List[str] = Field(default_factory=list, description="Active warnings")
    created_at: datetime = Field(default_factory=datetime.now)
    last_updated: datetime = Field(default_factory=datetime.now)


class ReputationAnalytics(BaseModel):
    """Reputation analytics and insights."""
    creator_id: str
    period_days: int
    score_change: float
    rank_change: int
    metric_improvements: List[str]
    metric_declines: List[str]
    growth_rate: float
    percentile_rank: float
    comparable_creators: List[str]
    recommendations: List[str]


class CreatorReputationService:
    """
    Enterprise Creator Reputation Service
    
    Manages dynamic reputation scoring, behavioral analysis, and trust levels
    for creators with sophisticated metrics and community-driven validation.
    """
    
    def __init__(self):
        self.reputation_profiles: Dict[str, CreatorReputationProfile] = {}
        self.reputation_metrics: Dict[str, Dict[ReputationMetricType, ReputationMetric]] = {}
        self.reputation_events: List[ReputationEvent] = []
        self.event_queue: List[ReputationEvent] = []
        self.metric_weights: Dict[ReputationMetricType, float] = {}
        self.level_thresholds: Dict[ReputationLevel, Tuple[float, float]] = {}
        self.badges_catalog: Dict[str, Dict[str, Any]] = {}
        
        # Initialize system
        self._initialize_metric_weights()
        self._initialize_level_thresholds()
        self._initialize_badges_catalog()
        
        logger.info("CreatorReputationService initialized successfully")
    
    def _initialize_metric_weights(self):
        """Initialize metric weights for reputation calculation."""
        self.metric_weights = {
            ReputationMetricType.CONTENT_QUALITY: 0.20,
            ReputationMetricType.ENGAGEMENT_RATE: 0.15,
            ReputationMetricType.COLLABORATION_SUCCESS: 0.15,
            ReputationMetricType.COMMUNITY_CONTRIBUTION: 0.10,
            ReputationMetricType.RELIABILITY: 0.10,
            ReputationMetricType.INNOVATION: 0.08,
            ReputationMetricType.MENTORSHIP: 0.07,
            ReputationMetricType.PLATFORM_COMPLIANCE: 0.05,
            ReputationMetricType.AUDIENCE_GROWTH: 0.05,
            ReputationMetricType.REVENUE_PERFORMANCE: 0.05
        }
    
    def _initialize_level_thresholds(self):
        """Initialize reputation level thresholds."""
        self.level_thresholds = {
            ReputationLevel.NEWCOMER: (0, 199),
            ReputationLevel.RISING_STAR: (200, 499),
            ReputationLevel.ESTABLISHED: (500, 999),
            ReputationLevel.EXPERT: (1000, 1999),
            ReputationLevel.MASTER: (2000, 4999),
            ReputationLevel.LEGEND: (5000, float('inf'))
        }
    
    def _initialize_badges_catalog(self):
        """Initialize available badges and their criteria."""
        self.badges_catalog = {
            "quality_creator": {
                "name": "Quality Creator",
                "description": "Consistently creates high-quality content",
                "criteria": {"content_quality": 85, "min_content": 10},
                "icon": "⭐",
                "rarity": "common"
            },
            "collaboration_master": {
                "name": "Collaboration Master",
                "description": "Excellent collaboration success rate",
                "criteria": {"collaboration_success": 90, "min_collaborations": 5},
                "icon": "🤝",
                "rarity": "rare"
            },
            "community_champion": {
                "name": "Community Champion",
                "description": "Outstanding community contributions",
                "criteria": {"community_contribution": 95, "min_activities": 20},
                "icon": "🏆",
                "rarity": "epic"
            },
            "innovator": {
                "name": "Innovator",
                "description": "Consistently creates innovative content",
                "criteria": {"innovation": 90, "min_innovations": 5},
                "icon": "💡",
                "rarity": "rare"
            },
            "mentor": {
                "name": "Mentor",
                "description": "Actively mentors other creators",
                "criteria": {"mentorship": 85, "min_mentees": 3},
                "icon": "🎓",
                "rarity": "uncommon"
            },
            "reliable_partner": {
                "name": "Reliable Partner",
                "description": "Highly reliable in collaborations",
                "criteria": {"reliability": 95, "min_projects": 10},
                "icon": "✅",
                "rarity": "uncommon"
            },
            "growth_hacker": {
                "name": "Growth Hacker",
                "description": "Exceptional audience growth",
                "criteria": {"audience_growth": 90, "min_followers": 1000},
                "icon": "📈",
                "rarity": "rare"
            },
            "revenue_optimizer": {
                "name": "Revenue Optimizer",
                "description": "Outstanding revenue performance",
                "criteria": {"revenue_performance": 90, "min_revenue": 1000},
                "icon": "💰",
                "rarity": "epic"
            }
        }
    
    async def create_reputation_profile(self, creator_id: str) -> CreatorReputationProfile:
        """Create new reputation profile for creator."""
        try:
            if creator_id in self.reputation_profiles:
                return self.reputation_profiles[creator_id]
            
            profile = CreatorReputationProfile(creator_id=creator_id)
            self.reputation_profiles[creator_id] = profile
            
            # Initialize metrics
            self.reputation_metrics[creator_id] = {}
            for metric_type in ReputationMetricType:
                self.reputation_metrics[creator_id][metric_type] = ReputationMetric(
                    type=metric_type,
                    value=0.0,
                    weight=self.metric_weights[metric_type],
                    last_updated=datetime.now(),
                    trend="stable"
                )
            
            logger.info(f"Created reputation profile for creator {creator_id}")
            return profile
            
        except Exception as e:
            logger.error(f"Error creating reputation profile: {e}")
            raise
    
    async def record_reputation_event(
        self, 
        creator_id: str, 
        event_type: ReputationEventType, 
        impact_score: float,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Record reputation affecting event."""
        try:
            event_id = f"rep_event_{int(datetime.now().timestamp())}_{creator_id}"
            
            event = ReputationEvent(
                id=event_id,
                creator_id=creator_id,
                event_type=event_type,
                impact_score=impact_score,
                timestamp=datetime.now(),
                metadata=metadata or {}
            )
            
            self.event_queue.append(event)
            
            # Process event immediately for real-time updates
            await self._process_reputation_event(event)
            
            logger.info(f"Recorded reputation event {event_id} for creator {creator_id}")
            return event_id
            
        except Exception as e:
            logger.error(f"Error recording reputation event: {e}")
            raise
    
    async def _process_reputation_event(self, event: ReputationEvent):
        """Process individual reputation event."""
        try:
            creator_id = event.creator_id
            
            # Ensure creator profile exists
            if creator_id not in self.reputation_profiles:
                await self.create_reputation_profile(creator_id)
            
            # Update relevant metrics based on event type
            metric_updates = self._calculate_metric_updates(event)
            
            for metric_type, score_change in metric_updates.items():
                current_metric = self.reputation_metrics[creator_id][metric_type]
                
                # Update metric value with decay factor for older events
                decay_factor = self._calculate_decay_factor(event.timestamp)
                adjusted_change = score_change * decay_factor
                
                new_value = max(0, min(100, current_metric.value + adjusted_change))
                
                # Store historical value
                current_metric.historical_values.append((event.timestamp, new_value))
                
                # Update metric
                current_metric.value = new_value
                current_metric.last_updated = datetime.now()
                
                # Update trend
                current_metric.trend = self._calculate_trend(current_metric.historical_values)
            
            # Recalculate overall reputation score
            await self._update_overall_reputation_score(creator_id)
            
            # Check for badge eligibility
            await self._check_badge_eligibility(creator_id)
            
            # Mark event as processed
            event.processed = True
            self.reputation_events.append(event)
            
        except Exception as e:
            logger.error(f"Error processing reputation event {event.id}: {e}")
    
    def _calculate_metric_updates(self, event: ReputationEvent) -> Dict[ReputationMetricType, float]:
        """Calculate metric updates based on event type."""
        updates = defaultdict(float)
        
        event_mappings = {
            ReputationEventType.CONTENT_PUBLISHED: {
                ReputationMetricType.CONTENT_QUALITY: 2.0,
                ReputationMetricType.RELIABILITY: 1.0
            },
            ReputationEventType.CONTENT_LIKED: {
                ReputationMetricType.CONTENT_QUALITY: 1.0,
                ReputationMetricType.ENGAGEMENT_RATE: 1.5
            },
            ReputationEventType.CONTENT_SHARED: {
                ReputationMetricType.CONTENT_QUALITY: 1.5,
                ReputationMetricType.ENGAGEMENT_RATE: 2.0
            },
            ReputationEventType.COLLABORATION_COMPLETED: {
                ReputationMetricType.COLLABORATION_SUCCESS: 5.0,
                ReputationMetricType.RELIABILITY: 3.0
            },
            ReputationEventType.COLLABORATION_CANCELLED: {
                ReputationMetricType.COLLABORATION_SUCCESS: -3.0,
                ReputationMetricType.RELIABILITY: -2.0
            },
            ReputationEventType.COMMUNITY_HELP: {
                ReputationMetricType.COMMUNITY_CONTRIBUTION: 3.0,
                ReputationMetricType.MENTORSHIP: 2.0
            },
            ReputationEventType.GUIDELINE_VIOLATION: {
                ReputationMetricType.PLATFORM_COMPLIANCE: -10.0,
                ReputationMetricType.RELIABILITY: -5.0
            },
            ReputationEventType.POSITIVE_REVIEW: {
                ReputationMetricType.COLLABORATION_SUCCESS: 2.0,
                ReputationMetricType.RELIABILITY: 1.5
            },
            ReputationEventType.NEGATIVE_REVIEW: {
                ReputationMetricType.COLLABORATION_SUCCESS: -2.0,
                ReputationMetricType.RELIABILITY: -1.5
            },
            ReputationEventType.MILESTONE_ACHIEVED: {
                ReputationMetricType.AUDIENCE_GROWTH: 5.0,
                ReputationMetricType.REVENUE_PERFORMANCE: 3.0
            },
            ReputationEventType.MENTOR_SESSION: {
                ReputationMetricType.MENTORSHIP: 4.0,
                ReputationMetricType.COMMUNITY_CONTRIBUTION: 2.0
            },
            ReputationEventType.INNOVATIVE_CONTENT: {
                ReputationMetricType.INNOVATION: 5.0,
                ReputationMetricType.CONTENT_QUALITY: 3.0
            },
            ReputationEventType.CONSISTENT_ACTIVITY: {
                ReputationMetricType.RELIABILITY: 2.0,
                ReputationMetricType.ENGAGEMENT_RATE: 1.0
            }
        }
        
        base_updates = event_mappings.get(event.event_type, {})
        
        # Apply impact score multiplier
        for metric_type, base_score in base_updates.items():
            updates[metric_type] = base_score * event.impact_score
        
        return dict(updates)
    
    def _calculate_decay_factor(self, event_timestamp: datetime) -> float:
        """Calculate decay factor for event impact based on age."""
        age_days = (datetime.now() - event_timestamp).days
        
        # Events lose impact over time (exponential decay)
        # Fresh events (0-7 days): 100% impact
        # Older events: decreasing impact
        if age_days <= 7:
            return 1.0
        elif age_days <= 30:
            return 0.8
        elif age_days <= 90:
            return 0.6
        elif age_days <= 180:
            return 0.4
        else:
            return 0.2
    
    def _calculate_trend(self, historical_values: List[Tuple[datetime, float]]) -> str:
        """Calculate trend based on historical values."""
        if len(historical_values) < 2:
            return "stable"
        
        # Look at last 5 values or all if less than 5
        recent_values = historical_values[-5:]
        values = [v[1] for v in recent_values]
        
        # Calculate slope
        n = len(values)
        x_mean = (n - 1) / 2
        y_mean = sum(values) / n
        
        slope = sum((i - x_mean) * (values[i] - y_mean) for i in range(n))
        slope /= sum((i - x_mean) ** 2 for i in range(n))
        
        if slope > 0.5:
            return "increasing"
        elif slope < -0.5:
            return "decreasing"
        else:
            return "stable"
    
    async def _update_overall_reputation_score(self, creator_id: str):
        """Update overall reputation score based on weighted metrics."""
        try:
            profile = self.reputation_profiles[creator_id]
            metrics = self.reputation_metrics[creator_id]
            
            # Calculate weighted score
            total_score = 0.0
            total_weight = 0.0
            
            for metric_type, metric in metrics.items():
                weight = self.metric_weights[metric_type]
                total_score += metric.value * weight
                total_weight += weight
            
            # Normalize score
            if total_weight > 0:
                normalized_score = total_score / total_weight
            else:
                normalized_score = 0.0
            
            # Apply bonus/penalty modifiers
            modifier = self._calculate_score_modifier(creator_id)
            final_score = max(0, normalized_score * modifier)
            
            # Update profile
            profile.overall_score = final_score
            profile.reputation_level = self._determine_reputation_level(final_score)
            profile.trust_level = self._determine_trust_level(creator_id)
            profile.last_updated = datetime.now()
            
            # Update metrics dict in profile
            profile.metrics = {mt: metrics[mt].value for mt in metrics}
            
            logger.info(f"Updated reputation score for creator {creator_id}: {final_score:.2f}")
            
        except Exception as e:
            logger.error(f"Error updating reputation score: {e}")
    
    def _calculate_score_modifier(self, creator_id: str) -> float:
        """Calculate score modifier based on warnings and certifications."""
        profile = self.reputation_profiles[creator_id]
        modifier = 1.0
        
        # Penalty for warnings
        warning_penalty = len(profile.warnings) * 0.05  # 5% penalty per warning
        modifier -= warning_penalty
        
        # Bonus for certifications
        certification_bonus = len(profile.certifications) * 0.02  # 2% bonus per certification
        modifier += certification_bonus
        
        return max(0.1, modifier)  # Minimum 10% of base score
    
    def _determine_reputation_level(self, score: float) -> ReputationLevel:
        """Determine reputation level based on score."""
        for level, (min_score, max_score) in self.level_thresholds.items():
            if min_score <= score <= max_score:
                return level
        return ReputationLevel.NEWCOMER
    
    def _determine_trust_level(self, creator_id: str) -> TrustLevel:
        """Determine trust level based on various factors."""
        profile = self.reputation_profiles[creator_id]
        metrics = self.reputation_metrics[creator_id]
        
        # Base trust on reliability and compliance
        reliability = metrics[ReputationMetricType.RELIABILITY].value
        compliance = metrics[ReputationMetricType.PLATFORM_COMPLIANCE].value
        
        # Account for warnings and certifications
        warning_count = len(profile.warnings)
        certification_count = len(profile.certifications)
        
        # Calculate trust score
        trust_score = (reliability + compliance) / 2
        trust_score -= warning_count * 10  # Penalties for warnings
        trust_score += certification_count * 5  # Bonus for certifications
        
        # Determine trust level
        if trust_score >= 90 and certification_count >= 3:
            return TrustLevel.ELITE
        elif trust_score >= 80 and certification_count >= 2:
            return TrustLevel.VERIFIED
        elif trust_score >= 70 and warning_count == 0:
            return TrustLevel.TRUSTED
        elif trust_score >= 50:
            return TrustLevel.BASIC
        else:
            return TrustLevel.UNVERIFIED
    
    async def _check_badge_eligibility(self, creator_id: str):
        """Check and award badges based on current metrics."""
        try:
            profile = self.reputation_profiles[creator_id]
            metrics = self.reputation_metrics[creator_id]
            
            for badge_id, badge_info in self.badges_catalog.items():
                if badge_id in profile.badges:
                    continue  # Already has this badge
                
                criteria = badge_info["criteria"]
                eligible = True
                
                # Check metric criteria
                for criterion, threshold in criteria.items():
                    if criterion in [mt.value for mt in ReputationMetricType]:
                        metric_type = ReputationMetricType(criterion)
                        if metrics[metric_type].value < threshold:
                            eligible = False
                            break
                    # Additional criteria would be checked here (min_content, etc.)
                
                if eligible:
                    profile.badges.append(badge_id)
                    logger.info(f"Awarded badge '{badge_id}' to creator {creator_id}")
                    
                    # Record badge achievement event
                    await self.record_reputation_event(
                        creator_id,
                        ReputationEventType.MILESTONE_ACHIEVED,
                        impact_score=2.0,
                        metadata={"badge": badge_id, "badge_name": badge_info["name"]}
                    )
            
        except Exception as e:
            logger.error(f"Error checking badge eligibility: {e}")
    
    async def get_reputation_profile(self, creator_id: str) -> Optional[CreatorReputationProfile]:
        """Get creator reputation profile."""
        return self.reputation_profiles.get(creator_id)
    
    async def get_creator_rankings(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get top creators by reputation score."""
        try:
            # Sort creators by reputation score
            sorted_creators = sorted(
                self.reputation_profiles.items(),
                key=lambda x: x[1].overall_score,
                reverse=True
            )
            
            rankings = []
            for rank, (creator_id, profile) in enumerate(sorted_creators[:limit], 1):
                rankings.append({
                    "rank": rank,
                    "creator_id": creator_id,
                    "reputation_score": profile.overall_score,
                    "reputation_level": profile.reputation_level,
                    "trust_level": profile.trust_level,
                    "badges_count": len(profile.badges),
                    "top_metric": max(profile.metrics.items(), key=lambda x: x[1])[0] if profile.metrics else None
                })
            
            return rankings
            
        except Exception as e:
            logger.error(f"Error getting creator rankings: {e}")
            return []
    
    async def get_reputation_analytics(
        self, 
        creator_id: str, 
        period_days: int = 30
    ) -> Optional[ReputationAnalytics]:
        """Get reputation analytics for creator."""
        try:
            if creator_id not in self.reputation_profiles:
                return None
            
            profile = self.reputation_profiles[creator_id]
            current_score = profile.overall_score
            
            # Calculate score change over period
            cutoff_date = datetime.now() - timedelta(days=period_days)
            historical_events = [
                e for e in self.reputation_events 
                if e.creator_id == creator_id and e.timestamp >= cutoff_date
            ]
            
            # Get score from period_days ago (approximate)
            previous_score = current_score
            for event in reversed(historical_events):
                # This is a simplified calculation
                impact = self._calculate_metric_updates(event)
                total_impact = sum(impact.values()) * 0.1  # Rough approximation
                previous_score -= total_impact
            
            score_change = current_score - previous_score
            
            # Calculate current rank
            all_scores = [p.overall_score for p in self.reputation_profiles.values()]
            current_rank = len([s for s in all_scores if s > current_score]) + 1
            
            # Percentile rank
            percentile_rank = (len(all_scores) - current_rank + 1) / len(all_scores) * 100
            
            # Find comparable creators (similar score range)
            comparable_creators = []
            score_range = 50  # ±50 points
            for cid, prof in self.reputation_profiles.items():
                if cid != creator_id and abs(prof.overall_score - current_score) <= score_range:
                    comparable_creators.append(cid)
            
            # Generate recommendations based on lowest metrics
            metrics = self.reputation_metrics[creator_id]
            lowest_metrics = sorted(metrics.items(), key=lambda x: x[1].value)[:3]
            
            recommendations = []
            for metric_type, metric in lowest_metrics:
                if metric.value < 70:  # Below good threshold
                    recommendations.append(f"Improve {metric_type.value.replace('_', ' ')}")
            
            return ReputationAnalytics(
                creator_id=creator_id,
                period_days=period_days,
                score_change=score_change,
                rank_change=0,  # Would need historical rank data
                metric_improvements=[],  # Would calculate from historical data
                metric_declines=[],  # Would calculate from historical data
                growth_rate=(score_change / previous_score * 100) if previous_score > 0 else 0,
                percentile_rank=percentile_rank,
                comparable_creators=comparable_creators[:5],
                recommendations=recommendations
            )
            
        except Exception as e:
            logger.error(f"Error getting reputation analytics: {e}")
            return None
    
    async def add_certification(self, creator_id: str, certification: str) -> bool:
        """Add certification to creator profile."""
        try:
            if creator_id not in self.reputation_profiles:
                await self.create_reputation_profile(creator_id)
            
            profile = self.reputation_profiles[creator_id]
            if certification not in profile.certifications:
                profile.certifications.append(certification)
                
                # Record certification achievement
                await self.record_reputation_event(
                    creator_id,
                    ReputationEventType.MILESTONE_ACHIEVED,
                    impact_score=3.0,
                    metadata={"certification": certification}
                )
                
                logger.info(f"Added certification '{certification}' to creator {creator_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error adding certification: {e}")
            return False
    
    async def add_warning(self, creator_id: str, warning: str, severity: str = "medium") -> bool:
        """Add warning to creator profile."""
        try:
            if creator_id not in self.reputation_profiles:
                await self.create_reputation_profile(creator_id)
            
            profile = self.reputation_profiles[creator_id]
            warning_entry = f"{severity.upper()}: {warning}"
            profile.warnings.append(warning_entry)
            
            # Record warning impact
            severity_impact = {"low": -5.0, "medium": -10.0, "high": -20.0}
            impact = severity_impact.get(severity, -10.0)
            
            await self.record_reputation_event(
                creator_id,
                ReputationEventType.GUIDELINE_VIOLATION,
                impact_score=impact,
                metadata={"warning": warning, "severity": severity}
            )
            
            logger.info(f"Added {severity} warning to creator {creator_id}: {warning}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding warning: {e}")
            return False
    
    async def remove_warning(self, creator_id: str, warning_index: int) -> bool:
        """Remove warning from creator profile."""
        try:
            if creator_id not in self.reputation_profiles:
                return False
            
            profile = self.reputation_profiles[creator_id]
            if 0 <= warning_index < len(profile.warnings):
                removed_warning = profile.warnings.pop(warning_index)
                
                # Small positive impact for warning removal
                await self.record_reputation_event(
                    creator_id,
                    ReputationEventType.MILESTONE_ACHIEVED,
                    impact_score=2.0,
                    metadata={"warning_removed": removed_warning}
                )
                
                logger.info(f"Removed warning from creator {creator_id}: {removed_warning}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error removing warning: {e}")
            return False
    
    async def process_event_queue(self) -> int:
        """Process all events in queue."""
        processed_count = 0
        
        while self.event_queue:
            event = self.event_queue.pop(0)
            if not event.processed:
                await self._process_reputation_event(event)
                processed_count += 1
        
        return processed_count
    
    def get_service_metrics(self) -> Dict[str, Any]:
        """Get comprehensive service metrics."""
        total_creators = len(self.reputation_profiles)
        
        if total_creators == 0:
            return {
                "total_creators": 0,
                "average_reputation_score": 0,
                "events_processed": 0,
                "badges_awarded": 0,
                "certifications_issued": 0
            }
        
        # Calculate averages and totals
        total_score = sum(p.overall_score for p in self.reputation_profiles.values())
        average_score = total_score / total_creators
        
        total_badges = sum(len(p.badges) for p in self.reputation_profiles.values())
        total_certifications = sum(len(p.certifications) for p in self.reputation_profiles.values())
        
        # Level distribution
        level_distribution = defaultdict(int)
        trust_distribution = defaultdict(int)
        
        for profile in self.reputation_profiles.values():
            level_distribution[profile.reputation_level.value] += 1
            trust_distribution[profile.trust_level.value] += 1
        
        return {
            "total_creators": total_creators,
            "average_reputation_score": average_score,
            "events_processed": len(self.reputation_events),
            "events_in_queue": len(self.event_queue),
            "badges_awarded": total_badges,
            "certifications_issued": total_certifications,
            "reputation_level_distribution": dict(level_distribution),
            "trust_level_distribution": dict(trust_distribution),
            "badges_catalog_size": len(self.badges_catalog)
        }


# Global service instance
_reputation_service_instance = None

def get_creator_reputation_service() -> CreatorReputationService:
    """Get singleton instance of CreatorReputationService."""
    global _reputation_service_instance
    if _reputation_service_instance is None:
        _reputation_service_instance = CreatorReputationService()
    return _reputation_service_instance


# Example usage and testing
async def example_usage():
    """Example usage of Creator Reputation Service."""
    service = get_creator_reputation_service()
    
    # Create reputation profile
    profile = await service.create_reputation_profile("creator_123")
    print(f"Created profile for creator: {profile.creator_id}")
    
    # Record various reputation events
    events = [
        (ReputationEventType.CONTENT_PUBLISHED, 1.0, {"content_type": "video"}),
        (ReputationEventType.CONTENT_LIKED, 1.2, {"likes": 150}),
        (ReputationEventType.COLLABORATION_COMPLETED, 2.0, {"project": "music_video"}),
        (ReputationEventType.COMMUNITY_HELP, 1.5, {"help_type": "mentoring"}),
        (ReputationEventType.INNOVATIVE_CONTENT, 2.5, {"innovation_type": "new_format"}),
    ]
    
    for event_type, impact, metadata in events:
        event_id = await service.record_reputation_event(
            "creator_123", event_type, impact, metadata
        )
        print(f"Recorded event: {event_id}")
    
    # Add certification
    await service.add_certification("creator_123", "Audio Engineering Certification")
    
    # Get updated profile
    updated_profile = await service.get_reputation_profile("creator_123")
    print(f"Updated reputation score: {updated_profile.overall_score:.2f}")
    print(f"Reputation level: {updated_profile.reputation_level}")
    print(f"Trust level: {updated_profile.trust_level}")
    print(f"Badges earned: {updated_profile.badges}")
    
    # Get rankings
    rankings = await service.get_creator_rankings(10)
    print(f"Top creators: {rankings}")
    
    # Get analytics
    analytics = await service.get_reputation_analytics("creator_123")
    if analytics:
        print(f"Analytics: Score change: {analytics.score_change:.2f}, "
              f"Percentile: {analytics.percentile_rank:.1f}%")
    
    # Get service metrics
    metrics = service.get_service_metrics()
    print(f"Service metrics: {metrics}")


if __name__ == "__main__":
    # Run example
    asyncio.run(example_usage())