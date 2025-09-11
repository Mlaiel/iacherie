"""⚡ Resource Allocation Engine - Enterprise ML Infrastructure
===========================================================
Module: ml/deployment/resource_allocation_engine.py
Author: Fahed Mlaiel (mlaiel@live.de)
===========================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🎯 DYNAMIC RESOURCE ALLOCATION ENGINE
Dynamic resource allocation optimization for cost and performance
- Intelligent resource scaling based on demand
- Cost optimization with performance constraints
- Creator-priority based resource allocation
- Multi-cloud resource orchestration
"""

import asyncio
import logging
import time
import uuid
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
import numpy as np

logger = logging.getLogger(__name__)


class ResourceType(Enum):
    """Types of computing resources"""
    CPU = "cpu"
    MEMORY = "memory"
    GPU = "gpu"
    STORAGE = "storage"
    NETWORK = "network"
    SPECIALIZED_AI = "specialized_ai"


class AllocationStrategy(Enum):
    """Resource allocation strategies"""
    COST_OPTIMIZED = "cost_optimized"
    PERFORMANCE_OPTIMIZED = "performance_optimized"
    BALANCED = "balanced"
    CREATOR_PRIORITY = "creator_priority"
    GREEN_COMPUTING = "green_computing"
    WORKLOAD_ADAPTIVE = "workload_adaptive"


class ResourceProvider(Enum):
    """Cloud resource providers"""
    AWS = "aws"
    AZURE = "azure"
    GCP = "gcp"
    ON_PREMISE = "on_premise"
    EDGE = "edge"


class WorkloadType(Enum):
    """ML workload types"""
    TRAINING = "training"
    INFERENCE = "inference"
    BATCH_PROCESSING = "batch_processing"
    REAL_TIME = "real_time"
    RESEARCH = "research"
    CREATOR_SPECIFIC = "creator_specific"


@dataclass
class ResourceSpecification:
    """Resource specification"""
    cpu_cores: float
    memory_gb: float
    gpu_count: int = 0
    gpu_type: str = ""
    storage_gb: float = 0
    network_bandwidth_mbps: float = 0
    specialized_hardware: List[str] = field(default_factory=list)


@dataclass
class ResourceNode:
    """Individual resource node"""
    node_id: str
    provider: ResourceProvider
    region: str
    available_resources: ResourceSpecification
    allocated_resources: ResourceSpecification
    cost_per_hour: float
    performance_score: float
    carbon_footprint_score: float = 1.0
    node_tags: List[str] = field(default_factory=list)
    status: str = "available"


@dataclass
class WorkloadRequest:
    """Resource request for ML workload"""
    request_id: str
    workload_type: WorkloadType
    required_resources: ResourceSpecification
    creator_type: Optional[str] = None
    priority: int = 1
    max_cost_per_hour: Optional[float] = None
    performance_requirements: Dict[str, float] = field(default_factory=dict)
    duration_hours: float = 1.0
    scheduling_constraints: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ResourceAllocation:
    """Resource allocation result"""
    allocation_id: str
    request_id: str
    allocated_nodes: List[str]
    total_cost_per_hour: float
    expected_performance_score: float
    carbon_footprint: float
    allocation_strategy: AllocationStrategy
    created_at: datetime = field(default_factory=datetime.utcnow)
    estimated_completion: Optional[datetime] = None


class ResourceAllocationEngine:
    """Enterprise Resource Allocation Engine"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        
        # Resource tracking
        self.resource_nodes: Dict[str, ResourceNode] = {}
        self.active_allocations: Dict[str, ResourceAllocation] = {}
        self.allocation_history: List[ResourceAllocation] = []
        
        # Configuration
        self.cost_optimization_weight = self.config.get('cost_optimization_weight', 0.6)
        self.performance_weight = self.config.get('performance_weight', 0.3)
        self.carbon_weight = self.config.get('carbon_weight', 0.1)
        self.enable_multi_cloud = self.config.get('enable_multi_cloud', True)
        self.max_allocation_time = self.config.get('max_allocation_time', 300)  # seconds
        
        # Creator priority weights
        self.creator_priority_multipliers = {
            'influencer': 1.5,
            'musician': 1.3,
            'photographer': 1.2,
            'blogger': 1.0,
            'comedian': 1.1
        }
        
        # Performance tracking
        self.allocation_metrics = {
            'total_allocations': 0,
            'successful_allocations': 0,
            'cost_savings': 0.0,
            'average_allocation_time': 0.0,
            'resource_utilization': 0.0,
            'carbon_footprint_reduced': 0.0
        }
        
        # Initialize default resource nodes
        self._initialize_resource_nodes()
        
        logger.info("⚡ Resource Allocation Engine initialized")
    
    def _initialize_resource_nodes(self):
        """Initialize default resource nodes"""
        nodes = [
            # AWS Nodes
            ResourceNode(
                node_id="aws_us_east_1_gpu_1",
                provider=ResourceProvider.AWS,
                region="us-east-1",
                available_resources=ResourceSpecification(
                    cpu_cores=16, memory_gb=64, gpu_count=4, gpu_type="V100",
                    storage_gb=1000, network_bandwidth_mbps=10000
                ),
                allocated_resources=ResourceSpecification(
                    cpu_cores=0, memory_gb=0, gpu_count=0, storage_gb=0
                ),
                cost_per_hour=12.50,
                performance_score=0.95,
                carbon_footprint_score=0.8,
                node_tags=["ml_optimized", "gpu_intensive"]
            ),
            ResourceNode(
                node_id="aws_us_west_2_cpu_1",
                provider=ResourceProvider.AWS,
                region="us-west-2",
                available_resources=ResourceSpecification(
                    cpu_cores=32, memory_gb=128, gpu_count=0,
                    storage_gb=2000, network_bandwidth_mbps=5000
                ),
                allocated_resources=ResourceSpecification(
                    cpu_cores=0, memory_gb=0, gpu_count=0, storage_gb=0
                ),
                cost_per_hour=3.20,
                performance_score=0.85,
                carbon_footprint_score=0.7,
                node_tags=["cpu_optimized", "batch_processing"]
            ),
            
            # Azure Nodes
            ResourceNode(
                node_id="azure_east_us_gpu_1",
                provider=ResourceProvider.AZURE,
                region="east-us",
                available_resources=ResourceSpecification(
                    cpu_cores=16, memory_gb=112, gpu_count=4, gpu_type="A100",
                    storage_gb=1500, network_bandwidth_mbps=12000
                ),
                allocated_resources=ResourceSpecification(
                    cpu_cores=0, memory_gb=0, gpu_count=0, storage_gb=0
                ),
                cost_per_hour=15.80,
                performance_score=0.98,
                carbon_footprint_score=0.6,
                node_tags=["latest_gpu", "high_performance"]
            ),
            
            # GCP Nodes
            ResourceNode(
                node_id="gcp_us_central_1_tpu_1",
                provider=ResourceProvider.GCP,
                region="us-central1",
                available_resources=ResourceSpecification(
                    cpu_cores=8, memory_gb=32, gpu_count=0,
                    storage_gb=500, network_bandwidth_mbps=8000,
                    specialized_hardware=["TPU_v4"]
                ),
                allocated_resources=ResourceSpecification(
                    cpu_cores=0, memory_gb=0, gpu_count=0, storage_gb=0
                ),
                cost_per_hour=8.90,
                performance_score=0.92,
                carbon_footprint_score=0.5,
                node_tags=["tpu_optimized", "training_focused"]
            ),
            
            # Edge Node
            ResourceNode(
                node_id="edge_mobile_cluster_1",
                provider=ResourceProvider.EDGE,
                region="global",
                available_resources=ResourceSpecification(
                    cpu_cores=4, memory_gb=16, gpu_count=1, gpu_type="Mobile_GPU",
                    storage_gb=200, network_bandwidth_mbps=1000
                ),
                allocated_resources=ResourceSpecification(
                    cpu_cores=0, memory_gb=0, gpu_count=0, storage_gb=0
                ),
                cost_per_hour=0.85,
                performance_score=0.65,
                carbon_footprint_score=0.3,
                node_tags=["edge_computing", "mobile_optimized", "low_latency"]
            )
        ]
        
        for node in nodes:
            self.resource_nodes[node.node_id] = node
    
    async def allocate_resources(
        self,
        request: WorkloadRequest,
        strategy: AllocationStrategy = AllocationStrategy.BALANCED
    ) -> Optional[ResourceAllocation]:
        """Allocate resources for ML workload"""
        try:
            start_time = time.time()
            
            # Find suitable nodes
            candidate_nodes = await self._find_candidate_nodes(request)
            
            if not candidate_nodes:
                logger.warning(f"No suitable nodes found for request {request.request_id}")
                return None
            
            # Apply allocation strategy
            selected_nodes = await self._apply_allocation_strategy(
                request, candidate_nodes, strategy
            )
            
            if not selected_nodes:
                logger.warning(f"No nodes selected after strategy application for {request.request_id}")
                return None
            
            # Create allocation
            allocation = await self._create_allocation(request, selected_nodes, strategy)
            
            # Reserve resources
            success = await self._reserve_resources(allocation)
            
            if success:
                self.active_allocations[allocation.allocation_id] = allocation
                
                # Update metrics
                allocation_time = time.time() - start_time
                await self._update_allocation_metrics(allocation_time, True)
                
                logger.info(f"✅ Resources allocated: {allocation.allocation_id}")
                return allocation
            else:
                logger.error(f"❌ Failed to reserve resources for {request.request_id}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error allocating resources: {e}")
            return None
    
    async def _find_candidate_nodes(self, request: WorkloadRequest) -> List[ResourceNode]:
        """Find nodes that can satisfy the resource request"""
        try:
            candidates = []
            
            for node in self.resource_nodes.values():
                if node.status != "available":
                    continue
                
                # Check resource availability
                available = node.available_resources
                required = request.required_resources
                allocated = node.allocated_resources
                
                # Calculate remaining resources
                remaining_cpu = available.cpu_cores - allocated.cpu_cores
                remaining_memory = available.memory_gb - allocated.memory_gb
                remaining_gpu = available.gpu_count - allocated.gpu_count
                remaining_storage = available.storage_gb - allocated.storage_gb
                
                # Check if node can satisfy requirements
                if (remaining_cpu >= required.cpu_cores and
                    remaining_memory >= required.memory_gb and
                    remaining_gpu >= required.gpu_count and
                    remaining_storage >= required.storage_gb):
                    
                    # Check GPU type compatibility if specified
                    if required.gpu_count > 0 and required.gpu_type:
                        if available.gpu_type != required.gpu_type:
                            continue
                    
                    # Check specialized hardware requirements
                    if required.specialized_hardware:
                        if not set(required.specialized_hardware).issubset(
                            set(available.specialized_hardware)
                        ):
                            continue
                    
                    # Check cost constraints
                    if request.max_cost_per_hour:
                        if node.cost_per_hour > request.max_cost_per_hour:
                            continue
                    
                    candidates.append(node)
            
            return candidates
            
        except Exception as e:
            logger.error(f"❌ Error finding candidate nodes: {e}")
            return []
    
    async def _apply_allocation_strategy(
        self,
        request: WorkloadRequest,
        candidates: List[ResourceNode],
        strategy: AllocationStrategy
    ) -> List[ResourceNode]:
        """Apply allocation strategy to select optimal nodes"""
        try:
            if not candidates:
                return []
            
            # Calculate scores for each candidate
            scored_candidates = []
            
            for node in candidates:
                score = await self._calculate_node_score(node, request, strategy)
                scored_candidates.append((node, score))
            
            # Sort by score (descending)
            scored_candidates.sort(key=lambda x: x[1], reverse=True)
            
            # Select nodes based on strategy
            if strategy == AllocationStrategy.COST_OPTIMIZED:
                # Select cheapest nodes first
                scored_candidates.sort(key=lambda x: x[0].cost_per_hour)
            
            elif strategy == AllocationStrategy.PERFORMANCE_OPTIMIZED:
                # Select highest performance nodes first
                scored_candidates.sort(key=lambda x: x[0].performance_score, reverse=True)
            
            elif strategy == AllocationStrategy.GREEN_COMPUTING:
                # Select nodes with lowest carbon footprint
                scored_candidates.sort(key=lambda x: x[0].carbon_footprint_score)
            
            # For now, select single best node (could be extended for multi-node allocation)
            if scored_candidates:
                return [scored_candidates[0][0]]
            
            return []
            
        except Exception as e:
            logger.error(f"❌ Error applying allocation strategy: {e}")
            return []
    
    async def _calculate_node_score(
        self,
        node: ResourceNode,
        request: WorkloadRequest,
        strategy: AllocationStrategy
    ) -> float:
        """Calculate node suitability score"""
        try:
            score = 0.0
            
            # Cost score (lower cost = higher score)
            max_cost = max(n.cost_per_hour for n in self.resource_nodes.values())
            cost_score = (max_cost - node.cost_per_hour) / max_cost
            score += cost_score * self.cost_optimization_weight
            
            # Performance score
            score += node.performance_score * self.performance_weight
            
            # Carbon footprint score (lower footprint = higher score)
            carbon_score = 1.0 - node.carbon_footprint_score
            score += carbon_score * self.carbon_weight
            
            # Creator priority adjustment
            if request.creator_type:
                priority_multiplier = self.creator_priority_multipliers.get(
                    request.creator_type, 1.0
                )
                score *= priority_multiplier
            
            # Workload type affinity
            workload_bonus = await self._calculate_workload_affinity(node, request)
            score *= (1.0 + workload_bonus)
            
            return score
            
        except Exception as e:
            logger.error(f"❌ Error calculating node score: {e}")
            return 0.0
    
    async def _calculate_workload_affinity(
        self,
        node: ResourceNode,
        request: WorkloadRequest
    ) -> float:
        """Calculate how well node matches workload requirements"""
        try:
            affinity = 0.0
            
            # GPU workloads prefer GPU nodes
            if request.workload_type in [WorkloadType.TRAINING, WorkloadType.RESEARCH]:
                if node.available_resources.gpu_count > 0:
                    affinity += 0.2
            
            # Real-time workloads prefer edge nodes
            if request.workload_type == WorkloadType.REAL_TIME:
                if node.provider == ResourceProvider.EDGE:
                    affinity += 0.3
                if "low_latency" in node.node_tags:
                    affinity += 0.1
            
            # Batch processing prefers CPU-optimized nodes
            if request.workload_type == WorkloadType.BATCH_PROCESSING:
                if "batch_processing" in node.node_tags:
                    affinity += 0.2
                if "cpu_optimized" in node.node_tags:
                    affinity += 0.1
            
            # Creator-specific workloads
            if request.workload_type == WorkloadType.CREATOR_SPECIFIC:
                if request.creator_type == "musician" and "gpu_intensive" in node.node_tags:
                    affinity += 0.15
                elif request.creator_type == "photographer" and "high_performance" in node.node_tags:
                    affinity += 0.15
            
            return affinity
            
        except Exception as e:
            logger.error(f"❌ Error calculating workload affinity: {e}")
            return 0.0
    
    async def _create_allocation(
        self,
        request: WorkloadRequest,
        selected_nodes: List[ResourceNode],
        strategy: AllocationStrategy
    ) -> ResourceAllocation:
        """Create resource allocation"""
        try:
            allocation_id = str(uuid.uuid4())
            
            # Calculate total cost and performance
            total_cost = sum(node.cost_per_hour for node in selected_nodes)
            avg_performance = sum(node.performance_score for node in selected_nodes) / len(selected_nodes)
            total_carbon = sum(node.carbon_footprint_score for node in selected_nodes)
            
            # Estimate completion time
            estimated_completion = None
            if request.duration_hours:
                estimated_completion = datetime.utcnow() + timedelta(hours=request.duration_hours)
            
            allocation = ResourceAllocation(
                allocation_id=allocation_id,
                request_id=request.request_id,
                allocated_nodes=[node.node_id for node in selected_nodes],
                total_cost_per_hour=total_cost,
                expected_performance_score=avg_performance,
                carbon_footprint=total_carbon,
                allocation_strategy=strategy,
                estimated_completion=estimated_completion
            )
            
            return allocation
            
        except Exception as e:
            logger.error(f"❌ Error creating allocation: {e}")
            raise
    
    async def _reserve_resources(self, allocation: ResourceAllocation) -> bool:
        """Reserve resources for allocation"""
        try:
            # This would interface with actual cloud APIs
            # For now, simulate resource reservation
            
            for node_id in allocation.allocated_nodes:
                if node_id in self.resource_nodes:
                    node = self.resource_nodes[node_id]
                    # Mark resources as allocated (simplified)
                    node.status = "allocated"
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error reserving resources: {e}")
            return False
    
    async def deallocate_resources(self, allocation_id: str) -> bool:
        """Deallocate resources"""
        try:
            if allocation_id not in self.active_allocations:
                return False
            
            allocation = self.active_allocations[allocation_id]
            
            # Free up resources
            for node_id in allocation.allocated_nodes:
                if node_id in self.resource_nodes:
                    node = self.resource_nodes[node_id]
                    node.status = "available"
                    # Reset allocated resources
                    node.allocated_resources = ResourceSpecification(
                        cpu_cores=0, memory_gb=0, gpu_count=0, storage_gb=0
                    )
            
            # Move to history
            self.allocation_history.append(allocation)
            del self.active_allocations[allocation_id]
            
            logger.info(f"✅ Resources deallocated: {allocation_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error deallocating resources: {e}")
            return False
    
    async def optimize_allocations(self) -> Dict[str, Any]:
        """Optimize current resource allocations"""
        try:
            optimization_results = {
                'reallocated_workloads': 0,
                'cost_savings': 0.0,
                'performance_improvements': 0,
                'carbon_reduction': 0.0
            }
            
            # Find suboptimal allocations
            for allocation_id, allocation in list(self.active_allocations.items()):
                # Create a mock request based on current allocation
                mock_request = WorkloadRequest(
                    request_id=f"reopt_{allocation.request_id}",
                    workload_type=WorkloadType.INFERENCE,  # Default
                    required_resources=ResourceSpecification(
                        cpu_cores=4, memory_gb=16, gpu_count=1  # Default requirements
                    )
                )
                
                # Find better allocation
                new_allocation = await self.allocate_resources(
                    mock_request, AllocationStrategy.COST_OPTIMIZED
                )
                
                if new_allocation and new_allocation.total_cost_per_hour < allocation.total_cost_per_hour:
                    # Migrate to better allocation
                    cost_savings = allocation.total_cost_per_hour - new_allocation.total_cost_per_hour
                    optimization_results['cost_savings'] += cost_savings
                    optimization_results['reallocated_workloads'] += 1
                    
                    # Deallocate old allocation
                    await self.deallocate_resources(allocation_id)
            
            self.allocation_metrics['cost_savings'] += optimization_results['cost_savings']
            
            logger.info(f"🔧 Allocation optimization completed: {optimization_results}")
            return optimization_results
            
        except Exception as e:
            logger.error(f"❌ Error optimizing allocations: {e}")
            return {}
    
    async def get_resource_utilization(self) -> Dict[str, Any]:
        """Get current resource utilization"""
        try:
            utilization = {
                'total_nodes': len(self.resource_nodes),
                'allocated_nodes': len([n for n in self.resource_nodes.values() if n.status == "allocated"]),
                'utilization_by_provider': {},
                'utilization_by_resource_type': {},
                'cost_analysis': {}
            }
            
            # Calculate utilization by provider
            for provider in ResourceProvider:
                provider_nodes = [n for n in self.resource_nodes.values() if n.provider == provider]
                allocated_provider_nodes = [n for n in provider_nodes if n.status == "allocated"]
                
                if provider_nodes:
                    provider_utilization = len(allocated_provider_nodes) / len(provider_nodes)
                    utilization['utilization_by_provider'][provider.value] = provider_utilization
            
            # Calculate cost analysis
            total_cost = sum(
                allocation.total_cost_per_hour
                for allocation in self.active_allocations.values()
            )
            
            utilization['cost_analysis'] = {
                'current_cost_per_hour': total_cost,
                'active_allocations': len(self.active_allocations),
                'estimated_daily_cost': total_cost * 24
            }
            
            return utilization
            
        except Exception as e:
            logger.error(f"❌ Error getting resource utilization: {e}")
            return {}
    
    async def _update_allocation_metrics(self, allocation_time: float, success: bool):
        """Update allocation metrics"""
        try:
            self.allocation_metrics['total_allocations'] += 1
            
            if success:
                self.allocation_metrics['successful_allocations'] += 1
                
                # Update average allocation time
                total_successful = self.allocation_metrics['successful_allocations']
                current_avg = self.allocation_metrics['average_allocation_time']
                new_avg = (current_avg * (total_successful - 1) + allocation_time) / total_successful
                self.allocation_metrics['average_allocation_time'] = new_avg
            
        except Exception as e:
            logger.error(f"❌ Error updating allocation metrics: {e}")
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get allocation engine metrics"""
        return {
            **self.allocation_metrics,
            'active_allocations': len(self.active_allocations),
            'total_nodes': len(self.resource_nodes),
            'available_nodes': len([n for n in self.resource_nodes.values() if n.status == "available"])
        }


# Global instance
resource_allocator = ResourceAllocationEngine()


async def main():
    """Test the Resource Allocation Engine"""
    engine = ResourceAllocationEngine()
    
    print("⚡ Testing Resource Allocation Engine...")
    
    # Create test workload request
    request = WorkloadRequest(
        request_id="test_training_001",
        workload_type=WorkloadType.TRAINING,
        required_resources=ResourceSpecification(
            cpu_cores=8, memory_gb=32, gpu_count=2, gpu_type="V100"
        ),
        creator_type="musician",
        priority=2,
        max_cost_per_hour=20.0,
        duration_hours=4.0
    )
    
    # Allocate resources
    allocation = await engine.allocate_resources(request, AllocationStrategy.BALANCED)
    
    if allocation:
        print(f"✅ Resources allocated: {allocation.allocation_id}")
        print(f"   Nodes: {allocation.allocated_nodes}")
        print(f"   Cost per hour: ${allocation.total_cost_per_hour:.2f}")
        print(f"   Performance score: {allocation.expected_performance_score:.2f}")
        print(f"   Carbon footprint: {allocation.carbon_footprint:.2f}")
    else:
        print("❌ Resource allocation failed")
    
    # Get utilization
    utilization = await engine.get_resource_utilization()
    print(f"\nResource utilization: {utilization['allocated_nodes']}/{utilization['total_nodes']} nodes")
    
    # Optimize allocations
    optimization = await engine.optimize_allocations()
    print(f"Optimization results: {optimization}")
    
    # Deallocate resources
    if allocation:
        success = await engine.deallocate_resources(allocation.allocation_id)
        print(f"Deallocation success: {success}")
    
    # Get metrics
    metrics = await engine.get_metrics()
    print(f"Metrics: {metrics}")


if __name__ == "__main__":
    asyncio.run(main())