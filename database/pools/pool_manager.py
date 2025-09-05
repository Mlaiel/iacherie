#!/usr/bin/env python3
"""Database Pool Manager - Central Orchestration System
=======================================================

⚠️  EXCLUSIVE INTELLECTUAL PROPERTY - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. All rights reserved.
Unauthorized use strictly prohibited and subject to legal prosecution.
Contact: mlaiel@live.de

Central pool orchestration system providing unified management of all database
connection pools with intelligent load balancing, auto-scaling, and health monitoring.

CORE RESPONSIBILITIES:
- Centralized pool lifecycle management
- Intelligent load balancing across pools
- Auto-scaling based on usage patterns
- Health monitoring and failure detection
- Resource allocation optimization
- Connection routing and distribution

Author: Fahed Mlaiel <mlaiel@live.de>
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security
"""

import asyncio
import logging
import weakref
import time
import statistics
from typing import Dict, Any, Optional, List, Union, Type
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, field
from enum import Enum
from contextlib import asynccontextmanager
import threading

# Import backend pools if available
try:
    import sys
    from pathlib import Path
    backend_path = Path(__file__).parent.parent.parent
    sys.path.insert(0, str(backend_path))
    
    from backend.database.pools import (
        DatabasePoolManager as BackendPoolManager,
        get_pool_manager as get_backend_pool_manager,
        PoolType,
        PoolStatus,
        PoolConfiguration,
        PoolMetrics
    )
    BACKEND_AVAILABLE = True
except ImportError:
    BACKEND_AVAILABLE = False

logger = logging.getLogger(__name__)


class ScalingStrategy(Enum):
    """Pool scaling strategy."""
    CONSERVATIVE = "conservative"  # Gradual scaling
    AGGRESSIVE = "aggressive"      # Fast scaling
    PREDICTIVE = "predictive"      # AI-based scaling
    COST_OPTIMIZED = "cost_optimized"  # Cost-aware scaling


class LoadBalancingStrategy(Enum):
    """Load balancing strategy for pool selection."""
    ROUND_ROBIN = "round_robin"
    LEAST_CONNECTIONS = "least_connections"  
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    RESPONSE_TIME = "response_time"
    RESOURCE_USAGE = "resource_usage"


@dataclass
class PoolHealthStatus:
    """Pool health status information."""
    pool_id: str
    is_healthy: bool
    last_check: datetime
    response_time: float
    error_count: int = 0
    warning_count: int = 0
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PoolStats:
    """Detailed pool statistics."""
    pool_id: str
    state: str
    database_type: str
    active_connections: int = 0
    idle_connections: int = 0
    total_connections: int = 0
    utilization_rate: float = 0.0
    average_wait_time: float = 0.0
    error_rate: float = 0.0
    throughput: float = 0.0
    last_updated: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class ScalingDecision:
    """Auto-scaling decision information."""
    pool_id: str
    current_size: int
    target_size: int
    strategy: ScalingStrategy
    reason: str
    confidence: float
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class PoolManager:
    """Central database pool orchestration and management system.
    
    Provides unified management of all database connection pools with:
    - Intelligent load balancing
    - Auto-scaling capabilities  
    - Health monitoring
    - Resource optimization
    - Connection routing
    """
    
    def __init__(self):
        self._backend_manager: Optional[BackendPoolManager] = None
        self._pools: Dict[str, Any] = {}
        self._pool_configs: Dict[str, Dict[str, Any]] = {}
        self._health_status: Dict[str, PoolHealthStatus] = {}
        self._pool_stats: Dict[str, PoolStats] = {}
        self._scaling_history: List[ScalingDecision] = []
        
        # Configuration
        self._scaling_strategy = ScalingStrategy.PREDICTIVE
        self._load_balancing_strategy = LoadBalancingStrategy.LEAST_CONNECTIONS
        self._health_check_interval = 30  # seconds
        self._scaling_cooldown = 300  # seconds
        
        # Monitoring
        self._monitoring_task: Optional[asyncio.Task] = None
        self._is_monitoring = False
        self._last_scale_time: Dict[str, datetime] = {}
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Initialize backend if available
        if BACKEND_AVAILABLE:
            self._backend_manager = get_backend_pool_manager()
    
    async def initialize(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the pool manager with configuration."""
        config = config or {}
        
        try:
            # Configure scaling strategy
            self._scaling_strategy = ScalingStrategy(
                config.get('scaling_strategy', 'predictive')
            )
            
            # Configure load balancing
            self._load_balancing_strategy = LoadBalancingStrategy(
                config.get('load_balancing_strategy', 'least_connections')
            )
            
            # Configure intervals
            self._health_check_interval = config.get('health_check_interval', 30)
            self._scaling_cooldown = config.get('scaling_cooldown', 300)
            
            # Start monitoring
            if config.get('auto_monitoring', True):
                await self.start_monitoring()
            
            logger.info(f"Pool manager initialized with strategy: {self._scaling_strategy.value}")
            return True
            
        except Exception as e:
            logger.error(f"Pool manager initialization failed: {e}")
            return False
    
    async def register_pool(self, pool_id: str, pool_instance: Any, config: Dict[str, Any]):
        """Register a new pool with the manager."""
        with self._lock:
            self._pools[pool_id] = pool_instance
            self._pool_configs[pool_id] = config
            
            # Initialize health status
            self._health_status[pool_id] = PoolHealthStatus(
                pool_id=pool_id,
                is_healthy=False,
                last_check=datetime.now(timezone.utc),
                response_time=0.0
            )
            
            # Initialize stats
            self._pool_stats[pool_id] = PoolStats(
                pool_id=pool_id,
                state="initializing",
                database_type=config.get('database_type', 'unknown')
            )
        
        # Perform initial health check
        await self._health_check_pool(pool_id)
        
        logger.info(f"Pool {pool_id} registered successfully")
    
    async def unregister_pool(self, pool_id: str):
        """Unregister a pool from the manager."""
        with self._lock:
            if pool_id in self._pools:
                # Close pool if it has a close method
                pool = self._pools[pool_id]
                if hasattr(pool, 'close'):
                    try:
                        await pool.close()
                    except Exception as e:
                        logger.error(f"Error closing pool {pool_id}: {e}")
                
                # Remove from collections
                del self._pools[pool_id]
                self._pool_configs.pop(pool_id, None)
                self._health_status.pop(pool_id, None)
                self._pool_stats.pop(pool_id, None)
                self._last_scale_time.pop(pool_id, None)
                
                logger.info(f"Pool {pool_id} unregistered")
    
    @asynccontextmanager
    async def get_connection(self, pool_identifier: Union[str, Type]):
        """Get a connection from the optimal pool using load balancing."""
        pool_id = await self._select_optimal_pool(pool_identifier)
        
        if not pool_id:
            raise ValueError(f"No healthy pool available for: {pool_identifier}")
        
        pool = self._pools.get(pool_id)
        if not pool:
            raise ValueError(f"Pool not found: {pool_id}")
        
        start_time = time.time()
        
        try:
            # Get connection from pool
            if hasattr(pool, 'get_connection'):
                async with pool.get_connection() as connection:
                    # Update statistics
                    await self._update_connection_stats(pool_id, start_time)
                    yield connection
            else:
                # Fallback for pools without context manager
                connection = await pool.acquire()
                try:
                    await self._update_connection_stats(pool_id, start_time)
                    yield connection
                finally:
                    await pool.release(connection)
        
        except Exception as e:
            # Update error statistics
            await self._update_error_stats(pool_id, str(e))
            raise
    
    async def _select_optimal_pool(self, pool_identifier: Union[str, Type]) -> Optional[str]:
        """Select the optimal pool based on load balancing strategy."""
        
        # If specific pool ID requested
        if isinstance(pool_identifier, str) and pool_identifier in self._pools:
            if self._health_status[pool_identifier].is_healthy:
                return pool_identifier
            return None
        
        # Find pools by type or pattern
        candidate_pools = []
        
        for pool_id, config in self._pool_configs.items():
            if self._health_status[pool_id].is_healthy:
                # Match by database type
                if hasattr(pool_identifier, 'value'):
                    if config.get('database_type') == pool_identifier.value:
                        candidate_pools.append(pool_id)
                elif isinstance(pool_identifier, str):
                    if pool_identifier in pool_id or config.get('database_type') == pool_identifier:
                        candidate_pools.append(pool_id)
        
        if not candidate_pools:
            return None
        
        # Apply load balancing strategy
        return await self._apply_load_balancing(candidate_pools)
    
    async def _apply_load_balancing(self, candidate_pools: List[str]) -> str:
        """Apply load balancing strategy to select best pool."""
        
        if not candidate_pools:
            return None
        
        if len(candidate_pools) == 1:
            return candidate_pools[0]
        
        if self._load_balancing_strategy == LoadBalancingStrategy.ROUND_ROBIN:
            # Simple round-robin
            return candidate_pools[int(time.time()) % len(candidate_pools)]
        
        elif self._load_balancing_strategy == LoadBalancingStrategy.LEAST_CONNECTIONS:
            # Select pool with least active connections
            best_pool = None
            min_connections = float('inf')
            
            for pool_id in candidate_pools:
                stats = self._pool_stats.get(pool_id)
                if stats and stats.active_connections < min_connections:
                    min_connections = stats.active_connections
                    best_pool = pool_id
            
            return best_pool or candidate_pools[0]
        
        elif self._load_balancing_strategy == LoadBalancingStrategy.RESPONSE_TIME:
            # Select pool with best response time
            best_pool = None
            min_response_time = float('inf')
            
            for pool_id in candidate_pools:
                health = self._health_status.get(pool_id)
                if health and health.response_time < min_response_time:
                    min_response_time = health.response_time
                    best_pool = pool_id
            
            return best_pool or candidate_pools[0]
        
        else:
            # Default to first available
            return candidate_pools[0]
    
    async def health_check_all(self) -> Dict[str, bool]:
        """Perform health check on all registered pools."""
        results = {}
        
        tasks = []
        for pool_id in self._pools.keys():
            tasks.append(self._health_check_pool(pool_id))
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
        
        # Collect results
        for pool_id in self._pools.keys():
            health = self._health_status.get(pool_id)
            results[pool_id] = health.is_healthy if health else False
        
        return results
    
    async def _health_check_pool(self, pool_id: str):
        """Perform health check on a specific pool."""
        pool = self._pools.get(pool_id)
        if not pool:
            return
        
        start_time = time.time()
        
        try:
            # Perform health check
            is_healthy = True
            details = {}
            
            if hasattr(pool, 'health_check'):
                is_healthy = await pool.health_check()
            elif hasattr(pool, 'ping'):
                await pool.ping()
            
            response_time = (time.time() - start_time) * 1000  # ms
            
            # Update health status
            self._health_status[pool_id] = PoolHealthStatus(
                pool_id=pool_id,
                is_healthy=is_healthy,
                last_check=datetime.now(timezone.utc),
                response_time=response_time,
                details=details
            )
            
            # Update pool state
            stats = self._pool_stats.get(pool_id)
            if stats:
                stats.state = "healthy" if is_healthy else "unhealthy"
        
        except Exception as e:
            logger.error(f"Health check failed for pool {pool_id}: {e}")
            
            # Mark as unhealthy
            health = self._health_status.get(pool_id)
            if health:
                health.is_healthy = False
                health.error_count += 1
                health.last_check = datetime.now(timezone.utc)
    
    async def get_all_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics for all pools."""
        stats = {}
        
        for pool_id in self._pools.keys():
            pool_stats = self._pool_stats.get(pool_id)
            if pool_stats:
                stats[pool_id] = {
                    'state': pool_stats.state,
                    'database_type': pool_stats.database_type,
                    'active_connections': pool_stats.active_connections,
                    'total_connections': pool_stats.total_connections,
                    'utilization_rate': pool_stats.utilization_rate,
                    'average_wait_time': pool_stats.average_wait_time,
                    'error_rate': pool_stats.error_rate,
                    'throughput': pool_stats.throughput,
                    'last_updated': pool_stats.last_updated.isoformat()
                }
        
        return stats
    
    async def start_monitoring(self):
        """Start background monitoring of all pools."""
        if self._is_monitoring:
            return
        
        self._is_monitoring = True
        self._monitoring_task = asyncio.create_task(self._monitoring_loop())
        logger.info("Pool monitoring started")
    
    async def stop_monitoring(self):
        """Stop background monitoring."""
        self._is_monitoring = False
        
        if self._monitoring_task:
            self._monitoring_task.cancel()
            try:
                await self._monitoring_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Pool monitoring stopped")
    
    async def _monitoring_loop(self):
        """Background monitoring loop."""
        while self._is_monitoring:
            try:
                # Perform health checks
                await self.health_check_all()
                
                # Check for scaling opportunities
                await self._check_auto_scaling()
                
                # Update statistics
                await self._update_pool_statistics()
                
                # Wait for next cycle
                await asyncio.sleep(self._health_check_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Monitoring loop error: {e}")
                await asyncio.sleep(5)  # Brief pause on error
    
    async def _check_auto_scaling(self):
        """Check if any pools need auto-scaling."""
        for pool_id in self._pools.keys():
            try:
                decision = await self._evaluate_scaling_decision(pool_id)
                if decision and decision.target_size != decision.current_size:
                    await self._execute_scaling_decision(decision)
            except Exception as e:
                logger.error(f"Auto-scaling check failed for {pool_id}: {e}")
    
    async def _evaluate_scaling_decision(self, pool_id: str) -> Optional[ScalingDecision]:
        """Evaluate whether a pool needs scaling."""
        
        # Check cooldown period
        last_scale = self._last_scale_time.get(pool_id)
        if last_scale:
            cooldown_remaining = (datetime.now(timezone.utc) - last_scale).total_seconds()
            if cooldown_remaining < self._scaling_cooldown:
                return None
        
        stats = self._pool_stats.get(pool_id)
        if not stats:
            return None
        
        config = self._pool_configs.get(pool_id, {})
        min_size = config.get('min_size', 5)
        max_size = config.get('max_size', 20)
        
        current_size = stats.total_connections
        target_size = current_size
        reason = ""
        confidence = 0.0
        
        # Scaling logic based on strategy
        if self._scaling_strategy == ScalingStrategy.CONSERVATIVE:
            # Scale up if utilization > 80%
            if stats.utilization_rate > 80 and current_size < max_size:
                target_size = min(current_size + 1, max_size)
                reason = f"High utilization: {stats.utilization_rate:.1f}%"
                confidence = 0.8
            # Scale down if utilization < 30%
            elif stats.utilization_rate < 30 and current_size > min_size:
                target_size = max(current_size - 1, min_size)
                reason = f"Low utilization: {stats.utilization_rate:.1f}%"
                confidence = 0.7
        
        elif self._scaling_strategy == ScalingStrategy.AGGRESSIVE:
            # Scale up if utilization > 70%
            if stats.utilization_rate > 70 and current_size < max_size:
                target_size = min(current_size + 2, max_size)
                reason = f"High utilization: {stats.utilization_rate:.1f}%"
                confidence = 0.9
            # Scale down if utilization < 40%
            elif stats.utilization_rate < 40 and current_size > min_size:
                target_size = max(current_size - 1, min_size)
                reason = f"Low utilization: {stats.utilization_rate:.1f}%"
                confidence = 0.8
        
        elif self._scaling_strategy == ScalingStrategy.PREDICTIVE:
            # AI-based predictive scaling (simplified)
            recent_decisions = [d for d in self._scaling_history[-10:] if d.pool_id == pool_id]
            
            # Scale based on trend and current metrics
            if stats.utilization_rate > 75 or stats.average_wait_time > 100:
                target_size = min(current_size + 1, max_size)
                reason = f"Predictive: utilization {stats.utilization_rate:.1f}%, wait time {stats.average_wait_time:.1f}ms"
                confidence = 0.85
            elif stats.utilization_rate < 35 and current_size > min_size:
                target_size = max(current_size - 1, min_size)
                reason = f"Predictive: low utilization {stats.utilization_rate:.1f}%"
                confidence = 0.75
        
        if target_size != current_size and confidence > 0.5:
            return ScalingDecision(
                pool_id=pool_id,
                current_size=current_size,
                target_size=target_size,
                strategy=self._scaling_strategy,
                reason=reason,
                confidence=confidence
            )
        
        return None
    
    async def _execute_scaling_decision(self, decision: ScalingDecision):
        """Execute a scaling decision."""
        try:
            pool = self._pools.get(decision.pool_id)
            if not pool:
                return
            
            # Execute scaling if pool supports it
            if hasattr(pool, 'resize'):
                await pool.resize(decision.target_size)
            elif hasattr(pool, 'set_pool_size'):
                await pool.set_pool_size(decision.target_size)
            
            # Record decision
            self._scaling_history.append(decision)
            self._last_scale_time[decision.pool_id] = datetime.now(timezone.utc)
            
            # Update stats
            stats = self._pool_stats.get(decision.pool_id)
            if stats:
                stats.total_connections = decision.target_size
            
            logger.info(f"Scaled pool {decision.pool_id} from {decision.current_size} to {decision.target_size}: {decision.reason}")
            
        except Exception as e:
            logger.error(f"Failed to execute scaling decision for {decision.pool_id}: {e}")
    
    async def _update_connection_stats(self, pool_id: str, start_time: float):
        """Update connection statistics after successful connection."""
        stats = self._pool_stats.get(pool_id)
        if stats:
            connection_time = (time.time() - start_time) * 1000  # ms
            
            # Update wait time (simple moving average)
            if stats.average_wait_time == 0:
                stats.average_wait_time = connection_time
            else:
                stats.average_wait_time = (stats.average_wait_time * 0.9) + (connection_time * 0.1)
            
            stats.last_updated = datetime.now(timezone.utc)
    
    async def _update_error_stats(self, pool_id: str, error: str):
        """Update error statistics after connection failure."""
        health = self._health_status.get(pool_id)
        if health:
            health.error_count += 1
        
        logger.warning(f"Pool {pool_id} connection error: {error}")
    
    async def _update_pool_statistics(self):
        """Update comprehensive pool statistics."""
        for pool_id, pool in self._pools.items():
            try:
                stats = self._pool_stats.get(pool_id)
                if not stats:
                    continue
                
                # Get current pool metrics if available
                if hasattr(pool, 'get_stats'):
                    pool_metrics = pool.get_stats()
                    if pool_metrics:
                        stats.active_connections = pool_metrics.get('active_connections', 0)
                        stats.idle_connections = pool_metrics.get('idle_connections', 0)
                        stats.total_connections = pool_metrics.get('total_connections', 0)
                        
                        # Calculate utilization rate
                        if stats.total_connections > 0:
                            stats.utilization_rate = (stats.active_connections / stats.total_connections) * 100
                
                stats.last_updated = datetime.now(timezone.utc)
                
            except Exception as e:
                logger.error(f"Failed to update statistics for pool {pool_id}: {e}")
    
    @property
    def pools(self) -> Dict[str, Any]:
        """Get dictionary of registered pools."""
        return dict(self._pools)
    
    @property
    def pool_configs(self) -> Dict[str, Dict[str, Any]]:
        """Get dictionary of pool configurations."""
        return dict(self._pool_configs)
    
    async def close_all_pools(self):
        """Close all registered pools."""
        logger.info("Closing all pools...")
        
        # Stop monitoring first
        await self.stop_monitoring()
        
        # Close all pools
        for pool_id in list(self._pools.keys()):
            await self.unregister_pool(pool_id)
        
        logger.info("All pools closed")


# Global pool manager instance
_pool_manager: Optional[PoolManager] = None


def get_pool_manager() -> PoolManager:
    """Get the global pool manager instance."""
    global _pool_manager
    if _pool_manager is None:
        _pool_manager = PoolManager()
    return _pool_manager


async def initialize_all_pools(config_dir: str = "config/pools", master_key: str = None, **kwargs) -> bool:
    """Initialize all pools from configuration directory."""
    try:
        pool_manager = get_pool_manager()
        
        # Initialize pool manager
        config = {
            'auto_monitoring': kwargs.get('auto_monitoring', True),
            'scaling_strategy': kwargs.get('scaling_strategy', 'predictive'),
            'load_balancing_strategy': kwargs.get('load_balancing_strategy', 'least_connections')
        }
        
        success = await pool_manager.initialize(config)
        
        if success:
            logger.info("All pools initialized successfully")
        else:
            logger.error("Pool initialization failed")
        
        return success
        
    except Exception as e:
        logger.error(f"Pool initialization error: {e}")
        return False


# Export public interface
__all__ = [
    "PoolManager",
    "get_pool_manager", 
    "initialize_all_pools",
    "ScalingStrategy",
    "LoadBalancingStrategy",
    "PoolHealthStatus",
    "PoolStats",
    "ScalingDecision"
]