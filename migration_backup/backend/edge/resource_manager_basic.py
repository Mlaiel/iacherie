"""Resource Manager for Edge Computing
===================================

Advanced resource management system for edge computing infrastructure,
providing dynamic resource allocation, monitoring, and optimization.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple, Set
from enum import Enum
from dataclasses import dataclass, asdict
import json
import uuid
from collections import defaultdict, deque
import psutil
import threading

logger = logging.getLogger(__name__)


class ResourceType(str, Enum):
    """Types of edge resources."""
    CPU = "cpu"
    MEMORY = "memory"
    GPU = "gpu"
    STORAGE = "storage"
    NETWORK = "network"
    BANDWIDTH = "bandwidth"


class ResourceStatus(str, Enum):
    """Resource status states."""
    AVAILABLE = "available"
    ALLOCATED = "allocated"
    RESERVED = "reserved"
    EXHAUSTED = "exhausted"
    MAINTENANCE = "maintenance"
    ERROR = "error"


class AllocationStrategy(str, Enum):
    """Resource allocation strategies."""
    FIRST_FIT = "first_fit"
    BEST_FIT = "best_fit"
    WORST_FIT = "worst_fit"
    BALANCED = "balanced"
    PERFORMANCE_OPTIMIZED = "performance_optimized"
    ENERGY_OPTIMIZED = "energy_optimized"


class ResourcePriority(str, Enum):
    """Resource allocation priorities."""
    CRITICAL = "critical"
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"
    BACKGROUND = "background"


@dataclass
class ResourceSpec:
    """Resource specification."""
    resource_type: ResourceType
    amount: float
    unit: str
    min_amount: Optional[float] = None
    max_amount: Optional[float] = None
    requirements: Optional[Dict[str, Any]] = None


@dataclass
class ResourceAllocation:
    """Resource allocation record."""
    allocation_id: str
    resource_type: ResourceType
    amount: float
    allocated_to: str
    priority: ResourcePriority
    timestamp: datetime
    expires_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class ResourceUsage:
    """Resource usage metrics."""
    resource_type: ResourceType
    total_capacity: float
    allocated: float
    available: float
    utilization_percent: float
    timestamp: datetime
    node_id: str


@dataclass
class ResourceNode:
    """Edge node resource information."""
    node_id: str
    node_type: str
    location: str
    resources: Dict[ResourceType, float]
    allocated_resources: Dict[ResourceType, float]
    status: ResourceStatus
    last_heartbeat: datetime
    capabilities: List[str]
    metadata: Dict[str, Any]


class EdgeResourceManager:
    """Advanced resource manager for edge computing infrastructure."""
    
    def __init__(self, 
                 default_strategy: AllocationStrategy = AllocationStrategy.BALANCED,
                 monitoring_interval: float = 5.0,
                 resource_timeout: int = 3600):
        self.default_strategy = default_strategy
        self.monitoring_interval = monitoring_interval
        self.resource_timeout = resource_timeout
        
        # Resource tracking
        self.nodes: Dict[str, ResourceNode] = {}
        self.allocations: Dict[str, ResourceAllocation] = {}
        self.usage_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        
        # Resource pools
        self.resource_pools: Dict[str, Dict[ResourceType, float]] = {}
        self.reserved_resources: Dict[str, List[ResourceAllocation]] = defaultdict(list)
        
        # Allocation strategies
        self.allocation_strategies = {
            AllocationStrategy.FIRST_FIT: self._first_fit_allocation,
            AllocationStrategy.BEST_FIT: self._best_fit_allocation,
            AllocationStrategy.WORST_FIT: self._worst_fit_allocation,
            AllocationStrategy.BALANCED: self._balanced_allocation,
            AllocationStrategy.PERFORMANCE_OPTIMIZED: self._performance_optimized_allocation,
            AllocationStrategy.ENERGY_OPTIMIZED: self._energy_optimized_allocation
        }
        
        # Monitoring and cleanup tasks
        self.monitoring_task: Optional[asyncio.Task] = None
        self.cleanup_task: Optional[asyncio.Task] = None
        self.running = False
        
        # Thread-safe locks
        self._allocation_lock = threading.RLock()
        
        logger.info(f"EdgeResourceManager initialized with strategy: {default_strategy}")
    
    async def start(self):
        """Start the resource manager."""
        if self.running:
            logger.warning("Resource manager already running")
            return
        
        self.running = True
        
        # Start monitoring and cleanup tasks
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
        self.cleanup_task = asyncio.create_task(self._cleanup_loop())
        
        # Initialize local node
        await self._initialize_local_node()
        
        logger.info("Edge resource manager started")
    
    async def stop(self):
        """Stop the resource manager."""
        self.running = False
        
        # Cancel tasks
        if self.monitoring_task:
            self.monitoring_task.cancel()
        if self.cleanup_task:
            self.cleanup_task.cancel()
        
        # Wait for tasks to complete
        tasks = [task for task in [self.monitoring_task, self.cleanup_task] if task]
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
        
        logger.info("Edge resource manager stopped")
    
    async def register_node(self, node: ResourceNode) -> bool:
        """Register a new edge node."""
        try:
            self.nodes[node.node_id] = node
            
            # Initialize resource pool for this node
            self.resource_pools[node.node_id] = node.resources.copy()
            
            logger.info(f"Registered edge node: {node.node_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register node {node.node_id}: {e}")
            return False
    
    async def unregister_node(self, node_id: str) -> bool:
        """Unregister an edge node."""
        try:
            if node_id not in self.nodes:
                logger.warning(f"Node {node_id} not found for unregistration")
                return False
            
            # Release all allocations on this node
            await self._release_node_allocations(node_id)
            
            # Remove node
            del self.nodes[node_id]
            if node_id in self.resource_pools:
                del self.resource_pools[node_id]
            
            logger.info(f"Unregistered edge node: {node_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to unregister node {node_id}: {e}")
            return False
    
    async def allocate_resources(self, 
                                specs: List[ResourceSpec],
                                requester_id: str,
                                priority: ResourcePriority = ResourcePriority.NORMAL,
                                strategy: Optional[AllocationStrategy] = None,
                                node_constraints: Optional[Dict[str, Any]] = None,
                                timeout: Optional[int] = None) -> Optional[List[ResourceAllocation]]:
        """Allocate resources according to specifications."""
        
        allocation_strategy = strategy or self.default_strategy
        timeout = timeout or self.resource_timeout
        
        with self._allocation_lock:
            try:
                # Find suitable nodes
                candidate_nodes = await self._find_candidate_nodes(specs, node_constraints)
                if not candidate_nodes:
                    logger.warning(f"No suitable nodes found for allocation request from {requester_id}")
                    return None
                
                # Apply allocation strategy
                allocation_plan = await self.allocation_strategies[allocation_strategy](
                    specs, candidate_nodes, priority
                )
                
                if not allocation_plan:
                    logger.warning(f"Allocation strategy failed for request from {requester_id}")
                    return None
                
                # Execute allocations
                allocations = []
                for node_id, resource_allocations in allocation_plan.items():
                    for spec, amount in resource_allocations:
                        allocation = ResourceAllocation(
                            allocation_id=str(uuid.uuid4()),
                            resource_type=spec.resource_type,
                            amount=amount,
                            allocated_to=requester_id,
                            priority=priority,
                            timestamp=datetime.now(),
                            expires_at=datetime.now() + timedelta(seconds=timeout) if timeout > 0 else None
                        )
                        
                        # Update node resources
                        if await self._execute_allocation(node_id, allocation):
                            allocations.append(allocation)
                            self.allocations[allocation.allocation_id] = allocation
                        else:
                            # Rollback previous allocations
                            await self._rollback_allocations(allocations)
                            return None
                
                logger.info(f"Successfully allocated {len(allocations)} resources to {requester_id}")
                return allocations
                
            except Exception as e:
                logger.error(f"Resource allocation failed: {e}")
                return None
    
    async def release_resources(self, allocation_ids: List[str]) -> bool:
        """Release allocated resources."""
        success = True
        
        with self._allocation_lock:
            for allocation_id in allocation_ids:
                if allocation_id not in self.allocations:
                    logger.warning(f"Allocation {allocation_id} not found")
                    success = False
                    continue
                
                allocation = self.allocations[allocation_id]
                
                # Find the node with this allocation
                node_id = await self._find_allocation_node(allocation_id)
                if node_id and await self._execute_release(node_id, allocation):
                    del self.allocations[allocation_id]
                    logger.debug(f"Released allocation {allocation_id}")
                else:
                    logger.error(f"Failed to release allocation {allocation_id}")
                    success = False
        
        return success
    
    async def get_resource_usage(self, node_id: Optional[str] = None) -> Dict[str, ResourceUsage]:
        """Get current resource usage statistics."""
        usage_stats = {}
        
        nodes_to_check = [node_id] if node_id else list(self.nodes.keys())
        
        for nid in nodes_to_check:
            if nid not in self.nodes:
                continue
            
            node = self.nodes[nid]
            
            for resource_type, total_capacity in node.resources.items():
                allocated = node.allocated_resources.get(resource_type, 0)
                available = total_capacity - allocated
                utilization = (allocated / total_capacity * 100) if total_capacity > 0 else 0
                
                usage = ResourceUsage(
                    resource_type=resource_type,
                    total_capacity=total_capacity,
                    allocated=allocated,
                    available=available,
                    utilization_percent=utilization,
                    timestamp=datetime.now(),
                    node_id=nid
                )
                
                usage_stats[f"{nid}_{resource_type.value}"] = usage
        
        return usage_stats
    
    async def get_allocation_info(self, allocation_id: str) -> Optional[ResourceAllocation]:
        """Get information about a specific allocation."""
        return self.allocations.get(allocation_id)
    
    async def list_allocations(self, requester_id: Optional[str] = None) -> List[ResourceAllocation]:
        """List current allocations, optionally filtered by requester."""
        allocations = list(self.allocations.values())
        
        if requester_id:
            allocations = [a for a in allocations if a.allocated_to == requester_id]
        
        return allocations
    
    async def update_node_status(self, node_id: str, status: ResourceStatus):
        """Update the status of an edge node."""
        if node_id in self.nodes:
            self.nodes[node_id].status = status
            self.nodes[node_id].last_heartbeat = datetime.now()
            logger.info(f"Updated node {node_id} status to {status}")
        else:
            logger.warning(f"Cannot update status for unknown node {node_id}")
    
    async def reserve_resources(self, 
                               specs: List[ResourceSpec],
                               requester_id: str,
                               reservation_duration: int = 300) -> Optional[str]:
        """Reserve resources for future allocation."""
        
        reservation_id = str(uuid.uuid4())
        
        try:
            # Create temporary allocations for reservation
            allocations = await self.allocate_resources(
                specs=specs,
                requester_id=f"reservation_{requester_id}",
                priority=ResourcePriority.HIGH,
                timeout=reservation_duration
            )
            
            if allocations:
                self.reserved_resources[reservation_id] = allocations
                logger.info(f"Reserved resources for {requester_id}: {reservation_id}")
                return reservation_id
            
            return None
            
        except Exception as e:
            logger.error(f"Resource reservation failed: {e}")
            return None
    
    async def claim_reservation(self, reservation_id: str, requester_id: str) -> Optional[List[ResourceAllocation]]:
        """Claim a previously made reservation."""
        if reservation_id not in self.reserved_resources:
            logger.warning(f"Reservation {reservation_id} not found")
            return None
        
        allocations = self.reserved_resources[reservation_id]
        
        # Update allocations to actual requester
        for allocation in allocations:
            allocation.allocated_to = requester_id
            allocation.timestamp = datetime.now()
        
        del self.reserved_resources[reservation_id]
        
        logger.info(f"Claimed reservation {reservation_id} for {requester_id}")
        return allocations
    
    # Private methods
    
    async def _initialize_local_node(self):
        """Initialize the local node as an edge resource node."""
        try:
            # Get system information
            cpu_count = psutil.cpu_count()
            memory_info = psutil.virtual_memory()
            disk_info = psutil.disk_usage('/')
            
            local_node = ResourceNode(
                node_id="local_node",
                node_type="edge_node",
                location="local",
                resources={
                    ResourceType.CPU: float(cpu_count),
                    ResourceType.MEMORY: float(memory_info.total // (1024**3)),  # GB
                    ResourceType.STORAGE: float(disk_info.total // (1024**3)),   # GB
                    ResourceType.NETWORK: 1000.0,  # Mbps - default
                    ResourceType.BANDWIDTH: 100.0   # Mbps - default
                },
                allocated_resources={
                    ResourceType.CPU: 0.0,
                    ResourceType.MEMORY: 0.0,
                    ResourceType.STORAGE: 0.0,
                    ResourceType.NETWORK: 0.0,
                    ResourceType.BANDWIDTH: 0.0
                },
                status=ResourceStatus.AVAILABLE,
                last_heartbeat=datetime.now(),
                capabilities=["compute", "storage", "networking"],
                metadata={"is_local": True}
            )
            
            await self.register_node(local_node)
            
        except Exception as e:
            logger.error(f"Failed to initialize local node: {e}")
    
    async def _monitoring_loop(self):
        """Monitor resource usage and node health."""
        while self.running:
            try:
                # Update resource usage statistics
                await self._update_usage_statistics()
                
                # Check node health
                await self._check_node_health()
                
                # Update system metrics for local node
                await self._update_local_metrics()
                
                await asyncio.sleep(self.monitoring_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(self.monitoring_interval)
    
    async def _cleanup_loop(self):
        """Clean up expired allocations and reservations."""
        while self.running:
            try:
                await self._cleanup_expired_allocations()
                await self._cleanup_expired_reservations()
                await asyncio.sleep(60)  # Check every minute
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}")
                await asyncio.sleep(60)
    
    async def _find_candidate_nodes(self, 
                                   specs: List[ResourceSpec],
                                   constraints: Optional[Dict[str, Any]]) -> List[str]:
        """Find nodes that can satisfy the resource requirements."""
        candidate_nodes = []
        
        for node_id, node in self.nodes.items():
            if node.status != ResourceStatus.AVAILABLE:
                continue
            
            # Check if node meets constraints
            if constraints and not await self._node_meets_constraints(node, constraints):
                continue
            
            # Check if node has sufficient resources
            can_satisfy = True
            for spec in specs:
                available = (node.resources.get(spec.resource_type, 0) - 
                           node.allocated_resources.get(spec.resource_type, 0))
                
                if available < spec.amount:
                    can_satisfy = False
                    break
            
            if can_satisfy:
                candidate_nodes.append(node_id)
        
        return candidate_nodes
    
    async def _node_meets_constraints(self, node: ResourceNode, constraints: Dict[str, Any]) -> bool:
        """Check if a node meets the specified constraints."""
        for constraint_type, constraint_value in constraints.items():
            if constraint_type == "location" and node.location != constraint_value:
                return False
            elif constraint_type == "capabilities":
                required_caps = constraint_value if isinstance(constraint_value, list) else [constraint_value]
                if not all(cap in node.capabilities for cap in required_caps):
                    return False
            elif constraint_type == "node_type" and node.node_type != constraint_value:
                return False
        
        return True
    
    # Allocation strategy implementations
    
    async def _first_fit_allocation(self, 
                                   specs: List[ResourceSpec],
                                   candidate_nodes: List[str],
                                   priority: ResourcePriority) -> Optional[Dict[str, List[Tuple[ResourceSpec, float]]]]:
        """First-fit allocation strategy."""
        allocation_plan = {}
        
        for spec in specs:
            allocated = False
            for node_id in candidate_nodes:
                node = self.nodes[node_id]
                available = (node.resources.get(spec.resource_type, 0) - 
                           node.allocated_resources.get(spec.resource_type, 0))
                
                if available >= spec.amount:
                    if node_id not in allocation_plan:
                        allocation_plan[node_id] = []
                    allocation_plan[node_id].append((spec, spec.amount))
                    
                    # Update temporary allocation for next specs
                    node.allocated_resources[spec.resource_type] = (
                        node.allocated_resources.get(spec.resource_type, 0) + spec.amount
                    )
                    allocated = True
                    break
            
            if not allocated:
                return None
        
        return allocation_plan
    
    async def _best_fit_allocation(self, 
                                  specs: List[ResourceSpec],
                                  candidate_nodes: List[str],
                                  priority: ResourcePriority) -> Optional[Dict[str, List[Tuple[ResourceSpec, float]]]]:
        """Best-fit allocation strategy - allocate to node with least available resources."""
        allocation_plan = {}
        
        for spec in specs:
            best_node = None
            best_available = float('inf')
            
            for node_id in candidate_nodes:
                node = self.nodes[node_id]
                available = (node.resources.get(spec.resource_type, 0) - 
                           node.allocated_resources.get(spec.resource_type, 0))
                
                if available >= spec.amount and available < best_available:
                    best_node = node_id
                    best_available = available
            
            if best_node:
                if best_node not in allocation_plan:
                    allocation_plan[best_node] = []
                allocation_plan[best_node].append((spec, spec.amount))
                
                # Update temporary allocation
                node = self.nodes[best_node]
                node.allocated_resources[spec.resource_type] = (
                    node.allocated_resources.get(spec.resource_type, 0) + spec.amount
                )
            else:
                return None
        
        return allocation_plan
    
    async def _worst_fit_allocation(self, 
                                   specs: List[ResourceSpec],
                                   candidate_nodes: List[str],
                                   priority: ResourcePriority) -> Optional[Dict[str, List[Tuple[ResourceSpec, float]]]]:
        """Worst-fit allocation strategy - allocate to node with most available resources."""
        allocation_plan = {}
        
        for spec in specs:
            best_node = None
            best_available = 0
            
            for node_id in candidate_nodes:
                node = self.nodes[node_id]
                available = (node.resources.get(spec.resource_type, 0) - 
                           node.allocated_resources.get(spec.resource_type, 0))
                
                if available >= spec.amount and available > best_available:
                    best_node = node_id
                    best_available = available
            
            if best_node:
                if best_node not in allocation_plan:
                    allocation_plan[best_node] = []
                allocation_plan[best_node].append((spec, spec.amount))
                
                # Update temporary allocation
                node = self.nodes[best_node]
                node.allocated_resources[spec.resource_type] = (
                    node.allocated_resources.get(spec.resource_type, 0) + spec.amount
                )
            else:
                return None
        
        return allocation_plan
    
    async def _balanced_allocation(self, 
                                  specs: List[ResourceSpec],
                                  candidate_nodes: List[str],
                                  priority: ResourcePriority) -> Optional[Dict[str, List[Tuple[ResourceSpec, float]]]]:
        """Balanced allocation strategy - distribute load evenly."""
        allocation_plan = {}
        
        # Calculate current utilization for each node
        node_utilization = {}
        for node_id in candidate_nodes:
            node = self.nodes[node_id]
            total_util = 0
            resource_count = 0
            
            for resource_type, total_capacity in node.resources.items():
                if total_capacity > 0:
                    allocated = node.allocated_resources.get(resource_type, 0)
                    util = allocated / total_capacity
                    total_util += util
                    resource_count += 1
            
            node_utilization[node_id] = total_util / max(resource_count, 1)
        
        for spec in specs:
            # Find node with lowest utilization that can handle the request
            best_node = None
            best_utilization = float('inf')
            
            for node_id in candidate_nodes:
                node = self.nodes[node_id]
                available = (node.resources.get(spec.resource_type, 0) - 
                           node.allocated_resources.get(spec.resource_type, 0))
                
                if available >= spec.amount and node_utilization[node_id] < best_utilization:
                    best_node = node_id
                    best_utilization = node_utilization[node_id]
            
            if best_node:
                if best_node not in allocation_plan:
                    allocation_plan[best_node] = []
                allocation_plan[best_node].append((spec, spec.amount))
                
                # Update temporary allocation and utilization
                node = self.nodes[best_node]
                node.allocated_resources[spec.resource_type] = (
                    node.allocated_resources.get(spec.resource_type, 0) + spec.amount
                )
                
                # Recalculate utilization for this node
                total_util = 0
                resource_count = 0
                for resource_type, total_capacity in node.resources.items():
                    if total_capacity > 0:
                        allocated = node.allocated_resources.get(resource_type, 0)
                        util = allocated / total_capacity
                        total_util += util
                        resource_count += 1
                
                node_utilization[best_node] = total_util / max(resource_count, 1)
            else:
                return None
        
        return allocation_plan
    
    async def _performance_optimized_allocation(self, 
                                               specs: List[ResourceSpec],
                                               candidate_nodes: List[str],
                                               priority: ResourcePriority) -> Optional[Dict[str, List[Tuple[ResourceSpec, float]]]]:
        """Performance-optimized allocation - prefer high-performance nodes."""
        # For now, use best-fit as a proxy for performance optimization
        return await self._best_fit_allocation(specs, candidate_nodes, priority)
    
    async def _energy_optimized_allocation(self, 
                                          specs: List[ResourceSpec],
                                          candidate_nodes: List[str],
                                          priority: ResourcePriority) -> Optional[Dict[str, List[Tuple[ResourceSpec, float]]]]:
        """Energy-optimized allocation - prefer nodes that minimize energy usage."""
        # For now, use worst-fit to consolidate workloads
        return await self._worst_fit_allocation(specs, candidate_nodes, priority)
    
    async def _execute_allocation(self, node_id: str, allocation: ResourceAllocation) -> bool:
        """Execute a resource allocation on a specific node."""
        try:
            if node_id not in self.nodes:
                return False
            
            node = self.nodes[node_id]
            resource_type = allocation.resource_type
            
            # Check if resources are still available
            available = (node.resources.get(resource_type, 0) - 
                        node.allocated_resources.get(resource_type, 0))
            
            if available < allocation.amount:
                return False
            
            # Execute allocation
            node.allocated_resources[resource_type] = (
                node.allocated_resources.get(resource_type, 0) + allocation.amount
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to execute allocation {allocation.allocation_id}: {e}")
            return False
    
    async def _execute_release(self, node_id: str, allocation: ResourceAllocation) -> bool:
        """Execute a resource release on a specific node."""
        try:
            if node_id not in self.nodes:
                return False
            
            node = self.nodes[node_id]
            resource_type = allocation.resource_type
            
            # Release resources
            current_allocated = node.allocated_resources.get(resource_type, 0)
            node.allocated_resources[resource_type] = max(0, current_allocated - allocation.amount)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to release allocation {allocation.allocation_id}: {e}")
            return False
    
    async def _find_allocation_node(self, allocation_id: str) -> Optional[str]:
        """Find which node contains a specific allocation."""
        # In a real implementation, this would be tracked more efficiently
        allocation = self.allocations.get(allocation_id)
        if not allocation:
            return None
        
        # For now, search through all nodes (inefficient but functional)
        for node_id in self.nodes.keys():
            # This is a placeholder - in practice, we'd maintain allocation-to-node mapping
            return node_id  # Return first node for demo
        
        return None
    
    async def _rollback_allocations(self, allocations: List[ResourceAllocation]):
        """Rollback a list of allocations."""
        for allocation in allocations:
            node_id = await self._find_allocation_node(allocation.allocation_id)
            if node_id:
                await self._execute_release(node_id, allocation)
                if allocation.allocation_id in self.allocations:
                    del self.allocations[allocation.allocation_id]
    
    async def _release_node_allocations(self, node_id: str):
        """Release all allocations on a specific node."""
        allocations_to_release = []
        
        for allocation_id, allocation in self.allocations.items():
            # Check if allocation belongs to this node
            if await self._find_allocation_node(allocation_id) == node_id:
                allocations_to_release.append(allocation_id)
        
        await self.release_resources(allocations_to_release)
    
    async def _update_usage_statistics(self):
        """Update resource usage statistics."""
        usage_stats = await self.get_resource_usage()
        
        for key, usage in usage_stats.items():
            self.usage_history[key].append(usage)
    
    async def _check_node_health(self):
        """Check health of all registered nodes."""
        current_time = datetime.now()
        
        for node_id, node in self.nodes.items():
            # Check if node has sent heartbeat recently
            if node.last_heartbeat and (current_time - node.last_heartbeat).seconds > 300:  # 5 minutes
                if node.status == ResourceStatus.AVAILABLE:
                    node.status = ResourceStatus.ERROR
                    logger.warning(f"Node {node_id} appears to be offline")
    
    async def _update_local_metrics(self):
        """Update metrics for the local node."""
        if "local_node" not in self.nodes:
            return
        
        try:
            # Update CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Update memory usage
            memory_info = psutil.virtual_memory()
            memory_used_gb = (memory_info.total - memory_info.available) // (1024**3)
            
            # Update local node allocated resources based on actual system usage
            local_node = self.nodes["local_node"]
            local_node.allocated_resources[ResourceType.CPU] = (
                local_node.resources[ResourceType.CPU] * cpu_percent / 100
            )
            local_node.allocated_resources[ResourceType.MEMORY] = float(memory_used_gb)
            local_node.last_heartbeat = datetime.now()
            
        except Exception as e:
            logger.error(f"Failed to update local metrics: {e}")
    
    async def _cleanup_expired_allocations(self):
        """Clean up expired resource allocations."""
        current_time = datetime.now()
        expired_allocations = []
        
        for allocation_id, allocation in self.allocations.items():
            if allocation.expires_at and current_time > allocation.expires_at:
                expired_allocations.append(allocation_id)
        
        if expired_allocations:
            await self.release_resources(expired_allocations)
            logger.info(f"Cleaned up {len(expired_allocations)} expired allocations")
    
    async def _cleanup_expired_reservations(self):
        """Clean up expired resource reservations."""
        current_time = datetime.now()
        expired_reservations = []
        
        for reservation_id, allocations in self.reserved_resources.items():
            # Check if any allocation in the reservation has expired
            if any(a.expires_at and current_time > a.expires_at for a in allocations):
                expired_reservations.append(reservation_id)
        
        for reservation_id in expired_reservations:
            allocations = self.reserved_resources[reservation_id]
            allocation_ids = [a.allocation_id for a in allocations]
            await self.release_resources(allocation_ids)
            del self.reserved_resources[reservation_id]
        
        if expired_reservations:
            logger.info(f"Cleaned up {len(expired_reservations)} expired reservations")


def create_resource_manager(
    default_strategy: AllocationStrategy = AllocationStrategy.BALANCED,
    monitoring_interval: float = 5.0,
    resource_timeout: int = 3600
) -> EdgeResourceManager:
    """Create and configure a resource manager instance."""
    return EdgeResourceManager(
        default_strategy=default_strategy,
        monitoring_interval=monitoring_interval,
        resource_timeout=resource_timeout
    )


# Example usage and testing
if __name__ == "__main__":
    async def test_resource_manager():
        """Test the resource manager."""
        manager = create_resource_manager()
        
        # Start manager
        await manager.start()
        
        # Test resource allocation
        specs = [
            ResourceSpec(ResourceType.CPU, 2.0, "cores"),
            ResourceSpec(ResourceType.MEMORY, 4.0, "GB")
        ]
        
        allocations = await manager.allocate_resources(
            specs=specs,
            requester_id="test_service",
            priority=ResourcePriority.HIGH
        )
        
        if allocations:
            print(f"Allocated {len(allocations)} resources")
            
            # Get usage stats
            usage = await manager.get_resource_usage()
            for key, stat in usage.items():
                print(f"{key}: {stat.utilization_percent:.1f}% utilized")
            
            # Release resources
            allocation_ids = [a.allocation_id for a in allocations]
            await manager.release_resources(allocation_ids)
            print("Resources released")
        
        # Stop manager
        await manager.stop()
    
    # Run test
    asyncio.run(test_resource_manager())