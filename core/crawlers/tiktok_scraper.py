"""
TikTok Advanced Scraping Engine
==============================

Professional TikTok content monitoring and scraping system.
Combines official TikTok Business API with advanced scraping techniques
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
class TikTokVideoData:
    """Comprehensive TikTok video metadata structure."""
    
    video_id: str
    video_url: str
    title: str
    description: str
    author_username: str
    author_display_name: str
    author_id: str
    author_verified: bool
    upload_date: datetime
    duration: int  # in seconds
    view_count: int
    like_count: int
    share_count: int
    comment_count: int
    music_title: Optional[str]
    music_author: Optional[str]
    music_id: Optional[str]
    music_duration: Optional[int]
    hashtags: List[str]
    mentions: List[str]
    video_quality: str
    video_format: str
    download_url: Optional[str]
    cover_image_url: str
    
    # Advanced metadata
    effects_used: List[str] = None
    is_ad: bool = False
    language: Optional[str] = None
    region: Optional[str] = None
    device_info: Optional[str] = None

@dataclass
class TikTokUserData:
    """TikTok user profile comprehensive information."""
    
    user_id: str
    username: str
    display_name: str
    bio: str
    follower_count: int
    following_count: int
    video_count: int
    like_count: int
    verified: bool
    avatar_url: str
    banner_url: Optional[str]
    external_links: List[str]
    creation_date: Optional[datetime]
    last_active: Optional[datetime]

class TikTokAPIManager:
    """Professional TikTok API management with business API integration."""
    
    def __init__(self, api_key: Optional[str] = None, client_secret: Optional[str] = None):
        """Initialize TikTok API service with business API credentials."""
        self.api_key = api_key
        self.client_secret = client_secret
        self.access_token = None
        self.rate_limiter = RateLimiter(
            max_calls=100,  # TikTok API rate limit
            time_window=60
        )
        
        if api_key and client_secret:
            asyncio.create_task(self._initialize_business_api())
    
    async def _initialize_business_api(self):
        """Initialize TikTok Business API with OAuth 2.0."""



        try:
            # TikTok Business API OAuth endpoint
            token_url = "https://business-api.tiktok.com/open_api/oauth2/access_token/"
            
            data = {
                'client_key': self.api_key,
                'client_secret': self.client_secret,
                'grant_type': 'client_credentials'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(token_url, json=data) as response:
                    if response.status == 200:
                        result = await response.json()
                        self.access_token = result.get('data', {}).get('access_token')
                        logger.info("TikTok Business API initialized successfully")
                    else:
                        logger.warning("TikTok Business API initialization failed")
                        
        except Exception as e:
            logger.error(f"TikTok Business API initialization error: {e}")
    
    async def search_videos_api(
        self,
        keyword: str,
        max_results: int = 100
    ) -> List[Dict[str, Any]]:
        """Search videos using TikTok Business API."""
        if not self.access_token:
            return []
        
        await self.rate_limiter.acquire()
        
        try:
            search_url = "https://business-api.tiktok.com/open_api/search/video/"
            
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            params = {
                'keyword': keyword,
                'count': min(max_results, 100),
                'offset': 0
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(search_url, headers=headers, params=params) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result.get('data', {}).get('videos', [])
                    else:
                        logger.error(f"TikTok API search failed: {response.status}")
                        return []
                        
        except Exception as e:
            logger.error(f"TikTok API search error: {e}")
            return []

class TikTokWebScraper:
    """Advanced TikTok web scraping with anti-detection measures."""
    
    def __init__(self, proxy_manager: Optional[ProxyManager] = None):
        """Initialize TikTok web scraper with proxy support."""
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
        
        # Random user agents
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        ]
        
        import random
        chrome_options.add_argument(f'--user-agent={random.choice(user_agents)}')
        
        # Proxy configuration
        if self.proxy_manager:
            proxy = self.proxy_manager.get_proxy()
            if proxy:
                chrome_options.add_argument(f'--proxy-server={proxy}')
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    async def scrape_video_data(self, video_url: str) -> Optional[TikTokVideoData]:
        """Scrape comprehensive video data from TikTok video page."""



        try:
            self.driver.get(video_url)
            
            # Wait for content to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "video"))
            )
            
            # Extract video ID from URL
            video_id_match = re.search(r'/video/(\d+)', video_url)
            video_id = video_id_match.group(1) if video_id_match else None
            
            if not video_id:
                return None
            
            # Extract structured data from page
            script_tags = self.driver.find_elements(By.TAG_NAME, "script")
            video_data = None
            
            for script in script_tags:
                script_content = script.get_attribute("innerHTML")
                if "window.__INITIAL_STATE__" in script_content:
                    # Parse initial state data
                    match = re.search(r'window\.__INITIAL_STATE__\s*=\s*({.*?});', script_content)
                    if match:
                        try:
                            initial_state = json.loads(match.group(1))
                            video_data = self._extract_video_from_state(initial_state, video_id)
                            break
                        except json.JSONDecodeError:
                            continue
            
            if not video_data:
                # Fallback to DOM parsing
                video_data = self._extract_video_from_dom(video_id)
            
            return video_data
            
        except Exception as e:
            logger.error(f"TikTok video scraping error {video_url}: {e}")
            return None
    
    def _extract_video_from_state(self, state_data: Dict[str, Any], video_id: str) -> Optional[TikTokVideoData]:
        """Extract video data from TikTok initial state object."""



        try:
            # Navigate through TikTok's complex state structure
            video_detail = None
            
            # Try different paths in the state object
            if 'VideoPage' in state_data:
                video_detail = state_data['VideoPage'].get('videoDetail')
            elif 'ItemModule' in state_data:
                items = state_data['ItemModule']
                video_detail = items.get(video_id)
            
            if not video_detail:
                return None
            
            # Extract user information
            author_info = video_detail.get('author', {})
            
            # Extract music information
            music_info = video_detail.get('music', {})
            
            # Extract statistics
            stats = video_detail.get('stats', {})
            
            # Extract hashtags and mentions
            desc = video_detail.get('desc', '')
            hashtags = re.findall(r'#\w+', desc)
            mentions = re.findall(r'@\w+', desc)
            
            return TikTokVideoData(
                video_id=video_id,
                video_url=f"https://www.tiktok.com/@{author_info.get('uniqueId', '')}/video/{video_id}",
                title=desc[:100] + "..." if len(desc) > 100 else desc,
                description=desc,
                author_username=author_info.get('uniqueId', ''),
                author_display_name=author_info.get('nickname', ''),
                author_id=author_info.get('id', ''),
                author_verified=author_info.get('verified', False),
                upload_date=datetime.fromtimestamp(video_detail.get('createTime', 0)),
                duration=video_detail.get('video', {}).get('duration', 0),
                view_count=stats.get('playCount', 0),
                like_count=stats.get('diggCount', 0),
                share_count=stats.get('shareCount', 0),
                comment_count=stats.get('commentCount', 0),
                music_title=music_info.get('title', ''),
                music_author=music_info.get('authorName', ''),
                music_id=music_info.get('id', ''),
                music_duration=music_info.get('duration', 0),
                hashtags=[tag.replace('#', '') for tag in hashtags],
                mentions=[mention.replace('@', '') for mention in mentions],
                video_quality=video_detail.get('video', {}).get('format', ''),
                video_format='mp4',
                download_url=video_detail.get('video', {}).get('downloadAddr', ''),
                cover_image_url=video_detail.get('video', {}).get('cover', ''),
                effects_used=[],
                is_ad=video_detail.get('isAd', False)
            )
            
        except Exception as e:
            logger.error(f"State data extraction error: {e}")
            return None
    
    def _extract_video_from_dom(self, video_id: str) -> Optional[TikTokVideoData]:
        """Fallback method to extract video data from DOM elements."""



        try:
            # Extract basic information from DOM
            title_element = self.driver.find_element(By.CSS_SELECTOR, "[data-e2e='browse-video-desc']")
            title = title_element.text if title_element else ""
            
            author_element = self.driver.find_element(By.CSS_SELECTOR, "[data-e2e='browse-username']")
            author = author_element.text if author_element else ""
            
            # Extract statistics
            like_element = self.driver.find_element(By.CSS_SELECTOR, "[data-e2e='browse-like-count']")
            like_count = self._parse_count(like_element.text) if like_element else 0
            
            comment_element = self.driver.find_element(By.CSS_SELECTOR, "[data-e2e='browse-comment-count']")
            comment_count = self._parse_count(comment_element.text) if comment_element else 0
            
            share_element = self.driver.find_element(By.CSS_SELECTOR, "[data-e2e='browse-share-count']")
            share_count = self._parse_count(share_element.text) if share_element else 0
            
            # Extract hashtags
            hashtags = re.findall(r'#\w+', title)
            mentions = re.findall(r'@\w+', title)
            
            return TikTokVideoData(
                video_id=video_id,
                video_url=self.driver.current_url,
                title=title,
                description=title,
                author_username=author.replace('@', ''),
                author_display_name=author.replace('@', ''),
                author_id='',
                author_verified=False,
                upload_date=datetime.now(),  # Approximate
                duration=0,
                view_count=0,  # Not available in DOM
                like_count=like_count,
                share_count=share_count,
                comment_count=comment_count,
                music_title='',
                music_author='',
                music_id='',
                music_duration=0,
                hashtags=[tag.replace('#', '') for tag in hashtags],
                mentions=[mention.replace('@', '') for mention in mentions],
                video_quality='',
                video_format='mp4',
                download_url='',
                cover_image_url='',
                effects_used=[],
                is_ad=False
            )
            
        except Exception as e:
            logger.error(f"DOM extraction error: {e}")
            return None
    
    def _parse_count(self, count_text: str) -> int:
        """Parse count strings like '1.2M', '50.3K' to integers."""



        try:
            count_text = count_text.lower().strip()
            if 'm' in count_text:
                return int(float(count_text.replace('m', '')) * 1_000_000)
            elif 'k' in count_text:
                return int(float(count_text.replace('k', '')) * 1_000)
            else:
                return int(count_text)
        except ValueError:
            return 0
    
    async def search_hashtag(self, hashtag: str, limit: int = 100) -> List[str]:
        """Search videos by hashtag and return video URLs."""



        try:
            search_url = f"https://www.tiktok.com/tag/{hashtag.replace('#', '')}"
            self.driver.get(search_url)
            
            # Wait for videos to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[data-e2e='challenge-item']"))
            )
            
            video_urls = []
            collected = 0
            scroll_attempts = 0
            max_scrolls = 10
            
            while collected < limit and scroll_attempts < max_scrolls:
                # Extract video links from current page
                video_elements = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='/video/']")
                
                for element in video_elements:
                    if collected >= limit:
                        break
                    
                    href = element.get_attribute('href')
                    if href and href not in video_urls:
                        video_urls.append(href)
                        collected += 1
                
                # Scroll down to load more videos
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                await asyncio.sleep(2)
                scroll_attempts += 1
            
            return video_urls
            
        except Exception as e:
            logger.error(f"TikTok hashtag search error: {e}")
            return []
    
    def close(self):
        """Clean up Selenium driver."""
        if self.driver:
            self.driver.quit()

class TikTokCrawler(BaseCrawler):
    """Professional TikTok crawler with comprehensive monitoring capabilities."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize TikTok crawler with configuration."""
        super().__init__(config)
        self.api_manager = TikTokAPIManager(
            api_key=config.get('tiktok_api_key'),
            client_secret=config.get('tiktok_client_secret')
        )
        self.web_scraper = TikTokWebScraper(
            proxy_manager=config.get('proxy_manager')
        )
        self.platform = 'tiktok'
    
    async def crawl_video(self, video_url: str) -> Optional[CrawlResult]:
        """Crawl comprehensive data for a specific TikTok video."""



        try:
            # Scrape video data
            video_data = await self.web_scraper.scrape_video_data(video_url)
            if not video_data:
                return None
            
            # Create standardized crawl result
            result = CrawlResult(
                url=video_url,
                platform=self.platform,
                content_type=ContentType.VIDEO.value,
                title=video_data.title,
                description=video_data.description,
                author=video_data.author_username,
                upload_date=video_data.upload_date,
                view_count=video_data.view_count,
                duration_ms=video_data.duration * 1000,
                thumbnail_url=video_data.cover_image_url,
                tags=video_data.hashtags,
                metadata={
                    'video_data': asdict(video_data),
                    'platform_specific': {
                        'video_id': video_data.video_id,
                        'author_id': video_data.author_id,
                        'music_id': video_data.music_id,
                        'is_ad': video_data.is_ad,
                        'effects_used': video_data.effects_used
                    },
                    'engagement': {
                        'like_count': video_data.like_count,
                        'share_count': video_data.share_count,
                        'comment_count': video_data.comment_count
                    }
                }
            )
            
            return result
            
        except Exception as e:
            logger.error(f"TikTok video crawl error {video_url}: {e}")
            return None
    
    async def search_similar_content(
        self,
        query: str,
        limit: int = 100,
        time_range: Optional[timedelta] = None
    ) -> List[CrawlResult]:
        """Search for potentially infringing content on TikTok."""



        try:
            results = []
            
            # Try API search first
            if self.api_manager.access_token:
                api_videos = await self.api_manager.search_videos_api(query, limit // 2)
                for video in api_videos:
                    video_url = video.get('video_url', '')
                    if video_url:
                        result = await self.crawl_video(video_url)
                        if result:
                            results.append(result)
                        await asyncio.sleep(0.5)
            
            # Hashtag search for remaining quota
            if len(results) < limit:
                remaining = limit - len(results)
                hashtag_urls = await self.web_scraper.search_hashtag(query, remaining)
                
                for video_url in hashtag_urls:
                    result = await self.crawl_video(video_url)
                    if result:
                        results.append(result)
                    await asyncio.sleep(1)  # Be respectful with scraping
            
            return results
            
        except Exception as e:
            logger.error(f"TikTok search crawl error: {e}")
            return []
    
    async def monitor_user(
        self,
        username: str,
        check_period: timedelta = timedelta(hours=24)
    ) -> List[CrawlResult]:
        """Monitor a specific user for new content."""



        try:
            user_url = f"https://www.tiktok.com/@{username}"
            self.web_scraper.driver.get(user_url)
            
            # Wait for videos to load
            WebDriverWait(self.web_scraper.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[data-e2e='user-post-item']"))
            )
            
            # Extract recent video URLs
            video_elements = self.web_scraper.driver.find_elements(
                By.CSS_SELECTOR, "a[href*='/video/']"
            )
            
            recent_videos = []
            for element in video_elements[:20]:  # Check last 20 videos
                href = element.get_attribute('href')
                if href:
                    recent_videos.append(href)
            
            # Crawl each video and filter by date
            results = []
            cutoff_date = datetime.now() - check_period
            
            for video_url in recent_videos:
                result = await self.crawl_video(video_url)
                if result and result.upload_date and result.upload_date > cutoff_date:
                    results.append(result)
                await asyncio.sleep(1)
            
            return results
            
        except Exception as e:
            logger.error(f"TikTok user monitoring error {username}: {e}")
            return []
    
    def cleanup(self):
        """Clean up resources."""
        if self.web_scraper:
            self.web_scraper.close()
