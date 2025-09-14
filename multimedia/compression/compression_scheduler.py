"""Compression Scheduler
Intelligent scheduling system for compression tasks and resource management.

Created by: Fahed Mlaiel <mlaiel@live.de>
"""

import asyncio
import logging
from typing import Dict, List, Optional, Union, Any, Callable
from dataclasses import dataclass, field
from pathlib import Path
from enum import Enum
import heapq
import time
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class TaskPriority(Enum):
    """Task priority levels."""
    LOW = 1
    NORMAL = 5
    HIGH = 8
    URGENT = 10

class TaskStatus(Enum):
    """Task execution status."""
    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class CompressionTask:
    """Compression task definition."""
    task_id: str
    input_path: Path
    output_path: Path
    compression_type: str  # audio, video, image
    profile: str
    priority: TaskPriority = TaskPriority.NORMAL
    estimated_duration: float = 0.0
    memory_requirement: int = 1024  # MB
    cpu_requirement: int = 1  # CPU cores
    gpu_requirement: bool = False
    deadline: Optional[datetime] = None
    dependencies: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __lt__(self, other) -> None:
        """Enable priority queue ordering."""
        return self.priority.value > other.priority.value

@dataclass
class ResourceUsage:
    """Current resource usage tracking."""
    cpu_cores_used: int = 0
    memory_mb_used: int = 0
    gpu_in_use: bool = False
    active_tasks: int = 0

class CompressionScheduler:
    """Intelligent task scheduler for compression operations."""
    
    def __init__(
        self,
        max_cpu_cores -> None: int = 4,
        max_memory_mb -> None: int = 8192,
        has_gpu -> None: bool = False,
        max_concurrent_tasks -> None: int = 3
    ) -> None:
        """Initialize the compression scheduler."""
        self.max_cpu_cores = max_cpu_cores
        self.max_memory_mb = max_memory_mb
        self.has_gpu = has_gpu
        self.max_concurrent_tasks = max_concurrent_tasks
        
        self.task_queue = []  # Priority queue
        self.active_tasks = {}
        self.completed_tasks = {}
        self.failed_tasks = {}
        
        self.resource_usage = ResourceUsage()
        self.scheduler_running = False
        
        # Performance tracking
        self.performance_metrics = {
            "tasks_completed": 0,
            "tasks_failed": 0,
            "total_processing_time": 0.0,
            "average_wait_time": 0.0,
            "resource_utilization": {
                "cpu": 0.0,
                "memory": 0.0,
                "gpu": 0.0
            }
        }
    
    async def schedule_task(
        self,
        input_path: Union[str, Path],
        output_path: Union[str, Path],
        compression_type: str,
        profile: str,
        priority: TaskPriority = TaskPriority.NORMAL,
        deadline: Optional[datetime] = None,
        dependencies: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Schedule a compression task.
        
        Args:
            input_path: Path to input file
            output_path: Path to output file
            compression_type: Type of compression (audio, video, image)
            profile: Compression profile to use
            priority: Task priority
            deadline: Optional deadline for completion
            dependencies: List of task IDs this task depends on
            metadata: Additional task metadata
            
        Returns:
            Task ID for tracking
        """
        task_id = f"task_{int(time.time())}_{len(self.task_queue)}"
        
        # Estimate resource requirements
        estimated_duration, memory_req, cpu_req, gpu_req = self._estimate_requirements(
            input_path, compression_type, profile
        )
        
        task = CompressionTask(
            task_id=task_id,
            input_path=Path(input_path),
            output_path=Path(output_path),
            compression_type=compression_type,
            profile=profile,
            priority=priority,
            estimated_duration=estimated_duration,
            memory_requirement=memory_req,
            cpu_requirement=cpu_req,
            gpu_requirement=gpu_req,
            deadline=deadline,
            dependencies=dependencies or [],
            metadata=metadata or {}
        )
        
        # Add to priority queue
        heapq.heappush(self.task_queue, task)
        
        logger.info(f"Scheduled task {task_id} with priority {priority.name}")
        
        return task_id
    
    def _estimate_requirements(
        self,
        input_path: Union[str, Path],
        compression_type: str,
        profile: str
    ) -> tuple:
        """Estimate resource requirements for a task."""
        input_path = Path(input_path)
        
        if not input_path.exists():
            file_size = 100 * 1024 * 1024  # Default 100MB
        else:
            file_size = input_path.stat().st_size
        
        # Base estimates
        if compression_type == "video":
            # Video is most resource intensive
            estimated_duration = file_size / (50 * 1024 * 1024)  # ~50MB/sec
            memory_req = min(4096, max(1024, file_size // (1024 * 1024)))
            cpu_req = 2
            gpu_req = file_size > 500 * 1024 * 1024  # Use GPU for large files
        elif compression_type == "audio":
            # Audio is moderately resource intensive
            estimated_duration = file_size / (100 * 1024 * 1024)  # ~100MB/sec
            memory_req = min(2048, max(512, file_size // (2 * 1024 * 1024)))
            cpu_req = 1
            gpu_req = False
        else:  # image
            # Images are least resource intensive
            estimated_duration = file_size / (200 * 1024 * 1024)  # ~200MB/sec
            memory_req = min(1024, max(256, file_size // (4 * 1024 * 1024)))
            cpu_req = 1
            gpu_req = False
        
        # Adjust for profile complexity
        if "high" in profile.lower() or "lossless" in profile.lower():
            estimated_duration *= 2
            memory_req = int(memory_req * 1.5)
        
        return estimated_duration, memory_req, cpu_req, gpu_req
    
    async def start_scheduler(self) -> None:
        """Start the task scheduler."""
        if self.scheduler_running:
            return
        
        self.scheduler_running = True
        logger.info("Starting compression scheduler")
        
        while self.scheduler_running:
            try:
                await self._process_queue()
                await asyncio.sleep(1.0)  # Check queue every second
            except Exception as e:
                logger.error(f"Scheduler error: {e}")
                await asyncio.sleep(5.0)
    
    async def _process_queue(self) -> None:
        """Process tasks in the queue based on available resources."""
        if not self.task_queue:
            return
        
        # Check for completed tasks and free resources
        await self._cleanup_completed_tasks()
        
        # Try to start new tasks
        tasks_to_start = []
        temp_queue = []
        
        while self.task_queue and len(tasks_to_start) < self.max_concurrent_tasks:
            task = heapq.heappop(self.task_queue)
            
            # Check if dependencies are satisfied
            if not self._dependencies_satisfied(task):
                temp_queue.append(task)
                continue
            
            # Check if resources are available
            if self._can_start_task(task):
                tasks_to_start.append(task)
            else:
                temp_queue.append(task)
                break  # No point checking more tasks if resources are full
        
        # Put remaining tasks back in queue
        for task in temp_queue:
            heapq.heappush(self.task_queue, task)
        
        # Start eligible tasks
        for task in tasks_to_start:
            await self._start_task(task)
    
    def _dependencies_satisfied(self, task: CompressionTask) -> bool:
        """Check if all task dependencies are satisfied."""
        for dep_id in task.dependencies:
            if dep_id not in self.completed_tasks:
                return False
        return True
    
    def _can_start_task(self, task: CompressionTask) -> bool:
        """Check if resources are available to start a task."""
        # Check CPU cores
        if (self.resource_usage.cpu_cores_used + task.cpu_requirement > 
            self.max_cpu_cores):
            return False
        
        # Check memory
        if (self.resource_usage.memory_mb_used + task.memory_requirement > 
            self.max_memory_mb):
            return False
        
        # Check GPU
        if task.gpu_requirement and (not self.has_gpu or self.resource_usage.gpu_in_use):
            return False
        
        # Check concurrent task limit
        if len(self.active_tasks) >= self.max_concurrent_tasks:
            return False
        
        return True
    
    async def _start_task(self, task -> None: CompressionTask) -> None:
        """Start executing a compression task."""
        # Reserve resources
        self.resource_usage.cpu_cores_used += task.cpu_requirement
        self.resource_usage.memory_mb_used += task.memory_requirement
        if task.gpu_requirement:
            self.resource_usage.gpu_in_use = True
        self.resource_usage.active_tasks += 1
        
        # Add to active tasks
        self.active_tasks[task.task_id] = {
            "task": task,
            "start_time": time.time(),
            "status": TaskStatus.RUNNING
        }
        
        logger.info(f"Starting task {task.task_id}")
        
        # Execute task asynchronously
        asyncio.create_task(self._execute_task(task))
    
    async def _execute_task(self, task -> None: CompressionTask) -> None:
        """Execute a compression task."""
        try:
            # Simulate task execution
            await asyncio.sleep(task.estimated_duration)
            
            # Mark as completed
            end_time = time.time()
            start_time = self.active_tasks[task.task_id]["start_time"]
            processing_time = end_time - start_time
            
            self.completed_tasks[task.task_id] = {
                "task": task,
                "start_time": start_time,
                "end_time": end_time,
                "processing_time": processing_time,
                "status": TaskStatus.COMPLETED
            }
            
            # Update performance metrics
            self.performance_metrics["tasks_completed"] += 1
            self.performance_metrics["total_processing_time"] += processing_time
            
            logger.info(f"Completed task {task.task_id} in {processing_time:.2f}s")
            
        except Exception as e:
            # Mark as failed
            self.failed_tasks[task.task_id] = {
                "task": task,
                "start_time": self.active_tasks[task.task_id]["start_time"],
                "end_time": time.time(),
                "error": str(e),
                "status": TaskStatus.FAILED
            }
            
            self.performance_metrics["tasks_failed"] += 1
            logger.error(f"Task {task.task_id} failed: {e}")
        
        finally:
            # Free resources
            self.resource_usage.cpu_cores_used -= task.cpu_requirement
            self.resource_usage.memory_mb_used -= task.memory_requirement
            if task.gpu_requirement:
                self.resource_usage.gpu_in_use = False
            self.resource_usage.active_tasks -= 1
    
    async def _cleanup_completed_tasks(self) -> None:
        """Clean up completed tasks from active tasks."""
        completed_task_ids = []
        
        for task_id, task_info in self.active_tasks.items():
            if (task_id in self.completed_tasks or 
                task_id in self.failed_tasks):
                completed_task_ids.append(task_id)
        
        for task_id in completed_task_ids:
            del self.active_tasks[task_id]
    
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific task."""
        if task_id in self.active_tasks:
            task_info = self.active_tasks[task_id]
            elapsed_time = time.time() - task_info["start_time"]
            progress = min(1.0, elapsed_time / task_info["task"].estimated_duration)
            
            return {
                "task_id": task_id,
                "status": TaskStatus.RUNNING.value,
                "progress": progress,
                "elapsed_time": elapsed_time,
                "estimated_remaining": max(0, task_info["task"].estimated_duration - elapsed_time)
            }
        elif task_id in self.completed_tasks:
            return {
                "task_id": task_id,
                "status": TaskStatus.COMPLETED.value,
                "result": self.completed_tasks[task_id]
            }
        elif task_id in self.failed_tasks:
            return {
                "task_id": task_id,
                "status": TaskStatus.FAILED.value,
                "error": self.failed_tasks[task_id]
            }
        else:
            # Check if in queue
            for task in self.task_queue:
                if task.task_id == task_id:
                    return {
                        "task_id": task_id,
                        "status": TaskStatus.QUEUED.value,
                        "queue_position": self._get_queue_position(task_id)
                    }
            
            return None
    
    def _get_queue_position(self, task_id: str) -> int:
        """Get position of task in queue."""
        for i, task in enumerate(self.task_queue):
            if task.task_id == task_id:
                return i + 1
        return -1
    
    def get_scheduler_status(self) -> Dict[str, Any]:
        """Get comprehensive scheduler status."""
        return {
            "running": self.scheduler_running,
            "queue_size": len(self.task_queue),
            "active_tasks": len(self.active_tasks),
            "completed_tasks": len(self.completed_tasks),
            "failed_tasks": len(self.failed_tasks),
            "resource_usage": {
                "cpu_cores": f"{self.resource_usage.cpu_cores_used}/{self.max_cpu_cores}",
                "memory_mb": f"{self.resource_usage.memory_mb_used}/{self.max_memory_mb}",
                "gpu_in_use": self.resource_usage.gpu_in_use,
                "utilization": {
                    "cpu": self.resource_usage.cpu_cores_used / self.max_cpu_cores,
                    "memory": self.resource_usage.memory_mb_used / self.max_memory_mb,
                    "gpu": 1.0 if self.resource_usage.gpu_in_use else 0.0
                }
            },
            "performance": self.performance_metrics
        }
    
    async def cancel_task(self, task_id: str) -> bool:
        """Cancel a task if possible."""
        # Remove from queue if not started
        for i, task in enumerate(self.task_queue):
            if task.task_id == task_id:
                del self.task_queue[i]
                heapq.heapify(self.task_queue)
                logger.info(f"Cancelled queued task {task_id}")
                return True
        
        # Cannot cancel running tasks in this simulation
        return False
    
    async def stop_scheduler(self) -> None:
        """Stop the task scheduler."""
        self.scheduler_running = False
        logger.info("Stopping compression scheduler")
        
        # Wait for active tasks to complete (or implement graceful shutdown)
        while self.active_tasks:
            await asyncio.sleep(1.0)
    
    def optimize_queue(self) -> None:
        """Optimize task queue order based on deadlines and priorities."""
        # Re-prioritize tasks with approaching deadlines
        current_time = datetime.now()
        
        for task in self.task_queue:
            if task.deadline:
                time_to_deadline = (task.deadline - current_time).total_seconds()
                if time_to_deadline < task.estimated_duration * 2:
                    # Boost priority for tasks close to deadline
                    task.priority = TaskPriority.URGENT
        
        # Re-heapify the queue
        heapq.heapify(self.task_queue)