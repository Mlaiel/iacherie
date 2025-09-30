"""Service Orchestration - IA Influencer Agent Platform
====================================================

Consolidated service orchestration for coordinating microservices, managing
distributed workflows, and ensuring system-wide service coordination.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Callable, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
import uuid
from collections import defaultdict

# Optional import for HTTP requests
try:
    import aiohttp
    AIOHTTP_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False

logger = logging.getLogger(__name__)


class ServiceType(Enum):
    """Types of services in the platform."""
    API_GATEWAY = "api_gateway"
    USER_SERVICE = "user_service"
    CONTENT_SERVICE = "content_service"
    PAYMENT_SERVICE = "payment_service"
    ANALYTICS_SERVICE = "analytics_service"
    NOTIFICATION_SERVICE = "notification_service"
    AI_SERVICE = "ai_service"
    STORAGE_SERVICE = "storage_service"
    SEARCH_SERVICE = "search_service"
    COLLABORATION_SERVICE = "collaboration_service"


class ServiceStatus(Enum):
    """Service status levels."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    OFFLINE = "offline"
    MAINTENANCE = "maintenance"


class OrchestrationStatus(Enum):
    """Orchestration task status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"


@dataclass
class ServiceDefinition:
    """Service definition and configuration."""
    service_id: str
    name: str
    service_type: ServiceType
    endpoint_url: str
    health_check_url: str
    version: str
    dependencies: List[str] = field(default_factory=list)
    capabilities: List[str] = field(default_factory=list)
    load_balancing: bool = True
    auto_scaling: bool = True
    min_instances: int = 1
    max_instances: int = 10
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ServiceInstance:
    """Individual service instance."""
    instance_id: str
    service_id: str
    endpoint_url: str
    status: ServiceStatus
    last_health_check: datetime = field(default_factory=datetime.utcnow)
    response_time: float = 0.0
    load: float = 0.0
    requests_per_minute: int = 0
    error_rate: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class OrchestrationTask:
    """Orchestration task definition."""
    task_id: str
    name: str
    workflow_id: str
    services_required: List[str]
    task_definition: Dict[str, Any]
    status: OrchestrationStatus = OrchestrationStatus.PENDING
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    retry_count: int = 0
    max_retries: int = 3
    results: Dict[str, Any] = field(default_factory=dict)
    error_details: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)


@dataclass
class DistributedWorkflow:
    """Distributed workflow definition."""
    workflow_id: str
    name: str
    description: str
    tasks: List[OrchestrationTask]
    status: OrchestrationStatus = OrchestrationStatus.PENDING
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_by: str = "system"
    metadata: Dict[str, Any] = field(default_factory=dict)


class ServiceOrchestrator:
    """
    Consolidated service orchestration engine for the IA Influencer platform.
    
    Manages microservices coordination, distributed workflows, service discovery,
    load balancing, and system-wide service orchestration.
    """
    
    def __init__(self):
        """Initialize the service orchestrator."""
        self.service_registry: Dict[str, ServiceDefinition] = {}
        self.service_instances: Dict[str, List[ServiceInstance]] = defaultdict(list)
        self.workflows: Dict[str, DistributedWorkflow] = {}
        self.task_queue: asyncio.Queue = asyncio.Queue()
        self.service_discovery: Dict[str, str] = {}  # service_name -> current_endpoint
        self.circuit_breakers: Dict[str, Dict[str, Any]] = {}
        self.is_orchestrating: bool = False
        self.logger = logging.getLogger(__name__)
        self._setup_default_services()
    
    def _setup_default_services(self):
        """Setup default service definitions."""
        default_services = [
            ServiceDefinition(
                service_id="api_gateway",
                name="API Gateway",
                service_type=ServiceType.API_GATEWAY,
                endpoint_url="http://localhost:8000",
                health_check_url="http://localhost:8000/health",
                version="1.0.0",
                dependencies=[],
                capabilities=["routing", "authentication", "rate_limiting"]
            ),
            ServiceDefinition(
                service_id="user_service",
                name="User Management Service",
                service_type=ServiceType.USER_SERVICE,
                endpoint_url="http://localhost:8001",
                health_check_url="http://localhost:8001/health",
                version="1.0.0",
                dependencies=["api_gateway"],
                capabilities=["user_registration", "authentication", "profile_management"]
            ),
            ServiceDefinition(
                service_id="content_service",
                name="Content Management Service",
                service_type=ServiceType.CONTENT_SERVICE,
                endpoint_url="http://localhost:8002",
                health_check_url="http://localhost:8002/health",
                version="1.0.0",
                dependencies=["user_service", "storage_service"],
                capabilities=["content_upload", "content_processing", "content_delivery"]
            ),
            ServiceDefinition(
                service_id="payment_service",
                name="Payment Processing Service",
                service_type=ServiceType.PAYMENT_SERVICE,
                endpoint_url="http://localhost:8003",
                health_check_url="http://localhost:8003/health",
                version="1.0.0",
                dependencies=["user_service"],
                capabilities=["payment_processing", "billing", "revenue_tracking"]
            ),
            ServiceDefinition(
                service_id="analytics_service",
                name="Analytics Service",
                service_type=ServiceType.ANALYTICS_SERVICE,
                endpoint_url="http://localhost:8004",
                health_check_url="http://localhost:8004/health",
                version="1.0.0",
                dependencies=["content_service", "user_service"],
                capabilities=["data_collection", "analytics_processing", "reporting"]
            ),
            ServiceDefinition(
                service_id="notification_service",
                name="Notification Service",
                service_type=ServiceType.NOTIFICATION_SERVICE,
                endpoint_url="http://localhost:8005",
                health_check_url="http://localhost:8005/health",
                version="1.0.0",
                dependencies=["user_service"],
                capabilities=["email_notifications", "push_notifications", "sms_notifications"]
            ),
            ServiceDefinition(
                service_id="ai_service",
                name="AI Processing Service",
                service_type=ServiceType.AI_SERVICE,
                endpoint_url="http://localhost:8006",
                health_check_url="http://localhost:8006/health",
                version="1.0.0",
                dependencies=["content_service"],
                capabilities=["content_analysis", "recommendation_engine", "ai_processing"]
            ),
            ServiceDefinition(
                service_id="storage_service",
                name="Storage Service",
                service_type=ServiceType.STORAGE_SERVICE,
                endpoint_url="http://localhost:8007",
                health_check_url="http://localhost:8007/health",
                version="1.0.0",
                dependencies=[],
                capabilities=["file_storage", "data_storage", "backup_management"]
            ),
            ServiceDefinition(
                service_id="collaboration_service",
                name="Collaboration Service",
                service_type=ServiceType.COLLABORATION_SERVICE,
                endpoint_url="http://localhost:8008",
                health_check_url="http://localhost:8008/health",
                version="1.0.0",
                dependencies=["user_service", "content_service"],
                capabilities=["collaboration_matching", "workflow_management", "revenue_sharing"]
            )
        ]
        
        for service in default_services:
            self.register_service(service)
    
    def register_service(self, service: ServiceDefinition) -> str:
        """Register a service with the orchestrator."""
        try:
            self.service_registry[service.service_id] = service
            self.service_discovery[service.name] = service.endpoint_url
            
            # Initialize circuit breaker for the service
            self.circuit_breakers[service.service_id] = {
                "state": "closed",  # closed, open, half_open
                "failure_count": 0,
                "last_failure_time": None,
                "success_count": 0,
                "threshold": 5,
                "timeout": 60  # seconds
            }
            
            self.logger.info(f"Registered service: {service.name} ({service.service_id})")
            return service.service_id
            
        except Exception as e:
            self.logger.error(f"Failed to register service {service.service_id}: {str(e)}")
            raise
    
    async def start_orchestration(self) -> None:
        """Start the service orchestration system."""
        try:
            self.is_orchestrating = True
            self.logger.info("Starting service orchestration system")
            
            # Start orchestration tasks
            await asyncio.gather(
                self._monitor_service_health(),
                self._process_task_queue(),
                self._manage_circuit_breakers(),
                self._auto_scale_services(),
                return_exceptions=True
            )
            
        except Exception as e:
            self.logger.error(f"Error starting orchestration: {str(e)}")
            self.is_orchestrating = False
            raise
    
    async def stop_orchestration(self) -> None:
        """Stop the service orchestration system."""
        try:
            self.is_orchestrating = False
            self.logger.info("Stopped service orchestration system")
        except Exception as e:
            self.logger.error(f"Error stopping orchestration: {str(e)}")
    
    async def _monitor_service_health(self) -> None:
        """Monitor health of all registered services."""
        while self.is_orchestrating:
            try:
                for service_id, service in self.service_registry.items():
                    await self._check_service_health(service_id)
                
                await asyncio.sleep(30)  # Check health every 30 seconds
                
            except Exception as e:
                self.logger.error(f"Error monitoring service health: {str(e)}")
                await asyncio.sleep(30)
    
    async def _check_service_health(self, service_id: str) -> None:
        """Check health of a specific service."""
        try:
            service = self.service_registry[service_id]
            circuit_breaker = self.circuit_breakers[service_id]
            
            # Skip health check if circuit breaker is open
            if circuit_breaker["state"] == "open":
                if datetime.utcnow().timestamp() - circuit_breaker["last_failure_time"] > circuit_breaker["timeout"]:
                    circuit_breaker["state"] = "half_open"
                else:
                    return
            
            start_time = datetime.utcnow()
            
            try:
                # Simulate health check (in real implementation, make HTTP request)
                await self._simulate_service_call(service.health_check_url)
                
                response_time = (datetime.utcnow() - start_time).total_seconds() * 1000
                
                # Update service instance or create if not exists
                if service_id not in self.service_instances or not self.service_instances[service_id]:
                    instance = ServiceInstance(
                        instance_id=f"{service_id}_instance_1",
                        service_id=service_id,
                        endpoint_url=service.endpoint_url,
                        status=ServiceStatus.HEALTHY,
                        response_time=response_time
                    )
                    self.service_instances[service_id].append(instance)
                else:
                    instance = self.service_instances[service_id][0]
                    instance.status = ServiceStatus.HEALTHY
                    instance.last_health_check = datetime.utcnow()
                    instance.response_time = response_time
                
                # Update circuit breaker
                circuit_breaker["failure_count"] = 0
                circuit_breaker["success_count"] += 1
                if circuit_breaker["state"] == "half_open":
                    circuit_breaker["state"] = "closed"
                
            except Exception as e:
                # Health check failed
                if self.service_instances[service_id]:
                    instance = self.service_instances[service_id][0]
                    instance.status = ServiceStatus.UNHEALTHY
                    instance.last_health_check = datetime.utcnow()
                
                # Update circuit breaker
                circuit_breaker["failure_count"] += 1
                circuit_breaker["last_failure_time"] = datetime.utcnow().timestamp()
                
                if circuit_breaker["failure_count"] >= circuit_breaker["threshold"]:
                    circuit_breaker["state"] = "open"
                    self.logger.warning(f"Circuit breaker opened for service: {service_id}")
                
                self.logger.error(f"Health check failed for service {service_id}: {str(e)}")
                
        except Exception as e:
            self.logger.error(f"Error checking health for service {service_id}: {str(e)}")
    
    async def _simulate_service_call(self, url: str) -> Dict[str, Any]:
        """Simulate a service call (in real implementation, use aiohttp)."""
        import random
        
        # Simulate some network delay
        await asyncio.sleep(random.uniform(0.01, 0.1))
        
        # Simulate occasional failures
        if random.random() < 0.05:  # 5% failure rate
            raise Exception("Service temporarily unavailable")
        
        return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}
    
    async def create_distributed_workflow(self, workflow_name: str, task_definitions: List[Dict[str, Any]]) -> str:
        """Create a new distributed workflow."""
        try:
            workflow_id = str(uuid.uuid4())
            
            # Create tasks from definitions
            tasks = []
            for i, task_def in enumerate(task_definitions):
                task = OrchestrationTask(
                    task_id=f"{workflow_id}_task_{i}",
                    name=task_def.get("name", f"Task {i}"),
                    workflow_id=workflow_id,
                    services_required=task_def.get("services_required", []),
                    task_definition=task_def,
                    dependencies=task_def.get("dependencies", [])
                )
                tasks.append(task)
            
            workflow = DistributedWorkflow(
                workflow_id=workflow_id,
                name=workflow_name,
                description=f"Distributed workflow with {len(tasks)} tasks",
                tasks=tasks
            )
            
            self.workflows[workflow_id] = workflow
            
            # Queue tasks for execution
            for task in tasks:
                await self.task_queue.put(task)
            
            self.logger.info(f"Created distributed workflow: {workflow_name} ({workflow_id})")
            return workflow_id
            
        except Exception as e:
            self.logger.error(f"Error creating distributed workflow: {str(e)}")
            raise
    
    async def _process_task_queue(self) -> None:
        """Process tasks from the orchestration queue."""
        while self.is_orchestrating:
            try:
                # Wait for task with timeout
                task = await asyncio.wait_for(self.task_queue.get(), timeout=1.0)
                
                # Execute task asynchronously
                asyncio.create_task(self._execute_orchestration_task(task))
                
            except asyncio.TimeoutError:
                # No tasks in queue, continue
                continue
            except Exception as e:
                self.logger.error(f"Error processing task queue: {str(e)}")
                await asyncio.sleep(1)
    
    async def _execute_orchestration_task(self, task: OrchestrationTask) -> None:
        """Execute an orchestration task."""
        try:
            task.status = OrchestrationStatus.RUNNING
            task.started_at = datetime.utcnow()
            
            # Check if all dependencies are completed
            if not await self._check_task_dependencies(task):
                # Re-queue task if dependencies not met
                await asyncio.sleep(5)
                await self.task_queue.put(task)
                return
            
            # Check if required services are available
            available_services = await self._check_service_availability(task.services_required)
            if not available_services:
                task.status = OrchestrationStatus.FAILED
                task.error_details = "Required services not available"
                task.completed_at = datetime.utcnow()
                return
            
            # Execute task based on its definition
            result = await self._execute_task_logic(task)
            
            task.results = result
            task.status = OrchestrationStatus.COMPLETED
            task.completed_at = datetime.utcnow()
            
            # Check if workflow is complete
            await self._check_workflow_completion(task.workflow_id)
            
            self.logger.info(f"Completed orchestration task: {task.name} ({task.task_id})")
            
        except Exception as e:
            task.status = OrchestrationStatus.FAILED
            task.error_details = str(e)
            task.completed_at = datetime.utcnow()
            
            # Retry logic
            if task.retry_count < task.max_retries:
                task.retry_count += 1
                task.status = OrchestrationStatus.RETRYING
                task.completed_at = None
                
                # Re-queue task for retry
                await asyncio.sleep(2 ** task.retry_count)  # Exponential backoff
                await self.task_queue.put(task)
                
                self.logger.warning(f"Retrying task: {task.name} (attempt {task.retry_count})")
            else:
                self.logger.error(f"Task failed after {task.max_retries} retries: {task.name} - {str(e)}")
    
    async def _check_task_dependencies(self, task: OrchestrationTask) -> bool:
        """Check if task dependencies are satisfied."""
        try:
            if not task.dependencies:
                return True
            
            workflow = self.workflows[task.workflow_id]
            
            for dep_task_id in task.dependencies:
                # Find dependency task
                dep_task = next((t for t in workflow.tasks if t.task_id == dep_task_id), None)
                
                if not dep_task or dep_task.status != OrchestrationStatus.COMPLETED:
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error checking task dependencies: {str(e)}")
            return False
    
    async def _check_service_availability(self, required_services: List[str]) -> bool:
        """Check if required services are available."""
        try:
            for service_id in required_services:
                if service_id not in self.service_instances:
                    return False
                
                # Check if at least one instance is healthy
                healthy_instances = [
                    instance for instance in self.service_instances[service_id]
                    if instance.status == ServiceStatus.HEALTHY
                ]
                
                if not healthy_instances:
                    return False
                
                # Check circuit breaker
                circuit_breaker = self.circuit_breakers.get(service_id, {})
                if circuit_breaker.get("state") == "open":
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error checking service availability: {str(e)}")
            return False
    
    async def _execute_task_logic(self, task: OrchestrationTask) -> Dict[str, Any]:
        """Execute the actual task logic."""
        try:
            task_type = task.task_definition.get("type", "generic")
            
            if task_type == "content_processing":
                return await self._execute_content_processing_task(task)
            elif task_type == "payment_processing":
                return await self._execute_payment_processing_task(task)
            elif task_type == "notification_sending":
                return await self._execute_notification_task(task)
            elif task_type == "analytics_calculation":
                return await self._execute_analytics_task(task)
            elif task_type == "collaboration_setup":
                return await self._execute_collaboration_task(task)
            else:
                return await self._execute_generic_task(task)
                
        except Exception as e:
            self.logger.error(f"Error executing task logic: {str(e)}")
            raise
    
    async def _execute_content_processing_task(self, task: OrchestrationTask) -> Dict[str, Any]:
        """Execute content processing task."""
        # Simulate content processing
        await asyncio.sleep(0.5)
        return {
            "task_type": "content_processing",
            "content_id": task.task_definition.get("content_id", "unknown"),
            "processing_status": "completed",
            "processing_time": 0.5,
            "services_used": task.services_required
        }
    
    async def _execute_payment_processing_task(self, task: OrchestrationTask) -> Dict[str, Any]:
        """Execute payment processing task."""
        await asyncio.sleep(0.3)
        return {
            "task_type": "payment_processing",
            "payment_id": task.task_definition.get("payment_id", "unknown"),
            "amount": task.task_definition.get("amount", 0),
            "status": "processed",
            "processing_time": 0.3
        }
    
    async def _execute_notification_task(self, task: OrchestrationTask) -> Dict[str, Any]:
        """Execute notification task."""
        await asyncio.sleep(0.2)
        return {
            "task_type": "notification_sending",
            "notification_type": task.task_definition.get("notification_type", "email"),
            "recipients": task.task_definition.get("recipients", []),
            "status": "sent",
            "processing_time": 0.2
        }
    
    async def _execute_analytics_task(self, task: OrchestrationTask) -> Dict[str, Any]:
        """Execute analytics task."""
        await asyncio.sleep(0.4)
        return {
            "task_type": "analytics_calculation",
            "metrics_calculated": task.task_definition.get("metrics", []),
            "data_points": task.task_definition.get("data_points", 1000),
            "status": "calculated",
            "processing_time": 0.4
        }
    
    async def _execute_collaboration_task(self, task: OrchestrationTask) -> Dict[str, Any]:
        """Execute collaboration task."""
        await asyncio.sleep(0.6)
        return {
            "task_type": "collaboration_setup",
            "collaboration_id": task.task_definition.get("collaboration_id", "unknown"),
            "participants": task.task_definition.get("participants", []),
            "status": "setup_completed",
            "processing_time": 0.6
        }
    
    async def _execute_generic_task(self, task: OrchestrationTask) -> Dict[str, Any]:
        """Execute generic task."""
        await asyncio.sleep(0.1)
        return {
            "task_type": "generic",
            "status": "completed",
            "processing_time": 0.1,
            "parameters": task.task_definition
        }
    
    async def _check_workflow_completion(self, workflow_id: str) -> None:
        """Check if workflow is complete."""
        try:
            workflow = self.workflows[workflow_id]
            
            completed_tasks = [t for t in workflow.tasks if t.status == OrchestrationStatus.COMPLETED]
            failed_tasks = [t for t in workflow.tasks if t.status == OrchestrationStatus.FAILED]
            
            if len(completed_tasks) == len(workflow.tasks):
                workflow.status = OrchestrationStatus.COMPLETED
                workflow.completed_at = datetime.utcnow()
                self.logger.info(f"Workflow completed: {workflow.name} ({workflow_id})")
            elif failed_tasks:
                # Check if any critical tasks failed
                critical_failures = [t for t in failed_tasks if t.retry_count >= t.max_retries]
                if critical_failures:
                    workflow.status = OrchestrationStatus.FAILED
                    workflow.completed_at = datetime.utcnow()
                    self.logger.error(f"Workflow failed: {workflow.name} ({workflow_id})")
            
        except Exception as e:
            self.logger.error(f"Error checking workflow completion: {str(e)}")
    
    async def _manage_circuit_breakers(self) -> None:
        """Manage circuit breakers for services."""
        while self.is_orchestrating:
            try:
                for service_id, circuit_breaker in self.circuit_breakers.items():
                    if circuit_breaker["state"] == "open":
                        # Check if enough time has passed to try half-open
                        if (datetime.utcnow().timestamp() - circuit_breaker["last_failure_time"] > 
                            circuit_breaker["timeout"]):
                            circuit_breaker["state"] = "half_open"
                            self.logger.info(f"Circuit breaker half-opened for service: {service_id}")
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                self.logger.error(f"Error managing circuit breakers: {str(e)}")
                await asyncio.sleep(30)
    
    async def _auto_scale_services(self) -> None:
        """Auto-scale services based on load."""
        while self.is_orchestrating:
            try:
                for service_id, service in self.service_registry.items():
                    if not service.auto_scaling:
                        continue
                    
                    instances = self.service_instances[service_id]
                    if not instances:
                        continue
                    
                    # Calculate average load
                    avg_load = sum(instance.load for instance in instances) / len(instances)
                    
                    # Scale up if load is high
                    if avg_load > 80 and len(instances) < service.max_instances:
                        await self._scale_up_service(service_id)
                    
                    # Scale down if load is low
                    elif avg_load < 20 and len(instances) > service.min_instances:
                        await self._scale_down_service(service_id)
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                self.logger.error(f"Error in auto-scaling: {str(e)}")
                await asyncio.sleep(60)
    
    async def _scale_up_service(self, service_id: str) -> None:
        """Scale up a service by adding instances."""
        try:
            service = self.service_registry[service_id]
            current_instances = len(self.service_instances[service_id])
            
            new_instance = ServiceInstance(
                instance_id=f"{service_id}_instance_{current_instances + 1}",
                service_id=service_id,
                endpoint_url=f"{service.endpoint_url.split(':')[0]}:{int(service.endpoint_url.split(':')[2]) + current_instances}",
                status=ServiceStatus.HEALTHY,
                load=0.0
            )
            
            self.service_instances[service_id].append(new_instance)
            self.logger.info(f"Scaled up service {service_id}: {current_instances} -> {current_instances + 1} instances")
            
        except Exception as e:
            self.logger.error(f"Error scaling up service {service_id}: {str(e)}")
    
    async def _scale_down_service(self, service_id: str) -> None:
        """Scale down a service by removing instances."""
        try:
            instances = self.service_instances[service_id]
            if len(instances) > 1:
                # Remove the last instance
                removed_instance = instances.pop()
                self.logger.info(f"Scaled down service {service_id}: removed instance {removed_instance.instance_id}")
            
        except Exception as e:
            self.logger.error(f"Error scaling down service {service_id}: {str(e)}")
    
    async def get_service_status(self, service_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific service."""
        try:
            if service_id not in self.service_registry:
                return None
            
            service = self.service_registry[service_id]
            instances = self.service_instances[service_id]
            circuit_breaker = self.circuit_breakers[service_id]
            
            return {
                "service_id": service_id,
                "name": service.name,
                "service_type": service.service_type.value,
                "version": service.version,
                "endpoint_url": service.endpoint_url,
                "dependencies": service.dependencies,
                "capabilities": service.capabilities,
                "instances": len(instances),
                "healthy_instances": len([i for i in instances if i.status == ServiceStatus.HEALTHY]),
                "circuit_breaker_state": circuit_breaker["state"],
                "circuit_breaker_failures": circuit_breaker["failure_count"],
                "avg_response_time": sum(i.response_time for i in instances) / len(instances) if instances else 0,
                "total_load": sum(i.load for i in instances),
                "last_health_check": max(i.last_health_check for i in instances).isoformat() if instances else None
            }
            
        except Exception as e:
            self.logger.error(f"Error getting service status: {str(e)}")
            return None
    
    async def get_workflow_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific workflow."""
        try:
            if workflow_id not in self.workflows:
                return None
            
            workflow = self.workflows[workflow_id]
            
            return {
                "workflow_id": workflow_id,
                "name": workflow.name,
                "description": workflow.description,
                "status": workflow.status.value,
                "started_at": workflow.started_at.isoformat() if workflow.started_at else None,
                "completed_at": workflow.completed_at.isoformat() if workflow.completed_at else None,
                "total_tasks": len(workflow.tasks),
                "completed_tasks": len([t for t in workflow.tasks if t.status == OrchestrationStatus.COMPLETED]),
                "failed_tasks": len([t for t in workflow.tasks if t.status == OrchestrationStatus.FAILED]),
                "running_tasks": len([t for t in workflow.tasks if t.status == OrchestrationStatus.RUNNING]),
                "tasks": [
                    {
                        "task_id": task.task_id,
                        "name": task.name,
                        "status": task.status.value,
                        "services_required": task.services_required,
                        "retry_count": task.retry_count,
                        "started_at": task.started_at.isoformat() if task.started_at else None,
                        "completed_at": task.completed_at.isoformat() if task.completed_at else None,
                        "error_details": task.error_details
                    } for task in workflow.tasks
                ]
            }
            
        except Exception as e:
            self.logger.error(f"Error getting workflow status: {str(e)}")
            return None
    
    async def get_orchestration_dashboard(self) -> Dict[str, Any]:
        """Get comprehensive orchestration dashboard."""
        try:
            # Service summary
            total_services = len(self.service_registry)
            healthy_services = len([
                s for s in self.service_instances.values()
                if any(i.status == ServiceStatus.HEALTHY for i in s)
            ])
            
            # Workflow summary
            total_workflows = len(self.workflows)
            active_workflows = len([w for w in self.workflows.values() if w.status == OrchestrationStatus.RUNNING])
            completed_workflows = len([w for w in self.workflows.values() if w.status == OrchestrationStatus.COMPLETED])
            
            # Circuit breaker summary
            open_circuit_breakers = len([cb for cb in self.circuit_breakers.values() if cb["state"] == "open"])
            
            # Task queue summary
            pending_tasks = self.task_queue.qsize()
            
            return {
                "orchestration_status": "active" if self.is_orchestrating else "inactive",
                "services_summary": {
                    "total_services": total_services,
                    "healthy_services": healthy_services,
                    "unhealthy_services": total_services - healthy_services,
                    "total_instances": sum(len(instances) for instances in self.service_instances.values()),
                    "service_types": list(set(s.service_type.value for s in self.service_registry.values()))
                },
                "workflows_summary": {
                    "total_workflows": total_workflows,
                    "active_workflows": active_workflows,
                    "completed_workflows": completed_workflows,
                    "failed_workflows": total_workflows - active_workflows - completed_workflows,
                    "pending_tasks": pending_tasks
                },
                "circuit_breakers": {
                    "total_breakers": len(self.circuit_breakers),
                    "open_breakers": open_circuit_breakers,
                    "closed_breakers": len(self.circuit_breakers) - open_circuit_breakers
                },
                "service_details": [
                    {
                        "service_id": service_id,
                        "name": service.name,
                        "status": "healthy" if any(i.status == ServiceStatus.HEALTHY for i in self.service_instances[service_id]) else "unhealthy",
                        "instances": len(self.service_instances[service_id]),
                        "circuit_breaker_state": self.circuit_breakers[service_id]["state"]
                    } for service_id, service in self.service_registry.items()
                ],
                "recent_workflows": [
                    {
                        "workflow_id": workflow.workflow_id,
                        "name": workflow.name,
                        "status": workflow.status.value,
                        "total_tasks": len(workflow.tasks),
                        "completed_tasks": len([t for t in workflow.tasks if t.status == OrchestrationStatus.COMPLETED])
                    } for workflow in sorted(self.workflows.values(), key=lambda w: w.started_at or datetime.min, reverse=True)[:5]
                ],
                "last_updated": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting orchestration dashboard: {str(e)}")
            return {"error": str(e)}
    
    def get_orchestration_summary(self) -> Dict[str, Any]:
        """Get summary of orchestration system."""
        try:
            return {
                "is_orchestrating": self.is_orchestrating,
                "total_services": len(self.service_registry),
                "total_workflows": len(self.workflows),
                "total_service_instances": sum(len(instances) for instances in self.service_instances.values()),
                "service_types": [st.value for st in ServiceType],
                "orchestration_statuses": [os.value for os in OrchestrationStatus],
                "services_by_type": {
                    st.value: len([s for s in self.service_registry.values() if s.service_type == st])
                    for st in ServiceType
                },
                "workflows_by_status": {
                    status.value: len([w for w in self.workflows.values() if w.status == status])
                    for status in OrchestrationStatus
                },
                "circuit_breakers_by_state": {
                    "open": len([cb for cb in self.circuit_breakers.values() if cb["state"] == "open"]),
                    "closed": len([cb for cb in self.circuit_breakers.values() if cb["state"] == "closed"]),
                    "half_open": len([cb for cb in self.circuit_breakers.values() if cb["state"] == "half_open"])
                }
            }
        except Exception as e:
            self.logger.error(f"Error getting orchestration summary: {str(e)}")
            return {}