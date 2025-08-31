"""Task Manager

Advanced task management system for coordinating and prioritizing tasks across
multiple AI agents with intelligent scheduling and resource optimization.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  LEGAL WARNING ⚠️
This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use is strictly prohibited.
"""
import asyncio
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, Any, Set, Callable
from dataclasses import dataclass, field, asdict
from enum import Enum
import logging
from heapq import heappush, heappop

logger = logging.getLogger(__name__)


class TaskPriority(Enum):
    """Task priority levels"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    URGENT = 4
    CRITICAL = 5


class TaskStatus(Enum):
    """Task execution status"""
    PENDING = "pending"
    QUEUED = "queued"
    ASSIGNED = "assigned"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"
    RETRY = "retry"


class TaskType(Enum):
    """Categories of tasks"""
    CONTENT_CREATION = "content_creation"
    CONTENT_ANALYSIS = "content_analysis"
    SOCIAL_MEDIA = "social_media"
    ENGAGEMENT = "engagement"
    ANALYTICS = "analytics"
    AUDIO_PROCESSING = "audio_processing"
    VIDEO_PROCESSING = "video_processing"
    IMAGE_PROCESSING = "image_processing"
    WORKFLOW = "workflow"
    MONITORING = "monitoring"
    OPTIMIZATION = "optimization"


@dataclass
class Task:
    """Individual task definition"""
    task_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    task_type: TaskType = TaskType.CONTENT_CREATION
    priority: TaskPriority = TaskPriority.MEDIUM
    status: TaskStatus = TaskStatus.PENDING
    
    # Task definition
    name: str = ""
    description: str = ""
    agent_requirements: Set[str] = field(default_factory=set)  # Required capabilities
    preferred_agents: List[str] = field(default_factory=list)  # Agent IDs
    context: Dict[str, Any] = field(default_factory=dict)
    
    # Scheduling
    created_at: datetime = field(default_factory=datetime.utcnow)
    scheduled_at: Optional[datetime] = None
    deadline: Optional[datetime] = None
    estimated_duration: Optional[timedelta] = None
    
    # Dependencies and relationships
    depends_on: List[str] = field(default_factory=list)  # Task IDs
    blocks: List[str] = field(default_factory=list)  # Task IDs this blocks
    parent_task: Optional[str] = None
    subtasks: List[str] = field(default_factory=list)
    
    # Execution
    assigned_agent: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    
    # Retry and recovery
    retry_count: int = 0
    max_retries: int = 3
    retry_delay: timedelta = field(default_factory=lambda: timedelta(minutes=5))
    
    # Monitoring and metadata
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def duration(self) -> Optional[timedelta]:
        """Calculate actual execution duration"""
        if self.started_at and self.completed_at:
            return self.completed_at - self.started_at
        return None
    
    @property
    def is_overdue(self) -> bool:
        """Check if task is overdue"""
        if not self.deadline:
            return False
        return datetime.utcnow() > self.deadline
    
    @property
    def is_ready(self) -> bool:
        """Check if task is ready to execute (dependencies satisfied)"""
        return self.status == TaskStatus.QUEUED and not self.depends_on
    
    @property
    def priority_score(self) -> float:
        """Calculate priority score for scheduling"""
        base_score = self.priority.value * 100
        
        # Urgency bonus
        if self.deadline:
            time_to_deadline = (self.deadline - datetime.utcnow()).total_seconds()
            urgency_bonus = max(0, 100 - (time_to_deadline / 3600))  # Bonus based on hours
            base_score += urgency_bonus
        
        # Retry penalty
        retry_penalty = self.retry_count * 10
        base_score -= retry_penalty
        
        return max(0, base_score)


@dataclass
class TaskBatch:
    """Batch of related tasks"""
    batch_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    tasks: List[str] = field(default_factory=list)  # Task IDs
    execution_mode: str = "parallel"  # parallel, sequential, mixed
    priority: TaskPriority = TaskPriority.MEDIUM
    created_at: datetime = field(default_factory=datetime.utcnow)
    deadline: Optional[datetime] = None
    
    @property
    def is_completed(self) -> bool:
        """Check if all tasks in batch are completed"""
        # This would need access to task manager to check actual status
        return False


@dataclass
class ResourceConstraint:
    """Resource constraints for task execution"""
    max_memory_mb: Optional[int] = None
    max_cpu_percent: Optional[int] = None
    max_concurrent_tasks: Optional[int] = None
    required_disk_space_mb: Optional[int] = None
    network_bandwidth_mbps: Optional[int] = None
    gpu_required: bool = False


class TaskManager:
    """
    Advanced task management system for AI agents
    
    Features:
    - Intelligent task prioritization
    - Resource-aware scheduling
    - Dependency resolution
    - Load balancing across agents
    - Retry and recovery mechanisms
    - Performance monitoring
    - Batch processing optimization
    """
    
    def __init__(self, agent_registry, communication_hub):
        self.agent_registry = agent_registry
        self.communication_hub = communication_hub
        
        # Task storage
        self.tasks: Dict[str, Task] = {}
        self.task_batches: Dict[str, TaskBatch] = {}
        self.task_queue: List[Tuple[float, str]] = []  # Priority queue (priority, task_id)
        
        # Scheduling and execution
        self.active_tasks: Dict[str, Task] = {}  # Currently running tasks
        self.completed_tasks: List[str] = []
        self.failed_tasks: List[str] = []
        
        # Agent assignment
        self.agent_assignments: Dict[str, List[str]] = {}  # agent_id -> task_ids
        self.agent_load: Dict[str, int] = {}  # agent_id -> current task count
        
        # Configuration
        self.max_concurrent_tasks = 100
        self.default_timeout = timedelta(hours=1)
        self.cleanup_interval = timedelta(hours=24)
        
        # Performance tracking
        self.execution_stats = {
            "total_tasks": 0,
            "completed_tasks": 0,
            "failed_tasks": 0,
            "average_execution_time": 0.0,
            "agent_utilization": 0.0
        }
        
        # Background processing
        self._shutdown_event = asyncio.Event()
        self._background_tasks: List[asyncio.Task] = []
    
    async def initialize(self) -> None:
        """Initialize the task manager"""
        try:
            # Start background processing tasks
            self._background_tasks.extend([
                asyncio.create_task(self._task_scheduler()),
                asyncio.create_task(self._dependency_resolver()),
                asyncio.create_task(self._task_monitor()),
                asyncio.create_task(self._resource_optimizer()),
                asyncio.create_task(self._cleanup_completed_tasks())
            ])
            
            logger.info("Task Manager initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize task manager: {str(e)}")
            raise
    
    async def submit_task(self, task: Task) -> str:
        """Submit a new task for execution"""
        try:
            # Validate task
            if not self._validate_task(task):
                raise ValueError(f"Invalid task: {task.task_id}")
            
            # Store task
            self.tasks[task.task_id] = task
            task.status = TaskStatus.QUEUED
            
            # Add to priority queue
            heappush(self.task_queue, (-task.priority_score, task.task_id))
            
            # Update statistics
            self.execution_stats["total_tasks"] += 1
            
            # Trigger scheduling
            await self._trigger_scheduling()
            
            logger.info(f"Task {task.task_id} submitted successfully")
            return task.task_id
            
        except Exception as e:
            logger.error(f"Failed to submit task {task.task_id}: {str(e)}")
            raise
    
    async def submit_batch(self, batch: TaskBatch) -> str:
        """Submit a batch of related tasks"""
        try:
            # Store batch
            self.task_batches[batch.batch_id] = batch
            
            # Submit individual tasks
            submitted_tasks = []
            for task_id in batch.tasks:
                if task_id in self.tasks:
                    task = self.tasks[task_id]
                    
                    # Set batch metadata
                    task.metadata["batch_id"] = batch.batch_id
                    task.metadata["batch_mode"] = batch.execution_mode
                    
                    # Adjust priority based on batch
                    if batch.priority.value > task.priority.value:
                        task.priority = batch.priority
                    
                    # Set dependencies for sequential execution
                    if batch.execution_mode == "sequential" and submitted_tasks:
                        task.depends_on.append(submitted_tasks[-1])
                    
                    await self.submit_task(task)
                    submitted_tasks.append(task_id)
            
            logger.info(f"Batch {batch.batch_id} with {len(submitted_tasks)} tasks submitted")
            return batch.batch_id
            
        except Exception as e:
            logger.error(f"Failed to submit batch {batch.batch_id}: {str(e)}")
            raise
    
    async def cancel_task(self, task_id: str) -> bool:
        """Cancel a task"""
        try:
            task = self.tasks.get(task_id)
            if not task:
                return False
            
            if task.status == TaskStatus.RUNNING:
                # Send cancellation message to agent
                if task.assigned_agent:
                    await self._send_cancellation_message(task.assigned_agent, task_id)
            
            task.status = TaskStatus.CANCELLED
            task.completed_at = datetime.utcnow()
            
            # Remove from active tasks
            self.active_tasks.pop(task_id, None)
            
            # Update agent assignment
            if task.assigned_agent:
                agent_tasks = self.agent_assignments.get(task.assigned_agent, [])
                if task_id in agent_tasks:
                    agent_tasks.remove(task_id)
                self.agent_load[task.assigned_agent] = max(0, self.agent_load.get(task.assigned_agent, 0) - 1)
            
            logger.info(f"Task {task_id} cancelled")
            return True
            
        except Exception as e:
            logger.error(f"Failed to cancel task {task_id}: {str(e)}")
            return False
    
    async def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed status of a task"""
        task = self.tasks.get(task_id)
        if not task:
            return None
        
        status_info = {
            "task_id": task.task_id,
            "status": task.status.value,
            "priority": task.priority.value,
            "created_at": task.created_at.isoformat(),
            "assigned_agent": task.assigned_agent,
            "progress": await self._calculate_task_progress(task),
            "estimated_completion": await self._estimate_completion_time(task),
            "dependencies_satisfied": len(task.depends_on) == 0,
            "retry_count": task.retry_count,
            "is_overdue": task.is_overdue
        }
        
        if task.started_at:
            status_info["started_at"] = task.started_at.isoformat()
        
        if task.completed_at:
            status_info["completed_at"] = task.completed_at.isoformat()
            status_info["duration"] = task.duration.total_seconds() if task.duration else None
        
        if task.error:
            status_info["error"] = task.error
        
        return status_info
    
    async def get_agent_workload(self, agent_id: str) -> Dict[str, Any]:
        """Get workload information for an agent"""
        agent_tasks = self.agent_assignments.get(agent_id, [])
        active_tasks = [tid for tid in agent_tasks if tid in self.active_tasks]
        
        return {
            "agent_id": agent_id,
            "total_assigned_tasks": len(agent_tasks),
            "active_tasks": len(active_tasks),
            "current_load": self.agent_load.get(agent_id, 0),
            "utilization_percent": await self._calculate_agent_utilization(agent_id),
            "average_task_duration": await self._calculate_average_task_duration(agent_id),
            "success_rate": await self._calculate_agent_success_rate(agent_id)
        }
    
    async def _task_scheduler(self) -> None:
        """Background task scheduler"""
        while not self._shutdown_event.is_set():
            try:
                # Process task queue
                await self._process_task_queue()
                
                # Check for overdue tasks
                await self._handle_overdue_tasks()
                
                # Rebalance load if needed
                await self._rebalance_agent_load()
                
            except Exception as e:
                logger.error(f"Error in task scheduler: {str(e)}")
            
            await asyncio.sleep(10)  # Schedule every 10 seconds
    
    async def _process_task_queue(self) -> None:
        """Process tasks from the priority queue"""
        while self.task_queue and len(self.active_tasks) < self.max_concurrent_tasks:
            try:
                # Get highest priority task
                _, task_id = heappop(self.task_queue)
                task = self.tasks.get(task_id)
                
                if not task or task.status != TaskStatus.QUEUED:
                    continue
                
                # Check if dependencies are satisfied
                if not await self._check_dependencies(task):
                    # Re-queue if dependencies not ready
                    heappush(self.task_queue, (-task.priority_score, task_id))
                    break
                
                # Find suitable agent
                agent_id = await self._find_best_agent(task)
                if not agent_id:
                    # No available agent, re-queue
                    heappush(self.task_queue, (-task.priority_score, task_id))
                    break
                
                # Assign and start task
                await self._assign_and_start_task(task, agent_id)
                
            except Exception as e:
                logger.error(f"Error processing task queue: {str(e)}")
                break
    
    async def _find_best_agent(self, task: Task) -> Optional[str]:
        """Find the best available agent for a task"""
        suitable_agents = []
        
        # Check preferred agents first
        for agent_id in task.preferred_agents:
            agent = self.agent_registry.agents.get(agent_id)
            if agent and await self._is_agent_available(agent_id, task):
                if await agent.can_handle_task(task.task_type.value, task.context):
                    suitable_agents.append((agent_id, 100))  # High score for preferred
        
        # Check all available agents
        for agent_id, agent in self.agent_registry.agents.items():
            if agent_id not in task.preferred_agents:
                if await self._is_agent_available(agent_id, task):
                    if await agent.can_handle_task(task.task_type.value, task.context):
                        # Calculate suitability score
                        score = await self._calculate_agent_suitability(agent_id, task)
                        suitable_agents.append((agent_id, score))
        
        if not suitable_agents:
            return None
        
        # Sort by score and return best agent
        suitable_agents.sort(key=lambda x: x[1], reverse=True)
        return suitable_agents[0][0]
    
    async def _assign_and_start_task(self, task: Task, agent_id: str) -> None:
        """Assign task to agent and start execution"""
        try:
            # Update task status
            task.status = TaskStatus.ASSIGNED
            task.assigned_agent = agent_id
            
            # Update agent assignment tracking
            if agent_id not in self.agent_assignments:
                self.agent_assignments[agent_id] = []
            self.agent_assignments[agent_id].append(task.task_id)
            self.agent_load[agent_id] = self.agent_load.get(agent_id, 0) + 1
            
            # Get agent and create agent task
            agent = self.agent_registry.agents[agent_id]
            from .base_agent import AgentTask, AgentPriority
            
            # Map priority
            priority_map = {
                TaskPriority.LOW: AgentPriority.LOW,
                TaskPriority.MEDIUM: AgentPriority.MEDIUM,
                TaskPriority.HIGH: AgentPriority.HIGH,
                TaskPriority.URGENT: AgentPriority.URGENT,
                TaskPriority.CRITICAL: AgentPriority.CRITICAL
            }
            
            agent_task = AgentTask(
                task_type=task.task_type.value,
                priority=priority_map[task.priority],
                context=task.context,
                timeout_seconds=int(self.default_timeout.total_seconds())
            )
            
            # Start execution
            task.status = TaskStatus.RUNNING
            task.started_at = datetime.utcnow()
            self.active_tasks[task.task_id] = task
            
            # Execute task asynchronously
            asyncio.create_task(self._execute_task_on_agent(task, agent, agent_task))
            
            logger.info(f"Task {task.task_id} assigned to agent {agent_id}")
            
        except Exception as e:
            logger.error(f"Failed to assign task {task.task_id} to agent {agent_id}: {str(e)}")
            task.status = TaskStatus.FAILED
            task.error = str(e)
    
    async def _execute_task_on_agent(self, task: Task, agent, agent_task) -> None:
        """Execute task on agent and handle result"""
        try:
            # Execute task
            result = await agent.execute_task(agent_task)
            
            # Handle successful completion
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.utcnow()
            task.result = result
            
            # Update statistics
            self.execution_stats["completed_tasks"] += 1
            
            # Resolve dependent tasks
            await self._resolve_dependencies(task.task_id)
            
            logger.info(f"Task {task.task_id} completed successfully")
            
        except Exception as e:
            # Handle task failure
            task.status = TaskStatus.FAILED
            task.completed_at = datetime.utcnow()
            task.error = str(e)
            
            # Update statistics
            self.execution_stats["failed_tasks"] += 1
            
            # Check retry policy
            if task.retry_count < task.max_retries:
                await self._schedule_retry(task)
            else:
                logger.error(f"Task {task.task_id} failed permanently: {str(e)}")
                self.failed_tasks.append(task.task_id)
        
        finally:
            # Cleanup
            self.active_tasks.pop(task.task_id, None)
            
            # Update agent load
            if task.assigned_agent:
                self.agent_load[task.assigned_agent] = max(0, self.agent_load.get(task.assigned_agent, 0) - 1)
    
    async def get_system_statistics(self) -> Dict[str, Any]:
        """Get comprehensive system statistics"""
        return {
            "task_statistics": self.execution_stats,
            "queue_size": len(self.task_queue),
            "active_tasks": len(self.active_tasks),
            "agent_count": len(self.agent_registry.agents),
            "average_agent_utilization": sum(self.agent_load.values()) / max(len(self.agent_load), 1),
            "system_load": len(self.active_tasks) / self.max_concurrent_tasks,
            "uptime": (datetime.utcnow() - datetime.utcnow()).total_seconds()  # Would track actual uptime
        }
    
    # Additional helper methods for dependency resolution, load balancing, monitoring, etc. would be implemented here
