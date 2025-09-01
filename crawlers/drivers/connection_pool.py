"""Enterprise Connection Pool Manager
=================================

Advanced connection pooling system for HTTP/HTTPS requests with intelligent management.
Provides enterprise-grade connection reuse, monitoring, and optimization features.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

⚠️  LEGAL WARNING:
This code is proprietary and confidential. Any unauthorized copying, modification, 
distribution, or use without explicit written permission from Fahed Mlaiel is strictly 
prohibited and may result in legal action.

Professional Development Team Specialties:
🥇 Lead AI Developer & Backend Senior Engineer - Advanced automation systems
🥇 Machine Learning Engineer & Audio Processing Specialist - Intelligence optimization  
🥇 Database Administrator & Security Expert - Data protection and performance
🥇 Microservices Architect & DevOps Engineer - Scalable infrastructure
🥇 AI Prompt Engineer & Content Protection Specialist - Content security
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, Any, Set
from dataclasses import dataclass, field
from enum import Enum
import time
import ssl
from urllib.parse import urlparse
import weakref
from collections import defaultdict

import aiohttp
from aiohttp import ClientSession, TCPConnector, ClientTimeout
from aiohttp.client_exceptions import ClientError


class ConnectionStatus(Enum):
    """
Connection status states"""

    IDLE = "idle"
    ACTIVE = "active"
    BUSY = "busy"
    ERROR = "error"
    CLOSING = "closing"
    CLOSED = "closed"


class PoolStrategy(Enum):
    """Connection pool strategies"""

    ROUND_ROBIN = "round_robin"
    LEAST_CONNECTIONS = "least_connections"
    FASTEST_RESPONSE = "fastest_response"
    RANDOM = "random"


@dataclass
class ConnectionInfo:
    """Connection information and statistics"""
    connection_id: str
    host: str
    port: int
    scheme: str
    status: ConnectionStatus = ConnectionStatus.IDLE
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_used: datetime = field(default_factory=datetime.utcnow)
    requests_count: int = 0
    errors_count: int = 0
    average_response_time: float = 0.0
    total_bytes_sent: int = 0
    total_bytes_received: int = 0
    is_persistent: bool = True
    keep_alive_timeout: int = 30
    max_requests: int = 1000


@dataclass
class PoolConfiguration:
    """
Connection pool configuration"""
    max_connections_total: int = 100
    max_connections_per_host: int = 20
    connection_timeout: int = 10
    read_timeout: int = 30
    keep_alive_timeout: int = 30
    max_requests_per_connection: int = 1000
    enable_ssl_verification: bool = True
    enable_compression: bool = True
    enable_cookies: bool = True
    dns_cache_ttl: int = 300
    pool_strategy: PoolStrategy = PoolStrategy.LEAST_CONNECTIONS
    cleanup_interval: int = 60
    connection_reuse_threshold: float = 0.8


@dataclass
class PoolMetrics:
    """
Connection pool metrics"""
    total_connections: int = 0
    active_connections: int = 0
    idle_connections: int = 0
    failed_connections: int = 0
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    average_pool_utilization: float = 0.0
    peak_connections: int = 0
    connection_creation_rate: float = 0.0
    connection_reuse_rate: float = 0.0
    last_cleanup: Optional[datetime] = None


class ConnectionPool:
    """
    Enterprise connection pool for HTTP/HTTPS connections.
    
    Features:
    - Intelligent connection reuse and management
    - Multiple pool strategies (round-robin, least connections, etc.)
    - Automatic connection cleanup and health monitoring
    - SSL/TLS support with custom verification
    - Comprehensive metrics and monitoring
    - DNS caching and connection persistence
    """
    
    def __init__(
        self,
        config: PoolConfiguration,
        pool_id: Optional[str] = None
    ):
        self.config = config
        self.pool_id = pool_id or f"pool_{int(time.time())}"
        
        # Connection management
        self.connections: Dict[str, ConnectionInfo] = {}
        self.host_connections: Dict[str, List[str]] = defaultdict(list)
        self.session_pools: Dict[str, ClientSession] = {}
        
        # Pool strategy state
        self.last_used_indices: Dict[str, int] = defaultdict(int)
        self.host_response_times: Dict[str, List[float]] = defaultdict(list)
        
        # Metrics and monitoring
        self.metrics = PoolMetrics()
        self.start_time = datetime.utcnow()
        
        # Cleanup and maintenance
        self.cleanup_task: Optional[asyncio.Task] = None
        self.shutdown_event = asyncio.Event()
        
        # SSL context
        self.ssl_context = self._create_ssl_context()
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
    
    async def initialize(self) -> bool:
        """Initialize connection pool"""
        try:
            self.logger.info(f"Initializing connection pool: {self.pool_id}")
            
            # Start cleanup task
            self.cleanup_task = asyncio.create_task(self._cleanup_loop())
            
            self.logger.info(f"Connection pool {self.pool_id} initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize connection pool: {e}")
            return False
    
    async def get_session(self, host: str, port: int = None, scheme: str = "https") -> ClientSession:
        """Get or create a session for the specified host"""
        if port is None:
            port = 443 if scheme == "https" else 80
        
        host_key = f"{scheme}://{host}:{port}"
        
        # Check if session exists and is valid
        if host_key in self.session_pools:
            session = self.session_pools[host_key]
            if not session.closed:
                return session
            else:
                # Remove closed session
                del self.session_pools[host_key]
        
        # Create new session
        session = await self._create_session(host, port, scheme)
        self.session_pools[host_key] = session
        
        return session
    
    async def get_connection(self, url: str) -> str:
        """Get an optimal connection for the URL"""
        parsed = urlparse(url)
        host = parsed.hostname
        port = parsed.port or (443 if parsed.scheme == "https" else 80)
        scheme = parsed.scheme
        
        host_key = f"{scheme}://{host}:{port}"
        
        # Check if we have available connections for this host
        available_connections = [
            conn_id for conn_id in self.host_connections[host_key]
            if (self.connections[conn_id].status == ConnectionStatus.IDLE and
                self.connections[conn_id].requests_count < self.config.max_requests_per_connection)
        ]
        
        # Apply pool strategy to select connection
        if available_connections:
            connection_id = self._select_connection(available_connections, host_key)
            self.connections[connection_id].status = ConnectionStatus.ACTIVE
            self.connections[connection_id].last_used = datetime.utcnow()
            return connection_id
        
        # Check if we can create new connection
        if len(self.host_connections[host_key]) < self.config.max_connections_per_host:
            if self.metrics.total_connections < self.config.max_connections_total:
                return await self._create_connection(host, port, scheme)
        
        # Wait for available connection or use least busy
        if self.host_connections[host_key]:
            # Use least busy connection
            least_busy = min(
                self.host_connections[host_key],
                key=lambda conn_id: self.connections[conn_id].requests_count
            )
            self.connections[least_busy].status = ConnectionStatus.BUSY
            return least_busy
        
        # Last resort: create connection even if over limit
        return await self._create_connection(host, port, scheme)
    
    async def release_connection(self, connection_id: str, success: bool = True):
        """Release connection back to pool"""
        if connection_id not in self.connections:
            return
        
        connection = self.connections[connection_id]
        
        if success:
            connection.status = ConnectionStatus.IDLE
            connection.requests_count += 1
            self.metrics.successful_requests += 1
        else:
            connection.errors_count += 1
            self.metrics.failed_requests += 1
            
            # Mark connection as error if too many failures
            if connection.errors_count > 5:
                connection.status = ConnectionStatus.ERROR
        
        connection.last_used = datetime.utcnow()
        self.metrics.total_requests += 1
    
    async def close_connection(self, connection_id: str):
        """
Close and remove connection from pool"""
        if connection_id not in self.connections:
            return
        
        connection = self.connections[connection_id]
        connection.status = ConnectionStatus.CLOSING
        
        # Remove from host connections
        host_key = f"{connection.scheme}://{connection.host}:{connection.port}"
        if connection_id in self.host_connections[host_key]:
            self.host_connections[host_key].remove(connection_id)
        
        # Remove from connections
        del self.connections[connection_id]
        connection.status = ConnectionStatus.CLOSED
        
        self.metrics.total_connections -= 1
        self.logger.debug(f"Closed connection: {connection_id}")
    
    async def cleanup_stale_connections(self):
        """Clean up stale and expired connections"""
        current_time = datetime.utcnow()
        stale_connections = []
        
        for conn_id, connection in self.connections.items():
            # Check if connection is stale
            time_since_use = (current_time - connection.last_used).total_seconds()
            
            if (connection.status == ConnectionStatus.ERROR or
                time_since_use > connection.keep_alive_timeout or
                connection.requests_count >= self.config.max_requests_per_connection):
                stale_connections.append(conn_id)
        
        # Close stale connections
        for conn_id in stale_connections:
            await self.close_connection(conn_id)
        
        if stale_connections:
            self.logger.info(f"Cleaned up {len(stale_connections)} stale connections")
        
        self.metrics.last_cleanup = current_time
    
    async def shutdown(self):
        """Shutdown connection pool and cleanup resources"""
        self.logger.info(f"Shutting down connection pool: {self.pool_id}")
        
        # Signal shutdown
        self.shutdown_event.set()
        
        # Cancel cleanup task
        if self.cleanup_task:
            self.cleanup_task.cancel()
            try:
                await self.cleanup_task
            except asyncio.CancelledError:
                pass
        
        # Close all sessions
        for session in self.session_pools.values():
            if not session.closed:
                await session.close()
        
        # Clear all connections
        for conn_id in list(self.connections.keys()):
            await self.close_connection(conn_id)
        
        self.logger.info(f"Connection pool {self.pool_id} shutdown completed")
    
    def get_metrics(self) -> PoolMetrics:
        """Get current pool metrics"""
        # Update real-time metrics
        self.metrics.total_connections = len(self.connections)
        self.metrics.active_connections = len([
            c for c in self.connections.values()
            if c.status == ConnectionStatus.ACTIVE
        ])
        self.metrics.idle_connections = len([
            c for c in self.connections.values()
            if c.status == ConnectionStatus.IDLE
        ])
        self.metrics.failed_connections = len([
            c for c in self.connections.values()
            if c.status == ConnectionStatus.ERROR
        ])
        
        # Calculate utilization
        if self.config.max_connections_total > 0:
            self.metrics.average_pool_utilization = (
                self.metrics.total_connections / self.config.max_connections_total * 100
            )
        
        # Update peak connections
        if self.metrics.total_connections > self.metrics.peak_connections:
            self.metrics.peak_connections = self.metrics.total_connections
        
        return self.metrics
    
    def get_connection_info(self, connection_id: str) -> Optional[ConnectionInfo]:
        """
Get information about a specific connection"""
        return self.connections.get(connection_id)
    
    def get_host_connections(self, host: str) -> List[ConnectionInfo]:
        """
Get all connections for a specific host"""
        host_keys = [key for key in self.host_connections.keys() if host in key]
        connections = []
        
        for host_key in host_keys:
            for conn_id in self.host_connections[host_key]:
                if conn_id in self.connections:
                    connections.append(self.connections[conn_id])
        
        return connections
    
    async def health_check(self) -> bool:
        """
Perform health check on connection pool"""
        try:
            # Check if we can create a test session
            test_session = await self._create_session("httpbin.org", 443, "https")
            
            # Test with a simple request
            async with test_session.get(
                "https://httpbin.org/status/200",
                timeout=ClientTimeout(total=5)
            ) as response:
                success = response.status == 200
            
            await test_session.close()
            return success
            
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return False
    
    async def _create_session(self, host: str, port: int, scheme: str) -> ClientSession:
        """Create a new HTTP session"""
        # Create connector
        connector = TCPConnector(
            limit_per_host=self.config.max_connections_per_host,
            ssl=self.ssl_context if scheme == "https" else False,
            use_dns_cache=True,
            ttl_dns_cache=self.config.dns_cache_ttl,
            enable_cleanup_closed=True,
            keepalive_timeout=self.config.keep_alive_timeout
        )
        
        # Create timeout
        timeout = ClientTimeout(
            total=self.config.read_timeout,
            connect=self.config.connection_timeout
        )
        
        # Create session
        session = ClientSession(
            connector=connector,
            timeout=timeout,
            auto_decompress=self.config.enable_compression,
            cookie_jar=aiohttp.CookieJar() if self.config.enable_cookies else None
        )
        
        return session
    
    async def _create_connection(self, host: str, port: int, scheme: str) -> str:
        """Create a new connection"""
        connection_id = f"conn_{host}_{port}_{int(time.time() * 1000)}"
        
        connection = ConnectionInfo(
            connection_id=connection_id,
            host=host,
            port=port,
            scheme=scheme,
            keep_alive_timeout=self.config.keep_alive_timeout,
            max_requests=self.config.max_requests_per_connection
        )
        
        # Add to connections
        self.connections[connection_id] = connection
        
        # Add to host connections
        host_key = f"{scheme}://{host}:{port}"
        self.host_connections[host_key].append(connection_id)
        
        self.metrics.total_connections += 1
        
        self.logger.debug(f"Created connection: {connection_id} for {host_key}")
        return connection_id
    
    def _select_connection(self, available_connections: List[str], host_key: str) -> str:
        """Select connection based on pool strategy"""
        if self.config.pool_strategy == PoolStrategy.ROUND_ROBIN:
            index = self.last_used_indices[host_key] % len(available_connections)
            self.last_used_indices[host_key] += 1
            return available_connections[index]
        
        elif self.config.pool_strategy == PoolStrategy.LEAST_CONNECTIONS:
            return min(
                available_connections,
                key=lambda conn_id: self.connections[conn_id].requests_count
            )
        
        elif self.config.pool_strategy == PoolStrategy.FASTEST_RESPONSE:
            return min(
                available_connections,
                key=lambda conn_id: self.connections[conn_id].average_response_time
            )
        
        else:  # RANDOM
            import random
            return random.choice(available_connections)
    
    def _create_ssl_context(self) -> ssl.SSLContext:
        """
Create SSL context for HTTPS connections"""
        context = ssl.create_default_context()
        
        if not self.config.enable_ssl_verification:
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
        
        return context
    
    async def _cleanup_loop(self):
        """
Main cleanup loop"""
        while not self.shutdown_event.is_set():
            try:
                await self.cleanup_stale_connections()
                await asyncio.sleep(self.config.cleanup_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in cleanup loop: {e}")
                await asyncio.sleep(self.config.cleanup_interval)


class ConnectionPoolManager:
    """
    Manager for multiple connection pools with automatic load balancing.
    
    Features:
    - Multiple pool management
    - Automatic pool selection
    - Load balancing across pools
    - Centralized monitoring and metrics
    """
    
    def __init__(
        self,
        default_config: Optional[PoolConfiguration] = None,
        max_pools: int = 10
    ):
        self.default_config = default_config or PoolConfiguration()
        self.max_pools = max_pools
        
        # Pool management
        self.pools: Dict[str, ConnectionPool] = {}
        self.pool_assignments: Dict[str, str] = {}  # host -> pool_id
        
        # Load balancing
        self.pool_usage_counts: Dict[str, int] = defaultdict(int)
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
    
    async def initialize(self) -> bool:
        """
Initialize connection pool manager"""
        try:
            self.logger.info("Initializing connection pool manager...")
            
            # Create default pool
            default_pool = ConnectionPool(self.default_config, "default")
            await default_pool.initialize()
            self.pools["default"] = default_pool
            
            self.logger.info("Connection pool manager initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize connection pool manager: {e}")
            return False
    
    async def get_pool_for_host(self, host: str) -> ConnectionPool:
        """Get optimal pool for the specified host"""
        # Check if host has assigned pool
        if host in self.pool_assignments:
            pool_id = self.pool_assignments[host]
            if pool_id in self.pools:
                return self.pools[pool_id]
        
        # Find least used pool
        if self.pools:
            pool_id = min(self.pool_usage_counts.keys(), key=lambda x: self.pool_usage_counts[x])
            self.pool_assignments[host] = pool_id
            self.pool_usage_counts[pool_id] += 1
            return self.pools[pool_id]
        
        # Return default pool
        return self.pools["default"]
    
    async def create_pool(
        self,
        pool_id: str,
        config: Optional[PoolConfiguration] = None
    ) -> bool:
        """Create a new connection pool"""
        if len(self.pools) >= self.max_pools:
            self.logger.warning("Maximum number of pools reached")
            return False
        
        if pool_id in self.pools:
            self.logger.warning(f"Pool already exists: {pool_id}")
            return False
        
        try:
            pool_config = config or self.default_config
            pool = ConnectionPool(pool_config, pool_id)
            await pool.initialize()
            
            self.pools[pool_id] = pool
            self.pool_usage_counts[pool_id] = 0
            
            self.logger.info(f"Created connection pool: {pool_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create pool {pool_id}: {e}")
            return False
    
    async def remove_pool(self, pool_id: str) -> bool:
        """Remove and shutdown a connection pool"""
        if pool_id not in self.pools:
            return False
        
        try:
            pool = self.pools[pool_id]
            await pool.shutdown()
            
            # Remove from pools
            del self.pools[pool_id]
            del self.pool_usage_counts[pool_id]
            
            # Update assignments
            hosts_to_reassign = [
                host for host, assigned_pool in self.pool_assignments.items()
                if assigned_pool == pool_id
            ]
            for host in hosts_to_reassign:
                del self.pool_assignments[host]
            
            self.logger.info(f"Removed connection pool: {pool_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to remove pool {pool_id}: {e}")
            return False
    
    async def shutdown(self):
        """Shutdown all connection pools"""
        self.logger.info("Shutting down connection pool manager...")
        
        for pool_id in list(self.pools.keys()):
            await self.remove_pool(pool_id)
        
        self.logger.info("Connection pool manager shutdown completed")
    
    def get_all_metrics(self) -> Dict[str, PoolMetrics]:
        """Get metrics from all pools"""
        return {
            pool_id: pool.get_metrics()
            for pool_id, pool in self.pools.items()
        }
    
    async def health_check(self) -> Dict[str, bool]:
        """
Perform health check on all pools"""
        results = {}
        
        for pool_id, pool in self.pools.items():
            try:
                results[pool_id] = await pool.health_check()
            except Exception as e:
                self.logger.error(f"Health check failed for pool {pool_id}: {e}")
                results[pool_id] = False
        
        return results


# Convenience functions
def create_pool_configuration(
    max_connections: int = 100,
    max_per_host: int = 20,
    strategy: PoolStrategy = PoolStrategy.LEAST_CONNECTIONS
) -> PoolConfiguration:
    """Create connection pool configuration"""
    return PoolConfiguration(
        max_connections_total=max_connections,
        max_connections_per_host=max_per_host,
        pool_strategy=strategy
    )


async def create_connection_pool(
    config: Optional[PoolConfiguration] = None,
    pool_id: Optional[str] = None
) -> ConnectionPool:
    """
Create and initialize a connection pool"""
    pool_config = config or PoolConfiguration()
    pool = ConnectionPool(pool_config, pool_id)
    await pool.initialize()
    return pool


async def create_pool_manager(
    default_config: Optional[PoolConfiguration] = None
) -> ConnectionPoolManager:
    """
Create and initialize a connection pool manager"""
    manager = ConnectionPoolManager(default_config)
    await manager.initialize()
    return manager
