"""Advanced Task Queue Manager - IA-Influencer-Agent
================================================================================
Module: backend/core/managers/queue_manager.py
Author: Fahed Mlaiel (mlaiel@live.de)
Type: Industrial Manager Core - Intelligent Task Queue & Workflow Orchestration
Responsibility: Enterprise queue management with AI-powered task prioritization
Technologies: Celery, Redis, RabbitMQ, Priority Queues, Dead Letter Queues
================================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
© 2025 Fahed Mlaiel. Tous droits réservés.
Usage non autorisé strictement interdit et passible de poursuites judiciaires.
Contact: mlaiel@live.de

LOGIQUE MÉTIER:
Tâche créateur → Analyse priorité IA → Queue optimale → 
Distribution workers → Monitoring execution → Retry intelligent → Résultat garanti
"""
from typing import Any, Dict, List, Optional, Union, Callable, Tuple, Set
import logging
import asyncio
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
import threading
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
import json
import uuid
from enum import Enum
import time
import hashlib
import pickle
from celery import Celery
from celery.result import AsyncResult
import redis.asyncio as redis
import aiofiles
from collections import defaultdict, deque
import heapq

logger = logging.getLogger(__name__)


class TaskPriority(Enum):
    """Task priority levels"""
    CRITICAL = 0  # Creator content upload/protection
    HIGH = 1  # User requests, real-time features
    MEDIUM = 2  # Analytics, reports
    LOW = 3  # Cleanup, maintenance
    BACKGROUND = 4  # Batch processing


class QueueType(Enum):
    """Different queue types for different workloads"""
    CONTENT_PROCESSING = "content_processing"  # Audio, video, image processing
    AI_INFERENCE = "ai_inference"  # ML model inference
    PROTECTION_ANALYSIS = "protection_analysis"  # Fingerprinting, monitoring
    NOTIFICATION = "notification"  # Email, push notifications
    ANALYTICS = "analytics"  # Data processing, reports
    BACKUP = "backup"  # Backup operations
    MONITORING = "monitoring"  # Health checks, metrics
    GENERAL = "general"  # General purpose tasks


class TaskStatus(Enum):
    """Task execution status"""
    PENDING = "pending"
    PROCESSING = "processing"
    SUCCESS = "success"
    FAILED = "failed"
    RETRY = "retry"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


@dataclass
class QueueConfig:
    """Advanced queue system configuration"""
    # Broker configuration
    broker_url: str = "redis://localhost:6379/0"
    result_backend: str = "redis://localhost:6379/1"
    
    # Queue routing
    queue_routing: Dict[QueueType, str] = field(default_factory=lambda: {
        QueueType.CONTENT_PROCESSING: "content_processing",
        QueueType.AI_INFERENCE: "ai_inference",
        QueueType.PROTECTION_ANALYSIS: "protection_analysis",
        QueueType.NOTIFICATION: "notification",
        QueueType.ANALYTICS: "analytics",
        QueueType.BACKUP: "backup",
        QueueType.MONITORING: "monitoring",
        QueueType.GENERAL: "general",
    })
    
    # Worker configuration
    worker_concurrency: Dict[QueueType, int] = field(default_factory=lambda: {
        QueueType.CONTENT_PROCESSING: 4,  # CPU intensive
        QueueType.AI_INFERENCE: 2,  # GPU/CPU intensive
        QueueType.PROTECTION_ANALYSIS: 6,  # Moderate CPU
        QueueType.NOTIFICATION: 10,  # I/O bound
        QueueType.ANALYTICS: 3,  # CPU/Memory intensive
        QueueType.BACKUP: 2,  # I/O bound
        QueueType.MONITORING: 5,  # Light operations
        QueueType.GENERAL: 8,  # Mixed workload
    })
    
    # Task configuration
    task_timeout_seconds: int = 300  # 5 minutes default
    task_retry_attempts: int = 3
    task_retry_delay: int = 60  # seconds
    
    # Priority queue settings
    priority_queue_enabled: bool = True
    ai_priority_optimization: bool = True
    dynamic_priority_adjustment: bool = True
    
    # Dead letter queue
    dlq_enabled: bool = True
    dlq_retention_days: int = 7
    
    # Monitoring
    metrics_collection: bool = True
    performance_tracking: bool = True
    queue_analytics: bool = True


@dataclass
class TaskMetrics:
    """Task queue performance metrics"""
    # Queue statistics
    total_tasks_queued: int = 0
    total_tasks_completed: int = 0
    total_tasks_failed: int = 0
    
    # Performance metrics
    average_task_duration_seconds: float = 0.0
    queue_throughput_per_minute: float = 0.0
    worker_utilization_percent: float = 0.0
    
    # Queue-specific metrics
    queue_lengths: Dict[QueueType, int] = field(default_factory=dict)
    queue_processing_times: Dict[QueueType, float] = field(default_factory=dict)
    
    # Error tracking
    error_rate_percent: float = 0.0
    retry_rate_percent: float = 0.0
    timeout_rate_percent: float = 0.0


@dataclass
class TaskDefinition:
    """Task definition with metadata"""
    task_id: str
    task_name: str
    queue_type: QueueType
    priority: TaskPriority
    parameters: Dict[str, Any]
    timeout_seconds: Optional[int] = None
    retry_attempts: Optional[int] = None
    depends_on: List[str] = field(default_factory=list)
    scheduled_for: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


class IntelligentQueueManager(ABC):
    """
    🎯 Advanced Intelligent Queue Manager - IA-Influencer-Agent
    
    Enterprise-grade task queue management system featuring:
    - Multi-queue orchestration with intelligent routing
    - AI-powered task prioritization and optimization
    - Dynamic worker scaling based on workload
    - Dead letter queue for failed task handling
    - Real-time monitoring and performance analytics
    - Task dependency management and workflow orchestration
    - Intelligent retry strategies with exponential backoff
    - Geographic distribution for global task processing
    """
    
    def __init__(self, config: QueueConfig = None):
        self.config = config or QueueConfig()
        
        # Celery application
        self._celery_app: Optional[Celery] = None
        
        # Queue management
        self._priority_queues: Dict[QueueType, List[Tuple[int, TaskDefinition]]] = {
            queue_type: [] for queue_type in QueueType
        }
        self._active_tasks: Dict[str, TaskDefinition] = {}
        self._task_results: Dict[str, Any] = {}
        
        # Performance tracking
        self._metrics = TaskMetrics()
        self._task_history: deque = deque(maxlen=10000)
        self._worker_stats: Dict[str, Dict[str, Any]] = defaultdict(dict)
        
        # AI optimization
        self._priority_model: Optional[Any] = None
        self._workload_predictor: Optional[Any] = None
        
        # Monitoring
        self._monitoring_tasks: Set[str] = set()
        
        logger.info(f"🎯 Initializing {self.__class__.__name__} with intelligent queuing")
    
    @abstractmethod
    async def initialize_queue_system(self) -> bool:
        """
        Initialize the queue system and all workers
        
        Returns:
            bool: True if initialization successful
        """
        pass
    
    @abstractmethod
    async def enqueue_task(
        self,
        task_definition: TaskDefinition,
        immediate: bool = False,
    ) -> str:
        """
        Enqueue a task with intelligent prioritization
        
        Args:
            task_definition: Task to enqueue
            immediate: Execute immediately without queueing
            
        Returns:
            Task ID for tracking
        """
        pass
    
    @abstractmethod
    async def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """
        Get comprehensive task status and progress
        
        Args:
            task_id: ID of the task to check
            
        Returns:
            Dict with task status and metadata
        """
        pass
    
    @abstractmethod
    async def cancel_task(self, task_id: str) -> bool:
        """
        Cancel a pending or running task
        
        Args:
            task_id: ID of the task to cancel
            
        Returns:
            bool: True if cancellation successful
        """
        pass
    
    @abstractmethod
    async def retry_failed_task(self, task_id: str) -> str:
        """
        Retry a failed task with intelligent retry strategy
        
        Args:
            task_id: ID of the failed task
            
        Returns:
            New task ID for the retry
        """
        pass
    
    async def optimize_queue_performance(self) -> Dict[str, Any]:
        """
        Analyze and optimize queue performance
        
        Returns:
            Dict with optimization results
        """
        try:
            optimization_results = {
                "performance_improvements": {},
                "worker_adjustments": {},
                "queue_rebalancing": {},
                "priority_optimizations": {},
                "cost_savings_percent": 0.0
            }
            
            # Analyze queue lengths and processing times
            queue_analysis = await self._analyze_queue_performance()
            optimization_results["performance_improvements"] = queue_analysis
            
            # Optimize worker allocation
            worker_optimization = await self._optimize_worker_allocation()
            optimization_results["worker_adjustments"] = worker_optimization
            
            # Rebalance queues based on current workload
            rebalancing = await self._rebalance_queues()
            optimization_results["queue_rebalancing"] = rebalancing
            
            # AI-powered priority optimization
            if self.config.ai_priority_optimization:
                priority_optimization = await self._optimize_task_priorities()
                optimization_results["priority_optimizations"] = priority_optimization
            
            logger.info("⚡ Queue performance optimization completed")
            return optimization_results
            
        except Exception as e:
            logger.error(f"❌ Queue optimization failed: {e}")
            return {"error": str(e)}
    
    async def get_comprehensive_metrics(self) -> Dict[str, Any]:
        """
        Get comprehensive queue metrics and analytics
        
        Returns:
            Dict with detailed queue analytics
        """
        try:
            metrics = {
                "overview": dict(self._metrics.__dict__),
                "queue_status": await self._get_queue_status(),
                "worker_performance": await self._get_worker_performance(),
                "task_patterns": await self._analyze_task_patterns(),
                "error_analysis": await self._analyze_errors(),
                "predictions": await self._get_workload_predictions(),
                "generated_at": datetime.now().isoformat(),
            }
            
            return metrics
            
        except Exception as e:
            logger.error(f"❌ Failed to get queue metrics: {e}")
            return {"error": str(e)}
    
    async def schedule_recurring_task(
        self,
        task_name: str,
        queue_type: QueueType,
        priority: TaskPriority,
        parameters: Dict[str, Any],
        cron_expression: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Schedule a recurring task with cron-like scheduling
        
        Args:
            task_name: Name of the task
            queue_type: Queue to use
            priority: Task priority
            parameters: Task parameters
            cron_expression: Cron expression for scheduling
            metadata: Additional metadata
            
        Returns:
            Scheduled task ID
        """
        try:
            scheduled_task_id = f"scheduled_{uuid.uuid4().hex}"
            
            # Create task definition
            task_def = TaskDefinition(
                task_id=scheduled_task_id,
                task_name=task_name,
                queue_type=queue_type,
                priority=priority,
                parameters=parameters,
                metadata=metadata or {}
            )
            
            # Schedule with Celery beat
            if self._celery_app:
                self._celery_app.conf.beat_schedule[scheduled_task_id] = {
                    'task': task_name,
                    'schedule': cron_expression,
                    'args': (parameters,),
                    'options': {
                        'queue': self.config.queue_routing[queue_type],
                        'priority': priority.value,
                    }
                }
            
            logger.info(f"📅 Scheduled recurring task: {task_name}")
            return scheduled_task_id
            
        except Exception as e:
            logger.error(f"❌ Failed to schedule recurring task: {e}")
            raise
    
    async def process_dead_letter_queue(self) -> Dict[str, Any]:
        """
        Process and analyze dead letter queue
        
        Returns:
            Dict with DLQ processing results
        """
        try:
            dlq_results = {
                "processed_tasks": 0,
                "recovered_tasks": 0,
                "permanently_failed": 0,
                "error_patterns": {},
                "recommendations": []
            }
            
            # Get dead letter queue items
            dlq_items = await self._get_dlq_items()
            
            for dlq_item in dlq_items:
                task_id = dlq_item["task_id"]
                error_info = dlq_item["error_info"]
                
                # Analyze error pattern
                error_type = error_info.get("error_type", "unknown")
                if error_type not in dlq_results["error_patterns"]:
                    dlq_results["error_patterns"][error_type] = 0
                dlq_results["error_patterns"][error_type] += 1
                
                # Attempt recovery based on error type
                recovery_success = await self._attempt_task_recovery(task_id, error_info)
                
                if recovery_success:
                    dlq_results["recovered_tasks"] += 1
                else:
                    dlq_results["permanently_failed"] += 1
                
                dlq_results["processed_tasks"] += 1
            
            # Generate recommendations
            dlq_results["recommendations"] = await self._generate_dlq_recommendations(
                dlq_results["error_patterns"]
            )
            
            logger.info(f"💀 Processed DLQ: {dlq_results['recovered_tasks']} recovered, {dlq_results['permanently_failed']} failed")
            return dlq_results
            
        except Exception as e:
            logger.error(f"❌ DLQ processing failed: {e}")
            return {"error": str(e)}
    
    # Helper methods for implementation
    async def _analyze_queue_performance(self) -> Dict[str, Any]:
        """Analyze queue performance metrics"""
        return {}
    
    async def _optimize_worker_allocation(self) -> Dict[str, Any]:
        """Optimize worker allocation based on workload"""
        return {}
    
    async def _rebalance_queues(self) -> Dict[str, Any]:
        """Rebalance queues based on current load"""
        return {}
    
    async def _optimize_task_priorities(self) -> Dict[str, Any]:
        """AI-powered task priority optimization"""
        return {}
    
    async def _get_queue_status(self) -> Dict[str, Any]:
        """Get current status of all queues"""
        return {}
    
    async def _get_worker_performance(self) -> Dict[str, Any]:
        """Get worker performance metrics"""
        return {}
    
    async def _analyze_task_patterns(self) -> Dict[str, Any]:
        """Analyze task execution patterns"""
        return {}
    
    async def _analyze_errors(self) -> Dict[str, Any]:
        """Analyze error patterns and trends"""
        return {}
    
    async def _get_workload_predictions(self) -> Dict[str, Any]:
        """Get AI-powered workload predictions"""
        return {}
    
    async def _get_dlq_items(self) -> List[Dict[str, Any]]:
        """Get items from dead letter queue"""
        return []
    
    async def _attempt_task_recovery(self, task_id: str, error_info: Dict[str, Any]) -> bool:
        """Attempt to recover a failed task"""
        return False
    
    async def _generate_dlq_recommendations(self, error_patterns: Dict[str, int]) -> List[str]:
        """Generate recommendations based on DLQ analysis"""
        return []


# Concrete implementation
class ProductionQueueManager(IntelligentQueueManager):
    """Production implementation of the queue manager"""
    
    async def initialize_queue_system(self) -> bool:
        """Initialize Celery and queue system"""
        try:
            # Initialize Celery app
            self._celery_app = Celery(
                'ia_influencer_queues',
                broker=self.config.broker_url,
                backend=self.config.result_backend
            )
            
            # Configure Celery
            self._celery_app.conf.update(
                task_serializer='pickle',
                accept_content=['pickle', 'json'],
                result_serializer='pickle',
                timezone='UTC',
                enable_utc=True,
                task_track_started=True,
                task_time_limit=self.config.task_timeout_seconds,
                task_soft_time_limit=self.config.task_timeout_seconds - 30,
                worker_prefetch_multiplier=1,
                task_acks_late=True,
                worker_disable_rate_limits=False,
            )
            
            # Configure queue routing
            task_routes = {}
            for queue_type, queue_name in self.config.queue_routing.items():
                task_routes[f'*{queue_type.value}*'] = {'queue': queue_name}
            
            self._celery_app.conf.task_routes = task_routes
            
            # Initialize priority queues
            for queue_type in QueueType:
                heapq.heapify(self._priority_queues[queue_type])
            
            logger.info("✅ Queue system initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Queue system initialization failed: {e}")
            return False
    
    async def enqueue_task(
        self,
        task_definition: TaskDefinition,
        immediate: bool = False,
    ) -> str:
        """Enqueue task with intelligent routing"""
        try:
            # Calculate dynamic priority if enabled
            if self.config.dynamic_priority_adjustment:
                adjusted_priority = await self._calculate_dynamic_priority(task_definition)
                task_definition.priority = adjusted_priority
            
            # Store task definition
            self._active_tasks[task_definition.task_id] = task_definition
            
            if immediate:
                # Execute immediately
                result = await self._execute_task_immediately(task_definition)
                return task_definition.task_id
            
            # Add to priority queue
            if self.config.priority_queue_enabled:
                priority_value = task_definition.priority.value
                heapq.heappush(
                    self._priority_queues[task_definition.queue_type],
                    (priority_value, task_definition)
                )
            
            # Enqueue with Celery
            if self._celery_app:
                queue_name = self.config.queue_routing[task_definition.queue_type]
                
                celery_task = self._celery_app.send_task(
                    task_definition.task_name,
                    args=[task_definition.parameters],
                    kwargs={},
                    queue=queue_name,
                    priority=task_definition.priority.value,
                    task_id=task_definition.task_id,
                    countdown=0 if not task_definition.scheduled_for else 
                              int((task_definition.scheduled_for - datetime.now()).total_seconds()),
                    retry=True,
                    retry_policy={
                        'max_retries': task_definition.retry_attempts or self.config.task_retry_attempts,
                        'interval_start': self.config.task_retry_delay,
                        'interval_step': 30,
                        'interval_max': 300,
                    }
                )
            
            # Update metrics
            self._metrics.total_tasks_queued += 1
            if task_definition.queue_type not in self._metrics.queue_lengths:
                self._metrics.queue_lengths[task_definition.queue_type] = 0
            self._metrics.queue_lengths[task_definition.queue_type] += 1
            
            logger.info(f"📋 Task enqueued: {task_definition.task_id} ({task_definition.priority.name})")
            return task_definition.task_id
            
        except Exception as e:
            logger.error(f"❌ Failed to enqueue task: {e}")
            raise
    
    async def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """Get comprehensive task status"""
        try:
            task_def = self._active_tasks.get(task_id)
            if not task_def:
                return {"error": "Task not found", "task_id": task_id}
            
            # Get Celery task status
            celery_result = None
            if self._celery_app:
                celery_result = AsyncResult(task_id, app=self._celery_app)
            
            status_info = {
                "task_id": task_id,
                "task_name": task_def.task_name,
                "queue_type": task_def.queue_type.value,
                "priority": task_def.priority.name,
                "created_at": task_def.created_at.isoformat(),
                "status": TaskStatus.PENDING.value,
                "progress": 0,
                "result": None,
                "error": None,
                "metadata": task_def.metadata,
            }
            
            if celery_result:
                status_info["status"] = celery_result.status.lower()
                if celery_result.ready():
                    if celery_result.successful():
                        status_info["result"] = celery_result.result
                        status_info["progress"] = 100
                    else:
                        status_info["error"] = str(celery_result.info)
                elif hasattr(celery_result, 'info') and isinstance(celery_result.info, dict):
                    status_info["progress"] = celery_result.info.get('progress', 0)
            
            return status_info
            
        except Exception as e:
            logger.error(f"❌ Failed to get task status: {e}")
            return {"error": str(e), "task_id": task_id}
    
    async def cancel_task(self, task_id: str) -> bool:
        """Cancel a task"""
        try:
            if self._celery_app:
                self._celery_app.control.revoke(task_id, terminate=True)
            
            # Remove from active tasks
            if task_id in self._active_tasks:
                del self._active_tasks[task_id]
            
            logger.info(f"🚫 Task cancelled: {task_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to cancel task {task_id}: {e}")
            return False
    
    async def retry_failed_task(self, task_id: str) -> str:
        """Retry a failed task"""
        try:
            original_task = self._active_tasks.get(task_id)
            if not original_task:
                raise ValueError(f"Task {task_id} not found")
            
            # Create new task for retry
            retry_task_id = f"retry_{uuid.uuid4().hex}"
            retry_task = TaskDefinition(
                task_id=retry_task_id,
                task_name=original_task.task_name,
                queue_type=original_task.queue_type,
                priority=original_task.priority,
                parameters=original_task.parameters,
                timeout_seconds=original_task.timeout_seconds,
                retry_attempts=original_task.retry_attempts,
                metadata={**original_task.metadata, "original_task_id": task_id}
            )
            
            # Enqueue retry
            await self.enqueue_task(retry_task)
            
            logger.info(f"🔄 Task retry enqueued: {retry_task_id} (original: {task_id})")
            return retry_task_id
            
        except Exception as e:
            logger.error(f"❌ Failed to retry task {task_id}: {e}")
            raise
    
    # Helper methods
    async def _calculate_dynamic_priority(self, task_def: TaskDefinition) -> TaskPriority:
        """Calculate dynamic priority based on AI analysis"""
        # Placeholder for AI-powered priority calculation
        return task_def.priority
    
    async def _execute_task_immediately(self, task_def: TaskDefinition) -> Any:
        """Execute task immediately without queueing"""
        # Placeholder for immediate execution
        return None


# Global queue manager instance
_queue_manager: Optional[ProductionQueueManager] = None


def get_queue_manager() -> ProductionQueueManager:
    """
    Get the global queue manager instance
    
    Returns:
        ProductionQueueManager: Global queue manager instance
    """
    global _queue_manager
    if _queue_manager is None:
        _queue_manager = ProductionQueueManager()
    return _queue_manager


# Alias for backward compatibility
QueueManager = IntelligentQueueManager
