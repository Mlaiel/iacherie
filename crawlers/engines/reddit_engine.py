"""
Reddit Crawling Engine
=====================

Advanced Reddit crawler for content discovery, trend analysis, and community monitoring.
Handles subreddits, posts, comments, and user data extraction.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

  AVERTISSEMENT LÉGAL 
Ce code est la propriété exclusive de Fahed Mlaiel (mlaiel@live.de).
Toute utilisation, reproduction, ou distribution sans autorisation écrite explicite est strictement interdite.
Les contrevenants seront poursuivis selon la loi allemande et internationale.

 Architecture Enterprise - Équipe Projet Spécialisée :
• Lead Developer IA : Fahed Mlaiel (mlaiel@live.de)
• Backend Senior Engineer : Architecture microservices & APIs
• ML/AI Engineer : Intelligence artificielle & algorithmes avancés
• Database Administrator : Optimisation données & performance
• Security Expert : Cybersécurité & protection contenu
• DevOps Engineer : Infrastructure cloud & déploiement
• Audio/Video Specialist : Traitement multimédia avancé
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, AsyncGenerator, Union
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import re
import json
import hashlib
import time

import aiohttp
import praw
import prawcore
import asyncpraw
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By

from ..core.base_engine import BaseCrawlerEngine
from ..core.exceptions import (
    CrawlerError, 
    RateLimitError, 
    AuthenticationError,
    ContentNotFoundError,
    SubredditPrivateError
)
from ..utils.rate_limiter import RateLimiter
from ..utils.cache_manager import CacheManager
from ..utils.proxy_manager import ProxyManager
from ..models.content_models import ForumPost, ForumComment, CommunityData
from ...core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


@dataclass
class RedditPostData:
    """Reddit post data structure"""
    post_id: str
    subreddit: str
    title: str
    selftext: str
    url: str
    author: str
    created_utc: datetime
    score: int
    upvote_ratio: float
    num_comments: int
    num_crossposts: int
    gilded: int
    total_awards_received: int
    over_18: bool
    spoiler: bool
    locked: bool
    stickied: bool
    distinguished: Optional[str]
    link_flair_text: Optional[str]
    link_flair_css_class: Optional[str]
    author_flair_text: Optional[str]
    author_flair_css_class: Optional[str]
    thumbnail: str
    is_self: bool
    is_video: bool
    media: Optional[Dict[str, Any]]
    media_embed: Dict[str, Any]
    secure_media: Optional[Dict[str, Any]]
    secure_media_embed: Dict[str, Any]
    post_hint: Optional[str]
    preview: Optional[Dict[str, Any]]
    all_awardings: List[Dict[str, Any]]
    treatment_tags: List[str]
    view_count: Optional[int] = None
    archived: bool = False
    removed_by_category: Optional[str] = None
    banned_by: Optional[str] = None
    removal_reason: Optional[str] = None


@dataclass
class RedditCommentData:
    """Reddit comment data structure"""
    comment_id: str
    post_id: str
    subreddit: str
    parent_id: str
    author: str
    body: str
    created_utc: datetime
    score: int
    gilded: int
    total_awards_received: int
    edited: Union[bool, float]
    distinguished: Optional[str]
    stickied: bool
    score_hidden: bool
    controversiality: int
    depth: int
    author_flair_text: Optional[str]
    author_flair_css_class: Optional[str]
    all_awardings: List[Dict[str, Any]]
    treatment_tags: List[str]
    replies: List['RedditCommentData'] = None
    is_submitter: bool = False
    archived: bool = False
    locked: bool = False
    removed: bool = False
    collapsed: bool = False


@dataclass
class RedditSubredditData:
    """Reddit subreddit data structure"""
    subreddit_name: str
    display_name: str
    title: str
    public_description: str
    description: str
    header_title: str
    header_img: str
    icon_img: str
    banner_img: str
    banner_background_image: str
    mobile_banner_image: str
    community_icon: str
    primary_color: str
    key_color: str
    created_utc: datetime
    subscribers: int
    active_user_count: int
    accounts_active: int
    lang: str
    whitelist_status: str
    subreddit_type: str  # public, private, restricted, etc.
    over18: bool
    quarantine: bool
    allow_images: bool
    allow_videos: bool
    allow_polls: bool
    allow_galleries: bool
    spoilers_enabled: bool
    original_content_tag_enabled: bool
    submit_text: str
    submit_text_label: str
    user_flair_enabled_in_sr: bool
    link_flair_enabled: bool
    moderators: List[str] = None
    rules: List[Dict[str, Any]] = None
    wiki_enabled: bool = True


@dataclass
class RedditUserData:
    """Reddit user data structure"""
    username: str
    user_id: str
    created_utc: datetime
    comment_karma: int
    link_karma: int
    total_karma: int
    awardee_karma: int
    awarder_karma: int
    is_employee: bool
    is_mod: bool
    is_gold: bool
    is_blocked: bool
    is_friend: bool
    verified: bool
    has_verified_email: bool
    icon_img: str
    subreddit: Dict[str, Any]
    coins: int
    num_friends: int
    created_timestamp: float
    gold_expiration: Optional[datetime] = None
    gold_creddits: int = 0
    inbox_count: int = 0
    has_mail: bool = False
    has_mod_mail: bool = False
    over_18: bool = False
    accept_followers: bool = True
    accept_pms: str = 'everyone'


class RedditCrawlerEngine(BaseCrawlerEngine):
    """
    Advanced Reddit crawler engine with comprehensive API integration.
    
    Features:
    - Official Reddit API (PRAW) integration
    - Async Reddit API support
    - Subreddit analysis and monitoring
    - Post and comment extraction
    - User profile analysis
    - Trending content detection
    - Cross-subreddit analysis
    - Sentiment analysis integration
    """

    def __init__(self, 
                 client_id: Optional[str] = None,
                 client_secret: Optional[str] = None,
                 user_agent: Optional[str] = None,
                 username: Optional[str] = None,
                 password: Optional[str] = None,
                 use_async: bool = True,
                 proxy_config: Optional[Dict] = None,
                 rate_limit_config: Optional[Dict] = None):
        """
        Initialize Reddit crawler engine.
        
        Args:
            client_id: Reddit API client ID
            client_secret: Reddit API client secret
            user_agent: User agent string
            username: Reddit username (for authenticated requests)
            password: Reddit password (for authenticated requests)
            use_async: Whether to use async PRAW
            proxy_config: Proxy configuration
            rate_limit_config: Rate limiting configuration
        """
        super().__init__()
        
        # API Configuration
        self.client_id = client_id or settings.REDDIT_CLIENT_ID
        self.client_secret = client_secret or settings.REDDIT_CLIENT_SECRET
        self.user_agent = user_agent or settings.REDDIT_USER_AGENT or "IA-Influencer-Agent:v1.0"
        self.username = username or settings.REDDIT_USERNAME
        self.password = password or settings.REDDIT_PASSWORD
        
        # Reddit API clients
        self.reddit = None
        self.async_reddit = None
        self.use_async = use_async
        
        # Rate limiting (Reddit: 60 requests per minute)
        rate_config = rate_limit_config or {
            'requests_per_minute': 60,
            'requests_per_hour': 3600,
            'burst_limit': 30
        }
        self.rate_limiter = RateLimiter(**rate_config)
        
        # Cache manager
        self.cache_manager = CacheManager(
            cache_type='redis',
            ttl=3600,  # 1 hour cache
            key_prefix='reddit_'
        )
        
        # Proxy manager
        if proxy_config:
            self.proxy_manager = ProxyManager(proxy_config)
        else:
            self.proxy_manager = None

    async def authenticate(self) -> bool:
        """Authenticate with Reddit API"""



        try:
            if self.use_async:
                self.async_reddit = asyncpraw.Reddit(
                    client_id=self.client_id,
                    client_secret=self.client_secret,
                    user_agent=self.user_agent,
                    username=self.username,
                    password=self.password
                )
                
                # Test authentication
                user = await self.async_reddit.user.me()
                if user:
                    logger.info(f"Authenticated Reddit user: {user.name}")
                    return True
            
            else:
                self.reddit = praw.Reddit(
                    client_id=self.client_id,
                    client_secret=self.client_secret,
                    user_agent=self.user_agent,
                    username=self.username,
                    password=self.password
                )
                
                # Test authentication
                user = self.reddit.user.me()
                if user:
                    logger.info(f"Authenticated Reddit user: {user.name}")
                    return True
            
            return False
        
        except Exception as e:
            logger.error(f"Reddit authentication failed: {e}")
            return False

    async def search_posts(self, 
                          query: str,
                          subreddit: Optional[str] = None,
                          sort: str = 'relevance',
                          time_filter: str = 'all',
                          limit: int = 100) -> List[RedditPostData]:
        """
        Search for Reddit posts by query.
        
        Args:
            query: Search query
            subreddit: Specific subreddit to search in (None for all)
            sort: Sort method (relevance, hot, top, new, comments)
            time_filter: Time filter (all, year, month, week, day, hour)
            limit: Maximum number of posts to return
        
        Returns:
            List of RedditPostData objects
        """
        cache_key = f"search_posts_{hashlib.md5(query.encode()).hexdigest()}_{subreddit}_{sort}_{limit}"
        cached_result = await self.cache_manager.get(cache_key)
        if cached_result:
            return [RedditPostData(**post) for post in cached_result]

        posts = []
        
        try:
            await self.rate_limiter.acquire()
            
            if self.use_async and self.async_reddit:
                if subreddit:
                    subreddit_obj = await self.async_reddit.subreddit(subreddit)
                    search_results = subreddit_obj.search(
                        query,
                        sort=sort,
                        time_filter=time_filter,
                        limit=limit
                    )
                else:
                    search_results = self.async_reddit.subreddit('all').search(
                        query,
                        sort=sort,
                        time_filter=time_filter,
                        limit=limit
                    )
                
                async for submission in search_results:
                    post_data = await self._process_post_data_async(submission)
                    if post_data:
                        posts.append(post_data)
            
            elif self.reddit:
                if subreddit:
                    subreddit_obj = self.reddit.subreddit(subreddit)
                    search_results = subreddit_obj.search(
                        query,
                        sort=sort,
                        time_filter=time_filter,
                        limit=limit
                    )
                else:
                    search_results = self.reddit.subreddit('all').search(
                        query,
                        sort=sort,
                        time_filter=time_filter,
                        limit=limit
                    )
                
                for submission in search_results:
                    post_data = await self._process_post_data(submission)
                    if post_data:
                        posts.append(post_data)
            
            # Cache results
            await self.cache_manager.set(
                cache_key, 
                [asdict(post) for post in posts]
            )
        
        except Exception as e:
            logger.error(f"Error searching Reddit posts: {e}")
            raise CrawlerError(f"Reddit post search failed: {e}")
        
        return posts

    async def get_subreddit_info(self, subreddit_name: str) -> RedditSubredditData:
        """
        Get Reddit subreddit information.
        
        Args:
            subreddit_name: Name of the subreddit
        
        Returns:
            RedditSubredditData object
        """
        cache_key = f"subreddit_info_{subreddit_name}"
        cached_result = await self.cache_manager.get(cache_key)
        if cached_result:
            return RedditSubredditData(**cached_result)

        try:
            await self.rate_limiter.acquire()
            
            if self.use_async and self.async_reddit:
                subreddit = await self.async_reddit.subreddit(subreddit_name)
                
                # Get moderators
                moderators = []
                async for mod in subreddit.moderator():
                    moderators.append(mod.name)
                
                # Get rules
                rules = []
                async for rule in subreddit.rules():
                    rules.append({
                        'short_name': rule.short_name,
                        'description': rule.description,
                        'kind': rule.kind,
                        'violation_reason': rule.violation_reason
                    })
                
                subreddit_data = RedditSubredditData(
                    subreddit_name=subreddit.display_name,
                    display_name=subreddit.display_name,
                    title=subreddit.title,
                    public_description=subreddit.public_description,
                    description=subreddit.description,
                    header_title=getattr(subreddit, 'header_title', ''),
                    header_img=getattr(subreddit, 'header_img', ''),
                    icon_img=getattr(subreddit, 'icon_img', ''),
                    banner_img=getattr(subreddit, 'banner_img', ''),
                    banner_background_image=getattr(subreddit, 'banner_background_image', ''),
                    mobile_banner_image=getattr(subreddit, 'mobile_banner_image', ''),
                    community_icon=getattr(subreddit, 'community_icon', ''),
                    primary_color=getattr(subreddit, 'primary_color', ''),
                    key_color=getattr(subreddit, 'key_color', ''),
                    created_utc=datetime.fromtimestamp(subreddit.created_utc),
                    subscribers=subreddit.subscribers,
                    active_user_count=getattr(subreddit, 'active_user_count', 0),
                    accounts_active=getattr(subreddit, 'accounts_active', 0),
                    lang=subreddit.lang,
                    whitelist_status=getattr(subreddit, 'whitelist_status', ''),
                    subreddit_type=subreddit.subreddit_type,
                    over18=subreddit.over18,
                    quarantine=getattr(subreddit, 'quarantine', False),
                    allow_images=getattr(subreddit, 'allow_images', True),
                    allow_videos=getattr(subreddit, 'allow_videos', True),
                    allow_polls=getattr(subreddit, 'allow_polls', True),
                    allow_galleries=getattr(subreddit, 'allow_galleries', True),
                    spoilers_enabled=getattr(subreddit, 'spoilers_enabled', True),
                    original_content_tag_enabled=getattr(subreddit, 'original_content_tag_enabled', False),
                    submit_text=getattr(subreddit, 'submit_text', ''),
                    submit_text_label=getattr(subreddit, 'submit_text_label', ''),
                    user_flair_enabled_in_sr=getattr(subreddit, 'user_flair_enabled_in_sr', False),
                    link_flair_enabled=getattr(subreddit, 'link_flair_enabled', False),
                    moderators=moderators,
                    rules=rules,
                    wiki_enabled=getattr(subreddit, 'wiki_enabled', True)
                )
            
            elif self.reddit:
                subreddit = self.reddit.subreddit(subreddit_name)
                
                # Get moderators
                moderators = [mod.name for mod in subreddit.moderator()]
                
                # Get rules
                rules = []
                for rule in subreddit.rules():
                    rules.append({
                        'short_name': rule.short_name,
                        'description': rule.description,
                        'kind': rule.kind,
                        'violation_reason': rule.violation_reason
                    })
                
                subreddit_data = RedditSubredditData(
                    subreddit_name=subreddit.display_name,
                    display_name=subreddit.display_name,
                    title=subreddit.title,
                    public_description=subreddit.public_description,
                    description=subreddit.description,
                    header_title=getattr(subreddit, 'header_title', ''),
                    header_img=getattr(subreddit, 'header_img', ''),
                    icon_img=getattr(subreddit, 'icon_img', ''),
                    banner_img=getattr(subreddit, 'banner_img', ''),
                    banner_background_image=getattr(subreddit, 'banner_background_image', ''),
                    mobile_banner_image=getattr(subreddit, 'mobile_banner_image', ''),
                    community_icon=getattr(subreddit, 'community_icon', ''),
                    primary_color=getattr(subreddit, 'primary_color', ''),
                    key_color=getattr(subreddit, 'key_color', ''),
                    created_utc=datetime.fromtimestamp(subreddit.created_utc),
                    subscribers=subreddit.subscribers,
                    active_user_count=getattr(subreddit, 'active_user_count', 0),
                    accounts_active=getattr(subreddit, 'accounts_active', 0),
                    lang=subreddit.lang,
                    whitelist_status=getattr(subreddit, 'whitelist_status', ''),
                    subreddit_type=subreddit.subreddit_type,
                    over18=subreddit.over18,
                    quarantine=getattr(subreddit, 'quarantine', False),
                    allow_images=getattr(subreddit, 'allow_images', True),
                    allow_videos=getattr(subreddit, 'allow_videos', True),
                    allow_polls=getattr(subreddit, 'allow_polls', True),
                    allow_galleries=getattr(subreddit, 'allow_galleries', True),
                    spoilers_enabled=getattr(subreddit, 'spoilers_enabled', True),
                    original_content_tag_enabled=getattr(subreddit, 'original_content_tag_enabled', False),
                    submit_text=getattr(subreddit, 'submit_text', ''),
                    submit_text_label=getattr(subreddit, 'submit_text_label', ''),
                    user_flair_enabled_in_sr=getattr(subreddit, 'user_flair_enabled_in_sr', False),
                    link_flair_enabled=getattr(subreddit, 'link_flair_enabled', False),
                    moderators=moderators,
                    rules=rules,
                    wiki_enabled=getattr(subreddit, 'wiki_enabled', True)
                )
            
            # Cache result
            await self.cache_manager.set(cache_key, asdict(subreddit_data))
            
            return subreddit_data
        
        except Exception as e:
            logger.error(f"Error getting Reddit subreddit info: {e}")
            raise CrawlerError(f"Reddit subreddit info retrieval failed: {e}")

    async def get_subreddit_posts(self, 
                                subreddit_name: str,
                                sort: str = 'hot',
                                time_filter: str = 'day',
                                limit: int = 100) -> List[RedditPostData]:
        """
        Get posts from a Reddit subreddit.
        
        Args:
            subreddit_name: Name of the subreddit
            sort: Sort method (hot, new, top, rising)
            time_filter: Time filter for top posts (all, year, month, week, day, hour)
            limit: Maximum number of posts to return
        
        Returns:
            List of RedditPostData objects
        """
        cache_key = f"subreddit_posts_{subreddit_name}_{sort}_{time_filter}_{limit}"
        cached_result = await self.cache_manager.get(cache_key)
        if cached_result:
            return [RedditPostData(**post) for post in cached_result]

        posts = []
        
        try:
            await self.rate_limiter.acquire()
            
            if self.use_async and self.async_reddit:
                subreddit = await self.async_reddit.subreddit(subreddit_name)
                
                if sort == 'hot':
                    submissions = subreddit.hot(limit=limit)
                elif sort == 'new':
                    submissions = subreddit.new(limit=limit)
                elif sort == 'top':
                    submissions = subreddit.top(time_filter=time_filter, limit=limit)
                elif sort == 'rising':
                    submissions = subreddit.rising(limit=limit)
                else:
                    submissions = subreddit.hot(limit=limit)
                
                async for submission in submissions:
                    post_data = await self._process_post_data_async(submission)
                    if post_data:
                        posts.append(post_data)
            
            elif self.reddit:
                subreddit = self.reddit.subreddit(subreddit_name)
                
                if sort == 'hot':
                    submissions = subreddit.hot(limit=limit)
                elif sort == 'new':
                    submissions = subreddit.new(limit=limit)
                elif sort == 'top':
                    submissions = subreddit.top(time_filter=time_filter, limit=limit)
                elif sort == 'rising':
                    submissions = subreddit.rising(limit=limit)
                else:
                    submissions = subreddit.hot(limit=limit)
                
                for submission in submissions:
                    post_data = await self._process_post_data(submission)
                    if post_data:
                        posts.append(post_data)
            
            # Cache results
            await self.cache_manager.set(
                cache_key, 
                [asdict(post) for post in posts]
            )
        
        except Exception as e:
            logger.error(f"Error getting Reddit subreddit posts: {e}")
            raise CrawlerError(f"Reddit subreddit posts retrieval failed: {e}")
        
        return posts

    async def get_post_comments(self, 
                              post_id: str,
                              sort: str = 'best',
                              limit: int = 100) -> List[RedditCommentData]:
        """
        Get comments from a Reddit post.
        
        Args:
            post_id: Reddit post ID
            sort: Sort method (best, top, new, controversial, old, qa)
            limit: Maximum number of comments to return
        
        Returns:
            List of RedditCommentData objects
        """
        cache_key = f"post_comments_{post_id}_{sort}_{limit}"
        cached_result = await self.cache_manager.get(cache_key)
        if cached_result:
            return [RedditCommentData(**comment) for comment in cached_result]

        comments = []
        
        try:
            await self.rate_limiter.acquire()
            
            if self.use_async and self.async_reddit:
                submission = await self.async_reddit.submission(id=post_id)
                await submission.load()
                
                submission.comment_sort = sort
                await submission.comments.replace_more(limit=0)
                
                for comment in submission.comments.list()[:limit]:
                    if hasattr(comment, 'body'):  # Skip MoreComments objects
                        comment_data = await self._process_comment_data_async(comment)
                        if comment_data:
                            comments.append(comment_data)
            
            elif self.reddit:
                submission = self.reddit.submission(id=post_id)
                submission.comment_sort = sort
                submission.comments.replace_more(limit=0)
                
                for comment in submission.comments.list()[:limit]:
                    if hasattr(comment, 'body'):  # Skip MoreComments objects
                        comment_data = await self._process_comment_data(comment)
                        if comment_data:
                            comments.append(comment_data)
            
            # Cache results
            await self.cache_manager.set(
                cache_key, 
                [asdict(comment) for comment in comments]
            )
        
        except Exception as e:
            logger.error(f"Error getting Reddit post comments: {e}")
            raise CrawlerError(f"Reddit post comments retrieval failed: {e}")
        
        return comments

    async def monitor_subreddit_content(self, 
                                      subreddits: List[str],
                                      keywords: List[str],
                                      check_interval: int = 300) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Monitor Reddit subreddits for content matches.
        
        Args:
            subreddits: List of subreddit names to monitor
            keywords: Keywords to search for
            check_interval: Check interval in seconds
        
        Yields:
            Dictionary containing monitoring results
        """
        logger.info(f"Starting Reddit content monitoring for {len(subreddits)} subreddits")
        
        while True:
            for subreddit_name in subreddits:
                try:
                    # Get recent posts
                    posts = await self.get_subreddit_posts(
                        subreddit_name,
                        sort='new',
                        limit=25
                    )
                    
                    for post in posts:
                        content = f"{post.title} {post.selftext}".lower()
                        for keyword in keywords:
                            if keyword.lower() in content:
                                yield {
                                    'type': 'reddit_content_match',
                                    'platform': 'reddit',
                                    'subreddit': subreddit_name,
                                    'post_id': post.post_id,
                                    'keyword': keyword,
                                    'title': post.title,
                                    'content': content[:500],
                                    'author': post.author,
                                    'url': post.url,
                                    'score': post.score,
                                    'comments': post.num_comments,
                                    'timestamp': post.created_utc
                                }
                
                except Exception as e:
                    logger.error(f"Error monitoring Reddit subreddit {subreddit_name}: {e}")
                    yield {
                        'type': 'error',
                        'platform': 'reddit',
                        'subreddit': subreddit_name,
                        'error': str(e),
                        'timestamp': datetime.now()
                    }
            
            await asyncio.sleep(check_interval)

    async def _process_post_data(self, submission) -> Optional[RedditPostData]:
        """Process Reddit submission into RedditPostData object"""



        try:
            return RedditPostData(
                post_id=submission.id,
                subreddit=submission.subreddit.display_name,
                title=submission.title,
                selftext=submission.selftext,
                url=submission.url,
                author=submission.author.name if submission.author else '[deleted]',
                created_utc=datetime.fromtimestamp(submission.created_utc),
                score=submission.score,
                upvote_ratio=submission.upvote_ratio,
                num_comments=submission.num_comments,
                num_crossposts=submission.num_crossposts,
                gilded=submission.gilded,
                total_awards_received=getattr(submission, 'total_awards_received', 0),
                over_18=submission.over_18,
                spoiler=submission.spoiler,
                locked=submission.locked,
                stickied=submission.stickied,
                distinguished=submission.distinguished,
                link_flair_text=submission.link_flair_text,
                link_flair_css_class=submission.link_flair_css_class,
                author_flair_text=submission.author_flair_text,
                author_flair_css_class=submission.author_flair_css_class,
                thumbnail=submission.thumbnail,
                is_self=submission.is_self,
                is_video=submission.is_video,
                media=submission.media,
                media_embed=submission.media_embed,
                secure_media=submission.secure_media,
                secure_media_embed=submission.secure_media_embed,
                post_hint=getattr(submission, 'post_hint', None),
                preview=getattr(submission, 'preview', None),
                all_awardings=getattr(submission, 'all_awardings', []),
                treatment_tags=getattr(submission, 'treatment_tags', []),
                view_count=getattr(submission, 'view_count', None),
                archived=submission.archived,
                removed_by_category=getattr(submission, 'removed_by_category', None),
                banned_by=getattr(submission, 'banned_by', None),
                removal_reason=getattr(submission, 'removal_reason', None)
            )
        
        except Exception as e:
            logger.error(f"Error processing Reddit post data: {e}")
            return None

    async def _process_post_data_async(self, submission) -> Optional[RedditPostData]:
        """Process async Reddit submission into RedditPostData object"""



        try:
            author_name = '[deleted]'
            if submission.author:
                author_name = submission.author.name
            
            return RedditPostData(
                post_id=submission.id,
                subreddit=submission.subreddit.display_name,
                title=submission.title,
                selftext=submission.selftext,
                url=submission.url,
                author=author_name,
                created_utc=datetime.fromtimestamp(submission.created_utc),
                score=submission.score,
                upvote_ratio=submission.upvote_ratio,
                num_comments=submission.num_comments,
                num_crossposts=submission.num_crossposts,
                gilded=submission.gilded,
                total_awards_received=getattr(submission, 'total_awards_received', 0),
                over_18=submission.over_18,
                spoiler=submission.spoiler,
                locked=submission.locked,
                stickied=submission.stickied,
                distinguished=submission.distinguished,
                link_flair_text=submission.link_flair_text,
                link_flair_css_class=submission.link_flair_css_class,
                author_flair_text=submission.author_flair_text,
                author_flair_css_class=submission.author_flair_css_class,
                thumbnail=submission.thumbnail,
                is_self=submission.is_self,
                is_video=submission.is_video,
                media=submission.media,
                media_embed=submission.media_embed,
                secure_media=submission.secure_media,
                secure_media_embed=submission.secure_media_embed,
                post_hint=getattr(submission, 'post_hint', None),
                preview=getattr(submission, 'preview', None),
                all_awardings=getattr(submission, 'all_awardings', []),
                treatment_tags=getattr(submission, 'treatment_tags', []),
                view_count=getattr(submission, 'view_count', None),
                archived=submission.archived,
                removed_by_category=getattr(submission, 'removed_by_category', None),
                banned_by=getattr(submission, 'banned_by', None),
                removal_reason=getattr(submission, 'removal_reason', None)
            )
        
        except Exception as e:
            logger.error(f"Error processing async Reddit post data: {e}")
            return None

    async def _process_comment_data(self, comment) -> Optional[RedditCommentData]:
        """Process Reddit comment into RedditCommentData object"""



        try:
            return RedditCommentData(
                comment_id=comment.id,
                post_id=comment.submission.id,
                subreddit=comment.subreddit.display_name,
                parent_id=comment.parent_id,
                author=comment.author.name if comment.author else '[deleted]',
                body=comment.body,
                created_utc=datetime.fromtimestamp(comment.created_utc),
                score=comment.score,
                gilded=comment.gilded,
                total_awards_received=getattr(comment, 'total_awards_received', 0),
                edited=comment.edited,
                distinguished=comment.distinguished,
                stickied=comment.stickied,
                score_hidden=comment.score_hidden,
                controversiality=comment.controversiality,
                depth=comment.depth,
                author_flair_text=comment.author_flair_text,
                author_flair_css_class=comment.author_flair_css_class,
                all_awardings=getattr(comment, 'all_awardings', []),
                treatment_tags=getattr(comment, 'treatment_tags', []),
                is_submitter=comment.is_submitter,
                archived=getattr(comment, 'archived', False),
                locked=getattr(comment, 'locked', False),
                removed=getattr(comment, 'removed', False),
                collapsed=getattr(comment, 'collapsed', False)
            )
        
        except Exception as e:
            logger.error(f"Error processing Reddit comment data: {e}")
            return None

    async def _process_comment_data_async(self, comment) -> Optional[RedditCommentData]:
        """Process async Reddit comment into RedditCommentData object"""



        try:
            author_name = '[deleted]'
            if comment.author:
                author_name = comment.author.name
            
            return RedditCommentData(
                comment_id=comment.id,
                post_id=comment.submission.id,
                subreddit=comment.subreddit.display_name,
                parent_id=comment.parent_id,
                author=author_name,
                body=comment.body,
                created_utc=datetime.fromtimestamp(comment.created_utc),
                score=comment.score,
                gilded=comment.gilded,
                total_awards_received=getattr(comment, 'total_awards_received', 0),
                edited=comment.edited,
                distinguished=comment.distinguished,
                stickied=comment.stickied,
                score_hidden=comment.score_hidden,
                controversiality=comment.controversiality,
                depth=comment.depth,
                author_flair_text=comment.author_flair_text,
                author_flair_css_class=comment.author_flair_css_class,
                all_awardings=getattr(comment, 'all_awardings', []),
                treatment_tags=getattr(comment, 'treatment_tags', []),
                is_submitter=comment.is_submitter,
                archived=getattr(comment, 'archived', False),
                locked=getattr(comment, 'locked', False),
                removed=getattr(comment, 'removed', False),
                collapsed=getattr(comment, 'collapsed', False)
            )
        
        except Exception as e:
            logger.error(f"Error processing async Reddit comment data: {e}")
            return None

    async def close(self):
        """Close Reddit API connections"""
        if self.async_reddit:
            await self.async_reddit.close()

    def __del__(self):
        """Cleanup resources"""



        try:
            if self.async_reddit:
                asyncio.create_task(self.close())
        except:
            pass
