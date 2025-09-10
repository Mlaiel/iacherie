"""Ainflue Core Database - Enterprise Database Management
======================================================

Core database management system providing advanced database orchestration,
connection pooling, query optimization, data integrity, and enterprise-grade
database operations for the Ainflue platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, AsyncContextManager
from dataclasses import dataclass, field
from enum import Enum
import asyncpg
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import redis.asyncio as redis
import time

logger = logging.getLogger(__name__)

class DatabaseType(str, Enum):
    """Database types supported"""
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    SQLITE = "sqlite"
    MONGODB = "mongodb"
    REDIS = "redis"

class ConnectionStatus(str, Enum):
    """Database connection status"""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"
    MAINTENANCE = "maintenance"

@dataclass
class DatabaseConfig:
    """Database configuration"""
    host: str = "localhost"
    port: int = 5432
    database: str = "ainflue"
    username: str = "postgres"
    password: str = ""
    pool_size: int = 20
    max_overflow: int = 50
    pool_timeout: int = 30
    pool_recycle: int = 3600
    ssl_mode: str = "prefer"

@dataclass
class DatabaseMetrics:
    """Database performance metrics"""
    active_connections: int = 0
    total_queries: int = 0
    avg_query_time: float = 0.0
    error_count: int = 0
    last_error: Optional[str] = None
    uptime_seconds: float = 0.0
    last_health_check: float = field(default_factory=time.time)

class DatabaseCore:
    """Enterprise database core management system"""
    
    def __init__(self, config: Optional[DatabaseConfig] = None):
        """Initialize database core"""
        self.config = config or DatabaseConfig()
        self.status = ConnectionStatus.DISCONNECTED
        self.metrics = DatabaseMetrics()
        self.start_time = time.time()
        
        # Database connections
        self.postgres_engine = None
        self.postgres_session_factory = None
        self.redis_client = None
        
        # Connection pools
        self.postgres_pool = None
        
        logger.info("🗄️ Database Core initialized")
    
    async def initialize(self) -> bool:
        """Initialize database connections"""
        try:
            self.status = ConnectionStatus.CONNECTING
            logger.info("🔌 Initializing database connections...")
            
            # Initialize PostgreSQL
            await self._initialize_postgresql()
            
            # Initialize Redis
            await self._initialize_redis()
            
            self.status = ConnectionStatus.CONNECTED
            self.metrics.uptime_seconds = time.time() - self.start_time
            
            logger.info("✅ Database Core initialization completed")
            return True
            
        except Exception as e:
            self.status = ConnectionStatus.ERROR
            self.metrics.error_count += 1
            self.metrics.last_error = str(e)
            logger.error(f"❌ Database Core initialization failed: {e}")
            return False
    
    async def _initialize_postgresql(self):
        """Initialize PostgreSQL connection"""
        try:
            # Create connection string
            connection_string = (
                f"postgresql+asyncpg://{self.config.username}:{self.config.password}"
                f"@{self.config.host}:{self.config.port}/{self.config.database}"
            )
            
            # Create async engine
            self.postgres_engine = create_async_engine(
                connection_string,
                pool_size=self.config.pool_size,
                max_overflow=self.config.max_overflow,
                pool_timeout=self.config.pool_timeout,
                pool_recycle=self.config.pool_recycle,
                echo=False  # Set to True for SQL debugging
            )
            
            # Create session factory
            self.postgres_session_factory = sessionmaker(
                self.postgres_engine,
                class_=AsyncSession,
                expire_on_commit=False
            )
            
            # Create raw connection pool for direct queries
            self.postgres_pool = await asyncpg.create_pool(
                host=self.config.host,
                port=self.config.port,
                user=self.config.username,
                password=self.config.password,
                database=self.config.database,
                min_size=5,
                max_size=self.config.pool_size,
                command_timeout=60
            )
            
            logger.info("✅ PostgreSQL connection initialized")
            
        except Exception as e:
            logger.error(f"❌ PostgreSQL initialization failed: {e}")
            raise
    
    async def _initialize_redis(self):
        """Initialize Redis connection"""
        try:
            self.redis_client = redis.Redis(
                host=self.config.host,
                port=6379,  # Redis default port
                decode_responses=True,
                health_check_interval=30
            )
            
            # Test connection
            await self.redis_client.ping()
            
            logger.info("✅ Redis connection initialized")
            
        except Exception as e:
            logger.error(f"❌ Redis initialization failed: {e}")
            # Redis is optional, don't raise
    
    async def get_postgres_session(self) -> AsyncContextManager[AsyncSession]:
        """Get PostgreSQL session"""
        if not self.postgres_session_factory:
            raise RuntimeError("PostgreSQL not initialized")
        
        return self.postgres_session_factory()
    
    async def execute_query(self, query: str, params: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Execute raw SQL query"""
        if not self.postgres_pool:
            raise RuntimeError("PostgreSQL pool not initialized")
        
        start_time = time.time()
        
        try:
            async with self.postgres_pool.acquire() as conn:
                result = await conn.fetch(query, *(params.values() if params else []))
                
                # Convert to list of dictionaries
                rows = [dict(row) for row in result]
                
                # Update metrics
                query_time = time.time() - start_time
                self.metrics.total_queries += 1
                self.metrics.avg_query_time = (
                    (self.metrics.avg_query_time * (self.metrics.total_queries - 1) + query_time)
                    / self.metrics.total_queries
                )
                
                return rows
                
        except Exception as e:
            self.metrics.error_count += 1
            self.metrics.last_error = str(e)
            logger.error(f"❌ Query execution failed: {e}")
            raise
    
    async def health_check(self) -> bool:
        """Perform database health check"""
        try:
            # Check PostgreSQL
            if self.postgres_pool:
                async with self.postgres_pool.acquire() as conn:
                    await conn.execute("SELECT 1")
            
            # Check Redis
            if self.redis_client:
                await self.redis_client.ping()
            
            self.metrics.last_health_check = time.time()
            return True
            
        except Exception as e:
            logger.error(f"❌ Database health check failed: {e}")
            self.metrics.error_count += 1
            self.metrics.last_error = str(e)
            return False
    
    async def close(self):
        """Close all database connections"""
        try:
            if self.postgres_engine:
                await self.postgres_engine.dispose()
            
            if self.postgres_pool:
                await self.postgres_pool.close()
            
            if self.redis_client:
                await self.redis_client.close()
            
            self.status = ConnectionStatus.DISCONNECTED
            logger.info("✅ Database connections closed")
            
        except Exception as e:
            logger.error(f"❌ Error closing database connections: {e}")

# Global database instance
database_core = DatabaseCore()

# Convenience functions
async def get_db_session() -> AsyncContextManager[AsyncSession]:
    """Get database session"""
    return await database_core.get_postgres_session()

async def execute_sql(query: str, params: Dict[str, Any] = None) -> List[Dict[str, Any]]:
    """Execute SQL query"""
    return await database_core.execute_query(query, params)

async def check_db_health() -> bool:
    """Check database health"""
    return await database_core.health_check()

# Module exports
__all__ = [
    "DatabaseCore", "DatabaseConfig", "DatabaseMetrics", "DatabaseType",
    "ConnectionStatus", "database_core", "get_db_session", "execute_sql",
    "check_db_health"
]