"""IA-Influencer Agent - Advanced Workflow Scheduler

Enterprise-grade workflow scheduling system with intelligent timing and resource optimization.
Provides sophisticated scheduling capabilities for content creator workflows.

Key Features:
- Intelligent workflow scheduling
- Resource-aware scheduling
- Time-zone aware scheduling
- Recurring workflow patterns
- Priority-based scheduling
- Dynamic schedule optimization

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: 2025 - All Rights Reserved

⚠️ IMPORTANT LEGAL NOTICE ⚠️
This code is the exclusive intellectual property of Fahed Mlaiel.
Unauthorized copying, distribution, or use is strictly prohibited.
Any violation will result in legal action.

Contact: mlaiel@live.de for licensing inquiries.
"""import asyncio
import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any, Callable, Union, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
import uuid
import json
import croniter
import pytz
from collections import defaultdict, deque
import heapq
from concurrent.futures import ThreadPoolExecutor
import threading

from ..base import BaseAgent


class ScheduleType(Enum):
    """Schedule type enumeration."""    ONE_TIME = "one_time"
    RECURRING = "recurring"
    CONDITIONAL = "conditional"
    EVENT_DRIVEN = "event_driven"
    ADAPTIVE = "adaptive"


class ScheduleStatus(Enum):
    """Schedule status enumeration."""    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"
    PAUSED = "paused"


class Priority(Enum):
    """Schedule priority enumeration."""    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4
    BACKGROUND = 5


@dataclass
class ScheduleCondition:
    """Schedule execution condition."""    type: str  # time, resource, event, custom
    parameters: Dict[str, Any]
    description: str = ""


@dataclass
class ResourceConstraint:
    """Resource constraint for scheduling."""    resource_type: str
    min_available: float
    max_usage: float
    preference: str = "balanced"  # balanced, performance, efficiency


@dataclass
class WorkflowSchedule:
    """Workflow schedule definition."""    id: str
    name: str
    workflow_id: str
    schedule_type: ScheduleType
    priority: Priority
    conditions: List[ScheduleCondition]
    resource_constraints: List[ResourceConstraint]
    timezone: str
    created_by: str
    created_at: datetime
    next_execution: Optional[datetime] = None
    last_execution: Optional[datetime] = None
    execution_count: int = 0
    max_executions: Optional[int] = None
    status: ScheduleStatus = ScheduleStatus.PENDING
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Recurring schedule parameters
    cron_expression: Optional[str] = None
    interval_seconds: Optional[int] = None
    
    # Adaptive parameters
    success_rate_threshold: float = 0.8
    performance_metrics: Dict[str, float] = field(default_factory=dict)


@dataclass
class ScheduleExecution:
    """Schedule execution record."""    id: str
    schedule_id: str
    workflow_id: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    status: str = "running"
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    duration: float = 0.0
    resource_usage: Dict[str, float] = field(default_factory=dict)


class WorkflowScheduler(BaseAgent):
    """    Advanced workflow scheduler for content creator workflows.
    
    This scheduler provides intelligent scheduling capabilities with
    resource optimization, adaptive timing, and complex scheduling patterns.
    """    def __init__(self, max_concurrent_executions: int = 50):
        """Initialize the workflow scheduler."""        super().__init__()
        self.logger = logging.getLogger(__name__)
        
        # Core scheduling components
        self.schedules: Dict[str, WorkflowSchedule] = {}
        self.execution_queue: List[Tuple[datetime, str]] = []  # Priority queue
        self.active_executions: Dict[str, ScheduleExecution] = {}
        self.execution_history: Dict[str, List[ScheduleExecution]] = defaultdict(list)
        
        # Resource management
        self.max_concurrent_executions = max_concurrent_executions
        self.current_resource_usage = defaultdict(float)
        self.resource_locks = defaultdict(asyncio.Lock)
        
        # Scheduling engine
        self.scheduler_running = False
        self.scheduler_task: Optional[asyncio.Task] = None
        self.execution_executor = ThreadPoolExecutor(max_workers=20)
        
        # Adaptive scheduling
        self.schedule_patterns = defaultdict(list)
        self.optimization_history = defaultdict(list)
        
        # Statistics
        self.scheduler_stats = {
            'total_schedules': 0,
            'active_schedules': 0,
            'completed_executions': 0,
            'failed_executions': 0,
            'average_execution_time': 0.0,
            'schedule_accuracy': 0.0
        }

    async def create_schedule(
        self,
        name: str,
        workflow_id: str,
        schedule_type: ScheduleType,
        conditions: List[Dict[str, Any]],
        created_by: str,
        priority: Priority = Priority.MEDIUM,
        timezone: str = "UTC",
        **kwargs
    ) -> str:
        """        Create a new workflow schedule.
        
        Args:
            name: Schedule name
            workflow_id: ID of workflow to schedule
            schedule_type: Type of schedule
            conditions: List of schedule conditions
            created_by: User creating the schedule
            priority: Schedule priority
            timezone: Timezone for schedule
            **kwargs: Additional schedule parameters
            
        Returns:
            str: Schedule ID
        """        try:
            schedule_id = str(uuid.uuid4())
            
            # Parse conditions
            parsed_conditions = []
            for condition in conditions:
                parsed_conditions.append(ScheduleCondition(
                    type=condition['type'],
                    parameters=condition['parameters'],
                    description=condition.get('description', '')
                ))
            
            # Parse resource constraints
            resource_constraints = []
            for constraint in kwargs.get('resource_constraints', []):
                resource_constraints.append(ResourceConstraint(
                    resource_type=constraint['resource_type'],
                    min_available=constraint['min_available'],
                    max_usage=constraint['max_usage'],
                    preference=constraint.get('preference', 'balanced')
                ))
            
            # Create schedule
            schedule = WorkflowSchedule(
                id=schedule_id,
                name=name,
                workflow_id=workflow_id,
                schedule_type=schedule_type,
                priority=priority,
                conditions=parsed_conditions,
                resource_constraints=resource_constraints,
                timezone=timezone,
                created_by=created_by,
                created_at=datetime.now(timezone=pytz.timezone(timezone)),
                cron_expression=kwargs.get('cron_expression'),
                interval_seconds=kwargs.get('interval_seconds'),
                max_executions=kwargs.get('max_executions'),
                metadata=kwargs.get('metadata', {}),
                success_rate_threshold=kwargs.get('success_rate_threshold', 0.8)
            )
            
            # Calculate next execution time
            schedule.next_execution = await self._calculate_next_execution(schedule)
            
            # Store schedule
            self.schedules[schedule_id] = schedule
            
            # Add to execution queue if applicable
            if schedule.next_execution:
                heapq.heappush(self.execution_queue, (schedule.next_execution, schedule_id))
            
            # Update statistics
            self.scheduler_stats['total_schedules'] += 1
            self.scheduler_stats['active_schedules'] += 1
            
            self.logger.info(f"Created schedule: {name} ({schedule_id})")
            return schedule_id
            
        except Exception as e:
            self.logger.error(f"Error creating schedule: {str(e)}")
            raise

    async def start_scheduler(self):
        """Start the workflow scheduler."""        try:
            if self.scheduler_running:
                self.logger.warning("Scheduler is already running")
                return
            
            self.scheduler_running = True
            self.scheduler_task = asyncio.create_task(self._scheduler_loop())
            
            self.logger.info("Workflow scheduler started")
            
        except Exception as e:
            self.logger.error(f"Error starting scheduler: {str(e)}")
            raise

    async def stop_scheduler(self):
        """Stop the workflow scheduler."""        try:
            if not self.scheduler_running:
                self.logger.warning("Scheduler is not running")
                return
            
            self.scheduler_running = False
            
            if self.scheduler_task:
                self.scheduler_task.cancel()
                try:
                    await self.scheduler_task
                except asyncio.CancelledError:
                    pass
            
            self.logger.info("Workflow scheduler stopped")
            
        except Exception as e:
            self.logger.error(f"Error stopping scheduler: {str(e)}")

    async def _scheduler_loop(self):
        """Main scheduler loop."""        try:
            while self.scheduler_running:
                try:
                    # Check for due executions
                    await self._process_due_executions()
                    
                    # Optimize schedules if needed
                    await self._optimize_schedules()
                    
                    # Clean up completed executions
                    await self._cleanup_executions()
                    
                    # Update statistics
                    await self._update_scheduler_stats()
                    
                    # Sleep before next iteration
                    await asyncio.sleep(1)  # Check every second
                    
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    self.logger.error(f"Scheduler loop error: {str(e)}")
                    await asyncio.sleep(5)  # Wait before retrying
                    
        except Exception as e:
            self.logger.error(f"Fatal scheduler error: {str(e)}")
        finally:
            self.scheduler_running = False

    async def _process_due_executions(self):
        """Process workflows that are due for execution."""        try:
            current_time = datetime.now(timezone.utc)
            due_schedules = []
            
            # Find due schedules
            while (self.execution_queue and 
                   self.execution_queue[0][0] <= current_time):
                execution_time, schedule_id = heapq.heappop(self.execution_queue)
                due_schedules.append(schedule_id)
            
            # Process due schedules
            for schedule_id in due_schedules:
                if schedule_id in self.schedules:
                    await self._execute_scheduled_workflow(schedule_id)
                    
        except Exception as e:
            self.logger.error(f"Error processing due executions: {str(e)}")

    async def _execute_scheduled_workflow(self, schedule_id: str):
        """Execute a scheduled workflow."""        try:
            schedule = self.schedules.get(schedule_id)
            if not schedule or schedule.status != ScheduleStatus.ACTIVE:
                return
            
            # Check if we're at max concurrent executions
            if len(self.active_executions) >= self.max_concurrent_executions:
                # Reschedule for later
                next_execution = datetime.now(timezone.utc) + timedelta(minutes=1)
                heapq.heappush(self.execution_queue, (next_execution, schedule_id))
                return
            
            # Check resource constraints
            if not await self._check_resource_constraints(schedule):
                # Reschedule for later
                next_execution = datetime.now(timezone.utc) + timedelta(minutes=5)
                heapq.heappush(self.execution_queue, (next_execution, schedule_id))
                return
            
            # Create execution record
            execution_id = str(uuid.uuid4())
            execution = ScheduleExecution(
                id=execution_id,
                schedule_id=schedule_id,
                workflow_id=schedule.workflow_id,
                started_at=datetime.now(timezone.utc)
            )
            
            # Register active execution
            self.active_executions[execution_id] = execution
            
            # Execute workflow asynchronously
            asyncio.create_task(self._run_workflow_execution(execution, schedule))
            
            # Update schedule
            schedule.last_execution = execution.started_at
            schedule.execution_count += 1
            
            # Schedule next execution if recurring
            if schedule.schedule_type == ScheduleType.RECURRING:
                schedule.next_execution = await self._calculate_next_execution(schedule)
                if schedule.next_execution:
                    heapq.heappush(self.execution_queue, (schedule.next_execution, schedule_id))
            
        except Exception as e:
            self.logger.error(f"Error executing scheduled workflow {schedule_id}: {str(e)}")

    async def _run_workflow_execution(self, execution: ScheduleExecution, schedule: WorkflowSchedule):
        """Run a workflow execution."""        try:
            start_time = datetime.now(timezone.utc)
            
            # Acquire resources
            acquired_resources = await self._acquire_execution_resources(schedule)
            
            try:
                # Execute workflow (placeholder - would integrate with workflow engine)
                result = await self._execute_workflow_instance(
                    schedule.workflow_id,
                    schedule.metadata
                )
                
                # Update execution record
                execution.completed_at = datetime.now(timezone.utc)
                execution.duration = (execution.completed_at - start_time).total_seconds()
                execution.status = "completed" if result.get('success') else "failed"
                execution.result = result
                execution.resource_usage = acquired_resources
                
                # Update schedule performance metrics
                await self._update_schedule_metrics(schedule, execution)
                
                # Log success
                if result.get('success'):
                    self.logger.info(f"Workflow execution completed: {execution.id}")
                    self.scheduler_stats['completed_executions'] += 1
                else:
                    self.logger.error(f"Workflow execution failed: {execution.id}")
                    self.scheduler_stats['failed_executions'] += 1
                
            except Exception as e:
                # Handle execution error
                execution.completed_at = datetime.now(timezone.utc)
                execution.duration = (execution.completed_at - start_time).total_seconds()
                execution.status = "failed"
                execution.error = str(e)
                
                self.logger.error(f"Workflow execution error {execution.id}: {str(e)}")
                self.scheduler_stats['failed_executions'] += 1
                
            finally:
                # Release resources
                await self._release_execution_resources(acquired_resources)
            
        except Exception as e:
            self.logger.error(f"Fatal execution error {execution.id}: {str(e)}")
            execution.status = "failed"
            execution.error = str(e)
        finally:
            # Move to execution history
            self.execution_history[execution.schedule_id].append(execution)
            
            # Remove from active executions
            if execution.id in self.active_executions:
                del self.active_executions[execution.id]

    async def _calculate_next_execution(self, schedule: WorkflowSchedule) -> Optional[datetime]:
        """Calculate next execution time for a schedule."""        try:
            current_time = datetime.now(pytz.timezone(schedule.timezone))
            
            if schedule.schedule_type == ScheduleType.ONE_TIME:
                # Find time-based condition
                for condition in schedule.conditions:
                    if condition.type == 'time':
                        execution_time = datetime.fromisoformat(
                            condition.parameters.get('datetime')
                        )
                        if execution_time > current_time:
                            return execution_time.astimezone(timezone.utc)
                return None
                
            elif schedule.schedule_type == ScheduleType.RECURRING:
                if schedule.cron_expression:
                    # Use cron expression
                    cron = croniter.croniter(schedule.cron_expression, current_time)
                    next_time = cron.get_next(datetime)
                    return next_time.astimezone(timezone.utc)
                    
                elif schedule.interval_seconds:
                    # Use interval
                    if schedule.last_execution:
                        next_time = schedule.last_execution + timedelta(
                            seconds=schedule.interval_seconds
                        )
                    else:
                        next_time = current_time + timedelta(
                            seconds=schedule.interval_seconds
                        )
                    return next_time.astimezone(timezone.utc)
                    
            elif schedule.schedule_type == ScheduleType.ADAPTIVE:
                # Use adaptive scheduling based on performance
                return await self._calculate_adaptive_next_execution(schedule)
                
            return None
            
        except Exception as e:
            self.logger.error(f"Error calculating next execution for {schedule.id}: {str(e)}")
            return None

    async def _calculate_adaptive_next_execution(self, schedule: WorkflowSchedule) -> Optional[datetime]:
        """Calculate next execution time using adaptive scheduling."""        try:
            # Analyze execution history
            executions = self.execution_history.get(schedule.id, [])
            if not executions:
                # Default to 1 hour for first execution
                return datetime.now(timezone.utc) + timedelta(hours=1)
            
            # Calculate success rate
            recent_executions = executions[-10:]  # Last 10 executions
            success_count = sum(1 for ex in recent_executions if ex.status == "completed")
            success_rate = success_count / len(recent_executions)
            
            # Calculate average execution time
            completed_executions = [ex for ex in recent_executions if ex.status == "completed"]
            if completed_executions:
                avg_duration = sum(ex.duration for ex in completed_executions) / len(completed_executions)
            else:
                avg_duration = 300  # Default 5 minutes
            
            # Adjust interval based on performance
            base_interval = schedule.interval_seconds or 3600  # Default 1 hour
            
            if success_rate >= schedule.success_rate_threshold:
                # Good performance - could schedule more frequently
                adjusted_interval = max(base_interval * 0.8, 300)  # Min 5 minutes
            else:
                # Poor performance - schedule less frequently
                adjusted_interval = min(base_interval * 1.5, 86400)  # Max 24 hours
            
            # Consider resource availability trends
            resource_factor = await self._calculate_resource_availability_factor()
            adjusted_interval *= resource_factor
            
            next_execution = datetime.now(timezone.utc) + timedelta(seconds=adjusted_interval)
            return next_execution
            
        except Exception as e:
            self.logger.error(f"Error calculating adaptive execution: {str(e)}")
            return datetime.now(timezone.utc) + timedelta(hours=1)

    async def _check_resource_constraints(self, schedule: WorkflowSchedule) -> bool:
        """Check if resource constraints are satisfied."""        try:
            for constraint in schedule.resource_constraints:
                current_usage = self.current_resource_usage.get(constraint.resource_type, 0.0)
                
                # Check minimum availability
                if current_usage > (100.0 - constraint.min_available):
                    return False
                
                # Check maximum usage
                if current_usage > constraint.max_usage:
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error checking resource constraints: {str(e)}")
            return False

    async def _acquire_execution_resources(self, schedule: WorkflowSchedule) -> Dict[str, float]:
        """Acquire resources for execution."""        try:
            acquired_resources = {}
            
            for constraint in schedule.resource_constraints:
                resource_type = constraint.resource_type
                
                # Estimate resource usage (placeholder - would be more sophisticated)
                estimated_usage = min(constraint.max_usage, 10.0)  # Conservative estimate
                
                async with self.resource_locks[resource_type]:
                    self.current_resource_usage[resource_type] += estimated_usage
                    acquired_resources[resource_type] = estimated_usage
            
            return acquired_resources
            
        except Exception as e:
            self.logger.error(f"Error acquiring resources: {str(e)}")
            return {}

    async def _release_execution_resources(self, acquired_resources: Dict[str, float]):
        """Release execution resources."""        try:
            for resource_type, amount in acquired_resources.items():
                async with self.resource_locks[resource_type]:
                    self.current_resource_usage[resource_type] = max(
                        0.0,
                        self.current_resource_usage[resource_type] - amount
                    )
                    
        except Exception as e:
            self.logger.error(f"Error releasing resources: {str(e)}")

    async def _execute_workflow_instance(
        self,
        workflow_id: str,
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a workflow instance (placeholder)."""        try:
            # Placeholder implementation - would integrate with workflow engine
            await asyncio.sleep(1)  # Simulate execution
            
            # Return success result
            return {
                'success': True,
                'workflow_id': workflow_id,
                'execution_time': 1.0,
                'results': {}
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'workflow_id': workflow_id
            }

    async def _update_schedule_metrics(self, schedule: WorkflowSchedule, execution: ScheduleExecution):
        """Update schedule performance metrics."""        try:
            # Update success rate
            recent_executions = self.execution_history[schedule.id][-10:]
            success_count = sum(1 for ex in recent_executions if ex.status == "completed")
            schedule.performance_metrics['success_rate'] = success_count / len(recent_executions)
            
            # Update average duration
            completed_executions = [ex for ex in recent_executions if ex.status == "completed"]
            if completed_executions:
                avg_duration = sum(ex.duration for ex in completed_executions) / len(completed_executions)
                schedule.performance_metrics['avg_duration'] = avg_duration
            
            # Update resource efficiency
            if execution.resource_usage:
                total_resources = sum(execution.resource_usage.values())
                if total_resources > 0:
                    efficiency = execution.duration / total_resources
                    schedule.performance_metrics['resource_efficiency'] = efficiency
                    
        except Exception as e:
            self.logger.error(f"Error updating schedule metrics: {str(e)}")

    async def _optimize_schedules(self):
        """Optimize schedules based on performance data."""        try:
            # Run optimization every 10 minutes
            if hasattr(self, '_last_optimization'):
                if (datetime.now() - self._last_optimization).total_seconds() < 600:
                    return
            
            self._last_optimization = datetime.now()
            
            # Analyze schedule performance
            for schedule_id, schedule in self.schedules.items():
                if schedule.schedule_type == ScheduleType.ADAPTIVE:
                    await self._optimize_adaptive_schedule(schedule)
                    
        except Exception as e:
            self.logger.error(f"Error optimizing schedules: {str(e)}")

    async def _optimize_adaptive_schedule(self, schedule: WorkflowSchedule):
        """Optimize an adaptive schedule based on performance."""        try:
            executions = self.execution_history.get(schedule.id, [])
            if len(executions) < 5:  # Need sufficient data
                return
            
            # Analyze performance trends
            recent_executions = executions[-20:]  # Last 20 executions
            
            # Calculate performance score
            success_rate = sum(1 for ex in recent_executions 
                             if ex.status == "completed") / len(recent_executions)
            
            avg_duration = sum(ex.duration for ex in recent_executions 
                             if ex.status == "completed") / max(1, sum(1 for ex in recent_executions 
                                                                     if ex.status == "completed"))
            
            # Adjust schedule parameters based on performance
            if success_rate < schedule.success_rate_threshold:
                # Increase interval to reduce load
                if schedule.interval_seconds:
                    schedule.interval_seconds = min(schedule.interval_seconds * 1.2, 86400)
            elif success_rate > 0.95 and avg_duration < 60:  # Excellent performance
                # Decrease interval for more frequent execution
                if schedule.interval_seconds:
                    schedule.interval_seconds = max(schedule.interval_seconds * 0.9, 300)
                    
        except Exception as e:
            self.logger.error(f"Error optimizing adaptive schedule {schedule.id}: {str(e)}")

    async def _cleanup_executions(self):
        """Clean up old execution records."""        try:
            # Clean up every hour
            if hasattr(self, '_last_cleanup'):
                if (datetime.now() - self._last_cleanup).total_seconds() < 3600:
                    return
            
            self._last_cleanup = datetime.now()
            
            # Keep last 100 executions per schedule
            for schedule_id, executions in self.execution_history.items():
                if len(executions) > 100:
                    self.execution_history[schedule_id] = executions[-100:]
                    
        except Exception as e:
            self.logger.error(f"Error cleaning up executions: {str(e)}")

    async def _update_scheduler_stats(self):
        """Update scheduler statistics."""        try:
            # Update every 5 minutes
            if hasattr(self, '_last_stats_update'):
                if (datetime.now() - self._last_stats_update).total_seconds() < 300:
                    return
            
            self._last_stats_update = datetime.now()
            
            # Count active schedules
            active_count = sum(1 for schedule in self.schedules.values() 
                             if schedule.status == ScheduleStatus.ACTIVE)
            self.scheduler_stats['active_schedules'] = active_count
            
            # Calculate average execution time
            all_executions = []
            for executions in self.execution_history.values():
                all_executions.extend(executions)
            
            if all_executions:
                completed_executions = [ex for ex in all_executions if ex.status == "completed"]
                if completed_executions:
                    avg_time = sum(ex.duration for ex in completed_executions) / len(completed_executions)
                    self.scheduler_stats['average_execution_time'] = avg_time
                    
        except Exception as e:
            self.logger.error(f"Error updating scheduler stats: {str(e)}")

    async def _calculate_resource_availability_factor(self) -> float:
        """Calculate resource availability factor for adaptive scheduling."""        try:
            # Calculate average resource usage
            if not self.current_resource_usage:
                return 1.0
            
            avg_usage = sum(self.current_resource_usage.values()) / len(self.current_resource_usage)
            
            # Convert to factor (higher usage = higher factor = longer intervals)
            if avg_usage < 20:
                return 0.8  # Low usage - can schedule more frequently
            elif avg_usage < 50:
                return 1.0  # Medium usage - normal scheduling
            elif avg_usage < 80:
                return 1.5  # High usage - schedule less frequently
            else:
                return 2.0  # Very high usage - much less frequent scheduling
                
        except Exception as e:
            self.logger.error(f"Error calculating resource factor: {str(e)}")
            return 1.0

    async def get_schedule(self, schedule_id: str) -> Optional[Dict[str, Any]]:
        """Get schedule by ID."""        try:
            schedule = self.schedules.get(schedule_id)
            if not schedule:
                return None
            
            # Get execution history
            executions = self.execution_history.get(schedule_id, [])
            recent_executions = executions[-10:] if executions else []
            
            return {
                'id': schedule.id,
                'name': schedule.name,
                'workflow_id': schedule.workflow_id,
                'schedule_type': schedule.schedule_type.value,
                'priority': schedule.priority.value,
                'status': schedule.status.value,
                'timezone': schedule.timezone,
                'created_by': schedule.created_by,
                'created_at': schedule.created_at.isoformat(),
                'next_execution': schedule.next_execution.isoformat() if schedule.next_execution else None,
                'last_execution': schedule.last_execution.isoformat() if schedule.last_execution else None,
                'execution_count': schedule.execution_count,
                'max_executions': schedule.max_executions,
                'performance_metrics': schedule.performance_metrics,
                'recent_executions': [
                    {
                        'id': ex.id,
                        'started_at': ex.started_at.isoformat(),
                        'completed_at': ex.completed_at.isoformat() if ex.completed_at else None,
                        'status': ex.status,
                        'duration': ex.duration
                    }
                    for ex in recent_executions
                ]
            }
            
        except Exception as e:
            self.logger.error(f"Error getting schedule {schedule_id}: {str(e)}")
            return None

    async def list_schedules(
        self,
        status: Optional[ScheduleStatus] = None,
        created_by: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """List schedules with optional filtering."""        try:
            schedules = []
            
            for schedule in self.schedules.values():
                # Apply filters
                if status and schedule.status != status:
                    continue
                
                if created_by and schedule.created_by != created_by:
                    continue
                
                # Add to results
                schedule_info = await self.get_schedule(schedule.id)
                if schedule_info:
                    schedules.append(schedule_info)
            
            # Sort by next execution time
            schedules.sort(key=lambda s: s.get('next_execution') or '9999-12-31T23:59:59')
            
            return schedules
            
        except Exception as e:
            self.logger.error(f"Error listing schedules: {str(e)}")
            return []

    async def update_schedule(
        self,
        schedule_id: str,
        updates: Dict[str, Any]
    ) -> bool:
        """Update a schedule."""        try:
            schedule = self.schedules.get(schedule_id)
            if not schedule:
                return False
            
            # Update allowed fields
            if 'name' in updates:
                schedule.name = updates['name']
            
            if 'priority' in updates:
                schedule.priority = Priority(updates['priority'])
            
            if 'status' in updates:
                schedule.status = ScheduleStatus(updates['status'])
            
            if 'cron_expression' in updates:
                schedule.cron_expression = updates['cron_expression']
                # Recalculate next execution
                schedule.next_execution = await self._calculate_next_execution(schedule)
            
            if 'interval_seconds' in updates:
                schedule.interval_seconds = updates['interval_seconds']
                # Recalculate next execution
                schedule.next_execution = await self._calculate_next_execution(schedule)
            
            self.logger.info(f"Updated schedule: {schedule_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating schedule {schedule_id}: {str(e)}")
            return False

    async def delete_schedule(self, schedule_id: str) -> bool:
        """Delete a schedule."""        try:
            if schedule_id not in self.schedules:
                return False
            
            # Remove from schedules
            del self.schedules[schedule_id]
            
            # Remove from execution queue
            self.execution_queue = [
                (time, sid) for time, sid in self.execution_queue 
                if sid != schedule_id
            ]
            heapq.heapify(self.execution_queue)
            
            # Keep execution history for analytics
            
            self.logger.info(f"Deleted schedule: {schedule_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error deleting schedule {schedule_id}: {str(e)}")
            return False

    async def get_scheduler_stats(self) -> Dict[str, Any]:
        """Get scheduler statistics."""        return {
            'stats': self.scheduler_stats.copy(),
            'active_executions': len(self.active_executions),
            'queue_size': len(self.execution_queue),
            'resource_usage': self.current_resource_usage.copy(),
            'scheduler_running': self.scheduler_running
        }
