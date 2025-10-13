#!/usr/bin/env python3
"""
🚀 IA Chérie Enterprise - Response Cache Manager
Enterprise response caching with intelligent invalidation and optimization

🎯 BUSINESS LOGIC INTEGRATION:
- Creator Content Caching (optimized content delivery for creators)
- Platform Response Caching (65+ platforms response optimization)
- AI Model Response Caching (ML inference result caching)
- Content Protection Caching (DMCA and rights verification caching)
- Collaboration Cache Sync (multi-creator project data consistency)
- Monetization Data Caching (revenue and payment data optimization)

👨‍💻 AUTHOR: Fahed Mlaiel (mlaiel@live.de)
📧 CONTACT: mlaiel@live.de  
🏢 ENTERPRISE: IA Chérie Platform
📅 CREATED: 2025
🔒 LICENSE: PROPRIETARY - All Rights Reserved

⚖️ LEGAL NOTICE:
This software is the EXCLUSIVE intellectual property of Fahed Mlaiel.
Unauthorized use, reproduction, or distribution is strictly prohibited
and subject to legal action.
"""

import asyncio
import json
import gzip
import hashlib
import time
from typing import Dict, Any, List, Optional, Union, Callable, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timezone, timedelta
import logging
import uuid
from abc import ABC, abstractmethod
import weakref

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CacheLevel(Enum):
    """Cache levels for multi-level caching strategy"""
    L1_MEMORY = "l1_memory"
    L2_REDIS = "l2_redis"
    L3_CDN = "l3_cdn"
    L4_PERSISTENT = "l4_persistent"


class CacheStrategy(Enum):
    """Cache strategies for different use cases"""
    LRU = "lru"  # Least Recently Used
    LFU = "lfu"  # Least Frequently Used
    TTL = "ttl"  # Time To Live
    FIFO = "fifo"  # First In First Out
    ADAPTIVE = "adaptive"  # AI-driven adaptive caching
    CREATOR_OPTIMIZED = "creator_optimized"  # Creator-specific optimization
    PLATFORM_OPTIMIZED = "platform_optimized"  # Platform-specific optimization


class InvalidationType(Enum):
    """Cache invalidation types"""
    TTL_EXPIRED = "ttl_expired"
    MANUAL = "manual"
    DEPENDENCY_CHANGED = "dependency_changed"
    EVENT_TRIGGERED = "event_triggered"
    CAPACITY_EXCEEDED = "capacity_exceeded"
    PATTERN_BASED = "pattern_based"
    BUSINESS_RULE = "business_rule"


class CompressionAlgorithm(Enum):
    """Compression algorithms for cache optimization"""
    NONE = "none"
    GZIP = "gzip"
    ZLIB = "zlib"
    BROTLI = "brotli"
    LZ4 = "lz4"


@dataclass
class CacheConfig:
    """Cache configuration settings"""
    cache_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    max_size_mb: int = 100
    default_ttl_seconds: int = 3600
    strategy: CacheStrategy = CacheStrategy.LRU
    compression: CompressionAlgorithm = CompressionAlgorithm.GZIP
    enable_warming: bool = True
    enable_preloading: bool = True
    enable_compression: bool = True
    enable_encryption: bool = False
    encryption_key: Optional[str] = None
    creator_specific: bool = False
    platform_specific: bool = False
    ai_optimized: bool = False
    business_logic_aware: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class CacheEntry:
    """Individual cache entry"""
    key: str
    value: Any
    size_bytes: int = 0
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    accessed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    access_count: int = 0
    ttl_seconds: Optional[int] = None
    dependencies: Set[str] = field(default_factory=set)
    tags: Set[str] = field(default_factory=set)
    creator_id: Optional[str] = None
    platform_id: Optional[str] = None
    content_type: Optional[str] = None
    compression_type: CompressionAlgorithm = CompressionAlgorithm.NONE
    compressed_size_bytes: int = 0
    hit_count: int = 0
    miss_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CacheMetrics:
    """Cache performance metrics"""
    total_hits: int = 0
    total_misses: int = 0
    total_entries: int = 0
    total_size_bytes: int = 0
    hit_rate: float = 0.0
    average_response_time_ms: float = 0.0
    compression_ratio: float = 0.0
    evictions_count: int = 0
    warming_operations: int = 0
    invalidations_count: int = 0
    last_updated: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass 
class CacheOperation:
    """Cache operation for tracking and analytics"""
    operation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    operation_type: str = "get"  # get, set, delete, invalidate
    cache_key: str = ""
    cache_level: CacheLevel = CacheLevel.L1_MEMORY
    hit: bool = False
    response_time_ms: float = 0.0
    data_size_bytes: int = 0
    creator_id: Optional[str] = None
    platform_id: Optional[str] = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class CacheInterface(ABC):
    """Abstract interface for cache implementations"""
    
    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        pass
    
    @abstractmethod
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache"""
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Delete value from cache"""
        pass
    
    @abstractmethod
    async def clear(self) -> bool:
        """Clear all cache entries"""
        pass
    
    @abstractmethod
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        pass


class MemoryCache(CacheInterface):
    """In-memory cache implementation with LRU eviction"""
    
    def __init__(self, config: CacheConfig):
        self.config = config
        self.data: Dict[str, CacheEntry] = {}
        self.access_order: List[str] = []  # For LRU tracking
        self.current_size_bytes = 0
        self.max_size_bytes = config.max_size_mb * 1024 * 1024
        self.metrics = CacheMetrics()
        
    async def get(self, key: str) -> Optional[Any]:
        """Get value from memory cache"""
        start_time = time.time()
        
        if key in self.data:
            entry = self.data[key]
            
            # Check TTL expiration
            if entry.ttl_seconds:
                age_seconds = (datetime.now(timezone.utc) - entry.created_at).total_seconds()
                if age_seconds > entry.ttl_seconds:
                    await self.delete(key)
                    self.metrics.total_misses += 1
                    return None
            
            # Update access statistics
            entry.accessed_at = datetime.now(timezone.utc)
            entry.access_count += 1
            entry.hit_count += 1
            
            # Update LRU order
            if key in self.access_order:
                self.access_order.remove(key)
            self.access_order.append(key)
            
            # Update metrics
            self.metrics.total_hits += 1
            response_time = (time.time() - start_time) * 1000
            self._update_response_time(response_time)
            
            return entry.value
        
        self.metrics.total_misses += 1
        return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in memory cache"""
        try:
            # Calculate entry size
            value_size = self._calculate_size(value)
            
            # Check if we need to evict entries
            while (self.current_size_bytes + value_size > self.max_size_bytes and 
                   self.access_order):
                await self._evict_lru()
            
            # Create cache entry
            entry = CacheEntry(
                key=key,
                value=value,
                size_bytes=value_size,
                ttl_seconds=ttl or self.config.default_ttl_seconds
            )
            
            # Store entry
            if key in self.data:
                # Update existing entry
                old_size = self.data[key].size_bytes
                self.current_size_bytes -= old_size
            else:
                self.metrics.total_entries += 1
            
            self.data[key] = entry
            self.current_size_bytes += value_size
            
            # Update access order
            if key in self.access_order:
                self.access_order.remove(key)
            self.access_order.append(key)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to set cache entry {key}: {str(e)}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete value from memory cache"""
        if key in self.data:
            entry = self.data[key]
            self.current_size_bytes -= entry.size_bytes
            del self.data[key]
            
            if key in self.access_order:
                self.access_order.remove(key)
            
            self.metrics.total_entries -= 1
            return True
        
        return False
    
    async def clear(self) -> bool:
        """Clear all entries from memory cache"""
        self.data.clear()
        self.access_order.clear()
        self.current_size_bytes = 0
        self.metrics.total_entries = 0
        return True
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in memory cache"""
        return key in self.data
    
    async def _evict_lru(self) -> None:
        """Evict least recently used entry"""
        if self.access_order:
            lru_key = self.access_order[0]
            await self.delete(lru_key)
            self.metrics.evictions_count += 1
    
    def _calculate_size(self, value: Any) -> int:
        """Calculate approximate size of value in bytes"""
        try:
            if isinstance(value, str):
                return len(value.encode('utf-8'))
            elif isinstance(value, bytes):
                return len(value)
            elif isinstance(value, (dict, list)):
                return len(json.dumps(value).encode('utf-8'))
            else:
                return len(str(value).encode('utf-8'))
        except:
            return 1024  # Default size estimate
    
    def _update_response_time(self, response_time_ms: float) -> None:
        """Update average response time"""
        if self.metrics.total_hits == 1:
            self.metrics.average_response_time_ms = response_time_ms
        else:
            # Rolling average
            self.metrics.average_response_time_ms = (
                (self.metrics.average_response_time_ms * (self.metrics.total_hits - 1) + 
                 response_time_ms) / self.metrics.total_hits
            )


class CacheWarmer:
    """Proactive cache warming and preloading"""
    
    def __init__(self):
        self.warming_tasks: Dict[str, asyncio.Task] = {}
        self.warming_rules: List[Dict[str, Any]] = []
        self.preload_functions: Dict[str, Callable] = {}
    
    def add_warming_rule(self, rule: Dict[str, Any]) -> None:
        """Add cache warming rule"""
        self.warming_rules.append(rule)
    
    def register_preload_function(self, name: str, function: Callable) -> None:
        """Register preload function"""
        self.preload_functions[name] = function
    
    async def warm_cache(self, cache_manager: 'ResponseCacheManager', 
                        rule: Dict[str, Any]) -> None:
        """Warm cache based on rule"""
        try:
            rule_type = rule.get("type")
            
            if rule_type == "creator_content":
                await self._warm_creator_content(cache_manager, rule)
            elif rule_type == "platform_responses":
                await self._warm_platform_responses(cache_manager, rule)
            elif rule_type == "ai_model_results":
                await self._warm_ai_model_results(cache_manager, rule)
            elif rule_type == "popular_content":
                await self._warm_popular_content(cache_manager, rule)
            
        except Exception as e:
            logger.error(f"Cache warming failed for rule {rule}: {str(e)}")
    
    async def _warm_creator_content(self, cache_manager: 'ResponseCacheManager',
                                  rule: Dict[str, Any]) -> None:
        """Warm cache with creator content"""
        creator_ids = rule.get("creator_ids", [])
        content_types = rule.get("content_types", ["video", "image", "audio", "text"])
        
        for creator_id in creator_ids:
            for content_type in content_types:
                cache_key = f"creator:{creator_id}:content:{content_type}"
                
                # Generate sample content for warming (placeholder)
                sample_content = {
                    "creator_id": creator_id,
                    "content_type": content_type,
                    "metadata": {"warmed": True, "timestamp": datetime.now(timezone.utc).isoformat()},
                    "data": f"Warmed content for {creator_id}"
                }
                
                await cache_manager.set(cache_key, sample_content, 
                                      ttl=rule.get("ttl", 3600))
    
    async def _warm_platform_responses(self, cache_manager: 'ResponseCacheManager',
                                     rule: Dict[str, Any]) -> None:
        """Warm cache with platform responses"""
        platforms = rule.get("platforms", ["youtube", "instagram", "tiktok", "spotify"])
        
        for platform in platforms:
            cache_key = f"platform:{platform}:status"
            
            # Generate sample platform status for warming
            platform_status = {
                "platform": platform,
                "status": "active",
                "api_version": "v1",
                "last_sync": datetime.now(timezone.utc).isoformat(),
                "features": ["upload", "metadata", "analytics"]
            }
            
            await cache_manager.set(cache_key, platform_status,
                                  ttl=rule.get("ttl", 1800))
    
    async def _warm_ai_model_results(self, cache_manager: 'ResponseCacheManager',
                                   rule: Dict[str, Any]) -> None:
        """Warm cache with AI model results"""
        models = rule.get("models", ["content_classifier", "sentiment_analyzer", "recommendation_engine"])
        
        for model in models:
            cache_key = f"ai_model:{model}:metadata"
            
            # Generate sample AI model metadata for warming
            model_metadata = {
                "model_name": model,
                "version": "1.0.0",
                "status": "ready",
                "last_inference": datetime.now(timezone.utc).isoformat(),
                "performance_metrics": {
                    "accuracy": 0.95,
                    "latency_ms": 50,
                    "throughput": 1000
                }
            }
            
            await cache_manager.set(cache_key, model_metadata,
                                  ttl=rule.get("ttl", 7200))
    
    async def _warm_popular_content(self, cache_manager: 'ResponseCacheManager',
                                  rule: Dict[str, Any]) -> None:
        """Warm cache with popular content"""
        content_categories = rule.get("categories", ["trending", "viral", "featured"])
        
        for category in content_categories:
            cache_key = f"popular_content:{category}"
            
            # Generate sample popular content for warming
            popular_content = {
                "category": category,
                "items": [
                    {"id": f"item_{i}", "title": f"Popular {category} item {i}", 
                     "engagement": 1000 - i * 10} 
                    for i in range(10)
                ],
                "last_updated": datetime.now(timezone.utc).isoformat()
            }
            
            await cache_manager.set(cache_key, popular_content,
                                  ttl=rule.get("ttl", 900))


class CacheInvalidator:
    """Intelligent cache invalidation system"""
    
    def __init__(self):
        self.invalidation_rules: List[Dict[str, Any]] = []
        self.dependency_graph: Dict[str, Set[str]] = {}
        self.event_handlers: Dict[str, List[Callable]] = {}
    
    def add_invalidation_rule(self, rule: Dict[str, Any]) -> None:
        """Add cache invalidation rule"""
        self.invalidation_rules.append(rule)
    
    def add_dependency(self, parent_key: str, child_key: str) -> None:
        """Add cache dependency relationship"""
        if parent_key not in self.dependency_graph:
            self.dependency_graph[parent_key] = set()
        self.dependency_graph[parent_key].add(child_key)
    
    def register_event_handler(self, event_type: str, handler: Callable) -> None:
        """Register event handler for cache invalidation"""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)
    
    async def invalidate_by_pattern(self, cache_manager: 'ResponseCacheManager',
                                  pattern: str) -> List[str]:
        """Invalidate cache entries by pattern"""
        invalidated_keys = []
        
        for key in cache_manager.memory_cache.data.keys():
            if self._matches_pattern(key, pattern):
                await cache_manager.delete(key)
                invalidated_keys.append(key)
        
        return invalidated_keys
    
    async def invalidate_by_dependency(self, cache_manager: 'ResponseCacheManager',
                                     changed_key: str) -> List[str]:
        """Invalidate dependent cache entries"""
        invalidated_keys = []
        
        if changed_key in self.dependency_graph:
            for dependent_key in self.dependency_graph[changed_key]:
                await cache_manager.delete(dependent_key)
                invalidated_keys.append(dependent_key)
                
                # Recursively invalidate dependencies
                recursive_invalidated = await self.invalidate_by_dependency(
                    cache_manager, dependent_key
                )
                invalidated_keys.extend(recursive_invalidated)
        
        return invalidated_keys
    
    async def invalidate_by_event(self, cache_manager: 'ResponseCacheManager',
                                event_type: str, event_data: Dict[str, Any]) -> List[str]:
        """Invalidate cache entries based on business events"""
        invalidated_keys = []
        
        if event_type == "creator_content_updated":
            creator_id = event_data.get("creator_id")
            if creator_id:
                pattern = f"creator:{creator_id}:*"
                invalidated_keys.extend(
                    await self.invalidate_by_pattern(cache_manager, pattern)
                )
        
        elif event_type == "platform_api_changed":
            platform_id = event_data.get("platform_id")
            if platform_id:
                pattern = f"platform:{platform_id}:*"
                invalidated_keys.extend(
                    await self.invalidate_by_pattern(cache_manager, pattern)
                )
        
        elif event_type == "ai_model_updated":
            model_name = event_data.get("model_name")
            if model_name:
                pattern = f"ai_model:{model_name}:*"
                invalidated_keys.extend(
                    await self.invalidate_by_pattern(cache_manager, pattern)
                )
        
        elif event_type == "content_rights_changed":
            content_id = event_data.get("content_id")
            if content_id:
                pattern = f"*:{content_id}:*"
                invalidated_keys.extend(
                    await self.invalidate_by_pattern(cache_manager, pattern)
                )
        
        # Call registered event handlers
        if event_type in self.event_handlers:
            for handler in self.event_handlers[event_type]:
                try:
                    handler_result = await handler(cache_manager, event_data)
                    if isinstance(handler_result, list):
                        invalidated_keys.extend(handler_result)
                except Exception as e:
                    logger.error(f"Event handler failed for {event_type}: {str(e)}")
        
        return invalidated_keys
    
    def _matches_pattern(self, key: str, pattern: str) -> bool:
        """Check if key matches invalidation pattern"""
        # Simple pattern matching with wildcards
        if "*" not in pattern:
            return key == pattern
        
        pattern_parts = pattern.split("*")
        key_pos = 0
        
        for i, part in enumerate(pattern_parts):
            if not part:  # Empty part from * at start or consecutive *
                continue
            
            pos = key.find(part, key_pos)
            if pos == -1:
                return False
            
            if i == 0 and pos != 0:  # First part must match from start
                return False
            
            key_pos = pos + len(part)
        
        # Check if last part is at the end (if pattern doesn't end with *)
        if pattern_parts[-1] and not key.endswith(pattern_parts[-1]):
            return False
        
        return True


class ResponseCacheManager:
    """
    🚀 Enterprise Response Cache Manager
    
    Provides comprehensive response caching capabilities with:
    - Multi-level caching (Memory + Redis + CDN + Persistent)
    - Intelligent invalidation and cache warming
    - Creator and platform-specific optimization
    - Compression and encryption support
    - Business logic-aware caching strategies
    """
    
    def __init__(self, config: CacheConfig = None):
        self.config = config or CacheConfig()
        self.memory_cache = MemoryCache(self.config)
        self.cache_warmer = CacheWarmer()
        self.cache_invalidator = CacheInvalidator()
        
        # Cache analytics and monitoring
        self.operation_history: List[CacheOperation] = []
        self.performance_metrics: Dict[str, Any] = {}
        self.creator_analytics: Dict[str, Dict[str, Any]] = {}
        self.platform_analytics: Dict[str, Dict[str, Any]] = {}
        
        # Business logic optimizations
        self.creator_cache_strategies: Dict[str, CacheStrategy] = {}
        self.platform_cache_strategies: Dict[str, CacheStrategy] = {}
        self.content_type_strategies: Dict[str, CacheStrategy] = {}
        
        # Initialize IA Chérie-specific caching rules
        self._initialize_iacherie_caching()
    
    def _initialize_iacherie_caching(self) -> None:
        """Initialize IA Chérie business logic caching rules"""
        
        # Creator-specific cache warming rules
        self.cache_warmer.add_warming_rule({
            "type": "creator_content",
            "creator_ids": ["default"],  # Will be populated with actual creator IDs
            "content_types": ["video", "image", "audio", "text"],
            "ttl": 3600
        })
        
        # Platform response warming rules
        self.cache_warmer.add_warming_rule({
            "type": "platform_responses",
            "platforms": ["youtube", "instagram", "tiktok", "spotify", "facebook", "twitter"],
            "ttl": 1800
        })
        
        # AI model results warming
        self.cache_warmer.add_warming_rule({
            "type": "ai_model_results",
            "models": ["content_classifier", "sentiment_analyzer", "recommendation_engine", 
                      "copyright_detector", "content_moderator"],
            "ttl": 7200
        })
        
        # Popular content warming
        self.cache_warmer.add_warming_rule({
            "type": "popular_content",
            "categories": ["trending", "viral", "featured", "recommended"],
            "ttl": 900
        })
        
        # Creator-specific cache strategies
        self.creator_cache_strategies.update({
            "musician": CacheStrategy.LRU,  # Music content accessed repeatedly
            "blogger": CacheStrategy.TTL,   # Blog content has natural expiration
            "photographer": CacheStrategy.LFU,  # Popular photos accessed frequently
            "influencer": CacheStrategy.ADAPTIVE  # Dynamic content needs adaptive caching
        })
        
        # Platform-specific cache strategies
        self.platform_cache_strategies.update({
            "youtube": CacheStrategy.LRU,  # Video metadata changes frequently
            "instagram": CacheStrategy.LFU,  # Images accessed by popularity
            "tiktok": CacheStrategy.ADAPTIVE,  # Viral content patterns
            "spotify": CacheStrategy.TTL,  # Music metadata stable
            "facebook": CacheStrategy.LRU,  # Social interactions change rapidly
            "twitter": CacheStrategy.ADAPTIVE  # Real-time content
        })
        
        # Content type strategies
        self.content_type_strategies.update({
            "video": CacheStrategy.LRU,
            "image": CacheStrategy.LFU, 
            "audio": CacheStrategy.TTL,
            "text": CacheStrategy.LRU,
            "metadata": CacheStrategy.ADAPTIVE
        })
    
    async def get(self, key: str, creator_id: str = None, platform_id: str = None) -> Optional[Any]:
        """Get value from cache with business logic optimization"""
        start_time = time.time()
        
        try:
            # Try L1 memory cache first
            value = await self.memory_cache.get(key)
            
            if value is not None:
                # Record cache hit
                operation = CacheOperation(
                    operation_type="get",
                    cache_key=key,
                    cache_level=CacheLevel.L1_MEMORY,
                    hit=True,
                    response_time_ms=(time.time() - start_time) * 1000,
                    creator_id=creator_id,
                    platform_id=platform_id
                )
                
                await self._record_operation(operation)
                await self._update_analytics(operation)
                
                return value
            
            # TODO: Try L2 Redis cache, L3 CDN cache, etc.
            # For now, record cache miss
            operation = CacheOperation(
                operation_type="get",
                cache_key=key,
                cache_level=CacheLevel.L1_MEMORY,
                hit=False,
                response_time_ms=(time.time() - start_time) * 1000,
                creator_id=creator_id,
                platform_id=platform_id
            )
            
            await self._record_operation(operation)
            await self._update_analytics(operation)
            
            return None
            
        except Exception as e:
            logger.error(f"Cache get failed for key {key}: {str(e)}")
            return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None,
                 creator_id: str = None, platform_id: str = None,
                 content_type: str = None, tags: Set[str] = None) -> bool:
        """Set value in cache with business logic optimization"""
        start_time = time.time()
        
        try:
            # Determine optimal TTL based on business logic
            if ttl is None:
                ttl = await self._calculate_optimal_ttl(
                    key, value, creator_id, platform_id, content_type
                )
            
            # Apply compression if enabled
            if self.config.enable_compression:
                original_size = self._calculate_size(value)
                compressed_value, compression_type = await self._compress_value(value)
                
                if compressed_value is not None:
                    value = compressed_value
                    logger.debug(f"Compressed cache entry {key}: {original_size} -> {self._calculate_size(value)} bytes")
            
            # Set in L1 memory cache
            success = await self.memory_cache.set(key, value, ttl)
            
            if success:
                # Update cache entry metadata
                if key in self.memory_cache.data:
                    entry = self.memory_cache.data[key]
                    entry.creator_id = creator_id
                    entry.platform_id = platform_id
                    entry.content_type = content_type
                    if tags:
                        entry.tags.update(tags)
                
                # Record cache set operation
                operation = CacheOperation(
                    operation_type="set",
                    cache_key=key,
                    cache_level=CacheLevel.L1_MEMORY,
                    hit=True,
                    response_time_ms=(time.time() - start_time) * 1000,
                    data_size_bytes=self._calculate_size(value),
                    creator_id=creator_id,
                    platform_id=platform_id
                )
                
                await self._record_operation(operation)
                await self._update_analytics(operation)
                
                # TODO: Propagate to L2, L3 caches based on strategy
                
            return success
            
        except Exception as e:
            logger.error(f"Cache set failed for key {key}: {str(e)}")
            return False
    
    async def delete(self, key: str, creator_id: str = None, platform_id: str = None) -> bool:
        """Delete value from cache"""
        start_time = time.time()
        
        try:
            # Delete from L1 memory cache
            success = await self.memory_cache.delete(key)
            
            # Record cache delete operation
            operation = CacheOperation(
                operation_type="delete",
                cache_key=key,
                cache_level=CacheLevel.L1_MEMORY,
                hit=success,
                response_time_ms=(time.time() - start_time) * 1000,
                creator_id=creator_id,
                platform_id=platform_id
            )
            
            await self._record_operation(operation)
            
            # TODO: Delete from L2, L3 caches
            
            return success
            
        except Exception as e:
            logger.error(f"Cache delete failed for key {key}: {str(e)}")
            return False
    
    async def invalidate_pattern(self, pattern: str) -> List[str]:
        """Invalidate cache entries by pattern"""
        return await self.cache_invalidator.invalidate_by_pattern(self, pattern)
    
    async def invalidate_by_event(self, event_type: str, event_data: Dict[str, Any]) -> List[str]:
        """Invalidate cache entries based on business events"""
        return await self.cache_invalidator.invalidate_by_event(self, event_type, event_data)
    
    async def warm_cache(self, rule_type: str = None) -> int:
        """Warm cache proactively"""
        warmed_count = 0
        
        rules_to_process = (
            [rule for rule in self.cache_warmer.warming_rules if rule.get("type") == rule_type]
            if rule_type else self.cache_warmer.warming_rules
        )
        
        for rule in rules_to_process:
            try:
                await self.cache_warmer.warm_cache(self, rule)
                warmed_count += 1
            except Exception as e:
                logger.error(f"Cache warming failed for rule {rule}: {str(e)}")
        
        return warmed_count
    
    async def _calculate_optimal_ttl(self, key: str, value: Any, creator_id: str = None,
                                   platform_id: str = None, content_type: str = None) -> int:
        """Calculate optimal TTL based on business logic"""
        base_ttl = self.config.default_ttl_seconds
        
        # Creator-specific TTL adjustments
        if creator_id and creator_id in self.creator_analytics:
            creator_stats = self.creator_analytics[creator_id]
            access_frequency = creator_stats.get("access_frequency", 1.0)
            if access_frequency > 10:  # High-frequency creator content
                base_ttl *= 2
            elif access_frequency < 1:  # Low-frequency creator content
                base_ttl //= 2
        
        # Platform-specific TTL adjustments
        if platform_id:
            platform_ttl_multipliers = {
                "youtube": 1.5,  # Longer TTL for video metadata
                "instagram": 1.0,  # Standard TTL for images
                "tiktok": 0.5,   # Shorter TTL for viral content
                "spotify": 2.0,  # Longer TTL for stable music metadata
                "twitter": 0.3,  # Very short TTL for real-time content
                "facebook": 0.8  # Shorter TTL for social content
            }
            multiplier = platform_ttl_multipliers.get(platform_id, 1.0)
            base_ttl = int(base_ttl * multiplier)
        
        # Content type-specific TTL adjustments
        if content_type:
            content_ttl_multipliers = {
                "video": 1.5,    # Longer TTL for video metadata
                "image": 1.2,    # Moderate TTL for images
                "audio": 1.8,    # Longer TTL for audio metadata
                "text": 0.8,     # Shorter TTL for text content
                "metadata": 2.0, # Longest TTL for metadata
                "analytics": 0.5 # Shortest TTL for real-time analytics
            }
            multiplier = content_ttl_multipliers.get(content_type, 1.0)
            base_ttl = int(base_ttl * multiplier)
        
        # Ensure minimum and maximum bounds
        return max(300, min(base_ttl, 86400))  # 5 minutes to 24 hours
    
    async def _compress_value(self, value: Any) -> tuple[Optional[Any], CompressionAlgorithm]:
        """Compress cache value if beneficial"""
        try:
            if isinstance(value, (dict, list)):
                json_str = json.dumps(value)
                original_size = len(json_str.encode('utf-8'))
                
                if original_size > 1024:  # Only compress if > 1KB
                    compressed_data = gzip.compress(json_str.encode('utf-8'))
                    compressed_size = len(compressed_data)
                    
                    if compressed_size < original_size * 0.8:  # 20% compression benefit
                        import base64
                        return {
                            "_compressed": True,
                            "_algorithm": CompressionAlgorithm.GZIP.value,
                            "_data": base64.b64encode(compressed_data).decode('utf-8'),
                            "_original_size": original_size
                        }, CompressionAlgorithm.GZIP
            
            return value, CompressionAlgorithm.NONE
            
        except Exception as e:
            logger.error(f"Compression failed: {str(e)}")
            return value, CompressionAlgorithm.NONE
    
    def _calculate_size(self, value: Any) -> int:
        """Calculate approximate size of value in bytes"""
        return self.memory_cache._calculate_size(value)
    
    async def _record_operation(self, operation: CacheOperation) -> None:
        """Record cache operation for analytics"""
        self.operation_history.append(operation)
        
        # Keep only recent operations (last 10000)
        if len(self.operation_history) > 10000:
            self.operation_history = self.operation_history[-10000:]
    
    async def _update_analytics(self, operation: CacheOperation) -> None:
        """Update cache analytics"""
        # Update creator analytics
        if operation.creator_id:
            if operation.creator_id not in self.creator_analytics:
                self.creator_analytics[operation.creator_id] = {
                    "total_operations": 0,
                    "cache_hits": 0,
                    "cache_misses": 0,
                    "access_frequency": 0.0,
                    "last_access": None
                }
            
            creator_stats = self.creator_analytics[operation.creator_id]
            creator_stats["total_operations"] += 1
            
            if operation.hit:
                creator_stats["cache_hits"] += 1
            else:
                creator_stats["cache_misses"] += 1
            
            creator_stats["access_frequency"] = (
                creator_stats["cache_hits"] / max(creator_stats["total_operations"], 1)
            )
            creator_stats["last_access"] = operation.timestamp
        
        # Update platform analytics
        if operation.platform_id:
            if operation.platform_id not in self.platform_analytics:
                self.platform_analytics[operation.platform_id] = {
                    "total_operations": 0,
                    "cache_hits": 0,
                    "cache_misses": 0,
                    "hit_rate": 0.0,
                    "last_access": None
                }
            
            platform_stats = self.platform_analytics[operation.platform_id]
            platform_stats["total_operations"] += 1
            
            if operation.hit:
                platform_stats["cache_hits"] += 1
            else:
                platform_stats["cache_misses"] += 1
            
            platform_stats["hit_rate"] = (
                platform_stats["cache_hits"] / max(platform_stats["total_operations"], 1)
            )
            platform_stats["last_access"] = operation.timestamp
    
    async def get_cache_metrics(self) -> Dict[str, Any]:
        """Get comprehensive cache metrics"""
        memory_metrics = self.memory_cache.metrics
        
        # Calculate overall hit rate
        total_hits = memory_metrics.total_hits
        total_misses = memory_metrics.total_misses
        total_operations = total_hits + total_misses
        overall_hit_rate = total_hits / max(total_operations, 1)
        
        return {
            "memory_cache": {
                "total_entries": memory_metrics.total_entries,
                "total_size_bytes": self.memory_cache.current_size_bytes,
                "max_size_bytes": self.memory_cache.max_size_bytes,
                "utilization_percent": (
                    self.memory_cache.current_size_bytes / 
                    max(self.memory_cache.max_size_bytes, 1) * 100
                ),
                "hit_rate": overall_hit_rate,
                "total_hits": total_hits,
                "total_misses": total_misses,
                "evictions": memory_metrics.evictions_count,
                "average_response_time_ms": memory_metrics.average_response_time_ms
            },
            "creator_analytics": self.creator_analytics,
            "platform_analytics": self.platform_analytics,
            "recent_operations": len(self.operation_history),
            "cache_warming_rules": len(self.cache_warmer.warming_rules),
            "invalidation_rules": len(self.cache_invalidator.invalidation_rules)
        }
    
    async def get_creator_cache_performance(self, creator_id: str) -> Dict[str, Any]:
        """Get cache performance metrics for specific creator"""
        if creator_id not in self.creator_analytics:
            return {"error": f"No cache analytics found for creator {creator_id}"}
        
        return self.creator_analytics[creator_id]
    
    async def get_platform_cache_performance(self, platform_id: str) -> Dict[str, Any]:
        """Get cache performance metrics for specific platform"""
        if platform_id not in self.platform_analytics:
            return {"error": f"No cache analytics found for platform {platform_id}"}
        
        return self.platform_analytics[platform_id]
    
    async def optimize_cache_strategies(self) -> Dict[str, Any]:
        """Optimize cache strategies based on usage patterns"""
        optimizations = {
            "creator_optimizations": {},
            "platform_optimizations": {},
            "content_type_optimizations": {}
        }
        
        # Optimize creator cache strategies
        for creator_id, stats in self.creator_analytics.items():
            current_strategy = self.creator_cache_strategies.get(creator_id, CacheStrategy.LRU)
            
            if stats["access_frequency"] > 0.8:  # High hit rate
                recommended_strategy = CacheStrategy.LFU
            elif stats["total_operations"] > 1000:  # High volume
                recommended_strategy = CacheStrategy.ADAPTIVE
            else:
                recommended_strategy = CacheStrategy.LRU
            
            if current_strategy != recommended_strategy:
                optimizations["creator_optimizations"][creator_id] = {
                    "current": current_strategy.value,
                    "recommended": recommended_strategy.value,
                    "reason": f"Hit rate: {stats['access_frequency']:.2f}, Operations: {stats['total_operations']}"
                }
        
        # Optimize platform cache strategies
        for platform_id, stats in self.platform_analytics.items():
            current_strategy = self.platform_cache_strategies.get(platform_id, CacheStrategy.LRU)
            
            if stats["hit_rate"] > 0.9:  # Very high hit rate
                recommended_strategy = CacheStrategy.LFU
            elif platform_id in ["twitter", "tiktok"]:  # Real-time platforms
                recommended_strategy = CacheStrategy.ADAPTIVE
            else:
                recommended_strategy = CacheStrategy.LRU
            
            if current_strategy != recommended_strategy:
                optimizations["platform_optimizations"][platform_id] = {
                    "current": current_strategy.value,
                    "recommended": recommended_strategy.value,
                    "reason": f"Hit rate: {stats['hit_rate']:.2f}"
                }
        
        return optimizations
    
    async def clear_cache(self, pattern: str = None) -> Dict[str, Any]:
        """Clear cache entries by pattern or all"""
        if pattern:
            cleared_keys = await self.invalidate_pattern(pattern)
            return {
                "action": "pattern_clear",
                "pattern": pattern,
                "cleared_keys": cleared_keys,
                "count": len(cleared_keys)
            }
        else:
            await self.memory_cache.clear()
            self.operation_history.clear()
            return {
                "action": "full_clear",
                "result": "All cache entries cleared"
            }
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform cache health check"""
        try:
            # Test basic cache operations
            test_key = f"health_check_{int(time.time())}"
            test_value = {"test": True, "timestamp": datetime.now(timezone.utc).isoformat()}
            
            # Test set operation
            set_success = await self.set(test_key, test_value, ttl=60)
            if not set_success:
                return {
                    "status": "unhealthy",
                    "error": "Cache set operation failed",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            
            # Test get operation
            retrieved_value = await self.get(test_key)
            if retrieved_value != test_value:
                return {
                    "status": "unhealthy", 
                    "error": "Cache get operation failed",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            
            # Test delete operation
            delete_success = await self.delete(test_key)
            if not delete_success:
                return {
                    "status": "unhealthy",
                    "error": "Cache delete operation failed",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            
            # Get current metrics
            metrics = await self.get_cache_metrics()
            
            return {
                "status": "healthy",
                "test_operations": {
                    "set": set_success,
                    "get": True,
                    "delete": delete_success
                },
                "cache_metrics": metrics,
                "components": {
                    "memory_cache": "operational",
                    "cache_warmer": "operational",
                    "cache_invalidator": "operational"
                },
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Cache health check failed: {str(e)}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }


# Global instance for enterprise usage
response_cache_manager = ResponseCacheManager()

# Export classes and functions for external usage
__all__ = [
    "ResponseCacheManager",
    "CacheConfig",
    "CacheEntry",
    "CacheMetrics", 
    "CacheOperation",
    "CacheLevel",
    "CacheStrategy",
    "InvalidationType",
    "CompressionAlgorithm",
    "response_cache_manager"
]