"""
Priority Scheduler Module
========================

Advanced priority-based scheduling system for crawler operations.
Implements intelligent task prioritization with machine learning optimization.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

WARNING: This code is protected by copyright law. Any unauthorized copying, 
distribution, or modification is strictly prohibited and will result in 
legal action. Contact mlaiel@live.de for licensing.

Expertise combinée:
- Lead Developer IA: Architecture intelligente et optimisations ML
- Backend Senior: Infrastructure robuste et scalabilité enterprise
- ML Engineer: Algorithmes d'apprentissage et modèles prédictifs
- DBA Expert: Gestion de données et optimisation des requêtes
- Sécurité: Protection et chiffrement des données sensibles
- Microservices: Architecture distribuée et communication inter-services
- Audio/Vidéo: Traitement multimédia et analyse de contenu
- DevOps: Déploiement, monitoring et infrastructure cloud
- IA Prompt Engineer: Optimisation des interactions et prompts

Business Logic Integration:
Creator content upload → AI priority analysis → Priority queue → 
Resource allocation → Execution optimization → Performance monitoring → 
SEO integration → Collaboration coordination → Multi-platform distribution
"""

import asyncio
import logging
import time
import heapq
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set, Callable, Tuple, Union
from dataclasses import dataclass, field, asdict
from enum import Enum, IntEnum
import json
import uuid
import threading
from collections import defaultdict, deque
import numpy as np
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class PriorityLevel(IntEnum):
    """Task priority levels with numeric values for heap operations."""
    CRITICAL = 0  # Creator content protection
    URGENT = 1    # Real-time violations
    HIGH = 2      # User requests
    NORMAL = 3    # Regular monitoring
    LOW = 4       # Background tasks
    MAINTENANCE = 5  # System maintenance


class SchedulingStrategy(Enum):
    """Scheduling strategy types."""
    PRIORITY_FIRST = "priority_first"
    ROUND_ROBIN = "round_robin"
    SHORTEST_JOB_FIRST = "shortest_job_first"
    DEADLINE_AWARE = "deadline_aware"
    LOAD_BALANCED = "load_balanced"
    ML_OPTIMIZED = "ml_optimized"


class TaskType(Enum):
    """Types of crawler tasks."""
    CONTENT_MONITORING = "content_monitoring"
    VIOLATION_DETECTION = "violation_detection"
    PLATFORM_CRAWLING = "platform_crawling"
    DATA_EXTRACTION = "data_extraction"
    ANALYSIS_PROCESSING = "analysis_processing"
    FINGERPRINT_GENERATION = "fingerprint_generation"
    COMPLIANCE_CHECK = "compliance_check"
    ALERT_PROCESSING = "alert_processing"


class TaskStatus(Enum):
    """Task execution status."""
    PENDING = "pending"
    SCHEDULED = "scheduled"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"
    RETRY = "retry"


@dataclass
class ResourceRequirements:
    """Task resource requirements."""
    cpu_cores: float = 1.0
    memory_mb: int = 512
    network_bandwidth: float = 1.0  # Mbps
    storage_mb: int = 100
    gpu_required: bool = False
    max_execution_time: int = 3600  # seconds


@dataclass
class TaskMetadata:
    """Task metadata and context."""
    creator_id: Optional[str] = None
    content_id: Optional[str] = None
    platform: Optional[str] = None
    content_type: Optional[str] = None
    business_impact: float = 0.5  # 0.0 to 1.0
    user_priority: bool = False
    collaboration_id: Optional[str] = None
    campaign_id: Optional[str] = None
    protection_level: Optional[str] = None
    seo_priority: float = 0.5
    tags: List[str] = field(default_factory=list)
    custom_attributes: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ScheduledTask:
    """Scheduled task with complete context."""
    task_id: str
    task_type: TaskType
    priority: PriorityLevel
    created_at: datetime
    scheduled_for: Optional[datetime] = None
    deadline: Optional[datetime] = None
    estimated_duration: int = 60  # seconds
    retry_count: int = 0
    max_retries: int = 3
    resource_requirements: ResourceRequirements = field(default_factory=ResourceRequirements)
    metadata: TaskMetadata = field(default_factory=TaskMetadata)
    status: TaskStatus = TaskStatus.PENDING
    parameters: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    callback_url: Optional[str] = None
    progress: float = 0.0
    result: Optional[Dict[str, Any]] = None
    error_details: Optional[str] = None
    execution_log: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """Post-initialization processing."""
        if not self.task_id:
            self.task_id = f"task_{uuid.uuid4().hex[:8]}"
        if not self.scheduled_for:
            self.scheduled_for = datetime.utcnow()
    
    @property
    def priority_score(self) -> float:
        """Calculate dynamic priority score."""
        base_score = self.priority.value * 1000
        
        # Business impact bonus
        impact_bonus = self.metadata.business_impact * 500
        
        # User priority bonus
        user_bonus = 200 if self.metadata.user_priority else 0
        
        # Time-based urgency
        time_urgency = 0
        if self.deadline:
            time_to_deadline = (self.deadline - datetime.utcnow()).total_seconds()
            if time_to_deadline > 0:
                # Higher urgency as deadline approaches
                time_urgency = max(0, 300 - (time_to_deadline / 60))
        
        # Retry penalty
        retry_penalty = self.retry_count * 50
        
        # SEO priority bonus
        seo_bonus = self.metadata.seo_priority * 100
        
        # Collaboration priority
        collab_bonus = 150 if self.metadata.collaboration_id else 0
        
        total_score = (
            base_score + impact_bonus + user_bonus + 
            time_urgency + seo_bonus + collab_bonus - retry_penalty
        )
        
        return max(0, total_score)
    
    @property
    def is_overdue(self) -> bool:
        """Check if task is overdue."""
        if not self.deadline:
            return False
        return datetime.utcnow() > self.deadline
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""



        return {
            'task_id': self.task_id,
            'task_type': self.task_type.value,
            'priority': self.priority.value,
            'priority_score': self.priority_score,
            'created_at': self.created_at.isoformat(),
            'scheduled_for': self.scheduled_for.isoformat() if self.scheduled_for else None,
            'deadline': self.deadline.isoformat() if self.deadline else None,
            'estimated_duration': self.estimated_duration,
            'retry_count': self.retry_count,
            'max_retries': self.max_retries,
            'status': self.status.value,
            'progress': self.progress,
            'is_overdue': self.is_overdue,
            'metadata': asdict(self.metadata),
            'resource_requirements': asdict(self.resource_requirements),
            'parameters': self.parameters,
            'dependencies': self.dependencies
        }


@dataclass
class SchedulerMetrics:
    """Scheduler performance metrics."""
    total_tasks_scheduled: int = 0
    total_tasks_completed: int = 0
    total_tasks_failed: int = 0
    total_tasks_cancelled: int = 0
    average_wait_time: float = 0.0
    average_execution_time: float = 0.0
    queue_length: int = 0
    active_tasks: int = 0
    success_rate: float = 0.0
    throughput_per_minute: float = 0.0
    resource_utilization: Dict[str, float] = field(default_factory=dict)
    priority_distribution: Dict[str, int] = field(default_factory=dict)
    last_updated: datetime = field(default_factory=datetime.utcnow)


class PriorityScheduler:
    """
    Advanced priority-based task scheduler for crawler operations.
    
    Features:
    - Multi-level priority queuing with dynamic scoring
    - Resource-aware scheduling
    - Deadline-aware prioritization
    - Load balancing across workers
    - ML-optimized scheduling
    - Business logic integration
    - Comprehensive monitoring
    """
    
    def __init__(
        self,
        max_concurrent_tasks: int = 50,
        strategy: SchedulingStrategy = SchedulingStrategy.ML_OPTIMIZED,
        enable_ml_optimization: bool = True,
        enable_deadline_enforcement: bool = True,
        enable_resource_monitoring: bool = True
    ):
        """Initialize priority scheduler."""
        self.max_concurrent_tasks = max_concurrent_tasks
        self.strategy = strategy
        self.enable_ml_optimization = enable_ml_optimization
        self.enable_deadline_enforcement = enable_deadline_enforcement
        self.enable_resource_monitoring = enable_resource_monitoring
        
        # Priority queue (min-heap based on priority score)
        self.task_queue: List[Tuple[float, float, ScheduledTask]] = []
        self.task_lookup: Dict[str, ScheduledTask] = {}
        self.active_tasks: Dict[str, ScheduledTask] = {}
        self.completed_tasks: deque = deque(maxlen=1000)
        
        # Resource tracking
        self.resource_pool = {
            'cpu_cores': 16.0,
            'memory_mb': 32768,
            'network_bandwidth': 1000.0,
            'storage_mb': 102400,
            'gpu_available': 2
        }
        self.allocated_resources = {
            'cpu_cores': 0.0,
            'memory_mb': 0,
            'network_bandwidth': 0.0,
            'storage_mb': 0,
            'gpu_allocated': 0
        }
        
        # Scheduling state
        self.running = False
        self.scheduler_task: Optional[asyncio.Task] = None
        self.lock = asyncio.Lock()
        self.metrics = SchedulerMetrics()
        
        # ML optimization
        self.ml_predictor = None
        if enable_ml_optimization:
            self._initialize_ml_predictor()
        
        # Event callbacks
        self.task_callbacks: Dict[str, List[Callable]] = defaultdict(list)
        
        # Configuration
        self.config = {
            'scheduling_interval': 1.0,  # seconds
            'metrics_update_interval': 10.0,  # seconds
            'deadline_check_interval': 5.0,  # seconds
            'resource_check_interval': 2.0,  # seconds
            'max_queue_size': 10000,
            'priority_boost_threshold': 300,  # seconds
            'overdue_penalty_multiplier': 2.0
        }
        
        logger.info(f"Priority scheduler initialized with strategy: {strategy.value}")
    
    def _initialize_ml_predictor(self) -> None:
        """Initialize ML predictor for scheduling optimization."""



        try:
            # Simple ML predictor for task execution time and success probability
            self.ml_predictor = {
                'execution_time_model': None,  # Would be trained model
                'success_probability_model': None,  # Would be trained model
                'features_history': deque(maxlen=1000),
                'performance_history': deque(maxlen=1000)
            }
            logger.info("ML predictor initialized for scheduling optimization")
        except Exception as e:
            logger.warning(f"Failed to initialize ML predictor: {e}")
            self.enable_ml_optimization = False
    
    async def schedule_task(
        self,
        task: ScheduledTask,
        immediate: bool = False
    ) -> str:
        """Schedule a task with priority-based queuing."""
        async with self.lock:
            try:
                # Validate task
                await self._validate_task(task)
                
                # Check queue capacity
                if len(self.task_queue) >= self.config['max_queue_size']:
                    raise ValueError("Task queue at maximum capacity")
                
                # Apply ML optimization if enabled
                if self.enable_ml_optimization and self.ml_predictor:
                    await self._apply_ml_optimization(task)
                
                # Calculate priority score
                priority_score = task.priority_score
                
                # Add timestamp for FIFO ordering among same priorities
                timestamp = time.time()
                
                # Add to queue
                heapq.heappush(
                    self.task_queue,
                    (priority_score, timestamp, task)
                )
                
                # Update lookup
                self.task_lookup[task.task_id] = task
                task.status = TaskStatus.SCHEDULED
                
                # Update metrics
                self.metrics.total_tasks_scheduled += 1
                self.metrics.queue_length = len(self.task_queue)
                
                # Log scheduling
                logger.info(
                    f"Task scheduled: {task.task_id} "
                    f"(priority={task.priority.name}, score={priority_score:.2f})"
                )
                
                # Trigger immediate processing if requested
                if immediate and not self.running:
                    await self._process_next_task()
                
                # Call scheduling callbacks
                await self._call_callbacks('scheduled', task)
                
                return task.task_id
                
            except Exception as e:
                logger.error(f"Failed to schedule task {task.task_id}: {e}")
                task.status = TaskStatus.FAILED
                task.error_details = str(e)
                raise
    
    async def _validate_task(self, task: ScheduledTask) -> None:
        """Validate task before scheduling."""
        # Check for duplicate task ID
        if task.task_id in self.task_lookup:
            raise ValueError(f"Task ID already exists: {task.task_id}")
        
        # Validate resource requirements
        if task.resource_requirements.cpu_cores > self.resource_pool['cpu_cores']:
            raise ValueError("Task requires more CPU cores than available")
        
        if task.resource_requirements.memory_mb > self.resource_pool['memory_mb']:
            raise ValueError("Task requires more memory than available")
        
        # Validate dependencies
        for dep_id in task.dependencies:
            if dep_id not in self.task_lookup and dep_id not in self.completed_tasks:
                raise ValueError(f"Unknown dependency: {dep_id}")
    
    async def _apply_ml_optimization(self, task: ScheduledTask) -> None:
        """Apply ML optimization to task parameters."""



        try:
            # Extract features for ML prediction
            features = {
                'task_type': task.task_type.value,
                'priority': task.priority.value,
                'estimated_duration': task.estimated_duration,
                'cpu_requirements': task.resource_requirements.cpu_cores,
                'memory_requirements': task.resource_requirements.memory_mb,
                'business_impact': task.metadata.business_impact,
                'current_queue_length': len(self.task_queue),
                'time_of_day': datetime.utcnow().hour,
                'day_of_week': datetime.utcnow().weekday()
            }
            
            # Predict execution time (simplified)
            if self.ml_predictor['execution_time_model']:
                predicted_time = self._predict_execution_time(features)
                if predicted_time > 0:
                    task.estimated_duration = int(predicted_time)
            
            # Store features for model training
            self.ml_predictor['features_history'].append(features)
            
        except Exception as e:
            logger.warning(f"ML optimization failed for task {task.task_id}: {e}")
    
    def _predict_execution_time(self, features: Dict[str, Any]) -> float:
        """Predict task execution time using ML model."""
        # Simplified heuristic-based prediction
        # In production, this would use a trained ML model
        base_time = features['estimated_duration']
        
        # Adjust based on task type
        type_multipliers = {
            'content_monitoring': 1.0,
            'violation_detection': 1.5,
            'platform_crawling': 2.0,
            'data_extraction': 1.2,
            'analysis_processing': 3.0,
            'fingerprint_generation': 2.5,
            'compliance_check': 1.8,
            'alert_processing': 0.8
        }
        
        multiplier = type_multipliers.get(features['task_type'], 1.0)
        
        # Adjust based on queue load
        load_factor = 1.0 + (features['current_queue_length'] / 100)
        
        return base_time * multiplier * load_factor
    
    async def start_scheduler(self) -> None:
        """Start the scheduler background process."""
        if self.running:
            logger.warning("Scheduler already running")
            return
        
        self.running = True
        
        # Start main scheduler loop
        self.scheduler_task = asyncio.create_task(self._scheduler_loop())
        
        # Start monitoring tasks
        asyncio.create_task(self._metrics_updater())
        asyncio.create_task(self._deadline_monitor())
        
        if self.enable_resource_monitoring:
            asyncio.create_task(self._resource_monitor())
        
        logger.info("Priority scheduler started")
    
    async def stop_scheduler(self) -> None:
        """Stop the scheduler gracefully."""
        self.running = False
        
        if self.scheduler_task:
            self.scheduler_task.cancel()
            try:
                await self.scheduler_task
            except asyncio.CancelledError:
                pass
        
        # Cancel all active tasks
        for task in list(self.active_tasks.values()):
            await self.cancel_task(task.task_id)
        
        logger.info("Priority scheduler stopped")
    
    async def _scheduler_loop(self) -> None:
        """Main scheduler loop."""
        while self.running:
            try:
                await self._process_next_task()
                await asyncio.sleep(self.config['scheduling_interval'])
                
            except Exception as e:
                logger.error(f"Scheduler loop error: {e}")
                await asyncio.sleep(1.0)
    
    async def _process_next_task(self) -> None:
        """Process the next task from the queue."""
        async with self.lock:
            # Check if we can process more tasks
            if len(self.active_tasks) >= self.max_concurrent_tasks:
                return
            
            # Check if queue is empty
            if not self.task_queue:
                return
            
            # Get next task
            while self.task_queue:
                _, _, task = heapq.heappop(self.task_queue)
                
                # Check if task is still valid
                if task.task_id not in self.task_lookup:
                    continue
                
                if task.status == TaskStatus.CANCELLED:
                    continue
                
                # Check dependencies
                if not await self._check_dependencies(task):
                    # Re-queue task
                    heapq.heappush(
                        self.task_queue,
                        (task.priority_score, time.time(), task)
                    )
                    break
                
                # Check resource availability
                if not await self._check_resource_availability(task):
                    # Re-queue task
                    heapq.heappush(
                        self.task_queue,
                        (task.priority_score, time.time(), task)
                    )
                    break
                
                # Start task execution
                await self._start_task_execution(task)
                break
            
            # Update queue metrics
            self.metrics.queue_length = len(self.task_queue)
            self.metrics.active_tasks = len(self.active_tasks)
    
    async def _check_dependencies(self, task: ScheduledTask) -> bool:
        """Check if task dependencies are satisfied."""
        for dep_id in task.dependencies:
            # Check if dependency is completed
            dep_completed = any(
                completed_task.task_id == dep_id 
                for completed_task in self.completed_tasks
            )
            
            if not dep_completed:
                # Check if dependency is still active or queued
                if dep_id in self.active_tasks or dep_id in self.task_lookup:
                    return False
                
                # Dependency not found - might be external
                logger.warning(f"Dependency not found: {dep_id} for task {task.task_id}")
        
        return True
    
    async def _check_resource_availability(self, task: ScheduledTask) -> bool:
        """Check if required resources are available."""
        req = task.resource_requirements
        
        # Check CPU availability
        if (self.allocated_resources['cpu_cores'] + req.cpu_cores > 
            self.resource_pool['cpu_cores']):
            return False
        
        # Check memory availability
        if (self.allocated_resources['memory_mb'] + req.memory_mb > 
            self.resource_pool['memory_mb']):
            return False
        
        # Check GPU availability if required
        if (req.gpu_required and 
            self.allocated_resources['gpu_allocated'] >= self.resource_pool['gpu_available']):
            return False
        
        return True
    
    async def _start_task_execution(self, task: ScheduledTask) -> None:
        """Start executing a task."""



        try:
            # Allocate resources
            await self._allocate_resources(task)
            
            # Update task status
            task.status = TaskStatus.RUNNING
            task.execution_log.append(f"Started execution at {datetime.utcnow().isoformat()}")
            
            # Move to active tasks
            self.active_tasks[task.task_id] = task
            del self.task_lookup[task.task_id]
            
            # Create execution task
            execution_task = asyncio.create_task(
                self._execute_task(task)
            )
            
            logger.info(f"Started executing task: {task.task_id}")
            
            # Call execution callbacks
            await self._call_callbacks('started', task)
            
        except Exception as e:
            logger.error(f"Failed to start task execution {task.task_id}: {e}")
            task.status = TaskStatus.FAILED
            task.error_details = str(e)
            await self._deallocate_resources(task)
    
    async def _execute_task(self, task: ScheduledTask) -> None:
        """Execute a task (placeholder for actual execution logic)."""



        try:
            start_time = time.time()
            
            # Simulate task execution
            # In real implementation, this would call the actual crawler/processor
            
            # Update progress periodically
            for progress in range(0, 101, 25):
                if task.status == TaskStatus.CANCELLED:
                    return
                
                task.progress = progress / 100.0
                await asyncio.sleep(task.estimated_duration / 10)  # Simulate work
            
            # Mark as completed
            execution_time = time.time() - start_time
            task.status = TaskStatus.COMPLETED
            task.progress = 1.0
            task.result = {
                'success': True,
                'execution_time': execution_time,
                'completed_at': datetime.utcnow().isoformat()
            }
            
            # Update metrics
            self.metrics.total_tasks_completed += 1
            
            logger.info(f"Task completed: {task.task_id} in {execution_time:.2f}s")
            
        except Exception as e:
            logger.error(f"Task execution failed {task.task_id}: {e}")
            task.status = TaskStatus.FAILED
            task.error_details = str(e)
            self.metrics.total_tasks_failed += 1
            
        finally:
            # Clean up
            await self._complete_task(task)
    
    async def _complete_task(self, task: ScheduledTask) -> None:
        """Complete task execution and cleanup."""
        async with self.lock:
            # Deallocate resources
            await self._deallocate_resources(task)
            
            # Move to completed tasks
            if task.task_id in self.active_tasks:
                del self.active_tasks[task.task_id]
                self.completed_tasks.append(task)
            
            # Call completion callbacks
            await self._call_callbacks('completed', task)
            
            # Update metrics
            self.metrics.active_tasks = len(self.active_tasks)
    
    async def _allocate_resources(self, task: ScheduledTask) -> None:
        """Allocate resources for task execution."""
        req = task.resource_requirements
        
        self.allocated_resources['cpu_cores'] += req.cpu_cores
        self.allocated_resources['memory_mb'] += req.memory_mb
        self.allocated_resources['network_bandwidth'] += req.network_bandwidth
        self.allocated_resources['storage_mb'] += req.storage_mb
        
        if req.gpu_required:
            self.allocated_resources['gpu_allocated'] += 1
    
    async def _deallocate_resources(self, task: ScheduledTask) -> None:
        """Deallocate resources after task completion."""
        req = task.resource_requirements
        
        self.allocated_resources['cpu_cores'] -= req.cpu_cores
        self.allocated_resources['memory_mb'] -= req.memory_mb
        self.allocated_resources['network_bandwidth'] -= req.network_bandwidth
        self.allocated_resources['storage_mb'] -= req.storage_mb
        
        if req.gpu_required:
            self.allocated_resources['gpu_allocated'] -= 1
        
        # Ensure no negative values
        for key in self.allocated_resources:
            self.allocated_resources[key] = max(0, self.allocated_resources[key])
    
    async def cancel_task(self, task_id: str) -> bool:
        """Cancel a scheduled or running task."""
        async with self.lock:
            # Check if task exists
            task = None
            
            if task_id in self.task_lookup:
                task = self.task_lookup[task_id]
                del self.task_lookup[task_id]
                
                # Remove from queue
                self.task_queue = [
                    (score, ts, t) for score, ts, t in self.task_queue 
                    if t.task_id != task_id
                ]
                heapq.heapify(self.task_queue)
                
            elif task_id in self.active_tasks:
                task = self.active_tasks[task_id]
                await self._deallocate_resources(task)
                del self.active_tasks[task_id]
            
            if task:
                task.status = TaskStatus.CANCELLED
                self.metrics.total_tasks_cancelled += 1
                
                # Call cancellation callbacks
                await self._call_callbacks('cancelled', task)
                
                logger.info(f"Task cancelled: {task_id}")
                return True
            
            return False
    
    async def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific task."""
        # Check queued tasks
        if task_id in self.task_lookup:
            return self.task_lookup[task_id].to_dict()
        
        # Check active tasks
        if task_id in self.active_tasks:
            return self.active_tasks[task_id].to_dict()
        
        # Check completed tasks
        for task in self.completed_tasks:
            if task.task_id == task_id:
                return task.to_dict()
        
        return None
    
    async def get_queue_status(self) -> Dict[str, Any]:
        """Get comprehensive queue status."""
        async with self.lock:
            # Calculate priority distribution
            priority_dist = defaultdict(int)
            for _, _, task in self.task_queue:
                priority_dist[task.priority.name] += 1
            
            # Calculate resource utilization
            resource_util = {}
            for resource, allocated in self.allocated_resources.items():
                if resource in self.resource_pool:
                    util_pct = (allocated / self.resource_pool[resource]) * 100
                    resource_util[resource] = round(util_pct, 2)
            
            return {
                'queue_length': len(self.task_queue),
                'active_tasks': len(self.active_tasks),
                'completed_tasks': len(self.completed_tasks),
                'max_concurrent_tasks': self.max_concurrent_tasks,
                'scheduler_running': self.running,
                'strategy': self.strategy.value,
                'priority_distribution': dict(priority_dist),
                'resource_utilization': resource_util,
                'metrics': asdict(self.metrics)
            }
    
    async def _metrics_updater(self) -> None:
        """Update scheduler metrics periodically."""
        while self.running:
            try:
                await self._update_metrics()
                await asyncio.sleep(self.config['metrics_update_interval'])
            except Exception as e:
                logger.error(f"Metrics update error: {e}")
                await asyncio.sleep(1.0)
    
    async def _update_metrics(self) -> None:
        """Update performance metrics."""
        # Calculate success rate
        total_completed = self.metrics.total_tasks_completed + self.metrics.total_tasks_failed
        if total_completed > 0:
            self.metrics.success_rate = (
                self.metrics.total_tasks_completed / total_completed
            ) * 100
        
        # Update resource utilization
        for resource, allocated in self.allocated_resources.items():
            if resource in self.resource_pool and self.resource_pool[resource] > 0:
                util_pct = (allocated / self.resource_pool[resource]) * 100
                self.metrics.resource_utilization[resource] = util_pct
        
        # Update priority distribution
        self.metrics.priority_distribution.clear()
        for _, _, task in self.task_queue:
            priority_name = task.priority.name
            self.metrics.priority_distribution[priority_name] = (
                self.metrics.priority_distribution.get(priority_name, 0) + 1
            )
        
        self.metrics.last_updated = datetime.utcnow()
    
    async def _deadline_monitor(self) -> None:
        """Monitor task deadlines and handle overdue tasks."""
        while self.running:
            try:
                await self._check_deadlines()
                await asyncio.sleep(self.config['deadline_check_interval'])
            except Exception as e:
                logger.error(f"Deadline monitor error: {e}")
                await asyncio.sleep(1.0)
    
    async def _check_deadlines(self) -> None:
        """Check for overdue tasks and apply penalties."""
        if not self.enable_deadline_enforcement:
            return
        
        current_time = datetime.utcnow()
        
        # Check queued tasks
        for _, _, task in self.task_queue:
            if task.deadline and current_time > task.deadline:
                if not task.is_overdue:
                    logger.warning(f"Task overdue: {task.task_id}")
                    # Apply priority boost for overdue tasks
                    task.metadata.business_impact *= self.config['overdue_penalty_multiplier']
        
        # Check active tasks
        for task in self.active_tasks.values():
            if task.deadline and current_time > task.deadline:
                logger.warning(f"Active task overdue: {task.task_id}")
    
    async def _resource_monitor(self) -> None:
        """Monitor resource usage and optimize allocation."""
        while self.running:
            try:
                await self._monitor_resources()
                await asyncio.sleep(self.config['resource_check_interval'])
            except Exception as e:
                logger.error(f"Resource monitor error: {e}")
                await asyncio.sleep(1.0)
    
    async def _monitor_resources(self) -> None:
        """Monitor and log resource usage."""
        # Log high resource utilization
        for resource, util_pct in self.metrics.resource_utilization.items():
            if util_pct > 90:
                logger.warning(f"High {resource} utilization: {util_pct:.1f}%")
    
    def add_callback(self, event_type: str, callback: Callable) -> None:
        """Add event callback."""
        self.task_callbacks[event_type].append(callback)
    
    async def _call_callbacks(self, event_type: str, task: ScheduledTask) -> None:
        """Call registered callbacks for an event."""
        for callback in self.task_callbacks.get(event_type, []):
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(task)
                else:
                    callback(task)
            except Exception as e:
                logger.error(f"Callback error for {event_type}: {e}")
    
    def get_metrics(self) -> SchedulerMetrics:
        """Get current scheduler metrics."""



        return self.metrics
    
    async def optimize_queue(self) -> None:
        """Optimize queue ordering based on current conditions."""
        if not self.enable_ml_optimization:
            return
        
        async with self.lock:
            # Re-calculate priority scores for all queued tasks
            updated_queue = []
            
            for _, _, task in self.task_queue:
                new_score = task.priority_score
                updated_queue.append((new_score, time.time(), task))
            
            # Rebuild heap with updated scores
            self.task_queue = updated_queue
            heapq.heapify(self.task_queue)
            
            logger.info("Queue optimized based on current conditions")


# Export main classes
__all__ = [
    'PriorityScheduler',
    'ScheduledTask',
    'PriorityLevel',
    'SchedulingStrategy',
    'TaskType',
    'TaskStatus',
    'ResourceRequirements',
    'TaskMetadata',
    'SchedulerMetrics'
]
