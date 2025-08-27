"""
Advanced Crawling Agent - Industrial Web Surveillance & Content Discovery System

Enterprise-grade web crawling engine with multi-platform monitoring, content detection,
and real-time surveillance capabilities for content protection and collaboration matching.

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
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
from urllib.parse import urljoin, urlparse, parse_qs
import re

import aiohttp
import aiofiles
from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.http import Request
import feedparser
import newspaper
from textblob import TextBlob
import cv2
import numpy as np
from PIL import Image
import imagehash

from ..base import BaseAgent, AgentRequest, AgentResponse, AgentMetrics
from ...core.config import settings
from ...core.database import get_db_session
from ...core.exceptions import CrawlingError, ValidationError, SecurityError
from ...security.content_fingerprint import ContentFingerprint
from ...ml.similarity_detector import SimilarityDetector
from ...monitoring.alert_system import AlertSystem
from ...utils.rate_limiter import RateLimiter
from ...utils.proxy_manager import ProxyManager
from ...utils.user_agent_rotator import UserAgentRotator

logger = logging.getLogger(__name__)

class CrawlingStrategy(Enum):
    """Web crawling execution strategies"""
    BREADTH_FIRST = "breadth_first"
    DEPTH_FIRST = "depth_first"
    FOCUSED = "focused"
    ADAPTIVE = "adaptive"
    STEALTH = "stealth"
    AGGRESSIVE = "aggressive"

class ContentType(Enum):
    """Monitored content types for crawling"""
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    DOCUMENT = "document"
    SOCIAL_POST = "social_post"
    PRODUCT = "product"
    NEWS = "news"

class PlatformType(Enum):
    """Supported platform types"""
    SOCIAL_MEDIA = "social_media"
    MUSIC_STREAMING = "music_streaming"
    VIDEO_PLATFORM = "video_platform"
    BLOG = "blog"
    NEWS_SITE = "news_site"
    MARKETPLACE = "marketplace"
    PORTFOLIO = "portfolio"
    GENERIC_WEB = "generic_web"

@dataclass
class CrawlingConfig:
    """Advanced crawling configuration"""
    max_depth: int = 3
    max_pages: int = 1000
    max_concurrent: int = 10
    delay_seconds: float = 1.0
    timeout_seconds: int = 30
    retries: int = 3
    strategy: CrawlingStrategy = CrawlingStrategy.ADAPTIVE
    respect_robots: bool = True
    use_proxy: bool = True
    stealth_mode: bool = False
    javascript_enabled: bool = True
    content_types: Set[ContentType] = field(default_factory=lambda: {ContentType.TEXT, ContentType.IMAGE})
    
@dataclass
class CrawledContent:
    """Comprehensive crawled content structure"""
    url: str
    title: str
    content: str
    content_type: ContentType
    platform_type: PlatformType
    metadata: Dict[str, Any]
    fingerprint: str
    timestamp: datetime
    source_domain: str
    language: str
    sentiment_score: float
    quality_score: float
    similarity_hash: str
    images: List[str] = field(default_factory=list)
    links: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    author: Optional[str] = None
    publish_date: Optional[datetime] = None
    view_count: Optional[int] = None
    engagement_metrics: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SurveillanceTarget:
    """Content surveillance target definition"""
    target_id: str
    user_id: str
    content_fingerprint: str
    search_keywords: List[str]
    platforms: List[str]
    monitoring_frequency: int  # hours
    alert_threshold: float
    active: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    last_scan: Optional[datetime] = None

class CrawlingAgent(BaseAgent):
    """
    Advanced Web Crawling Agent for Content Discovery & Surveillance
    
    Handles multi-platform crawling, content detection, similarity matching,
    and real-time monitoring for content protection and collaboration opportunities.
    """
    
    def __init__(self, config: Optional[Dict] = None):
        super().__init__("crawling_agent", config or {})
        
        # Core components initialization
        self.crawler_config = CrawlingConfig(**self.config.get('crawling', {}))
        self.rate_limiter = RateLimiter(max_requests=100, window_seconds=60)
        self.proxy_manager = ProxyManager()
        self.user_agent_rotator = UserAgentRotator()
        self.similarity_detector = SimilarityDetector()
        self.content_fingerprint = ContentFingerprint()
        self.alert_system = AlertSystem()
        
        # Crawler session and drivers
        self.session: Optional[aiohttp.ClientSession] = None
        self.selenium_driver: Optional[webdriver.Chrome] = None
        
        # Monitoring and surveillance
        self.surveillance_targets: Dict[str, SurveillanceTarget] = {}
        self.crawling_queue: asyncio.Queue = asyncio.Queue()
        self.results_cache: Dict[str, CrawledContent] = {}
        
        # Statistics and metrics
        self.crawl_stats = {
            'pages_crawled': 0,
            'content_discovered': 0,
            'duplicates_found': 0,
            'violations_detected': 0,
            'collaboration_matches': 0
        }
        
        logger.info("Advanced Crawling Agent initialized successfully")

    async def initialize(self) -> None:
        """Initialize crawling agent with all required components"""
        await super().initialize()
        
        try:
            # Initialize HTTP session with advanced configuration
            connector = aiohttp.TCPConnector(
                limit=self.crawler_config.max_concurrent,
                limit_per_host=5,
                ttl_dns_cache=300,
                use_dns_cache=True
            )
            
            self.session = aiohttp.ClientSession(
                connector=connector,
                timeout=aiohttp.ClientTimeout(total=self.crawler_config.timeout_seconds),
                headers={'User-Agent': self.user_agent_rotator.get_random_agent()}
            )
            
            # Initialize Selenium driver for JavaScript-heavy sites
            if self.crawler_config.javascript_enabled:
                await self._setup_selenium_driver()
            
            # Load surveillance targets from database
            await self._load_surveillance_targets()
            
            # Start background monitoring tasks
            asyncio.create_task(self._background_surveillance())
            asyncio.create_task(self._queue_processor())
            
            self.status = self.AgentStatus.ACTIVE
            logger.info("Crawling Agent fully initialized and active")
            
        except Exception as e:
            logger.error(f"Failed to initialize Crawling Agent: {str(e)}")
            raise CrawlingError(f"Initialization failed: {str(e)}")

    async def _setup_selenium_driver(self) -> None:
        """Setup Selenium WebDriver with stealth configuration"""
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        if self.crawler_config.stealth_mode:
            chrome_options.add_argument('--disable-extensions')
            chrome_options.add_argument('--disable-plugins')
            chrome_options.add_argument('--disable-images')
        
        self.selenium_driver = webdriver.Chrome(options=chrome_options)
        self.selenium_driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    async def process_request(self, request: AgentRequest) -> AgentResponse:
        """Process crawling requests with comprehensive error handling"""
        start_time = time.time()
        
        try:
            action = request.action.lower()
            
            if action == "crawl_website":
                result = await self._crawl_website(request.data)
            elif action == "monitor_content":
                result = await self._monitor_content(request.data)
            elif action == "search_similar":
                result = await self._search_similar_content(request.data)
            elif action == "platform_scan":
                result = await self._platform_scan(request.data)
            elif action == "surveillance_setup":
                result = await self._setup_surveillance(request.data)
            elif action == "bulk_crawl":
                result = await self._bulk_crawl(request.data)
            elif action == "real_time_monitor":
                result = await self._real_time_monitor(request.data)
            else:
                raise ValidationError(f"Unknown action: {action}")
            
            # Update metrics
            processing_time = time.time() - start_time
            self.metrics.total_requests += 1
            self.metrics.successful_requests += 1
            self.metrics.average_response_time = (
                (self.metrics.average_response_time * (self.metrics.total_requests - 1) + processing_time) /
                self.metrics.total_requests
            )
            
            return AgentResponse(
                success=True,
                data=result,
                message="Crawling request processed successfully",
                metadata={
                    'processing_time': processing_time,
                    'pages_processed': result.get('pages_processed', 0),
                    'content_found': result.get('content_found', 0)
                }
            )
            
        except Exception as e:
            self.metrics.failed_requests += 1
            logger.error(f"Crawling request failed: {str(e)}")
            
            return AgentResponse(
                success=False,
                error=str(e),
                message="Crawling request failed",
                metadata={'error_type': type(e).__name__}
            )

    async def _crawl_website(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Advanced website crawling with content extraction and analysis"""
        url = data.get('url')
        max_depth = data.get('max_depth', self.crawler_config.max_depth)
        content_types = data.get('content_types', ['text', 'image'])
        
        if not url:
            raise ValidationError("URL is required for website crawling")
        
        crawled_content: List[CrawledContent] = []
        visited_urls: Set[str] = set()
        url_queue = asyncio.Queue()
        await url_queue.put((url, 0))  # (url, depth)
        
        while not url_queue.empty() and len(crawled_content) < self.crawler_config.max_pages:
            current_url, depth = await url_queue.get()
            
            if current_url in visited_urls or depth > max_depth:
                continue
                
            visited_urls.add(current_url)
            
            try:
                # Rate limiting
                await self.rate_limiter.acquire()
                
                # Crawl the page
                content = await self._crawl_single_page(current_url, content_types)
                if content:
                    crawled_content.append(content)
                    
                    # Extract and queue new URLs if within depth limit
                    if depth < max_depth:
                        for link in content.links[:10]:  # Limit links per page
                            if link not in visited_urls:
                                await url_queue.put((link, depth + 1))
                
                # Delay between requests
                await asyncio.sleep(self.crawler_config.delay_seconds)
                
            except Exception as e:
                logger.warning(f"Failed to crawl {current_url}: {str(e)}")
                continue
        
        # Analyze crawled content for patterns and insights
        analysis_results = await self._analyze_crawled_content(crawled_content)
        
        return {
            'crawled_pages': len(crawled_content),
            'unique_urls': len(visited_urls),
            'content_discovered': len(crawled_content),
            'content_items': [self._serialize_crawled_content(item) for item in crawled_content],
            'analysis': analysis_results,
            'timestamp': datetime.now().isoformat()
        }

    async def _crawl_single_page(self, url: str, content_types: List[str]) -> Optional[CrawledContent]:
        """Crawl and extract content from a single web page"""
        try:
            headers = {
                'User-Agent': self.user_agent_rotator.get_random_agent(),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive'
            }
            
            # Use proxy if configured
            proxy = None
            if self.crawler_config.use_proxy:
                proxy = await self.proxy_manager.get_proxy()
            
            async with self.session.get(url, headers=headers, proxy=proxy) as response:
                if response.status != 200:
                    return None
                
                html_content = await response.text()
                content_type = response.headers.get('content-type', '').lower()
                
                # Parse HTML content
                soup = BeautifulSoup(html_content, 'html.parser')
                
                # Extract basic information
                title = soup.find('title')
                title_text = title.get_text().strip() if title else ""
                
                # Extract main content
                main_content = self._extract_main_content(soup)
                
                # Extract metadata
                metadata = self._extract_metadata(soup, response.headers)
                
                # Extract links
                links = self._extract_links(soup, url)
                
                # Extract images
                images = self._extract_images(soup, url) if 'image' in content_types else []
                
                # Determine platform type
                platform_type = self._detect_platform_type(url, soup)
                
                # Generate content fingerprint
                fingerprint = self.content_fingerprint.generate(main_content + title_text)
                
                # Calculate similarity hash
                similarity_hash = hashlib.md5(main_content.encode()).hexdigest()
                
                # Analyze content sentiment and quality
                sentiment_score = self._analyze_sentiment(main_content)
                quality_score = self._calculate_quality_score(soup, main_content)
                
                # Detect language
                language = self._detect_language(main_content)
                
                return CrawledContent(
                    url=url,
                    title=title_text,
                    content=main_content,
                    content_type=ContentType.TEXT,
                    platform_type=platform_type,
                    metadata=metadata,
                    fingerprint=fingerprint,
                    timestamp=datetime.now(),
                    source_domain=urlparse(url).netloc,
                    language=language,
                    sentiment_score=sentiment_score,
                    quality_score=quality_score,
                    similarity_hash=similarity_hash,
                    images=images,
                    links=links[:50],  # Limit links
                    tags=self._extract_tags(soup)
                )
                
        except Exception as e:
            logger.error(f"Error crawling page {url}: {str(e)}")
            return None

    def _extract_main_content(self, soup: BeautifulSoup) -> str:
        """Extract main content from HTML using advanced heuristics"""
        # Remove unwanted elements
        for element in soup(['script', 'style', 'nav', 'footer', 'header', 'sidebar']):
            element.decompose()
        
        # Try common content containers
        content_selectors = [
            'main', 'article', '.content', '#content', '.post', '.entry',
            '.article-body', '.story-body', '.post-content', '.entry-content'
        ]
        
        for selector in content_selectors:
            content_elem = soup.select_one(selector)
            if content_elem:
                return content_elem.get_text(strip=True, separator=' ')
        
        # Fallback to body content
        body = soup.find('body')
        if body:
            return body.get_text(strip=True, separator=' ')
        
        return soup.get_text(strip=True, separator=' ')

    def _extract_metadata(self, soup: BeautifulSoup, headers: Dict) -> Dict[str, Any]:
        """Extract comprehensive metadata from page"""
        metadata = {}
        
        # Meta tags
        for meta in soup.find_all('meta'):
            name = meta.get('name') or meta.get('property') or meta.get('http-equiv')
            content = meta.get('content')
            if name and content:
                metadata[name] = content
        
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
        
        # Response headers
        metadata['headers'] = dict(headers)
        
        return metadata

    def _extract_links(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """Extract and normalize all links from page"""
        links = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            absolute_url = urljoin(base_url, href)
            if self._is_valid_url(absolute_url):
                links.append(absolute_url)
        return list(set(links))  # Remove duplicates

    def _extract_images(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """Extract and normalize image URLs"""
        images = []
        for img in soup.find_all('img', src=True):
            src = img['src']
            absolute_url = urljoin(base_url, src)
            if self._is_valid_url(absolute_url):
                images.append(absolute_url)
        return list(set(images))

    def _extract_tags(self, soup: BeautifulSoup) -> List[str]:
        """Extract content tags and keywords"""
        tags = []
        
        # Meta keywords
        keywords_meta = soup.find('meta', attrs={'name': 'keywords'})
        if keywords_meta and keywords_meta.get('content'):
            tags.extend([tag.strip() for tag in keywords_meta['content'].split(',')])
        
        # Hash tags from content
        text_content = soup.get_text()
        hashtags = re.findall(r'#\w+', text_content)
        tags.extend([tag[1:] for tag in hashtags])  # Remove # symbol
        
        return list(set(tags))[:20]  # Limit and deduplicate

    def _detect_platform_type(self, url: str, soup: BeautifulSoup) -> PlatformType:
        """Detect platform type based on URL and content analysis"""
        domain = urlparse(url).netloc.lower()
        
        # Social media platforms
        social_domains = ['twitter.com', 'facebook.com', 'instagram.com', 'linkedin.com', 
                         'tiktok.com', 'youtube.com', 'reddit.com']
        if any(domain in url for domain in social_domains):
            return PlatformType.SOCIAL_MEDIA
        
        # Music streaming platforms
        music_domains = ['spotify.com', 'soundcloud.com', 'bandcamp.com', 'apple.com/music']
        if any(domain in url for domain in music_domains):
            return PlatformType.MUSIC_STREAMING
        
        # Video platforms
        video_domains = ['youtube.com', 'vimeo.com', 'dailymotion.com', 'twitch.tv']
        if any(domain in url for domain in video_domains):
            return PlatformType.VIDEO_PLATFORM
        
        # Blog detection
        blog_indicators = ['blog', 'wordpress', 'blogspot', 'medium.com']
        if any(indicator in domain for indicator in blog_indicators):
            return PlatformType.BLOG
        
        # News sites
        news_indicators = ['news', 'times', 'post', 'guardian', 'bbc', 'cnn']
        if any(indicator in domain for indicator in news_indicators):
            return PlatformType.NEWS_SITE
        
        return PlatformType.GENERIC_WEB

    def _analyze_sentiment(self, text: str) -> float:
        """Analyze content sentiment using TextBlob"""
        try:
            blob = TextBlob(text)
            return blob.sentiment.polarity
        except:
            return 0.0

    def _calculate_quality_score(self, soup: BeautifulSoup, content: str) -> float:
        """Calculate content quality score based on various factors"""
        score = 0.0
        
        # Content length factor
        if len(content) > 500:
            score += 0.3
        elif len(content) > 200:
            score += 0.2
        
        # HTML structure quality
        if soup.find('title'):
            score += 0.1
        if soup.find('meta', attrs={'name': 'description'}):
            score += 0.1
        
        # Image presence
        if soup.find_all('img'):
            score += 0.1
        
        # Link diversity
        links = soup.find_all('a', href=True)
        if len(links) > 5:
            score += 0.1
        
        # Headings structure
        headings = soup.find_all(['h1', 'h2', 'h3'])
        if headings:
            score += 0.1
        
        # Text-to-HTML ratio
        html_length = len(str(soup))
        text_length = len(content)
        if html_length > 0:
            ratio = text_length / html_length
            if ratio > 0.3:
                score += 0.1
        
        return min(score, 1.0)

    def _detect_language(self, text: str) -> str:
        """Detect content language"""
        try:
            blob = TextBlob(text)
            return blob.detect_language()
        except:
            return 'en'  # Default to English

    def _is_valid_url(self, url: str) -> bool:
        """Validate URL format and accessibility"""
        try:
            parsed = urlparse(url)
            return bool(parsed.scheme and parsed.netloc)
        except:
            return False

    async def _monitor_content(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Monitor specific content across platforms for violations or mentions"""
        content_fingerprint = data.get('content_fingerprint')
        search_keywords = data.get('keywords', [])
        platforms = data.get('platforms', [])
        
        if not content_fingerprint and not search_keywords:
            raise ValidationError("Either content fingerprint or search keywords required")
        
        monitoring_results = []
        
        for platform in platforms:
            try:
                platform_results = await self._monitor_platform(
                    platform, content_fingerprint, search_keywords
                )
                monitoring_results.extend(platform_results)
            except Exception as e:
                logger.error(f"Failed to monitor platform {platform}: {str(e)}")
        
        # Analyze results for potential violations
        violations = await self._analyze_monitoring_results(monitoring_results, content_fingerprint)
        
        return {
            'monitoring_results': monitoring_results,
            'potential_violations': violations,
            'platforms_monitored': len(platforms),
            'matches_found': len(monitoring_results),
            'timestamp': datetime.now().isoformat()
        }

    async def _monitor_platform(self, platform: str, fingerprint: str, keywords: List[str]) -> List[Dict]:
        """Monitor specific platform for content matches"""
        results = []
        
        # Platform-specific monitoring logic
        if platform.lower() == 'twitter':
            results.extend(await self._monitor_twitter(keywords))
        elif platform.lower() == 'instagram':
            results.extend(await self._monitor_instagram(keywords))
        elif platform.lower() == 'youtube':
            results.extend(await self._monitor_youtube(keywords))
        elif platform.lower() == 'generic':
            results.extend(await self._monitor_generic_web(keywords))
        
        return results

    async def _monitor_twitter(self, keywords: List[str]) -> List[Dict]:
        """Monitor Twitter for keyword matches"""
        results = []
        # Implementation would use Twitter API v2
        # This is a placeholder for the actual implementation
        return results

    async def _monitor_instagram(self, keywords: List[str]) -> List[Dict]:
        """Monitor Instagram for content matches"""
        results = []
        # Implementation would use Instagram API or web scraping
        return results

    async def _monitor_youtube(self, keywords: List[str]) -> List[Dict]:
        """Monitor YouTube for content matches"""
        results = []
        # Implementation would use YouTube Data API
        return results

    async def _monitor_generic_web(self, keywords: List[str]) -> List[Dict]:
        """Monitor generic web for keyword matches"""
        results = []
        
        # Use search engines to find content
        search_queries = [' '.join(keywords[i:i+3]) for i in range(0, len(keywords), 3)]
        
        for query in search_queries:
            try:
                # Simulate search engine results
                search_results = await self._search_engine_query(query)
                results.extend(search_results)
            except Exception as e:
                logger.error(f"Search query failed for: {query}, error: {str(e)}")
        
        return results

    async def _search_engine_query(self, query: str) -> List[Dict]:
        """Perform search engine query for content discovery"""
        results = []
        
        # This would integrate with search APIs (Google Custom Search, Bing, etc.)
        # Placeholder implementation
        search_url = f"https://www.google.com/search?q={query}"
        
        try:
            if self.selenium_driver:
                self.selenium_driver.get(search_url)
                # Wait for results to load
                WebDriverWait(self.selenium_driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "g"))
                )
                
                # Extract search results
                result_elements = self.selenium_driver.find_elements(By.CLASS_NAME, "g")
                
                for element in result_elements[:10]:  # Top 10 results
                    try:
                        title_elem = element.find_element(By.TAG_NAME, "h3")
                        link_elem = element.find_element(By.TAG_NAME, "a")
                        
                        results.append({
                            'title': title_elem.text,
                            'url': link_elem.get_attribute('href'),
                            'snippet': element.text,
                            'timestamp': datetime.now().isoformat()
                        })
                    except:
                        continue
                        
        except Exception as e:
            logger.error(f"Search engine query failed: {str(e)}")
        
        return results

    async def _analyze_monitoring_results(self, results: List[Dict], fingerprint: str) -> List[Dict]:
        """Analyze monitoring results for potential content violations"""
        violations = []
        
        for result in results:
            try:
                # Calculate similarity if fingerprint provided
                similarity_score = 0.0
                if fingerprint and 'content' in result:
                    similarity_score = await self.similarity_detector.calculate_similarity(
                        fingerprint, result['content']
                    )
                
                # Check for violation threshold
                if similarity_score > 0.8:  # 80% similarity threshold
                    violations.append({
                        'url': result.get('url'),
                        'title': result.get('title'),
                        'similarity_score': similarity_score,
                        'violation_type': 'high_similarity',
                        'detected_at': datetime.now().isoformat(),
                        'risk_level': 'high' if similarity_score > 0.9 else 'medium'
                    })
                    
            except Exception as e:
                logger.error(f"Error analyzing result: {str(e)}")
        
        return violations

    async def _search_similar_content(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Search for similar content across platforms"""
        reference_content = data.get('content')
        content_type = data.get('content_type', 'text')
        search_platforms = data.get('platforms', ['generic'])
        similarity_threshold = data.get('threshold', 0.7)
        
        if not reference_content:
            raise ValidationError("Reference content is required")
        
        # Generate fingerprint for reference content
        reference_fingerprint = self.content_fingerprint.generate(reference_content)
        
        similar_content = []
        
        for platform in search_platforms:
            try:
                platform_results = await self._platform_similarity_search(
                    platform, reference_content, reference_fingerprint, similarity_threshold
                )
                similar_content.extend(platform_results)
            except Exception as e:
                logger.error(f"Similarity search failed for platform {platform}: {str(e)}")
        
        # Sort by similarity score
        similar_content.sort(key=lambda x: x.get('similarity_score', 0), reverse=True)
        
        return {
            'reference_fingerprint': reference_fingerprint,
            'similar_content': similar_content,
            'total_matches': len(similar_content),
            'high_similarity_matches': len([c for c in similar_content if c.get('similarity_score', 0) > 0.9]),
            'platforms_searched': len(search_platforms),
            'search_timestamp': datetime.now().isoformat()
        }

    async def _platform_similarity_search(self, platform: str, content: str, 
                                        fingerprint: str, threshold: float) -> List[Dict]:
        """Search for similar content on specific platform"""
        results = []
        
        # Extract key phrases for search
        key_phrases = self._extract_key_phrases(content)
        
        # Search platform for these phrases
        for phrase in key_phrases[:5]:  # Top 5 phrases
            try:
                search_results = await self._platform_search(platform, phrase)
                
                for result in search_results:
                    # Calculate similarity
                    result_fingerprint = self.content_fingerprint.generate(
                        result.get('content', '')
                    )
                    
                    similarity = await self.similarity_detector.calculate_similarity(
                        fingerprint, result_fingerprint
                    )
                    
                    if similarity >= threshold:
                        result['similarity_score'] = similarity
                        result['matching_phrase'] = phrase
                        results.append(result)
                        
            except Exception as e:
                logger.error(f"Platform search failed for phrase '{phrase}': {str(e)}")
        
        return results

    def _extract_key_phrases(self, content: str) -> List[str]:
        """Extract key phrases from content for search"""
        # Simple implementation - can be enhanced with NLP
        sentences = content.split('.')[:10]  # First 10 sentences
        phrases = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 20 and len(sentence) < 100:
                phrases.append(sentence)
        
        return phrases

    async def _platform_search(self, platform: str, query: str) -> List[Dict]:
        """Search specific platform for content"""
        results = []
        
        if platform == 'generic':
            results = await self._search_engine_query(query)
        # Add other platform-specific search implementations
        
        return results

    async def _platform_scan(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Comprehensive platform scanning for content discovery"""
        platforms = data.get('platforms', [])
        scan_type = data.get('scan_type', 'content_discovery')
        filters = data.get('filters', {})
        
        scan_results = {}
        
        for platform in platforms:
            try:
                platform_data = await self._scan_single_platform(platform, scan_type, filters)
                scan_results[platform] = platform_data
            except Exception as e:
                logger.error(f"Platform scan failed for {platform}: {str(e)}")
                scan_results[platform] = {'error': str(e), 'results': []}
        
        return {
            'scan_results': scan_results,
            'platforms_scanned': len(platforms),
            'total_content_found': sum(len(r.get('results', [])) for r in scan_results.values()),
            'scan_timestamp': datetime.now().isoformat()
        }

    async def _scan_single_platform(self, platform: str, scan_type: str, filters: Dict) -> Dict:
        """Scan single platform for content"""
        results = []
        
        # Platform-specific scanning logic
        if platform.lower() == 'youtube':
            results = await self._scan_youtube(scan_type, filters)
        elif platform.lower() == 'instagram':
            results = await self._scan_instagram(scan_type, filters)
        elif platform.lower() == 'twitter':
            results = await self._scan_twitter(scan_type, filters)
        
        return {
            'platform': platform,
            'scan_type': scan_type,
            'results': results,
            'count': len(results)
        }

    async def _scan_youtube(self, scan_type: str, filters: Dict) -> List[Dict]:
        """Scan YouTube for content based on filters"""
        results = []
        # Implementation would use YouTube Data API
        return results

    async def _scan_instagram(self, scan_type: str, filters: Dict) -> List[Dict]:
        """Scan Instagram for content based on filters"""
        results = []
        # Implementation would use Instagram API or web scraping
        return results

    async def _scan_twitter(self, scan_type: str, filters: Dict) -> List[Dict]:
        """Scan Twitter for content based on filters"""
        results = []
        # Implementation would use Twitter API v2
        return results

    async def _setup_surveillance(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Setup automated surveillance for content protection"""
        user_id = data.get('user_id')
        content_fingerprint = data.get('content_fingerprint')
        keywords = data.get('keywords', [])
        platforms = data.get('platforms', [])
        frequency = data.get('frequency_hours', 24)
        alert_threshold = data.get('alert_threshold', 0.8)
        
        if not user_id or not content_fingerprint:
            raise ValidationError("User ID and content fingerprint are required")
        
        # Create surveillance target
        target_id = str(uuid.uuid4())
        surveillance_target = SurveillanceTarget(
            target_id=target_id,
            user_id=user_id,
            content_fingerprint=content_fingerprint,
            search_keywords=keywords,
            platforms=platforms,
            monitoring_frequency=frequency,
            alert_threshold=alert_threshold
        )
        
        # Store in memory and database
        self.surveillance_targets[target_id] = surveillance_target
        await self._save_surveillance_target(surveillance_target)
        
        return {
            'target_id': target_id,
            'surveillance_active': True,
            'monitoring_frequency': frequency,
            'platforms': platforms,
            'setup_timestamp': datetime.now().isoformat()
        }

    async def _bulk_crawl(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform bulk crawling operation across multiple URLs"""
        urls = data.get('urls', [])
        max_concurrent = data.get('max_concurrent', self.crawler_config.max_concurrent)
        content_types = data.get('content_types', ['text'])
        
        if not urls:
            raise ValidationError("URLs list is required for bulk crawling")
        
        # Process URLs in batches
        batch_size = min(max_concurrent, len(urls))
        batches = [urls[i:i + batch_size] for i in range(0, len(urls), batch_size)]
        
        all_results = []
        
        for batch in batches:
            batch_tasks = [
                self._crawl_single_page(url, content_types) for url in batch
            ]
            
            batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
            
            for result in batch_results:
                if isinstance(result, CrawledContent):
                    all_results.append(result)
        
        # Analyze bulk results
        analysis = await self._analyze_crawled_content(all_results)
        
        return {
            'urls_processed': len(urls),
            'successful_crawls': len(all_results),
            'failed_crawls': len(urls) - len(all_results),
            'content_items': [self._serialize_crawled_content(item) for item in all_results],
            'analysis': analysis,
            'processing_timestamp': datetime.now().isoformat()
        }

    async def _real_time_monitor(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Setup real-time monitoring for immediate alerts"""
        monitoring_config = data.get('config', {})
        duration_seconds = data.get('duration', 3600)  # 1 hour default
        
        # Start real-time monitoring task
        monitoring_task = asyncio.create_task(
            self._execute_real_time_monitoring(monitoring_config, duration_seconds)
        )
        
        return {
            'monitoring_active': True,
            'duration_seconds': duration_seconds,
            'config': monitoring_config,
            'task_id': id(monitoring_task),
            'start_timestamp': datetime.now().isoformat()
        }

    async def _execute_real_time_monitoring(self, config: Dict, duration: int) -> None:
        """Execute real-time monitoring for specified duration"""
        end_time = datetime.now() + timedelta(seconds=duration)
        
        while datetime.now() < end_time:
            try:
                # Perform monitoring cycle
                results = await self._monitoring_cycle(config)
                
                # Process results and send alerts if needed
                await self._process_monitoring_results(results)
                
                # Wait before next cycle
                await asyncio.sleep(config.get('cycle_interval', 60))
                
            except Exception as e:
                logger.error(f"Real-time monitoring cycle failed: {str(e)}")
                await asyncio.sleep(30)  # Brief pause before retry

    async def _monitoring_cycle(self, config: Dict) -> List[Dict]:
        """Perform single monitoring cycle"""
        results = []
        
        # Check each surveillance target
        for target in self.surveillance_targets.values():
            if target.active:
                try:
                    target_results = await self._check_surveillance_target(target)
                    results.extend(target_results)
                except Exception as e:
                    logger.error(f"Surveillance check failed for target {target.target_id}: {str(e)}")
        
        return results

    async def _check_surveillance_target(self, target: SurveillanceTarget) -> List[Dict]:
        """Check specific surveillance target for matches"""
        results = []
        
        # Check if enough time has passed since last scan
        if target.last_scan:
            hours_since_scan = (datetime.now() - target.last_scan).total_seconds() / 3600
            if hours_since_scan < target.monitoring_frequency:
                return results
        
        # Perform surveillance scan
        for platform in target.platforms:
            try:
                platform_results = await self._monitor_platform(
                    platform, target.content_fingerprint, target.search_keywords
                )
                
                # Filter results by alert threshold
                filtered_results = [
                    r for r in platform_results 
                    if r.get('similarity_score', 0) >= target.alert_threshold
                ]
                
                results.extend(filtered_results)
                
            except Exception as e:
                logger.error(f"Platform monitoring failed for {platform}: {str(e)}")
        
        # Update last scan time
        target.last_scan = datetime.now()
        await self._update_surveillance_target(target)
        
        return results

    async def _process_monitoring_results(self, results: List[Dict]) -> None:
        """Process monitoring results and trigger alerts"""
        for result in results:
            try:
                # Determine alert level
                similarity_score = result.get('similarity_score', 0)
                alert_level = 'high' if similarity_score > 0.9 else 'medium'
                
                # Send alert
                await self.alert_system.send_alert({
                    'type': 'content_violation_detected',
                    'level': alert_level,
                    'data': result,
                    'timestamp': datetime.now().isoformat()
                })
                
            except Exception as e:
                logger.error(f"Failed to process monitoring result: {str(e)}")

    async def _analyze_crawled_content(self, content_items: List[CrawledContent]) -> Dict[str, Any]:
        """Analyze crawled content for patterns and insights"""
        if not content_items:
            return {}
        
        analysis = {
            'content_stats': {
                'total_items': len(content_items),
                'unique_domains': len(set(item.source_domain for item in content_items)),
                'languages': list(set(item.language for item in content_items)),
                'average_quality_score': sum(item.quality_score for item in content_items) / len(content_items)
            },
            'platform_distribution': {},
            'content_type_distribution': {},
            'sentiment_analysis': {
                'average_sentiment': sum(item.sentiment_score for item in content_items) / len(content_items),
                'positive_content': len([i for i in content_items if i.sentiment_score > 0.1]),
                'negative_content': len([i for i in content_items if i.sentiment_score < -0.1]),
                'neutral_content': len([i for i in content_items if -0.1 <= i.sentiment_score <= 0.1])
            },
            'quality_distribution': {
                'high_quality': len([i for i in content_items if i.quality_score > 0.7]),
                'medium_quality': len([i for i in content_items if 0.3 <= i.quality_score <= 0.7]),
                'low_quality': len([i for i in content_items if i.quality_score < 0.3])
            }
        }
        
        # Platform distribution
        for item in content_items:
            platform = item.platform_type.value
            analysis['platform_distribution'][platform] = analysis['platform_distribution'].get(platform, 0) + 1
        
        # Content type distribution
        for item in content_items:
            content_type = item.content_type.value
            analysis['content_type_distribution'][content_type] = analysis['content_type_distribution'].get(content_type, 0) + 1
        
        return analysis

    def _serialize_crawled_content(self, content: CrawledContent) -> Dict[str, Any]:
        """Serialize CrawledContent object to dictionary"""
        return {
            'url': content.url,
            'title': content.title,
            'content': content.content[:1000],  # Truncate for response size
            'content_type': content.content_type.value,
            'platform_type': content.platform_type.value,
            'metadata': content.metadata,
            'fingerprint': content.fingerprint,
            'timestamp': content.timestamp.isoformat(),
            'source_domain': content.source_domain,
            'language': content.language,
            'sentiment_score': content.sentiment_score,
            'quality_score': content.quality_score,
            'similarity_hash': content.similarity_hash,
            'image_count': len(content.images),
            'link_count': len(content.links),
            'tag_count': len(content.tags),
            'author': content.author,
            'publish_date': content.publish_date.isoformat() if content.publish_date else None
        }

    async def _load_surveillance_targets(self) -> None:
        """Load surveillance targets from database"""
        try:
            # Implementation would load from database
            # This is a placeholder
            pass
        except Exception as e:
            logger.error(f"Failed to load surveillance targets: {str(e)}")

    async def _save_surveillance_target(self, target: SurveillanceTarget) -> None:
        """Save surveillance target to database"""
        try:
            # Implementation would save to database
            # This is a placeholder
            pass
        except Exception as e:
            logger.error(f"Failed to save surveillance target: {str(e)}")

    async def _update_surveillance_target(self, target: SurveillanceTarget) -> None:
        """Update surveillance target in database"""
        try:
            # Implementation would update database record
            pass
        except Exception as e:
            logger.error(f"Failed to update surveillance target: {str(e)}")

    async def _background_surveillance(self) -> None:
        """Background task for continuous surveillance"""
        while True:
            try:
                if self.surveillance_targets:
                    results = await self._monitoring_cycle({})
                    await self._process_monitoring_results(results)
                
                await asyncio.sleep(300)  # 5-minute intervals
                
            except Exception as e:
                logger.error(f"Background surveillance error: {str(e)}")
                await asyncio.sleep(60)

    async def _queue_processor(self) -> None:
        """Process crawling queue in background"""
        while True:
            try:
                # Process queued crawling requests
                if not self.crawling_queue.empty():
                    request = await self.crawling_queue.get()
                    await self._process_queued_request(request)
                else:
                    await asyncio.sleep(1)
                    
            except Exception as e:
                logger.error(f"Queue processor error: {str(e)}")
                await asyncio.sleep(5)

    async def _process_queued_request(self, request: Dict) -> None:
        """Process queued crawling request"""
        try:
            # Process based on request type
            request_type = request.get('type')
            
            if request_type == 'crawl_url':
                await self._crawl_single_page(request['url'], request.get('content_types', ['text']))
            elif request_type == 'monitor_target':
                target = self.surveillance_targets.get(request['target_id'])
                if target:
                    await self._check_surveillance_target(target)
                    
        except Exception as e:
            logger.error(f"Failed to process queued request: {str(e)}")

    async def shutdown(self) -> None:
        """Gracefully shutdown crawling agent"""
        logger.info("Shutting down Crawling Agent...")
        
        # Close HTTP session
        if self.session:
            await self.session.close()
        
        # Close Selenium driver
        if self.selenium_driver:
            self.selenium_driver.quit()
        
        # Save surveillance targets
        for target in self.surveillance_targets.values():
            await self._save_surveillance_target(target)
        
        await super().shutdown()
        logger.info("Crawling Agent shutdown complete")


class CrawlingAgentManager:
    """
    Manager class for coordinating multiple crawling agents and operations
    """
    
    def __init__(self):
        self.agents: Dict[str, CrawlingAgent] = {}
        self.load_balancer = LoadBalancer()
        self.task_scheduler = TaskScheduler()
        
    async def create_agent(self, agent_id: str, config: Dict) -> CrawlingAgent:
        """Create and initialize new crawling agent"""
        agent = CrawlingAgent(config)
        await agent.initialize()
        self.agents[agent_id] = agent
        return agent
    
    async def get_agent(self, agent_id: str) -> Optional[CrawlingAgent]:
        """Get existing crawling agent"""
        return self.agents.get(agent_id)
    
    async def distribute_request(self, request: AgentRequest) -> AgentResponse:
        """Distribute request to best available agent"""
        agent = await self.load_balancer.select_agent(self.agents.values())
        if agent:
            return await agent.process_request(request)
        else:
            raise CrawlingError("No available agents to process request")
    
    async def shutdown_all(self) -> None:
        """Shutdown all managed agents"""
        for agent in self.agents.values():
            await agent.shutdown()
        self.agents.clear()


class LoadBalancer:
    """Simple load balancer for crawling agents"""
    
    async def select_agent(self, agents) -> Optional[CrawlingAgent]:
        """Select best agent based on current load"""
        available_agents = [agent for agent in agents if agent.status == BaseAgent.AgentStatus.ACTIVE]
        
        if not available_agents:
            return None
        
        # Select agent with lowest request count
        return min(available_agents, key=lambda a: a.metrics.total_requests)


class TaskScheduler:
    """Task scheduler for crawling operations"""
    
    def __init__(self):
        self.scheduled_tasks: Dict[str, Dict] = {}
    
    async def schedule_task(self, task_id: str, task_config: Dict) -> None:
        """Schedule recurring crawling task"""
        self.scheduled_tasks[task_id] = task_config
    
    async def cancel_task(self, task_id: str) -> None:
        """Cancel scheduled task"""
        self.scheduled_tasks.pop(task_id, None)
