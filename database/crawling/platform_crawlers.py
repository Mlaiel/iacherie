"""Enterprise Platform Crawlers Database Module

Specialized database layer for platform-specific crawling operations
including YouTube, TikTok, Instagram, Twitter, and generic web crawlers.

PROTECTION NOTICE:
This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution is strictly prohibited.
Legal action will be taken against copyright infringement.

Author: Fahed Mlaiel <mlaiel@live.de>
Team Specialties: Lead AI Developer + Backend Senior + ML Engineer + DBA + Security + 
                 Microservices + Audio + DevOps + IA Prompt Engineer
Copyright: All rights reserved
"""

from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc, func, text
from uuid import uuid4
import json
import asyncio
from enum import Enum

from ..core.base import DatabaseManager
from ..models.crawling_models import (
    PlatformCrawler, CrawlerSession, CrawlerConfiguration,
    PlatformTarget, CrawlerResult, CrawlerError
)
from ..core.exceptions import (
    DatabaseError, CrawlerConfigurationError, PlatformAPIError,
    RateLimitExceededError, CrawlerAuthenticationError
)


class PlatformType(Enum):
    """
Supported platform types for specialized crawling."""

    YOUTUBE = "youtube"
    TIKTOK = "tiktok"
    INSTAGRAM = "instagram"
    TWITTER = "twitter"
    SPOTIFY = "spotify"
    SOUNDCLOUD = "soundcloud"
    GENERIC_WEB = "generic_web"
    SOCIAL_MEDIA = "social_media"


class CrawlerCapability(Enum):
    """Crawler capabilities and features."""

    CONTENT_DISCOVERY = "content_discovery"
    METADATA_EXTRACTION = "metadata_extraction"
    ENGAGEMENT_TRACKING = "engagement_tracking"
    USER_PROFILING = "user_profiling"
    TREND_ANALYSIS = "trend_analysis"
    REAL_TIME_MONITORING = "real_time_monitoring"
    CONTENT_VERIFICATION = "content_verification"
    COPYRIGHT_DETECTION = "copyright_detection"


class CrawlerStatus(Enum):
    """Crawler operational status."""

    ACTIVE = "active"
    PAUSED = "paused"
    DISABLED = "disabled"
    MAINTENANCE = "maintenance"
    ERROR = "error"
    RATE_LIMITED = "rate_limited"


class PlatformCrawlerManager(DatabaseManager):
    """
    Enterprise platform crawler database manager for multi-platform
    content discovery and surveillance operations.
    
    Manages specialized crawlers for:
    - YouTube: Video content, creator channels, trending analysis
    - TikTok: Short-form content, viral trends, user engagement
    - Instagram: Visual content, stories, IGTV, reels
    - Twitter/X: Real-time feeds, hashtag tracking, sentiment
    - Spotify: Music tracks, artist profiles, playlist analysis
    - SoundCloud: Independent music, emerging artists
    - Generic Web: Custom website surveillance
    """
    
    def __init__(self, db_session: Session):
        """
Initialize platform crawler manager."""
        super().__init__(db_session)
        self.platform_configs = {}
        self._load_platform_configurations()
        
    async def register_platform_crawler(
        self,
        platform_type: PlatformType,
        crawler_config: Dict[str, Any],
        capabilities: List[CrawlerCapability],
        user_id: str
    ) -> str:
        """
        Register a new platform-specific crawler configuration.
        
        Args:
            platform_type: Target platform type
            crawler_config: Platform-specific configuration
            capabilities: List of crawler capabilities
            user_id: User identifier for ownership
            
        Returns:
            Crawler ID for future operations
            
        Raises:
            CrawlerConfigurationError: If configuration is invalid
        """
        try:
            crawler_id = str(uuid4())
            
            # Validate platform configuration
            await self._validate_platform_config(platform_type, crawler_config)
            
            # Create crawler record
            crawler = PlatformCrawler(
                crawler_id=crawler_id,
                platform_type=platform_type.value,
                configuration=crawler_config,
                capabilities=[cap.value for cap in capabilities],
                user_id=user_id,
                status=CrawlerStatus.ACTIVE.value,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            self.db_session.add(crawler)
            await self.db_session.commit()
            
            # Initialize platform-specific settings
            await self._initialize_platform_settings(crawler_id, platform_type, crawler_config)
            
            return crawler_id
            
        except Exception as e:
            await self.db_session.rollback()
            raise CrawlerConfigurationError(
                f"Failed to register platform crawler: {str(e)}"
            )
    
    async def configure_youtube_crawler(
        self,
        api_key: str,
        channel_targets: List[str],
        search_keywords: List[str],
        content_types: List[str],
        user_id: str
    ) -> str:
        """
        Configure specialized YouTube crawler for content discovery.
        
        Args:
            api_key: YouTube Data API key
            channel_targets: List of channel IDs to monitor
            search_keywords: Keywords for content discovery
            content_types: Types of content to crawl (videos, shorts, live)
            user_id: User identifier
            
        Returns:
            Crawler ID for YouTube operations
        """
        try:
            crawler_config = {
                "api_key": api_key,
                "base_url": "https://www.googleapis.com/youtube/v3",
                "channel_targets": channel_targets,
                "search_keywords": search_keywords,
                "content_types": content_types,
                "rate_limit": {
                    "requests_per_day": 10000,
                    "quota_units_per_request": 100,
                    "concurrent_requests": 5
                },
                "extraction_settings": {
                    "include_thumbnails": True,
                    "include_transcripts": True,
                    "include_comments": True,
                    "include_analytics": True,
                    "max_results_per_query": 50
                },
                "monitoring_settings": {
                    "check_interval_minutes": 30,
                    "detect_new_uploads": True,
                    "track_view_changes": True,
                    "monitor_comments": True
                }
            }
            
            capabilities = [
                CrawlerCapability.CONTENT_DISCOVERY,
                CrawlerCapability.METADATA_EXTRACTION,
                CrawlerCapability.ENGAGEMENT_TRACKING,
                CrawlerCapability.TREND_ANALYSIS,
                CrawlerCapability.REAL_TIME_MONITORING
            ]
            
            return await self.register_platform_crawler(
                PlatformType.YOUTUBE,
                crawler_config,
                capabilities,
                user_id
            )
            
        except Exception as e:
            raise PlatformAPIError(f"YouTube crawler configuration failed: {str(e)}")
    
    async def configure_tiktok_crawler(
        self,
        auth_token: str,
        hashtag_targets: List[str],
        user_targets: List[str],
        trend_categories: List[str],
        user_id: str
    ) -> str:
        """
        Configure specialized TikTok crawler for viral content discovery.
        
        Args:
            auth_token: TikTok API authentication token
            hashtag_targets: Hashtags to monitor
            user_targets: User profiles to track
            trend_categories: Categories for trend analysis
            user_id: User identifier
            
        Returns:
            Crawler ID for TikTok operations
        """
        try:
            crawler_config = {
                "auth_token": auth_token,
                "base_url": "https://open-api.tiktok.com/platform/",
                "hashtag_targets": hashtag_targets,
                "user_targets": user_targets,
                "trend_categories": trend_categories,
                "rate_limit": {
                    "requests_per_hour": 1000,
                    "requests_per_day": 10000,
                    "concurrent_requests": 3
                },
                "extraction_settings": {
                    "include_video_metadata": True,
                    "include_audio_fingerprint": True,
                    "include_effects_used": True,
                    "include_engagement_metrics": True,
                    "max_videos_per_hashtag": 100
                },
                "monitoring_settings": {
                    "check_interval_minutes": 15,
                    "detect_viral_content": True,
                    "track_engagement_velocity": True,
                    "monitor_trending_sounds": True
                }
            }
            
            capabilities = [
                CrawlerCapability.CONTENT_DISCOVERY,
                CrawlerCapability.TREND_ANALYSIS,
                CrawlerCapability.ENGAGEMENT_TRACKING,
                CrawlerCapability.REAL_TIME_MONITORING,
                CrawlerCapability.COPYRIGHT_DETECTION
            ]
            
            return await self.register_platform_crawler(
                PlatformType.TIKTOK,
                crawler_config,
                capabilities,
                user_id
            )
            
        except Exception as e:
            raise PlatformAPIError(f"TikTok crawler configuration failed: {str(e)}")
    
    async def configure_instagram_crawler(
        self,
        access_token: str,
        account_targets: List[str],
        hashtag_targets: List[str],
        location_targets: List[str],
        user_id: str
    ) -> str:
        """
        Configure specialized Instagram crawler for visual content discovery.
        
        Args:
            access_token: Instagram Graph API access token
            account_targets: Instagram accounts to monitor
            hashtag_targets: Hashtags to track
            location_targets: Location-based content discovery
            user_id: User identifier
            
        Returns:
            Crawler ID for Instagram operations
        """
        try:
            crawler_config = {
                "access_token": access_token,
                "base_url": "https://graph.instagram.com",
                "account_targets": account_targets,
                "hashtag_targets": hashtag_targets,
                "location_targets": location_targets,
                "rate_limit": {
                    "requests_per_hour": 200,
                    "requests_per_day": 4800,
                    "concurrent_requests": 2
                },
                "extraction_settings": {
                    "include_posts": True,
                    "include_stories": True,
                    "include_reels": True,
                    "include_igtv": True,
                    "include_image_analysis": True,
                    "max_posts_per_account": 50
                },
                "monitoring_settings": {
                    "check_interval_minutes": 45,
                    "detect_new_posts": True,
                    "track_story_updates": True,
                    "monitor_engagement_patterns": True
                }
            }
            
            capabilities = [
                CrawlerCapability.CONTENT_DISCOVERY,
                CrawlerCapability.METADATA_EXTRACTION,
                CrawlerCapability.ENGAGEMENT_TRACKING,
                CrawlerCapability.USER_PROFILING,
                CrawlerCapability.CONTENT_VERIFICATION
            ]
            
            return await self.register_platform_crawler(
                PlatformType.INSTAGRAM,
                crawler_config,
                capabilities,
                user_id
            )
            
        except Exception as e:
            raise PlatformAPIError(f"Instagram crawler configuration failed: {str(e)}")
    
    async def configure_twitter_crawler(
        self,
        bearer_token: str,
        keyword_targets: List[str],
        user_targets: List[str],
        hashtag_targets: List[str],
        user_id: str
    ) -> str:
        """
        Configure specialized Twitter/X crawler for real-time content monitoring.
        
        Args:
            bearer_token: Twitter API v2 bearer token
            keyword_targets: Keywords to monitor
            user_targets: User accounts to track
            hashtag_targets: Hashtags to follow
            user_id: User identifier
            
        Returns:
            Crawler ID for Twitter operations
        """
        try:
            crawler_config = {
                "bearer_token": bearer_token,
                "base_url": "https://api.twitter.com/2",
                "keyword_targets": keyword_targets,
                "user_targets": user_targets,
                "hashtag_targets": hashtag_targets,
                "rate_limit": {
                    "requests_per_15min": 300,
                    "tweets_per_month": 500000,
                    "concurrent_requests": 1
                },
                "extraction_settings": {
                    "include_media": True,
                    "include_retweets": True,
                    "include_replies": True,
                    "include_thread_context": True,
                    "include_user_metrics": True,
                    "max_tweets_per_query": 100
                },
                "monitoring_settings": {
                    "real_time_streaming": True,
                    "check_interval_minutes": 5,
                    "detect_viral_tweets": True,
                    "track_sentiment_changes": True
                }
            }
            
            capabilities = [
                CrawlerCapability.CONTENT_DISCOVERY,
                CrawlerCapability.REAL_TIME_MONITORING,
                CrawlerCapability.TREND_ANALYSIS,
                CrawlerCapability.USER_PROFILING,
                CrawlerCapability.ENGAGEMENT_TRACKING
            ]
            
            return await self.register_platform_crawler(
                PlatformType.TWITTER,
                crawler_config,
                capabilities,
                user_id
            )
            
        except Exception as e:
            raise PlatformAPIError(f"Twitter crawler configuration failed: {str(e)}")
    
    async def configure_spotify_crawler(
        self,
        client_id: str,
        client_secret: str,
        artist_targets: List[str],
        playlist_targets: List[str],
        genre_targets: List[str],
        user_id: str
    ) -> str:
        """
        Configure specialized Spotify crawler for music content discovery.
        
        Args:
            client_id: Spotify API client ID
            client_secret: Spotify API client secret
            artist_targets: Artist IDs to monitor
            playlist_targets: Playlist IDs to track
            genre_targets: Music genres to discover
            user_id: User identifier
            
        Returns:
            Crawler ID for Spotify operations
        """
        try:
            crawler_config = {
                "client_id": client_id,
                "client_secret": client_secret,
                "base_url": "https://api.spotify.com/v1",
                "artist_targets": artist_targets,
                "playlist_targets": playlist_targets,
                "genre_targets": genre_targets,
                "rate_limit": {
                    "requests_per_second": 10,
                    "requests_per_hour": 3600,
                    "concurrent_requests": 5
                },
                "extraction_settings": {
                    "include_audio_features": True,
                    "include_track_analytics": True,
                    "include_artist_data": True,
                    "include_album_metadata": True,
                    "include_playlist_updates": True,
                    "max_tracks_per_playlist": 1000
                },
                "monitoring_settings": {
                    "check_interval_minutes": 60,
                    "detect_new_releases": True,
                    "track_popularity_changes": True,
                    "monitor_playlist_additions": True
                }
            }
            
            capabilities = [
                CrawlerCapability.CONTENT_DISCOVERY,
                CrawlerCapability.METADATA_EXTRACTION,
                CrawlerCapability.TREND_ANALYSIS,
                CrawlerCapability.USER_PROFILING,
                CrawlerCapability.COPYRIGHT_DETECTION
            ]
            
            return await self.register_platform_crawler(
                PlatformType.SPOTIFY,
                crawler_config,
                capabilities,
                user_id
            )
            
        except Exception as e:
            raise PlatformAPIError(f"Spotify crawler configuration failed: {str(e)}")
    
    async def get_crawler_status(self, crawler_id: str) -> Dict[str, Any]:
        """
        Get comprehensive status information for a crawler.
        
        Args:
            crawler_id: Crawler identifier
            
        Returns:
            Dictionary containing crawler status and metrics
        """
        try:
            crawler = await self.db_session.query(PlatformCrawler).filter(
                PlatformCrawler.crawler_id == crawler_id
            ).first()
            
            if not crawler:
                raise DatabaseError(f"Crawler {crawler_id} not found")
            
            # Get recent session statistics
            recent_sessions = await self._get_recent_sessions(crawler_id, hours=24)
            session_stats = await self._calculate_session_statistics(recent_sessions)
            
            # Get error statistics
            error_stats = await self._get_error_statistics(crawler_id, hours=24)
            
            # Get performance metrics
            performance_metrics = await self._get_performance_metrics(crawler_id)
            
            return {
                "crawler_id": crawler_id,
                "platform_type": crawler.platform_type,
                "status": crawler.status,
                "capabilities": crawler.capabilities,
                "created_at": crawler.created_at.isoformat(),
                "updated_at": crawler.updated_at.isoformat(),
                "session_statistics": session_stats,
                "error_statistics": error_stats,
                "performance_metrics": performance_metrics,
                "configuration": crawler.configuration
            }
            
        except Exception as e:
            raise DatabaseError(f"Failed to get crawler status: {str(e)}")
    
    async def update_crawler_status(
        self,
        crawler_id: str,
        new_status: CrawlerStatus,
        status_message: Optional[str] = None
    ) -> bool:
        """
        Update crawler operational status.
        
        Args:
            crawler_id: Crawler identifier
            new_status: New status to set
            status_message: Optional status message
            
        Returns:
            True if update successful
        """
        try:
            crawler = await self.db_session.query(PlatformCrawler).filter(
                PlatformCrawler.crawler_id == crawler_id
            ).first()
            
            if not crawler:
                raise DatabaseError(f"Crawler {crawler_id} not found")
            
            crawler.status = new_status.value
            crawler.updated_at = datetime.utcnow()
            
            if status_message:
                crawler.status_message = status_message
            
            await self.db_session.commit()
            return True
            
        except Exception as e:
            await self.db_session.rollback()
            raise DatabaseError(f"Failed to update crawler status: {str(e)}")
    
    async def _validate_platform_config(
        self,
        platform_type: PlatformType,
        config: Dict[str, Any]
    ) -> bool:
        """Validate platform-specific configuration."""
        required_fields = {
            PlatformType.YOUTUBE: ["api_key", "rate_limit"],
            PlatformType.TIKTOK: ["auth_token", "rate_limit"],
            PlatformType.INSTAGRAM: ["access_token", "rate_limit"],
            PlatformType.TWITTER: ["bearer_token", "rate_limit"],
            PlatformType.SPOTIFY: ["client_id", "client_secret", "rate_limit"]
        }
        
        platform_required = required_fields.get(platform_type, [])
        
        for field in platform_required:
            if field not in config:
                raise CrawlerConfigurationError(
                    f"Missing required field '{field}' for {platform_type.value}"
                )
        
        return True
    
    async def _initialize_platform_settings(
        self,
        crawler_id: str,
        platform_type: PlatformType,
        config: Dict[str, Any]
    ) -> None:
        """Initialize platform-specific settings and defaults."""
        # Store platform configuration in cache
        self.platform_configs[crawler_id] = {
            "platform": platform_type.value,
            "config": config,
            "initialized_at": datetime.utcnow().isoformat()
        }
    
    async def _get_recent_sessions(self, crawler_id: str, hours: int = 24) -> List[Dict]:
        """Get recent crawling sessions for a crawler."""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        sessions = await self.db_session.query(CrawlerSession).filter(
            and_(
                CrawlerSession.crawler_id == crawler_id,
                CrawlerSession.created_at >= cutoff_time
            )
        ).all()
        
        return [
            {
                "session_id": session.session_id,
                "status": session.status,
                "items_processed": session.items_processed,
                "duration_seconds": session.duration_seconds,
                "created_at": session.created_at.isoformat()
            }
            for session in sessions
        ]
    
    async def _calculate_session_statistics(self, sessions: List[Dict]) -> Dict[str, Any]:
        """Calculate statistics from recent sessions."""
        if not sessions:
            return {
                "total_sessions": 0,
                "successful_sessions": 0,
                "failed_sessions": 0,
                "average_duration": 0,
                "total_items_processed": 0,
                "success_rate": 0.0
            }
        
        successful = len([s for s in sessions if s["status"] == "completed"])
        failed = len([s for s in sessions if s["status"] == "failed"])
        total_duration = sum(s["duration_seconds"] for s in sessions if s["duration_seconds"])
        total_items = sum(s["items_processed"] for s in sessions if s["items_processed"])
        
        return {
            "total_sessions": len(sessions),
            "successful_sessions": successful,
            "failed_sessions": failed,
            "average_duration": total_duration / len(sessions) if sessions else 0,
            "total_items_processed": total_items,
            "success_rate": (successful / len(sessions)) * 100 if sessions else 0.0
        }
    
    async def _get_error_statistics(self, crawler_id: str, hours: int = 24) -> Dict[str, Any]:
        """Get error statistics for a crawler."""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        errors = await self.db_session.query(CrawlerError).filter(
            and_(
                CrawlerError.crawler_id == crawler_id,
                CrawlerError.created_at >= cutoff_time
            )
        ).all()
        
        error_types = {}
        for error in errors:
            error_type = error.error_type
            if error_type not in error_types:
                error_types[error_type] = 0
            error_types[error_type] += 1
        
        return {
            "total_errors": len(errors),
            "error_types": error_types,
            "error_rate": len(errors) / max(hours, 1)  # Errors per hour
        }
    
    async def _get_performance_metrics(self, crawler_id: str) -> Dict[str, Any]:
        """Get performance metrics for a crawler."""
        # This would integrate with monitoring systems
        return {
            "average_response_time": 1.2,  # seconds
            "throughput_per_minute": 45,   # items processed
            "memory_usage": 128,           # MB
            "cpu_usage_percent": 15.5,
            "last_health_check": datetime.utcnow().isoformat()
        }
    
    def _load_platform_configurations(self) -> None:
        """Load default platform configurations."""
        self.platform_configs = {
            "default_youtube": {
                "max_concurrent_requests": 5,
                "retry_attempts": 3,
                "timeout_seconds": 30
            },
            "default_tiktok": {
                "max_concurrent_requests": 3,
                "retry_attempts": 5,
                "timeout_seconds": 45
            },
            "default_instagram": {
                "max_concurrent_requests": 2,
                "retry_attempts": 3,
                "timeout_seconds": 60
            }
        }
