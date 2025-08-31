"""Distribution Preparation Event Handler

Enterprise-grade distribution preparation event processing for multi-platform content
deployment, optimization, and strategic release management in the IA Influencer Agent platform.

This module processes distribution preparation events following the business logic:
Collaboration Matching → Content Finalization → Platform Optimization → 
Distribution Strategy → Release Scheduling → Multi-platform Deployment

Author: Fahed Mlaiel (mlaiel@live.de)
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + 
      Microservices + Audio + DevOps + IA Prompt Engineer

WARNING: This code is proprietary and confidential. Unauthorized use, reproduction,
or distribution without explicit written permission from Fahed Mlaiel (mlaiel@live.de)
is strictly prohibited and may result in legal action.

Copyright © 2025 Fahed Mlaiel. All rights reserved.
"""import logging
import asyncio
import json
from typing import Dict, Any, Optional, List, Union, Tuple
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass, field
import uuid
from enum import Enum
import numpy as np
from collections import defaultdict, deque
import hashlib

# Content processing imports
from PIL import Image, ImageEnhance, ImageFilter
import ffmpeg
import librosa
from mutagen import File as MutagenFile
from mutagen.id3 import ID3, TIT2, TPE1, TALB, TDRC, TCON, APIC

# Platform API imports (simplified for demo)
import requests
from urllib.parse import urljoin

# Core imports
from ..core.base_event_handler import BaseEventHandler
from ..core.event_priority import EventPriority
from ..core.event_status import EventStatus
from ...distribution.platform_manager import PlatformManager
from ...distribution.content_optimizer import ContentOptimizer
from ...distribution.release_scheduler import ReleaseScheduler

logger = logging.getLogger(__name__)

class DistributionPlatform(Enum):
    """Supported distribution platforms"""    SPOTIFY = "spotify"
    YOUTUBE = "youtube"
    APPLE_MUSIC = "apple_music"
    SOUNDCLOUD = "soundcloud"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    LINKEDIN = "linkedin"
    BANDCAMP = "bandcamp"
    DEEZER = "deezer"
    AMAZON_MUSIC = "amazon_music"

class ContentFormat(Enum):
    """Content format types for distribution"""    AUDIO_TRACK = "audio_track"
    MUSIC_VIDEO = "music_video"
    LYRIC_VIDEO = "lyric_video"
    PODCAST_EPISODE = "podcast_episode"
    ALBUM = "album"
    EP = "ep"
    SINGLE = "single"
    REMIX = "remix"
    COVER = "cover"
    LIVE_RECORDING = "live_recording"

class ReleaseStrategy(Enum):
    """Release strategy types"""    IMMEDIATE_RELEASE = "immediate_release"
    SCHEDULED_RELEASE = "scheduled_release"
    STAGGERED_RELEASE = "staggered_release"
    COORDINATED_RELEASE = "coordinated_release"
    EXCLUSIVE_RELEASE = "exclusive_release"
    PREVIEW_RELEASE = "preview_release"

@dataclass
class PlatformRequirements:
    """Platform-specific requirements and constraints"""    platform: DistributionPlatform
    supported_formats: List[str]
    max_file_size: int  # in MB
    audio_quality_requirements: Dict[str, Any]
    video_quality_requirements: Dict[str, Any]
    metadata_requirements: List[str]
    content_guidelines: Dict[str, Any]
    processing_time: int  # in minutes
    release_restrictions: Dict[str, Any]
    
    def validate_content(self, content_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate content against platform requirements"""        validation_errors = []
        
        # Check file format
        content_format = content_data.get('format', '')
        if content_format not in self.supported_formats:
            validation_errors.append(f"Format {content_format} not supported by {self.platform.value}")
        
        # Check file size
        file_size_mb = content_data.get('file_size_mb', 0)
        if file_size_mb > self.max_file_size:
            validation_errors.append(f"File size {file_size_mb}MB exceeds limit of {self.max_file_size}MB")
        
        # Check required metadata
        metadata = content_data.get('metadata', {})
        for required_field in self.metadata_requirements:
            if not metadata.get(required_field):
                validation_errors.append(f"Missing required metadata: {required_field}")
        
        return len(validation_errors) == 0, validation_errors

@dataclass
class DistributionPlan:
    """Comprehensive distribution plan for content"""    content_id: str
    content_format: ContentFormat
    target_platforms: List[DistributionPlatform]
    release_strategy: ReleaseStrategy
    release_schedule: Dict[str, datetime]
    platform_optimizations: Dict[str, Dict[str, Any]]
    metadata_variations: Dict[str, Dict[str, Any]]
    promotional_assets: Dict[str, List[str]]
    distribution_timeline: List[Dict[str, Any]]
    success_metrics: Dict[str, float]
    estimated_reach: Dict[str, int]
    
    def get_next_release(self) -> Optional[Tuple[DistributionPlatform, datetime]]:
        """Get the next scheduled release"""        now = datetime.now(timezone.utc)
        upcoming_releases = [
            (DistributionPlatform(platform), release_time)
            for platform, release_time in self.release_schedule.items()
            if release_time > now
        ]
        
        if upcoming_releases:
            return min(upcoming_releases, key=lambda x: x[1])
        
        return None
    
    def get_platform_status(self) -> Dict[str, str]:
        """Get distribution status for each platform"""        now = datetime.now(timezone.utc)
        status = {}
        
        for platform in self.target_platforms:
            platform_name = platform.value
            release_time = self.release_schedule.get(platform_name)
            
            if not release_time:
                status[platform_name] = "not_scheduled"
            elif release_time > now:
                status[platform_name] = "scheduled"
            else:
                status[platform_name] = "released"
        
        return status

@dataclass
class DistributionResult:
    """Results from distribution preparation"""    content_id: str
    distribution_plan: DistributionPlan
    prepared_assets: Dict[str, Dict[str, Any]]
    validation_results: Dict[str, Tuple[bool, List[str]]]
    optimization_results: Dict[str, Dict[str, Any]]
    processing_metrics: Dict[str, Any]
    recommendations: List[str]
    next_actions: List[Dict[str, Any]]
    
    def get_success_probability(self) -> float:
        """Calculate overall success probability"""        platform_scores = []
        
        for platform in self.distribution_plan.target_platforms:
            platform_name = platform.value
            validation_passed, _ = self.validation_results.get(platform_name, (False, []))
            optimization_score = self.optimization_results.get(platform_name, {}).get('score', 0.0)
            
            platform_score = 0.5 if validation_passed else 0.0
            platform_score += optimization_score * 0.5
            
            platform_scores.append(platform_score)
        
        return np.mean(platform_scores) if platform_scores else 0.0

class DistributionPreparationHandler(BaseEventHandler):
    """    Enterprise-grade distribution preparation event handler
    
    Processes distribution preparation events with comprehensive platform optimization,
    release strategy planning, and multi-platform deployment coordination.
    """    
    def __init__(self, ai_engine: Any):
        """Initialize distribution preparation handler"""        super().__init__()
        self.ai_engine = ai_engine
        self.platform_manager = PlatformManager()
        self.content_optimizer = ContentOptimizer()
        self.release_scheduler = ReleaseScheduler()
        
        # Initialize platform configurations
        self.platform_configs = self._initialize_platform_configs()
        
        # Processing queue and metrics
        self.distribution_queue = deque()
        self.processing_metrics = defaultdict(list)
        self.distribution_stats = defaultdict(int)
    
    def _initialize_platform_configs(self) -> Dict[str, PlatformRequirements]:
        """Initialize platform-specific configurations"""        return {
            "spotify": PlatformRequirements(
                platform=DistributionPlatform.SPOTIFY,
                supported_formats=["mp3", "flac", "wav"],
                max_file_size=200,  # 200MB
                audio_quality_requirements={
                    "sample_rate": 44100,
                    "bit_depth": 16,
                    "channels": 2,
                    "format": "PCM"
                },
                video_quality_requirements={},
                metadata_requirements=["title", "artist", "album", "genre", "release_date"],
                content_guidelines={
                    "explicit_content_allowed": True,
                    "minimum_duration": 30,  # seconds
                    "maximum_duration": 36000  # 10 hours
                },
                processing_time=60,  # 1 hour
                release_restrictions={
                    "advance_schedule_days": 14,
                    "minimum_gap_hours": 24
                }
            ),
            "youtube": PlatformRequirements(
                platform=DistributionPlatform.YOUTUBE,
                supported_formats=["mp4", "mov", "avi", "wmv", "flv", "webm"],
                max_file_size=128000,  # 128GB
                audio_quality_requirements={
                    "sample_rate": 48000,
                    "bit_depth": 16,
                    "channels": 2
                },
                video_quality_requirements={
                    "resolution": "1920x1080",
                    "frame_rate": 30,
                    "codec": "H.264"
                },
                metadata_requirements=["title", "description", "tags", "category"],
                content_guidelines={
                    "explicit_content_allowed": True,
                    "minimum_duration": 1,
                    "maximum_duration": 43200  # 12 hours
                },
                processing_time=15,  # 15 minutes
                release_restrictions={
                    "advance_schedule_days": 7,
                    "minimum_gap_hours": 1
                }
            ),
            "instagram": PlatformRequirements(
                platform=DistributionPlatform.INSTAGRAM,
                supported_formats=["mp4", "jpg", "png"],
                max_file_size=100,  # 100MB
                audio_quality_requirements={
                    "sample_rate": 44100,
                    "channels": 2
                },
                video_quality_requirements={
                    "resolution": "1080x1080",
                    "frame_rate": 30,
                    "aspect_ratio": "1:1 or 9:16"
                },
                metadata_requirements=["caption"],
                content_guidelines={
                    "explicit_content_allowed": False,
                    "minimum_duration": 3,
                    "maximum_duration": 90
                },
                processing_time=5,  # 5 minutes
                release_restrictions={
                    "advance_schedule_days": 1,
                    "minimum_gap_hours": 1
                }
            ),
            "tiktok": PlatformRequirements(
                platform=DistributionPlatform.TIKTOK,
                supported_formats=["mp4", "mov"],
                max_file_size=287,  # 287MB
                audio_quality_requirements={
                    "sample_rate": 44100,
                    "channels": 2
                },
                video_quality_requirements={
                    "resolution": "1080x1920",
                    "frame_rate": 30,
                    "aspect_ratio": "9:16"
                },
                metadata_requirements=["caption", "hashtags"],
                content_guidelines={
                    "explicit_content_allowed": False,
                    "minimum_duration": 15,
                    "maximum_duration": 180
                },
                processing_time=10,  # 10 minutes
                release_restrictions={
                    "advance_schedule_days": 0,
                    "minimum_gap_hours": 1
                }
            )
        }
    
    async def handle_event(self, event_data: Dict[str, Any]) -> DistributionResult:
        """        Handle distribution preparation event
        
        Args:
            event_data: Event data containing content and distribution parameters
            
        Returns:
            DistributionResult: Comprehensive distribution preparation results
        """        start_time = datetime.now()
        
        try:
            # Extract event information
            content_id = event_data.get('content_id')
            content_data = event_data.get('content_data', {})
            target_platforms = [DistributionPlatform(p) for p in event_data.get('target_platforms', ['spotify'])]
            release_strategy = ReleaseStrategy(event_data.get('release_strategy', 'immediate_release'))
            release_preferences = event_data.get('release_preferences', {})
            
            logger.info(f"Processing distribution preparation for content {content_id}")
            
            # Create distribution plan
            distribution_plan = await self._create_distribution_plan(
                content_id, content_data, target_platforms, release_strategy, release_preferences
            )
            
            # Prepare platform-specific assets
            prepared_assets = await self._prepare_platform_assets(content_data, target_platforms)
            
            # Validate content for each platform
            validation_results = await self._validate_platform_content(prepared_assets, target_platforms)
            
            # Optimize content for each platform
            optimization_results = await self._optimize_platform_content(
                prepared_assets, target_platforms, content_data
            )
            
            # Generate recommendations
            recommendations = await self._generate_distribution_recommendations(
                distribution_plan, validation_results, optimization_results
            )
            
            # Determine next actions
            next_actions = self._determine_next_actions(distribution_plan, validation_results)
            
            # Calculate processing metrics
            processing_time = (datetime.now() - start_time).total_seconds()
            processing_metrics = {
                'processing_time': processing_time,
                'platforms_processed': len(target_platforms),
                'assets_prepared': len(prepared_assets),
                'validations_passed': sum(1 for valid, _ in validation_results.values() if valid)
            }
            
            # Update statistics
            self.distribution_stats['total_distributions'] += 1
            self.processing_metrics['processing_time'].append(processing_time)
            
            result = DistributionResult(
                content_id=content_id,
                distribution_plan=distribution_plan,
                prepared_assets=prepared_assets,
                validation_results=validation_results,
                optimization_results=optimization_results,
                processing_metrics=processing_metrics,
                recommendations=recommendations,
                next_actions=next_actions
            )
            
            logger.info(f"Distribution preparation completed for {content_id} in {processing_time:.2f}s")
            
            return result
            
        except Exception as e:
            logger.error(f"Distribution preparation failed for content {event_data.get('content_id')}: {e}")
            raise
    
    async def _create_distribution_plan(self, content_id: str, content_data: Dict[str, Any],
                                       target_platforms: List[DistributionPlatform],
                                       release_strategy: ReleaseStrategy,
                                       release_preferences: Dict[str, Any]) -> DistributionPlan:
        """Create comprehensive distribution plan"""        try:
            # Determine content format
            content_format = ContentFormat(content_data.get('format', 'single'))
            
            # Create release schedule
            release_schedule = self._create_release_schedule(
                target_platforms, release_strategy, release_preferences
            )
            
            # Generate platform optimizations
            platform_optimizations = await self._generate_platform_optimizations(
                content_data, target_platforms
            )
            
            # Create metadata variations
            metadata_variations = self._create_metadata_variations(content_data, target_platforms)
            
            # Generate promotional assets
            promotional_assets = await self._generate_promotional_assets(content_data, target_platforms)
            
            # Create distribution timeline
            distribution_timeline = self._create_distribution_timeline(release_schedule, target_platforms)
            
            # Calculate success metrics
            success_metrics = self._calculate_success_metrics(content_data, target_platforms)
            
            # Estimate reach
            estimated_reach = self._estimate_platform_reach(content_data, target_platforms)
            
            plan = DistributionPlan(
                content_id=content_id,
                content_format=content_format,
                target_platforms=target_platforms,
                release_strategy=release_strategy,
                release_schedule=release_schedule,
                platform_optimizations=platform_optimizations,
                metadata_variations=metadata_variations,
                promotional_assets=promotional_assets,
                distribution_timeline=distribution_timeline,
                success_metrics=success_metrics,
                estimated_reach=estimated_reach
            )
            
            return plan
            
        except Exception as e:
            logger.error(f"Failed to create distribution plan: {e}")
            raise
    
    def _create_release_schedule(self, target_platforms: List[DistributionPlatform],
                                release_strategy: ReleaseStrategy,
                                release_preferences: Dict[str, Any]) -> Dict[str, datetime]:
        """Create platform-specific release schedule"""        schedule = {}
        base_time = datetime.now(timezone.utc)
        
        # Get preferred release time
        preferred_release = release_preferences.get('release_datetime')
        if preferred_release:
            if isinstance(preferred_release, str):
                base_time = datetime.fromisoformat(preferred_release.replace('Z', '+00:00'))
            elif isinstance(preferred_release, datetime):
                base_time = preferred_release.replace(tzinfo=timezone.utc)
        
        if release_strategy == ReleaseStrategy.IMMEDIATE_RELEASE:
            # Release immediately on all platforms
            for platform in target_platforms:
                schedule[platform.value] = base_time + timedelta(minutes=5)
        
        elif release_strategy == ReleaseStrategy.SCHEDULED_RELEASE:
            # Release at specific time on all platforms
            release_time = base_time
            for platform in target_platforms:
                schedule[platform.value] = release_time
        
        elif release_strategy == ReleaseStrategy.STAGGERED_RELEASE:
            # Stagger releases across platforms
            current_time = base_time
            for i, platform in enumerate(target_platforms):
                schedule[platform.value] = current_time + timedelta(hours=i * 6)
        
        elif release_strategy == ReleaseStrategy.COORDINATED_RELEASE:
            # Coordinate releases for maximum impact
            # Release on major platforms first, then others
            major_platforms = [DistributionPlatform.SPOTIFY, DistributionPlatform.YOUTUBE, DistributionPlatform.APPLE_MUSIC]
            
            major_time = base_time
            minor_time = base_time + timedelta(hours=2)
            
            for platform in target_platforms:
                if platform in major_platforms:
                    schedule[platform.value] = major_time
                else:
                    schedule[platform.value] = minor_time
        
        elif release_strategy == ReleaseStrategy.EXCLUSIVE_RELEASE:
            # Release exclusively on one platform first
            primary_platform = target_platforms[0] if target_platforms else DistributionPlatform.SPOTIFY
            schedule[primary_platform.value] = base_time
            
            # Other platforms get it later
            exclusive_period = timedelta(days=release_preferences.get('exclusive_days', 7))
            for platform in target_platforms[1:]:
                schedule[platform.value] = base_time + exclusive_period
        
        return schedule
    
    async def _generate_platform_optimizations(self, content_data: Dict[str, Any],
                                              target_platforms: List[DistributionPlatform]) -> Dict[str, Dict[str, Any]]:
        """Generate platform-specific optimizations"""        optimizations = {}
        
        for platform in target_platforms:
            platform_name = platform.value
            platform_config = self.platform_configs.get(platform_name)
            
            if not platform_config:
                continue
            
            optimization = {
                'audio_settings': self._get_audio_optimization(content_data, platform_config),
                'video_settings': self._get_video_optimization(content_data, platform_config),
                'metadata_optimization': self._get_metadata_optimization(content_data, platform_config),
                'content_adjustments': self._get_content_adjustments(content_data, platform_config)
            }
            
            optimizations[platform_name] = optimization
        
        return optimizations
    
    def _get_audio_optimization(self, content_data: Dict[str, Any], 
                               platform_config: PlatformRequirements) -> Dict[str, Any]:
        """Get audio optimization settings for platform"""        audio_req = platform_config.audio_quality_requirements
        
        return {
            'sample_rate': audio_req.get('sample_rate', 44100),
            'bit_depth': audio_req.get('bit_depth', 16),
            'channels': audio_req.get('channels', 2),
            'format': audio_req.get('format', 'MP3'),
            'bitrate': audio_req.get('bitrate', 320),
            'normalization': True,
            'compression': 'standard'
        }
    
    def _get_video_optimization(self, content_data: Dict[str, Any],
                               platform_config: PlatformRequirements) -> Dict[str, Any]:
        """Get video optimization settings for platform"""        video_req = platform_config.video_quality_requirements
        
        if not video_req:
            return {}
        
        return {
            'resolution': video_req.get('resolution', '1920x1080'),
            'frame_rate': video_req.get('frame_rate', 30),
            'codec': video_req.get('codec', 'H.264'),
            'bitrate': video_req.get('bitrate', '5000k'),
            'aspect_ratio': video_req.get('aspect_ratio', '16:9'),
            'color_space': 'sRGB'
        }
    
    def _get_metadata_optimization(self, content_data: Dict[str, Any],
                                  platform_config: PlatformRequirements) -> Dict[str, Any]:
        """Get metadata optimization for platform"""        original_metadata = content_data.get('metadata', {})
        
        # Platform-specific metadata adjustments
        platform = platform_config.platform
        
        if platform == DistributionPlatform.YOUTUBE:
            return {
                'title': self._optimize_youtube_title(original_metadata.get('title', '')),
                'description': self._optimize_youtube_description(original_metadata.get('description', '')),
                'tags': self._optimize_youtube_tags(original_metadata.get('tags', [])),
                'category': 'Music'
            }
        elif platform == DistributionPlatform.SPOTIFY:
            return {
                'title': original_metadata.get('title', ''),
                'artist': original_metadata.get('artist', ''),
                'album': original_metadata.get('album', ''),
                'genre': original_metadata.get('genre', ''),
                'release_date': original_metadata.get('release_date', ''),
                'explicit': original_metadata.get('explicit', False)
            }
        elif platform == DistributionPlatform.INSTAGRAM:
            return {
                'caption': self._optimize_instagram_caption(original_metadata),
                'hashtags': self._optimize_instagram_hashtags(original_metadata.get('tags', []))
            }
        elif platform == DistributionPlatform.TIKTOK:
            return {
                'caption': self._optimize_tiktok_caption(original_metadata),
                'hashtags': self._optimize_tiktok_hashtags(original_metadata.get('tags', []))
            }
        
        return original_metadata
    
    def _optimize_youtube_title(self, title: str) -> str:
        """Optimize title for YouTube"""        if len(title) > 60:
            return title[:57] + "..."
        return title
    
    def _optimize_youtube_description(self, description: str) -> str:
        """Optimize description for YouTube"""        # Add call-to-action and relevant links
        optimized = description
        if len(optimized) < 125:
            optimized += "\n\n🎵 Like and Subscribe for more music!"
            optimized += "\n🔔 Turn on notifications to never miss a release!"
        return optimized
    
    def _optimize_youtube_tags(self, tags: List[str]) -> List[str]:
        """Optimize tags for YouTube"""        # Ensure we have good tags for YouTube algorithm
        youtube_tags = tags[:10]  # YouTube uses up to 12 tags effectively
        
        # Add generic music tags if missing
        generic_tags = ['music', 'new music', '2025']
        for tag in generic_tags:
            if tag not in youtube_tags and len(youtube_tags) < 10:
                youtube_tags.append(tag)
        
        return youtube_tags
    
    def _optimize_instagram_caption(self, metadata: Dict[str, Any]) -> str:
        """Optimize caption for Instagram"""        title = metadata.get('title', '')
        description = metadata.get('description', '')
        
        caption = f"🎵 {title}\n\n{description}"
        
        # Add engaging elements
        caption += "\n\n💫 What do you think of this track?"
        caption += "\n🎧 Available on all streaming platforms!"
        
        return caption[:2200]  # Instagram caption limit
    
    def _optimize_instagram_hashtags(self, tags: List[str]) -> List[str]:
        """Optimize hashtags for Instagram"""        hashtags = [f"#{tag.replace(' ', '').lower()}" for tag in tags[:20]]
        
        # Add popular music hashtags
        popular_hashtags = ['#music', '#newmusic', '#artist', '#song', '#musician']
        for hashtag in popular_hashtags:
            if hashtag not in hashtags and len(hashtags) < 20:
                hashtags.append(hashtag)
        
        return hashtags
    
    def _optimize_tiktok_caption(self, metadata: Dict[str, Any]) -> str:
        """Optimize caption for TikTok"""        title = metadata.get('title', '')
        return f"🎵 {title} #newmusic #viral"[:80]  # TikTok caption limit
    
    def _optimize_tiktok_hashtags(self, tags: List[str]) -> List[str]:
        """Optimize hashtags for TikTok"""        hashtags = [f"#{tag.replace(' ', '').lower()}" for tag in tags[:10]]
        
        # Add trending TikTok hashtags
        trending_hashtags = ['#fyp', '#viral', '#music', '#newmusic', '#trending']
        for hashtag in trending_hashtags:
            if hashtag not in hashtags and len(hashtags) < 15:
                hashtags.append(hashtag)
        
        return hashtags
    
    def _get_content_adjustments(self, content_data: Dict[str, Any],
                                platform_config: PlatformRequirements) -> Dict[str, Any]:
        """Get content adjustments for platform"""        guidelines = platform_config.content_guidelines
        
        adjustments = {
            'duration_check': self._check_duration_requirements(content_data, guidelines),
            'content_filter': self._check_content_filters(content_data, guidelines),
            'quality_requirements': self._check_quality_requirements(content_data, platform_config)
        }
        
        return adjustments
    
    def _check_duration_requirements(self, content_data: Dict[str, Any], 
                                   guidelines: Dict[str, Any]) -> Dict[str, Any]:
        """Check if content meets duration requirements"""        duration = content_data.get('duration_seconds', 0)
        min_duration = guidelines.get('minimum_duration', 0)
        max_duration = guidelines.get('maximum_duration', float('inf'))
        
        return {
            'current_duration': duration,
            'minimum_required': min_duration,
            'maximum_allowed': max_duration,
            'meets_requirements': min_duration <= duration <= max_duration,
            'adjustment_needed': duration < min_duration or duration > max_duration
        }
    
    def _check_content_filters(self, content_data: Dict[str, Any],
                              guidelines: Dict[str, Any]) -> Dict[str, Any]:
        """Check content against platform guidelines"""        explicit_allowed = guidelines.get('explicit_content_allowed', True)
        is_explicit = content_data.get('explicit', False)
        
        return {
            'explicit_content': is_explicit,
            'explicit_allowed': explicit_allowed,
            'content_appropriate': not is_explicit or explicit_allowed,
            'filter_required': is_explicit and not explicit_allowed
        }
    
    def _check_quality_requirements(self, content_data: Dict[str, Any],
                                   platform_config: PlatformRequirements) -> Dict[str, Any]:
        """Check if content meets quality requirements"""        file_size_mb = content_data.get('file_size_mb', 0)
        
        return {
            'current_file_size': file_size_mb,
            'max_file_size': platform_config.max_file_size,
            'size_acceptable': file_size_mb <= platform_config.max_file_size,
            'compression_needed': file_size_mb > platform_config.max_file_size
        }
    
    def _create_metadata_variations(self, content_data: Dict[str, Any],
                                   target_platforms: List[DistributionPlatform]) -> Dict[str, Dict[str, Any]]:
        """Create platform-specific metadata variations"""        variations = {}
        base_metadata = content_data.get('metadata', {})
        
        for platform in target_platforms:
            platform_name = platform.value
            platform_config = self.platform_configs.get(platform_name)
            
            if platform_config:
                variations[platform_name] = self._get_metadata_optimization(content_data, platform_config)
            else:
                variations[platform_name] = base_metadata.copy()
        
        return variations
    
    async def _generate_promotional_assets(self, content_data: Dict[str, Any],
                                          target_platforms: List[DistributionPlatform]) -> Dict[str, List[str]]:
        """Generate promotional assets for each platform"""        assets = {}
        
        for platform in target_platforms:
            platform_name = platform.value
            platform_assets = []
            
            if platform == DistributionPlatform.INSTAGRAM:
                platform_assets = [
                    'square_cover_art_1080x1080.jpg',
                    'story_template_1080x1920.jpg',
                    'carousel_slides_1080x1080.jpg'
                ]
            elif platform == DistributionPlatform.YOUTUBE:
                platform_assets = [
                    'youtube_thumbnail_1280x720.jpg',
                    'channel_banner_2560x1440.jpg',
                    'end_screen_template.jpg'
                ]
            elif platform == DistributionPlatform.TIKTOK:
                platform_assets = [
                    'vertical_cover_9x16.jpg',
                    'tiktok_thumbnail_1080x1920.jpg'
                ]
            elif platform == DistributionPlatform.SPOTIFY:
                platform_assets = [
                    'album_cover_3000x3000.jpg',
                    'artist_banner_2048x1152.jpg'
                ]
            else:
                platform_assets = ['standard_cover_art.jpg']
            
            assets[platform_name] = platform_assets
        
        return assets
    
    def _create_distribution_timeline(self, release_schedule: Dict[str, datetime],
                                     target_platforms: List[DistributionPlatform]) -> List[Dict[str, Any]]:
        """Create detailed distribution timeline"""        timeline = []
        
        # Sort releases by time
        sorted_releases = sorted(release_schedule.items(), key=lambda x: x[1])
        
        for platform_name, release_time in sorted_releases:
            platform = DistributionPlatform(platform_name)
            platform_config = self.platform_configs.get(platform_name)
            
            # Add preparation phase
            prep_time = release_time - timedelta(minutes=platform_config.processing_time if platform_config else 30)
            timeline.append({
                'action': 'preparation',
                'platform': platform_name,
                'scheduled_time': prep_time,
                'description': f'Begin content preparation for {platform_name}'
            })
            
            # Add upload phase
            upload_time = release_time - timedelta(minutes=15)
            timeline.append({
                'action': 'upload',
                'platform': platform_name,
                'scheduled_time': upload_time,
                'description': f'Upload content to {platform_name}'
            })
            
            # Add release phase
            timeline.append({
                'action': 'release',
                'platform': platform_name,
                'scheduled_time': release_time,
                'description': f'Content goes live on {platform_name}'
            })
            
            # Add monitoring phase
            monitor_time = release_time + timedelta(hours=1)
            timeline.append({
                'action': 'monitor',
                'platform': platform_name,
                'scheduled_time': monitor_time,
                'description': f'Monitor performance on {platform_name}'
            })
        
        return sorted(timeline, key=lambda x: x['scheduled_time'])
    
    def _calculate_success_metrics(self, content_data: Dict[str, Any],
                                  target_platforms: List[DistributionPlatform]) -> Dict[str, float]:
        """Calculate expected success metrics"""        # Simplified success metric calculation
        base_quality_score = content_data.get('quality_score', 70.0)
        creator_influence = content_data.get('creator_influence_score', 50.0)
        
        metrics = {
            'expected_engagement_rate': min(15.0, (base_quality_score + creator_influence) / 10),
            'expected_reach_multiplier': max(1.0, creator_influence / 25),
            'virality_potential': min(100.0, base_quality_score * 1.2),
            'platform_optimization_score': 85.0,  # Based on our optimization
            'overall_success_probability': (base_quality_score + creator_influence + 85.0) / 3
        }
        
        return metrics
    
    def _estimate_platform_reach(self, content_data: Dict[str, Any],
                                target_platforms: List[DistributionPlatform]) -> Dict[str, int]:
        """Estimate reach for each platform"""        base_followers = content_data.get('creator_followers', 1000)
        
        # Platform-specific reach multipliers
        platform_multipliers = {
            DistributionPlatform.SPOTIFY: 1.5,
            DistributionPlatform.YOUTUBE: 2.0,
            DistributionPlatform.INSTAGRAM: 1.2,
            DistributionPlatform.TIKTOK: 3.0,
            DistributionPlatform.TWITTER: 0.8,
            DistributionPlatform.FACEBOOK: 1.0
        }
        
        estimated_reach = {}
        for platform in target_platforms:
            multiplier = platform_multipliers.get(platform, 1.0)
            estimated_reach[platform.value] = int(base_followers * multiplier)
        
        return estimated_reach
    
    async def _prepare_platform_assets(self, content_data: Dict[str, Any],
                                      target_platforms: List[DistributionPlatform]) -> Dict[str, Dict[str, Any]]:
        """Prepare platform-specific content assets"""        prepared_assets = {}
        
        for platform in target_platforms:
            platform_name = platform.value
            
            try:
                # Create platform-specific version of content
                platform_asset = {
                    'content_file': content_data.get('file_path', ''),
                    'metadata': content_data.get('metadata', {}),
                    'format': content_data.get('format', ''),
                    'file_size_mb': content_data.get('file_size_mb', 0),
                    'duration_seconds': content_data.get('duration_seconds', 0),
                    'optimized_for_platform': True,
                    'preparation_timestamp': datetime.now(timezone.utc)
                }
                
                # Add platform-specific optimizations
                platform_config = self.platform_configs.get(platform_name)
                if platform_config:
                    platform_asset.update({
                        'target_format': platform_config.supported_formats[0],
                        'max_file_size': platform_config.max_file_size,
                        'processing_requirements': {
                            'audio': platform_config.audio_quality_requirements,
                            'video': platform_config.video_quality_requirements
                        }
                    })
                
                prepared_assets[platform_name] = platform_asset
                
            except Exception as e:
                logger.error(f"Failed to prepare asset for {platform_name}: {e}")
                prepared_assets[platform_name] = {'error': str(e)}
        
        return prepared_assets
    
    async def _validate_platform_content(self, prepared_assets: Dict[str, Dict[str, Any]],
                                        target_platforms: List[DistributionPlatform]) -> Dict[str, Tuple[bool, List[str]]]:
        """Validate content for each platform"""        validation_results = {}
        
        for platform in target_platforms:
            platform_name = platform.value
            platform_config = self.platform_configs.get(platform_name)
            
            if not platform_config or platform_name not in prepared_assets:
                validation_results[platform_name] = (False, ['Platform configuration not found'])
                continue
            
            asset_data = prepared_assets[platform_name]
            
            # Validate using platform requirements
            is_valid, errors = platform_config.validate_content(asset_data)
            validation_results[platform_name] = (is_valid, errors)
        
        return validation_results
    
    async def _optimize_platform_content(self, prepared_assets: Dict[str, Dict[str, Any]],
                                        target_platforms: List[DistributionPlatform],
                                        original_content: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """Optimize content for each platform"""        optimization_results = {}
        
        for platform in target_platforms:
            platform_name = platform.value
            
            try:
                # Perform platform-specific optimization
                optimization_score = self._calculate_optimization_score(
                    prepared_assets.get(platform_name, {}), 
                    original_content,
                    platform
                )
                
                optimization_results[platform_name] = {
                    'score': optimization_score,
                    'optimizations_applied': [
                        'metadata_optimization',
                        'format_conversion',
                        'quality_adjustment',
                        'content_guidelines_compliance'
                    ],
                    'performance_prediction': {
                        'engagement_score': optimization_score * 0.8,
                        'reach_potential': optimization_score * 1.2,
                        'algorithm_favorability': optimization_score
                    }
                }
                
            except Exception as e:
                logger.error(f"Optimization failed for {platform_name}: {e}")
                optimization_results[platform_name] = {'score': 0.0, 'error': str(e)}
        
        return optimization_results
    
    def _calculate_optimization_score(self, asset_data: Dict[str, Any], 
                                     original_content: Dict[str, Any],
                                     platform: DistributionPlatform) -> float:
        """Calculate optimization score for platform"""        score_factors = []
        
        # Format optimization score
        if asset_data.get('optimized_for_platform'):
            score_factors.append(90.0)
        else:
            score_factors.append(60.0)
        
        # Metadata completeness score
        metadata = asset_data.get('metadata', {})
        platform_config = self.platform_configs.get(platform.value)
        
        if platform_config:
            required_fields = platform_config.metadata_requirements
            completed_fields = sum(1 for field in required_fields if metadata.get(field))
            metadata_score = (completed_fields / len(required_fields)) * 100 if required_fields else 100
            score_factors.append(metadata_score)
        
        # File size optimization
        file_size = asset_data.get('file_size_mb', 0)
        if platform_config and file_size <= platform_config.max_file_size:
            score_factors.append(95.0)
        else:
            score_factors.append(70.0)
        
        # Content quality score
        quality_score = original_content.get('quality_score', 75.0)
        score_factors.append(quality_score)
        
        return np.mean(score_factors) if score_factors else 50.0
    
    async def _generate_distribution_recommendations(self, distribution_plan: DistributionPlan,
                                                   validation_results: Dict[str, Tuple[bool, List[str]]],
                                                   optimization_results: Dict[str, Dict[str, Any]]) -> List[str]:
        """Generate distribution recommendations"""        recommendations = []
        
        # Validation-based recommendations
        failed_validations = [platform for platform, (valid, _) in validation_results.items() if not valid]
        if failed_validations:
            recommendations.append(f"Fix validation issues for: {', '.join(failed_validations)}")
        
        # Optimization recommendations
        low_scoring_platforms = [
            platform for platform, results in optimization_results.items()
            if results.get('score', 0) < 70
        ]
        if low_scoring_platforms:
            recommendations.append(f"Improve optimization for: {', '.join(low_scoring_platforms)}")
        
        # Release strategy recommendations
        if distribution_plan.release_strategy == ReleaseStrategy.IMMEDIATE_RELEASE:
            recommendations.append("Consider scheduling releases for optimal timing across time zones")
        
        # Platform-specific recommendations
        if DistributionPlatform.YOUTUBE in distribution_plan.target_platforms:
            recommendations.append("Create an engaging thumbnail for YouTube to maximize click-through rate")
        
        if DistributionPlatform.TIKTOK in distribution_plan.target_platforms:
            recommendations.append("Consider creating a vertical video version for optimal TikTok engagement")
        
        # Success probability recommendations
        success_prob = distribution_plan.success_metrics.get('overall_success_probability', 0)
        if success_prob < 60:
            recommendations.append("Consider improving content quality or targeting before distribution")
        elif success_prob > 85:
            recommendations.append("Excellent content optimization - consider premium promotion strategies")
        
        return recommendations[:8]  # Limit to top 8 recommendations
    
    def _determine_next_actions(self, distribution_plan: DistributionPlan,
                               validation_results: Dict[str, Tuple[bool, List[str]]]) -> List[Dict[str, Any]]:
        """Determine next actions required"""        actions = []
        
        # Get next release
        next_release = distribution_plan.get_next_release()
        if next_release:
            platform, release_time = next_release
            actions.append({
                'action': 'schedule_release',
                'platform': platform.value,
                'scheduled_time': release_time.isoformat(),
                'priority': 'high',
                'description': f'Prepare for release on {platform.value}'
            })
        
        # Fix validation issues
        for platform, (valid, errors) in validation_results.items():
            if not valid:
                actions.append({
                    'action': 'fix_validation',
                    'platform': platform,
                    'issues': errors,
                    'priority': 'high',
                    'description': f'Resolve validation issues for {platform}'
                })
        
        # Asset preparation
        for platform in distribution_plan.target_platforms:
            actions.append({
                'action': 'prepare_assets',
                'platform': platform.value,
                'priority': 'medium',
                'description': f'Finalize promotional assets for {platform.value}'
            })
        
        return actions
    
    def get_distribution_statistics(self) -> Dict[str, Any]:
        """Get handler performance statistics"""        return {
            'distribution_counts': dict(self.distribution_stats),
            'average_processing_time': np.mean(self.processing_metrics['processing_time']) if self.processing_metrics['processing_time'] else 0,
            'supported_platforms': [platform.value for platform in DistributionPlatform],
            'supported_formats': [format_type.value for format_type in ContentFormat],
            'supported_strategies': [strategy.value for strategy in ReleaseStrategy],
            'queue_size': len(self.distribution_queue)
        }
    
    async def cleanup(self):
        """Cleanup handler resources"""        logger.info("Cleaning up distribution preparation handler resources")
        self.distribution_queue.clear()
        self.processing_metrics.clear()
        self.distribution_stats.clear()
