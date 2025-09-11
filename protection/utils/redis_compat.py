"""Redis compatibility wrapper for Python 3.12+.

This module provides a compatibility layer for aioredis to handle
the TimeoutError issue in Python 3.12.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel. All rights reserved.
"""

import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)

# Try to import aioredis with compatibility handling
try:
    import aioredis
    REDIS_AVAILABLE = True
    logger.info("aioredis imported successfully")
except (ImportError, TypeError) as e:
    if "duplicate base class TimeoutError" in str(e):
        logger.warning("aioredis has Python 3.12 compatibility issues - using fallback")
    else:
        logger.warning(f"aioredis not available: {e}")
    
    # Create a mock aioredis module for compatibility
    class MockRedis:
        """Mock Redis client for compatibility when aioredis is not available."""
        
        @classmethod
        async def from_url(cls, url: str, **kwargs):
            """Mock from_url method."""
            logger.warning("Redis functionality disabled - using mock client")
            return cls()
        
        async def get(self, key: str) -> Optional[Any]:
            """Mock get method."""
            return None
        
        async def set(self, key: str, value: Any, **kwargs) -> bool:
            """Mock set method."""
            return True
        
        async def delete(self, *keys: str) -> int:
            """Mock delete method.""" 
            return 0
        
        async def exists(self, *keys: str) -> int:
            """Mock exists method."""
            return 0
        
        async def expire(self, key: str, time: int) -> bool:
            """Mock expire method."""
            return True
        
        async def close(self):
            """Mock close method."""
            pass
        
        async def ping(self) -> bool:
            """Mock ping method."""
            return True
    
    # Create mock aioredis module
    class MockAioRedis:
        Redis = MockRedis
        from_url = MockRedis.from_url
    
    aioredis = MockAioRedis()
    REDIS_AVAILABLE = False

__all__ = ['aioredis', 'REDIS_AVAILABLE']