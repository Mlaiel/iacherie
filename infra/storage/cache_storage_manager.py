"""
Cache Storage Manager module
Enterprise implementation for Ainflue platform
"""

# Ainflue Infrastructure Module
# =============================
# 
# Enterprise-grade Cache Storage Management for Multi-Cloud Infrastructure
# Advanced caching strategies with performance optimization and scalability
#
# Author: Fahed Mlaiel <mlaiel@live.de>
# Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
#
# ⚠️  PROPRIETARY SOFTWARE - UNAUTHORIZED USE STRICTLY PROHIBITED ⚠️

import asyncio
import json
import logging
import hashlib
import pickle
import gzip
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set, Tuple, Union
from enum import Enum
import redis
import boto3
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient
from google.cloud import storage as gcp_storage
from google.cloud import redis as gcp_redis
import memcache
import pymongo

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CacheType(Enum):
    """Cache storage types."""
    MEMORY = "memory"
    REDIS = "redis"
    MEMCACHED = "memcached"
    DISTRIBUTED = "distributed"
    CDN = "cdn"
    DATABASE = "database"

class CachePolicy(Enum):
    """Cache eviction policies."""
    LRU = "lru"  # Least Recently Used
    LFU = "lfu"  # Least Frequently Used
    FIFO = "fifo"  # First In, First Out
    TTL = "ttl"  # Time To Live
    WRITE_THROUGH = "write_through"
    WRITE_BACK = "write_back"
    WRITE_AROUND = "write_around"

class CacheStatus(Enum):
    """Cache status."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    DEGRADED = "degraded"
    MAINTENANCE = "maintenance"
    ERROR = "error"

@dataclass
class CacheConfiguration:
    """Cache configuration settings."""
    cache_type: CacheType
    name: str
    capacity_mb: int
    ttl_seconds: int
    eviction_policy: CachePolicy
    compression_enabled: bool = True
    encryption_enabled: bool = True
    replication_factor: int = 1
    sharding_enabled: bool = False
    monitoring_enabled: bool = True
    backup_enabled: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class CacheMetrics:
    """Cache performance metrics."""
    cache_name: str
    hit_rate: float
    miss_rate: float
    total_requests: int
    cache_size_mb: float
    memory_usage_percent: float
    latency_avg_ms: float
    latency_p95_ms: float
    evictions: int
    errors: int
    timestamp: datetime = field(default_factory=datetime.utcnow)

@dataclass
class CacheEntry:
    """Cache entry with metadata."""
    key: str
    value: Any
    created_at: datetime
    accessed_at: datetime
    access_count: int = 0
    size_bytes: int = 0
    ttl_seconds: Optional[int] = None
    tags: Set[str] = field(default_factory=set)
    metadata: Dict[str, Any] = field(default_factory=dict)

class CacheStorageManager:
    """
    Enterprise-grade cache storage management system.
    
    Provides comprehensive caching across multiple storage tiers with
    intelligent eviction, performance optimization, and multi-cloud support.
    """
    
    def __init__(self, config -> None: Dict[str, Any]) -> None:
        """Initialize cache storage manager."""
        self.config = config
        self.cache_instances = {}
        self.cache_configs = {}
        self.cache_metrics = {}
        self.cache_entries = {}
        
        # Cloud clients
        self.aws_clients = {}
        self.azure_clients = {}
        self.gcp_clients = {}
        
        # Cache backends
        self.redis_clients = {}
        self.memcached_clients = {}
        self.memory_cache = {}
        
        self._initialize_cloud_clients()
        self._initialize_cache_backends()
        self._setup_default_caches()
    
    def _initialize_cloud_clients(self) -> None:
        """Initialize cloud provider clients."""
        try:
            # AWS clients
            if self.config.get('aws', {}).get('enabled', False):
                session = boto3.Session(
                    aws_access_key_id=self.config['aws'].get('access_key'),
                    aws_secret_access_key=self.config['aws'].get('secret_key'),
                    region_name=self.config['aws'].get('region', 'us-east-1')
                )
                
                self.aws_clients = {
                    'elasticache': session.client('elasticache'),
                    'cloudfront': session.client('cloudfront'),
                    'dynamodb': session.client('dynamodb'),
                    's3': session.client('s3'),
                    'cloudwatch': session.client('cloudwatch')
                }
            
            # Azure clients
            if self.config.get('azure', {}).get('enabled', False):
                credential = DefaultAzureCredential()
                
                self.azure_clients = {
                    'blob': BlobServiceClient(
                        account_url=f"https://{self.config['azure']['storage_account']}.blob.core.windows.net",
                        credential=credential
                    )
                }
            
            # GCP clients
            if self.config.get('gcp', {}).get('enabled', False):
                self.gcp_clients = {
                    'storage': gcp_storage.Client(),
                    'redis': gcp_redis.CloudRedisClient()
                }
                
        except Exception as e:
            logger.error(f"Failed to initialize cloud clients: {e}")
    
    def _initialize_cache_backends(self) -> None:
        """Initialize cache backend connections."""
        try:
            # Redis connections
            redis_configs = self.config.get('redis', {})
            for name, config in redis_configs.items():
                try:
                    redis_client = redis.Redis(
                        host=config.get('host', 'localhost'),
                        port=config.get('port', 6379),
                        password=config.get('password'),
                        db=config.get('db', 0),
                        decode_responses=True,
                        socket_timeout=config.get('timeout', 5),
                        socket_connect_timeout=config.get('connect_timeout', 5),
                        retry_on_timeout=True,
                        health_check_interval=30
                    )
                    
                    # Test connection
                    redis_client.ping()
                    self.redis_clients[name] = redis_client
                    logger.info(f"Connected to Redis instance: {name}")
                    
                except Exception as e:
                    logger.error(f"Failed to connect to Redis {name}: {e}")
            
            # Memcached connections
            memcached_configs = self.config.get('memcached', {})
            for name, config in memcached_configs.items():
                try:
                    mc_client = memcache.Client([
                        f"{config.get('host', 'localhost')}:{config.get('port', 11211)}"
                    ])
                    
                    # Test connection
                    mc_client.set("test", "value", time=1)
                    self.memcached_clients[name] = mc_client
                    logger.info(f"Connected to Memcached instance: {name}")
                    
                except Exception as e:
                    logger.error(f"Failed to connect to Memcached {name}: {e}")
                    
        except Exception as e:
            logger.error(f"Failed to initialize cache backends: {e}")
    
    def _setup_default_caches(self) -> None:
        """Setup default cache configurations."""
        try:
            default_configs = [
                CacheConfiguration(
                    cache_type=CacheType.MEMORY,
                    name="session_cache",
                    capacity_mb=512,
                    ttl_seconds=3600,
                    eviction_policy=CachePolicy.LRU,
                    compression_enabled=False,
                    encryption_enabled=True
                ),
                CacheConfiguration(
                    cache_type=CacheType.REDIS,
                    name="api_cache",
                    capacity_mb=2048,
                    ttl_seconds=1800,
                    eviction_policy=CachePolicy.LRU,
                    replication_factor=2
                ),
                CacheConfiguration(
                    cache_type=CacheType.DISTRIBUTED,
                    name="content_cache",
                    capacity_mb=10240,
                    ttl_seconds=7200,
                    eviction_policy=CachePolicy.LFU,
                    sharding_enabled=True,
                    replication_factor=3
                ),
                CacheConfiguration(
                    cache_type=CacheType.CDN,
                    name="static_assets",
                    capacity_mb=51200,
                    ttl_seconds=86400,
                    eviction_policy=CachePolicy.TTL
                )
            ]
            
            for config in default_configs:
                self.cache_configs[config.name] = config
                self.cache_entries[config.name] = {}
                self.cache_metrics[config.name] = CacheMetrics(
                    cache_name=config.name,
                    hit_rate=0.0,
                    miss_rate=0.0,
                    total_requests=0,
                    cache_size_mb=0.0,
                    memory_usage_percent=0.0,
                    latency_avg_ms=0.0,
                    latency_p95_ms=0.0,
                    evictions=0,
                    errors=0
                )
            
            logger.info(f"Setup {len(default_configs)} default cache configurations")
            
        except Exception as e:
            logger.error(f"Failed to setup default caches: {e}")
    
    async def create_cache(self, config: CacheConfiguration) -> bool:
        """Create a new cache instance."""
        try:
            if config.name in self.cache_configs:
                raise ValueError(f"Cache {config.name} already exists")
            
            # Create cache based on type
            if config.cache_type == CacheType.REDIS:
                success = await self._create_redis_cache(config)
            elif config.cache_type == CacheType.MEMCACHED:
                success = await self._create_memcached_cache(config)
            elif config.cache_type == CacheType.MEMORY:
                success = await self._create_memory_cache(config)
            elif config.cache_type == CacheType.DISTRIBUTED:
                success = await self._create_distributed_cache(config)
            elif config.cache_type == CacheType.CDN:
                success = await self._create_cdn_cache(config)
            else:
                raise ValueError(f"Unsupported cache type: {config.cache_type}")
            
            if success:
                self.cache_configs[config.name] = config
                self.cache_entries[config.name] = {}
                self.cache_metrics[config.name] = CacheMetrics(
                    cache_name=config.name,
                    hit_rate=0.0,
                    miss_rate=0.0,
                    total_requests=0,
                    cache_size_mb=0.0,
                    memory_usage_percent=0.0,
                    latency_avg_ms=0.0,
                    latency_p95_ms=0.0,
                    evictions=0,
                    errors=0
                )
                
                logger.info(f"Created cache: {config.name} ({config.cache_type.value})")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to create cache: {e}")
            return False
    
    async def _create_redis_cache(self, config: CacheConfiguration) -> bool:
        """Create Redis cache."""
        try:
            # If using cloud Redis, create cluster
            if self.aws_clients.get('elasticache'):
                return await self._create_aws_redis_cluster(config)
            elif self.gcp_clients.get('redis'):
                return await self._create_gcp_redis_instance(config)
            else:
                # Use existing Redis connection
                if 'default' in self.redis_clients:
                    return True
                else:
                    logger.warning("No Redis connection available")
                    return False
                    
        except Exception as e:
            logger.error(f"Failed to create Redis cache: {e}")
            return False
    
    async def _create_aws_redis_cluster(self, config: CacheConfiguration) -> bool:
        """Create AWS ElastiCache Redis cluster."""
        try:
            elasticache_client = self.aws_clients['elasticache']
            
            # Determine node type based on capacity
            if config.capacity_mb <= 1024:
                node_type = 'cache.t3.micro'
            elif config.capacity_mb <= 4096:
                node_type = 'cache.t3.small'
            elif config.capacity_mb <= 8192:
                node_type = 'cache.m5.large'
            else:
                node_type = 'cache.m5.xlarge'
            
            cluster_params = {
                'CacheClusterId': f"ainflue-{config.name}",
                'CacheNodeType': node_type,
                'Engine': 'redis',
                'NumCacheNodes': config.replication_factor,
                'SecurityGroupIds': self.config.get('aws', {}).get('security_groups', []),
                'SubnetGroupName': self.config.get('aws', {}).get('subnet_group'),
                'Tags': [
                    {'Key': 'Name', 'Value': config.name},
                    {'Key': 'Environment', 'Value': self.config.get('environment', 'production')},
                    {'Key': 'Application', 'Value': 'ainflue'}
                ]
            }
            
            # Create cluster
            response = elasticache_client.create_cache_cluster(**cluster_params)
            
            logger.info(f"Created AWS Redis cluster: {config.name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create AWS Redis cluster: {e}")
            return False
    
    async def _create_gcp_redis_instance(self, config: CacheConfiguration) -> bool:
        """Create GCP Cloud Redis instance."""
        try:
            redis_client = self.gcp_clients['redis']
            project_id = self.config['gcp']['project_id']
            region = self.config['gcp'].get('region', 'us-central1')
            
            # Determine memory size
            memory_size_gb = max(1, config.capacity_mb // 1024)
            
            instance = {
                'tier': 'STANDARD_HA' if config.replication_factor > 1 else 'BASIC',
                'memory_size_gb': memory_size_gb,
                'redis_version': 'REDIS_6_X',
                'display_name': config.name,
                'labels': {
                    'environment': self.config.get('environment', 'production'),
                    'application': 'ainflue'
                }
            }
            
            parent = f"projects/{project_id}/locations/{region}"
            instance_id = f"ainflue-{config.name}"
            
            operation = redis_client.create_instance(
                parent=parent,
                instance_id=instance_id,
                instance=instance
            )
            
            logger.info(f"Created GCP Redis instance: {config.name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create GCP Redis instance: {e}")
            return False
    
    async def _create_memcached_cache(self, config: CacheConfiguration) -> bool:
        """Create Memcached cache."""
        try:
            # Use existing Memcached connection
            if 'default' in self.memcached_clients:
                return True
            else:
                logger.warning("No Memcached connection available")
                return False
                
        except Exception as e:
            logger.error(f"Failed to create Memcached cache: {e}")
            return False
    
    async def _create_memory_cache(self, config: CacheConfiguration) -> bool:
        """Create in-memory cache."""
        try:
            self.memory_cache[config.name] = {}
            return True
            
        except Exception as e:
            logger.error(f"Failed to create memory cache: {e}")
            return False
    
    async def _create_distributed_cache(self, config: CacheConfiguration) -> bool:
        """Create distributed cache across multiple nodes."""
        try:
            # For distributed cache, we would typically use Redis Cluster
            # or a combination of Redis instances
            return await self._create_redis_cache(config)
            
        except Exception as e:
            logger.error(f"Failed to create distributed cache: {e}")
            return False
    
    async def _create_cdn_cache(self, config: CacheConfiguration) -> bool:
        """Create CDN cache configuration."""
        try:
            # Configure CDN caching behavior
            if self.aws_clients.get('cloudfront'):
                return await self._configure_cloudfront_cache(config)
            else:
                logger.info(f"CDN cache configuration stored: {config.name}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to create CDN cache: {e}")
            return False
    
    async def _configure_cloudfront_cache(self, config: CacheConfiguration) -> bool:
        """Configure AWS CloudFront cache behavior."""
        try:
            cloudfront_client = self.aws_clients['cloudfront']
            
            # Get existing distribution
            distributions = cloudfront_client.list_distributions()
            
            if distributions['DistributionList']['Items']:
                # Update existing distribution with new cache behavior
                # Implementation would modify cache behaviors
                logger.info(f"Would configure CloudFront cache for: {config.name}")
                return True
            else:
                logger.warning("No CloudFront distribution found")
                return False
                
        except Exception as e:
            logger.error(f"Failed to configure CloudFront cache: {e}")
            return False
    
    async def set(self,
                 cache_name: str,
                 key: str,
                 value: Any,
                 ttl: Optional[int] = None,
                 tags: Optional[Set[str]] = None) -> bool:
        """Set value in cache."""
        try:
            if cache_name not in self.cache_configs:
                raise ValueError(f"Cache not found: {cache_name}")
            
            config = self.cache_configs[cache_name]
            
            # Use config TTL if not specified
            if ttl is None:
                ttl = config.ttl_seconds
            
            # Serialize and possibly compress value
            serialized_value = await self._serialize_value(value, config)
            
            # Store in appropriate backend
            success = False
            if config.cache_type == CacheType.REDIS:
                success = await self._set_redis(cache_name, key, serialized_value, ttl)
            elif config.cache_type == CacheType.MEMCACHED:
                success = await self._set_memcached(cache_name, key, serialized_value, ttl)
            elif config.cache_type == CacheType.MEMORY:
                success = await self._set_memory(cache_name, key, serialized_value, ttl)
            elif config.cache_type in [CacheType.DISTRIBUTED, CacheType.CDN]:
                success = await self._set_distributed(cache_name, key, serialized_value, ttl)
            
            # Update cache entry metadata
            if success:
                entry = CacheEntry(
                    key=key,
                    value=value,
                    created_at=datetime.utcnow(),
                    accessed_at=datetime.utcnow(),
                    access_count=1,
                    size_bytes=len(serialized_value) if isinstance(serialized_value, bytes) else len(str(serialized_value)),
                    ttl_seconds=ttl,
                    tags=tags or set()
                )
                self.cache_entries[cache_name][key] = entry
                
                # Update metrics
                await self._update_cache_metrics(cache_name, 'set', True)
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to set cache value: {e}")
            await self._update_cache_metrics(cache_name, 'set', False)
            return False
    
    async def get(self, cache_name: str, key: str) -> Optional[Any]:
        """Get value from cache."""
        try:
            if cache_name not in self.cache_configs:
                raise ValueError(f"Cache not found: {cache_name}")
            
            config = self.cache_configs[cache_name]
            
            # Get from appropriate backend
            serialized_value = None
            if config.cache_type == CacheType.REDIS:
                serialized_value = await self._get_redis(cache_name, key)
            elif config.cache_type == CacheType.MEMCACHED:
                serialized_value = await self._get_memcached(cache_name, key)
            elif config.cache_type == CacheType.MEMORY:
                serialized_value = await self._get_memory(cache_name, key)
            elif config.cache_type in [CacheType.DISTRIBUTED, CacheType.CDN]:
                serialized_value = await self._get_distributed(cache_name, key)
            
            if serialized_value is not None:
                # Deserialize value
                value = await self._deserialize_value(serialized_value, config)
                
                # Update cache entry metadata
                if key in self.cache_entries[cache_name]:
                    entry = self.cache_entries[cache_name][key]
                    entry.accessed_at = datetime.utcnow()
                    entry.access_count += 1
                
                # Update metrics
                await self._update_cache_metrics(cache_name, 'get', True)
                return value
            else:
                # Cache miss
                await self._update_cache_metrics(cache_name, 'get', False)
                return None
                
        except Exception as e:
            logger.error(f"Failed to get cache value: {e}")
            await self._update_cache_metrics(cache_name, 'get', False)
            return None
    
    async def delete(self, cache_name: str, key: str) -> bool:
        """Delete value from cache."""
        try:
            if cache_name not in self.cache_configs:
                raise ValueError(f"Cache not found: {cache_name}")
            
            config = self.cache_configs[cache_name]
            
            # Delete from appropriate backend
            success = False
            if config.cache_type == CacheType.REDIS:
                success = await self._delete_redis(cache_name, key)
            elif config.cache_type == CacheType.MEMCACHED:
                success = await self._delete_memcached(cache_name, key)
            elif config.cache_type == CacheType.MEMORY:
                success = await self._delete_memory(cache_name, key)
            elif config.cache_type in [CacheType.DISTRIBUTED, CacheType.CDN]:
                success = await self._delete_distributed(cache_name, key)
            
            # Remove from cache entries
            if success and key in self.cache_entries[cache_name]:
                del self.cache_entries[cache_name][key]
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to delete cache value: {e}")
            return False
    
    async def _serialize_value(self, value: Any, config: CacheConfiguration) -> bytes:
        """Serialize and optionally compress value."""
        try:
            # Serialize using pickle
            serialized = pickle.dumps(value)
            
            # Compress if enabled
            if config.compression_enabled:
                serialized = gzip.compress(serialized)
            
            # Encrypt if enabled
            if config.encryption_enabled:
                # Simple encryption for demo (use proper encryption in production)
                serialized = self._encrypt_data(serialized)
            
            return serialized
            
        except Exception as e:
            logger.error(f"Failed to serialize value: {e}")
            raise
    
    async def _deserialize_value(self, data: bytes, config: CacheConfiguration) -> Any:
        """Deserialize and optionally decompress value."""
        try:
            # Decrypt if enabled
            if config.encryption_enabled:
                data = self._decrypt_data(data)
            
            # Decompress if enabled
            if config.compression_enabled:
                data = gzip.decompress(data)
            
            # Deserialize using pickle
            value = pickle.loads(data)
            
            return value
            
        except Exception as e:
            logger.error(f"Failed to deserialize value: {e}")
            raise
    
    def _encrypt_data(self, data: bytes) -> bytes:
        """Simple encryption (use proper encryption in production)."""
        # This is a placeholder - use proper encryption libraries
        return data
    
    def _decrypt_data(self, data: bytes) -> bytes:
        """Simple decryption (use proper encryption in production)."""
        # This is a placeholder - use proper encryption libraries
        return data
    
    async def _set_redis(self, cache_name: str, key: str, value: bytes, ttl: int) -> bool:
        """Set value in Redis."""
        try:
            redis_client = self.redis_clients.get('default')
            if not redis_client:
                return False
            
            # Use cache name as key prefix
            redis_key = f"{cache_name}:{key}"
            
            if ttl > 0:
                return redis_client.setex(redis_key, ttl, value)
            else:
                return redis_client.set(redis_key, value)
                
        except Exception as e:
            logger.error(f"Failed to set Redis value: {e}")
            return False
    
    async def _get_redis(self, cache_name: str, key: str) -> Optional[bytes]:
        """Get value from Redis."""
        try:
            redis_client = self.redis_clients.get('default')
            if not redis_client:
                return None
            
            redis_key = f"{cache_name}:{key}"
            return redis_client.get(redis_key)
            
        except Exception as e:
            logger.error(f"Failed to get Redis value: {e}")
            return None
    
    async def _delete_redis(self, cache_name: str, key: str) -> bool:
        """Delete value from Redis."""
        try:
            redis_client = self.redis_clients.get('default')
            if not redis_client:
                return False
            
            redis_key = f"{cache_name}:{key}"
            return redis_client.delete(redis_key) > 0
            
        except Exception as e:
            logger.error(f"Failed to delete Redis value: {e}")
            return False
    
    async def _set_memcached(self, cache_name: str, key: str, value: bytes, ttl: int) -> bool:
        """Set value in Memcached."""
        try:
            mc_client = self.memcached_clients.get('default')
            if not mc_client:
                return False
            
            mc_key = f"{cache_name}:{key}"
            return mc_client.set(mc_key, value, time=ttl)
            
        except Exception as e:
            logger.error(f"Failed to set Memcached value: {e}")
            return False
    
    async def _get_memcached(self, cache_name: str, key: str) -> Optional[bytes]:
        """Get value from Memcached."""
        try:
            mc_client = self.memcached_clients.get('default')
            if not mc_client:
                return None
            
            mc_key = f"{cache_name}:{key}"
            return mc_client.get(mc_key)
            
        except Exception as e:
            logger.error(f"Failed to get Memcached value: {e}")
            return None
    
    async def _delete_memcached(self, cache_name: str, key: str) -> bool:
        """Delete value from Memcached."""
        try:
            mc_client = self.memcached_clients.get('default')
            if not mc_client:
                return False
            
            mc_key = f"{cache_name}:{key}"
            return mc_client.delete(mc_key) == 1
            
        except Exception as e:
            logger.error(f"Failed to delete Memcached value: {e}")
            return False
    
    async def _set_memory(self, cache_name: str, key: str, value: bytes, ttl: int) -> bool:
        """Set value in memory cache."""
        try:
            if cache_name not in self.memory_cache:
                self.memory_cache[cache_name] = {}
            
            expire_time = datetime.utcnow() + timedelta(seconds=ttl) if ttl > 0 else None
            self.memory_cache[cache_name][key] = (value, expire_time)
            return True
            
        except Exception as e:
            logger.error(f"Failed to set memory value: {e}")
            return False
    
    async def _get_memory(self, cache_name: str, key: str) -> Optional[bytes]:
        """Get value from memory cache."""
        try:
            if cache_name not in self.memory_cache or key not in self.memory_cache[cache_name]:
                return None
            
            value, expire_time = self.memory_cache[cache_name][key]
            
            # Check if expired
            if expire_time and expire_time < datetime.utcnow():
                del self.memory_cache[cache_name][key]
                return None
            
            return value
            
        except Exception as e:
            logger.error(f"Failed to get memory value: {e}")
            return None
    
    async def _delete_memory(self, cache_name: str, key: str) -> bool:
        """Delete value from memory cache."""
        try:
            if cache_name in self.memory_cache and key in self.memory_cache[cache_name]:
                del self.memory_cache[cache_name][key]
                return True
            return False
            
        except Exception as e:
            logger.error(f"Failed to delete memory value: {e}")
            return False
    
    async def _set_distributed(self, cache_name: str, key: str, value: bytes, ttl: int) -> bool:
        """Set value in distributed cache."""
        # For distributed cache, use Redis by default
        return await self._set_redis(cache_name, key, value, ttl)
    
    async def _get_distributed(self, cache_name: str, key: str) -> Optional[bytes]:
        """Get value from distributed cache."""
        # For distributed cache, use Redis by default
        return await self._get_redis(cache_name, key)
    
    async def _delete_distributed(self, cache_name: str, key: str) -> bool:
        """Delete value from distributed cache."""
        # For distributed cache, use Redis by default
        return await self._delete_redis(cache_name, key)
    
    async def _update_cache_metrics(self, cache_name -> None: str, operation -> None: str, success -> None: bool) -> None:
        """Update cache performance metrics."""
        try:
            if cache_name not in self.cache_metrics:
                return
            
            metrics = self.cache_metrics[cache_name]
            metrics.total_requests += 1
            
            if operation == 'get':
                if success:
                    metrics.hit_rate = (metrics.hit_rate * (metrics.total_requests - 1) + 1) / metrics.total_requests
                    metrics.miss_rate = 1 - metrics.hit_rate
                else:
                    metrics.miss_rate = (metrics.miss_rate * (metrics.total_requests - 1) + 1) / metrics.total_requests
                    metrics.hit_rate = 1 - metrics.miss_rate
            
            if not success:
                metrics.errors += 1
            
            # Update cache size
            cache_size = sum(
                entry.size_bytes for entry in self.cache_entries[cache_name].values()
            ) / (1024 * 1024)  # Convert to MB
            metrics.cache_size_mb = cache_size
            
            # Update memory usage percentage
            config = self.cache_configs[cache_name]
            metrics.memory_usage_percent = (cache_size / config.capacity_mb) * 100 if config.capacity_mb > 0 else 0
            
            metrics.timestamp = datetime.utcnow()
            
        except Exception as e:
            logger.error(f"Failed to update cache metrics: {e}")
    
    async def clear_cache(self, cache_name: str) -> bool:
        """Clear all entries from cache."""
        try:
            if cache_name not in self.cache_configs:
                raise ValueError(f"Cache not found: {cache_name}")
            
            config = self.cache_configs[cache_name]
            
            # Clear from appropriate backend
            success = False
            if config.cache_type == CacheType.REDIS:
                success = await self._clear_redis_cache(cache_name)
            elif config.cache_type == CacheType.MEMCACHED:
                success = await self._clear_memcached_cache(cache_name)
            elif config.cache_type == CacheType.MEMORY:
                success = await self._clear_memory_cache(cache_name)
            elif config.cache_type in [CacheType.DISTRIBUTED, CacheType.CDN]:
                success = await self._clear_distributed_cache(cache_name)
            
            # Clear cache entries
            if success:
                self.cache_entries[cache_name] = {}
                logger.info(f"Cleared cache: {cache_name}")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to clear cache: {e}")
            return False
    
    async def _clear_redis_cache(self, cache_name: str) -> bool:
        """Clear Redis cache entries."""
        try:
            redis_client = self.redis_clients.get('default')
            if not redis_client:
                return False
            
            # Delete all keys with cache name prefix
            pattern = f"{cache_name}:*"
            keys = redis_client.keys(pattern)
            if keys:
                redis_client.delete(*keys)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to clear Redis cache: {e}")
            return False
    
    async def _clear_memcached_cache(self, cache_name: str) -> bool:
        """Clear Memcached cache entries."""
        try:
            # Memcached doesn't have pattern matching, so we track keys
            # In production, you'd need a more sophisticated approach
            return True
            
        except Exception as e:
            logger.error(f"Failed to clear Memcached cache: {e}")
            return False
    
    async def _clear_memory_cache(self, cache_name: str) -> bool:
        """Clear memory cache entries."""
        try:
            if cache_name in self.memory_cache:
                self.memory_cache[cache_name] = {}
            return True
            
        except Exception as e:
            logger.error(f"Failed to clear memory cache: {e}")
            return False
    
    async def _clear_distributed_cache(self, cache_name: str) -> bool:
        """Clear distributed cache entries."""
        return await self._clear_redis_cache(cache_name)
    
    async def get_cache_statistics(self, cache_name: Optional[str] = None) -> Dict[str, Any]:
        """Get cache performance statistics."""
        try:
            if cache_name:
                if cache_name not in self.cache_metrics:
                    raise ValueError(f"Cache not found: {cache_name}")
                
                metrics = self.cache_metrics[cache_name]
                return {
                    "cache_name": metrics.cache_name,
                    "hit_rate": round(metrics.hit_rate, 4),
                    "miss_rate": round(metrics.miss_rate, 4),
                    "total_requests": metrics.total_requests,
                    "cache_size_mb": round(metrics.cache_size_mb, 2),
                    "memory_usage_percent": round(metrics.memory_usage_percent, 2),
                    "latency_avg_ms": round(metrics.latency_avg_ms, 2),
                    "latency_p95_ms": round(metrics.latency_p95_ms, 2),
                    "evictions": metrics.evictions,
                    "errors": metrics.errors,
                    "last_updated": metrics.timestamp.isoformat()
                }
            else:
                # Return statistics for all caches
                all_stats = {}
                for name, metrics in self.cache_metrics.items():
                    all_stats[name] = {
                        "hit_rate": round(metrics.hit_rate, 4),
                        "miss_rate": round(metrics.miss_rate, 4),
                        "total_requests": metrics.total_requests,
                        "cache_size_mb": round(metrics.cache_size_mb, 2),
                        "memory_usage_percent": round(metrics.memory_usage_percent, 2),
                        "errors": metrics.errors
                    }
                
                # Overall statistics
                total_requests = sum(m.total_requests for m in self.cache_metrics.values())
                overall_hit_rate = (
                    sum(m.hit_rate * m.total_requests for m in self.cache_metrics.values()) / total_requests
                    if total_requests > 0 else 0
                )
                
                return {
                    "overview": {
                        "total_caches": len(self.cache_metrics),
                        "total_requests": total_requests,
                        "overall_hit_rate": round(overall_hit_rate, 4),
                        "total_cache_size_mb": round(sum(m.cache_size_mb for m in self.cache_metrics.values()), 2),
                        "total_errors": sum(m.errors for m in self.cache_metrics.values())
                    },
                    "caches": all_stats
                }
                
        except Exception as e:
            logger.error(f"Failed to get cache statistics: {e}")
            raise
    
    async def optimize_cache_performance(self) -> Dict[str, List[str]]:
        """Analyze and provide cache optimization recommendations."""
        try:
            recommendations = {}
            
            for cache_name, metrics in self.cache_metrics.items():
                cache_recommendations = []
                config = self.cache_configs[cache_name]
                
                # Check hit rate
                if metrics.hit_rate < 0.8:
                    cache_recommendations.append(
                        f"Low hit rate ({metrics.hit_rate:.2%}). Consider increasing cache size or TTL."
                    )
                
                # Check memory usage
                if metrics.memory_usage_percent > 90:
                    cache_recommendations.append(
                        "High memory usage. Consider increasing cache capacity or implementing eviction."
                    )
                elif metrics.memory_usage_percent < 20:
                    cache_recommendations.append(
                        "Low memory usage. Consider reducing cache capacity to save resources."
                    )
                
                # Check error rate
                error_rate = metrics.errors / metrics.total_requests if metrics.total_requests > 0 else 0
                if error_rate > 0.01:  # More than 1% errors
                    cache_recommendations.append(
                        f"High error rate ({error_rate:.2%}). Check cache backend health."
                    )
                
                # Check cache type efficiency
                if config.cache_type == CacheType.MEMORY and metrics.cache_size_mb > 1024:
                    cache_recommendations.append(
                        "Large memory cache. Consider using Redis for better scalability."
                    )
                
                # Check TTL settings
                avg_access_count = (
                    sum(entry.access_count for entry in self.cache_entries[cache_name].values()) /
                    len(self.cache_entries[cache_name])
                    if self.cache_entries[cache_name] else 0
                )
                
                if avg_access_count < 2 and config.ttl_seconds > 3600:
                    cache_recommendations.append(
                        "Low access frequency with high TTL. Consider reducing TTL."
                    )
                
                if not cache_recommendations:
                    cache_recommendations.append("Cache performance is optimal.")
                
                recommendations[cache_name] = cache_recommendations
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Failed to optimize cache performance: {e}")
            raise

# Example usage
if __name__ == "__main__":
    # Example configuration
    config = {
        "aws": {
            "enabled": True,
            "region": "us-east-1",
            "security_groups": ["sg-12345678"],
            "subnet_group": "ainflue-cache-subnet-group"
        },
        "gcp": {
            "enabled": True,
            "project_id": "ainflue-project",
            "region": "us-central1"
        },
        "redis": {
            "default": {
                "host": "localhost",
                "port": 6379,
                "password": None,
                "db": 0
            }
        },
        "memcached": {
            "default": {
                "host": "localhost",
                "port": 11211
            }
        },
        "environment": "production"
    }
    
    async def main() -> None:
        # Initialize cache storage manager
        manager = CacheStorageManager(config)
        
        # Create custom cache
        api_cache_config = CacheConfiguration(
            cache_type=CacheType.REDIS,
            name="user_sessions",
            capacity_mb=1024,
            ttl_seconds=1800,
            eviction_policy=CachePolicy.LRU,
            compression_enabled=True,
            encryption_enabled=True,
            replication_factor=2
        )
        
        await manager.create_cache(api_cache_config)
        
        # Set some values
        await manager.set("user_sessions", "user:123", {"id": 123, "name": "John Doe"})
        await manager.set("user_sessions", "user:456", {"id": 456, "name": "Jane Smith"})
        
        # Get values
        user_data = await manager.get("user_sessions", "user:123")
        print(f"Retrieved user data: {user_data}")
        
        # Get cache statistics
        stats = await manager.get_cache_statistics("user_sessions")
        print(f"Cache hit rate: {stats['hit_rate']:.2%}")
        
        # Get optimization recommendations
        recommendations = await manager.optimize_cache_performance()
        print(f"Recommendations: {recommendations}")
    
    # Run the example
    asyncio.run(main())