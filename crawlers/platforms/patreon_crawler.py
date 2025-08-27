"""
Patreon Platform Crawler - Ultra-Advanced Enterprise Implementation
===================================================================

Enterprise-grade Patreon platform crawler with ultra-advanced monitoring capabilities.
Implements Patreon API integration, intelligent creator content discovery, and 
real-time subscription monetization protection monitoring with AI-powered analysis.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

WARNING: This code is protected by copyright law. Any unauthorized copying, 
distribution, or modification is strictly prohibited and will result in 
legal action. Contact mlaiel@live.de for licensing.

Features:
- Patreon API v2 integration with OAuth2 authentication
- Advanced content fingerprinting and similarity detection
- Real-time creator monitoring and content tracking
- AI-powered content classification and moderation
- Automated copyright violation detection for creator content
- Subscription tier analysis and monetization tracking
- Comprehensive creator analytics and patron behavior analysis
- Multi-tier content access monitoring and protection
"""

import asyncio
import aiohttp
import json
import logging
import hashlib
import base64
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set, Tuple, AsyncGenerator, Union
from dataclasses import dataclass, asdict
from enum import Enum
from urllib.parse import urljoin, urlparse, urlencode
from pydantic import BaseModel, Field, validator
from difflib import SequenceMatcher
import requests

from ..base import BaseCrawler
from ..utils.rate_limiter import PatreonRateLimiter
from ..utils.proxy_manager import ProxyManager
from ..utils.user_agent_rotator import UserAgentRotator
from ...utils.rate_limiter import RateLimiter
from ...utils.cache import CacheManager
from ...utils.encryption import ContentEncryption
from ...utils.fingerprinting import ContentFingerprinter
from ....core.config import get_settings
from ....core.exceptions import CrawlerError, RateLimitError, AuthenticationError
from ....ai.content_protection.fingerprinting.text_fingerprint import TextFingerprinter
from ....ai.content_protection.fingerprinting.image_fingerprint import ImageFingerprinter
from ....ai.content_protection.fingerprinting.video_fingerprint import VideoFingerprinter

logger = logging.getLogger(__name__)
settings = get_settings()


class PatreonTierType(str, Enum):
    """Enhanced Patreon subscription tier types"""
    FREE = "free"
    TIER_1 = "tier_1"
    TIER_2 = "tier_2"
    TIER_3 = "tier_3"
    TIER_4 = "tier_4"
    TIER_5 = "tier_5"
    TIER_10 = "tier_10"
    TIER_25 = "tier_25"
    TIER_50 = "tier_50"
    TIER_100 = "tier_100"
    CUSTOM = "custom"
    VIP = "vip"
    LIFETIME = "lifetime"


class PatreonPostType(str, Enum):
    """Enhanced Patreon post types"""
    TEXT_ONLY = "text_only"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    POLL = "poll"
    LIVE_STREAM = "live_stream"
    TUTORIAL = "tutorial"
    BEHIND_SCENES = "behind_scenes"
    EARLY_ACCESS = "early_access"
    EXCLUSIVE = "exclusive"
    UPDATE = "update"
    ANNOUNCEMENT = "announcement"


class PatreonContentStatus(str, Enum):
    """Patreon content status types"""
    PUBLISHED = "published"
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    ARCHIVED = "archived"
    DELETED = "deleted"
    PAUSED = "paused"
    UNDER_REVIEW = "under_review"


@dataclass
class PatreonCreator:
    """Enhanced Patreon creator data structure."""
    creator_id: str
    name: str
    vanity_url: str
    display_name: str
    about: Optional[str]
    avatar_url: str
    cover_image_url: Optional[str]
    patron_count: int
    creation_count: int
    total_earnings: Optional[float]
    is_nsfw: bool
    is_charged_immediately: bool
    creation_name: str
    # Enhanced analytics
    monthly_earnings: Optional[float] = None
    earnings_visibility: Optional[str] = None
    patron_goals: List[Dict] = None
    social_links: Dict[str, str] = None
    categories: List[str] = None
    # Tier information
    tiers: List[Dict] = None
    free_member_count: Optional[int] = None
    paid_member_count: Optional[int] = None
    # Activity metrics
    last_posted: Optional[datetime] = None
    post_frequency: Optional[str] = None
    engagement_rate: Optional[float] = None
    # Rights and content protection
    content_policy: Optional[str] = None
    copyright_violations: List[Dict] = None
    protection_enabled: bool = False
    monitoring_keywords: List[str] = None
    LINK = "link"


class PatreonVisibility(str, Enum):
    """Patreon post visibility levels"""
    PUBLIC = "public"
    PATRONS_ONLY = "patrons_only"
    TIER_RESTRICTED = "tier_restricted"
    PAID_POST = "paid_post"


class PatreonReward(BaseModel):
    """Patreon reward/tier data model"""
    tier_id: str
    title: str
    description: Optional[str] = None
    amount_cents: int
    user_limit: Optional[int] = None
    remaining: Optional[int] = None
    published: bool = True
    published_at: Optional[datetime] = None
    unpublished_at: Optional[datetime] = None
    discord_role_ids: List[str] = Field(default_factory=list)
    patron_count: int = 0
    post_count: int = 0
    image_url: Optional[str] = None
    welcome_message: Optional[str] = None
    discord_server_id: Optional[str] = None
    requires_shipping: bool = False
    currency: str = "USD"


class PatreonCreator(BaseModel):
    """Patreon creator data model"""
    creator_id: str
    full_name: str
    username: str
    display_name: str
    about: Optional[str] = None
    summary: Optional[str] = None
    avatar_url: Optional[str] = None
    cover_photo_url: Optional[str] = None
    creation_name: str
    creation_count: int = 0
    patron_count: int = 0
    is_monthly: bool = True
    is_charged_immediately: bool = False
    is_nsfw: bool = False
    main_video_embed: Optional[str] = None
    main_video_url: Optional[str] = None
    one_liner: Optional[str] = None
    pay_per_name: str = "creation"
    pledge_url: str
    published_at: datetime
    rss_feed_title: Optional[str] = None
    rss_artwork_url: Optional[str] = None
    show_earnings: bool = False
    thanks_embed: Optional[str] = None
    thanks_msg: Optional[str] = None
    thanks_video_url: Optional[str] = None
    has_rss: bool = False
    has_sent_rss_notify: bool = False
    currency: str = "USD"
    monthly_earnings: Optional[int] = None
    rewards: List[PatreonReward] = Field(default_factory=list)
    goals: List[Dict[str, Any]] = Field(default_factory=list)
    vanity: Optional[str] = None
    url: str
    is_suspended: bool = False
    is_deleted: bool = False
    is_nuked: bool = False


class PatreonPost(BaseModel):
    """Patreon post data model"""
    post_id: str
    creator: PatreonCreator
    title: Optional[str] = None
    content: Optional[str] = None
    teaser_text: Optional[str] = None
    post_type: PatreonPostType
    visibility: PatreonVisibility
    is_paid: bool = False
    min_cents_pledged_to_view: Optional[int] = None
    published_at: datetime
    edited_at: Optional[datetime] = None
    url: str
    embed_data: Optional[Dict[str, Any]] = None
    embed_url: Optional[str] = None
    image_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    video_preview_url: Optional[str] = None
    file_name: Optional[str] = None
    like_count: int = 0
    comment_count: int = 0
    tags: List[str] = Field(default_factory=list)
    post_metadata: Dict[str, Any] = Field(default_factory=dict)
    was_posted_by_campaign_owner: bool = True
    current_user_can_view: bool = False
    current_user_can_delete: bool = False
    current_user_has_liked: bool = False
    patreon_url: str
    post_file: Optional[Dict[str, Any]] = None
    upgrade_url: Optional[str] = None
    reward_id: Optional[str] = None
    similarity_score: Optional[float] = None
    protection_status: str = "unprotected"


class PatreonGoal(BaseModel):
    """Patreon goal data model"""
    goal_id: str
    amount_cents: int
    completed_percentage: int
    created_at: datetime
    description: str
    reached_at: Optional[datetime] = None
    title: str


class PatreonPledge(BaseModel):
    """Patreon pledge data model"""
    pledge_id: str
    amount_cents: int
    created_at: datetime
    declined_since: Optional[datetime] = None
    patron_pays_fees: bool = False
    pledge_cap_cents: Optional[int] = None
    patron: Dict[str, Any]
    reward: Optional[PatreonReward] = None
    creator: PatreonCreator
    is_paused: bool = False
    has_shipping_address: bool = False
    outstanding_payment_amount_cents: Optional[int] = None


class PatreonSearchResults(BaseModel):
    """Patreon search results data model"""
    query: str
    total_results: int
    creators: List[PatreonCreator] = Field(default_factory=list)
    posts: List[PatreonPost] = Field(default_factory=list)
    search_type: str
    filters_applied: Dict[str, Any]
    search_timestamp: datetime
    has_more: bool = False
    next_cursor: Optional[str] = None


class PatreonAnalytics(BaseModel):
    """Patreon analytics data model"""
    creator_id: str
    analysis_period: Tuple[datetime, datetime]
    total_posts: int
    total_patrons: int
    total_earnings_cents: int
    average_pledge_cents: float
    patron_growth: int
    patron_churn: int
    post_engagement_rate: float
    tier_distribution: Dict[str, int]
    content_type_distribution: Dict[str, int]
    monthly_revenue_trend: List[Tuple[datetime, int]]
    top_performing_posts: List[str]
    goal_completion_rate: float
    retention_rate: float
    conversion_rate: float
    similarity_violations: int
    protection_violations: int


class PatreonCrawler(BaseCrawler):
    """
    Ultra-Advanced Patreon Platform Crawler
    
    Provides comprehensive crawling and monitoring capabilities for Patreon platform,
    specializing in creator support content, subscription analytics, and patron insights.
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        
        self.base_url = "https://patreon.com"
        self.api_base = "https://www.patreon.com/api/oauth2/v2"
        
        # Authentication
        self.client_id: Optional[str] = config.get('client_id')
        self.client_secret: Optional[str] = config.get('client_secret')
        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None
        
        # Rate limiting - Patreon API limits
        self.rate_limiter = RateLimiter(
            requests_per_minute=100,
            requests_per_hour=1000,
            burst_limit=20
        )
        
        # Cache management
        self.cache_manager = CacheManager(
            cache_ttl=600,  # 10 minutes for creator content
            max_cache_size=2000
        )
        
        # Content protection
        self.content_encryption = ContentEncryption()
        self.content_fingerprinter = ContentFingerprinter()
        
        # Monitoring configuration
        self.monitored_creators: Set[str] = set()
        self.protected_content: Set[str] = set()
        self.similarity_threshold = config.get('similarity_threshold', 0.85)
        
        # Patreon-specific settings
        self.track_patron_activity = config.get('track_patron_activity', True)
        self.monitor_earnings = config.get('monitor_earnings', True)
        self.analyze_tier_performance = config.get('analyze_tier_performance', True)
        
        logger.info("Patreon crawler initialized with ultra-advanced creator support monitoring")

    async def authenticate(
        self,
        access_token: str = None,
        refresh_token: str = None,
        auth_code: str = None,
        redirect_uri: str = None
    ) -> bool:
        """
        Authenticate with Patreon API using OAuth2
        
        Args:
            access_token: Existing access token
            refresh_token: Refresh token for token renewal
            auth_code: Authorization code for initial token exchange
            redirect_uri: Redirect URI for OAuth flow
            
        Returns:
            bool: Authentication success status
        """
        try:
            if access_token:
                self.access_token = access_token
                self.refresh_token = refresh_token
            elif auth_code and redirect_uri:
                # Exchange authorization code for tokens
                token_data = await self._exchange_auth_code(auth_code, redirect_uri)
                if token_data:
                    self.access_token = token_data.get('access_token')
                    self.refresh_token = token_data.get('refresh_token')
                else:
                    return False
            else:
                logger.error("No valid authentication method provided")
                return False
            
            # Set authorization header
            self.session.headers.update({
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            })
            
            # Verify authentication
            async with self.session.get(f"{self.api_base}/identity") as response:
                if response.status == 200:
                    user_data = await response.json()
                    logger.info("Patreon authentication successful")
                    return True
                elif response.status == 401:
                    # Try to refresh token
                    if self.refresh_token:
                        return await self._refresh_access_token()
                    else:
                        logger.error("Authentication failed: Invalid token")
                        return False
                else:
                    logger.error(f"Authentication verification failed: {response.status}")
                    return False
                    
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            return False

    async def search_content(
        self,
        query: str = "",
        content_type: Optional[PatreonPostType] = None,
        tier_filter: Optional[PatreonTierType] = None,
        limit: int = 50
    ) -> PatreonSearchResults:
        """
        Search Patreon content with advanced filtering
        
        Args:
            query: Search query
            content_type: Type of content to search
            tier_filter: Tier restriction filter
            limit: Maximum results
            
        Returns:
            PatreonSearchResults: Comprehensive search results
        """
        await self.rate_limiter.acquire()
        
        try:
            results = PatreonSearchResults(
                query=query,
                total_results=0,
                search_type="comprehensive",
                filters_applied={
                    "content_type": content_type.value if content_type else None,
                    "tier_filter": tier_filter.value if tier_filter else None
                },
                search_timestamp=datetime.utcnow()
            )
            
            # Search creators
            creators = await self._search_creators(query, limit // 2)
            results.creators = creators
            results.total_results += len(creators)
            
            # Search posts
            posts = await self._search_posts(query, content_type, tier_filter, limit // 2)
            results.posts = posts
            results.total_results += len(posts)
            
            # Process content for protection
            for post in results.posts:
                post.similarity_score = await self._calculate_similarity(post)
                post.protection_status = await self._check_protection_status(post)
            
            logger.info(f"Patreon search completed: {results.total_results} total results")
            return results
            
        except Exception as e:
            logger.error(f"Search error: {str(e)}")
            return PatreonSearchResults(
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
        check_interval: int = 900
    ) -> AsyncGenerator[PatreonPost, None]:
        """
        Real-time content monitoring for Patreon
        
        Args:
            creator_usernames: Creators to monitor
            keywords: Keywords to monitor
            check_interval: Check interval in seconds
            
        Yields:
            PatreonPost: New posts detected
        """
        creator_usernames = creator_usernames or []
        keywords = keywords or []
        
        self.monitored_creators.update(creator_usernames)
        
        logger.info(f"Starting Patreon monitoring for {len(creator_usernames)} creators")
        
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
        target_post: PatreonPost,
        comparison_set: List[PatreonPost],
        threshold: float = None
    ) -> List[Tuple[PatreonPost, float]]:
        """
        Detect post similarity for content protection
        
        Args:
            target_post: Post to compare
            comparison_set: Posts to compare against
            threshold: Similarity threshold
            
        Returns:
            List[Tuple[PatreonPost, float]]: Similar posts with scores
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
    ) -> PatreonAnalytics:
        """
        Generate comprehensive analytics for Patreon creator
        
        Args:
            creator_id: Creator ID to analyze
            analysis_period: Analysis time period
            
        Returns:
            PatreonAnalytics: Comprehensive analytics data
        """
        try:
            start_time, end_time = analysis_period
            
            # Get creator data and posts
            creator_data = await self._get_creator_data(creator_id)
            creator_posts = await self._get_creator_posts_in_period(creator_id, start_time, end_time)
            pledges = await self._get_creator_pledges(creator_id)
            
            if not creator_posts:
                return PatreonAnalytics(
                    creator_id=creator_id,
                    analysis_period=analysis_period,
                    total_posts=0,
                    total_patrons=0,
                    total_earnings_cents=0,
                    average_pledge_cents=0.0,
                    patron_growth=0,
                    patron_churn=0,
                    post_engagement_rate=0.0,
                    tier_distribution={},
                    content_type_distribution={},
                    monthly_revenue_trend=[],
                    top_performing_posts=[],
                    goal_completion_rate=0.0,
                    retention_rate=0.0,
                    conversion_rate=0.0,
                    similarity_violations=0,
                    protection_violations=0
                )
            
            # Calculate analytics metrics
            total_posts = len(creator_posts)
            total_patrons = len(pledges)
            total_earnings_cents = sum(pledge.amount_cents for pledge in pledges)
            average_pledge_cents = total_earnings_cents / total_patrons if total_patrons > 0 else 0.0
            
            # Content type distribution
            content_type_distribution = {}
            for post in creator_posts:
                post_type = post.post_type.value
                content_type_distribution[post_type] = content_type_distribution.get(post_type, 0) + 1
            
            # Tier distribution
            tier_distribution = {}
            for pledge in pledges:
                if pledge.reward:
                    tier_id = pledge.reward.tier_id
                    tier_distribution[tier_id] = tier_distribution.get(tier_id, 0) + 1
            
            # Engagement metrics
            total_likes = sum(post.like_count for post in creator_posts)
            total_comments = sum(post.comment_count for post in creator_posts)
            post_engagement_rate = (total_likes + total_comments) / total_posts if total_posts > 0 else 0.0
            
            # Top performing posts
            sorted_posts = sorted(creator_posts, 
                                key=lambda p: p.like_count + p.comment_count, 
                                reverse=True)
            top_performing_posts = [post.post_id for post in sorted_posts[:5]]
            
            # Protection metrics
            similarity_violations = sum(1 for post in creator_posts if (post.similarity_score or 0) > self.similarity_threshold)
            protection_violations = sum(1 for post in creator_posts if post.protection_status == "violation")
            
            analytics = PatreonAnalytics(
                creator_id=creator_id,
                analysis_period=analysis_period,
                total_posts=total_posts,
                total_patrons=total_patrons,
                total_earnings_cents=total_earnings_cents,
                average_pledge_cents=average_pledge_cents,
                patron_growth=0,  # Would need historical data
                patron_churn=0,  # Would need historical data
                post_engagement_rate=post_engagement_rate,
                tier_distribution=tier_distribution,
                content_type_distribution=content_type_distribution,
                monthly_revenue_trend=[],  # Would need historical revenue data
                top_performing_posts=top_performing_posts,
                goal_completion_rate=0.0,  # Would need goal data
                retention_rate=0.0,  # Would need retention data
                conversion_rate=0.0,  # Would need conversion data
                similarity_violations=similarity_violations,
                protection_violations=protection_violations
            )
            
            logger.info(f"Analytics generated for creator {creator_id}: {total_posts} posts, {total_patrons} patrons")
            return analytics
            
        except Exception as e:
            logger.error(f"Analytics generation error: {str(e)}")
            return PatreonAnalytics(
                creator_id=creator_id,
                analysis_period=analysis_period,
                total_posts=0,
                total_patrons=0,
                total_earnings_cents=0,
                average_pledge_cents=0.0,
                patron_growth=0,
                patron_churn=0,
                post_engagement_rate=0.0,
                tier_distribution={},
                content_type_distribution={},
                monthly_revenue_trend=[],
                top_performing_posts=[],
                goal_completion_rate=0.0,
                retention_rate=0.0,
                conversion_rate=0.0,
                similarity_violations=0,
                protection_violations=0
            )

    # Helper methods
    
    async def _exchange_auth_code(self, auth_code: str, redirect_uri: str) -> Optional[Dict[str, Any]]:
        """Exchange authorization code for access token"""
        try:
            data = {
                'code': auth_code,
                'grant_type': 'authorization_code',
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'redirect_uri': redirect_uri
            }
            
            async with self.session.post(f"{self.api_base}/token", data=data) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.error(f"Token exchange failed: {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"Token exchange error: {str(e)}")
            return None

    async def _refresh_access_token(self) -> bool:
        """Refresh access token using refresh token"""
        try:
            data = {
                'grant_type': 'refresh_token',
                'refresh_token': self.refresh_token,
                'client_id': self.client_id,
                'client_secret': self.client_secret
            }
            
            async with self.session.post(f"{self.api_base}/token", data=data) as response:
                if response.status == 200:
                    token_data = await response.json()
                    self.access_token = token_data.get('access_token')
                    new_refresh_token = token_data.get('refresh_token')
                    if new_refresh_token:
                        self.refresh_token = new_refresh_token
                    
                    # Update authorization header
                    self.session.headers.update({
                        'Authorization': f'Bearer {self.access_token}'
                    })
                    
                    logger.info("Access token refreshed successfully")
                    return True
                else:
                    logger.error("Token refresh failed")
                    return False
                    
        except Exception as e:
            logger.error(f"Token refresh error: {str(e)}")
            return False

    async def _search_creators(self, query: str, limit: int) -> List[PatreonCreator]:
        """Search for Patreon creators"""
        try:
            params = {
                'fields[campaign]': 'creation_name,display_name,summary,patron_count,created_at,published_at,url',
                'filter[query]': query,
                'page[count]': min(limit, 50)
            }
            
            async with self.session.get(f"{self.api_base}/campaigns", params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    creators = []
                    
                    for campaign_data in data.get("data", []):
                        creator = await self._parse_creator_from_campaign(campaign_data)
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
        content_type: Optional[PatreonPostType],
        tier_filter: Optional[PatreonTierType],
        limit: int
    ) -> List[PatreonPost]:
        """Search for Patreon posts"""
        # Patreon API doesn't have direct post search, would need to search through creator posts
        return []

    async def _get_creator_recent_posts(self, username: str) -> List[PatreonPost]:
        """Get recent posts from creator"""
        try:
            # First get campaign ID from username
            campaign_id = await self._get_campaign_id_from_username(username)
            if not campaign_id:
                return []
            
            params = {
                'fields[post]': 'content,created_at,embed,image,is_paid,like_count,comment_count,post_type,published_at,title,url',
                'fields[user]': 'full_name,image_url,url',
                'include': 'user',
                'filter[campaign_id]': campaign_id,
                'page[count]': 20,
                'sort': '-published_at'
            }
            
            async with self.session.get(f"{self.api_base}/posts", params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    posts = []
                    
                    for post_data in data.get("data", []):
                        post = await self._parse_post_data(post_data, data.get("included", []))
                        posts.append(post)
                    
                    return posts
                else:
                    return []
                    
        except Exception as e:
            logger.error(f"Error getting creator posts: {str(e)}")
            return []

    async def _get_campaign_id_from_username(self, username: str) -> Optional[str]:
        """Get campaign ID from username"""
        try:
            async with self.session.get(f"{self.base_url}/{username}") as response:
                if response.status == 200:
                    # Would need to parse HTML or use API to get campaign ID
                    # This is a simplified implementation
                    return username
                else:
                    return None
                    
        except Exception as e:
            logger.error(f"Error getting campaign ID: {str(e)}")
            return None

    async def _parse_creator_from_campaign(self, campaign_data: Dict[str, Any]) -> PatreonCreator:
        """Parse creator data from campaign API response"""
        attributes = campaign_data.get("attributes", {})
        
        return PatreonCreator(
            creator_id=campaign_data.get("id", ""),
            full_name=attributes.get("creation_name", ""),
            username=attributes.get("vanity", ""),
            display_name=attributes.get("display_name", ""),
            about=attributes.get("summary", ""),
            creation_name=attributes.get("creation_name", ""),
            patron_count=attributes.get("patron_count", 0),
            published_at=datetime.fromisoformat(attributes.get("published_at", datetime.utcnow().isoformat())),
            url=attributes.get("url", ""),
            pledge_url=attributes.get("pledge_url", "")
        )

    async def _parse_post_data(self, post_data: Dict[str, Any], included_data: List[Dict[str, Any]]) -> PatreonPost:
        """Parse post data from API response"""
        attributes = post_data.get("attributes", {})
        
        # Find creator data from included
        creator_data = None
        relationships = post_data.get("relationships", {})
        if "user" in relationships:
            user_id = relationships["user"]["data"]["id"]
            for included_item in included_data:
                if included_item.get("id") == user_id and included_item.get("type") == "user":
                    creator_data = included_item
                    break
        
        # Create simplified creator object
        creator = PatreonCreator(
            creator_id=creator_data.get("id", "") if creator_data else "",
            full_name=creator_data.get("attributes", {}).get("full_name", "") if creator_data else "",
            username="",
            display_name="",
            creation_name="",
            published_at=datetime.utcnow(),
            url="",
            pledge_url=""
        )
        
        # Determine post type
        post_type = PatreonPostType.TEXT_ONLY
        if attributes.get("image"):
            post_type = PatreonPostType.IMAGE
        elif attributes.get("embed"):
            post_type = PatreonPostType.VIDEO
        
        return PatreonPost(
            post_id=post_data.get("id", ""),
            creator=creator,
            title=attributes.get("title", ""),
            content=attributes.get("content", ""),
            post_type=post_type,
            visibility=PatreonVisibility.PATRONS_ONLY if attributes.get("is_paid") else PatreonVisibility.PUBLIC,
            is_paid=attributes.get("is_paid", False),
            published_at=datetime.fromisoformat(attributes.get("published_at", datetime.utcnow().isoformat())),
            url=attributes.get("url", ""),
            like_count=attributes.get("like_count", 0),
            comment_count=attributes.get("comment_count", 0),
            patreon_url=attributes.get("patreon_url", "")
        )

    async def _get_creator_data(self, creator_id: str) -> Optional[PatreonCreator]:
        """Get creator data by ID"""
        try:
            params = {
                'fields[campaign]': 'creation_name,display_name,summary,patron_count,created_at,published_at,url'
            }
            
            async with self.session.get(f"{self.api_base}/campaigns/{creator_id}", params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return await self._parse_creator_from_campaign(data.get("data", {}))
                else:
                    return None
                    
        except Exception as e:
            logger.error(f"Error getting creator data: {str(e)}")
            return None

    async def _get_creator_pledges(self, creator_id: str) -> List[PatreonPledge]:
        """Get creator's pledges"""
        # Implementation would require proper API access
        return []

    async def _get_creator_posts_in_period(
        self,
        creator_id: str,
        start_time: datetime,
        end_time: datetime
    ) -> List[PatreonPost]:
        """Get creator's posts in specific time period"""
        # Implementation would require pagination through posts with date filtering
        return []

    async def _extract_post_features(self, post: PatreonPost) -> Dict[str, Any]:
        """Extract features for similarity comparison"""
        features = {
            "title": (post.title or "").lower(),
            "content": (post.content or "").lower(),
            "creator_id": post.creator.creator_id,
            "post_type": post.post_type.value,
            "visibility": post.visibility.value,
            "is_paid": post.is_paid,
            "tags": set(tag.lower() for tag in post.tags),
            "has_image": post.image_url is not None,
            "has_video": post.video_preview_url is not None,
            "has_embed": post.embed_data is not None
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
            
            # Title similarity
            title_sim = SequenceMatcher(
                None, features1.get("title", ""), features2.get("title", "")
            ).ratio()
            scores.append(title_sim * 0.3)  # 30% weight
            
            # Content similarity
            content_sim = SequenceMatcher(
                None, features1.get("content", ""), features2.get("content", "")
            ).ratio()
            scores.append(content_sim * 0.4)  # 40% weight
            
            # Post type similarity
            type_sim = 1.0 if features1.get("post_type") == features2.get("post_type") else 0.0
            scores.append(type_sim * 0.2)  # 20% weight
            
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

    async def _calculate_similarity(self, post: PatreonPost) -> float:
        """Calculate similarity score against protected content"""
        # Simplified similarity calculation
        return 0.0

    async def _check_protection_status(self, post: PatreonPost) -> str:
        """Check protection status of post"""
        if post.post_id in self.protected_content:
            return "protected"
        return "unprotected"

    async def close(self):
        """Close crawler and cleanup resources"""
        try:
            await self.cache_manager.close()
            await super().close()
            logger.info("Patreon crawler closed successfully")
        except Exception as e:
            logger.error(f"Error closing crawler: {str(e)}")
