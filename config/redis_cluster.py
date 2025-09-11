"""
Redis Cluster Configuration for Distributed Caching
High-performance distributed caching solution for Ainflue Platform

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, timedelta
import hashlib
import pickle
from dataclasses import dataclass, asdict
import aioredis
from aioredis.cluster import RedisCluster
import os

@dataclass
class CacheConfig:
    """Configuration for Redis cluster caching"""
    cluster_nodes: List[str]
    password: Optional[str] = None
    max_connections: int = 100
    retry_on_timeout: bool = True
    decode_responses: bool = True
    health_check_interval: int = 30
    default_ttl: int = 3600  # 1 hour
    max_memory_policy: str = "allkeys-lru"

class DistributedCache:
    """
    Enterprise-grade distributed caching using Redis Cluster
    Provides high-performance caching for API responses and computations
    """
    
    def __init__(self, config: CacheConfig):
        self.config = config
        self.cluster: Optional[RedisCluster] = None
        self.logger = self._setup_logger()
        self.connection_pool = None
        self.is_healthy = False
        
    def _setup_logger(self) -> logging.Logger:
        """Setup logging for cache operations"""
        logger = logging.getLogger("ainflue.cache")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    async def initialize(self) -> bool:
        """Initialize Redis cluster connection"""
        try:
            # Parse cluster nodes
            startup_nodes = []
            for node in self.config.cluster_nodes:
                if ':' in node:
                    host, port = node.split(':')
                    startup_nodes.append({"host": host, "port": int(port)})
                else:
                    startup_nodes.append({"host": node, "port": 6379})
            
            # Create cluster connection
            self.cluster = RedisCluster(
                startup_nodes=startup_nodes,
                password=self.config.password,
                max_connections_per_node=self.config.max_connections,
                retry_on_timeout=self.config.retry_on_timeout,
                decode_responses=self.config.decode_responses
            )
            
            # Test connection
            await self.cluster.ping()
            self.is_healthy = True
            
            self.logger.info(f"Redis cluster initialized with {len(startup_nodes)} nodes")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Redis cluster: {e}")
            self.is_healthy = False
            return False
    
    async def close(self):
        """Close Redis cluster connection"""
        if self.cluster:
            await self.cluster.close()
            self.logger.info("Redis cluster connection closed")
    
    def _generate_key(self, prefix: str, identifier: str, **kwargs) -> str:
        """Generate cache key with namespace and hash"""
        # Create a hash of the identifier and kwargs for consistent keys
        key_data = f"{identifier}:{json.dumps(kwargs, sort_keys=True)}"
        key_hash = hashlib.md5(key_data.encode()).hexdigest()[:12]
        return f"ainflue:{prefix}:{key_hash}"
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            if not self.cluster or not self.is_healthy:
                return None
            
            value = await self.cluster.get(key)
            if value is None:
                return None
            
            # Try to deserialize JSON first, then pickle as fallback
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                try:
                    return pickle.loads(value.encode('latin-1'))
                except:
                    return value
                    
        except Exception as e:
            self.logger.error(f"Cache get error for key {key}: {e}")
            return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache with TTL"""
        try:
            if not self.cluster or not self.is_healthy:
                return False
            
            ttl = ttl or self.config.default_ttl
            
            # Serialize value
            if isinstance(value, (dict, list)):
                serialized_value = json.dumps(value)
            elif isinstance(value, (str, int, float, bool)):
                serialized_value = json.dumps(value)
            else:
                # Use pickle for complex objects
                serialized_value = pickle.dumps(value).decode('latin-1')
            
            await self.cluster.setex(key, ttl, serialized_value)
            return True
            
        except Exception as e:
            self.logger.error(f"Cache set error for key {key}: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete key from cache"""
        try:
            if not self.cluster or not self.is_healthy:
                return False
            
            result = await self.cluster.delete(key)
            return result > 0
            
        except Exception as e:
            self.logger.error(f"Cache delete error for key {key}: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        try:
            if not self.cluster or not self.is_healthy:
                return False
            
            result = await self.cluster.exists(key)
            return result > 0
            
        except Exception as e:
            self.logger.error(f"Cache exists error for key {key}: {e}")
            return False
    
    async def get_or_set(self, key: str, factory_func, ttl: Optional[int] = None) -> Any:
        """Get value from cache or execute factory function and cache result"""
        # Try to get from cache first
        cached_value = await self.get(key)
        if cached_value is not None:
            return cached_value
        
        # Execute factory function
        try:
            if asyncio.iscoroutinefunction(factory_func):
                value = await factory_func()
            else:
                value = factory_func()
            
            # Cache the result
            await self.set(key, value, ttl)
            return value
            
        except Exception as e:
            self.logger.error(f"Factory function error for key {key}: {e}")
            return None
    
    async def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate all keys matching a pattern"""
        try:
            if not self.cluster or not self.is_healthy:
                return 0
            
            # Get all keys matching pattern
            keys = []
            async for key in self.cluster.scan_iter(match=pattern):
                keys.append(key)
            
            if keys:
                deleted = await self.cluster.delete(*keys)
                self.logger.info(f"Invalidated {deleted} keys matching pattern: {pattern}")
                return deleted
            
            return 0
            
        except Exception as e:
            self.logger.error(f"Pattern invalidation error for {pattern}: {e}")
            return 0
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        try:
            if not self.cluster or not self.is_healthy:
                return {"status": "disconnected"}
            
            info = await self.cluster.info()
            
            stats = {
                "status": "connected",
                "cluster_size": len(self.config.cluster_nodes),
                "memory_usage_mb": info.get("used_memory", 0) / (1024 * 1024),
                "total_connections": info.get("connected_clients", 0),
                "total_commands_processed": info.get("total_commands_processed", 0),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
                "uptime_seconds": info.get("uptime_in_seconds", 0)
            }
            
            # Calculate hit rate
            hits = stats["keyspace_hits"]
            misses = stats["keyspace_misses"]
            if hits + misses > 0:
                stats["hit_rate"] = hits / (hits + misses)
            else:
                stats["hit_rate"] = 0.0
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Error getting cache stats: {e}")
            return {"status": "error", "error": str(e)}

class CacheManager:
    """
    High-level cache manager for different cache namespaces
    Provides specialized caching for different components
    """
    
    def __init__(self, cache: DistributedCache):
        self.cache = cache
        self.logger = logging.getLogger("ainflue.cache_manager")
    
    # API Response Caching
    async def cache_api_response(self, endpoint: str, params: Dict, response: Any, ttl: int = 300):
        """Cache API response for 5 minutes by default"""
        key = self.cache._generate_key("api", endpoint, **params)
        return await self.cache.set(key, response, ttl)
    
    async def get_cached_api_response(self, endpoint: str, params: Dict) -> Optional[Any]:
        """Get cached API response"""
        key = self.cache._generate_key("api", endpoint, **params)
        return await self.cache.get(key)
    
    # Validation Results Caching
    async def cache_validation_result(self, content_hash: str, validation_type: str, result: Any, ttl: int = 1800):
        """Cache validation result for 30 minutes"""
        key = self.cache._generate_key("validation", f"{content_hash}_{validation_type}")
        return await self.cache.set(key, result, ttl)
    
    async def get_cached_validation_result(self, content_hash: str, validation_type: str) -> Optional[Any]:
        """Get cached validation result"""
        key = self.cache._generate_key("validation", f"{content_hash}_{validation_type}")
        return await self.cache.get(key)
    
    # AI Model Results Caching
    async def cache_ai_result(self, model_name: str, input_hash: str, result: Any, ttl: int = 3600):
        """Cache AI model result for 1 hour"""
        key = self.cache._generate_key("ai", f"{model_name}_{input_hash}")
        return await self.cache.set(key, result, ttl)
    
    async def get_cached_ai_result(self, model_name: str, input_hash: str) -> Optional[Any]:
        """Get cached AI model result"""
        key = self.cache._generate_key("ai", f"{model_name}_{input_hash}")
        return await self.cache.get(key)
    
    # User Session Caching
    async def cache_user_session(self, user_id: str, session_data: Dict, ttl: int = 7200):
        """Cache user session for 2 hours"""
        key = self.cache._generate_key("session", user_id)
        return await self.cache.set(key, session_data, ttl)
    
    async def get_user_session(self, user_id: str) -> Optional[Dict]:
        """Get user session data"""
        key = self.cache._generate_key("session", user_id)
        return await self.cache.get(key)
    
    async def invalidate_user_session(self, user_id: str) -> bool:
        """Invalidate user session"""
        key = self.cache._generate_key("session", user_id)
        return await self.cache.delete(key)
    
    # Content Metadata Caching
    async def cache_content_metadata(self, content_id: str, metadata: Dict, ttl: int = 86400):
        """Cache content metadata for 24 hours"""
        key = self.cache._generate_key("content", content_id)
        return await self.cache.set(key, metadata, ttl)
    
    async def get_content_metadata(self, content_id: str) -> Optional[Dict]:
        """Get cached content metadata"""
        key = self.cache._generate_key("content", content_id)
        return await self.cache.get(key)
    
    # Analytics Caching
    async def cache_analytics_data(self, query_hash: str, data: Any, ttl: int = 1800):
        """Cache analytics data for 30 minutes"""
        key = self.cache._generate_key("analytics", query_hash)
        return await self.cache.set(key, data, ttl)
    
    async def get_cached_analytics_data(self, query_hash: str) -> Optional[Any]:
        """Get cached analytics data"""
        key = self.cache._generate_key("analytics", query_hash)
        return await self.cache.get(key)
    
    # Bulk Operations
    async def invalidate_user_cache(self, user_id: str) -> int:
        """Invalidate all cache entries for a user"""
        pattern = f"ainflue:*:*{user_id}*"
        return await self.cache.invalidate_pattern(pattern)
    
    async def invalidate_content_cache(self, content_id: str) -> int:
        """Invalidate all cache entries for content"""
        pattern = f"ainflue:*:*{content_id}*"
        return await self.cache.invalidate_pattern(pattern)

# Factory function to create cache instance
def create_cache_instance() -> tuple[DistributedCache, CacheManager]:
    """Create cache instance from environment configuration"""
    
    # Get configuration from environment
    cluster_nodes = os.getenv("REDIS_CLUSTER_NODES", "localhost:6379").split(",")
    password = os.getenv("REDIS_PASSWORD")
    max_connections = int(os.getenv("REDIS_MAX_CONNECTIONS", "100"))
    
    config = CacheConfig(
        cluster_nodes=cluster_nodes,
        password=password,
        max_connections=max_connections,
        default_ttl=int(os.getenv("CACHE_DEFAULT_TTL", "3600"))
    )
    
    cache = DistributedCache(config)
    cache_manager = CacheManager(cache)
    
    return cache, cache_manager

# Global cache instances (to be initialized at startup)
cache_instance: Optional[DistributedCache] = None
cache_manager: Optional[CacheManager] = None

async def initialize_cache():
    """Initialize global cache instances"""
    global cache_instance, cache_manager
    
    cache_instance, cache_manager = create_cache_instance()
    success = await cache_instance.initialize()
    
    if success:
        logging.getLogger("ainflue.cache").info("Distributed cache initialized successfully")
    else:
        logging.getLogger("ainflue.cache").error("Failed to initialize distributed cache")
    
    return success

async def cleanup_cache():
    """Cleanup cache connections"""
    global cache_instance
    
    if cache_instance:
        await cache_instance.close()

# Cache decorators for easy use
def cache_result(ttl: int = 3600, namespace: str = "general"):
    """Decorator to cache function results"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            if cache_manager is None:
                # Cache not available, execute function directly
                if asyncio.iscoroutinefunction(func):
                    return await func(*args, **kwargs)
                else:
                    return func(*args, **kwargs)
            
            # Generate cache key from function name and arguments
            key_data = f"{func.__name__}:{str(args)}:{json.dumps(kwargs, sort_keys=True)}"
            key_hash = hashlib.md5(key_data.encode()).hexdigest()[:12]
            cache_key = f"ainflue:{namespace}:{key_hash}"
            
            # Try to get from cache
            cached_result = await cache_manager.cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)
            
            await cache_manager.cache.set(cache_key, result, ttl)
            return result
        
        return wrapper
    return decorator

if __name__ == "__main__":
    # Example usage and testing
    async def test_cache():
        cache, manager = create_cache_instance()
        
        # Initialize cache
        success = await cache.initialize()
        if not success:
            print("Failed to initialize cache - using local testing")
            return
        
        # Test basic operations
        await manager.cache_api_response("/test", {"param": "value"}, {"result": "test"})
        result = await manager.get_cached_api_response("/test", {"param": "value"})
        print(f"Cached API result: {result}")
        
        # Test AI result caching
        await manager.cache_ai_result("test_model", "input_hash", {"prediction": 0.95})
        ai_result = await manager.get_cached_ai_result("test_model", "input_hash")
        print(f"Cached AI result: {ai_result}")
        
        # Get stats
        stats = await cache.get_stats()
        print(f"Cache stats: {stats}")
        
        # Cleanup
        await cache.close()
    
    # Run test
    asyncio.run(test_cache())