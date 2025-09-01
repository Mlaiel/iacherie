"""
Connection Pool Optimization with Active Connection Monitoring
Provides enhanced database and HTTP connection pooling with monitoring

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import time
import logging
from typing import Dict, List, Optional, Any, AsyncIterator
from dataclasses import dataclass, field
import asyncpg
import aiohttp
from contextlib import asynccontextmanager
from collections import defaultdict
import statistics


logger = logging.getLogger(__name__)


@dataclass
class ConnectionPoolConfig:
    """Configuration for connection pools"""
    min_size: int = 5
    max_size: int = 50
    max_queries: int = 50000
    max_inactive_time: float = 300.0  # 5 minutes
    timeout: float = 30.0
    command_timeout: float = 60.0
    retry_on_failure: bool = True
    max_retries: int = 3
    health_check_interval: float = 30.0
    connection_ttl: float = 3600.0  # 1 hour
    
    # Monitoring configuration
    enable_monitoring: bool = True
    metrics_collection_interval: float = 10.0
    slow_query_threshold: float = 1.0
    connection_leak_threshold: float = 600.0  # 10 minutes


@dataclass
class ConnectionMetrics:
    """Metrics for connection pool monitoring"""
    total_connections: int = 0
    active_connections: int = 0
    idle_connections: int = 0
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    slow_queries: int = 0
    connection_leaks: int = 0
    avg_response_time: float = 0.0
    p95_response_time: float = 0.0
    p99_response_time: float = 0.0
    created_connections: int = 0
    closed_connections: int = 0
    last_update: float = field(default_factory=time.time)
    response_times: List[float] = field(default_factory=list)


class ConnectionMonitor:
    """Monitor for tracking connection pool health and performance"""
    
    def __init__(self, name: str, config: ConnectionPoolConfig):
        self.name = name
        self.config = config
        self.metrics = ConnectionMetrics()
        self.active_connections: Dict[str, Dict[str, Any]] = {}
        self.monitoring_task: Optional[asyncio.Task] = None
        self.running = False
        self.lock = asyncio.Lock()
        
    async def start_monitoring(self):
        """Start the monitoring task"""
        if self.config.enable_monitoring and not self.running:
            self.running = True
            self.monitoring_task = asyncio.create_task(self._monitoring_loop())
            logger.info(f"Started monitoring for pool '{self.name}'")
    
    async def stop_monitoring(self):
        """Stop the monitoring task"""
        self.running = False
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
            logger.info(f"Stopped monitoring for pool '{self.name}'")
    
    async def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.running:
            try:
                await self._collect_metrics()
                await self._check_connection_health()
                await asyncio.sleep(self.config.metrics_collection_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop for '{self.name}': {e}")
                await asyncio.sleep(self.config.metrics_collection_interval)
    
    async def _collect_metrics(self):
        """Collect current metrics"""
        async with self.lock:
            current_time = time.time()
            
            # Update connection counts
            self.metrics.active_connections = len([
                conn for conn in self.active_connections.values()
                if conn['status'] == 'active'
            ])
            
            self.metrics.idle_connections = len([
                conn for conn in self.active_connections.values()
                if conn['status'] == 'idle'
            ])
            
            self.metrics.total_connections = len(self.active_connections)
            
            # Calculate response time statistics
            if self.metrics.response_times:
                self.metrics.avg_response_time = statistics.mean(self.metrics.response_times)
                if len(self.metrics.response_times) >= 20:
                    quantiles = statistics.quantiles(self.metrics.response_times, n=100)
                    self.metrics.p95_response_time = quantiles[94]
                    self.metrics.p99_response_time = quantiles[98]
                
                # Keep only recent response times (last 5 minutes)
                cutoff_time = current_time - 300
                self.metrics.response_times = [
                    rt for rt in self.metrics.response_times
                    if rt > cutoff_time
                ]
            
            self.metrics.last_update = current_time
    
    async def record_connection_created(self, connection_id: str):
        """Record that a new connection was created"""
        async with self.lock:
            self.metrics.created_connections += 1
            self.active_connections[connection_id] = {
                'created_at': time.time(),
                'last_activity': time.time(),
                'status': 'idle',
                'query_count': 0,
                'total_time': 0.0
            }
    
    async def record_query_end(self, connection_id: str, duration: float, success: bool):
        """Record the end of a query"""
        async with self.lock:
            if success:
                self.metrics.successful_requests += 1
            else:
                self.metrics.failed_requests += 1
            
            if duration > self.config.slow_query_threshold:
                self.metrics.slow_queries += 1
            
            self.metrics.response_times.append(duration)
            
            if connection_id in self.active_connections:
                self.active_connections[connection_id]['total_time'] += duration
                self.active_connections[connection_id]['last_activity'] = time.time()
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics snapshot"""
        return {
            'pool_name': self.name,
            'timestamp': time.time(),
            'connections': {
                'total': self.metrics.total_connections,
                'active': self.metrics.active_connections,
                'idle': self.metrics.idle_connections,
                'created': self.metrics.created_connections,
                'closed': self.metrics.closed_connections,
                'leaks': self.metrics.connection_leaks
            },
            'requests': {
                'total': self.metrics.total_requests,
                'successful': self.metrics.successful_requests,
                'failed': self.metrics.failed_requests,
                'slow_queries': self.metrics.slow_queries,
                'success_rate': (
                    self.metrics.successful_requests / max(self.metrics.total_requests, 1)
                )
            },
            'performance': {
                'avg_response_time': self.metrics.avg_response_time,
                'p95_response_time': self.metrics.p95_response_time,
                'p99_response_time': self.metrics.p99_response_time
            }
        }


class OptimizedAsyncPGPool:
    """Optimized PostgreSQL connection pool with monitoring"""
    
    def __init__(self, dsn: str, config: Optional[ConnectionPoolConfig] = None):
        self.dsn = dsn
        self.config = config or ConnectionPoolConfig()
        self.pool: Optional[asyncpg.Pool] = None
        self.monitor = ConnectionMonitor(f"asyncpg_{id(self)}", self.config)
        self._closed = False
        
    async def initialize(self):
        """Initialize the connection pool"""
        if self.pool is None:
            self.pool = await asyncpg.create_pool(
                self.dsn,
                min_size=self.config.min_size,
                max_size=self.config.max_size,
                max_queries=self.config.max_queries,
                max_inactive_connection_lifetime=self.config.max_inactive_time,
                timeout=self.config.timeout,
                command_timeout=self.config.command_timeout,
                server_settings={
                    'application_name': 'ia_influencer_optimized_pool'
                }
            )
            
            # Start monitoring
            await self.monitor.start_monitoring()
            
            logger.info(f"Initialized PostgreSQL pool with {self.config.min_size}-{self.config.max_size} connections")
    
    @asynccontextmanager
    async def acquire(self) -> AsyncIterator[asyncpg.Connection]:
        """Acquire a connection from the pool with monitoring"""
        if self.pool is None:
            await self.initialize()
        
        connection_id = f"conn_{int(time.time() * 1000000)}"
        
        try:
            async with self.pool.acquire() as connection:
                yield connection
        except Exception as e:
            logger.error(f"Error acquiring connection: {e}")
            raise
    
    async def execute(self, query: str, *args) -> str:
        """Execute a query with monitoring"""
        connection_id = f"query_{int(time.time() * 1000000)}"
        start_time = time.time()
        
        try:
            async with self.acquire() as connection:
                result = await connection.execute(query, *args)
                duration = time.time() - start_time
                await self.monitor.record_query_end(connection_id, duration, True)
                return result
        except Exception as e:
            duration = time.time() - start_time
            await self.monitor.record_query_end(connection_id, duration, False)
            raise
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get pool metrics"""
        base_metrics = self.monitor.get_metrics()
        
        if self.pool:
            base_metrics.update({
                'pool_info': {
                    'size': self.pool.get_size(),
                    'min_size': self.pool.get_min_size(),
                    'max_size': self.pool.get_max_size(),
                    'idle_size': self.pool.get_idle_size()
                }
            })
        
        return base_metrics
    
    async def close(self):
        """Close the connection pool"""
        if not self._closed:
            await self.monitor.stop_monitoring()
            
            if self.pool:
                await self.pool.close()
                self.pool = None
            
            self._closed = True
            logger.info("PostgreSQL pool closed")


class ConnectionPoolRegistry:
    """Registry for managing multiple connection pools"""
    
    def __init__(self):
        self.db_pools: Dict[str, OptimizedAsyncPGPool] = {}
        self.monitoring_task: Optional[asyncio.Task] = None
        self.running = False
    
    def get_db_pool(self, name: str, dsn: str, config: Optional[ConnectionPoolConfig] = None) -> OptimizedAsyncPGPool:
        """Get or create a database pool"""
        if name not in self.db_pools:
            self.db_pools[name] = OptimizedAsyncPGPool(dsn, config)
        return self.db_pools[name]
    
    def get_all_metrics(self) -> Dict[str, Dict[str, Any]]:
        """Get metrics for all pools"""
        metrics = {}
        
        for name, pool in self.db_pools.items():
            metrics[f"db_{name}"] = pool.get_metrics()
        
        return metrics
    
    async def close_all(self):
        """Close all connection pools"""
        for pool in self.db_pools.values():
            await pool.close()
        
        self.db_pools.clear()
        logger.info("All connection pools closed")


# Global registry instance
connection_pool_registry = ConnectionPoolRegistry()