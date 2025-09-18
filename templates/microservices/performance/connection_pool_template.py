#!/usr/bin/env python3
"""
🔌 CONNECTION POOL TEMPLATE - ENTERPRISE RESOURCE MANAGEMENT
===========================================================

Advanced connection pooling for databases, Redis, message queues, and
external APIs with intelligent load balancing and health monitoring.

© 2025 Fahed Mlaiel (mlaiel@live.de) - Propriété Intellectuelle Exclusive
🚨 UTILISATION COMMERCIALE INTERDITE SANS AUTORISATION ÉCRITE

🎯 EXPERTISE COMBINÉE:
- Backend Senior: Connection management and database optimization
- Performance Engineer: Pool sizing and resource optimization
- DevOps: Health monitoring and auto-scaling
- DBA: Connection lifecycle and transaction management
"""

import asyncio
import logging
import time
from typing import Any, Dict, List, Optional, Callable, Protocol
from dataclasses import dataclass, field
from enum import Enum
from contextlib import asynccontextmanager
import asyncpg
import aioredis
import aiohttp
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

class ConnectionType(Enum):
    """Connection types supported"""
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    REDIS = "redis"
    MONGODB = "mongodb"
    HTTP_CLIENT = "http_client"
    RABBITMQ = "rabbitmq"
    KAFKA = "kafka"

class PoolStrategy(Enum):
    """Pool management strategies"""
    ROUND_ROBIN = "round_robin"
    LEAST_CONNECTIONS = "least_connections"
    WEIGHTED = "weighted"
    RANDOM = "random"
    LOCALITY_AWARE = "locality_aware"

@dataclass
class ConnectionConfig:
    """Connection configuration"""
    connection_type: ConnectionType
    connection_string: str
    min_connections: int = 5
    max_connections: int = 20
    idle_timeout: int = 300  # seconds
    max_lifetime: int = 3600  # seconds
    health_check_interval: int = 30
    retry_attempts: int = 3
    retry_delay: float = 1.0
    pool_strategy: PoolStrategy = PoolStrategy.ROUND_ROBIN

@dataclass
class PoolMetrics:
    """Connection pool metrics"""
    total_connections: int = 0
    active_connections: int = 0
    idle_connections: int = 0
    failed_connections: int = 0
    total_requests: int = 0
    successful_requests: int = 0
    avg_response_time_ms: float = 0.0
    connection_errors: int = 0

class Connection:
    """Wrapper for database/service connections"""
    
    def __init__(self, connection: Any, connection_type: ConnectionType):
        self.connection = connection
        self.connection_type = connection_type
        self.created_at = time.time()
        self.last_used = time.time()
        self.usage_count = 0
        self.is_healthy = True
        self.is_busy = False
    
    async def execute(self, query: str, *args, **kwargs) -> Any:
        """Execute query/operation on connection"""
        self.last_used = time.time()
        self.usage_count += 1
        self.is_busy = True
        
        try:
            if self.connection_type == ConnectionType.POSTGRESQL:
                if query.strip().upper().startswith('SELECT'):
                    return await self.connection.fetch(query, *args)
                else:
                    return await self.connection.execute(query, *args)
            elif self.connection_type == ConnectionType.REDIS:
                return await self.connection.execute_command(*args)
            elif self.connection_type == ConnectionType.HTTP_CLIENT:
                return await self.connection.request(*args, **kwargs)
            else:
                raise NotImplementedError(f"Execute not implemented for {self.connection_type}")
                
        finally:
            self.is_busy = False
    
    async def health_check(self) -> bool:
        """Check connection health"""
        try:
            if self.connection_type == ConnectionType.POSTGRESQL:
                await self.connection.execute('SELECT 1')
            elif self.connection_type == ConnectionType.REDIS:
                await self.connection.ping()
            elif self.connection_type == ConnectionType.HTTP_CLIENT:
                # HTTP client doesn't need health check
                pass
            
            self.is_healthy = True
            return True
            
        except Exception as e:
            logger.warning(f"Health check failed: {e}")
            self.is_healthy = False
            return False
    
    async def close(self):
        """Close connection"""
        try:
            if hasattr(self.connection, 'close'):
                await self.connection.close()
        except Exception as e:
            logger.warning(f"Connection close failed: {e}")

class ConnectionPoolTemplate:
    """
    🚀 ENTERPRISE CONNECTION POOL TEMPLATE
    
    Multi-protocol connection pooling with intelligent load balancing,
    health monitoring, auto-scaling, and comprehensive metrics.
    
    **Expertise Backend Senior + Performance Engineer + DevOps**
    """
    
    def __init__(self, config: ConnectionConfig):
        """Initialize connection pool"""
        self.config = config
        self.connections: List[Connection] = []
        self.metrics = PoolMetrics()
        self.connection_factories = {
            ConnectionType.POSTGRESQL: self._create_postgresql_connection,
            ConnectionType.REDIS: self._create_redis_connection,
            ConnectionType.HTTP_CLIENT: self._create_http_connection,
        }
        self.last_used_index = 0
        self.health_monitor_task = None
        self.pool_lock = asyncio.Lock()
        
        # Initialize pool
        asyncio.create_task(self._initialize_pool())
    
    async def _initialize_pool(self):
        """Initialize connection pool with minimum connections"""
        try:
            # Create minimum connections
            for _ in range(self.config.min_connections):
                connection = await self._create_connection()
                if connection:
                    self.connections.append(connection)
                    self.metrics.total_connections += 1
                    self.metrics.idle_connections += 1
            
            # Start health monitoring
            self.health_monitor_task = asyncio.create_task(self._health_monitor())
            
            logger.info(f"✅ Connection pool initialized with {len(self.connections)} connections")
            
        except Exception as e:
            logger.error(f"❌ Pool initialization failed: {e}")
    
    async def _create_connection(self) -> Optional[Connection]:
        """Create new connection based on type"""
        try:
            factory = self.connection_factories.get(self.config.connection_type)
            if not factory:
                raise ValueError(f"Unsupported connection type: {self.config.connection_type}")
            
            raw_connection = await factory()
            connection = Connection(raw_connection, self.config.connection_type)
            
            # Verify health
            if await connection.health_check():
                return connection
            else:
                await connection.close()
                return None
                
        except Exception as e:
            logger.error(f"Connection creation failed: {e}")
            self.metrics.connection_errors += 1
            return None
    
    async def _create_postgresql_connection(self):
        """Create PostgreSQL connection"""
        return await asyncpg.connect(self.config.connection_string)
    
    async def _create_redis_connection(self):
        """Create Redis connection"""
        return await aioredis.from_url(self.config.connection_string)
    
    async def _create_http_connection(self):
        """Create HTTP client connection"""
        connector = aiohttp.TCPConnector(
            limit=self.config.max_connections,
            limit_per_host=self.config.max_connections // 4
        )
        return aiohttp.ClientSession(connector=connector)
    
    @asynccontextmanager
    async def get_connection(self):
        """Get connection from pool with automatic return"""
        connection = await self._acquire_connection()
        if not connection:
            raise Exception("No healthy connections available")
        
        try:
            yield connection
        finally:
            await self._release_connection(connection)
    
    async def _acquire_connection(self) -> Optional[Connection]:
        """Acquire connection from pool"""
        async with self.pool_lock:
            start_time = time.time()
            
            try:
                # Find available healthy connection
                connection = await self._select_connection()
                
                if not connection:
                    # Try to create new connection if under max limit
                    if self.metrics.total_connections < self.config.max_connections:
                        connection = await self._create_connection()
                        if connection:
                            self.connections.append(connection)
                            self.metrics.total_connections += 1
                
                if connection:
                    connection.is_busy = True
                    self.metrics.active_connections += 1
                    self.metrics.idle_connections -= 1
                    self.metrics.total_requests += 1
                    
                    # Update response time
                    response_time = (time.time() - start_time) * 1000
                    self._update_avg_response_time(response_time)
                
                return connection
                
            except Exception as e:
                logger.error(f"Connection acquisition failed: {e}")
                self.metrics.connection_errors += 1
                return None
    
    async def _select_connection(self) -> Optional[Connection]:
        """Select connection based on pool strategy"""
        available_connections = [
            conn for conn in self.connections 
            if not conn.is_busy and conn.is_healthy
        ]
        
        if not available_connections:
            return None
        
        if self.config.pool_strategy == PoolStrategy.ROUND_ROBIN:
            return self._round_robin_selection(available_connections)
        elif self.config.pool_strategy == PoolStrategy.LEAST_CONNECTIONS:
            return min(available_connections, key=lambda c: c.usage_count)
        elif self.config.pool_strategy == PoolStrategy.RANDOM:
            import random
            return random.choice(available_connections)
        else:
            return available_connections[0]  # Default to first available
    
    def _round_robin_selection(self, connections: List[Connection]) -> Connection:
        """Round-robin connection selection"""
        if not connections:
            return None
        
        self.last_used_index = (self.last_used_index + 1) % len(connections)
        return connections[self.last_used_index]
    
    async def _release_connection(self, connection: Connection):
        """Release connection back to pool"""
        async with self.pool_lock:
            connection.is_busy = False
            self.metrics.active_connections -= 1
            self.metrics.idle_connections += 1
            self.metrics.successful_requests += 1
    
    async def _health_monitor(self):
        """Background task to monitor connection health"""
        while True:
            try:
                await asyncio.sleep(self.config.health_check_interval)
                await self._check_all_connections()
                await self._cleanup_stale_connections()
                
            except Exception as e:
                logger.error(f"Health monitor error: {e}")
    
    async def _check_all_connections(self):
        """Check health of all connections"""
        unhealthy_connections = []
        
        for connection in self.connections:
            if not connection.is_busy:
                if not await connection.health_check():
                    unhealthy_connections.append(connection)
        
        # Remove unhealthy connections
        for connection in unhealthy_connections:
            await self._remove_connection(connection)
            
        # Ensure minimum connections
        await self._ensure_minimum_connections()
    
    async def _cleanup_stale_connections(self):
        """Remove connections that exceeded max lifetime"""
        current_time = time.time()
        stale_connections = []
        
        for connection in self.connections:
            if (not connection.is_busy and 
                current_time - connection.created_at > self.config.max_lifetime):
                stale_connections.append(connection)
        
        # Remove stale connections but maintain minimum
        for connection in stale_connections:
            if self.metrics.total_connections > self.config.min_connections:
                await self._remove_connection(connection)
    
    async def _remove_connection(self, connection: Connection):
        """Remove connection from pool"""
        try:
            await connection.close()
            self.connections.remove(connection)
            self.metrics.total_connections -= 1
            if connection.is_busy:
                self.metrics.active_connections -= 1
            else:
                self.metrics.idle_connections -= 1
                
        except Exception as e:
            logger.warning(f"Connection removal failed: {e}")
    
    async def _ensure_minimum_connections(self):
        """Ensure pool has minimum number of connections"""
        while self.metrics.total_connections < self.config.min_connections:
            connection = await self._create_connection()
            if connection:
                self.connections.append(connection)
                self.metrics.total_connections += 1
                self.metrics.idle_connections += 1
            else:
                break  # Stop trying if creation fails
    
    def _update_avg_response_time(self, response_time_ms: float):
        """Update average response time"""
        if self.metrics.total_requests == 1:
            self.metrics.avg_response_time_ms = response_time_ms
        else:
            # Exponential moving average
            alpha = 0.1
            self.metrics.avg_response_time_ms = (
                alpha * response_time_ms + 
                (1 - alpha) * self.metrics.avg_response_time_ms
            )
    
    async def execute(self, query: str, *args, **kwargs) -> Any:
        """Execute query using pooled connection"""
        async with self.get_connection() as connection:
            return await connection.execute(query, *args, **kwargs)
    
    def get_metrics(self) -> PoolMetrics:
        """Get pool performance metrics"""
        return self.metrics
    
    async def close_pool(self):
        """Close all connections in pool"""
        try:
            if self.health_monitor_task:
                self.health_monitor_task.cancel()
                
            for connection in self.connections:
                await connection.close()
                
            self.connections.clear()
            self.metrics = PoolMetrics()
            
            logger.info("✅ Connection pool closed successfully")
            
        except Exception as e:
            logger.error(f"Pool closure error: {e}")

# Pool factory
def create_connection_pool(connection_type: ConnectionType, connection_string: str, **kwargs) -> ConnectionPoolTemplate:
    """Factory function to create connection pool instances"""
    config = ConnectionConfig(
        connection_type=connection_type,
        connection_string=connection_string,
        **kwargs
    )
    return ConnectionPoolTemplate(config)