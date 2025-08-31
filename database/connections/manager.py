"""Database Connection Manager - IA Influencer Agent Platform

Central orchestrator for all database connections supporting the content creator ecosystem.
Manages PostgreSQL, Redis, MongoDB, Elasticsearch, Vector stores, and Object storage.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""
import asyncio
import logging
from typing import Dict, Any, Optional, List, Type
from contextlib import asynccontextmanager
from dataclasses import dataclass
from enum import Enum

from .postgresql import PostgreSQLConnectionHandler
from .redis import RedisConnectionHandler
from .mongodb import MongoDBConnectionHandler
from .elasticsearch import ElasticsearchConnectionHandler
from .vector_stores import VectorStoreConnectionHandler
from .object_storage import ObjectStorageConnectionHandler
from .health_monitor import DatabaseHealthMonitor
from .pool_manager import ConnectionPoolManager
from .transaction_manager import TransactionManager
from .tenant_manager import TenantConnectionManager


class DatabaseType(Enum):
    """Supported database types in the platform"""    POSTGRESQL = "postgresql"
    REDIS = "redis"
    MONGODB = "mongodb"
    ELASTICSEARCH = "elasticsearch"
    VECTOR_STORE = "vector_store"
    OBJECT_STORAGE = "object_storage"


@dataclass
class ConnectionConfig:
    """Database connection configuration"""    host: str
    port: int
    database: str
    username: str
    password: str
    ssl_enabled: bool = True
    pool_size: int = 20
    max_overflow: int = 30
    timeout: int = 30
    retry_attempts: int = 3
    tenant_isolation: bool = True
    encryption_key: Optional[str] = None


class DatabaseConnectionManager:
    """    Central database connection manager for IA Influencer platform.
    
    Orchestrates connections to all database systems required for:
    - Content creator management
    - AI processing and fingerprinting  
    - Content protection and monitoring
    - Revenue tracking and monetization
    - Collaboration and distribution
    """    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Connection handlers for each database type
        self.handlers: Dict[DatabaseType, Any] = {}
        
        # Infrastructure components
        self.health_monitor = DatabaseHealthMonitor()
        self.pool_manager = ConnectionPoolManager()
        self.transaction_manager = TransactionManager()
        self.tenant_manager = TenantConnectionManager()
        
        # Connection state
        self._initialized = False
        self._connections_healthy = False
        
    async def initialize(self) -> None:
        """Initialize all database connections and components"""        if self._initialized:
            return
            
        try:
            self.logger.info("Initializing database connection manager...")
            
            # Initialize connection handlers
            await self._initialize_handlers()
            
            # Setup health monitoring
            await self.health_monitor.initialize(self.handlers)
            
            # Initialize pool manager
            await self.pool_manager.initialize(self.handlers)
            
            # Setup transaction manager
            await self.transaction_manager.initialize(self.handlers)
            
            # Initialize tenant manager
            await self.tenant_manager.initialize(self.handlers)
            
            # Verify all connections
            await self._verify_connections()
            
            self._initialized = True
            self._connections_healthy = True
            
            self.logger.info("Database connection manager initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize database connections: {e}")
            raise
    
    async def _initialize_handlers(self) -> None:
        """Initialize individual database handlers"""        
        # PostgreSQL - Primary relational database
        if "postgresql" in self.config:
            self.handlers[DatabaseType.POSTGRESQL] = PostgreSQLConnectionHandler(
                self.config["postgresql"]
            )
            await self.handlers[DatabaseType.POSTGRESQL].initialize()
        
        # Redis - Caching and real-time operations
        if "redis" in self.config:
            self.handlers[DatabaseType.REDIS] = RedisConnectionHandler(
                self.config["redis"]
            )
            await self.handlers[DatabaseType.REDIS].initialize()
        
        # MongoDB - Content metadata and analytics
        if "mongodb" in self.config:
            self.handlers[DatabaseType.MONGODB] = MongoDBConnectionHandler(
                self.config["mongodb"]
            )
            await self.handlers[DatabaseType.MONGODB].initialize()
        
        # Elasticsearch - Search and indexing
        if "elasticsearch" in self.config:
            self.handlers[DatabaseType.ELASTICSEARCH] = ElasticsearchConnectionHandler(
                self.config["elasticsearch"]
            )
            await self.handlers[DatabaseType.ELASTICSEARCH].initialize()
        
        # Vector stores - Content fingerprinting similarity
        if "vector_store" in self.config:
            self.handlers[DatabaseType.VECTOR_STORE] = VectorStoreConnectionHandler(
                self.config["vector_store"]
            )
            await self.handlers[DatabaseType.VECTOR_STORE].initialize()
        
        # Object storage - Content files and assets
        if "object_storage" in self.config:
            self.handlers[DatabaseType.OBJECT_STORAGE] = ObjectStorageConnectionHandler(
                self.config["object_storage"]
            )
            await self.handlers[DatabaseType.OBJECT_STORAGE].initialize()
    
    async def _verify_connections(self) -> None:
        """Verify all database connections are working"""        verification_tasks = []
        
        for db_type, handler in self.handlers.items():
            task = asyncio.create_task(
                self._verify_single_connection(db_type, handler)
            )
            verification_tasks.append(task)
        
        results = await asyncio.gather(*verification_tasks, return_exceptions=True)
        
        failed_connections = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                db_type = list(self.handlers.keys())[i]
                failed_connections.append(db_type)
                self.logger.error(f"Connection verification failed for {db_type}: {result}")
        
        if failed_connections:
            raise ConnectionError(f"Failed to verify connections: {failed_connections}")
    
    async def _verify_single_connection(self, db_type: DatabaseType, handler: Any) -> None:
        """Verify a single database connection"""        try:
            await handler.health_check()
            self.logger.info(f"Connection verified for {db_type.value}")
        except Exception as e:
            self.logger.error(f"Connection verification failed for {db_type.value}: {e}")
            raise
    
    async def get_connection(self, db_type: DatabaseType, tenant_id: Optional[str] = None):
        """Get a database connection for the specified type and tenant"""        if not self._initialized:
            await self.initialize()
        
        if db_type not in self.handlers:
            raise ValueError(f"Database type {db_type.value} not configured")
        
        handler = self.handlers[db_type]
        
        if tenant_id and hasattr(handler, 'get_tenant_connection'):
            return await handler.get_tenant_connection(tenant_id)
        
        return await handler.get_connection()
    
    @asynccontextmanager
    async def transaction(self, tenant_id: Optional[str] = None):
        """Context manager for cross-database transactions"""        async with self.transaction_manager.transaction(tenant_id) as tx:
            yield tx
    
    async def execute_query(self, 
                          db_type: DatabaseType, 
                          query: str, 
                          params: Optional[Dict] = None,
                          tenant_id: Optional[str] = None) -> Any:
        """Execute a query on the specified database"""        connection = await self.get_connection(db_type, tenant_id)
        return await connection.execute(query, params)
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get connection metrics for all databases"""        metrics = {}
        
        for db_type, handler in self.handlers.items():
            if hasattr(handler, 'get_metrics'):
                metrics[db_type.value] = await handler.get_metrics()
        
        # Add health monitor metrics
        metrics['health'] = await self.health_monitor.get_metrics()
        
        # Add pool manager metrics
        metrics['pools'] = await self.pool_manager.get_metrics()
        
        return metrics
    
    async def health_check(self) -> Dict[str, Any]:
        """Comprehensive health check for all database connections"""        return await self.health_monitor.comprehensive_health_check()
    
    async def shutdown(self) -> None:
        """Gracefully shutdown all database connections"""        if not self._initialized:
            return
        
        self.logger.info("Shutting down database connections...")
        
        # Shutdown components in reverse order
        await self.tenant_manager.shutdown()
        await self.transaction_manager.shutdown()
        await self.pool_manager.shutdown()
        await self.health_monitor.shutdown()
        
        # Shutdown individual handlers
        shutdown_tasks = []
        for handler in self.handlers.values():
            task = asyncio.create_task(handler.shutdown())
            shutdown_tasks.append(task)
        
        await asyncio.gather(*shutdown_tasks, return_exceptions=True)
        
        self._initialized = False
        self._connections_healthy = False
        
        self.logger.info("Database connections shutdown completed")


# Global connection manager instance
_connection_manager: Optional[DatabaseConnectionManager] = None


def get_connection_manager() -> DatabaseConnectionManager:
    """Get the global database connection manager instance"""    global _connection_manager
    
    if _connection_manager is None:
        raise RuntimeError("Database connection manager not initialized")
    
    return _connection_manager


def initialize_connection_manager(config: Dict[str, Any]) -> DatabaseConnectionManager:
    """Initialize the global database connection manager"""    global _connection_manager
    
    _connection_manager = DatabaseConnectionManager(config)
    return _connection_manager
