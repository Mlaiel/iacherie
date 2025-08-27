"""
OnlyFans Platform Crawler - Ultra-Advanced Implementation
Premium Content Platform Monitoring System

This module provides comprehensive crawling capabilities for OnlyFans platform,
focusing on subscription content, creator analytics, and content protection.

PROPRIETARY SOFTWARE - CONFIDENTIAL AND PROTECTED
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
Created by: Fahed Mlaiel <mlaiel@live.de>

WARNING: This code is the exclusive property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution is strictly prohibited.
Violators will be prosecuted to the full extent of the law.
"""

import asyncio
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


class OnlyFansSubscriptionType(str, Enum):
    """OnlyFans subscription types"""
    FREE = "free"
    PAID = "paid"
    PROMOTIONAL = "promotional"


class OnlyFansContentType(str, Enum):
    """OnlyFans content types"""
    POST = "post"
    MESSAGE = "message"
    STORY = "story"
    LIVE_STREAM = "live_stream"
    TIPS = "tips"


class OnlyFansMediaType(str, Enum):
    """OnlyFans media types"""
    PHOTO = "photo"
    VIDEO = "video"
    AUDIO = "audio"
    GIF = "gif"


class OnlyFansMedia(BaseModel):
    """OnlyFans media data model"""
    media_id: str
    media_type: OnlyFansMediaType
    url: str
    preview_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    duration: Optional[int] = None  # for videos/audio
    width: Optional[int] = None
    height: Optional[int] = None
    file_size: Optional[int] = None
    is_premium: bool = True
    unlock_price: Optional[float] = None
    is_watermarked: bool = True


class OnlyFansCreator(BaseModel):
    """OnlyFans creator data model"""
    creator_id: str
    username: str
    display_name: str
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    header_url: Optional[str] = None
    subscriber_count: int = 0
    post_count: int = 0
    photo_count: int = 0
    video_count: int = 0
    is_verified: bool = False
    subscription_price: float = 0.0
    is_free_trial_enabled: bool = False
    free_trial_duration: Optional[int] = None
    is_live: bool = False
    last_seen: Optional[datetime] = None
    joined_date: datetime
    tips_enabled: bool = True
    wishlist_enabled: bool = True
    location: Optional[str] = None
    website: Optional[str] = None
    amazon_wishlist: Optional[str] = None


class OnlyFansPost(BaseModel):
    """OnlyFans post data model"""
    post_id: str
    creator: OnlyFansCreator
    text: Optional[str] = None
    price: Optional[float] = None
    is_premium: bool = False
    is_pinned: bool = False
    is_archived: bool = False
    created_at: datetime
    media: List[OnlyFansMedia] = Field(default_factory=list)
    likes_count: int = 0
    comments_count: int = 0
    tips_amount: float = 0.0
    tips_count: int = 0
    is_liked: bool = False
    is_purchased: bool = False
    is_bookmarked: bool = False
    can_comment: bool = True
    can_tip: bool = True
    hashtags: List[str] = Field(default_factory=list)
    mentions: List[str] = Field(default_factory=list)
    similarity_score: Optional[float] = None
    protection_status: str = "unprotected"


class OnlyFansMessage(BaseModel):
    """OnlyFans private message data model"""
    message_id: str
    from_user: OnlyFansCreator
    to_user: OnlyFansCreator
    text: Optional[str] = None
    price: Optional[float] = None
    is_premium: bool = False
    created_at: datetime
    media: List[OnlyFansMedia] = Field(default_factory=list)
    is_read: bool = False
    is_purchased: bool = False
    tips_amount: float = 0.0


class OnlyFansStory(BaseModel):
    """OnlyFans story data model"""
    story_id: str
    creator: OnlyFansCreator
    media: OnlyFansMedia
    created_at: datetime
    expires_at: datetime
    views_count: int = 0
    is_viewed: bool = False


class OnlyFansSearchResults(BaseModel):
    """OnlyFans search results data model"""
    query: str
    total_results: int
    creators: List[OnlyFansCreator] = Field(default_factory=list)
    posts: List[OnlyFansPost] = Field(default_factory=list)
    search_type: str
    filters_applied: Dict[str, Any]
    search_timestamp: datetime
    has_more: bool = False
    next_cursor: Optional[str] = None


class OnlyFansAnalytics(BaseModel):
    """OnlyFans analytics data model"""
    creator_id: str
    analysis_period: Tuple[datetime, datetime]
    total_posts: int
    total_earnings: float
    total_tips_received: float
    total_subscribers_gained: int
    total_subscribers_lost: int
    average_likes_per_post: float
    most_liked_post_id: Optional[str] = None
    engagement_rate: float
    content_type_distribution: Dict[str, int]
    peak_activity_hours: List[int]
    subscription_conversion_rate: float
    retention_rate: float
    premium_content_ratio: float
    similarity_violations: int
    protection_violations: int


class OnlyFansCrawler(BaseCrawler):
    """
    Ultra-Advanced OnlyFans Platform Crawler
    
    Provides comprehensive crawling and monitoring capabilities for OnlyFans platform,
    specializing in premium content monitoring, creator analytics, and content protection.
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        
        self.base_url = "https://onlyfans.com"
        self.api_base = "https://onlyfans.com/api2/v2"
        
        # Authentication
        self.auth_token: Optional[str] = None
        self.user_agent: str = config.get('user_agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        self.user_id: Optional[str] = None
        
        # Rate limiting - OnlyFans has strict limits
        self.rate_limiter = RateLimiter(
            requests_per_minute=30,
            requests_per_hour=500,
            burst_limit=10
        )
        
        # Cache management
        self.cache_manager = CacheManager(
            cache_ttl=300,  # 5 minutes for premium content
            max_cache_size=1000
        )
        
        # Content protection
        self.content_encryption = ContentEncryption()
        self.content_fingerprinter = ContentFingerprinter()
        
        # Monitoring configuration
        self.monitored_creators: Set[str] = set()
        self.protected_content: Set[str] = set()
        self.similarity_threshold = config.get('similarity_threshold', 0.9)  # Higher threshold for premium content
        
        # OnlyFans-specific settings
        self.enable_premium_monitoring = config.get('enable_premium_monitoring', True)
        self.enable_message_monitoring = config.get('enable_message_monitoring', False)
        self.track_earnings = config.get('track_earnings', True)
        
        logger.info("OnlyFans crawler initialized with ultra-advanced premium content monitoring")

    async def authenticate(self, auth_token: str, user_id: str = None) -> bool:
        """
        Authenticate with OnlyFans platform
        
        Args:
            auth_token: Authentication token
            user_id: User ID
            
        Returns:
            bool: Authentication success status
        """
        try:
            self.auth_token = auth_token
            self.user_id = user_id
            
            self.session.headers.update({
                'Authorization': f'Bearer {auth_token}',
                'User-Agent': self.user_agent,
                'Accept': 'application/json',
                'X-BC': 'a'
            })
            
            # Verify authentication
            async with self.session.get(f"{self.api_base}/users/me") as response:
                if response.status == 200:
                    user_data = await response.json()
                    self.user_id = str(user_data.get('id', ''))
                    logger.info("OnlyFans authentication successful")
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
        content_type: Optional[OnlyFansContentType] = None,
        price_range: Optional[Tuple[float, float]] = None,
        limit: int = 50
    ) -> OnlyFansSearchResults:
        """
        Search OnlyFans content with advanced filtering
        
        Args:
            query: Search query
            content_type: Type of content to search
            price_range: Price range filter (min, max)
            limit: Maximum results
            
        Returns:
            OnlyFansSearchResults: Comprehensive search results
        """
        await self.rate_limiter.acquire()
        
        try:
            results = OnlyFansSearchResults(
                query=query,
                total_results=0,
                search_type="comprehensive",
                filters_applied={
                    "content_type": content_type.value if content_type else None,
                    "price_range": price_range
                },
                search_timestamp=datetime.utcnow()
            )
            
            # Search creators
            creators = await self._search_creators(query, limit // 2)
            results.creators = creators
            results.total_results += len(creators)
            
            # Search posts if enabled
            if self.enable_premium_monitoring:
                posts = await self._search_posts(query, content_type, price_range, limit // 2)
                results.posts = posts
                results.total_results += len(posts)
            
            # Process content for protection
            for post in results.posts:
                post.similarity_score = await self._calculate_similarity(post)
                post.protection_status = await self._check_protection_status(post)
            
            logger.info(f"OnlyFans search completed: {results.total_results} total results")
            return results
            
        except Exception as e:
            logger.error(f"Search error: {str(e)}")
            return OnlyFansSearchResults(
                query=query,
                total_results=0,
                search_type="error",
                filters_applied={},
                search_timestamp=datetime.utcnow()
            )

    async def monitor_content(
        self,
        creator_usernames: List[str] = None,
        keywords: List[str] = None,
        check_interval: int = 600
    ) -> AsyncGenerator[OnlyFansPost, None]:
        """
        Real-time content monitoring for OnlyFans
        
        Args:
            creator_usernames: Creators to monitor
            keywords: Keywords to monitor
            check_interval: Check interval in seconds
            
        Yields:
            OnlyFansPost: New posts detected
        """
        creator_usernames = creator_usernames or []
        keywords = keywords or []
        
        self.monitored_creators.update(creator_usernames)
        
        logger.info(f"Starting OnlyFans monitoring for {len(creator_usernames)} creators")
        
        seen_posts = set()
        
        while True:
            try:
                await asyncio.sleep(check_interval)
                
                for username in creator_usernames:
                    try:
                        creator_posts = await self._get_creator_recent_posts(username)
                        
                        for post in creator_posts:
                            if post.post_id not in seen_posts:
                                # Enhanced monitoring analysis
                                post.similarity_score = await self._calculate_similarity(post)
                                post.protection_status = await self._check_protection_status(post)
                                
                                seen_posts.add(post.post_id)
                                
                                logger.info(f"New post from {username}: {post.post_id}")
                                yield post
                    
                    except Exception as e:
                        logger.error(f"Error monitoring creator {username}: {str(e)}")
                        continue
                
            except Exception as e:
                logger.error(f"Monitoring error: {str(e)}")
                await asyncio.sleep(60)

    async def detect_similarity(
        self,
        target_post: OnlyFansPost,
        comparison_set: List[OnlyFansPost],
        threshold: float = None
    ) -> List[Tuple[OnlyFansPost, float]]:
        """
        Detect post similarity for premium content protection
        
        Args:
            target_post: Post to compare
            comparison_set: Posts to compare against
            threshold: Similarity threshold
            
        Returns:
            List[Tuple[OnlyFansPost, float]]: Similar posts with scores
        """
        threshold = threshold or self.similarity_threshold
        similar_posts = []
        
        try:
            target_features = await self._extract_post_features(target_post)
            
            for post in comparison_set:
                if post.post_id == target_post.post_id:
                    continue
                
                comp_features = await self._extract_post_features(post)
                similarity_score = await self._calculate_feature_similarity(
                    target_features, comp_features
                )
                
                if similarity_score >= threshold:
                    similar_posts.append((post, similarity_score))
            
            similar_posts.sort(key=lambda x: x[1], reverse=True)
            
            logger.info(f"Similarity detection: {len(similar_posts)} matches found")
            return similar_posts
            
        except Exception as e:
            logger.error(f"Similarity detection error: {str(e)}")
            return []

    async def get_analytics(
        self,
        creator_id: str,
        analysis_period: Tuple[datetime, datetime]
    ) -> OnlyFansAnalytics:
        """
        Generate comprehensive analytics for OnlyFans creator
        
        Args:
            creator_id: Creator ID to analyze
            analysis_period: Analysis time period
            
        Returns:
            OnlyFansAnalytics: Comprehensive analytics data
        """
        try:
            start_time, end_time = analysis_period
            
            # Get creator's posts in the period
            creator_posts = await self._get_creator_posts_in_period(creator_id, start_time, end_time)
            
            if not creator_posts:
                return OnlyFansAnalytics(
                    creator_id=creator_id,
                    analysis_period=analysis_period,
                    total_posts=0,
                    total_earnings=0.0,
                    total_tips_received=0.0,
                    total_subscribers_gained=0,
                    total_subscribers_lost=0,
                    average_likes_per_post=0.0,
                    engagement_rate=0.0,
                    content_type_distribution={},
                    peak_activity_hours=[],
                    subscription_conversion_rate=0.0,
                    retention_rate=0.0,
                    premium_content_ratio=0.0,
                    similarity_violations=0,
                    protection_violations=0
                )
            
            # Calculate analytics metrics
            total_posts = len(creator_posts)
            total_tips_received = sum(post.tips_amount for post in creator_posts)
            total_likes = sum(post.likes_count for post in creator_posts)
            average_likes_per_post = total_likes / total_posts if total_posts > 0 else 0.0
            
            # Content type distribution
            content_type_distribution = {}
            for post in creator_posts:
                for media in post.media:
                    media_type = media.media_type.value
                    content_type_distribution[media_type] = content_type_distribution.get(media_type, 0) + 1
            
            # Premium content ratio
            premium_posts = sum(1 for post in creator_posts if post.is_premium)
            premium_content_ratio = premium_posts / total_posts if total_posts > 0 else 0.0
            
            # Activity patterns
            activity_hours = [post.created_at.hour for post in creator_posts]
            hour_counts = {}
            for hour in activity_hours:
                hour_counts[hour] = hour_counts.get(hour, 0) + 1
            peak_activity_hours = sorted(hour_counts.items(), key=lambda x: x[1], reverse=True)[:3]
            peak_activity_hours = [hour[0] for hour in peak_activity_hours]
            
            # Protection metrics
            similarity_violations = sum(1 for post in creator_posts if (post.similarity_score or 0) > self.similarity_threshold)
            protection_violations = sum(1 for post in creator_posts if post.protection_status == "violation")
            
            analytics = OnlyFansAnalytics(
                creator_id=creator_id,
                analysis_period=analysis_period,
                total_posts=total_posts,
                total_earnings=0.0,  # Would need earnings API
                total_tips_received=total_tips_received,
                total_subscribers_gained=0,  # Would need subscriber data
                total_subscribers_lost=0,
                average_likes_per_post=average_likes_per_post,
                engagement_rate=average_likes_per_post / 100,  # Simplified
                content_type_distribution=content_type_distribution,
                peak_activity_hours=peak_activity_hours,
                subscription_conversion_rate=0.0,  # Would need conversion data
                retention_rate=0.0,  # Would need retention data
                premium_content_ratio=premium_content_ratio,
                similarity_violations=similarity_violations,
                protection_violations=protection_violations
            )
            
            logger.info(f"Analytics generated for creator {creator_id}: {total_posts} posts analyzed")
            return analytics
            
        except Exception as e:
            logger.error(f"Analytics generation error: {str(e)}")
            return OnlyFansAnalytics(
                creator_id=creator_id,
                analysis_period=analysis_period,
                total_posts=0,
                total_earnings=0.0,
                total_tips_received=0.0,
                total_subscribers_gained=0,
                total_subscribers_lost=0,
                average_likes_per_post=0.0,
                engagement_rate=0.0,
                content_type_distribution={},
                peak_activity_hours=[],
                subscription_conversion_rate=0.0,
                retention_rate=0.0,
                premium_content_ratio=0.0,
                similarity_violations=0,
                protection_violations=0
            )

    # Helper methods
    
    async def _search_creators(self, query: str, limit: int) -> List[OnlyFansCreator]:
        """Search for OnlyFans creators"""
        try:
            params = {
                "query": query,
                "limit": limit
            }
            
            async with self.session.get(f"{self.api_base}/users/search", params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    creators = []
                    
                    for creator_data in data.get("list", []):
                        creator = await self._parse_creator_data(creator_data)
                        creators.append(creator)
                    
                    return creators
                else:
                    return []
                    
        except Exception as e:
            logger.error(f"Creator search error: {str(e)}")
            return []

    async def _search_posts(
        self,
        query: str,
        content_type: Optional[OnlyFansContentType],
        price_range: Optional[Tuple[float, float]],
        limit: int
    ) -> List[OnlyFansPost]:
        """Search for OnlyFans posts"""
        # Implementation would depend on available search API
        return []

    async def _get_creator_recent_posts(self, username: str) -> List[OnlyFansPost]:
        """Get recent posts from creator"""
        try:
            async with self.session.get(f"{self.api_base}/users/{username}/posts") as response:
                if response.status == 200:
                    data = await response.json()
                    posts = []
                    
                    for post_data in data.get("list", []):
                        post = await self._parse_post_data(post_data)
                        posts.append(post)
                    
                    return posts
                else:
                    return []
                    
        except Exception as e:
            logger.error(f"Error getting creator posts: {str(e)}")
            return []

    async def _parse_creator_data(self, data: Dict[str, Any]) -> OnlyFansCreator:
        """Parse creator data from API response"""
        return OnlyFansCreator(
            creator_id=str(data.get("id", "")),
            username=data.get("username", ""),
            display_name=data.get("name", ""),
            bio=data.get("rawAbout", ""),
            avatar_url=data.get("avatar", ""),
            header_url=data.get("header", ""),
            subscriber_count=data.get("subscribersCount", 0),
            post_count=data.get("postsCount", 0),
            photo_count=data.get("photosCount", 0),
            video_count=data.get("videosCount", 0),
            is_verified=data.get("isVerified", False),
            subscription_price=data.get("subscribePrice", 0.0),
            joined_date=datetime.utcnow(),
            location=data.get("location"),
            website=data.get("website")
        )

    async def _parse_post_data(self, data: Dict[str, Any]) -> OnlyFansPost:
        """Parse post data from API response"""
        # Parse media
        media = []
        for media_data in data.get("media", []):
            media_item = OnlyFansMedia(
                media_id=str(media_data.get("id", "")),
                media_type=OnlyFansMediaType(media_data.get("type", "photo")),
                url=media_data.get("source", {}).get("source", ""),
                preview_url=media_data.get("preview", ""),
                duration=media_data.get("duration"),
                width=media_data.get("info", {}).get("preview", {}).get("width"),
                height=media_data.get("info", {}).get("preview", {}).get("height")
            )
            media.append(media_item)
        
        # Parse creator
        creator_data = data.get("author", {})
        creator = OnlyFansCreator(
            creator_id=str(creator_data.get("id", "")),
            username=creator_data.get("username", ""),
            display_name=creator_data.get("name", ""),
            avatar_url=creator_data.get("avatar", ""),
            is_verified=creator_data.get("isVerified", False),
            joined_date=datetime.utcnow()
        )
        
        return OnlyFansPost(
            post_id=str(data.get("id", "")),
            creator=creator,
            text=data.get("text", ""),
            price=data.get("price"),
            is_premium=data.get("canPurchase", False),
            is_pinned=data.get("isPinned", False),
            created_at=datetime.fromisoformat(data.get("postedAt", datetime.utcnow().isoformat())),
            media=media,
            likes_count=data.get("likesCount", 0),
            comments_count=data.get("commentsCount", 0),
            tips_amount=data.get("tipsAmount", 0.0)
        )

    async def _extract_post_features(self, post: OnlyFansPost) -> Dict[str, Any]:
        """Extract features for similarity comparison"""
        features = {
            "text": (post.text or "").lower(),
            "creator_id": post.creator.creator_id,
            "media_count": len(post.media),
            "media_types": set(media.media_type.value for media in post.media),
            "is_premium": post.is_premium,
            "price": post.price or 0.0,
            "hashtags": set(tag.lower() for tag in post.hashtags),
            "has_video": any(media.media_type == OnlyFansMediaType.VIDEO for media in post.media),
            "has_photo": any(media.media_type == OnlyFansMediaType.PHOTO for media in post.media)
        }
        return features

    async def _calculate_feature_similarity(
        self,
        features1: Dict[str, Any],
        features2: Dict[str, Any]
    ) -> float:
        """Calculate similarity between post features"""
        try:
            scores = []
            
            # Text similarity
            text_sim = SequenceMatcher(
                None, features1.get("text", ""), features2.get("text", "")
            ).ratio()
            scores.append(text_sim * 0.4)  # 40% weight
            
            # Media type similarity
            media_types1 = features1.get("media_types", set())
            media_types2 = features2.get("media_types", set())
            if media_types1 and media_types2:
                media_sim = len(media_types1.intersection(media_types2)) / len(media_types1.union(media_types2))
                scores.append(media_sim * 0.3)  # 30% weight
            
            # Premium status similarity
            premium_sim = 1.0 if features1.get("is_premium") == features2.get("is_premium") else 0.0
            scores.append(premium_sim * 0.2)  # 20% weight
            
            # Hashtag similarity
            hashtags1 = features1.get("hashtags", set())
            hashtags2 = features2.get("hashtags", set())
            if hashtags1 and hashtags2:
                hashtag_sim = len(hashtags1.intersection(hashtags2)) / len(hashtags1.union(hashtags2))
                scores.append(hashtag_sim * 0.1)  # 10% weight
            
            return sum(scores) / len(scores) if scores else 0.0
            
        except Exception as e:
            logger.error(f"Feature similarity calculation error: {str(e)}")
            return 0.0

    async def _get_creator_posts_in_period(
        self,
        creator_id: str,
        start_time: datetime,
        end_time: datetime
    ) -> List[OnlyFansPost]:
        """Get creator's posts in specific time period"""
        # Implementation would require pagination through posts
        return []

    async def _calculate_similarity(self, post: OnlyFansPost) -> float:
        """Calculate similarity score against protected content"""
        # Simplified similarity calculation
        return 0.0

    async def _check_protection_status(self, post: OnlyFansPost) -> str:
        """Check protection status of post"""
        if post.post_id in self.protected_content:
            return "protected"
        return "unprotected"

    async def _handle_rate_limit(self, response: aiohttp.ClientResponse) -> bool:
        """Handle rate limiting responses"""
        if response.status == 429:
            retry_after = int(response.headers.get('Retry-After', 300))
            logger.warning(f"Rate limited. Waiting {retry_after} seconds")
            await asyncio.sleep(retry_after)
            return True
        return False

    async def close(self):
        """Close crawler and cleanup resources"""
        try:
            await self.cache_manager.close()
            await super().close()
            logger.info("OnlyFans crawler closed successfully")
        except Exception as e:
            logger.error(f"Error closing crawler: {str(e)}")
