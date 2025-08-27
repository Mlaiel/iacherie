"""
Multimedia Batch Processor - Enterprise Batch Processing System

High-performance batch processing system for large-scale multimedia operations.
Provides distributed processing, job scheduling, and resource optimization.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code and concept are the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, copying, distribution, or commercialization without explicit written permission is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.
"""

import asyncio
import logging
import uuid
import pickle
import hashlib
from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone, timedelta
from enum import Enum
from pathlib import Path
import concurrent.futures
import multiprocessing
import json

# Queue systems
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

try:
    import celery
    CELERY_AVAILABLE = True
except ImportError:
    CELERY_AVAILABLE = False

# Database
try:
    import psycopg2
    import sqlalchemy
    DATABASE_AVAILABLE = True
except ImportError:
    DATABASE_AVAILABLE = False

# Progress tracking
try:
    from tqdm import tqdm
    TQDM_AVAILABLE = True
except ImportError:
    TQDM_AVAILABLE = False

logger = logging.getLogger(__name__)


class JobStatus(Enum):
    """Job status enumeration"""
    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"


class JobPriority(Enum):
    """Job priority levels"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4
    CRITICAL = 5


class ProcessingStrategy(Enum):
    """Processing strategies"""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    DISTRIBUTED = "distributed"
    ADAPTIVE = "adaptive"


@dataclass
class BatchJob:
    """Batch processing job definition"""
    job_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    job_name: str = ""
    description: str = ""
    
    # Job configuration
    input_files: List[str] = field(default_factory=list)
    output_directory: str = ""
    processing_function: Optional[str] = None
    processing_parameters: Dict[str, Any] = field(default_factory=dict)
    
    # Execution settings
    priority: JobPriority = JobPriority.NORMAL
    strategy: ProcessingStrategy = ProcessingStrategy.PARALLEL
    max_workers: Optional[int] = None
    max_retries: int = 3
    retry_delay: float = 5.0
    timeout: Optional[float] = None
    
    # Resource requirements
    memory_limit: Optional[str] = None  # e.g., "4GB"
    cpu_limit: Optional[int] = None
    gpu_required: bool = False
    
    # Scheduling
    scheduled_at: Optional[datetime] = None
    deadline: Optional[datetime] = None
    
    # Status and tracking
    status: JobStatus = JobStatus.PENDING
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Progress tracking
    total_items: int = 0
    processed_items: int = 0
    failed_items: int = 0
    progress_percentage: float = 0.0
    
    # Results and metadata
    results: Dict[str, Any] = field(default_factory=dict)
    error_log: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # User information
    created_by: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    
    def update_progress(self):
        """Update progress percentage"""
        if self.total_items > 0:
            self.progress_percentage = (self.processed_items / self.total_items) * 100
    
    def add_error(self, error_message: str):
        """Add error to log"""
        timestamp = datetime.now(timezone.utc).isoformat()
        self.error_log.append(f"[{timestamp}] {error_message}")
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        # Convert datetime objects to ISO strings
        for field in ['created_at', 'started_at', 'completed_at', 'scheduled_at', 'deadline']:
            if data[field]:
                data[field] = data[field].isoformat()
        return data


@dataclass
class BatchConfiguration:
    """Batch processing configuration"""
    max_concurrent_jobs: int = 5
    default_workers: int = 4
    enable_distributed: bool = False
    redis_url: Optional[str] = None
    database_url: Optional[str] = None
    result_backend: str = "redis"
    job_timeout: float = 3600.0  # 1 hour
    cleanup_completed_after: timedelta = timedelta(days=7)
    enable_progress_tracking: bool = True
    chunk_size: int = 100
    retry_exponential_backoff: bool = True


@dataclass
class ProcessingResult:
    """Processing result for individual item"""
    item_id: str
    input_file: str
    output_file: Optional[str] = None
    success: bool = True
    processing_time: float = 0.0
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class MultimediaBatchProcessor:
    """Enterprise multimedia batch processor"""
    
    def __init__(self, config: BatchConfiguration):
        self.config = config
        
        # Job storage and queues
        self.jobs: Dict[str, BatchJob] = {}
        self.job_queue = asyncio.Queue(maxsize=1000)
        self.active_jobs: Dict[str, asyncio.Task] = {}
        
        # Processing components
        self.worker_pool = None
        self.redis_client = None
        self.database = None
        
        # Processing functions registry
        self.processing_functions: Dict[str, Callable] = {}
        
        # Statistics
        self.stats = {
            "total_jobs": 0,
            "completed_jobs": 0,
            "failed_jobs": 0,
            "cancelled_jobs": 0,
            "total_items_processed": 0,
            "average_job_duration": 0.0,
            "system_uptime": datetime.now(timezone.utc)
        }
        
        # Event handlers
        self.job_started_handlers: List[Callable] = []
        self.job_completed_handlers: List[Callable] = []
        self.job_failed_handlers: List[Callable] = []
        self.progress_handlers: List[Callable] = []
        
    async def initialize(self):
        """Initialize the batch processor"""
        try:
            # Initialize worker pool
            max_workers = min(self.config.max_concurrent_jobs, multiprocessing.cpu_count())
            self.worker_pool = concurrent.futures.ProcessPoolExecutor(max_workers=max_workers)
            
            # Initialize Redis if available
            if REDIS_AVAILABLE and self.config.redis_url:
                self.redis_client = redis.from_url(self.config.redis_url)
                await self._test_redis_connection()
                
            # Initialize database if available
            if DATABASE_AVAILABLE and self.config.database_url:
                await self._initialize_database()
                
            # Register default processing functions
            await self._register_default_functions()
            
            # Start job scheduler
            asyncio.create_task(self._job_scheduler())
            
            # Start cleanup task
            asyncio.create_task(self._cleanup_task())
            
            logger.info("Multimedia batch processor initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize batch processor: {e}")
            raise
            
    async def submit_job(self, job: BatchJob) -> str:
        """Submit a job for processing"""
        try:
            # Validate job
            await self._validate_job(job)
            
            # Set total items
            job.total_items = len(job.input_files)
            
            # Store job
            self.jobs[job.job_id] = job
            
            # Persist to database if available
            if self.database:
                await self._persist_job(job)
                
            # Add to queue or schedule
            if job.scheduled_at and job.scheduled_at > datetime.now(timezone.utc):
                # Schedule for later
                job.status = JobStatus.PENDING
            else:
                # Queue immediately
                await self.job_queue.put(job.job_id)
                job.status = JobStatus.QUEUED
                
            # Update statistics
            self.stats["total_jobs"] += 1
            
            logger.info(f"Job submitted: {job.job_id}")
            return job.job_id
            
        except Exception as e:
            logger.error(f"Failed to submit job: {e}")
            raise
            
    async def get_job_status(self, job_id: str) -> Optional[BatchJob]:
        """Get job status and details"""
        if job_id in self.jobs:
            return self.jobs[job_id]
        elif self.database:
            return await self._load_job_from_database(job_id)
        return None
        
    async def cancel_job(self, job_id: str) -> bool:
        """Cancel a job"""
        try:
            job = await self.get_job_status(job_id)
            if not job:
                return False
                
            if job.status in [JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED]:
                return False
                
            # Cancel active job
            if job_id in self.active_jobs:
                task = self.active_jobs[job_id]
                task.cancel()
                
            # Update status
            job.status = JobStatus.CANCELLED
            job.completed_at = datetime.now(timezone.utc)
            
            # Persist changes
            if self.database:
                await self._persist_job(job)
                
            # Update statistics
            self.stats["cancelled_jobs"] += 1
            
            logger.info(f"Job cancelled: {job_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to cancel job {job_id}: {e}")
            return False
            
    async def retry_job(self, job_id: str) -> bool:
        """Retry a failed job"""
        try:
            job = await self.get_job_status(job_id)
            if not job or job.status != JobStatus.FAILED:
                return False
                
            # Reset job state
            job.status = JobStatus.QUEUED
            job.started_at = None
            job.completed_at = None
            job.processed_items = 0
            job.failed_items = 0
            job.progress_percentage = 0.0
            job.results.clear()
            
            # Re-queue job
            await self.job_queue.put(job_id)
            
            logger.info(f"Job requeued for retry: {job_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to retry job {job_id}: {e}")
            return False
            
    async def list_jobs(
        self, 
        status: Optional[JobStatus] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[BatchJob]:
        """List jobs with optional filtering"""
        try:
            jobs = list(self.jobs.values())
            
            # Filter by status
            if status:
                jobs = [job for job in jobs if job.status == status]
                
            # Sort by creation time (newest first)
            jobs.sort(key=lambda x: x.created_at, reverse=True)
            
            # Apply pagination
            return jobs[offset:offset + limit]
            
        except Exception as e:
            logger.error(f"Failed to list jobs: {e}")
            return []
            
    async def get_statistics(self) -> Dict[str, Any]:
        """Get processing statistics"""
        try:
            # Update uptime
            uptime = datetime.now(timezone.utc) - self.stats["system_uptime"]
            
            return {
                **self.stats,
                "uptime_seconds": uptime.total_seconds(),
                "active_jobs": len(self.active_jobs),
                "queued_jobs": self.job_queue.qsize(),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get statistics: {e}")
            return {}
            
    async def register_processing_function(
        self, 
        name: str, 
        function: Callable
    ):
        """Register a processing function"""
        self.processing_functions[name] = function
        logger.info(f"Processing function registered: {name}")
        
    async def add_job_started_handler(self, handler: Callable):
        """Add job started event handler"""
        self.job_started_handlers.append(handler)
        
    async def add_job_completed_handler(self, handler: Callable):
        """Add job completed event handler"""
        self.job_completed_handlers.append(handler)
        
    async def add_job_failed_handler(self, handler: Callable):
        """Add job failed event handler"""
        self.job_failed_handlers.append(handler)
        
    async def add_progress_handler(self, handler: Callable):
        """Add progress update handler"""
        self.progress_handlers.append(handler)
        
    async def health_check(self) -> Dict[str, Any]:
        """System health check"""
        try:
            health = {
                "status": "healthy",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "worker_pool": "available" if self.worker_pool else "unavailable",
                "redis": "connected" if self.redis_client else "not_configured",
                "database": "connected" if self.database else "not_configured",
                "active_jobs": len(self.active_jobs),
                "queue_size": self.job_queue.qsize()
            }
            
            # Test Redis connection
            if self.redis_client:
                try:
                    await self.redis_client.ping()
                    health["redis"] = "connected"
                except:
                    health["redis"] = "disconnected"
                    health["status"] = "degraded"
                    
            # Check worker pool
            if not self.worker_pool:
                health["status"] = "degraded"
                
            return health
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
    # Private methods
    
    async def _job_scheduler(self):
        """Main job scheduling loop"""
        while True:
            try:
                # Process scheduled jobs
                await self._process_scheduled_jobs()
                
                # Process queued jobs
                if len(self.active_jobs) < self.config.max_concurrent_jobs:
                    try:
                        job_id = await asyncio.wait_for(self.job_queue.get(), timeout=1.0)
                        await self._start_job(job_id)
                    except asyncio.TimeoutError:
                        pass
                        
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"Job scheduler error: {e}")
                await asyncio.sleep(5)
                
    async def _process_scheduled_jobs(self):
        """Process scheduled jobs that are ready"""
        current_time = datetime.now(timezone.utc)
        
        for job in self.jobs.values():
            if (job.status == JobStatus.PENDING and 
                job.scheduled_at and 
                job.scheduled_at <= current_time):
                
                job.status = JobStatus.QUEUED
                await self.job_queue.put(job.job_id)
                
    async def _start_job(self, job_id: str):
        """Start processing a job"""
        try:
            job = self.jobs[job_id]
            job.status = JobStatus.RUNNING
            job.started_at = datetime.now(timezone.utc)
            
            # Create processing task
            task = asyncio.create_task(self._process_job(job))
            self.active_jobs[job_id] = task
            
            # Trigger event handlers
            for handler in self.job_started_handlers:
                try:
                    await self._call_handler(handler, job)
                except Exception as e:
                    logger.error(f"Job started handler error: {e}")
                    
            logger.info(f"Job started: {job_id}")
            
        except Exception as e:
            logger.error(f"Failed to start job {job_id}: {e}")
            
    async def _process_job(self, job: BatchJob):
        """Process a batch job"""
        try:
            # Get processing function
            if job.processing_function not in self.processing_functions:
                raise ValueError(f"Processing function not found: {job.processing_function}")
                
            processing_func = self.processing_functions[job.processing_function]
            
            # Determine processing strategy
            if job.strategy == ProcessingStrategy.SEQUENTIAL:
                await self._process_sequential(job, processing_func)
            elif job.strategy == ProcessingStrategy.PARALLEL:
                await self._process_parallel(job, processing_func)
            elif job.strategy == ProcessingStrategy.DISTRIBUTED:
                await self._process_distributed(job, processing_func)
            else:  # ADAPTIVE
                await self._process_adaptive(job, processing_func)
                
            # Mark as completed
            job.status = JobStatus.COMPLETED
            job.completed_at = datetime.now(timezone.utc)
            
            # Update statistics
            self.stats["completed_jobs"] += 1
            self.stats["total_items_processed"] += job.processed_items
            
            # Calculate average job duration
            job_duration = (job.completed_at - job.started_at).total_seconds()
            total_completed = self.stats["completed_jobs"]
            current_avg = self.stats["average_job_duration"]
            new_avg = ((current_avg * (total_completed - 1)) + job_duration) / total_completed
            self.stats["average_job_duration"] = new_avg
            
            # Trigger completion handlers
            for handler in self.job_completed_handlers:
                try:
                    await self._call_handler(handler, job)
                except Exception as e:
                    logger.error(f"Job completed handler error: {e}")
                    
            logger.info(f"Job completed: {job.job_id}")
            
        except Exception as e:
            logger.error(f"Job processing failed {job.job_id}: {e}")
            
            # Mark as failed
            job.status = JobStatus.FAILED
            job.completed_at = datetime.now(timezone.utc)
            job.add_error(str(e))
            
            # Update statistics
            self.stats["failed_jobs"] += 1
            
            # Trigger failure handlers
            for handler in self.job_failed_handlers:
                try:
                    await self._call_handler(handler, job)
                except Exception as e:
                    logger.error(f"Job failed handler error: {e}")
                    
        finally:
            # Cleanup
            self.active_jobs.pop(job.job_id, None)
            
            # Persist job state
            if self.database:
                await self._persist_job(job)
                
    async def _process_sequential(self, job: BatchJob, processing_func: Callable):
        """Process files sequentially"""
        for i, input_file in enumerate(job.input_files):
            try:
                # Process single file
                result = await self._process_single_file(
                    input_file, processing_func, job.processing_parameters, job.output_directory
                )
                
                # Update progress
                if result.success:
                    job.processed_items += 1
                else:
                    job.failed_items += 1
                    job.add_error(f"Failed to process {input_file}: {result.error_message}")
                    
                job.results[input_file] = result
                job.update_progress()
                
                # Trigger progress handlers
                await self._trigger_progress_handlers(job)
                
            except Exception as e:
                job.failed_items += 1
                job.add_error(f"Error processing {input_file}: {str(e)}")
                
    async def _process_parallel(self, job: BatchJob, processing_func: Callable):
        """Process files in parallel"""
        max_workers = job.max_workers or self.config.default_workers
        semaphore = asyncio.Semaphore(max_workers)
        
        async def process_with_semaphore(input_file):
            async with semaphore:
                return await self._process_single_file(
                    input_file, processing_func, job.processing_parameters, job.output_directory
                )
                
        # Create tasks for all files
        tasks = [process_with_semaphore(file) for file in job.input_files]
        
        # Process with progress tracking
        for i, task in enumerate(asyncio.as_completed(tasks)):
            try:
                result = await task
                input_file = job.input_files[i]  # This is simplified - in practice, you'd need better tracking
                
                # Update progress
                if result.success:
                    job.processed_items += 1
                else:
                    job.failed_items += 1
                    job.add_error(f"Failed to process {input_file}: {result.error_message}")
                    
                job.results[input_file] = result
                job.update_progress()
                
                # Trigger progress handlers
                await self._trigger_progress_handlers(job)
                
            except Exception as e:
                job.failed_items += 1
                job.add_error(f"Error in parallel processing: {str(e)}")
                
    async def _process_distributed(self, job: BatchJob, processing_func: Callable):
        """Process files using distributed workers (Celery)"""
        if not CELERY_AVAILABLE:
            logger.warning("Celery not available, falling back to parallel processing")
            await self._process_parallel(job, processing_func)
            return
            
        # This would implement Celery-based distributed processing
        # For now, fall back to parallel
        await self._process_parallel(job, processing_func)
        
    async def _process_adaptive(self, job: BatchJob, processing_func: Callable):
        """Adaptively choose processing strategy based on job characteristics"""
        # Simple heuristics for choosing strategy
        if len(job.input_files) < 10:
            await self._process_sequential(job, processing_func)
        elif len(job.input_files) < 100:
            await self._process_parallel(job, processing_func)
        else:
            await self._process_distributed(job, processing_func)
            
    async def _process_single_file(
        self, 
        input_file: str, 
        processing_func: Callable,
        parameters: Dict[str, Any],
        output_directory: str
    ) -> ProcessingResult:
        """Process a single file"""
        start_time = datetime.now()
        result = ProcessingResult(
            item_id=str(uuid.uuid4()),
            input_file=input_file
        )
        
        try:
            # Generate output file path
            input_path = Path(input_file)
            output_path = Path(output_directory) / f"processed_{input_path.name}"
            result.output_file = str(output_path)
            
            # Run processing function
            if asyncio.iscoroutinefunction(processing_func):
                await processing_func(input_file, str(output_path), **parameters)
            else:
                # Run in executor for CPU-bound tasks
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(
                    self.worker_pool,
                    processing_func,
                    input_file,
                    str(output_path),
                    parameters
                )
                
            result.success = True
            
        except Exception as e:
            result.success = False
            result.error_message = str(e)
            
        finally:
            result.processing_time = (datetime.now() - start_time).total_seconds()
            
        return result
        
    async def _trigger_progress_handlers(self, job: BatchJob):
        """Trigger progress update handlers"""
        for handler in self.progress_handlers:
            try:
                await self._call_handler(handler, job)
            except Exception as e:
                logger.error(f"Progress handler error: {e}")
                
    async def _call_handler(self, handler: Callable, data: Any):
        """Call event handler safely"""
        try:
            if asyncio.iscoroutinefunction(handler):
                await handler(data)
            else:
                handler(data)
        except Exception as e:
            logger.error(f"Handler execution failed: {e}")
            
    async def _validate_job(self, job: BatchJob):
        """Validate job configuration"""
        if not job.job_name:
            job.job_name = f"Job_{job.job_id[:8]}"
            
        if not job.input_files:
            raise ValueError("No input files specified")
            
        if not job.output_directory:
            raise ValueError("No output directory specified")
            
        if not job.processing_function:
            raise ValueError("No processing function specified")
            
        # Check if processing function exists
        if job.processing_function not in self.processing_functions:
            raise ValueError(f"Processing function not found: {job.processing_function}")
            
        # Validate file paths
        for file_path in job.input_files:
            if not Path(file_path).exists():
                raise ValueError(f"Input file not found: {file_path}")
                
        # Create output directory if it doesn't exist
        Path(job.output_directory).mkdir(parents=True, exist_ok=True)
        
    async def _cleanup_task(self):
        """Cleanup completed jobs periodically"""
        while True:
            try:
                await asyncio.sleep(3600)  # Run every hour
                
                cutoff_time = datetime.now(timezone.utc) - self.config.cleanup_completed_after
                
                jobs_to_remove = []
                for job_id, job in self.jobs.items():
                    if (job.status in [JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED] and
                        job.completed_at and job.completed_at < cutoff_time):
                        jobs_to_remove.append(job_id)
                        
                for job_id in jobs_to_remove:
                    del self.jobs[job_id]
                    
                if jobs_to_remove:
                    logger.info(f"Cleaned up {len(jobs_to_remove)} old jobs")
                    
            except Exception as e:
                logger.error(f"Cleanup task error: {e}")
                
    async def _test_redis_connection(self):
        """Test Redis connection"""
        if self.redis_client:
            await self.redis_client.ping()
            logger.info("Redis connection established")
            
    async def _initialize_database(self):
        """Initialize database connection"""
        # This would implement database initialization
        # For now, this is a placeholder
        logger.info("Database connection would be initialized here")
        
    async def _persist_job(self, job: BatchJob):
        """Persist job to database"""
        # This would implement job persistence
        # For now, this is a placeholder
        pass
        
    async def _load_job_from_database(self, job_id: str) -> Optional[BatchJob]:
        """Load job from database"""
        # This would implement job loading from database
        # For now, return None
        return None
        
    async def _register_default_functions(self):
        """Register default processing functions"""
        # Register basic image processing
        await self.register_processing_function("resize_image", self._resize_image)
        await self.register_processing_function("convert_format", self._convert_format)
        await self.register_processing_function("extract_metadata", self._extract_metadata)
        
    async def _resize_image(self, input_file: str, output_file: str, **kwargs):
        """Default image resize function"""
        # This would implement actual image resizing
        # For now, just copy the file
        import shutil
        shutil.copy2(input_file, output_file)
        
    async def _convert_format(self, input_file: str, output_file: str, **kwargs):
        """Default format conversion function"""
        # This would implement actual format conversion
        # For now, just copy the file
        import shutil
        shutil.copy2(input_file, output_file)
        
    async def _extract_metadata(self, input_file: str, output_file: str, **kwargs):
        """Default metadata extraction function"""
        # This would implement actual metadata extraction
        # For now, create a simple metadata file
        metadata = {"file": input_file, "extracted_at": datetime.now().isoformat()}
        with open(output_file, 'w') as f:
            json.dump(metadata, f, indent=2)
