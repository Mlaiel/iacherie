"""Monetization Workflow Manager - Automated Monetization Process Management
========================================================================

Enterprise-grade monetization workflow manager providing automated
workflow orchestration, process management, and monetization pipeline
coordination for content creators across all platforms.

Architecture: Enterprise Production-Ready (Backend Level 3)
Module: backend/monetization/monetization_workflow_manager.py

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Callable
from uuid import uuid4, UUID
from decimal import Decimal
from enum import Enum
from dataclasses import dataclass, field
import json

logger = logging.getLogger(__name__)


class WorkflowType(str, Enum):
    """Monetization workflow types."""
    CONTENT_UPLOAD = "content_upload"
    REVENUE_OPTIMIZATION = "revenue_optimization"
    PLATFORM_DISTRIBUTION = "platform_distribution"
    PAYOUT_PROCESSING = "payout_processing"
    COPYRIGHT_MONETIZATION = "copyright_monetization"
    COLLABORATION_REVENUE = "collaboration_revenue"
    GAMIFICATION_REWARDS = "gamification_rewards"
    SEO_OPTIMIZATION = "seo_optimization"
    ANALYTICS_PROCESSING = "analytics_processing"


class WorkflowStatus(str, Enum):
    """Workflow execution status."""
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


class StepStatus(str, Enum):
    """Individual step execution status."""
    WAITING = "waiting"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    RETRY = "retry"


class Priority(str, Enum):
    """Workflow priority levels."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"
    CRITICAL = "critical"


@dataclass
class WorkflowStep:
    """Individual workflow step definition."""
    step_id: str
    step_name: str
    step_type: str
    function: Optional[Callable] = None
    dependencies: List[str] = field(default_factory=list)
    timeout_seconds: int = 300
    retry_count: int = 3
    retry_delay: int = 60
    required: bool = True
    parameters: Dict[str, Any] = field(default_factory=dict)
    status: StepStatus = StepStatus.WAITING
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    error_message: Optional[str] = None
    result_data: Dict[str, Any] = field(default_factory=dict)
    attempt_count: int = 0


@dataclass
class WorkflowDefinition:
    """Workflow definition with steps and configuration."""
    workflow_id: str
    workflow_name: str
    workflow_type: WorkflowType
    description: str
    steps: List[WorkflowStep]
    priority: Priority = Priority.NORMAL
    timeout_minutes: int = 60
    max_parallel_steps: int = 5
    auto_retry: bool = True
    notification_enabled: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkflowExecution:
    """Workflow execution instance tracking."""
    execution_id: str
    workflow_id: str
    creator_id: str
    content_id: Optional[str] = None
    status: WorkflowStatus = WorkflowStatus.PENDING
    priority: Priority = Priority.NORMAL
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    total_steps: int = 0
    completed_steps: int = 0
    failed_steps: int = 0
    execution_context: Dict[str, Any] = field(default_factory=dict)
    step_results: Dict[str, Any] = field(default_factory=dict)
    error_log: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)


class MonetizationWorkflowManager:
    """
    Advanced monetization workflow manager providing automated
    workflow orchestration and process management.
    """
    
    def __init__(self):
        """Initialize the monetization workflow manager."""
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.workflow_definitions: Dict[str, WorkflowDefinition] = {}
        self.executions: Dict[str, WorkflowExecution] = {}
        self.step_functions: Dict[str, Callable] = {}
        self.execution_queue: asyncio.Queue = asyncio.Queue()
        self.running_executions: Dict[str, asyncio.Task] = {}
        self.max_concurrent_workflows: int = 10
        self.is_running: bool = False
        
        # Initialize default workflows
        self._initialize_default_workflows()
        
        self.logger.info("MonetizationWorkflowManager initialized")
    
    def _initialize_default_workflows(self):
        """Initialize default monetization workflows."""
        # Content Upload Monetization Workflow
        content_upload_steps = [
            WorkflowStep(
                step_id="analyze_content",
                step_name="Analyze Content Monetization",
                step_type="content_analysis",
                timeout_seconds=120,
                parameters={"enable_ai": True}
            ),
            WorkflowStep(
                step_id="optimize_metadata",
                step_name="Optimize Content Metadata",
                step_type="metadata_optimization",
                dependencies=["analyze_content"],
                timeout_seconds=60
            ),
            WorkflowStep(
                step_id="setup_revenue_streams",
                step_name="Setup Revenue Streams",
                step_type="revenue_setup",
                dependencies=["analyze_content"],
                timeout_seconds=90
            ),
            WorkflowStep(
                step_id="distribute_platforms",
                step_name="Distribute to Platforms",
                step_type="platform_distribution",
                dependencies=["optimize_metadata", "setup_revenue_streams"],
                timeout_seconds=300
            ),
            WorkflowStep(
                step_id="enable_monetization",
                step_name="Enable Platform Monetization",
                step_type="monetization_activation",
                dependencies=["distribute_platforms"],
                timeout_seconds=180
            )
        ]
        
        content_upload_workflow = WorkflowDefinition(
            workflow_id="content_upload_monetization",
            workflow_name="Content Upload Monetization",
            workflow_type=WorkflowType.CONTENT_UPLOAD,
            description="Automated monetization setup for newly uploaded content",
            steps=content_upload_steps,
            priority=Priority.HIGH,
            timeout_minutes=30
        )
        
        self.workflow_definitions["content_upload_monetization"] = content_upload_workflow
        
        # Revenue Optimization Workflow
        revenue_optimization_steps = [
            WorkflowStep(
                step_id="analyze_performance",
                step_name="Analyze Content Performance",
                step_type="performance_analysis",
                timeout_seconds=90
            ),
            WorkflowStep(
                step_id="identify_opportunities",
                step_name="Identify Optimization Opportunities",
                step_type="opportunity_identification",
                dependencies=["analyze_performance"],
                timeout_seconds=120
            ),
            WorkflowStep(
                step_id="optimize_pricing",
                step_name="Optimize Pricing Strategy",
                step_type="pricing_optimization",
                dependencies=["identify_opportunities"],
                timeout_seconds=60
            ),
            WorkflowStep(
                step_id="update_platforms",
                step_name="Update Platform Settings",
                step_type="platform_update",
                dependencies=["optimize_pricing"],
                timeout_seconds=180
            ),
            WorkflowStep(
                step_id="track_results",
                step_name="Track Optimization Results",
                step_type="result_tracking",
                dependencies=["update_platforms"],
                timeout_seconds=30
            )
        ]
        
        revenue_optimization_workflow = WorkflowDefinition(
            workflow_id="revenue_optimization",
            workflow_name="Revenue Optimization",
            workflow_type=WorkflowType.REVENUE_OPTIMIZATION,
            description="Automated revenue optimization based on performance data",
            steps=revenue_optimization_steps,
            priority=Priority.NORMAL,
            timeout_minutes=20
        )
        
        self.workflow_definitions["revenue_optimization"] = revenue_optimization_workflow
    
    def register_step_function(self, step_type: str, function: Callable):
        """Register a function to handle a specific step type."""
        self.step_functions[step_type] = function
        self.logger.info(f"Registered step function for type: {step_type}")
    
    async def create_workflow_execution(
        self,
        workflow_id: str,
        creator_id: str,
        content_id: Optional[str] = None,
        priority: Priority = Priority.NORMAL,
        context: Dict[str, Any] = None
    ) -> str:
        """Create a new workflow execution."""
        try:
            if workflow_id not in self.workflow_definitions:
                raise ValueError(f"Workflow definition not found: {workflow_id}")
            
            workflow_def = self.workflow_definitions[workflow_id]
            execution_id = str(uuid4())
            
            execution = WorkflowExecution(
                execution_id=execution_id,
                workflow_id=workflow_id,
                creator_id=creator_id,
                content_id=content_id,
                priority=priority,
                total_steps=len(workflow_def.steps),
                execution_context=context or {}
            )
            
            self.executions[execution_id] = execution
            
            # Add to execution queue
            await self.execution_queue.put(execution_id)
            
            self.logger.info(f"Created workflow execution: {execution_id}")
            return execution_id
            
        except Exception as e:
            self.logger.error(f"Error creating workflow execution: {e}")
            raise
    
    async def start_workflow_processor(self):
        """Start the workflow execution processor."""
        if self.is_running:
            return
        
        self.is_running = True
        self.logger.info("Starting workflow processor")
        
        async def process_workflows():
            while self.is_running:
                try:
                    # Check if we can start new workflows
                    if len(self.running_executions) < self.max_concurrent_workflows:
                        try:
                            # Get next execution from queue (with timeout)
                            execution_id = await asyncio.wait_for(
                                self.execution_queue.get(), 
                                timeout=1.0
                            )
                            
                            # Start workflow execution
                            task = asyncio.create_task(
                                self._execute_workflow(execution_id)
                            )
                            self.running_executions[execution_id] = task
                            
                        except asyncio.TimeoutError:
                            # No new workflows to process
                            pass
                    
                    # Clean up completed workflows
                    completed_executions = []
                    for execution_id, task in self.running_executions.items():
                        if task.done():
                            completed_executions.append(execution_id)
                    
                    for execution_id in completed_executions:
                        del self.running_executions[execution_id]
                    
                    await asyncio.sleep(1)  # Prevent busy waiting
                    
                except Exception as e:
                    self.logger.error(f"Error in workflow processor: {e}")
                    await asyncio.sleep(5)
        
        # Start the processor task
        asyncio.create_task(process_workflows())
    
    async def _execute_workflow(self, execution_id: str):
        """Execute a workflow instance."""
        try:
            execution = self.executions[execution_id]
            workflow_def = self.workflow_definitions[execution.workflow_id]
            
            self.logger.info(f"Starting workflow execution: {execution_id}")
            
            execution.status = WorkflowStatus.RUNNING
            execution.start_time = datetime.utcnow()
            
            # Create step tracking
            step_statuses = {step.step_id: step for step in workflow_def.steps}
            completed_steps = set()
            
            # Execute steps based on dependencies
            while len(completed_steps) < len(workflow_def.steps):
                # Find executable steps (dependencies met)
                executable_steps = []
                for step in workflow_def.steps:
                    if (step.step_id not in completed_steps and
                        step_statuses[step.step_id].status == StepStatus.WAITING and
                        all(dep in completed_steps for dep in step.dependencies)):
                        executable_steps.append(step)
                
                if not executable_steps:
                    # Check for failed required steps
                    failed_required = any(
                        step_statuses[step.step_id].status == StepStatus.FAILED and step.required
                        for step in workflow_def.steps
                        if step.step_id not in completed_steps
                    )
                    
                    if failed_required:
                        execution.status = WorkflowStatus.FAILED
                        break
                    
                    # No executable steps available, wait
                    await asyncio.sleep(1)
                    continue
                
                # Execute steps in parallel (up to max_parallel_steps)
                current_batch = executable_steps[:workflow_def.max_parallel_steps]
                step_tasks = []
                
                for step in current_batch:
                    task = asyncio.create_task(
                        self._execute_step(execution, step)
                    )
                    step_tasks.append((step.step_id, task))
                
                # Wait for batch completion
                for step_id, task in step_tasks:
                    try:
                        await task
                        if step_statuses[step_id].status == StepStatus.COMPLETED:
                            completed_steps.add(step_id)
                            execution.completed_steps += 1
                        elif step_statuses[step_id].status == StepStatus.FAILED:
                            execution.failed_steps += 1
                            if step_statuses[step_id].required:
                                execution.status = WorkflowStatus.FAILED
                                break
                    except Exception as e:
                        self.logger.error(f"Step execution error: {e}")
                        step_statuses[step_id].status = StepStatus.FAILED
                        execution.failed_steps += 1
            
            # Finalize execution
            execution.end_time = datetime.utcnow()
            if execution.status == WorkflowStatus.RUNNING:
                execution.status = WorkflowStatus.COMPLETED
            
            # Store step results
            execution.step_results = {
                step.step_id: step.result_data 
                for step in workflow_def.steps
            }
            
            self.logger.info(
                f"Workflow execution completed: {execution_id}, "
                f"status: {execution.status.value}, "
                f"completed: {execution.completed_steps}/{execution.total_steps}"
            )
            
        except Exception as e:
            self.logger.error(f"Error executing workflow {execution_id}: {e}")
            if execution_id in self.executions:
                self.executions[execution_id].status = WorkflowStatus.FAILED
                self.executions[execution_id].end_time = datetime.utcnow()
                self.executions[execution_id].error_log.append(str(e))
    
    async def _execute_step(self, execution: WorkflowExecution, step: WorkflowStep):
        """Execute an individual workflow step."""
        try:
            self.logger.debug(f"Executing step: {step.step_id}")
            
            step.status = StepStatus.RUNNING
            step.start_time = datetime.utcnow()
            step.attempt_count += 1
            
            # Get step function
            if step.function:
                step_function = step.function
            elif step.step_type in self.step_functions:
                step_function = self.step_functions[step.step_type]
            else:
                # Use default step processor
                step_function = self._default_step_processor
            
            # Prepare step context
            step_context = {
                "execution_id": execution.execution_id,
                "creator_id": execution.creator_id,
                "content_id": execution.content_id,
                "step_parameters": step.parameters,
                "execution_context": execution.execution_context,
                "step_results": execution.step_results
            }
            
            # Execute step with timeout
            try:
                result = await asyncio.wait_for(
                    step_function(step_context),
                    timeout=step.timeout_seconds
                )
                
                step.result_data = result or {}
                step.status = StepStatus.COMPLETED
                step.end_time = datetime.utcnow()
                
                self.logger.debug(f"Step completed: {step.step_id}")
                
            except asyncio.TimeoutError:
                step.status = StepStatus.FAILED
                step.error_message = f"Step timed out after {step.timeout_seconds} seconds"
                step.end_time = datetime.utcnow()
                
            except Exception as step_error:
                step.status = StepStatus.FAILED
                step.error_message = str(step_error)
                step.end_time = datetime.utcnow()
                
                # Retry if configured
                if (step.attempt_count < step.retry_count and 
                    execution.status != WorkflowStatus.FAILED):
                    self.logger.info(f"Retrying step {step.step_id} (attempt {step.attempt_count})")
                    await asyncio.sleep(step.retry_delay)
                    step.status = StepStatus.RETRY
                    await self._execute_step(execution, step)
                
        except Exception as e:
            self.logger.error(f"Error executing step {step.step_id}: {e}")
            step.status = StepStatus.FAILED
            step.error_message = str(e)
            step.end_time = datetime.utcnow()
    
    async def _default_step_processor(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Default step processor for unregistered step types."""
        self.logger.info(f"Processing step with default processor")
        
        # Simulate processing
        await asyncio.sleep(1)
        
        return {
            "processed": True,
            "timestamp": datetime.utcnow().isoformat(),
            "message": "Processed with default step processor"
        }
    
    async def get_execution_status(self, execution_id: str) -> Optional[WorkflowExecution]:
        """Get workflow execution status."""
        return self.executions.get(execution_id)
    
    async def cancel_execution(self, execution_id: str) -> bool:
        """Cancel a running workflow execution."""
        try:
            if execution_id not in self.executions:
                return False
            
            execution = self.executions[execution_id]
            
            if execution.status in [WorkflowStatus.COMPLETED, WorkflowStatus.FAILED, WorkflowStatus.CANCELLED]:
                return False
            
            execution.status = WorkflowStatus.CANCELLED
            execution.end_time = datetime.utcnow()
            
            # Cancel running task if exists
            if execution_id in self.running_executions:
                task = self.running_executions[execution_id]
                task.cancel()
                del self.running_executions[execution_id]
            
            self.logger.info(f"Cancelled workflow execution: {execution_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error cancelling execution: {e}")
            return False
    
    async def pause_execution(self, execution_id: str) -> bool:
        """Pause a running workflow execution."""
        try:
            if execution_id not in self.executions:
                return False
            
            execution = self.executions[execution_id]
            
            if execution.status != WorkflowStatus.RUNNING:
                return False
            
            execution.status = WorkflowStatus.PAUSED
            self.logger.info(f"Paused workflow execution: {execution_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error pausing execution: {e}")
            return False
    
    async def resume_execution(self, execution_id: str) -> bool:
        """Resume a paused workflow execution."""
        try:
            if execution_id not in self.executions:
                return False
            
            execution = self.executions[execution_id]
            
            if execution.status != WorkflowStatus.PAUSED:
                return False
            
            execution.status = WorkflowStatus.RUNNING
            await self.execution_queue.put(execution_id)
            
            self.logger.info(f"Resumed workflow execution: {execution_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error resuming execution: {e}")
            return False
    
    async def get_execution_history(
        self,
        creator_id: str,
        workflow_type: Optional[WorkflowType] = None,
        limit: int = 50
    ) -> List[WorkflowExecution]:
        """Get workflow execution history for creator."""
        executions = [
            execution for execution in self.executions.values()
            if execution.creator_id == creator_id
        ]
        
        # Filter by workflow type if specified
        if workflow_type:
            executions = [
                e for e in executions
                if self.workflow_definitions.get(e.workflow_id, {}).workflow_type == workflow_type
            ]
        
        # Sort by creation time (newest first) and limit
        executions.sort(key=lambda x: x.created_at, reverse=True)
        return executions[:limit]
    
    async def get_workflow_statistics(self) -> Dict[str, Any]:
        """Get workflow execution statistics."""
        total_executions = len(self.executions)
        status_counts = {}
        workflow_type_counts = {}
        
        for execution in self.executions.values():
            # Status distribution
            status = execution.status.value
            status_counts[status] = status_counts.get(status, 0) + 1
            
            # Workflow type distribution
            workflow_def = self.workflow_definitions.get(execution.workflow_id)
            if workflow_def:
                wf_type = workflow_def.workflow_type.value
                workflow_type_counts[wf_type] = workflow_type_counts.get(wf_type, 0) + 1
        
        success_rate = (
            status_counts.get("completed", 0) / max(total_executions, 1) * 100
        )
        
        return {
            "total_executions": total_executions,
            "running_executions": len(self.running_executions),
            "queued_executions": self.execution_queue.qsize(),
            "success_rate": round(success_rate, 2),
            "status_distribution": status_counts,
            "workflow_type_distribution": workflow_type_counts,
            "registered_workflows": len(self.workflow_definitions),
            "registered_step_functions": len(self.step_functions)
        }
    
    async def cleanup_old_executions(self, days_old: int = 30):
        """Clean up old workflow executions."""
        cutoff_date = datetime.utcnow() - timedelta(days=days_old)
        
        old_execution_ids = [
            execution_id for execution_id, execution in self.executions.items()
            if execution.created_at < cutoff_date and 
               execution.status in [WorkflowStatus.COMPLETED, WorkflowStatus.FAILED, WorkflowStatus.CANCELLED]
        ]
        
        for execution_id in old_execution_ids:
            del self.executions[execution_id]
        
        self.logger.info(f"Cleaned up {len(old_execution_ids)} old executions")
    
    async def stop(self):
        """Stop the workflow manager."""
        self.is_running = False
        
        # Cancel all running executions
        for execution_id, task in self.running_executions.items():
            task.cancel()
            if execution_id in self.executions:
                self.executions[execution_id].status = WorkflowStatus.CANCELLED
        
        self.running_executions.clear()
        
        self.logger.info("Workflow manager stopped")


# Example usage and testing
async def main():
    """Example usage of MonetizationWorkflowManager."""
    
    # Sample step functions
    async def analyze_content_step(context: Dict[str, Any]) -> Dict[str, Any]:
        """Sample content analysis step."""
        await asyncio.sleep(2)  # Simulate processing
        return {
            "monetization_potential": "high",
            "recommended_platforms": ["youtube", "spotify"],
            "estimated_revenue": "150.00"
        }
    
    async def setup_revenue_streams_step(context: Dict[str, Any]) -> Dict[str, Any]:
        """Sample revenue stream setup step."""
        await asyncio.sleep(1)
        return {
            "streams_configured": ["advertising", "subscription"],
            "monetization_enabled": True
        }
    
    # Initialize workflow manager
    manager = MonetizationWorkflowManager()
    
    # Register step functions
    manager.register_step_function("content_analysis", analyze_content_step)
    manager.register_step_function("revenue_setup", setup_revenue_streams_step)
    
    # Start workflow processor
    await manager.start_workflow_processor()
    
    # Create workflow execution
    execution_id = await manager.create_workflow_execution(
        workflow_id="content_upload_monetization",
        creator_id="test_creator_123",
        content_id="test_content_456",
        priority=Priority.HIGH,
        context={"content_type": "audio", "category": "music"}
    )
    
    print(f"Created workflow execution: {execution_id}")
    
    # Monitor execution
    while True:
        execution = await manager.get_execution_status(execution_id)
        if execution and execution.status in [WorkflowStatus.COMPLETED, WorkflowStatus.FAILED]:
            break
        await asyncio.sleep(1)
    
    print(f"Workflow completed with status: {execution.status.value}")
    print(f"Steps completed: {execution.completed_steps}/{execution.total_steps}")
    
    # Get statistics
    stats = await manager.get_workflow_statistics()
    print(f"Workflow Statistics: {stats}")
    
    # Stop manager
    await manager.stop()


if __name__ == "__main__":
    asyncio.run(main())