#!/usr/bin/env python3
"""
Platform Orchestration Manager - Enterprise Core Component
Central platform coordination and service orchestration system

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel. All rights reserved.
Licensed under Enterprise Commercial License.

This module provides comprehensive platform orchestration capabilities including:
- Multi-service workflow management and coordination
- Business logic pipeline orchestration
- Service dependency management and resolution
- Event-driven architecture coordination
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Callable, Awaitable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import json
import uuid
from contextlib import asynccontextmanager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ServiceStatus(Enum):
    """Service status enumeration"""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    STARTING = "starting"
    STOPPING = "stopping"
    MAINTENANCE = "maintenance"
    UNKNOWN = "unknown"


class WorkflowStatus(Enum):
    """Workflow execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"


@dataclass
class ServiceDefinition:
    """Service definition for orchestration"""
    service_id: str
    name: str
    version: str
    endpoints: List[str]
    dependencies: List[str] = field(default_factory=list)
    health_check_url: Optional[str] = None
    timeout: int = 30
    retry_count: int = 3
    metadata: Dict[str, Any] = field(default_factory=dict)
    status: ServiceStatus = ServiceStatus.UNKNOWN
    last_health_check: Optional[datetime] = None


@dataclass
class WorkflowStep:
    """Individual workflow step definition"""
    step_id: str
    service_id: str
    action: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    timeout: int = 300
    retry_count: int = 3
    on_failure: Optional[str] = None  # rollback, continue, abort


@dataclass
class WorkflowDefinition:
    """Complete workflow definition"""
    workflow_id: str
    name: str
    description: str
    steps: List[WorkflowStep]
    metadata: Dict[str, Any] = field(default_factory=dict)
    timeout: int = 3600
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class WorkflowExecution:
    """Workflow execution tracking"""
    execution_id: str
    workflow_id: str
    status: WorkflowStatus
    current_step: Optional[str] = None
    completed_steps: List[str] = field(default_factory=list)
    failed_steps: List[str] = field(default_factory=list)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    error_message: Optional[str] = None
    execution_log: List[Dict[str, Any]] = field(default_factory=list)


class PlatformOrchestrationManager:
    """
    Enterprise Platform Orchestration Manager
    
    Provides centralized coordination and orchestration for the entire platform,
    managing multi-service workflows, business logic pipelines, and service
    dependencies with enterprise-grade reliability and monitoring.
    """
    
    def __init__(self):
        self.services: Dict[str, ServiceDefinition] = {}
        self.workflows: Dict[str, WorkflowDefinition] = {}
        self.executions: Dict[str, WorkflowExecution] = {}
        self.event_handlers: Dict[str, List[Callable]] = {}
        self.running_tasks: Dict[str, asyncio.Task] = {}
        self._health_check_interval = 30
        self._cleanup_interval = 3600
        self._health_check_task: Optional[asyncio.Task] = None
        self._cleanup_task: Optional[asyncio.Task] = None
        self._shutdown_event = asyncio.Event()
        
        logger.info("Platform Orchestration Manager initialized")
    
    async def start(self) -> None:
        """Start the orchestration manager"""
        try:
            logger.info("Starting Platform Orchestration Manager...")
            
            # Start background tasks
            self._health_check_task = asyncio.create_task(self._health_check_loop())
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())
            
            # Initialize core workflows
            await self._initialize_core_workflows()
            
            logger.info("Platform Orchestration Manager started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start Platform Orchestration Manager: {e}")
            raise
    
    async def stop(self) -> None:
        """Stop the orchestration manager"""
        try:
            logger.info("Stopping Platform Orchestration Manager...")
            
            # Signal shutdown
            self._shutdown_event.set()
            
            # Cancel all running workflows
            for execution_id in list(self.executions.keys()):
                await self.cancel_workflow(execution_id)
            
            # Cancel background tasks
            if self._health_check_task:
                self._health_check_task.cancel()
            if self._cleanup_task:
                self._cleanup_task.cancel()
            
            # Cancel all running tasks
            for task in self.running_tasks.values():
                task.cancel()
            
            # Wait for tasks to complete
            if self.running_tasks:
                await asyncio.gather(*self.running_tasks.values(), return_exceptions=True)
            
            logger.info("Platform Orchestration Manager stopped")
            
        except Exception as e:
            logger.error(f"Error stopping Platform Orchestration Manager: {e}")
    
    # Service Management
    async def register_service(self, service: ServiceDefinition) -> bool:
        """Register a new service for orchestration"""
        try:
            # Validate service definition
            if not service.service_id or not service.name:
                raise ValueError("Service ID and name are required")
            
            # Check for conflicts
            if service.service_id in self.services:
                logger.warning(f"Service {service.service_id} already registered, updating...")
            
            # Register service
            self.services[service.service_id] = service
            
            # Perform initial health check
            await self._check_service_health(service.service_id)
            
            # Emit event
            await self._emit_event("service_registered", {
                "service_id": service.service_id,
                "name": service.name,
                "version": service.version
            })
            
            logger.info(f"Service {service.service_id} registered successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register service {service.service_id}: {e}")
            return False
    
    async def unregister_service(self, service_id: str) -> bool:
        """Unregister a service"""
        try:
            if service_id not in self.services:
                logger.warning(f"Service {service_id} not found for unregistration")
                return False
            
            # Remove service
            service = self.services.pop(service_id)
            
            # Emit event
            await self._emit_event("service_unregistered", {
                "service_id": service_id,
                "name": service.name
            })
            
            logger.info(f"Service {service_id} unregistered successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to unregister service {service_id}: {e}")
            return False
    
    async def get_service_status(self, service_id: str) -> Optional[ServiceStatus]:
        """Get current status of a service"""
        service = self.services.get(service_id)
        return service.status if service else None
    
    async def get_healthy_services(self) -> List[str]:
        """Get list of healthy service IDs"""
        return [
            service_id for service_id, service in self.services.items()
            if service.status == ServiceStatus.HEALTHY
        ]
    
    # Workflow Management
    async def register_workflow(self, workflow: WorkflowDefinition) -> bool:
        """Register a new workflow definition"""
        try:
            # Validate workflow
            if not workflow.workflow_id or not workflow.steps:
                raise ValueError("Workflow ID and steps are required")
            
            # Validate step dependencies
            step_ids = {step.step_id for step in workflow.steps}
            for step in workflow.steps:
                for dep in step.dependencies:
                    if dep not in step_ids:
                        raise ValueError(f"Step {step.step_id} has invalid dependency: {dep}")
                
                # Validate service exists
                if step.service_id not in self.services:
                    logger.warning(f"Step {step.step_id} references service {step.service_id} that is not yet registered")
            
            # Register workflow
            self.workflows[workflow.workflow_id] = workflow
            
            logger.info(f"Workflow {workflow.workflow_id} registered successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register workflow {workflow.workflow_id}: {e}")
            return False
    
    async def execute_workflow(self, workflow_id: str, parameters: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """Execute a workflow and return execution ID"""
        try:
            if workflow_id not in self.workflows:
                raise ValueError(f"Workflow {workflow_id} not found")
            
            workflow = self.workflows[workflow_id]
            execution_id = str(uuid.uuid4())
            
            # Create execution tracking
            execution = WorkflowExecution(
                execution_id=execution_id,
                workflow_id=workflow_id,
                status=WorkflowStatus.PENDING,
                start_time=datetime.utcnow()
            )
            
            self.executions[execution_id] = execution
            
            # Start workflow execution task
            task = asyncio.create_task(self._execute_workflow_steps(execution_id, parameters or {}))
            self.running_tasks[execution_id] = task
            
            logger.info(f"Workflow {workflow_id} execution started with ID: {execution_id}")
            return execution_id
            
        except Exception as e:
            logger.error(f"Failed to execute workflow {workflow_id}: {e}")
            return None
    
    async def get_workflow_status(self, execution_id: str) -> Optional[WorkflowExecution]:
        """Get workflow execution status"""
        return self.executions.get(execution_id)
    
    async def cancel_workflow(self, execution_id: str) -> bool:
        """Cancel a running workflow"""
        try:
            if execution_id not in self.executions:
                logger.warning(f"Execution {execution_id} not found")
                return False
            
            execution = self.executions[execution_id]
            if execution.status not in [WorkflowStatus.RUNNING, WorkflowStatus.PENDING, WorkflowStatus.PAUSED]:
                logger.warning(f"Execution {execution_id} cannot be cancelled in status: {execution.status}")
                return False
            
            # Cancel the task
            if execution_id in self.running_tasks:
                task = self.running_tasks[execution_id]
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
                del self.running_tasks[execution_id]
            
            # Update execution status
            execution.status = WorkflowStatus.CANCELLED
            execution.end_time = datetime.utcnow()
            
            # Emit event
            await self._emit_event("workflow_cancelled", {
                "execution_id": execution_id,
                "workflow_id": execution.workflow_id
            })
            
            logger.info(f"Workflow execution {execution_id} cancelled")
            return True
            
        except Exception as e:
            logger.error(f"Failed to cancel workflow {execution_id}: {e}")
            return False
    
    # Event System
    def add_event_handler(self, event_type: str, handler: Callable[[Dict[str, Any]], Awaitable[None]]) -> None:
        """Add event handler"""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)
    
    def remove_event_handler(self, event_type: str, handler: Callable) -> None:
        """Remove event handler"""
        if event_type in self.event_handlers:
            try:
                self.event_handlers[event_type].remove(handler)
            except ValueError:
                pass
    
    # Internal Methods
    async def _initialize_core_workflows(self) -> None:
        """Initialize core platform workflows"""
        try:
            # Creator Content Processing Workflow
            creator_workflow = WorkflowDefinition(
                workflow_id="creator_content_processing",
                name="Creator Content Processing Pipeline",
                description="Complete content processing workflow for creators",
                steps=[
                    WorkflowStep(
                        step_id="content_upload",
                        service_id="content_service",
                        action="upload_content",
                        timeout=300
                    ),
                    WorkflowStep(
                        step_id="ai_protection",
                        service_id="ai_protection_service",
                        action="apply_protection",
                        dependencies=["content_upload"],
                        timeout=600
                    ),
                    WorkflowStep(
                        step_id="seo_enhancement",
                        service_id="seo_service",
                        action="enhance_content",
                        dependencies=["ai_protection"],
                        timeout=300
                    ),
                    WorkflowStep(
                        step_id="distribution",
                        service_id="distribution_service",
                        action="distribute_content",
                        dependencies=["seo_enhancement"],
                        timeout=600
                    )
                ]
            )
            
            await self.register_workflow(creator_workflow)
            
            # Platform Health Check Workflow
            health_workflow = WorkflowDefinition(
                workflow_id="platform_health_check",
                name="Platform Health Monitoring",
                description="Comprehensive platform health verification",
                steps=[
                    WorkflowStep(
                        step_id="service_health",
                        service_id="monitoring_service",
                        action="check_services",
                        timeout=60
                    ),
                    WorkflowStep(
                        step_id="database_health",
                        service_id="database_service",
                        action="check_connections",
                        timeout=30
                    ),
                    WorkflowStep(
                        step_id="performance_check",
                        service_id="performance_service",
                        action="validate_performance",
                        dependencies=["service_health", "database_health"],
                        timeout=120
                    )
                ]
            )
            
            await self.register_workflow(health_workflow)
            
            logger.info("Core workflows initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize core workflows: {e}")
    
    async def _execute_workflow_steps(self, execution_id: str, parameters: Dict[str, Any]) -> None:
        """Execute workflow steps in dependency order"""
        try:
            execution = self.executions[execution_id]
            workflow = self.workflows[execution.workflow_id]
            
            execution.status = WorkflowStatus.RUNNING
            
            # Build dependency graph
            remaining_steps = {step.step_id: step for step in workflow.steps}
            completed_steps = set()
            
            while remaining_steps and execution.status == WorkflowStatus.RUNNING:
                # Find steps ready to execute (all dependencies completed)
                ready_steps = []
                for step_id, step in remaining_steps.items():
                    if all(dep in completed_steps for dep in step.dependencies):
                        ready_steps.append(step)
                
                if not ready_steps:
                    # Deadlock detection
                    execution.status = WorkflowStatus.FAILED
                    execution.error_message = "Workflow deadlock detected - circular dependencies"
                    break
                
                # Execute ready steps in parallel
                tasks = []
                for step in ready_steps:
                    task = asyncio.create_task(self._execute_workflow_step(execution_id, step, parameters))
                    tasks.append(task)
                
                # Wait for all steps to complete
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Process results
                for step, result in zip(ready_steps, results):
                    if isinstance(result, Exception):
                        logger.error(f"Step {step.step_id} failed: {result}")
                        execution.failed_steps.append(step.step_id)
                        
                        if step.on_failure == "abort":
                            execution.status = WorkflowStatus.FAILED
                            execution.error_message = f"Step {step.step_id} failed: {result}"
                            break
                    else:
                        execution.completed_steps.append(step.step_id)
                        completed_steps.add(step.step_id)
                    
                    # Remove completed step
                    remaining_steps.pop(step.step_id, None)
                
                # Check for failure
                if execution.status == WorkflowStatus.FAILED:
                    break
            
            # Update final status
            if execution.status == WorkflowStatus.RUNNING:
                if remaining_steps:
                    execution.status = WorkflowStatus.FAILED
                    execution.error_message = "Not all steps completed"
                else:
                    execution.status = WorkflowStatus.COMPLETED
            
            execution.end_time = datetime.utcnow()
            
            # Emit completion event
            await self._emit_event("workflow_completed", {
                "execution_id": execution_id,
                "workflow_id": execution.workflow_id,
                "status": execution.status.value,
                "duration": (execution.end_time - execution.start_time).total_seconds()
            })
            
            # Cleanup task reference
            self.running_tasks.pop(execution_id, None)
            
        except asyncio.CancelledError:
            execution.status = WorkflowStatus.CANCELLED
            execution.end_time = datetime.utcnow()
            raise
        except Exception as e:
            logger.error(f"Workflow execution {execution_id} failed: {e}")
            execution.status = WorkflowStatus.FAILED
            execution.error_message = str(e)
            execution.end_time = datetime.utcnow()
    
    async def _execute_workflow_step(self, execution_id: str, step: WorkflowStep, parameters: Dict[str, Any]) -> None:
        """Execute a single workflow step"""
        try:
            execution = self.executions[execution_id]
            service = self.services.get(step.service_id)
            
            if not service:
                logger.warning(f"Service {step.service_id} not registered, continuing with simulation")
            elif service.status != ServiceStatus.HEALTHY:
                raise Exception(f"Service {step.service_id} is not healthy: {service.status}")
            
            execution.current_step = step.step_id
            
            # Log step start
            log_entry = {
                "timestamp": datetime.utcnow().isoformat(),
                "step_id": step.step_id,
                "action": "start",
                "service_id": step.service_id
            }
            execution.execution_log.append(log_entry)
            
            # Simulate step execution (in real implementation, this would call the actual service)
            await asyncio.sleep(0.1)  # Simulate processing time
            
            # Log step completion
            log_entry = {
                "timestamp": datetime.utcnow().isoformat(),
                "step_id": step.step_id,
                "action": "complete",
                "service_id": step.service_id
            }
            execution.execution_log.append(log_entry)
            
            logger.info(f"Step {step.step_id} completed successfully")
            
        except Exception as e:
            # Log step failure
            log_entry = {
                "timestamp": datetime.utcnow().isoformat(),
                "step_id": step.step_id,
                "action": "failed",
                "service_id": step.service_id,
                "error": str(e)
            }
            execution.execution_log.append(log_entry)
            
            logger.error(f"Step {step.step_id} failed: {e}")
            raise
    
    async def _check_service_health(self, service_id: str) -> None:
        """Check health of a specific service"""
        try:
            service = self.services.get(service_id)
            if not service:
                return
            
            # Simulate health check (in real implementation, this would make HTTP calls)
            # For now, we'll randomly set health status
            import random
            if random.random() > 0.1:  # 90% healthy rate
                service.status = ServiceStatus.HEALTHY
            else:
                service.status = ServiceStatus.UNHEALTHY
            
            service.last_health_check = datetime.utcnow()
            
            # Emit health check event
            await self._emit_event("service_health_checked", {
                "service_id": service_id,
                "status": service.status.value,
                "timestamp": service.last_health_check.isoformat()
            })
            
        except Exception as e:
            logger.error(f"Health check failed for service {service_id}: {e}")
            if service_id in self.services:
                self.services[service_id].status = ServiceStatus.UNKNOWN
    
    async def _health_check_loop(self) -> None:
        """Background health check loop"""
        while not self._shutdown_event.is_set():
            try:
                # Check all registered services
                tasks = []
                for service_id in list(self.services.keys()):
                    task = asyncio.create_task(self._check_service_health(service_id))
                    tasks.append(task)
                
                if tasks:
                    await asyncio.gather(*tasks, return_exceptions=True)
                
                # Wait for next check
                await asyncio.sleep(self._health_check_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Health check loop error: {e}")
                await asyncio.sleep(5)  # Brief pause before retry
    
    async def _cleanup_loop(self) -> None:
        """Background cleanup loop for old executions"""
        while not self._shutdown_event.is_set():
            try:
                current_time = datetime.utcnow()
                cutoff_time = current_time - timedelta(hours=24)  # Keep 24 hours of history
                
                # Find old completed executions
                to_remove = []
                for execution_id, execution in self.executions.items():
                    if (execution.status in [WorkflowStatus.COMPLETED, WorkflowStatus.FAILED, WorkflowStatus.CANCELLED]
                        and execution.end_time 
                        and execution.end_time < cutoff_time):
                        to_remove.append(execution_id)
                
                # Remove old executions
                for execution_id in to_remove:
                    del self.executions[execution_id]
                    logger.info(f"Cleaned up old execution: {execution_id}")
                
                # Wait for next cleanup
                await asyncio.sleep(self._cleanup_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Cleanup loop error: {e}")
                await asyncio.sleep(300)  # 5 minute pause before retry
    
    async def _emit_event(self, event_type: str, event_data: Dict[str, Any]) -> None:
        """Emit an event to all registered handlers"""
        try:
            if event_type in self.event_handlers:
                tasks = []
                for handler in self.event_handlers[event_type]:
                    task = asyncio.create_task(handler(event_data))
                    tasks.append(task)
                
                if tasks:
                    await asyncio.gather(*tasks, return_exceptions=True)
            
        except Exception as e:
            logger.error(f"Error emitting event {event_type}: {e}")
    
    # Context Manager Support
    async def __aenter__(self):
        await self.start()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.stop()


# Factory function for easier instantiation
def create_platform_orchestrator() -> PlatformOrchestrationManager:
    """Factory function to create a Platform Orchestration Manager"""
    return PlatformOrchestrationManager()


# Example usage
async def main():
    """Example usage of Platform Orchestration Manager"""
    async with create_platform_orchestrator() as orchestrator:
        # Register some example services
        content_service = ServiceDefinition(
            service_id="content_service",
            name="Content Management Service",
            version="1.0.0",
            endpoints=["http://content-service:8080"]
        )
        
        ai_service = ServiceDefinition(
            service_id="ai_protection_service",
            name="AI Protection Service",
            version="1.0.0",
            endpoints=["http://ai-service:8080"]
        )
        
        await orchestrator.register_service(content_service)
        await orchestrator.register_service(ai_service)
        
        # Execute the creator content processing workflow
        execution_id = await orchestrator.execute_workflow("creator_content_processing")
        
        if execution_id:
            # Monitor execution
            while True:
                execution = await orchestrator.get_workflow_status(execution_id)
                if execution and execution.status in [WorkflowStatus.COMPLETED, WorkflowStatus.FAILED, WorkflowStatus.CANCELLED]:
                    print(f"Workflow completed with status: {execution.status}")
                    break
                await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())