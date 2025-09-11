"""Engagement Analytics Engine
User engagement tracking and behavioral analysis for multimedia content.

This module provides comprehensive engagement tracking including user interactions,
content performance metrics, engagement prediction, and behavioral insights.

Author: Fahed Mlaiel <mlaiel@live.de>
Project Team: Lead AI Developer + Backend Senior Engineer + ML Engineer + 
              Database Administrator + Security Expert + Microservices Architect +
              Multimedia Processing Specialist + DevOps Engineer + AI Prompt Engineer

⚠️ COPYRIGHT PROTECTION ⚠️
This code is proprietary and confidential. Unauthorized use is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.
"""

import logging
import numpy as np
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import asyncio
from enum import Enum
import uuid
from collections import defaultdict, deque

logger = logging.getLogger(__name__)

class EngagementType(Enum):
    """Types of engagement interactions"""
    VIEW = "view"
    LIKE = "like"
    SHARE = "share"
    COMMENT = "comment"
    DOWNLOAD = "download"
    BOOKMARK = "bookmark"
    CLICK = "click"
    SCROLL = "scroll"
    HOVER = "hover"
    PAUSE = "pause"
    SKIP = "skip"
    REPLAY = "replay"

@dataclass
class EngagementEvent:
    """Single engagement event data"""
    event_id: str
    user_id: str
    content_id: str
    engagement_type: EngagementType
    timestamp: datetime
    
    # Event details
    duration: Optional[float] = None  # For views, hovers
    position: Optional[float] = None  # For video/audio position
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Context
    platform: Optional[str] = None
    device_type: Optional[str] = None
    user_agent: Optional[str] = None
    referrer: Optional[str] = None
    session_id: Optional[str] = None

@dataclass
class EngagementMetrics:
    """Engagement metrics for content"""
    content_id: str
    analysis_period: Tuple[datetime, datetime]
    
    # Basic metrics
    total_views: int = 0
    unique_viewers: int = 0
    total_interactions: int = 0
    
    # Time-based metrics
    average_view_duration: float = 0.0
    completion_rate: float = 0.0
    bounce_rate: float = 0.0
    retention_curve: List[float] = field(default_factory=list)
    
    # Interaction metrics
    likes: int = 0
    shares: int = 0
    comments: int = 0
    downloads: int = 0
    bookmarks: int = 0
    
    # Calculated metrics
    engagement_rate: float = 0.0
    virality_score: float = 0.0
    quality_score: float = 0.0
    
    # Behavioral insights
    peak_engagement_time: Optional[float] = None
    drop_off_points: List[float] = field(default_factory=list)
    replay_segments: List[Tuple[float, float]] = field(default_factory=list)
    
    # Demographic breakdown
    demographics: Dict[str, Any] = field(default_factory=dict)
    
    # Performance indicators
    trending_score: float = 0.0
    predicted_reach: int = 0

@dataclass
class UserBehaviorProfile:
    """User behavior analysis profile"""
    user_id: str
    analysis_period: Tuple[datetime, datetime]
    
    # Consumption patterns
    total_content_consumed: int = 0
    average_session_duration: float = 0.0
    preferred_content_types: List[str] = field(default_factory=list)
    peak_activity_hours: List[int] = field(default_factory=list)
    
    # Interaction patterns
    interaction_frequency: float = 0.0
    favorite_interaction_types: List[EngagementType] = field(default_factory=list)
    content_completion_rate: float = 0.0
    
    # Preferences
    preferred_platforms: List[str] = field(default_factory=list)
    content_categories: Dict[str, float] = field(default_factory=dict)
    quality_threshold: float = 0.0
    
    # Behavioral scores
    engagement_score: float = 0.0
    loyalty_score: float = 0.0
    influence_score: float = 0.0
    
    # Predictions
    churn_probability: float = 0.0
    next_interaction_prediction: Optional[datetime] = None


class EngagementTracker:
    """Main engagement tracking system"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logger.getChild(self.__class__.__name__)
        
        # Data storage
        self.events: deque = deque(maxlen=self.config.get('max_events', 100000))
        self.user_sessions: Dict[str, List[EngagementEvent]] = defaultdict(list)
        self.content_metrics: Dict[str, EngagementMetrics] = {}
        
        # Analysis parameters
        self.session_timeout = self.config.get('session_timeout', 1800)  # 30 minutes
        self.retention_points = self.config.get('retention_points', 10)
        
    async def track_event(self, event: EngagementEvent) -> bool:
        """Track a single engagement event"""
        try:
            # Validate event
            if not self._validate_event(event):
                return False
            
            # Store event
            self.events.append(event)
            
            # Update user session
            if event.session_id:
                self.user_sessions[event.session_id].append(event)
            
            # Real-time metrics update
            await self._update_real_time_metrics(event)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to track event: {e}")
            return False
    
    def _validate_event(self, event: EngagementEvent) -> bool:
        """Validate engagement event data"""
        required_fields = ['event_id', 'user_id', 'content_id', 'engagement_type', 'timestamp']
        
        for field in required_fields:
            if not getattr(event, field, None):
                self.logger.warning(f"Missing required field: {field}")
                return False
        
        return True
    
    async def _update_real_time_metrics(self, event: EngagementEvent):
        """Update real-time engagement metrics"""
        try:
            content_id = event.content_id
            
            # Initialize metrics if not exists
            if content_id not in self.content_metrics:
                now = datetime.now()
                self.content_metrics[content_id] = EngagementMetrics(
                    content_id=content_id,
                    analysis_period=(now - timedelta(hours=24), now)
                )
            
            metrics = self.content_metrics[content_id]
            
            # Update basic metrics
            if event.engagement_type == EngagementType.VIEW:
                metrics.total_views += 1
                if event.duration:
                    metrics.average_view_duration = (
                        (metrics.average_view_duration * (metrics.total_views - 1) + event.duration) 
                        / metrics.total_views
                    )
            
            elif event.engagement_type == EngagementType.LIKE:
                metrics.likes += 1
            elif event.engagement_type == EngagementType.SHARE:
                metrics.shares += 1
            elif event.engagement_type == EngagementType.COMMENT:
                metrics.comments += 1
            elif event.engagement_type == EngagementType.DOWNLOAD:
                metrics.downloads += 1
            elif event.engagement_type == EngagementType.BOOKMARK:
                metrics.bookmarks += 1
            
            metrics.total_interactions += 1
            
            # Calculate engagement rate
            if metrics.total_views > 0:
                metrics.engagement_rate = (
                    (metrics.likes + metrics.shares + metrics.comments) / metrics.total_views
                )
            
        except Exception as e:
            self.logger.error(f"Failed to update real-time metrics: {e}")
    
    async def analyze_content_engagement(self, content_id: str, 
                                       period_hours: int = 24) -> EngagementMetrics:
        """Analyze engagement for specific content"""
        try:
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=period_hours)
            
            # Filter events for this content and period
            content_events = [
                event for event in self.events
                if event.content_id == content_id and start_time <= event.timestamp <= end_time
            ]
            
            if not content_events:
                return EngagementMetrics(
                    content_id=content_id,
                    analysis_period=(start_time, end_time)
                )
            
            # Initialize metrics
            metrics = EngagementMetrics(
                content_id=content_id,
                analysis_period=(start_time, end_time)
            )
            
            # Analyze events
            await self._calculate_basic_metrics(content_events, metrics)
            await self._calculate_time_based_metrics(content_events, metrics)
            await self._calculate_behavioral_insights(content_events, metrics)
            await self._calculate_performance_scores(content_events, metrics)
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Content engagement analysis failed: {e}")
            return EngagementMetrics(content_id=content_id, analysis_period=(start_time, end_time))
    
    async def _calculate_basic_metrics(self, events: List[EngagementEvent], 
                                     metrics: EngagementMetrics):
        """Calculate basic engagement metrics"""
        try:
            # Count events by type
            event_counts = defaultdict(int)
            unique_users = set()
            
            for event in events:
                event_counts[event.engagement_type] += 1
                unique_users.add(event.user_id)
            
            # Set basic counts
            metrics.total_views = event_counts[EngagementType.VIEW]
            metrics.unique_viewers = len(unique_users)
            metrics.total_interactions = len(events)
            metrics.likes = event_counts[EngagementType.LIKE]
            metrics.shares = event_counts[EngagementType.SHARE]
            metrics.comments = event_counts[EngagementType.COMMENT]
            metrics.downloads = event_counts[EngagementType.DOWNLOAD]
            metrics.bookmarks = event_counts[EngagementType.BOOKMARK]
            
            # Calculate engagement rate
            if metrics.total_views > 0:
                metrics.engagement_rate = (
                    (metrics.likes + metrics.shares + metrics.comments) / metrics.total_views
                )
            
        except Exception as e:
            self.logger.error(f"Basic metrics calculation failed: {e}")
    
    async def _calculate_time_based_metrics(self, events: List[EngagementEvent], 
                                          metrics: EngagementMetrics):
        """Calculate time-based engagement metrics"""
        try:
            view_events = [e for e in events if e.engagement_type == EngagementType.VIEW]
            
            if not view_events:
                return
            
            # Average view duration
            durations = [e.duration for e in view_events if e.duration]
            if durations:
                metrics.average_view_duration = np.mean(durations)
            
            # Calculate retention curve
            if view_events:
                retention_curve = await self._calculate_retention_curve(view_events)
                metrics.retention_curve = retention_curve
                
                # Completion rate (percentage who watched to the end)
                if retention_curve:
                    metrics.completion_rate = retention_curve[-1]
                
                # Bounce rate (percentage who left early)
                early_exits = sum(1 for e in view_events if e.duration and e.duration < 10)
                metrics.bounce_rate = early_exits / len(view_events) if view_events else 0
            
        except Exception as e:
            self.logger.error(f"Time-based metrics calculation failed: {e}")
    
    async def _calculate_retention_curve(self, view_events: List[EngagementEvent]) -> List[float]:
        """Calculate audience retention curve"""
        try:
            if not view_events:
                return []
            
            # Estimate content duration from longest view
            max_duration = max(e.duration for e in view_events if e.duration)
            if not max_duration or max_duration <= 0:
                return []
            
            # Create time points for retention analysis
            time_points = np.linspace(0, max_duration, self.retention_points)
            retention_values = []
            
            total_viewers = len(view_events)
            
            for time_point in time_points:
                # Count viewers still watching at this time point
                viewers_at_point = sum(
                    1 for event in view_events 
                    if event.duration and event.duration >= time_point
                )
                
                retention_rate = viewers_at_point / total_viewers if total_viewers > 0 else 0
                retention_values.append(retention_rate)
            
            return retention_values
            
        except Exception as e:
            self.logger.error(f"Retention curve calculation failed: {e}")
            return []
    
    async def _calculate_behavioral_insights(self, events: List[EngagementEvent], 
                                           metrics: EngagementMetrics):
        """Calculate behavioral insights"""
        try:
            view_events = [e for e in events if e.engagement_type == EngagementType.VIEW]
            
            if not view_events:
                return
            
            # Find peak engagement time
            if view_events:
                engagement_by_time = defaultdict(int)
                
                for event in events:
                    if event.position is not None:
                        time_bucket = int(event.position // 10) * 10  # 10-second buckets
                        engagement_by_time[time_bucket] += 1
                
                if engagement_by_time:
                    peak_time = max(engagement_by_time.items(), key=lambda x: x[1])[0]
                    metrics.peak_engagement_time = float(peak_time)
            
            # Identify drop-off points (significant decreases in retention)
            if metrics.retention_curve:
                drop_offs = []
                threshold = 0.2  # 20% drop threshold
                
                for i in range(1, len(metrics.retention_curve)):
                    drop = metrics.retention_curve[i-1] - metrics.retention_curve[i]
                    if drop > threshold:
                        time_point = (i / len(metrics.retention_curve)) * 100  # Percentage of content
                        drop_offs.append(time_point)
                
                metrics.drop_off_points = drop_offs
            
            # Find replay segments (areas with high re-engagement)
            replay_events = [e for e in events if e.engagement_type == EngagementType.REPLAY]
            if replay_events:
                replay_segments = []
                for event in replay_events:
                    if event.position is not None and event.duration is not None:
                        start_pos = event.position
                        end_pos = min(event.position + event.duration, event.position + 30)
                        replay_segments.append((start_pos, end_pos))
                
                metrics.replay_segments = replay_segments
            
        except Exception as e:
            self.logger.error(f"Behavioral insights calculation failed: {e}")
    
    async def _calculate_performance_scores(self, events: List[EngagementEvent], 
                                          metrics: EngagementMetrics):
        """Calculate performance and prediction scores"""
        try:
            # Virality score based on shares and engagement velocity
            time_span = (metrics.analysis_period[1] - metrics.analysis_period[0]).total_seconds() / 3600
            
            if time_span > 0:
                engagement_velocity = metrics.total_interactions / time_span
                share_ratio = metrics.shares / max(metrics.total_views, 1)
                
                metrics.virality_score = min(
                    (engagement_velocity / 100) * (1 + share_ratio * 10), 1.0
                )
            
            # Quality score based on completion rate and engagement
            quality_factors = [
                metrics.completion_rate,
                min(metrics.engagement_rate * 5, 1.0),  # Scale engagement rate
                max(0, 1 - metrics.bounce_rate)  # Inverse of bounce rate
            ]
            
            metrics.quality_score = np.mean([f for f in quality_factors if f is not None])
            
            # Trending score (recent engagement momentum)
            recent_events = [
                e for e in events 
                if e.timestamp >= metrics.analysis_period[1] - timedelta(hours=1)
            ]
            
            recent_engagement_rate = len(recent_events) / max(len(events), 1)
            metrics.trending_score = min(recent_engagement_rate * 2, 1.0)
            
            # Predicted reach (simple model based on current trajectory)
            if metrics.total_views > 0 and time_span > 0:
                growth_rate = metrics.total_views / time_span
                predicted_24h_reach = int(growth_rate * 24 * (1 + metrics.virality_score))
                metrics.predicted_reach = predicted_24h_reach
            
        except Exception as e:
            self.logger.error(f"Performance scores calculation failed: {e}")


class UserBehaviorAnalyzer:
    """User behavior analysis and profiling"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logger.getChild(self.__class__.__name__)
        
    async def analyze_user_behavior(self, user_id: str, events: List[EngagementEvent],
                                  period_days: int = 30) -> UserBehaviorProfile:
        """Analyze user behavior patterns"""
        try:
            end_time = datetime.now()
            start_time = end_time - timedelta(days=period_days)
            
            # Filter events for this user and period
            user_events = [
                event for event in events
                if event.user_id == user_id and start_time <= event.timestamp <= end_time
            ]
            
            profile = UserBehaviorProfile(
                user_id=user_id,
                analysis_period=(start_time, end_time)
            )
            
            if not user_events:
                return profile
            
            # Analyze consumption patterns
            await self._analyze_consumption_patterns(user_events, profile)
            
            # Analyze interaction patterns
            await self._analyze_interaction_patterns(user_events, profile)
            
            # Analyze preferences
            await self._analyze_preferences(user_events, profile)
            
            # Calculate behavioral scores
            await self._calculate_behavioral_scores(user_events, profile)
            
            # Generate predictions
            await self._generate_predictions(user_events, profile)
            
            return profile
            
        except Exception as e:
            self.logger.error(f"User behavior analysis failed: {e}")
            return UserBehaviorProfile(user_id=user_id, analysis_period=(start_time, end_time))
    
    async def _analyze_consumption_patterns(self, events: List[EngagementEvent],
                                          profile: UserBehaviorProfile):
        """Analyze user content consumption patterns"""
        try:
            # Total content consumed
            unique_content = set(event.content_id for event in events)
            profile.total_content_consumed = len(unique_content)
            
            # Session analysis
            sessions = self._group_events_by_session(events)
            session_durations = []
            
            for session in sessions:
                if len(session) > 1:
                    duration = (session[-1].timestamp - session[0].timestamp).total_seconds()
                    session_durations.append(duration)
            
            if session_durations:
                profile.average_session_duration = np.mean(session_durations)
            
            # Activity time patterns
            activity_hours = [event.timestamp.hour for event in events]
            if activity_hours:
                # Find peak activity hours
                hour_counts = defaultdict(int)
                for hour in activity_hours:
                    hour_counts[hour] += 1
                
                # Get top 3 hours
                peak_hours = sorted(hour_counts.items(), key=lambda x: x[1], reverse=True)[:3]
                profile.peak_activity_hours = [hour for hour, count in peak_hours]
            
        except Exception as e:
            self.logger.error(f"Consumption pattern analysis failed: {e}")
    
    async def _analyze_interaction_patterns(self, events: List[EngagementEvent],
                                          profile: UserBehaviorProfile):
        """Analyze user interaction patterns"""
        try:
            # Interaction frequency
            total_time = (profile.analysis_period[1] - profile.analysis_period[0]).total_seconds()
            profile.interaction_frequency = len(events) / (total_time / 3600)  # per hour
            
            # Favorite interaction types
            interaction_counts = defaultdict(int)
            for event in events:
                interaction_counts[event.engagement_type] += 1
            
            # Sort by frequency
            sorted_interactions = sorted(interaction_counts.items(), key=lambda x: x[1], reverse=True)
            profile.favorite_interaction_types = [interaction for interaction, count in sorted_interactions[:5]]
            
            # Content completion rate
            view_events = [e for e in events if e.engagement_type == EngagementType.VIEW]
            if view_events:
                completed_views = sum(1 for e in view_events if e.duration and e.duration > 60)
                profile.content_completion_rate = completed_views / len(view_events)
            
        except Exception as e:
            self.logger.error(f"Interaction pattern analysis failed: {e}")
    
    async def _analyze_preferences(self, events: List[EngagementEvent],
                                 profile: UserBehaviorProfile):
        """Analyze user preferences"""
        try:
            # Platform preferences
            platform_counts = defaultdict(int)
            for event in events:
                if event.platform:
                    platform_counts[event.platform] += 1
            
            sorted_platforms = sorted(platform_counts.items(), key=lambda x: x[1], reverse=True)
            profile.preferred_platforms = [platform for platform, count in sorted_platforms[:3]]
            
            # Content type analysis (would need additional metadata)
            # This is a simplified version
            content_engagement = defaultdict(list)
            for event in events:
                if event.engagement_type in [EngagementType.LIKE, EngagementType.SHARE, EngagementType.COMMENT]:
                    content_engagement[event.content_id].append(event)
            
            # Calculate engagement scores per content type (simplified)
            if content_engagement:
                avg_engagement = np.mean([len(engagements) for engagements in content_engagement.values()])
                profile.quality_threshold = avg_engagement * 0.8  # 80% of average engagement
            
        except Exception as e:
            self.logger.error(f"Preference analysis failed: {e}")
    
    async def _calculate_behavioral_scores(self, events: List[EngagementEvent],
                                         profile: UserBehaviorProfile):
        """Calculate behavioral scores"""
        try:
            # Engagement score
            interaction_variety = len(set(e.engagement_type for e in events))
            frequency_score = min(profile.interaction_frequency / 10, 1.0)  # Normalize to 10 interactions/hour
            variety_score = min(interaction_variety / 6, 1.0)  # Normalize to 6 interaction types
            
            profile.engagement_score = np.mean([frequency_score, variety_score])
            
            # Loyalty score (based on consistency and return behavior)
            days_active = len(set(event.timestamp.date() for event in events))
            total_days = (profile.analysis_period[1] - profile.analysis_period[0]).days
            consistency_score = days_active / max(total_days, 1)
            
            completion_score = profile.content_completion_rate
            profile.loyalty_score = np.mean([consistency_score, completion_score])
            
            # Influence score (based on shares and viral actions)
            shares = sum(1 for e in events if e.engagement_type == EngagementType.SHARE)
            comments = sum(1 for e in events if e.engagement_type == EngagementType.COMMENT)
            
            total_interactions = len(events)
            if total_interactions > 0:
                viral_ratio = (shares + comments) / total_interactions
                profile.influence_score = min(viral_ratio * 10, 1.0)  # Scale up viral actions
            
        except Exception as e:
            self.logger.error(f"Behavioral scores calculation failed: {e}")
    
    async def _generate_predictions(self, events: List[EngagementEvent],
                                  profile: UserBehaviorProfile):
        """Generate behavioral predictions"""
        try:
            # Churn probability (simplified model)
            recent_events = [
                e for e in events 
                if e.timestamp >= datetime.now() - timedelta(days=7)
            ]
            
            recent_activity = len(recent_events)
            expected_activity = profile.interaction_frequency * 24 * 7  # Expected weekly activity
            
            if expected_activity > 0:
                activity_ratio = recent_activity / expected_activity
                profile.churn_probability = max(0, 1 - activity_ratio)
            
            # Next interaction prediction (based on activity patterns)
            if events:
                # Calculate average time between interactions
                time_deltas = []
                sorted_events = sorted(events, key=lambda x: x.timestamp)
                
                for i in range(1, len(sorted_events)):
                    delta = (sorted_events[i].timestamp - sorted_events[i-1].timestamp).total_seconds()
                    time_deltas.append(delta)
                
                if time_deltas:
                    avg_interval = np.mean(time_deltas)
                    profile.next_interaction_prediction = (
                        events[-1].timestamp + timedelta(seconds=avg_interval)
                    )
            
        except Exception as e:
            self.logger.error(f"Prediction generation failed: {e}")
    
    def _group_events_by_session(self, events: List[EngagementEvent]) -> List[List[EngagementEvent]]:
        """Group events into user sessions"""
        if not events:
            return []
        
        sorted_events = sorted(events, key=lambda x: x.timestamp)
        sessions = []
        current_session = [sorted_events[0]]
        
        for i in range(1, len(sorted_events)):
            time_gap = (sorted_events[i].timestamp - sorted_events[i-1].timestamp).total_seconds()
            
            if time_gap <= self.config.get('session_timeout', 1800):  # 30 minutes default
                current_session.append(sorted_events[i])
            else:
                sessions.append(current_session)
                current_session = [sorted_events[i]]
        
        sessions.append(current_session)
        return sessions


class InteractionMetrics:
    """Advanced interaction metrics calculator"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logger.getChild(self.__class__.__name__)
    
    async def calculate_interaction_matrix(self, events: List[EngagementEvent]) -> Dict[str, Any]:
        """Calculate interaction correlation matrix"""
        try:
            # Group events by user and content
            user_content_interactions = defaultdict(lambda: defaultdict(list))
            
            for event in events:
                user_content_interactions[event.user_id][event.content_id].append(event.engagement_type)
            
            # Calculate interaction patterns
            interaction_sequences = []
            for user_interactions in user_content_interactions.values():
                for content_interactions in user_interactions.values():
                    if len(content_interactions) > 1:
                        interaction_sequences.append(content_interactions)
            
            # Analyze common interaction patterns
            pattern_frequency = defaultdict(int)
            for sequence in interaction_sequences:
                for i in range(len(sequence) - 1):
                    pattern = (sequence[i], sequence[i + 1])
                    pattern_frequency[pattern] += 1
            
            # Calculate transition probabilities
            transition_matrix = {}
            for (from_type, to_type), count in pattern_frequency.items():
                if from_type not in transition_matrix:
                    transition_matrix[from_type] = {}
                transition_matrix[from_type][to_type] = count
            
            # Normalize to probabilities
            for from_type in transition_matrix:
                total = sum(transition_matrix[from_type].values())
                for to_type in transition_matrix[from_type]:
                    transition_matrix[from_type][to_type] /= total
            
            return {
                'transition_matrix': transition_matrix,
                'common_patterns': dict(sorted(pattern_frequency.items(), key=lambda x: x[1], reverse=True)[:10])
            }
            
        except Exception as e:
            self.logger.error(f"Interaction matrix calculation failed: {e}")
            return {}