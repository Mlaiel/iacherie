"""
Threads Platform Crawler (Meta)
===============================

Enterprise-grade Meta Threads content crawler with ultra-advanced monitoring capabilities.
Implements Threads API integration, intelligent content discovery, and 
real-time social media content protection with AI-powered analysis.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

WARNING: This code is protected by copyright law. Any unauthorized copying, 
distribution, or modification is strictly prohibited and will result in 
legal action. Contact mlaiel@live.de for licensing.

Features:
- Meta Threads API integration with advanced authentication
- Real-time thread and reply monitoring
- AI-powered content classification and moderation
- Automated engagement and viral content detection
- Multi-user content discovery and tracking
- Media content analysis and fingerprinting
- Comprehensive user analytics and behavior analysis
- Content fingerprinting for copyright protection
"""

import asyncio
import logging
from typing import Dict, List, Optional, Union, AsyncGenerator, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import json
import re
import base64
import hashlib
from urllib.parse import urljoin, urlencode

import aiohttp
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

from ..utils.rate_limiter import ThreadsRateLimiter
from ..utils.proxy_manager import ProxyManager
from ..utils.user_agent_rotator import UserAgentRotator
from ...core.config import get_settings
from ...core.exceptions import CrawlerError, RateLimitError, AuthenticationError
from ...database.models import CrawlResult, ContentMatch
from ...ai.content_protection.fingerprinting.text_fingerprint import TextFingerprinter
from ...ai.content_protection.fingerprinting.image_fingerprint import ImageFingerprinter
from ...ai.content_protection.fingerprinting.video_fingerprint import VideoFingerprinter

logger = logging.getLogger(__name__)
settings = get_settings()

@dataclass
class ThreadsPost:
    """Threads post data structure with enhanced analysis."""
    post_id: str
    text: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    author_id: str
    author_username: str
    author_display_name: str
    author_verified: bool
    # Post metrics
    like_count: int
    reply_count: int
    repost_count: int
    view_count: Optional[int]
    # Content analysis
    media_attachments: List[Dict] = None
    hashtags: List[str] = None
    mentions: List[str] = None
    links: List[str] = None
    thread_id: Optional[str] = None
    parent_post_id: Optional[str] = None
    is_reply: bool = False
    is_repost: bool = False
    # Advanced analysis
    content_fingerprint: Optional[str] = None
    media_fingerprints: List[str] = None
    sentiment_score: Optional[float] = None
    toxicity_score: Optional[float] = None
    engagement_rate: Optional[float] = None
    viral_score: Optional[float] = None
    language: Optional[str] = None
    # Copyright protection
    copyright_matches: List[Dict] = None
    violation_flags: List[str] = None
    protection_status: Optional[str] = None
    # Threading context
    thread_depth: int = 0
    thread_root_id: Optional[str] = None

@dataclass
class ThreadsUser:
    """Threads user data structure."""
    user_id: str
    username: str
    display_name: str
    biography: Optional[str]
    profile_picture_url: Optional[str]
    verified: bool
    follower_count: Optional[int]
    following_count: Optional[int]
    post_count: Optional[int]
    # Profile details
    website: Optional[str] = None
    location: Optional[str] = None
    joined_date: Optional[datetime] = None
    # Analytics
    engagement_rate: Optional[float] = None
    average_likes: Optional[float] = None
    average_replies: Optional[float] = None
    growth_rate: Optional[float] = None
    # Activity patterns
    posting_frequency: Optional[str] = None
    peak_hours: List[int] = None
    # Content analysis
    primary_topics: List[str] = None
    content_categories: List[str] = None
    # Behavior metrics
    toxicity_score: Optional[float] = None
    spam_probability: Optional[float] = None

@dataclass
class ThreadsThread:
    """Complete Threads conversation thread."""
    thread_id: str
    root_post: ThreadsPost
    replies: List[ThreadsPost]
    total_replies: int
    participants: List[str]
    created_at: datetime
    last_activity: datetime
    # Thread analytics
    engagement_score: Optional[float] = None
    virality_score: Optional[float] = None
    sentiment_distribution: Optional[Dict] = None
    # Content analysis
    main_topics: List[str] = None
    language_distribution: Optional[Dict] = None

class ThreadsCrawler:
    """
    Enterprise Meta Threads content crawler with advanced monitoring capabilities.
    
    Provides comprehensive Threads content discovery, monitoring, and analysis
    with focus on social media engagement and content protection.
    """
    
    def __init__(self, 
                 access_token: str = None,
                 proxy_manager: ProxyManager = None,
                 rate_limiter: ThreadsRateLimiter = None,
                 use_selenium: bool = False):
        """
        Initialize Threads crawler.
        
        Args:
            access_token: Threads API access token (when available)
            proxy_manager: Proxy manager instance
            rate_limiter: Rate limiter instance
            use_selenium: Use Selenium for web scraping fallback
        """
        self.access_token = access_token
        self.proxy_manager = proxy_manager or ProxyManager()
        self.rate_limiter = rate_limiter or ThreadsRateLimiter()
        self.user_agent_rotator = UserAgentRotator()
        self.use_selenium = use_selenium
        
        # Initialize fingerprinters
        self.text_fingerprinter = TextFingerprinter()
        self.image_fingerprinter = ImageFingerprinter()
        self.video_fingerprinter = VideoFingerprinter()
        
        # API endpoints
        self.base_url = "https://graph.threads.net"  # Official API when available
        self.web_base_url = "https://www.threads.net"
        
        self.session = None
        self.driver = None
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Monitoring state
        self.monitored_users = set()
        self.monitored_hashtags = set()
        self.content_violations = []
        
    async def __aenter__(self):
        """Async context manager entry."""
        await self.initialize()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
        
    async def initialize(self):
        """Initialize the crawler session and browser."""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers=self.user_agent_rotator.get_headers()
        )
        
        if self.use_selenium:
            await self._initialize_selenium()
        
        self.logger.info("Threads crawler initialized")
        
    async def close(self):
        """Close the crawler session and browser."""
        if self.session:
            await self.session.close()
        
        if self.driver:
            self.driver.quit()
            
        self.logger.info("Threads crawler closed")
        
    async def _initialize_selenium(self):
        """Initialize Selenium WebDriver."""
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument(f'--user-agent={self.user_agent_rotator.get_user_agent()}')
        
        if self.proxy_manager:
            proxy_url = await self.proxy_manager.get_proxy()
            if proxy_url:
                chrome_options.add_argument(f'--proxy-server={proxy_url}')
        
        self.driver = webdriver.Chrome(options=chrome_options)
        
    async def _make_api_request(self, endpoint: str, params: Dict = None, method: str = "GET") -> Dict:
        """Make request to Threads API (when available)."""
        if not self.access_token:
            raise AuthenticationError("Threads API access token required")
        
        await self.rate_limiter.acquire()
        
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json',
            **self.user_agent_rotator.get_headers()
        }
        
        try:
            proxy_url = await self.proxy_manager.get_proxy() if self.proxy_manager else None
            
            async with self.session.request(
                method=method,
                url=url,
                params=params,
                headers=headers,
                proxy=proxy_url
            ) as response:
                
                if response.status == 429:
                    self.logger.warning("Rate limit hit, backing off")
                    await asyncio.sleep(60)
                    raise RateLimitError("Threads API rate limit exceeded")
                
                if response.status == 401:
                    raise AuthenticationError("Threads API authentication failed")
                
                if not response.ok:
                    error_text = await response.text()
                    self.logger.error(f"API request failed: {response.status} - {error_text}")
                    raise CrawlerError(f"Threads API error: {response.status}")
                
                return await response.json()
                
        except aiohttp.ClientError as e:
            self.logger.error(f"Request failed: {str(e)}")
            raise CrawlerError(f"Network error: {str(e)}")
    
    async def search_posts(self, 
                          query: str, 
                          limit: int = 50,
                          sort_by: str = "recent") -> List[ThreadsPost]:
        """
        Search for posts on Threads.
        
        Args:
            query: Search query
            limit: Maximum results
            sort_by: Sort order (recent, popular, etc.)
            
        Returns:
            List of matching posts
        """



        try:
            # Since official API might not be available, use web scraping
            if self.use_selenium:
                return await self._search_posts_selenium(query, limit, sort_by)
            else:
                # Fallback to HTTP requests
                return await self._search_posts_http(query, limit, sort_by)
            
        except Exception as e:
            self.logger.error(f"Post search failed: {str(e)}")
            raise CrawlerError(f"Post search error: {str(e)}")
    
    async def get_user_posts(self, 
                            username: str, 
                            limit: int = 50,
                            include_replies: bool = False) -> List[ThreadsPost]:
        """
        Get posts from a specific user.
        
        Args:
            username: Threads username
            limit: Maximum posts to return
            include_replies: Include reply posts
            
        Returns:
            List of user posts
        """



        try:
            if self.use_selenium:
                return await self._get_user_posts_selenium(username, limit, include_replies)
            else:
                return await self._get_user_posts_http(username, limit, include_replies)
            
        except Exception as e:
            self.logger.error(f"User posts retrieval failed: {str(e)}")
            raise CrawlerError(f"User posts error: {str(e)}")
    
    async def get_thread_conversation(self, post_id: str) -> ThreadsThread:
        """
        Get complete conversation thread.
        
        Args:
            post_id: Root post ID
            
        Returns:
            Complete thread with all replies
        """



        try:
            if self.use_selenium:
                return await self._get_thread_selenium(post_id)
            else:
                return await self._get_thread_http(post_id)
            
        except Exception as e:
            self.logger.error(f"Thread retrieval failed: {str(e)}")
            raise CrawlerError(f"Thread retrieval error: {str(e)}")
    
    async def monitor_user(self, username: str) -> Dict:
        """
        Start monitoring a specific user.
        
        Args:
            username: Threads username to monitor
            
        Returns:
            Monitoring configuration
        """



        try:
            self.monitored_users.add(username)
            
            # Get initial user data
            user_data = await self.get_user_profile(username)
            recent_posts = await self.get_user_posts(username, limit=10)
            
            monitoring_config = {
                'username': username,
                'monitoring_started': datetime.utcnow(),
                'initial_posts_count': len(recent_posts),
                'user_data': asdict(user_data) if user_data else None
            }
            
            self.logger.info(f"Started monitoring user: {username}")
            return monitoring_config
            
        except Exception as e:
            self.logger.error(f"Failed to start user monitoring: {str(e)}")
            raise CrawlerError(f"User monitoring error: {str(e)}")
    
    async def detect_trending_content(self, 
                                     time_window: int = 24,
                                     min_engagement: int = 100) -> List[ThreadsPost]:
        """
        Detect trending content based on engagement metrics.
        
        Args:
            time_window: Time window in hours to analyze
            min_engagement: Minimum engagement threshold
            
        Returns:
            List of trending posts
        """



        try:
            trending_posts = []
            cutoff_time = datetime.utcnow() - timedelta(hours=time_window)
            
            # Search for recent high-engagement content
            for query in ['trending', 'viral', 'popular']:
                posts = await self.search_posts(query, limit=100)
                
                for post in posts:
                    if (post.created_at >= cutoff_time and 
                        (post.like_count + post.reply_count + post.repost_count) >= min_engagement):
                        
                        # Calculate engagement rate
                        total_engagement = post.like_count + post.reply_count + post.repost_count
                        post.engagement_rate = total_engagement / max(post.view_count or 1, 1)
                        post.viral_score = self._calculate_viral_score(post)
                        
                        trending_posts.append(post)
            
            # Sort by viral score
            trending_posts.sort(key=lambda x: x.viral_score or 0, reverse=True)
            
            self.logger.info(f"Found {len(trending_posts)} trending posts")
            return trending_posts[:50]  # Return top 50
            
        except Exception as e:
            self.logger.error(f"Trending content detection failed: {str(e)}")
            raise CrawlerError(f"Trending detection error: {str(e)}")
    
    async def detect_content_violations(self, 
                                       protected_content: List[str],
                                       similarity_threshold: float = 0.8) -> List[Dict]:
        """
        Detect potential content violations.
        
        Args:
            protected_content: List of protected content fingerprints
            similarity_threshold: Minimum similarity for violation
            
        Returns:
            List of potential violations
        """



        try:
            violations = []
            
            # Check monitored users
            for username in self.monitored_users:
                recent_posts = await self.get_user_posts(username, limit=50)
                
                for post in recent_posts:
                    if not post.content_fingerprint:
                        continue
                    
                    # Check against protected content
                    for protected_fp in protected_content:
                        similarity = await self._calculate_content_similarity(
                            post.content_fingerprint,
                            protected_fp
                        )
                        
                        if similarity >= similarity_threshold:
                            violation = {
                                'post_id': post.post_id,
                                'author_username': post.author_username,
                                'content_similarity': similarity,
                                'detected_at': datetime.utcnow(),
                                'violation_type': 'content_similarity',
                                'protected_content_id': protected_fp
                            }
                            violations.append(violation)
            
            self.logger.info(f"Detected {len(violations)} potential violations")
            return violations
            
        except Exception as e:
            self.logger.error(f"Violation detection failed: {str(e)}")
            raise CrawlerError(f"Violation detection error: {str(e)}")
    
    async def _search_posts_selenium(self, query: str, limit: int, sort_by: str) -> List[ThreadsPost]:
        """Search posts using Selenium web scraping."""
        if not self.driver:
            await self._initialize_selenium()
        
        search_url = f"{self.web_base_url}/search?q={urlencode({'q': query})}"
        self.driver.get(search_url)
        
        posts = []
        # Implementation would involve parsing DOM elements
        # This is a simplified structure
        
        return posts
    
    async def _search_posts_http(self, query: str, limit: int, sort_by: str) -> List[ThreadsPost]:
        """Search posts using HTTP requests."""
        # Implementation for HTTP-based searching
        # This would involve reverse-engineering web requests
        
        posts = []
        return posts
    
    async def get_user_profile(self, username: str) -> ThreadsUser:
        """Get user profile information."""



        try:
            if self.use_selenium:
                return await self._get_user_profile_selenium(username)
            else:
                return await self._get_user_profile_http(username)
            
        except Exception as e:
            self.logger.error(f"User profile retrieval failed: {str(e)}")
            raise CrawlerError(f"User profile error: {str(e)}")
    
    def _calculate_viral_score(self, post: ThreadsPost) -> float:
        """Calculate viral score for a post."""
        # Viral score calculation based on engagement metrics
        total_engagement = post.like_count + (post.reply_count * 2) + (post.repost_count * 3)
        time_factor = max(1, (datetime.utcnow() - post.created_at).total_seconds() / 3600)
        
        viral_score = total_engagement / time_factor
        return min(viral_score, 100.0)  # Cap at 100
    
    async def _calculate_content_similarity(self, fingerprint1: str, fingerprint2: str) -> float:
        """Calculate similarity between content fingerprints."""



        return await self.text_fingerprinter.calculate_similarity(fingerprint1, fingerprint2)
    
    def get_crawler_stats(self) -> Dict[str, any]:
        """Get crawler statistics and status."""



        return {
            'platform': 'threads',
            'selenium_enabled': bool(self.driver),
            'monitored_users': len(self.monitored_users),
            'monitored_hashtags': len(self.monitored_hashtags),
            'content_violations': len(self.content_violations),
            'rate_limiter_status': self.rate_limiter.get_status() if self.rate_limiter else None
        }

# Example usage
if __name__ == "__main__":
    import asyncio
    
    async def test_threads_crawler():
        access_token = "YOUR_ACCESS_TOKEN"  # When API is available
        
        async with ThreadsCrawler(access_token, use_selenium=True) as crawler:
            # Search posts
            posts = await crawler.search_posts("AI technology", limit=10)
            print(f"Found {len(posts)} posts")
            
            # Monitor user
            monitoring_config = await crawler.monitor_user("some_username")
            print(f"Monitoring config: {monitoring_config}")
            
            # Detect trending content
            trending = await crawler.detect_trending_content()
            print(f"Found {len(trending)} trending posts")
    
    # asyncio.run(test_threads_crawler())

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


class ThreadsPostType(str, Enum):
    """Threads post types"""
    TEXT = "text"
    PHOTO = "photo"
    VIDEO = "video"
    CAROUSEL = "carousel"
    QUOTE_POST = "quote_post"
    REPOST = "repost"


class ThreadsInteractionType(str, Enum):
    """Threads interaction types"""
    LIKE = "like"
    REPLY = "reply"
    REPOST = "repost"
    QUOTE = "quote"
    SHARE = "share"


class ThreadsContentVisibility(str, Enum):
    """Threads content visibility levels"""
    PUBLIC = "public"
    FOLLOWERS = "followers"
    MENTIONED_ONLY = "mentioned_only"
    HIDDEN = "hidden"


class ThreadsUser(BaseModel):
    """Threads user data model"""
    user_id: str
    username: str
    display_name: str
    bio: Optional[str] = None
    profile_picture_url: Optional[str] = None
    followers_count: int = 0
    following_count: int = 0
    posts_count: int = 0
    is_verified: bool = False
    is_private: bool = False
    is_business: bool = False
    joined_date: datetime
    last_activity: Optional[datetime] = None
    location: Optional[str] = None
    website: Optional[str] = None
    instagram_connected: bool = False
    instagram_username: Optional[str] = None
    external_links: List[str] = Field(default_factory=list)


class ThreadsMedia(BaseModel):
    """Threads media data model"""
    media_id: str
    media_type: str  # "image", "video", "carousel_album"
    url: str
    thumbnail_url: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    duration: Optional[float] = None  # for videos
    alt_text: Optional[str] = None
    is_video: bool = False
    video_duration: Optional[float] = None
    carousel_children: List[Dict[str, Any]] = Field(default_factory=list)


class ThreadsPost(BaseModel):
    """Threads post data model"""
    post_id: str
    user: ThreadsUser
    text: Optional[str] = None
    media: List[ThreadsMedia] = Field(default_factory=list)
    post_type: ThreadsPostType
    created_at: datetime
    visibility: ThreadsContentVisibility = ThreadsContentVisibility.PUBLIC
    like_count: int = 0
    reply_count: int = 0
    repost_count: int = 0
    quote_count: int = 0
    view_count: int = 0
    hashtags: List[str] = Field(default_factory=list)
    mentions: List[str] = Field(default_factory=list)
    urls: List[str] = Field(default_factory=list)
    permalink: str
    is_reply: bool = False
    reply_to_post_id: Optional[str] = None
    reply_to_user: Optional[ThreadsUser] = None
    is_quote_post: bool = False
    quoted_post: Optional['ThreadsPost'] = None
    is_repost: bool = False
    original_post: Optional['ThreadsPost'] = None
    thread_continuation: bool = False
    conversation_id: Optional[str] = None
    edit_history: List[Dict[str, Any]] = Field(default_factory=list)
    is_edited: bool = False
    edited_at: Optional[datetime] = None
    language: Optional[str] = None
    sentiment_score: Optional[float] = None
    similarity_score: Optional[float] = None
    protection_status: str = "unprotected"


class ThreadsConversation(BaseModel):
    """Threads conversation/thread data model"""
    conversation_id: str
    root_post: ThreadsPost
    replies: List[ThreadsPost] = Field(default_factory=list)
    participants: List[ThreadsUser] = Field(default_factory=list)
    total_posts: int = 0
    total_participants: int = 0
    created_at: datetime
    last_activity: datetime
    is_trending: bool = False
    engagement_score: float = 0.0


class ThreadsTrend(BaseModel):
    """Threads trending topic data model"""
    trend_id: str
    hashtag: str
    posts_count: int
    mentions_count: int
    growth_rate: float
    created_at: datetime
    peak_time: Optional[datetime] = None
    related_hashtags: List[str] = Field(default_factory=list)
    top_posts: List[str] = Field(default_factory=list)  # post IDs
    geographic_distribution: Dict[str, int] = Field(default_factory=dict)


class ThreadsSearchResults(BaseModel):
    """Threads search results data model"""
    query: str
    total_results: int
    users: List[ThreadsUser] = Field(default_factory=list)
    posts: List[ThreadsPost] = Field(default_factory=list)
    conversations: List[ThreadsConversation] = Field(default_factory=list)
    hashtags: List[str] = Field(default_factory=list)
    search_type: str
    filters_applied: Dict[str, Any]
    search_timestamp: datetime
    has_more: bool = False
    next_cursor: Optional[str] = None


class ThreadsAnalytics(BaseModel):
    """Threads analytics data model"""
    user_id: str
    analysis_period: Tuple[datetime, datetime]
    total_posts: int
    total_replies: int
    total_reposts: int
    total_likes_received: int
    total_replies_received: int
    total_reposts_received: int
    average_engagement_rate: float
    top_performing_post_id: Optional[str] = None
    most_used_hashtags: List[str]
    conversation_participation: int
    follower_growth: int
    posting_frequency: float
    peak_activity_hours: List[int]
    engagement_by_content_type: Dict[str, float]
    reply_to_post_ratio: float
    original_content_ratio: float
    average_thread_length: float
    sentiment_distribution: Dict[str, int]
    similarity_violations: int
    protection_violations: int


class ThreadsCrawler(BaseCrawler):
    """
    Ultra-Advanced Threads Platform Crawler
    
    Provides comprehensive crawling and monitoring capabilities for Meta Threads platform,
    specializing in text-based conversations, community interactions, and real-time discussions.
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        
        self.base_url = "https://threads.net"
        self.api_base = "https://graph.threads.net/v1.0"
        
        # Authentication
        self.access_token: Optional[str] = None
        self.user_agent: str = config.get('user_agent', 'Mozilla/5.0 (compatible; ThreadsCrawler/1.0)')
        self.user_id: Optional[str] = None
        
        # Rate limiting - Threads API limits
        self.rate_limiter = RateLimiter(
            requests_per_minute=200,
            requests_per_hour=2000,
            burst_limit=50
        )
        
        # Cache management
        self.cache_manager = CacheManager(
            cache_ttl=300,  # 5 minutes for posts
            max_cache_size=5000
        )
        
        # Content protection
        self.content_encryption = ContentEncryption()
        self.content_fingerprinter = ContentFingerprinter()
        
        # Monitoring configuration
        self.monitored_users: Set[str] = set()
        self.monitored_hashtags: Set[str] = set()
        self.protected_content: Set[str] = set()
        self.similarity_threshold = config.get('similarity_threshold', 0.85)
        
        # Threads-specific settings
        self.track_conversations = config.get('track_conversations', True)
        self.monitor_trends = config.get('monitor_trends', True)
        self.analyze_sentiment = config.get('analyze_sentiment', True)
        self.track_instagram_integration = config.get('track_instagram_integration', True)
        
        logger.info("Threads crawler initialized with ultra-advanced text conversation monitoring")

    async def authenticate(self, access_token: str) -> bool:
        """
        Authenticate with Threads API
        
        Args:
            access_token: Access token for Threads API
            
        Returns:
            bool: Authentication success status
        """



        try:
            self.access_token = access_token
            
            self.session.headers.update({
                'Authorization': f'Bearer {access_token}',
                'User-Agent': self.user_agent,
                'Accept': 'application/json'
            })
            
            # Verify authentication
            async with self.session.get(f"{self.api_base}/me") as response:
                if response.status == 200:
                    user_data = await response.json()
                    self.user_id = user_data.get('id', '')
                    logger.info("Threads authentication successful")
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
        post_type: Optional[ThreadsPostType] = None,
        hashtag: Optional[str] = None,
        limit: int = 100
    ) -> ThreadsSearchResults:
        """
        Search Threads content with advanced filtering
        
        Args:
            query: Search query
            post_type: Type of post to search
            hashtag: Hashtag to search
            limit: Maximum results
            
        Returns:
            ThreadsSearchResults: Comprehensive search results
        """
        await self.rate_limiter.acquire()
        
        try:
            results = ThreadsSearchResults(
                query=query,
                total_results=0,
                search_type="comprehensive",
                filters_applied={
                    "post_type": post_type.value if post_type else None,
                    "hashtag": hashtag
                },
                search_timestamp=datetime.utcnow()
            )
            
            # Search users
            users = await self._search_users(query, limit // 4)
            results.users = users
            results.total_results += len(users)
            
            # Search posts
            posts = await self._search_posts(query, post_type, hashtag, limit // 2)
            results.posts = posts
            results.total_results += len(posts)
            
            # Search conversations if enabled
            if self.track_conversations:
                conversations = await self._search_conversations(query, limit // 4)
                results.conversations = conversations
                results.total_results += len(conversations)
            
            # Get related hashtags
            if hashtag or query.startswith('#'):
                hashtags = await self._get_related_hashtags(hashtag or query.lstrip('#'))
                results.hashtags = hashtags
            
            # Process content for protection
            for post in results.posts:
                post.similarity_score = await self._calculate_similarity(post)
                post.protection_status = await self._check_protection_status(post)
                
                # Analyze sentiment if enabled
                if self.analyze_sentiment:
                    post.sentiment_score = await self._analyze_sentiment(post.text or "")
            
            logger.info(f"Threads search completed: {results.total_results} total results")
            return results
            
        except Exception as e:
            logger.error(f"Search error: {str(e)}")
            return ThreadsSearchResults(
                query=query,
                total_results=0,
                search_type="error",
                filters_applied={},
                search_timestamp=datetime.utcnow()
            )

    async def monitor_content(
        self,
        usernames: List[str] = None,
        hashtags: List[str] = None,
        keywords: List[str] = None,
        check_interval: int = 300
    ) -> AsyncGenerator[ThreadsPost, None]:
        """
        Real-time content monitoring for Threads
        
        Args:
            usernames: Users to monitor
            hashtags: Hashtags to monitor
            keywords: Keywords to monitor
            check_interval: Check interval in seconds
            
        Yields:
            ThreadsPost: New posts detected
        """
        usernames = usernames or []
        hashtags = hashtags or []
        keywords = keywords or []
        
        self.monitored_users.update(usernames)
        self.monitored_hashtags.update(hashtags)
        
        logger.info(f"Starting Threads monitoring for {len(usernames)} users, {len(hashtags)} hashtags")
        
        seen_posts = set()
        
        while True:
            try:
                await asyncio.sleep(check_interval)
                
                # Monitor users
                for username in usernames:
                    try:
                        user_posts = await self._get_user_recent_posts(username)
                        
                        for post in user_posts:
                            if post.post_id not in seen_posts:
                                # Enhanced monitoring analysis
                                post.similarity_score = await self._calculate_similarity(post)
                                post.protection_status = await self._check_protection_status(post)
                                
                                if self.analyze_sentiment:
                                    post.sentiment_score = await self._analyze_sentiment(post.text or "")
                                
                                seen_posts.add(post.post_id)
                                
                                logger.info(f"New post from {username}: {post.post_id}")
                                yield post
                    
                    except Exception as e:
                        logger.error(f"Error monitoring user {username}: {str(e)}")
                        continue
                
                # Monitor hashtags
                for hashtag in hashtags:
                    try:
                        hashtag_posts = await self._get_hashtag_recent_posts(hashtag)
                        
                        for post in hashtag_posts:
                            if post.post_id not in seen_posts:
                                post.similarity_score = await self._calculate_similarity(post)
                                post.protection_status = await self._check_protection_status(post)
                                
                                if self.analyze_sentiment:
                                    post.sentiment_score = await self._analyze_sentiment(post.text or "")
                                
                                seen_posts.add(post.post_id)
                                
                                logger.info(f"New post with #{hashtag}: {post.post_id}")
                                yield post
                    
                    except Exception as e:
                        logger.error(f"Error monitoring hashtag #{hashtag}: {str(e)}")
                        continue
                
            except Exception as e:
                logger.error(f"Monitoring error: {str(e)}")
                await asyncio.sleep(60)

    async def detect_similarity(
        self,
        target_post: ThreadsPost,
        comparison_set: List[ThreadsPost],
        threshold: float = None
    ) -> List[Tuple[ThreadsPost, float]]:
        """
        Detect post similarity for content protection
        
        Args:
            target_post: Post to compare
            comparison_set: Posts to compare against
            threshold: Similarity threshold
            
        Returns:
            List[Tuple[ThreadsPost, float]]: Similar posts with scores
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
        user_id: str,
        analysis_period: Tuple[datetime, datetime]
    ) -> ThreadsAnalytics:
        """
        Generate comprehensive analytics for Threads user
        
        Args:
            user_id: User ID to analyze
            analysis_period: Analysis time period
            
        Returns:
            ThreadsAnalytics: Comprehensive analytics data
        """



        try:
            start_time, end_time = analysis_period
            
            # Get user's posts in the period
            user_posts = await self._get_user_posts_in_period(user_id, start_time, end_time)
            
            if not user_posts:
                return ThreadsAnalytics(
                    user_id=user_id,
                    analysis_period=analysis_period,
                    total_posts=0,
                    total_replies=0,
                    total_reposts=0,
                    total_likes_received=0,
                    total_replies_received=0,
                    total_reposts_received=0,
                    average_engagement_rate=0.0,
                    most_used_hashtags=[],
                    conversation_participation=0,
                    follower_growth=0,
                    posting_frequency=0.0,
                    peak_activity_hours=[],
                    engagement_by_content_type={},
                    reply_to_post_ratio=0.0,
                    original_content_ratio=1.0,
                    average_thread_length=1.0,
                    sentiment_distribution={},
                    similarity_violations=0,
                    protection_violations=0
                )
            
            # Calculate basic metrics
            total_posts = len(user_posts)
            total_replies = sum(1 for post in user_posts if post.is_reply)
            total_reposts = sum(1 for post in user_posts if post.is_repost)
            total_likes_received = sum(post.like_count for post in user_posts)
            total_replies_received = sum(post.reply_count for post in user_posts)
            total_reposts_received = sum(post.repost_count for post in user_posts)
            
            # Calculate engagement rate
            total_engagements = total_likes_received + total_replies_received + total_reposts_received
            average_engagement_rate = total_engagements / total_posts if total_posts > 0 else 0.0
            
            # Hashtag analysis
            hashtag_counts = {}
            for post in user_posts:
                for hashtag in post.hashtags:
                    hashtag_counts[hashtag] = hashtag_counts.get(hashtag, 0) + 1
            
            most_used_hashtags = sorted(hashtag_counts.items(), key=lambda x: x[1], reverse=True)[:10]
            most_used_hashtags = [hashtag[0] for hashtag in most_used_hashtags]
            
            # Content type distribution
            engagement_by_content_type = {}
            type_counts = {}
            for post in user_posts:
                post_type = post.post_type.value
                type_counts[post_type] = type_counts.get(post_type, 0) + 1
                
                engagement = post.like_count + post.reply_count + post.repost_count
                if post_type not in engagement_by_content_type:
                    engagement_by_content_type[post_type] = []
                engagement_by_content_type[post_type].append(engagement)
            
            # Average engagement by type
            for post_type, engagements in engagement_by_content_type.items():
                engagement_by_content_type[post_type] = sum(engagements) / len(engagements)
            
            # Activity patterns
            activity_hours = [post.created_at.hour for post in user_posts]
            hour_counts = {}
            for hour in activity_hours:
                hour_counts[hour] = hour_counts.get(hour, 0) + 1
            peak_activity_hours = sorted(hour_counts.items(), key=lambda x: x[1], reverse=True)[:3]
            peak_activity_hours = [hour[0] for hour in peak_activity_hours]
            
            # Content ratios
            reply_to_post_ratio = total_replies / total_posts if total_posts > 0 else 0.0
            original_posts = sum(1 for post in user_posts if not post.is_reply and not post.is_repost)
            original_content_ratio = original_posts / total_posts if total_posts > 0 else 0.0
            
            # Posting frequency (posts per day)
            period_days = (end_time - start_time).days
            posting_frequency = total_posts / period_days if period_days > 0 else 0.0
            
            # Sentiment analysis
            sentiment_distribution = {"positive": 0, "negative": 0, "neutral": 0}
            for post in user_posts:
                if post.sentiment_score is not None:
                    if post.sentiment_score > 0.1:
                        sentiment_distribution["positive"] += 1
                    elif post.sentiment_score < -0.1:
                        sentiment_distribution["negative"] += 1
                    else:
                        sentiment_distribution["neutral"] += 1
            
            # Protection metrics
            similarity_violations = sum(1 for post in user_posts if (post.similarity_score or 0) > self.similarity_threshold)
            protection_violations = sum(1 for post in user_posts if post.protection_status == "violation")
            
            # Top performing post
            top_performing_post = max(user_posts, 
                                    key=lambda p: p.like_count + p.reply_count + p.repost_count,
                                    default=None)
            
            analytics = ThreadsAnalytics(
                user_id=user_id,
                analysis_period=analysis_period,
                total_posts=total_posts,
                total_replies=total_replies,
                total_reposts=total_reposts,
                total_likes_received=total_likes_received,
                total_replies_received=total_replies_received,
                total_reposts_received=total_reposts_received,
                average_engagement_rate=average_engagement_rate,
                top_performing_post_id=top_performing_post.post_id if top_performing_post else None,
                most_used_hashtags=most_used_hashtags,
                conversation_participation=0,  # Would need conversation data
                follower_growth=0,  # Would need historical follower data
                posting_frequency=posting_frequency,
                peak_activity_hours=peak_activity_hours,
                engagement_by_content_type=engagement_by_content_type,
                reply_to_post_ratio=reply_to_post_ratio,
                original_content_ratio=original_content_ratio,
                average_thread_length=1.0,  # Would need thread length calculation
                sentiment_distribution=sentiment_distribution,
                similarity_violations=similarity_violations,
                protection_violations=protection_violations
            )
            
            logger.info(f"Analytics generated for user {user_id}: {total_posts} posts analyzed")
            return analytics
            
        except Exception as e:
            logger.error(f"Analytics generation error: {str(e)}")
            return ThreadsAnalytics(
                user_id=user_id,
                analysis_period=analysis_period,
                total_posts=0,
                total_replies=0,
                total_reposts=0,
                total_likes_received=0,
                total_replies_received=0,
                total_reposts_received=0,
                average_engagement_rate=0.0,
                most_used_hashtags=[],
                conversation_participation=0,
                follower_growth=0,
                posting_frequency=0.0,
                peak_activity_hours=[],
                engagement_by_content_type={},
                reply_to_post_ratio=0.0,
                original_content_ratio=1.0,
                average_thread_length=1.0,
                sentiment_distribution={},
                similarity_violations=0,
                protection_violations=0
            )

    # Helper methods
    
    async def _search_users(self, query: str, limit: int) -> List[ThreadsUser]:
        """Search for Threads users"""



        try:
            params = {
                "q": query,
                "limit": limit,
                "fields": "id,username,name,biography,followers_count,media_count,profile_picture_url"
            }
            
            async with self.session.get(f"{self.api_base}/users/search", params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    users = []
                    
                    for user_data in data.get("data", []):
                        user = await self._parse_user_data(user_data)
                        users.append(user)
                    
                    return users
                else:
                    return []
                    
        except Exception as e:
            logger.error(f"User search error: {str(e)}")
            return []

    async def _search_posts(
        self,
        query: str,
        post_type: Optional[ThreadsPostType],
        hashtag: Optional[str],
        limit: int
    ) -> List[ThreadsPost]:
        """Search for Threads posts"""



        try:
            params = {
                "q": hashtag if hashtag else query,
                "limit": limit,
                "fields": "id,media_type,media_url,permalink,timestamp,caption,like_count,comments_count"
            }
            
            endpoint = f"{self.api_base}/tags/{hashtag.lstrip('#')}/media" if hashtag else f"{self.api_base}/media"
            
            async with self.session.get(endpoint, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    posts = []
                    
                    for post_data in data.get("data", []):
                        post = await self._parse_post_data(post_data)
                        if not post_type or post.post_type == post_type:
                            posts.append(post)
                    
                    return posts
                else:
                    return []
                    
        except Exception as e:
            logger.error(f"Post search error: {str(e)}")
            return []

    async def _search_conversations(self, query: str, limit: int) -> List[ThreadsConversation]:
        """Search for conversations/threads"""
        # Implementation would require conversation API
        return []

    async def _get_related_hashtags(self, hashtag: str) -> List[str]:
        """Get related hashtags"""
        # Implementation would require hashtag suggestion API
        return []

    async def _get_user_recent_posts(self, username: str) -> List[ThreadsPost]:
        """Get recent posts from user"""



        try:
            # First get user ID from username
            user_id = await self._get_user_id_from_username(username)
            if not user_id:
                return []
            
            params = {
                "fields": "id,media_type,media_url,permalink,timestamp,caption,like_count,comments_count",
                "limit": 25
            }
            
            async with self.session.get(f"{self.api_base}/{user_id}/threads", params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    posts = []
                    
                    for post_data in data.get("data", []):
                        post = await self._parse_post_data(post_data)
                        posts.append(post)
                    
                    return posts
                else:
                    return []
                    
        except Exception as e:
            logger.error(f"Error getting user posts: {str(e)}")
            return []

    async def _get_hashtag_recent_posts(self, hashtag: str) -> List[ThreadsPost]:
        """Get recent posts with hashtag"""



        try:
            params = {
                "fields": "id,media_type,media_url,permalink,timestamp,caption,like_count,comments_count",
                "limit": 25
            }
            
            async with self.session.get(f"{self.api_base}/tags/{hashtag.lstrip('#')}/media", params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    posts = []
                    
                    for post_data in data.get("data", []):
                        post = await self._parse_post_data(post_data)
                        posts.append(post)
                    
                    return posts
                else:
                    return []
                    
        except Exception as e:
            logger.error(f"Error getting hashtag posts: {str(e)}")
            return []

    async def _get_user_id_from_username(self, username: str) -> Optional[str]:
        """Get user ID from username"""



        try:
            params = {
                "q": username,
                "limit": 1,
                "fields": "id,username"
            }
            
            async with self.session.get(f"{self.api_base}/users/search", params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    users = data.get("data", [])
                    for user in users:
                        if user.get("username", "").lower() == username.lower():
                            return user.get("id")
                    return None
                else:
                    return None
                    
        except Exception as e:
            logger.error(f"Error getting user ID: {str(e)}")
            return None

    async def _parse_user_data(self, data: Dict[str, Any]) -> ThreadsUser:
        """Parse user data from API response"""



        return ThreadsUser(
            user_id=str(data.get("id", "")),
            username=data.get("username", ""),
            display_name=data.get("name", ""),
            bio=data.get("biography", ""),
            profile_picture_url=data.get("profile_picture_url"),
            followers_count=data.get("followers_count", 0),
            posts_count=data.get("media_count", 0),
            is_verified=data.get("is_verified", False),
            is_business=data.get("account_type") == "BUSINESS",
            joined_date=datetime.utcnow(),
            instagram_connected=data.get("instagram_business_account") is not None
        )

    async def _parse_post_data(self, data: Dict[str, Any]) -> ThreadsPost:
        """Parse post data from API response"""
        # Parse media
        media = []
        if data.get("media_url"):
            media_item = ThreadsMedia(
                media_id=str(data.get("id", "")),
                media_type=data.get("media_type", "TEXT"),
                url=data.get("media_url", ""),
                thumbnail_url=data.get("thumbnail_url"),
                width=data.get("width"),
                height=data.get("height"),
                is_video=data.get("media_type") == "VIDEO"
            )
            media.append(media_item)
        
        # Determine post type
        post_type = ThreadsPostType.TEXT
        if data.get("media_type") == "IMAGE":
            post_type = ThreadsPostType.PHOTO
        elif data.get("media_type") == "VIDEO":
            post_type = ThreadsPostType.VIDEO
        elif data.get("media_type") == "CAROUSEL_ALBUM":
            post_type = ThreadsPostType.CAROUSEL
        
        # Extract hashtags and mentions from caption
        caption = data.get("caption", "")
        hashtags = []
        mentions = []
        urls = []
        
        if caption:
            import re
            hashtags = re.findall(r'#(\w+)', caption)
            mentions = re.findall(r'@(\w+)', caption)
            urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', caption)
        
        # Create simplified user object
        user = ThreadsUser(
            user_id="",
            username="",
            display_name="",
            joined_date=datetime.utcnow()
        )
        
        return ThreadsPost(
            post_id=str(data.get("id", "")),
            user=user,
            text=caption,
            media=media,
            post_type=post_type,
            created_at=datetime.fromisoformat(data.get("timestamp", datetime.utcnow().isoformat())),
            like_count=data.get("like_count", 0),
            reply_count=data.get("comments_count", 0),
            hashtags=hashtags,
            mentions=mentions,
            urls=urls,
            permalink=data.get("permalink", "")
        )

    async def _extract_post_features(self, post: ThreadsPost) -> Dict[str, Any]:
        """Extract features for similarity comparison"""
        features = {
            "text": (post.text or "").lower(),
            "user_id": post.user.user_id,
            "post_type": post.post_type.value,
            "media_count": len(post.media),
            "hashtags": set(tag.lower() for tag in post.hashtags),
            "mentions": set(mention.lower() for mention in post.mentions),
            "has_media": len(post.media) > 0,
            "has_urls": len(post.urls) > 0,
            "is_reply": post.is_reply,
            "is_repost": post.is_repost,
            "text_length": len(post.text or ""),
            "sentiment": post.sentiment_score or 0.0
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
            scores.append(text_sim * 0.5)  # 50% weight
            
            # Hashtag similarity
            hashtags1 = features1.get("hashtags", set())
            hashtags2 = features2.get("hashtags", set())
            if hashtags1 and hashtags2:
                hashtag_sim = len(hashtags1.intersection(hashtags2)) / len(hashtags1.union(hashtags2))
                scores.append(hashtag_sim * 0.2)  # 20% weight
            
            # Post type similarity
            type_sim = 1.0 if features1.get("post_type") == features2.get("post_type") else 0.0
            scores.append(type_sim * 0.1)  # 10% weight
            
            # Media presence similarity
            media_sim = 1.0 if features1.get("has_media") == features2.get("has_media") else 0.0
            scores.append(media_sim * 0.1)  # 10% weight
            
            # Mention similarity
            mentions1 = features1.get("mentions", set())
            mentions2 = features2.get("mentions", set())
            if mentions1 and mentions2:
                mention_sim = len(mentions1.intersection(mentions2)) / len(mentions1.union(mentions2))
                scores.append(mention_sim * 0.1)  # 10% weight
            
            return sum(scores) / len(scores) if scores else 0.0
            
        except Exception as e:
            logger.error(f"Feature similarity calculation error: {str(e)}")
            return 0.0

    async def _analyze_sentiment(self, text: str) -> float:
        """Analyze sentiment of text"""



        try:
            # Simplified sentiment analysis
            positive_words = ['good', 'great', 'amazing', 'awesome', 'love', 'happy', 'excellent']
            negative_words = ['bad', 'terrible', 'awful', 'hate', 'sad', 'angry', 'horrible']
            
            text_lower = text.lower()
            positive_count = sum(1 for word in positive_words if word in text_lower)
            negative_count = sum(1 for word in negative_words if word in text_lower)
            
            if positive_count > negative_count:
                return min(positive_count / 10.0, 1.0)
            elif negative_count > positive_count:
                return max(-negative_count / 10.0, -1.0)
            else:
                return 0.0
                
        except Exception as e:
            logger.error(f"Sentiment analysis error: {str(e)}")
            return 0.0

    async def _get_user_posts_in_period(
        self,
        user_id: str,
        start_time: datetime,
        end_time: datetime
    ) -> List[ThreadsPost]:
        """Get user's posts in specific time period"""
        # Implementation would require pagination through posts with date filtering
        return []

    async def _calculate_similarity(self, post: ThreadsPost) -> float:
        """Calculate similarity score against protected content"""
        # Simplified similarity calculation
        return 0.0

    async def _check_protection_status(self, post: ThreadsPost) -> str:
        """Check protection status of post"""
        if post.post_id in self.protected_content:
            return "protected"
        return "unprotected"

    async def close(self):
        """Close crawler and cleanup resources"""



        try:
            await self.cache_manager.close()
            await super().close()
            logger.info("Threads crawler closed successfully")
        except Exception as e:
            logger.error(f"Error closing crawler: {str(e)}")
