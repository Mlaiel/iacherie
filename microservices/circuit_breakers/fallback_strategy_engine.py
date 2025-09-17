"""
Fallback Strategy Engine - Ainflue Platform
===========================================

Moteur stratégies fallback enterprise.
Multi-tier fallbacks + cache strategies + service mesh integration.

Author: Fahed Mlaiel (mlaiel@live.de)
Expert Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + Microservices + Audio + DevOps + IA Prompt Engineer

⚠️ PROPRIÉTÉ INTELLECTUELLE - FAHED MLAIEL
Cette architecture circuit breakers et tous ses patterns sont la propriété intellectuelle 
EXCLUSIVE de Fahed Mlaiel (mlaiel@live.de). Toute reproduction, modification, distribution 
ou vol d'idée/concept/code sans autorisation écrite PERSONNELLE est STRICTEMENT INTERDITE.

Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import time
import json
import logging
import hashlib
from typing import Dict, Any, Optional, List, Union, Callable
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
from collections import defaultdict, deque
import statistics

# Cache imports with graceful degradation
try:
    import redis
    import redis.asyncio as aioredis
    HAS_REDIS = True
except ImportError:
    HAS_REDIS = False
    redis = aioredis = None

try:
    import memcached
    HAS_MEMCACHED = True
except ImportError:
    HAS_MEMCACHED = False
    memcached = None

# HTTP client for service mesh integration
try:
    import aiohttp
    HAS_AIOHTTP = True
except ImportError:
    HAS_AIOHTTP = False
    aiohttp = None

logger = logging.getLogger(__name__)

class FallbackStrategyType(Enum):
    """Types of fallback strategies"""
    CACHE_BASED = "CACHE_BASED"
    SERVICE_MESH_ROUTING = "SERVICE_MESH_ROUTING"
    STATIC_RESPONSE = "STATIC_RESPONSE"
    ALTERNATE_SERVICE = "ALTERNATE_SERVICE"
    DEGRADED_FUNCTIONALITY = "DEGRADED_FUNCTIONALITY"
    QUEUE_DELAYED_PROCESSING = "QUEUE_DELAYED_PROCESSING"
    BACKUP_DATA_SOURCE = "BACKUP_DATA_SOURCE"
    DEFAULT_CONTENT = "DEFAULT_CONTENT"

class CacheType(Enum):
    """Supported cache types"""
    REDIS = "REDIS"
    MEMCACHED = "MEMCACHED"
    IN_MEMORY = "IN_MEMORY"
    HYBRID = "HYBRID"

class ServiceMeshType(Enum):
    """Supported service mesh types"""
    ISTIO = "ISTIO"
    LINKERD = "LINKERD"
    CONSUL_CONNECT = "CONSUL_CONNECT"
    ENVOY = "ENVOY"
    GENERIC = "GENERIC"

@dataclass
class FallbackQuality:
    """Quality metrics for fallback responses"""
    completeness: float  # 0.0 to 1.0
    freshness: float     # 0.0 to 1.0
    accuracy: float      # 0.0 to 1.0
    latency: float       # milliseconds
    confidence: float    # 0.0 to 1.0
    
    @property
    def overall_score(self) -> float:
        """Calculate overall quality score"""
        return (self.completeness * 0.3 + 
                self.freshness * 0.2 + 
                self.accuracy * 0.3 + 
                (1.0 - min(1.0, self.latency / 1000)) * 0.1 + 
                self.confidence * 0.1)

@dataclass
class FallbackStrategy:
    """Configuration for a fallback strategy"""
    strategy_type: FallbackStrategyType
    service_name: str
    priority: int = 1  # Lower number = higher priority
    enabled: bool = True
    configuration: Dict[str, Any] = field(default_factory=dict)
    quality_threshold: float = 0.5
    timeout_seconds: float = 5.0
    retry_count: int = 1
    cache_ttl_seconds: int = 300
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'strategy_type': self.strategy_type.value,
            'service_name': self.service_name,
            'priority': self.priority,
            'enabled': self.enabled,
            'configuration': self.configuration,
            'quality_threshold': self.quality_threshold,
            'timeout_seconds': self.timeout_seconds,
            'retry_count': self.retry_count,
            'cache_ttl_seconds': self.cache_ttl_seconds
        }

@dataclass
class FallbackConfig:
    """Configuration for fallback engine"""
    strategies: List[FallbackStrategy] = field(default_factory=list)
    enable_quality_evaluation: bool = True
    enable_learning: bool = True
    cache_config: Dict[str, Any] = field(default_factory=dict)
    service_mesh_config: Dict[str, Any] = field(default_factory=dict)
    default_timeout: float = 10.0
    max_concurrent_fallbacks: int = 5

class MultiTierCacheManager:
    """Multi-tier cache management with Redis, Memcached, and in-memory caches"""
    
    def __init__(self, cache_config: Dict[str, Any]):
        self.cache_config = cache_config
        self.caches = {}
        self.cache_hierarchy = [CacheType.IN_MEMORY, CacheType.REDIS, CacheType.MEMCACHED]
        self.in_memory_cache = {}
        self.cache_stats = defaultdict(lambda: {'hits': 0, 'misses': 0, 'sets': 0})
        
        # Initialize cache connections
        asyncio.create_task(self._initialize_caches())
    
    async def _initialize_caches(self):
        """Initialize cache connections"""
        try:
            # Redis connection
            if HAS_REDIS and self.cache_config.get('redis_enabled', False):
                redis_config = self.cache_config.get('redis', {})
                self.caches[CacheType.REDIS] = aioredis.Redis(
                    host=redis_config.get('host', 'localhost'),
                    port=redis_config.get('port', 6379),
                    db=redis_config.get('db', 0),
                    password=redis_config.get('password'),
                    socket_timeout=redis_config.get('timeout', 5)
                )
                logger.info("Redis cache initialized")
            
            # Memcached connection (simplified, as python-memcached doesn't have async support)
            if HAS_MEMCACHED and self.cache_config.get('memcached_enabled', False):
                # Note: This would need an async memcached client in production
                logger.info("Memcached cache initialization placeholder")
            
            # In-memory cache is always available
            self.caches[CacheType.IN_MEMORY] = self.in_memory_cache
            logger.info("In-memory cache initialized")
            
        except Exception as e:
            logger.error(f"Cache initialization failed: {str(e)}")
    
    async def get(self, key: str, default: Any = None) -> Any:
        """Get value from cache hierarchy"""
        for cache_type in self.cache_hierarchy:
            try:
                cache = self.caches.get(cache_type)
                if not cache:
                    continue
                
                if cache_type == CacheType.IN_MEMORY:
                    if key in cache:
                        entry = cache[key]
                        if entry['expires'] > datetime.now():
                            self.cache_stats[cache_type.value]['hits'] += 1
                            return entry['value']
                        else:
                            del cache[key]  # Remove expired entry
                
                elif cache_type == CacheType.REDIS:
                    value = await cache.get(key)
                    if value:
                        self.cache_stats[cache_type.value]['hits'] += 1
                        try:
                            return json.loads(value)
                        except json.JSONDecodeError:
                            return value.decode('utf-8')
                
                self.cache_stats[cache_type.value]['misses'] += 1
                
            except Exception as e:
                logger.debug(f"Cache get error for {cache_type.value}: {str(e)}")
                continue
        
        return default
    
    async def set(self, key: str, value: Any, ttl_seconds: int = 300):
        """Set value in all available caches"""
        for cache_type in self.cache_hierarchy:
            try:
                cache = self.caches.get(cache_type)
                if not cache:
                    continue
                
                if cache_type == CacheType.IN_MEMORY:
                    cache[key] = {
                        'value': value,
                        'expires': datetime.now() + timedelta(seconds=ttl_seconds)
                    }
                    self.cache_stats[cache_type.value]['sets'] += 1
                
                elif cache_type == CacheType.REDIS:
                    serialized_value = json.dumps(value) if not isinstance(value, str) else value
                    await cache.setex(key, ttl_seconds, serialized_value)
                    self.cache_stats[cache_type.value]['sets'] += 1
                
            except Exception as e:
                logger.debug(f"Cache set error for {cache_type.value}: {str(e)}")
                continue
    
    async def delete(self, key: str):
        """Delete key from all caches"""
        for cache_type in self.cache_hierarchy:
            try:
                cache = self.caches.get(cache_type)
                if not cache:
                    continue
                
                if cache_type == CacheType.IN_MEMORY:
                    cache.pop(key, None)
                elif cache_type == CacheType.REDIS:
                    await cache.delete(key)
                
            except Exception as e:
                logger.debug(f"Cache delete error for {cache_type.value}: {str(e)}")
                continue
    
    async def clear_expired(self):
        """Clear expired entries from in-memory cache"""
        current_time = datetime.now()
        expired_keys = []
        
        for key, entry in self.in_memory_cache.items():
            if entry['expires'] <= current_time:
                expired_keys.append(key)
        
        for key in expired_keys:
            del self.in_memory_cache[key]
        
        logger.debug(f"Cleared {len(expired_keys)} expired cache entries")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return dict(self.cache_stats)

class ServiceMeshConnector:
    """Connector for service mesh integration"""
    
    def __init__(self, service_mesh_config: Dict[str, Any]):
        self.service_mesh_config = service_mesh_config
        self.mesh_type = ServiceMeshType(service_mesh_config.get('type', 'GENERIC'))
        self.service_registry = {}
        self.health_cache = {}
    
    async def discover_alternate_services(self, service_name: str) -> List[str]:
        """Discover alternate service endpoints"""
        try:
            if self.mesh_type == ServiceMeshType.ISTIO:
                return await self._discover_istio_services(service_name)
            elif self.mesh_type == ServiceMeshType.LINKERD:
                return await self._discover_linkerd_services(service_name)
            elif self.mesh_type == ServiceMeshType.CONSUL_CONNECT:
                return await self._discover_consul_services(service_name)
            else:
                return await self._discover_generic_services(service_name)
                
        except Exception as e:
            logger.error(f"Service discovery failed: {str(e)}")
            return []
    
    async def _discover_istio_services(self, service_name: str) -> List[str]:
        """Discover services through Istio service mesh"""
        # This would integrate with Istio's service discovery API
        # For now, return placeholder endpoints
        return [
            f"{service_name}-v1.default.svc.cluster.local",
            f"{service_name}-v2.default.svc.cluster.local",
            f"{service_name}-canary.default.svc.cluster.local"
        ]
    
    async def _discover_linkerd_services(self, service_name: str) -> List[str]:
        """Discover services through Linkerd service mesh"""
        return [f"{service_name}.linkerd.svc.cluster.local"]
    
    async def _discover_consul_services(self, service_name: str) -> List[str]:
        """Discover services through Consul Connect"""
        return [f"{service_name}.service.consul"]
    
    async def _discover_generic_services(self, service_name: str) -> List[str]:
        """Generic service discovery"""
        # Use configured service registry or DNS
        configured_services = self.service_mesh_config.get('services', {})
        return configured_services.get(service_name, [])
    
    async def check_service_health(self, service_endpoint: str) -> bool:
        """Check if service endpoint is healthy"""
        # Check cache first
        if service_endpoint in self.health_cache:
            cache_entry = self.health_cache[service_endpoint]
            if cache_entry['timestamp'] > datetime.now() - timedelta(seconds=30):
                return cache_entry['healthy']
        
        # Perform health check
        try:
            if HAS_AIOHTTP:
                async with aiohttp.ClientSession() as session:
                    health_endpoint = f"http://{service_endpoint}/health"
                    timeout = aiohttp.ClientTimeout(total=3)
                    
                    async with session.get(health_endpoint, timeout=timeout) as response:
                        healthy = response.status == 200
                        
                        # Cache result
                        self.health_cache[service_endpoint] = {
                            'healthy': healthy,
                            'timestamp': datetime.now()
                        }
                        
                        return healthy
            else:
                # Fallback: assume healthy if no HTTP client
                return True
                
        except Exception as e:
            logger.debug(f"Health check failed for {service_endpoint}: {str(e)}")
            
            # Cache negative result
            self.health_cache[service_endpoint] = {
                'healthy': False,
                'timestamp': datetime.now()
            }
            
            return False
    
    async def route_request(self, service_name: str, request_data: Dict[str, Any]) -> Optional[str]:
        """Route request to healthy service instance"""
        alternate_services = await self.discover_alternate_services(service_name)
        
        for service_endpoint in alternate_services:
            if await self.check_service_health(service_endpoint):
                return service_endpoint
        
        return None

class FallbackRegistry:
    """Registry for managing fallback strategies"""
    
    def __init__(self):
        self.strategies: Dict[str, List[FallbackStrategy]] = defaultdict(list)
        self.execution_history = deque(maxlen=1000)
        self.quality_metrics = defaultdict(list)
        self.registry_lock = asyncio.Lock()
    
    async def register_strategy(self, strategy: FallbackStrategy):
        """Register a fallback strategy"""
        async with self.registry_lock:
            service_strategies = self.strategies[strategy.service_name]
            
            # Remove existing strategy of same type
            service_strategies[:] = [s for s in service_strategies 
                                   if s.strategy_type != strategy.strategy_type]
            
            # Add new strategy
            service_strategies.append(strategy)
            
            # Sort by priority (lower number = higher priority)
            service_strategies.sort(key=lambda x: x.priority)
            
            logger.info(f"Registered fallback strategy {strategy.strategy_type.value} for {strategy.service_name}")
    
    async def get_strategies(self, service_name: str) -> List[FallbackStrategy]:
        """Get strategies for service"""
        return [s for s in self.strategies.get(service_name, []) if s.enabled]
    
    async def record_execution(self, service_name: str, strategy_type: FallbackStrategyType, 
                             quality: FallbackQuality, success: bool):
        """Record strategy execution results"""
        execution_record = {
            'timestamp': datetime.now(),
            'service_name': service_name,
            'strategy_type': strategy_type.value,
            'quality': quality,
            'success': success
        }
        
        self.execution_history.append(execution_record)
        self.quality_metrics[f"{service_name}:{strategy_type.value}"].append(quality.overall_score)
        
        # Keep only recent quality metrics
        if len(self.quality_metrics[f"{service_name}:{strategy_type.value}"]) > 100:
            self.quality_metrics[f"{service_name}:{strategy_type.value}"] = \
                self.quality_metrics[f"{service_name}:{strategy_type.value}"][-100:]
    
    async def get_strategy_performance(self, service_name: str, 
                                     strategy_type: FallbackStrategyType) -> Dict[str, Any]:
        """Get performance metrics for strategy"""
        key = f"{service_name}:{strategy_type.value}"
        quality_scores = self.quality_metrics.get(key, [])
        
        if not quality_scores:
            return {'average_quality': 0.0, 'execution_count': 0}
        
        return {
            'average_quality': statistics.mean(quality_scores),
            'min_quality': min(quality_scores),
            'max_quality': max(quality_scores),
            'execution_count': len(quality_scores),
            'recent_trend': statistics.mean(quality_scores[-10:]) if len(quality_scores) >= 10 else 0.0
        }

class FallbackStrategyEngine:
    """
    Moteur stratégies fallback enterprise.
    Multi-tier fallbacks + cache strategies + service mesh integration.
    """
    
    def __init__(self, strategy_config: FallbackConfig):
        self.strategy_config = strategy_config
        self.cache_manager = MultiTierCacheManager(strategy_config.cache_config)
        self.service_mesh = ServiceMeshConnector(strategy_config.service_mesh_config)
        self.fallback_registry = FallbackRegistry()
        
        # Performance tracking
        self.execution_metrics = defaultdict(lambda: {
            'total_executions': 0,
            'successful_executions': 0,
            'average_latency': 0.0,
            'last_execution': None
        })
        
        # Concurrent execution control
        self.concurrent_fallbacks = 0
        self.execution_semaphore = asyncio.Semaphore(strategy_config.max_concurrent_fallbacks)
        
        logger.info("Fallback strategy engine initialized")
    
    async def initialize(self):
        """Initialize the fallback engine"""
        # Register configured strategies
        for strategy in self.strategy_config.strategies:
            await self.fallback_registry.register_strategy(strategy)
        
        # Start background tasks
        asyncio.create_task(self._periodic_cache_cleanup())
    
    async def execute_fallback_strategy(self, strategy_type: str, context: Dict[str, Any]) -> Any:
        """
        Exécution stratégie fallback intelligente.
        
        Strategies:
        - Cache-based fallback (Redis/Memcached)
        - Service mesh routing fallback
        - Static response fallback
        - Alternate service endpoint fallback
        - Degraded functionality fallback
        - Queue-based delayed processing
        """
        service_name = context.get('service_name', 'unknown')
        start_time = time.time()
        
        async with self.execution_semaphore:
            try:
                # Get fallback strategies for service
                strategies = await self.fallback_registry.get_strategies(service_name)
                
                if not strategies:
                    return await self._execute_default_fallback(context)
                
                # Try strategies in priority order
                for strategy in strategies:
                    if strategy_type != "auto" and strategy.strategy_type.value.lower() != strategy_type.lower():
                        continue
                    
                    try:
                        result = await self._execute_single_strategy(strategy, context)
                        
                        if result is not None:
                            # Evaluate quality
                            quality = await self._evaluate_fallback_quality(result, context, strategy)
                            
                            # Record execution
                            execution_time = (time.time() - start_time) * 1000
                            await self._record_execution_metrics(service_name, strategy.strategy_type, 
                                                               quality, True, execution_time)
                            
                            return result
                    
                    except Exception as e:
                        logger.warning(f"Fallback strategy {strategy.strategy_type.value} failed: {str(e)}")
                        continue
                
                # All strategies failed, use default
                return await self._execute_default_fallback(context)
                
            except Exception as e:
                execution_time = (time.time() - start_time) * 1000
                logger.error(f"Fallback execution failed: {str(e)}")
                
                # Record failure
                await self._record_execution_metrics(service_name, FallbackStrategyType.STATIC_RESPONSE, 
                                                   None, False, execution_time)
                
                return await self._execute_default_fallback(context)
    
    async def _execute_single_strategy(self, strategy: FallbackStrategy, context: Dict[str, Any]) -> Any:
        """Execute a single fallback strategy"""
        strategy_handlers = {
            FallbackStrategyType.CACHE_BASED: self._execute_cache_fallback,
            FallbackStrategyType.SERVICE_MESH_ROUTING: self._execute_service_mesh_fallback,
            FallbackStrategyType.STATIC_RESPONSE: self._execute_static_fallback,
            FallbackStrategyType.ALTERNATE_SERVICE: self._execute_alternate_service_fallback,
            FallbackStrategyType.DEGRADED_FUNCTIONALITY: self._execute_degraded_fallback,
            FallbackStrategyType.QUEUE_DELAYED_PROCESSING: self._execute_queue_fallback,
            FallbackStrategyType.BACKUP_DATA_SOURCE: self._execute_backup_data_fallback,
            FallbackStrategyType.DEFAULT_CONTENT: self._execute_default_content_fallback
        }
        
        handler = strategy_handlers.get(strategy.strategy_type, self._execute_static_fallback)
        
        # Execute with timeout
        try:
            return await asyncio.wait_for(
                handler(strategy, context),
                timeout=strategy.timeout_seconds
            )
        except asyncio.TimeoutError:
            logger.warning(f"Fallback strategy {strategy.strategy_type.value} timed out")
            return None
    
    async def _execute_cache_fallback(self, strategy: FallbackStrategy, context: Dict[str, Any]) -> Any:
        """Execute cache-based fallback"""
        cache_key = context.get('cache_key') or f"{strategy.service_name}:{context.get('request_id', 'default')}"
        
        # Try to get from cache
        cached_result = await self.cache_manager.get(cache_key)
        
        if cached_result:
            logger.info(f"Cache fallback successful for {strategy.service_name}")
            return {
                'status': 'success',
                'source': 'cache',
                'data': cached_result,
                'fallback': True,
                'strategy': 'cache_based'
            }
        
        # Cache miss - try to use stale data
        stale_key = f"{cache_key}:stale"
        stale_result = await self.cache_manager.get(stale_key)
        
        if stale_result:
            logger.info(f"Stale cache fallback for {strategy.service_name}")
            return {
                'status': 'success',
                'source': 'stale_cache',
                'data': stale_result,
                'fallback': True,
                'strategy': 'cache_based',
                'warning': 'Data may be outdated'
            }
        
        return None
    
    async def _execute_service_mesh_fallback(self, strategy: FallbackStrategy, context: Dict[str, Any]) -> Any:
        """Execute service mesh routing fallback"""
        service_name = strategy.service_name
        
        # Find healthy alternate service
        alternate_endpoint = await self.service_mesh.route_request(service_name, context)
        
        if not alternate_endpoint:
            return None
        
        # Make request to alternate service
        if HAS_AIOHTTP:
            try:
                async with aiohttp.ClientSession() as session:
                    request_data = context.get('request_data', {})
                    timeout = aiohttp.ClientTimeout(total=strategy.timeout_seconds)
                    
                    async with session.post(
                        f"http://{alternate_endpoint}/api/{context.get('endpoint', '')}",
                        json=request_data,
                        timeout=timeout
                    ) as response:
                        if response.status == 200:
                            result_data = await response.json()
                            return {
                                'status': 'success',
                                'source': 'service_mesh',
                                'data': result_data,
                                'fallback': True,
                                'strategy': 'service_mesh_routing',
                                'alternate_endpoint': alternate_endpoint
                            }
            except Exception as e:
                logger.debug(f"Service mesh fallback failed: {str(e)}")
        
        return None
    
    async def _execute_static_fallback(self, strategy: FallbackStrategy, context: Dict[str, Any]) -> Any:
        """Execute static response fallback"""
        static_response = strategy.configuration.get('static_response', {
            'status': 'degraded',
            'message': 'Service temporarily unavailable',
            'data': None
        })
        
        return {
            'status': 'success',
            'source': 'static',
            'data': static_response,
            'fallback': True,
            'strategy': 'static_response'
        }
    
    async def _execute_alternate_service_fallback(self, strategy: FallbackStrategy, context: Dict[str, Any]) -> Any:
        """Execute alternate service endpoint fallback"""
        alternate_endpoints = strategy.configuration.get('alternate_endpoints', [])
        
        for endpoint in alternate_endpoints:
            if HAS_AIOHTTP:
                try:
                    async with aiohttp.ClientSession() as session:
                        request_data = context.get('request_data', {})
                        timeout = aiohttp.ClientTimeout(total=strategy.timeout_seconds)
                        
                        async with session.post(endpoint, json=request_data, timeout=timeout) as response:
                            if response.status == 200:
                                result_data = await response.json()
                                return {
                                    'status': 'success',
                                    'source': 'alternate_service',
                                    'data': result_data,
                                    'fallback': True,
                                    'strategy': 'alternate_service',
                                    'endpoint': endpoint
                                }
                except Exception as e:
                    logger.debug(f"Alternate service {endpoint} failed: {str(e)}")
                    continue
        
        return None
    
    async def _execute_degraded_fallback(self, strategy: FallbackStrategy, context: Dict[str, Any]) -> Any:
        """Execute degraded functionality fallback"""
        degraded_response = strategy.configuration.get('degraded_response', {})
        
        # Provide limited functionality
        base_response = {
            'status': 'degraded',
            'message': 'Limited functionality available',
            'fallback': True,
            'strategy': 'degraded_functionality'
        }
        
        base_response.update(degraded_response)
        
        return {
            'status': 'success',
            'source': 'degraded',
            'data': base_response,
            'fallback': True,
            'strategy': 'degraded_functionality'
        }
    
    async def _execute_queue_fallback(self, strategy: FallbackStrategy, context: Dict[str, Any]) -> Any:
        """Execute queue-based delayed processing fallback"""
        # Queue request for later processing
        queue_config = strategy.configuration.get('queue_config', {})
        
        # Simulate queuing (in production, this would use actual message queue)
        request_id = context.get('request_id', f"req_{int(time.time())}")
        
        return {
            'status': 'queued',
            'source': 'queue',
            'data': {
                'message': 'Request queued for processing',
                'request_id': request_id,
                'estimated_delay': queue_config.get('estimated_delay', 60),
                'queue_name': queue_config.get('queue_name', 'default')
            },
            'fallback': True,
            'strategy': 'queue_delayed_processing'
        }
    
    async def _execute_backup_data_fallback(self, strategy: FallbackStrategy, context: Dict[str, Any]) -> Any:
        """Execute backup data source fallback"""
        backup_config = strategy.configuration.get('backup_config', {})
        backup_type = backup_config.get('type', 'file')
        
        if backup_type == 'file':
            # Load from backup file
            backup_file = backup_config.get('file_path', '/tmp/backup_data.json')
            try:
                with open(backup_file, 'r') as f:
                    backup_data = json.load(f)
                
                return {
                    'status': 'success',
                    'source': 'backup_file',
                    'data': backup_data,
                    'fallback': True,
                    'strategy': 'backup_data_source'
                }
            except Exception as e:
                logger.debug(f"Backup file read failed: {str(e)}")
        
        return None
    
    async def _execute_default_content_fallback(self, strategy: FallbackStrategy, context: Dict[str, Any]) -> Any:
        """Execute default content fallback"""
        default_content = strategy.configuration.get('default_content', {
            'title': 'Content Unavailable',
            'message': 'The requested content is temporarily unavailable',
            'type': 'error'
        })
        
        return {
            'status': 'success',
            'source': 'default_content',
            'data': default_content,
            'fallback': True,
            'strategy': 'default_content'
        }
    
    async def _execute_default_fallback(self, context: Dict[str, Any]) -> Any:
        """Execute default fallback when all strategies fail"""
        return {
            'status': 'error',
            'source': 'default',
            'data': {
                'message': 'All fallback strategies exhausted',
                'service': context.get('service_name', 'unknown'),
                'timestamp': datetime.now().isoformat()
            },
            'fallback': True,
            'strategy': 'default'
        }
    
    async def register_fallback_strategy(self, service: str, strategy: FallbackStrategy) -> bool:
        """Enregistrement stratégie fallback per service"""
        try:
            strategy.service_name = service
            await self.fallback_registry.register_strategy(strategy)
            return True
        except Exception as e:
            logger.error(f"Failed to register fallback strategy: {str(e)}")
            return False
    
    async def evaluate_fallback_quality(self, fallback_result: Any, expected_result: Any) -> float:
        """Évaluation qualité fallback avec ML scoring"""
        if not fallback_result:
            return 0.0
        
        try:
            # Extract quality metrics
            completeness = await self._calculate_completeness(fallback_result, expected_result)
            freshness = await self._calculate_freshness(fallback_result)
            accuracy = await self._calculate_accuracy(fallback_result, expected_result)
            latency = fallback_result.get('latency', 0)
            confidence = fallback_result.get('confidence', 0.5)
            
            quality = FallbackQuality(
                completeness=completeness,
                freshness=freshness,
                accuracy=accuracy,
                latency=latency,
                confidence=confidence
            )
            
            return quality.overall_score
            
        except Exception as e:
            logger.debug(f"Quality evaluation failed: {str(e)}")
            return 0.5  # Default score
    
    async def _evaluate_fallback_quality(self, fallback_result: Any, context: Dict[str, Any], 
                                       strategy: FallbackStrategy) -> FallbackQuality:
        """Evaluate the quality of fallback result"""
        # Simple heuristic-based quality evaluation
        completeness = 0.8 if fallback_result.get('data') else 0.2
        freshness = 1.0 if strategy.strategy_type == FallbackStrategyType.STATIC_RESPONSE else 0.5
        accuracy = 0.7  # Assume reasonable accuracy for fallbacks
        latency = context.get('execution_time', 100)  # milliseconds
        confidence = 0.6  # Default confidence
        
        return FallbackQuality(
            completeness=completeness,
            freshness=freshness,
            accuracy=accuracy,
            latency=latency,
            confidence=confidence
        )
    
    async def _calculate_completeness(self, fallback_result: Any, expected_result: Any) -> float:
        """Calculate completeness score"""
        if not fallback_result:
            return 0.0
        
        if not expected_result:
            return 0.8  # Assume reasonable completeness without reference
        
        # Compare keys/fields
        fallback_keys = set(str(fallback_result).split())
        expected_keys = set(str(expected_result).split())
        
        if not expected_keys:
            return 0.8
        
        overlap = len(fallback_keys & expected_keys)
        return min(1.0, overlap / len(expected_keys))
    
    async def _calculate_freshness(self, fallback_result: Any) -> float:
        """Calculate freshness score"""
        source = fallback_result.get('source', 'unknown')
        
        freshness_scores = {
            'cache': 0.7,
            'stale_cache': 0.3,
            'service_mesh': 0.9,
            'alternate_service': 0.8,
            'static': 1.0,  # Static data doesn't age
            'degraded': 0.5,
            'queue': 0.4,
            'backup_file': 0.2,
            'default_content': 1.0
        }
        
        return freshness_scores.get(source, 0.5)
    
    async def _calculate_accuracy(self, fallback_result: Any, expected_result: Any) -> float:
        """Calculate accuracy score"""
        # This would ideally use ML models to compare semantic similarity
        # For now, use simple heuristics
        
        if not expected_result:
            return 0.7  # Assume reasonable accuracy without reference
        
        # Simple string similarity (very basic)
        fallback_str = str(fallback_result).lower()
        expected_str = str(expected_result).lower()
        
        if fallback_str == expected_str:
            return 1.0
        
        # Calculate simple character overlap
        common_chars = set(fallback_str) & set(expected_str)
        total_chars = set(fallback_str) | set(expected_str)
        
        if not total_chars:
            return 0.0
        
        return len(common_chars) / len(total_chars)
    
    async def optimize_fallback_selection(self, historical_data: Dict[str, Any]) -> Dict[str, Any]:
        """Optimisation sélection fallback basée sur historique"""
        optimization_results = {}
        
        for service_name in historical_data.get('services', []):
            service_strategies = await self.fallback_registry.get_strategies(service_name)
            strategy_performance = {}
            
            for strategy in service_strategies:
                performance = await self.fallback_registry.get_strategy_performance(
                    service_name, strategy.strategy_type
                )
                strategy_performance[strategy.strategy_type.value] = performance
            
            # Find best performing strategy
            best_strategy = max(strategy_performance.items(), 
                              key=lambda x: x[1].get('average_quality', 0))
            
            optimization_results[service_name] = {
                'recommended_strategy': best_strategy[0],
                'strategy_performance': strategy_performance,
                'optimization_confidence': best_strategy[1].get('average_quality', 0)
            }
        
        return optimization_results
    
    async def _record_execution_metrics(self, service_name: str, strategy_type: FallbackStrategyType,
                                      quality: Optional[FallbackQuality], success: bool, 
                                      execution_time: float):
        """Record execution metrics"""
        key = f"{service_name}:{strategy_type.value}"
        metrics = self.execution_metrics[key]
        
        metrics['total_executions'] += 1
        if success:
            metrics['successful_executions'] += 1
        
        # Update average latency
        total_latency = metrics['average_latency'] * (metrics['total_executions'] - 1)
        metrics['average_latency'] = (total_latency + execution_time) / metrics['total_executions']
        metrics['last_execution'] = datetime.now()
        
        # Record in registry
        if quality:
            await self.fallback_registry.record_execution(service_name, strategy_type, quality, success)
    
    async def _periodic_cache_cleanup(self):
        """Periodic cache cleanup task"""
        while True:
            try:
                await asyncio.sleep(300)  # Run every 5 minutes
                await self.cache_manager.clear_expired()
            except Exception as e:
                logger.error(f"Cache cleanup failed: {str(e)}")
                await asyncio.sleep(300)
    
    async def get_engine_status(self) -> Dict[str, Any]:
        """Get fallback engine status and metrics"""
        cache_stats = self.cache_manager.get_cache_stats()
        
        total_executions = sum(metrics['total_executions'] for metrics in self.execution_metrics.values())
        successful_executions = sum(metrics['successful_executions'] for metrics in self.execution_metrics.values())
        
        return {
            'total_strategies': sum(len(strategies) for strategies in self.fallback_registry.strategies.values()),
            'total_executions': total_executions,
            'successful_executions': successful_executions,
            'success_rate': (successful_executions / total_executions * 100) if total_executions > 0 else 0,
            'concurrent_fallbacks': self.concurrent_fallbacks,
            'cache_stats': cache_stats,
            'execution_metrics': dict(self.execution_metrics),
            'last_updated': datetime.now().isoformat()
        }

# Export main classes
__all__ = [
    'FallbackStrategyEngine',
    'FallbackConfig',
    'FallbackStrategy',
    'FallbackStrategyType',
    'FallbackQuality',
    'MultiTierCacheManager',
    'ServiceMeshConnector',
    'FallbackRegistry',
    'CacheType',
    'ServiceMeshType'
]