"""
Advanced Cache Management System
High-performance caching with Redis, intelligent invalidation, and distributed locking.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import json
import pickle
import hashlib
from datetime import datetime, timedelta
from typing import Any, Optional, Dict, List, Union, Callable
import asyncio
from functools import wraps

from ..config import settings


class CacheKeyGenerator:
    """Intelligent cache key generation and management"""
    
    @staticmethod
    def generate_key(prefix: str, *args, **kwargs) -> str:
        """Generate consistent cache key from parameters"""
        # Create deterministic hash from all parameters
        key_data = f"{prefix}:{':'.join(map(str, args))}:{':'.join(f'{k}={v}' for k, v in sorted(kwargs.items()))}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    @staticmethod
    def user_key(user_id: str, key_type: str, *args) -> str:
        """Generate user-specific cache key"""
        return CacheKeyGenerator.generate_key(f"user:{user_id}:{key_type}", *args)
    
    @staticmethod
    def content_key(content_id: str, key_type: str, *args) -> str:
        """Generate content-specific cache key"""
        return CacheKeyGenerator.generate_key(f"content:{content_id}:{key_type}", *args)
    
    @staticmethod
    def platform_key(platform: str, key_type: str, *args) -> str:
        """Generate platform-specific cache key"""
        return CacheKeyGenerator.generate_key(f"platform:{platform}:{key_type}", *args)


class CacheSerializer:
    """Advanced serialization for complex objects"""
    
    @staticmethod
    def serialize(data: Any) -> bytes:
        """Serialize data for caching"""
        if isinstance(data, (dict, list, tuple)):
            return json.dumps(data, default=str).encode()
        elif isinstance(data, (str, int, float, bool)):
            return json.dumps(data).encode()
        else:
            return pickle.dumps(data)
    
    @staticmethod
    def deserialize(data: bytes) -> Any:
        """Deserialize cached data"""
        try:
            # Try JSON first (faster)
            return json.loads(data.decode())
        except (json.JSONDecodeError, UnicodeDecodeError):
            # Fallback to pickle
            return pickle.loads(data)


class DistributedLock:
    """Distributed locking mechanism using Redis"""
    
    def __init__(self, redis_client, lock_key: str, timeout: int = 10):
        self.redis_client = redis_client
        self.lock_key = f"lock:{lock_key}"
        self.timeout = timeout
        self.acquired = False
    
    async def __aenter__(self):
        """Acquire distributed lock"""
        start_time = datetime.utcnow()
        
        while (datetime.utcnow() - start_time).seconds < self.timeout:
            # Try to acquire lock
            acquired = await self.redis_client.set(
                self.lock_key, 
                "locked", 
                ex=self.timeout, 
                nx=True
            )
            
            if acquired:
                self.acquired = True
                return self
            
            # Wait before retry
            await asyncio.sleep(0.1)
        
        raise TimeoutError(f"Could not acquire lock '{self.lock_key}' within {self.timeout} seconds")
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Release distributed lock"""
        if self.acquired:
            await self.redis_client.delete(self.lock_key)
            self.acquired = False


class CacheManager:
    """
    Advanced cache management with intelligent strategies and performance optimization.
    Supports multiple cache types, automatic invalidation, and distributed operations.
    """
    
    def __init__(self):
        self.redis_client = None
        self.local_cache = {}
        self.cache_stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "deletes": 0
        }
        self.invalidation_patterns = {}
    
    async def initialize(self, redis_client):
        """Initialize cache manager with Redis client"""
        self.redis_client = redis_client
    
    async def get(self, key: str, default: Any = None) -> Any:
        """Get value from cache with fallback hierarchy"""
        try:
            # Try Redis first
            if self.redis_client:
                cached_data = await self.redis_client.get(key)
                if cached_data:
                    self.cache_stats["hits"] += 1
                    return CacheSerializer.deserialize(cached_data.encode() if isinstance(cached_data, str) else cached_data)
            
            # Try local cache
            if key in self.local_cache:
                cache_entry = self.local_cache[key]
                if cache_entry["expires_at"] > datetime.utcnow():
                    self.cache_stats["hits"] += 1
                    return cache_entry["data"]
                else:
                    del self.local_cache[key]
            
            self.cache_stats["misses"] += 1
            return default
            
        except Exception:
            self.cache_stats["misses"] += 1
            return default
    
    async def set(self, key: str, value: Any, ttl: int = 3600, cache_type: str = "redis") -> bool:
        """Set value in cache with TTL"""
        try:
            serialized_data = CacheSerializer.serialize(value)
            
            # Set in Redis
            if cache_type in ["redis", "both"] and self.redis_client:
                await self.redis_client.setex(key, ttl, serialized_data)
            
            # Set in local cache
            if cache_type in ["local", "both"]:
                self.local_cache[key] = {
                    "data": value,
                    "expires_at": datetime.utcnow() + timedelta(seconds=ttl)
                }
            
            self.cache_stats["sets"] += 1
            return True
            
        except Exception:
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete key from all cache layers"""
        try:
            deleted = False
            
            # Delete from Redis
            if self.redis_client:
                redis_deleted = await self.redis_client.delete(key)
                deleted = deleted or bool(redis_deleted)
            
            # Delete from local cache
            if key in self.local_cache:
                del self.local_cache[key]
                deleted = True
            
            if deleted:
                self.cache_stats["deletes"] += 1
            
            return deleted
            
        except Exception:
            return False
    
    async def delete_pattern(self, pattern: str) -> int:
        """Delete all keys matching pattern"""
        try:
            deleted_count = 0
            
            # Delete from Redis
            if self.redis_client:
                keys = await self.redis_client.keys(pattern)
                if keys:
                    deleted_count += await self.redis_client.delete(*keys)
            
            # Delete from local cache
            keys_to_delete = [key for key in self.local_cache.keys() if self._match_pattern(key, pattern)]
            for key in keys_to_delete:
                del self.local_cache[key]
                deleted_count += 1
            
            self.cache_stats["deletes"] += deleted_count
            return deleted_count
            
        except Exception:
            return 0
    
    def _match_pattern(self, key: str, pattern: str) -> bool:
        """Simple pattern matching for cache keys"""
        return pattern.replace("*", "") in key
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        try:
            # Check Redis
            if self.redis_client:
                exists = await self.redis_client.exists(key)
                if exists:
                    return True
            
            # Check local cache
            if key in self.local_cache:
                cache_entry = self.local_cache[key]
                if cache_entry["expires_at"] > datetime.utcnow():
                    return True
                else:
                    del self.local_cache[key]
            
            return False
            
        except Exception:
            return False
    
    async def increment(self, key: str, amount: int = 1, ttl: int = 3600) -> int:
        """Increment numeric value in cache"""
        try:
            if self.redis_client:
                result = await self.redis_client.incrby(key, amount)
                await self.redis_client.expire(key, ttl)
                return result
            else:
                current = await self.get(key, 0)
                new_value = int(current) + amount
                await self.set(key, new_value, ttl, "local")
                return new_value
                
        except Exception:
            return 0
    
    async def get_or_set(self, key: str, factory: Callable, ttl: int = 3600, 
                        cache_type: str = "redis") -> Any:
        """Get value from cache or compute and store it"""
        # Try to get from cache first
        cached_value = await self.get(key)
        if cached_value is not None:
            return cached_value
        
        # Compute value using factory function
        if asyncio.iscoroutinefunction(factory):
            computed_value = await factory()
        else:
            computed_value = factory()
        
        # Store in cache
        await self.set(key, computed_value, ttl, cache_type)
        return computed_value
    
    async def get_multi(self, keys: List[str]) -> Dict[str, Any]:
        """Get multiple values from cache"""
        results = {}
        
        try:
            # Get from Redis using pipeline
            if self.redis_client and keys:
                redis_results = await self.redis_client.mget(keys)
                for i, key in enumerate(keys):
                    if redis_results[i]:
                        results[key] = CacheSerializer.deserialize(
                            redis_results[i].encode() if isinstance(redis_results[i], str) else redis_results[i]
                        )
                        self.cache_stats["hits"] += 1
                    else:
                        self.cache_stats["misses"] += 1
            
            # Get remaining from local cache
            for key in keys:
                if key not in results and key in self.local_cache:
                    cache_entry = self.local_cache[key]
                    if cache_entry["expires_at"] > datetime.utcnow():
                        results[key] = cache_entry["data"]
                        self.cache_stats["hits"] += 1
                    else:
                        del self.local_cache[key]
                        self.cache_stats["misses"] += 1
            
            return results
            
        except Exception:
            return {}
    
    async def set_multi(self, mapping: Dict[str, Any], ttl: int = 3600, 
                       cache_type: str = "redis") -> bool:
        """Set multiple values in cache"""
        try:
            # Set in Redis using pipeline
            if cache_type in ["redis", "both"] and self.redis_client:
                pipe = self.redis_client.pipeline()
                for key, value in mapping.items():
                    serialized_data = CacheSerializer.serialize(value)
                    pipe.setex(key, ttl, serialized_data)
                await pipe.execute()
            
            # Set in local cache
            if cache_type in ["local", "both"]:
                expires_at = datetime.utcnow() + timedelta(seconds=ttl)
                for key, value in mapping.items():
                    self.local_cache[key] = {
                        "data": value,
                        "expires_at": expires_at
                    }
            
            self.cache_stats["sets"] += len(mapping)
            return True
            
        except Exception:
            return False
    
    def register_invalidation_pattern(self, event_type: str, patterns: List[str]):
        """Register cache invalidation patterns for events"""
        self.invalidation_patterns[event_type] = patterns
    
    async def invalidate_by_event(self, event_type: str, **kwargs):
        """Invalidate cache based on event type and parameters"""
        if event_type not in self.invalidation_patterns:
            return
        
        for pattern_template in self.invalidation_patterns[event_type]:
            pattern = pattern_template.format(**kwargs)
            await self.delete_pattern(pattern)
    
    async def get_distributed_lock(self, lock_key: str, timeout: int = 10) -> DistributedLock:
        """Get distributed lock for cache operations"""
        return DistributedLock(self.redis_client, lock_key, timeout)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache performance statistics"""
        total_requests = self.cache_stats["hits"] + self.cache_stats["misses"]
        hit_rate = (self.cache_stats["hits"] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            **self.cache_stats,
            "hit_rate": f"{hit_rate:.2f}%",
            "total_requests": total_requests,
            "local_cache_size": len(self.local_cache)
        }
    
    async def clear_all(self) -> bool:
        """Clear all cache layers"""
        try:
            # Clear Redis
            if self.redis_client:
                await self.redis_client.flushdb()
            
            # Clear local cache
            self.local_cache.clear()
            
            return True
            
        except Exception:
            return False
    
    def cache_function(self, ttl: int = 3600, key_prefix: str = "func", 
                      cache_type: str = "redis"):
        """Decorator to cache function results"""
        def decorator(func: Callable):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # Generate cache key from function name and arguments
                cache_key = CacheKeyGenerator.generate_key(
                    f"{key_prefix}:{func.__name__}", *args, **kwargs
                )
                
                # Try to get from cache
                cached_result = await self.get(cache_key)
                if cached_result is not None:
                    return cached_result
                
                # Execute function
                if asyncio.iscoroutinefunction(func):
                    result = await func(*args, **kwargs)
                else:
                    result = func(*args, **kwargs)
                
                # Cache result
                await self.set(cache_key, result, ttl, cache_type)
                return result
            
            return wrapper
        return decorator


# Global cache manager instance
cache_manager = CacheManager()