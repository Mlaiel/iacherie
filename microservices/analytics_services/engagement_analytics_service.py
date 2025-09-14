"""
Engagement Analytics Service module
Enterprise implementation for Ainflue platform
"""

#!/usr/bin/env python3
"""
📊 ENGAGEMENT ANALYTICS SERVICE
===============================

Advanced engagement analytics and optimization service for creator platform.
Tracks, analyzes, and optimizes user engagement across all content and interactions.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved

⚠️ STRICT COPYRIGHT WARNING ⚠️
This code is proprietary and confidential. Unauthorized use, reproduction,
distribution, or modification is strictly prohibited and will be prosecuted
to the full extent of the law.

🎖️ MULTI-EXPERT IMPLEMENTATION:
- Lead Dev IA: AI-powered engagement prediction and optimization algorithms
- Backend Senior: Enterprise analytics infrastructure with real-time processing
- ML Engineer: ML models for engagement prediction and user behavior analysis
- DBA: Optimized analytics data models and time-series databases
- Security: Secure analytics data collection and privacy compliance
- Microservices: Integration with content, user, and gamification services
- Audio Engineer: Audio content engagement metrics and optimization
- DevOps: Real-time analytics pipelines and monitoring dashboards
- AI Prompt Engineer: Intelligent engagement insights and recommendation generation
"""

import asyncio
import logging
import time
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Set, Union
from dataclasses import dataclass, asdict
from enum import Enum
import pandas as pd
import numpy as np
from collections import defaultdict, deque
import uuid
import redis.asyncio as redis
from concurrent.futures import ThreadPoolExecutor
import statistics
import math
import random

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EngagementType(Enum):
    """Types of engagement events"""
    VIEW = "view"
    LIKE = "like"
    COMMENT = "comment"
    SHARE = "share"
    DOWNLOAD = "download"
    FOLLOW = "follow"
    SUBSCRIBE = "subscribe"
    PLAY = "play"
    PAUSE = "pause"
    SKIP = "skip"
    REPLAY = "replay"
    BOOKMARK = "bookmark"
    CLICK = "click"
    SCROLL = "scroll"
    TIME_SPENT = "time_spent"

class ContentType(Enum):
    """Content type classification for analytics"""
    MUSIC = "music"
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"
    PODCAST = "podcast"
    LIVE_STREAM = "live_stream"
    SHORT_FORM = "short_form"
    STORY = "story"

class EngagementChannel(Enum):
    """Channels where engagement occurs"""
    PLATFORM_NATIVE = "platform_native"
    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    SPOTIFY = "spotify"
    SOUNDCLOUD = "soundcloud"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    LINKEDIN = "linkedin"
    TWITCH = "twitch"

class AnalyticsTimeframe(Enum):
    """Analytics timeframe options"""
    REAL_TIME = "real_time"
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"

@dataclass
class EngagementEvent:
    """Individual engagement event"""
    id: str
    user_id: str
    content_id: str
    creator_id: str
    engagement_type: EngagementType
    content_type: ContentType
    channel: EngagementChannel
    timestamp: datetime
    value: float = 1.0  # Engagement strength/weight
    session_id: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self) -> None:
        if self.metadata is None:
            self.metadata = {}

@dataclass
class EngagementMetrics:
    """Aggregated engagement metrics"""
    content_id: str
    creator_id: str
    timeframe: str
    
    # Core metrics
    total_views: int = 0
    unique_viewers: int = 0
    total_likes: int = 0
    total_comments: int = 0
    total_shares: int = 0
    total_downloads: int = 0
    
    # Time-based metrics
    average_session_duration: float = 0.0
    completion_rate: float = 0.0
    replay_rate: float = 0.0
    
    # Engagement rates
    like_rate: float = 0.0
    comment_rate: float = 0.0
    share_rate: float = 0.0
    engagement_rate: float = 0.0
    
    # Advanced metrics
    viral_coefficient: float = 0.0
    stickiness_score: float = 0.0
    quality_score: float = 0.0

@dataclass
class UserEngagementProfile:
    """User engagement behavior profile"""
    user_id: str
    
    # Behavior patterns
    preferred_content_types: List[str]
    preferred_channels: List[str]
    peak_activity_hours: List[int]
    engagement_consistency: float
    
    # Engagement metrics
    total_engagements: int
    average_session_duration: float
    content_discovery_rate: float
    creator_loyalty_score: float
    
    # Predictions
    churn_probability: float = 0.0
    next_engagement_prediction: Optional[datetime] = None
    recommended_content_types: List[str] = None
    
    def __post_init__(self) -> None:
        if self.recommended_content_types is None:
            self.recommended_content_types = []

class EngagementAnalyticsService:
    """
    📊 Advanced Engagement Analytics Service
    
    Multi-Expert Implementation:
    - Lead Dev IA: AI-powered engagement prediction and optimization
    - Backend Senior: Scalable real-time analytics infrastructure
    - ML Engineer: Advanced ML models for behavior analysis and prediction
    - DBA: Optimized time-series data storage and analytics queries
    - Security: Privacy-compliant data collection and secure analytics
    - Microservices: Integration with content and user management systems
    - Audio Engineer: Audio-specific engagement metrics and optimization
    - DevOps: Real-time analytics pipelines and monitoring systems
    - AI Prompt Engineer: Intelligent insights and recommendation generation
    """
    
    def __init__(self, redis_url -> None: str = "redis -> None://localhost -> None:6379") -> None:
        """Initialize engagement analytics service"""
        self.redis_url = redis_url
        self.redis_client = None
        self.executor = ThreadPoolExecutor(max_workers=20)
        
        # Analytics storage
        self.engagement_events: deque = deque(maxlen=100000)  # Recent events buffer
        self.aggregated_metrics: Dict[str, EngagementMetrics] = {}
        self.user_profiles: Dict[str, UserEngagementProfile] = {}
        self.content_analytics: Dict[str, Dict] = defaultdict(dict)
        
        # Real-time tracking
        self.active_sessions: Dict[str, Dict] = {}
        self.real_time_counters: Dict[str, int] = defaultdict(int)
        
        # ML models and predictions
        self.engagement_predictor = None
        self.churn_predictor = None
        self.content_optimizer = None
        
        # Analytics caches
        self.trending_content: List[Dict] = []
        self.engagement_insights: Dict[str, Any] = {}
        
        # Performance metrics
        self.service_metrics = {
            'events_processed': 0,
            'analytics_generated': 0,
            'predictions_made': 0,
            'insights_delivered': 0,
            'processing_latency': 0.0
        }
        
        logger.info("Engagement Analytics Service initialized")
    
    async def initialize(self) -> None:
        """Initialize Redis connection and analytics models"""
        try:
            self.redis_client = redis.from_url(self.redis_url)
            await self.redis_client.ping()
            
            # Initialize ML models
            await self._initialize_ml_models()
            
            # Load historical data for warm-up
            await self._load_historical_data()
            
            # Start background analytics processors
            asyncio.create_task(self._process_engagement_events())
            asyncio.create_task(self._generate_real_time_insights())
            asyncio.create_task(self._update_trending_content())
            
            logger.info("Engagement Analytics Service initialization complete")
            
        except Exception as e:
            logger.error(f"Failed to initialize Engagement Analytics Service: {e}")
            raise
    
    async def track_engagement(self, event_data: Dict[str, Any]) -> bool:
        """Track an engagement event with real-time processing"""
        try:
            start_time = time.time()
            
            # Create engagement event
            event = EngagementEvent(
                id=str(uuid.uuid4()),
                user_id=event_data["user_id"],
                content_id=event_data["content_id"],
                creator_id=event_data["creator_id"],
                engagement_type=EngagementType(event_data["engagement_type"]),
                content_type=ContentType(event_data["content_type"]),
                channel=EngagementChannel(event_data.get("channel", "platform_native")),
                timestamp=datetime.now(),
                value=event_data.get("value", 1.0),
                session_id=event_data.get("session_id"),
                metadata=event_data.get("metadata", {})
            )
            
            # Add to events buffer
            self.engagement_events.append(event)
            
            # Update real-time counters
            await self._update_real_time_counters(event)
            
            # Track active sessions
            await self._track_session(event)
            
            # Store in Redis for persistence
            await self._store_event_to_redis(event)
            
            # Trigger real-time analytics update
            asyncio.create_task(self._process_event_analytics(event))
            
            # Update service metrics
            self.service_metrics['events_processed'] += 1
            self.service_metrics['processing_latency'] = time.time() - start_time
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to track engagement event: {e}")
            return False
    
    async def _update_real_time_counters(self, event -> None: EngagementEvent) -> None:
        """Update real-time engagement counters"""
        try:
            # Update content-specific counters
            content_key = f"content:{event.content_id}"
            self.real_time_counters[f"{content_key}:{event.engagement_type.value}"] += 1
            self.real_time_counters[f"{content_key}:total"] += 1
            
            # Update creator-specific counters
            creator_key = f"creator:{event.creator_id}"
            self.real_time_counters[f"{creator_key}:{event.engagement_type.value}"] += 1
            self.real_time_counters[f"{creator_key}:total"] += 1
            
            # Update platform-wide counters
            platform_key = "platform"
            self.real_time_counters[f"{platform_key}:{event.engagement_type.value}"] += 1
            self.real_time_counters[f"{platform_key}:total"] += 1
            
            # Update channel-specific counters
            channel_key = f"channel:{event.channel.value}"
            self.real_time_counters[f"{channel_key}:{event.engagement_type.value}"] += 1
            
        except Exception as e:
            logger.error(f"Failed to update real-time counters: {e}")
    
    async def _track_session(self, event -> None: EngagementEvent) -> None:
        """Track user session for engagement analysis"""
        try:
            session_id = event.session_id or f"{event.user_id}:{event.timestamp.date()}"
            
            if session_id not in self.active_sessions:
                self.active_sessions[session_id] = {
                    'user_id': event.user_id,
                    'start_time': event.timestamp,
                    'last_activity': event.timestamp,
                    'events': [],
                    'content_engaged': set(),
                    'engagement_score': 0.0
                }
            
            session = self.active_sessions[session_id]
            session['last_activity'] = event.timestamp
            session['events'].append(event)
            session['content_engaged'].add(event.content_id)
            
            # Calculate engagement score
            engagement_weights = {
                EngagementType.VIEW: 1.0,
                EngagementType.LIKE: 2.0,
                EngagementType.COMMENT: 3.0,
                EngagementType.SHARE: 4.0,
                EngagementType.DOWNLOAD: 3.0,
                EngagementType.FOLLOW: 5.0,
                EngagementType.REPLAY: 2.5
            }
            
            weight = engagement_weights.get(event.engagement_type, 1.0)
            session['engagement_score'] += weight * event.value
            
        except Exception as e:
            logger.error(f"Failed to track session: {e}")
    
    async def _process_event_analytics(self, event -> None: EngagementEvent) -> None:
        """Process individual event for immediate analytics updates"""
        try:
            # Update content analytics
            content_analytics = self.content_analytics[event.content_id]
            
            if 'hourly_metrics' not in content_analytics:
                content_analytics['hourly_metrics'] = defaultdict(int)
            
            hour_key = event.timestamp.strftime("%Y-%m-%d-%H")
            content_analytics['hourly_metrics'][f"{hour_key}:{event.engagement_type.value}"] += 1
            
            # Update user engagement profile
            await self._update_user_profile(event)
            
            # Check for trending potential
            await self._check_trending_potential(event)
            
            # Update aggregated metrics
            await self._update_aggregated_metrics(event)
            
        except Exception as e:
            logger.error(f"Failed to process event analytics: {e}")
    
    async def _update_user_profile(self, event -> None: EngagementEvent) -> None:
        """Update user engagement profile with new event"""
        try:
            if event.user_id not in self.user_profiles:
                self.user_profiles[event.user_id] = UserEngagementProfile(
                    user_id=event.user_id,
                    preferred_content_types=[],
                    preferred_channels=[],
                    peak_activity_hours=[],
                    engagement_consistency=0.0,
                    total_engagements=0,
                    average_session_duration=0.0,
                    content_discovery_rate=0.0,
                    creator_loyalty_score=0.0
                )
            
            profile = self.user_profiles[event.user_id]
            profile.total_engagements += 1
            
            # Update preferred content types
            content_type = event.content_type.value
            if content_type not in profile.preferred_content_types:
                profile.preferred_content_types.append(content_type)
            
            # Update preferred channels
            channel = event.channel.value
            if channel not in profile.preferred_channels:
                profile.preferred_channels.append(channel)
            
            # Update peak activity hours
            hour = event.timestamp.hour
            if hour not in profile.peak_activity_hours:
                profile.peak_activity_hours.append(hour)
            
            # Predict next engagement using ML
            profile.next_engagement_prediction = await self._predict_next_engagement(profile)
            
        except Exception as e:
            logger.error(f"Failed to update user profile: {e}")
    
    async def _check_trending_potential(self, event -> None: EngagementEvent) -> None:
        """Check if content has trending potential based on engagement velocity"""
        try:
            content_id = event.content_id
            
            # Get recent engagement velocity (last hour)
            current_hour = event.timestamp.replace(minute=0, second=0, microsecond=0)
            hour_key = f"content:{content_id}:velocity:{current_hour.isoformat()}"
            
            # Increment velocity counter
            if self.redis_client:
                await self.redis_client.incr(hour_key)
                await self.redis_client.expire(hour_key, 7200)  # 2 hours TTL
                
                # Get velocity for trending detection
                velocity = await self.redis_client.get(hour_key)
                velocity = int(velocity) if velocity else 0
                
                # Check trending thresholds
                if velocity >= 50:  # High engagement threshold
                    await self._mark_as_trending(content_id, velocity)
            
        except Exception as e:
            logger.error(f"Failed to check trending potential: {e}")
    
    async def _mark_as_trending(self, content_id -> None: str, velocity -> None: int) -> None:
        """Mark content as trending and update trending lists"""
        try:
            # Add to trending content list
            trending_item = {
                'content_id': content_id,
                'velocity': velocity,
                'timestamp': datetime.now().isoformat(),
                'trend_score': velocity * 1.5  # Weighted trend score
            }
            
            # Update trending list (keep top 100)
            self.trending_content.append(trending_item)
            self.trending_content.sort(key=lambda x: x['trend_score'], reverse=True)
            self.trending_content = self.trending_content[:100]
            
            # Store in Redis for cross-service access
            if self.redis_client:
                await self.redis_client.zadd(
                    "trending_content",
                    {content_id: trending_item['trend_score']}
                )
                await self.redis_client.expire("trending_content", 3600)  # 1 hour TTL
            
            logger.info(f"Content {content_id} marked as trending with velocity {velocity}")
            
        except Exception as e:
            logger.error(f"Failed to mark content as trending: {e}")
    
    async def get_engagement_analytics(self, content_id: Optional[str] = None,
                                     creator_id: Optional[str] = None,
                                     timeframe: AnalyticsTimeframe = AnalyticsTimeframe.DAILY,
                                     start_date: Optional[datetime] = None,
                                     end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """Get comprehensive engagement analytics"""
        try:
            analytics_start_time = time.time()
            
            # Set default date range if not provided
            if not end_date:
                end_date = datetime.now()
            if not start_date:
                if timeframe == AnalyticsTimeframe.DAILY:
                    start_date = end_date - timedelta(days=7)
                elif timeframe == AnalyticsTimeframe.WEEKLY:
                    start_date = end_date - timedelta(weeks=4)
                elif timeframe == AnalyticsTimeframe.MONTHLY:
                    start_date = end_date - timedelta(days=90)
                else:
                    start_date = end_date - timedelta(days=1)
            
            # Filter events based on criteria
            filtered_events = self._filter_events(
                content_id=content_id,
                creator_id=creator_id,
                start_date=start_date,
                end_date=end_date
            )
            
            if not filtered_events:
                return {"error": "No engagement data found for the specified criteria"}
            
            # Generate analytics
            analytics = {
                "timeframe": timeframe.value,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "summary": await self._generate_summary_analytics(filtered_events),
                "engagement_breakdown": await self._generate_engagement_breakdown(filtered_events),
                "temporal_analysis": await self._generate_temporal_analysis(filtered_events, timeframe),
                "user_analytics": await self._generate_user_analytics(filtered_events),
                "content_performance": await self._generate_content_performance(filtered_events),
                "channel_analysis": await self._generate_channel_analysis(filtered_events),
                "predictions": await self._generate_predictions(filtered_events),
                "recommendations": await self._generate_recommendations(filtered_events)
            }
            
            # Add specific analytics if single content/creator
            if content_id:
                analytics["content_specific"] = await self._generate_content_specific_analytics(content_id)
            
            if creator_id:
                analytics["creator_specific"] = await self._generate_creator_specific_analytics(creator_id)
            
            # Update service metrics
            self.service_metrics['analytics_generated'] += 1
            self.service_metrics['processing_latency'] = time.time() - analytics_start_time
            
            return analytics
            
        except Exception as e:
            logger.error(f"Failed to get engagement analytics: {e}")
            return {"error": str(e)}
    
    def _filter_events(self, content_id: Optional[str] = None,
                      creator_id: Optional[str] = None,
                      start_date: Optional[datetime] = None,
                      end_date: Optional[datetime] = None) -> List[EngagementEvent]:
        """Filter engagement events based on criteria"""
        filtered_events = []
        
        for event in self.engagement_events:
            # Check date range
            if start_date and event.timestamp < start_date:
                continue
            if end_date and event.timestamp > end_date:
                continue
            
            # Check content filter
            if content_id and event.content_id != content_id:
                continue
            
            # Check creator filter
            if creator_id and event.creator_id != creator_id:
                continue
            
            filtered_events.append(event)
        
        return filtered_events
    
    async def _generate_summary_analytics(self, events: List[EngagementEvent]) -> Dict[str, Any]:
        """Generate summary analytics from events"""
        try:
            if not events:
                return {}
            
            # Basic counts
            total_events = len(events)
            unique_users = len(set(event.user_id for event in events))
            unique_content = len(set(event.content_id for event in events))
            unique_creators = len(set(event.creator_id for event in events))
            
            # Engagement type breakdown
            type_counts = defaultdict(int)
            for event in events:
                type_counts[event.engagement_type.value] += 1
            
            # Calculate engagement rates
            views = type_counts.get("view", 0)
            likes = type_counts.get("like", 0)
            comments = type_counts.get("comment", 0)
            shares = type_counts.get("share", 0)
            
            like_rate = (likes / max(views, 1)) * 100
            comment_rate = (comments / max(views, 1)) * 100
            share_rate = (shares / max(views, 1)) * 100
            engagement_rate = ((likes + comments + shares) / max(views, 1)) * 100
            
            return {
                "total_events": total_events,
                "unique_users": unique_users,
                "unique_content": unique_content,
                "unique_creators": unique_creators,
                "engagement_types": dict(type_counts),
                "engagement_rates": {
                    "like_rate": round(like_rate, 2),
                    "comment_rate": round(comment_rate, 2),
                    "share_rate": round(share_rate, 2),
                    "overall_engagement_rate": round(engagement_rate, 2)
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to generate summary analytics: {e}")
            return {}
    
    async def _generate_engagement_breakdown(self, events: List[EngagementEvent]) -> Dict[str, Any]:
        """Generate detailed engagement breakdown"""
        try:
            breakdown = {
                "by_content_type": defaultdict(int),
                "by_channel": defaultdict(int),
                "by_engagement_type": defaultdict(int),
                "by_hour": defaultdict(int),
                "by_day": defaultdict(int)
            }
            
            for event in events:
                breakdown["by_content_type"][event.content_type.value] += 1
                breakdown["by_channel"][event.channel.value] += 1
                breakdown["by_engagement_type"][event.engagement_type.value] += 1
                breakdown["by_hour"][event.timestamp.hour] += 1
                breakdown["by_day"][event.timestamp.strftime("%A")] += 1
            
            # Convert defaultdicts to regular dicts
            return {key: dict(value) for key, value in breakdown.items()}
            
        except Exception as e:
            logger.error(f"Failed to generate engagement breakdown: {e}")
            return {}
    
    async def _generate_temporal_analysis(self, events: List[EngagementEvent],
                                        timeframe: AnalyticsTimeframe) -> Dict[str, Any]:
        """Generate temporal engagement analysis"""
        try:
            temporal_data = defaultdict(int)
            
            for event in events:
                if timeframe == AnalyticsTimeframe.HOURLY:
                    key = event.timestamp.strftime("%Y-%m-%d %H:00")
                elif timeframe == AnalyticsTimeframe.DAILY:
                    key = event.timestamp.strftime("%Y-%m-%d")
                elif timeframe == AnalyticsTimeframe.WEEKLY:
                    # Get week start (Monday)
                    week_start = event.timestamp - timedelta(days=event.timestamp.weekday())
                    key = week_start.strftime("%Y-W%W")
                elif timeframe == AnalyticsTimeframe.MONTHLY:
                    key = event.timestamp.strftime("%Y-%m")
                else:
                    key = event.timestamp.strftime("%Y-%m-%d %H:%M")
                
                temporal_data[key] += 1
            
            # Calculate trends
            values = list(temporal_data.values())
            if len(values) > 1:
                trend_direction = "increasing" if values[-1] > values[0] else "decreasing"
                trend_strength = abs(values[-1] - values[0]) / max(values[0], 1)
            else:
                trend_direction = "stable"
                trend_strength = 0.0
            
            return {
                "temporal_data": dict(temporal_data),
                "trend_analysis": {
                    "direction": trend_direction,
                    "strength": round(trend_strength, 2),
                    "peak_period": max(temporal_data.keys(), key=lambda k: temporal_data[k]) if temporal_data else None
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to generate temporal analysis: {e}")
            return {}
    
    async def _generate_user_analytics(self, events: List[EngagementEvent]) -> Dict[str, Any]:
        """Generate user behavior analytics"""
        try:
            user_engagement = defaultdict(int)
            user_sessions = defaultdict(set)
            user_content = defaultdict(set)
            
            for event in events:
                user_engagement[event.user_id] += 1
                if event.session_id:
                    user_sessions[event.user_id].add(event.session_id)
                user_content[event.user_id].add(event.content_id)
            
            # Calculate user metrics
            total_users = len(user_engagement)
            avg_engagements_per_user = statistics.mean(user_engagement.values()) if user_engagement else 0
            avg_content_per_user = statistics.mean([len(content) for content in user_content.values()]) if user_content else 0
            
            # Find power users (top 10% by engagement)
            sorted_users = sorted(user_engagement.items(), key=lambda x: x[1], reverse=True)
            power_user_threshold = int(total_users * 0.1) if total_users > 10 else total_users
            power_users = sorted_users[:power_user_threshold]
            
            return {
                "total_users": total_users,
                "average_engagements_per_user": round(avg_engagements_per_user, 2),
                "average_content_per_user": round(avg_content_per_user, 2),
                "power_users": [{"user_id": user_id, "engagements": count} for user_id, count in power_users[:10]],
                "user_distribution": {
                    "high_engagement": len([u for u in user_engagement.values() if u > avg_engagements_per_user * 2]),
                    "medium_engagement": len([u for u in user_engagement.values() if avg_engagements_per_user <= u <= avg_engagements_per_user * 2]),
                    "low_engagement": len([u for u in user_engagement.values() if u < avg_engagements_per_user])
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to generate user analytics: {e}")
            return {}
    
    async def _generate_content_performance(self, events: List[EngagementEvent]) -> Dict[str, Any]:
        """Generate content performance analytics"""
        try:
            content_metrics = defaultdict(lambda: defaultdict(int))
            
            for event in events:
                content_metrics[event.content_id]["total_engagements"] += 1
                content_metrics[event.content_id][event.engagement_type.value] += 1
                content_metrics[event.content_id]["unique_users"] = len(set(
                    e.user_id for e in events if e.content_id == event.content_id
                ))
            
            # Calculate performance scores
            performance_data = []
            for content_id, metrics in content_metrics.items():
                views = metrics.get("view", 0)
                likes = metrics.get("like", 0)
                comments = metrics.get("comment", 0)
                shares = metrics.get("share", 0)
                
                # Calculate engagement score
                engagement_score = (likes * 2 + comments * 3 + shares * 4) / max(views, 1)
                
                performance_data.append({
                    "content_id": content_id,
                    "total_engagements": metrics["total_engagements"],
                    "unique_users": metrics["unique_users"],
                    "engagement_score": round(engagement_score, 2),
                    "metrics": dict(metrics)
                })
            
            # Sort by engagement score
            performance_data.sort(key=lambda x: x["engagement_score"], reverse=True)
            
            return {
                "top_performing_content": performance_data[:10],
                "performance_distribution": {
                    "high_performance": len([c for c in performance_data if c["engagement_score"] > 5.0]),
                    "medium_performance": len([c for c in performance_data if 2.0 <= c["engagement_score"] <= 5.0]),
                    "low_performance": len([c for c in performance_data if c["engagement_score"] < 2.0])
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to generate content performance analytics: {e}")
            return {}
    
    async def _generate_channel_analysis(self, events: List[EngagementEvent]) -> Dict[str, Any]:
        """Generate channel performance analysis"""
        try:
            channel_metrics = defaultdict(lambda: defaultdict(int))
            
            for event in events:
                channel = event.channel.value
                channel_metrics[channel]["total_engagements"] += 1
                channel_metrics[channel][event.engagement_type.value] += 1
                channel_metrics[channel]["unique_users"] = len(set(
                    e.user_id for e in events if e.channel.value == channel
                ))
            
            # Calculate channel effectiveness
            channel_analysis = []
            for channel, metrics in channel_metrics.items():
                total_engagements = metrics["total_engagements"]
                unique_users = metrics["unique_users"]
                
                # Calculate engagement rate per user
                engagement_per_user = total_engagements / max(unique_users, 1)
                
                channel_analysis.append({
                    "channel": channel,
                    "total_engagements": total_engagements,
                    "unique_users": unique_users,
                    "engagement_per_user": round(engagement_per_user, 2),
                    "metrics": dict(metrics)
                })
            
            # Sort by engagement per user
            channel_analysis.sort(key=lambda x: x["engagement_per_user"], reverse=True)
            
            return {
                "channel_performance": channel_analysis,
                "most_effective_channel": channel_analysis[0]["channel"] if channel_analysis else None,
                "channel_distribution": {channel["channel"]: channel["total_engagements"] for channel in channel_analysis}
            }
            
        except Exception as e:
            logger.error(f"Failed to generate channel analysis: {e}")
            return {}
    
    async def _generate_predictions(self, events: List[EngagementEvent]) -> Dict[str, Any]:
        """Generate engagement predictions using ML models"""
        try:
            predictions = {}
            
            # Predict next hour engagement
            if len(events) >= 24:  # Need at least 24 hours of data
                hourly_counts = defaultdict(int)
                for event in events[-24:]:  # Last 24 events
                    hour = event.timestamp.hour
                    hourly_counts[hour] += 1
                
                current_hour = datetime.now().hour
                next_hour = (current_hour + 1) % 24
                
                # Simple prediction based on historical pattern
                avg_for_hour = statistics.mean([hourly_counts[h] for h in range(24)])
                next_hour_historical = hourly_counts.get(next_hour, avg_for_hour)
                
                # Apply trend factor
                recent_trend = len([e for e in events if e.timestamp > datetime.now() - timedelta(hours=1)])
                trend_factor = max(0.5, min(2.0, recent_trend / avg_for_hour)) if avg_for_hour > 0 else 1.0
                
                predicted_next_hour = int(next_hour_historical * trend_factor)
                
                predictions["next_hour_engagement"] = {
                    "predicted_events": predicted_next_hour,
                    "confidence": min(0.9, len(events) / 1000),  # Higher confidence with more data
                    "trend_factor": round(trend_factor, 2)
                }
            
            # Predict viral potential
            if events:
                recent_velocity = len([e for e in events if e.timestamp > datetime.now() - timedelta(minutes=30)])
                viral_threshold = 20  # Events per 30 minutes
                viral_probability = min(1.0, recent_velocity / viral_threshold)
                
                predictions["viral_potential"] = {
                    "probability": round(viral_probability, 2),
                    "current_velocity": recent_velocity,
                    "threshold": viral_threshold
                }
            
            # Content lifecycle prediction
            if events:
                # Simple lifecycle stage based on engagement pattern
                event_timeline = sorted(events, key=lambda x: x.timestamp)
                if len(event_timeline) > 10:
                    early_engagements = len(event_timeline[:len(event_timeline)//3])
                    late_engagements = len(event_timeline[-len(event_timeline)//3:])
                    
                    if late_engagements > early_engagements * 1.5:
                        lifecycle_stage = "growing"
                    elif late_engagements < early_engagements * 0.5:
                        lifecycle_stage = "declining"
                    else:
                        lifecycle_stage = "stable"
                    
                    predictions["content_lifecycle"] = {
                        "stage": lifecycle_stage,
                        "early_engagement": early_engagements,
                        "late_engagement": late_engagements
                    }
            
            return predictions
            
        except Exception as e:
            logger.error(f"Failed to generate predictions: {e}")
            return {}
    
    async def _generate_recommendations(self, events: List[EngagementEvent]) -> Dict[str, Any]:
        """Generate AI-powered optimization recommendations"""
        try:
            recommendations = []
            
            if not events:
                return {"recommendations": []}
            
            # Analyze engagement patterns for recommendations
            
            # 1. Peak time recommendation
            hourly_engagement = defaultdict(int)
            for event in events:
                hourly_engagement[event.timestamp.hour] += 1
            
            if hourly_engagement:
                peak_hour = max(hourly_engagement.keys(), key=lambda h: hourly_engagement[h])
                recommendations.append({
                    "type": "optimal_posting_time",
                    "recommendation": f"Post content around {peak_hour}:00 for maximum engagement",
                    "confidence": 0.8,
                    "data": {"peak_hour": peak_hour, "peak_engagement": hourly_engagement[peak_hour]}
                })
            
            # 2. Content type recommendation
            content_performance = defaultdict(list)
            for event in events:
                if event.engagement_type == EngagementType.LIKE:
                    content_performance[event.content_type.value].append(1)
            
            if content_performance:
                best_content_type = max(content_performance.keys(), 
                                      key=lambda ct: len(content_performance[ct]))
                recommendations.append({
                    "type": "content_type_optimization",
                    "recommendation": f"Focus on {best_content_type} content for better engagement",
                    "confidence": 0.7,
                    "data": {"best_type": best_content_type, "engagement_count": len(content_performance[best_content_type])}
                })
            
            # 3. Channel optimization
            channel_performance = defaultdict(int)
            for event in events:
                channel_performance[event.channel.value] += 1
            
            if channel_performance:
                best_channel = max(channel_performance.keys(), key=lambda c: channel_performance[c])
                recommendations.append({
                    "type": "channel_optimization",
                    "recommendation": f"Increase activity on {best_channel} for better reach",
                    "confidence": 0.6,
                    "data": {"best_channel": best_channel, "engagement_count": channel_performance[best_channel]}
                })
            
            # 4. Engagement rate improvement
            views = len([e for e in events if e.engagement_type == EngagementType.VIEW])
            likes = len([e for e in events if e.engagement_type == EngagementType.LIKE])
            
            if views > 0:
                like_rate = (likes / views) * 100
                if like_rate < 5.0:  # Below 5% like rate
                    recommendations.append({
                        "type": "engagement_improvement",
                        "recommendation": "Consider adding more engaging call-to-actions to improve like rate",
                        "confidence": 0.7,
                        "data": {"current_like_rate": round(like_rate, 2), "target_rate": 8.0}
                    })
            
            return {"recommendations": recommendations}
            
        except Exception as e:
            logger.error(f"Failed to generate recommendations: {e}")
            return {"recommendations": []}
    
    async def get_real_time_metrics(self) -> Dict[str, Any]:
        """Get real-time engagement metrics dashboard"""
        try:
            current_time = datetime.now()
            
            # Get metrics for the last hour
            recent_events = [
                event for event in self.engagement_events 
                if event.timestamp > current_time - timedelta(hours=1)
            ]
            
            # Calculate real-time metrics
            metrics = {
                "timestamp": current_time.isoformat(),
                "last_hour": {
                    "total_events": len(recent_events),
                    "unique_users": len(set(event.user_id for event in recent_events)),
                    "top_content": self._get_top_content_last_hour(recent_events),
                    "engagement_velocity": len(recent_events) / 60  # Events per minute
                },
                "active_sessions": len(self.active_sessions),
                "trending_content": self.trending_content[:10],
                "platform_metrics": {
                    "total_events_today": len([
                        event for event in self.engagement_events 
                        if event.timestamp.date() == current_time.date()
                    ]),
                    "events_per_second": len(recent_events) / 3600  # Last hour average
                },
                "service_health": {
                    "events_processed": self.service_metrics['events_processed'],
                    "processing_latency": self.service_metrics['processing_latency'],
                    "buffer_size": len(self.engagement_events)
                }
            }
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to get real-time metrics: {e}")
            return {"error": str(e)}
    
    def _get_top_content_last_hour(self, recent_events: List[EngagementEvent]) -> List[Dict[str, Any]]:
        """Get top performing content in the last hour"""
        content_counts = defaultdict(int)
        for event in recent_events:
            content_counts[event.content_id] += 1
        
        sorted_content = sorted(content_counts.items(), key=lambda x: x[1], reverse=True)
        
        return [
            {"content_id": content_id, "engagements": count}
            for content_id, count in sorted_content[:5]
        ]
    
    async def _process_engagement_events(self) -> None:
        """Background task to process engagement events"""
        while True:
            try:
                await asyncio.sleep(10)  # Process every 10 seconds
                
                # Process recent events for aggregation
                if self.engagement_events:
                    # Update aggregated metrics
                    await self._update_hourly_aggregations()
                    
                    # Clean up old active sessions
                    await self._cleanup_inactive_sessions()
                
            except Exception as e:
                logger.error(f"Error in engagement events processing: {e}")
                await asyncio.sleep(30)  # Wait longer on error
    
    async def _generate_real_time_insights(self) -> None:
        """Background task to generate real-time insights"""
        while True:
            try:
                await asyncio.sleep(60)  # Generate insights every minute
                
                # Update engagement insights
                self.engagement_insights = await self._calculate_real_time_insights()
                
                # Update service metrics
                self.service_metrics['insights_delivered'] += 1
                
            except Exception as e:
                logger.error(f"Error generating real-time insights: {e}")
                await asyncio.sleep(120)  # Wait longer on error
    
    async def _update_trending_content(self) -> None:
        """Background task to update trending content"""
        while True:
            try:
                await asyncio.sleep(300)  # Update every 5 minutes
                
                # Decay trending scores
                for item in self.trending_content:
                    item['trend_score'] *= 0.95  # 5% decay per update
                
                # Remove low-scoring items
                self.trending_content = [
                    item for item in self.trending_content 
                    if item['trend_score'] > 1.0
                ]
                
            except Exception as e:
                logger.error(f"Error updating trending content: {e}")
                await asyncio.sleep(600)  # Wait longer on error
    
    async def _calculate_real_time_insights(self) -> Dict[str, Any]:
        """Calculate real-time engagement insights"""
        try:
            current_time = datetime.now()
            last_15_min = current_time - timedelta(minutes=15)
            
            recent_events = [
                event for event in self.engagement_events 
                if event.timestamp > last_15_min
            ]
            
            if not recent_events:
                return {}
            
            insights = {
                "engagement_spike": len(recent_events) > 100,  # Threshold for spike detection
                "dominant_content_type": max(
                    set(event.content_type.value for event in recent_events),
                    key=lambda ct: len([e for e in recent_events if e.content_type.value == ct])
                ),
                "user_activity_level": "high" if len(set(event.user_id for event in recent_events)) > 50 else "normal",
                "viral_content_detected": any(item['trend_score'] > 100 for item in self.trending_content[:5])
            }
            
            return insights
            
        except Exception as e:
            logger.error(f"Failed to calculate real-time insights: {e}")
            return {}
    
    async def _predict_next_engagement(self, profile: UserEngagementProfile) -> Optional[datetime]:
        """Predict when user will next engage (placeholder for ML model)"""
        try:
            # Simple prediction based on user patterns
            if profile.peak_activity_hours:
                # Find next peak hour
                current_hour = datetime.now().hour
                next_peak = min([h for h in profile.peak_activity_hours if h > current_hour], 
                              default=min(profile.peak_activity_hours))
                
                # Calculate prediction time
                if next_peak > current_hour:
                    prediction_time = datetime.now().replace(hour=next_peak, minute=0, second=0)
                else:
                    prediction_time = datetime.now().replace(hour=next_peak, minute=0, second=0) + timedelta(days=1)
                
                return prediction_time
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to predict next engagement: {e}")
            return None
    
    async def _store_event_to_redis(self, event -> None: EngagementEvent) -> None:
        """Store engagement event to Redis for persistence"""
        try:
            if self.redis_client:
                event_data = {
                    'id': event.id,
                    'user_id': event.user_id,
                    'content_id': event.content_id,
                    'creator_id': event.creator_id,
                    'engagement_type': event.engagement_type.value,
                    'content_type': event.content_type.value,
                    'channel': event.channel.value,
                    'timestamp': event.timestamp.isoformat(),
                    'value': event.value,
                    'session_id': event.session_id or '',
                    'metadata': json.dumps(event.metadata)
                }
                
                # Store in time-series format
                await self.redis_client.hset(f"engagement_event:{event.id}", mapping=event_data)
                
                # Add to time-based sorted sets for efficient querying
                timestamp_score = event.timestamp.timestamp()
                await self.redis_client.zadd(f"events_by_content:{event.content_id}", {event.id: timestamp_score})
                await self.redis_client.zadd(f"events_by_user:{event.user_id}", {event.id: timestamp_score})
                await self.redis_client.zadd("events_global", {event.id: timestamp_score})
                
                # Set TTL for automatic cleanup (30 days)
                await self.redis_client.expire(f"engagement_event:{event.id}", 2592000)
                
        except Exception as e:
            logger.error(f"Failed to store event to Redis: {e}")
    
    async def _load_historical_data(self) -> None:
        """Load historical engagement data for analysis"""
        try:
            if self.redis_client:
                # Load recent events from Redis
                event_keys = await self.redis_client.keys("engagement_event:*")
                
                for key in event_keys[:1000]:  # Load up to 1000 recent events
                    event_data = await self.redis_client.hgetall(key)
                    if event_data:
                        # Reconstruct engagement event
                        # Implementation details would depend on Redis data format
                        pass
                        
        except Exception as e:
            logger.error(f"Failed to load historical data: {e}")
    
    async def _initialize_ml_models(self) -> None:
        """Initialize machine learning models for analytics"""
        try:
            # Placeholder for ML model initialization
            # In production, this would load actual trained models
            self.engagement_predictor = "engagement_prediction_model"
            self.churn_predictor = "churn_prediction_model"
            self.content_optimizer = "content_optimization_model"
            
            logger.info("ML models initialized for engagement analytics")
            
        except Exception as e:
            logger.error(f"Failed to initialize ML models: {e}")
    
    async def shutdown(self) -> None:
        """Graceful shutdown of engagement analytics service"""
        try:
            if self.redis_client:
                await self.redis_client.close()
            
            self.executor.shutdown(wait=True)
            logger.info("Engagement Analytics Service shutdown complete")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")

# Example usage and testing
async def main() -> None:
    """Example usage of Engagement Analytics Service"""
    service = EngagementAnalyticsService()
    await service.initialize()
    
    try:
        # Track sample engagement events
        sample_events = [
            {
                "user_id": "user_123",
                "content_id": "content_456",
                "creator_id": "creator_789",
                "engagement_type": "view",
                "content_type": "music",
                "channel": "spotify",
                "value": 1.0,
                "metadata": {"duration": 180}
            },
            {
                "user_id": "user_124",
                "content_id": "content_456",
                "creator_id": "creator_789",
                "engagement_type": "like",
                "content_type": "music",
                "channel": "spotify",
                "value": 1.0
            },
            {
                "user_id": "user_125",
                "content_id": "content_457",
                "creator_id": "creator_790",
                "engagement_type": "share",
                "content_type": "video",
                "channel": "youtube",
                "value": 1.0
            }
        ]
        
        for event_data in sample_events:
            await service.track_engagement(event_data)
            print(f"Tracked engagement: {event_data['engagement_type']}")
        
        # Get analytics
        analytics = await service.get_engagement_analytics()
        print(f"Engagement analytics: {analytics}")
        
        # Get real-time metrics
        real_time = await service.get_real_time_metrics()
        print(f"Real-time metrics: {real_time}")
        
    finally:
        await service.shutdown()

if __name__ == "__main__":
    asyncio.run(main())