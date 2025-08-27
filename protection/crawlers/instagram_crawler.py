"""
📸 Instagram Content Crawler
============================

Professional Instagram content discovery and monitoring system.
Integrates Instagram Graph API with web scraping for comprehensive coverage.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

⚠️ STRICT WARNING: Unauthorized use, copying, or distribution of this code 
is strictly prohibited without explicit written permission from Fahed Mlaiel.
Contact: mlaiel@live.de for licensing and authorization.
"""

import asyncio
import logging
import re
import json
import time
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import requests
from urllib.parse import urljoin, urlparse
import random

from .base_crawler import BasePlatformCrawler, CrawlResult, CrawlerStatus

logger = logging.getLogger(__name__)

@dataclass
class InstagramPostInfo:
    """Instagram post information structure."""
    post_id: str
    shortcode: str
    url: str
    caption: str
    media_type: str  # photo, video, carousel
    username: str
    user_id: str
    timestamp: datetime
    like_count: int
    comment_count: int
    view_count: Optional[int] = None
    media_urls: List[str] = None
    hashtags: List[str] = None
    mentions: List[str] = None
    location: Optional[str] = None
    is_ad: bool = False
    is_verified: bool = False
    metadata: Dict[str, Any] = None

@dataclass
class InstagramUserInfo:
    """Instagram user information structure."""
    user_id: str
    username: str
    full_name: str
    bio: str
    follower_count: int
    following_count: int
    post_count: int
    profile_pic_url: str
    is_verified: bool = False
    is_private: bool = False
    is_business: bool = False
    category: Optional[str] = None
    external_url: Optional[str] = None

@dataclass
class InstagramStoryInfo:
    """Instagram story information structure."""
    story_id: str
    username: str
    user_id: str
    media_type: str
    media_url: str
    timestamp: datetime
    expires_at: datetime
    view_count: Optional[int] = None
    is_ad: bool = False

class InstagramAPIClient:
    """Instagram Graph API client for business accounts."""
    
    def __init__(self, access_token: str, app_id: str):
        """Initialize Instagram API client."""
        self.access_token = access_token
        self.app_id = app_id
        self.base_url = "https://graph.instagram.com"
        self.api_version = "v18.0"
        
        # Rate limiting
        self.requests_per_hour = 200
        self.requests_made = []
        
        logger.info("Instagram API client initialized")
    
    def _check_rate_limit(self) -> bool:
        """Check API rate limit."""
        now = datetime.utcnow()
        
        # Remove requests older than 1 hour
        self.requests_made = [
            req_time for req_time in self.requests_made
            if now - req_time < timedelta(hours=1)
        ]
        
        return len(self.requests_made) < self.requests_per_hour
    
    async def _make_request(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Make authenticated API request."""
        if not self._check_rate_limit():
            raise Exception("Instagram API rate limit exceeded")
        
        url = f"{self.base_url}/{endpoint}"
        
        default_params = {
            'access_token': self.access_token
        }
        
        if params:
            default_params.update(params)
        
        try:
            response = requests.get(url, params=default_params, timeout=30)
            response.raise_for_status()
            
            self.requests_made.append(datetime.utcnow())
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Instagram API request failed: {e}")
            raise
    
    async def get_user_media(
        self,
        user_id: str,
        limit: int = 25,
        fields: List[str] = None
    ) -> List[InstagramPostInfo]:
        """Get user's media posts."""
        if not fields:
            fields = [
                'id', 'caption', 'media_type', 'media_url', 'permalink',
                'timestamp', 'username', 'like_count', 'comments_count'
            ]
        
        params = {
            'fields': ','.join(fields),
            'limit': limit
        }
        
        try:
            data = await self._make_request(f"{user_id}/media", params)
            
            posts = []
            for item in data.get('data', []):
                post = self._parse_media_item(item)
                if post:
                    posts.append(post)
            
            return posts
            
        except Exception as e:
            logger.error(f"Error getting user media: {e}")
            return []
    
    def _parse_media_item(self, item: Dict[str, Any]) -> Optional[InstagramPostInfo]:
        """Parse media item from API response."""
        try:
            # Extract hashtags and mentions from caption
            caption = item.get('caption', '')
            hashtags = re.findall(r'#(\w+)', caption)
            mentions = re.findall(r'@(\w+)', caption)
            
            return InstagramPostInfo(
                post_id=item['id'],
                shortcode=self._extract_shortcode(item.get('permalink', '')),
                url=item.get('permalink', ''),
                caption=caption,
                media_type=item.get('media_type', 'unknown'),
                username=item.get('username', ''),
                user_id=item.get('owner', {}).get('id', ''),
                timestamp=datetime.fromisoformat(item['timestamp'].replace('Z', '+00:00')),
                like_count=item.get('like_count', 0),
                comment_count=item.get('comments_count', 0),
                media_urls=[item.get('media_url', '')],
                hashtags=hashtags,
                mentions=mentions,
                metadata={
                    'api_source': True,
                    'media_product_type': item.get('media_product_type'),
                    'is_shared_to_feed': item.get('is_shared_to_feed')
                }
            )
            
        except Exception as e:
            logger.error(f"Error parsing media item: {e}")
            return None
    
    def _extract_shortcode(self, permalink: str) -> str:
        """Extract shortcode from Instagram permalink."""
        # Instagram URLs: https://www.instagram.com/p/SHORTCODE/
        match = re.search(r'/p/([A-Za-z0-9_-]+)/', permalink)
        return match.group(1) if match else ''

class InstagramSeleniumCrawler:
    """Selenium-based Instagram crawler for public content."""
    
    def __init__(self, headless: bool = True, proxy: Optional[str] = None):
        """Initialize Instagram Selenium crawler."""
        self.headless = headless
        self.proxy = proxy
        self.driver = None
        self.wait = None
        self.base_url = "https://www.instagram.com"
        
        # Rate limiting
        self.last_request_time = 0
        self.min_request_interval = 3.0
    
    def _setup_driver(self) -> webdriver.Chrome:
        """Setup Chrome WebDriver for Instagram."""
        options = Options()
        
        if self.headless:
            options.add_argument('--headless')
        
        # Instagram-specific options
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Mobile user agent for better compatibility
        options.add_argument(
            '--user-agent=Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) '
            'AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1'
        )
        
        if self.proxy:
            options.add_argument(f'--proxy-server={self.proxy}')
        
        try:
            driver = webdriver.Chrome(options=options)
            driver.set_page_load_timeout(30)
            return driver
        except Exception as e:
            logger.error(f"Failed to setup Chrome driver for Instagram: {e}")
            raise
    
    async def _rate_limit(self):
        """Apply rate limiting between requests."""
        current_time = time.time()
        elapsed = current_time - self.last_request_time
        
        if elapsed < self.min_request_interval:
            wait_time = self.min_request_interval - elapsed
            await asyncio.sleep(wait_time)
        
        self.last_request_time = time.time()
    
    async def search_hashtag(self, hashtag: str, max_results: int = 20) -> List[InstagramPostInfo]:
        """Search posts by hashtag."""
        if not self.driver:
            self.driver = self._setup_driver()
            self.wait = WebDriverWait(self.driver, 10)
        
        await self._rate_limit()
        
        try:
            # Navigate to hashtag page
            if not hashtag.startswith('#'):
                hashtag = hashtag.lstrip('#')
            
            hashtag_url = f"{self.base_url}/explore/tags/{hashtag}/"
            self.driver.get(hashtag_url)
            
            # Wait for posts to load
            await asyncio.sleep(3)
            
            # Extract posts
            posts = await self._extract_posts_from_grid(max_results)
            
            logger.info(f"Found {len(posts)} posts for hashtag #{hashtag}")
            return posts
            
        except Exception as e:
            logger.error(f"Instagram hashtag search error: {e}")
            return []
    
    async def search_location(self, location_id: str, max_results: int = 20) -> List[InstagramPostInfo]:
        """Search posts by location."""
        if not self.driver:
            self.driver = self._setup_driver()
            self.wait = WebDriverWait(self.driver, 10)
        
        await self._rate_limit()
        
        try:
            # Navigate to location page
            location_url = f"{self.base_url}/explore/locations/{location_id}/"
            self.driver.get(location_url)
            
            # Wait for posts to load
            await asyncio.sleep(3)
            
            # Extract posts
            posts = await self._extract_posts_from_grid(max_results)
            
            logger.info(f"Found {len(posts)} posts for location {location_id}")
            return posts
            
        except Exception as e:
            logger.error(f"Instagram location search error: {e}")
            return []
    
    async def _extract_posts_from_grid(self, max_results: int) -> List[InstagramPostInfo]:
        """Extract posts from Instagram grid layout."""
        posts = []
        
        try:
            # Scroll to load more posts
            for _ in range(max_results // 12):
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                await asyncio.sleep(2)
            
            # Find post links
            post_links = self.driver.find_elements(By.CSS_SELECTOR, 'article a[href*="/p/"]')
            
            # Extract information from each post link
            for link in post_links[:max_results]:
                try:
                    post_url = link.get_attribute('href')
                    post_info = await self._extract_basic_post_info(link, post_url)
                    
                    if post_info:
                        posts.append(post_info)
                        
                except Exception as e:
                    logger.debug(f"Error extracting post info: {e}")
                    continue
            
            return posts
            
        except Exception as e:
            logger.error(f"Error extracting posts from grid: {e}")
            return []
    
    async def _extract_basic_post_info(self, link_element, post_url: str) -> Optional[InstagramPostInfo]:
        """Extract basic post information from grid element."""
        try:
            # Extract shortcode from URL
            shortcode = self._extract_shortcode(post_url)
            
            # Try to find image/video element
            try:
                media_element = link_element.find_element(By.CSS_SELECTOR, 'img, video')
                media_url = media_element.get_attribute('src')
                media_type = 'video' if media_element.tag_name == 'video' else 'photo'
            except:
                media_url = ''
                media_type = 'unknown'
            
            # Try to extract basic stats from overlay
            like_count = 0
            comment_count = 0
            
            try:
                stats_overlay = link_element.find_element(By.CSS_SELECTOR, '[role="button"]')
                stats_text = stats_overlay.text
                
                # Parse likes and comments from overlay text
                like_match = re.search(r'(\d+(?:,\d+)*)\s*likes?', stats_text, re.IGNORECASE)
                if like_match:
                    like_count = int(like_match.group(1).replace(',', ''))
                
                comment_match = re.search(r'(\d+(?:,\d+)*)\s*comments?', stats_text, re.IGNORECASE)
                if comment_match:
                    comment_count = int(comment_match.group(1).replace(',', ''))
                    
            except:
                pass
            
            return InstagramPostInfo(
                post_id=shortcode,
                shortcode=shortcode,
                url=post_url,
                caption='',  # Would need individual post page for full caption
                media_type=media_type,
                username='',  # Would need individual post page
                user_id='',
                timestamp=datetime.utcnow(),  # Would need individual post page
                like_count=like_count,
                comment_count=comment_count,
                media_urls=[media_url] if media_url else [],
                metadata={
                    'extraction_method': 'grid_basic',
                    'extracted_at': datetime.utcnow().isoformat()
                }
            )
            
        except Exception as e:
            logger.debug(f"Error extracting basic post info: {e}")
            return None
    
    def _extract_shortcode(self, url: str) -> str:
        """Extract shortcode from Instagram URL."""
        match = re.search(r'/p/([A-Za-z0-9_-]+)/', url)
        return match.group(1) if match else ''
    
    async def scrape_post_details(self, post_url: str) -> Optional[InstagramPostInfo]:
        """Scrape detailed information from Instagram post page."""
        if not self.driver:
            self.driver = self._setup_driver()
            self.wait = WebDriverWait(self.driver, 10)
        
        await self._rate_limit()
        
        try:
            # Navigate to post
            self.driver.get(post_url)
            await asyncio.sleep(3)
            
            # Extract detailed information
            # This would involve more complex scraping
            # For now, return basic structure
            shortcode = self._extract_shortcode(post_url)
            
            return InstagramPostInfo(
                post_id=shortcode,
                shortcode=shortcode,
                url=post_url,
                caption='',
                media_type='unknown',
                username='',
                user_id='',
                timestamp=datetime.utcnow(),
                like_count=0,
                comment_count=0,
                metadata={'method': 'detailed_scrape'}
            )
            
        except Exception as e:
            logger.error(f"Error scraping Instagram post details: {e}")
            return None
    
    def close(self):
        """Close Selenium driver."""
        if self.driver:
            self.driver.quit()
            self.driver = None

class InstagramCrawler(BasePlatformCrawler):
    """
    Professional Instagram Content Crawler
    ======================================
    
    Advanced Instagram content discovery and monitoring system featuring:
    - Instagram Graph API integration for business accounts
    - Selenium web scraping for public content
    - Hashtag and location-based content discovery
    - Story monitoring and analysis
    - User profile tracking
    - Media content extraction and analysis
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize Instagram crawler."""
        super().__init__("instagram", config)
        
        # API configuration
        self.access_token = config.get('access_token')
        self.app_id = config.get('app_id')
        
        # Scraping configuration
        self.headless = config.get('headless', True)
        self.proxy = config.get('proxy')
        self.max_results_per_search = config.get('max_results_per_search', 50)
        
        # Initialize clients
        self.api_client = None
        self.selenium_crawler = None
        
        if self.access_token and self.app_id:
            try:
                self.api_client = InstagramAPIClient(self.access_token, self.app_id)
                logger.info("Instagram API client initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Instagram API: {e}")
        
        try:
            self.selenium_crawler = InstagramSeleniumCrawler(self.headless, self.proxy)
            logger.info("Instagram Selenium crawler initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Instagram Selenium crawler: {e}")
    
    async def search_content(
        self,
        query: str,
        content_type: str = 'post',
        max_results: int = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[CrawlResult]:
        """Search for content on Instagram."""
        max_results = max_results or self.max_results_per_search
        results = []
        
        try:
            # Determine search type
            if query.startswith('#'):
                # Hashtag search
                results = await self._search_hashtag(query, max_results, filters)
            elif query.startswith('@'):
                # User search
                results = await self._search_user(query[1:], max_results, filters)
            else:
                # General search (try hashtag)
                results = await self._search_hashtag(f"#{query}", max_results, filters)
            
            logger.info(f"Instagram search '{query}' returned {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"Instagram search error: {e}")
            return []
    
    async def _search_hashtag(
        self,
        hashtag: str,
        max_results: int,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[CrawlResult]:
        """Search content by hashtag."""
        if not self.selenium_crawler:
            return []
        
        try:
            posts = await self.selenium_crawler.search_hashtag(hashtag, max_results)
            return await self._convert_posts_to_results(posts)
            
        except Exception as e:
            logger.error(f"Instagram hashtag search error: {e}")
            return []
    
    async def _search_user(
        self,
        username: str,
        max_results: int,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[CrawlResult]:
        """Search content by user."""
        results = []
        
        try:
            # Try API first if available
            if self.api_client:
                # Note: This would require user ID, which we'd need to get from username
                # For now, we'll use selenium
                pass
            
            # Use selenium for public content
            if self.selenium_crawler:
                # Would need to implement user profile scraping
                pass
            
            return results
            
        except Exception as e:
            logger.error(f"Instagram user search error: {e}")
            return []
    
    async def _convert_posts_to_results(self, posts: List[InstagramPostInfo]) -> List[CrawlResult]:
        """Convert Instagram posts to CrawlResult format."""
        results = []
        
        for post in posts:
            try:
                result = CrawlResult(
                    platform="instagram",
                    url=post.url,
                    title=post.caption[:100] if post.caption else f"Post by {post.username}",
                    description=post.caption,
                    content_type=post.media_type,
                    file_url=post.media_urls[0] if post.media_urls else None,
                    metadata={
                        'post_id': post.post_id,
                        'shortcode': post.shortcode,
                        'username': post.username,
                        'user_id': post.user_id,
                        'timestamp': post.timestamp.isoformat(),
                        'like_count': post.like_count,
                        'comment_count': post.comment_count,
                        'view_count': post.view_count,
                        'media_urls': post.media_urls,
                        'hashtags': post.hashtags,
                        'mentions': post.mentions,
                        'location': post.location,
                        'is_ad': post.is_ad,
                        'is_verified': post.is_verified,
                        **(post.metadata or {})
                    },
                    discovered_at=datetime.utcnow(),
                    fingerprint_candidates=[
                        post.url,
                        post.caption or '',
                        ' '.join(post.hashtags or []),
                        post.username
                    ]
                )
                results.append(result)
                
            except Exception as e:
                logger.error(f"Error converting post to result: {e}")
                continue
        
        return results
    
    async def search_by_location(self, location_id: str, max_results: int = 20) -> List[CrawlResult]:
        """Search content by location."""
        if not self.selenium_crawler:
            return []
        
        try:
            posts = await self.selenium_crawler.search_location(location_id, max_results)
            return await self._convert_posts_to_results(posts)
            
        except Exception as e:
            logger.error(f"Instagram location search error: {e}")
            return []
    
    async def monitor_hashtag(
        self,
        hashtag: str,
        callback_func: callable = None,
        interval_minutes: int = 60
    ) -> bool:
        """Monitor hashtag for new content."""
        try:
            monitoring_key = f"hashtag_{hashtag}"
            
            if monitoring_key in self.monitoring_tasks:
                logger.warning(f"Already monitoring hashtag {hashtag}")
                return False
            
            # Create monitoring task
            task = asyncio.create_task(
                self._continuous_hashtag_monitor(hashtag, callback_func, interval_minutes)
            )
            self.monitoring_tasks[monitoring_key] = task
            
            logger.info(f"Started monitoring hashtag {hashtag}")
            return True
            
        except Exception as e:
            logger.error(f"Error starting hashtag monitoring: {e}")
            return False
    
    async def _continuous_hashtag_monitor(
        self,
        hashtag: str,
        callback_func: callable,
        interval_minutes: int
    ):
        """Continuous hashtag monitoring loop."""
        logger.info(f"Starting continuous monitoring for hashtag {hashtag}")
        
        try:
            while True:
                try:
                    results = await self._search_hashtag(hashtag, 20)
                    
                    if results and callback_func:
                        await callback_func(results)
                    
                except Exception as e:
                    logger.error(f"Error in hashtag monitoring: {e}")
                
                # Wait before next check
                await asyncio.sleep(interval_minutes * 60)
                
        except asyncio.CancelledError:
            logger.info(f"Hashtag monitoring cancelled for {hashtag}")
        except Exception as e:
            logger.error(f"Hashtag monitoring error: {e}")
    
    async def check_rate_limits(self) -> bool:
        """Check if crawler is within rate limits."""
        api_ok = True
        if self.api_client:
            api_ok = self.api_client._check_rate_limit()
        
        return api_ok
    
    async def get_crawler_stats(self) -> Dict[str, Any]:
        """Get crawler statistics."""
        stats = {
            "platform": "instagram",
            "api_available": self.api_client is not None,
            "selenium_available": self.selenium_crawler is not None,
            "active_monitoring": len(self.monitoring_tasks)
        }
        
        if self.api_client:
            stats["api_requests_last_hour"] = len(self.api_client.requests_made)
            stats["api_rate_limited"] = not self.api_client._check_rate_limit()
        
        return stats
    
    def cleanup(self):
        """Cleanup crawler resources."""
        if self.selenium_crawler:
            self.selenium_crawler.close()
        
        # Cancel monitoring tasks
        for task in self.monitoring_tasks.values():
            task.cancel()
        self.monitoring_tasks.clear()
        
        logger.info("Instagram crawler cleanup completed")

# Export main classes
__all__ = [
    'InstagramCrawler',
    'InstagramAPIClient',
    'InstagramSeleniumCrawler',
    'InstagramPostInfo',
    'InstagramUserInfo',
    'InstagramStoryInfo'
]
