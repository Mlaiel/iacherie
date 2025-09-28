#!/usr/bin/env python3
"""
⚡ Rate Limiter Utilities - Protection Utils Module
=================================================

Rate limiting utilities for the protection system.

Author: Fahed Mlaiel (mlaiel@live.de)
Protection Utils Module
"""

import time
import asyncio
from typing import Dict, Optional, Any, Union
from datetime import datetime, timedelta
from collections import defaultdict, deque
import threading
from functools import wraps

class RateLimiter:
    """Basic rate limiter implementation"""
    
    def __init__(self, max_requests: int = 100, time_window: int = 3600):
        """Initialize rate limiter"""
        self.max_requests = max_requests
        self.time_window = time_window
        self._requests: defaultdict = defaultdict(deque)
        self._lock = threading.Lock()
    
    def is_allowed(self, identifier: str) -> bool:
        """Check if request is allowed"""
        with self._lock:
            current_time = time.time()
            request_times = self._requests[identifier]
            
            # Remove expired requests
            while request_times and current_time - request_times[0] > self.time_window:
                request_times.popleft()
            
            # Check if under limit
            if len(request_times) < self.max_requests:
                request_times.append(current_time)
                return True
            
            return False
    
    def time_until_allowed(self, identifier: str) -> float:
        """Get time until request is allowed"""
        with self._lock:
            current_time = time.time()
            request_times = self._requests[identifier]
            
            if not request_times or len(request_times) < self.max_requests:
                return 0.0
            
            oldest_request = request_times[0]
            return max(0.0, self.time_window - (current_time - oldest_request))
    
    def reset(self, identifier: str) -> None:
        """Reset rate limit for identifier"""
        with self._lock:
            if identifier in self._requests:
                self._requests[identifier].clear()
    
    def get_stats(self, identifier: str) -> Dict[str, Any]:
        """Get rate limit statistics"""
        with self._lock:
            current_time = time.time()
            request_times = self._requests[identifier]
            
            # Remove expired requests
            while request_times and current_time - request_times[0] > self.time_window:
                request_times.popleft()
            
            return {
                'requests_made': len(request_times),
                'requests_remaining': max(0, self.max_requests - len(request_times)),
                'max_requests': self.max_requests,
                'time_window': self.time_window,
                'reset_time': request_times[0] + self.time_window if request_times else current_time
            }

class AsyncRateLimiter(RateLimiter):
    """Async rate limiter implementation"""
    
    def __init__(self, max_requests: int = 100, time_window: int = 3600):
        super().__init__(max_requests, time_window)
        self._async_lock = asyncio.Lock()
    
    async def async_is_allowed(self, identifier: str) -> bool:
        """Async check if request is allowed"""
        await asyncio.sleep(0)  # Yield control
        return self.is_allowed(identifier)
    
    async def async_wait_if_needed(self, identifier: str) -> None:
        """Wait if rate limit is exceeded"""
        wait_time = self.time_until_allowed(identifier)
        if wait_time > 0:
            await asyncio.sleep(wait_time)

class SlidingWindowRateLimiter:
    """Sliding window rate limiter"""
    
    def __init__(self, max_requests: int = 100, time_window: int = 3600):
        self.max_requests = max_requests
        self.time_window = time_window
        self._windows: defaultdict = defaultdict(list)
        self._lock = threading.Lock()
    
    def is_allowed(self, identifier: str, weight: int = 1) -> bool:
        """Check if weighted request is allowed"""
        with self._lock:
            current_time = time.time()
            window = self._windows[identifier]
            
            # Clean old entries
            cutoff = current_time - self.time_window
            self._windows[identifier] = [entry for entry in window if entry[0] > cutoff]
            
            # Calculate current usage
            current_usage = sum(entry[1] for entry in self._windows[identifier])
            
            # Check if request can be allowed
            if current_usage + weight <= self.max_requests:
                self._windows[identifier].append((current_time, weight))
                return True
            
            return False

class TokenBucketRateLimiter:
    """Token bucket rate limiter"""
    
    def __init__(self, capacity: int = 100, refill_rate: float = 1.0):
        self.capacity = capacity
        self.refill_rate = refill_rate
        self._buckets: defaultdict = defaultdict(lambda: {'tokens': capacity, 'last_refill': time.time()})
        self._lock = threading.Lock()
    
    def is_allowed(self, identifier: str, tokens_needed: int = 1) -> bool:
        """Check if request is allowed with token consumption"""
        with self._lock:
            current_time = time.time()
            bucket = self._buckets[identifier]
            
            # Refill tokens
            time_passed = current_time - bucket['last_refill']
            tokens_to_add = time_passed * self.refill_rate
            bucket['tokens'] = min(self.capacity, bucket['tokens'] + tokens_to_add)
            bucket['last_refill'] = current_time
            
            # Check if enough tokens
            if bucket['tokens'] >= tokens_needed:
                bucket['tokens'] -= tokens_needed
                return True
            
            return False
    
    def get_tokens_available(self, identifier: str) -> float:
        """Get available tokens for identifier"""
        with self._lock:
            current_time = time.time()
            bucket = self._buckets[identifier]
            
            # Calculate current tokens
            time_passed = current_time - bucket['last_refill']
            tokens = min(self.capacity, bucket['tokens'] + time_passed * self.refill_rate)
            
            return tokens

class GlobalRateLimiter:
    """Global rate limiter for the entire system"""
    
    def __init__(self, 
                 api_requests_per_minute: int = 1000,
                 crawler_requests_per_minute: int = 600,
                 user_requests_per_minute: int = 60):
        """Initialize global rate limiter"""
        self.api_limiter = RateLimiter(api_requests_per_minute, 60)
        self.crawler_limiter = RateLimiter(crawler_requests_per_minute, 60)
        self.user_limiter = RateLimiter(user_requests_per_minute, 60)
        
        # Enterprise rate limiters
        self.enterprise_limiters = {
            'api': TokenBucketRateLimiter(capacity=api_requests_per_minute, refill_rate=api_requests_per_minute/60),
            'crawler': TokenBucketRateLimiter(capacity=crawler_requests_per_minute, refill_rate=crawler_requests_per_minute/60),
            'user': TokenBucketRateLimiter(capacity=user_requests_per_minute, refill_rate=user_requests_per_minute/60)
        }
    
    def check_api_rate_limit(self, identifier: str) -> bool:
        """Check API rate limit"""
        return self.api_limiter.is_allowed(identifier)
    
    def check_crawler_rate_limit(self, identifier: str) -> bool:
        """Check crawler rate limit"""
        return self.crawler_limiter.is_allowed(identifier)
    
    def check_user_rate_limit(self, identifier: str) -> bool:
        """Check user rate limit"""
        return self.user_limiter.is_allowed(identifier)
    
    def check_enterprise_rate_limit(self, limiter_type: str, identifier: str, tokens: int = 1) -> bool:
        """Check enterprise rate limit"""
        if limiter_type in self.enterprise_limiters:
            return self.enterprise_limiters[limiter_type].is_allowed(identifier, tokens)
        return False
    
    def get_global_stats(self) -> Dict[str, Any]:
        """Get global rate limiting statistics"""
        return {
            'api_limiter': {
                'max_requests': self.api_limiter.max_requests,
                'time_window': self.api_limiter.time_window
            },
            'crawler_limiter': {
                'max_requests': self.crawler_limiter.max_requests,
                'time_window': self.crawler_limiter.time_window
            },
            'user_limiter': {
                'max_requests': self.user_limiter.max_requests,
                'time_window': self.user_limiter.time_window
            },
            'enterprise_limiters': list(self.enterprise_limiters.keys())
        }

class DistributedRateLimiter:
    """Distributed rate limiter for multi-instance deployments"""
    
    def __init__(self, redis_client=None, fallback_limiter=None):
        self.redis_client = redis_client
        self.fallback_limiter = fallback_limiter or RateLimiter()
    
    def is_allowed(self, identifier: str, max_requests: int = 100, time_window: int = 3600) -> bool:
        """Check if request is allowed in distributed environment"""
        if self.redis_client:
            try:
                current_time = int(time.time())
                key = f"rate_limit:{identifier}:{current_time // time_window}"
                
                current_count = self.redis_client.incr(key)
                if current_count == 1:
                    self.redis_client.expire(key, time_window)
                
                return current_count <= max_requests
            except Exception:
                pass  # Fall back to local rate limiter
        
        return self.fallback_limiter.is_allowed(identifier)

# Decorator for rate limiting
def rate_limit(max_requests: int = 100, time_window: int = 3600, identifier_func=None):
    """Rate limiting decorator"""
    limiter = RateLimiter(max_requests, time_window)
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Determine identifier
            if identifier_func:
                identifier = identifier_func(*args, **kwargs)
            else:
                identifier = f"{func.__module__}.{func.__name__}"
            
            if not limiter.is_allowed(identifier):
                raise Exception(f"Rate limit exceeded for {identifier}")
            
            return func(*args, **kwargs)
        return wrapper
    return decorator

# Async decorator for rate limiting
def async_rate_limit(max_requests: int = 100, time_window: int = 3600, identifier_func=None):
    """Async rate limiting decorator"""
    limiter = AsyncRateLimiter(max_requests, time_window)
    
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Determine identifier
            if identifier_func:
                identifier = identifier_func(*args, **kwargs)
            else:
                identifier = f"{func.__module__}.{func.__name__}"
            
            if not await limiter.async_is_allowed(identifier):
                await limiter.async_wait_if_needed(identifier)
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

# Global rate limiter instance
global_rate_limiter = GlobalRateLimiter()

# Convenience functions
def check_rate_limit(identifier: str, limiter_type: str = 'api') -> bool:
    """Check rate limit using global limiter"""
    if limiter_type == 'api':
        return global_rate_limiter.check_api_rate_limit(identifier)
    elif limiter_type == 'crawler':
        return global_rate_limiter.check_crawler_rate_limit(identifier)
    elif limiter_type == 'user':
        return global_rate_limiter.check_user_rate_limit(identifier)
    return False

def get_rate_limit_stats() -> Dict[str, Any]:
    """Get global rate limit statistics"""
    return global_rate_limiter.get_global_stats()

# Aliases for backward compatibility
BasicRateLimiter = RateLimiter
WindowRateLimiter = SlidingWindowRateLimiter
BucketRateLimiter = TokenBucketRateLimiter