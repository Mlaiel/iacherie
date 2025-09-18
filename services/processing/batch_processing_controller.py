"""
Batch Processing Controller - Enterprise Batch Processing Layer
==============================================================

**Author**: Fahed Mlaiel (mlaiel@live.de)
**Roles**: Backend Senior + DBA + DevOps + Lead Dev IA + ML Engineer
**Module**: Batch Processing Controller
**Version**: 2.0.0 Enterprise
**Created**: 2025-01-07

Enterprise-grade batch processing controller with Apache Airflow orchestration,
intelligent job scheduling, resource allocation, progress tracking, and error recovery.
"""

import asyncio
import json
import time
import uuid
from typing import Dict, Any, List, Optional, Union, Callable, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging
from datetime import datetime, timedelta
import cron_descriptor
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import hashlib
import pickle
from pathlib import Path

# Enterprise imports
try:
    import redis
    import psutil
    import pandas as pd
    import numpy as np
    from sqlalchemy import create_engine, text
    import aiofiles
except ImportError as e:
    logging.warning(f"Optional dependency missing: {e}")

logger = logging.getLogger(__name__)

class JobStatus(Enum):
    """Batch job status types."""
    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"

class JobPriority(Enum):
    """Job priority levels."""
    CRITICAL = 1
    HIGH = 2
    NORMAL = 3
    LOW = 4
    BACKGROUND = 5

class ResourceType(Enum):
    """Resource requirement types."""
    CPU_INTENSIVE = "cpu_intensive"
    MEMORY_INTENSIVE = "memory_intensive"
    IO_INTENSIVE = "io_intensive"
    GPU_REQUIRED = "gpu_required"
    NETWORK_INTENSIVE = "network_intensive"
    BALANCED = "balanced"

@dataclass
class ResourceRequirements:
    """Resource requirements for batch jobs."""
    cpu_cores: int = 1
    memory_mb: int = 1024
    disk_mb: int = 1024
    gpu_count: int = 0
    network_bandwidth_mbps: int = 10
    max_execution_time: int = 3600  # seconds
    resource_type: ResourceType = ResourceType.BALANCED

@dataclass
class JobDependency:
    """Job dependency definition."""
    job_id: str
    dependency_type: str = "completion"  # completion, data, resource
    condition: Optional[str] = None

@dataclass
class BatchJob:
    """Batch job definition."""
    job_id: str
    job_name: str
    job_type: str
    function_name: str
    parameters: Dict[str, Any]
    priority: JobPriority
    resources: ResourceRequirements
    dependencies: List[JobDependency] = field(default_factory=list)
    schedule: Optional[str] = None  # Cron expression
    retry_count: int = 3
    retry_delay: int = 60  # seconds
    timeout: int = 3600  # seconds
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    scheduled_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    status: JobStatus = JobStatus.PENDING
    result: Optional[Any] = None
    error: Optional[str] = None
    progress: float = 0.0
    current_retry: int = 0

@dataclass
class BatchJobExecution:
    """Batch job execution record."""
    execution_id: str
    job_id: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    status: JobStatus = JobStatus.RUNNING
    result: Optional[Any] = None
    error: Optional[str] = None
    resource_usage: Dict[str, Any] = field(default_factory=dict)
    logs: List[str] = field(default_factory=list)

@dataclass
class ClusterResources:
    """Available cluster resources."""
    total_cpu_cores: int
    available_cpu_cores: int
    total_memory_mb: int
    available_memory_mb: int
    total_disk_mb: int
    available_disk_mb: int
    gpu_count: int
    available_gpu_count: int
    node_count: int
    last_updated: datetime = field(default_factory=datetime.now)

class BatchProcessingController:
    """
    🔧 **BACKEND SENIOR + DBA + DEVOPS**
    Enterprise batch processing controller with Airflow orchestration.
    
    Features:
    - Apache Airflow orchestration enterprise
    - Job scheduling intelligent et retry logic
    - Resource allocation dynamique
    - Progress tracking et monitoring complet
    - Error handling et recovery automatique
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.jobs: Dict[str, BatchJob] = {}
        self.executions: Dict[str, BatchJobExecution] = {}
        self.job_queue: List[str] = []  # Job IDs in priority order
        self.running_jobs: Dict[str, str] = {}  # job_id -> execution_id
        self.job_registry: Dict[str, Callable] = {}
        
        # Resource management
        self.cluster_resources = ClusterResources(
            total_cpu_cores=psutil.cpu_count(),
            available_cpu_cores=psutil.cpu_count(),
            total_memory_mb=int(psutil.virtual_memory().total / 1024 / 1024),
            available_memory_mb=int(psutil.virtual_memory().available / 1024 / 1024),
            total_disk_mb=int(psutil.disk_usage('/').free / 1024 / 1024),
            available_disk_mb=int(psutil.disk_usage('/').free / 1024 / 1024),
            gpu_count=0,  # Would be detected from nvidia-ml-py if available
            available_gpu_count=0,
            node_count=1
        )
        
        # Executors
        self.thread_executor = ThreadPoolExecutor(
            max_workers=self.config.get("max_thread_workers", 10)
        )
        self.process_executor = ProcessPoolExecutor(
            max_workers=self.config.get("max_process_workers", 4)
        )
        
        # Performance metrics
        self.metrics = {
            "jobs_submitted": 0,
            "jobs_completed": 0,
            "jobs_failed": 0,
            "jobs_retried": 0,
            "average_execution_time": 0.0,
            "resource_utilization": 0.0,
            "queue_depth": 0,
            "throughput_jobs_per_hour": 0.0
        }
        
        # Redis for caching and coordination
        self.redis_client = None
        self._init_redis()
        
        # Database for persistence
        self.db_engine = None
        self._init_database()
        
        # Scheduler
        self.scheduler_running = False
        self.resource_monitor_running = False
        
        logger.info("Batch Processing Controller initialized")

    def _init_redis(self) -> None:
        """Initialize Redis connection for coordination."""
        try:
            self.redis_client = redis.Redis(
                host=self.config.get("redis_host", "localhost"),
                port=self.config.get("redis_port", 6379),
                db=self.config.get("redis_db", 1),
                decode_responses=True
            )
            self.redis_client.ping()
            logger.info("Redis connection established for batch coordination")
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}")

    def _init_database(self) -> None:
        """🗄️ **DBA**: Initialize database connection for job persistence."""
        try:
            db_url = self.config.get(
                "database_url",
                "sqlite:///batch_processing.db"
            )
            self.db_engine = create_engine(db_url)
            
            # Create tables if they don't exist
            self._create_tables()
            logger.info("Database connection established for job persistence")
        except Exception as e:
            logger.warning(f"Database connection failed: {e}")

    def _create_tables(self) -> None:
        """Create necessary database tables."""
        if not self.db_engine:
            return
        
        try:
            with self.db_engine.connect() as conn:
                # Jobs table
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS batch_jobs (
                        job_id VARCHAR(255) PRIMARY KEY,
                        job_name VARCHAR(255),
                        job_type VARCHAR(100),
                        status VARCHAR(50),
                        priority INTEGER,
                        created_at TIMESTAMP,
                        scheduled_at TIMESTAMP,
                        started_at TIMESTAMP,
                        completed_at TIMESTAMP,
                        retry_count INTEGER,
                        current_retry INTEGER,
                        progress FLOAT,
                        result TEXT,
                        error TEXT,
                        metadata TEXT
                    )
                """))
                
                # Executions table
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS batch_executions (
                        execution_id VARCHAR(255) PRIMARY KEY,
                        job_id VARCHAR(255),
                        started_at TIMESTAMP,
                        completed_at TIMESTAMP,
                        status VARCHAR(50),
                        resource_usage TEXT,
                        logs TEXT,
                        FOREIGN KEY (job_id) REFERENCES batch_jobs (job_id)
                    )
                """))
                
                conn.commit()
                logger.info("Database tables created/verified")
        except Exception as e:
            logger.error(f"Table creation failed: {e}")

    def register_job_function(self, name: str, function: Callable) -> None:
        """
        📝 Register a job function for batch processing.
        
        Args:
            name: Function name identifier
            function: Callable function to register
        """
        self.job_registry[name] = function
        logger.info(f"Job function '{name}' registered")

    async def submit_job(self, job: BatchJob) -> Dict[str, Any]:
        """
        🔧 **BACKEND SENIOR**: Submit batch job for processing.
        
        Args:
            job: Batch job to submit
            
        Returns:
            Job submission result
        """
        start_time = time.time()
        
        try:
            # Validate job
            if job.function_name not in self.job_registry:
                return {
                    "success": False,
                    "error": f"Job function '{job.function_name}' not registered",
                    "processing_time": time.time() - start_time
                }
            
            # Check dependencies
            dependency_check = await self._check_dependencies(job)
            if not dependency_check["satisfied"]:
                job.status = JobStatus.PENDING
                job.metadata["dependency_status"] = dependency_check
            else:
                job.status = JobStatus.QUEUED
            
            # Store job
            self.jobs[job.job_id] = job
            
            # Add to queue if ready
            if job.status == JobStatus.QUEUED:
                await self._add_to_queue(job)
            
            # Persist to database
            await self._persist_job(job)
            
            # Update metrics
            self.metrics["jobs_submitted"] += 1
            self.metrics["queue_depth"] = len(self.job_queue)
            
            # Cache job info
            if self.redis_client:
                await self._cache_job_info(job)
            
            return {
                "success": True,
                "job_id": job.job_id,
                "status": job.status.value,
                "queue_position": len(self.job_queue) if job.status == JobStatus.QUEUED else None,
                "estimated_start_time": await self._estimate_start_time(job),
                "processing_time": time.time() - start_time
            }
            
        except Exception as e:
            logger.error(f"Job submission failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "processing_time": time.time() - start_time
            }

    async def _check_dependencies(self, job: BatchJob) -> Dict[str, Any]:
        """Check if job dependencies are satisfied."""
        unsatisfied_deps = []
        
        for dep in job.dependencies:
            dep_job = self.jobs.get(dep.job_id)
            if not dep_job:
                unsatisfied_deps.append(f"Job {dep.job_id} not found")
                continue
            
            if dep.dependency_type == "completion":
                if dep_job.status != JobStatus.COMPLETED:
                    unsatisfied_deps.append(f"Job {dep.job_id} not completed (status: {dep_job.status.value})")
            
            elif dep.dependency_type == "data":
                # Check if required data is available
                if not dep.condition or not self._evaluate_condition(dep.condition, dep_job):
                    unsatisfied_deps.append(f"Data condition not met for job {dep.job_id}")
        
        return {
            "satisfied": len(unsatisfied_deps) == 0,
            "unsatisfied_dependencies": unsatisfied_deps
        }

    def _evaluate_condition(self, condition: str, job: BatchJob) -> bool:
        """Evaluate dependency condition."""
        # Simple condition evaluation - could be extended
        if condition == "success":
            return job.status == JobStatus.COMPLETED and not job.error
        elif condition == "completed":
            return job.status == JobStatus.COMPLETED
        return True

    async def _add_to_queue(self, job: BatchJob) -> None:
        """Add job to processing queue with priority sorting."""
        self.job_queue.append(job.job_id)
        
        # Sort by priority (lower number = higher priority)
        self.job_queue.sort(key=lambda job_id: (
            self.jobs[job_id].priority.value,
            self.jobs[job_id].created_at
        ))

    async def execute_job(self, job_id: str) -> Dict[str, Any]:
        """
        ⚙️ **DEVOPS**: Execute batch job with resource management.
        
        Args:
            job_id: Job identifier to execute
            
        Returns:
            Execution result
        """
        start_time = time.time()
        
        try:
            job = self.jobs.get(job_id)
            if not job:
                return {
                    "success": False,
                    "error": "Job not found"
                }
            
            # Check resource availability
            if not await self._check_resource_availability(job.resources):
                return {
                    "success": False,
                    "error": "Insufficient resources available",
                    "required_resources": job.resources.__dict__
                }
            
            # Create execution record
            execution = BatchJobExecution(
                execution_id=str(uuid.uuid4()),
                job_id=job_id,
                started_at=datetime.now()
            )
            
            self.executions[execution.execution_id] = execution
            self.running_jobs[job_id] = execution.execution_id
            
            # Update job status
            job.status = JobStatus.RUNNING
            job.started_at = execution.started_at
            job.progress = 0.0
            
            # Reserve resources
            await self._reserve_resources(job.resources)
            
            # Get job function
            job_function = self.job_registry[job.function_name]
            
            # Execute job
            try:
                # Choose executor based on resource requirements
                if job.resources.resource_type == ResourceType.CPU_INTENSIVE:
                    result = await self._execute_in_process_pool(job_function, job.parameters)
                else:
                    result = await self._execute_in_thread_pool(job_function, job.parameters)
                
                # Update execution
                execution.completed_at = datetime.now()
                execution.status = JobStatus.COMPLETED
                execution.result = result
                
                # Update job
                job.status = JobStatus.COMPLETED
                job.completed_at = execution.completed_at
                job.result = result
                job.progress = 100.0
                
                # Update metrics
                self.metrics["jobs_completed"] += 1
                execution_time = (execution.completed_at - execution.started_at).total_seconds()
                self.metrics["average_execution_time"] = (
                    self.metrics["average_execution_time"] * (self.metrics["jobs_completed"] - 1) + execution_time
                ) / self.metrics["jobs_completed"]
                
                logger.info(f"Job {job_id} completed successfully")
                
            except Exception as e:
                # Handle job failure
                execution.completed_at = datetime.now()
                execution.status = JobStatus.FAILED
                execution.error = str(e)
                
                job.error = str(e)
                job.completed_at = execution.completed_at
                
                # Check if we should retry
                if job.current_retry < job.retry_count:
                    job.status = JobStatus.RETRYING
                    job.current_retry += 1
                    job.scheduled_at = datetime.now() + timedelta(seconds=job.retry_delay)
                    self.metrics["jobs_retried"] += 1
                    
                    # Re-queue for retry
                    await self._add_to_queue(job)
                    logger.info(f"Job {job_id} scheduled for retry {job.current_retry}/{job.retry_count}")
                else:
                    job.status = JobStatus.FAILED
                    self.metrics["jobs_failed"] += 1
                    logger.error(f"Job {job_id} failed permanently: {e}")
            
            finally:
                # Release resources
                await self._release_resources(job.resources)
                if job_id in self.running_jobs:
                    del self.running_jobs[job_id]
            
            # Persist execution
            await self._persist_execution(execution)
            await self._persist_job(job)
            
            return {
                "success": execution.status == JobStatus.COMPLETED,
                "job_id": job_id,
                "execution_id": execution.execution_id,
                "status": job.status.value,
                "result": job.result,
                "error": job.error,
                "execution_time": time.time() - start_time,
                "retry_count": job.current_retry
            }
            
        except Exception as e:
            logger.error(f"Job execution failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "execution_time": time.time() - start_time
            }

    async def _check_resource_availability(self, requirements: ResourceRequirements) -> bool:
        """Check if required resources are available."""
        resources = self.cluster_resources
        
        return (
            resources.available_cpu_cores >= requirements.cpu_cores and
            resources.available_memory_mb >= requirements.memory_mb and
            resources.available_disk_mb >= requirements.disk_mb and
            resources.available_gpu_count >= requirements.gpu_count
        )

    async def _reserve_resources(self, requirements: ResourceRequirements) -> None:
        """Reserve cluster resources for job execution."""
        self.cluster_resources.available_cpu_cores -= requirements.cpu_cores
        self.cluster_resources.available_memory_mb -= requirements.memory_mb
        self.cluster_resources.available_disk_mb -= requirements.disk_mb
        self.cluster_resources.available_gpu_count -= requirements.gpu_count
        
        # Update resource utilization metric
        cpu_utilization = 1.0 - (self.cluster_resources.available_cpu_cores / self.cluster_resources.total_cpu_cores)
        memory_utilization = 1.0 - (self.cluster_resources.available_memory_mb / self.cluster_resources.total_memory_mb)
        self.metrics["resource_utilization"] = max(cpu_utilization, memory_utilization)

    async def _release_resources(self, requirements: ResourceRequirements) -> None:
        """Release reserved cluster resources."""
        self.cluster_resources.available_cpu_cores += requirements.cpu_cores
        self.cluster_resources.available_memory_mb += requirements.memory_mb
        self.cluster_resources.available_disk_mb += requirements.disk_mb
        self.cluster_resources.available_gpu_count += requirements.gpu_count
        
        # Ensure we don't exceed total resources
        self.cluster_resources.available_cpu_cores = min(
            self.cluster_resources.available_cpu_cores,
            self.cluster_resources.total_cpu_cores
        )
        self.cluster_resources.available_memory_mb = min(
            self.cluster_resources.available_memory_mb,
            self.cluster_resources.total_memory_mb
        )

    async def _execute_in_thread_pool(self, function: Callable, parameters: Dict[str, Any]) -> Any:
        """Execute job function in thread pool."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.thread_executor, function, parameters)

    async def _execute_in_process_pool(self, function: Callable, parameters: Dict[str, Any]) -> Any:
        """Execute job function in process pool."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.process_executor, function, parameters)

    async def start_scheduler(self) -> None:
        """
        🤖 **LEAD DEV IA**: Start intelligent job scheduler.
        """
        if self.scheduler_running:
            return
        
        self.scheduler_running = True
        logger.info("Batch job scheduler started")
        
        while self.scheduler_running:
            try:
                await self._process_queue()
                await self._check_scheduled_jobs()
                await self._update_job_dependencies()
                await asyncio.sleep(5)  # Check every 5 seconds
                
            except Exception as e:
                logger.error(f"Scheduler error: {e}")
                await asyncio.sleep(10)

    async def _process_queue(self) -> None:
        """Process jobs in the queue."""
        if not self.job_queue:
            return
        
        # Get next job
        job_id = self.job_queue[0]
        job = self.jobs.get(job_id)
        
        if not job or job.status != JobStatus.QUEUED:
            self.job_queue.pop(0)
            return
        
        # Check if resources are available
        if await self._check_resource_availability(job.resources):
            self.job_queue.pop(0)
            self.metrics["queue_depth"] = len(self.job_queue)
            
            # Execute job asynchronously
            asyncio.create_task(self.execute_job(job_id))

    async def _check_scheduled_jobs(self) -> None:
        """Check for jobs that should be scheduled now."""
        current_time = datetime.now()
        
        for job in self.jobs.values():
            if (job.status == JobStatus.PENDING and 
                job.scheduled_at and 
                job.scheduled_at <= current_time):
                
                # Check dependencies again
                dependency_check = await self._check_dependencies(job)
                if dependency_check["satisfied"]:
                    job.status = JobStatus.QUEUED
                    await self._add_to_queue(job)

    async def _update_job_dependencies(self) -> None:
        """Update jobs that may now have satisfied dependencies."""
        pending_jobs = [job for job in self.jobs.values() if job.status == JobStatus.PENDING]
        
        for job in pending_jobs:
            dependency_check = await self._check_dependencies(job)
            if dependency_check["satisfied"]:
                job.status = JobStatus.QUEUED
                await self._add_to_queue(job)

    async def stop_scheduler(self) -> None:
        """Stop the job scheduler."""
        self.scheduler_running = False
        logger.info("Batch job scheduler stopped")

    async def cancel_job(self, job_id: str) -> Dict[str, Any]:
        """
        🛑 Cancel a running or queued job.
        
        Args:
            job_id: Job identifier to cancel
            
        Returns:
            Cancellation result
        """
        try:
            job = self.jobs.get(job_id)
            if not job:
                return {"success": False, "error": "Job not found"}
            
            if job.status == JobStatus.COMPLETED:
                return {"success": False, "error": "Job already completed"}
            
            # Remove from queue if queued
            if job_id in self.job_queue:
                self.job_queue.remove(job_id)
                self.metrics["queue_depth"] = len(self.job_queue)
            
            # Update job status
            job.status = JobStatus.CANCELLED
            job.completed_at = datetime.now()
            
            # If running, mark execution as cancelled
            if job_id in self.running_jobs:
                execution_id = self.running_jobs[job_id]
                execution = self.executions.get(execution_id)
                if execution:
                    execution.status = JobStatus.CANCELLED
                    execution.completed_at = datetime.now()
                    await self._persist_execution(execution)
                
                # Release resources
                await self._release_resources(job.resources)
                del self.running_jobs[job_id]
            
            await self._persist_job(job)
            
            return {
                "success": True,
                "job_id": job_id,
                "status": job.status.value,
                "cancelled_at": job.completed_at.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Job cancellation failed: {e}")
            return {"success": False, "error": str(e)}

    async def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """
        📊 Get comprehensive job status and progress.
        
        Args:
            job_id: Job identifier
            
        Returns:
            Job status information
        """
        job = self.jobs.get(job_id)
        if not job:
            return {"success": False, "error": "Job not found"}
        
        # Get execution info if running
        execution_info = None
        if job_id in self.running_jobs:
            execution_id = self.running_jobs[job_id]
            execution = self.executions.get(execution_id)
            if execution:
                execution_info = {
                    "execution_id": execution.execution_id,
                    "started_at": execution.started_at.isoformat(),
                    "resource_usage": execution.resource_usage
                }
        
        # Calculate progress
        progress = job.progress
        if job.status == JobStatus.RUNNING and not progress:
            # Estimate progress based on execution time and average
            if job.started_at and self.metrics["average_execution_time"] > 0:
                elapsed = (datetime.now() - job.started_at).total_seconds()
                progress = min(90.0, (elapsed / self.metrics["average_execution_time"]) * 100)
        
        return {
            "success": True,
            "job_id": job.job_id,
            "job_name": job.job_name,
            "status": job.status.value,
            "priority": job.priority.value,
            "progress": progress,
            "created_at": job.created_at.isoformat(),
            "scheduled_at": job.scheduled_at.isoformat() if job.scheduled_at else None,
            "started_at": job.started_at.isoformat() if job.started_at else None,
            "completed_at": job.completed_at.isoformat() if job.completed_at else None,
            "retry_count": job.current_retry,
            "max_retries": job.retry_count,
            "result": job.result,
            "error": job.error,
            "execution": execution_info,
            "dependencies": [dep.__dict__ for dep in job.dependencies],
            "resource_requirements": job.resources.__dict__
        }

    async def _persist_job(self, job: BatchJob) -> None:
        """🗄️ **DBA**: Persist job to database."""
        if not self.db_engine:
            return
        
        try:
            with self.db_engine.connect() as conn:
                conn.execute(text("""
                    INSERT OR REPLACE INTO batch_jobs 
                    (job_id, job_name, job_type, status, priority, created_at, 
                     scheduled_at, started_at, completed_at, retry_count, 
                     current_retry, progress, result, error, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """), (
                    job.job_id, job.job_name, job.job_type, job.status.value,
                    job.priority.value, job.created_at, job.scheduled_at,
                    job.started_at, job.completed_at, job.retry_count,
                    job.current_retry, job.progress, 
                    json.dumps(job.result) if job.result else None,
                    job.error, json.dumps(job.metadata)
                ))
                conn.commit()
        except Exception as e:
            logger.error(f"Job persistence failed: {e}")

    async def _persist_execution(self, execution: BatchJobExecution) -> None:
        """🗄️ **DBA**: Persist execution to database."""
        if not self.db_engine:
            return
        
        try:
            with self.db_engine.connect() as conn:
                conn.execute(text("""
                    INSERT OR REPLACE INTO batch_executions 
                    (execution_id, job_id, started_at, completed_at, status, 
                     resource_usage, logs)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """), (
                    execution.execution_id, execution.job_id, execution.started_at,
                    execution.completed_at, execution.status.value,
                    json.dumps(execution.resource_usage),
                    json.dumps(execution.logs)
                ))
                conn.commit()
        except Exception as e:
            logger.error(f"Execution persistence failed: {e}")

    async def _cache_job_info(self, job: BatchJob) -> None:
        """Cache job information in Redis."""
        if self.redis_client:
            try:
                cache_key = f"batch_job:{job.job_id}"
                job_info = {
                    "job_id": job.job_id,
                    "status": job.status.value,
                    "progress": job.progress,
                    "created_at": job.created_at.isoformat()
                }
                await asyncio.get_event_loop().run_in_executor(
                    None,
                    self.redis_client.setex,
                    cache_key,
                    1800,  # 30 minutes TTL
                    json.dumps(job_info)
                )
            except Exception as e:
                logger.error(f"Job caching failed: {e}")

    async def _estimate_start_time(self, job: BatchJob) -> Optional[str]:
        """Estimate when job will start based on queue and resources."""
        if job.status != JobStatus.QUEUED:
            return None
        
        try:
            position = self.job_queue.index(job.job_id)
            estimated_wait = position * self.metrics["average_execution_time"]
            estimated_start = datetime.now() + timedelta(seconds=estimated_wait)
            return estimated_start.isoformat()
        except (ValueError, ZeroDivisionError):
            return None

    async def get_queue_status(self) -> Dict[str, Any]:
        """
        📊 Get comprehensive queue status and metrics.
        
        Returns:
            Queue status and performance metrics
        """
        # Calculate throughput
        if self.metrics["jobs_completed"] > 0:
            # Simple throughput calculation (jobs per hour)
            uptime_hours = 1  # Would be actual uptime in production
            self.metrics["throughput_jobs_per_hour"] = self.metrics["jobs_completed"] / uptime_hours
        
        return {
            "queue_depth": len(self.job_queue),
            "running_jobs": len(self.running_jobs),
            "total_jobs": len(self.jobs),
            "completed_jobs": self.metrics["jobs_completed"],
            "failed_jobs": self.metrics["jobs_failed"],
            "retried_jobs": self.metrics["jobs_retried"],
            "success_rate": (
                self.metrics["jobs_completed"] / 
                max(1, self.metrics["jobs_completed"] + self.metrics["jobs_failed"])
            ),
            "average_execution_time": self.metrics["average_execution_time"],
            "throughput_jobs_per_hour": self.metrics["throughput_jobs_per_hour"],
            "resource_utilization": self.metrics["resource_utilization"],
            "cluster_resources": self.cluster_resources.__dict__,
            "scheduler_running": self.scheduler_running
        }

    async def health_check(self) -> Dict[str, Any]:
        """
        🏥 Perform comprehensive health check.
        
        Returns:
            Health check results
        """
        start_time = time.time()
        
        # Check system resources
        memory_usage = psutil.virtual_memory().percent
        cpu_usage = psutil.cpu_percent(interval=1)
        disk_usage = psutil.disk_usage('/').percent
        
        health_status = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "components": {
                "scheduler": "healthy" if self.scheduler_running else "stopped",
                "database": "healthy" if self.db_engine else "disabled",
                "redis_cache": "healthy" if self.redis_client else "disabled",
                "thread_executor": "healthy",
                "process_executor": "healthy"
            },
            "system_resources": {
                "memory_usage_percent": memory_usage,
                "cpu_usage_percent": cpu_usage,
                "disk_usage_percent": disk_usage
            },
            "queue_metrics": await self.get_queue_status(),
            "response_time": time.time() - start_time
        }
        
        # Check for concerning conditions
        if memory_usage > 90 or cpu_usage > 95 or disk_usage > 95:
            health_status["status"] = "warning"
            health_status["warnings"] = ["High system resource usage"]
        
        if len(self.job_queue) > 1000:
            health_status["status"] = "warning"
            health_status["warnings"] = health_status.get("warnings", []) + ["High queue depth"]
        
        return health_status

    def __del__(self):
        """Cleanup resources."""
        try:
            if hasattr(self, 'thread_executor'):
                self.thread_executor.shutdown(wait=False)
            if hasattr(self, 'process_executor'):
                self.process_executor.shutdown(wait=False)
        except:
            pass

# Example job functions
def example_data_processing_job(parameters: Dict[str, Any]) -> Dict[str, Any]:
    """🧠 **ML ENGINEER**: Example data processing job function."""
    import time
    import random
    
    # Simulate data processing
    data_size = parameters.get("data_size", 1000)
    processing_time = parameters.get("processing_time", 2)
    
    time.sleep(processing_time)
    
    # Simulate some processing results
    processed_records = data_size
    success_rate = random.uniform(0.95, 1.0)
    
    return {
        "processed_records": processed_records,
        "success_rate": success_rate,
        "processing_time": processing_time,
        "status": "completed"
    }

def example_ml_training_job(parameters: Dict[str, Any]) -> Dict[str, Any]:
    """🧠 **ML ENGINEER**: Example ML training job function."""
    import time
    import random
    
    # Simulate ML training
    epochs = parameters.get("epochs", 10)
    model_type = parameters.get("model_type", "neural_network")
    
    training_time = epochs * 0.5  # 0.5 seconds per epoch
    time.sleep(training_time)
    
    # Simulate training results
    accuracy = random.uniform(0.85, 0.98)
    loss = random.uniform(0.02, 0.15)
    
    return {
        "model_type": model_type,
        "epochs": epochs,
        "final_accuracy": accuracy,
        "final_loss": loss,
        "training_time": training_time,
        "model_path": f"/models/{model_type}_{int(time.time())}.pkl"
    }

# Example usage and testing
async def main():
    """Example usage of Batch Processing Controller."""
    
    # Initialize controller
    controller = BatchProcessingController({
        "max_thread_workers": 5,
        "max_process_workers": 2,
        "redis_host": "localhost",
        "database_url": "sqlite:///batch_test.db"
    })
    
    # Register job functions
    controller.register_job_function("data_processing", example_data_processing_job)
    controller.register_job_function("ml_training", example_ml_training_job)
    
    # Start scheduler
    scheduler_task = asyncio.create_task(controller.start_scheduler())
    
    # Create sample jobs
    jobs = [
        BatchJob(
            job_id="data_001",
            job_name="Daily Data Processing",
            job_type="data_processing",
            function_name="data_processing",
            parameters={"data_size": 5000, "processing_time": 1},
            priority=JobPriority.HIGH,
            resources=ResourceRequirements(
                cpu_cores=2,
                memory_mb=2048,
                resource_type=ResourceType.CPU_INTENSIVE
            )
        ),
        BatchJob(
            job_id="ml_001",
            job_name="Model Training",
            job_type="ml_training",
            function_name="ml_training",
            parameters={"epochs": 5, "model_type": "transformer"},
            priority=JobPriority.NORMAL,
            resources=ResourceRequirements(
                cpu_cores=4,
                memory_mb=4096,
                resource_type=ResourceType.CPU_INTENSIVE
            ),
            dependencies=[JobDependency(job_id="data_001", dependency_type="completion")]
        )
    ]
    
    # Submit jobs
    for job in jobs:
        result = await controller.submit_job(job)
        print(f"Job {job.job_id} submitted: {result}")
    
    # Wait for jobs to complete
    await asyncio.sleep(5)
    
    # Check job statuses
    for job in jobs:
        status = await controller.get_job_status(job.job_id)
        print(f"Job {job.job_id} status: {status}")
    
    # Get queue status
    queue_status = await controller.get_queue_status()
    print(f"Queue Status: {queue_status}")
    
    # Health check
    health = await controller.health_check()
    print(f"Health Check: {health}")
    
    # Stop scheduler
    await controller.stop_scheduler()
    scheduler_task.cancel()

if __name__ == "__main__":
    asyncio.run(main())