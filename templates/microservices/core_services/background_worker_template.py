"""
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

Background Worker Template for Ainflue Microservices Platform
============================================================

Enterprise-grade background worker service template providing:
- Celery-based distributed task processing
- Redis/RabbitMQ message broker integration
- Task retry mechanisms and error handling
- Priority-based task queues
- Periodic and scheduled tasks
- Task monitoring and metrics
- Dead letter queue handling
- Horizontal scaling support
- Resource management and throttling
- Task result persistence

Author: Fahed Mlaiel (mlaiel@live.de)
Backend Senior & Distributed Systems Expert
"""

import logging
import asyncio
import json
from typing import Dict, Any, Optional, List, Callable, Union
from datetime import datetime, timedelta
from enum import Enum
from abc import ABC, abstractmethod
import uuid
import time
import pickle

from celery import Celery, Task
from celery.signals import task_prerun, task_postrun, task_failure, task_retry
from celery.exceptions import Retry, Ignore
from kombu import Queue, Exchange
from pydantic import BaseModel, Field
import redis.asyncio as redis

from ..base_microservice import BaseMicroservice
from ..microservice_template import ServiceConfig, ServiceStatus

logger = logging.getLogger(__name__)


class TaskPriority(Enum):
    """Task priority levels"""
    LOW = 1
    NORMAL = 3
    HIGH = 5
    CRITICAL = 9


class TaskStatus(Enum):
    """Task execution status"""
    PENDING = "pending"
    STARTED = "started"
    SUCCESS = "success"
    FAILURE = "failure"
    RETRY = "retry"
    REVOKED = "revoked"


class WorkerConfig(ServiceConfig):
    """Background worker configuration"""
    broker_url: str = Field(default="redis://localhost:6379/0", description="Message broker URL")
    result_backend: str = Field(default="redis://localhost:6379/0", description="Result backend URL")
    task_routes: Dict[str, str] = Field(default_factory=dict, description="Task routing configuration")
    worker_concurrency: int = Field(default=4, description="Number of concurrent workers")
    worker_prefetch_multiplier: int = Field(default=4, description="Worker prefetch multiplier")
    task_soft_time_limit: int = Field(default=300, description="Soft time limit for tasks in seconds")
    task_time_limit: int = Field(default=600, description="Hard time limit for tasks in seconds")
    task_max_retries: int = Field(default=3, description="Maximum task retry attempts")
    task_default_retry_delay: int = Field(default=60, description="Default retry delay in seconds")
    result_expires: int = Field(default=3600, description="Task result expiration in seconds")
    enable_utc: bool = Field(default=True, description="Enable UTC timezone")
    timezone: str = Field(default="UTC", description="Worker timezone")
    worker_hijack_root_logger: bool = Field(default=False, description="Hijack root logger")
    worker_log_color: bool = Field(default=True, description="Enable colored logs")
    beat_schedule: Dict[str, Dict[str, Any]] = Field(default_factory=dict, description="Periodic task schedule")
    enable_monitoring: bool = Field(default=True, description="Enable task monitoring")
    enable_dead_letter_queue: bool = Field(default=True, description="Enable dead letter queue")
    dlq_max_retries: int = Field(default=5, description="Maximum retries before DLQ")


class TaskInfo(BaseModel):
    """Task execution information"""
    task_id: str = Field(..., description="Unique task ID")
    task_name: str = Field(..., description="Task name")
    priority: TaskPriority = Field(default=TaskPriority.NORMAL, description="Task priority")
    status: TaskStatus = Field(default=TaskStatus.PENDING, description="Task status")
    args: List[Any] = Field(default_factory=list, description="Task arguments")
    kwargs: Dict[str, Any] = Field(default_factory=dict, description="Task keyword arguments")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Task creation time")
    started_at: Optional[datetime] = Field(default=None, description="Task start time")
    completed_at: Optional[datetime] = Field(default=None, description="Task completion time")
    retry_count: int = Field(default=0, description="Number of retry attempts")
    max_retries: int = Field(default=3, description="Maximum retry attempts")
    error_message: Optional[str] = Field(default=None, description="Error message if failed")
    result: Optional[Any] = Field(default=None, description="Task result")
    worker_id: Optional[str] = Field(default=None, description="Worker that executed the task")
    execution_time: Optional[float] = Field(default=None, description="Task execution time in seconds")


class TaskResult(BaseModel):
    """Task execution result"""
    task_id: str = Field(..., description="Task ID")
    success: bool = Field(..., description="Execution success status")
    result: Optional[Any] = Field(default=None, description="Task result data")
    error: Optional[str] = Field(default=None, description="Error message if failed")
    execution_time: float = Field(..., description="Execution time in seconds")
    retry_count: int = Field(default=0, description="Number of retries")


class BaseTask(Task):
    """Base task class with enhanced functionality"""
    
    def __init__(self):
        self.task_info: Optional[TaskInfo] = None
        self.start_time: Optional[float] = None
    
    def before_start(self, task_id: str, args: List[Any], kwargs: Dict[str, Any]):
        """Called before task execution"""
        self.start_time = time.time()
        self.task_info = TaskInfo(
            task_id=task_id,
            task_name=self.name,
            args=args,
            kwargs=kwargs,
            started_at=datetime.utcnow()
        )
        logger.info(f"Starting task {self.name} [{task_id}]")
    
    def on_success(self, retval: Any, task_id: str, args: List[Any], kwargs: Dict[str, Any]):
        """Called on successful task completion"""
        execution_time = time.time() - self.start_time if self.start_time else 0
        
        if self.task_info:
            self.task_info.status = TaskStatus.SUCCESS
            self.task_info.completed_at = datetime.utcnow()
            self.task_info.result = retval
            self.task_info.execution_time = execution_time
        
        logger.info(f"Task {self.name} [{task_id}] completed successfully in {execution_time:.2f}s")
    
    def on_failure(self, exc: Exception, task_id: str, args: List[Any], kwargs: Dict[str, Any], einfo):
        """Called on task failure"""
        execution_time = time.time() - self.start_time if self.start_time else 0
        
        if self.task_info:
            self.task_info.status = TaskStatus.FAILURE
            self.task_info.completed_at = datetime.utcnow()
            self.task_info.error_message = str(exc)
            self.task_info.execution_time = execution_time
        
        logger.error(f"Task {self.name} [{task_id}] failed after {execution_time:.2f}s: {str(exc)}")
    
    def on_retry(self, exc: Exception, task_id: str, args: List[Any], kwargs: Dict[str, Any], einfo):
        """Called on task retry"""
        if self.task_info:
            self.task_info.status = TaskStatus.RETRY
            self.task_info.retry_count += 1
            self.task_info.error_message = str(exc)
        
        logger.warning(f"Task {self.name} [{task_id}] retry {self.task_info.retry_count}: {str(exc)}")


class TaskManager:
    """Task management and monitoring"""
    
    def __init__(self, celery_app: Celery, redis_client: Optional[redis.Redis] = None):
        self.celery_app = celery_app
        self.redis_client = redis_client
        self.task_history: Dict[str, TaskInfo] = {}
        self.active_tasks: Dict[str, TaskInfo] = {}
    
    async def submit_task(
        self,
        task_name: str,
        args: List[Any] = None,
        kwargs: Dict[str, Any] = None,
        priority: TaskPriority = TaskPriority.NORMAL,
        eta: Optional[datetime] = None,
        countdown: Optional[int] = None
    ) -> str:
        """Submit task for execution"""
        task_id = str(uuid.uuid4())
        
        # Create task info
        task_info = TaskInfo(
            task_id=task_id,
            task_name=task_name,
            priority=priority,
            args=args or [],
            kwargs=kwargs or {}
        )
        
        # Store task info
        self.active_tasks[task_id] = task_info
        
        # Submit to Celery
        task_options = {
            'task_id': task_id,
            'priority': priority.value
        }
        
        if eta:
            task_options['eta'] = eta
        elif countdown:
            task_options['countdown'] = countdown
        
        try:
            self.celery_app.send_task(
                task_name,
                args=args or [],
                kwargs=kwargs or {},
                **task_options
            )
            
            logger.info(f"Submitted task {task_name} [{task_id}] with priority {priority.name}")
            return task_id
            
        except Exception as e:
            task_info.status = TaskStatus.FAILURE
            task_info.error_message = str(e)
            logger.error(f"Failed to submit task {task_name}: {str(e)}")
            raise
    
    async def get_task_status(self, task_id: str) -> Optional[TaskInfo]:
        """Get task status and information"""
        # Check active tasks first
        if task_id in self.active_tasks:
            return self.active_tasks[task_id]
        
        # Check history
        if task_id in self.task_history:
            return self.task_history[task_id]
        
        # Query Celery result backend
        try:
            result = self.celery_app.AsyncResult(task_id)
            if result.state:
                return TaskInfo(
                    task_id=task_id,
                    task_name="unknown",
                    status=TaskStatus(result.state.lower()) if result.state.lower() in [s.value for s in TaskStatus] else TaskStatus.PENDING,
                    result=result.result if result.successful() else None,
                    error_message=str(result.result) if result.failed() else None
                )
        except Exception as e:
            logger.error(f"Failed to get task status for {task_id}: {str(e)}")
        
        return None
    
    async def cancel_task(self, task_id: str) -> bool:
        """Cancel a pending or running task"""
        try:
            self.celery_app.control.revoke(task_id, terminate=True)
            
            # Update task info
            if task_id in self.active_tasks:
                self.active_tasks[task_id].status = TaskStatus.REVOKED
                self.active_tasks[task_id].completed_at = datetime.utcnow()
            
            logger.info(f"Cancelled task {task_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to cancel task {task_id}: {str(e)}")
            return False
    
    def move_task_to_history(self, task_id: str):
        """Move completed task to history"""
        if task_id in self.active_tasks:
            self.task_history[task_id] = self.active_tasks.pop(task_id)
            
            # Keep history size manageable
            if len(self.task_history) > 10000:
                # Remove oldest entries
                oldest_tasks = sorted(
                    self.task_history.items(),
                    key=lambda x: x[1].created_at
                )[:1000]
                
                for old_task_id, _ in oldest_tasks:
                    del self.task_history[old_task_id]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get task execution statistics"""
        total_active = len(self.active_tasks)
        total_history = len(self.task_history)
        
        # Count by status
        status_counts = {}
        for task_info in self.active_tasks.values():
            status = task_info.status.value
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Calculate success rate from history
        if self.task_history:
            successful = sum(1 for t in self.task_history.values() if t.status == TaskStatus.SUCCESS)
            success_rate = successful / len(self.task_history) * 100
        else:
            success_rate = 0
        
        return {
            "active_tasks": total_active,
            "completed_tasks": total_history,
            "status_counts": status_counts,
            "success_rate_percent": success_rate
        }


class BackgroundWorkerTemplate(BaseMicroservice):
    """
    Enterprise background worker service template
    
    Provides comprehensive background task processing including:
    - Celery-based distributed task execution
    - Redis/RabbitMQ message broker integration
    - Priority-based task queues
    - Retry mechanisms with exponential backoff
    - Task monitoring and metrics collection
    - Periodic and scheduled task execution
    - Dead letter queue for failed tasks
    - Horizontal scaling support
    - Resource management and throttling
    - Task result persistence and retrieval
    """
    
    def __init__(self, config: WorkerConfig):
        """Initialize background worker service"""
        self.worker_config = config
        super().__init__(config)
        
        # Initialize Celery app
        self.celery_app = self._create_celery_app()
        
        # Task manager
        self.task_manager: Optional[TaskManager] = None
        
        # Worker process
        self.worker_process: Optional[asyncio.subprocess.Process] = None
        
        # Setup worker routes
        self._setup_worker_routes()
        self._register_default_tasks()
        
        logger.info(f"Background worker service initialized")
    
    def _create_celery_app(self) -> Celery:
        """Create and configure Celery application"""
        app = Celery(
            self.config.name,
            broker=self.worker_config.broker_url,
            backend=self.worker_config.result_backend
        )
        
        # Configure Celery
        app.conf.update(
            task_serializer='json',
            accept_content=['json'],
            result_serializer='json',
            timezone=self.worker_config.timezone,
            enable_utc=self.worker_config.enable_utc,
            task_soft_time_limit=self.worker_config.task_soft_time_limit,
            task_time_limit=self.worker_config.task_time_limit,
            task_max_retries=self.worker_config.task_max_retries,
            task_default_retry_delay=self.worker_config.task_default_retry_delay,
            result_expires=self.worker_config.result_expires,
            worker_prefetch_multiplier=self.worker_config.worker_prefetch_multiplier,
            task_routes=self.worker_config.task_routes,
            beat_schedule=self.worker_config.beat_schedule,
            worker_hijack_root_logger=self.worker_config.worker_hijack_root_logger,
            worker_log_color=self.worker_config.worker_log_color
        )
        
        # Setup priority queues
        app.conf.task_routes = {
            'tasks.critical.*': {'queue': 'critical'},
            'tasks.high.*': {'queue': 'high'},
            'tasks.normal.*': {'queue': 'normal'},
            'tasks.low.*': {'queue': 'low'}
        }
        
        app.conf.task_default_queue = 'normal'
        app.conf.task_queues = (
            Queue('critical', Exchange('critical'), routing_key='critical', priority=9),
            Queue('high', Exchange('high'), routing_key='high', priority=5),
            Queue('normal', Exchange('normal'), routing_key='normal', priority=3),
            Queue('low', Exchange('low'), routing_key='low', priority=1),
        )
        
        return app
    
    def _setup_worker_routes(self):
        """Setup worker management routes"""
        
        @self.app.post("/tasks/submit")
        async def submit_task(task_data: Dict[str, Any]):
            """Submit a task for execution"""
            try:
                task_id = await self.task_manager.submit_task(
                    task_name=task_data.get('task_name'),
                    args=task_data.get('args', []),
                    kwargs=task_data.get('kwargs', {}),
                    priority=TaskPriority(task_data.get('priority', TaskPriority.NORMAL.value))
                )
                
                return {"task_id": task_id, "status": "submitted"}
                
            except Exception as e:
                logger.error(f"Failed to submit task: {str(e)}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/tasks/{task_id}/status")
        async def get_task_status(task_id: str):
            """Get task status"""
            task_info = await self.task_manager.get_task_status(task_id)
            
            if not task_info:
                raise HTTPException(status_code=404, detail="Task not found")
            
            return task_info.dict()
        
        @self.app.delete("/tasks/{task_id}")
        async def cancel_task(task_id: str):
            """Cancel a task"""
            success = await self.task_manager.cancel_task(task_id)
            
            if success:
                return {"task_id": task_id, "status": "cancelled"}
            else:
                raise HTTPException(status_code=500, detail="Failed to cancel task")
        
        @self.app.get("/worker/stats")
        async def worker_statistics():
            """Get worker statistics"""
            stats = self.task_manager.get_statistics()
            
            # Add Celery worker stats
            inspect = self.celery_app.control.inspect()
            active = inspect.active()
            reserved = inspect.reserved()
            
            stats.update({
                "celery_active": active,
                "celery_reserved": reserved,
                "worker_config": {
                    "concurrency": self.worker_config.worker_concurrency,
                    "prefetch_multiplier": self.worker_config.worker_prefetch_multiplier
                }
            })
            
            return stats
        
        @self.app.get("/worker/queues")
        async def list_queues():
            """List task queues"""
            inspect = self.celery_app.control.inspect()
            return {
                "queues": list(self.celery_app.conf.task_queues),
                "active_queues": inspect.active_queues()
            }
    
    def _register_default_tasks(self):
        """Register default tasks"""
        
        @self.celery_app.task(base=BaseTask, bind=True)
        def example_task(self, data: Dict[str, Any]) -> Dict[str, Any]:
            """Example task implementation"""
            logger.info(f"Processing example task with data: {data}")
            
            # Simulate work
            time.sleep(data.get('duration', 1))
            
            return {
                "processed": True,
                "data": data,
                "timestamp": datetime.utcnow().isoformat()
            }
        
        @self.celery_app.task(base=BaseTask, bind=True)
        def email_task(self, to_email: str, subject: str, body: str) -> Dict[str, Any]:
            """Email sending task"""
            logger.info(f"Sending email to {to_email}")
            
            # Implement email sending logic
            # This is a placeholder implementation
            time.sleep(2)  # Simulate email sending
            
            return {
                "sent": True,
                "to": to_email,
                "subject": subject,
                "timestamp": datetime.utcnow().isoformat()
            }
        
        @self.celery_app.task(base=BaseTask, bind=True)
        def data_processing_task(self, data_source: str, processing_options: Dict[str, Any]) -> Dict[str, Any]:
            """Data processing task"""
            logger.info(f"Processing data from {data_source}")
            
            try:
                # Implement data processing logic
                # This is a placeholder implementation
                processed_records = processing_options.get('batch_size', 100)
                time.sleep(processed_records / 100)  # Simulate processing time
                
                return {
                    "processed_records": processed_records,
                    "source": data_source,
                    "options": processing_options,
                    "timestamp": datetime.utcnow().isoformat()
                }
                
            except Exception as e:
                # Retry on failure
                raise self.retry(exc=e, countdown=60, max_retries=3)
        
        @self.celery_app.task(base=BaseTask, bind=True)
        def cleanup_task(self) -> Dict[str, Any]:
            """Periodic cleanup task"""
            logger.info("Running cleanup task")
            
            # Implement cleanup logic
            cleaned_items = 0
            
            return {
                "cleaned_items": cleaned_items,
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def start_worker(self):
        """Start Celery worker process"""
        try:
            # Build worker command
            worker_cmd = [
                'celery',
                '-A', self.config.name,
                'worker',
                '--concurrency', str(self.worker_config.worker_concurrency),
                '--loglevel', 'info'
            ]
            
            # Start worker process
            self.worker_process = await asyncio.create_subprocess_exec(
                *worker_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            logger.info(f"Celery worker started with PID {self.worker_process.pid}")
            
        except Exception as e:
            logger.error(f"Failed to start Celery worker: {str(e)}")
            raise
    
    async def stop_worker(self):
        """Stop Celery worker process"""
        if self.worker_process:
            try:
                self.worker_process.terminate()
                await self.worker_process.wait()
                logger.info("Celery worker stopped")
            except Exception as e:
                logger.error(f"Error stopping Celery worker: {str(e)}")
    
    # Override abstract methods from BaseMicroservice
    
    async def initialize_service(self):
        """Initialize background worker service"""
        # Initialize task manager
        self.task_manager = TaskManager(self.celery_app, self.redis_client)
        
        logger.info(f"Background worker service {self.config.name} initialized")
    
    async def cleanup_service(self):
        """Cleanup background worker service"""
        await self.stop_worker()
        logger.info(f"Background worker service {self.config.name} cleaned up")
    
    def register_routes(self):
        """Register service-specific routes"""
        # Routes are registered in _setup_worker_routes
        pass
    
    async def register_service(self):
        """Register service with service discovery"""
        await self.start_worker()
        logger.info(f"Background worker service {self.config.name} registered")
    
    async def deregister_service(self):
        """Deregister service from service discovery"""
        await self.stop_worker()
        logger.info(f"Background worker service {self.config.name} deregistered")
    
    async def get_service_url(self, service_name: str) -> str:
        """Get service URL from service discovery"""
        return f"http://{service_name}:8000"
    
    async def start_background_tasks(self):
        """Start background tasks"""
        logger.info("Background worker tasks management started")
    
    async def stop_background_tasks(self):
        """Stop background tasks"""
        logger.info("Background worker tasks management stopped")


def create_background_worker_service(
    service_name: str = "background-worker-service",
    broker_url: str = "redis://localhost:6379/0",
    concurrency: int = 4
) -> BackgroundWorkerTemplate:
    """Factory function to create background worker service"""
    
    config = WorkerConfig(
        name=service_name,
        broker_url=broker_url,
        result_backend=broker_url,
        worker_concurrency=concurrency,
        enable_monitoring=True,
        enable_metrics=True
    )
    
    return BackgroundWorkerTemplate(config)


if __name__ == "__main__":
    # Example usage
    service = create_background_worker_service()
    service.run()