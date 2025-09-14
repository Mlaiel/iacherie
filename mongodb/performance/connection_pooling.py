"""MongoDB Connection Pooling Manager
===================================

Advanced connection pool management with intelligent load balancing and health monitoring.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
"""

import logging
import time
import threading
import asyncio
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass
from enum import Enum
from pymongo import MongoClient
from pymongo.pool import Pool
from pymongo.server_type import SERVER_TYPE
import pymongo.errors

logger = logging.getLogger(__name__)

class ConnectionStatus(Enum):
    """Connection status enumeration."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    DISCONNECTED = "disconnected"

@dataclass
class ConnectionMetrics:
    """Connection pool metrics."""
    pool_id: str
    active_connections: int
    idle_connections: int
    total_connections: int
    max_pool_size: int
    min_pool_size: int
    queue_size: int
    connection_errors: int
    last_error: Optional[str]
    avg_response_time_ms: float
    status: ConnectionStatus
    uptime_seconds: float

@dataclass
class PoolConfiguration:
    """Connection pool configuration."""
    host: str
    port: int = 27017
    max_pool_size: int = 100
    min_pool_size: int = 10
    max_idle_time_ms: int = 30000
    wait_queue_timeout_ms: int = 5000
    connect_timeout_ms: int = 5000
    server_selection_timeout_ms: int = 5000
    heartbeat_frequency_ms: int = 10000
    replica_set: Optional[str] = None
    read_preference: str = "primary"
    write_concern: Dict[str, Any] = None
    read_concern: Dict[str, Any] = None
    ssl_enabled: bool = False
    ssl_cert_path: Optional[str] = None
    auth_database: str = "admin"
    username: Optional[str] = None
    password: Optional[str] = None

class ConnectionPool:
    """Advanced MongoDB connection pool with health monitoring."""
    
    def __init__(self, config -> None: PoolConfiguration, pool_id -> None: str = None) -> None:
        """Initialize connection pool.
        
        Args:
            config: Pool configuration
            pool_id: Unique pool identifier
        """
        self.config = config
        self.pool_id = pool_id or f"pool_{int(time.time())}"
        self.created_at = time.time()
        
        # Connection metrics
        self._metrics = ConnectionMetrics(
            pool_id=self.pool_id,
            active_connections=0,
            idle_connections=0,
            total_connections=0,
            max_pool_size=config.max_pool_size,
            min_pool_size=config.min_pool_size,
            queue_size=0,
            connection_errors=0,
            last_error=None,
            avg_response_time_ms=0.0,
            status=ConnectionStatus.DISCONNECTED,
            uptime_seconds=0.0
        )
        
        # Performance tracking
        self._response_times: List[float] = []
        self._response_time_lock = threading.Lock()
        
        # Health monitoring
        self._health_callbacks: List[Callable] = []
        self._last_health_check = 0
        self._health_check_interval = 30  # seconds
        
        # MongoDB client
        self._client: Optional[MongoClient] = None
        self._client_lock = threading.Lock()
        
        # Auto-connect
        self.connect()
    
    def connect(self) -> bool:
        """Establish connection to MongoDB.
        
        Returns:
            True if connection successful
        """
        try:
            with self._client_lock:
                if self._client:
                    self._client.close()
                
                # Build connection URI
                uri = self._build_connection_uri()
                
                # Create MongoDB client
                self._client = MongoClient(
                    uri,
                    maxPoolSize=self.config.max_pool_size,
                    minPoolSize=self.config.min_pool_size,
                    maxIdleTimeMS=self.config.max_idle_time_ms,
                    waitQueueTimeoutMS=self.config.wait_queue_timeout_ms,
                    connectTimeoutMS=self.config.connect_timeout_ms,
                    serverSelectionTimeoutMS=self.config.server_selection_timeout_ms,
                    heartbeatFrequencyMS=self.config.heartbeat_frequency_ms
                )
                
                # Test connection
                self._client.admin.command('ping')
                
                self._metrics.status = ConnectionStatus.HEALTHY
                logger.info(f"Connection pool '{self.pool_id}' connected successfully")
                
                # Notify health callbacks
                self._notify_health_callbacks(ConnectionStatus.HEALTHY)
                
                return True
                
        except Exception as e:
            self._metrics.connection_errors += 1
            self._metrics.last_error = str(e)
            self._metrics.status = ConnectionStatus.DISCONNECTED
            logger.error(f"Connection pool '{self.pool_id}' failed to connect: {e}")
            
            # Notify health callbacks
            self._notify_health_callbacks(ConnectionStatus.DISCONNECTED)
            
            return False
    
    def disconnect(self) -> None:
        """Disconnect from MongoDB."""
        with self._client_lock:
            if self._client:
                self._client.close()
                self._client = None
            
            self._metrics.status = ConnectionStatus.DISCONNECTED
            logger.info(f"Connection pool '{self.pool_id}' disconnected")
    
    def get_client(self) -> Optional[MongoClient]:
        """Get MongoDB client instance.
        
        Returns:
            MongoDB client or None if not connected
        """
        with self._client_lock:
            if self._client is None:
                if not self.connect():
                    return None
            
            return self._client
    
    def execute_with_timing(self, operation: Callable, *args, **kwargs) -> Any:
        """Execute operation with response time tracking.
        
        Args:
            operation: Operation to execute
            *args: Operation arguments
            **kwargs: Operation keyword arguments
            
        Returns:
            Operation result
        """
        start_time = time.time()
        
        try:
            result = operation(*args, **kwargs)
            
            # Record successful response time
            response_time = (time.time() - start_time) * 1000  # Convert to ms
            self._record_response_time(response_time)
            
            return result
            
        except Exception as e:
            # Record error
            self._metrics.connection_errors += 1
            self._metrics.last_error = str(e)
            
            # Update status based on error type
            if isinstance(e, (pymongo.errors.ConnectionFailure, 
                            pymongo.errors.ServerSelectionTimeoutError)):
                self._metrics.status = ConnectionStatus.UNHEALTHY
            else:
                self._metrics.status = ConnectionStatus.DEGRADED
            
            raise
    
    def health_check(self, force: bool = False) -> ConnectionStatus:
        """Perform health check on connection pool.
        
        Args:
            force: Force health check even if recently performed
            
        Returns:
            Current connection status
        """
        current_time = time.time()
        
        # Skip if recent health check and not forced
        if (not force and 
            current_time - self._last_health_check < self._health_check_interval):
            return self._metrics.status
        
        self._last_health_check = current_time
        
        try:
            client = self.get_client()
            if not client:
                self._metrics.status = ConnectionStatus.DISCONNECTED
                return self._metrics.status
            
            # Perform ping with timeout
            start_time = time.time()
            client.admin.command('ping')
            ping_time = (time.time() - start_time) * 1000
            
            # Update status based on ping time
            if ping_time < 100:
                self._metrics.status = ConnectionStatus.HEALTHY
            elif ping_time < 500:
                self._metrics.status = ConnectionStatus.DEGRADED
            else:
                self._metrics.status = ConnectionStatus.UNHEALTHY
            
            # Update metrics
            self._update_pool_metrics()
            self._metrics.uptime_seconds = current_time - self.created_at
            
            logger.debug(f"Health check for pool '{self.pool_id}': "
                        f"{self._metrics.status.value} (ping: {ping_time:.1f}ms)")
            
        except Exception as e:
            self._metrics.connection_errors += 1
            self._metrics.last_error = str(e)
            self._metrics.status = ConnectionStatus.UNHEALTHY
            logger.warning(f"Health check failed for pool '{self.pool_id}': {e}")
        
        # Notify health callbacks
        self._notify_health_callbacks(self._metrics.status)
        
        return self._metrics.status
    
    def get_metrics(self) -> ConnectionMetrics:
        """Get current connection pool metrics.
        
        Returns:
            Connection pool metrics
        """
        # Update metrics before returning
        self._update_pool_metrics()
        self._metrics.uptime_seconds = time.time() - self.created_at
        
        return self._metrics
    
    def register_health_callback(self, callback: Callable[[ConnectionStatus], None]) -> None:
        """Register callback for health status changes.
        
        Args:
            callback: Callback function that receives ConnectionStatus
        """
        self._health_callbacks.append(callback)
    
    def _build_connection_uri(self) -> str:
        """Build MongoDB connection URI."""
        # Base URI
        if self.config.username and self.config.password:
            uri = f"mongodb://{self.config.username}:{self.config.password}@"
        else:
            uri = "mongodb://"
        
        uri += f"{self.config.host}:{self.config.port}/"
        
        # Add database
        if self.config.auth_database:
            uri += self.config.auth_database
        
        # Add options
        options = []
        
        if self.config.replica_set:
            options.append(f"replicaSet={self.config.replica_set}")
        
        if self.config.read_preference != "primary":
            options.append(f"readPreference={self.config.read_preference}")
        
        if self.config.ssl_enabled:
            options.append("ssl=true")
            if self.config.ssl_cert_path:
                options.append(f"ssl_certfile={self.config.ssl_cert_path}")
        
        if options:
            uri += "?" + "&".join(options)
        
        return uri
    
    def _record_response_time(self, response_time_ms: float) -> None:
        """Record response time for averaging."""
        with self._response_time_lock:
            self._response_times.append(response_time_ms)
            
            # Keep only recent response times (last 100)
            if len(self._response_times) > 100:
                self._response_times = self._response_times[-100:]
            
            # Update average
            if self._response_times:
                self._metrics.avg_response_time_ms = sum(self._response_times) / len(self._response_times)
    
    def _update_pool_metrics(self) -> None:
        """Update connection pool metrics."""
        try:
            client = self.get_client()
            if not client:
                return
            
            # Get pool statistics from MongoDB client
            for server in client._topology.description.server_descriptions():
                pool = server.pool
                if pool:
                    self._metrics.active_connections = pool.active_sockets
                    self._metrics.idle_connections = len(pool.sockets)
                    self._metrics.total_connections = pool.active_sockets + len(pool.sockets)
                    self._metrics.queue_size = pool.requests if hasattr(pool, 'requests') else 0
                    break
                    
        except Exception as e:
            logger.debug(f"Failed to update pool metrics: {e}")
    
    def _notify_health_callbacks(self, status: ConnectionStatus) -> None:
        """Notify health status change callbacks."""
        for callback in self._health_callbacks:
            try:
                callback(status)
            except Exception as e:
                logger.error(f"Health callback error: {e}")

class ConnectionPoolManager:
    """Manager for multiple connection pools with load balancing."""
    
    def __init__(self) -> None:
        """Initialize connection pool manager."""
        self._pools: Dict[str, ConnectionPool] = {}
        self._pools_lock = threading.RLock()
        self._round_robin_index = 0
        
        # Health monitoring
        self._health_monitor_thread = None
        self._health_monitor_running = False
        self._health_check_interval = 30  # seconds
        
        # Load balancing strategies
        self._load_balancing_strategy = "round_robin"  # round_robin, least_connections, response_time
    
    def add_pool(self, pool_id: str, config: PoolConfiguration) -> bool:
        """Add connection pool to manager.
        
        Args:
            pool_id: Unique pool identifier
            config: Pool configuration
            
        Returns:
            True if pool added successfully
        """
        with self._pools_lock:
            if pool_id in self._pools:
                logger.warning(f"Pool '{pool_id}' already exists")
                return False
            
            pool = ConnectionPool(config, pool_id)
            self._pools[pool_id] = pool
            
            logger.info(f"Added connection pool '{pool_id}'")
            return True
    
    def remove_pool(self, pool_id: str) -> bool:
        """Remove connection pool from manager.
        
        Args:
            pool_id: Pool identifier to remove
            
        Returns:
            True if pool removed successfully
        """
        with self._pools_lock:
            if pool_id not in self._pools:
                logger.warning(f"Pool '{pool_id}' not found")
                return False
            
            pool = self._pools[pool_id]
            pool.disconnect()
            del self._pools[pool_id]
            
            logger.info(f"Removed connection pool '{pool_id}'")
            return True
    
    def get_pool(self, pool_id: str = None) -> Optional[ConnectionPool]:
        """Get connection pool by ID or select optimal pool.
        
        Args:
            pool_id: Specific pool ID, or None for load-balanced selection
            
        Returns:
            Connection pool or None if not found
        """
        with self._pools_lock:
            if pool_id:
                return self._pools.get(pool_id)
            
            # Select pool using load balancing strategy
            healthy_pools = [
                pool for pool in self._pools.values()
                if pool.get_metrics().status in [ConnectionStatus.HEALTHY, ConnectionStatus.DEGRADED]
            ]
            
            if not healthy_pools:
                logger.warning("No healthy connection pools available")
                return None
            
            return self._select_optimal_pool(healthy_pools)
    
    def get_client(self, pool_id: str = None) -> Optional[MongoClient]:
        """Get MongoDB client from optimal pool.
        
        Args:
            pool_id: Specific pool ID, or None for load-balanced selection
            
        Returns:
            MongoDB client or None
        """
        pool = self.get_pool(pool_id)
        if pool:
            return pool.get_client()
        return None
    
    def execute_operation(self, operation: Callable, pool_id: str = None, 
                         *args, **kwargs) -> Any:
        """Execute operation on optimal connection pool.
        
        Args:
            operation: Operation to execute
            pool_id: Specific pool ID, or None for load-balanced selection
            *args: Operation arguments
            **kwargs: Operation keyword arguments
            
        Returns:
            Operation result
        """
        pool = self.get_pool(pool_id)
        if not pool:
            raise RuntimeError("No available connection pools")
        
        return pool.execute_with_timing(operation, *args, **kwargs)
    
    def health_check_all(self) -> Dict[str, ConnectionStatus]:
        """Perform health check on all pools.
        
        Returns:
            Dictionary of pool ID to status
        """
        with self._pools_lock:
            return {
                pool_id: pool.health_check()
                for pool_id, pool in self._pools.items()
            }
    
    def get_all_metrics(self) -> Dict[str, ConnectionMetrics]:
        """Get metrics for all connection pools.
        
        Returns:
            Dictionary of pool ID to metrics
        """
        with self._pools_lock:
            return {
                pool_id: pool.get_metrics()
                for pool_id, pool in self._pools.items()
            }
    
    def set_load_balancing_strategy(self, strategy: str) -> None:
        """Set load balancing strategy.
        
        Args:
            strategy: Load balancing strategy (round_robin, least_connections, response_time)
        """
        valid_strategies = ["round_robin", "least_connections", "response_time"]
        if strategy not in valid_strategies:
            raise ValueError(f"Invalid strategy. Must be one of: {valid_strategies}")
        
        self._load_balancing_strategy = strategy
        logger.info(f"Load balancing strategy set to: {strategy}")
    
    def start_health_monitoring(self) -> None:
        """Start background health monitoring."""
        if self._health_monitor_running:
            return
        
        self._health_monitor_running = True
        self._health_monitor_thread = threading.Thread(
            target=self._health_monitor_loop,
            daemon=True
        )
        self._health_monitor_thread.start()
        
        logger.info("Health monitoring started")
    
    def stop_health_monitoring(self) -> None:
        """Stop background health monitoring."""
        self._health_monitor_running = False
        if self._health_monitor_thread:
            self._health_monitor_thread.join(timeout=5)
        
        logger.info("Health monitoring stopped")
    
    def shutdown(self) -> None:
        """Shutdown all connection pools."""
        self.stop_health_monitoring()
        
        with self._pools_lock:
            for pool in self._pools.values():
                pool.disconnect()
            self._pools.clear()
        
        logger.info("Connection pool manager shutdown complete")
    
    def _select_optimal_pool(self, pools: List[ConnectionPool]) -> ConnectionPool:
        """Select optimal pool based on load balancing strategy."""
        if not pools:
            return None
        
        if self._load_balancing_strategy == "round_robin":
            self._round_robin_index = (self._round_robin_index + 1) % len(pools)
            return pools[self._round_robin_index]
        
        elif self._load_balancing_strategy == "least_connections":
            return min(pools, key=lambda p: p.get_metrics().active_connections)
        
        elif self._load_balancing_strategy == "response_time":
            return min(pools, key=lambda p: p.get_metrics().avg_response_time_ms)
        
        else:
            # Fallback to round robin
            return pools[0]
    
    def _health_monitor_loop(self) -> None:
        """Background health monitoring loop."""
        while self._health_monitor_running:
            try:
                self.health_check_all()
                time.sleep(self._health_check_interval)
            except Exception as e:
                logger.error(f"Health monitor error: {e}")
                time.sleep(5)  # Short sleep on error

# Global pool manager instance
_default_pool_manager: Optional[ConnectionPoolManager] = None

def get_pool_manager() -> ConnectionPoolManager:
    """Get or create default connection pool manager."""
    global _default_pool_manager
    if _default_pool_manager is None:
        _default_pool_manager = ConnectionPoolManager()
    return _default_pool_manager

__all__ = [
    'ConnectionPool', 'ConnectionPoolManager', 'PoolConfiguration',
    'ConnectionMetrics', 'ConnectionStatus', 'get_pool_manager'
]