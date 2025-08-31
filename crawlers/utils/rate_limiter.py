"""Rate Limiter Module
===================

Professional rate limiting implementations for different platforms.
Implements intelligent rate limiting with backoff strategies and quota management.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

WARNING: This code is protected by copyright law. Any unauthorized copying, 
distribution, or modification is strictly prohibited and will result in 
legal action. Contact mlaiel@live.de for licensing.
"""
import asyncio
import logging
from typing import Dict, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
import time
from collections import deque
import redis
import json

logger = logging.getLogger(__name__)

@dataclass
class RateLimitInfo:
    """Rate limit information structure."""    requests_made: int
    requests_remaining: int
    reset_time: datetime
    retry_after: Optional[int]
    quota_used: int
    quota_limit: int

class RateLimiter:
    """    Base rate limiter with advanced features.
    
    Features:
    - Sliding window rate limiting
    - Burst protection
    - Quota management
    - Adaptive backoff
    - Redis-based distributed limiting
    - Platform-specific configurations
    """    
    def __init__(
        self,
        max_requests_per_minute: int = 60,
        burst_limit: int = 10,
        base_delay: float = 1.0,
        backoff_factor: float = 1.5,
        max_backoff: float = 300.0,
        redis_client: Optional[redis.Redis] = None
    ):
        """Initialize rate limiter."""        self.max_requests_per_minute = max_requests_per_minute
        self.burst_limit = burst_limit
        self.base_delay = base_delay
        self.backoff_factor = backoff_factor
        self.max_backoff = max_backoff
        self.redis_client = redis_client
        
        # Local tracking
        self.request_times = deque()
        self.last_request_time = 0
        self.current_delay = base_delay
        self.consecutive_rate_limits = 0
        
        # Quota tracking
        self.daily_quota_used = 0
        self.daily_quota_limit = None
        self.quota_reset_time = None
    
    async def wait_if_needed(self, identifier: str = "default") -> None:
        """Wait if rate limit would be exceeded."""        current_time = time.time()
        
        # Check distributed rate limiting (Redis)
        if self.redis_client:
            await self._check_distributed_rate_limit(identifier)
        
        # Clean old requests from sliding window
        self._clean_old_requests(current_time)
        
        # Check burst limit
        if len(self.request_times) >= self.burst_limit:
            burst_wait = self._calculate_burst_wait()
            if burst_wait > 0:
                logger.debug(f"Burst limit reached, waiting {burst_wait:.2f}s")
                await asyncio.sleep(burst_wait)
        
        # Check requests per minute limit
        if len(self.request_times) >= self.max_requests_per_minute:
            minute_wait = self._calculate_minute_wait(current_time)
            if minute_wait > 0:
                logger.debug(f"Rate limit reached, waiting {minute_wait:.2f}s")
                await asyncio.sleep(minute_wait)
        
        # Apply base delay with backoff
        delay = self._calculate_adaptive_delay()
        if delay > 0:
            await asyncio.sleep(delay)
    
    def _clean_old_requests(self, current_time: float) -> None:
        """Remove requests older than 1 minute from sliding window."""        minute_ago = current_time - 60
        while self.request_times and self.request_times[0] < minute_ago:
            self.request_times.popleft()
    
    def _calculate_burst_wait(self) -> float:
        """Calculate wait time for burst protection."""        if len(self.request_times) < self.burst_limit:
            return 0
        
        # Wait until oldest request in burst window expires
        oldest_request = self.request_times[-self.burst_limit]
        burst_window = 10  # 10 seconds burst window
        return max(0, oldest_request + burst_window - time.time())
    
    def _calculate_minute_wait(self, current_time: float) -> float:
        """Calculate wait time for minute-based rate limiting."""        if len(self.request_times) < self.max_requests_per_minute:
            return 0
        
        # Wait until oldest request expires from minute window
        oldest_request = self.request_times[0]
        return max(0, oldest_request + 60 - current_time)
    
    def _calculate_adaptive_delay(self) -> float:
        """Calculate adaptive delay based on recent rate limiting."""        base_delay = self.current_delay
        
        # Increase delay if we've been rate limited recently
        if self.consecutive_rate_limits > 0:
            backoff_multiplier = self.backoff_factor ** self.consecutive_rate_limits
            base_delay = min(self.max_backoff, base_delay * backoff_multiplier)
        
        return base_delay
    
    async def _check_distributed_rate_limit(self, identifier: str) -> None:
        """Check distributed rate limiting using Redis."""        try:
            key = f"rate_limit:{self.__class__.__name__}:{identifier}"
            current_time = time.time()
            
            # Get current count
            pipe = self.redis_client.pipeline()
            pipe.zremrangebyscore(key, 0, current_time - 60)  # Remove old entries
            pipe.zcard(key)  # Count current entries
            pipe.expire(key, 120)  # Set expiration
            
            results = pipe.execute()
            current_count = results[1]
            
            if current_count >= self.max_requests_per_minute:
                # Get oldest entry to calculate wait time
                oldest_entries = self.redis_client.zrange(key, 0, 0, withscores=True)
                if oldest_entries:
                    oldest_time = oldest_entries[0][1]
                    wait_time = max(0, oldest_time + 60 - current_time)
                    if wait_time > 0:
                        await asyncio.sleep(wait_time)
                        
        except Exception as e:
            logger.warning(f"Distributed rate limiting check failed: {e}")
    
    async def update_usage(self, identifier: str = "default", count: int = 1) -> None:
        """Update rate limit usage."""        current_time = time.time()
        
        # Add to local tracking
        for _ in range(count):
            self.request_times.append(current_time)
        
        self.last_request_time = current_time
        
        # Update distributed tracking
        if self.redis_client:
            await self._update_distributed_usage(identifier, count, current_time)
        
        # Reset consecutive rate limits on successful request
        self.consecutive_rate_limits = 0
        self.current_delay = self.base_delay
    
    async def _update_distributed_usage(self, identifier: str, count: int, timestamp: float) -> None:
        """Update distributed usage in Redis."""        try:
            key = f"rate_limit:{self.__class__.__name__}:{identifier}"
            
            pipe = self.redis_client.pipeline()
            for _ in range(count):
                pipe.zadd(key, {f"{timestamp}:{id(self)}": timestamp})
            pipe.expire(key, 120)
            pipe.execute()
            
        except Exception as e:
            logger.warning(f"Failed to update distributed usage: {e}")
    
    async def handle_rate_limit_response(self, retry_after: Optional[int] = None) -> None:
        """Handle rate limit response from API."""        self.consecutive_rate_limits += 1
        
        if retry_after:
            logger.info(f"Rate limited, waiting {retry_after} seconds")
            await asyncio.sleep(retry_after)
        else:
            # Use adaptive backoff
            backoff_delay = min(
                self.max_backoff,
                self.base_delay * (self.backoff_factor ** self.consecutive_rate_limits)
            )
            logger.info(f"Rate limited, adaptive backoff: {backoff_delay:.2f}s")
            await asyncio.sleep(backoff_delay)
        
        # Increase current delay for future requests
        self.current_delay = min(
            self.max_backoff,
            self.current_delay * self.backoff_factor
        )
    
    def get_rate_limit_info(self) -> RateLimitInfo:
        """Get current rate limit information."""        current_time = time.time()
        self._clean_old_requests(current_time)
        
        requests_made = len(self.request_times)
        requests_remaining = max(0, self.max_requests_per_minute - requests_made)
        
        # Calculate reset time (when oldest request expires)
        if self.request_times:
            reset_time = datetime.fromtimestamp(self.request_times[0] + 60)
        else:
            reset_time = datetime.now()
        
        return RateLimitInfo(
            requests_made=requests_made,
            requests_remaining=requests_remaining,
            reset_time=reset_time,
            retry_after=None,
            quota_used=self.daily_quota_used,
            quota_limit=self.daily_quota_limit or 0
        )

class YouTubeRateLimiter(RateLimiter):
    """YouTube-specific rate limiter."""    
    def __init__(self, redis_client: Optional[redis.Redis] = None):
        super().__init__(
            max_requests_per_minute=100,
            burst_limit=10,
            base_delay=0.6,
            backoff_factor=2.0,
            max_backoff=300.0,
            redis_client=redis_client
        )
        self.daily_quota_limit = 10000  # YouTube API quota

class InstagramRateLimiter(RateLimiter):
    """Instagram-specific rate limiter."""    
    def __init__(self, redis_client: Optional[redis.Redis] = None):
        super().__init__(
            max_requests_per_minute=60,
            burst_limit=5,
            base_delay=1.0,
            backoff_factor=1.5,
            max_backoff=600.0,
            redis_client=redis_client
        )

class TikTokRateLimiter(RateLimiter):
    """TikTok-specific rate limiter."""    
    def __init__(self, redis_client: Optional[redis.Redis] = None):
        super().__init__(
            max_requests_per_minute=30,
            burst_limit=3,
            base_delay=2.0,
            backoff_factor=2.0,
            max_backoff=900.0,
            redis_client=redis_client
        )

class TwitterRateLimiter(RateLimiter):
    """Twitter-specific rate limiter."""    
    def __init__(self, redis_client: Optional[redis.Redis] = None):
        super().__init__(
            max_requests_per_minute=180,
            burst_limit=15,
            base_delay=0.5,
            backoff_factor=1.5,
            max_backoff=900.0,
            redis_client=redis_client
        )

class FacebookRateLimiter(RateLimiter):
    """Facebook-specific rate limiter."""    
    def __init__(self, redis_client: Optional[redis.Redis] = None):
        super().__init__(
            max_requests_per_minute=200,
            burst_limit=20,
            base_delay=0.3,
            backoff_factor=1.5,
            max_backoff=300.0,
            redis_client=redis_client
        )

class SpotifyRateLimiter(RateLimiter):
    """Spotify-specific rate limiter."""    
    def __init__(self, redis_client: Optional[redis.Redis] = None):
        super().__init__(
            max_requests_per_minute=100,
            burst_limit=10,
            base_delay=0.6,
            backoff_factor=1.2,
            max_backoff=60.0,
            redis_client=redis_client
        )

class SubstackRateLimiter(RateLimiter):
    """Substack-specific rate limiter."""    
    def __init__(self, redis_client: Optional[redis.Redis] = None):
        super().__init__(
            max_requests_per_minute=30,  # Conservative for RSS and web scraping
            burst_limit=5,
            base_delay=2.0,  # Be respectful to Substack servers
            backoff_factor=1.5,
            max_backoff=300.0,
            redis_client=redis_client
        )

class GenericRateLimiter(RateLimiter):
    """Generic rate limiter for unknown platforms."""    
    def __init__(self, redis_client: Optional[redis.Redis] = None):
        super().__init__(
            max_requests_per_minute=60,
            burst_limit=5,
            base_delay=1.0,
            backoff_factor=1.5,
            max_backoff=300.0,
            redis_client=redis_client
        )

class AdaptiveRateLimiter(RateLimiter):
    """    Adaptive rate limiter that learns from response patterns.
    
    Features:
    - Machine learning-based adaptation
    - Response time analysis
    - Success rate monitoring
    - Dynamic parameter adjustment
    """    
    def __init__(self, redis_client: Optional[redis.Redis] = None):
        super().__init__(redis_client=redis_client)
        
        # Metrics tracking
        self.response_times = deque(maxlen=100)
        self.success_rate = 1.0
        self.recent_successes = deque(maxlen=20)
        
        # Adaptive parameters
        self.min_delay = 0.1
        self.target_success_rate = 0.95
        self.adaptation_factor = 0.1
    
    async def record_response(self, response_time: float, success: bool) -> None:
        """Record response metrics for adaptation."""        self.response_times.append(response_time)
        self.recent_successes.append(success)
        
        # Update success rate
        if len(self.recent_successes) > 0:
            self.success_rate = sum(self.recent_successes) / len(self.recent_successes)
        
        # Adapt delay based on success rate
        if self.success_rate < self.target_success_rate:
            # Increase delay if success rate is low
            self.current_delay *= (1 + self.adaptation_factor)
        elif self.success_rate > self.target_success_rate + 0.05:
            # Decrease delay if success rate is high
            self.current_delay *= (1 - self.adaptation_factor)
        
        # Ensure delay stays within bounds
        self.current_delay = max(self.min_delay, min(self.max_backoff, self.current_delay))
    
    def get_average_response_time(self) -> float:
        """Get average response time."""        if not self.response_times:
            return 0.0
        return sum(self.response_times) / len(self.response_times)
    
    def get_performance_metrics(self) -> Dict:
        """Get detailed performance metrics."""        return {
            'success_rate': self.success_rate,
            'average_response_time': self.get_average_response_time(),
            'current_delay': self.current_delay,
            'consecutive_rate_limits': self.consecutive_rate_limits,
            'total_requests': len(self.request_times),
            'adaptation_factor': self.adaptation_factor
        }
