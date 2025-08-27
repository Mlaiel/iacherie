"""
Database Connection Management - IA Influencer Agent Platform
Enterprise-grade connection handling with pool management and failover

Author: Fahed Mlaiel <mlaiel@live.de>
Team Specialties: Lead AI Developer, Senior Backend Engineer, ML Engineer, 
Database Administrator, Security Expert, Microservices Architect, Audio Engineer, 
DevOps Engineer, AI Prompt Engineer

WARNING: This code is protected by copyright. Any unauthorized use, reproduction,
or distribution without written permission from Fahed Mlaiel is strictly prohibited.
Contact: mlaiel@live.de for licensing and permissions.
"""

import asyncio
import asyncpg
import psycopg2
import redis
import logging
from typing import Optional, Dict, Any, List, Union
from contextlib import asynccontextmanager, contextmanager
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import create_engine, event, pool, text
from sqlalchemy.pool import QueuePool, NullPool
from urllib.parse import urlparse
import time
from dataclasses import dataclass
from enum import Enum

from ..core.config import get_settings
from ..core.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()


class DatabaseType(Enum):
    """Supported database types"""
    POSTGRESQL = "postgresql"
    REDIS = "redis"
    MONGODB = "mongodb"
    ELASTICSEARCH = "elasticsearch"


class ConnectionState(Enum):
    """Connection state enumeration"""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"
    MAINTENANCE = "maintenance"


@dataclass
class ConnectionConfig:
    """Database connection configuration"""
    host: str
    port: int
    database: str
    username: str
    password: str
    ssl_mode: str = "require"
    pool_size: int = 20
    max_overflow: int = 30
    pool_timeout: int = 30
    pool_recycle: int = 3600
    pool_pre_ping: bool = True
    connect_timeout: int = 10
    command_timeout: int = 60
    application_name: str = "ia_influencer_agent"


class DatabaseConnection:
    """
    Enterprise-grade database connection manager with connection pooling,
    failover, monitoring, and automatic recovery capabilities.
    """
    
    _instance = None
    _lock = asyncio.Lock()
    
    def __init__(self):
        self.connections: Dict[str, Any] = {}
        self.connection_pools: Dict[str, Any] = {}
        self.connection_states: Dict[str, ConnectionState] = {}
        self.connection_configs: Dict[str, ConnectionConfig] = {}
        self.health_check_tasks: Dict[str, asyncio.Task] = {}
        self.metrics: Dict[str, Dict[str, Any]] = {}
        self._initialized = False
        
    @classmethod
    async def get_instance(cls) -> 'DatabaseConnection':
        """Get singleton instance with async initialization"""
        if cls._instance is None:
            async with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
                    await cls._instance.initialize()
        return cls._instance
    
    async def initialize(self):
        """Initialize all database connections"""
        if self._initialized:
            return
            
        logger.info("Initializing database connections...")
        
        # Initialize PostgreSQL primary connection
        await self._initialize_postgresql()
        
        # Initialize Redis connections
        await self._initialize_redis()
        
        # Initialize read replicas if configured
        await self._initialize_read_replicas()
        
        # Start health monitoring
        await self._start_health_monitoring()
        
        self._initialized = True
        logger.info("Database connections initialized successfully")
    
    async def _initialize_postgresql(self):
        """Initialize PostgreSQL connection with pooling"""
        try:
            config = ConnectionConfig(
                host=settings.DATABASE_HOST,
                port=settings.DATABASE_PORT,
                database=settings.DATABASE_NAME,
                username=settings.DATABASE_USER,
                password=settings.DATABASE_PASSWORD,
                pool_size=settings.DATABASE_POOL_SIZE,
                max_overflow=settings.DATABASE_MAX_OVERFLOW,
                pool_timeout=settings.DATABASE_POOL_TIMEOUT
            )
            
            self.connection_configs["postgresql_primary"] = config
            
            # Create async engine for modern async operations
            database_url = (
                f"postgresql+asyncpg://{config.username}:{config.password}"
                f"@{config.host}:{config.port}/{config.database}"
            )
            
            self.connections["postgresql_async"] = create_async_engine(
                database_url,
                poolclass=QueuePool,
                pool_size=config.pool_size,
                max_overflow=config.max_overflow,
                pool_timeout=config.pool_timeout,
                pool_recycle=config.pool_recycle,
                pool_pre_ping=config.pool_pre_ping,
                echo=settings.DATABASE_ECHO,
                future=True
            )
            
            # Create sync engine for backward compatibility
            sync_database_url = (
                f"postgresql+psycopg2://{config.username}:{config.password}"
                f"@{config.host}:{config.port}/{config.database}"
            )
            
            self.connections["postgresql_sync"] = create_engine(
                sync_database_url,
                poolclass=QueuePool,
                pool_size=config.pool_size,
                max_overflow=config.max_overflow,
                pool_timeout=config.pool_timeout,
                pool_recycle=config.pool_recycle,
                pool_pre_ping=config.pool_pre_ping,
                echo=settings.DATABASE_ECHO
            )
            
            # Test connection
            async with self.connections["postgresql_async"].begin() as conn:
                await conn.execute(text("SELECT 1"))
            
            self.connection_states["postgresql_primary"] = ConnectionState.CONNECTED
            logger.info("PostgreSQL primary connection established")
            
        except Exception as e:
            logger.error(f"Failed to initialize PostgreSQL connection: {e}")
            self.connection_states["postgresql_primary"] = ConnectionState.ERROR
            raise
    
    async def _initialize_redis(self):
        """Initialize Redis connections"""
        try:
            # Primary Redis connection
            self.connections["redis_primary"] = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                password=settings.REDIS_PASSWORD,
                db=settings.REDIS_DB,
                encoding="utf-8",
                decode_responses=True,
                socket_timeout=settings.REDIS_SOCKET_TIMEOUT,
                socket_connect_timeout=settings.REDIS_CONNECT_TIMEOUT,
                health_check_interval=30,
                retry_on_timeout=True,
                max_connections=100
            )
            
            # Test Redis connection
            await asyncio.get_event_loop().run_in_executor(
                None, self.connections["redis_primary"].ping
            )
            
            # Cache-specific Redis connection
            self.connections["redis_cache"] = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                password=settings.REDIS_PASSWORD,
                db=settings.REDIS_CACHE_DB or 1,
                encoding="utf-8",
                decode_responses=True,
                socket_timeout=settings.REDIS_SOCKET_TIMEOUT,
                socket_connect_timeout=settings.REDIS_CONNECT_TIMEOUT,
                health_check_interval=30,
                retry_on_timeout=True,
                max_connections=50
            )
            
            # Session Redis connection
            self.connections["redis_sessions"] = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                password=settings.REDIS_PASSWORD,
                db=settings.REDIS_SESSION_DB or 2,
                encoding="utf-8",
                decode_responses=True,
                socket_timeout=settings.REDIS_SOCKET_TIMEOUT,
                socket_connect_timeout=settings.REDIS_CONNECT_TIMEOUT,
                health_check_interval=30,
                retry_on_timeout=True,
                max_connections=50
            )
            
            self.connection_states["redis_primary"] = ConnectionState.CONNECTED
            self.connection_states["redis_cache"] = ConnectionState.CONNECTED
            self.connection_states["redis_sessions"] = ConnectionState.CONNECTED
            
            logger.info("Redis connections established")
            
        except Exception as e:
            logger.error(f"Failed to initialize Redis connections: {e}")
            self.connection_states["redis_primary"] = ConnectionState.ERROR
            raise
    
    async def _initialize_read_replicas(self):
        """Initialize read replica connections if configured"""
        if not hasattr(settings, 'DATABASE_READ_REPLICAS') or not settings.DATABASE_READ_REPLICAS:
            return
            
        for i, replica_config in enumerate(settings.DATABASE_READ_REPLICAS):
            try:
                replica_name = f"postgresql_read_{i}"
                database_url = (
                    f"postgresql+asyncpg://{replica_config['username']}:{replica_config['password']}"
                    f"@{replica_config['host']}:{replica_config['port']}/{replica_config['database']}"
                )
                
                self.connections[replica_name] = create_async_engine(
                    database_url,
                    poolclass=QueuePool,
                    pool_size=replica_config.get('pool_size', 10),
                    max_overflow=replica_config.get('max_overflow', 20),
                    pool_timeout=replica_config.get('pool_timeout', 30),
                    pool_recycle=3600,
                    pool_pre_ping=True,
                    echo=False
                )
                
                # Test connection
                async with self.connections[replica_name].begin() as conn:
                    await conn.execute(text("SELECT 1"))
                
                self.connection_states[replica_name] = ConnectionState.CONNECTED
                logger.info(f"Read replica {replica_name} connection established")
                
            except Exception as e:
                logger.error(f"Failed to initialize read replica {replica_name}: {e}")
                self.connection_states[replica_name] = ConnectionState.ERROR
    
    async def _start_health_monitoring(self):
        """Start background health monitoring tasks"""
        for connection_name in self.connections.keys():
            if connection_name not in self.health_check_tasks:
                task = asyncio.create_task(
                    self._health_check_loop(connection_name)
                )
                self.health_check_tasks[connection_name] = task
    
    async def _health_check_loop(self, connection_name: str):
        """Background health check loop for a specific connection"""
        while True:
            try:
                await asyncio.sleep(30)  # Check every 30 seconds
                await self._perform_health_check(connection_name)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Health check error for {connection_name}: {e}")
    
    async def _perform_health_check(self, connection_name: str):
        """Perform health check for a specific connection"""
        try:
            connection = self.connections.get(connection_name)
            if not connection:
                return
            
            start_time = time.time()
            
            if "postgresql" in connection_name:
                async with connection.begin() as conn:
                    await conn.execute(text("SELECT 1"))
            elif "redis" in connection_name:
                await asyncio.get_event_loop().run_in_executor(
                    None, connection.ping
                )
            
            response_time = time.time() - start_time
            
            # Update metrics
            if connection_name not in self.metrics:
                self.metrics[connection_name] = {
                    'total_checks': 0,
                    'successful_checks': 0,
                    'avg_response_time': 0,
                    'last_check_time': 0,
                    'last_error': None
                }
            
            metrics = self.metrics[connection_name]
            metrics['total_checks'] += 1
            metrics['successful_checks'] += 1
            metrics['avg_response_time'] = (
                (metrics['avg_response_time'] * (metrics['total_checks'] - 1) + response_time) 
                / metrics['total_checks']
            )
            metrics['last_check_time'] = time.time()
            
            if self.connection_states[connection_name] != ConnectionState.CONNECTED:
                self.connection_states[connection_name] = ConnectionState.CONNECTED
                logger.info(f"Connection {connection_name} restored")
                
        except Exception as e:
            logger.warning(f"Health check failed for {connection_name}: {e}")
            self.connection_states[connection_name] = ConnectionState.ERROR
            
            # Update error metrics
            if connection_name in self.metrics:
                self.metrics[connection_name]['last_error'] = str(e)
    
    def get_connection(self, connection_name: str) -> Any:
        """Get a specific database connection"""
        if connection_name not in self.connections:
            raise ValueError(f"Unknown connection: {connection_name}")
        
        if self.connection_states.get(connection_name) != ConnectionState.CONNECTED:
            logger.warning(f"Connection {connection_name} is not healthy")
        
        return self.connections[connection_name]
    
    def get_postgresql_engine(self, async_mode: bool = True) -> Any:
        """Get PostgreSQL engine (async by default)"""
        if async_mode:
            return self.get_connection("postgresql_async")
        else:
            return self.get_connection("postgresql_sync")
    
    def get_redis_connection(self, connection_type: str = "primary") -> redis.Redis:
        """Get Redis connection by type"""
        connection_map = {
            "primary": "redis_primary",
            "cache": "redis_cache", 
            "sessions": "redis_sessions"
        }
        
        connection_name = connection_map.get(connection_type, "redis_primary")
        return self.get_connection(connection_name)
    
    def get_read_replica(self, replica_index: int = 0) -> Any:
        """Get a read replica connection"""
        replica_name = f"postgresql_read_{replica_index}"
        
        if replica_name not in self.connections:
            logger.warning(f"Read replica {replica_name} not available, falling back to primary")
            return self.get_postgresql_engine()
        
        return self.get_connection(replica_name)
    
    def get_connection_health(self) -> Dict[str, Any]:
        """Get health status of all connections"""
        return {
            "states": dict(self.connection_states),
            "metrics": dict(self.metrics),
            "active_connections": len(self.connections),
            "health_check_tasks": len(self.health_check_tasks)
        }
    
    async def close_all_connections(self):
        """Close all database connections gracefully"""
        logger.info("Closing all database connections...")
        
        # Cancel health check tasks
        for task in self.health_check_tasks.values():
            task.cancel()
        
        await asyncio.gather(
            *self.health_check_tasks.values(), 
            return_exceptions=True
        )
        
        # Close connections
        for name, connection in self.connections.items():
            try:
                if "postgresql" in name:
                    await connection.dispose()
                elif "redis" in name:
                    await asyncio.get_event_loop().run_in_executor(
                        None, connection.close
                    )
                logger.info(f"Connection {name} closed")
            except Exception as e:
                logger.error(f"Error closing connection {name}: {e}")
        
        # Reset state
        self.connections.clear()
        self.connection_states.clear()
        self.health_check_tasks.clear()
        self._initialized = False
        
        logger.info("All database connections closed")


class ConnectionPool:
    """
    Advanced connection pool manager with load balancing and failover
    """
    
    def __init__(self, db_connection: DatabaseConnection):
        self.db_connection = db_connection
        self.pool_stats: Dict[str, Dict[str, int]] = {}
        self.load_balancer_index = 0
    
    async def get_connection(self, 
                           connection_type: str = "postgresql",
                           read_only: bool = False,
                           preferred_replica: Optional[int] = None) -> Any:
        """
        Get connection with intelligent routing
        
        Args:
            connection_type: Type of connection (postgresql, redis)
            read_only: Whether this is a read-only operation
            preferred_replica: Preferred replica index for read operations
        """
        if connection_type == "postgresql":
            if read_only:
                return await self._get_read_connection(preferred_replica)
            else:
                return self.db_connection.get_postgresql_engine()
        elif connection_type == "redis":
            return self.db_connection.get_redis_connection()
        else:
            raise ValueError(f"Unsupported connection type: {connection_type}")
    
    async def _get_read_connection(self, preferred_replica: Optional[int] = None) -> Any:
        """Get read connection with load balancing"""
        # Check for read replicas
        available_replicas = []
        for name, state in self.db_connection.connection_states.items():
            if name.startswith("postgresql_read_") and state == ConnectionState.CONNECTED:
                replica_index = int(name.split("_")[-1])
                available_replicas.append(replica_index)
        
        if not available_replicas:
            # No replicas available, use primary
            return self.db_connection.get_postgresql_engine()
        
        # Use preferred replica if available and healthy
        if preferred_replica is not None and preferred_replica in available_replicas:
            return self.db_connection.get_read_replica(preferred_replica)
        
        # Round-robin load balancing
        selected_replica = available_replicas[self.load_balancer_index % len(available_replicas)]
        self.load_balancer_index += 1
        
        return self.db_connection.get_read_replica(selected_replica)
    
    def get_pool_statistics(self) -> Dict[str, Any]:
        """Get connection pool statistics"""
        stats = {}
        
        for name, connection in self.db_connection.connections.items():
            if hasattr(connection, 'pool'):
                pool = connection.pool
                stats[name] = {
                    'size': getattr(pool, 'size', 0),
                    'checked_out': getattr(pool, 'checked_out', 0),
                    'invalid': getattr(pool, 'invalid', 0),
                    'overflow': getattr(pool, 'overflow', 0)
                }
        
        return stats


class SessionManager:
    """
    Enterprise session manager with automatic transaction handling
    """
    
    def __init__(self):
        self.db_connection = None
        self.session_factories: Dict[str, Any] = {}
        self.active_sessions: Dict[str, List[Any]] = {}
    
    async def initialize(self):
        """Initialize session manager"""
        self.db_connection = await DatabaseConnection.get_instance()
        
        # Create async session factory
        async_engine = self.db_connection.get_postgresql_engine(async_mode=True)
        self.session_factories["async"] = async_sessionmaker(
            bind=async_engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
            autocommit=False
        )
        
        # Create sync session factory
        sync_engine = self.db_connection.get_postgresql_engine(async_mode=False)
        self.session_factories["sync"] = sessionmaker(
            bind=sync_engine,
            expire_on_commit=False,
            autoflush=False,
            autocommit=False
        )
    
    @asynccontextmanager
    async def get_async_session(self):
        """Get async database session with automatic cleanup"""
        if "async" not in self.session_factories:
            await self.initialize()
        
        session = self.session_factories["async"]()
        session_id = id(session)
        
        if "async" not in self.active_sessions:
            self.active_sessions["async"] = []
        self.active_sessions["async"].append(session_id)
        
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
            if session_id in self.active_sessions["async"]:
                self.active_sessions["async"].remove(session_id)
    
    @contextmanager
    def get_sync_session(self):
        """Get sync database session with automatic cleanup"""
        if "sync" not in self.session_factories:
            raise RuntimeError("SessionManager not initialized")
        
        session = self.session_factories["sync"]()
        session_id = id(session)
        
        if "sync" not in self.active_sessions:
            self.active_sessions["sync"] = []
        self.active_sessions["sync"].append(session_id)
        
        try:
            yield session
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
            if session_id in self.active_sessions["sync"]:
                self.active_sessions["sync"].remove(session_id)
    
    def get_session_statistics(self) -> Dict[str, Any]:
        """Get session statistics"""
        return {
            "active_sessions": {
                session_type: len(sessions) 
                for session_type, sessions in self.active_sessions.items()
            },
            "session_factories": list(self.session_factories.keys())
        }


class TransactionManager:
    """
    Enterprise transaction manager with nested transaction support
    """
    
    def __init__(self):
        self.session_manager = SessionManager()
        self.transaction_history: List[Dict[str, Any]] = []
        self.active_transactions: Dict[str, Dict[str, Any]] = {}
    
    @asynccontextmanager
    async def transaction(self, 
                         isolation_level: str = "READ_COMMITTED",
                         read_only: bool = False):
        """
        Async transaction context manager with configurable isolation
        
        Args:
            isolation_level: SQL isolation level
            read_only: Whether transaction is read-only
        """
        transaction_id = f"txn_{int(time.time() * 1000)}"
        start_time = time.time()
        
        self.active_transactions[transaction_id] = {
            "start_time": start_time,
            "isolation_level": isolation_level,
            "read_only": read_only,
            "status": "active"
        }
        
        async with self.session_manager.get_async_session() as session:
            transaction = session.begin()
            
            try:
                # Configure isolation level
                if isolation_level != "READ_COMMITTED":
                    await session.execute(
                        text(f"SET TRANSACTION ISOLATION LEVEL {isolation_level}")
                    )
                
                if read_only:
                    await session.execute(text("SET TRANSACTION READ ONLY"))
                
                async with transaction:
                    yield session
                
                self.active_transactions[transaction_id]["status"] = "committed"
                
            except Exception as e:
                self.active_transactions[transaction_id]["status"] = "rolled_back"
                self.active_transactions[transaction_id]["error"] = str(e)
                raise
            
            finally:
                # Record transaction history
                end_time = time.time()
                duration = end_time - start_time
                
                transaction_record = {
                    "transaction_id": transaction_id,
                    "start_time": start_time,
                    "end_time": end_time,
                    "duration": duration,
                    "isolation_level": isolation_level,
                    "read_only": read_only,
                    "status": self.active_transactions[transaction_id]["status"]
                }
                
                if "error" in self.active_transactions[transaction_id]:
                    transaction_record["error"] = self.active_transactions[transaction_id]["error"]
                
                self.transaction_history.append(transaction_record)
                
                # Keep only last 1000 transactions
                if len(self.transaction_history) > 1000:
                    self.transaction_history = self.transaction_history[-1000:]
                
                # Remove from active transactions
                del self.active_transactions[transaction_id]
    
    def get_transaction_statistics(self) -> Dict[str, Any]:
        """Get transaction statistics"""
        if not self.transaction_history:
            return {
                "total_transactions": 0,
                "active_transactions": len(self.active_transactions),
                "avg_duration": 0,
                "success_rate": 0
            }
        
        successful = len([t for t in self.transaction_history if t["status"] == "committed"])
        total = len(self.transaction_history)
        avg_duration = sum(t["duration"] for t in self.transaction_history) / total
        
        return {
            "total_transactions": total,
            "active_transactions": len(self.active_transactions),
            "successful_transactions": successful,
            "failed_transactions": total - successful,
            "success_rate": successful / total * 100 if total > 0 else 0,
            "avg_duration": avg_duration,
            "recent_transactions": self.transaction_history[-10:]
        }


class ReadReplicaManager:
    """
    Read replica manager with intelligent routing and failover
    """
    
    def __init__(self, db_connection: DatabaseConnection):
        self.db_connection = db_connection
        self.replica_weights: Dict[str, float] = {}
        self.replica_health_scores: Dict[str, float] = {}
        self.query_routing_stats: Dict[str, int] = {}
    
    async def route_read_query(self, 
                              query_complexity: str = "simple",
                              data_freshness_required: str = "eventual") -> Any:
        """
        Intelligently route read queries to optimal replica
        
        Args:
            query_complexity: simple, moderate, complex
            data_freshness_required: strict, moderate, eventual
        """
        # Get available replicas
        available_replicas = self._get_healthy_replicas()
        
        if not available_replicas:
            # No replicas available, route to primary
            self.query_routing_stats["primary"] = self.query_routing_stats.get("primary", 0) + 1
            return self.db_connection.get_postgresql_engine()
        
        # Select best replica based on routing logic
        selected_replica = self._select_optimal_replica(
            available_replicas, 
            query_complexity, 
            data_freshness_required
        )
        
        self.query_routing_stats[selected_replica] = self.query_routing_stats.get(selected_replica, 0) + 1
        
        if selected_replica == "primary":
            return self.db_connection.get_postgresql_engine()
        else:
            replica_index = int(selected_replica.split("_")[-1])
            return self.db_connection.get_read_replica(replica_index)
    
    def _get_healthy_replicas(self) -> List[str]:
        """Get list of healthy replica connections"""
        healthy_replicas = []
        
        for name, state in self.db_connection.connection_states.items():
            if name.startswith("postgresql_read_") and state == ConnectionState.CONNECTED:
                healthy_replicas.append(name)
        
        return healthy_replicas
    
    def _select_optimal_replica(self, 
                               available_replicas: List[str],
                               query_complexity: str,
                               data_freshness_required: str) -> str:
        """Select optimal replica based on various factors"""
        
        # For strict freshness requirements, use primary
        if data_freshness_required == "strict":
            return "primary"
        
        # Score each replica
        replica_scores = {}
        
        for replica_name in available_replicas:
            score = 1.0
            
            # Consider replica health
            if replica_name in self.replica_health_scores:
                score *= self.replica_health_scores[replica_name]
            
            # Consider current load
            current_load = self.query_routing_stats.get(replica_name, 0)
            if current_load > 0:
                score *= (1.0 / (1.0 + current_load * 0.1))  # Penalize high load
            
            # Consider query complexity
            if query_complexity == "complex":
                # Prefer replicas with better specs (if configured)
                weight = self.replica_weights.get(replica_name, 1.0)
                score *= weight
            
            replica_scores[replica_name] = score
        
        # Select replica with highest score
        if replica_scores:
            return max(replica_scores.keys(), key=lambda k: replica_scores[k])
        else:
            return "primary"
    
    async def update_replica_health_scores(self):
        """Update health scores for all replicas"""
        for replica_name in self._get_healthy_replicas():
            try:
                # Get metrics for this replica
                if replica_name in self.db_connection.metrics:
                    metrics = self.db_connection.metrics[replica_name]
                    
                    # Calculate health score based on various factors
                    response_time_score = max(0, 1.0 - (metrics['avg_response_time'] / 10.0))
                    success_rate = metrics['successful_checks'] / max(1, metrics['total_checks'])
                    
                    health_score = (response_time_score * 0.4) + (success_rate * 0.6)
                    self.replica_health_scores[replica_name] = max(0.1, min(1.0, health_score))
                
            except Exception as e:
                logger.warning(f"Error updating health score for {replica_name}: {e}")
                self.replica_health_scores[replica_name] = 0.1
    
    def get_routing_statistics(self) -> Dict[str, Any]:
        """Get read routing statistics"""
        total_queries = sum(self.query_routing_stats.values())
        
        routing_distribution = {}
        if total_queries > 0:
            for replica, count in self.query_routing_stats.items():
                routing_distribution[replica] = (count / total_queries) * 100
        
        return {
            "total_queries_routed": total_queries,
            "routing_distribution": routing_distribution,
            "available_replicas": len(self._get_healthy_replicas()),
            "replica_health_scores": dict(self.replica_health_scores)
        }


# Event listeners for connection monitoring
@event.listens_for(pool.Pool, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """Set connection-level pragmas for PostgreSQL"""
    if hasattr(dbapi_connection, 'set_session'):
        # Set session parameters for PostgreSQL
        cursor = dbapi_connection.cursor()
        cursor.execute("SET application_name = 'ia_influencer_agent'")
        cursor.execute("SET statement_timeout = '300s'")
        cursor.execute("SET lock_timeout = '30s'")
        cursor.close()


@event.listens_for(pool.Pool, "checkout")
def receive_checkout(dbapi_connection, connection_record, connection_proxy):
    """Log connection checkout events"""
    logger.debug("Database connection checked out")


@event.listens_for(pool.Pool, "checkin")
def receive_checkin(dbapi_connection, connection_record):
    """Log connection checkin events"""
    logger.debug("Database connection returned to pool")
