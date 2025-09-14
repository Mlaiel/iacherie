"""Base Collector Infrastructure
=============================

Abstract base class for consolidated platform collectors.
Provides standardized interface for content collection across all platforms.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Any, Union, AsyncGenerator
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class CollectorStatus(Enum):
    """Collector status enumeration."""
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    ERROR = "error"
    COMPLETED = "completed"

@dataclass
class CollectorResult:
    """Standardized collector result structure."""
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
    
    # Additional fields for enhanced functionality
    engagement_metrics: Optional[Dict[str, Any]] = None
    location_data: Optional[Dict[str, Any]] = None
    media_urls: Optional[List[str]] = None
    hashtags: Optional[List[str]] = None
    mentions: Optional[List[str]] = None
    language: Optional[str] = None
    sentiment_score: Optional[float] = None

@dataclass 
class CollectionConfig:
    """Configuration for content collection operations."""
    max_results: int = 50
    include_metadata: bool = True
    include_engagement: bool = True
    include_media: bool = False
    rate_limit_delay: float = 1.0
    timeout_seconds: int = 30
    retry_attempts: int = 3

class RateLimiter:
    """Basic rate limiter for collectors."""
    
    def __init__(self, max_requests -> None: int = 60, time_window -> None: int = 60) -> None:
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = []
    
    async def wait_if_needed(self) -> None:
        """Wait if rate limit would be exceeded."""
        now = time.time()
        # Remove old requests outside time window
        self.requests = [req_time for req_time in self.requests 
                        if now - req_time < self.time_window]
        
        # Check if we need to wait
        if len(self.requests) >= self.max_requests:
            oldest_request = min(self.requests)
            wait_time = self.time_window - (now - oldest_request)
            if wait_time > 0:
                logger.info(f"Rate limit reached, waiting {wait_time:.2f} seconds")
                await asyncio.sleep(wait_time)
        
        # Record this request
        self.requests.append(now)

class BaseCollector(ABC):
    """
    Abstract base class for platform content collectors.
    
    Consolidates multiple specialized crawler functionalities into
    a single, comprehensive collector for each platform.
    """
    
    def __init__(self, platform_name -> None: str, rate_limit -> None: int = 60) -> None:
        self.platform_name = platform_name
        self.rate_limiter = RateLimiter(max_requests=rate_limit)
        self.status = CollectorStatus.IDLE
        self.total_collected = 0
        self.last_collection_time: Optional[datetime] = None
        
        # Initialize collection statistics
        self.stats = {
            'successful_collections': 0,
            'failed_collections': 0,
            'total_requests': 0,
            'avg_response_time': 0.0
        }
        
        logger.info(f"Initialized {platform_name} collector")
    
    @abstractmethod
    async def search_content(self, query: str, config: CollectionConfig) -> List[CollectorResult]:
        """Search for content matching the query."""
        pass
    
    @abstractmethod
    async def get_content_details(self, content_id: str) -> Optional[CollectorResult]:
        """Get detailed information about specific content."""
        pass
    
    @abstractmethod
    async def get_user_content(self, user_id: str, config: CollectionConfig) -> List[CollectorResult]:
        """Get content from a specific user."""
        pass
    
    @abstractmethod
    async def monitor_hashtags(self, hashtags: List[str], config: CollectionConfig) -> AsyncGenerator[CollectorResult, None]:
        """Monitor content for specific hashtags in real-time."""
        pass
    
    @abstractmethod
    async def get_trending_content(self, config: CollectionConfig) -> List[CollectorResult]:
        """Get currently trending content."""
        pass
    
    async def collect_analytics(self, content_id: str) -> Dict[str, Any]:
        """Collect analytics data for content (default implementation)."""
        logger.warning(f"Analytics collection not implemented for {self.platform_name}")
        return {}
    
    async def detect_violations(self, content: CollectorResult) -> List[str]:
        """Detect potential violations in content (default implementation)."""
        logger.warning(f"Violation detection not implemented for {self.platform_name}")
        return []
    
    def get_platform_info(self) -> Dict[str, Any]:
        """Get platform information and capabilities."""
        return {
            'platform': self.platform_name,
            'status': self.status.value,
            'stats': self.stats,
            'last_collection': self.last_collection_time.isoformat() if self.last_collection_time else None,
            'total_collected': self.total_collected
        }
    
    def update_stats(self, success -> None: bool, response_time -> None: float) -> None:
        """Update collection statistics."""
        self.stats['total_requests'] += 1
        
        if success:
            self.stats['successful_collections'] += 1
            self.total_collected += 1
        else:
            self.stats['failed_collections'] += 1
        
        # Update average response time
        current_avg = self.stats['avg_response_time']
        total_requests = self.stats['total_requests']
        self.stats['avg_response_time'] = ((current_avg * (total_requests - 1)) + response_time) / total_requests
        
        self.last_collection_time = datetime.now()