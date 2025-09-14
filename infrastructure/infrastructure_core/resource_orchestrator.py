"""
Resource Orchestrator - Enterprise Resource Management and Allocation
© 2025 Fahed Mlaiel. All rights reserved.

Advanced resource orchestration for Ainflue creator platform with intelligent
resource allocation, optimization, and multi-cloud resource management.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta
import json
import uuid

logger = logging.getLogger(__name__)


class ResourceType(Enum):
    """Resource types"""
    CPU = "cpu"
    MEMORY = "memory"
    STORAGE = "storage"
    GPU = "gpu"
    NETWORK = "network"
    DATABASE = "database"


class ResourceState(Enum):
    """Resource states"""
    AVAILABLE = "available"
    ALLOCATED = "allocated"
    RESERVED = "reserved"
    MAINTENANCE = "maintenance"
    FAILED = "failed"


@dataclass
class ResourcePool:
    """Resource pool definition"""
    pool_id: str
    name: str
    resource_type: ResourceType
    total_capacity: float
    available_capacity: float
    allocated_capacity: float
    reserved_capacity: float
    region: str
    cost_per_unit: float
    metadata: Dict[str, Any]


@dataclass
class ResourceAllocation:
    """Resource allocation information"""
    allocation_id: str
    service_id: str
    resource_type: ResourceType
    amount: float
    pool_id: str
    allocation_time: datetime
    expiry_time: Optional[datetime]
    priority: int
    metadata: Dict[str, Any]


class ResourceOrchestrator:
    """
    Enterprise resource orchestration system for Ainflue platform.
    
    Provides:
    - Intelligent resource allocation and scheduling
    - Multi-cloud resource optimization
    - Cost-aware resource management
    - Auto-scaling resource pools
    - Creator workload specific allocations
    - Resource efficiency monitoring
    """
    
    def __init__(self):
        self.resource_pools = {}
        self.allocations = {}
        self.allocation_history = []
        self.optimization_policies = {}
        
        # Ainflue-specific resource configuration
        self.ainflue_resources = self._initialize_ainflue_resources()
        
        # Resource orchestration settings
        self.orchestration_config = {
            'allocation_timeout_seconds': 300,
            'auto_optimization_enabled': True,
            'cost_optimization_threshold': 0.8,
            'resource_utilization_target': 0.75,
            'multi_cloud_enabled': True
        }
        
        logger.info("Resource orchestrator initialized for Ainflue platform")
    
    def _initialize_ainflue_resources(self) -> Dict[str, ResourcePool]:
        """Initialize Ainflue-specific resource pools"""
        
        pools = {}
        
        # CPU Pools for different workloads
        pools['cpu-creator-workloads'] = ResourcePool(
            pool_id="cpu-creator-workloads",
            name="CPU Pool for Creator Workloads",
            resource_type=ResourceType.CPU,
            total_capacity=1000.0,  # 1000 CPU cores
            available_capacity=700.0,
            allocated_capacity=250.0,
            reserved_capacity=50.0,
            region="us-west-2",
            cost_per_unit=0.05,  # $0.05 per core-hour
            metadata={
                'workload_type': 'creator_processing',
                'scaling_enabled': True,
                'priority': 'high'
            }
        )
        
        pools['cpu-ai-processing'] = ResourcePool(
            pool_id="cpu-ai-processing",
            name="CPU Pool for AI Processing",
            resource_type=ResourceType.CPU,
            total_capacity=500.0,
            available_capacity=200.0,
            allocated_capacity=250.0,
            reserved_capacity=50.0,
            region="us-west-2",
            cost_per_unit=0.08,  # Higher cost for AI workloads
            metadata={
                'workload_type': 'ai_processing',
                'scaling_enabled': True,
                'priority': 'critical'
            }
        )
        
        # Memory Pools
        pools['memory-high-performance'] = ResourcePool(
            pool_id="memory-high-performance",
            name="High Performance Memory Pool",
            resource_type=ResourceType.MEMORY,
            total_capacity=10000.0,  # 10TB
            available_capacity=6000.0,
            allocated_capacity=3500.0,
            reserved_capacity=500.0,
            region="us-west-2",
            cost_per_unit=0.001,  # $0.001 per GB-hour
            metadata={
                'memory_type': 'high_performance',
                'scaling_enabled': True,
                'priority': 'high'
            }
        )
        
        # GPU Pools for AI/ML workloads
        pools['gpu-v100-cluster'] = ResourcePool(
            pool_id="gpu-v100-cluster",
            name="NVIDIA V100 GPU Cluster",
            resource_type=ResourceType.GPU,
            total_capacity=50.0,  # 50 GPUs
            available_capacity=20.0,
            allocated_capacity=25.0,
            reserved_capacity=5.0,
            region="us-west-2",
            cost_per_unit=2.50,  # $2.50 per GPU-hour
            metadata={
                'gpu_type': 'v100',
                'memory_per_gpu': '32GB',
                'ai_optimized': True,
                'priority': 'critical'
            }
        )
        
        pools['gpu-a100-cluster'] = ResourcePool(
            pool_id="gpu-a100-cluster",
            name="NVIDIA A100 GPU Cluster",
            resource_type=ResourceType.GPU,
            total_capacity=20.0,  # 20 A100 GPUs
            available_capacity=8.0,
            allocated_capacity=10.0,
            reserved_capacity=2.0,
            region="us-west-2",
            cost_per_unit=4.00,  # $4.00 per GPU-hour
            metadata={
                'gpu_type': 'a100',
                'memory_per_gpu': '80GB',
                'ai_optimized': True,
                'priority': 'critical'
            }
        )
        
        # Storage Pools
        pools['storage-ssd-high-iops'] = ResourcePool(
            pool_id="storage-ssd-high-iops",
            name="High IOPS SSD Storage",
            resource_type=ResourceType.STORAGE,
            total_capacity=50000.0,  # 50TB
            available_capacity=30000.0,
            allocated_capacity=18000.0,
            reserved_capacity=2000.0,
            region="us-west-2",
            cost_per_unit=0.0002,  # $0.0002 per GB-hour
            metadata={
                'storage_type': 'ssd',
                'iops': 10000,
                'creator_content': True,
                'priority': 'high'
            }
        )
        
        # Database Resources
        pools['database-primary-cluster'] = ResourcePool(
            pool_id="database-primary-cluster",
            name="Primary Database Cluster",
            resource_type=ResourceType.DATABASE,
            total_capacity=100.0,  # 100 connection units
            available_capacity=60.0,
            allocated_capacity=35.0,
            reserved_capacity=5.0,
            region="us-west-2",
            cost_per_unit=0.10,  # $0.10 per connection-hour
            metadata={
                'database_type': 'postgresql',
                'cluster_size': 3,
                'high_availability': True,
                'priority': 'critical'
            }
        )
        
        self.resource_pools = pools
        
        logger.info(f"Initialized {len(pools)} resource pools for Ainflue")
        return pools
    
    async def allocate_resources(
        self,
        service_id: str,
        resource_requirements: Dict[str, float],
        priority: int = 5,
        duration_hours: Optional[float] = None
    ) -> Dict[str, ResourceAllocation]:
        """Allocate resources for a service"""
        
        logger.info(f"Allocating resources for service: {service_id}")
        
        allocations = {}
        
        try:
            for resource_type_str, amount in resource_requirements.items():
                resource_type = ResourceType(resource_type_str)
                
                # Find best pool for resource
                pool = await self._find_optimal_pool(resource_type, amount, priority)
                
                if not pool:
                    raise Exception(f"No available pool for {resource_type_str}: {amount}")
                
                # Create allocation
                allocation = await self._create_allocation(
                    service_id=service_id,
                    resource_type=resource_type,
                    amount=amount,
                    pool_id=pool.pool_id,
                    priority=priority,
                    duration_hours=duration_hours
                )
                
                allocations[resource_type_str] = allocation
                
                # Update pool capacity
                pool.allocated_capacity += amount
                pool.available_capacity -= amount
            
            logger.info(f"Successfully allocated {len(allocations)} resources for {service_id}")
            return allocations
            
        except Exception as e:
            # Rollback any successful allocations
            await self._rollback_allocations(list(allocations.values()))
            logger.error(f"Resource allocation failed for {service_id}: {e}")
            raise
    
    async def _find_optimal_pool(
        self,
        resource_type: ResourceType,
        amount: float,
        priority: int
    ) -> Optional[ResourcePool]:
        """Find optimal resource pool for allocation"""
        
        # Filter pools by resource type
        candidate_pools = [
            pool for pool in self.resource_pools.values()
            if pool.resource_type == resource_type and pool.available_capacity >= amount
        ]
        
        if not candidate_pools:
            return None
        
        # Score pools based on multiple factors
        scored_pools = []
        for pool in candidate_pools:
            score = await self._calculate_pool_score(pool, amount, priority)
            scored_pools.append((score, pool))
        
        # Return pool with highest score
        scored_pools.sort(key=lambda x: x[0], reverse=True)
        return scored_pools[0][1] if scored_pools else None
    
    async def _calculate_pool_score(
        self,
        pool: ResourcePool,
        amount: float,
        priority: int
    ) -> float:
        """Calculate score for pool selection"""
        
        score = 0.0
        
        # Availability score (higher available capacity = better)
        availability_ratio = pool.available_capacity / pool.total_capacity
        score += availability_ratio * 40
        
        # Cost efficiency score (lower cost = better)
        max_cost = 10.0  # Assume max cost per unit
        cost_efficiency = (max_cost - pool.cost_per_unit) / max_cost
        score += cost_efficiency * 30
        
        # Utilization score (prefer balanced utilization)
        current_utilization = (pool.allocated_capacity / pool.total_capacity)
        target_utilization = self.orchestration_config['resource_utilization_target']
        
        if current_utilization < target_utilization:
            utilization_score = (target_utilization - current_utilization) / target_utilization
        else:
            utilization_score = 0
        
        score += utilization_score * 20
        
        # Priority matching score
        pool_priority = pool.metadata.get('priority', 'medium')
        priority_scores = {'low': 1, 'medium': 5, 'high': 8, 'critical': 10}
        
        if priority >= 8 and pool_priority in ['high', 'critical']:
            score += 10
        elif priority >= 5 and pool_priority in ['medium', 'high', 'critical']:
            score += 5
        
        return score
    
    async def _create_allocation(
        self,
        service_id: str,
        resource_type: ResourceType,
        amount: float,
        pool_id: str,
        priority: int,
        duration_hours: Optional[float]
    ) -> ResourceAllocation:
        """Create resource allocation"""
        
        allocation_id = str(uuid.uuid4())
        allocation_time = datetime.utcnow()
        expiry_time = None
        
        if duration_hours:
            expiry_time = allocation_time + timedelta(hours=duration_hours)
        
        allocation = ResourceAllocation(
            allocation_id=allocation_id,
            service_id=service_id,
            resource_type=resource_type,
            amount=amount,
            pool_id=pool_id,
            allocation_time=allocation_time,
            expiry_time=expiry_time,
            priority=priority,
            metadata={
                'created_by': 'resource_orchestrator',
                'allocation_reason': 'service_deployment'
            }
        )
        
        self.allocations[allocation_id] = allocation
        self.allocation_history.append(allocation)
        
        logger.info(f"Created allocation: {allocation_id} for {service_id}")
        return allocation
    
    async def _rollback_allocations(self, allocations: List[ResourceAllocation]):
        """Rollback resource allocations"""
        
        for allocation in allocations:
            await self.deallocate_resources(allocation.allocation_id)
    
    async def deallocate_resources(self, allocation_id: str) -> bool:
        """Deallocate resources"""
        
        if allocation_id not in self.allocations:
            return False
        
        allocation = self.allocations[allocation_id]
        pool = self.resource_pools.get(allocation.pool_id)
        
        if pool:
            # Return capacity to pool
            pool.allocated_capacity -= allocation.amount
            pool.available_capacity += allocation.amount
        
        # Remove allocation
        del self.allocations[allocation_id]
        
        logger.info(f"Deallocated resources: {allocation_id}")
        return True
    
    async def optimize_resource_allocation(self) -> Dict[str, Any]:
        """Optimize current resource allocation"""
        
        logger.info("Starting resource allocation optimization")
        
        optimization_results = {
            'optimizations_applied': 0,
            'cost_savings': 0.0,
            'efficiency_improvements': [],
            'recommendations': []
        }
        
        # Analyze current allocations
        for pool in self.resource_pools.values():
            utilization = pool.allocated_capacity / pool.total_capacity
            
            # Check for underutilized pools
            if utilization < 0.3:
                optimization_results['recommendations'].append({
                    'type': 'scale_down',
                    'pool_id': pool.pool_id,
                    'current_utilization': utilization,
                    'recommended_action': 'Consider scaling down pool capacity'
                })
            
            # Check for overutilized pools
            elif utilization > 0.9:
                optimization_results['recommendations'].append({
                    'type': 'scale_up',
                    'pool_id': pool.pool_id,
                    'current_utilization': utilization,
                    'recommended_action': 'Consider scaling up pool capacity'
                })
        
        # Optimize cost by moving workloads to cheaper pools
        cost_optimizations = await self._optimize_cost_allocation()
        optimization_results['cost_savings'] = cost_optimizations['savings']
        optimization_results['optimizations_applied'] += cost_optimizations['moves']
        
        # Optimize performance by balancing loads
        performance_optimizations = await self._optimize_performance_allocation()
        optimization_results['efficiency_improvements'] = performance_optimizations['improvements']
        optimization_results['optimizations_applied'] += performance_optimizations['moves']
        
        logger.info(f"Optimization completed: {optimization_results['optimizations_applied']} optimizations applied")
        return optimization_results
    
    async def _optimize_cost_allocation(self) -> Dict[str, Any]:
        """Optimize allocations for cost efficiency"""
        
        savings = 0.0
        moves = 0
        
        # Group allocations by resource type
        resource_groups = {}
        for allocation in self.allocations.values():
            resource_type = allocation.resource_type
            if resource_type not in resource_groups:
                resource_groups[resource_type] = []
            resource_groups[resource_type].append(allocation)
        
        # For each resource type, find cost optimization opportunities
        for resource_type, allocations in resource_groups.items():
            # Find pools with different costs for same resource type
            pools_by_cost = sorted(
                [p for p in self.resource_pools.values() if p.resource_type == resource_type],
                key=lambda p: p.cost_per_unit
            )
            
            if len(pools_by_cost) < 2:
                continue
            
            # Try to move allocations from expensive to cheaper pools
            expensive_pools = pools_by_cost[-2:]  # Most expensive pools
            cheap_pools = pools_by_cost[:2]       # Cheapest pools
            
            for allocation in allocations:
                if allocation.pool_id in [p.pool_id for p in expensive_pools]:
                    # Try to move to cheaper pool
                    for cheap_pool in cheap_pools:
                        if cheap_pool.available_capacity >= allocation.amount:
                            # Calculate savings
                            old_cost = self.resource_pools[allocation.pool_id].cost_per_unit
                            new_cost = cheap_pool.cost_per_unit
                            hourly_savings = (old_cost - new_cost) * allocation.amount
                            
                            if hourly_savings > 0:
                                # Simulate move (in real implementation, would actually move)
                                savings += hourly_savings * 24  # Daily savings
                                moves += 1
                                logger.info(f"Cost optimization: Move allocation {allocation.allocation_id} to cheaper pool")
                                break
        
        return {'savings': savings, 'moves': moves}
    
    async def _optimize_performance_allocation(self) -> Dict[str, Any]:
        """Optimize allocations for performance"""
        
        improvements = []
        moves = 0
        
        # Analyze pool utilization and suggest rebalancing
        for pool in self.resource_pools.values():
            utilization = pool.allocated_capacity / pool.total_capacity
            
            if utilization > 0.85:  # High utilization
                # Look for opportunities to move some allocations
                candidate_pools = [
                    p for p in self.resource_pools.values()
                    if (p.resource_type == pool.resource_type and
                        p.pool_id != pool.pool_id and
                        p.allocated_capacity / p.total_capacity < 0.7)
                ]
                
                if candidate_pools:
                    improvements.append({
                        'type': 'load_balancing',
                        'source_pool': pool.pool_id,
                        'target_pools': [p.pool_id for p in candidate_pools],
                        'current_utilization': utilization,
                        'recommendation': 'Redistribute load to improve performance'
                    })
                    moves += 1
        
        return {'improvements': improvements, 'moves': moves}
    
    async def get_resource_usage_report(self) -> Dict[str, Any]:
        """Generate resource usage report"""
        
        report = {
            'timestamp': datetime.utcnow().isoformat(),
            'pools': {},
            'allocations': {},
            'summary': {}
        }
        
        total_capacity = 0
        total_allocated = 0
        total_cost = 0
        
        # Pool details
        for pool in self.resource_pools.values():
            utilization = pool.allocated_capacity / pool.total_capacity
            cost = pool.allocated_capacity * pool.cost_per_unit
            
            report['pools'][pool.pool_id] = {
                'name': pool.name,
                'resource_type': pool.resource_type.value,
                'total_capacity': pool.total_capacity,
                'allocated_capacity': pool.allocated_capacity,
                'available_capacity': pool.available_capacity,
                'utilization_percent': utilization * 100,
                'cost_per_hour': cost,
                'region': pool.region
            }
            
            total_capacity += pool.total_capacity
            total_allocated += pool.allocated_capacity
            total_cost += cost
        
        # Allocation details
        for allocation in self.allocations.values():
            pool = self.resource_pools.get(allocation.pool_id)
            cost = allocation.amount * (pool.cost_per_unit if pool else 0)
            
            report['allocations'][allocation.allocation_id] = {
                'service_id': allocation.service_id,
                'resource_type': allocation.resource_type.value,
                'amount': allocation.amount,
                'pool_id': allocation.pool_id,
                'allocation_time': allocation.allocation_time.isoformat(),
                'priority': allocation.priority,
                'cost_per_hour': cost
            }
        
        # Summary
        overall_utilization = total_allocated / total_capacity if total_capacity > 0 else 0
        
        report['summary'] = {
            'total_pools': len(self.resource_pools),
            'total_allocations': len(self.allocations),
            'overall_utilization_percent': overall_utilization * 100,
            'total_cost_per_hour': total_cost,
            'total_cost_per_day': total_cost * 24,
            'efficiency_score': self._calculate_efficiency_score()
        }
        
        return report
    
    def _calculate_efficiency_score(self) -> float:
        """Calculate overall resource efficiency score"""
        
        if not self.resource_pools:
            return 0.0
        
        total_score = 0.0
        total_weight = 0.0
        
        for pool in self.resource_pools.values():
            utilization = pool.allocated_capacity / pool.total_capacity
            
            # Efficiency is best around 75% utilization
            target_utilization = 0.75
            if utilization <= target_utilization:
                efficiency = utilization / target_utilization
            else:
                # Penalize over-utilization
                efficiency = target_utilization / utilization
            
            # Weight by pool capacity
            weight = pool.total_capacity
            total_score += efficiency * weight
            total_weight += weight
        
        return (total_score / total_weight) * 100 if total_weight > 0 else 0.0
    
    async def forecast_resource_needs(
        self,
        service_growth_projections: Dict[str, float],
        forecast_hours: int = 168  # 1 week
    ) -> Dict[str, Any]:
        """Forecast future resource needs based on growth projections"""
        
        logger.info(f"Forecasting resource needs for {forecast_hours} hours")
        
        forecast = {
            'forecast_period_hours': forecast_hours,
            'projected_needs': {},
            'capacity_gaps': {},
            'recommendations': []
        }
        
        # Calculate current resource usage by service
        current_usage = {}
        for allocation in self.allocations.values():
            service_id = allocation.service_id
            if service_id not in current_usage:
                current_usage[service_id] = {}
            
            resource_type = allocation.resource_type.value
            if resource_type not in current_usage[service_id]:
                current_usage[service_id][resource_type] = 0
            
            current_usage[service_id][resource_type] += allocation.amount
        
        # Project future needs
        for service_id, growth_rate in service_growth_projections.items():
            if service_id not in current_usage:
                continue
            
            projected_usage = {}
            for resource_type, current_amount in current_usage[service_id].items():
                projected_amount = current_amount * (1 + growth_rate)
                projected_usage[resource_type] = projected_amount
            
            forecast['projected_needs'][service_id] = projected_usage
        
        # Check for capacity gaps
        resource_totals = {}
        for service_usage in forecast['projected_needs'].values():
            for resource_type, amount in service_usage.items():
                if resource_type not in resource_totals:
                    resource_totals[resource_type] = 0
                resource_totals[resource_type] += amount
        
        for resource_type_str, total_needed in resource_totals.items():
            resource_type = ResourceType(resource_type_str)
            
            # Calculate total available capacity for this resource type
            total_capacity = sum(
                pool.total_capacity
                for pool in self.resource_pools.values()
                if pool.resource_type == resource_type
            )
            
            if total_needed > total_capacity:
                gap = total_needed - total_capacity
                forecast['capacity_gaps'][resource_type_str] = {
                    'needed': total_needed,
                    'available': total_capacity,
                    'gap': gap,
                    'gap_percent': (gap / total_needed) * 100
                }
                
                forecast['recommendations'].append({
                    'type': 'capacity_expansion',
                    'resource_type': resource_type_str,
                    'additional_capacity_needed': gap,
                    'urgency': 'high' if gap > total_capacity * 0.5 else 'medium'
                })
        
        return forecast