"""Professional web crawling and content discovery system for creator protection.

This module implements advanced crawling capabilities for detecting unauthorized
content usage, monitoring brand mentions, competitor analysis, and automated
content discovery across multiple platforms and social media networks.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 IA-Influencer Project. All rights reserved.
Licensed under proprietary license - reproduction forbidden without written authorization.

Project Team Specialties:
- Lead AI Developer & Senior Backend Engineer: Fahed Mlaiel
- Web Scraping Specialist: Advanced Crawling & Data Extraction
- Data Mining Engineer: Large-Scale Content Analysis
- Security Analyst: Anti-Bot Detection & Ethical Crawling
- Machine Learning Engineer: Content Classification & Similarity Detection
- Network Engineer: Distributed Crawling Infrastructure
- Legal Compliance Officer: DMCA & Content Rights Protection
- DevOps Engineer: Scalable Crawling Infrastructure

Contact: mlaiel@live.de

LEGAL WARNING: This software and all associated intellectual property
belong exclusively to Fahed Mlaiel. Any unauthorized copying, redistribution,
reverse engineering, or commercial use without explicit written permission
will result in immediate legal action under international copyright laws.
"""
from typing import Dict, Any, List, Optional, Union, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from urllib.parse import urljoin, urlparse, parse_qs
from pathlib import Path
import asyncio
import logging
import aiohttp
import hashlib
import uuid
import re
import time
import random
from concurrent.futures import ThreadPoolExecutor

# Web scraping imports
from bs4 import BeautifulSoup, Comment
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

# Content analysis imports
import mimetypes
from PIL import Image
import cv2
import numpy as np

from ..core.exceptions import CrawlerException, ValidationException
from ..core.models import BaseModel


class CrawlerType(Enum):
    """Types of web crawlers."""    SOCIAL_MEDIA = "social_media"
    E_COMMERCE = "e_commerce"
    NEWS_MEDIA = "news_media"
    BLOG_CONTENT = "blog_content"
    VIDEO_PLATFORMS = "video_platforms"
    IMAGE_GALLERIES = "image_galleries"
    MUSIC_PLATFORMS = "music_platforms"
    PIRACY_SITES = "piracy_sites"
    COMPETITOR_ANALYSIS = "competitor_analysis"
    BRAND_MONITORING = "brand_monitoring"


class CrawlingStrategy(Enum):
    """Crawling strategy approaches."""    BREADTH_FIRST = "breadth_first"
    DEPTH_FIRST = "depth_first"
    FOCUSED_CRAWLING = "focused_crawling"
    ADAPTIVE_CRAWLING = "adaptive_crawling"
    DISTRIBUTED_CRAWLING = "distributed_crawling"


class ContentType(Enum):
    """Types of content to extract."""    TEXT = "text"
    IMAGES = "images"
    VIDEOS = "videos"
    AUDIO = "audio"
    DOCUMENTS = "documents"
    SOCIAL_POSTS = "social_posts"
    PRODUCT_LISTINGS = "product_listings"
    USER_PROFILES = "user_profiles"
    COMMENTS = "comments"
    METADATA = "metadata"


class PlatformType(Enum):
    """Supported platforms for crawling."""    INSTAGRAM = "instagram"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    TIKTOK = "tiktok"
    YOUTUBE = "youtube"
    LINKEDIN = "linkedin"
    PINTEREST = "pinterest"
    REDDIT = "reddit"
    DISCORD = "discord"
    TELEGRAM = "telegram"
    TWITCH = "twitch"
    SNAPCHAT = "snapchat"
    GENERIC_WEBSITE = "generic_website"


@dataclass
class CrawlTarget:
    """Crawling target configuration."""    target_id: str
    name: str
    base_urls: List[str]
    platform_type: PlatformType
    content_types: List[ContentType]
    max_depth: int = 3
    max_pages: int = 1000
    crawl_frequency: timedelta = field(default_factory=lambda: timedelta(hours=24))
    respect_robots_txt: bool = True
    rate_limit_delay: float = 1.0
    custom_headers: Dict[str, str] = field(default_factory=dict)
    authentication: Optional[Dict[str, Any]] = None
    filters: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class CrawlResult:
    """Result from crawling operation."""    crawl_id: str
    target_id: str
    url: str
    title: Optional[str] = None
    content: Optional[str] = None
    content_type: ContentType = ContentType.TEXT
    metadata: Dict[str, Any] = field(default_factory=dict)
    media_urls: List[str] = field(default_factory=list)
    links: List[str] = field(default_factory=list)
    similarity_score: float = 0.0
    potential_infringement: bool = False
    crawled_at: datetime = field(default_factory=datetime.utcnow)
    file_size: int = 0
    response_time: float = 0.0


@dataclass
class CrawlSession:
    """Crawling session tracking."""    session_id: str
    target_id: str
    crawler_type: CrawlerType
    strategy: CrawlingStrategy
    start_time: datetime
    end_time: Optional[datetime] = None
    pages_crawled: int = 0
    pages_failed: int = 0
    data_extracted: int = 0
    potential_matches: int = 0
    status: str = "running"
    error_logs: List[str] = field(default_factory=list)


class WebCrawler:
    """    Advanced web crawling engine with anti-detection capabilities.
    
    Provides comprehensive crawling functionality including:
    - Multiple crawling strategies (BFS, DFS, Focused)
    - Anti-bot detection evasion
    - Rate limiting and politeness policies  
    - Content extraction and analysis
    - Similarity detection for copyright protection
    - Distributed crawling support
    """    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = logging.getLogger("crawler.web")
        
        # Crawling settings
        self.user_agents = self.config.get("user_agents", self._get_default_user_agents())
        self.max_concurrent_requests = self.config.get("max_concurrent_requests", 10)
        self.request_timeout = self.config.get("request_timeout", 30)
        self.retry_attempts = self.config.get("retry_attempts", 3)
        self.respect_robots_txt = self.config.get("respect_robots_txt", True)
        
        # Anti-detection settings
        self.use_proxy_rotation = self.config.get("use_proxy_rotation", False)
        self.proxy_list = self.config.get("proxy_list", [])
        self.random_delay_range = self.config.get("random_delay_range", (1, 3))
        self.browser_automation = self.config.get("browser_automation", True)
        
        # Content analysis settings
        self.similarity_threshold = self.config.get("similarity_threshold", 0.85)
        self.content_analysis_enabled = self.config.get("content_analysis_enabled", True)
        
        # Initialize components
        self._initialize_crawler_components()
        
        self.logger.info("WebCrawler initialized successfully")
    
    def _initialize_crawler_components(self):
        """Initialize crawler components and sessions."""


        try:
            # HTTP session with connection pooling
            self.session_connector = aiohttp.TCPConnector(
                limit=self.max_concurrent_requests,
                limit_per_host=5,
                ttl_dns_cache=300,
                use_dns_cache=True
            )
            
            # Active crawl sessions
            self.active_sessions: Dict[str, CrawlSession] = {}
            self.crawl_results: Dict[str, List[CrawlResult]] = {}
            self.crawl_targets: Dict[str, CrawlTarget] = {}
            
            # Rate limiting tracking
            self.domain_last_request: Dict[str, float] = {}
            self.domain_request_counts: Dict[str, int] = {}
            
            # Content similarity tracking
            self.content_hashes: Set[str] = set()
            self.similarity_cache: Dict[str, float] = {}
            
            # Browser automation setup
            if self.browser_automation:
                self._setup_browser_automation()
            
            self.logger.info("Crawler components initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize crawler components: {e}")
            raise CrawlerException(f"Crawler initialization error: {e}")
    
    def _setup_browser_automation(self):
        """Set up browser automation with Selenium."""


        try:
            # Chrome options for headless browsing
            self.chrome_options = Options()
            self.chrome_options.add_argument('--headless')
            self.chrome_options.add_argument('--no-sandbox')
            self.chrome_options.add_argument('--disable-dev-shm-usage')
            self.chrome_options.add_argument('--disable-gpu')
            self.chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            self.chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            self.chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # Anti-detection measures
            self.chrome_options.add_argument(f'--user-agent={random.choice(self.user_agents)}')
            self.chrome_options.add_argument('--disable-extensions')
            self.chrome_options.add_argument('--disable-plugins-discovery')
            
            # Window size randomization
            widths = [1366, 1920, 1440, 1536]
            heights = [768, 1080, 900, 864]
            width = random.choice(widths)
            height = random.choice(heights)
            self.chrome_options.add_argument(f'--window-size={width},{height}')
            
            self.logger.info("Browser automation configured")
            
        except Exception as e:
            self.logger.warning(f"Browser automation setup failed: {e}")
            self.browser_automation = False
    
    def _get_default_user_agents(self) -> List[str]:
        """Get list of realistic user agents for anti-detection."""


        return [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/89.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Safari/14.1.1',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/91.0.864.59',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        ]
    
    async def create_crawl_target(
        self,
        target_config: Dict[str, Any]
    ) -> CrawlTarget:
        """        Create new crawling target configuration.
        
        Sets up comprehensive crawling target with platform-specific
        settings, content filters, and extraction rules.
        """


        try:
            self.logger.info(f"Creating crawl target: {target_config.get('name', 'Unknown')}")
            
            # Generate unique target ID
            target_id = f"target_{uuid.uuid4().hex[:12]}"
            
            # Validate and parse configuration
            platform_type = PlatformType(target_config["platform_type"])
            content_types = [ContentType(ct) for ct in target_config.get("content_types", ["text"])]
            
            # Create crawl target
            crawl_target = CrawlTarget(
                target_id=target_id,
                name=target_config["name"],
                base_urls=target_config["base_urls"],
                platform_type=platform_type,
                content_types=content_types,
                max_depth=target_config.get("max_depth", 3),
                max_pages=target_config.get("max_pages", 1000),
                crawl_frequency=timedelta(
                    seconds=target_config.get("crawl_frequency_seconds", 86400)
                ),
                respect_robots_txt=target_config.get("respect_robots_txt", True),
                rate_limit_delay=target_config.get("rate_limit_delay", 1.0),
                custom_headers=target_config.get("custom_headers", {}),
                authentication=target_config.get("authentication"),
                filters=target_config.get("filters", {})
            )
            
            # Apply platform-specific configurations
            await self._apply_platform_specific_config(crawl_target)
            
            # Store crawl target
            self.crawl_targets[target_id] = crawl_target
            self.crawl_results[target_id] = []
            
            self.logger.info(f"Crawl target created successfully: {target_id}")
            
            return crawl_target
            
        except Exception as e:
            self.logger.error(f"Crawl target creation failed: {e}")
            raise CrawlerException(f"Crawl target creation error: {e}")
    
    async def _apply_platform_specific_config(self, crawl_target: CrawlTarget):
        """Apply platform-specific crawling configurations."""        platform = crawl_target.platform_type
        
        if platform == PlatformType.INSTAGRAM:
            # Instagram-specific settings
            crawl_target.custom_headers.update({
                'X-Instagram-AJAX': '1',
                'X-CSRFToken': 'missing',
                'X-Requested-With': 'XMLHttpRequest'
            })
            crawl_target.rate_limit_delay = max(crawl_target.rate_limit_delay, 2.0)
            
        elif platform == PlatformType.TWITTER:
            # Twitter-specific settings
            crawl_target.custom_headers.update({
                'Authorization': 'Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA',
                'X-Twitter-Active-User': 'yes',
                'X-Twitter-Auth-Type': 'OAuth2Session'
            })
            
        elif platform == PlatformType.YOUTUBE:
            # YouTube-specific settings
            crawl_target.custom_headers.update({
                'X-YouTube-Client-Name': '1',
                'X-YouTube-Client-Version': '2.20210721.00.00'
            })
            
        elif platform == PlatformType.TIKTOK:
            # TikTok-specific settings
            crawl_target.rate_limit_delay = max(crawl_target.rate_limit_delay, 3.0)
            crawl_target.custom_headers.update({
                'Sec-Fetch-Dest': 'empty',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Site': 'same-origin'
            })
        
        # Add more platform-specific configurations as needed
    
    async def start_crawl_session(
        self,
        target_id: str,
        crawler_type: CrawlerType = CrawlerType.SOCIAL_MEDIA,
        strategy: CrawlingStrategy = CrawlingStrategy.BREADTH_FIRST
    ) -> str:
        """        Start new crawling session for target.
        
        Initiates comprehensive crawling session with specified strategy
        and begins content discovery and analysis process.
        """


        try:
            self.logger.info(f"Starting crawl session for target: {target_id}")
            
            # Validate target exists
            if target_id not in self.crawl_targets:
                raise CrawlerException(f"Crawl target not found: {target_id}")
            
            # Generate session ID
            session_id = f"session_{uuid.uuid4().hex[:12]}"
            
            # Create crawl session
            crawl_session = CrawlSession(
                session_id=session_id,
                target_id=target_id,
                crawler_type=crawler_type,
                strategy=strategy,
                start_time=datetime.utcnow()
            )
            
            # Store active session
            self.active_sessions[session_id] = crawl_session
            
            # Start crawling in background
            asyncio.create_task(self._execute_crawl_session(session_id))
            
            self.logger.info(f"Crawl session started: {session_id}")
            
            return session_id
            
        except Exception as e:
            self.logger.error(f"Crawl session start failed: {e}")
            raise CrawlerException(f"Crawl session start error: {e}")
    
    async def _execute_crawl_session(self, session_id: str):
        """Execute crawling session with specified strategy."""        session = self.active_sessions[session_id]
        target = self.crawl_targets[session.target_id]
        
        try:
            self.logger.info(f"Executing crawl session: {session_id}")
            
            # Initialize URL queue based on strategy
            if session.strategy == CrawlingStrategy.BREADTH_FIRST:
                await self._execute_breadth_first_crawl(session, target)
            elif session.strategy == CrawlingStrategy.DEPTH_FIRST:
                await self._execute_depth_first_crawl(session, target)
            elif session.strategy == CrawlingStrategy.FOCUSED_CRAWLING:
                await self._execute_focused_crawl(session, target)
            else:
                await self._execute_adaptive_crawl(session, target)
            
            # Mark session as completed
            session.end_time = datetime.utcnow()
            session.status = "completed"
            
            self.logger.info(
                f"Crawl session completed: {session_id}, "
                f"pages: {session.pages_crawled}, "
                f"matches: {session.potential_matches}"
            )
            
        except Exception as e:
            session.status = "failed"
            session.error_logs.append(str(e))
            self.logger.error(f"Crawl session failed: {session_id}, {e}")
    
    async def _execute_breadth_first_crawl(
        self,
        session: CrawlSession,
        target: CrawlTarget
    ):
        """Execute breadth-first crawling strategy."""        url_queue = asyncio.Queue()
        visited_urls: Set[str] = set()
        
        # Initialize queue with base URLs
        for base_url in target.base_urls:
            await url_queue.put((base_url, 0))  # (url, depth)
        
        # Create HTTP session
        timeout = aiohttp.ClientTimeout(total=self.request_timeout)
        async with aiohttp.ClientSession(
            connector=self.session_connector,
            timeout=timeout
        ) as http_session:
            
            # Process URLs level by level
            while not url_queue.empty() and session.pages_crawled < target.max_pages:
                current_level_urls = []
                
                # Collect all URLs at current depth level
                while not url_queue.empty():
                    try:
                        url, depth = url_queue.get_nowait()
                        if url not in visited_urls and depth <= target.max_depth:
                            current_level_urls.append((url, depth))
                            visited_urls.add(url)
                    except asyncio.QueueEmpty:
                        break
                
                # Process current level URLs concurrently
                semaphore = asyncio.Semaphore(self.max_concurrent_requests)
                tasks = [
                    self._crawl_single_url(
                        http_session, url, depth, target, session, semaphore
                    )
                    for url, depth in current_level_urls
                ]
                
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Add discovered URLs to queue for next level
                for result in results:
                    if isinstance(result, CrawlResult) and result.links:
                        for link in result.links:
                            if link not in visited_urls:
                                await url_queue.put((link, result.metadata.get("depth", 0) + 1))
    
    async def _execute_depth_first_crawl(
        self,
        session: CrawlSession,
        target: CrawlTarget
    ):
        """Execute depth-first crawling strategy."""        async with aiohttp.ClientSession(
            connector=self.session_connector,
            timeout=aiohttp.ClientTimeout(total=self.request_timeout)
        ) as http_session:
            
            visited_urls: Set[str] = set()
            semaphore = asyncio.Semaphore(self.max_concurrent_requests)
            
            # Start DFS from each base URL
            for base_url in target.base_urls:
                if session.pages_crawled >= target.max_pages:
                    break
                
                await self._dfs_crawl_recursive(
                    http_session, base_url, 0, target, session, 
                    visited_urls, semaphore
                )
    
    async def _dfs_crawl_recursive(
        self,
        http_session: aiohttp.ClientSession,
        url: str,
        depth: int,
        target: CrawlTarget,
        session: CrawlSession,
        visited_urls: Set[str],
        semaphore: asyncio.Semaphore
    ):
        """Recursive depth-first crawling."""        if (url in visited_urls or 
            depth > target.max_depth or 
            session.pages_crawled >= target.max_pages):
            return
        
        visited_urls.add(url)
        
        # Crawl current URL
        result = await self._crawl_single_url(
            http_session, url, depth, target, session, semaphore
        )
        
        # Recursively crawl discovered links
        if isinstance(result, CrawlResult) and result.links:
            for link in result.links[:10]:  # Limit links per page for DFS
                await self._dfs_crawl_recursive(
                    http_session, link, depth + 1, target, session,
                    visited_urls, semaphore
                )
    
    async def _execute_focused_crawl(
        self,
        session: CrawlSession,
        target: CrawlTarget
    ):
        """Execute focused crawling strategy based on content relevance."""        url_queue = asyncio.PriorityQueue()
        visited_urls: Set[str] = set()
        
        # Initialize with base URLs (priority 0)
        for base_url in target.base_urls:
            await url_queue.put((0, base_url, 0))  # (priority, url, depth)
        
        async with aiohttp.ClientSession(
            connector=self.session_connector,
            timeout=aiohttp.ClientTimeout(total=self.request_timeout)
        ) as http_session:
            
            semaphore = asyncio.Semaphore(self.max_concurrent_requests)
            
            while not url_queue.empty() and session.pages_crawled < target.max_pages:
                try:
                    priority, url, depth = await asyncio.wait_for(
                        url_queue.get(), timeout=1.0
                    )
                    
                    if url in visited_urls or depth > target.max_depth:
                        continue
                    
                    visited_urls.add(url)
                    
                    # Crawl URL
                    result = await self._crawl_single_url(
                        http_session, url, depth, target, session, semaphore
                    )
                    
                    # Score and prioritize discovered links
                    if isinstance(result, CrawlResult) and result.links:
                        for link in result.links:
                            if link not in visited_urls:
                                # Calculate link priority based on content relevance
                                link_priority = await self._calculate_link_priority(
                                    link, result, target
                                )
                                await url_queue.put((
                                    -link_priority,  # Negative for max-heap behavior
                                    link,
                                    depth + 1
                                ))
                
                except asyncio.TimeoutError:
                    break  # No more URLs to process
    
    async def _execute_adaptive_crawl(
        self,
        session: CrawlSession,
        target: CrawlTarget
    ):
        """Execute adaptive crawling strategy that adjusts based on results."""        # Start with breadth-first approach
        await self._execute_breadth_first_crawl(session, target)
        
        # Analyze results and adapt strategy if needed
        if session.potential_matches > 10:
            # Switch to focused crawling if many matches found
            self.logger.info(f"Switching to focused crawling for session: {session.session_id}")
            await self._execute_focused_crawl(session, target)
    
    async def _crawl_single_url(
        self,
        http_session: aiohttp.ClientSession,
        url: str,
        depth: int,
        target: CrawlTarget,
        session: CrawlSession,
        semaphore: asyncio.Semaphore
    ) -> Union[CrawlResult, Exception]:
        """Crawl single URL and extract content."""        async with semaphore:
            try:
                # Rate limiting
                await self._apply_rate_limiting(url, target.rate_limit_delay)
                
                # Prepare request headers
                headers = self._prepare_request_headers(target)
                
                start_time = time.time()
                
                # Make HTTP request
                async with http_session.get(url, headers=headers) as response:
                    content = await response.read()
                    response_time = time.time() - start_time
                    
                    # Check if successful response
                    if response.status != 200:
                        session.pages_failed += 1
                        return Exception(f"HTTP {response.status} for {url}")
                    
                    # Create crawl result
                    result = await self._process_crawl_response(
                        url, content, response, depth, target, response_time
                    )
                    
                    # Store result
                    self.crawl_results[target.target_id].append(result)
                    session.pages_crawled += 1
                    session.data_extracted += 1
                    
                    # Check for potential copyright infringement
                    if result.similarity_score > self.similarity_threshold:
                        result.potential_infringement = True
                        session.potential_matches += 1
                    
                    return result
                    
            except Exception as e:
                session.pages_failed += 1
                session.error_logs.append(f"Error crawling {url}: {str(e)}")
                return e
    
    async def _apply_rate_limiting(self, url: str, delay: float):
        """Apply rate limiting based on domain."""        domain = urlparse(url).netloc
        current_time = time.time()
        
        # Check if we need to wait
        if domain in self.domain_last_request:
            time_since_last = current_time - self.domain_last_request[domain]
            if time_since_last < delay:
                sleep_time = delay - time_since_last
                # Add random jitter to avoid detection
                jitter = random.uniform(*self.random_delay_range)
                await asyncio.sleep(sleep_time + jitter)
        
        # Update last request time
        self.domain_last_request[domain] = time.time()
        
        # Update request count
        self.domain_request_counts[domain] = (
            self.domain_request_counts.get(domain, 0) + 1
        )
    
    def _prepare_request_headers(self, target: CrawlTarget) -> Dict[str, str]:
        """Prepare HTTP request headers with anti-detection measures."""        headers = {
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        }
        
        # Add custom headers
        headers.update(target.custom_headers)
        
        # Add authentication headers if configured
        if target.authentication:
            auth_type = target.authentication.get("type", "")
            if auth_type == "bearer":
                headers['Authorization'] = f"Bearer {target.authentication['token']}"
            elif auth_type == "api_key":
                headers[target.authentication['header']] = target.authentication['key']
        
        return headers
    
    async def _process_crawl_response(
        self,
        url: str,
        content: bytes,
        response: aiohttp.ClientResponse,
        depth: int,
        target: CrawlTarget,
        response_time: float
    ) -> CrawlResult:
        """Process crawl response and extract content."""        # Determine content type
        content_type_header = response.headers.get('content-type', '')
        content_type = self._determine_content_type(content_type_header, url)
        
        # Parse HTML content
        soup = BeautifulSoup(content, 'html.parser')
        
        # Extract basic information
        title = soup.find('title')
        title_text = title.get_text().strip() if title else None
        
        # Extract main content
        extracted_content = await self._extract_content_by_type(
            soup, content_type, target.content_types
        )
        
        # Extract links
        links = self._extract_links(soup, url)
        
        # Extract media URLs
        media_urls = self._extract_media_urls(soup, url, target.content_types)
        
        # Calculate content hash for similarity detection
        content_hash = hashlib.sha256(extracted_content.encode()).hexdigest()
        similarity_score = self._calculate_content_similarity(content_hash)
        
        # Create crawl result
        result = CrawlResult(
            crawl_id=f"crawl_{uuid.uuid4().hex[:8]}",
            target_id=target.target_id,
            url=url,
            title=title_text,
            content=extracted_content,
            content_type=content_type,
            metadata={
                'depth': depth,
                'content_hash': content_hash,
                'status_code': response.status,
                'headers': dict(response.headers),
                'encoding': response.charset or 'utf-8'
            },
            media_urls=media_urls,
            links=links,
            similarity_score=similarity_score,
            file_size=len(content),
            response_time=response_time
        )
        
        return result
    
    def _determine_content_type(self, content_type_header: str, url: str) -> ContentType:
        """Determine content type from headers and URL."""        content_type_header = content_type_header.lower()
        
        if 'image' in content_type_header:
            return ContentType.IMAGES
        elif 'video' in content_type_header:
            return ContentType.VIDEOS
        elif 'audio' in content_type_header:
            return ContentType.AUDIO
        elif 'application/pdf' in content_type_header:
            return ContentType.DOCUMENTS
        else:
            # Check URL extension
            url_lower = url.lower()
            if any(ext in url_lower for ext in ['.jpg', '.png', '.gif', '.webp']):
                return ContentType.IMAGES
            elif any(ext in url_lower for ext in ['.mp4', '.avi', '.mov', '.webm']):
                return ContentType.VIDEOS
            elif any(ext in url_lower for ext in ['.mp3', '.wav', '.ogg', '.m4a']):
                return ContentType.AUDIO
            else:
                return ContentType.TEXT
    
    async def _extract_content_by_type(
        self,
        soup: BeautifulSoup,
        content_type: ContentType,
        target_types: List[ContentType]
    ) -> str:
        """Extract content based on specified content types."""        if content_type not in target_types:
            return ""
        
        if content_type == ContentType.TEXT:
            return self._extract_text_content(soup)
        elif content_type == ContentType.SOCIAL_POSTS:
            return self._extract_social_posts(soup)
        elif content_type == ContentType.PRODUCT_LISTINGS:
            return self._extract_product_listings(soup)
        elif content_type == ContentType.COMMENTS:
            return self._extract_comments(soup)
        else:
            return self._extract_text_content(soup)
    
    def _extract_text_content(self, soup: BeautifulSoup) -> str:
        """Extract main text content from HTML."""        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.extract()
        
        # Remove comments
        comments = soup.findAll(text=lambda text: isinstance(text, Comment))
        for comment in comments:
            comment.extract()
        
        # Extract main content areas
        main_content_selectors = [
            'main', 'article', '.content', '#content', 
            '.post-content', '.entry-content', '.article-content'
        ]
        
        content_text = ""
        for selector in main_content_selectors:
            elements = soup.select(selector)
            if elements:
                content_text = elements[0].get_text().strip()
                break
        
        # Fallback to body text
        if not content_text:
            content_text = soup.get_text()
        
        # Clean up whitespace
        content_text = re.sub(r'\s+', ' ', content_text).strip()
        
        return content_text[:10000]  # Limit content length
    
    def _extract_social_posts(self, soup: BeautifulSoup) -> str:
        """Extract social media posts content."""        # Platform-specific selectors
        post_selectors = [
            '[data-testid="tweet"]',  # Twitter
            '.post', '.entry', '.status-content',  # Generic
            '[data-ad-preview="message"]',  # Facebook
            '.photo-caption', '.caption'  # Instagram
        ]
        
        posts = []
        for selector in post_selectors:
            elements = soup.select(selector)
            for element in elements[:10]:  # Limit number of posts
                post_text = element.get_text().strip()
                if post_text and len(post_text) > 10:
                    posts.append(post_text)
        
        return '\n\n'.join(posts)
    
    def _extract_product_listings(self, soup: BeautifulSoup) -> str:
        """Extract product listing information."""        product_selectors = [
            '.product-item', '.product-card', '.listing-item',
            '[data-testid="product"]', '.search-result-item'
        ]
        
        products = []
        for selector in product_selectors:
            elements = soup.select(selector)
            for element in elements[:20]:  # Limit products
                # Extract product title
                title_elem = element.select_one('.product-title, .title, h3, h2')
                title = title_elem.get_text().strip() if title_elem else ""
                
                # Extract price
                price_elem = element.select_one('.price, .cost, .amount')
                price = price_elem.get_text().strip() if price_elem else ""
                
                if title:
                    product_info = f"Title: {title}"
                    if price:
                        product_info += f" | Price: {price}"
                    products.append(product_info)
        
        return '\n'.join(products)
    
    def _extract_comments(self, soup: BeautifulSoup) -> str:
        """Extract comments and user-generated content."""        comment_selectors = [
            '.comment', '.comment-content', '.user-comment',
            '[data-testid="comment"]', '.review-content'
        ]
        
        comments = []
        for selector in comment_selectors:
            elements = soup.select(selector)
            for element in elements[:50]:  # Limit comments
                comment_text = element.get_text().strip()
                if comment_text and len(comment_text) > 5:
                    comments.append(comment_text[:500])  # Limit comment length
        
        return '\n\n'.join(comments)
    
    def _extract_links(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """Extract and normalize links from page."""        links = []
        base_domain = urlparse(base_url).netloc
        
        for link_elem in soup.find_all('a', href=True):
            href = link_elem['href']
            
            # Convert relative URLs to absolute
            absolute_url = urljoin(base_url, href)
            
            # Validate URL
            parsed_url = urlparse(absolute_url)
            if parsed_url.scheme in ['http', 'https'] and parsed_url.netloc:
                # Optionally filter to same domain or related domains
                links.append(absolute_url)
        
        # Remove duplicates and limit
        return list(set(links))[:100]
    
    def _extract_media_urls(
        self,
        soup: BeautifulSoup,
        base_url: str,
        target_types: List[ContentType]
    ) -> List[str]:
        """Extract media URLs from page."""        media_urls = []
        
        if ContentType.IMAGES in target_types:
            # Extract image URLs
            for img in soup.find_all('img', src=True):
                img_url = urljoin(base_url, img['src'])
                media_urls.append(img_url)
        
        if ContentType.VIDEOS in target_types:
            # Extract video URLs
            for video in soup.find_all('video', src=True):
                video_url = urljoin(base_url, video['src'])
                media_urls.append(video_url)
            
            # Extract video source elements
            for source in soup.find_all('source', src=True):
                source_url = urljoin(base_url, source['src'])
                media_urls.append(source_url)
        
        if ContentType.AUDIO in target_types:
            # Extract audio URLs
            for audio in soup.find_all('audio', src=True):
                audio_url = urljoin(base_url, audio['src'])
                media_urls.append(audio_url)
        
        return list(set(media_urls))[:50]  # Remove duplicates and limit
    
    def _calculate_content_similarity(self, content_hash: str) -> float:
        """Calculate content similarity score for potential infringement detection."""        if content_hash in self.content_hashes:
            return 1.0  # Exact match
        
        # Check cached similarities
        if content_hash in self.similarity_cache:
            return self.similarity_cache[content_hash]
        
        # Calculate similarity with existing content hashes
        # This is a simplified implementation - in production would use
        # more sophisticated similarity algorithms
        max_similarity = 0.0
        
        for existing_hash in list(self.content_hashes)[-1000:]:  # Check last 1000
            # Simple hash comparison (would use better algorithms in production)
            if existing_hash[:16] == content_hash[:16]:  # First 16 chars match
                similarity = 0.8
            elif existing_hash[:8] == content_hash[:8]:   # First 8 chars match
                similarity = 0.6
            else:
                similarity = 0.0
            
            max_similarity = max(max_similarity, similarity)
        
        # Cache result
        self.similarity_cache[content_hash] = max_similarity
        self.content_hashes.add(content_hash)
        
        # Cleanup caches if too large
        if len(self.content_hashes) > 10000:
            self.content_hashes = set(list(self.content_hashes)[-5000:])
        if len(self.similarity_cache) > 10000:
            # Keep most recent entries
            recent_entries = dict(list(self.similarity_cache.items())[-5000:])
            self.similarity_cache = recent_entries
        
        return max_similarity
    
    async def _calculate_link_priority(
        self,
        link: str,
        parent_result: CrawlResult,
        target: CrawlTarget
    ) -> float:
        """Calculate priority score for link in focused crawling."""        priority = 0.0
        
        # Base priority from parent result similarity
        priority += parent_result.similarity_score * 10
        
        # URL-based scoring
        link_lower = link.lower()
        
        # Positive indicators
        positive_keywords = ['download', 'file', 'content', 'media', 'gallery', 'post']
        for keyword in positive_keywords:
            if keyword in link_lower:
                priority += 2.0
        
        # Platform-specific scoring
        if target.platform_type == PlatformType.INSTAGRAM:
            if '/p/' in link or '/reel/' in link:  # Instagram posts
                priority += 5.0
        elif target.platform_type == PlatformType.YOUTUBE:
            if '/watch?v=' in link or '/shorts/' in link:  # YouTube videos
                priority += 5.0
        
        # Negative indicators
        negative_keywords = ['login', 'register', 'cart', 'checkout', 'privacy', 'terms']
        for keyword in negative_keywords:
            if keyword in link_lower:
                priority -= 5.0
        
        return max(priority, 0.0)  # Ensure non-negative
    
    async def get_crawl_results(
        self,
        target_id: str,
        filters: Dict[str, Any] = None
    ) -> List[CrawlResult]:
        """Get crawl results with optional filtering."""        if target_id not in self.crawl_results:
            return []
        
        results = self.crawl_results[target_id]
        
        if not filters:
            return results
        
        # Apply filters
        filtered_results = []
        for result in results:
            if self._matches_filters(result, filters):
                filtered_results.append(result)
        
        return filtered_results
    
    def _matches_filters(self, result: CrawlResult, filters: Dict[str, Any]) -> bool:
        """Check if crawl result matches specified filters."""        # Minimum similarity score filter
        if 'min_similarity' in filters:
            if result.similarity_score < filters['min_similarity']:
                return False
        
        # Content type filter
        if 'content_types' in filters:
            if result.content_type not in filters['content_types']:
                return False
        
        # Date range filter
        if 'date_from' in filters:
            date_from = datetime.fromisoformat(filters['date_from'])
            if result.crawled_at < date_from:
                return False
        
        if 'date_to' in filters:
            date_to = datetime.fromisoformat(filters['date_to'])
            if result.crawled_at > date_to:
                return False
        
        # Keyword filter
        if 'keywords' in filters:
            content_lower = (result.content or "").lower()
            title_lower = (result.title or "").lower()
            
            for keyword in filters['keywords']:
                if keyword.lower() in content_lower or keyword.lower() in title_lower:
                    return True
            return False
        
        return True
    
    async def cleanup_crawler_resources(self):
        """Clean up crawler resources and connections."""


        try:
            # Close HTTP connector
            if hasattr(self, 'session_connector') and self.session_connector:
                await self.session_connector.close()
            
            # Clear caches
            self.content_hashes.clear()
            self.similarity_cache.clear()
            self.domain_last_request.clear()
            self.domain_request_counts.clear()
            
            self.logger.info("Crawler resources cleaned up")
            
        except Exception as e:
            self.logger.error(f"Error cleaning up crawler resources: {e}")


# Export main classes
__all__ = [
    "WebCrawler",
    "CrawlTarget",
    "CrawlResult", 
    "CrawlSession",
    "CrawlerType",
    "CrawlingStrategy",
    "ContentType",
    "PlatformType",
    # Content Protection
    "ContentProtectionCrawler",
    "ProtectionCrawlerType", 
    "InfringementSeverity",
    "ContentFingerprint",
    "ProtectionAlert",
    "InfringementReport",
    # Social Media
    "SocialMediaCrawler",
    "SocialMediaPlatform",
    "ContentDiscoveryMode",
    "SocialMediaContent",
    "PlatformAnalytics",
    "InfluencerProfile",
    # Platform Analysis
    "PlatformAnalyzer",
    "PlatformAnalysisType",
    "AnalysisMetrics",
    "CompetitorTier",
    "PlatformMetrics",
    "CompetitorProfile",
    "TrendAnalysis",
    # Web Scraping
    "WebScrapingEngine",
    "ScrapingStrategy",
    "AntiDetectionLevel",
    "ContentExtractorType",
    "ScrapingSession",
    "ScrapedContent",
    "ProxyConfiguration",
    # API Integrations
    "APIIntegrationEngine",
    "APIProvider",
    "AuthenticationType",
    "DataFormat",
    "APICredentials",
    "APIRequest",
    "APIResponse",
    "NormalizedContent",
    # DMCA Enforcement
    "DMCAEnforcementEngine",
    "DMCARequestType",
    "EnforcementStatus",
    "PlatformDMCAPolicy",
    "CopyrightOwner",
    "CopyrightWork",
    "InfringementEvidence",
    "DMCANotice",
    "EnforcementCase"
]
