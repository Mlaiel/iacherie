"""
Scheduler Service module
Enterprise implementation for Ainflue platform
"""

#!/usr/bin/env python3
"""
🔧 SCHEDULER SERVICE
===================

Advanced distributed task scheduling and job management service for the Ainflue platform.
Handles periodic tasks, job queuing, and distributed cron-like functionality.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved

⚠️ STRICT COPYRIGHT WARNING ⚠️
This code is proprietary and confidential. Unauthorized use, reproduction,
distribution, or modification is strictly prohibited and will be prosecuted
to the full extent of the law.
"""

import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, asdict
from enum import Enum
import json
import uuid
from concurrent.futures import ThreadPoolExecutor
import redis.asyncio as redis

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class JobStatus(Enum):
    """Job execution status enumeration"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    SCHEDULED = "scheduled"

class JobPriority(Enum):
    """Job priority levels"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4

@dataclass
class ScheduledJob:
    """Scheduled job definition"""
    id: str
    name: str
    function_name: str
    args: List[Any]
    kwargs: Dict[str, Any]
    schedule: str  # Cron-like expression
    priority: JobPriority
    status: JobStatus
    created_at: datetime
    next_run: Optional[datetime] = None
    last_run: Optional[datetime] = None
    run_count: int = 0
    max_retries: int = 3
    retry_count: int = 0
    timeout: int = 300  # seconds
    enabled: bool = True

class CronParser:
    """Simple cron expression parser"""
    
    @staticmethod
    def parse_cron(cron_expr: str) -> Dict[str, Any]:
        """Parse cron expression (simplified)"""
        parts = cron_expr.split()
        if len(parts) != 5:
            raise ValueError("Invalid cron expression")
        
        return {
            'minute': parts[0],
            'hour': parts[1],
            'day': parts[2],
            'month': parts[3],
            'weekday': parts[4]
        }
    
    @staticmethod
    def next_run_time(cron_expr: str, from_time: datetime = None) -> datetime:
        """Calculate next run time (simplified)"""
        if from_time is None:
            from_time = datetime.now()
        
        # Simple implementation - for production use croniter library
        if cron_expr == "*/5 * * * *":  # Every 5 minutes
            return from_time + timedelta(minutes=5)
        elif cron_expr == "0 * * * *":  # Every hour
            return from_time.replace(minute=0) + timedelta(hours=1)
        elif cron_expr == "0 0 * * *":  # Daily at midnight
            return (from_time + timedelta(days=1)).replace(hour=0, minute=0)
        else:
            # Default to 1 hour
            return from_time + timedelta(hours=1)

class SchedulerService:
    """Advanced distributed task scheduling service"""
    
    def __init__(self) -> None:
        self.service_name = "SchedulerService"
        self.version = "1.0.0"
        self.jobs: Dict[str, ScheduledJob] = {}
        self.job_functions: Dict[str, Callable] = {}
        self.redis_client: Optional[redis.Redis] = None
        self.running = False
        self.executor = ThreadPoolExecutor(max_workers=10)
        self.scheduler_task = None
        
        logger.info(f"✅ {self.service_name} v{self.version} initialized")
    
    async def initialize(self, redis_url -> None: str = "redis -> None://localhost -> None:6379/0") -> None:
        """Initialize the scheduler service"""
        try:
            # Initialize Redis connection
            self.redis_client = redis.from_url(redis_url, decode_responses=True)
            await self.redis_client.ping()
            
            # Load existing jobs from Redis
            await self._load_jobs_from_storage()
            
            logger.info(f"🔧 {self.service_name} initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize {self.service_name}: {str(e)}")
            return False
    
    async def register_job_function(self, name -> None: str, function -> None: Callable) -> None:
        """Register a function that can be scheduled"""
        self.job_functions[name] = function
        logger.info(f"📋 Registered job function: {name}")
    
    async def schedule_job(
        self,
        name: str,
        function_name: str,
        schedule: str,
        args: List[Any] = None,
        kwargs: Dict[str, Any] = None,
        priority: JobPriority = JobPriority.NORMAL,
        max_retries: int = 3,
        timeout: int = 300
    ) -> str:
        """Schedule a new job"""
        job_id = str(uuid.uuid4())
        
        job = ScheduledJob(
            id=job_id,
            name=name,
            function_name=function_name,
            args=args or [],
            kwargs=kwargs or {},
            schedule=schedule,
            priority=priority,
            status=JobStatus.SCHEDULED,
            created_at=datetime.now(),
            max_retries=max_retries,
            timeout=timeout
        )
        
        # Calculate next run time
        job.next_run = CronParser.next_run_time(schedule)
        
        self.jobs[job_id] = job
        await self._save_job_to_storage(job)
        
        logger.info(f"⏰ Scheduled job '{name}' (ID: {job_id}) to run at {job.next_run}")
        return job_id
    
    async def start_scheduler(self) -> None:
        """Start the scheduler main loop"""
        self.running = True
        self.scheduler_task = asyncio.create_task(self._scheduler_loop())
        logger.info(f"🚀 {self.service_name} started")
    
    async def stop_scheduler(self) -> None:
        """Stop the scheduler"""
        self.running = False
        if self.scheduler_task:
            self.scheduler_task.cancel()
            try:
                await self.scheduler_task
            except asyncio.CancelledError:
                pass
        
        self.executor.shutdown(wait=True)
        if self.redis_client:
            await self.redis_client.close()
        
        logger.info(f"🛑 {self.service_name} stopped")
    
    async def _scheduler_loop(self) -> None:
        """Main scheduler loop"""
        while self.running:
            try:
                current_time = datetime.now()
                
                # Check for jobs to execute
                jobs_to_run = [
                    job for job in self.jobs.values()
                    if (job.next_run and job.next_run <= current_time and 
                        job.enabled and job.status in [JobStatus.SCHEDULED, JobStatus.PENDING])
                ]
                
                # Sort by priority
                jobs_to_run.sort(key=lambda x: x.priority.value, reverse=True)
                
                for job in jobs_to_run:
                    asyncio.create_task(self._execute_job(job))
                
                # Sleep for a short interval
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"❌ Error in scheduler loop: {str(e)}")
                await asyncio.sleep(5)
    
    async def _execute_job(self, job -> None: ScheduledJob) -> None:
        """Execute a scheduled job"""
        try:
            logger.info(f"🔄 Executing job '{job.name}' (ID: {job.id})")
            
            # Update job status
            job.status = JobStatus.RUNNING
            job.last_run = datetime.now()
            await self._save_job_to_storage(job)
            
            # Get the function to execute
            if job.function_name not in self.job_functions:
                raise ValueError(f"Function '{job.function_name}' not registered")
            
            function = self.job_functions[job.function_name]
            
            # Execute with timeout
            try:
                if asyncio.iscoroutinefunction(function):
                    await asyncio.wait_for(
                        function(*job.args, **job.kwargs),
                        timeout=job.timeout
                    )
                else:
                    # Run in thread pool for sync functions
                    await asyncio.wait_for(
                        asyncio.get_event_loop().run_in_executor(
                            self.executor, function, *job.args, **job.kwargs
                        ),
                        timeout=job.timeout
                    )
                
                # Job completed successfully
                job.status = JobStatus.COMPLETED
                job.run_count += 1
                job.retry_count = 0
                
                # Calculate next run time
                job.next_run = CronParser.next_run_time(job.schedule, datetime.now())
                
                logger.info(f"✅ Job '{job.name}' completed successfully")
                
            except asyncio.TimeoutError:
                raise Exception(f"Job timed out after {job.timeout} seconds")
            
        except Exception as e:
            logger.error(f"❌ Job '{job.name}' failed: {str(e)}")
            
            job.status = JobStatus.FAILED
            job.retry_count += 1
            
            # Retry logic
            if job.retry_count < job.max_retries:
                job.status = JobStatus.SCHEDULED
                job.next_run = datetime.now() + timedelta(minutes=5)  # Retry in 5 minutes
                logger.info(f"🔄 Scheduling retry {job.retry_count}/{job.max_retries} for job '{job.name}'")
            else:
                logger.error(f"❌ Job '{job.name}' failed permanently after {job.max_retries} retries")
        
        finally:
            await self._save_job_to_storage(job)
    
    async def _save_job_to_storage(self, job -> None: ScheduledJob) -> None:
        """Save job to Redis storage"""
        if self.redis_client:
            try:
                job_data = asdict(job)
                # Convert datetime objects to ISO strings
                for key, value in job_data.items():
                    if isinstance(value, datetime):
                        job_data[key] = value.isoformat() if value else None
                    elif isinstance(value, (JobStatus, JobPriority)):
                        job_data[key] = value.value
                
                await self.redis_client.hset(
                    f"scheduler:jobs",
                    job.id,
                    json.dumps(job_data)
                )
            except Exception as e:
                logger.error(f"❌ Failed to save job to storage: {str(e)}")
    
    async def _load_jobs_from_storage(self) -> None:
        """Load jobs from Redis storage"""
        if self.redis_client:
            try:
                jobs_data = await self.redis_client.hgetall("scheduler:jobs")
                
                for job_id, job_json in jobs_data.items():
                    job_data = json.loads(job_json)
                    
                    # Convert ISO strings back to datetime objects
                    for key in ['created_at', 'next_run', 'last_run']:
                        if job_data.get(key):
                            job_data[key] = datetime.fromisoformat(job_data[key])
                    
                    # Convert enums
                    job_data['status'] = JobStatus(job_data['status'])
                    job_data['priority'] = JobPriority(job_data['priority'])
                    
                    job = ScheduledJob(**job_data)
                    self.jobs[job_id] = job
                
                logger.info(f"📂 Loaded {len(self.jobs)} jobs from storage")
                
            except Exception as e:
                logger.error(f"❌ Failed to load jobs from storage: {str(e)}")
    
    async def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get job status and details"""
        if job_id in self.jobs:
            job = self.jobs[job_id]
            return {
                'id': job.id,
                'name': job.name,
                'status': job.status.value,
                'priority': job.priority.value,
                'schedule': job.schedule,
                'next_run': job.next_run.isoformat() if job.next_run else None,
                'last_run': job.last_run.isoformat() if job.last_run else None,
                'run_count': job.run_count,
                'retry_count': job.retry_count,
                'enabled': job.enabled
            }
        return None
    
    async def list_jobs(self) -> List[Dict[str, Any]]:
        """List all scheduled jobs"""
        return [await self.get_job_status(job_id) for job_id in self.jobs.keys()]
    
    async def cancel_job(self, job_id: str) -> bool:
        """Cancel a scheduled job"""
        if job_id in self.jobs:
            self.jobs[job_id].status = JobStatus.CANCELLED
            self.jobs[job_id].enabled = False
            await self._save_job_to_storage(self.jobs[job_id])
            logger.info(f"🚫 Cancelled job: {job_id}")
            return True
        return False
    
    async def delete_job(self, job_id: str) -> bool:
        """Delete a job completely"""
        if job_id in self.jobs:
            del self.jobs[job_id]
            
            if self.redis_client:
                await self.redis_client.hdel("scheduler:jobs", job_id)
            
            logger.info(f"🗑️ Deleted job: {job_id}")
            return True
        return False
    
    async def get_service_health(self) -> Dict[str, Any]:
        """Get service health status"""
        return {
            'service': self.service_name,
            'version': self.version,
            'status': 'healthy' if self.running else 'stopped',
            'total_jobs': len(self.jobs),
            'active_jobs': len([j for j in self.jobs.values() if j.enabled]),
            'redis_connected': self.redis_client is not None,
            'timestamp': datetime.now().isoformat()
        }

# Example job functions
async def example_async_job(message -> None: str) -> None:
    """Example async job function"""
    logger.info(f"🔄 Executing async job: {message}")
    await asyncio.sleep(2)
    logger.info(f"✅ Async job completed: {message}")

def example_sync_job(message -> None: str) -> None:
    """Example sync job function"""
    logger.info(f"🔄 Executing sync job: {message}")
    time.sleep(2)
    logger.info(f"✅ Sync job completed: {message}")

# Service instance
scheduler_service = SchedulerService()

# Example usage
async def main() -> None:
    """Example usage of the scheduler service"""
    try:
        # Initialize service
        await scheduler_service.initialize()
        
        # Register job functions
        await scheduler_service.register_job_function("async_job", example_async_job)
        await scheduler_service.register_job_function("sync_job", example_sync_job)
        
        # Schedule jobs
        job1_id = await scheduler_service.schedule_job(
            name="Daily Report",
            function_name="async_job",
            schedule="0 0 * * *",  # Daily at midnight
            args=["Daily report generation"],
            priority=JobPriority.HIGH
        )
        
        job2_id = await scheduler_service.schedule_job(
            name="Health Check",
            function_name="sync_job",
            schedule="*/5 * * * *",  # Every 5 minutes
            args=["System health check"],
            priority=JobPriority.NORMAL
        )
        
        # Start scheduler
        await scheduler_service.start_scheduler()
        
        # Let it run for a while
        await asyncio.sleep(30)
        
        # Check job status
        job1_status = await scheduler_service.get_job_status(job1_id)
        print(f"Job 1 status: {job1_status}")
        
        # List all jobs
        all_jobs = await scheduler_service.list_jobs()
        print(f"All jobs: {all_jobs}")
        
        # Service health
        health = await scheduler_service.get_service_health()
        print(f"Service health: {health}")
        
    except Exception as e:
        logger.error(f"❌ Error in main: {str(e)}")
    finally:
        await scheduler_service.stop_scheduler()

if __name__ == "__main__":
    asyncio.run(main())