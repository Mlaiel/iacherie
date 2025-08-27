"""
Redis Configuration Module for IA-Influencer Agent Platform
==========================================================

Professional Redis configuration for caching, session management, real-time
messaging, and task queue operations in multi-tenant content protection platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA-Influencer Agent + Content Protection Platform
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps

Copyright Notice:
This code is the intellectual property of Fahed Mlaiel. 
Any unauthorized use, reproduction, or distribution of this code 
without explicit written permission from the author is strictly prohibited.

Contact: mlaiel@live.de for licensing inquiries.
"""

import os
import json
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import redis
from redis import Redis, ConnectionPool, Sentinel
from redis.exceptions import ConnectionError, TimeoutError, RedisError
import redis.asyncio as aioredis
from urllib.parse import urlparse
import ssl
import logging

logger = logging.getLogger(__name__)


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
    max_value_size: int = 1048576  # 1MB
    eviction_policy: str = "allkeys-lru"


@dataclass
class RedisClusterConfig:
    """Redis cluster configuration"""
    startup_nodes: List[Dict[str, Union[str, int]]] = field(default_factory=list)
    decode_responses: bool = True
    skip_full_coverage_check: bool = False
    max_connections_per_node: int = 50
    readonly_mode: bool = False
    health_check_interval: int = 30


class RedisConfig:
    """
    Professional Redis configuration manager for IA-Influencer Agent Platform
    
    Handles caching, session management, pub/sub messaging, task queues,
    and real-time analytics across multi-tenant content protection platform.
    """

    def __init__(self, 
                 environment: RedisEnvironment = RedisEnvironment.DEVELOPMENT,
                 workload_type: RedisWorkloadType = RedisWorkloadType.CACHE,
                 deployment_type: RedisDeploymentType = RedisDeploymentType.STANDALONE):
        self.environment = environment
        self.workload_type = workload_type
        self.deployment_type = deployment_type
        self.credentials = self._load_credentials()
        self.pool_config = self._get_pool_config()
        self.cache_config = self._get_cache_config()
        self.cluster_config = self._get_cluster_config() if deployment_type == RedisDeploymentType.CLUSTER else None
        self._pools: Dict[str, ConnectionPool] = {}
        self._clients: Dict[str, Redis] = {}
        self._async_clients: Dict[str, aioredis.Redis] = {}
        self._setup_logging()

    def _setup_logging(self) -> None:
        """Setup Redis-specific logging"""
        self.logger = logging.getLogger(f"redis.{self.environment.value}.{self.workload_type.value}")
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    def _load_credentials(self) -> RedisCredentials:
        """Load Redis credentials from environment"""
        env_prefix = f"REDIS_{self.environment.value.upper()}"
        
        # Parse sentinel hosts if provided
        sentinel_hosts = []
        sentinel_hosts_str = os.getenv(f"{env_prefix}_SENTINEL_HOSTS", "")
        if sentinel_hosts_str:
            try:
                sentinel_hosts = json.loads(sentinel_hosts_str)
            except json.JSONDecodeError:
                # Parse simple comma-separated format: host1:port1,host2:port2
                for host_port in sentinel_hosts_str.split(","):
                    if ":" in host_port:
                        host, port = host_port.strip().split(":", 1)
                        sentinel_hosts.append({"host": host, "port": int(port)})
        
        return RedisCredentials(
            host=os.getenv(f"{env_prefix}_HOST", "localhost"),
            port=int(os.getenv(f"{env_prefix}_PORT", "6379")),
            password=os.getenv(f"{env_prefix}_PASSWORD"),
            username=os.getenv(f"{env_prefix}_USERNAME"),
            ssl_enabled=os.getenv(f"{env_prefix}_SSL_ENABLED", "false").lower() == "true",
            ssl_cert_path=os.getenv(f"{env_prefix}_SSL_CERT"),
            ssl_key_path=os.getenv(f"{env_prefix}_SSL_KEY"),
            ssl_ca_path=os.getenv(f"{env_prefix}_SSL_CA"),
            ssl_check_hostname=os.getenv(f"{env_prefix}_SSL_CHECK_HOSTNAME", "true").lower() == "true",
            sentinel_hosts=sentinel_hosts,
            sentinel_service_name=os.getenv(f"{env_prefix}_SENTINEL_SERVICE")
        )

    def _get_pool_config(self) -> RedisPoolConfig:
        """Get connection pool configuration based on environment and workload"""
        base_configs = {
            RedisEnvironment.DEVELOPMENT: RedisPoolConfig(max_connections=10),
            RedisEnvironment.STAGING: RedisPoolConfig(max_connections=25),
            RedisEnvironment.PRODUCTION: RedisPoolConfig(max_connections=50),
            RedisEnvironment.TESTING: RedisPoolConfig(max_connections=5)
        }
        
        config = base_configs.get(self.environment, RedisPoolConfig())
        
        # Adjust based on workload type
        workload_adjustments = {
            RedisWorkloadType.CACHE: {"max_connections": config.max_connections},
            RedisWorkloadType.SESSION: {"max_connections": config.max_connections * 2},
            RedisWorkloadType.PUBSUB: {"max_connections": config.max_connections * 3},
            RedisWorkloadType.QUEUE: {"max_connections": config.max_connections * 2},
            RedisWorkloadType.ANALYTICS: {"max_connections": config.max_connections * 4},
            RedisWorkloadType.REAL_TIME: {
                "max_connections": config.max_connections * 5,
                "socket_timeout": 1,
                "socket_connect_timeout": 2
            }
        }
        
        adjustments = workload_adjustments.get(self.workload_type, {})
        for key, value in adjustments.items():
            setattr(config, key, value)
        
        return config

    def _get_cache_config(self) -> RedisCacheConfig:
        """Get cache configuration based on workload type"""
        workload_configs = {
            RedisWorkloadType.CACHE: RedisCacheConfig(
                default_ttl=3600,
                key_prefix="cache:",
                compression=True
            ),
            RedisWorkloadType.SESSION: RedisCacheConfig(
                default_ttl=86400,  # 24 hours
                key_prefix="session:",
                serializer="json"
            ),
            RedisWorkloadType.QUEUE: RedisCacheConfig(
                default_ttl=0,  # No expiration for queues
                key_prefix="queue:",
                serializer="json"
            ),
            RedisWorkloadType.ANALYTICS: RedisCacheConfig(
                default_ttl=7200,  # 2 hours
                key_prefix="analytics:",
                compression=True,
                max_value_size=5242880  # 5MB
            ),
            RedisWorkloadType.REAL_TIME: RedisCacheConfig(
                default_ttl=300,  # 5 minutes
                key_prefix="realtime:",
                serializer="json"
            ),
            RedisWorkloadType.PUBSUB: RedisCacheConfig(
                default_ttl=0,
                key_prefix="pubsub:",
                serializer="json"
            )
        }
        
        return workload_configs.get(self.workload_type, RedisCacheConfig())

    def _get_cluster_config(self) -> RedisClusterConfig:
        """Get cluster configuration from environment"""
        env_prefix = f"REDIS_{self.environment.value.upper()}_CLUSTER"
        
        # Parse startup nodes
        startup_nodes = []
        nodes_str = os.getenv(f"{env_prefix}_NODES", "")
        if nodes_str:
            try:
                startup_nodes = json.loads(nodes_str)
            except json.JSONDecodeError:
                # Parse simple format: host1:port1,host2:port2
                for node in nodes_str.split(","):
                    if ":" in node:
                        host, port = node.strip().split(":", 1)
                        startup_nodes.append({"host": host, "port": int(port)})
        
        return RedisClusterConfig(
            startup_nodes=startup_nodes,
            max_connections_per_node=int(os.getenv(f"{env_prefix}_MAX_CONNECTIONS_PER_NODE", "50")),
            readonly_mode=os.getenv(f"{env_prefix}_READONLY", "false").lower() == "true",
            skip_full_coverage_check=os.getenv(f"{env_prefix}_SKIP_COVERAGE_CHECK", "false").lower() == "true"
        )

    def _get_ssl_context(self) -> Optional[ssl.SSLContext]:
        """Create SSL context if SSL is enabled"""
        if not self.credentials.ssl_enabled:
            return None
        
        try:
            context = ssl.create_default_context()
            
            if self.credentials.ssl_ca_path:
                context.load_verify_locations(self.credentials.ssl_ca_path)
            
            if self.credentials.ssl_cert_path and self.credentials.ssl_key_path:
                context.load_cert_chain(self.credentials.ssl_cert_path, self.credentials.ssl_key_path)
            
            context.check_hostname = self.credentials.ssl_check_hostname
            
            return context
            
        except Exception as e:
            self.logger.error(f"Failed to create SSL context: {str(e)}")
            raise

    def create_connection_pool(self, database: int = 0, pool_name: str = "default") -> ConnectionPool:
        """
        Create Redis connection pool
        
        Args:
            database: Redis database number
            pool_name: Unique pool identifier
            
        Returns:
            Configured Redis connection pool
        """
        if pool_name in self._pools:
            return self._pools[pool_name]
        
        try:
            ssl_context = self._get_ssl_context()
            
            pool_kwargs = {
                "host": self.credentials.host,
                "port": self.credentials.port,
                "db": database,
                "password": self.credentials.password,
                "username": self.credentials.username,
                "max_connections": self.pool_config.max_connections,
                "retry_on_timeout": self.pool_config.retry_on_timeout,
                "retry_on_error": self.pool_config.retry_on_error,
                "health_check_interval": self.pool_config.health_check_interval,
                "socket_connect_timeout": self.pool_config.socket_connect_timeout,
                "socket_timeout": self.pool_config.socket_timeout,
                "socket_keepalive": self.pool_config.socket_keepalive,
                "socket_keepalive_options": self.pool_config.socket_keepalive_options,
                "decode_responses": True
            }
            
            if ssl_context:
                pool_kwargs["ssl"] = True
                pool_kwargs["ssl_context"] = ssl_context
            
            pool = ConnectionPool(**pool_kwargs)
            self._pools[pool_name] = pool
            
            self.logger.info(f"Redis connection pool created: {pool_name} (db={database})")
            return pool
            
        except Exception as e:
            self.logger.error(f"Failed to create Redis connection pool: {str(e)}")
            raise

    def create_client(self, database: int = 0, client_name: str = "default") -> Redis:
        """
        Create Redis client
        
        Args:
            database: Redis database number
            client_name: Unique client identifier
            
        Returns:
            Configured Redis client
        """
        if client_name in self._clients:
            return self._clients[client_name]
        
        try:
            if self.deployment_type == RedisDeploymentType.SENTINEL:
                client = self._create_sentinel_client(database)
            elif self.deployment_type == RedisDeploymentType.CLUSTER:
                client = self._create_cluster_client()
            else:
                pool = self.create_connection_pool(database, f"{client_name}_pool")
                client = Redis(connection_pool=pool)
            
            # Test connection
            client.ping()
            
            self._clients[client_name] = client
            self.logger.info(f"Redis client created: {client_name} (db={database})")
            
            return client
            
        except Exception as e:
            self.logger.error(f"Failed to create Redis client: {str(e)}")
            raise

    def _create_sentinel_client(self, database: int = 0) -> Redis:
        """Create Redis client using Sentinel"""
        try:
            sentinel = Sentinel(self.credentials.sentinel_hosts)
            return sentinel.master_for(
                self.credentials.sentinel_service_name,
                socket_timeout=self.pool_config.socket_timeout,
                password=self.credentials.password,
                db=database
            )
        except Exception as e:
            self.logger.error(f"Failed to create Sentinel client: {str(e)}")
            raise

    def _create_cluster_client(self) -> Redis:
        """Create Redis cluster client"""
        try:
            from rediscluster import RedisCluster
            
            return RedisCluster(
                startup_nodes=self.cluster_config.startup_nodes,
                decode_responses=self.cluster_config.decode_responses,
                skip_full_coverage_check=self.cluster_config.skip_full_coverage_check,
                max_connections_per_node=self.cluster_config.max_connections_per_node,
                readonly_mode=self.cluster_config.readonly_mode,
                health_check_interval=self.cluster_config.health_check_interval,
                password=self.credentials.password
            )
        except ImportError:
            self.logger.error("redis-py-cluster not installed. Install with: pip install redis-py-cluster")
            raise
        except Exception as e:
            self.logger.error(f"Failed to create cluster client: {str(e)}")
            raise

    def create_async_client(self, database: int = 0, client_name: str = "async_default") -> aioredis.Redis:
        """
        Create async Redis client for real-time operations
        
        Args:
            database: Redis database number
            client_name: Unique client identifier
            
        Returns:
            Configured async Redis client
        """
        if client_name in self._async_clients:
            return self._async_clients[client_name]
        
        try:
            ssl_context = self._get_ssl_context()
            
            client_kwargs = {
                "host": self.credentials.host,
                "port": self.credentials.port,
                "db": database,
                "password": self.credentials.password,
                "username": self.credentials.username,
                "decode_responses": True,
                "socket_timeout": self.pool_config.socket_timeout,
                "socket_connect_timeout": self.pool_config.socket_connect_timeout,
                "socket_keepalive": self.pool_config.socket_keepalive,
                "socket_keepalive_options": self.pool_config.socket_keepalive_options,
                "retry_on_timeout": self.pool_config.retry_on_timeout,
                "max_connections": self.pool_config.max_connections
            }
            
            if ssl_context:
                client_kwargs["ssl"] = True
                client_kwargs["ssl_context"] = ssl_context
            
            client = aioredis.Redis(**client_kwargs)
            self._async_clients[client_name] = client
            
            self.logger.info(f"Redis async client created: {client_name} (db={database})")
            return client
            
        except Exception as e:
            self.logger.error(f"Failed to create async Redis client: {str(e)}")
            raise

    def get_cache_client(self) -> Redis:
        """Get Redis client optimized for caching operations"""
        return self.create_client(database=0, client_name="cache")

    def get_session_client(self) -> Redis:
        """Get Redis client for session management"""
        return self.create_client(database=1, client_name="session")

    def get_queue_client(self) -> Redis:
        """Get Redis client for task queue operations (Celery)"""
        return self.create_client(database=2, client_name="queue")

    def get_pubsub_client(self) -> Redis:
        """Get Redis client for pub/sub messaging"""
        return self.create_client(database=3, client_name="pubsub")

    def get_analytics_client(self) -> Redis:
        """Get Redis client for analytics data"""
        return self.create_client(database=4, client_name="analytics")

    def get_real_time_client(self) -> aioredis.Redis:
        """Get async Redis client for real-time operations"""
        return self.create_async_client(database=5, client_name="realtime")

    def get_tenant_client(self, tenant_id: str) -> Redis:
        """
        Get tenant-specific Redis client
        
        Args:
            tenant_id: Unique tenant identifier
            
        Returns:
            Tenant-specific Redis client
        """
        # Use database 10+ for tenants
        tenant_db = 10 + hash(tenant_id) % 5  # Distribute across 5 DBs
        return self.create_client(database=tenant_db, client_name=f"tenant_{tenant_id}")

    def health_check(self) -> Dict[str, Any]:
        """
        Perform comprehensive health check on Redis connections
        
        Returns:
            Health check results dictionary
        """
        health_status = {
            "status": "healthy",
            "environment": self.environment.value,
            "workload_type": self.workload_type.value,
            "deployment_type": self.deployment_type.value,
            "clients": {},
            "timestamp": None
        }
        
        import datetime
        health_status["timestamp"] = datetime.datetime.utcnow().isoformat()
        
        try:
            # Test main client
            main_client = self.create_client()
            
            # Basic connectivity test
            ping_result = main_client.ping()
            
            # Get Redis info
            redis_info = main_client.info()
            
            health_status["clients"]["main"] = {
                "status": "healthy",
                "ping": ping_result,
                "redis_version": redis_info.get("redis_version"),
                "uptime_seconds": redis_info.get("uptime_in_seconds"),
                "connected_clients": redis_info.get("connected_clients"),
                "used_memory": redis_info.get("used_memory"),
                "used_memory_human": redis_info.get("used_memory_human"),
                "used_memory_peak": redis_info.get("used_memory_peak"),
                "used_memory_peak_human": redis_info.get("used_memory_peak_human"),
                "keyspace_hits": redis_info.get("keyspace_hits", 0),
                "keyspace_misses": redis_info.get("keyspace_misses", 0),
                "instantaneous_ops_per_sec": redis_info.get("instantaneous_ops_per_sec"),
                "total_commands_processed": redis_info.get("total_commands_processed")
            }
            
            # Calculate hit rate
            hits = redis_info.get("keyspace_hits", 0)
            misses = redis_info.get("keyspace_misses", 0)
            total_requests = hits + misses
            hit_rate = (hits / total_requests * 100) if total_requests > 0 else 0
            health_status["clients"]["main"]["cache_hit_rate_percent"] = round(hit_rate, 2)
            
        except (ConnectionError, TimeoutError, RedisError) as e:
            health_status["status"] = "unhealthy"
            health_status["clients"]["main"] = {
                "status": "unhealthy",
                "error": str(e)
            }
            self.logger.error(f"Redis health check failed: {str(e)}")
        except Exception as e:
            health_status["status"] = "unhealthy"
            health_status["error"] = str(e)
            self.logger.error(f"Redis health check error: {str(e)}")
        
        return health_status

    def close_all_connections(self) -> None:
        """Close all Redis connections and cleanup resources"""
        # Close sync clients
        for client_name, client in self._clients.items():
            try:
                client.close()
                self.logger.info(f"Closed Redis client: {client_name}")
            except Exception as e:
                self.logger.error(f"Error closing client {client_name}: {str(e)}")
        
        # Close async clients
        for client_name, client in self._async_clients.items():
            try:
                client.close()
                self.logger.info(f"Closed Redis async client: {client_name}")
            except Exception as e:
                self.logger.error(f"Error closing async client {client_name}: {str(e)}")
        
        # Close connection pools
        for pool_name, pool in self._pools.items():
            try:
                pool.disconnect()
                self.logger.info(f"Closed Redis connection pool: {pool_name}")
            except Exception as e:
                self.logger.error(f"Error closing pool {pool_name}: {str(e)}")
        
        self._clients.clear()
        self._async_clients.clear()
        self._pools.clear()

    def __del__(self):
        """Cleanup on object destruction"""
        self.close_all_connections()
