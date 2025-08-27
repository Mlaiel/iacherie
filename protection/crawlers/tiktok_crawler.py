"""
🎵 TikTok Content Crawler  
========================

Professional TikTok content discovery and monitoring system.
Advanced scraping with anti-detection and content protection focus.

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
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import requests
from urllib.parse import urljoin, urlparse
import random

from .base_crawler import BasePlatformCrawler, CrawlResult, CrawlerStatus

logger = logging.getLogger(__name__)

@dataclass
class TikTokVideoInfo:
    """TikTok video information structure."""
    video_id: str
    url: str
    title: str
    description: str
    author: str
    author_id: str
    view_count: int
    like_count: int
    comment_count: int
    share_count: int
    play_count: int
    created_at: datetime
    duration: float
    music_title: Optional[str] = None
    music_author: Optional[str] = None
    music_url: Optional[str] = None
    hashtags: List[str] = None
    mentions: List[str] = None
    video_url: Optional[str] = None
    cover_url: Optional[str] = None
    is_ad: bool = False
    metadata: Dict[str, Any] = None

@dataclass
class TikTokUserInfo:
    """TikTok user information structure."""
    user_id: str
    username: str
    display_name: str
    bio: str
    follower_count: int
    following_count: int
    like_count: int
    video_count: int
    avatar_url: str
    is_verified: bool = False
    is_private: bool = False

class TikTokAntiDetection:
    """Advanced anti-detection measures for TikTok scraping."""
    
    @staticmethod
    def get_random_user_agent() -> str:
        """Get random realistic user agent."""
        user_agents = [
            'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1',
            'Mozilla/5.0 (Android 11; Mobile; rv:91.0) Gecko/91.0 Firefox/91.0',
            'Mozilla/5.0 (Linux; Android 11; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Mobile Safari/537.36',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Mobile/15E148 Safari/604.1',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        ]
        return random.choice(user_agents)
    
    @staticmethod
    def get_random_viewport() -> tuple:
        """Get random viewport size."""
        viewports = [
            (375, 667),   # iPhone 8
            (414, 896),   # iPhone 11 Pro
            (390, 844),   # iPhone 12
            (360, 640),   # Android
            (1920, 1080), # Desktop
            (1366, 768),  # Laptop
        ]
        return random.choice(viewports)
    
    @staticmethod
    async def random_delay(min_seconds: float = 1.0, max_seconds: float = 3.0):
        """Random delay to mimic human behavior."""
        delay = random.uniform(min_seconds, max_seconds)
        await asyncio.sleep(delay)
    
    @staticmethod
    def setup_stealth_options() -> Options:
        """Setup Chrome options for stealth scraping."""
        options = Options()
        
        # Basic stealth settings
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Disable images and CSS for faster loading
        prefs = {
            "profile.managed_default_content_settings.images": 2,
            "profile.default_content_setting_values.notifications": 2,
            "profile.default_content_settings.popups": 0
        }
        options.add_experimental_option("prefs", prefs)
        
        # Set random user agent
        options.add_argument(f'--user-agent={TikTokAntiDetection.get_random_user_agent()}')
        
        return options

class TikTokSeleniumCrawler:
    """Selenium-based TikTok crawler with anti-detection."""
    
    def __init__(self, headless: bool = True, proxy: Optional[str] = None):
        """Initialize TikTok Selenium crawler."""
        self.headless = headless
        self.proxy = proxy
        self.driver = None
        self.wait = None
        self.base_url = "https://www.tiktok.com"
        
        # Anti-detection
        self.anti_detection = TikTokAntiDetection()
        
        # Rate limiting
        self.last_request_time = 0
        self.min_request_interval = 2.0
    
    def _setup_driver(self) -> webdriver.Chrome:
        """Setup Chrome WebDriver with stealth configuration."""
        options = self.anti_detection.setup_stealth_options()
        
        if self.headless:
            options.add_argument('--headless')
        
        if self.proxy:
            options.add_argument(f'--proxy-server={self.proxy}')
        
        # Set random viewport
        width, height = self.anti_detection.get_random_viewport()
        options.add_argument(f'--window-size={width},{height}')
        
        try:
            driver = webdriver.Chrome(options=options)
            
            # Execute stealth script
            driver.execute_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined,
                });
            """)
            
            driver.set_page_load_timeout(30)
            return driver
            
        except Exception as e:
            logger.error(f"Failed to setup Chrome driver for TikTok: {e}")
            raise
    
    async def _rate_limit(self):
        """Apply rate limiting between requests."""
        current_time = time.time()
        elapsed = current_time - self.last_request_time
        
        if elapsed < self.min_request_interval:
            wait_time = self.min_request_interval - elapsed
            await asyncio.sleep(wait_time)
        
        self.last_request_time = time.time()
    
    async def search_videos(
        self,
        query: str,
        max_results: int = 20,
        sort_by: str = 'recent'
    ) -> List[TikTokVideoInfo]:
        """Search for TikTok videos."""
        if not self.driver:
            self.driver = self._setup_driver()
            self.wait = WebDriverWait(self.driver, 10)
        
        await self._rate_limit()
        
        try:
            # Navigate to search page
            search_url = f"{self.base_url}/search/video"
            self.driver.get(search_url)
            
            # Wait for page load
            await self.anti_detection.random_delay(2, 4)
            
            # Find search input
            search_input = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="search"]'))
            )
            
            # Clear and type search query
            search_input.clear()
            await self._human_type(search_input, query)
            
            # Submit search
            search_input.submit()
            await self.anti_detection.random_delay(3, 5)
            
            # Extract video information
            videos = await self._extract_search_results(max_results)
            
            logger.info(f"Found {len(videos)} TikTok videos for query: {query}")
            return videos
            
        except Exception as e:
            logger.error(f"TikTok search error: {e}")
            return []
    
    async def _human_type(self, element, text: str):
        """Type text with human-like delays."""
        for char in text:
            element.send_keys(char)
            await asyncio.sleep(random.uniform(0.05, 0.15))
    
    async def _extract_search_results(self, max_results: int) -> List[TikTokVideoInfo]:
        """Extract video information from search results."""
        videos = []
        
        try:
            # Scroll to load more videos
            for _ in range(max_results // 10):
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                await self.anti_detection.random_delay(2, 4)
            
            # Find video containers
            video_containers = self.driver.find_elements(
                By.CSS_SELECTOR, 
                '[data-e2e="search_top-item"]'
            )
            
            for container in video_containers[:max_results]:
                try:
                    video_info = await self._extract_video_info(container)
                    if video_info:
                        videos.append(video_info)
                except Exception as e:
                    logger.debug(f"Error extracting video info: {e}")
                    continue
            
            return videos
            
        except Exception as e:
            logger.error(f"Error extracting search results: {e}")
            return []
    
    async def _extract_video_info(self, container) -> Optional[TikTokVideoInfo]:
        """Extract video information from container element."""
        try:
            # Video URL
            link_element = container.find_element(By.CSS_SELECTOR, 'a')
            video_url = link_element.get_attribute('href')
            
            # Extract video ID from URL
            video_id = self._extract_video_id(video_url)
            
            # Title/Description
            try:
                desc_element = container.find_element(
                    By.CSS_SELECTOR, '[data-e2e="search-card-desc"]'
                )
                description = desc_element.text
            except:
                description = ""
            
            # Author
            try:
                author_element = container.find_element(
                    By.CSS_SELECTOR, '[data-e2e="search-card-user-unique-id"]'
                )
                author = author_element.text.replace('@', '')
            except:
                author = ""
            
            # Stats
            stats = await self._extract_video_stats(container)
            
            # Music info
            music_info = await self._extract_music_info(container)
            
            # Create video info object
            video_info = TikTokVideoInfo(
                video_id=video_id,
                url=video_url,
                title=description[:100] if description else "",
                description=description,
                author=author,
                author_id=author,  # Would need profile extraction for real ID
                view_count=stats.get('views', 0),
                like_count=stats.get('likes', 0),
                comment_count=stats.get('comments', 0),
                share_count=stats.get('shares', 0),
                play_count=stats.get('views', 0),
                created_at=datetime.utcnow(),  # Would need actual timestamp
                duration=stats.get('duration', 0),
                music_title=music_info.get('title'),
                music_author=music_info.get('author'),
                hashtags=self._extract_hashtags(description),
                mentions=self._extract_mentions(description),
                metadata={
                    'extracted_at': datetime.utcnow().isoformat(),
                    'extraction_method': 'selenium_search'
                }
            )
            
            return video_info
            
        except Exception as e:
            logger.debug(f"Error extracting video info: {e}")
            return None
    
    def _extract_video_id(self, url: str) -> str:
        """Extract video ID from TikTok URL."""
        # TikTok video URLs: https://www.tiktok.com/@user/video/1234567890
        match = re.search(r'/video/(\d+)', url)
        if match:
            return match.group(1)
        return url.split('/')[-1] if url else ""
    
    async def _extract_video_stats(self, container) -> Dict[str, int]:
        """Extract video statistics."""
        stats = {}
        
        try:
            # Try to find stats elements
            stats_selectors = {
                'views': '[data-e2e="video-views"]',
                'likes': '[data-e2e="like-count"]',
                'comments': '[data-e2e="comment-count"]',
                'shares': '[data-e2e="share-count"]'
            }
            
            for stat_name, selector in stats_selectors.items():
                try:
                    element = container.find_element(By.CSS_SELECTOR, selector)
                    text = element.text
                    stats[stat_name] = self._parse_count(text)
                except:
                    stats[stat_name] = 0
            
        except Exception as e:
            logger.debug(f"Error extracting stats: {e}")
        
        return stats
    
    async def _extract_music_info(self, container) -> Dict[str, str]:
        """Extract music information."""
        music_info = {}
        
        try:
            music_element = container.find_element(
                By.CSS_SELECTOR, '[data-e2e="search-card-music"]'
            )
            music_text = music_element.text
            
            # Parse music text (usually "♪ song - artist")
            if music_text.startswith('♪'):
                music_text = music_text[1:].strip()
                
                if ' - ' in music_text:
                    title, author = music_text.split(' - ', 1)
                    music_info['title'] = title.strip()
                    music_info['author'] = author.strip()
                else:
                    music_info['title'] = music_text
            
        except Exception as e:
            logger.debug(f"Error extracting music info: {e}")
        
        return music_info
    
    def _parse_count(self, text: str) -> int:
        """Parse count text to integer."""
        if not text:
            return 0
        
        # Remove non-numeric characters except K, M, B
        clean_text = re.sub(r'[^\d\.,KMB]', '', text.upper())
        
        try:
            if 'B' in clean_text:
                return int(float(clean_text.replace('B', '')) * 1_000_000_000)
            elif 'M' in clean_text:
                return int(float(clean_text.replace('M', '')) * 1_000_000)
            elif 'K' in clean_text:
                return int(float(clean_text.replace('K', '')) * 1_000)
            else:
                return int(clean_text.replace(',', '').replace('.', ''))
        except:
            return 0
    
    def _extract_hashtags(self, text: str) -> List[str]:
        """Extract hashtags from text."""
        if not text:
            return []
        
        hashtags = re.findall(r'#(\w+)', text)
        return hashtags
    
    def _extract_mentions(self, text: str) -> List[str]:
        """Extract mentions from text."""
        if not text:
            return []
        
        mentions = re.findall(r'@(\w+)', text)
        return mentions
    
    async def scrape_video_page(self, video_url: str) -> Optional[TikTokVideoInfo]:
        """Scrape detailed information from TikTok video page."""
        if not self.driver:
            self.driver = self._setup_driver()
            self.wait = WebDriverWait(self.driver, 10)
        
        await self._rate_limit()
        
        try:
            # Navigate to video
            self.driver.get(video_url)
            await self.anti_detection.random_delay(3, 5)
            
            # Extract detailed video information
            # This would be a more comprehensive extraction
            # For now, return basic info
            video_id = self._extract_video_id(video_url)
            
            return TikTokVideoInfo(
                video_id=video_id,
                url=video_url,
                title="",
                description="",
                author="",
                author_id="",
                view_count=0,
                like_count=0,
                comment_count=0,
                share_count=0,
                play_count=0,
                created_at=datetime.utcnow(),
                duration=0,
                metadata={'method': 'single_page_scrape'}
            )
            
        except Exception as e:
            logger.error(f"Error scraping TikTok video page: {e}")
            return None
    
    def close(self):
        """Close Selenium driver."""
        if self.driver:
            self.driver.quit()
            self.driver = None

class TikTokCrawler(BasePlatformCrawler):
    """
    Professional TikTok Content Crawler
    ===================================
    
    Advanced TikTok content discovery and monitoring system featuring:
    - Stealth web scraping with anti-detection
    - Comprehensive video metadata extraction
    - Music and audio content identification
    - Hashtag and trend analysis
    - User profile monitoring
    - Real-time content discovery
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize TikTok crawler."""
        super().__init__("tiktok", config)
        
        # Scraping configuration
        self.headless = config.get('headless', True)
        self.proxy = config.get('proxy')
        self.max_results_per_search = config.get('max_results_per_search', 50)
        
        # Rate limiting
        self.requests_per_minute = config.get('requests_per_minute', 10)
        self.last_requests = []
        
        # Initialize crawler
        self.selenium_crawler = None
        
        try:
            self.selenium_crawler = TikTokSeleniumCrawler(self.headless, self.proxy)
            logger.info("TikTok Selenium crawler initialized")
        except Exception as e:
            logger.error(f"Failed to initialize TikTok crawler: {e}")
            raise
    
    async def search_content(
        self,
        query: str,
        content_type: str = 'video',
        max_results: int = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[CrawlResult]:
        """Search for content on TikTok."""
        if not self.selenium_crawler:
            raise Exception("TikTok crawler not available")
        
        max_results = max_results or self.max_results_per_search
        
        # Check rate limits
        if not await self.check_rate_limits():
            logger.warning("TikTok rate limit exceeded")
            return []
        
        try:
            # Search videos
            videos = await self.selenium_crawler.search_videos(
                query=query,
                max_results=max_results,
                sort_by=filters.get('sort_by', 'recent') if filters else 'recent'
            )
            
            # Convert to CrawlResult format
            results = []
            for video in videos:
                result = CrawlResult(
                    platform="tiktok",
                    url=video.url,
                    title=video.title,
                    description=video.description,
                    content_type="video",
                    file_url=video.video_url,
                    metadata={
                        'video_id': video.video_id,
                        'author': video.author,
                        'author_id': video.author_id,
                        'view_count': video.view_count,
                        'like_count': video.like_count,
                        'comment_count': video.comment_count,
                        'share_count': video.share_count,
                        'duration': video.duration,
                        'music_title': video.music_title,
                        'music_author': video.music_author,
                        'hashtags': video.hashtags,
                        'mentions': video.mentions,
                        'is_ad': video.is_ad,
                        **(video.metadata or {})
                    },
                    discovered_at=datetime.utcnow(),
                    fingerprint_candidates=[
                        video.url,
                        video.title,
                        video.music_title or '',
                        ' '.join(video.hashtags or [])
                    ]
                )
                results.append(result)
            
            # Update rate limiting
            self.last_requests.append(datetime.utcnow())
            
            logger.info(f"TikTok search '{query}' returned {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"TikTok search error: {e}")
            return []
    
    async def check_rate_limits(self) -> bool:
        """Check if crawler is within rate limits."""
        now = datetime.utcnow()
        
        # Remove requests older than 1 minute
        self.last_requests = [
            req_time for req_time in self.last_requests
            if now - req_time < timedelta(minutes=1)
        ]
        
        return len(self.last_requests) < self.requests_per_minute
    
    async def search_by_hashtag(self, hashtag: str, max_results: int = 20) -> List[CrawlResult]:
        """Search content by hashtag."""
        if not hashtag.startswith('#'):
            hashtag = f"#{hashtag}"
        
        return await self.search_content(
            query=hashtag,
            max_results=max_results,
            filters={'sort_by': 'recent'}
        )
    
    async def search_by_sound(self, sound_name: str, max_results: int = 20) -> List[CrawlResult]:
        """Search content by sound/music."""
        return await self.search_content(
            query=f"sound:{sound_name}",
            max_results=max_results
        )
    
    async def monitor_trending(self, callback_func: callable = None) -> List[CrawlResult]:
        """Monitor trending TikTok content."""
        try:
            # Search for trending content
            trending_results = await self.search_content(
                query="trending",
                max_results=50,
                filters={'sort_by': 'trending'}
            )
            
            if callback_func and trending_results:
                await callback_func(trending_results)
            
            return trending_results
            
        except Exception as e:
            logger.error(f"Error monitoring TikTok trending: {e}")
            return []
    
    async def get_crawler_stats(self) -> Dict[str, Any]:
        """Get crawler statistics."""
        now = datetime.utcnow()
        recent_requests = [
            req for req in self.last_requests
            if now - req < timedelta(hours=1)
        ]
        
        return {
            "platform": "tiktok",
            "requests_last_hour": len(recent_requests),
            "requests_per_minute_limit": self.requests_per_minute,
            "rate_limited": not await self.check_rate_limits(),
            "selenium_active": self.selenium_crawler is not None
        }
    
    def cleanup(self):
        """Cleanup crawler resources."""
        if self.selenium_crawler:
            self.selenium_crawler.close()
        
        logger.info("TikTok crawler cleanup completed")

# Export main classes
__all__ = [
    'TikTokCrawler',
    'TikTokSeleniumCrawler',
    'TikTokVideoInfo',
    'TikTokUserInfo',
    'TikTokAntiDetection'
]
