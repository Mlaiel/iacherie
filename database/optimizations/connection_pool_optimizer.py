"""Enhanced Connection Pool Optimization Module

Advanced connection pool optimization with adaptive sizing, load balancing,
circuit breakers, and intelligent resource management.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""
import asyncio
import time
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Tuple, Any, Union
from enum import Enum
from dataclasses import dataclass, field
from collections import defaultdict, deque
import logging
import threading

from .manager import DatabasePoolManager, PoolConfig, DatabaseConnectionInfo, DatabaseType
from ...core.logging import get_logger

logger = get_logger(__name__)


class LoadBalancingStrategy(Enum):
    """Load balancing strategies"""
    ROUND_ROBIN = "round_robin"
    LEAST_CONNECTIONS = "least_connections"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    RESPONSE_TIME = "response_time"
    ADAPTIVE = "adaptive"


class CircuitBreakerState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


@dataclass
class ConnectionMetrics:
    """Connection performance metrics"""
    connection_count: int = 0
    active_connections: int = 0
    avg_response_time: float = 0.0
    error_rate: float = 0.0
    throughput: float = 0.0
    last_updated: datetime = field(default_factory=datetime.now)
    
    def update_response_time(self, response_time: float):
        """Update average response time"""
        if self.connection_count == 0:
            self.avg_response_time = response_time
        else:
            # Exponential moving average
            alpha = 0.1
            self.avg_response_time = alpha * response_time + (1 - alpha) * self.avg_response_time
        
        self.last_updated = datetime.now()


@dataclass
class PoolOptimizationConfig:
    """Pool optimization configuration"""
    adaptive_sizing_enabled: bool = True
    load_balancing_strategy: LoadBalancingStrategy = LoadBalancingStrategy.ADAPTIVE
    circuit_breaker_enabled: bool = True
    metrics_window_size: int = 100
    optimization_interval: int = 60  # seconds
    
    # Adaptive sizing parameters
    target_utilization: float = 0.7  # 70% target utilization
    scale_up_threshold: float = 0.85  # Scale up at 85% utilization
    scale_down_threshold: float = 0.5  # Scale down at 50% utilization
    min_scale_interval: int = 300  # Minimum 5 minutes between scaling
    
    # Circuit breaker parameters
    failure_threshold: int = 5
    recovery_timeout: int = 60
    half_open_max_calls: int = 3


class LoadBalancer:
    """Intelligent load balancer for database connections"""
    
    def __init__(self, strategy: LoadBalancingStrategy):
        self.strategy = strategy
        self.pool_weights: Dict[str, float] = {}
        self.pool_metrics: Dict[str, ConnectionMetrics] = {}
        self.round_robin_index = 0
        self._lock = asyncio.Lock()
    
    async def select_pool(self, available_pools: List[str]) -> str:
        """Select optimal pool based on strategy"""
        async with self._lock:
            if not available_pools:
                raise ValueError("No available pools")
            
            if len(available_pools) == 1:
                return available_pools[0]
            
            if self.strategy == LoadBalancingStrategy.ROUND_ROBIN:
                return self._round_robin_select(available_pools)
            elif self.strategy == LoadBalancingStrategy.LEAST_CONNECTIONS:
                return self._least_connections_select(available_pools)
            elif self.strategy == LoadBalancingStrategy.WEIGHTED_ROUND_ROBIN:
                return self._weighted_round_robin_select(available_pools)
            elif self.strategy == LoadBalancingStrategy.RESPONSE_TIME:
                return self._response_time_select(available_pools)
            elif self.strategy == LoadBalancingStrategy.ADAPTIVE:
                return self._adaptive_select(available_pools)
            else:
                return available_pools[0]
    
    def _round_robin_select(self, pools: List[str]) -> str:
        """Round-robin selection"""
        selected = pools[self.round_robin_index % len(pools)]
        self.round_robin_index += 1
        return selected
    
    def _least_connections_select(self, pools: List[str]) -> str:
        """Select pool with least active connections"""
        min_connections = float('inf')
        selected_pool = pools[0]
        
        for pool_id in pools:
            metrics = self.pool_metrics.get(pool_id, ConnectionMetrics())
            if metrics.active_connections < min_connections:
                min_connections = metrics.active_connections
                selected_pool = pool_id
        
        return selected_pool
    
    def _weighted_round_robin_select(self, pools: List[str]) -> str:
        """Weighted round-robin based on pool weights"""
        if not self.pool_weights:
            return self._round_robin_select(pools)
        
        # Calculate cumulative weights
        cumulative_weights = []
        total_weight = 0
        
        for pool_id in pools:
            weight = self.pool_weights.get(pool_id, 1.0)
            total_weight += weight
            cumulative_weights.append(total_weight)
        
        # Select based on weights
        import random
        r = random.uniform(0, total_weight)
        
        for i, weight in enumerate(cumulative_weights):
            if r <= weight:
                return pools[i]
        
        return pools[0]
    
    def _response_time_select(self, pools: List[str]) -> str:
        """Select pool with best response time"""
        best_time = float('inf')
        selected_pool = pools[0]
        
        for pool_id in pools:
            metrics = self.pool_metrics.get(pool_id, ConnectionMetrics())
            if metrics.avg_response_time < best_time:
                best_time = metrics.avg_response_time
                selected_pool = pool_id
        
        return selected_pool
    
    def _adaptive_select(self, pools: List[str]) -> str:
        """Adaptive selection based on multiple factors"""
        scores = {}
        
        for pool_id in pools:
            metrics = self.pool_metrics.get(pool_id, ConnectionMetrics())
            
            # Calculate composite score
            # Lower is better for response time and active connections
            # Higher is better for throughput
            response_score = 1.0 / max(metrics.avg_response_time, 0.001)
            connection_score = 1.0 / max(metrics.active_connections + 1, 1)
            throughput_score = metrics.throughput
            error_score = 1.0 / max(metrics.error_rate + 0.01, 0.01)
            
            # Weighted composite score
            scores[pool_id] = (
                0.3 * response_score +
                0.2 * connection_score +
                0.3 * throughput_score +
                0.2 * error_score
            )
        
        # Select pool with highest score
        return max(scores.keys(), key=lambda k: scores[k])
    
    def update_metrics(self, pool_id: str, metrics: ConnectionMetrics):
        """Update pool metrics for load balancing decisions"""
        self.pool_metrics[pool_id] = metrics
    
    def set_pool_weight(self, pool_id: str, weight: float):
        """Set weight for specific pool"""
        self.pool_weights[pool_id] = weight


class CircuitBreaker:
    """Circuit breaker for database connections"""
    
    def __init__(self, config: PoolOptimizationConfig):
        self.config = config
        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.half_open_calls = 0
        self._lock = asyncio.Lock()
    
    async def call_allowed(self) -> bool:
        """Check if call is allowed through circuit breaker"""
        async with self._lock:
            if self.state == CircuitBreakerState.CLOSED:
                return True
            elif self.state == CircuitBreakerState.OPEN:
                # Check if we should transition to half-open
                if (self.last_failure_time and 
                    datetime.now() - self.last_failure_time > timedelta(seconds=self.config.recovery_timeout)):
                    self.state = CircuitBreakerState.HALF_OPEN
                    self.half_open_calls = 0
                    return True
                return False
            elif self.state == CircuitBreakerState.HALF_OPEN:
                return self.half_open_calls < self.config.half_open_max_calls
            
            return False
    
    async def record_success(self):
        """Record successful operation"""
        async with self._lock:
            if self.state == CircuitBreakerState.HALF_OPEN:
                self.half_open_calls += 1
                if self.half_open_calls >= self.config.half_open_max_calls:
                    # Recovered - close circuit
                    self.state = CircuitBreakerState.CLOSED
                    self.failure_count = 0
                    self.half_open_calls = 0
            elif self.state == CircuitBreakerState.CLOSED:
                # Reset failure count on success
                self.failure_count = max(0, self.failure_count - 1)
    
    async def record_failure(self):
        """Record failed operation"""
        async with self._lock:
            self.failure_count += 1
            self.last_failure_time = datetime.now()
            
            if self.state == CircuitBreakerState.HALF_OPEN:
                # Failed during half-open - back to open
                self.state = CircuitBreakerState.OPEN
            elif (self.state == CircuitBreakerState.CLOSED and 
                  self.failure_count >= self.config.failure_threshold):
                # Too many failures - open circuit
                self.state = CircuitBreakerState.OPEN
    
    def get_state(self) -> Dict[str, Any]:
        """Get circuit breaker state"""
        return {
            'state': self.state.value,
            'failure_count': self.failure_count,
            'last_failure_time': self.last_failure_time.isoformat() if self.last_failure_time else None,
            'half_open_calls': self.half_open_calls
        }


class AdaptivePoolSizer:
    """Adaptive pool sizing based on workload"""
    
    def __init__(self, config: PoolOptimizationConfig):
        self.config = config
        self.utilization_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=config.metrics_window_size))
        self.last_scaling: Dict[str, datetime] = {}
    
    async def should_scale_pool(self, pool_id: str, current_metrics: ConnectionMetrics, 
                              current_size: int, max_size: int, min_size: int) -> Optional[int]:
        """Determine if pool should be scaled and return new size"""
        
        # Calculate current utilization
        utilization = current_metrics.active_connections / max(current_size, 1)
        
        # Update history
        self.utilization_history[pool_id].append({
            'timestamp': datetime.now(),
            'utilization': utilization,
            'response_time': current_metrics.avg_response_time,
            'error_rate': current_metrics.error_rate
        })
        
        # Check if enough time has passed since last scaling
        if (pool_id in self.last_scaling and 
            datetime.now() - self.last_scaling[pool_id] < timedelta(seconds=self.config.min_scale_interval)):
            return None
        
        # Analyze recent history for scaling decision
        recent_metrics = list(self.utilization_history[pool_id])[-10:]  # Last 10 data points
        
        if len(recent_metrics) < 5:
            return None  # Not enough data
        
        avg_utilization = statistics.mean(m['utilization'] for m in recent_metrics)
        avg_response_time = statistics.mean(m['response_time'] for m in recent_metrics)
        avg_error_rate = statistics.mean(m['error_rate'] for m in recent_metrics)
        
        # Scale up conditions
        if (avg_utilization > self.config.scale_up_threshold and
            current_size < max_size and
            (avg_response_time > 1.0 or avg_error_rate > 0.01)):  # Performance degradation
            
            new_size = min(max_size, int(current_size * 1.2))  # Scale up by 20%
            self.last_scaling[pool_id] = datetime.now()
            logger.info(f"Scaling up pool {pool_id}: {current_size} -> {new_size}")
            return new_size
        
        # Scale down conditions
        elif (avg_utilization < self.config.scale_down_threshold and
              current_size > min_size and
              avg_response_time < 0.5 and  # Good performance
              avg_error_rate < 0.001):  # Low error rate
            
            new_size = max(min_size, int(current_size * 0.8))  # Scale down by 20%
            self.last_scaling[pool_id] = datetime.now()
            logger.info(f"Scaling down pool {pool_id}: {current_size} -> {new_size}")
            return new_size
        
        return None


class EnhancedConnectionPoolManager:
    """Enhanced connection pool manager with optimization features"""
    
    def __init__(self, base_manager: DatabasePoolManager, config: PoolOptimizationConfig):
        self.base_manager = base_manager
        self.config = config
        
        # Optimization components
        self.load_balancer = LoadBalancer(config.load_balancing_strategy)
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.adaptive_sizer = AdaptivePoolSizer(config)
        
        # Metrics and monitoring
        self.connection_metrics: Dict[str, ConnectionMetrics] = defaultdict(ConnectionMetrics)
        self.optimization_task: Optional[asyncio.Task] = None
        self.is_optimizing = False
    
    async def start_optimization(self):
        """Start pool optimization background task"""
        if self.is_optimizing:
            return
        
        self.is_optimizing = True
        self.optimization_task = asyncio.create_task(self._optimization_loop())
        logger.info("Enhanced pool optimization started")
    
    async def stop_optimization(self):
        """Stop pool optimization"""
        self.is_optimizing = False
        
        if self.optimization_task:
            self.optimization_task.cancel()
            try:
                await self.optimization_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Enhanced pool optimization stopped")
    
    async def acquire_connection_optimized(self, pool_id: str, **kwargs) -> Any:
        """Acquire connection with optimization"""
        # Check circuit breaker
        if pool_id not in self.circuit_breakers:
            self.circuit_breakers[pool_id] = CircuitBreaker(self.config)
        
        circuit_breaker = self.circuit_breakers[pool_id]
        
        if not await circuit_breaker.call_allowed():
            raise Exception(f"Circuit breaker open for pool {pool_id}")
        
        start_time = time.time()
        
        try:
            # Get connection from base manager
            connection = await self.base_manager.acquire_connection(pool_id, **kwargs)
            
            # Record success
            response_time = time.time() - start_time
            await circuit_breaker.record_success()
            
            # Update metrics
            metrics = self.connection_metrics[pool_id]
            metrics.connection_count += 1
            metrics.active_connections += 1
            metrics.update_response_time(response_time)
            metrics.throughput = metrics.connection_count / max((datetime.now() - metrics.last_updated).total_seconds(), 1)
            
            # Update load balancer metrics
            self.load_balancer.update_metrics(pool_id, metrics)
            
            return connection
            
        except Exception as e:
            # Record failure
            await circuit_breaker.record_failure()
            
            # Update error metrics
            metrics = self.connection_metrics[pool_id]
            metrics.error_rate = min(1.0, metrics.error_rate + 0.1)
            
            raise
    
    async def release_connection_optimized(self, pool_id: str, connection: Any):
        """Release connection with metrics update"""
        try:
            await self.base_manager.release_connection(pool_id, connection)
            
            # Update metrics
            metrics = self.connection_metrics[pool_id]
            metrics.active_connections = max(0, metrics.active_connections - 1)
            
        except Exception as e:
            logger.error(f"Failed to release connection for pool {pool_id}: {e}")
            raise
    
    async def _optimization_loop(self):
        """Main optimization loop"""
        while self.is_optimizing:
            try:
                await self._optimize_all_pools()
                await asyncio.sleep(self.config.optimization_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Pool optimization error: {e}")
                await asyncio.sleep(10)
    
    async def _optimize_all_pools(self):
        """Optimize all pools"""
        for pool_id, pool in self.base_manager.pools.items():
            try:
                await self._optimize_single_pool(pool_id, pool)
            except Exception as e:
                logger.error(f"Failed to optimize pool {pool_id}: {e}")
    
    async def _optimize_single_pool(self, pool_id: str, pool):
        """Optimize a single pool"""
        # Get current pool stats
        stats = pool.get_stats()
        current_size = stats.get('pool_size', 0)
        active_connections = stats.get('active_connections', 0)
        
        # Get metrics
        metrics = self.connection_metrics[pool_id]
        
        # Adaptive sizing
        if self.config.adaptive_sizing_enabled:
            pool_config = self.base_manager.pool_configs.get(
                self._get_pool_type(pool_id), 
                PoolConfig()
            )
            
            new_size = await self.adaptive_sizer.should_scale_pool(
                pool_id, metrics, current_size, 
                pool_config.max_size, pool_config.min_size
            )
            
            if new_size is not None and new_size != current_size:
                success = await pool.resize_pool(pool_config.min_size, new_size)
                if success:
                    logger.info(f"Resized pool {pool_id} to {new_size} connections")
        
        # Pool maintenance
        await pool.execute_maintenance()
        
        # Decay error rate over time
        time_since_update = (datetime.now() - metrics.last_updated).total_seconds()
        if time_since_update > 60:  # 1 minute
            metrics.error_rate *= 0.9  # Decay by 10%
            metrics.last_updated = datetime.now()
    
    def _get_pool_type(self, pool_id: str) -> DatabaseType:
        """Get database type for pool"""
        # This would need to be implemented based on pool naming convention
        if 'postgres' in pool_id.lower():
            return DatabaseType.POSTGRESQL
        elif 'redis' in pool_id.lower():
            return DatabaseType.REDIS
        elif 'mongo' in pool_id.lower():
            return DatabaseType.MONGODB
        else:
            return DatabaseType.POSTGRESQL  # Default
    
    async def get_optimization_stats(self) -> Dict[str, Any]:
        """Get comprehensive optimization statistics"""
        stats = {
            'optimization_enabled': self.is_optimizing,
            'load_balancing_strategy': self.config.load_balancing_strategy.value,
            'circuit_breaker_states': {
                pool_id: cb.get_state() 
                for pool_id, cb in self.circuit_breakers.items()
            },
            'connection_metrics': {
                pool_id: {
                    'connection_count': m.connection_count,
                    'active_connections': m.active_connections,
                    'avg_response_time': m.avg_response_time,
                    'error_rate': m.error_rate,
                    'throughput': m.throughput
                }
                for pool_id, m in self.connection_metrics.items()
            },
            'pool_utilizations': {}
        }
        
        # Add utilization data
        for pool_id in self.adaptive_sizer.utilization_history:
            history = list(self.adaptive_sizer.utilization_history[pool_id])
            if history:
                recent = history[-10:]  # Last 10 data points
                stats['pool_utilizations'][pool_id] = {
                    'current_utilization': recent[-1]['utilization'] if recent else 0,
                    'avg_utilization': statistics.mean(m['utilization'] for m in recent),
                    'avg_response_time': statistics.mean(m['response_time'] for m in recent),
                    'trend': 'stable'  # Could implement trend analysis
                }
        
        return stats


# Export main class
__all__ = ['EnhancedConnectionPoolManager', 'PoolOptimizationConfig', 'LoadBalancingStrategy']