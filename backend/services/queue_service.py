"""Queue Service - Consolidated Queue Management Services
================================================================

Comprehensive queue system providing job processing, task scheduling,
and workflow management for the IA Influencer Agent platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import logging
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import uuid
import asyncio
import json

logger = logging.getLogger(__name__)

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"


class JobStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRY = "retry"


class JobPriority(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


@dataclass
class QueueJob:
    job_id: str
    queue_name: str
    job_type: str
    payload: Dict[str, Any]
    status: JobStatus = JobStatus.PENDING
    priority: JobPriority = JobPriority.NORMAL
    max_retries: int = 3
    retry_count: int = 0
    scheduled_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


class JobProcessor:
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.handlers = {}
        
    def register_handler(self, job_type: str, handler: Callable):
        """Register job handler function"""
        self.handlers[job_type] = handler
        logger.info(f"Registered handler for job type: {job_type}")
    
    async def process_job(self, job: QueueJob) -> Dict[str, Any]:
        """Process a single job"""
        try:
            job.status = JobStatus.PROCESSING
            job.started_at = datetime.utcnow()
            
            handler = self.handlers.get(job.job_type)
            if not handler:
                raise ValueError(f"No handler registered for job type: {job.job_type}")
            
            # Execute job handler
            result = await handler(job.payload)
            
            job.status = JobStatus.COMPLETED
            job.completed_at = datetime.utcnow()
            
            logger.info(f"Job completed: {job.job_id}")
            return {
                'success': True,
                'result': result,
                'job_id': job.job_id
            }
            
        except Exception as e:
            job.status = JobStatus.FAILED
            job.error_message = str(e)
            job.retry_count += 1
            
            # Check if should retry
            if job.retry_count < job.max_retries:
                job.status = JobStatus.RETRY
                job.scheduled_at = datetime.utcnow() + timedelta(minutes=job.retry_count * 5)
            
            logger.error(f"Job failed: {job.job_id} - {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'job_id': job.job_id,
                'retry_count': job.retry_count
            }


class TaskScheduler:
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.scheduled_tasks = {}
        
    async def schedule_task(self, task_id: str, schedule_time: datetime, job_data: Dict[str, Any]) -> bool:
        """Schedule a task for future execution"""
        try:
            self.scheduled_tasks[task_id] = {
                'schedule_time': schedule_time,
                'job_data': job_data,
                'created_at': datetime.utcnow()
            }
            
            logger.info(f"Scheduled task: {task_id} for {schedule_time}")
            return True
            
        except Exception as e:
            logger.error(f"Task scheduling error: {str(e)}")
            return False
    
    async def get_due_tasks(self) -> List[Dict[str, Any]]:
        """Get tasks that are due for execution"""
        try:
            current_time = datetime.utcnow()
            due_tasks = []
            
            for task_id, task_data in self.scheduled_tasks.items():
                if task_data['schedule_time'] <= current_time:
                    due_tasks.append({
                        'task_id': task_id,
                        **task_data['job_data']
                    })
            
            # Remove processed tasks
            for task in due_tasks:
                del self.scheduled_tasks[task['task_id']]
            
            return due_tasks
            
        except Exception as e:
            logger.error(f"Due tasks retrieval error: {str(e)}")
            return []


class WorkflowManager:
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.workflows = {}
        
    async def create_workflow(self, workflow_id: str, steps: List[Dict[str, Any]]) -> bool:
        """Create a multi-step workflow"""
        try:
            workflow = {
                'workflow_id': workflow_id,
                'steps': steps,
                'current_step': 0,
                'status': 'pending',
                'created_at': datetime.utcnow(),
                'results': []
            }
            
            self.workflows[workflow_id] = workflow
            logger.info(f"Created workflow: {workflow_id} with {len(steps)} steps")
            return True
            
        except Exception as e:
            logger.error(f"Workflow creation error: {str(e)}")
            return False
    
    async def execute_workflow_step(self, workflow_id: str) -> Dict[str, Any]:
        """Execute the next step in a workflow"""
        try:
            workflow = self.workflows.get(workflow_id)
            if not workflow:
                raise ValueError(f"Workflow not found: {workflow_id}")
            
            if workflow['current_step'] >= len(workflow['steps']):
                workflow['status'] = 'completed'
                return {
                    'success': True,
                    'workflow_completed': True,
                    'workflow_id': workflow_id
                }
            
            current_step = workflow['steps'][workflow['current_step']]
            
            # Execute step (simplified)
            step_result = {
                'step_index': workflow['current_step'],
                'step_type': current_step.get('type'),
                'result': 'success',
                'executed_at': datetime.utcnow()
            }
            
            workflow['results'].append(step_result)
            workflow['current_step'] += 1
            
            logger.info(f"Executed workflow step: {workflow_id} step {workflow['current_step']}")
            return {
                'success': True,
                'workflow_completed': False,
                'step_result': step_result
            }
            
        except Exception as e:
            logger.error(f"Workflow step execution error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }


class QueueService:
    """
    Unified Queue Service that orchestrates all queue-related services
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        
        # Initialize sub-services
        self.job_processor = JobProcessor(self.config.get('processor', {}))
        self.task_scheduler = TaskScheduler(self.config.get('scheduler', {}))
        self.workflow_manager = WorkflowManager(self.config.get('workflow', {}))
        
        # Job queues by priority
        self.queues = {
            JobPriority.URGENT: asyncio.Queue(),
            JobPriority.HIGH: asyncio.Queue(), 
            JobPriority.NORMAL: asyncio.Queue(),
            JobPriority.LOW: asyncio.Queue()
        }
        
        self.running = False
        self.worker_tasks = []
        
        logger.info("📋 Queue Service initialized")
    
    async def initialize(self):
        """Initialize all queue services"""
        logger.info("🚀 Initializing Queue Service")
        self.running = True
        
        # Start worker tasks
        worker_count = self.config.get('worker_count', 4)
        for i in range(worker_count):
            task = asyncio.create_task(self._worker_loop(f"worker-{i}"))
            self.worker_tasks.append(task)
        
        # Start scheduler task
        scheduler_task = asyncio.create_task(self._scheduler_loop())
        self.worker_tasks.append(scheduler_task)
    
    async def shutdown(self):
        """Shutdown all queue services"""
        logger.info("🛑 Shutting down Queue Service")
        self.running = False
        
        # Cancel worker tasks
        for task in self.worker_tasks:
            task.cancel()
        
        # Wait for tasks to complete
        await asyncio.gather(*self.worker_tasks, return_exceptions=True)
    
    async def _worker_loop(self, worker_id: str):
        """Main worker loop to process jobs"""
        logger.info(f"Started worker: {worker_id}")
        
        while self.running:
            try:
                # Check queues by priority
                job = None
                for priority in [JobPriority.URGENT, JobPriority.HIGH, JobPriority.NORMAL, JobPriority.LOW]:
                    try:
                        job = self.queues[priority].get_nowait()
                        break
                    except asyncio.QueueEmpty:
                        continue
                
                if job:
                    await self.job_processor.process_job(job)
                else:
                    # No jobs available, wait a bit
                    await asyncio.sleep(1)
                    
            except Exception as e:
                logger.error(f"Worker {worker_id} error: {str(e)}")
                await asyncio.sleep(5)  # Brief pause on error
    
    async def _scheduler_loop(self):
        """Scheduler loop to check for due tasks"""
        logger.info("Started scheduler loop")
        
        while self.running:
            try:
                due_tasks = await self.task_scheduler.get_due_tasks()
                
                for task_data in due_tasks:
                    job = QueueJob(
                        job_id=str(uuid.uuid4()),
                        queue_name='scheduled',
                        job_type=task_data.get('job_type', 'default'),
                        payload=task_data.get('payload', {}),
                        priority=JobPriority(task_data.get('priority', 'normal'))
                    )
                    
                    await self.add_job(job)
                
                await asyncio.sleep(10)  # Check every 10 seconds
                
            except Exception as e:
                logger.error(f"Scheduler loop error: {str(e)}")
                await asyncio.sleep(30)
    
    async def add_job(self, job: QueueJob) -> bool:
        """Add job to queue"""
        try:
            queue = self.queues[job.priority]
            await queue.put(job)
            
            logger.info(f"Added job to queue: {job.job_id} (priority: {job.priority})")
            return True
            
        except Exception as e:
            logger.error(f"Add job error: {str(e)}")
            return False
    
    async def create_job(self, job_data: Dict[str, Any]) -> QueueJob:
        """Create and queue a new job"""
        try:
            job = QueueJob(
                job_id=str(uuid.uuid4()),
                queue_name=job_data.get('queue_name', 'default'),
                job_type=job_data['job_type'],
                payload=job_data.get('payload', {}),
                priority=JobPriority(job_data.get('priority', 'normal')),
                max_retries=job_data.get('max_retries', 3),
                scheduled_at=job_data.get('scheduled_at')
            )
            
            if job.scheduled_at and job.scheduled_at > datetime.utcnow():
                # Schedule for later
                await self.task_scheduler.schedule_task(job.job_id, job.scheduled_at, {
                    'job_type': job.job_type,
                    'payload': job.payload,
                    'priority': job.priority.value
                })
            else:
                # Add to queue immediately
                await self.add_job(job)
            
            return job
            
        except Exception as e:
            logger.error(f"Job creation error: {str(e)}")
            raise
    
    def register_job_handler(self, job_type: str, handler: Callable):
        """Register job handler"""
        self.job_processor.register_handler(job_type, handler)
    
    async def create_workflow(self, workflow_id: str, steps: List[Dict[str, Any]]) -> bool:
        """Create workflow"""
        return await self.workflow_manager.create_workflow(workflow_id, steps)
    
    async def execute_workflow_step(self, workflow_id: str) -> Dict[str, Any]:
        """Execute workflow step"""
        return await self.workflow_manager.execute_workflow_step(workflow_id)
    
    async def get_queue_stats(self) -> Dict[str, Any]:
        """Get queue statistics"""
        try:
            stats = {
                'queue_sizes': {},
                'worker_count': len(self.worker_tasks) - 1,  # Exclude scheduler
                'running': self.running,
                'timestamp': datetime.utcnow()
            }
            
            for priority, queue in self.queues.items():
                stats['queue_sizes'][priority.value] = queue.qsize()
            
            return stats
            
        except Exception as e:
            logger.error(f"Queue stats error: {str(e)}")
            return {}


__all__ = [
    "JobStatus", "JobPriority", "QueueJob",
    "JobProcessor", "TaskScheduler", "WorkflowManager",
    "QueueService"
]

logger.info(f"📋 Queue Service v{__version__} loaded")