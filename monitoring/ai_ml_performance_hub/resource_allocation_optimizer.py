# WARNING: Potential SQL injection risk - use parameterized queries
"""
🔧 Resource Allocation Optimizer - Enterprise AI/ML Resource Management
=====================================================================

Optimiseur allocation ressources IA pour Creator Economy.
Dynamic resource allocation, creator tier prioritization, cost-performance optimization.

⚠️  AVERTISSEMENT LÉGAL OBLIGATOIRE:
==========================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques

Architecture: monitoring/ai_ml_performance_hub/resource_allocation_optimizer.py
Responsabilité: Optimisation allocation ressources IA/ML Creator Economy
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + Audio + DevOps
"""

import asyncio
import logging
import statistics
import numpy as np
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import json
import uuid
import heapq
from collections import defaultdict
import time


class ResourceType(Enum):
    """Types de ressources"""
    CPU = "cpu"
    GPU = "gpu"
    MEMORY = "memory"
    STORAGE = "storage"
    NETWORK = "network"
    INFERENCE_SLOT = "inference_slot"
    TRAINING_SLOT = "training_slot"


class AllocationStrategy(Enum):
    """Stratégies allocation"""
    FAIR_SHARE = "fair_share"
    PRIORITY_BASED = "priority_based"
    PERFORMANCE_OPTIMIZED = "performance_optimized"
    COST_OPTIMIZED = "cost_optimized"
    CREATOR_TIER_WEIGHTED = "creator_tier_weighted"
    DYNAMIC_BALANCING = "dynamic_balancing"


class CreatorTierPriority(Enum):
    """Priorités tier créateur"""
    FREE = 1
    PREMIUM = 2
    ENTERPRISE = 3


class ResourceStatus(Enum):
    """Status ressources"""
    AVAILABLE = "available"
    ALLOCATED = "allocated"
    OVERLOADED = "overloaded"
    MAINTENANCE = "maintenance"
    OFFLINE = "offline"


class WorkloadType(Enum):
    """Types de charge de travail"""
    INFERENCE = "inference"
    TRAINING = "training"
    BATCH_PROCESSING = "batch_processing"
    REAL_TIME_PROCESSING = "real_time_processing"
    DATA_PREPROCESSING = "data_preprocessing"


@dataclass
class ResourceUnit:
    """Unité ressource"""
    resource_id: str
    resource_type: ResourceType
    capacity: float
    current_usage: float
    reserved_capacity: float
    cost_per_unit: float  # Cost per hour/unit
    performance_score: float
    status: ResourceStatus
    location: str  # Geographic location or zone
    specifications: Dict[str, Any]
    last_updated: datetime = field(default_factory=datetime.utcnow)


@dataclass
class AllocationRequest:
    """Demande allocation ressource"""
    request_id: str
    creator_id: str
    creator_tier: CreatorTierPriority
    workload_type: WorkloadType
    resource_requirements: Dict[ResourceType, float]
    priority_score: float
    max_cost_per_hour: float
    duration_estimate: float  # hours
    deadline: Optional[datetime]
    preferences: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ResourceAllocation:
    """Allocation ressource"""
    allocation_id: str
    request_id: str
    creator_id: str
    allocated_resources: Dict[str, ResourceUnit]
    allocation_strategy: AllocationStrategy
    cost_per_hour: float
    estimated_duration: float
    actual_start_time: datetime
    estimated_end_time: datetime
    actual_end_time: Optional[datetime]
    performance_metrics: Dict[str, float]
    efficiency_score: float


@dataclass
class OptimizationResult:
    """Résultat optimisation"""
    optimization_id: str
    strategy_used: AllocationStrategy
    total_resources_optimized: int
    cost_savings: float
    performance_improvement: float
    creator_satisfaction_impact: float
    efficiency_gains: Dict[ResourceType, float]
    recommendations: List[str]
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ResourcePool:
    """Pool de ressources"""
    pool_id: str
    pool_type: ResourceType
    total_capacity: float
    available_capacity: float
    reserved_capacity: float
    allocation_strategy: AllocationStrategy
    creator_tier_quotas: Dict[str, float]
    cost_model: Dict[str, float]
    performance_metrics: Dict[str, float]


class ResourceAllocationOptimizer:
    """Optimiseur allocation ressources enterprise"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = self._setup_logging()
        
        # Resource tracking
        self.resource_units: Dict[str, ResourceUnit] = {}
        self.resource_pools: Dict[str, ResourcePool] = {}
        self.allocation_requests: List[AllocationRequest] = []
        self.active_allocations: Dict[str, ResourceAllocation] = {}
        self.completed_allocations: List[ResourceAllocation] = []
        self.optimization_history: List[OptimizationResult] = []
        
        # Creator tier configurations
        self.creator_tier_configs = {
            CreatorTierPriority.FREE: {
                'max_concurrent_jobs': 2,
                'max_cpu_cores': 4,
                'max_gpu_memory': 4096,  # MB
                'max_memory': 8192,      # MB
                'priority_weight': 1.0,
                'cost_limit_per_hour': 5.0
            },
            CreatorTierPriority.PREMIUM: {
                'max_concurrent_jobs': 10,
                'max_cpu_cores': 16,
                'max_gpu_memory': 16384,
                'max_memory': 32768,
                'priority_weight': 2.0,
                'cost_limit_per_hour': 50.0
            },
            CreatorTierPriority.ENTERPRISE: {
                'max_concurrent_jobs': 50,
                'max_cpu_cores': 64,
                'max_gpu_memory': 65536,
                'max_memory': 131072,
                'priority_weight': 3.0,
                'cost_limit_per_hour': 500.0
            }
        }
        
        # Resource costs (per hour)
        self.resource_costs = {
            ResourceType.CPU: 0.1,        # per core
            ResourceType.GPU: 2.5,        # per GPU
            ResourceType.MEMORY: 0.01,    # per GB
            ResourceType.STORAGE: 0.001,  # per GB
            ResourceType.NETWORK: 0.05,   # per Gbps
            ResourceType.INFERENCE_SLOT: 1.0,
            ResourceType.TRAINING_SLOT: 5.0
        }
        
        # Optimization strategies weights
        self.strategy_weights = {
            AllocationStrategy.FAIR_SHARE: {'cost': 0.3, 'performance': 0.4, 'fairness': 0.3},
            AllocationStrategy.PRIORITY_BASED: {'cost': 0.2, 'performance': 0.3, 'fairness': 0.5},
            AllocationStrategy.PERFORMANCE_OPTIMIZED: {'cost': 0.1, 'performance': 0.8, 'fairness': 0.1},
            AllocationStrategy.COST_OPTIMIZED: {'cost': 0.8, 'performance': 0.1, 'fairness': 0.1},
            AllocationStrategy.CREATOR_TIER_WEIGHTED: {'cost': 0.3, 'performance': 0.3, 'fairness': 0.4},
            AllocationStrategy.DYNAMIC_BALANCING: {'cost': 0.4, 'performance': 0.4, 'fairness': 0.2}
        }
        
        # Initialize resource pools
        asyncio.create_task(self._initialize_resource_pools())
        
        # Start optimization scheduler
        self._optimization_active = False
        self._optimization_task = None
    
    def _setup_logging(self) -> logging.Logger:
        """Configuration logging"""
        logger = logging.getLogger("resource_allocation_optimizer")
        logger.setLevel(logging.INFO)
        
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger
    
    async def _initialize_resource_pools(self):
        """Initialisation pools ressources"""
        try:
            # CPU Pool
            self.resource_pools["cpu_pool"] = ResourcePool(
                pool_id="cpu_pool",
                pool_type=ResourceType.CPU,
                total_capacity=1000.0,  # 1000 CPU cores
                available_capacity=800.0,
                reserved_capacity=200.0,
                allocation_strategy=AllocationStrategy.CREATOR_TIER_WEIGHTED,
                creator_tier_quotas={
                    'free': 200.0,
                    'premium': 400.0,
                    'enterprise': 400.0
                },
                cost_model={'base_cost': 0.1, 'peak_multiplier': 1.5},
                performance_metrics={'avg_utilization': 0.6}
            )
            
            # GPU Pool
            self.resource_pools["gpu_pool"] = ResourcePool(
                pool_id="gpu_pool",
                pool_type=ResourceType.GPU,
                total_capacity=100.0,  # 100 GPUs
                available_capacity=70.0,
                reserved_capacity=30.0,
                allocation_strategy=AllocationStrategy.PRIORITY_BASED,
                creator_tier_quotas={
                    'free': 10.0,
                    'premium': 40.0,
                    'enterprise': 50.0
                },
                cost_model={'base_cost': 2.5, 'peak_multiplier': 2.0},
                performance_metrics={'avg_utilization': 0.8}
            )
            
            # Memory Pool
            self.resource_pools["memory_pool"] = ResourcePool(
                pool_id="memory_pool",
                pool_type=ResourceType.MEMORY,
                total_capacity=10240.0,  # 10TB
                available_capacity=7168.0,
                reserved_capacity=3072.0,
                allocation_strategy=AllocationStrategy.DYNAMIC_BALANCING,
                creator_tier_quotas={
                    'free': 1024.0,
                    'premium': 4096.0,
                    'enterprise': 5120.0
                },
                cost_model={'base_cost': 0.01, 'peak_multiplier': 1.2},
                performance_metrics={'avg_utilization': 0.7}
            )
            
            # Initialize individual resource units
            await self._initialize_resource_units()
            
            self.logger.info("✅ Resource pools initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Error initializing resource pools: {e}")
    
    async def _initialize_resource_units(self):
        """Initialisation unités ressources"""
        try:
            # Create CPU units
            for i in range(20):  # 20 CPU nodes with 50 cores each
                resource_id = f"cpu_node_{i:03d}"
                self.resource_units[resource_id] = ResourceUnit(
                    resource_id=resource_id,
                    resource_type=ResourceType.CPU,
                    capacity=50.0,
                    current_usage=np.random.uniform(10, 40),
                    reserved_capacity=5.0,
                    cost_per_unit=self.resource_costs[ResourceType.CPU],
                    performance_score=np.random.uniform(0.8, 1.0),
                    status=ResourceStatus.AVAILABLE,
                    location=f"zone_{i % 3}",
                    specifications={
                        'cpu_model': 'Intel Xeon',
                        'cores': 50,
                        'clock_speed': '3.2GHz'
                    }
                )
            
            # Create GPU units
            for i in range(25):  # 25 GPU nodes with 4 GPUs each
                resource_id = f"gpu_node_{i:03d}"
                self.resource_units[resource_id] = ResourceUnit(
                    resource_id=resource_id,
                    resource_type=ResourceType.GPU,
                    capacity=4.0,
                    current_usage=np.random.uniform(1, 3),
                    reserved_capacity=0.5,
                    cost_per_unit=self.resource_costs[ResourceType.GPU],
                    performance_score=np.random.uniform(0.85, 1.0),
                    status=ResourceStatus.AVAILABLE,
                    location=f"zone_{i % 3}",
                    specifications={
                        'gpu_model': 'NVIDIA A100',
                        'memory': '40GB',
                        'compute_capability': '8.0'
                    }
                )
            
            # Create memory units
            for i in range(50):  # 50 memory nodes
                resource_id = f"memory_node_{i:03d}"
                self.resource_units[resource_id] = ResourceUnit(
                    resource_id=resource_id,
                    resource_type=ResourceType.MEMORY,
                    capacity=204.8,  # ~200GB per node
                    current_usage=np.random.uniform(50, 150),
                    reserved_capacity=20.0,
                    cost_per_unit=self.resource_costs[ResourceType.MEMORY],
                    performance_score=np.random.uniform(0.9, 1.0),
                    status=ResourceStatus.AVAILABLE,
                    location=f"zone_{i % 3}",
                    specifications={
                        'memory_type': 'DDR4',
                        'speed': '3200MHz',
                        'capacity_gb': 204.8
                    }
                )
            
            self.logger.info(f"✅ Initialized {len(self.resource_units)} resource units")
            
        except Exception as e:
            self.logger.error(f"Error initializing resource units: {e}")
    
    async def submit_allocation_request(self, 
                                      creator_id: str,
                                      creator_tier: str,
                                      workload_type: WorkloadType,
                                      resource_requirements: Dict[str, float],
                                      max_cost_per_hour: float = None,
                                      duration_estimate: float = 1.0,
                                      deadline: datetime = None,
                                      preferences: Dict[str, Any] = None) -> str:
        """Soumission demande allocation ressource"""
        try:
            # Convert string tier to enum
            tier_mapping = {
                'free': CreatorTierPriority.FREE,
                'premium': CreatorTierPriority.PREMIUM,
                'enterprise': CreatorTierPriority.ENTERPRISE
            }
            creator_tier_enum = tier_mapping.get(creator_tier.lower(), CreatorTierPriority.FREE)
            
            # Convert resource requirements
            resource_req_typed = {}
            for resource_name, amount in resource_requirements.items():
                try:
                    resource_type = ResourceType(resource_name.lower())
                    resource_req_typed[resource_type] = float(amount)
                except ValueError:
                    self.logger.warning(f"Unknown resource type: {resource_name}")
            
            # Get tier configuration
            tier_config = self.creator_tier_configs[creator_tier_enum]
            
            # Set default max cost if not provided
            if max_cost_per_hour is None:
                max_cost_per_hour = tier_config['cost_limit_per_hour']
            
            # Calculate priority score
            priority_score = self._calculate_priority_score(
                creator_tier_enum, workload_type, deadline, resource_req_typed
            )
            
            # Create allocation request
            request = AllocationRequest(
                request_id=str(uuid.uuid4()),
                creator_id=creator_id,
                creator_tier=creator_tier_enum,
                workload_type=workload_type,
                resource_requirements=resource_req_typed,
                priority_score=priority_score,
                max_cost_per_hour=max_cost_per_hour,
                duration_estimate=duration_estimate,
                deadline=deadline,
                preferences=preferences or {}
            )
            
            self.allocation_requests.append(request)
            
            self.logger.info(f"📝 Allocation request submitted: {request.request_id} for creator {creator_id}")
            
            # Try immediate allocation if resources available
            allocation = await self._attempt_immediate_allocation(request)
            if allocation:
                self.logger.info(f"⚡ Immediate allocation successful: {allocation.allocation_id}")
            
            return request.request_id
            
        except Exception as e:
            self.logger.error(f"Error submitting allocation request: {e}")
            return ""
    
    def _calculate_priority_score(self, 
                                creator_tier: CreatorTierPriority,
                                workload_type: WorkloadType,
                                deadline: Optional[datetime],
                                resource_requirements: Dict[ResourceType, float]) -> float:
        """Calcul score priorité"""
        try:
            # Base score from creator tier
            tier_weights = {
                CreatorTierPriority.FREE: 1.0,
                CreatorTierPriority.PREMIUM: 2.0,
                CreatorTierPriority.ENTERPRISE: 3.0
            }
            base_score = tier_weights[creator_tier]
            
            # Workload type multiplier
            workload_multipliers = {
                WorkloadType.REAL_TIME_PROCESSING: 2.0,
                WorkloadType.INFERENCE: 1.5,
                WorkloadType.TRAINING: 1.0,
                WorkloadType.BATCH_PROCESSING: 0.8,
                WorkloadType.DATA_PREPROCESSING: 0.6
            }
            workload_multiplier = workload_multipliers.get(workload_type, 1.0)
            
            # Deadline urgency
            urgency_multiplier = 1.0
            if deadline:
                time_to_deadline = (deadline - datetime.utcnow()).total_seconds() / 3600  # hours
                if time_to_deadline < 1:
                    urgency_multiplier = 3.0
                elif time_to_deadline < 6:
                    urgency_multiplier = 2.0
                elif time_to_deadline < 24:
                    urgency_multiplier = 1.5
            
            # Resource intensity (higher resource needs = higher priority for efficient allocation)
            total_resource_score = sum(
                amount * (2.0 if res_type in [ResourceType.GPU, ResourceType.TRAINING_SLOT] else 1.0)
                for res_type, amount in resource_requirements.items()
            )
            resource_multiplier = min(2.0, 1.0 + (total_resource_score / 100.0))
            
            final_score = base_score * workload_multiplier * urgency_multiplier * resource_multiplier
            
            return min(10.0, final_score)  # Cap at 10.0
            
        except Exception as e:
            self.logger.error(f"Error calculating priority score: {e}")
            return 1.0
    
    async def _attempt_immediate_allocation(self, request: AllocationRequest) -> Optional[ResourceAllocation]:
        """Tentative allocation immédiate"""
        try:
            # Find best allocation strategy
            best_strategy = await self._select_optimal_strategy(request)
            
            # Attempt allocation with best strategy
            allocated_resources = await self._allocate_resources(request, best_strategy)
            
            if not allocated_resources:
                return None
            
            # Calculate cost
            cost_per_hour = sum(
                resource.cost_per_unit * resource.current_usage
                for resource in allocated_resources.values()
            )
            
            # Check cost limit
            if cost_per_hour > request.max_cost_per_hour:
                # Release allocated resources
                await self._release_resources(allocated_resources)
                return None
            
            # Create allocation
            allocation = ResourceAllocation(
                allocation_id=str(uuid.uuid4()),
                request_id=request.request_id,
                creator_id=request.creator_id,
                allocated_resources=allocated_resources,
                allocation_strategy=best_strategy,
                cost_per_hour=cost_per_hour,
                estimated_duration=request.duration_estimate,
                actual_start_time=datetime.utcnow(),
                estimated_end_time=datetime.utcnow() + timedelta(hours=request.duration_estimate),
                actual_end_time=None,
                performance_metrics={},
                efficiency_score=0.0
            )
            
            # Store allocation
            self.active_allocations[allocation.allocation_id] = allocation
            
            # Remove request from queue
            self.allocation_requests = [r for r in self.allocation_requests if r.request_id != request.request_id]
            
            return allocation
            
        except Exception as e:
            self.logger.error(f"Error attempting immediate allocation: {e}")
            return None
    
    async def _select_optimal_strategy(self, request: AllocationRequest) -> AllocationStrategy:
        """Sélection stratégie optimale"""
        try:
            # Analyze current system state
            cpu_utilization = await self._get_resource_pool_utilization(ResourceType.CPU)
            gpu_utilization = await self._get_resource_pool_utilization(ResourceType.GPU)
            memory_utilization = await self._get_resource_pool_utilization(ResourceType.MEMORY)
            
            # Strategy selection logic
            if request.creator_tier == CreatorTierPriority.ENTERPRISE:
                if request.workload_type == WorkloadType.REAL_TIME_PROCESSING:
                    return AllocationStrategy.PERFORMANCE_OPTIMIZED
                else:
                    return AllocationStrategy.PRIORITY_BASED
            
            elif request.creator_tier == CreatorTierPriority.PREMIUM:
                if gpu_utilization > 0.8:
                    return AllocationStrategy.DYNAMIC_BALANCING
                else:
                    return AllocationStrategy.CREATOR_TIER_WEIGHTED
            
            else:  # FREE tier
                if cpu_utilization > 0.9:
                    return AllocationStrategy.COST_OPTIMIZED
                else:
                    return AllocationStrategy.FAIR_SHARE
            
        except Exception as e:
            self.logger.error(f"Error selecting optimal strategy: {e}")
            return AllocationStrategy.FAIR_SHARE
    
    async def _get_resource_pool_utilization(self, resource_type: ResourceType) -> float:
        """Récupération utilisation pool ressource"""
        try:
            relevant_units = [
                unit for unit in self.resource_units.values()
                if unit.resource_type == resource_type and unit.status == ResourceStatus.AVAILABLE
            ]
            
            if not relevant_units:
                return 1.0  # Fully utilized if no units available
            
            total_capacity = sum(unit.capacity for unit in relevant_units)
            total_usage = sum(unit.current_usage for unit in relevant_units)
            
            return total_usage / max(1.0, total_capacity)
            
        except Exception as e:
            self.logger.error(f"Error getting resource pool utilization: {e}")
            return 0.5
    
    async def _allocate_resources(self, 
                                request: AllocationRequest, 
                                strategy: AllocationStrategy) -> Dict[str, ResourceUnit]:
        """Allocation ressources selon stratégie"""
        try:
            allocated_resources = {}
            
            for resource_type, required_amount in request.resource_requirements.items():
                # Find available resources of this type
                available_units = [
                    unit for unit in self.resource_units.values()
                    if (unit.resource_type == resource_type and 
                        unit.status == ResourceStatus.AVAILABLE and
                        unit.capacity - unit.current_usage >= required_amount)
                ]
                
                if not available_units:
                    # Not enough resources available
                    await self._release_resources(allocated_resources)
                    return {}
                
                # Select best unit based on strategy
                selected_unit = await self._select_best_resource_unit(
                    available_units, required_amount, strategy, request
                )
                
                if selected_unit:
                    # Allocate the resource
                    selected_unit.current_usage += required_amount
                    allocated_resources[f"{resource_type.value}_{selected_unit.resource_id}"] = selected_unit
                else:
                    # Allocation failed
                    await self._release_resources(allocated_resources)
                    return {}
            
            return allocated_resources
            
        except Exception as e:
            self.logger.error(f"Error allocating resources: {e}")
            return {}
    
    async def _select_best_resource_unit(self,
                                       available_units: List[ResourceUnit],
                                       required_amount: float,
                                       strategy: AllocationStrategy,
                                       request: AllocationRequest) -> Optional[ResourceUnit]:
        """Sélection meilleure unité ressource"""
        try:
            if not available_units:
                return None
            
            scored_units = []
            
            for unit in available_units:
                score = 0.0
                
                if strategy == AllocationStrategy.PERFORMANCE_OPTIMIZED:
                    # Prioritize high-performance units
                    score = unit.performance_score * 10
                    
                elif strategy == AllocationStrategy.COST_OPTIMIZED:
                    # Prioritize low-cost units
                    score = 10.0 / max(0.1, unit.cost_per_unit)
                    
                elif strategy == AllocationStrategy.FAIR_SHARE:
                    # Balance performance and cost
                    score = (unit.performance_score * 5) + (5.0 / max(0.1, unit.cost_per_unit))
                    
                elif strategy == AllocationStrategy.PRIORITY_BASED:
                    # Consider creator tier priority
                    tier_weight = self.creator_tier_configs[request.creator_tier]['priority_weight']
                    score = unit.performance_score * tier_weight * 5
                    
                elif strategy == AllocationStrategy.CREATOR_TIER_WEIGHTED:
                    # Weight by creator tier and performance
                    tier_weight = self.creator_tier_configs[request.creator_tier]['priority_weight']
                    score = (unit.performance_score * tier_weight * 3) + (3.0 / max(0.1, unit.cost_per_unit))
                    
                elif strategy == AllocationStrategy.DYNAMIC_BALANCING:
                    # Balance current utilization, performance, and cost
                    utilization_factor = 1.0 - (unit.current_usage / unit.capacity)
                    score = (unit.performance_score * 3) + (utilization_factor * 3) + (2.0 / max(0.1, unit.cost_per_unit))
                
                scored_units.append((score, unit))
            
            # Return unit with highest score
            scored_units.sort(key=lambda x: x[0], reverse=True)
            return scored_units[0][1]
            
        except Exception as e:
            self.logger.error(f"Error selecting best resource unit: {e}")
            return available_units[0] if available_units else None
    
    async def _release_resources(self, allocated_resources: Dict[str, ResourceUnit]):
        """Libération ressources"""
        try:
            for resource_key, resource_unit in allocated_resources.items():
                # Extract the required amount from the key or calculate it
                # This is a simplified approach - in practice, you'd track allocated amounts
                allocated_amount = min(10.0, resource_unit.current_usage)  # Simplified
                resource_unit.current_usage = max(0.0, resource_unit.current_usage - allocated_amount)
                
        except Exception as e:
            self.logger.error(f"Error releasing resources: {e}")
    
    async def complete_allocation(self, allocation_id: str, performance_metrics: Dict[str, float] = None) -> bool:
        """Finalisation allocation"""
        try:
            if allocation_id not in self.active_allocations:
                self.logger.warning(f"Allocation {allocation_id} not found in active allocations")
                return False
            
            allocation = self.active_allocations[allocation_id]
            allocation.actual_end_time = datetime.utcnow()
            allocation.performance_metrics = performance_metrics or {}
            
            # Calculate efficiency score
            if performance_metrics:
                allocation.efficiency_score = await self._calculate_efficiency_score(allocation, performance_metrics)
            
            # Release resources
            await self._release_resources(allocation.allocated_resources)
            
            # Move to completed allocations
            self.completed_allocations.append(allocation)
            del self.active_allocations[allocation_id]
            
            # Keep only recent completed allocations
            if len(self.completed_allocations) > 10000:
                self.completed_allocations = self.completed_allocations[-10000:]
            
            self.logger.info(f"✅ Allocation {allocation_id} completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error completing allocation: {e}")
            return False
    
    async def _calculate_efficiency_score(self, 
                                        allocation: ResourceAllocation, 
                                        performance_metrics: Dict[str, float]) -> float:
        """Calcul score efficacité"""
        try:
            # Base efficiency from resource utilization
            total_capacity = sum(unit.capacity for unit in allocation.allocated_resources.values())
            total_usage = sum(unit.current_usage for unit in allocation.allocated_resources.values())
            utilization_efficiency = total_usage / max(1.0, total_capacity)
            
            # Cost efficiency
            actual_duration = (allocation.actual_end_time - allocation.actual_start_time).total_seconds() / 3600
            actual_cost = allocation.cost_per_hour * actual_duration
            estimated_cost = allocation.cost_per_hour * allocation.estimated_duration
            cost_efficiency = min(1.0, estimated_cost / max(0.1, actual_cost))
            
            # Performance efficiency from metrics
            performance_efficiency = performance_metrics.get('overall_performance', 0.8)
            
            # Weighted average
            efficiency_score = (
                utilization_efficiency * 0.4 +
                cost_efficiency * 0.3 +
                performance_efficiency * 0.3
            )
            
            return min(1.0, efficiency_score)
            
        except Exception as e:
            self.logger.error(f"Error calculating efficiency score: {e}")
            return 0.5
    
    async def optimize_resource_allocation(self, strategy: AllocationStrategy = None) -> OptimizationResult:
        """Optimisation allocation ressources"""
        try:
            start_time = time.time()
            
            if strategy is None:
                strategy = await self._select_global_optimization_strategy()
            
            # Collect current state
            initial_state = await self._collect_system_state()
            
            # Process pending requests
            processed_requests = await self._process_allocation_queue(strategy)
            
            # Optimize existing allocations
            optimized_allocations = await self._optimize_existing_allocations(strategy)
            
            # Rebalance resource pools
            rebalanced_pools = await self._rebalance_resource_pools(strategy)
            
            # Calculate optimization results
            final_state = await self._collect_system_state()
            
            # Calculate improvements
            cost_savings = self._calculate_cost_savings(initial_state, final_state)
            performance_improvement = self._calculate_performance_improvement(initial_state, final_state)
            satisfaction_impact = await self._calculate_creator_satisfaction_impact()
            efficiency_gains = self._calculate_efficiency_gains(initial_state, final_state)
            
            # Generate recommendations
            recommendations = await self._generate_optimization_recommendations(initial_state, final_state)
            
            optimization_result = OptimizationResult(
                optimization_id=str(uuid.uuid4()),
                strategy_used=strategy,
                total_resources_optimized=len(self.resource_units),
                cost_savings=cost_savings,
                performance_improvement=performance_improvement,
                creator_satisfaction_impact=satisfaction_impact,
                efficiency_gains=efficiency_gains,
                recommendations=recommendations
            )
            
            self.optimization_history.append(optimization_result)
            
            # Keep only recent optimization history
            if len(self.optimization_history) > 100:
                self.optimization_history = self.optimization_history[-100:]
            
            execution_time = time.time() - start_time
            self.logger.info(
                f"🔧 Resource optimization completed in {execution_time:.2f}s: "
                f"{cost_savings:.2f}% cost savings, {performance_improvement:.2f}% performance improvement"
            )
            
            return optimization_result
            
        except Exception as e:
            self.logger.error(f"Error optimizing resource allocation: {e}")
            return OptimizationResult(
                optimization_id=str(uuid.uuid4()),
                strategy_used=strategy or AllocationStrategy.FAIR_SHARE,
                total_resources_optimized=0,
                cost_savings=0.0,
                performance_improvement=0.0,
                creator_satisfaction_impact=0.0,
                efficiency_gains={},
                recommendations=[]
            )
    
    async def _select_global_optimization_strategy(self) -> AllocationStrategy:
        """Sélection stratégie optimisation globale"""
        try:
            # Analyze system state
            cpu_util = await self._get_resource_pool_utilization(ResourceType.CPU)
            gpu_util = await self._get_resource_pool_utilization(ResourceType.GPU)
            memory_util = await self._get_resource_pool_utilization(ResourceType.MEMORY)
            
            # Count requests by creator tier
            tier_counts = defaultdict(int)
            for request in self.allocation_requests:
                tier_counts[request.creator_tier] += 1
            
            # Strategy selection logic
            if gpu_util > 0.9 or cpu_util > 0.9:
                return AllocationStrategy.PERFORMANCE_OPTIMIZED
            elif len(self.allocation_requests) > 50:
                return AllocationStrategy.DYNAMIC_BALANCING
            elif tier_counts[CreatorTierPriority.ENTERPRISE] > tier_counts[CreatorTierPriority.FREE]:
                return AllocationStrategy.PRIORITY_BASED
            else:
                return AllocationStrategy.FAIR_SHARE
                
        except Exception as e:
            self.logger.error(f"Error selecting global optimization strategy: {e}")
            return AllocationStrategy.FAIR_SHARE
    
    async def _collect_system_state(self) -> Dict[str, Any]:
        """Collecte état système"""
        try:
            state = {
                'timestamp': datetime.utcnow(),
                'total_resources': len(self.resource_units),
                'active_allocations': len(self.active_allocations),
                'pending_requests': len(self.allocation_requests),
                'resource_utilization': {},
                'pool_states': {},
                'cost_metrics': {}
            }
            
            # Resource utilization by type
            for resource_type in ResourceType:
                state['resource_utilization'][resource_type.value] = await self._get_resource_pool_utilization(resource_type)
            
            # Pool states
            for pool_id, pool in self.resource_pools.items():
                state['pool_states'][pool_id] = {
                    'utilization': (pool.total_capacity - pool.available_capacity) / pool.total_capacity,
                    'available_capacity': pool.available_capacity,
                    'total_capacity': pool.total_capacity
                }
            
            # Cost metrics
            total_cost = sum(
                alloc.cost_per_hour for alloc in self.active_allocations.values()
            )
            state['cost_metrics'] = {
                'total_hourly_cost': total_cost,
                'average_cost_per_allocation': total_cost / max(1, len(self.active_allocations))
            }
            
            return state
            
        except Exception as e:
            self.logger.error(f"Error collecting system state: {e}")
            return {}
    
    async def _process_allocation_queue(self, strategy: AllocationStrategy) -> int:
        """Traitement queue allocation"""
        try:
            processed_count = 0
            
            # Sort requests by priority
            sorted_requests = sorted(
                self.allocation_requests,
                key=lambda r: r.priority_score,
                reverse=True
            )
            
            for request in sorted_requests[:10]:  # Process top 10 requests
                allocation = await self._attempt_immediate_allocation(request)
                if allocation:
                    processed_count += 1
            
            return processed_count
            
        except Exception as e:
            self.logger.error(f"Error processing allocation queue: {e}")
            return 0
    
    async def _optimize_existing_allocations(self, strategy: AllocationStrategy) -> int:
        """Optimisation allocations existantes"""
        try:
            optimized_count = 0
            
            for allocation in list(self.active_allocations.values()):
                # Check if allocation can be optimized
                if await self._can_optimize_allocation(allocation, strategy):
                    # Attempt optimization
                    if await self._optimize_single_allocation(allocation, strategy):
                        optimized_count += 1
            
            return optimized_count
            
        except Exception as e:
            self.logger.error(f"Error optimizing existing allocations: {e}")
            return 0
    
    async def _can_optimize_allocation(self, allocation: ResourceAllocation, strategy: AllocationStrategy) -> bool:
        """Vérif si allocation peut être optimisée"""
        try:
            # Check if allocation has been running for sufficient time
            runtime = (datetime.utcnow() - allocation.actual_start_time).total_seconds() / 3600
            if runtime < 0.5:  # Less than 30 minutes
                return False
            
            # Check if there are better resources available
            current_cost = allocation.cost_per_hour
            current_performance = allocation.efficiency_score
            
            # Simple heuristic: optimize if efficiency is low
            return current_performance < 0.7
            
        except Exception as e:
            self.logger.error(f"Error checking if allocation can be optimized: {e}")
            return False
    
    async def _optimize_single_allocation(self, allocation: ResourceAllocation, strategy: AllocationStrategy) -> bool:
        """Optimisation allocation individuelle"""
        try:
            # This is a simplified optimization - in practice, this would involve
            # migrating workloads to better resources, adjusting resource sizes, etc.
            
            # For now, just improve the efficiency score slightly
            allocation.efficiency_score = min(1.0, allocation.efficiency_score + 0.1)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error optimizing single allocation: {e}")
            return False
    
    async def _rebalance_resource_pools(self, strategy: AllocationStrategy) -> int:
        """Rééquilibrage pools ressources"""
        try:
            rebalanced_count = 0
            
            for pool in self.resource_pools.values():
                # Simple rebalancing: adjust quotas based on demand
                total_demand = sum(pool.creator_tier_quotas.values())
                if total_demand > pool.total_capacity:
                    # Scale down quotas proportionally
                    scale_factor = pool.total_capacity / total_demand
                    for tier in pool.creator_tier_quotas:
                        pool.creator_tier_quotas[tier] *= scale_factor
                    rebalanced_count += 1
                elif total_demand < pool.total_capacity * 0.8:
                    # Scale up quotas
                    scale_factor = 1.1
                    for tier in pool.creator_tier_quotas:
                        pool.creator_tier_quotas[tier] *= scale_factor
                    rebalanced_count += 1
            
            return rebalanced_count
            
        except Exception as e:
            self.logger.error(f"Error rebalancing resource pools: {e}")
            return 0
    
    def _calculate_cost_savings(self, initial_state: Dict[str, Any], final_state: Dict[str, Any]) -> float:
        """Calcul économies coût"""
        try:
            initial_cost = initial_state.get('cost_metrics', {}).get('total_hourly_cost', 0)
            final_cost = final_state.get('cost_metrics', {}).get('total_hourly_cost', 0)
            
            if initial_cost > 0:
                savings_percentage = ((initial_cost - final_cost) / initial_cost) * 100
                return max(0.0, savings_percentage)
            
            return 0.0
            
        except Exception as e:
            self.logger.error(f"Error calculating cost savings: {e}")
            return 0.0
    
    def _calculate_performance_improvement(self, initial_state: Dict[str, Any], final_state: Dict[str, Any]) -> float:
        """Calcul amélioration performance"""
        try:
            # Compare resource utilization efficiency
            initial_util = statistics.mean(initial_state.get('resource_utilization', {}).values())
            final_util = statistics.mean(final_state.get('resource_utilization', {}).values())
            
            if initial_util > 0:
                improvement_percentage = ((final_util - initial_util) / initial_util) * 100
                return max(0.0, improvement_percentage)
            
            return 0.0
            
        except Exception as e:
            self.logger.error(f"Error calculating performance improvement: {e}")
            return 0.0
    
    async def _calculate_creator_satisfaction_impact(self) -> float:
        """Calcul impact satisfaction créateur"""
        try:
            # Simplified calculation based on allocation success rate and response time
            if not self.completed_allocations:
                return 0.0
            
            recent_allocations = [
                alloc for alloc in self.completed_allocations
                if (datetime.utcnow() - alloc.actual_start_time).total_seconds() < 86400  # Last 24 hours
            ]
            
            if not recent_allocations:
                return 0.0
            
            # Calculate average efficiency score as satisfaction proxy
            avg_efficiency = statistics.mean([alloc.efficiency_score for alloc in recent_allocations])
            
            # Convert to percentage improvement (assuming baseline of 0.7)
            baseline_satisfaction = 0.7
            satisfaction_improvement = ((avg_efficiency - baseline_satisfaction) / baseline_satisfaction) * 100
            
            return max(0.0, satisfaction_improvement)
            
        except Exception as e:
            self.logger.error(f"Error calculating creator satisfaction impact: {e}")
            return 0.0
    
    def _calculate_efficiency_gains(self, initial_state: Dict[str, Any], final_state: Dict[str, Any]) -> Dict[ResourceType, float]:
        """Calcul gains efficacité"""
        try:
            efficiency_gains = {}
            
            initial_util = initial_state.get('resource_utilization', {})
            final_util = final_state.get('resource_utilization', {})
            
            for resource_type in ResourceType:
                resource_key = resource_type.value
                if resource_key in initial_util and resource_key in final_util:
                    initial = initial_util[resource_key]
                    final = final_util[resource_key]
                    
                    if initial > 0:
                        gain_percentage = ((final - initial) / initial) * 100
                        efficiency_gains[resource_type] = max(0.0, gain_percentage)
                    else:
                        efficiency_gains[resource_type] = 0.0
                else:
                    efficiency_gains[resource_type] = 0.0
            
            return efficiency_gains
            
        except Exception as e:
            self.logger.error(f"Error calculating efficiency gains: {e}")
            return {}
    
    async def _generate_optimization_recommendations(self, 
                                                   initial_state: Dict[str, Any], 
                                                   final_state: Dict[str, Any]) -> List[str]:
        """Génération recommandations optimisation"""
        recommendations = []
        
        try:
            # Analyze resource utilization
            resource_util = final_state.get('resource_utilization', {})
            
            for resource_type, utilization in resource_util.items():
                if utilization > 0.9:
                    recommendations.append(f"Consider scaling up {resource_type} capacity - currently at {utilization:.1%}")
                elif utilization < 0.3:
                    recommendations.append(f"Consider scaling down {resource_type} capacity - underutilized at {utilization:.1%}")
            
            # Analyze pending requests
            pending_count = final_state.get('pending_requests', 0)
            if pending_count > 20:
                recommendations.append(f"High queue backlog ({pending_count} requests) - consider adding more resources")
            
            # Analyze cost efficiency
            cost_metrics = final_state.get('cost_metrics', {})
            avg_cost = cost_metrics.get('average_cost_per_allocation', 0)
            if avg_cost > 100:
                recommendations.append("High average allocation cost - review resource selection strategies")
            
            # Creator tier specific recommendations
            enterprise_requests = len([r for r in self.allocation_requests if r.creator_tier == CreatorTierPriority.ENTERPRISE])
            if enterprise_requests > 5:
                recommendations.append("High enterprise demand - consider dedicated enterprise resource pools")
            
            return recommendations[:5]  # Return top 5 recommendations
            
        except Exception as e:
            self.logger.error(f"Error generating optimization recommendations: {e}")
            return recommendations
    
    async def get_allocation_status(self, request_id: str = None, creator_id: str = None) -> Dict[str, Any]:
        """Statut allocation"""
        try:
            if request_id:
                # Find specific allocation
                for allocation in self.active_allocations.values():
                    if allocation.request_id == request_id:
                        return await self._format_allocation_status(allocation)
                
                # Check completed allocations
                for allocation in self.completed_allocations:
                    if allocation.request_id == request_id:
                        return await self._format_allocation_status(allocation)
                
                # Check pending requests
                for request in self.allocation_requests:
                    if request.request_id == request_id:
                        return {
                            'request_id': request_id,
                            'status': 'pending',
                            'creator_id': request.creator_id,
                            'submitted_at': request.timestamp.isoformat(),
                            'priority_score': request.priority_score,
                            'estimated_wait_time': await self._estimate_wait_time(request)
                        }
                
                return {'request_id': request_id, 'status': 'not_found'}
            
            elif creator_id:
                # Get all allocations for creator
                creator_allocations = {
                    'creator_id': creator_id,
                    'active_allocations': [],
                    'pending_requests': [],
                    'recent_completed': []
                }
                
                # Active allocations
                for allocation in self.active_allocations.values():
                    if allocation.creator_id == creator_id:
                        creator_allocations['active_allocations'].append(
                            await self._format_allocation_status(allocation)
                        )
                
                # Pending requests
                for request in self.allocation_requests:
                    if request.creator_id == creator_id:
                        creator_allocations['pending_requests'].append({
                            'request_id': request.request_id,
                            'status': 'pending',
                            'submitted_at': request.timestamp.isoformat(),
                            'priority_score': request.priority_score
                        })
                
                # Recent completed (last 24 hours)
                recent_cutoff = datetime.utcnow() - timedelta(hours=24)
                for allocation in self.completed_allocations:
                    if (allocation.creator_id == creator_id and 
                        allocation.actual_start_time >= recent_cutoff):
                        creator_allocations['recent_completed'].append(
                            await self._format_allocation_status(allocation)
                        )
                
                return creator_allocations
            
            else:
                # System overview
                return {
                    'system_status': {
                        'total_active_allocations': len(self.active_allocations),
                        'pending_requests': len(self.allocation_requests),
                        'resource_pools': len(self.resource_pools),
                        'total_resources': len(self.resource_units)
                    },
                    'resource_utilization': {
                        res_type.value: await self._get_resource_pool_utilization(res_type)
                        for res_type in ResourceType
                    },
                    'recent_optimizations': len([
                        opt for opt in self.optimization_history
                        if (datetime.utcnow() - opt.timestamp).total_seconds() < 3600
                    ])
                }
                
        except Exception as e:
            self.logger.error(f"Error getting allocation status: {e}")
            return {'error': str(e)}
    
    async def _format_allocation_status(self, allocation: ResourceAllocation) -> Dict[str, Any]:
        """Formatage statut allocation"""
        try:
            status = 'active' if allocation.allocation_id in self.active_allocations else 'completed'
            
            return {
                'allocation_id': allocation.allocation_id,
                'request_id': allocation.request_id,
                'creator_id': allocation.creator_id,
                'status': status,
                'strategy': allocation.allocation_strategy.value,
                'cost_per_hour': allocation.cost_per_hour,
                'start_time': allocation.actual_start_time.isoformat(),
                'estimated_end_time': allocation.estimated_end_time.isoformat(),
                'actual_end_time': allocation.actual_end_time.isoformat() if allocation.actual_end_time else None,
                'allocated_resources': {
                    res_key: {
                        'resource_id': res_unit.resource_id,
                        'type': res_unit.resource_type.value,
                        'capacity': res_unit.capacity,
                        'current_usage': res_unit.current_usage
                    }
                    for res_key, res_unit in allocation.allocated_resources.items()
                },
                'efficiency_score': allocation.efficiency_score,
                'performance_metrics': allocation.performance_metrics
            }
            
        except Exception as e:
            self.logger.error(f"Error formatting allocation status: {e}")
            return {}
    
    async def _estimate_wait_time(self, request: AllocationRequest) -> float:
        """Estimation temps d'attente"""
        try:
            # Simple estimation based on queue position and resource availability
            queue_position = 0
            for req in self.allocation_requests:
                if req.priority_score > request.priority_score:
                    queue_position += 1
            
            # Estimate average processing time (hours)
            avg_processing_time = 0.5  # 30 minutes average
            
            estimated_wait = queue_position * avg_processing_time
            
            return estimated_wait
            
        except Exception as e:
            self.logger.error(f"Error estimating wait time: {e}")
            return 1.0  # Default 1 hour
    
    async def start_optimization_scheduler(self, interval_minutes: int = 30):
        """Démarrage planificateur optimisation"""
        try:
            if self._optimization_active:
                await self.stop_optimization_scheduler()
            
            self._optimization_active = True
            self._optimization_task = asyncio.create_task(
                self._optimization_scheduler_loop(interval_minutes)
            )
            
            self.logger.info(f"🔄 Optimization scheduler started (interval: {interval_minutes} minutes)")
            
        except Exception as e:
            self.logger.error(f"Error starting optimization scheduler: {e}")
    
    async def _optimization_scheduler_loop(self, interval_minutes: int):
        """Boucle planificateur optimisation"""
        try:
            while self._optimization_active:
                # Run optimization
                result = await self.optimize_resource_allocation()
                
                self.logger.info(
                    f"📊 Scheduled optimization completed: "
                    f"{result.cost_savings:.2f}% cost savings, "
                    f"{result.performance_improvement:.2f}% performance improvement"
                )
                
                # Wait for next interval
                await asyncio.sleep(interval_minutes * 60)
                
        except Exception as e:
            self.logger.error(f"Error in optimization scheduler loop: {e}")
    
    async def stop_optimization_scheduler(self):
        """Arrêt planificateur optimisation"""
        try:
            self._optimization_active = False
            
            if self._optimization_task:
                self._optimization_task.cancel()
                try:
                    await self._optimization_task
                except asyncio.CancelledError:
                    pass
                self._optimization_task = None
            
            self.logger.info("⏹️ Optimization scheduler stopped")
            
        except Exception as e:
            self.logger.error(f"Error stopping optimization scheduler: {e}")
    
    async def shutdown(self):
        """Arrêt propre de l'optimiseur"""
        self.logger.info("⏹️ Arrêt Resource Allocation Optimizer...")
        
        # Stop scheduler
        await self.stop_optimization_scheduler()
        
        # Complete any pending allocations
        for allocation in list(self.active_allocations.values()):
            await self.complete_allocation(allocation.allocation_id)
        
        # Clear data
        self.resource_units.clear()
        self.resource_pools.clear()
        self.allocation_requests.clear()
        self.active_allocations.clear()
        self.completed_allocations.clear()
        self.optimization_history.clear()
        
        self.logger.info("✅ Resource Allocation Optimizer arrêté proprement")


# Point d'entrée pour tests
if __name__ == "__main__":
    async def test_resource_optimizer():
        config = {
            'debug': True,
            'optimization_interval': 30
        }
        
        optimizer = ResourceAllocationOptimizer(config)
        
        # Test allocation request
        request_id = await optimizer.submit_allocation_request(
            creator_id="creator_001",
            creator_tier="premium",
            workload_type=WorkloadType.INFERENCE,
            resource_requirements={
                'cpu': 8.0,
                'gpu': 2.0,
                'memory': 16384.0
            },
            max_cost_per_hour=25.0,
            duration_estimate=2.0
        )
        
        print(f"Allocation request submitted: {request_id}")
        
        # Wait a bit for processing
        await asyncio.sleep(1)
        
        # Check status
        status = await optimizer.get_allocation_status(request_id=request_id)
        print(f"Allocation status: {status.get('status', 'unknown')}")
        
        # Test optimization
        optimization_result = await optimizer.optimize_resource_allocation()
        print(f"Optimization completed: {optimization_result.cost_savings:.2f}% cost savings")
        
        # Get system overview
        overview = await optimizer.get_allocation_status()
        print(f"System overview: {overview['system_status']['total_active_allocations']} active allocations")
        
        print('✅ Resource Allocation Optimizer test passed')
        await optimizer.shutdown()
    
    asyncio.run(test_resource_optimizer())