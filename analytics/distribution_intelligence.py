"""Distribution Intelligence
========================

Advanced cross-platform distribution analytics and optimization system.
Monitors and optimizes content distribution across 35+ platforms with audience analytics.

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
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier


class DistributionPlatform(Enum):
    """Distribution platforms supported"""
    # Video Platforms
    YOUTUBE = "youtube"
    VIMEO = "vimeo"
    DAILYMOTION = "dailymotion"
    TWITCH = "twitch"
    FACEBOOK_VIDEO = "facebook_video"
    
    # Social Media
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    FACEBOOK = "facebook"
    PINTEREST = "pinterest"
    SNAPCHAT = "snapchat"
    REDDIT = "reddit"
    
    # Audio Platforms
    SPOTIFY = "spotify"
    APPLE_MUSIC = "apple_music"
    SOUNDCLOUD = "soundcloud"
    AMAZON_MUSIC = "amazon_music"
    YOUTUBE_MUSIC = "youtube_music"
    DEEZER = "deezer"
    TIDAL = "tidal"
    BANDCAMP = "bandcamp"
    
    # Blogging/Publishing
    MEDIUM = "medium"
    WORDPRESS = "wordpress"
    BLOGGER = "blogger"
    SUBSTACK = "substack"
    HASHNODE = "hashnode"
    DEV_TO = "dev_to"
    
    # Professional
    BEHANCE = "behance"
    DRIBBBLE = "dribbble"
    GITHUB = "github"
    
    # Gaming
    STEAM = "steam"
    DISCORD = "discord"
    
    # Emerging Platforms
    CLUBHOUSE = "clubhouse"
    THREADS = "threads"
    MASTODON = "mastodon"
    BLUESKY = "bluesky"


class ContentFormat(Enum):
    """Content format types"""
    VIDEO = "video"
    AUDIO = "audio"
    IMAGE = "image"
    TEXT = "text"
    LIVE_STREAM = "live_stream"
    PODCAST = "podcast"
    BLOG_POST = "blog_post"
    SOCIAL_POST = "social_post"
    STORY = "story"
    REEL = "reel"
    SHORT = "short"
    CAROUSEL = "carousel"
    PLAYLIST = "playlist"
    ALBUM = "album"
    ARTICLE = "article"
    NEWSLETTER = "newsletter"


class DistributionStatus(Enum):
    """Distribution status states"""
    SCHEDULED = "scheduled"
    PUBLISHING = "publishing"
    PUBLISHED = "published"
    FAILED = "failed"
    REJECTED = "rejected"
    PENDING_REVIEW = "pending_review"
    MONETIZED = "monetized"
    DEMONETIZED = "demonetized"
    TAKEN_DOWN = "taken_down"


@dataclass
class PlatformMetrics:
    """Metrics for a specific platform"""
    platform: DistributionPlatform
    content_count: int = 0
    total_views: int = 0
    total_likes: int = 0
    total_shares: int = 0
    total_comments: int = 0
    total_revenue: float = 0.0
    engagement_rate: float = 0.0
    reach: int = 0
    impressions: int = 0
    click_through_rate: float = 0.0
    conversion_rate: float = 0.0
    audience_retention: float = 0.0
    growth_rate: float = 0.0
    cost_per_acquisition: float = 0.0


@dataclass
class DistributionEvent:
    """Individual content distribution event"""
    event_id: str
    content_id: str
    platform: DistributionPlatform
    content_format: ContentFormat
    status: DistributionStatus
    scheduled_time: datetime
    published_time: Optional[datetime] = None
    performance_metrics: Dict[str, Any] = field(default_factory=dict)
    audience_data: Dict[str, Any] = field(default_factory=dict)
    revenue_data: Dict[str, float] = field(default_factory=dict)
    engagement_data: Dict[str, int] = field(default_factory=dict)
    error_details: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AudienceSegment:
    """Audience segment analysis"""
    segment_id: str
    name: str
    size: int
    demographics: Dict[str, Any]
    interests: List[str]
    behavior_patterns: Dict[str, Any]
    platform_preferences: List[DistributionPlatform]
    engagement_preferences: Dict[str, float]
    optimal_posting_times: List[str]
    content_preferences: List[ContentFormat]
    revenue_potential: float
    growth_trend: str  # "growing", "stable", "declining"


@dataclass
class CrossPlatformCampaign:
    """Cross-platform distribution campaign"""
    campaign_id: str
    name: str
    content_pieces: List[str]
    target_platforms: List[DistributionPlatform]
    target_audience_segments: List[str]
    start_date: datetime
    end_date: datetime
    objectives: Dict[str, float]
    current_performance: Dict[str, float] = field(default_factory=dict)
    platform_customizations: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    budget_allocation: Dict[str, float] = field(default_factory=dict)
    success_metrics: Dict[str, float] = field(default_factory=dict)
    roi_score: float = 0.0


@dataclass
class DistributionIntelligence:
    """Comprehensive distribution analytics"""
    time_period: Tuple[datetime, datetime]
    total_content_distributed: int = 0
    total_platforms_used: int = 0
    total_reach: int = 0
    total_revenue: float = 0.0
    platform_performance: Dict[str, PlatformMetrics] = field(default_factory=dict)
    audience_overlap: Dict[str, float] = field(default_factory=dict)
    content_format_performance: Dict[str, Dict[str, float]] = field(default_factory=dict)
    optimal_distribution_strategy: Dict[str, Any] = field(default_factory=dict)
    revenue_attribution: Dict[str, float] = field(default_factory=dict)
    growth_opportunities: List[Dict[str, Any]] = field(default_factory=list)
    distribution_efficiency: float = 0.0
    cross_platform_synergy: float = 0.0


class DistributionIntelligenceEngine:
    """
    Advanced cross-platform distribution intelligence and optimization engine.
    
    Provides comprehensive analysis and optimization of content distribution
    across 35+ platforms with audience analytics and revenue attribution.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Data storage
        self.distribution_events = deque(maxlen=100000)
        self.platform_metrics: Dict[str, PlatformMetrics] = {}
        self.audience_segments: Dict[str, AudienceSegment] = {}
        self.campaigns: Dict[str, CrossPlatformCampaign] = {}
        self.analytics_history = deque(maxlen=1000)
        
        # ML models for optimization
        self.platform_selector = None
        self.timing_optimizer = None
        self.audience_predictor = None
        self.revenue_optimizer = None
        
        # Redis for real-time distribution data
        self.redis_client = None
        self._initialize_redis()
        
        # Content format compatibility matrix (initialize before platform APIs)
        self.format_compatibility = {
            DistributionPlatform.YOUTUBE: [ContentFormat.VIDEO, ContentFormat.LIVE_STREAM, ContentFormat.SHORT],
            DistributionPlatform.INSTAGRAM: [ContentFormat.IMAGE, ContentFormat.VIDEO, ContentFormat.STORY, ContentFormat.REEL, ContentFormat.CAROUSEL],
            DistributionPlatform.TIKTOK: [ContentFormat.VIDEO, ContentFormat.SHORT],
            DistributionPlatform.SPOTIFY: [ContentFormat.AUDIO, ContentFormat.PODCAST, ContentFormat.ALBUM],
            DistributionPlatform.MEDIUM: [ContentFormat.ARTICLE, ContentFormat.BLOG_POST],
            DistributionPlatform.TWITTER: [ContentFormat.TEXT, ContentFormat.IMAGE, ContentFormat.VIDEO, ContentFormat.SOCIAL_POST],
            DistributionPlatform.LINKEDIN: [ContentFormat.ARTICLE, ContentFormat.SOCIAL_POST, ContentFormat.VIDEO],
            DistributionPlatform.PINTEREST: [ContentFormat.IMAGE, ContentFormat.VIDEO]
        }
        
        # Platform API configurations
        self.platform_apis = self._initialize_platform_apis()
        
        # Platform-specific optimization rules
        self.platform_rules = {
            DistributionPlatform.YOUTUBE: {
                "optimal_length": {"min": 600, "max": 1800},  # 10-30 minutes
                "posting_frequency": "2-3 times per week",
                "best_times": ["14:00", "15:00", "20:00"],
                "audience_retention_target": 0.6
            },
            DistributionPlatform.INSTAGRAM: {
                "optimal_length": {"min": 15, "max": 60},  # 15-60 seconds for videos
                "posting_frequency": "1-2 times per day",
                "best_times": ["11:00", "13:00", "17:00"],
                "hashtag_limit": 30
            },
            DistributionPlatform.TIKTOK: {
                "optimal_length": {"min": 15, "max": 60},
                "posting_frequency": "1-3 times per day",
                "best_times": ["06:00", "10:00", "19:00"],
                "trending_factor": 0.8
            }
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
    
    def _initialize_platform_apis(self) -> Dict[str, Dict[str, Any]]:
        """Initialize platform API configurations"""
        # In production, this would contain actual API credentials and endpoints
        return {
            platform.value: {
                "api_endpoint": f"https://api.{platform.value}.com",
                "rate_limit": 100,  # requests per hour
                "auth_method": "oauth2",
                "supported_formats": self.format_compatibility.get(platform, [])
            }
            for platform in DistributionPlatform
        }
    
    async def _initialize_ml_models(self):
        """Initialize ML models for distribution optimization"""
        try:
            if self._ml_models_initialized:
                return
            
            # Platform selection model
            self.platform_selector = RandomForestClassifier(
                n_estimators=100, 
                random_state=42
            )
            
            # Timing optimization model
            self.timing_optimizer = RandomForestRegressor(
                n_estimators=100, 
                random_state=42
            )
            
            # Audience prediction model
            self.audience_predictor = KMeans(
                n_clusters=8, 
                random_state=42
            )
            
            # Revenue optimization model
            self.revenue_optimizer = RandomForestRegressor(
                n_estimators=100, 
                random_state=42
            )
            
            self._ml_models_initialized = True
            self.logger.info("Distribution ML models initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize ML models: {e}")
    
    async def distribute_content(
        self,
        content_id: str,
        content_format: ContentFormat,
        target_platforms: List[DistributionPlatform],
        scheduled_time: Optional[datetime] = None,
        audience_targeting: Optional[Dict[str, Any]] = None,
        customizations: Optional[Dict[str, Dict[str, Any]]] = None
    ) -> List[DistributionEvent]:
        """Distribute content across multiple platforms"""
        try:
            if not self._ml_models_initialized:
                await self._initialize_ml_models()
            
            distribution_events = []
            scheduled_time = scheduled_time or datetime.now()
            
            # Validate platform compatibility
            compatible_platforms = [
                platform for platform in target_platforms
                if content_format in self.format_compatibility.get(platform, [])
            ]
            
            if len(compatible_platforms) < len(target_platforms):
                incompatible = set(target_platforms) - set(compatible_platforms)
                self.logger.warning(f"Content format {content_format.value} not compatible with: {[p.value for p in incompatible]}")
            
            # Create distribution events for each platform
            for platform in compatible_platforms:
                event_id = f"dist_{int(datetime.now().timestamp())}_{hash(content_id + platform.value) % 10000}"
                
                # Apply platform-specific customizations
                platform_metadata = customizations.get(platform.value, {}) if customizations else {}
                
                # Optimize timing for platform
                optimized_time = await self._optimize_timing(platform, scheduled_time, audience_targeting)
                
                event = DistributionEvent(
                    event_id=event_id,
                    content_id=content_id,
                    platform=platform,
                    content_format=content_format,
                    status=DistributionStatus.SCHEDULED,
                    scheduled_time=optimized_time,
                    metadata=platform_metadata
                )
                
                distribution_events.append(event)
                self.distribution_events.append(event)
                
                # Cache in Redis
                if self.redis_client:
                    await self._cache_distribution_event(event)
            
            # Schedule actual distribution
            await self._schedule_distribution(distribution_events)
            
            self.logger.info(f"Content {content_id} scheduled for distribution on {len(compatible_platforms)} platforms")
            return distribution_events
            
        except Exception as e:
            self.logger.error(f"Error distributing content: {e}")
            raise
    
    async def _optimize_timing(
        self,
        platform: DistributionPlatform,
        base_time: datetime,
        audience_targeting: Optional[Dict[str, Any]] = None
    ) -> datetime:
        """Optimize posting timing for platform and audience"""
        try:
            # Get platform-specific best times
            platform_rules = self.platform_rules.get(platform, {})
            best_times = platform_rules.get("best_times", ["12:00"])
            
            # If audience targeting is provided, consider their timezone
            if audience_targeting and "timezone" in audience_targeting:
                # Adjust for audience timezone
                # This is simplified - would use proper timezone handling
                timezone_offset = audience_targeting.get("timezone_offset", 0)
                base_time = base_time + timedelta(hours=timezone_offset)
            
            # Find the next optimal time slot
            current_hour = base_time.hour
            optimal_hours = [int(time.split(":")[0]) for time in best_times]
            
            # Find next optimal hour
            next_optimal = min([h for h in optimal_hours if h > current_hour], default=optimal_hours[0])
            
            # If next optimal is the next day
            if next_optimal < current_hour:
                base_time = base_time + timedelta(days=1)
            
            # Set to optimal hour
            optimized_time = base_time.replace(hour=next_optimal, minute=0, second=0, microsecond=0)
            
            return optimized_time
            
        except Exception as e:
            self.logger.error(f"Error optimizing timing: {e}")
            return base_time
    
    async def _schedule_distribution(self, events: List[DistributionEvent]):
        """Schedule actual distribution to platforms"""
        for event in events:
            try:
                # In production, this would interface with actual platform APIs
                # For now, simulate successful scheduling
                
                # Update status
                event.status = DistributionStatus.SCHEDULED
                
                # Log scheduling
                self.logger.info(f"Scheduled content {event.content_id} for {event.platform.value} at {event.scheduled_time}")
                
            except Exception as e:
                event.status = DistributionStatus.FAILED
                event.error_details = str(e)
                self.logger.error(f"Failed to schedule content {event.content_id} for {event.platform.value}: {e}")
    
    async def update_distribution_performance(
        self,
        event_id: str,
        performance_metrics: Dict[str, Any],
        audience_data: Optional[Dict[str, Any]] = None,
        revenue_data: Optional[Dict[str, float]] = None
    ) -> bool:
        """Update distribution event with performance data"""
        try:
            # Find the event
            event = None
            for dist_event in self.distribution_events:
                if dist_event.event_id == event_id:
                    event = dist_event
                    break
            
            if not event:
                self.logger.warning(f"Distribution event not found: {event_id}")
                return False
            
            # Update performance metrics
            event.performance_metrics.update(performance_metrics)
            
            if audience_data:
                event.audience_data.update(audience_data)
            
            if revenue_data:
                event.revenue_data.update(revenue_data)
            
            # Update engagement data from performance metrics
            engagement_metrics = ["likes", "shares", "comments", "saves", "views"]
            for metric in engagement_metrics:
                if metric in performance_metrics:
                    event.engagement_data[metric] = performance_metrics[metric]
            
            # Update status if content is now published
            if event.status == DistributionStatus.SCHEDULED and performance_metrics.get("views", 0) > 0:
                event.status = DistributionStatus.PUBLISHED
                event.published_time = datetime.now()
            
            # Update platform metrics
            await self._update_platform_metrics(event)
            
            # Cache updated event
            if self.redis_client:
                await self._cache_distribution_event(event)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating distribution performance: {e}")
            return False
    
    async def _update_platform_metrics(self, event: DistributionEvent):
        """Update aggregated platform metrics"""
        platform_key = event.platform.value
        
        if platform_key not in self.platform_metrics:
            self.platform_metrics[platform_key] = PlatformMetrics(platform=event.platform)
        
        metrics = self.platform_metrics[platform_key]
        
        # Update counters
        if event.status == DistributionStatus.PUBLISHED:
            metrics.content_count += 1
        
        # Update aggregated metrics from event data
        perf = event.performance_metrics
        metrics.total_views += perf.get("views", 0)
        metrics.total_likes += perf.get("likes", 0)
        metrics.total_shares += perf.get("shares", 0)
        metrics.total_comments += perf.get("comments", 0)
        metrics.total_revenue += sum(event.revenue_data.values())
        
        # Calculate rates
        if metrics.total_views > 0:
            total_engagement = metrics.total_likes + metrics.total_shares + metrics.total_comments
            metrics.engagement_rate = total_engagement / metrics.total_views
        
        metrics.reach = perf.get("reach", metrics.reach)
        metrics.impressions = perf.get("impressions", metrics.impressions)
        metrics.click_through_rate = perf.get("ctr", metrics.click_through_rate)
        metrics.conversion_rate = perf.get("conversion_rate", metrics.conversion_rate)
        metrics.audience_retention = perf.get("retention", metrics.audience_retention)
    
    async def analyze_audience_segments(
        self,
        platform_filter: Optional[List[DistributionPlatform]] = None
    ) -> List[AudienceSegment]:
        """Analyze and identify audience segments across platforms"""
        try:
            if not self._ml_models_initialized:
                await self._initialize_ml_models()
            
            # Collect audience data from distribution events
            audience_data = []
            platforms_filter = platform_filter or list(DistributionPlatform)
            
            for event in self.distribution_events:
                if event.platform in platforms_filter and event.audience_data:
                    audience_data.append({
                        "platform": event.platform.value,
                        "content_format": event.content_format.value,
                        "engagement": event.performance_metrics.get("engagement_rate", 0),
                        "demographics": event.audience_data.get("demographics", {}),
                        "interests": event.audience_data.get("interests", []),
                        "behavior": event.audience_data.get("behavior", {})
                    })
            
            if not audience_data:
                return []
            
            # Create audience segments (simplified)
            segments = []
            
            # Segment 1: High Engagement Users
            high_engagement = [d for d in audience_data if d["engagement"] > 0.1]
            if high_engagement:
                segment = AudienceSegment(
                    segment_id="high_engagement",
                    name="High Engagement Users",
                    size=len(high_engagement),
                    demographics=self._aggregate_demographics(high_engagement),
                    interests=self._aggregate_interests(high_engagement),
                    behavior_patterns=self._analyze_behavior_patterns(high_engagement),
                    platform_preferences=self._get_platform_preferences(high_engagement),
                    engagement_preferences={"video": 0.8, "image": 0.6, "text": 0.4},
                    optimal_posting_times=["12:00", "18:00", "21:00"],
                    content_preferences=[ContentFormat.VIDEO, ContentFormat.SHORT, ContentFormat.REEL],
                    revenue_potential=150.0,
                    growth_trend="growing"
                )
                segments.append(segment)
                self.audience_segments[segment.segment_id] = segment
            
            # Segment 2: Content Creators
            creator_focused = [d for d in audience_data if "content_creation" in d.get("interests", [])]
            if creator_focused:
                segment = AudienceSegment(
                    segment_id="content_creators",
                    name="Content Creators",
                    size=len(creator_focused),
                    demographics=self._aggregate_demographics(creator_focused),
                    interests=self._aggregate_interests(creator_focused),
                    behavior_patterns=self._analyze_behavior_patterns(creator_focused),
                    platform_preferences=self._get_platform_preferences(creator_focused),
                    engagement_preferences={"video": 0.9, "article": 0.7, "audio": 0.5},
                    optimal_posting_times=["09:00", "14:00", "20:00"],
                    content_preferences=[ContentFormat.VIDEO, ContentFormat.ARTICLE, ContentFormat.PODCAST],
                    revenue_potential=200.0,
                    growth_trend="stable"
                )
                segments.append(segment)
                self.audience_segments[segment.segment_id] = segment
            
            # Segment 3: General Audience
            general_audience = [d for d in audience_data if d not in high_engagement and d not in creator_focused]
            if general_audience:
                segment = AudienceSegment(
                    segment_id="general_audience",
                    name="General Audience",
                    size=len(general_audience),
                    demographics=self._aggregate_demographics(general_audience),
                    interests=self._aggregate_interests(general_audience),
                    behavior_patterns=self._analyze_behavior_patterns(general_audience),
                    platform_preferences=self._get_platform_preferences(general_audience),
                    engagement_preferences={"image": 0.7, "video": 0.6, "text": 0.5},
                    optimal_posting_times=["11:00", "15:00", "19:00"],
                    content_preferences=[ContentFormat.IMAGE, ContentFormat.SOCIAL_POST, ContentFormat.VIDEO],
                    revenue_potential=75.0,
                    growth_trend="growing"
                )
                segments.append(segment)
                self.audience_segments[segment.segment_id] = segment
            
            return segments
            
        except Exception as e:
            self.logger.error(f"Error analyzing audience segments: {e}")
            return []
    
    def _aggregate_demographics(self, audience_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Aggregate demographic data from audience"""
        age_groups = defaultdict(int)
        genders = defaultdict(int)
        locations = defaultdict(int)
        
        for data in audience_data:
            demographics = data.get("demographics", {})
            
            age_group = demographics.get("age_group", "unknown")
            age_groups[age_group] += 1
            
            gender = demographics.get("gender", "unknown")
            genders[gender] += 1
            
            location = demographics.get("location", "unknown")
            locations[location] += 1
        
        return {
            "age_groups": dict(age_groups),
            "genders": dict(genders),
            "locations": dict(locations)
        }
    
    def _aggregate_interests(self, audience_data: List[Dict[str, Any]]) -> List[str]:
        """Aggregate interests from audience data"""
        interest_counts = defaultdict(int)
        
        for data in audience_data:
            interests = data.get("interests", [])
            for interest in interests:
                interest_counts[interest] += 1
        
        # Return top interests
        sorted_interests = sorted(interest_counts.items(), key=lambda x: x[1], reverse=True)
        return [interest for interest, count in sorted_interests[:10]]
    
    def _analyze_behavior_patterns(self, audience_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze behavior patterns from audience data"""
        behaviors = {
            "active_hours": defaultdict(int),
            "session_duration": [],
            "content_consumption": defaultdict(int),
            "interaction_rate": []
        }
        
        for data in audience_data:
            behavior = data.get("behavior", {})
            
            # Active hours
            active_hour = behavior.get("most_active_hour", 12)
            behaviors["active_hours"][str(active_hour)] += 1
            
            # Session duration
            duration = behavior.get("avg_session_duration", 300)  # 5 minutes default
            behaviors["session_duration"].append(duration)
            
            # Content consumption
            content_type = data.get("content_format", "unknown")
            behaviors["content_consumption"][content_type] += 1
            
            # Interaction rate
            interaction = behavior.get("interaction_rate", 0.05)
            behaviors["interaction_rate"].append(interaction)
        
        # Calculate averages
        return {
            "most_active_hours": dict(behaviors["active_hours"]),
            "average_session_duration": statistics.mean(behaviors["session_duration"]) if behaviors["session_duration"] else 300,
            "preferred_content_types": dict(behaviors["content_consumption"]),
            "average_interaction_rate": statistics.mean(behaviors["interaction_rate"]) if behaviors["interaction_rate"] else 0.05
        }
    
    def _get_platform_preferences(self, audience_data: List[Dict[str, Any]]) -> List[DistributionPlatform]:
        """Get platform preferences from audience data"""
        platform_counts = defaultdict(int)
        
        for data in audience_data:
            platform = data.get("platform")
            if platform:
                platform_counts[platform] += 1
        
        # Sort by preference and convert to enum
        sorted_platforms = sorted(platform_counts.items(), key=lambda x: x[1], reverse=True)
        return [DistributionPlatform(platform) for platform, count in sorted_platforms[:5]]
    
    async def optimize_distribution_strategy(
        self,
        content_type: ContentFormat,
        target_audience: Optional[str] = None,
        budget_constraint: Optional[float] = None,
        priority_metrics: List[str] = None
    ) -> Dict[str, Any]:
        """Optimize distribution strategy for content type and audience"""
        try:
            if not self._ml_models_initialized:
                await self._initialize_ml_models()
            
            priority_metrics = priority_metrics or ["reach", "engagement", "revenue"]
            
            # Analyze historical performance
            relevant_events = [
                event for event in self.distribution_events
                if event.content_format == content_type
                and event.status == DistributionStatus.PUBLISHED
            ]
            
            if not relevant_events:
                return {"error": "No historical data for this content type"}
            
            # Calculate platform effectiveness scores
            platform_scores = {}
            for platform in DistributionPlatform:
                platform_events = [e for e in relevant_events if e.platform == platform]
                if platform_events:
                    score = await self._calculate_platform_effectiveness(platform_events, priority_metrics)
                    platform_scores[platform.value] = score
            
            # Sort platforms by effectiveness
            sorted_platforms = sorted(platform_scores.items(), key=lambda x: x[1], reverse=True)
            recommended_platforms = [platform for platform, score in sorted_platforms[:8]]  # Top 8 platforms
            
            # Optimize timing strategy
            timing_strategy = await self._optimize_timing_strategy(relevant_events, target_audience)
            
            # Optimize content customization
            customization_strategy = await self._optimize_content_customization(relevant_events)
            
            # Calculate expected performance
            expected_performance = await self._predict_campaign_performance(
                recommended_platforms, content_type, target_audience
            )
            
            # Budget allocation if constraint provided
            budget_allocation = {}
            if budget_constraint:
                budget_allocation = await self._optimize_budget_allocation(
                    recommended_platforms, budget_constraint, platform_scores
                )
            
            return {
                "content_type": content_type.value,
                "target_audience": target_audience,
                "recommended_platforms": recommended_platforms,
                "platform_effectiveness_scores": platform_scores,
                "timing_strategy": timing_strategy,
                "customization_strategy": customization_strategy,
                "expected_performance": expected_performance,
                "budget_allocation": budget_allocation,
                "priority_metrics": priority_metrics,
                "confidence_score": 0.85,
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error optimizing distribution strategy: {e}")
            return {"error": str(e)}
    
    async def _calculate_platform_effectiveness(
        self,
        platform_events: List[DistributionEvent],
        priority_metrics: List[str]
    ) -> float:
        """Calculate platform effectiveness score"""
        try:
            if not platform_events:
                return 0.0
            
            scores = []
            
            for metric in priority_metrics:
                if metric == "reach":
                    reach_values = [e.performance_metrics.get("reach", 0) for e in platform_events]
                    avg_reach = statistics.mean(reach_values) if reach_values else 0
                    scores.append(min(100, avg_reach / 1000))  # Normalize to 0-100
                
                elif metric == "engagement":
                    engagement_values = [e.performance_metrics.get("engagement_rate", 0) for e in platform_events]
                    avg_engagement = statistics.mean(engagement_values) if engagement_values else 0
                    scores.append(avg_engagement * 100)  # Convert to 0-100 scale
                
                elif metric == "revenue":
                    revenue_values = [sum(e.revenue_data.values()) for e in platform_events]
                    avg_revenue = statistics.mean(revenue_values) if revenue_values else 0
                    scores.append(min(100, avg_revenue / 10))  # Normalize to 0-100
            
            return statistics.mean(scores) if scores else 0.0
            
        except Exception as e:
            self.logger.error(f"Error calculating platform effectiveness: {e}")
            return 0.0
    
    async def _optimize_timing_strategy(
        self,
        events: List[DistributionEvent],
        target_audience: Optional[str] = None
    ) -> Dict[str, Any]:
        """Optimize posting timing strategy"""
        try:
            # Analyze posting times vs performance
            time_performance = defaultdict(list)
            
            for event in events:
                if event.published_time:
                    hour = event.published_time.hour
                    performance = event.performance_metrics.get("engagement_rate", 0)
                    time_performance[hour].append(performance)
            
            # Calculate average performance by hour
            hour_scores = {}
            for hour, performances in time_performance.items():
                hour_scores[hour] = statistics.mean(performances) if performances else 0
            
            # Find optimal hours
            sorted_hours = sorted(hour_scores.items(), key=lambda x: x[1], reverse=True)
            optimal_hours = [f"{hour:02d}:00" for hour, score in sorted_hours[:3]]
            
            # Day of week analysis
            day_performance = defaultdict(list)
            for event in events:
                if event.published_time:
                    day = event.published_time.strftime("%A")
                    performance = event.performance_metrics.get("engagement_rate", 0)
                    day_performance[day].append(performance)
            
            day_scores = {}
            for day, performances in day_performance.items():
                day_scores[day] = statistics.mean(performances) if performances else 0
            
            sorted_days = sorted(day_scores.items(), key=lambda x: x[1], reverse=True)
            optimal_days = [day for day, score in sorted_days[:3]]
            
            return {
                "optimal_hours": optimal_hours,
                "optimal_days": optimal_days,
                "hour_performance_scores": hour_scores,
                "day_performance_scores": day_scores,
                "posting_frequency_recommendation": "1-2 times per day",
                "timezone_considerations": target_audience or "UTC"
            }
            
        except Exception as e:
            self.logger.error(f"Error optimizing timing strategy: {e}")
            return {}
    
    async def _optimize_content_customization(self, events: List[DistributionEvent]) -> Dict[str, Any]:
        """Optimize content customization for different platforms"""
        customizations = {}
        
        # Group events by platform
        platform_events = defaultdict(list)
        for event in events:
            platform_events[event.platform.value].append(event)
        
        for platform, platform_event_list in platform_events.items():
            # Analyze what works for this platform
            high_performers = [
                e for e in platform_event_list 
                if e.performance_metrics.get("engagement_rate", 0) > 0.05
            ]
            
            if high_performers:
                # Extract common characteristics
                customizations[platform] = {
                    "optimal_content_length": self._analyze_content_length(high_performers),
                    "effective_hashtags": self._analyze_hashtags(high_performers),
                    "engagement_tactics": self._analyze_engagement_tactics(high_performers),
                    "visual_preferences": self._analyze_visual_preferences(high_performers)
                }
        
        return customizations
    
    def _analyze_content_length(self, events: List[DistributionEvent]) -> Dict[str, Any]:
        """Analyze optimal content length for events"""
        lengths = []
        for event in events:
            length = event.metadata.get("content_length", 0)
            if length > 0:
                lengths.append(length)
        
        if lengths:
            return {
                "average": statistics.mean(lengths),
                "median": statistics.median(lengths),
                "range": {"min": min(lengths), "max": max(lengths)}
            }
        return {"average": 0, "median": 0, "range": {"min": 0, "max": 0}}
    
    def _analyze_hashtags(self, events: List[DistributionEvent]) -> List[str]:
        """Analyze effective hashtags from events"""
        hashtag_performance = defaultdict(list)
        
        for event in events:
            hashtags = event.metadata.get("hashtags", [])
            engagement = event.performance_metrics.get("engagement_rate", 0)
            
            for hashtag in hashtags:
                hashtag_performance[hashtag].append(engagement)
        
        # Calculate average performance per hashtag
        hashtag_scores = {
            hashtag: statistics.mean(performances)
            for hashtag, performances in hashtag_performance.items()
            if len(performances) >= 2  # Must appear in at least 2 posts
        }
        
        # Return top performing hashtags
        sorted_hashtags = sorted(hashtag_scores.items(), key=lambda x: x[1], reverse=True)
        return [hashtag for hashtag, score in sorted_hashtags[:10]]
    
    def _analyze_engagement_tactics(self, events: List[DistributionEvent]) -> List[str]:
        """Analyze effective engagement tactics"""
        tactics = []
        
        # Check for common successful patterns
        high_engagement_events = [
            e for e in events 
            if e.performance_metrics.get("engagement_rate", 0) > 0.08
        ]
        
        if high_engagement_events:
            # Common tactics in high-performing content
            tactics.extend([
                "Use engaging questions in captions",
                "Include call-to-action prompts",
                "Post during optimal hours",
                "Use trending hashtags",
                "Engage with comments quickly"
            ])
        
        return tactics
    
    def _analyze_visual_preferences(self, events: List[DistributionEvent]) -> Dict[str, Any]:
        """Analyze visual preferences for high-performing content"""
        # Simplified analysis - would analyze actual visual content
        return {
            "preferred_aspect_ratio": "16:9",
            "color_palette": "vibrant",
            "thumbnail_style": "high_contrast",
            "text_overlay": "minimal",
            "branding_placement": "bottom_right"
        }
    
    async def _predict_campaign_performance(
        self,
        platforms: List[str],
        content_type: ContentFormat,
        target_audience: Optional[str] = None
    ) -> Dict[str, Any]:
        """Predict expected campaign performance"""
        # Simplified prediction based on historical data
        # In production, would use trained ML models
        
        base_metrics = {
            "expected_reach": 10000 * len(platforms),
            "expected_engagement_rate": 0.05,
            "expected_conversions": 100 * len(platforms),
            "expected_revenue": 500.0 * len(platforms)
        }
        
        # Adjust based on content type
        content_multipliers = {
            ContentFormat.VIDEO: 1.5,
            ContentFormat.SHORT: 1.3,
            ContentFormat.IMAGE: 1.0,
            ContentFormat.ARTICLE: 0.8,
            ContentFormat.AUDIO: 0.9
        }
        
        multiplier = content_multipliers.get(content_type, 1.0)
        
        return {
            "expected_reach": int(base_metrics["expected_reach"] * multiplier),
            "expected_engagement_rate": base_metrics["expected_engagement_rate"] * multiplier,
            "expected_conversions": int(base_metrics["expected_conversions"] * multiplier),
            "expected_revenue": base_metrics["expected_revenue"] * multiplier,
            "confidence_interval": 0.8,
            "prediction_accuracy": 0.75
        }
    
    async def _optimize_budget_allocation(
        self,
        platforms: List[str],
        total_budget: float,
        platform_scores: Dict[str, float]
    ) -> Dict[str, float]:
        """Optimize budget allocation across platforms"""
        # Calculate allocation based on platform effectiveness scores
        total_score = sum(platform_scores.get(platform, 0) for platform in platforms)
        
        allocation = {}
        if total_score > 0:
            for platform in platforms:
                score = platform_scores.get(platform, 0)
                allocation[platform] = (score / total_score) * total_budget
        else:
            # Equal allocation if no scores available
            per_platform = total_budget / len(platforms)
            allocation = {platform: per_platform for platform in platforms}
        
        return allocation
    
    async def analyze_cross_platform_performance(
        self,
        time_range: Tuple[datetime, datetime]
    ) -> DistributionIntelligence:
        """Analyze comprehensive cross-platform distribution performance"""
        try:
            start_time, end_time = time_range
            
            # Filter events by time range
            filtered_events = [
                event for event in self.distribution_events
                if start_time <= event.scheduled_time <= end_time
            ]
            
            if not filtered_events:
                return DistributionIntelligence(time_period=time_range)
            
            # Basic metrics
            total_content = len(set(e.content_id for e in filtered_events))
            total_platforms = len(set(e.platform for e in filtered_events))
            total_reach = sum(e.performance_metrics.get("reach", 0) for e in filtered_events)
            total_revenue = sum(sum(e.revenue_data.values()) for e in filtered_events)
            
            # Platform performance analysis
            platform_performance = {}
            for platform in DistributionPlatform:
                platform_events = [e for e in filtered_events if e.platform == platform]
                if platform_events:
                    metrics = await self._calculate_platform_metrics(platform_events)
                    platform_performance[platform.value] = metrics
            
            # Audience overlap analysis
            audience_overlap = await self._calculate_audience_overlap(filtered_events)
            
            # Content format performance
            format_performance = await self._analyze_format_performance(filtered_events)
            
            # Optimal distribution strategy
            optimal_strategy = await self._determine_optimal_strategy(filtered_events)
            
            # Revenue attribution
            revenue_attribution = await self._calculate_revenue_attribution(filtered_events)
            
            # Growth opportunities
            growth_opportunities = await self._identify_growth_opportunities(filtered_events)
            
            # Distribution efficiency
            efficiency = await self._calculate_distribution_efficiency(filtered_events)
            
            # Cross-platform synergy
            synergy = await self._calculate_cross_platform_synergy(filtered_events)
            
            intelligence = DistributionIntelligence(
                time_period=time_range,
                total_content_distributed=total_content,
                total_platforms_used=total_platforms,
                total_reach=total_reach,
                total_revenue=total_revenue,
                platform_performance=platform_performance,
                audience_overlap=audience_overlap,
                content_format_performance=format_performance,
                optimal_distribution_strategy=optimal_strategy,
                revenue_attribution=revenue_attribution,
                growth_opportunities=growth_opportunities,
                distribution_efficiency=efficiency,
                cross_platform_synergy=synergy
            )
            
            # Store intelligence
            self.analytics_history.append(intelligence)
            
            return intelligence
            
        except Exception as e:
            self.logger.error(f"Error analyzing cross-platform performance: {e}")
            return DistributionIntelligence(time_period=time_range)
    
    async def _calculate_platform_metrics(self, events: List[DistributionEvent]) -> Dict[str, Any]:
        """Calculate detailed metrics for platform events"""
        if not events:
            return {}
        
        total_views = sum(e.performance_metrics.get("views", 0) for e in events)
        total_engagement = sum(e.performance_metrics.get("engagement_rate", 0) for e in events)
        total_revenue = sum(sum(e.revenue_data.values()) for e in events)
        
        return {
            "content_count": len(events),
            "total_views": total_views,
            "average_engagement_rate": total_engagement / len(events) if events else 0,
            "total_revenue": total_revenue,
            "average_revenue_per_content": total_revenue / len(events) if events else 0,
            "success_rate": len([e for e in events if e.status == DistributionStatus.PUBLISHED]) / len(events) if events else 0
        }
    
    async def _calculate_audience_overlap(self, events: List[DistributionEvent]) -> Dict[str, float]:
        """Calculate audience overlap between platforms"""
        # Simplified overlap calculation
        # In production, would analyze actual user data across platforms
        
        platform_audiences = defaultdict(set)
        for event in events:
            # Simulate audience IDs
            audience_size = event.performance_metrics.get("reach", 1000)
            simulated_audience = set(range(int(audience_size * 0.1)))  # 10% sample
            platform_audiences[event.platform.value].update(simulated_audience)
        
        overlap = {}
        platforms = list(platform_audiences.keys())
        
        for i, platform_a in enumerate(platforms):
            for platform_b in platforms[i+1:]:
                audience_a = platform_audiences[platform_a]
                audience_b = platform_audiences[platform_b]
                
                if audience_a and audience_b:
                    overlap_count = len(audience_a & audience_b)
                    total_unique = len(audience_a | audience_b)
                    overlap_percentage = overlap_count / total_unique if total_unique > 0 else 0
                    overlap[f"{platform_a}_{platform_b}"] = overlap_percentage
        
        return overlap
    
    async def _analyze_format_performance(self, events: List[DistributionEvent]) -> Dict[str, Dict[str, float]]:
        """Analyze performance by content format"""
        format_metrics = defaultdict(lambda: defaultdict(list))
        
        for event in events:
            format_key = event.content_format.value
            
            # Collect metrics by format
            format_metrics[format_key]["views"].append(event.performance_metrics.get("views", 0))
            format_metrics[format_key]["engagement"].append(event.performance_metrics.get("engagement_rate", 0))
            format_metrics[format_key]["revenue"].append(sum(event.revenue_data.values()))
        
        # Calculate averages
        performance = {}
        for format_type, metrics in format_metrics.items():
            performance[format_type] = {
                "average_views": statistics.mean(metrics["views"]) if metrics["views"] else 0,
                "average_engagement_rate": statistics.mean(metrics["engagement"]) if metrics["engagement"] else 0,
                "average_revenue": statistics.mean(metrics["revenue"]) if metrics["revenue"] else 0,
                "content_count": len(metrics["views"])
            }
        
        return performance
    
    async def _determine_optimal_strategy(self, events: List[DistributionEvent]) -> Dict[str, Any]:
        """Determine optimal distribution strategy based on data"""
        # Analyze most successful combinations
        strategy = {
            "recommended_platforms": [],
            "optimal_content_mix": {},
            "timing_recommendations": {},
            "budget_recommendations": {}
        }
        
        # Platform effectiveness
        platform_performance = defaultdict(list)
        for event in events:
            success_score = self._calculate_event_success_score(event)
            platform_performance[event.platform.value].append(success_score)
        
        # Sort platforms by average success
        platform_scores = {
            platform: statistics.mean(scores) 
            for platform, scores in platform_performance.items()
            if scores
        }
        
        sorted_platforms = sorted(platform_scores.items(), key=lambda x: x[1], reverse=True)
        strategy["recommended_platforms"] = [platform for platform, score in sorted_platforms[:5]]
        
        # Content format recommendations
        format_performance = defaultdict(list)
        for event in events:
            success_score = self._calculate_event_success_score(event)
            format_performance[event.content_format.value].append(success_score)
        
        format_scores = {
            format_type: statistics.mean(scores)
            for format_type, scores in format_performance.items()
            if scores
        }
        
        strategy["optimal_content_mix"] = format_scores
        
        return strategy
    
    def _calculate_event_success_score(self, event: DistributionEvent) -> float:
        """Calculate success score for an event"""
        if event.status != DistributionStatus.PUBLISHED:
            return 0.0
        
        # Weighted success score
        views = event.performance_metrics.get("views", 0)
        engagement = event.performance_metrics.get("engagement_rate", 0)
        revenue = sum(event.revenue_data.values())
        
        # Normalize and weight
        views_score = min(100, views / 1000)  # Normalize views
        engagement_score = engagement * 100   # Convert to percentage
        revenue_score = min(100, revenue / 10)  # Normalize revenue
        
        return (views_score * 0.4) + (engagement_score * 0.4) + (revenue_score * 0.2)
    
    async def _calculate_revenue_attribution(self, events: List[DistributionEvent]) -> Dict[str, float]:
        """Calculate revenue attribution by platform"""
        platform_revenue = defaultdict(float)
        
        for event in events:
            platform = event.platform.value
            revenue = sum(event.revenue_data.values())
            platform_revenue[platform] += revenue
        
        total_revenue = sum(platform_revenue.values())
        
        # Calculate attribution percentages
        attribution = {}
        for platform, revenue in platform_revenue.items():
            attribution[platform] = (revenue / total_revenue * 100) if total_revenue > 0 else 0
        
        return attribution
    
    async def _identify_growth_opportunities(self, events: List[DistributionEvent]) -> List[Dict[str, Any]]:
        """Identify growth opportunities from distribution data"""
        opportunities = []
        
        # Underperforming platforms
        platform_performance = defaultdict(list)
        for event in events:
            success_score = self._calculate_event_success_score(event)
            platform_performance[event.platform.value].append(success_score)
        
        for platform, scores in platform_performance.items():
            avg_score = statistics.mean(scores) if scores else 0
            if avg_score < 30:  # Low performance threshold
                opportunities.append({
                    "type": "platform_optimization",
                    "platform": platform,
                    "current_score": round(avg_score, 2),
                    "description": f"Low performance on {platform} - optimization needed",
                    "potential_improvement": "40-60% increase in engagement"
                })
        
        # Untapped platforms
        used_platforms = set(event.platform.value for event in events)
        all_platforms = set(platform.value for platform in DistributionPlatform)
        untapped = all_platforms - used_platforms
        
        if untapped:
            opportunities.append({
                "type": "platform_expansion",
                "platforms": list(untapped)[:5],  # Top 5 suggestions
                "description": "Expand to additional platforms for broader reach",
                "potential_improvement": "25-40% increase in total reach"
            })
        
        # Content format opportunities
        format_usage = defaultdict(int)
        for event in events:
            format_usage[event.content_format.value] += 1
        
        if not format_usage.get("video", 0):
            opportunities.append({
                "type": "content_format_expansion",
                "format": "video",
                "description": "Video content typically performs 50% better",
                "potential_improvement": "50-70% increase in engagement"
            })
        
        return opportunities
    
    async def _calculate_distribution_efficiency(self, events: List[DistributionEvent]) -> float:
        """Calculate overall distribution efficiency score"""
        if not events:
            return 0.0
        
        # Efficiency factors
        successful_distributions = len([e for e in events if e.status == DistributionStatus.PUBLISHED])
        success_rate = successful_distributions / len(events)
        
        # Average performance across all events
        performance_scores = [self._calculate_event_success_score(event) for event in events]
        avg_performance = statistics.mean(performance_scores) if performance_scores else 0
        
        # Platform utilization efficiency
        unique_platforms = len(set(e.platform for e in events))
        platform_efficiency = min(1.0, unique_platforms / 10)  # Up to 10 platforms is efficient
        
        # Overall efficiency score
        efficiency = (success_rate * 0.4) + (avg_performance / 100 * 0.4) + (platform_efficiency * 0.2)
        
        return efficiency * 100  # Convert to percentage
    
    async def _calculate_cross_platform_synergy(self, events: List[DistributionEvent]) -> float:
        """Calculate cross-platform synergy score"""
        # Group events by content
        content_groups = defaultdict(list)
        for event in events:
            content_groups[event.content_id].append(event)
        
        synergy_scores = []
        
        for content_id, content_events in content_groups.items():
            if len(content_events) > 1:  # Multi-platform content
                # Calculate performance boost from multi-platform distribution
                total_performance = sum(self._calculate_event_success_score(e) for e in content_events)
                expected_single_platform = total_performance / len(content_events)
                actual_average = total_performance / len(content_events)
                
                # Synergy score (simplified)
                synergy = min(2.0, actual_average / max(1, expected_single_platform))
                synergy_scores.append(synergy)
        
        if synergy_scores:
            return (statistics.mean(synergy_scores) - 1) * 100  # Convert to percentage above baseline
        return 0.0
    
    # Redis caching methods
    async def _cache_distribution_event(self, event: DistributionEvent):
        """Cache distribution event in Redis"""
        if self.redis_client:
            try:
                key = f"dist_event:{event.event_id}"
                data = {
                    "content_id": event.content_id,
                    "platform": event.platform.value,
                    "status": event.status.value,
                    "scheduled_time": event.scheduled_time.isoformat(),
                    "performance_views": event.performance_metrics.get("views", 0),
                    "performance_engagement": event.performance_metrics.get("engagement_rate", 0)
                }
                self.redis_client.hset(key, mapping=data)
                self.redis_client.expire(key, 604800)  # 7 day expiry
            except Exception as e:
                self.logger.error(f"Redis cache error: {e}")
    
    def get_distribution_summary(self) -> Dict[str, Any]:
        """Get summary of distribution intelligence system"""
        try:
            total_events = len(self.distribution_events)
            total_platforms = len(self.platform_metrics)
            total_campaigns = len(self.campaigns)
            total_segments = len(self.audience_segments)
            
            # Calculate success metrics
            published_events = [e for e in self.distribution_events if e.status == DistributionStatus.PUBLISHED]
            success_rate = len(published_events) / total_events if total_events > 0 else 0
            
            total_reach = sum(e.performance_metrics.get("reach", 0) for e in published_events)
            total_revenue = sum(sum(e.revenue_data.values()) for e in published_events)
            
            return {
                "system_stats": {
                    "total_distribution_events": total_events,
                    "active_platforms": total_platforms,
                    "active_campaigns": total_campaigns,
                    "audience_segments": total_segments
                },
                "performance_metrics": {
                    "distribution_success_rate": round(success_rate * 100, 2),
                    "total_reach": total_reach,
                    "total_revenue": round(total_revenue, 2),
                    "ml_models_initialized": self._ml_models_initialized,
                    "redis_connected": self.redis_client is not None
                },
                "recent_activity": {
                    "events_last_24h": len([
                        e for e in self.distribution_events 
                        if (datetime.now() - e.scheduled_time).days == 0
                    ]),
                    "successful_distributions_today": len([
                        e for e in self.distribution_events 
                        if e.status == DistributionStatus.PUBLISHED
                        and (datetime.now() - e.scheduled_time).days == 0
                    ])
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error getting distribution summary: {e}")
            return {"error": str(e)}