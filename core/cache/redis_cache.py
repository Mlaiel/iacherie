"""
Enterprise Redis Cache Implementation for IA Influencer Agent Platform
High-performance distributed caching with Redis and Redis Cluster support
Specialized for multi-format content creators with AI processing pipeline

Business Logic: Creator Upload → AI Processing → Redis Cache → SEO → Distribution → Monetization

Author: Fahed Mlaiel <mlaiel@live.de>
Contact: mlaiel@live.de
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security Expert + 
      Microservices Architect + Audio Processing Expert + DevOps Engineer + IA Prompt Engineer

  PROPRIETARY SOFTWARE - UNAUTHORIZED USE PROHIBITED 
Copyright (C) 2024 Fahed Mlaiel. All rights reserved.
For licensing inquiries: mlaiel@live.de
"""

import asyncio
import logging
import json
import pickle
import zlib
import msgpack
import time
import struct
from typing import Any, Dict, List, Optional, Union, Set, Tuple, Callable, TypeVar
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import redis.asyncio as redis
from redis.cluster import RedisCluster
from redis.exceptions import ConnectionError, TimeoutError, ResponseError
import hashlib
import ssl
from cryptography.fernet import Fernet
import base64

logger = logging.getLogger(__name__)

T = TypeVar('T')

class SerializerType(Enum):
    """Supported serialization formats"""
    PICKLE = "pickle"
    JSON = "json"
    MSGPACK = "msgpack"
    BINARY = "binary"

class CompressionType(Enum):
    """Supported compression algorithms"""
    NONE = "none"
    ZLIB = "zlib"
    GZIP = "gzip"
    LZ4 = "lz4"

class EncryptionMode(Enum):
    """Encryption modes for sensitive data"""
    NONE = "none"
    FERNET = "fernet"
    AES = "aes"

@dataclass
class RedisConfig:
    """Enterprise Redis configuration for IA Influencer Agent"""
    # Connection settings
    host: str = "localhost"
    port: int = 6379
    password: Optional[str] = None
    db: int = 0
    username: Optional[str] = None
    
    # SSL/TLS configuration
    ssl_enabled: bool = False
    ssl_cert_reqs: str = "required"
    ssl_ca_certs: Optional[str] = None
    ssl_certfile: Optional[str] = None
    ssl_keyfile: Optional[str] = None
    
    # Connection pool settings
    max_connections: int = 100
    min_connections: int = 10
    socket_timeout: float = 5.0
    connection_timeout: float = 5.0
    retry_on_timeout: bool = True
    retry_attempts: int = 3
    retry_delay: float = 0.5
    health_check_interval: int = 30
    
    # Serialization and compression
    serializer: SerializerType = SerializerType.PICKLE
    compression: CompressionType = CompressionType.ZLIB
    compression_level: int = 6
    compression_threshold: int = 1024  # Compress if data > 1KB
    
    # Encryption for sensitive data
    encryption: EncryptionMode = EncryptionMode.NONE
    encryption_key: Optional[str] = None
    
    # Performance and monitoring
    enable_metrics: bool = True
    metrics_prefix: str = "cache:redis"
    enable_slow_log: bool = True
    slow_log_threshold: float = 0.1  # 100ms
    
    # Multi-tenant support
    tenant_isolation: bool = True
    tenant_prefix: str = "tenant"
    global_prefix: str = "ia_influencer"
    
    # Creator-specific settings
    creator_cache_ttl: int = 3600  # 1 hour default
    content_cache_ttl: int = 7200  # 2 hours for content
    analytics_cache_ttl: int = 300  # 5 minutes for analytics
    revenue_cache_ttl: int = 1800  # 30 minutes for revenue data
    
    # Platform-specific settings
    platform_api_cache_ttl: int = 600  # 10 minutes for platform APIs
    fingerprint_cache_ttl: int = 86400  # 24 hours for fingerprints
    session_cache_ttl: int = 1800  # 30 minutes for sessions
    
    # Memory optimization
    enable_memory_optimization: bool = True
    max_memory_policy: str = "allkeys-lru"  # Redis eviction policy
    lazy_free: bool = True
    
    # Connection pool kwargs
    connection_pool_kwargs: Dict[str, Any] = field(default_factory=dict)

@dataclass 
class RedisMetrics:
    """Redis performance and usage metrics"""
    # Operation counts
    hits: int = 0
    misses: int = 0
    sets: int = 0
    gets: int = 0
    deletes: int = 0
    errors: int = 0
    
    # Performance metrics
    total_latency: float = 0.0
    operation_count: int = 0
    avg_latency: float = 0.0
    max_latency: float = 0.0
    min_latency: float = float('inf')
    
    # Memory and compression
    total_memory_used: int = 0
    compression_ratio: float = 0.0
    encryption_overhead: float = 0.0
    
    # Connection stats
    active_connections: int = 0
    connection_errors: int = 0
    timeouts: int = 0
    
    # Business metrics
    creator_cache_usage: Dict[str, int] = field(default_factory=dict)
    content_type_stats: Dict[str, int] = field(default_factory=dict)
    platform_cache_stats: Dict[str, int] = field(default_factory=dict)
    
    # Timestamps
    last_reset: datetime = field(default_factory=datetime.utcnow)
    
    @property
    def hit_rate(self) -> float:
        """Calculate cache hit rate"""
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0
    
    @property
    def error_rate(self) -> float:
        """Calculate error rate"""
        total = self.operation_count
        return self.errors / total if total > 0 else 0.0
    
    def update_latency(self, latency: float):
        """Update latency statistics"""
        self.total_latency += latency
        self.operation_count += 1
        self.avg_latency = self.total_latency / self.operation_count
        self.max_latency = max(self.max_latency, latency)
        self.min_latency = min(self.min_latency, latency)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary"""



        return {
            'performance': {
                'hit_rate': self.hit_rate,
                'error_rate': self.error_rate,
                'avg_latency_ms': self.avg_latency * 1000,
                'max_latency_ms': self.max_latency * 1000,
                'min_latency_ms': self.min_latency * 1000
            },
            'operations': {
                'hits': self.hits,
                'misses': self.misses,
                'sets': self.sets,
                'gets': self.gets,
                'deletes': self.deletes,
                'errors': self.errors
            },
            'memory': {
                'total_used_bytes': self.total_memory_used,
                'compression_ratio': self.compression_ratio,
                'encryption_overhead': self.encryption_overhead
            },
            'connections': {
                'active': self.active_connections,
                'errors': self.connection_errors,
                'timeouts': self.timeouts
            },
            'business': {
                'creator_usage': self.creator_cache_usage,
                'content_types': self.content_type_stats,
                'platforms': self.platform_cache_stats
            },
            'last_reset': self.last_reset.isoformat()
        }

class RedisCache:
    """
    Enterprise Redis cache implementation for IA Influencer Agent platform
    Supports multi-format content creators with advanced features:
    - Multi-tenant isolation
    - Content-aware caching strategies  
    - AI fingerprint storage
    - Revenue tracking cache
    - Platform API caching
    - Real-time analytics
    """
    
    def __init__(self, config: RedisConfig):
        self.config = config
        self._redis: Optional[redis.Redis] = None
        self._connection_pool = None
        self._lock = asyncio.Lock()
        self._metrics = RedisMetrics()
        
        # Encryption handler
        self._encryption_handler = None
        if config.encryption != EncryptionMode.NONE:
            self._setup_encryption()
        
        # Compression handler
        self._compression_handler = self._get_compression_handler()
        
        # Serialization handler
        self._serialization_handler = self._get_serialization_handler()
        
        # Slow query tracking
        self._slow_queries: List[Dict[str, Any]] = []
        
        logger.info(f"RedisCache initialized for IA Influencer Agent - Backend: {config.host}:{config.port}")
    
    def _setup_encryption(self):
        """Setup encryption handler"""
        if self.config.encryption == EncryptionMode.FERNET:
            if not self.config.encryption_key:
                # Generate key if not provided
                key = Fernet.generate_key()
                self.config.encryption_key = base64.urlsafe_b64encode(key).decode()
                logger.warning("Generated new encryption key. Store securely!")
            
            key_bytes = base64.urlsafe_b64decode(self.config.encryption_key.encode())
            self._encryption_handler = Fernet(key_bytes)
    
    def _get_compression_handler(self) -> Callable:
        """Get compression handler based on configuration"""
        if self.config.compression == CompressionType.ZLIB:
            return lambda data: zlib.compress(data, self.config.compression_level)
        elif self.config.compression == CompressionType.GZIP:
            import gzip
            return lambda data: gzip.compress(data, compresslevel=self.config.compression_level)
        elif self.config.compression == CompressionType.LZ4:
            try:
                import lz4.frame
                return lz4.frame.compress
            except ImportError:
                logger.warning("LZ4 not available, falling back to zlib")
                return lambda data: zlib.compress(data, self.config.compression_level)
        else:
            return lambda data: data
    
    def _get_decompression_handler(self) -> Callable:
        """Get decompression handler"""
        if self.config.compression == CompressionType.ZLIB:
            return zlib.decompress
        elif self.config.compression == CompressionType.GZIP:
            import gzip
            return gzip.decompress
        elif self.config.compression == CompressionType.LZ4:
            try:
                import lz4.frame
                return lz4.frame.decompress
            except ImportError:
                return zlib.decompress
        else:
            return lambda data: data
    
    def _get_serialization_handler(self) -> Callable:
        """Get serialization handler"""
        if self.config.serializer == SerializerType.PICKLE:
            return lambda obj: pickle.dumps(obj, protocol=pickle.HIGHEST_PROTOCOL)
        elif self.config.serializer == SerializerType.JSON:
            return lambda obj: json.dumps(obj, default=str, ensure_ascii=False).encode('utf-8')
        elif self.config.serializer == SerializerType.MSGPACK:
            return lambda obj: msgpack.packb(obj, use_bin_type=True)
        else:
            return lambda obj: str(obj).encode('utf-8')
    
    def _get_deserialization_handler(self) -> Callable:
        """Get deserialization handler"""
        if self.config.serializer == SerializerType.PICKLE:
            return pickle.loads
        elif self.config.serializer == SerializerType.JSON:
            return lambda data: json.loads(data.decode('utf-8'))
        elif self.config.serializer == SerializerType.MSGPACK:
            return lambda data: msgpack.unpackb(data, raw=False)
        else:
            return lambda data: data.decode('utf-8')
    
    async def connect(self):
        """Establish Redis connection with enterprise features"""



        try:
            # SSL context setup
            ssl_context = None
            if self.config.ssl_enabled:
                ssl_context = ssl.create_default_context()
                if self.config.ssl_ca_certs:
                    ssl_context.load_verify_locations(self.config.ssl_ca_certs)
                if self.config.ssl_certfile and self.config.ssl_keyfile:
                    ssl_context.load_cert_chain(self.config.ssl_certfile, self.config.ssl_keyfile)
            
            # Create connection pool with enterprise settings
            pool_kwargs = {
                'host': self.config.host,
                'port': self.config.port,
                'password': self.config.password,
                'db': self.config.db,
                'username': self.config.username,
                'max_connections': self.config.max_connections,
                'socket_timeout': self.config.socket_timeout,
                'connection_timeout': self.config.connection_timeout,
                'retry_on_timeout': self.config.retry_on_timeout,
                'health_check_interval': self.config.health_check_interval,
                'ssl': ssl_context,
                **self.config.connection_pool_kwargs
            }
            
            self._connection_pool = redis.ConnectionPool(**pool_kwargs)
            self._redis = redis.Redis(connection_pool=self._connection_pool)
            
            # Test connection
            await self._redis.ping()
            
            # Configure Redis for optimal performance
            await self._configure_redis_optimization()
            
            self._metrics.active_connections = self.config.max_connections
            logger.info("Redis connection established with enterprise configuration")
            
        except Exception as e:
            self._metrics.connection_errors += 1
            logger.error(f"Failed to connect to Redis: {e}")
            raise ConnectionError(f"Redis connection failed: {e}")
    
    async def _configure_redis_optimization(self):
        """Configure Redis for optimal performance"""



        try:
            if self.config.enable_memory_optimization:
                # Set memory policy
                await self._redis.config_set('maxmemory-policy', self.config.max_memory_policy)
                
                # Enable lazy freeing
                if self.config.lazy_free:
                    await self._redis.config_set('lazyfree-lazy-eviction', 'yes')
                    await self._redis.config_set('lazyfree-lazy-expire', 'yes')
                    await self._redis.config_set('lazyfree-lazy-server-del', 'yes')
            
            logger.info("Redis optimization configured")
            
        except Exception as e:
            logger.warning(f"Redis optimization configuration failed: {e}")
    
    def _generate_cache_key(self, 
                           key: str, 
                           tenant_id: Optional[str] = None,
                           content_type: Optional[str] = None,
                           creator_id: Optional[str] = None) -> str:
        """Generate hierarchical cache key for IA Influencer Agent"""
        key_parts = [self.config.global_prefix]
        
        # Add tenant isolation
        if self.config.tenant_isolation and tenant_id:
            key_parts.append(f"{self.config.tenant_prefix}:{tenant_id}")
        
        # Add creator-specific namespace
        if creator_id:
            key_parts.append(f"creator:{creator_id}")
        
        # Add content type for better organization
        if content_type:
            key_parts.append(f"type:{content_type}")
        
        key_parts.append(key)
        return ":".join(key_parts)
    
    def _get_ttl_for_content_type(self, content_type: str) -> int:
        """Get appropriate TTL based on content type"""
        ttl_mapping = {
            'creator_profile': self.config.creator_cache_ttl,
            'audio_content': self.config.content_cache_ttl,
            'video_content': self.config.content_cache_ttl,
            'image_content': self.config.content_cache_ttl,
            'text_content': self.config.content_cache_ttl,
            'analytics': self.config.analytics_cache_ttl,
            'revenue': self.config.revenue_cache_ttl,
            'platform_api': self.config.platform_api_cache_ttl,
            'fingerprint': self.config.fingerprint_cache_ttl,
            'session': self.config.session_cache_ttl
        }
        
        return ttl_mapping.get(content_type, self.config.creator_cache_ttl)
    
    def _serialize(self, value: Any) -> bytes:
        """Advanced serialization with compression and encryption"""
        start_time = time.time()
        
        try:
            # Serialize
            serialized = self._serialization_handler(value)
            original_size = len(serialized)
            
            # Compress if above threshold
            if (self.config.compression != CompressionType.NONE and 
                len(serialized) > self.config.compression_threshold):
                compressed = self._compression_handler(serialized)
                compression_ratio = len(compressed) / len(serialized)
                
                # Update compression metrics
                self._metrics.compression_ratio = (
                    self._metrics.compression_ratio * 0.9 + compression_ratio * 0.1
                )
                
                # Prepend compression flag
                serialized = b'\x01' + compressed
            else:
                # No compression flag
                serialized = b'\x00' + serialized
            
            # Encrypt if enabled
            if self.config.encryption != EncryptionMode.NONE and self._encryption_handler:
                encrypted = self._encryption_handler.encrypt(serialized)
                encryption_overhead = len(encrypted) / len(serialized)
                self._metrics.encryption_overhead = (
                    self._metrics.encryption_overhead * 0.9 + encryption_overhead * 0.1
                )
                serialized = b'\xFF' + encrypted
            else:
                # No encryption flag
                serialized = b'\x00' + serialized
            
            # Update memory metrics
            self._metrics.total_memory_used += len(serialized)
            
            # Track serialization time
            latency = time.time() - start_time
            if latency > self.config.slow_log_threshold:
                self._track_slow_operation('serialize', latency, {'size': original_size})
            
            return serialized
            
        except Exception as e:
            logger.error(f"Serialization error: {e}")
            raise ValueError(f"Failed to serialize data: {e}")
    
    def _deserialize(self, data: bytes) -> Any:
        """Advanced deserialization with decompression and decryption"""
        start_time = time.time()
        
        try:
            # Check encryption flag
            if data[0:1] == b'\xFF':
                if self._encryption_handler:
                    data = self._encryption_handler.decrypt(data[1:])
                else:
                    raise ValueError("Encrypted data found but no encryption handler")
            else:
                data = data[1:]  # Remove encryption flag
            
            # Check compression flag
            if data[0:1] == b'\x01':
                decompression_handler = self._get_decompression_handler()
                data = decompression_handler(data[1:])
            else:
                data = data[1:]  # Remove compression flag
            
            # Deserialize
            deserialization_handler = self._get_deserialization_handler()
            result = deserialization_handler(data)
            
            # Track deserialization time
            latency = time.time() - start_time
            if latency > self.config.slow_log_threshold:
                self._track_slow_operation('deserialize', latency, {'size': len(data)})
            
            return result
            
        except Exception as e:
            logger.error(f"Deserialization error: {e}")
            raise ValueError(f"Failed to deserialize data: {e}")
    
    def _track_slow_operation(self, operation: str, latency: float, metadata: Dict[str, Any]):
        """Track slow operations for performance monitoring"""
        if self.config.enable_slow_log:
            slow_query = {
                'operation': operation,
                'latency_ms': latency * 1000,
                'timestamp': datetime.utcnow().isoformat(),
                'metadata': metadata
            }
            
            self._slow_queries.append(slow_query)
            
            # Keep only recent slow queries (last 100)
            if len(self._slow_queries) > 100:
                self._slow_queries = self._slow_queries[-100:]
            
            logger.warning(f"Slow Redis operation: {operation} took {latency*1000:.2f}ms")
    
    async def get(self, 
                  key: str, 
                  tenant_id: Optional[str] = None,
                  content_type: Optional[str] = None,
                  creator_id: Optional[str] = None,
                  default: Optional[T] = None) -> Optional[T]:
        """Get value from Redis cache with business logic awareness"""
        if not self._redis:
            await self.connect()
        
        cache_key = self._generate_cache_key(key, tenant_id, content_type, creator_id)
        start_time = time.time()
        
        try:
            data = await self._redis.get(cache_key)
            latency = time.time() - start_time
            
            if data is None:
                self._metrics.misses += 1
                self._metrics.gets += 1
                self._metrics.update_latency(latency)
                return default
            
            value = self._deserialize(data)
            
            # Update metrics
            self._metrics.hits += 1
            self._metrics.gets += 1
            self._metrics.update_latency(latency)
            
            # Track business metrics
            if creator_id:
                self._metrics.creator_cache_usage[creator_id] = (
                    self._metrics.creator_cache_usage.get(creator_id, 0) + 1
                )
            
            if content_type:
                self._metrics.content_type_stats[content_type] = (
                    self._metrics.content_type_stats.get(content_type, 0) + 1
                )
            
            return value
            
        except (ConnectionError, TimeoutError) as e:
            self._metrics.timeouts += 1
            self._metrics.errors += 1
            logger.error(f"Redis connection error for key {cache_key}: {e}")
            return default
            
        except Exception as e:
            self._metrics.errors += 1
            logger.error(f"Redis get error for key {cache_key}: {e}")
            return default
    
    async def set(self, 
                  key: str, 
                  value: Any, 
                  ttl: Optional[int] = None,
                  tenant_id: Optional[str] = None,
                  content_type: Optional[str] = None,
                  creator_id: Optional[str] = None) -> bool:
        """Set value in Redis cache with intelligent TTL and business awareness"""
        if not self._redis:
            await self.connect()
        
        cache_key = self._generate_cache_key(key, tenant_id, content_type, creator_id)
        start_time = time.time()
        
        try:
            # Determine TTL based on content type if not provided
            if ttl is None and content_type:
                ttl = self._get_ttl_for_content_type(content_type)
            elif ttl is None:
                ttl = self.config.creator_cache_ttl
            
            serialized_data = self._serialize(value)
            
            # Set with TTL
            if ttl > 0:
                result = await self._redis.setex(cache_key, ttl, serialized_data)
            else:
                result = await self._redis.set(cache_key, serialized_data)
            
            latency = time.time() - start_time
            
            if result:
                self._metrics.sets += 1
                self._metrics.update_latency(latency)
                
                # Track business metrics
                if creator_id:
                    self._metrics.creator_cache_usage[creator_id] = (
                        self._metrics.creator_cache_usage.get(creator_id, 0) + 1
                    )
                
                if content_type:
                    self._metrics.content_type_stats[content_type] = (
                        self._metrics.content_type_stats.get(content_type, 0) + 1
                    )
                
                return True
            
            return False
            
        except (ConnectionError, TimeoutError) as e:
            self._metrics.timeouts += 1
            self._metrics.errors += 1
            logger.error(f"Redis connection error for key {cache_key}: {e}")
            return False
            
        except Exception as e:
            self._metrics.errors += 1
            logger.error(f"Redis set error for key {cache_key}: {e}")
            return False
    
    async def delete(self, 
                     key: str,
                     tenant_id: Optional[str] = None,
                     content_type: Optional[str] = None,
                     creator_id: Optional[str] = None) -> bool:
        """Delete key from Redis cache with business logic awareness"""
        if not self._redis:
            await self.connect()
        
        cache_key = self._generate_cache_key(key, tenant_id, content_type, creator_id)
        start_time = time.time()
        
        try:
            result = await self._redis.delete(cache_key)
            latency = time.time() - start_time
            
            if result > 0:
                self._metrics.deletes += 1
                self._metrics.update_latency(latency)
                return True
            return False
            
        except (ConnectionError, TimeoutError) as e:
            self._metrics.timeouts += 1
            self._metrics.errors += 1
            logger.error(f"Redis connection error for key {cache_key}: {e}")
            return False
            
        except Exception as e:
            self._metrics.errors += 1
            logger.error(f"Redis delete error for key {cache_key}: {e}")
            return False
    
    async def exists(self, 
                     key: str,
                     tenant_id: Optional[str] = None,
                     content_type: Optional[str] = None,
                     creator_id: Optional[str] = None) -> bool:
        """Check if key exists in Redis with business logic awareness"""
        if not self._redis:
            await self.connect()
        
        cache_key = self._generate_cache_key(key, tenant_id, content_type, creator_id)
        
        try:
            return bool(await self._redis.exists(cache_key))
        except Exception as e:
            logger.error(f"Redis exists error for key {cache_key}: {e}")
            return False
    
    async def expire(self, 
                     key: str, 
                     ttl: int,
                     tenant_id: Optional[str] = None,
                     content_type: Optional[str] = None,
                     creator_id: Optional[str] = None) -> bool:
        """Set expiration time for key"""
        if not self._redis:
            await self.connect()
        
        cache_key = self._generate_cache_key(key, tenant_id, content_type, creator_id)
        
        try:
            return bool(await self._redis.expire(cache_key, ttl))
        except Exception as e:
            logger.error(f"Redis expire error for key {cache_key}: {e}")
            return False
    
    async def ttl(self, 
                  key: str,
                  tenant_id: Optional[str] = None,
                  content_type: Optional[str] = None,
                  creator_id: Optional[str] = None) -> int:
        """Get TTL for key"""
        if not self._redis:
            await self.connect()
        
        cache_key = self._generate_cache_key(key, tenant_id, content_type, creator_id)
        
        try:
            return await self._redis.ttl(cache_key)
        except Exception as e:
            logger.error(f"Redis TTL error for key {cache_key}: {e}")
            return -1
    
    async def keys(self, 
                   pattern: str = "*",
                   tenant_id: Optional[str] = None,
                   content_type: Optional[str] = None,
                   creator_id: Optional[str] = None) -> List[str]:
        """Get keys matching pattern with business logic awareness"""
        if not self._redis:
            await self.connect()
        
        # Build pattern with business logic
        if tenant_id or content_type or creator_id:
            cache_pattern = self._generate_cache_key(pattern, tenant_id, content_type, creator_id)
        else:
            cache_pattern = f"{self.config.global_prefix}:{pattern}"
        
        try:
            keys = await self._redis.keys(cache_pattern)
            return [key.decode() if isinstance(key, bytes) else key for key in keys]
        except Exception as e:
            logger.error(f"Redis keys error for pattern {cache_pattern}: {e}")
            return []
    
    async def flush(self, tenant_id: Optional[str] = None) -> bool:
        """Flush data from Redis - tenant-aware"""
        if not self._redis:
            await self.connect()
        
        try:
            if tenant_id and self.config.tenant_isolation:
                # Flush only tenant data
                pattern = f"{self.config.global_prefix}:{self.config.tenant_prefix}:{tenant_id}:*"
                keys = await self._redis.keys(pattern)
                if keys:
                    await self._redis.delete(*keys)
            else:
                # Flush all data in current DB
                await self._redis.flushdb()
            
            return True
        except Exception as e:
            logger.error(f"Redis flush error: {e}")
            return False
    
    async def info(self) -> Dict[str, Any]:
        """Get Redis server information"""
        if not self._redis:
            await self.connect()
        
        try:
            return await self._redis.info()
        except Exception as e:
            logger.error(f"Redis info error: {e}")
            return {}
    
    async def pipeline(self):
        """Create Redis pipeline for batch operations"""
        if not self._redis:
            await self.connect()
        return self._redis.pipeline()
    
    # Content-specific cache operations for IA Influencer Agent
    
    async def cache_creator_profile(self, 
                                   creator_id: str,
                                   profile_data: Dict[str, Any],
                                   ttl: Optional[int] = None) -> bool:
        """Cache creator profile with optimized settings"""



        return await self.set(
            key=f"profile:{creator_id}",
            value=profile_data,
            ttl=ttl or self.config.creator_cache_ttl,
            content_type="creator_profile",
            creator_id=creator_id
        )
    
    async def get_creator_profile(self, creator_id: str) -> Optional[Dict[str, Any]]:
        """Get cached creator profile"""



        return await self.get(
            key=f"profile:{creator_id}",
            content_type="creator_profile",
            creator_id=creator_id
        )
    
    async def cache_content_metadata(self,
                                    content_id: str,
                                    metadata: Dict[str, Any],
                                    content_type: str,
                                    creator_id: str,
                                    ttl: Optional[int] = None) -> bool:
        """Cache content metadata (audio, video, image, text)"""



        return await self.set(
            key=f"content:{content_id}:metadata",
            value=metadata,
            ttl=ttl or self.config.content_cache_ttl,
            content_type=f"{content_type}_content",
            creator_id=creator_id
        )
    
    async def get_content_metadata(self,
                                  content_id: str,
                                  content_type: str,
                                  creator_id: str) -> Optional[Dict[str, Any]]:
        """Get cached content metadata"""



        return await self.get(
            key=f"content:{content_id}:metadata",
            content_type=f"{content_type}_content",
            creator_id=creator_id
        )
    
    async def cache_analytics_data(self,
                                  analytics_id: str,
                                  analytics_data: Dict[str, Any],
                                  creator_id: str,
                                  ttl: Optional[int] = None) -> bool:
        """Cache analytics data with short TTL"""



        return await self.set(
            key=f"analytics:{analytics_id}",
            value=analytics_data,
            ttl=ttl or self.config.analytics_cache_ttl,
            content_type="analytics",
            creator_id=creator_id
        )
    
    async def get_analytics_data(self,
                                analytics_id: str,
                                creator_id: str) -> Optional[Dict[str, Any]]:
        """Get cached analytics data"""



        return await self.get(
            key=f"analytics:{analytics_id}",
            content_type="analytics",
            creator_id=creator_id
        )
    
    async def cache_revenue_data(self,
                                revenue_id: str,
                                revenue_data: Dict[str, Any],
                                creator_id: str,
                                ttl: Optional[int] = None) -> bool:
        """Cache revenue tracking data"""



        return await self.set(
            key=f"revenue:{revenue_id}",
            value=revenue_data,
            ttl=ttl or self.config.revenue_cache_ttl,
            content_type="revenue",
            creator_id=creator_id
        )
    
    async def get_revenue_data(self,
                              revenue_id: str,
                              creator_id: str) -> Optional[Dict[str, Any]]:
        """Get cached revenue data"""



        return await self.get(
            key=f"revenue:{revenue_id}",
            content_type="revenue",
            creator_id=creator_id
        )
    
    async def cache_platform_api_response(self,
                                         platform: str,
                                         endpoint: str,
                                         response_data: Dict[str, Any],
                                         creator_id: Optional[str] = None,
                                         ttl: Optional[int] = None) -> bool:
        """Cache platform API responses (Spotify, YouTube, Instagram, etc.)"""
        api_key = f"platform:{platform}:api:{hashlib.md5(endpoint.encode()).hexdigest()}"
        return await self.set(
            key=api_key,
            value=response_data,
            ttl=ttl or self.config.platform_api_cache_ttl,
            content_type="platform_api",
            creator_id=creator_id
        )
    
    async def get_platform_api_response(self,
                                       platform: str,
                                       endpoint: str,
                                       creator_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get cached platform API response"""
        api_key = f"platform:{platform}:api:{hashlib.md5(endpoint.encode()).hexdigest()}"
        return await self.get(
            key=api_key,
            content_type="platform_api",
            creator_id=creator_id
        )
    
    async def cache_ai_fingerprint(self,
                                  fingerprint_id: str,
                                  fingerprint_data: Dict[str, Any],
                                  content_type: str,
                                  creator_id: str,
                                  ttl: Optional[int] = None) -> bool:
        """Cache AI fingerprint for content protection"""



        return await self.set(
            key=f"fingerprint:{content_type}:{fingerprint_id}",
            value=fingerprint_data,
            ttl=ttl or self.config.fingerprint_cache_ttl,
            content_type="fingerprint",
            creator_id=creator_id
        )
    
    async def get_ai_fingerprint(self,
                                fingerprint_id: str,
                                content_type: str,
                                creator_id: str) -> Optional[Dict[str, Any]]:
        """Get cached AI fingerprint"""



        return await self.get(
            key=f"fingerprint:{content_type}:{fingerprint_id}",
            content_type="fingerprint",
            creator_id=creator_id
        )
    
    # Hash operations with business logic
    async def hget(self, 
                   name: str, 
                   key: str,
                   tenant_id: Optional[str] = None,
                   content_type: Optional[str] = None,
                   creator_id: Optional[str] = None) -> Optional[Any]:
        """Get hash field value with business logic"""
        if not self._redis:
            await self.connect()
        
        cache_name = self._generate_cache_key(name, tenant_id, content_type, creator_id)
        
        try:
            data = await self._redis.hget(cache_name, key)
            if data is None:
                return None
            return self._deserialize(data)
        except Exception as e:
            logger.error(f"Redis hget error for {cache_name}:{key}: {e}")
            return None
    
    async def hset(self, 
                   name: str, 
                   key: str, 
                   value: Any,
                   tenant_id: Optional[str] = None,
                   content_type: Optional[str] = None,
                   creator_id: Optional[str] = None) -> bool:
        """Set hash field value with business logic"""
        if not self._redis:
            await self.connect()
        
        cache_name = self._generate_cache_key(name, tenant_id, content_type, creator_id)
        
        try:
            serialized_data = self._serialize(value)
            result = await self._redis.hset(cache_name, key, serialized_data)
            return bool(result)
        except Exception as e:
            logger.error(f"Redis hset error for {cache_name}:{key}: {e}")
            return False
    
    async def hgetall(self, 
                      name: str,
                      tenant_id: Optional[str] = None,
                      content_type: Optional[str] = None,
                      creator_id: Optional[str] = None) -> Dict[str, Any]:
        """Get all hash fields with business logic"""
        if not self._redis:
            await self.connect()
        
        cache_name = self._generate_cache_key(name, tenant_id, content_type, creator_id)
        
        try:
            data = await self._redis.hgetall(cache_name)
            return {
                k.decode() if isinstance(k, bytes) else k: self._deserialize(v)
                for k, v in data.items()
            }
        except Exception as e:
            logger.error(f"Redis hgetall error for {cache_name}: {e}")
            return {}
    
    # List operations with business logic
    async def lpush(self, 
                    name: str, 
                    *values: Any,
                    tenant_id: Optional[str] = None,
                    content_type: Optional[str] = None,
                    creator_id: Optional[str] = None) -> int:
        """Push values to left of list with business logic"""
        if not self._redis:
            await self.connect()
        
        cache_name = self._generate_cache_key(name, tenant_id, content_type, creator_id)
        
        try:
            serialized_values = [self._serialize(v) for v in values]
            return await self._redis.lpush(cache_name, *serialized_values)
        except Exception as e:
            logger.error(f"Redis lpush error for {cache_name}: {e}")
            return 0
    
    async def rpop(self, 
                   name: str,
                   tenant_id: Optional[str] = None,
                   content_type: Optional[str] = None,
                   creator_id: Optional[str] = None) -> Optional[Any]:
        """Pop value from right of list with business logic"""
        if not self._redis:
            await self.connect()
        
        cache_name = self._generate_cache_key(name, tenant_id, content_type, creator_id)
        
        try:
            data = await self._redis.rpop(cache_name)
            if data is None:
                return None
            return self._deserialize(data)
        except Exception as e:
            logger.error(f"Redis rpop error for {cache_name}: {e}")
            return None
    
    async def lrange(self, 
                     name: str, 
                     start: int = 0, 
                     end: int = -1,
                     tenant_id: Optional[str] = None,
                     content_type: Optional[str] = None,
                     creator_id: Optional[str] = None) -> List[Any]:
        """Get list range with business logic"""
        if not self._redis:
            await self.connect()
        
        cache_name = self._generate_cache_key(name, tenant_id, content_type, creator_id)
        
        try:
            data = await self._redis.lrange(cache_name, start, end)
            return [self._deserialize(item) for item in data]
        except Exception as e:
            logger.error(f"Redis lrange error for {cache_name}: {e}")
            return []
    
    # Set operations with business logic
    async def sadd(self, 
                   name: str, 
                   *values: Any,
                   tenant_id: Optional[str] = None,
                   content_type: Optional[str] = None,
                   creator_id: Optional[str] = None) -> int:
        """Add values to set with business logic"""
        if not self._redis:
            await self.connect()
        
        cache_name = self._generate_cache_key(name, tenant_id, content_type, creator_id)
        
        try:
            serialized_values = [self._serialize(v) for v in values]
            return await self._redis.sadd(cache_name, *serialized_values)
        except Exception as e:
            logger.error(f"Redis sadd error for {cache_name}: {e}")
            return 0
    
    async def smembers(self, 
                       name: str,
                       tenant_id: Optional[str] = None,
                       content_type: Optional[str] = None,
                       creator_id: Optional[str] = None) -> Set[Any]:
        """Get all set members with business logic"""
        if not self._redis:
            await self.connect()
        
        cache_name = self._generate_cache_key(name, tenant_id, content_type, creator_id)
        
        try:
            data = await self._redis.smembers(cache_name)
            return {self._deserialize(item) for item in data}
        except Exception as e:
            logger.error(f"Redis smembers error for {cache_name}: {e}")
            return set()
    
    # Bulk operations for performance
    async def mget(self, 
                   keys: List[str],
                   tenant_id: Optional[str] = None,
                   content_type: Optional[str] = None,
                   creator_id: Optional[str] = None) -> List[Optional[Any]]:
        """Get multiple values in single operation"""
        if not self._redis:
            await self.connect()
        
        cache_keys = [
            self._generate_cache_key(key, tenant_id, content_type, creator_id)
            for key in keys
        ]
        
        try:
            data_list = await self._redis.mget(cache_keys)
            return [
                self._deserialize(data) if data is not None else None
                for data in data_list
            ]
        except Exception as e:
            logger.error(f"Redis mget error: {e}")
            return [None] * len(keys)
    
    async def mset(self, 
                   mapping: Dict[str, Any],
                   ttl: Optional[int] = None,
                   tenant_id: Optional[str] = None,
                   content_type: Optional[str] = None,
                   creator_id: Optional[str] = None) -> bool:
        """Set multiple values in single operation"""
        if not self._redis:
            await self.connect()
        
        try:
            # Prepare serialized mapping
            cache_mapping = {}
            for key, value in mapping.items():
                cache_key = self._generate_cache_key(key, tenant_id, content_type, creator_id)
                cache_mapping[cache_key] = self._serialize(value)
            
            # Use pipeline for atomic operation
            pipe = await self.pipeline()
            await pipe.mset(cache_mapping)
            
            # Set TTL if provided
            if ttl:
                for cache_key in cache_mapping.keys():
                    await pipe.expire(cache_key, ttl)
            
            await pipe.execute()
            
            self._metrics.sets += len(mapping)
            return True
            
        except Exception as e:
            logger.error(f"Redis mset error: {e}")
            return False
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics"""
        server_info = await self.info()
        
        return {
            'redis_metrics': self._metrics.to_dict(),
            'slow_queries': self._slow_queries[-10:],  # Last 10 slow queries
            'server_info': {
                'redis_version': server_info.get('redis_version', 'unknown'),
                'used_memory': server_info.get('used_memory', 0),
                'used_memory_human': server_info.get('used_memory_human', '0B'),
                'connected_clients': server_info.get('connected_clients', 0),
                'total_commands_processed': server_info.get('total_commands_processed', 0),
                'keyspace_hits': server_info.get('keyspace_hits', 0),
                'keyspace_misses': server_info.get('keyspace_misses', 0)
            },
            'configuration': {
                'host': self.config.host,
                'port': self.config.port,
                'db': self.config.db,
                'ssl_enabled': self.config.ssl_enabled,
                'compression': self.config.compression.value,
                'serializer': self.config.serializer.value,
                'encryption': self.config.encryption.value,
                'tenant_isolation': self.config.tenant_isolation
            }
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Comprehensive health check for monitoring"""



        try:
            if not self._redis:
                await self.connect()
            
            start_time = time.time()
            await self._redis.ping()
            ping_latency = time.time() - start_time
            
            # Test basic operations
            test_key = f"{self.config.global_prefix}:health_check"
            test_value = {"timestamp": datetime.utcnow().isoformat(), "test": True}
            
            start_time = time.time()
            await self.set(test_key, test_value, ttl=60)
            set_latency = time.time() - start_time
            
            start_time = time.time()
            retrieved = await self.get(test_key)
            get_latency = time.time() - start_time
            
            await self.delete(test_key)
            
            is_healthy = (
                ping_latency < 0.1 and  # Ping < 100ms
                set_latency < 0.1 and   # Set < 100ms  
                get_latency < 0.1 and   # Get < 100ms
                retrieved is not None
            )
            
            return {
                'healthy': is_healthy,
                'ping_latency_ms': ping_latency * 1000,
                'set_latency_ms': set_latency * 1000,
                'get_latency_ms': get_latency * 1000,
                'data_integrity': retrieved == test_value,
                'connection_active': True,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                'healthy': False,
                'error': str(e),
                'connection_active': False,
                'timestamp': datetime.utcnow().isoformat()
            }
    
    async def close(self):
        """Close Redis connection gracefully"""



        try:
            if self._redis:
                await self._redis.close()
            if self._connection_pool:
                await self._connection_pool.disconnect()
            
            logger.info("Redis connection closed gracefully")
            
        except Exception as e:
            logger.error(f"Error closing Redis connection: {e}")

class RedisClusterCache(RedisCache):
    """
    Redis Cluster cache implementation for distributed caching
    Specialized for IA Influencer Agent with high availability
    """
    
    def __init__(self, config: RedisConfig, startup_nodes: List[Dict[str, Any]]):
        super().__init__(config)
        self.startup_nodes = startup_nodes
        self._cluster: Optional[RedisCluster] = None
        
        logger.info(f"RedisClusterCache initialized with {len(startup_nodes)} nodes")
    
    async def connect(self):
        """Establish Redis Cluster connection with enterprise features"""



        try:
            cluster_kwargs = {
                'startup_nodes': self.startup_nodes,
                'password': self.config.password,
                'username': self.config.username,
                'socket_timeout': self.config.socket_timeout,
                'decode_responses': False,
                'skip_full_coverage_check': True,
                'health_check_interval': self.config.health_check_interval,
                'max_connections_per_node': self.config.max_connections // len(self.startup_nodes)
            }
            
            # SSL configuration for cluster
            if self.config.ssl_enabled:
                ssl_context = ssl.create_default_context()
                if self.config.ssl_ca_certs:
                    ssl_context.load_verify_locations(self.config.ssl_ca_certs)
                cluster_kwargs['ssl'] = ssl_context
            
            self._cluster = RedisCluster(**cluster_kwargs)
            
            # Test cluster connection
            await self._cluster.ping()
            
            # Configure cluster optimization
            await self._configure_cluster_optimization()
            
            self._metrics.active_connections = len(self.startup_nodes) * (
                self.config.max_connections // len(self.startup_nodes)
            )
            
            logger.info("Redis Cluster connection established with enterprise configuration")
            
        except Exception as e:
            self._metrics.connection_errors += 1
            logger.error(f"Failed to connect to Redis Cluster: {e}")
            raise ConnectionError(f"Redis Cluster connection failed: {e}")
    
    async def _configure_cluster_optimization(self):
        """Configure Redis Cluster for optimal performance"""



        try:
            # Apply optimization settings to all cluster nodes
            cluster_info = await self._cluster.cluster_info()
            logger.info(f"Redis Cluster optimization configured: {cluster_info.get('cluster_state', 'unknown')}")
            
        except Exception as e:
            logger.warning(f"Redis Cluster optimization configuration failed: {e}")
    
    # Override key methods to use cluster client
    async def get(self, 
                  key: str, 
                  tenant_id: Optional[str] = None,
                  content_type: Optional[str] = None,
                  creator_id: Optional[str] = None,
                  default: Optional[T] = None) -> Optional[T]:
        """Get value from Redis Cluster with business logic"""
        if not self._cluster:
            await self.connect()
        
        cache_key = self._generate_cache_key(key, tenant_id, content_type, creator_id)
        start_time = time.time()
        
        try:
            data = await self._cluster.get(cache_key)
            latency = time.time() - start_time
            
            if data is None:
                self._metrics.misses += 1
                self._metrics.gets += 1
                self._metrics.update_latency(latency)
                return default
            
            value = self._deserialize(data)
            
            # Update metrics
            self._metrics.hits += 1
            self._metrics.gets += 1
            self._metrics.update_latency(latency)
            
            # Track business metrics
            if creator_id:
                self._metrics.creator_cache_usage[creator_id] = (
                    self._metrics.creator_cache_usage.get(creator_id, 0) + 1
                )
            
            if content_type:
                self._metrics.content_type_stats[content_type] = (
                    self._metrics.content_type_stats.get(content_type, 0) + 1
                )
            
            return value
            
        except (ConnectionError, TimeoutError) as e:
            self._metrics.timeouts += 1
            self._metrics.errors += 1
            logger.error(f"Redis Cluster connection error for key {cache_key}: {e}")
            return default
            
        except Exception as e:
            self._metrics.errors += 1
            logger.error(f"Redis Cluster get error for key {cache_key}: {e}")
            return default
    
    async def set(self, 
                  key: str, 
                  value: Any, 
                  ttl: Optional[int] = None,
                  tenant_id: Optional[str] = None,
                  content_type: Optional[str] = None,
                  creator_id: Optional[str] = None) -> bool:
        """Set value in Redis Cluster with business logic"""
        if not self._cluster:
            await self.connect()
        
        cache_key = self._generate_cache_key(key, tenant_id, content_type, creator_id)
        start_time = time.time()
        
        try:
            # Determine TTL based on content type if not provided
            if ttl is None and content_type:
                ttl = self._get_ttl_for_content_type(content_type)
            elif ttl is None:
                ttl = self.config.creator_cache_ttl
            
            serialized_data = self._serialize(value)
            
            # Set with TTL
            if ttl > 0:
                result = await self._cluster.setex(cache_key, ttl, serialized_data)
            else:
                result = await self._cluster.set(cache_key, serialized_data)
            
            latency = time.time() - start_time
            
            if result:
                self._metrics.sets += 1
                self._metrics.update_latency(latency)
                
                # Track business metrics
                if creator_id:
                    self._metrics.creator_cache_usage[creator_id] = (
                        self._metrics.creator_cache_usage.get(creator_id, 0) + 1
                    )
                
                if content_type:
                    self._metrics.content_type_stats[content_type] = (
                        self._metrics.content_type_stats.get(content_type, 0) + 1
                    )
                
                return True
            
            return False
            
        except (ConnectionError, TimeoutError) as e:
            self._metrics.timeouts += 1
            self._metrics.errors += 1
            logger.error(f"Redis Cluster connection error for key {cache_key}: {e}")
            return False
            
        except Exception as e:
            self._metrics.errors += 1
            logger.error(f"Redis Cluster set error for key {cache_key}: {e}")
            return False
    
    async def close(self):
        """Close Redis Cluster connection gracefully"""



        try:
            if self._cluster:
                await self._cluster.close()
            
            logger.info("Redis Cluster connection closed gracefully")
            
        except Exception as e:
            logger.error(f"Error closing Redis Cluster connection: {e}")

# Factory functions for easy instantiation
async def create_redis_cache(config: RedisConfig) -> RedisCache:
    """Create and connect Redis cache instance"""
    cache = RedisCache(config)
    await cache.connect()
    return cache

async def create_redis_cluster_cache(
    config: RedisConfig, 
    startup_nodes: List[Dict[str, Any]]
) -> RedisClusterCache:
    """Create and connect Redis Cluster cache instance"""
    cache = RedisClusterCache(config, startup_nodes)
    await cache.connect()
    return cache

# Global cache instances for IA Influencer Agent
_redis_cache_instance: Optional[RedisCache] = None
_redis_cluster_cache_instance: Optional[RedisClusterCache] = None

async def get_redis_cache() -> RedisCache:
    """Get or create global Redis cache instance"""
    global _redis_cache_instance
    
    if _redis_cache_instance is None:
        config = RedisConfig()
        _redis_cache_instance = await create_redis_cache(config)
    
    return _redis_cache_instance

async def get_redis_cluster_cache(startup_nodes: List[Dict[str, Any]]) -> RedisClusterCache:
    """Get or create global Redis Cluster cache instance"""
    global _redis_cluster_cache_instance
    
    if _redis_cluster_cache_instance is None:
        config = RedisConfig()
        _redis_cluster_cache_instance = await create_redis_cluster_cache(config, startup_nodes)
    
    return _redis_cluster_cache_instance
