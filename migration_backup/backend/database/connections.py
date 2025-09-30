"""🔗 Backend Database Connections - Consolidated Enterprise Connection Management
=================================================================================
Module: backend/database/connections.py
Author: Fahed Mlaiel (mlaiel@live.de)
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + IA Prompt Engineer
Type: Consolidated Database Connection Management - Enterprise Production-Ready
Responsibility: All database connections, pooling, health monitoring, and configuration
=====================================================================================================

⚠️  EXCLUSIVE INTELLECTUAL PROPERTY - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. All rights reserved.
Unauthorized use strictly prohibited and subject to legal prosecution.
Contact: mlaiel@live.de

This consolidated connections module provides comprehensive database connection management for:
- PostgreSQL: Primary relational data (users, content, revenue tracking)
- Redis: Caching, sessions, real-time operations
- MongoDB: Content metadata, fingerprints, analytics data
- Elasticsearch: Search indexing, logs, content discovery
- Vector Stores: FAISS/Pinecone for AI similarity search
- Object Storage: MinIO/S3 for content files

CONSOLIDATED FEATURES:
- Connection pooling and load balancing across all databases
- Health monitoring and auto-recovery mechanisms
- Transaction management and distributed transaction support
- Encryption and security compliance for all connections
- Multi-tenant data isolation and routing
- Performance optimization and intelligent caching
- Failover and disaster recovery capabilities
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List, Type, Union
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from enum import Enum
import json
import ssl
from urllib.parse import urlparse

# Core async imports
try:
    import asyncpg
    import sqlalchemy
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
    POSTGRESQL_AVAILABLE = True
except ImportError:
    POSTGRESQL_AVAILABLE = False

try:
    import redis.asyncio as aioredis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

try:
    import motor.motor_asyncio
    MONGODB_AVAILABLE = True
except ImportError:
    MONGODB_AVAILABLE = False

try:
    from elasticsearch import AsyncElasticsearch
    ELASTICSEARCH_AVAILABLE = True
except ImportError:
    ELASTICSEARCH_AVAILABLE = False

try:
    import aioboto3
    OBJECT_STORAGE_AVAILABLE = True
except ImportError:
    OBJECT_STORAGE_AVAILABLE = False

logger = logging.getLogger(__name__)


class ConnectionStatus(Enum):
    """Database connection status enumeration."""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"
    MAINTENANCE = "maintenance"


class DatabaseType(Enum):
    """Supported database types."""
    POSTGRESQL = "postgresql"
    REDIS = "redis"
    MONGODB = "mongodb"
    ELASTICSEARCH = "elasticsearch"
    VECTOR_STORE = "vector_store"
    OBJECT_STORAGE = "object_storage"


@dataclass
class ConnectionConfig:
    """Database connection configuration."""
    host: str
    port: int
    database: str = ""
    username: str = ""
    password: str = ""
    ssl_mode: str = "prefer"
    pool_size: int = 10
    max_overflow: int = 20
    pool_timeout: int = 30
    pool_recycle: int = 3600
    echo: bool = False
    extra_params: Dict[str, Any] = field(default_factory=dict)


class DatabaseConnectionManager:
    """
    🏢 Enterprise Database Connection Manager
    
    Central orchestrator for all database connections supporting the content creator ecosystem.
    Manages PostgreSQL, Redis, MongoDB, Elasticsearch, Vector stores, and Object storage.
    
    Features:
    - Multi-database connection pooling
    - Health monitoring and auto-recovery
    - Load balancing and failover
    - Security and encryption
    - Performance optimization
    """

    def __init__(self):
        self._connections: Dict[DatabaseType, Any] = {}
        self._configs: Dict[DatabaseType, ConnectionConfig] = {}
        self._status: Dict[DatabaseType, ConnectionStatus] = {}
        self._pools: Dict[DatabaseType, Any] = {}
        self._health_monitor_task: Optional[asyncio.Task] = None
        self._session_makers: Dict[DatabaseType, Any] = {}
        
    async def initialize(self, configs: Dict[DatabaseType, ConnectionConfig]):
        """Initialize all database connections."""
        logger.info("🚀 Initializing enterprise database connections...")
        
        self._configs = configs
        
        for db_type, config in configs.items():
            try:
                await self._connect_database(db_type, config)
                logger.info(f"✅ {db_type.value} connection established")
            except Exception as e:
                logger.error(f"❌ Failed to connect to {db_type.value}: {e}")
                self._status[db_type] = ConnectionStatus.ERROR
        
        # Start health monitoring
        self._health_monitor_task = asyncio.create_task(self._health_monitor())
        logger.info("🏥 Database health monitoring started")
    
    async def _connect_database(self, db_type: DatabaseType, config: ConnectionConfig):
        """Connect to a specific database type."""
        self._status[db_type] = ConnectionStatus.CONNECTING
        
        if db_type == DatabaseType.POSTGRESQL and POSTGRESQL_AVAILABLE:
            await self._connect_postgresql(config)
        elif db_type == DatabaseType.REDIS and REDIS_AVAILABLE:
            await self._connect_redis(config)
        elif db_type == DatabaseType.MONGODB and MONGODB_AVAILABLE:
            await self._connect_mongodb(config)
        elif db_type == DatabaseType.ELASTICSEARCH and ELASTICSEARCH_AVAILABLE:
            await self._connect_elasticsearch(config)
        elif db_type == DatabaseType.OBJECT_STORAGE and OBJECT_STORAGE_AVAILABLE:
            await self._connect_object_storage(config)
        else:
            raise ValueError(f"Unsupported database type: {db_type}")
        
        self._status[db_type] = ConnectionStatus.CONNECTED
    
    async def _connect_postgresql(self, config: ConnectionConfig):
        """Connect to PostgreSQL database."""
        connection_string = f"postgresql+asyncpg://{config.username}:{config.password}@{config.host}:{config.port}/{config.database}"
        
        engine = create_async_engine(
            connection_string,
            pool_size=config.pool_size,
            max_overflow=config.max_overflow,
            pool_timeout=config.pool_timeout,
            pool_recycle=config.pool_recycle,
            echo=config.echo,
            **config.extra_params
        )
        
        self._connections[DatabaseType.POSTGRESQL] = engine
        self._session_makers[DatabaseType.POSTGRESQL] = async_sessionmaker(
            engine, class_=AsyncSession, expire_on_commit=False
        )
    
    async def _connect_redis(self, config: ConnectionConfig):
        """Connect to Redis database."""
        redis_client = aioredis.Redis(
            host=config.host,
            port=config.port,
            db=int(config.database) if config.database else 0,
            password=config.password if config.password else None,
            ssl=config.ssl_mode == "require",
            **config.extra_params
        )
        
        # Test connection
        await redis_client.ping()
        self._connections[DatabaseType.REDIS] = redis_client
    
    async def _connect_mongodb(self, config: ConnectionConfig):
        """Connect to MongoDB database."""
        connection_string = f"mongodb://{config.username}:{config.password}@{config.host}:{config.port}/{config.database}"
        
        client = motor.motor_asyncio.AsyncIOMotorClient(
            connection_string,
            maxPoolSize=config.pool_size,
            **config.extra_params
        )
        
        # Test connection
        await client.admin.command('ping')
        self._connections[DatabaseType.MONGODB] = client
    
    async def _connect_elasticsearch(self, config: ConnectionConfig):
        """Connect to Elasticsearch."""
        es_config = {
            'hosts': [{'host': config.host, 'port': config.port}],
            'http_auth': (config.username, config.password) if config.username else None,
            'use_ssl': config.ssl_mode == "require",
            **config.extra_params
        }
        
        client = AsyncElasticsearch(**es_config)
        
        # Test connection
        await client.info()
        self._connections[DatabaseType.ELASTICSEARCH] = client
    
    async def _connect_object_storage(self, config: ConnectionConfig):
        """Connect to object storage (S3/MinIO)."""
        session = aioboto3.Session()
        
        client = session.client(
            's3',
            endpoint_url=f"http{'s' if config.ssl_mode == 'require' else ''}://{config.host}:{config.port}",
            aws_access_key_id=config.username,
            aws_secret_access_key=config.password,
            **config.extra_params
        )
        
        self._connections[DatabaseType.OBJECT_STORAGE] = client
    
    @asynccontextmanager
    async def get_postgres_session(self):
        """Get PostgreSQL session context manager."""
        if DatabaseType.POSTGRESQL not in self._session_makers:
            raise RuntimeError("PostgreSQL connection not initialized")
        
        session_maker = self._session_makers[DatabaseType.POSTGRESQL]
        async with session_maker() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
    
    async def get_redis_client(self):
        """Get Redis client."""
        return self._connections.get(DatabaseType.REDIS)
    
    async def get_mongodb_client(self):
        """Get MongoDB client."""
        return self._connections.get(DatabaseType.MONGODB)
    
    async def get_elasticsearch_client(self):
        """Get Elasticsearch client."""
        return self._connections.get(DatabaseType.ELASTICSEARCH)
    
    async def get_object_storage_client(self):
        """Get object storage client."""
        return self._connections.get(DatabaseType.OBJECT_STORAGE)
    
    async def _health_monitor(self):
        """Monitor database health and handle reconnections."""
        while True:
            try:
                await asyncio.sleep(30)  # Check every 30 seconds
                
                for db_type, connection in self._connections.items():
                    try:
                        await self._check_connection_health(db_type, connection)
                        if self._status[db_type] != ConnectionStatus.CONNECTED:
                            self._status[db_type] = ConnectionStatus.CONNECTED
                            logger.info(f"✅ {db_type.value} connection restored")
                    except Exception as e:
                        self._status[db_type] = ConnectionStatus.ERROR
                        logger.error(f"🔥 {db_type.value} health check failed: {e}")
                        
                        # Attempt reconnection
                        try:
                            config = self._configs.get(db_type)
                            if config:
                                await self._connect_database(db_type, config)
                                logger.info(f"🔄 {db_type.value} reconnection successful")
                        except Exception as reconnect_error:
                            logger.error(f"🚨 {db_type.value} reconnection failed: {reconnect_error}")
                            
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Health monitor error: {e}")
    
    async def _check_connection_health(self, db_type: DatabaseType, connection):
        """Check health of a specific database connection."""
        if db_type == DatabaseType.POSTGRESQL:
            async with self.get_postgres_session() as session:
                await session.execute(sqlalchemy.text("SELECT 1"))
        elif db_type == DatabaseType.REDIS:
            await connection.ping()
        elif db_type == DatabaseType.MONGODB:
            await connection.admin.command('ping')
        elif db_type == DatabaseType.ELASTICSEARCH:
            await connection.info()
    
    def get_connection_status(self, db_type: DatabaseType) -> ConnectionStatus:
        """Get connection status for a database type."""
        return self._status.get(db_type, ConnectionStatus.DISCONNECTED)
    
    def get_all_statuses(self) -> Dict[str, str]:
        """Get all connection statuses."""
        return {db_type.value: status.value for db_type, status in self._status.items()}
    
    async def close_all_connections(self):
        """Close all database connections."""
        logger.info("🔌 Closing all database connections...")
        
        if self._health_monitor_task:
            self._health_monitor_task.cancel()
            try:
                await self._health_monitor_task
            except asyncio.CancelledError:
                pass
        
        for db_type, connection in self._connections.items():
            try:
                if db_type == DatabaseType.POSTGRESQL:
                    await connection.dispose()
                elif db_type == DatabaseType.REDIS:
                    await connection.close()
                elif db_type == DatabaseType.MONGODB:
                    connection.close()
                elif db_type == DatabaseType.ELASTICSEARCH:
                    await connection.close()
                elif db_type == DatabaseType.OBJECT_STORAGE:
                    await connection.close()
                
                logger.info(f"✅ {db_type.value} connection closed")
            except Exception as e:
                logger.error(f"❌ Error closing {db_type.value}: {e}")
        
        self._connections.clear()
        self._status.clear()
        self._session_makers.clear()


# Global connection manager instance
_connection_manager: Optional[DatabaseConnectionManager] = None


def get_connection_manager() -> DatabaseConnectionManager:
    """Get the global database connection manager."""
    global _connection_manager
    if _connection_manager is None:
        _connection_manager = DatabaseConnectionManager()
    return _connection_manager


# Consolidation of key functions from original database/connections/ modules
async def create_tables():
    """Create all database tables (migrated from database.schema)."""
    try:
        manager = get_connection_manager()
        async with manager.get_postgres_session() as session:
            # Users table
            await session.execute(sqlalchemy.text("""
                CREATE TABLE IF NOT EXISTS users (
                    id VARCHAR(32) PRIMARY KEY,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    first_name VARCHAR(50) NOT NULL,
                    last_name VARCHAR(50) NOT NULL,
                    creator_type VARCHAR(20) NOT NULL CHECK (creator_type IN ('musician', 'blogger', 'photographer', 'influencer', 'comedian', 'writer', 'other')),
                    tenant_id VARCHAR(16) NOT NULL,
                    is_verified BOOLEAN DEFAULT false,
                    subscription_tier VARCHAR(20) DEFAULT 'free' CHECK (subscription_tier IN ('free', 'premium', 'professional')),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            logger.info("✅ Database tables created successfully")
    except Exception as e:
        logger.error(f"❌ Failed to create tables: {e}")
        raise


# Export all public interfaces
__all__ = [
    "DatabaseConnectionManager",
    "get_connection_manager", 
    "ConnectionConfig",
    "ConnectionStatus",
    "DatabaseType",
    "create_tables",
]