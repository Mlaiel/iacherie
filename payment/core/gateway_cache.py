"""🚀 Payment Gateway Cache
==========================

Enterprise caching system for payment gateway performance optimization.
Handles transaction result caching, provider configuration caching,
performance optimization, and cache invalidation strategies.

Features:
- Transaction result caching
- Provider configuration caching
- Performance optimization
- Cache invalidation strategies
- Multi-layer cache architecture
- Intelligent cache warming

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from decimal import Decimal
import json
import hashlib
import pickle
import uuid
import time
from collections import defaultdict, OrderedDict
import aioredis

logger = logging.getLogger(__name__)


class CacheType(Enum):
    """Types of cache storage"""
    MEMORY = "memory"
    REDIS = "redis"
    HYBRID = "hybrid"


class CacheStrategy(Enum):
    """Cache strategies"""
    LRU = "lru"  # Least Recently Used
    LFU = "lfu"  # Least Frequently Used
    TTL = "ttl"  # Time To Live
    FIFO = "fifo"  # First In First Out
    ADAPTIVE = "adaptive"  # Adaptive based on access patterns


class CacheLayer(Enum):
    """Cache layers"""
    L1_MEMORY = "l1_memory"      # In-memory cache (fastest)
    L2_REDIS = "l2_redis"        # Redis cache (persistent)
    L3_DATABASE = "l3_database"  # Database cache (slowest)


class InvalidationStrategy(Enum):
    """Cache invalidation strategies"""
    TTL_BASED = "ttl_based"
    EVENT_BASED = "event_based"
    MANUAL = "manual"
    WRITE_THROUGH = "write_through"
    WRITE_BEHIND = "write_behind"


@dataclass
class CacheEntry:
    """Cache entry information"""
    key: str
    value: Any
    created_at: datetime
    last_accessed: datetime
    access_count: int
    ttl_seconds: Optional[int]
    cache_layer: CacheLayer
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_expired(self) -> bool:
        """Check if cache entry is expired"""
        if not self.ttl_seconds:
            return False
        return (datetime.now() - self.created_at).total_seconds() > self.ttl_seconds
    
    @property
    def age_seconds(self) -> float:
        """Get age of cache entry in seconds"""
        return (datetime.now() - self.created_at).total_seconds()


@dataclass
class CacheStats:
    """Cache statistics"""
    total_requests: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    evictions: int = 0
    invalidations: int = 0
    l1_hits: int = 0
    l2_hits: int = 0
    l3_hits: int = 0
    
    @property
    def hit_rate(self) -> float:
        """Calculate cache hit rate"""
        if self.total_requests == 0:
            return 0.0
        return (self.cache_hits / self.total_requests) * 100
    
    @property
    def miss_rate(self) -> float:
        """Calculate cache miss rate"""
        return 100.0 - self.hit_rate


class PaymentGatewayCache:
    """Enterprise caching system for payment gateway"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.redis_client = None
        self.is_initialized = False
        
        # Cache configuration
        self.cache_type = CacheType(config.get('cache_type', 'hybrid'))
        self.default_ttl = config.get('default_ttl', 3600)  # 1 hour
        self.max_memory_size = config.get('max_memory_size', 1000)  # Max items in memory
        self.cleanup_interval = config.get('cleanup_interval', 300)  # 5 minutes
        
        # Multi-layer cache storage
        self.l1_cache: OrderedDict[str, CacheEntry] = OrderedDict()  # Memory cache
        self.cache_stats = CacheStats()
        
        # Cache warming configuration
        self.warm_cache_on_startup = config.get('warm_cache_on_startup', True)
        self.cache_warming_patterns = config.get('cache_warming_patterns', [])
        
        # Cache key patterns for different data types
        self.key_patterns = {
            'transaction': 'tx:{transaction_id}',
            'provider_config': 'provider:{provider_id}:config',
            'routing_decision': 'routing:{hash}',
            'fraud_score': 'fraud:{transaction_hash}',
            'exchange_rates': 'rates:{currency_pair}',
            'provider_health': 'health:{provider_id}',
            'user_preferences': 'user:{user_id}:prefs',
            'payment_methods': 'methods:{user_id}',
            'analytics': 'analytics:{metric}:{period}'
        }
        
        # TTL configurations for different data types
        self.ttl_configs = {
            'transaction': 3600,        # 1 hour
            'provider_config': 300,     # 5 minutes
            'routing_decision': 1800,   # 30 minutes
            'fraud_score': 7200,        # 2 hours
            'exchange_rates': 60,       # 1 minute
            'provider_health': 30,      # 30 seconds
            'user_preferences': 86400,  # 24 hours
            'payment_methods': 3600,    # 1 hour
            'analytics': 900            # 15 minutes
        }
        
    async def initialize(self):
        """Initialize the cache system"""
        try:
            # Initialize Redis connection for L2 cache
            if self.cache_type in [CacheType.REDIS, CacheType.HYBRID]:
                redis_config = self.config.get('redis', {})
                self.redis_client = aioredis.from_url(
                    f"redis://{redis_config.get('host', 'localhost')}:"
                    f"{redis_config.get('port', 6379)}"
                )
                
                # Test Redis connection
                await self.redis_client.ping()
                logger.info("Redis cache connection established")
            
            # Start background tasks
            asyncio.create_task(self._cleanup_expired_entries())
            asyncio.create_task(self._collect_cache_metrics())
            
            # Warm cache if configured
            if self.warm_cache_on_startup:
                asyncio.create_task(self._warm_cache())
            
            self.is_initialized = True
            logger.info("Payment Gateway Cache initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Payment Gateway Cache: {e}")
            raise
    
    async def get(
        self, 
        key: str, 
        data_type: Optional[str] = None,
        default: Any = None
    ) -> Any:
        """Get value from cache"""
        try:
            self.cache_stats.total_requests += 1
            start_time = time.time()
            
            # Try L1 cache first (memory)
            if key in self.l1_cache:
                entry = self.l1_cache[key]
                
                if not entry.is_expired:
                    # Update access statistics
                    entry.last_accessed = datetime.now()
                    entry.access_count += 1
                    
                    # Move to end (LRU)
                    self.l1_cache.move_to_end(key)
                    
                    self.cache_stats.cache_hits += 1
                    self.cache_stats.l1_hits += 1
                    
                    logger.debug(f"L1 cache hit for key: {key}")
                    return entry.value
                else:
                    # Remove expired entry
                    del self.l1_cache[key]
            
            # Try L2 cache (Redis)
            if self.redis_client:
                redis_value = await self.redis_client.get(f"cache:{key}")
                if redis_value:
                    try:
                        # Deserialize value
                        cached_data = json.loads(redis_value.decode())
                        value = cached_data['value']
                        
                        # Check TTL
                        created_at = datetime.fromisoformat(cached_data['created_at'])
                        ttl = cached_data.get('ttl_seconds')
                        
                        if not ttl or (datetime.now() - created_at).total_seconds() <= ttl:
                            # Cache hit - store in L1 for faster access
                            await self._store_in_l1(key, value, data_type)
                            
                            self.cache_stats.cache_hits += 1
                            self.cache_stats.l2_hits += 1
                            
                            logger.debug(f"L2 cache hit for key: {key}")
                            return value
                        else:
                            # Expired - remove from Redis
                            await self.redis_client.delete(f"cache:{key}")
                    
                    except (json.JSONDecodeError, KeyError) as e:
                        logger.warning(f"Failed to deserialize cached value for {key}: {e}")
                        await self.redis_client.delete(f"cache:{key}")
            
            # Cache miss
            self.cache_stats.cache_misses += 1
            logger.debug(f"Cache miss for key: {key}")
            
            return default
            
        except Exception as e:
            logger.error(f"Failed to get from cache: {e}")
            return default
    
    async def set(
        self,
        key: str,
        value: Any,
        data_type: Optional[str] = None,
        ttl: Optional[int] = None
    ) -> bool:
        """Set value in cache"""
        try:
            # Determine TTL
            if ttl is None:
                ttl = self.ttl_configs.get(data_type, self.default_ttl)
            
            # Store in L1 cache (memory)
            await self._store_in_l1(key, value, data_type, ttl)
            
            # Store in L2 cache (Redis) if available
            if self.redis_client:
                cached_data = {
                    'value': value,
                    'created_at': datetime.now().isoformat(),
                    'ttl_seconds': ttl,
                    'data_type': data_type
                }
                
                await self.redis_client.set(
                    f"cache:{key}",
                    json.dumps(cached_data, default=str),
                    ex=ttl
                )
            
            logger.debug(f"Cached value for key: {key} (TTL: {ttl}s)")
            return True
            
        except Exception as e:
            logger.error(f"Failed to set cache: {e}")
            return False
    
    async def _store_in_l1(
        self,
        key: str,
        value: Any,
        data_type: Optional[str] = None,
        ttl: Optional[int] = None
    ):
        """Store value in L1 (memory) cache"""
        try:
            # Check if we need to evict entries
            if len(self.l1_cache) >= self.max_memory_size:
                # Remove least recently used entry
                oldest_key, _ = self.l1_cache.popitem(last=False)
                self.cache_stats.evictions += 1
                logger.debug(f"Evicted L1 cache entry: {oldest_key}")
            
            # Create cache entry
            entry = CacheEntry(
                key=key,
                value=value,
                created_at=datetime.now(),
                last_accessed=datetime.now(),
                access_count=1,
                ttl_seconds=ttl,
                cache_layer=CacheLayer.L1_MEMORY,
                metadata={'data_type': data_type}
            )
            
            self.l1_cache[key] = entry
            
        except Exception as e:
            logger.error(f"Failed to store in L1 cache: {e}")
    
    async def delete(self, key: str) -> bool:
        """Delete value from cache"""
        try:
            deleted = False
            
            # Remove from L1 cache
            if key in self.l1_cache:
                del self.l1_cache[key]
                deleted = True
            
            # Remove from L2 cache
            if self.redis_client:
                result = await self.redis_client.delete(f"cache:{key}")
                if result > 0:
                    deleted = True
            
            if deleted:
                self.cache_stats.invalidations += 1
                logger.debug(f"Deleted cache entry: {key}")
            
            return deleted
            
        except Exception as e:
            logger.error(f"Failed to delete from cache: {e}")
            return False
    
    async def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate cache entries matching pattern"""
        try:
            invalidated_count = 0
            
            # Invalidate from L1 cache
            keys_to_delete = [key for key in self.l1_cache.keys() if self._matches_pattern(key, pattern)]
            for key in keys_to_delete:
                del self.l1_cache[key]
                invalidated_count += 1
            
            # Invalidate from L2 cache (Redis)
            if self.redis_client:
                redis_keys = await self.redis_client.keys(f"cache:{pattern}")
                if redis_keys:
                    await self.redis_client.delete(*redis_keys)
                    invalidated_count += len(redis_keys)
            
            self.cache_stats.invalidations += invalidated_count
            logger.info(f"Invalidated {invalidated_count} cache entries matching pattern: {pattern}")
            
            return invalidated_count
            
        except Exception as e:
            logger.error(f"Failed to invalidate pattern: {e}")
            return 0
    
    def _matches_pattern(self, key: str, pattern: str) -> bool:
        """Check if key matches pattern (simple wildcard matching)"""
        if '*' not in pattern:
            return key == pattern
        
        # Simple wildcard matching
        parts = pattern.split('*')
        if not key.startswith(parts[0]):
            return False
        
        if len(parts) > 1 and not key.endswith(parts[-1]):
            return False
        
        return True
    
    async def cache_transaction_result(
        self,
        transaction_id: str,
        provider_id: str,
        result: Dict[str, Any]
    ) -> bool:
        """Cache transaction result"""
        key = self.key_patterns['transaction'].format(transaction_id=transaction_id)
        
        cache_data = {
            'transaction_id': transaction_id,
            'provider_id': provider_id,
            'result': result,
            'cached_at': datetime.now().isoformat()
        }
        
        return await self.set(key, cache_data, 'transaction')
    
    async def get_cached_transaction_result(self, transaction_id: str) -> Optional[Dict[str, Any]]:
        """Get cached transaction result"""
        key = self.key_patterns['transaction'].format(transaction_id=transaction_id)
        return await self.get(key, 'transaction')
    
    async def cache_provider_config(
        self,
        provider_id: str,
        config: Dict[str, Any]
    ) -> bool:
        """Cache provider configuration"""
        key = self.key_patterns['provider_config'].format(provider_id=provider_id)
        
        cache_data = {
            'provider_id': provider_id,
            'config': config,
            'cached_at': datetime.now().isoformat()
        }
        
        return await self.set(key, cache_data, 'provider_config')
    
    async def get_cached_provider_config(self, provider_id: str) -> Optional[Dict[str, Any]]:
        """Get cached provider configuration"""
        key = self.key_patterns['provider_config'].format(provider_id=provider_id)
        return await self.get(key, 'provider_config')
    
    async def cache_routing_decision(
        self,
        request_hash: str,
        decision: Dict[str, Any]
    ) -> bool:
        """Cache routing decision"""
        key = self.key_patterns['routing_decision'].format(hash=request_hash)
        
        cache_data = {
            'request_hash': request_hash,
            'decision': decision,
            'cached_at': datetime.now().isoformat()
        }
        
        return await self.set(key, cache_data, 'routing_decision')
    
    async def get_cached_routing_decision(self, request_hash: str) -> Optional[Dict[str, Any]]:
        """Get cached routing decision"""
        key = self.key_patterns['routing_decision'].format(hash=request_hash)
        return await self.get(key, 'routing_decision')
    
    async def cache_fraud_score(
        self,
        transaction_hash: str,
        fraud_score: float,
        risk_factors: List[str]
    ) -> bool:
        """Cache fraud detection score"""
        key = self.key_patterns['fraud_score'].format(transaction_hash=transaction_hash)
        
        cache_data = {
            'transaction_hash': transaction_hash,
            'fraud_score': fraud_score,
            'risk_factors': risk_factors,
            'cached_at': datetime.now().isoformat()
        }
        
        return await self.set(key, cache_data, 'fraud_score')
    
    async def get_cached_fraud_score(self, transaction_hash: str) -> Optional[Dict[str, Any]]:
        """Get cached fraud score"""
        key = self.key_patterns['fraud_score'].format(transaction_hash=transaction_hash)
        return await self.get(key, 'fraud_score')
    
    async def cache_exchange_rates(
        self,
        currency_pair: str,
        rates: Dict[str, float]
    ) -> bool:
        """Cache exchange rates"""
        key = self.key_patterns['exchange_rates'].format(currency_pair=currency_pair)
        
        cache_data = {
            'currency_pair': currency_pair,
            'rates': rates,
            'cached_at': datetime.now().isoformat()
        }
        
        return await self.set(key, cache_data, 'exchange_rates')
    
    async def get_cached_exchange_rates(self, currency_pair: str) -> Optional[Dict[str, Any]]:
        """Get cached exchange rates"""
        key = self.key_patterns['exchange_rates'].format(currency_pair=currency_pair)
        return await self.get(key, 'exchange_rates')
    
    async def cache_provider_health(
        self,
        provider_id: str,
        health_status: Dict[str, Any]
    ) -> bool:
        """Cache provider health status"""
        key = self.key_patterns['provider_health'].format(provider_id=provider_id)
        
        cache_data = {
            'provider_id': provider_id,
            'health_status': health_status,
            'cached_at': datetime.now().isoformat()
        }
        
        return await self.set(key, cache_data, 'provider_health')
    
    async def get_cached_provider_health(self, provider_id: str) -> Optional[Dict[str, Any]]:
        """Get cached provider health status"""
        key = self.key_patterns['provider_health'].format(provider_id=provider_id)
        return await self.get(key, 'provider_health')
    
    async def cache_analytics_data(
        self,
        metric: str,
        period: str,
        data: Dict[str, Any]
    ) -> bool:
        """Cache analytics data"""
        key = self.key_patterns['analytics'].format(metric=metric, period=period)
        
        cache_data = {
            'metric': metric,
            'period': period,
            'data': data,
            'cached_at': datetime.now().isoformat()
        }
        
        return await self.set(key, cache_data, 'analytics')
    
    async def get_cached_analytics_data(self, metric: str, period: str) -> Optional[Dict[str, Any]]:
        """Get cached analytics data"""
        key = self.key_patterns['analytics'].format(metric=metric, period=period)
        return await self.get(key, 'analytics')
    
    async def _cleanup_expired_entries(self):
        """Clean up expired cache entries"""
        while True:
            try:
                current_time = datetime.now()
                
                # Clean up L1 cache
                expired_keys = []
                for key, entry in self.l1_cache.items():
                    if entry.is_expired:
                        expired_keys.append(key)
                
                for key in expired_keys:
                    del self.l1_cache[key]
                    self.cache_stats.evictions += 1
                
                if expired_keys:
                    logger.debug(f"Cleaned up {len(expired_keys)} expired L1 cache entries")
                
                # Sleep for cleanup interval
                await asyncio.sleep(self.cleanup_interval)
                
            except Exception as e:
                logger.error(f"Error in cache cleanup: {e}")
                await asyncio.sleep(60)
    
    async def _collect_cache_metrics(self):
        """Collect cache performance metrics"""
        while True:
            try:
                # Log cache statistics periodically
                logger.info(f"Cache Stats - Hit Rate: {self.cache_stats.hit_rate:.2f}%, "
                           f"L1 Size: {len(self.l1_cache)}, "
                           f"Total Requests: {self.cache_stats.total_requests}")
                
                # Reset counters periodically to prevent overflow
                if self.cache_stats.total_requests > 1000000:
                    ratio = self.cache_stats.cache_hits / self.cache_stats.total_requests
                    self.cache_stats.total_requests = 1000
                    self.cache_stats.cache_hits = int(1000 * ratio)
                    self.cache_stats.cache_misses = 1000 - self.cache_stats.cache_hits
                
                await asyncio.sleep(300)  # Every 5 minutes
                
            except Exception as e:
                logger.error(f"Error in cache metrics collection: {e}")
                await asyncio.sleep(60)
    
    async def _warm_cache(self):
        """Warm up cache with frequently accessed data"""
        try:
            logger.info("Starting cache warming...")
            
            # Warm up provider configurations
            default_providers = ['stripe', 'paypal', 'wise', 'crypto']
            for provider_id in default_providers:
                # Simulate provider config (in real implementation, fetch from database)
                config = {
                    'provider_id': provider_id,
                    'api_endpoint': f'https://api.{provider_id}.com',
                    'timeout': 30000,
                    'retry_count': 3
                }
                await self.cache_provider_config(provider_id, config)
            
            # Warm up common exchange rates
            currency_pairs = ['USD-EUR', 'USD-GBP', 'EUR-GBP', 'USD-JPY']
            for pair in currency_pairs:
                # Simulate exchange rates
                rates = {
                    'rate': 1.0 + (hash(pair) % 100) / 1000,
                    'timestamp': datetime.now().isoformat()
                }
                await self.cache_exchange_rates(pair, rates)
            
            # Warm up analytics data
            metrics = ['transaction_volume', 'success_rate', 'revenue']
            periods = ['1h', '24h', '7d']
            for metric in metrics:
                for period in periods:
                    # Simulate analytics data
                    data = {
                        'value': hash(f"{metric}_{period}") % 10000,
                        'trend': 'up' if hash(metric) % 2 == 0 else 'down'
                    }
                    await self.cache_analytics_data(metric, period, data)
            
            logger.info("Cache warming completed")
            
        except Exception as e:
            logger.error(f"Error in cache warming: {e}")
    
    async def get_cache_statistics(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics"""
        try:
            # Calculate L1 cache statistics
            l1_size = len(self.l1_cache)
            l1_memory_usage = sum(
                len(str(entry.value)) for entry in self.l1_cache.values()
            )  # Rough estimate
            
            # Calculate data type distribution
            data_type_counts = defaultdict(int)
            for entry in self.l1_cache.values():
                data_type = entry.metadata.get('data_type', 'unknown')
                data_type_counts[data_type] += 1
            
            # Calculate average age
            if self.l1_cache:
                average_age = sum(entry.age_seconds for entry in self.l1_cache.values()) / len(self.l1_cache)
            else:
                average_age = 0
            
            return {
                'cache_stats': {
                    'total_requests': self.cache_stats.total_requests,
                    'cache_hits': self.cache_stats.cache_hits,
                    'cache_misses': self.cache_stats.cache_misses,
                    'hit_rate': self.cache_stats.hit_rate,
                    'miss_rate': self.cache_stats.miss_rate,
                    'evictions': self.cache_stats.evictions,
                    'invalidations': self.cache_stats.invalidations,
                    'l1_hits': self.cache_stats.l1_hits,
                    'l2_hits': self.cache_stats.l2_hits
                },
                'l1_cache': {
                    'size': l1_size,
                    'max_size': self.max_memory_size,
                    'utilization': (l1_size / self.max_memory_size) * 100,
                    'memory_usage_bytes': l1_memory_usage,
                    'average_age_seconds': average_age
                },
                'data_types': dict(data_type_counts),
                'configuration': {
                    'cache_type': self.cache_type.value,
                    'default_ttl': self.default_ttl,
                    'cleanup_interval': self.cleanup_interval
                },
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get cache statistics: {e}")
            return {'error': str(e)}
    
    async def optimize_cache(self) -> Dict[str, Any]:
        """Optimize cache performance"""
        try:
            optimization_results = {
                'actions_taken': [],
                'before_stats': await self.get_cache_statistics(),
                'recommendations': []
            }
            
            # Remove entries with very low access count
            low_access_threshold = 2
            low_access_keys = [
                key for key, entry in self.l1_cache.items()
                if entry.access_count <= low_access_threshold and entry.age_seconds > 3600
            ]
            
            for key in low_access_keys[:10]:  # Limit to 10 entries per optimization cycle
                del self.l1_cache[key]
                optimization_results['actions_taken'].append(f"Removed low-access entry: {key}")
            
            # Identify cache hotspots
            high_access_entries = sorted(
                self.l1_cache.items(),
                key=lambda x: x[1].access_count,
                reverse=True
            )[:10]
            
            if high_access_entries:
                most_accessed = high_access_entries[0][1]
                optimization_results['recommendations'].append(
                    f"Consider increasing TTL for frequently accessed data type: "
                    f"{most_accessed.metadata.get('data_type', 'unknown')}"
                )
            
            # Check hit rate and provide recommendations
            if self.cache_stats.hit_rate < 70:
                optimization_results['recommendations'].append(
                    "Low hit rate detected. Consider increasing cache size or TTL values."
                )
            
            if self.cache_stats.hit_rate > 95:
                optimization_results['recommendations'].append(
                    "Very high hit rate. Consider reducing cache size to free up memory."
                )
            
            optimization_results['after_stats'] = await self.get_cache_statistics()
            
            return optimization_results
            
        except Exception as e:
            logger.error(f"Failed to optimize cache: {e}")
            return {'error': str(e)}
    
    async def export_cache_data(self, format: str = "json") -> str:
        """Export cache data for analysis"""
        try:
            if format.lower() == "json":
                cache_export = {
                    'metadata': {
                        'exported_at': datetime.now().isoformat(),
                        'cache_type': self.cache_type.value,
                        'total_entries': len(self.l1_cache)
                    },
                    'entries': []
                }
                
                for key, entry in self.l1_cache.items():
                    cache_export['entries'].append({
                        'key': key,
                        'created_at': entry.created_at.isoformat(),
                        'last_accessed': entry.last_accessed.isoformat(),
                        'access_count': entry.access_count,
                        'ttl_seconds': entry.ttl_seconds,
                        'age_seconds': entry.age_seconds,
                        'data_type': entry.metadata.get('data_type', 'unknown')
                    })
                
                return json.dumps(cache_export, indent=2)
            
            else:
                raise ValueError(f"Unsupported export format: {format}")
                
        except Exception as e:
            logger.error(f"Failed to export cache data: {e}")
            raise
    
    async def clear_cache(self, confirm: bool = False) -> bool:
        """Clear all cache data"""
        try:
            if not confirm:
                raise ValueError("Cache clear operation requires confirmation")
            
            # Clear L1 cache
            l1_count = len(self.l1_cache)
            self.l1_cache.clear()
            
            # Clear L2 cache (Redis)
            l2_count = 0
            if self.redis_client:
                redis_keys = await self.redis_client.keys("cache:*")
                if redis_keys:
                    await self.redis_client.delete(*redis_keys)
                    l2_count = len(redis_keys)
            
            # Reset statistics
            self.cache_stats = CacheStats()
            
            logger.warning(f"Cache cleared - L1: {l1_count} entries, L2: {l2_count} entries")
            return True
            
        except Exception as e:
            logger.error(f"Failed to clear cache: {e}")
            return False
    
    async def close(self):
        """Close the cache system and cleanup resources"""
        try:
            if self.redis_client:
                await self.redis_client.close()
            
            logger.info("Payment Gateway Cache closed successfully")
            
        except Exception as e:
            logger.error(f"Failed to close Payment Gateway Cache: {e}")