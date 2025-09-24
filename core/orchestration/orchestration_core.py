"""
Enterprise Orchestration Core - Advanced Enterprise Workflow Orchestration System
=================================================================================

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

Core business logic for enterprise workflow orchestration, service coordination,
distributed system management, and business process automation.
"""

import asyncio
from typing import Dict, List, Optional, Any, Tuple, Union, Callable
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import logging
import json
import hashlib
import uuid
from concurrent.futures import ThreadPoolExecutor
import threading

# Get logger
logger = logging.getLogger(__name__)

class WorkflowStatus(Enum):
    """Workflow execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"
    RETRYING = "retrying"

class TaskStatus(Enum):
    """Individual task status"""
    WAITING = "waiting"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    RETRY = "retry"

class TaskType(Enum):
    """Task execution types"""
    SYNC = "sync"
    ASYNC = "async"
    PARALLEL = "parallel"
    SEQUENTIAL = "sequential"
    CONDITIONAL = "conditional"
    LOOP = "loop"

class ServiceType(Enum):
    """Service types in the ecosystem"""
    CORE = "core"
    API = "api"
    PAYMENT = "payment"
    NOTIFICATION = "notification"
    ANALYTICS = "analytics"
    ML = "ml"
    STORAGE = "storage"
    AUTH = "auth"
    EXTERNAL = "external"

class OrchestrationEvent(Enum):
    """Orchestration events"""
    WORKFLOW_STARTED = "workflow_started"
    WORKFLOW_COMPLETED = "workflow_completed"
    WORKFLOW_FAILED = "workflow_failed"
    TASK_STARTED = "task_started"
    TASK_COMPLETED = "task_completed"
    TASK_FAILED = "task_failed"
    SERVICE_DOWN = "service_down"
    SERVICE_UP = "service_up"

@dataclass
class Task:
    """Individual task definition"""
    task_id: str
    name: str
    task_type: TaskType
    service_name: str
    function_name: str
    input_parameters: Dict[str, Any]
    depends_on: List[str]
    timeout_seconds: int
    retry_count: int
    retry_delay_seconds: int
    status: TaskStatus = TaskStatus.WAITING
    result: Optional[Any] = None
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    execution_duration: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Workflow:
    """Workflow definition and execution state"""
    workflow_id: str
    name: str
    description: str
    tasks: List[Task]
    status: WorkflowStatus
    priority: int
    created_by: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    total_duration: Optional[float] = None
    success_count: int = 0
    failure_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Service:
    """Service registration and health information"""
    service_id: str
    name: str
    service_type: ServiceType
    endpoint: str
    health_check_url: str
    version: str
    is_healthy: bool = True
    last_health_check: Optional[datetime] = None
    response_time_ms: float = 0.0
    registered_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class OrchestrationMetrics:
    """Orchestration system metrics"""
    total_workflows: int
    active_workflows: int
    completed_workflows: int
    failed_workflows: int
    total_tasks: int
    completed_tasks: int
    failed_tasks: int
    average_workflow_duration: float
    average_task_duration: float
    system_throughput: float
    error_rate: float
    calculated_at: datetime = field(default_factory=datetime.utcnow)

class ServiceRegistry:
    """Service discovery and health monitoring"""
    
    def __init__(self):
        self.services = {}
        self.health_check_interval = 30  # seconds
        self.health_check_timeout = 5  # seconds
        self.unhealthy_threshold = 3  # consecutive failures
        self._health_check_task = None
        
        logger.info("Service Registry initialized")

    async def register_service(self, service_data: Dict[str, Any]) -> str:
        """Register a new service"""
        try:
            service_id = service_data.get("service_id", f"svc_{uuid.uuid4().hex[:12]}")
            
            service = Service(
                service_id=service_id,
                name=service_data["name"],
                service_type=ServiceType(service_data["service_type"]),
                endpoint=service_data["endpoint"],
                health_check_url=service_data["health_check_url"],
                version=service_data.get("version", "1.0.0"),
                metadata=service_data.get("metadata", {})
            )
            
            self.services[service_id] = service
            
            # Perform initial health check
            await self._check_service_health(service)
            
            logger.info(f"Service registered: {service_id} ({service.name})")
            return service_id
            
        except Exception as e:
            logger.error(f"Error registering service: {str(e)}")
            raise

    async def unregister_service(self, service_id: str) -> bool:
        """Unregister a service"""
        try:
            if service_id in self.services:
                service = self.services[service_id]
                del self.services[service_id]
                logger.info(f"Service unregistered: {service_id} ({service.name})")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error unregistering service: {str(e)}")
            return False

    async def get_service(self, service_name: str) -> Optional[Service]:
        """Get service by name"""
        for service in self.services.values():
            if service.name == service_name and service.is_healthy:
                return service
        return None

    async def get_healthy_services(self, service_type: Optional[ServiceType] = None) -> List[Service]:
        """Get all healthy services, optionally filtered by type"""
        services = [s for s in self.services.values() if s.is_healthy]
        
        if service_type:
            services = [s for s in services if s.service_type == service_type]
        
        return services

    async def start_health_monitoring(self):
        """Start continuous health monitoring"""
        if self._health_check_task is None:
            self._health_check_task = asyncio.create_task(self._health_check_loop())
            logger.info("Health monitoring started")

    async def stop_health_monitoring(self):
        """Stop health monitoring"""
        if self._health_check_task:
            self._health_check_task.cancel()
            self._health_check_task = None
            logger.info("Health monitoring stopped")

    async def _health_check_loop(self):
        """Continuous health check loop"""
        while True:
            try:
                await asyncio.sleep(self.health_check_interval)
                await self._check_all_services_health()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Health check loop error: {str(e)}")

    async def _check_all_services_health(self):
        """Check health of all registered services"""
        tasks = []
        for service in self.services.values():
            task = asyncio.create_task(self._check_service_health(service))
            tasks.append(task)
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    async def _check_service_health(self, service: Service):
        """Check health of individual service"""
        try:
            start_time = datetime.utcnow()
            
            # Mock health check - would make actual HTTP request
            is_healthy = await self._perform_health_check(service.health_check_url)
            
            end_time = datetime.utcnow()
            response_time = (end_time - start_time).total_seconds() * 1000
            
            service.is_healthy = is_healthy
            service.last_health_check = end_time
            service.response_time_ms = response_time
            
            if not is_healthy:
                logger.warning(f"Service unhealthy: {service.name} ({service.service_id})")
            
        except Exception as e:
            service.is_healthy = False
            service.last_health_check = datetime.utcnow()
            logger.error(f"Health check failed for {service.name}: {str(e)}")

    async def _perform_health_check(self, health_check_url: str) -> bool:
        """Perform actual health check (mock implementation)"""
        # Mock health check - would use aiohttp or similar
        await asyncio.sleep(0.1)  # Simulate network delay
        return True  # Mock healthy response

class TaskExecutor:
    """Task execution engine"""
    
    def __init__(self, service_registry: ServiceRegistry):
        self.service_registry = service_registry
        self.executor = ThreadPoolExecutor(max_workers=10)
        self.running_tasks = {}
        
        logger.info("Task Executor initialized")

    async def execute_task(self, task: Task) -> Dict[str, Any]:
        """Execute individual task"""
        try:
            task.status = TaskStatus.RUNNING
            task.started_at = datetime.utcnow()
            
            # Get service for task
            service = await self.service_registry.get_service(task.service_name)
            if not service:
                raise Exception(f"Service not available: {task.service_name}")
            
            # Execute task based on type
            if task.task_type == TaskType.SYNC:
                result = await self._execute_sync_task(task, service)
            elif task.task_type == TaskType.ASYNC:
                result = await self._execute_async_task(task, service)
            else:
                result = await self._execute_generic_task(task, service)
            
            task.status = TaskStatus.COMPLETED
            task.result = result
            task.completed_at = datetime.utcnow()
            task.execution_duration = (task.completed_at - task.started_at).total_seconds()
            
            return {
                "success": True,
                "task_id": task.task_id,
                "result": result,
                "execution_time": task.execution_duration
            }
            
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error = str(e)
            task.completed_at = datetime.utcnow()
            if task.started_at:
                task.execution_duration = (task.completed_at - task.started_at).total_seconds()
            
            logger.error(f"Task execution failed: {task.task_id} - {str(e)}")
            
            return {
                "success": False,
                "task_id": task.task_id,
                "error": str(e),
                "execution_time": task.execution_duration
            }

    async def _execute_sync_task(self, task: Task, service: Service) -> Any:
        """Execute synchronous task"""
        # Mock synchronous execution
        await asyncio.sleep(0.5)  # Simulate processing time
        
        result = {
            "task_id": task.task_id,
            "service": service.name,
            "function": task.function_name,
            "input": task.input_parameters,
            "output": f"Result from {task.function_name}",
            "processed_at": datetime.utcnow().isoformat()
        }
        
        return result

    async def _execute_async_task(self, task: Task, service: Service) -> Any:
        """Execute asynchronous task"""
        # Mock asynchronous execution
        await asyncio.sleep(1.0)  # Simulate async processing
        
        result = {
            "task_id": task.task_id,
            "service": service.name,
            "function": task.function_name,
            "input": task.input_parameters,
            "output": f"Async result from {task.function_name}",
            "processed_at": datetime.utcnow().isoformat()
        }
        
        return result

    async def _execute_generic_task(self, task: Task, service: Service) -> Any:
        """Execute generic task"""
        # Mock generic execution
        await asyncio.sleep(0.3)  # Simulate processing
        
        result = {
            "task_id": task.task_id,
            "service": service.name,
            "function": task.function_name,
            "input": task.input_parameters,
            "output": f"Generic result from {task.function_name}",
            "processed_at": datetime.utcnow().isoformat()
        }
        
        return result

    async def execute_with_retry(self, task: Task) -> Dict[str, Any]:
        """Execute task with retry logic"""
        max_retries = task.retry_count
        retry_delay = task.retry_delay_seconds
        
        for attempt in range(max_retries + 1):
            try:
                result = await self.execute_task(task)
                if result["success"]:
                    return result
                
                if attempt < max_retries:
                    task.status = TaskStatus.RETRY
                    logger.info(f"Retrying task {task.task_id}, attempt {attempt + 1}/{max_retries + 1}")
                    await asyncio.sleep(retry_delay)
                
            except Exception as e:
                if attempt < max_retries:
                    task.status = TaskStatus.RETRY
                    logger.info(f"Retrying task {task.task_id} after error: {str(e)}")
                    await asyncio.sleep(retry_delay)
                else:
                    task.status = TaskStatus.FAILED
                    task.error = str(e)
                    return {
                        "success": False,
                        "task_id": task.task_id,
                        "error": str(e),
                        "attempts": attempt + 1
                    }
        
        return {
            "success": False,
            "task_id": task.task_id,
            "error": "Max retries exceeded",
            "attempts": max_retries + 1
        }

class WorkflowEngine:
    """Workflow orchestration engine"""
    
    def __init__(self, task_executor: TaskExecutor):
        self.task_executor = task_executor
        self.workflows = {}
        self.workflow_templates = {}
        self.running_workflows = {}
        
        logger.info("Workflow Engine initialized")

    async def create_workflow(self, workflow_data: Dict[str, Any]) -> str:
        """Create new workflow"""
        try:
            workflow_id = f"wf_{uuid.uuid4().hex[:12]}"
            
            # Create tasks
            tasks = []
            for task_data in workflow_data.get("tasks", []):
                task = Task(
                    task_id=f"task_{uuid.uuid4().hex[:8]}",
                    name=task_data["name"],
                    task_type=TaskType(task_data.get("task_type", "sync")),
                    service_name=task_data["service_name"],
                    function_name=task_data["function_name"],
                    input_parameters=task_data.get("input_parameters", {}),
                    depends_on=task_data.get("depends_on", []),
                    timeout_seconds=task_data.get("timeout_seconds", 300),
                    retry_count=task_data.get("retry_count", 3),
                    retry_delay_seconds=task_data.get("retry_delay_seconds", 5),
                    metadata=task_data.get("metadata", {})
                )
                tasks.append(task)
            
            # Create workflow
            workflow = Workflow(
                workflow_id=workflow_id,
                name=workflow_data["name"],
                description=workflow_data.get("description", ""),
                tasks=tasks,
                status=WorkflowStatus.PENDING,
                priority=workflow_data.get("priority", 1),
                created_by=workflow_data.get("created_by", "system"),
                metadata=workflow_data.get("metadata", {})
            )
            
            self.workflows[workflow_id] = workflow
            
            logger.info(f"Workflow created: {workflow_id} ({workflow.name})")
            return workflow_id
            
        except Exception as e:
            logger.error(f"Error creating workflow: {str(e)}")
            raise

    async def execute_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """Execute workflow with dependency resolution"""
        try:
            if workflow_id not in self.workflows:
                raise ValueError(f"Workflow not found: {workflow_id}")
            
            workflow = self.workflows[workflow_id]
            
            if workflow.status != WorkflowStatus.PENDING:
                raise ValueError(f"Workflow not in pending state: {workflow.status.value}")
            
            # Start workflow execution
            workflow.status = WorkflowStatus.RUNNING
            workflow.started_at = datetime.utcnow()
            self.running_workflows[workflow_id] = workflow
            
            # Build dependency graph
            dependency_graph = self._build_dependency_graph(workflow.tasks)
            
            # Execute tasks in dependency order
            execution_results = {}
            
            while dependency_graph:
                # Find tasks with no dependencies
                ready_tasks = [task_id for task_id, deps in dependency_graph.items() if not deps]
                
                if not ready_tasks:
                    # Circular dependency detected
                    workflow.status = WorkflowStatus.FAILED
                    remaining_tasks = list(dependency_graph.keys())
                    error_msg = f"Circular dependency detected in tasks: {remaining_tasks}"
                    logger.error(error_msg)
                    return {
                        "success": False,
                        "workflow_id": workflow_id,
                        "error": error_msg,
                        "status": workflow.status.value
                    }
                
                # Execute ready tasks in parallel
                task_objects = [self._get_task_by_id(workflow, task_id) for task_id in ready_tasks]
                parallel_results = await self._execute_tasks_parallel(task_objects)
                
                # Process results and update dependencies
                for task_id, result in zip(ready_tasks, parallel_results):
                    execution_results[task_id] = result
                    
                    # Remove completed task from dependency graph
                    del dependency_graph[task_id]
                    
                    # Remove this task from other tasks' dependencies
                    for deps in dependency_graph.values():
                        deps.discard(task_id)
                    
                    # Update workflow counters
                    if result["success"]:
                        workflow.success_count += 1
                    else:
                        workflow.failure_count += 1
            
            # Complete workflow
            workflow.completed_at = datetime.utcnow()
            workflow.total_duration = (workflow.completed_at - workflow.started_at).total_seconds()
            
            # Determine final status
            if workflow.failure_count == 0:
                workflow.status = WorkflowStatus.COMPLETED
                success = True
            else:
                workflow.status = WorkflowStatus.FAILED
                success = False
            
            # Remove from running workflows
            del self.running_workflows[workflow_id]
            
            logger.info(f"Workflow completed: {workflow_id} - {workflow.status.value}")
            
            return {
                "success": success,
                "workflow_id": workflow_id,
                "status": workflow.status.value,
                "total_duration": workflow.total_duration,
                "success_count": workflow.success_count,
                "failure_count": workflow.failure_count,
                "task_results": execution_results
            }
            
        except Exception as e:
            workflow.status = WorkflowStatus.FAILED
            workflow.completed_at = datetime.utcnow()
            if workflow.started_at:
                workflow.total_duration = (workflow.completed_at - workflow.started_at).total_seconds()
            
            if workflow_id in self.running_workflows:
                del self.running_workflows[workflow_id]
            
            logger.error(f"Workflow execution failed: {workflow_id} - {str(e)}")
            
            return {
                "success": False,
                "workflow_id": workflow_id,
                "error": str(e),
                "status": workflow.status.value
            }

    def _build_dependency_graph(self, tasks: List[Task]) -> Dict[str, set]:
        """Build task dependency graph"""
        graph = {}
        task_ids = {task.task_id for task in tasks}
        
        for task in tasks:
            # Filter dependencies to only include tasks in this workflow
            valid_deps = set(task.depends_on) & task_ids
            graph[task.task_id] = valid_deps
        
        return graph

    def _get_task_by_id(self, workflow: Workflow, task_id: str) -> Optional[Task]:
        """Get task by ID from workflow"""
        for task in workflow.tasks:
            if task.task_id == task_id:
                return task
        return None

    async def _execute_tasks_parallel(self, tasks: List[Task]) -> List[Dict[str, Any]]:
        """Execute multiple tasks in parallel"""
        if not tasks:
            return []
        
        # Create execution coroutines
        task_coroutines = []
        for task in tasks:
            if task.retry_count > 0:
                coroutine = self.task_executor.execute_with_retry(task)
            else:
                coroutine = self.task_executor.execute_task(task)
            task_coroutines.append(coroutine)
        
        # Execute tasks concurrently
        results = await asyncio.gather(*task_coroutines, return_exceptions=True)
        
        # Process results
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append({
                    "success": False,
                    "task_id": tasks[i].task_id,
                    "error": str(result)
                })
            else:
                processed_results.append(result)
        
        return processed_results

    async def cancel_workflow(self, workflow_id: str) -> bool:
        """Cancel running workflow"""
        try:
            if workflow_id not in self.workflows:
                return False
            
            workflow = self.workflows[workflow_id]
            
            if workflow.status == WorkflowStatus.RUNNING:
                workflow.status = WorkflowStatus.CANCELLED
                workflow.completed_at = datetime.utcnow()
                if workflow.started_at:
                    workflow.total_duration = (workflow.completed_at - workflow.started_at).total_seconds()
                
                if workflow_id in self.running_workflows:
                    del self.running_workflows[workflow_id]
                
                logger.info(f"Workflow cancelled: {workflow_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error cancelling workflow: {str(e)}")
            return False

    async def get_workflow_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get current workflow status"""
        if workflow_id not in self.workflows:
            return None
        
        workflow = self.workflows[workflow_id]
        
        # Calculate task status summary
        task_summary = {}
        for task in workflow.tasks:
            status = task.status.value
            task_summary[status] = task_summary.get(status, 0) + 1
        
        return {
            "workflow_id": workflow_id,
            "name": workflow.name,
            "status": workflow.status.value,
            "created_at": workflow.created_at.isoformat(),
            "started_at": workflow.started_at.isoformat() if workflow.started_at else None,
            "completed_at": workflow.completed_at.isoformat() if workflow.completed_at else None,
            "total_duration": workflow.total_duration,
            "success_count": workflow.success_count,
            "failure_count": workflow.failure_count,
            "total_tasks": len(workflow.tasks),
            "task_status_summary": task_summary,
            "priority": workflow.priority
        }

class EventBus:
    """Event-driven orchestration communication"""
    
    def __init__(self):
        self.subscribers = {}
        self.event_history = []
        self.max_history = 1000
        
        logger.info("Event Bus initialized")

    def subscribe(self, event_type: OrchestrationEvent, callback: Callable):
        """Subscribe to orchestration events"""
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        
        self.subscribers[event_type].append(callback)
        logger.info(f"Subscribed to event: {event_type.value}")

    def unsubscribe(self, event_type: OrchestrationEvent, callback: Callable):
        """Unsubscribe from orchestration events"""
        if event_type in self.subscribers:
            try:
                self.subscribers[event_type].remove(callback)
                logger.info(f"Unsubscribed from event: {event_type.value}")
            except ValueError:
                pass

    async def publish(self, event_type: OrchestrationEvent, event_data: Dict[str, Any]):
        """Publish orchestration event"""
        try:
            event = {
                "event_id": uuid.uuid4().hex,
                "event_type": event_type.value,
                "data": event_data,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Store in history
            self.event_history.append(event)
            if len(self.event_history) > self.max_history:
                self.event_history.pop(0)
            
            # Notify subscribers
            if event_type in self.subscribers:
                for callback in self.subscribers[event_type]:
                    try:
                        if asyncio.iscoroutinefunction(callback):
                            await callback(event)
                        else:
                            callback(event)
                    except Exception as e:
                        logger.error(f"Event callback error: {str(e)}")
            
            logger.debug(f"Event published: {event_type.value}")
            
        except Exception as e:
            logger.error(f"Error publishing event: {str(e)}")

    def get_event_history(self, event_type: Optional[OrchestrationEvent] = None, 
                         limit: int = 100) -> List[Dict[str, Any]]:
        """Get event history"""
        events = self.event_history
        
        if event_type:
            events = [e for e in events if e["event_type"] == event_type.value]
        
        return events[-limit:] if limit else events

class EnterpriseOrchestrationCore:
    """Main Enterprise Orchestration Core System"""
    
    def __init__(self, level: str = "enterprise"):
        self.version = "2.1.0"
        self.level = level
        self.service_registry = ServiceRegistry()
        self.task_executor = TaskExecutor(self.service_registry)
        self.workflow_engine = WorkflowEngine(self.task_executor)
        self.event_bus = EventBus()
        self.metrics = None
        
        # Setup event handlers
        self._setup_event_handlers()
        
        logger.info("Enterprise Orchestration Core initialized")

    def _setup_event_handlers(self):
        """Setup internal event handlers"""
        self.event_bus.subscribe(OrchestrationEvent.WORKFLOW_STARTED, self._on_workflow_started)
        self.event_bus.subscribe(OrchestrationEvent.WORKFLOW_COMPLETED, self._on_workflow_completed)
        self.event_bus.subscribe(OrchestrationEvent.WORKFLOW_FAILED, self._on_workflow_failed)

    async def _on_workflow_started(self, event: Dict[str, Any]):
        """Handle workflow started event"""
        logger.info(f"Workflow started: {event['data']['workflow_id']}")

    async def _on_workflow_completed(self, event: Dict[str, Any]):
        """Handle workflow completed event"""
        logger.info(f"Workflow completed: {event['data']['workflow_id']}")

    async def _on_workflow_failed(self, event: Dict[str, Any]):
        """Handle workflow failed event"""
        logger.warning(f"Workflow failed: {event['data']['workflow_id']}")

    async def start_orchestration(self):
        """Start orchestration system"""
        try:
            # Start health monitoring
            await self.service_registry.start_health_monitoring()
            
            logger.info("Enterprise Orchestration System started")
            
        except Exception as e:
            logger.error(f"Error starting orchestration: {str(e)}")
            raise

    async def stop_orchestration(self):
        """Stop orchestration system"""
        try:
            # Stop health monitoring
            await self.service_registry.stop_health_monitoring()
            
            # Cancel running workflows
            for workflow_id in list(self.workflow_engine.running_workflows.keys()):
                await self.workflow_engine.cancel_workflow(workflow_id)
            
            logger.info("Enterprise Orchestration System stopped")
            
        except Exception as e:
            logger.error(f"Error stopping orchestration: {str(e)}")

    async def register_service(self, service_data: Dict[str, Any]) -> str:
        """Register service with orchestration system"""
        try:
            service_id = await self.service_registry.register_service(service_data)
            
            # Publish service registration event
            await self.event_bus.publish(OrchestrationEvent.SERVICE_UP, {
                "service_id": service_id,
                "service_name": service_data["name"],
                "service_type": service_data["service_type"]
            })
            
            return service_id
            
        except Exception as e:
            logger.error(f"Error registering service: {str(e)}")
            raise

    async def create_and_execute_workflow(self, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create and immediately execute workflow"""
        try:
            # Create workflow
            workflow_id = await self.workflow_engine.create_workflow(workflow_data)
            
            # Publish workflow creation event
            await self.event_bus.publish(OrchestrationEvent.WORKFLOW_STARTED, {
                "workflow_id": workflow_id,
                "workflow_name": workflow_data["name"]
            })
            
            # Execute workflow
            execution_result = await self.workflow_engine.execute_workflow(workflow_id)
            
            # Publish completion event
            if execution_result["success"]:
                await self.event_bus.publish(OrchestrationEvent.WORKFLOW_COMPLETED, {
                    "workflow_id": workflow_id,
                    "duration": execution_result["total_duration"],
                    "success_count": execution_result["success_count"]
                })
            else:
                await self.event_bus.publish(OrchestrationEvent.WORKFLOW_FAILED, {
                    "workflow_id": workflow_id,
                    "error": execution_result.get("error"),
                    "failure_count": execution_result.get("failure_count", 0)
                })
            
            return execution_result
            
        except Exception as e:
            logger.error(f"Error creating and executing workflow: {str(e)}")
            raise

    async def get_orchestration_status(self) -> Dict[str, Any]:
        """Get comprehensive orchestration system status"""
        try:
            # Service statistics
            total_services = len(self.service_registry.services)
            healthy_services = len([s for s in self.service_registry.services.values() if s.is_healthy])
            
            # Workflow statistics
            total_workflows = len(self.workflow_engine.workflows)
            running_workflows = len(self.workflow_engine.running_workflows)
            completed_workflows = len([w for w in self.workflow_engine.workflows.values() 
                                    if w.status == WorkflowStatus.COMPLETED])
            failed_workflows = len([w for w in self.workflow_engine.workflows.values() 
                                  if w.status == WorkflowStatus.FAILED])
            
            # Task statistics
            all_tasks = []
            for workflow in self.workflow_engine.workflows.values():
                all_tasks.extend(workflow.tasks)
            
            total_tasks = len(all_tasks)
            completed_tasks = len([t for t in all_tasks if t.status == TaskStatus.COMPLETED])
            failed_tasks = len([t for t in all_tasks if t.status == TaskStatus.FAILED])
            
            # Calculate metrics
            avg_workflow_duration = 0.0
            if completed_workflows > 0:
                durations = [w.total_duration for w in self.workflow_engine.workflows.values() 
                           if w.status == WorkflowStatus.COMPLETED and w.total_duration]
                avg_workflow_duration = sum(durations) / len(durations) if durations else 0.0
            
            avg_task_duration = 0.0
            completed_task_durations = [t.execution_duration for t in all_tasks 
                                      if t.status == TaskStatus.COMPLETED and t.execution_duration]
            if completed_task_durations:
                avg_task_duration = sum(completed_task_durations) / len(completed_task_durations)
            
            error_rate = 0.0
            if total_workflows > 0:
                error_rate = failed_workflows / total_workflows
            
            status = {
                "system_version": self.version,
                "system_status": "running",
                "services": {
                    "total": total_services,
                    "healthy": healthy_services,
                    "unhealthy": total_services - healthy_services
                },
                "workflows": {
                    "total": total_workflows,
                    "running": running_workflows,
                    "completed": completed_workflows,
                    "failed": failed_workflows
                },
                "tasks": {
                    "total": total_tasks,
                    "completed": completed_tasks,
                    "failed": failed_tasks
                },
                "performance": {
                    "average_workflow_duration_seconds": avg_workflow_duration,
                    "average_task_duration_seconds": avg_task_duration,
                    "error_rate": error_rate
                },
                "last_updated": datetime.utcnow().isoformat()
            }
            
            return status
            
        except Exception as e:
            logger.error(f"Error getting orchestration status: {str(e)}")
            raise

    async def get_system_health(self) -> Dict[str, Any]:
        """Get detailed system health information"""
        try:
            orchestration_status = await self.get_orchestration_status()
            
            # Additional health checks
            health_indicators = {
                "service_registry_healthy": len(self.service_registry.services) > 0,
                "workflow_engine_healthy": True,  # Basic health check
                "task_executor_healthy": True,   # Basic health check
                "event_bus_healthy": len(self.event_bus.subscribers) >= 0
            }
            
            overall_health = all(health_indicators.values())
            
            health_info = {
                "overall_healthy": overall_health,
                "health_indicators": health_indicators,
                "orchestration_status": orchestration_status,
                "event_bus_stats": {
                    "total_subscribers": sum(len(subs) for subs in self.event_bus.subscribers.values()),
                    "event_history_size": len(self.event_bus.event_history)
                },
                "system_uptime": "running",  # Would track actual uptime
                "last_health_check": datetime.utcnow().isoformat()
            }
            
            return health_info
            
        except Exception as e:
            logger.error(f"Error getting system health: {str(e)}")
            raise

    async def create_workflow_template(self, template_data: Dict[str, Any]) -> str:
        """Create reusable workflow template"""
        try:
            template_id = f"template_{uuid.uuid4().hex[:12]}"
            
            template = {
                "template_id": template_id,
                "name": template_data["name"],
                "description": template_data.get("description", ""),
                "version": template_data.get("version", "1.0.0"),
                "tasks": template_data["tasks"],
                "default_parameters": template_data.get("default_parameters", {}),
                "created_at": datetime.utcnow().isoformat(),
                "created_by": template_data.get("created_by", "system")
            }
            
            self.workflow_engine.workflow_templates[template_id] = template
            
            logger.info(f"Workflow template created: {template_id}")
            return template_id
            
        except Exception as e:
            logger.error(f"Error creating workflow template: {str(e)}")
            raise

    async def execute_workflow_from_template(self, template_id: str, 
                                           parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute workflow from template"""
        try:
            if template_id not in self.workflow_engine.workflow_templates:
                raise ValueError(f"Template not found: {template_id}")
            
            template = self.workflow_engine.workflow_templates[template_id]
            
            # Merge parameters
            merged_params = template["default_parameters"].copy()
            if parameters:
                merged_params.update(parameters)
            
            # Create workflow from template
            workflow_data = {
                "name": f"{template['name']} - {datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                "description": f"Workflow from template: {template['name']}",
                "tasks": template["tasks"],
                "metadata": {
                    "template_id": template_id,
                    "parameters": merged_params
                }
            }
            
            # Execute workflow
            return await self.create_and_execute_workflow(workflow_data)
            
        except Exception as e:
            logger.error(f"Error executing workflow from template: {str(e)}")
            raise

# Global instance
enterprise_orchestration_core = EnterpriseOrchestrationCore()

# Export main functions
__all__ = [
    "WorkflowStatus",
    "TaskStatus",
    "TaskType",
    "ServiceType",
    "OrchestrationEvent",
    "Task",
    "Workflow",
    "Service",
    "OrchestrationMetrics",
    "EnterpriseOrchestrationCore",
    "enterprise_orchestration_core"
]

if __name__ == "__main__":
    logger.info("Enterprise Orchestration Core module loaded successfully")