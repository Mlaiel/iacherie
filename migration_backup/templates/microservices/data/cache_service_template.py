"""
⚠️ AVERTISSEMENT LÉGAL OBLIGATOIRE:
==========================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques

Cache Service Template for Ainflue Creator Economy Platform
Enterprise distributed cache service with multi-provider, intelligent eviction and performance optimization
"""

import asyncio
import json
import time
import hashlib
import pickle
import gzip
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Set
from dataclasses import dataclass, field
from enum import Enum
import secrets

from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel, validator
import redis.asyncio as redis
import aiomcache
import asyncio_mqtt
from redis.asyncio import Redis
import logging
from prometheus_client import Counter, Histogram, Gauge


class CacheProvider(str, Enum):
    REDIS = "redis"
    MEMCACHED = "memcached"
    MEMORY = "memory"
    HYBRID = "hybrid"


class EvictionPolicy(str, Enum):
    LRU = "lru"  # Least Recently Used
    LFU = "lfu"  # Least Frequently Used
    TTL = "ttl"  # Time To Live
    RANDOM = "random"
    FIFO = "fifo"  # First In First Out


class CompressionType(str, Enum):
    NONE = "none"
    GZIP = "gzip"
    LZ4 = "lz4"
    SNAPPY = "snappy"


class CacheEventType(str, Enum):
    HIT = "hit"
    MISS = "miss"
    SET = "set"
    DELETE = "delete"
    EXPIRE = "expire"
    EVICT = "evict"


@dataclass
class CacheConfig:
    """Configuration du service de cache"""
    # Provider settings
    primary_provider: CacheProvider = CacheProvider.REDIS
    fallback_provider: CacheProvider = CacheProvider.MEMORY
    
    # Redis configuration
    redis_url: str = "redis://localhost:6379/0"
    redis_cluster_urls: List[str] = field(default_factory=list)
    redis_sentinel_hosts: List[str] = field(default_factory=list)
    
    # Memcached configuration
    memcached_hosts: List[str] = field(default_factory=lambda: ["localhost:11211"])
    
    # Memory cache configuration
    memory_max_size: int = 1000000  # 1M entries
    memory_max_memory_mb: int = 512  # 512MB
    
    # Performance settings
    default_ttl_seconds: int = 3600  # 1 hour
    max_ttl_seconds: int = 86400 * 7  # 7 days
    compression_threshold: int = 1024  # Compress if > 1KB
    compression_type: CompressionType = CompressionType.GZIP
    
    # Eviction and cleanup
    eviction_policy: EvictionPolicy = EvictionPolicy.LRU
    cleanup_interval_seconds: int = 300  # 5 minutes
    max_key_size: int = 250
    max_value_size: int = 1024 * 1024  # 1MB
    
    # High availability
    enable_replication: bool = True
    enable_clustering: bool = False
    health_check_interval: int = 30
    
    # Advanced features
    enable_cache_warming: bool = True
    enable_stats_collection: bool = True
    enable_invalidation_events: bool = True
    enable_distributed_locks: bool = True


class CacheKey(BaseModel):
    """Clé de cache structurée"""
    namespace: str = "default"
    category: str = "general"
    key: str
    version: str = "v1"
    
    def generate_full_key(self) -> str:
        """Génère la clé complète"""
        return f"{self.namespace}:{self.category}:{self.version}:{self.key}"


class CacheRequest(BaseModel):
    """Demande de cache"""
    key: Union[str, CacheKey]
    value: Optional[Any] = None
    ttl_seconds: Optional[int] = None
    compress: bool = False
    tags: List[str] = []
    metadata: Dict[str, Any] = {}


class CacheResponse(BaseModel):
    """Réponse de cache"""
    key: str
    value: Optional[Any] = None
    hit: bool = False
    ttl_remaining: Optional[int] = None
    compressed: bool = False
    metadata: Dict[str, Any] = {}
    cached_at: Optional[datetime] = None
    accessed_at: datetime = None


class CacheStats(BaseModel):
    """Statistiques de cache"""
    total_keys: int = 0
    total_memory_bytes: int = 0
    hit_count: int = 0
    miss_count: int = 0
    set_count: int = 0
    delete_count: int = 0
    eviction_count: int = 0
    hit_ratio: float = 0.0
    memory_usage_ratio: float = 0.0
    provider_stats: Dict[str, Any] = {}


class CacheServiceTemplate:
    """
    Template de service de cache enterprise pour Ainflue
    
    Fonctionnalités:
    - Multi-provider (Redis, Memcached, Memory)
    - Compression intelligente
    - Éviction policies avancées
    - High availability avec clustering
    - Cache warming et pre-loading
    - Distributed locking
    - Real-time monitoring
    - Tag-based invalidation
    - Performance optimization
    """
    
    def __init__(self, config: CacheConfig = None):
        self.config = config or CacheConfig()
        self.app = FastAPI(
            title="Ainflue Cache Service",
            description="Enterprise distributed cache service",
            version="1.0.0"
        )
        
        # Cache providers
        self.redis_client: Optional[Redis] = None
        self.memcached_client: Optional[aiomcache.Client] = None
        self.memory_cache: Dict[str, Dict[str, Any]] = {}
        self.memory_access_times: Dict[str, float] = {}
        self.memory_access_counts: Dict[str, int] = {}
        
        # Stats tracking
        self.stats = CacheStats()
        
        # Distributed locks
        self.locks: Dict[str, asyncio.Lock] = {}
        
        # Event publishing
        self.event_subscribers: Set[str] = set()
        
        # Métriques Prometheus
        self.cache_operations = Counter('cache_operations_total', ['provider', 'operation', 'status'])
        self.cache_hit_ratio = Gauge('cache_hit_ratio', ['provider'])
        self.cache_memory_usage = Gauge('cache_memory_usage_bytes', ['provider'])
        self.cache_response_time = Histogram('cache_response_time_seconds', ['provider', 'operation'])
        self.cache_key_count = Gauge('cache_key_count_total', ['provider'])
        
        # Setup
        asyncio.create_task(self._initialize_providers())
        self._setup_routes()
        self._start_background_tasks()
        
        # Logger
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    async def _initialize_providers(self):
        """Initialisation des providers de cache"""
        try:
            # Redis initialization
            if self.config.primary_provider == CacheProvider.REDIS or self.config.fallback_provider == CacheProvider.REDIS:
                await self._initialize_redis()
            
            # Memcached initialization
            if self.config.primary_provider == CacheProvider.MEMCACHED or self.config.fallback_provider == CacheProvider.MEMCACHED:
                await self._initialize_memcached()
            
            self.logger.info("Cache providers initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize cache providers: {str(e)}")
            raise

    async def _initialize_redis(self):
        """Initialisation Redis"""
        try:
            if self.config.redis_cluster_urls:
                # Redis Cluster
                from redis.asyncio.cluster import RedisCluster
                self.redis_client = RedisCluster.from_url(
                    self.config.redis_cluster_urls[0],
                    decode_responses=True
                )
            elif self.config.redis_sentinel_hosts:
                # Redis Sentinel
                from redis.asyncio.sentinel import Sentinel
                sentinel = Sentinel([(host.split(':')[0], int(host.split(':')[1])) 
                                   for host in self.config.redis_sentinel_hosts])
                self.redis_client = sentinel.master_for('mymaster')
            else:
                # Single Redis instance
                self.redis_client = Redis.from_url(
                    self.config.redis_url,
                    decode_responses=True,
                    encoding='utf-8'
                )
            
            # Test connection
            await self.redis_client.ping()
            self.logger.info("Redis client initialized")
            
        except Exception as e:
            self.logger.error(f"Redis initialization failed: {str(e)}")
            if self.config.primary_provider == CacheProvider.REDIS:
                raise

    async def _initialize_memcached(self):
        """Initialisation Memcached"""
        try:
            host, port = self.config.memcached_hosts[0].split(':')
            self.memcached_client = aiomcache.Client(host, int(port))
            
            # Test connection
            await self.memcached_client.version()
            self.logger.info("Memcached client initialized")
            
        except Exception as e:
            self.logger.error(f"Memcached initialization failed: {str(e)}")
            if self.config.primary_provider == CacheProvider.MEMCACHED:
                raise

    def _start_background_tasks(self):
        """Démarre les tâches en arrière-plan"""
        # Cleanup task
        asyncio.create_task(self._cleanup_loop())
        
        # Stats collection task
        if self.config.enable_stats_collection:
            asyncio.create_task(self._stats_collection_loop())
        
        # Health monitoring
        asyncio.create_task(self._health_monitoring_loop())

    def _setup_routes(self):
        """Configuration des routes du service"""
        
        @self.app.post("/cache/set", response_model=Dict[str, Any])
        async def set_cache_value(request: CacheRequest):
            """Stocker une valeur dans le cache"""
            with self.cache_response_time.labels(provider=self.config.primary_provider.value, operation='set').time():
                try:
                    key = self._normalize_key(request.key)
                    
                    # Validation
                    if len(key) > self.config.max_key_size:
                        raise HTTPException(status_code=400, detail="Key too large")
                    
                    # Sérialisation et compression
                    serialized_value = await self._serialize_value(request.value, request.compress)
                    
                    if len(serialized_value) > self.config.max_value_size:
                        raise HTTPException(status_code=400, detail="Value too large")
                    
                    # TTL
                    ttl = request.ttl_seconds or self.config.default_ttl_seconds
                    ttl = min(ttl, self.config.max_ttl_seconds)
                    
                    # Stocker dans le cache
                    success = await self._set_value(key, serialized_value, ttl, request.tags, request.metadata)
                    
                    if success:
                        self.cache_operations.labels(
                            provider=self.config.primary_provider.value,
                            operation='set',
                            status='success'
                        ).inc()
                        self.stats.set_count += 1
                        
                        # Publier événement
                        if self.config.enable_invalidation_events:
                            await self._publish_cache_event(CacheEventType.SET, key)
                        
                        return {
                            "success": True,
                            "key": key,
                            "ttl": ttl,
                            "compressed": request.compress or len(str(request.value)) > self.config.compression_threshold
                        }
                    else:
                        raise HTTPException(status_code=500, detail="Failed to set cache value")
                        
                except HTTPException:
                    raise
                except Exception as e:
                    self.cache_operations.labels(
                        provider=self.config.primary_provider.value,
                        operation='set',
                        status='error'
                    ).inc()
                    self.logger.error(f"Cache set error: {str(e)}")
                    raise HTTPException(status_code=500, detail=f"Cache operation failed: {str(e)}")

        @self.app.get("/cache/get/{key}", response_model=CacheResponse)
        async def get_cache_value(key: str):
            """Récupérer une valeur du cache"""
            with self.cache_response_time.labels(provider=self.config.primary_provider.value, operation='get').time():
                try:
                    normalized_key = self._normalize_key(key)
                    
                    # Récupérer du cache
                    cache_data = await self._get_value(normalized_key)
                    
                    if cache_data:
                        # Cache hit
                        self.cache_operations.labels(
                            provider=self.config.primary_provider.value,
                            operation='get',
                            status='hit'
                        ).inc()
                        self.stats.hit_count += 1
                        
                        # Publier événement
                        if self.config.enable_invalidation_events:
                            await self._publish_cache_event(CacheEventType.HIT, normalized_key)
                        
                        # Décompresser et désérialiser
                        value = await self._deserialize_value(cache_data['value'], cache_data.get('compressed', False))
                        
                        return CacheResponse(
                            key=normalized_key,
                            value=value,
                            hit=True,
                            ttl_remaining=cache_data.get('ttl_remaining'),
                            compressed=cache_data.get('compressed', False),
                            metadata=cache_data.get('metadata', {}),
                            cached_at=cache_data.get('cached_at'),
                            accessed_at=datetime.utcnow()
                        )
                    
                    else:
                        # Cache miss
                        self.cache_operations.labels(
                            provider=self.config.primary_provider.value,
                            operation='get',
                            status='miss'
                        ).inc()
                        self.stats.miss_count += 1
                        
                        # Publier événement
                        if self.config.enable_invalidation_events:
                            await self._publish_cache_event(CacheEventType.MISS, normalized_key)
                        
                        return CacheResponse(
                            key=normalized_key,
                            hit=False,
                            accessed_at=datetime.utcnow()
                        )
                    
                except Exception as e:
                    self.cache_operations.labels(
                        provider=self.config.primary_provider.value,
                        operation='get',
                        status='error'
                    ).inc()
                    self.logger.error(f"Cache get error: {str(e)}")
                    raise HTTPException(status_code=500, detail=f"Cache operation failed: {str(e)}")

        @self.app.delete("/cache/delete/{key}")
        async def delete_cache_value(key: str):
            """Supprimer une valeur du cache"""
            try:
                normalized_key = self._normalize_key(key)
                
                success = await self._delete_value(normalized_key)
                
                if success:
                    self.cache_operations.labels(
                        provider=self.config.primary_provider.value,
                        operation='delete',
                        status='success'
                    ).inc()
                    self.stats.delete_count += 1
                    
                    # Publier événement
                    if self.config.enable_invalidation_events:
                        await self._publish_cache_event(CacheEventType.DELETE, normalized_key)
                
                return {"success": success, "key": normalized_key}
                
            except Exception as e:
                self.cache_operations.labels(
                    provider=self.config.primary_provider.value,
                    operation='delete',
                    status='error'
                ).inc()
                self.logger.error(f"Cache delete error: {str(e)}")
                raise HTTPException(status_code=500, detail=f"Cache operation failed: {str(e)}")

        @self.app.post("/cache/invalidate")
        async def invalidate_cache(pattern: str = "*", tags: List[str] = None):
            """Invalider le cache par pattern ou tags"""
            try:
                invalidated_count = 0
                
                if tags:
                    # Invalidation par tags
                    invalidated_count = await self._invalidate_by_tags(tags)
                else:
                    # Invalidation par pattern
                    invalidated_count = await self._invalidate_by_pattern(pattern)
                
                return {
                    "success": True,
                    "invalidated_count": invalidated_count,
                    "pattern": pattern,
                    "tags": tags
                }
                
            except Exception as e:
                self.logger.error(f"Cache invalidation error: {str(e)}")
                raise HTTPException(status_code=500, detail=f"Cache invalidation failed: {str(e)}")

        @self.app.post("/cache/lock/{lock_key}")
        async def acquire_distributed_lock(lock_key: str, timeout_seconds: int = 30):
            """Acquérir un verrou distribué"""
            if not self.config.enable_distributed_locks:
                raise HTTPException(status_code=501, detail="Distributed locks not enabled")
            
            try:
                lock_acquired = await self._acquire_lock(lock_key, timeout_seconds)
                
                return {
                    "success": lock_acquired,
                    "lock_key": lock_key,
                    "timeout_seconds": timeout_seconds
                }
                
            except Exception as e:
                self.logger.error(f"Lock acquisition error: {str(e)}")
                raise HTTPException(status_code=500, detail=f"Lock acquisition failed: {str(e)}")

        @self.app.delete("/cache/lock/{lock_key}")
        async def release_distributed_lock(lock_key: str):
            """Libérer un verrou distribué"""
            if not self.config.enable_distributed_locks:
                raise HTTPException(status_code=501, detail="Distributed locks not enabled")
            
            try:
                lock_released = await self._release_lock(lock_key)
                
                return {
                    "success": lock_released,
                    "lock_key": lock_key
                }
                
            except Exception as e:
                self.logger.error(f"Lock release error: {str(e)}")
                raise HTTPException(status_code=500, detail=f"Lock release failed: {str(e)}")

        @self.app.get("/cache/stats", response_model=CacheStats)
        async def get_cache_stats():
            """Récupérer statistiques du cache"""
            try:
                # Mettre à jour stats en temps réel
                await self._update_stats()
                
                # Calculer hit ratio
                total_requests = self.stats.hit_count + self.stats.miss_count
                self.stats.hit_ratio = (self.stats.hit_count / total_requests * 100) if total_requests > 0 else 0
                
                return self.stats
                
            except Exception as e:
                self.logger.error(f"Stats collection error: {str(e)}")
                raise HTTPException(status_code=500, detail="Failed to collect stats")

        @self.app.post("/cache/warm")
        async def warm_cache(keys_data: List[Dict[str, Any]], background_tasks: BackgroundTasks):
            """Pré-charger le cache avec des données"""
            if not self.config.enable_cache_warming:
                raise HTTPException(status_code=501, detail="Cache warming not enabled")
            
            background_tasks.add_task(self._warm_cache_background, keys_data)
            
            return {
                "success": True,
                "warming_keys": len(keys_data),
                "message": "Cache warming started in background"
            }

        @self.app.get("/cache/health")
        async def get_cache_health():
            """Health check du service de cache"""
            try:
                health_status = await self._check_providers_health()
                
                return {
                    "overall_status": health_status["overall_status"],
                    "providers": health_status["providers"],
                    "timestamp": datetime.utcnow().isoformat(),
                    "stats": {
                        "total_keys": self.stats.total_keys,
                        "hit_ratio": self.stats.hit_ratio,
                        "memory_usage_mb": self.stats.total_memory_bytes / 1024 / 1024
                    }
                }
                
            except Exception as e:
                return {
                    "overall_status": "unhealthy",
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat()
                }

    def _normalize_key(self, key: Union[str, CacheKey]) -> str:
        """Normaliser une clé de cache"""
        if isinstance(key, CacheKey):
            return key.generate_full_key()
        return str(key)

    async def _serialize_value(self, value: Any, compress: bool = False) -> str:
        """Sérialiser et comprimer une valeur"""
        try:
            # Sérialisation JSON
            serialized = json.dumps(value, default=str)
            
            # Compression si nécessaire
            if compress or (len(serialized) > self.config.compression_threshold):
                if self.config.compression_type == CompressionType.GZIP:
                    compressed = gzip.compress(serialized.encode('utf-8'))
                    return f"gzip:{compressed.hex()}"
                # Autres types de compression peuvent être ajoutés ici
            
            return serialized
            
        except Exception as e:
            self.logger.error(f"Serialization error: {str(e)}")
            raise

    async def _deserialize_value(self, serialized_value: str, compressed: bool = False) -> Any:
        """Désérialiser et décompresser une valeur"""
        try:
            value = serialized_value
            
            # Décompression si nécessaire
            if value.startswith("gzip:"):
                hex_data = value[5:]  # Remove "gzip:" prefix
                compressed_data = bytes.fromhex(hex_data)
                value = gzip.decompress(compressed_data).decode('utf-8')
            
            # Désérialisation
            return json.loads(value)
            
        except Exception as e:
            self.logger.error(f"Deserialization error: {str(e)}")
            raise

    async def _set_value(self, key: str, value: str, ttl: int, tags: List[str], metadata: Dict[str, Any]) -> bool:
        """Stocker valeur dans le provider principal"""
        try:
            cache_data = {
                "value": value,
                "cached_at": datetime.utcnow().isoformat(),
                "ttl": ttl,
                "tags": tags,
                "metadata": metadata,
                "compressed": value.startswith("gzip:")
            }
            
            # Provider principal
            if self.config.primary_provider == CacheProvider.REDIS and self.redis_client:
                await self.redis_client.setex(key, ttl, json.dumps(cache_data))
                
                # Stocker tags pour invalidation
                if tags:
                    for tag in tags:
                        await self.redis_client.sadd(f"tag:{tag}", key)
                        await self.redis_client.expire(f"tag:{tag}", ttl)
                
                return True
                
            elif self.config.primary_provider == CacheProvider.MEMCACHED and self.memcached_client:
                await self.memcached_client.set(key.encode(), json.dumps(cache_data).encode(), exptime=ttl)
                return True
                
            elif self.config.primary_provider == CacheProvider.MEMORY:
                return await self._set_memory_cache(key, cache_data, ttl)
            
            return False
            
        except Exception as e:
            self.logger.error(f"Set value error: {str(e)}")
            return False

    async def _get_value(self, key: str) -> Optional[Dict[str, Any]]:
        """Récupérer valeur du provider principal"""
        try:
            # Provider principal
            if self.config.primary_provider == CacheProvider.REDIS and self.redis_client:
                data = await self.redis_client.get(key)
                if data:
                    cache_data = json.loads(data)
                    # Calculer TTL restant
                    ttl_remaining = await self.redis_client.ttl(key)
                    cache_data['ttl_remaining'] = ttl_remaining if ttl_remaining > 0 else None
                    return cache_data
                    
            elif self.config.primary_provider == CacheProvider.MEMCACHED and self.memcached_client:
                data = await self.memcached_client.get(key.encode())
                if data:
                    return json.loads(data.decode())
                    
            elif self.config.primary_provider == CacheProvider.MEMORY:
                return await self._get_memory_cache(key)
            
            # Fallback provider
            if self.config.fallback_provider != self.config.primary_provider:
                return await self._get_value_fallback(key)
            
            return None
            
        except Exception as e:
            self.logger.error(f"Get value error: {str(e)}")
            return None

    async def _set_memory_cache(self, key: str, data: Dict[str, Any], ttl: int) -> bool:
        """Stocker dans le cache mémoire"""
        try:
            # Vérifier limites
            if len(self.memory_cache) >= self.config.memory_max_size:
                await self._evict_memory_cache()
            
            # Calculer taille approximative
            data_size = len(json.dumps(data))
            current_memory = sum(len(json.dumps(v)) for v in self.memory_cache.values())
            
            if current_memory + data_size > self.config.memory_max_memory_mb * 1024 * 1024:
                await self._evict_memory_cache()
            
            # Stocker avec métadonnées
            self.memory_cache[key] = {
                **data,
                "expires_at": time.time() + ttl
            }
            
            # Tracking pour LRU/LFU
            self.memory_access_times[key] = time.time()
            self.memory_access_counts[key] = self.memory_access_counts.get(key, 0) + 1
            
            return True
            
        except Exception as e:
            self.logger.error(f"Memory cache set error: {str(e)}")
            return False

    async def _get_memory_cache(self, key: str) -> Optional[Dict[str, Any]]:
        """Récupérer du cache mémoire"""
        try:
            if key not in self.memory_cache:
                return None
            
            data = self.memory_cache[key]
            
            # Vérifier expiration
            if data.get("expires_at", 0) < time.time():
                del self.memory_cache[key]
                self.memory_access_times.pop(key, None)
                self.memory_access_counts.pop(key, None)
                return None
            
            # Mettre à jour access tracking
            self.memory_access_times[key] = time.time()
            self.memory_access_counts[key] = self.memory_access_counts.get(key, 0) + 1
            
            # Calculer TTL restant
            ttl_remaining = int(data.get("expires_at", 0) - time.time())
            data["ttl_remaining"] = ttl_remaining if ttl_remaining > 0 else None
            
            return data
            
        except Exception as e:
            self.logger.error(f"Memory cache get error: {str(e)}")
            return None

    async def _evict_memory_cache(self):
        """Éviction du cache mémoire selon la policy"""
        try:
            if not self.memory_cache:
                return
            
            evict_count = max(1, len(self.memory_cache) // 10)  # Évict 10%
            
            if self.config.eviction_policy == EvictionPolicy.LRU:
                # Évict les moins récemment utilisés
                sorted_keys = sorted(
                    self.memory_cache.keys(),
                    key=lambda k: self.memory_access_times.get(k, 0)
                )[:evict_count]
                
            elif self.config.eviction_policy == EvictionPolicy.LFU:
                # Évict les moins fréquemment utilisés
                sorted_keys = sorted(
                    self.memory_cache.keys(),
                    key=lambda k: self.memory_access_counts.get(k, 0)
                )[:evict_count]
                
            elif self.config.eviction_policy == EvictionPolicy.RANDOM:
                import random
                sorted_keys = random.sample(list(self.memory_cache.keys()), evict_count)
                
            else:  # FIFO or TTL
                sorted_keys = list(self.memory_cache.keys())[:evict_count]
            
            # Évict selected keys
            for key in sorted_keys:
                self.memory_cache.pop(key, None)
                self.memory_access_times.pop(key, None)
                self.memory_access_counts.pop(key, None)
                self.stats.eviction_count += 1
            
            self.logger.debug(f"Evicted {len(sorted_keys)} keys from memory cache")
            
        except Exception as e:
            self.logger.error(f"Memory cache eviction error: {str(e)}")

    async def _cleanup_loop(self):
        """Boucle de nettoyage en arrière-plan"""
        while True:
            try:
                await asyncio.sleep(self.config.cleanup_interval_seconds)
                
                # Nettoyer cache mémoire expiré
                if self.config.primary_provider == CacheProvider.MEMORY or self.config.fallback_provider == CacheProvider.MEMORY:
                    await self._cleanup_expired_memory_cache()
                
                # Autres tâches de nettoyage
                await self._cleanup_tags()
                
            except Exception as e:
                self.logger.error(f"Cleanup loop error: {str(e)}")

    async def _cleanup_expired_memory_cache(self):
        """Nettoyer les entrées expirées du cache mémoire"""
        try:
            current_time = time.time()
            expired_keys = []
            
            for key, data in self.memory_cache.items():
                if data.get("expires_at", 0) < current_time:
                    expired_keys.append(key)
            
            for key in expired_keys:
                self.memory_cache.pop(key, None)
                self.memory_access_times.pop(key, None)
                self.memory_access_counts.pop(key, None)
            
            if expired_keys:
                self.logger.debug(f"Cleaned up {len(expired_keys)} expired keys from memory cache")
                
        except Exception as e:
            self.logger.error(f"Memory cache cleanup error: {str(e)}")

    def get_app(self) -> FastAPI:
        """Retourne instance FastAPI"""
        return self.app


def create_cache_service(config: CacheConfig = None) -> FastAPI:
    """
    Factory pour créer service de cache
    
    Args:
        config: Configuration personnalisée
        
    Returns:
        FastAPI: Instance du service configuré
    """
    cache_service = CacheServiceTemplate(config)
    return cache_service.get_app()


if __name__ == "__main__":
    import uvicorn
    
    config = CacheConfig(
        primary_provider=CacheProvider.REDIS,
        fallback_provider=CacheProvider.MEMORY,
        enable_stats_collection=True,
        enable_distributed_locks=True
    )
    
    app = create_cache_service(config)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )