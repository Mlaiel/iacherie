"""🕷️ Crawlers Manager - IA-Influencer-Agent  
==================================================================
Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
==================================================================

⚠️  COPYRIGHT NOTICE & LEGAL WARNING ⚠️
This code is the exclusive property of Fahed Mlaiel (mlaiel@live.de).
Any unauthorized use, copy, distribution, or modification of this code
without explicit written permission is strictly prohibited and will be
prosecuted to the full extent of the law.

Advanced web crawling system for multi-platform content monitoring.
Provides real-time surveillance across major social media platforms,
video sharing sites, and content distribution networks with
industrial-grade performance and reliability.
"""
from typing import Dict, List, Optional, Any, Union, Callable, Protocol, Set, Tuple
from abc import ABC, abstractmethod
from dataclasses import dataclass, field, asdict
from enum import Enum, IntEnum
from datetime import datetime, timezone, timedelta
import asyncio
import logging
import json
import uuid
import hashlib
import base64
import time
import random
import re
from pathlib import Path
from urllib.parse import urljoin, urlparse, parse_qs, quote, unquote
from urllib.robotparser import RobotFileParser
import mimetypes
import tempfile
import concurrent.futures

# HTTP and web scraping imports
import aiohttp
import requests
from aiohttp import ClientSession, ClientTimeout, TCPConnector
from bs4 import BeautifulSoup, NavigableString, Tag
import lxml
from lxml import html, etree

# Selenium for JavaScript-heavy sites
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException

# Image and media processing
import cv2
import numpy as np
from PIL import Image
import imagehash
import librosa
import magic

# Machine learning and AI
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer

# Network and proxy management
import proxy_crawler
import fake_useragent
from rotating_proxies import RotatingProxySession

# Rate limiting and caching
import redis
from cachetools import TTLCache
from ratelimiter import RateLimiter

# Database integration
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import Column, String, Integer, DateTime, Text, Boolean, Float, LargeBinary

logger = logging.getLogger(__name__)

# =============== ENUMS & CONFIGURATION ===============

class CrawlerManagerStatus(Enum):
    """Crawler manager operational status"""    ACTIVE = "active"
    INACTIVE = "inactive"
    CRAWLING = "crawling"
    PAUSED = "paused"
    ERROR = "error"
    RATE_LIMITED = "rate_limited"
    MAINTENANCE = "maintenance"

class PlatformType(Enum):
    """Supported platforms for crawling"""    YOUTUBE = "youtube"
    SPOTIFY = "spotify"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    SOUNDCLOUD = "soundcloud"
    VIMEO = "vimeo"
    TWITCH = "twitch"
    MEDIUM = "medium"
    WORDPRESS = "wordpress"
    BLOGGER = "blogger"
    LINKEDIN = "linkedin"
    REDDIT = "reddit"
    PINTEREST = "pinterest"
    SNAPCHAT = "snapchat"
    TELEGRAM = "telegram"
    DISCORD = "discord"
    GENERIC_WEB = "generic_web"

class CrawlerMethod(Enum):
    """Crawling methods"""    API_BASED = "api_based"
    WEB_SCRAPING = "web_scraping"
    SELENIUM = "selenium"
    HEADLESS_BROWSER = "headless_browser"
    RSS_FEED = "rss_feed"
    WEBHOOK = "webhook"
    SMART_CRAWLER = "smart_crawler"
    AI_GUIDED = "ai_guided"

class ContentMatchType(Enum):
    """Types of content matches found"""    EXACT_MATCH = "exact_match"
    SIMILAR_MATCH = "similar_match"
    PARTIAL_MATCH = "partial_match"
    METADATA_MATCH = "metadata_match"
    TITLE_MATCH = "title_match"
    DESCRIPTION_MATCH = "description_match"
    HASH_MATCH = "hash_match"
    VISUAL_MATCH = "visual_match"
    AUDIO_MATCH = "audio_match"

class CrawlPriority(IntEnum):
    """Crawling priority levels"""    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4
    CRITICAL = 5

class ProxyType(Enum):
    """Types of proxies"""    HTTP = "http"
    HTTPS = "https"
    SOCKS4 = "socks4"
    SOCKS5 = "socks5"
    ROTATING = "rotating"

@dataclass
class CrawlerManagerConfig:
    """Configuration for crawler manager"""    enabled: bool = True
    max_concurrent_crawlers: int = 20
    crawl_interval_seconds: int = 300
    request_delay_seconds: float = 1.0
    max_retries: int = 3
    timeout_seconds: int = 30
    user_agent_rotation: bool = True
    proxy_enabled: bool = False
    proxy_list: List[str] = field(default_factory=list)
    rate_limits: Dict[str, int] = field(default_factory=dict)
    api_keys: Dict[str, str] = field(default_factory=dict)
    screenshot_enabled: bool = True
    cache_enabled: bool = True
    cache_ttl_seconds: int = 1800

@dataclass
class CrawlerResult:
    """Result from crawler operation"""    result_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    platform: PlatformType = PlatformType.GENERIC_WEB
    crawler_method: CrawlerMethod = CrawlerMethod.WEB_SCRAPING
    search_query: str = ""
    found_urls: List[str] = field(default_factory=list)
    content_matches: List[Dict[str, Any]] = field(default_factory=list)
    total_results: int = 0
    processing_time_ms: float = 0.0
    success: bool = True
    error_message: Optional[str] = None
    crawled_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class PlatformCrawler:
    """Platform-specific crawler configuration"""    platform: PlatformType = PlatformType.GENERIC_WEB
    crawler_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    method: CrawlerMethod = CrawlerMethod.WEB_SCRAPING
    base_url: str = ""
    search_endpoint: str = ""
    api_key: Optional[str] = None
    rate_limit_requests_per_hour: int = 100
    enabled: bool = True
    last_crawl: Optional[datetime] = None
    total_crawls: int = 0
    success_rate: float = 0.0
    configuration: Dict[str, Any] = field(default_factory=dict)

# =============== CORE INTERFACES ===============

class ICrawlerManagerService(ABC):
    """Interface for crawler manager service"""    
    @abstractmethod
    async def initialize(self) -> bool:
        """Initialize crawler manager"""        pass
    
    @abstractmethod
    async def crawl_platform(self, platform: PlatformType, search_terms: List[str]) -> CrawlerResult:
        """Crawl specific platform for content"""        pass
    
    @abstractmethod
    async def monitor_content(self, content_fingerprints: List[str]) -> List[CrawlerResult]:
        """Monitor platforms for specific content fingerprints"""        pass

# =============== PLATFORM-SPECIFIC CRAWLERS ===============

class YouTubeCrawler:
    """YouTube platform crawler using API and web scraping"""    
    def __init__(self, config: CrawlerManagerConfig):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.YouTubeCrawler")
        self.api_key = config.api_keys.get('youtube', '')
        self.base_url = "https://www.googleapis.com/youtube/v3"
        self.rate_limiter = asyncio.Semaphore(100)  # 100 requests per batch
        
    async def search_videos(self, query: str, max_results: int = 50) -> List[Dict[str, Any]]:
        """Search YouTube videos using API"""        results = []
        
        try:
            async with self.rate_limiter:
                if self.api_key:
                    # Use YouTube Data API
                    results = await self._api_search(query, max_results)
                else:
                    # Fallback to web scraping
                    results = await self._web_search(query, max_results)
                    
        except Exception as e:
            self.logger.error(f"YouTube search failed: {e}")
            
        return results
    
    async def _api_search(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Search using YouTube Data API v3"""        results = []
        
        try:
            url = f"{self.base_url}/search"
            params = {
                'part': 'snippet',
                'q': query,
                'maxResults': min(max_results, 50),
                'key': self.api_key,
                'type': 'video'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        for item in data.get('items', []):
                            video_data = {
                                'video_id': item['id']['videoId'],
                                'title': item['snippet']['title'],
                                'description': item['snippet']['description'],
                                'channel': item['snippet']['channelTitle'],
                                'published_at': item['snippet']['publishedAt'],
                                'thumbnail': item['snippet']['thumbnails']['default']['url'],
                                'url': f"https://www.youtube.com/watch?v={item['id']['videoId']}"
                            }
                            results.append(video_data)
                    else:
                        self.logger.warning(f"YouTube API error: {response.status}")
                        
        except Exception as e:
            self.logger.error(f"YouTube API search failed: {e}")
            
        return results
    
    async def _web_search(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Fallback web scraping search"""        results = []
        
        try:
            search_url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
            
            # Use selenium for dynamic content
            options = Options()
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            
            driver = webdriver.Chrome(options=options)
            driver.get(search_url)
            
            # Wait for results to load
            await asyncio.sleep(3)
            
            # Extract video information
            video_elements = driver.find_elements(By.CSS_SELECTOR, 'div#contents ytd-video-renderer')
            
            for element in video_elements[:max_results]:
                try:
                    title_elem = element.find_element(By.CSS_SELECTOR, 'h3 a#video-title')
                    channel_elem = element.find_element(By.CSS_SELECTOR, 'a.yt-simple-endpoint.style-scope.yt-formatted-string')
                    
                    video_data = {
                        'title': title_elem.text,
                        'url': title_elem.get_attribute('href'),
                        'channel': channel_elem.text,
                        'video_id': self._extract_video_id(title_elem.get_attribute('href'))
                    }
                    results.append(video_data)
                    
                except Exception as e:
                    self.logger.warning(f"Failed to extract video data: {e}")
                    continue
            
            driver.quit()
            
        except Exception as e:
            self.logger.error(f"YouTube web search failed: {e}")
            
        return results
    
    def _extract_video_id(self, url: str) -> str:
        """Extract video ID from YouTube URL"""        try:
            parsed = urlparse(url)
            if 'watch' in parsed.path:
                return parse_qs(parsed.query)['v'][0]
            elif 'embed' in parsed.path:
                return parsed.path.split('/')[-1]
        except:
            pass
        return ""

class InstagramCrawler:
    """Instagram platform crawler"""    
    def __init__(self, config: CrawlerManagerConfig):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.InstagramCrawler")
        self.access_token = config.api_keys.get('instagram', '')
        self.base_url = "https://graph.instagram.com"
        
    async def search_posts(self, hashtag: str, max_results: int = 50) -> List[Dict[str, Any]]:
        """Search Instagram posts by hashtag"""        results = []
        
        try:
            if self.access_token:
                results = await self._api_search(hashtag, max_results)
            else:
                results = await self._web_search(hashtag, max_results)
                
        except Exception as e:
            self.logger.error(f"Instagram search failed: {e}")
            
        return results
    
    async def _api_search(self, hashtag: str, max_results: int) -> List[Dict[str, Any]]:
        """Search using Instagram Basic Display API"""        results = []
        
        try:
            # Note: Instagram's API is quite restricted
            # This is a placeholder for actual implementation
            url = f"{self.base_url}/me/media"
            params = {
                'fields': 'id,caption,media_type,media_url,thumbnail_url,permalink',
                'access_token': self.access_token
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        for item in data.get('data', []):
                            post_data = {
                                'post_id': item['id'],
                                'caption': item.get('caption', ''),
                                'media_type': item['media_type'],
                                'media_url': item.get('media_url', ''),
                                'permalink': item['permalink']
                            }
                            results.append(post_data)
                            
        except Exception as e:
            self.logger.error(f"Instagram API search failed: {e}")
            
        return results
    
    async def _web_search(self, hashtag: str, max_results: int) -> List[Dict[str, Any]]:
        """Web scraping fallback (limited due to Instagram's restrictions)"""        results = []
        
        try:
            # Instagram heavily restricts scraping, this is a placeholder
            search_url = f"https://www.instagram.com/explore/tags/{hashtag}/"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            async with aiohttp.ClientSession(headers=headers) as session:
                async with session.get(search_url) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        # Extract what's available from the initial page load
                        scripts = soup.find_all('script', type='application/ld+json')
                        for script in scripts:
                            try:
                                data = json.loads(script.string)
                                # Process structured data
                                if '@type' in data and 'SocialMediaPosting' in data.get('@type', ''):
                                    results.append({
                                        'title': data.get('headline', ''),
                                        'url': data.get('url', ''),
                                        'author': data.get('author', {}).get('name', ''),
                                        'date': data.get('datePublished', '')
                                    })
                            except json.JSONDecodeError:
                                continue
                                
        except Exception as e:
            self.logger.error(f"Instagram web search failed: {e}")
            
        return results

class TikTokCrawler:
    """TikTok platform crawler"""    
    def __init__(self, config: CrawlerManagerConfig):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.TikTokCrawler")
        self.api_key = config.api_keys.get('tiktok', '')
        
    async def search_videos(self, query: str, max_results: int = 50) -> List[Dict[str, Any]]:
        """Search TikTok videos"""        results = []
        
        try:
            if self.api_key:
                results = await self._api_search(query, max_results)
            else:
                results = await self._web_search(query, max_results)
                
        except Exception as e:
            self.logger.error(f"TikTok search failed: {e}")
            
        return results
    
    async def _api_search(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Search using TikTok API"""        results = []
        
        try:
            # TikTok API implementation would go here
            # Note: TikTok's API access is quite restricted
            pass
            
        except Exception as e:
            self.logger.error(f"TikTok API search failed: {e}")
            
        return results
    
    async def _web_search(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Web scraping search for TikTok"""        results = []
        
        try:
            # TikTok web scraping is complex due to their anti-bot measures
            # This would require sophisticated techniques
            pass
            
        except Exception as e:
            self.logger.error(f"TikTok web search failed: {e}")
            
        return results

class SpotifyCrawler:
    """Spotify platform crawler"""    
    def __init__(self, config: CrawlerManagerConfig):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.SpotifyCrawler")
        self.client_id = config.api_keys.get('spotify_client_id', '')
        self.client_secret = config.api_keys.get('spotify_client_secret', '')
        self.access_token = None
        
    async def search_tracks(self, query: str, max_results: int = 50) -> List[Dict[str, Any]]:
        """Search Spotify tracks"""        results = []
        
        try:
            if self.client_id and self.client_secret:
                await self._get_access_token()
                results = await self._api_search(query, max_results)
                
        except Exception as e:
            self.logger.error(f"Spotify search failed: {e}")
            
        return results
    
    async def _get_access_token(self) -> None:
        """Get Spotify access token"""        try:
            auth_url = "https://accounts.spotify.com/api/token"
            
            auth_data = {
                'grant_type': 'client_credentials',
                'client_id': self.client_id,
                'client_secret': self.client_secret
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(auth_url, data=auth_data) as response:
                    if response.status == 200:
                        data = await response.json()
                        self.access_token = data['access_token']
                        
        except Exception as e:
            self.logger.error(f"Spotify token fetch failed: {e}")
    
    async def _api_search(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Search using Spotify Web API"""        results = []
        
        try:
            search_url = "https://api.spotify.com/v1/search"
            headers = {'Authorization': f'Bearer {self.access_token}'}
            
            params = {
                'q': query,
                'type': 'track',
                'limit': min(max_results, 50)
            }
            
            async with aiohttp.ClientSession(headers=headers) as session:
                async with session.get(search_url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        for track in data['tracks']['items']:
                            track_data = {
                                'track_id': track['id'],
                                'name': track['name'],
                                'artists': [artist['name'] for artist in track['artists']],
                                'album': track['album']['name'],
                                'duration_ms': track['duration_ms'],
                                'popularity': track['popularity'],
                                'preview_url': track.get('preview_url'),
                                'external_urls': track['external_urls']
                            }
                            results.append(track_data)
                            
        except Exception as e:
            self.logger.error(f"Spotify API search failed: {e}")
            
        return results

# =============== GENERIC WEB CRAWLER ===============

class GenericWebCrawler:
    """Generic web crawler for any website"""    
    def __init__(self, config: CrawlerManagerConfig):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.GenericWebCrawler")
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        ]
        
    async def crawl_url(self, url: str, search_terms: List[str]) -> Dict[str, Any]:
        """Crawl specific URL for search terms"""        result = {
            'url': url,
            'matches': [],
            'content_preview': '',
            'success': False
        }
        
        try:
            headers = {
                'User-Agent': random.choice(self.user_agents) if self.config.user_agent_rotation else self.user_agents[0]
            }
            
            async with aiohttp.ClientSession(headers=headers, timeout=aiohttp.ClientTimeout(total=self.config.timeout_seconds)) as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        content = await response.text()
                        soup = BeautifulSoup(content, 'html.parser')
                        
                        # Remove scripts and styles
                        for script in soup(["script", "style"]):
                            script.extract()
                        
                        text_content = soup.get_text()
                        
                        # Search for terms
                        matches = []
                        for term in search_terms:
                            if term.lower() in text_content.lower():
                                matches.append({
                                    'term': term,
                                    'count': text_content.lower().count(term.lower()),
                                    'context': self._extract_context(text_content, term)
                                })
                        
                        result.update({
                            'matches': matches,
                            'content_preview': text_content[:500],
                            'success': True,
                            'title': soup.title.string if soup.title else '',
                            'meta_description': self._get_meta_description(soup)
                        })
                        
        except Exception as e:
            self.logger.error(f"Web crawling failed for {url}: {e}")
            result['error'] = str(e)
            
        return result
    
    def _extract_context(self, text: str, term: str, context_length: int = 100) -> List[str]:
        """Extract context around search term"""        contexts = []
        text_lower = text.lower()
        term_lower = term.lower()
        
        start = 0
        while True:
            pos = text_lower.find(term_lower, start)
            if pos == -1:
                break
                
            context_start = max(0, pos - context_length)
            context_end = min(len(text), pos + len(term) + context_length)
            context = text[context_start:context_end].strip()
            
            if context not in contexts:
                contexts.append(context)
                
            start = pos + 1
            
            if len(contexts) >= 3:  # Limit contexts
                break
        
        return contexts
    
    def _get_meta_description(self, soup: BeautifulSoup) -> str:
        """Extract meta description from HTML"""        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc:
            return meta_desc.get('content', '')
        return ''

# =============== MAIN SERVICE IMPLEMENTATION ===============

class CrawlerManagerService(ICrawlerManagerService):
    """Professional crawler manager service"""    
    def __init__(self, config: CrawlerManagerConfig):
        self.config = config
        self.status = CrawlerManagerStatus.INACTIVE
        self.logger = logging.getLogger(f"{__name__}.Service")
        
        # Initialize platform crawlers
        self.crawlers = {
            PlatformType.YOUTUBE: YouTubeCrawler(config),
            PlatformType.INSTAGRAM: InstagramCrawler(config),
            PlatformType.TIKTOK: TikTokCrawler(config),
            PlatformType.SPOTIFY: SpotifyCrawler(config),
            PlatformType.GENERIC_WEB: GenericWebCrawler(config)
        }
        
        # Active crawl tasks
        self.active_crawls: Dict[str, asyncio.Task] = {}
        self.crawl_results: Dict[str, CrawlerResult] = {}
        
    async def initialize(self) -> bool:
        """Initialize crawler manager service"""        try:
            self.logger.info("🚀 Initializing Crawler Manager Service")
            
            # Setup rate limiters for each platform
            self._setup_rate_limiters()
            
            # Initialize proxy rotation if enabled
            if self.config.proxy_enabled:
                await self._setup_proxy_rotation()
            
            self.status = CrawlerManagerStatus.ACTIVE
            self.logger.info("✅ Crawler Manager Service initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Crawler Manager initialization failed: {e}")
            self.status = CrawlerManagerStatus.ERROR
            return False
    
    async def crawl_platform(self, platform: PlatformType, search_terms: List[str]) -> CrawlerResult:
        """Crawl specific platform for search terms"""        crawler_result = CrawlerResult(
            platform=platform,
            search_query=' '.join(search_terms)
        )
        
        try:
            self.status = CrawlerManagerStatus.CRAWLING
            start_time = time.time()
            
            crawler = self.crawlers.get(platform)
            if not crawler:
                raise ValueError(f"No crawler available for platform: {platform}")
            
            self.logger.info(f"🕷️ Crawling {platform.value} for terms: {search_terms}")
            
            # Execute platform-specific crawling
            if platform == PlatformType.YOUTUBE:
                for term in search_terms:
                    results = await crawler.search_videos(term)
                    crawler_result.content_matches.extend(results)
                    crawler_result.found_urls.extend([r.get('url', '') for r in results])
            elif platform == PlatformType.INSTAGRAM:
                for term in search_terms:
                    results = await crawler.search_posts(term)
                    crawler_result.content_matches.extend(results)
                    crawler_result.found_urls.extend([r.get('permalink', '') for r in results])
            elif platform == PlatformType.SPOTIFY:
                for term in search_terms:
                    results = await crawler.search_tracks(term)
                    crawler_result.content_matches.extend(results)
                    crawler_result.found_urls.extend([r.get('external_urls', {}).get('spotify', '') for r in results])
            
            crawler_result.total_results = len(crawler_result.content_matches)
            crawler_result.processing_time_ms = (time.time() - start_time) * 1000
            crawler_result.success = True
            
            self.status = CrawlerManagerStatus.ACTIVE
            self.logger.info(f"✅ Platform crawl completed: {crawler_result.total_results} results found")
            
        except Exception as e:
            self.logger.error(f"❌ Platform crawling failed: {e}")
            crawler_result.success = False
            crawler_result.error_message = str(e)
            self.status = CrawlerManagerStatus.ERROR
            
        return crawler_result
    
    async def monitor_content(self, content_fingerprints: List[str]) -> List[CrawlerResult]:
        """Monitor platforms for specific content fingerprints"""        all_results = []
        
        try:
            self.logger.info(f"🔍 Monitoring {len(content_fingerprints)} content fingerprints")
            
            # Create monitoring tasks for each platform
            monitor_tasks = []
            for platform in [PlatformType.YOUTUBE, PlatformType.INSTAGRAM, PlatformType.TIKTOK]:
                task = asyncio.create_task(self._monitor_platform_for_fingerprints(platform, content_fingerprints))
                monitor_tasks.append(task)
            
            # Execute monitoring tasks
            results = await asyncio.gather(*monitor_tasks, return_exceptions=True)
            
            for result in results:
                if isinstance(result, list):
                    all_results.extend(result)
                elif isinstance(result, Exception):
    proxy_rotation: bool = False
    proxy_list: List[str] = field(default_factory=list)
    respect_robots_txt: bool = True
    javascript_support: bool = True
    download_media: bool = False
    media_storage_path: str = "/tmp/crawler_media"
    enable_caching: bool = True
    cache_ttl_hours: int = 24
    enable_content_analysis: bool = True
    similarity_threshold: float = 0.85
    max_depth: int = 3
    follow_redirects: bool = True
    custom_headers: Dict[str, str] = field(default_factory=dict)
    rate_limits: Dict[str, int] = field(default_factory=lambda: {
        'youtube': 1000,
        'instagram': 200,
        'tiktok': 100,
        'twitter': 300,
        'facebook': 200,
        'soundcloud': 500,
        'generic_web': 100
    })

@dataclass
class CrawlTarget:
    """Target for crawling operations"""    target_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    platform: PlatformType = PlatformType.GENERIC_WEB
    search_queries: List[str] = field(default_factory=list)
    target_urls: List[str] = field(default_factory=list)
    content_fingerprints: List[str] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)
    priority: CrawlPriority = CrawlPriority.NORMAL
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_crawled: Optional[datetime] = None
    crawl_frequency_hours: int = 24
    is_active: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class CrawlResult:
    """Result from a crawling operation"""    result_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    target_id: str = ""
    platform: PlatformType = PlatformType.GENERIC_WEB
    url: str = ""
    title: str = ""
    description: str = ""
    content_text: str = ""
    content_hash: str = ""
    media_urls: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    match_type: ContentMatchType = ContentMatchType.PARTIAL_MATCH
    similarity_score: float = 0.0
    crawl_timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    response_time_ms: float = 0.0
    status_code: int = 200
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary"""        return {
            'result_id': self.result_id,
            'target_id': self.target_id,
            'platform': self.platform.value,
            'url': self.url,
            'title': self.title,
            'description': self.description,
            'content_hash': self.content_hash,
            'match_type': self.match_type.value,
            'similarity_score': self.similarity_score,
            'crawl_timestamp': self.crawl_timestamp.isoformat(),
            'response_time_ms': self.response_time_ms,
            'status_code': self.status_code,
            'error_message': self.error_message
        }


class UserAgentRotator:
    """Advanced user agent rotation system"""    
    def __init__(self):
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15'
        ]
        self.current_index = 0
    
    def get_user_agent(self) -> str:
        """Get next user agent in rotation"""        user_agent = self.user_agents[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.user_agents)
        return user_agent
    
    def get_random_user_agent(self) -> str:
        """Get random user agent"""        return random.choice(self.user_agents)


class ProxyManager:
    """Advanced proxy management system"""    
    def __init__(self, proxy_list: List[str]):
        self.proxy_list = proxy_list
        self.current_index = 0
        self.failed_proxies = set()
        self.proxy_stats = {}
    
    def get_next_proxy(self) -> Optional[str]:
        """Get next working proxy"""        attempts = 0
        max_attempts = len(self.proxy_list)
        
        while attempts < max_attempts:
            proxy = self.proxy_list[self.current_index]
            self.current_index = (self.current_index + 1) % len(self.proxy_list)
            
            if proxy not in self.failed_proxies:
                return proxy
            
            attempts += 1
        
        return None  # No working proxies available
    
    def mark_proxy_failed(self, proxy: str):
        """Mark proxy as failed"""        self.failed_proxies.add(proxy)
        logger.warning(f"Marked proxy as failed: {proxy}")
    
    def reset_failed_proxies(self):
        """Reset failed proxies (for retry logic)"""        self.failed_proxies.clear()
        logger.info("Reset failed proxy list")


class ContentAnalyzer:
    """Advanced content analysis for similarity detection"""    
    def __init__(self):
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 3)
        )
        self.stemmer = PorterStemmer()
    
    def analyze_text_similarity(self, text1: str, text2: str) -> float:
        """Calculate text similarity using TF-IDF and cosine similarity"""        try:
            if not text1 or not text2:
                return 0.0
            
            # Preprocess texts
            texts = [self._preprocess_text(text1), self._preprocess_text(text2)]
            
            # Calculate TF-IDF vectors
            tfidf_matrix = self.tfidf_vectorizer.fit_transform(texts)
            
            # Calculate cosine similarity
            similarity_matrix = cosine_similarity(tfidf_matrix)
            return float(similarity_matrix[0, 1])
            
        except Exception as e:
            logger.error(f"Error calculating text similarity: {str(e)}")
            return 0.0
    
    def _preprocess_text(self, text: str) -> str:
        """Preprocess text for analysis"""        try:
            # Convert to lowercase and tokenize
            tokens = word_tokenize(text.lower())
            
            # Remove stopwords and stem
            stop_words = set(stopwords.words('english'))
            filtered_tokens = [
                self.stemmer.stem(token) 
                for token in tokens 
                if token.isalnum() and token not in stop_words
            ]
            
            return ' '.join(filtered_tokens)
            
        except Exception as e:
            logger.error(f"Error preprocessing text: {str(e)}")
            return text.lower()
    
    def analyze_image_similarity(self, image_path1: str, image_path2: str) -> float:
        """Calculate image similarity using perceptual hashing"""        try:
            with Image.open(image_path1) as img1, Image.open(image_path2) as img2:
                # Calculate perceptual hashes
                hash1 = imagehash.phash(img1)
                hash2 = imagehash.phash(img2)
                
                # Calculate similarity (Hamming distance)
                hamming_distance = hash1 - hash2
                
                # Convert to similarity score (0-1)
                max_distance = len(str(hash1)) * 4  # 4 bits per hex character
                similarity = 1.0 - (hamming_distance / max_distance)
                
                return max(0.0, similarity)
                
        except Exception as e:
            logger.error(f"Error calculating image similarity: {str(e)}")
            return 0.0


class SeleniumCrawler:
    """Advanced Selenium-based crawler for JavaScript-heavy sites"""    
    def __init__(self, config: CrawlerManagerConfig):
        self.config = config
        self.driver = None
        self.user_agent_rotator = UserAgentRotator()
    
    async def initialize(self):
        """Initialize Selenium driver"""        try:
            options = ChromeOptions()
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--disable-extensions')
            options.add_argument('--disable-plugins')
            options.add_argument('--disable-images')
            options.add_argument('--disable-javascript')
            
            # Add user agent
            if self.config.user_agent_rotation:
                user_agent = self.user_agent_rotator.get_user_agent()
                options.add_argument(f'--user-agent={user_agent}')
            
            # Add custom headers
            if self.config.custom_headers:
                for header, value in self.config.custom_headers.items():
                    options.add_argument(f'--header={header}:{value}')
            
            self.driver = webdriver.Chrome(options=options)
            self.driver.set_page_load_timeout(self.config.timeout_seconds)
            
            logger.info("Selenium crawler initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing Selenium crawler: {str(e)}")
            raise
    
    async def crawl_url(self, url: str, wait_for_element: str = None) -> Dict[str, Any]:
        """Crawl URL using Selenium"""        try:
            if not self.driver:
                await self.initialize()
            
            start_time = time.time()
            
            # Navigate to URL
            self.driver.get(url)
            
            # Wait for specific element if specified
            if wait_for_element:
                wait = WebDriverWait(self.driver, 10)
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, wait_for_element)))
            
            # Extract content
            title = self.driver.title
            page_source = self.driver.page_source
            
            # Parse with BeautifulSoup for structured extraction
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # Extract text content
            text_content = soup.get_text(strip=True)
            
            # Extract metadata
            meta_description = ""
            meta_tag = soup.find('meta', attrs={'name': 'description'})
            if meta_tag and meta_tag.get('content'):
                meta_description = meta_tag['content']
            
            # Extract media URLs
            media_urls = []
            for img in soup.find_all('img', src=True):
                img_url = urljoin(url, img['src'])
                media_urls.append(img_url)
            
            for video in soup.find_all('video', src=True):
                video_url = urljoin(url, video['src'])
                media_urls.append(video_url)
            
            response_time = (time.time() - start_time) * 1000
            
            return {
                'url': url,
                'title': title,
                'description': meta_description,
                'content_text': text_content,
                'media_urls': media_urls,
                'response_time_ms': response_time,
                'status_code': 200,
                'method': 'selenium'
            }
            
        except TimeoutException:
            logger.error(f"Timeout crawling URL with Selenium: {url}")
            return {'url': url, 'error': 'timeout', 'status_code': 408}
        except Exception as e:
            logger.error(f"Error crawling URL with Selenium: {str(e)}")
            return {'url': url, 'error': str(e), 'status_code': 500}
    
    def cleanup(self):
        """Cleanup Selenium resources"""        try:
            if self.driver:
                self.driver.quit()
                self.driver = None
            logger.info("Selenium crawler cleaned up")
        except Exception as e:
            logger.error(f"Error cleaning up Selenium crawler: {str(e)}")


class PlatformSpecificCrawler:
    """Platform-specific crawling logic"""    
    def __init__(self, platform: PlatformType, session: ClientSession):
        self.platform = platform
        self.session = session
        self.content_analyzer = ContentAnalyzer()
    
    async def search_content(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search for content on specific platform"""        try:
            if self.platform == PlatformType.YOUTUBE:
                return await self._search_youtube(query, limit)
            elif self.platform == PlatformType.INSTAGRAM:
                return await self._search_instagram(query, limit)
            elif self.platform == PlatformType.TWITTER:
                return await self._search_twitter(query, limit)
            elif self.platform == PlatformType.TIKTOK:
                return await self._search_tiktok(query, limit)
            elif self.platform == PlatformType.SOUNDCLOUD:
                return await self._search_soundcloud(query, limit)
            else:
                return await self._search_generic_web(query, limit)
                
        except Exception as e:
            logger.error(f"Error searching {self.platform.value}: {str(e)}")
            return []
    
    async def _search_youtube(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """Search YouTube (web scraping approach)"""        try:
            search_url = f"https://www.youtube.com/results?search_query={quote(query)}"
            
            async with self.session.get(search_url) as response:
                if response.status == 200:
                    html_content = await response.text()
                    soup = BeautifulSoup(html_content, 'html.parser')
                    
                    results = []
                    video_containers = soup.find_all('div', class_='ytd-video-renderer')
                    
                    for container in video_containers[:limit]:
                        try:
                            # Extract video information
                            title_element = container.find('h3', class_='ytd-video-meta-block')
                            title = title_element.get_text(strip=True) if title_element else "Unknown"
                            
                            link_element = container.find('a', {'id': 'video-title'})
                            video_url = urljoin('https://www.youtube.com', link_element['href']) if link_element else ""
                            
                            description_element = container.find('div', class_='metadata-snippet-text')
                            description = description_element.get_text(strip=True) if description_element else ""
                            
                            results.append({
                                'platform': 'youtube',
                                'title': title,
                                'url': video_url,
                                'description': description,
                                'type': 'video'
                            })
                            
                        except Exception as e:
                            logger.error(f"Error parsing YouTube video container: {str(e)}")
                            continue
                    
                    return results
                    
        except Exception as e:
            logger.error(f"Error searching YouTube: {str(e)}")
            return []
    
    async def _search_instagram(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """Search Instagram (limited web scraping)"""        try:
            # Instagram heavily restricts scraping, so this is a simplified approach
            # In production, you'd use Instagram's official API
            
            search_url = f"https://www.instagram.com/explore/tags/{quote(query.replace('#', ''))}"
            
            async with self.session.get(search_url) as response:
                if response.status == 200:
                    html_content = await response.text()
                    
                    # Look for JSON data in script tags (Instagram embeds data this way)
                    soup = BeautifulSoup(html_content, 'html.parser')
                    script_tags = soup.find_all('script', type='text/javascript')
                    
                    results = []
                    for script in script_tags:
                        if script.string and 'window._sharedData' in script.string:
                            # Parse JSON data (simplified)
                            # In real implementation, you'd properly parse the JSON structure
                            results.append({
                                'platform': 'instagram',
                                'title': f"Instagram post for #{query}",
                                'url': search_url,
                                'description': f"Hashtag search results for {query}",
                                'type': 'social_post'
                            })
                            break
                    
                    return results[:limit]
                    
        except Exception as e:
            logger.error(f"Error searching Instagram: {str(e)}")
            return []
    
    async def _search_twitter(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """Search Twitter (web scraping approach)"""        try:
            # Note: Twitter has strict API policies, this is a simplified example
            search_url = f"https://twitter.com/search?q={quote(query)}&src=typed_query"
            
            # Twitter requires JavaScript, so this would need Selenium in practice
            results = [{
                'platform': 'twitter',
                'title': f"Twitter search for: {query}",
                'url': search_url,
                'description': f"Search results for '{query}' on Twitter",
                'type': 'social_search'
            }]
            
            return results[:limit]
            
        except Exception as e:
            logger.error(f"Error searching Twitter: {str(e)}")
            return []
    
    async def _search_tiktok(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """Search TikTok (web scraping approach)"""        try:
            # TikTok heavily uses JavaScript, would need Selenium for full functionality
            search_url = f"https://www.tiktok.com/search?q={quote(query)}"
            
            results = [{
                'platform': 'tiktok',
                'title': f"TikTok search for: {query}",
                'url': search_url,
                'description': f"Search results for '{query}' on TikTok",
                'type': 'video_search'
            }]
            
            return results[:limit]
            
        except Exception as e:
            logger.error(f"Error searching TikTok: {str(e)}")
            return []
    
    async def _search_soundcloud(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """Search SoundCloud (web scraping approach)"""        try:
            search_url = f"https://soundcloud.com/search?q={quote(query)}"
            
            async with self.session.get(search_url) as response:
                if response.status == 200:
                    html_content = await response.text()
                    soup = BeautifulSoup(html_content, 'html.parser')
                    
                    results = []
                    track_containers = soup.find_all('div', class_='searchList__item')
                    
                    for container in track_containers[:limit]:
                        try:
                            title_element = container.find('a', class_='trackItem__trackTitle')
                            title = title_element.get_text(strip=True) if title_element else "Unknown Track"
                            
                            url_element = container.find('a', class_='trackItem__trackTitle')
                            track_url = urljoin('https://soundcloud.com', url_element['href']) if url_element and url_element.get('href') else ""
                            
                            artist_element = container.find('a', class_='trackItem__username')
                            artist = artist_element.get_text(strip=True) if artist_element else "Unknown Artist"
                            
                            results.append({
                                'platform': 'soundcloud',
                                'title': f"{title} by {artist}",
                                'url': track_url,
                                'description': f"Audio track by {artist}",
                                'type': 'audio'
                            })
                            
                        except Exception as e:
                            logger.error(f"Error parsing SoundCloud track: {str(e)}")
                            continue
                    
                    return results
                    
        except Exception as e:
            logger.error(f"Error searching SoundCloud: {str(e)}")
            return []
    
    async def _search_generic_web(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """Search generic web using search engines"""        try:
            # Use DuckDuckGo as it's more crawler-friendly
            search_url = f"https://html.duckduckgo.com/html/?q={quote(query)}"
            
            async with self.session.get(search_url) as response:
                if response.status == 200:
                    html_content = await response.text()
                    soup = BeautifulSoup(html_content, 'html.parser')
                    
                    results = []
                    result_containers = soup.find_all('div', class_='result')
                    
                    for container in result_containers[:limit]:
                        try:
                            title_element = container.find('a', class_='result__a')
                            title = title_element.get_text(strip=True) if title_element else "Unknown"
                            
                            url = title_element['href'] if title_element and title_element.get('href') else ""
                            
                            snippet_element = container.find('a', class_='result__snippet')
                            description = snippet_element.get_text(strip=True) if snippet_element else ""
                            
                            results.append({
                                'platform': 'web_search',
                                'title': title,
                                'url': url,
                                'description': description,
                                'type': 'web_page'
                            })
                            
                        except Exception as e:
                            logger.error(f"Error parsing web search result: {str(e)}")
                            continue
                    
                    return results
                    
        except Exception as e:
            logger.error(f"Error searching web: {str(e)}")
            return []


class CrawlerManager:
    """Advanced crawler manager coordinating all crawling operations"""    
    def __init__(self, config: CrawlerManagerConfig):
        self.config = config
        self.status = CrawlerManagerStatus.INACTIVE
        
        # Initialize components
        self.user_agent_rotator = UserAgentRotator()
        self.proxy_manager = ProxyManager(config.proxy_list) if config.proxy_list else None
        self.content_analyzer = ContentAnalyzer()
        self.selenium_crawler = SeleniumCrawler(config) if config.javascript_support else None
        
        # Session management
        self.session = None
        self.platform_crawlers: Dict[PlatformType, PlatformSpecificCrawler] = {}
        
        # Crawl management
        self.active_crawls: Set[str] = set()
        self.crawl_results: Dict[str, CrawlResult] = {}
        self.crawl_cache = TTLCache(maxsize=1000, ttl=config.cache_ttl_hours * 3600)
        
        # Rate limiting
        self.rate_limiters: Dict[PlatformType, RateLimiter] = {}
        self._setup_rate_limiters()
        
        # Statistics
        self.crawl_stats = {
            'total_crawls': 0,
            'successful_crawls': 0,
            'failed_crawls': 0,
            'total_results': 0,
            'platforms_active': 0
        }
    
    def _setup_rate_limiters(self):
        """Setup rate limiters for each platform"""        for platform_str, limit in self.config.rate_limits.items():
            try:
                platform = PlatformType(platform_str)
                # Create rate limiter (limit per hour)
                self.rate_limiters[platform] = RateLimiter(max_calls=limit, period=3600)
            except ValueError:
                logger.warning(f"Unknown platform in rate limits: {platform_str}")
    
    async def initialize(self):
        """Initialize the crawler manager"""        try:
            self.status = CrawlerManagerStatus.ACTIVE
            
            # Setup HTTP session
            timeout = ClientTimeout(total=self.config.timeout_seconds)
            connector = TCPConnector(limit=self.config.max_concurrent_crawlers)
            
            headers = {
                'User-Agent': self.user_agent_rotator.get_user_agent()
            }
            headers.update(self.config.custom_headers)
            
            self.session = ClientSession(
                timeout=timeout,
                connector=connector,
                headers=headers
            )
            
            # Initialize platform-specific crawlers
            for platform in PlatformType:
                if platform != PlatformType.GENERIC_WEB:
                    self.platform_crawlers[platform] = PlatformSpecificCrawler(platform, self.session)
            
            # Initialize Selenium crawler if needed
            if self.selenium_crawler:
                await self.selenium_crawler.initialize()
            
            logger.info("Crawler manager initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing crawler manager: {str(e)}")
            self.status = CrawlerManagerStatus.ERROR
            raise
    
    async def crawl_target(self, target: CrawlTarget) -> List[CrawlResult]:
        """Crawl a specific target"""        try:
            if self.status != CrawlerManagerStatus.ACTIVE:
                raise RuntimeError("Crawler manager is not active")
            
            self.status = CrawlerManagerStatus.CRAWLING
            target_id = target.target_id
            
            if target_id in self.active_crawls:
                logger.warning(f"Target {target_id} is already being crawled")
                return []
            
            self.active_crawls.add(target_id)
            results = []
            
            try:
                # Check rate limiting
                if target.platform in self.rate_limiters:
                    with self.rate_limiters[target.platform]:
                        # Execute crawl based on platform
                        if target.platform in self.platform_crawlers:
                            platform_results = await self._crawl_platform_target(target)
                            results.extend(platform_results)
                        
                        # Handle direct URLs
                        if target.target_urls:
                            url_results = await self._crawl_urls(target.target_urls, target)
                            results.extend(url_results)
                else:
                    # No rate limiting for this platform
                    if target.platform in self.platform_crawlers:
                        platform_results = await self._crawl_platform_target(target)
                        results.extend(platform_results)
                    
                    if target.target_urls:
                        url_results = await self._crawl_urls(target.target_urls, target)
                        results.extend(url_results)
                
                # Update statistics
                self.crawl_stats['total_crawls'] += 1
                if results:
                    self.crawl_stats['successful_crawls'] += 1
                    self.crawl_stats['total_results'] += len(results)
                
                # Cache results
                for result in results:
                    self.crawl_results[result.result_id] = result
                    if self.config.enable_caching:
                        cache_key = f"{target.platform.value}:{hashlib.md5(result.url.encode()).hexdigest()}"
                        self.crawl_cache[cache_key] = result
                
                # Update target
                target.last_crawled = datetime.now(timezone.utc)
                
                logger.info(f"Crawled target {target_id}: {len(results)} results")
                return results
                
            finally:
                self.active_crawls.discard(target_id)
                self.status = CrawlerManagerStatus.ACTIVE
                
        except Exception as e:
            logger.error(f"Error crawling target {target.target_id}: {str(e)}")
            self.crawl_stats['failed_crawls'] += 1
            return []
    
    async def _crawl_platform_target(self, target: CrawlTarget) -> List[CrawlResult]:
        """Crawl target on specific platform"""        try:
            results = []
            platform_crawler = self.platform_crawlers.get(target.platform)
            
            if not platform_crawler:
                return results
            
            # Search using queries
            for query in target.search_queries:
                try:
                    search_results = await platform_crawler.search_content(query, limit=10)
                    
                    for search_result in search_results:
                        crawl_result = CrawlResult(
                            target_id=target.target_id,
                            platform=target.platform,
                            url=search_result.get('url', ''),
                            title=search_result.get('title', ''),
                            description=search_result.get('description', ''),
                            metadata=search_result,
                            match_type=ContentMatchType.PARTIAL_MATCH
                        )
                        
                        # Calculate content hash
                        content = f"{crawl_result.title} {crawl_result.description}"
                        crawl_result.content_hash = hashlib.sha256(content.encode()).hexdigest()
                        
                        # Analyze similarity if we have reference content
                        if target.keywords:
                            reference_text = ' '.join(target.keywords)
                            similarity = self.content_analyzer.analyze_text_similarity(
                                content, reference_text
                            )
                            crawl_result.similarity_score = similarity
                            
                            if similarity > self.config.similarity_threshold:
                                crawl_result.match_type = ContentMatchType.SIMILAR_MATCH
                        
                        results.append(crawl_result)
                        
                except Exception as e:
                    logger.error(f"Error searching platform {target.platform.value} with query '{query}': {str(e)}")
                    continue
            
            return results
            
        except Exception as e:
            logger.error(f"Error crawling platform target: {str(e)}")
            return []
    
    async def _crawl_urls(self, urls: List[str], target: CrawlTarget) -> List[CrawlResult]:
        """Crawl specific URLs"""        try:
            results = []
            
            # Process URLs concurrently
            semaphore = asyncio.Semaphore(self.config.max_concurrent_crawlers)
            tasks = [self._crawl_single_url(semaphore, url, target) for url in urls]
            
            crawl_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for result in crawl_results:
                if isinstance(result, CrawlResult):
                    results.append(result)
                elif isinstance(result, Exception):
                    logger.error(f"URL crawl failed: {str(result)}")
            
            return results
            
        except Exception as e:
            logger.error(f"Error crawling URLs: {str(e)}")
            return []
    
    async def _crawl_single_url(self, semaphore: asyncio.Semaphore, url: str, target: CrawlTarget) -> Optional[CrawlResult]:
        """Crawl a single URL"""        async with semaphore:
            try:
                # Check cache first
                if self.config.enable_caching:
                    cache_key = f"{target.platform.value}:{hashlib.md5(url.encode()).hexdigest()}"
                    if cache_key in self.crawl_cache:
                        cached_result = self.crawl_cache[cache_key]
                        logger.debug(f"Using cached result for {url}")
                        return cached_result
                
                # Respect robots.txt if enabled
                if self.config.respect_robots_txt:
                    if not await self._check_robots_txt(url):
                        logger.warning(f"URL blocked by robots.txt: {url}")
                        return None
                
                start_time = time.time()
                
                # Choose crawling method based on URL and configuration
                if self._requires_javascript(url) and self.selenium_crawler:
                    result_data = await self.selenium_crawler.crawl_url(url)
                else:
                    result_data = await self._crawl_with_session(url)
                
                if not result_data:
                    return None
                
                # Create crawl result
                crawl_result = CrawlResult(
                    target_id=target.target_id,
                    platform=target.platform,
                    url=url,
                    title=result_data.get('title', ''),
                    description=result_data.get('description', ''),
                    content_text=result_data.get('content_text', ''),
                    media_urls=result_data.get('media_urls', []),
                    metadata=result_data,
                    response_time_ms=result_data.get('response_time_ms', (time.time() - start_time) * 1000),
                    status_code=result_data.get('status_code', 200)
                )
                
                # Calculate content hash
                content = f"{crawl_result.title} {crawl_result.description} {crawl_result.content_text}"
                crawl_result.content_hash = hashlib.sha256(content.encode()).hexdigest()
                
                # Analyze content similarity
                if target.keywords:
                    reference_text = ' '.join(target.keywords)
                    similarity = self.content_analyzer.analyze_text_similarity(
                        content, reference_text
                    )
                    crawl_result.similarity_score = similarity
                    
                    if similarity > self.config.similarity_threshold:
                        crawl_result.match_type = ContentMatchType.SIMILAR_MATCH
                    elif similarity > 0.5:
                        crawl_result.match_type = ContentMatchType.PARTIAL_MATCH
                    else:
                        crawl_result.match_type = ContentMatchType.METADATA_MATCH
                
                return crawl_result
                
            except Exception as e:
                logger.error(f"Error crawling single URL {url}: {str(e)}")
                return CrawlResult(
                    target_id=target.target_id,
                    platform=target.platform,
                    url=url,
                    error_message=str(e),
                    status_code=500
                )
    
    async def _crawl_with_session(self, url: str) -> Optional[Dict[str, Any]]:
        """Crawl URL using aiohttp session"""        try:
            headers = {}
            
            # Rotate user agent if enabled
            if self.config.user_agent_rotation:
                headers['User-Agent'] = self.user_agent_rotator.get_user_agent()
            
            # Add custom headers
            headers.update(self.config.custom_headers)
            
            # Use proxy if available
            proxy = None
            if self.proxy_manager:
                proxy = self.proxy_manager.get_next_proxy()
            
            start_time = time.time()
            
            async with self.session.get(url, headers=headers, proxy=proxy) as response:
                response_time = (time.time() - start_time) * 1000
                
                if response.status == 200:
                    html_content = await response.text()
                    soup = BeautifulSoup(html_content, 'html.parser')
                    
                    # Extract basic information
                    title = soup.title.string if soup.title else ""
                    
                    # Extract meta description
                    meta_desc = soup.find('meta', attrs={'name': 'description'})
                    description = meta_desc['content'] if meta_desc and meta_desc.get('content') else ""
                    
                    # Extract text content
                    text_content = soup.get_text(strip=True)
                    
                    # Extract media URLs
                    media_urls = []
                    for img in soup.find_all('img', src=True):
                        img_url = urljoin(url, img['src'])
                        media_urls.append(img_url)
                    
                    return {
                        'title': title.strip(),
                        'description': description.strip(),
                        'content_text': text_content[:5000],  # Limit text length
                        'media_urls': media_urls[:20],  # Limit media URLs
                        'response_time_ms': response_time,
                        'status_code': response.status,
                        'method': 'aiohttp'
                    }
                else:
                    logger.warning(f"HTTP {response.status} for URL: {url}")
                    return {
                        'status_code': response.status,
                        'error': f'HTTP {response.status}',
                        'response_time_ms': response_time
                    }
                    
        except asyncio.TimeoutError:
            logger.error(f"Timeout crawling URL: {url}")
            return {'status_code': 408, 'error': 'timeout'}
        except Exception as e:
            logger.error(f"Error crawling URL {url}: {str(e)}")
            return {'status_code': 500, 'error': str(e)}
    
    def _requires_javascript(self, url: str) -> bool:
        """Check if URL likely requires JavaScript rendering"""        js_heavy_domains = [
            'instagram.com', 'facebook.com', 'twitter.com', 'tiktok.com',
            'linkedin.com', 'medium.com', 'pinterest.com'
        ]
        
        domain = urlparse(url).netloc.lower()
        return any(js_domain in domain for js_domain in js_heavy_domains)
    
    async def _check_robots_txt(self, url: str) -> bool:
        """Check if URL is allowed by robots.txt"""        try:
            parsed_url = urlparse(url)
            robots_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"
            
            rp = RobotFileParser()
            rp.set_url(robots_url)
            rp.read()
            
            user_agent = '*'
            return rp.can_fetch(user_agent, url)
            
        except Exception as e:
            logger.warning(f"Error checking robots.txt for {url}: {str(e)}")
            return True  # Allow by default if robots.txt check fails
    
    async def get_crawl_statistics(self) -> Dict[str, Any]:
        """Get comprehensive crawl statistics"""        try:
            return {
                'total_crawls': self.crawl_stats['total_crawls'],
                'successful_crawls': self.crawl_stats['successful_crawls'],
                'failed_crawls': self.crawl_stats['failed_crawls'],
                'success_rate': (self.crawl_stats['successful_crawls'] / self.crawl_stats['total_crawls'] * 100) if self.crawl_stats['total_crawls'] > 0 else 0,
                'total_results': self.crawl_stats['total_results'],
                'active_crawls': len(self.active_crawls),
                'cached_results': len(self.crawl_cache),
                'platforms_configured': len(self.platform_crawlers),
                'status': self.status.value,
                'proxy_enabled': self.proxy_manager is not None,
                'javascript_support': self.selenium_crawler is not None,
                'last_updated': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting crawl statistics: {str(e)}")
            return {}
    
    async def cleanup(self):
        """Cleanup crawler resources"""        try:
            self.status = CrawlerManagerStatus.INACTIVE
            
            # Close HTTP session
            if self.session:
                await self.session.close()
            
            # Cleanup Selenium
            if self.selenium_crawler:
                self.selenium_crawler.cleanup()
            
            # Clear active crawls
            self.active_crawls.clear()
            
            logger.info("Crawler manager cleaned up successfully")
            
        except Exception as e:
            logger.error(f"Error during crawler cleanup: {str(e)}")


# Export all main classes
__all__ = [
    'CrawlerManagerStatus',
    'PlatformType',
    'CrawlerMethod',
    'ContentMatchType',
    'CrawlPriority',
    'ProxyType',
    'CrawlerManagerConfig',
    'CrawlTarget',
    'CrawlResult',
    'UserAgentRotator',
    'ProxyManager',
    'ContentAnalyzer',
    'SeleniumCrawler',
    'PlatformSpecificCrawler',
    'CrawlerManager'
]
            self.logger.error(f"Platform monitoring failed for {platform}: {e}")
            
        return results
    
    def _get_next_proxy(self) -> Optional[str]:
        """Get next proxy from rotation"""        if not self.config.proxy_enabled or not self.config.proxy_list:
            return None
        
        proxy = self.config.proxy_list[self.proxy_index]
        self.proxy_index = (self.proxy_index + 1) % len(self.config.proxy_list)
        return proxy


# =============== FACTORY & UTILITIES ===============

class CrawlerManagerFactory:
    """Factory for creating crawler manager instances"""    
    @staticmethod
    def create_service(config: Optional[CrawlerManagerConfig] = None) -> CrawlerManagerService:
        """Create configured crawler manager service"""        if config is None:
            config = CrawlerManagerConfig()
        
        return CrawlerManagerService(config)
    
    @staticmethod
    def create_config(
        max_concurrent_crawlers: int = 20,
        crawl_interval_seconds: int = 300,
        **kwargs
    ) -> CrawlerManagerConfig:
        """Create crawler manager configuration"""        return CrawlerManagerConfig(
            max_concurrent_crawlers=max_concurrent_crawlers,
            crawl_interval_seconds=crawl_interval_seconds,
            **kwargs
        )


def extract_domain(url: str) -> str:
    """Extract domain from URL"""    try:
        parsed = urlparse(url)
        return parsed.netloc
    except:
        return ""


def is_valid_url(url: str) -> bool:
    """Check if URL is valid"""    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False


# Export public classes
__all__ = [
    'CrawlerManagerService',
    'ICrawlerManagerService',
    'CrawlerManagerStatus', 
    'CrawlerManagerConfig',
    'CrawlerResult',
    'PlatformCrawler',
    'PlatformType',
    'CrawlerMethod',
    'ContentMatchType',
    'CrawlerManagerFactory',
    'extract_domain',
    'is_valid_url'
]
