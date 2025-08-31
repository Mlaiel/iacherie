"""Generic Web Crawler
===================

Professional generic web crawler for content monitoring across any website.
Implements advanced scraping techniques with intelligent content detection.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

WARNING: This code is protected by copyright law. Any unauthorized copying, 
distribution, or modification is strictly prohibited and will result in 
legal action. Contact mlaiel@live.de for licensing.
"""import asyncio
import logging
from typing import Dict, List, Optional, Union, AsyncGenerator
from datetime import datetime, timedelta
from dataclasses import dataclass
import json
import re
from urllib.parse import urljoin, urlparse, parse_qs
import hashlib

import aiohttp
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests_html

from ..utils.rate_limiter import GenericRateLimiter
from ..utils.proxy_manager import ProxyManager
from ..utils.user_agent_rotator import UserAgentRotator
from ..utils.content_extractor import ContentExtractor
from ...core.config import get_settings
from ...core.exceptions import CrawlerError, RateLimitError
from ...database.models import CrawlResult, ContentMatch

logger = logging.getLogger(__name__)
settings = get_settings()

@dataclass
class WebContent:
    """Generic web content data structure."""    url: str
    title: str
    content: str
    description: str
    author: Optional[str]
    published_date: Optional[datetime]
    modified_date: Optional[datetime]
    tags: List[str]
    images: List[Dict]
    videos: List[Dict]
    links: List[Dict]
    social_shares: Dict
    metadata: Dict
    content_type: str
    language: str
    content_hash: str

@dataclass
class SiteMap:
    """Website sitemap structure."""    domain: str
    pages: List[str]
    last_crawled: datetime
    total_pages: int
    crawlable_pages: int
    robots_allowed: List[str]
    robots_disallowed: List[str]

class GenericWebCrawler:
    """    Professional generic web crawler implementation.
    
    Features:
    - Universal content extraction
    - Respect for robots.txt
    - Advanced rate limiting
    - Content deduplication
    - Multiple scraping methods
    - JavaScript rendering support
    - Content similarity detection
    - SEO metadata extraction
    - Social media integration detection
    """    
    def __init__(self):
        """Initialize generic web crawler."""        self.rate_limiter = GenericRateLimiter()
        self.proxy_manager = ProxyManager()
        self.user_agent_rotator = UserAgentRotator()
        self.content_extractor = ContentExtractor()
        self.session = None
        
        # Crawler configuration
        self.max_redirects = 5
        self.timeout = 30
        self.max_content_size = 10 * 1024 * 1024  # 10MB
        
        # Content type patterns
        self.content_patterns = {
            'article': [
                'article', '.article', '#article', '.post', '.content',
                '.entry', '.story', 'main', '[role="main"]'
            ],
            'title': [
                'h1', '.title', '.headline', '.post-title', 'title',
                '[property="og:title"]', '[name="twitter:title"]'
            ],
            'description': [
                '.description', '.excerpt', '.summary', '.lead',
                '[name="description"]', '[property="og:description"]'
            ],
            'author': [
                '.author', '.byline', '.writer', '[rel="author"]',
                '[property="article:author"]', '.post-author'
            ],
            'date': [
                '.date', '.published', '.timestamp', 'time',
                '[datetime]', '[property="article:published_time"]'
            ]
        }
        
        # Selenium configuration
        self.selenium_options = webdriver.ChromeOptions()
        self.selenium_options.add_argument('--headless')
        self.selenium_options.add_argument('--no-sandbox')
        self.selenium_options.add_argument('--disable-dev-shm-usage')
        self.selenium_options.add_argument('--disable-gpu')
        self.selenium_options.add_argument('--disable-blink-features=AutomationControlled')
    
    async def __aenter__(self):
        """Async context manager entry."""        headers = {
            'User-Agent': self.user_agent_rotator.get_user_agent(),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        connector = aiohttp.TCPConnector(limit=100, limit_per_host=10)
        timeout = aiohttp.ClientTimeout(total=self.timeout)
        
        self.session = aiohttp.ClientSession(
            headers=headers,
            connector=connector,
            timeout=timeout
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""        if self.session:
            await self.session.close()
    
    async def crawl_url(self, url: str, method: str = 'auto') -> Optional[WebContent]:
        """        Crawl a single URL and extract content.
        
        Args:
            url: URL to crawl
            method: Crawling method ('requests', 'selenium', 'requests_html', 'auto')
            
        Returns:
            WebContent object or None if failed
        """        try:
            # Check rate limiting
            domain = urlparse(url).netloc
            await self.rate_limiter.wait_if_needed(domain)
            
            # Check robots.txt
            if not await self._check_robots_allowed(url):
                logger.warning(f"URL blocked by robots.txt: {url}")
                return None
            
            # Choose crawling method
            if method == 'auto':
                method = await self._determine_best_method(url)
            
            # Crawl content
            content = None
            if method == 'requests':
                content = await self._crawl_with_requests(url)
            elif method == 'selenium':
                content = await self._crawl_with_selenium(url)
            elif method == 'requests_html':
                content = await self._crawl_with_requests_html(url)
            
            # Update rate limiter
            await self.rate_limiter.update_usage(domain, 1)
            
            return content
            
        except Exception as e:
            logger.error(f"Failed to crawl URL {url}: {e}")
            return None
    
    async def _crawl_with_requests(self, url: str) -> Optional[WebContent]:
        """Crawl URL using aiohttp requests."""        try:
            async with self.session.get(url) as response:
                if response.status != 200:
                    logger.warning(f"HTTP {response.status} for {url}")
                    return None
                
                # Check content size
                content_length = response.headers.get('content-length')
                if content_length and int(content_length) > self.max_content_size:
                    logger.warning(f"Content too large for {url}")
                    return None
                
                html_content = await response.text()
                
                # Parse content
                soup = BeautifulSoup(html_content, 'html.parser')
                return await self._extract_content(url, soup, html_content)
                
        except Exception as e:
            logger.error(f"Requests crawling failed for {url}: {e}")
            return None
    
    async def _crawl_with_selenium(self, url: str) -> Optional[WebContent]:
        """Crawl URL using Selenium for JavaScript-heavy sites."""        try:
            driver = webdriver.Chrome(options=self.selenium_options)
            driver.get(url)
            
            # Wait for page to load
            await asyncio.sleep(3)
            
            # Get page source
            html_content = driver.page_source
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Extract content
            content = await self._extract_content(url, soup, html_content)
            
            driver.quit()
            return content
            
        except Exception as e:
            logger.error(f"Selenium crawling failed for {url}: {e}")
            if 'driver' in locals():
                driver.quit()
            return None
    
    async def _crawl_with_requests_html(self, url: str) -> Optional[WebContent]:
        """Crawl URL using requests-html for JavaScript rendering."""        try:
            # This would be implemented with requests-html
            # For now, fallback to requests method
            return await self._crawl_with_requests(url)
            
        except Exception as e:
            logger.error(f"Requests-HTML crawling failed for {url}: {e}")
            return None
    
    async def _extract_content(self, url: str, soup: BeautifulSoup, html_content: str) -> WebContent:
        """Extract structured content from parsed HTML."""        try:
            # Extract title
            title = self._extract_element_text(soup, self.content_patterns['title'])
            
            # Extract main content
            content = self._extract_element_text(soup, self.content_patterns['article'])
            
            # Extract description
            description = self._extract_element_text(soup, self.content_patterns['description'])
            
            # Extract author
            author = self._extract_element_text(soup, self.content_patterns['author'])
            
            # Extract dates
            published_date = self._extract_date(soup, self.content_patterns['date'])
            
            # Extract metadata
            metadata = self._extract_metadata(soup)
            
            # Extract images
            images = self._extract_images(soup, url)
            
            # Extract videos
            videos = self._extract_videos(soup, url)
            
            # Extract links
            links = self._extract_links(soup, url)
            
            # Extract tags/keywords
            tags = self._extract_tags(soup)
            
            # Detect language
            language = self._detect_language(soup, content)
            
            # Calculate content hash
            content_hash = hashlib.md5(content.encode()).hexdigest()
            
            # Extract social shares
            social_shares = self._extract_social_shares(soup)
            
            # Determine content type
            content_type = self._determine_content_type(soup, url)
            
            return WebContent(
                url=url,
                title=title,
                content=content,
                description=description,
                author=author,
                published_date=published_date,
                modified_date=None,  # Would need additional extraction
                tags=tags,
                images=images,
                videos=videos,
                links=links,
                social_shares=social_shares,
                metadata=metadata,
                content_type=content_type,
                language=language,
                content_hash=content_hash
            )
            
        except Exception as e:
            logger.error(f"Content extraction failed for {url}: {e}")
            return None
    
    def _extract_element_text(self, soup: BeautifulSoup, selectors: List[str]) -> str:
        """Extract text from first matching element."""        for selector in selectors:
            try:
                if selector.startswith('['):
                    # Attribute selector
                    element = soup.select_one(selector)
                    if element:
                        if 'content' in element.attrs:
                            return element.get('content', '')
                        return element.get_text(strip=True)
                else:
                    # CSS selector
                    element = soup.select_one(selector)
                    if element:
                        return element.get_text(strip=True)
            except:
                continue
        return ""
    
    def _extract_date(self, soup: BeautifulSoup, selectors: List[str]) -> Optional[datetime]:
        """Extract and parse date from elements."""        for selector in selectors:
            try:
                element = soup.select_one(selector)
                if element:
                    # Try different date attributes
                    date_text = (
                        element.get('datetime') or
                        element.get('content') or
                        element.get_text(strip=True)
                    )
                    
                    if date_text:
                        # Parse common date formats
                        date_formats = [
                            '%Y-%m-%dT%H:%M:%S%z',
                            '%Y-%m-%d %H:%M:%S',
                            '%Y-%m-%d',
                            '%B %d, %Y',
                            '%b %d, %Y'
                        ]
                        
                        for date_format in date_formats:
                            try:
                                return datetime.strptime(date_text, date_format)
                            except:
                                continue
            except:
                continue
        return None
    
    def _extract_metadata(self, soup: BeautifulSoup) -> Dict:
        """Extract various metadata from page."""        metadata = {}
        
        # Meta tags
        for meta in soup.find_all('meta'):
            name = meta.get('name') or meta.get('property')
            content = meta.get('content')
            if name and content:
                metadata[name] = content
        
        # JSON-LD structured data
        json_ld_scripts = soup.find_all('script', type='application/ld+json')
        json_ld_data = []
        for script in json_ld_scripts:
            try:
                data = json.loads(script.string)
                json_ld_data.append(data)
            except:
                continue
        
        if json_ld_data:
            metadata['json_ld'] = json_ld_data
        
        return metadata
    
    def _extract_images(self, soup: BeautifulSoup, base_url: str) -> List[Dict]:
        """Extract image information."""        images = []
        
        for img in soup.find_all('img'):
            src = img.get('src')
            if src:
                # Make URL absolute
                absolute_url = urljoin(base_url, src)
                
                image_data = {
                    'url': absolute_url,
                    'alt': img.get('alt', ''),
                    'title': img.get('title', ''),
                    'width': img.get('width'),
                    'height': img.get('height')
                }
                images.append(image_data)
        
        return images
    
    def _extract_videos(self, soup: BeautifulSoup, base_url: str) -> List[Dict]:
        """Extract video information."""        videos = []
        
        # Video tags
        for video in soup.find_all('video'):
            src = video.get('src')
            if src:
                absolute_url = urljoin(base_url, src)
                video_data = {
                    'url': absolute_url,
                    'type': 'video',
                    'poster': video.get('poster'),
                    'controls': video.get('controls') is not None
                }
                videos.append(video_data)
        
        # Embedded videos (YouTube, Vimeo, etc.)
        iframe_patterns = [
            r'youtube\.com/embed/([^"&?]+)',
            r'vimeo\.com/video/([^"&?]+)',
            r'dailymotion\.com/embed/video/([^"&?]+)'
        ]
        
        for iframe in soup.find_all('iframe'):
            src = iframe.get('src', '')
            for pattern in iframe_patterns:
                match = re.search(pattern, src)
                if match:
                    video_data = {
                        'url': src,
                        'type': 'embedded',
                        'video_id': match.group(1),
                        'platform': self._detect_video_platform(src)
                    }
                    videos.append(video_data)
                    break
        
        return videos
    
    def _detect_video_platform(self, url: str) -> str:
        """Detect video platform from URL."""        if 'youtube.com' in url or 'youtu.be' in url:
            return 'youtube'
        elif 'vimeo.com' in url:
            return 'vimeo'
        elif 'dailymotion.com' in url:
            return 'dailymotion'
        elif 'tiktok.com' in url:
            return 'tiktok'
        else:
            return 'unknown'
    
    def _extract_links(self, soup: BeautifulSoup, base_url: str) -> List[Dict]:
        """Extract internal and external links."""        links = []
        domain = urlparse(base_url).netloc
        
        for link in soup.find_all('a', href=True):
            href = link.get('href')
            absolute_url = urljoin(base_url, href)
            link_domain = urlparse(absolute_url).netloc
            
            link_data = {
                'url': absolute_url,
                'text': link.get_text(strip=True),
                'title': link.get('title', ''),
                'internal': link_domain == domain,
                'rel': link.get('rel', [])
            }
            links.append(link_data)
        
        return links
    
    def _extract_tags(self, soup: BeautifulSoup) -> List[str]:
        """Extract tags and keywords."""        tags = []
        
        # Meta keywords
        keywords_meta = soup.find('meta', attrs={'name': 'keywords'})
        if keywords_meta:
            keywords = keywords_meta.get('content', '')
            tags.extend([tag.strip() for tag in keywords.split(',')])
        
        # Tag elements
        for tag_elem in soup.find_all(['tag', '.tag', '.keyword', '.label']):
            tag_text = tag_elem.get_text(strip=True)
            if tag_text:
                tags.append(tag_text)
        
        # Hashtags in content
        content_text = soup.get_text()
        hashtags = re.findall(r'#(\w+)', content_text)
        tags.extend(hashtags)
        
        return list(set(tags))  # Remove duplicates
    
    def _detect_language(self, soup: BeautifulSoup, content: str) -> str:
        """Detect content language."""        # Check HTML lang attribute
        html_tag = soup.find('html')
        if html_tag and html_tag.get('lang'):
            return html_tag.get('lang')
        
        # Check meta tags
        lang_meta = soup.find('meta', attrs={'name': 'language'})
        if lang_meta:
            return lang_meta.get('content', 'en')
        
        # Simple heuristic based on content
        # In production, you'd use a proper language detection library
        return 'en'  # Default to English
    
    def _extract_social_shares(self, soup: BeautifulSoup) -> Dict:
        """Extract social media share counts."""        shares = {}
        
        # Look for social share widgets
        social_patterns = {
            'facebook': ['.fb-share', '.facebook-share', '[data-share="facebook"]'],
            'twitter': ['.twitter-share', '.tweet-button', '[data-share="twitter"]'],
            'linkedin': ['.linkedin-share', '[data-share="linkedin"]'],
            'pinterest': ['.pinterest-share', '[data-share="pinterest"]']
        }
        
        for platform, selectors in social_patterns.items():
            for selector in selectors:
                element = soup.select_one(selector)
                if element:
                    # Try to extract share count
                    count_text = element.get_text()
                    count_match = re.search(r'\d+', count_text)
                    if count_match:
                        shares[platform] = int(count_match.group())
                    break
        
        return shares
    
    def _determine_content_type(self, soup: BeautifulSoup, url: str) -> str:
        """Determine the type of content."""        # Check schema.org types
        for script in soup.find_all('script', type='application/ld+json'):
            try:
                data = json.loads(script.string)
                if isinstance(data, dict) and '@type' in data:
                    return data['@type'].lower()
            except:
                continue
        
        # Check meta types
        type_meta = soup.find('meta', attrs={'property': 'og:type'})
        if type_meta:
            return type_meta.get('content', 'webpage')
        
        # Heuristic based on URL and content
        if '/blog/' in url or '/post/' in url or '/article/' in url:
            return 'article'
        elif '/product/' in url or '/shop/' in url:
            return 'product'
        elif '/video/' in url or soup.find('video'):
            return 'video'
        elif '/news/' in url:
            return 'news'
        else:
            return 'webpage'
    
    async def _determine_best_method(self, url: str) -> str:
        """Determine the best crawling method for a URL."""        try:
            # Quick check with HEAD request
            async with self.session.head(url) as response:
                content_type = response.headers.get('content-type', '')
                
                # If it's clearly HTML, try requests first
                if 'text/html' in content_type:
                    return 'requests'
                else:
                    return 'selenium'  # Fallback for dynamic content
                    
        except:
            return 'selenium'  # Default fallback
    
    async def _check_robots_allowed(self, url: str) -> bool:
        """Check if URL is allowed by robots.txt."""        try:
            domain = urlparse(url).netloc
            robots_url = f"https://{domain}/robots.txt"
            
            async with self.session.get(robots_url) as response:
                if response.status == 200:
                    robots_content = await response.text()
                    # Simple robots.txt parsing
                    # In production, use a proper robots.txt parser
                    return 'Disallow: /' not in robots_content
                else:
                    return True  # No robots.txt means allowed
                    
        except:
            return True  # Default to allowed on error
    
    async def crawl_sitemap(self, domain: str) -> Optional[SiteMap]:
        """Crawl and parse website sitemap."""        try:
            sitemap_urls = [
                f"https://{domain}/sitemap.xml",
                f"https://{domain}/sitemap_index.xml",
                f"https://{domain}/robots.txt"  # Check for sitemap reference
            ]
            
            pages = []
            
            for sitemap_url in sitemap_urls:
                try:
                    async with self.session.get(sitemap_url) as response:
                        if response.status == 200:
                            content = await response.text()
                            
                            if sitemap_url.endswith('.xml'):
                                # Parse XML sitemap
                                soup = BeautifulSoup(content, 'xml')
                                for loc in soup.find_all('loc'):
                                    pages.append(loc.get_text())
                            else:
                                # Parse robots.txt for sitemap references
                                for line in content.split('\n'):
                                    if line.startswith('Sitemap:'):
                                        sitemap_ref = line.split(':', 1)[1].strip()
                                        # Recursively fetch referenced sitemaps
                                        # Implementation would continue here
                except:
                    continue
            
            return SiteMap(
                domain=domain,
                pages=pages,
                last_crawled=datetime.now(),
                total_pages=len(pages),
                crawlable_pages=len(pages),  # Would need robots.txt analysis
                robots_allowed=[],
                robots_disallowed=[]
            )
            
        except Exception as e:
            logger.error(f"Failed to crawl sitemap for {domain}: {e}")
            return None
    
    async def monitor_website(
        self,
        urls: List[str],
        check_interval: int = 3600
    ) -> AsyncGenerator[List[WebContent], None]:
        """Monitor multiple URLs for content changes."""        content_hashes = {}
        
        while True:
            try:
                changed_content = []
                
                for url in urls:
                    content = await self.crawl_url(url)
                    if content:
                        current_hash = content.content_hash
                        previous_hash = content_hashes.get(url)
                        
                        if previous_hash != current_hash:
                            changed_content.append(content)
                            content_hashes[url] = current_hash
                
                if changed_content:
                    yield changed_content
                
                await asyncio.sleep(check_interval)
                
            except Exception as e:
                logger.error(f"Website monitoring error: {e}")
                await asyncio.sleep(60)
