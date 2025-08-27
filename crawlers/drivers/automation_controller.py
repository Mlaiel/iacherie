"""
Enterprise Automation Controller
================================

Advanced automation controller for coordinating browser, API, and session management.
Provides centralized control for complex automation workflows and orchestration.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

⚠️  LEGAL WARNING:
This code is proprietary and confidential. Any unauthorized copying, modification, 
distribution, or use without explicit written permission from Fahed Mlaiel is strictly 
prohibited and may result in legal action.

Professional Development Team Specialties:
🥇 Lead AI Developer & Backend Senior Engineer - Advanced automation systems
🥇 Machine Learning Engineer & Audio Processing Specialist - Intelligence optimization  
🥇 Database Administrator & Security Expert - Data protection and performance
🥇 Microservices Architect & DevOps Engineer - Scalable infrastructure
🥇 AI Prompt Engineer & Content Protection Specialist - Content security
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import time
from contextlib import asynccontextmanager

from .browser_manager import BrowserManager, BrowserConfiguration
from .api_client_manager import APIClientManager
from .session_pool import SessionPoolManager
from .proxy_manager import ProxyManager
from .user_agent_rotator import UserAgentRotator


class AutomationMode(Enum):
    """Automation execution modes"""
    STEALTH = "stealth"
    PERFORMANCE = "performance"
    BALANCED = "balanced"
    AGGRESSIVE = "aggressive"
    CONSERVATIVE = "conservative"


class TaskPriority(Enum):
    """Task execution priority levels"""
    CRITICAL = 1
    HIGH = 2
    NORMAL = 3
    LOW = 4
    BACKGROUND = 5


class AutomationStatus(Enum):
    """Automation controller status"""
    IDLE = "idle"
    INITIALIZING = "initializing"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPING = "stopping"
    ERROR = "error"
    MAINTENANCE = "maintenance"


@dataclass
class AutomationTask:
    """Automation task definition"""
    task_id: str
    task_type: str
    priority: TaskPriority
    target_url: Optional[str] = None
    api_endpoint: Optional[str] = None
    parameters: Dict[str, Any] = field(default_factory=dict)
    retry_count: int = 0
    max_retries: int = 3
    timeout: int = 30
    created_at: datetime = field(default_factory=datetime.utcnow)
    scheduled_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


@dataclass
class AutomationMetrics:
    """Automation performance metrics"""
    tasks_total: int = 0
    tasks_completed: int = 0
    tasks_failed: int = 0
    tasks_retried: int = 0
    average_execution_time: float = 0.0
    success_rate: float = 0.0
    current_load: int = 0
    peak_load: int = 0
    uptime: timedelta = field(default_factory=lambda: timedelta(0))
    last_update: datetime = field(default_factory=datetime.utcnow)


class AutomationController:
    """
    Enterprise automation controller for coordinating browser and API operations.
    
    Features:
    - Centralized task orchestration
    - Resource management and load balancing
    - Performance monitoring and metrics
    - Error handling and recovery
    - Configurable execution modes
    """
    
    def __init__(
        self,
        mode: AutomationMode = AutomationMode.BALANCED,
        max_concurrent_tasks: int = 10,
        max_browser_sessions: int = 5,
        max_api_sessions: int = 20,
        enable_monitoring: bool = True
    ):
        self.mode = mode
        self.max_concurrent_tasks = max_concurrent_tasks
        self.status = AutomationStatus.IDLE
        self.enable_monitoring = enable_monitoring
        
        # Initialize managers
        self.browser_manager = BrowserManager(max_sessions=max_browser_sessions)
        self.api_manager = APIClientManager(max_sessions=max_api_sessions)
        self.session_pool = SessionPoolManager()
        self.proxy_manager = ProxyManager()
        self.user_agent_rotator = UserAgentRotator()
        
        # Task management
        self.task_queue: List[AutomationTask] = []
        self.active_tasks: Dict[str, AutomationTask] = {}
        self.completed_tasks: List[AutomationTask] = []
        
        # Execution control
        self.executor = ThreadPoolExecutor(max_workers=max_concurrent_tasks)
        self.shutdown_event = asyncio.Event()
        
        # Monitoring and metrics
        self.metrics = AutomationMetrics()
        self.start_time = datetime.utcnow()
        
        # Task handlers registry
        self.task_handlers: Dict[str, Callable] = {}
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
    async def initialize(self) -> bool:
        """Initialize automation controller and all managers"""
        try:
            self.status = AutomationStatus.INITIALIZING
            self.logger.info("Initializing automation controller...")
            
            # Initialize all managers
            await self.browser_manager.initialize()
            await self.api_manager.initialize()
            await self.session_pool.initialize()
            await self.proxy_manager.initialize()
            
            self.status = AutomationStatus.IDLE
            self.logger.info("Automation controller initialized successfully")
            return True
            
        except Exception as e:
            self.status = AutomationStatus.ERROR
            self.logger.error(f"Failed to initialize automation controller: {e}")
            return False
    
    def register_task_handler(self, task_type: str, handler: Callable):
        """Register a task handler for specific task type"""
        self.task_handlers[task_type] = handler
        self.logger.info(f"Registered handler for task type: {task_type}")
    
    def submit_task(self, task: AutomationTask) -> str:
        """Submit a task for execution"""
        if task.scheduled_at and task.scheduled_at > datetime.utcnow():
            # Add to scheduled tasks
            self.task_queue.append(task)
            self.logger.info(f"Task {task.task_id} scheduled for {task.scheduled_at}")
        else:
            # Add to immediate execution queue
            self.task_queue.insert(0, task)
            self.logger.info(f"Task {task.task_id} queued for immediate execution")
        
        self.metrics.tasks_total += 1
        return task.task_id
    
    async def execute_task(self, task: AutomationTask) -> Dict[str, Any]:
        """Execute a single automation task"""
        task.started_at = datetime.utcnow()
        self.active_tasks[task.task_id] = task
        
        try:
            # Get task handler
            handler = self.task_handlers.get(task.task_type)
            if not handler:
                raise ValueError(f"No handler registered for task type: {task.task_type}")
            
            # Execute task with timeout
            result = await asyncio.wait_for(
                handler(task), 
                timeout=task.timeout
            )
            
            task.result = result
            task.completed_at = datetime.utcnow()
            self.metrics.tasks_completed += 1
            
            # Update metrics
            execution_time = (task.completed_at - task.started_at).total_seconds()
            self._update_execution_metrics(execution_time)
            
            self.logger.info(f"Task {task.task_id} completed successfully")
            return result
            
        except asyncio.TimeoutError:
            task.error = f"Task timeout after {task.timeout} seconds"
            self.logger.error(f"Task {task.task_id} timed out")
            self.metrics.tasks_failed += 1
            
        except Exception as e:
            task.error = str(e)
            self.logger.error(f"Task {task.task_id} failed: {e}")
            self.metrics.tasks_failed += 1
            
        finally:
            # Move task to completed
            self.active_tasks.pop(task.task_id, None)
            self.completed_tasks.append(task)
            
            # Retry logic
            if task.error and task.retry_count < task.max_retries:
                task.retry_count += 1
                task.error = None
                task.started_at = None
                task.completed_at = None
                self.task_queue.insert(0, task)
                self.metrics.tasks_retried += 1
                self.logger.info(f"Task {task.task_id} scheduled for retry {task.retry_count}")
    
    async def start(self):
        """Start the automation controller"""
        if self.status != AutomationStatus.IDLE:
            raise RuntimeError(f"Cannot start controller in status: {self.status}")
        
        self.status = AutomationStatus.RUNNING
        self.logger.info("Starting automation controller...")
        
        # Start monitoring if enabled
        if self.enable_monitoring:
            asyncio.create_task(self._monitoring_loop())
        
        # Start main execution loop
        await self._execution_loop()
    
    async def stop(self):
        """Stop the automation controller gracefully"""
        self.status = AutomationStatus.STOPPING
        self.logger.info("Stopping automation controller...")
        
        # Signal shutdown
        self.shutdown_event.set()
        
        # Wait for active tasks to complete
        while self.active_tasks:
            await asyncio.sleep(0.1)
        
        # Cleanup resources
        await self.browser_manager.cleanup()
        await self.api_manager.cleanup()
        await self.session_pool.cleanup()
        await self.proxy_manager.cleanup()
        
        self.executor.shutdown(wait=True)
        self.status = AutomationStatus.IDLE
        self.logger.info("Automation controller stopped")
    
    async def pause(self):
        """Pause task execution"""
        self.status = AutomationStatus.PAUSED
        self.logger.info("Automation controller paused")
    
    async def resume(self):
        """Resume task execution"""
        self.status = AutomationStatus.RUNNING
        self.logger.info("Automation controller resumed")
    
    def get_metrics(self) -> AutomationMetrics:
        """Get current automation metrics"""
        self.metrics.current_load = len(self.active_tasks)
        self.metrics.uptime = datetime.utcnow() - self.start_time
        self.metrics.success_rate = (
            self.metrics.tasks_completed / max(self.metrics.tasks_total, 1) * 100
        )
        self.metrics.last_update = datetime.utcnow()
        return self.metrics
    
    def get_task_status(self, task_id: str) -> Optional[AutomationTask]:
        """Get status of a specific task"""
        # Check active tasks
        if task_id in self.active_tasks:
            return self.active_tasks[task_id]
        
        # Check completed tasks
        for task in self.completed_tasks:
            if task.task_id == task_id:
                return task
        
        # Check queued tasks
        for task in self.task_queue:
            if task.task_id == task_id:
                return task
        
        return None
    
    async def _execution_loop(self):
        """Main execution loop for processing tasks"""
        while not self.shutdown_event.is_set():
            try:
                if self.status == AutomationStatus.PAUSED:
                    await asyncio.sleep(1)
                    continue
                
                # Process scheduled tasks
                current_time = datetime.utcnow()
                ready_tasks = [
                    task for task in self.task_queue
                    if not task.scheduled_at or task.scheduled_at <= current_time
                ]
                
                # Sort by priority
                ready_tasks.sort(key=lambda t: t.priority.value)
                
                # Execute tasks up to concurrency limit
                available_slots = self.max_concurrent_tasks - len(self.active_tasks)
                tasks_to_execute = ready_tasks[:available_slots]
                
                for task in tasks_to_execute:
                    self.task_queue.remove(task)
                    asyncio.create_task(self.execute_task(task))
                
                await asyncio.sleep(0.1)
                
            except Exception as e:
                self.logger.error(f"Error in execution loop: {e}")
                await asyncio.sleep(1)
    
    async def _monitoring_loop(self):
        """Monitoring loop for metrics and health checks"""
        while not self.shutdown_event.is_set():
            try:
                # Update metrics
                self.get_metrics()
                
                # Check peak load
                current_load = len(self.active_tasks)
                if current_load > self.metrics.peak_load:
                    self.metrics.peak_load = current_load
                
                # Health checks for managers
                await self._perform_health_checks()
                
                # Clean up old completed tasks
                cutoff_time = datetime.utcnow() - timedelta(hours=24)
                self.completed_tasks = [
                    task for task in self.completed_tasks
                    if task.completed_at and task.completed_at > cutoff_time
                ]
                
                await asyncio.sleep(10)  # Monitor every 10 seconds
                
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(10)
    
    async def _perform_health_checks(self):
        """Perform health checks on all managers"""
        try:
            # Check browser manager health
            if not await self.browser_manager.health_check():
                self.logger.warning("Browser manager health check failed")
            
            # Check API manager health
            if not await self.api_manager.health_check():
                self.logger.warning("API manager health check failed")
            
            # Check session pool health
            if not await self.session_pool.health_check():
                self.logger.warning("Session pool health check failed")
            
        except Exception as e:
            self.logger.error(f"Health check error: {e}")
    
    def _update_execution_metrics(self, execution_time: float):
        """Update execution time metrics"""
        total_time = (
            self.metrics.average_execution_time * self.metrics.tasks_completed +
            execution_time
        )
        self.metrics.average_execution_time = total_time / (self.metrics.tasks_completed + 1)


# Convenience functions
async def create_automation_controller(
    mode: AutomationMode = AutomationMode.BALANCED,
    **kwargs
) -> AutomationController:
    """Create and initialize an automation controller"""
    controller = AutomationController(mode=mode, **kwargs)
    await controller.initialize()
    return controller


@asynccontextmanager
async def automation_context(
    mode: AutomationMode = AutomationMode.BALANCED,
    **kwargs
):
    """Context manager for automation controller"""
    controller = await create_automation_controller(mode=mode, **kwargs)
    try:
        yield controller
    finally:
        await controller.stop()
