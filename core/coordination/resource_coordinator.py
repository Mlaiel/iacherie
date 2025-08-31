"""Resource Coordinator - Enterprise Resource Management & Allocation System

Advanced resource coordination system providing intelligent resource allocation,
monitoring, and optimization for the IA-Influencer-Agent platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL WARNING:
This resource coordination system is the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, or distribution is strictly prohibited and will result in legal action.
Contact: mlaiel@live.de for authorization.

🎯 BUSINESS LOGIC:
Resource Discovery → Allocation → Monitoring → Optimization → Cleanup → Reporting
"""
import asyncio
import uuid
import psutil
import threading
from datetime import datetime, timezone, timedelta
from enum import Enum
from typing import Dict, List, Any, Optional, Callable, Set, Union
from dataclasses import dataclass, field
from collections import defaultdict, deque
import logging
import json
import time

logger = logging.getLogger(__name__)


class ResourceType(Enum):
    """Types of resources managed by the system"""    CPU = "cpu"
    MEMORY = "memory"
    DISK = "disk"
    NETWORK = "network"
    GPU = "gpu"
    DATABASE_CONNECTION = "database_connection"
    API_QUOTA = "api_quota"
    FILE_DESCRIPTOR = "file_descriptor"
    THREAD_POOL = "thread_pool"
    PROCESS_SLOT = "process_slot"


class AllocationStrategy(Enum):
    """Resource allocation strategies"""    FIRST_FIT = "first_fit"
    BEST_FIT = "best_fit"
    WORST_FIT = "worst_fit"
    ROUND_ROBIN = "round_robin"
    PRIORITY_BASED = "priority_based"
    LOAD_BALANCED = "load_balanced"
    FAIR_SHARE = "fair_share"
    PREDICTIVE = "predictive"


class ResourceStatus(Enum):
    """Resource status states"""    AVAILABLE = "available"
    ALLOCATED = "allocated"
    RESERVED = "reserved"
    UNAVAILABLE = "unavailable"
    MAINTENANCE = "maintenance"
    FAILED = "failed"
    DEGRADED = "degraded"


class AllocationPriority(Enum):
    """Resource allocation priority levels"""    CRITICAL = 1
    HIGH = 2
    NORMAL = 3
    LOW = 4
    BACKGROUND = 5


@dataclass
class ResourceCapacity:
    """Resource capacity definition"""    total: float
    available: float
    allocated: float
    reserved: float
    unit: str
    
    @property
    def utilization_percentage(self) -> float:
        """Calculate resource utilization percentage"""        if self.total == 0:
            return 0.0
        return (self.allocated / self.total) * 100


@dataclass
class ResourceRequirement:
    """Resource requirement specification"""    resource_type: ResourceType
    amount: float
    priority: AllocationPriority
    duration_seconds: Optional[int] = None
    constraints: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ResourceAllocation:
    """Resource allocation record"""    allocation_id: str
    resource_id: str
    consumer_id: str
    resource_type: ResourceType
    allocated_amount: float
    allocated_at: datetime
    expires_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    performance_metrics: Dict[str, float] = field(default_factory=dict)


@dataclass
class ResourceInstance:
    """Individual resource instance"""    resource_id: str
    resource_type: ResourceType
    name: str
    capacity: ResourceCapacity
    status: ResourceStatus
    location: str = "local"
    properties: Dict[str, Any] = field(default_factory=dict)
    allocations: List[str] = field(default_factory=list)
    health_score: float = 100.0
    last_updated: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class ResourceCoordinator:
    """Enterprise resource management and allocation coordination system"""    
    def __init__(self, monitoring_interval: int = 30):
        self.monitoring_interval = monitoring_interval
        
        # Resource registry
        self.resources: Dict[str, ResourceInstance] = {}
        self.allocations: Dict[str, ResourceAllocation] = {}
        self.allocation_queue: deque = deque()
        
        # Allocation strategies
        self.default_strategy = AllocationStrategy.BEST_FIT
        self.strategy_handlers = {
            AllocationStrategy.FIRST_FIT: self._allocate_first_fit,
            AllocationStrategy.BEST_FIT: self._allocate_best_fit,
            AllocationStrategy.WORST_FIT: self._allocate_worst_fit,
            AllocationStrategy.ROUND_ROBIN: self._allocate_round_robin,
            AllocationStrategy.PRIORITY_BASED: self._allocate_priority_based,
            AllocationStrategy.LOAD_BALANCED: self._allocate_load_balanced,
            AllocationStrategy.FAIR_SHARE: self._allocate_fair_share,
            AllocationStrategy.PREDICTIVE: self._allocate_predictive
        }
        
        # Monitoring and optimization
        self.monitoring_active = False
        self.monitoring_thread: Optional[threading.Thread] = None
        self.resource_locks: Dict[str, threading.Lock] = defaultdict(threading.Lock)
        
        # Performance tracking
        self.allocation_metrics: Dict[str, List[float]] = defaultdict(list)
        self.utilization_history: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self.optimization_recommendations: List[Dict[str, Any]] = []
        
        # Event handling
        self.event_handlers: Dict[str, List[Callable]] = defaultdict(list)
        self.allocation_listeners: Dict[str, List[Callable]] = defaultdict(list)
        
        # Initialize system resources
        self._initialize_system_resources()
        
        # Start monitoring
        self.start_monitoring()
        
        logger.info("ResourceCoordinator initialized successfully")
    
    def _initialize_system_resources(self):
        """Initialize system resource instances"""        try:
            # CPU Resources
            cpu_resource = ResourceInstance(
                resource_id="system_cpu",
                resource_type=ResourceType.CPU,
                name="System CPU",
                capacity=ResourceCapacity(
                    total=psutil.cpu_count(),
                    available=psutil.cpu_count(),
                    allocated=0,
                    reserved=0,
                    unit="cores"
                ),
                status=ResourceStatus.AVAILABLE,
                properties={
                    "architecture": "x86_64",
                    "frequency": psutil.cpu_freq().current if psutil.cpu_freq() else 2400
                }
            )
            
            # Memory Resources
            memory_info = psutil.virtual_memory()
            memory_resource = ResourceInstance(
                resource_id="system_memory",
                resource_type=ResourceType.MEMORY,
                name="System Memory",
                capacity=ResourceCapacity(
                    total=memory_info.total / (1024**3),  # GB
                    available=memory_info.available / (1024**3),  # GB
                    allocated=0,
                    reserved=memory_info.total * 0.1 / (1024**3),  # Reserve 10%
                    unit="GB"
                ),
                status=ResourceStatus.AVAILABLE,
                properties={
                    "type": "RAM",
                    "swap_total": psutil.swap_memory().total / (1024**3)
                }
            )
            
            # Disk Resources
            disk_info = psutil.disk_usage('/')
            disk_resource = ResourceInstance(
                resource_id="system_disk",
                resource_type=ResourceType.DISK,
                name="System Disk",
                capacity=ResourceCapacity(
                    total=disk_info.total / (1024**3),  # GB
                    available=disk_info.free / (1024**3),  # GB
                    allocated=0,
                    reserved=disk_info.total * 0.05 / (1024**3),  # Reserve 5%
                    unit="GB"
                ),
                status=ResourceStatus.AVAILABLE,
                properties={
                    "filesystem": "ext4",
                    "mount_point": "/"
                }
            )
            
            # Network Resources
            network_resource = ResourceInstance(
                resource_id="system_network",
                resource_type=ResourceType.NETWORK,
                name="System Network",
                capacity=ResourceCapacity(
                    total=1000,  # Mbps
                    available=1000,
                    allocated=0,
                    reserved=100,  # Reserve 100 Mbps
                    unit="Mbps"
                ),
                status=ResourceStatus.AVAILABLE,
                properties={
                    "interfaces": len(psutil.net_if_addrs()),
                    "type": "ethernet"
                }
            )
            
            # Database Connection Pool
            db_pool_resource = ResourceInstance(
                resource_id="database_connections",
                resource_type=ResourceType.DATABASE_CONNECTION,
                name="Database Connection Pool",
                capacity=ResourceCapacity(
                    total=100,
                    available=100,
                    allocated=0,
                    reserved=10,
                    unit="connections"
                ),
                status=ResourceStatus.AVAILABLE,
                properties={
                    "database_type": "postgresql",
                    "max_connections": 100
                }
            )
            
            # API Quota Resources
            api_quota_resource = ResourceInstance(
                resource_id="api_quotas",
                resource_type=ResourceType.API_QUOTA,
                name="API Request Quotas",
                capacity=ResourceCapacity(
                    total=10000,  # requests per hour
                    available=10000,
                    allocated=0,
                    reserved=1000,
                    unit="requests/hour"
                ),
                status=ResourceStatus.AVAILABLE,
                properties={
                    "rate_limit": "10000/hour",
                    "burst_limit": 100
                }
            )
            
            # Register system resources
            self.register_resource(cpu_resource)
            self.register_resource(memory_resource)
            self.register_resource(disk_resource)
            self.register_resource(network_resource)
            self.register_resource(db_pool_resource)
            self.register_resource(api_quota_resource)
            
        except Exception as e:
            logger.error(f"System resource initialization failed: {e}")
    
    def register_resource(self, resource: ResourceInstance) -> bool:
        """Register a new resource instance"""        try:
            with self.resource_locks[resource.resource_id]:
                self.resources[resource.resource_id] = resource
                
            logger.info(f"Resource registered: {resource.resource_id} ({resource.resource_type.value})")
            return True
            
        except Exception as e:
            logger.error(f"Resource registration failed: {e}")
            return False
    
    async def allocate_resources(
        self,
        consumer_id: str,
        requirements: List[ResourceRequirement],
        strategy: Optional[AllocationStrategy] = None
    ) -> Dict[str, str]:
        """Allocate resources based on requirements"""        try:
            strategy = strategy or self.default_strategy
            allocations = {}
            allocated_resources = []
            
            # Sort requirements by priority
            sorted_requirements = sorted(
                requirements, 
                key=lambda r: r.priority.value
            )
            
            try:
                # Attempt to allocate all required resources
                for requirement in sorted_requirements:
                    allocation_id = await self._allocate_single_resource(
                        consumer_id, requirement, strategy
                    )
                    
                    if allocation_id:
                        allocations[requirement.resource_type.value] = allocation_id
                        allocated_resources.append(allocation_id)
                    else:
                        # Allocation failed, rollback all previous allocations
                        for rollback_id in allocated_resources:
                            await self.deallocate_resource(rollback_id)
                        
                        raise Exception(f"Failed to allocate {requirement.resource_type.value}")
                
                # Emit allocation success event
                await self._emit_resource_event("resources_allocated", {
                    "consumer_id": consumer_id,
                    "allocations": allocations,
                    "strategy": strategy.value
                })
                
                logger.info(f"Resources allocated for consumer {consumer_id}: {allocations}")
                return allocations
                
            except Exception as e:
                logger.error(f"Resource allocation failed: {e}")
                raise
                
        except Exception as e:
            logger.error(f"Resource allocation error: {e}")
            raise
    
    async def _allocate_single_resource(
        self,
        consumer_id: str,
        requirement: ResourceRequirement,
        strategy: AllocationStrategy
    ) -> Optional[str]:
        """Allocate a single resource using specified strategy"""        try:
            # Get suitable resources
            candidates = self._find_suitable_resources(requirement)
            
            if not candidates:
                logger.warning(f"No suitable resources found for {requirement.resource_type.value}")
                return None
            
            # Apply allocation strategy
            selected_resource = await self.strategy_handlers[strategy](
                candidates, requirement
            )
            
            if not selected_resource:
                return None
            
            # Create allocation
            allocation_id = str(uuid.uuid4())
            expires_at = None
            
            if requirement.duration_seconds:
                expires_at = datetime.now(timezone.utc) + timedelta(
                    seconds=requirement.duration_seconds
                )
            
            allocation = ResourceAllocation(
                allocation_id=allocation_id,
                resource_id=selected_resource.resource_id,
                consumer_id=consumer_id,
                resource_type=requirement.resource_type,
                allocated_amount=requirement.amount,
                allocated_at=datetime.now(timezone.utc),
                expires_at=expires_at,
                metadata=requirement.metadata
            )
            
            # Update resource state
            with self.resource_locks[selected_resource.resource_id]:
                selected_resource.capacity.allocated += requirement.amount
                selected_resource.capacity.available -= requirement.amount
                selected_resource.allocations.append(allocation_id)
                selected_resource.last_updated = datetime.now(timezone.utc)
            
            # Store allocation
            self.allocations[allocation_id] = allocation
            
            # Track metrics
            self.allocation_metrics[requirement.resource_type.value].append(
                requirement.amount
            )
            
            logger.info(f"Resource allocated: {allocation_id} for {consumer_id}")
            return allocation_id
            
        except Exception as e:
            logger.error(f"Single resource allocation failed: {e}")
            return None
    
    def _find_suitable_resources(
        self, 
        requirement: ResourceRequirement
    ) -> List[ResourceInstance]:
        """Find resources suitable for the requirement"""        candidates = []
        
        for resource in self.resources.values():
            if (resource.resource_type == requirement.resource_type and
                resource.status == ResourceStatus.AVAILABLE and
                resource.capacity.available >= requirement.amount):
                
                # Check constraints
                if self._meets_constraints(resource, requirement.constraints):
                    candidates.append(resource)
        
        return candidates
    
    def _meets_constraints(
        self, 
        resource: ResourceInstance, 
        constraints: Dict[str, Any]
    ) -> bool:
        """Check if resource meets allocation constraints"""        try:
            for constraint_key, constraint_value in constraints.items():
                if constraint_key == "location":
                    if resource.location != constraint_value:
                        return False
                elif constraint_key == "min_health_score":
                    if resource.health_score < constraint_value:
                        return False
                elif constraint_key == "max_utilization":
                    if resource.capacity.utilization_percentage > constraint_value:
                        return False
                elif constraint_key in resource.properties:
                    if resource.properties[constraint_key] != constraint_value:
                        return False
            
            return True
            
        except Exception as e:
            logger.error(f"Constraint checking failed: {e}")
            return False
    
    async def _allocate_first_fit(
        self, 
        candidates: List[ResourceInstance], 
        requirement: ResourceRequirement
    ) -> Optional[ResourceInstance]:
        """First-fit allocation strategy"""        return candidates[0] if candidates else None
    
    async def _allocate_best_fit(
        self, 
        candidates: List[ResourceInstance], 
        requirement: ResourceRequirement
    ) -> Optional[ResourceInstance]:
        """Best-fit allocation strategy"""        if not candidates:
            return None
        
        # Find resource with minimum waste
        best_candidate = min(
            candidates,
            key=lambda r: r.capacity.available - requirement.amount
        )
        
        return best_candidate
    
    async def _allocate_worst_fit(
        self, 
        candidates: List[ResourceInstance], 
        requirement: ResourceRequirement
    ) -> Optional[ResourceInstance]:
        """Worst-fit allocation strategy"""        if not candidates:
            return None
        
        # Find resource with maximum remaining capacity
        worst_candidate = max(
            candidates,
            key=lambda r: r.capacity.available - requirement.amount
        )
        
        return worst_candidate
    
    async def _allocate_round_robin(
        self, 
        candidates: List[ResourceInstance], 
        requirement: ResourceRequirement
    ) -> Optional[ResourceInstance]:
        """Round-robin allocation strategy"""        if not candidates:
            return None
        
        # Simple round-robin based on allocation count
        return min(candidates, key=lambda r: len(r.allocations))
    
    async def _allocate_priority_based(
        self, 
        candidates: List[ResourceInstance], 
        requirement: ResourceRequirement
    ) -> Optional[ResourceInstance]:
        """Priority-based allocation strategy"""        if not candidates:
            return None
        
        # Allocate based on resource health score and availability
        return max(
            candidates,
            key=lambda r: (r.health_score, r.capacity.available)
        )
    
    async def _allocate_load_balanced(
        self, 
        candidates: List[ResourceInstance], 
        requirement: ResourceRequirement
    ) -> Optional[ResourceInstance]:
        """Load-balanced allocation strategy"""        if not candidates:
            return None
        
        # Find resource with lowest utilization
        return min(
            candidates,
            key=lambda r: r.capacity.utilization_percentage
        )
    
    async def _allocate_fair_share(
        self, 
        candidates: List[ResourceInstance], 
        requirement: ResourceRequirement
    ) -> Optional[ResourceInstance]:
        """Fair-share allocation strategy"""        if not candidates:
            return None
        
        # Distribute load fairly across resources
        return min(candidates, key=lambda r: len(r.allocations))
    
    async def _allocate_predictive(
        self, 
        candidates: List[ResourceInstance], 
        requirement: ResourceRequirement
    ) -> Optional[ResourceInstance]:
        """Predictive allocation strategy"""        if not candidates:
            return None
        
        # Use historical data to predict best allocation
        # For now, use best-fit as fallback
        return await self._allocate_best_fit(candidates, requirement)
    
    async def deallocate_resource(self, allocation_id: str) -> bool:
        """Deallocate a previously allocated resource"""        try:
            if allocation_id not in self.allocations:
                logger.warning(f"Allocation not found: {allocation_id}")
                return False
            
            allocation = self.allocations[allocation_id]
            resource = self.resources.get(allocation.resource_id)
            
            if not resource:
                logger.error(f"Resource not found: {allocation.resource_id}")
                return False
            
            # Update resource state
            with self.resource_locks[resource.resource_id]:
                resource.capacity.allocated -= allocation.allocated_amount
                resource.capacity.available += allocation.allocated_amount
                
                if allocation_id in resource.allocations:
                    resource.allocations.remove(allocation_id)
                
                resource.last_updated = datetime.now(timezone.utc)
            
            # Remove allocation
            del self.allocations[allocation_id]
            
            # Emit deallocation event
            await self._emit_resource_event("resource_deallocated", {
                "allocation_id": allocation_id,
                "consumer_id": allocation.consumer_id,
                "resource_id": allocation.resource_id,
                "amount": allocation.allocated_amount
            })
            
            logger.info(f"Resource deallocated: {allocation_id}")
            return True
            
        except Exception as e:
            logger.error(f"Resource deallocation failed: {e}")
            return False
    
    async def deallocate_consumer_resources(self, consumer_id: str) -> int:
        """Deallocate all resources for a specific consumer"""        try:
            consumer_allocations = [
                allocation_id for allocation_id, allocation in self.allocations.items()
                if allocation.consumer_id == consumer_id
            ]
            
            deallocated_count = 0
            for allocation_id in consumer_allocations:
                if await self.deallocate_resource(allocation_id):
                    deallocated_count += 1
            
            logger.info(f"Deallocated {deallocated_count} resources for consumer {consumer_id}")
            return deallocated_count
            
        except Exception as e:
            logger.error(f"Consumer resource deallocation failed: {e}")
            return 0
    
    def start_monitoring(self):
        """Start resource monitoring"""        if not self.monitoring_active:
            self.monitoring_active = True
            self.monitoring_thread = threading.Thread(
                target=self._monitoring_loop,
                daemon=True
            )
            self.monitoring_thread.start()
            logger.info("Resource monitoring started")
    
    def stop_monitoring(self):
        """Stop resource monitoring"""        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        logger.info("Resource monitoring stopped")
    
    def _monitoring_loop(self):
        """Continuous resource monitoring loop"""        while self.monitoring_active:
            try:
                self._update_resource_metrics()
                self._check_resource_health()
                self._handle_expired_allocations()
                self._generate_optimization_recommendations()
                time.sleep(self.monitoring_interval)
            except Exception as e:
                logger.error(f"Monitoring loop error: {e}")
    
    def _update_resource_metrics(self):
        """Update resource utilization metrics"""        try:
            for resource in self.resources.values():
                with self.resource_locks[resource.resource_id]:
                    # Update system resource metrics
                    if resource.resource_type == ResourceType.CPU:
                        resource.capacity.available = psutil.cpu_count() - resource.capacity.allocated
                    
                    elif resource.resource_type == ResourceType.MEMORY:
                        memory_info = psutil.virtual_memory()
                        total_gb = memory_info.total / (1024**3)
                        available_gb = memory_info.available / (1024**3)
                        resource.capacity.total = total_gb
                        resource.capacity.available = available_gb - resource.capacity.allocated
                    
                    elif resource.resource_type == ResourceType.DISK:
                        disk_info = psutil.disk_usage('/')
                        total_gb = disk_info.total / (1024**3)
                        available_gb = disk_info.free / (1024**3)
                        resource.capacity.total = total_gb
                        resource.capacity.available = available_gb - resource.capacity.allocated
                    
                    # Record utilization history
                    utilization_record = {
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "utilization_percentage": resource.capacity.utilization_percentage,
                        "allocated": resource.capacity.allocated,
                        "available": resource.capacity.available,
                        "health_score": resource.health_score
                    }
                    
                    self.utilization_history[resource.resource_id].append(utilization_record)
                    
                    # Keep only last 100 records
                    if len(self.utilization_history[resource.resource_id]) > 100:
                        self.utilization_history[resource.resource_id].pop(0)
                    
        except Exception as e:
            logger.error(f"Resource metrics update failed: {e}")
    
    def _check_resource_health(self):
        """Check health status of all resources"""        try:
            for resource in self.resources.values():
                with self.resource_locks[resource.resource_id]:
                    previous_health = resource.health_score
                    
                    # Calculate health based on utilization and availability
                    utilization = resource.capacity.utilization_percentage
                    
                    if utilization > 95:
                        resource.health_score = 20  # Critical
                        resource.status = ResourceStatus.DEGRADED
                    elif utilization > 85:
                        resource.health_score = 40  # Warning
                    elif utilization > 70:
                        resource.health_score = 70  # Moderate
                    else:
                        resource.health_score = 100  # Good
                        resource.status = ResourceStatus.AVAILABLE
                    
                    # Detect health score changes
                    if abs(resource.health_score - previous_health) > 20:
                        asyncio.create_task(self._emit_resource_event("health_changed", {
                            "resource_id": resource.resource_id,
                            "previous_health": previous_health,
                            "current_health": resource.health_score,
                            "status": resource.status.value
                        }))
                    
        except Exception as e:
            logger.error(f"Resource health check failed: {e}")
    
    def _handle_expired_allocations(self):
        """Handle expired resource allocations"""        try:
            now = datetime.now(timezone.utc)
            expired_allocations = []
            
            for allocation_id, allocation in self.allocations.items():
                if (allocation.expires_at and allocation.expires_at <= now):
                    expired_allocations.append(allocation_id)
            
            # Deallocate expired resources
            for allocation_id in expired_allocations:
                asyncio.create_task(self.deallocate_resource(allocation_id))
                logger.info(f"Expired allocation deallocated: {allocation_id}")
                
        except Exception as e:
            logger.error(f"Expired allocation handling failed: {e}")
    
    def _generate_optimization_recommendations(self):
        """Generate resource optimization recommendations"""        try:
            recommendations = []
            
            for resource in self.resources.values():
                utilization = resource.capacity.utilization_percentage
                
                # High utilization recommendation
                if utilization > 85:
                    recommendations.append({
                        "type": "high_utilization",
                        "resource_id": resource.resource_id,
                        "resource_type": resource.resource_type.value,
                        "utilization": utilization,
                        "recommendation": "Consider scaling up or load balancing",
                        "priority": "high",
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    })
                
                # Low utilization recommendation
                elif utilization < 20 and len(resource.allocations) > 0:
                    recommendations.append({
                        "type": "low_utilization",
                        "resource_id": resource.resource_id,
                        "resource_type": resource.resource_type.value,
                        "utilization": utilization,
                        "recommendation": "Consider consolidating or scaling down",
                        "priority": "medium",
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    })
            
            # Update recommendations
            self.optimization_recommendations = recommendations[-50:]  # Keep last 50
            
        except Exception as e:
            logger.error(f"Optimization recommendation generation failed: {e}")
    
    async def _emit_resource_event(self, event_type: str, event_data: Dict[str, Any]):
        """Emit resource events to registered handlers"""        try:
            event_data.update({
                "event_type": event_type,
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
            
            # Call registered event handlers
            for handler in self.event_handlers.get(event_type, []):
                try:
                    await handler(event_data)
                except Exception as e:
                    logger.error(f"Event handler failed: {e}")
                    
        except Exception as e:
            logger.error(f"Event emission failed: {e}")
    
    def get_resource_status(self, resource_id: str) -> Optional[Dict[str, Any]]:
        """Get current resource status"""        resource = self.resources.get(resource_id)
        if not resource:
            return None
        
        return {
            "resource_id": resource.resource_id,
            "resource_type": resource.resource_type.value,
            "name": resource.name,
            "status": resource.status.value,
            "capacity": {
                "total": resource.capacity.total,
                "available": resource.capacity.available,
                "allocated": resource.capacity.allocated,
                "reserved": resource.capacity.reserved,
                "utilization_percentage": resource.capacity.utilization_percentage,
                "unit": resource.capacity.unit
            },
            "health_score": resource.health_score,
            "active_allocations": len(resource.allocations),
            "last_updated": resource.last_updated.isoformat()
        }
    
    def get_allocation_status(self, allocation_id: str) -> Optional[Dict[str, Any]]:
        """Get allocation status"""        allocation = self.allocations.get(allocation_id)
        if not allocation:
            return None
        
        return {
            "allocation_id": allocation.allocation_id,
            "resource_id": allocation.resource_id,
            "consumer_id": allocation.consumer_id,
            "resource_type": allocation.resource_type.value,
            "allocated_amount": allocation.allocated_amount,
            "allocated_at": allocation.allocated_at.isoformat(),
            "expires_at": allocation.expires_at.isoformat() if allocation.expires_at else None,
            "metadata": allocation.metadata,
            "performance_metrics": allocation.performance_metrics
        }
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get comprehensive system resource metrics"""        total_resources = len(self.resources)
        active_allocations = len(self.allocations)
        
        # Calculate overall utilization by resource type
        utilization_by_type = {}
        for resource_type in ResourceType:
            type_resources = [r for r in self.resources.values() if r.resource_type == resource_type]
            if type_resources:
                avg_utilization = sum(r.capacity.utilization_percentage for r in type_resources) / len(type_resources)
                utilization_by_type[resource_type.value] = avg_utilization
        
        return {
            "total_resources": total_resources,
            "active_allocations": active_allocations,
            "utilization_by_type": utilization_by_type,
            "allocation_metrics": dict(self.allocation_metrics),
            "optimization_recommendations": self.optimization_recommendations,
            "healthy_resources": len([r for r in self.resources.values() if r.health_score > 70]),
            "degraded_resources": len([r for r in self.resources.values() if r.health_score <= 70])
        }
    
    def register_event_handler(self, event_type: str, handler: Callable):
        """Register event handler for resource events"""        self.event_handlers[event_type].append(handler)
    
    def set_default_strategy(self, strategy: AllocationStrategy):
        """Set default allocation strategy"""        self.default_strategy = strategy
        logger.info(f"Default allocation strategy set to: {strategy.value}")
    
    def shutdown(self):
        """Shutdown resource coordinator and cleanup"""        try:
            self.stop_monitoring()
            
            # Deallocate all resources
            for allocation_id in list(self.allocations.keys()):
                asyncio.create_task(self.deallocate_resource(allocation_id))
            
            logger.info("ResourceCoordinator shutdown completed")
            
        except Exception as e:
            logger.error(f"ResourceCoordinator shutdown failed: {e}")
