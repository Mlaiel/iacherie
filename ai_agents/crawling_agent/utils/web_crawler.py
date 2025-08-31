"""Advanced Web Crawler - High-Performance Multi-Platform Content Extraction Engine

Industrial-grade web crawling system with stealth capabilities, JavaScript rendering,
and intelligent content extraction for the IA-Influencer-Agent platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  IMPORTANT LEGAL NOTICE:
This code and concept are the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, copying, distribution, or commercialization without explicit written permission is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.

Team Specialties:
- Lead AI Developer & Backend Senior Engineer
- Machine Learning Engineer & Audio Processing Specialist  
- Database Administrator & Security Expert
- Microservices Architect & DevOps Engineer
- AI Prompt Engineer & Content Protection Specialist
"""
import asyncio
import logging
import time
import hashlib
import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set, Tuple, Union, AsyncGenerator
from dataclasses import dataclass, field
from enum import Enum
from urllib.parse import urljoin, urlparse, urlencode
from urllib.robotparser import RobotFileParser
import re

import aiohttp
import aiofiles
from bs4 import BeautifulSoup, Comment
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
import scrapy
from scrapy.http import Request, Response
from scrapy.spiders import Spider
from scrapy.crawler import CrawlerRunner
from twisted.internet import reactor, defer
import feedparser
import newspaper
from newspaper import Article
import readability
from goose3 import Goose
import trafilatura

try:
    from core.config import settings
except ImportError:
    # Fallback settings
    settings = type('Settings', (), {'debug': True, 'log_level': 'INFO'})()
try:
    from core.exceptions import CrawlingError, ValidationError, SecurityError
except ImportError:
    # Fallback exception classes
    class ValidationError(Exception): pass
    class ConfigurationError(Exception): pass
    class ProcessingError(Exception): pass
    CrawlingError, ValidationError, SecurityError = globals().get('CrawlingError, ValidationError, SecurityError', Exception)
from ...utils.rate_limiter import RateLimiter
from ...utils.proxy_manager import ProxyManager
from ...utils.user_agent_rotator import UserAgentRotator
from ...utils.cache_manager import CacheManager
from ...security.content_sanitizer import ContentSanitizer

logger = logging.getLogger(__name__)

class CrawlerMode(Enum):
    """Web crawler operational modes"""    FAST = "fast"
    THOROUGH = "thorough"
    STEALTH = "stealth"
    JAVASCRIPT = "javascript"
    HEADLESS = "headless"
    RESEARCH = "research"

class ContentExtractionMethod(Enum):
    """Content extraction methods"""    BEAUTIFULSOUP = "beautifulsoup"
    NEWSPAPER = "newspaper"
    TRAFILATURA = "trafilatura"
    GOOSE = "goose"
    READABILITY = "readability"
    CUSTOM = "custom"

class RobotsPolicyLevel(Enum):
    """Robots.txt compliance levels"""    STRICT = "strict"
    MODERATE = "moderate"
    LENIENT = "lenient"
    IGNORE = "ignore"

@dataclass
class CrawlerConfig:
    """Comprehensive crawler configuration"""    mode: CrawlerMode = CrawlerMode.THOROUGH
    max_concurrent_requests: int = 10
    max_pages_per_domain: int = 1000
    max_crawl_depth: int = 3
    request_delay: float = 1.0
    request_timeout: int = 30
    max_retries: int = 3
    retry_delay: float = 2.0
    
    # Content extraction
    extraction_method: ContentExtractionMethod = ContentExtractionMethod.TRAFILATURA
    min_content_length: int = 100
    max_content_length: int = 100000
    extract_images: bool = True
    extract_links: bool = True
    extract_metadata: bool = True
    
    # Browser settings
    headless_browser: bool = True
    javascript_timeout: int = 10
    page_load_timeout: int = 30
    window_size: Tuple[int, int] = (1920, 1080)
    
    # Compliance and ethics
    robots_policy: RobotsPolicyLevel = RobotsPolicyLevel.MODERATE
    respect_crawl_delay: bool = True
    user_agent_rotation: bool = True
    proxy_rotation: bool = True
    
    # Performance and caching
    enable_caching: bool = True
    cache_ttl_hours: int = 24
    compress_content: bool = True
    
    # Security and safety
    sanitize_content: bool = True
    block_malicious_domains: bool = True
    max_redirect_follows: int = 5

@dataclass
class CrawlResult:
    """Comprehensive crawl result structure"""    url: str
    status_code: int
    title: str
    content: str
    cleaned_content: str
    html: str
    
    # Metadata
    metadata: Dict[str, Any]
    headers: Dict[str, str]
    cookies: Dict[str, str]
    
    # Content analysis
    language: str
    encoding: str
    content_type: str
    content_length: int
    word_count: int
    
    # Links and media
    internal_links: List[str]
    external_links: List[str]
    images: List[Dict[str, str]]
    videos: List[Dict[str, str]]
    
    # Technical details
    response_time: float
    final_url: str
    redirect_chain: List[str]
    crawl_timestamp: datetime
    
    # Quality metrics
    readability_score: float
    content_quality_score: float
    seo_score: float
    
    # Fingerprinting
    content_hash: str
    structure_hash: str
    
    # Error handling
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

class WebCrawler:
    """    Advanced Web Crawler with Multi-Method Content Extraction
    
    High-performance web crawler capable of handling JavaScript-heavy sites,
    respecting robots.txt, rotating proxies/user agents, and extracting clean content.
    """    
    def __init__(self, config: Optional[CrawlerConfig] = None):
        self.config = config or CrawlerConfig()
        
        # Core components
        self.session: Optional[aiohttp.ClientSession] = None
        self.selenium_driver: Optional[webdriver.Chrome] = None
        self.rate_limiter = RateLimiter(
            max_requests=self.config.max_concurrent_requests,
            window_seconds=60
        )
        self.proxy_manager = ProxyManager()
        self.user_agent_rotator = UserAgentRotator()
        self.cache_manager = CacheManager() if self.config.enable_caching else None
        self.content_sanitizer = ContentSanitizer()
        
        # Content extraction engines
        self.goose = Goose()
        self.newspaper_config = newspaper.Config()
        self.newspaper_config.memoize_articles = False
        self.newspaper_config.fetch_images = self.config.extract_images
        
        # State tracking
        self.crawled_urls: Set[str] = set()
        self.failed_urls: Set[str] = set()
        self.robots_cache: Dict[str, RobotFileParser] = {}
        self.domain_delays: Dict[str, float] = {}
        
        # Statistics
        self.stats = {
            'requests_made': 0,
            'successful_crawls': 0,
            'failed_crawls': 0,
            'bytes_downloaded': 0,
            'average_response_time': 0.0,
            'cache_hits': 0,
            'cache_misses': 0
        }
        
        logger.info(f"Web Crawler initialized in {self.config.mode.value} mode")

    async def initialize(self) -> None:
        """Initialize crawler components and connections"""        try:
            # Setup HTTP session
            connector = aiohttp.TCPConnector(
                limit=self.config.max_concurrent_requests,
                limit_per_host=5,
                ttl_dns_cache=300,
                use_dns_cache=True,
                keepalive_timeout=60,
                enable_cleanup_closed=True
            )
            
            timeout = aiohttp.ClientTimeout(
                total=self.config.request_timeout,
                connect=10,
                sock_read=self.config.request_timeout
            )
            
            self.session = aiohttp.ClientSession(
                connector=connector,
                timeout=timeout,
                headers=self._get_default_headers()
            )
            
            # Initialize Selenium if JavaScript mode
            if self.config.mode in [CrawlerMode.JAVASCRIPT, CrawlerMode.STEALTH]:
                await self._setup_selenium()
            
            # Initialize cache
            if self.cache_manager:
                await self.cache_manager.initialize()
            
            logger.info("Web Crawler initialization complete")
            
        except Exception as e:
            logger.error(f"Failed to initialize Web Crawler: {str(e)}")
            raise CrawlingError(f"Crawler initialization failed: {str(e)}")

    async def _setup_selenium(self) -> None:
        """Setup Selenium WebDriver with optimal configuration"""        chrome_options = Options()
        
        # Basic options
        if self.config.headless_browser:
            chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument(f'--window-size={self.config.window_size[0]},{self.config.window_size[1]}')
        
        # Performance optimizations
        chrome_options.add_argument('--disable-background-timer-throttling')
        chrome_options.add_argument('--disable-backgrounding-occluded-windows')
        chrome_options.add_argument('--disable-renderer-backgrounding')
        chrome_options.add_argument('--disable-features=TranslateUI')
        chrome_options.add_argument('--disable-ipc-flooding-protection')
        
        # Stealth mode enhancements
        if self.config.mode == CrawlerMode.STEALTH:
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            chrome_options.add_argument('--disable-web-security')
            chrome_options.add_argument('--allow-running-insecure-content')
        
        # Memory and performance
        chrome_options.add_argument('--max_old_space_size=4096')
        chrome_options.add_argument('--memory-pressure-off')
        
        try:
            self.selenium_driver = webdriver.Chrome(options=chrome_options)
            
            if self.config.mode == CrawlerMode.STEALTH:
                # Execute stealth scripts
                self.selenium_driver.execute_script("""                    Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                    Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
                    Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
                """)
            
            # Set timeouts
            self.selenium_driver.set_page_load_timeout(self.config.page_load_timeout)
            self.selenium_driver.implicitly_wait(self.config.javascript_timeout)
            
        except Exception as e:
            logger.error(f"Failed to setup Selenium driver: {str(e)}")
            raise

    def _get_default_headers(self) -> Dict[str, str]:
        """Generate default HTTP headers"""        return {
            'User-Agent': self.user_agent_rotator.get_random_agent(),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }

    async def crawl_url(self, url: str, **kwargs) -> Optional[CrawlResult]:
        """Crawl single URL with comprehensive error handling"""        start_time = time.time()
        
        try:
            # URL validation and normalization
            normalized_url = self._normalize_url(url)
            if not self._is_valid_url(normalized_url):
                raise ValidationError(f"Invalid URL: {url}")
            
            # Check if already crawled
            if normalized_url in self.crawled_urls:
                logger.debug(f"URL already crawled: {normalized_url}")
                return None
            
            # Check cache first
            if self.cache_manager:
                cached_result = await self.cache_manager.get(normalized_url)
                if cached_result:
                    self.stats['cache_hits'] += 1
                    return cached_result
                self.stats['cache_misses'] += 1
            
            # Check robots.txt compliance
            if not await self._check_robots_compliance(normalized_url):
                logger.warning(f"Robots.txt disallows crawling: {normalized_url}")
                return None
            
            # Apply rate limiting
            await self._apply_rate_limiting(normalized_url)
            
            # Perform the crawl
            crawl_result = await self._perform_crawl(normalized_url, **kwargs)
            
            if crawl_result:
                # Post-process result
                crawl_result = await self._post_process_result(crawl_result)
                
                # Cache result
                if self.cache_manager and crawl_result.status_code == 200:
                    await self.cache_manager.set(
                        normalized_url, 
                        crawl_result, 
                        ttl_hours=self.config.cache_ttl_hours
                    )
                
                # Update statistics
                self.crawled_urls.add(normalized_url)
                self.stats['successful_crawls'] += 1
                self.stats['bytes_downloaded'] += crawl_result.content_length
                
                # Update average response time
                response_time = time.time() - start_time
                self.stats['average_response_time'] = (
                    (self.stats['average_response_time'] * (self.stats['successful_crawls'] - 1) + response_time) /
                    self.stats['successful_crawls']
                )
                
                return crawl_result
            
        except Exception as e:
            self.failed_urls.add(url)
            self.stats['failed_crawls'] += 1
            logger.error(f"Failed to crawl {url}: {str(e)}")
            
            # Return error result
            return CrawlResult(
                url=url,
                status_code=0,
                title="",
                content="",
                cleaned_content="",
                html="",
                metadata={},
                headers={},
                cookies={},
                language="",
                encoding="",
                content_type="",
                content_length=0,
                word_count=0,
                internal_links=[],
                external_links=[],
                images=[],
                videos=[],
                response_time=time.time() - start_time,
                final_url=url,
                redirect_chain=[],
                crawl_timestamp=datetime.now(),
                readability_score=0.0,
                content_quality_score=0.0,
                seo_score=0.0,
                content_hash="",
                structure_hash="",
                errors=[str(e)]
            )
        
        finally:
            self.stats['requests_made'] += 1

    async def _perform_crawl(self, url: str, **kwargs) -> Optional[CrawlResult]:
        """Perform actual crawling based on configured mode"""        if self.config.mode == CrawlerMode.JAVASCRIPT or kwargs.get('require_js', False):
            return await self._crawl_with_selenium(url, **kwargs)
        else:
            return await self._crawl_with_aiohttp(url, **kwargs)

    async def _crawl_with_aiohttp(self, url: str, **kwargs) -> Optional[CrawlResult]:
        """Crawl URL using aiohttp for fast static content"""        headers = self._get_request_headers()
        proxy = None
        
        if self.config.proxy_rotation:
            proxy = await self.proxy_manager.get_proxy()
        
        try:
            async with self.session.get(url, headers=headers, proxy=proxy, 
                                      allow_redirects=True, max_redirects=self.config.max_redirect_follows) as response:
                
                # Track redirect chain
                redirect_chain = []
                if response.history:
                    redirect_chain = [str(resp.url) for resp in response.history]
                
                # Read content
                content_bytes = await response.read()
                
                # Determine encoding
                encoding = self._detect_encoding(content_bytes, response.headers)
                html_content = content_bytes.decode(encoding, errors='replace')
                
                # Create crawl result
                return await self._build_crawl_result(
                    url=url,
                    status_code=response.status,
                    headers=dict(response.headers),
                    html_content=html_content,
                    final_url=str(response.url),
                    redirect_chain=redirect_chain,
                    encoding=encoding,
                    response_time=0.0  # Will be calculated by caller
                )
                
        except asyncio.TimeoutError:
            logger.warning(f"Timeout crawling {url}")
            return None
        except Exception as e:
            logger.error(f"HTTP crawl error for {url}: {str(e)}")
            return None

    async def _crawl_with_selenium(self, url: str, **kwargs) -> Optional[CrawlResult]:
        """Crawl URL using Selenium for JavaScript-heavy content"""        if not self.selenium_driver:
            await self._setup_selenium()
        
        try:
            # Navigate to URL
            self.selenium_driver.get(url)
            
            # Wait for page load
            WebDriverWait(self.selenium_driver, self.config.page_load_timeout).until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )
            
            # Additional wait for JavaScript content
            if kwargs.get('js_wait_time'):
                await asyncio.sleep(kwargs['js_wait_time'])
            
            # Get page source and metadata
            html_content = self.selenium_driver.page_source
            final_url = self.selenium_driver.current_url
            
            # Get cookies
            cookies = {cookie['name']: cookie['value'] for cookie in self.selenium_driver.get_cookies()}
            
            # Simulate headers (Selenium doesn't provide response headers)
            headers = {
                'content-type': 'text/html; charset=utf-8',
                'status': '200'
            }
            
            return await self._build_crawl_result(
                url=url,
                status_code=200,
                headers=headers,
                html_content=html_content,
                final_url=final_url,
                redirect_chain=[],
                encoding='utf-8',
                response_time=0.0,
                cookies=cookies
            )
            
        except TimeoutException:
            logger.warning(f"Selenium timeout for {url}")
            return None
        except WebDriverException as e:
            logger.error(f"Selenium error for {url}: {str(e)}")
            return None

    def _get_request_headers(self) -> Dict[str, str]:
        """Generate request headers with rotation"""        headers = self._get_default_headers()
        
        if self.config.user_agent_rotation:
            headers['User-Agent'] = self.user_agent_rotator.get_random_agent()
        
        # Add random headers for stealth
        if self.config.mode == CrawlerMode.STEALTH:
            headers.update({
                'Cache-Control': random.choice(['no-cache', 'max-age=0', 'must-revalidate']),
                'Pragma': 'no-cache',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1'
            })
        
        return headers

    def _detect_encoding(self, content: bytes, headers: Dict[str, str]) -> str:
        """Detect content encoding from headers and content"""        # Check Content-Type header
        content_type = headers.get('content-type', '').lower()
        if 'charset=' in content_type:
            try:
                return content_type.split('charset=')[1].split(';')[0].strip()
            except:
                pass
        
        # Check HTML meta tags
        try:
            html_start = content[:2048].decode('utf-8', errors='ignore')
            soup = BeautifulSoup(html_start, 'html.parser')
            
            # Look for charset in meta tags
            meta_charset = soup.find('meta', charset=True)
            if meta_charset:
                return meta_charset['charset']
            
            # Look for http-equiv content-type
            meta_content_type = soup.find('meta', attrs={'http-equiv': 'content-type'})
            if meta_content_type and meta_content_type.get('content'):
                content_attr = meta_content_type['content'].lower()
                if 'charset=' in content_attr:
                    return content_attr.split('charset=')[1].split(';')[0].strip()
        except:
            pass
        
        return 'utf-8'  # Default fallback

    async def _build_crawl_result(self, url: str, status_code: int, headers: Dict[str, str],
                                html_content: str, final_url: str, redirect_chain: List[str],
                                encoding: str, response_time: float, cookies: Dict[str, str] = None) -> CrawlResult:
        """Build comprehensive crawl result from raw response data"""        
        # Parse HTML
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Extract title
        title_elem = soup.find('title')
        title = title_elem.get_text().strip() if title_elem else ""
        
        # Extract content using configured method
        content, cleaned_content = await self._extract_content(html_content, soup)
        
        # Extract metadata
        metadata = self._extract_comprehensive_metadata(soup)
        
        # Extract links
        internal_links, external_links = self._extract_and_categorize_links(soup, final_url)
        
        # Extract media
        images = self._extract_images_with_metadata(soup, final_url) if self.config.extract_images else []
        videos = self._extract_videos_with_metadata(soup, final_url) if self.config.extract_images else []
        
        # Calculate quality metrics
        readability_score = self._calculate_readability_score(cleaned_content)
        content_quality_score = self._calculate_content_quality(soup, cleaned_content)
        seo_score = self._calculate_seo_score(soup, metadata)
        
        # Generate fingerprints
        content_hash = hashlib.sha256(cleaned_content.encode()).hexdigest()
        structure_hash = hashlib.sha256(str(soup.find_all()).encode()).hexdigest()
        
        # Detect language
        language = self._detect_content_language(cleaned_content)
        
        return CrawlResult(
            url=url,
            status_code=status_code,
            title=title,
            content=content,
            cleaned_content=cleaned_content,
            html=html_content,
            metadata=metadata,
            headers=headers,
            cookies=cookies or {},
            language=language,
            encoding=encoding,
            content_type=headers.get('content-type', ''),
            content_length=len(html_content.encode()),
            word_count=len(cleaned_content.split()),
            internal_links=internal_links,
            external_links=external_links,
            images=images,
            videos=videos,
            response_time=response_time,
            final_url=final_url,
            redirect_chain=redirect_chain,
            crawl_timestamp=datetime.now(),
            readability_score=readability_score,
            content_quality_score=content_quality_score,
            seo_score=seo_score,
            content_hash=content_hash,
            structure_hash=structure_hash
        )

    async def _extract_content(self, html: str, soup: BeautifulSoup) -> Tuple[str, str]:
        """Extract and clean content using configured method"""        raw_content = ""
        cleaned_content = ""
        
        try:
            if self.config.extraction_method == ContentExtractionMethod.TRAFILATURA:
                cleaned_content = trafilatura.extract(html) or ""
                raw_content = soup.get_text(separator=' ', strip=True)
                
            elif self.config.extraction_method == ContentExtractionMethod.NEWSPAPER:
                article = Article("")
                article.set_html(html)
                article.parse()
                cleaned_content = article.text
                raw_content = soup.get_text(separator=' ', strip=True)
                
            elif self.config.extraction_method == ContentExtractionMethod.GOOSE:
                article = self.goose.extract(raw_html=html)
                cleaned_content = article.cleaned_text or ""
                raw_content = soup.get_text(separator=' ', strip=True)
                
            elif self.config.extraction_method == ContentExtractionMethod.READABILITY:
                doc = readability.Document(html)
                cleaned_content = BeautifulSoup(doc.summary(), 'html.parser').get_text(separator=' ', strip=True)
                raw_content = soup.get_text(separator=' ', strip=True)
                
            else:  # BEAUTIFULSOUP or CUSTOM
                cleaned_content = self._extract_main_content_heuristic(soup)
                raw_content = soup.get_text(separator=' ', strip=True)
            
            # Apply content sanitization
            if self.config.sanitize_content:
                cleaned_content = self.content_sanitizer.sanitize_text(cleaned_content)
                raw_content = self.content_sanitizer.sanitize_text(raw_content)
            
            # Apply length constraints
            if len(cleaned_content) < self.config.min_content_length:
                cleaned_content = raw_content[:self.config.max_content_length]
            elif len(cleaned_content) > self.config.max_content_length:
                cleaned_content = cleaned_content[:self.config.max_content_length]
                
        except Exception as e:
            logger.error(f"Content extraction failed: {str(e)}")
            # Fallback to basic extraction
            raw_content = soup.get_text(separator=' ', strip=True)
            cleaned_content = raw_content[:self.config.max_content_length]
        
        return raw_content, cleaned_content

    def _extract_main_content_heuristic(self, soup: BeautifulSoup) -> str:
        """Extract main content using heuristic approach"""        # Remove unwanted elements
        for element in soup(['script', 'style', 'nav', 'footer', 'header', 
                           'aside', 'sidebar', 'menu', 'advertisement']):
            element.decompose()
        
        # Remove comments
        for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
            comment.extract()
        
        # Try semantic HTML5 elements first
        main_content = soup.find('main')
        if main_content:
            return main_content.get_text(separator=' ', strip=True)
        
        article_content = soup.find('article')
        if article_content:
            return article_content.get_text(separator=' ', strip=True)
        
        # Try common content class names
        content_selectors = [
            '.content', '#content', '.post', '.entry', '.article',
            '.story', '.text', '.body', '.main', '.primary'
        ]
        
        for selector in content_selectors:
            content_elem = soup.select_one(selector)
            if content_elem:
                text = content_elem.get_text(separator=' ', strip=True)
                if len(text) > 100:  # Minimum content threshold
                    return text
        
        # Fallback to largest text block
        return self._find_largest_text_block(soup)

    def _find_largest_text_block(self, soup: BeautifulSoup) -> str:
        """Find the largest text block in the document"""        largest_block = ""
        largest_size = 0
        
        for element in soup.find_all(['div', 'section', 'article', 'p']):
            text = element.get_text(separator=' ', strip=True)
            if len(text) > largest_size:
                largest_size = len(text)
                largest_block = text
        
        return largest_block

    def _extract_comprehensive_metadata(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract comprehensive metadata from HTML"""        metadata = {}
        
        # Basic meta tags
        for meta in soup.find_all('meta'):
            name = meta.get('name') or meta.get('property') or meta.get('http-equiv')
            content = meta.get('content')
            if name and content:
                metadata[name.lower()] = content
        
        # Open Graph tags
        og_tags = {}
        for meta in soup.find_all('meta', attrs={'property': lambda x: x and x.startswith('og:')}):
            prop = meta.get('property')[3:]  # Remove 'og:' prefix
            og_tags[prop] = meta.get('content')
        if og_tags:
            metadata['open_graph'] = og_tags
        
        # Twitter Card tags
        twitter_tags = {}
        for meta in soup.find_all('meta', attrs={'name': lambda x: x and x.startswith('twitter:')}):
            name = meta.get('name')[8:]  # Remove 'twitter:' prefix
            twitter_tags[name] = meta.get('content')
        if twitter_tags:
            metadata['twitter_card'] = twitter_tags
        
        # Schema.org structured data
        structured_data = []
        for script in soup.find_all('script', type='application/ld+json'):
            try:
                data = json.loads(script.string)
                structured_data.append(data)
            except (json.JSONDecodeError, AttributeError):
                continue
        if structured_data:
            metadata['structured_data'] = structured_data
        
        # HTML lang attribute
        html_tag = soup.find('html')
        if html_tag and html_tag.get('lang'):
            metadata['html_lang'] = html_tag['lang']
        
        # Canonical URL
        canonical = soup.find('link', rel='canonical')
        if canonical and canonical.get('href'):
            metadata['canonical_url'] = canonical['href']
        
        # Author information
        author_meta = soup.find('meta', attrs={'name': 'author'})
        if author_meta:
            metadata['author'] = author_meta.get('content')
        
        # Publication date
        date_selectors = [
            'meta[name="date"]',
            'meta[name="publish-date"]',
            'meta[property="article:published_time"]',
            'time[datetime]',
            '.date', '.publish-date', '.timestamp'
        ]
        
        for selector in date_selectors:
            date_elem = soup.select_one(selector)
            if date_elem:
                date_value = date_elem.get('content') or date_elem.get('datetime') or date_elem.get_text().strip()
                if date_value:
                    metadata['publish_date'] = date_value
                    break
        
        return metadata

    def _extract_and_categorize_links(self, soup: BeautifulSoup, base_url: str) -> Tuple[List[str], List[str]]:
        """Extract and categorize internal and external links"""        base_domain = urlparse(base_url).netloc
        internal_links = []
        external_links = []
        
        for link in soup.find_all('a', href=True):
            href = link['href']
            absolute_url = urljoin(base_url, href)
            
            # Skip non-HTTP links
            if not absolute_url.startswith(('http://', 'https://')):
                continue
            
            link_domain = urlparse(absolute_url).netloc
            
            if link_domain == base_domain:
                internal_links.append(absolute_url)
            else:
                external_links.append(absolute_url)
        
        # Remove duplicates and limit
        internal_links = list(set(internal_links))[:100]
        external_links = list(set(external_links))[:50]
        
        return internal_links, external_links

    def _extract_images_with_metadata(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, str]]:
        """Extract images with comprehensive metadata"""        images = []
        
        for img in soup.find_all('img'):
            src = img.get('src')
            if not src:
                continue
            
            absolute_url = urljoin(base_url, src)
            
            image_data = {
                'url': absolute_url,
                'alt': img.get('alt', ''),
                'title': img.get('title', ''),
                'width': img.get('width', ''),
                'height': img.get('height', ''),
                'loading': img.get('loading', ''),
                'srcset': img.get('srcset', '')
            }
            
            images.append(image_data)
        
        return images[:50]  # Limit number of images

    def _extract_videos_with_metadata(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, str]]:
        """Extract videos with metadata"""        videos = []
        
        # Video tags
        for video in soup.find_all('video'):
            src = video.get('src')
            if src:
                videos.append({
                    'url': urljoin(base_url, src),
                    'type': 'video',
                    'controls': str(video.get('controls', '')),
                    'autoplay': str(video.get('autoplay', '')),
                    'muted': str(video.get('muted', ''))
                })
        
        # Embedded iframes (YouTube, Vimeo, etc.)
        for iframe in soup.find_all('iframe'):
            src = iframe.get('src')
            if src and any(domain in src for domain in ['youtube.com', 'vimeo.com', 'dailymotion.com']):
                videos.append({
                    'url': urljoin(base_url, src),
                    'type': 'embedded',
                    'width': iframe.get('width', ''),
                    'height': iframe.get('height', ''),
                    'title': iframe.get('title', '')
                })
        
        return videos[:20]  # Limit number of videos

    def _calculate_readability_score(self, content: str) -> float:
        """Calculate readability score using Flesch-Kincaid"""        if not content or len(content) < 100:
            return 0.0
        
        try:
            from textstat import flesch_kincaid_grade
            return max(0.0, min(100.0, 100.0 - flesch_kincaid_grade(content) * 10))
        except:
            # Simple fallback calculation
            sentences = len(re.split(r'[.!?]+', content))
            words = len(content.split())
            if sentences == 0 or words == 0:
                return 0.0
            
            avg_words_per_sentence = words / sentences
            avg_syllables_per_word = sum(self._count_syllables(word) for word in content.split()) / words
            
            # Simplified Flesch Reading Ease
            score = 206.835 - (1.015 * avg_words_per_sentence) - (84.6 * avg_syllables_per_word)
            return max(0.0, min(100.0, score))

    def _count_syllables(self, word: str) -> int:
        """Count syllables in a word"""        word = word.lower()
        count = 0
        vowels = "aeiouy"
        if word[0] in vowels:
            count += 1
        for index in range(1, len(word)):
            if word[index] in vowels and word[index - 1] not in vowels:
                count += 1
        if word.endswith("e"):
            count -= 1
        if count == 0:
            count += 1
        return count

    def _calculate_content_quality(self, soup: BeautifulSoup, content: str) -> float:
        """Calculate overall content quality score"""        score = 0.0
        
        # Content length factor (0-20 points)
        word_count = len(content.split())
        if word_count >= 300:
            score += 20
        elif word_count >= 150:
            score += 15
        elif word_count >= 50:
            score += 10
        
        # Structure quality (0-20 points)
        if soup.find('h1'):
            score += 5
        if soup.find_all(['h2', 'h3', 'h4', 'h5', 'h6']):
            score += 5
        if soup.find_all('p'):
            score += 5
        if soup.find_all(['ul', 'ol']):
            score += 5
        
        # Media content (0-15 points)
        if soup.find_all('img'):
            score += 10
        if soup.find_all(['video', 'iframe']):
            score += 5
        
        # Metadata quality (0-15 points)
        if soup.find('meta', attrs={'name': 'description'}):
            score += 5
        if soup.find('title') and len(soup.find('title').get_text().strip()) > 10:
            score += 5
        if soup.find('meta', attrs={'name': 'keywords'}):
            score += 5
        
        # Link quality (0-15 points)
        internal_links = len([a for a in soup.find_all('a', href=True) 
                             if not a['href'].startswith(('http://', 'https://')) or 
                             urlparse(a['href']).netloc == urlparse(soup.find('base', href=True)['href'] if soup.find('base', href=True) else '').netloc])
        external_links = len([a for a in soup.find_all('a', href=True) 
                             if a['href'].startswith(('http://', 'https://')) and 
                             urlparse(a['href']).netloc != urlparse(soup.find('base', href=True)['href'] if soup.find('base', href=True) else '').netloc])
        
        if internal_links > 0:
            score += 7
        if external_links > 0:
            score += 8
        
        # Content originality (0-15 points)
        unique_sentences = len(set(re.split(r'[.!?]+', content)))
        total_sentences = len(re.split(r'[.!?]+', content))
        if total_sentences > 0:
            originality = unique_sentences / total_sentences
            score += originality * 15
        
        return min(score, 100.0)

    def _calculate_seo_score(self, soup: BeautifulSoup, metadata: Dict) -> float:
        """Calculate SEO quality score"""        score = 0.0
        
        # Title optimization (0-25 points)
        title_elem = soup.find('title')
        if title_elem:
            title_text = title_elem.get_text().strip()
            title_length = len(title_text)
            if 30 <= title_length <= 60:
                score += 25
            elif 20 <= title_length <= 70:
                score += 20
            elif title_length > 0:
                score += 10
        
        # Meta description (0-25 points)
        if 'description' in metadata:
            desc_length = len(metadata['description'])
            if 120 <= desc_length <= 160:
                score += 25
            elif 100 <= desc_length <= 180:
                score += 20
            elif desc_length > 0:
                score += 10
        
        # Heading structure (0-20 points)
        h1_tags = soup.find_all('h1')
        if len(h1_tags) == 1:
            score += 10
        elif len(h1_tags) > 0:
            score += 5
        
        if soup.find_all(['h2', 'h3', 'h4']):
            score += 10
        
        # Image alt attributes (0-15 points)
        images = soup.find_all('img')
        images_with_alt = soup.find_all('img', alt=True)
        if images:
            alt_ratio = len(images_with_alt) / len(images)
            score += alt_ratio * 15
        
        # Internal linking (0-15 points)
        internal_links = len([a for a in soup.find_all('a', href=True) 
                             if not a['href'].startswith(('http://', 'https://', 'mailto:', 'tel:'))])
        if internal_links >= 3:
            score += 15
        elif internal_links > 0:
            score += 10
        
        return min(score, 100.0)

    def _detect_content_language(self, content: str) -> str:
        """Detect content language"""        if not content or len(content) < 50:
            return 'unknown'
        
        try:
            from langdetect import detect
            return detect(content)
        except:
            # Fallback to simple heuristics
            english_words = len(re.findall(r'\b(the|and|is|in|to|of|a|for|with|on|as|by|at|this|that)\b', 
                                         content.lower()))
            if english_words > 10:
                return 'en'
            return 'unknown'

    def _normalize_url(self, url: str) -> str:
        """Normalize URL for consistency"""        url = url.strip()
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        # Remove fragment and common tracking parameters
        parsed = urlparse(url)
        query_params = parse_qs(parsed.query)
        
        # Remove tracking parameters
        tracking_params = ['utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content',
                          'gclid', 'fbclid', 'msclkid', '_ga', 'ref', 'referrer']
        
        for param in tracking_params:
            query_params.pop(param, None)
        
        # Rebuild URL without fragment and tracking params
        clean_query = urlencode(query_params, doseq=True)
        clean_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        if clean_query:
            clean_url += f"?{clean_query}"
        
        return clean_url

    def _is_valid_url(self, url: str) -> bool:
        """Validate URL format and domain"""        try:
            parsed = urlparse(url)
            if not all([parsed.scheme, parsed.netloc]):
                return False
            
            # Check for blocked domains
            if self.config.block_malicious_domains:
                blocked_domains = [
                    'malware.com', 'phishing.com', 'spam.com'  # Add actual blocked domains
                ]
                if any(blocked in parsed.netloc.lower() for blocked in blocked_domains):
                    return False
            
            return True
        except:
            return False

    async def _check_robots_compliance(self, url: str) -> bool:
        """Check robots.txt compliance"""        if self.config.robots_policy == RobotsPolicyLevel.IGNORE:
            return True
        
        try:
            parsed_url = urlparse(url)
            domain = f"{parsed_url.scheme}://{parsed_url.netloc}"
            
            # Check cache first
            if domain in self.robots_cache:
                rp = self.robots_cache[domain]
            else:
                # Fetch and parse robots.txt
                robots_url = urljoin(domain, '/robots.txt')
                rp = RobotFileParser()
                rp.set_url(robots_url)
                
                try:
                    rp.read()
                    self.robots_cache[domain] = rp
                except:
                    # If robots.txt is inaccessible, allow crawling based on policy
                    if self.config.robots_policy == RobotsPolicyLevel.LENIENT:
                        return True
                    else:
                        return False
            
            # Check if crawling is allowed
            user_agent = self.user_agent_rotator.get_current_agent()
            can_fetch = rp.can_fetch(user_agent, url)
            
            if self.config.robots_policy == RobotsPolicyLevel.STRICT:
                return can_fetch
            elif self.config.robots_policy == RobotsPolicyLevel.MODERATE:
                # Allow if robots.txt doesn't explicitly disallow
                return can_fetch or not rp.disallow_all
            else:  # LENIENT
                return True
            
        except Exception as e:
            logger.warning(f"Robots.txt check failed for {url}: {str(e)}")
            return self.config.robots_policy != RobotsPolicyLevel.STRICT

    async def _apply_rate_limiting(self, url: str) -> None:
        """Apply rate limiting and respect crawl delays"""        domain = urlparse(url).netloc
        
        # Apply global rate limiting
        await self.rate_limiter.acquire()
        
        # Check domain-specific crawl delay
        if domain in self.domain_delays:
            delay = self.domain_delays[domain]
        else:
            # Check robots.txt for crawl delay
            delay = self.config.request_delay
            if self.config.respect_crawl_delay and domain in self.robots_cache:
                try:
                    robots_delay = self.robots_cache[domain].crawl_delay(
                        self.user_agent_rotator.get_current_agent()
                    )
                    if robots_delay:
                        delay = max(delay, robots_delay)
                except:
                    pass
            
            self.domain_delays[domain] = delay
        
        # Apply delay
        if delay > 0:
            await asyncio.sleep(delay)

    async def _post_process_result(self, result: CrawlResult) -> CrawlResult:
        """Post-process crawl result for quality and consistency"""        try:
            # Validate content length constraints
            if len(result.cleaned_content) < self.config.min_content_length:
                result.warnings.append(f"Content length ({len(result.cleaned_content)}) below minimum threshold")
            
            # Check for potential bot detection
            if "blocked" in result.title.lower() or "access denied" in result.content.lower():
                result.warnings.append("Potential bot detection or access restriction")
            
            # Validate required fields
            if not result.title and not result.cleaned_content:
                result.errors.append("No meaningful content extracted")
            
            return result
            
        except Exception as e:
            logger.error(f"Post-processing failed: {str(e)}")
            result.errors.append(f"Post-processing error: {str(e)}")
            return result

    async def crawl_multiple(self, urls: List[str], max_concurrent: int = None, **kwargs) -> List[CrawlResult]:
        """Crawl multiple URLs concurrently"""        max_concurrent = max_concurrent or self.config.max_concurrent_requests
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def crawl_with_semaphore(url):
            async with semaphore:
                return await self.crawl_url(url, **kwargs)
        
        tasks = [crawl_with_semaphore(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions and None results
        valid_results = []
        for result in results:
            if isinstance(result, CrawlResult):
                valid_results.append(result)
            elif isinstance(result, Exception):
                logger.error(f"Crawl task failed: {str(result)}")
        
        return valid_results

    async def crawl_sitemap(self, sitemap_url: str, **kwargs) -> List[CrawlResult]:
        """Crawl URLs from sitemap"""        try:
            # Fetch sitemap
            async with self.session.get(sitemap_url) as response:
                sitemap_content = await response.text()
            
            # Parse sitemap (simple XML parsing)
            urls = re.findall(r'<loc>(.*?)</loc>', sitemap_content)
            
            logger.info(f"Found {len(urls)} URLs in sitemap")
            
            # Crawl URLs from sitemap
            return await self.crawl_multiple(urls, **kwargs)
            
        except Exception as e:
            logger.error(f"Failed to crawl sitemap {sitemap_url}: {str(e)}")
            return []

    def get_statistics(self) -> Dict[str, Any]:
        """Get crawler statistics"""        return {
            **self.stats,
            'crawled_urls_count': len(self.crawled_urls),
            'failed_urls_count': len(self.failed_urls),
            'robots_cache_size': len(self.robots_cache),
            'domain_delays_count': len(self.domain_delays),
            'success_rate': (
                self.stats['successful_crawls'] / max(1, self.stats['requests_made'])
            ) * 100
        }

    async def cleanup(self) -> None:
        """Clean up resources and connections"""        if self.session:
            await self.session.close()
        
        if self.selenium_driver:
            self.selenium_driver.quit()
        
        if self.cache_manager:
            await self.cache_manager.cleanup()
        
        logger.info("Web Crawler cleanup complete")


class SiteMonitor:
    """    Advanced Site Monitoring for Content Changes and Updates
    
    Monitors websites for content changes, new publications, and structural updates.
    Provides diff analysis and change notifications.
    """    
    def __init__(self, crawler: WebCrawler):
        self.crawler = crawler
        self.monitored_sites: Dict[str, Dict] = {}
        self.change_history: List[Dict] = []
        self.monitoring_active = False
        
    async def add_site(self, url: str, check_interval_minutes: int = 60, 
                      change_threshold: float = 0.1) -> str:
        """Add site to monitoring list"""        site_id = hashlib.md5(url.encode()).hexdigest()[:12]
        
        # Initial crawl
        initial_result = await self.crawler.crawl_url(url)
        
        self.monitored_sites[site_id] = {
            'url': url,
            'site_id': site_id,
            'check_interval_minutes': check_interval_minutes,
            'change_threshold': change_threshold,
            'last_check': datetime.now(),
            'last_result': initial_result,
            'check_count': 1,
            'changes_detected': 0,
            'monitoring_since': datetime.now()
        }
        
        return site_id
    
    async def check_site_changes(self, site_id: str) -> Optional[Dict]:
        """Check specific site for changes"""        if site_id not in self.monitored_sites:
            return None
        
        site_info = self.monitored_sites[site_id]
        current_result = await self.crawler.crawl_url(site_info['url'])
        
        if not current_result:
            return None
        
        # Compare with last result
        changes = self._detect_changes(site_info['last_result'], current_result)
        
        # Update monitoring info
        site_info['last_check'] = datetime.now()
        site_info['last_result'] = current_result
        site_info['check_count'] += 1
        
        if changes['change_score'] > site_info['change_threshold']:
            site_info['changes_detected'] += 1
            
            # Record change
            change_record = {
                'site_id': site_id,
                'url': site_info['url'],
                'timestamp': datetime.now(),
                'changes': changes,
                'change_score': changes['change_score']
            }
            
            self.change_history.append(change_record)
            return change_record
        
        return None
    
    def _detect_changes(self, old_result: CrawlResult, new_result: CrawlResult) -> Dict:
        """Detect and analyze changes between crawl results"""        changes = {
            'content_changed': False,
            'title_changed': False,
            'structure_changed': False,
            'links_changed': False,
            'images_changed': False,
            'change_score': 0.0,
            'details': []
        }
        
        if not old_result or not new_result:
            return changes
        
        # Title changes
        if old_result.title != new_result.title:
            changes['title_changed'] = True
            changes['change_score'] += 0.2
            changes['details'].append(f"Title changed: '{old_result.title}' → '{new_result.title}'")
        
        # Content changes (using similarity)
        content_similarity = self._calculate_text_similarity(
            old_result.cleaned_content, new_result.cleaned_content
        )
        content_change_score = 1.0 - content_similarity
        
        if content_change_score > 0.1:  # 10% threshold
            changes['content_changed'] = True
            changes['change_score'] += content_change_score * 0.5
            changes['details'].append(f"Content similarity: {content_similarity:.2%}")
        
        # Structure changes (hash comparison)
        if old_result.structure_hash != new_result.structure_hash:
            changes['structure_changed'] = True
            changes['change_score'] += 0.3
            changes['details'].append("Page structure changed")
        
        # Link changes
        old_links = set(old_result.internal_links + old_result.external_links)
        new_links = set(new_result.internal_links + new_result.external_links)
        
        if old_links != new_links:
            changes['links_changed'] = True
            added_links = len(new_links - old_links)
            removed_links = len(old_links - new_links)
            changes['change_score'] += min(0.2, (added_links + removed_links) * 0.01)
            changes['details'].append(f"Links changed: +{added_links}, -{removed_links}")
        
        # Image changes
        old_images = {img['url'] for img in old_result.images}
        new_images = {img['url'] for img in new_result.images}
        
        if old_images != new_images:
            changes['images_changed'] = True
            added_images = len(new_images - old_images)
            removed_images = len(old_images - new_images)
            changes['change_score'] += min(0.1, (added_images + removed_images) * 0.005)
            changes['details'].append(f"Images changed: +{added_images}, -{removed_images}")
        
        return changes
    
    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Calculate text similarity using simple word overlap"""        if not text1 or not text2:
            return 0.0 if text1 != text2 else 1.0
        
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 and not words2:
            return 1.0
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0
    
    async def start_monitoring(self) -> None:
        """Start continuous monitoring of all sites"""        self.monitoring_active = True
        
        while self.monitoring_active:
            for site_id, site_info in self.monitored_sites.items():
                try:
                    # Check if it's time for next check
                    time_since_check = datetime.now() - site_info['last_check']
                    if time_since_check.total_seconds() >= site_info['check_interval_minutes'] * 60:
                        changes = await self.check_site_changes(site_id)
                        
                        if changes:
                            logger.info(f"Changes detected for {site_info['url']}: {changes['change_score']:.2%}")
                
                except Exception as e:
                    logger.error(f"Error monitoring site {site_id}: {str(e)}")
            
            await asyncio.sleep(60)  # Check every minute
    
    def stop_monitoring(self) -> None:
        """Stop continuous monitoring"""        self.monitoring_active = False
    
    def get_monitoring_report(self) -> Dict:
        """Get comprehensive monitoring report"""        return {
            'monitored_sites_count': len(self.monitored_sites),
            'total_checks': sum(site['check_count'] for site in self.monitored_sites.values()),
            'total_changes_detected': sum(site['changes_detected'] for site in self.monitored_sites.values()),
            'recent_changes': sorted(self.change_history[-10:], key=lambda x: x['timestamp'], reverse=True),
            'sites_summary': [
                {
                    'site_id': site_id,
                    'url': info['url'],
                    'checks': info['check_count'],
                    'changes': info['changes_detected'],
                    'last_check': info['last_check'].isoformat(),
                    'monitoring_duration': (datetime.now() - info['monitoring_since']).total_seconds() / 3600
                }
                for site_id, info in self.monitored_sites.items()
            ]
        }
