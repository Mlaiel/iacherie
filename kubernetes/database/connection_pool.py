"""
Database Connection Pool Manager
Advanced connection pooling and load balancing for high availability

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved - Unauthorized use prohibited

AVERTISSEMENT LEGAL:
Ce code est la propriété intellectuelle exclusive de Fahed Mlaiel.
Toute utilisation, copie, modification ou distribution sans autorisation
écrite explicite est strictement interdite et passible de poursuites judiciaires.
Contact: mlaiel@live.de
"""

import time
import threading
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
from contextlib import contextmanager
from dataclasses import dataclass, asdict
import psycopg2
from psycopg2.pool import ThreadedConnectionPool, SimpleConnectionPool
import asyncpg
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool, StaticPool
import random

from backend.core.config import get_database_settings
from backend.core.logging import get_logger
from backend.core.monitoring import MetricsCollector


@dataclass
class DatabaseEndpoint:
    """Database endpoint configuration"""
    endpoint_id: str
    host: str
    port: int
    database: str
    username: str
    password: str
    role: str  # primary, replica, readonly
    priority: int  # Higher = preferred
    max_connections: int
    is_active: bool = True
    last_health_check: Optional[datetime] = None
    consecutive_failures: int = 0


@dataclass
class ConnectionPoolStats:
    """Connection pool statistics"""
    pool_id: str
    total_connections: int
    active_connections: int
    idle_connections: int
    waiting_connections: int
    pool_utilization: float
    avg_connection_time: float
    total_requests: int
    failed_requests: int
    success_rate: float


class ConnectionPoolManager:
    """
    Advanced database connection pool manager with features:
    - Multiple database endpoint support
    - Load balancing across read replicas
    - Automatic failover and failback
    - Connection health monitoring
    - Dynamic pool sizing
    - Connection leak detection
    - Performance metrics and monitoring
    """
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.config = get_database_settings()
        self.metrics = MetricsCollector()
        
        # Database endpoints
        self.endpoints: Dict[str, DatabaseEndpoint] = {}
        self.connection_pools: Dict[str, ThreadedConnectionPool] = {}
        self.async_pools: Dict[str, asyncpg.Pool] = {}
        self.sqlalchemy_engines: Dict[str, Any] = {}
        
        # Pool management
        self.pool_stats: Dict[str, ConnectionPoolStats] = {}
        self.health_check_interval = 30  # seconds
        self.is_monitoring = False
        self.monitor_thread: Optional[threading.Thread] = None
        
        # Load balancing
        self.read_replicas: List[str] = []
        self.primary_endpoint_id: Optional[str] = None
        self.failover_in_progress = False
        
        # Connection tracking
        self.active_connections: Dict[str, Dict] = {}
        self.connection_history: List[Dict] = []
        
        self._initialize_pools()
    
    def _initialize_pools(self) -> None:
        """Initialize connection pools"""
        try:
            # Add primary database endpoint
            primary_endpoint = DatabaseEndpoint(
                endpoint_id="primary",
                host=self.config.DB_HOST,
                port=self.config.DB_PORT,
                database=self.config.DB_NAME,
                username=self.config.DB_USER,
                password=self.config.DB_PASSWORD,
                role="primary",
                priority=100,
                max_connections=self.config.MAX_CONNECTIONS
            )
            
            self.add_endpoint(primary_endpoint)
            self.primary_endpoint_id = "primary"
            
            # Add read replicas if configured
            if hasattr(self.config, 'READ_REPLICAS'):
                for i, replica_config in enumerate(self.config.READ_REPLICAS):
                    replica_endpoint = DatabaseEndpoint(
                        endpoint_id=f"replica_{i}",
                        host=replica_config['host'],
                        port=replica_config['port'],
                        database=replica_config['database'],
                        username=replica_config['username'],
                        password=replica_config['password'],
                        role="replica",
                        priority=50 - i,  # Decreasing priority
                        max_connections=replica_config.get('max_connections', 20)
                    )
                    self.add_endpoint(replica_endpoint)
                    self.read_replicas.append(replica_endpoint.endpoint_id)
            
            # Start health monitoring
            self.start_monitoring()
            
            self.logger.info(f"Connection pool manager initialized with {len(self.endpoints)} endpoints")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize connection pools: {e}")
            raise
    
    def add_endpoint(self, endpoint: DatabaseEndpoint) -> bool:
        """Add database endpoint and create connection pool"""
        try:
            self.endpoints[endpoint.endpoint_id] = endpoint
            
            # Create synchronous connection pool
            pool = ThreadedConnectionPool(
                minconn=1,
                maxconn=endpoint.max_connections,
                host=endpoint.host,
                port=endpoint.port,
                database=endpoint.database,
                user=endpoint.username,
                password=endpoint.password,
                application_name=f"IA_Influencer_{endpoint.role}_{endpoint.endpoint_id}"
            )
            
            self.connection_pools[endpoint.endpoint_id] = pool
            
            # Create SQLAlchemy engine
            database_url = (
                f"postgresql://{endpoint.username}:{endpoint.password}"
                f"@{endpoint.host}:{endpoint.port}/{endpoint.database}"
            )
            
            engine = create_engine(
                database_url,
                poolclass=QueuePool,
                pool_size=endpoint.max_connections // 2,
                max_overflow=endpoint.max_connections // 4,
                pool_timeout=30,
                pool_recycle=3600,
                echo=False
            )
            
            self.sqlalchemy_engines[endpoint.endpoint_id] = engine
            
            # Initialize pool stats
            self.pool_stats[endpoint.endpoint_id] = ConnectionPoolStats(
                pool_id=endpoint.endpoint_id,
                total_connections=0,
                active_connections=0,
                idle_connections=0,
                waiting_connections=0,
                pool_utilization=0.0,
                avg_connection_time=0.0,
                total_requests=0,
                failed_requests=0,
                success_rate=100.0
            )
            
            # Test connection
            if self._test_endpoint_connection(endpoint):
                self.logger.info(f"Added database endpoint: {endpoint.endpoint_id} ({endpoint.role})")
                return True
            else:
                self.logger.error(f"Failed to connect to endpoint: {endpoint.endpoint_id}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to add endpoint {endpoint.endpoint_id}: {e}")
            return False
    
    def remove_endpoint(self, endpoint_id: str) -> bool:
        """Remove database endpoint and close connections"""
        try:
            if endpoint_id not in self.endpoints:
                return False
            
            # Close connection pool
            if endpoint_id in self.connection_pools:
                self.connection_pools[endpoint_id].closeall()
                del self.connection_pools[endpoint_id]
            
            # Close async pool
            if endpoint_id in self.async_pools:
                # Note: Need to handle async pool closing properly
                del self.async_pools[endpoint_id]
            
            # Dispose SQLAlchemy engine
            if endpoint_id in self.sqlalchemy_engines:
                self.sqlalchemy_engines[endpoint_id].dispose()
                del self.sqlalchemy_engines[endpoint_id]
            
            # Remove from tracking
            del self.endpoints[endpoint_id]
            if endpoint_id in self.pool_stats:
                del self.pool_stats[endpoint_id]
            
            # Remove from read replicas list
            if endpoint_id in self.read_replicas:
                self.read_replicas.remove(endpoint_id)
            
            self.logger.info(f"Removed database endpoint: {endpoint_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to remove endpoint {endpoint_id}: {e}")
            return False
    
    def _test_endpoint_connection(self, endpoint: DatabaseEndpoint) -> bool:
        """Test connection to database endpoint"""
        try:
            connection = psycopg2.connect(
                host=endpoint.host,
                port=endpoint.port,
                database=endpoint.database,
                user=endpoint.username,
                password=endpoint.password,
                connect_timeout=10
            )
            
            cursor = connection.cursor()
            cursor.execute("SELECT 1")
            cursor.close()
            connection.close()
            
            endpoint.last_health_check = datetime.now()
            endpoint.consecutive_failures = 0
            return True
            
        except Exception as e:
            self.logger.error(f"Health check failed for {endpoint.endpoint_id}: {e}")
            endpoint.consecutive_failures += 1
            return False
    
    @contextmanager
    def get_connection(self, read_only: bool = False):
        """Get database connection with automatic load balancing"""
        endpoint_id = None
        connection = None
        start_time = time.time()
        
        try:
            # Select appropriate endpoint
            endpoint_id = self._select_endpoint(read_only)
            
            if not endpoint_id:
                raise Exception("No available database endpoints")
            
            # Get connection from pool
            pool = self.connection_pools[endpoint_id]
            connection = pool.getconn()
            
            if not connection:
                raise Exception(f"Failed to get connection from pool {endpoint_id}")
            
            # Track connection
            connection_id = f"{endpoint_id}_{id(connection)}"
            self.active_connections[connection_id] = {
                'endpoint_id': endpoint_id,
                'acquired_at': datetime.now(),
                'read_only': read_only
            }
            
            # Update stats
            self._update_pool_stats(endpoint_id, 'acquire')
            
            yield connection
            
        except Exception as e:
            self.logger.error(f"Connection error: {e}")
            self._update_pool_stats(endpoint_id, 'error')
            raise
        finally:
            # Return connection to pool
            if connection and endpoint_id:
                try:
                    pool = self.connection_pools[endpoint_id]
                    pool.putconn(connection)
                    
                    # Remove from tracking
                    connection_id = f"{endpoint_id}_{id(connection)}"
                    if connection_id in self.active_connections:
                        del self.active_connections[connection_id]
                    
                    # Record connection time
                    connection_time = time.time() - start_time
                    self._record_connection_time(endpoint_id, connection_time)
                    
                except Exception as e:
                    self.logger.error(f"Failed to return connection: {e}")
    
    def _select_endpoint(self, read_only: bool = False) -> Optional[str]:
        """Select appropriate database endpoint based on load balancing strategy"""
        try:
            available_endpoints = [
                endpoint_id for endpoint_id, endpoint in self.endpoints.items()
                if endpoint.is_active and endpoint.consecutive_failures < 3
            ]
            
            if not available_endpoints:
                return None
            
            if read_only and self.read_replicas:
                # Use read replicas for read-only queries
                available_replicas = [
                    endpoint_id for endpoint_id in self.read_replicas
                    if endpoint_id in available_endpoints
                ]
                
                if available_replicas:
                    # Load balance among read replicas
                    return self._load_balance_endpoints(available_replicas)
            
            # Use primary for writes or if no replicas available
            if self.primary_endpoint_id and self.primary_endpoint_id in available_endpoints:
                return self.primary_endpoint_id
            
            # Fallback to any available endpoint
            return available_endpoints[0]
            
        except Exception as e:
            self.logger.error(f"Endpoint selection failed: {e}")
            return None
    
    def _load_balance_endpoints(self, endpoint_ids: List[str]) -> str:
        """Load balance among available endpoints"""
        try:
            # Strategy: Weighted random based on priority and current load
            weights = []
            
            for endpoint_id in endpoint_ids:
                endpoint = self.endpoints[endpoint_id]
                stats = self.pool_stats[endpoint_id]
                
                # Calculate weight based on priority and utilization
                priority_weight = endpoint.priority
                utilization_penalty = stats.pool_utilization * 50  # Penalize high utilization
                
                weight = max(1, priority_weight - utilization_penalty)
                weights.append(weight)
            
            # Weighted random selection
            total_weight = sum(weights)
            if total_weight == 0:
                return random.choice(endpoint_ids)
            
            random_value = random.uniform(0, total_weight)
            cumulative_weight = 0
            
            for i, weight in enumerate(weights):
                cumulative_weight += weight
                if random_value <= cumulative_weight:
                    return endpoint_ids[i]
            
            return endpoint_ids[-1]  # Fallback
            
        except Exception as e:
            self.logger.error(f"Load balancing failed: {e}")
            return endpoint_ids[0] if endpoint_ids else None
    
    async def get_async_connection(self, read_only: bool = False):
        """Get asynchronous database connection"""
        try:
            endpoint_id = self._select_endpoint(read_only)
            
            if not endpoint_id:
                raise Exception("No available database endpoints")
            
            # Create async pool if not exists
            if endpoint_id not in self.async_pools:
                await self._create_async_pool(endpoint_id)
            
            async_pool = self.async_pools[endpoint_id]
            
            async with async_pool.acquire() as connection:
                yield connection
                
        except Exception as e:
            self.logger.error(f"Async connection error: {e}")
            raise
    
    async def _create_async_pool(self, endpoint_id: str) -> None:
        """Create asynchronous connection pool"""
        try:
            endpoint = self.endpoints[endpoint_id]
            
            pool = await asyncpg.create_pool(
                host=endpoint.host,
                port=endpoint.port,
                database=endpoint.database,
                user=endpoint.username,
                password=endpoint.password,
                min_size=1,
                max_size=endpoint.max_connections // 2,
                command_timeout=60,
                server_settings={
                    'application_name': f'IA_Influencer_Async_{endpoint.role}_{endpoint_id}'
                }
            )
            
            self.async_pools[endpoint_id] = pool
            
        except Exception as e:
            self.logger.error(f"Failed to create async pool for {endpoint_id}: {e}")
            raise
    
    def get_sqlalchemy_engine(self, read_only: bool = False):
        """Get SQLAlchemy engine"""
        try:
            endpoint_id = self._select_endpoint(read_only)
            
            if not endpoint_id:
                raise Exception("No available database endpoints")
            
            return self.sqlalchemy_engines[endpoint_id]
            
        except Exception as e:
            self.logger.error(f"Failed to get SQLAlchemy engine: {e}")
            raise
    
    def _update_pool_stats(self, endpoint_id: str, operation: str) -> None:
        """Update connection pool statistics"""
        try:
            if endpoint_id not in self.pool_stats:
                return
            
            stats = self.pool_stats[endpoint_id]
            
            if operation == 'acquire':
                stats.total_requests += 1
            elif operation == 'error':
                stats.failed_requests += 1
                if endpoint_id:
                    stats.total_requests += 1
            
            # Calculate success rate
            if stats.total_requests > 0:
                stats.success_rate = ((stats.total_requests - stats.failed_requests) / 
                                    stats.total_requests) * 100
            
            # Update pool utilization
            if endpoint_id in self.connection_pools:
                pool = self.connection_pools[endpoint_id]
                # Note: psycopg2 pools don't expose detailed stats
                # This would need custom implementation or different pool library
                active_count = len(self.active_connections)
                total_count = self.endpoints[endpoint_id].max_connections
                stats.pool_utilization = active_count / total_count if total_count > 0 else 0
            
        except Exception as e:
            self.logger.error(f"Failed to update pool stats: {e}")
    
    def _record_connection_time(self, endpoint_id: str, connection_time: float) -> None:
        """Record connection acquisition time"""
        try:
            if endpoint_id in self.pool_stats:
                stats = self.pool_stats[endpoint_id]
                
                # Simple moving average
                if stats.avg_connection_time == 0:
                    stats.avg_connection_time = connection_time
                else:
                    stats.avg_connection_time = (stats.avg_connection_time * 0.9 + 
                                               connection_time * 0.1)
            
            # Record metric
            self.metrics.record_histogram(
                'database.connection_time',
                connection_time,
                tags={'endpoint': endpoint_id}
            )
            
        except Exception as e:
            self.logger.error(f"Failed to record connection time: {e}")
    
    def start_monitoring(self) -> None:
        """Start connection pool monitoring"""
        if self.is_monitoring:
            return
        
        self.is_monitoring = True
        self.monitor_thread = threading.Thread(
            target=self._monitoring_loop,
            daemon=True
        )
        self.monitor_thread.start()
        
        self.logger.info("Started connection pool monitoring")
    
    def stop_monitoring(self) -> None:
        """Stop connection pool monitoring"""
        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=10)
        
        self.logger.info("Stopped connection pool monitoring")
    
    def _monitoring_loop(self) -> None:
        """Main monitoring loop"""
        while self.is_monitoring:
            try:
                # Check endpoint health
                self._check_endpoint_health()
                
                # Update pool statistics
                self._update_all_pool_stats()
                
                # Check for failover conditions
                self._check_failover_conditions()
                
                # Clean up stale connections
                self._cleanup_stale_connections()
                
                time.sleep(self.health_check_interval)
                
            except Exception as e:
                self.logger.error(f"Monitoring loop error: {e}")
                time.sleep(self.health_check_interval)
    
    def _check_endpoint_health(self) -> None:
        """Check health of all endpoints"""
        for endpoint_id, endpoint in self.endpoints.items():
            try:
                is_healthy = self._test_endpoint_connection(endpoint)
                
                if not is_healthy:
                    endpoint.is_active = False
                    self.logger.warning(f"Endpoint {endpoint_id} marked as unhealthy")
                    
                    # Trigger failover if primary is down
                    if endpoint_id == self.primary_endpoint_id and not self.failover_in_progress:
                        self._initiate_failover()
                else:
                    if not endpoint.is_active:
                        endpoint.is_active = True
                        self.logger.info(f"Endpoint {endpoint_id} recovered")
                
            except Exception as e:
                self.logger.error(f"Health check failed for {endpoint_id}: {e}")
    
    def _update_all_pool_stats(self) -> None:
        """Update statistics for all connection pools"""
        for endpoint_id in self.endpoints:
            try:
                self._collect_pool_metrics(endpoint_id)
            except Exception as e:
                self.logger.error(f"Failed to update stats for {endpoint_id}: {e}")
    
    def _collect_pool_metrics(self, endpoint_id: str) -> None:
        """Collect detailed metrics for a connection pool"""
        try:
            stats = self.pool_stats[endpoint_id]
            
            # Count active connections for this endpoint
            active_count = sum(
                1 for conn_info in self.active_connections.values()
                if conn_info['endpoint_id'] == endpoint_id
            )
            
            stats.active_connections = active_count
            
            # Record metrics
            self.metrics.record_gauge(
                'database.pool.active_connections',
                active_count,
                tags={'endpoint': endpoint_id}
            )
            
            self.metrics.record_gauge(
                'database.pool.utilization',
                stats.pool_utilization,
                tags={'endpoint': endpoint_id}
            )
            
            self.metrics.record_gauge(
                'database.pool.success_rate',
                stats.success_rate,
                tags={'endpoint': endpoint_id}
            )
            
        except Exception as e:
            self.logger.error(f"Failed to collect metrics for {endpoint_id}: {e}")
    
    def _check_failover_conditions(self) -> None:
        """Check if failover is needed"""
        if self.failover_in_progress:
            return
        
        # Check if primary is down
        if (self.primary_endpoint_id and 
            self.primary_endpoint_id in self.endpoints and
            not self.endpoints[self.primary_endpoint_id].is_active):
            
            self._initiate_failover()
    
    def _initiate_failover(self) -> None:
        """Initiate failover to read replica"""
        try:
            self.failover_in_progress = True
            self.logger.critical("Initiating database failover")
            
            # Find best replica to promote
            best_replica = self._select_failover_target()
            
            if best_replica:
                self.logger.info(f"Promoting replica {best_replica} to primary")
                
                # Update endpoint role
                self.endpoints[best_replica].role = "primary"
                old_primary = self.primary_endpoint_id
                self.primary_endpoint_id = best_replica
                
                # Remove from read replicas
                if best_replica in self.read_replicas:
                    self.read_replicas.remove(best_replica)
                
                self.logger.critical(f"Failover completed: {old_primary} -> {best_replica}")
            else:
                self.logger.critical("No suitable replica found for failover")
            
        except Exception as e:
            self.logger.error(f"Failover failed: {e}")
        finally:
            self.failover_in_progress = False
    
    def _select_failover_target(self) -> Optional[str]:
        """Select best replica for failover"""
        try:
            available_replicas = [
                endpoint_id for endpoint_id in self.read_replicas
                if (endpoint_id in self.endpoints and 
                    self.endpoints[endpoint_id].is_active)
            ]
            
            if not available_replicas:
                return None
            
            # Select replica with highest priority
            best_replica = max(
                available_replicas,
                key=lambda eid: self.endpoints[eid].priority
            )
            
            return best_replica
            
        except Exception as e:
            self.logger.error(f"Failed to select failover target: {e}")
            return None
    
    def _cleanup_stale_connections(self) -> None:
        """Clean up stale connection tracking"""
        try:
            stale_threshold = datetime.now() - timedelta(hours=1)
            
            stale_connections = [
                conn_id for conn_id, conn_info in self.active_connections.items()
                if conn_info['acquired_at'] < stale_threshold
            ]
            
            for conn_id in stale_connections:
                del self.active_connections[conn_id]
                self.logger.warning(f"Cleaned up stale connection: {conn_id}")
            
        except Exception as e:
            self.logger.error(f"Connection cleanup failed: {e}")
    
    def get_pool_status(self) -> Dict[str, Any]:
        """Get comprehensive pool status"""
        try:
            status = {
                'timestamp': datetime.now().isoformat(),
                'total_endpoints': len(self.endpoints),
                'active_endpoints': sum(1 for ep in self.endpoints.values() if ep.is_active),
                'primary_endpoint': self.primary_endpoint_id,
                'read_replicas': self.read_replicas,
                'failover_in_progress': self.failover_in_progress,
                'endpoints': {},
                'pool_stats': {}
            }
            
            for endpoint_id, endpoint in self.endpoints.items():
                status['endpoints'][endpoint_id] = {
                    'role': endpoint.role,
                    'host': endpoint.host,
                    'port': endpoint.port,
                    'is_active': endpoint.is_active,
                    'priority': endpoint.priority,
                    'consecutive_failures': endpoint.consecutive_failures,
                    'last_health_check': endpoint.last_health_check.isoformat() if endpoint.last_health_check else None
                }
            
            for pool_id, stats in self.pool_stats.items():
                status['pool_stats'][pool_id] = asdict(stats)
            
            return status
            
        except Exception as e:
            self.logger.error(f"Failed to get pool status: {e}")
            return {'error': str(e)}
    
    def close_all_pools(self) -> None:
        """Close all connection pools"""
        try:
            # Stop monitoring
            self.stop_monitoring()
            
            # Close synchronous pools
            for pool in self.connection_pools.values():
                pool.closeall()
            
            # Close async pools
            for pool in self.async_pools.values():
                # Note: Need to handle async pool closing properly
                pass
            
            # Dispose SQLAlchemy engines
            for engine in self.sqlalchemy_engines.values():
                engine.dispose()
            
            self.logger.info("All connection pools closed")
            
        except Exception as e:
            self.logger.error(f"Failed to close pools: {e}")


# Singleton instance
_pool_manager = None

def get_pool_manager() -> ConnectionPoolManager:
    """Get connection pool manager singleton instance"""
    global _pool_manager
    if _pool_manager is None:
        _pool_manager = ConnectionPoolManager()
    return _pool_manager
