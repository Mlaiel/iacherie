"""🔗 Connection Pool Manager - Intelligent Database Connection Optimization
=========================================================================

Advanced connection pooling with adaptive scaling, load balancing, and intelligent
resource management for enterprise database environments.

Expert Roles Implementation:
🏗️ Backend Senior: Connection architecture + pooling strategies + resource management
🗄️ DBA Senior: Connection optimization + database-specific tuning + performance monitoring
🔒 Sécurité: Connection security + authentication + secure connection protocols
⚡ Performance: Connection metrics + load balancing + adaptive scaling algorithms
🔗 Microservices: Multi-tenant isolation + service-specific pools + circuit breakers

Author: Fahed Mlaiel (mlaiel@live.de)
Version: 1.0.0 Enterprise Production
Date: December 2025

⚠️ PROPRIÉTÉ INTELLECTUELLE - FAHED MLAIEL
==========================================
Cette architecture connection pooling est la propriété intellectuelle EXCLUSIVE de
Fahed Mlaiel. Toute reproduction sans autorisation écrite est INTERDITE.
"""

import asyncio
import logging
import time
import threading
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Callable, AsyncGenerator
from dataclasses import dataclass, field
from enum import Enum
from contextlib import asynccontextmanager
from collections import deque, defaultdict
import hashlib
import psutil

# Database connection libraries
try:
    import asyncpg
    import aiomysql
    # Safe Redis import with Python 3.12 compatibility
try:
    import aioredis
    REDIS_AVAILABLE = True
except (ImportError, TypeError) as e:
    # Handle Python 3.12 TimeoutError duplicate base class issue
    from protection.utils.redis_compat import MockRedis as aioredis, REDIS_AVAILABLE
    import logging
    logging.warning(f"Using Redis compatibility layer: {e}")
    from sqlalchemy import create_engine, pool
    from sqlalchemy.ext.asyncio import create_async_engine
    from sqlalchemy.pool import QueuePool, NullPool, StaticPool
except ImportError as e:
    logging.warning(f"Database connection libraries not available: {e}")

logger = logging.getLogger(__name__)

class DatabaseType(Enum):
    """Types de bases de données supportées."""
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    REDIS = "redis"
    MONGODB = "mongodb"
    SQLITE = "sqlite"
    ORACLE = "oracle"

class ConnectionState(Enum):
    """États des connexions dans le pool."""
    IDLE = "idle"
    ACTIVE = "active"
    TESTING = "testing"
    FAILED = "failed"
    CLOSED = "closed"

class LoadBalancingStrategy(Enum):
    """Stratégies d'équilibrage de charge."""
    ROUND_ROBIN = "round_robin"
    LEAST_CONNECTIONS = "least_connections"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    RESPONSE_TIME = "response_time"
    GEOGRAPHIC = "geographic"

class PoolScalingMode(Enum):
    """Modes de scaling automatique du pool."""
    STATIC = "static"
    DYNAMIC = "dynamic"
    PREDICTIVE = "predictive"

@dataclass
class DatabaseEndpoint:
    """Configuration d'un endpoint de base de données."""
    host: str
    port: int
    database: str
    username: str
    password: str
    db_type: DatabaseType
    ssl_enabled: bool = True
    connection_timeout: int = 30
    read_only: bool = False
    weight: float = 1.0
    region: str = "default"
    max_connections: int = 100

@dataclass
class ConnectionMetrics:
    """Métriques de performance d'une connexion."""
    connection_id: str
    endpoint: str
    state: ConnectionState
    created_at: datetime
    last_used: datetime
    total_queries: int
    avg_response_time: float
    error_count: int
    bytes_transferred: int
    active_time: float
    idle_time: float

@dataclass
class PoolConfiguration:
    """Configuration avancée du pool de connexions."""
    min_size: int = 5
    max_size: int = 20
    overflow: int = 10
    pool_timeout: int = 30
    pool_pre_ping: bool = True
    pool_recycle: int = 3600
    retry_attempts: int = 3
    retry_delay: float = 1.0
    health_check_interval: int = 60
    scaling_mode: PoolScalingMode = PoolScalingMode.DYNAMIC
    load_balancing: LoadBalancingStrategy = LoadBalancingStrategy.LEAST_CONNECTIONS

@dataclass
class CircuitBreakerConfig:
    """Configuration du circuit breaker."""
    failure_threshold: int = 5
    recovery_timeout: int = 60
    success_threshold: int = 3
    monitoring_window: int = 300

class ConnectionPool:
    """🔗 Pool de connexions avancé avec monitoring."""
    
    def __init__(self, endpoint: DatabaseEndpoint, config: PoolConfiguration):
        """Initialise le pool de connexions."""
        self.endpoint = endpoint
        self.config = config
        self.pool_id = hashlib.md5(f"{endpoint.host}:{endpoint.port}".encode()).hexdigest()[:12]
        
        # Pool state
        self._connections: Dict[str, Any] = {}
        self._available_connections: deque = deque()
        self._metrics: Dict[str, ConnectionMetrics] = {}
        self._lock = asyncio.Lock()
        
        # Circuit breaker
        self._circuit_breaker = CircuitBreakerConfig()
        self._failure_count = 0
        self._last_failure_time = None
        self._circuit_open = False
        
        # Performance tracking
        self._performance_history: List[float] = []
        self._load_factor = 0.0
        
        logger.info(f"Connection pool initialized for {endpoint.host}:{endpoint.port}")

    async def get_connection(self, timeout: Optional[float] = None) -> Any:
        """🔍 Obtient une connexion du pool avec gestion intelligente."""
        timeout = timeout or self.config.pool_timeout
        start_time = time.time()
        
        # Check circuit breaker
        if self._circuit_open:
            if time.time() - self._last_failure_time > self._circuit_breaker.recovery_timeout:
                self._circuit_open = False
                self._failure_count = 0
            else:
                raise Exception(f"Circuit breaker open for pool {self.pool_id}")
        
        async with self._lock:
            # Try to get existing available connection
            if self._available_connections:
                conn_id = self._available_connections.popleft()
                connection = self._connections[conn_id]
                
                # Health check
                if await self._health_check_connection(connection):
                    await self._update_connection_metrics(conn_id, "acquired")
                    return connection
                else:
                    # Remove unhealthy connection
                    await self._remove_connection(conn_id)
            
            # Create new connection if possible
            if len(self._connections) < self.config.max_size:
                connection = await self._create_new_connection()
                if connection:
                    return connection
            
            # Wait for available connection
            return await self._wait_for_connection(timeout)

    async def return_connection(self, connection: Any) -> None:
        """🔄 Retourne une connexion au pool."""
        async with self._lock:
            conn_id = self._get_connection_id(connection)
            if conn_id in self._connections:
                await self._update_connection_metrics(conn_id, "returned")
                self._available_connections.append(conn_id)

    async def close_pool(self) -> None:
        """🛑 Ferme proprement le pool de connexions."""
        async with self._lock:
            for conn_id in list(self._connections.keys()):
                await self._close_connection(conn_id)
            
            self._connections.clear()
            self._available_connections.clear()
            self._metrics.clear()
        
        logger.info(f"Connection pool {self.pool_id} closed")

    async def get_pool_stats(self) -> Dict[str, Any]:
        """📊 Retourne les statistiques du pool."""
        async with self._lock:
            active_connections = len(self._connections) - len(self._available_connections)
            
            stats = {
                "pool_id": self.pool_id,
                "endpoint": f"{self.endpoint.host}:{self.endpoint.port}",
                "total_connections": len(self._connections),
                "active_connections": active_connections,
                "available_connections": len(self._available_connections),
                "utilization_rate": active_connections / max(1, self.config.max_size),
                "circuit_breaker_status": "open" if self._circuit_open else "closed",
                "failure_count": self._failure_count,
                "avg_response_time": statistics.mean(self._performance_history) if self._performance_history else 0.0,
                "load_factor": self._load_factor
            }
            
            return stats

    # Méthodes privées

    async def _create_new_connection(self) -> Optional[Any]:
        """Crée une nouvelle connexion à la base de données."""
        try:
            connection = await self._establish_connection()
            if connection:
                conn_id = self._generate_connection_id()
                self._connections[conn_id] = connection
                
                # Initialize metrics
                self._metrics[conn_id] = ConnectionMetrics(
                    connection_id=conn_id,
                    endpoint=f"{self.endpoint.host}:{self.endpoint.port}",
                    state=ConnectionState.ACTIVE,
                    created_at=datetime.now(),
                    last_used=datetime.now(),
                    total_queries=0,
                    avg_response_time=0.0,
                    error_count=0,
                    bytes_transferred=0,
                    active_time=0.0,
                    idle_time=0.0
                )
                
                logger.debug(f"New connection created: {conn_id}")
                return connection
                
        except Exception as e:
            await self._handle_connection_failure(e)
            return None

    async def _establish_connection(self) -> Any:
        """Établit la connexion selon le type de base de données."""
        if self.endpoint.db_type == DatabaseType.POSTGRESQL:
            return await asyncpg.connect(
                host=self.endpoint.host,
                port=self.endpoint.port,
                user=self.endpoint.username,
                password=self.endpoint.password,
                database=self.endpoint.database,
                ssl='require' if self.endpoint.ssl_enabled else 'disable',
                command_timeout=self.endpoint.connection_timeout
            )
        elif self.endpoint.db_type == DatabaseType.MYSQL:
            return await aiomysql.connect(
                host=self.endpoint.host,
                port=self.endpoint.port,
                user=self.endpoint.username,
                password=self.endpoint.password,
                db=self.endpoint.database,
                ssl=self.endpoint.ssl_enabled,
                connect_timeout=self.endpoint.connection_timeout
            )
        elif self.endpoint.db_type == DatabaseType.REDIS:
            return await aioredis.create_redis_pool(
                f"redis://{self.endpoint.host}:{self.endpoint.port}",
                password=self.endpoint.password,
                ssl=self.endpoint.ssl_enabled
            )
        else:
            raise ValueError(f"Unsupported database type: {self.endpoint.db_type}")

    async def _health_check_connection(self, connection: Any) -> bool:
        """Vérifie la santé d'une connexion."""
        try:
            if self.endpoint.db_type == DatabaseType.POSTGRESQL:
                await connection.fetchval("SELECT 1")
            elif self.endpoint.db_type == DatabaseType.MYSQL:
                async with connection.cursor() as cursor:
                    await cursor.execute("SELECT 1")
            elif self.endpoint.db_type == DatabaseType.REDIS:
                await connection.ping()
            
            return True
        except Exception:
            return False

    async def _wait_for_connection(self, timeout: float) -> Any:
        """Attend qu'une connexion devienne disponible."""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            await asyncio.sleep(0.1)
            
            if self._available_connections:
                conn_id = self._available_connections.popleft()
                connection = self._connections[conn_id]
                
                if await self._health_check_connection(connection):
                    await self._update_connection_metrics(conn_id, "acquired_wait")
                    return connection
                else:
                    await self._remove_connection(conn_id)
        
        raise TimeoutError(f"Connection timeout after {timeout}s for pool {self.pool_id}")

    async def _update_connection_metrics(self, conn_id: str, action: str) -> None:
        """Met à jour les métriques d'une connexion."""
        if conn_id in self._metrics:
            metrics = self._metrics[conn_id]
            metrics.last_used = datetime.now()
            
            if action == "acquired":
                metrics.state = ConnectionState.ACTIVE
            elif action == "returned":
                metrics.state = ConnectionState.IDLE

    async def _handle_connection_failure(self, error: Exception) -> None:
        """Gère les échecs de connexion et le circuit breaker."""
        self._failure_count += 1
        self._last_failure_time = time.time()
        
        if self._failure_count >= self._circuit_breaker.failure_threshold:
            self._circuit_open = True
            logger.warning(f"Circuit breaker opened for pool {self.pool_id} after {self._failure_count} failures")
        
        logger.error(f"Connection failure in pool {self.pool_id}: {str(error)}")

    async def _remove_connection(self, conn_id: str) -> None:
        """Supprime une connexion défaillante du pool."""
        if conn_id in self._connections:
            await self._close_connection(conn_id)
            del self._connections[conn_id]
            del self._metrics[conn_id]

    async def _close_connection(self, conn_id: str) -> None:
        """Ferme une connexion spécifique."""
        try:
            connection = self._connections.get(conn_id)
            if connection:
                if self.endpoint.db_type == DatabaseType.POSTGRESQL:
                    await connection.close()
                elif self.endpoint.db_type == DatabaseType.MYSQL:
                    await connection.ensure_closed()
                elif self.endpoint.db_type == DatabaseType.REDIS:
                    connection.close()
                    await connection.wait_closed()
        except Exception as e:
            logger.warning(f"Error closing connection {conn_id}: {str(e)}")

    def _generate_connection_id(self) -> str:
        """Génère un ID unique pour une connexion."""
        return f"{self.pool_id}_{len(self._connections)}_{int(time.time())}"

    def _get_connection_id(self, connection: Any) -> Optional[str]:
        """Trouve l'ID d'une connexion donnée."""
        for conn_id, conn in self._connections.items():
            if conn is connection:
                return conn_id
        return None


class ConnectionPoolManager:
    """🎯 Gestionnaire principal des pools de connexions avec load balancing."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialise le gestionnaire de pools."""
        self.config = config or {}
        self.pools: Dict[str, ConnectionPool] = {}
        self.endpoints: Dict[str, DatabaseEndpoint] = {}
        
        # Load balancing
        self.load_balancer = LoadBalancingStrategy(
            self.config.get("load_balancing", "least_connections")
        )
        self._round_robin_counter = 0
        
        # Monitoring
        self._global_metrics = {
            "total_connections": 0,
            "active_pools": 0,
            "failed_connections": 0,
            "avg_response_time": 0.0
        }
        
        # Auto-scaling
        self._scaling_enabled = self.config.get("auto_scaling", True)
        self._scaling_thread = None
        
        logger.info("Connection Pool Manager initialized")

    async def add_endpoint(self, endpoint: DatabaseEndpoint, pool_config: PoolConfiguration) -> str:
        """📍 Ajoute un endpoint avec son pool de connexions."""
        endpoint_id = f"{endpoint.host}_{endpoint.port}_{endpoint.database}"
        
        # Store endpoint configuration
        self.endpoints[endpoint_id] = endpoint
        
        # Create connection pool
        pool = ConnectionPool(endpoint, pool_config)
        self.pools[endpoint_id] = pool
        
        self._global_metrics["active_pools"] += 1
        
        logger.info(f"Endpoint added: {endpoint_id}")
        return endpoint_id

    async def get_connection(self, 
                           endpoint_id: Optional[str] = None,
                           read_only: bool = False,
                           region: Optional[str] = None) -> Any:
        """🔍 Obtient une connexion optimale selon la stratégie de load balancing."""
        
        # Select optimal endpoint
        if endpoint_id:
            if endpoint_id not in self.pools:
                raise ValueError(f"Endpoint not found: {endpoint_id}")
            target_pool = self.pools[endpoint_id]
        else:
            target_pool = await self._select_optimal_pool(read_only, region)
        
        if not target_pool:
            raise Exception("No available database pools")
        
        # Get connection from selected pool
        connection = await target_pool.get_connection()
        self._global_metrics["total_connections"] += 1
        
        return connection

    async def return_connection(self, connection: Any) -> None:
        """🔄 Retourne une connexion au pool approprié."""
        # Find the pool for this connection
        for pool in self.pools.values():
            try:
                await pool.return_connection(connection)
                return
            except:
                continue
        
        logger.warning("Could not return connection to any pool")

    async def get_global_stats(self) -> Dict[str, Any]:
        """📊 Retourne les statistiques globales."""
        pool_stats = []
        total_connections = 0
        total_active = 0
        
        for pool_id, pool in self.pools.items():
            stats = await pool.get_pool_stats()
            pool_stats.append(stats)
            total_connections += stats["total_connections"]
            total_active += stats["active_connections"]
        
        global_stats = {
            "manager_stats": self._global_metrics.copy(),
            "pool_count": len(self.pools),
            "total_connections": total_connections,
            "total_active_connections": total_active,
            "global_utilization": total_active / max(1, total_connections),
            "load_balancing_strategy": self.load_balancer.value,
            "pools": pool_stats
        }
        
        return global_stats

    async def optimize_pools(self) -> Dict[str, Any]:
        """⚡ Optimise automatiquement les pools de connexions."""
        optimization_results = {
            "pools_optimized": 0,
            "connections_added": 0,
            "connections_removed": 0,
            "recommendations": []
        }
        
        for pool_id, pool in self.pools.items():
            stats = await pool.get_pool_stats()
            
            # Analyze utilization
            utilization = stats["utilization_rate"]
            
            if utilization > 0.8:  # High utilization
                optimization_results["recommendations"].append({
                    "pool_id": pool_id,
                    "action": "scale_up",
                    "reason": f"High utilization: {utilization:.2%}",
                    "suggested_size": min(pool.config.max_size + 5, 50)
                })
            elif utilization < 0.2:  # Low utilization
                optimization_results["recommendations"].append({
                    "pool_id": pool_id,
                    "action": "scale_down", 
                    "reason": f"Low utilization: {utilization:.2%}",
                    "suggested_size": max(pool.config.min_size, 5)
                })
        
        return optimization_results

    async def health_check_all_pools(self) -> Dict[str, Any]:
        """🏥 Vérifie la santé de tous les pools."""
        health_report = {
            "timestamp": datetime.now().isoformat(),
            "overall_health": "healthy",
            "pools": {}
        }
        
        unhealthy_pools = 0
        
        for pool_id, pool in self.pools.items():
            stats = await pool.get_pool_stats()
            
            # Determine health status
            if stats["circuit_breaker_status"] == "open":
                health_status = "unhealthy"
                unhealthy_pools += 1
            elif stats["failure_count"] > 3:
                health_status = "degraded"
            else:
                health_status = "healthy"
            
            health_report["pools"][pool_id] = {
                "status": health_status,
                "connections": stats["total_connections"],
                "utilization": stats["utilization_rate"],
                "failures": stats["failure_count"]
            }
        
        # Overall health
        if unhealthy_pools > len(self.pools) / 2:
            health_report["overall_health"] = "unhealthy"
        elif unhealthy_pools > 0:
            health_report["overall_health"] = "degraded"
        
        return health_report

    async def close_all_pools(self) -> None:
        """🛑 Ferme tous les pools de connexions."""
        for pool in self.pools.values():
            await pool.close_pool()
        
        self.pools.clear()
        self.endpoints.clear()
        
        logger.info("All connection pools closed")

    # Méthodes privées pour le load balancing

    async def _select_optimal_pool(self, read_only: bool, region: Optional[str]) -> Optional[ConnectionPool]:
        """Sélectionne le pool optimal selon la stratégie."""
        available_pools = []
        
        # Filter pools based on criteria
        for endpoint_id, pool in self.pools.items():
            endpoint = self.endpoints[endpoint_id]
            
            if read_only and not endpoint.read_only:
                continue
            if region and endpoint.region != region:
                continue
            
            available_pools.append((endpoint_id, pool, endpoint))
        
        if not available_pools:
            return None
        
        # Apply load balancing strategy
        if self.load_balancer == LoadBalancingStrategy.ROUND_ROBIN:
            return self._round_robin_selection(available_pools)
        elif self.load_balancer == LoadBalancingStrategy.LEAST_CONNECTIONS:
            return await self._least_connections_selection(available_pools)
        elif self.load_balancer == LoadBalancingStrategy.WEIGHTED_ROUND_ROBIN:
            return self._weighted_round_robin_selection(available_pools)
        elif self.load_balancer == LoadBalancingStrategy.RESPONSE_TIME:
            return await self._response_time_selection(available_pools)
        else:
            return available_pools[0][1]  # Fallback to first available

    def _round_robin_selection(self, pools: List[tuple[str, ConnectionPool, DatabaseEndpoint]]) -> ConnectionPool:
        """Sélection round-robin."""
        selected = pools[self._round_robin_counter % len(pools)]
        self._round_robin_counter += 1
        return selected[1]

    async def _least_connections_selection(self, pools: List[tuple[str, ConnectionPool, DatabaseEndpoint]]) -> ConnectionPool:
        """Sélection basée sur le nombre de connexions actives."""
        min_connections = float('inf')
        selected_pool = None
        
        for pool_id, pool, endpoint in pools:
            stats = await pool.get_pool_stats()
            active_connections = stats["active_connections"]
            
            if active_connections < min_connections:
                min_connections = active_connections
                selected_pool = pool
        
        return selected_pool

    def _weighted_round_robin_selection(self, pools: List[tuple[str, ConnectionPool, DatabaseEndpoint]]) -> ConnectionPool:
        """Sélection round-robin pondérée."""
        # Simplified implementation - could be more sophisticated
        weights = [endpoint.weight for _, _, endpoint in pools]
        total_weight = sum(weights)
        
        if total_weight == 0:
            return pools[0][1]
        
        # Select based on weight
        selection_point = (self._round_robin_counter % int(total_weight * 10)) / 10
        cumulative_weight = 0
        
        for (pool_id, pool, endpoint), weight in zip(pools, weights):
            cumulative_weight += weight
            if selection_point <= cumulative_weight:
                self._round_robin_counter += 1
                return pool
        
        return pools[0][1]

    async def _response_time_selection(self, pools: List[tuple[str, ConnectionPool, DatabaseEndpoint]]) -> ConnectionPool:
        """Sélection basée sur le temps de réponse."""
        best_response_time = float('inf')
        selected_pool = None
        
        for pool_id, pool, endpoint in pools:
            stats = await pool.get_pool_stats()
            response_time = stats["avg_response_time"]
            
            if response_time < best_response_time:
                best_response_time = response_time
                selected_pool = pool
        
        return selected_pool


# Context manager pour l'utilisation simple
@asynccontextmanager
async def get_database_connection(pool_manager: ConnectionPoolManager, 
                                endpoint_id: Optional[str] = None,
                                read_only: bool = False,
                                region: Optional[str] = None):
    """🎯 Context manager pour utilisation simple des connexions."""
    connection = await pool_manager.get_connection(endpoint_id, read_only, region)
    try:
        yield connection
    finally:
        await pool_manager.return_connection(connection)


# Fonction d'initialisation
async def initialize_connection_pool_manager(config: Optional[Dict[str, Any]] = None) -> ConnectionPoolManager:
    """🚀 Initialise le gestionnaire de pools de connexions."""
    manager = ConnectionPoolManager(config)
    logger.info("Connection Pool Manager ready for enterprise database connections")
    return manager


# Export des classes principales
__all__ = [
    "ConnectionPoolManager",
    "ConnectionPool",
    "DatabaseEndpoint",
    "PoolConfiguration",
    "DatabaseType",
    "ConnectionState",
    "LoadBalancingStrategy",
    "PoolScalingMode",
    "ConnectionMetrics",
    "CircuitBreakerConfig",
    "get_database_connection",
    "initialize_connection_pool_manager"
]