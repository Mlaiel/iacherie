"""
Enterprise Deployment Scheduler for MLOps
DevOps + Backend Senior implementation with intelligent deployment scheduling
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Callable, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
import json
import cron_descriptor
from croniter import croniter
import uuid
import heapq
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)


class DeploymentStrategy(Enum):
    """Deployment strategy types"""
    BLUE_GREEN = "blue_green"
    CANARY = "canary"
    ROLLING = "rolling"
    RECREATE = "recreate"
    A_B_TEST = "a_b_test"
    SHADOW = "shadow"


class DeploymentPriority(Enum):
    """Deployment priority levels"""
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4
    MAINTENANCE = 5


class DeploymentStatus(Enum):
    """Deployment task status"""
    SCHEDULED = "scheduled"
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    ROLLBACK = "rollback"
    PAUSED = "paused"


class Environment(Enum):
    """Deployment environments"""
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"
    DISASTER_RECOVERY = "disaster_recovery"


@dataclass
class DeploymentWindow:
    """Deployment time window configuration"""
    start_time: str  # HH:MM format
    end_time: str  # HH:MM format
    timezone: str = "UTC"
    days_of_week: List[int] = field(default_factory=lambda: list(range(7)))  # 0=Monday
    blackout_dates: List[str] = field(default_factory=list)  # YYYY-MM-DD format
    maintenance_windows: List[Tuple[str, str]] = field(default_factory=list)  # (start, end) datetime ISO


@dataclass
class ResourceRequirements:
    """Resource requirements for deployment"""
    cpu_cores: float = 1.0
    memory_mb: int = 512
    gpu_count: int = 0
    storage_gb: int = 10
    network_bandwidth_mbps: int = 100
    estimated_duration_minutes: int = 15


@dataclass
class DeploymentTask:
    """Deployment task definition"""
    task_id: str
    model_id: str
    version: str
    environment: Environment
    strategy: DeploymentStrategy
    priority: DeploymentPriority
    scheduled_time: datetime
    deployment_window: Optional[DeploymentWindow] = None
    resource_requirements: ResourceRequirements = field(default_factory=ResourceRequirements)
    dependencies: List[str] = field(default_factory=list)  # Other task IDs
    rollback_enabled: bool = True
    approval_required: bool = False
    approved_by: Optional[str] = None
    approval_timestamp: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_timestamp: datetime = field(default_factory=datetime.now)
    status: DeploymentStatus = DeploymentStatus.SCHEDULED
    retry_count: int = 0
    max_retries: int = 3
    error_message: Optional[str] = None
    execution_log: List[str] = field(default_factory=list)


@dataclass
class SchedulerConfig:
    """Deployment scheduler configuration"""
    max_concurrent_deployments: int = 5
    max_concurrent_per_environment: Dict[Environment, int] = field(default_factory=lambda: {
        Environment.DEVELOPMENT: 10,
        Environment.TESTING: 5,
        Environment.STAGING: 3,
        Environment.PRODUCTION: 1
    })
    default_deployment_window: Optional[DeploymentWindow] = None
    auto_approval_environments: List[Environment] = field(default_factory=lambda: [
        Environment.DEVELOPMENT, Environment.TESTING
    ])
    enable_smart_scheduling: bool = True
    resource_optimization_enabled: bool = True
    conflict_resolution_strategy: str = "priority_based"  # priority_based, fifo, resource_optimal
    monitoring_interval_seconds: int = 30


class ResourceManager:
    """Manages deployment resource allocation"""
    
    def __init__(self) -> None:
        self.allocated_resources = {}
        self.resource_lock = asyncio.Lock()
    
    async def check_resource_availability(self, requirements: ResourceRequirements,
                                        environment: Environment) -> bool:
        """Check if resources are available for deployment"""
        async with self.resource_lock:
            env_resources = self.allocated_resources.get(environment.value, {
                'cpu_cores': 0,
                'memory_mb': 0,
                'gpu_count': 0,
                'storage_gb': 0
            })
            
            # Define environment limits (would come from configuration)
            env_limits = {
                Environment.DEVELOPMENT: {'cpu_cores': 32, 'memory_mb': 32768, 'gpu_count': 4, 'storage_gb': 1000},
                Environment.TESTING: {'cpu_cores': 16, 'memory_mb': 16384, 'gpu_count': 2, 'storage_gb': 500},
                Environment.STAGING: {'cpu_cores': 8, 'memory_mb': 8192, 'gpu_count': 1, 'storage_gb': 250},
                Environment.PRODUCTION: {'cpu_cores': 64, 'memory_mb': 65536, 'gpu_count': 8, 'storage_gb': 2000}
            }
            
            limits = env_limits.get(environment, env_limits[Environment.DEVELOPMENT])
            
            return (
                env_resources['cpu_cores'] + requirements.cpu_cores <= limits['cpu_cores'] and
                env_resources['memory_mb'] + requirements.memory_mb <= limits['memory_mb'] and
                env_resources['gpu_count'] + requirements.gpu_count <= limits['gpu_count'] and
                env_resources['storage_gb'] + requirements.storage_gb <= limits['storage_gb']
            )
    
    async def allocate_resources(self, task_id: str, requirements: ResourceRequirements,
                               environment: Environment) -> bool:
        """Allocate resources for deployment"""
        async with self.resource_lock:
            if await self.check_resource_availability(requirements, environment):
                if environment.value not in self.allocated_resources:
                    self.allocated_resources[environment.value] = {
                        'cpu_cores': 0, 'memory_mb': 0, 'gpu_count': 0, 'storage_gb': 0, 'tasks': {}
                    }
                
                env_resources = self.allocated_resources[environment.value]
                env_resources['cpu_cores'] += requirements.cpu_cores
                env_resources['memory_mb'] += requirements.memory_mb
                env_resources['gpu_count'] += requirements.gpu_count
                env_resources['storage_gb'] += requirements.storage_gb
                env_resources['tasks'][task_id] = requirements
                
                return True
            return False
    
    async def release_resources(self, task_id -> None: str, environment -> None: Environment) -> None:
        """Release allocated resources"""
        async with self.resource_lock:
            if environment.value in self.allocated_resources:
                env_resources = self.allocated_resources[environment.value]
                if task_id in env_resources['tasks']:
                    requirements = env_resources['tasks'][task_id]
                    env_resources['cpu_cores'] -= requirements.cpu_cores
                    env_resources['memory_mb'] -= requirements.memory_mb
                    env_resources['gpu_count'] -= requirements.gpu_count
                    env_resources['storage_gb'] -= requirements.storage_gb
                    del env_resources['tasks'][task_id]


class DeploymentWindowManager:
    """Manages deployment windows and scheduling constraints"""
    
    def is_deployment_allowed(self, deployment_time: datetime, 
                            window: Optional[DeploymentWindow]) -> bool:
        """Check if deployment is allowed at specified time"""
        if not window:
            return True
        
        # Convert to target timezone
        target_tz = timezone.utc if window.timezone == "UTC" else timezone.utc  # Simplified
        deployment_time = deployment_time.replace(tzinfo=target_tz)
        
        # Check day of week
        if deployment_time.weekday() not in window.days_of_week:
            return False
        
        # Check time window
        start_time = datetime.strptime(window.start_time, "%H:%M").time()
        end_time = datetime.strptime(window.end_time, "%H:%M").time()
        
        deployment_time_only = deployment_time.time()
        
        if start_time <= end_time:
            # Same day window
            if not (start_time <= deployment_time_only <= end_time):
                return False
        else:
            # Cross-midnight window
            if not (deployment_time_only >= start_time or deployment_time_only <= end_time):
                return False
        
        # Check blackout dates
        deployment_date = deployment_time.date().isoformat()
        if deployment_date in window.blackout_dates:
            return False
        
        # Check maintenance windows
        for maint_start, maint_end in window.maintenance_windows:
            maint_start_dt = datetime.fromisoformat(maint_start)
            maint_end_dt = datetime.fromisoformat(maint_end)
            if maint_start_dt <= deployment_time <= maint_end_dt:
                return False
        
        return True
    
    def find_next_available_slot(self, preferred_time: datetime,
                                window: Optional[DeploymentWindow],
                                max_delay_hours: int = 24) -> Optional[datetime]:
        """Find next available deployment slot"""
        if not window:
            return preferred_time
        
        current_time = preferred_time
        end_search_time = preferred_time + timedelta(hours=max_delay_hours)
        
        while current_time <= end_search_time:
            if self.is_deployment_allowed(current_time, window):
                return current_time
            current_time += timedelta(minutes=15)  # Check every 15 minutes
        
        return None


class SmartScheduler:
    """Intelligent deployment scheduling logic"""
    
    def __init__(self, config -> None: SchedulerConfig) -> None:
        self.config = config
    
    def optimize_schedule(self, tasks: List[DeploymentTask]) -> List[DeploymentTask]:
        """Optimize deployment schedule using intelligent algorithms"""
        if not self.config.enable_smart_scheduling:
            return sorted(tasks, key=lambda t: (t.priority.value, t.scheduled_time))
        
        # Group by environment to respect concurrency limits
        env_tasks = {}
        for task in tasks:
            if task.environment not in env_tasks:
                env_tasks[task.environment] = []
            env_tasks[task.environment].append(task)
        
        optimized_tasks = []
        
        for environment, env_task_list in env_tasks.items():
            # Sort by priority first, then by dependencies
            sorted_tasks = self._resolve_dependencies(env_task_list)
            
            if self.config.resource_optimization_enabled:
                sorted_tasks = self._optimize_resource_usage(sorted_tasks)
            
            optimized_tasks.extend(sorted_tasks)
        
        return optimized_tasks
    
    def _resolve_dependencies(self, tasks: List[DeploymentTask]) -> List[DeploymentTask]:
        """Resolve task dependencies using topological sort"""
        # Create dependency graph
        task_map = {task.task_id: task for task in tasks}
        in_degree = {task.task_id: 0 for task in tasks}
        
        # Calculate in-degrees
        for task in tasks:
            for dep_id in task.dependencies:
                if dep_id in in_degree:
                    in_degree[task.task_id] += 1
        
        # Topological sort with priority consideration
        queue = [(task.priority.value, task.scheduled_time, task.task_id) 
                for task in tasks if in_degree[task.task_id] == 0]
        heapq.heapify(queue)
        
        sorted_tasks = []
        
        while queue:
            _, _, task_id = heapq.heappop(queue)
            task = task_map[task_id]
            sorted_tasks.append(task)
            
            # Update dependencies
            for other_task in tasks:
                if task_id in other_task.dependencies:
                    in_degree[other_task.task_id] -= 1
                    if in_degree[other_task.task_id] == 0:
                        heapq.heappush(queue, (
                            other_task.priority.value,
                            other_task.scheduled_time,
                            other_task.task_id
                        ))
        
        return sorted_tasks
    
    def _optimize_resource_usage(self, tasks: List[DeploymentTask]) -> List[DeploymentTask]:
        """Optimize resource usage across deployments"""
        # Simple bin packing optimization for resource utilization
        # In a production system, this would use more sophisticated algorithms
        
        # Group tasks by similar resource requirements
        resource_groups = {}
        
        for task in tasks:
            resource_key = (
                task.resource_requirements.cpu_cores,
                task.resource_requirements.memory_mb,
                task.resource_requirements.gpu_count
            )
            
            if resource_key not in resource_groups:
                resource_groups[resource_key] = []
            resource_groups[resource_key].append(task)
        
        # Schedule resource groups to minimize fragmentation
        optimized_tasks = []
        for group in sorted(resource_groups.values(), key=lambda g: -len(g)):
            optimized_tasks.extend(sorted(group, key=lambda t: (t.priority.value, t.scheduled_time)))
        
        return optimized_tasks


class DeploymentScheduler:
    """Main deployment scheduler with enterprise features"""
    
    def __init__(self, config -> None: SchedulerConfig) -> None:
        self.config = config
        self.task_queue = []
        self.running_tasks = {}
        self.completed_tasks = {}
        self.resource_manager = ResourceManager()
        self.window_manager = DeploymentWindowManager()
        self.smart_scheduler = SmartScheduler(config)
        self.scheduler_lock = asyncio.Lock()
        self.is_running = False
        self.executor = ThreadPoolExecutor(max_workers=config.max_concurrent_deployments)
    
    async def schedule_deployment(self, task: DeploymentTask) -> str:
        """Schedule a new deployment task"""
        async with self.scheduler_lock:
            # Validate deployment window
            if task.deployment_window:
                if not self.window_manager.is_deployment_allowed(
                    task.scheduled_time, task.deployment_window
                ):
                    # Find next available slot
                    next_slot = self.window_manager.find_next_available_slot(
                        task.scheduled_time, task.deployment_window
                    )
                    if next_slot:
                        task.scheduled_time = next_slot
                        task.execution_log.append(
                            f"Rescheduled from {task.scheduled_time} to {next_slot} due to deployment window"
                        )
                    else:
                        raise ValueError("No available deployment slot within allowed window")
            
            # Check for approval requirements
            if task.approval_required and not task.approved_by:
                if task.environment not in self.config.auto_approval_environments:
                    task.status = DeploymentStatus.PENDING
                    task.execution_log.append("Waiting for approval")
                else:
                    task.approved_by = "auto_approval"
                    task.approval_timestamp = datetime.now()
            
            # Add to queue
            heapq.heappush(self.task_queue, (
                task.priority.value,
                task.scheduled_time.timestamp(),
                task.task_id,
                task
            ))
            
            logger.info(f"Scheduled deployment task {task.task_id} for {task.scheduled_time}")
            return task.task_id
    
    async def approve_deployment(self, task_id: str, approver: str) -> bool:
        """Approve a pending deployment"""
        async with self.scheduler_lock:
            # Find task in queue
            for i, (priority, timestamp, tid, task) in enumerate(self.task_queue):
                if tid == task_id:
                    if task.status == DeploymentStatus.PENDING:
                        task.approved_by = approver
                        task.approval_timestamp = datetime.now()
                        task.status = DeploymentStatus.SCHEDULED
                        task.execution_log.append(f"Approved by {approver}")
                        logger.info(f"Deployment {task_id} approved by {approver}")
                        return True
                    else:
                        logger.warning(f"Task {task_id} is not in pending state")
                        return False
            
            logger.warning(f"Task {task_id} not found")
            return False
    
    async def cancel_deployment(self, task_id: str, reason: str = "") -> bool:
        """Cancel a scheduled deployment"""
        async with self.scheduler_lock:
            # Remove from queue
            new_queue = []
            cancelled = False
            
            for priority, timestamp, tid, task in self.task_queue:
                if tid == task_id:
                    task.status = DeploymentStatus.CANCELLED
                    task.error_message = f"Cancelled: {reason}"
                    task.execution_log.append(f"Cancelled: {reason}")
                    self.completed_tasks[task_id] = task
                    cancelled = True
                    logger.info(f"Cancelled deployment {task_id}: {reason}")
                else:
                    new_queue.append((priority, timestamp, tid, task))
            
            self.task_queue = new_queue
            heapq.heapify(self.task_queue)
            
            # Check if currently running
            if task_id in self.running_tasks:
                running_task = self.running_tasks[task_id]
                running_task.status = DeploymentStatus.CANCELLED
                running_task.error_message = f"Cancelled: {reason}"
                running_task.execution_log.append(f"Cancelled during execution: {reason}")
                # Note: In production, would need to actually stop the deployment process
                cancelled = True
            
            return cancelled
    
    async def start_scheduler(self) -> None:
        """Start the deployment scheduler main loop"""
        if self.is_running:
            logger.warning("Scheduler is already running")
            return
        
        self.is_running = True
        logger.info("Starting deployment scheduler")
        
        while self.is_running:
            try:
                await self._process_pending_deployments()
                await self._check_running_deployments()
                await asyncio.sleep(self.config.monitoring_interval_seconds)
            except Exception as e:
                logger.error(f"Scheduler error: {e}")
                await asyncio.sleep(5)  # Brief pause before retry
    
    async def stop_scheduler(self) -> None:
        """Stop the deployment scheduler"""
        self.is_running = False
        logger.info("Stopping deployment scheduler")
        
        # Wait for running deployments to complete or cancel them
        if self.running_tasks:
            logger.info(f"Waiting for {len(self.running_tasks)} running deployments to complete")
            await asyncio.sleep(10)  # Give time for graceful shutdown
    
    async def _process_pending_deployments(self) -> None:
        """Process pending deployments from the queue"""
        async with self.scheduler_lock:
            current_time = datetime.now()
            ready_tasks = []
            
            # Find tasks ready for execution
            temp_queue = []
            while self.task_queue:
                priority, timestamp, task_id, task = heapq.heappop(self.task_queue)
                
                if task.scheduled_time <= current_time and task.status == DeploymentStatus.SCHEDULED:
                    if await self._can_execute_task(task):
                        ready_tasks.append(task)
                    else:
                        # Put back in queue with slight delay
                        task.scheduled_time = current_time + timedelta(minutes=1)
                        heapq.heappush(temp_queue, (priority, task.scheduled_time.timestamp(), task_id, task))
                else:
                    heapq.heappush(temp_queue, (priority, timestamp, task_id, task))
            
            # Restore queue
            self.task_queue = temp_queue
            heapq.heapify(self.task_queue)
            
            # Optimize and execute ready tasks
            if ready_tasks:
                optimized_tasks = self.smart_scheduler.optimize_schedule(ready_tasks)
                
                for task in optimized_tasks:
                    if len(self.running_tasks) < self.config.max_concurrent_deployments:
                        await self._execute_deployment(task)
                    else:
                        # Put back in queue
                        heapq.heappush(self.task_queue, (
                            task.priority.value,
                            task.scheduled_time.timestamp(),
                            task.task_id,
                            task
                        ))
                        break
    
    async def _can_execute_task(self, task: DeploymentTask) -> bool:
        """Check if task can be executed now"""
        # Check approval
        if task.approval_required and not task.approved_by:
            return False
        
        # Check environment concurrency limits
        env_limit = self.config.max_concurrent_per_environment.get(
            task.environment, self.config.max_concurrent_deployments
        )
        
        env_running_count = sum(
            1 for t in self.running_tasks.values()
            if t.environment == task.environment
        )
        
        if env_running_count >= env_limit:
            return False
        
        # Check resource availability
        if not await self.resource_manager.check_resource_availability(
            task.resource_requirements, task.environment
        ):
            return False
        
        # Check dependencies
        for dep_id in task.dependencies:
            if dep_id not in self.completed_tasks:
                return False
            if self.completed_tasks[dep_id].status != DeploymentStatus.COMPLETED:
                return False
        
        return True
    
    async def _execute_deployment(self, task -> None: DeploymentTask) -> None:
        """Execute a deployment task"""
        try:
            # Allocate resources
            if not await self.resource_manager.allocate_resources(
                task.task_id, task.resource_requirements, task.environment
            ):
                logger.warning(f"Failed to allocate resources for task {task.task_id}")
                return
            
            task.status = DeploymentStatus.RUNNING
            task.execution_log.append(f"Started execution at {datetime.now()}")
            self.running_tasks[task.task_id] = task
            
            logger.info(f"Starting deployment {task.task_id} for model {task.model_id} v{task.version}")
            
            # Submit to thread pool for execution
            future = self.executor.submit(self._run_deployment_process, task)
            
            # Store future reference (in production, would track this better)
            task.metadata['execution_future'] = future
            
        except Exception as e:
            logger.error(f"Failed to start deployment {task.task_id}: {e}")
            task.status = DeploymentStatus.FAILED
            task.error_message = str(e)
            task.execution_log.append(f"Failed to start: {e}")
            await self.resource_manager.release_resources(task.task_id, task.environment)
            self.completed_tasks[task.task_id] = task
    
    def _run_deployment_process(self, task: DeploymentTask) -> Dict[str, Any]:
        """Run the actual deployment process (would interface with deployment systems)"""
        try:
            # Simulate deployment process
            import time
            
            task.execution_log.append("Preparing deployment environment")
            time.sleep(2)  # Simulate preparation
            
            task.execution_log.append(f"Deploying model {task.model_id} v{task.version}")
            time.sleep(task.resource_requirements.estimated_duration_minutes * 0.1)  # Simulate deployment
            
            task.execution_log.append("Running health checks")
            time.sleep(1)  # Simulate health checks
            
            task.execution_log.append("Deployment completed successfully")
            
            return {
                "status": "success",
                "deployment_id": f"deploy-{task.task_id}",
                "endpoints": [f"https://{task.environment.value}.example.com/models/{task.model_id}"],
                "completion_time": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "failed",
                "error": str(e),
                "completion_time": datetime.now().isoformat()
            }
    
    async def _check_running_deployments(self) -> None:
        """Check status of running deployments"""
        completed_task_ids = []
        
        for task_id, task in self.running_tasks.items():
            future = task.metadata.get('execution_future')
            if future and future.done():
                try:
                    result = future.result()
                    
                    if result['status'] == 'success':
                        task.status = DeploymentStatus.COMPLETED
                        task.execution_log.append("Deployment completed successfully")
                        task.metadata.update(result)
                    else:
                        task.status = DeploymentStatus.FAILED
                        task.error_message = result.get('error', 'Unknown error')
                        task.execution_log.append(f"Deployment failed: {task.error_message}")
                    
                    completed_task_ids.append(task_id)
                    
                except Exception as e:
                    task.status = DeploymentStatus.FAILED
                    task.error_message = str(e)
                    task.execution_log.append(f"Execution error: {e}")
                    completed_task_ids.append(task_id)
                
                finally:
                    # Release resources
                    await self.resource_manager.release_resources(task_id, task.environment)
        
        # Move completed tasks
        for task_id in completed_task_ids:
            task = self.running_tasks.pop(task_id)
            self.completed_tasks[task_id] = task
            
            logger.info(f"Deployment {task_id} completed with status: {task.status}")
            
            # Handle retries for failed tasks
            if task.status == DeploymentStatus.FAILED and task.retry_count < task.max_retries:
                task.retry_count += 1
                task.status = DeploymentStatus.SCHEDULED
                task.scheduled_time = datetime.now() + timedelta(minutes=5 * task.retry_count)
                task.execution_log.append(f"Scheduling retry {task.retry_count}/{task.max_retries}")
                
                # Add back to queue
                heapq.heappush(self.task_queue, (
                    task.priority.value,
                    task.scheduled_time.timestamp(),
                    task.task_id,
                    task
                ))
    
    def get_deployment_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a deployment task"""
        # Check running tasks
        if task_id in self.running_tasks:
            task = self.running_tasks[task_id]
            return self._task_to_dict(task)
        
        # Check completed tasks
        if task_id in self.completed_tasks:
            task = self.completed_tasks[task_id]
            return self._task_to_dict(task)
        
        # Check queue
        for _, _, tid, task in self.task_queue:
            if tid == task_id:
                return self._task_to_dict(task)
        
        return None
    
    def _task_to_dict(self, task: DeploymentTask) -> Dict[str, Any]:
        """Convert task to dictionary representation"""
        return {
            "task_id": task.task_id,
            "model_id": task.model_id,
            "version": task.version,
            "environment": task.environment.value,
            "strategy": task.strategy.value,
            "priority": task.priority.value,
            "status": task.status.value,
            "scheduled_time": task.scheduled_time.isoformat(),
            "created_timestamp": task.created_timestamp.isoformat(),
            "approval_required": task.approval_required,
            "approved_by": task.approved_by,
            "approval_timestamp": task.approval_timestamp.isoformat() if task.approval_timestamp else None,
            "retry_count": task.retry_count,
            "max_retries": task.max_retries,
            "error_message": task.error_message,
            "execution_log": task.execution_log,
            "metadata": task.metadata
        }
    
    def get_scheduler_stats(self) -> Dict[str, Any]:
        """Get scheduler statistics"""
        return {
            "running_deployments": len(self.running_tasks),
            "queued_deployments": len(self.task_queue),
            "completed_deployments": len(self.completed_tasks),
            "is_running": self.is_running,
            "resource_allocation": self.resource_manager.allocated_resources,
            "deployment_stats": {
                "by_status": self._count_by_status(),
                "by_environment": self._count_by_environment(),
                "by_priority": self._count_by_priority()
            }
        }
    
    def _count_by_status(self) -> Dict[str, int]:
        """Count tasks by status"""
        counts = {status.value: 0 for status in DeploymentStatus}
        
        for task in self.running_tasks.values():
            counts[task.status.value] += 1
        
        for task in self.completed_tasks.values():
            counts[task.status.value] += 1
        
        for _, _, _, task in self.task_queue:
            counts[task.status.value] += 1
        
        return counts
    
    def _count_by_environment(self) -> Dict[str, int]:
        """Count tasks by environment"""
        counts = {env.value: 0 for env in Environment}
        
        for task in self.running_tasks.values():
            counts[task.environment.value] += 1
        
        for _, _, _, task in self.task_queue:
            counts[task.environment.value] += 1
        
        return counts
    
    def _count_by_priority(self) -> Dict[str, int]:
        """Count tasks by priority"""
        counts = {priority.name: 0 for priority in DeploymentPriority}
        
        for task in self.running_tasks.values():
            counts[task.priority.name] += 1
        
        for _, _, _, task in self.task_queue:
            counts[task.priority.name] += 1
        
        return counts


# Factory function
def create_deployment_scheduler(
    max_concurrent_deployments: int = 5,
    enable_smart_scheduling: bool = True,
    resource_optimization: bool = True
) -> DeploymentScheduler:
    """Create a configured deployment scheduler"""
    
    config = SchedulerConfig(
        max_concurrent_deployments=max_concurrent_deployments,
        enable_smart_scheduling=enable_smart_scheduling,
        resource_optimization_enabled=resource_optimization
    )
    
    return DeploymentScheduler(config)


# Export main classes
__all__ = [
    "DeploymentScheduler",
    "DeploymentTask",
    "DeploymentStrategy",
    "DeploymentPriority",
    "DeploymentStatus",
    "Environment",
    "DeploymentWindow",
    "ResourceRequirements",
    "SchedulerConfig",
    "create_deployment_scheduler"
]