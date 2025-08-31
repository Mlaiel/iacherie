"""
 Generic Web Crawler
======================

Professional generic web crawling system using Scrapy framework.
Advanced content discovery for any website with intelligent parsing.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

 STRICT WARNING: Unauthorized use, copying, or distribution of this code 
is strictly prohibited without explicit written permission from Fahed Mlaiel.
Contact: mlaiel@live.de for licensing and authorization.
"""

import asyncio
import logging
import re
import json
import time
from typing import Dict, List, Optional, Any, Union, Set
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from urllib.parse import urljoin, urlparse, urlunparse
from urllib.robotparser import RobotFileParser
import requests
from bs4 import BeautifulSoup
import scrapy
from scrapy.crawler import CrawlerRunner, CrawlerProcess
from scrapy.utils.project import get_project_settings
from scrapy.http import Request, Response
from scrapy.spiders import Spider, CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.exceptions import IgnoreRequest
import hashlib
import mimetypes

from .base_crawler import BasePlatformCrawler, CrawlResult, CrawlerStatus

logger = logging.getLogger(__name__)

@dataclass
class WebPageInfo:
    """Web page information structure."""
    url: str
    title: str
    description: str
    content: str
    content_type: str
    file_size: Optional[int] = None
    last_modified: Optional[datetime] = None
    crawled_at: datetime = None
    status_code: int = 200
    headers: Dict[str, str] = None
    links: List[str] = None
    images: List[str] = None
    videos: List[str] = None
    audio: List[str] = None
    documents: List[str] = None
    metadata: Dict[str, Any] = None

@dataclass
class CrawlConfig:
    """Crawling configuration structure."""
    allowed_domains: List[str]
    start_urls: List[str]
    max_depth: int = 3
    max_pages: int = 1000
    delay: float = 1.0
    concurrent_requests: int = 16
    respect_robots_txt: bool = True
    user_agent: str = 'IA-Influencer-Agent/1.0'
    custom_headers: Dict[str, str] = None
    follow_redirects: bool = True
    max_redirect_times: int = 20
    download_timeout: int = 180
    content_types: List[str] = None  # MIME types to crawl
    file_extensions: List[str] = None  # File extensions to crawl

class ContentAnalyzer:
    """Intelligent content analysis and extraction."""
    
    @staticmethod
    def extract_metadata(soup: BeautifulSoup, url: str) -> Dict[str, Any]:
        """Extract comprehensive metadata from HTML."""
        metadata = {}
        
        try:
            # Basic meta tags
            meta_tags = soup.find_all('meta')
            for tag in meta_tags:
                name = tag.get('name') or tag.get('property') or tag.get('http-equiv')
                content = tag.get('content')
                
                if name and content:
                    metadata[name.lower()] = content
            
            # OpenGraph metadata
            og_data = {}
            for tag in meta_tags:
                property_name = tag.get('property', '')
                if property_name.startswith('og:'):
                    og_data[property_name] = tag.get('content', '')
            
            if og_data:
                metadata['opengraph'] = og_data
            
            # Twitter Card metadata
            twitter_data = {}
            for tag in meta_tags:
                name = tag.get('name', '')
                if name.startswith('twitter:'):
                    twitter_data[name] = tag.get('content', '')
            
            if twitter_data:
                metadata['twitter'] = twitter_data
            
            # JSON-LD structured data
            json_ld_scripts = soup.find_all('script', {'type': 'application/ld+json'})
            json_ld_data = []
            
            for script in json_ld_scripts:
                try:
                    data = json.loads(script.string)
                    json_ld_data.append(data)
                except (json.JSONDecodeError, TypeError):
                    continue
            
            if json_ld_data:
                metadata['json_ld'] = json_ld_data
            
            # Microdata
            microdata = ContentAnalyzer._extract_microdata(soup)
            if microdata:
                metadata['microdata'] = microdata
            
            # Language detection
            html_tag = soup.find('html')
            if html_tag:
                lang = html_tag.get('lang')
                if lang:
                    metadata['language'] = lang
            
            # Canonical URL
            canonical_link = soup.find('link', {'rel': 'canonical'})
            if canonical_link:
                metadata['canonical_url'] = canonical_link.get('href')
            
            # Author information
            author_meta = soup.find('meta', {'name': 'author'})
            if author_meta:
                metadata['author'] = author_meta.get('content')
            
            # Publication date
            date_meta = soup.find('meta', {'name': 'date'}) or soup.find('meta', {'property': 'article:published_time'})
            if date_meta:
                metadata['published_date'] = date_meta.get('content')
            
        except Exception as e:
            logger.error(f"Error extracting metadata: {e}")
        
        return metadata
    
    @staticmethod
    def _extract_microdata(soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract microdata from HTML."""
        microdata_items = []
        
        items = soup.find_all(attrs={'itemscope': True})
        for item in items:
            item_data = {'type': item.get('itemtype')}
            properties = {}
            
            # Find all properties within this item
            props = item.find_all(attrs={'itemprop': True})
            for prop in props:
                prop_name = prop.get('itemprop')
                
                # Get property value
                if prop.name in ['meta']:
                    prop_value = prop.get('content')
                elif prop.name in ['time']:
                    prop_value = prop.get('datetime')
                elif prop.name in ['a', 'link']:
                    prop_value = prop.get('href')
                elif prop.name in ['img']:
                    prop_value = prop.get('src')
                else:
                    prop_value = prop.get_text().strip()
                
                properties[prop_name] = prop_value
            
            item_data['properties'] = properties
            microdata_items.append(item_data)
        
        return microdata_items
    
    @staticmethod
    def extract_media_urls(soup: BeautifulSoup, base_url: str) -> Dict[str, List[str]]:
        """Extract media URLs from HTML."""
        media_urls = {
            'images': [],
            'videos': [],
            'audio': [],
            'documents': []
        }
        
        try:
            # Images
            for img in soup.find_all('img'):
                src = img.get('src') or img.get('data-src')
                if src:
                    full_url = urljoin(base_url, src)
                    media_urls['images'].append(full_url)
            
            # Videos
            for video in soup.find_all('video'):
                src = video.get('src')
                if src:
                    full_url = urljoin(base_url, src)
                    media_urls['videos'].append(full_url)
                
                # Video sources
                for source in video.find_all('source'):
                    src = source.get('src')
                    if src:
                        full_url = urljoin(base_url, src)
                        media_urls['videos'].append(full_url)
            
            # Audio
            for audio in soup.find_all('audio'):
                src = audio.get('src')
                if src:
                    full_url = urljoin(base_url, src)
                    media_urls['audio'].append(full_url)
                
                # Audio sources
                for source in audio.find_all('source'):
                    src = source.get('src')
                    if src:
                        full_url = urljoin(base_url, src)
                        media_urls['audio'].append(full_url)
            
            # Documents (links to common document formats)
            doc_extensions = ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.txt', '.rtf']
            
            for link in soup.find_all('a'):
                href = link.get('href')
                if href:
                    full_url = urljoin(base_url, href)
                    parsed_url = urlparse(full_url)
                    
                    if any(parsed_url.path.lower().endswith(ext) for ext in doc_extensions):
                        media_urls['documents'].append(full_url)
        
        except Exception as e:
            logger.error(f"Error extracting media URLs: {e}")
        
        return media_urls
    
    @staticmethod
    def detect_content_type(soup: BeautifulSoup, url: str) -> str:
        """Detect content type based on page structure and content."""



        try:
            # Check for video platforms
            if any(domain in url for domain in ['youtube.com', 'vimeo.com', 'dailymotion.com']):
                return 'video'
            
            # Check for audio platforms
            if any(domain in url for domain in ['soundcloud.com', 'spotify.com', 'bandcamp.com']):
                return 'audio'
            
            # Check for image platforms
            if any(domain in url for domain in ['instagram.com', 'flickr.com', 'pinterest.com']):
                return 'image'
            
            # Check for blog/article indicators
            article_indicators = [
                'article', 'blog', 'post', 'news', 'story',
                '.article', '.blog-post', '.news-article'
            ]
            
            for indicator in article_indicators:
                if soup.find(class_=indicator) or soup.find(id=indicator) or soup.find(indicator):
                    return 'article'
            
            # Check for e-commerce indicators
            ecommerce_indicators = ['product', 'shop', 'cart', 'price']
            for indicator in ecommerce_indicators:
                if soup.find(class_=indicator) or soup.find(id=indicator):
                    return 'product'
            
            # Check for media content
            if soup.find('video') or soup.find('embed'):
                return 'video'
            
            if soup.find('audio'):
                return 'audio'
            
            # Check image galleries
            img_tags = soup.find_all('img')
            if len(img_tags) > 5:  # Threshold for image gallery
                return 'gallery'
            
            # Default to webpage
            return 'webpage'
            
        except Exception as e:
            logger.error(f"Error detecting content type: {e}")
            return 'webpage'

class GenericSpider(scrapy.Spider):
    """Generic Scrapy spider for web crawling."""
    
    name = 'generic_spider'
    
    def __init__(self, crawl_config: CrawlConfig, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.crawl_config = crawl_config
        self.allowed_domains = crawl_config.allowed_domains
        self.start_urls = crawl_config.start_urls
        
        # Statistics
        self.pages_crawled = 0
        self.errors_encountered = 0
        self.results = []
        
        # Content analyzer
        self.content_analyzer = ContentAnalyzer()
    
    def parse(self, response: Response):
        """Parse web page response."""



        try:
            # Update statistics
            self.pages_crawled += 1
            
            # Create BeautifulSoup object for parsing
            soup = BeautifulSoup(response.body, 'html.parser')
            
            # Extract page information
            page_info = self._extract_page_info(response, soup)
            
            # Add to results
            self.results.append(page_info)
            
            # Extract links for further crawling
            if self.pages_crawled < self.crawl_config.max_pages:
                for link in self._extract_links(response, soup):
                    yield scrapy.Request(url=link, callback=self.parse)
            
            # Yield the page information
            yield page_info
            
        except Exception as e:
            logger.error(f"Error parsing {response.url}: {e}")
            self.errors_encountered += 1
    
    def _extract_page_info(self, response: Response, soup: BeautifulSoup) -> WebPageInfo:
        """Extract comprehensive page information."""
        url = response.url
        
        # Basic information
        title = ""
        title_tag = soup.find('title')
        if title_tag:
            title = title_tag.get_text().strip()
        
        # Description
        description = ""
        desc_meta = soup.find('meta', {'name': 'description'}) or soup.find('meta', {'property': 'og:description'})
        if desc_meta:
            description = desc_meta.get('content', '')
        
        # Extract text content
        content = self._extract_text_content(soup)
        
        # Detect content type
        content_type = self.content_analyzer.detect_content_type(soup, url)
        
        # Extract metadata
        metadata = self.content_analyzer.extract_metadata(soup, url)
        
        # Extract media URLs
        media_urls = self.content_analyzer.extract_media_urls(soup, url)
        
        # Extract all links
        all_links = [urljoin(url, link.get('href')) for link in soup.find_all('a', href=True)]
        
        return WebPageInfo(
            url=url,
            title=title,
            description=description,
            content=content,
            content_type=content_type,
            crawled_at=datetime.utcnow(),
            status_code=response.status,
            headers=dict(response.headers),
            links=all_links,
            images=media_urls['images'],
            videos=media_urls['videos'],
            audio=media_urls['audio'],
            documents=media_urls['documents'],
            metadata=metadata
        )
    
    def _extract_text_content(self, soup: BeautifulSoup) -> str:
        """Extract clean text content from HTML."""



        try:
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Get text
            text = soup.get_text()
            
            # Clean up text
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            return text
            
        except Exception as e:
            logger.error(f"Error extracting text content: {e}")
            return ""
    
    def _extract_links(self, response: Response, soup: BeautifulSoup) -> List[str]:
        """Extract valid links for further crawling."""
        links = []
        
        try:
            for link_tag in soup.find_all('a', href=True):
                href = link_tag.get('href')
                if href:
                    full_url = urljoin(response.url, href)
                    parsed_url = urlparse(full_url)
                    
                    # Filter links
                    if (parsed_url.netloc in self.allowed_domains and
                        self._is_valid_link(full_url)):
                        links.append(full_url)
            
        except Exception as e:
            logger.error(f"Error extracting links: {e}")
        
        return links
    
    def _is_valid_link(self, url: str) -> bool:
        """Check if link is valid for crawling."""



        try:
            parsed_url = urlparse(url)
            
            # Skip fragments and javascript links
            if parsed_url.fragment or url.startswith('javascript:'):
                return False
            
            # Skip common non-content file extensions
            skip_extensions = [
                '.css', '.js', '.ico', '.png', '.jpg', '.jpeg', '.gif',
                '.svg', '.woff', '.woff2', '.ttf', '.eot'
            ]
            
            if any(parsed_url.path.lower().endswith(ext) for ext in skip_extensions):
                return False
            
            return True
            
        except Exception:
            return False

class RobotsTxtChecker:
    """Robots.txt compliance checker."""
    
    def __init__(self):
        self.robots_cache = {}
        self.cache_timeout = timedelta(hours=24)
    
    def can_fetch(self, url: str, user_agent: str = '*') -> bool:
        """Check if URL can be fetched according to robots.txt."""



        try:
            parsed_url = urlparse(url)
            robots_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"
            
            # Check cache
            if robots_url in self.robots_cache:
                cached_data = self.robots_cache[robots_url]
                if datetime.utcnow() - cached_data['timestamp'] < self.cache_timeout:
                    return cached_data['parser'].can_fetch(user_agent, url)
            
            # Fetch and parse robots.txt
            rp = RobotFileParser()
            rp.set_url(robots_url)
            
            try:
                rp.read()
                self.robots_cache[robots_url] = {
                    'parser': rp,
                    'timestamp': datetime.utcnow()
                }
                return rp.can_fetch(user_agent, url)
            except:
                # If robots.txt cannot be fetched, assume allowed
                return True
            
        except Exception as e:
            logger.error(f"Error checking robots.txt for {url}: {e}")
            return True

class GenericWebCrawler(BasePlatformCrawler):
    """
    Professional Generic Web Crawler
    ================================
    
    Advanced web crawling system featuring:
    - Scrapy-based distributed crawling
    - Intelligent content analysis and extraction
    - Robots.txt compliance
    - Multi-format content detection
    - Metadata extraction (OpenGraph, JSON-LD, Microdata)
    - Media content discovery
    - Rate limiting and politeness policies
    - Content deduplication
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize generic web crawler."""
        super().__init__("web", config)
        
        # Crawling configuration
        self.max_depth = config.get('max_depth', 3)
        self.max_pages = config.get('max_pages', 1000)
        self.delay = config.get('delay', 1.0)
        self.concurrent_requests = config.get('concurrent_requests', 16)
        self.respect_robots_txt = config.get('respect_robots_txt', True)
        self.user_agent = config.get('user_agent', 'IA-Influencer-Agent/1.0')
        
        # Content filtering
        self.allowed_content_types = config.get('content_types', [
            'text/html', 'application/pdf', 'text/plain'
        ])
        self.allowed_extensions = config.get('file_extensions', [
            '.html', '.htm', '.pdf', '.txt', '.doc', '.docx'
        ])
        
        # Initialize components
        self.robots_checker = RobotsTxtChecker()
        self.content_analyzer = ContentAnalyzer()
        self.crawled_urls = set()
        
        # Scrapy settings
        self.scrapy_settings = self._get_scrapy_settings()
        
        logger.info("Generic web crawler initialized")
    
    def _get_scrapy_settings(self) -> Dict[str, Any]:
        """Get Scrapy settings for crawling."""



        return {
            'USER_AGENT': self.user_agent,
            'ROBOTSTXT_OBEY': self.respect_robots_txt,
            'DOWNLOAD_DELAY': self.delay,
            'CONCURRENT_REQUESTS': self.concurrent_requests,
            'CONCURRENT_REQUESTS_PER_DOMAIN': 8,
            'DEPTH_LIMIT': self.max_depth,
            'DOWNLOAD_TIMEOUT': 180,
            'RETRY_TIMES': 3,
            'REDIRECT_MAX_TIMES': 20,
            'DUPEFILTER_CLASS': 'scrapy.dupefilters.RFPDupeFilter',
            'LOG_LEVEL': 'INFO'
        }
    
    async def search_content(
        self,
        query: str,
        content_type: str = 'all',
        max_results: int = 50,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[CrawlResult]:
        """
        Search for content using web crawling.
        
        For generic web crawler, 'query' should be a domain or URL pattern.
        """
        if not query:
            return []
        
        try:
            # Parse query as URL or domain
            if not query.startswith(('http://', 'https://')):
                query = f"https://{query}"
            
            parsed_url = urlparse(query)
            domain = parsed_url.netloc
            
            # Create crawl configuration
            crawl_config = CrawlConfig(
                allowed_domains=[domain],
                start_urls=[query],
                max_depth=filters.get('max_depth', self.max_depth) if filters else self.max_depth,
                max_pages=min(max_results, self.max_pages),
                delay=self.delay,
                concurrent_requests=self.concurrent_requests,
                respect_robots_txt=self.respect_robots_txt,
                user_agent=self.user_agent
            )
            
            # Execute crawling
            pages = await self._crawl_website(crawl_config)
            
            # Convert to CrawlResult format
            results = await self._convert_pages_to_results(pages, content_type)
            
            logger.info(f"Web crawl of {domain} returned {len(results)} results")
            return results[:max_results]
            
        except Exception as e:
            logger.error(f"Web crawling error: {e}")
            return []
    
    async def _crawl_website(self, crawl_config: CrawlConfig) -> List[WebPageInfo]:
        """Execute website crawling using Scrapy."""
        results = []
        
        try:
            # Create Scrapy runner
            settings = get_project_settings()
            settings.update(self.scrapy_settings)
            
            runner = CrawlerRunner(settings)
            
            # Create and run spider
            spider = GenericSpider(crawl_config)
            
            # Run in event loop
            deferred = runner.crawl(spider)
            
            # Wait for completion
            await self._wait_for_crawler(deferred)
            
            # Get results from spider
            results = spider.results
            
            # Update statistics
            self._update_stats(True)
            
        except Exception as e:
            logger.error(f"Scrapy crawling error: {e}")
            self._update_stats(False)
        
        return results
    
    async def _wait_for_crawler(self, deferred):
        """Wait for Scrapy crawler to complete."""
        # This is a simplified implementation
        # In a real implementation, you would properly handle Twisted deferreds
        try:
            # Wait for crawler completion (simplified)
            await asyncio.sleep(1)  # Minimal wait
            
            # Check if crawler is done
            max_wait = 300  # 5 minutes max
            waited = 0
            
            while waited < max_wait:
                if deferred.called:
                    break
                await asyncio.sleep(1)
                waited += 1
            
        except Exception as e:
            logger.error(f"Error waiting for crawler: {e}")
    
    async def _convert_pages_to_results(
        self,
        pages: List[WebPageInfo],
        content_type_filter: str
    ) -> List[CrawlResult]:
        """Convert web pages to CrawlResult format."""
        results = []
        
        for page in pages:
            try:
                # Apply content type filter
                if content_type_filter != 'all' and page.content_type != content_type_filter:
                    continue
                
                # Generate fingerprint candidates
                fingerprint_candidates = [
                    page.url,
                    page.title or '',
                    page.description or ''
                ]
                
                # Add metadata-based candidates
                if page.metadata:
                    if 'author' in page.metadata:
                        fingerprint_candidates.append(page.metadata['author'])
                    
                    if 'keywords' in page.metadata:
                        fingerprint_candidates.append(page.metadata['keywords'])
                
                # Clean and deduplicate candidates
                fingerprint_candidates = list(filter(None, set(fingerprint_candidates)))
                
                result = CrawlResult(
                    platform="web",
                    url=page.url,
                    title=page.title,
                    description=page.description,
                    content_type=page.content_type,
                    file_url=page.url,
                    metadata={
                        'crawled_at': page.crawled_at.isoformat(),
                        'status_code': page.status_code,
                        'content_length': len(page.content) if page.content else 0,
                        'last_modified': page.last_modified.isoformat() if page.last_modified else None,
                        'links_count': len(page.links or []),
                        'images_count': len(page.images or []),
                        'videos_count': len(page.videos or []),
                        'audio_count': len(page.audio or []),
                        'documents_count': len(page.documents or []),
                        'links': page.links or [],
                        'images': page.images or [],
                        'videos': page.videos or [],
                        'audio': page.audio or [],
                        'documents': page.documents or [],
                        'headers': page.headers or {},
                        **(page.metadata or {})
                    },
                    discovered_at=datetime.utcnow(),
                    fingerprint_candidates=fingerprint_candidates
                )
                
                results.append(result)
                
            except Exception as e:
                logger.error(f"Error converting page to result: {e}")
                continue
        
        return results
    
    async def crawl_domain(
        self,
        domain: str,
        max_pages: int = 100,
        max_depth: int = 3
    ) -> List[CrawlResult]:
        """Crawl an entire domain."""
        start_url = f"https://{domain}" if not domain.startswith(('http://', 'https://')) else domain
        
        return await self.search_content(
            query=start_url,
            max_results=max_pages,
            filters={'max_depth': max_depth}
        )
    
    async def crawl_sitemap(self, sitemap_url: str) -> List[CrawlResult]:
        """Crawl URLs from a sitemap."""



        try:
            # Fetch sitemap
            response = requests.get(sitemap_url, timeout=30)
            response.raise_for_status()
            
            # Parse sitemap XML
            soup = BeautifulSoup(response.content, 'xml')
            
            # Extract URLs
            urls = []
            for loc in soup.find_all('loc'):
                url = loc.get_text().strip()
                if url:
                    urls.append(url)
            
            # Crawl each URL
            results = []
            for url in urls[:100]:  # Limit to 100 URLs
                try:
                    url_results = await self.search_content(url, max_results=1)
                    results.extend(url_results)
                except Exception as e:
                    logger.error(f"Error crawling sitemap URL {url}: {e}")
                    continue
            
            logger.info(f"Crawled {len(results)} pages from sitemap {sitemap_url}")
            return results
            
        except Exception as e:
            logger.error(f"Error crawling sitemap {sitemap_url}: {e}")
            return []
    
    async def check_rate_limits(self) -> bool:
        """Check if crawler is within rate limits."""
        # Generic web crawler uses delay-based rate limiting
        return True
    
    async def get_crawler_stats(self) -> Dict[str, Any]:
        """Get crawler statistics."""



        return {
            "platform": "web",
            "crawled_urls": len(self.crawled_urls),
            "active_monitoring": len(self.monitoring_tasks),
            "max_depth": self.max_depth,
            "max_pages": self.max_pages,
            "delay": self.delay,
            "respect_robots_txt": self.respect_robots_txt,
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "failed_requests": self.failed_requests
        }
    
    def cleanup(self):
        """Cleanup crawler resources."""
        self.crawled_urls.clear()
        
        # Cancel monitoring tasks
        for task in self.monitoring_tasks.values():
            task.cancel()
        self.monitoring_tasks.clear()
        
        logger.info("Generic web crawler cleanup completed")

# Export main classes
__all__ = [
    'GenericWebCrawler',
    'GenericSpider',
    'ContentAnalyzer',
    'WebPageInfo',
    'CrawlConfig',
    'RobotsTxtChecker'
]
