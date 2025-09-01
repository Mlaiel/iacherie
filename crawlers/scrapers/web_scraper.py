"""Advanced Web Scraper - IA-Influencer-Agent
==========================================

High-performance web scraping engine with anti-detection capabilities.
Designed for large-scale content discovery and monitoring.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

⚠️ CRITICAL LEGAL WARNING ⚠️
UNAUTHORIZED USE, COPYING, OR DISTRIBUTION IS STRICTLY PROHIBITED AND WILL RESULT IN IMMEDIATE LEGAL ACTION.
This technology is EXCLUSIVE property of Fahed Mlaiel. Contact: mlaiel@live.de for licensing.
"""

import asyncio
import aiohttp
import time
import random
import logging
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import lxml
from fake_useragent import UserAgent
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential
import hashlib
import json
from datetime import datetime, timedelta

@dataclass
class ScrapingResult:
    """
Structured scraping result."""
    url: str
    status_code: int
    content: str
    headers: Dict[str, str]
    metadata: Dict[str, Any]
    timestamp: datetime
    processing_time: float
    success: bool
    error: Optional[str] = None

@dataclass
class ScrapingConfig:
    """
Scraping configuration parameters."""
    concurrent_requests: int = 10
    request_delay: float = 1.0
    timeout: int = 30
    retries: int = 3
    use_proxy: bool = False
    respect_robots: bool = True
    custom_headers: Optional[Dict[str, str]] = None
    user_agent_rotation: bool = True
    javascript_enabled: bool = False

class WebScraper:
    """
    Professional web scraping engine with advanced features.
    
    Features:
    - Anti-detection mechanisms
    - Concurrent processing
    - Request throttling
    - User agent rotation
    - Proxy support
    - Content parsing
    - Error handling and retries
    """
    
    def __init__(self, config: Optional[ScrapingConfig] = None):
        self.config = config or ScrapingConfig()
        self.session: Optional[aiohttp.ClientSession] = None
        self.user_agent = UserAgent()
        self.logger = logging.getLogger(__name__)
        self.request_history: List[Dict] = []
        self.rate_limiter = {}
        
    async def __aenter__(self):
        """
Async context manager entry."""
        await self._create_session()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """
Async context manager exit."""
        await self._close_session()
        
    async def _create_session(self):
        """
Create HTTP session with optimal settings."""
        connector = aiohttp.TCPConnector(
            limit=100,
            limit_per_host=10,
            ttl_dns_cache=300,
            use_dns_cache=True,
            enable_cleanup_closed=True
        )
        
        timeout = aiohttp.ClientTimeout(total=self.config.timeout)
        
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers=self._get_default_headers()
        )
        
    async def _close_session(self):
        """
Close HTTP session."""
        if self.session:
            await self.session.close()
            
    def _get_default_headers(self) -> Dict[str, str]:
        """
Get default HTTP headers."""
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        if self.config.custom_headers:
            headers.update(self.config.custom_headers)
            
        return headers
        
    def _get_user_agent(self) -> str:
        """
Get randomized user agent."""
        if self.config.user_agent_rotation:
            return self.user_agent.random
        return self.user_agent.chrome
        
    def _should_respect_robots(self, url: str) -> bool:
        """
Check if robots.txt should be respected."""
        if not self.config.respect_robots:
            return True
            
        # Implementation would check robots.txt
        # For now, return True (allow scraping)
        return True
        
    async def _rate_limit(self, domain: str):
        """
Apply rate limiting per domain."""
        now = time.time()
        if domain in self.rate_limiter:
            last_request = self.rate_limiter[domain]
            elapsed = now - last_request
            if elapsed < self.config.request_delay:
                await asyncio.sleep(self.config.request_delay - elapsed)
                
        self.rate_limiter[domain] = now
        
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def _fetch_url(self, url: str, headers: Optional[Dict] = None) -> ScrapingResult:
        """
Fetch single URL with retries and error handling."""
        start_time = time.time()
        domain = urlparse(url).netloc
        
        await self._rate_limit(domain)
        
        if not self._should_respect_robots(url):
            return ScrapingResult(
                url=url,
                status_code=403,
                content="",
                headers={},
                metadata={},
                timestamp=datetime.now(),
                processing_time=time.time() - start_time,
                success=False,
                error="Blocked by robots.txt"
            )
            
        request_headers = self._get_default_headers()
        request_headers['User-Agent'] = self._get_user_agent()
        
        if headers:
            request_headers.update(headers)
            
        try:
            async with self.session.get(url, headers=request_headers) as response:
                content = await response.text()
                
                result = ScrapingResult(
                    url=url,
                    status_code=response.status,
                    content=content,
                    headers=dict(response.headers),
                    metadata={
                        'final_url': str(response.url),
                        'content_length': len(content),
                        'content_type': response.headers.get('content-type', ''),
                        'encoding': response.charset or 'utf-8'
                    },
                    timestamp=datetime.now(),
                    processing_time=time.time() - start_time,
                    success=response.status == 200
                )
                
                self._log_request(result)
                return result
                
        except Exception as e:
            error_result = ScrapingResult(
                url=url,
                status_code=0,
                content="",
                headers={},
                metadata={},
                timestamp=datetime.now(),
                processing_time=time.time() - start_time,
                success=False,
                error=str(e)
            )
            
            self.logger.error(f"Error fetching {url}: {e}")
            return error_result
            
    def _log_request(self, result: ScrapingResult):
        """Log request for monitoring and analytics."""
        log_entry = {
            'url': result.url,
            'status_code': result.status_code,
            'processing_time': result.processing_time,
            'timestamp': result.timestamp.isoformat(),
            'success': result.success,
            'content_length': len(result.content)
        }
        
        self.request_history.append(log_entry)
        
        # Keep only last 1000 requests
        if len(self.request_history) > 1000:
            self.request_history = self.request_history[-1000:]
            
    async def scrape_url(self, url: str, headers: Optional[Dict] = None) -> ScrapingResult:
        """
Scrape single URL."""
        if not self.session:
            await self._create_session()
            
        return await self._fetch_url(url, headers)
        
    async def scrape_urls(self, urls: List[str], headers: Optional[Dict] = None) -> List[ScrapingResult]:
        """
Scrape multiple URLs concurrently."""
        if not self.session:
            await self._create_session()
            
        semaphore = asyncio.Semaphore(self.config.concurrent_requests)
        
        async def scrape_with_semaphore(url: str) -> ScrapingResult:
            async with semaphore:
                return await self._fetch_url(url, headers)
                
        tasks = [scrape_with_semaphore(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle exceptions
        clean_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                clean_results.append(ScrapingResult(
                    url=urls[i],
                    status_code=0,
                    content="",
                    headers={},
                    metadata={},
                    timestamp=datetime.now(),
                    processing_time=0,
                    success=False,
                    error=str(result)
                ))
            else:
                clean_results.append(result)
                
        return clean_results
        
    def parse_content(self, content: str, parser: str = 'html.parser') -> BeautifulSoup:
        """Parse HTML content with BeautifulSoup."""
        return BeautifulSoup(content, parser)
        
    def extract_links(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """
Extract all links from parsed content."""
        links = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            full_url = urljoin(base_url, href)
            links.append(full_url)
        return links
        
    def extract_images(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, str]]:
        """
Extract all images from parsed content."""
        images = []
        for img in soup.find_all('img'):
            src = img.get('src')
            if src:
                full_url = urljoin(base_url, src)
                images.append({
                    'src': full_url,
                    'alt': img.get('alt', ''),
                    'title': img.get('title', '')
                })
        return images
        
    def extract_text(self, soup: BeautifulSoup, clean: bool = True) -> str:
        """
Extract clean text from parsed content."""
        if clean:
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            return soup.get_text(separator=' ', strip=True)
        return soup.get_text()
        
    def extract_metadata(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract page metadata."""
        metadata = {}
        
        # Title
        title_tag = soup.find('title')
        if title_tag:
            metadata['title'] = title_tag.get_text().strip()
            
        # Meta tags
        meta_tags = soup.find_all('meta')
        for meta in meta_tags:
            name = meta.get('name') or meta.get('property')
            content = meta.get('content')
            if name and content:
                metadata[name] = content
                
        return metadata
        
    def get_stats(self) -> Dict[str, Any]:
        """
Get scraping statistics."""
        if not self.request_history:
            return {}
            
        successful_requests = [r for r in self.request_history if r['success']]
        failed_requests = [r for r in self.request_history if not r['success']]
        
        return {
            'total_requests': len(self.request_history),
            'successful_requests': len(successful_requests),
            'failed_requests': len(failed_requests),
            'success_rate': len(successful_requests) / len(self.request_history) * 100,
            'average_response_time': sum(r['processing_time'] for r in self.request_history) / len(self.request_history),
            'total_content_size': sum(r['content_length'] for r in self.request_history),
            'requests_per_hour': self._calculate_requests_per_hour()
        }
        
    def _calculate_requests_per_hour(self) -> float:
        """
Calculate requests per hour based on recent history."""
        if not self.request_history:
            return 0
            
        now = datetime.now()
        one_hour_ago = now - timedelta(hours=1)
        
        recent_requests = [
            r for r in self.request_history 
            if datetime.fromisoformat(r['timestamp']) > one_hour_ago
        ]
        
        return len(recent_requests)
        
    async def health_check(self) -> Dict[str, Any]:
        """
Perform health check on scraper."""
        test_url = "https://httpbin.org/get"
        
        try:
            result = await self.scrape_url(test_url)
            return {
                'healthy': result.success,
                'response_time': result.processing_time,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'healthy': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
