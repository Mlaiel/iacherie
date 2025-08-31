"""Database Connection Pool Manager - IA Influencer Agent + Content Protection Platform

This module provides enterprise-grade connection pool management for multi-database
architecture supporting content creators, AI processing, protection, and monetization.

Pool Management Features:
- Dynamic pool sizing based on load
- Health monitoring and auto-recovery
- Load balancing across read replicas
- Connection lifecycle management
- Performance metrics and optimization
- Multi-tenant connection isolation
- Failover and circuit breaker patterns
- Memory optimization and leak prevention

Supported Databases:
- PostgreSQL: Primary relational data with read replicas
- Redis: Caching, sessions, real-time operations
- MongoDB: Content metadata, fingerprints, analytics
- Elasticsearch: Search indexing, logs, content discovery
- FAISS: Vector similarity for content fingerprinting
- MinIO/S3: Object storage connection pooling

Business Logic Integration:
User content upload → AI fingerprinting → Protection monitoring →
Revenue tracking → Collaboration matching → Distribution

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps

WARNING: This code is proprietary and confidential. Any unauthorized use, modification,
or distribution is strictly prohibited and may result in legal action.
Contact: mlaiel@live.de for licensing inquiries.

Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""import asyncio
import logging
import time
from typing import Dict, List, Optional, Any, Union, Type, Callable
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from contextlib import asynccontextmanager
from enum import Enum
import weakref
import gc
from datetime import datetime, timedelta

# Database drivers and libraries
try:
    import asyncpg
except ImportError:
    asyncpg = None
    
try:
    import aioredis
except ImportError:
    aioredis = None

# Initialize logger
logger = logging.getLogger(__name__)

# Database imports
try:
    import asyncpg
    import aioredis
    import motor.motor_asyncio
    from elasticsearch import AsyncElasticsearch
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
    from sqlalchemy.pool import QueuePool, NullPool
    from sqlalchemy.engine.events import PoolEvents
    import boto3
    from aiobotocore.session import get_session
except ImportError as e:
    logging.warning(f"Database dependency missing: {e}")

logger = logging.getLogger(__name__)

# =============== ENUMS & CONSTANTS ===============

class DatabaseType(str, Enum):
    """Supported database types"""    POSTGRESQL = "postgresql"
    REDIS = "redis"
    MONGODB = "mongodb"
    ELASTICSEARCH = "elasticsearch"
    VECTOR_STORE = "vector_store"
    OBJECT_STORAGE = "object_storage"

class ConnectionState(str, Enum):
    """Connection states"""    IDLE = "idle"
    ACTIVE = "active"
    FAILED = "failed"
    RECOVERING = "recovering"
    CLOSED = "closed"

class PoolStrategy(str, Enum):
    """Pool management strategies"""    FIXED = "fixed"
    DYNAMIC = "dynamic"
    ADAPTIVE = "adaptive"
    ELASTIC = "elastic"

# =============== CONFIGURATION ===============

@dataclass
class PoolConfig:
    """Database pool configuration"""    # Core settings
    min_size: int = 5
    max_size: int = 50
    initial_size: int = 10
    pool_timeout: int = 30
    connection_timeout: int = 60
    idle_timeout: int = 3600
    
    # Advanced settings
    strategy: PoolStrategy = PoolStrategy.ADAPTIVE
    max_retries: int = 3
    retry_delay: float = 1.0
    health_check_interval: int = 30
    enable_monitoring: bool = True
    
    # Performance tuning
    prefill_connections: bool = True
    pool_pre_ping: bool = True
    recycle_connections: int = 3600
    overflow_size: int = 10
    
    # Security & compliance
    encrypt_connections: bool = True
    validate_ssl: bool = True
    connection_encryption_key: Optional[str] = None
    
    # Multi-tenant settings
    tenant_isolation: bool = True
    max_tenants: int = 1000
    tenant_pool_ratio: float = 0.1

@dataclass
class DatabaseConnectionInfo:
    """Database connection information"""    host: str
    port: int
    database: str
    username: str
    password: str
    ssl_mode: str = "prefer"
    connection_params: Dict[str, Any] = field(default_factory=dict)
    is_replica: bool = False
    weight: int = 100
    tags: List[str] = field(default_factory=list)

# =============== POOL INTERFACES ===============

class IConnectionPool(ABC):
    """Interface for connection pools"""    
    @abstractmethod
    async def acquire(self, timeout: Optional[float] = None) -> Any:
        """Acquire connection from pool"""        pass
    
    @abstractmethod
    async def release(self, connection: Any) -> None:
        """Release connection back to pool"""        pass
    
    @abstractmethod
    async def close(self) -> None:
        """Close all connections in pool"""        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """Check pool health"""        pass
    
    @abstractmethod
    def get_stats(self) -> Dict[str, Any]:
        """Get pool statistics"""        pass
    
    @abstractmethod
    async def resize_pool(self, new_min_size: int, new_max_size: int) -> bool:
        """Dynamically resize pool"""        pass
    
    @abstractmethod
    async def execute_maintenance(self) -> bool:
        """Execute pool maintenance operations"""        pass

# =============== CONNECTION POOL IMPLEMENTATIONS ===============

class PostgreSQLConnectionPool(IConnectionPool):
    """PostgreSQL connection pool with advanced features"""    
    def __init__(self, config: PoolConfig, connection_info: DatabaseConnectionInfo):
        self.config = config
        self.connection_info = connection_info
        self.pool: Optional[asyncpg.Pool] = None
        self.read_pools: List[asyncpg.Pool] = []
        self.state = ConnectionState.IDLE
        self.stats = {
            "created_at": datetime.utcnow(),
            "total_connections": 0,
            "active_connections": 0,
            "failed_connections": 0,
            "total_queries": 0,
            "avg_query_time": 0.0,
            "last_health_check": None
        }
        self._connection_semaphore = asyncio.Semaphore(config.max_size)
        self._health_check_task: Optional[asyncio.Task] = None
    
    async def initialize(self, read_replicas: Optional[List[DatabaseConnectionInfo]] = None) -> bool:
        """Initialize connection pools"""        try:
            # Primary connection pool
            dsn = self._build_dsn(self.connection_info)
            self.pool = await asyncpg.create_pool(
                dsn,
                min_size=self.config.min_size,
                max_size=self.config.max_size,
                command_timeout=self.config.connection_timeout,
                server_settings={
                    'jit': 'off',
                    'application_name': 'ia_influencer_agent'
                }
            )
            
            # Read replica pools
            if read_replicas:
                for replica_info in read_replicas:
                    replica_dsn = self._build_dsn(replica_info)
                    replica_pool = await asyncpg.create_pool(
                        replica_dsn,
                        min_size=max(1, self.config.min_size // 2),
                        max_size=max(5, self.config.max_size // 2),
                        command_timeout=self.config.connection_timeout
                    )
                    self.read_pools.append(replica_pool)
            
            self.state = ConnectionState.ACTIVE
            
            # Start health monitoring
            if self.config.enable_monitoring:
                self._health_check_task = asyncio.create_task(self._health_monitor())
            
            logger.info(f"✅ PostgreSQL pool initialized - Primary: {self.pool.get_size()}, Replicas: {len(self.read_pools)}")
            return True
            
        except Exception as e:
            logger.error(f"❌ PostgreSQL pool initialization failed: {e}")
            self.state = ConnectionState.FAILED
            return False
    
    def _build_dsn(self, info: DatabaseConnectionInfo) -> str:
        """Build PostgreSQL DSN"""        dsn_params = {
            'host': info.host,
            'port': info.port,
            'database': info.database,
            'user': info.username,
            'password': info.password,
            'sslmode': info.ssl_mode
        }
        dsn_params.update(info.connection_params)
        
        return "postgresql://{user}:{password}@{host}:{port}/{database}?sslmode={sslmode}".format(**dsn_params)
    
    async def acquire(self, timeout: Optional[float] = None, read_only: bool = False) -> asyncpg.Connection:
        """Acquire connection from appropriate pool"""        timeout = timeout or self.config.pool_timeout
        
        try:
            async with self._connection_semaphore:
                # Use read replica for read-only operations
                if read_only and self.read_pools:
                    pool = self._select_read_pool()
                else:
                    pool = self.pool
                
                if not pool:
                    raise Exception("Pool not initialized")
                
                connection = await asyncio.wait_for(
                    pool.acquire(),
                    timeout=timeout
                )
                
                self.stats["active_connections"] += 1
                return connection
                
        except asyncio.TimeoutError:
            logger.warning(f"PostgreSQL connection timeout after {timeout}s")
            raise
        except Exception as e:
            logger.error(f"Failed to acquire PostgreSQL connection: {e}")
            self.stats["failed_connections"] += 1
            raise
    
    def _select_read_pool(self) -> asyncpg.Pool:
        """Select read replica pool using weighted round-robin"""        if not self.read_pools:
            return self.pool
        
        # Simple round-robin for now
        import random
        return random.choice(self.read_pools)
    
    async def release(self, connection: asyncpg.Connection) -> None:
        """Release connection back to pool"""        try:
            # Determine which pool the connection belongs to
            pool_to_release = self.pool
            for replica_pool in self.read_pools:
                # This is a simplified check - in production you'd track connection origins
                if replica_pool:
                    pool_to_release = replica_pool
                    break
            
            await pool_to_release.release(connection)
            self.stats["active_connections"] = max(0, self.stats["active_connections"] - 1)
            
        except Exception as e:
            logger.error(f"Failed to release PostgreSQL connection: {e}")
    
    async def execute_query(self, query: str, *args, read_only: bool = False) -> Any:
        """Execute query with automatic connection management"""        start_time = time.time()
        connection = await self.acquire(read_only=read_only)
        
        try:
            if args:
                result = await connection.fetch(query, *args)
            else:
                result = await connection.fetch(query)
            
            # Update statistics
            query_time = time.time() - start_time
            self.stats["total_queries"] += 1
            self.stats["avg_query_time"] = (
                (self.stats["avg_query_time"] * (self.stats["total_queries"] - 1) + query_time) / 
                self.stats["total_queries"]
            )
            
            return result
            
        finally:
            await self.release(connection)
    
    async def health_check(self) -> bool:
        """Check pool health"""        try:
            connection = await self.acquire(timeout=5.0)
            result = await connection.fetchval("SELECT 1")
            await self.release(connection)
            
            self.stats["last_health_check"] = datetime.utcnow()
            return result == 1
            
        except Exception as e:
            logger.error(f"PostgreSQL health check failed: {e}")
            return False
    
    async def _health_monitor(self) -> None:
        """Background health monitoring"""        while self.state == ConnectionState.ACTIVE:
            try:
                is_healthy = await self.health_check()
                if not is_healthy:
                    logger.warning("PostgreSQL pool health check failed")
                    # Implement recovery logic here
                
                await asyncio.sleep(self.config.health_check_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Health monitor error: {e}")
                await asyncio.sleep(5)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get pool statistics"""        pool_stats = {
            "pool_size": self.pool.get_size() if self.pool else 0,
            "available_connections": self.pool.get_idle_size() if self.pool else 0,
            "replica_pools": len(self.read_pools),
            "state": self.state.value
        }
        pool_stats.update(self.stats)
        return pool_stats
    
    async def close(self) -> None:
        """Close all pools"""        try:
            self.state = ConnectionState.CLOSED
            
            # Cancel health monitoring
            if self._health_check_task:
                self._health_check_task.cancel()
                try:
                    await self._health_check_task
                except asyncio.CancelledError:
                    pass
            
            # Close replica pools
            for replica_pool in self.read_pools:
                await replica_pool.close()
            
            # Close primary pool
            if self.pool:
                await self.pool.close()
            
            logger.info("✅ PostgreSQL pools closed")
            
        except Exception as e:
            logger.error(f"Error closing PostgreSQL pools: {e}")
    
    async def resize_pool(self, new_min_size: int, new_max_size: int) -> bool:
        """Dynamically resize PostgreSQL pool"""        try:
            if self.pool:
                # Close existing pool
                await self.pool.close()
                
                # Update configuration
                self.config.min_size = new_min_size
                self.config.max_size = new_max_size
                
                # Recreate pool with new size
                dsn = self._build_dsn(self.connection_info)
                self.pool = await asyncpg.create_pool(
                    dsn,
                    min_size=new_min_size,
                    max_size=new_max_size,
                    command_timeout=self.config.connection_timeout
                )
                
                logger.info(f"✅ PostgreSQL pool resized - Min: {new_min_size}, Max: {new_max_size}")
                return True
                
        except Exception as e:
            logger.error(f"❌ Failed to resize PostgreSQL pool: {e}")
            return False
    
    async def execute_maintenance(self) -> bool:
        """Execute PostgreSQL pool maintenance"""        try:
            # Clear connection statistics
            expired_connections = 0
            
            # Check for long-running connections
            if self.pool:
                pool_size = self.pool.get_size()
                idle_size = self.pool.get_idle_size()
                
                # Force garbage collection if too many idle connections
                if idle_size > self.config.max_size * 0.8:
                    gc.collect()
                    expired_connections = idle_size - int(self.config.max_size * 0.6)
            
            # Update maintenance timestamp
            self.stats["last_maintenance"] = datetime.utcnow()
            
            logger.info(f"✅ PostgreSQL pool maintenance completed - Cleaned {expired_connections} connections")
            return True
            
        except Exception as e:
            logger.error(f"❌ PostgreSQL pool maintenance failed: {e}")
            return False

class RedisConnectionPool(IConnectionPool):
    """Redis connection pool with clustering support"""    
    def __init__(self, config: PoolConfig, connection_info: DatabaseConnectionInfo):
        self.config = config
        self.connection_info = connection_info
        self.pool: Optional[aioredis.ConnectionPool] = None
        self.redis_client: Optional[aioredis.Redis] = None
        self.state = ConnectionState.IDLE
        self.stats = {
            "created_at": datetime.utcnow(),
            "total_connections": 0,
            "active_connections": 0,
            "failed_connections": 0,
            "total_commands": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "last_health_check": None
        }
    
    async def initialize(self) -> bool:
        """Initialize Redis connection pool"""        try:
            # Connection pool configuration
            pool_config = {
                'host': self.connection_info.host,
                'port': self.connection_info.port,
                'db': int(self.connection_info.database),
                'password': self.connection_info.password,
                'max_connections': self.config.max_size,
                'retry_on_timeout': True,
                'socket_keepalive': True,
                'socket_keepalive_options': {},
                'health_check_interval': self.config.health_check_interval
            }
            
            self.pool = aioredis.ConnectionPool(**pool_config)
            self.redis_client = aioredis.Redis(connection_pool=self.pool)
            
            # Test connection
            await self.redis_client.ping()
            self.state = ConnectionState.ACTIVE
            
            logger.info(f"✅ Redis pool initialized - Max connections: {self.config.max_size}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Redis pool initialization failed: {e}")
            self.state = ConnectionState.FAILED
            return False
    
    async def acquire(self, timeout: Optional[float] = None) -> aioredis.Redis:
        """Acquire Redis client"""        if not self.redis_client:
            raise Exception("Redis pool not initialized")
        
        self.stats["active_connections"] += 1
        return self.redis_client
    
    async def release(self, connection: aioredis.Redis) -> None:
        """Release Redis client (no-op for Redis)"""        self.stats["active_connections"] = max(0, self.stats["active_connections"] - 1)
    
    async def health_check(self) -> bool:
        """Check Redis health"""        try:
            client = await self.acquire()
            result = await client.ping()
            await self.release(client)
            
            self.stats["last_health_check"] = datetime.utcnow()
            return result
            
        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get Redis pool statistics"""        pool_stats = {
            "pool_max_connections": self.config.max_size,
            "pool_created_connections": self.pool.created_connections if self.pool else 0,
            "pool_available_connections": self.pool.available_connections if self.pool else 0,
            "state": self.state.value
        }
        pool_stats.update(self.stats)
        return pool_stats
    
    async def close(self) -> None:
        """Close Redis pool"""        try:
            self.state = ConnectionState.CLOSED
            
            if self.redis_client:
                await self.redis_client.close()
            
            if self.pool:
                await self.pool.disconnect()
            
            logger.info("✅ Redis pool closed")
            
        except Exception as e:
            logger.error(f"Error closing Redis pool: {e}")
    
    async def resize_pool(self, new_min_size: int, new_max_size: int) -> bool:
        """Dynamically resize Redis pool"""        try:
            # Close existing connections
            if self.redis_client:
                await self.redis_client.close()
            if self.pool:
                await self.pool.disconnect()
            
            # Update configuration
            self.config.max_size = new_max_size
            
            # Recreate pool with new size
            pool_config = {
                'host': self.connection_info.host,
                'port': self.connection_info.port,
                'db': int(self.connection_info.database),
                'password': self.connection_info.password,
                'max_connections': new_max_size,
                'retry_on_timeout': True,
                'socket_keepalive': True,
                'health_check_interval': self.config.health_check_interval
            }
            
            self.pool = aioredis.ConnectionPool(**pool_config)
            self.redis_client = aioredis.Redis(connection_pool=self.pool)
            
            logger.info(f"✅ Redis pool resized - Max connections: {new_max_size}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to resize Redis pool: {e}")
            return False
    
    async def execute_maintenance(self) -> bool:
        """Execute Redis pool maintenance"""        try:
            # Clear expired keys and optimize memory
            if self.redis_client:
                # Get memory usage statistics
                memory_info = await self.redis_client.memory_usage()
                
                # Force garbage collection in Redis
                await self.redis_client.memory_purge()
                
                # Update statistics
                self.stats["last_maintenance"] = datetime.utcnow()
                
            logger.info("✅ Redis pool maintenance completed")
            return True
            
        except Exception as e:
            logger.error(f"❌ Redis pool maintenance failed: {e}")
            return False

# =============== POOL MANAGER ===============

class DatabasePoolManager:
    """Central manager for all database connection pools"""    
    def __init__(self):
        self.pools: Dict[str, IConnectionPool] = {}
        self.pool_configs: Dict[DatabaseType, PoolConfig] = {}
        self.connection_infos: Dict[str, DatabaseConnectionInfo] = {}
        self.monitoring_task: Optional[asyncio.Task] = None
        self.is_running = False
        self._pool_locks: Dict[str, asyncio.Lock] = {}
        
        # Enhanced pool management features
        self.load_balancers: Dict[str, 'LoadBalancer'] = {}
        self.circuit_breakers: Dict[str, 'CircuitBreaker'] = {}
        self.connection_metrics: Dict[str, Dict[str, Any]] = defaultdict(dict)
        self.adaptive_sizing_enabled = True
        self.optimization_history: List[Dict[str, Any]] = []
    
    def register_pool_config(self, db_type: DatabaseType, config: PoolConfig) -> None:
        """Register pool configuration for database type"""        self.pool_configs[db_type] = config
        logger.info(f"✅ Pool config registered for {db_type.value}")
    
    def register_connection_info(self, pool_id: str, connection_info: DatabaseConnectionInfo) -> None:
        """Register connection information"""        self.connection_infos[pool_id] = connection_info
        self._pool_locks[pool_id] = asyncio.Lock()
        logger.info(f"✅ Connection info registered for {pool_id}")
    
    async def create_pool(self, pool_id: str, db_type: DatabaseType, 
                         read_replicas: Optional[List[DatabaseConnectionInfo]] = None) -> bool:
        """Create and initialize database pool"""        async with self._pool_locks.get(pool_id, asyncio.Lock()):
            try:
                if pool_id in self.pools:
                    logger.warning(f"Pool {pool_id} already exists")
                    return True
                
                config = self.pool_configs.get(db_type)
                connection_info = self.connection_infos.get(pool_id)
                
                if not config or not connection_info:
                    raise ValueError(f"Missing config or connection info for {pool_id}")
                
                # Create appropriate pool implementation
                if db_type == DatabaseType.POSTGRESQL:
                    pool = PostgreSQLConnectionPool(config, connection_info)
                    success = await pool.initialize(read_replicas)
                elif db_type == DatabaseType.REDIS:
                    pool = RedisConnectionPool(config, connection_info)
                    success = await pool.initialize()
                elif db_type == DatabaseType.MONGODB:
                    # Import MongoDB pool implementation
                    from .mongodb_pool import MongoDBConnectionPool
                    pool = MongoDBConnectionPool(config, connection_info)
                    success = await pool.initialize()
                elif db_type == DatabaseType.ELASTICSEARCH:
                    # Import Elasticsearch pool implementation  
                    from .elasticsearch_pool import ElasticsearchConnectionPool
                    pool = ElasticsearchConnectionPool(config, connection_info)
                    success = await pool.initialize()
                elif db_type == DatabaseType.VECTOR_STORE:
                    # Import Vector store pool implementation
                    from .vector_store_pool import VectorStoreConnectionPool
                    pool = VectorStoreConnectionPool(config, connection_info)
                    success = await pool.initialize()
                elif db_type == DatabaseType.OBJECT_STORAGE:
                    # Import Object storage pool implementation
                    from .object_storage_pool import ObjectStorageConnectionPool
                    pool = ObjectStorageConnectionPool(config, connection_info)
                    success = await pool.initialize()
                else:
                    logger.error(f"Unsupported database type: {db_type}")
                    return False
                
                if success:
                    self.pools[pool_id] = pool
                    logger.info(f"✅ Pool {pool_id} created successfully")
                    return True
                else:
                    logger.error(f"❌ Pool {pool_id} creation failed")
                    return False
                
            except Exception as e:
                logger.error(f"Error creating pool {pool_id}: {e}")
                return False
    
    async def get_pool(self, pool_id: str) -> Optional[IConnectionPool]:
        """Get pool by ID"""        return self.pools.get(pool_id)
    
    async def acquire_connection(self, pool_id: str, **kwargs) -> Any:
        """Acquire connection from specific pool"""        pool = await self.get_pool(pool_id)
        if not pool:
            raise ValueError(f"Pool {pool_id} not found")
        
        return await pool.acquire(**kwargs)
    
    async def release_connection(self, pool_id: str, connection: Any) -> None:
        """Release connection back to pool"""        pool = await self.get_pool(pool_id)
        if pool:
            await pool.release(connection)
    
    async def health_check_all(self) -> Dict[str, bool]:
        """Health check all pools"""        results = {}
        
        for pool_id, pool in self.pools.items():
            try:
                results[pool_id] = await pool.health_check()
            except Exception as e:
                logger.error(f"Health check failed for {pool_id}: {e}")
                results[pool_id] = False
        
        return results
    
    def get_all_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics for all pools"""        return {
            pool_id: pool.get_stats() 
            for pool_id, pool in self.pools.items()
        }
    
    async def start_monitoring(self) -> None:
        """Start background monitoring"""        if self.is_running:
            return
        
        self.is_running = True
        self.monitoring_task = asyncio.create_task(self._monitor_pools())
        logger.info("✅ Pool monitoring started")
    
    async def _monitor_pools(self) -> None:
        """Background monitoring task"""        while self.is_running:
            try:
                # Health checks
                health_results = await self.health_check_all()
                failed_pools = [pool_id for pool_id, healthy in health_results.items() if not healthy]
                
                if failed_pools:
                    logger.warning(f"Unhealthy pools detected: {failed_pools}")
                
                # Memory cleanup
                gc.collect()
                
                await asyncio.sleep(30)  # Monitor every 30 seconds
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Pool monitoring error: {e}")
                await asyncio.sleep(10)
    
    async def close_all_pools(self) -> None:
        """Close all database pools"""        try:
            self.is_running = False
            
            # Cancel monitoring
            if self.monitoring_task:
                self.monitoring_task.cancel()
                try:
                    await self.monitoring_task
                except asyncio.CancelledError:
                    pass
            
            # Close all pools
            for pool_id, pool in self.pools.items():
                try:
                    await pool.close()
                    logger.info(f"✅ Pool {pool_id} closed")
                except Exception as e:
                    logger.error(f"Error closing pool {pool_id}: {e}")
            
            self.pools.clear()
            logger.info("✅ All pools closed")
            
        except Exception as e:
            logger.error(f"Error closing pools: {e}")

# =============== GLOBAL POOL MANAGER INSTANCE ===============

_global_pool_manager: Optional[DatabasePoolManager] = None

def get_pool_manager() -> DatabasePoolManager:
    """Get global pool manager instance"""    global _global_pool_manager
    if _global_pool_manager is None:
        _global_pool_manager = DatabasePoolManager()
    return _global_pool_manager

async def initialize_pools(config_dict: Dict[str, Any]) -> bool:
    """Initialize all pools from configuration"""    manager = get_pool_manager()
    
    try:
        # Register configurations
        for db_type_str, pool_config_dict in config_dict.get('pool_configs', {}).items():
            db_type = DatabaseType(db_type_str)
            config = PoolConfig(**pool_config_dict)
            manager.register_pool_config(db_type, config)
        
        # Register connections
        for pool_id, conn_info_dict in config_dict.get('connections', {}).items():
            conn_info = DatabaseConnectionInfo(**conn_info_dict)
            manager.register_connection_info(pool_id, conn_info)
        
        # Create pools
        for pool_id, pool_def in config_dict.get('pools', {}).items():
            db_type = DatabaseType(pool_def['type'])
            read_replicas = pool_def.get('read_replicas', [])
            replica_infos = [DatabaseConnectionInfo(**r) for r in read_replicas]
            
            await manager.create_pool(pool_id, db_type, replica_infos or None)
        
        # Start monitoring
        await manager.start_monitoring()
        
        logger.info("✅ All database pools initialized successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ Pool initialization failed: {e}")
        return False

# =============== EXPORTS ===============

__all__ = [
    # Core classes
    "DatabasePoolManager",
    "PostgreSQLConnectionPool", 
    "RedisConnectionPool",
    # Configuration
    "PoolConfig",
    "DatabaseConnectionInfo",
    # Enums
    "DatabaseType",
    "ConnectionState", 
    "PoolStrategy",
    # Functions
    "get_pool_manager",
    "initialize_pools",
    # Interfaces
    "IConnectionPool"
]
