"""Redis Cache Configuration for IA-Influencer Agent Platform
==========================================================

Enterprise-grade Redis configuration and connection management
for high-performance caching in multi-tenant environment.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA-Influencer Agent + Content Protection Platform
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps

Copyright Notice:
This code is the intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution of this code
without explicit written permission from the author is strictly prohibited.

Contact: mlaiel@live.de for licensing inquiries.
"""import ssl
from typing import Dict, Optional, List, Any
from dataclasses import dataclass, field
from enum import Enum
import redis
from redis.sentinel import Sentinel
from redis.connection import ConnectionPool
from pydantic import BaseModel, validator


class RedisMode(str, Enum):
    """Redis deployment modes"""    STANDALONE = "standalone"
    CLUSTER = "cluster"
    SENTINEL = "sentinel"
    

class RedisCompressionType(str, Enum):
    """Redis compression algorithms"""    GZIP = "gzip"
    LZ4 = "lz4"
    ZSTD = "zstd"
    NONE = "none"


@dataclass
class RedisConnectionConfig:
    """Redis connection configuration"""    host: str = "localhost"
    port: int = 6379
    db: int = 0
    password: Optional[str] = None
    username: Optional[str] = None
    ssl_enabled: bool = False
    ssl_cert_reqs: str = "required"
    ssl_ca_certs: Optional[str] = None
    ssl_certfile: Optional[str] = None
    ssl_keyfile: Optional[str] = None
    socket_timeout: float = 30.0
    socket_connect_timeout: float = 30.0
    socket_keepalive: bool = True
    socket_keepalive_options: Dict[str, int] = field(default_factory=dict)
    health_check_interval: int = 30
    retry_on_timeout: bool = True
    encoding: str = "utf-8"
    decode_responses: bool = True


@dataclass
class RedisPoolConfig:
    """Redis connection pool configuration"""    max_connections: int = 100
    connection_pool_class: type = ConnectionPool
    connection_pool_class_kwargs: Dict[str, Any] = field(default_factory=dict)
    socket_keepalive: bool = True
    socket_keepalive_options: Dict[str, int] = field(default_factory=dict)


@dataclass
class RedisSentinelConfig:
    """Redis Sentinel configuration for high availability"""    sentinels: List[tuple] = field(default_factory=list)
    service_name: str = "mymaster"
    sentinel_kwargs: Dict[str, Any] = field(default_factory=dict)
    password: Optional[str] = None
    socket_timeout: float = 0.1
    socket_connect_timeout: float = 0.1


@dataclass
class RedisClusterConfig:
    """Redis Cluster configuration"""    startup_nodes: List[Dict[str, Any]] = field(default_factory=list)
    max_connections: int = 32
    max_connections_per_node: int = 50
    readonly_mode: bool = False
    decode_responses: bool = True
    health_check_interval: int = 30
    cluster_require_full_coverage: bool = True


class RedisCacheConfig(BaseModel):
    """    Comprehensive Redis cache configuration for enterprise deployment
    """    
    # Connection configuration
    connection: RedisConnectionConfig = RedisConnectionConfig()
    pool: RedisPoolConfig = RedisPoolConfig()
    
    # Deployment mode
    mode: RedisMode = RedisMode.STANDALONE
    sentinel: Optional[RedisSentinelConfig] = None
    cluster: Optional[RedisClusterConfig] = None
    
    # Cache behavior
    default_ttl: int = 3600  # 1 hour
    max_ttl: int = 86400  # 24 hours
    key_prefix: str = "ia_agent:"
    serializer: str = "json"  # json, pickle, msgpack
    compression: RedisCompressionType = RedisCompressionType.NONE
    compression_threshold: int = 1024  # bytes
    
    # Performance settings
    pipeline_size: int = 1000
    batch_size: int = 100
    async_enabled: bool = True
    
    # Multi-tenant support
    tenant_isolation: bool = True
    tenant_key_pattern: str = "{tenant_id}:{key}"
    
    # Monitoring and metrics
    enable_metrics: bool = True
    slow_log_threshold: float = 0.1  # seconds
    track_memory_usage: bool = True
    
    # Security
    auth_enabled: bool = True
    acl_enabled: bool = False
    allowed_commands: Optional[List[str]] = None
    blocked_commands: List[str] = field(default_factory=lambda: ["FLUSHALL", "FLUSHDB", "CONFIG"])
    
    # Backup and persistence
    persistence_enabled: bool = True
    backup_interval: int = 3600  # seconds
    backup_retention_days: int = 7
    
    class Config:
        use_enum_values = True
        validate_assignment = True
    
    @validator('default_ttl')
    def validate_ttl(cls, v):
        if v <= 0:
            raise ValueError("TTL must be positive")
        return v
    
    @validator('key_prefix')
    def validate_key_prefix(cls, v):
        if not v.endswith(':'):
            return f"{v}:"
        return v
    
    def get_redis_client(self) -> redis.Redis:
        """        Create and return configured Redis client
        """        if self.mode == RedisMode.STANDALONE:
            return self._create_standalone_client()
        elif self.mode == RedisMode.SENTINEL:
            return self._create_sentinel_client()
        elif self.mode == RedisMode.CLUSTER:
            return self._create_cluster_client()
        else:
            raise ValueError(f"Unsupported Redis mode: {self.mode}")
    
    def _create_standalone_client(self) -> redis.Redis:
        """Create standalone Redis client"""        connection_kwargs = {
            'host': self.connection.host,
            'port': self.connection.port,
            'db': self.connection.db,
            'password': self.connection.password,
            'username': self.connection.username,
            'socket_timeout': self.connection.socket_timeout,
            'socket_connect_timeout': self.connection.socket_connect_timeout,
            'socket_keepalive': self.connection.socket_keepalive,
            'socket_keepalive_options': self.connection.socket_keepalive_options,
            'health_check_interval': self.connection.health_check_interval,
            'retry_on_timeout': self.connection.retry_on_timeout,
            'encoding': self.connection.encoding,
            'decode_responses': self.connection.decode_responses,
            'max_connections': self.pool.max_connections
        }
        
        if self.connection.ssl_enabled:
            ssl_context = ssl.create_default_context()
            if self.connection.ssl_cert_reqs == "none":
                ssl_context.check_hostname = False
                ssl_context.verify_mode = ssl.CERT_NONE
            
            connection_kwargs.update({
                'ssl': True,
                'ssl_context': ssl_context,
                'ssl_cert_reqs': getattr(ssl, f"CERT_{self.connection.ssl_cert_reqs.upper()}"),
                'ssl_ca_certs': self.connection.ssl_ca_certs,
                'ssl_certfile': self.connection.ssl_certfile,
                'ssl_keyfile': self.connection.ssl_keyfile
            })
        
        return redis.Redis(**connection_kwargs)
    
    def _create_sentinel_client(self) -> redis.Redis:
        """Create Redis client with Sentinel support"""        if not self.sentinel:
            raise ValueError("Sentinel configuration required for sentinel mode")
        
        sentinel = Sentinel(
            self.sentinel.sentinels,
            socket_timeout=self.sentinel.socket_timeout,
            socket_connect_timeout=self.sentinel.socket_connect_timeout,
            **self.sentinel.sentinel_kwargs
        )
        
        return sentinel.master_for(
            self.sentinel.service_name,
            password=self.sentinel.password,
            db=self.connection.db
        )
    
    def _create_cluster_client(self) -> redis.RedisCluster:
        """Create Redis Cluster client"""        if not self.cluster:
            raise ValueError("Cluster configuration required for cluster mode")
        
        from redis.cluster import RedisCluster
        
        return RedisCluster(
            startup_nodes=self.cluster.startup_nodes,
            max_connections=self.cluster.max_connections,
            max_connections_per_node=self.cluster.max_connections_per_node,
            readonly_mode=self.cluster.readonly_mode,
            decode_responses=self.cluster.decode_responses,
            health_check_interval=self.cluster.health_check_interval,
            cluster_require_full_coverage=self.cluster.cluster_require_full_coverage,
            password=self.connection.password
        )
    
    def generate_tenant_key(self, tenant_id: str, key: str) -> str:
        """Generate tenant-isolated cache key"""        if self.tenant_isolation:
            return f"{self.key_prefix}{tenant_id}:{key}"
        return f"{self.key_prefix}{key}"
    
    def get_connection_info(self) -> Dict[str, Any]:
        """Get connection information for monitoring"""        return {
            "mode": self.mode,
            "host": self.connection.host,
            "port": self.connection.port,
            "database": self.connection.db,
            "ssl_enabled": self.connection.ssl_enabled,
            "pool_max_connections": self.pool.max_connections,
            "default_ttl": self.default_ttl,
            "compression": self.compression,
            "tenant_isolation": self.tenant_isolation
        }


# Default configurations for different environments
DEVELOPMENT_CONFIG = RedisCacheConfig(
    connection=RedisConnectionConfig(
        host="localhost",
        port=6379,
        db=0
    ),
    default_ttl=1800,  # 30 minutes
    enable_metrics=True,
    auth_enabled=False
)

PRODUCTION_CONFIG = RedisCacheConfig(
    connection=RedisConnectionConfig(
        host="redis-cluster.internal",
        port=6379,
        ssl_enabled=True,
        socket_keepalive=True,
        health_check_interval=30
    ),
    mode=RedisMode.CLUSTER,
    default_ttl=3600,  # 1 hour
    max_ttl=86400,  # 24 hours
    compression=RedisCompressionType.LZ4,
    compression_threshold=512,
    enable_metrics=True,
    auth_enabled=True,
    persistence_enabled=True
)

TESTING_CONFIG = RedisCacheConfig(
    connection=RedisConnectionConfig(
        host="localhost",
        port=6379,
        db=15  # Separate database for tests
    ),
    default_ttl=300,  # 5 minutes
    enable_metrics=False,
    auth_enabled=False,
    persistence_enabled=False
)
