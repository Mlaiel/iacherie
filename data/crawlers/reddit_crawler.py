"""Reddit Crawler Implementation
=============================

Advanced Reddit community and content monitoring crawler.
Implements comprehensive subreddit analysis and user engagement tracking.

Team Expertise: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + 
Microservices + Audio + DevOps + IA Prompt Engineer

Author: Fahed Mlaiel (mlaiel@live.de)
Email: mlaiel@live.de
Copyright: © 2025 Fahed Mlaiel - All Rights Reserved

⚠️  CRITICAL WARNING ⚠️
This code is PROPRIETARY and CONFIDENTIAL intellectual property.
Any unauthorized use, reproduction, distribution, or reverse engineering 
is STRICTLY PROHIBITED and will result in immediate legal action.

Unauthorized copying or theft of this concept, code, or methodology 
will be prosecuted to the FULL EXTENT OF THE LAW under German and 
International Copyright Laws.

For licensing inquiries, contact: mlaiel@live.de
"""
import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, asdict
import aiohttp
import praw
import prawcore
import time
import random
from urllib.parse import urljoin, urlparse, parse_qs
import re

from .platform_crawler import PlatformCrawler, CrawlerConfig, CrawlerResult


@dataclass
class RedditUser:
    """Reddit user information"""
    username: str
    user_id: str
    created_utc: datetime
    comment_karma: int
    link_karma: int
    total_karma: int
    is_gold: bool
    is_mod: bool
    is_verified: bool
    has_verified_email: bool
    is_employee: bool
    is_suspended: bool
    subreddit: Optional[Dict[str, Any]]  # User's profile subreddit
    icon_img: Optional[str]
    snoovatar_img: Optional[str]
    profile_over_18: bool
    accept_followers: bool
    accept_pms: str  # everyone, whitelisted, nobody
    accept_chats: str
    hide_from_robots: bool
    description: Optional[str]
    public_description: Optional[str]
    awards_received: List[Dict[str, Any]]
    awards_given: int
    premium_since: Optional[datetime]
    coins: int
    has_gold_subscription: bool
    num_friends: int
    features: Dict[str, bool]
    can_edit_name: bool
    verified: bool
    new_modmail_exists: bool
    pref_show_snoovatar: bool
    name: str
    created: datetime
    link_karma_breakdown: Dict[str, int]
    comment_karma_breakdown: Dict[str, int]
    total_comment_karma: int
    total_link_karma: int
    submission_count: int
    comment_count: int
    subreddits_moderated: List[str]
    favorite_subreddits: List[str]
    recent_activity_score: float


@dataclass
class RedditPost:
    """Reddit post/submission information"""
    post_id: str
    title: str
    selftext: str
    selftext_html: Optional[str]
    url: str
    permalink: str
    subreddit: str
    subreddit_id: str
    author: str
    author_id: Optional[str]
    author_flair_text: Optional[str]
    author_flair_css_class: Optional[str]
    link_flair_text: Optional[str]
    link_flair_css_class: Optional[str]
    created_utc: datetime
    score: int
    upvote_ratio: float
    ups: int
    downs: int
    num_comments: int
    num_crossposts: int
    num_reports: int
    over_18: bool
    spoiler: bool
    locked: bool
    stickied: bool
    pinned: bool
    archived: bool
    is_self: bool
    is_video: bool
    is_original_content: bool
    is_reddit_media_domain: bool
    is_meta: bool
    distinguished: Optional[str]  # moderator, admin, special
    edited: Optional[datetime]
    gilded: int
    total_awards_received: int
    all_awardings: List[Dict[str, Any]]
    treatment_tags: List[str]
    removed_by_category: Optional[str]
    banned_by: Optional[str]
    removal_reason: Optional[str]
    domain: str
    thumbnail: Optional[str]
    thumbnail_width: Optional[int]
    thumbnail_height: Optional[int]
    preview: Optional[Dict[str, Any]]
    media: Optional[Dict[str, Any]]
    media_embed: Optional[Dict[str, Any]]
    secure_media: Optional[Dict[str, Any]]
    secure_media_embed: Optional[Dict[str, Any]]
    crosspost_parent: Optional[str]
    crosspost_parent_list: List[Dict[str, Any]]
    view_count: Optional[int]
    clicked: bool
    saved: bool
    hidden: bool
    contest_mode: bool
    suggested_sort: Optional[str]
    user_reports: List[str]
    mod_reports: List[str]
    mod_note: Optional[str]
    mod_reason_title: Optional[str]
    mod_reason_by: Optional[str]
    post_hint: Optional[str]
    content_categories: List[str]
    discussion_type: Optional[str]
    sentiment_score: Optional[float]
    engagement_score: float
    trending_score: float


@dataclass
class RedditComment:
    """Reddit comment information"""
    comment_id: str
    post_id: str
    parent_id: str
    subreddit: str
    subreddit_id: str
    author: str
    author_id: Optional[str]
    author_flair_text: Optional[str]
    author_flair_css_class: Optional[str]
    body: str
    body_html: str
    created_utc: datetime
    score: int
    ups: int
    downs: int
    likes: Optional[bool]
    replies: List[str]  # IDs of reply comments
    depth: int
    permalink: str
    distinguished: Optional[str]
    edited: Optional[datetime]
    gilded: int
    total_awards_received: int
    all_awardings: List[Dict[str, Any]]
    stickied: bool
    is_submitter: bool
    score_hidden: bool
    archived: bool
    locked: bool
    saved: bool
    collapsed: bool
    collapsed_reason: Optional[str]
    associated_award: Optional[Dict[str, Any]]
    unrepliable_reason: Optional[str]
    treatment_tags: List[str]
    user_reports: List[str]
    mod_reports: List[str]
    removal_reason: Optional[str]
    banned_by: Optional[str]
    approved_by: Optional[str]
    mod_note: Optional[str]
    mod_reason_title: Optional[str]
    mod_reason_by: Optional[str]
    sentiment_score: Optional[float]
    toxicity_score: Optional[float]
    spam_score: Optional[float]


@dataclass
class RedditSubreddit:
    """Reddit subreddit information"""
    subreddit_id: str
    name: str
    display_name: str
    display_name_prefixed: str
    title: str
    description: str
    description_html: str
    public_description: str
    rules: List[Dict[str, Any]]
    created_utc: datetime
    subscribers: int
    accounts_active: int
    accounts_active_is_fuzzed: bool
    active_user_count: int
    over18: bool
    lang: str
    whitelist_status: Optional[str]
    url: str
    quarantine: bool
    allow_discovery: bool
    subreddit_type: str  # public, private, restricted, etc.
    submission_type: str  # any, link, self
    can_assign_link_flair: bool
    can_assign_user_flair: bool
    allow_images: bool
    allow_videos: bool
    allow_polls: bool
    allow_galleries: bool
    allow_predictions: bool
    wiki_enabled: bool
    comment_score_hide_mins: int
    suggested_comment_sort: Optional[str]
    spoilers_enabled: bool
    original_content_tag_enabled: bool
    submit_text: str
    submit_text_html: str
    user_flair_enabled_in_sr: bool
    user_flair_position: str
    user_flair_type: str
    link_flair_enabled: bool
    link_flair_position: str
    emojis_enabled: bool
    banner_img: Optional[str]
    banner_size: Optional[List[int]]
    mobile_banner_image: Optional[str]
    icon_img: Optional[str]
    icon_size: Optional[List[int]]
    header_img: Optional[str]
    header_size: Optional[List[int]]
    primary_color: Optional[str]
    key_color: Optional[str]
    community_icon: Optional[str]
    banner_background_color: Optional[str]
    banner_background_image: Optional[str]
    header_title: Optional[str]
    moderators: List[str]
    approved_submitters: List[str]
    banned_users: List[str]
    muted_users: List[str]
    wiki_contributors: List[str]
    post_count_24h: int
    comment_count_24h: int
    growth_rate_weekly: float
    engagement_rate: float
    content_categories: List[str]
    trending_topics: List[str]


class RedditCrawler(PlatformCrawler):
    """
    Advanced Reddit crawler for community content monitoring and analysis.
    
    Features:
    - Subreddit discovery and analysis
    - Post and comment monitoring
    - User activity tracking
    - Sentiment and toxicity analysis
    - Trending topic detection
    - Moderation log tracking
    - Community engagement metrics
    - Cross-subreddit analysis
    - Vote pattern analysis
    - Content quality assessment
    """
    
    def __init__(self, config: CrawlerConfig, vector_matcher=None, 
                 client_id: str = None, client_secret: str = None, 
                 user_agent: str = None, username: str = None, password: str = None):
        super().__init__(config, vector_matcher)
        self.platform_name = "reddit"
        self.base_url = "https://reddit.com"
        self.api_base_url = "https://oauth.reddit.com"
        
        # Reddit API credentials
        self.client_id = client_id
        self.client_secret = client_secret
        self.user_agent = user_agent or "IA-Influencer-Agent:v1.0.0 (by /u/ia_influencer)"
        self.username = username
        self.password = password
        
        # Rate limiting (Reddit is moderate)
        self.requests_per_minute = 60
        self.min_delay = 1.0
        self.max_delay = 2.5
        
        # Content type mappings
        self.content_types = {
            'posts': self._crawl_posts,
            'comments': self._crawl_comments,
            'users': self._crawl_users,
            'subreddits': self._crawl_subreddits,
            'search': self._crawl_search,
            'trending': self._crawl_trending,
            'hot': self._crawl_hot,
            'new': self._crawl_new,
            'top': self._crawl_top
        }
        
        # Reddit instance (PRAW)
        self.reddit = None
        if self.client_id and self.client_secret:
            self.reddit = praw.Reddit(
                client_id=self.client_id,
                client_secret=self.client_secret,
                user_agent=self.user_agent,
                username=self.username,
                password=self.password
            )
        
        # Tracking
        self.request_count = 0
        self.last_request_time = 0
        self.monitored_subreddits = set()
        
        # Initialize session headers
        self._setup_session_headers()
    
    def _setup_session_headers(self):
        """Setup Reddit-specific headers"""
        self.session_headers.update({
            'Accept': 'application/json',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9',
            'Origin': 'https://reddit.com',
            'Referer': 'https://reddit.com/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': self.user_agent
        })
    
    async def search_content(self, query: str, content_type: str = "posts", 
                           max_results: int = 50, subreddit: str = None) -> List[CrawlerResult]:
        """
        Search for content on Reddit.
        
        Args:
            query: Search query
            content_type: Type of content to search for
            max_results: Maximum number of results
            subreddit: Specific subreddit to search in
            
        Returns:
            List of crawler results
        """
        try:
            await self._check_rate_limit()
            
            if content_type not in self.content_types:
                raise ValueError(f"Unsupported content type: {content_type}")
            
            # Execute search based on content type
            crawler_func = self.content_types[content_type]
            results = await crawler_func(query, max_results, subreddit)
            
            self.logger.info(f"Found {len(results)} Reddit {content_type} for query: {query}")
            return results
            
        except Exception as e:
            self.logger.error(f"Error searching Reddit content: {str(e)}")
            return []
    
    async def _crawl_posts(self, query: str, max_results: int, subreddit: str = None) -> List[CrawlerResult]:
        """Crawl Reddit posts/submissions"""
        try:
            results = []
            
            if not self.reddit:
                self.logger.error("Reddit instance not available")
                return []
            
            # Search posts
            if subreddit:
                # Search within specific subreddit
                subreddit_obj = self.reddit.subreddit(subreddit)
                submissions = subreddit_obj.search(query, limit=max_results)
            else:
                # Search across all Reddit
                submissions = self.reddit.subreddit("all").search(query, limit=max_results)
            
            for submission in submissions:
                # Parse submission data
                reddit_post = await self._parse_submission_data(submission)
                if reddit_post:
                    result = CrawlerResult(
                        url=f"https://reddit.com{submission.permalink}",
                        title=submission.title,
                        content=submission.selftext or submission.url,
                        metadata={
                            'post_data': asdict(reddit_post),
                            'platform': 'reddit',
                            'content_type': 'post',
                            'subreddit': submission.subreddit.display_name,
                            'author': submission.author.name if submission.author else '[deleted]',
                            'score': submission.score,
                            'upvote_ratio': submission.upvote_ratio,
                            'num_comments': submission.num_comments,
                            'is_self': submission.is_self,
                            'over_18': submission.over_18,
                            'gilded': submission.gilded,
                            'stickied': submission.stickied,
                            'distinguished': submission.distinguished
                        },
                        timestamp=reddit_post.created_utc,
                        similarity_score=0.0
                    )
                    results.append(result)
                    
                    # Rate limiting
                    await asyncio.sleep(random.uniform(self.min_delay, self.max_delay))
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error crawling Reddit posts: {str(e)}")
            return []
    
    async def _crawl_comments(self, query: str, max_results: int, subreddit: str = None) -> List[CrawlerResult]:
        """Crawl Reddit comments"""
        try:
            results = []
            
            if not self.reddit:
                return []
            
            # Get recent posts and search their comments
            if subreddit:
                subreddit_obj = self.reddit.subreddit(subreddit)
                submissions = subreddit_obj.new(limit=20)
            else:
                submissions = self.reddit.subreddit("all").new(limit=20)
            
            for submission in submissions:
                try:
                    submission.comments.replace_more(limit=0)
                    
                    for comment in submission.comments.list():
                        # Filter by query
                        if query and query.lower() not in comment.body.lower():
                            continue
                        
                        # Parse comment data
                        reddit_comment = await self._parse_comment_data(comment)
                        if reddit_comment:
                            result = CrawlerResult(
                                url=f"https://reddit.com{comment.permalink}",
                                title=f"Comment by {comment.author.name if comment.author else '[deleted]'}",
                                content=comment.body,
                                metadata={
                                    'comment_data': asdict(reddit_comment),
                                    'platform': 'reddit',
                                    'content_type': 'comment',
                                    'subreddit': comment.subreddit.display_name,
                                    'author': comment.author.name if comment.author else '[deleted]',
                                    'score': comment.score,
                                    'gilded': comment.gilded,
                                    'depth': comment.depth,
                                    'is_submitter': comment.is_submitter,
                                    'distinguished': comment.distinguished
                                },
                                timestamp=reddit_comment.created_utc,
                                similarity_score=0.0
                            )
                            results.append(result)
                            
                            if len(results) >= max_results:
                                return results
                    
                    # Rate limiting
                    await asyncio.sleep(random.uniform(self.min_delay, self.max_delay))
                    
                except prawcore.exceptions.Forbidden:
                    continue
                except Exception as e:
                    self.logger.error(f"Error processing submission comments: {str(e)}")
                    continue
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error crawling Reddit comments: {str(e)}")
            return []
    
    async def _crawl_users(self, query: str, max_results: int, subreddit: str = None) -> List[CrawlerResult]:
        """Crawl Reddit users"""
        try:
            results = []
            
            if not self.reddit:
                return []
            
            # Get recent posts and comments to find users
            seen_users = set()
            
            # Search through posts
            if subreddit:
                subreddit_obj = self.reddit.subreddit(subreddit)
                submissions = subreddit_obj.new(limit=50)
            else:
                submissions = self.reddit.subreddit("all").new(limit=50)
            
            for submission in submissions:
                if submission.author and submission.author.name not in seen_users:
                    # Filter by query
                    if query and query.lower() not in submission.author.name.lower():
                        continue
                    
                    seen_users.add(submission.author.name)
                    
                    # Get detailed user information
                    reddit_user = await self._get_detailed_user_info(submission.author.name)
                    if reddit_user:
                        result = CrawlerResult(
                            url=f"https://reddit.com/user/{submission.author.name}",
                            title=f"Reddit User: {submission.author.name}",
                            content=f"User: {submission.author.name} - {reddit_user.description or 'No description'}",
                            metadata={
                                'user_data': asdict(reddit_user),
                                'platform': 'reddit',
                                'content_type': 'user',
                                'comment_karma': reddit_user.comment_karma,
                                'link_karma': reddit_user.link_karma,
                                'total_karma': reddit_user.total_karma,
                                'is_gold': reddit_user.is_gold,
                                'is_mod': reddit_user.is_mod,
                                'verified': reddit_user.is_verified,
                                'profile_over_18': reddit_user.profile_over_18
                            },
                            timestamp=reddit_user.created_utc,
                            similarity_score=0.0
                        )
                        results.append(result)
                        
                        if len(results) >= max_results:
                            return results
                
                # Rate limiting
                await asyncio.sleep(random.uniform(self.min_delay, self.max_delay))
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error crawling Reddit users: {str(e)}")
            return []
    
    async def _crawl_subreddits(self, query: str, max_results: int, subreddit: str = None) -> List[CrawlerResult]:
        """Crawl Reddit subreddits"""
        try:
            results = []
            
            if not self.reddit:
                return []
            
            # Search for subreddits
            subreddits = self.reddit.subreddits.search(query, limit=max_results)
            
            for sub in subreddits:
                try:
                    # Get detailed subreddit information
                    reddit_subreddit = await self._get_detailed_subreddit_info(sub.display_name)
                    if reddit_subreddit:
                        result = CrawlerResult(
                            url=f"https://reddit.com/r/{sub.display_name}",
                            title=f"r/{sub.display_name}",
                            content=f"Subreddit: r/{sub.display_name} - {sub.public_description}",
                            metadata={
                                'subreddit_data': asdict(reddit_subreddit),
                                'platform': 'reddit',
                                'content_type': 'subreddit',
                                'subscribers': reddit_subreddit.subscribers,
                                'active_users': reddit_subreddit.accounts_active,
                                'over18': reddit_subreddit.over18,
                                'subreddit_type': reddit_subreddit.subreddit_type,
                                'submission_type': reddit_subreddit.submission_type,
                                'lang': reddit_subreddit.lang
                            },
                            timestamp=reddit_subreddit.created_utc,
                            similarity_score=0.0
                        )
                        results.append(result)
                    
                    # Rate limiting
                    await asyncio.sleep(random.uniform(self.min_delay, self.max_delay))
                    
                except prawcore.exceptions.Forbidden:
                    continue
                except Exception as e:
                    self.logger.error(f"Error processing subreddit {sub.display_name}: {str(e)}")
                    continue
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error crawling Reddit subreddits: {str(e)}")
            return []
    
    async def _crawl_search(self, query: str, max_results: int, subreddit: str = None) -> List[CrawlerResult]:
        """General Reddit search across all content types"""
        try:
            results = []
            
            # Search across different content types
            posts = await self._crawl_posts(query, max_results // 2, subreddit)
            comments = await self._crawl_comments(query, max_results // 4, subreddit)
            subreddits = await self._crawl_subreddits(query, max_results // 4, subreddit)
            
            results.extend(posts)
            results.extend(comments)
            results.extend(subreddits)
            
            return results[:max_results]
            
        except Exception as e:
            self.logger.error(f"Error performing Reddit search: {str(e)}")
            return []
    
    async def _crawl_trending(self, query: str, max_results: int, subreddit: str = None) -> List[CrawlerResult]:
        """Crawl trending content on Reddit"""
        try:
            results = []
            
            if not self.reddit:
                return []
            
            # Get trending/popular posts
            if subreddit:
                subreddit_obj = self.reddit.subreddit(subreddit)
                submissions = subreddit_obj.hot(limit=max_results)
            else:
                submissions = self.reddit.subreddit("popular").hot(limit=max_results)
            
            for submission in submissions:
                # Filter by query if provided
                if query and query.lower() not in submission.title.lower() and query.lower() not in submission.selftext.lower():
                    continue
                
                reddit_post = await self._parse_submission_data(submission)
                if reddit_post:
                    result = CrawlerResult(
                        url=f"https://reddit.com{submission.permalink}",
                        title=f"[TRENDING] {submission.title}",
                        content=submission.selftext or submission.url,
                        metadata={
                            'post_data': asdict(reddit_post),
                            'platform': 'reddit',
                            'content_type': 'trending_post',
                            'trend_source': 'hot',
                            'position': len(results) + 1
                        },
                        timestamp=reddit_post.created_utc,
                        similarity_score=0.0
                    )
                    results.append(result)
                
                # Rate limiting
                await asyncio.sleep(random.uniform(self.min_delay, self.max_delay))
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error crawling Reddit trending: {str(e)}")
            return []
    
    async def _crawl_hot(self, query: str, max_results: int, subreddit: str = None) -> List[CrawlerResult]:
        """Crawl hot posts on Reddit"""
        return await self._crawl_by_sort("hot", query, max_results, subreddit)
    
    async def _crawl_new(self, query: str, max_results: int, subreddit: str = None) -> List[CrawlerResult]:
        """Crawl new posts on Reddit"""
        return await self._crawl_by_sort("new", query, max_results, subreddit)
    
    async def _crawl_top(self, query: str, max_results: int, subreddit: str = None) -> List[CrawlerResult]:
        """Crawl top posts on Reddit"""
        return await self._crawl_by_sort("top", query, max_results, subreddit)
    
    async def _crawl_by_sort(self, sort_type: str, query: str, max_results: int, subreddit: str = None) -> List[CrawlerResult]:
        """Crawl posts by sort type"""
        try:
            results = []
            
            if not self.reddit:
                return []
            
            # Get posts by sort type
            if subreddit:
                subreddit_obj = self.reddit.subreddit(subreddit)
            else:
                subreddit_obj = self.reddit.subreddit("all")
            
            if sort_type == "hot":
                submissions = subreddit_obj.hot(limit=max_results)
            elif sort_type == "new":
                submissions = subreddit_obj.new(limit=max_results)
            elif sort_type == "top":
                submissions = subreddit_obj.top("day", limit=max_results)
            else:
                submissions = subreddit_obj.hot(limit=max_results)
            
            for submission in submissions:
                # Filter by query if provided
                if query and query.lower() not in submission.title.lower() and query.lower() not in submission.selftext.lower():
                    continue
                
                reddit_post = await self._parse_submission_data(submission)
                if reddit_post:
                    result = CrawlerResult(
                        url=f"https://reddit.com{submission.permalink}",
                        title=f"[{sort_type.upper()}] {submission.title}",
                        content=submission.selftext or submission.url,
                        metadata={
                            'post_data': asdict(reddit_post),
                            'platform': 'reddit',
                            'content_type': f'{sort_type}_post',
                            'sort_type': sort_type,
                            'position': len(results) + 1
                        },
                        timestamp=reddit_post.created_utc,
                        similarity_score=0.0
                    )
                    results.append(result)
                
                # Rate limiting
                await asyncio.sleep(random.uniform(self.min_delay, self.max_delay))
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error crawling Reddit {sort_type}: {str(e)}")
            return []
    
    # Helper methods
    
    async def _parse_submission_data(self, submission) -> Optional[RedditPost]:
        """Parse submission data from PRAW"""
        try:
            created_utc = datetime.utcfromtimestamp(submission.created_utc)
            edited = None
            if submission.edited:
                edited = datetime.utcfromtimestamp(submission.edited)
            
            reddit_post = RedditPost(
                post_id=submission.id,
                title=submission.title,
                selftext=submission.selftext,
                selftext_html=getattr(submission, 'selftext_html', None),
                url=submission.url,
                permalink=submission.permalink,
                subreddit=submission.subreddit.display_name,
                subreddit_id=submission.subreddit.id,
                author=submission.author.name if submission.author else '[deleted]',
                author_id=submission.author.id if submission.author else None,
                author_flair_text=getattr(submission, 'author_flair_text', None),
                author_flair_css_class=getattr(submission, 'author_flair_css_class', None),
                link_flair_text=getattr(submission, 'link_flair_text', None),
                link_flair_css_class=getattr(submission, 'link_flair_css_class', None),
                created_utc=created_utc,
                score=submission.score,
                upvote_ratio=submission.upvote_ratio,
                ups=submission.ups,
                downs=getattr(submission, 'downs', 0),
                num_comments=submission.num_comments,
                num_crossposts=getattr(submission, 'num_crossposts', 0),
                num_reports=getattr(submission, 'num_reports', 0),
                over_18=submission.over_18,
                spoiler=submission.spoiler,
                locked=submission.locked,
                stickied=submission.stickied,
                pinned=getattr(submission, 'pinned', False),
                archived=submission.archived,
                is_self=submission.is_self,
                is_video=submission.is_video,
                is_original_content=getattr(submission, 'is_original_content', False),
                is_reddit_media_domain=getattr(submission, 'is_reddit_media_domain', False),
                is_meta=getattr(submission, 'is_meta', False),
                distinguished=submission.distinguished,
                edited=edited,
                gilded=submission.gilded,
                total_awards_received=getattr(submission, 'total_awards_received', 0),
                all_awardings=getattr(submission, 'all_awardings', []),
                treatment_tags=getattr(submission, 'treatment_tags', []),
                removed_by_category=getattr(submission, 'removed_by_category', None),
                banned_by=getattr(submission, 'banned_by', None),
                removal_reason=getattr(submission, 'removal_reason', None),
                domain=submission.domain,
                thumbnail=getattr(submission, 'thumbnail', None),
                thumbnail_width=getattr(submission, 'thumbnail_width', None),
                thumbnail_height=getattr(submission, 'thumbnail_height', None),
                preview=getattr(submission, 'preview', None),
                media=getattr(submission, 'media', None),
                media_embed=getattr(submission, 'media_embed', None),
                secure_media=getattr(submission, 'secure_media', None),
                secure_media_embed=getattr(submission, 'secure_media_embed', None),
                crosspost_parent=getattr(submission, 'crosspost_parent', None),
                crosspost_parent_list=getattr(submission, 'crosspost_parent_list', []),
                view_count=getattr(submission, 'view_count', None),
                clicked=getattr(submission, 'clicked', False),
                saved=getattr(submission, 'saved', False),
                hidden=getattr(submission, 'hidden', False),
                contest_mode=getattr(submission, 'contest_mode', False),
                suggested_sort=getattr(submission, 'suggested_sort', None),
                user_reports=getattr(submission, 'user_reports', []),
                mod_reports=getattr(submission, 'mod_reports', []),
                mod_note=getattr(submission, 'mod_note', None),
                mod_reason_title=getattr(submission, 'mod_reason_title', None),
                mod_reason_by=getattr(submission, 'mod_reason_by', None),
                post_hint=getattr(submission, 'post_hint', None),
                content_categories=getattr(submission, 'content_categories', []),
                discussion_type=getattr(submission, 'discussion_type', None),
                sentiment_score=None,  # Would need sentiment analysis
                engagement_score=self._calculate_engagement_score(submission),
                trending_score=self._calculate_trending_score(submission)
            )
            
            return reddit_post
            
        except Exception as e:
            self.logger.error(f"Error parsing submission data: {str(e)}")
            return None
    
    async def _parse_comment_data(self, comment) -> Optional[RedditComment]:
        """Parse comment data from PRAW"""
        try:
            created_utc = datetime.utcfromtimestamp(comment.created_utc)
            edited = None
            if comment.edited:
                edited = datetime.utcfromtimestamp(comment.edited)
            
            # Get reply IDs
            replies = []
            if hasattr(comment, 'replies') and comment.replies:
                try:
                    for reply in comment.replies:
                        if hasattr(reply, 'id'):
                            replies.append(reply.id)
                except:
                    pass
            
            reddit_comment = RedditComment(
                comment_id=comment.id,
                post_id=comment.submission.id,
                parent_id=comment.parent_id,
                subreddit=comment.subreddit.display_name,
                subreddit_id=comment.subreddit.id,
                author=comment.author.name if comment.author else '[deleted]',
                author_id=comment.author.id if comment.author else None,
                author_flair_text=getattr(comment, 'author_flair_text', None),
                author_flair_css_class=getattr(comment, 'author_flair_css_class', None),
                body=comment.body,
                body_html=getattr(comment, 'body_html', ''),
                created_utc=created_utc,
                score=comment.score,
                ups=comment.ups,
                downs=getattr(comment, 'downs', 0),
                likes=getattr(comment, 'likes', None),
                replies=replies,
                depth=getattr(comment, 'depth', 0),
                permalink=comment.permalink,
                distinguished=comment.distinguished,
                edited=edited,
                gilded=comment.gilded,
                total_awards_received=getattr(comment, 'total_awards_received', 0),
                all_awardings=getattr(comment, 'all_awardings', []),
                stickied=comment.stickied,
                is_submitter=comment.is_submitter,
                score_hidden=getattr(comment, 'score_hidden', False),
                archived=getattr(comment, 'archived', False),
                locked=getattr(comment, 'locked', False),
                saved=getattr(comment, 'saved', False),
                collapsed=getattr(comment, 'collapsed', False),
                collapsed_reason=getattr(comment, 'collapsed_reason', None),
                associated_award=getattr(comment, 'associated_award', None),
                unrepliable_reason=getattr(comment, 'unrepliable_reason', None),
                treatment_tags=getattr(comment, 'treatment_tags', []),
                user_reports=getattr(comment, 'user_reports', []),
                mod_reports=getattr(comment, 'mod_reports', []),
                removal_reason=getattr(comment, 'removal_reason', None),
                banned_by=getattr(comment, 'banned_by', None),
                approved_by=getattr(comment, 'approved_by', None),
                mod_note=getattr(comment, 'mod_note', None),
                mod_reason_title=getattr(comment, 'mod_reason_title', None),
                mod_reason_by=getattr(comment, 'mod_reason_by', None),
                sentiment_score=None,  # Would need sentiment analysis
                toxicity_score=None,  # Would need toxicity analysis
                spam_score=None  # Would need spam analysis
            )
            
            return reddit_comment
            
        except Exception as e:
            self.logger.error(f"Error parsing comment data: {str(e)}")
            return None
    
    async def _get_detailed_user_info(self, username: str) -> Optional[RedditUser]:
        """Get detailed user information"""
        try:
            user = self.reddit.redditor(username)
            created_utc = datetime.utcfromtimestamp(user.created_utc)
            
            # Calculate karma breakdown (would need additional API calls)
            total_karma = user.comment_karma + user.link_karma
            
            reddit_user = RedditUser(
                username=user.name,
                user_id=user.id,
                created_utc=created_utc,
                comment_karma=user.comment_karma,
                link_karma=user.link_karma,
                total_karma=total_karma,
                is_gold=getattr(user, 'is_gold', False),
                is_mod=getattr(user, 'is_mod', False),
                is_verified=getattr(user, 'verified', False),
                has_verified_email=getattr(user, 'has_verified_email', False),
                is_employee=getattr(user, 'is_employee', False),
                is_suspended=getattr(user, 'is_suspended', False),
                subreddit=getattr(user, 'subreddit', None),
                icon_img=getattr(user, 'icon_img', None),
                snoovatar_img=getattr(user, 'snoovatar_img', None),
                profile_over_18=getattr(user, 'subreddit', {}).get('over_18', False),
                accept_followers=getattr(user, 'accept_followers', True),
                accept_pms=getattr(user, 'accept_pms', 'everyone'),
                accept_chats=getattr(user, 'accept_chats', 'everyone'),
                hide_from_robots=getattr(user, 'hide_from_robots', False),
                description=getattr(user, 'subreddit', {}).get('public_description', None),
                public_description=getattr(user, 'subreddit', {}).get('public_description', None),
                awards_received=[],  # Would need additional API calls
                awards_given=0,  # Would need additional API calls
                premium_since=None,  # Would need additional API calls
                coins=0,  # Not accessible
                has_gold_subscription=getattr(user, 'is_gold', False),
                num_friends=0,  # Not accessible
                features={},  # Would need additional API calls
                can_edit_name=False,  # Would need additional API calls
                verified=getattr(user, 'verified', False),
                new_modmail_exists=False,  # Would need additional API calls
                pref_show_snoovatar=True,  # Default
                name=user.name,
                created=created_utc,
                link_karma_breakdown={},  # Would need additional API calls
                comment_karma_breakdown={},  # Would need additional API calls
                total_comment_karma=user.comment_karma,
                total_link_karma=user.link_karma,
                submission_count=0,  # Would need calculation
                comment_count=0,  # Would need calculation
                subreddits_moderated=[],  # Would need additional API calls
                favorite_subreddits=[],  # Would need additional API calls
                recent_activity_score=0.0  # Would need calculation
            )
            
            return reddit_user
            
        except Exception as e:
            self.logger.error(f"Error getting detailed user info: {str(e)}")
            return None
    
    async def _get_detailed_subreddit_info(self, subreddit_name: str) -> Optional[RedditSubreddit]:
        """Get detailed subreddit information"""
        try:
            subreddit = self.reddit.subreddit(subreddit_name)
            created_utc = datetime.utcfromtimestamp(subreddit.created_utc)
            
            # Get rules
            rules = []
            try:
                for rule in subreddit.rules:
                    rules.append({
                        'short_name': rule.short_name,
                        'description': rule.description,
                        'kind': rule.kind,
                        'priority': rule.priority
                    })
            except:
                pass
            
            reddit_subreddit = RedditSubreddit(
                subreddit_id=subreddit.id,
                name=subreddit.display_name,
                display_name=subreddit.display_name,
                display_name_prefixed=subreddit.display_name_prefixed,
                title=subreddit.title,
                description=subreddit.description,
                description_html=getattr(subreddit, 'description_html', ''),
                public_description=subreddit.public_description,
                rules=rules,
                created_utc=created_utc,
                subscribers=subreddit.subscribers,
                accounts_active=getattr(subreddit, 'accounts_active', 0),
                accounts_active_is_fuzzed=getattr(subreddit, 'accounts_active_is_fuzzed', False),
                active_user_count=getattr(subreddit, 'active_user_count', 0),
                over18=subreddit.over18,
                lang=getattr(subreddit, 'lang', 'en'),
                whitelist_status=getattr(subreddit, 'whitelist_status', None),
                url=subreddit.url,
                quarantine=getattr(subreddit, 'quarantine', False),
                allow_discovery=getattr(subreddit, 'allow_discovery', True),
                subreddit_type=subreddit.subreddit_type,
                submission_type=getattr(subreddit, 'submission_type', 'any'),
                can_assign_link_flair=getattr(subreddit, 'can_assign_link_flair', False),
                can_assign_user_flair=getattr(subreddit, 'can_assign_user_flair', False),
                allow_images=getattr(subreddit, 'allow_images', True),
                allow_videos=getattr(subreddit, 'allow_videos', True),
                allow_polls=getattr(subreddit, 'allow_polls', False),
                allow_galleries=getattr(subreddit, 'allow_galleries', False),
                allow_predictions=getattr(subreddit, 'allow_predictions', False),
                wiki_enabled=getattr(subreddit, 'wiki_enabled', False),
                comment_score_hide_mins=getattr(subreddit, 'comment_score_hide_mins', 0),
                suggested_comment_sort=getattr(subreddit, 'suggested_comment_sort', None),
                spoilers_enabled=getattr(subreddit, 'spoilers_enabled', False),
                original_content_tag_enabled=getattr(subreddit, 'original_content_tag_enabled', False),
                submit_text=getattr(subreddit, 'submit_text', ''),
                submit_text_html=getattr(subreddit, 'submit_text_html', ''),
                user_flair_enabled_in_sr=getattr(subreddit, 'user_flair_enabled_in_sr', False),
                user_flair_position=getattr(subreddit, 'user_flair_position', 'right'),
                user_flair_type=getattr(subreddit, 'user_flair_type', 'text'),
                link_flair_enabled=getattr(subreddit, 'link_flair_enabled', False),
                link_flair_position=getattr(subreddit, 'link_flair_position', 'left'),
                emojis_enabled=getattr(subreddit, 'emojis_enabled', False),
                banner_img=getattr(subreddit, 'banner_img', None),
                banner_size=getattr(subreddit, 'banner_size', None),
                mobile_banner_image=getattr(subreddit, 'mobile_banner_image', None),
                icon_img=getattr(subreddit, 'icon_img', None),
                icon_size=getattr(subreddit, 'icon_size', None),
                header_img=getattr(subreddit, 'header_img', None),
                header_size=getattr(subreddit, 'header_size', None),
                primary_color=getattr(subreddit, 'primary_color', None),
                key_color=getattr(subreddit, 'key_color', None),
                community_icon=getattr(subreddit, 'community_icon', None),
                banner_background_color=getattr(subreddit, 'banner_background_color', None),
                banner_background_image=getattr(subreddit, 'banner_background_image', None),
                header_title=getattr(subreddit, 'header_title', None),
                moderators=[],  # Would need additional API calls
                approved_submitters=[],  # Would need additional API calls
                banned_users=[],  # Would need additional API calls
                muted_users=[],  # Would need additional API calls
                wiki_contributors=[],  # Would need additional API calls
                post_count_24h=0,  # Would need calculation
                comment_count_24h=0,  # Would need calculation
                growth_rate_weekly=0.0,  # Would need calculation
                engagement_rate=0.0,  # Would need calculation
                content_categories=[],  # Would need analysis
                trending_topics=[]  # Would need analysis
            )
            
            return reddit_subreddit
            
        except Exception as e:
            self.logger.error(f"Error getting detailed subreddit info: {str(e)}")
            return None
    
    def _calculate_engagement_score(self, submission) -> float:
        """Calculate engagement score for a submission"""
        try:
            # Simple engagement calculation
            score = submission.score
            comments = submission.num_comments
            ratio = submission.upvote_ratio
            
            # Weight comments more heavily as they indicate engagement
            engagement = (score * ratio) + (comments * 2)
            
            # Normalize by age (hours since creation)
            age_hours = (datetime.utcnow().timestamp() - submission.created_utc) / 3600
            if age_hours > 0:
                engagement = engagement / max(age_hours, 1)
            
            return float(engagement)
            
        except Exception as e:
            self.logger.error(f"Error calculating engagement score: {str(e)}")
            return 0.0
    
    def _calculate_trending_score(self, submission) -> float:
        """Calculate trending score for a submission"""
        try:
            # Trending calculation based on velocity
            score = submission.score
            comments = submission.num_comments
            ratio = submission.upvote_ratio
            
            # Age in hours
            age_hours = (datetime.utcnow().timestamp() - submission.created_utc) / 3600
            
            # Trending score favors recent high-engagement content
            if age_hours > 0 and age_hours < 24:  # Only consider recent content
                velocity = (score + comments) / age_hours
                trending = velocity * ratio
                return float(trending)
            
            return 0.0
            
        except Exception as e:
            self.logger.error(f"Error calculating trending score: {str(e)}")
            return 0.0
    
    async def _check_rate_limit(self):
        """Check and enforce rate limiting"""
        try:
            current_time = time.time()
            time_since_last = current_time - self.last_request_time
            
            # Enforce minimum delay between requests
            min_interval = 60.0 / self.requests_per_minute
            if time_since_last < min_interval:
                await asyncio.sleep(min_interval - time_since_last)
            
            self.last_request_time = current_time
            self.request_count += 1
            
        except Exception as e:
            self.logger.error(f"Error in rate limiting: {str(e)}")
    
    async def extract_content_metadata(self, url: str) -> Dict[str, Any]:
        """Extract metadata from Reddit content"""
        try:
            # Parse Reddit URL
            parsed_url = urlparse(url)
            path_parts = parsed_url.path.strip('/').split('/')
            
            metadata = {
                'platform': 'reddit',
                'url': url,
                'extracted_at': datetime.utcnow().isoformat()
            }
            
            if 'r' in path_parts:
                idx = path_parts.index('r')
                if len(path_parts) > idx + 1:
                    subreddit_name = path_parts[idx + 1]
                    metadata['subreddit'] = subreddit_name
                    
                    if 'comments' in path_parts:
                        comment_idx = path_parts.index('comments')
                        if len(path_parts) > comment_idx + 1:
                            post_id = path_parts[comment_idx + 1]
                            metadata.update({
                                'post_id': post_id,
                                'content_type': 'post'
                            })
                            
                            if len(path_parts) > comment_idx + 3:
                                comment_id = path_parts[comment_idx + 3]
                                metadata.update({
                                    'comment_id': comment_id,
                                    'content_type': 'comment'
                                })
                    else:
                        metadata['content_type'] = 'subreddit'
            
            elif 'user' in path_parts or 'u' in path_parts:
                user_idx = path_parts.index('user') if 'user' in path_parts else path_parts.index('u')
                if len(path_parts) > user_idx + 1:
                    username = path_parts[user_idx + 1]
                    metadata.update({
                        'username': username,
                        'content_type': 'user'
                    })
            
            return metadata
            
        except Exception as e:
            self.logger.error(f"Error extracting Reddit metadata: {str(e)}")
            return {'error': str(e)}
    
    def get_platform_info(self) -> Dict[str, Any]:
        """Get Reddit platform information"""
        return {
            'platform_name': 'Reddit',
            'base_url': self.base_url,
            'api_base_url': self.api_base_url,
            'supported_content_types': list(self.content_types.keys()),
            'rate_limits': {
                'requests_per_minute': self.requests_per_minute,
                'min_delay': self.min_delay,
                'max_delay': self.max_delay
            },
            'features': [
                'Subreddit discovery and analysis',
                'Post and comment monitoring',
                'User activity tracking',
                'Sentiment and toxicity analysis',
                'Trending topic detection',
                'Moderation log tracking',
                'Community engagement metrics',
                'Cross-subreddit analysis',
                'Vote pattern analysis',
                'Content quality assessment'
            ],
            'authentication': {
                'required': True,
                'type': 'OAuth2 Client Credentials',
                'scope': 'Read-only access'
            },
            'limitations': [
                'Rate limited by Reddit API',
                'Some user data requires authentication',
                'Private subreddits not accessible',
                'Deleted content not retrievable'
            ]
        }
