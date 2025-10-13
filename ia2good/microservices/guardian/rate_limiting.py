"""
Guardian Rate Limiting System
Prevent spam and abuse
"""

from datetime import datetime, timedelta
from typing import Dict, Optional
from collections import defaultdict
import time

class RateLimitExceeded(Exception):
    """Rate limit exceeded exception"""
    pass

class RateLimiter:
    """Simple in-memory rate limiter"""
    
    def __init__(self):
        # Store: {identifier: [(timestamp, count), ...]}
        self.requests: Dict[str, list] = defaultdict(list)
        self.cleanup_interval = 60  # Cleanup every 60 seconds
        self.last_cleanup = time.time()
    
    def _cleanup_old_entries(self):
        """Remove old entries to prevent memory leak"""
        current_time = time.time()
        if current_time - self.last_cleanup > self.cleanup_interval:
            cutoff = current_time - 3600  # Remove entries older than 1 hour
            for identifier in list(self.requests.keys()):
                self.requests[identifier] = [
                    (ts, count) for ts, count in self.requests[identifier]
                    if ts > cutoff
                ]
                if not self.requests[identifier]:
                    del self.requests[identifier]
            self.last_cleanup = current_time
    
    def check_rate_limit(
        self,
        identifier: str,
        max_requests: int,
        window_seconds: int,
        increment: bool = True
    ) -> bool:
        """
        Check if request is within rate limit
        
        Args:
            identifier: Unique identifier (user_id, ip_address, etc.)
            max_requests: Maximum requests allowed
            window_seconds: Time window in seconds
            increment: Whether to increment the counter
        
        Returns:
            True if within limit, False otherwise
        """
        self._cleanup_old_entries()
        
        current_time = time.time()
        cutoff_time = current_time - window_seconds
        
        # Get requests within window
        recent_requests = [
            count for ts, count in self.requests[identifier]
            if ts > cutoff_time
        ]
        
        current_count = sum(recent_requests)
        
        if current_count >= max_requests:
            return False
        
        if increment:
            self.requests[identifier].append((current_time, 1))
        
        return True
    
    def get_remaining(self, identifier: str, max_requests: int, window_seconds: int) -> int:
        """Get remaining requests in current window"""
        current_time = time.time()
        cutoff_time = current_time - window_seconds
        
        recent_requests = [
            count for ts, count in self.requests[identifier]
            if ts > cutoff_time
        ]
        
        current_count = sum(recent_requests)
        return max(0, max_requests - current_count)
    
    def reset(self, identifier: str):
        """Reset rate limit for identifier"""
        if identifier in self.requests:
            del self.requests[identifier]

# Rate limit configurations
RATE_LIMITS = {
    # API endpoints
    "mission_create": {"max_requests": 10, "window": 3600},  # 10 missions per hour
    "volunteer_register": {"max_requests": 5, "window": 3600},  # 5 registrations per hour
    "file_upload": {"max_requests": 50, "window": 3600},  # 50 uploads per hour
    "chat_message": {"max_requests": 100, "window": 60},  # 100 messages per minute
    "stream_create": {"max_requests": 5, "window": 3600},  # 5 streams per hour
    "room_create": {"max_requests": 10, "window": 3600},  # 10 rooms per hour
    
    # General API
    "api_general": {"max_requests": 1000, "window": 3600},  # 1000 requests per hour
    
    # Websocket
    "websocket_connect": {"max_requests": 20, "window": 60},  # 20 connections per minute
    "websocket_message": {"max_requests": 100, "window": 10},  # 100 messages per 10 seconds
}

# Singleton instance
_rate_limiter_instance = None

def get_rate_limiter() -> RateLimiter:
    """Get or create rate limiter instance"""
    global _rate_limiter_instance
    if _rate_limiter_instance is None:
        _rate_limiter_instance = RateLimiter()
    return _rate_limiter_instance

def check_rate_limit(identifier: str, limit_type: str) -> bool:
    """
    Convenience function to check rate limit
    
    Args:
        identifier: User/IP identifier
        limit_type: Type of rate limit (from RATE_LIMITS dict)
    
    Returns:
        True if within limit
    
    Raises:
        RateLimitExceeded: If limit exceeded
    """
    limiter = get_rate_limiter()
    config = RATE_LIMITS.get(limit_type, RATE_LIMITS["api_general"])
    
    if not limiter.check_rate_limit(
        f"{limit_type}:{identifier}",
        config["max_requests"],
        config["window"]
    ):
        raise RateLimitExceeded(
            f"Rate limit exceeded for {limit_type}. "
            f"Max {config['max_requests']} requests per {config['window']} seconds."
        )
    
    return True
