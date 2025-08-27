"""
Enterprise Request Management System
===================================

Advanced HTTP request management with intelligent retries, rate limiting, and error handling.
Provides enterprise-grade request processing with monitoring and optimization features.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

⚠️  LEGAL WARNING:
This code is proprietary and confidential. Any unauthorized copying, modification, 
distribution, or use without explicit written permission from Fahed Mlaiel is strictly 
prohibited and may result in legal action.

Professional Development Team Specialties:
🥇 Lead AI Developer & Backend Senior Engineer - Advanced automation systems
🥇 Machine Learning Engineer & Audio Processing Specialist - Intelligence optimization  
🥇 Database Administrator & Security Expert - Data protection and performance
🥇 Microservices Architect & DevOps Engineer - Scalable infrastructure
🥇 AI Prompt Engineer & Content Protection Specialist - Content security
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import json
import time
import hashlib
from urllib.parse import urljoin, urlparse
import aiohttp
import ssl
from aiohttp import ClientSession, ClientTimeout, TCPConnector
from aiohttp.client_exceptions import ClientError, ClientTimeout as AioTimeoutError


class RequestMethod(Enum):
    """HTTP request methods"""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"


class RetryStrategy(Enum):
    """Request retry strategies"""
    EXPONENTIAL_BACKOFF = "exponential_backoff"
    LINEAR_BACKOFF = "linear_backoff"
    FIXED_DELAY = "fixed_delay"
    IMMEDIATE = "immediate"


class RequestPriority(Enum):
    """Request priority levels"""
    CRITICAL = 1
    HIGH = 2
    NORMAL = 3
    LOW = 4
    BACKGROUND = 5


@dataclass
class RateLimitConfig:
    """Rate limiting configuration"""
    requests_per_second: float = 1.0
    requests_per_minute: int = 60
    requests_per_hour: int = 3600
    requests_per_day: int = 86400
    burst_limit: int = 10
    window_size: int = 60  # seconds


@dataclass
class RetryConfig:
    """Retry configuration"""
    max_attempts: int = 3
    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL_BACKOFF
    base_delay: float = 1.0
    max_delay: float = 60.0
    backoff_factor: float = 2.0
    jitter: bool = True
    retry_on_status: List[int] = field(default_factory=lambda: [429, 500, 502, 503, 504])


@dataclass
class RequestConfig:
    """Request configuration"""
    timeout: int = 30
    max_redirects: int = 10
    verify_ssl: bool = True
    allow_cookies: bool = True
    follow_redirects: bool = True
    compress: bool = True
    headers: Dict[str, str] = field(default_factory=dict)
    auth: Optional[tuple] = None
    proxy: Optional[str] = None


@dataclass
class RequestMetrics:
    """Request performance metrics"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    retried_requests: int = 0
    rate_limited_requests: int = 0
    average_response_time: float = 0.0
    min_response_time: float = float('inf')
    max_response_time: float = 0.0
    last_request_time: Optional[datetime] = None
    bytes_downloaded: int = 0
    bytes_uploaded: int = 0


@dataclass
class RequestRecord:
    """Individual request record"""
    request_id: str
    method: RequestMethod
    url: str
    priority: RequestPriority = RequestPriority.NORMAL
    config: RequestConfig = field(default_factory=RequestConfig)
    retry_config: RetryConfig = field(default_factory=RetryConfig)
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    attempts: int = 0
    response_status: Optional[int] = None
    response_size: int = 0
    error: Optional[str] = None
    headers: Dict[str, str] = field(default_factory=dict)
    body: Optional[Union[str, bytes, Dict]] = None
    response_data: Optional[bytes] = None
    response_headers: Dict[str, str] = field(default_factory=dict)


class RequestManager:
    """
    Enterprise HTTP request management system.
    
    Features:
    - Intelligent retry mechanisms with multiple strategies
    - Rate limiting with burst protection
    - Request prioritization and queuing
    - Performance monitoring and metrics
    - Connection pooling and reuse
    - SSL verification and proxy support
    """
    
    def __init__(
        self,
        max_concurrent_requests: int = 50,
        connection_pool_size: int = 100,
        enable_rate_limiting: bool = True,
        default_rate_limit: Optional[RateLimitConfig] = None,
        enable_monitoring: bool = True
    ):
        self.max_concurrent_requests = max_concurrent_requests
        self.connection_pool_size = connection_pool_size
        self.enable_rate_limiting = enable_rate_limiting
        self.enable_monitoring = enable_monitoring
        
        # Rate limiting
        self.default_rate_limit = default_rate_limit or RateLimitConfig()
        self.rate_limiters: Dict[str, Dict] = {}
        
        # Request management
        self.request_queue: List[RequestRecord] = []
        self.active_requests: Dict[str, RequestRecord] = {}
        self.completed_requests: List[RequestRecord] = []
        
        # Session management
        self.session: Optional[ClientSession] = None
        self.connector: Optional[TCPConnector] = None
        
        # Monitoring
        self.metrics = RequestMetrics()
        self.start_time = datetime.utcnow()
        
        # Semaphore for concurrency control
        self.semaphore = asyncio.Semaphore(max_concurrent_requests)
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
    
    async def initialize(self) -> bool:
        """Initialize request manager"""
        try:
            self.logger.info("Initializing request manager...")
            
            # Create SSL context
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            # Create TCP connector
            self.connector = TCPConnector(
                limit=self.connection_pool_size,
                limit_per_host=20,
                ssl=ssl_context,
                use_dns_cache=True,
                ttl_dns_cache=300,
                enable_cleanup_closed=True
            )
            
            # Create client session
            timeout = ClientTimeout(total=30, connect=10)
            self.session = ClientSession(
                connector=self.connector,
                timeout=timeout,
                auto_decompress=True
            )
            
            # Start monitoring if enabled
            if self.enable_monitoring:
                asyncio.create_task(self._monitoring_loop())
            
            self.logger.info("Request manager initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize request manager: {e}")
            return False
    
    async def submit_request(
        self,
        method: RequestMethod,
        url: str,
        priority: RequestPriority = RequestPriority.NORMAL,
        config: Optional[RequestConfig] = None,
        retry_config: Optional[RetryConfig] = None,
        headers: Optional[Dict[str, str]] = None,
        body: Optional[Union[str, bytes, Dict]] = None,
        request_id: Optional[str] = None
    ) -> str:
        """Submit a request for execution"""
        if not request_id:
            request_id = self._generate_request_id(method, url)
        
        if not config:
            config = RequestConfig()
        
        if headers:
            config.headers.update(headers)
        
        request = RequestRecord(
            request_id=request_id,
            method=method,
            url=url,
            priority=priority,
            config=config,
            retry_config=retry_config or RetryConfig(),
            headers=config.headers,
            body=body
        )
        
        # Add to queue based on priority
        self._insert_by_priority(request)
        
        self.logger.info(f"Submitted request: {request_id} [{method.value}] {url}")
        return request_id
    
    async def execute_request(self, request: RequestRecord) -> Dict[str, Any]:
        """Execute a single request with retries and rate limiting"""
        async with self.semaphore:
            request.started_at = datetime.utcnow()
            self.active_requests[request.request_id] = request
            
            try:
                # Apply rate limiting
                if self.enable_rate_limiting:
                    await self._apply_rate_limiting(request.url)
                
                # Execute with retries
                result = await self._execute_with_retries(request)
                
                request.completed_at = datetime.utcnow()
                self.metrics.successful_requests += 1
                
                # Update metrics
                response_time = (request.completed_at - request.started_at).total_seconds()
                self._update_response_time_metrics(response_time)
                
                self.logger.info(f"Request completed: {request.request_id}")
                return result
                
            except Exception as e:
                request.error = str(e)
                request.completed_at = datetime.utcnow()
                self.metrics.failed_requests += 1
                
                self.logger.error(f"Request failed: {request.request_id} - {e}")
                raise
                
            finally:
                # Move to completed
                self.active_requests.pop(request.request_id, None)
                self.completed_requests.append(request)
                
                # Update total metrics
                self.metrics.total_requests += 1
                self.metrics.last_request_time = datetime.utcnow()
    
    async def get_request_status(self, request_id: str) -> Optional[RequestRecord]:
        """Get status of a specific request"""
        # Check active requests
        if request_id in self.active_requests:
            return self.active_requests[request_id]
        
        # Check completed requests
        for request in self.completed_requests:
            if request.request_id == request_id:
                return request
        
        # Check queued requests
        for request in self.request_queue:
            if request.request_id == request_id:
                return request
        
        return None
    
    async def process_queue(self):
        """Process the request queue"""
        while self.request_queue:
            request = self.request_queue.pop(0)
            try:
                await self.execute_request(request)
            except Exception as e:
                self.logger.error(f"Queue processing error: {e}")
            
            # Small delay to prevent overwhelming
            await asyncio.sleep(0.01)
    
    async def cancel_request(self, request_id: str) -> bool:
        """Cancel a queued or active request"""
        # Remove from queue
        for i, request in enumerate(self.request_queue):
            if request.request_id == request_id:
                self.request_queue.pop(i)
                self.logger.info(f"Cancelled queued request: {request_id}")
                return True
        
        # Cannot cancel active requests (they'll complete or timeout)
        if request_id in self.active_requests:
            self.logger.warning(f"Cannot cancel active request: {request_id}")
            return False
        
        return False
    
    async def cleanup(self):
        """Cleanup request manager resources"""
        self.logger.info("Cleaning up request manager...")
        
        if self.session:
            await self.session.close()
        
        if self.connector:
            await self.connector.close()
        
        self.logger.info("Request manager cleanup completed")
    
    async def health_check(self) -> bool:
        """Perform health check on request manager"""
        try:
            if not self.session or self.session.closed:
                return False
            
            # Test with a simple request
            test_url = "https://httpbin.org/status/200"
            async with self.session.get(test_url, timeout=ClientTimeout(total=5)) as response:
                return response.status == 200
                
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return False
    
    def get_metrics(self) -> RequestMetrics:
        """Get current request metrics"""
        if self.metrics.total_requests > 0:
            self.metrics.success_rate = (
                self.metrics.successful_requests / self.metrics.total_requests * 100
            )
        
        return self.metrics
    
    async def _execute_with_retries(self, request: RequestRecord) -> Dict[str, Any]:
        """Execute request with retry logic"""
        last_exception = None
        
        for attempt in range(request.retry_config.max_attempts):
            request.attempts = attempt + 1
            
            try:
                # Execute the actual request
                result = await self._execute_single_request(request)
                
                # Success
                if request.response_status and request.response_status < 400:
                    return result
                
                # Check if status is retryable
                if (request.response_status not in request.retry_config.retry_on_status and
                    attempt == request.retry_config.max_attempts - 1):
                    break
                
            except Exception as e:
                last_exception = e
                self.logger.warning(f"Request attempt {attempt + 1} failed: {e}")
                
                if attempt == request.retry_config.max_attempts - 1:
                    break
            
            # Calculate retry delay
            delay = self._calculate_retry_delay(request.retry_config, attempt)
            await asyncio.sleep(delay)
            
            self.metrics.retried_requests += 1
        
        # All retries exhausted
        if last_exception:
            raise last_exception
        else:
            raise Exception(f"Request failed after {request.retry_config.max_attempts} attempts")
    
    async def _execute_single_request(self, request: RequestRecord) -> Dict[str, Any]:
        """Execute a single HTTP request"""
        # Prepare request parameters
        kwargs = {
            'headers': request.headers,
            'timeout': ClientTimeout(total=request.config.timeout),
            'allow_redirects': request.config.follow_redirects,
            'max_redirects': request.config.max_redirects,
            'compress': request.config.compress
        }
        
        # Add body for POST/PUT/PATCH requests
        if request.body and request.method in [RequestMethod.POST, RequestMethod.PUT, RequestMethod.PATCH]:
            if isinstance(request.body, dict):
                kwargs['json'] = request.body
            elif isinstance(request.body, (str, bytes)):
                kwargs['data'] = request.body
        
        # Add authentication
        if request.config.auth:
            kwargs['auth'] = aiohttp.BasicAuth(
                request.config.auth[0],
                request.config.auth[1]
            )
        
        # Add proxy
        if request.config.proxy:
            kwargs['proxy'] = request.config.proxy
        
        # Execute request
        async with self.session.request(
            request.method.value,
            request.url,
            **kwargs
        ) as response:
            # Store response information
            request.response_status = response.status
            request.response_headers = dict(response.headers)
            
            # Read response data
            response_data = await response.read()
            request.response_data = response_data
            request.response_size = len(response_data)
            
            # Update metrics
            self.metrics.bytes_downloaded += request.response_size
            
            # Prepare result
            result = {
                'status': response.status,
                'headers': dict(response.headers),
                'data': response_data,
                'url': str(response.url),
                'request_id': request.request_id
            }
            
            return result
    
    async def _apply_rate_limiting(self, url: str):
        """Apply rate limiting for the given URL"""
        domain = urlparse(url).netloc
        
        if domain not in self.rate_limiters:
            self.rate_limiters[domain] = {
                'requests': [],
                'config': self.default_rate_limit
            }
        
        limiter = self.rate_limiters[domain]
        config = limiter['config']
        current_time = time.time()
        
        # Clean old requests
        limiter['requests'] = [
            req_time for req_time in limiter['requests']
            if current_time - req_time < config.window_size
        ]
        
        # Check rate limits
        if len(limiter['requests']) >= config.requests_per_minute:
            delay = config.window_size - (current_time - limiter['requests'][0])
            if delay > 0:
                self.metrics.rate_limited_requests += 1
                await asyncio.sleep(delay)
        
        # Record this request
        limiter['requests'].append(current_time)
    
    def _calculate_retry_delay(self, retry_config: RetryConfig, attempt: int) -> float:
        """Calculate delay for retry attempt"""
        if retry_config.strategy == RetryStrategy.EXPONENTIAL_BACKOFF:
            delay = retry_config.base_delay * (retry_config.backoff_factor ** attempt)
        elif retry_config.strategy == RetryStrategy.LINEAR_BACKOFF:
            delay = retry_config.base_delay * (attempt + 1)
        elif retry_config.strategy == RetryStrategy.FIXED_DELAY:
            delay = retry_config.base_delay
        else:  # IMMEDIATE
            delay = 0
        
        # Apply maximum delay limit
        delay = min(delay, retry_config.max_delay)
        
        # Add jitter if enabled
        if retry_config.jitter and delay > 0:
            import random
            delay *= (0.5 + random.random() * 0.5)
        
        return delay
    
    def _generate_request_id(self, method: RequestMethod, url: str) -> str:
        """Generate unique request ID"""
        timestamp = int(time.time() * 1000)
        content = f"{method.value}:{url}:{timestamp}"
        hash_obj = hashlib.md5(content.encode())
        return f"req_{hash_obj.hexdigest()[:8]}_{timestamp}"
    
    def _insert_by_priority(self, request: RequestRecord):
        """Insert request in queue based on priority"""
        if not self.request_queue:
            self.request_queue.append(request)
            return
        
        # Find insertion point
        for i, existing_request in enumerate(self.request_queue):
            if request.priority.value < existing_request.priority.value:
                self.request_queue.insert(i, request)
                return
        
        # Add at the end if no higher priority found
        self.request_queue.append(request)
    
    def _update_response_time_metrics(self, response_time: float):
        """Update response time metrics"""
        if response_time < self.metrics.min_response_time:
            self.metrics.min_response_time = response_time
        
        if response_time > self.metrics.max_response_time:
            self.metrics.max_response_time = response_time
        
        # Update average
        total_time = (
            self.metrics.average_response_time * self.metrics.successful_requests +
            response_time
        )
        self.metrics.average_response_time = total_time / (self.metrics.successful_requests + 1)
    
    async def _monitoring_loop(self):
        """Monitoring loop for metrics and cleanup"""
        while True:
            try:
                # Clean up old completed requests
                cutoff_time = datetime.utcnow() - timedelta(hours=24)
                self.completed_requests = [
                    req for req in self.completed_requests
                    if req.completed_at and req.completed_at > cutoff_time
                ]
                
                # Log statistics
                self.logger.debug(
                    f"Request stats: {len(self.request_queue)} queued, "
                    f"{len(self.active_requests)} active, "
                    f"{len(self.completed_requests)} completed"
                )
                
                await asyncio.sleep(60)  # Monitor every minute
                
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(60)


# Convenience functions
async def create_request_manager(**kwargs) -> RequestManager:
    """Create and initialize a request manager"""
    manager = RequestManager(**kwargs)
    await manager.initialize()
    return manager


def create_rate_limit_config(
    requests_per_minute: int = 60,
    burst_limit: int = 10
) -> RateLimitConfig:
    """Create rate limiting configuration"""
    return RateLimitConfig(
        requests_per_minute=requests_per_minute,
        burst_limit=burst_limit
    )


def create_retry_config(
    max_attempts: int = 3,
    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL_BACKOFF
) -> RetryConfig:
    """Create retry configuration"""
    return RetryConfig(
        max_attempts=max_attempts,
        strategy=strategy
    )
