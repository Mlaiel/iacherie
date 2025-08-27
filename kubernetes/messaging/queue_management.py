"""
IA Influencer Agent - Queue Management System
Enterprise queue orchestration and monitoring for distributed task processing

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved - Unauthorized use prohibited

STRICT WARNING: This code is proprietary and confidential.
Any unauthorized use, reproduction, or distribution is strictly prohibited.
Legal action will be taken against violators.
Contact: mlaiel@live.de for licensing inquiries.

Team Specialties:
- Lead Dev IA + Backend Senior + ML Engineer + DBA + DevOps 
- Audio Processing + Security + Microservices + IA Prompt Engineering
"""

import asyncio
import logging
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Union

import aioredis
from pydantic import BaseModel, Field

from ...core.config import get_settings
from ...core.logging import get_logger
from ...monitoring.metrics_collector import MetricsCollector

logger = get_logger(__name__)
settings = get_settings()


class QueuePriority(str, Enum):
    """Queue priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class QueueType(str, Enum):
    """Queue types for different processing needs"""
    CONTENT_PROCESSING = "content_processing"
    FINGERPRINT_GENERATION = "fingerprint_generation"
    AI_ANALYSIS = "ai_analysis"
    ML_INFERENCE = "ml_inference"
    WEB_CRAWLING = "web_crawling"
    MONITORING = "monitoring"
    NOTIFICATIONS = "notifications"
    ALERTS = "alerts"
    REVENUE_CALCULATION = "revenue_calculation"
    PAYMENT_PROCESSING = "payment_processing"
    AUDIO_PROCESSING = "audio_processing"
    VIDEO_PROCESSING = "video_processing"
    IMAGE_PROCESSING = "image_processing"
    TEXT_ANALYSIS = "text_analysis"


class QueueStatus(str, Enum):
    """Queue operational status"""
    ACTIVE = "active"
    PAUSED = "paused"
    DRAINING = "draining"
    STOPPED = "stopped"
    ERROR = "error"


@dataclass
class QueueTask:
    """Represents a task in a queue"""
    id: str
    queue_name: str
    task_type: str
    payload: Dict[str, Any]
    priority: QueuePriority
    created_at: float
    scheduled_at: Optional[float] = None
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    retry_count: int = 0
    max_retries: int = 3
    timeout: Optional[int] = None
    metadata: Dict[str, Any] = None


class QueueConfiguration(BaseModel):
    """Configuration for a queue"""
    name: str = Field(..., description="Queue name")
    queue_type: QueueType = Field(..., description="Queue type")
    priority: QueuePriority = Field(default=QueuePriority.MEDIUM, description="Default priority")
    max_workers: int = Field(default=4, description="Maximum concurrent workers")
    min_workers: int = Field(default=1, description="Minimum workers")
    auto_scale: bool = Field(default=True, description="Enable auto-scaling")
    max_size: int = Field(default=10000, description="Maximum queue size")
    timeout: int = Field(default=300, description="Task timeout in seconds")
    retry_policy: Dict[str, Any] = Field(default_factory=dict, description="Retry policy")
    dead_letter_queue: bool = Field(default=True, description="Enable dead letter queue")
    monitoring: bool = Field(default=True, description="Enable monitoring")


class QueueStats(BaseModel):
    """Queue statistics"""
    name: str
    status: QueueStatus
    pending_tasks: int
    active_tasks: int
    completed_tasks: int
    failed_tasks: int
    retry_tasks: int
    workers_active: int
    workers_total: int
    avg_processing_time: float
    throughput_per_minute: float
    last_activity: float


class QueueManager:
    """
    Enterprise queue management system
    Handles distributed task queuing, processing, and monitoring
    """

    def __init__(self):
        self.redis_client: Optional[aioredis.Redis] = None
        self.queues: Dict[str, QueueConfiguration] = {}
        self.queue_stats: Dict[str, QueueStats] = {}
        self.workers: Dict[str, List[asyncio.Task]] = {}
        self.metrics_collector = MetricsCollector()
        
        # Queue monitoring
        self.monitoring_tasks: List[asyncio.Task] = []
        self.is_running = False

    async def initialize(self) -> None:
        """Initialize queue manager"""
        try:
            # Setup Redis connection
            self.redis_client = aioredis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True
            )
            
            # Create default queues
            await self._create_default_queues()
            
            # Start monitoring
            await self._start_monitoring()
            
            self.is_running = True
            logger.info("Queue manager initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize queue manager: {e}")
            raise

    async def _create_default_queues(self) -> None:
        """Create default queues for IA processing"""
        default_queues = [
            QueueConfiguration(
                name="ia.content.processing",
                queue_type=QueueType.CONTENT_PROCESSING,
                priority=QueuePriority.HIGH,
                max_workers=8,
                timeout=600,
                auto_scale=True
            ),
            QueueConfiguration(
                name="ia.fingerprint.generation",
                queue_type=QueueType.FINGERPRINT_GENERATION,
                priority=QueuePriority.HIGH,
                max_workers=6,
                timeout=300,
                auto_scale=True
            ),
            QueueConfiguration(
                name="ia.ai.analysis",
                queue_type=QueueType.AI_ANALYSIS,
                priority=QueuePriority.MEDIUM,
                max_workers=4,
                timeout=900,
                auto_scale=True
            ),
            QueueConfiguration(
                name="ia.ml.inference",
                queue_type=QueueType.ML_INFERENCE,
                priority=QueuePriority.MEDIUM,
                max_workers=6,
                timeout=180,
                auto_scale=True
            ),
            QueueConfiguration(
                name="ia.web.crawling",
                queue_type=QueueType.WEB_CRAWLING,
                priority=QueuePriority.MEDIUM,
                max_workers=10,
                timeout=120,
                auto_scale=True
            ),
            QueueConfiguration(
                name="ia.monitoring",
                queue_type=QueueType.MONITORING,
                priority=QueuePriority.LOW,
                max_workers=3,
                timeout=60,
                auto_scale=False
            ),
            QueueConfiguration(
                name="ia.notifications",
                queue_type=QueueType.NOTIFICATIONS,
                priority=QueuePriority.HIGH,
                max_workers=5,
                timeout=30,
                auto_scale=True
            ),
            QueueConfiguration(
                name="ia.alerts",
                queue_type=QueueType.ALERTS,
                priority=QueuePriority.CRITICAL,
                max_workers=3,
                timeout=15,
                auto_scale=False
            ),
            QueueConfiguration(
                name="ia.revenue.calculation",
                queue_type=QueueType.REVENUE_CALCULATION,
                priority=QueuePriority.MEDIUM,
                max_workers=2,
                timeout=300,
                auto_scale=False
            ),
            QueueConfiguration(
                name="ia.payment.processing",
                queue_type=QueueType.PAYMENT_PROCESSING,
                priority=QueuePriority.HIGH,
                max_workers=2,
                timeout=60,
                auto_scale=False
            ),
            QueueConfiguration(
                name="ia.audio.processing",
                queue_type=QueueType.AUDIO_PROCESSING,
                priority=QueuePriority.HIGH,
                max_workers=4,
                timeout=600,
                auto_scale=True
            ),
            QueueConfiguration(
                name="ia.video.processing",
                queue_type=QueueType.VIDEO_PROCESSING,
                priority=QueuePriority.MEDIUM,
                max_workers=2,
                timeout=1800,
                auto_scale=True
            ),
            QueueConfiguration(
                name="ia.image.processing",
                queue_type=QueueType.IMAGE_PROCESSING,
                priority=QueuePriority.MEDIUM,
                max_workers=4,
                timeout=300,
                auto_scale=True
            ),
            QueueConfiguration(
                name="ia.text.analysis",
                queue_type=QueueType.TEXT_ANALYSIS,
                priority=QueuePriority.MEDIUM,
                max_workers=6,
                timeout=120,
                auto_scale=True
            )
        ]
        
        for queue_config in default_queues:
            await self.create_queue(queue_config)

    async def create_queue(self, config: QueueConfiguration) -> bool:
        """Create a new queue"""
        try:
            # Store configuration
            self.queues[config.name] = config
            
            # Initialize Redis structures
            await self._initialize_queue_redis_structures(config.name)
            
            # Initialize stats
            self.queue_stats[config.name] = QueueStats(
                name=config.name,
                status=QueueStatus.ACTIVE,
                pending_tasks=0,
                active_tasks=0,
                completed_tasks=0,
                failed_tasks=0,
                retry_tasks=0,
                workers_active=0,
                workers_total=config.min_workers,
                avg_processing_time=0.0,
                throughput_per_minute=0.0,
                last_activity=time.time()
            )
            
            # Start workers
            await self._start_queue_workers(config.name, config.min_workers)
            
            logger.info(f"Created queue '{config.name}' with {config.min_workers} workers")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create queue '{config.name}': {e}")
            return False

    async def _initialize_queue_redis_structures(self, queue_name: str) -> None:
        """Initialize Redis structures for queue"""
        try:
            # Priority queues for different priority levels
            for priority in QueuePriority:
                await self.redis_client.delete(f"queue:{queue_name}:{priority}")
            
            # Active tasks set
            await self.redis_client.delete(f"queue:{queue_name}:active")
            
            # Dead letter queue
            await self.redis_client.delete(f"queue:{queue_name}:dlq")
            
            # Stats hash
            await self.redis_client.delete(f"queue:{queue_name}:stats")
            
        except Exception as e:
            logger.error(f"Failed to initialize Redis structures for {queue_name}: {e}")
            raise

    async def enqueue_task(
        self,
        queue_name: str,
        task_type: str,
        payload: Dict[str, Any],
        priority: QueuePriority = QueuePriority.MEDIUM,
        delay: Optional[int] = None,
        timeout: Optional[int] = None,
        max_retries: int = 3
    ) -> str:
        """Enqueue a task for processing"""
        try:
            if queue_name not in self.queues:
                raise ValueError(f"Queue '{queue_name}' does not exist")
            
            # Create task
            task_id = f"task_{queue_name}_{int(time.time() * 1000000)}"
            task = QueueTask(
                id=task_id,
                queue_name=queue_name,
                task_type=task_type,
                payload=payload,
                priority=priority,
                created_at=time.time(),
                scheduled_at=time.time() + delay if delay else None,
                max_retries=max_retries,
                timeout=timeout or self.queues[queue_name].timeout
            )
            
            # Serialize task
            task_data = {
                "id": task.id,
                "queue_name": task.queue_name,
                "task_type": task.task_type,
                "payload": task.payload,
                "priority": task.priority,
                "created_at": task.created_at,
                "scheduled_at": task.scheduled_at,
                "max_retries": task.max_retries,
                "timeout": task.timeout,
                "retry_count": task.retry_count
            }
            
            # Add to appropriate queue
            if delay:
                # Delayed task - add to scheduled set
                await self.redis_client.zadd(
                    f"queue:{queue_name}:scheduled",
                    {task_id: task.scheduled_at}
                )
                await self.redis_client.hset(f"task:{task_id}", mapping=task_data)
            else:
                # Immediate task - add to priority queue
                await self.redis_client.lpush(f"queue:{queue_name}:{priority}", task_id)
                await self.redis_client.hset(f"task:{task_id}", mapping=task_data)
            
            # Update stats
            await self._update_queue_stats(queue_name, "pending_tasks", 1)
            
            logger.debug(f"Enqueued task {task_id} to queue {queue_name}")
            return task_id
            
        except Exception as e:
            logger.error(f"Failed to enqueue task: {e}")
            raise

    async def dequeue_task(self, queue_name: str, worker_id: str) -> Optional[QueueTask]:
        """Dequeue next task for processing"""
        try:
            if queue_name not in self.queues:
                return None
            
            # Check scheduled tasks first
            await self._process_scheduled_tasks(queue_name)
            
            # Try to get task by priority order
            for priority in [QueuePriority.CRITICAL, QueuePriority.HIGH, QueuePriority.MEDIUM, QueuePriority.LOW]:
                queue_key = f"queue:{queue_name}:{priority}"
                task_id = await self.redis_client.rpop(queue_key)
                
                if task_id:
                    # Get task data
                    task_data = await self.redis_client.hgetall(f"task:{task_id}")
                    if not task_data:
                        continue
                    
                    # Create task object
                    task = QueueTask(
                        id=task_data["id"],
                        queue_name=task_data["queue_name"],
                        task_type=task_data["task_type"],
                        payload=eval(task_data["payload"]),  # In production, use proper JSON deserialization
                        priority=QueuePriority(task_data["priority"]),
                        created_at=float(task_data["created_at"]),
                        retry_count=int(task_data.get("retry_count", 0)),
                        max_retries=int(task_data["max_retries"]),
                        timeout=int(task_data.get("timeout", 300))
                    )
                    
                    # Mark as active
                    await self.redis_client.sadd(f"queue:{queue_name}:active", task_id)
                    await self.redis_client.hset(f"task:{task_id}", "worker_id", worker_id)
                    await self.redis_client.hset(f"task:{task_id}", "started_at", time.time())
                    
                    # Update stats
                    await self._update_queue_stats(queue_name, "pending_tasks", -1)
                    await self._update_queue_stats(queue_name, "active_tasks", 1)
                    
                    return task
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to dequeue task from {queue_name}: {e}")
            return None

    async def _process_scheduled_tasks(self, queue_name: str) -> None:
        """Move scheduled tasks to active queues when ready"""
        try:
            current_time = time.time()
            scheduled_key = f"queue:{queue_name}:scheduled"
            
            # Get tasks ready to run
            ready_tasks = await self.redis_client.zrangebyscore(
                scheduled_key, 0, current_time, withscores=False
            )
            
            for task_id in ready_tasks:
                # Get task data
                task_data = await self.redis_client.hgetall(f"task:{task_id}")
                if task_data:
                    priority = task_data.get("priority", QueuePriority.MEDIUM)
                    
                    # Move to priority queue
                    await self.redis_client.lpush(f"queue:{queue_name}:{priority}", task_id)
                    await self.redis_client.zrem(scheduled_key, task_id)
                    
        except Exception as e:
            logger.error(f"Error processing scheduled tasks: {e}")

    async def complete_task(self, task_id: str, result: Dict[str, Any] = None) -> bool:
        """Mark task as completed"""
        try:
            # Get task data
            task_data = await self.redis_client.hgetall(f"task:{task_id}")
            if not task_data:
                return False
            
            queue_name = task_data["queue_name"]
            started_at = float(task_data.get("started_at", time.time()))
            processing_time = time.time() - started_at
            
            # Remove from active tasks
            await self.redis_client.srem(f"queue:{queue_name}:active", task_id)
            
            # Store completion data
            await self.redis_client.hset(f"task:{task_id}", "completed_at", time.time())
            await self.redis_client.hset(f"task:{task_id}", "processing_time", processing_time)
            if result:
                await self.redis_client.hset(f"task:{task_id}", "result", str(result))
            
            # Update stats
            await self._update_queue_stats(queue_name, "active_tasks", -1)
            await self._update_queue_stats(queue_name, "completed_tasks", 1)
            await self._update_processing_time_stats(queue_name, processing_time)
            
            # Clean up task after some time
            await self.redis_client.expire(f"task:{task_id}", 3600)  # 1 hour
            
            logger.debug(f"Task {task_id} completed in {processing_time:.2f}s")
            return True
            
        except Exception as e:
            logger.error(f"Failed to complete task {task_id}: {e}")
            return False

    async def fail_task(self, task_id: str, error: str, retry: bool = True) -> bool:
        """Mark task as failed and optionally retry"""
        try:
            # Get task data
            task_data = await self.redis_client.hgetall(f"task:{task_id}")
            if not task_data:
                return False
            
            queue_name = task_data["queue_name"]
            retry_count = int(task_data.get("retry_count", 0))
            max_retries = int(task_data.get("max_retries", 3))
            
            # Remove from active tasks
            await self.redis_client.srem(f"queue:{queue_name}:active", task_id)
            
            if retry and retry_count < max_retries:
                # Retry task
                retry_count += 1
                await self.redis_client.hset(f"task:{task_id}", "retry_count", retry_count)
                await self.redis_client.hset(f"task:{task_id}", "last_error", error)
                
                # Re-queue with exponential backoff
                delay = min(300, 2 ** retry_count)  # Max 5 minutes
                scheduled_at = time.time() + delay
                
                await self.redis_client.zadd(
                    f"queue:{queue_name}:scheduled",
                    {task_id: scheduled_at}
                )
                
                # Update stats
                await self._update_queue_stats(queue_name, "active_tasks", -1)
                await self._update_queue_stats(queue_name, "retry_tasks", 1)
                
                logger.info(f"Retrying task {task_id} (attempt {retry_count}/{max_retries}) in {delay}s")
                
            else:
                # Move to dead letter queue
                await self.redis_client.lpush(f"queue:{queue_name}:dlq", task_id)
                await self.redis_client.hset(f"task:{task_id}", "failed_at", time.time())
                await self.redis_client.hset(f"task:{task_id}", "final_error", error)
                
                # Update stats
                await self._update_queue_stats(queue_name, "active_tasks", -1)
                await self._update_queue_stats(queue_name, "failed_tasks", 1)
                
                logger.error(f"Task {task_id} moved to dead letter queue: {error}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to handle task failure {task_id}: {e}")
            return False

    async def _start_queue_workers(self, queue_name: str, worker_count: int) -> None:
        """Start workers for a queue"""
        try:
            if queue_name not in self.workers:
                self.workers[queue_name] = []
            
            for i in range(worker_count):
                worker_id = f"worker_{queue_name}_{i}"
                worker_task = asyncio.create_task(
                    self._worker_loop(queue_name, worker_id)
                )
                self.workers[queue_name].append(worker_task)
            
            logger.info(f"Started {worker_count} workers for queue {queue_name}")
            
        except Exception as e:
            logger.error(f"Failed to start workers for {queue_name}: {e}")

    async def _worker_loop(self, queue_name: str, worker_id: str) -> None:
        """Main worker loop for processing tasks"""
        logger.info(f"Worker {worker_id} started for queue {queue_name}")
        
        while self.is_running:
            try:
                # Dequeue task
                task = await self.dequeue_task(queue_name, worker_id)
                
                if task is None:
                    # No tasks available, wait a bit
                    await asyncio.sleep(1)
                    continue
                
                # Process task
                try:
                    result = await self._process_task(task)
                    await self.complete_task(task.id, result)
                    
                except asyncio.TimeoutError:
                    await self.fail_task(task.id, "Task timeout", retry=True)
                    
                except Exception as e:
                    await self.fail_task(task.id, str(e), retry=True)
                
            except Exception as e:
                logger.error(f"Worker {worker_id} error: {e}")
                await asyncio.sleep(5)
        
        logger.info(f"Worker {worker_id} stopped")

    async def _process_task(self, task: QueueTask) -> Dict[str, Any]:
        """Process a task (placeholder - would be implemented by specific processors)"""
        try:
            # This is a placeholder - actual task processing would be implemented
            # by specific task processors based on task_type
            
            logger.info(f"Processing task {task.id} of type {task.task_type}")
            
            # Simulate processing time
            await asyncio.sleep(0.1)
            
            return {"status": "completed", "processed_at": time.time()}
            
        except Exception as e:
            logger.error(f"Task processing failed: {e}")
            raise

    async def _update_queue_stats(self, queue_name: str, metric: str, delta: int) -> None:
        """Update queue statistics"""
        try:
            if queue_name in self.queue_stats:
                current_value = getattr(self.queue_stats[queue_name], metric, 0)
                setattr(self.queue_stats[queue_name], metric, max(0, current_value + delta))
                self.queue_stats[queue_name].last_activity = time.time()
            
        except Exception as e:
            logger.error(f"Failed to update stats for {queue_name}: {e}")

    async def _update_processing_time_stats(self, queue_name: str, processing_time: float) -> None:
        """Update average processing time statistics"""
        try:
            if queue_name in self.queue_stats:
                stats = self.queue_stats[queue_name]
                completed = stats.completed_tasks
                
                if completed > 0:
                    stats.avg_processing_time = (
                        (stats.avg_processing_time * (completed - 1) + processing_time) / completed
                    )
                else:
                    stats.avg_processing_time = processing_time
                    
        except Exception as e:
            logger.error(f"Failed to update processing time stats: {e}")

    async def _start_monitoring(self) -> None:
        """Start queue monitoring tasks"""
        try:
            # Queue stats monitor
            stats_task = asyncio.create_task(self._monitor_queue_stats())
            self.monitoring_tasks.append(stats_task)
            
            # Auto-scaling monitor
            scaling_task = asyncio.create_task(self._monitor_auto_scaling())
            self.monitoring_tasks.append(scaling_task)
            
            # Dead letter queue monitor
            dlq_task = asyncio.create_task(self._monitor_dead_letter_queues())
            self.monitoring_tasks.append(dlq_task)
            
            logger.info("Started queue monitoring tasks")
            
        except Exception as e:
            logger.error(f"Failed to start monitoring: {e}")

    async def _monitor_queue_stats(self) -> None:
        """Monitor queue statistics"""
        while self.is_running:
            try:
                for queue_name in self.queues:
                    await self._collect_queue_metrics(queue_name)
                
                await asyncio.sleep(30)  # Update every 30 seconds
                
            except Exception as e:
                logger.error(f"Error in queue stats monitoring: {e}")
                await asyncio.sleep(60)

    async def _collect_queue_metrics(self, queue_name: str) -> None:
        """Collect metrics for a specific queue"""
        try:
            # Get queue lengths
            pending_count = 0
            for priority in QueuePriority:
                count = await self.redis_client.llen(f"queue:{queue_name}:{priority}")
                pending_count += count
            
            # Get active tasks count
            active_count = await self.redis_client.scard(f"queue:{queue_name}:active")
            
            # Get dead letter queue count
            dlq_count = await self.redis_client.llen(f"queue:{queue_name}:dlq")
            
            # Update stats
            if queue_name in self.queue_stats:
                stats = self.queue_stats[queue_name]
                stats.pending_tasks = pending_count
                stats.active_tasks = active_count
                
                # Calculate throughput
                current_time = time.time()
                if hasattr(stats, '_last_completed_count'):
                    time_diff = current_time - stats._last_stats_update
                    completed_diff = stats.completed_tasks - stats._last_completed_count
                    if time_diff > 0:
                        stats.throughput_per_minute = (completed_diff / time_diff) * 60
                
                stats._last_completed_count = stats.completed_tasks
                stats._last_stats_update = current_time
            
        except Exception as e:
            logger.error(f"Error collecting metrics for {queue_name}: {e}")

    async def _monitor_auto_scaling(self) -> None:
        """Monitor and perform auto-scaling of workers"""
        while self.is_running:
            try:
                for queue_name, config in self.queues.items():
                    if config.auto_scale:
                        await self._auto_scale_queue(queue_name, config)
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Error in auto-scaling monitoring: {e}")
                await asyncio.sleep(120)

    async def _auto_scale_queue(self, queue_name: str, config: QueueConfiguration) -> None:
        """Auto-scale workers for a queue based on demand"""
        try:
            stats = self.queue_stats.get(queue_name)
            if not stats:
                return
            
            current_workers = len(self.workers.get(queue_name, []))
            pending_tasks = stats.pending_tasks
            active_tasks = stats.active_tasks
            
            # Scale up if queue is backing up
            if pending_tasks > current_workers * 5 and current_workers < config.max_workers:
                new_workers = min(2, config.max_workers - current_workers)
                await self._scale_up_workers(queue_name, new_workers)
                
            # Scale down if workers are idle
            elif pending_tasks < current_workers / 2 and current_workers > config.min_workers:
                workers_to_remove = min(1, current_workers - config.min_workers)
                await self._scale_down_workers(queue_name, workers_to_remove)
                
        except Exception as e:
            logger.error(f"Error auto-scaling queue {queue_name}: {e}")

    async def _scale_up_workers(self, queue_name: str, count: int) -> None:
        """Scale up workers for a queue"""
        try:
            current_count = len(self.workers.get(queue_name, []))
            
            for i in range(count):
                worker_id = f"worker_{queue_name}_{current_count + i}"
                worker_task = asyncio.create_task(
                    self._worker_loop(queue_name, worker_id)
                )
                self.workers[queue_name].append(worker_task)
            
            logger.info(f"Scaled up {count} workers for queue {queue_name}")
            
        except Exception as e:
            logger.error(f"Error scaling up workers for {queue_name}: {e}")

    async def _scale_down_workers(self, queue_name: str, count: int) -> None:
        """Scale down workers for a queue"""
        try:
            workers = self.workers.get(queue_name, [])
            
            for _ in range(min(count, len(workers))):
                worker = workers.pop()
                worker.cancel()
            
            logger.info(f"Scaled down {count} workers for queue {queue_name}")
            
        except Exception as e:
            logger.error(f"Error scaling down workers for {queue_name}: {e}")

    async def _monitor_dead_letter_queues(self) -> None:
        """Monitor dead letter queues for failed tasks"""
        while self.is_running:
            try:
                for queue_name in self.queues:
                    dlq_length = await self.redis_client.llen(f"queue:{queue_name}:dlq")
                    
                    if dlq_length > 100:  # Alert if too many failed tasks
                        logger.warning(f"Dead letter queue for {queue_name} has {dlq_length} failed tasks")
                
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                logger.error(f"Error monitoring dead letter queues: {e}")
                await asyncio.sleep(600)

    async def get_queue_status(self, queue_name: str) -> Optional[QueueStats]:
        """Get status for a specific queue"""
        try:
            if queue_name not in self.queue_stats:
                return None
            
            # Update real-time stats
            await self._collect_queue_metrics(queue_name)
            
            return self.queue_stats[queue_name]
            
        except Exception as e:
            logger.error(f"Error getting queue status: {e}")
            return None

    async def get_all_queue_status(self) -> Dict[str, QueueStats]:
        """Get status for all queues"""
        try:
            for queue_name in self.queues:
                await self._collect_queue_metrics(queue_name)
            
            return self.queue_stats.copy()
            
        except Exception as e:
            logger.error(f"Error getting all queue status: {e}")
            return {}

    async def pause_queue(self, queue_name: str) -> bool:
        """Pause a queue"""
        try:
            if queue_name in self.queue_stats:
                self.queue_stats[queue_name].status = QueueStatus.PAUSED
                logger.info(f"Queue {queue_name} paused")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error pausing queue {queue_name}: {e}")
            return False

    async def resume_queue(self, queue_name: str) -> bool:
        """Resume a paused queue"""
        try:
            if queue_name in self.queue_stats:
                self.queue_stats[queue_name].status = QueueStatus.ACTIVE
                logger.info(f"Queue {queue_name} resumed")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error resuming queue {queue_name}: {e}")
            return False

    async def shutdown(self) -> None:
        """Shutdown queue manager"""
        try:
            logger.info("Shutting down queue manager")
            
            self.is_running = False
            
            # Cancel monitoring tasks
            for task in self.monitoring_tasks:
                task.cancel()
            
            # Cancel all workers
            for queue_workers in self.workers.values():
                for worker in queue_workers:
                    worker.cancel()
            
            # Close Redis connection
            if self.redis_client:
                await self.redis_client.close()
            
            logger.info("Queue manager shutdown completed")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")
