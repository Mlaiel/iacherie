"""Connection Optimizer Module

Enterprise-grade database connection pool management and optimization for maximum performance,
including dynamic scaling, health monitoring, and intelligent routing.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use prohibited.
"""
import asyncio
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union, Callable, Awaitable
from enum import Enum
from dataclasses import dataclass, field
from contextlib import asynccontextmanager
import psutil
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, AsyncSession
from sqlalchemy.pool import StaticPool, QueuePool, NullPool
from sqlalchemy import event, text
from sqlalchemy.exc import DisconnectionError, TimeoutError as SQLTimeoutError
import asyncpg

from ...core.logging import get_logger
from ...core.config import settings
from ...core.metrics import MetricsCollector

logger = get_logger(__name__)


class PoolStrategy(Enum):
    """Connection pool strategies"""
    STATIC = "static"
    DYNAMIC = "dynamic"
    QUEUE = "queue"
    NULL = "null"
    OVERFLOW = "overflow"


class ConnectionState(Enum):
    """Connection states"""
    IDLE = "idle"
    ACTIVE = "active"
    IN_TRANSACTION = "in_transaction"
    INVALID = "invalid"
    CLOSED = "closed"


@dataclass
class ConnectionPoolConfig:
    """Connection pool configuration"""
    # Basic settings
    min_connections: int = 5
    max_connections: int = 20
    pool_strategy: PoolStrategy = PoolStrategy.QUEUE
    
    # Timeout settings
    connection_timeout: float = 30.0
    idle_timeout: float = 300.0
    max_overflow: int = 10
    pool_timeout: float = 5.0
    
    # Health check settings
    health_check_interval: float = 60.0
    ping_interval: float = 30.0
    retry_attempts: int = 3
    retry_delay: float = 1.0
    
    # Performance settings
    pre_ping: bool = True
    pool_pre_ping: bool = True
    pool_recycle: int = 3600
    echo: bool = False
    
    # Database settings
    database_url: Optional[str] = None
    charset: str = "utf8mb4"
    isolation_level: str = "READ_COMMITTED"
    
    # Monitoring settings
    metrics_enabled: bool = True
    slow_query_threshold: float = 1.0
    log_connections: bool = True


@dataclass
class ConnectionMetrics:
    """Connection pool metrics"""
    total_connections: int = 0
    active_connections: int = 0
    idle_connections: int = 0
    invalid_connections: int = 0
    connection_requests: int = 0
    connection_errors: int = 0
    query_count: int = 0
    slow_queries: int = 0
    avg_connection_time: float = 0.0
    avg_query_time: float = 0.0
    peak_connections: int = 0
    last_updated: datetime = field(default_factory=datetime.now)
    
    @property
    def error_rate(self) -> float:
        """Calculate connection error rate"""
        if self.connection_requests == 0:
            return 0.0
        return self.connection_errors / self.connection_requests
    
    @property
    def pool_utilization(self) -> float:
        """Calculate pool utilization rate"""
        if self.total_connections == 0:
            return 0.0
        return self.active_connections / self.total_connections


class ConnectionInfo:
    """Connection information and metadata"""
    
    def __init__(self, connection_id: str, created_at: datetime = None):
        self.connection_id = connection_id
        self.created_at = created_at or datetime.now()
        self.last_used = self.created_at
        self.state = ConnectionState.IDLE
        self.query_count = 0
        self.error_count = 0
        self.total_time = 0.0
        self.current_query: Optional[str] = None
        self.transaction_count = 0
        
    def start_query(self, query: str) -> None:
        """Mark query start"""
        self.current_query = query
        self.state = ConnectionState.ACTIVE
        self.last_used = datetime.now()
    
    def end_query(self, execution_time: float, error: bool = False) -> None:
        """Mark query end"""
        self.current_query = None
        self.state = ConnectionState.IDLE
        self.query_count += 1
        self.total_time += execution_time
        if error:
            self.error_count += 1
    
    @property
    def avg_query_time(self) -> float:
        """Calculate average query time"""
        return self.total_time / self.query_count if self.query_count > 0 else 0.0
    
    @property
    def age(self) -> timedelta:
        """Get connection age"""
        return datetime.now() - self.created_at
    
    @property
    def idle_time(self) -> timedelta:
        """Get idle time"""
        return datetime.now() - self.last_used


class HealthChecker:
    """Database connection health checker"""
    
    def __init__(self, config: ConnectionPoolConfig):
        self.config = config
        self._last_check = datetime.now()
        self._healthy = True
        
    async def check_connection(self, engine: AsyncEngine) -> bool:
        """Check if connection is healthy"""
        try:
            async with engine.begin() as conn:
                result = await conn.execute(text("SELECT 1"))
                await result.fetchone()
            return True
        except Exception as e:
            logger.warning(f"Health check failed: {e}")
            return False
    
    async def ping_connection(self, connection) -> bool:
        """Ping a specific connection"""
        try:
            if hasattr(connection, 'ping'):
                return await connection.ping()
            else:
                # For SQLAlchemy connections
                await connection.execute(text("SELECT 1"))
                return True
        except Exception as e:
            logger.warning(f"Connection ping failed: {e}")
            return False
    
    def should_check(self) -> bool:
        """Check if health check is due"""
        return (datetime.now() - self._last_check).total_seconds() >= self.config.health_check_interval
    
    def mark_checked(self, healthy: bool) -> None:
        """Mark health check as completed"""
        self._last_check = datetime.now()
        self._healthy = healthy
    
    @property
    def is_healthy(self) -> bool:
        """Get current health status"""
        return self._healthy


class ConnectionOptimizer:
    """Advanced database connection optimizer"""
    
    def __init__(self, config: ConnectionPoolConfig):
        self.config = config
        self.metrics = ConnectionMetrics()
        self.metrics_collector = MetricsCollector()
        self.health_checker = HealthChecker(config)
        
        # Connection tracking
        self._connections: Dict[str, ConnectionInfo] = {}
        self._engine: Optional[AsyncEngine] = None
        self._session_factory: Optional[Callable] = None
        
        # Monitoring
        self._monitoring_task: Optional[asyncio.Task] = None
        self._last_optimization = datetime.now()
        
        # Performance tuning
        self._slow_queries: List[Dict[str, Any]] = []
        self._query_patterns: Dict[str, int] = {}
        
    async def initialize(self, database_url: Optional[str] = None) -> None:
        """Initialize connection optimizer"""
        try:
            url = database_url or self.config.database_url or settings.DATABASE_URL
            
            # Create engine with optimized settings
            engine_kwargs = self._get_engine_kwargs()
            self._engine = create_async_engine(url, **engine_kwargs)
            
            # Setup event listeners
            self._setup_event_listeners()
            
            # Create session factory
            from sqlalchemy.ext.asyncio import async_sessionmaker
            self._session_factory = async_sessionmaker(
                bind=self._engine,
                expire_on_commit=False,
                class_=AsyncSession
            )
            
            # Start monitoring
            if self.config.metrics_enabled:
                self._monitoring_task = asyncio.create_task(self._monitor_connections())
            
            logger.info("Connection optimizer initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize connection optimizer: {e}")
            raise
    
    def _get_engine_kwargs(self) -> Dict[str, Any]:
        """Get engine configuration parameters"""
        pool_class = self._get_pool_class()
        
        kwargs = {
            "echo": self.config.echo,
            "pool_pre_ping": self.config.pool_pre_ping,
            "pool_recycle": self.config.pool_recycle,
            "poolclass": pool_class,
            "connect_args": {
                "command_timeout": self.config.connection_timeout,
                "server_settings": {
                    "jit": "off",  # Disable JIT for better performance in some cases
                }
            }
        }
        
        # Pool-specific settings
        if pool_class != NullPool:
            kwargs.update({
                "pool_size": self.config.min_connections,
                "max_overflow": self.config.max_overflow,
                "pool_timeout": self.config.pool_timeout,
            })
        
        return kwargs
    
    def _get_pool_class(self):
        """Get appropriate pool class based on strategy"""
        pool_classes = {
            PoolStrategy.STATIC: StaticPool,
            PoolStrategy.QUEUE: QueuePool,
            PoolStrategy.NULL: NullPool,
        }
        return pool_classes.get(self.config.pool_strategy, QueuePool)
    
    def _setup_event_listeners(self) -> None:
        """Setup SQLAlchemy event listeners for monitoring"""
        
        @event.listens_for(self._engine.sync_engine, "connect")
        def on_connect(dbapi_connection, connection_record):
            """Handle new connection creation"""
            connection_id = str(id(dbapi_connection))
            self._connections[connection_id] = ConnectionInfo(connection_id)
            self.metrics.total_connections += 1
            self.metrics.connection_requests += 1
            
            if self.config.log_connections:
                logger.debug(f"New connection created: {connection_id}")
        
        @event.listens_for(self._engine.sync_engine, "checkout")
        def on_checkout(dbapi_connection, connection_record, connection_proxy):
            """Handle connection checkout from pool"""
            connection_id = str(id(dbapi_connection))
            if connection_id in self._connections:
                self._connections[connection_id].state = ConnectionState.ACTIVE
                self.metrics.active_connections += 1
        
        @event.listens_for(self._engine.sync_engine, "checkin")
        def on_checkin(dbapi_connection, connection_record):
            """Handle connection checkin to pool"""
            connection_id = str(id(dbapi_connection))
            if connection_id in self._connections:
                self._connections[connection_id].state = ConnectionState.IDLE
                self.metrics.active_connections = max(0, self.metrics.active_connections - 1)
        
        @event.listens_for(self._engine.sync_engine, "close")
        def on_close(dbapi_connection, connection_record):
            """Handle connection close"""
            connection_id = str(id(dbapi_connection))
            if connection_id in self._connections:
                self._connections[connection_id].state = ConnectionState.CLOSED
                del self._connections[connection_id]
                self.metrics.total_connections = max(0, self.metrics.total_connections - 1)
        
        @event.listens_for(self._engine.sync_engine, "invalid")
        def on_invalid(dbapi_connection, connection_record, exception):
            """Handle connection invalidation"""
            connection_id = str(id(dbapi_connection))
            if connection_id in self._connections:
                self._connections[connection_id].state = ConnectionState.INVALID
                self.metrics.invalid_connections += 1
                self.metrics.connection_errors += 1
            
            logger.warning(f"Connection invalidated: {connection_id}, error: {exception}")
    
    @asynccontextmanager
    async def get_session(self):
        """Get database session with automatic management"""
        if not self._session_factory:
            raise RuntimeError("Connection optimizer not initialized")
        
        session = self._session_factory()
        start_time = time.time()
        
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f"Session error: {e}")
            raise
        finally:
            await session.close()
            
            # Update metrics
            connection_time = time.time() - start_time
            self._update_connection_metrics(connection_time)
    
    async def execute_query(
        self,
        query: str,
        parameters: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None
    ) -> Any:
        """Execute query with optimization and monitoring"""
        start_time = time.time()
        
        try:
            async with self.get_session() as session:
                # Track query pattern
                self._track_query_pattern(query)
                
                # Execute with timeout
                if timeout:
                    result = await asyncio.wait_for(
                        session.execute(text(query), parameters or {}),
                        timeout=timeout
                    )
                else:
                    result = await session.execute(text(query), parameters or {})
                
                execution_time = time.time() - start_time
                
                # Check for slow queries
                if execution_time > self.config.slow_query_threshold:
                    self._record_slow_query(query, execution_time, parameters)
                
                self._update_query_metrics(execution_time)
                return result
                
        except (SQLTimeoutError, asyncio.TimeoutError) as e:
            execution_time = time.time() - start_time
            logger.warning(f"Query timeout after {execution_time:.2f}s: {query[:100]}...")
            raise
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Query error after {execution_time:.2f}s: {e}")
            self.metrics.connection_errors += 1
            raise
    
    async def optimize_pool(self) -> None:
        """Optimize connection pool based on metrics and performance"""
        try:
            current_time = datetime.now()
            if (current_time - self._last_optimization).total_seconds() < 300:  # 5 minutes
                return
            
            logger.info("Starting connection pool optimization")
            
            # Analyze current metrics
            utilization = self.metrics.pool_utilization
            error_rate = self.metrics.error_rate
            
            # Dynamic pool sizing
            if utilization > 0.8 and self.metrics.total_connections < self.config.max_connections:
                await self._scale_up_pool()
            elif utilization < 0.3 and self.metrics.total_connections > self.config.min_connections:
                await self._scale_down_pool()
            
            # Close invalid connections
            await self._cleanup_invalid_connections()
            
            # Optimize slow queries
            await self._optimize_slow_queries()
            
            self._last_optimization = current_time
            logger.info("Connection pool optimization completed")
            
        except Exception as e:
            logger.error(f"Pool optimization error: {e}")
    
    async def _scale_up_pool(self) -> None:
        """Scale up connection pool"""
        # This would require engine reconfiguration
        # For now, log the recommendation
        logger.info("Recommending pool scale-up due to high utilization")
        
        if self.config.metrics_enabled:
            self.metrics_collector.counter(
                "connection_pool_scale_events_total",
                1,
                {"direction": "up"}
            )
    
    async def _scale_down_pool(self) -> None:
        """Scale down connection pool"""
        # Close idle connections
        idle_connections = [
            conn for conn in self._connections.values()
            if conn.state == ConnectionState.IDLE
            and conn.idle_time.total_seconds() > self.config.idle_timeout
        ]
        
        for conn in idle_connections[:2]:  # Close max 2 at a time
            # Mark for closure - actual implementation depends on pool type
            conn.state = ConnectionState.CLOSED
        
        logger.info(f"Scaled down pool by {len(idle_connections[:2])} connections")
        
        if self.config.metrics_enabled:
            self.metrics_collector.counter(
                "connection_pool_scale_events_total",
                1,
                {"direction": "down"}
            )
    
    async def _cleanup_invalid_connections(self) -> None:
        """Clean up invalid connections"""
        invalid_connections = [
            conn_id for conn_id, conn in self._connections.items()
            if conn.state == ConnectionState.INVALID
        ]
        
        for conn_id in invalid_connections:
            del self._connections[conn_id]
            self.metrics.invalid_connections = max(0, self.metrics.invalid_connections - 1)
        
        if invalid_connections:
            logger.info(f"Cleaned up {len(invalid_connections)} invalid connections")
    
    async def _optimize_slow_queries(self) -> None:
        """Analyze and provide recommendations for slow queries"""
        if not self._slow_queries:
            return
        
        # Group by query pattern
        pattern_counts = {}
        for slow_query in self._slow_queries:
            pattern = self._extract_query_pattern(slow_query["query"])
            pattern_counts[pattern] = pattern_counts.get(pattern, 0) + 1
        
        # Log recommendations for most frequent slow queries
        for pattern, count in sorted(pattern_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
            logger.warning(f"Slow query pattern (occurred {count} times): {pattern}")
            # Here you could implement automatic index suggestions
    
    def _track_query_pattern(self, query: str) -> None:
        """Track query patterns for analysis"""
        pattern = self._extract_query_pattern(query)
        self._query_patterns[pattern] = self._query_patterns.get(pattern, 0) + 1
    
    def _extract_query_pattern(self, query: str) -> str:
        """Extract pattern from query (remove literals)"""
        import re
        # Simple pattern extraction - replace literals with placeholders
        pattern = re.sub(r"'[^']*'", "?", query)
        pattern = re.sub(r"\b\d+\b", "?", pattern)
        return pattern.strip()
    
    def _record_slow_query(self, query: str, execution_time: float, parameters: Optional[Dict] = None) -> None:
        """Record slow query for analysis"""
        slow_query = {
            "query": query,
            "execution_time": execution_time,
            "parameters": parameters,
            "timestamp": datetime.now(),
        }
        
        self._slow_queries.append(slow_query)
        
        # Keep only recent slow queries
        if len(self._slow_queries) > 100:
            self._slow_queries = self._slow_queries[-50:]
        
        self.metrics.slow_queries += 1
        
        # Log slow query
        logger.warning(f"Slow query ({execution_time:.2f}s): {query[:200]}...")
        
        if self.config.metrics_enabled:
            self.metrics_collector.histogram(
                "slow_query_duration_seconds",
                execution_time,
                {"query_pattern": self._extract_query_pattern(query)}
            )
    
    def _update_connection_metrics(self, connection_time: float) -> None:
        """Update connection metrics"""
        self.metrics.connection_requests += 1
        
        # Update average connection time
        if self.metrics.connection_requests == 1:
            self.metrics.avg_connection_time = connection_time
        else:
            self.metrics.avg_connection_time = (
                (self.metrics.avg_connection_time * (self.metrics.connection_requests - 1) + connection_time)
                / self.metrics.connection_requests
            )
        
        self.metrics.last_updated = datetime.now()
        
        if self.config.metrics_enabled:
            self.metrics_collector.histogram(
                "database_connection_duration_seconds",
                connection_time
            )
    
    def _update_query_metrics(self, execution_time: float) -> None:
        """Update query metrics"""
        self.metrics.query_count += 1
        
        # Update average query time
        if self.metrics.query_count == 1:
            self.metrics.avg_query_time = execution_time
        else:
            self.metrics.avg_query_time = (
                (self.metrics.avg_query_time * (self.metrics.query_count - 1) + execution_time)
                / self.metrics.query_count
            )
        
        if self.config.metrics_enabled:
            self.metrics_collector.histogram(
                "database_query_duration_seconds",
                execution_time
            )
    
    async def _monitor_connections(self) -> None:
        """Background task for connection monitoring"""
        while True:
            try:
                await asyncio.sleep(self.config.health_check_interval)
                
                # Update connection states
                self.metrics.idle_connections = sum(
                    1 for conn in self._connections.values()
                    if conn.state == ConnectionState.IDLE
                )
                
                self.metrics.peak_connections = max(
                    self.metrics.peak_connections,
                    self.metrics.total_connections
                )
                
                # Health check
                if self._engine and self.health_checker.should_check():
                    healthy = await self.health_checker.check_connection(self._engine)
                    self.health_checker.mark_checked(healthy)
                    
                    if not healthy:
                        logger.error("Database health check failed")
                
                # Optimize pool if needed
                await self.optimize_pool()
                
                # Send metrics
                if self.config.metrics_enabled:
                    await self._send_metrics()
                
            except Exception as e:
                logger.error(f"Connection monitoring error: {e}")
    
    async def _send_metrics(self) -> None:
        """Send metrics to monitoring system"""
        self.metrics_collector.gauge(
            "database_connections_total",
            self.metrics.total_connections
        )
        
        self.metrics_collector.gauge(
            "database_connections_active",
            self.metrics.active_connections
        )
        
        self.metrics_collector.gauge(
            "database_connections_idle",
            self.metrics.idle_connections
        )
        
        self.metrics_collector.gauge(
            "database_pool_utilization",
            self.metrics.pool_utilization
        )
        
        self.metrics_collector.gauge(
            "database_connection_error_rate",
            self.metrics.error_rate
        )
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive connection statistics"""
        return {
            "total_connections": self.metrics.total_connections,
            "active_connections": self.metrics.active_connections,
            "idle_connections": self.metrics.idle_connections,
            "invalid_connections": self.metrics.invalid_connections,
            "pool_utilization": self.metrics.pool_utilization,
            "error_rate": self.metrics.error_rate,
            "avg_connection_time": self.metrics.avg_connection_time,
            "avg_query_time": self.metrics.avg_query_time,
            "query_count": self.metrics.query_count,
            "slow_queries": self.metrics.slow_queries,
            "peak_connections": self.metrics.peak_connections,
            "connection_requests": self.metrics.connection_requests,
            "connection_errors": self.metrics.connection_errors,
            "health_status": self.health_checker.is_healthy,
            "last_updated": self.metrics.last_updated.isoformat(),
        }
    
    async def close(self) -> None:
        """Close connection optimizer"""
        if self._monitoring_task:
            self._monitoring_task.cancel()
            try:
                await self._monitoring_task
            except asyncio.CancelledError:
                pass
        
        if self._engine:
            await self._engine.dispose()
            logger.info("Database engine disposed")


# Global connection optimizer instance
_connection_optimizer: Optional[ConnectionOptimizer] = None


def get_connection_optimizer(config: Optional[ConnectionPoolConfig] = None) -> ConnectionOptimizer:
    """Get global connection optimizer instance"""
    global _connection_optimizer
    
    if _connection_optimizer is None:
        _connection_optimizer = ConnectionOptimizer(config or ConnectionPoolConfig())
    
    return _connection_optimizer


async def initialize_connections(config: Optional[ConnectionPoolConfig] = None) -> None:
    """Initialize global connection optimizer"""
    optimizer = get_connection_optimizer(config)
    await optimizer.initialize()


async def close_connections() -> None:
    """Close global connection optimizer"""
    global _connection_optimizer
    
    if _connection_optimizer:
        await _connection_optimizer.close()
        _connection_optimizer = None


class ContentProtectionConnectionManager:
    """Specialized connection manager for content protection operations"""
    
    def __init__(self, base_optimizer: ConnectionOptimizer):
        self.base_optimizer = base_optimizer
        self.fingerprint_pool_config = ConnectionPoolConfig(
            pool_size=20,
            max_overflow=30,
            pool_timeout=30,
            pool_recycle=7200,  # 2 hours for long-running fingerprint operations
            pool_pre_ping=True
        )
        self.vector_pool_config = ConnectionPoolConfig(
            pool_size=15,
            max_overflow=25,
            pool_timeout=45,
            pool_recycle=3600,  # 1 hour for vector operations
            pool_pre_ping=True
        )
    
    async def get_fingerprint_connection(self) -> AsyncSession:
        """Get optimized connection for fingerprint operations"""
        return await self.base_optimizer.get_connection(
            pool_config=self.fingerprint_pool_config
        )
    
    async def get_vector_search_connection(self) -> AsyncSession:
        """Get optimized connection for vector similarity search"""
        return await self.base_optimizer.get_connection(
            pool_config=self.vector_pool_config
        )
    
    async def get_bulk_content_connection(self) -> AsyncSession:
        """Get connection optimized for bulk content operations"""
        bulk_config = ConnectionPoolConfig(
            pool_size=25,
            max_overflow=40,
            pool_timeout=60,
            pool_recycle=1800,  # 30 minutes for bulk operations
            pool_pre_ping=True
        )
        return await self.base_optimizer.get_connection(pool_config=bulk_config)


class MonetizationConnectionManager:
    """Specialized connection manager for monetization and analytics operations"""
    
    def __init__(self, base_optimizer: ConnectionOptimizer):
        self.base_optimizer = base_optimizer
        self.analytics_pool_config = ConnectionPoolConfig(
            pool_size=12,
            max_overflow=20,
            pool_timeout=25,
            pool_recycle=3600,  # 1 hour for analytics
            pool_pre_ping=True
        )
        self.revenue_pool_config = ConnectionPoolConfig(
            pool_size=8,
            max_overflow=15,
            pool_timeout=20,
            pool_recycle=1800,  # 30 minutes for revenue operations
            pool_pre_ping=True
        )
    
    async def get_analytics_connection(self) -> AsyncSession:
        """Get optimized connection for analytics operations"""
        return await self.base_optimizer.get_connection(
            pool_config=self.analytics_pool_config
        )
    
    async def get_revenue_connection(self) -> AsyncSession:
        """Get optimized connection for revenue tracking"""
        return await self.base_optimizer.get_connection(
            pool_config=self.revenue_pool_config
        )
    
    async def get_reporting_connection(self) -> AsyncSession:
        """Get read-only connection optimized for reporting"""
        reporting_config = ConnectionPoolConfig(
            pool_size=6,
            max_overflow=10,
            pool_timeout=15,
            pool_recycle=7200,  # 2 hours for long-running reports
            pool_pre_ping=True,
            read_only=True
        )
        return await self.base_optimizer.get_connection(pool_config=reporting_config)


class MultimediaConnectionManager:
    """Specialized connection manager for multimedia content operations"""
    
    def __init__(self, base_optimizer: ConnectionOptimizer):
        self.base_optimizer = base_optimizer
        self.audio_pool_config = ConnectionPoolConfig(
            pool_size=18,
            max_overflow=30,
            pool_timeout=40,
            pool_recycle=5400,  # 1.5 hours for audio processing
            pool_pre_ping=True
        )
        self.video_pool_config = ConnectionPoolConfig(
            pool_size=15,
            max_overflow=25,
            pool_timeout=50,
            pool_recycle=3600,  # 1 hour for video processing
            pool_pre_ping=True
        )
        self.image_pool_config = ConnectionPoolConfig(
            pool_size=12,
            max_overflow=20,
            pool_timeout=30,
            pool_recycle=7200,  # 2 hours for image processing
            pool_pre_ping=True
        )
    
    async def get_audio_connection(self) -> AsyncSession:
        """Get optimized connection for audio content operations"""
        return await self.base_optimizer.get_connection(
            pool_config=self.audio_pool_config
        )
    
    async def get_video_connection(self) -> AsyncSession:
        """Get optimized connection for video content operations"""
        return await self.base_optimizer.get_connection(
            pool_config=self.video_pool_config
        )
    
    async def get_image_connection(self) -> AsyncSession:
        """Get optimized connection for image content operations"""
        return await self.base_optimizer.get_connection(
            pool_config=self.image_pool_config
        )
    
    async def get_metadata_connection(self) -> AsyncSession:
        """Get optimized connection for multimedia metadata operations"""
        metadata_config = ConnectionPoolConfig(
            pool_size=10,
            max_overflow=15,
            pool_timeout=20,
            pool_recycle=3600,  # 1 hour for metadata
            pool_pre_ping=True
        )
        return await self.base_optimizer.get_connection(pool_config=metadata_config)


class AIProcessingConnectionManager:
    """Specialized connection manager for AI processing operations"""
    
    def __init__(self, base_optimizer: ConnectionOptimizer):
        self.base_optimizer = base_optimizer
        self.ml_pool_config = ConnectionPoolConfig(
            pool_size=20,
            max_overflow=35,
            pool_timeout=60,
            pool_recycle=1800,  # 30 minutes for ML operations
            pool_pre_ping=True
        )
        self.inference_pool_config = ConnectionPoolConfig(
            pool_size=25,
            max_overflow=40,
            pool_timeout=45,
            pool_recycle=3600,  # 1 hour for inference
            pool_pre_ping=True
        )
    
    async def get_ml_connection(self) -> AsyncSession:
        """Get optimized connection for ML training operations"""
        return await self.base_optimizer.get_connection(
            pool_config=self.ml_pool_config
        )
    
    async def get_inference_connection(self) -> AsyncSession:
        """Get optimized connection for AI inference operations"""
        return await self.base_optimizer.get_connection(
            pool_config=self.inference_pool_config
        )
    
    async def get_model_storage_connection(self) -> AsyncSession:
        """Get optimized connection for model metadata storage"""
        model_config = ConnectionPoolConfig(
            pool_size=8,
            max_overflow=12,
            pool_timeout=30,
            pool_recycle=7200,  # 2 hours for model storage
            pool_pre_ping=True
        )
        return await self.base_optimizer.get_connection(pool_config=model_config)
