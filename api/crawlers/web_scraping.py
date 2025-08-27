"""
Professional web scraping infrastructure for distributed content monitoring.

This module implements advanced web scraping capabilities with anti-detection,
proxy rotation, headless browsing, and intelligent content extraction for
large-scale content monitoring and brand protection.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 IA-Influencer Project. All rights reserved.
Licensed under proprietary license - reproduction forbidden without written authorization.

Project Team Specialties:
- Lead AI Developer & Senior Backend Engineer: Fahed Mlaiel
- Web Scraping Infrastructure Specialist: Scalable Crawling Systems
- Anti-Detection Engineer: Bot Evasion & Stealth Technologies
- Distributed Systems Expert: Large-Scale Data Collection
- Network Security Analyst: Safe & Legal Scraping Practices
- Data Engineering Specialist: ETL & Data Pipeline Management

Contact: mlaiel@live.de

LEGAL WARNING: This software and all associated intellectual property
belong exclusively to Fahed Mlaiel. Any unauthorized copying, redistribution,
reverse engineering, or commercial use without explicit written permission
will result in immediate legal action under international copyright laws.
"""

from typing import Dict, Any, List, Optional, Union, Set, Tuple, AsyncIterator, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import asyncio
import logging
import json
import re
import time
import random
import hashlib
import uuid
from urllib.parse import urljoin, urlparse, parse_qs, quote
from pathlib import Path
import mimetypes
import base64
from concurrent.futures import ThreadPoolExecutor, as_completed

# HTTP and web scraping
import aiohttp
import requests
from aiohttp_proxy import ProxyConnector
import aiofiles

# Selenium and browser automation
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import (
    TimeoutException, NoSuchElementException, WebDriverException,
    StaleElementReferenceException
)

# Beautiful Soup and parsing
from bs4 import BeautifulSoup, Comment
import lxml
from selectolax.parser import HTMLParser

# Scrapy framework
import scrapy
from scrapy.crawler import CrawlerProcess, CrawlerRunner
from scrapy.utils.project import get_project_settings
from scrapy.http import Request, Response
from scrapy.exceptions import CloseSpider

# Content analysis
import cv2
import numpy as np
from PIL import Image
import imagehash
import pytesseract

# ML and AI
from transformers import pipeline
from sklearn.cluster import DBSCAN
import torch

from . import WebCrawler, CrawlResult, CrawlTarget, ContentType, PlatformType
from ..core.exceptions import CrawlerException, ValidationException, ScrapingException
from ..core.models import BaseModel
from ..security.encryption import EncryptionManager
from ..utils.rate_limiter import RateLimiter
from ..utils.proxy_manager import ProxyManager
from ..utils.user_agent_rotator import UserAgentRotator


class ScrapingStrategy(Enum):
    """Web scraping strategies."""
    REQUESTS_ONLY = "requests_only"
    SELENIUM_HEADLESS = "selenium_headless"
    SELENIUM_VISIBLE = "selenium_visible"
    SCRAPY_FRAMEWORK = "scrapy_framework"
    HYBRID_APPROACH = "hybrid_approach"
    STEALTH_MODE = "stealth_mode"


class AntiDetectionLevel(Enum):
    """Anti-detection protection levels."""
    MINIMAL = "minimal"
    STANDARD = "standard"
    AGGRESSIVE = "aggressive"
    MILITARY_GRADE = "military_grade"


class ContentExtractorType(Enum):
    """Content extraction types."""
    TEXT_ONLY = "text_only"
    IMAGES_ONLY = "images_only"
    VIDEOS_ONLY = "videos_only"
    MULTIMEDIA = "multimedia"
    STRUCTURED_DATA = "structured_data"
    SOCIAL_MEDIA = "social_media"
    ECOMMERCE = "ecommerce"
    NEWS_ARTICLES = "news_articles"


@dataclass
class ScrapingSession:
    """Scraping session configuration."""
    session_id: str
    target_domains: List[str]
    strategy: ScrapingStrategy
    anti_detection_level: AntiDetectionLevel
    max_pages: int = 1000
    max_depth: int = 3
    respect_robots_txt: bool = True
    use_proxies: bool = False
    rotate_user_agents: bool = True
    delay_range: Tuple[float, float] = (1.0, 3.0)
    concurrent_requests: int = 5
    timeout: int = 30
    retry_attempts: int = 3
    extract_types: List[ContentExtractorType] = field(default_factory=list)
    custom_headers: Dict[str, str] = field(default_factory=dict)
    cookies: Dict[str, str] = field(default_factory=dict)
    javascript_required: bool = False
    screenshot_enabled: bool = False
    content_filters: List[str] = field(default_factory=list)
    output_format: str = "json"
    compression_enabled: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ScrapedContent:
    """Scraped content result."""
    content_id: str
    url: str
    title: str = ""
    text_content: str = ""
    html_content: str = ""
    images: List[Dict[str, str]] = field(default_factory=list)
    videos: List[Dict[str, str]] = field(default_factory=list)
    links: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    structured_data: Dict[str, Any] = field(default_factory=dict)
    social_signals: Dict[str, int] = field(default_factory=dict)
    sentiment_score: float = 0.0
    content_hash: str = ""
    screenshot_path: str = ""
    extraction_confidence: float = 0.0
    processing_time: float = 0.0
    scraped_at: datetime = field(default_factory=datetime.utcnow)
    source_ip: str = ""
    user_agent: str = ""
    response_status: int = 200
    response_headers: Dict[str, str] = field(default_factory=dict)


@dataclass
class ProxyConfiguration:
    """Proxy server configuration."""
    proxy_type: str  # http, socks4, socks5
    host: str
    port: int
    username: Optional[str] = None
    password: Optional[str] = None
    country: Optional[str] = None
    anonymity_level: str = "elite"  # transparent, anonymous, elite
    speed_score: float = 0.0
    reliability_score: float = 0.0
    last_tested: Optional[datetime] = None
    is_active: bool = True


class WebScrapingEngine:
    """
    Advanced web scraping engine with enterprise-grade capabilities.
    
    Features:
    - Multiple scraping strategies (Requests, Selenium, Scrapy)
    - Advanced anti-detection mechanisms
    - Proxy rotation and IP management
    - Intelligent content extraction
    - Large-scale distributed scraping
    - Real-time monitoring and alerts
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = logging.getLogger("scraper.web")
        
        # Core components
        self.rate_limiter = RateLimiter(config.get("rate_limits", {}))
        self.proxy_manager = ProxyManager(config.get("proxy_config", {}))
        self.user_agent_rotator = UserAgentRotator()
        self.encryption_manager = EncryptionManager()
        
        # Scraping configuration
        self.default_headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }
        
        # Browser configurations
        self.chrome_options = self._setup_chrome_options()
        self.firefox_options = self._setup_firefox_options()
        
        # Content extractors
        self._setup_content_extractors()
        
        # Active sessions
        self.active_sessions: Dict[str, ScrapingSession] = {}
        self.session_drivers: Dict[str, webdriver.Remote] = {}
        
        # Performance metrics
        self.metrics = {
            "total_pages_scraped": 0,
            "successful_extractions": 0,
            "failed_extractions": 0,
            "blocked_requests": 0,
            "proxy_failures": 0,
            "average_response_time": 0.0
        }
    
    def _setup_chrome_options(self) -> ChromeOptions:
        """Setup Chrome browser options for scraping."""
        options = ChromeOptions()
        
        # Basic options
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        
        # Performance options
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-images")
        options.add_argument("--disable-javascript")  # Can be enabled per session
        options.add_argument("--disable-plugins")
        options.add_argument("--disable-extensions")
        
        # Privacy and security
        options.add_argument("--disable-web-security")
        options.add_argument("--allow-running-insecure-content")
        options.add_argument("--disable-features=TranslateUI")
        options.add_argument("--disable-iframes")
        
        # Anti-detection
        options.add_argument("--disable-blink-features")
        options.add_argument("--disable-automation")
        options.add_argument("--disable-browser-side-navigation")
        options.add_argument("--disable-dev-tools")
        
        return options
    
    def _setup_firefox_options(self) -> FirefoxOptions:
        """Setup Firefox browser options for scraping."""
        options = FirefoxOptions()
        
        # Basic options
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        # Performance
        options.set_preference("dom.ipc.plugins.enabled.libflashplayer.so", False)
        options.set_preference("media.volume_scale", "0.0")
        
        # Privacy
        options.set_preference("privacy.trackingprotection.enabled", True)
        options.set_preference("geo.enabled", False)
        
        return options
    
    def _setup_content_extractors(self):
        """Setup content extraction pipelines."""
        try:
            # Text summarization
            self.text_summarizer = pipeline(
                "summarization",
                model="facebook/bart-large-cnn"
            )
            
            # Sentiment analysis
            self.sentiment_analyzer = pipeline(
                "sentiment-analysis",
                model="cardiffnlp/twitter-roberta-base-sentiment-latest"
            )
            
            # Content classification
            self.content_classifier = pipeline(
                "text-classification",
                model="microsoft/DialoGPT-medium"
            )
            
            self.logger.info("Content extractors initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize content extractors: {e}")
            # Continue without ML extractors
    
    async def create_scraping_session(
        self,
        session_config: ScrapingSession
    ) -> str:
        """Create a new scraping session."""
        try:
            session_id = session_config.session_id or str(uuid.uuid4())
            session_config.session_id = session_id
            
            # Validate configuration
            self._validate_session_config(session_config)
            
            # Setup browser driver if needed
            if session_config.strategy in [
                ScrapingStrategy.SELENIUM_HEADLESS,
                ScrapingStrategy.SELENIUM_VISIBLE,
                ScrapingStrategy.STEALTH_MODE
            ]:
                driver = await self._create_browser_driver(session_config)
                self.session_drivers[session_id] = driver
            
            # Store session
            self.active_sessions[session_id] = session_config
            
            self.logger.info(f"Scraping session created: {session_id}")
            return session_id
            
        except Exception as e:
            self.logger.error(f"Failed to create scraping session: {e}")
            raise ScrapingException(f"Session creation failed: {e}")
    
    def _validate_session_config(self, config: ScrapingSession):
        """Validate scraping session configuration."""
        if not config.target_domains:
            raise ValidationException("Target domains required")
        
        if config.max_pages <= 0:
            raise ValidationException("Max pages must be positive")
        
        if config.concurrent_requests <= 0:
            raise ValidationException("Concurrent requests must be positive")
        
        # Validate delay range
        if config.delay_range[0] > config.delay_range[1]:
            raise ValidationException("Invalid delay range")
    
    async def _create_browser_driver(self, config: ScrapingSession) -> webdriver.Remote:
        """Create browser driver for session."""
        try:
            options = self.chrome_options
            
            # Configure anti-detection level
            if config.anti_detection_level == AntiDetectionLevel.AGGRESSIVE:
                options.add_argument("--user-agent=" + self.user_agent_rotator.get_random())
                options.add_argument("--disable-blink-features=AutomationControlled")
                
            elif config.anti_detection_level == AntiDetectionLevel.MILITARY_GRADE:
                # Maximum stealth configuration
                options.add_argument("--user-agent=" + self.user_agent_rotator.get_random())
                options.add_argument("--disable-blink-features=AutomationControlled")
                options.add_experimental_option("excludeSwitches", ["enable-automation"])
                options.add_experimental_option("useAutomationExtension", False)
                
                # Additional stealth options
                options.add_argument("--disable-dev-shm-usage")
                options.add_argument("--disable-extensions")
                options.add_argument("--disable-plugins")
                options.add_argument("--disable-images")
                options.add_argument("--mute-audio")
            
            # Headless configuration
            if config.strategy == ScrapingStrategy.SELENIUM_HEADLESS:
                options.add_argument("--headless")
            
            # Proxy configuration
            if config.use_proxies:
                proxy = await self.proxy_manager.get_proxy()
                if proxy:
                    options.add_argument(f"--proxy-server={proxy.host}:{proxy.port}")
            
            # Create driver
            driver = webdriver.Chrome(options=options)
            
            # Anti-detection JavaScript execution
            if config.anti_detection_level in [
                AntiDetectionLevel.AGGRESSIVE,
                AntiDetectionLevel.MILITARY_GRADE
            ]:
                driver.execute_script("""
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined,
                    });
                """)
                
                driver.execute_script("""
                    Object.defineProperty(navigator, 'plugins', {
                        get: () => [1, 2, 3, 4, 5],
                    });
                """)
            
            return driver
            
        except Exception as e:
            self.logger.error(f"Failed to create browser driver: {e}")
            raise ScrapingException(f"Browser driver creation failed: {e}")
    
    async def scrape_url(
        self,
        session_id: str,
        url: str,
        extract_types: List[ContentExtractorType] = None
    ) -> ScrapedContent:
        """Scrape content from a single URL."""
        try:
            start_time = time.time()
            
            # Get session configuration
            session = self.active_sessions.get(session_id)
            if not session:
                raise ScrapingException(f"Session not found: {session_id}")
            
            # Rate limiting
            domain = urlparse(url).netloc
            await self.rate_limiter.acquire(f"domain_{domain}")
            
            # Choose scraping method
            if session.strategy == ScrapingStrategy.REQUESTS_ONLY:
                content = await self._scrape_with_requests(session, url)
            elif session.strategy in [
                ScrapingStrategy.SELENIUM_HEADLESS,
                ScrapingStrategy.SELENIUM_VISIBLE,
                ScrapingStrategy.STEALTH_MODE
            ]:
                content = await self._scrape_with_selenium(session_id, url)
            elif session.strategy == ScrapingStrategy.SCRAPY_FRAMEWORK:
                content = await self._scrape_with_scrapy(session, url)
            else:
                content = await self._scrape_hybrid(session, url)
            
            # Extract additional content types
            extract_types = extract_types or session.extract_types
            for extract_type in extract_types:
                await self._extract_content_type(content, extract_type)
            
            # Calculate processing time
            content.processing_time = time.time() - start_time
            
            # Generate content hash
            content.content_hash = hashlib.sha256(
                (content.text_content + content.html_content).encode()
            ).hexdigest()
            
            # Update metrics
            self.metrics["total_pages_scraped"] += 1
            self.metrics["successful_extractions"] += 1
            
            self.logger.info(f"Successfully scraped: {url}")
            return content
            
        except Exception as e:
            self.metrics["failed_extractions"] += 1
            self.logger.error(f"Failed to scrape {url}: {e}")
            raise ScrapingException(f"Scraping failed for {url}: {e}")
    
    async def _scrape_with_requests(
        self,
        session: ScrapingSession,
        url: str
    ) -> ScrapedContent:
        """Scrape URL using requests library."""
        try:
            # Prepare headers
            headers = self.default_headers.copy()
            headers.update(session.custom_headers)
            
            if session.rotate_user_agents:
                headers["User-Agent"] = self.user_agent_rotator.get_random()
            
            # Setup proxy if needed
            proxies = None
            if session.use_proxies:
                proxy = await self.proxy_manager.get_proxy()
                if proxy:
                    proxy_url = f"{proxy.proxy_type}://{proxy.host}:{proxy.port}"
                    if proxy.username and proxy.password:
                        proxy_url = f"{proxy.proxy_type}://{proxy.username}:{proxy.password}@{proxy.host}:{proxy.port}"
                    proxies = {"http": proxy_url, "https": proxy_url}
            
            # Make request
            async with aiohttp.ClientSession(
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=session.timeout),
                connector=ProxyConnector.from_url(proxies.get("http")) if proxies else None
            ) as client_session:
                
                async with client_session.get(url) as response:
                    html_content = await response.text()
                    
                    # Create scraped content object
                    content = ScrapedContent(
                        content_id=str(uuid.uuid4()),
                        url=url,
                        html_content=html_content,
                        response_status=response.status,
                        response_headers=dict(response.headers),
                        user_agent=headers.get("User-Agent", "")
                    )
                    
                    # Parse HTML content
                    soup = BeautifulSoup(html_content, 'lxml')
                    
                    # Extract title
                    title_tag = soup.find('title')
                    content.title = title_tag.get_text().strip() if title_tag else ""
                    
                    # Extract text content
                    for tag in soup(["script", "style", "nav", "footer", "aside"]):
                        tag.decompose()
                    content.text_content = soup.get_text().strip()
                    
                    # Extract links
                    links = soup.find_all('a', href=True)
                    content.links = [urljoin(url, link['href']) for link in links]
                    
                    # Extract images
                    images = soup.find_all('img', src=True)
                    content.images = [{
                        "src": urljoin(url, img['src']),
                        "alt": img.get('alt', ''),
                        "title": img.get('title', '')
                    } for img in images]
                    
                    # Extract videos
                    videos = soup.find_all(['video', 'iframe'])
                    content.videos = []
                    for video in videos:
                        if video.name == 'video':
                            src = video.get('src') or (video.find('source') or {}).get('src')
                            if src:
                                content.videos.append({
                                    "src": urljoin(url, src),
                                    "type": "video"
                                })
                        elif 'youtube.com' in str(video.get('src', '')):
                            content.videos.append({
                                "src": video['src'],
                                "type": "youtube"
                            })
                    
                    # Extract metadata
                    meta_tags = soup.find_all('meta')
                    content.metadata = {}
                    for meta in meta_tags:
                        name = meta.get('name') or meta.get('property') or meta.get('itemprop')
                        content_attr = meta.get('content')
                        if name and content_attr:
                            content.metadata[name] = content_attr
                    
                    return content
            
        except Exception as e:
            self.logger.error(f"Requests scraping failed: {e}")
            raise ScrapingException(f"Requests scraping failed: {e}")
    
    async def _scrape_with_selenium(
        self,
        session_id: str,
        url: str
    ) -> ScrapedContent:
        """Scrape URL using Selenium WebDriver."""
        try:
            driver = self.session_drivers.get(session_id)
            if not driver:
                raise ScrapingException(f"No driver found for session: {session_id}")
            
            session = self.active_sessions[session_id]
            
            # Navigate to URL
            driver.get(url)
            
            # Wait for page load
            WebDriverWait(driver, session.timeout).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Handle JavaScript-heavy sites
            if session.javascript_required:
                # Wait for dynamic content
                await asyncio.sleep(random.uniform(2, 5))
                
                # Scroll to load lazy content
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                await asyncio.sleep(1)
                driver.execute_script("window.scrollTo(0, 0);")
            
            # Create content object
            content = ScrapedContent(
                content_id=str(uuid.uuid4()),
                url=url,
                html_content=driver.page_source,
                response_status=200
            )
            
            # Extract title
            try:
                content.title = driver.title or ""
            except:
                content.title = ""
            
            # Extract text content
            try:
                body = driver.find_element(By.TAG_NAME, "body")
                content.text_content = body.text
            except:
                content.text_content = ""
            
            # Extract links
            try:
                link_elements = driver.find_elements(By.TAG_NAME, "a")
                content.links = []
                for link in link_elements:
                    href = link.get_attribute("href")
                    if href:
                        content.links.append(href)
            except:
                pass
            
            # Extract images
            try:
                img_elements = driver.find_elements(By.TAG_NAME, "img")
                content.images = []
                for img in img_elements:
                    src = img.get_attribute("src")
                    if src:
                        content.images.append({
                            "src": src,
                            "alt": img.get_attribute("alt") or "",
                            "title": img.get_attribute("title") or ""
                        })
            except:
                pass
            
            # Take screenshot if enabled
            if session.screenshot_enabled:
                try:
                    screenshot_path = f"/tmp/screenshots/{session_id}_{int(time.time())}.png"
                    driver.save_screenshot(screenshot_path)
                    content.screenshot_path = screenshot_path
                except Exception as e:
                    self.logger.warning(f"Screenshot failed: {e}")
            
            return content
            
        except Exception as e:
            self.logger.error(f"Selenium scraping failed: {e}")
            raise ScrapingException(f"Selenium scraping failed: {e}")
    
    async def _scrape_with_scrapy(
        self,
        session: ScrapingSession,
        url: str
    ) -> ScrapedContent:
        """Scrape URL using Scrapy framework."""
        try:
            # This would require a more complex implementation
            # For now, fall back to requests
            return await self._scrape_with_requests(session, url)
            
        except Exception as e:
            self.logger.error(f"Scrapy scraping failed: {e}")
            raise ScrapingException(f"Scrapy scraping failed: {e}")
    
    async def _scrape_hybrid(
        self,
        session: ScrapingSession,
        url: str
    ) -> ScrapedContent:
        """Hybrid scraping approach - try requests first, fallback to Selenium."""
        try:
            # Try requests first
            try:
                return await self._scrape_with_requests(session, url)
            except:
                # Fallback to Selenium if requests fail
                self.logger.info(f"Requests failed for {url}, falling back to Selenium")
                
                # Create temporary Selenium session
                temp_session = ScrapingSession(
                    session_id=str(uuid.uuid4()),
                    target_domains=[urlparse(url).netloc],
                    strategy=ScrapingStrategy.SELENIUM_HEADLESS,
                    anti_detection_level=session.anti_detection_level
                )
                
                temp_session_id = await self.create_scraping_session(temp_session)
                content = await self._scrape_with_selenium(temp_session_id, url)
                
                # Cleanup temporary session
                await self.close_session(temp_session_id)
                
                return content
                
        except Exception as e:
            self.logger.error(f"Hybrid scraping failed: {e}")
            raise ScrapingException(f"Hybrid scraping failed: {e}")
    
    async def _extract_content_type(
        self,
        content: ScrapedContent,
        extract_type: ContentExtractorType
    ):
        """Extract specific content type from scraped data."""
        try:
            if extract_type == ContentExtractorType.STRUCTURED_DATA:
                await self._extract_structured_data(content)
            elif extract_type == ContentExtractorType.SOCIAL_MEDIA:
                await self._extract_social_signals(content)
            elif extract_type == ContentExtractorType.ECOMMERCE:
                await self._extract_ecommerce_data(content)
            elif extract_type == ContentExtractorType.NEWS_ARTICLES:
                await self._extract_article_data(content)
            
        except Exception as e:
            self.logger.error(f"Content extraction failed for {extract_type}: {e}")
    
    async def _extract_structured_data(self, content: ScrapedContent):
        """Extract structured data (JSON-LD, microdata, etc.)."""
        try:
            soup = BeautifulSoup(content.html_content, 'lxml')
            structured_data = {}
            
            # Extract JSON-LD
            json_ld_scripts = soup.find_all('script', type='application/ld+json')
            json_ld_data = []
            for script in json_ld_scripts:
                try:
                    data = json.loads(script.string)
                    json_ld_data.append(data)
                except:
                    continue
            
            if json_ld_data:
                structured_data['json_ld'] = json_ld_data
            
            # Extract Open Graph data
            og_data = {}
            og_tags = soup.find_all('meta', property=lambda x: x and x.startswith('og:'))
            for tag in og_tags:
                property_name = tag.get('property')
                content_value = tag.get('content')
                if property_name and content_value:
                    og_data[property_name] = content_value
            
            if og_data:
                structured_data['open_graph'] = og_data
            
            # Extract Twitter Card data
            twitter_data = {}
            twitter_tags = soup.find_all('meta', attrs={'name': lambda x: x and x.startswith('twitter:')})
            for tag in twitter_tags:
                name = tag.get('name')
                content_value = tag.get('content')
                if name and content_value:
                    twitter_data[name] = content_value
            
            if twitter_data:
                structured_data['twitter_card'] = twitter_data
            
            content.structured_data = structured_data
            
        except Exception as e:
            self.logger.error(f"Structured data extraction failed: {e}")
    
    async def _extract_social_signals(self, content: ScrapedContent):
        """Extract social media signals and engagement metrics."""
        try:
            social_signals = {}
            
            # Look for social share buttons and counts
            soup = BeautifulSoup(content.html_content, 'lxml')
            
            # Facebook shares
            fb_elements = soup.find_all(text=re.compile(r'\d+.*share', re.I))
            for element in fb_elements:
                numbers = re.findall(r'\d+', str(element))
                if numbers:
                    social_signals['facebook_shares'] = max(int(num) for num in numbers)
                    break
            
            # Twitter mentions
            twitter_elements = soup.find_all(text=re.compile(r'\d+.*tweet', re.I))
            for element in twitter_elements:
                numbers = re.findall(r'\d+', str(element))
                if numbers:
                    social_signals['twitter_shares'] = max(int(num) for num in numbers)
                    break
            
            # LinkedIn shares
            linkedin_elements = soup.find_all(text=re.compile(r'\d+.*linkedin', re.I))
            for element in linkedin_elements:
                numbers = re.findall(r'\d+', str(element))
                if numbers:
                    social_signals['linkedin_shares'] = max(int(num) for num in numbers)
                    break
            
            content.social_signals = social_signals
            
        except Exception as e:
            self.logger.error(f"Social signals extraction failed: {e}")
    
    async def _extract_ecommerce_data(self, content: ScrapedContent):
        """Extract e-commerce specific data."""
        try:
            soup = BeautifulSoup(content.html_content, 'lxml')
            ecommerce_data = {}
            
            # Extract price information
            price_selectors = [
                '.price', '.cost', '.amount', '[class*="price"]',
                '[id*="price"]', '.money', '.currency'
            ]
            
            for selector in price_selectors:
                price_elements = soup.select(selector)
                for element in price_elements:
                    price_text = element.get_text().strip()
                    # Look for currency symbols and numbers
                    price_match = re.search(r'[\$€£¥₹][\d,.]+ | [\d,.]+\s*[\$€£¥₹]', price_text)
                    if price_match:
                        ecommerce_data['price'] = price_match.group().strip()
                        break
                if 'price' in ecommerce_data:
                    break
            
            # Extract product ratings
            rating_selectors = [
                '.rating', '.stars', '[class*="rating"]',
                '[class*="star"]', '.score'
            ]
            
            for selector in rating_selectors:
                rating_elements = soup.select(selector)
                for element in rating_elements:
                    rating_text = element.get_text().strip()
                    rating_match = re.search(r'(\d+\.?\d*)\s*(?:out of|/|\s)\s*(\d+)', rating_text)
                    if rating_match:
                        ecommerce_data['rating'] = f"{rating_match.group(1)}/{rating_match.group(2)}"
                        break
                if 'rating' in ecommerce_data:
                    break
            
            # Extract availability
            availability_keywords = ['in stock', 'available', 'sold out', 'out of stock']
            page_text = content.text_content.lower()
            for keyword in availability_keywords:
                if keyword in page_text:
                    ecommerce_data['availability'] = keyword
                    break
            
            if ecommerce_data:
                content.structured_data['ecommerce'] = ecommerce_data
            
        except Exception as e:
            self.logger.error(f"E-commerce data extraction failed: {e}")
    
    async def _extract_article_data(self, content: ScrapedContent):
        """Extract news article specific data."""
        try:
            soup = BeautifulSoup(content.html_content, 'lxml')
            article_data = {}
            
            # Extract publish date
            date_selectors = [
                'time[datetime]', '.publish-date', '.date',
                '[class*="date"]', '[id*="date"]'
            ]
            
            for selector in date_selectors:
                date_elements = soup.select(selector)
                for element in date_elements:
                    datetime_attr = element.get('datetime')
                    if datetime_attr:
                        article_data['publish_date'] = datetime_attr
                        break
                    
                    date_text = element.get_text().strip()
                    # Basic date pattern matching
                    date_match = re.search(
                        r'(\d{1,2}[/-]\d{1,2}[/-]\d{4}|\d{4}[/-]\d{1,2}[/-]\d{1,2})',
                        date_text
                    )
                    if date_match:
                        article_data['publish_date'] = date_match.group(1)
                        break
                if 'publish_date' in article_data:
                    break
            
            # Extract author
            author_selectors = [
                '.author', '.byline', '[class*="author"]',
                '[rel="author"]', '.writer'
            ]
            
            for selector in author_selectors:
                author_elements = soup.select(selector)
                for element in author_elements:
                    author_text = element.get_text().strip()
                    if author_text and len(author_text) < 100:  # Reasonable author name length
                        article_data['author'] = author_text
                        break
                if 'author' in article_data:
                    break
            
            # Extract article category/tags
            tag_selectors = [
                '.tags', '.categories', '.category',
                '[class*="tag"]', '.keywords'
            ]
            
            tags = []
            for selector in tag_selectors:
                tag_elements = soup.select(selector)
                for element in tag_elements:
                    # Look for links or list items within tag containers
                    tag_links = element.find_all(['a', 'li', 'span'])
                    if tag_links:
                        tags.extend([link.get_text().strip() for link in tag_links])
                    else:
                        # Split on commas if no sub-elements
                        tag_text = element.get_text().strip()
                        if ',' in tag_text:
                            tags.extend([tag.strip() for tag in tag_text.split(',')])
                
            if tags:
                article_data['tags'] = list(set(tags))  # Remove duplicates
            
            if article_data:
                content.structured_data['article'] = article_data
            
        except Exception as e:
            self.logger.error(f"Article data extraction failed: {e}")
    
    async def bulk_scrape_urls(
        self,
        session_id: str,
        urls: List[str],
        max_concurrent: int = None
    ) -> List[ScrapedContent]:
        """Scrape multiple URLs concurrently."""
        try:
            session = self.active_sessions.get(session_id)
            if not session:
                raise ScrapingException(f"Session not found: {session_id}")
            
            max_concurrent = max_concurrent or session.concurrent_requests
            
            # Process URLs in batches
            results = []
            semaphore = asyncio.Semaphore(max_concurrent)
            
            async def scrape_with_semaphore(url):
                async with semaphore:
                    try:
                        # Add delay between requests
                        delay = random.uniform(*session.delay_range)
                        await asyncio.sleep(delay)
                        
                        return await self.scrape_url(session_id, url)
                    except Exception as e:
                        self.logger.error(f"Failed to scrape {url}: {e}")
                        return None
            
            # Create tasks
            tasks = [scrape_with_semaphore(url) for url in urls]
            
            # Execute tasks
            scrape_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Filter successful results
            for result in scrape_results:
                if isinstance(result, ScrapedContent):
                    results.append(result)
                elif isinstance(result, Exception):
                    self.logger.error(f"Scraping task failed: {result}")
            
            self.logger.info(f"Bulk scraping completed: {len(results)}/{len(urls)} successful")
            return results
            
        except Exception as e:
            self.logger.error(f"Bulk scraping failed: {e}")
            raise ScrapingException(f"Bulk scraping failed: {e}")
    
    async def close_session(self, session_id: str):
        """Close and cleanup scraping session."""
        try:
            # Close browser driver if exists
            if session_id in self.session_drivers:
                driver = self.session_drivers[session_id]
                driver.quit()
                del self.session_drivers[session_id]
            
            # Remove session
            if session_id in self.active_sessions:
                del self.active_sessions[session_id]
            
            self.logger.info(f"Session closed: {session_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to close session {session_id}: {e}")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get scraping performance metrics."""
        return {
            **self.metrics,
            "active_sessions": len(self.active_sessions),
            "active_drivers": len(self.session_drivers)
        }
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit - cleanup all sessions."""
        for session_id in list(self.active_sessions.keys()):
            await self.close_session(session_id)


class ScrapingSessionManager:
    """Manager for multiple scraping sessions."""
    
    def __init__(self, max_sessions: int = 10):
        self.max_sessions = max_sessions
        self.scraping_engine = WebScrapingEngine()
        self.session_queue = asyncio.Queue(maxsize=max_sessions)
        self.active_sessions = {}
    
    async def create_managed_session(self, config: ScrapingSession) -> str:
        """Create a managed scraping session."""
        if len(self.active_sessions) >= self.max_sessions:
            # Wait for available session slot
            await self.session_queue.get()
        
        session_id = await self.scraping_engine.create_scraping_session(config)
        self.active_sessions[session_id] = config
        
        return session_id
    
    async def close_managed_session(self, session_id: str):
        """Close a managed session and free up slot."""
        await self.scraping_engine.close_session(session_id)
        
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]
            
        # Signal available slot
        try:
            self.session_queue.put_nowait(None)
        except asyncio.QueueFull:
            pass
