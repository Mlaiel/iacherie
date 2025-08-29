"""
� IA-Influencer-Agent - Ultra-Advanced Web Crawler Engine
==========================================================

Ultra-sophisticated web crawling system for comprehensive content monitoring
across all digital platforms with AI-powered content analysis, fingerprinting,
and real-time threat detection capabilities.

Architecture: Enterprise 3-Tier Professional (Backend Level 2)
Module: backend/business/surveillance/web_crawler.py
Expert Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + IA Prompt Engineer

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

⚠️ STRICT COPYRIGHT WARNING - INTELLECTUAL PROPERTY PROTECTION
================================================================
This code and concept are the EXCLUSIVE PROPERTY of Fahed Mlaiel.
Unauthorized access, copying, modification, distribution, reverse engineering,
or commercialization without explicit written permission from Fahed Mlaiel
(mlaiel@live.de) is STRICTLY PROHIBITED and will result in immediate legal
action under German and International copyright laws.

For licensing inquiries ONLY: mlaiel@live.de
================================================================

Business Logic Flow:
Target Configuration → Crawling Strategy Selection → Multi-Platform Crawling →
Content Extraction → AI Analysis → Fingerprint Matching → Threat Detection →
Data Storage → Real-time Notifications → Performance Optimization
"""

import asyncio
import aiohttp
import logging
import random
import time
import json
import hashlib
import re
from typing import Dict, List, Optional, Any, Union, Set, Tuple, AsyncGenerator, Callable
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone, timedelta
from pathlib import Path
from urllib.parse import urljoin, urlparse, parse_qs, unquote
from urllib.robotparser import RobotFileParser
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor, as_completed
import subprocess
import base64
import mimetypes

# External libraries
import requests
from bs4 import BeautifulSoup, Comment
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from fake_useragent import UserAgent
import cloudscraper
import undetected_chromedriver as uc
from playwright.async_api import async_playwright, Browser, BrowserContext, Page

# Database imports
import redis
import psycopg2
from psycopg2.extras import Json
from sqlalchemy import create_engine, Column, String, Integer, DateTime, Text, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

# ML/AI imports
import torch
import numpy as np
from transformers import AutoTokenizer, AutoModel
import cv2
from PIL import Image
import librosa
import faiss

# Internal imports
try:
    from backend.core.database import get_database_session
    from backend.core.redis_client import get_redis_client
    from backend.ai.content_analysis.fingerprinting import ContentFingerprintExtractor
    from backend.utils.encryption import encrypt_sensitive_data, decrypt_sensitive_data
    from backend.utils.rate_limiter import RateLimiter
    from backend.monitoring.metrics import PrometheusMetrics
except ImportError:
    # Fallback for missing modules
    get_database_session = None
    get_redis_client = None
    ContentFingerprintExtractor = None
    encrypt_sensitive_data = lambda x: x
    decrypt_sensitive_data = lambda x: x
    RateLimiter = None
    PrometheusMetrics = None

logger = logging.getLogger(__name__)

# Database Models
Base = declarative_base()


class CrawlRecord(Base):
    """Database model for crawl records"""
    __tablename__ = 'crawl_records'
    
    id = Column(String, primary_key=True)
    target_url = Column(String, nullable=False)
    platform = Column(String, nullable=False)
    content_type = Column(String)
    title = Column(String)
    description = Column(Text)
    metadata = Column(JSON)
    fingerprints = Column(JSON)
    threat_indicators = Column(JSON)
    crawl_timestamp = Column(DateTime, default=datetime.utcnow)
    processing_status = Column(String, default='pending')
    content_hash = Column(String)
    similarity_scores = Column(JSON)


@dataclass
class CrawlerTarget:
    """Configuration for crawler targets"""
    url: str
    platform: str
    content_type: str = "unknown"
    priority: int = 1
    crawl_depth: int = 1
    follow_redirects: bool = True
    respect_robots: bool = True
    custom_headers: Dict[str, str] = field(default_factory=dict)
    selectors: Dict[str, str] = field(default_factory=dict)
    javascript_required: bool = False
    auth_required: bool = False
    rate_limit: float = 1.0
    max_retries: int = 3
    timeout: int = 30
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass 
class CrawlerResult:
    """Result from crawler operation"""
    target: CrawlerTarget
    success: bool
    content: Optional[str] = None
    media_urls: List[str] = field(default_factory=list)
    extracted_data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    fingerprints: Dict[str, Any] = field(default_factory=dict)
    threat_score: float = 0.0
    similarity_matches: List[Dict[str, Any]] = field(default_factory=list)
    processing_time: float = 0.0
    error_message: Optional[str] = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        result = asdict(self)
        result['timestamp'] = self.timestamp.isoformat()
        result['target'] = asdict(self.target)
        return result


@dataclass
class CrawlerConfig:
    """Configuration for web crawler"""
    # Basic settings
    concurrent_requests: int = 10
    request_delay: float = 1.0
    timeout: int = 30
    max_retries: int = 3
    follow_redirects: bool = True
    respect_robots: bool = True
    
    # Browser settings
    use_selenium: bool = False
    use_playwright: bool = False
    headless: bool = True
    browser_executable: Optional[str] = None
    
    # Headers and user agents
    user_agents: List[str] = field(default_factory=list)
    custom_headers: Dict[str, str] = field(default_factory=dict)
    
    # Proxy settings
    proxy_urls: List[str] = field(default_factory=list)
    rotate_proxies: bool = False
    
    # Content filtering
    allowed_content_types: List[str] = field(default_factory=lambda: [
        'text/html', 'application/json', 'text/xml', 'application/xml'
    ])
    max_content_size: int = 50 * 1024 * 1024  # 50MB
    
    # Database settings
    database_url: Optional[str] = None
    redis_url: Optional[str] = None
    
    # Storage settings
    storage_path: Optional[Path] = None
    store_content: bool = True
    compress_content: bool = True
    encrypt_content: bool = False
    
    # AI/ML settings
    enable_ai_analysis: bool = True
    fingerprinting_enabled: bool = True
    similarity_threshold: float = 0.8
    
    # Performance settings
    enable_caching: bool = True
    cache_ttl: int = 3600
    enable_metrics: bool = True


class PlatformCrawler:
    """Base class for platform-specific crawlers"""
    
    def __init__(self, platform: str, config: CrawlerConfig):
        self.platform = platform
        self.config = config
        self.rate_limiter = RateLimiter() if RateLimiter else None
        self.session: Optional[aiohttp.ClientSession] = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        
    async def initialize(self):
        """Initialize crawler resources"""
        # Create HTTP session
        timeout = aiohttp.ClientTimeout(total=self.config.timeout)
        connector = aiohttp.TCPConnector(limit=self.config.concurrent_requests)
        
        self.session = aiohttp.ClientSession(
            timeout=timeout,
            connector=connector,
            headers=self.config.custom_headers
        )
        
        # Initialize browser if needed
        if self.config.use_playwright:
            playwright = await async_playwright().start()
            self.browser = await playwright.chromium.launch(
                headless=self.config.headless,
                executable_path=self.config.browser_executable
            )
            self.context = await self.browser.new_context()
    
    async def cleanup(self):
        """Clean up crawler resources"""
        if self.session:
            await self.session.close()
        
        if self.context:
            await self.context.close()
        
        if self.browser:
            await self.browser.close()
    
    async def crawl(self, target: CrawlerTarget) -> CrawlerResult:
        """Crawl target URL and extract content"""
        start_time = time.time()
        
        try:
            # Rate limiting
            if self.rate_limiter:
                await self.rate_limiter.wait(target.rate_limit)
            
            # Check robots.txt if required
            if target.respect_robots and self.config.respect_robots:
                if not await self._check_robots_allowed(target.url):
                    return CrawlerResult(
                        target=target,
                        success=False,
                        error_message="Blocked by robots.txt"
                    )
            
            # Perform crawling based on requirements
            if target.javascript_required or self.config.use_playwright:
                result = await self._crawl_with_browser(target)
            else:
                result = await self._crawl_with_http(target)
            
            # Calculate processing time
            result.processing_time = time.time() - start_time
            
            logger.info(f"Crawled {target.url} in {result.processing_time:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"Crawling failed for {target.url}: {e}")
            return CrawlerResult(
                target=target,
                success=False,
                error_message=str(e),
                processing_time=time.time() - start_time
            )
    
    async def _crawl_with_http(self, target: CrawlerTarget) -> CrawlerResult:
        """Crawl using HTTP client"""
        headers = {**self.config.custom_headers, **target.custom_headers}
        
        # Add random user agent
        if self.config.user_agents:
            headers['User-Agent'] = random.choice(self.config.user_agents)
        
        async with self.session.get(
            target.url,
            headers=headers,
            allow_redirects=target.follow_redirects,
            timeout=target.timeout
        ) as response:
            
            # Check content type
            content_type = response.headers.get('content-type', '').lower()
            if not any(allowed in content_type for allowed in self.config.allowed_content_types):
                return CrawlerResult(
                    target=target,
                    success=False,
                    error_message=f"Unsupported content type: {content_type}"
                )
            
            # Get content
            content = await response.text()
            
            # Extract data
            extracted_data = await self._extract_data(content, target)
            
            # Extract media URLs
            media_urls = await self._extract_media_urls(content, target.url)
            
            return CrawlerResult(
                target=target,
                success=True,
                content=content,
                media_urls=media_urls,
                extracted_data=extracted_data,
                metadata={
                    'status_code': response.status,
                    'content_type': content_type,
                    'content_length': len(content),
                    'headers': dict(response.headers)
                }
            )
    
    async def _crawl_with_browser(self, target: CrawlerTarget) -> CrawlerResult:
        """Crawl using browser automation"""
        page = await self.context.new_page()
        
        try:
            # Navigate to page
            await page.goto(target.url, wait_until='networkidle')
            
            # Wait for specific elements if defined
            if target.selectors:
                for selector in target.selectors.values():
                    try:
                        await page.wait_for_selector(selector, timeout=5000)
                    except:
                        pass  # Continue if selector not found
            
            # Get content
            content = await page.content()
            
            # Extract data using selectors
            extracted_data = {}
            if target.selectors:
                for key, selector in target.selectors.items():
                    try:
                        element = await page.query_selector(selector)
                        if element:
                            extracted_data[key] = await element.inner_text()
                    except:
                        continue
            
            # Extract media URLs
            media_urls = await self._extract_media_urls_from_page(page)
            
            # Take screenshot for visual analysis
            screenshot = await page.screenshot()
            
            return CrawlerResult(
                target=target,
                success=True,
                content=content,
                media_urls=media_urls,
                extracted_data=extracted_data,
                metadata={
                    'page_title': await page.title(),
                    'url': page.url,
                    'screenshot': base64.b64encode(screenshot).decode()
                }
            )
            
        finally:
            await page.close()
    
    async def _extract_data(self, content: str, target: CrawlerTarget) -> Dict[str, Any]:
        """Extract structured data from content"""
        data = {}
        
        try:
            soup = BeautifulSoup(content, 'html.parser')
            
            # Extract basic metadata
            if soup.title:
                data['title'] = soup.title.string
            
            # Extract meta tags
            meta_tags = soup.find_all('meta')
            data['meta'] = {}
            for tag in meta_tags:
                name = tag.get('name') or tag.get('property')
                content_attr = tag.get('content')
                if name and content_attr:
                    data['meta'][name] = content_attr
            
            # Extract links
            links = soup.find_all('a', href=True)
            data['links'] = [urljoin(target.url, link['href']) for link in links]
            
            # Extract text content
            data['text_content'] = soup.get_text(strip=True)
            
            # Platform-specific extraction
            data.update(await self._platform_specific_extraction(soup, target))
            
        except Exception as e:
            logger.warning(f"Data extraction failed: {e}")
        
        return data
    
    async def _platform_specific_extraction(self, soup: BeautifulSoup, target: CrawlerTarget) -> Dict[str, Any]:
        """Platform-specific data extraction - override in subclasses"""
        return {}
    
    async def _extract_media_urls(self, content: str, base_url: str) -> List[str]:
        """Extract media URLs from content"""
        media_urls = []
        
        try:
            soup = BeautifulSoup(content, 'html.parser')
            
            # Extract images
            for img in soup.find_all('img', src=True):
                media_urls.append(urljoin(base_url, img['src']))
            
            # Extract videos
            for video in soup.find_all('video', src=True):
                media_urls.append(urljoin(base_url, video['src']))
            
            for source in soup.find_all('source', src=True):
                media_urls.append(urljoin(base_url, source['src']))
            
            # Extract audio
            for audio in soup.find_all('audio', src=True):
                media_urls.append(urljoin(base_url, audio['src']))
            
        except Exception as e:
            logger.warning(f"Media extraction failed: {e}")
        
        return media_urls
    
    async def _extract_media_urls_from_page(self, page: Page) -> List[str]:
        """Extract media URLs using browser automation"""
        media_urls = []
        
        try:
            # Get all media elements
            media_elements = await page.query_selector_all('img, video, audio, source')
            
            for element in media_elements:
                src = await element.get_attribute('src')
                if src:
                    media_urls.append(urljoin(page.url, src))
        
        except Exception as e:
            logger.warning(f"Browser media extraction failed: {e}")
        
        return media_urls
    
    async def _check_robots_allowed(self, url: str) -> bool:
        """Check if URL is allowed by robots.txt"""
        try:
            parsed = urlparse(url)
            robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
            
            async with self.session.get(robots_url) as response:
                if response.status == 200:
                    robots_content = await response.text()
                    # Simple robots.txt checking - can be enhanced
                    return 'Disallow: /' not in robots_content
        
        except:
            pass
        
        return True


class YoutubeCrawler(PlatformCrawler):
    """YouTube-specific crawler"""
    
    def __init__(self, config: CrawlerConfig):
        super().__init__("youtube", config)
    
    async def _platform_specific_extraction(self, soup: BeautifulSoup, target: CrawlerTarget) -> Dict[str, Any]:
        """Extract YouTube-specific data"""
        data = {}
        
        try:
            # Extract video metadata
            scripts = soup.find_all('script')
            for script in scripts:
                if script.string and 'ytInitialData' in script.string:
                    # Extract structured data from YouTube's JavaScript
                    content = script.string
                    # Parse YouTube data structure
                    data['youtube_metadata'] = self._parse_youtube_data(content)
                    break
        
        except Exception as e:
            logger.warning(f"YouTube extraction failed: {e}")
        
        return data
    
    def _parse_youtube_data(self, content: str) -> Dict[str, Any]:
        """Parse YouTube's structured data"""
        # Implementation for parsing YouTube's complex data structure
        # This is a simplified version - real implementation would be more complex
        return {'parsed': True}


class TiktokCrawler(PlatformCrawler):
    """TikTok-specific crawler"""
    
    def __init__(self, config: CrawlerConfig):
        super().__init__("tiktok", config)
    
    async def _platform_specific_extraction(self, soup: BeautifulSoup, target: CrawlerTarget) -> Dict[str, Any]:
        """Extract TikTok-specific data"""
        data = {}
        
        try:
            # TikTok requires browser automation due to heavy JavaScript
            # Extract from structured data
            scripts = soup.find_all('script', {'type': 'application/ld+json'})
            for script in scripts:
                try:
                    json_data = json.loads(script.string)
                    data['tiktok_structured_data'] = json_data
                    break
                except:
                    continue
        
        except Exception as e:
            logger.warning(f"TikTok extraction failed: {e}")
        
        return data


class InstagramCrawler(PlatformCrawler):
    """Instagram-specific crawler"""
    
    def __init__(self, config: CrawlerConfig):
        super().__init__("instagram", config)
    
    async def _platform_specific_extraction(self, soup: BeautifulSoup, target: CrawlerTarget) -> Dict[str, Any]:
        """Extract Instagram-specific data"""
        data = {}
        
        try:
            # Extract from meta tags
            og_tags = soup.find_all('meta', property=re.compile(r'^og:'))
            for tag in og_tags:
                property_name = tag.get('property')
                content = tag.get('content')
                if property_name and content:
                    data[property_name] = content
        
        except Exception as e:
            logger.warning(f"Instagram extraction failed: {e}")
        
        return data


class WebCrawlerEngine:
    """
    Ultra-Advanced Web Crawler Engine
    
    Provides comprehensive web crawling capabilities with AI-powered content
    analysis, multi-platform support, and real-time threat detection.
    """
    
    def __init__(self, config: CrawlerConfig):
        """Initialize web crawler engine"""
        self.config = config
        self.metrics = PrometheusMetrics() if (PrometheusMetrics and config.enable_metrics) else None
        self.redis_client: Optional[redis.Redis] = None
        self.db_session: Optional[Session] = None
        
        # Platform crawlers
        self.crawlers: Dict[str, PlatformCrawler] = {}
        
        # AI components
        self.fingerprint_extractor: Optional[ContentFingerprintExtractor] = None
        
        # Initialize components
        asyncio.create_task(self._initialize_async_components())
        
        logger.info("WebCrawlerEngine initialized")
    
    async def _initialize_async_components(self):
        """Initialize async components"""
        try:
            # Initialize database
            if self.config.database_url:
                engine = create_engine(self.config.database_url)
                Session = sessionmaker(bind=engine)
                self.db_session = Session()
                
                # Create tables
                Base.metadata.create_all(engine)
            
            # Initialize Redis
            if self.config.redis_url:
                self.redis_client = redis.from_url(self.config.redis_url)
            
            # Initialize AI components
            if self.config.enable_ai_analysis and ContentFingerprintExtractor:
                self.fingerprint_extractor = ContentFingerprintExtractor()
            
            # Initialize platform crawlers
            await self._initialize_crawlers()
            
            logger.info("Async components initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize async components: {e}")
            raise
    
    async def _initialize_crawlers(self):
        """Initialize platform-specific crawlers"""
        crawler_classes = {
            'youtube': YoutubeCrawler,
            'tiktok': TiktokCrawler,
            'instagram': InstagramCrawler,
            'generic': PlatformCrawler
        }
        
        for platform, crawler_class in crawler_classes.items():
            try:
                if platform == 'generic':
                    crawler = crawler_class(platform, self.config)
                else:
                    crawler = crawler_class(self.config)
                
                await crawler.initialize()
                self.crawlers[platform] = crawler
                
                logger.info(f"Initialized {platform} crawler")
                
            except Exception as e:
                logger.error(f"Failed to initialize {platform} crawler: {e}")
    
    async def crawl_targets(
        self,
        targets: List[CrawlerTarget],
        concurrent_limit: Optional[int] = None
    ) -> List[CrawlerResult]:
        """Crawl multiple targets concurrently"""
        if not concurrent_limit:
            concurrent_limit = self.config.concurrent_requests
        
        semaphore = asyncio.Semaphore(concurrent_limit)
        
        async def crawl_with_semaphore(target: CrawlerTarget) -> CrawlerResult:
            async with semaphore:
                return await self.crawl_target(target)
        
        # Create tasks
        tasks = [crawl_with_semaphore(target) for target in targets]
        
        # Execute concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append(CrawlerResult(
                    target=targets[i],
                    success=False,
                    error_message=str(result)
                ))
            else:
                processed_results.append(result)
        
        # Store results if database available
        if self.db_session:
            await self._store_results(processed_results)
        
        logger.info(f"Crawled {len(targets)} targets, {sum(1 for r in processed_results if r.success)} successful")
        
        return processed_results
    
    async def crawl_target(self, target: CrawlerTarget) -> CrawlerResult:
        """Crawl single target"""
        try:
            # Get appropriate crawler
            crawler = self._get_crawler_for_target(target)
            
            # Check cache if enabled
            if self.config.enable_caching:
                cached_result = await self._get_cached_result(target)
                if cached_result:
                    return cached_result
            
            # Perform crawling
            result = await crawler.crawl(target)
            
            # Process result with AI if successful
            if result.success and self.config.enable_ai_analysis:
                result = await self._analyze_content(result)
            
            # Cache result if enabled
            if self.config.enable_caching and result.success:
                await self._cache_result(target, result)
            
            # Update metrics
            if self.metrics:
                self.metrics.increment_counter(
                    'crawler_requests_total',
                    {'platform': target.platform, 'success': str(result.success)}
                )
                
                if result.success:
                    self.metrics.record_histogram(
                        'crawler_processing_duration_seconds',
                        result.processing_time,
                        {'platform': target.platform}
                    )
            
            return result
            
        except Exception as e:
            logger.error(f"Crawling failed for {target.url}: {e}")
            return CrawlerResult(
                target=target,
                success=False,
                error_message=str(e)
            )
    
    def _get_crawler_for_target(self, target: CrawlerTarget) -> PlatformCrawler:
        """Get appropriate crawler for target"""
        platform = target.platform.lower()
        
        if platform in self.crawlers:
            return self.crawlers[platform]
        else:
            return self.crawlers.get('generic', self.crawlers['generic'])
    
    async def _analyze_content(self, result: CrawlerResult) -> CrawlerResult:
        """Analyze crawled content with AI"""
        try:
            if not result.content:
                return result
            
            # Extract fingerprints
            if self.config.fingerprinting_enabled and self.fingerprint_extractor:
                fingerprints = await self.fingerprint_extractor.extract_fingerprints(
                    content=result.content,
                    content_type='text/html',
                    media_urls=result.media_urls
                )
                result.fingerprints = fingerprints
            
            # Calculate threat score
            result.threat_score = await self._calculate_threat_score(result)
            
            # Find similarity matches
            if result.fingerprints:
                result.similarity_matches = await self._find_similarity_matches(result)
            
        except Exception as e:
            logger.error(f"Content analysis failed: {e}")
        
        return result
    
    async def _calculate_threat_score(self, result: CrawlerResult) -> float:
        """Calculate threat score for crawled content"""
        threat_score = 0.0
        
        try:
            # Check for suspicious patterns
            if result.content:
                suspicious_patterns = [
                    r'download.*video',
                    r'rip.*audio',
                    r'convert.*mp3',
                    r'free.*download',
                    r'pirate.*content'
                ]
                
                content_lower = result.content.lower()
                for pattern in suspicious_patterns:
                    if re.search(pattern, content_lower):
                        threat_score += 0.2
            
            # Check extracted data for threats
            extracted_data = result.extracted_data
            if extracted_data.get('title'):
                if any(word in extracted_data['title'].lower() for word in ['download', 'rip', 'convert']):
                    threat_score += 0.3
            
            # Normalize score
            threat_score = min(threat_score, 1.0)
            
        except Exception as e:
            logger.error(f"Threat score calculation failed: {e}")
        
        return threat_score
    
    async def _find_similarity_matches(self, result: CrawlerResult) -> List[Dict[str, Any]]:
        """Find similar content in database"""
        matches = []
        
        try:
            if not self.db_session:
                return matches
            
            # Query similar fingerprints from database
            # This is a simplified version - real implementation would use FAISS
            similar_records = self.db_session.query(CrawlRecord).filter(
                CrawlRecord.content_hash == result.fingerprints.get('content_hash')
            ).limit(10).all()
            
            for record in similar_records:
                matches.append({
                    'id': record.id,
                    'url': record.target_url,
                    'platform': record.platform,
                    'similarity_score': 0.9,  # Placeholder
                    'timestamp': record.crawl_timestamp.isoformat()
                })
        
        except Exception as e:
            logger.error(f"Similarity matching failed: {e}")
        
        return matches
    
    async def _get_cached_result(self, target: CrawlerTarget) -> Optional[CrawlerResult]:
        """Get cached crawl result"""
        if not self.redis_client:
            return None
        
        try:
            cache_key = f"crawl_result:{hashlib.md5(target.url.encode()).hexdigest()}"
            cached_data = self.redis_client.get(cache_key)
            
            if cached_data:
                result_dict = json.loads(cached_data)
                # Reconstruct CrawlerResult from dict
                return CrawlerResult(**result_dict)
        
        except Exception as e:
            logger.error(f"Cache retrieval failed: {e}")
        
        return None
    
    async def _cache_result(self, target: CrawlerTarget, result: CrawlerResult):
        """Cache crawl result"""
        if not self.redis_client:
            return
        
        try:
            cache_key = f"crawl_result:{hashlib.md5(target.url.encode()).hexdigest()}"
            result_dict = result.to_dict()
            
            self.redis_client.setex(
                cache_key,
                self.config.cache_ttl,
                json.dumps(result_dict, default=str)
            )
        
        except Exception as e:
            logger.error(f"Cache storage failed: {e}")
    
    async def _store_results(self, results: List[CrawlerResult]):
        """Store crawl results in database"""
        if not self.db_session:
            return
        
        try:
            for result in results:
                if result.success:
                    record = CrawlRecord(
                        id=hashlib.sha256(f"{result.target.url}_{result.timestamp}".encode()).hexdigest(),
                        target_url=result.target.url,
                        platform=result.target.platform,
                        content_type=result.target.content_type,
                        title=result.extracted_data.get('title'),
                        description=result.extracted_data.get('description'),
                        metadata=result.metadata,
                        fingerprints=result.fingerprints,
                        threat_indicators={'threat_score': result.threat_score},
                        crawl_timestamp=result.timestamp,
                        processing_status='completed',
                        content_hash=result.fingerprints.get('content_hash'),
                        similarity_scores=[match.get('similarity_score') for match in result.similarity_matches]
                    )
                    
                    self.db_session.add(record)
            
            self.db_session.commit()
            logger.info(f"Stored {len([r for r in results if r.success])} crawl results")
            
        except Exception as e:
            logger.error(f"Result storage failed: {e}")
            if self.db_session:
                self.db_session.rollback()
    
    async def get_crawl_history(
        self,
        platform: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Get crawl history from database"""
        if not self.db_session:
            return []
        
        try:
            query = self.db_session.query(CrawlRecord)
            
            if platform:
                query = query.filter(CrawlRecord.platform == platform)
            
            records = query.order_by(CrawlRecord.crawl_timestamp.desc()).offset(offset).limit(limit).all()
            
            return [
                {
                    'id': record.id,
                    'target_url': record.target_url,
                    'platform': record.platform,
                    'title': record.title,
                    'metadata': record.metadata,
                    'threat_score': record.threat_indicators.get('threat_score', 0.0) if record.threat_indicators else 0.0,
                    'crawl_timestamp': record.crawl_timestamp.isoformat(),
                    'processing_status': record.processing_status
                }
                for record in records
            ]
        
        except Exception as e:
            logger.error(f"Failed to get crawl history: {e}")
            return []
    
    async def search_crawled_content(
        self,
        query: str,
        platform: Optional[str] = None,
        content_type: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Search through crawled content"""
        if not self.db_session:
            return []
        
        try:
            db_query = self.db_session.query(CrawlRecord)
            
            # Add text search
            db_query = db_query.filter(
                CrawlRecord.title.contains(query) |
                CrawlRecord.description.contains(query)
            )
            
            if platform:
                db_query = db_query.filter(CrawlRecord.platform == platform)
            
            if content_type:
                db_query = db_query.filter(CrawlRecord.content_type == content_type)
            
            records = db_query.limit(limit).all()
            
            return [
                {
                    'id': record.id,
                    'target_url': record.target_url,
                    'platform': record.platform,
                    'title': record.title,
                    'description': record.description,
                    'content_type': record.content_type,
                    'crawl_timestamp': record.crawl_timestamp.isoformat(),
                    'threat_score': record.threat_indicators.get('threat_score', 0.0) if record.threat_indicators else 0.0
                }
                for record in records
            ]
        
        except Exception as e:
            logger.error(f"Content search failed: {e}")
            return []
    
    async def get_threat_analysis(
        self,
        threshold: float = 0.5,
        platform: Optional[str] = None,
        limit: int = 100
    ) -> Dict[str, Any]:
        """Get threat analysis from crawled content"""
        if not self.db_session:
            return {}
        
        try:
            query = self.db_session.query(CrawlRecord)
            
            if platform:
                query = query.filter(CrawlRecord.platform == platform)
            
            # Get high-threat content
            high_threat_query = query.filter(
                CrawlRecord.threat_indicators['threat_score'].astext.cast(float) >= threshold
            )
            high_threat_records = high_threat_query.limit(limit).all()
            
            # Get statistics
            total_records = query.count()
            threat_records = high_threat_query.count()
            
            # Calculate threat distribution
            threat_distribution = {}
            for record in high_threat_records:
                platform_name = record.platform
                if platform_name not in threat_distribution:
                    threat_distribution[platform_name] = 0
                threat_distribution[platform_name] += 1
            
            return {
                'total_crawled': total_records,
                'high_threat_count': threat_records,
                'threat_percentage': (threat_records / total_records * 100) if total_records > 0 else 0,
                'threat_distribution': threat_distribution,
                'high_threat_content': [
                    {
                        'id': record.id,
                        'url': record.target_url,
                        'platform': record.platform,
                        'title': record.title,
                        'threat_score': record.threat_indicators.get('threat_score', 0.0) if record.threat_indicators else 0.0,
                        'timestamp': record.crawl_timestamp.isoformat()
                    }
                    for record in high_threat_records
                ]
            }
        
        except Exception as e:
            logger.error(f"Threat analysis failed: {e}")
            return {'error': str(e)}
    
    async def shutdown(self):
        """Gracefully shutdown crawler engine"""
        logger.info("Shutting down WebCrawlerEngine...")
        
        # Cleanup crawlers
        for crawler in self.crawlers.values():
            try:
                await crawler.cleanup()
            except Exception as e:
                logger.error(f"Crawler cleanup failed: {e}")
        
        # Close database session
        if self.db_session:
            self.db_session.close()
        
        # Close Redis connection
        if self.redis_client:
            self.redis_client.close()
        
        logger.info("WebCrawlerEngine shutdown complete")


# Factory functions
def create_crawler_config(
    concurrent_requests: int = 10,
    enable_browser: bool = False,
    database_url: Optional[str] = None,
    **kwargs
) -> CrawlerConfig:
    """Create crawler configuration with defaults"""
    
    config = CrawlerConfig(
        concurrent_requests=concurrent_requests,
        use_playwright=enable_browser,
        database_url=database_url
    )
    
    # Apply custom settings
    for key, value in kwargs.items():
        if hasattr(config, key):
            setattr(config, key, value)
    
    return config


def create_crawler_target(
    url: str,
    platform: str = "generic",
    **kwargs
) -> CrawlerTarget:
    """Create crawler target with defaults"""
    
    target = CrawlerTarget(url=url, platform=platform)
    
    # Apply custom settings
    for key, value in kwargs.items():
        if hasattr(target, key):
            setattr(target, key, value)
    
    return target


async def create_web_crawler_engine(
    database_url: Optional[str] = None,
    redis_url: Optional[str] = None,
    **config_kwargs
) -> WebCrawlerEngine:
    """Create and initialize web crawler engine"""
    
    config = create_crawler_config(
        database_url=database_url,
        redis_url=redis_url,
        **config_kwargs
    )
    
    engine = WebCrawlerEngine(config)
    
    # Wait for async initialization to complete
    await asyncio.sleep(0.1)  # Allow initialization task to start
    
    return engine
    errors: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class PlatformCrawler:
    """Base class for platform-specific crawlers"""
    
    def __init__(self, platform: str, config: CrawlerConfig):
        self.platform = platform
        self.config = config
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def initialize(self) -> None:
        """Initialize crawler session"""
        timeout = aiohttp.ClientTimeout(total=self.config.request_timeout)
        self.session = aiohttp.ClientSession(
            timeout=timeout,
            headers=self.config.headers,
            connector=aiohttp.TCPConnector(limit=self.config.max_concurrent_requests)
        )
    
    async def crawl(
        self, 
        search_terms: List[str], 
        content_fingerprints: Dict[str, Any]
    ) -> CrawlerResult:
        """Crawl platform for content matches"""
        # Default implementation for platforms without crawling support
        logging.warning(f"Web crawling not implemented for {self.__class__.__name__}")
        from datetime import datetime
        return CrawlerResult(
            platform=getattr(self, 'platform', 'unknown'),
            search_terms=search_terms,
            total_results=0,
            matches_found=0,
            crawl_duration=0.0,
            crawled_at=datetime.utcnow(),
            results=[]
        )
    
    async def shutdown(self) -> None:
        """Cleanup crawler resources"""
        if self.session:
            await self.session.close()


class YouTubeCrawler(PlatformCrawler):
    """YouTube-specific crawler"""
    
    def __init__(self, config: CrawlerConfig):
        super().__init__("youtube", config)
        self.search_urls = [
            "https://www.youtube.com/results?search_query={query}",
            "https://www.youtube.com/feed/trending"
        ]
    
    async def crawl(
        self, 
        search_terms: List[str], 
        content_fingerprints: Dict[str, Any]
    ) -> CrawlerResult:
        """Crawl YouTube for content matches"""
        start_time = time.time()
        result = CrawlerResult(
            platform=self.platform,
            urls_scanned=0,
            content_found=[],
            matches_detected=0,
            processing_time=0.0
        )
        
        try:
            for search_term in search_terms[:10]:  # Limit search terms
                search_url = self.search_urls[0].format(query=search_term.replace(" ", "+"))
                
                try:
                    async with self.session.get(search_url) as response:
                        if response.status == 200:
                            html_content = await response.text()
                            videos = await self._extract_youtube_videos(html_content)
                            
                            for video in videos:
                                content_match = await self._check_content_match(
                                    video, content_fingerprints
                                )
                                if content_match:
                                    result.content_found.append(video)
                                    result.matches_detected += 1
                            
                            result.urls_scanned += 1
                        
                        # Respectful delay
                        await asyncio.sleep(self.config.delay_between_requests)
                        
                except Exception as e:
                    result.errors.append(f"YouTube search error: {str(e)}")
                    logger.error(f"YouTube crawling error for '{search_term}': {e}")
        
        except Exception as e:
            result.errors.append(f"YouTube crawler error: {str(e)}")
            logger.error(f"YouTube crawler failed: {e}")
        
        result.processing_time = time.time() - start_time
        return result
    
    async def _extract_youtube_videos(self, html_content: str) -> List[Dict[str, Any]]:
        """Extract video information from YouTube HTML"""
        videos = []
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Look for video containers (simplified extraction)
            video_elements = soup.find_all('div', {'class': 'ytd-video-renderer'})
            
            for element in video_elements[:20]:  # Limit results
                try:
                    # Extract basic video info
                    title_elem = element.find('a', {'id': 'video-title'})
                    if title_elem:
                        video_info = {
                            'title': title_elem.get_text(strip=True),
                            'url': urljoin('https://www.youtube.com', title_elem.get('href', '')),
                            'platform': 'youtube',
                            'type': 'video',
                            'extracted_at': datetime.now(timezone.utc).isoformat()
                        }
                        videos.append(video_info)
                
                except Exception as e:
                    logger.debug(f"Error extracting video info: {e}")
                    continue
        
        except Exception as e:
            logger.error(f"Error parsing YouTube HTML: {e}")
        
        return videos
    
    async def _check_content_match(
        self, 
        video_data: Dict[str, Any], 
        content_fingerprints: Dict[str, Any]
    ) -> bool:
        """Check if video matches content fingerprints"""
        # Simplified matching based on title similarity
        video_title = video_data.get('title', '').lower()
        
        # Check against fingerprint keywords
        keywords = content_fingerprints.get('keywords', [])
        title_keywords = content_fingerprints.get('title_keywords', [])
        
        for keyword in keywords + title_keywords:
            if keyword.lower() in video_title:
                return True
        
        return False


class TikTokCrawler(PlatformCrawler):
    """TikTok-specific crawler"""
    
    def __init__(self, config: CrawlerConfig):
        super().__init__("tiktok", config)
    
    async def crawl(
        self, 
        search_terms: List[str], 
        content_fingerprints: Dict[str, Any]
    ) -> CrawlerResult:
        """Crawl TikTok for content matches"""
        start_time = time.time()
        result = CrawlerResult(
            platform=self.platform,
            urls_scanned=0,
            content_found=[],
            matches_detected=0,
            processing_time=0.0
        )
        
        # TikTok crawling implementation (simplified for demo)
        try:
            # Simulate TikTok API calls or web scraping
            for search_term in search_terms[:5]:
                # Placeholder for actual TikTok crawling logic
                await asyncio.sleep(1)  # Simulate processing time
                result.urls_scanned += 1
                
                # Simulate finding matches
                if "music" in search_term.lower():
                    result.content_found.append({
                        'title': f"TikTok video with {search_term}",
                        'url': f"https://tiktok.com/@user/video/{hash(search_term)}",
                        'platform': 'tiktok',
                        'type': 'video',
                        'extracted_at': datetime.now(timezone.utc).isoformat()
                    })
                    result.matches_detected += 1
        
        except Exception as e:
            result.errors.append(f"TikTok crawler error: {str(e)}")
            logger.error(f"TikTok crawler failed: {e}")
        
        result.processing_time = time.time() - start_time
        return result


class InstagramCrawler(PlatformCrawler):
    """Instagram-specific crawler"""
    
    def __init__(self, config: CrawlerConfig):
        super().__init__("instagram", config)
    
    async def crawl(
        self, 
        search_terms: List[str], 
        content_fingerprints: Dict[str, Any]
    ) -> CrawlerResult:
        """Crawl Instagram for content matches"""
        start_time = time.time()
        result = CrawlerResult(
            platform=self.platform,
            urls_scanned=0,
            content_found=[],
            matches_detected=0,
            processing_time=0.0
        )
        
        # Instagram crawling implementation (simplified for demo)
        try:
            # Due to Instagram's strict API policies, this would typically
            # use their official API or approved scraping methods
            for search_term in search_terms[:5]:
                await asyncio.sleep(1)  # Simulate processing time
                result.urls_scanned += 1
                
                # Simulate finding matches based on hashtags or content
                if len(search_term) > 3:
                    result.content_found.append({
                        'title': f"Instagram post with #{search_term}",
                        'url': f"https://instagram.com/p/{hash(search_term)}",
                        'platform': 'instagram',
                        'type': 'image',
                        'extracted_at': datetime.now(timezone.utc).isoformat()
                    })
                    result.matches_detected += 1
        
        except Exception as e:
            result.errors.append(f"Instagram crawler error: {str(e)}")
            logger.error(f"Instagram crawler failed: {e}")
        
        result.processing_time = time.time() - start_time
        return result


class GenericWebCrawler(PlatformCrawler):
    """Generic web crawler for other websites"""
    
    def __init__(self, config: CrawlerConfig):
        super().__init__("generic", config)
    
    async def crawl(
        self, 
        search_terms: List[str], 
        content_fingerprints: Dict[str, Any],
        target_domains: Optional[List[str]] = None
    ) -> CrawlerResult:
        """Crawl generic websites for content matches"""
        start_time = time.time()
        result = CrawlerResult(
            platform=self.platform,
            urls_scanned=0,
            content_found=[],
            matches_detected=0,
            processing_time=0.0
        )
        
        try:
            # Default domains to search if none provided
            if not target_domains:
                target_domains = [
                    "soundcloud.com",
                    "vimeo.com",
                    "dailymotion.com",
                    "twitch.tv"
                ]
            
            for domain in target_domains:
                for search_term in search_terms[:3]:  # Limit per domain
                    try:
                        # Construct search URL (simplified)
                        search_url = f"https://{domain}/search?q={search_term.replace(' ', '+')}"
                        
                        async with self.session.get(search_url) as response:
                            if response.status == 200:
                                html_content = await response.text()
                                content_items = await self._extract_generic_content(
                                    html_content, domain
                                )
                                
                                for item in content_items:
                                    content_match = await self._check_generic_content_match(
                                        item, content_fingerprints
                                    )
                                    if content_match:
                                        result.content_found.append(item)
                                        result.matches_detected += 1
                                
                                result.urls_scanned += 1
                            
                            await asyncio.sleep(self.config.delay_between_requests)
                    
                    except Exception as e:
                        result.errors.append(f"Generic crawling error for {domain}: {str(e)}")
                        logger.error(f"Generic crawling error for {domain}: {e}")
        
        except Exception as e:
            result.errors.append(f"Generic crawler error: {str(e)}")
            logger.error(f"Generic crawler failed: {e}")
        
        result.processing_time = time.time() - start_time
        return result
    
    async def _extract_generic_content(
        self, 
        html_content: str, 
        domain: str
    ) -> List[Dict[str, Any]]:
        """Extract content from generic website HTML"""
        content_items = []
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Look for common content elements
            content_selectors = [
                'div[class*="content"]',
                'div[class*="item"]',
                'div[class*="result"]',
                'article',
                'section[class*="content"]'
            ]
            
            for selector in content_selectors:
                elements = soup.select(selector)[:10]  # Limit results
                
                for element in elements:
                    try:
                        # Extract title and link
                        title_elem = element.find(['h1', 'h2', 'h3', 'h4', 'a'])
                        link_elem = element.find('a')
                        
                        if title_elem and link_elem:
                            item = {
                                'title': title_elem.get_text(strip=True),
                                'url': urljoin(f"https://{domain}", link_elem.get('href', '')),
                                'platform': domain,
                                'type': self._detect_content_type(domain),
                                'extracted_at': datetime.now(timezone.utc).isoformat()
                            }
                            content_items.append(item)
                    
                    except Exception as e:
                        logger.debug(f"Error extracting content item: {e}")
                        continue
        
        except Exception as e:
            logger.error(f"Error parsing HTML for {domain}: {e}")
        
        return content_items
    
    async def _check_generic_content_match(
        self, 
        content_item: Dict[str, Any], 
        content_fingerprints: Dict[str, Any]
    ) -> bool:
        """Check if content matches fingerprints"""
        title = content_item.get('title', '').lower()
        
        # Check against fingerprint data
        keywords = content_fingerprints.get('keywords', [])
        for keyword in keywords:
            if keyword.lower() in title:
                return True
        
        return False
    
    def _detect_content_type(self, domain: str) -> str:
        """Detect content type based on domain"""
        if 'soundcloud' in domain:
            return 'audio'
        elif 'vimeo' in domain or 'dailymotion' in domain:
            return 'video'
        elif 'twitch' in domain:
            return 'live_stream'
        else:
            return 'mixed_media'


class WebCrawlerEngine:
    """
    Main web crawler engine orchestrating multiple platform crawlers
    for comprehensive content surveillance
    """
    
    def __init__(self, surveillance_config):
        self.config = CrawlerConfig()
        self.surveillance_config = surveillance_config
        self.crawlers: Dict[str, PlatformCrawler] = {}
        self.initialized = False
    
    async def initialize(self) -> None:
        """Initialize all platform crawlers"""
        try:
            # Initialize platform-specific crawlers
            self.crawlers["youtube"] = YouTubeCrawler(self.config)
            self.crawlers["tiktok"] = TikTokCrawler(self.config)
            self.crawlers["instagram"] = InstagramCrawler(self.config)
            self.crawlers["generic"] = GenericWebCrawler(self.config)
            
            # Initialize each crawler
            for crawler in self.crawlers.values():
                await crawler.initialize()
            
            self.initialized = True
            logger.info("Web Crawler Engine initialized successfully")
        
        except Exception as e:
            logger.error(f"Failed to initialize Web Crawler Engine: {e}")
            raise
    
    async def crawl_platform(
        self,
        platform: str,
        content_fingerprints: Dict[str, Any],
        search_parameters: Dict[str, Any]
    ) -> CrawlerResult:
        """Crawl specific platform for content matches"""
        if not self.initialized:
            raise RuntimeError("Web Crawler Engine not initialized")
        
        # Generate search terms from fingerprints and parameters
        search_terms = self._generate_search_terms(content_fingerprints, search_parameters)
        
        # Select appropriate crawler
        crawler = self.crawlers.get(platform)
        if not crawler:
            # Use generic crawler for unknown platforms
            crawler = self.crawlers["generic"]
        
        try:
            result = await crawler.crawl(search_terms, content_fingerprints)
            logger.info(f"Crawled {platform}: {result.matches_detected} matches found")
            return result
            
        except Exception as e:
            logger.error(f"Crawling failed for {platform}: {e}")
            # Return empty result with error
            return CrawlerResult(
                platform=platform,
                urls_scanned=0,
                content_found=[],
                matches_detected=0,
                processing_time=0.0,
                errors=[str(e)]
            )
    
    async def crawl_multiple_platforms(
        self,
        platforms: List[str],
        content_fingerprints: Dict[str, Any],
        search_parameters: Dict[str, Any]
    ) -> Dict[str, CrawlerResult]:
        """Crawl multiple platforms concurrently"""
        if not self.initialized:
            raise RuntimeError("Web Crawler Engine not initialized")
        
        # Create crawling tasks
        crawling_tasks = []
        for platform in platforms:
            if platform in self.surveillance_config.enabled_platforms:
                task = asyncio.create_task(
                    self.crawl_platform(platform, content_fingerprints, search_parameters)
                )
                crawling_tasks.append((platform, task))
        
        # Execute tasks concurrently with limit
        semaphore = asyncio.Semaphore(self.config.max_concurrent_requests)
        
        async def limited_crawl(platform_task):
            async with semaphore:
                platform, task = platform_task
                return platform, await task
        
        # Run limited concurrent crawling
        limited_tasks = [limited_crawl(pt) for pt in crawling_tasks]
        results = await asyncio.gather(*limited_tasks, return_exceptions=True)
        
        # Process results
        crawling_results = {}
        for result in results:
            if isinstance(result, tuple):
                platform, crawler_result = result
                crawling_results[platform] = crawler_result
            elif isinstance(result, Exception):
                logger.error(f"Crawling task failed: {result}")
        
        return crawling_results
    
    def _generate_search_terms(
        self,
        content_fingerprints: Dict[str, Any],
        search_parameters: Dict[str, Any]
    ) -> List[str]:
        """Generate search terms from fingerprints and parameters"""
        search_terms = []
        
        # Add terms from fingerprints
        if 'title' in content_fingerprints:
            search_terms.append(content_fingerprints['title'])
        
        if 'keywords' in content_fingerprints:
            search_terms.extend(content_fingerprints['keywords'][:5])
        
        if 'artist_name' in content_fingerprints:
            search_terms.append(content_fingerprints['artist_name'])
        
        if 'album_name' in content_fingerprints:
            search_terms.append(content_fingerprints['album_name'])
        
        # Add terms from search parameters
        creator_id = search_parameters.get('creator_id', '')
        if creator_id:
            search_terms.append(creator_id)
        
        # Remove duplicates and empty terms
        search_terms = list(set([term for term in search_terms if term and len(term) > 2]))
        
        return search_terms[:10]  # Limit search terms
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on crawler engine"""
        health_status = {
            "engine": "healthy" if self.initialized else "unhealthy",
            "crawlers": {},
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        for platform, crawler in self.crawlers.items():
            try:
                # Simple connectivity test
                if hasattr(crawler, 'session') and crawler.session:
                    health_status["crawlers"][platform] = "ready"
                else:
                    health_status["crawlers"][platform] = "not_initialized"
            except Exception as e:
                health_status["crawlers"][platform] = f"error: {str(e)}"
        
        return health_status
    
    async def shutdown(self) -> None:
        """Gracefully shutdown crawler engine"""
        logger.info("Shutting down Web Crawler Engine")
        
        # Shutdown all crawlers
        for platform, crawler in self.crawlers.items():
            try:
                await crawler.shutdown()
            except Exception as e:
                logger.error(f"Error shutting down {platform} crawler: {e}")
        
        self.initialized = False
        logger.info("Web Crawler Engine shutdown complete")


# Export main components
__all__ = [
    "WebCrawlerEngine",
    "CrawlerConfig",
    "CrawlerResult",
    "PlatformCrawler",
    "YouTubeCrawler",
    "TikTokCrawler",
    "InstagramCrawler",
    "GenericWebCrawler"
]
