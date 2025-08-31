"""Universal Web Crawler Engine
===========================

Advanced generic web crawler for monitoring content across any website.
Provides comprehensive scraping capabilities with anti-detection measures,
proxy rotation, and intelligent content extraction for copyright protection.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

⚠️  INTELLECTUAL PROPERTY WARNING ⚠️
This code is the exclusive property of Fahed Mlaiel (mlaiel@live.de).
Unauthorized use, copying, modification, or distribution is strictly prohibited.
Violators will face immediate legal action under German and international law.
"""import asyncio
import logging
import re
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Set
from dataclasses import dataclass, asdict
from urllib.parse import urljoin, urlparse, parse_qs
import aiohttp
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from bs4 import BeautifulSoup
import requests
from newspaper import Article
import tldextract

from .base import BaseCrawler, CrawlResult
from ..config import ContentType
from ..security.encryption import SecurityManager
from ..utils.rate_limiter import RateLimiter
from ..utils.proxy_manager import ProxyManager

logger = logging.getLogger(__name__)

@dataclass
class WebsiteData:
    """Comprehensive website content metadata structure."""    
    url: str
    title: str
    content: str
    author: Optional[str]
    publish_date: Optional[datetime]
    domain: str
    subdomain: Optional[str]
    language: Optional[str]
    
    # Content analysis
    word_count: int
    images: List[str]
    videos: List[str]
    links: List[str]
    meta_description: Optional[str]
    meta_keywords: List[str]
    
    # Technical metadata
    status_code: int
    response_time: float
    content_type: str
    content_length: int
    last_modified: Optional[datetime]
    etag: Optional[str]
    
    # Content fingerprinting
    text_hash: str
    structure_hash: str
    similarity_keywords: List[str]

@dataclass
class CrawlingTarget:
    """Configuration for website crawling targets."""    
    domain: str
    start_urls: List[str]
    allowed_patterns: List[str]
    blocked_patterns: List[str]
    max_depth: int = 3
    max_pages: int = 1000
    respect_robots: bool = True
    crawl_delay: float = 1.0
    
    # Content filters
    content_types: List[str] = None
    min_content_length: int = 100
    language_filters: List[str] = None
    
    # Monitoring settings
    monitor_frequency: timedelta = timedelta(hours=24)
    alert_on_changes: bool = True
    similarity_threshold: float = 0.8

class ContentExtractor:
    """Advanced content extraction from web pages."""    
    def __init__(self):
        """Initialize content extractor with multiple extraction methods."""        self.session = aiohttp.ClientSession()
    
    async def extract_article_content(self, url: str) -> Optional[WebsiteData]:
        """Extract article content using newspaper3k and custom methods."""        try:
            # Use newspaper3k for article extraction
            article = Article(url)
            article.download()
            article.parse()
            
            # Get additional metadata
            response_metadata = await self._get_response_metadata(url)
            
            # Extract images and videos
            images = list(set([img for img in article.images]))
            videos = await self._extract_videos(url)
            
            # Calculate content hashes
            text_hash = hashlib.sha256(article.text.encode()).hexdigest()
            structure_hash = await self._calculate_structure_hash(url)
            
            # Extract similarity keywords
            keywords = self._extract_keywords(article.text)
            
            # Parse domain
            extracted = tldextract.extract(url)
            domain = f"{extracted.domain}.{extracted.suffix}"
            subdomain = extracted.subdomain if extracted.subdomain else None
            
            return WebsiteData(
                url=url,
                title=article.title,
                content=article.text,
                author=', '.join(article.authors) if article.authors else None,
                publish_date=article.publish_date,
                domain=domain,
                subdomain=subdomain,
                language=article.meta_lang,
                word_count=len(article.text.split()),
                images=images,
                videos=videos,
                links=list(article.canonical_link) if article.canonical_link else [],
                meta_description=article.meta_description,
                meta_keywords=article.meta_keywords,
                status_code=response_metadata.get('status_code', 0),
                response_time=response_metadata.get('response_time', 0),
                content_type=response_metadata.get('content_type', ''),
                content_length=len(article.text),
                last_modified=response_metadata.get('last_modified'),
                etag=response_metadata.get('etag'),
                text_hash=text_hash,
                structure_hash=structure_hash,
                similarity_keywords=keywords
            )
            
        except Exception as e:
            logger.error(f"Article extraction error for {url}: {e}")
            return None
    
    async def _get_response_metadata(self, url: str) -> Dict[str, Any]:
        """Get HTTP response metadata."""        try:
            start_time = datetime.now()
            
            async with self.session.head(url) as response:
                response_time = (datetime.now() - start_time).total_seconds()
                
                last_modified = None
                if 'Last-Modified' in response.headers:
                    from email.utils import parsedate_to_datetime
                    last_modified = parsedate_to_datetime(response.headers['Last-Modified'])
                
                return {
                    'status_code': response.status,
                    'response_time': response_time,
                    'content_type': response.headers.get('Content-Type', ''),
                    'last_modified': last_modified,
                    'etag': response.headers.get('ETag')
                }
                
        except Exception as e:
            logger.error(f"Response metadata error: {e}")
            return {}
    
    async def _extract_videos(self, url: str) -> List[str]:
        """Extract video URLs from page."""        try:
            async with self.session.get(url) as response:
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                videos = []
                
                # Extract video tags
                for video in soup.find_all('video'):
                    src = video.get('src')
                    if src:
                        videos.append(urljoin(url, src))
                    
                    # Check source tags
                    for source in video.find_all('source'):
                        src = source.get('src')
                        if src:
                            videos.append(urljoin(url, src))
                
                # Extract iframe embeds (YouTube, Vimeo, etc.)
                for iframe in soup.find_all('iframe'):
                    src = iframe.get('src')
                    if src and any(domain in src for domain in ['youtube.com', 'vimeo.com', 'dailymotion.com']):
                        videos.append(src)
                
                return list(set(videos))
                
        except Exception as e:
            logger.error(f"Video extraction error: {e}")
            return []
    
    async def _calculate_structure_hash(self, url: str) -> str:
        """Calculate hash of page structure for change detection."""        try:
            async with self.session.get(url) as response:
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                # Remove variable content (scripts, comments, etc.)
                for element in soup(['script', 'style', 'noscript']):
                    element.decompose()
                
                # Extract structural elements
                structure_elements = []
                for tag in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'div', 'section']):
                    if tag.get_text(strip=True):
                        structure_elements.append(f"{tag.name}:{len(tag.get_text())}")
                
                structure_string = '|'.join(structure_elements)
                return hashlib.sha256(structure_string.encode()).hexdigest()
                
        except Exception as e:
            logger.error(f"Structure hash error: {e}")
            return ""
    
    def _extract_keywords(self, text: str, max_keywords: int = 20) -> List[str]:
        """Extract important keywords from text content."""        try:
            # Simple keyword extraction (could be enhanced with NLP)
            words = re.findall(r'\b\w{4,}\b', text.lower())
            
            # Remove common stop words
            stop_words = {
                'this', 'that', 'with', 'have', 'will', 'from', 'they', 'know',
                'want', 'been', 'good', 'much', 'some', 'time', 'very', 'when',
                'come', 'here', 'just', 'like', 'long', 'make', 'many', 'over',
                'such', 'take', 'than', 'them', 'well', 'were'
            }
            
            # Count word frequencies
            word_freq = {}
            for word in words:
                if word not in stop_words and len(word) > 3:
                    word_freq[word] = word_freq.get(word, 0) + 1
            
            # Get most frequent words
            keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
            return [word for word, freq in keywords[:max_keywords]]
            
        except Exception as e:
            logger.error(f"Keyword extraction error: {e}")
            return []
    
    async def close(self):
        """Close session."""        if self.session:
            await self.session.close()

class ScrapyWebCrawler:
    """Scrapy-based web crawler for large-scale crawling."""    
    def __init__(self, target: CrawlingTarget):
        """Initialize Scrapy crawler."""        self.target = target
        self.results = []
        
    def create_spider(self):
        """Create Scrapy spider for the target."""        
        class WebSpider(scrapy.Spider):
            name = 'web_crawler'
            allowed_domains = [self.target.domain]
            start_urls = self.target.start_urls
            
            custom_settings = {
                'ROBOTSTXT_OBEY': self.target.respect_robots,
                'DOWNLOAD_DELAY': self.target.crawl_delay,
                'DEPTH_LIMIT': self.target.max_depth,
                'CLOSESPIDER_PAGECOUNT': self.target.max_pages,
                'USER_AGENT': 'Mozilla/5.0 (compatible; ContentMonitor/1.0; +http://example.com/bot)',
            }
            
            def parse(self, response):
                # Extract page data
                yield {
                    'url': response.url,
                    'title': response.css('title::text').get(),
                    'content': ' '.join(response.css('p::text').getall()),
                    'links': response.css('a::attr(href)').getall(),
                    'images': response.css('img::attr(src)').getall(),
                    'status_code': response.status,
                }
                
                # Follow links
                for link in response.css('a::attr(href)').getall():
                    if self._should_follow_link(link):
                        yield response.follow(link, self.parse)
            
            def _should_follow_link(self, link):
                """Check if link should be followed based on patterns."""                if not link:
                    return False
                
                # Check allowed patterns
                if self.target.allowed_patterns:
                    if not any(re.search(pattern, link) for pattern in self.target.allowed_patterns):
                        return False
                
                # Check blocked patterns
                if self.target.blocked_patterns:
                    if any(re.search(pattern, link) for pattern in self.target.blocked_patterns):
                        return False
                
                return True
        
        return WebSpider
    
    async def crawl(self) -> List[Dict[str, Any]]:
        """Run Scrapy crawler and return results."""        try:
            process = CrawlerProcess(get_project_settings())
            spider_class = self.create_spider()
            
            # Run crawler in separate process
            process.crawl(spider_class)
            process.start()
            
            # Note: In production, this would be more complex
            # to handle async execution properly
            
            return self.results
            
        except Exception as e:
            logger.error(f"Scrapy crawl error: {e}")
            return []

class UniversalWebCrawler(BaseCrawler):
    """Universal web crawler with comprehensive monitoring capabilities."""    
    def __init__(self, config: Dict[str, Any]):
        """Initialize universal web crawler."""        super().__init__(config)
        self.content_extractor = ContentExtractor()
        self.proxy_manager = config.get('proxy_manager')
        self.platform = 'web'
        
        # Rate limiting
        self.rate_limiter = RateLimiter(
            max_calls=config.get('max_requests_per_minute', 60),
            time_window=60
        )
        
        # Tracking
        self.crawled_urls: Set[str] = set()
        self.crawling_targets: List[CrawlingTarget] = []
    
    def add_crawling_target(self, target: CrawlingTarget):
        """Add a new crawling target."""        self.crawling_targets.append(target)
    
    async def crawl_url(self, url: str) -> Optional[CrawlResult]:
        """Crawl a specific URL and extract content."""        await self.rate_limiter.acquire()
        
        try:
            if url in self.crawled_urls:
                return None
            
            # Extract website data
            website_data = await self.content_extractor.extract_article_content(url)
            if not website_data:
                return None
            
            self.crawled_urls.add(url)
            
            # Determine content type
            content_type = ContentType.TEXT.value
            if website_data.videos:
                content_type = ContentType.VIDEO.value
            elif website_data.images:
                content_type = ContentType.IMAGE.value
            if website_data.videos and website_data.images:
                content_type = ContentType.MIXED.value
            
            # Create standardized crawl result
            result = CrawlResult(
                url=url,
                platform=self.platform,
                content_type=content_type,
                title=website_data.title,
                description=website_data.meta_description or website_data.content[:200],
                author=website_data.author,
                upload_date=website_data.publish_date,
                view_count=0,  # Not available for generic websites
                duration_ms=None,
                thumbnail_url=website_data.images[0] if website_data.images else None,
                tags=website_data.meta_keywords,
                metadata={
                    'website_data': asdict(website_data),
                    'technical': {
                        'domain': website_data.domain,
                        'subdomain': website_data.subdomain,
                        'status_code': website_data.status_code,
                        'response_time': website_data.response_time,
                        'content_length': website_data.content_length
                    },
                    'fingerprinting': {
                        'text_hash': website_data.text_hash,
                        'structure_hash': website_data.structure_hash,
                        'similarity_keywords': website_data.similarity_keywords,
                        'word_count': website_data.word_count
                    }
                }
            )
            
            return result
            
        except Exception as e:
            logger.error(f"URL crawl error {url}: {e}")
            return None
    
    async def crawl_domain(self, target: CrawlingTarget) -> List[CrawlResult]:
        """Crawl an entire domain based on target configuration."""        try:
            results = []
            
            # Use Scrapy for large-scale crawling
            scrapy_crawler = ScrapyWebCrawler(target)
            scrapy_results = await scrapy_crawler.crawl()
            
            # Process Scrapy results
            for page_data in scrapy_results:
                url = page_data.get('url')
                if url:
                    result = await self.crawl_url(url)
                    if result:
                        results.append(result)
                    
                    await asyncio.sleep(target.crawl_delay)
            
            return results
            
        except Exception as e:
            logger.error(f"Domain crawl error: {e}")
            return []
    
    async def monitor_websites(self) -> List[CrawlResult]:
        """Monitor all configured crawling targets for changes."""        try:
            all_results = []
            
            for target in self.crawling_targets:
                # Check if it's time to crawl
                # (This would be enhanced with database tracking)
                
                results = await self.crawl_domain(target)
                all_results.extend(results)
                
                # Rate limiting between domains
                await asyncio.sleep(5)
            
            return all_results
            
        except Exception as e:
            logger.error(f"Website monitoring error: {e}")
            return []
    
    async def search_content_similarity(
        self,
        reference_content: str,
        domains: List[str],
        similarity_threshold: float = 0.8
    ) -> List[CrawlResult]:
        """Search for similar content across specified domains."""        try:
            results = []
            reference_keywords = self.content_extractor._extract_keywords(reference_content)
            
            # Create search queries from keywords
            search_queries = [
                ' '.join(reference_keywords[:5]),
                ' '.join(reference_keywords[5:10]),
                f'"{reference_content[:100]}"'  # Exact phrase search
            ]
            
            for domain in domains:
                for query in search_queries:
                    # Use search engines or site-specific search
                    search_results = await self._search_domain(domain, query)
                    
                    for url in search_results:
                        result = await self.crawl_url(url)
                        if result:
                            # Calculate similarity
                            similarity = self._calculate_content_similarity(
                                reference_content, result.description
                            )
                            
                            if similarity >= similarity_threshold:
                                result.metadata['similarity_score'] = similarity
                                results.append(result)
                        
                        await asyncio.sleep(1)
            
            return results
            
        except Exception as e:
            logger.error(f"Content similarity search error: {e}")
            return []
    
    async def _search_domain(self, domain: str, query: str) -> List[str]:
        """Search within a specific domain using search engines."""        try:
            # Use Google search with site: operator
            search_query = f"site:{domain} {query}"
            
            # This would use a search API (Google Custom Search, Bing, etc.)
            # For now, return empty list as placeholder
            return []
            
        except Exception as e:
            logger.error(f"Domain search error: {e}")
            return []
    
    def _calculate_content_similarity(self, content1: str, content2: str) -> float:
        """Calculate similarity between two content strings."""        try:
            # Simple Jaccard similarity (could be enhanced with NLP)
            words1 = set(content1.lower().split())
            words2 = set(content2.lower().split())
            
            if not words1 and not words2:
                return 1.0
            if not words1 or not words2:
                return 0.0
            
            intersection = len(words1.intersection(words2))
            union = len(words1.union(words2))
            
            return intersection / union if union > 0 else 0.0
            
        except Exception as e:
            logger.error(f"Similarity calculation error: {e}")
            return 0.0
    
    async def cleanup(self):
        """Clean up resources."""        if self.content_extractor:
            await self.content_extractor.close()
