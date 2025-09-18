"""GraphQL Caching Template for Ainflue Platform
Enterprise-grade GraphQL caching with Redis and in-memory optimization

⚠️  AVERTISSEMENT LÉGAL:
==========================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques

Author: Fahed Mlaiel (mlaiel@live.de)
Created: 2025-01-18
"""

import logging
import hashlib
import json
import asyncio
from typing import Dict, Any, Optional, List, Union, Callable, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import pickle
import zlib

import redis.asyncio as aioredis
from graphql import GraphQLResolveInfo, GraphQLError
from graphql.execution.middleware import Middleware

from core.config import get_settings
from core.auth import get_current_user
from core.logging import log_cache_operation
from utils.exceptions import CacheException
from monitoring.api_metrics import CacheMetrics

logger = logging.getLogger(__name__)
settings = get_settings()


class CacheStrategy(Enum):
    """Cache strategy types"""
    NO_CACHE = "no_cache"
    MEMORY_ONLY = "memory_only" 
    REDIS_ONLY = "redis_only"
    MULTI_TIER = "multi_tier"
    WRITE_THROUGH = "write_through"
    WRITE_BEHIND = "write_behind"


class CacheScope(Enum):
    """Cache scope levels"""
    GLOBAL = "global"  # Same for all users
    USER = "user"      # Per user
    TENANT = "tenant"  # Per tenant/organization
    SESSION = "session" # Per session


@dataclass
class CacheConfig:
    """Cache configuration for GraphQL operations"""
    ttl: int = 300  # Time to live in seconds
    strategy: CacheStrategy = CacheStrategy.MULTI_TIER
    scope: CacheScope = CacheScope.GLOBAL
    compress: bool = True
    serialize_method: str = "json"  # json, pickle, msgpack
    invalidation_tags: List[str] = field(default_factory=list)
    cache_key_prefix: str = "graphql"
    max_size: Optional[int] = None  # Max cache entry size in bytes
    
    def get_cache_key(self, base_key: str, user_id: Optional[str] = None, tenant_id: Optional[str] = None) -> str:
        """Generate cache key based on scope"""
        key_parts = [self.cache_key_prefix, base_key]
        
        if self.scope == CacheScope.USER and user_id:
            key_parts.append(f"user:{user_id}")
        elif self.scope == CacheScope.TENANT and tenant_id:
            key_parts.append(f"tenant:{tenant_id}")
        elif self.scope == CacheScope.SESSION:
            # Would include session ID
            pass
        
        return ":".join(key_parts)


class GraphQLQueryNormalizer:
    """Normalizes GraphQL queries for consistent caching"""
    
    def __init__(self):
        self.field_order_cache = {}
    
    def normalize_query(self, query: str, variables: Optional[Dict[str, Any]] = None) -> str:
        """Normalize query for consistent cache keys"""
        # Remove whitespace and normalize formatting
        normalized = self._remove_extra_whitespace(query)
        
        # Sort fields alphabetically for consistent ordering
        normalized = self._sort_fields(normalized)
        
        # Include variables in normalization if present
        if variables:
            vars_str = json.dumps(variables, sort_keys=True, separators=(',', ':'))
            normalized = f"{normalized}|vars:{vars_str}"
        
        return normalized
    
    def _remove_extra_whitespace(self, query: str) -> str:
        """Remove extra whitespace from query"""
        import re
        # Replace multiple spaces with single space
        query = re.sub(r'\s+', ' ', query)
        # Remove spaces around braces and other GraphQL syntax
        query = re.sub(r'\s*{\s*', '{', query)
        query = re.sub(r'\s*}\s*', '}', query)
        query = re.sub(r'\s*\(\s*', '(', query)
        query = re.sub(r'\s*\)\s*', ')', query)
        query = re.sub(r'\s*:\s*', ':', query)
        query = re.sub(r'\s*,\s*', ',', query)
        return query.strip()
    
    def _sort_fields(self, query: str) -> str:
        """Sort fields alphabetically (simplified implementation)"""
        # This is a simplified version - full implementation would use AST
        return query
    
    def generate_cache_key(self, query: str, variables: Optional[Dict[str, Any]] = None) -> str:
        """Generate cache key from normalized query"""
        normalized = self.normalize_query(query, variables)
        return hashlib.sha256(normalized.encode()).hexdigest()


class MultiTierCache:
    """Multi-tier caching system with memory and Redis"""
    
    def __init__(self, redis_client: aioredis.Redis):
        self.redis_client = redis_client
        self.memory_cache: Dict[str, Tuple[Any, datetime, int]] = {}  # key -> (value, expiry, size)
        self.memory_cache_size = 0
        self.max_memory_size = 100 * 1024 * 1024  # 100MB
        self.metrics = CacheMetrics()
        self.query_normalizer = GraphQLQueryNormalizer()
        
        # Start cleanup task
        self._cleanup_task = asyncio.create_task(self._cleanup_expired_entries())
    
    async def get(self, key: str, config: CacheConfig) -> Optional[Any]:
        """Get value from cache with fallback strategy"""
        try:
            # Try memory cache first for multi-tier strategy
            if config.strategy in [CacheStrategy.MEMORY_ONLY, CacheStrategy.MULTI_TIER]:
                memory_result = await self._get_from_memory(key)
                if memory_result is not None:
                    self.metrics.record_hit("memory", key)
                    return memory_result
                else:
                    self.metrics.record_miss("memory", key)
            
            # Try Redis cache
            if config.strategy in [CacheStrategy.REDIS_ONLY, CacheStrategy.MULTI_TIER]:
                redis_result = await self._get_from_redis(key, config)
                if redis_result is not None:
                    self.metrics.record_hit("redis", key)
                    
                    # Populate memory cache for multi-tier
                    if config.strategy == CacheStrategy.MULTI_TIER:
                        await self._set_in_memory(key, redis_result, config.ttl)
                    
                    return redis_result
                else:
                    self.metrics.record_miss("redis", key)
            
            return None
            
        except Exception as e:
            logger.error(f"Cache get error for key {key}: {e}")
            self.metrics.record_error("get", str(e))
            return None
    
    async def set(self, key: str, value: Any, config: CacheConfig) -> bool:
        """Set value in cache"""
        try:
            # Serialize value
            serialized_value = await self._serialize_value(value, config)
            
            # Check size limits
            if config.max_size and len(serialized_value) > config.max_size:
                logger.warning(f"Cache value too large for key {key}: {len(serialized_value)} bytes")
                return False
            
            # Set in appropriate cache layers
            success = True
            
            if config.strategy in [CacheStrategy.MEMORY_ONLY, CacheStrategy.MULTI_TIER]:
                success &= await self._set_in_memory(key, value, config.ttl)
            
            if config.strategy in [CacheStrategy.REDIS_ONLY, CacheStrategy.MULTI_TIER, CacheStrategy.WRITE_THROUGH]:
                success &= await self._set_in_redis(key, serialized_value, config)
            
            if success:
                self.metrics.record_set(key, len(serialized_value))
            
            return success
            
        except Exception as e:
            logger.error(f"Cache set error for key {key}: {e}")
            self.metrics.record_error("set", str(e))
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete value from all cache layers"""
        try:
            success = True
            
            # Delete from memory
            if key in self.memory_cache:
                _, _, size = self.memory_cache[key]
                del self.memory_cache[key]
                self.memory_cache_size -= size
            
            # Delete from Redis
            result = await self.redis_client.delete(key)
            success &= result > 0
            
            if success:
                self.metrics.record_delete(key)
            
            return success
            
        except Exception as e:
            logger.error(f"Cache delete error for key {key}: {e}")
            self.metrics.record_error("delete", str(e))
            return False
    
    async def invalidate_by_tags(self, tags: List[str]) -> int:
        """Invalidate cache entries by tags"""
        try:
            invalidated_count = 0
            
            for tag in tags:
                # Get keys associated with tag
                tag_key = f"tag:{tag}"
                tagged_keys = await self.redis_client.smembers(tag_key)
                
                # Delete tagged keys
                if tagged_keys:
                    pipeline = self.redis_client.pipeline()
                    for key in tagged_keys:
                        pipeline.delete(key)
                        # Also remove from memory cache
                        if key in self.memory_cache:
                            _, _, size = self.memory_cache[key]
                            del self.memory_cache[key]
                            self.memory_cache_size -= size
                    
                    # Remove tag set
                    pipeline.delete(tag_key)
                    results = await pipeline.execute()
                    invalidated_count += sum(results[:-1])  # Exclude tag set deletion
            
            self.metrics.record_invalidation(tags, invalidated_count)
            return invalidated_count
            
        except Exception as e:
            logger.error(f"Cache invalidation error for tags {tags}: {e}")
            self.metrics.record_error("invalidate", str(e))
            return 0
    
    async def _get_from_memory(self, key: str) -> Optional[Any]:
        """Get value from memory cache"""
        if key in self.memory_cache:
            value, expiry, _ = self.memory_cache[key]
            if datetime.utcnow() < expiry:
                return value
            else:
                # Remove expired entry
                size = self.memory_cache[key][2]
                del self.memory_cache[key]
                self.memory_cache_size -= size
        return None
    
    async def _set_in_memory(self, key: str, value: Any, ttl: int) -> bool:
        """Set value in memory cache"""
        try:
            # Estimate size
            size = len(pickle.dumps(value))
            
            # Check if we need to evict entries
            while self.memory_cache_size + size > self.max_memory_size and self.memory_cache:
                await self._evict_lru_entry()
            
            # Set value with expiry
            expiry = datetime.utcnow() + timedelta(seconds=ttl)
            
            # Remove old entry if exists
            if key in self.memory_cache:
                old_size = self.memory_cache[key][2]
                self.memory_cache_size -= old_size
            
            self.memory_cache[key] = (value, expiry, size)
            self.memory_cache_size += size
            
            return True
            
        except Exception as e:
            logger.error(f"Memory cache set error: {e}")
            return False
    
    async def _get_from_redis(self, key: str, config: CacheConfig) -> Optional[Any]:
        """Get value from Redis cache"""
        try:
            serialized_value = await self.redis_client.get(key)
            if serialized_value:
                return await self._deserialize_value(serialized_value, config)
            return None
        except Exception as e:
            logger.error(f"Redis get error for key {key}: {e}")
            return None
    
    async def _set_in_redis(self, key: str, serialized_value: bytes, config: CacheConfig) -> bool:
        """Set value in Redis cache"""
        try:
            # Set with TTL
            success = await self.redis_client.setex(key, config.ttl, serialized_value)
            
            # Add to tag sets for invalidation
            if config.invalidation_tags:
                pipeline = self.redis_client.pipeline()
                for tag in config.invalidation_tags:
                    tag_key = f"tag:{tag}"
                    pipeline.sadd(tag_key, key)
                    pipeline.expire(tag_key, config.ttl + 3600)  # Tag TTL longer than cache TTL
                await pipeline.execute()
            
            return bool(success)
            
        except Exception as e:
            logger.error(f"Redis set error for key {key}: {e}")
            return False
    
    async def _serialize_value(self, value: Any, config: CacheConfig) -> bytes:
        """Serialize value for storage"""
        if config.serialize_method == "json":
            serialized = json.dumps(value, default=str).encode()
        elif config.serialize_method == "pickle":
            serialized = pickle.dumps(value)
        else:
            # Default to JSON
            serialized = json.dumps(value, default=str).encode()
        
        # Compress if enabled
        if config.compress:
            serialized = zlib.compress(serialized)
        
        return serialized
    
    async def _deserialize_value(self, serialized_value: bytes, config: CacheConfig) -> Any:
        """Deserialize value from storage"""
        # Decompress if needed
        if config.compress:
            serialized_value = zlib.decompress(serialized_value)
        
        if config.serialize_method == "json":
            return json.loads(serialized_value.decode())
        elif config.serialize_method == "pickle":
            return pickle.loads(serialized_value)
        else:
            return json.loads(serialized_value.decode())
    
    async def _evict_lru_entry(self):
        """Evict least recently used entry from memory cache"""
        if not self.memory_cache:
            return
        
        # Find entry with earliest expiry (simple LRU approximation)
        oldest_key = min(self.memory_cache.keys(), 
                        key=lambda k: self.memory_cache[k][1])
        
        _, _, size = self.memory_cache[oldest_key]
        del self.memory_cache[oldest_key]
        self.memory_cache_size -= size
    
    async def _cleanup_expired_entries(self):
        """Periodic cleanup of expired memory cache entries"""
        while True:
            try:
                await asyncio.sleep(60)  # Cleanup every minute
                
                now = datetime.utcnow()
                expired_keys = [
                    key for key, (_, expiry, _) in self.memory_cache.items()
                    if now >= expiry
                ]
                
                for key in expired_keys:
                    size = self.memory_cache[key][2]
                    del self.memory_cache[key]
                    self.memory_cache_size -= size
                
                if expired_keys:
                    logger.debug(f"Cleaned up {len(expired_keys)} expired cache entries")
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cache cleanup: {e}")
    
    async def cleanup(self):
        """Cleanup cache resources"""
        if hasattr(self, '_cleanup_task'):
            self._cleanup_task.cancel()
        self.memory_cache.clear()
        self.memory_cache_size = 0


class GraphQLCacheMiddleware(Middleware):
    """GraphQL caching middleware with intelligent cache management"""
    
    def __init__(self, redis_client: aioredis.Redis):
        self.cache = MultiTierCache(redis_client)
        self.default_config = CacheConfig()
        self.field_configs: Dict[str, CacheConfig] = {}
        self.cache_stats = {"hits": 0, "misses": 0, "sets": 0}
    
    def configure_field_caching(self, field_name: str, config: CacheConfig):
        """Configure caching for specific fields"""
        self.field_configs[field_name] = config
    
    async def resolve(self, next, root, info: GraphQLResolveInfo, **args):
        """Middleware resolver with caching"""
        field_name = info.field_name
        operation_name = info.operation.name.value if info.operation.name else None
        
        # Get cache configuration for this field
        cache_config = self.field_configs.get(field_name, self.default_config)
        
        # Skip caching for mutations and subscriptions
        if info.operation.operation.value in ['mutation', 'subscription']:
            return await next(root, info, **args)
        
        # Skip caching if strategy is NO_CACHE
        if cache_config.strategy == CacheStrategy.NO_CACHE:
            return await next(root, info, **args)
        
        # Generate cache key
        cache_key = await self._generate_cache_key(info, args, cache_config)
        
        # Try to get from cache
        cached_result = await self.cache.get(cache_key, cache_config)
        if cached_result is not None:
            self.cache_stats["hits"] += 1
            log_cache_operation("hit", field_name, cache_key)
            return cached_result
        
        # Cache miss - execute resolver
        self.cache_stats["misses"] += 1
        log_cache_operation("miss", field_name, cache_key)
        
        try:
            result = await next(root, info, **args)
            
            # Cache the result if it's cacheable
            if await self._is_cacheable(result, info, cache_config):
                success = await self.cache.set(cache_key, result, cache_config)
                if success:
                    self.cache_stats["sets"] += 1
                    log_cache_operation("set", field_name, cache_key)
            
            return result
            
        except Exception as e:
            # Don't cache errors
            logger.error(f"Error in resolver {field_name}: {e}")
            raise
    
    async def _generate_cache_key(self, info: GraphQLResolveInfo, args: Dict[str, Any], config: CacheConfig) -> str:
        """Generate cache key for the resolver"""
        # Base key components
        field_name = info.field_name
        parent_type = info.parent_type.name if info.parent_type else "root"
        
        # Include arguments in key
        args_hash = ""
        if args:
            args_str = json.dumps(args, sort_keys=True, default=str)
            args_hash = hashlib.md5(args_str.encode()).hexdigest()[:8]
        
        # Get user context for scoped caching
        user_id = None
        tenant_id = None
        
        try:
            user = await get_current_user(info.context["request"])
            if user:
                user_id = str(user.id)
                tenant_id = getattr(user, 'tenant_id', None)
        except:
            pass  # Anonymous access
        
        # Build base key
        base_key = f"{parent_type}:{field_name}"
        if args_hash:
            base_key += f":{args_hash}"
        
        # Apply scoping
        return config.get_cache_key(base_key, user_id, tenant_id)
    
    async def _is_cacheable(self, result: Any, info: GraphQLResolveInfo, config: CacheConfig) -> bool:
        """Determine if result should be cached"""
        # Don't cache None results
        if result is None:
            return False
        
        # Don't cache errors
        if isinstance(result, Exception):
            return False
        
        # Don't cache very large results (if size limit set)
        if config.max_size:
            try:
                size = len(json.dumps(result, default=str).encode())
                if size > config.max_size:
                    return False
            except:
                return False  # Can't serialize
        
        # Don't cache real-time data fields
        realtime_fields = ["live_count", "current_viewers", "real_time_stats"]
        if info.field_name in realtime_fields:
            return False
        
        return True
    
    async def invalidate_field_cache(self, field_name: str, tags: Optional[List[str]] = None):
        """Invalidate cache for specific field"""
        if tags:
            await self.cache.invalidate_by_tags(tags)
        else:
            # Invalidate all entries for this field (simplified)
            await self.cache.invalidate_by_tags([f"field:{field_name}"])
    
    async def invalidate_user_cache(self, user_id: str):
        """Invalidate all cache entries for a user"""
        await self.cache.invalidate_by_tags([f"user:{user_id}"])
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        memory_stats = {
            "size": self.cache.memory_cache_size,
            "entries": len(self.cache.memory_cache),
            "max_size": self.cache.max_memory_size
        }
        
        return {
            "hits": self.cache_stats["hits"],
            "misses": self.cache_stats["misses"],
            "sets": self.cache_stats["sets"],
            "hit_rate": self.cache_stats["hits"] / max(self.cache_stats["hits"] + self.cache_stats["misses"], 1),
            "memory": memory_stats
        }
    
    async def cleanup(self):
        """Cleanup cache resources"""
        await self.cache.cleanup()


# Factory function to create cache middleware
async def create_graphql_cache_middleware() -> GraphQLCacheMiddleware:
    """Create GraphQL cache middleware with Redis connection"""
    redis_client = aioredis.from_url(
        settings.REDIS_URL,
        encoding="utf-8",
        decode_responses=False  # We handle encoding ourselves
    )
    
    middleware = GraphQLCacheMiddleware(redis_client)
    
    # Configure caching for common fields
    middleware.configure_field_caching("{{entity_name}}", CacheConfig(
        ttl=300,  # 5 minutes
        strategy=CacheStrategy.MULTI_TIER,
        scope=CacheScope.GLOBAL,
        invalidation_tags=["{{entity_name}}", "entity"]
    ))
    
    middleware.configure_field_caching("{{entity_name}}_list", CacheConfig(
        ttl=600,  # 10 minutes
        strategy=CacheStrategy.REDIS_ONLY,
        scope=CacheScope.USER,
        invalidation_tags=["{{entity_name}}_list", "entity_list"]
    ))
    
    middleware.configure_field_caching("analytics", CacheConfig(
        ttl=1800,  # 30 minutes
        strategy=CacheStrategy.MULTI_TIER,
        scope=CacheScope.GLOBAL,
        invalidation_tags=["analytics"]
    ))
    
    return middleware


# Export for template system
__all__ = [
    "GraphQLCacheMiddleware",
    "MultiTierCache",
    "CacheConfig",
    "CacheStrategy", 
    "CacheScope",
    "GraphQLQueryNormalizer",
    "create_graphql_cache_middleware"
]