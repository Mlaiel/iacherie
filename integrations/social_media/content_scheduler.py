"""Multi-Platform Content Scheduler
==================================

Enterprise-grade multi-platform social media content scheduling system
supporting Instagram, TikTok, YouTube, Twitter, LinkedIn, Facebook, and more.

This module provides intelligent content scheduling, optimal timing analysis,
audience engagement optimization, and cross-platform content adaptation
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
import hashlib
import re

import httpx
import pytz
from PIL import Image
import cv2
import numpy as np
from moviepy.editor import VideoFileClip
import schedule
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger


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
    MEDIUM = "medium"


class ContentType(Enum):
    """Types of content that can be scheduled."""
    POST = "post"
    STORY = "story"
    REEL = "reel"
    VIDEO = "video"
    LIVE_STREAM = "live_stream"
    CAROUSEL = "carousel"
    POLL = "poll"
    BLOG_POST = "blog_post"
    NEWSLETTER = "newsletter"
    PODCAST = "podcast"


class ScheduleStatus(Enum):
    """Content schedule status."""
    SCHEDULED = "scheduled"
    PUBLISHED = "published"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PENDING_APPROVAL = "pending_approval"
    DRAFT = "draft"


class OptimalTimeType(Enum):
    """Types of optimal timing analysis."""
    ENGAGEMENT = "engagement"
    REACH = "reach"
    CONVERSIONS = "conversions"
    VIEWS = "views"
    SHARES = "shares"


@dataclass
class MediaAsset:
    """Media asset for content."""
    id: str
    type: str  # image, video, audio
    url: str
    filename: str
    size_bytes: int
    dimensions: Optional[Tuple[int, int]] = None
    duration_seconds: Optional[float] = None
    format: Optional[str] = None
    thumbnail_url: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ContentItem:
    """Social media content item."""
    id: str
    title: str
    description: str
    platform: SocialPlatform
    content_type: ContentType
    scheduled_time: datetime
    timezone: str = "UTC"
    
    # Media
    media_assets: List[MediaAsset] = field(default_factory=list)
    
    # Platform-specific content
    caption: Optional[str] = None
    hashtags: List[str] = field(default_factory=list)
    mentions: List[str] = field(default_factory=list)
    location: Optional[str] = None
    
    # Scheduling
    status: ScheduleStatus = ScheduleStatus.DRAFT
    auto_publish: bool = True
    requires_approval: bool = False
    
    # Analytics
    target_audience: Dict[str, Any] = field(default_factory=dict)
    campaign_id: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.utcnow)
    created_by: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class OptimalTime:
    """Optimal posting time analysis."""
    platform: SocialPlatform
    day_of_week: int  # 0=Monday, 6=Sunday
    hour: int  # 0-23
    minute: int = 0
    confidence_score: float = 0.0
    metric_type: OptimalTimeType = OptimalTimeType.ENGAGEMENT
    audience_segment: Optional[str] = None
    timezone: str = "UTC"
    analysis_date: datetime = field(default_factory=datetime.utcnow)


@dataclass
class SchedulingRule:
    """Content scheduling rule."""
    id: str
    name: str
    description: str
    platform: SocialPlatform
    content_type: ContentType
    
    # Timing rules
    min_interval_hours: int = 1  # Minimum time between posts
    max_posts_per_day: int = 10
    optimal_times: List[OptimalTime] = field(default_factory=list)
    
    # Content rules
    max_hashtags: int = 30
    max_caption_length: int = 2200
    required_media: bool = False
    
    # Approval rules
    requires_approval: bool = False
    approval_threshold: float = 0.8  # Quality score threshold
    
    # Active period
    enabled: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)


class MultiPlatformContentScheduler:
    """Enterprise multi-platform social media content scheduler."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize content scheduler.
        
        Args:
            config: Configuration dict with platform API credentials and settings
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Platform API clients
        self.platform_clients: Dict[SocialPlatform, Any] = {}
        
        # Scheduling
        self.scheduler = AsyncIOScheduler()
        self.scheduled_content: Dict[str, ContentItem] = {}
        self.scheduling_rules: Dict[SocialPlatform, SchedulingRule] = {}
        
        # Optimal timing analysis
        self.optimal_times: Dict[SocialPlatform, List[OptimalTime]] = {}
        self.audience_insights: Dict[str, Any] = {}
        
        # Content queue and management
        self.content_queue: List[ContentItem] = []
        self.published_content: List[ContentItem] = []
        self.failed_content: List[ContentItem] = []
        
        # AI and analytics
        self.content_analyzer = None
        self.engagement_predictor = None
        
        # Performance tracking
        self.scheduling_stats = {
            'total_scheduled': 0,
            'total_published': 0,
            'total_failed': 0,
            'avg_engagement_rate': 0.0,
            'platform_performance': {},
            'last_analysis': None
        }
        
        self._initialize_platform_clients()
        self._load_scheduling_rules()
    
    def _initialize_platform_clients(self) -> None:
        """Initialize social media platform API clients."""
        try:
            # Instagram Business API
            if 'instagram' in self.config:
                instagram_config = self.config['instagram']
                self.platform_clients[SocialPlatform.INSTAGRAM] = httpx.AsyncClient(
                    base_url='https://graph.facebook.com/v18.0',
                    headers={'Authorization': f'Bearer {instagram_config.get("access_token")}'}
                )
                self.logger.info("Instagram API client initialized")
            
            # TikTok Business API
            if 'tiktok' in self.config:
                tiktok_config = self.config['tiktok']
                self.platform_clients[SocialPlatform.TIKTOK] = httpx.AsyncClient(
                    base_url='https://business-api.tiktok.com/open_api/v1.3',
                    headers={'Access-Token': tiktok_config.get("access_token")}
                )
                self.logger.info("TikTok API client initialized")
            
            # YouTube Data API
            if 'youtube' in self.config:
                youtube_config = self.config['youtube']
                self.platform_clients[SocialPlatform.YOUTUBE] = httpx.AsyncClient(
                    base_url='https://www.googleapis.com/youtube/v3',
                    headers={'Authorization': f'Bearer {youtube_config.get("access_token")}'}
                )
                self.logger.info("YouTube API client initialized")
            
            # Twitter API v2
            if 'twitter' in self.config:
                twitter_config = self.config['twitter']
                self.platform_clients[SocialPlatform.TWITTER] = httpx.AsyncClient(
                    base_url='https://api.twitter.com/2',
                    headers={'Authorization': f'Bearer {twitter_config.get("bearer_token")}'}
                )
                self.logger.info("Twitter API client initialized")
            
            # LinkedIn API
            if 'linkedin' in self.config:
                linkedin_config = self.config['linkedin']
                self.platform_clients[SocialPlatform.LINKEDIN] = httpx.AsyncClient(
                    base_url='https://api.linkedin.com/rest',
                    headers={
                        'Authorization': f'Bearer {linkedin_config.get("access_token")}',
                        'LinkedIn-Version': '202309'
                    }
                )
                self.logger.info("LinkedIn API client initialized")
                
        except Exception as e:
            self.logger.error(f"Error initializing platform clients: {e}")
            raise
    
    def _load_scheduling_rules(self) -> None:
        """Load platform-specific scheduling rules."""
        try:
            # Instagram rules
            self.scheduling_rules[SocialPlatform.INSTAGRAM] = SchedulingRule(
                id="instagram_default",
                name="Instagram Default Rules",
                description="Default scheduling rules for Instagram",
                platform=SocialPlatform.INSTAGRAM,
                content_type=ContentType.POST,
                min_interval_hours=1,
                max_posts_per_day=5,
                max_hashtags=30,
                max_caption_length=2200
            )
            
            # TikTok rules
            self.scheduling_rules[SocialPlatform.TIKTOK] = SchedulingRule(
                id="tiktok_default",
                name="TikTok Default Rules",
                description="Default scheduling rules for TikTok",
                platform=SocialPlatform.TIKTOK,
                content_type=ContentType.VIDEO,
                min_interval_hours=2,
                max_posts_per_day=3,
                max_hashtags=100,
                max_caption_length=4000,
                required_media=True
            )
            
            # YouTube rules
            self.scheduling_rules[SocialPlatform.YOUTUBE] = SchedulingRule(
                id="youtube_default",
                name="YouTube Default Rules",
                description="Default scheduling rules for YouTube",
                platform=SocialPlatform.YOUTUBE,
                content_type=ContentType.VIDEO,
                min_interval_hours=24,
                max_posts_per_day=1,
                max_caption_length=5000,
                required_media=True,
                requires_approval=True
            )
            
            # Twitter rules
            self.scheduling_rules[SocialPlatform.TWITTER] = SchedulingRule(
                id="twitter_default",
                name="Twitter Default Rules",
                description="Default scheduling rules for Twitter",
                platform=SocialPlatform.TWITTER,
                content_type=ContentType.POST,
                min_interval_hours=0.5,
                max_posts_per_day=20,
                max_hashtags=10,
                max_caption_length=280
            )
            
            # LinkedIn rules
            self.scheduling_rules[SocialPlatform.LINKEDIN] = SchedulingRule(
                id="linkedin_default",
                name="LinkedIn Default Rules",
                description="Default scheduling rules for LinkedIn",
                platform=SocialPlatform.LINKEDIN,
                content_type=ContentType.POST,
                min_interval_hours=4,
                max_posts_per_day=2,
                max_hashtags=5,
                max_caption_length=3000
            )
            
            self.logger.info("Scheduling rules loaded for all platforms")
            
        except Exception as e:
            self.logger.error(f"Error loading scheduling rules: {e}")
    
    async def schedule_content(
        self,
        content: ContentItem,
        auto_optimize_timing: bool = True
    ) -> str:
        """Schedule content for publishing.
        
        Args:
            content: Content item to schedule
            auto_optimize_timing: Whether to optimize timing automatically
            
        Returns:
            Scheduled content ID
        """
        try:
            # Validate content
            validation_result = await self._validate_content(content)
            if not validation_result['valid']:
                raise ValueError(f"Content validation failed: {validation_result['errors']}")
            
            # Optimize timing if requested
            if auto_optimize_timing:
                optimized_time = await self._optimize_posting_time(content)
                if optimized_time:
                    content.scheduled_time = optimized_time
                    self.logger.info(f"Optimized posting time to {optimized_time}")
            
            # Check scheduling conflicts
            conflicts = await self._check_scheduling_conflicts(content)
            if conflicts:
                self.logger.warning(f"Scheduling conflicts detected: {conflicts}")
                # Adjust timing to avoid conflicts
                content.scheduled_time = await self._resolve_scheduling_conflicts(content, conflicts)
            
            # Set content status
            if content.requires_approval:
                content.status = ScheduleStatus.PENDING_APPROVAL
            else:
                content.status = ScheduleStatus.SCHEDULED
            
            # Store scheduled content
            self.scheduled_content[content.id] = content
            
            # Add to scheduler
            if content.status == ScheduleStatus.SCHEDULED:
                self.scheduler.add_job(
                    self._publish_content,
                    trigger='date',
                    run_date=content.scheduled_time,
                    args=[content.id],
                    id=content.id,
                    replace_existing=True
                )
            
            self.scheduling_stats['total_scheduled'] += 1
            
            self.logger.info(
                f"Scheduled content {content.id} for {content.platform.value} "
                f"at {content.scheduled_time}"
            )
            
            return content.id
            
        except Exception as e:
            self.logger.error(f"Error scheduling content: {e}")
            raise
    
    async def _validate_content(self, content: ContentItem) -> Dict[str, Any]:
        """Validate content against platform rules.
        
        Args:
            content: Content to validate
            
        Returns:
            Validation result
        """
        validation = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        try:
            # Get platform rules
            rules = self.scheduling_rules.get(content.platform)
            if not rules:
                validation['errors'].append(f"No rules found for platform {content.platform.value}")
                validation['valid'] = False
                return validation
            
            # Check caption length
            if content.caption and len(content.caption) > rules.max_caption_length:
                validation['errors'].append(
                    f"Caption too long: {len(content.caption)} > {rules.max_caption_length}"
                )
                validation['valid'] = False
            
            # Check hashtag count
            if len(content.hashtags) > rules.max_hashtags:
                validation['errors'].append(
                    f"Too many hashtags: {len(content.hashtags)} > {rules.max_hashtags}"
                )
                validation['valid'] = False
            
            # Check media requirements
            if rules.required_media and not content.media_assets:
                validation['errors'].append("Media is required but not provided")
                validation['valid'] = False
            
            # Validate media assets
            for asset in content.media_assets:
                media_validation = await self._validate_media_asset(asset, content.platform)
                if not media_validation['valid']:
                    validation['errors'].extend(media_validation['errors'])
                    validation['valid'] = False
            
            # Check scheduling time (not in the past)
            if content.scheduled_time < datetime.utcnow():
                validation['errors'].append("Scheduled time is in the past")
                validation['valid'] = False
            
            # Platform-specific validations
            platform_validation = await self._platform_specific_validation(content)
            validation['errors'].extend(platform_validation.get('errors', []))
            validation['warnings'].extend(platform_validation.get('warnings', []))
            
            if platform_validation.get('errors'):
                validation['valid'] = False
                
        except Exception as e:
            validation['errors'].append(f"Validation error: {str(e)}")
            validation['valid'] = False
        
        return validation
    
    async def _validate_media_asset(
        self,
        asset: MediaAsset,
        platform: SocialPlatform
    ) -> Dict[str, Any]:
        """Validate media asset for specific platform.
        
        Args:
            asset: Media asset to validate
            platform: Target platform
            
        Returns:
            Validation result
        """
        validation = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        try:
            # Platform-specific media requirements
            requirements = {
                SocialPlatform.INSTAGRAM: {
                    'image': {
                        'formats': ['jpg', 'jpeg', 'png'],
                        'max_size_mb': 30,
                        'min_resolution': (320, 320),
                        'max_resolution': (8000, 8000),
                        'aspect_ratios': [(1, 1), (4, 5), (16, 9)]
                    },
                    'video': {
                        'formats': ['mp4', 'mov'],
                        'max_size_mb': 4000,
                        'max_duration_seconds': 60,
                        'min_resolution': (720, 720),
                        'max_resolution': (1080, 1920)
                    }
                },
                SocialPlatform.TIKTOK: {
                    'video': {
                        'formats': ['mp4', 'mov', 'mpeg', 'flv', 'avi', 'webm', '3gp'],
                        'max_size_mb': 287,
                        'max_duration_seconds': 180,
                        'min_resolution': (540, 960),
                        'max_resolution': (1080, 1920),
                        'aspect_ratios': [(9, 16)]
                    }
                },
                SocialPlatform.YOUTUBE: {
                    'video': {
                        'formats': ['mp4', 'mov', 'avi', 'wmv', 'flv', 'webm'],
                        'max_size_mb': 128000,  # 128GB
                        'max_duration_seconds': 43200,  # 12 hours
                        'min_resolution': (426, 240),
                        'max_resolution': (7680, 4320)  # 8K
                    }
                },
                SocialPlatform.TWITTER: {
                    'image': {
                        'formats': ['jpg', 'jpeg', 'png', 'gif', 'webp'],
                        'max_size_mb': 5,
                        'max_resolution': (4096, 4096)
                    },
                    'video': {
                        'formats': ['mp4', 'mov'],
                        'max_size_mb': 512,
                        'max_duration_seconds': 140,
                        'max_resolution': (1920, 1200)
                    }
                }
            }
            
            platform_reqs = requirements.get(platform, {})
            asset_type_reqs = platform_reqs.get(asset.type, {})
            
            if not asset_type_reqs:
                validation['warnings'].append(f"No requirements defined for {asset.type} on {platform.value}")
                return validation
            
            # Check format
            if asset.format and asset.format.lower() not in asset_type_reqs.get('formats', []):
                validation['errors'].append(
                    f"Unsupported format {asset.format} for {platform.value}"
                )
                validation['valid'] = False
            
            # Check file size
            max_size_bytes = asset_type_reqs.get('max_size_mb', 100) * 1024 * 1024
            if asset.size_bytes > max_size_bytes:
                validation['errors'].append(
                    f"File too large: {asset.size_bytes / 1024 / 1024:.1f}MB > "
                    f"{max_size_bytes / 1024 / 1024:.1f}MB"
                )
                validation['valid'] = False
            
            # Check video duration
            if asset.type == 'video' and asset.duration_seconds:
                max_duration = asset_type_reqs.get('max_duration_seconds', 3600)
                if asset.duration_seconds > max_duration:
                    validation['errors'].append(
                        f"Video too long: {asset.duration_seconds}s > {max_duration}s"
                    )
                    validation['valid'] = False
            
            # Check resolution
            if asset.dimensions:
                width, height = asset.dimensions
                
                min_res = asset_type_reqs.get('min_resolution')
                if min_res and (width < min_res[0] or height < min_res[1]):
                    validation['errors'].append(
                        f"Resolution too low: {width}x{height} < {min_res[0]}x{min_res[1]}"
                    )
                    validation['valid'] = False
                
                max_res = asset_type_reqs.get('max_resolution')
                if max_res and (width > max_res[0] or height > max_res[1]):
                    validation['errors'].append(
                        f"Resolution too high: {width}x{height} > {max_res[0]}x{max_res[1]}"
                    )
                    validation['valid'] = False
                
                # Check aspect ratio
                aspect_ratios = asset_type_reqs.get('aspect_ratios', [])
                if aspect_ratios:
                    current_ratio = width / height
                    valid_ratio = False
                    
                    for ar_width, ar_height in aspect_ratios:
                        expected_ratio = ar_width / ar_height
                        if abs(current_ratio - expected_ratio) < 0.1:  # 10% tolerance
                            valid_ratio = True
                            break
                    
                    if not valid_ratio:
                        validation['warnings'].append(
                            f"Aspect ratio {width}:{height} may not be optimal for {platform.value}"
                        )
                        
        except Exception as e:
            validation['errors'].append(f"Media validation error: {str(e)}")
            validation['valid'] = False
        
        return validation
    
    async def _optimize_posting_time(
        self,
        content: ContentItem,
        metric_type: OptimalTimeType = OptimalTimeType.ENGAGEMENT
    ) -> Optional[datetime]:
        """Optimize posting time based on audience insights and platform analytics.
        
        Args:
            content: Content to optimize timing for
            metric_type: Type of metric to optimize for
            
        Returns:
            Optimized posting time or None if no optimization available
        """
        try:
            # Get optimal times for platform
            optimal_times = self.optimal_times.get(content.platform, [])
            
            # If we don't have historical data, use default optimal times
            if not optimal_times:
                optimal_times = await self._get_default_optimal_times(content.platform)
            
            # Filter by metric type
            relevant_times = [
                ot for ot in optimal_times 
                if ot.metric_type == metric_type
            ]
            
            if not relevant_times:
                relevant_times = optimal_times
            
            if not relevant_times:
                return None
            
            # Find best time within next 7 days
            current_time = datetime.utcnow()
            candidate_times = []
            
            for optimal_time in relevant_times:
                # Find next occurrence of this day/time
                for days_ahead in range(7):
                    candidate_date = current_time + timedelta(days=days_ahead)
                    
                    if candidate_date.weekday() == optimal_time.day_of_week:
                        candidate_datetime = candidate_date.replace(
                            hour=optimal_time.hour,
                            minute=optimal_time.minute,
                            second=0,
                            microsecond=0
                        )
                        
                        # Convert to content's timezone
                        if content.timezone != "UTC":
                            tz = pytz.timezone(content.timezone)
                            candidate_datetime = pytz.utc.localize(candidate_datetime).astimezone(tz)
                            candidate_datetime = candidate_datetime.replace(tzinfo=None)
                        
                        # Only consider future times
                        if candidate_datetime > current_time:
                            candidate_times.append({
                                'datetime': candidate_datetime,
                                'confidence': optimal_time.confidence_score,
                                'optimal_time': optimal_time
                            })
            
            if not candidate_times:
                return None
            
            # Sort by confidence score and select best time
            candidate_times.sort(key=lambda x: x['confidence'], reverse=True)
            best_time = candidate_times[0]['datetime']
            
            self.logger.info(
                f"Optimized posting time for {content.platform.value}: {best_time} "
                f"(confidence: {candidate_times[0]['confidence']:.2f})"
            )
            
            return best_time
            
        except Exception as e:
            self.logger.error(f"Error optimizing posting time: {e}")
            return None
    
    async def _get_default_optimal_times(self, platform: SocialPlatform) -> List[OptimalTime]:
        """Get default optimal times for platform based on general best practices.
        
        Args:
            platform: Social media platform
            
        Returns:
            List of default optimal times
        """
        defaults = {
            SocialPlatform.INSTAGRAM: [
                OptimalTime(platform, 1, 11, 0, 0.8, OptimalTimeType.ENGAGEMENT),  # Tuesday 11:00
                OptimalTime(platform, 2, 14, 0, 0.75, OptimalTimeType.ENGAGEMENT),  # Wednesday 14:00
                OptimalTime(platform, 4, 17, 0, 0.7, OptimalTimeType.ENGAGEMENT),   # Friday 17:00
                OptimalTime(platform, 6, 9, 0, 0.65, OptimalTimeType.ENGAGEMENT),   # Sunday 09:00
            ],
            SocialPlatform.TIKTOK: [
                OptimalTime(platform, 1, 6, 0, 0.9, OptimalTimeType.VIEWS),    # Tuesday 06:00
                OptimalTime(platform, 2, 9, 0, 0.85, OptimalTimeType.VIEWS),   # Wednesday 09:00
                OptimalTime(platform, 3, 19, 0, 0.8, OptimalTimeType.VIEWS),   # Thursday 19:00
                OptimalTime(platform, 6, 7, 0, 0.75, OptimalTimeType.VIEWS),   # Sunday 07:00
            ],
            SocialPlatform.YOUTUBE: [
                OptimalTime(platform, 1, 14, 0, 0.8, OptimalTimeType.VIEWS),   # Tuesday 14:00
                OptimalTime(platform, 2, 15, 0, 0.75, OptimalTimeType.VIEWS),  # Wednesday 15:00
                OptimalTime(platform, 5, 12, 0, 0.7, OptimalTimeType.VIEWS),   # Saturday 12:00
                OptimalTime(platform, 6, 11, 0, 0.7, OptimalTimeType.VIEWS),   # Sunday 11:00
            ],
            SocialPlatform.TWITTER: [
                OptimalTime(platform, 1, 9, 0, 0.8, OptimalTimeType.ENGAGEMENT),  # Tuesday 09:00
                OptimalTime(platform, 2, 12, 0, 0.75, OptimalTimeType.ENGAGEMENT), # Wednesday 12:00
                OptimalTime(platform, 3, 15, 0, 0.7, OptimalTimeType.ENGAGEMENT),  # Thursday 15:00
                OptimalTime(platform, 2, 18, 0, 0.65, OptimalTimeType.ENGAGEMENT), # Wednesday 18:00
            ],
            SocialPlatform.LINKEDIN: [
                OptimalTime(platform, 1, 8, 0, 0.85, OptimalTimeType.ENGAGEMENT),  # Tuesday 08:00
                OptimalTime(platform, 2, 10, 0, 0.8, OptimalTimeType.ENGAGEMENT),  # Wednesday 10:00
                OptimalTime(platform, 3, 12, 0, 0.75, OptimalTimeType.ENGAGEMENT), # Thursday 12:00
                OptimalTime(platform, 2, 17, 0, 0.7, OptimalTimeType.ENGAGEMENT),  # Wednesday 17:00
            ]
        }
        
        return defaults.get(platform, [])
    
    async def _check_scheduling_conflicts(self, content: ContentItem) -> List[Dict[str, Any]]:
        """Check for scheduling conflicts with existing content.
        
        Args:
            content: Content to check for conflicts
            
        Returns:
            List of conflicts found
        """
        conflicts = []
        
        try:
            rules = self.scheduling_rules.get(content.platform)
            if not rules:
                return conflicts
            
            # Check minimum interval between posts
            min_interval = timedelta(hours=rules.min_interval_hours)
            conflict_window_start = content.scheduled_time - min_interval
            conflict_window_end = content.scheduled_time + min_interval
            
            for existing_content in self.scheduled_content.values():
                if (existing_content.platform == content.platform and
                    existing_content.id != content.id and
                    existing_content.status == ScheduleStatus.SCHEDULED):
                    
                    if (conflict_window_start <= existing_content.scheduled_time <= conflict_window_end):
                        conflicts.append({
                            'type': 'min_interval',
                            'conflicting_content_id': existing_content.id,
                            'conflicting_time': existing_content.scheduled_time,
                            'min_interval_hours': rules.min_interval_hours
                        })
            
            # Check daily post limit
            same_day_posts = [
                sc for sc in self.scheduled_content.values()
                if (sc.platform == content.platform and
                    sc.scheduled_time.date() == content.scheduled_time.date() and
                    sc.status == ScheduleStatus.SCHEDULED)
            ]
            
            if len(same_day_posts) >= rules.max_posts_per_day:
                conflicts.append({
                    'type': 'daily_limit',
                    'current_count': len(same_day_posts),
                    'max_posts_per_day': rules.max_posts_per_day
                })
                
        except Exception as e:
            self.logger.error(f"Error checking scheduling conflicts: {e}")
        
        return conflicts
    
    async def _resolve_scheduling_conflicts(
        self,
        content: ContentItem,
        conflicts: List[Dict[str, Any]]
    ) -> datetime:
        """Resolve scheduling conflicts by finding alternative time.
        
        Args:
            content: Content with conflicts
            conflicts: List of conflicts to resolve
            
        Returns:
            New conflict-free scheduled time
        """
        try:
            rules = self.scheduling_rules.get(content.platform)
            if not rules:
                return content.scheduled_time
            
            # Start with original time and find next available slot
            candidate_time = content.scheduled_time
            max_attempts = 168  # One week worth of hours
            
            for attempt in range(max_attempts):
                # Check if this time has conflicts
                temp_content = ContentItem(
                    id=f"temp-{uuid.uuid4().hex[:8]}",
                    title=content.title,
                    description=content.description,
                    platform=content.platform,
                    content_type=content.content_type,
                    scheduled_time=candidate_time
                )
                
                check_conflicts = await self._check_scheduling_conflicts(temp_content)
                
                if not check_conflicts:
                    self.logger.info(
                        f"Resolved scheduling conflicts, new time: {candidate_time}"
                    )
                    return candidate_time
                
                # Move to next possible time slot
                candidate_time += timedelta(hours=rules.min_interval_hours)
            
            # If no resolution found, return original time with warning
            self.logger.warning(
                f"Could not resolve scheduling conflicts for {content.id}, "
                f"using original time: {content.scheduled_time}"
            )
            return content.scheduled_time
            
        except Exception as e:
            self.logger.error(f"Error resolving scheduling conflicts: {e}")
            return content.scheduled_time
    
    async def _publish_content(self, content_id: str) -> None:
        """Publish scheduled content to platform.
        
        Args:
            content_id: ID of content to publish
        """
        try:
            content = self.scheduled_content.get(content_id)
            if not content:
                self.logger.error(f"Content {content_id} not found for publishing")
                return
            
            self.logger.info(f"Publishing content {content_id} to {content.platform.value}")
            
            # Publish to specific platform
            if content.platform == SocialPlatform.INSTAGRAM:
                result = await self._publish_to_instagram(content)
            elif content.platform == SocialPlatform.TIKTOK:
                result = await self._publish_to_tiktok(content)
            elif content.platform == SocialPlatform.YOUTUBE:
                result = await self._publish_to_youtube(content)
            elif content.platform == SocialPlatform.TWITTER:
                result = await self._publish_to_twitter(content)
            elif content.platform == SocialPlatform.LINKEDIN:
                result = await self._publish_to_linkedin(content)
            else:
                raise ValueError(f"Publishing not implemented for {content.platform.value}")
            
            if result['success']:
                content.status = ScheduleStatus.PUBLISHED
                content.metadata.update(result.get('metadata', {}))
                self.published_content.append(content)
                self.scheduling_stats['total_published'] += 1
                
                self.logger.info(f"Successfully published content {content_id}")
            else:
                content.status = ScheduleStatus.FAILED
                content.metadata['error'] = result.get('error', 'Unknown error')
                self.failed_content.append(content)
                self.scheduling_stats['total_failed'] += 1
                
                self.logger.error(f"Failed to publish content {content_id}: {result.get('error')}")
            
            # Remove from scheduled content
            if content_id in self.scheduled_content:
                del self.scheduled_content[content_id]
                
        except Exception as e:
            self.logger.error(f"Error publishing content {content_id}: {e}")
            
            # Mark as failed
            if content_id in self.scheduled_content:
                content = self.scheduled_content[content_id]
                content.status = ScheduleStatus.FAILED
                content.metadata['error'] = str(e)
                self.failed_content.append(content)
                self.scheduling_stats['total_failed'] += 1
                del self.scheduled_content[content_id]
    
    async def _publish_to_instagram(self, content: ContentItem) -> Dict[str, Any]:
        """Publish content to Instagram.
        
        Args:
            content: Content to publish
            
        Returns:
            Publishing result
        """
        try:
            client = self.platform_clients.get(SocialPlatform.INSTAGRAM)
            if not client:
                return {'success': False, 'error': 'Instagram client not initialized'}
            
            # Prepare media
            media_objects = []
            for asset in content.media_assets:
                if asset.type == 'image':
                    # Create image media object
                    media_response = await client.post(
                        f"/{self.config['instagram']['page_id']}/media",
                        json={
                            'image_url': asset.url,
                            'caption': content.caption or content.description,
                            'access_token': self.config['instagram']['access_token']
                        }
                    )
                    
                    if media_response.status_code == 200:
                        media_data = media_response.json()
                        media_objects.append(media_data['id'])
                    else:
                        return {
                            'success': False,
                            'error': f'Failed to create media object: {media_response.text}'
                        }
            
            # Publish post
            if media_objects:
                publish_response = await client.post(
                    f"/{self.config['instagram']['page_id']}/media_publish",
                    json={
                        'creation_id': media_objects[0],
                        'access_token': self.config['instagram']['access_token']
                    }
                )
                
                if publish_response.status_code == 200:
                    publish_data = publish_response.json()
                    return {
                        'success': True,
                        'metadata': {
                            'post_id': publish_data.get('id'),
                            'platform_response': publish_data
                        }
                    }
                else:
                    return {
                        'success': False,
                        'error': f'Failed to publish: {publish_response.text}'
                    }
            else:
                return {'success': False, 'error': 'No media objects created'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def _publish_to_twitter(self, content: ContentItem) -> Dict[str, Any]:
        """Publish content to Twitter.
        
        Args:
            content: Content to publish
            
        Returns:
            Publishing result
        """
        try:
            client = self.platform_clients.get(SocialPlatform.TWITTER)
            if not client:
                return {'success': False, 'error': 'Twitter client not initialized'}
            
            # Prepare tweet text
            tweet_text = content.caption or content.description
            if content.hashtags:
                hashtags_text = ' '.join([f'#{tag}' for tag in content.hashtags])
                tweet_text = f"{tweet_text}\n\n{hashtags_text}"
            
            # Ensure tweet is within character limit
            if len(tweet_text) > 280:
                tweet_text = tweet_text[:277] + "..."
            
            # Upload media if present
            media_ids = []
            for asset in content.media_assets:
                # This would require implementing Twitter media upload
                # For now, we'll skip media upload
                pass
            
            # Create tweet
            tweet_data = {'text': tweet_text}
            if media_ids:
                tweet_data['media'] = {'media_ids': media_ids}
            
            response = await client.post('/tweets', json=tweet_data)
            
            if response.status_code == 201:
                tweet_response = response.json()
                return {
                    'success': True,
                    'metadata': {
                        'tweet_id': tweet_response['data']['id'],
                        'platform_response': tweet_response
                    }
                }
            else:
                return {
                    'success': False,
                    'error': f'Failed to create tweet: {response.text}'
                }
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def analyze_optimal_times(
        self,
        platform: SocialPlatform,
        days_back: int = 30
    ) -> List[OptimalTime]:
        """Analyze optimal posting times based on historical performance.
        
        Args:
            platform: Platform to analyze
            days_back: Number of days of historical data to analyze
            
        Returns:
            List of optimal times with confidence scores
        """
        try:
            # This would typically analyze engagement data from the platform
            # For now, we'll use default optimal times
            optimal_times = await self._get_default_optimal_times(platform)
            
            # Store for future use
            self.optimal_times[platform] = optimal_times
            
            self.logger.info(
                f"Analyzed optimal times for {platform.value}: "
                f"found {len(optimal_times)} optimal time slots"
            )
            
            return optimal_times
            
        except Exception as e:
            self.logger.error(f"Error analyzing optimal times: {e}")
            return []
    
    async def get_content_performance(
        self,
        content_id: str
    ) -> Dict[str, Any]:
        """Get performance metrics for published content.
        
        Args:
            content_id: Content ID to get performance for
            
        Returns:
            Performance metrics
        """
        try:
            # Find content in published list
            content = None
            for published_content in self.published_content:
                if published_content.id == content_id:
                    content = published_content
                    break
            
            if not content:
                return {'error': 'Content not found or not published'}
            
            # Get platform-specific metrics
            if content.platform == SocialPlatform.INSTAGRAM:
                metrics = await self._get_instagram_metrics(content)
            elif content.platform == SocialPlatform.TWITTER:
                metrics = await self._get_twitter_metrics(content)
            else:
                metrics = {
                    'views': 0,
                    'likes': 0,
                    'shares': 0,
                    'comments': 0,
                    'engagement_rate': 0.0
                }
            
            return {
                'content_id': content_id,
                'platform': content.platform.value,
                'published_at': content.metadata.get('published_at'),
                'metrics': metrics,
                'retrieved_at': datetime.utcnow()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting content performance: {e}")
            return {'error': str(e)}
    
    def start_scheduler(self) -> None:
        """Start the content scheduler."""
        try:
            if not self.scheduler.running:
                self.scheduler.start()
                self.logger.info("Content scheduler started")
            else:
                self.logger.info("Content scheduler is already running")
                
        except Exception as e:
            self.logger.error(f"Error starting scheduler: {e}")
            raise
    
    def stop_scheduler(self) -> None:
        """Stop the content scheduler."""
        try:
            if self.scheduler.running:
                self.scheduler.shutdown()
                self.logger.info("Content scheduler stopped")
            else:
                self.logger.info("Content scheduler is not running")
                
        except Exception as e:
            self.logger.error(f"Error stopping scheduler: {e}")
    
    def get_scheduling_stats(self) -> Dict[str, Any]:
        """Get scheduling statistics."""
        return {
            **self.scheduling_stats,
            'scheduled_content_count': len(self.scheduled_content),
            'published_content_count': len(self.published_content),
            'failed_content_count': len(self.failed_content),
            'active_platforms': list(self.platform_clients.keys())
        }
    
    async def close(self) -> None:
        """Close scheduler and platform connections."""
        try:
            self.stop_scheduler()
            
            # Close platform clients
            for client in self.platform_clients.values():
                if hasattr(client, 'aclose'):
                    await client.aclose()
            
            self.logger.info("Content scheduler closed")
            
        except Exception as e:
            self.logger.error(f"Error closing scheduler: {e}")


# Example usage
async def example_usage():
    """Example usage of MultiPlatformContentScheduler."""
    
    config = {
        'instagram': {
            'access_token': 'your-instagram-token',
            'page_id': 'your-page-id'
        },
        'twitter': {
            'bearer_token': 'your-twitter-token'
        },
        'youtube': {
            'access_token': 'your-youtube-token'
        }
    }
    
    scheduler = MultiPlatformContentScheduler(config)
    
    try:
        # Create media asset
        media_asset = MediaAsset(
            id="image-001",
            type="image",
            url="https://example.com/image.jpg",
            filename="content-image.jpg",
            size_bytes=1024000,
            dimensions=(1080, 1080),
            format="jpg"
        )
        
        # Create content item
        content = ContentItem(
            id="content-001",
            title="Amazing AI-Generated Content",
            description="Check out this amazing AI-generated content from Ainflue!",
            platform=SocialPlatform.INSTAGRAM,
            content_type=ContentType.POST,
            scheduled_time=datetime.utcnow() + timedelta(hours=2),
            caption="🚀 Exciting news from Ainflue! AI is revolutionizing content creation. #AI #ContentCreation #Innovation",
            hashtags=["AI", "ContentCreation", "Innovation", "Ainflue"],
            media_assets=[media_asset]
        )
        
        # Start scheduler
        scheduler.start_scheduler()
        
        # Schedule content
        content_id = await scheduler.schedule_content(
            content,
            auto_optimize_timing=True
        )
        
        print(f"Content scheduled: {content_id}")
        
        # Analyze optimal times
        optimal_times = await scheduler.analyze_optimal_times(
            SocialPlatform.INSTAGRAM,
            days_back=30
        )
        
        print(f"Found {len(optimal_times)} optimal time slots for Instagram")
        
        # Get scheduling stats
        stats = scheduler.get_scheduling_stats()
        print(f"Scheduling stats: {stats}")
        
        # Wait a bit for demonstration
        await asyncio.sleep(2)
        
    finally:
        await scheduler.close()


if __name__ == "__main__":
    asyncio.run(example_usage())