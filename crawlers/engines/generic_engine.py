"""Generic Web Crawling Engine
==========================

Advanced generic web crawler for broad content discovery and surveillance.
Handles various website structures, content extraction, and monitoring.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

⚠️  AVERTISSEMENT LÉGAL ⚠️
Ce code est la propriété exclusive de Fahed Mlaiel (mlaiel@live.de).
Toute utilisation, reproduction, ou distribution sans autorisation écrite explicite est strictement interdite.
Les contrevenants seront poursuivis selon la loi allemande et internationale.
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any, AsyncGenerator, Set, Union
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import re
import json
import hashlib
import time
import random
from urllib.parse import urljoin, urlparse, quote, unquote
from urllib.robotparser import RobotFileParser

import aiohttp
import scrapy
from scrapy.crawler import CrawlerRunner
from scrapy.utils.project import get_project_settings
from scrapy.http import Request, Response
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import requests
from bs4 import BeautifulSoup
import trafilatura
from newspaper import Article
import feedparser

from ..core.base_engine import BaseCrawlerEngine
from ..core.exceptions import (
    CrawlerError, 
    RateLimitError, 
    AuthenticationError,
    ContentNotFoundError,
    BlockedByRobotsError,
    GeoBlockedError
)
from ..utils.rate_limiter import RateLimiter
from ..utils.cache_manager import CacheManager
from ..utils.proxy_manager import ProxyManager
from ..utils.content_extractor import ContentExtractor
from ..models.content_models import WebPage, WebSite, ContentMatch
from ...core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


@dataclass
class WebPageData:
    """Web page data structure"""    url: str
    title: str
    content: str
    meta_description: str
    meta_keywords: List[str]
    headers: Dict[str, str]
    links: List[str]
    images: List[str]
    videos: List[str]
    author: Optional[str]
    publish_date: Optional[datetime]
    language: str
    content_type: str
    word_count: int
    reading_time: int
    social_shares: Dict[str, int]
    seo_score: float
    accessibility_score: float
    performance_metrics: Dict[str, Any]
    extracted_entities: List[Dict]
    sentiment_score: float = 0.0
    content_hash: str = ""
    last_modified: Optional[datetime] = None
    content_similarity_hash: str = ""


@dataclass
class WebSiteData:
    """Website data structure"""    domain: str
    homepage_url: str
    site_name: str
    description: str
    technology_stack: List[str]
    cms_type: Optional[str]
    contact_info: Dict[str, Any]
    social_profiles: Dict[str, str]
    rss_feeds: List[str]
    sitemap_urls: List[str]
    robots_txt: str
    ssl_info: Dict[str, Any]
    performance_score: float
    seo_score: float
    accessibility_score: float
    mobile_friendly: bool
    pages_count: int
    last_crawled: datetime
    crawl_frequency: str = "weekly"


@dataclass
class ContentMatchData:
    """Content match data for theft detection"""    original_url: str
    matched_url: str
    similarity_score: float
    match_type: str  # exact, partial, paraphrased
    matched_content: str
    context: str
    discovered_at: datetime
    confidence_level: float
    evidence_strength: str
    plagiarism_indicators: List[str]


class GenericWebCrawlerEngine(BaseCrawlerEngine):
    """    Advanced generic web crawler engine for comprehensive content discovery.
    
    Features:
    - Multi-engine crawling (Scrapy, Selenium, requests)
    - Content extraction and analysis
    - Plagiarism and theft detection
    - SEO and performance analysis
    - Robots.txt compliance
    - Rate limiting and proxy support
    - Content fingerprinting
    """    
    def __init__(self, config: Optional[Dict] = None):
        """Initialize generic web crawler engine"""        super().__init__(config)
        self.session = None
        self.crawler_runner = None
        self.rate_limiter = RateLimiter(
            requests_per_minute=60,  # Conservative for unknown sites
            requests_per_hour=2000,
            requests_per_day=20000
        )
        self.cache_manager = CacheManager(
            cache_duration=timedelta(hours=6),
            max_cache_size=15000
        )
        self.proxy_manager = ProxyManager() if config and config.get('use_proxies') else None
        self.content_extractor = ContentExtractor()
        self.visited_urls = set()
        self.robots_cache = {}
        self._setup_session()
        self._setup_selenium_driver()
        self._setup_scrapy_runner()
    
    def _setup_session(self) -> None:
        """Setup HTTP session with comprehensive headers"""        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        })
        
        # Configure retries and timeouts
        from requests.adapters import HTTPAdapter
        from urllib3.util.retry import Retry
        
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        logger.info("Generic web crawler HTTP session initialized")
    
    def _setup_selenium_driver(self) -> None:
        """Setup Selenium WebDriver for JavaScript-heavy sites"""        try:
            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # Additional options for better compatibility
            chrome_options.add_argument('--disable-extensions')
            chrome_options.add_argument('--disable-plugins')
            chrome_options.add_argument('--disable-images')  # Faster loading
            chrome_options.add_argument('--disable-javascript')  # Can be enabled per site
            
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            logger.info("Selenium WebDriver initialized for generic crawling")
        except Exception as e:
            logger.error(f"Failed to initialize Selenium WebDriver: {e}")
            self.driver = None
    
    def _setup_scrapy_runner(self) -> None:
        """Setup Scrapy crawler runner"""        try:
            scrapy_settings = get_project_settings()
            scrapy_settings.setdict({
                'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'ROBOTSTXT_OBEY': True,
                'CONCURRENT_REQUESTS': 16,
                'CONCURRENT_REQUESTS_PER_DOMAIN': 8,
                'DOWNLOAD_DELAY': 1,
                'RANDOMIZE_DOWNLOAD_DELAY': 0.5,
                'AUTOTHROTTLE_ENABLED': True,
                'AUTOTHROTTLE_START_DELAY': 1,
                'AUTOTHROTTLE_MAX_DELAY': 60,
                'AUTOTHROTTLE_TARGET_CONCURRENCY': 1.0,
                'AUTOTHROTTLE_DEBUG': False,
                'HTTPCACHE_ENABLED': True,
                'HTTPCACHE_EXPIRATION_SECS': 3600,
                'LOG_LEVEL': 'WARNING'
            })
            
            self.crawler_runner = CrawlerRunner(scrapy_settings)
            logger.info("Scrapy crawler runner initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize Scrapy runner: {e}")
            self.crawler_runner = None
    
    async def crawl_url(self, url: str, method: str = 'auto') -> Optional[WebPageData]:
        """        Crawl a single URL and extract comprehensive data
        
        Args:
            url: URL to crawl
            method: Crawling method ('auto', 'requests', 'selenium', 'scrapy')
            
        Returns:
            Web page data or None if failed
        """        await self.rate_limiter.wait()
        
        # Check robots.txt
        if not await self._check_robots_txt(url):
            raise BlockedByRobotsError(f"URL blocked by robots.txt: {url}")
        
        cache_key = f"page_{hashlib.md5(url.encode()).hexdigest()}"
        cached_result = await self.cache_manager.get(cache_key)
        if cached_result:
            return cached_result
        
        try:
            # Determine crawling method
            if method == 'auto':
                method = await self._determine_best_method(url)
            
            page_data = None
            
            if method == 'requests':
                page_data = await self._crawl_with_requests(url)
            elif method == 'selenium':
                page_data = await self._crawl_with_selenium(url)
            elif method == 'scrapy':
                page_data = await self._crawl_with_scrapy(url)
            
            if page_data:
                await self.cache_manager.set(cache_key, page_data)
                self.visited_urls.add(url)
            
            return page_data
            
        except Exception as e:
            logger.error(f"Error crawling URL {url}: {e}")
            raise CrawlerError(f"Failed to crawl URL: {e}")
    
    async def crawl_website(self, domain: str, max_pages: int = 100) -> WebSiteData:
        """        Comprehensive website crawling and analysis
        
        Args:
            domain: Domain to crawl
            max_pages: Maximum number of pages to crawl
            
        Returns:
            Website data with all discovered pages
        """        start_url = f"https://{domain}" if not domain.startswith('http') else domain
        base_domain = urlparse(start_url).netloc
        
        try:
            # Initialize website data
            website_data = WebSiteData(
                domain=base_domain,
                homepage_url=start_url,
                site_name="",
                description="",
                technology_stack=[],
                cms_type=None,
                contact_info={},
                social_profiles={},
                rss_feeds=[],
                sitemap_urls=[],
                robots_txt="",
                ssl_info={},
                performance_score=0.0,
                seo_score=0.0,
                accessibility_score=0.0,
                mobile_friendly=False,
                pages_count=0,
                last_crawled=datetime.now()
            )
            
            # Crawl homepage first
            homepage_data = await self.crawl_url(start_url)
            if homepage_data:
                website_data.site_name = homepage_data.title
                website_data.description = homepage_data.meta_description
                website_data.pages_count += 1
            
            # Discover and crawl additional pages
            discovered_urls = await self._discover_urls(start_url, max_pages)
            
            for url in discovered_urls[:max_pages-1]:  # -1 because we already crawled homepage
                try:
                    if urlparse(url).netloc == base_domain:
                        page_data = await self.crawl_url(url)
                        if page_data:
                            website_data.pages_count += 1
                            
                        # Add delay between pages
                        await asyncio.sleep(random.uniform(1, 3))
                        
                except Exception as e:
                    logger.warning(f"Error crawling page {url}: {e}")
                    continue
            
            # Analyze website characteristics
            await self._analyze_website(website_data)
            
            return website_data
            
        except Exception as e:
            logger.error(f"Error crawling website {domain}: {e}")
            raise CrawlerError(f"Website crawling failed: {e}")
    
    async def search_content_theft(
        self, 
        original_content: str, 
        search_engines: List[str] = None,
        similarity_threshold: float = 0.7
    ) -> List[ContentMatchData]:
        """        Search for potential content theft across the web
        
        Args:
            original_content: Original content to search for
            search_engines: Search engines to use
            similarity_threshold: Minimum similarity to consider a match
            
        Returns:
            List of potential content matches
        """        if search_engines is None:
            search_engines = ['google', 'bing', 'duckduckgo']
        
        matches = []
        content_hash = hashlib.md5(original_content.encode()).hexdigest()
        
        # Extract key phrases for searching
        key_phrases = await self._extract_key_phrases(original_content)
        
        for search_engine in search_engines:
            for phrase in key_phrases[:5]:  # Search top 5 phrases
                try:
                    search_results = await self._search_web(phrase, search_engine)
                    
                    for result in search_results[:10]:  # Check top 10 results
                        try:
                            page_data = await self.crawl_url(result['url'])
                            if page_data:
                                similarity_score = await self._calculate_content_similarity(
                                    original_content,
                                    page_data.content
                                )
                                
                                if similarity_score >= similarity_threshold:
                                    match_data = ContentMatchData(
                                        original_url="",  # Would be provided by caller
                                        matched_url=result['url'],
                                        similarity_score=similarity_score,
                                        match_type=await self._classify_match_type(similarity_score),
                                        matched_content=page_data.content[:1000],  # First 1000 chars
                                        context=result.get('snippet', ''),
                                        discovered_at=datetime.now(),
                                        confidence_level=similarity_score,
                                        evidence_strength=await self._assess_evidence_strength(similarity_score),
                                        plagiarism_indicators=await self._detect_plagiarism_indicators(
                                            original_content, 
                                            page_data.content
                                        )
                                    )
                                    matches.append(match_data)
                                    
                        except Exception as e:
                            logger.warning(f"Error analyzing search result {result['url']}: {e}")
                            continue
                    
                    # Add delay between searches
                    await asyncio.sleep(random.uniform(2, 5))
                    
                except Exception as e:
                    logger.error(f"Error searching with {search_engine} for phrase '{phrase}': {e}")
                    continue
        
        # Remove duplicates and sort by similarity score
        unique_matches = {match.matched_url: match for match in matches}
        sorted_matches = sorted(unique_matches.values(), key=lambda x: x.similarity_score, reverse=True)
        
        return sorted_matches
    
    async def monitor_urls(
        self, 
        urls: List[str], 
        check_interval: int = 3600
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """        Monitor URLs for changes over time
        
        Args:
            urls: List of URLs to monitor
            check_interval: Check interval in seconds
            
        Yields:
            Change notifications
        """        url_snapshots = {}
        
        # Initial crawl
        for url in urls:
            try:
                page_data = await self.crawl_url(url)
                if page_data:
                    url_snapshots[url] = {
                        'content_hash': page_data.content_hash,
                        'last_modified': page_data.last_modified,
                        'title': page_data.title,
                        'word_count': page_data.word_count,
                        'last_checked': datetime.now()
                    }
            except Exception as e:
                logger.error(f"Error in initial crawl of {url}: {e}")
                continue
        
        while True:
            await asyncio.sleep(check_interval)
            
            for url in urls:
                try:
                    # Clear cache for fresh data
                    cache_key = f"page_{hashlib.md5(url.encode()).hexdigest()}"
                    await self.cache_manager.delete(cache_key)
                    
                    page_data = await self.crawl_url(url)
                    if page_data and url in url_snapshots:
                        previous = url_snapshots[url]
                        current_hash = page_data.content_hash
                        
                        if current_hash != previous['content_hash']:
                            # Content changed
                            change_info = {
                                'url': url,
                                'change_type': 'content_modified',
                                'previous_hash': previous['content_hash'],
                                'current_hash': current_hash,
                                'previous_title': previous['title'],
                                'current_title': page_data.title,
                                'previous_word_count': previous['word_count'],
                                'current_word_count': page_data.word_count,
                                'detected_at': datetime.now(),
                                'last_checked': previous['last_checked']
                            }
                            
                            yield change_info
                            
                            # Update snapshot
                            url_snapshots[url] = {
                                'content_hash': current_hash,
                                'last_modified': page_data.last_modified,
                                'title': page_data.title,
                                'word_count': page_data.word_count,
                                'last_checked': datetime.now()
                            }
                    
                except Exception as e:
                    logger.error(f"Error monitoring {url}: {e}")
                    continue
    
    async def _crawl_with_requests(self, url: str) -> Optional[WebPageData]:
        """Crawl URL using requests library"""        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            # Use trafilatura for content extraction
            content = trafilatura.extract(
                response.text,
                include_comments=False,
                include_tables=True,
                include_links=True
            )
            
            if not content:
                # Fallback to BeautifulSoup
                soup = BeautifulSoup(response.text, 'html.parser')
                content = soup.get_text(strip=True)
            
            # Extract metadata
            soup = BeautifulSoup(response.text, 'html.parser')
            
            title = soup.find('title')
            title = title.text.strip() if title else ""
            
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            meta_desc = meta_desc.get('content', '') if meta_desc else ""
            
            meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
            keywords = meta_keywords.get('content', '').split(',') if meta_keywords else []
            keywords = [k.strip() for k in keywords if k.strip()]
            
            # Extract links and media
            links = [urljoin(url, a.get('href', '')) for a in soup.find_all('a', href=True)]
            images = [urljoin(url, img.get('src', '')) for img in soup.find_all('img', src=True)]
            videos = [urljoin(url, video.get('src', '')) for video in soup.find_all('video', src=True)]
            
            # Calculate metrics
            word_count = len(content.split()) if content else 0
            reading_time = max(1, word_count // 200)  # Assume 200 WPM
            content_hash = hashlib.md5(content.encode()).hexdigest()
            
            return WebPageData(
                url=url,
                title=title,
                content=content or "",
                meta_description=meta_desc,
                meta_keywords=keywords,
                headers=dict(response.headers),
                links=links,
                images=images,
                videos=videos,
                author=None,  # Would need additional extraction
                publish_date=None,  # Would need additional extraction
                language=response.headers.get('Content-Language', 'en'),
                content_type=response.headers.get('Content-Type', ''),
                word_count=word_count,
                reading_time=reading_time,
                social_shares={},  # Would need API calls
                seo_score=0.0,  # Would need analysis
                accessibility_score=0.0,  # Would need analysis
                performance_metrics={},  # Would need measurement
                extracted_entities=[],  # Would need NLP
                content_hash=content_hash
            )
            
        except Exception as e:
            logger.error(f"Error crawling with requests: {e}")
            return None
    
    async def _crawl_with_selenium(self, url: str) -> Optional[WebPageData]:
        """Crawl URL using Selenium for JavaScript-heavy sites"""        if not self.driver:
            return None
        
        try:
            self.driver.get(url)
            
            # Wait for page to load
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Wait for additional content to load
            await asyncio.sleep(3)
            
            # Get page source after JavaScript execution
            page_source = self.driver.page_source
            
            # Extract content using trafilatura
            content = trafilatura.extract(
                page_source,
                include_comments=False,
                include_tables=True,
                include_links=True
            )
            
            if not content:
                # Fallback to BeautifulSoup
                soup = BeautifulSoup(page_source, 'html.parser')
                content = soup.get_text(strip=True)
            
            # Extract metadata
            soup = BeautifulSoup(page_source, 'html.parser')
            
            title = soup.find('title')
            title = title.text.strip() if title else ""
            
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            meta_desc = meta_desc.get('content', '') if meta_desc else ""
            
            meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
            keywords = meta_keywords.get('content', '').split(',') if meta_keywords else []
            keywords = [k.strip() for k in keywords if k.strip()]
            
            # Extract links and media
            links = [urljoin(url, a.get('href', '')) for a in soup.find_all('a', href=True)]
            images = [urljoin(url, img.get('src', '')) for img in soup.find_all('img', src=True)]
            videos = [urljoin(url, video.get('src', '')) for video in soup.find_all('video', src=True)]
            
            # Calculate metrics
            word_count = len(content.split()) if content else 0
            reading_time = max(1, word_count // 200)
            content_hash = hashlib.md5(content.encode()).hexdigest()
            
            return WebPageData(
                url=url,
                title=title,
                content=content or "",
                meta_description=meta_desc,
                meta_keywords=keywords,
                headers={},  # Selenium doesn't provide headers
                links=links,
                images=images,
                videos=videos,
                author=None,
                publish_date=None,
                language="en",  # Default
                content_type="text/html",
                word_count=word_count,
                reading_time=reading_time,
                social_shares={},
                seo_score=0.0,
                accessibility_score=0.0,
                performance_metrics={},
                extracted_entities=[],
                content_hash=content_hash
            )
            
        except Exception as e:
            logger.error(f"Error crawling with Selenium: {e}")
            return None
    
    async def _check_robots_txt(self, url: str) -> bool:
        """Check if URL is allowed by robots.txt"""        try:
            parsed_url = urlparse(url)
            base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
            robots_url = urljoin(base_url, '/robots.txt')
            
            if robots_url in self.robots_cache:
                rp = self.robots_cache[robots_url]
            else:
                rp = RobotFileParser()
                rp.set_url(robots_url)
                rp.read()
                self.robots_cache[robots_url] = rp
            
            user_agent = self.session.headers.get('User-Agent', '*')
            return rp.can_fetch(user_agent, url)
            
        except Exception as e:
            logger.warning(f"Error checking robots.txt for {url}: {e}")
            return True  # Allow if unable to check
    
    async def _determine_best_method(self, url: str) -> str:
        """Determine the best crawling method for a URL"""        try:
            # Quick HEAD request to check content type
            response = self.session.head(url, timeout=10)
            content_type = response.headers.get('Content-Type', '').lower()
            
            # Check for JavaScript-heavy indicators
            if 'application/json' in content_type:
                return 'selenium'
            
            # For most HTML content, requests is sufficient
            if 'text/html' in content_type:
                return 'requests'
            
            return 'requests'  # Default
            
        except Exception:
            return 'requests'  # Default fallback
    
    async def _extract_key_phrases(self, content: str) -> List[str]:
        """Extract key phrases from content for searching"""        # Simple implementation - could be enhanced with NLP
        sentences = re.split(r'[.!?]+', content)
        phrases = []
        
        for sentence in sentences[:10]:  # First 10 sentences
            sentence = sentence.strip()
            if len(sentence) > 20 and len(sentence) < 100:
                # Remove common words
                words = sentence.split()
                if len(words) >= 4:
                    phrases.append(sentence)
        
        return phrases[:10]  # Return top 10 phrases
    
    async def _calculate_content_similarity(self, content1: str, content2: str) -> float:
        """Calculate similarity between two pieces of content"""        try:
            # Simple word-based similarity
            words1 = set(content1.lower().split())
            words2 = set(content2.lower().split())
            
            if not words1 or not words2:
                return 0.0
            
            intersection = words1.intersection(words2)
            union = words1.union(words2)
            
            return len(intersection) / len(union)
            
        except Exception:
            return 0.0
    
    async def _classify_match_type(self, similarity_score: float) -> str:
        """Classify the type of content match"""        if similarity_score >= 0.9:
            return "exact"
        elif similarity_score >= 0.7:
            return "partial"
        elif similarity_score >= 0.5:
            return "paraphrased"
        else:
            return "potential"
    
    async def _assess_evidence_strength(self, similarity_score: float) -> str:
        """Assess the strength of plagiarism evidence"""        if similarity_score >= 0.9:
            return "strong"
        elif similarity_score >= 0.7:
            return "moderate"
        elif similarity_score >= 0.5:
            return "weak"
        else:
            return "minimal"
    
    async def _detect_plagiarism_indicators(self, original: str, candidate: str) -> List[str]:
        """Detect specific plagiarism indicators"""        indicators = []
        
        # Check for exact phrase matches
        original_sentences = re.split(r'[.!?]+', original)
        candidate_sentences = re.split(r'[.!?]+', candidate)
        
        for orig_sent in original_sentences:
            orig_sent = orig_sent.strip()
            if len(orig_sent) > 20:
                for cand_sent in candidate_sentences:
                    if orig_sent.lower() in cand_sent.lower():
                        indicators.append("exact_phrase_match")
                        break
        
        # Check for structural similarity
        if len(original.split()) > 0 and len(candidate.split()) > 0:
            length_ratio = len(candidate.split()) / len(original.split())
            if 0.8 <= length_ratio <= 1.2:
                indicators.append("similar_length")
        
        return list(set(indicators))  # Remove duplicates
    
    async def cleanup(self) -> None:
        """Cleanup resources"""        try:
            if hasattr(self, 'driver') and self.driver:
                self.driver.quit()
            if hasattr(self, 'session') and self.session:
                self.session.close()
            await self.cache_manager.cleanup()
            logger.info("Generic web crawler engine cleanup completed")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
    
    def __del__(self):
        """Destructor to ensure cleanup"""        try:
            if hasattr(self, 'driver') and self.driver:
                self.driver.quit()
            if hasattr(self, 'session') and self.session:
                self.session.close()
        except:
            pass


# Export main class
__all__ = ['GenericWebCrawlerEngine', 'WebPageData', 'WebSiteData', 'ContentMatchData']
