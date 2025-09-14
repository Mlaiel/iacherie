"""
Rate Limiting Service Index
Enterprise Rate Limiting and Throttling

This module provides advanced rate limiting capabilities to protect
services from overload and ensure fair resource allocation.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class RateLimitingService:
    """Enterprise rate limiting service"""
    
    def __init__(self):
        self.limits: Dict[str, Dict[str, Any]] = {}
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    async def set_rate_limit(self, identifier: str, requests_per_second: int, burst_size: Optional[int] = None) -> bool:
        """Set rate limit for an identifier"""
        try:
            self.limits[identifier] = {
                'requests_per_second': requests_per_second,
                'burst_size': burst_size or requests_per_second,
                'tokens': requests_per_second,
                'last_refill': datetime.now()
            }
            self.logger.info(f"Rate limit set for {identifier}: {requests_per_second} req/s")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to set rate limit for {identifier}: {str(e)}")
            return False
    
    async def check_rate_limit(self, identifier: str) -> bool:
        """Check if request is within rate limit"""
        try:
            if identifier not in self.limits:
                return True  # No limit set, allow request
            
            limit_info = self.limits[identifier]
            now = datetime.now()
            
            # Refill tokens based on time elapsed
            time_elapsed = (now - limit_info['last_refill']).total_seconds()
            tokens_to_add = time_elapsed * limit_info['requests_per_second']
            limit_info['tokens'] = min(
                limit_info['burst_size'],
                limit_info['tokens'] + tokens_to_add
            )
            limit_info['last_refill'] = now
            
            # Check if request can be served
            if limit_info['tokens'] >= 1:
                limit_info['tokens'] -= 1
                return True
            else:
                self.logger.warning(f"Rate limit exceeded for {identifier}")
                return False
                
        except Exception as e:
            self.logger.error(f"Rate limit check failed for {identifier}: {str(e)}")
            return True  # Fail open

# Global rate limiting service
rate_limiting_service = RateLimitingService()

__all__ = ['RateLimitingService', 'rate_limiting_service']