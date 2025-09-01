"""Core Crawler Infrastructure
============================

Basic crawler infrastructure without heavy dependencies.
Provides foundation classes for platform-specific crawlers.
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Any, Union
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class CrawlerStatus(Enum):
    """
Crawler status enumeration."""

    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    ERROR = "error"
    COMPLETED = "completed"

@dataclass
class CrawlerResult:
    """Basic crawler result structure."""
    platform: str
    content_id: str
    content_type: str
    title: str
    description: str
    url: str
    author: str
    timestamp: float
    metadata: Dict[str, Any]
    raw_data: Dict[str, Any]

class RateLimiter:
    """
Basic rate limiter."""
    
    def __init__(self, max_requests: int = 60, time_window: int = 60):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = []
    
    async def wait_if_needed(self):
        """
Wait if rate limit would be exceeded."""
        now = time.time()
        # Remove old requests outside time window
        self.requests = [req_time for req_time in self.requests 
                        if now - req_time < self.time_window]
        
        if len(self.requests) >= self.max_requests:
            wait_time = self.time_window - (now - self.requests[0])
            if wait_time > 0:
                await asyncio.sleep(wait_time)
        
        self.requests.append(now)

class BaseCrawler(ABC):
    """
Abstract base crawler class."""
    
    def __init__(self, platform_name: str, rate_limit: int = 60):
        self.platform_name = platform_name
        self.rate_limiter = RateLimiter(max_requests=rate_limit)
        self.status = CrawlerStatus.IDLE
        
    @abstractmethod
    async def search_content(self, query: str, max_results: int = 50) -> List[CrawlerResult]:
        """
Search for content on the platform."""
        pass
    
    @abstractmethod
    async def get_content_details(self, content_id: str) -> Optional[CrawlerResult]:
        """
Get detailed information about specific content."""
        pass
    
    async def monitor_real_time(self, keywords: List[str], callback=None):
        """
Monitor platform for real-time content updates."""
        # Default implementation - override in platform-specific crawlers
        while True:
            try:
                for keyword in keywords:
                    results = await self.search_content(keyword, max_results=10)
                    if callback and results:
                        await callback(results)
                
                await asyncio.sleep(60)  # Check every minute
            except Exception as e:
                logger.error(f"Real-time monitoring error: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes on error