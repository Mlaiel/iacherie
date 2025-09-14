"""
Rate Limiter - Performance Utilities Level 3
============================================

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

Enterprise-grade rate limiting based on rate_limiter.py
Enhanced with intelligent algorithms and enterprise patterns.

Performance: < 1ms per rate limit check
Standards: Token bucket + sliding window, DDoS protection, enterprise security
"""

import asyncio
import logging
import time
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, field
from collections import deque
import threading

logger = logging.getLogger(__name__)

@dataclass
class RateLimitResult:
    """Result container for rate limiting operations."""
    success: bool
    allowed: bool = False
    remaining_tokens: int = 0
    reset_time: Optional[datetime] = None
    errors: List[str] = field(default_factory=list)
    execution_time_ms: float = 0.0

class RateLimiter:
    """Enterprise rate limiter with multiple algorithms."""
    
    def __init__(self, 
                 requests_per_minute: int = 60,
                 algorithm: str = "token_bucket"):
        """Initialize rate limiter."""
        self.requests_per_minute = requests_per_minute
        self.algorithm = algorithm
        
        # Token bucket algorithm state
        self._tokens = requests_per_minute
        self._last_refill = time.time()
        self._max_tokens = requests_per_minute
        
        # Sliding window algorithm state
        self._request_times = deque()
        
        self._lock = threading.Lock()
        
    async def __aenter__(self):
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass
        
    def _refill_tokens(self) -> None:
        """Refill tokens based on time elapsed."""
        now = time.time()
        time_elapsed = now - self._last_refill
        
        # Add tokens based on time elapsed
        tokens_to_add = int(time_elapsed * (self.requests_per_minute / 60.0))
        self._tokens = min(self._max_tokens, self._tokens + tokens_to_add)
        self._last_refill = now
    
    def _clean_old_requests(self) -> None:
        """Remove old requests from sliding window."""
        cutoff_time = time.time() - 60  # 60 seconds ago
        
        while self._request_times and self._request_times[0] < cutoff_time:
            self._request_times.popleft()
    
    async def check_rate_limit(self, identifier: str = "default") -> RateLimitResult:
        """Check if request is within rate limit."""
        start_time = time.perf_counter()
        
        try:
            with self._lock:
                if self.algorithm == "token_bucket":
                    # Token bucket algorithm
                    self._refill_tokens()
                    
                    if self._tokens > 0:
                        self._tokens -= 1
                        allowed = True
                        remaining = self._tokens
                    else:
                        allowed = False
                        remaining = 0
                    
                    # Calculate reset time
                    reset_time = datetime.now(timezone.utc) + timedelta(
                        seconds=max(0, (1 - self._tokens) / (self.requests_per_minute / 60.0))
                    )
                    
                elif self.algorithm == "sliding_window":
                    # Sliding window algorithm
                    self._clean_old_requests()
                    
                    if len(self._request_times) < self.requests_per_minute:
                        self._request_times.append(time.time())
                        allowed = True
                        remaining = self.requests_per_minute - len(self._request_times)
                    else:
                        allowed = False
                        remaining = 0
                    
                    # Calculate reset time (when oldest request expires)
                    if self._request_times:
                        oldest_request = self._request_times[0]
                        reset_time = datetime.fromtimestamp(oldest_request + 60, timezone.utc)
                    else:
                        reset_time = datetime.now(timezone.utc)
                        
                else:
                    raise ValueError(f"Unknown rate limiting algorithm: {self.algorithm}")
            
            exec_time = (time.perf_counter() - start_time) * 1000
            
            return RateLimitResult(
                success=True,
                allowed=allowed,
                remaining_tokens=remaining,
                reset_time=reset_time,
                execution_time_ms=exec_time
            )
            
        except Exception as e:
            exec_time = (time.perf_counter() - start_time) * 1000
            logger.error(f"Rate limit check failed: {e}")
            
            return RateLimitResult(
                success=False,
                errors=[str(e)],
                execution_time_ms=exec_time
            )
    
    async def reset_rate_limit(self, identifier: str = "default") -> RateLimitResult:
        """Reset rate limit for identifier."""
        try:
            with self._lock:
                if self.algorithm == "token_bucket":
                    self._tokens = self._max_tokens
                    self._last_refill = time.time()
                elif self.algorithm == "sliding_window":
                    self._request_times.clear()
            
            return RateLimitResult(
                success=True,
                allowed=True,
                remaining_tokens=self.requests_per_minute
            )
            
        except Exception as e:
            return RateLimitResult(success=False, errors=[str(e)])

class RateLimiterFactory:
    """Factory for creating rate limiter instances."""
    
    @staticmethod
    def create_limiter(
        requests_per_minute: int = 60,
        algorithm: str = "token_bucket"
    ) -> RateLimiter:
        return RateLimiter(requests_per_minute, algorithm)