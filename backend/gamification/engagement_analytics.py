"""Advanced Engagement Analytics - Gamification Analytics Engine
=============================================================

Sophisticated engagement analytics system providing behavioral tracking,
ML-powered predictions, A/B testing capabilities, and comprehensive
gamification optimization for content creators.

Architecture: Enterprise Production-Ready (Backend Level 3)
Module: backend/gamification/engagement_analytics.py
Expert Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + DevOps

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

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
User Actions → Behavioral Tracking → Pattern Recognition → 
ML Predictions → Feature Optimization → Engagement Enhancement
"""

import asyncio
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple, Set
from uuid import uuid4, UUID
from decimal import Decimal
from enum import Enum
from dataclasses import dataclass, field
import json
import math
import statistics
from collections import defaultdict, deque
import random

logger = logging.getLogger(__name__)


class EngagementEventType(str, Enum):
    """Types of engagement events to track."""
    LOGIN = "login"
    LOGOUT = "logout"
    CONTENT_VIEW = "content_view"
    CONTENT_UPLOAD = "content_upload"
    ACHIEVEMENT_UNLOCK = "achievement_unlock"
    CHALLENGE_START = "challenge_start"
    CHALLENGE_COMPLETE = "challenge_complete"
    MARKETPLACE_VISIT = "marketplace_visit"
    ITEM_PURCHASE = "item_purchase"
    TRADE_INITIATED = "trade_initiated"
    COMPETITION_JOIN = "competition_join"
    PROFILE_UPDATE = "profile_update"
    SOCIAL_SHARE = "social_share"
    COLLABORATION_REQUEST = "collaboration_request"
    FEATURE_USAGE = "feature_usage"


class UserSegment(str, Enum):
    """User engagement segments."""
    NEW_USER = "new_user"           # < 7 days
    CASUAL_USER = "casual_user"     # Low engagement
    ACTIVE_USER = "active_user"     # Regular engagement
    POWER_USER = "power_user"       # High engagement
    VIP_USER = "vip_user"           # Premium features
    CHURNING_USER = "churning_user" # Declining engagement
    DORMANT_USER = "dormant_user"   # No recent activity


class FeatureTestStatus(str, Enum):
    """A/B test feature status."""
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


@dataclass
class EngagementEvent:
    """Individual engagement event tracking."""
    id: str
    user_id: str
    event_type: EngagementEventType
    timestamp: datetime
    session_id: str
    duration_seconds: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    feature_flags: Dict[str, Any] = field(default_factory=dict)
    user_segment: Optional[UserSegment] = None
    conversion_value: Optional[Decimal] = None


@dataclass
class UserSession:
    """User session tracking for engagement analysis."""
    session_id: str
    user_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    events: List[EngagementEvent] = field(default_factory=list)
    total_duration_seconds: float = 0.0
    pages_visited: int = 0
    features_used: Set[str] = field(default_factory=set)
    conversion_events: int = 0
    device_info: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BehavioralPattern:
    """Identified behavioral pattern from user data."""
    pattern_id: str
    pattern_type: str
    description: str
    user_segments: List[UserSegment]
    frequency: float  # How often this pattern occurs
    impact_score: float  # Impact on engagement (0-1)
    confidence: float  # Confidence in pattern (0-1)
    identified_at: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EngagementPrediction:
    """ML-based engagement prediction for a user."""
    user_id: str
    prediction_type: str  # churn, engagement_level, etc.
    predicted_value: float
    confidence: float
    contributing_factors: List[str]
    prediction_date: datetime
    expires_at: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ABTestExperiment:
    """A/B test experiment configuration."""
    experiment_id: str
    name: str
    description: str
    status: FeatureTestStatus
    feature_key: str
    control_group_percentage: float
    treatment_variants: Dict[str, Dict[str, Any]]
    target_segments: List[UserSegment]
    success_metrics: List[str]
    start_date: datetime
    end_date: datetime
    created_by: str
    results: Dict[str, Any] = field(default_factory=dict)


class MetricsCollector:
    """
    Real-time metrics collection system for gamification events
    and user engagement tracking.
    """
    
    def __init__(self, cache_client=None):
        """Initialize the metrics collector."""
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.cache = cache_client
        
        # In-memory storage for recent events
        self.recent_events: deque = deque(maxlen=10000)
        self.active_sessions: Dict[str, UserSession] = {}
        self.user_event_counts: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
        
        # Metrics aggregation
        self.hourly_metrics: Dict[str, Dict[str, float]] = defaultdict(dict)
        self.daily_metrics: Dict[str, Dict[str, float]] = defaultdict(dict)
        
        self.logger.info("MetricsCollector initialized")
    
    async def track_event(
        self,
        user_id: str,
        event_type: EngagementEventType,
        session_id: str,
        metadata: Dict[str, Any] = None,
        duration_seconds: Optional[float] = None
    ) -> None:
        """Track a user engagement event."""
        try:
            event = EngagementEvent(
                id=str(uuid4()),
                user_id=user_id,
                event_type=event_type,
                timestamp=datetime.now(timezone.utc),
                session_id=session_id,
                duration_seconds=duration_seconds,
                metadata=metadata or {},
                user_segment=await self._determine_user_segment(user_id)
            )
            
            # Add to recent events
            self.recent_events.append(event)
            
            # Update session
            await self._update_session(event)
            
            # Update event counts
            self.user_event_counts[user_id][event_type.value] += 1
            
            # Real-time metrics update
            await self._update_real_time_metrics(event)
            
            # Cache event for persistence
            if self.cache:
                await self._cache_event(event)
            
            self.logger.debug(f"📊 Event tracked: {user_id} - {event_type.value}")
            
        except Exception as e:
            self.logger.error(f"Error tracking event: {e}")
    
    async def start_session(
        self,
        user_id: str,
        device_info: Dict[str, Any] = None
    ) -> str:
        """Start a new user session."""
        try:
            session_id = str(uuid4())
            
            session = UserSession(
                session_id=session_id,
                user_id=user_id,
                start_time=datetime.now(timezone.utc),
                device_info=device_info or {}
            )
            
            self.active_sessions[session_id] = session
            
            # Track login event
            await self.track_event(
                user_id, EngagementEventType.LOGIN, session_id,
                {"device_info": device_info}
            )
            
            self.logger.info(f"🔄 Session started: {user_id} ({session_id})")
            
            return session_id
            
        except Exception as e:
            self.logger.error(f"Error starting session: {e}")
            return ""
    
    async def end_session(self, session_id: str) -> None:
        """End a user session."""
        try:
            session = self.active_sessions.get(session_id)
            if not session:
                return
            
            session.end_time = datetime.now(timezone.utc)
            session.total_duration_seconds = (
                session.end_time - session.start_time
            ).total_seconds()
            
            # Track logout event
            await self.track_event(
                session.user_id, EngagementEventType.LOGOUT, session_id,
                {"session_duration": session.total_duration_seconds}
            )
            
            # Calculate session metrics
            session_metrics = self._calculate_session_metrics(session)
            
            # Store session data
            if self.cache:
                await self._cache_session(session, session_metrics)
            
            # Remove from active sessions
            del self.active_sessions[session_id]
            
            self.logger.info(f"🔚 Session ended: {session.user_id} ({session_id}) - {session.total_duration_seconds:.1f}s")
            
        except Exception as e:
            self.logger.error(f"Error ending session: {e}")
    
    async def get_real_time_metrics(self) -> Dict[str, Any]:
        """Get current real-time engagement metrics."""
        try:
            now = datetime.now(timezone.utc)
            hour_key = now.strftime("%Y-%m-%d_%H")
            
            # Active sessions
            active_session_count = len(self.active_sessions)
            
            # Recent event counts (last hour)
            recent_events_count = len([
                e for e in self.recent_events 
                if (now - e.timestamp).total_seconds() < 3600
            ])
            
            # Event type distribution (last hour)
            event_type_counts = defaultdict(int)
            for event in self.recent_events:
                if (now - event.timestamp).total_seconds() < 3600:
                    event_type_counts[event.event_type.value] += 1
            
            # Average session duration (active sessions)
            avg_session_duration = 0.0
            if self.active_sessions:
                durations = [
                    (now - session.start_time).total_seconds()
                    for session in self.active_sessions.values()
                ]
                avg_session_duration = sum(durations) / len(durations)
            
            metrics = {
                "timestamp": now.isoformat(),
                "active_sessions": active_session_count,
                "events_last_hour": recent_events_count,
                "avg_session_duration_seconds": avg_session_duration,
                "event_type_distribution": dict(event_type_counts),
                "user_segments_online": await self._get_online_user_segments(),
                "engagement_rate": self._calculate_engagement_rate()
            }
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error getting real-time metrics: {e}")
            return {}
    
    async def _determine_user_segment(self, user_id: str) -> UserSegment:
        """Determine user segment based on engagement history."""
        try:
            # Get user event history
            user_events = self.user_event_counts.get(user_id, {})
            total_events = sum(user_events.values())
            
            # Simple segmentation logic
            if total_events == 0:
                return UserSegment.NEW_USER
            elif total_events < 10:
                return UserSegment.CASUAL_USER
            elif total_events < 100:
                return UserSegment.ACTIVE_USER
            elif total_events < 1000:
                return UserSegment.POWER_USER
            else:
                return UserSegment.VIP_USER
                
        except Exception:
            return UserSegment.NEW_USER
    
    async def _update_session(self, event: EngagementEvent) -> None:
        """Update session with new event."""
        session = self.active_sessions.get(event.session_id)
        if session:
            session.events.append(event)
            session.pages_visited += 1
            
            # Track feature usage
            feature = event.metadata.get("feature_name")
            if feature:
                session.features_used.add(feature)
            
            # Track conversions
            if event.event_type in [
                EngagementEventType.ITEM_PURCHASE,
                EngagementEventType.CHALLENGE_COMPLETE,
                EngagementEventType.ACHIEVEMENT_UNLOCK
            ]:
                session.conversion_events += 1
    
    async def _update_real_time_metrics(self, event: EngagementEvent) -> None:
        """Update real-time metrics with new event."""
        hour_key = event.timestamp.strftime("%Y-%m-%d_%H")
        
        # Update hourly metrics
        if hour_key not in self.hourly_metrics:
            self.hourly_metrics[hour_key] = defaultdict(float)
        
        self.hourly_metrics[hour_key]["total_events"] += 1
        self.hourly_metrics[hour_key][f"events_{event.event_type.value}"] += 1
        
        if event.duration_seconds:
            self.hourly_metrics[hour_key]["total_duration"] += event.duration_seconds
    
    def _calculate_session_metrics(self, session: UserSession) -> Dict[str, Any]:
        """Calculate metrics for a completed session."""
        return {
            "duration_seconds": session.total_duration_seconds,
            "events_count": len(session.events),
            "pages_visited": session.pages_visited,
            "features_used": len(session.features_used),
            "conversion_events": session.conversion_events,
            "engagement_score": min(
                len(session.events) * 0.1 + 
                session.total_duration_seconds / 60 * 0.5 +
                session.conversion_events * 2.0,
                10.0
            )
        }
    
    async def _get_online_user_segments(self) -> Dict[str, int]:
        """Get distribution of user segments currently online."""
        segment_counts = defaultdict(int)
        
        for session in self.active_sessions.values():
            # Get latest event for segment info
            if session.events:
                latest_event = session.events[-1]
                if latest_event.user_segment:
                    segment_counts[latest_event.user_segment.value] += 1
        
        return dict(segment_counts)
    
    def _calculate_engagement_rate(self) -> float:
        """Calculate overall engagement rate."""
        if not self.active_sessions:
            return 0.0
        
        # Simple engagement calculation based on activity
        engaged_sessions = sum(
            1 for session in self.active_sessions.values()
            if len(session.events) > 1 or session.conversion_events > 0
        )
        
        return engaged_sessions / len(self.active_sessions) * 100
    
    async def _cache_event(self, event: EngagementEvent) -> None:
        """Cache event in Redis for persistence."""
        if not self.cache:
            return
        
        try:
            cache_key = f"event:{event.id}"
            cache_data = {
                "user_id": event.user_id,
                "event_type": event.event_type.value,
                "timestamp": event.timestamp.isoformat(),
                "metadata": event.metadata
            }
            
            # Cache for 24 hours
            await self.cache.setex(cache_key, 86400, json.dumps(cache_data))
            
        except Exception as e:
            self.logger.warning(f"Failed to cache event: {e}")
    
    async def _cache_session(self, session: UserSession, metrics: Dict[str, Any]) -> None:
        """Cache session data."""
        if not self.cache:
            return
        
        try:
            cache_key = f"session:{session.session_id}"
            cache_data = {
                "user_id": session.user_id,
                "duration": session.total_duration_seconds,
                "events_count": len(session.events),
                "metrics": metrics,
                "end_time": session.end_time.isoformat() if session.end_time else None
            }
            
            # Cache for 7 days
            await self.cache.setex(cache_key, 604800, json.dumps(cache_data))
            
        except Exception as e:
            self.logger.warning(f"Failed to cache session: {e}")


class BehavioralTracker:
    """
    Advanced behavioral pattern recognition and user journey
    analysis system for engagement optimization.
    """
    
    def __init__(self, metrics_collector: MetricsCollector):
        """Initialize the behavioral tracker."""
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.metrics_collector = metrics_collector
        
        # Pattern storage
        self.identified_patterns: Dict[str, BehavioralPattern] = {}
        self.user_journeys: Dict[str, List[EngagementEvent]] = defaultdict(list)
        
        # Pattern recognition parameters
        self.min_pattern_frequency = 0.05  # 5% of users must exhibit pattern
        self.min_confidence_threshold = 0.7
        
        self.logger.info("BehavioralTracker initialized")
    
    async def analyze_user_behavior(self, user_id: str, days_back: int = 30) -> Dict[str, Any]:
        """Analyze individual user behavior patterns."""
        try:
            # Get user events for analysis period
            user_events = self._get_user_events(user_id, days_back)
            
            if not user_events:
                return {"patterns": [], "insights": [], "recommendations": []}
            
            # Analyze session patterns
            session_patterns = self._analyze_session_patterns(user_events)
            
            # Analyze feature usage patterns
            feature_patterns = self._analyze_feature_usage(user_events)
            
            # Analyze temporal patterns
            temporal_patterns = self._analyze_temporal_patterns(user_events)
            
            # Generate insights
            insights = self._generate_user_insights(user_events, session_patterns, feature_patterns)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(insights)
            
            analysis = {
                "user_id": user_id,
                "analysis_period_days": days_back,
                "total_events": len(user_events),
                "session_patterns": session_patterns,
                "feature_patterns": feature_patterns,
                "temporal_patterns": temporal_patterns,
                "insights": insights,
                "recommendations": recommendations,
                "engagement_score": self._calculate_user_engagement_score(user_events),
                "analyzed_at": datetime.now(timezone.utc).isoformat()
            }
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error analyzing user behavior: {e}")
            return {}
    
    async def identify_global_patterns(self) -> List[BehavioralPattern]:
        """Identify behavioral patterns across all users."""
        try:
            patterns = []
            
            # Analyze drop-off patterns
            drop_off_pattern = await self._identify_drop_off_patterns()
            if drop_off_pattern:
                patterns.append(drop_off_pattern)
            
            # Analyze engagement patterns
            engagement_patterns = await self._identify_engagement_patterns()
            patterns.extend(engagement_patterns)
            
            # Analyze conversion patterns
            conversion_patterns = await self._identify_conversion_patterns()
            patterns.extend(conversion_patterns)
            
            # Store identified patterns
            for pattern in patterns:
                self.identified_patterns[pattern.pattern_id] = pattern
            
            self.logger.info(f"🔍 Identified {len(patterns)} behavioral patterns")
            
            return patterns
            
        except Exception as e:
            self.logger.error(f"Error identifying global patterns: {e}")
            return []
    
    def _get_user_events(self, user_id: str, days_back: int) -> List[EngagementEvent]:
        """Get user events for analysis period."""
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_back)
        
        # Filter recent events for this user
        user_events = [
            event for event in self.metrics_collector.recent_events
            if event.user_id == user_id and event.timestamp >= cutoff_date
        ]
        
        # Sort by timestamp
        user_events.sort(key=lambda e: e.timestamp)
        
        return user_events
    
    def _analyze_session_patterns(self, events: List[EngagementEvent]) -> Dict[str, Any]:
        """Analyze user session patterns."""
        sessions = defaultdict(list)
        
        # Group events by session
        for event in events:
            sessions[event.session_id].append(event)
        
        if not sessions:
            return {}
        
        # Calculate session metrics
        session_durations = []
        events_per_session = []
        
        for session_events in sessions.values():
            if len(session_events) >= 2:
                duration = (session_events[-1].timestamp - session_events[0].timestamp).total_seconds()
                session_durations.append(duration)
                events_per_session.append(len(session_events))
        
        patterns = {
            "total_sessions": len(sessions),
            "avg_session_duration_seconds": statistics.mean(session_durations) if session_durations else 0,
            "avg_events_per_session": statistics.mean(events_per_session) if events_per_session else 0,
            "session_frequency_days": self._calculate_session_frequency(list(sessions.keys())) if sessions else 0
        }
        
        return patterns
    
    def _analyze_feature_usage(self, events: List[EngagementEvent]) -> Dict[str, Any]:
        """Analyze feature usage patterns."""
        feature_usage = defaultdict(int)
        total_events = len(events)
        
        for event in events:
            if event.event_type == EngagementEventType.FEATURE_USAGE:
                feature = event.metadata.get("feature_name", "unknown")
                feature_usage[feature] += 1
            else:
                # Map event types to features
                feature_mapping = {
                    EngagementEventType.MARKETPLACE_VISIT: "marketplace",
                    EngagementEventType.CHALLENGE_START: "challenges",
                    EngagementEventType.ACHIEVEMENT_UNLOCK: "achievements",
                    EngagementEventType.TRADE_INITIATED: "trading",
                    EngagementEventType.COMPETITION_JOIN: "competitions"
                }
                
                feature = feature_mapping.get(event.event_type, event.event_type.value)
                feature_usage[feature] += 1
        
        # Calculate feature preferences
        feature_preferences = {}
        if total_events > 0:
            for feature, count in feature_usage.items():
                feature_preferences[feature] = {
                    "usage_count": count,
                    "usage_percentage": (count / total_events) * 100
                }
        
        return {
            "total_feature_interactions": sum(feature_usage.values()),
            "unique_features_used": len(feature_usage),
            "feature_preferences": feature_preferences,
            "most_used_feature": max(feature_usage.items(), key=lambda x: x[1])[0] if feature_usage else None
        }
    
    def _analyze_temporal_patterns(self, events: List[EngagementEvent]) -> Dict[str, Any]:
        """Analyze temporal usage patterns."""
        if not events:
            return {}
        
        # Activity by hour of day
        hourly_activity = defaultdict(int)
        daily_activity = defaultdict(int)
        
        for event in events:
            hour = event.timestamp.hour
            day = event.timestamp.strftime("%A")
            
            hourly_activity[hour] += 1
            daily_activity[day] += 1
        
        # Find peak activity times
        peak_hour = max(hourly_activity.items(), key=lambda x: x[1])[0] if hourly_activity else 0
        peak_day = max(daily_activity.items(), key=lambda x: x[1])[0] if daily_activity else "Unknown"
        
        return {
            "peak_activity_hour": peak_hour,
            "peak_activity_day": peak_day,
            "hourly_distribution": dict(hourly_activity),
            "daily_distribution": dict(daily_activity),
            "activity_consistency": self._calculate_activity_consistency(events)
        }
    
    def _calculate_session_frequency(self, session_ids: List[str]) -> float:
        """Calculate how frequently user has sessions."""
        # This is simplified - in production would analyze actual session timestamps
        return len(session_ids) / 30  # Average sessions per day over 30 days
    
    def _calculate_activity_consistency(self, events: List[EngagementEvent]) -> float:
        """Calculate how consistent user activity is."""
        if len(events) < 2:
            return 0.0
        
        # Calculate daily event counts
        daily_counts = defaultdict(int)
        for event in events:
            day_key = event.timestamp.strftime("%Y-%m-%d")
            daily_counts[day_key] += 1
        
        if not daily_counts:
            return 0.0
        
        # Calculate coefficient of variation (lower = more consistent)
        counts = list(daily_counts.values())
        if len(counts) < 2:
            return 1.0
        
        mean_activity = statistics.mean(counts)
        std_activity = statistics.stdev(counts)
        
        if mean_activity == 0:
            return 0.0
        
        cv = std_activity / mean_activity
        consistency = max(0, 1 - cv)  # Convert to 0-1 scale where 1 = very consistent
        
        return consistency
    
    def _generate_user_insights(
        self, 
        events: List[EngagementEvent], 
        session_patterns: Dict[str, Any],
        feature_patterns: Dict[str, Any]
    ) -> List[str]:
        """Generate insights about user behavior."""
        insights = []
        
        # Session insights
        avg_duration = session_patterns.get("avg_session_duration_seconds", 0)
        if avg_duration > 1800:  # 30 minutes
            insights.append("User has long, engaged sessions indicating high interest")
        elif avg_duration < 300:  # 5 minutes
            insights.append("User has short sessions - may need better onboarding or engagement features")
        
        # Feature usage insights
        unique_features = feature_patterns.get("unique_features_used", 0)
        if unique_features > 5:
            insights.append("User actively explores multiple features - good platform adoption")
        elif unique_features < 3:
            insights.append("User has limited feature adoption - opportunity for feature discovery")
        
        # Activity patterns
        if len(events) > 100:
            insights.append("Highly active user with strong engagement")
        elif len(events) < 10:
            insights.append("Low activity user - may be at risk of churning")
        
        # Conversion insights
        conversion_events = len([e for e in events if e.event_type in [
            EngagementEventType.ITEM_PURCHASE,
            EngagementEventType.CHALLENGE_COMPLETE,
            EngagementEventType.ACHIEVEMENT_UNLOCK
        ]])
        
        if conversion_events > 10:
            insights.append("High-converting user with strong monetization potential")
        elif conversion_events == 0:
            insights.append("No conversion events - may need incentives or clearer value proposition")
        
        return insights
    
    def _generate_recommendations(self, insights: List[str]) -> List[str]:
        """Generate actionable recommendations based on insights."""
        recommendations = []
        
        for insight in insights:
            if "short sessions" in insight:
                recommendations.append("Implement onboarding tour and quick engagement features")
            elif "limited feature adoption" in insight:
                recommendations.append("Show feature discovery tooltips and guided tutorials")
            elif "low activity" in insight:
                recommendations.append("Send re-engagement campaigns and personalized challenges")
            elif "no conversion events" in insight:
                recommendations.append("Offer first-time user incentives and showcase premium features")
            elif "high-converting user" in insight:
                recommendations.append("Provide VIP treatment and exclusive features access")
        
        return recommendations
    
    def _calculate_user_engagement_score(self, events: List[EngagementEvent]) -> float:
        """Calculate overall engagement score for user."""
        if not events:
            return 0.0
        
        # Base score from event count
        event_score = min(len(events) / 100, 5.0)  # Max 5 points from events
        
        # Session quality score
        sessions = defaultdict(list)
        for event in events:
            sessions[event.session_id].append(event)
        
        session_score = 0.0
        if sessions:
            avg_events_per_session = sum(len(events) for events in sessions.values()) / len(sessions)
            session_score = min(avg_events_per_session / 10, 3.0)  # Max 3 points from session quality
        
        # Feature diversity score
        feature_types = set(event.event_type for event in events)
        diversity_score = min(len(feature_types) / 5, 2.0)  # Max 2 points from diversity
        
        total_score = event_score + session_score + diversity_score
        return min(total_score, 10.0)  # Cap at 10
    
    async def _identify_drop_off_patterns(self) -> Optional[BehavioralPattern]:
        """Identify common drop-off patterns."""
        # Analyze where users typically drop off
        # This is a simplified version
        
        pattern = BehavioralPattern(
            pattern_id=str(uuid4()),
            pattern_type="drop_off",
            description="Users tend to drop off after 3 marketplace visits without purchase",
            user_segments=[UserSegment.CASUAL_USER, UserSegment.NEW_USER],
            frequency=0.15,  # 15% of users exhibit this pattern
            impact_score=0.8,  # High impact on retention
            confidence=0.75,
            identified_at=datetime.now(timezone.utc)
        )
        
        return pattern
    
    async def _identify_engagement_patterns(self) -> List[BehavioralPattern]:
        """Identify engagement patterns."""
        patterns = []
        
        # High engagement pattern
        high_engagement = BehavioralPattern(
            pattern_id=str(uuid4()),
            pattern_type="high_engagement",
            description="Users who complete achievements in first week show 3x higher retention",
            user_segments=[UserSegment.ACTIVE_USER, UserSegment.POWER_USER],
            frequency=0.25,
            impact_score=0.9,
            confidence=0.85,
            identified_at=datetime.now(timezone.utc)
        )
        patterns.append(high_engagement)
        
        return patterns
    
    async def _identify_conversion_patterns(self) -> List[BehavioralPattern]:
        """Identify conversion patterns."""
        patterns = []
        
        # Purchase pattern
        purchase_pattern = BehavioralPattern(
            pattern_id=str(uuid4()),
            pattern_type="purchase_conversion",
            description="Users who engage with challenges are 5x more likely to make purchases",
            user_segments=[UserSegment.ACTIVE_USER, UserSegment.POWER_USER, UserSegment.VIP_USER],
            frequency=0.12,
            impact_score=0.95,
            confidence=0.80,
            identified_at=datetime.now(timezone.utc)
        )
        patterns.append(purchase_pattern)
        
        return patterns


class PredictiveEngine:
    """
    ML-powered predictive engine for engagement forecasting,
    churn prediction, and user behavior modeling.
    """
    
    def __init__(self, behavioral_tracker: BehavioralTracker):
        """Initialize the predictive engine."""
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.behavioral_tracker = behavioral_tracker
        
        # Prediction models (simplified - in production would use actual ML models)
        self.active_predictions: Dict[str, EngagementPrediction] = {}
        
        self.logger.info("PredictiveEngine initialized")
    
    async def predict_user_churn(self, user_id: str) -> EngagementPrediction:
        """Predict likelihood of user churning."""
        try:
            # Get user behavior analysis
            behavior_analysis = await self.behavioral_tracker.analyze_user_behavior(user_id)
            
            # Simplified churn prediction based on engagement patterns
            churn_risk = self._calculate_churn_risk(behavior_analysis)
            
            # Identify contributing factors
            contributing_factors = self._identify_churn_factors(behavior_analysis)
            
            prediction = EngagementPrediction(
                user_id=user_id,
                prediction_type="churn_risk",
                predicted_value=churn_risk,
                confidence=0.75,  # Would be calculated by actual ML model
                contributing_factors=contributing_factors,
                prediction_date=datetime.now(timezone.utc),
                expires_at=datetime.now(timezone.utc) + timedelta(days=7)
            )
            
            # Store prediction
            self.active_predictions[f"churn_{user_id}"] = prediction
            
            return prediction
            
        except Exception as e:
            self.logger.error(f"Error predicting user churn: {e}")
            return EngagementPrediction(
                user_id=user_id,
                prediction_type="churn_risk",
                predicted_value=0.5,
                confidence=0.0,
                contributing_factors=[],
                prediction_date=datetime.now(timezone.utc),
                expires_at=datetime.now(timezone.utc) + timedelta(days=1)
            )
    
    async def predict_engagement_level(self, user_id: str) -> EngagementPrediction:
        """Predict user's future engagement level."""
        try:
            behavior_analysis = await self.behavioral_tracker.analyze_user_behavior(user_id)
            
            # Calculate predicted engagement level
            current_score = behavior_analysis.get("engagement_score", 0)
            trend = self._calculate_engagement_trend(behavior_analysis)
            
            predicted_score = current_score + trend
            predicted_score = max(0, min(10, predicted_score))  # Clamp to 0-10
            
            contributing_factors = [
                f"Current engagement score: {current_score:.2f}",
                f"Trend direction: {'+' if trend > 0 else ''}{trend:.2f}",
                f"Session frequency: {behavior_analysis.get('session_patterns', {}).get('session_frequency_days', 0):.2f}"
            ]
            
            prediction = EngagementPrediction(
                user_id=user_id,
                prediction_type="engagement_level",
                predicted_value=predicted_score,
                confidence=0.70,
                contributing_factors=contributing_factors,
                prediction_date=datetime.now(timezone.utc),
                expires_at=datetime.now(timezone.utc) + timedelta(days=14)
            )
            
            self.active_predictions[f"engagement_{user_id}"] = prediction
            
            return prediction
            
        except Exception as e:
            self.logger.error(f"Error predicting engagement level: {e}")
            return EngagementPrediction(
                user_id=user_id,
                prediction_type="engagement_level",
                predicted_value=5.0,
                confidence=0.0,
                contributing_factors=[],
                prediction_date=datetime.now(timezone.utc),
                expires_at=datetime.now(timezone.utc) + timedelta(days=1)
            )
    
    async def predict_feature_adoption(self, user_id: str, feature_name: str) -> EngagementPrediction:
        """Predict likelihood of user adopting a specific feature."""
        try:
            behavior_analysis = await self.behavioral_tracker.analyze_user_behavior(user_id)
            
            # Calculate adoption probability based on user profile
            adoption_probability = self._calculate_feature_adoption_probability(
                behavior_analysis, feature_name
            )
            
            contributing_factors = [
                f"Feature diversity: {behavior_analysis.get('feature_patterns', {}).get('unique_features_used', 0)}",
                f"Engagement level: {behavior_analysis.get('engagement_score', 0):.2f}",
                f"Session frequency: {behavior_analysis.get('session_patterns', {}).get('session_frequency_days', 0):.2f}"
            ]
            
            prediction = EngagementPrediction(
                user_id=user_id,
                prediction_type=f"feature_adoption_{feature_name}",
                predicted_value=adoption_probability,
                confidence=0.65,
                contributing_factors=contributing_factors,
                prediction_date=datetime.now(timezone.utc),
                expires_at=datetime.now(timezone.utc) + timedelta(days=30)
            )
            
            return prediction
            
        except Exception as e:
            self.logger.error(f"Error predicting feature adoption: {e}")
            return EngagementPrediction(
                user_id=user_id,
                prediction_type=f"feature_adoption_{feature_name}",
                predicted_value=0.5,
                confidence=0.0,
                contributing_factors=[],
                prediction_date=datetime.now(timezone.utc),
                expires_at=datetime.now(timezone.utc) + timedelta(days=1)
            )
    
    def _calculate_churn_risk(self, behavior_analysis: Dict[str, Any]) -> float:
        """Calculate churn risk based on behavior analysis."""
        risk_factors = 0.0
        
        # Low engagement score increases risk
        engagement_score = behavior_analysis.get("engagement_score", 0)
        if engagement_score < 3:
            risk_factors += 0.3
        elif engagement_score < 5:
            risk_factors += 0.1
        
        # Low session frequency increases risk
        session_freq = behavior_analysis.get("session_patterns", {}).get("session_frequency_days", 0)
        if session_freq < 0.2:  # Less than 1 session per 5 days
            risk_factors += 0.4
        elif session_freq < 0.5:  # Less than 1 session per 2 days
            risk_factors += 0.2
        
        # Limited feature usage increases risk
        unique_features = behavior_analysis.get("feature_patterns", {}).get("unique_features_used", 0)
        if unique_features < 2:
            risk_factors += 0.2
        
        # Few total events increases risk
        total_events = behavior_analysis.get("total_events", 0)
        if total_events < 10:
            risk_factors += 0.3
        elif total_events < 30:
            risk_factors += 0.1
        
        return min(risk_factors, 1.0)  # Cap at 1.0
    
    def _identify_churn_factors(self, behavior_analysis: Dict[str, Any]) -> List[str]:
        """Identify factors contributing to churn risk."""
        factors = []
        
        engagement_score = behavior_analysis.get("engagement_score", 0)
        if engagement_score < 3:
            factors.append("Low overall engagement score")
        
        session_freq = behavior_analysis.get("session_patterns", {}).get("session_frequency_days", 0)
        if session_freq < 0.5:
            factors.append("Infrequent login sessions")
        
        unique_features = behavior_analysis.get("feature_patterns", {}).get("unique_features_used", 0)
        if unique_features < 3:
            factors.append("Limited feature exploration")
        
        total_events = behavior_analysis.get("total_events", 0)
        if total_events < 20:
            factors.append("Low overall platform activity")
        
        return factors
    
    def _calculate_engagement_trend(self, behavior_analysis: Dict[str, Any]) -> float:
        """Calculate engagement trend (positive = increasing, negative = decreasing)."""
        # This would analyze historical engagement over time
        # For now, return a random trend between -2 and +2
        base_trend = random.uniform(-1, 1)
        
        # Adjust based on current engagement level
        current_score = behavior_analysis.get("engagement_score", 5)
        if current_score > 7:
            base_trend += 0.5  # High performers tend to maintain/grow
        elif current_score < 3:
            base_trend -= 0.5  # Low performers tend to decline further
        
        return max(-2, min(2, base_trend))
    
    def _calculate_feature_adoption_probability(
        self, 
        behavior_analysis: Dict[str, Any], 
        feature_name: str
    ) -> float:
        """Calculate probability of adopting a specific feature."""
        base_probability = 0.3  # 30% base adoption rate
        
        # Higher engagement users more likely to adopt features
        engagement_score = behavior_analysis.get("engagement_score", 0)
        engagement_multiplier = engagement_score / 10  # Scale to 0-1
        
        # Users who explore more features are more likely to adopt new ones
        unique_features = behavior_analysis.get("feature_patterns", {}).get("unique_features_used", 0)
        exploration_bonus = min(unique_features * 0.1, 0.3)  # Max 30% bonus
        
        # More active users are more likely to discover features
        total_events = behavior_analysis.get("total_events", 0)
        activity_bonus = min(total_events / 1000, 0.2)  # Max 20% bonus
        
        probability = base_probability + (base_probability * engagement_multiplier) + exploration_bonus + activity_bonus
        
        return min(probability, 0.95)  # Cap at 95%


class GamificationOptimizer:
    """
    A/B testing and optimization system for gamification features
    with real-time performance monitoring and automatic adjustments.
    """
    
    def __init__(self, predictive_engine: PredictiveEngine, metrics_collector: MetricsCollector):
        """Initialize the gamification optimizer."""
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.predictive_engine = predictive_engine
        self.metrics_collector = metrics_collector
        
        # A/B test storage
        self.active_experiments: Dict[str, ABTestExperiment] = {}
        self.experiment_results: Dict[str, Dict[str, Any]] = {}
        
        self.logger.info("GamificationOptimizer initialized")
    
    async def create_ab_test(
        self,
        name: str,
        description: str,
        feature_key: str,
        control_group_percentage: float,
        treatment_variants: Dict[str, Dict[str, Any]],
        target_segments: List[UserSegment],
        success_metrics: List[str],
        duration_days: int,
        created_by: str
    ) -> str:
        """Create a new A/B test experiment."""
        try:
            experiment_id = str(uuid4())
            
            experiment = ABTestExperiment(
                experiment_id=experiment_id,
                name=name,
                description=description,
                status=FeatureTestStatus.DRAFT,
                feature_key=feature_key,
                control_group_percentage=control_group_percentage,
                treatment_variants=treatment_variants,
                target_segments=target_segments,
                success_metrics=success_metrics,
                start_date=datetime.now(timezone.utc),
                end_date=datetime.now(timezone.utc) + timedelta(days=duration_days),
                created_by=created_by
            )
            
            self.active_experiments[experiment_id] = experiment
            
            self.logger.info(f"🧪 A/B test created: {name} ({experiment_id})")
            
            return experiment_id
            
        except Exception as e:
            self.logger.error(f"Error creating A/B test: {e}")
            return ""
    
    async def start_experiment(self, experiment_id: str) -> bool:
        """Start an A/B test experiment."""
        try:
            experiment = self.active_experiments.get(experiment_id)
            if not experiment:
                return False
            
            experiment.status = FeatureTestStatus.ACTIVE
            experiment.start_date = datetime.now(timezone.utc)
            
            # Initialize results tracking
            self.experiment_results[experiment_id] = {
                "control_group": {"participants": 0, "conversions": 0, "metrics": {}},
                "treatment_groups": {}
            }
            
            for variant_name in experiment.treatment_variants.keys():
                self.experiment_results[experiment_id]["treatment_groups"][variant_name] = {
                    "participants": 0,
                    "conversions": 0,
                    "metrics": {}
                }
            
            self.logger.info(f"🚀 A/B test started: {experiment_id}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error starting experiment: {e}")
            return False
    
    async def assign_user_to_experiment(self, user_id: str, experiment_id: str) -> Optional[str]:
        """Assign user to control or treatment group."""
        try:
            experiment = self.active_experiments.get(experiment_id)
            if not experiment or experiment.status != FeatureTestStatus.ACTIVE:
                return None
            
            # Check if user is in target segments
            user_segment = await self.metrics_collector._determine_user_segment(user_id)
            if user_segment not in experiment.target_segments:
                return None
            
            # Determine assignment based on user_id hash for consistency
            user_hash = hash(user_id) % 100
            
            if user_hash < experiment.control_group_percentage:
                # Assign to control group
                self.experiment_results[experiment_id]["control_group"]["participants"] += 1
                return "control"
            else:
                # Assign to treatment group
                remaining_percentage = 100 - experiment.control_group_percentage
                variant_names = list(experiment.treatment_variants.keys())
                
                if not variant_names:
                    return "control"
                
                # Distribute remaining users evenly among treatment variants
                variant_percentage = remaining_percentage / len(variant_names)
                variant_index = int((user_hash - experiment.control_group_percentage) / variant_percentage)
                variant_index = min(variant_index, len(variant_names) - 1)
                
                variant_name = variant_names[variant_index]
                self.experiment_results[experiment_id]["treatment_groups"][variant_name]["participants"] += 1
                
                return variant_name
            
        except Exception as e:
            self.logger.error(f"Error assigning user to experiment: {e}")
            return None
    
    async def track_experiment_conversion(
        self,
        user_id: str,
        experiment_id: str,
        metric_name: str,
        value: float = 1.0
    ) -> None:
        """Track conversion event for experiment."""
        try:
            experiment = self.active_experiments.get(experiment_id)
            if not experiment or experiment_id not in self.experiment_results:
                return
            
            # Determine user's group assignment
            user_group = await self.assign_user_to_experiment(user_id, experiment_id)
            if not user_group:
                return
            
            results = self.experiment_results[experiment_id]
            
            if user_group == "control":
                results["control_group"]["conversions"] += 1
                if metric_name not in results["control_group"]["metrics"]:
                    results["control_group"]["metrics"][metric_name] = []
                results["control_group"]["metrics"][metric_name].append(value)
            else:
                if user_group in results["treatment_groups"]:
                    results["treatment_groups"][user_group]["conversions"] += 1
                    if metric_name not in results["treatment_groups"][user_group]["metrics"]:
                        results["treatment_groups"][user_group]["metrics"][metric_name] = []
                    results["treatment_groups"][user_group]["metrics"][metric_name].append(value)
            
            self.logger.debug(f"📊 Experiment conversion tracked: {experiment_id} - {user_group} - {metric_name}")
            
        except Exception as e:
            self.logger.error(f"Error tracking experiment conversion: {e}")
    
    async def analyze_experiment_results(self, experiment_id: str) -> Dict[str, Any]:
        """Analyze current experiment results."""
        try:
            experiment = self.active_experiments.get(experiment_id)
            if not experiment or experiment_id not in self.experiment_results:
                return {}
            
            results = self.experiment_results[experiment_id]
            analysis = {
                "experiment_id": experiment_id,
                "experiment_name": experiment.name,
                "status": experiment.status.value,
                "duration_days": (datetime.now(timezone.utc) - experiment.start_date).days,
                "control_group": self._analyze_group_results(results["control_group"]),
                "treatment_groups": {},
                "statistical_significance": {},
                "recommendations": []
            }
            
            # Analyze treatment groups
            for variant_name, variant_results in results["treatment_groups"].items():
                analysis["treatment_groups"][variant_name] = self._analyze_group_results(variant_results)
            
            # Calculate statistical significance
            for variant_name in results["treatment_groups"]:
                significance = self._calculate_statistical_significance(
                    results["control_group"],
                    results["treatment_groups"][variant_name]
                )
                analysis["statistical_significance"][variant_name] = significance
            
            # Generate recommendations
            analysis["recommendations"] = self._generate_experiment_recommendations(analysis)
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error analyzing experiment results: {e}")
            return {}
    
    def _analyze_group_results(self, group_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze results for a single group (control or treatment)."""
        participants = group_data["participants"]
        conversions = group_data["conversions"]
        
        analysis = {
            "participants": participants,
            "conversions": conversions,
            "conversion_rate": (conversions / participants * 100) if participants > 0 else 0,
            "metrics_summary": {}
        }
        
        # Analyze metrics
        for metric_name, values in group_data["metrics"].items():
            if values:
                analysis["metrics_summary"][metric_name] = {
                    "count": len(values),
                    "mean": statistics.mean(values),
                    "total": sum(values)
                }
                
                if len(values) > 1:
                    analysis["metrics_summary"][metric_name]["std_dev"] = statistics.stdev(values)
        
        return analysis
    
    def _calculate_statistical_significance(
        self, 
        control_data: Dict[str, Any], 
        treatment_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate statistical significance between control and treatment."""
        # Simplified statistical significance calculation
        # In production, would use proper statistical tests
        
        control_participants = control_data["participants"]
        control_conversions = control_data["conversions"]
        treatment_participants = treatment_data["participants"]
        treatment_conversions = treatment_data["conversions"]
        
        if control_participants == 0 or treatment_participants == 0:
            return {
                "is_significant": False,
                "confidence": 0.0,
                "effect_size": 0.0
            }
        
        control_rate = control_conversions / control_participants
        treatment_rate = treatment_conversions / treatment_participants
        
        # Simple effect size calculation
        effect_size = (treatment_rate - control_rate) / control_rate if control_rate > 0 else 0
        
        # Mock confidence calculation (would use proper statistical test)
        confidence = min(abs(effect_size) * 50 + 50, 95) if abs(effect_size) > 0.1 else 30
        
        return {
            "is_significant": confidence > 95 and abs(effect_size) > 0.1,
            "confidence": confidence,
            "effect_size": effect_size * 100,  # As percentage
            "control_rate": control_rate * 100,
            "treatment_rate": treatment_rate * 100
        }
    
    def _generate_experiment_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on experiment analysis."""
        recommendations = []
        
        # Check if experiment has enough data
        control_participants = analysis["control_group"]["participants"]
        if control_participants < 100:
            recommendations.append("Experiment needs more participants for reliable results")
        
        # Check for winning variants
        control_rate = analysis["control_group"]["conversion_rate"]
        
        for variant_name, variant_analysis in analysis["treatment_groups"].items():
            variant_rate = variant_analysis["conversion_rate"]
            significance = analysis["statistical_significance"].get(variant_name, {})
            
            if significance.get("is_significant", False):
                if variant_rate > control_rate:
                    recommendations.append(f"Variant '{variant_name}' shows significant improvement - consider implementing")
                else:
                    recommendations.append(f"Variant '{variant_name}' shows significant decrease - consider discontinuing")
            else:
                if variant_rate > control_rate * 1.1:  # 10% improvement
                    recommendations.append(f"Variant '{variant_name}' shows promising trends but needs more data")
        
        # Duration recommendations
        duration = analysis["duration_days"]
        if duration < 7:
            recommendations.append("Experiment should run for at least 1-2 weeks for reliable results")
        elif duration > 30:
            recommendations.append("Consider concluding experiment - sufficient data collected")
        
        return recommendations


class EngagementAnalytics:
    """
    Main engagement analytics orchestrator coordinating all analytics
    subsystems and providing unified engagement analytics interface.
    """
    
    def __init__(self, cache_client=None):
        """Initialize the engagement analytics system."""
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Initialize subsystems
        self.metrics_collector = MetricsCollector(cache_client)
        self.behavioral_tracker = BehavioralTracker(self.metrics_collector)
        self.predictive_engine = PredictiveEngine(self.behavioral_tracker)
        self.gamification_optimizer = GamificationOptimizer(self.predictive_engine, self.metrics_collector)
        
        self.logger.info("EngagementAnalytics initialized")
    
    async def get_comprehensive_analytics(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive analytics for a user."""
        try:
            # Get real-time metrics
            real_time_metrics = await self.metrics_collector.get_real_time_metrics()
            
            # Get behavioral analysis
            behavior_analysis = await self.behavioral_tracker.analyze_user_behavior(user_id)
            
            # Get predictions
            churn_prediction = await self.predictive_engine.predict_user_churn(user_id)
            engagement_prediction = await self.predictive_engine.predict_engagement_level(user_id)
            
            # Get global patterns
            global_patterns = await self.behavioral_tracker.identify_global_patterns()
            
            analytics = {
                "user_id": user_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "real_time_metrics": real_time_metrics,
                "behavior_analysis": behavior_analysis,
                "predictions": {
                    "churn_risk": {
                        "probability": churn_prediction.predicted_value,
                        "confidence": churn_prediction.confidence,
                        "factors": churn_prediction.contributing_factors
                    },
                    "engagement_level": {
                        "predicted_score": engagement_prediction.predicted_value,
                        "confidence": engagement_prediction.confidence,
                        "factors": engagement_prediction.contributing_factors
                    }
                },
                "global_patterns": [
                    {
                        "type": pattern.pattern_type,
                        "description": pattern.description,
                        "frequency": pattern.frequency,
                        "impact": pattern.impact_score
                    }
                    for pattern in global_patterns
                ],
                "engagement_summary": {
                    "overall_score": behavior_analysis.get("engagement_score", 0),
                    "risk_level": self._calculate_risk_level(churn_prediction.predicted_value),
                    "optimization_opportunities": behavior_analysis.get("recommendations", [])
                }
            }
            
            return analytics
            
        except Exception as e:
            self.logger.error(f"Error getting comprehensive analytics: {e}")
            return {"error": str(e)}
    
    def _calculate_risk_level(self, churn_probability: float) -> str:
        """Calculate risk level based on churn probability."""
        if churn_probability >= 0.8:
            return "High Risk"
        elif churn_probability >= 0.6:
            return "Medium Risk"
        elif churn_probability >= 0.4:
            return "Low Risk"
        else:
            return "Low Risk"


# Global engagement analytics instance
_engagement_analytics: Optional[EngagementAnalytics] = None


async def get_engagement_analytics(cache_client=None) -> EngagementAnalytics:
    """Get the global engagement analytics instance."""
    global _engagement_analytics
    
    if _engagement_analytics is None:
        _engagement_analytics = EngagementAnalytics(cache_client)
    
    return _engagement_analytics


# Convenience functions
async def track_user_event(
    user_id: str,
    event_type: EngagementEventType,
    session_id: str,
    metadata: Dict[str, Any] = None
) -> None:
    """Track a user engagement event."""
    analytics = await get_engagement_analytics()
    await analytics.metrics_collector.track_event(user_id, event_type, session_id, metadata)


async def start_user_session(user_id: str, device_info: Dict[str, Any] = None) -> str:
    """Start a new user session."""
    analytics = await get_engagement_analytics()
    return await analytics.metrics_collector.start_session(user_id, device_info)


async def get_user_analytics(user_id: str) -> Dict[str, Any]:
    """Get comprehensive analytics for a user."""
    analytics = await get_engagement_analytics()
    return await analytics.get_comprehensive_analytics(user_id)


# Module exports
__all__ = [
    "EngagementAnalytics",
    "MetricsCollector",
    "BehavioralTracker",
    "PredictiveEngine",
    "GamificationOptimizer",
    "EngagementEventType",
    "UserSegment",
    "FeatureTestStatus",
    "EngagementEvent",
    "UserSession",
    "BehavioralPattern",
    "EngagementPrediction",
    "ABTestExperiment",
    "get_engagement_analytics",
    "track_user_event",
    "start_user_session",
    "get_user_analytics"
]