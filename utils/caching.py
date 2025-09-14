"""Caching Module

Simple caching utilities for workflow management.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
"""

from typing import Any, Optional
import time
from collections import defaultdict


class CacheManager:
    """Simple in-memory cache manager"""
    
    def __init__(self, default_ttl -> None: int = 3600) -> None:
        self.default_ttl = default_ttl
        self._cache = {}
        self._timestamps = {}
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if key not in self._cache:
            return None
        
        # Check if expired
        if time.time() - self._timestamps[key] > self.default_ttl:
            self.delete(key)
            return None
        
        return self._cache[key]
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache"""
        self._cache[key] = value
        self._timestamps[key] = time.time()
    
    def delete(self, key: str) -> None:
        """Delete value from cache"""
        if key in self._cache:
            del self._cache[key]
        if key in self._timestamps:
            del self._timestamps[key]
    
    def clear(self) -> None:
        """Clear all cache"""
        self._cache.clear()
        self._timestamps.clear()