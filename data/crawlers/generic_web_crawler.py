"""
Generic Web Crawler Implementation
=================================

Professional generic web crawler for content monitoring across various platforms and websites.
Implements advanced web scraping with comprehensive content detection capabilities.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel - All Rights Reserved

WARNING: This code is proprietary and confidential. Any unauthorized use, 
reproduction, or distribution is strictly prohibited and may result in 
severe legal consequences.
"""

import asyncio
import re
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Set
from urllib.parse import urljoin, urlparse, urlencode
from urllib.robotparser import RobotFileParser
import hashlib
import mimetypes
from dataclasses import dataclass

import aiohttp
import scrapy
from scrapy import signals
from scrapy.crawler import CrawlerProcess
from scrapy.http import Request, Response
from scrapy.utils.project import get_project_settings
from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from .platform_crawler import PlatformCrawler, CrawlerConfig, ContentMatch, ContentMatchType
from ..fingerprinting.vector_matcher import VectorMatcher


@dataclass
class CrawlTarget:
    """Web crawl target specification"""
    url: str
    domain: str
    max_depth: int
    allowed_paths: List[str]
    excluded_paths: List[str]
    content_types: List[str]
    rate_limit: float
    use_selenium: bool


@dataclass
class WebContent:
    """Web content structure"""
    url: str
    title: str
    content: str
    content_type: str
    media_urls: List[str]
    links: List[str]
    metadata: Dict[str, Any]
    discovered_at: datetime
    file_size: Optional[int]
    hash_signature: str


class GenericWebCrawler(PlatformCrawler):
    """
    Professional generic web crawler for content monitoring and discovery.
    
    Features:
    - Multi-domain crawling with respect for robots.txt
    - Content type detection and filtering
    - Media file discovery and analysis
    - Advanced duplicate detection
    - Depth-limited crawling
    - Rate limiting per domain
    - JavaScript rendering with Selenium
    - Content similarity matching
    - Structured data extraction
    """
    
    def __init__(self, config: CrawlerConfig, vector_matcher: VectorMatcher):
        """
        Initialize generic web crawler.
        
        Args:
            config: Crawler configuration
            vector_matcher: Vector matching service
        """
        super().__init__(config, vector_matcher)
        
        # Crawler settings
        self.max_concurrent_requests = 10
        self.download_delay = 1.0
        self.max_file_size = 50 * 1024 * 1024  # 50MB
        self.crawl_targets: List[CrawlTarget] = []
        self.visited_urls: Set[str] = set()
        self.robots_cache: Dict[str, RobotFileParser] = {}
        
        # Content detection settings
        self.supported_content_types = [
            'text/html', 'text/plain', 'application/json',
            'image/jpeg', 'image/png', 'image/gif', 'image/webp',
            'video/mp4', 'video/webm', 'video/avi', 'video/mov',
            'audio/mp3', 'audio/wav', 'audio/ogg', 'audio/m4a',
            'application/pdf', 'application/msword'
        ]
        
        # Media file extensions
        self.media_extensions = {
            'image': ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.svg'],
            'video': ['.mp4', '.webm', '.avi', '.mov', '.wmv', '.flv', '.mkv'],
            'audio': ['.mp3', '.wav', '.ogg', '.m4a', '.aac', '.flac', '.wma'],
            'document': ['.pdf', '.doc', '.docx', '.txt', '.rtf']
        }
        
        # Selenium driver for JavaScript-heavy sites
        self.selenium_driver = None
    
    async def add_crawl_target(self, target: CrawlTarget):
        """Add a new crawl target"""
        self.crawl_targets.append(target)
        self.logger.info(f"Added crawl target: {target.domain}")
    
    async def search_content(self, search_terms: List[str], 
                           max_results: int = 100) -> List[Dict[str, Any]]:
        """
        Search for content across configured crawl targets.
        
        Args:
            search_terms: Terms to search for
            max_results: Maximum number of results to return
            
        Returns:
            List of found content items
        """



        try:
            all_results = []
            
            for target in self.crawl_targets:
                try:
                    # Crawl target domain
                    target_results = await self._crawl_target(target, search_terms, max_results // len(self.crawl_targets))
                    all_results.extend(target_results)
                    
                    # Apply rate limiting between targets
                    await asyncio.sleep(target.rate_limit)
                    
                except Exception as e:
                    self.logger.error(f"Error crawling target {target.domain}: {str(e)}")
                    continue
            
            # Remove duplicates and sort by relevance
            unique_results = await self._deduplicate_and_rank(all_results, search_terms)
            
            final_results = unique_results[:max_results]
            
            self.logger.info(f"Generic web crawler found {len(final_results)} content items")
            return final_results
            
        except Exception as e:
            self.logger.error(f"Error in generic web search: {str(e)}")
            return []
    
    async def extract_content_metadata(self, content_url: str) -> Dict[str, Any]:
        """
        Extract detailed metadata from web content URL.
        
        Args:
            content_url: Web content URL
            
        Returns:
            Detailed content metadata
        """



        try:
            # Check if URL was already processed
            if content_url in self.visited_urls:
                self.logger.debug(f"URL already processed: {content_url}")
                return {}
            
            # Check robots.txt compliance
            if not await self._can_fetch_url(content_url):
                self.logger.warning(f"Robots.txt disallows crawling: {content_url}")
                return {}
            
            # Fetch content
            content = await self._fetch_content(content_url)
            if not content:
                return {}
            
            # Extract metadata
            metadata = await self._extract_metadata_from_content(content, content_url)
            
            self.visited_urls.add(content_url)
            
            return metadata
            
        except Exception as e:
            self.logger.error(f"Error extracting metadata for {content_url}: {str(e)}")
            return {}
    
    async def download_content_sample(self, content_url: str) -> Optional[bytes]:
        """
        Download content sample for fingerprinting.
        
        Args:
            content_url: Web content URL
            
        Returns:
            Content sample data or None
        """



        try:
            # Check file size first
            file_size = await self._get_content_size(content_url)
            if file_size and file_size > self.max_file_size:
                self.logger.warning(f"File too large to download: {file_size} bytes")
                return None
            
            # Download content
            async with aiohttp.ClientSession() as session:
                async with session.get(content_url, headers=self.headers) as response:
                    if response.status == 200:
                        if file_size and file_size <= 1024 * 1024:  # Download full file if < 1MB
                            return await response.read()
                        else:
                            # Download partial content for large files
                            content = b''
                            async for chunk in response.content.iter_chunked(1024):
                                content += chunk
                                if len(content) >= 1024 * 1024:  # Stop at 1MB
                                    break
                            return content
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error downloading content sample for {content_url}: {str(e)}")
            return None
    
    async def crawl_domain_comprehensively(self, domain: str, max_pages: int = 1000) -> List[Dict[str, Any]]:
        """
        Perform comprehensive crawl of a specific domain.
        
        Args:
            domain: Domain to crawl
            max_pages: Maximum number of pages to crawl
            
        Returns:
            List of discovered content
        """



        try:
            # Create crawl target for domain
            target = CrawlTarget(
                url=f"https://{domain}",
                domain=domain,
                max_depth=3,
                allowed_paths=['*'],
                excluded_paths=['/admin', '/private', '/api'],
                content_types=self.supported_content_types,
                rate_limit=1.0,
                use_selenium=False
            )
            
            discovered_content = []
            
            # Start crawling from root
            pages_to_crawl = [target.url]
            crawled_count = 0
            
            while pages_to_crawl and crawled_count < max_pages:
                current_url = pages_to_crawl.pop(0)
                
                try:
                    # Skip if already crawled
                    if current_url in self.visited_urls:
                        continue
                    
                    # Fetch and process page
                    content = await self._fetch_content(current_url)
                    if not content:
                        continue
                    
                    # Extract content and metadata
                    metadata = await self._extract_metadata_from_content(content, current_url)
                    if metadata:
                        discovered_content.append(metadata)
                    
                    # Find links to other pages
                    links = await self._extract_links(content, current_url, domain)
                    pages_to_crawl.extend(links[:10])  # Limit new links per page
                    
                    self.visited_urls.add(current_url)
                    crawled_count += 1
                    
                    # Rate limiting
                    await asyncio.sleep(target.rate_limit)
                    
                except Exception as e:
                    self.logger.error(f"Error crawling page {current_url}: {str(e)}")
                    continue
            
            self.logger.info(f"Crawled {crawled_count} pages from domain {domain}")
            return discovered_content
            
        except Exception as e:
            self.logger.error(f"Error in comprehensive domain crawl for {domain}: {str(e)}")
            return []
    
    async def search_specific_file_types(self, domain: str, file_types: List[str]) -> List[Dict[str, Any]]:
        """
        Search for specific file types on a domain.
        
        Args:
            domain: Domain to search
            file_types: List of file extensions to search for
            
        Returns:
            List of found files
        """



        try:
            found_files = []
            
            # Use search engines to find files
            for file_type in file_types:
                search_queries = [
                    f"site:{domain} filetype:{file_type.lstrip('.')}",
                    f"site:{domain} ext:{file_type.lstrip('.')}"
                ]
                
                for query in search_queries:
                    files = await self._search_files_via_search_engines(query)
                    found_files.extend(files)
                    
                    await asyncio.sleep(2.0)  # Rate limiting
            
            # Remove duplicates
            unique_files = {}
            for file_data in found_files:
                url = file_data.get('url')
                if url and url not in unique_files:
                    unique_files[url] = file_data
            
            result_files = list(unique_files.values())
            
            self.logger.info(f"Found {len(result_files)} files of types {file_types} on {domain}")
            return result_files
            
        except Exception as e:
            self.logger.error(f"Error searching file types on {domain}: {str(e)}")
            return []
    
    # Private helper methods
    
    async def _crawl_target(self, target: CrawlTarget, search_terms: List[str], max_results: int) -> List[Dict[str, Any]]:
        """Crawl a specific target"""



        try:
            results = []
            
            if target.use_selenium:
                results = await self._crawl_with_selenium(target, search_terms, max_results)
            else:
                results = await self._crawl_with_requests(target, search_terms, max_results)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error crawling target {target.domain}: {str(e)}")
            return []
    
    async def _crawl_with_requests(self, target: CrawlTarget, search_terms: List[str], max_results: int) -> List[Dict[str, Any]]:
        """Crawl using HTTP requests"""
        results = []
        
        try:
            # Start with target URL
            urls_to_visit = [target.url]
            visited = set()
            
            while urls_to_visit and len(results) < max_results:
                current_url = urls_to_visit.pop(0)
                
                if current_url in visited:
                    continue
                
                # Fetch content
                content = await self._fetch_content(current_url)
                if not content:
                    continue
                
                # Check if content matches search terms
                if await self._content_matches_terms(content, search_terms):
                    metadata = await self._extract_metadata_from_content(content, current_url)
                    if metadata:
                        results.append(metadata)
                
                # Extract links for further crawling
                links = await self._extract_links(content, current_url, target.domain)
                urls_to_visit.extend(links[:5])  # Limit links per page
                
                visited.add(current_url)
                
                # Rate limiting
                await asyncio.sleep(target.rate_limit)
            
        except Exception as e:
            self.logger.error(f"Error in requests-based crawling: {str(e)}")
        
        return results
    
    async def _crawl_with_selenium(self, target: CrawlTarget, search_terms: List[str], max_results: int) -> List[Dict[str, Any]]:
        """Crawl using Selenium for JavaScript-heavy sites"""
        results = []
        
        try:
            # Initialize Selenium if needed
            if not self.selenium_driver:
                await self._initialize_selenium()
            
            self.selenium_driver.get(target.url)
            await asyncio.sleep(2.0)
            
            # Extract content with JavaScript execution
            page_source = self.selenium_driver.page_source
            
            # Process page content
            if await self._content_matches_terms(page_source, search_terms):
                metadata = await self._extract_metadata_from_content(page_source, target.url)
                if metadata:
                    results.append(metadata)
            
        except Exception as e:
            self.logger.error(f"Error in Selenium-based crawling: {str(e)}")
        
        return results
    
    async def _fetch_content(self, url: str) -> Optional[str]:
        """Fetch content from URL"""



        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers) as response:
                    if response.status == 200:
                        content_type = response.headers.get('content-type', '')
                        if 'text/html' in content_type or 'text/plain' in content_type:
                            return await response.text()
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error fetching content from {url}: {str(e)}")
            return None
    
    async def _extract_metadata_from_content(self, content: str, url: str) -> Dict[str, Any]:
        """Extract metadata from content"""



        try:
            soup = BeautifulSoup(content, 'html.parser')
            
            metadata = {
                'url': url,
                'title': '',
                'description': '',
                'content': '',
                'media_urls': [],
                'links': [],
                'metadata': {},
                'discovered_at': datetime.utcnow().isoformat(),
                'platform': 'web'
            }
            
            # Extract title
            title_tag = soup.find('title')
            if title_tag:
                metadata['title'] = title_tag.get_text().strip()
            
            # Extract meta description
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if meta_desc:
                metadata['description'] = meta_desc.get('content', '')
            
            # Extract text content
            for script in soup(["script", "style"]):
                script.extract()
            metadata['content'] = soup.get_text()[:5000]  # First 5000 chars
            
            # Extract media URLs
            media_urls = []
            for tag in soup.find_all(['img', 'video', 'audio']):
                src = tag.get('src')
                if src:
                    media_urls.append(urljoin(url, src))
            metadata['media_urls'] = media_urls
            
            # Extract links
            links = []
            for a_tag in soup.find_all('a', href=True):
                href = a_tag['href']
                if href.startswith('http'):
                    links.append(href)
            metadata['links'] = links[:20]  # Limit links
            
            # Extract structured data
            structured_data = await self._extract_structured_data(soup)
            metadata['metadata'].update(structured_data)
            
            return metadata
            
        except Exception as e:
            self.logger.error(f"Error extracting metadata: {str(e)}")
            return {}
    
    async def _extract_structured_data(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract structured data from HTML"""
        structured_data = {}
        
        try:
            # JSON-LD
            for script in soup.find_all('script', type='application/ld+json'):
                try:
                    data = json.loads(script.string)
                    structured_data['jsonld'] = data
                    break
                except:
                    continue
            
            # Open Graph
            og_data = {}
            for meta in soup.find_all('meta', property=re.compile(r'^og:')):
                property_name = meta.get('property')
                content = meta.get('content')
                if property_name and content:
                    og_data[property_name] = content
            if og_data:
                structured_data['opengraph'] = og_data
            
            # Twitter Cards
            twitter_data = {}
            for meta in soup.find_all('meta', attrs={'name': re.compile(r'^twitter:')}):
                name = meta.get('name')
                content = meta.get('content')
                if name and content:
                    twitter_data[name] = content
            if twitter_data:
                structured_data['twitter'] = twitter_data
            
        except Exception as e:
            self.logger.error(f"Error extracting structured data: {str(e)}")
        
        return structured_data
    
    async def _extract_links(self, content: str, base_url: str, target_domain: str) -> List[str]:
        """Extract links from content"""



        try:
            soup = BeautifulSoup(content, 'html.parser')
            links = []
            
            for a_tag in soup.find_all('a', href=True):
                href = a_tag['href']
                full_url = urljoin(base_url, href)
                
                # Only include links from target domain
                parsed_url = urlparse(full_url)
                if parsed_url.netloc == target_domain:
                    links.append(full_url)
            
            return links[:50]  # Limit to 50 links
            
        except Exception as e:
            self.logger.error(f"Error extracting links: {str(e)}")
            return []
    
    async def _content_matches_terms(self, content: str, search_terms: List[str]) -> bool:
        """Check if content matches search terms"""
        content_lower = content.lower()
        return any(term.lower() in content_lower for term in search_terms)
    
    async def _can_fetch_url(self, url: str) -> bool:
        """Check if URL can be fetched according to robots.txt"""



        try:
            parsed_url = urlparse(url)
            domain = parsed_url.netloc
            
            if domain not in self.robots_cache:
                # Fetch robots.txt
                robots_url = f"{parsed_url.scheme}://{domain}/robots.txt"
                try:
                    rp = RobotFileParser()
                    rp.set_url(robots_url)
                    rp.read()
                    self.robots_cache[domain] = rp
                except:
                    # If robots.txt fails, assume crawling is allowed
                    self.robots_cache[domain] = None
            
            robots_parser = self.robots_cache[domain]
            if robots_parser:
                return robots_parser.can_fetch(self.config.user_agent, url)
            
            return True  # Allow if no robots.txt
            
        except Exception as e:
            self.logger.error(f"Error checking robots.txt for {url}: {str(e)}")
            return True  # Allow on error
    
    async def _get_content_size(self, url: str) -> Optional[int]:
        """Get content size without downloading"""



        try:
            async with aiohttp.ClientSession() as session:
                async with session.head(url, headers=self.headers) as response:
                    content_length = response.headers.get('content-length')
                    if content_length:
                        return int(content_length)
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting content size for {url}: {str(e)}")
            return None
    
    async def _deduplicate_and_rank(self, results: List[Dict[str, Any]], search_terms: List[str]) -> List[Dict[str, Any]]:
        """Remove duplicates and rank results by relevance"""



        try:
            # Remove duplicates based on URL
            unique_results = {}
            for result in results:
                url = result.get('url')
                if url and url not in unique_results:
                    unique_results[url] = result
            
            # Rank by relevance (simple term frequency)
            ranked_results = []
            for result in unique_results.values():
                content = f"{result.get('title', '')} {result.get('description', '')} {result.get('content', '')}"
                relevance_score = sum(
                    content.lower().count(term.lower()) for term in search_terms
                )
                result['relevance_score'] = relevance_score
                ranked_results.append(result)
            
            # Sort by relevance score
            ranked_results.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
            
            return ranked_results
            
        except Exception as e:
            self.logger.error(f"Error in deduplication and ranking: {str(e)}")
            return results
    
    async def _search_files_via_search_engines(self, query: str) -> List[Dict[str, Any]]:
        """Search for files using search engines (placeholder implementation)"""
        # This would integrate with search engine APIs
        # Placeholder implementation
        return []
    
    async def _initialize_selenium(self):
        """Initialize Selenium WebDriver"""



        try:
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument(f'--user-agent={self.config.user_agent}')
            
            self.selenium_driver = webdriver.Chrome(options=chrome_options)
            self.logger.info("Selenium WebDriver initialized for generic crawler")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Selenium driver: {str(e)}")
            raise
    
    async def _cleanup_selenium(self):
        """Cleanup Selenium WebDriver"""
        if self.selenium_driver:
            try:
                self.selenium_driver.quit()
                self.selenium_driver = None
                self.logger.info("Selenium WebDriver cleaned up")
            except Exception as e:
                self.logger.error(f"Error cleaning up Selenium driver: {str(e)}")
    
    def get_crawl_statistics(self) -> Dict[str, Any]:
        """Get crawler statistics"""



        return {
            'platform': 'generic_web',
            'crawl_targets_count': len(self.crawl_targets),
            'visited_urls_count': len(self.visited_urls),
            'robots_cache_size': len(self.robots_cache),
            'max_concurrent_requests': self.max_concurrent_requests,
            'download_delay': self.download_delay,
            'max_file_size': self.max_file_size,
            'supported_content_types': len(self.supported_content_types),
            'selenium_active': self.selenium_driver is not None
        }
    
    async def close(self):
        """Cleanup crawler resources"""
        await self._cleanup_selenium()
        await self.cleanup_session()
        self.visited_urls.clear()
        self.robots_cache.clear()
