"""AI Processing Scheduler
======================

Enterprise-grade scheduling system for AI processing tasks with
intelligent prioritization, resource management, and optimization.

Features:
- Priority-based task scheduling
- Resource-aware task distribution
- Deadline management and SLA compliance
- Dynamic load balancing
- Performance optimization

Author: Fahed Mlaiel <mlaiel@live.de>
"""
import asyncio
import logging
import time
import uuid
from collections import defaultdict, deque
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Callable, Set
import heapq
import json

import numpy as np
from prometheus_client import Counter, Histogram, Gauge
import redis.asyncio as aioredis

from .core import ProcessingTask, ProcessingStatus, AIModelType

# Metrics
scheduler_tasks_queued = Counter('scheduler_tasks_queued_total', 'Total tasks queued')
scheduler_tasks_scheduled = Counter('scheduler_tasks_scheduled_total', 'Total tasks scheduled')
scheduler_queue_wait_time = Histogram('scheduler_queue_wait_time_seconds', 'Task queue wait time')
scheduler_queue_size = Gauge('scheduler_queue_size', 'Current queue size')
scheduler_active_jobs = Gauge('scheduler_active_jobs', 'Active scheduled jobs')

logger = logging.getLogger(__name__)


class SchedulingStrategy(Enum):
    """Task scheduling strategies."""    FIFO = "first_in_first_out"
    PRIORITY = "priority_based"
    SJF = "shortest_job_first"
    ROUND_ROBIN = "round_robin"
    DEADLINE_AWARE = "deadline_aware"
    RESOURCE_OPTIMIZED = "resource_optimized"


class TaskPriority(Enum):
    """Task priority levels."""    CRITICAL = 1
    HIGH = 2
    NORMAL = 3
    LOW = 4
    BACKGROUND = 5


class ResourceRequirement(Enum):
    """Resource requirement types."""    CPU_INTENSIVE = "cpu_intensive"
    GPU_INTENSIVE = "gpu_intensive"
    MEMORY_INTENSIVE = "memory_intensive"
    IO_INTENSIVE = "io_intensive"
    BALANCED = "balanced"


@dataclass
class SchedulingConfig:
    """Scheduler configuration parameters."""    strategy: SchedulingStrategy = SchedulingStrategy.PRIORITY
    max_concurrent_tasks: int = 50
    max_queue_size: int = 1000
    default_timeout: int = 300
    enable_deadline_enforcement: bool = True
    enable_resource_optimization: bool = True
    enable_load_balancing: bool = True
    priority_aging_factor: float = 0.1
    queue_cleanup_interval: int = 300


@dataclass
class ScheduledTask:
    """Scheduled task with metadata."""    task: ProcessingTask
    priority: TaskPriority
    resource_requirement: ResourceRequirement
    deadline: Optional[datetime] = None
    estimated_duration: float = 60.0
    retry_count: int = 0
    max_retries: int = 3
    scheduled_at: datetime = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.scheduled_at is None:
            self.scheduled_at = datetime.utcnow()


@dataclass
class ResourcePool:
    """Resource pool for task execution."""    pool_id: str
    resource_type: ResourceRequirement
    capacity: int
    available: int
    active_tasks: Set[str]
    last_updated: datetime
    
    def __post_init__(self):
        if self.last_updated is None:
            self.last_updated = datetime.utcnow()


class AIProcessingScheduler:
    """    Enterprise AI Processing Scheduler
    
    Manages scheduling and execution of AI processing tasks with
    intelligent prioritization, resource optimization, and SLA compliance.
    """    
    def __init__(self, config: SchedulingConfig):
        """Initialize AI processing scheduler."""        self.config = config
        self.task_queue = []  # Priority queue (heapq)
        self.active_tasks: Dict[str, ScheduledTask] = {}
        self.completed_tasks = deque(maxlen=10000)
        self.failed_tasks = deque(maxlen=1000)
        
        # Resource management
        self.resource_pools: Dict[str, ResourcePool] = {}
        self.resource_allocation: Dict[str, str] = {}  # task_id -> pool_id
        
        # Scheduling statistics
        self.scheduling_stats = defaultdict(int)
        self.performance_metrics = defaultdict(list)
        
        # External connections
        self.redis_client: Optional[aioredis.Redis] = None
        
        # Background tasks
        self._scheduler_task: Optional[asyncio.Task] = None
        self._cleanup_task: Optional[asyncio.Task] = None
        self._metrics_task: Optional[asyncio.Task] = None
        
        self._initialize_scheduler()
    
    async def _initialize_scheduler(self):
        """Initialize scheduler components."""        try:
            # Initialize Redis for persistence
            self.redis_client = aioredis.from_url(
                "redis://localhost:6379",
                decode_responses=True,
                health_check_interval=30
            )
            
            # Initialize resource pools
            await self._initialize_resource_pools()
            
            # Start background tasks
            self._scheduler_task = asyncio.create_task(self._scheduler_loop())
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())
            self._metrics_task = asyncio.create_task(self._metrics_loop())
            
            logger.info("AI processing scheduler initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize scheduler: {e}")
            raise
    
    async def _initialize_resource_pools(self):
        """Initialize resource pools for different task types."""        try:
            # CPU-intensive tasks pool
            self.resource_pools['cpu_pool'] = ResourcePool(
                pool_id='cpu_pool',
                resource_type=ResourceRequirement.CPU_INTENSIVE,
                capacity=20,
                available=20,
                active_tasks=set(),
                last_updated=datetime.utcnow()
            )
            
            # GPU-intensive tasks pool
            self.resource_pools['gpu_pool'] = ResourcePool(
                pool_id='gpu_pool',
                resource_type=ResourceRequirement.GPU_INTENSIVE,
                capacity=10,
                available=10,
                active_tasks=set(),
                last_updated=datetime.utcnow()
            )
            
            # Memory-intensive tasks pool
            self.resource_pools['memory_pool'] = ResourcePool(
                pool_id='memory_pool',
                resource_type=ResourceRequirement.MEMORY_INTENSIVE,
                capacity=15,
                available=15,
                active_tasks=set(),
                last_updated=datetime.utcnow()
            )
            
            # I/O-intensive tasks pool
            self.resource_pools['io_pool'] = ResourcePool(
                pool_id='io_pool',
                resource_type=ResourceRequirement.IO_INTENSIVE,
                capacity=30,
                available=30,
                active_tasks=set(),
                last_updated=datetime.utcnow()
            )
            
            # Balanced tasks pool
            self.resource_pools['balanced_pool'] = ResourcePool(
                pool_id='balanced_pool',
                resource_type=ResourceRequirement.BALANCED,
                capacity=25,
                available=25,
                active_tasks=set(),
                last_updated=datetime.utcnow()
            )
            
            logger.info(f"Initialized {len(self.resource_pools)} resource pools")
            
        except Exception as e:
            logger.error(f"Failed to initialize resource pools: {e}")
            raise
    
    async def schedule_task(
        self,
        task: ProcessingTask,
        priority: TaskPriority = TaskPriority.NORMAL,
        deadline: Optional[datetime] = None,
        estimated_duration: float = 60.0
    ) -> str:
        """        Schedule a processing task for execution.
        
        Args:
            task: Processing task to schedule
            priority: Task priority level
            deadline: Optional deadline for completion
            estimated_duration: Estimated execution time in seconds
            
        Returns:
            str: Scheduled task ID
        """        try:
            scheduler_tasks_queued.inc()
            
            # Validate queue capacity
            if len(self.task_queue) >= self.config.max_queue_size:
                raise RuntimeError("Task queue is full")
            
            # Determine resource requirement
            resource_requirement = self._determine_resource_requirement(task)
            
            # Create scheduled task
            scheduled_task = ScheduledTask(
                task=task,
                priority=priority,
                resource_requirement=resource_requirement,
                deadline=deadline,
                estimated_duration=estimated_duration
            )
            
            # Calculate priority score for heap
            priority_score = self._calculate_priority_score(scheduled_task)
            
            # Add to priority queue
            heapq.heappush(self.task_queue, (priority_score, time.time(), scheduled_task))
            scheduler_queue_size.set(len(self.task_queue))
            
            # Store in Redis for persistence
            if self.redis_client:
                task_data = {
                    'task_id': task.task_id,
                    'tenant_id': task.tenant_id,
                    'content_type': task.content_type,
                    'model_type': task.model_type.value,
                    'priority': priority.value,
                    'resource_requirement': resource_requirement.value,
                    'estimated_duration': estimated_duration,
                    'scheduled_at': scheduled_task.scheduled_at.isoformat(),
                    'deadline': deadline.isoformat() if deadline else None
                }
                await self.redis_client.hset(f"scheduled_task:{task.task_id}", mapping=task_data)
                await self.redis_client.expire(f"scheduled_task:{task.task_id}", 3600)
            
            self.scheduling_stats['tasks_queued'] += 1
            logger.info(f"Task {task.task_id} scheduled with priority {priority.name}")
            
            return task.task_id
            
        except Exception as e:
            logger.error(f"Failed to schedule task {task.task_id}: {e}")
            raise
    
    def _determine_resource_requirement(self, task: ProcessingTask) -> ResourceRequirement:
        """Determine resource requirement based on task characteristics."""        model_type = task.model_type
        content_type = task.content_type
        
        # GPU-intensive tasks
        if model_type in [AIModelType.VIDEO_FINGERPRINT, AIModelType.IMAGE_FINGERPRINT]:
            return ResourceRequirement.GPU_INTENSIVE
        
        # CPU-intensive tasks
        if model_type == AIModelType.AUDIO_FINGERPRINT:
            return ResourceRequirement.CPU_INTENSIVE
        
        # Memory-intensive tasks
        if content_type == 'video' or model_type == AIModelType.CONTENT_ANALYZER:
            return ResourceRequirement.MEMORY_INTENSIVE
        
        # I/O-intensive tasks
        if model_type == AIModelType.SIMILARITY_MATCHER:
            return ResourceRequirement.IO_INTENSIVE
        
        # Default to balanced
        return ResourceRequirement.BALANCED
    
    def _calculate_priority_score(self, scheduled_task: ScheduledTask) -> float:
        """Calculate priority score for heap ordering (lower = higher priority)."""        base_score = scheduled_task.priority.value
        
        # Age factor (older tasks get higher priority)
        age_hours = (datetime.utcnow() - scheduled_task.scheduled_at).total_seconds() / 3600
        age_bonus = age_hours * self.config.priority_aging_factor
        
        # Deadline factor
        deadline_penalty = 0.0
        if scheduled_task.deadline:
            time_to_deadline = (scheduled_task.deadline - datetime.utcnow()).total_seconds()
            if time_to_deadline < scheduled_task.estimated_duration * 2:
                deadline_penalty = -2.0  # High priority for near-deadline tasks
            elif time_to_deadline < 0:
                deadline_penalty = -5.0  # Highest priority for overdue tasks
        
        # Resource availability factor
        resource_factor = self._get_resource_availability_factor(scheduled_task.resource_requirement)
        
        final_score = base_score - age_bonus + deadline_penalty + resource_factor
        return max(0.1, final_score)  # Ensure positive score
    
    def _get_resource_availability_factor(self, resource_requirement: ResourceRequirement) -> float:
        """Get resource availability factor for priority calculation."""        pool_id = self._get_pool_for_resource(resource_requirement)
        pool = self.resource_pools.get(pool_id)
        
        if not pool or pool.capacity == 0:
            return 2.0  # High penalty if no resources
        
        availability_ratio = pool.available / pool.capacity
        return (1.0 - availability_ratio) * 0.5  # Lower penalty for more available resources
    
    def _get_pool_for_resource(self, resource_requirement: ResourceRequirement) -> str:
        """Get resource pool ID for requirement type."""        pool_mapping = {
            ResourceRequirement.CPU_INTENSIVE: 'cpu_pool',
            ResourceRequirement.GPU_INTENSIVE: 'gpu_pool',
            ResourceRequirement.MEMORY_INTENSIVE: 'memory_pool',
            ResourceRequirement.IO_INTENSIVE: 'io_pool',
            ResourceRequirement.BALANCED: 'balanced_pool'
        }
        return pool_mapping.get(resource_requirement, 'balanced_pool')
    
    async def _scheduler_loop(self):
        """Main scheduler loop for task execution."""        while True:
            try:
                # Process pending tasks
                await self._process_pending_tasks()
                
                # Check active tasks for completion
                await self._check_active_tasks()
                
                # Update resource pools
                await self._update_resource_pools()
                
                # Wait before next iteration
                await asyncio.sleep(1.0)
                
            except Exception as e:
                logger.error(f"Error in scheduler loop: {e}")
                await asyncio.sleep(5.0)
    
    async def _process_pending_tasks(self):
        """Process pending tasks from the queue."""        try:
            while (self.task_queue and 
                   len(self.active_tasks) < self.config.max_concurrent_tasks):
                
                # Get highest priority task
                priority_score, queued_time, scheduled_task = heapq.heappop(self.task_queue)
                scheduler_queue_size.set(len(self.task_queue))
                
                # Check if task can be allocated resources
                if await self._allocate_resources(scheduled_task):
                    # Start task execution
                    await self._start_task_execution(scheduled_task)
                    
                    # Record queue wait time
                    wait_time = time.time() - queued_time
                    scheduler_queue_wait_time.observe(wait_time)
                    
                    scheduler_tasks_scheduled.inc()
                    self.scheduling_stats['tasks_scheduled'] += 1
                else:
                    # Put task back in queue if no resources available
                    heapq.heappush(self.task_queue, (priority_score, queued_time, scheduled_task))
                    break  # Stop processing until resources are available
            
        except Exception as e:
            logger.error(f"Error processing pending tasks: {e}")
    
    async def _allocate_resources(self, scheduled_task: ScheduledTask) -> bool:
        """Allocate resources for task execution."""        try:
            pool_id = self._get_pool_for_resource(scheduled_task.resource_requirement)
            pool = self.resource_pools.get(pool_id)
            
            if not pool or pool.available <= 0:
                return False
            
            # Allocate resource
            pool.available -= 1
            pool.active_tasks.add(scheduled_task.task.task_id)
            pool.last_updated = datetime.utcnow()
            
            # Record allocation
            self.resource_allocation[scheduled_task.task.task_id] = pool_id
            
            logger.debug(f"Allocated {pool_id} resource to task {scheduled_task.task.task_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to allocate resources for task {scheduled_task.task.task_id}: {e}")
            return False
    
    async def _start_task_execution(self, scheduled_task: ScheduledTask):
        """Start execution of a scheduled task."""        try:
            task_id = scheduled_task.task.task_id
            
            # Update task status
            scheduled_task.started_at = datetime.utcnow()
            scheduled_task.task.status = ProcessingStatus.PROCESSING
            
            # Add to active tasks
            self.active_tasks[task_id] = scheduled_task
            scheduler_active_jobs.set(len(self.active_tasks))
            
            # Update in Redis
            if self.redis_client:
                await self.redis_client.hset(
                    f"scheduled_task:{task_id}",
                    "status",
                    "processing"
                )
                await self.redis_client.hset(
                    f"scheduled_task:{task_id}",
                    "started_at",
                    scheduled_task.started_at.isoformat()
                )
            
            logger.info(f"Started execution of task {task_id}")
            
        except Exception as e:
            logger.error(f"Failed to start task execution for {scheduled_task.task.task_id}: {e}")
    
    async def _check_active_tasks(self):
        """Check active tasks for completion or timeout."""        try:
            completed_tasks = []
            current_time = datetime.utcnow()
            
            for task_id, scheduled_task in self.active_tasks.items():
                # Check for timeout
                if (scheduled_task.started_at and 
                    (current_time - scheduled_task.started_at).total_seconds() > self.config.default_timeout):
                    
                    logger.warning(f"Task {task_id} timed out")
                    scheduled_task.task.status = ProcessingStatus.FAILED
                    scheduled_task.task.error = "Task execution timeout"
                    completed_tasks.append(task_id)
                    continue
                
                # Check for deadline violation
                if (self.config.enable_deadline_enforcement and 
                    scheduled_task.deadline and 
                    current_time > scheduled_task.deadline):
                    
                    logger.warning(f"Task {task_id} exceeded deadline")
                    scheduled_task.task.status = ProcessingStatus.FAILED
                    scheduled_task.task.error = "Deadline exceeded"
                    completed_tasks.append(task_id)
                    continue
                
                # Check if task is actually completed (this would be updated by the processing engine)
                if scheduled_task.task.status in [ProcessingStatus.COMPLETED, ProcessingStatus.FAILED]:
                    completed_tasks.append(task_id)
            
            # Remove completed tasks
            for task_id in completed_tasks:
                await self._complete_task(task_id)
            
        except Exception as e:
            logger.error(f"Error checking active tasks: {e}")
    
    async def _complete_task(self, task_id: str):
        """Complete and cleanup a task."""        try:
            scheduled_task = self.active_tasks.get(task_id)
            if not scheduled_task:
                return
            
            # Update completion time
            scheduled_task.completed_at = datetime.utcnow()
            
            # Release resources
            await self._release_resources(scheduled_task)
            
            # Move to appropriate completed list
            if scheduled_task.task.status == ProcessingStatus.COMPLETED:
                self.completed_tasks.append(scheduled_task)
                self.scheduling_stats['tasks_completed'] += 1
            else:
                self.failed_tasks.append(scheduled_task)
                self.scheduling_stats['tasks_failed'] += 1
                
                # Handle retry logic
                if (scheduled_task.retry_count < scheduled_task.max_retries and
                    scheduled_task.task.error != "Deadline exceeded"):
                    await self._retry_task(scheduled_task)
            
            # Remove from active tasks
            del self.active_tasks[task_id]
            scheduler_active_jobs.set(len(self.active_tasks))
            
            # Update Redis
            if self.redis_client:
                await self.redis_client.hset(
                    f"scheduled_task:{task_id}",
                    "completed_at",
                    scheduled_task.completed_at.isoformat()
                )
                await self.redis_client.hset(
                    f"scheduled_task:{task_id}",
                    "status",
                    scheduled_task.task.status.value
                )
            
            logger.info(f"Task {task_id} completed with status {scheduled_task.task.status.value}")
            
        except Exception as e:
            logger.error(f"Failed to complete task {task_id}: {e}")
    
    async def _release_resources(self, scheduled_task: ScheduledTask):
        """Release allocated resources for a task."""        try:
            task_id = scheduled_task.task.task_id
            pool_id = self.resource_allocation.get(task_id)
            
            if pool_id:
                pool = self.resource_pools.get(pool_id)
                if pool:
                    pool.available += 1
                    pool.active_tasks.discard(task_id)
                    pool.last_updated = datetime.utcnow()
                
                del self.resource_allocation[task_id]
                logger.debug(f"Released {pool_id} resource from task {task_id}")
            
        except Exception as e:
            logger.error(f"Failed to release resources for task {scheduled_task.task.task_id}: {e}")
    
    async def _retry_task(self, scheduled_task: ScheduledTask):
        """Retry a failed task."""        try:
            scheduled_task.retry_count += 1
            scheduled_task.task.status = ProcessingStatus.PENDING
            scheduled_task.task.error = None
            scheduled_task.started_at = None
            
            # Lower priority for retry
            retry_priority = TaskPriority.LOW if scheduled_task.priority != TaskPriority.BACKGROUND else TaskPriority.BACKGROUND
            
            # Re-schedule with retry priority
            await self.schedule_task(
                scheduled_task.task,
                priority=retry_priority,
                deadline=scheduled_task.deadline,
                estimated_duration=scheduled_task.estimated_duration
            )
            
            logger.info(f"Retrying task {scheduled_task.task.task_id} (attempt {scheduled_task.retry_count})")
            
        except Exception as e:
            logger.error(f"Failed to retry task {scheduled_task.task.task_id}: {e}")
    
    async def _update_resource_pools(self):
        """Update resource pool statistics and optimization."""        try:
            for pool_id, pool in self.resource_pools.items():
                # Calculate utilization
                utilization = (pool.capacity - pool.available) / pool.capacity if pool.capacity > 0 else 0
                
                # Store performance metrics
                self.performance_metrics[f"{pool_id}_utilization"].append(utilization)
                
                # Dynamic capacity adjustment (if enabled)
                if self.config.enable_resource_optimization:
                    await self._optimize_pool_capacity(pool)
            
        except Exception as e:
            logger.error(f"Error updating resource pools: {e}")
    
    async def _optimize_pool_capacity(self, pool: ResourcePool):
        """Optimize resource pool capacity based on usage patterns."""        try:
            utilization_key = f"{pool.pool_id}_utilization"
            recent_utilization = self.performance_metrics[utilization_key][-10:]  # Last 10 measurements
            
            if len(recent_utilization) >= 5:
                avg_utilization = np.mean(recent_utilization)
                
                # Scale up if consistently high utilization
                if avg_utilization > 0.9 and pool.capacity < 100:
                    new_capacity = min(pool.capacity + 5, 100)
                    additional_resources = new_capacity - pool.capacity
                    pool.capacity = new_capacity
                    pool.available += additional_resources
                    logger.info(f"Scaled up {pool.pool_id} capacity to {new_capacity}")
                
                # Scale down if consistently low utilization
                elif avg_utilization < 0.3 and pool.capacity > 5:
                    reduction = min(5, pool.available)  # Only reduce available resources
                    pool.capacity -= reduction
                    pool.available -= reduction
                    logger.info(f"Scaled down {pool.pool_id} capacity to {pool.capacity}")
            
        except Exception as e:
            logger.error(f"Failed to optimize pool capacity for {pool.pool_id}: {e}")
    
    async def _cleanup_loop(self):
        """Background cleanup task."""        while True:
            try:
                await asyncio.sleep(self.config.queue_cleanup_interval)
                
                # Clean old completed tasks
                cutoff_time = datetime.utcnow() - timedelta(hours=24)
                
                # Clean completed tasks
                while (self.completed_tasks and 
                       self.completed_tasks[0].completed_at and
                       self.completed_tasks[0].completed_at < cutoff_time):
                    self.completed_tasks.popleft()
                
                # Clean failed tasks
                while (self.failed_tasks and 
                       self.failed_tasks[0].completed_at and
                       self.failed_tasks[0].completed_at < cutoff_time):
                    self.failed_tasks.popleft()
                
                # Clean old performance metrics
                cutoff_timestamp = time.time() - 3600  # 1 hour
                for key in list(self.performance_metrics.keys()):
                    self.performance_metrics[key] = [
                        value for value in self.performance_metrics[key][-100:]  # Keep last 100 values
                    ]
                
                logger.debug("Completed scheduler cleanup")
                
            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}")
    
    async def _metrics_loop(self):
        """Background metrics collection task."""        while True:
            try:
                await asyncio.sleep(60)  # Update every minute
                
                # Update Prometheus metrics
                scheduler_queue_size.set(len(self.task_queue))
                scheduler_active_jobs.set(len(self.active_tasks))
                
                # Log statistics
                if self.scheduling_stats['tasks_queued'] > 0:
                    completion_rate = (self.scheduling_stats['tasks_completed'] / 
                                     self.scheduling_stats['tasks_queued']) * 100
                    logger.info(f"Scheduler stats - Queued: {self.scheduling_stats['tasks_queued']}, "
                               f"Completed: {self.scheduling_stats['tasks_completed']}, "
                               f"Rate: {completion_rate:.1f}%")
                
            except Exception as e:
                logger.error(f"Error in metrics loop: {e}")
    
    async def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a scheduled task."""        try:
            # Check active tasks
            if task_id in self.active_tasks:
                scheduled_task = self.active_tasks[task_id]
                return self._format_task_status(scheduled_task)
            
            # Check completed tasks
            for scheduled_task in self.completed_tasks:
                if scheduled_task.task.task_id == task_id:
                    return self._format_task_status(scheduled_task)
            
            # Check failed tasks
            for scheduled_task in self.failed_tasks:
                if scheduled_task.task.task_id == task_id:
                    return self._format_task_status(scheduled_task)
            
            # Check queue
            for _, _, scheduled_task in self.task_queue:
                if scheduled_task.task.task_id == task_id:
                    return self._format_task_status(scheduled_task)
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get task status for {task_id}: {e}")
            return None
    
    def _format_task_status(self, scheduled_task: ScheduledTask) -> Dict[str, Any]:
        """Format task status for response."""        return {
            'task_id': scheduled_task.task.task_id,
            'status': scheduled_task.task.status.value,
            'priority': scheduled_task.priority.name,
            'resource_requirement': scheduled_task.resource_requirement.value,
            'scheduled_at': scheduled_task.scheduled_at.isoformat(),
            'started_at': scheduled_task.started_at.isoformat() if scheduled_task.started_at else None,
            'completed_at': scheduled_task.completed_at.isoformat() if scheduled_task.completed_at else None,
            'deadline': scheduled_task.deadline.isoformat() if scheduled_task.deadline else None,
            'estimated_duration': scheduled_task.estimated_duration,
            'retry_count': scheduled_task.retry_count,
            'error': scheduled_task.task.error
        }
    
    async def get_scheduler_statistics(self) -> Dict[str, Any]:
        """Get comprehensive scheduler statistics."""        try:
            # Resource pool stats
            pool_stats = {}
            for pool_id, pool in self.resource_pools.items():
                utilization = (pool.capacity - pool.available) / pool.capacity if pool.capacity > 0 else 0
                pool_stats[pool_id] = {
                    'capacity': pool.capacity,
                    'available': pool.available,
                    'utilization': round(utilization * 100, 1),
                    'active_tasks': len(pool.active_tasks)
                }
            
            return {
                'queue_size': len(self.task_queue),
                'active_tasks': len(self.active_tasks),
                'completed_tasks': len(self.completed_tasks),
                'failed_tasks': len(self.failed_tasks),
                'scheduling_strategy': self.config.strategy.value,
                'max_concurrent_tasks': self.config.max_concurrent_tasks,
                'resource_pools': pool_stats,
                'statistics': dict(self.scheduling_stats),
                'configuration': {
                    'max_queue_size': self.config.max_queue_size,
                    'default_timeout': self.config.default_timeout,
                    'deadline_enforcement': self.config.enable_deadline_enforcement,
                    'resource_optimization': self.config.enable_resource_optimization,
                    'load_balancing': self.config.enable_load_balancing
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get scheduler statistics: {e}")
            return {}
    
    async def shutdown(self):
        """Gracefully shutdown scheduler."""        try:
            logger.info("Shutting down AI processing scheduler")
            
            # Cancel background tasks
            if self._scheduler_task:
                self._scheduler_task.cancel()
            if self._cleanup_task:
                self._cleanup_task.cancel()
            if self._metrics_task:
                self._metrics_task.cancel()
            
            # Wait for active tasks to complete (with timeout)
            if self.active_tasks:
                logger.info(f"Waiting for {len(self.active_tasks)} active tasks to complete")
                timeout = 60  # 1 minute timeout
                start_time = time.time()
                
                while self.active_tasks and (time.time() - start_time) < timeout:
                    await asyncio.sleep(1)
                
                if self.active_tasks:
                    logger.warning(f"{len(self.active_tasks)} tasks did not complete within timeout")
            
            # Close Redis connection
            if self.redis_client:
                await self.redis_client.close()
            
            logger.info("Scheduler shutdown completed")
            
        except Exception as e:
            logger.error(f"Error during scheduler shutdown: {e}")


# Factory functions
def create_scheduler(strategy: str = "priority") -> AIProcessingScheduler:
    """Create scheduler with specified strategy."""    config = SchedulingConfig(
        strategy=SchedulingStrategy(strategy.lower()),
        max_concurrent_tasks=50,
        max_queue_size=1000
    )
    return AIProcessingScheduler(config)


def create_high_performance_scheduler() -> AIProcessingScheduler:
    """Create high-performance scheduler configuration."""    config = SchedulingConfig(
        strategy=SchedulingStrategy.RESOURCE_OPTIMIZED,
        max_concurrent_tasks=100,
        max_queue_size=2000,
        enable_deadline_enforcement=True,
        enable_resource_optimization=True,
        enable_load_balancing=True,
        priority_aging_factor=0.2
    )
    return AIProcessingScheduler(config)
