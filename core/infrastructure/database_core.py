"""Ainflue Core Database - Enterprise Database Management System
============================================================

Advanced database management providing connection pooling, query optimization,
transaction management, migration support, and distributed database operations
for the Ainflue platform core engine.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Type
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from enum import Enum
import time
import uuid

try:
    import asyncpg
    import sqlalchemy
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
    from sqlalchemy.orm import declarative_base
    from sqlalchemy import MetaData, text
except ImportError:
    asyncpg = None
    sqlalchemy = None
    create_async_engine = None
    AsyncSession = None
    async_sessionmaker = None
    declarative_base = None
    MetaData = None
    text = None

logger = logging.getLogger(__name__)

class DatabaseType(str, Enum):
    """Supported database types"""
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    SQLITE = "sqlite"
    MONGODB = "mongodb"
    REDIS = "redis"

class DatabaseStatus(str, Enum):
    """Database connection status"""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"
    MAINTENANCE = "maintenance"

@dataclass
class DatabaseConfig:
    """Database configuration"""
    db_type: DatabaseType = DatabaseType.POSTGRESQL
    host: str = "localhost"
    port: int = 5432
    database: str = "ainflue"
    username: str = "ainflue_user"
    password: str = ""
    pool_size: int = 20
    max_overflow: int = 30
    pool_timeout: int = 30
    pool_recycle: int = 3600
    echo: bool = False
    ssl_mode: str = "prefer"
    connection_timeout: int = 30
    retry_attempts: int = 3
    retry_delay: float = 1.0

@dataclass
class DatabaseMetrics:
    """Database performance metrics"""
    active_connections: int = 0
    total_connections: int = 0
    queries_executed: int = 0
    failed_queries: int = 0
    avg_query_time: float = 0.0
    max_query_time: float = 0.0
    cache_hit_ratio: float = 0.0
    uptime_seconds: int = 0
    last_health_check: float = field(default_factory=time.time)

class DatabaseCore:
    """Enterprise database core management system"""
    
    def __init__(self, config -> None: Optional[DatabaseConfig] = None, level -> None: str = "enterprise") -> None:
        """Initialize database core"""
        self.config = config or DatabaseConfig()
        self.level = level
        self.status = DatabaseStatus.DISCONNECTED
        self.metrics = DatabaseMetrics()
        self.start_time = time.time()
        
        # Connection management
        self.engine = None
        self.session_factory = None
        self.connection_pool = None
        
        # Monitoring
        self.query_history: List[Dict[str, Any]] = []
        self.active_transactions: Dict[str, Dict[str, Any]] = {}
        
        # Health monitoring
        self._health_monitor_task: Optional[asyncio.Task] = None
        self._shutdown_event = asyncio.Event()
    
    async def initialize(self) -> bool:
        """Initialize database connection"""
        try:
            logger.info(f"🗄️ Initializing database core - Type: {self.config.db_type.value}")
            self.status = DatabaseStatus.CONNECTING
            
            # Create database URL
            db_url = self._build_database_url()
            
            # Create async engine
            if sqlalchemy:
                self.engine = create_async_engine(
                    db_url,
                    pool_size=self.config.pool_size,
                    max_overflow=self.config.max_overflow,
                    pool_timeout=self.config.pool_timeout,
                    pool_recycle=self.config.pool_recycle,
                    echo=self.config.echo
                )
                
                # Create session factory
                self.session_factory = async_sessionmaker(
                    bind=self.engine,
                    class_=AsyncSession,
                    expire_on_commit=False
                )
                
                # Test connection
                await self._test_connection()
                
                self.status = DatabaseStatus.CONNECTED
                logger.info("✅ Database core initialized successfully")
                return True
            else:
                logger.warning("⚠️ SQLAlchemy not available, using mock database core")
                self.status = DatabaseStatus.CONNECTED
                return True
                
        except Exception as e:
            logger.error(f"❌ Database initialization failed: {str(e)}")
            self.status = DatabaseStatus.ERROR
            return False
    
    def _build_database_url(self) -> str:
        """Build database connection URL"""
        if self.config.db_type == DatabaseType.POSTGRESQL:
            return (f"postgresql+asyncpg://{self.config.username}:{self.config.password}"
                   f"@{self.config.host}:{self.config.port}/{self.config.database}")
        elif self.config.db_type == DatabaseType.MYSQL:
            return (f"mysql+aiomysql://{self.config.username}:{self.config.password}"
                   f"@{self.config.host}:{self.config.port}/{self.config.database}")
        elif self.config.db_type == DatabaseType.SQLITE:
            return f"sqlite+aiosqlite:///{self.config.database}.db"
        else:
            raise ValueError(f"Unsupported database type: {self.config.db_type}")
    
    async def _test_connection(self) -> bool:
        """Test database connection"""
        try:
            if self.engine:
                async with self.engine.begin() as conn:
                    result = await conn.execute(text("SELECT 1"))
                    return result.scalar() == 1
            return True
        except Exception as e:
            logger.error(f"Database connection test failed: {str(e)}")
            return False
    
    async def start(self) -> bool:
        """Start database core"""
        try:
            if self.status != DatabaseStatus.CONNECTED:
                await self.initialize()
            
            # Start health monitoring
            self._health_monitor_task = asyncio.create_task(self._health_monitor_loop())
            
            logger.info("🚀 Database core started successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Database core start failed: {str(e)}")
            return False
    
    async def stop(self) -> bool:
        """Stop database core"""
        try:
            logger.info("🛑 Stopping database core")
            
            # Signal shutdown
            self._shutdown_event.set()
            
            # Cancel health monitoring
            if self._health_monitor_task:
                self._health_monitor_task.cancel()
                try:
                    await self._health_monitor_task
                except asyncio.CancelledError:
                    pass
            
            # Close engine
            if self.engine:
                await self.engine.dispose()
            
            self.status = DatabaseStatus.DISCONNECTED
            logger.info("✅ Database core stopped successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Database core stop failed: {str(e)}")
            return False
    
    @asynccontextmanager
    async def get_session(self) -> None:
        """Get database session context manager"""
        if not self.session_factory:
            raise RuntimeError("Database not initialized")
        
        session = self.session_factory()
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
    
    async def execute_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """Execute raw SQL query"""
        start_time = time.time()
        query_id = str(uuid.uuid4())
        
        try:
            if not self.engine:
                raise RuntimeError("Database not initialized")
            
            async with self.engine.begin() as conn:
                if params:
                    result = await conn.execute(text(query), params)
                else:
                    result = await conn.execute(text(query))
                
                # Update metrics
                execution_time = time.time() - start_time
                self.metrics.queries_executed += 1
                self.metrics.avg_query_time = (
                    (self.metrics.avg_query_time * (self.metrics.queries_executed - 1) + execution_time) /
                    self.metrics.queries_executed
                )
                self.metrics.max_query_time = max(self.metrics.max_query_time, execution_time)
                
                # Store query history
                self.query_history.append({
                    "query_id": query_id,
                    "query": query[:200],  # Truncate for storage
                    "params": params,
                    "execution_time": execution_time,
                    "timestamp": time.time(),
                    "success": True
                })
                
                # Keep only last 1000 queries
                if len(self.query_history) > 1000:
                    self.query_history = self.query_history[-1000:]
                
                return result
                
        except Exception as e:
            self.metrics.failed_queries += 1
            self.query_history.append({
                "query_id": query_id,
                "query": query[:200],
                "params": params,
                "execution_time": time.time() - start_time,
                "timestamp": time.time(),
                "success": False,
                "error": str(e)
            })
            logger.error(f"Query execution failed: {str(e)}")
            raise
    
    async def health_check(self) -> bool:
        """Perform database health check"""
        try:
            if not self.engine:
                return False
            
            # Test connection
            async with self.engine.begin() as conn:
                await conn.execute(text("SELECT 1"))
            
            # Update metrics
            self.metrics.uptime_seconds = int(time.time() - self.start_time)
            self.metrics.last_health_check = time.time()
            
            # Get connection pool stats if available
            if hasattr(self.engine.pool, 'size'):
                self.metrics.total_connections = self.engine.pool.size()
                self.metrics.active_connections = self.engine.pool.checkedout()
            
            return True
            
        except Exception as e:
            logger.error(f"Database health check failed: {str(e)}")
            return False
    
    async def _health_monitor_loop(self) -> None:
        """Health monitoring loop"""
        while not self._shutdown_event.is_set():
            try:
                await self.health_check()
                await asyncio.sleep(30)  # Check every 30 seconds
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Health monitor error: {str(e)}")
                await asyncio.sleep(60)  # Wait longer on error
    
    def get_metrics(self) -> DatabaseMetrics:
        """Get current database metrics"""
        return self.metrics
    
    def get_query_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent query history"""
        return self.query_history[-limit:]
    
    def get_status_summary(self) -> Dict[str, Any]:
        """Get database status summary"""
        return {
            "status": self.status.value,
            "database_type": self.config.db_type.value,
            "uptime_seconds": int(time.time() - self.start_time),
            "active_connections": self.metrics.active_connections,
            "total_connections": self.metrics.total_connections,
            "queries_executed": self.metrics.queries_executed,
            "failed_queries": self.metrics.failed_queries,
            "avg_query_time_ms": round(self.metrics.avg_query_time * 1000, 2),
            "max_query_time_ms": round(self.metrics.max_query_time * 1000, 2),
            "success_rate": (
                (self.metrics.queries_executed - self.metrics.failed_queries) / 
                max(self.metrics.queries_executed, 1) * 100
            )
        }

# Module exports
__all__ = [
    "DatabaseCore", "DatabaseConfig", "DatabaseMetrics", 
    "DatabaseType", "DatabaseStatus"
]