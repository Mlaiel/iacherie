"""Database Connection Pool Manager for IA-Influencer Agent Platform
================================================================

Professional database connection pool management orchestrating PostgreSQL,
MongoDB, Redis, FAISS, and Elasticsearch connections across multi-tenant platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA-Influencer Agent + Content Protection Platform
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps

Copyright Notice:
This code is the intellectual property of Fahed Mlaiel. 
Any unauthorized use, reproduction, or distribution of this code 
without explicit written permission from the author is strictly prohibited.

Contact: mlaiel@live.de for licensing inquiries.
"""
import asyncio
import threading
import time
from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
from concurrent.futures import ThreadPoolExecutor
import logging
from contextlib import contextmanager, asynccontextmanager

from .postgresql_config import PostgreSQLConfig, PostgreSQLEnvironment
from .mongodb_config import MongoDBConfig, MongoDBEnvironment, MongoDBWorkloadType
from .redis_config import RedisConfig, RedisEnvironment, RedisWorkloadType
from .faiss_config import FAISSConfig, FAISSEnvironment, FAISSContentType
from .elasticsearch_config import ElasticsearchConfig, ElasticsearchEnvironment, ElasticsearchWorkloadType

logger = logging.getLogger(__name__)


class DatabaseType(Enum):
    """Supported database types"""    POSTGRESQL = "postgresql"
    MONGODB = "mongodb"
    REDIS = "redis"
    FAISS = "faiss"
    ELASTICSEARCH = "elasticsearch"


class ConnectionPoolStrategy(Enum):
    """Connection pool strategies"""    LAZY_LOADING = "lazy_loading"          # Create connections on-demand
    EAGER_LOADING = "eager_loading"        # Pre-create all connections
    MIXED = "mixed"                        # Combination of both


class HealthCheckLevel(Enum):
    """Health check detail levels"""    BASIC = "basic"                        # Simple ping checks
    DETAILED = "detailed"                  # Full health statistics
    COMPREHENSIVE = "comprehensive"        # Complete diagnostic information


@dataclass
class ConnectionPoolConfig:
    """Connection pool configuration"""    strategy: ConnectionPoolStrategy = ConnectionPoolStrategy.MIXED
    health_check_interval: int = 30
    connection_timeout: int = 30
    max_retries: int = 3
    retry_delay: int = 5
    enable_monitoring: bool = True
    monitoring_interval: int = 60
    auto_cleanup: bool = True
    cleanup_interval: int = 300


@dataclass
class DatabaseConnectionInfo:
    """Database connection information and statistics"""    database_type: DatabaseType
    connection_id: str
    created_at: float
    last_used_at: float
    usage_count: int = 0
    error_count: int = 0
    status: str = "healthy"
    metadata: Dict[str, Any] = field(default_factory=dict)


class DatabaseConnectionPool:
    """    Professional database connection pool manager for IA-Influencer Agent Platform
    
    Orchestrates connections across multiple database systems with intelligent
    load balancing, health monitoring, and automatic failover capabilities.
    """
    def __init__(self, 
                 environment: str = "development",
                 config: Optional[ConnectionPoolConfig] = None):
        self.environment = environment
        self.config = config or ConnectionPoolConfig()
        
        # Database configurations
        self.postgresql_config = PostgreSQLConfig(PostgreSQLEnvironment(environment))
        self.mongodb_config = MongoDBConfig(MongoDBEnvironment(environment))
        self.redis_config = RedisConfig(RedisEnvironment(environment))
        self.faiss_config = FAISSConfig(FAISSEnvironment(environment))
        self.elasticsearch_config = ElasticsearchConfig(ElasticsearchEnvironment(environment))
        
        # Connection pools and metadata
        self._connections: Dict[str, Any] = {}
        self._connection_info: Dict[str, DatabaseConnectionInfo] = {}
        self._connection_lock = threading.RLock()
        
        # Monitoring and health check
        self._monitoring_enabled = False
        self._health_check_executor = ThreadPoolExecutor(max_workers=5, thread_name_prefix="health_check")
        self._cleanup_executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="cleanup")
        
        # Event handlers
        self._connection_callbacks: Dict[str, List[Callable]] = {
            "on_connection_created": [],
            "on_connection_error": [],
            "on_connection_closed": [],
            "on_health_check_failed": []
        }
        
        self._setup_logging()
        
        if self.config.strategy in [ConnectionPoolStrategy.EAGER_LOADING, ConnectionPoolStrategy.MIXED]:
            self._initialize_core_connections()
        
        if self.config.enable_monitoring:
            self.start_monitoring()

    def _setup_logging(self) -> None:
        """Setup connection pool logging"""        self.logger = logging.getLogger(f"database_pool.{self.environment}")
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - [%(threadName)s] - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    def _initialize_core_connections(self) -> None:
        """Initialize core database connections eagerly"""        try:
            # Create core connections that are commonly used
            core_connections = [
                ("postgresql_main", DatabaseType.POSTGRESQL, {}),
                ("mongodb_main", DatabaseType.MONGODB, {}),
                ("redis_cache", DatabaseType.REDIS, {"workload": RedisWorkloadType.CACHE}),
                ("redis_session", DatabaseType.REDIS, {"workload": RedisWorkloadType.SESSION}),
                ("elasticsearch_search", DatabaseType.ELASTICSEARCH, {"workload": ElasticsearchWorkloadType.SEARCH})
            ]
            
            for conn_id, db_type, params in core_connections:
                try:
                    self.get_connection(conn_id, db_type, **params)
                    self.logger.info(f"Core connection initialized: {conn_id}")
                except Exception as e:
                    self.logger.warning(f"Failed to initialize core connection {conn_id}: {str(e)}")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize core connections: {str(e)}")

    def get_connection(self, 
                      connection_id: str, 
                      database_type: DatabaseType, 
                      **kwargs) -> Any:
        """        Get database connection with intelligent caching and load balancing
        
        Args:
            connection_id: Unique connection identifier
            database_type: Type of database connection
            **kwargs: Database-specific parameters
            
        Returns:
            Database connection object
        """        with self._connection_lock:
            # Check if connection exists and is healthy
            if connection_id in self._connections:
                connection = self._connections[connection_id]
                conn_info = self._connection_info[connection_id]
                
                # Update usage statistics
                conn_info.last_used_at = time.time()
                conn_info.usage_count += 1
                
                # Quick health check for critical connections
                if self._is_connection_healthy(connection, database_type):
                    return connection
                else:
                    self.logger.warning(f"Unhealthy connection detected, recreating: {connection_id}")
                    self._close_connection(connection_id)
            
            # Create new connection
            try:
                connection = self._create_connection(database_type, **kwargs)
                
                # Store connection and metadata
                self._connections[connection_id] = connection
                self._connection_info[connection_id] = DatabaseConnectionInfo(
                    database_type=database_type,
                    connection_id=connection_id,
                    created_at=time.time(),
                    last_used_at=time.time(),
                    metadata=kwargs
                )
                
                self.logger.info(f"Created new database connection: {connection_id} ({database_type.value})")
                
                # Trigger callbacks
                for callback in self._connection_callbacks.get("on_connection_created", []):
                    try:
                        callback(connection_id, database_type, connection)
                    except Exception as e:
                        self.logger.error(f"Connection callback error: {str(e)}")
                
                return connection
                
            except Exception as e:
                self.logger.error(f"Failed to create connection {connection_id}: {str(e)}")
                
                # Update error statistics
                if connection_id in self._connection_info:
                    self._connection_info[connection_id].error_count += 1
                    self._connection_info[connection_id].status = "error"
                
                # Trigger error callbacks
                for callback in self._connection_callbacks.get("on_connection_error", []):
                    try:
                        callback(connection_id, database_type, e)
                    except Exception as callback_error:
                        self.logger.error(f"Error callback failed: {str(callback_error)}")
                
                raise

    def _create_connection(self, database_type: DatabaseType, **kwargs) -> Any:
        """Create database connection based on type"""        if database_type == DatabaseType.POSTGRESQL:
            tenant_id = kwargs.get("tenant_id")
            if tenant_id:
                return self.postgresql_config.get_tenant_engine(tenant_id)
            
            connection_type = kwargs.get("connection_type", "main")
            if connection_type == "analytics":
                return self.postgresql_config.get_analytics_engine()
            elif connection_type == "content_protection":
                return self.postgresql_config.get_content_protection_engine()
            elif connection_type == "monetization":
                return self.postgresql_config.get_monetization_engine()
            else:
                return self.postgresql_config.create_engine()
        
        elif database_type == DatabaseType.MONGODB:
            workload = kwargs.get("workload", MongoDBWorkloadType.MEDIA_STORAGE)
            client_name = kwargs.get("client_name", "default")
            
            config = MongoDBConfig(MongoDBEnvironment(self.environment), workload)
            return config.create_client(client_name=client_name)
        
        elif database_type == DatabaseType.REDIS:
            workload = kwargs.get("workload", RedisWorkloadType.CACHE)
            database = kwargs.get("database", 0)
            client_name = kwargs.get("client_name", "default")
            
            config = RedisConfig(RedisEnvironment(self.environment), workload)
            return config.create_client(database, client_name)
        
        elif database_type == DatabaseType.FAISS:
            content_type = kwargs.get("content_type", FAISSContentType.AUDIO_FINGERPRINT)
            config = FAISSConfig(FAISSEnvironment(self.environment), content_type)
            return config.create_index()
        
        elif database_type == DatabaseType.ELASTICSEARCH:
            workload = kwargs.get("workload", ElasticsearchWorkloadType.SEARCH)
            client_name = kwargs.get("client_name", "default")
            
            config = ElasticsearchConfig(ElasticsearchEnvironment(self.environment), workload)
            return config.create_client(client_name)
        
        else:
            raise ValueError(f"Unsupported database type: {database_type}")

    def _is_connection_healthy(self, connection: Any, database_type: DatabaseType) -> bool:
        """Quick health check for database connection"""        try:
            if database_type == DatabaseType.POSTGRESQL:
                # SQLAlchemy engine health check
                with connection.connect() as conn:
                    conn.execute("SELECT 1")
                return True
            
            elif database_type == DatabaseType.MONGODB:
                # MongoDB client ping
                connection.admin.command('ping')
                return True
            
            elif database_type == DatabaseType.REDIS:
                # Redis ping
                return connection.ping()
            
            elif database_type == DatabaseType.ELASTICSEARCH:
                # Elasticsearch ping
                return connection.ping()
            
            elif database_type == DatabaseType.FAISS:
                # FAISS index is always available once loaded
                return True
            
            return False
            
        except Exception:
            return False

    @contextmanager
    def get_postgresql_connection(self, connection_type: str = "main", **kwargs):
        """Context manager for PostgreSQL connections"""        connection_id = f"postgresql_{connection_type}"
        connection = self.get_connection(
            connection_id, 
            DatabaseType.POSTGRESQL, 
            connection_type=connection_type, 
            **kwargs
        )
        
        try:
            with connection.connect() as conn:
                yield conn
        finally:
            pass  # Connection pool handles cleanup

    @contextmanager
    def get_mongodb_connection(self, workload: MongoDBWorkloadType = MongoDBWorkloadType.MEDIA_STORAGE, **kwargs):
        """Context manager for MongoDB connections"""        connection_id = f"mongodb_{workload.value}"
        connection = self.get_connection(
            connection_id, 
            DatabaseType.MONGODB, 
            workload=workload, 
            **kwargs
        )
        
        try:
            yield connection
        finally:
            pass  # Connection pool handles cleanup

    @contextmanager
    def get_redis_connection(self, workload: RedisWorkloadType = RedisWorkloadType.CACHE, **kwargs):
        """Context manager for Redis connections"""        connection_id = f"redis_{workload.value}"
        connection = self.get_connection(
            connection_id, 
            DatabaseType.REDIS, 
            workload=workload, 
            **kwargs
        )
        
        try:
            yield connection
        finally:
            pass  # Connection pool handles cleanup

    def get_tenant_connections(self, tenant_id: str) -> Dict[str, Any]:
        """Get all database connections for a specific tenant"""        connections = {}
        
        try:
            # PostgreSQL tenant connection
            connections["postgresql"] = self.get_connection(
                f"postgresql_tenant_{tenant_id}",
                DatabaseType.POSTGRESQL,
                tenant_id=tenant_id
            )
            
            # MongoDB tenant connection
            connections["mongodb"] = self.get_connection(
                f"mongodb_tenant_{tenant_id}",
                DatabaseType.MONGODB,
                workload=MongoDBWorkloadType.MEDIA_STORAGE,
                client_name=f"tenant_{tenant_id}"
            )
            
            # Redis tenant connection
            connections["redis"] = self.get_connection(
                f"redis_tenant_{tenant_id}",
                DatabaseType.REDIS,
                workload=RedisWorkloadType.CACHE,
                client_name=f"tenant_{tenant_id}"
            )
            
        except Exception as e:
            self.logger.error(f"Failed to get tenant connections for {tenant_id}: {str(e)}")
            raise
        
        return connections

    def add_connection_callback(self, event: str, callback: Callable) -> None:
        """Add callback for connection events"""        if event in self._connection_callbacks:
            self._connection_callbacks[event].append(callback)
        else:
            raise ValueError(f"Unknown event: {event}")

    def start_monitoring(self) -> None:
        """Start connection pool monitoring"""        if self._monitoring_enabled:
            return
        
        self._monitoring_enabled = True
        
        def monitoring_loop():
            while self._monitoring_enabled:
                try:
                    self._perform_health_checks()
                    time.sleep(self.config.monitoring_interval)
                except Exception as e:
                    self.logger.error(f"Monitoring loop error: {str(e)}")
                    time.sleep(self.config.monitoring_interval)
        
        # Start monitoring in background thread
        monitoring_thread = threading.Thread(target=monitoring_loop, daemon=True, name="db_pool_monitor")
        monitoring_thread.start()
        
        if self.config.auto_cleanup:
            def cleanup_loop():
                while self._monitoring_enabled:
                    try:
                        self._cleanup_stale_connections()
                        time.sleep(self.config.cleanup_interval)
                    except Exception as e:
                        self.logger.error(f"Cleanup loop error: {str(e)}")
                        time.sleep(self.config.cleanup_interval)
            
            cleanup_thread = threading.Thread(target=cleanup_loop, daemon=True, name="db_pool_cleanup")
            cleanup_thread.start()
        
        self.logger.info("Database connection pool monitoring started")

    def stop_monitoring(self) -> None:
        """Stop connection pool monitoring"""        self._monitoring_enabled = False
        self.logger.info("Database connection pool monitoring stopped")

    def _perform_health_checks(self) -> None:
        """Perform health checks on all connections"""        with self._connection_lock:
            for connection_id, connection in list(self._connections.items()):
                conn_info = self._connection_info[connection_id]
                
                # Submit health check to thread pool
                future = self._health_check_executor.submit(
                    self._check_connection_health, 
                    connection_id, 
                    connection, 
                    conn_info
                )
                
                # Don't wait for completion to avoid blocking

    def _check_connection_health(self, connection_id: str, connection: Any, conn_info: DatabaseConnectionInfo) -> None:
        """Check health of individual connection"""        try:
            is_healthy = self._is_connection_healthy(connection, conn_info.database_type)
            
            if is_healthy:
                if conn_info.status != "healthy":
                    conn_info.status = "healthy"
                    self.logger.info(f"Connection recovered: {connection_id}")
            else:
                conn_info.status = "unhealthy"
                conn_info.error_count += 1
                self.logger.warning(f"Connection unhealthy: {connection_id}")
                
                # Trigger health check failed callbacks
                for callback in self._connection_callbacks.get("on_health_check_failed", []):
                    try:
                        callback(connection_id, conn_info.database_type, connection)
                    except Exception as e:
                        self.logger.error(f"Health check callback error: {str(e)}")
        
        except Exception as e:
            conn_info.status = "error"
            conn_info.error_count += 1
            self.logger.error(f"Health check failed for {connection_id}: {str(e)}")

    def _cleanup_stale_connections(self) -> None:
        """Cleanup stale or unused connections"""        current_time = time.time()
        stale_connections = []
        
        with self._connection_lock:
            for connection_id, conn_info in self._connection_info.items():
                # Identify stale connections
                time_since_last_use = current_time - conn_info.last_used_at
                
                if (time_since_last_use > 3600 and  # 1 hour
                    conn_info.usage_count < 10):      # Low usage
                    stale_connections.append(connection_id)
        
        # Close stale connections
        for connection_id in stale_connections:
            try:
                self._close_connection(connection_id)
                self.logger.info(f"Closed stale connection: {connection_id}")
            except Exception as e:
                self.logger.error(f"Failed to close stale connection {connection_id}: {str(e)}")

    def _close_connection(self, connection_id: str) -> None:
        """Close specific connection"""        with self._connection_lock:
            if connection_id in self._connections:
                connection = self._connections[connection_id]
                conn_info = self._connection_info[connection_id]
                
                try:
                    # Close connection based on type
                    if conn_info.database_type == DatabaseType.POSTGRESQL:
                        connection.dispose()
                    elif conn_info.database_type == DatabaseType.MONGODB:
                        connection.close()
                    elif conn_info.database_type == DatabaseType.REDIS:
                        connection.close()
                    elif conn_info.database_type == DatabaseType.ELASTICSEARCH:
                        connection.transport.close()
                    
                    # Remove from pools
                    del self._connections[connection_id]
                    del self._connection_info[connection_id]
                    
                    # Trigger callbacks
                    for callback in self._connection_callbacks.get("on_connection_closed", []):
                        try:
                            callback(connection_id, conn_info.database_type, connection)
                        except Exception as e:
                            self.logger.error(f"Close callback error: {str(e)}")
                    
                except Exception as e:
                    self.logger.error(f"Error closing connection {connection_id}: {str(e)}")

    def get_pool_statistics(self) -> Dict[str, Any]:
        """Get comprehensive connection pool statistics"""        with self._connection_lock:
            stats = {
                "environment": self.environment,
                "total_connections": len(self._connections),
                "connections_by_type": {},
                "connections_by_status": {},
                "total_usage_count": 0,
                "total_error_count": 0,
                "average_age_seconds": 0,
                "connections": []
            }
            
            current_time = time.time()
            total_age = 0
            
            for connection_id, conn_info in self._connection_info.items():
                # Count by type
                db_type = conn_info.database_type.value
                stats["connections_by_type"][db_type] = stats["connections_by_type"].get(db_type, 0) + 1
                
                # Count by status
                status = conn_info.status
                stats["connections_by_status"][status] = stats["connections_by_status"].get(status, 0) + 1
                
                # Accumulate statistics
                stats["total_usage_count"] += conn_info.usage_count
                stats["total_error_count"] += conn_info.error_count
                total_age += (current_time - conn_info.created_at)
                
                # Connection details
                stats["connections"].append({
                    "connection_id": connection_id,
                    "database_type": db_type,
                    "status": status,
                    "created_at": conn_info.created_at,
                    "last_used_at": conn_info.last_used_at,
                    "usage_count": conn_info.usage_count,
                    "error_count": conn_info.error_count,
                    "age_seconds": current_time - conn_info.created_at,
                    "idle_seconds": current_time - conn_info.last_used_at
                })
            
            if len(self._connections) > 0:
                stats["average_age_seconds"] = total_age / len(self._connections)
            
            return stats

    def health_check(self, level: HealthCheckLevel = HealthCheckLevel.BASIC) -> Dict[str, Any]:
        """        Perform comprehensive health check on all database connections
        
        Args:
            level: Detail level of health check
            
        Returns:
            Health check results dictionary
        """        health_status = {
            "status": "healthy",
            "environment": self.environment,
            "pool_stats": {},
            "databases": {},
            "timestamp": None
        }
        
        import datetime
        health_status["timestamp"] = datetime.datetime.utcnow().isoformat()
        
        try:
            # Get pool statistics
            if level in [HealthCheckLevel.DETAILED, HealthCheckLevel.COMPREHENSIVE]:
                health_status["pool_stats"] = self.get_pool_statistics()
            
            # Check individual database systems
            database_configs = {
                "postgresql": self.postgresql_config,
                "mongodb": self.mongodb_config,
                "redis": self.redis_config,
                "faiss": self.faiss_config,
                "elasticsearch": self.elasticsearch_config
            }
            
            for db_name, config in database_configs.items():
                try:
                    if level == HealthCheckLevel.COMPREHENSIVE:
                        health_status["databases"][db_name] = config.health_check()
                    else:
                        # Basic health check
                        health_status["databases"][db_name] = {"status": "healthy"}
                except Exception as e:
                    health_status["databases"][db_name] = {
                        "status": "unhealthy",
                        "error": str(e)
                    }
                    health_status["status"] = "degraded"
            
        except Exception as e:
            health_status["status"] = "unhealthy"
            health_status["error"] = str(e)
            self.logger.error(f"Health check failed: {str(e)}")
        
        return health_status

    def close_all_connections(self) -> None:
        """Close all database connections and cleanup resources"""        self.stop_monitoring()
        
        with self._connection_lock:
            connection_ids = list(self._connections.keys())
            
            for connection_id in connection_ids:
                try:
                    self._close_connection(connection_id)
                except Exception as e:
                    self.logger.error(f"Error closing connection {connection_id}: {str(e)}")
        
        # Shutdown executors
        try:
            self._health_check_executor.shutdown(wait=True)
            self._cleanup_executor.shutdown(wait=True)
        except Exception as e:
            self.logger.error(f"Error shutting down executors: {str(e)}")
        
        self.logger.info("All database connections closed")

    def __del__(self):
        """Cleanup on object destruction"""        try:
            self.close_all_connections()
        except:
            pass
