"""Resource Allocator - Intelligent Resource Allocation and Optimization
=====================================================================

Advanced resource allocation system providing:
- AI-powered resource optimization
- Capacity planning and forecasting
- Skill-based resource matching
- Dynamic resource reallocation
- Utilization optimization
- Conflict resolution

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ STRICT COPYRIGHT WARNING - INTELLECTUAL PROPERTY PROTECTION
================================================================
This code and concept are the EXCLUSIVE PROPERTY of Fahed Mlaiel.
Unauthorized access, copying, modification, distribution, reverse engineering,
or commercialization without explicit written permission from Fahed Mlaiel
(mlaiel@live.de) is STRICTLY PROHIBITED and will result in immediate legal
action under German and International copyright laws.
"""

import asyncio
import logging
import numpy as np
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import json
import uuid
from collections import defaultdict

logger = logging.getLogger(__name__)


class ResourceType(Enum):
    """Types of resources"""
    HUMAN = "human"
    EQUIPMENT = "equipment"
    SOFTWARE = "software"
    FACILITY = "facility"
    BUDGET = "budget"
    TIME = "time"


class AllocationStrategy(Enum):
    """Resource allocation strategies"""
    SKILL_BASED = "skill_based"
    LOAD_BALANCING = "load_balancing"
    COST_OPTIMIZATION = "cost_optimization"
    QUALITY_FIRST = "quality_first"
    DEADLINE_DRIVEN = "deadline_driven"
    HYBRID = "hybrid"


class ResourceStatus(Enum):
    """Resource availability status"""
    AVAILABLE = "available"
    ALLOCATED = "allocated"
    BUSY = "busy"
    UNAVAILABLE = "unavailable"
    MAINTENANCE = "maintenance"
    OVERLOADED = "overloaded"


@dataclass
class ResourcePool:
    """Resource pool definition"""
    pool_id: str
    name: str
    resource_type: ResourceType
    resources: List[Dict[str, Any]] = field(default_factory=list)
    capacity_limits: Dict[str, float] = field(default_factory=dict)
    availability_schedule: Dict[str, Any] = field(default_factory=dict)
    cost_structure: Dict[str, float] = field(default_factory=dict)
    skills_matrix: Dict[str, List[str]] = field(default_factory=dict)
    utilization_metrics: Dict[str, float] = field(default_factory=dict)
    
    def __post_init__(self):
        if not self.pool_id:
            self.pool_id = str(uuid.uuid4())


@dataclass
class ResourceRequirement:
    """Resource requirement specification"""
    requirement_id: str
    task_id: str
    resource_type: ResourceType
    quantity: float
    duration: float  # in hours
    required_skills: List[str] = field(default_factory=list)
    priority: int = 1
    flexibility: float = 0.0  # 0 = rigid, 1 = very flexible
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    constraints: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        if not self.requirement_id:
            self.requirement_id = str(uuid.uuid4())


@dataclass
class ResourceAllocation:
    """Resource allocation record"""
    allocation_id: str
    resource_id: str
    task_id: str
    quantity: float
    start_time: datetime
    end_time: datetime
    efficiency_score: float
    cost: float
    status: ResourceStatus = ResourceStatus.ALLOCATED
    constraints_satisfied: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        if not self.allocation_id:
            self.allocation_id = str(uuid.uuid4())


@dataclass
class ResourceUtilization:
    """Resource utilization metrics"""
    resource_id: str
    utilization_rate: float  # 0-1
    efficiency_score: float  # 0-1
    workload_distribution: Dict[str, float]
    peak_usage_times: List[datetime]
    idle_times: List[Tuple[datetime, datetime]]
    satisfaction_score: float  # 0-1
    recommendations: List[str] = field(default_factory=list)


@dataclass
class CapacityPlanning:
    """Capacity planning analysis"""
    planning_id: str
    time_horizon: int  # days
    current_capacity: Dict[str, float]
    projected_demand: Dict[str, float]
    capacity_gaps: Dict[str, float]
    surplus_capacity: Dict[str, float]
    scaling_recommendations: List[Dict[str, Any]]
    cost_projections: Dict[str, float]
    risk_factors: List[str]
    
    def __post_init__(self):
        if not self.planning_id:
            self.planning_id = str(uuid.uuid4())


@dataclass
class OptimalAllocation:
    """Optimal allocation solution"""
    solution_id: str
    project_id: str
    allocations: List[ResourceAllocation]
    total_cost: float
    efficiency_score: float
    utilization_rate: float
    quality_score: float
    risk_score: float
    constraints_satisfied: int
    optimization_time: float
    alternative_solutions: List[Dict[str, Any]] = field(default_factory=list)
    
    def __post_init__(self):
        if not self.solution_id:
            self.solution_id = str(uuid.uuid4())


class ResourceAllocator:
    """
    Intelligent Resource Allocation Engine
    
    Provides AI-powered resource optimization, capacity planning,
    and dynamic allocation for collaboration projects.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the resource allocator"""
        self.config = config or {}
        
        # Allocation settings
        self.default_strategy = self.config.get(
            'strategy', AllocationStrategy.HYBRID
        )
        self.optimization_timeout = self.config.get('optimization_timeout', 300)
        self.max_iterations = self.config.get('max_iterations', 1000)
        
        # Scoring weights
        self.allocation_weights = self.config.get('allocation_weights', {
            'cost': 0.25,
            'efficiency': 0.25,
            'utilization': 0.20,
            'quality': 0.20,
            'risk': 0.10
        })
        
        # Resource data
        self.resource_pools = {}
        self.allocations = {}
        self.utilization_history = defaultdict(list)
        self.capacity_plans = {}
        
        logger.info("ResourceAllocator initialized with AI optimization")
    
    async def create_resource_pool(
        self,
        name: str,
        resource_type: ResourceType,
        resources: List[Dict[str, Any]],
        capacity_limits: Optional[Dict[str, float]] = None
    ) -> ResourcePool:
        """
        Create a new resource pool
        
        Args:
            name: Pool name
            resource_type: Type of resources in pool
            resources: List of resource definitions
            capacity_limits: Capacity constraints
            
        Returns:
            Created resource pool
        """
        try:
            pool = ResourcePool(
                pool_id=str(uuid.uuid4()),
                name=name,
                resource_type=resource_type,
                resources=resources,
                capacity_limits=capacity_limits or {},
                availability_schedule={},
                cost_structure={},
                skills_matrix={},
                utilization_metrics={}
            )
            
            # Initialize resource data
            await self._initialize_pool_data(pool)
            
            self.resource_pools[pool.pool_id] = pool
            
            logger.info(f"Resource pool '{name}' created with {len(resources)} resources")
            return pool
            
        except Exception as e:
            logger.error(f"Failed to create resource pool: {str(e)}")
            raise
    
    async def allocate_resources(
        self,
        project_id: str,
        requirements: List[ResourceRequirement],
        strategy: Optional[AllocationStrategy] = None
    ) -> OptimalAllocation:
        """
        Allocate resources optimally for project requirements
        
        Args:
            project_id: Project identifier
            requirements: List of resource requirements
            strategy: Allocation strategy to use
            
        Returns:
            Optimal allocation solution
        """
        try:
            strategy = strategy or self.default_strategy
            
            # Analyze requirements
            requirement_analysis = await self._analyze_requirements(requirements)
            
            # Find available resources
            available_resources = await self._find_available_resources(
                requirements, requirement_analysis
            )
            
            # Generate allocation solutions
            solutions = await self._generate_allocation_solutions(
                requirements, available_resources, strategy
            )
            
            # Select optimal solution
            optimal_solution = await self._select_optimal_solution(
                solutions, strategy
            )
            
            # Apply allocation
            await self._apply_allocation(optimal_solution)
            
            self.allocations[optimal_solution.solution_id] = optimal_solution
            
            logger.info(f"Resources allocated for project {project_id}")
            return optimal_solution
            
        except Exception as e:
            logger.error(f"Resource allocation failed: {str(e)}")
            raise
    
    async def optimize_utilization(
        self,
        pool_id: str,
        time_window: int = 7  # days
    ) -> ResourceUtilization:
        """
        Optimize resource utilization for a pool
        
        Args:
            pool_id: Resource pool identifier
            time_window: Analysis time window in days
            
        Returns:
            Utilization analysis and recommendations
        """
        try:
            if pool_id not in self.resource_pools:
                raise ValueError(f"Resource pool {pool_id} not found")
            
            pool = self.resource_pools[pool_id]
            
            # Analyze current utilization
            utilization_data = await self._analyze_utilization(pool, time_window)
            
            # Generate optimization recommendations
            recommendations = await self._generate_utilization_recommendations(
                pool, utilization_data
            )
            
            # Update pool metrics
            await self._update_pool_metrics(pool, utilization_data)
            
            logger.info(f"Utilization optimized for pool {pool_id}")
            return utilization_data
            
        except Exception as e:
            logger.error(f"Utilization optimization failed: {str(e)}")
            raise
    
    async def plan_capacity(
        self,
        pools: List[str],
        time_horizon: int = 30,  # days
        growth_scenarios: Optional[List[Dict[str, Any]]] = None
    ) -> CapacityPlanning:
        """
        Plan capacity requirements for resource pools
        
        Args:
            pools: List of pool IDs to analyze
            time_horizon: Planning horizon in days
            growth_scenarios: Different growth scenarios to analyze
            
        Returns:
            Capacity planning analysis
        """
        try:
            # Analyze current capacity
            current_capacity = await self._analyze_current_capacity(pools)
            
            # Project demand
            demand_forecast = await self._forecast_demand(
                pools, time_horizon, growth_scenarios
            )
            
            # Identify gaps and surpluses
            capacity_analysis = await self._analyze_capacity_gaps(
                current_capacity, demand_forecast
            )
            
            # Generate scaling recommendations
            scaling_recommendations = await self._generate_scaling_recommendations(
                capacity_analysis, time_horizon
            )
            
            planning = CapacityPlanning(
                planning_id=str(uuid.uuid4()),
                time_horizon=time_horizon,
                current_capacity=current_capacity,
                projected_demand=demand_forecast,
                capacity_gaps=capacity_analysis['gaps'],
                surplus_capacity=capacity_analysis['surplus'],
                scaling_recommendations=scaling_recommendations,
                cost_projections=await self._project_costs(
                    scaling_recommendations, time_horizon
                ),
                risk_factors=await self._identify_capacity_risks(capacity_analysis)
            )
            
            self.capacity_plans[planning.planning_id] = planning
            
            logger.info(f"Capacity planning completed for {len(pools)} pools")
            return planning
            
        except Exception as e:
            logger.error(f"Capacity planning failed: {str(e)}")
            raise
    
    async def reallocate_dynamically(
        self,
        allocation_id: str,
        changes: List[Dict[str, Any]]
    ) -> OptimalAllocation:
        """
        Dynamically reallocate resources based on changes
        
        Args:
            allocation_id: Existing allocation ID
            changes: List of changes to apply
            
        Returns:
            Updated allocation solution
        """
        try:
            if allocation_id not in self.allocations:
                raise ValueError(f"Allocation {allocation_id} not found")
            
            current_allocation = self.allocations[allocation_id]
            
            # Apply changes
            updated_requirements = await self._apply_allocation_changes(
                current_allocation, changes
            )
            
            # Re-optimize allocation
            new_allocation = await self.allocate_resources(
                current_allocation.project_id,
                updated_requirements,
                AllocationStrategy.HYBRID
            )
            
            # Release old allocations
            await self._release_allocations(current_allocation)
            
            logger.info(f"Dynamic reallocation completed for {allocation_id}")
            return new_allocation
            
        except Exception as e:
            logger.error(f"Dynamic reallocation failed: {str(e)}")
            raise
    
    async def _initialize_pool_data(self, pool: ResourcePool):
        """Initialize resource pool data"""
        # Set up availability schedules
        for resource in pool.resources:
            resource_id = resource['id']
            
            # Default 40-hour work week
            pool.availability_schedule[resource_id] = {
                'monday': {'start': '09:00', 'end': '17:00'},
                'tuesday': {'start': '09:00', 'end': '17:00'},
                'wednesday': {'start': '09:00', 'end': '17:00'},
                'thursday': {'start': '09:00', 'end': '17:00'},
                'friday': {'start': '09:00', 'end': '17:00'},
                'saturday': {'start': None, 'end': None},
                'sunday': {'start': None, 'end': None}
            }
            
            # Set up cost structure
            pool.cost_structure[resource_id] = resource.get('hourly_rate', 50.0)
            
            # Set up skills matrix
            pool.skills_matrix[resource_id] = resource.get('skills', [])
            
            # Initialize utilization metrics
            pool.utilization_metrics[resource_id] = {
                'current_utilization': 0.0,
                'average_utilization': 0.0,
                'efficiency_score': 1.0
            }
    
    async def _analyze_requirements(
        self, 
        requirements: List[ResourceRequirement]
    ) -> Dict[str, Any]:
        """Analyze resource requirements"""
        analysis = {
            'total_requirements': len(requirements),
            'resource_types': defaultdict(int),
            'skill_requirements': defaultdict(int),
            'priority_distribution': defaultdict(int),
            'time_constraints': [],
            'flexibility_score': 0.0
        }
        
        total_flexibility = 0.0
        
        for req in requirements:
            analysis['resource_types'][req.resource_type.value] += 1
            analysis['priority_distribution'][req.priority] += 1
            
            for skill in req.required_skills:
                analysis['skill_requirements'][skill] += 1
            
            if req.start_time and req.end_time:
                analysis['time_constraints'].append({
                    'requirement_id': req.requirement_id,
                    'start': req.start_time,
                    'end': req.end_time,
                    'duration': req.duration
                })
            
            total_flexibility += req.flexibility
        
        analysis['flexibility_score'] = (
            total_flexibility / len(requirements) if requirements else 0.0
        )
        
        return analysis
    
    async def _find_available_resources(
        self,
        requirements: List[ResourceRequirement],
        analysis: Dict[str, Any]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Find available resources for requirements"""
        available_resources = defaultdict(list)
        
        for req in requirements:
            resource_type = req.resource_type
            
            # Find pools with matching resource type
            matching_pools = [
                pool for pool in self.resource_pools.values()
                if pool.resource_type == resource_type
            ]
            
            for pool in matching_pools:
                for resource in pool.resources:
                    resource_id = resource['id']
                    
                    # Check skill compatibility
                    resource_skills = pool.skills_matrix.get(resource_id, [])
                    skills_match = all(
                        skill in resource_skills for skill in req.required_skills
                    )
                    
                    # Check availability
                    is_available = await self._check_resource_availability(
                        resource_id, req.start_time, req.end_time, req.duration
                    )
                    
                    if skills_match and is_available:
                        available_resources[req.requirement_id].append({
                            'resource_id': resource_id,
                            'pool_id': pool.pool_id,
                            'resource_data': resource,
                            'skills': resource_skills,
                            'cost': pool.cost_structure.get(resource_id, 0.0),
                            'utilization': pool.utilization_metrics.get(
                                resource_id, {}
                            ).get('current_utilization', 0.0)
                        })
        
        return dict(available_resources)
    
    async def _check_resource_availability(
        self,
        resource_id: str,
        start_time: Optional[datetime],
        end_time: Optional[datetime],
        duration: float
    ) -> bool:
        """Check if resource is available for specified time"""
        # Check existing allocations
        for allocation in self.allocations.values():
            for alloc in allocation.allocations:
                if alloc.resource_id == resource_id:
                    if start_time and end_time:
                        # Check for time overlap
                        if (start_time < alloc.end_time and 
                            end_time > alloc.start_time):
                            return False
        
        return True
    
    async def _generate_allocation_solutions(
        self,
        requirements: List[ResourceRequirement],
        available_resources: Dict[str, List[Dict[str, Any]]],
        strategy: AllocationStrategy
    ) -> List[OptimalAllocation]:
        """Generate multiple allocation solutions"""
        solutions = []
        
        if strategy == AllocationStrategy.SKILL_BASED:
            solutions.extend(
                await self._generate_skill_based_solutions(
                    requirements, available_resources
                )
            )
        elif strategy == AllocationStrategy.COST_OPTIMIZATION:
            solutions.extend(
                await self._generate_cost_optimized_solutions(
                    requirements, available_resources
                )
            )
        elif strategy == AllocationStrategy.LOAD_BALANCING:
            solutions.extend(
                await self._generate_load_balanced_solutions(
                    requirements, available_resources
                )
            )
        elif strategy == AllocationStrategy.HYBRID:
            # Generate solutions using multiple strategies
            solutions.extend(
                await self._generate_skill_based_solutions(
                    requirements, available_resources
                )
            )
            solutions.extend(
                await self._generate_cost_optimized_solutions(
                    requirements, available_resources
                )
            )
            solutions.extend(
                await self._generate_load_balanced_solutions(
                    requirements, available_resources
                )
            )
        
        return solutions
    
    async def _generate_skill_based_solutions(
        self,
        requirements: List[ResourceRequirement],
        available_resources: Dict[str, List[Dict[str, Any]]]
    ) -> List[OptimalAllocation]:
        """Generate skill-based allocation solutions"""
        solutions = []
        
        # Create allocation based on best skill match
        allocations = []
        total_cost = 0.0
        
        for req in requirements:
            if req.requirement_id in available_resources:
                # Score resources by skill compatibility
                scored_resources = []
                
                for resource in available_resources[req.requirement_id]:
                    skill_score = self._calculate_skill_score(
                        req.required_skills, resource['skills']
                    )
                    scored_resources.append((skill_score, resource))
                
                # Select best matching resource
                if scored_resources:
                    scored_resources.sort(key=lambda x: x[0], reverse=True)
                    best_resource = scored_resources[0][1]
                    
                    allocation = ResourceAllocation(
                        allocation_id=str(uuid.uuid4()),
                        resource_id=best_resource['resource_id'],
                        task_id=req.task_id,
                        quantity=req.quantity,
                        start_time=req.start_time or datetime.now(),
                        end_time=req.end_time or (
                            datetime.now() + timedelta(hours=req.duration)
                        ),
                        efficiency_score=scored_resources[0][0],
                        cost=best_resource['cost'] * req.duration * req.quantity
                    )
                    
                    allocations.append(allocation)
                    total_cost += allocation.cost
        
        if allocations:
            solution = OptimalAllocation(
                solution_id=str(uuid.uuid4()),
                project_id="",  # Will be set by caller
                allocations=allocations,
                total_cost=total_cost,
                efficiency_score=sum(a.efficiency_score for a in allocations) / len(allocations),
                utilization_rate=0.0,  # Will be calculated
                quality_score=0.8,  # High for skill-based allocation
                risk_score=0.2,
                constraints_satisfied=len(allocations),
                optimization_time=0.0
            )
            solutions.append(solution)
        
        return solutions
    
    async def _generate_cost_optimized_solutions(
        self,
        requirements: List[ResourceRequirement],
        available_resources: Dict[str, List[Dict[str, Any]]]
    ) -> List[OptimalAllocation]:
        """Generate cost-optimized allocation solutions"""
        solutions = []
        
        # Create allocation based on lowest cost
        allocations = []
        total_cost = 0.0
        
        for req in requirements:
            if req.requirement_id in available_resources:
                # Sort resources by cost
                available = available_resources[req.requirement_id]
                available.sort(key=lambda x: x['cost'])
                
                if available:
                    cheapest_resource = available[0]
                    
                    allocation = ResourceAllocation(
                        allocation_id=str(uuid.uuid4()),
                        resource_id=cheapest_resource['resource_id'],
                        task_id=req.task_id,
                        quantity=req.quantity,
                        start_time=req.start_time or datetime.now(),
                        end_time=req.end_time or (
                            datetime.now() + timedelta(hours=req.duration)
                        ),
                        efficiency_score=0.7,  # May be lower due to skill mismatch
                        cost=cheapest_resource['cost'] * req.duration * req.quantity
                    )
                    
                    allocations.append(allocation)
                    total_cost += allocation.cost
        
        if allocations:
            solution = OptimalAllocation(
                solution_id=str(uuid.uuid4()),
                project_id="",
                allocations=allocations,
                total_cost=total_cost,
                efficiency_score=sum(a.efficiency_score for a in allocations) / len(allocations),
                utilization_rate=0.0,
                quality_score=0.6,  # May be lower for cost optimization
                risk_score=0.4,
                constraints_satisfied=len(allocations),
                optimization_time=0.0
            )
            solutions.append(solution)
        
        return solutions
    
    async def _generate_load_balanced_solutions(
        self,
        requirements: List[ResourceRequirement],
        available_resources: Dict[str, List[Dict[str, Any]]]
    ) -> List[OptimalAllocation]:
        """Generate load-balanced allocation solutions"""
        solutions = []
        
        # Track resource utilization
        resource_loads = defaultdict(float)
        allocations = []
        total_cost = 0.0
        
        for req in requirements:
            if req.requirement_id in available_resources:
                # Find least utilized resource
                available = available_resources[req.requirement_id]
                
                best_resource = None
                min_load = float('inf')
                
                for resource in available:
                    resource_id = resource['resource_id']
                    current_load = (
                        resource_loads[resource_id] + 
                        resource['utilization']
                    )
                    
                    if current_load < min_load:
                        min_load = current_load
                        best_resource = resource
                
                if best_resource:
                    allocation = ResourceAllocation(
                        allocation_id=str(uuid.uuid4()),
                        resource_id=best_resource['resource_id'],
                        task_id=req.task_id,
                        quantity=req.quantity,
                        start_time=req.start_time or datetime.now(),
                        end_time=req.end_time or (
                            datetime.now() + timedelta(hours=req.duration)
                        ),
                        efficiency_score=0.75,
                        cost=best_resource['cost'] * req.duration * req.quantity
                    )
                    
                    allocations.append(allocation)
                    total_cost += allocation.cost
                    resource_loads[best_resource['resource_id']] += req.duration
        
        if allocations:
            # Calculate utilization balance score
            load_values = list(resource_loads.values())
            utilization_variance = np.var(load_values) if load_values else 0
            balance_score = 1.0 / (1.0 + utilization_variance)
            
            solution = OptimalAllocation(
                solution_id=str(uuid.uuid4()),
                project_id="",
                allocations=allocations,
                total_cost=total_cost,
                efficiency_score=sum(a.efficiency_score for a in allocations) / len(allocations),
                utilization_rate=balance_score,
                quality_score=0.7,
                risk_score=0.3,
                constraints_satisfied=len(allocations),
                optimization_time=0.0
            )
            solutions.append(solution)
        
        return solutions
    
    def _calculate_skill_score(
        self, 
        required_skills: List[str], 
        resource_skills: List[str]
    ) -> float:
        """Calculate skill compatibility score"""
        if not required_skills:
            return 1.0
        
        if not resource_skills:
            return 0.0
        
        # Calculate Jaccard similarity
        required_set = set(required_skills)
        resource_set = set(resource_skills)
        
        intersection = len(required_set.intersection(resource_set))
        union = len(required_set.union(resource_set))
        
        if union == 0:
            return 0.0
        
        return intersection / union
    
    async def _select_optimal_solution(
        self,
        solutions: List[OptimalAllocation],
        strategy: AllocationStrategy
    ) -> OptimalAllocation:
        """Select optimal solution based on strategy"""
        if not solutions:
            raise ValueError("No feasible allocation solutions found")
        
        # Score solutions based on multiple criteria
        for solution in solutions:
            score = 0.0
            
            # Cost score (lower is better)
            max_cost = max(s.total_cost for s in solutions)
            min_cost = min(s.total_cost for s in solutions)
            cost_range = max_cost - min_cost
            
            if cost_range > 0:
                cost_score = 1.0 - (solution.total_cost - min_cost) / cost_range
            else:
                cost_score = 1.0
            
            score += cost_score * self.allocation_weights['cost']
            
            # Efficiency score
            score += solution.efficiency_score * self.allocation_weights['efficiency']
            
            # Utilization score
            score += solution.utilization_rate * self.allocation_weights['utilization']
            
            # Quality score
            score += solution.quality_score * self.allocation_weights['quality']
            
            # Risk score (lower is better)
            score += (1.0 - solution.risk_score) * self.allocation_weights['risk']
            
            solution.optimization_score = score
        
        # Select best solution
        best_solution = max(solutions, key=lambda s: getattr(s, 'optimization_score', 0))
        
        # Store alternative solutions
        alternatives = [s for s in solutions if s != best_solution]
        best_solution.alternative_solutions = [
            {
                'solution_id': alt.solution_id,
                'total_cost': alt.total_cost,
                'efficiency_score': alt.efficiency_score,
                'optimization_score': getattr(alt, 'optimization_score', 0)
            }
            for alt in alternatives[:3]  # Store top 3 alternatives
        ]
        
        return best_solution
    
    async def _apply_allocation(self, solution: OptimalAllocation):
        """Apply allocation solution"""
        for allocation in solution.allocations:
            # Update resource utilization
            await self._update_resource_utilization(
                allocation.resource_id, allocation
            )
            
            # Record allocation
            allocation.status = ResourceStatus.ALLOCATED
    
    async def _update_resource_utilization(
        self, 
        resource_id: str, 
        allocation: ResourceAllocation
    ):
        """Update resource utilization metrics"""
        # Find the pool containing this resource
        for pool in self.resource_pools.values():
            if any(r['id'] == resource_id for r in pool.resources):
                if resource_id in pool.utilization_metrics:
                    metrics = pool.utilization_metrics[resource_id]
                    
                    # Update current utilization
                    duration_hours = (
                        allocation.end_time - allocation.start_time
                    ).total_seconds() / 3600
                    
                    # Simple utilization calculation
                    weekly_hours = 40.0  # Assume 40-hour work week
                    utilization_increase = (duration_hours * allocation.quantity) / weekly_hours
                    
                    metrics['current_utilization'] += utilization_increase
                    
                    # Update efficiency score based on allocation
                    metrics['efficiency_score'] = (
                        (metrics['efficiency_score'] + allocation.efficiency_score) / 2
                    )
                break
    
    async def _analyze_utilization(
        self, 
        pool: ResourcePool, 
        time_window: int
    ) -> ResourceUtilization:
        """Analyze resource utilization for a pool"""
        # Aggregate utilization across all resources in pool
        total_utilization = 0.0
        total_efficiency = 0.0
        resource_count = len(pool.resources)
        
        workload_distribution = {}
        recommendations = []
        
        for resource in pool.resources:
            resource_id = resource['id']
            metrics = pool.utilization_metrics.get(resource_id, {})
            
            utilization = metrics.get('current_utilization', 0.0)
            efficiency = metrics.get('efficiency_score', 1.0)
            
            total_utilization += utilization
            total_efficiency += efficiency
            
            workload_distribution[resource_id] = utilization
            
            # Generate recommendations
            if utilization > 0.9:
                recommendations.append(
                    f"Resource {resource_id} is overloaded ({utilization:.1%})"
                )
            elif utilization < 0.3:
                recommendations.append(
                    f"Resource {resource_id} is underutilized ({utilization:.1%})"
                )
        
        avg_utilization = total_utilization / max(resource_count, 1)
        avg_efficiency = total_efficiency / max(resource_count, 1)
        
        # Calculate satisfaction score
        utilization_variance = np.var(list(workload_distribution.values()))
        satisfaction_score = 1.0 / (1.0 + utilization_variance)
        
        return ResourceUtilization(
            resource_id=pool.pool_id,
            utilization_rate=avg_utilization,
            efficiency_score=avg_efficiency,
            workload_distribution=workload_distribution,
            peak_usage_times=[],  # Would be calculated from historical data
            idle_times=[],  # Would be calculated from schedule analysis
            satisfaction_score=satisfaction_score,
            recommendations=recommendations
        )
    
    async def _generate_utilization_recommendations(
        self,
        pool: ResourcePool,
        utilization_data: ResourceUtilization
    ) -> List[str]:
        """Generate utilization optimization recommendations"""
        recommendations = []
        
        # Analyze utilization patterns
        avg_utilization = utilization_data.utilization_rate
        
        if avg_utilization > 0.85:
            recommendations.extend([
                "Consider adding more resources to the pool",
                "Implement overtime policies for peak periods",
                "Evaluate task prioritization and scheduling"
            ])
        elif avg_utilization < 0.4:
            recommendations.extend([
                "Consider reducing pool size or reallocating resources",
                "Look for additional work opportunities",
                "Cross-train resources for other skill areas"
            ])
        
        # Analyze workload distribution
        workloads = list(utilization_data.workload_distribution.values())
        if workloads:
            workload_std = np.std(workloads)
            if workload_std > 0.3:
                recommendations.append(
                    "Implement load balancing to distribute work more evenly"
                )
        
        return recommendations
    
    async def _update_pool_metrics(
        self, 
        pool: ResourcePool, 
        utilization_data: ResourceUtilization
    ):
        """Update pool metrics with utilization data"""
        # Update pool-level metrics
        pool.utilization_metrics['pool_average'] = utilization_data.utilization_rate
        pool.utilization_metrics['pool_efficiency'] = utilization_data.efficiency_score
        pool.utilization_metrics['pool_satisfaction'] = utilization_data.satisfaction_score
        
        # Store utilization history
        self.utilization_history[pool.pool_id].append({
            'timestamp': datetime.now(),
            'utilization_rate': utilization_data.utilization_rate,
            'efficiency_score': utilization_data.efficiency_score,
            'satisfaction_score': utilization_data.satisfaction_score
        })
    
    async def _analyze_current_capacity(self, pools: List[str]) -> Dict[str, float]:
        """Analyze current capacity across pools"""
        capacity = {}
        
        for pool_id in pools:
            if pool_id in self.resource_pools:
                pool = self.resource_pools[pool_id]
                
                # Calculate total capacity
                total_capacity = 0.0
                for resource in pool.resources:
                    # Assume 40 hours per week per resource
                    total_capacity += 40.0
                
                capacity[pool_id] = total_capacity
        
        return capacity
    
    async def _forecast_demand(
        self,
        pools: List[str],
        time_horizon: int,
        growth_scenarios: Optional[List[Dict[str, Any]]]
    ) -> Dict[str, float]:
        """Forecast resource demand"""
        demand_forecast = {}
        
        # Simple linear projection based on historical data
        for pool_id in pools:
            if pool_id in self.utilization_history:
                history = self.utilization_history[pool_id]
                
                if len(history) >= 2:
                    # Calculate trend
                    recent_utilization = [h['utilization_rate'] for h in history[-4:]]
                    avg_utilization = np.mean(recent_utilization)
                    
                    # Project demand
                    if pool_id in self.resource_pools:
                        pool = self.resource_pools[pool_id]
                        current_capacity = len(pool.resources) * 40.0  # 40 hours/week
                        projected_demand = current_capacity * avg_utilization * 1.1  # 10% buffer
                        
                        demand_forecast[pool_id] = projected_demand
                    else:
                        demand_forecast[pool_id] = 0.0
                else:
                    demand_forecast[pool_id] = 0.0
            else:
                demand_forecast[pool_id] = 0.0
        
        return demand_forecast
    
    async def _analyze_capacity_gaps(
        self,
        current_capacity: Dict[str, float],
        demand_forecast: Dict[str, float]
    ) -> Dict[str, Dict[str, float]]:
        """Analyze capacity gaps and surpluses"""
        analysis = {
            'gaps': {},
            'surplus': {}
        }
        
        for pool_id in current_capacity:
            capacity = current_capacity[pool_id]
            demand = demand_forecast.get(pool_id, 0.0)
            
            if demand > capacity:
                analysis['gaps'][pool_id] = demand - capacity
            else:
                analysis['surplus'][pool_id] = capacity - demand
        
        return analysis
    
    async def _generate_scaling_recommendations(
        self,
        capacity_analysis: Dict[str, Dict[str, float]],
        time_horizon: int
    ) -> List[Dict[str, Any]]:
        """Generate scaling recommendations"""
        recommendations = []
        
        # Handle capacity gaps
        for pool_id, gap in capacity_analysis['gaps'].items():
            if gap > 20:  # More than 20 hours gap
                additional_resources = int(np.ceil(gap / 40))  # 40 hours per resource
                
                recommendations.append({
                    'type': 'scale_up',
                    'pool_id': pool_id,
                    'action': f'Add {additional_resources} resources',
                    'urgency': 'high' if gap > 80 else 'medium',
                    'estimated_cost': additional_resources * 50 * 40 * 4,  # Monthly cost
                    'timeline': f'{time_horizon // 7} weeks'
                })
        
        # Handle surplus capacity
        for pool_id, surplus in capacity_analysis['surplus'].items():
            if surplus > 40:  # More than 1 full resource surplus
                excess_resources = int(surplus // 40)
                
                recommendations.append({
                    'type': 'scale_down',
                    'pool_id': pool_id,
                    'action': f'Consider reducing by {excess_resources} resources',
                    'urgency': 'low',
                    'estimated_savings': excess_resources * 50 * 40 * 4,  # Monthly savings
                    'timeline': f'{time_horizon // 7} weeks'
                })
        
        return recommendations
    
    async def _project_costs(
        self,
        scaling_recommendations: List[Dict[str, Any]],
        time_horizon: int
    ) -> Dict[str, float]:
        """Project costs for scaling recommendations"""
        cost_projections = {
            'current_costs': 0.0,
            'projected_costs': 0.0,
            'scaling_costs': 0.0,
            'cost_savings': 0.0
        }
        
        # Calculate current costs
        for pool in self.resource_pools.values():
            monthly_pool_cost = len(pool.resources) * 50 * 40 * 4  # $50/hour * 40h/week * 4 weeks
            cost_projections['current_costs'] += monthly_pool_cost
        
        # Calculate scaling costs
        for recommendation in scaling_recommendations:
            if recommendation['type'] == 'scale_up':
                cost_projections['scaling_costs'] += recommendation.get('estimated_cost', 0)
            elif recommendation['type'] == 'scale_down':
                cost_projections['cost_savings'] += recommendation.get('estimated_savings', 0)
        
        cost_projections['projected_costs'] = (
            cost_projections['current_costs'] + 
            cost_projections['scaling_costs'] - 
            cost_projections['cost_savings']
        )
        
        return cost_projections
    
    async def _identify_capacity_risks(
        self, 
        capacity_analysis: Dict[str, Dict[str, float]]
    ) -> List[str]:
        """Identify capacity-related risks"""
        risks = []
        
        # High demand risks
        for pool_id, gap in capacity_analysis['gaps'].items():
            if gap > 80:  # More than 2 resources gap
                risks.append(f"Critical capacity shortage in pool {pool_id}")
            elif gap > 40:
                risks.append(f"Moderate capacity shortage in pool {pool_id}")
        
        # Low utilization risks
        for pool_id, surplus in capacity_analysis['surplus'].items():
            if surplus > 80:
                risks.append(f"Significant overcapacity in pool {pool_id}")
        
        return risks
    
    async def _apply_allocation_changes(
        self,
        current_allocation: OptimalAllocation,
        changes: List[Dict[str, Any]]
    ) -> List[ResourceRequirement]:
        """Apply changes to existing allocation"""
        # Convert current allocation back to requirements
        requirements = []
        
        for allocation in current_allocation.allocations:
            # Create requirement from allocation
            req = ResourceRequirement(
                requirement_id=str(uuid.uuid4()),
                task_id=allocation.task_id,
                resource_type=ResourceType.HUMAN,  # Simplified
                quantity=allocation.quantity,
                duration=(allocation.end_time - allocation.start_time).total_seconds() / 3600,
                start_time=allocation.start_time,
                end_time=allocation.end_time
            )
            requirements.append(req)
        
        # Apply changes
        for change in changes:
            change_type = change.get('type')
            
            if change_type == 'add_requirement':
                new_req = ResourceRequirement(
                    requirement_id=str(uuid.uuid4()),
                    task_id=change['task_id'],
                    resource_type=ResourceType(change['resource_type']),
                    quantity=change['quantity'],
                    duration=change['duration'],
                    required_skills=change.get('skills', [])
                )
                requirements.append(new_req)
            
            elif change_type == 'modify_requirement':
                task_id = change['task_id']
                for req in requirements:
                    if req.task_id == task_id:
                        if 'quantity' in change:
                            req.quantity = change['quantity']
                        if 'duration' in change:
                            req.duration = change['duration']
                        break
            
            elif change_type == 'remove_requirement':
                task_id = change['task_id']
                requirements = [req for req in requirements if req.task_id != task_id]
        
        return requirements
    
    async def _release_allocations(self, allocation: OptimalAllocation):
        """Release resources from allocation"""
        for alloc in allocation.allocations:
            alloc.status = ResourceStatus.AVAILABLE
            
            # Update resource utilization
            await self._reduce_resource_utilization(alloc.resource_id, alloc)
    
    async def _reduce_resource_utilization(
        self, 
        resource_id: str, 
        allocation: ResourceAllocation
    ):
        """Reduce resource utilization when releasing allocation"""
        for pool in self.resource_pools.values():
            if any(r['id'] == resource_id for r in pool.resources):
                if resource_id in pool.utilization_metrics:
                    metrics = pool.utilization_metrics[resource_id]
                    
                    # Reduce utilization
                    duration_hours = (
                        allocation.end_time - allocation.start_time
                    ).total_seconds() / 3600
                    
                    weekly_hours = 40.0
                    utilization_decrease = (duration_hours * allocation.quantity) / weekly_hours
                    
                    metrics['current_utilization'] = max(
                        0.0, metrics['current_utilization'] - utilization_decrease
                    )
                break
    
    async def get_allocation_metrics(self, solution_id: str) -> Dict[str, Any]:
        """Get comprehensive allocation metrics"""
        if solution_id not in self.allocations:
            raise ValueError(f"Allocation {solution_id} not found")
        
        allocation = self.allocations[solution_id]
        
        metrics = {
            'solution_id': solution_id,
            'project_id': allocation.project_id,
            'total_cost': allocation.total_cost,
            'efficiency_score': allocation.efficiency_score,
            'utilization_rate': allocation.utilization_rate,
            'quality_score': allocation.quality_score,
            'risk_score': allocation.risk_score,
            'resource_count': len(allocation.allocations),
            'constraints_satisfied': allocation.constraints_satisfied,
            'optimization_time': allocation.optimization_time,
            'alternative_solutions_count': len(allocation.alternative_solutions)
        }
        
        return metrics


# Export main classes
__all__ = [
    'ResourceAllocator',
    'ResourcePool',
    'ResourceRequirement',
    'ResourceAllocation',
    'ResourceUtilization',
    'CapacityPlanning',
    'OptimalAllocation',
    'AllocationStrategy',
    'ResourceType',
    'ResourceStatus'
]