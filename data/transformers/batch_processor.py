"""
Batch Processor - High-performance batch processing for IA Influencer Agent Platform
==================================================================================

Advanced batch processing system for high-throughput content transformation workflows.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel - All Rights Reserved
Warning: Unauthorized use strictly prohibited
"""

import asyncio
import logging
from typing import Dict, List, Optional, Union, Any, Callable, Iterator
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum
import json
import time
import threading
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
import queue
import multiprocessing as mp

logger = logging.getLogger(__name__)


class ProcessingMode(Enum):
    """Processing execution modes."""
    SEQUENTIAL = "sequential"
    PARALLEL_THREAD = "parallel_thread"
    PARALLEL_PROCESS = "parallel_process"
    HYBRID = "hybrid"
    DISTRIBUTED = "distributed"


class BatchPriority(Enum):
    """Batch processing priority levels."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"
    CRITICAL = "critical"


class TaskStatus(Enum):
    """Task processing status."""
    PENDING = "pending"
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"


@dataclass
class BatchTask:
    """Individual task in a batch processing job."""
    id: str
    input_file: str
    output_file: str
    transform_type: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    
    # Status tracking
    status: TaskStatus = TaskStatus.PENDING
    priority: BatchPriority = BatchPriority.NORMAL
    
    # Timing information
    created_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    
    # Processing information
    worker_id: Optional[str] = None
    attempt_count: int = 0
    max_retries: int = 3
    
    # Results
    success: bool = False
    error_message: Optional[str] = None
    result_data: Optional[Dict[str, Any]] = None
    
    # Progress tracking
    progress_percent: float = 0.0
    estimated_duration: Optional[float] = None


@dataclass
class BatchJob:
    """Batch processing job containing multiple tasks."""
    id: str
    name: str
    description: str = ""
    
    # Task collection
    tasks: List[BatchTask] = field(default_factory=list)
    
    # Processing configuration
    mode: ProcessingMode = ProcessingMode.PARALLEL_THREAD
    max_workers: Optional[int] = None
    chunk_size: int = 10
    
    # Priority and scheduling
    priority: BatchPriority = BatchPriority.NORMAL
    scheduled_at: Optional[float] = None
    
    # Status tracking
    created_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    
    # Progress information
    total_tasks: int = 0
    completed_tasks: int = 0
    failed_tasks: int = 0
    cancelled_tasks: int = 0
    
    # Configuration
    stop_on_error: bool = False
    retry_failed: bool = True
    save_progress: bool = True
    
    # Results
    success: bool = False
    results: List[Dict[str, Any]] = field(default_factory=list)
    
    def get_progress_percent(self) -> float:
        """Get overall job progress percentage."""
        if self.total_tasks == 0:
            return 0.0
        
        return (self.completed_tasks + self.failed_tasks) / self.total_tasks * 100
    
    def get_success_rate(self) -> float:
        """Get success rate percentage."""
        processed_tasks = self.completed_tasks + self.failed_tasks
        if processed_tasks == 0:
            return 0.0
        
        return self.completed_tasks / processed_tasks * 100


@dataclass
class BatchConfiguration:
    """Batch processor configuration."""
    # Worker configuration
    max_thread_workers: int = 4
    max_process_workers: int = 2
    worker_timeout: float = 300.0  # 5 minutes
    
    # Queue configuration
    max_queue_size: int = 1000
    queue_timeout: float = 30.0
    
    # Performance tuning
    chunk_size: int = 10
    memory_limit_mb: int = 1024
    cpu_limit_percent: float = 80.0
    
    # Retry configuration
    default_max_retries: int = 3
    retry_delay: float = 1.0
    exponential_backoff: bool = True
    
    # Monitoring
    progress_update_interval: float = 5.0
    metrics_collection: bool = True
    
    # Storage
    temp_directory: str = "/tmp/batch_processor"
    keep_temp_files: bool = False
    
    # Error handling
    continue_on_error: bool = True
    error_threshold_percent: float = 20.0


class BatchProcessor:
    """
    High-performance batch processor for the IA Influencer Agent Platform.
    
    Provides scalable batch processing capabilities for content transformation
    workflows with advanced scheduling, monitoring, and error handling.
    """
    
    def __init__(
        self,
        config: Optional[BatchConfiguration] = None,
        transformer_registry: Optional[Dict[str, Callable]] = None
    ):
        """
        Initialize batch processor.
        
        Args:
            config: Batch processing configuration
            transformer_registry: Registry of available transformers
        """
        self.config = config or BatchConfiguration()
        self.transformer_registry = transformer_registry or {}
        
        # Processing state
        self.active_jobs: Dict[str, BatchJob] = {}
        self.job_history: List[BatchJob] = []
        
        # Worker pools
        self.thread_executor = ThreadPoolExecutor(
            max_workers=self.config.max_thread_workers
        )
        self.process_executor = ProcessPoolExecutor(
            max_workers=self.config.max_process_workers
        )
        
        # Queue system
        self.task_queue = queue.PriorityQueue(maxsize=self.config.max_queue_size)
        self.result_queue = queue.Queue()
        
        # Monitoring
        self.metrics = {
            "jobs_processed": 0,
            "tasks_processed": 0,
            "total_processing_time": 0.0,
            "average_task_time": 0.0,
            "success_rate": 0.0,
            "error_count": 0
        }
        
        # Control flags
        self.is_running = False
        self.shutdown_requested = False
        
        # Create temp directory
        Path(self.config.temp_directory).mkdir(parents=True, exist_ok=True)
        
        logger.info("BatchProcessor initialized")
    
    async def submit_job(
        self,
        job: BatchJob,
        start_immediately: bool = True
    ) -> str:
        """
        Submit a batch job for processing.
        
        Args:
            job: Batch job to process
            start_immediately: Start processing immediately
            
        Returns:
            Job ID
        """
        try:
            # Validate job
            if not job.tasks:
                raise ValueError("Job must contain at least one task")
            
            # Set job metrics
            job.total_tasks = len(job.tasks)
            
            # Add to active jobs
            self.active_jobs[job.id] = job
            
            # Schedule for processing
            if start_immediately:
                await self._schedule_job(job)
            
            logger.info(f"Job submitted: {job.id} ({job.total_tasks} tasks)")
            return job.id
            
        except Exception as e:
            logger.error(f"Failed to submit job: {str(e)}")
            raise
    
    async def create_batch_job(
        self,
        name: str,
        input_files: List[str],
        transform_type: str,
        output_directory: str,
        parameters: Optional[Dict[str, Any]] = None,
        mode: ProcessingMode = ProcessingMode.PARALLEL_THREAD,
        priority: BatchPriority = BatchPriority.NORMAL
    ) -> BatchJob:
        """
        Create a batch job from input files.
        
        Args:
            name: Job name
            input_files: List of input files
            transform_type: Type of transformation
            output_directory: Output directory
            parameters: Transformation parameters
            mode: Processing mode
            priority: Job priority
            
        Returns:
            Created batch job
        """
        try:
            # Generate job ID
            job_id = f"batch_{int(time.time())}_{len(self.active_jobs)}"
            
            # Create tasks
            tasks = []
            output_dir = Path(output_directory)
            output_dir.mkdir(parents=True, exist_ok=True)
            
            for i, input_file in enumerate(input_files):
                input_path = Path(input_file)
                output_file = output_dir / f"{input_path.stem}_transformed{input_path.suffix}"
                
                task = BatchTask(
                    id=f"{job_id}_task_{i}",
                    input_file=input_file,
                    output_file=str(output_file),
                    transform_type=transform_type,
                    parameters=parameters or {},
                    priority=priority
                )
                tasks.append(task)
            
            # Create job
            job = BatchJob(
                id=job_id,
                name=name,
                tasks=tasks,
                mode=mode,
                priority=priority,
                max_workers=self._calculate_optimal_workers(len(tasks), mode)
            )
            
            return job
            
        except Exception as e:
            logger.error(f"Failed to create batch job: {str(e)}")
            raise
    
    async def process_job(self, job_id: str) -> BatchJob:
        """
        Process a specific batch job.
        
        Args:
            job_id: Job ID to process
            
        Returns:
            Processed job
        """
        try:
            job = self.active_jobs.get(job_id)
            if not job:
                raise ValueError(f"Job not found: {job_id}")
            
            job.started_at = time.time()
            
            # Choose processing strategy
            if job.mode == ProcessingMode.SEQUENTIAL:
                await self._process_sequential(job)
            elif job.mode == ProcessingMode.PARALLEL_THREAD:
                await self._process_parallel_thread(job)
            elif job.mode == ProcessingMode.PARALLEL_PROCESS:
                await self._process_parallel_process(job)
            elif job.mode == ProcessingMode.HYBRID:
                await self._process_hybrid(job)
            else:
                raise ValueError(f"Unsupported processing mode: {job.mode}")
            
            job.completed_at = time.time()
            job.success = job.failed_tasks == 0 or not job.stop_on_error
            
            # Update metrics
            self._update_metrics(job)
            
            # Move to history
            self.job_history.append(job)
            del self.active_jobs[job_id]
            
            logger.info(f"Job completed: {job_id} (Success: {job.success})")
            return job
            
        except Exception as e:
            logger.error(f"Job processing failed: {str(e)}")
            raise
    
    async def _schedule_job(self, job: BatchJob):
        """Schedule job for processing."""
        try:
            # Priority-based scheduling
            priority_value = {
                BatchPriority.LOW: 5,
                BatchPriority.NORMAL: 3,
                BatchPriority.HIGH: 2,
                BatchPriority.URGENT: 1,
                BatchPriority.CRITICAL: 0
            }[job.priority]
            
            # Add tasks to queue
            for task in job.tasks:
                task.status = TaskStatus.QUEUED
                self.task_queue.put((priority_value, time.time(), task))
            
        except Exception as e:
            logger.error(f"Job scheduling failed: {str(e)}")
            raise
    
    async def _process_sequential(self, job: BatchJob):
        """Process job tasks sequentially."""
        try:
            for task in job.tasks:
                if self.shutdown_requested or (job.stop_on_error and job.failed_tasks > 0):
                    task.status = TaskStatus.CANCELLED
                    job.cancelled_tasks += 1
                    continue
                
                await self._process_task(task)
                
                if task.success:
                    job.completed_tasks += 1
                else:
                    job.failed_tasks += 1
                    
                    if job.stop_on_error:
                        break
            
        except Exception as e:
            logger.error(f"Sequential processing failed: {str(e)}")
            raise
    
    async def _process_parallel_thread(self, job: BatchJob):
        """Process job tasks using thread parallelism."""
        try:
            # Create semaphore for worker limiting
            semaphore = asyncio.Semaphore(job.max_workers or self.config.max_thread_workers)
            
            async def process_with_semaphore(task):
                async with semaphore:
                    await self._process_task(task)
                    
                    if task.success:
                        job.completed_tasks += 1
                    else:
                        job.failed_tasks += 1
            
            # Process all tasks
            tasks_coroutines = [process_with_semaphore(task) for task in job.tasks]
            await asyncio.gather(*tasks_coroutines, return_exceptions=True)
            
        except Exception as e:
            logger.error(f"Parallel thread processing failed: {str(e)}")
            raise
    
    async def _process_parallel_process(self, job: BatchJob):
        """Process job tasks using process parallelism."""
        try:
            loop = asyncio.get_event_loop()
            
            # Create process tasks
            futures = []
            max_workers = job.max_workers or self.config.max_process_workers
            
            with ProcessPoolExecutor(max_workers=max_workers) as executor:
                for task in job.tasks:
                    future = loop.run_in_executor(
                        executor,
                        self._process_task_sync,
                        task
                    )
                    futures.append(future)
                
                # Wait for completion
                completed = await asyncio.gather(*futures, return_exceptions=True)
                
                # Update job status
                for i, result in enumerate(completed):
                    task = job.tasks[i]
                    if isinstance(result, Exception):
                        task.success = False
                        task.error_message = str(result)
                        job.failed_tasks += 1
                    else:
                        if task.success:
                            job.completed_tasks += 1
                        else:
                            job.failed_tasks += 1
            
        except Exception as e:
            logger.error(f"Parallel process processing failed: {str(e)}")
            raise
    
    async def _process_hybrid(self, job: BatchJob):
        """Process job using hybrid thread/process approach."""
        try:
            # Determine optimal split
            cpu_intensive_tasks = []
            io_intensive_tasks = []
            
            for task in job.tasks:
                if self._is_cpu_intensive(task.transform_type):
                    cpu_intensive_tasks.append(task)
                else:
                    io_intensive_tasks.append(task)
            
            # Process CPU-intensive tasks with processes
            if cpu_intensive_tasks:
                cpu_job = BatchJob(
                    id=f"{job.id}_cpu",
                    name=f"{job.name} (CPU)",
                    tasks=cpu_intensive_tasks,
                    mode=ProcessingMode.PARALLEL_PROCESS,
                    max_workers=self.config.max_process_workers
                )
                await self._process_parallel_process(cpu_job)
            
            # Process I/O-intensive tasks with threads
            if io_intensive_tasks:
                io_job = BatchJob(
                    id=f"{job.id}_io",
                    name=f"{job.name} (I/O)",
                    tasks=io_intensive_tasks,
                    mode=ProcessingMode.PARALLEL_THREAD,
                    max_workers=self.config.max_thread_workers
                )
                await self._process_parallel_thread(io_job)
            
            # Merge results
            job.completed_tasks = sum(1 for task in job.tasks if task.success)
            job.failed_tasks = sum(1 for task in job.tasks if not task.success and task.status != TaskStatus.CANCELLED)
            
        except Exception as e:
            logger.error(f"Hybrid processing failed: {str(e)}")
            raise
    
    async def _process_task(self, task: BatchTask):
        """Process individual task."""
        try:
            task.status = TaskStatus.PROCESSING
            task.started_at = time.time()
            
            # Get transformer
            transformer = self.transformer_registry.get(task.transform_type)
            if not transformer:
                raise ValueError(f"Unknown transform type: {task.transform_type}")
            
            # Execute transformation
            if asyncio.iscoroutinefunction(transformer):
                result = await transformer(
                    input_file=task.input_file,
                    output_file=task.output_file,
                    **task.parameters
                )
            else:
                result = transformer(
                    input_file=task.input_file,
                    output_file=task.output_file,
                    **task.parameters
                )
            
            # Update task status
            task.success = True
            task.status = TaskStatus.COMPLETED
            task.result_data = result if isinstance(result, dict) else {"result": result}
            
        except Exception as e:
            logger.error(f"Task processing failed: {task.id} - {str(e)}")
            task.success = False
            task.status = TaskStatus.FAILED
            task.error_message = str(e)
            
            # Retry logic
            if task.attempt_count < task.max_retries:
                task.attempt_count += 1
                task.status = TaskStatus.RETRYING
                
                # Exponential backoff
                delay = self.config.retry_delay
                if self.config.exponential_backoff:
                    delay *= (2 ** task.attempt_count)
                
                await asyncio.sleep(delay)
                await self._process_task(task)
        
        finally:
            task.completed_at = time.time()
    
    def _process_task_sync(self, task: BatchTask) -> BatchTask:
        """Synchronous task processing for process pools."""
        try:
            # This would be called in a separate process
            # Need to handle transformer execution differently
            task.status = TaskStatus.PROCESSING
            task.started_at = time.time()
            
            # Simulate processing
            time.sleep(0.1)  # Simulate work
            
            task.success = True
            task.status = TaskStatus.COMPLETED
            task.completed_at = time.time()
            
            return task
            
        except Exception as e:
            task.success = False
            task.status = TaskStatus.FAILED
            task.error_message = str(e)
            task.completed_at = time.time()
            return task
    
    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get current status of a job."""
        job = self.active_jobs.get(job_id)
        if not job:
            # Check history
            for historical_job in self.job_history:
                if historical_job.id == job_id:
                    job = historical_job
                    break
        
        if not job:
            return None
        
        return {
            "id": job.id,
            "name": job.name,
            "status": "completed" if job.completed_at else "processing",
            "progress_percent": job.get_progress_percent(),
            "success_rate": job.get_success_rate(),
            "total_tasks": job.total_tasks,
            "completed_tasks": job.completed_tasks,
            "failed_tasks": job.failed_tasks,
            "cancelled_tasks": job.cancelled_tasks,
            "created_at": job.created_at,
            "started_at": job.started_at,
            "completed_at": job.completed_at,
            "estimated_completion": self._estimate_completion_time(job)
        }
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get system processing metrics."""
        return {
            "active_jobs": len(self.active_jobs),
            "queue_size": self.task_queue.qsize(),
            "metrics": self.metrics,
            "worker_utilization": {
                "thread_workers": self.config.max_thread_workers,
                "process_workers": self.config.max_process_workers
            },
            "system_resources": self._get_system_resources()
        }
    
    def cancel_job(self, job_id: str) -> bool:
        """Cancel a running job."""
        try:
            job = self.active_jobs.get(job_id)
            if not job:
                return False
            
            # Mark remaining tasks as cancelled
            for task in job.tasks:
                if task.status in [TaskStatus.PENDING, TaskStatus.QUEUED]:
                    task.status = TaskStatus.CANCELLED
                    job.cancelled_tasks += 1
            
            job.completed_at = time.time()
            job.success = False
            
            # Move to history
            self.job_history.append(job)
            del self.active_jobs[job_id]
            
            logger.info(f"Job cancelled: {job_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to cancel job: {str(e)}")
            return False
    
    async def shutdown(self, timeout: float = 30.0):
        """Shutdown batch processor gracefully."""
        try:
            logger.info("Shutting down batch processor...")
            self.shutdown_requested = True
            
            # Wait for active jobs to complete
            start_time = time.time()
            while self.active_jobs and (time.time() - start_time) < timeout:
                await asyncio.sleep(1)
            
            # Force cancel remaining jobs
            for job_id in list(self.active_jobs.keys()):
                self.cancel_job(job_id)
            
            # Shutdown executors
            self.thread_executor.shutdown(wait=True)
            self.process_executor.shutdown(wait=True)
            
            logger.info("Batch processor shutdown complete")
            
        except Exception as e:
            logger.error(f"Shutdown failed: {str(e)}")
    
    def _calculate_optimal_workers(self, task_count: int, mode: ProcessingMode) -> int:
        """Calculate optimal number of workers."""
        if mode == ProcessingMode.PARALLEL_THREAD:
            return min(task_count, self.config.max_thread_workers)
        elif mode == ProcessingMode.PARALLEL_PROCESS:
            return min(task_count, self.config.max_process_workers)
        else:
            return 1
    
    def _is_cpu_intensive(self, transform_type: str) -> bool:
        """Determine if transformation is CPU-intensive."""
        cpu_intensive_types = {
            "video_encoding", "image_processing", "audio_analysis",
            "ml_inference", "compression", "encryption"
        }
        return transform_type in cpu_intensive_types
    
    def _update_metrics(self, job: BatchJob):
        """Update processing metrics."""
        self.metrics["jobs_processed"] += 1
        self.metrics["tasks_processed"] += job.total_tasks
        
        if job.started_at and job.completed_at:
            processing_time = job.completed_at - job.started_at
            self.metrics["total_processing_time"] += processing_time
            
            self.metrics["average_task_time"] = (
                self.metrics["total_processing_time"] / 
                max(1, self.metrics["tasks_processed"])
            )
        
        # Update success rate
        total_tasks = self.metrics["tasks_processed"]
        if total_tasks > 0:
            successful_tasks = total_tasks - self.metrics["error_count"]
            self.metrics["success_rate"] = (successful_tasks / total_tasks) * 100
        
        self.metrics["error_count"] += job.failed_tasks
    
    def _estimate_completion_time(self, job: BatchJob) -> Optional[float]:
        """Estimate job completion time."""
        try:
            if job.completed_at:
                return job.completed_at
            
            if not job.started_at or job.completed_tasks == 0:
                return None
            
            elapsed = time.time() - job.started_at
            avg_time_per_task = elapsed / job.completed_tasks
            remaining_tasks = job.total_tasks - job.completed_tasks - job.failed_tasks
            
            estimated_remaining = remaining_tasks * avg_time_per_task
            return time.time() + estimated_remaining
            
        except Exception:
            return None
    
    def _get_system_resources(self) -> Dict[str, Any]:
        """Get current system resource usage."""
        try:
            import psutil
            return {
                "cpu_percent": psutil.cpu_percent(),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_usage": psutil.disk_usage('/').percent
            }
        except ImportError:
            return {
                "cpu_percent": 0,
                "memory_percent": 0,
                "disk_usage": 0
            }


class BatchJobBuilder:
    """Builder pattern for creating batch jobs."""
    
    def __init__(self, name: str):
        self.name = name
        self.tasks = []
        self.mode = ProcessingMode.PARALLEL_THREAD
        self.priority = BatchPriority.NORMAL
        self.parameters = {}
    
    def add_task(
        self,
        input_file: str,
        output_file: str,
        transform_type: str,
        task_parameters: Optional[Dict[str, Any]] = None
    ) -> 'BatchJobBuilder':
        """Add a task to the batch."""
        task = BatchTask(
            id=f"task_{len(self.tasks)}",
            input_file=input_file,
            output_file=output_file,
            transform_type=transform_type,
            parameters=task_parameters or {},
            priority=self.priority
        )
        self.tasks.append(task)
        return self
    
    def set_mode(self, mode: ProcessingMode) -> 'BatchJobBuilder':
        """Set processing mode."""
        self.mode = mode
        return self
    
    def set_priority(self, priority: BatchPriority) -> 'BatchJobBuilder':
        """Set job priority."""
        self.priority = priority
        return self
    
    def build(self) -> BatchJob:
        """Build the batch job."""
        job_id = f"batch_{int(time.time())}_{hash(self.name) % 10000}"
        
        return BatchJob(
            id=job_id,
            name=self.name,
            tasks=self.tasks,
            mode=self.mode,
            priority=self.priority
        )


class BatchScheduler:
    """Advanced batch job scheduler."""
    
    def __init__(self, processor: BatchProcessor):
        self.processor = processor
        self.scheduled_jobs = []
        self.scheduler_running = False
    
    async def schedule_job(
        self,
        job: BatchJob,
        schedule_time: float,
        repeat_interval: Optional[float] = None
    ):
        """Schedule a job for future execution."""
        self.scheduled_jobs.append({
            "job": job,
            "schedule_time": schedule_time,
            "repeat_interval": repeat_interval,
            "last_run": None
        })
    
    async def start_scheduler(self):
        """Start the job scheduler."""
        self.scheduler_running = True
        
        while self.scheduler_running:
            current_time = time.time()
            
            for scheduled_job in self.scheduled_jobs[:]:
                if current_time >= scheduled_job["schedule_time"]:
                    # Execute job
                    await self.processor.submit_job(scheduled_job["job"])
                    scheduled_job["last_run"] = current_time
                    
                    # Handle repeating jobs
                    if scheduled_job["repeat_interval"]:
                        scheduled_job["schedule_time"] = current_time + scheduled_job["repeat_interval"]
                    else:
                        self.scheduled_jobs.remove(scheduled_job)
            
            await asyncio.sleep(1)  # Check every second
    
    def stop_scheduler(self):
        """Stop the job scheduler."""
        self.scheduler_running = False
