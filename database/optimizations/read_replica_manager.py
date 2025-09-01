"""Enhanced Read Replicas Configuration System

Advanced read replica management with intelligent load balancing, automatic failover,
and performance optimization for high-availability database operations.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import time
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Tuple, Any, Union
from enum import Enum
from dataclasses import dataclass, field
from collections import defaultdict, deque
import logging

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from .manager import ReplicationManager
from ...core.logging import get_logger

logger = get_logger(__name__)


class ReplicaStatus(Enum):
    """
Read replica status states"""

    ACTIVE = "active"
    SYNCING = "syncing"
    LAGGING = "lagging"
    FAILED = "failed"
    MAINTENANCE = "maintenance"
    STANDBY = "standby"


class LoadBalancingStrategy(Enum):
    """Load balancing strategies for read replicas"""

    ROUND_ROBIN = "round_robin"
    LEAST_CONNECTIONS = "least_connections"
    RESPONSE_TIME = "response_time"
    GEOGRAPHIC = "geographic"
    CAPACITY_BASED = "capacity_based"
    INTELLIGENT = "intelligent"


class FailoverMode(Enum):
    """Failover modes"""

    MANUAL = "manual"
    AUTOMATIC = "automatic"
    SEMI_AUTOMATIC = "semi_automatic"


@dataclass
class ReplicaConfig:
    """Read replica configuration"""
    replica_id: str
    host: str
    port: int
    database: str
    username: str
    password: str
    region: str = "default"
    weight: float = 1.0
    max_connections: int = 100
    connection_timeout: int = 30
    read_only: bool = True
    ssl_config: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)


@dataclass
class ReplicaMetrics:
    """Read replica performance metrics"""
    replica_id: str
    lag_seconds: float = 0.0
    active_connections: int = 0
    queries_per_second: float = 0.0
    avg_response_time: float = 0.0
    error_rate: float = 0.0
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    last_updated: datetime = field(default_factory=datetime.now)
    
    def health_score(self) -> float:
        """
Calculate overall health score (0-100)"""
        score = 100.0
        
        # Penalize lag
        if self.lag_seconds > 5:
            score -= min(50, self.lag_seconds * 2)
        
        # Penalize high response time
        if self.avg_response_time > 1.0:
            score -= min(30, self.avg_response_time * 10)
        
        # Penalize errors
        score -= min(30, self.error_rate * 100)
        
        # Penalize high resource usage
        if self.cpu_usage > 0.8:
            score -= 10
        if self.memory_usage > 0.8:
            score -= 10
        
        return max(0.0, score)


class IntelligentLoadBalancer:
    """
Intelligent load balancer for read replicas"""
    
    def __init__(self, strategy: LoadBalancingStrategy):
        self.strategy = strategy
        self.replica_metrics: Dict[str, ReplicaMetrics] = {}
        self.connection_counts: Dict[str, int] = defaultdict(int)
        self.round_robin_index = 0
        self.geographic_preferences: Dict[str, List[str]] = {}
        self._lock = asyncio.Lock()
    
    async def select_replica(self, available_replicas: List[str], 
                           client_region: Optional[str] = None,
                           query_type: str = "read") -> Optional[str]:
        """Select optimal replica based on strategy and current conditions"""
        async with self._lock:
            if not available_replicas:
                return None
            
            if len(available_replicas) == 1:
                return available_replicas[0]
            
            # Filter out unhealthy replicas
            healthy_replicas = self._filter_healthy_replicas(available_replicas)
            if not healthy_replicas:
                # If no healthy replicas, use best available
                healthy_replicas = available_replicas
            
            if self.strategy == LoadBalancingStrategy.ROUND_ROBIN:
                return self._round_robin_select(healthy_replicas)
            elif self.strategy == LoadBalancingStrategy.LEAST_CONNECTIONS:
                return self._least_connections_select(healthy_replicas)
            elif self.strategy == LoadBalancingStrategy.RESPONSE_TIME:
                return self._response_time_select(healthy_replicas)
            elif self.strategy == LoadBalancingStrategy.GEOGRAPHIC:
                return self._geographic_select(healthy_replicas, client_region)
            elif self.strategy == LoadBalancingStrategy.CAPACITY_BASED:
                return self._capacity_based_select(healthy_replicas)
            elif self.strategy == LoadBalancingStrategy.INTELLIGENT:
                return self._intelligent_select(healthy_replicas, client_region, query_type)
            else:
                return healthy_replicas[0]
    
    def _filter_healthy_replicas(self, replicas: List[str]) -> List[str]:
        """
Filter out unhealthy replicas"""
        healthy = []
        
        for replica_id in replicas:
            metrics = self.replica_metrics.get(replica_id)
            if metrics and metrics.health_score() > 50:  # Health threshold
                healthy.append(replica_id)
        
        return healthy if healthy else replicas  # Return all if none healthy
    
    def _round_robin_select(self, replicas: List[str]) -> str:
        """
Round-robin selection"""
        selected = replicas[self.round_robin_index % len(replicas)]
        self.round_robin_index += 1
        return selected
    
    def _least_connections_select(self, replicas: List[str]) -> str:
        """
Select replica with least connections"""
        return min(replicas, key=lambda r: self.connection_counts.get(r, 0))
    
    def _response_time_select(self, replicas: List[str]) -> str:
        """
Select replica with best response time"""
        def get_response_time(replica_id):
            metrics = self.replica_metrics.get(replica_id)
            return metrics.avg_response_time if metrics else float('inf')
        
        return min(replicas, key=get_response_time)
    
    def _geographic_select(self, replicas: List[str], client_region: Optional[str]) -> str:
        """
Select replica based on geographic proximity"""
        if not client_region:
            return self._round_robin_select(replicas)
        
        # Get preferred replicas for this region
        preferred = self.geographic_preferences.get(client_region, [])
        
        # Find available preferred replicas
        available_preferred = [r for r in replicas if r in preferred]
        
        if available_preferred:
            return self._response_time_select(available_preferred)
        else:
            return self._response_time_select(replicas)
    
    def _capacity_based_select(self, replicas: List[str]) -> str:
        """
Select replica based on current capacity"""
        def get_capacity_score(replica_id):
            metrics = self.replica_metrics.get(replica_id)
            if not metrics:
                return 0.0
            
            # Calculate available capacity
            connection_usage = self.connection_counts.get(replica_id, 0) / 100  # Assume max 100
            cpu_usage = metrics.cpu_usage
            memory_usage = metrics.memory_usage
            
            # Higher score is better (more available capacity)
            return 1.0 - max(connection_usage, cpu_usage, memory_usage)
        
        return max(replicas, key=get_capacity_score)
    
    def _intelligent_select(self, replicas: List[str], client_region: Optional[str], 
                          query_type: str) -> str:
        """
Intelligent selection combining multiple factors"""
        scores = {}
        
        for replica_id in replicas:
            metrics = self.replica_metrics.get(replica_id)
            if not metrics:
                scores[replica_id] = 0.0
                continue
            
            # Base score from health
            score = metrics.health_score() / 100.0
            
            # Adjust for capacity
            connection_usage = self.connection_counts.get(replica_id, 0) / 100
            score *= (1.0 - connection_usage)
            
            # Adjust for response time
            if metrics.avg_response_time > 0:
                score *= (1.0 / max(metrics.avg_response_time, 0.001))
            
            # Adjust for geographic proximity
            if client_region and replica_id in self.geographic_preferences.get(client_region, []):
                score *= 1.2  # 20% bonus for geographic proximity
            
            # Adjust for query type (some replicas might be optimized for specific queries)
            if query_type == "analytics" and "analytics" in replica_id:
                score *= 1.1  # 10% bonus for analytics queries
            
            scores[replica_id] = score
        
        # Select replica with highest score
        return max(scores.keys(), key=lambda k: scores[k])
    
    def update_metrics(self, replica_id: str, metrics: ReplicaMetrics):
        """Update replica metrics for load balancing decisions"""
        self.replica_metrics[replica_id] = metrics
    
    def update_connection_count(self, replica_id: str, delta: int):
        """
Update connection count for replica"""
        self.connection_counts[replica_id] = max(0, self.connection_counts[replica_id] + delta)
    
    def set_geographic_preferences(self, preferences: Dict[str, List[str]]):
        """
Set geographic preferences for regions"""
        self.geographic_preferences = preferences


class ReadReplicaMonitor:
    """
Monitor for read replica health and performance"""
    
    def __init__(self, replica_configs: Dict[str, ReplicaConfig]):
        self.replica_configs = replica_configs
        self.replica_engines: Dict[str, AsyncEngine] = {}
        self.replica_metrics: Dict[str, ReplicaMetrics] = {}
        self.monitoring_task: Optional[asyncio.Task] = None
        self.is_monitoring = False
        
    async def start_monitoring(self):
        """
Start replica monitoring"""
        if self.is_monitoring:
            return
        
        self.is_monitoring = True
        
        # Initialize engines for each replica
        for replica_id, config in self.replica_configs.items():
            try:
                engine = await self._create_replica_engine(config)
                self.replica_engines[replica_id] = engine
                self.replica_metrics[replica_id] = ReplicaMetrics(replica_id=replica_id)
            except Exception as e:
                logger.error(f"Failed to initialize replica {replica_id}: {e}")
        
        # Start monitoring task
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
        logger.info("Read replica monitoring started")
    
    async def stop_monitoring(self):
        """Stop replica monitoring"""
        self.is_monitoring = False
        
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
        
        # Close engines
        for engine in self.replica_engines.values():
            await engine.dispose()
        
        logger.info("Read replica monitoring stopped")
    
    async def _create_replica_engine(self, config: ReplicaConfig) -> AsyncEngine:
        """Create async engine for replica"""
        dsn = f"postgresql+asyncpg://{config.username}:{config.password}@{config.host}:{config.port}/{config.database}"
        
        return create_async_engine(
            dsn,
            pool_size=5,
            max_overflow=10,
            pool_timeout=config.connection_timeout,
            pool_recycle=3600,
            echo=False
        )
    
    async def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.is_monitoring:
            try:
                # Check all replicas
                for replica_id in self.replica_configs:
                    await self._check_replica_health(replica_id)
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Replica monitoring error: {e}")
                await asyncio.sleep(10)
    
    async def _check_replica_health(self, replica_id: str):
        """Check health of a specific replica"""
        try:
            engine = self.replica_engines.get(replica_id)
            if not engine:
                return
            
            start_time = time.time()
            
            # Test connectivity and get basic metrics
            async with engine.begin() as conn:
                # Check if replica is accessible
                await conn.execute(text("SELECT 1"))
                
                # Get replication lag
                lag_result = await conn.execute(text("""
                    SELECT EXTRACT(EPOCH FROM (now() - pg_last_xact_replay_timestamp())) as lag_seconds
                """))
                lag_row = lag_result.fetchone()
                lag_seconds = lag_row.lag_seconds if lag_row and lag_row.lag_seconds else 0.0
                
                # Get connection count
                conn_result = await conn.execute(text("""
                    SELECT count(*) as active_connections 
                    FROM pg_stat_activity 
                    WHERE state = 'active'
                """))
                conn_row = conn_result.fetchone()
                active_connections = conn_row.active_connections if conn_row else 0
                
                # Calculate response time
                response_time = time.time() - start_time
            
            # Update metrics
            metrics = self.replica_metrics[replica_id]
            metrics.lag_seconds = lag_seconds
            metrics.active_connections = active_connections
            metrics.avg_response_time = response_time
            metrics.error_rate = max(0, metrics.error_rate - 0.01)  # Decay error rate
            metrics.last_updated = datetime.now()
            
            # Update QPS (simplified)
            current_time = datetime.now()
            if hasattr(metrics, '_last_check_time'):
                time_diff = (current_time - metrics._last_check_time).total_seconds()
                if time_diff > 0:
                    # Estimate QPS based on activity
                    metrics.queries_per_second = active_connections / max(time_diff, 1)
            metrics._last_check_time = current_time
            
        except Exception as e:
            logger.warning(f"Health check failed for replica {replica_id}: {e}")
            
            # Update error metrics
            metrics = self.replica_metrics[replica_id]
            metrics.error_rate = min(1.0, metrics.error_rate + 0.1)
            metrics.last_updated = datetime.now()
    
    def get_replica_metrics(self, replica_id: str) -> Optional[ReplicaMetrics]:
        """Get metrics for specific replica"""
        return self.replica_metrics.get(replica_id)
    
    def get_all_metrics(self) -> Dict[str, ReplicaMetrics]:
        """
Get metrics for all replicas"""
        return self.replica_metrics.copy()
    
    async def test_replica_connectivity(self, replica_id: str) -> bool:
        """
Test connectivity to specific replica"""
        try:
            engine = self.replica_engines.get(replica_id)
            if not engine:
                return False
            
            async with engine.begin() as conn:
                await conn.execute(text("SELECT 1"))
            
            return True
            
        except Exception as e:
            logger.error(f"Connectivity test failed for replica {replica_id}: {e}")
            return False


class ReadReplicaManager:
    """Enhanced read replica manager with intelligent load balancing"""
    
    def __init__(self, primary_engine: AsyncEngine, 
                 replica_configs: Dict[str, ReplicaConfig],
                 strategy: LoadBalancingStrategy = LoadBalancingStrategy.INTELLIGENT):
        self.primary_engine = primary_engine
        self.replica_configs = replica_configs
        self.strategy = strategy
        
        # Components
        self.load_balancer = IntelligentLoadBalancer(strategy)
        self.monitor = ReadReplicaMonitor(replica_configs)
        
        # Replica management
        self.replica_engines: Dict[str, AsyncEngine] = {}
        self.replica_status: Dict[str, ReplicaStatus] = {}
        self.failover_mode = FailoverMode.AUTOMATIC
        
        # Statistics
        self.query_stats: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
        self.failover_history: List[Dict[str, Any]] = []
    
    async def initialize(self) -> bool:
        """
Initialize read replica manager"""
        try:
            logger.info("Initializing read replica manager")
            
            # Initialize replica engines
            for replica_id, config in self.replica_configs.items():
                try:
                    engine = await self._create_replica_engine(config)
                    self.replica_engines[replica_id] = engine
                    self.replica_status[replica_id] = ReplicaStatus.ACTIVE
                    
                    # Test connectivity
                    if await self._test_replica(replica_id):
                        logger.info(f"Replica {replica_id} initialized successfully")
                    else:
                        self.replica_status[replica_id] = ReplicaStatus.FAILED
                        logger.warning(f"Replica {replica_id} failed connectivity test")
                        
                except Exception as e:
                    logger.error(f"Failed to initialize replica {replica_id}: {e}")
                    self.replica_status[replica_id] = ReplicaStatus.FAILED
            
            # Configure geographic preferences
            self._setup_geographic_preferences()
            
            # Start monitoring
            await self.monitor.start_monitoring()
            
            # Update load balancer with initial metrics
            for replica_id in self.replica_configs:
                metrics = self.monitor.get_replica_metrics(replica_id)
                if metrics:
                    self.load_balancer.update_metrics(replica_id, metrics)
            
            logger.info(f"Read replica manager initialized with {len(self.replica_engines)} replicas")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize read replica manager: {e}")
            return False
    
    async def _create_replica_engine(self, config: ReplicaConfig) -> AsyncEngine:
        """Create async engine for replica"""
        dsn = f"postgresql+asyncpg://{config.username}:{config.password}@{config.host}:{config.port}/{config.database}"
        
        return create_async_engine(
            dsn,
            pool_size=min(config.max_connections // 2, 20),
            max_overflow=10,
            pool_timeout=config.connection_timeout,
            pool_recycle=3600,
            echo=False
        )
    
    async def _test_replica(self, replica_id: str) -> bool:
        """Test replica connectivity"""
        try:
            engine = self.replica_engines.get(replica_id)
            if not engine:
                return False
            
            async with engine.begin() as conn:
                result = await conn.execute(text("SELECT 1"))
                return result.fetchone() is not None
                
        except Exception as e:
            logger.error(f"Replica test failed for {replica_id}: {e}")
            return False
    
    def _setup_geographic_preferences(self):
        """Setup geographic preferences for load balancing"""
        preferences = {}
        
        for region in ["us-east", "us-west", "eu-central", "asia-pacific"]:
            # Find replicas in this region
            region_replicas = [
                replica_id for replica_id, config in self.replica_configs.items()
                if config.region == region
            ]
            
            if region_replicas:
                preferences[region] = region_replicas
        
        self.load_balancer.set_geographic_preferences(preferences)
    
    async def execute_read_query(self, query: str, *args, 
                                client_region: Optional[str] = None,
                                query_type: str = "read",
                                timeout: Optional[float] = None) -> Any:
        """Execute read query on optimal replica"""
        try:
            # Get available replicas
            available_replicas = [
                replica_id for replica_id, status in self.replica_status.items()
                if status == ReplicaStatus.ACTIVE
            ]
            
            if not available_replicas:
                # Fallback to primary if no replicas available
                logger.warning("No read replicas available, using primary")
                return await self._execute_on_primary(query, *args, timeout=timeout)
            
            # Select optimal replica
            selected_replica = await self.load_balancer.select_replica(
                available_replicas, client_region, query_type
            )
            
            if not selected_replica:
                return await self._execute_on_primary(query, *args, timeout=timeout)
            
            # Execute query on selected replica
            result = await self._execute_on_replica(selected_replica, query, *args, timeout=timeout)
            
            # Update statistics
            self.query_stats[selected_replica]["success"] += 1
            self.load_balancer.update_connection_count(selected_replica, 1)
            
            return result
            
        except Exception as e:
            logger.error(f"Read query execution failed: {e}")
            
            # Update error statistics
            if 'selected_replica' in locals():
                self.query_stats[selected_replica]["errors"] += 1
                # Mark replica as potentially problematic
                await self._handle_replica_error(selected_replica, e)
            
            # Fallback to primary
            return await self._execute_on_primary(query, *args, timeout=timeout)
        
        finally:
            # Update connection count
            if 'selected_replica' in locals():
                self.load_balancer.update_connection_count(selected_replica, -1)
    
    async def _execute_on_replica(self, replica_id: str, query: str, *args, 
                                timeout: Optional[float] = None) -> Any:
        """Execute query on specific replica"""
        engine = self.replica_engines.get(replica_id)
        if not engine:
            raise Exception(f"Replica {replica_id} not available")
        
        async with engine.begin() as conn:
            if timeout:
                result = await asyncio.wait_for(
                    conn.execute(text(query), *args),
                    timeout=timeout
                )
            else:
                result = await conn.execute(text(query), *args)
            
            return result.fetchall()
    
    async def _execute_on_primary(self, query: str, *args, 
                                timeout: Optional[float] = None) -> Any:
        """Execute query on primary database"""
        async with self.primary_engine.begin() as conn:
            if timeout:
                result = await asyncio.wait_for(
                    conn.execute(text(query), *args),
                    timeout=timeout
                )
            else:
                result = await conn.execute(text(query), *args)
            
            return result.fetchall()
    
    async def _handle_replica_error(self, replica_id: str, error: Exception):
        """
Handle replica error"""
        try:
            # Update replica status based on error
            if "connection" in str(error).lower():
                self.replica_status[replica_id] = ReplicaStatus.FAILED
                logger.warning(f"Marking replica {replica_id} as failed due to connection error")
                
                # Record failover
                self.failover_history.append({
                    'timestamp': datetime.now(),
                    'replica_id': replica_id,
                    'error': str(error),
                    'action': 'marked_failed'
                })
                
                # Trigger health check
                if self.failover_mode == FailoverMode.AUTOMATIC:
                    asyncio.create_task(self._attempt_replica_recovery(replica_id))
                    
        except Exception as e:
            logger.error(f"Error handling replica error: {e}")
    
    async def _attempt_replica_recovery(self, replica_id: str):
        """Attempt to recover failed replica"""
        try:
            logger.info(f"Attempting recovery for replica {replica_id}")
            
            # Wait before retry
            await asyncio.sleep(30)
            
            # Test connectivity
            if await self._test_replica(replica_id):
                self.replica_status[replica_id] = ReplicaStatus.ACTIVE
                logger.info(f"Replica {replica_id} recovered successfully")
                
                # Record recovery
                self.failover_history.append({
                    'timestamp': datetime.now(),
                    'replica_id': replica_id,
                    'action': 'recovered'
                })
            else:
                logger.warning(f"Replica {replica_id} recovery failed")
                
        except Exception as e:
            logger.error(f"Replica recovery error for {replica_id}: {e}")
    
    async def get_replica_stats(self) -> Dict[str, Any]:
        """Get comprehensive replica statistics"""
        try:
            stats = {
                'total_replicas': len(self.replica_configs),
                'active_replicas': len([s for s in self.replica_status.values() if s == ReplicaStatus.ACTIVE]),
                'failed_replicas': len([s for s in self.replica_status.values() if s == ReplicaStatus.FAILED]),
                'load_balancing_strategy': self.strategy.value,
                'failover_mode': self.failover_mode.value,
                'replicas': {}
            }
            
            # Get metrics for each replica
            for replica_id, config in self.replica_configs.items():
                metrics = self.monitor.get_replica_metrics(replica_id)
                query_stats = self.query_stats.get(replica_id, {})
                
                replica_stats = {
                    'status': self.replica_status.get(replica_id, ReplicaStatus.FAILED).value,
                    'region': config.region,
                    'weight': config.weight,
                    'queries_success': query_stats.get('success', 0),
                    'queries_errors': query_stats.get('errors', 0)
                }
                
                if metrics:
                    replica_stats.update({
                        'lag_seconds': metrics.lag_seconds,
                        'active_connections': metrics.active_connections,
                        'avg_response_time': metrics.avg_response_time,
                        'health_score': metrics.health_score(),
                        'last_updated': metrics.last_updated.isoformat()
                    })
                
                stats['replicas'][replica_id] = replica_stats
            
            # Add failover history
            stats['recent_failovers'] = self.failover_history[-10:]  # Last 10 failovers
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get replica stats: {e}")
            return {}
    
    async def shutdown(self):
        """Shutdown read replica manager"""
        try:
            # Stop monitoring
            await self.monitor.stop_monitoring()
            
            # Close all replica engines
            for engine in self.replica_engines.values():
                await engine.dispose()
            
            logger.info("Read replica manager shutdown completed")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")


# Export main classes
__all__ = [
    'ReadReplicaManager', 
    'ReplicaConfig', 
    'LoadBalancingStrategy', 
    'ReplicaStatus',
    'FailoverMode'
]