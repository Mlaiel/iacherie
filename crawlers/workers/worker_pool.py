"""Worker Pool Manager - IA-Influencer-Agent
================================================================================
Module: backend/crawlers/workers/worker_pool.py
Author: Fahed Mlaiel (mlaiel@live.de)
Type: Industrial Worker Pool - Distributed Processing Management
Responsibility: Intelligent worker orchestration and load balancing
Technologies: AsyncIO, Dynamic Scaling, Load Balancing, Health Monitoring
================================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Usage non autorisé strictement interdit et passible de poursuites judiciaires.
Contact: mlaiel@live.de

LOGIQUE MÉTIER:
Task submission → Load analysis → Worker selection → 
Task distribution → Execution monitoring → Result aggregation → Auto-scaling
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

from .crawler_worker import CrawlerWorker, WorkerConfig, WorkerType, WorkerStatus, CrawlerTask, TaskResult
from .worker_scheduler import WorkerScheduler
from .load_balancer import WorkerLoadBalancer
from .scaling_manager import WorkerScalingManager
from ...core.managers.queue_manager import ProductionQueueManager, TaskPriority
from ...monitoring.performance_monitor import PerformanceMonitor
from ...security.access_control import AccessControl
from ...utils.resource_utils import ResourceUtils

logger = logging.getLogger(__name__)


class PoolStatus(Enum):
    """
Worker pool status states"""

    INITIALIZING = "initializing"
    ACTIVE = "active"
    DEGRADED = "degraded"
    OVERLOADED = "overloaded"
    MAINTENANCE = "maintenance"
    SHUTDOWN = "shutdown"


class LoadBalancingStrategy(Enum):
    """Load balancing strategies"""

    ROUND_ROBIN = "round_robin"
    LEAST_CONNECTIONS = "least_connections"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    RESPONSE_TIME = "response_time"
    RESOURCE_BASED = "resource_based"
    INTELLIGENT = "intelligent"


@dataclass
class PoolConfig:
    """Worker pool configuration"""
    pool_id: str
    min_workers: int = 2
    max_workers: int = 20
    initial_workers: int = 5
    scaling_threshold: float = 0.8
    scale_down_threshold: float = 0.3
    health_check_interval: int = 30
    load_balancing_strategy: LoadBalancingStrategy = LoadBalancingStrategy.INTELLIGENT
    worker_timeout: int = 300
    max_queue_size: int = 1000
    auto_scaling_enabled: bool = True
    worker_types: List[WorkerType] = field(default_factory=lambda: [WorkerType.GENERIC])


@dataclass
class PoolMetrics:
    """
Worker pool performance metrics"""
    pool_id: str
    total_workers: int = 0
    active_workers: int = 0
    idle_workers: int = 0
    busy_workers: int = 0
    overloaded_workers: int = 0
    error_workers: int = 0
    queue_size: int = 0
    total_tasks_processed: int = 0
    successful_tasks: int = 0
    failed_tasks: int = 0
    average_response_time: float = 0.0
    throughput_per_second: float = 0.0
    resource_utilization: float = 0.0
    last_scaling_action: Optional[datetime] = None
    uptime_hours: float = 0.0


@dataclass
class TaskAssignment:
    """
Task assignment tracking"""
    task_id: str
    worker_id: str
    assigned_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[TaskResult] = None
    duration_seconds: Optional[float] = None


class WorkerPool:
    """
    Intelligent worker pool for distributed crawler task processing
    
    Features:
    - Dynamic worker scaling
    - Intelligent load balancing
    - Health monitoring and recovery
    - Resource optimization
    - Task routing and queuing
    - Performance analytics
    """
    def __init__(self, config: PoolConfig):
        self.config = config
        self.pool_id = config.pool_id
        self.status = PoolStatus.INITIALIZING
        self.metrics = PoolMetrics(pool_id=self.pool_id)
        
        # Worker management
        self.workers: Dict[str, CrawlerWorker] = {}
        self.worker_configs: Dict[str, WorkerConfig] = {}
        self.worker_health: Dict[str, Dict[str, Any]] = {}
        
        # Task management
        self.task_queue: asyncio.PriorityQueue = asyncio.PriorityQueue(maxsize=config.max_queue_size)
        self.pending_tasks: Dict[str, CrawlerTask] = {}
        self.active_assignments: Dict[str, TaskAssignment] = {}
        self.completed_assignments: deque = deque(maxlen=10000)
        
        # Components
        self.scheduler = WorkerScheduler(self)
        self.load_balancer = WorkerLoadBalancer(config.load_balancing_strategy)
        self.scaling_manager = WorkerScalingManager(config)
        self.performance_monitor = PerformanceMonitor()
        self.access_control = AccessControl()
        self.resource_utils = ResourceUtils()
        
        # Background tasks
        self.background_tasks: Set[asyncio.Task] = set()
        self.shutdown_event = asyncio.Event()
        self.startup_time = datetime.utcnow()
        
        # Statistics
        self.task_statistics: Dict[str, List[float]] = defaultdict(list)
        self.worker_statistics: Dict[str, Dict[str, List[float]]] = defaultdict(lambda: defaultdict(list))

    async def start(self) -> bool:
        """
Start the worker pool"""
        try:
            logger.info(f"🚀 Starting worker pool: {self.pool_id}")
            
            # Initialize components
            await self._initialize_components()
            
            # Create initial workers
            await self._create_initial_workers()
            
            # Start background tasks
            await self._start_background_tasks()
            
            self.status = PoolStatus.ACTIVE
            
            logger.info(f"✅ Worker pool {self.pool_id} started with {len(self.workers)} workers")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to start worker pool {self.pool_id}: {e}")
            self.status = PoolStatus.SHUTDOWN
            return False

    async def stop(self) -> None:
        """Gracefully stop the worker pool"""
        try:
            logger.info(f"🛑 Stopping worker pool: {self.pool_id}")
            
            self.status = PoolStatus.SHUTDOWN
            self.shutdown_event.set()
            
            # Stop accepting new tasks
            logger.info("⏹️ Stopping task acceptance...")
            
            # Wait for active tasks to complete
            if self.active_assignments:
                logger.info(f"⏳ Waiting for {len(self.active_assignments)} active tasks to complete...")
                await asyncio.wait_for(
                    self._wait_for_active_tasks(),
                    timeout=300.0  # 5 minutes max
                )
            
            # Stop all workers
            logger.info(f"🛑 Stopping {len(self.workers)} workers...")
            await self._stop_all_workers()
            
            # Cancel background tasks
            for task in self.background_tasks:
                if not task.done():
                    task.cancel()
            
            if self.background_tasks:
                await asyncio.gather(*self.background_tasks, return_exceptions=True)
            
            logger.info(f"✅ Worker pool {self.pool_id} stopped gracefully")
            
        except Exception as e:
            logger.error(f"❌ Error stopping worker pool {self.pool_id}: {e}")

    async def submit_task(self, task: CrawlerTask, priority: Optional[TaskPriority] = None) -> bool:
        """Submit a task to the worker pool"""
        try:
            # Validate task
            if not await self._validate_task(task):
                logger.warning(f"❌ Invalid task rejected: {task.task_id}")
                return False
            
            # Check pool capacity
            if self.task_queue.full():
                logger.warning(f"⚠️ Worker pool {self.pool_id} queue full, task rejected: {task.task_id}")
                return False
            
            # Determine priority
            if priority is None:
                priority = await self._calculate_task_priority(task)
            
            # Add to queue
            priority_value = self._get_priority_value(priority)
            await self.task_queue.put((priority_value, time.time(), task))
            
            self.pending_tasks[task.task_id] = task
            self.metrics.queue_size = self.task_queue.qsize()
            
            logger.info(f"📝 Task submitted to pool {self.pool_id}: {task.task_id} (priority: {priority.value})")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to submit task {task.task_id}: {e}")
            return False

    async def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """Get comprehensive task status"""
        try:
            # Check if task is active
            if task_id in self.active_assignments:
                assignment = self.active_assignments[task_id]
                worker = self.workers.get(assignment.worker_id)
                
                return {
                    "task_id": task_id,
                    "status": "running",
                    "worker_id": assignment.worker_id,
                    "assigned_at": assignment.assigned_at.isoformat(),
                    "started_at": assignment.started_at.isoformat() if assignment.started_at else None,
                    "worker_status": worker.status.value if worker else "unknown",
                    "estimated_completion": await self._estimate_completion_time(assignment)
                }
            
            # Check if task is pending
            if task_id in self.pending_tasks:
                position = await self._get_queue_position(task_id)
                return {
                    "task_id": task_id,
                    "status": "pending",
                    "queue_position": position,
                    "estimated_start": await self._estimate_start_time(position)
                }
            
            # Check completed tasks
            for assignment in self.completed_assignments:
                if assignment.task_id == task_id:
                    return {
                        "task_id": task_id,
                        "status": "completed",
                        "result": assignment.result.value if assignment.result else "unknown",
                        "worker_id": assignment.worker_id,
                        "assigned_at": assignment.assigned_at.isoformat(),
                        "started_at": assignment.started_at.isoformat() if assignment.started_at else None,
                        "completed_at": assignment.completed_at.isoformat() if assignment.completed_at else None,
                        "duration_seconds": assignment.duration_seconds
                    }
            
            return {"task_id": task_id, "status": "not_found"}
            
        except Exception as e:
            logger.error(f"❌ Failed to get task status {task_id}: {e}")
            return {"task_id": task_id, "status": "error", "error": str(e)}

    async def get_pool_status(self) -> Dict[str, Any]:
        """Get comprehensive pool status"""
        try:
            # Update metrics
            await self._update_pool_metrics()
            
            # Get worker statuses
            worker_statuses = {}
            for worker_id, worker in self.workers.items():
                worker_statuses[worker_id] = await worker.get_status()
            
            return {
                "pool_id": self.pool_id,
                "status": self.status.value,
                "config": {
                    "min_workers": self.config.min_workers,
                    "max_workers": self.config.max_workers,
                    "current_workers": len(self.workers),
                    "auto_scaling": self.config.auto_scaling_enabled,
                    "load_balancing": self.config.load_balancing_strategy.value
                },
                "metrics": {
                    "total_workers": self.metrics.total_workers,
                    "active_workers": self.metrics.active_workers,
                    "idle_workers": self.metrics.idle_workers,
                    "busy_workers": self.metrics.busy_workers,
                    "overloaded_workers": self.metrics.overloaded_workers,
                    "error_workers": self.metrics.error_workers,
                    "queue_size": self.metrics.queue_size,
                    "total_processed": self.metrics.total_tasks_processed,
                    "successful": self.metrics.successful_tasks,
                    "failed": self.metrics.failed_tasks,
                    "success_rate": (self.metrics.successful_tasks / max(1, self.metrics.total_tasks_processed)) * 100,
                    "avg_response_time": self.metrics.average_response_time,
                    "throughput_per_second": self.metrics.throughput_per_second,
                    "resource_utilization": self.metrics.resource_utilization,
                    "uptime_hours": self.metrics.uptime_hours
                },
                "workers": worker_statuses,
                "last_scaling": self.metrics.last_scaling_action.isoformat() if self.metrics.last_scaling_action else None
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get pool status: {e}")
            return {"pool_id": self.pool_id, "status": "error", "error": str(e)}

    async def scale_workers(self, target_count: int) -> bool:
        """Manually scale workers to target count"""
        try:
            current_count = len(self.workers)
            
            if target_count > self.config.max_workers:
                target_count = self.config.max_workers
                logger.warning(f"⚠️ Target count capped at max_workers: {self.config.max_workers}")
            elif target_count < self.config.min_workers:
                target_count = self.config.min_workers
                logger.warning(f"⚠️ Target count raised to min_workers: {self.config.min_workers}")
            
            if target_count > current_count:
                # Scale up
                workers_to_add = target_count - current_count
                await self._add_workers(workers_to_add)
                logger.info(f"📈 Scaled up pool {self.pool_id}: {current_count} → {target_count} workers")
            elif target_count < current_count:
                # Scale down
                workers_to_remove = current_count - target_count
                await self._remove_workers(workers_to_remove)
                logger.info(f"📉 Scaled down pool {self.pool_id}: {current_count} → {target_count} workers")
            
            self.metrics.last_scaling_action = datetime.utcnow()
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to scale workers: {e}")
            return False

    async def _initialize_components(self) -> None:
        """Initialize pool components"""
        try:
            # Initialize scheduler
            await self.scheduler.initialize()
            
            # Initialize load balancer
            await self.load_balancer.initialize()
            
            # Initialize scaling manager
            await self.scaling_manager.initialize()
            
            logger.info(f"✅ Pool {self.pool_id} components initialized")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize pool components: {e}")
            raise

    async def _create_initial_workers(self) -> None:
        """Create initial set of workers"""
        try:
            for i in range(self.config.initial_workers):
                worker_id = f"{self.pool_id}-worker-{i+1}"
                worker_type = self.config.worker_types[i % len(self.config.worker_types)]
                
                await self._create_worker(worker_id, worker_type)
            
            logger.info(f"✅ Created {self.config.initial_workers} initial workers")
            
        except Exception as e:
            logger.error(f"❌ Failed to create initial workers: {e}")
            raise

    async def _create_worker(self, worker_id: str, worker_type: WorkerType) -> bool:
        """Create and start a new worker"""
        try:
            # Create worker config
            worker_config = WorkerConfig(
                worker_id=worker_id,
                worker_type=worker_type,
                timeout_seconds=self.config.worker_timeout
            )
            
            # Create worker
            worker = CrawlerWorker(worker_config)
            
            # Start worker
            if await worker.start():
                self.workers[worker_id] = worker
                self.worker_configs[worker_id] = worker_config
                self.worker_health[worker_id] = {
                    "last_check": datetime.utcnow(),
                    "status": "healthy",
                    "consecutive_failures": 0
                }
                
                logger.info(f"✅ Created worker: {worker_id} ({worker_type.value})")
                return True
            else:
                logger.error(f"❌ Failed to start worker: {worker_id}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Failed to create worker {worker_id}: {e}")
            return False

    async def _start_background_tasks(self) -> None:
        """Start background pool tasks"""
        try:
            # Task dispatcher
            task_dispatcher = asyncio.create_task(self._task_dispatcher())
            self.background_tasks.add(task_dispatcher)
            
            # Pool monitor
            pool_monitor = asyncio.create_task(self._pool_monitor())
            self.background_tasks.add(pool_monitor)
            
            # Health checker
            health_checker = asyncio.create_task(self._health_checker())
            self.background_tasks.add(health_checker)
            
            # Metrics collector
            metrics_collector = asyncio.create_task(self._metrics_collector())
            self.background_tasks.add(metrics_collector)
            
            # Auto scaler (if enabled)
            if self.config.auto_scaling_enabled:
                auto_scaler = asyncio.create_task(self._auto_scaler())
                self.background_tasks.add(auto_scaler)
            
            logger.info(f"✅ Background tasks started for pool {self.pool_id}")
            
        except Exception as e:
            logger.error(f"❌ Failed to start background tasks: {e}")
            raise

    async def _task_dispatcher(self) -> None:
        """Dispatch tasks to available workers"""
        while not self.shutdown_event.is_set():
            try:
                # Get next task from queue
                priority, timestamp, task = await asyncio.wait_for(
                    self.task_queue.get(),
                    timeout=1.0
                )
                
                # Find best worker for task
                worker_id = await self.load_balancer.select_worker(
                    task, list(self.workers.keys()), self.worker_health
                )
                
                if worker_id and worker_id in self.workers:
                    # Assign task to worker
                    await self._assign_task_to_worker(task, worker_id)
                else:
                    # No available worker, requeue task
                    await self.task_queue.put((priority, timestamp, task))
                    await asyncio.sleep(1)  # Brief delay before retry
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"❌ Task dispatcher error: {e}")
                await asyncio.sleep(5)

    async def _assign_task_to_worker(self, task: CrawlerTask, worker_id: str) -> None:
        """Assign a task to a specific worker"""
        try:
            worker = self.workers[worker_id]
            
            # Create assignment record
            assignment = TaskAssignment(
                task_id=task.task_id,
                worker_id=worker_id,
                assigned_at=datetime.utcnow()
            )
            
            # Submit task to worker
            if await worker.submit_task(task):
                self.active_assignments[task.task_id] = assignment
                self.pending_tasks.pop(task.task_id, None)
                
                logger.info(f"✅ Task {task.task_id} assigned to worker {worker_id}")
                
                # Monitor task execution
                asyncio.create_task(self._monitor_task_execution(assignment))
                
            else:
                logger.error(f"❌ Failed to assign task {task.task_id} to worker {worker_id}")
                
        except Exception as e:
            logger.error(f"❌ Failed to assign task {task.task_id} to worker {worker_id}: {e}")

    async def _monitor_task_execution(self, assignment: TaskAssignment) -> None:
        """Monitor task execution and update assignment"""
        try:
            task_id = assignment.task_id
            worker_id = assignment.worker_id
            worker = self.workers.get(worker_id)
            
            if not worker:
                return
            
            # Wait for task completion
            start_time = time.time()
            timeout = 600  # 10 minutes max
            
            while time.time() - start_time < timeout:
                worker_status = await worker.get_status()
                
                # Check if task is still active
                if task_id not in worker_status.get('active_tasks', []):
                    # Task completed
                    assignment.completed_at = datetime.utcnow()
                    assignment.duration_seconds = (assignment.completed_at - assignment.assigned_at).total_seconds()
                    
                    # Move to completed
                    self.active_assignments.pop(task_id, None)
                    self.completed_assignments.append(assignment)
                    
                    # Update metrics
                    self.metrics.total_tasks_processed += 1
                    self.metrics.successful_tasks += 1
                    
                    logger.info(f"✅ Task {task_id} completed on worker {worker_id}")
                    break
                
                await asyncio.sleep(5)  # Check every 5 seconds
            else:
                # Task timeout
                assignment.result = TaskResult.TIMEOUT
                assignment.completed_at = datetime.utcnow()
                
                logger.warning(f"⏰ Task {task_id} timed out on worker {worker_id}")
                
        except Exception as e:
            logger.error(f"❌ Task monitoring error for {assignment.task_id}: {e}")

    async def _pool_monitor(self) -> None:
        """Monitor pool status and performance"""
        while not self.shutdown_event.is_set():
            try:
                # Update pool metrics
                await self._update_pool_metrics()
                
                # Check pool health
                await self._check_pool_health()
                
                # Log pool status
                if len(self.workers) > 0:
                    logger.debug(f"📊 Pool {self.pool_id}: {len(self.workers)} workers, "
                               f"{self.metrics.queue_size} queued, "
                               f"{len(self.active_assignments)} active")
                
                await asyncio.sleep(30)  # Monitor every 30 seconds
                
            except Exception as e:
                logger.error(f"❌ Pool monitor error: {e}")
                await asyncio.sleep(60)

    async def _health_checker(self) -> None:
        """Check health of all workers"""
        while not self.shutdown_event.is_set():
            try:
                unhealthy_workers = []
                
                for worker_id, worker in self.workers.items():
                    try:
                        # Get worker status
                        status = await asyncio.wait_for(
                            worker.get_status(),
                            timeout=10.0
                        )
                        
                        # Update health record
                        if status.get('status') == 'error':
                            self.worker_health[worker_id]['consecutive_failures'] += 1
                            if self.worker_health[worker_id]['consecutive_failures'] >= 3:
                                unhealthy_workers.append(worker_id)
                        else:
                            self.worker_health[worker_id]['consecutive_failures'] = 0
                            self.worker_health[worker_id]['status'] = 'healthy'
                        
                        self.worker_health[worker_id]['last_check'] = datetime.utcnow()
                        
                    except asyncio.TimeoutError:
                        logger.warning(f"⚠️ Worker {worker_id} health check timeout")
                        self.worker_health[worker_id]['consecutive_failures'] += 1
                    except Exception as e:
                        logger.error(f"❌ Health check failed for worker {worker_id}: {e}")
                        self.worker_health[worker_id]['consecutive_failures'] += 1
                
                # Replace unhealthy workers
                for worker_id in unhealthy_workers:
                    await self._replace_unhealthy_worker(worker_id)
                
                await asyncio.sleep(self.config.health_check_interval)
                
            except Exception as e:
                logger.error(f"❌ Health checker error: {e}")
                await asyncio.sleep(60)

    async def _replace_unhealthy_worker(self, worker_id: str) -> None:
        """Replace an unhealthy worker"""
        try:
            logger.warning(f"🔄 Replacing unhealthy worker: {worker_id}")
            
            # Get worker config
            worker_config = self.worker_configs.get(worker_id)
            if not worker_config:
                return
            
            # Stop unhealthy worker
            worker = self.workers.get(worker_id)
            if worker:
                await worker.stop()
            
            # Remove from collections
            self.workers.pop(worker_id, None)
            self.worker_health.pop(worker_id, None)
            
            # Create replacement worker
            new_worker_id = f"{worker_id}-replacement-{int(time.time())}"
            await self._create_worker(new_worker_id, worker_config.worker_type)
            
            logger.info(f"✅ Replaced worker {worker_id} with {new_worker_id}")
            
        except Exception as e:
            logger.error(f"❌ Failed to replace unhealthy worker {worker_id}: {e}")

    async def _auto_scaler(self) -> None:
        """Automatic worker scaling based on load"""
        while not self.shutdown_event.is_set():
            try:
                # Calculate current load
                current_load = await self._calculate_pool_load()
                
                # Determine scaling action
                scaling_action = await self.scaling_manager.analyze_scaling_need(
                    current_load, self.metrics, len(self.workers)
                )
                
                if scaling_action.should_scale:
                    await self.scale_workers(scaling_action.target_workers)
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"❌ Auto scaler error: {e}")
                await asyncio.sleep(120)

    async def _calculate_pool_load(self) -> float:
        """Calculate current pool load percentage"""
        try:
            if not self.workers:
                return 0.0
            
            total_capacity = len(self.workers) * 5  # Assuming 5 tasks per worker
            current_usage = len(self.active_assignments) + self.metrics.queue_size
            
            return min(1.0, current_usage / total_capacity)
            
        except Exception as e:
            logger.error(f"❌ Failed to calculate pool load: {e}")
            return 0.0

    async def _update_pool_metrics(self) -> None:
        """Update pool performance metrics"""
        try:
            # Count workers by status
            status_counts = defaultdict(int)
            for worker in self.workers.values():
                worker_status = await worker.get_status()
                status_counts[worker_status.get('status', 'unknown')] += 1
            
            # Update metrics
            self.metrics.total_workers = len(self.workers)
            self.metrics.active_workers = status_counts.get('running', 0)
            self.metrics.idle_workers = status_counts.get('idle', 0)
            self.metrics.busy_workers = status_counts.get('busy', 0)
            self.metrics.overloaded_workers = status_counts.get('overloaded', 0)
            self.metrics.error_workers = status_counts.get('error', 0)
            self.metrics.queue_size = self.task_queue.qsize()
            
            # Calculate uptime
            uptime = datetime.utcnow() - self.startup_time
            self.metrics.uptime_hours = uptime.total_seconds() / 3600
            
            # Calculate throughput
            if self.metrics.uptime_hours > 0:
                self.metrics.throughput_per_second = self.metrics.total_tasks_processed / (self.metrics.uptime_hours * 3600)
            
            # Calculate average response time
            if self.completed_assignments:
                recent_assignments = list(self.completed_assignments)[-100:]  # Last 100 tasks
                durations = [a.duration_seconds for a in recent_assignments if a.duration_seconds]
                if durations:
                    self.metrics.average_response_time = statistics.mean(durations)
            
        except Exception as e:
            logger.error(f"❌ Failed to update pool metrics: {e}")

    async def _check_pool_health(self) -> None:
        """Check overall pool health"""
        try:
            healthy_workers = sum(1 for h in self.worker_health.values() if h['status'] == 'healthy')
            total_workers = len(self.workers)
            
            if total_workers == 0:
                self.status = PoolStatus.SHUTDOWN
            elif healthy_workers / total_workers < 0.5:
                self.status = PoolStatus.DEGRADED
            elif self.metrics.queue_size > self.config.max_queue_size * 0.9:
                self.status = PoolStatus.OVERLOADED
            else:
                self.status = PoolStatus.ACTIVE
                
        except Exception as e:
            logger.error(f"❌ Pool health check failed: {e}")

    async def _add_workers(self, count: int) -> None:
        """Add new workers to the pool"""
        try:
            for i in range(count):
                worker_id = f"{self.pool_id}-worker-{len(self.workers) + i + 1}"
                worker_type = self.config.worker_types[i % len(self.config.worker_types)]
                await self._create_worker(worker_id, worker_type)
                
        except Exception as e:
            logger.error(f"❌ Failed to add workers: {e}")

    async def _remove_workers(self, count: int) -> None:
        """Remove workers from the pool"""
        try:
            # Select workers to remove (prefer idle workers)
            workers_to_remove = []
            
            for worker_id, worker in self.workers.items():
                if len(workers_to_remove) >= count:
                    break
                
                status = await worker.get_status()
                if status.get('status') == 'idle' and status.get('active_tasks', 0) == 0:
                    workers_to_remove.append(worker_id)
            
            # Remove selected workers
            for worker_id in workers_to_remove:
                worker = self.workers.get(worker_id)
                if worker:
                    await worker.stop()
                    self.workers.pop(worker_id, None)
                    self.worker_configs.pop(worker_id, None)
                    self.worker_health.pop(worker_id, None)
                    
        except Exception as e:
            logger.error(f"❌ Failed to remove workers: {e}")

    async def _stop_all_workers(self) -> None:
        """Stop all workers in the pool"""
        try:
            stop_tasks = []
            for worker in self.workers.values():
                stop_tasks.append(worker.stop())
            
            if stop_tasks:
                await asyncio.gather(*stop_tasks, return_exceptions=True)
            
            self.workers.clear()
            self.worker_configs.clear()
            self.worker_health.clear()
            
        except Exception as e:
            logger.error(f"❌ Failed to stop all workers: {e}")

    async def _wait_for_active_tasks(self) -> None:
        """Wait for all active tasks to complete"""
        while self.active_assignments:
            await asyncio.sleep(1)

    def _get_priority_value(self, priority: TaskPriority) -> int:
        """
Convert priority enum to integer value for queue"""
        priority_values = {
            TaskPriority.CRITICAL: 1,
            TaskPriority.HIGH: 2,
            TaskPriority.MEDIUM: 3,
            TaskPriority.LOW: 4,
            TaskPriority.BACKGROUND: 5
        }
        return priority_values.get(priority, 3)

    async def _validate_task(self, task: CrawlerTask) -> bool:
        """
Validate task before queueing"""
        try:
            # Basic validation
            if not task.task_id or not task.target_url:
                return False
                
            # Access control
            if not await self.access_control.validate_task_access(task):
                return False
                
            return True
            
        except Exception as e:
            logger.error(f"❌ Task validation failed: {e}")
            return False

    async def _calculate_task_priority(self, task: CrawlerTask) -> TaskPriority:
        """Calculate intelligent task priority"""
        try:
            # Default priority
            priority = TaskPriority.MEDIUM
            
            # Priority factors
            if task.metadata.get('urgent', False):
                priority = TaskPriority.CRITICAL
            elif task.metadata.get('user_tier') == 'premium':
                priority = TaskPriority.HIGH
            elif task.metadata.get('background_task', False):
                priority = TaskPriority.BACKGROUND
            
            return priority
            
        except Exception as e:
            logger.error(f"❌ Priority calculation failed: {e}")
            return TaskPriority.MEDIUM

    async def _get_queue_position(self, task_id: str) -> int:
        """Get position of task in queue"""
        try:
            position = 0
            temp_queue = []
            
            # Extract all items to find position
            while not self.task_queue.empty():
                item = await self.task_queue.get()
                temp_queue.append(item)
                
                if item[2].task_id == task_id:
                    break
                position += 1
            
            # Restore queue
            for item in temp_queue:
                await self.task_queue.put(item)
            
            return position
            
        except Exception as e:
            logger.error(f"❌ Failed to get queue position: {e}")
            return -1

    async def _estimate_start_time(self, queue_position: int) -> Optional[str]:
        """Estimate when task will start"""
        try:
            if queue_position < 0:
                return None
            
            # Calculate based on average task duration and available workers
            avg_duration = self.metrics.average_response_time or 60  # Default 1 minute
            available_workers = max(1, self.metrics.idle_workers)
            
            estimated_seconds = (queue_position * avg_duration) / available_workers
            estimated_time = datetime.utcnow() + timedelta(seconds=estimated_seconds)
            
            return estimated_time.isoformat()
            
        except Exception as e:
            logger.error(f"❌ Failed to estimate start time: {e}")
            return None

    async def _estimate_completion_time(self, assignment: TaskAssignment) -> Optional[str]:
        """Estimate when task will complete"""
        try:
            if not assignment.started_at:
                return None
            
            # Calculate based on average task duration
            avg_duration = self.metrics.average_response_time or 300  # Default 5 minutes
            elapsed = (datetime.utcnow() - assignment.started_at).total_seconds()
            remaining = max(0, avg_duration - elapsed)
            
            estimated_time = datetime.utcnow() + timedelta(seconds=remaining)
            return estimated_time.isoformat()
            
        except Exception as e:
            logger.error(f"❌ Failed to estimate completion time: {e}")
            return None

    async def _metrics_collector(self) -> None:
        """Collect and aggregate metrics"""
        while not self.shutdown_event.is_set():
            try:
                # Collect worker metrics
                for worker_id, worker in self.workers.items():
                    status = await worker.get_status()
                    metrics = status.get('metrics', {})
                    
                    # Store metrics for analysis
                    self.worker_statistics[worker_id]['cpu_usage'].append(metrics.get('cpu_usage_percent', 0))
                    self.worker_statistics[worker_id]['memory_usage'].append(metrics.get('memory_usage_mb', 0))
                    self.worker_statistics[worker_id]['throughput'].append(metrics.get('throughput_per_hour', 0))
                    
                    # Keep only recent data
                    for metric_list in self.worker_statistics[worker_id].values():
                        if len(metric_list) > 100:
                            metric_list.pop(0)
                
                await asyncio.sleep(60)  # Collect every minute
                
            except Exception as e:
                logger.error(f"❌ Metrics collector error: {e}")
                await asyncio.sleep(120)
