"""
Bulkhead Pattern Manager - Enterprise Circuit Breakers
Advanced resource isolation and compartmentalization patterns

This module implements the bulkhead pattern for resource isolation in microservices,
providing thread pool isolation, connection pool management, and resource
compartmentalization to prevent cascade failures.

Expert Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + 
            Microservices + Audio + DevOps + IA Prompt Engineer

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ PROPRIÉTÉ INTELLECTUELLE - PROTECTION FORTE
Cette implémentation est la propriété exclusive de Fahed Mlaiel.
Toute reproduction ou utilisation non autorisée est strictement interdite.
"""

import asyncio
import logging
import threading
import time
import uuid
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Callable, Union, Set
from datetime import datetime, timedelta
import psutil
import weakref
from collections import defaultdict
import json


logger = logging.getLogger(__name__)


class BulkheadType(Enum):
    """Types of bulkhead isolation patterns"""
    THREAD_POOL = "thread_pool"
    CONNECTION_POOL = "connection_pool"
    MEMORY_POOL = "memory_pool"
    CPU_POOL = "cpu_pool"
    BANDWIDTH_POOL = "bandwidth_pool"
    QUEUE_POOL = "queue_pool"
    SEMAPHORE_POOL = "semaphore_pool"


class ResourceState(Enum):
    """Resource pool states"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    OVERLOADED = "overloaded"
    ISOLATED = "isolated"
    RECOVERING = "recovering"


class IsolationStrategy(Enum):
    """Resource isolation strategies"""
    STRICT = "strict"           # No resource sharing
    ADAPTIVE = "adaptive"       # Dynamic resource allocation
    WEIGHTED = "weighted"       # Weight-based resource distribution
    ELASTIC = "elastic"         # Auto-scaling resource pools


@dataclass
class BulkheadConfig:
    """Bulkhead configuration parameters"""
    name: str
    bulkhead_type: BulkheadType
    max_resources: int = 10
    min_resources: int = 2
    reserve_resources: int = 2
    timeout_seconds: float = 30.0
    isolation_strategy: IsolationStrategy = IsolationStrategy.ADAPTIVE
    auto_scaling: bool = True
    monitoring_enabled: bool = True
    failure_threshold: int = 5
    recovery_timeout: int = 60
    health_check_interval: int = 10
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ResourceMetrics:
    """Resource utilization metrics"""
    total_resources: int = 0
    active_resources: int = 0
    available_resources: int = 0
    pending_requests: int = 0
    completed_requests: int = 0
    failed_requests: int = 0
    avg_response_time: float = 0.0
    peak_utilization: float = 0.0
    efficiency_ratio: float = 0.0
    last_updated: datetime = field(default_factory=datetime.now)


@dataclass
class BulkheadStatus:
    """Bulkhead status information"""
    bulkhead_id: str
    name: str
    state: ResourceState
    config: BulkheadConfig
    metrics: ResourceMetrics
    last_health_check: datetime = field(default_factory=datetime.now)
    isolation_reason: Optional[str] = None
    recovery_eta: Optional[datetime] = None


class ResourcePool:
    """Base resource pool implementation"""
    
    def __init__(self, config: BulkheadConfig):
        self.config = config
        self.pool_id = str(uuid.uuid4())
        self.state = ResourceState.HEALTHY
        self.metrics = ResourceMetrics()
        self.lock = asyncio.Lock()
        self.resources: Set[Any] = set()
        self.active_resources: Set[Any] = set()
        self.request_queue = asyncio.Queue()
        self.health_check_task: Optional[asyncio.Task] = None
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
    async def acquire_resource(self, timeout: Optional[float] = None) -> Any:
        """Acquire resource from pool"""
        timeout = timeout or self.config.timeout_seconds
        
        async with self.lock:
            if self.state == ResourceState.ISOLATED:
                raise RuntimeError(f"Resource pool {self.config.name} is isolated")
            
            # Try to get available resource
            available = self.resources - self.active_resources
            if available:
                resource = available.pop()
                self.active_resources.add(resource)
                self.metrics.active_resources = len(self.active_resources)
                self.metrics.available_resources = len(available)
                return resource
            
            # Check if we can create new resource
            if len(self.resources) < self.config.max_resources:
                resource = await self._create_resource()
                self.resources.add(resource)
                self.active_resources.add(resource)
                self.metrics.total_resources = len(self.resources)
                self.metrics.active_resources = len(self.active_resources)
                return resource
            
            # Wait for resource to become available
            return await self._wait_for_resource(timeout)
    
    async def release_resource(self, resource: Any, success: bool = True):
        """Release resource back to pool"""
        async with self.lock:
            if resource in self.active_resources:
                self.active_resources.remove(resource)
                self.metrics.active_resources = len(self.active_resources)
                self.metrics.available_resources = len(self.resources - self.active_resources)
                
                if success:
                    self.metrics.completed_requests += 1
                else:
                    self.metrics.failed_requests += 1
                    await self._handle_resource_failure(resource)
    
    async def _create_resource(self) -> Any:
        """Create new resource - to be implemented by subclasses"""
        raise NotImplementedError
    
    async def _wait_for_resource(self, timeout: float) -> Any:
        """Wait for resource to become available"""
        try:
            # Add request to queue
            request_future = asyncio.Future()
            await self.request_queue.put(request_future)
            self.metrics.pending_requests = self.request_queue.qsize()
            
            # Wait for resource with timeout
            resource = await asyncio.wait_for(request_future, timeout=timeout)
            return resource
            
        except asyncio.TimeoutError:
            self.logger.warning(f"Resource acquisition timeout for pool {self.config.name}")
            raise
    
    async def _handle_resource_failure(self, resource: Any):
        """Handle resource failure"""
        failure_count = getattr(resource, '_failure_count', 0) + 1
        setattr(resource, '_failure_count', failure_count)
        
        if failure_count >= self.config.failure_threshold:
            self.logger.warning(f"Resource {resource} exceeded failure threshold, removing from pool")
            self.resources.discard(resource)
            await self._cleanup_resource(resource)
    
    async def _cleanup_resource(self, resource: Any):
        """Cleanup failed resource - to be implemented by subclasses"""
        pass
    
    async def start_health_monitoring(self):
        """Start health monitoring task"""
        if not self.health_check_task:
            self.health_check_task = asyncio.create_task(self._health_monitor_loop())
    
    async def stop_health_monitoring(self):
        """Stop health monitoring task"""
        if self.health_check_task:
            self.health_check_task.cancel()
            try:
                await self.health_check_task
            except asyncio.CancelledError:
                pass
            self.health_check_task = None
    
    async def _health_monitor_loop(self):
        """Health monitoring loop"""
        while True:
            try:
                await asyncio.sleep(self.config.health_check_interval)
                await self._perform_health_check()
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Health check error for pool {self.config.name}: {e}")
    
    async def _perform_health_check(self):
        """Perform health check on resource pool"""
        async with self.lock:
            # Calculate utilization metrics
            utilization = len(self.active_resources) / len(self.resources) if self.resources else 0
            self.metrics.peak_utilization = max(self.metrics.peak_utilization, utilization)
            
            # Determine pool state based on utilization
            if utilization > 0.9:
                self.state = ResourceState.OVERLOADED
            elif utilization > 0.7:
                self.state = ResourceState.DEGRADED
            else:
                self.state = ResourceState.HEALTHY
            
            # Update metrics
            self.metrics.last_updated = datetime.now()


class ThreadPoolBulkhead(ResourcePool):
    """Thread pool bulkhead implementation"""
    
    def __init__(self, config: BulkheadConfig):
        super().__init__(config)
        self.executor: Optional[ThreadPoolExecutor] = None
        
    async def _create_resource(self) -> ThreadPoolExecutor:
        """Create thread pool executor"""
        if not self.executor:
            self.executor = ThreadPoolExecutor(
                max_workers=self.config.max_resources,
                thread_name_prefix=f"bulkhead-{self.config.name}"
            )
        return self.executor
    
    async def execute_task(self, func: Callable, *args, **kwargs) -> Any:
        """Execute task in thread pool"""
        executor = await self.acquire_resource()
        try:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(executor, func, *args, **kwargs)
            await self.release_resource(executor, success=True)
            return result
        except Exception as e:
            await self.release_resource(executor, success=False)
            raise e
    
    async def _cleanup_resource(self, resource: ThreadPoolExecutor):
        """Cleanup thread pool"""
        if resource:
            resource.shutdown(wait=False)


class ConnectionPoolBulkhead(ResourcePool):
    """Connection pool bulkhead implementation"""
    
    def __init__(self, config: BulkheadConfig, connection_factory: Callable):
        super().__init__(config)
        self.connection_factory = connection_factory
        self.connections: Set[Any] = set()
    
    async def _create_resource(self) -> Any:
        """Create new connection"""
        connection = await self.connection_factory()
        return connection
    
    async def _cleanup_resource(self, resource: Any):
        """Cleanup connection"""
        try:
            if hasattr(resource, 'close'):
                await resource.close()
            elif hasattr(resource, 'disconnect'):
                await resource.disconnect()
        except Exception as e:
            self.logger.warning(f"Error closing connection: {e}")


class MemoryPoolBulkhead(ResourcePool):
    """Memory pool bulkhead implementation"""
    
    def __init__(self, config: BulkheadConfig):
        super().__init__(config)
        self.memory_limit_bytes = config.metadata.get('memory_limit_mb', 100) * 1024 * 1024
        self.allocated_memory = 0
        self.memory_blocks: Dict[str, bytes] = {}
    
    async def allocate_memory(self, size_bytes: int) -> str:
        """Allocate memory block"""
        async with self.lock:
            if self.allocated_memory + size_bytes > self.memory_limit_bytes:
                raise MemoryError("Memory pool exhausted")
            
            block_id = str(uuid.uuid4())
            self.memory_blocks[block_id] = bytearray(size_bytes)
            self.allocated_memory += size_bytes
            return block_id
    
    async def deallocate_memory(self, block_id: str):
        """Deallocate memory block"""
        async with self.lock:
            if block_id in self.memory_blocks:
                size = len(self.memory_blocks[block_id])
                del self.memory_blocks[block_id]
                self.allocated_memory -= size


class BulkheadPatternManager:
    """
    Enterprise bulkhead pattern manager for resource isolation.
    Implements multiple isolation strategies with monitoring and auto-scaling.
    """
    
    def __init__(self):
        """Initialize bulkhead pattern manager"""
        self.bulkheads: Dict[str, ResourcePool] = {}
        self.configurations: Dict[str, BulkheadConfig] = {}
        self.metrics_history: Dict[str, List[ResourceMetrics]] = defaultdict(list)
        self.isolation_rules: Dict[str, Dict[str, Any]] = {}
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.monitoring_task: Optional[asyncio.Task] = None
        self._shutdown_event = asyncio.Event()
        
        self.logger.info("🛡️ Bulkhead Pattern Manager initialized - Enterprise isolation ready")
    
    async def create_resource_bulkhead(self, resource_type: str, config: BulkheadConfig) -> str:
        """Create bulkhead for resource isolation"""
        try:
            bulkhead_id = f"{resource_type}_{config.name}_{uuid.uuid4().hex[:8]}"
            
            # Create appropriate bulkhead based on type
            if config.bulkhead_type == BulkheadType.THREAD_POOL:
                bulkhead = ThreadPoolBulkhead(config)
            elif config.bulkhead_type == BulkheadType.CONNECTION_POOL:
                connection_factory = config.metadata.get('connection_factory')
                if not connection_factory:
                    raise ValueError("Connection factory required for connection pool bulkhead")
                bulkhead = ConnectionPoolBulkhead(config, connection_factory)
            elif config.bulkhead_type == BulkheadType.MEMORY_POOL:
                bulkhead = MemoryPoolBulkhead(config)
            else:
                bulkhead = ResourcePool(config)
            
            # Register bulkhead
            self.bulkheads[bulkhead_id] = bulkhead
            self.configurations[bulkhead_id] = config
            
            # Start health monitoring
            if config.monitoring_enabled:
                await bulkhead.start_health_monitoring()
            
            self.logger.info(f"✅ Created {config.bulkhead_type.value} bulkhead: {bulkhead_id}")
            return bulkhead_id
            
        except Exception as e:
            self.logger.error(f"❌ Failed to create bulkhead {resource_type}: {e}")
            raise
    
    async def manage_thread_pool_isolation(self, pool_configs: Dict[str, Dict]) -> Dict[str, str]:
        """Manage thread pool isolation per service"""
        results = {}
        
        try:
            for service_name, pool_config in pool_configs.items():
                config = BulkheadConfig(
                    name=f"{service_name}_thread_pool",
                    bulkhead_type=BulkheadType.THREAD_POOL,
                    max_resources=pool_config.get('max_threads', 10),
                    min_resources=pool_config.get('min_threads', 2),
                    timeout_seconds=pool_config.get('timeout', 30.0),
                    isolation_strategy=IsolationStrategy[pool_config.get('strategy', 'ADAPTIVE')],
                    metadata=pool_config.get('metadata', {})
                )
                
                bulkhead_id = await self.create_resource_bulkhead("thread_pool", config)
                results[service_name] = bulkhead_id
                
                self.logger.info(f"🧵 Thread pool isolation configured for {service_name}: {bulkhead_id}")
            
            return results
            
        except Exception as e:
            self.logger.error(f"❌ Failed to manage thread pool isolation: {e}")
            raise
    
    async def monitor_resource_utilization(self, bulkhead_id: str) -> Dict[str, Any]:
        """Monitor resource utilization for bulkhead"""
        try:
            if bulkhead_id not in self.bulkheads:
                raise ValueError(f"Bulkhead {bulkhead_id} not found")
            
            bulkhead = self.bulkheads[bulkhead_id]
            config = self.configurations[bulkhead_id]
            
            # Get current metrics
            metrics = bulkhead.metrics
            
            # Calculate additional metrics
            system_metrics = await self._get_system_metrics()
            
            utilization_data = {
                'bulkhead_id': bulkhead_id,
                'bulkhead_name': config.name,
                'bulkhead_type': config.bulkhead_type.value,
                'state': bulkhead.state.value,
                'metrics': {
                    'total_resources': metrics.total_resources,
                    'active_resources': metrics.active_resources,
                    'available_resources': metrics.available_resources,
                    'pending_requests': metrics.pending_requests,
                    'completed_requests': metrics.completed_requests,
                    'failed_requests': metrics.failed_requests,
                    'utilization_ratio': metrics.active_resources / max(metrics.total_resources, 1),
                    'efficiency_ratio': metrics.efficiency_ratio,
                    'avg_response_time': metrics.avg_response_time,
                    'peak_utilization': metrics.peak_utilization
                },
                'system_metrics': system_metrics,
                'timestamp': datetime.now().isoformat()
            }
            
            # Store metrics history
            self.metrics_history[bulkhead_id].append(metrics)
            
            # Keep only last 100 entries
            if len(self.metrics_history[bulkhead_id]) > 100:
                self.metrics_history[bulkhead_id] = self.metrics_history[bulkhead_id][-100:]
            
            return utilization_data
            
        except Exception as e:
            self.logger.error(f"❌ Failed to monitor resource utilization: {e}")
            raise
    
    async def _get_system_metrics(self) -> Dict[str, float]:
        """Get system-wide resource metrics"""
        try:
            return {
                'cpu_usage': psutil.cpu_percent(interval=1),
                'memory_usage': psutil.virtual_memory().percent,
                'disk_usage': psutil.disk_usage('/').percent,
                'network_connections': len(psutil.net_connections()),
                'process_count': len(psutil.pids())
            }
        except Exception as e:
            self.logger.warning(f"⚠️ Failed to get system metrics: {e}")
            return {}
    
    async def configure_isolation_strategy(self, bulkhead_id: str, strategy: IsolationStrategy, 
                                         params: Dict[str, Any]) -> bool:
        """Configure isolation strategy for bulkhead"""
        try:
            if bulkhead_id not in self.bulkheads:
                raise ValueError(f"Bulkhead {bulkhead_id} not found")
            
            config = self.configurations[bulkhead_id]
            config.isolation_strategy = strategy
            config.metadata.update(params)
            
            # Apply strategy-specific configuration
            if strategy == IsolationStrategy.STRICT:
                await self._apply_strict_isolation(bulkhead_id, params)
            elif strategy == IsolationStrategy.ADAPTIVE:
                await self._apply_adaptive_isolation(bulkhead_id, params)
            elif strategy == IsolationStrategy.WEIGHTED:
                await self._apply_weighted_isolation(bulkhead_id, params)
            elif strategy == IsolationStrategy.ELASTIC:
                await self._apply_elastic_isolation(bulkhead_id, params)
            
            self.logger.info(f"🔧 Configured {strategy.value} isolation for {bulkhead_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to configure isolation strategy: {e}")
            return False
    
    async def _apply_strict_isolation(self, bulkhead_id: str, params: Dict[str, Any]):
        """Apply strict isolation strategy"""
        config = self.configurations[bulkhead_id]
        bulkhead = self.bulkheads[bulkhead_id]
        
        # Disable resource sharing
        config.max_resources = params.get('dedicated_resources', config.max_resources)
        config.min_resources = config.max_resources
        config.auto_scaling = False
        
        self.logger.info(f"🔒 Applied strict isolation: {config.max_resources} dedicated resources")
    
    async def _apply_adaptive_isolation(self, bulkhead_id: str, params: Dict[str, Any]):
        """Apply adaptive isolation strategy"""
        config = self.configurations[bulkhead_id]
        
        # Enable dynamic resource allocation
        config.auto_scaling = True
        adaptation_factor = params.get('adaptation_factor', 1.5)
        config.metadata['adaptation_factor'] = adaptation_factor
        
        self.logger.info(f"🔄 Applied adaptive isolation with factor {adaptation_factor}")
    
    async def _apply_weighted_isolation(self, bulkhead_id: str, params: Dict[str, Any]):
        """Apply weighted isolation strategy"""
        weight = params.get('weight', 1.0)
        priority = params.get('priority', 'normal')
        
        config = self.configurations[bulkhead_id]
        config.metadata['weight'] = weight
        config.metadata['priority'] = priority
        
        self.logger.info(f"⚖️ Applied weighted isolation: weight={weight}, priority={priority}")
    
    async def _apply_elastic_isolation(self, bulkhead_id: str, params: Dict[str, Any]):
        """Apply elastic isolation strategy"""
        config = self.configurations[bulkhead_id]
        
        # Configure auto-scaling parameters
        config.auto_scaling = True
        config.metadata.update({
            'scale_up_threshold': params.get('scale_up_threshold', 0.8),
            'scale_down_threshold': params.get('scale_down_threshold', 0.3),
            'scale_factor': params.get('scale_factor', 2.0),
            'max_scale_limit': params.get('max_scale_limit', config.max_resources * 3)
        })
        
        self.logger.info(f"🏗️ Applied elastic isolation with auto-scaling")
    
    async def get_bulkhead_status(self, bulkhead_id: str) -> BulkheadStatus:
        """Get comprehensive bulkhead status"""
        if bulkhead_id not in self.bulkheads:
            raise ValueError(f"Bulkhead {bulkhead_id} not found")
        
        bulkhead = self.bulkheads[bulkhead_id]
        config = self.configurations[bulkhead_id]
        
        return BulkheadStatus(
            bulkhead_id=bulkhead_id,
            name=config.name,
            state=bulkhead.state,
            config=config,
            metrics=bulkhead.metrics,
            last_health_check=datetime.now()
        )
    
    async def isolate_bulkhead(self, bulkhead_id: str, reason: str = "Manual isolation"):
        """Manually isolate bulkhead"""
        if bulkhead_id not in self.bulkheads:
            raise ValueError(f"Bulkhead {bulkhead_id} not found")
        
        bulkhead = self.bulkheads[bulkhead_id]
        bulkhead.state = ResourceState.ISOLATED
        
        self.isolation_rules[bulkhead_id] = {
            'reason': reason,
            'timestamp': datetime.now().isoformat(),
            'auto_recovery': False
        }
        
        self.logger.warning(f"🚫 Bulkhead {bulkhead_id} isolated: {reason}")
    
    async def recover_bulkhead(self, bulkhead_id: str):
        """Recover isolated bulkhead"""
        if bulkhead_id not in self.bulkheads:
            raise ValueError(f"Bulkhead {bulkhead_id} not found")
        
        bulkhead = self.bulkheads[bulkhead_id]
        bulkhead.state = ResourceState.RECOVERING
        
        # Perform recovery health check
        await bulkhead._perform_health_check()
        
        if bulkhead_id in self.isolation_rules:
            del self.isolation_rules[bulkhead_id]
        
        self.logger.info(f"🔄 Bulkhead {bulkhead_id} recovery initiated")
    
    async def start_monitoring(self):
        """Start global monitoring"""
        if not self.monitoring_task:
            self.monitoring_task = asyncio.create_task(self._monitoring_loop())
            self.logger.info("📊 Started bulkhead monitoring")
    
    async def stop_monitoring(self):
        """Stop global monitoring"""
        if self.monitoring_task:
            self._shutdown_event.set()
            await self.monitoring_task
            self.monitoring_task = None
            self.logger.info("⏹️ Stopped bulkhead monitoring")
    
    async def _monitoring_loop(self):
        """Global monitoring loop"""
        while not self._shutdown_event.is_set():
            try:
                await asyncio.sleep(30)  # Monitor every 30 seconds
                
                for bulkhead_id in list(self.bulkheads.keys()):
                    try:
                        await self.monitor_resource_utilization(bulkhead_id)
                        await self._check_auto_scaling(bulkhead_id)
                    except Exception as e:
                        self.logger.error(f"❌ Monitoring error for {bulkhead_id}: {e}")
                        
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"❌ Global monitoring error: {e}")
    
    async def _check_auto_scaling(self, bulkhead_id: str):
        """Check and apply auto-scaling if needed"""
        config = self.configurations[bulkhead_id]
        if not config.auto_scaling:
            return
        
        bulkhead = self.bulkheads[bulkhead_id]
        metrics = bulkhead.metrics
        
        if metrics.total_resources == 0:
            return
        
        utilization = metrics.active_resources / metrics.total_resources
        
        # Scale up if needed
        scale_up_threshold = config.metadata.get('scale_up_threshold', 0.8)
        if utilization > scale_up_threshold and metrics.total_resources < config.max_resources:
            new_capacity = min(
                int(metrics.total_resources * config.metadata.get('scale_factor', 1.5)),
                config.max_resources
            )
            await self._scale_bulkhead(bulkhead_id, new_capacity)
            self.logger.info(f"📈 Scaled up {bulkhead_id} to {new_capacity} resources")
        
        # Scale down if needed
        scale_down_threshold = config.metadata.get('scale_down_threshold', 0.3)
        if utilization < scale_down_threshold and metrics.total_resources > config.min_resources:
            new_capacity = max(
                int(metrics.total_resources / config.metadata.get('scale_factor', 1.5)),
                config.min_resources
            )
            await self._scale_bulkhead(bulkhead_id, new_capacity)
            self.logger.info(f"📉 Scaled down {bulkhead_id} to {new_capacity} resources")
    
    async def _scale_bulkhead(self, bulkhead_id: str, new_capacity: int):
        """Scale bulkhead to new capacity"""
        # Implementation depends on bulkhead type
        # This is a placeholder for the scaling logic
        config = self.configurations[bulkhead_id]
        config.max_resources = new_capacity
        
        # Update actual resource pool based on type
        bulkhead = self.bulkheads[bulkhead_id]
        if isinstance(bulkhead, ThreadPoolBulkhead) and bulkhead.executor:
            # For thread pools, we need to recreate the executor
            # This is a simplified approach - in production, you'd want more sophisticated scaling
            pass
    
    async def cleanup(self):
        """Cleanup all bulkheads and resources"""
        try:
            await self.stop_monitoring()
            
            for bulkhead_id, bulkhead in self.bulkheads.items():
                try:
                    await bulkhead.stop_health_monitoring()
                    if isinstance(bulkhead, ThreadPoolBulkhead) and bulkhead.executor:
                        bulkhead.executor.shutdown(wait=True)
                except Exception as e:
                    self.logger.error(f"❌ Error cleaning up bulkhead {bulkhead_id}: {e}")
            
            self.bulkheads.clear()
            self.configurations.clear()
            self.metrics_history.clear()
            
            self.logger.info("🧹 Bulkhead Pattern Manager cleaned up")
            
        except Exception as e:
            self.logger.error(f"❌ Cleanup error: {e}")


# Global bulkhead pattern manager instance
bulkhead_manager = BulkheadPatternManager()


# Export main classes and functions
__all__ = [
    'BulkheadPatternManager',
    'BulkheadConfig',
    'BulkheadType',
    'ResourceState',
    'IsolationStrategy',
    'BulkheadStatus',
    'ResourceMetrics',
    'ResourcePool',
    'ThreadPoolBulkhead',
    'ConnectionPoolBulkhead',
    'MemoryPoolBulkhead',
    'bulkhead_manager'
]


if __name__ == "__main__":
    async def demo():
        """Demo bulkhead pattern manager functionality"""
        manager = BulkheadPatternManager()
        
        # Create thread pool bulkhead
        config = BulkheadConfig(
            name="demo_service",
            bulkhead_type=BulkheadType.THREAD_POOL,
            max_resources=5,
            min_resources=2
        )
        
        bulkhead_id = await manager.create_resource_bulkhead("demo", config)
        
        # Monitor utilization
        status = await manager.monitor_resource_utilization(bulkhead_id)
        print(f"Bulkhead status: {json.dumps(status, indent=2, default=str)}")
        
        # Cleanup
        await manager.cleanup()
    
    # Run demo
    asyncio.run(demo())