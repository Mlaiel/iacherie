"""Resource Manager - Enterprise Resource Allocation & Optimization System

Advanced resource management system for intelligent allocation, monitoring, and optimization
of system resources across distributed content processing workflows.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL WARNING:
This code is the EXCLUSIVE INTELLECTUAL PROPERTY of Fahed Mlaiel.
Unauthorized use, copying, or distribution is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
import uuid
import json

from backend.core.utils.metrics_collector import MetricsCollector
from backend.core.utils.event_dispatcher import EventDispatcher


class ResourceType(Enum):
    """
System resource types."""

    CPU = "cpu"
    MEMORY = "memory"
    GPU = "gpu"
    STORAGE = "storage"
    NETWORK = "network"
    DATABASE = "database"
    CACHE = "cache"
    QUEUE = "queue"


class ResourceStatus(Enum):
    """Resource status enumeration."""

    AVAILABLE = "available"
    ALLOCATED = "allocated"
    RESERVED = "reserved"
    OVERCOMMITTED = "overcommitted"
    MAINTENANCE = "maintenance"
    FAILED = "failed"


class AllocationStrategy(Enum):
    """Resource allocation strategy options."""

    FIRST_FIT = "first_fit"
    BEST_FIT = "best_fit"
    WORST_FIT = "worst_fit"
    LOAD_BALANCED = "load_balanced"
    PERFORMANCE_OPTIMIZED = "performance_optimized"
    COST_OPTIMIZED = "cost_optimized"
    AI_OPTIMIZED = "ai_optimized"


@dataclass
class ResourceMetrics:
    """Resource performance and usage metrics."""
    utilization: float = 0.0
    throughput: float = 0.0
    latency: float = 0.0
    error_rate: float = 0.0
    availability: float = 100.0
    last_updated: datetime = field(default_factory=datetime.now)
    historical_data: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class ResourceCapacity:
    """
Resource capacity specification."""
    total: float
    allocated: float = 0.0
    reserved: float = 0.0
    available: float = 0.0
    unit: str = "units"
    scalable: bool = False
    min_capacity: float = 0.0
    max_capacity: Optional[float] = None
    
    def __post_init__(self):
        try:
                    # Request validation
                    if not data:
                        raise ValueError("Invalid request")
            
                    # Process request
                    result = await self._handle___post_init___request(data)
            
                    # Return response
                    return {"status": "success", "data": result}
            
                except Exception as e:
                    logger.error(f"API handler __post_init__ failed: {e}")
                    return {"status": "error", "message": str(e)}
@dataclass
class ResourceNode:
    """Individual resource node definition."""
    node_id: str
    name: str
    resource_type: ResourceType
    capacity: ResourceCapacity
    location: str
    status: ResourceStatus = ResourceStatus.AVAILABLE
    metrics: ResourceMetrics = field(default_factory=ResourceMetrics)
    configuration: Dict[str, Any] = field(default_factory=dict)
    tags: Set[str] = field(default_factory=set)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Health and monitoring
    health_score: float = 1.0
    last_heartbeat: Optional[datetime] = None
    uptime: float = 0.0
    downtime: float = 0.0


@dataclass
class ResourcePool:
    """
Collection of related resource nodes."""
    pool_id: str
    name: str
    resource_type: ResourceType
    nodes: Dict[str, ResourceNode] = field(default_factory=dict)
    allocation_strategy: AllocationStrategy = AllocationStrategy.LOAD_BALANCED
    auto_scaling: bool = False
    min_nodes: int = 1
    max_nodes: int = 10
    scaling_threshold: float = 0.8
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ResourceAllocation:
    """
Resource allocation tracking."""
    allocation_id: str
    requester_id: str
    resource_type: ResourceType
    amount: float
    duration: Optional[timedelta] = None
    priority: int = 5
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    allocated_nodes: List[str] = field(default_factory=list)
    status: str = "active"
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ResourceRequest:
    """Resource allocation request."""
    request_id: str
    requester_id: str
    resource_requirements: Dict[ResourceType, float]
    duration: Optional[timedelta] = None
    priority: int = 5
    deadline: Optional[datetime] = None
    constraints: Dict[str, Any] = field(default_factory=dict)
    preferences: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ScalingDecision:
    """
Auto-scaling decision information."""
    pool_id: str
    action: str  # "scale_up", "scale_down", "no_action"
    current_nodes: int
    target_nodes: int
    reason: str
    confidence: float
    estimated_cost: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class ResourceManager:
    """
    Enterprise-grade resource management system with intelligent allocation and optimization.
    
    Provides comprehensive resource management capabilities including:
    - Multi-type resource allocation and tracking
    - Intelligent load balancing and optimization
    - Auto-scaling based on demand patterns
    - Performance monitoring and health checking
    - Cost optimization and resource efficiency
    """
    
    def __init__(self, allocation_strategy: AllocationStrategy = AllocationStrategy.AI_OPTIMIZED):
        self.logger = logging.getLogger(__name__)
        self.metrics_collector = MetricsCollector()
        self.event_dispatcher = EventDispatcher()
        
        # Core configuration
        self.allocation_strategy = allocation_strategy
        self.resource_pools: Dict[str, ResourcePool] = {}
        self.resource_nodes: Dict[str, ResourceNode] = {}
        self.active_allocations: Dict[str, ResourceAllocation] = {}
        self.allocation_history: List[ResourceAllocation] = []
        
        # Request tracking
        self.pending_requests: Dict[str, ResourceRequest] = {}
        self.fulfilled_requests: Dict[str, ResourceRequest] = {}
        
        # Performance tracking
        self.management_stats = {
            'total_requests': 0,
            'fulfilled_requests': 0,
            'rejected_requests': 0,
            'average_allocation_time': 0.0,
            'resource_utilization': 0.0,
            'allocation_efficiency': 0.0,
            'cost_per_hour': 0.0,
            'availability_score': 0.0
        }
        
        # Optimization settings
        self.auto_scaling_enabled = True
        self.load_balancing_enabled = True
        self.cost_optimization_enabled = True
        self.predictive_scaling = True
        
        # Background tasks
        self._manager_running = True
        asyncio.create_task(self._resource_monitor_loop())
        asyncio.create_task(self._auto_scaling_loop())
        
        self.logger.info(f"ResourceManager initialized with strategy: {allocation_strategy.value}")
    
    async def register_resource_pool(self, pool: ResourcePool) -> bool:
        """
        Register a new resource pool.
        
        Args:
            pool: Resource pool configuration
            
        Returns:
            bool: Success status
        """
        try:
            # Validate pool configuration
            if not await self._validate_resource_pool(pool):
                return False
            
            self.resource_pools[pool.pool_id] = pool
            
            # Register all nodes in the pool
            for node in pool.nodes.values():
                self.resource_nodes[node.node_id] = node
            
            await self.event_dispatcher.emit('resource_pool_registered', {
                'pool_id': pool.pool_id,
                'resource_type': pool.resource_type.value,
                'node_count': len(pool.nodes),
                'total_capacity': sum(node.capacity.total for node in pool.nodes.values())
            })
            
            await self.metrics_collector.increment('resource_pools.registered')
            self.logger.info(f"Resource pool registered: {pool.pool_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to register resource pool: {e}")
            return False
    
    async def register_resource_node(self, node: ResourceNode, pool_id: Optional[str] = None) -> bool:
        """
        Register a new resource node.
        
        Args:
            node: Resource node configuration
            pool_id: Optional pool to add node to
            
        Returns:
            bool: Success status
        """
        try:
            # Validate node configuration
            if not await self._validate_resource_node(node):
                return False
            
            self.resource_nodes[node.node_id] = node
            
            # Add to pool if specified
            if pool_id and pool_id in self.resource_pools:
                self.resource_pools[pool_id].nodes[node.node_id] = node
            
            await self.event_dispatcher.emit('resource_node_registered', {
                'node_id': node.node_id,
                'resource_type': node.resource_type.value,
                'capacity': node.capacity.total,
                'pool_id': pool_id
            })
            
            await self.metrics_collector.increment('resource_nodes.registered')
            self.logger.info(f"Resource node registered: {node.node_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to register resource node: {e}")
            return False
    
    async def request_resources(self, request: ResourceRequest) -> Optional[str]:
        """
        Request resource allocation.
        
        Args:
            request: Resource request specification
            
        Returns:
            Optional[str]: Allocation ID if successful
        """
        try:
            # Validate request
            if not await self._validate_resource_request(request):
                return None
            
            self.pending_requests[request.request_id] = request
            self.management_stats['total_requests'] += 1
            
            # Attempt allocation
            allocation = await self._allocate_resources(request)
            
            if allocation:
                self.active_allocations[allocation.allocation_id] = allocation
                self.fulfilled_requests[request.request_id] = request
                self.management_stats['fulfilled_requests'] += 1
                
                # Remove from pending
                if request.request_id in self.pending_requests:
                    del self.pending_requests[request.request_id]
                
                await self.event_dispatcher.emit('resources_allocated', {
                    'allocation_id': allocation.allocation_id,
                    'request_id': request.request_id,
                    'resource_types': list(request.resource_requirements.keys()),
                    'allocated_nodes': allocation.allocated_nodes
                })
                
                await self.metrics_collector.increment('resources.allocated')
                self.logger.info(f"Resources allocated: {allocation.allocation_id}")
                return allocation.allocation_id
            else:
                self.management_stats['rejected_requests'] += 1
                await self.metrics_collector.increment('resources.allocation_failed')
                return None
                
        except Exception as e:
            self.logger.error(f"Failed to allocate resources: {e}")
            self.management_stats['rejected_requests'] += 1
            return None
    
    async def _allocate_resources(self, request: ResourceRequest) -> Optional[ResourceAllocation]:
        """
        Internal resource allocation logic.
        
        Args:
            request: Resource request
            
        Returns:
            Optional[ResourceAllocation]: Allocation result
        """
        allocation_id = str(uuid.uuid4())
        allocated_nodes = []
        
        try:
            # Find suitable nodes for each resource type
            for resource_type, amount in request.resource_requirements.items():
                suitable_nodes = await self._find_suitable_nodes(
                    resource_type, amount, request.constraints
                )
                
                if not suitable_nodes:
                    # Rollback any partial allocations
                    await self._rollback_allocation(allocated_nodes)
                    return None
                
                # Select optimal nodes based on strategy
                selected_nodes = await self._select_optimal_nodes(
                    suitable_nodes, amount, request
                )
                
                if not selected_nodes:
                    await self._rollback_allocation(allocated_nodes)
                    return None
                
                # Allocate resources on selected nodes
                for node_id, allocated_amount in selected_nodes.items():
                    node = self.resource_nodes[node_id]
                    node.capacity.allocated += allocated_amount
                    node.capacity.available -= allocated_amount
                    allocated_nodes.append(node_id)
            
            # Create allocation record
            allocation = ResourceAllocation(
                allocation_id=allocation_id,
                requester_id=request.requester_id,
                resource_type=list(request.resource_requirements.keys())[0],  # Primary type
                amount=sum(request.resource_requirements.values()),
                duration=request.duration,
                priority=request.priority,
                allocated_nodes=allocated_nodes,
                expires_at=datetime.now() + request.duration if request.duration else None
            )
            
            self.allocation_history.append(allocation)
            return allocation
            
        except Exception as e:
            await self._rollback_allocation(allocated_nodes)
            raise e
    
    async def _find_suitable_nodes(
        self,
        resource_type: ResourceType,
        amount: float,
        constraints: Dict[str, Any]
    ) -> List[ResourceNode]:
        """
Find nodes that can satisfy resource requirements."""
        suitable_nodes = []
        
        for node in self.resource_nodes.values():
            if (node.resource_type == resource_type and
                node.status == ResourceStatus.AVAILABLE and
                node.capacity.available >= amount):
                
                # Check constraints
                if await self._check_node_constraints(node, constraints):
                    suitable_nodes.append(node)
        
        return suitable_nodes
    
    async def _select_optimal_nodes(
        self,
        suitable_nodes: List[ResourceNode],
        amount: float,
        request: ResourceRequest
    ) -> Dict[str, float]:
        """
Select optimal nodes based on allocation strategy."""
        if self.allocation_strategy == AllocationStrategy.AI_OPTIMIZED:
            return await self._ai_optimized_selection(suitable_nodes, amount, request)
        elif self.allocation_strategy == AllocationStrategy.BEST_FIT:
            return await self._best_fit_selection(suitable_nodes, amount)
        elif self.allocation_strategy == AllocationStrategy.LOAD_BALANCED:
            return await self._load_balanced_selection(suitable_nodes, amount)
        elif self.allocation_strategy == AllocationStrategy.PERFORMANCE_OPTIMIZED:
            return await self._performance_optimized_selection(suitable_nodes, amount)
        else:  # Default to first fit
            return await self._first_fit_selection(suitable_nodes, amount)
    
    async def _ai_optimized_selection(
        self,
        suitable_nodes: List[ResourceNode],
        amount: float,
        request: ResourceRequest
    ) -> Dict[str, float]:
        """
AI-powered optimal node selection."""
        selected_nodes = {}
        remaining_amount = amount
        
        # Score nodes based on multiple criteria
        scored_nodes = []
        for node in suitable_nodes:
            score = await self._calculate_node_score(node, request)
            scored_nodes.append((score, node))
        
        # Sort by score (descending)
        scored_nodes.sort(key=lambda x: x[0], reverse=True)
        
        # Allocate resources starting with highest scored nodes
        for score, node in scored_nodes:
            if remaining_amount <= 0:
                break
            
            allocate_amount = min(remaining_amount, node.capacity.available)
            selected_nodes[node.node_id] = allocate_amount
            remaining_amount -= allocate_amount
        
        return selected_nodes if remaining_amount <= 0 else {}
    
    async def _best_fit_selection(
        self,
        suitable_nodes: List[ResourceNode],
        amount: float
    ) -> Dict[str, float]:
        """
Best fit allocation strategy."""
        # Find node with smallest available capacity that can fit the request
        best_node = None
        best_fit_size = float('inf')
        
        for node in suitable_nodes:
            if node.capacity.available >= amount and node.capacity.available < best_fit_size:
                best_node = node
                best_fit_size = node.capacity.available
        
        if best_node:
            return {best_node.node_id: amount}
        else:
            return {}
    
    async def _load_balanced_selection(
        self,
        suitable_nodes: List[ResourceNode],
        amount: float
    ) -> Dict[str, float]:
        """
Load balanced allocation strategy."""
        # Distribute load evenly across multiple nodes
        selected_nodes = {}
        remaining_amount = amount
        available_nodes = [node for node in suitable_nodes if node.capacity.available > 0]
        
        while remaining_amount > 0 and available_nodes:
            # Calculate fair share per node
            nodes_count = len(available_nodes)
            share_per_node = remaining_amount / nodes_count
            
            nodes_to_remove = []
            for node in available_nodes:
                allocate_amount = min(share_per_node, node.capacity.available, remaining_amount)
                
                if node.node_id in selected_nodes:
                    selected_nodes[node.node_id] += allocate_amount
                else:
                    selected_nodes[node.node_id] = allocate_amount
                
                remaining_amount -= allocate_amount
                node.capacity.available -= allocate_amount  # Temporary adjustment
                
                if node.capacity.available <= 0:
                    nodes_to_remove.append(node)
            
            # Remove exhausted nodes
            for node in nodes_to_remove:
                available_nodes.remove(node)
        
        # Restore original available capacity
        for node in suitable_nodes:
            if node.node_id in selected_nodes:
                node.capacity.available += selected_nodes[node.node_id]
        
        return selected_nodes if remaining_amount <= 0 else {}
    
    async def _performance_optimized_selection(
        self,
        suitable_nodes: List[ResourceNode],
        amount: float
    ) -> Dict[str, float]:
        """
Performance optimized allocation strategy."""
        # Select nodes with best performance metrics
        performance_scored = []
        for node in suitable_nodes:
            performance_score = (
                node.health_score * 0.4 +
                (1.0 - node.metrics.utilization) * 0.3 +
                (1.0 - node.metrics.latency / 1000.0) * 0.2 +
                (node.metrics.availability / 100.0) * 0.1
            )
            performance_scored.append((performance_score, node))
        
        # Sort by performance score
        performance_scored.sort(key=lambda x: x[0], reverse=True)
        
        # Allocate to best performing nodes
        selected_nodes = {}
        remaining_amount = amount
        
        for score, node in performance_scored:
            if remaining_amount <= 0:
                break
            
            allocate_amount = min(remaining_amount, node.capacity.available)
            selected_nodes[node.node_id] = allocate_amount
            remaining_amount -= allocate_amount
        
        return selected_nodes if remaining_amount <= 0 else {}
    
    async def _first_fit_selection(
        self,
        suitable_nodes: List[ResourceNode],
        amount: float
    ) -> Dict[str, float]:
        """
First fit allocation strategy."""
        for node in suitable_nodes:
            if node.capacity.available >= amount:
                return {node.node_id: amount}
        return {}
    
    async def _calculate_node_score(self, node: ResourceNode, request: ResourceRequest) -> float:
        """
Calculate comprehensive node score for AI optimization."""
        # Base score components
        utilization_score = 1.0 - node.metrics.utilization
        health_score = node.health_score
        availability_score = node.metrics.availability / 100.0
        performance_score = 1.0 - min(node.metrics.latency / 1000.0, 1.0)
        
        # Resource efficiency score
        requested_amount = request.resource_requirements.get(node.resource_type, 0.0)
        efficiency_score = min(node.capacity.available / max(requested_amount, 1.0), 1.0)
        
        # Location preference (if specified)
        location_score = 1.0
        if 'preferred_location' in request.preferences:
            if node.location == request.preferences['preferred_location']:
                location_score = 1.5
            else:
                location_score = 0.8
        
        # Weighted combination
        overall_score = (
            utilization_score * 0.25 +
            health_score * 0.2 +
            availability_score * 0.2 +
            performance_score * 0.15 +
            efficiency_score * 0.15 +
            location_score * 0.05
        )
        
        return overall_score
    
    async def release_resources(self, allocation_id: str) -> bool:
        """
        Release allocated resources.
        
        Args:
            allocation_id: Allocation identifier
            
        Returns:
            bool: Success status
        """
        try:
            if allocation_id not in self.active_allocations:
                return False
            
            allocation = self.active_allocations[allocation_id]
            
            # Release resources on allocated nodes
            for node_id in allocation.allocated_nodes:
                if node_id in self.resource_nodes:
                    node = self.resource_nodes[node_id]
                    
                    # Calculate amount to release (simplified)
                    release_amount = allocation.amount / len(allocation.allocated_nodes)
                    
                    node.capacity.allocated -= release_amount
                    node.capacity.available += release_amount
                    
                    # Ensure capacity constraints
                    node.capacity.allocated = max(0.0, node.capacity.allocated)
                    node.capacity.available = min(
                        node.capacity.total - node.capacity.reserved,
                        node.capacity.available
                    )
            
            # Update allocation status
            allocation.status = "released"
            
            # Remove from active allocations
            del self.active_allocations[allocation_id]
            
            await self.event_dispatcher.emit('resources_released', {
                'allocation_id': allocation_id,
                'requester_id': allocation.requester_id,
                'released_nodes': allocation.allocated_nodes
            })
            
            await self.metrics_collector.increment('resources.released')
            self.logger.info(f"Resources released: {allocation_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to release resources: {e}")
            return False
    
    async def _resource_monitor_loop(self) -> None:
        """Background resource monitoring loop."""
        while self._manager_running:
            try:
                await self._update_resource_metrics()
                await self._check_resource_health()
                await self._cleanup_expired_allocations()
                await self._update_management_stats()
                await asyncio.sleep(30)  # 30-second monitoring interval
                
            except Exception as e:
                self.logger.error(f"Resource monitor error: {e}")
                await asyncio.sleep(60)
    
    async def _auto_scaling_loop(self) -> None:
        """Background auto-scaling loop."""
        while self._manager_running and self.auto_scaling_enabled:
            try:
                for pool in self.resource_pools.values():
                    if pool.auto_scaling:
                        scaling_decision = await self._evaluate_scaling_need(pool)
                        if scaling_decision.action != "no_action":
                            await self._execute_scaling_decision(scaling_decision)
                
                await asyncio.sleep(300)  # 5-minute scaling interval
                
            except Exception as e:
                self.logger.error(f"Auto-scaling error: {e}")
                await asyncio.sleep(600)
    
    async def _evaluate_scaling_need(self, pool: ResourcePool) -> ScalingDecision:
        """Evaluate if pool needs scaling."""
        current_nodes = len(pool.nodes)
        
        # Calculate average utilization
        total_utilization = sum(node.metrics.utilization for node in pool.nodes.values())
        avg_utilization = total_utilization / max(current_nodes, 1)
        
        # Scaling decision logic
        if avg_utilization > pool.scaling_threshold and current_nodes < pool.max_nodes:
            target_nodes = min(current_nodes + 1, pool.max_nodes)
            return ScalingDecision(
                pool_id=pool.pool_id,
                action="scale_up",
                current_nodes=current_nodes,
                target_nodes=target_nodes,
                reason=f"High utilization: {avg_utilization:.2f}",
                confidence=0.8
            )
        elif avg_utilization < (pool.scaling_threshold * 0.5) and current_nodes > pool.min_nodes:
            target_nodes = max(current_nodes - 1, pool.min_nodes)
            return ScalingDecision(
                pool_id=pool.pool_id,
                action="scale_down",
                current_nodes=current_nodes,
                target_nodes=target_nodes,
                reason=f"Low utilization: {avg_utilization:.2f}",
                confidence=0.7
            )
        else:
            return ScalingDecision(
                pool_id=pool.pool_id,
                action="no_action",
                current_nodes=current_nodes,
                target_nodes=current_nodes,
                reason="Utilization within acceptable range",
                confidence=1.0
            )
    
    async def _execute_scaling_decision(self, decision: ScalingDecision) -> bool:
        """Execute scaling decision."""
        try:
            await self.event_dispatcher.emit('scaling_decision', {
                'pool_id': decision.pool_id,
                'action': decision.action,
                'current_nodes': decision.current_nodes,
                'target_nodes': decision.target_nodes,
                'reason': decision.reason,
                'confidence': decision.confidence
            })
            
            await self.metrics_collector.increment(f'scaling.{decision.action}')
            self.logger.info(f"Scaling decision: {decision.pool_id} - {decision.action}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to execute scaling decision: {e}")
            return False
    
    async def _validate_resource_pool(self, pool: ResourcePool) -> bool:
        """Validate resource pool configuration."""
        try:
            if not pool.pool_id or not pool.name:
                return False
            
            if pool.min_nodes > pool.max_nodes:
                return False
            
            return True
            
        except Exception:
            return False
    
    async def _validate_resource_node(self, node: ResourceNode) -> bool:
        """
Validate resource node configuration."""
        try:
            if not node.node_id or not node.name:
                return False
            
            if node.capacity.total <= 0:
                return False
            
            return True
            
        except Exception:
            return False
    
    async def _validate_resource_request(self, request: ResourceRequest) -> bool:
        """
Validate resource request."""
        try:
            if not request.request_id or not request.requester_id:
                return False
            
            if not request.resource_requirements:
                return False
            
            if request.deadline and request.deadline <= datetime.now():
                return False
            
            return True
            
        except Exception:
            return False
    
    async def _check_node_constraints(self, node: ResourceNode, constraints: Dict[str, Any]) -> bool:
        """
Check if node satisfies request constraints."""
        # Location constraint
        if 'location' in constraints:
            if node.location != constraints['location']:
                return False
        
        # Tag constraints
        if 'required_tags' in constraints:
            required_tags = set(constraints['required_tags'])
            if not required_tags.issubset(node.tags):
                return False
        
        # Health constraint
        if 'min_health_score' in constraints:
            if node.health_score < constraints['min_health_score']:
                return False
        
        return True
    
    async def _rollback_allocation(self, allocated_nodes: List[str]) -> None:
        """
Rollback partial resource allocation."""
        for node_id in allocated_nodes:
            if node_id in self.resource_nodes:
                # This is simplified - in reality we'd need to track exact amounts
                node = self.resource_nodes[node_id]
                # Restore capacity (implementation depends on tracking mechanism)
                pass
    
    async def _update_resource_metrics(self) -> None:
        """
Update resource performance metrics."""
        for node in self.resource_nodes.values():
            # Simulate metric updates (in reality, these would come from monitoring systems)
            node.metrics.last_updated = datetime.now()
            
            # Add to historical data
            node.metrics.historical_data.append({
                'timestamp': datetime.now().isoformat(),
                'utilization': node.metrics.utilization,
                'throughput': node.metrics.throughput,
                'latency': node.metrics.latency,
                'availability': node.metrics.availability
            })
            
            # Keep only recent history
            if len(node.metrics.historical_data) > 1440:  # 24 hours of minute-level data
                node.metrics.historical_data = node.metrics.historical_data[-1440:]
    
    async def _check_resource_health(self) -> None:
        """
Check health status of all resources."""
        for node in self.resource_nodes.values():
            # Health check logic (simplified)
            if node.last_heartbeat:
                time_since_heartbeat = (datetime.now() - node.last_heartbeat).total_seconds()
                if time_since_heartbeat > 300:  # 5 minutes
                    node.status = ResourceStatus.FAILED
                    node.health_score = 0.0
                else:
                    node.status = ResourceStatus.AVAILABLE
                    node.health_score = max(0.1, 1.0 - (time_since_heartbeat / 3600))
    
    async def _cleanup_expired_allocations(self) -> None:
        """
Cleanup expired resource allocations."""
        current_time = datetime.now()
        expired_allocations = []
        
        for allocation_id, allocation in self.active_allocations.items():
            if allocation.expires_at and allocation.expires_at <= current_time:
                expired_allocations.append(allocation_id)
        
        for allocation_id in expired_allocations:
            await self.release_resources(allocation_id)
    
    async def _update_management_stats(self) -> None:
        """
Update resource management statistics."""
        # Calculate resource utilization
        total_capacity = sum(node.capacity.total for node in self.resource_nodes.values())
        total_allocated = sum(node.capacity.allocated for node in self.resource_nodes.values())
        
        if total_capacity > 0:
            self.management_stats['resource_utilization'] = total_allocated / total_capacity
        
        # Calculate allocation efficiency
        if self.management_stats['total_requests'] > 0:
            self.management_stats['allocation_efficiency'] = (
                self.management_stats['fulfilled_requests'] / 
                self.management_stats['total_requests']
            )
        
        # Calculate availability score
        healthy_nodes = sum(1 for node in self.resource_nodes.values() 
                          if node.status == ResourceStatus.AVAILABLE)
        total_nodes = len(self.resource_nodes)
        
        if total_nodes > 0:
            self.management_stats['availability_score'] = healthy_nodes / total_nodes
    
    async def get_resource_status(self, node_id: str) -> Optional[ResourceNode]:
        """
Get current resource node status."""
        return self.resource_nodes.get(node_id)
    
    async def get_pool_status(self, pool_id: str) -> Optional[ResourcePool]:
        """
Get current resource pool status."""
        return self.resource_pools.get(pool_id)
    
    async def get_allocation_status(self, allocation_id: str) -> Optional[ResourceAllocation]:
        """
Get current allocation status."""
        return self.active_allocations.get(allocation_id)
    
    async def get_management_stats(self) -> Dict[str, Any]:
        """
Get resource management statistics."""
        return {
            **self.management_stats,
            'active_allocations': len(self.active_allocations),
            'pending_requests': len(self.pending_requests),
            'total_nodes': len(self.resource_nodes),
            'total_pools': len(self.resource_pools),
            'allocation_strategy': self.allocation_strategy.value
        }
    
    async def shutdown(self) -> None:
        """
Shutdown resource manager gracefully."""
        self._manager_running = False
        
        # Release all active allocations
        for allocation_id in list(self.active_allocations.keys()):
            await self.release_resources(allocation_id)
        
        self.logger.info("ResourceManager shutdown completed")
