"""Bulkhead Manager Service - Service isolation and resource management
Enterprise-grade bulkhead pattern implementation for the Ainflue AI platform.

This service implements the bulkhead pattern to provide service isolation,
resource management, and prevent cascading failures across microservices.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from enum import Enum
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import resource
import psutil
import json
from pathlib import Path


class ResourceType(Enum):
    """Resource types for bulkhead isolation."""
    CPU = "cpu"
    MEMORY = "memory"
    IO = "io"
    NETWORK = "network"
    DATABASE = "database"
    CACHE = "cache"


class BulkheadState(Enum):
    """Bulkhead partition states."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    ISOLATED = "isolated"
    FAILED = "failed"


@dataclass
class ResourceLimits:
    """Resource limits for a bulkhead partition."""
    max_cpu_percent: float = 80.0
    max_memory_mb: int = 1024
    max_concurrent_requests: int = 100
    max_io_operations: int = 1000
    max_network_connections: int = 50
    max_db_connections: int = 10


@dataclass
class BulkheadPartition:
    """Represents a bulkhead partition with resource isolation."""
    name: str
    services: Set[str] = field(default_factory=set)
    resource_limits: ResourceLimits = field(default_factory=ResourceLimits)
    current_usage: Dict[ResourceType, float] = field(default_factory=dict)
    state: BulkheadState = BulkheadState.HEALTHY
    active_requests: int = 0
    total_requests: int = 0
    failed_requests: int = 0
    created_at: float = field(default_factory=time.time)
    last_health_check: float = field(default_factory=time.time)
    executor: Optional[ThreadPoolExecutor] = None
    
    def __post_init__(self):
        """Initialize partition with thread executor."""
        self.executor = ThreadPoolExecutor(
            max_workers=self.resource_limits.max_concurrent_requests,
            thread_name_prefix=f"bulkhead-{self.name}"
        )


class BulkheadManager:
    """Enterprise bulkhead manager for service isolation and resource management."""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the bulkhead manager.
        
        Args:
            config_path: Optional path to configuration file
        """
        self.logger = logging.getLogger(__name__)
        self.partitions: Dict[str, BulkheadPartition] = {}
        self.service_to_partition: Dict[str, str] = {}
        self.monitoring_enabled = True
        self.health_check_interval = 30.0  # seconds
        self._monitoring_task: Optional[asyncio.Task] = None
        self._lock = threading.RLock()
        
        # Performance metrics
        self.metrics = {
            'total_partitions': 0,
            'healthy_partitions': 0,
            'degraded_partitions': 0,
            'isolated_partitions': 0,
            'failed_partitions': 0,
            'total_requests_processed': 0,
            'total_requests_rejected': 0,
            'average_response_time': 0.0,
            'resource_violations': 0
        }
        
        # Load configuration if provided
        if config_path:
            self._load_configuration(config_path)
        
        # Create default partitions
        self._create_default_partitions()
        
        self.logger.info("BulkheadManager initialized successfully")
    
    def _create_default_partitions(self) -> None:
        """Create default bulkhead partitions for standard services."""
        default_partitions = {
            'critical': {
                'services': ['auth', 'security', 'health_check'],
                'limits': ResourceLimits(
                    max_cpu_percent=90.0,
                    max_memory_mb=2048,
                    max_concurrent_requests=200
                )
            },
            'ai_processing': {
                'services': ['ai_inference', 'ai_orchestration', 'content_processing'],
                'limits': ResourceLimits(
                    max_cpu_percent=85.0,
                    max_memory_mb=4096,
                    max_concurrent_requests=50
                )
            },
            'content': {
                'services': ['content_upload', 'fingerprinting', 'copyright_protection'],
                'limits': ResourceLimits(
                    max_cpu_percent=70.0,
                    max_memory_mb=2048,
                    max_concurrent_requests=100
                )
            },
            'analytics': {
                'services': ['analytics_orchestration', 'real_time_analytics', 'creator_analytics'],
                'limits': ResourceLimits(
                    max_cpu_percent=60.0,
                    max_memory_mb=1536,
                    max_concurrent_requests=75
                )
            },
            'business': {
                'services': ['creator_onboarding', 'collaboration_matching', 'revenue_optimization'],
                'limits': ResourceLimits(
                    max_cpu_percent=50.0,
                    max_memory_mb=1024,
                    max_concurrent_requests=150
                )
            }
        }
        
        for partition_name, config in default_partitions.items():
            partition = BulkheadPartition(
                name=partition_name,
                services=set(config['services']),
                resource_limits=config['limits']
            )
            self.partitions[partition_name] = partition
            
            # Map services to partitions
            for service in config['services']:
                self.service_to_partition[service] = partition_name
        
        self.logger.info(f"Created {len(default_partitions)} default bulkhead partitions")
    
    def create_partition(self, name: str, services: List[str], 
                        resource_limits: Optional[ResourceLimits] = None) -> bool:
        """Create a new bulkhead partition.
        
        Args:
            name: Partition name
            services: List of service names to include
            resource_limits: Optional resource limits
            
        Returns:
            True if partition created successfully
        """
        try:
            with self._lock:
                if name in self.partitions:
                    self.logger.warning(f"Partition {name} already exists")
                    return False
                
                # Create partition
                partition = BulkheadPartition(
                    name=name,
                    services=set(services),
                    resource_limits=resource_limits or ResourceLimits()
                )
                
                self.partitions[name] = partition
                
                # Update service mappings
                for service in services:
                    if service in self.service_to_partition:
                        old_partition = self.service_to_partition[service]
                        self.logger.warning(f"Service {service} moved from {old_partition} to {name}")
                    self.service_to_partition[service] = name
                
                self.metrics['total_partitions'] = len(self.partitions)
                self.logger.info(f"Created bulkhead partition: {name} with {len(services)} services")
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to create partition {name}: {e}")
            return False
    
    def add_service_to_partition(self, service_name: str, partition_name: str) -> bool:
        """Add a service to an existing partition.
        
        Args:
            service_name: Name of the service
            partition_name: Name of the partition
            
        Returns:
            True if service added successfully
        """
        try:
            with self._lock:
                if partition_name not in self.partitions:
                    self.logger.error(f"Partition {partition_name} does not exist")
                    return False
                
                # Remove from old partition if exists
                if service_name in self.service_to_partition:
                    old_partition_name = self.service_to_partition[service_name]
                    old_partition = self.partitions[old_partition_name]
                    old_partition.services.discard(service_name)
                
                # Add to new partition
                partition = self.partitions[partition_name]
                partition.services.add(service_name)
                self.service_to_partition[service_name] = partition_name
                
                self.logger.info(f"Added service {service_name} to partition {partition_name}")
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to add service {service_name} to partition {partition_name}: {e}")
            return False
    
    async def execute_in_partition(self, service_name: str, func, *args, **kwargs) -> Any:
        """Execute a function within the appropriate bulkhead partition.
        
        Args:
            service_name: Name of the service
            func: Function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Function result or raises exception
        """
        partition_name = self.service_to_partition.get(service_name, 'default')
        
        if partition_name not in self.partitions:
            # Create default partition if not exists
            self.create_partition('default', [service_name])
            partition_name = 'default'
        
        partition = self.partitions[partition_name]
        
        # Check if partition can accept new requests
        if not self._can_accept_request(partition):
            self.metrics['total_requests_rejected'] += 1
            raise Exception(f"Partition {partition_name} is overloaded or isolated")
        
        start_time = time.time()
        
        try:
            # Increment active requests
            partition.active_requests += 1
            partition.total_requests += 1
            
            # Execute function in partition's thread pool
            loop = asyncio.get_event_loop()
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = await loop.run_in_executor(partition.executor, func, *args, **kwargs)
            
            # Update metrics
            response_time = time.time() - start_time
            self._update_response_time_metric(response_time)
            self.metrics['total_requests_processed'] += 1
            
            return result
            
        except Exception as e:
            partition.failed_requests += 1
            self.logger.error(f"Error executing function in partition {partition_name}: {e}")
            raise
        finally:
            partition.active_requests -= 1
    
    def _can_accept_request(self, partition: BulkheadPartition) -> bool:
        """Check if partition can accept a new request.
        
        Args:
            partition: Bulkhead partition to check
            
        Returns:
            True if partition can accept request
        """
        # Check state
        if partition.state in [BulkheadState.ISOLATED, BulkheadState.FAILED]:
            return False
        
        # Check concurrent requests limit
        if partition.active_requests >= partition.resource_limits.max_concurrent_requests:
            return False
        
        # Check resource usage
        if self._is_resource_overloaded(partition):
            return False
        
        return True
    
    def _is_resource_overloaded(self, partition: BulkheadPartition) -> bool:
        """Check if partition resources are overloaded.
        
        Args:
            partition: Partition to check
            
        Returns:
            True if resources are overloaded
        """
        try:
            # Check CPU usage
            cpu_percent = psutil.cpu_percent(interval=0.1)
            if cpu_percent > partition.resource_limits.max_cpu_percent:
                return True
            
            # Check memory usage
            memory_info = psutil.virtual_memory()
            memory_mb = memory_info.used / (1024 * 1024)
            if memory_mb > partition.resource_limits.max_memory_mb:
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error checking resource usage: {e}")
            return True  # Fail safe
    
    async def isolate_partition(self, partition_name: str, reason: str = "Manual isolation") -> bool:
        """Isolate a partition from receiving new requests.
        
        Args:
            partition_name: Name of partition to isolate
            reason: Reason for isolation
            
        Returns:
            True if partition isolated successfully
        """
        try:
            if partition_name not in self.partitions:
                self.logger.error(f"Partition {partition_name} does not exist")
                return False
            
            partition = self.partitions[partition_name]
            partition.state = BulkheadState.ISOLATED
            
            self.logger.warning(f"Isolated partition {partition_name}: {reason}")
            self._update_partition_metrics()
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to isolate partition {partition_name}: {e}")
            return False
    
    async def restore_partition(self, partition_name: str) -> bool:
        """Restore an isolated partition to healthy state.
        
        Args:
            partition_name: Name of partition to restore
            
        Returns:
            True if partition restored successfully
        """
        try:
            if partition_name not in self.partitions:
                self.logger.error(f"Partition {partition_name} does not exist")
                return False
            
            partition = self.partitions[partition_name]
            
            # Check if partition can be restored
            if not self._can_restore_partition(partition):
                self.logger.warning(f"Partition {partition_name} cannot be restored yet")
                return False
            
            partition.state = BulkheadState.HEALTHY
            
            self.logger.info(f"Restored partition {partition_name} to healthy state")
            self._update_partition_metrics()
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to restore partition {partition_name}: {e}")
            return False
    
    def _can_restore_partition(self, partition: BulkheadPartition) -> bool:
        """Check if partition can be restored.
        
        Args:
            partition: Partition to check
            
        Returns:
            True if partition can be restored
        """
        # Check resource usage
        if self._is_resource_overloaded(partition):
            return False
        
        # Check active requests
        if partition.active_requests > 0:
            return False
        
        # Check failure rate
        if partition.total_requests > 0:
            failure_rate = partition.failed_requests / partition.total_requests
            if failure_rate > 0.1:  # 10% failure rate threshold
                return False
        
        return True
    
    async def start_monitoring(self) -> None:
        """Start the partition monitoring task."""
        if self._monitoring_task is None:
            self._monitoring_task = asyncio.create_task(self._monitor_partitions())
            self.logger.info("Started bulkhead partition monitoring")
    
    async def stop_monitoring(self) -> None:
        """Stop the partition monitoring task."""
        if self._monitoring_task:
            self._monitoring_task.cancel()
            try:
                await self._monitoring_task
            except asyncio.CancelledError:
                pass
            self._monitoring_task = None
            self.logger.info("Stopped bulkhead partition monitoring")
    
    async def _monitor_partitions(self) -> None:
        """Monitor partition health and resource usage."""
        while self.monitoring_enabled:
            try:
                for partition in self.partitions.values():
                    await self._check_partition_health(partition)
                
                self._update_partition_metrics()
                await asyncio.sleep(self.health_check_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in partition monitoring: {e}")
                await asyncio.sleep(5.0)  # Brief pause on error
    
    async def _check_partition_health(self, partition: BulkheadPartition) -> None:
        """Check the health of a specific partition.
        
        Args:
            partition: Partition to check
        """
        try:
            current_time = time.time()
            partition.last_health_check = current_time
            
            # Update resource usage
            partition.current_usage[ResourceType.CPU] = psutil.cpu_percent(interval=0.1)
            memory_info = psutil.virtual_memory()
            partition.current_usage[ResourceType.MEMORY] = memory_info.used / (1024 * 1024)
            
            # Determine partition state
            if self._is_resource_overloaded(partition):
                if partition.state == BulkheadState.HEALTHY:
                    partition.state = BulkheadState.DEGRADED
                    self.metrics['resource_violations'] += 1
                    self.logger.warning(f"Partition {partition.name} degraded due to resource overload")
                elif partition.state == BulkheadState.DEGRADED:
                    # Check if should be isolated
                    if partition.active_requests >= partition.resource_limits.max_concurrent_requests * 0.9:
                        await self.isolate_partition(partition.name, "Resource overload and high load")
            else:
                if partition.state == BulkheadState.DEGRADED:
                    partition.state = BulkheadState.HEALTHY
                    self.logger.info(f"Partition {partition.name} restored to healthy state")
            
        except Exception as e:
            self.logger.error(f"Error checking partition {partition.name} health: {e}")
            partition.state = BulkheadState.FAILED
    
    def _update_partition_metrics(self) -> None:
        """Update partition state metrics."""
        state_counts = {state: 0 for state in BulkheadState}
        
        for partition in self.partitions.values():
            state_counts[partition.state] += 1
        
        self.metrics.update({
            'total_partitions': len(self.partitions),
            'healthy_partitions': state_counts[BulkheadState.HEALTHY],
            'degraded_partitions': state_counts[BulkheadState.DEGRADED],
            'isolated_partitions': state_counts[BulkheadState.ISOLATED],
            'failed_partitions': state_counts[BulkheadState.FAILED]
        })
    
    def _update_response_time_metric(self, response_time: float) -> None:
        """Update average response time metric.
        
        Args:
            response_time: Response time to include in average
        """
        current_avg = self.metrics['average_response_time']
        total_requests = self.metrics['total_requests_processed']
        
        if total_requests == 0:
            self.metrics['average_response_time'] = response_time
        else:
            # Exponential moving average
            alpha = 0.1
            self.metrics['average_response_time'] = (alpha * response_time) + ((1 - alpha) * current_avg)
    
    def get_partition_status(self, partition_name: str) -> Optional[Dict[str, Any]]:
        """Get status information for a partition.
        
        Args:
            partition_name: Name of partition
            
        Returns:
            Partition status dictionary or None if not found
        """
        if partition_name not in self.partitions:
            return None
        
        partition = self.partitions[partition_name]
        
        return {
            'name': partition.name,
            'state': partition.state.value,
            'services': list(partition.services),
            'active_requests': partition.active_requests,
            'total_requests': partition.total_requests,
            'failed_requests': partition.failed_requests,
            'failure_rate': partition.failed_requests / max(partition.total_requests, 1),
            'resource_limits': {
                'max_cpu_percent': partition.resource_limits.max_cpu_percent,
                'max_memory_mb': partition.resource_limits.max_memory_mb,
                'max_concurrent_requests': partition.resource_limits.max_concurrent_requests
            },
            'current_usage': dict(partition.current_usage),
            'created_at': partition.created_at,
            'last_health_check': partition.last_health_check
        }
    
    def get_service_partition(self, service_name: str) -> Optional[str]:
        """Get the partition name for a service.
        
        Args:
            service_name: Name of service
            
        Returns:
            Partition name or None if service not found
        """
        return self.service_to_partition.get(service_name)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current bulkhead manager metrics.
        
        Returns:
            Metrics dictionary
        """
        return self.metrics.copy()
    
    def _load_configuration(self, config_path: str) -> None:
        """Load configuration from file.
        
        Args:
            config_path: Path to configuration file
        """
        try:
            config_file = Path(config_path)
            if config_file.exists():
                with open(config_file, 'r') as f:
                    config = json.load(f)
                
                # Load partitions from config
                for partition_config in config.get('partitions', []):
                    limits = ResourceLimits(**partition_config.get('resource_limits', {}))
                    self.create_partition(
                        partition_config['name'],
                        partition_config['services'],
                        limits
                    )
                
                # Load other settings
                self.health_check_interval = config.get('health_check_interval', 30.0)
                
                self.logger.info(f"Loaded configuration from {config_path}")
            else:
                self.logger.warning(f"Configuration file {config_path} not found")
                
        except Exception as e:
            self.logger.error(f"Failed to load configuration: {e}")
    
    async def shutdown(self) -> None:
        """Shutdown the bulkhead manager."""
        try:
            # Stop monitoring
            await self.stop_monitoring()
            
            # Shutdown thread executors
            for partition in self.partitions.values():
                if partition.executor:
                    partition.executor.shutdown(wait=True)
            
            self.logger.info("BulkheadManager shutdown completed")
            
        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")


# Example usage and testing
async def main():
    """Example usage of the BulkheadManager."""
    # Initialize manager
    manager = BulkheadManager()
    
    try:
        # Start monitoring
        await manager.start_monitoring()
        
        # Example: Execute function in partition
        async def sample_ai_task():
            await asyncio.sleep(0.1)  # Simulate AI processing
            return "AI processing completed"
        
        result = await manager.execute_in_partition('ai_inference', sample_ai_task)
        print(f"Result: {result}")
        
        # Get partition status
        status = manager.get_partition_status('ai_processing')
        print(f"AI Processing Partition Status: {status}")
        
        # Get metrics
        metrics = manager.get_metrics()
        print(f"Bulkhead Metrics: {metrics}")
        
        # Wait a bit for monitoring
        await asyncio.sleep(5)
        
    finally:
        # Cleanup
        await manager.shutdown()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())