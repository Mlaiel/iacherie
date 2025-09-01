"""🔍 Enterprise Base Platform Crawler Infrastructure
=================================================

Advanced abstract base class and standardized structures for enterprise-grade 
platform crawlers. Provides comprehensive interface for multi-platform content 
discovery with industrial-strength monitoring, rate limiting, and analytics.

Enterprise Features:
- Standardized crawling interface across all platforms
- Advanced rate limiting with exponential backoff
- Real-time monitoring with webhook notifications
- Performance analytics and metrics collection
- Intelligent retry mechanisms and circuit breakers
- Content deduplication and fingerprinting
- Anti-detection mechanisms and proxy support
- Comprehensive error handling and recovery
- Multi-threaded and async operation support

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ STRICT WARNING: Unauthorized use, copying, or distribution of this code 
is strictly prohibited without explicit written permission from Fahed Mlaiel.
Contact: mlaiel@live.de for licensing and authorization.
"""

import asyncio
import logging
import hashlib
import random
import time
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Set, Callable, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from collections import defaultdict, deque
import json

logger = logging.getLogger(__name__)

class CrawlerStatus(str, Enum):
    """
Comprehensive crawler status enumeration."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    RATE_LIMITED = "rate_limited"
    MAINTENANCE = "maintenance"
    CIRCUIT_BREAKER_OPEN = "circuit_breaker_open"
    INITIALIZING = "initializing"
    SHUTTING_DOWN = "shutting_down"

class ContentType(str, Enum):
    """Content type enumeration for standardized classification."""

    VIDEO = "video"
    AUDIO = "audio"
    IMAGE = "image"
    TEXT = "text"
    LIVE_STREAM = "live_stream"
    STORY = "story"
    REEL = "reel"
    PODCAST = "podcast"
    ARTICLE = "article"
    PLAYLIST = "playlist"
    CHANNEL = "channel"
    PROFILE = "profile"
    UNKNOWN = "unknown"

class Priority(str, Enum):
    """Task priority levels for intelligent scheduling."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    BACKGROUND = "background"

@dataclass
class CrawlResult:
    """Enhanced standardized crawl result structure with comprehensive metadata."""
    platform: str
    url: str
    title: Optional[str]
    description: Optional[str]
    content_type: ContentType
    file_url: Optional[str]
    metadata: Dict[str, Any]
    discovered_at: datetime
    fingerprint_candidates: List[str]
    
    # Enhanced fields for enterprise use
    confidence_score: float = 0.0
    content_hash: Optional[str] = None
    author_info: Dict[str, Any] = field(default_factory=dict)
    engagement_metrics: Dict[str, int] = field(default_factory=dict)
    technical_metadata: Dict[str, Any] = field(default_factory=dict)
    detection_score: float = 0.0
    priority: Priority = Priority.MEDIUM
    source_quality: str = "unknown"
    language: Optional[str] = None
    geographic_data: Dict[str, Any] = field(default_factory=dict)
    timestamp_extracted: Optional[datetime] = None
    related_content: List[str] = field(default_factory=list)
    violations_detected: List[str] = field(default_factory=list)

@dataclass
class RateLimitInfo:
    """Rate limiting information structure."""
    requests_per_minute: int
    requests_per_hour: int
    requests_per_day: int
    current_minute_count: int = 0
    current_hour_count: int = 0
    current_day_count: int = 0
    last_request_time: Optional[datetime] = None
    reset_time: Optional[datetime] = None
    backoff_until: Optional[datetime] = None

@dataclass
class CircuitBreakerState:
    """
Circuit breaker pattern implementation for fault tolerance."""
    failure_threshold: int = 5
    recovery_timeout: int = 60
    failure_count: int = 0
    last_failure_time: Optional[datetime] = None
    state: str = "closed"  # closed, open, half_open

class PerformanceMetrics:
    """Advanced performance monitoring and analytics."""
    
    def __init__(self):
        self.request_times: deque = deque(maxlen=1000)
        self.error_rates: Dict[str, int] = defaultdict(int)
        self.success_count = 0
        self.total_requests = 0
        self.bandwidth_usage = 0
        self.cache_hits = 0
        self.cache_misses = 0
        
    def record_request(self, duration: float, success: bool, error_type: str = None):
        """
Record request performance metrics."""
        self.request_times.append(duration)
        self.total_requests += 1
        
        if success:
            self.success_count += 1
        elif error_type:
            self.error_rates[error_type] += 1
    
    def get_avg_response_time(self) -> float:
        """
Calculate average response time."""
        return sum(self.request_times) / len(self.request_times) if self.request_times else 0.0
    
    def get_success_rate(self) -> float:
        """
Calculate success rate percentage."""
        return (self.success_count / max(self.total_requests, 1)) * 100

class BasePlatformCrawler(ABC):
    """
    Enterprise-grade abstract base class for platform crawlers.
    
    Provides comprehensive standardized interface and advanced functionality for:
    - Intelligent content discovery and search
    - Advanced rate limiting with circuit breaker pattern
    - Real-time monitoring and alerting systems
    - Performance analytics and optimization
    - Anti-detection and stealth mechanisms
    - Result standardization and quality scoring
    - Fault tolerance and recovery mechanisms
    - Distributed crawling coordination
    """
    
    # Class-level configuration requirements
    REQUIRED_CONFIG_FIELDS: List[str] = []
    DEFAULT_RATE_LIMITS = RateLimitInfo(
        requests_per_minute=60,
        requests_per_hour=1000,
        requests_per_day=10000
    )
    
    def __init__(self, platform: str, config: Dict[str, Any]):
        """
Initialize enhanced base crawler with enterprise features."""
        self.platform = platform
        self.config = config
        self.status = CrawlerStatus.INITIALIZING
        self.last_crawl = None
        
        # Enhanced monitoring and task management
        self.monitoring_tasks: Dict[str, asyncio.Task] = {}
        self.monitoring_channels: Dict[str, Dict[str, Any]] = {}
        self.webhook_callbacks: List[Callable] = []
        
        # Rate limiting and circuit breaker
        self.rate_limits = self._load_rate_limits()
        self.circuit_breaker = CircuitBreakerState()
        
        # Performance monitoring
        self.performance_metrics = PerformanceMetrics()
        
        # Content tracking and deduplication
        self.seen_content_hashes: Set[str] = set()
        self.content_cache: Dict[str, CrawlResult] = {}
        
        # Anti-detection features
        self.user_agents = self._load_user_agents()
        self.proxy_pool: List[str] = config.get('proxy_pool', [])
        self.current_proxy_index = 0
        
        # Alert thresholds
        self.alert_thresholds = {
            'error_rate': config.get('error_rate_threshold', 10.0),
            'response_time': config.get('response_time_threshold', 5.0),
            'success_rate': config.get('success_rate_threshold', 95.0)
        }
        
        logger.info(f"Initialized enterprise {platform} crawler with enhanced features")
        self.status = CrawlerStatus.INACTIVE
    
    @abstractmethod
    async def search_content(
        self,
        query: str,
        content_type: ContentType = ContentType.UNKNOWN,
        max_results: int = 50,
        filters: Optional[Dict[str, Any]] = None,
        priority: Priority = Priority.MEDIUM
    ) -> List[CrawlResult]:
        """
        Advanced content search with intelligent filtering and prioritization.
        
        Args:
            query: Search query string with support for advanced operators
            content_type: Specific type of content to search for
            max_results: Maximum number of results to return
            filters: Advanced search filters (date range, author, etc.)
            priority: Request priority for intelligent scheduling
            
        Returns:
            List of enhanced CrawlResult objects with quality scoring
        """
        pass
    
    @abstractmethod
    async def check_rate_limits(self) -> bool:
        """
        Advanced rate limit checking with predictive analysis.
        
        Returns:
            True if within limits, False if rate limited
        """
        pass
    
    @abstractmethod 
    async def authenticate(self) -> bool:
        """
        Platform-specific authentication with automatic token refresh.
        
        Returns:
            True if authentication successful
        """
        pass
    
    @abstractmethod
    async def get_content_details(self, content_url: str) -> Optional[CrawlResult]:
        """
        Extract detailed information from specific content URL.
        
        Args:
            content_url: Direct URL to content
            
        Returns:
            Detailed CrawlResult or None if not accessible
        """
        pass
    
    # Enterprise utility methods
    
    def _load_rate_limits(self) -> RateLimitInfo:
        """
Load platform-specific rate limits from configuration."""
        return RateLimitInfo(
            requests_per_minute=self.config.get('rate_limit_rpm', self.DEFAULT_RATE_LIMITS.requests_per_minute),
            requests_per_hour=self.config.get('rate_limit_rph', self.DEFAULT_RATE_LIMITS.requests_per_hour),
            requests_per_day=self.config.get('rate_limit_rpd', self.DEFAULT_RATE_LIMITS.requests_per_day)
        )
    
    def _load_user_agents(self) -> List[str]:
        """
Load diverse user agent strings for anti-detection."""
        default_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:122.0) Gecko/20100101 Firefox/122.0'
        ]
        return self.config.get('user_agents', default_agents)
    
    async def _check_circuit_breaker(self) -> bool:
        """
Check and manage circuit breaker state for fault tolerance."""
        now = datetime.utcnow()
        
        if self.circuit_breaker.state == "open":
            if (now - self.circuit_breaker.last_failure_time).seconds >= self.circuit_breaker.recovery_timeout:
                self.circuit_breaker.state = "half_open"
                logger.info(f"{self.platform} circuit breaker moved to half-open state")
            else:
                return False
        
        return self.circuit_breaker.state != "open"
    
    async def _record_circuit_breaker_result(self, success: bool):
        """Record request result for circuit breaker pattern."""
        if success:
            if self.circuit_breaker.state == "half_open":
                self.circuit_breaker.state = "closed"
                self.circuit_breaker.failure_count = 0
                logger.info(f"{self.platform} circuit breaker closed after successful recovery")
        else:
            self.circuit_breaker.failure_count += 1
            self.circuit_breaker.last_failure_time = datetime.utcnow()
            
            if self.circuit_breaker.failure_count >= self.circuit_breaker.failure_threshold:
                self.circuit_breaker.state = "open"
                self.status = CrawlerStatus.CIRCUIT_BREAKER_OPEN
                logger.warning(f"{self.platform} circuit breaker opened due to failures")
    
    async def _apply_rate_limiting(self) -> bool:
        """Advanced rate limiting with exponential backoff."""
        now = datetime.utcnow()
        
        # Check if in backoff period
        if self.rate_limits.backoff_until and now < self.rate_limits.backoff_until:
            return False
        
        # Reset counters if time windows have passed
        if self.rate_limits.last_request_time:
            time_diff = (now - self.rate_limits.last_request_time).total_seconds()
            
            if time_diff >= 60:  # Reset minute counter
                self.rate_limits.current_minute_count = 0
            if time_diff >= 3600:  # Reset hour counter
                self.rate_limits.current_hour_count = 0
            if time_diff >= 86400:  # Reset day counter
                self.rate_limits.current_day_count = 0
        
        # Check rate limits
        if (self.rate_limits.current_minute_count >= self.rate_limits.requests_per_minute or
            self.rate_limits.current_hour_count >= self.rate_limits.requests_per_hour or
            self.rate_limits.current_day_count >= self.rate_limits.requests_per_day):
            
            # Apply exponential backoff
            backoff_seconds = min(300, 2 ** self.circuit_breaker.failure_count)
            self.rate_limits.backoff_until = now + timedelta(seconds=backoff_seconds)
            self.status = CrawlerStatus.RATE_LIMITED
            
            logger.warning(f"{self.platform} rate limited, backing off for {backoff_seconds} seconds")
            return False
        
        return True
    
    def _get_random_user_agent(self) -> str:
        """Get random user agent for anti-detection."""
        return random.choice(self.user_agents)
    
    def _get_next_proxy(self) -> Optional[str]:
        """
Get next proxy from rotation pool."""
        if not self.proxy_pool:
            return None
        
        proxy = self.proxy_pool[self.current_proxy_index]
        self.current_proxy_index = (self.current_proxy_index + 1) % len(self.proxy_pool)
        return proxy
    
    def _generate_content_hash(self, content: Union[str, bytes]) -> str:
        """
Generate SHA-256 hash for content deduplication."""
        if isinstance(content, str):
            content = content.encode('utf-8')
        return hashlib.sha256(content).hexdigest()
    
    def _is_duplicate_content(self, content_hash: str) -> bool:
        """
Check if content has been seen before."""
        return content_hash in self.seen_content_hashes
    
    def _add_to_content_cache(self, result: CrawlResult):
        """
Add result to content cache with size management."""
        if len(self.content_cache) > 10000:  # Limit cache size
            # Remove oldest entries
            oldest_keys = list(self.content_cache.keys())[:1000]
            for key in oldest_keys:
                del self.content_cache[key]
        
        cache_key = f"{result.platform}:{result.url}"
        self.content_cache[cache_key] = result
    
    async def _trigger_webhooks(self, event_type: str, data: Dict[str, Any]):
        """Trigger registered webhook callbacks for events."""
        for callback in self.webhook_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(event_type, data)
                else:
                    callback(event_type, data)
            except Exception as e:
                logger.error(f"Webhook callback error: {e}")
    
    def register_webhook(self, callback: Callable):
        """Register webhook callback for real-time notifications."""
        self.webhook_callbacks.append(callback)
    
    async def _check_alert_conditions(self):
        """
Check performance metrics against alert thresholds."""
        metrics = self.performance_metrics
        
        # Check error rate
        error_rate = (1 - metrics.get_success_rate() / 100) * 100
        if error_rate > self.alert_thresholds['error_rate']:
            await self._trigger_webhooks('high_error_rate', {
                'platform': self.platform,
                'error_rate': error_rate,
                'threshold': self.alert_thresholds['error_rate']
            })
        
        # Check response time
        avg_response_time = metrics.get_avg_response_time()
        if avg_response_time > self.alert_thresholds['response_time']:
            await self._trigger_webhooks('slow_response_time', {
                'platform': self.platform,
                'avg_response_time': avg_response_time,
                'threshold': self.alert_thresholds['response_time']
            })
        
        # Check success rate
        success_rate = metrics.get_success_rate()
        if success_rate < self.alert_thresholds['success_rate']:
            await self._trigger_webhooks('low_success_rate', {
                'platform': self.platform,
                'success_rate': success_rate,
                'threshold': self.alert_thresholds['success_rate']
            })
        """
        Check if crawler is within rate limits.
        
        Returns:
            True if within limits, False if rate limited
        """
        pass
    
    async def start_monitoring(
        self,
        monitor_id: str,
        search_queries: List[str],
        callback_func: callable = None,
        interval_minutes: int = 30
    ) -> bool:
        """
        Start continuous monitoring for content.
        
        Args:
            monitor_id: Unique identifier for monitoring task
            search_queries: List of queries to monitor
            callback_func: Function to call with new results
            interval_minutes: Monitoring interval in minutes
            
        Returns:
            True if monitoring started successfully
        """
        try:
            if monitor_id in self.monitoring_tasks:
                logger.warning(f"Monitoring already active for {monitor_id}")
                return False
            
            # Create monitoring task
            task = asyncio.create_task(
                self._continuous_monitor(monitor_id, search_queries, callback_func, interval_minutes)
            )
            self.monitoring_tasks[monitor_id] = task
            
            logger.info(f"Started monitoring {monitor_id} on {self.platform}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start monitoring {monitor_id}: {e}")
            return False
    
    async def stop_monitoring(self, monitor_id: str) -> bool:
        """
        Stop continuous monitoring.
        
        Args:
            monitor_id: Identifier of monitoring task to stop
            
        Returns:
            True if monitoring stopped successfully
        """
        try:
            if monitor_id in self.monitoring_tasks:
                self.monitoring_tasks[monitor_id].cancel()
                del self.monitoring_tasks[monitor_id]
                
                # Clean up monitoring channels
                if monitor_id in self.monitoring_channels:
                    del self.monitoring_channels[monitor_id]
                
                logger.info(f"Stopped monitoring {monitor_id} on {self.platform}")
                return True
            else:
                logger.warning(f"No active monitoring found for {monitor_id}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to stop monitoring {monitor_id}: {e}")
            return False
    
    async def _continuous_monitor(
        self,
        monitor_id: str,
        search_queries: List[str],
        callback_func: callable,
        interval_minutes: int
    ):
        """
        Continuous monitoring loop.
        
        Args:
            monitor_id: Monitoring task identifier
            search_queries: Queries to monitor
            callback_func: Callback function for results
            interval_minutes: Monitoring interval
        """
        logger.info(f"Starting continuous monitoring {monitor_id} on {self.platform}")
        
        last_results = set()
        
        try:
            while True:
                new_results = []
                
                for query in search_queries:
                    try:
                        results = await self.search_content(query, max_results=50)
                        
                        # Filter out previously seen results
                        for result in results:
                            result_hash = hash((result.url, result.title))
                            if result_hash not in last_results:
                                new_results.append(result)
                                last_results.add(result_hash)
                        
                    except Exception as e:
                        logger.error(f"Error in monitoring query '{query}': {e}")
                
                # Call callback with new results
                if new_results and callback_func:
                    try:
                        await callback_func(new_results)
                    except Exception as e:
                        logger.error(f"Error in monitoring callback: {e}")
                
                # Wait before next monitoring cycle
                await asyncio.sleep(interval_minutes * 60)
                
        except asyncio.CancelledError:
            logger.info(f"Monitoring cancelled for {monitor_id} on {self.platform}")
        except Exception as e:
            logger.error(f"Monitoring error for {monitor_id}: {e}")
    
    async def get_status(self) -> Dict[str, Any]:
        """
        Get crawler status information.
        
        Returns:
            Dictionary with status information
        """
        return {
            "platform": self.platform,
            "status": self.status.value,
            "last_crawl": self.last_crawl.isoformat() if self.last_crawl else None,
            "rate_limit_reset": self.rate_limit_reset.isoformat() if self.rate_limit_reset else None,
            "active_monitoring": len(self.monitoring_tasks),
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "failed_requests": self.failed_requests,
            "success_rate": self.successful_requests / max(self.total_requests, 1) * 100
        }
    
    async def validate_config(self) -> bool:
        """
        Validate crawler configuration.
        
        Returns:
            True if configuration is valid
        """
        required_fields = getattr(self, 'REQUIRED_CONFIG_FIELDS', [])
        
        for field in required_fields:
            if field not in self.config:
                logger.error(f"Missing required config field: {field}")
                return False
            
            if not self.config[field]:
                logger.error(f"Empty required config field: {field}")
                return False
        
        return True
    
    def _update_stats(self, success: bool):
        """Update crawler statistics."""
        self.total_requests += 1
        if success:
            self.successful_requests += 1
        else:
            self.failed_requests += 1
        
        self.last_crawl = datetime.utcnow()
    
    def _standardize_result(
        self,
        platform: str,
        url: str,
        title: str,
        description: str,
        content_type: str,
        metadata: Dict[str, Any],
        file_url: Optional[str] = None
    ) -> CrawlResult:
        """
        Create standardized crawl result.
        
        Args:
            platform: Platform name
            url: Content URL
            title: Content title
            description: Content description
            content_type: Type of content
            metadata: Additional metadata
            file_url: Direct file URL if available
            
        Returns:
            CrawlResult object
        """
        # Generate fingerprint candidates
        fingerprint_candidates = [url]
        
        if title:
            fingerprint_candidates.append(title.lower().strip())
        
        if description:
            fingerprint_candidates.append(description.lower().strip())
        
        # Add platform-specific fingerprint data
        if 'hashtags' in metadata:
            fingerprint_candidates.extend(metadata['hashtags'])
        
        if 'author' in metadata:
            fingerprint_candidates.append(metadata['author'].lower())
        
        # Remove duplicates and empty strings
        fingerprint_candidates = list(filter(None, set(fingerprint_candidates)))
        
        return CrawlResult(
            platform=platform,
            url=url,
            title=title,
            description=description,
            content_type=content_type,
            file_url=file_url,
            metadata=metadata,
            discovered_at=datetime.utcnow(),
            fingerprint_candidates=fingerprint_candidates
        )
    
    async def cleanup(self):
        """
        Cleanup crawler resources.
        
        Should be called when shutting down the crawler.
        """
        logger.info(f"Cleaning up {self.platform} crawler...")
        
        # Cancel all monitoring tasks
        for monitor_id, task in self.monitoring_tasks.items():
            try:
                task.cancel()
                logger.info(f"Cancelled monitoring task {monitor_id}")
            except Exception as e:
                logger.error(f"Error cancelling monitoring task {monitor_id}: {e}")
        
        # Wait for tasks to complete
        if self.monitoring_tasks:
            await asyncio.gather(*self.monitoring_tasks.values(), return_exceptions=True)
        
        self.monitoring_tasks.clear()
        self.monitoring_channels.clear()
        
        # Set status to inactive
        self.status = CrawlerStatus.INACTIVE
        
        logger.info(f"{self.platform} crawler cleanup completed")

# Export main classes and types
__all__ = [
    'BasePlatformCrawler',
    'CrawlResult',
    'CrawlerStatus'
]
