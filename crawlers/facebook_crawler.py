"""
Facebook Crawler
================

Professional Facebook content crawler with Graph API integration.
Implements Facebook Graph API with intelligent rate limiting and monitoring.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

WARNING: This code is protected by copyright law. Any unauthorized copying, 
distribution, or modification is strictly prohibited and will result in 
legal action. Contact mlaiel@live.de for licensing.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Union, AsyncGenerator
from datetime import datetime, timedelta
from dataclasses import dataclass
import json
import re

import aiohttp
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from ..utils.rate_limiter import FacebookRateLimiter
from ..utils.proxy_manager import ProxyManager
from ..utils.user_agent_rotator import UserAgentRotator
from ...core.config import get_settings
from ...core.exceptions import CrawlerError, RateLimitError
from ...database.models import CrawlResult, ContentMatch

logger = logging.getLogger(__name__)
settings = get_settings()

@dataclass
class FacebookPost:
    """Facebook post data structure."""
    post_id: str
    message: str
    story: str
    link: str
    name: str
    caption: str
    description: str
    source: str
    type: str
    status_type: str
    object_id: str
    parent_id: str
    permalink_url: str
    created_time: datetime
    updated_time: datetime
    is_hidden: bool
    is_published: bool
    is_spherical: bool
    reactions: Dict
    comments: Dict
    shares: Dict
    attachments: Dict

@dataclass
class FacebookPage:
    """Facebook page data structure."""
    page_id: str
    name: str
    category: str
    category_list: List[Dict]
    description: str
    about: str
    website: str
    phone: str
    emails: List[str]
    fan_count: int
    follow_count: int
    checkin_count: int
    talking_about_count: int
    were_here_count: int
    is_verified: bool
    is_published: bool
    link: str
    picture: Dict
    cover: Dict
    location: Dict
    hours: Dict

@dataclass
class FacebookEvent:
    """Facebook event data structure."""
    event_id: str
    name: str
    description: str
    start_time: datetime
    end_time: Optional[datetime]
    place: Dict
    is_online: bool
    event_times: List[Dict]
    attending_count: int
    interested_count: int
    maybe_count: int
    noreply_count: int
    category: str
    type: str
    is_canceled: bool
    is_draft: bool
    owner: Dict
    ticket_uri: str
    cover: Dict

class FacebookCrawler:
    """
    Professional Facebook crawler implementation.
    
    Features:
    - Facebook Graph API integration
    - Page and post monitoring
    - Event discovery and tracking
    - Advanced search capabilities
    - Content similarity detection
    - Engagement analytics
    - Real-time monitoring
    - Multi-format content support
    """
    
    def __init__(self):
        """Initialize Facebook crawler."""
        self.access_token = settings.FACEBOOK_ACCESS_TOKEN
        self.app_id = settings.FACEBOOK_APP_ID
        self.app_secret = settings.FACEBOOK_APP_SECRET
        self.rate_limiter = FacebookRateLimiter()
        self.proxy_manager = ProxyManager()
        self.user_agent_rotator = UserAgentRotator()
        self.session = None
        
        # Base URLs
        self.api_base_url = "https://graph.facebook.com/v18.0"
        self.web_base_url = "https://www.facebook.com"
        
        # Selenium configuration
        self.selenium_options = webdriver.ChromeOptions()
        self.selenium_options.add_argument('--headless')
        self.selenium_options.add_argument('--no-sandbox')
        self.selenium_options.add_argument('--disable-dev-shm-usage')
        self.selenium_options.add_argument('--disable-gpu')
        self.selenium_options.add_argument('--disable-blink-features=AutomationControlled')
    
    async def __aenter__(self):
        """Async context manager entry."""
        headers = {
            'User-Agent': self.user_agent_rotator.get_user_agent()
        }
        self.session = aiohttp.ClientSession(headers=headers)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def search_pages(
        self,
        query: str,
        max_results: int = 50,
        fields: List[str] = None
    ) -> List[FacebookPage]:
        """
        Search Facebook pages.
        
        Args:
            query: Search query
            max_results: Maximum number of pages to return
            fields: Page fields to retrieve
            
        Returns:
            List of Facebook page objects
        """



        try:
            await self.rate_limiter.wait_if_needed()
            
            if self.access_token:
                return await self._search_pages_api(query, max_results, fields)
            else:
                return await self._search_pages_scraping(query, max_results)
                
        except Exception as e:
            logger.error(f"Facebook page search error: {e}")
            return []
    
    async def _search_pages_api(self, query: str, max_results: int, fields: List[str]) -> List[FacebookPage]:
        """Search pages using Facebook Graph API."""



        try:
            if not fields:
                fields = [
                    'id', 'name', 'category', 'category_list', 'description',
                    'about', 'website', 'phone', 'emails', 'fan_count',
                    'follow_count', 'checkin_count', 'talking_about_count',
                    'were_here_count', 'is_verified', 'is_published',
                    'link', 'picture', 'cover', 'location', 'hours'
                ]
            
            url = f"{self.api_base_url}/search"
            params = {
                'q': query,
                'type': 'page',
                'fields': ','.join(fields),
                'limit': min(max_results, 100),
                'access_token': self.access_token
            }
            
            pages = []
            next_page = None
            
            while len(pages) < max_results:
                if next_page:
                    params['after'] = next_page
                
                async with self.session.get(url, params=params) as response:
                    if response.status != 200:
                        break
                    
                    data = await response.json()
                    
                    if 'error' in data:
                        logger.error(f"Facebook API error: {data['error']}")
                        break
                    
                    for page_data in data.get('data', []):
                        page = self._parse_page_data(page_data)
                        if page:
                            pages.append(page)
                    
                    # Check for next page
                    paging = data.get('paging', {})
                    cursors = paging.get('cursors', {})
                    next_page = cursors.get('after')
                    
                    if not next_page or not paging.get('next'):
                        break
                
                await self.rate_limiter.update_usage(1)
            
            return pages[:max_results]
            
        except Exception as e:
            logger.error(f"Facebook API page search failed: {e}")
            return []
    
    def _parse_page_data(self, page_data: dict) -> Optional[FacebookPage]:
        """Parse Facebook page data from API response."""



        try:
            return FacebookPage(
                page_id=page_data.get('id', ''),
                name=page_data.get('name', ''),
                category=page_data.get('category', ''),
                category_list=page_data.get('category_list', []),
                description=page_data.get('description', ''),
                about=page_data.get('about', ''),
                website=page_data.get('website', ''),
                phone=page_data.get('phone', ''),
                emails=page_data.get('emails', []),
                fan_count=page_data.get('fan_count', 0),
                follow_count=page_data.get('follow_count', 0),
                checkin_count=page_data.get('checkin_count', 0),
                talking_about_count=page_data.get('talking_about_count', 0),
                were_here_count=page_data.get('were_here_count', 0),
                is_verified=page_data.get('is_verified', False),
                is_published=page_data.get('is_published', True),
                link=page_data.get('link', ''),
                picture=page_data.get('picture', {}),
                cover=page_data.get('cover', {}),
                location=page_data.get('location', {}),
                hours=page_data.get('hours', {})
            )
            
        except Exception as e:
            logger.error(f"Failed to parse page data: {e}")
            return None
    
    async def get_page_posts(
        self,
        page_id: str,
        max_results: int = 50,
        since: Optional[datetime] = None,
        until: Optional[datetime] = None,
        fields: List[str] = None
    ) -> List[FacebookPost]:
        """Get posts from a Facebook page."""



        try:
            await self.rate_limiter.wait_if_needed()
            
            if self.access_token:
                return await self._get_page_posts_api(page_id, max_results, since, until, fields)
            else:
                return await self._get_page_posts_scraping(page_id, max_results)
                
        except Exception as e:
            logger.error(f"Failed to get page posts for {page_id}: {e}")
            return []
    
    async def _get_page_posts_api(
        self,
        page_id: str,
        max_results: int,
        since: Optional[datetime],
        until: Optional[datetime],
        fields: List[str]
    ) -> List[FacebookPost]:
        """Get page posts using Facebook Graph API."""



        try:
            if not fields:
                fields = [
                    'id', 'message', 'story', 'link', 'name', 'caption',
                    'description', 'source', 'type', 'status_type',
                    'object_id', 'parent_id', 'permalink_url', 'created_time',
                    'updated_time', 'is_hidden', 'is_published', 'is_spherical',
                    'reactions.summary(total_count)', 'comments.summary(total_count)',
                    'shares', 'attachments'
                ]
            
            url = f"{self.api_base_url}/{page_id}/posts"
            params = {
                'fields': ','.join(fields),
                'limit': min(max_results, 100),
                'access_token': self.access_token
            }
            
            if since:
                params['since'] = int(since.timestamp())
            if until:
                params['until'] = int(until.timestamp())
            
            posts = []
            next_page = None
            
            while len(posts) < max_results:
                if next_page:
                    params['after'] = next_page
                
                async with self.session.get(url, params=params) as response:
                    if response.status != 200:
                        break
                    
                    data = await response.json()
                    
                    if 'error' in data:
                        logger.error(f"Facebook API error: {data['error']}")
                        break
                    
                    for post_data in data.get('data', []):
                        post = self._parse_post_data(post_data)
                        if post:
                            posts.append(post)
                    
                    # Check for next page
                    paging = data.get('paging', {})
                    cursors = paging.get('cursors', {})
                    next_page = cursors.get('after')
                    
                    if not next_page or not paging.get('next'):
                        break
                
                await self.rate_limiter.update_usage(1)
            
            return posts[:max_results]
            
        except Exception as e:
            logger.error(f"Facebook API get posts failed: {e}")
            return []
    
    def _parse_post_data(self, post_data: dict) -> Optional[FacebookPost]:
        """Parse Facebook post data from API response."""



        try:
            # Parse timestamps
            created_time = datetime.fromisoformat(
                post_data.get('created_time', '').replace('Z', '+00:00')
            ) if post_data.get('created_time') else datetime.now()
            
            updated_time = datetime.fromisoformat(
                post_data.get('updated_time', '').replace('Z', '+00:00')
            ) if post_data.get('updated_time') else created_time
            
            # Parse engagement metrics
            reactions = {}
            if 'reactions' in post_data:
                reactions = {
                    'total_count': post_data['reactions'].get('summary', {}).get('total_count', 0)
                }
            
            comments = {}
            if 'comments' in post_data:
                comments = {
                    'total_count': post_data['comments'].get('summary', {}).get('total_count', 0)
                }
            
            shares = post_data.get('shares', {})
            
            return FacebookPost(
                post_id=post_data.get('id', ''),
                message=post_data.get('message', ''),
                story=post_data.get('story', ''),
                link=post_data.get('link', ''),
                name=post_data.get('name', ''),
                caption=post_data.get('caption', ''),
                description=post_data.get('description', ''),
                source=post_data.get('source', ''),
                type=post_data.get('type', ''),
                status_type=post_data.get('status_type', ''),
                object_id=post_data.get('object_id', ''),
                parent_id=post_data.get('parent_id', ''),
                permalink_url=post_data.get('permalink_url', ''),
                created_time=created_time,
                updated_time=updated_time,
                is_hidden=post_data.get('is_hidden', False),
                is_published=post_data.get('is_published', True),
                is_spherical=post_data.get('is_spherical', False),
                reactions=reactions,
                comments=comments,
                shares=shares,
                attachments=post_data.get('attachments', {})
            )
            
        except Exception as e:
            logger.error(f"Failed to parse post data: {e}")
            return None
    
    async def search_events(
        self,
        query: str,
        location: Optional[str] = None,
        max_results: int = 50
    ) -> List[FacebookEvent]:
        """Search Facebook events."""



        try:
            await self.rate_limiter.wait_if_needed()
            
            if self.access_token:
                return await self._search_events_api(query, location, max_results)
            else:
                return await self._search_events_scraping(query, location, max_results)
                
        except Exception as e:
            logger.error(f"Facebook event search error: {e}")
            return []
    
    async def _search_events_api(self, query: str, location: Optional[str], max_results: int) -> List[FacebookEvent]:
        """Search events using Facebook Graph API."""



        try:
            # Note: Public event search was restricted in Facebook API
            # This would require special permissions or alternative approaches
            logger.info("Facebook event search requires special API permissions")
            return []
            
        except Exception as e:
            logger.error(f"Facebook API event search failed: {e}")
            return []
    
    async def monitor_page(
        self,
        page_id: str,
        check_interval: int = 300
    ) -> AsyncGenerator[List[FacebookPost], None]:
        """Monitor Facebook page for new posts."""
        last_check = datetime.now()
        seen_posts = set()
        
        while True:
            try:
                # Get recent posts from page
                page_posts = await self.get_page_posts(
                    page_id,
                    max_results=20,
                    since=last_check
                )
                
                # Filter new posts
                new_posts = []
                for post in page_posts:
                    if post.post_id not in seen_posts:
                        new_posts.append(post)
                        seen_posts.add(post.post_id)
                
                if new_posts:
                    yield new_posts
                
                last_check = datetime.now()
                await asyncio.sleep(check_interval)
                
            except Exception as e:
                logger.error(f"Page monitoring error for {page_id}: {e}")
                await asyncio.sleep(60)
    
    async def analyze_post_engagement(self, post: FacebookPost) -> Dict:
        """Analyze Facebook post engagement metrics."""



        try:
            # Extract engagement counts
            reaction_count = post.reactions.get('total_count', 0)
            comment_count = post.comments.get('total_count', 0)
            share_count = post.shares.get('count', 0) if post.shares else 0
            
            total_engagement = reaction_count + comment_count + share_count
            
            # Post age analysis
            post_age = datetime.now() - post.created_time
            engagement_per_hour = total_engagement / max(post_age.total_seconds() / 3600, 1)
            
            # Content analysis
            has_link = bool(post.link)
            has_image = post.type in ['photo', 'album']
            has_video = post.type == 'video'
            message_length = len(post.message) if post.message else 0
            
            # Performance categorization
            if total_engagement > 1000:
                performance = "viral"
            elif total_engagement > 100:
                performance = "high"
            elif total_engagement > 20:
                performance = "medium"
            else:
                performance = "low"
            
            return {
                'total_engagement': total_engagement,
                'reaction_count': reaction_count,
                'comment_count': comment_count,
                'share_count': share_count,
                'engagement_per_hour': round(engagement_per_hour, 2),
                'post_age_hours': round(post_age.total_seconds() / 3600, 1),
                'performance_category': performance,
                'content_type': post.type,
                'has_link': has_link,
                'has_image': has_image,
                'has_video': has_video,
                'message_length': message_length,
                'reaction_to_comment_ratio': round(reaction_count / max(comment_count, 1), 2),
                'share_rate': round((share_count / max(total_engagement, 1)) * 100, 2)
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze post engagement: {e}")
            return {}
    
    async def detect_similar_posts(
        self,
        reference_post: FacebookPost,
        page_ids: List[str] = None,
        similarity_threshold: float = 0.7
    ) -> List[Dict]:
        """Detect posts similar to reference post."""



        try:
            similar_posts = []
            
            # If no specific pages provided, search broadly
            if not page_ids:
                # This would require a more complex search implementation
                logger.info("Broad post similarity search not implemented")
                return []
            
            # Search within specific pages
            for page_id in page_ids:
                page_posts = await self.get_page_posts(page_id, max_results=50)
                
                for post in page_posts:
                    if post.post_id == reference_post.post_id:
                        continue
                    
                    similarity = self._calculate_post_similarity(reference_post, post)
                    
                    if similarity >= similarity_threshold:
                        similar_posts.append({
                            'post': post,
                            'similarity_score': similarity,
                            'match_factors': self._get_post_match_factors(reference_post, post)
                        })
            
            # Sort by similarity
            return sorted(similar_posts, key=lambda x: x['similarity_score'], reverse=True)
            
        except Exception as e:
            logger.error(f"Similar post detection failed: {e}")
            return []
    
    def _calculate_post_similarity(self, post1: FacebookPost, post2: FacebookPost) -> float:
        """Calculate similarity score between two posts."""
        # Message similarity
        message1_words = set((post1.message or '').lower().split())
        message2_words = set((post2.message or '').lower().split())
        message_similarity = len(message1_words & message2_words) / len(message1_words | message2_words) if message1_words | message2_words else 0
        
        # Type similarity
        type_similarity = 1.0 if post1.type == post2.type else 0.0
        
        # Link similarity
        link_similarity = 1.0 if post1.link and post2.link and post1.link == post2.link else 0.0
        
        # Time proximity
        time_diff = abs((post1.created_time - post2.created_time).total_seconds())
        time_similarity = max(0, 1 - (time_diff / (7 * 24 * 3600)))  # 7 days max
        
        # Weighted average
        weights = {
            'message': 0.5,
            'type': 0.2,
            'link': 0.2,
            'time': 0.1
        }
        
        similarity = (
            weights['message'] * message_similarity +
            weights['type'] * type_similarity +
            weights['link'] * link_similarity +
            weights['time'] * time_similarity
        )
        
        return similarity
    
    def _get_post_match_factors(self, post1: FacebookPost, post2: FacebookPost) -> List[str]:
        """Get factors that contribute to post similarity."""
        factors = []
        
        if post1.type == post2.type:
            factors.append(f'same_type: {post1.type}')
        
        if post1.link and post2.link and post1.link == post2.link:
            factors.append('same_link')
        
        # Check message similarity
        if post1.message and post2.message:
            message1_words = set(post1.message.lower().split())
            message2_words = set(post2.message.lower().split())
            common_words = message1_words & message2_words
            if len(common_words) > 3:
                factors.append('similar_message')
        
        # Check time proximity
        time_diff = abs((post1.created_time - post2.created_time).total_seconds())
        if time_diff < 3600:  # Within 1 hour
            factors.append('posted_within_hour')
        elif time_diff < 86400:  # Within 1 day
            factors.append('posted_same_day')
        
        return factors
    
    async def get_page_insights(self, page_id: str, metrics: List[str] = None) -> Dict:
        """Get Facebook page insights (requires page access token)."""



        try:
            await self.rate_limiter.wait_if_needed()
            
            if not self.access_token:
                logger.warning("Page insights require access token")
                return {}
            
            if not metrics:
                metrics = [
                    'page_fans', 'page_fans_online', 'page_views', 'page_engaged_users',
                    'page_post_engagements', 'page_posts_impressions', 'page_video_views'
                ]
            
            url = f"{self.api_base_url}/{page_id}/insights"
            params = {
                'metric': ','.join(metrics),
                'period': 'day',
                'access_token': self.access_token
            }
            
            async with self.session.get(url, params=params) as response:
                if response.status != 200:
                    return {}
                
                data = await response.json()
                
                if 'error' in data:
                    logger.error(f"Facebook insights error: {data['error']}")
                    return {}
                
                insights = {}
                for metric_data in data.get('data', []):
                    metric_name = metric_data.get('name')
                    values = metric_data.get('values', [])
                    if values:
                        insights[metric_name] = values[-1].get('value', 0)
                
                await self.rate_limiter.update_usage(1)
                return insights
                
        except Exception as e:
            logger.error(f"Failed to get page insights: {e}")
            return {}
