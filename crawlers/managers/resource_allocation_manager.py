"""
Resource Allocation Manager
==========================

Intelligent resource allocation and optimization system for crawler operations.
Manages memory, CPU, network bandwidth, and storage resources efficiently.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.
"""

import asyncio
import psutil
import logging
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import json
import pickle
from collections import defaultdict, deque
import weakref

from ..config.resource_config import ResourceConfig
from ...core.database import get_database_session
from ...core.logging import get_logger
from ...monitoring.metrics_collector import MetricsCollector


class ResourceType(Enum):
    """Types of system resources to manage."""
    CPU = "cpu"
    MEMORY = "memory"
    NETWORK = "network"
    STORAGE = "storage"
    GPU = "gpu"
    THREADS = "threads"
    CONNECTIONS = "connections"


class Priority(Enum):
    """Task priority levels for resource allocation."""
    CRITICAL = 1
    HIGH = 2
    NORMAL = 3
    LOW = 4
    BACKGROUND = 5


@dataclass
class ResourceLimit:
    """Resource limit configuration."""
    max_value: float
    warning_threshold: float = 0.8
    critical_threshold: float = 0.95
    unit: str = ""
    adaptive: bool = True


@dataclass
class ResourceRequest:
    """Resource allocation request."""
    task_id: str
    resource_type: ResourceType
    amount: float
    priority: Priority
    duration_estimate: Optional[float] = None
    callback: Optional[Callable] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    requested_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ResourceAllocation:
    """Active resource allocation."""
    request: ResourceRequest
    allocated_amount: float
    start_time: datetime
    estimated_end_time: Optional[datetime] = None
    actual_usage: float = 0.0
    peak_usage: float = 0.0
    efficiency_score: float = 1.0


@dataclass
class ResourceMetrics:
    """System resource metrics."""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    memory_available: int
    disk_usage_percent: float
    network_io_counters: Dict[str, int]
    active_connections: int
    thread_count: int
    gpu_utilization: Optional[float] = None
    custom_metrics: Dict[str, float] = field(default_factory=dict)


class ResourceAllocationManager:
    """
    Intelligent resource allocation manager for crawler operations.
    
    Provides dynamic resource allocation, monitoring, and optimization
    with adaptive algorithms and predictive scaling.
    """
    
    def __init__(self, config: Optional[ResourceConfig] = None):
        """Initialize the resource allocation manager."""
        self.config = config or ResourceConfig()
        self.logger = get_logger(self.__class__.__name__)
        self.metrics_collector = MetricsCollector()
        
        # Resource state
        self.resource_limits: Dict[ResourceType, ResourceLimit] = {}
        self.active_allocations: Dict[str, ResourceAllocation] = {}
        self.allocation_queue: List[ResourceRequest] = []
        self.allocation_history: deque = deque(maxlen=self.config.HISTORY_SIZE)
        
        # Monitoring state
        self.metrics_history: deque = deque(maxlen=self.config.METRICS_HISTORY_SIZE)
        self.monitoring_active = False
        self.monitoring_thread: Optional[threading.Thread] = None
        
        # Allocation algorithms
        self.allocation_strategies = {
            'fair_share': self._fair_share_allocation,
            'priority_based': self._priority_based_allocation,
            'adaptive': self._adaptive_allocation,
            'predictive': self._predictive_allocation
        }
        
        # Statistics
        self.allocation_stats = {
            'total_requests': 0,
            'successful_allocations': 0,
            'failed_allocations': 0,
            'average_wait_time': 0.0,
            'resource_efficiency': {},
            'peak_usage': {}
        }
        
        # Initialize default resource limits
        self._initialize_resource_limits()
        
    def _initialize_resource_limits(self):
        """Initialize default resource limits based on system capabilities."""
        try:
            # CPU limits
            cpu_count = psutil.cpu_count()
            self.resource_limits[ResourceType.CPU] = ResourceLimit(
                max_value=cpu_count * 100,  # CPU percentage
                warning_threshold=0.8,
                critical_threshold=0.95,
                unit="%"
            )
            
            # Memory limits
            memory_info = psutil.virtual_memory()
            self.resource_limits[ResourceType.MEMORY] = ResourceLimit(
                max_value=memory_info.total,
                warning_threshold=0.8,
                critical_threshold=0.95,
                unit="bytes"
            )
            
            # Network limits (default to 1 Gbps)
            self.resource_limits[ResourceType.NETWORK] = ResourceLimit(
                max_value=1_000_000_000,  # bytes per second
                warning_threshold=0.8,
                critical_threshold=0.95,
                unit="bps"
            )
            
            # Storage limits
            disk_usage = psutil.disk_usage('/')
            self.resource_limits[ResourceType.STORAGE] = ResourceLimit(
                max_value=disk_usage.total,
                warning_threshold=0.8,
                critical_threshold=0.95,
                unit="bytes"
            )
            
            # Thread limits
            self.resource_limits[ResourceType.THREADS] = ResourceLimit(
                max_value=self.config.MAX_THREADS,
                warning_threshold=0.8,
                critical_threshold=0.95,
                unit="threads"
            )
            
            # Connection limits
            self.resource_limits[ResourceType.CONNECTIONS] = ResourceLimit(
                max_value=self.config.MAX_CONNECTIONS,
                warning_threshold=0.8,
                critical_threshold=0.95,
                unit="connections"
            )
            
            self.logger.info("Resource limits initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize resource limits: {e}")
            raise
            
    async def start_monitoring(self):
        """Start resource monitoring."""
        if self.monitoring_active:
            return
            
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        
        self.logger.info("Resource monitoring started")
        
    def stop_monitoring(self):
        """Stop resource monitoring."""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
            
        self.logger.info("Resource monitoring stopped")
        
    def _monitoring_loop(self):
        """Main monitoring loop running in separate thread."""
        while self.monitoring_active:
            try:
                # Collect current metrics
                metrics = self._collect_system_metrics()
                self.metrics_history.append(metrics)
                
                # Update allocation tracking
                self._update_allocation_tracking()
                
                # Check for resource violations
                self._check_resource_violations(metrics)
                
                # Optimize allocations if needed
                asyncio.run_coroutine_threadsafe(
                    self._optimize_allocations(),
                    asyncio.get_event_loop()
                )
                
                time.sleep(self.config.MONITORING_INTERVAL)
                
            except Exception as e:
                self.logger.error(f"Monitoring loop error: {e}")
                time.sleep(1)
                
    def _collect_system_metrics(self) -> ResourceMetrics:
        """Collect current system resource metrics."""
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=None)
            
            # Memory metrics
            memory_info = psutil.virtual_memory()
            
            # Disk metrics
            disk_usage = psutil.disk_usage('/')
            
            # Network metrics
            network_io = psutil.net_io_counters()
            network_counters = {
                'bytes_sent': network_io.bytes_sent,
                'bytes_recv': network_io.bytes_recv,
                'packets_sent': network_io.packets_sent,
                'packets_recv': network_io.packets_recv
            }
            
            # Connection metrics
            connections = len(psutil.net_connections())
            
            # Thread metrics
            process = psutil.Process()
            thread_count = process.num_threads()
            
            # GPU metrics (if available)
            gpu_utilization = self._get_gpu_utilization()
            
            return ResourceMetrics(
                timestamp=datetime.utcnow(),
                cpu_percent=cpu_percent,
                memory_percent=memory_info.percent,
                memory_available=memory_info.available,
                disk_usage_percent=disk_usage.percent,
                network_io_counters=network_counters,
                active_connections=connections,
                thread_count=thread_count,
                gpu_utilization=gpu_utilization
            )
            
        except Exception as e:
            self.logger.error(f"Failed to collect system metrics: {e}")
            return ResourceMetrics(
                timestamp=datetime.utcnow(),
                cpu_percent=0.0,
                memory_percent=0.0,
                memory_available=0,
                disk_usage_percent=0.0,
                network_io_counters={},
                active_connections=0,
                thread_count=0
            )
            
    def _get_gpu_utilization(self) -> Optional[float]:
        """Get GPU utilization if available."""
        try:
            import GPUtil
            gpus = GPUtil.getGPUs()
            if gpus:
                return sum(gpu.load for gpu in gpus) / len(gpus) * 100
        except ImportError:
            pass
        except Exception as e:
            self.logger.debug(f"GPU utilization check failed: {e}")
            
        return None
        
    def _update_allocation_tracking(self):
        """Update tracking for active allocations."""
        current_time = datetime.utcnow()
        
        for allocation_id, allocation in list(self.active_allocations.items()):
            try:
                # Update actual usage
                actual_usage = self._measure_actual_usage(allocation)
                allocation.actual_usage = actual_usage
                allocation.peak_usage = max(allocation.peak_usage, actual_usage)
                
                # Calculate efficiency
                if allocation.allocated_amount > 0:
                    allocation.efficiency_score = min(actual_usage / allocation.allocated_amount, 1.0)
                    
                # Check if allocation should expire
                if (allocation.estimated_end_time and 
                    current_time > allocation.estimated_end_time):
                    self._auto_release_allocation(allocation_id)
                    
            except Exception as e:
                self.logger.error(f"Failed to update allocation tracking for {allocation_id}: {e}")
                
    def _measure_actual_usage(self, allocation: ResourceAllocation) -> float:
        """Measure actual resource usage for an allocation."""
        try:
            resource_type = allocation.request.resource_type
            
            if resource_type == ResourceType.CPU:
                # CPU usage measurement logic
                return psutil.cpu_percent()
                
            elif resource_type == ResourceType.MEMORY:
                # Memory usage measurement logic
                process = psutil.Process()
                return process.memory_info().rss
                
            elif resource_type == ResourceType.NETWORK:
                # Network usage measurement logic
                return 0.0  # Placeholder
                
            elif resource_type == ResourceType.STORAGE:
                # Storage usage measurement logic
                return 0.0  # Placeholder
                
            elif resource_type == ResourceType.THREADS:
                # Thread count measurement
                process = psutil.Process()
                return process.num_threads()
                
            elif resource_type == ResourceType.CONNECTIONS:
                # Connection count measurement
                return len(psutil.net_connections())
                
        except Exception as e:
            self.logger.debug(f"Failed to measure actual usage: {e}")
            
        return 0.0
        
    def _check_resource_violations(self, metrics: ResourceMetrics):
        """Check for resource limit violations and take action."""
        try:
            violations = []
            
            # Check CPU usage
            cpu_limit = self.resource_limits[ResourceType.CPU]
            if metrics.cpu_percent > cpu_limit.max_value * cpu_limit.critical_threshold:
                violations.append(('CPU', metrics.cpu_percent, cpu_limit.max_value))
                
            # Check memory usage
            memory_limit = self.resource_limits[ResourceType.MEMORY]
            if metrics.memory_percent > memory_limit.warning_threshold * 100:
                violations.append(('Memory', metrics.memory_percent, 100.0))
                
            # Check disk usage
            if metrics.disk_usage_percent > 90:
                violations.append(('Disk', metrics.disk_usage_percent, 100.0))
                
            # Handle violations
            if violations:
                self._handle_resource_violations(violations)
                
        except Exception as e:
            self.logger.error(f"Resource violation check failed: {e}")
            
    def _handle_resource_violations(self, violations: List[Tuple[str, float, float]]):
        """Handle resource violations by freeing up resources."""
        self.logger.warning(f"Resource violations detected: {violations}")
        
        # Implement violation handling strategies
        # 1. Suspend low-priority tasks
        # 2. Reduce resource allocations
        # 3. Send alerts
        
        for resource_name, current_usage, limit in violations:
            self.logger.warning(f"{resource_name} usage at {current_usage:.1f}% (limit: {limit:.1f}%)")
            
            # Suspend background tasks
            self._suspend_background_tasks()
            
            # Send alerts if configured
            if self.config.ENABLE_ALERTS:
                asyncio.run_coroutine_threadsafe(
                    self._send_resource_alert(resource_name, current_usage, limit),
                    asyncio.get_event_loop()
                )
                
    def _suspend_background_tasks(self):
        """Suspend background and low-priority tasks."""
        suspended_count = 0
        
        for allocation_id, allocation in list(self.active_allocations.items()):
            if allocation.request.priority in [Priority.LOW, Priority.BACKGROUND]:
                self.logger.info(f"Suspending background task: {allocation_id}")
                self._release_allocation(allocation_id)
                suspended_count += 1
                
        self.logger.info(f"Suspended {suspended_count} background tasks due to resource pressure")
        
    async def _send_resource_alert(self, resource_name: str, current_usage: float, limit: float):
        """Send resource violation alert."""
        try:
            alert_data = {
                'type': 'resource_violation',
                'resource': resource_name,
                'current_usage': current_usage,
                'limit': limit,
                'timestamp': datetime.utcnow().isoformat(),
                'severity': 'critical' if current_usage > limit * 0.95 else 'warning'
            }
            
            # Send to monitoring system
            await self.metrics_collector.send_alert(alert_data)
            
        except Exception as e:
            self.logger.error(f"Failed to send resource alert: {e}")
            
    async def request_resource(self, request: ResourceRequest) -> Optional[str]:
        """
        Request resource allocation.
        
        Args:
            request: Resource allocation request
            
        Returns:
            Allocation ID if successful, None otherwise
        """
        try:
            self.allocation_stats['total_requests'] += 1
            
            # Validate request
            if not self._validate_request(request):
                self.allocation_stats['failed_allocations'] += 1
                return None
                
            # Check immediate availability
            if self._can_allocate_immediately(request):
                allocation_id = await self._allocate_resource(request)
                if allocation_id:
                    self.allocation_stats['successful_allocations'] += 1
                    return allocation_id
                    
            # Queue for later allocation
            self.allocation_queue.append(request)
            self.logger.info(f"Resource request queued: {request.task_id}")
            
            # Try to process queue
            await self._process_allocation_queue()
            
            return None
            
        except Exception as e:
            self.logger.error(f"Resource request failed: {e}")
            self.allocation_stats['failed_allocations'] += 1
            return None
            
    def _validate_request(self, request: ResourceRequest) -> bool:
        """Validate resource allocation request."""
        try:
            # Check if resource type is supported
            if request.resource_type not in self.resource_limits:
                self.logger.warning(f"Unsupported resource type: {request.resource_type}")
                return False
                
            # Check if amount is reasonable
            limit = self.resource_limits[request.resource_type]
            if request.amount > limit.max_value:
                self.logger.warning(f"Request amount exceeds limit: {request.amount} > {limit.max_value}")
                return False
                
            # Check if task ID is unique
            if request.task_id in self.active_allocations:
                self.logger.warning(f"Task ID already allocated: {request.task_id}")
                return False
                
            return True
            
        except Exception as e:
            self.logger.error(f"Request validation failed: {e}")
            return False
            
    def _can_allocate_immediately(self, request: ResourceRequest) -> bool:
        """Check if resource can be allocated immediately."""
        try:
            resource_type = request.resource_type
            limit = self.resource_limits[resource_type]
            
            # Calculate current usage
            current_usage = self._calculate_current_usage(resource_type)
            
            # Check if there's enough capacity
            available = limit.max_value * limit.warning_threshold - current_usage
            
            return available >= request.amount
            
        except Exception as e:
            self.logger.error(f"Immediate allocation check failed: {e}")
            return False
            
    def _calculate_current_usage(self, resource_type: ResourceType) -> float:
        """Calculate current resource usage."""
        current_usage = 0.0
        
        for allocation in self.active_allocations.values():
            if allocation.request.resource_type == resource_type:
                current_usage += allocation.allocated_amount
                
        return current_usage
        
    async def _allocate_resource(self, request: ResourceRequest) -> Optional[str]:
        """Allocate resource to request."""
        try:
            allocation_id = f"{request.task_id}_{int(time.time())}"
            
            # Determine allocation amount using strategy
            strategy = self.allocation_strategies.get(
                self.config.ALLOCATION_STRATEGY,
                self._fair_share_allocation
            )
            
            allocated_amount = strategy(request)
            
            if allocated_amount <= 0:
                return None
                
            # Create allocation
            allocation = ResourceAllocation(
                request=request,
                allocated_amount=allocated_amount,
                start_time=datetime.utcnow(),
                estimated_end_time=(
                    datetime.utcnow() + timedelta(seconds=request.duration_estimate)
                    if request.duration_estimate else None
                )
            )
            
            # Store allocation
            self.active_allocations[allocation_id] = allocation
            
            # Call callback if provided
            if request.callback:
                try:
                    await request.callback(allocation_id, allocated_amount)
                except Exception as e:
                    self.logger.error(f"Allocation callback failed: {e}")
                    
            self.logger.info(f"Resource allocated: {allocation_id} ({allocated_amount} {resource_type.value})")
            
            return allocation_id
            
        except Exception as e:
            self.logger.error(f"Resource allocation failed: {e}")
            return None
            
    def _fair_share_allocation(self, request: ResourceRequest) -> float:
        """Fair share allocation strategy."""
        resource_type = request.resource_type
        limit = self.resource_limits[resource_type]
        
        # Calculate fair share based on number of active allocations
        active_count = sum(1 for alloc in self.active_allocations.values() 
                          if alloc.request.resource_type == resource_type)
        
        if active_count == 0:
            return min(request.amount, limit.max_value * 0.5)
            
        fair_share = limit.max_value / (active_count + 1)
        return min(request.amount, fair_share)
        
    def _priority_based_allocation(self, request: ResourceRequest) -> float:
        """Priority-based allocation strategy."""
        resource_type = request.resource_type
        limit = self.resource_limits[resource_type]
        
        # Priority multipliers
        priority_multipliers = {
            Priority.CRITICAL: 1.0,
            Priority.HIGH: 0.8,
            Priority.NORMAL: 0.6,
            Priority.LOW: 0.4,
            Priority.BACKGROUND: 0.2
        }
        
        multiplier = priority_multipliers.get(request.priority, 0.6)
        max_allocation = limit.max_value * multiplier
        
        return min(request.amount, max_allocation)
        
    def _adaptive_allocation(self, request: ResourceRequest) -> float:
        """Adaptive allocation strategy based on historical usage."""
        # Use historical data to predict optimal allocation
        base_allocation = self._fair_share_allocation(request)
        
        # Adjust based on system load
        if self.metrics_history:
            recent_metrics = self.metrics_history[-1]
            
            if request.resource_type == ResourceType.CPU:
                load_factor = 1.0 - (recent_metrics.cpu_percent / 100.0)
            elif request.resource_type == ResourceType.MEMORY:
                load_factor = 1.0 - (recent_metrics.memory_percent / 100.0)
            else:
                load_factor = 1.0
                
            return base_allocation * max(0.1, load_factor)
            
        return base_allocation
        
    def _predictive_allocation(self, request: ResourceRequest) -> float:
        """Predictive allocation strategy using ML models."""
        # Placeholder for ML-based prediction
        # Would use historical data to predict optimal allocation
        return self._adaptive_allocation(request)
        
    async def _process_allocation_queue(self):
        """Process queued allocation requests."""
        if not self.allocation_queue:
            return
            
        # Sort queue by priority
        self.allocation_queue.sort(key=lambda x: x.priority.value)
        
        processed_count = 0
        remaining_queue = []
        
        for request in self.allocation_queue:
            try:
                if self._can_allocate_immediately(request):
                    allocation_id = await self._allocate_resource(request)
                    if allocation_id:
                        processed_count += 1
                        self.allocation_stats['successful_allocations'] += 1
                        continue
                        
                remaining_queue.append(request)
                
            except Exception as e:
                self.logger.error(f"Queue processing error for {request.task_id}: {e}")
                self.allocation_stats['failed_allocations'] += 1
                
        self.allocation_queue = remaining_queue
        
        if processed_count > 0:
            self.logger.info(f"Processed {processed_count} queued allocation requests")
            
    def release_resource(self, allocation_id: str) -> bool:
        """
        Release resource allocation.
        
        Args:
            allocation_id: ID of allocation to release
            
        Returns:
            True if successful, False otherwise
        """
        return self._release_allocation(allocation_id)
        
    def _release_allocation(self, allocation_id: str) -> bool:
        """Internal method to release allocation."""
        try:
            if allocation_id not in self.active_allocations:
                self.logger.warning(f"Allocation not found: {allocation_id}")
                return False
                
            allocation = self.active_allocations.pop(allocation_id)
            
            # Store in history
            self.allocation_history.append({
                'allocation_id': allocation_id,
                'request': allocation.request,
                'allocated_amount': allocation.allocated_amount,
                'actual_usage': allocation.actual_usage,
                'peak_usage': allocation.peak_usage,
                'efficiency_score': allocation.efficiency_score,
                'duration': (datetime.utcnow() - allocation.start_time).total_seconds(),
                'released_at': datetime.utcnow()
            })
            
            self.logger.info(f"Resource released: {allocation_id}")
            
            # Process waiting queue
            asyncio.create_task(self._process_allocation_queue())
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to release allocation {allocation_id}: {e}")
            return False
            
    def _auto_release_allocation(self, allocation_id: str):
        """Automatically release expired allocation."""
        self.logger.info(f"Auto-releasing expired allocation: {allocation_id}")
        self._release_allocation(allocation_id)
        
    async def _optimize_allocations(self):
        """Optimize current resource allocations."""
        try:
            # Identify underutilized allocations
            underutilized = []
            for allocation_id, allocation in self.active_allocations.items():
                if allocation.efficiency_score < self.config.MIN_EFFICIENCY_THRESHOLD:
                    underutilized.append((allocation_id, allocation))
                    
            # Resize underutilized allocations
            for allocation_id, allocation in underutilized:
                if allocation.actual_usage > 0:
                    new_size = allocation.actual_usage * self.config.OPTIMIZATION_FACTOR
                    self.logger.info(f"Optimizing allocation {allocation_id}: {allocation.allocated_amount} -> {new_size}")
                    allocation.allocated_amount = new_size
                    
        except Exception as e:
            self.logger.error(f"Allocation optimization failed: {e}")
            
    async def get_resource_usage(self) -> Dict[str, Any]:
        """Get current resource usage statistics."""
        try:
            usage_stats = {}
            
            for resource_type, limit in self.resource_limits.items():
                current_usage = self._calculate_current_usage(resource_type)
                usage_percentage = (current_usage / limit.max_value) * 100
                
                usage_stats[resource_type.value] = {
                    'current_usage': current_usage,
                    'max_limit': limit.max_value,
                    'usage_percentage': usage_percentage,
                    'available': limit.max_value - current_usage,
                    'warning_threshold': limit.warning_threshold * 100,
                    'critical_threshold': limit.critical_threshold * 100
                }
                
            return usage_stats
            
        except Exception as e:
            self.logger.error(f"Failed to get resource usage: {e}")
            return {}
            
    async def get_allocation_stats(self) -> Dict[str, Any]:
        """Get allocation statistics."""
        stats = self.allocation_stats.copy()
        
        # Calculate additional metrics
        if stats['total_requests'] > 0:
            stats['success_rate'] = stats['successful_allocations'] / stats['total_requests']
            
        stats['active_allocations'] = len(self.active_allocations)
        stats['queued_requests'] = len(self.allocation_queue)
        
        return stats
        
    async def get_system_metrics(self) -> Optional[ResourceMetrics]:
        """Get latest system metrics."""
        if self.metrics_history:
            return self.metrics_history[-1]
        return None
        
    def set_resource_limit(self, resource_type: ResourceType, limit: ResourceLimit):
        """Set resource limit."""
        self.resource_limits[resource_type] = limit
        self.logger.info(f"Resource limit updated: {resource_type.value} = {limit.max_value}")
        
    def update_allocation_strategy(self, strategy: str):
        """Update allocation strategy."""
        if strategy in self.allocation_strategies:
            self.config.ALLOCATION_STRATEGY = strategy
            self.logger.info(f"Allocation strategy updated: {strategy}")
        else:
            self.logger.warning(f"Unknown allocation strategy: {strategy}")
            
    async def cleanup(self):
        """Cleanup resources and stop monitoring."""
        try:
            # Stop monitoring
            self.stop_monitoring()
            
            # Release all active allocations
            for allocation_id in list(self.active_allocations.keys()):
                self._release_allocation(allocation_id)
                
            # Clear queue
            self.allocation_queue.clear()
            
            self.logger.info("Resource allocation manager cleaned up successfully")
            
        except Exception as e:
            self.logger.error(f"Cleanup error: {e}")


# Factory function
def create_resource_allocation_manager(config: Optional[ResourceConfig] = None) -> ResourceAllocationManager:
    """Create and return a resource allocation manager instance."""
    return ResourceAllocationManager(config)


# Utility functions
async def monitor_resource_usage(duration_seconds: int = 60) -> List[ResourceMetrics]:
    """Monitor resource usage for specified duration."""
    metrics = []
    manager = create_resource_allocation_manager()
    
    try:
        await manager.start_monitoring()
        
        start_time = time.time()
        while time.time() - start_time < duration_seconds:
            current_metrics = await manager.get_system_metrics()
            if current_metrics:
                metrics.append(current_metrics)
            await asyncio.sleep(1)
            
    finally:
        await manager.cleanup()
        
    return metrics


async def optimize_resource_allocation(manager: ResourceAllocationManager) -> Dict[str, Any]:
    """Optimize resource allocation and return statistics."""
    initial_stats = await manager.get_allocation_stats()
    await manager._optimize_allocations()
    final_stats = await manager.get_allocation_stats()
    
    return {
        'initial_stats': initial_stats,
        'final_stats': final_stats,
        'optimization_time': datetime.utcnow().isoformat()
    }
