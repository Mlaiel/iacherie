"""
AI Resource Allocator Service - Enterprise AI Resource Management
Ainflue Platform - Microservices Architecture

© FAHED MLAIEL 2024-2025 - CONFIDENTIAL ENTERPRISE MODULE
"""

import asyncio
import time
import logging
import psutil
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import statistics

class ResourceType(Enum):
    """Types of AI resources"""
    CPU = "cpu"
    MEMORY = "memory"
    GPU = "gpu"
    STORAGE = "storage"
    NETWORK = "network"

class AllocationStrategy(Enum):
    """Resource allocation strategies"""
    FAIR_SHARE = "fair_share"
    PRIORITY_BASED = "priority_based"
    WORKLOAD_OPTIMIZED = "workload_optimized"
    COST_OPTIMIZED = "cost_optimized"
    PERFORMANCE_OPTIMIZED = "performance_optimized"

class ResourceStatus(Enum):
    """Resource allocation status"""
    AVAILABLE = "available"
    ALLOCATED = "allocated"
    OVERCOMMITTED = "overcommitted"
    EXHAUSTED = "exhausted"
    MAINTENANCE = "maintenance"

@dataclass
class ResourceRequirement:
    """Resource requirement specification"""
    resource_type: ResourceType
    amount: float
    unit: str
    priority: int  # 1-10, higher is more important
    duration_minutes: Optional[int] = None
    preemptible: bool = False

@dataclass
class ResourceAllocation:
    """Resource allocation record"""
    allocation_id: str
    service_name: str
    model_id: Optional[str]
    requirements: List[ResourceRequirement]
    allocated_resources: Dict[str, float]
    allocation_time: datetime
    duration_minutes: Optional[int]
    priority: int
    status: ResourceStatus
    actual_usage: Dict[str, float]

@dataclass
class ResourcePool:
    """Resource pool configuration"""
    pool_id: str
    resource_type: ResourceType
    total_capacity: float
    available_capacity: float
    allocated_capacity: float
    reserved_capacity: float
    unit: str
    cost_per_unit: float
    nodes: List[str]

class AIResourceAllocator:
    """
    Enterprise AI Resource Allocator Service
    
    Manages intelligent allocation of computational resources (CPU, GPU, memory, storage)
    across AI services with priority-based scheduling, load balancing, cost optimization,
    and automatic scaling for enterprise AI workloads.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.resource_pools = {}
        self.allocations = {}
        self.allocation_history = []
        self.usage_metrics = {}
        self.allocation_strategy = AllocationStrategy.WORKLOAD_OPTIMIZED
        
    async def initialize(self) -> bool:
        """Initialize AI resource allocator"""
        try:
            self.logger.info("Initializing AI Resource Allocator Service...")
            
            # Initialize resource pools
            await self._initialize_resource_pools()
            
            # Setup resource monitoring
            await self._setup_resource_monitoring()
            
            # Start resource optimization task
            self.optimization_task = asyncio.create_task(self._optimize_resource_allocation())
            
            self.logger.info("AI Resource Allocator Service initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize AI Resource Allocator: {e}")
            return False
    
    async def _initialize_resource_pools(self):
        """Initialize resource pools with current system capacity"""
        # Get system resources
        cpu_count = psutil.cpu_count()
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Initialize CPU pool
        self.resource_pools[ResourceType.CPU] = ResourcePool(
            pool_id="cpu_pool_main",
            resource_type=ResourceType.CPU,
            total_capacity=float(cpu_count),
            available_capacity=float(cpu_count),
            allocated_capacity=0.0,
            reserved_capacity=cpu_count * 0.1,  # Reserve 10% for system
            unit="cores",
            cost_per_unit=0.10,  # $0.10 per core-hour
            nodes=["node-1", "node-2", "node-3"]
        )
        
        # Initialize Memory pool
        memory_gb = memory.total / (1024**3)
        self.resource_pools[ResourceType.MEMORY] = ResourcePool(
            pool_id="memory_pool_main",
            resource_type=ResourceType.MEMORY,
            total_capacity=memory_gb,
            available_capacity=memory_gb,
            allocated_capacity=0.0,
            reserved_capacity=memory_gb * 0.15,  # Reserve 15% for system
            unit="GB",
            cost_per_unit=0.05,  # $0.05 per GB-hour
            nodes=["node-1", "node-2", "node-3"]
        )
        
        # Initialize GPU pool (simulated)
        gpu_count = 4  # Simulate 4 GPUs
        self.resource_pools[ResourceType.GPU] = ResourcePool(
            pool_id="gpu_pool_main",
            resource_type=ResourceType.GPU,
            total_capacity=float(gpu_count),
            available_capacity=float(gpu_count),
            allocated_capacity=0.0,
            reserved_capacity=0.0,
            unit="GPUs",
            cost_per_unit=2.50,  # $2.50 per GPU-hour
            nodes=["gpu-node-1", "gpu-node-2"]
        )
        
        # Initialize Storage pool
        storage_gb = disk.total / (1024**3)
        self.resource_pools[ResourceType.STORAGE] = ResourcePool(
            pool_id="storage_pool_main",
            resource_type=ResourceType.STORAGE,
            total_capacity=storage_gb,
            available_capacity=storage_gb,
            allocated_capacity=0.0,
            reserved_capacity=storage_gb * 0.05,  # Reserve 5% for system
            unit="GB",
            cost_per_unit=0.001,  # $0.001 per GB-hour
            nodes=["storage-node-1", "storage-node-2"]
        )
        
        # Initialize Network pool (simulated bandwidth)
        network_gbps = 10.0  # 10 Gbps
        self.resource_pools[ResourceType.NETWORK] = ResourcePool(
            pool_id="network_pool_main",
            resource_type=ResourceType.NETWORK,
            total_capacity=network_gbps,
            available_capacity=network_gbps,
            allocated_capacity=0.0,
            reserved_capacity=network_gbps * 0.1,  # Reserve 10% for overhead
            unit="Gbps",
            cost_per_unit=0.02,  # $0.02 per Gbps-hour
            nodes=["network-node-1", "network-node-2"]
        )
    
    async def _setup_resource_monitoring(self):
        """Setup resource usage monitoring"""
        self.monitoring_interval = 30  # seconds
        self.monitoring_task = asyncio.create_task(self._monitor_resource_usage())
    
    async def _monitor_resource_usage(self):
        """Monitor actual resource usage"""
        try:
            while True:
                # Update actual usage metrics
                await self._update_usage_metrics()
                
                # Check for resource violations
                await self._check_resource_violations()
                
                await asyncio.sleep(self.monitoring_interval)
                
        except asyncio.CancelledError:
            pass
        except Exception as e:
            self.logger.error(f"Resource monitoring error: {e}")
    
    async def _update_usage_metrics(self):
        """Update resource usage metrics"""
        try:
            # Update CPU usage
            cpu_usage = psutil.cpu_percent(interval=1)
            self.usage_metrics[ResourceType.CPU] = {
                'current_usage_percent': cpu_usage,
                'available_capacity': self.resource_pools[ResourceType.CPU].available_capacity,
                'allocated_capacity': self.resource_pools[ResourceType.CPU].allocated_capacity,
                'timestamp': datetime.now()
            }
            
            # Update Memory usage
            memory = psutil.virtual_memory()
            memory_usage_gb = memory.used / (1024**3)
            self.usage_metrics[ResourceType.MEMORY] = {
                'current_usage_gb': memory_usage_gb,
                'current_usage_percent': memory.percent,
                'available_capacity': self.resource_pools[ResourceType.MEMORY].available_capacity,
                'allocated_capacity': self.resource_pools[ResourceType.MEMORY].allocated_capacity,
                'timestamp': datetime.now()
            }
            
            # Update GPU usage (simulated)
            gpu_usage = await self._get_gpu_usage()
            self.usage_metrics[ResourceType.GPU] = {
                'current_usage_percent': gpu_usage['utilization'],
                'memory_usage_percent': gpu_usage['memory_usage'],
                'available_capacity': self.resource_pools[ResourceType.GPU].available_capacity,
                'allocated_capacity': self.resource_pools[ResourceType.GPU].allocated_capacity,
                'timestamp': datetime.now()
            }
            
            # Update Storage usage
            disk = psutil.disk_usage('/')
            storage_usage_gb = disk.used / (1024**3)
            self.usage_metrics[ResourceType.STORAGE] = {
                'current_usage_gb': storage_usage_gb,
                'current_usage_percent': disk.percent,
                'available_capacity': self.resource_pools[ResourceType.STORAGE].available_capacity,
                'allocated_capacity': self.resource_pools[ResourceType.STORAGE].allocated_capacity,
                'timestamp': datetime.now()
            }
            
            # Update Network usage (simulated)
            network_stats = psutil.net_io_counters()
            network_usage_mbps = (network_stats.bytes_sent + network_stats.bytes_recv) / (1024**2) / 8  # Convert to Mbps
            self.usage_metrics[ResourceType.NETWORK] = {
                'current_usage_mbps': network_usage_mbps,
                'current_usage_percent': min(network_usage_mbps / (self.resource_pools[ResourceType.NETWORK].total_capacity * 1000) * 100, 100),
                'available_capacity': self.resource_pools[ResourceType.NETWORK].available_capacity,
                'allocated_capacity': self.resource_pools[ResourceType.NETWORK].allocated_capacity,
                'timestamp': datetime.now()
            }
            
        except Exception as e:
            self.logger.error(f"Error updating usage metrics: {e}")
    
    async def _get_gpu_usage(self) -> Dict[str, float]:
        """Get GPU usage metrics (simulated)"""
        # In production, would use nvidia-ml-py or similar
        return {
            'utilization': 45.5,  # GPU utilization percentage
            'memory_usage': 65.2,  # GPU memory usage percentage
            'temperature': 72,     # GPU temperature in Celsius
            'power_usage': 185     # Power usage in watts
        }
    
    async def _check_resource_violations(self):
        """Check for resource allocation violations"""
        violations = []
        
        for resource_type, pool in self.resource_pools.items():
            usage_metric = self.usage_metrics.get(resource_type)
            if not usage_metric:
                continue
            
            # Check overallocation
            if pool.allocated_capacity > pool.total_capacity - pool.reserved_capacity:
                violations.append(f"{resource_type.value} pool overallocated")
                pool.status = ResourceStatus.OVERCOMMITTED
            
            # Check high utilization
            current_usage_percent = usage_metric.get('current_usage_percent', 0)
            if current_usage_percent > 90:
                violations.append(f"{resource_type.value} usage critical: {current_usage_percent:.1f}%")
            
            # Check available capacity
            if pool.available_capacity < pool.total_capacity * 0.1:
                violations.append(f"{resource_type.value} capacity low")
                pool.status = ResourceStatus.EXHAUSTED
        
        if violations:
            self.logger.warning(f"Resource violations detected: {violations}")
            await self._handle_resource_violations(violations)
    
    async def _handle_resource_violations(self, violations: List[str]):
        """Handle resource allocation violations"""
        # Implement violation handling strategies
        for violation in violations:
            if "overallocated" in violation:
                await self._rebalance_allocations()
            elif "usage critical" in violation:
                await self._trigger_scaling()
            elif "capacity low" in violation:
                await self._optimize_allocations()
    
    async def allocate_resources(self, service_name: str, requirements: List[ResourceRequirement], 
                               model_id: Optional[str] = None) -> ResourceAllocation:
        """
        Allocate resources for AI service
        
        Args:
            service_name: Name of requesting service
            requirements: List of resource requirements
            model_id: Optional model identifier
            
        Returns:
            ResourceAllocation: Allocation result
        """
        allocation_id = f"alloc_{int(time.time())}_{service_name}"
        
        try:
            self.logger.info(f"Allocating resources for {service_name}: {len(requirements)} requirements")
            
            # Validate requirements
            validation_result = await self._validate_requirements(requirements)
            if not validation_result['valid']:
                raise ValueError(f"Invalid requirements: {validation_result['errors']}")
            
            # Check resource availability
            availability_check = await self._check_resource_availability(requirements)
            if not availability_check['available']:
                # Try optimization strategies
                optimization_result = await self._optimize_for_allocation(requirements)
                if not optimization_result['success']:
                    raise ResourceError(f"Insufficient resources: {availability_check['missing']}")
            
            # Calculate optimal allocation
            allocation_plan = await self._calculate_allocation_plan(requirements)
            
            # Execute allocation
            allocated_resources = await self._execute_allocation(allocation_plan)
            
            # Update resource pools
            await self._update_resource_pools(allocated_resources)
            
            # Calculate priority
            priority = max(req.priority for req in requirements)
            
            # Create allocation record
            allocation = ResourceAllocation(
                allocation_id=allocation_id,
                service_name=service_name,
                model_id=model_id,
                requirements=requirements,
                allocated_resources=allocated_resources,
                allocation_time=datetime.now(),
                duration_minutes=max((req.duration_minutes or 60) for req in requirements),
                priority=priority,
                status=ResourceStatus.ALLOCATED,
                actual_usage={}
            )
            
            self.allocations[allocation_id] = allocation
            self.allocation_history.append(allocation)
            
            self.logger.info(f"Resources allocated successfully: {allocation_id}")
            return allocation
            
        except Exception as e:
            self.logger.error(f"Resource allocation failed for {service_name}: {e}")
            raise
    
    async def _validate_requirements(self, requirements: List[ResourceRequirement]) -> Dict[str, Any]:
        """Validate resource requirements"""
        errors = []
        
        for req in requirements:
            # Check if resource type is supported
            if req.resource_type not in self.resource_pools:
                errors.append(f"Unsupported resource type: {req.resource_type}")
            
            # Check if amount is positive
            if req.amount <= 0:
                errors.append(f"Resource amount must be positive: {req.amount}")
            
            # Check priority range
            if not 1 <= req.priority <= 10:
                errors.append(f"Priority must be between 1-10: {req.priority}")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
    
    async def _check_resource_availability(self, requirements: List[ResourceRequirement]) -> Dict[str, Any]:
        """Check if resources are available"""
        missing_resources = []
        
        for req in requirements:
            pool = self.resource_pools[req.resource_type]
            available = pool.available_capacity - pool.reserved_capacity
            
            if req.amount > available:
                missing_resources.append({
                    'resource_type': req.resource_type.value,
                    'required': req.amount,
                    'available': available,
                    'deficit': req.amount - available
                })
        
        return {
            'available': len(missing_resources) == 0,
            'missing': missing_resources
        }
    
    async def _optimize_for_allocation(self, requirements: List[ResourceRequirement]) -> Dict[str, Any]:
        """Try to optimize allocations to make room for new requirements"""
        try:
            # Try to free up resources by optimizing current allocations
            freed_resources = await self._free_underutilized_resources()
            
            # Try to preempt lower priority allocations
            preempted_resources = await self._preempt_lower_priority_allocations(requirements)
            
            return {
                'success': True,
                'freed_resources': freed_resources,
                'preempted_resources': preempted_resources
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _free_underutilized_resources(self) -> Dict[str, float]:
        """Free up underutilized resources"""
        freed_resources = {}
        
        for allocation_id, allocation in self.allocations.items():
            # Check if allocation is underutilized
            utilization = await self._calculate_allocation_utilization(allocation)
            
            if utilization['avg_utilization'] < 0.3:  # Less than 30% utilized
                # Reduce allocation
                for resource_type, amount in allocation.allocated_resources.items():
                    reduction = amount * 0.5  # Reduce by 50%
                    freed_resources[resource_type] = freed_resources.get(resource_type, 0) + reduction
                    allocation.allocated_resources[resource_type] -= reduction
                    
                    # Update pool
                    pool = self.resource_pools[ResourceType(resource_type)]
                    pool.available_capacity += reduction
                    pool.allocated_capacity -= reduction
        
        return freed_resources
    
    async def _preempt_lower_priority_allocations(self, requirements: List[ResourceRequirement]) -> Dict[str, float]:
        """Preempt lower priority allocations"""
        preempted_resources = {}
        max_priority = max(req.priority for req in requirements)
        
        # Find allocations with lower priority and preemptible flag
        preemptible_allocations = [
            alloc for alloc in self.allocations.values()
            if alloc.priority < max_priority and 
            any(req.preemptible for req in alloc.requirements)
        ]
        
        # Sort by priority (lowest first)
        preemptible_allocations.sort(key=lambda x: x.priority)
        
        for allocation in preemptible_allocations:
            # Preempt allocation
            await self.deallocate_resources(allocation.allocation_id)
            
            for resource_type, amount in allocation.allocated_resources.items():
                preempted_resources[resource_type] = preempted_resources.get(resource_type, 0) + amount
        
        return preempted_resources
    
    async def _calculate_allocation_plan(self, requirements: List[ResourceRequirement]) -> Dict[str, Any]:
        """Calculate optimal allocation plan"""
        allocation_plan = {}
        
        for req in requirements:
            pool = self.resource_pools[req.resource_type]
            
            # Calculate allocation based on strategy
            if self.allocation_strategy == AllocationStrategy.FAIR_SHARE:
                allocated_amount = min(req.amount, pool.available_capacity / len(requirements))
            elif self.allocation_strategy == AllocationStrategy.PRIORITY_BASED:
                # Allocate based on priority weight
                priority_weight = req.priority / 10.0
                allocated_amount = min(req.amount, pool.available_capacity * priority_weight)
            else:  # WORKLOAD_OPTIMIZED (default)
                allocated_amount = min(req.amount, pool.available_capacity)
            
            allocation_plan[req.resource_type.value] = {
                'amount': allocated_amount,
                'unit': pool.unit,
                'cost_per_hour': allocated_amount * pool.cost_per_unit,
                'nodes': pool.nodes[:min(len(pool.nodes), max(1, int(allocated_amount)))]
            }
        
        return allocation_plan
    
    async def _execute_allocation(self, allocation_plan: Dict[str, Any]) -> Dict[str, float]:
        """Execute resource allocation"""
        allocated_resources = {}
        
        for resource_type_str, plan in allocation_plan.items():
            resource_type = ResourceType(resource_type_str)
            amount = plan['amount']
            
            # Update pool allocation
            pool = self.resource_pools[resource_type]
            pool.allocated_capacity += amount
            pool.available_capacity -= amount
            
            allocated_resources[resource_type_str] = amount
            
            self.logger.info(f"Allocated {amount} {plan['unit']} of {resource_type_str}")
        
        return allocated_resources
    
    async def _update_resource_pools(self, allocated_resources: Dict[str, float]):
        """Update resource pool states after allocation"""
        for resource_type_str, amount in allocated_resources.items():
            resource_type = ResourceType(resource_type_str)
            pool = self.resource_pools[resource_type]
            
            # Update pool status based on availability
            utilization = (pool.allocated_capacity / pool.total_capacity) * 100
            
            if utilization > 95:
                pool.status = ResourceStatus.EXHAUSTED
            elif utilization > 80:
                pool.status = ResourceStatus.OVERCOMMITTED
            else:
                pool.status = ResourceStatus.AVAILABLE
    
    async def deallocate_resources(self, allocation_id: str) -> bool:
        """
        Deallocate resources
        
        Args:
            allocation_id: Allocation identifier
            
        Returns:
            bool: Success status
        """
        try:
            if allocation_id not in self.allocations:
                raise ValueError(f"Allocation not found: {allocation_id}")
            
            allocation = self.allocations[allocation_id]
            
            self.logger.info(f"Deallocating resources: {allocation_id}")
            
            # Return resources to pools
            for resource_type_str, amount in allocation.allocated_resources.items():
                resource_type = ResourceType(resource_type_str)
                pool = self.resource_pools[resource_type]
                
                pool.allocated_capacity -= amount
                pool.available_capacity += amount
                
                # Update pool status
                utilization = (pool.allocated_capacity / pool.total_capacity) * 100
                if utilization < 80:
                    pool.status = ResourceStatus.AVAILABLE
            
            # Update allocation status
            allocation.status = ResourceStatus.AVAILABLE
            
            # Remove from active allocations
            del self.allocations[allocation_id]
            
            self.logger.info(f"Resources deallocated successfully: {allocation_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Resource deallocation failed: {e}")
            raise
    
    async def _optimize_resource_allocation(self):
        """Continuous resource allocation optimization"""
        try:
            while True:
                await asyncio.sleep(300)  # Optimize every 5 minutes
                
                # Rebalance allocations
                await self._rebalance_allocations()
                
                # Cleanup expired allocations
                await self._cleanup_expired_allocations()
                
                # Optimize for cost
                await self._optimize_for_cost()
                
        except asyncio.CancelledError:
            pass
        except Exception as e:
            self.logger.error(f"Resource optimization error: {e}")
    
    async def _rebalance_allocations(self):
        """Rebalance resource allocations"""
        try:
            # Identify overcommitted pools
            overcommitted_pools = [
                pool for pool in self.resource_pools.values()
                if pool.allocated_capacity > pool.total_capacity - pool.reserved_capacity
            ]
            
            if not overcommitted_pools:
                return
            
            self.logger.info(f"Rebalancing {len(overcommitted_pools)} overcommitted pools")
            
            # Implement rebalancing strategy
            for pool in overcommitted_pools:
                excess = pool.allocated_capacity - (pool.total_capacity - pool.reserved_capacity)
                
                # Find allocations to reduce
                pool_allocations = [
                    alloc for alloc in self.allocations.values()
                    if pool.resource_type.value in alloc.allocated_resources
                ]
                
                # Sort by utilization (lowest first)
                pool_allocations.sort(key=lambda x: self._get_allocation_utilization_score(x))
                
                # Reduce allocations until excess is resolved
                remaining_excess = excess
                for allocation in pool_allocations:
                    if remaining_excess <= 0:
                        break
                    
                    current_amount = allocation.allocated_resources[pool.resource_type.value]
                    reduction = min(current_amount * 0.2, remaining_excess)  # Reduce by max 20%
                    
                    allocation.allocated_resources[pool.resource_type.value] -= reduction
                    pool.allocated_capacity -= reduction
                    pool.available_capacity += reduction
                    remaining_excess -= reduction
            
        except Exception as e:
            self.logger.error(f"Rebalancing error: {e}")
    
    def _get_allocation_utilization_score(self, allocation: ResourceAllocation) -> float:
        """Get utilization score for allocation (lower means less utilized)"""
        # Simulate utilization calculation
        return 0.6  # Return mock utilization score
    
    async def _cleanup_expired_allocations(self):
        """Cleanup expired allocations"""
        current_time = datetime.now()
        expired_allocations = []
        
        for allocation_id, allocation in self.allocations.items():
            if allocation.duration_minutes:
                expiry_time = allocation.allocation_time + timedelta(minutes=allocation.duration_minutes)
                if current_time > expiry_time:
                    expired_allocations.append(allocation_id)
        
        for allocation_id in expired_allocations:
            await self.deallocate_resources(allocation_id)
            self.logger.info(f"Cleaned up expired allocation: {allocation_id}")
    
    async def _optimize_for_cost(self):
        """Optimize allocations for cost efficiency"""
        try:
            # Calculate current cost
            total_cost = self._calculate_total_cost()
            
            # Find cost optimization opportunities
            optimizations = await self._find_cost_optimizations()
            
            if optimizations:
                self.logger.info(f"Found {len(optimizations)} cost optimization opportunities")
                
                for optimization in optimizations:
                    await self._apply_cost_optimization(optimization)
            
        except Exception as e:
            self.logger.error(f"Cost optimization error: {e}")
    
    def _calculate_total_cost(self) -> float:
        """Calculate total current allocation cost"""
        total_cost = 0.0
        
        for allocation in self.allocations.values():
            for resource_type_str, amount in allocation.allocated_resources.items():
                resource_type = ResourceType(resource_type_str)
                pool = self.resource_pools[resource_type]
                total_cost += amount * pool.cost_per_unit
        
        return total_cost
    
    async def _find_cost_optimizations(self) -> List[Dict[str, Any]]:
        """Find cost optimization opportunities"""
        optimizations = []
        
        # Find overprovisioned allocations
        for allocation in self.allocations.values():
            utilization = await self._calculate_allocation_utilization(allocation)
            
            if utilization['avg_utilization'] < 0.5:  # Less than 50% utilized
                potential_savings = 0.0
                for resource_type_str, amount in allocation.allocated_resources.items():
                    resource_type = ResourceType(resource_type_str)
                    pool = self.resource_pools[resource_type]
                    reduction = amount * 0.3  # 30% reduction
                    potential_savings += reduction * pool.cost_per_unit
                
                optimizations.append({
                    'type': 'downsize',
                    'allocation_id': allocation.allocation_id,
                    'potential_savings': potential_savings,
                    'reduction_factor': 0.3
                })
        
        return optimizations
    
    async def _apply_cost_optimization(self, optimization: Dict[str, Any]):
        """Apply cost optimization"""
        if optimization['type'] == 'downsize':
            allocation_id = optimization['allocation_id']
            reduction_factor = optimization['reduction_factor']
            
            allocation = self.allocations[allocation_id]
            
            for resource_type_str, amount in allocation.allocated_resources.items():
                resource_type = ResourceType(resource_type_str)
                pool = self.resource_pools[resource_type]
                
                reduction = amount * reduction_factor
                allocation.allocated_resources[resource_type_str] -= reduction
                pool.allocated_capacity -= reduction
                pool.available_capacity += reduction
    
    async def _calculate_allocation_utilization(self, allocation: ResourceAllocation) -> Dict[str, float]:
        """Calculate allocation utilization"""
        # Simulate utilization calculation
        return {
            'avg_utilization': 0.65,
            'cpu_utilization': 0.70,
            'memory_utilization': 0.60,
            'gpu_utilization': 0.65
        }
    
    async def _trigger_scaling(self):
        """Trigger auto-scaling when resources are constrained"""
        self.logger.info("Triggering auto-scaling due to resource constraints")
        
        # Simulate scaling by increasing capacity
        for resource_type, pool in self.resource_pools.items():
            if pool.status in [ResourceStatus.OVERCOMMITTED, ResourceStatus.EXHAUSTED]:
                # Increase capacity by 20%
                increase = pool.total_capacity * 0.2
                pool.total_capacity += increase
                pool.available_capacity += increase
                pool.status = ResourceStatus.AVAILABLE
                
                self.logger.info(f"Scaled {resource_type.value} capacity by {increase} {pool.unit}")
    
    def get_resource_status(self) -> Dict[str, Any]:
        """Get current resource status"""
        status = {}
        
        for resource_type, pool in self.resource_pools.items():
            usage_metric = self.usage_metrics.get(resource_type, {})
            
            status[resource_type.value] = {
                'total_capacity': pool.total_capacity,
                'available_capacity': pool.available_capacity,
                'allocated_capacity': pool.allocated_capacity,
                'reserved_capacity': pool.reserved_capacity,
                'utilization_percent': (pool.allocated_capacity / pool.total_capacity) * 100,
                'current_usage_percent': usage_metric.get('current_usage_percent', 0),
                'status': pool.status.value,
                'unit': pool.unit,
                'cost_per_unit': pool.cost_per_unit,
                'nodes': pool.nodes
            }
        
        return status
    
    def get_allocation_status(self, allocation_id: Optional[str] = None) -> Dict[str, Any]:
        """Get allocation status"""
        if allocation_id:
            allocation = self.allocations.get(allocation_id)
            if allocation:
                return asdict(allocation)
            return {}
        
        return {alloc_id: asdict(alloc) for alloc_id, alloc in self.allocations.items()}
    
    def get_allocation_history(self, service_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get allocation history"""
        if service_name:
            return [
                asdict(alloc) for alloc in self.allocation_history 
                if alloc.service_name == service_name
            ]
        
        return [asdict(alloc) for alloc in self.allocation_history]
    
    async def generate_resource_report(self) -> Dict[str, Any]:
        """Generate comprehensive resource utilization report"""
        total_allocations = len(self.allocations)
        total_cost = self._calculate_total_cost()
        
        # Calculate efficiency metrics
        efficiency_metrics = {}
        for resource_type, pool in self.resource_pools.items():
            efficiency = (pool.allocated_capacity / pool.total_capacity) * 100
            efficiency_metrics[resource_type.value] = efficiency
        
        avg_efficiency = sum(efficiency_metrics.values()) / len(efficiency_metrics) if efficiency_metrics else 0
        
        return {
            'summary': {
                'total_allocations': total_allocations,
                'total_cost_per_hour': round(total_cost, 2),
                'average_efficiency_percent': round(avg_efficiency, 1),
                'allocation_strategy': self.allocation_strategy.value
            },
            'resource_pools': self.get_resource_status(),
            'efficiency_metrics': efficiency_metrics,
            'cost_breakdown': {
                resource_type.value: pool.allocated_capacity * pool.cost_per_unit
                for resource_type, pool in self.resource_pools.items()
            },
            'recommendations': self._generate_resource_recommendations(),
            'generated_at': datetime.now().isoformat()
        }
    
    def _generate_resource_recommendations(self) -> List[str]:
        """Generate resource optimization recommendations"""
        recommendations = []
        
        # Check for overcommitted resources
        overcommitted = [
            resource_type.value for resource_type, pool in self.resource_pools.items()
            if pool.allocated_capacity > pool.total_capacity - pool.reserved_capacity
        ]
        
        if overcommitted:
            recommendations.append(f"Scale up overcommitted resources: {', '.join(overcommitted)}")
        
        # Check for underutilized resources
        underutilized = [
            resource_type.value for resource_type, pool in self.resource_pools.items()
            if (pool.allocated_capacity / pool.total_capacity) < 0.3
        ]
        
        if underutilized:
            recommendations.append(f"Consider scaling down underutilized resources: {', '.join(underutilized)}")
        
        # Check cost optimization
        total_cost = self._calculate_total_cost()
        if total_cost > 100:  # $100/hour threshold
            recommendations.append("Review allocations for cost optimization opportunities")
        
        return recommendations or ["Resource allocation is well optimized"]

class ResourceError(Exception):
    """Resource allocation error"""
    pass

# Service instance
ai_resource_allocator = AIResourceAllocator()