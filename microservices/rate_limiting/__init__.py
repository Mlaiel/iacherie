"""
Rate Limiting Module for Ainflue Microservices
Implements rate limiting and throttling for API protection.

Author: Fahed Mlaiel <mlaiel@live.de>
"""

import time
import threading
from typing import Dict, Optional, Any
from collections import defaultdict, deque
import logging

logger = logging.getLogger(__name__)

__all__ = ['RateLimiter', 'TokenBucket', 'SlidingWindowLimiter', 'RateLimitExceeded']

class RateLimitExceeded(Exception):
    """Exception raised when rate limit is exceeded"""
    def __init__(self, message -> None: str, retry_after -> None: Optional[float] = None) -> None:
        super().__init__(message)
        self.retry_after = retry_after

class TokenBucket:
    """Token bucket rate limiter implementation"""
    
    def __init__(self, capacity -> None: int, refill_rate -> None: float) -> None:
        self.capacity = capacity
        self.refill_rate = refill_rate  # tokens per second
        self.tokens = capacity
        self.last_refill = time.time()
        self._lock = threading.Lock()
        
    def consume(self, tokens: int = 1) -> bool:
        """Try to consume tokens from bucket"""
        with self._lock:
            self._refill()
            
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            return False
    
    def _refill(self) -> None:
        """Refill tokens based on time elapsed"""
        now = time.time()
        time_passed = now - self.last_refill
        tokens_to_add = time_passed * self.refill_rate
        
        self.tokens = min(self.capacity, self.tokens + tokens_to_add)
        self.last_refill = now

class SlidingWindowLimiter:
    """Sliding window rate limiter"""
    
    def __init__(self, max_requests -> None: int, window_size -> None: int) -> None:
        self.max_requests = max_requests
        self.window_size = window_size  # in seconds
        self.requests: Dict[str, deque] = defaultdict(deque)
        self._lock = threading.Lock()
        
    def is_allowed(self, identifier: str) -> bool:
        """Check if request is allowed for identifier"""
        with self._lock:
            now = time.time()
            window_start = now - self.window_size
            
            # Clean old requests
            while (self.requests[identifier] and 
                   self.requests[identifier][0] < window_start):
                self.requests[identifier].popleft()
            
            # Check if under limit
            if len(self.requests[identifier]) < self.max_requests:
                self.requests[identifier].append(now)
                return True
            
            return False
    
    def get_reset_time(self, identifier: str) -> Optional[float]:
        """Get time when rate limit resets for identifier"""
        with self._lock:
            if not self.requests[identifier]:
                return None
            
            oldest_request = self.requests[identifier][0]
            return oldest_request + self.window_size

class RateLimiter:
    """Main rate limiter class with multiple strategies"""
    
    def __init__(self, strategy -> None: str = "token_bucket", **kwargs) -> None:
        self.strategy = strategy
        
        if strategy == "token_bucket":
            capacity = kwargs.get("capacity", 100)
            refill_rate = kwargs.get("refill_rate", 10)
            self.limiter = TokenBucket(capacity, refill_rate)
        elif strategy == "sliding_window":
            max_requests = kwargs.get("max_requests", 100)
            window_size = kwargs.get("window_size", 60)
            self.limiter = SlidingWindowLimiter(max_requests, window_size)
        else:
            raise ValueError(f"Unknown rate limiting strategy: {strategy}")
    
    def check_rate_limit(self, identifier: str = "default") -> bool:
        """Check if request should be allowed"""
        if self.strategy == "token_bucket":
            return self.limiter.consume()
        elif self.strategy == "sliding_window":
            return self.limiter.is_allowed(identifier)
        
        return False
    
    def enforce_rate_limit(self, identifier -> None: str = "default") -> None:
        """Enforce rate limit, raise exception if exceeded"""
        if not self.check_rate_limit(identifier):
            retry_after = None
            
            if self.strategy == "sliding_window":
                retry_after = self.limiter.get_reset_time(identifier)
                if retry_after:
                    retry_after = retry_after - time.time()
            
            raise RateLimitExceeded(
                f"Rate limit exceeded for {identifier}",
                retry_after=retry_after
            )

def create_api_rate_limiter(requests_per_minute: int = 60) -> RateLimiter:
    """Create a standard API rate limiter"""
    return RateLimiter(
        strategy="sliding_window",
        max_requests=requests_per_minute,
        window_size=60
    )

def create_burst_limiter(burst_size: int = 100, sustained_rate: float = 10) -> RateLimiter:
    """Create a burst-capable rate limiter"""
    return RateLimiter(
        strategy="token_bucket",
        capacity=burst_size,
        refill_rate=sustained_rate
    )
