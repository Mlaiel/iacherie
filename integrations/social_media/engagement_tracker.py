"""Cross-Platform Engagement Tracker
====================================

Enterprise-grade multi-platform engagement analytics and tracking system
supporting Instagram, TikTok, YouTube, Twitter, LinkedIn, Facebook, and more.

This module provides real-time engagement monitoring, performance analytics,
audience behavior analysis, and engagement optimization recommendations
for the Ainflue platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import json
import os
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import uuid
from decimal import Decimal
import statistics
import math

import httpx
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error
import plotly.graph_objects as go
import plotly.express as px


class SocialPlatform(Enum):
    """Supported social media platforms."""
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    YOUTUBE = "youtube"
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    FACEBOOK = "facebook"
    PINTEREST = "pinterest"
    SNAPCHAT = "snapchat"
    TWITCH = "twitch"
    DISCORD = "discord"
    REDDIT = "reddit"


class EngagementType(Enum):
    """Types of engagement interactions."""
    LIKE = "like"
    COMMENT = "comment"
    SHARE = "share"
    SAVE = "save"
    CLICK = "click"
    VIEW = "view"
    FOLLOW = "follow"
    UNFOLLOW = "unfollow"
    MENTION = "mention"
    HASHTAG_USE = "hashtag_use"
    STORY_VIEW = "story_view"
    STORY_REACTION = "story_reaction"


class ContentType(Enum):
    """Types of content."""
    POST = "post"
    STORY = "story"
    REEL = "reel"
    VIDEO = "video"
    LIVE_STREAM = "live_stream"
    CAROUSEL = "carousel"
    POLL = "poll"
    IGTV = "igtv"


class TimeFrame(Enum):
    """Time frame for analytics."""
    REAL_TIME = "real_time"
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


@dataclass
class EngagementMetric:
    """Individual engagement metric."""
    id: str
    content_id: str
    platform: SocialPlatform
    engagement_type: EngagementType
    value: float
    timestamp: datetime
    user_id: Optional[str] = None
    user_demographic: Dict[str, Any] = field(default_factory=dict)
    content_type: Optional[ContentType] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EngagementSummary:
    """Aggregated engagement summary for content."""
    content_id: str
    platform: SocialPlatform
    content_type: ContentType
    published_at: datetime
    
    # Core metrics
    total_views: int = 0
    total_likes: int = 0
    total_comments: int = 0
    total_shares: int = 0
    total_saves: int = 0
    total_clicks: int = 0
    
    # Calculated metrics
    engagement_rate: float = 0.0
    reach: int = 0
    impressions: int = 0
    ctr: float = 0.0  # Click-through rate
    
    # Time-based metrics
    first_hour_engagement: int = 0
    peak_engagement_hour: Optional[int] = None
    engagement_velocity: float = 0.0  # Engagement per hour
    
    # Audience metrics
    unique_users: int = 0
    repeat_engagement_rate: float = 0.0
    
    # Quality metrics
    comment_sentiment_score: float = 0.0
    engagement_quality_score: float = 0.0
    
    # Comparison metrics
    industry_benchmark_score: float = 0.0
    personal_best_score: float = 0.0
    
    # Metadata
    last_updated: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AudienceInsight:
    """Audience engagement insights."""
    platform: SocialPlatform
    time_period: TimeFrame
    start_date: datetime
    end_date: datetime
    
    # Demographics
    age_distribution: Dict[str, float] = field(default_factory=dict)
    gender_distribution: Dict[str, float] = field(default_factory=dict)
    location_distribution: Dict[str, float] = field(default_factory=dict)
    
    # Behavior patterns
    peak_activity_hours: List[int] = field(default_factory=list)
    peak_activity_days: List[str] = field(default_factory=list)
    content_preferences: Dict[str, float] = field(default_factory=dict)
    
    # Engagement patterns
    avg_engagement_rate: float = 0.0
    most_engaging_content_types: List[str] = field(default_factory=list)
    optimal_posting_frequency: int = 0
    
    # Growth metrics
    follower_growth_rate: float = 0.0
    engagement_growth_rate: float = 0.0
    reach_growth_rate: float = 0.0


@dataclass
class EngagementForecast:
    """Engagement prediction and forecast."""
    content_id: str
    platform: SocialPlatform
    forecast_horizon_hours: int
    
    # Predictions
    predicted_total_engagement: int = 0
    predicted_peak_hour: int = 0
    predicted_final_reach: int = 0
    confidence_interval: Tuple[float, float] = (0.0, 0.0)
    
    # Model metrics
    model_accuracy: float = 0.0
    last_updated: datetime = field(default_factory=datetime.utcnow)


class CrossPlatformEngagementTracker:
    """Enterprise cross-platform engagement analytics and tracking system."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize engagement tracker.
        
        Args:
            config: Configuration dict with platform API credentials and settings
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Platform API clients
        self.platform_clients: Dict[SocialPlatform, httpx.AsyncClient] = {}
        
        # Data storage
        self.engagement_metrics: List[EngagementMetric] = []
        self.engagement_summaries: Dict[str, EngagementSummary] = {}
        self.audience_insights: Dict[SocialPlatform, AudienceInsight] = {}
        
        # ML Models
        self.engagement_predictor = None
        self.scaler = StandardScaler()
        
        # Analytics cache
        self.analytics_cache: Dict[str, Any] = {}
        self.cache_ttl_minutes = 30
        
        # Real-time tracking
        self.real_time_tracking: Dict[str, bool] = {}
        self.tracking_intervals: Dict[SocialPlatform, int] = {
            SocialPlatform.INSTAGRAM: 300,  # 5 minutes
            SocialPlatform.TIKTOK: 300,
            SocialPlatform.YOUTUBE: 600,     # 10 minutes
            SocialPlatform.TWITTER: 180,     # 3 minutes
            SocialPlatform.LINKEDIN: 900,    # 15 minutes
        }
        
        # Performance tracking
        self.tracking_stats = {
            'total_metrics_collected': 0,
            'total_content_tracked': 0,
            'average_engagement_rate': 0.0,
            'top_performing_platform': None,
            'last_analysis_time': None,
            'prediction_accuracy': 0.0
        }
        
        self._initialize_platform_clients()
        self._initialize_ml_models()
    
    def _initialize_platform_clients(self) -> None:
        """Initialize social media platform API clients."""
        try:
            # Instagram Business API
            if 'instagram' in self.config:
                instagram_config = self.config['instagram']
                self.platform_clients[SocialPlatform.INSTAGRAM] = httpx.AsyncClient(
                    base_url='https://graph.facebook.com/v18.0',
                    headers={'Authorization': f'Bearer {instagram_config.get("access_token")}'},
                    timeout=30
                )
                self.logger.info("Instagram API client initialized for engagement tracking")
            
            # TikTok Business API
            if 'tiktok' in self.config:
                tiktok_config = self.config['tiktok']
                self.platform_clients[SocialPlatform.TIKTOK] = httpx.AsyncClient(
                    base_url='https://business-api.tiktok.com/open_api/v1.3',
                    headers={'Access-Token': tiktok_config.get("access_token")},
                    timeout=30
                )
                self.logger.info("TikTok API client initialized for engagement tracking")
            
            # YouTube Data API
            if 'youtube' in self.config:
                youtube_config = self.config['youtube']
                self.platform_clients[SocialPlatform.YOUTUBE] = httpx.AsyncClient(
                    base_url='https://www.googleapis.com/youtube/v3',
                    headers={'Authorization': f'Bearer {youtube_config.get("access_token")}'},
                    timeout=30
                )
                self.logger.info("YouTube API client initialized for engagement tracking")
            
            # Twitter API v2
            if 'twitter' in self.config:
                twitter_config = self.config['twitter']
                self.platform_clients[SocialPlatform.TWITTER] = httpx.AsyncClient(
                    base_url='https://api.twitter.com/2',
                    headers={'Authorization': f'Bearer {twitter_config.get("bearer_token")}'},
                    timeout=30
                )
                self.logger.info("Twitter API client initialized for engagement tracking")
            
            # LinkedIn API
            if 'linkedin' in self.config:
                linkedin_config = self.config['linkedin']
                self.platform_clients[SocialPlatform.LINKEDIN] = httpx.AsyncClient(
                    base_url='https://api.linkedin.com/rest',
                    headers={
                        'Authorization': f'Bearer {linkedin_config.get("access_token")}',
                        'LinkedIn-Version': '202309'
                    },
                    timeout=30
                )
                self.logger.info("LinkedIn API client initialized for engagement tracking")
                
        except Exception as e:
            self.logger.error(f"Error initializing platform clients: {e}")
            raise
    
    def _initialize_ml_models(self) -> None:
        """Initialize machine learning models for engagement prediction."""
        try:
            # Random Forest model for engagement prediction
            self.engagement_predictor = RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                random_state=42
            )
            
            self.logger.info("ML models initialized for engagement prediction")
            
        except Exception as e:
            self.logger.error(f"Error initializing ML models: {e}")
    
    async def track_content_engagement(
        self,
        content_id: str,
        platform: SocialPlatform,
        content_type: ContentType,
        published_at: datetime,
        real_time: bool = True
    ) -> str:
        """Start tracking engagement for specific content.
        
        Args:
            content_id: Platform-specific content ID
            platform: Social media platform
            content_type: Type of content
            published_at: When content was published
            real_time: Whether to enable real-time tracking
            
        Returns:
            Tracking session ID
        """
        try:
            tracking_id = f"track-{platform.value}-{content_id}-{uuid.uuid4().hex[:8]}"
            
            # Initialize engagement summary
            summary = EngagementSummary(
                content_id=content_id,
                platform=platform,
                content_type=content_type,
                published_at=published_at
            )
            
            self.engagement_summaries[tracking_id] = summary
            
            # Enable real-time tracking if requested
            if real_time:
                self.real_time_tracking[tracking_id] = True
                
                # Schedule periodic updates
                interval = self.tracking_intervals.get(platform, 300)
                # In a real implementation, this would use a task scheduler
                # For now, we'll track this in the background
            
            self.tracking_stats['total_content_tracked'] += 1
            
            self.logger.info(
                f"Started tracking engagement for {platform.value} content {content_id} "
                f"(tracking_id: {tracking_id})"
            )
            
            return tracking_id
            
        except Exception as e:
            self.logger.error(f"Error starting engagement tracking: {e}")
            raise
    
    async def collect_engagement_metrics(
        self,
        tracking_id: str,
        include_demographics: bool = True
    ) -> List[EngagementMetric]:
        """Collect current engagement metrics for tracked content.
        
        Args:
            tracking_id: Tracking session ID
            include_demographics: Whether to include user demographic data
            
        Returns:
            List of engagement metrics
        """
        try:
            summary = self.engagement_summaries.get(tracking_id)
            if not summary:
                raise ValueError(f"Tracking session {tracking_id} not found")
            
            # Collect platform-specific metrics
            if summary.platform == SocialPlatform.INSTAGRAM:
                metrics = await self._collect_instagram_metrics(summary, include_demographics)
            elif summary.platform == SocialPlatform.TIKTOK:
                metrics = await self._collect_tiktok_metrics(summary, include_demographics)
            elif summary.platform == SocialPlatform.YOUTUBE:
                metrics = await self._collect_youtube_metrics(summary, include_demographics)
            elif summary.platform == SocialPlatform.TWITTER:
                metrics = await self._collect_twitter_metrics(summary, include_demographics)
            elif summary.platform == SocialPlatform.LINKEDIN:
                metrics = await self._collect_linkedin_metrics(summary, include_demographics)
            else:
                self.logger.warning(f"Engagement collection not implemented for {summary.platform.value}")
                metrics = []
            
            # Store metrics
            self.engagement_metrics.extend(metrics)
            
            # Update summary
            await self._update_engagement_summary(tracking_id, metrics)
            
            self.tracking_stats['total_metrics_collected'] += len(metrics)
            
            self.logger.info(
                f"Collected {len(metrics)} engagement metrics for {tracking_id}"
            )
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error collecting engagement metrics: {e}")
            raise
    
    async def _collect_instagram_metrics(
        self,
        summary: EngagementSummary,
        include_demographics: bool
    ) -> List[EngagementMetric]:
        """Collect Instagram engagement metrics."""
        metrics = []
        
        try:
            client = self.platform_clients.get(SocialPlatform.INSTAGRAM)
            if not client:
                return metrics
            
            # Get post insights
            response = await client.get(
                f"/{summary.content_id}/insights",
                params={
                    'metric': 'impressions,reach,likes,comments,shares,saves,profile_visits',
                    'access_token': self.config['instagram']['access_token']
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                
                for insight in data.get('data', []):
                    metric_name = insight['name']
                    value = insight['values'][0]['value'] if insight['values'] else 0
                    
                    # Map Instagram metrics to engagement types
                    engagement_type_map = {
                        'impressions': EngagementType.VIEW,
                        'reach': EngagementType.VIEW,
                        'likes': EngagementType.LIKE,
                        'comments': EngagementType.COMMENT,
                        'shares': EngagementType.SHARE,
                        'saves': EngagementType.SAVE,
                        'profile_visits': EngagementType.CLICK
                    }
                    
                    engagement_type = engagement_type_map.get(metric_name)
                    if engagement_type:
                        metric = EngagementMetric(
                            id=f"ig-{summary.content_id}-{metric_name}-{int(datetime.utcnow().timestamp())}",
                            content_id=summary.content_id,
                            platform=SocialPlatform.INSTAGRAM,
                            engagement_type=engagement_type,
                            value=float(value),
                            timestamp=datetime.utcnow(),
                            content_type=summary.content_type,
                            metadata={'metric_name': metric_name}
                        )
                        metrics.append(metric)
            
            # Get comments for sentiment analysis
            if include_demographics:
                comments_response = await client.get(
                    f"/{summary.content_id}/comments",
                    params={
                        'fields': 'text,from,created_time',
                        'access_token': self.config['instagram']['access_token']
                    }
                )
                
                if comments_response.status_code == 200:
                    comments_data = comments_response.json()
                    
                    for comment in comments_data.get('data', []):
                        metric = EngagementMetric(
                            id=f"ig-comment-{comment['id']}",
                            content_id=summary.content_id,
                            platform=SocialPlatform.INSTAGRAM,
                            engagement_type=EngagementType.COMMENT,
                            value=1.0,
                            timestamp=datetime.fromisoformat(comment['created_time'].replace('Z', '+00:00')),
                            user_id=comment.get('from', {}).get('id'),
                            content_type=summary.content_type,
                            metadata={
                                'comment_text': comment['text'],
                                'user_name': comment.get('from', {}).get('username')
                            }
                        )
                        metrics.append(metric)
                        
        except Exception as e:
            self.logger.error(f"Error collecting Instagram metrics: {e}")
        
        return metrics
    
    async def _collect_youtube_metrics(
        self,
        summary: EngagementSummary,
        include_demographics: bool
    ) -> List[EngagementMetric]:
        """Collect YouTube engagement metrics."""
        metrics = []
        
        try:
            client = self.platform_clients.get(SocialPlatform.YOUTUBE)
            if not client:
                return metrics
            
            # Get video statistics
            response = await client.get(
                '/videos',
                params={
                    'part': 'statistics,snippet',
                    'id': summary.content_id,
                    'key': self.config['youtube']['api_key']
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('items'):
                    video = data['items'][0]
                    stats = video.get('statistics', {})
                    
                    # Create metrics for each statistic
                    metric_mappings = {
                        'viewCount': EngagementType.VIEW,
                        'likeCount': EngagementType.LIKE,
                        'commentCount': EngagementType.COMMENT,
                        'favoriteCount': EngagementType.SAVE,
                        'subscriberGainedFromVideoCount': EngagementType.FOLLOW
                    }
                    
                    for stat_name, engagement_type in metric_mappings.items():
                        if stat_name in stats:
                            metric = EngagementMetric(
                                id=f"yt-{summary.content_id}-{stat_name}-{int(datetime.utcnow().timestamp())}",
                                content_id=summary.content_id,
                                platform=SocialPlatform.YOUTUBE,
                                engagement_type=engagement_type,
                                value=float(stats[stat_name]),
                                timestamp=datetime.utcnow(),
                                content_type=summary.content_type,
                                metadata={'metric_name': stat_name}
                            )
                            metrics.append(metric)
            
            # Get video analytics (requires OAuth)
            if include_demographics and 'access_token' in self.config['youtube']:
                analytics_response = await client.get(
                    '/reports',
                    params={
                        'ids': 'channel==MINE',
                        'startDate': summary.published_at.strftime('%Y-%m-%d'),
                        'endDate': datetime.utcnow().strftime('%Y-%m-%d'),
                        'metrics': 'views,likes,comments,shares,estimatedMinutesWatched',
                        'dimensions': 'video',
                        'filters': f'video=={summary.content_id}',
                        'access_token': self.config['youtube']['access_token']
                    }
                )
                
                if analytics_response.status_code == 200:
                    analytics_data = analytics_response.json()
                    
                    for row in analytics_data.get('rows', []):
                        # Process analytics data
                        views = float(row[1]) if len(row) > 1 else 0
                        likes = float(row[2]) if len(row) > 2 else 0
                        comments = float(row[3]) if len(row) > 3 else 0
                        shares = float(row[4]) if len(row) > 4 else 0
                        watch_time = float(row[5]) if len(row) > 5 else 0
                        
                        # Add detailed metrics
                        detailed_metrics = [
                            (EngagementType.VIEW, views),
                            (EngagementType.LIKE, likes),
                            (EngagementType.COMMENT, comments),
                            (EngagementType.SHARE, shares)
                        ]
                        
                        for engagement_type, value in detailed_metrics:
                            if value > 0:
                                metric = EngagementMetric(
                                    id=f"yt-analytics-{summary.content_id}-{engagement_type.value}-{int(datetime.utcnow().timestamp())}",
                                    content_id=summary.content_id,
                                    platform=SocialPlatform.YOUTUBE,
                                    engagement_type=engagement_type,
                                    value=value,
                                    timestamp=datetime.utcnow(),
                                    content_type=summary.content_type,
                                    metadata={
                                        'source': 'youtube_analytics',
                                        'watch_time_minutes': watch_time
                                    }
                                )
                                metrics.append(metric)
                        
        except Exception as e:
            self.logger.error(f"Error collecting YouTube metrics: {e}")
        
        return metrics
    
    async def _collect_twitter_metrics(
        self,
        summary: EngagementSummary,
        include_demographics: bool
    ) -> List[EngagementMetric]:
        """Collect Twitter engagement metrics."""
        metrics = []
        
        try:
            client = self.platform_clients.get(SocialPlatform.TWITTER)
            if not client:
                return metrics
            
            # Get tweet metrics
            response = await client.get(
                f'/tweets/{summary.content_id}',
                params={
                    'tweet.fields': 'public_metrics,created_at,context_annotations',
                    'expansions': 'author_id'
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if 'data' in data:
                    tweet = data['data']
                    public_metrics = tweet.get('public_metrics', {})
                    
                    # Map Twitter metrics to engagement types
                    metric_mappings = {
                        'impression_count': EngagementType.VIEW,
                        'like_count': EngagementType.LIKE,
                        'reply_count': EngagementType.COMMENT,
                        'retweet_count': EngagementType.SHARE,
                        'quote_count': EngagementType.SHARE,
                        'bookmark_count': EngagementType.SAVE
                    }
                    
                    for metric_name, engagement_type in metric_mappings.items():
                        if metric_name in public_metrics:
                            metric = EngagementMetric(
                                id=f"tw-{summary.content_id}-{metric_name}-{int(datetime.utcnow().timestamp())}",
                                content_id=summary.content_id,
                                platform=SocialPlatform.TWITTER,
                                engagement_type=engagement_type,
                                value=float(public_metrics[metric_name]),
                                timestamp=datetime.utcnow(),
                                content_type=summary.content_type,
                                metadata={'metric_name': metric_name}
                            )
                            metrics.append(metric)
                        
        except Exception as e:
            self.logger.error(f"Error collecting Twitter metrics: {e}")
        
        return metrics
    
    async def _update_engagement_summary(
        self,
        tracking_id: str,
        new_metrics: List[EngagementMetric]
    ) -> None:
        """Update engagement summary with new metrics.
        
        Args:
            tracking_id: Tracking session ID
            new_metrics: New metrics to incorporate
        """
        try:
            summary = self.engagement_summaries.get(tracking_id)
            if not summary:
                return
            
            # Aggregate metrics by type
            metrics_by_type = {}
            for metric in new_metrics:
                if metric.engagement_type not in metrics_by_type:
                    metrics_by_type[metric.engagement_type] = []
                metrics_by_type[metric.engagement_type].append(metric)
            
            # Update summary fields
            if EngagementType.VIEW in metrics_by_type:
                view_metrics = metrics_by_type[EngagementType.VIEW]
                summary.total_views = int(max(m.value for m in view_metrics))
                summary.impressions = summary.total_views  # Simplified
            
            if EngagementType.LIKE in metrics_by_type:
                like_metrics = metrics_by_type[EngagementType.LIKE]
                summary.total_likes = int(max(m.value for m in like_metrics))
            
            if EngagementType.COMMENT in metrics_by_type:
                comment_metrics = metrics_by_type[EngagementType.COMMENT]
                summary.total_comments = int(max(m.value for m in comment_metrics))
            
            if EngagementType.SHARE in metrics_by_type:
                share_metrics = metrics_by_type[EngagementType.SHARE]
                summary.total_shares = int(max(m.value for m in share_metrics))
            
            if EngagementType.SAVE in metrics_by_type:
                save_metrics = metrics_by_type[EngagementType.SAVE]
                summary.total_saves = int(max(m.value for m in save_metrics))
            
            if EngagementType.CLICK in metrics_by_type:
                click_metrics = metrics_by_type[EngagementType.CLICK]
                summary.total_clicks = int(max(m.value for m in click_metrics))
            
            # Calculate engagement rate
            total_engagement = (summary.total_likes + summary.total_comments + 
                              summary.total_shares + summary.total_saves)
            
            if summary.total_views > 0:
                summary.engagement_rate = (total_engagement / summary.total_views) * 100
            
            # Calculate click-through rate
            if summary.impressions > 0:
                summary.ctr = (summary.total_clicks / summary.impressions) * 100
            
            # Calculate engagement velocity (engagement per hour since published)
            hours_since_published = (datetime.utcnow() - summary.published_at).total_seconds() / 3600
            if hours_since_published > 0:
                summary.engagement_velocity = total_engagement / hours_since_published
            
            # Calculate first hour engagement
            if hours_since_published <= 1:
                summary.first_hour_engagement = total_engagement
            
            # Update last updated timestamp
            summary.last_updated = datetime.utcnow()
            
            self.logger.debug(f"Updated engagement summary for {tracking_id}")
            
        except Exception as e:
            self.logger.error(f"Error updating engagement summary: {e}")
    
    async def analyze_audience_insights(
        self,
        platform: SocialPlatform,
        time_period: TimeFrame = TimeFrame.MONTHLY,
        days_back: int = 30
    ) -> AudienceInsight:
        """Analyze audience insights for platform.
        
        Args:
            platform: Social media platform
            time_period: Time frame for analysis
            days_back: Number of days to analyze
            
        Returns:
            Audience insights
        """
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days_back)
            
            # Filter metrics for platform and time period
            platform_metrics = [
                m for m in self.engagement_metrics
                if (m.platform == platform and 
                    start_date <= m.timestamp <= end_date)
            ]
            
            if not platform_metrics:
                # Return empty insights if no data
                return AudienceInsight(
                    platform=platform,
                    time_period=time_period,
                    start_date=start_date,
                    end_date=end_date
                )
            
            # Analyze peak activity patterns
            hourly_engagement = {}
            daily_engagement = {}
            
            for metric in platform_metrics:
                hour = metric.timestamp.hour
                day = metric.timestamp.strftime('%A')
                
                if hour not in hourly_engagement:
                    hourly_engagement[hour] = 0
                hourly_engagement[hour] += metric.value
                
                if day not in daily_engagement:
                    daily_engagement[day] = 0
                daily_engagement[day] += metric.value
            
            # Find peak hours and days
            peak_hours = sorted(hourly_engagement.items(), key=lambda x: x[1], reverse=True)[:3]
            peak_days = sorted(daily_engagement.items(), key=lambda x: x[1], reverse=True)[:3]
            
            # Calculate average engagement rate
            engagement_metrics = [
                m for m in platform_metrics 
                if m.engagement_type in [EngagementType.LIKE, EngagementType.COMMENT, EngagementType.SHARE]
            ]
            
            avg_engagement = statistics.mean([m.value for m in engagement_metrics]) if engagement_metrics else 0
            
            # Analyze content preferences
            content_type_performance = {}
            for metric in platform_metrics:
                if metric.content_type:
                    content_type = metric.content_type.value
                    if content_type not in content_type_performance:
                        content_type_performance[content_type] = []
                    content_type_performance[content_type].append(metric.value)
            
            # Calculate average performance per content type
            content_preferences = {}
            for content_type, values in content_type_performance.items():
                content_preferences[content_type] = statistics.mean(values)
            
            # Create audience insight
            insight = AudienceInsight(
                platform=platform,
                time_period=time_period,
                start_date=start_date,
                end_date=end_date,
                peak_activity_hours=[hour for hour, _ in peak_hours],
                peak_activity_days=[day for day, _ in peak_days],
                avg_engagement_rate=avg_engagement,
                content_preferences=content_preferences,
                most_engaging_content_types=list(content_preferences.keys())[:3]
            )
            
            # Store insights
            self.audience_insights[platform] = insight
            
            self.logger.info(
                f"Analyzed audience insights for {platform.value}: "
                f"peak hours {insight.peak_activity_hours}, "
                f"avg engagement {insight.avg_engagement_rate:.2f}"
            )
            
            return insight
            
        except Exception as e:
            self.logger.error(f"Error analyzing audience insights: {e}")
            raise
    
    async def predict_engagement(
        self,
        content_id: str,
        platform: SocialPlatform,
        content_type: ContentType,
        published_at: datetime,
        forecast_hours: int = 24
    ) -> EngagementForecast:
        """Predict future engagement for content.
        
        Args:
            content_id: Content ID
            platform: Social media platform
            content_type: Type of content
            published_at: When content was published
            forecast_hours: Hours to forecast ahead
            
        Returns:
            Engagement forecast
        """
        try:
            # Prepare features for prediction
            features = await self._extract_prediction_features(
                platform, content_type, published_at
            )
            
            # Train model if not trained or needs updating
            if not hasattr(self.engagement_predictor, 'feature_importances_'):
                await self._train_engagement_predictor(platform)
            
            # Make prediction
            if hasattr(self.engagement_predictor, 'feature_importances_'):
                # Prepare feature vector
                feature_vector = np.array(features).reshape(1, -1)
                feature_vector_scaled = self.scaler.transform(feature_vector)
                
                # Predict total engagement
                predicted_engagement = self.engagement_predictor.predict(feature_vector_scaled)[0]
                
                # Calculate confidence interval (simplified)
                confidence_range = predicted_engagement * 0.2  # ±20%
                confidence_interval = (
                    max(0, predicted_engagement - confidence_range),
                    predicted_engagement + confidence_range
                )
                
                # Predict peak hour (simplified - based on historical patterns)
                audience_insight = self.audience_insights.get(platform)
                predicted_peak_hour = 12  # Default
                if audience_insight and audience_insight.peak_activity_hours:
                    predicted_peak_hour = audience_insight.peak_activity_hours[0]
                
                forecast = EngagementForecast(
                    content_id=content_id,
                    platform=platform,
                    forecast_horizon_hours=forecast_hours,
                    predicted_total_engagement=int(predicted_engagement),
                    predicted_peak_hour=predicted_peak_hour,
                    predicted_final_reach=int(predicted_engagement * 1.5),  # Simplified
                    confidence_interval=confidence_interval,
                    model_accuracy=self.tracking_stats.get('prediction_accuracy', 0.0)
                )
            else:
                # Return default forecast if model not trained
                forecast = EngagementForecast(
                    content_id=content_id,
                    platform=platform,
                    forecast_horizon_hours=forecast_hours,
                    predicted_total_engagement=100,  # Default prediction
                    predicted_peak_hour=12,
                    predicted_final_reach=150,
                    confidence_interval=(50.0, 200.0),
                    model_accuracy=0.0
                )
            
            self.logger.info(
                f"Predicted engagement for {content_id}: "
                f"{forecast.predicted_total_engagement} total engagement"
            )
            
            return forecast
            
        except Exception as e:
            self.logger.error(f"Error predicting engagement: {e}")
            raise
    
    async def _extract_prediction_features(
        self,
        platform: SocialPlatform,
        content_type: ContentType,
        published_at: datetime
    ) -> List[float]:
        """Extract features for engagement prediction.
        
        Args:
            platform: Social media platform
            content_type: Type of content
            published_at: When content was published
            
        Returns:
            Feature vector for prediction
        """
        try:
            features = []
            
            # Time-based features
            hour_of_day = published_at.hour
            day_of_week = published_at.weekday()
            
            features.extend([
                hour_of_day / 24.0,  # Normalize to 0-1
                day_of_week / 7.0,   # Normalize to 0-1
            ])
            
            # Platform encoding (one-hot)
            platform_features = [0.0] * len(SocialPlatform)
            platform_features[list(SocialPlatform).index(platform)] = 1.0
            features.extend(platform_features)
            
            # Content type encoding (one-hot)
            content_type_features = [0.0] * len(ContentType)
            content_type_features[list(ContentType).index(content_type)] = 1.0
            features.extend(content_type_features)
            
            # Historical performance features
            platform_metrics = [
                m for m in self.engagement_metrics
                if m.platform == platform
            ]
            
            if platform_metrics:
                avg_engagement = statistics.mean([m.value for m in platform_metrics])
                features.append(avg_engagement / 1000.0)  # Normalize
            else:
                features.append(0.0)
            
            # Audience insight features
            audience_insight = self.audience_insights.get(platform)
            if audience_insight:
                features.extend([
                    audience_insight.avg_engagement_rate / 100.0,  # Normalize
                    len(audience_insight.peak_activity_hours) / 24.0,  # Normalize
                ])
            else:
                features.extend([0.0, 0.0])
            
            return features
            
        except Exception as e:
            self.logger.error(f"Error extracting prediction features: {e}")
            return [0.0] * 20  # Return default feature vector
    
    async def _train_engagement_predictor(self, platform: SocialPlatform) -> None:
        """Train engagement prediction model.
        
        Args:
            platform: Platform to train model for
        """
        try:
            # Get historical data for platform
            platform_summaries = [
                s for s in self.engagement_summaries.values()
                if s.platform == platform
            ]
            
            if len(platform_summaries) < 10:  # Need minimum data
                self.logger.warning(f"Insufficient data to train model for {platform.value}")
                return
            
            # Prepare training data
            X = []
            y = []
            
            for summary in platform_summaries:
                features = await self._extract_prediction_features(
                    summary.platform,
                    summary.content_type,
                    summary.published_at
                )
                
                total_engagement = (
                    summary.total_likes + summary.total_comments + 
                    summary.total_shares + summary.total_saves
                )
                
                X.append(features)
                y.append(total_engagement)
            
            # Convert to numpy arrays
            X = np.array(X)
            y = np.array(y)
            
            # Scale features
            X_scaled = self.scaler.fit_transform(X)
            
            # Train model
            self.engagement_predictor.fit(X_scaled, y)
            
            # Calculate accuracy (simplified - using training data)
            y_pred = self.engagement_predictor.predict(X_scaled)
            accuracy = 1 - (mean_absolute_error(y, y_pred) / np.mean(y))
            self.tracking_stats['prediction_accuracy'] = max(0, accuracy)
            
            self.logger.info(
                f"Trained engagement predictor for {platform.value} "
                f"with {len(X)} samples, accuracy: {accuracy:.2f}"
            )
            
        except Exception as e:
            self.logger.error(f"Error training engagement predictor: {e}")
    
    async def generate_engagement_report(
        self,
        time_period: TimeFrame = TimeFrame.WEEKLY,
        include_predictions: bool = True
    ) -> Dict[str, Any]:
        """Generate comprehensive engagement report.
        
        Args:
            time_period: Time period for report
            include_predictions: Whether to include engagement predictions
            
        Returns:
            Comprehensive engagement report
        """
        try:
            # Calculate date range
            if time_period == TimeFrame.DAILY:
                days_back = 1
            elif time_period == TimeFrame.WEEKLY:
                days_back = 7
            elif time_period == TimeFrame.MONTHLY:
                days_back = 30
            else:
                days_back = 7
            
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days_back)
            
            # Filter data for time period
            period_metrics = [
                m for m in self.engagement_metrics
                if start_date <= m.timestamp <= end_date
            ]
            
            period_summaries = [
                s for s in self.engagement_summaries.values()
                if start_date <= s.published_at <= end_date
            ]
            
            # Overall performance metrics
            total_engagement = sum(
                s.total_likes + s.total_comments + s.total_shares + s.total_saves
                for s in period_summaries
            )
            
            total_reach = sum(s.reach for s in period_summaries)
            avg_engagement_rate = statistics.mean([s.engagement_rate for s in period_summaries]) if period_summaries else 0
            
            # Platform breakdown
            platform_performance = {}
            for platform in SocialPlatform:
                platform_summaries = [s for s in period_summaries if s.platform == platform]
                
                if platform_summaries:
                    platform_engagement = sum(
                        s.total_likes + s.total_comments + s.total_shares + s.total_saves
                        for s in platform_summaries
                    )
                    
                    platform_performance[platform.value] = {
                        'total_content': len(platform_summaries),
                        'total_engagement': platform_engagement,
                        'avg_engagement_rate': statistics.mean([s.engagement_rate for s in platform_summaries]),
                        'total_reach': sum(s.reach for s in platform_summaries)
                    }
            
            # Top performing content
            top_content = sorted(
                period_summaries,
                key=lambda s: s.total_likes + s.total_comments + s.total_shares + s.total_saves,
                reverse=True
            )[:5]
            
            # Generate report
            report = {
                'report_id': f"engagement-report-{uuid.uuid4().hex[:8]}",
                'generated_at': datetime.utcnow(),
                'time_period': time_period.value,
                'date_range': {
                    'start_date': start_date,
                    'end_date': end_date,
                    'days': days_back
                },
                'summary': {
                    'total_content_pieces': len(period_summaries),
                    'total_engagement': total_engagement,
                    'total_reach': total_reach,
                    'average_engagement_rate': avg_engagement_rate,
                    'total_metrics_collected': len(period_metrics)
                },
                'platform_performance': platform_performance,
                'top_performing_content': [
                    {
                        'content_id': s.content_id,
                        'platform': s.platform.value,
                        'content_type': s.content_type.value,
                        'engagement_rate': s.engagement_rate,
                        'total_engagement': s.total_likes + s.total_comments + s.total_shares + s.total_saves,
                        'published_at': s.published_at
                    }
                    for s in top_content
                ],
                'audience_insights': {
                    platform.value: {
                        'peak_hours': insight.peak_activity_hours,
                        'peak_days': insight.peak_activity_days,
                        'content_preferences': insight.content_preferences
                    }
                    for platform, insight in self.audience_insights.items()
                },
                'tracking_stats': self.tracking_stats.copy()
            }
            
            # Add predictions if requested
            if include_predictions and period_summaries:
                predictions = []
                for summary in period_summaries[-3:]:  # Last 3 pieces of content
                    try:
                        forecast = await self.predict_engagement(
                            summary.content_id,
                            summary.platform,
                            summary.content_type,
                            summary.published_at,
                            forecast_hours=24
                        )
                        predictions.append({
                            'content_id': forecast.content_id,
                            'platform': forecast.platform.value,
                            'predicted_engagement': forecast.predicted_total_engagement,
                            'confidence_interval': forecast.confidence_interval
                        })
                    except:
                        pass  # Skip if prediction fails
                
                report['predictions'] = predictions
            
            self.tracking_stats['last_analysis_time'] = datetime.utcnow()
            
            self.logger.info(
                f"Generated engagement report: {report['summary']['total_content_pieces']} "
                f"content pieces, {total_engagement} total engagement"
            )
            
            return report
            
        except Exception as e:
            self.logger.error(f"Error generating engagement report: {e}")
            raise
    
    def get_tracking_stats(self) -> Dict[str, Any]:
        """Get engagement tracking statistics."""
        return {
            **self.tracking_stats,
            'active_tracking_sessions': len(self.real_time_tracking),
            'total_engagement_summaries': len(self.engagement_summaries),
            'platforms_with_insights': len(self.audience_insights),
            'cache_size': len(self.analytics_cache)
        }
    
    async def close(self) -> None:
        """Close platform connections and cleanup resources."""
        try:
            # Close platform clients
            for client in self.platform_clients.values():
                if hasattr(client, 'aclose'):
                    await client.aclose()
            
            # Clear real-time tracking
            self.real_time_tracking.clear()
            
            self.logger.info("Cross-platform engagement tracker closed")
            
        except Exception as e:
            self.logger.error(f"Error closing engagement tracker: {e}")


# Example usage
async def example_usage():
    """Example usage of CrossPlatformEngagementTracker."""
    
    config = {
        'instagram': {
            'access_token': 'your-instagram-token'
        },
        'youtube': {
            'api_key': 'your-youtube-api-key',
            'access_token': 'your-youtube-oauth-token'
        },
        'twitter': {
            'bearer_token': 'your-twitter-bearer-token'
        }
    }
    
    tracker = CrossPlatformEngagementTracker(config)
    
    try:
        # Start tracking content engagement
        tracking_id = await tracker.track_content_engagement(
            content_id="instagram_post_12345",
            platform=SocialPlatform.INSTAGRAM,
            content_type=ContentType.POST,
            published_at=datetime.utcnow() - timedelta(hours=2),
            real_time=True
        )
        
        print(f"Started tracking: {tracking_id}")
        
        # Collect current engagement metrics
        metrics = await tracker.collect_engagement_metrics(
            tracking_id,
            include_demographics=True
        )
        
        print(f"Collected {len(metrics)} engagement metrics")
        
        # Analyze audience insights
        insights = await tracker.analyze_audience_insights(
            SocialPlatform.INSTAGRAM,
            time_period=TimeFrame.WEEKLY
        )
        
        print(f"Peak activity hours: {insights.peak_activity_hours}")
        
        # Predict future engagement
        forecast = await tracker.predict_engagement(
            content_id="new_post_67890",
            platform=SocialPlatform.INSTAGRAM,
            content_type=ContentType.REEL,
            published_at=datetime.utcnow(),
            forecast_hours=24
        )
        
        print(f"Predicted engagement: {forecast.predicted_total_engagement}")
        
        # Generate comprehensive report
        report = await tracker.generate_engagement_report(
            time_period=TimeFrame.WEEKLY,
            include_predictions=True
        )
        
        print(f"Generated report with {report['summary']['total_content_pieces']} content pieces")
        
        # Get tracking stats
        stats = tracker.get_tracking_stats()
        print(f"Tracking stats: {stats}")
        
    finally:
        await tracker.close()


if __name__ == "__main__":
    asyncio.run(example_usage())