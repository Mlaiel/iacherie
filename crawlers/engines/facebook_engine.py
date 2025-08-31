"""
Facebook Crawling Engine
=======================

Advanced Facebook crawler for content discovery, analytics, and business insights.
Handles posts, pages, groups, and marketplace data extraction.

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
from urllib.parse import urljoin, urlparse, parse_qs

import aiohttp
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.page import Page
from facebook_business.adobjects.post import Post
from facebook_business.adobjects.user import User
import facebook

from ..core.base_engine import BaseCrawlerEngine
from ..core.exceptions import (
    CrawlerError, 
    RateLimitError, 
    AuthenticationError,
    ContentNotFoundError,
    PrivacyRestrictedError
)
from ..utils.rate_limiter import RateLimiter
from ..utils.cache_manager import CacheManager
from ..utils.proxy_manager import ProxyManager
from ..models.content_models import SocialPost, SocialProfile, BusinessProfile
from ...core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


@dataclass
class FacebookPostData:
    """Facebook post data structure"""
    post_id: str
    message: str
    story: str
    created_time: datetime
    updated_time: datetime
    type: str  # status, photo, video, link, etc.
    status_type: str
    permalink_url: str
    shares: Dict[str, Any]
    reactions: Dict[str, int]  # like, love, wow, haha, sad, angry
    comments: Dict[str, Any]
    attachments: List[Dict[str, Any]]
    privacy: Dict[str, Any]
    targeting: Dict[str, Any]
    insights: Dict[str, Any]
    place: Optional[Dict[str, Any]] = None
    tagged_users: List[str] = None
    hashtags: List[str] = None
    mentions: List[str] = None
    is_published: bool = True
    is_popular: bool = False
    engagement_rate: float = 0.0
    reach: int = 0
    impressions: int = 0


@dataclass
class FacebookPageData:
    """Facebook page data structure"""
    page_id: str
    name: str
    username: str
    about: str
    category: str
    category_list: List[Dict[str, Any]]
    description: str
    website: str
    phone: str
    emails: List[str]
    location: Dict[str, Any]
    hours: Dict[str, Any]
    fan_count: int
    followers_count: int
    checkins: int
    talking_about_count: int
    were_here_count: int
    link: str
    picture: Dict[str, Any]
    cover: Dict[str, Any]
    business: Dict[str, Any]
    verification_status: str
    is_verified: bool
    is_published: bool
    single_line_address: str
    posts: List[FacebookPostData] = None
    insights: Dict[str, Any] = None
    rating_count: int = 0
    overall_star_rating: float = 0.0
    page_token: Optional[str] = None


@dataclass
class FacebookGroupData:
    """Facebook group data structure"""
    group_id: str
    name: str
    description: str
    privacy: str  # CLOSED, PUBLIC, SECRET
    member_count: int
    member_request_count: int
    cover: Dict[str, Any]
    picture: Dict[str, Any]
    icon: str
    updated_time: datetime
    email: str
    venue: Dict[str, Any]
    owner: Dict[str, Any]
    administrators: List[Dict[str, Any]]
    posts: List[FacebookPostData] = None
    insights: Dict[str, Any] = None
    rules: List[str] = None
    tags: List[str] = None
    is_archived: bool = False


@dataclass
class FacebookBusinessData:
    """Facebook business data structure"""
    business_id: str
    name: str
    primary_page: Dict[str, Any]
    accounts: List[Dict[str, Any]]
    ad_accounts: List[Dict[str, Any]]
    apps: List[Dict[str, Any]]
    managed_businesses: List[Dict[str, Any]]
    owned_businesses: List[Dict[str, Any]]
    client_businesses: List[Dict[str, Any]]
    business_users: List[Dict[str, Any]]
    system_users: List[Dict[str, Any]]
    pending_users: List[Dict[str, Any]]
    verification_status: str
    is_verified: bool
    insights: Dict[str, Any] = None
    revenue_data: Dict[str, Any] = None
    advertising_spend: Dict[str, Any] = None


class FacebookCrawlerEngine(BaseCrawlerEngine):
    """
    Advanced Facebook crawler engine with comprehensive API integration.
    
    Features:
    - Graph API integration for official data access
    - Selenium fallback for public content
    - Business Manager API for enterprise features
    - Real-time engagement tracking
    - Privacy-aware content collection
    - Advanced analytics and insights
    - Rate limiting and quota management
    - Content classification and filtering
    """

    def __init__(self, 
                 access_token: Optional[str] = None,
                 app_id: Optional[str] = None,
                 app_secret: Optional[str] = None,
                 use_selenium: bool = True,
                 proxy_config: Optional[Dict] = None,
                 rate_limit_config: Optional[Dict] = None):
        """
        Initialize Facebook crawler engine.
        
        Args:
            access_token: Facebook Graph API access token
            app_id: Facebook app ID
            app_secret: Facebook app secret
            use_selenium: Whether to use Selenium for scraping
            proxy_config: Proxy configuration
            rate_limit_config: Rate limiting configuration
        """
        super().__init__()
        
        # API Configuration
        self.access_token = access_token or settings.FACEBOOK_ACCESS_TOKEN
        self.app_id = app_id or settings.FACEBOOK_APP_ID
        self.app_secret = app_secret or settings.FACEBOOK_APP_SECRET
        
        # Initialize Facebook API
        if self.access_token:
            try:
                self.graph = facebook.GraphAPI(access_token=self.access_token, version="18.0")
                if self.app_id and self.app_secret:
                    FacebookAdsApi.init(self.app_id, self.app_secret, self.access_token)
            except Exception as e:
                logger.warning(f"Failed to initialize Facebook API: {e}")
                self.graph = None
        
        # Selenium setup
        self.use_selenium = use_selenium
        self.driver = None
        
        # Rate limiting
        rate_config = rate_limit_config or {
            'requests_per_hour': 600,  # Facebook Graph API limit
            'requests_per_day': 7200,
            'burst_limit': 100
        }
        self.rate_limiter = RateLimiter(**rate_config)
        
        # Cache manager
        self.cache_manager = CacheManager(
            cache_type='redis',
            ttl=3600,  # 1 hour cache
            key_prefix='facebook_'
        )
        
        # Proxy manager
        if proxy_config:
            self.proxy_manager = ProxyManager(proxy_config)
        else:
            self.proxy_manager = None

    async def authenticate(self) -> bool:
        """Authenticate with Facebook API"""



        try:
            if not self.graph:
                return False
            
            # Test API access
            me = self.graph.get_object('me')
            logger.info(f"Authenticated as Facebook user: {me.get('name', 'Unknown')}")
            return True
        except Exception as e:
            logger.error(f"Facebook authentication failed: {e}")
            return False

    async def search_posts(self, 
                          query: str, 
                          limit: int = 100,
                          post_type: Optional[str] = None,
                          date_range: Optional[tuple] = None) -> List[FacebookPostData]:
        """
        Search for Facebook posts by query.
        
        Args:
            query: Search query
            limit: Maximum number of posts to return
            post_type: Type of posts to search (status, photo, video, etc.)
            date_range: Date range tuple (start_date, end_date)
        
        Returns:
            List of FacebookPostData objects
        """
        cache_key = f"search_posts_{hashlib.md5(query.encode()).hexdigest()}_{limit}"
        cached_result = await self.cache_manager.get(cache_key)
        if cached_result:
            return [FacebookPostData(**post) for post in cached_result]

        posts = []
        
        try:
            await self.rate_limiter.acquire()
            
            if self.graph:
                # Use Graph API for search
                search_results = self.graph.search(
                    type='post',
                    q=query,
                    limit=limit,
                    fields='id,message,story,created_time,updated_time,type,status_type,'
                           'permalink_url,shares,reactions.summary(total_count).limit(0),'
                           'comments.summary(total_count).limit(0),attachments,privacy,'
                           'place,insights'
                )
                
                for post_data in search_results.get('data', []):
                    post = await self._process_post_data(post_data)
                    if post and self._filter_post(post, post_type, date_range):
                        posts.append(post)
            
            else:
                # Fallback to Selenium scraping
                posts = await self._scrape_posts_selenium(query, limit, post_type, date_range)
            
            # Cache results
            await self.cache_manager.set(
                cache_key, 
                [asdict(post) for post in posts]
            )
            
        except Exception as e:
            logger.error(f"Error searching Facebook posts: {e}")
            raise CrawlerError(f"Facebook post search failed: {e}")
        
        return posts

    async def get_page_info(self, page_id: str) -> FacebookPageData:
        """
        Get comprehensive Facebook page information.
        
        Args:
            page_id: Facebook page ID or username
        
        Returns:
            FacebookPageData object
        """
        cache_key = f"page_info_{page_id}"
        cached_result = await self.cache_manager.get(cache_key)
        if cached_result:
            return FacebookPageData(**cached_result)

        try:
            await self.rate_limiter.acquire()
            
            if self.graph:
                page_data = self.graph.get_object(
                    page_id,
                    fields='id,name,username,about,category,category_list,description,'
                           'website,phone,emails,location,hours,fan_count,followers_count,'
                           'checkins,talking_about_count,were_here_count,link,picture,'
                           'cover,business,verification_status,is_verified,is_published,'
                           'single_line_address,rating_count,overall_star_rating'
                )
                
                # Get page insights if available
                try:
                    insights = self.graph.get_connections(
                        page_id,
                        'insights',
                        metric='page_fans,page_fan_adds,page_fan_removes,page_impressions,'
                               'page_reach,page_actions_post_reactions_total'
                    )
                    page_data['insights'] = insights
                except:
                    page_data['insights'] = {}
                
                page = FacebookPageData(
                    page_id=page_data.get('id'),
                    name=page_data.get('name', ''),
                    username=page_data.get('username', ''),
                    about=page_data.get('about', ''),
                    category=page_data.get('category', ''),
                    category_list=page_data.get('category_list', []),
                    description=page_data.get('description', ''),
                    website=page_data.get('website', ''),
                    phone=page_data.get('phone', ''),
                    emails=page_data.get('emails', []),
                    location=page_data.get('location', {}),
                    hours=page_data.get('hours', {}),
                    fan_count=page_data.get('fan_count', 0),
                    followers_count=page_data.get('followers_count', 0),
                    checkins=page_data.get('checkins', 0),
                    talking_about_count=page_data.get('talking_about_count', 0),
                    were_here_count=page_data.get('were_here_count', 0),
                    link=page_data.get('link', ''),
                    picture=page_data.get('picture', {}),
                    cover=page_data.get('cover', {}),
                    business=page_data.get('business', {}),
                    verification_status=page_data.get('verification_status', ''),
                    is_verified=page_data.get('is_verified', False),
                    is_published=page_data.get('is_published', True),
                    single_line_address=page_data.get('single_line_address', ''),
                    rating_count=page_data.get('rating_count', 0),
                    overall_star_rating=page_data.get('overall_star_rating', 0.0),
                    insights=page_data.get('insights', {})
                )
                
                # Cache result
                await self.cache_manager.set(cache_key, asdict(page))
                
                return page
            
            else:
                raise AuthenticationError("Facebook Graph API not available")
        
        except Exception as e:
            logger.error(f"Error getting Facebook page info: {e}")
            raise CrawlerError(f"Facebook page info retrieval failed: {e}")

    async def get_page_posts(self, 
                           page_id: str, 
                           limit: int = 100,
                           since: Optional[datetime] = None,
                           until: Optional[datetime] = None) -> List[FacebookPostData]:
        """
        Get posts from a Facebook page.
        
        Args:
            page_id: Facebook page ID or username
            limit: Maximum number of posts to return
            since: Start date for post retrieval
            until: End date for post retrieval
        
        Returns:
            List of FacebookPostData objects
        """
        cache_key = f"page_posts_{page_id}_{limit}_{since}_{until}"
        cached_result = await self.cache_manager.get(cache_key)
        if cached_result:
            return [FacebookPostData(**post) for post in cached_result]

        posts = []
        
        try:
            await self.rate_limiter.acquire()
            
            if self.graph:
                # Build parameters
                params = {
                    'fields': 'id,message,story,created_time,updated_time,type,status_type,'
                             'permalink_url,shares,reactions.summary(total_count).limit(0),'
                             'comments.summary(total_count).limit(0),attachments,privacy,'
                             'place,insights',
                    'limit': limit
                }
                
                if since:
                    params['since'] = since.isoformat()
                if until:
                    params['until'] = until.isoformat()
                
                page_posts = self.graph.get_connections(page_id, 'posts', **params)
                
                for post_data in page_posts.get('data', []):
                    post = await self._process_post_data(post_data)
                    if post:
                        posts.append(post)
                
                # Cache results
                await self.cache_manager.set(
                    cache_key, 
                    [asdict(post) for post in posts]
                )
            
            else:
                raise AuthenticationError("Facebook Graph API not available")
        
        except Exception as e:
            logger.error(f"Error getting Facebook page posts: {e}")
            raise CrawlerError(f"Facebook page posts retrieval failed: {e}")
        
        return posts

    async def get_group_info(self, group_id: str) -> FacebookGroupData:
        """
        Get Facebook group information.
        
        Args:
            group_id: Facebook group ID
        
        Returns:
            FacebookGroupData object
        """
        cache_key = f"group_info_{group_id}"
        cached_result = await self.cache_manager.get(cache_key)
        if cached_result:
            return FacebookGroupData(**cached_result)

        try:
            await self.rate_limiter.acquire()
            
            if self.graph:
                group_data = self.graph.get_object(
                    group_id,
                    fields='id,name,description,privacy,member_count,member_request_count,'
                           'cover,picture,icon,updated_time,email,venue,owner'
                )
                
                group = FacebookGroupData(
                    group_id=group_data.get('id'),
                    name=group_data.get('name', ''),
                    description=group_data.get('description', ''),
                    privacy=group_data.get('privacy', ''),
                    member_count=group_data.get('member_count', 0),
                    member_request_count=group_data.get('member_request_count', 0),
                    cover=group_data.get('cover', {}),
                    picture=group_data.get('picture', {}),
                    icon=group_data.get('icon', ''),
                    updated_time=datetime.fromisoformat(
                        group_data.get('updated_time', datetime.now().isoformat())
                    ),
                    email=group_data.get('email', ''),
                    venue=group_data.get('venue', {}),
                    owner=group_data.get('owner', {}),
                    administrators=[]
                )
                
                # Cache result
                await self.cache_manager.set(cache_key, asdict(group))
                
                return group
            
            else:
                raise AuthenticationError("Facebook Graph API not available")
        
        except Exception as e:
            logger.error(f"Error getting Facebook group info: {e}")
            raise CrawlerError(f"Facebook group info retrieval failed: {e}")

    async def monitor_content(self, 
                            targets: List[str],
                            keywords: List[str],
                            check_interval: int = 300) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Monitor Facebook content for copyright infringement.
        
        Args:
            targets: List of page IDs, group IDs, or usernames to monitor
            keywords: Keywords to search for
            check_interval: Check interval in seconds
        
        Yields:
            Dictionary containing monitoring results
        """
        logger.info(f"Starting Facebook content monitoring for {len(targets)} targets")
        
        while True:
            for target in targets:
                try:
                    # Check if target is a page or group
                    if target.startswith('group_'):
                        group_id = target.replace('group_', '')
                        # Monitor group posts (if accessible)
                        pass
                    else:
                        # Monitor page posts
                        posts = await self.get_page_posts(target, limit=50)
                        
                        for post in posts:
                            # Check for keyword matches
                            content = f"{post.message} {post.story}".lower()
                            for keyword in keywords:
                                if keyword.lower() in content:
                                    yield {
                                        'type': 'content_match',
                                        'platform': 'facebook',
                                        'target': target,
                                        'post_id': post.post_id,
                                        'keyword': keyword,
                                        'content': content[:500],
                                        'url': post.permalink_url,
                                        'timestamp': datetime.now(),
                                        'engagement': {
                                            'reactions': post.reactions,
                                            'comments': post.comments,
                                            'shares': post.shares
                                        }
                                    }
                
                except Exception as e:
                    logger.error(f"Error monitoring Facebook target {target}: {e}")
                    yield {
                        'type': 'error',
                        'platform': 'facebook',
                        'target': target,
                        'error': str(e),
                        'timestamp': datetime.now()
                    }
            
            await asyncio.sleep(check_interval)

    async def _process_post_data(self, post_data: Dict[str, Any]) -> Optional[FacebookPostData]:
        """Process raw Facebook post data into FacebookPostData object"""



        try:
            # Extract hashtags and mentions
            message = post_data.get('message', '')
            hashtags = re.findall(r'#(\w+)', message)
            mentions = re.findall(r'@(\w+)', message)
            
            # Calculate engagement rate
            reactions = post_data.get('reactions', {}).get('summary', {}).get('total_count', 0)
            comments = post_data.get('comments', {}).get('summary', {}).get('total_count', 0)
            shares = post_data.get('shares', {}).get('count', 0)
            
            total_engagement = reactions + comments + shares
            
            return FacebookPostData(
                post_id=post_data.get('id'),
                message=message,
                story=post_data.get('story', ''),
                created_time=datetime.fromisoformat(
                    post_data.get('created_time', datetime.now().isoformat())
                ),
                updated_time=datetime.fromisoformat(
                    post_data.get('updated_time', datetime.now().isoformat())
                ),
                type=post_data.get('type', ''),
                status_type=post_data.get('status_type', ''),
                permalink_url=post_data.get('permalink_url', ''),
                shares=post_data.get('shares', {}),
                reactions=post_data.get('reactions', {}),
                comments=post_data.get('comments', {}),
                attachments=post_data.get('attachments', {}).get('data', []),
                privacy=post_data.get('privacy', {}),
                targeting=post_data.get('targeting', {}),
                insights=post_data.get('insights', {}),
                place=post_data.get('place'),
                tagged_users=[],
                hashtags=hashtags,
                mentions=mentions,
                is_published=True,
                is_popular=total_engagement > 100,
                engagement_rate=total_engagement,
                reach=post_data.get('insights', {}).get('reach', 0),
                impressions=post_data.get('insights', {}).get('impressions', 0)
            )
        
        except Exception as e:
            logger.error(f"Error processing Facebook post data: {e}")
            return None

    def _filter_post(self, 
                    post: FacebookPostData, 
                    post_type: Optional[str] = None,
                    date_range: Optional[tuple] = None) -> bool:
        """Filter post based on criteria"""
        if post_type and post.type != post_type:
            return False
        
        if date_range:
            start_date, end_date = date_range
            if post.created_time < start_date or post.created_time > end_date:
                return False
        
        return True

    async def _scrape_posts_selenium(self, 
                                   query: str, 
                                   limit: int,
                                   post_type: Optional[str] = None,
                                   date_range: Optional[tuple] = None) -> List[FacebookPostData]:
        """Fallback Selenium scraping for public content"""
        # This would implement Selenium-based scraping for public Facebook content
        # Note: Facebook heavily restricts scraping, so this should only be used for public content
        logger.warning("Selenium scraping for Facebook is limited due to platform restrictions")
        return []

    def __del__(self):
        """Cleanup resources"""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
