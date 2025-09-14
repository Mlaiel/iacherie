"""Database Configuration Module - Consolidated Database Configs
==============================================================

Consolidates all database-related configurations from:
- config/database/ (22 files)
- config/cache/ (Redis-related configs)

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import os
import json
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
from urllib.parse import urlparse
import ssl
import logging

# Optional Redis imports - fail gracefully if not available
try:
    import redis
    from redis import Redis, ConnectionPool, Sentinel
    from redis.exceptions import ConnectionError, TimeoutError, RedisError
    import redis.asyncio as aioredis
    REDIS_AVAILABLE = True
except ImportError:
    # Create dummy classes for when Redis is not available
    class Redis: pass
    class ConnectionPool: pass
    class Sentinel: pass
    class ConnectionError(Exception): pass
    class TimeoutError(Exception): pass
    class RedisError(Exception): pass
    redis = None
    aioredis = None
    REDIS_AVAILABLE = False

logger = logging.getLogger(__name__)

# ===== REDIS CONFIGURATION (from config/database/redis_config.py) =====

class RedisEnvironment(Enum):
    """Redis environment configurations"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"

class RedisDeploymentType(Enum):
    """Redis deployment types"""
    STANDALONE = "standalone"
    CLUSTER = "cluster"
    SENTINEL = "sentinel"

class RedisWorkloadType(Enum):
    """Redis workload optimization types"""
    CACHE = "cache"
    SESSION = "session"
    PUBSUB = "pubsub"
    QUEUE = "queue"
    ANALYTICS = "analytics"
    REAL_TIME = "real_time"

@dataclass
class RedisCredentials:
    """Redis authentication and connection credentials"""
    host: str = "localhost"
    port: int = 6379
    password: Optional[str] = None
    username: Optional[str] = None
    ssl_enabled: bool = False
    ssl_cert_path: Optional[str] = None
    ssl_key_path: Optional[str] = None
    ssl_ca_path: Optional[str] = None
    ssl_check_hostname: bool = True
    sentinel_hosts: List[Dict[str, Union[str, int]]] = field(default_factory=list)
    sentinel_service_name: Optional[str] = None

@dataclass
class RedisPoolConfig:
    """Redis connection pool configuration"""
    max_connections: int = 50
    retry_on_timeout: bool = True
    retry_on_error: List[Exception] = field(default_factory=lambda: [ConnectionError, TimeoutError])
    health_check_interval: int = 30
    socket_connect_timeout: int = 5
    socket_timeout: int = 5
    socket_keepalive: bool = True
    socket_keepalive_options: Dict[int, int] = field(default_factory=dict)

@dataclass
class RedisCacheConfig:
    """Redis caching configuration"""
    default_ttl: int = 3600  # 1 hour
    key_prefix: str = "ia_influencer:"
    serializer: str = "json"  # json, pickle, msgpack
    compression: bool = False
    compression_threshold: int = 1024
    max_key_size: int = 1024
    max_value_size: int = 1048576  # 1MB

@dataclass
class RedisClusterConfig:
    """Redis cluster configuration"""
    startup_nodes: List[Dict[str, Union[str, int]]] = field(default_factory=list)
    max_connections_per_node: int = 50
    skip_full_coverage_check: bool = False
    decode_responses: bool = True
    cluster_error_retry_attempts: int = 3
    cluster_error_retry_delay: float = 0.25
    reinitialize_steps: int = 10

class RedisConfig:
    """
    Main Redis configuration class that handles different deployment types
    and environments with enterprise-grade features.
    """
    
    def __init__(self, 
                 deployment_type -> None: RedisDeploymentType = RedisDeploymentType.STANDALONE,
                 environment -> None: str = "development",
                 workload_type -> None: RedisWorkloadType = RedisWorkloadType.CACHE) -> None:
        
        self.deployment_type = deployment_type
        self.environment = environment
        self.workload_type = workload_type
        
        # Load configuration from environment
        self.credentials = self._load_credentials()
        self.pool_config = self._load_pool_config()
        self.cache_config = self._load_cache_config()
        self.cluster_config = self._load_cluster_config()
        
        # Initialize clients
        self._client = None
        self._async_client = None
        self._pool = None
        
    def _load_credentials(self) -> RedisCredentials:
        """Load Redis credentials from environment variables"""
        return RedisCredentials(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", 6379)),
            password=os.getenv("REDIS_PASSWORD"),
            username=os.getenv("REDIS_USERNAME"),
            ssl_enabled=os.getenv("REDIS_SSL_ENABLED", "false").lower() == "true",
            ssl_cert_path=os.getenv("REDIS_SSL_CERT_PATH"),
            ssl_key_path=os.getenv("REDIS_SSL_KEY_PATH"),
            ssl_ca_path=os.getenv("REDIS_SSL_CA_PATH"),
            sentinel_service_name=os.getenv("REDIS_SENTINEL_SERVICE_NAME")
        )
    
    def _load_pool_config(self) -> RedisPoolConfig:
        """Load Redis pool configuration"""
        return RedisPoolConfig(
            max_connections=int(os.getenv("REDIS_MAX_CONNECTIONS", 50)),
            socket_connect_timeout=int(os.getenv("REDIS_CONNECT_TIMEOUT", 5)),
            socket_timeout=int(os.getenv("REDIS_SOCKET_TIMEOUT", 5)),
            health_check_interval=int(os.getenv("REDIS_HEALTH_CHECK_INTERVAL", 30))
        )
    
    def _load_cache_config(self) -> RedisCacheConfig:
        """Load Redis cache configuration"""
        return RedisCacheConfig(
            default_ttl=int(os.getenv("REDIS_DEFAULT_TTL", 3600)),
            key_prefix=os.getenv("REDIS_KEY_PREFIX", "ia_influencer:"),
            serializer=os.getenv("REDIS_SERIALIZER", "json"),
            compression=os.getenv("REDIS_COMPRESSION", "false").lower() == "true"
        )
    
    def _load_cluster_config(self) -> RedisClusterConfig:
        """Load Redis cluster configuration"""
        return RedisClusterConfig(
            max_connections_per_node=int(os.getenv("REDIS_CLUSTER_MAX_CONNECTIONS", 50)),
            skip_full_coverage_check=os.getenv("REDIS_CLUSTER_SKIP_COVERAGE", "false").lower() == "true"
        )
    
    def create_client(self) -> Redis:
        """Create Redis client based on deployment type"""
        if not REDIS_AVAILABLE:
            logger.warning("Redis is not available - returning mock client")
            return None
            
        try:
            if self.deployment_type == RedisDeploymentType.CLUSTER:
                from rediscluster import RedisCluster
                return RedisCluster(
                    startup_nodes=self.cluster_config.startup_nodes or [
                        {"host": self.credentials.host, "port": self.credentials.port}
                    ],
                    password=self.credentials.password,
                    max_connections_per_node=self.cluster_config.max_connections_per_node
                )
            elif self.deployment_type == RedisDeploymentType.SENTINEL:
                sentinel = Sentinel(self.credentials.sentinel_hosts)
                return sentinel.master_for(
                    self.credentials.sentinel_service_name,
                    password=self.credentials.password
                )
            else:  # STANDALONE
                pool = ConnectionPool(
                    host=self.credentials.host,
                    port=self.credentials.port,
                    password=self.credentials.password,
                    max_connections=self.pool_config.max_connections,
                    socket_connect_timeout=self.pool_config.socket_connect_timeout,
                    socket_timeout=self.pool_config.socket_timeout
                )
                return Redis(connection_pool=pool)
        
        except Exception as e:
            logger.error(f"Failed to create Redis client: {e}")
            raise
    
    def optimize_cluster_performance(self) -> None:
        """Optimize Redis cluster for high performance"""
        if not REDIS_AVAILABLE:
            logger.warning("Redis is not available - skipping cluster optimization")
            return
            
        # Implementation for cluster optimization
        logger.info("Optimizing Redis cluster performance")
        # Add cluster-specific optimizations here

# ===== ELASTICSEARCH CONFIGURATION =====

@dataclass  
class ElasticsearchConfig:
    """Elasticsearch configuration for search and analytics"""
    hosts: List[str] = field(default_factory=lambda: ["localhost:9200"])
    username: Optional[str] = None
    password: Optional[str] = None
    use_ssl: bool = False
    verify_certs: bool = True
    timeout: int = 30
    max_retries: int = 3
    
    @classmethod
    def from_env(cls) -> None:
        """Create config from environment variables"""
        return cls(
            hosts=os.getenv("ELASTICSEARCH_HOSTS", "localhost:9200").split(","),
            username=os.getenv("ELASTICSEARCH_USERNAME"),
            password=os.getenv("ELASTICSEARCH_PASSWORD"),
            use_ssl=os.getenv("ELASTICSEARCH_USE_SSL", "false").lower() == "true",
            timeout=int(os.getenv("ELASTICSEARCH_TIMEOUT", 30))
        )

# ===== MONGODB CONFIGURATION =====

@dataclass
class MongoDBConfig:
    """MongoDB configuration for document storage"""
    connection_string: str = "mongodb://localhost:27017"
    database_name: str = "ia_influencer"
    max_pool_size: int = 100
    min_pool_size: int = 0
    server_selection_timeout: int = 30000
    
    @classmethod
    def from_env(cls) -> None:
        """Create config from environment variables"""
        return cls(
            connection_string=os.getenv("MONGODB_CONNECTION_STRING", "mongodb://localhost:27017"),
            database_name=os.getenv("MONGODB_DATABASE", "ia_influencer"),
            max_pool_size=int(os.getenv("MONGODB_MAX_POOL_SIZE", 100)),
            server_selection_timeout=int(os.getenv("MONGODB_TIMEOUT", 30000))
        )

# ===== POSTGRESQL CONFIGURATION =====

@dataclass
class PostgreSQLConfig:
    """PostgreSQL configuration for relational data"""
    host: str = "localhost"
    port: int = 5432
    database: str = "ia_influencer"
    username: str = "postgres"
    password: Optional[str] = None
    pool_size: int = 20
    max_overflow: int = 30
    pool_timeout: int = 30
    pool_recycle: int = 3600
    
    @classmethod
    def from_env(cls) -> None:
        """Create config from environment variables"""
        return cls(
            host=os.getenv("DATABASE_HOST", "localhost"),
            port=int(os.getenv("DATABASE_PORT", 5432)),
            database=os.getenv("DATABASE_NAME", "ia_influencer"),
            username=os.getenv("DATABASE_USER", "postgres"),
            password=os.getenv("DATABASE_PASSWORD"),
            pool_size=int(os.getenv("DATABASE_POOL_SIZE", 20)),
            max_overflow=int(os.getenv("DATABASE_MAX_OVERFLOW", 30))
        )

# Export all database configurations
__all__ = [
    # Redis Configuration
    "RedisConfig",
    "RedisEnvironment", 
    "RedisDeploymentType",
    "RedisWorkloadType",
    "RedisCredentials",
    "RedisPoolConfig", 
    "RedisCacheConfig",
    "RedisClusterConfig",
    
    # Other Database Configurations
    "ElasticsearchConfig",
    "MongoDBConfig", 
    "PostgreSQLConfig"
]