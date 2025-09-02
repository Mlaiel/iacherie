"""Reddit Platform Crawler
=======================

Enterprise-grade Reddit content crawler with ultra-advanced monitoring capabilities.
Implements Reddit API integration, intelligent subreddit and post monitoring, and 
real-time community content protection with AI-powered analysis.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

WARNING: This code is protected by copyright law. Any unauthorized copying, 
distribution, or modification is strictly prohibited and will result in 
legal action. Contact mlaiel@live.de for licensing.

Features:
- Reddit API (PRAW) integration with OAuth2 authentication
- Real-time subreddit and post monitoring
- AI-powered content classification and moderation
- Automated spam and violation detection
- Multi-subreddit content discovery and tracking
- Comment thread analysis and sentiment monitoring
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
import praw
from praw.models import Submission, Comment, Subreddit, Redditor
import prawcore
import requests

from ..utils.specialized_rate_limiters import RedditRateLimiter
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
class RedditPost:
    """
Reddit submission/post data structure with enhanced analysis."""
    post_id: str
    title: str
    selftext: Optional[str]
    url: Optional[str]
    created_utc: datetime
    author: Optional[str]
    author_id: Optional[str]
    subreddit: str
    subreddit_id: str
    # Post metrics
    score: int
    upvote_ratio: float
    num_comments: int
    num_crossposts: int
    view_count: Optional[int]
    # Post metadata
    domain: Optional[str]
    link_flair_text: Optional[str]
    author_flair_text: Optional[str]
    is_self: bool
    is_video: bool
    is_original_content: bool
    over_18: bool
    spoiler: bool
    locked: bool
    archived: bool
    removed: bool
    deleted: bool
    # Media content
    media_type: Optional[str] = None
    media_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    preview_images: List[str] = None
    # Advanced analysis
    content_fingerprint: Optional[str] = None
    media_fingerprint: Optional[str] = None
    sentiment_score: Optional[float] = None
    toxicity_score: Optional[float] = None
    engagement_rate: Optional[float] = None
    viral_score: Optional[float] = None
    language: Optional[str] = None
    # Copyright protection
    copyright_matches: List[Dict] = None
    violation_flags: List[str] = None
    protection_status: Optional[str] = None
    # Reddit-specific
    gilded: int = 0
    stickied: bool = False
    distinguished: Optional[str] = None

@dataclass
class RedditComment:
    """
Reddit comment data structure."""
    comment_id: str
    body: str
    created_utc: datetime
    author: Optional[str]
    author_id: Optional[str]
    submission_id: str
    parent_id: str
    subreddit: str
    # Comment metrics
    score: int
    is_submitter: bool
    stickied: bool
    distinguished: Optional[str]
    # Comment hierarchy
    depth: int = 0
    replies: List[str] = None
    # Analysis
    content_fingerprint: Optional[str] = None
    sentiment_score: Optional[float] = None
    toxicity_score: Optional[float] = None
    spam_probability: Optional[float] = None

@dataclass
class RedditSubreddit:
    """
Reddit subreddit data structure."""
    subreddit_id: str
    display_name: str
    display_name_prefixed: str
    title: str
    description: Optional[str]
    public_description: Optional[str]
    created_utc: datetime
    # Subreddit metrics
    subscribers: int
    active_user_count: Optional[int]
    # Subreddit settings
    over18: bool
    subreddit_type: str  # public, restricted, private
    submission_type: str  # any, link, self
    # Moderation
    user_is_banned: Optional[bool] = None
    user_is_moderator: Optional[bool] = None
    user_is_contributor: Optional[bool] = None
    # Analytics
    activity_score: Optional[float] = None
    growth_rate: Optional[float] = None
    engagement_metrics: Optional[Dict] = None
    # Content analysis
    primary_topics: List[str] = None
    content_categories: List[str] = None

@dataclass
class RedditUser:
    """
Reddit user (Redditor) data structure."""
    user_id: str
    name: str
    created_utc: datetime
    # User metrics
    comment_karma: int
    link_karma: int
    total_karma: int
    # User status
    is_employee: bool
    is_mod: bool
    is_gold: bool
    verified: bool
    has_verified_email: bool
    # Analytics
    activity_score: Optional[float] = None
    average_score: Optional[float] = None
    # Behavior analysis
    toxicity_score: Optional[float] = None
    spam_probability: Optional[float] = None
    violation_history: List[Dict] = None

class RedditCrawler:
    """
    Enterprise Reddit content crawler with advanced monitoring capabilities.
    
    Provides comprehensive Reddit content discovery, monitoring, and analysis
    with focus on community management and content protection.
    """
    
    def __init__(self, 
                 client_id: str,
        try:
            logger.info(f"Executing __init__")
            
            # Implementation for __init__
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"__init__ completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"__init__ failed: {e}")
            raise
    async def __aenter__(self):
        """Async context manager entry."""
        await self.initialize()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """
Async context manager exit."""
        await self.close()
        
    async def initialize(self):
        """
Initialize the crawler and Reddit client."""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30)
        )
        
        # Initialize PRAW Reddit client
        try:
            self.reddit = praw.Reddit(
                client_id=self.client_id,
                client_secret=self.client_secret,
                user_agent=self.user_agent,
                username=self.username,
                password=self.password
            )
            
            # Test authentication
            if self.username:
                _ = self.reddit.user.me()
                self.logger.info(f"Authenticated as: {self.username}")
            else:
                self.logger.info("Initialized read-only Reddit client")
                
        except Exception as e:
            self.logger.error(f"Reddit authentication failed: {str(e)}")
            raise AuthenticationError(f"Reddit auth error: {str(e)}")
        
        self.logger.info("Reddit crawler initialized")
        
    async def close(self):
        try:
            logger.info(f"Executing initialize")
            
            # Implementation for initialize
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"initialize completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"initialize failed: {e}")
            raise
            await self.rate_limiter.acquire()
            
            posts = []
            
            if subreddit:
                subreddit_obj = self.reddit.subreddit(subreddit)
                search_results = subreddit_obj.search(
                    query=query,
                    sort=sort,
                    time_filter=time_filter,
                    limit=limit
                )
            else:
                search_results = self.reddit.subreddit("all").search(
                    query=query,
                    sort=sort,
                    time_filter=time_filter,
                    limit=limit
                )
            
            for submission in search_results:
                post_data = await self._parse_submission_data(submission)
                posts.append(post_data)
            
            self.logger.info(f"Found {len(posts)} posts for query: {query}")
            return posts
            
        except prawcore.exceptions.TooManyRequests:
            self.logger.warning("Reddit rate limit hit")
            raise RateLimitError("Reddit API rate limit exceeded")
        except Exception as e:
            self.logger.error(f"Post search failed: {str(e)}")
            raise CrawlerError(f"Post search error: {str(e)}")
    
    async def get_subreddit_posts(self, 
                                 subreddit_name: str,
                                 sort: str = "hot",
                                 time_filter: str = "day",
                                 limit: int = 100) -> List[RedditPost]:
        """
        Get posts from a specific subreddit.
        
        Args:
            subreddit_name: Name of the subreddit
            sort: Sort order (hot, new, top, rising)
            time_filter: Time filter for top posts
            limit: Maximum posts to return
            
        Returns:
            List of subreddit posts
        """
        try:
            await self.rate_limiter.acquire()
            
            subreddit = self.reddit.subreddit(subreddit_name)
            posts = []
            
            if sort == "hot":
                submissions = subreddit.hot(limit=limit)
            elif sort == "new":
                submissions = subreddit.new(limit=limit)
            elif sort == "top":
                submissions = subreddit.top(time_filter=time_filter, limit=limit)
            elif sort == "rising":
                submissions = subreddit.rising(limit=limit)
            else:
                submissions = subreddit.hot(limit=limit)
            
            for submission in submissions:
                post_data = await self._parse_submission_data(submission)
                posts.append(post_data)
            
            self.logger.info(f"Retrieved {len(posts)} posts from r/{subreddit_name}")
            return posts
            
        except prawcore.exceptions.TooManyRequests:
            raise RateLimitError("Reddit API rate limit exceeded")
        except Exception as e:
            self.logger.error(f"Subreddit posts retrieval failed: {str(e)}")
            raise CrawlerError(f"Subreddit posts error: {str(e)}")
    
    async def get_post_comments(self, 
                               post_id: str, 
                               sort: str = "best",
                               limit: int = None) -> List[RedditComment]:
        """
        Get comments from a specific post.
        
        Args:
            post_id: Reddit post ID
            sort: Comment sort order (best, top, new, controversial, old, qa)
            limit: Maximum comments to return (None for all)
            
        Returns:
            List of comments
        """
        try:
            await self.rate_limiter.acquire()
            
            submission = self.reddit.submission(id=post_id)
            submission.comment_sort = sort
            
            if limit:
                submission.comment_limit = limit
            
            submission.comments.replace_more(limit=None)
            
            comments = []
            for comment in submission.comments.list():
                if isinstance(comment, Comment):
                    comment_data = await self._parse_comment_data(comment)
                    comments.append(comment_data)
            
            self.logger.info(f"Retrieved {len(comments)} comments from post {post_id}")
            return comments
            
        except prawcore.exceptions.TooManyRequests:
            raise RateLimitError("Reddit API rate limit exceeded")
        except Exception as e:
            self.logger.error(f"Comments retrieval failed: {str(e)}")
            raise CrawlerError(f"Comments retrieval error: {str(e)}")
    
    async def monitor_subreddit(self, subreddit_name: str) -> Dict:
        """
        Start monitoring a specific subreddit.
        
        Args:
            subreddit_name: Name of the subreddit to monitor
            
        Returns:
            Monitoring configuration
        """
        try:
            subreddit = self.reddit.subreddit(subreddit_name)
            
            # Verify subreddit exists and is accessible
            _ = subreddit.id
            
            self.monitored_subreddits.add(subreddit_name)
            
            # Get initial subreddit analysis
            subreddit_data = await self._analyze_subreddit(subreddit)
            
            monitoring_config = {
                'subreddit_name': subreddit_name,
                'monitoring_started': datetime.utcnow(),
                'initial_analysis': asdict(subreddit_data)
            }
            
            self.logger.info(f"Started monitoring subreddit: r/{subreddit_name}")
            return monitoring_config
            
        except Exception as e:
            self.logger.error(f"Failed to start subreddit monitoring: {str(e)}")
            raise CrawlerError(f"Subreddit monitoring error: {str(e)}")
    
    async def detect_content_violations(self, 
                                       protected_content: List[str],
                                       similarity_threshold: float = 0.8) -> List[Dict]:
        """
        Detect potential content violations across monitored subreddits.
        
        Args:
            protected_content: List of protected content fingerprints
            similarity_threshold: Minimum similarity for violation
            
        Returns:
            List of potential violations
        """
        try:
            violations = []
            
            for subreddit_name in self.monitored_subreddits:
                # Get recent posts
                recent_posts = await self.get_subreddit_posts(
                    subreddit_name,
                    sort="new",
                    limit=100
                )
                
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
                                'subreddit': post.subreddit,
                                'author': post.author,
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
    
    async def get_trending_posts(self, 
                                subreddits: List[str] = None,
                                time_filter: str = "day",
                                min_score: int = 100) -> List[RedditPost]:
        """
        Get trending posts across specified subreddits.
        
        Args:
            subreddits: List of subreddit names (default: popular)
            time_filter: Time filter for trending content
            min_score: Minimum score threshold
            
        Returns:
            List of trending posts
        """
        try:
            trending_posts = []
            
            if not subreddits:
                subreddits = ["popular", "all"]
            
            for subreddit_name in subreddits:
                posts = await self.get_subreddit_posts(
                    subreddit_name,
                    sort="top",
                    time_filter=time_filter,
                    limit=50
                )
                
                # Filter by score and calculate viral metrics
                for post in posts:
                    if post.score >= min_score:
                        post.viral_score = self._calculate_viral_score(post)
                        trending_posts.append(post)
            
            # Sort by viral score
            trending_posts.sort(key=lambda x: x.viral_score or 0, reverse=True)
            
            self.logger.info(f"Found {len(trending_posts)} trending posts")
            return trending_posts[:100]  # Return top 100
            
        except Exception as e:
            self.logger.error(f"Trending posts detection failed: {str(e)}")
            raise CrawlerError(f"Trending posts error: {str(e)}")
    
    async def _parse_submission_data(self, submission) -> RedditPost:
        """Parse Reddit submission into structured data."""
        # Generate content fingerprint
        content_text = f"{submission.title} {submission.selftext or ''}"
        content_fingerprint = await self.text_fingerprinter.generate_fingerprint(content_text)
        
        return RedditPost(
            post_id=submission.id,
            title=submission.title,
            selftext=submission.selftext,
            url=submission.url,
            created_utc=datetime.fromtimestamp(submission.created_utc),
            author=submission.author.name if submission.author else None,
            author_id=submission.author.id if submission.author else None,
            subreddit=submission.subreddit.display_name,
            subreddit_id=submission.subreddit.id,
            score=submission.score,
            upvote_ratio=submission.upvote_ratio,
            num_comments=submission.num_comments,
            num_crossposts=submission.num_crossposts,
            domain=submission.domain,
            link_flair_text=submission.link_flair_text,
            author_flair_text=submission.author_flair_text,
            is_self=submission.is_self,
            is_video=submission.is_video,
            is_original_content=submission.is_original_content,
            over_18=submission.over_18,
            spoiler=submission.spoiler,
            locked=submission.locked,
            archived=submission.archived,
            removed=submission.removed,
            gilded=submission.gilded,
            stickied=submission.stickied,
            distinguished=submission.distinguished,
            content_fingerprint=content_fingerprint
        )
    
    async def _parse_comment_data(self, comment) -> RedditComment:
        """Parse Reddit comment into structured data."""
        content_fingerprint = await self.text_fingerprinter.generate_fingerprint(comment.body)
        
        return RedditComment(
            comment_id=comment.id,
            body=comment.body,
            created_utc=datetime.fromtimestamp(comment.created_utc),
            author=comment.author.name if comment.author else None,
            author_id=comment.author.id if comment.author else None,
            submission_id=comment.submission.id,
            parent_id=comment.parent_id,
            subreddit=comment.subreddit.display_name,
            score=comment.score,
            is_submitter=comment.is_submitter,
            stickied=comment.stickied,
            distinguished=comment.distinguished,
            content_fingerprint=content_fingerprint
        )
    
    async def _analyze_subreddit(self, subreddit) -> RedditSubreddit:
        """
Perform comprehensive subreddit analysis."""
        return RedditSubreddit(
            subreddit_id=subreddit.id,
            display_name=subreddit.display_name,
            display_name_prefixed=subreddit.display_name_prefixed,
            title=subreddit.title,
            description=subreddit.description,
            public_description=subreddit.public_description,
            created_utc=datetime.fromtimestamp(subreddit.created_utc),
            subscribers=subreddit.subscribers,
            active_user_count=subreddit.active_user_count,
            over18=subreddit.over18,
            subreddit_type=subreddit.subreddit_type,
            submission_type=subreddit.submission_type
        )
    
    def _calculate_viral_score(self, post: RedditPost) -> float:
        """
Calculate viral score for a post."""
        # Viral score based on Reddit-specific metrics
        age_hours = (datetime.utcnow() - post.created_utc).total_seconds() / 3600
        age_factor = max(1, age_hours)
        
        # Weight different engagement types
        engagement_score = (
            post.score * 1.0 +
            post.num_comments * 2.0 +
            post.num_crossposts * 3.0 +
            post.gilded * 10.0
        )
        
        viral_score = engagement_score / age_factor
        return min(viral_score, 100.0)  # Cap at 100
    
    async def _calculate_content_similarity(self, fingerprint1: str, fingerprint2: str) -> float:
        """
Calculate similarity between content fingerprints."""
        return await self.text_fingerprinter.calculate_similarity(fingerprint1, fingerprint2)
    
    def get_crawler_stats(self) -> Dict[str, any]:
        """
Get crawler statistics and status."""
        return {
            'platform': 'reddit',
            'authenticated': bool(self.username),
            'monitored_subreddits': len(self.monitored_subreddits),
            'monitored_users': len(self.monitored_users),
            'monitored_keywords': len(self.monitored_keywords),
            'content_violations': len(self.content_violations),
            'rate_limiter_status': self.rate_limiter.get_status() if self.rate_limiter else None
        }

# Example usage
if __name__ == "__main__":
    import asyncio
    
    async def test_reddit_crawler():
        client_id = "YOUR_CLIENT_ID"
        client_secret = "YOUR_CLIENT_SECRET"
        user_agent = "Reddit Crawler v1.0"
        
        async with RedditCrawler(client_id, client_secret, user_agent) as crawler:
            # Search posts
            posts = await crawler.search_posts("artificial intelligence", limit=10)
            print(f"Found {len(posts)} posts")
            
            # Monitor subreddit
            monitoring_config = await crawler.monitor_subreddit("MachineLearning")
            print(f"Monitoring config: {monitoring_config}")
            
            # Get trending posts
            trending = await crawler.get_trending_posts(["technology", "programming"])
            print(f"Found {len(trending)} trending posts")
    
    # asyncio.run(test_reddit_crawler())

import asyncio
import json
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Any
from urllib.parse import urljoin, urlparse

import aiohttp
import pandas as pd
from pydantic import BaseModel, Field

from ..base_crawler import BaseCrawler
from ....core.config import get_settings
from ....core.logging import get_logger
from ....models.content import ContentMatch, PlatformContent
from ....utils.rate_limiter import RateLimiter
from ....security.encryption import encrypt_sensitive_data

logger = get_logger(__name__)
settings = get_settings()


class RedditPost(BaseModel):
    """Reddit Post data model"""
    post_id: str
    title: str
    content: str
    author: str
    subreddit: str
    url: str
    permalink: str
    created_utc: datetime
    score: int = 0
    upvote_ratio: float = 0.0
    num_comments: int = 0
    gilded: int = 0
    is_self: bool = True
    is_nsfw: bool = False
    is_spoiler: bool = False
    is_stickied: bool = False
    is_locked: bool = False
    post_hint: Optional[str] = None
    thumbnail: Optional[str] = None
    flair_text: Optional[str] = None
    awards: List[Dict] = Field(default_factory=list)
    media_metadata: Dict[str, Any] = Field(default_factory=dict)
    crosspost_parent: Optional[str] = None


class RedditComment(BaseModel):
    """
Reddit Comment data model"""
    comment_id: str
    body: str
    author: str
    post_id: str
    parent_id: Optional[str] = None
    subreddit: str
    created_utc: datetime
    score: int = 0
    gilded: int = 0
    is_submitter: bool = False
    is_mod: bool = False
    is_admin: bool = False
    depth: int = 0
    awards: List[Dict] = Field(default_factory=list)
    edited: bool = False


class RedditSubreddit(BaseModel):
    """
Reddit Subreddit data model"""
    subreddit_name: str
    display_name: str
    title: str
    description: str
    subscribers: int = 0
    active_users: int = 0
    created_utc: datetime
    is_nsfw: bool = False
    subreddit_type: str = "public"
    submission_type: str = "any"
    icon_url: Optional[str] = None
    banner_url: Optional[str] = None
    primary_color: Optional[str] = None
    rules: List[Dict] = Field(default_factory=list)
    moderators: List[str] = Field(default_factory=list)


class RedditUser(BaseModel):
    """Reddit User data model"""
    username: str
    created_utc: datetime
    comment_karma: int = 0
    link_karma: int = 0
    total_karma: int = 0
    is_verified: bool = False
    is_mod: bool = False
    is_admin: bool = False
    is_premium: bool = False
    has_verified_email: bool = False
    icon_img: Optional[str] = None
    profile_over_18: bool = False
    subreddit_count: int = 0


class RedditCrawler(BaseCrawler):
    """
    Advanced Reddit crawler for comprehensive content monitoring and community analysis
    
    Features:
    - Post and comment monitoring across subreddits
    - User profile analysis and behavior tracking
    - Subreddit analytics and trend detection
    - Content sentiment analysis and engagement metrics
    - Copyright infringement detection in posts/comments
    - Viral content identification and tracking
    - Community sentiment and discussion analysis
    - Real-time monitoring with Reddit API
    """
    
    def __init__(self):
        super().__init__()
        self.platform = "reddit"
        self.base_url = "https://www.reddit.com"
        self.api_base = "https://oauth.reddit.com"
        self.rate_limiter = RateLimiter(
            requests_per_minute=60,  # Reddit API rate limit
            requests_per_hour=3600
        )
        self.session_headers = {
            'User-Agent': 'IA-Influencer-Agent/2.0 (Content Protection)',
            'Accept': 'application/json'
        }
        self.access_token = None
        
    async def authenticate(self, client_id: str, client_secret: str, username: str = None, password: str = None) -> bool:
        """Authenticate with Reddit API using OAuth2"""
        try:
            # Reddit OAuth2 authentication
            auth_url = "https://www.reddit.com/api/v1/access_token"
            
            auth_data = {
                'grant_type': 'client_credentials'
            }
            
            # If username/password provided, use password grant
            if username and password:
                auth_data.update({
                    'grant_type': 'password',
                    'username': username,
                    'password': password
                })
            
            auth_headers = {
                'User-Agent': self.session_headers['User-Agent']
            }
            
            auth = aiohttp.BasicAuth(client_id, client_secret)
            
            async with aiohttp.ClientSession() as session:
                async with session.post(auth_url, data=auth_data, headers=auth_headers, auth=auth) as response:
                    if response.status == 200:
                        data = await response.json()
                        self.access_token = data.get('access_token')
                        
                        if self.access_token:
                            self.session_headers['Authorization'] = f'Bearer {self.access_token}'
                            logger.info("Successfully authenticated with Reddit API")
                            return True
                        else:
                            logger.error("No access token received from Reddit")
                            return False
                    else:
                        logger.error(f"Reddit authentication failed: {response.status}")
                        return False
                        
        except Exception as e:
            logger.error(f"Reddit authentication error: {str(e)}")
            return False
    
    async def search_posts(
        self,
        query: str,
        subreddit: str = None,
        sort: str = "relevance",
        time_filter: str = "all",
        limit: int = 100
    ) -> List[Dict]:
        """
        Search Reddit posts
        
        Args:
            query: Search query
            subreddit: Specific subreddit to search (None for all)
            sort: Sort method (relevance, hot, top, new, comments)
            time_filter: Time filter (hour, day, week, month, year, all)
            limit: Maximum results to return
            
        Returns:
            List of matching posts
        """
        await self.rate_limiter.wait()
        
        try:
            if subreddit:
                endpoint = f"{self.api_base}/r/{subreddit}/search"
            else:
                endpoint = f"{self.api_base}/search"
            
            search_params = {
                'q': query,
                'sort': sort,
                't': time_filter,
                'limit': min(limit, 100),  # Reddit API limit
                'restrict_sr': 'true' if subreddit else 'false',
                'raw_json': '1'
            }
            
            async with aiohttp.ClientSession(headers=self.session_headers) as session:
                async with session.get(endpoint, params=search_params) as response:
                    if response.status == 200:
                        data = await response.json()
                        posts = data.get('data', {}).get('children', [])
                        
                        logger.info(f"Found {len(posts)} posts for query: {query}")
                        return [post.get('data', {}) for post in posts]
                    else:
                        logger.error(f"Reddit post search failed: {response.status}")
                        return []
                        
        except Exception as e:
            logger.error(f"Reddit post search error: {str(e)}")
            return []
    
    async def get_subreddit_posts(
        self,
        subreddit: str,
        sort: str = "hot",
        time_filter: str = "day",
        limit: int = 100
    ) -> List[RedditPost]:
        """Get posts from a specific subreddit"""
        await self.rate_limiter.wait()
        
        try:
            endpoint = f"{self.api_base}/r/{subreddit}/{sort}"
            params = {
                'limit': min(limit, 100),
                't': time_filter,
                'raw_json': '1'
            }
            
            async with aiohttp.ClientSession(headers=self.session_headers) as session:
                async with session.get(endpoint, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        posts_data = data.get('data', {}).get('children', [])
                        
                        posts = []
                        for post_data in posts_data:
                            post = await self._parse_post_data(post_data.get('data', {}))
                            if post:
                                posts.append(post)
                        
                        logger.info(f"Retrieved {len(posts)} posts from r/{subreddit}")
                        return posts
                    else:
                        logger.error(f"Failed to get subreddit posts: {response.status}")
                        return []
                        
        except Exception as e:
            logger.error(f"Error getting subreddit posts: {str(e)}")
            return []
    
    async def get_post_details(self, post_id: str, subreddit: str) -> Optional[RedditPost]:
        """Get detailed information about a specific post"""
        await self.rate_limiter.wait()
        
        try:
            endpoint = f"{self.api_base}/r/{subreddit}/comments/{post_id}"
            params = {'raw_json': '1'}
            
            async with aiohttp.ClientSession(headers=self.session_headers) as session:
                async with session.get(endpoint, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Reddit returns an array, first element is the post
                        if data and len(data) > 0:
                            post_data = data[0].get('data', {}).get('children', [])
                            if post_data:
                                return await self._parse_post_data(post_data[0].get('data', {}))
                        
                        return None
                    else:
                        logger.error(f"Failed to get post details: {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"Error getting post details: {str(e)}")
            return None
    
    async def get_post_comments(self, post_id: str, subreddit: str, limit: int = 100) -> List[RedditComment]:
        """Get comments from a specific post"""
        await self.rate_limiter.wait()
        
        try:
            endpoint = f"{self.api_base}/r/{subreddit}/comments/{post_id}"
            params = {
                'limit': min(limit, 500),
                'raw_json': '1'
            }
            
            async with aiohttp.ClientSession(headers=self.session_headers) as session:
                async with session.get(endpoint, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Reddit returns an array, second element contains comments
                        if data and len(data) > 1:
                            comments_data = data[1].get('data', {}).get('children', [])
                            
                            comments = []
                            for comment_data in comments_data:
                                comment = await self._parse_comment_data(comment_data.get('data', {}), post_id)
                                if comment:
                                    comments.append(comment)
                            
                            logger.info(f"Retrieved {len(comments)} comments from post {post_id}")
                            return comments
                        
                        return []
                    else:
                        logger.error(f"Failed to get post comments: {response.status}")
                        return []
                        
        except Exception as e:
            logger.error(f"Error getting post comments: {str(e)}")
            return []
    
    async def get_subreddit_info(self, subreddit: str) -> Optional[RedditSubreddit]:
        """Get detailed information about a subreddit"""
        await self.rate_limiter.wait()
        
        try:
            endpoint = f"{self.api_base}/r/{subreddit}/about"
            params = {'raw_json': '1'}
            
            async with aiohttp.ClientSession(headers=self.session_headers) as session:
                async with session.get(endpoint, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        subreddit_data = data.get('data', {})
                        
                        return await self._parse_subreddit_data(subreddit_data)
                    else:
                        logger.error(f"Failed to get subreddit info: {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"Error getting subreddit info: {str(e)}")
            return None
    
    async def get_user_profile(self, username: str) -> Optional[RedditUser]:
        """Get detailed user profile information"""
        await self.rate_limiter.wait()
        
        try:
            endpoint = f"{self.api_base}/user/{username}/about"
            params = {'raw_json': '1'}
            
            async with aiohttp.ClientSession(headers=self.session_headers) as session:
                async with session.get(endpoint, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        user_data = data.get('data', {})
                        
                        return await self._parse_user_data(user_data)
                    else:
                        logger.error(f"Failed to get user profile: {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"Error getting user profile: {str(e)}")
            return None
    
    async def get_trending_subreddits(self, limit: int = 50) -> List[Dict]:
        """Get trending/popular subreddits"""
        await self.rate_limiter.wait()
        
        try:
            endpoint = f"{self.api_base}/subreddits/popular"
            params = {
                'limit': min(limit, 100),
                'raw_json': '1'
            }
            
            async with aiohttp.ClientSession(headers=self.session_headers) as session:
                async with session.get(endpoint, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        subreddits = data.get('data', {}).get('children', [])
                        
                        trending_data = []
                        for subreddit_data in subreddits:
                            subreddit_info = subreddit_data.get('data', {})
                            trending_data.append({
                                'name': subreddit_info.get('display_name', ''),
                                'title': subreddit_info.get('title', ''),
                                'subscribers': subreddit_info.get('subscribers', 0),
                                'description': subreddit_info.get('public_description', ''),
                                'created_utc': subreddit_info.get('created_utc', 0)
                            })
                        
                        logger.info(f"Retrieved {len(trending_data)} trending subreddits")
                        return trending_data
                    else:
                        logger.error(f"Failed to get trending subreddits: {response.status}")
                        return []
                        
        except Exception as e:
            logger.error(f"Error getting trending subreddits: {str(e)}")
            return []
    
    async def monitor_content_infringement(
        self,
        protected_content: Dict,
        subreddits: List[str] = None,
        similarity_threshold: float = 0.8
    ) -> List[ContentMatch]:
        """
        Monitor Reddit for potential copyright infringement
        
        Args:
            protected_content: Content to protect
            subreddits: Specific subreddits to monitor (None for all)
            similarity_threshold: Minimum similarity for match detection
            
        Returns:
            List of potential copyright matches
        """
        matches = []
        
        try:
            # Generate search queries from protected content
            search_queries = self._generate_search_queries(protected_content)
            
            # If specific subreddits provided, search them; otherwise search globally
            search_targets = subreddits if subreddits else [None]
            
            for target in search_targets:
                for query in search_queries:
                    results = await self.search_posts(query, target, limit=50)
                    
                    for result in results:
                        post = await self._parse_post_data(result)
                        if post:
                            similarity_score = await self._calculate_content_similarity(
                                protected_content, post
                            )
                            
                            if similarity_score >= similarity_threshold:
                                match = ContentMatch(
                                    platform="reddit",
                                    content_id=post.post_id,
                                    url=f"https://reddit.com{post.permalink}",
                                    title=post.title,
                                    description=post.content[:200] + "..." if len(post.content) > 200 else post.content,
                                    creator=post.author,
                                    similarity_score=similarity_score,
                                    detection_date=datetime.utcnow(),
                                    content_type="post",
                                    metadata={
                                        'subreddit': post.subreddit,
                                        'score': post.score,
                                        'num_comments': post.num_comments,
                                        'upvote_ratio': post.upvote_ratio,
                                        'is_nsfw': post.is_nsfw,
                                        'created_utc': post.created_utc.isoformat()
                                    }
                                )
                                matches.append(match)
            
            logger.info(f"Found {len(matches)} potential copyright matches on Reddit")
            return matches
            
        except Exception as e:
            logger.error(f"Error monitoring Reddit content infringement: {str(e)}")
            return []
    
    async def analyze_post_performance(self, post_id: str, subreddit: str) -> Dict[str, Any]:
        """
        Analyze post performance metrics and engagement
        
        Args:
            post_id: Reddit post ID
            subreddit: Subreddit name
            
        Returns:
            Comprehensive performance analysis
        """
        try:
            post = await self.get_post_details(post_id, subreddit)
            if not post:
                return {}
            
            comments = await self.get_post_comments(post_id, subreddit, limit=100)
            
            # Calculate engagement metrics
            comment_score_avg = sum(c.score for c in comments) / len(comments) if comments else 0
            gilding_total = post.gilded + sum(c.gilded for c in comments)
            
            # Calculate post age and velocity
            post_age_hours = (datetime.utcnow() - post.created_utc).total_seconds() / 3600
            score_velocity = post.score / max(post_age_hours, 1)
            comment_velocity = post.num_comments / max(post_age_hours, 1)
            
            performance_analysis = {
                'post_id': post.post_id,
                'basic_metrics': {
                    'score': post.score,
                    'upvote_ratio': post.upvote_ratio,
                    'num_comments': post.num_comments,
                    'gilded': post.gilded,
                    'awards_count': len(post.awards)
                },
                'engagement_metrics': {
                    'score_velocity': score_velocity,
                    'comment_velocity': comment_velocity,
                    'comment_score_avg': comment_score_avg,
                    'engagement_rate': (post.num_comments + post.gilded) / max(post.score, 1),
                    'virality_score': self._calculate_virality_score(post)
                },
                'content_analysis': {
                    'title_length': len(post.title),
                    'content_length': len(post.content),
                    'has_media': post.post_hint is not None,
                    'is_self_post': post.is_self,
                    'flair_text': post.flair_text
                },
                'temporal_analysis': {
                    'post_age_hours': post_age_hours,
                    'created_utc': post.created_utc.isoformat(),
                    'peak_activity_prediction': await self._predict_peak_activity(post)
                },
                'community_response': {
                    'total_gilding': gilding_total,
                    'comment_sentiment': await self._analyze_comment_sentiment(comments),
                    'discussion_quality': self._assess_discussion_quality(comments)
                },
                'performance_category': self._categorize_performance(post)
            }
            
            return performance_analysis
            
        except Exception as e:
            logger.error(f"Error analyzing post performance: {str(e)}")
            return {}
    
    async def analyze_subreddit_trends(
        self,
        subreddit: str,
        time_period: str = "week",
        limit: int = 100
    ) -> Dict[str, Any]:
        """
        Analyze trends within a specific subreddit
        
        Args:
            subreddit: Subreddit to analyze
            time_period: Time period for analysis
            limit: Maximum posts to analyze
            
        Returns:
            Comprehensive trend analysis
        """
        try:
            # Get recent posts from the subreddit
            hot_posts = await self.get_subreddit_posts(subreddit, "hot", time_period, limit//2)
            top_posts = await self.get_subreddit_posts(subreddit, "top", time_period, limit//2)
            
            all_posts = hot_posts + top_posts
            
            # Analyze trends
            trends_analysis = {
                'subreddit': subreddit,
                'analysis_period': time_period,
                'total_posts_analyzed': len(all_posts),
                'content_trends': {
                    'avg_score': sum(p.score for p in all_posts) / len(all_posts) if all_posts else 0,
                    'avg_comments': sum(p.num_comments for p in all_posts) / len(all_posts) if all_posts else 0,
                    'avg_upvote_ratio': sum(p.upvote_ratio for p in all_posts) / len(all_posts) if all_posts else 0,
                    'media_posts_percentage': len([p for p in all_posts if p.post_hint]) / len(all_posts) * 100 if all_posts else 0
                },
                'temporal_patterns': await self._analyze_posting_patterns(all_posts),
                'popular_flairs': await self._analyze_popular_flairs(all_posts),
                'top_performing_content': [
                    {
                        'title': p.title[:100],
                        'score': p.score,
                        'comments': p.num_comments,
                        'author': p.author
                    }
                    for p in sorted(all_posts, key=lambda x: x.score, reverse=True)[:10]
                ],
                'engagement_distribution': await self._analyze_engagement_distribution(all_posts),
                'content_type_analysis': await self._analyze_content_types(all_posts),
                'user_activity': await self._analyze_user_activity(all_posts)
            }
            
            return trends_analysis
            
        except Exception as e:
            logger.error(f"Error analyzing subreddit trends: {str(e)}")
            return {}
    
    async def get_viral_content(
        self,
        subreddits: List[str] = None,
        min_score: int = 1000,
        time_filter: str = "day"
    ) -> List[Dict]:
        """
        Identify viral content across Reddit
        
        Args:
            subreddits: Specific subreddits to check (None for popular)
            min_score: Minimum score threshold for viral content
            time_filter: Time period to check
            
        Returns:
            List of viral content items
        """
        viral_content = []
        
        try:
            if subreddits is None:
                # Get from r/all or popular
                endpoint = f"{self.api_base}/r/all/hot"
                params = {
                    'limit': 100,
                    't': time_filter,
                    'raw_json': '1'
                }
                
                async with aiohttp.ClientSession(headers=self.session_headers) as session:
                    async with session.get(endpoint, params=params) as response:
                        if response.status == 200:
                            data = await response.json()
                            posts = data.get('data', {}).get('children', [])
                            
                            for post_data in posts:
                                post_info = post_data.get('data', {})
                                if post_info.get('score', 0) >= min_score:
                                    viral_item = {
                                        'post_id': post_info.get('id'),
                                        'title': post_info.get('title'),
                                        'subreddit': post_info.get('subreddit'),
                                        'author': post_info.get('author'),
                                        'score': post_info.get('score'),
                                        'num_comments': post_info.get('num_comments'),
                                        'upvote_ratio': post_info.get('upvote_ratio'),
                                        'created_utc': post_info.get('created_utc'),
                                        'url': f"https://reddit.com{post_info.get('permalink', '')}",
                                        'virality_score': self._calculate_virality_score_from_data(post_info)
                                    }
                                    viral_content.append(viral_item)
            else:
                # Check specific subreddits
                for subreddit in subreddits:
                    posts = await self.get_subreddit_posts(subreddit, "hot", time_filter, 50)
                    
                    for post in posts:
                        if post.score >= min_score:
                            viral_item = {
                                'post_id': post.post_id,
                                'title': post.title,
                                'subreddit': post.subreddit,
                                'author': post.author,
                                'score': post.score,
                                'num_comments': post.num_comments,
                                'upvote_ratio': post.upvote_ratio,
                                'created_utc': post.created_utc.timestamp(),
                                'url': f"https://reddit.com{post.permalink}",
                                'virality_score': self._calculate_virality_score(post)
                            }
                            viral_content.append(viral_item)
            
            # Sort by virality score
            viral_content.sort(key=lambda x: x['virality_score'], reverse=True)
            
            logger.info(f"Found {len(viral_content)} viral content items")
            return viral_content[:50]  # Return top 50
            
        except Exception as e:
            logger.error(f"Error getting viral content: {str(e)}")
            return []
    
    async def _parse_post_data(self, post_data: Dict) -> Optional[RedditPost]:
        """Parse Reddit API post data into RedditPost model"""
        try:
            if not post_data or post_data.get('kind') == 'more':
                return None
            
            post = RedditPost(
                post_id=post_data.get('id', ''),
                title=post_data.get('title', ''),
                content=post_data.get('selftext', ''),
                author=post_data.get('author', '[deleted]'),
                subreddit=post_data.get('subreddit', ''),
                url=post_data.get('url', ''),
                permalink=post_data.get('permalink', ''),
                created_utc=datetime.fromtimestamp(post_data.get('created_utc', 0)),
                score=post_data.get('score', 0),
                upvote_ratio=post_data.get('upvote_ratio', 0.0),
                num_comments=post_data.get('num_comments', 0),
                gilded=post_data.get('gilded', 0),
                is_self=post_data.get('is_self', True),
                is_nsfw=post_data.get('over_18', False),
                is_spoiler=post_data.get('spoiler', False),
                is_stickied=post_data.get('stickied', False),
                is_locked=post_data.get('locked', False),
                post_hint=post_data.get('post_hint'),
                thumbnail=post_data.get('thumbnail') if post_data.get('thumbnail') not in ['self', 'default', 'nsfw'] else None,
                flair_text=post_data.get('link_flair_text'),
                awards=post_data.get('all_awardings', []),
                media_metadata=post_data.get('media_metadata', {}),
                crosspost_parent=post_data.get('crosspost_parent_list', [{}])[0].get('id') if post_data.get('crosspost_parent_list') else None
            )
            
            return post
            
        except Exception as e:
            logger.error(f"Error parsing post data: {str(e)}")
            return None
    
    async def _parse_comment_data(self, comment_data: Dict, post_id: str) -> Optional[RedditComment]:
        """Parse Reddit API comment data into RedditComment model"""
        try:
            if not comment_data or comment_data.get('kind') == 'more':
                return None
            
            comment = RedditComment(
                comment_id=comment_data.get('id', ''),
                body=comment_data.get('body', ''),
                author=comment_data.get('author', '[deleted]'),
                post_id=post_id,
                parent_id=comment_data.get('parent_id'),
                subreddit=comment_data.get('subreddit', ''),
                created_utc=datetime.fromtimestamp(comment_data.get('created_utc', 0)),
                score=comment_data.get('score', 0),
                gilded=comment_data.get('gilded', 0),
                is_submitter=comment_data.get('is_submitter', False),
                is_mod=comment_data.get('distinguished') == 'moderator',
                is_admin=comment_data.get('distinguished') == 'admin',
                depth=comment_data.get('depth', 0),
                awards=comment_data.get('all_awardings', []),
                edited=comment_data.get('edited', False) != False
            )
            
            return comment
            
        except Exception as e:
            logger.error(f"Error parsing comment data: {str(e)}")
            return None
    
    async def _parse_subreddit_data(self, subreddit_data: Dict) -> Optional[RedditSubreddit]:
        """Parse Reddit API subreddit data into RedditSubreddit model"""
        try:
            subreddit = RedditSubreddit(
                subreddit_name=subreddit_data.get('name', ''),
                display_name=subreddit_data.get('display_name', ''),
                title=subreddit_data.get('title', ''),
                description=subreddit_data.get('description', ''),
                subscribers=subreddit_data.get('subscribers', 0),
                active_users=subreddit_data.get('active_user_count', 0),
                created_utc=datetime.fromtimestamp(subreddit_data.get('created_utc', 0)),
                is_nsfw=subreddit_data.get('over18', False),
                subreddit_type=subreddit_data.get('subreddit_type', 'public'),
                submission_type=subreddit_data.get('submission_type', 'any'),
                icon_url=subreddit_data.get('icon_img'),
                banner_url=subreddit_data.get('banner_background_image'),
                primary_color=subreddit_data.get('primary_color')
            )
            
            return subreddit
            
        except Exception as e:
            logger.error(f"Error parsing subreddit data: {str(e)}")
            return None
    
    async def _parse_user_data(self, user_data: Dict) -> Optional[RedditUser]:
        """Parse Reddit API user data into RedditUser model"""
        try:
            user = RedditUser(
                username=user_data.get('name', ''),
                created_utc=datetime.fromtimestamp(user_data.get('created_utc', 0)),
                comment_karma=user_data.get('comment_karma', 0),
                link_karma=user_data.get('link_karma', 0),
                total_karma=user_data.get('total_karma', 0),
                is_verified=user_data.get('verified', False),
                is_mod=user_data.get('is_mod', False),
                is_admin=user_data.get('is_employee', False),
                is_premium=user_data.get('is_gold', False),
                has_verified_email=user_data.get('has_verified_email', False),
                icon_img=user_data.get('icon_img'),
                profile_over_18=user_data.get('subreddit', {}).get('over_18', False)
            )
            
            return user
            
        except Exception as e:
            logger.error(f"Error parsing user data: {str(e)}")
            return None
    
    def _generate_search_queries(self, protected_content: Dict) -> List[str]:
        """Generate search queries for content protection"""
        queries = []
        
        if 'title' in protected_content:
            queries.append(protected_content['title'])
        
        if 'content' in protected_content:
            # Extract key phrases from content
            words = protected_content['content'].split()
            if len(words) > 5:
                queries.append(' '.join(words[:10]))
        
        if 'keywords' in protected_content:
            queries.extend(protected_content['keywords'][:3])
        
        return queries[:5]
    
    async def _calculate_content_similarity(
        self,
        protected_content: Dict,
        post: RedditPost
    ) -> float:
        """
Calculate similarity between protected content and Reddit post"""
        from difflib import SequenceMatcher
        
        similarity_scores = []
        
        # Title similarity
        if 'title' in protected_content and post.title:
            title_similarity = SequenceMatcher(
                None,
                protected_content['title'].lower(),
                post.title.lower()
            ).ratio()
            similarity_scores.append(title_similarity * 0.4)
        
        # Content similarity
        if 'content' in protected_content and post.content:
            content_similarity = SequenceMatcher(
                None,
                protected_content['content'].lower(),
                post.content.lower()
            ).ratio()
            similarity_scores.append(content_similarity * 0.6)
        
        return sum(similarity_scores) if similarity_scores else 0.0
    
    def _calculate_virality_score(self, post: RedditPost) -> float:
        """
Calculate post virality score"""
        post_age_hours = (datetime.utcnow() - post.created_utc).total_seconds() / 3600
        if post_age_hours == 0:
            post_age_hours = 1
        
        # Normalize by post age
        score_velocity = post.score / post_age_hours
        comment_velocity = post.num_comments / post_age_hours
        
        # Factor in upvote ratio and gilding
        engagement_multiplier = post.upvote_ratio * (1 + post.gilded * 0.1)
        
        virality_score = (score_velocity + comment_velocity * 2) * engagement_multiplier
        
        return min(virality_score, 10000)  # Cap at 10000
    
    def _calculate_virality_score_from_data(self, post_data: Dict) -> float:
        """
Calculate virality score from raw post data"""
        created_utc = post_data.get('created_utc', 0)
        post_age_hours = (datetime.utcnow().timestamp() - created_utc) / 3600
        if post_age_hours == 0:
            post_age_hours = 1
        
        score = post_data.get('score', 0)
        num_comments = post_data.get('num_comments', 0)
        upvote_ratio = post_data.get('upvote_ratio', 0.5)
        gilded = post_data.get('gilded', 0)
        
        score_velocity = score / post_age_hours
        comment_velocity = num_comments / post_age_hours
        engagement_multiplier = upvote_ratio * (1 + gilded * 0.1)
        
        virality_score = (score_velocity + comment_velocity * 2) * engagement_multiplier
        
        return min(virality_score, 10000)
    
    async def _predict_peak_activity(self, post: RedditPost) -> str:
        """
Predict when post will reach peak activity"""
        post_age_hours = (datetime.utcnow() - post.created_utc).total_seconds() / 3600
        
        if post_age_hours < 2:
            return "within_2_hours"
        elif post_age_hours < 6:
            return "within_6_hours"
        elif post_age_hours < 24:
            return "within_24_hours"
        else:
            return "peak_passed"
    
    async def _analyze_comment_sentiment(self, comments: List[RedditComment]) -> Dict[str, Any]:
        """Analyze sentiment of comments"""
        if not comments:
            return {'overall_sentiment': 'neutral', 'positive_ratio': 0.0}
        
        # Simple sentiment analysis based on scores and keywords
        positive_comments = len([c for c in comments if c.score > 5])
        negative_comments = len([c for c in comments if c.score < -1])
        total_comments = len(comments)
        
        positive_ratio = positive_comments / total_comments if total_comments > 0 else 0
        negative_ratio = negative_comments / total_comments if total_comments > 0 else 0
        
        if positive_ratio > 0.6:
            overall_sentiment = 'positive'
        elif negative_ratio > 0.3:
            overall_sentiment = 'negative'
        else:
            overall_sentiment = 'neutral'
        
        return {
            'overall_sentiment': overall_sentiment,
            'positive_ratio': positive_ratio,
            'negative_ratio': negative_ratio,
            'avg_comment_score': sum(c.score for c in comments) / len(comments)
        }
    
    def _assess_discussion_quality(self, comments: List[RedditComment]) -> str:
        """
Assess quality of discussion in comments"""
        if not comments:
            return 'no_discussion'
        
        # Simple quality assessment based on comment length and depth
        avg_comment_length = sum(len(c.body) for c in comments) / len(comments)
        max_depth = max(c.depth for c in comments) if comments else 0
        gilded_comments = len([c for c in comments if c.gilded > 0])
        
        quality_score = 0
        
        if avg_comment_length > 100:
            quality_score += 2
        elif avg_comment_length > 50:
            quality_score += 1
        
        if max_depth > 3:
            quality_score += 2
        elif max_depth > 1:
            quality_score += 1
        
        if gilded_comments > 0:
            quality_score += 1
        
        if quality_score >= 4:
            return 'high_quality'
        elif quality_score >= 2:
            return 'medium_quality'
        else:
            return 'low_quality'
    
    def _categorize_performance(self, post: RedditPost) -> str:
        """
Categorize post performance level"""
        if post.score > 10000:
            return "viral"
        elif post.score > 1000:
            return "high"
        elif post.score > 100:
            return "medium"
        else:
            return "low"
    
    async def _analyze_posting_patterns(self, posts: List[RedditPost]) -> Dict[str, Any]:
        """Analyze temporal posting patterns"""
        if not posts:
            return {}
        
        # Analyze posting by hour
        hour_counts = {}
        for post in posts:
            hour = post.created_utc.hour
            hour_counts[hour] = hour_counts.get(hour, 0) + 1
        
        # Find peak posting hour
        peak_hour = max(hour_counts.items(), key=lambda x: x[1])[0] if hour_counts else 0
        
        return {
            'posts_by_hour': hour_counts,
            'peak_posting_hour': peak_hour,
            'total_posts': len(posts)
        }
    
    async def _analyze_popular_flairs(self, posts: List[RedditPost]) -> Dict[str, int]:
        """
Analyze popular flairs in posts"""
        flair_counts = {}
        
        for post in posts:
            if post.flair_text:
                flair_counts[post.flair_text] = flair_counts.get(post.flair_text, 0) + 1
        
        return dict(sorted(flair_counts.items(), key=lambda x: x[1], reverse=True)[:10])
    
    async def _analyze_engagement_distribution(self, posts: List[RedditPost]) -> Dict[str, Any]:
        """
Analyze engagement distribution across posts"""
        if not posts:
            return {}
        
        scores = [p.score for p in posts]
        comments = [p.num_comments for p in posts]
        
        return {
            'score_distribution': {
                'min': min(scores),
                'max': max(scores),
                'avg': sum(scores) / len(scores),
                'median': sorted(scores)[len(scores)//2]
            },
            'comment_distribution': {
                'min': min(comments),
                'max': max(comments),
                'avg': sum(comments) / len(comments),
                'median': sorted(comments)[len(comments)//2]
            }
        }
    
    async def _analyze_content_types(self, posts: List[RedditPost]) -> Dict[str, int]:
        """
Analyze distribution of content types"""
        type_counts = {
            'text_posts': 0,
            'image_posts': 0,
            'video_posts': 0,
            'link_posts': 0,
            'other': 0
        }
        
        for post in posts:
            if post.is_self:
                type_counts['text_posts'] += 1
            elif post.post_hint == 'image':
                type_counts['image_posts'] += 1
            elif post.post_hint in ['hosted:video', 'rich:video']:
                type_counts['video_posts'] += 1
            elif post.post_hint == 'link':
                type_counts['link_posts'] += 1
            else:
                type_counts['other'] += 1
        
        return type_counts
    
    async def _analyze_user_activity(self, posts: List[RedditPost]) -> Dict[str, Any]:
        """
Analyze user activity patterns"""
        authors = [p.author for p in posts if p.author != '[deleted]']
        unique_authors = set(authors)
        
        # Count posts per author
        author_counts = {}
        for author in authors:
            author_counts[author] = author_counts.get(author, 0) + 1
        
        # Find most active users
        top_contributors = sorted(author_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            'unique_contributors': len(unique_authors),
            'total_posts': len(posts),
            'avg_posts_per_user': len(posts) / len(unique_authors) if unique_authors else 0,
            'top_contributors': [{'username': user, 'post_count': count} for user, count in top_contributors]
        }
