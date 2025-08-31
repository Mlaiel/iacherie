"""
Instagram Professional API Integration
=====================================

Professional Instagram monitoring and content extraction system.
Combines Instagram Graph API, Basic Display API with advanced scraping
for comprehensive content surveillance and rights protection.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

  INTELLECTUAL PROPERTY WARNING 
This code is the exclusive property of Fahed Mlaiel (mlaiel@live.de).
Unauthorized use, copying, modification, or distribution is strictly prohibited.
Violators will face immediate legal action under German and international law.
"""

import asyncio
import logging
import re
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
import aiohttp
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import requests
from bs4 import BeautifulSoup

from .base import BaseCrawler, CrawlResult
from ..config import ContentType
from ..security.encryption import SecurityManager
from ..utils.rate_limiter import RateLimiter
from ..utils.proxy_manager import ProxyManager

logger = logging.getLogger(__name__)

@dataclass
class InstagramMediaData:
    """Comprehensive Instagram media metadata structure."""
    
    media_id: str
    media_url: str
    media_type: str  # IMAGE, VIDEO, CAROUSEL_ALBUM
    permalink: str
    caption: str
    username: str
    user_id: str
    timestamp: datetime
    like_count: int
    comment_count: int
    share_count: Optional[int]
    save_count: Optional[int]
    hashtags: List[str]
    mentions: List[str]
    location: Optional[Dict[str, Any]]
    
    # Media-specific data
    thumbnail_url: Optional[str] = None
    video_url: Optional[str] = None
    duration: Optional[int] = None  # for videos
    dimensions: Optional[Dict[str, int]] = None
    
    # Advanced metadata
    is_story: bool = False
    is_reel: bool = False
    is_ad: bool = False
    music_metadata: Optional[Dict[str, Any]] = None
    product_tags: List[Dict[str, Any]] = None

@dataclass
class InstagramUserData:
    """Instagram user profile comprehensive information."""
    
    user_id: str
    username: str
    display_name: str
    bio: str
    follower_count: int
    following_count: int
    media_count: int
    verified: bool
    profile_picture_url: str
    external_url: Optional[str]
    business_account: bool
    category: Optional[str]
    contact_info: Optional[Dict[str, Any]]

class InstagramAPIManager:
    """Professional Instagram API management with Graph API integration."""
    
    def __init__(
        self,
        app_id: str,
        app_secret: str,
        access_token: Optional[str] = None
    ):
        """Initialize Instagram API service with Graph API credentials."""
        self.app_id = app_id
        self.app_secret = app_secret
        self.access_token = access_token
        self.graph_api_url = "https://graph.instagram.com"
        self.basic_api_url = "https://graph.facebook.com"
        
        self.rate_limiter = RateLimiter(
            max_calls=200,  # Instagram API rate limit
            time_window=3600  # Per hour
        )
    
    async def get_user_media(
        self,
        user_id: str,
        limit: int = 25,
        fields: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Fetch user media using Instagram Graph API."""
        await self.rate_limiter.acquire()
        
        if not fields:
            fields = [
                'id', 'media_type', 'media_url', 'permalink', 'caption',
                'timestamp', 'like_count', 'comments_count', 'thumbnail_url'
            ]
        
        try:
            url = f"{self.graph_api_url}/{user_id}/media"
            params = {
                'fields': ','.join(fields),
                'limit': limit,
                'access_token': self.access_token
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result.get('data', [])
                    else:
                        logger.error(f"Instagram API error: {response.status}")
                        return []
                        
        except Exception as e:
            logger.error(f"Instagram user media fetch error: {e}")
            return []
    
    async def get_media_details(self, media_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about specific media."""
        await self.rate_limiter.acquire()
        
        try:
            fields = [
                'id', 'media_type', 'media_url', 'permalink', 'caption',
                'timestamp', 'like_count', 'comments_count', 'thumbnail_url',
                'children', 'username'
            ]
            
            url = f"{self.graph_api_url}/{media_id}"
            params = {
                'fields': ','.join(fields),
                'access_token': self.access_token
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        logger.error(f"Media details fetch error: {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"Media details error: {e}")
            return None
    
    async def search_hashtag(
        self,
        hashtag: str,
        user_id: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Search media by hashtag using Instagram Graph API."""
        await self.rate_limiter.acquire()
        
        try:
            # First get hashtag ID
            hashtag_search_url = f"{self.graph_api_url}/ig_hashtag_search"
            search_params = {
                'user_id': user_id,
                'q': hashtag,
                'access_token': self.access_token
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(hashtag_search_url, params=search_params) as response:
                    if response.status != 200:
                        return []
                    
                    hashtag_data = await response.json()
                    hashtag_results = hashtag_data.get('data', [])
                    
                    if not hashtag_results:
                        return []
                    
                    hashtag_id = hashtag_results[0]['id']
                
                # Get media from hashtag
                media_url = f"{self.graph_api_url}/{hashtag_id}/recent_media"
                media_params = {
                    'user_id': user_id,
                    'fields': 'id,media_type,media_url,permalink,caption,timestamp',
                    'limit': limit,
                    'access_token': self.access_token
                }
                
                async with session.get(media_url, params=media_params) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result.get('data', [])
                    else:
                        return []
                        
        except Exception as e:
            logger.error(f"Instagram hashtag search error: {e}")
            return []

class InstagramWebScraper:
    """Advanced Instagram web scraping with anti-detection measures."""
    
    def __init__(self, proxy_manager: Optional[ProxyManager] = None):
        """Initialize Instagram web scraper with proxy support."""
        self.proxy_manager = proxy_manager
        self.session = None
        self.driver = None
        self._setup_selenium_driver()
    
    def _setup_selenium_driver(self):
        """Configure Selenium WebDriver with anti-detection measures."""
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Mobile user agent for better compatibility
        mobile_agents = [
            'Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X) AppleWebKit/605.1.15',
            'Mozilla/5.0 (Android 11; Mobile; rv:68.0) Gecko/68.0 Firefox/88.0',
            'Mozilla/5.0 (Linux; Android 11; SM-G991B) AppleWebKit/537.36'
        ]
        
        import random
        chrome_options.add_argument(f'--user-agent={random.choice(mobile_agents)}')
        
        # Proxy configuration
        if self.proxy_manager:
            proxy = self.proxy_manager.get_proxy()
            if proxy:
                chrome_options.add_argument(f'--proxy-server={proxy}')
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    async def scrape_post_data(self, post_url: str) -> Optional[InstagramMediaData]:
        """Scrape comprehensive post data from Instagram post page."""



        try:
            self.driver.get(post_url)
            
            # Wait for content to load
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "article"))
            )
            
            # Extract post ID from URL
            post_id_match = re.search(r'/p/([A-Za-z0-9_-]+)', post_url)
            if not post_id_match:
                return None
            
            shortcode = post_id_match.group(1)
            
            # Try to extract data from script tags
            script_tags = self.driver.find_elements(By.TAG_NAME, "script")
            post_data = None
            
            for script in script_tags:
                script_content = script.get_attribute("innerHTML")
                if "window._sharedData" in script_content:
                    # Parse shared data
                    match = re.search(r'window\._sharedData\s*=\s*({.*?});', script_content)
                    if match:
                        try:
                            shared_data = json.loads(match.group(1))
                            post_data = self._extract_post_from_shared_data(shared_data, shortcode)
                            break
                        except json.JSONDecodeError:
                            continue
            
            if not post_data:
                # Fallback to DOM parsing
                post_data = self._extract_post_from_dom(shortcode, post_url)
            
            return post_data
            
        except Exception as e:
            logger.error(f"Instagram post scraping error {post_url}: {e}")
            return None
    
    def _extract_post_from_shared_data(
        self,
        shared_data: Dict[str, Any],
        shortcode: str
    ) -> Optional[InstagramMediaData]:
        """Extract post data from Instagram shared data object."""



        try:
            # Navigate through Instagram's complex shared data structure
            entry_data = shared_data.get('entry_data', {})
            post_page = entry_data.get('PostPage', [])
            
            if not post_page:
                return None
            
            media = post_page[0].get('graphql', {}).get('shortcode_media', {})
            
            if not media:
                return None
            
            # Extract user information
            owner = media.get('owner', {})
            
            # Extract caption
            caption_edges = media.get('edge_media_to_caption', {}).get('edges', [])
            caption = caption_edges[0]['node']['text'] if caption_edges else ""
            
            # Extract hashtags and mentions
            hashtags = re.findall(r'#\w+', caption)
            mentions = re.findall(r'@\w+', caption)
            
            # Extract location
            location = media.get('location')
            location_data = None
            if location:
                location_data = {
                    'id': location.get('id'),
                    'name': location.get('name'),
                    'slug': location.get('slug')
                }
            
            # Determine media type and extract URLs
            media_type = 'IMAGE'
            video_url = None
            thumbnail_url = media.get('display_url')
            duration = None
            
            if media.get('is_video'):
                media_type = 'VIDEO'
                video_url = media.get('video_url')
                duration = media.get('video_duration')
            elif media.get('edge_sidecar_to_children'):
                media_type = 'CAROUSEL_ALBUM'
            
            return InstagramMediaData(
                media_id=media.get('id', ''),
                media_url=video_url or thumbnail_url or '',
                media_type=media_type,
                permalink=f"https://www.instagram.com/p/{shortcode}/",
                caption=caption,
                username=owner.get('username', ''),
                user_id=owner.get('id', ''),
                timestamp=datetime.fromtimestamp(media.get('taken_at_timestamp', 0)),
                like_count=media.get('edge_media_preview_like', {}).get('count', 0),
                comment_count=media.get('edge_media_to_comment', {}).get('count', 0),
                share_count=None,  # Not available
                save_count=None,   # Not available
                hashtags=[tag.replace('#', '') for tag in hashtags],
                mentions=[mention.replace('@', '') for mention in mentions],
                location=location_data,
                thumbnail_url=thumbnail_url,
                video_url=video_url,
                duration=duration,
                dimensions={
                    'height': media.get('dimensions', {}).get('height'),
                    'width': media.get('dimensions', {}).get('width')
                }
            )
            
        except Exception as e:
            logger.error(f"Shared data extraction error: {e}")
            return None
    
    def _extract_post_from_dom(self, shortcode: str, post_url: str) -> Optional[InstagramMediaData]:
        """Fallback method to extract post data from DOM elements."""



        try:
            # Extract basic information from DOM
            # Note: Instagram's DOM structure changes frequently
            
            # Try to find caption
            caption_selectors = [
                "article div div div div span",
                "[data-testid='post-caption'] span",
                "article span[dir='auto']"
            ]
            
            caption = ""
            for selector in caption_selectors:
                try:
                    caption_element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    caption = caption_element.text
                    break
                except:
                    continue
            
            # Try to find username
            username_selectors = [
                "article header div div div a",
                "[data-testid='post-header'] a",
                "article a[role='link']"
            ]
            
            username = ""
            for selector in username_selectors:
                try:
                    username_element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    username = username_element.text
                    break
                except:
                    continue
            
            # Try to find media
            media_url = ""
            media_type = "IMAGE"
            
            # Check for video
            try:
                video_element = self.driver.find_element(By.CSS_SELECTOR, "video")
                media_url = video_element.get_attribute("src")
                media_type = "VIDEO"
            except:
                # Check for image
                try:
                    img_element = self.driver.find_element(By.CSS_SELECTOR, "article img")
                    media_url = img_element.get_attribute("src")
                except:
                    pass
            
            # Extract hashtags and mentions
            hashtags = re.findall(r'#\w+', caption)
            mentions = re.findall(r'@\w+', caption)
            
            return InstagramMediaData(
                media_id=shortcode,
                media_url=media_url,
                media_type=media_type,
                permalink=post_url,
                caption=caption,
                username=username,
                user_id='',
                timestamp=datetime.now(),  # Approximate
                like_count=0,  # Not easily extractable
                comment_count=0,  # Not easily extractable
                share_count=None,
                save_count=None,
                hashtags=[tag.replace('#', '') for tag in hashtags],
                mentions=[mention.replace('@', '') for mention in mentions],
                location=None,
                thumbnail_url=media_url if media_type == "IMAGE" else None,
                video_url=media_url if media_type == "VIDEO" else None,
                duration=None
            )
            
        except Exception as e:
            logger.error(f"DOM extraction error: {e}")
            return None
    
    async def search_hashtag_posts(self, hashtag: str, limit: int = 50) -> List[str]:
        """Search posts by hashtag and return post URLs."""



        try:
            hashtag_url = f"https://www.instagram.com/explore/tags/{hashtag.replace('#', '')}/"
            self.driver.get(hashtag_url)
            
            # Wait for posts to load
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "article a"))
            )
            
            post_urls = []
            collected = 0
            scroll_attempts = 0
            max_scrolls = 10
            
            while collected < limit and scroll_attempts < max_scrolls:
                # Extract post links from current page
                post_elements = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='/p/']")
                
                for element in post_elements:
                    if collected >= limit:
                        break
                    
                    href = element.get_attribute('href')
                    if href and href not in post_urls:
                        post_urls.append(href)
                        collected += 1
                
                # Scroll down to load more posts
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                await asyncio.sleep(3)
                scroll_attempts += 1
            
            return post_urls
            
        except Exception as e:
            logger.error(f"Instagram hashtag search error: {e}")
            return []
    
    def close(self):
        """Clean up Selenium driver."""
        if self.driver:
            self.driver.quit()

class InstagramCrawler(BaseCrawler):
    """Professional Instagram crawler with comprehensive monitoring capabilities."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize Instagram crawler with configuration."""
        super().__init__(config)
        self.api_manager = None
        
        # Initialize API manager if credentials provided
        if all(k in config for k in ['instagram_app_id', 'instagram_app_secret']):
            self.api_manager = InstagramAPIManager(
                app_id=config['instagram_app_id'],
                app_secret=config['instagram_app_secret'],
                access_token=config.get('instagram_access_token')
            )
        
        self.web_scraper = InstagramWebScraper(
            proxy_manager=config.get('proxy_manager')
        )
        self.platform = 'instagram'
    
    async def crawl_post(self, post_url: str) -> Optional[CrawlResult]:
        """Crawl comprehensive data for a specific Instagram post."""



        try:
            # Scrape post data
            post_data = await self.web_scraper.scrape_post_data(post_url)
            if not post_data:
                return None
            
            # Determine content type
            content_type = ContentType.IMAGE.value
            if post_data.media_type == 'VIDEO':
                content_type = ContentType.VIDEO.value
            elif post_data.media_type == 'CAROUSEL_ALBUM':
                content_type = ContentType.MIXED.value
            
            # Create standardized crawl result
            result = CrawlResult(
                url=post_url,
                platform=self.platform,
                content_type=content_type,
                title=post_data.caption[:100] + "..." if len(post_data.caption) > 100 else post_data.caption,
                description=post_data.caption,
                author=post_data.username,
                upload_date=post_data.timestamp,
                view_count=0,  # Not available for Instagram
                duration_ms=post_data.duration * 1000 if post_data.duration else None,
                thumbnail_url=post_data.thumbnail_url,
                tags=post_data.hashtags,
                metadata={
                    'post_data': asdict(post_data),
                    'platform_specific': {
                        'media_id': post_data.media_id,
                        'user_id': post_data.user_id,
                        'media_type': post_data.media_type,
                        'location': post_data.location
                    },
                    'engagement': {
                        'like_count': post_data.like_count,
                        'comment_count': post_data.comment_count,
                        'save_count': post_data.save_count
                    }
                }
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Instagram post crawl error {post_url}: {e}")
            return None
    
    async def search_similar_content(
        self,
        query: str,
        limit: int = 100,
        time_range: Optional[timedelta] = None
    ) -> List[CrawlResult]:
        """Search for potentially infringing content on Instagram."""



        try:
            results = []
            
            # Try API search first if available
            if self.api_manager and self.api_manager.access_token:
                # Note: Instagram API has limited search capabilities
                # This would require a business account and specific permissions
                pass
            
            # Hashtag search through web scraping
            hashtag_urls = await self.web_scraper.search_hashtag_posts(query, limit)
            
            for post_url in hashtag_urls:
                result = await self.crawl_post(post_url)
                if result:
                    # Filter by time range if specified
                    if time_range:
                        cutoff_date = datetime.now() - time_range
                        if result.upload_date and result.upload_date < cutoff_date:
                            continue
                    
                    results.append(result)
                
                # Be respectful with scraping rate
                await asyncio.sleep(2)
            
            return results
            
        except Exception as e:
            logger.error(f"Instagram search crawl error: {e}")
            return []
    
    async def monitor_user(
        self,
        username: str,
        check_period: timedelta = timedelta(hours=24)
    ) -> List[CrawlResult]:
        """Monitor a specific user for new content."""



        try:
            user_url = f"https://www.instagram.com/{username}/"
            self.web_scraper.driver.get(user_url)
            
            # Wait for posts to load
            WebDriverWait(self.web_scraper.driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "article a"))
            )
            
            # Extract recent post URLs
            post_elements = self.web_scraper.driver.find_elements(
                By.CSS_SELECTOR, "a[href*='/p/']"
            )
            
            recent_posts = []
            for element in post_elements[:12]:  # Check last 12 posts
                href = element.get_attribute('href')
                if href:
                    recent_posts.append(href)
            
            # Crawl each post and filter by date
            results = []
            cutoff_date = datetime.now() - check_period
            
            for post_url in recent_posts:
                result = await self.crawl_post(post_url)
                if result and result.upload_date and result.upload_date > cutoff_date:
                    results.append(result)
                await asyncio.sleep(2)
            
            return results
            
        except Exception as e:
            logger.error(f"Instagram user monitoring error {username}: {e}")
            return []
    
    def cleanup(self):
        """Clean up resources."""
        if self.web_scraper:
            self.web_scraper.close()
