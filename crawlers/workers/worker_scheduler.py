"""
Worker Scheduler - IA-Influencer-Agent
================================================================================
Module: backend/crawlers/workers/worker_scheduler.py
Author: Fahed Mlaiel (mlaiel@live.de)
Type: Industrial Worker Scheduler - Intelligent Task Orchestration
Responsibility: Advanced task scheduling and worker coordination
Technologies: Priority Scheduling, Resource Allocation, Dependency Management
================================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
© 2025 Fahed Mlaiel. Tous droits réservés.
Usage non autorisé strictement interdit et passible de poursuites judiciaires.
Contact: mlaiel@live.de

LOGIQUE MÉTIER:
Task analysis → Dependency resolution → Resource calculation → 
Priority assignment → Worker selection → Execution scheduling → Monitoring
"""

from typing import Any, Dict, List, Optional, Union, Callable, Set, Tuple
import logging
import asyncio
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import uuid
import json
import time
from collections import defaultdict, deque
import heapq
import statistics
from contextlib import asynccontextmanager

from .crawler_worker import CrawlerTask, WorkerType
from ...core.managers.queue_manager import TaskPriority
from ...ai.ml.prediction_engine import PredictionEngine
from ...utils.time_utils import TimeUtils
from ...monitoring.performance_monitor import PerformanceMonitor

logger = logging.getLogger(__name__)


class SchedulingStrategy(Enum):
    """Task scheduling strategies"""
    FIFO = "fifo"
    LIFO = "lifo"
    PRIORITY = "priority"
    SHORTEST_JOB_FIRST = "shortest_job_first"
    ROUND_ROBIN = "round_robin"
    FAIR_SHARE = "fair_share"
    INTELLIGENT = "intelligent"


class ResourceType(Enum):
    """Resource types for scheduling"""
    CPU = "cpu"
    MEMORY = "memory"
    NETWORK = "network"
    STORAGE = "storage"
    GPU = "gpu"


@dataclass
class TaskDependency:
    """Task dependency definition"""
    task_id: str
    dependent_task_id: str
    dependency_type: str = "completion"  # completion, data, resource
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ResourceRequirement:
    """Resource requirement for tasks"""
    cpu_cores: float = 1.0
    memory_mb: int = 256
    network_mbps: float = 10.0
    storage_mb: int = 100
    gpu_required: bool = False
    estimated_duration: Optional[float] = None


@dataclass
class SchedulingConstraint:
    """Scheduling constraint definition"""
    constraint_type: str  # time_window, resource_limit, dependency, affinity
    constraint_data: Dict[str, Any]
    priority: int = 1
    is_hard: bool = True  # Hard vs soft constraint


@dataclass
class ScheduledTask:
    """Scheduled task with metadata"""
    task: CrawlerTask
    scheduled_time: datetime
    estimated_completion: datetime
    assigned_worker: Optional[str] = None
    resource_allocation: Optional[ResourceRequirement] = None
    dependencies: List[str] = field(default_factory=list)
    constraints: List[SchedulingConstraint] = field(default_factory=list)
    retry_count: int = 0
    scheduling_metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkerCapacity:
    """Worker capacity information"""
    worker_id: str
    worker_type: WorkerType
    max_cpu: float = 4.0
    max_memory: int = 2048
    max_network: float = 100.0
    max_concurrent_tasks: int = 5
    current_cpu: float = 0.0
    current_memory: int = 0
    current_network: float = 0.0
    current_tasks: int = 0
    efficiency_score: float = 1.0
    specializations: List[str] = field(default_factory=list)


class WorkerScheduler:
    """
    Intelligent worker scheduler for optimal task distribution
    
    Features:
    - Multi-strategy scheduling
    - Resource-aware allocation
    - Dependency resolution
    - Constraint satisfaction
    - Performance prediction
    - Load balancing optimization
    """

    def __init__(self, worker_pool):
        self.worker_pool = worker_pool
        self.strategy = SchedulingStrategy.INTELLIGENT
        
        # Scheduling queues
        self.priority_queue: List[Tuple[int, float, ScheduledTask]] = []
        self.dependency_graph: Dict[str, List[str]] = defaultdict(list)
        self.completed_tasks: Set[str] = set()
        self.scheduled_tasks: Dict[str, ScheduledTask] = {}
        self.pending_dependencies: Dict[str, Set[str]] = defaultdict(set)
        
        # Worker management
        self.worker_capacities: Dict[str, WorkerCapacity] = {}
        self.worker_schedules: Dict[str, List[ScheduledTask]] = defaultdict(list)
        self.worker_performance: Dict[str, Dict[str, List[float]]] = defaultdict(lambda: defaultdict(list))
        
        # Components
        self.prediction_engine = PredictionEngine()
        self.time_utils = TimeUtils()
        self.performance_monitor = PerformanceMonitor()
        
        # Scheduling metrics
        self.scheduling_stats = {
            'total_scheduled': 0,
            'successful_schedules': 0,
            'failed_schedules': 0,
            'average_wait_time': 0.0,
            'average_execution_time': 0.0,
            'resource_utilization': 0.0
        }
        
        # Background tasks
        self.background_tasks: Set[asyncio.Task] = set()
        self.shutdown_event = asyncio.Event()
        
        # Constraint solver
        self.constraint_weights = {
            'resource_limit': 1.0,
            'time_window': 0.8,
            'dependency': 1.0,
            'affinity': 0.6
        }

    async def initialize(self) -> None:
        """Initialize the scheduler"""
        try:
            logger.info("🚀 Initializing worker scheduler")
            
            # Initialize prediction engine
            await self.prediction_engine.initialize()
            
            # Start background tasks
            await self._start_background_tasks()
            
            logger.info("✅ Worker scheduler initialized")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize scheduler: {e}")
            raise

    async def shutdown(self) -> None:
        """Gracefully shutdown the scheduler"""
        try:
            logger.info("🛑 Shutting down worker scheduler")
            
            self.shutdown_event.set()
            
            # Cancel background tasks
            for task in self.background_tasks:
                if not task.done():
                    task.cancel()
            
            if self.background_tasks:
                await asyncio.gather(*self.background_tasks, return_exceptions=True)
            
            logger.info("✅ Worker scheduler shutdown complete")
            
        except Exception as e:
            logger.error(f"❌ Error during scheduler shutdown: {e}")

    async def schedule_task(
        self, 
        task: CrawlerTask,
        dependencies: Optional[List[str]] = None,
        constraints: Optional[List[SchedulingConstraint]] = None,
        resource_requirements: Optional[ResourceRequirement] = None
    ) -> bool:
        """Schedule a task for execution"""
        try:
            # Estimate resource requirements if not provided
            if resource_requirements is None:
                resource_requirements = await self._estimate_resource_requirements(task)
            
            # Calculate scheduling time
            scheduled_time = await self._calculate_optimal_schedule_time(
                task, resource_requirements, constraints or []
            )
            
            # Estimate completion time
            estimated_duration = resource_requirements.estimated_duration or await self._estimate_task_duration(task)
            estimated_completion = scheduled_time + timedelta(seconds=estimated_duration)
            
            # Create scheduled task
            scheduled_task = ScheduledTask(
                task=task,
                scheduled_time=scheduled_time,
                estimated_completion=estimated_completion,
                resource_allocation=resource_requirements,
                dependencies=dependencies or [],
                constraints=constraints or [],
                scheduling_metadata={
                    'scheduler_version': '1.0',
                    'scheduling_strategy': self.strategy.value,
                    'created_at': datetime.utcnow().isoformat()
                }
            )
            
            # Add dependencies to graph
            if dependencies:
                for dep_task_id in dependencies:
                    self.dependency_graph[dep_task_id].append(task.task_id)
                    self.pending_dependencies[task.task_id].add(dep_task_id)
            
            # Add to scheduling queue
            priority_value = self._calculate_scheduling_priority(scheduled_task)
            heapq.heappush(
                self.priority_queue, 
                (priority_value, time.time(), scheduled_task)
            )
            
            self.scheduled_tasks[task.task_id] = scheduled_task
            self.scheduling_stats['total_scheduled'] += 1
            
            logger.info(f"📅 Task scheduled: {task.task_id} for {scheduled_time.isoformat()}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to schedule task {task.task_id}: {e}")
            self.scheduling_stats['failed_schedules'] += 1
            return False

    async def update_worker_capacity(self, worker_id: str, capacity: WorkerCapacity) -> None:
        """Update worker capacity information"""
        try:
            self.worker_capacities[worker_id] = capacity
            
            # Update worker performance history
            if worker_id not in self.worker_performance:
                self.worker_performance[worker_id] = defaultdict(list)
            
            self.worker_performance[worker_id]['cpu_usage'].append(capacity.current_cpu)
            self.worker_performance[worker_id]['memory_usage'].append(capacity.current_memory)
            self.worker_performance[worker_id]['efficiency'].append(capacity.efficiency_score)
            
            # Keep only recent data
            for metric_list in self.worker_performance[worker_id].values():
                if len(metric_list) > 100:
                    metric_list.pop(0)
            
        except Exception as e:
            logger.error(f"❌ Failed to update worker capacity {worker_id}: {e}")

    async def get_next_scheduled_task(self, worker_id: str) -> Optional[ScheduledTask]:
        """Get the next task scheduled for a specific worker"""
        try:
            # Check if worker has capacity
            capacity = self.worker_capacities.get(worker_id)
            if not capacity or capacity.current_tasks >= capacity.max_concurrent_tasks:
                return None
            
            # Find suitable task from queue
            suitable_tasks = []
            temp_queue = []
            
            while self.priority_queue:
                priority, timestamp, scheduled_task = heapq.heappop(self.priority_queue)
                
                # Check if task is ready
                if await self._is_task_ready(scheduled_task):
                    # Check if worker can handle task
                    if await self._can_worker_handle_task(worker_id, scheduled_task):
                        suitable_tasks.append((priority, timestamp, scheduled_task))
                    else:
                        temp_queue.append((priority, timestamp, scheduled_task))
                else:
                    temp_queue.append((priority, timestamp, scheduled_task))
                
                # Found suitable task
                if suitable_tasks:
                    break
            
            # Restore remaining tasks to queue
            for task_data in temp_queue:
                heapq.heappush(self.priority_queue, task_data)
            
            if suitable_tasks:
                # Select best task
                _, _, selected_task = min(suitable_tasks, key=lambda x: x[0])
                
                # Assign worker
                selected_task.assigned_worker = worker_id
                
                # Update worker capacity
                await self._allocate_resources(worker_id, selected_task)
                
                logger.info(f"✅ Task {selected_task.task.task_id} assigned to worker {worker_id}")
                return selected_task
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Failed to get next scheduled task for worker {worker_id}: {e}")
            return None

    async def mark_task_completed(self, task_id: str, success: bool = True) -> None:
        """Mark a task as completed"""
        try:
            self.completed_tasks.add(task_id)
            
            # Update statistics
            if success:
                self.scheduling_stats['successful_schedules'] += 1
            
            # Resolve dependencies
            if task_id in self.dependency_graph:
                for dependent_task_id in self.dependency_graph[task_id]:
                    if dependent_task_id in self.pending_dependencies:
                        self.pending_dependencies[dependent_task_id].discard(task_id)
            
            # Free up resources
            scheduled_task = self.scheduled_tasks.get(task_id)
            if scheduled_task and scheduled_task.assigned_worker:
                await self._deallocate_resources(scheduled_task.assigned_worker, scheduled_task)
            
            # Clean up
            self.scheduled_tasks.pop(task_id, None)
            
            logger.info(f"✅ Task marked as completed: {task_id}")
            
        except Exception as e:
            logger.error(f"❌ Failed to mark task completed {task_id}: {e}")

    async def get_scheduling_status(self) -> Dict[str, Any]:
        """Get comprehensive scheduling status"""
        try:
            # Calculate metrics
            total_workers = len(self.worker_capacities)
            active_workers = sum(1 for c in self.worker_capacities.values() if c.current_tasks > 0)
            
            avg_utilization = 0.0
            if self.worker_capacities:
                utilizations = []
                for capacity in self.worker_capacities.values():
                    cpu_util = capacity.current_cpu / capacity.max_cpu
                    mem_util = capacity.current_memory / capacity.max_memory
                    task_util = capacity.current_tasks / capacity.max_concurrent_tasks
                    utilizations.append((cpu_util + mem_util + task_util) / 3)
                avg_utilization = statistics.mean(utilizations) * 100
            
            return {
                'scheduler_status': 'active',
                'strategy': self.strategy.value,
                'queue_size': len(self.priority_queue),
                'scheduled_tasks': len(self.scheduled_tasks),
                'completed_tasks': len(self.completed_tasks),
                'pending_dependencies': sum(len(deps) for deps in self.pending_dependencies.values()),
                'workers': {
                    'total': total_workers,
                    'active': active_workers,
                    'idle': total_workers - active_workers,
                    'average_utilization': avg_utilization
                },
                'statistics': self.scheduling_stats,
                'performance': {
                    'avg_wait_time': self.scheduling_stats['average_wait_time'],
                    'avg_execution_time': self.scheduling_stats['average_execution_time'],
                    'success_rate': (
                        self.scheduling_stats['successful_schedules'] / 
                        max(1, self.scheduling_stats['total_scheduled'])
                    ) * 100
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get scheduling status: {e}")
            return {'error': str(e)}

    async def _start_background_tasks(self) -> None:
        """Start background scheduler tasks"""
        try:
            # Dependency resolver
            dependency_resolver = asyncio.create_task(self._dependency_resolver())
            self.background_tasks.add(dependency_resolver)
            
            # Performance analyzer
            performance_analyzer = asyncio.create_task(self._performance_analyzer())
            self.background_tasks.add(performance_analyzer)
            
            # Resource optimizer
            resource_optimizer = asyncio.create_task(self._resource_optimizer())
            self.background_tasks.add(resource_optimizer)
            
            # Statistics updater
            stats_updater = asyncio.create_task(self._statistics_updater())
            self.background_tasks.add(stats_updater)
            
            logger.info("✅ Scheduler background tasks started")
            
        except Exception as e:
            logger.error(f"❌ Failed to start background tasks: {e}")
            raise

    async def _dependency_resolver(self) -> None:
        """Resolve task dependencies continuously"""
        while not self.shutdown_event.is_set():
            try:
                # Check for resolved dependencies
                resolved_tasks = []
                for task_id, dependencies in list(self.pending_dependencies.items()):
                    if not dependencies:  # All dependencies resolved
                        resolved_tasks.append(task_id)
                
                # Remove resolved dependencies
                for task_id in resolved_tasks:
                    del self.pending_dependencies[task_id]
                
                await asyncio.sleep(5)  # Check every 5 seconds
                
            except Exception as e:
                logger.error(f"❌ Dependency resolver error: {e}")
                await asyncio.sleep(30)

    async def _performance_analyzer(self) -> None:
        """Analyze worker performance and optimize scheduling"""
        while not self.shutdown_event.is_set():
            try:
                # Analyze worker performance
                for worker_id, performance_data in self.worker_performance.items():
                    if worker_id in self.worker_capacities:
                        # Calculate efficiency trends
                        efficiency_scores = performance_data.get('efficiency', [])
                        if len(efficiency_scores) >= 10:
                            recent_avg = statistics.mean(efficiency_scores[-10:])
                            overall_avg = statistics.mean(efficiency_scores)
                            
                            # Update worker capacity efficiency
                            self.worker_capacities[worker_id].efficiency_score = recent_avg
                            
                            # Log performance insights
                            if recent_avg < overall_avg * 0.8:
                                logger.warning(f"⚠️ Worker {worker_id} performance declining")
                
                await asyncio.sleep(60)  # Analyze every minute
                
            except Exception as e:
                logger.error(f"❌ Performance analyzer error: {e}")
                await asyncio.sleep(120)

    async def _resource_optimizer(self) -> None:
        """Optimize resource allocation across workers"""
        while not self.shutdown_event.is_set():
            try:
                # Calculate global resource utilization
                total_cpu = sum(c.max_cpu for c in self.worker_capacities.values())
                used_cpu = sum(c.current_cpu for c in self.worker_capacities.values())
                
                total_memory = sum(c.max_memory for c in self.worker_capacities.values())
                used_memory = sum(c.current_memory for c in self.worker_capacities.values())
                
                # Update global utilization
                if total_cpu > 0 and total_memory > 0:
                    cpu_util = used_cpu / total_cpu
                    mem_util = used_memory / total_memory
                    self.scheduling_stats['resource_utilization'] = (cpu_util + mem_util) / 2
                
                # Identify optimization opportunities
                await self._identify_optimization_opportunities()
                
                await asyncio.sleep(120)  # Optimize every 2 minutes
                
            except Exception as e:
                logger.error(f"❌ Resource optimizer error: {e}")
                await asyncio.sleep(180)

    async def _identify_optimization_opportunities(self) -> None:
        """Identify opportunities for resource optimization"""
        try:
            # Find overloaded and underutilized workers
            overloaded_workers = []
            underutilized_workers = []
            
            for worker_id, capacity in self.worker_capacities.items():
                cpu_util = capacity.current_cpu / capacity.max_cpu
                mem_util = capacity.current_memory / capacity.max_memory
                task_util = capacity.current_tasks / capacity.max_concurrent_tasks
                
                avg_util = (cpu_util + mem_util + task_util) / 3
                
                if avg_util > 0.9:
                    overloaded_workers.append(worker_id)
                elif avg_util < 0.3:
                    underutilized_workers.append(worker_id)
            
            # Log optimization opportunities
            if overloaded_workers:
                logger.info(f"📊 Overloaded workers detected: {overloaded_workers}")
            
            if underutilized_workers:
                logger.info(f"📊 Underutilized workers detected: {underutilized_workers}")
            
        except Exception as e:
            logger.error(f"❌ Failed to identify optimization opportunities: {e}")

    async def _statistics_updater(self) -> None:
        """Update scheduling statistics"""
        while not self.shutdown_event.is_set():
            try:
                # Calculate average wait times
                if self.scheduled_tasks:
                    wait_times = []
                    execution_times = []
                    
                    for scheduled_task in self.scheduled_tasks.values():
                        if scheduled_task.assigned_worker:
                            # Calculate wait time
                            wait_time = (scheduled_task.scheduled_time - scheduled_task.task.created_at).total_seconds()
                            wait_times.append(wait_time)
                            
                            # Calculate execution time estimate
                            if scheduled_task.resource_allocation and scheduled_task.resource_allocation.estimated_duration:
                                execution_times.append(scheduled_task.resource_allocation.estimated_duration)
                    
                    if wait_times:
                        self.scheduling_stats['average_wait_time'] = statistics.mean(wait_times)
                    
                    if execution_times:
                        self.scheduling_stats['average_execution_time'] = statistics.mean(execution_times)
                
                await asyncio.sleep(30)  # Update every 30 seconds
                
            except Exception as e:
                logger.error(f"❌ Statistics updater error: {e}")
                await asyncio.sleep(60)

    async def _estimate_resource_requirements(self, task: CrawlerTask) -> ResourceRequirement:
        """Estimate resource requirements for a task"""
        try:
            # Base requirements
            base_cpu = 1.0
            base_memory = 256
            base_network = 10.0
            base_storage = 100
            
            # Adjust based on task characteristics
            if task.platform in ['youtube', 'tiktok']:
                # Video platforms require more resources
                base_cpu *= 1.5
                base_memory *= 2
                base_network *= 3
            elif task.platform in ['instagram', 'pinterest']:
                # Image-heavy platforms
                base_memory *= 1.5
                base_network *= 2
            
            # Adjust for content types
            if 'video' in task.content_types:
                base_cpu *= 2
                base_memory *= 2
                base_storage *= 5
            elif 'audio' in task.content_types:
                base_cpu *= 1.5
                base_memory *= 1.5
                base_storage *= 3
            elif 'images' in task.content_types:
                base_memory *= 1.3
                base_storage *= 2
            
            # Estimate duration using ML prediction
            estimated_duration = await self.prediction_engine.predict_task_duration(
                task.platform,
                task.content_types,
                task.metadata
            )
            
            return ResourceRequirement(
                cpu_cores=base_cpu,
                memory_mb=base_memory,
                network_mbps=base_network,
                storage_mb=base_storage,
                estimated_duration=estimated_duration
            )
            
        except Exception as e:
            logger.error(f"❌ Failed to estimate resource requirements: {e}")
            return ResourceRequirement()

    async def _calculate_optimal_schedule_time(
        self, 
        task: CrawlerTask,
        resource_req: ResourceRequirement,
        constraints: List[SchedulingConstraint]
    ) -> datetime:
        """Calculate optimal scheduling time"""
        try:
            # Start with current time
            schedule_time = datetime.utcnow()
            
            # Apply time window constraints
            for constraint in constraints:
                if constraint.constraint_type == 'time_window':
                    window_start = constraint.constraint_data.get('start_time')
                    window_end = constraint.constraint_data.get('end_time')
                    
                    if window_start and schedule_time < window_start:
                        schedule_time = window_start
            
            # Consider resource availability
            earliest_available = await self._find_earliest_resource_availability(resource_req)
            if earliest_available > schedule_time:
                schedule_time = earliest_available
            
            # Add small buffer for scheduling overhead
            schedule_time += timedelta(seconds=5)
            
            return schedule_time
            
        except Exception as e:
            logger.error(f"❌ Failed to calculate optimal schedule time: {e}")
            return datetime.utcnow()

    async def _find_earliest_resource_availability(self, resource_req: ResourceRequirement) -> datetime:
        """Find earliest time when resources will be available"""
        try:
            earliest_time = datetime.utcnow()
            
            # Check each worker's schedule
            for worker_id, capacity in self.worker_capacities.items():
                # Check if worker can theoretically handle the task
                if (resource_req.cpu_cores <= capacity.max_cpu and 
                    resource_req.memory_mb <= capacity.max_memory):
                    
                    # Find when worker will have sufficient resources
                    worker_schedule = self.worker_schedules.get(worker_id, [])
                    
                    # Simple approach: find gap in schedule
                    # In production, this would be more sophisticated
                    if not worker_schedule:
                        return earliest_time
                    
                    # Check for gaps between scheduled tasks
                    for i in range(len(worker_schedule) - 1):
                        gap_start = worker_schedule[i].estimated_completion
                        gap_end = worker_schedule[i + 1].scheduled_time
                        
                        if gap_end - gap_start >= timedelta(seconds=resource_req.estimated_duration or 300):
                            return gap_start
            
            return earliest_time
            
        except Exception as e:
            logger.error(f"❌ Failed to find earliest resource availability: {e}")
            return datetime.utcnow()

    def _calculate_scheduling_priority(self, scheduled_task: ScheduledTask) -> int:
        """Calculate priority value for scheduling queue"""
        try:
            # Base priority from task
            base_priority = {
                TaskPriority.CRITICAL: 1,
                TaskPriority.HIGH: 2,
                TaskPriority.MEDIUM: 3,
                TaskPriority.LOW: 4,
                TaskPriority.BACKGROUND: 5
            }.get(scheduled_task.task.priority, 3)
            
            # Adjust for constraints
            priority_adjustment = 0
            for constraint in scheduled_task.constraints:
                if constraint.is_hard:
                    priority_adjustment -= constraint.priority
            
            # Adjust for dependencies
            if scheduled_task.dependencies:
                priority_adjustment += len(scheduled_task.dependencies)
            
            # Adjust for estimated duration (favor shorter tasks)
            if scheduled_task.resource_allocation and scheduled_task.resource_allocation.estimated_duration:
                duration_factor = min(2, scheduled_task.resource_allocation.estimated_duration / 300)
                priority_adjustment += duration_factor
            
            return max(1, base_priority + priority_adjustment)
            
        except Exception as e:
            logger.error(f"❌ Failed to calculate scheduling priority: {e}")
            return 3

    async def _is_task_ready(self, scheduled_task: ScheduledTask) -> bool:
        """Check if task is ready for execution"""
        try:
            # Check if scheduled time has arrived
            if scheduled_task.scheduled_time > datetime.utcnow():
                return False
            
            # Check dependencies
            if scheduled_task.task.task_id in self.pending_dependencies:
                if self.pending_dependencies[scheduled_task.task.task_id]:
                    return False
            
            # Check constraints
            for constraint in scheduled_task.constraints:
                if not await self._check_constraint_satisfaction(constraint):
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to check if task is ready: {e}")
            return False

    async def _can_worker_handle_task(self, worker_id: str, scheduled_task: ScheduledTask) -> bool:
        """Check if worker can handle the task"""
        try:
            capacity = self.worker_capacities.get(worker_id)
            if not capacity:
                return False
            
            resource_req = scheduled_task.resource_allocation
            if not resource_req:
                return True  # No specific requirements
            
            # Check resource capacity
            if (capacity.current_cpu + resource_req.cpu_cores > capacity.max_cpu or
                capacity.current_memory + resource_req.memory_mb > capacity.max_memory or
                capacity.current_tasks >= capacity.max_concurrent_tasks):
                return False
            
            # Check worker specializations
            if capacity.specializations:
                task_platform = scheduled_task.task.platform
                if task_platform not in capacity.specializations and 'all' not in capacity.specializations:
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to check if worker can handle task: {e}")
            return False

    async def _allocate_resources(self, worker_id: str, scheduled_task: ScheduledTask) -> None:
        """Allocate resources to worker for task"""
        try:
            capacity = self.worker_capacities.get(worker_id)
            resource_req = scheduled_task.resource_allocation
            
            if capacity and resource_req:
                capacity.current_cpu += resource_req.cpu_cores
                capacity.current_memory += resource_req.memory_mb
                capacity.current_network += resource_req.network_mbps
                capacity.current_tasks += 1
            
            # Add to worker schedule
            self.worker_schedules[worker_id].append(scheduled_task)
            
        except Exception as e:
            logger.error(f"❌ Failed to allocate resources: {e}")

    async def _deallocate_resources(self, worker_id: str, scheduled_task: ScheduledTask) -> None:
        """Deallocate resources from worker"""
        try:
            capacity = self.worker_capacities.get(worker_id)
            resource_req = scheduled_task.resource_allocation
            
            if capacity and resource_req:
                capacity.current_cpu = max(0, capacity.current_cpu - resource_req.cpu_cores)
                capacity.current_memory = max(0, capacity.current_memory - resource_req.memory_mb)
                capacity.current_network = max(0, capacity.current_network - resource_req.network_mbps)
                capacity.current_tasks = max(0, capacity.current_tasks - 1)
            
            # Remove from worker schedule
            if worker_id in self.worker_schedules:
                self.worker_schedules[worker_id] = [
                    task for task in self.worker_schedules[worker_id]
                    if task.task.task_id != scheduled_task.task.task_id
                ]
            
        except Exception as e:
            logger.error(f"❌ Failed to deallocate resources: {e}")

    async def _check_constraint_satisfaction(self, constraint: SchedulingConstraint) -> bool:
        """Check if constraint is satisfied"""
        try:
            constraint_type = constraint.constraint_type
            constraint_data = constraint.constraint_data
            
            if constraint_type == 'time_window':
                current_time = datetime.utcnow()
                start_time = constraint_data.get('start_time')
                end_time = constraint_data.get('end_time')
                
                if start_time and current_time < start_time:
                    return False
                if end_time and current_time > end_time:
                    return False
            
            elif constraint_type == 'resource_limit':
                # Check global resource limits
                resource_type = constraint_data.get('resource_type')
                limit_value = constraint_data.get('limit')
                
                if resource_type and limit_value:
                    current_usage = await self._get_current_resource_usage(resource_type)
                    if current_usage > limit_value:
                        return False
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to check constraint satisfaction: {e}")
            return True  # Default to satisfied for safety

    async def _get_current_resource_usage(self, resource_type: str) -> float:
        """Get current resource usage across all workers"""
        try:
            total_usage = 0.0
            
            for capacity in self.worker_capacities.values():
                if resource_type == 'cpu':
                    total_usage += capacity.current_cpu
                elif resource_type == 'memory':
                    total_usage += capacity.current_memory
                elif resource_type == 'network':
                    total_usage += capacity.current_network
            
            return total_usage
            
        except Exception as e:
            logger.error(f"❌ Failed to get current resource usage: {e}")
            return 0.0

    async def _estimate_task_duration(self, task: CrawlerTask) -> float:
        """Estimate task duration using historical data"""
        try:
            # Use prediction engine
            predicted_duration = await self.prediction_engine.predict_task_duration(
                task.platform,
                task.content_types,
                task.metadata
            )
            
            return predicted_duration or 300.0  # Default 5 minutes
            
        except Exception as e:
            logger.error(f"❌ Failed to estimate task duration: {e}")
            return 300.0
