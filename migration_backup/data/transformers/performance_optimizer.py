"""Performance Optimizer - High-performance batch and real-time processing for IA Influencer Agent Platform
=========================================================================================================

Advanced performance optimization suite providing industrial-grade batch processing, real-time conversion,
and quality optimization for creator workflows and enterprise content management.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
Warning: Unauthorized use strictly prohibited
"""

import asyncio
import logging
from typing import Dict, List, Optional, Union, Any, Tuple, Callable, AsyncGenerator
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum
import json
import time
import threading
import queue
import multiprocessing
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, Future
import heapq
import statistics

logger = logging.getLogger(__name__)


class ProcessingPriority(Enum):
    """Priority levels for processing operations."""
    
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4
    CRITICAL = 5


class ProcessingMode(Enum):
    """Processing execution modes."""
    
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    PIPELINE = "pipeline"
    ADAPTIVE = "adaptive"


class OptimizationStrategy(Enum):
    """Quality optimization strategies."""
    
    PRESERVE_QUALITY = "preserve_quality"
    BALANCED = "balanced"
    OPTIMIZE_SIZE = "optimize_size"
    OPTIMIZE_SPEED = "optimize_speed"
    CUSTOM = "custom"


class StreamingMode(Enum):
    """Real-time streaming modes."""
    
    LOW_LATENCY = "low_latency"
    BALANCED = "balanced"
    HIGH_QUALITY = "high_quality"
    ADAPTIVE_BITRATE = "adaptive_bitrate"


@dataclass
class BatchJob:
    """Batch processing job definition."""
    
    job_id: str
    tasks: List['BatchTask']
    priority: ProcessingPriority = ProcessingPriority.NORMAL
    processing_mode: ProcessingMode = ProcessingMode.PARALLEL
    max_workers: Optional[int] = None
    timeout: Optional[float] = None
    retry_count: int = 3
    callback: Optional[Callable] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: Optional[float] = None
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    status: str = "pending"


@dataclass
class BatchTask:
    """Individual task within a batch job."""
    
    task_id: str
    operation: str
    input_data: Any
    parameters: Dict[str, Any] = field(default_factory=dict)
    priority: ProcessingPriority = ProcessingPriority.NORMAL
    dependencies: List[str] = field(default_factory=list)
    retry_count: int = 3
    timeout: Optional[float] = None
    status: str = "pending"
    result: Optional[Any] = None
    error: Optional[str] = None
    processing_time: float = 0.0
    attempts: int = 0


@dataclass
class BatchResult:
    """Result of batch processing operation."""
    
    job_id: str
    success: bool
    completed_tasks: int = 0
    failed_tasks: int = 0
    total_processing_time: float = 0.0
    throughput: float = 0.0
    task_results: List[Dict[str, Any]] = field(default_factory=list)
    performance_metrics: Dict[str, Any] = field(default_factory=dict)
    error_summary: List[str] = field(default_factory=list)


@dataclass
class StreamConfiguration:
    """Configuration for real-time streaming conversion."""
    
    input_format: str
    output_format: str
    streaming_mode: StreamingMode = StreamingMode.BALANCED
    target_bitrate: Optional[int] = None
    buffer_size: int = 1024 * 1024  # 1MB default
    chunk_size: int = 64 * 1024     # 64KB default
    latency_target: float = 100.0   # milliseconds
    quality_threshold: float = 0.8
    adaptive_quality: bool = True
    error_recovery: bool = True
    custom_params: Dict[str, Any] = field(default_factory=dict)


@dataclass
class StreamChunk:
    """Data chunk for streaming processing."""
    
    chunk_id: str
    data: bytes
    timestamp: float
    sequence_number: int
    metadata: Dict[str, Any] = field(default_factory=dict)
    processing_time: float = 0.0
    quality_score: Optional[float] = None


@dataclass
class QualityMetrics:
    """Quality metrics for processed content."""
    
    overall_score: float
    visual_quality: Optional[float] = None
    audio_quality: Optional[float] = None
    compression_efficiency: Optional[float] = None
    processing_speed: Optional[float] = None
    resource_usage: Optional[float] = None
    user_satisfaction: Optional[float] = None
    metrics_timestamp: float = field(default_factory=time.time)


@dataclass
class OptimizationResult:
    """Result of quality optimization operation."""
    
    success: bool
    original_metrics: Optional[QualityMetrics] = None
    optimized_metrics: Optional[QualityMetrics] = None
    improvement_percentage: float = 0.0
    optimization_strategy: OptimizationStrategy = OptimizationStrategy.BALANCED
    processing_time: float = 0.0
    recommendations: List[str] = field(default_factory=list)
    error_message: Optional[str] = None


class BatchProcessor:
    """High-performance batch processing engine with intelligent scheduling."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize batch processor with configuration."""
        self.config = config or {}
        self.max_workers = self.config.get("max_workers", multiprocessing.cpu_count())
        self.max_concurrent_jobs = self.config.get("max_concurrent_jobs", 10)
        
        # Job management
        self.job_queue = []  # Priority queue for jobs
        self.active_jobs = {}
        self.completed_jobs = {}
        self.job_lock = threading.Lock()
        
        # Worker pools
        self.thread_pool = ThreadPoolExecutor(max_workers=self.max_workers)
        self.process_pool = ProcessPoolExecutor(max_workers=self.max_workers // 2)
        
        # Performance monitoring
        self.performance_stats = {
            "jobs_processed": 0,
            "total_processing_time": 0.0,
            "average_throughput": 0.0,
            "error_rate": 0.0
        }
        
        logger.info(f"BatchProcessor initialized with {self.max_workers} workers")
    
    async def submit_job(self, job: BatchJob) -> str:
        """
        Submit a batch job for processing.
        
        Args:
            job: BatchJob to process
            
        Returns:
            Job ID for tracking
        """
        try:
            # Set job timestamps
            job.created_at = time.time()
            job.status = "queued"
            
            # Validate job
            validation_result = await self._validate_job(job)
            if not validation_result["valid"]:
                raise ValueError(validation_result["error"])
            
            # Add to priority queue
            with self.job_lock:
                priority_score = self._calculate_job_priority(job)
                heapq.heappush(self.job_queue, (-priority_score, time.time(), job))
            
            logger.info(f"Job {job.job_id} submitted with priority {job.priority}")
            
            # Start processing if capacity available
            asyncio.create_task(self._process_job_queue())
            
            return job.job_id
            
        except Exception as e:
            logger.error(f"Failed to submit job {job.job_id}: {str(e)}")
            raise
    
    async def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """Get status of a specific job."""
        with self.job_lock:
            # Check active jobs
            if job_id in self.active_jobs:
                job = self.active_jobs[job_id]
                return {
                    "job_id": job_id,
                    "status": job.status,
                    "progress": self._calculate_job_progress(job),
                    "started_at": job.started_at,
                    "estimated_completion": self._estimate_completion_time(job)
                }
            
            # Check completed jobs
            if job_id in self.completed_jobs:
                result = self.completed_jobs[job_id]
                return {
                    "job_id": job_id,
                    "status": "completed",
                    "success": result.success,
                    "completed_tasks": result.completed_tasks,
                    "failed_tasks": result.failed_tasks,
                    "total_processing_time": result.total_processing_time
                }
            
            # Check queue
            for _, _, job in self.job_queue:
                if job.job_id == job_id:
                    return {
                        "job_id": job_id,
                        "status": "queued",
                        "queue_position": self._get_queue_position(job_id)
                    }
            
            return {"job_id": job_id, "status": "not_found"}
    
    async def cancel_job(self, job_id: str) -> bool:
        """Cancel a queued or running job."""
        try:
            with self.job_lock:
                # Remove from queue if queued
                self.job_queue = [
                    item for item in self.job_queue
                    if item[2].job_id != job_id
                ]
                heapq.heapify(self.job_queue)
                
                # Cancel active job
                if job_id in self.active_jobs:
                    job = self.active_jobs[job_id]
                    job.status = "cancelled"
                    # Note: In a real implementation, you'd need to cancel running tasks
                    
                    logger.info(f"Job {job_id} cancelled")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to cancel job {job_id}: {str(e)}")
            return False
    
    async def _validate_job(self, job: BatchJob) -> Dict[str, Any]:
        """Validate a batch job before processing."""
        if not job.job_id:
            return {"valid": False, "error": "Job ID is required"}
        
        if not job.tasks:
            return {"valid": False, "error": "Job must have at least one task"}
        
        # Validate task dependencies
        task_ids = {task.task_id for task in job.tasks}
        for task in job.tasks:
            for dep in task.dependencies:
                if dep not in task_ids:
                    return {"valid": False, "error": f"Task {task.task_id} has invalid dependency {dep}"}
        
        # Check for circular dependencies
        if self._has_circular_dependencies(job.tasks):
            return {"valid": False, "error": "Circular dependencies detected"}
        
        return {"valid": True}
    
    def _calculate_job_priority(self, job: BatchJob) -> float:
        """Calculate priority score for job scheduling."""
        base_priority = job.priority.value
        
        # Factor in number of tasks (smaller jobs get slight priority boost)
        task_factor = max(0.1, 1.0 - (len(job.tasks) / 1000.0))
        
        # Factor in creation time (older jobs get slight priority boost)
        age_factor = (time.time() - (job.created_at or time.time())) / 3600.0  # Hours
        
        return base_priority + task_factor + (age_factor * 0.1)
    
    async def _process_job_queue(self):
        """Process jobs from the priority queue."""
        while True:
            try:
                with self.job_lock:
                    if (len(self.active_jobs) >= self.max_concurrent_jobs or
                        not self.job_queue):
                        break
                    
                    # Get highest priority job
                    _, _, job = heapq.heappop(self.job_queue)
                    self.active_jobs[job.job_id] = job
                
                # Process job asynchronously
                asyncio.create_task(self._execute_job(job))
                
            except Exception as e:
                logger.error(f"Error processing job queue: {str(e)}")
                break
    
    async def _execute_job(self, job: BatchJob):
        """Execute a batch job."""
        try:
            job.started_at = time.time()
            job.status = "running"
            
            logger.info(f"Starting job {job.job_id} with {len(job.tasks)} tasks")
            
            # Create dependency graph and execution plan
            execution_plan = self._create_execution_plan(job.tasks)
            
            # Execute tasks according to plan
            task_results = await self._execute_tasks(job, execution_plan)
            
            # Compile results
            job.completed_at = time.time()
            total_time = job.completed_at - job.started_at
            
            successful_tasks = sum(1 for result in task_results if result.get("success", False))
            failed_tasks = len(task_results) - successful_tasks
            
            result = BatchResult(
                job_id=job.job_id,
                success=failed_tasks == 0,
                completed_tasks=successful_tasks,
                failed_tasks=failed_tasks,
                total_processing_time=total_time,
                throughput=len(job.tasks) / total_time if total_time > 0 else 0,
                task_results=task_results,
                performance_metrics=self._calculate_performance_metrics(job, task_results)
            )
            
            # Store result and cleanup
            with self.job_lock:
                del self.active_jobs[job.job_id]
                self.completed_jobs[job.job_id] = result
            
            # Update performance stats
            self._update_performance_stats(result)
            
            # Call callback if provided
            if job.callback:
                try:
                    await job.callback(result)
                except Exception as e:
                    logger.error(f"Job callback failed: {str(e)}")
            
            logger.info(f"Job {job.job_id} completed: {successful_tasks}/{len(job.tasks)} tasks successful")
            
        except Exception as e:
            logger.error(f"Job {job.job_id} execution failed: {str(e)}")
            job.status = "failed"
            
            with self.job_lock:
                if job.job_id in self.active_jobs:
                    del self.active_jobs[job.job_id]
                self.completed_jobs[job.job_id] = BatchResult(
                    job_id=job.job_id,
                    success=False,
                    error_summary=[str(e)]
                )
    
    def _create_execution_plan(self, tasks: List[BatchTask]) -> List[List[BatchTask]]:
        """Create execution plan considering task dependencies."""
        # Topological sort for dependency resolution
        in_degree = {task.task_id: 0 for task in tasks}
        task_map = {task.task_id: task for task in tasks}
        
        # Calculate in-degrees
        for task in tasks:
            for dep in task.dependencies:
                in_degree[task.task_id] += 1
        
        # Create execution levels
        execution_levels = []
        remaining_tasks = set(task.task_id for task in tasks)
        
        while remaining_tasks:
            # Find tasks with no dependencies
            ready_tasks = [
                task_map[task_id] for task_id in remaining_tasks
                if in_degree[task_id] == 0
            ]
            
            if not ready_tasks:
                # Circular dependency or error
                ready_tasks = [task_map[list(remaining_tasks)[0]]]
            
            execution_levels.append(ready_tasks)
            
            # Remove completed tasks and update in-degrees
            for task in ready_tasks:
                remaining_tasks.remove(task.task_id)
                for other_task in tasks:
                    if task.task_id in other_task.dependencies:
                        in_degree[other_task.task_id] -= 1
        
        return execution_levels
    
    async def _execute_tasks(self, job: BatchJob, execution_plan: List[List[BatchTask]]) -> List[Dict[str, Any]]:
        """Execute tasks according to execution plan."""
        all_results = []
        
        for level_tasks in execution_plan:
            if job.processing_mode == ProcessingMode.SEQUENTIAL:
                # Sequential execution within level
                for task in level_tasks:
                    result = await self._execute_single_task(task)
                    all_results.append(result)
            else:
                # Parallel execution within level
                level_results = await asyncio.gather(
                    *[self._execute_single_task(task) for task in level_tasks],
                    return_exceptions=True
                )
                
                # Handle exceptions
                for i, result in enumerate(level_results):
                    if isinstance(result, Exception):
                        all_results.append({
                            "task_id": level_tasks[i].task_id,
                            "success": False,
                            "error": str(result)
                        })
                    else:
                        all_results.append(result)
        
        return all_results
    
    async def _execute_single_task(self, task: BatchTask) -> Dict[str, Any]:
        """Execute a single task."""
        start_time = time.time()
        task.attempts += 1
        
        try:
            # Execute task based on operation type
            if task.operation == "format_conversion":
                result = await self._execute_format_conversion_task(task)
            elif task.operation == "media_transformation":
                result = await self._execute_media_transformation_task(task)
            elif task.operation == "content_processing":
                result = await self._execute_content_processing_task(task)
            else:
                # Generic task execution
                result = await self._execute_generic_task(task)
            
            task.processing_time = time.time() - start_time
            task.status = "completed"
            task.result = result
            
            return {
                "task_id": task.task_id,
                "success": True,
                "result": result,
                "processing_time": task.processing_time
            }
            
        except Exception as e:
            task.processing_time = time.time() - start_time
            task.error = str(e)
            
            # Retry logic
            if task.attempts < task.retry_count:
                logger.warning(f"Task {task.task_id} failed, retrying ({task.attempts}/{task.retry_count})")
                await asyncio.sleep(0.5 * task.attempts)  # Exponential backoff
                return await self._execute_single_task(task)
            else:
                task.status = "failed"
                logger.error(f"Task {task.task_id} failed after {task.attempts} attempts: {str(e)}")
                
                return {
                    "task_id": task.task_id,
                    "success": False,
                    "error": str(e),
                    "processing_time": task.processing_time
                }
    
    async def _execute_format_conversion_task(self, task: BatchTask) -> Any:
        """Execute format conversion task."""
        # Placeholder - would integrate with FormatConverter
        await asyncio.sleep(0.1)  # Simulate processing
        return {"converted": True, "format": task.parameters.get("target_format")}
    
    async def _execute_media_transformation_task(self, task: BatchTask) -> Any:
        """Execute media transformation task."""
        # Placeholder - would integrate with MediaTransformers
        await asyncio.sleep(0.2)  # Simulate processing
        return {"transformed": True, "type": task.parameters.get("transformation_type")}
    
    async def _execute_content_processing_task(self, task: BatchTask) -> Any:
        """Execute content processing task."""
        # Placeholder - would integrate with ContentProcessor
        await asyncio.sleep(0.05)  # Simulate processing
        return {"processed": True, "content_type": task.parameters.get("content_type")}
    
    async def _execute_generic_task(self, task: BatchTask) -> Any:
        """Execute generic task."""
        # Placeholder for custom task execution
        await asyncio.sleep(0.1)
        return {"executed": True, "operation": task.operation}
    
    def _calculate_performance_metrics(self, job: BatchJob, task_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate performance metrics for completed job."""
        processing_times = [
            result.get("processing_time", 0) for result in task_results
            if result.get("success", False)
        ]
        
        if not processing_times:
            return {}
        
        return {
            "avg_task_time": statistics.mean(processing_times),
            "min_task_time": min(processing_times),
            "max_task_time": max(processing_times),
            "median_task_time": statistics.median(processing_times),
            "std_task_time": statistics.stdev(processing_times) if len(processing_times) > 1 else 0,
            "total_cpu_time": sum(processing_times),
            "parallelization_efficiency": len(processing_times) / sum(processing_times) if sum(processing_times) > 0 else 0
        }
    
    def _update_performance_stats(self, result: BatchResult):
        """Update global performance statistics."""
        self.performance_stats["jobs_processed"] += 1
        self.performance_stats["total_processing_time"] += result.total_processing_time
        
        if self.performance_stats["jobs_processed"] > 0:
            self.performance_stats["average_throughput"] = (
                self.performance_stats["total_processing_time"] / 
                self.performance_stats["jobs_processed"]
            )
        
        # Update error rate
        total_tasks = result.completed_tasks + result.failed_tasks
        if total_tasks > 0:
            job_error_rate = result.failed_tasks / total_tasks
            current_error_rate = self.performance_stats["error_rate"]
            jobs_processed = self.performance_stats["jobs_processed"]
            
            # Moving average of error rate
            self.performance_stats["error_rate"] = (
                (current_error_rate * (jobs_processed - 1) + job_error_rate) / jobs_processed
            )
    
    def _calculate_job_progress(self, job: BatchJob) -> float:
        """Calculate progress percentage for a job."""
        if not job.tasks:
            return 0.0
        
        completed_tasks = sum(1 for task in job.tasks if task.status == "completed")
        return completed_tasks / len(job.tasks)
    
    def _estimate_completion_time(self, job: BatchJob) -> Optional[float]:
        """Estimate completion time for a running job."""
        if not job.started_at or job.status != "running":
            return None
        
        progress = self._calculate_job_progress(job)
        if progress <= 0:
            return None
        
        elapsed_time = time.time() - job.started_at
        estimated_total_time = elapsed_time / progress
        return job.started_at + estimated_total_time
    
    def _get_queue_position(self, job_id: str) -> int:
        """Get position of job in queue."""
        for i, (_, _, job) in enumerate(self.job_queue):
            if job.job_id == job_id:
                return i + 1
        return -1
    
    def _has_circular_dependencies(self, tasks: List[BatchTask]) -> bool:
        """Check for circular dependencies in task list."""
        # Simple DFS-based cycle detection
        task_map = {task.task_id: task for task in tasks}
        visited = set()
        rec_stack = set()
        
        def has_cycle(task_id):
            if task_id in rec_stack:
                return True
            if task_id in visited:
                return False
            
            visited.add(task_id)
            rec_stack.add(task_id)
            
            task = task_map.get(task_id)
            if task:
                for dep in task.dependencies:
                    if has_cycle(dep):
                        return True
            
            rec_stack.remove(task_id)
            return False
        
        for task in tasks:
            if task.task_id not in visited:
                if has_cycle(task.task_id):
                    return True
        
        return False
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get current performance statistics."""
        return self.performance_stats.copy()
    
    async def shutdown(self):
        """Shutdown the batch processor gracefully."""
        logger.info("Shutting down BatchProcessor...")
        
        # Cancel all queued jobs
        with self.job_lock:
            self.job_queue.clear()
        
        # Wait for active jobs to complete (with timeout)
        shutdown_timeout = 30.0
        start_time = time.time()
        
        while self.active_jobs and (time.time() - start_time) < shutdown_timeout:
            await asyncio.sleep(0.1)
        
        # Shutdown executor pools
        self.thread_pool.shutdown(wait=True)
        self.process_pool.shutdown(wait=True)
        
        logger.info("BatchProcessor shutdown complete")


class RealtimeConverter:
    """Real-time streaming conversion engine with adaptive quality."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize real-time converter with configuration."""
        self.config = config or {}
        self.max_concurrent_streams = self.config.get("max_concurrent_streams", 10)
        
        # Stream management
        self.active_streams = {}
        self.stream_stats = {}
        self.stream_lock = threading.Lock()
        
        # Performance monitoring
        self.performance_monitor = {
            "total_streams": 0,
            "active_streams": 0,
            "average_latency": 0.0,
            "throughput_mbps": 0.0,
            "error_rate": 0.0
        }
        
        logger.info("RealtimeConverter initialized")
    
    async def start_stream(self, stream_id: str, config: StreamConfiguration) -> bool:
        """
        Start a real-time conversion stream.
        
        Args:
            stream_id: Unique identifier for the stream
            config: Stream configuration
            
        Returns:
            True if stream started successfully
        """
        try:
            if len(self.active_streams) >= self.max_concurrent_streams:
                logger.warning(f"Maximum concurrent streams ({self.max_concurrent_streams}) reached")
                return False
            
            # Validate configuration
            if not await self._validate_stream_config(config):
                return False
            
            # Initialize stream context
            stream_context = {
                "config": config,
                "start_time": time.time(),
                "chunks_processed": 0,
                "total_data_processed": 0,
                "average_latency": 0.0,
                "quality_scores": [],
                "errors": [],
                "status": "running"
            }
            
            with self.stream_lock:
                self.active_streams[stream_id] = stream_context
                self.performance_monitor["active_streams"] = len(self.active_streams)
                self.performance_monitor["total_streams"] += 1
            
            logger.info(f"Stream {stream_id} started with mode {config.streaming_mode}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start stream {stream_id}: {str(e)}")
            return False
    
    async def process_chunk(self, stream_id: str, chunk: StreamChunk) -> Optional[StreamChunk]:
        """
        Process a chunk of streaming data.
        
        Args:
            stream_id: Stream identifier
            chunk: Data chunk to process
            
        Returns:
            Processed chunk or None if processing failed
        """
        start_time = time.time()
        
        try:
            with self.stream_lock:
                if stream_id not in self.active_streams:
                    logger.warning(f"Stream {stream_id} not found")
                    return None
                
                stream_context = self.active_streams[stream_id]
            
            config = stream_context["config"]
            
            # Process chunk based on configuration
            processed_chunk = await self._process_streaming_chunk(chunk, config)
            
            # Update metrics
            processing_time = time.time() - start_time
            processed_chunk.processing_time = processing_time
            
            # Update stream context
            with self.stream_lock:
                stream_context["chunks_processed"] += 1
                stream_context["total_data_processed"] += len(chunk.data)
                
                # Update average latency
                if stream_context["chunks_processed"] == 1:
                    stream_context["average_latency"] = processing_time
                else:
                    stream_context["average_latency"] = (
                        (stream_context["average_latency"] * (stream_context["chunks_processed"] - 1) + 
                         processing_time) / stream_context["chunks_processed"]
                    )
                
                # Track quality scores
                if processed_chunk.quality_score:
                    stream_context["quality_scores"].append(processed_chunk.quality_score)
            
            # Adaptive quality adjustment
            if config.adaptive_quality:
                await self._adjust_stream_quality(stream_id, processing_time)
            
            return processed_chunk
            
        except Exception as e:
            logger.error(f"Chunk processing failed for stream {stream_id}: {str(e)}")
            
            with self.stream_lock:
                if stream_id in self.active_streams:
                    self.active_streams[stream_id]["errors"].append(str(e))
            
            return None
    
    async def stop_stream(self, stream_id: str) -> Dict[str, Any]:
        """
        Stop a real-time conversion stream.
        
        Args:
            stream_id: Stream identifier
            
        Returns:
            Stream statistics
        """
        try:
            with self.stream_lock:
                if stream_id not in self.active_streams:
                    return {"error": "Stream not found"}
                
                stream_context = self.active_streams[stream_id]
                stream_context["status"] = "stopped"
                stream_context["end_time"] = time.time()
                
                # Calculate final statistics
                duration = stream_context["end_time"] - stream_context["start_time"]
                throughput = stream_context["total_data_processed"] / duration if duration > 0 else 0
                
                stats = {
                    "stream_id": stream_id,
                    "duration": duration,
                    "chunks_processed": stream_context["chunks_processed"],
                    "total_data_processed": stream_context["total_data_processed"],
                    "average_latency": stream_context["average_latency"],
                    "throughput_bps": throughput,
                    "average_quality": (
                        statistics.mean(stream_context["quality_scores"]) 
                        if stream_context["quality_scores"] else 0.0
                    ),
                    "error_count": len(stream_context["errors"]),
                    "success_rate": (
                        (stream_context["chunks_processed"] - len(stream_context["errors"])) / 
                        max(stream_context["chunks_processed"], 1)
                    )
                }
                
                # Store in completed streams and remove from active
                self.stream_stats[stream_id] = stats
                del self.active_streams[stream_id]
                self.performance_monitor["active_streams"] = len(self.active_streams)
            
            logger.info(f"Stream {stream_id} stopped - processed {stats['chunks_processed']} chunks")
            return stats
            
        except Exception as e:
            logger.error(f"Failed to stop stream {stream_id}: {str(e)}")
            return {"error": str(e)}
    
    async def _validate_stream_config(self, config: StreamConfiguration) -> bool:
        """Validate stream configuration."""
        if not config.input_format or not config.output_format:
            logger.error("Input and output formats are required")
            return False
        
        if config.buffer_size <= 0 or config.chunk_size <= 0:
            logger.error("Buffer size and chunk size must be positive")
            return False
        
        if config.latency_target <= 0:
            logger.error("Latency target must be positive")
            return False
        
        return True
    
    async def _process_streaming_chunk(self, chunk: StreamChunk, config: StreamConfiguration) -> StreamChunk:
        """Process a streaming chunk according to configuration."""
        # Placeholder implementation - would integrate with actual conversion engines
        
        # Simulate processing based on streaming mode
        if config.streaming_mode == StreamingMode.LOW_LATENCY:
            await asyncio.sleep(0.001)  # 1ms processing time
            quality_score = 0.7
        elif config.streaming_mode == StreamingMode.HIGH_QUALITY:
            await asyncio.sleep(0.01)   # 10ms processing time
            quality_score = 0.9
        elif config.streaming_mode == StreamingMode.ADAPTIVE_BITRATE:
            await asyncio.sleep(0.005)  # 5ms processing time
            quality_score = 0.8
        else:  # BALANCED
            await asyncio.sleep(0.003)  # 3ms processing time
            quality_score = 0.75
        
        # Create processed chunk
        processed_chunk = StreamChunk(
            chunk_id=chunk.chunk_id,
            data=f"processed_{config.output_format}_chunk_data".encode(),
            timestamp=time.time(),
            sequence_number=chunk.sequence_number,
            metadata=chunk.metadata.copy(),
            quality_score=quality_score
        )
        
        return processed_chunk
    
    async def _adjust_stream_quality(self, stream_id: str, processing_time: float):
        """Adjust stream quality based on performance."""
        with self.stream_lock:
            if stream_id not in self.active_streams:
                return
            
            stream_context = self.active_streams[stream_id]
            config = stream_context["config"]
            
            # Check if processing time exceeds latency target
            if processing_time > config.latency_target / 1000.0:  # Convert ms to seconds
                # Reduce quality to improve latency
                if config.streaming_mode != StreamingMode.LOW_LATENCY:
                    if config.streaming_mode == StreamingMode.HIGH_QUALITY:
                        config.streaming_mode = StreamingMode.BALANCED
                    else:
                        config.streaming_mode = StreamingMode.LOW_LATENCY
                    
                    logger.info(f"Stream {stream_id} quality adjusted to {config.streaming_mode} for latency")
            
            elif processing_time < config.latency_target / 2000.0:  # Half target latency
                # Increase quality if we have latency headroom
                if config.streaming_mode != StreamingMode.HIGH_QUALITY:
                    if config.streaming_mode == StreamingMode.LOW_LATENCY:
                        config.streaming_mode = StreamingMode.BALANCED
                    else:
                        config.streaming_mode = StreamingMode.HIGH_QUALITY
                    
                    logger.info(f"Stream {stream_id} quality upgraded to {config.streaming_mode}")
    
    def get_stream_status(self, stream_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific stream."""
        with self.stream_lock:
            if stream_id in self.active_streams:
                context = self.active_streams[stream_id]
                return {
                    "stream_id": stream_id,
                    "status": context["status"],
                    "chunks_processed": context["chunks_processed"],
                    "average_latency": context["average_latency"],
                    "data_processed": context["total_data_processed"],
                    "error_count": len(context["errors"])
                }
            elif stream_id in self.stream_stats:
                return self.stream_stats[stream_id]
            else:
                return None
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get real-time conversion performance statistics."""
        with self.stream_lock:
            # Calculate current throughput
            total_throughput = sum(
                context["total_data_processed"] / max(time.time() - context["start_time"], 1)
                for context in self.active_streams.values()
            )
            
            # Calculate average latency across active streams
            latencies = [
                context["average_latency"] 
                for context in self.active_streams.values()
                if context["average_latency"] > 0
            ]
            
            avg_latency = statistics.mean(latencies) if latencies else 0.0
            
            self.performance_monitor.update({
                "active_streams": len(self.active_streams),
                "average_latency": avg_latency,
                "throughput_mbps": total_throughput / (1024 * 1024) * 8  # Convert to Mbps
            })
            
            return self.performance_monitor.copy()


class QualityOptimizer:
    """Intelligent quality optimization engine with ML-driven recommendations."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize quality optimizer with configuration."""
        self.config = config or {}
        self.optimization_history = []
        self.quality_models = {}
        
        # Initialize optimization strategies
        self._init_optimization_strategies()
        
        logger.info("QualityOptimizer initialized")
    
    def _init_optimization_strategies(self):
        """Initialize optimization strategy configurations."""
        self.optimization_strategies = {
            OptimizationStrategy.PRESERVE_QUALITY: {
                "priority": "quality",
                "quality_threshold": 0.95,
                "compression_limit": 0.3,
                "processing_time_limit": None
            },
            OptimizationStrategy.BALANCED: {
                "priority": "balanced",
                "quality_threshold": 0.8,
                "compression_limit": 0.6,
                "processing_time_limit": 10.0
            },
            OptimizationStrategy.OPTIMIZE_SIZE: {
                "priority": "size",
                "quality_threshold": 0.6,
                "compression_limit": 0.8,
                "processing_time_limit": 5.0
            },
            OptimizationStrategy.OPTIMIZE_SPEED: {
                "priority": "speed",
                "quality_threshold": 0.7,
                "compression_limit": 0.5,
                "processing_time_limit": 2.0
            }
        }
    
    async def optimize_quality(
        self,
        input_data: Any,
        current_metrics: QualityMetrics,
        strategy: OptimizationStrategy = OptimizationStrategy.BALANCED,
        constraints: Optional[Dict[str, Any]] = None
    ) -> OptimizationResult:
        """
        Optimize quality based on strategy and constraints.
        
        Args:
            input_data: Input data to optimize
            current_metrics: Current quality metrics
            strategy: Optimization strategy to use
            constraints: Additional constraints
            
        Returns:
            OptimizationResult with improvements and recommendations
        """
        start_time = time.time()
        
        try:
            # Get strategy configuration
            strategy_config = self.optimization_strategies[strategy]
            
            # Analyze current quality
            analysis = await self._analyze_quality_characteristics(input_data, current_metrics)
            
            # Generate optimization plan
            optimization_plan = await self._create_optimization_plan(
                analysis, strategy_config, constraints or {}
            )
            
            # Apply optimizations
            optimized_metrics = await self._apply_optimizations(
                input_data, current_metrics, optimization_plan
            )
            
            # Calculate improvement
            improvement = await self._calculate_improvement_percentage(
                current_metrics, optimized_metrics
            )
            
            # Generate recommendations
            recommendations = await self._generate_optimization_recommendations(
                analysis, optimization_plan, improvement
            )
            
            result = OptimizationResult(
                success=True,
                original_metrics=current_metrics,
                optimized_metrics=optimized_metrics,
                improvement_percentage=improvement,
                optimization_strategy=strategy,
                processing_time=time.time() - start_time,
                recommendations=recommendations
            )
            
            # Store optimization history
            self.optimization_history.append(result)
            
            return result
            
        except Exception as e:
            logger.error(f"Quality optimization failed: {str(e)}")
            return OptimizationResult(
                success=False,
                error_message=str(e),
                processing_time=time.time() - start_time
            )
    
    async def _analyze_quality_characteristics(
        self, input_data: Any, metrics: QualityMetrics
    ) -> Dict[str, Any]:
        """Analyze quality characteristics of input data."""
        analysis = {
            "current_quality": metrics.overall_score,
            "quality_distribution": {
                "visual": metrics.visual_quality or metrics.overall_score,
                "audio": metrics.audio_quality or metrics.overall_score,
                "compression": metrics.compression_efficiency or 0.8
            },
            "optimization_potential": 1.0 - metrics.overall_score,
            "bottlenecks": [],
            "strengths": []
        }
        
        # Identify bottlenecks
        if metrics.visual_quality and metrics.visual_quality < 0.7:
            analysis["bottlenecks"].append("visual_quality")
        
        if metrics.audio_quality and metrics.audio_quality < 0.7:
            analysis["bottlenecks"].append("audio_quality")
        
        if metrics.compression_efficiency and metrics.compression_efficiency < 0.6:
            analysis["bottlenecks"].append("compression_efficiency")
        
        # Identify strengths
        if metrics.visual_quality and metrics.visual_quality > 0.9:
            analysis["strengths"].append("visual_quality")
        
        if metrics.audio_quality and metrics.audio_quality > 0.9:
            analysis["strengths"].append("audio_quality")
        
        return analysis
    
    async def _create_optimization_plan(
        self,
        analysis: Dict[str, Any],
        strategy_config: Dict[str, Any],
        constraints: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create optimization plan based on analysis and strategy."""
        plan = {
            "target_quality": strategy_config["quality_threshold"],
            "optimizations": [],
            "parameters": {},
            "priority_order": []
        }
        
        # Determine optimization priorities based on strategy
        if strategy_config["priority"] == "quality":
            plan["priority_order"] = ["visual_enhancement", "audio_enhancement", "compression_optimization"]
        elif strategy_config["priority"] == "size":
            plan["priority_order"] = ["compression_optimization", "format_optimization", "resolution_optimization"]
        elif strategy_config["priority"] == "speed":
            plan["priority_order"] = ["format_optimization", "compression_optimization", "resolution_optimization"]
        else:  # balanced
            plan["priority_order"] = ["compression_optimization", "visual_enhancement", "audio_enhancement"]
        
        # Add specific optimizations based on bottlenecks
        for bottleneck in analysis["bottlenecks"]:
            if bottleneck == "visual_quality":
                plan["optimizations"].append({
                    "type": "visual_enhancement",
                    "target_improvement": 0.1,
                    "methods": ["denoising", "sharpening", "upscaling"]
                })
            elif bottleneck == "audio_quality":
                plan["optimizations"].append({
                    "type": "audio_enhancement",
                    "target_improvement": 0.1,
                    "methods": ["noise_reduction", "normalization", "eq_adjustment"]
                })
            elif bottleneck == "compression_efficiency":
                plan["optimizations"].append({
                    "type": "compression_optimization",
                    "target_improvement": 0.15,
                    "methods": ["adaptive_bitrate", "smart_encoding", "format_selection"]
                })
        
        return plan
    
    async def _apply_optimizations(
        self,
        input_data: Any,
        current_metrics: QualityMetrics,
        optimization_plan: Dict[str, Any]
    ) -> QualityMetrics:
        """Apply optimizations according to the plan."""
        # Placeholder implementation - would apply actual optimizations
        
        optimized_metrics = QualityMetrics(
            overall_score=min(1.0, current_metrics.overall_score + 0.1),
            visual_quality=min(1.0, (current_metrics.visual_quality or current_metrics.overall_score) + 0.05),
            audio_quality=min(1.0, (current_metrics.audio_quality or current_metrics.overall_score) + 0.05),
            compression_efficiency=min(1.0, (current_metrics.compression_efficiency or 0.8) + 0.1),
            processing_speed=(current_metrics.processing_speed or 0.8) * 1.05,
            resource_usage=(current_metrics.resource_usage or 0.7) * 0.95
        )
        
        return optimized_metrics
    
    async def _calculate_improvement_percentage(
        self, original: QualityMetrics, optimized: QualityMetrics
    ) -> float:
        """Calculate overall improvement percentage."""
        original_score = original.overall_score
        optimized_score = optimized.overall_score
        
        if original_score == 0:
            return 0.0
        
        improvement = ((optimized_score - original_score) / original_score) * 100
        return max(0.0, improvement)
    
    async def _generate_optimization_recommendations(
        self,
        analysis: Dict[str, Any],
        optimization_plan: Dict[str, Any],
        improvement: float
    ) -> List[str]:
        """Generate optimization recommendations."""
        recommendations = []
        
        if improvement < 5.0:
            recommendations.append("Consider using a more aggressive optimization strategy")
        
        if "visual_quality" in analysis["bottlenecks"]:
            recommendations.append("Apply visual enhancement filters for better quality")
        
        if "audio_quality" in analysis["bottlenecks"]:
            recommendations.append("Use audio enhancement to improve sound quality")
        
        if "compression_efficiency" in analysis["bottlenecks"]:
            recommendations.append("Optimize compression settings for better efficiency")
        
        if analysis["optimization_potential"] > 0.3:
            recommendations.append("Significant optimization potential available")
        
        return recommendations
    
    def get_optimization_history(self, limit: int = 10) -> List[OptimizationResult]:
        """Get recent optimization history."""
        return self.optimization_history[-limit:]
    
    def get_strategy_recommendations(self, metrics: QualityMetrics) -> OptimizationStrategy:
        """Get recommended optimization strategy based on current metrics."""
        if metrics.overall_score > 0.9:
            return OptimizationStrategy.OPTIMIZE_SIZE
        elif metrics.overall_score < 0.6:
            return OptimizationStrategy.PRESERVE_QUALITY
        elif metrics.processing_speed and metrics.processing_speed < 0.5:
            return OptimizationStrategy.OPTIMIZE_SPEED
        else:
            return OptimizationStrategy.BALANCED


# Export all classes for module imports
__all__ = [
    "BatchProcessor",
    "RealtimeConverter",
    "QualityOptimizer",
    "ProcessingPriority",
    "ProcessingMode",
    "OptimizationStrategy",
    "StreamingMode",
    "BatchJob",
    "BatchTask",
    "BatchResult",
    "StreamConfiguration",
    "StreamChunk",
    "QualityMetrics",
    "OptimizationResult"
]

logger.info("Performance optimizer module loaded successfully")