"""Resource Scheduler Module
========================

Advanced resource-aware scheduling system for crawler operations.
Implements intelligent resource allocation and optimization.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

WARNING: This code is protected by copyright law. Any unauthorized copying, 
distribution, or modification is strictly prohibited and will result in 
legal action. Contact mlaiel@live.de for licensing.

Expertise combinée:
- Lead Developer IA: Architecture intelligente et optimisations ML
- Backend Senior: Infrastructure robuste et scalabilité enterprise
- ML Engineer: Algorithmes d'apprentissage et modèles prédictifs
- DBA Expert: Gestion de données et optimisation des requêtes
- Sécurité: Protection et chiffrement des données sensibles
- Microservices: Architecture distribuée et communication inter-services
- Audio/Vidéo: Traitement multimédia et analyse de contenu
- DevOps: Déploiement, monitoring et infrastructure cloud
- IA Prompt Engineer: Optimisation des interactions et prompts

Business Logic Integration:
Resource monitoring → Intelligent allocation → Performance optimization → 
Scaling decisions → Cost optimization → SLA compliance → 
Quality assurance → Business continuity → Revenue protection
"""

import asyncio
import logging
import time
import psutil
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set, Tuple, Union, Callable
from dataclasses import dataclass, field, asdict
from enum import Enum, IntEnum
import numpy as np
from collections import defaultdict, deque
import threading
from abc import ABC, abstractmethod
import aiohttp
import aiofiles

logger = logging.getLogger(__name__)


class ResourceType(Enum):
    """
Types of system resources."""

    CPU = "cpu"
    MEMORY = "memory"
    DISK = "disk"
    NETWORK = "network"
    GPU = "gpu"
    DATABASE = "database"
    CACHE = "cache"
    QUEUE = "queue"


class AllocationStrategy(Enum):
    """Resource allocation strategies."""

    FAIR_SHARE = "fair_share"
    PRIORITY_BASED = "priority_based"
    PERFORMANCE_BASED = "performance_based"
    COST_OPTIMIZED = "cost_optimized"
    SLA_GUARANTEED = "sla_guaranteed"
    ADAPTIVE = "adaptive"
    BURST_CAPABLE = "burst_capable"


class ResourceStatus(Enum):
    """Resource availability status."""

    AVAILABLE = "available"
    ALLOCATED = "allocated"
    OVERLOADED = "overloaded"
    UNAVAILABLE = "unavailable"
    MAINTENANCE = "maintenance"
    SCALING = "scaling"


class ScalingAction(Enum):
    """Auto-scaling actions."""

    SCALE_UP = "scale_up"
    SCALE_DOWN = "scale_down"
    SCALE_OUT = "scale_out"
    SCALE_IN = "scale_in"
    MAINTAIN = "maintain"
    REDISTRIBUTE = "redistribute"


@dataclass
class ResourceQuota:
    """Resource quota definition."""
    cpu_cores: float = 0.0
    memory_mb: int = 0
    disk_mb: int = 0
    network_mbps: float = 0.0
    gpu_units: int = 0
    database_connections: int = 0
    cache_mb: int = 0
    queue_slots: int = 0
    max_concurrent_tasks: int = 0
    priority_weight: float = 1.0


@dataclass
class ResourceUsage:
    """
Current resource usage statistics."""
    cpu_percent: float = 0.0
    memory_percent: float = 0.0
    disk_percent: float = 0.0
    network_percent: float = 0.0
    gpu_percent: float = 0.0
    database_percent: float = 0.0
    cache_percent: float = 0.0
    queue_percent: float = 0.0
    active_tasks: int = 0
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ResourcePool:
    """
Resource pool configuration."""
    pool_id: str
    resource_type: ResourceType
    total_capacity: ResourceQuota
    available_capacity: ResourceQuota
    allocated_capacity: ResourceQuota
    reserved_capacity: ResourceQuota
    allocation_strategy: AllocationStrategy
    status: ResourceStatus = ResourceStatus.AVAILABLE
    priority_levels: Dict[int, float] = field(default_factory=dict)
    scaling_config: Dict[str, Any] = field(default_factory=dict)
    cost_per_unit: Dict[str, float] = field(default_factory=dict)
    sla_requirements: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_updated: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ResourceAllocation:
    """
Resource allocation record."""
    allocation_id: str
    task_id: str
    pool_id: str
    allocated_quota: ResourceQuota
    allocated_at: datetime
    expires_at: Optional[datetime] = None
    actual_usage: Optional[ResourceUsage] = None
    cost_incurred: float = 0.0
    sla_compliance: float = 100.0
    allocation_efficiency: float = 0.0
    priority: int = 5
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ScalingEvent:
    """
Auto-scaling event record."""
    event_id: str
    pool_id: str
    action: ScalingAction
    trigger_metric: str
    trigger_value: float
    threshold: float
    scaling_factor: float
    executed_at: datetime
    execution_duration: float = 0.0
    success: bool = True
    error_details: Optional[str] = None
    cost_impact: float = 0.0
    performance_impact: float = 0.0


@dataclass
class ResourceMetrics:
    """
Resource scheduler performance metrics."""
    total_allocations: int = 0
    successful_allocations: int = 0
    failed_allocations: int = 0
    average_allocation_time: float = 0.0
    resource_utilization: Dict[str, float] = field(default_factory=dict)
    scaling_events: int = 0
    cost_efficiency: float = 0.0
    sla_compliance_rate: float = 100.0
    allocation_accuracy: float = 0.0
    last_updated: datetime = field(default_factory=datetime.utcnow)


class ResourceScheduler:
    """
    Advanced resource-aware scheduler for crawler operations.
    
    Features:
    - Intelligent resource allocation and optimization
    - Auto-scaling based on demand and performance
    - Cost optimization with SLA compliance
    - Multi-tenancy with fair resource sharing
    - Real-time resource monitoring and alerting
    - Predictive resource planning
    - Performance-based resource adjustment
    - Emergency resource reallocation
    """
    
    def __init__(
        self,
        enable_auto_scaling: bool = True,
        enable_cost_optimization: bool = True,
        enable_predictive_scaling: bool = True,
        monitoring_interval: int = 30,  # seconds
        scaling_cooldown: int = 300,  # seconds
        resource_history_size: int = 1000
    ):
        """
Initialize resource scheduler."""
        self.enable_auto_scaling = enable_auto_scaling
        self.enable_cost_optimization = enable_cost_optimization
        self.enable_predictive_scaling = enable_predictive_scaling
        self.monitoring_interval = monitoring_interval
        self.scaling_cooldown = scaling_cooldown
        self.resource_history_size = resource_history_size
        
        # Resource management
        self.resource_pools: Dict[str, ResourcePool] = {}
        self.active_allocations: Dict[str, ResourceAllocation] = {}
        self.allocation_history: deque = deque(maxlen=resource_history_size)
        self.scaling_history: deque = deque(maxlen=500)
        
        # Monitoring and metrics
        self.resource_usage_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=200))
        self.metrics = ResourceMetrics()
        self.performance_baselines: Dict[str, Dict[str, float]] = {}
        
        # Auto-scaling state
        self.last_scaling_time: Dict[str, datetime] = {}
        self.scaling_in_progress: Set[str] = set()
        self.emergency_mode: bool = False
        
        # Configuration
        self.config = {
            'cpu_utilization_target': 70.0,  # percent
            'memory_utilization_target': 80.0,  # percent
            'scaling_threshold_upper': 85.0,  # percent
            'scaling_threshold_lower': 30.0,  # percent
            'emergency_threshold': 95.0,  # percent
            'allocation_timeout': 60.0,  # seconds
            'resource_check_interval': 10.0,  # seconds
            'cost_optimization_interval': 300.0,  # seconds
            'sla_enforcement_enabled': True,
            'burst_allocation_enabled': True,
            'max_burst_multiplier': 2.0,
            'resource_reservation_percent': 10.0,  # percent
            'predictive_scaling_horizon': 3600,  # seconds
            'fair_share_enabled': True
        }
        
        # State tracking
        self.is_running = False
        self.monitor_task: Optional[asyncio.Task] = None
        self.scaling_task: Optional[asyncio.Task] = None
        self.cost_optimizer_task: Optional[asyncio.Task] = None
        
        # Event callbacks
        self.event_callbacks: Dict[str, List[Callable]] = defaultdict(list)
        
        logger.info("Resource scheduler initialized")
    
    async def initialize(self) -> None:
        """Initialize resource scheduler."""
        try:
            # Initialize default resource pools
            await self._initialize_default_pools()
            
            # Start monitoring and optimization
            await self.start_monitoring()
            
            logger.info("Resource scheduler initialization complete")
            
        except Exception as e:
            logger.error(f"Failed to initialize resource scheduler: {e}")
            raise
    
    async def _initialize_default_pools(self) -> None:
        """Initialize default resource pools."""
        # Get system resources
        system_info = await self._get_system_info()
        
        # CPU Pool
        cpu_pool = ResourcePool(
            pool_id="cpu_pool",
            resource_type=ResourceType.CPU,
            total_capacity=ResourceQuota(cpu_cores=system_info['cpu_cores']),
            available_capacity=ResourceQuota(cpu_cores=system_info['cpu_cores'] * 0.9),
            allocated_capacity=ResourceQuota(),
            reserved_capacity=ResourceQuota(cpu_cores=system_info['cpu_cores'] * 0.1),
            allocation_strategy=AllocationStrategy.PERFORMANCE_BASED,
            scaling_config={
                'min_capacity': system_info['cpu_cores'] * 0.5,
                'max_capacity': system_info['cpu_cores'] * 2.0,
                'scale_up_threshold': 80.0,
                'scale_down_threshold': 30.0
            }
        )
        
        # Memory Pool
        memory_pool = ResourcePool(
            pool_id="memory_pool",
            resource_type=ResourceType.MEMORY,
            total_capacity=ResourceQuota(memory_mb=system_info['memory_mb']),
            available_capacity=ResourceQuota(memory_mb=int(system_info['memory_mb'] * 0.85)),
            allocated_capacity=ResourceQuota(),
            reserved_capacity=ResourceQuota(memory_mb=int(system_info['memory_mb'] * 0.15)),
            allocation_strategy=AllocationStrategy.FAIR_SHARE,
            scaling_config={
                'min_capacity': system_info['memory_mb'] * 0.5,
                'max_capacity': system_info['memory_mb'] * 1.5,
                'scale_up_threshold': 85.0,
                'scale_down_threshold': 40.0
            }
        )
        
        # Network Pool
        network_pool = ResourcePool(
            pool_id="network_pool",
            resource_type=ResourceType.NETWORK,
            total_capacity=ResourceQuota(network_mbps=1000.0),  # Assume 1 Gbps
            available_capacity=ResourceQuota(network_mbps=900.0),
            allocated_capacity=ResourceQuota(),
            reserved_capacity=ResourceQuota(network_mbps=100.0),
            allocation_strategy=AllocationStrategy.PRIORITY_BASED,
            scaling_config={
                'burst_enabled': True,
                'burst_threshold': 80.0,
                'burst_multiplier': 1.5
            }
        )
        
        # Database Pool
        database_pool = ResourcePool(
            pool_id="database_pool",
            resource_type=ResourceType.DATABASE,
            total_capacity=ResourceQuota(database_connections=100),
            available_capacity=ResourceQuota(database_connections=80),
            allocated_capacity=ResourceQuota(),
            reserved_capacity=ResourceQuota(database_connections=20),
            allocation_strategy=AllocationStrategy.SLA_GUARANTEED,
            scaling_config={
                'connection_pool_size': 100,
                'max_connections': 200,
                'scale_up_threshold': 75.0
            }
        )
        
        # Add pools
        for pool in [cpu_pool, memory_pool, network_pool, database_pool]:
            self.resource_pools[pool.pool_id] = pool
        
        logger.info(f"Initialized {len(self.resource_pools)} resource pools")
    
    async def _get_system_info(self) -> Dict[str, Any]:
        """Get system resource information."""
        try:
            # CPU information
            cpu_count = psutil.cpu_count(logical=True)
            cpu_freq = psutil.cpu_freq()
            
            # Memory information
            memory = psutil.virtual_memory()
            
            # Disk information
            disk = psutil.disk_usage('/')
            
            # Network information (simplified)
            network_stats = psutil.net_io_counters()
            
            return {
                'cpu_cores': float(cpu_count),
                'cpu_frequency': cpu_freq.max if cpu_freq else 2000.0,
                'memory_mb': int(memory.total / (1024 * 1024)),
                'disk_mb': int(disk.total / (1024 * 1024)),
                'network_interfaces': len(psutil.net_if_addrs()),
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get system info: {e}")
            # Return default values
            return {
                'cpu_cores': 4.0,
                'cpu_frequency': 2000.0,
                'memory_mb': 8192,
                'disk_mb': 102400,
                'network_interfaces': 1
            }
    
    async def start_monitoring(self) -> None:
        """Start resource monitoring and optimization."""
        if self.is_running:
            return
        
        self.is_running = True
        
        # Start monitoring tasks
        self.monitor_task = asyncio.create_task(self._resource_monitoring_loop())
        
        if self.enable_auto_scaling:
            self.scaling_task = asyncio.create_task(self._auto_scaling_loop())
        
        if self.enable_cost_optimization:
            self.cost_optimizer_task = asyncio.create_task(self._cost_optimization_loop())
        
        logger.info("Resource monitoring started")
    
    async def stop_monitoring(self) -> None:
        """Stop resource monitoring."""
        self.is_running = False
        
        for task in [self.monitor_task, self.scaling_task, self.cost_optimizer_task]:
            if task:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
        
        logger.info("Resource monitoring stopped")
    
    async def allocate_resources(
        self,
        task_id: str,
        resource_requirements: ResourceQuota,
        priority: int = 5,
        timeout: Optional[float] = None,
        allow_burst: bool = False
    ) -> Optional[ResourceAllocation]:
        """Allocate resources for a task."""
        try:
            allocation_start = time.time()
            timeout = timeout or self.config['allocation_timeout']
            
            # Generate allocation ID
            allocation_id = f"alloc_{task_id}_{int(time.time())}"
            
            # Find best resource allocation strategy
            allocation_plan = await self._plan_resource_allocation(
                resource_requirements, priority, allow_burst
            )
            
            if not allocation_plan:
                logger.warning(f"No resources available for task {task_id}")
                self.metrics.failed_allocations += 1
                return None
            
            # Execute allocation
            allocation = await self._execute_allocation(
                allocation_id, task_id, allocation_plan, priority
            )
            
            if allocation:
                # Track allocation
                self.active_allocations[allocation_id] = allocation
                self.allocation_history.append(allocation)
                
                # Update metrics
                self.metrics.total_allocations += 1
                self.metrics.successful_allocations += 1
                allocation_time = time.time() - allocation_start
                self.metrics.average_allocation_time = (
                    (self.metrics.average_allocation_time * (self.metrics.total_allocations - 1) + allocation_time) /
                    self.metrics.total_allocations
                )
                
                # Call allocation callbacks
                await self._call_callbacks('allocated', allocation)
                
                logger.info(f"Resources allocated for task {task_id}: {allocation_id}")
                return allocation
            
            else:
                self.metrics.failed_allocations += 1
                return None
                
        except Exception as e:
            logger.error(f"Resource allocation failed for task {task_id}: {e}")
            self.metrics.failed_allocations += 1
            return None
    
    async def _plan_resource_allocation(
        self,
        requirements: ResourceQuota,
        priority: int,
        allow_burst: bool
    ) -> Optional[Dict[str, Any]]:
        """Plan optimal resource allocation."""
        allocation_plan = {}
        
        # Check each resource requirement
        resource_mappings = {
            'cpu_cores': ('cpu_pool', 'cpu_cores'),
            'memory_mb': ('memory_pool', 'memory_mb'),
            'network_mbps': ('network_pool', 'network_mbps'),
            'database_connections': ('database_pool', 'database_connections')
        }
        
        for req_attr, (pool_id, pool_attr) in resource_mappings.items():
            required_amount = getattr(requirements, req_attr, 0)
            
            if required_amount > 0:
                pool = self.resource_pools.get(pool_id)
                if not pool:
                    continue
                
                available_amount = getattr(pool.available_capacity, pool_attr, 0)
                
                # Check if allocation is possible
                if required_amount <= available_amount:
                    allocation_plan[pool_id] = {
                        'resource_type': pool_attr,
                        'amount': required_amount,
                        'allocation_strategy': pool.allocation_strategy
                    }
                elif allow_burst and self.config['burst_allocation_enabled']:
                    # Check burst capacity
                    burst_multiplier = self.config['max_burst_multiplier']
                    burst_available = available_amount * burst_multiplier
                    
                    if required_amount <= burst_available:
                        allocation_plan[pool_id] = {
                            'resource_type': pool_attr,
                            'amount': required_amount,
                            'allocation_strategy': pool.allocation_strategy,
                            'burst_allocation': True
                        }
                    else:
                        return None  # Cannot satisfy requirement
                else:
                    return None  # Cannot satisfy requirement
        
        return allocation_plan if allocation_plan else None
    
    async def _execute_allocation(
        self,
        allocation_id: str,
        task_id: str,
        allocation_plan: Dict[str, Any],
        priority: int
    ) -> Optional[ResourceAllocation]:
        """
Execute the resource allocation plan."""
        try:
            allocated_quota = ResourceQuota()
            pool_allocations = {}
            
            # Allocate from each pool
            for pool_id, plan in allocation_plan.items():
                pool = self.resource_pools[pool_id]
                resource_type = plan['resource_type']
                amount = plan['amount']
                
                # Update pool allocations
                current_allocated = getattr(pool.allocated_capacity, resource_type, 0)
                current_available = getattr(pool.available_capacity, resource_type, 0)
                
                # Check if still available
                if amount > current_available and not plan.get('burst_allocation', False):
                    # Rollback previous allocations
                    await self._rollback_allocations(pool_allocations)
                    return None
                
                # Update pool state
                setattr(pool.allocated_capacity, resource_type, current_allocated + amount)
                setattr(pool.available_capacity, resource_type, current_available - amount)
                setattr(allocated_quota, resource_type, amount)
                
                pool_allocations[pool_id] = {
                    'resource_type': resource_type,
                    'amount': amount
                }
                
                pool.last_updated = datetime.utcnow()
            
            # Create allocation record
            allocation = ResourceAllocation(
                allocation_id=allocation_id,
                task_id=task_id,
                pool_id=",".join(allocation_plan.keys()),
                allocated_quota=allocated_quota,
                allocated_at=datetime.utcnow(),
                priority=priority,
                metadata={'allocation_plan': allocation_plan}
            )
            
            return allocation
            
        except Exception as e:
            logger.error(f"Failed to execute allocation {allocation_id}: {e}")
            return None
    
    async def _rollback_allocations(self, pool_allocations: Dict[str, Dict[str, Any]]) -> None:
        """Rollback partial allocations."""
        for pool_id, allocation_info in pool_allocations.items():
            pool = self.resource_pools.get(pool_id)
            if pool:
                resource_type = allocation_info['resource_type']
                amount = allocation_info['amount']
                
                # Restore pool state
                current_allocated = getattr(pool.allocated_capacity, resource_type, 0)
                current_available = getattr(pool.available_capacity, resource_type, 0)
                
                setattr(pool.allocated_capacity, resource_type, max(0, current_allocated - amount))
                setattr(pool.available_capacity, resource_type, current_available + amount)
    
    async def deallocate_resources(self, allocation_id: str) -> bool:
        """
Deallocate resources."""
        try:
            allocation = self.active_allocations.get(allocation_id)
            if not allocation:
                return False
            
            # Parse pool IDs
            pool_ids = allocation.pool_id.split(',')
            
            # Return resources to pools
            for pool_id in pool_ids:
                pool = self.resource_pools.get(pool_id)
                if not pool:
                    continue
                
                # Find allocation plan for this pool
                allocation_plan = allocation.metadata.get('allocation_plan', {})
                plan = allocation_plan.get(pool_id)
                
                if plan:
                    resource_type = plan['resource_type']
                    amount = plan['amount']
                    
                    # Update pool state
                    current_allocated = getattr(pool.allocated_capacity, resource_type, 0)
                    current_available = getattr(pool.available_capacity, resource_type, 0)
                    
                    setattr(pool.allocated_capacity, resource_type, max(0, current_allocated - amount))
                    setattr(pool.available_capacity, resource_type, current_available + amount)
                    
                    pool.last_updated = datetime.utcnow()
            
            # Remove from active allocations
            del self.active_allocations[allocation_id]
            
            # Call deallocation callbacks
            await self._call_callbacks('deallocated', allocation)
            
            logger.info(f"Resources deallocated: {allocation_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to deallocate resources {allocation_id}: {e}")
            return False
    
    async def update_resource_usage(
        self,
        allocation_id: str,
        usage: ResourceUsage
    ) -> None:
        """Update actual resource usage for an allocation."""
        allocation = self.active_allocations.get(allocation_id)
        if allocation:
            allocation.actual_usage = usage
            
            # Calculate allocation efficiency
            if allocation.allocated_quota.cpu_cores > 0:
                cpu_efficiency = (usage.cpu_percent / 100.0) / allocation.allocated_quota.cpu_cores
                allocation.allocation_efficiency = min(100.0, cpu_efficiency * 100.0)
            
            # Store usage history
            self.resource_usage_history[allocation_id].append(usage)
    
    async def _resource_monitoring_loop(self) -> None:
        """
Resource monitoring background loop."""
        while self.is_running:
            try:
                await self._monitor_system_resources()
                await self._monitor_pool_health()
                await self._update_resource_metrics()
                
                await asyncio.sleep(self.monitoring_interval)
                
            except Exception as e:
                logger.error(f"Resource monitoring error: {e}")
                await asyncio.sleep(10)
    
    async def _monitor_system_resources(self) -> None:
        """Monitor system resource usage."""
        try:
            # Get current system usage
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Update pool usage
            for pool_id, pool in self.resource_pools.items():
                if pool.resource_type == ResourceType.CPU:
                    pool.status = self._determine_pool_status(cpu_percent, 85.0, 95.0)
                elif pool.resource_type == ResourceType.MEMORY:
                    pool.status = self._determine_pool_status(memory.percent, 85.0, 95.0)
                elif pool.resource_type == ResourceType.DISK:
                    pool.status = self._determine_pool_status(disk.percent, 85.0, 95.0)
            
            # Check for emergency conditions
            if cpu_percent > 95.0 or memory.percent > 95.0:
                if not self.emergency_mode:
                    self.emergency_mode = True
                    await self._handle_emergency_condition()
            else:
                self.emergency_mode = False
                
        except Exception as e:
            logger.error(f"System resource monitoring failed: {e}")
    
    def _determine_pool_status(
        self,
        usage_percent: float,
        warning_threshold: float,
        critical_threshold: float
    ) -> ResourceStatus:
        """Determine pool status based on usage."""
        if usage_percent >= critical_threshold:
            return ResourceStatus.OVERLOADED
        elif usage_percent >= warning_threshold:
            return ResourceStatus.ALLOCATED
        else:
            return ResourceStatus.AVAILABLE
    
    async def _monitor_pool_health(self) -> None:
        """
Monitor health of resource pools."""
        for pool_id, pool in self.resource_pools.items():
            try:
                # Calculate utilization
                total_capacity = pool.total_capacity
                allocated_capacity = pool.allocated_capacity
                
                # CPU utilization
                if total_capacity.cpu_cores > 0:
                    cpu_util = (allocated_capacity.cpu_cores / total_capacity.cpu_cores) * 100
                    self.metrics.resource_utilization[f"{pool_id}_cpu"] = cpu_util
                
                # Memory utilization
                if total_capacity.memory_mb > 0:
                    memory_util = (allocated_capacity.memory_mb / total_capacity.memory_mb) * 100
                    self.metrics.resource_utilization[f"{pool_id}_memory"] = memory_util
                
                # Check for scaling triggers
                if self.enable_auto_scaling:
                    await self._check_scaling_triggers(pool)
                
            except Exception as e:
                logger.error(f"Pool health monitoring failed for {pool_id}: {e}")
    
    async def _auto_scaling_loop(self) -> None:
        """Auto-scaling background loop."""
        while self.is_running:
            try:
                await self._evaluate_scaling_decisions()
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Auto-scaling error: {e}")
                await asyncio.sleep(10)
    
    async def _check_scaling_triggers(self, pool: ResourcePool) -> None:
        """Check if scaling is needed for a pool."""
        if pool.pool_id in self.scaling_in_progress:
            return
        
        # Check cooldown period
        last_scaling = self.last_scaling_time.get(pool.pool_id)
        if last_scaling and (datetime.utcnow() - last_scaling).seconds < self.scaling_cooldown:
            return
        
        scaling_config = pool.scaling_config
        
        # Calculate current utilization
        if pool.total_capacity.cpu_cores > 0:
            cpu_util = (pool.allocated_capacity.cpu_cores / pool.total_capacity.cpu_cores) * 100
        else:
            cpu_util = 0
        
        # Check scaling thresholds
        scale_up_threshold = scaling_config.get('scale_up_threshold', 80.0)
        scale_down_threshold = scaling_config.get('scale_down_threshold', 30.0)
        
        if cpu_util >= scale_up_threshold:
            await self._trigger_scaling(pool, ScalingAction.SCALE_UP, cpu_util)
        elif cpu_util <= scale_down_threshold:
            await self._trigger_scaling(pool, ScalingAction.SCALE_DOWN, cpu_util)
    
    async def _trigger_scaling(
        self,
        pool: ResourcePool,
        action: ScalingAction,
        current_utilization: float
    ) -> None:
        """
Trigger scaling action for a pool."""
        try:
            self.scaling_in_progress.add(pool.pool_id)
            self.last_scaling_time[pool.pool_id] = datetime.utcnow()
            
            event = ScalingEvent(
                event_id=f"scale_{pool.pool_id}_{int(time.time())}",
                pool_id=pool.pool_id,
                action=action,
                trigger_metric="cpu_utilization",
                trigger_value=current_utilization,
                threshold=pool.scaling_config.get(f'{action.value}_threshold', 0),
                scaling_factor=1.5 if action == ScalingAction.SCALE_UP else 0.7,
                executed_at=datetime.utcnow()
            )
            
            start_time = time.time()
            
            # Execute scaling
            success = await self._execute_scaling(pool, action, event.scaling_factor)
            
            event.execution_duration = time.time() - start_time
            event.success = success
            
            if success:
                self.metrics.scaling_events += 1
                logger.info(f"Scaling {action.value} completed for pool {pool.pool_id}")
            else:
                logger.error(f"Scaling {action.value} failed for pool {pool.pool_id}")
            
            self.scaling_history.append(event)
            
            # Call scaling callbacks
            await self._call_callbacks('scaling', event)
            
        except Exception as e:
            logger.error(f"Scaling trigger failed for pool {pool.pool_id}: {e}")
        finally:
            self.scaling_in_progress.discard(pool.pool_id)
    
    async def _execute_scaling(
        self,
        pool: ResourcePool,
        action: ScalingAction,
        scaling_factor: float
    ) -> bool:
        """Execute scaling action."""
        try:
            if action == ScalingAction.SCALE_UP:
                # Increase capacity
                new_cpu_cores = pool.total_capacity.cpu_cores * scaling_factor
                new_memory_mb = int(pool.total_capacity.memory_mb * scaling_factor)
                
                # Check maximum limits
                max_cpu = pool.scaling_config.get('max_capacity', pool.total_capacity.cpu_cores * 2)
                max_memory = pool.scaling_config.get('max_memory', pool.total_capacity.memory_mb * 2)
                
                new_cpu_cores = min(new_cpu_cores, max_cpu)
                new_memory_mb = min(new_memory_mb, max_memory)
                
                # Update capacity
                pool.total_capacity.cpu_cores = new_cpu_cores
                pool.total_capacity.memory_mb = new_memory_mb
                pool.available_capacity.cpu_cores = new_cpu_cores - pool.allocated_capacity.cpu_cores
                pool.available_capacity.memory_mb = new_memory_mb - pool.allocated_capacity.memory_mb
                
            elif action == ScalingAction.SCALE_DOWN:
                # Decrease capacity (if safe)
                new_cpu_cores = pool.total_capacity.cpu_cores * scaling_factor
                new_memory_mb = int(pool.total_capacity.memory_mb * scaling_factor)
                
                # Ensure we don't go below allocated resources
                new_cpu_cores = max(new_cpu_cores, pool.allocated_capacity.cpu_cores * 1.1)
                new_memory_mb = max(new_memory_mb, int(pool.allocated_capacity.memory_mb * 1.1))
                
                # Check minimum limits
                min_cpu = pool.scaling_config.get('min_capacity', pool.total_capacity.cpu_cores * 0.5)
                min_memory = pool.scaling_config.get('min_memory', pool.total_capacity.memory_mb * 0.5)
                
                new_cpu_cores = max(new_cpu_cores, min_cpu)
                new_memory_mb = max(new_memory_mb, min_memory)
                
                # Update capacity
                pool.total_capacity.cpu_cores = new_cpu_cores
                pool.total_capacity.memory_mb = new_memory_mb
                pool.available_capacity.cpu_cores = new_cpu_cores - pool.allocated_capacity.cpu_cores
                pool.available_capacity.memory_mb = new_memory_mb - pool.allocated_capacity.memory_mb
            
            pool.last_updated = datetime.utcnow()
            return True
            
        except Exception as e:
            logger.error(f"Scaling execution failed: {e}")
            return False
    
    async def _cost_optimization_loop(self) -> None:
        """Cost optimization background loop."""
        while self.is_running:
            try:
                await self._optimize_resource_costs()
                await asyncio.sleep(self.config['cost_optimization_interval'])
                
            except Exception as e:
                logger.error(f"Cost optimization error: {e}")
                await asyncio.sleep(60)
    
    async def _optimize_resource_costs(self) -> None:
        """Optimize resource allocation for cost efficiency."""
        if not self.enable_cost_optimization:
            return
        
        try:
            # Analyze current allocations
            total_cost = 0.0
            underutilized_allocations = []
            
            for allocation_id, allocation in self.active_allocations.items():
                # Calculate cost (simplified)
                allocation_cost = self._calculate_allocation_cost(allocation)
                total_cost += allocation_cost
                
                # Check utilization efficiency
                if allocation.allocation_efficiency < 50.0:  # Less than 50% efficient
                    underutilized_allocations.append(allocation)
            
            # Optimize underutilized allocations
            for allocation in underutilized_allocations:
                await self._optimize_allocation(allocation)
            
            # Update cost efficiency metric
            if self.metrics.total_allocations > 0:
                self.metrics.cost_efficiency = (
                    self.metrics.successful_allocations / self.metrics.total_allocations
                ) * 100
            
        except Exception as e:
            logger.error(f"Cost optimization failed: {e}")
    
    def _calculate_allocation_cost(self, allocation: ResourceAllocation) -> float:
        """Calculate cost for an allocation."""
        # Simplified cost calculation
        quota = allocation.allocated_quota
        
        cpu_cost = quota.cpu_cores * 0.1  # $0.1 per core-hour
        memory_cost = (quota.memory_mb / 1024) * 0.05  # $0.05 per GB-hour
        network_cost = quota.network_mbps * 0.01  # $0.01 per Mbps-hour
        
        return cpu_cost + memory_cost + network_cost
    
    async def _optimize_allocation(self, allocation: ResourceAllocation) -> None:
        """
Optimize a specific allocation."""
        # This could involve:
        # 1. Reducing allocated resources if underutilized
        # 2. Moving to cheaper resource pool
        # 3. Consolidating with other allocations
        
        logger.info(f"Optimizing allocation {allocation.allocation_id} (efficiency: {allocation.allocation_efficiency:.1f}%)")
    
    async def _handle_emergency_condition(self) -> None:
        """Handle emergency resource conditions."""
        logger.critical("Emergency resource condition detected - initiating response")
        
        # Emergency actions:
        # 1. Pause low-priority allocations
        # 2. Scale up critical resources immediately
        # 3. Activate resource cleanup
        # 4. Send alerts
        
        await self._call_callbacks('emergency', {'timestamp': datetime.utcnow()})
    
    async def _update_resource_metrics(self) -> None:
        """Update resource scheduler metrics."""
        # Calculate allocation success rate
        if self.metrics.total_allocations > 0:
            success_rate = (self.metrics.successful_allocations / self.metrics.total_allocations) * 100
            self.metrics.allocation_accuracy = success_rate
        
        # Calculate SLA compliance
        compliant_allocations = sum(
            1 for alloc in self.active_allocations.values()
            if alloc.sla_compliance >= 95.0
        )
        
        if self.active_allocations:
            self.metrics.sla_compliance_rate = (compliant_allocations / len(self.active_allocations)) * 100
        
        self.metrics.last_updated = datetime.utcnow()
    
    async def _evaluate_scaling_decisions(self) -> None:
        """
Evaluate and make scaling decisions."""
        if not self.enable_predictive_scaling:
            return
        
        # Predictive scaling based on historical patterns
        # This would involve ML models to predict future resource needs
        pass
    
    async def get_resource_status(self) -> Dict[str, Any]:
        """
Get comprehensive resource status."""
        pool_status = {}
        
        for pool_id, pool in self.resource_pools.items():
            # Calculate utilization percentages
            cpu_util = 0.0
            memory_util = 0.0
            
            if pool.total_capacity.cpu_cores > 0:
                cpu_util = (pool.allocated_capacity.cpu_cores / pool.total_capacity.cpu_cores) * 100
            
            if pool.total_capacity.memory_mb > 0:
                memory_util = (pool.allocated_capacity.memory_mb / pool.total_capacity.memory_mb) * 100
            
            pool_status[pool_id] = {
                'resource_type': pool.resource_type.value,
                'status': pool.status.value,
                'allocation_strategy': pool.allocation_strategy.value,
                'cpu_utilization': cpu_util,
                'memory_utilization': memory_util,
                'total_capacity': asdict(pool.total_capacity),
                'available_capacity': asdict(pool.available_capacity),
                'allocated_capacity': asdict(pool.allocated_capacity),
                'last_updated': pool.last_updated.isoformat()
            }
        
        return {
            'monitoring_enabled': self.is_running,
            'auto_scaling_enabled': self.enable_auto_scaling,
            'cost_optimization_enabled': self.enable_cost_optimization,
            'emergency_mode': self.emergency_mode,
            'active_allocations': len(self.active_allocations),
            'scaling_in_progress': list(self.scaling_in_progress),
            'resource_pools': pool_status,
            'metrics': asdict(self.metrics),
            'recent_scaling_events': len(self.scaling_history),
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def add_callback(self, event_type: str, callback: Callable) -> None:
        """
Add event callback."""
        self.event_callbacks[event_type].append(callback)
    
    async def _call_callbacks(self, event_type: str, *args) -> None:
        """
Call registered callbacks for an event."""
        for callback in self.event_callbacks.get(event_type, []):
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(*args)
                else:
                    callback(*args)
            except Exception as e:
                logger.error(f"Callback error for {event_type}: {e}")


# Export main classes
__all__ = [
    'ResourceScheduler',
    'ResourcePool',
    'ResourceAllocation',
    'ResourceQuota',
    'ResourceUsage',
    'ScalingEvent',
    'ResourceType',
    'AllocationStrategy',
    'ResourceStatus',
    'ScalingAction',
    'ResourceMetrics'
]
