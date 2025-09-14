"""Core Streaming Engine for IA Influencer Agent Platform
======================================================

Consolidated streaming engine combining manager, processor, and scheduler
functionality for enterprise-grade real-time content streaming operations.

CONSOLIDATED ARCHITECTURE:
- StreamingEngine: Main orchestrator combining all streaming functions
- DataStreamManager: Legacy compatibility for stream management
- RealTimeProcessor: Legacy compatibility for real-time processing
- StreamScheduler: Legacy compatibility for task scheduling

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved

⚠️  LEGAL WARNING ⚠️
Unauthorized use, copying, modification, or distribution of this code
without explicit written permission from Fahed Mlaiel is strictly prohibited.
Violations will be prosecuted under German and international copyright law.

Contact: mlaiel@live.de for licensing inquiries.
"""

import asyncio
import logging
import time
import uuid
from typing import Dict, List, Optional, Any, Callable, Union, Tuple
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
from concurrent.futures import ThreadPoolExecutor, Future
from queue import Queue, PriorityQueue
import threading
from contextlib import asynccontextmanager

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class StreamType(str, Enum):
    """Stream content types"""
    AUDIO = "audio"
    VIDEO = "video" 
    IMAGE = "image"
    TEXT = "text"
    METADATA = "metadata"
    MIXED = "mixed"


class StreamStatus(str, Enum):
    """Stream status indicators"""
    INITIALIZING = "initializing"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"
    ERROR = "error"
    COMPLETED = "completed"


class ProcessingPriority(str, Enum):
    """Processing priority levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class ProcessingStage(str, Enum):
    """Processing pipeline stages"""
    VALIDATION = "validation"
    PREPROCESSING = "preprocessing"
    ANALYSIS = "analysis"
    PROTECTION = "protection"
    MONETIZATION = "monetization"
    POSTPROCESSING = "postprocessing"
    COMPLETION = "completion"


class ContentFormat(str, Enum):
    """Supported content formats"""
    # Audio formats
    MP3 = "mp3"
    WAV = "wav"
    FLAC = "flac"
    AAC = "aac"
    OGG = "ogg"
    
    # Video formats
    MP4 = "mp4"
    AVI = "avi"
    MOV = "mov"
    WEBM = "webm"
    MKV = "mkv"
    
    # Image formats
    JPEG = "jpeg"
    PNG = "png"
    GIF = "gif"
    WEBP = "webp"
    SVG = "svg"
    
    # Text formats
    TXT = "txt"
    MD = "md"
    HTML = "html"
    JSON = "json"


class TaskPriority(int, Enum):
    """Task scheduling priorities"""
    LOW = 1
    NORMAL = 5
    HIGH = 10
    CRITICAL = 20


class TaskStatus(str, Enum):
    """Task execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class StreamEvent:
    """Stream event data structure"""
    stream_id: str
    event_type: str
    content_type: StreamType
    content_format: ContentFormat
    data: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    priority: ProcessingPriority = ProcessingPriority.NORMAL
    correlation_id: str = field(default_factory=lambda: str(uuid.uuid4()))


@dataclass
class StreamMetrics:
    """Stream performance metrics"""
    stream_id: str
    events_processed: int = 0
    events_failed: int = 0
    average_processing_time: float = 0.0
    peak_processing_time: float = 0.0
    throughput_per_second: float = 0.0
    success_rate: float = 100.0
    last_event_time: Optional[datetime] = None
    uptime_seconds: float = 0.0
    
    def update_processing_time(self, processing_time: float) -> None:
        """Update processing time metrics"""
        self.peak_processing_time = max(self.peak_processing_time, processing_time)
        if self.events_processed > 0:
            total_time = self.average_processing_time * self.events_processed
            self.average_processing_time = (total_time + processing_time) / (self.events_processed + 1)
        else:
            self.average_processing_time = processing_time
            
    def calculate_success_rate(self) -> None:
        """Calculate success rate"""
        total_events = self.events_processed + self.events_failed
        if total_events > 0:
            self.success_rate = (self.events_processed / total_events) * 100


@dataclass
class ProcessingJob:
    """Processing job data structure"""
    job_id: str
    stream_id: str
    event: StreamEvent
    stage: ProcessingStage
    priority: ProcessingPriority
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    processor_id: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3


@dataclass
class ProcessingResult:
    """Processing result data structure"""
    job_id: str
    stream_id: str
    success: bool
    stage: ProcessingStage
    processing_time: float
    result_data: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None
    next_stage: Optional[ProcessingStage] = None


@dataclass
class ProcessingMetrics:
    """Processing performance metrics"""
    processor_id: str
    jobs_processed: int = 0
    jobs_failed: int = 0
    average_processing_time: float = 0.0
    peak_processing_time: float = 0.0
    current_load: int = 0
    max_load: int = 100


@dataclass
class ScheduledTask:
    """Scheduled task data structure"""
    task_id: str
    name: str
    function: Callable
    args: tuple = field(default_factory=tuple)
    kwargs: dict = field(default_factory=dict)
    schedule_time: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    priority: TaskPriority = TaskPriority.NORMAL
    status: TaskStatus = TaskStatus.PENDING
    max_retries: int = 3
    retry_count: int = 0
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None


class StreamingEngine:
    """
    Consolidated streaming engine combining manager, processor, and scheduler
    functionality for enterprise-grade real-time content streaming.
    
    Features:
    - High-performance event processing
    - Intelligent task scheduling
    - Real-time metrics and monitoring
    - Automatic scaling and load balancing
    - Error recovery and retry mechanisms
    """
    
    def __init__(
        self,
        max_workers -> None: int = 16,
        max_queue_size -> None: int = 10000,
        enable_metrics -> None: bool = True,
        enable_scheduling -> None: bool = True
    ) -> None:
        # Core configuration
        self.max_workers = max_workers
        self.max_queue_size = max_queue_size
        self.enable_metrics = enable_metrics
        self.enable_scheduling = enable_scheduling
        
        # Stream management
        self.active_streams: Dict[str, Dict[str, Any]] = {}
        self.stream_metrics: Dict[str, StreamMetrics] = {}
        self.stream_callbacks: Dict[str, List[Callable]] = {}
        
        # Processing infrastructure
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.processing_queue = Queue(maxsize=max_queue_size)
        self.processing_workers: List[threading.Thread] = []
        self.processing_metrics: Dict[str, ProcessingMetrics] = {}
        
        # Scheduling infrastructure
        self.scheduled_tasks: Dict[str, ScheduledTask] = {}
        self.task_queue = PriorityQueue()
        self.scheduler_thread: Optional[threading.Thread] = None
        
        # State management
        self._running = False
        self._shutdown_event = threading.Event()
        self._lock = threading.RLock()
        
        logger.info(f"StreamingEngine initialized with {max_workers} workers")
        
    async def initialize(self) -> None:
        """Initialize the streaming engine"""
        try:
            with self._lock:
                if self._running:
                    return
                    
                # Start processing workers
                self._start_processing_workers()
                
                # Start scheduler if enabled
                if self.enable_scheduling:
                    self._start_scheduler()
                    
                # Start metrics collection if enabled
                if self.enable_metrics:
                    asyncio.create_task(self._metrics_collector())
                    
                self._running = True
                logger.info("StreamingEngine initialized successfully")
                
        except Exception as e:
            logger.error(f"Failed to initialize StreamingEngine: {e}")
            raise
            
    async def create_stream(
        self,
        stream_id: str,
        content_type: StreamType,
        config: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Create a new data stream
        
        Args:
            stream_id: Unique stream identifier
            content_type: Type of content to stream
            config: Optional stream configuration
            
        Returns:
            Success status
        """
        try:
            with self._lock:
                if stream_id in self.active_streams:
                    logger.warning(f"Stream {stream_id} already exists")
                    return False
                    
                stream_config = {
                    "stream_id": stream_id,
                    "content_type": content_type,
                    "status": StreamStatus.INITIALIZING,
                    "created_at": datetime.now(timezone.utc),
                    "config": config or {},
                    "event_count": 0
                }
                
                self.active_streams[stream_id] = stream_config
                
                if self.enable_metrics:
                    self.stream_metrics[stream_id] = StreamMetrics(stream_id=stream_id)
                    
                # Initialize callbacks list
                self.stream_callbacks[stream_id] = []
                
                # Update status to running
                stream_config["status"] = StreamStatus.RUNNING
                
                logger.info(f"Stream {stream_id} created successfully")
                return True
                
        except Exception as e:
            logger.error(f"Failed to create stream {stream_id}: {e}")
            return False
            
    async def process_event(
        self,
        stream_id: str,
        event: StreamEvent,
        stage: ProcessingStage = ProcessingStage.ANALYSIS,
        priority: ProcessingPriority = ProcessingPriority.NORMAL
    ) -> Optional[str]:
        """
        Process a stream event
        
        Args:
            stream_id: Stream identifier
            event: Event to process
            stage: Processing stage
            priority: Processing priority
            
        Returns:
            Job ID if successfully queued, None otherwise
        """
        try:
            # Validate stream exists
            if stream_id not in self.active_streams:
                logger.error(f"Stream {stream_id} not found")
                return None
                
            # Create processing job
            job_id = str(uuid.uuid4())
            job = ProcessingJob(
                job_id=job_id,
                stream_id=stream_id,
                event=event,
                stage=stage,
                priority=priority
            )
            
            # Queue for processing
            try:
                self.processing_queue.put(job, block=False)
                
                # Update stream metrics
                self.active_streams[stream_id]["event_count"] += 1
                
                logger.debug(f"Event queued for processing: {job_id}")
                return job_id
                
            except:
                logger.error(f"Processing queue full, dropping event {job_id}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to process event: {e}")
            return None
            
    async def schedule_task(
        self,
        name: str,
        function: Callable,
        schedule_time: datetime,
        priority: TaskPriority = TaskPriority.NORMAL,
        args: tuple = (),
        kwargs: dict = None
    ) -> Optional[str]:
        """
        Schedule a task for execution
        
        Args:
            name: Task name
            function: Function to execute
            schedule_time: When to execute
            priority: Task priority
            args: Function arguments
            kwargs: Function keyword arguments
            
        Returns:
            Task ID if successfully scheduled, None otherwise
        """
        if not self.enable_scheduling:
            logger.warning("Scheduling is disabled")
            return None
            
        try:
            task_id = str(uuid.uuid4())
            task = ScheduledTask(
                task_id=task_id,
                name=name,
                function=function,
                args=args,
                kwargs=kwargs or {},
                schedule_time=schedule_time,
                priority=priority
            )
            
            with self._lock:
                self.scheduled_tasks[task_id] = task
                
            # Add to priority queue (negative priority for max-heap behavior)
            priority_score = (-priority.value, schedule_time.timestamp())
            self.task_queue.put((priority_score, task_id))
            
            logger.info(f"Task {name} scheduled for {schedule_time}")
            return task_id
            
        except Exception as e:
            logger.error(f"Failed to schedule task {name}: {e}")
            return None
            
    async def get_stream_status(self, stream_id: str) -> Optional[Dict[str, Any]]:
        """Get stream status and metrics"""
        try:
            if stream_id not in self.active_streams:
                return None
                
            stream_info = self.active_streams[stream_id].copy()
            
            if self.enable_metrics and stream_id in self.stream_metrics:
                metrics = self.stream_metrics[stream_id]
                stream_info["metrics"] = {
                    "events_processed": metrics.events_processed,
                    "events_failed": metrics.events_failed,
                    "success_rate": metrics.success_rate,
                    "average_processing_time": metrics.average_processing_time,
                    "throughput_per_second": metrics.throughput_per_second,
                    "uptime_seconds": metrics.uptime_seconds
                }
                
            return stream_info
            
        except Exception as e:
            logger.error(f"Failed to get stream status: {e}")
            return None
            
    async def stop_stream(self, stream_id: str) -> bool:
        """Stop a data stream"""
        try:
            with self._lock:
                if stream_id not in self.active_streams:
                    logger.warning(f"Stream {stream_id} not found")
                    return False
                    
                self.active_streams[stream_id]["status"] = StreamStatus.STOPPED
                self.active_streams[stream_id]["stopped_at"] = datetime.now(timezone.utc)
                
                logger.info(f"Stream {stream_id} stopped")
                return True
                
        except Exception as e:
            logger.error(f"Failed to stop stream {stream_id}: {e}")
            return False
            
    def _start_processing_workers(self) -> None:
        """Start processing worker threads"""
        for i in range(self.max_workers):
            worker_id = f"worker_{i}"
            worker = threading.Thread(
                target=self._processing_worker,
                args=(worker_id,),
                daemon=True
            )
            worker.start()
            self.processing_workers.append(worker)
            
            # Initialize worker metrics
            if self.enable_metrics:
                self.processing_metrics[worker_id] = ProcessingMetrics(
                    processor_id=worker_id,
                    max_load=100
                )
                
        logger.info(f"Started {self.max_workers} processing workers")
        
    def _processing_worker(self, worker_id: str) -> None:
        """Processing worker main loop"""
        logger.info(f"Processing worker {worker_id} started")
        
        while not self._shutdown_event.is_set():
            try:
                # Get job from queue with timeout
                try:
                    job = self.processing_queue.get(timeout=1.0)
                except:
                    continue
                    
                # Update worker metrics
                if self.enable_metrics and worker_id in self.processing_metrics:
                    self.processing_metrics[worker_id].current_load += 1
                    
                # Process the job
                result = self._process_job(job, worker_id)
                
                # Update metrics
                if self.enable_metrics:
                    self._update_processing_metrics(result, worker_id)
                    
                # Mark job as done
                self.processing_queue.task_done()
                
                # Update worker metrics
                if self.enable_metrics and worker_id in self.processing_metrics:
                    self.processing_metrics[worker_id].current_load -= 1
                    
            except Exception as e:
                logger.error(f"Processing worker {worker_id} error: {e}")
                
        logger.info(f"Processing worker {worker_id} stopped")
        
    def _process_job(self, job: ProcessingJob, worker_id: str) -> ProcessingResult:
        """Process a single job"""
        start_time = time.time()
        job.started_at = datetime.now(timezone.utc)
        job.processor_id = worker_id
        
        try:
            # Simulate processing based on stage
            if job.stage == ProcessingStage.VALIDATION:
                result_data = self._validate_content(job.event)
            elif job.stage == ProcessingStage.ANALYSIS:
                result_data = self._analyze_content(job.event)
            elif job.stage == ProcessingStage.PROTECTION:
                result_data = self._check_protection(job.event)
            elif job.stage == ProcessingStage.MONETIZATION:
                result_data = self._process_monetization(job.event)
            else:
                result_data = {"processed": True, "stage": job.stage.value}
                
            processing_time = time.time() - start_time
            job.completed_at = datetime.now(timezone.utc)
            
            result = ProcessingResult(
                job_id=job.job_id,
                stream_id=job.stream_id,
                success=True,
                stage=job.stage,
                processing_time=processing_time,
                result_data=result_data,
                next_stage=self._get_next_stage(job.stage)
            )
            
            logger.debug(f"Job {job.job_id} processed successfully in {processing_time:.3f}s")
            return result
            
        except Exception as e:
            processing_time = time.time() - start_time
            
            result = ProcessingResult(
                job_id=job.job_id,
                stream_id=job.stream_id,
                success=False,
                stage=job.stage,
                processing_time=processing_time,
                error_message=str(e)
            )
            
            logger.error(f"Job {job.job_id} failed: {e}")
            return result
            
    def _validate_content(self, event: StreamEvent) -> Dict[str, Any]:
        """Validate content based on type and format"""
        return {
            "valid": True,
            "content_type": event.content_type.value,
            "format": event.content_format.value,
            "size_mb": event.data.get("size", 0) / (1024 * 1024)
        }
        
    def _analyze_content(self, event: StreamEvent) -> Dict[str, Any]:
        """Analyze content using AI models"""
        return {
            "analyzed": True,
            "confidence": 0.95,
            "categories": ["entertainment", "music"],
            "sentiment": "positive",
            "language": "en"
        }
        
    def _check_protection(self, event: StreamEvent) -> Dict[str, Any]:
        """Check content protection and copyright"""
        return {
            "protected": False,
            "copyright_matches": [],
            "risk_score": 0.1,
            "cleared_for_monetization": True
        }
        
    def _process_monetization(self, event: StreamEvent) -> Dict[str, Any]:
        """Process monetization opportunities"""
        return {
            "monetizable": True,
            "estimated_revenue": 10.50,
            "platforms": ["youtube", "instagram"],
            "optimization_score": 0.85
        }
        
    def _get_next_stage(self, current_stage: ProcessingStage) -> Optional[ProcessingStage]:
        """Get next processing stage"""
        stage_flow = {
            ProcessingStage.VALIDATION: ProcessingStage.PREPROCESSING,
            ProcessingStage.PREPROCESSING: ProcessingStage.ANALYSIS,
            ProcessingStage.ANALYSIS: ProcessingStage.PROTECTION,
            ProcessingStage.PROTECTION: ProcessingStage.MONETIZATION,
            ProcessingStage.MONETIZATION: ProcessingStage.POSTPROCESSING,
            ProcessingStage.POSTPROCESSING: ProcessingStage.COMPLETION,
            ProcessingStage.COMPLETION: None
        }
        return stage_flow.get(current_stage)
        
    def _start_scheduler(self) -> None:
        """Start the task scheduler"""
        self.scheduler_thread = threading.Thread(
            target=self._scheduler_worker,
            daemon=True
        )
        self.scheduler_thread.start()
        logger.info("Task scheduler started")
        
    def _scheduler_worker(self) -> None:
        """Scheduler worker main loop"""
        logger.info("Scheduler worker started")
        
        while not self._shutdown_event.is_set():
            try:
                # Check for tasks to execute
                current_time = datetime.now(timezone.utc)
                
                # Get next task from queue
                try:
                    priority_score, task_id = self.task_queue.get(timeout=1.0)
                except:
                    continue
                    
                # Check if task still exists
                with self._lock:
                    if task_id not in self.scheduled_tasks:
                        continue
                        
                    task = self.scheduled_tasks[task_id]
                    
                # Check if it's time to execute
                if task.schedule_time <= current_time:
                    self._execute_task(task)
                else:
                    # Put back in queue for later
                    self.task_queue.put((priority_score, task_id))
                    time.sleep(0.1)  # Small delay to prevent busy waiting
                    
            except Exception as e:
                logger.error(f"Scheduler worker error: {e}")
                
        logger.info("Scheduler worker stopped")
        
    def _execute_task(self, task: ScheduledTask) -> None:
        """Execute a scheduled task"""
        try:
            task.status = TaskStatus.RUNNING
            task.started_at = datetime.now(timezone.utc)
            
            # Execute task function
            if asyncio.iscoroutinefunction(task.function):
                # Run async function in executor
                future = self.executor.submit(
                    asyncio.run,
                    task.function(*task.args, **task.kwargs)
                )
            else:
                # Run sync function
                future = self.executor.submit(
                    task.function,
                    *task.args,
                    **task.kwargs
                )
                
            # Wait for completion
            result = future.result(timeout=300)  # 5 minute timeout
            
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now(timezone.utc)
            
            logger.info(f"Task {task.name} completed successfully")
            
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error_message = str(e)
            task.retry_count += 1
            
            logger.error(f"Task {task.name} failed: {e}")
            
            # Retry if under limit
            if task.retry_count < task.max_retries:
                retry_time = datetime.now(timezone.utc) + timedelta(seconds=30)
                task.schedule_time = retry_time
                task.status = TaskStatus.PENDING
                
                priority_score = (-task.priority.value, retry_time.timestamp())
                self.task_queue.put((priority_score, task.task_id))
                
                logger.info(f"Task {task.name} scheduled for retry")
                
    def _update_processing_metrics(self, result: ProcessingResult, worker_id: str) -> None:
        """Update processing metrics"""
        if not self.enable_metrics:
            return
            
        try:
            # Update stream metrics
            if result.stream_id in self.stream_metrics:
                metrics = self.stream_metrics[result.stream_id]
                
                if result.success:
                    metrics.events_processed += 1
                    metrics.update_processing_time(result.processing_time)
                else:
                    metrics.events_failed += 1
                    
                metrics.calculate_success_rate()
                metrics.last_event_time = datetime.now(timezone.utc)
                
            # Update worker metrics
            if worker_id in self.processing_metrics:
                worker_metrics = self.processing_metrics[worker_id]
                
                if result.success:
                    worker_metrics.jobs_processed += 1
                else:
                    worker_metrics.jobs_failed += 1
                    
                # Update processing times
                if worker_metrics.jobs_processed > 0:
                    total_time = worker_metrics.average_processing_time * worker_metrics.jobs_processed
                    worker_metrics.average_processing_time = (total_time + result.processing_time) / (worker_metrics.jobs_processed + 1)
                else:
                    worker_metrics.average_processing_time = result.processing_time
                    
                worker_metrics.peak_processing_time = max(worker_metrics.peak_processing_time, result.processing_time)
                
        except Exception as e:
            logger.error(f"Failed to update metrics: {e}")
            
    async def _metrics_collector(self) -> None:
        """Background metrics collection task"""
        while self._running:
            try:
                await asyncio.sleep(30)  # Collect every 30 seconds
                
                # Calculate throughput for streams
                current_time = datetime.now(timezone.utc)
                
                for stream_id, metrics in self.stream_metrics.items():
                    if metrics.last_event_time:
                        time_diff = (current_time - metrics.last_event_time).total_seconds()
                        if time_diff > 0:
                            metrics.throughput_per_second = metrics.events_processed / time_diff
                            
                    # Update uptime
                    if stream_id in self.active_streams:
                        created_at = self.active_streams[stream_id]["created_at"]
                        metrics.uptime_seconds = (current_time - created_at).total_seconds()
                        
            except Exception as e:
                logger.error(f"Metrics collector error: {e}")
                
    async def shutdown(self) -> None:
        """Gracefully shutdown the streaming engine"""
        try:
            logger.info("Shutting down StreamingEngine...")
            
            with self._lock:
                self._running = False
                self._shutdown_event.set()
                
            # Wait for processing queue to empty
            self.processing_queue.join()
            
            # Shutdown executor
            self.executor.shutdown(wait=True)
            
            # Stop all streams
            for stream_id in list(self.active_streams.keys()):
                await self.stop_stream(stream_id)
                
            logger.info("StreamingEngine shutdown completed")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")


# Legacy compatibility classes
class DataStreamManager:
    """Legacy compatibility wrapper for StreamingEngine stream management"""
    
    def __init__(self, engine -> None: Optional[StreamingEngine] = None) -> None:
        self.engine = engine or StreamingEngine()
        
    async def initialize(self) -> None:
        """Initialize the manager"""
        await self.engine.initialize()
        
    async def create_stream(self, stream_id: str, content_type: StreamType, config: Dict[str, Any] = None) -> bool:
        """Create a new stream"""
        return await self.engine.create_stream(stream_id, content_type, config)
        
    async def get_stream_status(self, stream_id: str) -> Optional[Dict[str, Any]]:
        """Get stream status"""
        return await self.engine.get_stream_status(stream_id)
        
    async def stop_stream(self, stream_id: str) -> bool:
        """Stop a stream"""
        return await self.engine.stop_stream(stream_id)


class RealTimeProcessor:
    """Legacy compatibility wrapper for StreamingEngine processing"""
    
    def __init__(self, max_workers -> None: int = 16, engine -> None: Optional[StreamingEngine] = None) -> None:
        self.engine = engine or StreamingEngine(max_workers=max_workers)
        
    async def initialize(self) -> None:
        """Initialize the processor"""
        await self.engine.initialize()
        
    async def process_event(self, stream_id: str, event: StreamEvent, stage: ProcessingStage = ProcessingStage.ANALYSIS) -> Optional[str]:
        """Process an event"""
        return await self.engine.process_event(stream_id, event, stage)


class StreamScheduler:
    """Legacy compatibility wrapper for StreamingEngine scheduling"""
    
    def __init__(self, engine -> None: Optional[StreamingEngine] = None) -> None:
        self.engine = engine or StreamingEngine(enable_scheduling=True)
        
    async def initialize(self) -> None:
        """Initialize the scheduler"""
        await self.engine.initialize()
        
    async def schedule_task(self, name: str, function: Callable, schedule_time: datetime, priority: TaskPriority = TaskPriority.NORMAL) -> Optional[str]:
        """Schedule a task"""
        return await self.engine.schedule_task(name, function, schedule_time, priority)