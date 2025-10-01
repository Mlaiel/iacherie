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

Cron Job Template for IA Chéries Microservices Platform
==================================================

Enterprise-grade scheduled task service template providing:
- Cron-based job scheduling with persistence
- Job history and execution tracking
- Failure retry mechanisms with exponential backoff
- Job dependency management
- Resource allocation and limits
- Distributed job coordination
- Health monitoring and alerting
- Job performance metrics
- Configuration hot-reloading
- Graceful shutdown handling

Author: Fahed Mlaiel (mlaiel@live.de)
DevOps Engineer & Scheduling Systems Specialist
"""

import logging
import asyncio
import json
from typing import Dict, Any, Optional, List, Callable, Type, Union
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
import croniter
import hashlib
import uuid

from pydantic import BaseModel, Field, validator
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import Column, String, DateTime, Integer, Text, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
import redis.asyncio as redis
from prometheus_client import Counter, Histogram, Gauge
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.redis import RedisJobStore
from apscheduler.executors.asyncio import AsyncIOExecutor

from ..base_microservice import BaseMicroservice
from ..microservice_template import ServiceConfig, ServiceStatus
from ..communication_manager import CommunicationManager, CommunicationConfig

logger = logging.getLogger(__name__)

Base = declarative_base()


class JobStatus(str, Enum):
    """Job execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"


class JobPriority(str, Enum):
    """Job priority levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class RetryPolicy(BaseModel):
    """Job retry policy configuration"""
    max_retries: int = Field(default=3, ge=0, description="Maximum retry attempts")
    initial_delay: int = Field(default=60, ge=1, description="Initial retry delay in seconds")
    max_delay: int = Field(default=3600, ge=1, description="Maximum retry delay in seconds")
    exponential_base: float = Field(default=2.0, ge=1.0, description="Exponential backoff base")
    jitter: bool = Field(default=True, description="Add random jitter to delays")


class ResourceLimits(BaseModel):
    """Job resource limits"""
    max_memory_mb: Optional[int] = Field(default=None, description="Maximum memory in MB")
    max_cpu_percent: Optional[int] = Field(default=None, description="Maximum CPU percentage")
    max_execution_time: Optional[int] = Field(default=None, description="Maximum execution time in seconds")
    max_disk_io_mb: Optional[int] = Field(default=None, description="Maximum disk I/O in MB")


class JobDefinition(BaseModel):
    """Cron job definition"""
    id: str = Field(..., description="Unique job identifier")
    name: str = Field(..., description="Human-readable job name")
    description: Optional[str] = Field(default=None, description="Job description")
    cron_expression: str = Field(..., description="Cron expression for scheduling")
    function_name: str = Field(..., description="Function to execute")
    function_args: List[Any] = Field(default_factory=list, description="Function arguments")
    function_kwargs: Dict[str, Any] = Field(default_factory=dict, description="Function keyword arguments")
    priority: JobPriority = Field(default=JobPriority.NORMAL, description="Job priority")
    enabled: bool = Field(default=True, description="Whether job is enabled")
    retry_policy: RetryPolicy = Field(default_factory=RetryPolicy, description="Retry policy")
    resource_limits: ResourceLimits = Field(default_factory=ResourceLimits, description="Resource limits")
    dependencies: List[str] = Field(default_factory=list, description="Job dependencies")
    tags: List[str] = Field(default_factory=list, description="Job tags")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    timezone: str = Field(default="UTC", description="Timezone for cron expression")
    
    @validator('cron_expression')
    def validate_cron_expression(cls, v):
        """Validate cron expression"""
        try:
            croniter.croniter(v)
        except ValueError as e:
            raise ValueError(f"Invalid cron expression: {e}")
        return v


class JobExecution(Base):
    """Job execution record"""
    __tablename__ = "job_executions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    job_id = Column(String, nullable=False, index=True)
    execution_id = Column(String, nullable=False)
    status = Column(String, nullable=False, default=JobStatus.PENDING)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    duration_seconds = Column(Integer, nullable=True)
    result = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)
    resource_usage = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


@dataclass
class JobContext:
    """Job execution context"""
    job_id: str
    execution_id: str
    started_at: datetime
    retry_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


class CronJobConfig(ServiceConfig):
    """Cron job service configuration"""
    # Scheduler settings
    scheduler_timezone: str = Field(default="UTC", description="Scheduler timezone")
    max_workers: int = Field(default=10, description="Maximum worker threads")
    job_defaults: Dict[str, Any] = Field(default_factory=dict, description="Default job settings")
    
    # Redis settings for job store
    redis_host: str = Field(default="localhost", description="Redis host")
    redis_port: int = Field(default=6379, description="Redis port")
    redis_db: int = Field(default=1, description="Redis database")
    redis_password: Optional[str] = Field(default=None, description="Redis password")
    
    # Job management
    enable_job_persistence: bool = Field(default=True, description="Enable job persistence")
    job_history_retention_days: int = Field(default=30, description="Job history retention in days")
    enable_distributed_locking: bool = Field(default=True, description="Enable distributed job locking")
    
    # Monitoring
    enable_metrics: bool = Field(default=True, description="Enable job metrics")
    enable_health_checks: bool = Field(default=True, description="Enable health checks")
    health_check_interval: int = Field(default=60, description="Health check interval in seconds")
    
    # Performance
    job_execution_timeout: int = Field(default=3600, description="Default job execution timeout")
    enable_resource_monitoring: bool = Field(default=True, description="Enable resource monitoring")


class CronJobTemplate(BaseMicroservice):
    """
    Enterprise Cron Job Template
    
    Provides comprehensive scheduled task management with:
    - Persistent job scheduling
    - Distributed coordination
    - Resource monitoring
    - Failure handling
    """
    
    def __init__(self, config: CronJobConfig):
        super().__init__(config)
        self.config = config
        self.scheduler: Optional[AsyncIOScheduler] = None
        self.redis_client: Optional[redis.Redis] = None
        self.registered_functions: Dict[str, Callable] = {}
        self.active_executions: Dict[str, JobContext] = {}
        
        # Metrics
        self.job_executions_total = Counter(
            'cron_job_executions_total',
            'Total job executions',
            ['job_id', 'status']
        )
        self.job_duration_seconds = Histogram(
            'cron_job_duration_seconds',
            'Job execution duration',
            ['job_id']
        )
        self.active_jobs_gauge = Gauge(
            'cron_active_jobs',
            'Number of active jobs'
        )
        
    async def initialize(self) -> None:
        """Initialize cron job service"""
        try:
            logger.info("Initializing cron job service")
            
            # Initialize Redis client
            await self._initialize_redis()
            
            # Initialize scheduler
            await self._initialize_scheduler()
            
            # Load persisted jobs
            if self.config.enable_job_persistence:
                await self._load_persisted_jobs()
            
            # Start health monitoring
            if self.config.enable_health_checks:
                await self._start_health_monitoring()
                
            logger.info("Cron job service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize cron job service: {e}")
            raise
    
    async def _initialize_redis(self) -> None:
        """Initialize Redis connection"""
        self.redis_client = redis.Redis(
            host=self.config.redis_host,
            port=self.config.redis_port,
            db=self.config.redis_db,
            password=self.config.redis_password,
            decode_responses=True
        )
        
        # Test connection
        await self.redis_client.ping()
        logger.info("Redis connection established")
    
    async def _initialize_scheduler(self) -> None:
        """Initialize APScheduler"""
        jobstores = {
            'default': RedisJobStore(
                host=self.config.redis_host,
                port=self.config.redis_port,
                db=self.config.redis_db,
                password=self.config.redis_password
            )
        }
        
        executors = {
            'default': AsyncIOExecutor(max_workers=self.config.max_workers)
        }
        
        job_defaults = {
            'coalesce': False,
            'max_instances': 1,
            'misfire_grace_time': 60,
            **self.config.job_defaults
        }
        
        self.scheduler = AsyncIOScheduler(
            jobstores=jobstores,
            executors=executors,
            job_defaults=job_defaults,
            timezone=self.config.scheduler_timezone
        )
        
        self.scheduler.start()
        logger.info("Scheduler started")
    
    async def register_function(self, name: str, func: Callable) -> None:
        """Register a function for job execution"""
        if not asyncio.iscoroutinefunction(func):
            # Wrap sync function in async
            async def async_wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            self.registered_functions[name] = async_wrapper
        else:
            self.registered_functions[name] = func
        
        logger.info(f"Registered function: {name}")
    
    async def create_job(self, job_def: JobDefinition) -> Dict[str, Any]:
        """Create a new cron job"""
        try:
            # Validate function exists
            if job_def.function_name not in self.registered_functions:
                raise ValueError(f"Function not registered: {job_def.function_name}")
            
            # Check dependencies
            await self._validate_dependencies(job_def.dependencies)
            
            # Create job wrapper
            job_func = self._create_job_wrapper(job_def)
            
            # Add job to scheduler
            job = self.scheduler.add_job(
                job_func,
                trigger='cron',
                **self._parse_cron_expression(job_def.cron_expression),
                id=job_def.id,
                name=job_def.name,
                timezone=job_def.timezone,
                replace_existing=True
            )
            
            # Persist job definition
            if self.config.enable_job_persistence:
                await self._persist_job_definition(job_def)
            
            logger.info(f"Created job: {job_def.id}")
            
            return {
                "job_id": job_def.id,
                "name": job_def.name,
                "status": "created",
                "next_run": job.next_run_time.isoformat() if job.next_run_time else None
            }
            
        except Exception as e:
            logger.error(f"Failed to create job {job_def.id}: {e}")
            raise
    
    def _create_job_wrapper(self, job_def: JobDefinition) -> Callable:
        """Create a wrapper function for job execution"""
        async def job_wrapper():
            execution_id = str(uuid.uuid4())
            context = JobContext(
                job_id=job_def.id,
                execution_id=execution_id,
                started_at=datetime.utcnow()
            )
            
            # Track active execution
            self.active_executions[execution_id] = context
            
            try:
                # Update metrics
                self.active_jobs_gauge.inc()
                
                # Check dependencies
                if job_def.dependencies:
                    await self._check_dependencies(job_def.dependencies)
                
                # Execute with timeout
                start_time = datetime.utcnow()
                
                # Get function
                func = self.registered_functions[job_def.function_name]
                
                # Execute with resource monitoring
                if self.config.enable_resource_monitoring:
                    result = await self._execute_with_monitoring(
                        func, job_def, context
                    )
                else:
                    result = await func(*job_def.function_args, **job_def.function_kwargs)
                
                # Calculate duration
                duration = (datetime.utcnow() - start_time).total_seconds()
                
                # Record successful execution
                await self._record_execution(
                    job_def.id, execution_id, JobStatus.COMPLETED,
                    start_time, duration, result
                )
                
                # Update metrics
                self.job_executions_total.labels(
                    job_id=job_def.id, status='completed'
                ).inc()
                self.job_duration_seconds.labels(job_id=job_def.id).observe(duration)
                
                logger.info(f"Job {job_def.id} completed successfully in {duration:.2f}s")
                
            except Exception as e:
                # Handle failure
                await self._handle_job_failure(job_def, context, e)
                
            finally:
                # Cleanup
                self.active_jobs_gauge.dec()
                if execution_id in self.active_executions:
                    del self.active_executions[execution_id]
        
        return job_wrapper
    
    async def _execute_with_monitoring(
        self, func: Callable, job_def: JobDefinition, context: JobContext
    ) -> Any:
        """Execute function with resource monitoring"""
        import psutil
        import asyncio
        
        process = psutil.Process()
        start_memory = process.memory_info().rss / 1024 / 1024  # MB
        start_cpu_time = process.cpu_times()
        
        # Execute with timeout
        timeout = (
            job_def.resource_limits.max_execution_time or 
            self.config.job_execution_timeout
        )
        
        try:
            result = await asyncio.wait_for(
                func(*job_def.function_args, **job_def.function_kwargs),
                timeout=timeout
            )
            
            # Record resource usage
            end_memory = process.memory_info().rss / 1024 / 1024  # MB
            end_cpu_time = process.cpu_times()
            
            resource_usage = {
                "memory_peak_mb": max(start_memory, end_memory),
                "memory_delta_mb": end_memory - start_memory,
                "cpu_time_user": end_cpu_time.user - start_cpu_time.user,
                "cpu_time_system": end_cpu_time.system - start_cpu_time.system
            }
            
            context.metadata["resource_usage"] = resource_usage
            
            return result
            
        except asyncio.TimeoutError:
            raise TimeoutError(f"Job execution exceeded timeout of {timeout}s")
    
    async def _handle_job_failure(
        self, job_def: JobDefinition, context: JobContext, error: Exception
    ) -> None:
        """Handle job execution failure"""
        context.retry_count += 1
        
        # Record failed execution
        duration = (datetime.utcnow() - context.started_at).total_seconds()
        await self._record_execution(
            job_def.id, context.execution_id, JobStatus.FAILED,
            context.started_at, duration, None, str(error)
        )
        
        # Update metrics
        self.job_executions_total.labels(
            job_id=job_def.id, status='failed'
        ).inc()
        
        # Check if we should retry
        if context.retry_count <= job_def.retry_policy.max_retries:
            await self._schedule_retry(job_def, context)
        else:
            logger.error(f"Job {job_def.id} failed permanently after {context.retry_count} attempts: {error}")
    
    async def _schedule_retry(self, job_def: JobDefinition, context: JobContext) -> None:
        """Schedule job retry with exponential backoff"""
        delay = min(
            job_def.retry_policy.initial_delay * (
                job_def.retry_policy.exponential_base ** (context.retry_count - 1)
            ),
            job_def.retry_policy.max_delay
        )
        
        if job_def.retry_policy.jitter:
            import random
            delay *= random.uniform(0.8, 1.2)
        
        # Schedule retry
        retry_time = datetime.utcnow() + timedelta(seconds=delay)
        
        self.scheduler.add_job(
            self._create_job_wrapper(job_def),
            trigger='date',
            run_date=retry_time,
            id=f"{job_def.id}_retry_{context.retry_count}",
            replace_existing=True
        )
        
        logger.info(f"Scheduled retry for job {job_def.id} in {delay:.1f}s (attempt {context.retry_count})")
    
    async def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """Get job status and information"""
        job = self.scheduler.get_job(job_id)
        if not job:
            raise ValueError(f"Job not found: {job_id}")
        
        # Get recent executions
        executions = await self._get_recent_executions(job_id, limit=10)
        
        return {
            "job_id": job_id,
            "name": job.name,
            "next_run": job.next_run_time.isoformat() if job.next_run_time else None,
            "trigger": str(job.trigger),
            "recent_executions": executions,
            "is_active": job_id in [ctx.job_id for ctx in self.active_executions.values()]
        }
    
    async def delete_job(self, job_id: str) -> bool:
        """Delete a job"""
        try:
            self.scheduler.remove_job(job_id)
            
            # Remove from persistence
            if self.config.enable_job_persistence:
                await self.redis_client.delete(f"job_def:{job_id}")
            
            logger.info(f"Deleted job: {job_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete job {job_id}: {e}")
            return False
    
    async def pause_job(self, job_id: str) -> bool:
        """Pause a job"""
        try:
            self.scheduler.pause_job(job_id)
            logger.info(f"Paused job: {job_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to pause job {job_id}: {e}")
            return False
    
    async def resume_job(self, job_id: str) -> bool:
        """Resume a paused job"""
        try:
            self.scheduler.resume_job(job_id)
            logger.info(f"Resumed job: {job_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to resume job {job_id}: {e}")
            return False
    
    async def get_health_status(self) -> Dict[str, Any]:
        """Get service health status"""
        try:
            jobs = self.scheduler.get_jobs()
            active_count = len(self.active_executions)
            
            # Check Redis connection
            redis_healthy = False
            try:
                await self.redis_client.ping()
                redis_healthy = True
            except Exception:
                pass
            
            return {
                "service": "cron_job_template",
                "status": "healthy" if redis_healthy else "degraded",
                "timestamp": datetime.utcnow().isoformat(),
                "metrics": {
                    "total_jobs": len(jobs),
                    "active_executions": active_count,
                    "scheduler_running": self.scheduler.running,
                    "redis_connected": redis_healthy
                }
            }
            
        except Exception as e:
            return {
                "service": "cron_job_template",
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def _parse_cron_expression(self, cron_expr: str) -> Dict[str, str]:
        """Parse cron expression into APScheduler format"""
        parts = cron_expr.split()
        if len(parts) != 5:
            raise ValueError("Cron expression must have 5 parts")
        
        minute, hour, day, month, day_of_week = parts
        
        return {
            'minute': minute,
            'hour': hour,
            'day': day,
            'month': month,
            'day_of_week': day_of_week
        }
    
    async def _persist_job_definition(self, job_def: JobDefinition) -> None:
        """Persist job definition to Redis"""
        key = f"job_def:{job_def.id}"
        value = job_def.json()
        await self.redis_client.set(key, value)
    
    async def _load_persisted_jobs(self) -> None:
        """Load persisted job definitions"""
        keys = await self.redis_client.keys("job_def:*")
        for key in keys:
            try:
                data = await self.redis_client.get(key)
                job_def = JobDefinition.parse_raw(data)
                
                if job_def.enabled and job_def.function_name in self.registered_functions:
                    await self.create_job(job_def)
                    
            except Exception as e:
                logger.error(f"Failed to load job from {key}: {e}")
    
    async def _record_execution(
        self, job_id: str, execution_id: str, status: JobStatus,
        started_at: datetime, duration: float, result: Any = None,
        error_message: str = None
    ) -> None:
        """Record job execution in database"""
        # Implementation would depend on database setup
        # For now, store in Redis with TTL
        execution_data = {
            "job_id": job_id,
            "execution_id": execution_id,
            "status": status.value,
            "started_at": started_at.isoformat(),
            "duration_seconds": duration,
            "result": result,
            "error_message": error_message
        }
        
        key = f"execution:{job_id}:{execution_id}"
        await self.redis_client.setex(
            key, 
            timedelta(days=self.config.job_history_retention_days).total_seconds(),
            json.dumps(execution_data, default=str)
        )
    
    async def _get_recent_executions(self, job_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent job executions"""
        pattern = f"execution:{job_id}:*"
        keys = await self.redis_client.keys(pattern)
        
        executions = []
        for key in keys[:limit]:
            data = await self.redis_client.get(key)
            if data:
                executions.append(json.loads(data))
        
        # Sort by started_at desc
        executions.sort(key=lambda x: x['started_at'], reverse=True)
        return executions[:limit]
    
    async def _validate_dependencies(self, dependencies: List[str]) -> None:
        """Validate job dependencies exist"""
        for dep_id in dependencies:
            if not self.scheduler.get_job(dep_id):
                raise ValueError(f"Dependency job not found: {dep_id}")
    
    async def _check_dependencies(self, dependencies: List[str]) -> None:
        """Check if dependency jobs completed successfully"""
        for dep_id in dependencies:
            # Check last execution of dependency
            executions = await self._get_recent_executions(dep_id, limit=1)
            if not executions or executions[0]['status'] != JobStatus.COMPLETED.value:
                raise RuntimeError(f"Dependency job {dep_id} not completed successfully")
    
    async def _start_health_monitoring(self) -> None:
        """Start background health monitoring"""
        async def health_monitor():
            while True:
                try:
                    await asyncio.sleep(self.config.health_check_interval)
                    
                    # Update active jobs gauge
                    self.active_jobs_gauge.set(len(self.active_executions))
                    
                    # Check for stuck jobs
                    now = datetime.utcnow()
                    for execution_id, context in list(self.active_executions.items()):
                        if (now - context.started_at).total_seconds() > self.config.job_execution_timeout:
                            logger.warning(f"Job {context.job_id} execution {execution_id} appears stuck")
                    
                except Exception as e:
                    logger.error(f"Health monitoring error: {e}")
        
        asyncio.create_task(health_monitor())
    
    async def shutdown(self) -> None:
        """Shutdown the service gracefully"""
        try:
            logger.info("Shutting down cron job service")
            
            # Stop scheduler
            if self.scheduler and self.scheduler.running:
                self.scheduler.shutdown(wait=True)
            
            # Close Redis connection
            if self.redis_client:
                await self.redis_client.close()
            
            logger.info("Cron job service shutdown complete")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")