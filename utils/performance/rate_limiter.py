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
from collections import deque, defaultdict
import threading
import functools

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

# === ENHANCED ENTERPRISE RATE LIMITING ===
# Additional functionality from standalone rate_limiter.py

class MultiTierRateLimiter:
    """Enhanced multi-tier rate limiter for enterprise DDoS protection
    
    DevOps Expert: Advanced rate limiting with multiple algorithms and tiers
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Multi-tier limits
        self.tier_limits = {
            'global': self.config.get('global_limit', 10000),  # requests per minute globally
            'ip': self.config.get('ip_limit', 1000),           # requests per minute per IP
            'user': self.config.get('user_limit', 100),        # requests per minute per user
            'endpoint': self.config.get('endpoint_limit', 500) # requests per minute per endpoint
        }
        
        # Request tracking per tier
        self.request_trackers = {
            tier: defaultdict(list) for tier in self.tier_limits.keys()
        }
        
        # Window size (in seconds)
        self.window_size = self.config.get('window_size', 60)
        
        # Thread safety
        self._lock = threading.Lock()
        
        # Whitelist and blacklist
        self.whitelisted_ips = set(self.config.get('whitelist', []))
        self.blacklisted_ips = set(self.config.get('blacklist', []))
    
    async def check_rate_limit(
        self,
        identifier: str,
        tier: str = 'global',
        ip_address: Optional[str] = None,
        user_id: Optional[str] = None,
        endpoint: Optional[str] = None
    ) -> RateLimitResult:
        """Check rate limits across multiple tiers"""
        
        start_time = time.time()
        
        try:
            # Check blacklist
            if ip_address and ip_address in self.blacklisted_ips:
                return RateLimitResult(
                    success=True,
                    allowed=False,
                    remaining_tokens=0,
                    execution_time_ms=(time.time() - start_time) * 1000
                )
            
            # Check whitelist (bypass rate limits)
            if ip_address and ip_address in self.whitelisted_ips:
                return RateLimitResult(
                    success=True,
                    allowed=True,
                    remaining_tokens=999999,
                    execution_time_ms=(time.time() - start_time) * 1000
                )
            
            # Check all applicable tiers
            checks = [
                ('global', 'global'),
                ('ip', ip_address or identifier),
                ('user', user_id or identifier),
                ('endpoint', endpoint or identifier)
            ]
            
            with self._lock:
                current_time = time.time()
                window_start = current_time - self.window_size
                
                for tier_name, tier_identifier in checks:
                    if tier_name not in self.tier_limits or not tier_identifier:
                        continue
                    
                    # Clean old requests
                    requests = self.request_trackers[tier_name][tier_identifier]
                    self.request_trackers[tier_name][tier_identifier] = [
                        req_time for req_time in requests if req_time > window_start
                    ]
                    
                    # Check limit
                    current_count = len(self.request_trackers[tier_name][tier_identifier])
                    limit = self.tier_limits[tier_name]
                    
                    if current_count >= limit:
                        # Rate limit exceeded
                        reset_time = datetime.fromtimestamp(
                            max(self.request_trackers[tier_name][tier_identifier]) + self.window_size,
                            tz=timezone.utc
                        )
                        
                        return RateLimitResult(
                            success=True,
                            allowed=False,
                            remaining_tokens=0,
                            reset_time=reset_time,
                            execution_time_ms=(time.time() - start_time) * 1000
                        )
                
                # All checks passed - record the request
                for tier_name, tier_identifier in checks:
                    if tier_name in self.tier_limits and tier_identifier:
                        self.request_trackers[tier_name][tier_identifier].append(current_time)
                
                # Calculate remaining tokens (minimum across all tiers)
                remaining_tokens = min(
                    self.tier_limits[tier_name] - len(self.request_trackers[tier_name][tier_identifier])
                    for tier_name, tier_identifier in checks
                    if tier_name in self.tier_limits and tier_identifier
                )
                
                return RateLimitResult(
                    success=True,
                    allowed=True,
                    remaining_tokens=max(0, remaining_tokens),
                    execution_time_ms=(time.time() - start_time) * 1000
                )
        
        except Exception as e:
            self.logger.error(f"Rate limit check failed: {e}")
            return RateLimitResult(
                success=False,
                errors=[str(e)],
                execution_time_ms=(time.time() - start_time) * 1000
            )
    
    async def add_to_blacklist(self, ip_address: str):
        """Add IP to blacklist"""
        self.blacklisted_ips.add(ip_address)
        self.logger.warning(f"Added {ip_address} to blacklist")
    
    async def remove_from_blacklist(self, ip_address: str):
        """Remove IP from blacklist"""
        self.blacklisted_ips.discard(ip_address)
        self.logger.info(f"Removed {ip_address} from blacklist")
    
    async def add_to_whitelist(self, ip_address: str):
        """Add IP to whitelist"""
        self.whitelisted_ips.add(ip_address)
        self.logger.info(f"Added {ip_address} to whitelist")
    
    async def remove_from_whitelist(self, ip_address: str):
        """Remove IP from whitelist"""
        self.whitelisted_ips.discard(ip_address)
        self.logger.info(f"Removed {ip_address} from whitelist")
    
    async def get_rate_limit_stats(self) -> Dict[str, Any]:
        """Get comprehensive rate limiting statistics"""
        with self._lock:
            stats = {
                'tier_limits': self.tier_limits,
                'current_usage': {},
                'whitelist_count': len(self.whitelisted_ips),
                'blacklist_count': len(self.blacklisted_ips),
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
            # Calculate current usage for each tier
            current_time = time.time()
            window_start = current_time - self.window_size
            
            for tier_name, tracker in self.request_trackers.items():
                tier_usage = {}
                for identifier, requests in tracker.items():
                    active_requests = [req for req in requests if req > window_start]
                    if active_requests:
                        tier_usage[identifier] = {
                            'count': len(active_requests),
                            'limit': self.tier_limits[tier_name],
                            'utilization_percent': (len(active_requests) / self.tier_limits[tier_name]) * 100
                        }
                
                stats['current_usage'][tier_name] = tier_usage
            
            return stats
    
    async def reset_limits(self, tier: Optional[str] = None, identifier: Optional[str] = None):
        """Reset rate limits for specific tier/identifier or all"""
        with self._lock:
            if tier and identifier:
                # Reset specific identifier in tier
                if tier in self.request_trackers:
                    self.request_trackers[tier][identifier] = []
                    self.logger.info(f"Reset rate limits for {tier}:{identifier}")
            elif tier:
                # Reset entire tier
                if tier in self.request_trackers:
                    self.request_trackers[tier].clear()
                    self.logger.info(f"Reset all rate limits for tier {tier}")
            else:
                # Reset all
                for tracker in self.request_trackers.values():
                    tracker.clear()
                self.logger.info("Reset all rate limits")

# Rate limiting decorator
def rate_limit(
    rate_limiter: MultiTierRateLimiter,
    tier: str = 'global',
    extract_ip: bool = True,
    extract_user: bool = True
):
    """Decorator for automatic rate limiting"""
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract context for rate limiting
            # This is a simplified example - in practice you'd extract from request context
            identifier = 'default'
            ip_address = None
            user_id = None
            endpoint = func.__name__
            
            # Check rate limit
            result = await rate_limiter.check_rate_limit(
                identifier=identifier,
                tier=tier,
                ip_address=ip_address,
                user_id=user_id,
                endpoint=endpoint
            )
            
            if not result.allowed:
                raise Exception(f"Rate limit exceeded. Reset at: {result.reset_time}")
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

# Export enhanced rate limiting utilities
__all__ = ['RateLimiter', 'RateLimiterFactory', 'RateLimitResult', 
           'MultiTierRateLimiter', 'rate_limit']