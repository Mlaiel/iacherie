"""
Orchestration Controller - Master Orchestration Control System

Enterprise-grade orchestration controller providing centralized management,
monitoring, and coordination of all content processing workflows with
intelligent resource allocation and performance optimization.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL WARNING:
This code is the EXCLUSIVE INTELLECTUAL PROPERTY of Fahed Mlaiel.
Unauthorized use, copying, or distribution is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Union, Set
from dataclasses import dataclass, field
from enum import Enum
import uuid
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

from backend.core.orchestration.workflow_engine import (
    WorkflowEngine, WorkflowDefinition, WorkflowStatus, ExecutionMode
)
from backend.core.orchestration.pipeline_coordinator import PipelineCoordinator
from backend.core.orchestration.task_scheduler import TaskScheduler
from backend.core.orchestration.resource_manager import ResourceManager
from backend.core.orchestration.performance_optimizer import PerformanceOptimizer
from backend.core.orchestration.pipeline_builder import PipelineBuilder
from backend.core.orchestration.metrics_collector import MetricsCollector
from backend.core.orchestration.error_handler import ErrorHandler


class OrchestrationMode(Enum):
    """Orchestration operation modes."""
    NORMAL = "normal"
    HIGH_PERFORMANCE = "high_performance"
    BATCH_PROCESSING = "batch_processing"
    REAL_TIME = "real_time"
    MAINTENANCE = "maintenance"
    EMERGENCY = "emergency"


class Priority(Enum):
    """Workflow execution priority levels."""
    CRITICAL = 1
    HIGH = 2
    NORMAL = 3
    LOW = 4
    BACKGROUND = 5


@dataclass
class OrchestrationConfig:
    """Orchestration system configuration."""
    mode: OrchestrationMode = OrchestrationMode.NORMAL
    max_concurrent_workflows: int = 50
    max_concurrent_tasks: int = 200
    default_timeout: int = 3600
    retry_policy: Dict[str, Any] = field(default_factory=lambda: {
        "max_retries": 3,
        "retry_delay": 15,
        "exponential_backoff": True
    })
    resource_limits: Dict[str, Any] = field(default_factory=lambda: {
        "cpu_cores": 8,
        "memory_gb": 32,
        "storage_gb": 1000
    })
    monitoring_config: Dict[str, Any] = field(default_factory=lambda: {
        "metrics_interval": 30,
        "health_check_interval": 60,
        "alert_thresholds": {
            "error_rate": 0.05,
            "response_time": 30,
            "resource_usage": 0.8
        }
    })


@dataclass
class WorkflowRequest:
    """Workflow execution request."""
    request_id: str
    workflow_name: str
    template_id: Optional[str] = None
    workflow_definition: Optional[WorkflowDefinition] = None
    priority: Priority = Priority.NORMAL
    parameters: Dict[str, Any] = field(default_factory=dict)
    context: Dict[str, Any] = field(default_factory=dict)
    timeout: Optional[int] = None
    retry_policy: Optional[Dict[str, Any]] = None
    user_id: Optional[str] = None
    tenant_id: Optional[str] = None
    callback_url: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class OrchestrationMetrics:
    """System orchestration metrics."""
    active_workflows: int
    completed_workflows: int
    failed_workflows: int
    queued_requests: int
    average_execution_time: float
    success_rate: float
    resource_utilization: Dict[str, float]
    throughput: float
    error_rate: float
    last_updated: datetime


class OrchestrationController:
    """
    Master Orchestration Controller for IA Influencer Agent Platform.
    
    Features:
    - Centralized workflow management
    - Intelligent resource allocation
    - Performance optimization
    - Real-time monitoring
    - Multi-tenant support
    - Priority-based scheduling
    - Fault tolerance and recovery
    """

    def __init__(
        self,
        config: Optional[OrchestrationConfig] = None,
        logger: Optional[logging.Logger] = None
    ):
        """Initialize the orchestration controller."""
        self.config = config or OrchestrationConfig()
        self.logger = logger or logging.getLogger(__name__)
        
        # Initialize core components
        self.workflow_engine = WorkflowEngine()
        self.pipeline_coordinator = PipelineCoordinator()
        self.task_scheduler = TaskScheduler()
        self.resource_manager = ResourceManager()
        self.performance_optimizer = PerformanceOptimizer()
        self.pipeline_builder = PipelineBuilder()
        self.metrics_collector = MetricsCollector()
        self.error_handler = ErrorHandler()
        
        # State management
        self.active_workflows: Dict[str, WorkflowDefinition] = {}
        self.workflow_requests: Dict[str, WorkflowRequest] = {}
        self.execution_queue: List[WorkflowRequest] = []
        self.priority_queues: Dict[Priority, List[WorkflowRequest]] = {
            priority: [] for priority in Priority
        }
        
        # Performance tracking
        self.metrics_history: List[OrchestrationMetrics] = []
        self.executor = ThreadPoolExecutor(max_workers=self.config.max_concurrent_workflows)
        
        # Initialize system
        self._initialize_system()

    def _initialize_system(self):
        """Initialize orchestration system components."""
        try:
            # Configure resource limits
            self.resource_manager.configure_limits(self.config.resource_limits)
            
            # Set up monitoring
            self._setup_monitoring()
            
            # Initialize performance optimizer
            self.performance_optimizer.initialize()
            
            # Load pipeline templates
            self._load_pipeline_templates()
            
            self.logger.info("Orchestration controller initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize orchestration controller: {str(e)}")
            raise

    def _setup_monitoring(self):
        """Set up system monitoring and health checks."""
        # Configure metrics collection
        self.metrics_collector.configure(self.config.monitoring_config)
        
        # Set up periodic health checks
        asyncio.create_task(self._health_check_loop())
        asyncio.create_task(self._metrics_collection_loop())

    def _load_pipeline_templates(self):
        """Load default pipeline templates."""
        # This would load predefined templates from configuration or database
        # For now, the PipelineBuilder handles template initialization
        pass

    async def submit_workflow(self, request: WorkflowRequest) -> str:
        """
        Submit a workflow for execution.
        
        Args:
            request: Workflow execution request
            
        Returns:
            str: Execution ID for tracking
        """
        try:
            execution_id = str(uuid.uuid4())
            request.metadata["execution_id"] = execution_id
            request.metadata["submitted_at"] = datetime.utcnow().isoformat()
            
            # Validate request
            self._validate_workflow_request(request)
            
            # Store request
            self.workflow_requests[execution_id] = request
            
            # Add to appropriate priority queue
            self.priority_queues[request.priority].append(request)
            
            # Schedule for execution
            await self._schedule_workflow_execution(request)
            
            self.logger.info(
                f"Workflow submitted: {request.workflow_name} (ID: {execution_id})"
            )
            
            return execution_id
            
        except Exception as e:
            self.logger.error(f"Failed to submit workflow: {str(e)}")
            raise

    def _validate_workflow_request(self, request: WorkflowRequest):
        """Validate workflow request parameters."""
        if not request.workflow_name:
            raise ValueError("Workflow name is required")
        
        if not request.template_id and not request.workflow_definition:
            raise ValueError("Either template_id or workflow_definition must be provided")
        
        # Additional validation logic
        if request.timeout and request.timeout > self.config.default_timeout * 2:
            raise ValueError(f"Timeout exceeds maximum allowed: {self.config.default_timeout * 2}")

    async def _schedule_workflow_execution(self, request: WorkflowRequest):
        """Schedule workflow for execution based on priority and resources."""
        try:
            # Check resource availability
            if not await self._check_resource_availability(request):
                self.logger.warning(f"Insufficient resources for workflow {request.request_id}")
                return
            
            # Create or retrieve workflow definition
            workflow = await self._prepare_workflow_definition(request)
            
            # Execute workflow
            await self._execute_workflow(workflow, request)
            
        except Exception as e:
            self.logger.error(f"Failed to schedule workflow execution: {str(e)}")
            await self._handle_execution_error(request, e)

    async def _check_resource_availability(self, request: WorkflowRequest) -> bool:
        """Check if sufficient resources are available for workflow execution."""
        return await self.resource_manager.check_availability(
            cpu_required=request.metadata.get("cpu_cores", 1),
            memory_required=request.metadata.get("memory_mb", 1024),
            storage_required=request.metadata.get("storage_mb", 100)
        )

    async def _prepare_workflow_definition(self, request: WorkflowRequest) -> WorkflowDefinition:
        """Prepare workflow definition from request."""
        if request.workflow_definition:
            return request.workflow_definition
        
        if request.template_id:
            # Build workflow from template
            workflow = self.pipeline_builder.create_pipeline(
                pipeline_name=request.workflow_name,
                template_id=request.template_id,
                custom_config=request.parameters
            )
            
            # Apply request-specific settings
            if request.timeout:
                workflow.timeout = request.timeout
            
            if request.retry_policy:
                workflow.max_retries = request.retry_policy.get("max_retries", 3)
                workflow.retry_delay = request.retry_policy.get("retry_delay", 15)
            
            # Add request metadata
            workflow.metadata.update({
                "request_id": request.request_id,
                "user_id": request.user_id,
                "tenant_id": request.tenant_id,
                "priority": request.priority.value,
                "context": request.context
            })
            
            return workflow
        
        raise ValueError("No workflow definition or template provided")

    async def _execute_workflow(self, workflow: WorkflowDefinition, request: WorkflowRequest):
        """Execute workflow with monitoring and error handling."""
        try:
            # Add to active workflows
            self.active_workflows[workflow.workflow_id] = workflow
            
            # Start execution
            execution_task = asyncio.create_task(
                self.workflow_engine.execute_workflow(workflow)
            )
            
            # Monitor execution
            await self._monitor_workflow_execution(workflow, execution_task, request)
            
        except Exception as e:
            self.logger.error(f"Workflow execution failed: {str(e)}")
            await self._handle_execution_error(request, e)
        finally:
            # Clean up
            if workflow.workflow_id in self.active_workflows:
                del self.active_workflows[workflow.workflow_id]

    async def _monitor_workflow_execution(
        self,
        workflow: WorkflowDefinition,
        execution_task: asyncio.Task,
        request: WorkflowRequest
    ):
        """Monitor workflow execution progress and handle completion."""
        try:
            # Wait for completion with timeout
            timeout = workflow.timeout or self.config.default_timeout
            result = await asyncio.wait_for(execution_task, timeout=timeout)
            
            # Handle successful completion
            await self._handle_workflow_completion(workflow, request, result)
            
        except asyncio.TimeoutError:
            # Handle timeout
            self.logger.warning(f"Workflow {workflow.workflow_id} timed out")
            execution_task.cancel()
            await self._handle_workflow_timeout(workflow, request)
            
        except Exception as e:
            # Handle execution error
            self.logger.error(f"Workflow execution error: {str(e)}")
            await self._handle_execution_error(request, e)

    async def _handle_workflow_completion(
        self,
        workflow: WorkflowDefinition,
        request: WorkflowRequest,
        result: Any
    ):
        """Handle successful workflow completion."""
        try:
            # Update metrics
            self.metrics_collector.record_workflow_completion(
                workflow_id=workflow.workflow_id,
                execution_time=datetime.utcnow().timestamp() - 
                               datetime.fromisoformat(request.metadata["submitted_at"]).timestamp(),
                success=True
            )
            
            # Send callback if configured
            if request.callback_url:
                await self._send_completion_callback(request, result, success=True)
            
            # Clean up resources
            await self.resource_manager.release_workflow_resources(workflow.workflow_id)
            
            self.logger.info(f"Workflow completed successfully: {workflow.workflow_id}")
            
        except Exception as e:
            self.logger.error(f"Error handling workflow completion: {str(e)}")

    async def _handle_workflow_timeout(self, workflow: WorkflowDefinition, request: WorkflowRequest):
        """Handle workflow timeout."""
        try:
            # Update metrics
            self.metrics_collector.record_workflow_completion(
                workflow_id=workflow.workflow_id,
                execution_time=workflow.timeout or self.config.default_timeout,
                success=False,
                error_type="timeout"
            )
            
            # Send callback if configured
            if request.callback_url:
                await self._send_completion_callback(
                    request, 
                    {"error": "Workflow execution timed out"}, 
                    success=False
                )
            
            # Clean up resources
            await self.resource_manager.release_workflow_resources(workflow.workflow_id)
            
        except Exception as e:
            self.logger.error(f"Error handling workflow timeout: {str(e)}")

    async def _handle_execution_error(self, request: WorkflowRequest, error: Exception):
        """Handle workflow execution error."""
        try:
            # Record error metrics
            self.metrics_collector.record_error(
                error_type=type(error).__name__,
                context={
                    "request_id": request.request_id,
                    "workflow_name": request.workflow_name
                }
            )
            
            # Send error callback if configured
            if request.callback_url:
                await self._send_completion_callback(
                    request,
                    {"error": str(error)},
                    success=False
                )
            
        except Exception as e:
            self.logger.error(f"Error handling execution error: {str(e)}")

    async def _send_completion_callback(
        self,
        request: WorkflowRequest,
        result: Any,
        success: bool
    ):
        """Send workflow completion callback."""
        # This would implement HTTP callback to the specified URL
        # For now, just log the callback
        self.logger.info(
            f"Callback for {request.request_id}: success={success}, result={result}"
        )

    async def get_workflow_status(self, execution_id: str) -> Dict[str, Any]:
        """Get current status of a workflow execution."""
        try:
            if execution_id not in self.workflow_requests:
                raise ValueError(f"Workflow execution {execution_id} not found")
            
            request = self.workflow_requests[execution_id]
            
            # Find corresponding active workflow
            active_workflow = None
            for workflow_id, workflow in self.active_workflows.items():
                if workflow.metadata.get("request_id") == execution_id:
                    active_workflow = workflow
                    break
            
            status = {
                "execution_id": execution_id,
                "workflow_name": request.workflow_name,
                "priority": request.priority.value,
                "submitted_at": request.metadata.get("submitted_at"),
                "status": "queued" if not active_workflow else "running",
                "progress": 0.0
            }
            
            if active_workflow:
                # Get detailed execution status from workflow engine
                execution_status = await self.workflow_engine.get_workflow_status(
                    active_workflow.workflow_id
                )
                status.update(execution_status)
            
            return status
            
        except Exception as e:
            self.logger.error(f"Failed to get workflow status: {str(e)}")
            raise

    async def cancel_workflow(self, execution_id: str) -> bool:
        """Cancel a workflow execution."""
        try:
            if execution_id not in self.workflow_requests:
                raise ValueError(f"Workflow execution {execution_id} not found")
            
            # Remove from queue if not started
            request = self.workflow_requests[execution_id]
            for priority_queue in self.priority_queues.values():
                if request in priority_queue:
                    priority_queue.remove(request)
                    self.logger.info(f"Cancelled queued workflow: {execution_id}")
                    return True
            
            # Cancel active execution
            for workflow_id, workflow in self.active_workflows.items():
                if workflow.metadata.get("request_id") == execution_id:
                    success = await self.workflow_engine.cancel_workflow(workflow_id)
                    if success:
                        self.logger.info(f"Cancelled active workflow: {execution_id}")
                    return success
            
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to cancel workflow: {str(e)}")
            raise

    async def pause_workflow(self, execution_id: str) -> bool:
        """Pause a workflow execution."""
        try:
            # Find and pause active workflow
            for workflow_id, workflow in self.active_workflows.items():
                if workflow.metadata.get("request_id") == execution_id:
                    success = await self.workflow_engine.pause_workflow(workflow_id)
                    if success:
                        self.logger.info(f"Paused workflow: {execution_id}")
                    return success
            
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to pause workflow: {str(e)}")
            raise

    async def resume_workflow(self, execution_id: str) -> bool:
        """Resume a paused workflow execution."""
        try:
            # Find and resume paused workflow
            for workflow_id, workflow in self.active_workflows.items():
                if workflow.metadata.get("request_id") == execution_id:
                    success = await self.workflow_engine.resume_workflow(workflow_id)
                    if success:
                        self.logger.info(f"Resumed workflow: {execution_id}")
                    return success
            
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to resume workflow: {str(e)}")
            raise

    async def list_active_workflows(self) -> List[Dict[str, Any]]:
        """List all currently active workflows."""
        try:
            active_list = []
            
            for workflow_id, workflow in self.active_workflows.items():
                status = await self.workflow_engine.get_workflow_status(workflow_id)
                
                active_list.append({
                    "workflow_id": workflow_id,
                    "name": workflow.name,
                    "execution_id": workflow.metadata.get("request_id"),
                    "user_id": workflow.metadata.get("user_id"),
                    "tenant_id": workflow.metadata.get("tenant_id"),
                    "priority": workflow.metadata.get("priority"),
                    "status": status.get("status"),
                    "progress": status.get("progress", 0.0),
                    "start_time": status.get("start_time")
                })
            
            return active_list
            
        except Exception as e:
            self.logger.error(f"Failed to list active workflows: {str(e)}")
            raise

    async def get_system_metrics(self) -> OrchestrationMetrics:
        """Get current system orchestration metrics."""
        try:
            # Collect current metrics
            current_metrics = OrchestrationMetrics(
                active_workflows=len(self.active_workflows),
                completed_workflows=self.metrics_collector.get_completed_count(),
                failed_workflows=self.metrics_collector.get_failed_count(),
                queued_requests=sum(len(queue) for queue in self.priority_queues.values()),
                average_execution_time=self.metrics_collector.get_average_execution_time(),
                success_rate=self.metrics_collector.get_success_rate(),
                resource_utilization=await self.resource_manager.get_utilization_metrics(),
                throughput=self.metrics_collector.get_throughput(),
                error_rate=self.metrics_collector.get_error_rate(),
                last_updated=datetime.utcnow()
            )
            
            # Store in history
            self.metrics_history.append(current_metrics)
            
            # Keep only last 100 entries
            if len(self.metrics_history) > 100:
                self.metrics_history = self.metrics_history[-100:]
            
            return current_metrics
            
        except Exception as e:
            self.logger.error(f"Failed to get system metrics: {str(e)}")
            raise

    async def optimize_performance(self) -> Dict[str, Any]:
        """Trigger performance optimization across the system."""
        try:
            optimization_results = {}
            
            # Optimize resource allocation
            resource_optimization = await self.resource_manager.optimize_allocation()
            optimization_results["resource_optimization"] = resource_optimization
            
            # Optimize workflow scheduling
            scheduling_optimization = await self.task_scheduler.optimize_scheduling()
            optimization_results["scheduling_optimization"] = scheduling_optimization
            
            # Apply performance tuning
            performance_optimization = await self.performance_optimizer.optimize()
            optimization_results["performance_optimization"] = performance_optimization
            
            self.logger.info("Performance optimization completed")
            return optimization_results
            
        except Exception as e:
            self.logger.error(f"Performance optimization failed: {str(e)}")
            raise

    async def _health_check_loop(self):
        """Periodic health check loop."""
        while True:
            try:
                await asyncio.sleep(self.config.monitoring_config["health_check_interval"])
                
                # Check system health
                health_status = await self._check_system_health()
                
                # Take action if needed
                if not health_status["healthy"]:
                    await self._handle_health_issues(health_status)
                
            except Exception as e:
                self.logger.error(f"Health check loop error: {str(e)}")

    async def _metrics_collection_loop(self):
        """Periodic metrics collection loop."""
        while True:
            try:
                await asyncio.sleep(self.config.monitoring_config["metrics_interval"])
                
                # Collect and store metrics
                await self.get_system_metrics()
                
            except Exception as e:
                self.logger.error(f"Metrics collection loop error: {str(e)}")

    async def _check_system_health(self) -> Dict[str, Any]:
        """Check overall system health."""
        health_status = {
            "healthy": True,
            "issues": [],
            "metrics": {}
        }
        
        try:
            # Check resource utilization
            utilization = await self.resource_manager.get_utilization_metrics()
            for resource, usage in utilization.items():
                if usage > self.config.monitoring_config["alert_thresholds"]["resource_usage"]:
                    health_status["healthy"] = False
                    health_status["issues"].append(f"High {resource} usage: {usage:.2%}")
            
            # Check error rate
            error_rate = self.metrics_collector.get_error_rate()
            if error_rate > self.config.monitoring_config["alert_thresholds"]["error_rate"]:
                health_status["healthy"] = False
                health_status["issues"].append(f"High error rate: {error_rate:.2%}")
            
            # Check response time
            avg_response_time = self.metrics_collector.get_average_execution_time()
            if avg_response_time > self.config.monitoring_config["alert_thresholds"]["response_time"]:
                health_status["healthy"] = False
                health_status["issues"].append(f"High response time: {avg_response_time:.2f}s")
            
            health_status["metrics"] = {
                "resource_utilization": utilization,
                "error_rate": error_rate,
                "avg_response_time": avg_response_time
            }
            
        except Exception as e:
            health_status["healthy"] = False
            health_status["issues"].append(f"Health check error: {str(e)}")
        
        return health_status

    async def _handle_health_issues(self, health_status: Dict[str, Any]):
        """Handle detected health issues."""
        self.logger.warning(f"Health issues detected: {health_status['issues']}")
        
        # Trigger optimization if needed
        if len(health_status["issues"]) > 2:
            await self.optimize_performance()
        
        # Scale resources if possible
        if any("usage" in issue for issue in health_status["issues"]):
            await self.resource_manager.scale_resources()

    async def shutdown(self):
        """Gracefully shutdown the orchestration controller."""
        try:
            self.logger.info("Shutting down orchestration controller...")
            
            # Cancel all active workflows
            for workflow_id in list(self.active_workflows.keys()):
                await self.workflow_engine.cancel_workflow(workflow_id)
            
            # Shutdown executor
            self.executor.shutdown(wait=True)
            
            # Clean up resources
            await self.resource_manager.cleanup()
            
            self.logger.info("Orchestration controller shutdown complete")
            
        except Exception as e:
            self.logger.error(f"Error during shutdown: {str(e)}")

    def get_configuration(self) -> OrchestrationConfig:
        """Get current orchestration configuration."""
        return self.config

    async def update_configuration(self, new_config: OrchestrationConfig):
        """Update orchestration configuration."""
        try:
            old_config = self.config
            self.config = new_config
            
            # Apply configuration changes
            await self._apply_configuration_changes(old_config, new_config)
            
            self.logger.info("Configuration updated successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to update configuration: {str(e)}")
            self.config = old_config  # Rollback
            raise

    async def _apply_configuration_changes(
        self,
        old_config: OrchestrationConfig,
        new_config: OrchestrationConfig
    ):
        """Apply configuration changes to system components."""
        # Update resource limits
        if old_config.resource_limits != new_config.resource_limits:
            self.resource_manager.configure_limits(new_config.resource_limits)
        
        # Update monitoring configuration
        if old_config.monitoring_config != new_config.monitoring_config:
            self.metrics_collector.configure(new_config.monitoring_config)
        
        # Update executor if max workers changed
        if old_config.max_concurrent_workflows != new_config.max_concurrent_workflows:
            self.executor.shutdown(wait=False)
            self.executor = ThreadPoolExecutor(max_workers=new_config.max_concurrent_workflows)
