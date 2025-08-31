"""Enterprise Engagement Analytics - Advanced engagement analytics system for IA Influencer platform.

This module provides comprehensive engagement analytics and insights that track,
analyze, and optimize user engagement patterns across the gamification ecosystem
for multi-format content creators.

Architecture: Enterprise Production-Ready (Backend Level 2)
Module: backend/business/engagement/engagement_analytics.py
Expert Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + DevOps

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

⚠️ STRICT COPYRIGHT WARNING - INTELLECTUAL PROPERTY PROTECTION
================================================================
This code and concept are the EXCLUSIVE PROPERTY of Fahed Mlaiel.
Unauthorized access, copying, modification, distribution, reverse engineering,
or commercialization without explicit written permission from Fahed Mlaiel
(mlaiel@live.de) is STRICTLY PROHIBITED and will result in immediate legal
action under German and International copyright laws.

For licensing inquiries ONLY: mlaiel@live.de
================================================================

Business Logic Integration:
Creator Upload → AI Processing → Protection → SEO → Collaboration Matching + Gamification →
Engagement Analytics → Distribution → Monetization → Analytics
"""import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Union, Set
from uuid import uuid4, UUID
from decimal import Decimal
from enum import Enum
from dataclasses import dataclass, field
import json
import statistics
import math

logger = logging.getLogger(__name__)


class EngagementEventType(str, Enum):
    """Types of engagement events tracked."""    LOGIN = "login"
    CONTENT_UPLOAD = "content_upload"
    CONTENT_VIEW = "content_view"
    CONTENT_LIKE = "content_like"
    CONTENT_SHARE = "content_share"
    CONTENT_COMMENT = "content_comment"
    PROFILE_VIEW = "profile_view"
    COLLABORATION_INITIATED = "collaboration_initiated"
    COLLABORATION_COMPLETED = "collaboration_completed"
    CHALLENGE_JOINED = "challenge_joined"
    CHALLENGE_COMPLETED = "challenge_completed"
    ACHIEVEMENT_UNLOCKED = "achievement_unlocked"
    MARKETPLACE_BROWSE = "marketplace_browse"
    MARKETPLACE_PURCHASE = "marketplace_purchase"
    LEADERBOARD_VIEW = "leaderboard_view"
    SOCIAL_INTERACTION = "social_interaction"
    FEATURE_USAGE = "feature_usage"
    SESSION_START = "session_start"
    SESSION_END = "session_end"


class EngagementMetricType(str, Enum):
    """Types of engagement metrics."""    SESSION_DURATION = "session_duration"
    DAILY_ACTIVE_TIME = "daily_active_time"
    FEATURE_ADOPTION_RATE = "feature_adoption_rate"
    CONTENT_INTERACTION_RATE = "content_interaction_rate"
    COLLABORATION_PARTICIPATION = "collaboration_participation"
    CHALLENGE_COMPLETION_RATE = "challenge_completion_rate"
    ACHIEVEMENT_UNLOCK_RATE = "achievement_unlock_rate"
    MARKETPLACE_ENGAGEMENT = "marketplace_engagement"
    SOCIAL_CONNECTIVITY = "social_connectivity"
    RETENTION_RATE = "retention_rate"
    CHURN_RISK_SCORE = "churn_risk_score"
    ENGAGEMENT_MOMENTUM = "engagement_momentum"


class AnalyticsPeriod(str, Enum):
    """Time periods for analytics."""    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"
    CUSTOM = "custom"


@dataclass
class EngagementEvent:
    """Represents a single engagement event."""    event_id: str = field(default_factory=lambda: str(uuid4()))
    user_id: str = ""
    event_type: EngagementEventType = EngagementEventType.LOGIN
    
    # Event details
    timestamp: datetime = field(default_factory=datetime.utcnow)
    duration: Optional[timedelta] = None
    value: Optional[float] = None
    
    # Context
    session_id: Optional[str] = None
    platform: Optional[str] = None
    device_type: Optional[str] = None
    location: Optional[str] = None
    
    # Related entities
    content_id: Optional[str] = None
    challenge_id: Optional[str] = None
    achievement_id: Optional[str] = None
    collaboration_id: Optional[str] = None
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    processed: bool = False
    
    def get_event_value(self) -> float:
        """Get numeric value for the event."""        if self.value is not None:
            return self.value
        
        # Default values based on event type
        event_values = {
            EngagementEventType.LOGIN: 1.0,
            EngagementEventType.CONTENT_UPLOAD: 5.0,
            EngagementEventType.CONTENT_VIEW: 0.5,
            EngagementEventType.CONTENT_LIKE: 1.0,
            EngagementEventType.CONTENT_SHARE: 2.0,
            EngagementEventType.CONTENT_COMMENT: 3.0,
            EngagementEventType.COLLABORATION_INITIATED: 4.0,
            EngagementEventType.COLLABORATION_COMPLETED: 8.0,
            EngagementEventType.CHALLENGE_JOINED: 3.0,
            EngagementEventType.CHALLENGE_COMPLETED: 10.0,
            EngagementEventType.ACHIEVEMENT_UNLOCKED: 5.0,
            EngagementEventType.MARKETPLACE_PURCHASE: 6.0,
        }
        
        return event_values.get(self.event_type, 1.0)


@dataclass
class EngagementMetrics:
    """Comprehensive engagement metrics for a user."""    user_id: str = ""
    period_start: datetime = field(default_factory=datetime.utcnow)
    period_end: datetime = field(default_factory=datetime.utcnow)
    
    # Activity metrics
    total_sessions: int = 0
    total_session_time: timedelta = field(default_factory=lambda: timedelta())
    average_session_duration: timedelta = field(default_factory=lambda: timedelta())
    daily_active_time: timedelta = field(default_factory=lambda: timedelta())
    
    # Interaction metrics
    total_events: int = 0
    events_by_type: Dict[str, int] = field(default_factory=dict)
    content_interactions: int = 0
    social_interactions: int = 0
    
    # Feature adoption
    features_used: Set[str] = field(default_factory=set)
    feature_adoption_rate: float = 0.0
    
    # Gamification engagement
    challenges_joined: int = 0
    challenges_completed: int = 0
    achievements_unlocked: int = 0
    collaborations_participated: int = 0
    
    # Marketplace activity
    marketplace_views: int = 0
    marketplace_purchases: int = 0
    virtual_currency_earned: Decimal = field(default_factory=lambda: Decimal('0'))
    virtual_currency_spent: Decimal = field(default_factory=lambda: Decimal('0'))
    
    # Engagement quality
    engagement_score: float = 0.0
    engagement_momentum: float = 0.0
    consistency_score: float = 0.0
    depth_score: float = 0.0
    
    # Predictive metrics
    churn_risk_score: float = 0.0
    retention_probability: float = 0.0
    lifetime_value_prediction: float = 0.0
    
    def calculate_engagement_score(self) -> float:
        """Calculate overall engagement score."""        # Weighted combination of different factors
        activity_score = min(100, (self.total_sessions * 2) + (self.total_session_time.total_seconds() / 3600))
        interaction_score = min(100, self.content_interactions * 0.5 + self.social_interactions * 1.5)
        feature_score = self.feature_adoption_rate * 100
        gamification_score = min(100, (self.challenges_completed * 10) + (self.achievements_unlocked * 5))
        
        # Weighted average
        engagement_score = (
            activity_score * 0.3 +
            interaction_score * 0.25 +
            feature_score * 0.2 +
            gamification_score * 0.25
        )
        
        return min(100, engagement_score)


@dataclass
class EngagementInsight:
    """Represents an actionable engagement insight."""    insight_id: str = field(default_factory=lambda: str(uuid4()))
    user_id: str = ""
    insight_type: str = ""
    title: str = ""
    description: str = ""
    
    # Insight details
    priority: str = "medium"  # low, medium, high, critical
    confidence: float = 0.0  # 0-1 confidence score
    impact_prediction: float = 0.0  # Predicted impact on engagement
    
    # Recommendations
    recommended_actions: List[str] = field(default_factory=list)
    suggested_content: List[str] = field(default_factory=list)
    
    # Data backing the insight
    supporting_metrics: Dict[str, Any] = field(default_factory=dict)
    trend_data: List[Dict[str, Any]] = field(default_factory=list)
    
    # Metadata
    generated_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    acted_upon: bool = False


class EngagementAnalytics:
    """    Enterprise-grade engagement analytics system.
    
    Provides comprehensive tracking, analysis, and insights into user
    engagement patterns across the gamification ecosystem.
    """    
    def __init__(self):
        """Initialize the engagement analytics system."""        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self._events: List[EngagementEvent] = []
        self._user_metrics: Dict[str, EngagementMetrics] = {}
        self._user_sessions: Dict[str, List[Dict[str, Any]]] = {}
        self._insights: Dict[str, List[EngagementInsight]] = {}
        self._processing_lock = asyncio.Lock()
        
        # Feature definitions for adoption tracking
        self._platform_features = {
            "content_upload", "collaboration_tools", "challenge_participation",
            "achievement_system", "marketplace", "leaderboards", "analytics_dashboard",
            "profile_customization", "social_features", "premium_tools"
        }
        
        self.logger.info("EngagementAnalytics initialized successfully")
    
    async def track_event(
        self,
        user_id: str,
        event_type: EngagementEventType,
        duration: Optional[timedelta] = None,
        value: Optional[float] = None,
        session_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> EngagementEvent:
        """Track an engagement event."""        try:
            event = EngagementEvent(
                user_id=user_id,
                event_type=event_type,
                duration=duration,
                value=value,
                session_id=session_id,
                metadata=metadata or {}
            )
            
            # Add contextual information
            if "platform" in (metadata or {}):
                event.platform = metadata["platform"]
            if "device_type" in (metadata or {}):
                event.device_type = metadata["device_type"]
            if "content_id" in (metadata or {}):
                event.content_id = metadata["content_id"]
            if "challenge_id" in (metadata or {}):
                event.challenge_id = metadata["challenge_id"]
            if "achievement_id" in (metadata or {}):
                event.achievement_id = metadata["achievement_id"]
            if "collaboration_id" in (metadata or {}):
                event.collaboration_id = metadata["collaboration_id"]
            
            # Store event
            self._events.append(event)
            
            # Process event immediately for real-time insights
            await self._process_event(event)
            
            self.logger.debug(f"Tracked {event_type.value} event for user {user_id}")
            
            return event
            
        except Exception as e:
            self.logger.error(f"Error tracking engagement event: {e}")
            raise
    
    async def _process_event(self, event: EngagementEvent) -> None:
        """Process an engagement event for real-time analytics."""        async with self._processing_lock:
            try:
                # Update session tracking
                await self._update_session_tracking(event)
                
                # Update user metrics
                await self._update_user_metrics(event)
                
                # Generate real-time insights
                await self._generate_real_time_insights(event)
                
                # Mark event as processed
                event.processed = True
                
            except Exception as e:
                self.logger.error(f"Error processing engagement event: {e}")
    
    async def _update_session_tracking(self, event: EngagementEvent) -> None:
        """Update session tracking data."""        if event.session_id:
            if event.user_id not in self._user_sessions:
                self._user_sessions[event.user_id] = []
            
            # Find or create session
            session = None
            for s in self._user_sessions[event.user_id]:
                if s["session_id"] == event.session_id:
                    session = s
                    break
            
            if not session:
                session = {
                    "session_id": event.session_id,
                    "start_time": event.timestamp,
                    "end_time": event.timestamp,
                    "events": [],
                    "platforms": set(),
                    "devices": set()
                }
                self._user_sessions[event.user_id].append(session)
            
            # Update session
            session["events"].append(event.event_id)
            session["end_time"] = event.timestamp
            
            if event.platform:
                session["platforms"].add(event.platform)
            if event.device_type:
                session["devices"].add(event.device_type)
    
    async def _update_user_metrics(self, event: EngagementEvent) -> None:
        """Update user engagement metrics based on event."""        user_id = event.user_id
        
        # Get or create metrics for today
        today = event.timestamp.date()
        metrics_key = f"{user_id}_{today}"
        
        if metrics_key not in self._user_metrics:
            self._user_metrics[metrics_key] = EngagementMetrics(
                user_id=user_id,
                period_start=datetime.combine(today, datetime.min.time()),
                period_end=datetime.combine(today, datetime.max.time())
            )
        
        metrics = self._user_metrics[metrics_key]
        
        # Update event counts
        metrics.total_events += 1
        event_type_key = event.event_type.value
        metrics.events_by_type[event_type_key] = metrics.events_by_type.get(event_type_key, 0) + 1
        
        # Update specific metrics based on event type
        if event.event_type in [EngagementEventType.CONTENT_VIEW, EngagementEventType.CONTENT_LIKE, 
                                EngagementEventType.CONTENT_SHARE, EngagementEventType.CONTENT_COMMENT]:
            metrics.content_interactions += 1
        
        elif event.event_type in [EngagementEventType.SOCIAL_INTERACTION, EngagementEventType.COLLABORATION_INITIATED]:
            metrics.social_interactions += 1
        
        elif event.event_type == EngagementEventType.CHALLENGE_JOINED:
            metrics.challenges_joined += 1
        
        elif event.event_type == EngagementEventType.CHALLENGE_COMPLETED:
            metrics.challenges_completed += 1
        
        elif event.event_type == EngagementEventType.ACHIEVEMENT_UNLOCKED:
            metrics.achievements_unlocked += 1
        
        elif event.event_type in [EngagementEventType.COLLABORATION_INITIATED, EngagementEventType.COLLABORATION_COMPLETED]:
            metrics.collaborations_participated += 1
        
        elif event.event_type == EngagementEventType.MARKETPLACE_BROWSE:
            metrics.marketplace_views += 1
        
        elif event.event_type == EngagementEventType.MARKETPLACE_PURCHASE:
            metrics.marketplace_purchases += 1
        
        # Track feature usage
        if event.event_type == EngagementEventType.FEATURE_USAGE:
            feature_name = event.metadata.get("feature_name")
            if feature_name:
                metrics.features_used.add(feature_name)
        
        # Update feature adoption rate
        metrics.feature_adoption_rate = len(metrics.features_used) / len(self._platform_features)
        
        # Recalculate engagement score
        metrics.engagement_score = metrics.calculate_engagement_score()
    
    async def _generate_real_time_insights(self, event: EngagementEvent) -> None:
        """Generate real-time insights based on event patterns."""        try:
            user_id = event.user_id
            
            # Initialize insights list for user
            if user_id not in self._insights:
                self._insights[user_id] = []
            
            # Check for specific insight patterns
            
            # Detect feature discovery opportunities
            if event.event_type == EngagementEventType.FEATURE_USAGE:
                await self._check_feature_discovery_insights(user_id, event)
            
            # Detect engagement momentum
            if event.event_type in [EngagementEventType.CONTENT_UPLOAD, EngagementEventType.CHALLENGE_COMPLETED]:
                await self._check_momentum_insights(user_id, event)
            
            # Detect collaboration opportunities
            if event.event_type == EngagementEventType.CONTENT_UPLOAD:
                await self._check_collaboration_insights(user_id, event)
            
            # Detect monetization opportunities
            if event.event_type == EngagementEventType.MARKETPLACE_BROWSE:
                await self._check_monetization_insights(user_id, event)
            
        except Exception as e:
            self.logger.error(f"Error generating real-time insights: {e}")
    
    async def _check_feature_discovery_insights(self, user_id: str, event: EngagementEvent) -> None:
        """Check for feature discovery opportunities."""        # Get user's feature usage pattern
        user_events = [e for e in self._events if e.user_id == user_id and e.processed]
        feature_events = [e for e in user_events if e.event_type == EngagementEventType.FEATURE_USAGE]
        
        used_features = {e.metadata.get("feature_name") for e in feature_events if e.metadata.get("feature_name")}
        unused_features = self._platform_features - used_features
        
        if len(unused_features) > 0:
            # Suggest most relevant unused feature
            feature_recommendations = {
                "collaboration_tools": "Try collaborating with other creators to expand your reach",
                "challenge_participation": "Join challenges to earn rewards and showcase your skills",
                "marketplace": "Explore the marketplace for tools to boost your content",
                "analytics_dashboard": "Check your analytics to understand your audience better"
            }
            
            for feature in unused_features:
                if feature in feature_recommendations:
                    insight = EngagementInsight(
                        user_id=user_id,
                        insight_type="feature_discovery",
                        title=f"Discover {feature.replace('_', ' ').title()}",
                        description=feature_recommendations[feature],
                        priority="medium",
                        confidence=0.8,
                        impact_prediction=15.0,
                        recommended_actions=[f"explore_{feature}"],
                        expires_at=datetime.utcnow() + timedelta(days=7)
                    )
                    
                    self._insights[user_id].append(insight)
                    break  # Only suggest one feature at a time
    
    async def _check_momentum_insights(self, user_id: str, event: EngagementEvent) -> None:
        """Check for engagement momentum insights."""        # Get recent events (last 7 days)
        week_ago = datetime.utcnow() - timedelta(days=7)
        recent_events = [
            e for e in self._events 
            if e.user_id == user_id and e.timestamp >= week_ago and e.processed
        ]
        
        # Calculate momentum score
        daily_activity = {}
        for e in recent_events:
            day = e.timestamp.date()
            if day not in daily_activity:
                daily_activity[day] = 0
            daily_activity[day] += e.get_event_value()
        
        if len(daily_activity) >= 3:  # At least 3 days of activity
            activity_values = list(daily_activity.values())
            momentum = statistics.mean(activity_values[-3:]) - statistics.mean(activity_values[:-3]) if len(activity_values) > 3 else 0
            
            if momentum > 5:  # Positive momentum
                insight = EngagementInsight(
                    user_id=user_id,
                    insight_type="momentum_boost",
                    title="You're on Fire! 🔥",
                    description="Your engagement is trending upward. Keep the momentum going!",
                    priority="high",
                    confidence=0.9,
                    impact_prediction=25.0,
                    recommended_actions=["maintain_streak", "try_new_features", "collaborate"],
                    supporting_metrics={"momentum_score": momentum, "daily_activity": daily_activity}
                )
                
                self._insights[user_id].append(insight)
    
    async def _check_collaboration_insights(self, user_id: str, event: EngagementEvent) -> None:
        """Check for collaboration opportunities."""        # Get collaboration history
        collab_events = [
            e for e in self._events 
            if e.user_id == user_id and 
               e.event_type in [EngagementEventType.COLLABORATION_INITIATED, EngagementEventType.COLLABORATION_COMPLETED] and
               e.processed
        ]
        
        # If user hasn't collaborated much, suggest it
        if len(collab_events) < 3:
            insight = EngagementInsight(
                user_id=user_id,
                insight_type="collaboration_opportunity",
                title="Collaboration Opportunity",
                description="Collaborating with other creators can significantly boost your reach and earnings.",
                priority="medium",
                confidence=0.75,
                impact_prediction=30.0,
                recommended_actions=["browse_creators", "join_collaboration_challenge"],
                supporting_metrics={"collaboration_count": len(collab_events)}
            )
            
            self._insights[user_id].append(insight)
    
    async def _check_monetization_insights(self, user_id: str, event: EngagementEvent) -> None:
        """Check for monetization opportunities."""        # Get marketplace activity
        marketplace_events = [
            e for e in self._events 
            if e.user_id == user_id and 
               e.event_type in [EngagementEventType.MARKETPLACE_BROWSE, EngagementEventType.MARKETPLACE_PURCHASE] and
               e.processed
        ]
        
        browse_count = len([e for e in marketplace_events if e.event_type == EngagementEventType.MARKETPLACE_BROWSE])
        purchase_count = len([e for e in marketplace_events if e.event_type == EngagementEventType.MARKETPLACE_PURCHASE])
        
        # If user browses but doesn't purchase, suggest specific items
        if browse_count >= 3 and purchase_count == 0:
            insight = EngagementInsight(
                user_id=user_id,
                insight_type="monetization_opportunity",
                title="Boost Your Content Performance",
                description="You've been exploring the marketplace. Consider investing in content boosts to increase your reach.",
                priority="medium",
                confidence=0.7,
                impact_prediction=20.0,
                recommended_actions=["purchase_content_boost", "try_premium_analytics"],
                suggested_content=["content_boost_small", "premium_analytics"],
                supporting_metrics={"browse_count": browse_count, "purchase_count": purchase_count}
            )
            
            self._insights[user_id].append(insight)
    
    async def calculate_user_metrics(
        self,
        user_id: str,
        period: AnalyticsPeriod = AnalyticsPeriod.DAILY,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> EngagementMetrics:
        """Calculate comprehensive engagement metrics for a user."""        try:
            # Determine time period
            if not start_date:
                if period == AnalyticsPeriod.DAILY:
                    start_date = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
                elif period == AnalyticsPeriod.WEEKLY:
                    start_date = datetime.utcnow() - timedelta(days=7)
                elif period == AnalyticsPeriod.MONTHLY:
                    start_date = datetime.utcnow() - timedelta(days=30)
                else:
                    start_date = datetime.utcnow() - timedelta(days=1)
            
            if not end_date:
                end_date = datetime.utcnow()
            
            # Get events in period
            period_events = [
                e for e in self._events
                if e.user_id == user_id and start_date <= e.timestamp <= end_date and e.processed
            ]
            
            # Initialize metrics
            metrics = EngagementMetrics(
                user_id=user_id,
                period_start=start_date,
                period_end=end_date
            )
            
            # Calculate basic metrics
            metrics.total_events = len(period_events)
            
            # Events by type
            for event in period_events:
                event_type = event.event_type.value
                metrics.events_by_type[event_type] = metrics.events_by_type.get(event_type, 0) + 1
            
            # Session metrics
            user_sessions = self._user_sessions.get(user_id, [])
            period_sessions = [
                s for s in user_sessions
                if start_date <= s["start_time"] <= end_date
            ]
            
            metrics.total_sessions = len(period_sessions)
            
            if period_sessions:
                total_session_seconds = sum(
                    (s["end_time"] - s["start_time"]).total_seconds()
                    for s in period_sessions
                )
                metrics.total_session_time = timedelta(seconds=total_session_seconds)
                metrics.average_session_duration = timedelta(seconds=total_session_seconds / len(period_sessions))
                metrics.daily_active_time = timedelta(seconds=total_session_seconds / max(1, (end_date - start_date).days))
            
            # Content and social interactions
            metrics.content_interactions = sum(
                metrics.events_by_type.get(event_type, 0)
                for event_type in ["content_view", "content_like", "content_share", "content_comment"]
            )
            
            metrics.social_interactions = sum(
                metrics.events_by_type.get(event_type, 0)
                for event_type in ["social_interaction", "collaboration_initiated"]
            )
            
            # Feature adoption
            feature_events = [e for e in period_events if e.event_type == EngagementEventType.FEATURE_USAGE]
            features_used = {e.metadata.get("feature_name") for e in feature_events if e.metadata.get("feature_name")}
            metrics.features_used = features_used
            metrics.feature_adoption_rate = len(features_used) / len(self._platform_features)
            
            # Gamification metrics
            metrics.challenges_joined = metrics.events_by_type.get("challenge_joined", 0)
            metrics.challenges_completed = metrics.events_by_type.get("challenge_completed", 0)
            metrics.achievements_unlocked = metrics.events_by_type.get("achievement_unlocked", 0)
            metrics.collaborations_participated = sum(
                metrics.events_by_type.get(event_type, 0)
                for event_type in ["collaboration_initiated", "collaboration_completed"]
            )
            
            # Marketplace metrics
            metrics.marketplace_views = metrics.events_by_type.get("marketplace_browse", 0)
            metrics.marketplace_purchases = metrics.events_by_type.get("marketplace_purchase", 0)
            
            # Calculate engagement quality scores
            metrics.engagement_score = metrics.calculate_engagement_score()
            metrics.engagement_momentum = await self._calculate_momentum_score(user_id, end_date)
            metrics.consistency_score = await self._calculate_consistency_score(user_id, start_date, end_date)
            metrics.depth_score = await self._calculate_depth_score(period_events)
            
            # Predictive metrics
            metrics.churn_risk_score = await self._calculate_churn_risk(user_id)
            metrics.retention_probability = 1.0 - metrics.churn_risk_score
            metrics.lifetime_value_prediction = await self._predict_lifetime_value(user_id, metrics)
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error calculating user metrics: {e}")
            return EngagementMetrics(user_id=user_id)
    
    async def _calculate_momentum_score(self, user_id: str, end_date: datetime) -> float:
        """Calculate engagement momentum score."""        try:
            # Get events from last 14 days, split into two 7-day periods
            two_weeks_ago = end_date - timedelta(days=14)
            one_week_ago = end_date - timedelta(days=7)
            
            recent_events = [
                e for e in self._events
                if e.user_id == user_id and e.timestamp >= two_weeks_ago and e.processed
            ]
            
            # Split into two periods
            period1_events = [e for e in recent_events if e.timestamp < one_week_ago]
            period2_events = [e for e in recent_events if e.timestamp >= one_week_ago]
            
            # Calculate activity scores for each period
            period1_score = sum(e.get_event_value() for e in period1_events)
            period2_score = sum(e.get_event_value() for e in period2_events)
            
            # Calculate momentum (percentage change)
            if period1_score == 0:
                return 100.0 if period2_score > 0 else 0.0
            
            momentum = ((period2_score - period1_score) / period1_score) * 100
            return max(-100, min(100, momentum))  # Clamp between -100 and 100
            
        except Exception as e:
            self.logger.error(f"Error calculating momentum score: {e}")
            return 0.0
    
    async def _calculate_consistency_score(self, user_id: str, start_date: datetime, end_date: datetime) -> float:
        """Calculate engagement consistency score."""        try:
            # Get daily activity counts
            daily_activity = {}
            period_events = [
                e for e in self._events
                if e.user_id == user_id and start_date <= e.timestamp <= end_date and e.processed
            ]
            
            for event in period_events:
                day = event.timestamp.date()
                if day not in daily_activity:
                    daily_activity[day] = 0
                daily_activity[day] += event.get_event_value()
            
            if len(daily_activity) < 2:
                return 0.0
            
            # Calculate consistency as inverse of coefficient of variation
            activity_values = list(daily_activity.values())
            mean_activity = statistics.mean(activity_values)
            
            if mean_activity == 0:
                return 0.0
            
            std_deviation = statistics.stdev(activity_values) if len(activity_values) > 1 else 0
            coefficient_of_variation = std_deviation / mean_activity
            
            # Convert to score (lower CV = higher consistency)
            consistency_score = max(0, 100 - (coefficient_of_variation * 100))
            return min(100, consistency_score)
            
        except Exception as e:
            self.logger.error(f"Error calculating consistency score: {e}")
            return 0.0
    
    async def _calculate_depth_score(self, events: List[EngagementEvent]) -> float:
        """Calculate engagement depth score based on event diversity and value."""        try:
            if not events:
                return 0.0
            
            # Calculate event type diversity
            event_types = {e.event_type for e in events}
            diversity_score = len(event_types) / len(EngagementEventType) * 100
            
            # Calculate average event value
            total_value = sum(e.get_event_value() for e in events)
            avg_value = total_value / len(events)
            value_score = min(100, avg_value * 10)  # Scale appropriately
            
            # Combine scores
            depth_score = (diversity_score * 0.6) + (value_score * 0.4)
            return min(100, depth_score)
            
        except Exception as e:
            self.logger.error(f"Error calculating depth score: {e}")
            return 0.0
    
    async def _calculate_churn_risk(self, user_id: str) -> float:
        """Calculate churn risk score for a user."""        try:
            now = datetime.utcnow()
            
            # Get recent activity
            week_ago = now - timedelta(days=7)
            month_ago = now - timedelta(days=30)
            
            recent_events = [
                e for e in self._events
                if e.user_id == user_id and e.timestamp >= month_ago and e.processed
            ]
            
            last_week_events = [e for e in recent_events if e.timestamp >= week_ago]
            
            # Risk factors
            risk_score = 0.0
            
            # Days since last activity
            if recent_events:
                last_activity = max(e.timestamp for e in recent_events)
                days_inactive = (now - last_activity).days
                risk_score += min(50, days_inactive * 5)  # Up to 50 points for 10+ days inactive
            else:
                risk_score += 50  # No recent activity
            
            # Declining activity trend
            if len(recent_events) >= 7:
                # Compare first week vs last week
                first_week_events = recent_events[:len(recent_events)//2]
                last_week_events = recent_events[len(recent_events)//2:]
                
                first_week_score = sum(e.get_event_value() for e in first_week_events)
                last_week_score = sum(e.get_event_value() for e in last_week_events)
                
                if first_week_score > 0:
                    decline_ratio = (first_week_score - last_week_score) / first_week_score
                    if decline_ratio > 0:
                        risk_score += min(30, decline_ratio * 100)  # Up to 30 points for declining activity
            
            # Low engagement diversity
            if recent_events:
                event_types = {e.event_type for e in recent_events}
                diversity_ratio = len(event_types) / len(EngagementEventType)
                if diversity_ratio < 0.3:
                    risk_score += 20  # Low diversity penalty
            
            return min(100, risk_score) / 100  # Normalize to 0-1
            
        except Exception as e:
            self.logger.error(f"Error calculating churn risk: {e}")
            return 0.5  # Default moderate risk
    
    async def _predict_lifetime_value(self, user_id: str, metrics: EngagementMetrics) -> float:
        """Predict user lifetime value based on engagement patterns."""        try:
            # Simple LTV prediction based on engagement metrics
            base_value = 100  # Base LTV
            
            # Engagement score factor
            engagement_factor = metrics.engagement_score / 100
            
            # Activity factor
            activity_factor = min(2.0, metrics.total_sessions / 10)  # Cap at 2x
            
            # Feature adoption factor
            adoption_factor = 1 + metrics.feature_adoption_rate
            
            # Consistency factor
            consistency_factor = 1 + (metrics.consistency_score / 100)
            
            # Gamification engagement factor
            gamification_factor = 1 + (
                (metrics.challenges_completed * 0.1) +
                (metrics.achievements_unlocked * 0.05) +
                (metrics.collaborations_participated * 0.2)
            )
            
            # Calculate predicted LTV
            predicted_ltv = (
                base_value *
                engagement_factor *
                activity_factor *
                adoption_factor *
                consistency_factor *
                gamification_factor
            )
            
            return min(1000, predicted_ltv)  # Cap at reasonable maximum
            
        except Exception as e:
            self.logger.error(f"Error predicting lifetime value: {e}")
            return 100  # Default value
    
    async def get_user_insights(
        self,
        user_id: str,
        limit: int = 10,
        priority_filter: Optional[str] = None
    ) -> List[EngagementInsight]:
        """Get actionable insights for a user."""        try:
            user_insights = self._insights.get(user_id, [])
            
            # Filter by priority if specified
            if priority_filter:
                user_insights = [i for i in user_insights if i.priority == priority_filter]
            
            # Filter out expired insights
            now = datetime.utcnow()
            active_insights = [
                i for i in user_insights
                if not i.expires_at or i.expires_at > now
            ]
            
            # Sort by priority and confidence
            priority_order = {"critical": 4, "high": 3, "medium": 2, "low": 1}
            active_insights.sort(
                key=lambda x: (priority_order.get(x.priority, 0), x.confidence),
                reverse=True
            )
            
            return active_insights[:limit]
            
        except Exception as e:
            self.logger.error(f"Error getting user insights: {e}")
            return []
    
    async def get_platform_analytics(
        self,
        period: AnalyticsPeriod = AnalyticsPeriod.DAILY,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get platform-wide engagement analytics."""        try:
            # Determine time period
            if not start_date:
                if period == AnalyticsPeriod.DAILY:
                    start_date = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
                elif period == AnalyticsPeriod.WEEKLY:
                    start_date = datetime.utcnow() - timedelta(days=7)
                elif period == AnalyticsPeriod.MONTHLY:
                    start_date = datetime.utcnow() - timedelta(days=30)
                else:
                    start_date = datetime.utcnow() - timedelta(days=1)
            
            if not end_date:
                end_date = datetime.utcnow()
            
            # Get events in period
            period_events = [
                e for e in self._events
                if start_date <= e.timestamp <= end_date and e.processed
            ]
            
            # Calculate platform metrics
            total_events = len(period_events)
            unique_users = len({e.user_id for e in period_events})
            
            # Events by type
            events_by_type = {}
            for event in period_events:
                event_type = event.event_type.value
                events_by_type[event_type] = events_by_type.get(event_type, 0) + 1
            
            # Calculate engagement rates
            content_events = sum(
                events_by_type.get(event_type, 0)
                for event_type in ["content_view", "content_like", "content_share", "content_comment"]
            )
            
            gamification_events = sum(
                events_by_type.get(event_type, 0)
                for event_type in ["challenge_joined", "challenge_completed", "achievement_unlocked"]
            )
            
            # Get top active users
            user_activity = {}
            for event in period_events:
                user_id = event.user_id
                if user_id not in user_activity:
                    user_activity[user_id] = 0
                user_activity[user_id] += event.get_event_value()
            
            top_users = sorted(user_activity.items(), key=lambda x: x[1], reverse=True)[:10]
            
            return {
                "period": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat(),
                    "type": period.value
                },
                "overview": {
                    "total_events": total_events,
                    "unique_active_users": unique_users,
                    "events_per_user": total_events / unique_users if unique_users > 0 else 0
                },
                "event_breakdown": events_by_type,
                "engagement_metrics": {
                    "content_engagement_events": content_events,
                    "gamification_engagement_events": gamification_events,
                    "content_engagement_rate": content_events / total_events if total_events > 0 else 0,
                    "gamification_engagement_rate": gamification_events / total_events if total_events > 0 else 0
                },
                "top_users": [
                    {"user_id": user_id, "activity_score": score}
                    for user_id, score in top_users
                ]
            }
            
        except Exception as e:
            self.logger.error(f"Error getting platform analytics: {e}")
            return {}


# Global engagement analytics instance
_engagement_analytics: Optional[EngagementAnalytics] = None


async def get_engagement_analytics() -> EngagementAnalytics:
    """Get the global engagement analytics instance."""    global _engagement_analytics
    
    if _engagement_analytics is None:
        _engagement_analytics = EngagementAnalytics()
    
    return _engagement_analytics


# Convenience functions for common operations
async def track_user_event(
    user_id: str,
    event_type: EngagementEventType,
    metadata: Optional[Dict[str, Any]] = None
) -> EngagementEvent:
    """Track a user engagement event (convenience function)."""    analytics = await get_engagement_analytics()
    return await analytics.track_event(user_id, event_type, metadata=metadata)


async def get_user_engagement_summary(user_id: str) -> Dict[str, Any]:
    """Get engagement summary for a user (convenience function)."""    analytics = await get_engagement_analytics()
    
    # Get daily, weekly, and monthly metrics
    daily_metrics = await analytics.calculate_user_metrics(user_id, AnalyticsPeriod.DAILY)
    weekly_metrics = await analytics.calculate_user_metrics(user_id, AnalyticsPeriod.WEEKLY)
    monthly_metrics = await analytics.calculate_user_metrics(user_id, AnalyticsPeriod.MONTHLY)
    
    # Get insights
    insights = await analytics.get_user_insights(user_id, limit=5)
    
    return {
        "user_id": user_id,
        "daily_metrics": {
            "engagement_score": daily_metrics.engagement_score,
            "total_events": daily_metrics.total_events,
            "session_count": daily_metrics.total_sessions,
            "feature_adoption_rate": daily_metrics.feature_adoption_rate
        },
        "weekly_metrics": {
            "engagement_score": weekly_metrics.engagement_score,
            "total_events": weekly_metrics.total_events,
            "momentum_score": weekly_metrics.engagement_momentum,
            "consistency_score": weekly_metrics.consistency_score
        },
        "monthly_metrics": {
            "engagement_score": monthly_metrics.engagement_score,
            "churn_risk": monthly_metrics.churn_risk_score,
            "predicted_ltv": monthly_metrics.lifetime_value_prediction
        },
        "insights": [
            {
                "type": insight.insight_type,
                "title": insight.title,
                "description": insight.description,
                "priority": insight.priority,
                "recommendations": insight.recommended_actions
            }
            for insight in insights
        ]
    }