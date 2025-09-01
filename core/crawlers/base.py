"""Base Crawler Abstract Class
===========================

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  INTELLECTUAL PROPERTY WARNING ⚠️
Unauthorized use, copying or distribution prohibited.

Abstract base class defining the common interface for all platform-specific
crawlers. Provides standardized methods for content extraction, rate limiting,
error handling, and result normalization across different platforms.
"""

import asyncio
import logging
import time
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass
import aiohttp
import requests
from sqlalchemy.orm import Session

from ..config import PlatformConfig, ContentType

logger = logging.getLogger(__name__)

@dataclass
class CrawlResult:
    """
Standardized result structure for crawler operations."""
    
    url: str
    platform: str
    content_type: str
    title: Optional[str] = None
    description: Optional[str] = None
    author: Optional[str] = None
    upload_date: Optional[datetime] = None
    view_count: Optional[int] = None
    duration_ms: Optional[int] = None
    file_size: Optional[int] = None
    thumbnail_url: Optional[str] = None
    tags: List[str] = None
    metadata: Dict[str, Any] = None
    content_data: Optional[bytes] = None
    
    def __post_init__(self):
        """
Initialize default values."""
        if self.tags is None:
            self.tags = []
        if self.metadata is None:
            self.metadata = {}

class RateLimiter:
    """
Rate limiting implementation for crawler requests."""
    
    def __init__(self, requests_per_minute: int, requests_per_hour: int):
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        
        # Request tracking
        self.minute_requests: List[float] = []
        self.hour_requests: List[float] = []
    
    async def acquire(self):
        """
Acquire permission to make a request, blocking if necessary."""
        
        now = time.time()
        
        # Clean old requests
        self._clean_old_requests(now)
        
        # Check minute limit
        if len(self.minute_requests) >= self.requests_per_minute:
            sleep_time = 60 - (now - self.minute_requests[0])
            if sleep_time > 0:
                logger.debug("Rate limited: waiting %.2f seconds", sleep_time)
                await asyncio.sleep(sleep_time)
                now = time.time()
                self._clean_old_requests(now)
        
        # Check hour limit
        if len(self.hour_requests) >= self.requests_per_hour:
            sleep_time = 3600 - (now - self.hour_requests[0])
            if sleep_time > 0:
                logger.debug("Rate limited (hourly): waiting %.2f seconds", sleep_time)
                await asyncio.sleep(sleep_time)
                now = time.time()
                self._clean_old_requests(now)
        
        # Record this request
        self.minute_requests.append(now)
        self.hour_requests.append(now)
    
    def _clean_old_requests(self, now: float):
        """Remove old request timestamps."""
        
        # Remove requests older than 1 minute
        self.minute_requests = [req_time for req_time in self.minute_requests if now - req_time < 60]
        
        # Remove requests older than 1 hour
        self.hour_requests = [req_time for req_time in self.hour_requests if now - req_time < 3600]

class BaseCrawler(ABC):
    """
    Abstract base class for all platform-specific crawlers.
    
    Provides common functionality including rate limiting, error handling,
    retry logic, and standardized result formatting.
    """
    
    def __init__(self, config: PlatformConfig, database_session: Session):
        self.config = config
        self.db_session = database_session
        
        # Rate limiting
        self.rate_limiter = RateLimiter(
            config.requests_per_minute,
            config.requests_per_hour
        )
        
        # Request session configuration
        self.session_timeout = aiohttp.ClientTimeout(total=30)
        self.headers = self._build_headers()
        
        # Error tracking
        self.error_count = 0
        self.last_error_time: Optional[datetime] = None
        
        # Performance metrics
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.avg_response_time = 0.0
        
        logger.info("Initialized %s crawler", self.__class__.__name__)
    
    def _build_headers(self) -> Dict[str, str]:
        """Build HTTP headers for requests."""
        
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        # Add custom headers from config
        headers.update(self.config.custom_headers)
        
        # Select random user agent if available
        if self.config.user_agents:
            import random
            headers['User-Agent'] = random.choice(self.config.user_agents)
        
        return headers
    
    async def crawl_urls(
        self, 
        urls: List[str], 
        fingerprints: List[str]
    ) -> List[CrawlResult]:
        """
        Crawl multiple URLs and return results.
        
        Args:
            urls: List of URLs to crawl
            fingerprints: List of protected content fingerprints for matching
            
        Returns:
            List of CrawlResult objects
        """
        
        results = []
        
        for url in urls:
            try:
                result = await self.crawl_single_url(url, fingerprints)
                if result:
                    results.append(result)
                    
            except Exception as e:
                logger.error("Error crawling URL %s: %s", url, str(e))
                self._record_error(e)
        
        logger.info("Crawled %d URLs, got %d results", len(urls), len(results))
        return results
    
    async def crawl_single_url(
        self, 
        url: str, 
        fingerprints: List[str]
    ) -> Optional[CrawlResult]:
        """
        Crawl a single URL with retry logic.
        
        Args:
            url: URL to crawl
            fingerprints: Protected content fingerprints
            
        Returns:
            CrawlResult or None if failed
        """
        
        for attempt in range(self.config.max_retries + 1):
            try:
                # Rate limiting
                await self.rate_limiter.acquire()
                
                # Record start time
                start_time = time.time()
                
                # Perform crawling
                result = await self._crawl_url_implementation(url, fingerprints)
                
                # Update performance metrics
                response_time = time.time() - start_time
                self._update_performance_metrics(response_time, success=True)
                
                return result
                
            except Exception as e:
                self._update_performance_metrics(0, success=False)
                
                if attempt < self.config.max_retries:
                    wait_time = self.config.retry_delay * (self.config.backoff_factor ** attempt)
                    logger.warning("Retry %d/%d for %s in %.1fs: %s", 
                                 attempt + 1, self.config.max_retries, url, wait_time, str(e))
                    await asyncio.sleep(wait_time)
                else:
                    logger.error("Failed to crawl %s after %d attempts: %s", 
                               url, self.config.max_retries + 1, str(e))
                    self._record_error(e)
                    return None
        
        return None
    
    @abstractmethod
    async def _crawl_url_implementation(
        self, 
        url: str, 
        fingerprints: List[str]
    ) -> Optional[CrawlResult]:
        """
        Platform-specific implementation of URL crawling.
        
        This method must be implemented by each platform-specific crawler.
        
        Args:
            url: URL to crawl
            fingerprints: Protected content fingerprints
            
        Returns:
            CrawlResult or None
        """
        pass
    
    @abstractmethod
    def extract_content_metadata(self, content_data: Any) -> Dict[str, Any]:
        """
        Extract platform-specific metadata from content.
        
        Args:
            content_data: Platform-specific content data
            
        Returns:
            Dictionary of extracted metadata
        """
        pass
    
    @abstractmethod
    def is_url_supported(self, url: str) -> bool:
        """
        Check if URL is supported by this crawler.
        
        Args:
            url: URL to check
            
        Returns:
            True if URL is supported
        """
        pass
    
    async def search_content(
        self, 
        search_terms: List[str], 
        fingerprints: List[str],
        max_results: int = 50
    ) -> List[CrawlResult]:
        """
        Search for content using platform-specific search capabilities.
        
        Args:
            search_terms: Terms to search for
            fingerprints: Protected content fingerprints
            max_results: Maximum number of results to return
            
        Returns:
            List of CrawlResult objects
        """
        
        # Default implementation - can be overridden by specific crawlers
        logger.info("Search not implemented for %s", self.__class__.__name__)
        return []
    
    async def get_trending_content(
        self, 
        fingerprints: List[str],
        category: Optional[str] = None,
        max_results: int = 50
    ) -> List[CrawlResult]:
        """
        Get trending content from the platform.
        
        Args:
            fingerprints: Protected content fingerprints
            category: Optional content category
            max_results: Maximum number of results
            
        Returns:
            List of CrawlResult objects
        """
        
        # Default implementation - can be overridden by specific crawlers
        logger.info("Trending content not implemented for %s", self.__class__.__name__)
        return []
    
    async def health_check(self) -> bool:
        """
        Perform health check on the crawler.
        
        Returns:
            True if crawler is healthy
        """
        
        try:
            # Test basic connectivity
            test_url = self._get_health_check_url()
            if not test_url:
                return True  # No health check URL available
            
            async with aiohttp.ClientSession(timeout=self.session_timeout) as session:
                async with session.head(test_url, headers=self.headers) as response:
                    return response.status < 500
                    
        except Exception as e:
            logger.error("Health check failed for %s: %s", self.__class__.__name__, str(e))
            return False
    
    def _get_health_check_url(self) -> Optional[str]:
        """Get URL for health check - can be overridden by specific crawlers."""
        return self.config.base_url if self.config.base_url else None
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """
Get crawler performance metrics."""
        
        success_rate = self.successful_requests / self.total_requests if self.total_requests > 0 else 0
        
        return {
            'total_requests': self.total_requests,
            'successful_requests': self.successful_requests,
            'failed_requests': self.failed_requests,
            'success_rate': success_rate,
            'avg_response_time': self.avg_response_time,
            'error_count': self.error_count,
            'last_error_time': self.last_error_time.isoformat() if self.last_error_time else None,
            'rate_limit_status': {
                'requests_per_minute': len(self.rate_limiter.minute_requests),
                'requests_per_hour': len(self.rate_limiter.hour_requests),
                'limit_per_minute': self.config.requests_per_minute,
                'limit_per_hour': self.config.requests_per_hour
            }
        }
    
    def _update_performance_metrics(self, response_time: float, success: bool):
        """
Update performance tracking metrics."""
        
        self.total_requests += 1
        
        if success:
            self.successful_requests += 1
            
            # Update average response time
            if self.avg_response_time == 0:
                self.avg_response_time = response_time
            else:
                # Exponential moving average
                self.avg_response_time = 0.9 * self.avg_response_time + 0.1 * response_time
        else:
            self.failed_requests += 1
    
    def _record_error(self, error: Exception):
        """
Record error for monitoring and debugging."""
        
        self.error_count += 1
        self.last_error_time = datetime.utcnow()
        
        # Log error details
        logger.error("Crawler error in %s: %s", self.__class__.__name__, str(error))
    
    def _normalize_url(self, url: str) -> str:
        """Normalize URL format for consistent processing."""
        
        url = url.strip()
        
        # Remove tracking parameters
        if '?' in url:
            base_url, params = url.split('?', 1)
            # Keep only essential parameters
            essential_params = []
            for param in params.split('&'):
                if '=' in param:
                    key, value = param.split('=', 1)
                    if key.lower() in ['v', 'id', 'p', 'video_id', 'post_id']:
                        essential_params.append(param)
            
            if essential_params:
                url = f"{base_url}?{'&'.join(essential_params)}"
            else:
                url = base_url
        
        return url
    
    def _extract_content_id(self, url: str) -> Optional[str]:
        """Extract content ID from URL - to be implemented by specific crawlers."""
        return None
    
    def _determine_content_type(self, metadata: Dict[str, Any]) -> ContentType:
        """
Determine content type from metadata."""
        
        # Default implementation based on common patterns
        content_type_str = metadata.get('content_type', '').lower()
        
        if any(video_indicator in content_type_str for video_indicator in ['video', 'mp4', 'webm']):
            return ContentType.VIDEO
        elif any(audio_indicator in content_type_str for audio_indicator in ['audio', 'mp3', 'wav']):
            return ContentType.AUDIO
        elif any(image_indicator in content_type_str for image_indicator in ['image', 'jpg', 'png', 'gif']):
            return ContentType.IMAGE
        elif any(text_indicator in content_type_str for text_indicator in ['text', 'post', 'tweet']):
            return ContentType.TEXT
        else:
            return ContentType.MIXED
    
    async def close(self):
        """
Clean up crawler resources."""
        
        # Override in specific crawlers if needed
        logger.info("Closing %s crawler", self.__class__.__name__)
