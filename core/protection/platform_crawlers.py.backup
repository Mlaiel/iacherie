"""Platform Crawlers & Web Surveillance System

This module provides comprehensive web crawling and surveillance capabilities:
- Multi-platform content monitoring (YouTube, Instagram, TikTok, Twitter, Facebook)
- Intelligent crawling with anti-detection mechanisms
- Real-time violation detection and evidence collection
- Scalable crawler management with rate limiting
- Automated screenshot and metadata capture

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

WARNING: This code is proprietary and confidential. Unauthorized use, reproduction,
or distribution is strictly prohibited and will result in legal action.
Contact: mlaiel@live.de for licensing inquiries.
"""
import asyncio
import json
import random
import time
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import logging
import uuid
from pathlib import Path
import urllib.parse
from concurrent.futures import ThreadPoolExecutor

# Web scraping and automation
import aiohttp
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, WebDriverException
from bs4 import BeautifulSoup
import scrapy
from scrapy.crawler import CrawlerRunner
from scrapy.utils.project import get_project_settings

# Image processing
from PIL import Image
import cv2
import numpy as np

# Internal imports
from ...utils.logging import get_logger
from ...database.models.content import ContentFingerprint, SurveillanceResult
from ...config.settings import get_settings
from .fingerprint_engine import FingerprintEngine
from .evidence_collector import EvidenceCollector

logger = get_logger(__name__)
settings = get_settings()


class CrawlerPlatform(Enum):
    """Supported crawler platforms"""
    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    LINKEDIN = "linkedin"
    PINTEREST = "pinterest"
    REDDIT = "reddit"
    GENERIC_WEB = "generic_web"


class CrawlerType(Enum):
    """Types of crawlers"""
    API_BASED = "api_based"         # Official API access
    SELENIUM_BROWSER = "selenium"   # Browser automation
    REQUESTS_HTTP = "requests"      # HTTP requests
    SCRAPY_SPIDER = "scrapy"        # Scrapy framework


class CrawlerStatus(Enum):
    """Crawler execution status"""
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    ERROR = "error"
    RATE_LIMITED = "rate_limited"
    COMPLETED = "completed"


@dataclass
class CrawlerConfiguration:
    """Configuration for platform crawlers"""
    platform: CrawlerPlatform
    crawler_type: CrawlerType
    
    # Rate limiting
    requests_per_minute: int = 30
    concurrent_requests: int = 3
    delay_between_requests: float = 2.0
    
    # Browser settings (for Selenium)
    headless: bool = True
    window_size: Tuple[int, int] = (1920, 1080)
    user_agent: Optional[str] = None
    proxy_rotation: bool = False
    
    # Search settings
    search_keywords: List[str] = field(default_factory=list)
    search_depth: int = 5  # Number of pages to crawl
    content_types: List[str] = field(default_factory=lambda: ['video', 'image', 'audio'])
    
    # API settings
    api_credentials: Dict[str, str] = field(default_factory=dict)
    api_rate_limits: Dict[str, int] = field(default_factory=dict)
    
    # Evidence collection
    capture_screenshots: bool = True
    download_content: bool = False
    collect_metadata: bool = True


@dataclass
class CrawlResult:
    """Result from a crawling operation"""
    platform: CrawlerPlatform
    url: str
    content_type: str
    title: Optional[str] = None
    description: Optional[str] = None
    author: Optional[str] = None
    upload_date: Optional[datetime] = None
    view_count: Optional[int] = None
    like_count: Optional[int] = None
    share_count: Optional[int] = None
    
    # Content data
    thumbnail_url: Optional[str] = None
    content_url: Optional[str] = None
    content_data: Optional[bytes] = None
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    html_content: Optional[str] = None
    screenshot_path: Optional[str] = None
    
    # Fingerprinting
    fingerprint_hash: Optional[str] = None
    similarity_score: Optional[float] = None
    
    # Timestamps
    crawled_at: datetime = field(default_factory=datetime.utcnow)


class PlatformCrawler:
    """
    Base class for platform-specific crawlers
    
    Provides common functionality for web crawling and content monitoring
    across different social media platforms.
    """
    
    def __init__(self, config: CrawlerConfiguration):
        self.config = config
        self.status = CrawlerStatus.IDLE
        self.executor = ThreadPoolExecutor(max_workers=config.concurrent_requests)
        self.fingerprint_engine = FingerprintEngine()
        self.evidence_collector = EvidenceCollector()
        
        # Rate limiting
        self._last_request_time = 0
        self._request_count = 0
        self._request_times = []
        
        # Browser instances (for Selenium)
        self._browser_pool = []
        self._max_browsers = config.concurrent_requests
        
        # Session (for requests)
        self._session = None
        
        logger.info(f"Initialized {config.platform.value} crawler with {config.crawler_type.value}")
    
    async def start_monitoring(self, fingerprints: List[ContentFingerprint]) -> List[CrawlResult]:
        """Start monitoring for content violations"""
        try:
            self.status = CrawlerStatus.RUNNING
            results = []
            
            for fingerprint in fingerprints:
                # Generate search queries based on content
                search_queries = self._generate_search_queries(fingerprint)
                
                for query in search_queries:
                    # Rate limiting check
                    await self._check_rate_limits()
                    
                    # Perform search
                    search_results = await self._search_content(query)
                    
                    # Process each result
                    for result in search_results:
                        # Check for similarity
                        similarity = await self._check_content_similarity(fingerprint, result)
                        
                        if similarity > 0.7:  # Potential violation
                            result.fingerprint_hash = fingerprint.fingerprint_hash
                            result.similarity_score = similarity
                            results.append(result)
                            
                            # Collect evidence
                            await self._collect_evidence(result)
            
            self.status = CrawlerStatus.COMPLETED
            logger.info(f"Completed monitoring, found {len(results)} potential violations")
            return results
            
        except Exception as e:
            self.status = CrawlerStatus.ERROR
            logger.error(f"Monitoring failed: {e}")
            return []
    
    async def _search_content(self, query: str) -> List[CrawlResult]:
        """Search for content using platform-specific method"""
        if self.config.crawler_type == CrawlerType.API_BASED:
            return await self._api_search(query)
        elif self.config.crawler_type == CrawlerType.SELENIUM_BROWSER:
            return await self._selenium_search(query)
        elif self.config.crawler_type == CrawlerType.REQUESTS_HTTP:
            return await self._requests_search(query)
        else:
            logger.warning(f"Unsupported crawler type: {self.config.crawler_type}")
            return []
    
    async def _api_search(self, query: str) -> List[CrawlResult]:
        """Search using official platform API"""
        results = []
        
        try:
            if self.config.platform == CrawlerPlatform.YOUTUBE:
                results = await self._youtube_api_search(query)
            elif self.config.platform == CrawlerPlatform.INSTAGRAM:
                results = await self._instagram_api_search(query)
            elif self.config.platform == CrawlerPlatform.TWITTER:
                results = await self._twitter_api_search(query)
            else:
                logger.warning(f"API search not implemented for {self.config.platform}")
            
        except Exception as e:
            logger.error(f"API search failed: {e}")
        
        return results
    
    async def _selenium_search(self, query: str) -> List[CrawlResult]:
        """Search using Selenium browser automation"""
        results = []
        browser = None
        
        try:
            browser = await self._get_browser()
            
            if self.config.platform == CrawlerPlatform.YOUTUBE:
                results = await self._youtube_selenium_search(browser, query)
            elif self.config.platform == CrawlerPlatform.INSTAGRAM:
                results = await self._instagram_selenium_search(browser, query)
            elif self.config.platform == CrawlerPlatform.TIKTOK:
                results = await self._tiktok_selenium_search(browser, query)
            else:
                logger.warning(f"Selenium search not implemented for {self.config.platform}")
            
        except Exception as e:
            logger.error(f"Selenium search failed: {e}")
        finally:
            if browser:
                await self._return_browser(browser)
        
        return results
    
    async def _requests_search(self, query: str) -> List[CrawlResult]:
        """Search using HTTP requests"""
        results = []
        
        try:
            if not self._session:
                self._session = aiohttp.ClientSession(
                    timeout=aiohttp.ClientTimeout(total=30),
                    headers={'User-Agent': self._get_user_agent()}
                )
            
            if self.config.platform == CrawlerPlatform.REDDIT:
                results = await self._reddit_requests_search(query)
            elif self.config.platform == CrawlerPlatform.PINTEREST:
                results = await self._pinterest_requests_search(query)
            else:
                logger.warning(f"Requests search not implemented for {self.config.platform}")
            
        except Exception as e:
            logger.error(f"Requests search failed: {e}")
        
        return results
    
    async def _youtube_api_search(self, query: str) -> List[CrawlResult]:
        """YouTube API search implementation"""
        results = []
        
        try:
            from googleapiclient.discovery import build
            
            youtube = build('youtube', 'v3', developerKey=self.config.api_credentials.get('youtube_api_key'))
            
            search_response = youtube.search().list(
                q=query,
                part='id,snippet',
                maxResults=50,
                type='video'
            ).execute()
            
            for item in search_response['items']:
                result = CrawlResult(
                    platform=CrawlerPlatform.YOUTUBE,
                    url=f"https://www.youtube.com/watch?v={item['id']['videoId']}",
                    content_type='video',
                    title=item['snippet']['title'],
                    description=item['snippet']['description'],
                    author=item['snippet']['channelTitle'],
                    upload_date=datetime.fromisoformat(item['snippet']['publishedAt'].replace('Z', '+00:00')),
                    thumbnail_url=item['snippet']['thumbnails']['high']['url'],
                    metadata=item
                )
                results.append(result)
            
        except Exception as e:
            logger.error(f"YouTube API search failed: {e}")
        
        return results
    
    async def _youtube_selenium_search(self, browser: webdriver.Chrome, query: str) -> List[CrawlResult]:
        """YouTube Selenium search implementation"""
        results = []
        
        try:
            # Navigate to YouTube search
            search_url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(query)}"
            browser.get(search_url)
            
            # Wait for results to load
            wait = WebDriverWait(browser, 10)
            wait.until(EC.presence_of_element_located((By.ID, "contents")))
            
            # Scroll to load more results
            for _ in range(3):
                browser.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
                await asyncio.sleep(2)
            
            # Extract video results
            video_elements = browser.find_elements(By.CSS_SELECTOR, "ytd-video-renderer")
            
            for element in video_elements[:20]:  # Limit to first 20 results
                try:
                    title_element = element.find_element(By.CSS_SELECTOR, "h3 a")
                    title = title_element.get_attribute("title")
                    url = title_element.get_attribute("href")
                    
                    channel_element = element.find_element(By.CSS_SELECTOR, "ytd-channel-name a")
                    author = channel_element.text
                    
                    thumbnail_element = element.find_element(By.CSS_SELECTOR, "img")
                    thumbnail_url = thumbnail_element.get_attribute("src")
                    
                    result = CrawlResult(
                        platform=CrawlerPlatform.YOUTUBE,
                        url=url,
                        content_type='video',
                        title=title,
                        author=author,
                        thumbnail_url=thumbnail_url
                    )
                    results.append(result)
                    
                except Exception as e:
                    logger.debug(f"Failed to extract video data: {e}")
                    continue
            
        except Exception as e:
            logger.error(f"YouTube Selenium search failed: {e}")
        
        return results
    
    async def _instagram_selenium_search(self, browser: webdriver.Chrome, query: str) -> List[CrawlResult]:
        """Instagram Selenium search implementation"""
        results = []
        
        try:
            # Instagram search requires login, so we'll use tag search
            search_url = f"https://www.instagram.com/explore/tags/{urllib.parse.quote(query.replace(' ', ''))}"
            browser.get(search_url)
            
            # Wait for posts to load
            wait = WebDriverWait(browser, 10)
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "article")))
            
            # Scroll to load more posts
            for _ in range(3):
                browser.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
                await asyncio.sleep(2)
            
            # Extract post links
            post_links = browser.find_elements(By.CSS_SELECTOR, "article a")
            
            for link in post_links[:20]:  # Limit to first 20 results
                try:
                    post_url = link.get_attribute("href")
                    
                    # Get thumbnail from the link
                    img_element = link.find_element(By.CSS_SELECTOR, "img")
                    thumbnail_url = img_element.get_attribute("src")
                    
                    result = CrawlResult(
                        platform=CrawlerPlatform.INSTAGRAM,
                        url=post_url,
                        content_type='image',  # Could be video, but we'll detect later
                        thumbnail_url=thumbnail_url
                    )
                    results.append(result)
                    
                except Exception as e:
                    logger.debug(f"Failed to extract Instagram post: {e}")
                    continue
            
        except Exception as e:
            logger.error(f"Instagram Selenium search failed: {e}")
        
        return results
    
    async def _tiktok_selenium_search(self, browser: webdriver.Chrome, query: str) -> List[CrawlResult]:
        """TikTok Selenium search implementation"""
        results = []
        
        try:
            search_url = f"https://www.tiktok.com/search?q={urllib.parse.quote(query)}"
            browser.get(search_url)
            
            # Wait for results to load
            wait = WebDriverWait(browser, 10)
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "[data-e2e='search-card-item']")))
            
            # Scroll to load more results
            for _ in range(3):
                browser.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
                await asyncio.sleep(2)
            
            # Extract video results
            video_elements = browser.find_elements(By.CSS_SELECTOR, "[data-e2e='search-card-item']")
            
            for element in video_elements[:20]:  # Limit to first 20 results
                try:
                    link_element = element.find_element(By.CSS_SELECTOR, "a")
                    url = link_element.get_attribute("href")
                    
                    # Extract video details
                    video_element = element.find_element(By.CSS_SELECTOR, "video")
                    thumbnail_url = video_element.get_attribute("poster")
                    
                    result = CrawlResult(
                        platform=CrawlerPlatform.TIKTOK,
                        url=url,
                        content_type='video',
                        thumbnail_url=thumbnail_url
                    )
                    results.append(result)
                    
                except Exception as e:
                    logger.debug(f"Failed to extract TikTok video: {e}")
                    continue
            
        except Exception as e:
            logger.error(f"TikTok Selenium search failed: {e}")
        
        return results
    
    async def _get_browser(self) -> webdriver.Chrome:
        """Get a browser instance from the pool"""
        if self._browser_pool:
            return self._browser_pool.pop()
        
        # Create new browser instance
        options = Options()
        if self.config.headless:
            options.add_argument('--headless')
        
        options.add_argument(f'--window-size={self.config.window_size[0]},{self.config.window_size[1]}')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        
        if self.config.user_agent:
            options.add_argument(f'--user-agent={self.config.user_agent}')
        
        browser = webdriver.Chrome(options=options)
        return browser
    
    async def _return_browser(self, browser: webdriver.Chrome):
        """Return browser to pool or close if pool is full"""
        if len(self._browser_pool) < self._max_browsers:
            self._browser_pool.append(browser)
        else:
            browser.quit()
    
    async def _check_rate_limits(self):
        """Check and enforce rate limiting"""
        current_time = time.time()
        
        # Remove old request times (older than 1 minute)
        self._request_times = [t for t in self._request_times if current_time - t < 60]
        
        # Check if we've exceeded rate limit
        if len(self._request_times) >= self.config.requests_per_minute:
            sleep_time = 60 - (current_time - self._request_times[0])
            if sleep_time > 0:
                logger.info(f"Rate limit reached, sleeping for {sleep_time:.2f} seconds")
                await asyncio.sleep(sleep_time)
        
        # Ensure minimum delay between requests
        if self._last_request_time > 0:
            time_since_last = current_time - self._last_request_time
            if time_since_last < self.config.delay_between_requests:
                await asyncio.sleep(self.config.delay_between_requests - time_since_last)
        
        # Record this request
        self._request_times.append(current_time)
        self._last_request_time = current_time
    
    def _generate_search_queries(self, fingerprint: ContentFingerprint) -> List[str]:
        """Generate search queries based on content fingerprint"""
        queries = []
        
        # Use content metadata to generate queries
        if fingerprint.metadata:
            # Extract title, artist, description, etc.
            title = fingerprint.metadata.get('title', '')
            artist = fingerprint.metadata.get('artist', '')
            description = fingerprint.metadata.get('description', '')
            
            if title:
                queries.append(title)
            if artist:
                queries.append(f"{artist} {title}".strip())
            if description:
                # Extract key phrases from description
                words = description.split()[:10]  # First 10 words
                queries.append(' '.join(words))
        
        # Add generic search terms based on content type
        if fingerprint.content_type.value == 'audio':
            queries.extend(['music', 'song', 'audio'])
        elif fingerprint.content_type.value == 'video':
            queries.extend(['video', 'clip', 'movie'])
        elif fingerprint.content_type.value == 'image':
            queries.extend(['image', 'photo', 'picture'])
        
        # Add user-defined keywords
        queries.extend(self.config.search_keywords)
        
        return list(set(queries))  # Remove duplicates
    
    async def _check_content_similarity(self, fingerprint: ContentFingerprint, result: CrawlResult) -> float:
        """Check similarity between original content and crawled result"""
        try:
            # Download and fingerprint the crawled content
            if result.thumbnail_url:
                # For now, we'll use thumbnail similarity
                thumbnail_data = await self._download_content(result.thumbnail_url)
                if thumbnail_data:
                    # Create temporary fingerprint for comparison
                    temp_fingerprint = await self.fingerprint_engine.create_image_fingerprint(thumbnail_data)
                    
                    # Compare fingerprints
                    similarity = await self.fingerprint_engine.compare_fingerprints(
                        fingerprint.fingerprint_hash, 
                        temp_fingerprint.fingerprint_hash
                    )
                    
                    return similarity
            
            return 0.0
            
        except Exception as e:
            logger.error(f"Similarity check failed: {e}")
            return 0.0
    
    async def _download_content(self, url: str) -> Optional[bytes]:
        """Download content from URL"""
        try:
            if not self._session:
                self._session = aiohttp.ClientSession()
            
            async with self._session.get(url) as response:
                if response.status == 200:
                    return await response.read()
            
        except Exception as e:
            logger.error(f"Content download failed: {e}")
        
        return None
    
    async def _collect_evidence(self, result: CrawlResult):
        """Collect evidence for potential violation"""
        try:
            if self.config.capture_screenshots:
                # Take screenshot of the page
                screenshot_path = await self.evidence_collector.capture_screenshot(result.url)
                result.screenshot_path = screenshot_path
            
            if self.config.collect_metadata:
                # Collect additional metadata
                metadata = await self.evidence_collector.collect_page_metadata(result.url)
                result.metadata.update(metadata)
            
            logger.info(f"Evidence collected for potential violation: {result.url}")
            
        except Exception as e:
            logger.error(f"Evidence collection failed: {e}")
    
    def _get_user_agent(self) -> str:
        """Get user agent string"""
        if self.config.user_agent:
            return self.config.user_agent
        
        # Default user agents for different platforms
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        ]
        
        return random.choice(user_agents)
    
    async def cleanup(self):
        """Cleanup resources"""
        # Close all browsers
        for browser in self._browser_pool:
            browser.quit()
        self._browser_pool.clear()
        
        # Close session
        if self._session:
            await self._session.close()
        
        logger.info(f"Crawler cleanup completed for {self.config.platform.value}")


class CrawlerManager:
    """
    Manages multiple platform crawlers and coordinates monitoring activities
    """
    
    def __init__(self):
        self.crawlers: Dict[CrawlerPlatform, PlatformCrawler] = {}
        self.active_monitoring = set()
        self.executor = ThreadPoolExecutor(max_workers=8)
        
        logger.info("Crawler manager initialized")
    
    def add_crawler(self, config: CrawlerConfiguration):
        """Add a new platform crawler"""
        crawler = PlatformCrawler(config)
        self.crawlers[config.platform] = crawler
        logger.info(f"Added crawler for {config.platform.value}")
    
    async def start_monitoring_all(self, fingerprints: List[ContentFingerprint]) -> Dict[CrawlerPlatform, List[CrawlResult]]:
        """Start monitoring across all configured platforms"""
        results = {}
        
        tasks = []
        for platform, crawler in self.crawlers.items():
            task = asyncio.create_task(crawler.start_monitoring(fingerprints))
            tasks.append((platform, task))
        
        # Wait for all crawlers to complete
        for platform, task in tasks:
            try:
                platform_results = await task
                results[platform] = platform_results
                logger.info(f"Monitoring completed for {platform.value}: {len(platform_results)} results")
            except Exception as e:
                logger.error(f"Monitoring failed for {platform.value}: {e}")
                results[platform] = []
        
        return results
    
    async def cleanup_all(self):
        """Cleanup all crawlers"""
        for crawler in self.crawlers.values():
            await crawler.cleanup()
        
        logger.info("All crawlers cleaned up")
