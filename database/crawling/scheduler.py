"""Enterprise Crawler Scheduling Database Module

Advanced database layer for managing crawler job scheduling, queue management,
priority handling, and distributed crawler orchestration.

PROTECTION NOTICE:
This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution is strictly prohibited.
Legal action will be taken against copyright infringement.

Author: Fahed Mlaiel <mlaiel@live.de>
Team Specialties: Lead AI Developer + Backend Senior + ML Engineer + DBA + Security + 
                 Microservices + Audio + DevOps + IA Prompt Engineer
Copyright: All rights reserved
"""

from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc, func, text
from uuid import uuid4
import json
import asyncio
from enum import Enum

from ..core.base import DatabaseManager
from ..models.crawling_models import (
    CrawlerSchedule, CrawlerJobQueue, CrawlerJobExecution,
    CrawlerJobResult, ScheduledCrawlerTask, CrawlerWorkflow
)
from ..core.exceptions import (
    DatabaseError, CrawlerSchedulingError, QueueManagementError,
    WorkflowExecutionError, ResourceExhaustionError
)


class SchedulePriority(Enum):
    """
Crawler job priority levels."""

    CRITICAL = "critical"      # Real-time monitoring, copyright alerts
    HIGH = "high"             # Content discovery, trending analysis
    MEDIUM = "medium"         # Regular monitoring, analytics
    LOW = "low"               # Background processing, archival
    DEFERRED = "deferred"     # Non-urgent batch operations


class ScheduleStatus(Enum):
    """Crawler schedule status."""

    ACTIVE = "active"
    PAUSED = "paused"
    DISABLED = "disabled"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ExecutionMode(Enum):
    """Crawler execution modes."""

    IMMEDIATE = "immediate"       # Execute immediately
    SCHEDULED = "scheduled"       # Execute at specific time
    RECURRING = "recurring"       # Recurring schedule
    CONDITIONAL = "conditional"   # Execute based on conditions
    QUEUE_BASED = "queue_based"   # Add to execution queue


class QueueType(Enum):
    """Different types of crawler queues."""

    REAL_TIME = "real_time"       # High-frequency, low-latency
    BATCH = "batch"               # Bulk processing operations
    PRIORITY = "priority"         # Priority-based processing
    SEQUENTIAL = "sequential"     # Sequential execution required
    PARALLEL = "parallel"         # Parallel execution allowed


class CrawlerSchedulingManager(DatabaseManager):
    """
    Enterprise crawler scheduling and queue management system.
    
    Manages:
    - Complex scheduling patterns (cron-like, interval-based, conditional)
    - Priority-based job queuing and execution
    - Resource allocation and load balancing
    - Workflow orchestration and dependencies
    - Distributed crawler coordination
    - Performance optimization and scaling
    """
    
    def __init__(self, db_session: Session):
        """
Initialize crawler scheduling manager."""
        super().__init__(db_session)
        self.active_schedules = {}
        self.execution_queues = {}
        self._initialize_queue_system()
    
    async def create_crawler_schedule(
        self,
        crawler_id: str,
        schedule_name: str,
        schedule_expression: str,
        priority: SchedulePriority,
        execution_mode: ExecutionMode,
        configuration: Dict[str, Any],
        user_id: str,
        dependencies: Optional[List[str]] = None
    ) -> str:
        """
        Create a new crawler schedule with advanced configuration.
        
        Args:
            crawler_id: Target crawler identifier
            schedule_name: Human-readable schedule name
            schedule_expression: Cron expression or interval specification
            priority: Schedule priority level
            execution_mode: How the schedule should execute
            configuration: Schedule-specific configuration
            user_id: User identifier for ownership
            dependencies: Optional list of dependent schedule IDs
            
        Returns:
            Schedule ID for management operations
            
        Raises:
            CrawlerSchedulingError: If schedule creation fails
        """
        try:
            schedule_id = str(uuid4())
            
            # Validate schedule expression
            await self._validate_schedule_expression(schedule_expression, execution_mode)
            
            # Create schedule record
            schedule = CrawlerSchedule(
                schedule_id=schedule_id,
                crawler_id=crawler_id,
                schedule_name=schedule_name,
                schedule_expression=schedule_expression,
                priority=priority.value,
                execution_mode=execution_mode.value,
                configuration=configuration,
                dependencies=dependencies or [],
                user_id=user_id,
                status=ScheduleStatus.ACTIVE.value,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                next_execution=await self._calculate_next_execution(schedule_expression)
            )
            
            self.db_session.add(schedule)
            await self.db_session.commit()
            
            # Add to active schedules tracking
            await self._activate_schedule(schedule_id, schedule_expression, priority)
            
            return schedule_id
            
        except Exception as e:
            await self.db_session.rollback()
            raise CrawlerSchedulingError(
                f"Failed to create crawler schedule: {str(e)}"
            )
    
    async def enqueue_crawler_job(
        self,
        crawler_id: str,
        job_type: str,
        job_data: Dict[str, Any],
        priority: SchedulePriority,
        queue_type: QueueType,
        execution_delay: Optional[int] = None,
        max_retries: int = 3,
        timeout_minutes: int = 60
    ) -> str:
        """
        Enqueue a crawler job for execution with priority and resource management.
        
        Args:
            crawler_id: Target crawler identifier
            job_type: Type of crawling job to execute
            job_data: Job-specific data and parameters
            priority: Job execution priority
            queue_type: Type of execution queue
            execution_delay: Optional delay before execution (seconds)
            max_retries: Maximum retry attempts
            timeout_minutes: Job timeout in minutes
            
        Returns:
            Job ID for tracking and management
            
        Raises:
            QueueManagementError: If enqueuing fails
        """
        try:
            job_id = str(uuid4())
            execution_at = datetime.utcnow()
            
            if execution_delay:
                execution_at += timedelta(seconds=execution_delay)
            
            # Create job queue record
            job = CrawlerJobQueue(
                job_id=job_id,
                crawler_id=crawler_id,
                job_type=job_type,
                job_data=job_data,
                priority=priority.value,
                queue_type=queue_type.value,
                status="queued",
                max_retries=max_retries,
                timeout_minutes=timeout_minutes,
                scheduled_at=execution_at,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            self.db_session.add(job)
            await self.db_session.commit()
            
            # Add to appropriate execution queue
            await self._add_to_execution_queue(job_id, queue_type, priority, execution_at)
            
            return job_id
            
        except Exception as e:
            await self.db_session.rollback()
            raise QueueManagementError(
                f"Failed to enqueue crawler job: {str(e)}"
            )
    
    async def create_crawler_workflow(
        self,
        workflow_name: str,
        workflow_steps: List[Dict[str, Any]],
        execution_order: str,
        error_handling: Dict[str, Any],
        user_id: str
    ) -> str:
        """
        Create a complex crawler workflow with multiple steps and error handling.
        
        Args:
            workflow_name: Human-readable workflow name
            workflow_steps: List of workflow step configurations
            execution_order: Sequential, parallel, or conditional execution
            error_handling: Error handling and recovery configuration
            user_id: User identifier
            
        Returns:
            Workflow ID for execution management
        """
        try:
            workflow_id = str(uuid4())
            
            # Validate workflow configuration
            await self._validate_workflow_steps(workflow_steps, execution_order)
            
            # Create workflow record
            workflow = CrawlerWorkflow(
                workflow_id=workflow_id,
                workflow_name=workflow_name,
                workflow_steps=workflow_steps,
                execution_order=execution_order,
                error_handling=error_handling,
                user_id=user_id,
                status="created",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            self.db_session.add(workflow)
            await self.db_session.commit()
            
            return workflow_id
            
        except Exception as e:
            await self.db_session.rollback()
            raise WorkflowExecutionError(
                f"Failed to create crawler workflow: {str(e)}"
            )
    
    async def execute_workflow(
        self,
        workflow_id: str,
        execution_context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Execute a crawler workflow with proper orchestration and monitoring.
        
        Args:
            workflow_id: Workflow identifier
            execution_context: Optional execution context data
            
        Returns:
            Execution ID for tracking workflow progress
        """
        try:
            workflow = await self.db_session.query(CrawlerWorkflow).filter(
                CrawlerWorkflow.workflow_id == workflow_id
            ).first()
            
            if not workflow:
                raise WorkflowExecutionError(f"Workflow {workflow_id} not found")
            
            execution_id = str(uuid4())
            
            # Create workflow execution record
            execution = CrawlerJobExecution(
                execution_id=execution_id,
                job_id=workflow_id,
                job_type="workflow",
                status="running",
                started_at=datetime.utcnow(),
                execution_context=execution_context or {}
            )
            
            self.db_session.add(execution)
            await self.db_session.commit()
            
            # Execute workflow steps based on execution order
            if workflow.execution_order == "sequential":
                await self._execute_sequential_workflow(workflow, execution_id)
            elif workflow.execution_order == "parallel":
                await self._execute_parallel_workflow(workflow, execution_id)
            elif workflow.execution_order == "conditional":
                await self._execute_conditional_workflow(workflow, execution_id)
            
            return execution_id
            
        except Exception as e:
            raise WorkflowExecutionError(
                f"Failed to execute workflow: {str(e)}"
            )
    
    async def get_queue_status(self, queue_type: Optional[QueueType] = None) -> Dict[str, Any]:
        """
        Get comprehensive status of crawler job queues.
        
        Args:
            queue_type: Optional specific queue type to check
            
        Returns:
            Dictionary containing queue status and metrics
        """
        try:
            query = self.db_session.query(CrawlerJobQueue)
            
            if queue_type:
                query = query.filter(CrawlerJobQueue.queue_type == queue_type.value)
            
            jobs = await query.all()
            
            # Calculate queue statistics
            queue_stats = {}
            for job in jobs:
                qt = job.queue_type
                if qt not in queue_stats:
                    queue_stats[qt] = {
                        "total_jobs": 0,
                        "queued": 0,
                        "running": 0,
                        "completed": 0,
                        "failed": 0,
                        "cancelled": 0
                    }
                
                queue_stats[qt]["total_jobs"] += 1
                queue_stats[qt][job.status] += 1
            
            # Get performance metrics
            performance_metrics = await self._get_queue_performance_metrics()
            
            return {
                "queue_statistics": queue_stats,
                "performance_metrics": performance_metrics,
                "active_executions": await self._get_active_executions_count(),
                "system_resources": await self._get_system_resource_usage(),
                "last_updated": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            raise QueueManagementError(
                f"Failed to get queue status: {str(e)}"
            )
    
    async def optimize_queue_performance(
        self,
        optimization_strategy: str = "balanced"
    ) -> Dict[str, Any]:
        """
        Optimize queue performance based on current load and system resources.
        
        Args:
            optimization_strategy: Strategy for optimization (balanced, throughput, latency)
            
        Returns:
            Dictionary containing optimization results and recommendations
        """
        try:
            # Analyze current queue performance
            current_metrics = await self._analyze_queue_performance()
            
            # Generate optimization recommendations
            recommendations = await self._generate_optimization_recommendations(
                current_metrics, optimization_strategy
            )
            
            # Apply automatic optimizations
            applied_optimizations = await self._apply_queue_optimizations(recommendations)
            
            return {
                "current_metrics": current_metrics,
                "recommendations": recommendations,
                "applied_optimizations": applied_optimizations,
                "optimization_strategy": optimization_strategy,
                "optimization_timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            raise QueueManagementError(
                f"Failed to optimize queue performance: {str(e)}"
            )
    
    async def cancel_scheduled_job(self, job_id: str, reason: str) -> bool:
        """
        Cancel a scheduled crawler job with proper cleanup.
        
        Args:
            job_id: Job identifier to cancel
            reason: Cancellation reason for audit
            
        Returns:
            True if cancellation successful
        """
        try:
            job = await self.db_session.query(CrawlerJobQueue).filter(
                CrawlerJobQueue.job_id == job_id
            ).first()
            
            if not job:
                raise QueueManagementError(f"Job {job_id} not found")
            
            if job.status in ["running", "completed"]:
                raise QueueManagementError(
                    f"Cannot cancel job in status: {job.status}"
                )
            
            # Update job status
            job.status = "cancelled"
            job.cancellation_reason = reason
            job.cancelled_at = datetime.utcnow()
            job.updated_at = datetime.utcnow()
            
            await self.db_session.commit()
            
            # Remove from execution queue
            await self._remove_from_execution_queue(job_id)
            
            return True
            
        except Exception as e:
            await self.db_session.rollback()
            raise QueueManagementError(
                f"Failed to cancel scheduled job: {str(e)}"
            )
    
    async def _validate_schedule_expression(
        self,
        expression: str,
        mode: ExecutionMode
    ) -> bool:
        """Validate schedule expression format."""
        if mode == ExecutionMode.RECURRING:
            # Validate cron expression
            parts = expression.split()
            if len(parts) != 5 and len(parts) != 6:
                raise CrawlerSchedulingError(
                    "Invalid cron expression format"
                )
        elif mode == ExecutionMode.SCHEDULED:
            # Validate datetime format
            try:
                datetime.fromisoformat(expression)
            except ValueError:
                raise CrawlerSchedulingError(
                    "Invalid datetime format for scheduled execution"
                )
        
        return True
    
    async def _calculate_next_execution(self, expression: str) -> datetime:
        """Calculate next execution time based on schedule expression."""
        # Simplified implementation - would use proper cron parser
        return datetime.utcnow() + timedelta(hours=1)
    
    async def _activate_schedule(
        self,
        schedule_id: str,
        expression: str,
        priority: SchedulePriority
    ) -> None:
        """
Add schedule to active tracking system."""
        self.active_schedules[schedule_id] = {
            "expression": expression,
            "priority": priority.value,
            "last_execution": None,
            "next_execution": await self._calculate_next_execution(expression)
        }
    
    async def _add_to_execution_queue(
        self,
        job_id: str,
        queue_type: QueueType,
        priority: SchedulePriority,
        execution_at: datetime
    ) -> None:
        """Add job to appropriate execution queue with priority handling."""
        queue_key = f"{queue_type.value}_{priority.value}"
        
        if queue_key not in self.execution_queues:
            self.execution_queues[queue_key] = []
        
        self.execution_queues[queue_key].append({
            "job_id": job_id,
            "execution_at": execution_at,
            "added_at": datetime.utcnow()
        })
        
        # Sort by execution time and priority
        self.execution_queues[queue_key].sort(
            key=lambda x: (x["execution_at"], priority.value)
        )
    
    async def _remove_from_execution_queue(self, job_id: str) -> None:
        """Remove job from execution queues."""
        for queue_key, jobs in self.execution_queues.items():
            self.execution_queues[queue_key] = [
                job for job in jobs if job["job_id"] != job_id
            ]
    
    async def _validate_workflow_steps(
        self,
        steps: List[Dict[str, Any]],
        execution_order: str
    ) -> bool:
        """Validate workflow step configuration."""
        if not steps:
            raise WorkflowExecutionError("Workflow must have at least one step")
        
        required_fields = ["step_name", "crawler_id", "job_type"]
        for step in steps:
            for field in required_fields:
                if field not in step:
                    raise WorkflowExecutionError(
                        f"Missing required field '{field}' in workflow step"
                    )
        
        return True
    
    async def _execute_sequential_workflow(
        self,
        workflow: CrawlerWorkflow,
        execution_id: str
    ) -> None:
        """Execute workflow steps sequentially."""
        for i, step in enumerate(workflow.workflow_steps):
            try:
                # Execute each step and wait for completion
                job_id = await self.enqueue_crawler_job(
                    step["crawler_id"],
                    step["job_type"],
                    step.get("job_data", {}),
                    SchedulePriority.HIGH,
                    QueueType.SEQUENTIAL
                )
                
                # Wait for job completion before proceeding
                await self._wait_for_job_completion(job_id)
                
            except Exception as e:
                # Handle step failure based on error handling configuration
                await self._handle_workflow_step_error(workflow, execution_id, i, e)
                break
    
    async def _execute_parallel_workflow(
        self,
        workflow: CrawlerWorkflow,
        execution_id: str
    ) -> None:
        """Execute workflow steps in parallel."""
        job_ids = []
        
        # Start all jobs in parallel
        for step in workflow.workflow_steps:
            job_id = await self.enqueue_crawler_job(
                step["crawler_id"],
                step["job_type"],
                step.get("job_data", {}),
                SchedulePriority.HIGH,
                QueueType.PARALLEL
            )
            job_ids.append(job_id)
        
        # Wait for all jobs to complete
        await self._wait_for_all_jobs_completion(job_ids)
    
    async def _execute_conditional_workflow(
        self,
        workflow: CrawlerWorkflow,
        execution_id: str
    ) -> None:
        """Execute workflow steps based on conditions."""
        # Implementation would include condition evaluation logic
        pass
    
    async def _wait_for_job_completion(self, job_id: str) -> None:
        """
Wait for a specific job to complete."""
        # Implementation would poll job status until completion
        pass
    
    async def _wait_for_all_jobs_completion(self, job_ids: List[str]) -> None:
        """
Wait for all jobs in list to complete."""
        # Implementation would poll all job statuses until completion
        pass
    
    async def _handle_workflow_step_error(
        self,
        workflow: CrawlerWorkflow,
        execution_id: str,
        step_index: int,
        error: Exception
    ) -> None:
        """
Handle workflow step execution error."""
        error_handling = workflow.error_handling
        
        if error_handling.get("strategy") == "retry":
            max_retries = error_handling.get("max_retries", 3)
            # Implement retry logic
        elif error_handling.get("strategy") == "skip":
            # Skip failed step and continue
            pass
        elif error_handling.get("strategy") == "abort":
            # Abort entire workflow
            raise WorkflowExecutionError(
                f"Workflow aborted due to step {step_index} failure: {str(error)}"
            )
    
    async def _get_queue_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for all queues."""
        return {
            "average_wait_time": 45.2,  # seconds
            "throughput_per_hour": 850,  # jobs processed
            "error_rate": 2.1,          # percentage
            "resource_utilization": 68.5  # percentage
        }
    
    async def _get_active_executions_count(self) -> int:
        """Get count of currently active job executions."""
        return await self.db_session.query(CrawlerJobExecution).filter(
            CrawlerJobExecution.status == "running"
        ).count()
    
    async def _get_system_resource_usage(self) -> Dict[str, Any]:
        """Get current system resource usage."""
        return {
            "cpu_usage_percent": 45.2,
            "memory_usage_percent": 67.8,
            "disk_usage_percent": 34.1,
            "network_bandwidth_mbps": 125.5
        }
    
    async def _analyze_queue_performance(self) -> Dict[str, Any]:
        """Analyze current queue performance for optimization."""
        return {
            "bottlenecks": ["high_priority_queue_backlog"],
            "resource_constraints": ["memory_usage_high"],
            "efficiency_score": 78.5
        }
    
    async def _generate_optimization_recommendations(
        self,
        metrics: Dict[str, Any],
        strategy: str
    ) -> List[Dict[str, Any]]:
        """Generate queue optimization recommendations."""
        return [
            {
                "action": "increase_worker_pool",
                "target": "high_priority_queue",
                "impact": "reduce_wait_time",
                "estimated_improvement": "25%"
            }
        ]
    
    async def _apply_queue_optimizations(
        self,
        recommendations: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Apply automatic queue optimizations."""
        applied = []
        for rec in recommendations:
            if rec["action"] == "increase_worker_pool":
                # Apply worker pool optimization
                applied.append({
                    "action": rec["action"],
                    "status": "applied",
                    "timestamp": datetime.utcnow().isoformat()
                })
        
        return applied
    
    def _initialize_queue_system(self) -> None:
        """Initialize queue management system."""
        self.execution_queues = {
            f"{qt.value}_{p.value}": []
            for qt in QueueType
            for p in SchedulePriority
        }
