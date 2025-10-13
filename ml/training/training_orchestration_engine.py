"""
🎼 Training Orchestration Engine - Enterprise Multi-Model Training Coordinator

🎖️ LEAD DEV IA + ⚙️ DEVOPS + 🔬 ML ENGINEER EXPERTISE

Advanced training orchestration system for coordinating multiple ML model training
tasks, resource optimization, and creator-specific training workflows across
distributed infrastructure with intelligent scheduling and monitoring.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel. All rights reserved.
Version: 1.0.0

🎼 TRAINING ORCHESTRATION PLATFORM
- Multi-model training coordination and scheduling
- Resource allocation and optimization
- Creator-specific training workflow management
- Distributed training across multiple nodes/GPUs
- Real-time monitoring and adaptive scheduling
- Enterprise-grade fault tolerance and recovery
"""

import asyncio
import logging
import json
import numpy as np
import torch
import torch.nn as nn
import torch.multiprocessing as mp
from typing import Dict, List, Optional, Any, Tuple, Union, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import uuid
import yaml
import concurrent.futures
from collections import defaultdict, deque
import heapq
import threading
import queue

logger = logging.getLogger(__name__)

class TrainingJobStatus(Enum):
    """Training job status types"""
    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"

class JobPriority(Enum):
    """Job priority levels"""
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4
    BACKGROUND = 5

class ResourceType(Enum):
    """Resource types for allocation"""
    CPU = "cpu"
    GPU = "gpu"
    MEMORY = "memory"
    STORAGE = "storage"
    NETWORK = "network"

class CreatorType(Enum):
    """Creator types for specialized training"""
    MUSICIAN = "musician"
    BLOGGER = "blogger"
    PHOTOGRAPHER = "photographer"
    INFLUENCER = "influencer"
    COMEDIAN = "comedian"
    GENERAL = "general"

@dataclass
class ResourceRequirement:
    """Resource requirement specification"""
    resource_type: ResourceType
    amount: float
    unit: str
    min_amount: Optional[float] = None
    max_amount: Optional[float] = None
    preferred_amount: Optional[float] = None

@dataclass
class TrainingJobConfig:
    """Training job configuration"""
    job_id: str
    job_name: str
    model_config: Dict[str, Any]
    dataset_config: Dict[str, Any]
    training_config: Dict[str, Any]
    resource_requirements: List[ResourceRequirement]
    priority: JobPriority
    creator_type: CreatorType
    estimated_duration_hours: float
    max_retries: int = 3
    timeout_hours: float = 24.0
    dependencies: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    notifications: Dict[str, Any] = field(default_factory=dict)
    custom_parameters: Dict[str, Any] = field(default_factory=dict)

@dataclass
class TrainingJobState:
    """Training job execution state"""
    job_id: str
    status: TrainingJobStatus
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    progress_percentage: float = 0.0
    current_epoch: int = 0
    total_epochs: int = 0
    current_loss: float = 0.0
    best_loss: float = float('inf')
    assigned_resources: Dict[str, Any] = field(default_factory=dict)
    metrics: Dict[str, float] = field(default_factory=dict)
    logs: List[str] = field(default_factory=list)
    error_message: Optional[str] = None
    retry_count: int = 0
    worker_id: Optional[str] = None

@dataclass
class ResourcePool:
    """Resource pool for training allocation"""
    pool_id: str
    resource_type: ResourceType
    total_capacity: float
    available_capacity: float
    allocated_capacity: float
    unit: str
    efficiency_score: float = 1.0
    maintenance_scheduled: bool = False
    last_update: datetime = field(default_factory=datetime.now)

@dataclass
class TrainingWorker:
    """Training worker specification"""
    worker_id: str
    worker_type: str
    resource_capacity: Dict[ResourceType, float]
    current_jobs: List[str]
    max_concurrent_jobs: int
    status: str
    last_heartbeat: datetime
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    creator_specialization: Optional[CreatorType] = None

class ResourceManager:
    """🛡️ BACKEND SENIOR - Resource allocation and optimization"""
    
    def __init__(self):
        self.resource_pools: Dict[str, ResourcePool] = {}
        self.allocation_history = []
        self.optimization_strategies = {
            "round_robin": self._round_robin_allocation,
            "load_balanced": self._load_balanced_allocation,
            "creator_optimized": self._creator_optimized_allocation,
            "priority_based": self._priority_based_allocation
        }
        
    def initialize_resource_pools(self, pool_configs: List[Dict[str, Any]]) -> None:
        """Initialize resource pools from configuration"""
        for config in pool_configs:
            pool = ResourcePool(
                pool_id=config["pool_id"],
                resource_type=ResourceType(config["resource_type"]),
                total_capacity=config["total_capacity"],
                available_capacity=config["total_capacity"],
                allocated_capacity=0.0,
                unit=config["unit"],
                efficiency_score=config.get("efficiency_score", 1.0)
            )
            self.resource_pools[pool.pool_id] = pool
            
        logger.info(f"🔧 Initialized {len(self.resource_pools)} resource pools")
    
    async def allocate_resources(self, job_config: TrainingJobConfig,
                               strategy: str = "creator_optimized") -> Dict[str, Any]:
        """Allocate resources for training job"""
        
        if strategy not in self.optimization_strategies:
            strategy = "load_balanced"
        
        allocation_func = self.optimization_strategies[strategy]
        allocation = await allocation_func(job_config)
        
        if allocation.get("success", False):
            # Update resource pools
            for resource_id, amount in allocation.get("allocated_resources", {}).items():
                if resource_id in self.resource_pools:
                    pool = self.resource_pools[resource_id]
                    pool.allocated_capacity += amount
                    pool.available_capacity -= amount
                    pool.last_update = datetime.now()
            
            # Record allocation
            self.allocation_history.append({
                "job_id": job_config.job_id,
                "allocation": allocation,
                "timestamp": datetime.now(),
                "strategy": strategy
            })
            
            logger.info(f"✅ Resources allocated for job {job_config.job_id}")
        
        return allocation
    
    async def deallocate_resources(self, job_id: str, allocated_resources: Dict[str, Any]) -> None:
        """Deallocate resources after job completion"""
        for resource_id, amount in allocated_resources.items():
            if resource_id in self.resource_pools:
                pool = self.resource_pools[resource_id]
                pool.allocated_capacity = max(0, pool.allocated_capacity - amount)
                pool.available_capacity = min(pool.total_capacity, 
                                            pool.available_capacity + amount)
                pool.last_update = datetime.now()
        
        logger.info(f"🔄 Resources deallocated for job {job_id}")
    
    async def _round_robin_allocation(self, job_config: TrainingJobConfig) -> Dict[str, Any]:
        """Round-robin resource allocation strategy"""
        allocation = {"success": False, "allocated_resources": {}, "worker_assignments": []}
        
        # Simple round-robin allocation
        available_pools = [p for p in self.resource_pools.values() 
                          if p.available_capacity > 0 and not p.maintenance_scheduled]
        
        if not available_pools:
            allocation["error"] = "No available resource pools"
            return allocation
        
        # Allocate from first available pool for each requirement
        allocated = {}
        for req in job_config.resource_requirements:
            suitable_pools = [p for p in available_pools if p.resource_type == req.resource_type]
            
            if suitable_pools and suitable_pools[0].available_capacity >= req.amount:
                pool = suitable_pools[0]
                allocated[pool.pool_id] = req.amount
            else:
                allocation["error"] = f"Insufficient {req.resource_type.value} resources"
                return allocation
        
        allocation["success"] = True
        allocation["allocated_resources"] = allocated
        return allocation
    
    async def _load_balanced_allocation(self, job_config: TrainingJobConfig) -> Dict[str, Any]:
        """Load-balanced resource allocation strategy"""
        allocation = {"success": False, "allocated_resources": {}, "worker_assignments": []}
        
        allocated = {}
        
        for req in job_config.resource_requirements:
            # Find pools with the resource type
            suitable_pools = [p for p in self.resource_pools.values() 
                            if (p.resource_type == req.resource_type and 
                                p.available_capacity >= req.amount and 
                                not p.maintenance_scheduled)]
            
            if not suitable_pools:
                allocation["error"] = f"No available {req.resource_type.value} pools"
                return allocation
            
            # Choose pool with highest availability ratio
            best_pool = max(suitable_pools, 
                          key=lambda p: p.available_capacity / p.total_capacity)
            allocated[best_pool.pool_id] = req.amount
        
        allocation["success"] = True
        allocation["allocated_resources"] = allocated
        return allocation
    
    async def _creator_optimized_allocation(self, job_config: TrainingJobConfig) -> Dict[str, Any]:
        """Creator-optimized resource allocation strategy"""
        allocation = {"success": False, "allocated_resources": {}, "worker_assignments": []}
        
        # Creator-specific resource optimization
        creator_multipliers = {
            CreatorType.MUSICIAN: {"gpu": 1.2, "memory": 1.1, "cpu": 0.9},
            CreatorType.PHOTOGRAPHER: {"gpu": 1.5, "memory": 1.3, "cpu": 1.0},
            CreatorType.BLOGGER: {"gpu": 0.8, "memory": 0.9, "cpu": 1.2},
            CreatorType.INFLUENCER: {"gpu": 1.1, "memory": 1.0, "cpu": 1.1},
            CreatorType.COMEDIAN: {"gpu": 1.3, "memory": 1.2, "cpu": 1.0}
        }
        
        multipliers = creator_multipliers.get(job_config.creator_type, {"gpu": 1.0, "memory": 1.0, "cpu": 1.0})
        allocated = {}
        
        for req in job_config.resource_requirements:
            # Apply creator-specific multiplier
            resource_key = req.resource_type.value
            multiplier = multipliers.get(resource_key, 1.0)
            adjusted_amount = req.amount * multiplier
            
            # Find best pool considering creator optimization
            suitable_pools = [p for p in self.resource_pools.values() 
                            if (p.resource_type == req.resource_type and 
                                p.available_capacity >= adjusted_amount and 
                                not p.maintenance_scheduled)]
            
            if not suitable_pools:
                allocation["error"] = f"Insufficient {req.resource_type.value} for creator type {job_config.creator_type.value}"
                return allocation
            
            # Prioritize pools with higher efficiency for this creator type
            best_pool = max(suitable_pools, key=lambda p: p.efficiency_score)
            allocated[best_pool.pool_id] = adjusted_amount
        
        allocation["success"] = True
        allocation["allocated_resources"] = allocated
        allocation["creator_optimized"] = True
        return allocation
    
    async def _priority_based_allocation(self, job_config: TrainingJobConfig) -> Dict[str, Any]:
        """Priority-based resource allocation strategy"""
        allocation = {"success": False, "allocated_resources": {}, "worker_assignments": []}
        
        # Priority-based resource allocation
        priority_multipliers = {
            JobPriority.CRITICAL: 1.5,
            JobPriority.HIGH: 1.2,
            JobPriority.MEDIUM: 1.0,
            JobPriority.LOW: 0.8,
            JobPriority.BACKGROUND: 0.6
        }
        
        multiplier = priority_multipliers.get(job_config.priority, 1.0)
        allocated = {}
        
        for req in job_config.resource_requirements:
            # Apply priority multiplier
            adjusted_amount = req.amount * multiplier
            
            suitable_pools = [p for p in self.resource_pools.values() 
                            if (p.resource_type == req.resource_type and 
                                p.available_capacity >= adjusted_amount and 
                                not p.maintenance_scheduled)]
            
            if not suitable_pools:
                # For high priority jobs, try to preempt lower priority jobs
                if job_config.priority in [JobPriority.CRITICAL, JobPriority.HIGH]:
                    preemption_result = await self._attempt_preemption(req, job_config.priority)
                    if preemption_result["success"]:
                        allocated.update(preemption_result["allocated_resources"])
                        continue
                
                allocation["error"] = f"Insufficient {req.resource_type.value} for priority {job_config.priority.value}"
                return allocation
            
            best_pool = max(suitable_pools, key=lambda p: p.available_capacity)
            allocated[best_pool.pool_id] = adjusted_amount
        
        allocation["success"] = True
        allocation["allocated_resources"] = allocated
        return allocation
    
    async def _attempt_preemption(self, resource_req: ResourceRequirement, 
                                 job_priority: JobPriority) -> Dict[str, Any]:
        """Attempt to preempt lower priority jobs for resources"""
        # Implementation would involve finding and pausing lower priority jobs
        # This is a simplified version
        return {"success": False, "allocated_resources": {}}

class JobScheduler:
    """🎖️ LEAD DEV IA - Intelligent job scheduling and orchestration"""
    
    def __init__(self):
        self.job_queue: List[Tuple[int, TrainingJobConfig]] = []  # Priority queue
        self.running_jobs: Dict[str, TrainingJobState] = {}
        self.completed_jobs: Dict[str, TrainingJobState] = {}
        self.scheduling_strategies = {
            "fifo": self._fifo_scheduling,
            "priority": self._priority_scheduling,
            "shortest_job_first": self._sjf_scheduling,
            "creator_aware": self._creator_aware_scheduling
        }
        self.dependency_graph: Dict[str, List[str]] = {}
        
    def submit_job(self, job_config: TrainingJobConfig) -> bool:
        """Submit training job to scheduler"""
        try:
            # Add to dependency graph
            self.dependency_graph[job_config.job_id] = job_config.dependencies
            
            # Add to priority queue
            priority_value = job_config.priority.value
            heapq.heappush(self.job_queue, (priority_value, job_config))
            
            logger.info(f"📝 Job {job_config.job_id} submitted with priority {job_config.priority.value}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to submit job {job_config.job_id}: {e}")
            return False
    
    async def schedule_next_job(self, strategy: str = "creator_aware") -> Optional[TrainingJobConfig]:
        """Schedule next job using specified strategy"""
        if not self.job_queue:
            return None
        
        if strategy not in self.scheduling_strategies:
            strategy = "priority"
        
        scheduling_func = self.scheduling_strategies[strategy]
        return await scheduling_func()
    
    async def _fifo_scheduling(self) -> Optional[TrainingJobConfig]:
        """First-In-First-Out scheduling"""
        if self.job_queue:
            _, job_config = heapq.heappop(self.job_queue)
            if self._check_dependencies(job_config):
                return job_config
            else:
                # Re-queue if dependencies not met
                heapq.heappush(self.job_queue, (job_config.priority.value, job_config))
        return None
    
    async def _priority_scheduling(self) -> Optional[TrainingJobConfig]:
        """Priority-based scheduling"""
        if self.job_queue:
            _, job_config = heapq.heappop(self.job_queue)
            if self._check_dependencies(job_config):
                return job_config
            else:
                heapq.heappush(self.job_queue, (job_config.priority.value, job_config))
        return None
    
    async def _sjf_scheduling(self) -> Optional[TrainingJobConfig]:
        """Shortest Job First scheduling"""
        if not self.job_queue:
            return None
        
        # Find job with shortest estimated duration
        min_duration = float('inf')
        best_job_idx = -1
        
        for i, (priority, job_config) in enumerate(self.job_queue):
            if (job_config.estimated_duration_hours < min_duration and 
                self._check_dependencies(job_config)):
                min_duration = job_config.estimated_duration_hours
                best_job_idx = i
        
        if best_job_idx >= 0:
            # Remove job from queue
            _, job_config = self.job_queue.pop(best_job_idx)
            heapq.heapify(self.job_queue)  # Re-heapify after removal
            return job_config
        
        return None
    
    async def _creator_aware_scheduling(self) -> Optional[TrainingJobConfig]:
        """Creator-aware scheduling with load balancing"""
        if not self.job_queue:
            return None
        
        # Count running jobs by creator type
        creator_loads = defaultdict(int)
        for job_state in self.running_jobs.values():
            # Would need to track creator type in job state
            creator_loads["general"] += 1
        
        # Find job with least loaded creator type
        min_load = float('inf')
        best_job_idx = -1
        
        for i, (priority, job_config) in enumerate(self.job_queue):
            creator_load = creator_loads.get(job_config.creator_type.value, 0)
            
            if (creator_load < min_load and self._check_dependencies(job_config)):
                min_load = creator_load
                best_job_idx = i
        
        if best_job_idx >= 0:
            _, job_config = self.job_queue.pop(best_job_idx)
            heapq.heapify(self.job_queue)
            return job_config
        
        return None
    
    def _check_dependencies(self, job_config: TrainingJobConfig) -> bool:
        """Check if job dependencies are satisfied"""
        for dep_job_id in job_config.dependencies:
            if (dep_job_id not in self.completed_jobs or 
                self.completed_jobs[dep_job_id].status != TrainingJobStatus.COMPLETED):
                return False
        return True
    
    def update_job_status(self, job_id: str, status: TrainingJobStatus,
                         metrics: Optional[Dict[str, float]] = None) -> None:
        """Update job status and metrics"""
        if job_id in self.running_jobs:
            job_state = self.running_jobs[job_id]
            job_state.status = status
            
            if metrics:
                job_state.metrics.update(metrics)
            
            if status == TrainingJobStatus.COMPLETED:
                job_state.end_time = datetime.now()
                self.completed_jobs[job_id] = job_state
                del self.running_jobs[job_id]
            elif status == TrainingJobStatus.FAILED:
                job_state.end_time = datetime.now()
                job_state.retry_count += 1
                # Could implement retry logic here

class WorkerManager:
    """⚙️ DEVOPS - Training worker management and coordination"""
    
    def __init__(self):
        self.workers: Dict[str, TrainingWorker] = {}
        self.worker_pool = concurrent.futures.ThreadPoolExecutor(max_workers=10)
        self.heartbeat_timeout = timedelta(minutes=5)
        
    def register_worker(self, worker_config: Dict[str, Any]) -> str:
        """Register new training worker"""
        worker_id = worker_config.get("worker_id", str(uuid.uuid4()))
        
        worker = TrainingWorker(
            worker_id=worker_id,
            worker_type=worker_config["worker_type"],
            resource_capacity={
                ResourceType(k): v for k, v in worker_config["resource_capacity"].items()
            },
            current_jobs=[],
            max_concurrent_jobs=worker_config.get("max_concurrent_jobs", 1),
            status="available",
            last_heartbeat=datetime.now(),
            creator_specialization=CreatorType(worker_config.get("creator_specialization", "general"))
        )
        
        self.workers[worker_id] = worker
        logger.info(f"👷 Worker {worker_id} registered ({worker.worker_type})")
        return worker_id
    
    async def assign_job_to_worker(self, job_config: TrainingJobConfig,
                                  job_state: TrainingJobState) -> Optional[str]:
        """Assign training job to available worker"""
        
        # Find suitable workers
        suitable_workers = []
        
        for worker in self.workers.values():
            if (worker.status == "available" and 
                len(worker.current_jobs) < worker.max_concurrent_jobs and
                self._worker_can_handle_job(worker, job_config)):
                suitable_workers.append(worker)
        
        if not suitable_workers:
            logger.warning(f"No available workers for job {job_config.job_id}")
            return None
        
        # Choose best worker (creator specialization, resource capacity, etc.)
        best_worker = self._select_best_worker(suitable_workers, job_config)
        
        # Assign job to worker
        best_worker.current_jobs.append(job_config.job_id)
        best_worker.status = "busy" if len(best_worker.current_jobs) >= best_worker.max_concurrent_jobs else "available"
        
        job_state.worker_id = best_worker.worker_id
        
        logger.info(f"👷 Job {job_config.job_id} assigned to worker {best_worker.worker_id}")
        return best_worker.worker_id
    
    def _worker_can_handle_job(self, worker: TrainingWorker, job_config: TrainingJobConfig) -> bool:
        """Check if worker can handle the job requirements"""
        for req in job_config.resource_requirements:
            if (req.resource_type not in worker.resource_capacity or
                worker.resource_capacity[req.resource_type] < req.amount):
                return False
        return True
    
    def _select_best_worker(self, workers: List[TrainingWorker], 
                          job_config: TrainingJobConfig) -> TrainingWorker:
        """Select best worker for job based on multiple criteria"""
        
        def worker_score(worker: TrainingWorker) -> float:
            score = 0.0
            
            # Creator specialization bonus
            if worker.creator_specialization == job_config.creator_type:
                score += 10.0
            
            # Resource capacity efficiency
            for req in job_config.resource_requirements:
                if req.resource_type in worker.resource_capacity:
                    utilization = req.amount / worker.resource_capacity[req.resource_type]
                    score += (1.0 - utilization) * 5.0  # Prefer not fully utilizing resources
            
            # Lower current load
            score += (worker.max_concurrent_jobs - len(worker.current_jobs)) * 2.0
            
            # Performance history
            avg_performance = np.mean(list(worker.performance_metrics.values())) if worker.performance_metrics else 0.5
            score += avg_performance * 3.0
            
            return score
        
        return max(workers, key=worker_score)
    
    async def update_worker_heartbeat(self, worker_id: str, metrics: Dict[str, float]) -> None:
        """Update worker heartbeat and performance metrics"""
        if worker_id in self.workers:
            worker = self.workers[worker_id]
            worker.last_heartbeat = datetime.now()
            worker.performance_metrics.update(metrics)
    
    def get_worker_health(self) -> Dict[str, Any]:
        """Get overall worker health status"""
        now = datetime.now()
        healthy_workers = 0
        unhealthy_workers = 0
        
        for worker in self.workers.values():
            if now - worker.last_heartbeat < self.heartbeat_timeout:
                healthy_workers += 1
            else:
                unhealthy_workers += 1
        
        return {
            "total_workers": len(self.workers),
            "healthy_workers": healthy_workers,
            "unhealthy_workers": unhealthy_workers,
            "utilization": sum(len(w.current_jobs) for w in self.workers.values()) / max(1, len(self.workers))
        }

class TrainingOrchestrationEngine:
    """
    🎼 🎖️ LEAD DEV IA + ⚙️ DEVOPS + 🔬 ML ENGINEER - MASTER CLASS
    
    Enterprise-grade training orchestration engine for coordinating multiple ML
    model training tasks with intelligent resource management and creator optimization.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path)
        self.resource_manager = ResourceManager()
        self.job_scheduler = JobScheduler()
        self.worker_manager = WorkerManager()
        
        # Orchestration state
        self.orchestration_active = False
        self.orchestration_stats = {
            "jobs_submitted": 0,
            "jobs_completed": 0,
            "jobs_failed": 0,
            "total_training_hours": 0.0,
            "resource_efficiency": 0.0
        }
        
        # Monitoring and alerting
        self.monitoring_enabled = True
        self.alert_thresholds = {
            "queue_length": 50,
            "failure_rate": 0.1,
            "resource_utilization": 0.9
        }
        
        logger.info("🎼 Training Orchestration Engine initialized")
    
    async def start_orchestration(self) -> None:
        """Start training orchestration system"""
        if self.orchestration_active:
            logger.warning("Orchestration already active")
            return
        
        self.orchestration_active = True
        
        # Initialize resource pools
        resource_configs = self.config.get("resource_pools", [
            {
                "pool_id": "gpu_pool_1",
                "resource_type": "gpu",
                "total_capacity": 8.0,
                "unit": "cards",
                "efficiency_score": 0.95
            },
            {
                "pool_id": "cpu_pool_1", 
                "resource_type": "cpu",
                "total_capacity": 64.0,
                "unit": "cores",
                "efficiency_score": 0.90
            },
            {
                "pool_id": "memory_pool_1",
                "resource_type": "memory",
                "total_capacity": 512.0,
                "unit": "GB",
                "efficiency_score": 0.92
            }
        ])
        
        self.resource_manager.initialize_resource_pools(resource_configs)
        
        # Register default workers
        await self._register_default_workers()
        
        # Start orchestration loop
        asyncio.create_task(self._orchestration_loop())
        
        logger.info("🚀 Training orchestration started")
    
    async def stop_orchestration(self) -> None:
        """Stop training orchestration system"""
        self.orchestration_active = False
        logger.info("🛑 Training orchestration stopped")
    
    async def submit_training_job(self, job_config: TrainingJobConfig) -> str:
        """Submit training job to orchestration system"""
        
        # Validate job configuration
        validation_result = await self._validate_job_config(job_config)
        if not validation_result["valid"]:
            raise ValueError(f"Invalid job configuration: {validation_result['errors']}")
        
        # Submit to scheduler
        success = self.job_scheduler.submit_job(job_config)
        if not success:
            raise RuntimeError(f"Failed to submit job {job_config.job_id}")
        
        self.orchestration_stats["jobs_submitted"] += 1
        
        logger.info(f"📤 Training job {job_config.job_id} submitted successfully")
        return job_config.job_id
    
    async def cancel_job(self, job_id: str) -> bool:
        """Cancel training job"""
        # Remove from queue if pending
        updated_queue = []
        job_found = False
        
        for priority, job_config in self.job_scheduler.job_queue:
            if job_config.job_id != job_id:
                updated_queue.append((priority, job_config))
            else:
                job_found = True
        
        if job_found:
            self.job_scheduler.job_queue = updated_queue
            heapq.heapify(self.job_scheduler.job_queue)
            logger.info(f"❌ Job {job_id} cancelled (was in queue)")
            return True
        
        # Cancel running job
        if job_id in self.job_scheduler.running_jobs:
            job_state = self.job_scheduler.running_jobs[job_id]
            job_state.status = TrainingJobStatus.CANCELLED
            job_state.end_time = datetime.now()
            
            # Deallocate resources
            if job_state.assigned_resources:
                await self.resource_manager.deallocate_resources(
                    job_id, job_state.assigned_resources
                )
            
            # Update worker
            if job_state.worker_id and job_state.worker_id in self.worker_manager.workers:
                worker = self.worker_manager.workers[job_state.worker_id]
                if job_id in worker.current_jobs:
                    worker.current_jobs.remove(job_id)
                    worker.status = "available" if len(worker.current_jobs) < worker.max_concurrent_jobs else "busy"
            
            del self.job_scheduler.running_jobs[job_id]
            logger.info(f"❌ Running job {job_id} cancelled")
            return True
        
        logger.warning(f"Job {job_id} not found for cancellation")
        return False
    
    async def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get training job status and metrics"""
        
        # Check running jobs
        if job_id in self.job_scheduler.running_jobs:
            job_state = self.job_scheduler.running_jobs[job_id]
            return self._serialize_job_state(job_state)
        
        # Check completed jobs
        if job_id in self.job_scheduler.completed_jobs:
            job_state = self.job_scheduler.completed_jobs[job_id]
            return self._serialize_job_state(job_state)
        
        # Check queue
        for _, job_config in self.job_scheduler.job_queue:
            if job_config.job_id == job_id:
                return {
                    "job_id": job_id,
                    "status": "queued",
                    "position_in_queue": self._get_queue_position(job_id),
                    "estimated_start_time": self._estimate_start_time(job_config)
                }
        
        return None
    
    async def get_orchestration_status(self) -> Dict[str, Any]:
        """Get overall orchestration system status"""
        
        # Resource utilization
        resource_utilization = {}
        for pool_id, pool in self.resource_manager.resource_pools.items():
            utilization = pool.allocated_capacity / pool.total_capacity if pool.total_capacity > 0 else 0
            resource_utilization[pool_id] = {
                "utilization": utilization,
                "allocated": pool.allocated_capacity,
                "total": pool.total_capacity,
                "unit": pool.unit
            }
        
        # Worker health
        worker_health = self.worker_manager.get_worker_health()
        
        # Queue status
        queue_status = {
            "pending_jobs": len(self.job_scheduler.job_queue),
            "running_jobs": len(self.job_scheduler.running_jobs),
            "completed_jobs": len(self.job_scheduler.completed_jobs)
        }
        
        return {
            "orchestration_active": self.orchestration_active,
            "resource_utilization": resource_utilization,
            "worker_health": worker_health,
            "queue_status": queue_status,
            "orchestration_stats": self.orchestration_stats,
            "last_update": datetime.now().isoformat()
        }
    
    async def _orchestration_loop(self) -> None:
        """Main orchestration loop"""
        logger.info("🔄 Orchestration loop started")
        
        while self.orchestration_active:
            try:
                # Schedule next job
                job_config = await self.job_scheduler.schedule_next_job("creator_aware")
                
                if job_config:
                    # Allocate resources
                    allocation = await self.resource_manager.allocate_resources(
                        job_config, "creator_optimized"
                    )
                    
                    if allocation.get("success", False):
                        # Create job state
                        job_state = TrainingJobState(
                            job_id=job_config.job_id,
                            status=TrainingJobStatus.RUNNING,
                            start_time=datetime.now(),
                            total_epochs=job_config.training_config.get("epochs", 100),
                            assigned_resources=allocation["allocated_resources"]
                        )
                        
                        # Assign to worker
                        worker_id = await self.worker_manager.assign_job_to_worker(
                            job_config, job_state
                        )
                        
                        if worker_id:
                            # Start training job
                            self.job_scheduler.running_jobs[job_config.job_id] = job_state
                            
                            # Launch training task
                            asyncio.create_task(
                                self._execute_training_job(job_config, job_state)
                            )
                            
                            logger.info(f"🚀 Started training job {job_config.job_id}")
                        else:
                            # Deallocate resources if no worker available
                            await self.resource_manager.deallocate_resources(
                                job_config.job_id, allocation["allocated_resources"]
                            )
                            # Re-queue job
                            self.job_scheduler.submit_job(job_config)
                    else:
                        # Re-queue job if resources not available
                        self.job_scheduler.submit_job(job_config)
                        logger.debug(f"Resources not available for job {job_config.job_id}, re-queued")
                
                # Monitoring and cleanup
                await self._monitor_running_jobs()
                await self._cleanup_completed_jobs()
                
                # Brief pause before next iteration
                await asyncio.sleep(5.0)
                
            except Exception as e:
                logger.error(f"Error in orchestration loop: {e}")
                await asyncio.sleep(10.0)
    
    async def _execute_training_job(self, job_config: TrainingJobConfig, 
                                  job_state: TrainingJobState) -> None:
        """Execute training job (simplified simulation)"""
        try:
            logger.info(f"🎯 Executing training job {job_config.job_id}")
            
            # Simulate training progress
            total_epochs = job_state.total_epochs
            
            for epoch in range(total_epochs):
                if job_state.status != TrainingJobStatus.RUNNING:
                    break
                
                # Simulate epoch training
                await asyncio.sleep(2.0)  # Simulated epoch time
                
                # Update progress
                job_state.current_epoch = epoch + 1
                job_state.progress_percentage = (epoch + 1) / total_epochs * 100
                
                # Simulate loss improvement
                current_loss = 1.0 * np.exp(-epoch * 0.1) + np.random.normal(0, 0.01)
                job_state.current_loss = max(0.01, current_loss)
                job_state.best_loss = min(job_state.best_loss, job_state.current_loss)
                
                # Update metrics
                job_state.metrics.update({
                    "epoch": epoch + 1,
                    "loss": job_state.current_loss,
                    "best_loss": job_state.best_loss,
                    "progress": job_state.progress_percentage
                })
                
                # Creator-specific metrics
                if job_config.creator_type == CreatorType.MUSICIAN:
                    job_state.metrics["audio_quality_score"] = 0.9 + epoch * 0.01
                elif job_config.creator_type == CreatorType.PHOTOGRAPHER:
                    job_state.metrics["image_aesthetic_score"] = 0.85 + epoch * 0.015
                
                logger.debug(f"Job {job_config.job_id} epoch {epoch + 1}/{total_epochs}, loss: {current_loss:.4f}")
            
            # Complete job
            job_state.status = TrainingJobStatus.COMPLETED
            job_state.end_time = datetime.now()
            job_state.progress_percentage = 100.0
            
            # Update statistics
            self.orchestration_stats["jobs_completed"] += 1
            duration_hours = (job_state.end_time - job_state.start_time).total_seconds() / 3600
            self.orchestration_stats["total_training_hours"] += duration_hours
            
            logger.info(f"✅ Training job {job_config.job_id} completed successfully")
            
        except Exception as e:
            job_state.status = TrainingJobStatus.FAILED
            job_state.end_time = datetime.now()
            job_state.error_message = str(e)
            
            self.orchestration_stats["jobs_failed"] += 1
            
            logger.error(f"❌ Training job {job_config.job_id} failed: {e}")
    
    async def _monitor_running_jobs(self) -> None:
        """Monitor running jobs for health and progress"""
        current_time = datetime.now()
        
        for job_id, job_state in list(self.job_scheduler.running_jobs.items()):
            # Check for timeout
            if job_state.start_time:
                runtime_hours = (current_time - job_state.start_time).total_seconds() / 3600
                
                # Get job config to check timeout
                job_config = None
                for _, config in self.job_scheduler.job_queue:
                    if config.job_id == job_id:
                        job_config = config
                        break
                
                if job_config and runtime_hours > job_config.timeout_hours:
                    logger.warning(f"⏰ Job {job_id} timed out after {runtime_hours:.2f} hours")
                    job_state.status = TrainingJobStatus.FAILED
                    job_state.error_message = "Job timeout"
                    job_state.end_time = current_time
    
    async def _cleanup_completed_jobs(self) -> None:
        """Clean up completed and failed jobs"""
        for job_id, job_state in list(self.job_scheduler.running_jobs.items()):
            if job_state.status in [TrainingJobStatus.COMPLETED, TrainingJobStatus.FAILED, TrainingJobStatus.CANCELLED]:
                # Deallocate resources
                if job_state.assigned_resources:
                    await self.resource_manager.deallocate_resources(
                        job_id, job_state.assigned_resources
                    )
                
                # Update worker
                if job_state.worker_id and job_state.worker_id in self.worker_manager.workers:
                    worker = self.worker_manager.workers[job_state.worker_id]
                    if job_id in worker.current_jobs:
                        worker.current_jobs.remove(job_id)
                        worker.status = "available" if len(worker.current_jobs) < worker.max_concurrent_jobs else "busy"
                
                # Move to completed jobs
                self.job_scheduler.completed_jobs[job_id] = job_state
                del self.job_scheduler.running_jobs[job_id]
    
    async def _register_default_workers(self) -> None:
        """Register default training workers"""
        default_workers = [
            {
                "worker_id": "gpu_worker_1",
                "worker_type": "gpu_trainer",
                "resource_capacity": {"gpu": 2.0, "memory": 32.0, "cpu": 8.0},
                "max_concurrent_jobs": 2,
                "creator_specialization": "musician"
            },
            {
                "worker_id": "gpu_worker_2",
                "worker_type": "gpu_trainer",
                "resource_capacity": {"gpu": 4.0, "memory": 64.0, "cpu": 16.0},
                "max_concurrent_jobs": 1,
                "creator_specialization": "photographer"
            },
            {
                "worker_id": "cpu_worker_1",
                "worker_type": "cpu_trainer",
                "resource_capacity": {"cpu": 16.0, "memory": 64.0},
                "max_concurrent_jobs": 4,
                "creator_specialization": "blogger"
            }
        ]
        
        for worker_config in default_workers:
            self.worker_manager.register_worker(worker_config)
    
    async def _validate_job_config(self, job_config: TrainingJobConfig) -> Dict[str, Any]:
        """Validate training job configuration"""
        errors = []
        
        # Required fields
        if not job_config.job_id:
            errors.append("job_id is required")
        
        if not job_config.resource_requirements:
            errors.append("resource_requirements is required")
        
        # Resource requirements validation
        for req in job_config.resource_requirements:
            if req.amount <= 0:
                errors.append(f"Invalid resource amount for {req.resource_type.value}")
        
        # Dependencies validation
        for dep_id in job_config.dependencies:
            if dep_id == job_config.job_id:
                errors.append("Job cannot depend on itself")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }
    
    def _serialize_job_state(self, job_state: TrainingJobState) -> Dict[str, Any]:
        """Serialize job state to dictionary"""
        return {
            "job_id": job_state.job_id,
            "status": job_state.status.value,
            "start_time": job_state.start_time.isoformat() if job_state.start_time else None,
            "end_time": job_state.end_time.isoformat() if job_state.end_time else None,
            "progress_percentage": job_state.progress_percentage,
            "current_epoch": job_state.current_epoch,
            "total_epochs": job_state.total_epochs,
            "current_loss": job_state.current_loss,
            "best_loss": job_state.best_loss,
            "metrics": job_state.metrics,
            "error_message": job_state.error_message,
            "retry_count": job_state.retry_count,
            "worker_id": job_state.worker_id
        }
    
    def _get_queue_position(self, job_id: str) -> int:
        """Get position of job in queue"""
        for i, (_, job_config) in enumerate(self.job_scheduler.job_queue):
            if job_config.job_id == job_id:
                return i + 1
        return -1
    
    def _estimate_start_time(self, job_config: TrainingJobConfig) -> Optional[str]:
        """Estimate job start time based on queue and resource availability"""
        # Simplified estimation - would be more complex in practice
        position = self._get_queue_position(job_config.job_id)
        if position > 0:
            estimated_minutes = position * 30  # Assume 30 minutes per job average
            estimated_start = datetime.now() + timedelta(minutes=estimated_minutes)
            return estimated_start.isoformat()
        return None
    
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load orchestration configuration"""
        default_config = {
            "max_concurrent_jobs": 10,
            "job_timeout_hours": 24.0,
            "resource_allocation_strategy": "creator_optimized",
            "scheduling_strategy": "creator_aware",
            "monitoring_interval_seconds": 30,
            "cleanup_interval_seconds": 60
        }
        
        if config_path and Path(config_path).exists():
            with open(config_path, 'r') as f:
                custom_config = yaml.safe_load(f)
            default_config.update(custom_config)
        
        return default_config

# Example usage and testing
if __name__ == "__main__":
    async def test_training_orchestration():
        """Test training orchestration engine"""
        
        # Initialize orchestration engine
        orchestrator = TrainingOrchestrationEngine()
        
        # Start orchestration
        await orchestrator.start_orchestration()
        
        # Create test training jobs
        jobs = []
        
        for i in range(3):
            job_config = TrainingJobConfig(
                job_id=f"training_job_{i}",
                job_name=f"Model Training {i}",
                model_config={"architecture": "transformer", "layers": 12},
                dataset_config={"dataset": "creator_content", "size": "1M"},
                training_config={"epochs": 50, "batch_size": 32, "learning_rate": 0.001},
                resource_requirements=[
                    ResourceRequirement(ResourceType.GPU, 2.0, "cards"),
                    ResourceRequirement(ResourceType.MEMORY, 16.0, "GB"),
                    ResourceRequirement(ResourceType.CPU, 4.0, "cores")
                ],
                priority=JobPriority.HIGH if i == 0 else JobPriority.MEDIUM,
                creator_type=CreatorType.MUSICIAN if i % 2 == 0 else CreatorType.PHOTOGRAPHER,
                estimated_duration_hours=2.0,
                dependencies=[] if i == 0 else [f"training_job_{i-1}"]
            )
            jobs.append(job_config)
        
        # Submit jobs
        for job_config in jobs:
            job_id = await orchestrator.submit_training_job(job_config)
            print(f"📤 Submitted job: {job_id}")
        
        # Monitor progress
        print("\n🔍 Monitoring training progress...")
        
        for _ in range(20):  # Monitor for 20 iterations
            status = await orchestrator.get_orchestration_status()
            
            print(f"\n📊 Orchestration Status:")
            print(f"   Active: {status['orchestration_active']}")
            print(f"   Pending Jobs: {status['queue_status']['pending_jobs']}")
            print(f"   Running Jobs: {status['queue_status']['running_jobs']}")
            print(f"   Completed Jobs: {status['queue_status']['completed_jobs']}")
            print(f"   Jobs Submitted: {status['orchestration_stats']['jobs_submitted']}")
            print(f"   Jobs Completed: {status['orchestration_stats']['jobs_completed']}")
            
            # Check individual job status
            for job_config in jobs:
                job_status = await orchestrator.get_job_status(job_config.job_id)
                if job_status:
                    print(f"   Job {job_config.job_id}: {job_status['status']}")
                    if "progress_percentage" in job_status:
                        print(f"      Progress: {job_status['progress_percentage']:.1f}%")
            
            await asyncio.sleep(5.0)
            
            # Break if all jobs completed
            if status['queue_status']['completed_jobs'] >= len(jobs):
                break
        
        print("\n✅ Training orchestration test completed")
        
        # Stop orchestration
        await orchestrator.stop_orchestration()
    
    # Run test
    asyncio.run(test_training_orchestration())