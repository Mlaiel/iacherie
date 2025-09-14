"""
Rate Limiter Utility - DevOps Expert Implementation
==================================================

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

Enterprise rate limiting implementation.
"""

import time
import logging
from typing import Dict, List
from collections import defaultdict

logger = logging.getLogger(__name__)


class RateLimiter:
    """Enterprise rate limiter implementation"""
    
    def __init__(self, max_requests -> None: int = 100, window_size -> None: int = 60) -> None:
        self.max_requests = max_requests
        self.window_size = window_size
        self.requests: Dict[str, List[float]] = defaultdict(list)
    
    def is_allowed(self, identifier: str) -> bool:
        """Check if request is allowed"""
        now = time.time()
        window_start = now - self.window_size
        
        # Clean old requests
        self.requests[identifier] = [
            req_time for req_time in self.requests[identifier]
            if req_time > window_start
        ]
        
        # Check if under limit
        if len(self.requests[identifier]) < self.max_requests:
            self.requests[identifier].append(now)
            return True
        
        return False
    
    def get_remaining_requests(self, identifier: str) -> int:
        """Get remaining requests for identifier"""
        current_count = len(self.requests.get(identifier, []))
        return max(0, self.max_requests - current_count)