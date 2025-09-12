"""{{service_name}} Asynchronous Service for Ainflue Platform
{{service_description}}

Author: {{author_name}} ({{author_email}})
Created: {{created_date}}
"""

import logging
import asyncio
from typing import Dict, Any, Optional, List, Union, Callable, Awaitable, TypeVar, Generic
from datetime import datetime, timedelta
from abc import ABC, abstractmethod
from enum import Enum
import inspect
import uuid
import json
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field

import aioredis
import aiohttp
from pydantic import BaseModel, Field, validator
from fastapi import HTTPException
import aioboto3

from core.base_service import BaseService
from core.config import get_settings
from core.exceptions import ServiceException, AsyncOperationException
from core.database import get_async_db_session
from monitoring.async_metrics import AsyncMetricsCollector
from utils.async_decorators import retry_async, timeout_async, circuit_breaker
from utils.rate_limiter import AsyncRateLimiter
from utils.caching import AsyncCacheManager

logger = logging.getLogger(__name__)
settings = get_settings()

T = TypeVar('T')


class TaskStatus(Enum):
    """Async task status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


class TaskPriority(Enum):
    """Task priority levels"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


class AsyncTaskRequest(BaseModel):
    """Async task request model"""
    task_id: Optional[str] = None
    operation: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    priority: TaskPriority = TaskPriority.NORMAL
    timeout_seconds: Optional[int] = Field(default=300, ge=1, le=3600)
    retry_count: int = Field(default=3, ge=0, le=10)
    callback_url: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

    def __post_init__(self):
        if not self.task_id:
            self.task_id = str(uuid.uuid4())


class AsyncTaskResult(BaseModel):
    """Async task result model"""
    task_id: str
    operation: str
    status: TaskStatus
    result: Optional[Any] = None
    error: Optional[str] = None
    progress: float = Field(default=0.0, ge=0.0, le=1.0)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    execution_time: Optional[float] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AsyncOperationConfig(BaseModel):
    """Configuration for async operations"""
    max_concurrent_tasks: int = 100
    default_timeout: int = 300
    enable_task_queue: bool = True
    enable_result_caching: bool = True
    cache_ttl_seconds: int = 3600
    enable_callbacks: bool = True
    enable_progress_tracking: bool = True
    max_retry_attempts: int = 3
    circuit_breaker_threshold: int = 5


@dataclass
class TaskContext:
    """Context for async task execution"""
    task_id: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    request_id: Optional[str] = None
    correlation_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class AsyncTaskManager:
    """Manager for async task lifecycle"""
    
    def __init__(self, redis_client, cache_manager):
        self.redis = redis_client
        self.cache = cache_manager
        self.running_tasks: Dict[str, asyncio.Task] = {}
        self.task_results: Dict[str, AsyncTaskResult] = {}
        
    async def submit_task(
        self,
        task_request: AsyncTaskRequest,
        task_func: Callable[..., Awaitable[Any]],
        context: Optional[TaskContext] = None
    ) -> str:
        """Submit async task for execution"""
        try:
            task_id = task_request.task_id or str(uuid.uuid4())
            
            # Create task result entry
            task_result = AsyncTaskResult(
                task_id=task_id,
                operation=task_request.operation,
                status=TaskStatus.PENDING,
                started_at=datetime.utcnow()
            )
            
            # Store in Redis for persistence
            await self.redis.setex(
                f"task:{task_id}",
                3600,  # 1 hour TTL
                json.dumps(task_result.dict(), default=str)
            )
            
            # Create and start asyncio task
            async_task = asyncio.create_task(
                self._execute_task(task_request, task_func, context)
            )
            
            self.running_tasks[task_id] = async_task
            
            return task_id
            
        except Exception as e:
            logger.error(f"Task submission failed: {str(e)}")
            raise AsyncOperationException(f"Failed to submit task: {str(e)}")
    
    async def _execute_task(
        self,
        task_request: AsyncTaskRequest,
        task_func: Callable[..., Awaitable[Any]],
        context: Optional[TaskContext] = None
    ) -> Any:
        """Execute async task with error handling and monitoring"""
        task_id = task_request.task_id
        start_time = datetime.utcnow()
        
        try:
            # Update status to running
            await self._update_task_status(task_id, TaskStatus.RUNNING)
            
            # Execute with timeout if specified
            if task_request.timeout_seconds:
                result = await asyncio.wait_for(
                    task_func(**task_request.parameters),
                    timeout=task_request.timeout_seconds
                )
            else:
                result = await task_func(**task_request.parameters)
            
            # Update with success result
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            task_result = AsyncTaskResult(
                task_id=task_id,
                operation=task_request.operation,
                status=TaskStatus.COMPLETED,
                result=result,
                started_at=start_time,
                completed_at=datetime.utcnow(),
                execution_time=execution_time,
                progress=1.0
            )
            
            await self._store_task_result(task_result)
            
            # Execute callback if configured
            if task_request.callback_url:
                await self._execute_callback(task_request.callback_url, task_result)
            
            return result
            
        except asyncio.TimeoutError:
            await self._handle_task_timeout(task_id, task_request)
            raise
        except Exception as e:
            await self._handle_task_error(task_id, task_request, e)
            raise
        finally:
            # Cleanup
            self.running_tasks.pop(task_id, None)
    
    async def _update_task_status(self, task_id: str, status: TaskStatus) -> None:
        """Update task status in Redis"""
        try:
            task_data = await self.redis.get(f"task:{task_id}")
            if task_data:
                task_result = AsyncTaskResult(**json.loads(task_data))
                task_result.status = status
                
                await self.redis.setex(
                    f"task:{task_id}",
                    3600,
                    json.dumps(task_result.dict(), default=str)
                )
        except Exception as e:
            logger.error(f"Failed to update task status: {str(e)}")
    
    async def _store_task_result(self, task_result: AsyncTaskResult) -> None:
        """Store task result in Redis"""
        try:
            await self.redis.setex(
                f"task:{task_result.task_id}",
                3600,
                json.dumps(task_result.dict(), default=str)
            )
        except Exception as e:
            logger.error(f"Failed to store task result: {str(e)}")
    
    async def _handle_task_timeout(
        self,
        task_id: str,
        task_request: AsyncTaskRequest
    ) -> None:
        """Handle task timeout"""
        task_result = AsyncTaskResult(
            task_id=task_id,
            operation=task_request.operation,
            status=TaskStatus.TIMEOUT,
            error="Task execution timed out",
            completed_at=datetime.utcnow()
        )
        
        await self._store_task_result(task_result)
    
    async def _handle_task_error(
        self,
        task_id: str,
        task_request: AsyncTaskRequest,
        error: Exception
    ) -> None:
        """Handle task execution error"""
        task_result = AsyncTaskResult(
            task_id=task_id,
            operation=task_request.operation,
            status=TaskStatus.FAILED,
            error=str(error),
            completed_at=datetime.utcnow()
        )
        
        await self._store_task_result(task_result)
    
    async def _execute_callback(
        self,
        callback_url: str,
        task_result: AsyncTaskResult
    ) -> None:
        """Execute callback notification"""
        try:
            async with aiohttp.ClientSession() as session:
                await session.post(
                    callback_url,
                    json=task_result.dict(),
                    timeout=aiohttp.ClientTimeout(total=30)
                )
        except Exception as e:
            logger.error(f"Callback execution failed: {str(e)}")
    
    async def get_task_status(self, task_id: str) -> Optional[AsyncTaskResult]:
        """Get task status and result"""
        try:
            task_data = await self.redis.get(f"task:{task_id}")
            if task_data:
                return AsyncTaskResult(**json.loads(task_data))
            return None
        except Exception as e:
            logger.error(f"Failed to get task status: {str(e)}")
            return None
    
    async def cancel_task(self, task_id: str) -> bool:
        """Cancel running task"""
        try:
            if task_id in self.running_tasks:
                task = self.running_tasks[task_id]
                task.cancel()
                
                # Update status
                await self._update_task_status(task_id, TaskStatus.CANCELLED)
                
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to cancel task: {str(e)}")
            return False


class {{service_class_name}}(BaseService):
    """
    Advanced asynchronous service for Ainflue platform.
    
    Features:
    - Non-blocking async operations with coroutines
    - Task queue management with priorities
    - Progress tracking and status monitoring
    - Callback notifications and webhooks
    - Circuit breaker and retry mechanisms
    - Rate limiting and resource management
    - Result caching and persistence
    - Concurrent execution control
    - Error handling and recovery
    - Performance monitoring and metrics
    """
    
    def __init__(
        self,
        name: str = "{{service_name}}",
        config: Optional[AsyncOperationConfig] = None,
        **kwargs
    ):
        super().__init__(name=name, **kwargs)
        self.config = config or AsyncOperationConfig()
        
        # Initialize async components
        self.redis_client = None
        self.cache_manager = AsyncCacheManager()
        self.rate_limiter = AsyncRateLimiter()
        self.task_manager = None
        self.thread_executor = ThreadPoolExecutor(
            max_workers=self.config.max_concurrent_tasks
        )
        
        # Initialize metrics collector
        self.metrics = AsyncMetricsCollector()
        
        # Active operations tracking
        self.active_operations: Dict[str, asyncio.Task] = {}
        self.operation_semaphore = asyncio.Semaphore(
            self.config.max_concurrent_tasks
        )
        
        logger.info(f"Async service '{name}' initialized successfully")

    async def initialize(self) -> None:
        """Initialize async service components"""
        try:
            # Initialize Redis connection
            self.redis_client = await aioredis.from_url(
                settings.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
            
            # Initialize task manager
            self.task_manager = AsyncTaskManager(
                self.redis_client,
                self.cache_manager
            )
            
            # Initialize cache manager
            await self.cache_manager.initialize(self.redis_client)
            
            logger.info("Async service components initialized")
            
        except Exception as e:
            logger.error(f"Async service initialization failed: {str(e)}")
            raise ServiceException(f"Initialization failed: {str(e)}")

    async def cleanup(self) -> None:
        """Cleanup async service resources"""
        try:
            # Cancel all running tasks
            for task in self.active_operations.values():
                task.cancel()
            
            # Wait for tasks to complete
            await asyncio.gather(
                *self.active_operations.values(),
                return_exceptions=True
            )
            
            # Cleanup thread executor
            self.thread_executor.shutdown(wait=True)
            
            # Close Redis connection
            if self.redis_client:
                await self.redis_client.close()
            
            logger.info("Async service cleanup completed")
            
        except Exception as e:
            logger.error(f"Async service cleanup failed: {str(e)}")

    @retry_async(max_attempts=3, backoff_factor=1.5)
    @timeout_async(timeout=300)
    @circuit_breaker(failure_threshold=5, recovery_timeout=60)
    async def execute_async_operation(
        self,
        operation: str,
        parameters: Dict[str, Any],
        priority: TaskPriority = TaskPriority.NORMAL,
        timeout_seconds: Optional[int] = None,
        callback_url: Optional[str] = None,
        context: Optional[TaskContext] = None
    ) -> str:
        """
        Execute an asynchronous operation.
        
        Args:
            operation: Name of the operation to execute
            parameters: Operation parameters
            priority: Task priority level
            timeout_seconds: Operation timeout in seconds
            callback_url: Optional callback URL for notifications
            context: Task execution context
            
        Returns:
            Task ID for tracking the operation
        """
        try:
            # Create task request
            task_request = AsyncTaskRequest(
                operation=operation,
                parameters=parameters,
                priority=priority,
                timeout_seconds=timeout_seconds or self.config.default_timeout,
                callback_url=callback_url
            )
            
            # Get operation handler
            operation_handler = self._get_operation_handler(operation)
            if not operation_handler:
                raise ValueError(f"Unknown operation: {operation}")
            
            # Check rate limits
            await self.rate_limiter.check_rate_limit(
                key=f"operation:{operation}",
                limit=100,  # 100 operations per minute
                window=60
            )
            
            # Submit task for execution
            task_id = await self.task_manager.submit_task(
                task_request,
                operation_handler,
                context
            )
            
            # Record metrics
            await self.metrics.record_operation_start(operation, task_id)
            
            return task_id
            
        except Exception as e:
            logger.error(f"Async operation execution failed: {str(e)}")
            raise AsyncOperationException(f"Operation failed: {str(e)}")

    async def get_operation_status(self, task_id: str) -> Optional[AsyncTaskResult]:
        """
        Get the status of an async operation.
        
        Args:
            task_id: Task identifier
            
        Returns:
            Task result with current status
        """
        try:
            return await self.task_manager.get_task_status(task_id)
        except Exception as e:
            logger.error(f"Failed to get operation status: {str(e)}")
            return None

    async def cancel_operation(self, task_id: str) -> bool:
        """
        Cancel a running async operation.
        
        Args:
            task_id: Task identifier
            
        Returns:
            True if cancellation was successful
        """
        try:
            return await self.task_manager.cancel_task(task_id)
        except Exception as e:
            logger.error(f"Failed to cancel operation: {str(e)}")
            return False

    async def execute_batch_operations(
        self,
        operations: List[AsyncTaskRequest],
        max_concurrent: Optional[int] = None
    ) -> List[str]:
        """
        Execute multiple operations concurrently.
        
        Args:
            operations: List of operations to execute
            max_concurrent: Maximum concurrent operations
            
        Returns:
            List of task IDs
        """
        try:
            max_concurrent = max_concurrent or self.config.max_concurrent_tasks
            semaphore = asyncio.Semaphore(max_concurrent)
            
            async def execute_single(task_request: AsyncTaskRequest) -> str:
                async with semaphore:
                    return await self.execute_async_operation(
                        operation=task_request.operation,
                        parameters=task_request.parameters,
                        priority=task_request.priority,
                        timeout_seconds=task_request.timeout_seconds,
                        callback_url=task_request.callback_url
                    )
            
            # Execute all operations concurrently
            tasks = [execute_single(op) for op in operations]
            task_ids = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Filter out exceptions and return successful task IDs
            successful_ids = [
                task_id for task_id in task_ids
                if isinstance(task_id, str)
            ]
            
            return successful_ids
            
        except Exception as e:
            logger.error(f"Batch operation execution failed: {str(e)}")
            raise AsyncOperationException(f"Batch execution failed: {str(e)}")

    async def wait_for_completion(
        self,
        task_ids: List[str],
        timeout_seconds: Optional[int] = None
    ) -> List[AsyncTaskResult]:
        """
        Wait for multiple operations to complete.
        
        Args:
            task_ids: List of task IDs to wait for
            timeout_seconds: Maximum time to wait
            
        Returns:
            List of completed task results
        """
        try:
            start_time = datetime.utcnow()
            timeout = timeout_seconds or 300  # 5 minutes default
            
            results = []
            
            while task_ids:
                # Check timeout
                elapsed = (datetime.utcnow() - start_time).total_seconds()
                if elapsed >= timeout:
                    logger.warning(f"Wait timeout reached for {len(task_ids)} tasks")
                    break
                
                # Check completed tasks
                completed_ids = []
                for task_id in task_ids:
                    result = await self.get_operation_status(task_id)
                    if result and result.status in [
                        TaskStatus.COMPLETED,
                        TaskStatus.FAILED,
                        TaskStatus.CANCELLED,
                        TaskStatus.TIMEOUT
                    ]:
                        results.append(result)
                        completed_ids.append(task_id)
                
                # Remove completed tasks
                for task_id in completed_ids:
                    task_ids.remove(task_id)
                
                # Wait before next check
                if task_ids:
                    await asyncio.sleep(1)
            
            return results
            
        except Exception as e:
            logger.error(f"Wait for completion failed: {str(e)}")
            raise AsyncOperationException(f"Wait failed: {str(e)}")

    async def stream_operation_progress(
        self,
        task_id: str
    ) -> AsyncGenerator[AsyncTaskResult, None]:
        """
        Stream progress updates for an operation.
        
        Args:
            task_id: Task identifier
            
        Yields:
            Task result updates
        """
        try:
            last_progress = 0.0
            
            while True:
                result = await self.get_operation_status(task_id)
                
                if not result:
                    break
                
                # Yield if progress changed or status changed
                if result.progress != last_progress or result.status != TaskStatus.RUNNING:
                    yield result
                    last_progress = result.progress
                
                # Break if operation completed
                if result.status in [
                    TaskStatus.COMPLETED,
                    TaskStatus.FAILED,
                    TaskStatus.CANCELLED,
                    TaskStatus.TIMEOUT
                ]:
                    break
                
                await asyncio.sleep(1)  # Check every second
                
        except Exception as e:
            logger.error(f"Progress streaming failed: {str(e)}")

    def _get_operation_handler(self, operation: str) -> Optional[Callable]:
        """Get handler function for operation"""
        # Map operation names to handler methods
        operation_handlers = {
            "process_content": self._process_content_async,
            "analyze_data": self._analyze_data_async,
            "generate_report": self._generate_report_async,
            "send_notifications": self._send_notifications_async,
            "backup_data": self._backup_data_async,
            "sync_external": self._sync_external_async
        }
        
        return operation_handlers.get(operation)

    # Example async operation handlers

    async def _process_content_async(
        self,
        content_id: str,
        processing_options: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Example: Process content asynchronously"""
        try:
            # Simulate content processing
            await asyncio.sleep(2)  # Simulate processing time
            
            result = {
                "content_id": content_id,
                "processed_at": datetime.utcnow().isoformat(),
                "status": "processed",
                "metadata": processing_options or {}
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Content processing failed: {str(e)}")
            raise

    async def _analyze_data_async(
        self,
        data_source: str,
        analysis_type: str = "basic"
    ) -> Dict[str, Any]:
        """Example: Analyze data asynchronously"""
        try:
            # Simulate data analysis
            await asyncio.sleep(5)  # Simulate analysis time
            
            result = {
                "data_source": data_source,
                "analysis_type": analysis_type,
                "analyzed_at": datetime.utcnow().isoformat(),
                "results": {
                    "total_records": 1000,
                    "processed_records": 950,
                    "errors": 50
                }
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Data analysis failed: {str(e)}")
            raise

    async def _generate_report_async(
        self,
        report_type: str,
        parameters: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Example: Generate report asynchronously"""
        try:
            # Simulate report generation
            await asyncio.sleep(10)  # Simulate generation time
            
            result = {
                "report_type": report_type,
                "generated_at": datetime.utcnow().isoformat(),
                "file_path": f"/reports/{report_type}_{uuid.uuid4()}.pdf",
                "parameters": parameters or {}
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Report generation failed: {str(e)}")
            raise

    async def _send_notifications_async(
        self,
        recipients: List[str],
        message: str,
        notification_type: str = "email"
    ) -> Dict[str, Any]:
        """Example: Send notifications asynchronously"""
        try:
            # Simulate notification sending
            await asyncio.sleep(3)  # Simulate sending time
            
            result = {
                "recipients": recipients,
                "message": message,
                "notification_type": notification_type,
                "sent_at": datetime.utcnow().isoformat(),
                "status": "sent",
                "delivery_count": len(recipients)
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Notification sending failed: {str(e)}")
            raise

    async def _backup_data_async(
        self,
        backup_type: str,
        data_sources: List[str]
    ) -> Dict[str, Any]:
        """Example: Backup data asynchronously"""
        try:
            # Simulate backup process
            await asyncio.sleep(15)  # Simulate backup time
            
            result = {
                "backup_type": backup_type,
                "data_sources": data_sources,
                "backup_at": datetime.utcnow().isoformat(),
                "backup_location": f"/backups/backup_{uuid.uuid4()}.tar.gz",
                "size_mb": 1024
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Data backup failed: {str(e)}")
            raise

    async def _sync_external_async(
        self,
        external_service: str,
        sync_options: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Example: Sync with external service asynchronously"""
        try:
            # Simulate external sync
            await asyncio.sleep(8)  # Simulate sync time
            
            result = {
                "external_service": external_service,
                "synced_at": datetime.utcnow().isoformat(),
                "sync_options": sync_options or {},
                "records_synced": 500,
                "status": "completed"
            }
            
            return result
            
        except Exception as e:
            logger.error(f"External sync failed: {str(e)}")
            raise

    async def run_in_thread(
        self,
        func: Callable[..., T],
        *args,
        **kwargs
    ) -> T:
        """
        Run a blocking function in a thread pool.
        
        Args:
            func: Function to run
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Function result
        """
        try:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                self.thread_executor,
                lambda: func(*args, **kwargs)
            )
            return result
        except Exception as e:
            logger.error(f"Thread execution failed: {str(e)}")
            raise AsyncOperationException(f"Thread execution failed: {str(e)}")

    def get_service_status(self) -> Dict[str, Any]:
        """Get async service status"""
        return {
            "active_operations": len(self.active_operations),
            "max_concurrent_tasks": self.config.max_concurrent_tasks,
            "thread_pool_active": not self.thread_executor._shutdown,
            "redis_connected": self.redis_client is not None,
            "cache_enabled": self.config.enable_result_caching,
            "metrics": self.metrics.get_summary()
        }

    def get_capabilities(self) -> Dict[str, Any]:
        """Get service capabilities"""
        return {
            "async_operations": True,
            "task_queue": self.config.enable_task_queue,
            "progress_tracking": self.config.enable_progress_tracking,
            "callback_support": self.config.enable_callbacks,
            "result_caching": self.config.enable_result_caching,
            "batch_operations": True,
            "streaming_progress": True,
            "thread_pool_execution": True,
            "max_concurrent_tasks": self.config.max_concurrent_tasks,
            "supported_operations": [
                "process_content",
                "analyze_data", 
                "generate_report",
                "send_notifications",
                "backup_data",
                "sync_external"
            ]
        }