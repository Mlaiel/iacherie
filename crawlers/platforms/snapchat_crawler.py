"""Snapchat Platform Crawler - Ultra-Advanced Implementation
Ephemeral Content Monitoring System

This module provides comprehensive crawling capabilities for Snapchat platform,
focusing on Stories, Discover content, and ephemeral media monitoring.

PROPRIETARY SOFTWARE - CONFIDENTIAL AND PROTECTED
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
Created by: Fahed Mlaiel <mlaiel@live.de>

WARNING: This code is the exclusive property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution is strictly prohibited.
Violators will be prosecuted to the full extent of the law.
"""import asyncio
import aiohttp
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set, Tuple, AsyncGenerator
from dataclasses import dataclass
from enum import Enum
import hashlib
import base64
from urllib.parse import urljoin, urlparse
from pydantic import BaseModel, Field, validator
from difflib import SequenceMatcher

from ..base import BaseCrawler
from ...utils.rate_limiter import RateLimiter
from ...utils.cache import CacheManager
from ...utils.encryption import ContentEncryption
from ...utils.fingerprinting import ContentFingerprinter

logger = logging.getLogger(__name__)


class SnapchatContentType(str, Enum):
    """Snapchat content types"""    STORY = "story"
    DISCOVER = "discover"
    SPOTLIGHT = "spotlight"
    SNAP_MAP = "snap_map"
    LENS = "lens"
    FILTER = "filter"
    BITMOJI = "bitmoji"


class SnapchatMediaType(str, Enum):
    """Snapchat media types"""    PHOTO = "photo"
    VIDEO = "video"
    GIF = "gif"
    STICKER = "sticker"
    LENS_VIDEO = "lens_video"


class SnapchatVisibility(str, Enum):
    """Snapchat content visibility"""    PUBLIC = "public"
    FRIENDS = "friends"
    CUSTOM = "custom"
    PRIVATE = "private"


class SnapchatStoryType(str, Enum):
    """Snapchat story types"""    USER_STORY = "user_story"
    OUR_STORY = "our_story"
    LIVE_STORY = "live_story"
    BRAND_STORY = "brand_story"


class SnapchatMedia(BaseModel):
    """Snapchat media data model"""    media_id: str
    media_type: SnapchatMediaType
    url: str
    thumbnail_url: Optional[str] = None
    duration: Optional[int] = None  # for videos
    width: Optional[int] = None
    height: Optional[int] = None
    file_size: Optional[int] = None
    created_at: datetime
    expires_at: datetime
    is_expired: bool = False
    has_audio: bool = False
    lens_id: Optional[str] = None
    filter_id: Optional[str] = None
    stickers: List[Dict[str, Any]] = Field(default_factory=list)
    text_overlays: List[Dict[str, Any]] = Field(default_factory=list)
    drawing_overlays: List[Dict[str, Any]] = Field(default_factory=list)


class SnapchatUser(BaseModel):
    """Snapchat user data model"""    user_id: str
    username: str
    display_name: str
    bitmoji_avatar: Optional[str] = None
    score: Optional[int] = None
    is_verified: bool = False
    is_premium: bool = False
    story_count: int = 0
    friends_count: Optional[int] = None
    created_at: datetime
    last_seen: Optional[datetime] = None
    location: Optional[Dict[str, Any]] = None
    snap_map_visible: bool = False
    ghost_mode: bool = True
    profile_visibility: SnapchatVisibility = SnapchatVisibility.FRIENDS
    bio: Optional[str] = None
    website: Optional[str] = None


class SnapchatStory(BaseModel):
    """Snapchat story data model"""    story_id: str
    user: SnapchatUser
    story_type: SnapchatStoryType
    title: Optional[str] = None
    media: List[SnapchatMedia] = Field(default_factory=list)
    created_at: datetime
    expires_at: datetime
    view_count: int = 0
    is_expired: bool = False
    visibility: SnapchatVisibility
    location: Optional[Dict[str, Any]] = None
    tags: List[str] = Field(default_factory=list)
    mentions: List[str] = Field(default_factory=list)
    contributors: List[SnapchatUser] = Field(default_factory=list)
    can_reply: bool = True
    can_share: bool = False
    similarity_score: Optional[float] = None
    protection_status: str = "unprotected"


class SnapchatDiscover(BaseModel):
    """Snapchat Discover content data model"""    discover_id: str
    publisher: str
    publisher_logo: Optional[str] = None
    title: str
    subtitle: Optional[str] = None
    description: Optional[str] = None
    media: SnapchatMedia
    created_at: datetime
    category: str
    tags: List[str] = Field(default_factory=list)
    view_count: int = 0
    share_count: int = 0
    is_sponsored: bool = False
    url: Optional[str] = None
    article_url: Optional[str] = None
    duration_seconds: Optional[int] = None


class SnapchatSpotlight(BaseModel):
    """Snapchat Spotlight content data model"""    spotlight_id: str
    creator: SnapchatUser
    media: SnapchatMedia
    caption: Optional[str] = None
    sound_id: Optional[str] = None
    sound_title: Optional[str] = None
    view_count: int = 0
    like_count: int = 0
    share_count: int = 0
    comment_count: int = 0
    created_at: datetime
    hashtags: List[str] = Field(default_factory=list)
    effects_used: List[str] = Field(default_factory=list)
    is_trending: bool = False
    trend_score: Optional[float] = None


class SnapchatLens(BaseModel):
    """Snapchat lens data model"""    lens_id: str
    name: str
    creator: str
    description: Optional[str] = None
    icon_url: Optional[str] = None
    preview_video_url: Optional[str] = None
    created_at: datetime
    category: str
    tags: List[str] = Field(default_factory=list)
    usage_count: int = 0
    is_trending: bool = False
    is_official: bool = False
    unlock_type: str = "scan"  # scan, snapcode, search
    snapcode_url: Optional[str] = None


class SnapchatSearchResults(BaseModel):
    """Snapchat search results data model"""    query: str
    total_results: int
    users: List[SnapchatUser] = Field(default_factory=list)
    stories: List[SnapchatStory] = Field(default_factory=list)
    discover_content: List[SnapchatDiscover] = Field(default_factory=list)
    spotlight_content: List[SnapchatSpotlight] = Field(default_factory=list)
    lenses: List[SnapchatLens] = Field(default_factory=list)
    search_type: str
    filters_applied: Dict[str, Any]
    search_timestamp: datetime
    has_more: bool = False
    next_cursor: Optional[str] = None


class SnapchatAnalytics(BaseModel):
    """Snapchat analytics data model"""    user_id: str
    analysis_period: Tuple[datetime, datetime]
    total_stories_posted: int
    total_story_views: int
    average_views_per_story: float
    total_spotlight_posts: int
    total_spotlight_views: int
    spotlight_engagement_rate: float
    lens_usage_count: int
    popular_lenses_used: List[str]
    story_completion_rate: float
    peak_activity_hours: List[int]
    audience_demographics: Dict[str, Any]
    content_type_distribution: Dict[str, int]
    location_insights: Dict[str, Any]
    ephemeral_content_ratio: float
    similarity_violations: int
    protection_violations: int


class SnapchatCrawler(BaseCrawler):
    """    Ultra-Advanced Snapchat Platform Crawler
    
    Provides comprehensive crawling and monitoring capabilities for Snapchat platform,
    specializing in ephemeral content, Stories, and Discover content monitoring.
    """    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        
        self.base_url = "https://snapchat.com"
        self.api_base = "https://web.snapchat.com/web"
        
        # Authentication
        self.session_token: Optional[str] = None
        self.user_agent: str = config.get('user_agent', 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15')
        self.user_id: Optional[str] = None
        
        # Rate limiting - Snapchat has strict limits
        self.rate_limiter = RateLimiter(
            requests_per_minute=20,
            requests_per_hour=300,
            burst_limit=5
        )
        
        # Cache management with short TTL for ephemeral content
        self.cache_manager = CacheManager(
            cache_ttl=60,  # 1 minute for ephemeral content
            max_cache_size=500
        )
        
        # Content protection
        self.content_encryption = ContentEncryption()
        self.content_fingerprinter = ContentFingerprinter()
        
        # Monitoring configuration
        self.monitored_users: Set[str] = set()
        self.protected_content: Set[str] = set()
        self.similarity_threshold = config.get('similarity_threshold', 0.88)
        
        # Snapchat-specific settings
        self.track_ephemeral_content = config.get('track_ephemeral_content', True)
        self.monitor_discover = config.get('monitor_discover', True)
        self.track_spotlight = config.get('track_spotlight', True)
        self.monitor_lenses = config.get('monitor_lenses', False)
        self.preserve_expired_content = config.get('preserve_expired_content', True)
        
        logger.info("Snapchat crawler initialized with ultra-advanced ephemeral content monitoring")

    async def authenticate(self, session_token: str, user_id: str = None) -> bool:
        """        Authenticate with Snapchat platform
        
        Args:
            session_token: Session authentication token
            user_id: User ID
            
        Returns:
            bool: Authentication success status
        """        try:
            self.session_token = session_token
            self.user_id = user_id
            
            self.session.headers.update({
                'Authorization': f'Bearer {session_token}',
                'User-Agent': self.user_agent,
                'Accept': 'application/json',
                'X-Snapchat-Client-Auth-Token': session_token
            })
            
            # Verify authentication with user info
            async with self.session.get(f"{self.api_base}/user/me") as response:
                if response.status == 200:
                    user_data = await response.json()
                    self.user_id = user_data.get('id', '')
                    logger.info("Snapchat authentication successful")
                    return True
                else:
                    logger.error(f"Authentication verification failed: {response.status}")
                    return False
                    
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            return False

    async def search_content(
        self,
        query: str = "",
        content_type: Optional[SnapchatContentType] = None,
        media_type: Optional[SnapchatMediaType] = None,
        limit: int = 50
    ) -> SnapchatSearchResults:
        """        Search Snapchat content with advanced filtering
        
        Args:
            query: Search query
            content_type: Type of content to search
            media_type: Type of media to search
            limit: Maximum results
            
        Returns:
            SnapchatSearchResults: Comprehensive search results
        """        await self.rate_limiter.acquire()
        
        try:
            results = SnapchatSearchResults(
                query=query,
                total_results=0,
                search_type="comprehensive",
                filters_applied={
                    "content_type": content_type.value if content_type else None,
                    "media_type": media_type.value if media_type else None
                },
                search_timestamp=datetime.utcnow()
            )
            
            # Search users
            if not content_type or content_type == SnapchatContentType.STORY:
                users = await self._search_users(query, limit // 4)
                results.users = users
                results.total_results += len(users)
            
            # Search stories
            if not content_type or content_type == SnapchatContentType.STORY:
                stories = await self._search_stories(query, media_type, limit // 4)
                results.stories = stories
                results.total_results += len(stories)
            
            # Search Discover content
            if self.monitor_discover and (not content_type or content_type == SnapchatContentType.DISCOVER):
                discover_content = await self._search_discover(query, limit // 4)
                results.discover_content = discover_content
                results.total_results += len(discover_content)
            
            # Search Spotlight content
            if self.track_spotlight and (not content_type or content_type == SnapchatContentType.SPOTLIGHT):
                spotlight_content = await self._search_spotlight(query, limit // 4)
                results.spotlight_content = spotlight_content
                results.total_results += len(spotlight_content)
            
            # Search lenses
            if self.monitor_lenses and (not content_type or content_type == SnapchatContentType.LENS):
                lenses = await self._search_lenses(query, limit // 4)
                results.lenses = lenses
                results.total_results += len(lenses)
            
            # Process content for protection
            for story in results.stories:
                story.similarity_score = await self._calculate_similarity(story)
                story.protection_status = await self._check_protection_status(story)
            
            logger.info(f"Snapchat search completed: {results.total_results} total results")
            return results
            
        except Exception as e:
            logger.error(f"Search error: {str(e)}")
            return SnapchatSearchResults(
                query=query,
                total_results=0,
                search_type="error",
                filters_applied={},
                search_timestamp=datetime.utcnow()
            )

    async def monitor_content(
        self,
        usernames: List[str] = None,
        keywords: List[str] = None,
        check_interval: int = 180  # 3 minutes for ephemeral content
    ) -> AsyncGenerator[SnapchatStory, None]:
        """        Real-time content monitoring for Snapchat
        
        Args:
            usernames: Users to monitor
            keywords: Keywords to monitor
            check_interval: Check interval in seconds
            
        Yields:
            SnapchatStory: New stories detected
        """        usernames = usernames or []
        keywords = keywords or []
        
        self.monitored_users.update(usernames)
        
        logger.info(f"Starting Snapchat monitoring for {len(usernames)} users")
        
        seen_stories = set()
        
        while True:
            try:
                await asyncio.sleep(check_interval)
                
                for username in usernames:
                    try:
                        user_stories = await self._get_user_recent_stories(username)
                        
                        for story in user_stories:
                            if story.story_id not in seen_stories and not story.is_expired:
                                # Enhanced monitoring analysis
                                story.similarity_score = await self._calculate_similarity(story)
                                story.protection_status = await self._check_protection_status(story)
                                
                                seen_stories.add(story.story_id)
                                
                                # Preserve content if enabled
                                if self.preserve_expired_content:
                                    await self._preserve_ephemeral_content(story)
                                
                                logger.info(f"New story from {username}: {story.story_id}")
                                yield story
                    
                    except Exception as e:
                        logger.error(f"Error monitoring user {username}: {str(e)}")
                        continue
                
                # Clean up expired content
                await self._cleanup_expired_content()
                
            except Exception as e:
                logger.error(f"Monitoring error: {str(e)}")
                await asyncio.sleep(60)

    async def detect_similarity(
        self,
        target_story: SnapchatStory,
        comparison_set: List[SnapchatStory],
        threshold: float = None
    ) -> List[Tuple[SnapchatStory, float]]:
        """        Detect story similarity for ephemeral content protection
        
        Args:
            target_story: Story to compare
            comparison_set: Stories to compare against
            threshold: Similarity threshold
            
        Returns:
            List[Tuple[SnapchatStory, float]]: Similar stories with scores
        """        threshold = threshold or self.similarity_threshold
        similar_stories = []
        
        try:
            target_features = await self._extract_story_features(target_story)
            
            for story in comparison_set:
                if story.story_id == target_story.story_id or story.is_expired:
                    continue
                
                comp_features = await self._extract_story_features(story)
                similarity_score = await self._calculate_feature_similarity(
                    target_features, comp_features
                )
                
                if similarity_score >= threshold:
                    similar_stories.append((story, similarity_score))
            
            similar_stories.sort(key=lambda x: x[1], reverse=True)
            
            logger.info(f"Similarity detection: {len(similar_stories)} matches found")
            return similar_stories
            
        except Exception as e:
            logger.error(f"Similarity detection error: {str(e)}")
            return []

    async def get_analytics(
        self,
        user_id: str,
        analysis_period: Tuple[datetime, datetime]
    ) -> SnapchatAnalytics:
        """        Generate comprehensive analytics for Snapchat user
        
        Args:
            user_id: User ID to analyze
            analysis_period: Analysis time period
            
        Returns:
            SnapchatAnalytics: Comprehensive analytics data
        """        try:
            start_time, end_time = analysis_period
            
            # Get user's stories in the period
            user_stories = await self._get_user_stories_in_period(user_id, start_time, end_time)
            spotlight_posts = await self._get_user_spotlight_in_period(user_id, start_time, end_time)
            
            if not user_stories and not spotlight_posts:
                return SnapchatAnalytics(
                    user_id=user_id,
                    analysis_period=analysis_period,
                    total_stories_posted=0,
                    total_story_views=0,
                    average_views_per_story=0.0,
                    total_spotlight_posts=0,
                    total_spotlight_views=0,
                    spotlight_engagement_rate=0.0,
                    lens_usage_count=0,
                    popular_lenses_used=[],
                    story_completion_rate=0.0,
                    peak_activity_hours=[],
                    audience_demographics={},
                    content_type_distribution={},
                    location_insights={},
                    ephemeral_content_ratio=1.0,
                    similarity_violations=0,
                    protection_violations=0
                )
            
            # Calculate story analytics
            total_stories_posted = len(user_stories)
            total_story_views = sum(story.view_count for story in user_stories)
            average_views_per_story = total_story_views / total_stories_posted if total_stories_posted > 0 else 0.0
            
            # Calculate Spotlight analytics
            total_spotlight_posts = len(spotlight_posts)
            total_spotlight_views = sum(post.view_count for post in spotlight_posts)
            total_spotlight_likes = sum(post.like_count for post in spotlight_posts)
            spotlight_engagement_rate = (total_spotlight_likes / total_spotlight_views) if total_spotlight_views > 0 else 0.0
            
            # Content type distribution
            content_type_distribution = {}
            for story in user_stories:
                for media in story.media:
                    media_type = media.media_type.value
                    content_type_distribution[media_type] = content_type_distribution.get(media_type, 0) + 1
            
            # Lens usage analysis
            lens_usage_count = 0
            popular_lenses_used = []
            lens_counts = {}
            
            for story in user_stories:
                for media in story.media:
                    if media.lens_id:
                        lens_usage_count += 1
                        lens_counts[media.lens_id] = lens_counts.get(media.lens_id, 0) + 1
            
            popular_lenses_used = sorted(lens_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            popular_lenses_used = [lens[0] for lens in popular_lenses_used]
            
            # Activity patterns
            activity_hours = []
            for story in user_stories:
                activity_hours.append(story.created_at.hour)
            
            hour_counts = {}
            for hour in activity_hours:
                hour_counts[hour] = hour_counts.get(hour, 0) + 1
            peak_activity_hours = sorted(hour_counts.items(), key=lambda x: x[1], reverse=True)[:3]
            peak_activity_hours = [hour[0] for hour in peak_activity_hours]
            
            # Protection metrics
            similarity_violations = sum(1 for story in user_stories if (story.similarity_score or 0) > self.similarity_threshold)
            protection_violations = sum(1 for story in user_stories if story.protection_status == "violation")
            
            analytics = SnapchatAnalytics(
                user_id=user_id,
                analysis_period=analysis_period,
                total_stories_posted=total_stories_posted,
                total_story_views=total_story_views,
                average_views_per_story=average_views_per_story,
                total_spotlight_posts=total_spotlight_posts,
                total_spotlight_views=total_spotlight_views,
                spotlight_engagement_rate=spotlight_engagement_rate,
                lens_usage_count=lens_usage_count,
                popular_lenses_used=popular_lenses_used,
                story_completion_rate=0.8,  # Simplified
                peak_activity_hours=peak_activity_hours,
                audience_demographics={},  # Would need audience API
                content_type_distribution=content_type_distribution,
                location_insights={},  # Would need location data
                ephemeral_content_ratio=1.0,  # All Snapchat content is ephemeral
                similarity_violations=similarity_violations,
                protection_violations=protection_violations
            )
            
            logger.info(f"Analytics generated for user {user_id}: {total_stories_posted} stories, {total_spotlight_posts} spotlight posts")
            return analytics
            
        except Exception as e:
            logger.error(f"Analytics generation error: {str(e)}")
            return SnapchatAnalytics(
                user_id=user_id,
                analysis_period=analysis_period,
                total_stories_posted=0,
                total_story_views=0,
                average_views_per_story=0.0,
                total_spotlight_posts=0,
                total_spotlight_views=0,
                spotlight_engagement_rate=0.0,
                lens_usage_count=0,
                popular_lenses_used=[],
                story_completion_rate=0.0,
                peak_activity_hours=[],
                audience_demographics={},
                content_type_distribution={},
                location_insights={},
                ephemeral_content_ratio=1.0,
                similarity_violations=0,
                protection_violations=0
            )

    # Helper methods
    
    async def _search_users(self, query: str, limit: int) -> List[SnapchatUser]:
        """Search for Snapchat users"""        try:
            params = {
                "query": query,
                "limit": limit
            }
            
            async with self.session.get(f"{self.api_base}/search/users", params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    users = []
                    
                    for user_data in data.get("users", []):
                        user = await self._parse_user_data(user_data)
                        users.append(user)
                    
                    return users
                else:
                    return []
                    
        except Exception as e:
            logger.error(f"User search error: {str(e)}")
            return []

    async def _search_stories(self, query: str, media_type: Optional[SnapchatMediaType], limit: int) -> List[SnapchatStory]:
        """Search for Snapchat stories"""        # Implementation would depend on available search API
        return []

    async def _search_discover(self, query: str, limit: int) -> List[SnapchatDiscover]:
        """Search Discover content"""        try:
            params = {
                "query": query,
                "limit": limit
            }
            
            async with self.session.get(f"{self.api_base}/discover/search", params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    discover_content = []
                    
                    for content_data in data.get("content", []):
                        content = await self._parse_discover_data(content_data)
                        discover_content.append(content)
                    
                    return discover_content
                else:
                    return []
                    
        except Exception as e:
            logger.error(f"Discover search error: {str(e)}")
            return []

    async def _search_spotlight(self, query: str, limit: int) -> List[SnapchatSpotlight]:
        """Search Spotlight content"""        # Implementation would depend on available search API
        return []

    async def _search_lenses(self, query: str, limit: int) -> List[SnapchatLens]:
        """Search for lenses"""        try:
            params = {
                "query": query,
                "limit": limit
            }
            
            async with self.session.get(f"{self.api_base}/lenses/search", params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    lenses = []
                    
                    for lens_data in data.get("lenses", []):
                        lens = await self._parse_lens_data(lens_data)
                        lenses.append(lens)
                    
                    return lenses
                else:
                    return []
                    
        except Exception as e:
            logger.error(f"Lens search error: {str(e)}")
            return []

    async def _get_user_recent_stories(self, username: str) -> List[SnapchatStory]:
        """Get recent stories from user"""        try:
            async with self.session.get(f"{self.api_base}/users/{username}/stories") as response:
                if response.status == 200:
                    data = await response.json()
                    stories = []
                    
                    for story_data in data.get("stories", []):
                        story = await self._parse_story_data(story_data)
                        if not story.is_expired:
                            stories.append(story)
                    
                    return stories
                else:
                    return []
                    
        except Exception as e:
            logger.error(f"Error getting user stories: {str(e)}")
            return []

    async def _parse_user_data(self, data: Dict[str, Any]) -> SnapchatUser:
        """Parse user data from API response"""        return SnapchatUser(
            user_id=str(data.get("id", "")),
            username=data.get("username", ""),
            display_name=data.get("display_name", ""),
            bitmoji_avatar=data.get("bitmoji_avatar"),
            score=data.get("score"),
            is_verified=data.get("is_verified", False),
            story_count=data.get("story_count", 0),
            created_at=datetime.utcnow(),
            snap_map_visible=data.get("snap_map_visible", False),
            ghost_mode=data.get("ghost_mode", True)
        )

    async def _parse_story_data(self, data: Dict[str, Any]) -> SnapchatStory:
        """Parse story data from API response"""        # Parse media
        media = []
        for media_data in data.get("media", []):
            media_item = SnapchatMedia(
                media_id=str(media_data.get("id", "")),
                media_type=SnapchatMediaType(media_data.get("type", "photo")),
                url=media_data.get("url", ""),
                thumbnail_url=media_data.get("thumbnail_url"),
                duration=media_data.get("duration"),
                width=media_data.get("width"),
                height=media_data.get("height"),
                created_at=datetime.fromisoformat(media_data.get("created_at", datetime.utcnow().isoformat())),
                expires_at=datetime.fromisoformat(media_data.get("expires_at", (datetime.utcnow() + timedelta(hours=24)).isoformat())),
                lens_id=media_data.get("lens_id"),
                filter_id=media_data.get("filter_id"),
                stickers=media_data.get("stickers", []),
                text_overlays=media_data.get("text_overlays", [])
            )
            media.append(media_item)
        
        # Parse user
        user_data = data.get("user", {})
        user = SnapchatUser(
            user_id=str(user_data.get("id", "")),
            username=user_data.get("username", ""),
            display_name=user_data.get("display_name", ""),
            bitmoji_avatar=user_data.get("bitmoji_avatar"),
            is_verified=user_data.get("is_verified", False),
            created_at=datetime.utcnow()
        )
        
        created_at = datetime.fromisoformat(data.get("created_at", datetime.utcnow().isoformat()))
        expires_at = datetime.fromisoformat(data.get("expires_at", (datetime.utcnow() + timedelta(hours=24)).isoformat()))
        
        return SnapchatStory(
            story_id=str(data.get("id", "")),
            user=user,
            story_type=SnapchatStoryType(data.get("story_type", "user_story")),
            title=data.get("title"),
            media=media,
            created_at=created_at,
            expires_at=expires_at,
            view_count=data.get("view_count", 0),
            is_expired=datetime.utcnow() > expires_at,
            visibility=SnapchatVisibility(data.get("visibility", "friends")),
            tags=data.get("tags", []),
            mentions=data.get("mentions", [])
        )

    async def _parse_discover_data(self, data: Dict[str, Any]) -> SnapchatDiscover:
        """Parse Discover content data"""        media_data = data.get("media", {})
        media = SnapchatMedia(
            media_id=str(media_data.get("id", "")),
            media_type=SnapchatMediaType(media_data.get("type", "video")),
            url=media_data.get("url", ""),
            thumbnail_url=media_data.get("thumbnail_url"),
            duration=media_data.get("duration"),
            created_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(hours=24)
        )
        
        return SnapchatDiscover(
            discover_id=str(data.get("id", "")),
            publisher=data.get("publisher", ""),
            publisher_logo=data.get("publisher_logo"),
            title=data.get("title", ""),
            subtitle=data.get("subtitle"),
            description=data.get("description"),
            media=media,
            created_at=datetime.fromisoformat(data.get("created_at", datetime.utcnow().isoformat())),
            category=data.get("category", ""),
            tags=data.get("tags", []),
            view_count=data.get("view_count", 0),
            is_sponsored=data.get("is_sponsored", False)
        )

    async def _parse_lens_data(self, data: Dict[str, Any]) -> SnapchatLens:
        """Parse lens data"""        return SnapchatLens(
            lens_id=str(data.get("id", "")),
            name=data.get("name", ""),
            creator=data.get("creator", ""),
            description=data.get("description"),
            icon_url=data.get("icon_url"),
            preview_video_url=data.get("preview_video_url"),
            created_at=datetime.fromisoformat(data.get("created_at", datetime.utcnow().isoformat())),
            category=data.get("category", ""),
            tags=data.get("tags", []),
            usage_count=data.get("usage_count", 0),
            is_trending=data.get("is_trending", False),
            is_official=data.get("is_official", False),
            snapcode_url=data.get("snapcode_url")
        )

    async def _extract_story_features(self, story: SnapchatStory) -> Dict[str, Any]:
        """Extract features for similarity comparison"""        features = {
            "title": (story.title or "").lower(),
            "user_id": story.user.user_id,
            "media_count": len(story.media),
            "media_types": set(media.media_type.value for media in story.media),
            "story_type": story.story_type.value,
            "has_text_overlay": any(media.text_overlays for media in story.media),
            "has_stickers": any(media.stickers for media in story.media),
            "has_filter": any(media.filter_id for media in story.media),
            "has_lens": any(media.lens_id for media in story.media),
            "tags": set(tag.lower() for tag in story.tags),
            "mentions": set(mention.lower() for mention in story.mentions),
            "visibility": story.visibility.value,
            "location": story.location is not None
        }
        return features

    async def _calculate_feature_similarity(
        self,
        features1: Dict[str, Any],
        features2: Dict[str, Any]
    ) -> float:
        """Calculate similarity between story features"""        try:
            scores = []
            
            # Title similarity
            title_sim = SequenceMatcher(
                None, features1.get("title", ""), features2.get("title", "")
            ).ratio()
            scores.append(title_sim * 0.2)  # 20% weight
            
            # Media type similarity
            media_types1 = features1.get("media_types", set())
            media_types2 = features2.get("media_types", set())
            if media_types1 and media_types2:
                media_sim = len(media_types1.intersection(media_types2)) / len(media_types1.union(media_types2))
                scores.append(media_sim * 0.3)  # 30% weight
            
            # Story type similarity
            type_sim = 1.0 if features1.get("story_type") == features2.get("story_type") else 0.0
            scores.append(type_sim * 0.2)  # 20% weight
            
            # Feature similarity (overlays, stickers, etc.)
            feature_sim = 0.0
            if features1.get("has_text_overlay") == features2.get("has_text_overlay"):
                feature_sim += 0.25
            if features1.get("has_stickers") == features2.get("has_stickers"):
                feature_sim += 0.25
            if features1.get("has_filter") == features2.get("has_filter"):
                feature_sim += 0.25
            if features1.get("has_lens") == features2.get("has_lens"):
                feature_sim += 0.25
            scores.append(feature_sim * 0.2)  # 20% weight
            
            # Tag similarity
            tags1 = features1.get("tags", set())
            tags2 = features2.get("tags", set())
            if tags1 and tags2:
                tag_sim = len(tags1.intersection(tags2)) / len(tags1.union(tags2))
                scores.append(tag_sim * 0.1)  # 10% weight
            
            return sum(scores) / len(scores) if scores else 0.0
            
        except Exception as e:
            logger.error(f"Feature similarity calculation error: {str(e)}")
            return 0.0

    async def _preserve_ephemeral_content(self, story: SnapchatStory):
        """Preserve ephemeral content before it expires"""        if self.preserve_expired_content:
            try:
                # Encrypt and store story data
                story_data = story.dict()
                encrypted_data = await self.content_encryption.encrypt(json.dumps(story_data))
                
                # Store in cache with extended TTL
                await self.cache_manager.set(
                    f"preserved_story_{story.story_id}",
                    encrypted_data,
                    ttl=86400  # 24 hours
                )
                
                logger.info(f"Preserved ephemeral story: {story.story_id}")
                
            except Exception as e:
                logger.error(f"Error preserving content: {str(e)}")

    async def _cleanup_expired_content(self):
        """Clean up expired content from cache"""        try:
            # Implementation would clean up expired stories
            current_time = datetime.utcnow()
            # Clean up logic here
            pass
            
        except Exception as e:
            logger.error(f"Error cleaning up expired content: {str(e)}")

    async def _get_user_stories_in_period(
        self,
        user_id: str,
        start_time: datetime,
        end_time: datetime
    ) -> List[SnapchatStory]:
        """Get user's stories in specific time period"""        # Implementation would require accessing stored story data
        return []

    async def _get_user_spotlight_in_period(
        self,
        user_id: str,
        start_time: datetime,
        end_time: datetime
    ) -> List[SnapchatSpotlight]:
        """Get user's Spotlight posts in specific time period"""        # Implementation would require accessing Spotlight data
        return []

    async def _calculate_similarity(self, story: SnapchatStory) -> float:
        """Calculate similarity score against protected content"""        # Simplified similarity calculation
        return 0.0

    async def _check_protection_status(self, story: SnapchatStory) -> str:
        """Check protection status of story"""        if story.story_id in self.protected_content:
            return "protected"
        return "unprotected"

    async def close(self):
        """Close crawler and cleanup resources"""        try:
            await self.cache_manager.close()
            await super().close()
            logger.info("Snapchat crawler closed successfully")
        except Exception as e:
            logger.error(f"Error closing crawler: {str(e)}")
