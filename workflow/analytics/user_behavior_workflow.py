"""User Behavior Workflow - Advanced User Behavior Analytics for Ainflue Platform.

This module provides comprehensive user behavior analysis and interaction patterns
across all touchpoints, enabling deep insights into audience preferences and optimization opportunities.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Ainflue Platform. All rights reserved.
Licensed under proprietary license - reproduction forbidden without written authorization.
"""

from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import asyncio
import logging
import json

logger = logging.getLogger(__name__)


class UserActionType(Enum):
    """Types of user actions to track."""
    VIEW = "view"
    CLICK = "click"
    LIKE = "like"
    COMMENT = "comment"
    SHARE = "share"
    SAVE = "save"
    FOLLOW = "follow"
    UNFOLLOW = "unfollow"
    PURCHASE = "purchase"
    DOWNLOAD = "download"
    SEARCH = "search"
    NAVIGATION = "navigation"
    TIME_SPENT = "time_spent"
    SCROLL_DEPTH = "scroll_depth"


class DeviceType(Enum):
    """Device types for behavior tracking."""
    MOBILE = "mobile"
    DESKTOP = "desktop"
    TABLET = "tablet"
    SMART_TV = "smart_tv"
    WEARABLE = "wearable"


@dataclass
class BehaviorMetrics:
    """User behavior metrics data structure."""
    user_id: str
    session_id: str
    content_id: Optional[str]
    action_type: UserActionType
    timestamp: datetime
    platform: str
    device_type: DeviceType
    duration: Optional[float] = None  # seconds
    location: Optional[Dict[str, str]] = None
    referrer: Optional[str] = None
    user_agent: Optional[str] = None
    scroll_depth: Optional[float] = None  # percentage
    interaction_context: Optional[Dict[str, Any]] = None
    conversion_value: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class UserSegment:
    """User behavior segment."""
    segment_id: str
    name: str
    description: str
    user_count: int
    behavioral_characteristics: Dict[str, Any]
    engagement_level: str  # high, medium, low
    preferred_content_types: List[str]
    peak_activity_times: List[int]  # hours of day
    conversion_rate: float
    lifetime_value: float


@dataclass
class UserInsights:
    """Comprehensive user behavior insights."""
    analysis_period: Dict[str, datetime]
    total_users: int
    unique_sessions: int
    user_segments: List[UserSegment]
    behavior_patterns: Dict[str, Any]
    content_preferences: Dict[str, Any]
    journey_analysis: Dict[str, Any]
    engagement_funnel: Dict[str, float]
    churn_analysis: Dict[str, Any]
    personalization_opportunities: List[str]
    user_lifetime_analytics: Dict[str, Any]


class UserBehaviorWorkflow:
    """Advanced user behavior analysis workflow for comprehensive audience insights."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize user behavior workflow.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.tracking_window = self.config.get('tracking_window', 30)  # days
        self.session_timeout = self.config.get('session_timeout', 1800)  # 30 minutes
        self.behavior_cache = {}

    async def analyze_user_behavior(
        self,
        creator_id: str,
        time_period: Optional[Dict[str, datetime]] = None,
        platforms: Optional[List[str]] = None,
        user_cohort: Optional[str] = None
    ) -> UserInsights:
        """Perform comprehensive user behavior analysis.
        
        Args:
            creator_id: Creator identifier
            time_period: Time period for analysis
            platforms: Platforms to analyze
            user_cohort: Specific user cohort to analyze
            
        Returns:
            UserInsights with comprehensive behavior data
        """
        try:
            logger.info(f"Starting user behavior analysis for creator: {creator_id}")
            
            # Set defaults
            time_period = time_period or {
                'start': datetime.now() - timedelta(days=self.tracking_window),
                'end': datetime.now()
            }
            platforms = platforms or ['instagram', 'tiktok', 'youtube', 'website']
            
            # Collect behavior data
            behavior_data = await self._collect_behavior_data(
                creator_id, time_period, platforms, user_cohort
            )
            
            # Calculate basic metrics
            total_users = len(set(metric.user_id for metric in behavior_data))
            unique_sessions = len(set(metric.session_id for metric in behavior_data))
            
            # Perform user segmentation
            user_segments = await self._segment_users(behavior_data)
            
            # Analyze behavior patterns
            behavior_patterns = self._analyze_behavior_patterns(behavior_data)
            
            # Analyze content preferences
            content_preferences = self._analyze_content_preferences(behavior_data)
            
            # Perform journey analysis
            journey_analysis = await self._analyze_user_journey(behavior_data)
            
            # Calculate engagement funnel
            engagement_funnel = self._calculate_engagement_funnel(behavior_data)
            
            # Perform churn analysis
            churn_analysis = await self._analyze_churn(creator_id, behavior_data)
            
            # Identify personalization opportunities
            personalization_opportunities = await self._identify_personalization_opportunities(
                behavior_data, user_segments
            )
            
            # Calculate user lifetime analytics
            lifetime_analytics = self._calculate_user_lifetime_analytics(behavior_data)
            
            insights = UserInsights(
                analysis_period=time_period,
                total_users=total_users,
                unique_sessions=unique_sessions,
                user_segments=user_segments,
                behavior_patterns=behavior_patterns,
                content_preferences=content_preferences,
                journey_analysis=journey_analysis,
                engagement_funnel=engagement_funnel,
                churn_analysis=churn_analysis,
                personalization_opportunities=personalization_opportunities,
                user_lifetime_analytics=lifetime_analytics
            )
            
            # Cache insights
            self.behavior_cache[creator_id] = insights
            
            logger.info(f"User behavior analysis completed for creator: {creator_id}")
            return insights
            
        except Exception as e:
            logger.error(f"Error analyzing user behavior for creator {creator_id}: {str(e)}")
            raise

    async def _collect_behavior_data(
        self,
        creator_id: str,
        time_period: Dict[str, datetime],
        platforms: List[str],
        user_cohort: Optional[str]
    ) -> List[BehaviorMetrics]:
        """Collect user behavior data from all sources.
        
        Args:
            creator_id: Creator identifier
            time_period: Time period for collection
            platforms: Platforms to collect from
            user_cohort: Specific user cohort filter
            
        Returns:
            List of BehaviorMetrics
        """
        try:
            behavior_data = []
            
            for platform in platforms:
                platform_data = await self._get_platform_behavior_data(
                    creator_id, platform, time_period, user_cohort
                )
                behavior_data.extend(platform_data)
            
            return behavior_data
            
        except Exception as e:
            logger.error(f"Error collecting behavior data: {str(e)}")
            return []

    async def _get_platform_behavior_data(
        self,
        creator_id: str,
        platform: str,
        time_period: Dict[str, datetime],
        user_cohort: Optional[str]
    ) -> List[BehaviorMetrics]:
        """Get behavior data from specific platform.
        
        Args:
            creator_id: Creator identifier
            platform: Platform name
            time_period: Time period
            user_cohort: User cohort filter
            
        Returns:
            List of BehaviorMetrics for the platform
        """
        try:
            # Simulate API call delay
            await asyncio.sleep(0.2)
            
            # Mock behavior data generation
            import random
            import uuid
            
            behavior_data = []
            days = (time_period['end'] - time_period['start']).days
            
            # Generate realistic user sessions
            num_users = random.randint(100, 1000)
            user_ids = [f"user_{uuid.uuid4().hex[:8]}" for _ in range(num_users)]
            
            for day in range(days):
                date = time_period['start'] + timedelta(days=day)
                
                # Daily active users (some percentage of total users)
                daily_active_users = random.sample(user_ids, random.randint(20, min(200, len(user_ids))))
                
                for user_id in daily_active_users:
                    # Generate user session
                    session_data = self._generate_user_session(
                        user_id, platform, date, creator_id
                    )
                    behavior_data.extend(session_data)
            
            return behavior_data
            
        except Exception as e:
            logger.error(f"Error getting {platform} behavior data: {str(e)}")
            return []

    def _generate_user_session(
        self,
        user_id: str,
        platform: str,
        date: datetime,
        creator_id: str
    ) -> List[BehaviorMetrics]:
        """Generate realistic user session data.
        
        Args:
            user_id: User identifier
            platform: Platform name
            date: Session date
            creator_id: Creator identifier
            
        Returns:
            List of BehaviorMetrics for the session
        """
        import random
        import uuid
        
        session_id = f"session_{uuid.uuid4().hex[:12]}"
        session_data = []
        
        # Random session start time during the day
        hour = random.randint(6, 23)
        minute = random.randint(0, 59)
        session_start = date.replace(hour=hour, minute=minute)
        
        # Session duration (5 minutes to 2 hours)
        session_duration = random.randint(300, 7200)  # seconds
        
        # Device type distribution
        device_types = [DeviceType.MOBILE, DeviceType.DESKTOP, DeviceType.TABLET]
        device_weights = [0.7, 0.25, 0.05]  # Mobile-first
        device_type = random.choices(device_types, weights=device_weights)[0]
        
        # Generate content interactions
        content_ids = [f"content_{i}" for i in range(1, 21)]  # Mock content IDs
        current_time = session_start
        
        # Entry action
        entry_action = BehaviorMetrics(
            user_id=user_id,
            session_id=session_id,
            content_id=None,
            action_type=UserActionType.NAVIGATION,
            timestamp=current_time,
            platform=platform,
            device_type=device_type,
            location={'country': 'US', 'city': 'New York'},
            referrer=random.choice(['google', 'direct', 'social', 'email']),
            metadata={'entry_point': 'home_page'}
        )
        session_data.append(entry_action)
        
        # Content interactions during session
        num_interactions = random.randint(3, 20)
        for i in range(num_interactions):
            content_id = random.choice(content_ids)
            action_type = random.choices(
                [UserActionType.VIEW, UserActionType.LIKE, UserActionType.COMMENT, 
                 UserActionType.SHARE, UserActionType.SAVE, UserActionType.CLICK],
                weights=[0.4, 0.2, 0.1, 0.1, 0.1, 0.1]
            )[0]
            
            # Time progression
            time_increment = random.randint(10, 300)  # 10 seconds to 5 minutes
            current_time += timedelta(seconds=time_increment)
            
            if current_time > session_start + timedelta(seconds=session_duration):
                break
            
            interaction = BehaviorMetrics(
                user_id=user_id,
                session_id=session_id,
                content_id=content_id,
                action_type=action_type,
                timestamp=current_time,
                platform=platform,
                device_type=device_type,
                duration=random.uniform(5, 120) if action_type == UserActionType.VIEW else None,
                scroll_depth=random.uniform(20, 100) if action_type == UserActionType.VIEW else None,
                interaction_context={
                    'source': 'feed',
                    'position': random.randint(1, 20)
                },
                conversion_value=random.uniform(0, 100) if action_type == UserActionType.PURCHASE else None
            )
            session_data.append(interaction)
        
        return session_data

    async def _segment_users(self, behavior_data: List[BehaviorMetrics]) -> List[UserSegment]:
        """Segment users based on behavior patterns.
        
        Args:
            behavior_data: List of behavior metrics
            
        Returns:
            List of UserSegment objects
        """
        try:
            # Analyze user behavior patterns
            user_profiles = {}
            
            for metric in behavior_data:
                user_id = metric.user_id
                if user_id not in user_profiles:
                    user_profiles[user_id] = {
                        'actions': [],
                        'sessions': set(),
                        'platforms': set(),
                        'devices': set(),
                        'total_duration': 0,
                        'content_interactions': 0
                    }
                
                profile = user_profiles[user_id]
                profile['actions'].append(metric.action_type)
                profile['sessions'].add(metric.session_id)
                profile['platforms'].add(metric.platform)
                profile['devices'].add(metric.device_type)
                
                if metric.duration:
                    profile['total_duration'] += metric.duration
                
                if metric.content_id:
                    profile['content_interactions'] += 1
            
            # Create user segments based on behavior patterns
            segments = []
            
            # High Engagement Segment
            high_engagement_users = [
                user_id for user_id, profile in user_profiles.items()
                if len(profile['sessions']) >= 5 and profile['content_interactions'] >= 20
            ]
            
            if high_engagement_users:
                segments.append(UserSegment(
                    segment_id="high_engagement",
                    name="High Engagement Users",
                    description="Users with frequent visits and high content interaction",
                    user_count=len(high_engagement_users),
                    behavioral_characteristics={
                        'avg_sessions_per_user': sum(len(user_profiles[uid]['sessions']) 
                                                   for uid in high_engagement_users) / len(high_engagement_users),
                        'avg_content_interactions': sum(user_profiles[uid]['content_interactions'] 
                                                      for uid in high_engagement_users) / len(high_engagement_users),
                        'platform_diversity': 'high'
                    },
                    engagement_level="high",
                    preferred_content_types=['video', 'carousel', 'stories'],
                    peak_activity_times=[19, 20, 21],
                    conversion_rate=8.5,
                    lifetime_value=250.0
                ))
            
            # Medium Engagement Segment
            medium_engagement_users = [
                user_id for user_id, profile in user_profiles.items()
                if 2 <= len(profile['sessions']) < 5 and 5 <= profile['content_interactions'] < 20
            ]
            
            if medium_engagement_users:
                segments.append(UserSegment(
                    segment_id="medium_engagement",
                    name="Medium Engagement Users",
                    description="Users with moderate visit frequency and content interaction",
                    user_count=len(medium_engagement_users),
                    behavioral_characteristics={
                        'avg_sessions_per_user': sum(len(user_profiles[uid]['sessions']) 
                                                   for uid in medium_engagement_users) / len(medium_engagement_users),
                        'avg_content_interactions': sum(user_profiles[uid]['content_interactions'] 
                                                      for uid in medium_engagement_users) / len(medium_engagement_users),
                        'platform_diversity': 'medium'
                    },
                    engagement_level="medium",
                    preferred_content_types=['image', 'video'],
                    peak_activity_times=[12, 18, 22],
                    conversion_rate=4.2,
                    lifetime_value=120.0
                ))
            
            # Low Engagement Segment
            low_engagement_users = [
                user_id for user_id, profile in user_profiles.items()
                if len(profile['sessions']) < 2 or profile['content_interactions'] < 5
            ]
            
            if low_engagement_users:
                segments.append(UserSegment(
                    segment_id="low_engagement",
                    name="Low Engagement Users",
                    description="Users with infrequent visits and minimal content interaction",
                    user_count=len(low_engagement_users),
                    behavioral_characteristics={
                        'avg_sessions_per_user': sum(len(user_profiles[uid]['sessions']) 
                                                   for uid in low_engagement_users) / len(low_engagement_users),
                        'avg_content_interactions': sum(user_profiles[uid]['content_interactions'] 
                                                      for uid in low_engagement_users) / len(low_engagement_users),
                        'platform_diversity': 'low'
                    },
                    engagement_level="low",
                    preferred_content_types=['image'],
                    peak_activity_times=[8, 13, 20],
                    conversion_rate=1.8,
                    lifetime_value=45.0
                ))
            
            return segments
            
        except Exception as e:
            logger.error(f"Error segmenting users: {str(e)}")
            return []

    def _analyze_behavior_patterns(self, behavior_data: List[BehaviorMetrics]) -> Dict[str, Any]:
        """Analyze general behavior patterns.
        
        Args:
            behavior_data: List of behavior metrics
            
        Returns:
            Dictionary with behavior pattern analysis
        """
        if not behavior_data:
            return {}
        
        # Analyze activity by hour
        hourly_activity = {}
        for metric in behavior_data:
            hour = metric.timestamp.hour
            if hour not in hourly_activity:
                hourly_activity[hour] = 0
            hourly_activity[hour] += 1
        
        # Find peak hours
        peak_hours = sorted(hourly_activity.items(), key=lambda x: x[1], reverse=True)[:3]
        
        # Analyze device usage
        device_usage = {}
        for metric in behavior_data:
            device = metric.device_type.value
            if device not in device_usage:
                device_usage[device] = 0
            device_usage[device] += 1
        
        # Analyze platform distribution
        platform_usage = {}
        for metric in behavior_data:
            platform = metric.platform
            if platform not in platform_usage:
                platform_usage[platform] = 0
            platform_usage[platform] += 1
        
        # Calculate session metrics
        sessions = {}
        for metric in behavior_data:
            session_id = metric.session_id
            if session_id not in sessions:
                sessions[session_id] = []
            sessions[session_id].append(metric)
        
        session_durations = []
        for session_actions in sessions.values():
            if len(session_actions) > 1:
                start_time = min(action.timestamp for action in session_actions)
                end_time = max(action.timestamp for action in session_actions)
                duration = (end_time - start_time).total_seconds()
                session_durations.append(duration)
        
        avg_session_duration = sum(session_durations) / len(session_durations) if session_durations else 0
        
        return {
            'peak_activity_hours': [hour for hour, count in peak_hours],
            'hourly_activity_distribution': hourly_activity,
            'device_usage_distribution': device_usage,
            'platform_usage_distribution': platform_usage,
            'average_session_duration_seconds': avg_session_duration,
            'total_sessions': len(sessions),
            'actions_per_session': len(behavior_data) / len(sessions) if sessions else 0
        }

    def _analyze_content_preferences(self, behavior_data: List[BehaviorMetrics]) -> Dict[str, Any]:
        """Analyze user content preferences.
        
        Args:
            behavior_data: List of behavior metrics
            
        Returns:
            Dictionary with content preference analysis
        """
        content_interactions = {}
        action_types = {}
        
        for metric in behavior_data:
            if metric.content_id:
                content_id = metric.content_id
                action = metric.action_type.value
                
                if content_id not in content_interactions:
                    content_interactions[content_id] = 0
                content_interactions[content_id] += 1
                
                if action not in action_types:
                    action_types[action] = 0
                action_types[action] += 1
        
        # Most popular content
        popular_content = sorted(content_interactions.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # Most common actions
        common_actions = sorted(action_types.items(), key=lambda x: x[1], reverse=True)
        
        return {
            'most_popular_content': popular_content,
            'interaction_type_distribution': action_types,
            'most_common_actions': common_actions,
            'content_engagement_rate': len(content_interactions) / len(set(metric.user_id for metric in behavior_data)) if behavior_data else 0
        }

    async def _analyze_user_journey(self, behavior_data: List[BehaviorMetrics]) -> Dict[str, Any]:
        """Analyze user journey patterns.
        
        Args:
            behavior_data: List of behavior metrics
            
        Returns:
            Dictionary with user journey analysis
        """
        try:
            # Group actions by session
            sessions = {}
            for metric in behavior_data:
                session_id = metric.session_id
                if session_id not in sessions:
                    sessions[session_id] = []
                sessions[session_id].append(metric)
            
            # Analyze journey paths
            journey_paths = []
            entry_points = {}
            exit_points = {}
            
            for session_actions in sessions.values():
                # Sort by timestamp
                sorted_actions = sorted(session_actions, key=lambda x: x.timestamp)
                
                if sorted_actions:
                    # Entry point
                    entry_action = sorted_actions[0]
                    entry_key = f"{entry_action.platform}_{entry_action.action_type.value}"
                    if entry_key not in entry_points:
                        entry_points[entry_key] = 0
                    entry_points[entry_key] += 1
                    
                    # Exit point
                    exit_action = sorted_actions[-1]
                    exit_key = f"{exit_action.platform}_{exit_action.action_type.value}"
                    if exit_key not in exit_points:
                        exit_points[exit_key] = 0
                    exit_points[exit_key] += 1
                    
                    # Journey path
                    path = " -> ".join([f"{action.action_type.value}" for action in sorted_actions[:5]])  # First 5 actions
                    journey_paths.append(path)
            
            # Common journey patterns
            from collections import Counter
            path_frequency = Counter(journey_paths)
            common_paths = path_frequency.most_common(10)
            
            return {
                'total_journeys': len(sessions),
                'common_entry_points': sorted(entry_points.items(), key=lambda x: x[1], reverse=True)[:5],
                'common_exit_points': sorted(exit_points.items(), key=lambda x: x[1], reverse=True)[:5],
                'most_common_journey_paths': common_paths,
                'average_journey_length': sum(len(actions) for actions in sessions.values()) / len(sessions) if sessions else 0
            }
            
        except Exception as e:
            logger.error(f"Error analyzing user journey: {str(e)}")
            return {}

    def _calculate_engagement_funnel(self, behavior_data: List[BehaviorMetrics]) -> Dict[str, float]:
        """Calculate engagement funnel metrics.
        
        Args:
            behavior_data: List of behavior metrics
            
        Returns:
            Dictionary with funnel conversion rates
        """
        user_actions = {}
        
        for metric in behavior_data:
            user_id = metric.user_id
            if user_id not in user_actions:
                user_actions[user_id] = set()
            user_actions[user_id].add(metric.action_type)
        
        total_users = len(user_actions)
        if total_users == 0:
            return {}
        
        # Define funnel stages
        stages = {
            'awareness': [UserActionType.VIEW, UserActionType.NAVIGATION],
            'interest': [UserActionType.LIKE, UserActionType.SAVE],
            'consideration': [UserActionType.COMMENT, UserActionType.SHARE],
            'intent': [UserActionType.FOLLOW, UserActionType.CLICK],
            'action': [UserActionType.PURCHASE, UserActionType.DOWNLOAD]
        }
        
        funnel_rates = {}
        previous_stage_users = total_users
        
        for stage, actions in stages.items():
            users_in_stage = sum(1 for user_actions_set in user_actions.values() 
                               if any(action in user_actions_set for action in actions))
            
            conversion_rate = (users_in_stage / previous_stage_users) * 100 if previous_stage_users > 0 else 0
            funnel_rates[stage] = round(conversion_rate, 2)
            
            previous_stage_users = users_in_stage
        
        return funnel_rates

    async def _analyze_churn(self, creator_id: str, behavior_data: List[BehaviorMetrics]) -> Dict[str, Any]:
        """Analyze user churn patterns.
        
        Args:
            creator_id: Creator identifier
            behavior_data: List of behavior metrics
            
        Returns:
            Dictionary with churn analysis
        """
        try:
            # Mock churn analysis (in real implementation, analyze historical data)
            import random
            
            user_last_activity = {}
            for metric in behavior_data:
                user_id = metric.user_id
                if user_id not in user_last_activity or metric.timestamp > user_last_activity[user_id]:
                    user_last_activity[user_id] = metric.timestamp
            
            # Define churn threshold (e.g., no activity in last 14 days)
            churn_threshold = datetime.now() - timedelta(days=14)
            
            churned_users = [user_id for user_id, last_activity in user_last_activity.items() 
                           if last_activity < churn_threshold]
            
            active_users = len(user_last_activity) - len(churned_users)
            churn_rate = (len(churned_users) / len(user_last_activity)) * 100 if user_last_activity else 0
            
            # Mock additional churn metrics
            return {
                'total_users_analyzed': len(user_last_activity),
                'churned_users': len(churned_users),
                'active_users': active_users,
                'churn_rate_percentage': round(churn_rate, 2),
                'average_user_lifespan_days': random.randint(30, 180),
                'churn_risk_factors': ['low_engagement', 'infrequent_visits', 'single_platform_usage'],
                'retention_recommendations': [
                    'Implement re-engagement campaigns',
                    'Personalize content recommendations',
                    'Send activity reminders'
                ]
            }
            
        except Exception as e:
            logger.error(f"Error analyzing churn: {str(e)}")
            return {}

    async def _identify_personalization_opportunities(
        self,
        behavior_data: List[BehaviorMetrics],
        user_segments: List[UserSegment]
    ) -> List[str]:
        """Identify personalization opportunities.
        
        Args:
            behavior_data: List of behavior metrics
            user_segments: User segments
            
        Returns:
            List of personalization opportunity descriptions
        """
        opportunities = []
        
        if not behavior_data:
            return ["No behavior data available for personalization analysis"]
        
        # Device-based personalization
        device_usage = {}
        for metric in behavior_data:
            device = metric.device_type.value
            device_usage[device] = device_usage.get(device, 0) + 1
        
        if device_usage.get('mobile', 0) > device_usage.get('desktop', 0) * 2:
            opportunities.append("High mobile usage detected - optimize for mobile-first content experience")
        
        # Time-based personalization
        hourly_activity = {}
        for metric in behavior_data:
            hour = metric.timestamp.hour
            hourly_activity[hour] = hourly_activity.get(hour, 0) + 1
        
        peak_hours = sorted(hourly_activity.items(), key=lambda x: x[1], reverse=True)[:3]
        peak_times = [f"{hour}:00" for hour, _ in peak_hours]
        opportunities.append(f"Personalize content delivery for peak activity times: {', '.join(peak_times)}")
        
        # Segment-based personalization
        for segment in user_segments:
            if segment.engagement_level == "high":
                opportunities.append(f"Create exclusive content for {segment.name} to maintain high engagement")
            elif segment.engagement_level == "low":
                opportunities.append(f"Develop re-engagement campaigns for {segment.name}")
        
        # Content preference personalization
        content_interactions = {}
        for metric in behavior_data:
            if metric.content_id and metric.action_type == UserActionType.VIEW:
                content_type = metric.metadata.get('content_type', 'unknown') if metric.metadata else 'unknown'
                content_interactions[content_type] = content_interactions.get(content_type, 0) + 1
        
        if content_interactions:
            top_content_type = max(content_interactions, key=content_interactions.get)
            opportunities.append(f"Focus on {top_content_type} content based on user preferences")
        
        return opportunities

    def _calculate_user_lifetime_analytics(self, behavior_data: List[BehaviorMetrics]) -> Dict[str, Any]:
        """Calculate user lifetime analytics.
        
        Args:
            behavior_data: List of behavior metrics
            
        Returns:
            Dictionary with user lifetime analytics
        """
        if not behavior_data:
            return {}
        
        # Calculate user activity spans
        user_activity = {}
        for metric in behavior_data:
            user_id = metric.user_id
            if user_id not in user_activity:
                user_activity[user_id] = {'first': metric.timestamp, 'last': metric.timestamp, 'actions': 0}
            
            user_activity[user_id]['first'] = min(user_activity[user_id]['first'], metric.timestamp)
            user_activity[user_id]['last'] = max(user_activity[user_id]['last'], metric.timestamp)
            user_activity[user_id]['actions'] += 1
        
        # Calculate lifetime metrics
        lifespans = []
        total_actions = []
        
        for user_data in user_activity.values():
            lifespan = (user_data['last'] - user_data['first']).days
            lifespans.append(lifespan)
            total_actions.append(user_data['actions'])
        
        avg_lifespan = sum(lifespans) / len(lifespans) if lifespans else 0
        avg_actions = sum(total_actions) / len(total_actions) if total_actions else 0
        
        # Mock additional lifetime metrics
        import random
        
        return {
            'average_user_lifespan_days': round(avg_lifespan, 2),
            'average_actions_per_user': round(avg_actions, 2),
            'user_retention_day_1': random.uniform(80, 95),  # Mock retention rates
            'user_retention_day_7': random.uniform(60, 80),
            'user_retention_day_30': random.uniform(30, 50),
            'average_session_frequency': round(len(set(metric.session_id for metric in behavior_data)) / len(user_activity), 2),
            'power_users_percentage': random.uniform(5, 15)  # Users with high activity
        }