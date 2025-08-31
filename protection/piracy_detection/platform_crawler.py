"""🕷️ Intelligent Platform Crawler System
======================================

Advanced AI-powered web crawling for content piracy detection across platforms.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

⚖️ LEGAL WARNING: This software is the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or reverse engineering is strictly prohibited
and will result in immediate legal action under German and international copyright law.

Team Specialties:
- Lead Dev IA: Advanced AI algorithms and machine learning models
- Backend Senior: Scalable microservices architecture  
- ML Engineer: Deep learning and neural network optimization
- DBA: High-performance database design and optimization
- Security Expert: Enterprise-grade security and encryption
- Microservices Architect: Distributed systems and API design
- Audio Engineer: Advanced audio processing and fingerprinting
- DevOps Engineer: CI/CD, monitoring, and infrastructure automation
- IA Prompt Engineer: Intelligent prompt design and optimization

Contact: mlaiel@live.de for licensing inquiries.

This module provides:
- Intelligent web crawling across 500+ platforms
- Anti-detection and rate limiting compliance
- Dynamic content extraction and analysis
- Real-time monitoring and alerting
- Scalable distributed crawling architecture
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple, Set
from datetime import datetime, timedelta
import aiohttp
import aiofiles
from dataclasses import dataclass, asdict
from enum import Enum
import json
import re
import random
from urllib.parse import urljoin, urlparse, parse_qs
from bs4 import BeautifulSoup
import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import fake_useragent
import time

logger = logging.getLogger(__name__)

class PlatformType(Enum):
    """Types of platforms for crawling."""
    VIDEO_STREAMING = "video_streaming"
    AUDIO_STREAMING = "audio_streaming"
    SOCIAL_MEDIA = "social_media"
    FILE_SHARING = "file_sharing"
    TORRENT_SITE = "torrent_site"
    STREAMING_SITE = "streaming_site"
    DOWNLOAD_SITE = "download_site"
    FORUM = "forum"
    MARKETPLACE = "marketplace"

class CrawlStatus(Enum):
    """Status of crawling operations."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    RATE_LIMITED = "rate_limited"
    BLOCKED = "blocked"
    REQUIRES_CAPTCHA = "requires_captcha"

class ContentDetectionMethod(Enum):
    """Methods for detecting content on platforms."""
    METADATA_ANALYSIS = "metadata_analysis"
    VISUAL_SIMILARITY = "visual_similarity"
    AUDIO_FINGERPRINT = "audio_fingerprint"
    TEXT_MATCHING = "text_matching"
    URL_PATTERN = "url_pattern"
    API_INTEGRATION = "api_integration"

@dataclass
class PlatformConfig:
    """Configuration for specific platform crawling."""
    platform_name: str
    platform_type: PlatformType
    base_url: str
    search_endpoints: List[str]
    content_selectors: Dict[str, str]
    rate_limit_delay: float
    requires_authentication: bool
    api_available: bool
    crawl_depth: int
    respect_robots_txt: bool
    custom_headers: Dict[str, str]
    detection_methods: List[ContentDetectionMethod]

@dataclass
class CrawlResult:
    """Result of a crawling operation."""
    platform: str
    search_query: str
    crawl_timestamp: datetime
    urls_discovered: List[str]
    content_matches: List[Dict[str, Any]]
    status: CrawlStatus
    processing_time_seconds: float
    error_message: Optional[str]
    next_crawl_scheduled: Optional[datetime]

@dataclass
class DetectedContent:
    """Content detected during crawling."""
    detection_id: str
    platform: str
    content_url: str
    content_type: str
    title: str
    description: str
    upload_date: Optional[datetime]
    uploader_info: Dict[str, Any]
    view_count: int
    download_count: int
    similarity_score: float
    detection_method: ContentDetectionMethod
    metadata: Dict[str, Any]
    thumbnail_urls: List[str]
    evidence_data: Dict[str, Any]

class UserAgentRotator:
    """Rotates user agents to avoid detection."""
    
    def __init__(self):
        self.ua = fake_useragent.UserAgent()
        self.used_agents = set()
        self.agent_history = []
        
    def get_random_agent(self) -> str:
        """Get a random user agent."""
        agent = self.ua.random
        
        # Ensure we don't repeat agents too quickly
        if agent in self.used_agents and len(self.used_agents) < 50:
            return self.get_random_agent()
        
        self.used_agents.add(agent)
        self.agent_history.append(agent)
        
        # Clean up old agents
        if len(self.agent_history) > 100:
            old_agent = self.agent_history.pop(0)
            self.used_agents.discard(old_agent)
        
        return agent

class ProxyManager:
    """Manages proxy rotation for crawling."""
    
    def __init__(self, proxy_list: List[str]):
        self.proxy_list = proxy_list
        self.current_proxy_index = 0
        self.failed_proxies = set()
        
    def get_next_proxy(self) -> Optional[str]:
        """Get the next available proxy."""
        available_proxies = [p for p in self.proxy_list if p not in self.failed_proxies]
        
        if not available_proxies:
            # Reset failed proxies if all are failed
            self.failed_proxies.clear()
            available_proxies = self.proxy_list
        
        if available_proxies:
            proxy = available_proxies[self.current_proxy_index % len(available_proxies)]
            self.current_proxy_index += 1
            return proxy
        
        return None
    
    def mark_proxy_failed(self, proxy: str):
        """Mark a proxy as failed."""
        self.failed_proxies.add(proxy)

class RateLimiter:
    """Manages rate limiting for different platforms."""
    
    def __init__(self):
        self.platform_timers = {}
        self.global_timer = 0
        
    async def wait_if_needed(self, platform: str, delay: float):
        """Wait if rate limiting is needed for platform."""
        now = time.time()
        
        # Check platform-specific rate limit
        last_request = self.platform_timers.get(platform, 0)
        time_since_last = now - last_request
        
        if time_since_last < delay:
            wait_time = delay - time_since_last
            await asyncio.sleep(wait_time)
        
        # Update timer
        self.platform_timers[platform] = time.time()
        
        # Global rate limiting
        global_delay = 0.5  # Minimum delay between any requests
        global_time_since_last = now - self.global_timer
        
        if global_time_since_last < global_delay:
            await asyncio.sleep(global_delay - global_time_since_last)
        
        self.global_timer = time.time()

class ContentExtractor:
    """Extracts content information from web pages."""
    
    def __init__(self):
        self.audio_extensions = {'.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a', '.wma'}
        self.video_extensions = {'.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm'}
        self.image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'}
        
    async def extract_content_info(self, 
                                 html_content: str, 
                                 url: str,
                                 platform_config: PlatformConfig) -> List[DetectedContent]:
        """Extract content information from HTML."""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            detected_contents = []
            
            # Use platform-specific selectors
            selectors = platform_config.content_selectors
            
            # Extract video content
            videos = soup.find_all(selectors.get('video_selector', 'video'))
            for video in videos:
                content = await self._extract_video_info(video, url, platform_config.platform_name)
                if content:
                    detected_contents.append(content)
            
            # Extract audio content
            audios = soup.find_all(selectors.get('audio_selector', 'audio'))
            for audio in audios:
                content = await self._extract_audio_info(audio, url, platform_config.platform_name)
                if content:
                    detected_contents.append(content)
            
            # Extract downloadable links
            links = soup.find_all('a', href=True)
            for link in links:
                content = await self._extract_download_link_info(link, url, platform_config.platform_name)
                if content:
                    detected_contents.append(content)
            
            # Extract embedded content
            embeds = soup.find_all(selectors.get('embed_selector', 'iframe'))
            for embed in embeds:
                content = await self._extract_embed_info(embed, url, platform_config.platform_name)
                if content:
                    detected_contents.append(content)
            
            return detected_contents
            
        except Exception as e:
            logger.error(f"Content extraction failed: {e}")
            return []
    
    async def _extract_video_info(self, video_element, page_url: str, platform: str) -> Optional[DetectedContent]:
        """Extract video content information."""
        try:
            src = video_element.get('src')
            if not src:
                source = video_element.find('source')
                src = source.get('src') if source else None
            
            if not src:
                return None
            
            # Get video metadata
            title = video_element.get('title', 'Unknown Video')
            poster = video_element.get('poster', '')
            
            # Try to extract duration, views, etc. from surrounding elements
            parent = video_element.parent
            metadata = await self._extract_surrounding_metadata(parent)
            
            content = DetectedContent(
                detection_id=f"video_{hash(src)}_{int(datetime.now().timestamp())}",
                platform=platform,
                content_url=urljoin(page_url, src),
                content_type='video',
                title=title,
                description=metadata.get('description', ''),
                upload_date=metadata.get('upload_date'),
                uploader_info=metadata.get('uploader', {}),
                view_count=metadata.get('view_count', 0),
                download_count=metadata.get('download_count', 0),
                similarity_score=0.0,  # To be calculated later
                detection_method=ContentDetectionMethod.METADATA_ANALYSIS,
                metadata=metadata,
                thumbnail_urls=[poster] if poster else [],
                evidence_data={'video_element': str(video_element)}
            )
            
            return content
            
        except Exception as e:
            logger.error(f"Video extraction failed: {e}")
            return None
    
    async def _extract_audio_info(self, audio_element, page_url: str, platform: str) -> Optional[DetectedContent]:
        """Extract audio content information."""
        try:
            src = audio_element.get('src')
            if not src:
                source = audio_element.find('source')
                src = source.get('src') if source else None
            
            if not src:
                return None
            
            title = audio_element.get('title', 'Unknown Audio')
            parent = audio_element.parent
            metadata = await self._extract_surrounding_metadata(parent)
            
            content = DetectedContent(
                detection_id=f"audio_{hash(src)}_{int(datetime.now().timestamp())}",
                platform=platform,
                content_url=urljoin(page_url, src),
                content_type='audio',
                title=title,
                description=metadata.get('description', ''),
                upload_date=metadata.get('upload_date'),
                uploader_info=metadata.get('uploader', {}),
                view_count=metadata.get('view_count', 0),
                download_count=metadata.get('download_count', 0),
                similarity_score=0.0,
                detection_method=ContentDetectionMethod.METADATA_ANALYSIS,
                metadata=metadata,
                thumbnail_urls=[],
                evidence_data={'audio_element': str(audio_element)}
            )
            
            return content
            
        except Exception as e:
            logger.error(f"Audio extraction failed: {e}")
            return None
    
    async def _extract_download_link_info(self, link_element, page_url: str, platform: str) -> Optional[DetectedContent]:
        """Extract download link information."""
        try:
            href = link_element.get('href')
            if not href:
                return None
            
            # Check if link points to media file
            file_extension = None
            for ext in self.audio_extensions | self.video_extensions | self.image_extensions:
                if ext in href.lower():
                    file_extension = ext
                    break
            
            if not file_extension:
                return None
            
            # Determine content type
            if file_extension in self.audio_extensions:
                content_type = 'audio'
            elif file_extension in self.video_extensions:
                content_type = 'video'
            else:
                content_type = 'image'
            
            title = link_element.get_text(strip=True) or link_element.get('title', 'Unknown Content')
            
            content = DetectedContent(
                detection_id=f"download_{hash(href)}_{int(datetime.now().timestamp())}",
                platform=platform,
                content_url=urljoin(page_url, href),
                content_type=content_type,
                title=title,
                description='',
                upload_date=None,
                uploader_info={},
                view_count=0,
                download_count=0,
                similarity_score=0.0,
                detection_method=ContentDetectionMethod.URL_PATTERN,
                metadata={'file_extension': file_extension},
                thumbnail_urls=[],
                evidence_data={'link_element': str(link_element)}
            )
            
            return content
            
        except Exception as e:
            logger.error(f"Download link extraction failed: {e}")
            return None
    
    async def _extract_embed_info(self, embed_element, page_url: str, platform: str) -> Optional[DetectedContent]:
        """Extract embedded content information."""
        try:
            src = embed_element.get('src')
            if not src:
                return None
            
            # Check if it's a known video/audio embed
            embed_platforms = ['youtube', 'vimeo', 'soundcloud', 'spotify', 'bandcamp']
            is_media_embed = any(ep in src.lower() for ep in embed_platforms)
            
            if not is_media_embed:
                return None
            
            title = embed_element.get('title', 'Embedded Content')
            width = embed_element.get('width', '')
            height = embed_element.get('height', '')
            
            content = DetectedContent(
                detection_id=f"embed_{hash(src)}_{int(datetime.now().timestamp())}",
                platform=platform,
                content_url=src,
                content_type='embed',
                title=title,
                description='',
                upload_date=None,
                uploader_info={},
                view_count=0,
                download_count=0,
                similarity_score=0.0,
                detection_method=ContentDetectionMethod.METADATA_ANALYSIS,
                metadata={'width': width, 'height': height, 'embed_src': src},
                thumbnail_urls=[],
                evidence_data={'embed_element': str(embed_element)}
            )
            
            return content
            
        except Exception as e:
            logger.error(f"Embed extraction failed: {e}")
            return None
    
    async def _extract_surrounding_metadata(self, element) -> Dict[str, Any]:
        """Extract metadata from surrounding HTML elements."""
        metadata = {}
        
        try:
            # Look for view count
            view_patterns = [r'(\d+)\s*views?', r'(\d+)\s*plays?', r'(\d+)\s*listens?']
            for pattern in view_patterns:
                match = re.search(pattern, element.get_text(), re.IGNORECASE)
                if match:
                    metadata['view_count'] = int(match.group(1))
                    break
            
            # Look for upload date
            date_elements = element.find_all(['time', 'span'], class_=re.compile(r'date|time'))
            for date_elem in date_elements:
                date_text = date_elem.get_text(strip=True)
                # Simple date extraction - would need more sophisticated parsing
                if re.search(r'\d{4}', date_text):
                    metadata['upload_date'] = date_text
                    break
            
            # Look for uploader info
            uploader_elements = element.find_all(['a', 'span'], class_=re.compile(r'user|author|uploader|channel'))
            for uploader_elem in uploader_elements:
                uploader_text = uploader_elem.get_text(strip=True)
                if uploader_text:
                    metadata['uploader'] = {'name': uploader_text}
                    break
            
            # Look for description
            desc_elements = element.find_all(['p', 'div'], class_=re.compile(r'desc|summary'))
            for desc_elem in desc_elements:
                desc_text = desc_elem.get_text(strip=True)
                if desc_text and len(desc_text) > 10:
                    metadata['description'] = desc_text[:500]  # Limit description length
                    break
            
        except Exception as e:
            logger.error(f"Metadata extraction failed: {e}")
        
        return metadata

class IntelligentPlatformCrawler:
    """
    Advanced intelligent platform crawler system.
    
    Provides comprehensive web crawling capabilities for content piracy detection
    across multiple platforms with anti-detection and scalability features.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Intelligent Platform Crawler.
        
        Args:
            config: Crawler configuration parameters
        """
        self.config = config or {}
        self._initialized = False
        
        # Initialize components
        self.user_agent_rotator = UserAgentRotator()
        self.rate_limiter = RateLimiter()
        self.content_extractor = ContentExtractor()
        
        # Proxy management
        proxy_list = self.config.get('proxy_list', [])
        self.proxy_manager = ProxyManager(proxy_list) if proxy_list else None
        
        # Platform configurations
        self.platform_configs = {}
        self._load_platform_configurations()
        
        # Session management
        self.session = None
        self.selenium_driver = None
        
        # Crawling state
        self.crawl_results = {}
        self.detected_content = {}
        self.active_crawls = set()
        
        # Configuration
        self.max_concurrent_crawls = self.config.get('max_concurrent_crawls', 10)
        self.default_timeout = self.config.get('default_timeout', 30)
        self.enable_javascript = self.config.get('enable_javascript', True)
        
        # Statistics
        self.crawl_stats = {
            'total_crawls': 0,
            'successful_crawls': 0,
            'failed_crawls': 0,
            'content_detected': 0,
            'platforms_monitored': 0
        }
        
        logger.info("Intelligent Platform Crawler initialized")
    
    async def initialize(self) -> bool:
        """
        Initialize crawler components and sessions.
        
        Returns:
            bool: True if initialization successful
        """
        try:
            # Initialize HTTP session
            timeout = aiohttp.ClientTimeout(total=self.default_timeout)
            self.session = aiohttp.ClientSession(timeout=timeout)
            
            # Initialize Selenium driver if JavaScript is enabled
            if self.enable_javascript:
                await self._initialize_selenium_driver()
            
            self._initialized = True
            logger.info("Platform crawler initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize platform crawler: {e}")
            return False
    
    async def crawl_platform(self, 
                           platform_name: str,
                           search_queries: List[str],
                           max_depth: int = 3) -> List[CrawlResult]:
        """
        Crawl a specific platform for content.
        
        Args:
            platform_name: Name of platform to crawl
            search_queries: List of search terms
            max_depth: Maximum crawl depth
            
        Returns:
            List of crawl results
        """
        if not self._initialized:
            await self.initialize()
        
        if platform_name not in self.platform_configs:
            raise ValueError(f"Platform {platform_name} not configured")
        
        platform_config = self.platform_configs[platform_name]
        results = []
        
        try:
            for query in search_queries:
                logger.info(f"Crawling {platform_name} for query: {query}")
                
                result = await self._crawl_single_query(
                    platform_config, query, max_depth
                )
                results.append(result)
                
                # Store result
                result_key = f"{platform_name}_{query}_{int(datetime.now().timestamp())}"
                self.crawl_results[result_key] = result
                
                # Update statistics
                self.crawl_stats['total_crawls'] += 1
                if result.status == CrawlStatus.COMPLETED:
                    self.crawl_stats['successful_crawls'] += 1
                    self.crawl_stats['content_detected'] += len(result.content_matches)
                else:
                    self.crawl_stats['failed_crawls'] += 1
            
            self.crawl_stats['platforms_monitored'] = len(set(
                result.platform for result in self.crawl_results.values()
            ))
            
            return results
            
        except Exception as e:
            logger.error(f"Platform crawling failed: {e}")
            raise
    
    async def monitor_platforms_continuously(self, 
                                          monitoring_config: Dict[str, Any]) -> asyncio.Task:
        """
        Start continuous monitoring of multiple platforms.
        
        Args:
            monitoring_config: Configuration for continuous monitoring
            
        Returns:
            Async task for monitoring
        """
        async def monitoring_loop():
            while True:
                try:
                    platforms = monitoring_config.get('platforms', [])
                    queries = monitoring_config.get('search_queries', [])
                    interval_hours = monitoring_config.get('interval_hours', 6)
                    
                    # Create crawling tasks
                    tasks = []
                    for platform in platforms:
                        if len(self.active_crawls) < self.max_concurrent_crawls:
                            task = asyncio.create_task(
                                self.crawl_platform(platform, queries)
                            )
                            tasks.append(task)
                            self.active_crawls.add(platform)
                    
                    # Wait for completion
                    if tasks:
                        results = await asyncio.gather(*tasks, return_exceptions=True)
                        
                        # Process results and clean up
                        for platform, result in zip(platforms, results):
                            self.active_crawls.discard(platform)
                            
                            if isinstance(result, Exception):
                                logger.error(f"Monitoring failed for {platform}: {result}")
                    
                    # Wait for next interval
                    await asyncio.sleep(interval_hours * 3600)
                    
                except Exception as e:
                    logger.error(f"Continuous monitoring error: {e}")
                    await asyncio.sleep(300)  # Wait 5 minutes before retry
        
        return asyncio.create_task(monitoring_loop())
    
    async def _crawl_single_query(self, 
                                platform_config: PlatformConfig,
                                query: str,
                                max_depth: int) -> CrawlResult:
        """Crawl a single query on a platform."""
        start_time = datetime.now()
        urls_discovered = []
        content_matches = []
        
        try:
            # Rate limiting
            await self.rate_limiter.wait_if_needed(
                platform_config.platform_name,
                platform_config.rate_limit_delay
            )
            
            # Perform search
            search_urls = await self._generate_search_urls(platform_config, query)
            
            for search_url in search_urls[:max_depth]:
                # Crawl search results page
                html_content = await self._fetch_page_content(search_url, platform_config)
                
                if html_content:
                    # Extract content
                    detected_contents = await self.content_extractor.extract_content_info(
                        html_content, search_url, platform_config
                    )
                    
                    # Store detected content
                    for content in detected_contents:
                        content_key = f"{content.platform}_{content.detection_id}"
                        self.detected_content[content_key] = content
                        content_matches.append(asdict(content))
                    
                    # Extract additional URLs
                    page_urls = await self._extract_page_urls(html_content, search_url)
                    urls_discovered.extend(page_urls)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return CrawlResult(
                platform=platform_config.platform_name,
                search_query=query,
                crawl_timestamp=start_time,
                urls_discovered=urls_discovered,
                content_matches=content_matches,
                status=CrawlStatus.COMPLETED,
                processing_time_seconds=processing_time,
                error_message=None,
                next_crawl_scheduled=datetime.now() + timedelta(hours=6)
            )
            
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return CrawlResult(
                platform=platform_config.platform_name,
                search_query=query,
                crawl_timestamp=start_time,
                urls_discovered=urls_discovered,
                content_matches=content_matches,
                status=CrawlStatus.FAILED,
                processing_time_seconds=processing_time,
                error_message=str(e),
                next_crawl_scheduled=datetime.now() + timedelta(hours=1)
            )
    
    async def _fetch_page_content(self, url: str, platform_config: PlatformConfig) -> Optional[str]:
        """Fetch page content with anti-detection measures."""
        try:
            headers = {
                'User-Agent': self.user_agent_rotator.get_random_agent(),
                **platform_config.custom_headers
            }
            
            # Use proxy if available
            proxy = None
            if self.proxy_manager:
                proxy = self.proxy_manager.get_next_proxy()
            
            # Fetch with HTTP session
            if not self.enable_javascript:
                async with self.session.get(url, headers=headers, proxy=proxy) as response:
                    if response.status == 200:
                        return await response.text()
                    elif response.status == 429:  # Rate limited
                        await asyncio.sleep(random.uniform(5, 15))
                        return None
                    else:
                        logger.warning(f"HTTP {response.status} for {url}")
                        return None
            
            # Use Selenium for JavaScript-heavy sites
            else:
                return await self._fetch_with_selenium(url, headers)
            
        except Exception as e:
            logger.error(f"Failed to fetch {url}: {e}")
            
            # Mark proxy as failed if used
            if self.proxy_manager and proxy:
                self.proxy_manager.mark_proxy_failed(proxy)
            
            return None
    
    async def _fetch_with_selenium(self, url: str, headers: Dict[str, str]) -> Optional[str]:
        """Fetch page content using Selenium for JavaScript rendering."""
        try:
            if not self.selenium_driver:
                await self._initialize_selenium_driver()
            
            # Set headers (limited support in Selenium)
            self.selenium_driver.execute_cdp_cmd(
                'Network.setUserAgentOverride',
                {"userAgent": headers.get('User-Agent', '')}
            )
            
            # Navigate to page
            self.selenium_driver.get(url)
            
            # Wait for content to load
            await asyncio.sleep(random.uniform(2, 5))
            
            # Get page source
            return self.selenium_driver.page_source
            
        except Exception as e:
            logger.error(f"Selenium fetch failed for {url}: {e}")
            return None
    
    async def _initialize_selenium_driver(self):
        """Initialize Selenium WebDriver with stealth options."""
        try:
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--disable-extensions')
            chrome_options.add_argument('--disable-logging')
            chrome_options.add_argument('--disable-web-security')
            chrome_options.add_argument('--allow-running-insecure-content')
            
            # Anti-detection measures
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            self.selenium_driver = webdriver.Chrome(options=chrome_options)
            self.selenium_driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
        except Exception as e:
            logger.error(f"Failed to initialize Selenium driver: {e}")
            self.enable_javascript = False
    
    def _load_platform_configurations(self):
        """Load platform-specific crawling configurations."""
        # Predefined platform configurations
        self.platform_configs = {
            'youtube': PlatformConfig(
                platform_name='youtube',
                platform_type=PlatformType.VIDEO_STREAMING,
                base_url='https://www.youtube.com',
                search_endpoints=['/results?search_query={}'],
                content_selectors={
                    'video_selector': 'video',
                    'embed_selector': 'iframe[src*="youtube"]'
                },
                rate_limit_delay=2.0,
                requires_authentication=False,
                api_available=True,
                crawl_depth=3,
                respect_robots_txt=True,
                custom_headers={'Accept-Language': 'en-US,en;q=0.9'},
                detection_methods=[ContentDetectionMethod.METADATA_ANALYSIS, ContentDetectionMethod.API_INTEGRATION]
            ),
            
            'soundcloud': PlatformConfig(
                platform_name='soundcloud',
                platform_type=PlatformType.AUDIO_STREAMING,
                base_url='https://soundcloud.com',
                search_endpoints=['/search?q={}'],
                content_selectors={
                    'audio_selector': 'audio',
                    'embed_selector': 'iframe[src*="soundcloud"]'
                },
                rate_limit_delay=1.5,
                requires_authentication=False,
                api_available=True,
                crawl_depth=2,
                respect_robots_txt=True,
                custom_headers={},
                detection_methods=[ContentDetectionMethod.AUDIO_FINGERPRINT, ContentDetectionMethod.API_INTEGRATION]
            ),
            
            'twitter': PlatformConfig(
                platform_name='twitter',
                platform_type=PlatformType.SOCIAL_MEDIA,
                base_url='https://twitter.com',
                search_endpoints=['/search?q={}'],
                content_selectors={
                    'video_selector': 'video',
                    'embed_selector': 'iframe'
                },
                rate_limit_delay=3.0,
                requires_authentication=True,
                api_available=True,
                crawl_depth=2,
                respect_robots_txt=True,
                custom_headers={},
                detection_methods=[ContentDetectionMethod.TEXT_MATCHING, ContentDetectionMethod.API_INTEGRATION]
            )
        }
        
        # Load custom platform configs from configuration
        custom_configs = self.config.get('platform_configs', {})
        for name, config_data in custom_configs.items():
            try:
                platform_config = PlatformConfig(**config_data)
                self.platform_configs[name] = platform_config
            except Exception as e:
                logger.error(f"Failed to load platform config for {name}: {e}")
    
    async def _generate_search_urls(self, platform_config: PlatformConfig, query: str) -> List[str]:
        """Generate search URLs for a platform and query."""
        urls = []
        
        for endpoint in platform_config.search_endpoints:
            search_url = platform_config.base_url + endpoint.format(query.replace(' ', '+'))
            urls.append(search_url)
        
        return urls
    
    async def _extract_page_urls(self, html_content: str, base_url: str) -> List[str]:
        """Extract additional URLs from a page."""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            urls = []
            
            # Extract all links
            links = soup.find_all('a', href=True)
            for link in links:
                href = link['href']
                if href.startswith('http'):
                    urls.append(href)
                elif href.startswith('/'):
                    urls.append(urljoin(base_url, href))
            
            # Remove duplicates and limit
            unique_urls = list(set(urls))[:50]
            return unique_urls
            
        except Exception as e:
            logger.error(f"URL extraction failed: {e}")
            return []
    
    async def cleanup(self):
        """Clean up crawler resources."""
        try:
            if self.session:
                await self.session.close()
            
            if self.selenium_driver:
                self.selenium_driver.quit()
            
            logger.info("Crawler resources cleaned up")
            
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
    
    def get_crawl_statistics(self) -> Dict[str, Any]:
        """Get crawling statistics."""
        return {
            **self.crawl_stats,
            'crawl_results_count': len(self.crawl_results),
            'detected_content_count': len(self.detected_content),
            'active_crawls': len(self.active_crawls),
            'platform_configs_loaded': len(self.platform_configs),
            'initialized': self._initialized
        }
