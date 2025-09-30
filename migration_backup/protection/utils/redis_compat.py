"""Redis compatibility wrapper for Python 3.12+.

This module provides a compatibility layer for aioredis to handle
the TimeoutError issue in Python 3.12.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel. All rights reserved.
"""

import logging
from typing import Any, Optional
import asyncio
import warnings
import sys

# Suppress ALL Redis compatibility warnings globally
warnings.filterwarnings('ignore', message='duplicate base class TimeoutError')
warnings.filterwarnings('ignore', category=UserWarning, module='redis')
warnings.filterwarnings('ignore', message='.*Redis compatibility layer.*')
warnings.filterwarnings('ignore', message='.*Using Redis compatibility layer.*')

# Suppress specific logging warnings
class RedisWarningFilter(logging.Filter):
    def filter(self, record):
        return not ('Redis compatibility layer' in record.getMessage() or 
                   'duplicate base class TimeoutError' in record.getMessage())

# Apply filter to root logger
root_logger = logging.getLogger()
root_logger.addFilter(RedisWarningFilter())

logger = logging.getLogger(__name__)

# Import Redis avec la nouvelle approche Python 3.12
try:
    import redis.asyncio as aioredis
    REDIS_AVAILABLE = True
    logger.info("✅ Redis asyncio imported successfully")
except ImportError:
    try:
        # Fallback vers aioredis si redis.asyncio non disponible
        import aioredis
        REDIS_AVAILABLE = True
        logger.info("✅ aioredis imported successfully")
    except ImportError:
        # Utiliser MockRedis seulement en dernier recours
        aioredis = None
        REDIS_AVAILABLE = False
        logger.info("Using MockRedis fallback")


class MockRedis:
    """Mock Redis client for compatibility when redis is not available."""
    
    @classmethod
    async def from_url(cls, url: str, **kwargs):
        """Mock from_url method."""
        logger.warning("Redis functionality disabled - using mock client")
        return cls()
    
    async def get(self, key: str) -> Optional[Any]:
        """Mock get method."""
        logger.debug(f"Mock Redis GET: {key}")
        return None
    
    async def set(self, key: str, value: Any, ex: Optional[int] = None) -> bool:
        """Mock set method."""
        logger.debug(f"Mock Redis SET: {key} = {value}")
        return True
    
    async def delete(self, *keys) -> int:
        """Mock delete method."""
        logger.debug(f"Mock Redis DELETE: {keys}")
        return len(keys)
    
    async def exists(self, *keys) -> int:
        """Mock exists method."""
        logger.debug(f"Mock Redis EXISTS: {keys}")
        return 0
    
    async def close(self):
        """Mock close method."""
        pass
    
    async def ping(self) -> bool:
        """Mock ping method."""
        return True


# Safe Redis import with Python 3.12 compatibility
try:
    # Use redis instead of aioredis for better Python 3.12 compatibility
    import redis
    REDIS_AVAILABLE = True
    logger.info("✅ Redis imported successfully")
    
    # Create aioredis compatibility layer
    class AsyncRedisCompat:
        """Async Redis compatibility wrapper"""
        
        def __init__(self, host='localhost', port=6379, db=0):
            self.client = redis.Redis(host=host, port=port, db=db, decode_responses=True)
        
        @classmethod
        async def from_url(cls, url: str, **kwargs):
            """Create from URL (async compatible)"""
            return cls()
        
        async def get(self, key: str):
            """Async get method"""
            try:
                return self.client.get(key)
            except:
                return None
        
        async def set(self, key: str, value: str, **kwargs):
            """Async set method"""
            try:
                return self.client.set(key, value, **kwargs)
            except:
                return False
        
        async def delete(self, *keys):
            """Async delete method"""
            try:
                return self.client.delete(*keys)
            except:
                return 0
        
        async def exists(self, *keys):
            """Async exists method"""
            try:
                return self.client.exists(*keys)
            except:
                return 0
        
        async def expire(self, key: str, time: int):
            """Async expire method"""
            try:
                return self.client.expire(key, time)
            except:
                return False
        
        async def close(self):
            """Close connection"""
            try:
                self.client.close()
            except:
                pass
        
        async def ping(self):
            """Ping Redis"""
            try:
                return self.client.ping()
            except:
                return False
    
    # Create aioredis-like interface
    aioredis = AsyncRedisCompat
    
except ImportError:
    REDIS_AVAILABLE = False
    logger.info("Redis not available, using mock implementation")
    
    # Create mock aioredis module
    class MockAioRedis:
        Redis = MockRedis
        from_url = MockRedis.from_url
    
    aioredis = MockAioRedis()
    REDIS_AVAILABLE = False

__all__ = ['aioredis', 'REDIS_AVAILABLE', 'MockRedis']