"""Memcached Configuration for IA-Influencer Agent Platform
========================================================

Enterprise-grade Memcached configuration and client management
for distributed caching and session storage.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA-Influencer Agent + Content Protection Platform
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps

Copyright Notice:
This code is the intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution of this code
without explicit written permission from the author is strictly prohibited.

Contact: mlaiel@live.de for licensing inquiries.
"""from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import hashlib
import time
from pydantic import BaseModel, validator


class MemcachedHashingAlgorithm(str, Enum):
    """Memcached hashing algorithms for consistent hashing"""    CRC32 = "crc32"
    FNV1_32 = "fnv1_32"
    FNV1A_32 = "fnv1a_32"
    FNV1_64 = "fnv1_64"
    FNV1A_64 = "fnv1a_64"
    MD5 = "md5"


class MemcachedBehavior(str, Enum):
    """Memcached client behaviors"""    BINARY_PROTOCOL = "binary_protocol"
    TCP_NODELAY = "tcp_nodelay"
    KETAMA_WEIGHTED = "ketama_weighted"
    REMOVE_FAILED_SERVERS = "remove_failed_servers"
    RETRY_TIMEOUT = "retry_timeout"
    DEAD_TIMEOUT = "dead_timeout"


@dataclass
class MemcachedServerConfig:
    """Memcached server configuration"""    host: str = "localhost"
    port: int = 11211
    weight: int = 1
    
    def __str__(self) -> str:
        return f"{self.host}:{self.port}"


@dataclass
class MemcachedConnectionConfig:
    """Memcached connection configuration"""    socket_timeout: float = 3.0
    connect_timeout: float = 3.0
    receive_timeout: float = 3.0
    send_timeout: float = 3.0
    tcp_nodelay: bool = True
    buffer_requests: bool = False
    binary_protocol: bool = True
    no_block: bool = False
    max_pool_size: int = 10


@dataclass
class MemcachedFailureHandling:
    """Memcached failure handling configuration"""    retry_timeout: int = 30  # seconds
    dead_timeout: int = 30  # seconds
    failure_limit: int = 5
    remove_failed_servers: bool = True
    auto_eject_hosts: bool = True
    server_failure_counter_threshold: int = 5


class MemcachedConfig(BaseModel):
    """    Comprehensive Memcached configuration for enterprise deployment
    """    
    # Server configuration
    servers: List[MemcachedServerConfig] = field(
        default_factory=lambda: [MemcachedServerConfig()]
    )
    
    # Connection settings
    connection: MemcachedConnectionConfig = MemcachedConnectionConfig()
    
    # Hashing and distribution
    hashing_algorithm: MemcachedHashingAlgorithm = MemcachedHashingAlgorithm.KETAMA_WEIGHTED
    ketama_weighted: bool = True
    consistent_hashing: bool = True
    
    # Cache behavior
    default_ttl: int = 3600  # 1 hour
    max_ttl: int = 86400  # 24 hours
    key_prefix: str = "ia_agent:"
    
    # Serialization
    serializer: str = "pickle"  # pickle, json, msgpack
    compression_enabled: bool = True
    compression_threshold: int = 1024  # bytes
    
    # Performance settings
    pool_size: int = 10
    pool_block: bool = True
    pool_timeout: float = 10.0
    
    # Multi-tenant support
    tenant_isolation: bool = True
    tenant_key_pattern: str = "{tenant_id}:{key}"
    
    # Failure handling
    failure_handling: MemcachedFailureHandling = MemcachedFailureHandling()
    
    # Monitoring
    enable_metrics: bool = True
    stats_collection_interval: int = 60  # seconds
    track_key_statistics: bool = True
    
    # Client behaviors
    behaviors: Dict[str, Any] = field(default_factory=dict)
    
    class Config:
        use_enum_values = True
        validate_assignment = True
    
    @validator('servers')
    def validate_servers(cls, v):
        if not v:
            raise ValueError("At least one server must be configured")
        return v
    
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
    
    def get_server_list(self) -> List[str]:
        """Get list of server addresses"""        return [str(server) for server in self.servers]
    
    def get_weighted_servers(self) -> List[Tuple[str, int]]:
        """Get servers with weights for consistent hashing"""        return [(str(server), server.weight) for server in self.servers]
    
    def get_client_config(self) -> Dict[str, Any]:
        """Get configuration for memcached client"""        config = {
            'servers': self.get_server_list(),
            'binary': self.connection.binary_protocol,
            'behaviors': self._get_client_behaviors(),
            'socket_timeout': self.connection.socket_timeout,
            'connect_timeout': self.connection.connect_timeout,
            'receive_timeout': self.connection.receive_timeout,
            'send_timeout': self.connection.send_timeout,
            'no_block': self.connection.no_block,
            'tcp_nodelay': self.connection.tcp_nodelay,
            'buffer_requests': self.connection.buffer_requests
        }
        
        if self.ketama_weighted:
            config['server_weights'] = {
                str(server): server.weight for server in self.servers
            }
        
        return config
    
    def _get_client_behaviors(self) -> Dict[str, Any]:
        """Get memcached client behaviors"""        behaviors = {
            'ketama_weighted': self.ketama_weighted,
            'remove_failed_servers': self.failure_handling.remove_failed_servers,
            'retry_timeout': self.failure_handling.retry_timeout,
            'dead_timeout': self.failure_handling.dead_timeout,
            'auto_eject_hosts': self.failure_handling.auto_eject_hosts,
            'failure_limit': self.failure_handling.failure_limit,
            'tcp_nodelay': self.connection.tcp_nodelay,
            'binary_protocol': self.connection.binary_protocol
        }
        
        # Add custom behaviors
        behaviors.update(self.behaviors)
        
        return behaviors
    
    def generate_tenant_key(self, tenant_id: str, key: str) -> str:
        """Generate tenant-isolated cache key"""        if self.tenant_isolation:
            return f"{self.key_prefix}{tenant_id}:{key}"
        return f"{self.key_prefix}{key}"
    
    def hash_key(self, key: str) -> str:
        """Hash key using specified algorithm"""        if self.hashing_algorithm == MemcachedHashingAlgorithm.MD5:
            return hashlib.md5(key.encode()).hexdigest()
        elif self.hashing_algorithm == MemcachedHashingAlgorithm.CRC32:
            import zlib
            return str(zlib.crc32(key.encode()) & 0xffffffff)
        else:
            # Default to MD5 for other algorithms
            return hashlib.md5(key.encode()).hexdigest()
    
    def get_server_stats_config(self) -> Dict[str, Any]:
        """Get configuration for server statistics collection"""        return {
            'collection_interval': self.stats_collection_interval,
            'track_keys': self.track_key_statistics,
            'enable_metrics': self.enable_metrics,
            'servers': self.get_server_list()
        }
    
    def validate_connection(self) -> bool:
        """Validate connection to all configured servers"""        try:
            import pymemcache
            from pymemcache.client.base import Client
            
            for server in self.servers:
                client = Client(
                    (server.host, server.port),
                    timeout=self.connection.connect_timeout
                )
                
                # Test connection
                stats = client.stats()
                if not stats:
                    return False
                client.close()
            
            return True
            
        except Exception:
            return False
    
    def get_connection_info(self) -> Dict[str, Any]:
        """Get connection information for monitoring"""        return {
            "servers": [
                {
                    "host": server.host,
                    "port": server.port,
                    "weight": server.weight
                }
                for server in self.servers
            ],
            "hashing_algorithm": self.hashing_algorithm,
            "binary_protocol": self.connection.binary_protocol,
            "consistent_hashing": self.consistent_hashing,
            "default_ttl": self.default_ttl,
            "compression_enabled": self.compression_enabled,
            "tenant_isolation": self.tenant_isolation,
            "pool_size": self.pool_size
        }


class MemcachedPoolManager:
    """    Connection pool manager for Memcached clients
    """    
    def __init__(self, config: MemcachedConfig):
        self.config = config
        self._pool: List[Any] = []
        self._pool_lock = None
        self._init_pool()
    
    def _init_pool(self):
        """Initialize connection pool"""        try:
            import threading
            import pymemcache
            from pymemcache.client.hash import HashClient
            from pymemcache.client.base import PooledClient
            
            self._pool_lock = threading.Lock()
            
            # Create pooled clients
            for _ in range(self.config.pool_size):
                if len(self.config.servers) > 1:
                    # Use HashClient for multiple servers
                    client = HashClient(
                        servers=self.config.get_weighted_servers(),
                        **self.config.get_client_config()
                    )
                else:
                    # Use PooledClient for single server
                    server = self.config.servers[0]
                    client = PooledClient(
                        (server.host, server.port),
                        max_pool_size=self.config.connection.max_pool_size,
                        **self.config.get_client_config()
                    )
                
                self._pool.append(client)
        
        except ImportError:
            # pymemcache not available, create dummy pool
            self._pool = []
    
    def get_client(self):
        """Get client from pool"""        if not self._pool:
            return None
        
        with self._pool_lock:
            if self._pool:
                return self._pool.pop()
        
        return None
    
    def return_client(self, client):
        """Return client to pool"""        if client and len(self._pool) < self.config.pool_size:
            with self._pool_lock:
                self._pool.append(client)
    
    def close_all(self):
        """Close all pooled connections"""        with self._pool_lock:
            for client in self._pool:
                try:
                    client.close()
                except:
                    pass
            self._pool.clear()


# Default configurations for different environments
DEVELOPMENT_CONFIG = MemcachedConfig(
    servers=[MemcachedServerConfig(host="localhost", port=11211)],
    default_ttl=1800,  # 30 minutes
    enable_metrics=True,
    compression_enabled=False,
    pool_size=5
)

PRODUCTION_CONFIG = MemcachedConfig(
    servers=[
        MemcachedServerConfig(host="memcached-1.internal", port=11211, weight=3),
        MemcachedServerConfig(host="memcached-2.internal", port=11211, weight=3),
        MemcachedServerConfig(host="memcached-3.internal", port=11211, weight=2)
    ],
    hashing_algorithm=MemcachedHashingAlgorithm.KETAMA_WEIGHTED,
    default_ttl=3600,  # 1 hour
    max_ttl=86400,  # 24 hours
    compression_enabled=True,
    compression_threshold=512,
    enable_metrics=True,
    pool_size=20,
    failure_handling=MemcachedFailureHandling(
        retry_timeout=60,
        dead_timeout=60,
        failure_limit=3
    )
)

TESTING_CONFIG = MemcachedConfig(
    servers=[MemcachedServerConfig(host="localhost", port=11211)],
    default_ttl=300,  # 5 minutes
    enable_metrics=False,
    compression_enabled=False,
    pool_size=2,
    key_prefix="test:"
)
