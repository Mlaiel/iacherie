"""AI/ML Pipeline Integration System
===================================

Advanced ML pipeline integration and orchestration system for seamless model
deployment, training, and inference workflows in production environments.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved

EXPERT ROLES IMPLEMENTATION:
- Lead Dev IA: ML pipeline architecture and orchestration
- ML Engineer: Model training and deployment automation
- Backend Senior: High-performance pipeline execution
- DevOps: CI/CD integration and monitoring
- Microservices: Service mesh integration and communication
"""

import asyncio
import logging
import json
import time
from typing import Dict, Any, List, Optional, Callable, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import uuid

logger = logging.getLogger(__name__)

class PipelineStatus(Enum):
    """Pipeline execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"

class StepType(Enum):
    """Pipeline step types."""
    DATA_PREPROCESSING = "data_preprocessing"
    FEATURE_ENGINEERING = "feature_engineering"
    MODEL_TRAINING = "model_training"
    MODEL_VALIDATION = "model_validation"
    MODEL_DEPLOYMENT = "model_deployment"
    INFERENCE = "inference"
    POST_PROCESSING = "post_processing"
    CUSTOM = "custom"

@dataclass
class PipelineStep:
    """Individual pipeline step configuration."""
    step_id: str
    step_type: StepType
    name: str
    function: Callable
    dependencies: List[str] = field(default_factory=list)
    parameters: Dict[str, Any] = field(default_factory=dict)
    timeout_seconds: int = 3600
    retry_count: int = 3
    parallel: bool = False
    required: bool = True

@dataclass
class PipelineExecution:
    """Pipeline execution tracking."""
    execution_id: str
    pipeline_id: str
    status: PipelineStatus
    started_at: datetime
    completed_at: Optional[datetime] = None
    steps_completed: List[str] = field(default_factory=list)
    steps_failed: List[str] = field(default_factory=list)
    error_message: Optional[str] = None
    metrics: Dict[str, Any] = field(default_factory=dict)
    artifacts: Dict[str, str] = field(default_factory=dict)

@dataclass
class MLPipeline:
    """ML pipeline configuration."""
    pipeline_id: str
    name: str
    description: str
    steps: List[PipelineStep]
    schedule_cron: Optional[str] = None
    max_parallel_executions: int = 1
    notification_webhooks: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

class PipelineIntegrator:
    """Enterprise ML pipeline integration and orchestration system."""
    
    def __init__(self, database_connection=None, storage_backend=None) -> None:
        """Initialize pipeline integrator.
        
        Args:
            database_connection: MongoDB connection for pipeline metadata
            storage_backend: Storage backend for artifacts and models
        """
        self.db = database_connection
        self.storage = storage_backend
        self.logger = logger
        
        # Active pipelines and executions
        self._pipelines: Dict[str, MLPipeline] = {}
        self._active_executions: Dict[str, PipelineExecution] = {}
        self._execution_tasks: Dict[str, asyncio.Task] = {}
        
        # Pipeline registry and caching
        self._step_registry: Dict[str, Callable] = {}
        self._pipeline_cache: Dict[str, Any] = {}
        
        # Monitoring and metrics
        self._execution_history: List[PipelineExecution] = []
        self._performance_metrics: Dict[str, List[float]] = {}
        
        # Configuration
        self._max_concurrent_executions = 10
        self._cleanup_interval = 3600  # 1 hour
        
        # Initialize built-in steps
        self._register_builtin_steps()
    
    def register_pipeline(self, pipeline: MLPipeline) -> bool:
        """Register a new ML pipeline.
        
        Args:
            pipeline: Pipeline configuration
            
        Returns:
            bool: Success status
        """
        try:
            # Validate pipeline configuration
            if not self._validate_pipeline(pipeline):
                return False
            
            # Store pipeline
            self._pipelines[pipeline.pipeline_id] = pipeline
            
            # Store in database if available
            if self.db:
                asyncio.create_task(self._store_pipeline(pipeline))
            
            self.logger.info(f"Registered pipeline: {pipeline.pipeline_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error registering pipeline {pipeline.pipeline_id}: {e}")
            return False
    
    def register_step_function(self, step_type: str, function: Callable) -> bool:
        """Register a custom step function.
        
        Args:
            step_type: Step type identifier
            function: Step execution function
            
        Returns:
            bool: Success status
        """
        try:
            self._step_registry[step_type] = function
            self.logger.info(f"Registered step function: {step_type}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error registering step function {step_type}: {e}")
            return False
    
    async def execute_pipeline(self, pipeline_id: str, parameters: Dict[str, Any] = None) -> str:
        """Execute a pipeline asynchronously.
        
        Args:
            pipeline_id: Pipeline identifier
            parameters: Runtime parameters
            
        Returns:
            str: Execution ID
        """
        try:
            if pipeline_id not in self._pipelines:
                raise ValueError(f"Pipeline {pipeline_id} not found")
            
            # Check concurrent execution limits
            active_count = len([e for e in self._active_executions.values() 
                              if e.pipeline_id == pipeline_id and e.status == PipelineStatus.RUNNING])
            
            pipeline = self._pipelines[pipeline_id]
            if active_count >= pipeline.max_parallel_executions:
                raise RuntimeError(f"Maximum parallel executions ({pipeline.max_parallel_executions}) reached")
            
            # Create execution record
            execution_id = str(uuid.uuid4())
            execution = PipelineExecution(
                execution_id=execution_id,
                pipeline_id=pipeline_id,
                status=PipelineStatus.PENDING,
                started_at=datetime.utcnow(),
                metrics={"parameters": parameters or {}}
            )
            
            self._active_executions[execution_id] = execution
            
            # Start execution task
            task = asyncio.create_task(self._execute_pipeline_task(execution_id, parameters or {}))
            self._execution_tasks[execution_id] = task
            
            self.logger.info(f"Started pipeline execution: {execution_id}")
            return execution_id
            
        except Exception as e:
            self.logger.error(f"Error starting pipeline execution: {e}")
            raise
    
    async def get_execution_status(self, execution_id: str) -> Dict[str, Any]:
        """Get pipeline execution status.
        
        Args:
            execution_id: Execution identifier
            
        Returns:
            dict: Execution status information
        """
        try:
            if execution_id in self._active_executions:
                execution = self._active_executions[execution_id]
            else:
                # Check execution history
                execution = next((e for e in self._execution_history if e.execution_id == execution_id), None)
                if not execution:
                    return {"error": "Execution not found"}
            
            # Calculate progress
            pipeline = self._pipelines.get(execution.pipeline_id)
            total_steps = len(pipeline.steps) if pipeline else 0
            completed_steps = len(execution.steps_completed)
            progress_percent = (completed_steps / total_steps * 100) if total_steps > 0 else 0
            
            # Calculate duration
            duration_seconds = None
            if execution.completed_at:
                duration_seconds = (execution.completed_at - execution.started_at).total_seconds()
            elif execution.status == PipelineStatus.RUNNING:
                duration_seconds = (datetime.utcnow() - execution.started_at).total_seconds()
            
            return {
                "execution_id": execution.execution_id,
                "pipeline_id": execution.pipeline_id,
                "status": execution.status.value,
                "started_at": execution.started_at.isoformat(),
                "completed_at": execution.completed_at.isoformat() if execution.completed_at else None,
                "duration_seconds": duration_seconds,
                "progress_percent": progress_percent,
                "steps_completed": execution.steps_completed,
                "steps_failed": execution.steps_failed,
                "error_message": execution.error_message,
                "metrics": execution.metrics,
                "artifacts": execution.artifacts
            }
            
        except Exception as e:
            self.logger.error(f"Error getting execution status: {e}")
            return {"error": str(e)}
    
    async def cancel_execution(self, execution_id: str) -> bool:
        """Cancel a running pipeline execution.
        
        Args:
            execution_id: Execution identifier
            
        Returns:
            bool: Success status
        """
        try:
            if execution_id not in self._active_executions:
                return False
            
            execution = self._active_executions[execution_id]
            if execution.status not in [PipelineStatus.RUNNING, PipelineStatus.PENDING]:
                return False
            
            # Cancel the execution task
            if execution_id in self._execution_tasks:
                self._execution_tasks[execution_id].cancel()
                del self._execution_tasks[execution_id]
            
            # Update execution status
            execution.status = PipelineStatus.CANCELLED
            execution.completed_at = datetime.utcnow()
            execution.error_message = "Execution cancelled by user"
            
            # Move to history
            self._execution_history.append(execution)
            del self._active_executions[execution_id]
            
            self.logger.info(f"Cancelled pipeline execution: {execution_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error cancelling execution {execution_id}: {e}")
            return False
    
    async def get_pipeline_metrics(self, pipeline_id: str, days: int = 7) -> Dict[str, Any]:
        """Get pipeline performance metrics.
        
        Args:
            pipeline_id: Pipeline identifier
            days: Number of days to analyze
            
        Returns:
            dict: Pipeline metrics
        """
        try:
            cutoff_time = datetime.utcnow() - timedelta(days=days)
            
            # Get recent executions
            recent_executions = [
                e for e in self._execution_history
                if e.pipeline_id == pipeline_id and e.started_at >= cutoff_time
            ]
            
            if not recent_executions:
                return {"error": "No execution data available"}
            
            # Calculate metrics
            total_executions = len(recent_executions)
            successful_executions = len([e for e in recent_executions if e.status == PipelineStatus.COMPLETED])
            failed_executions = len([e for e in recent_executions if e.status == PipelineStatus.FAILED])
            
            success_rate = (successful_executions / total_executions * 100) if total_executions > 0 else 0
            
            # Calculate average duration
            completed_executions = [e for e in recent_executions if e.completed_at]
            if completed_executions:
                durations = [(e.completed_at - e.started_at).total_seconds() for e in completed_executions]
                avg_duration = sum(durations) / len(durations)
                min_duration = min(durations)
                max_duration = max(durations)
            else:
                avg_duration = min_duration = max_duration = 0
            
            return {
                "pipeline_id": pipeline_id,
                "analysis_period_days": days,
                "total_executions": total_executions,
                "successful_executions": successful_executions,
                "failed_executions": failed_executions,
                "success_rate_percent": success_rate,
                "average_duration_seconds": avg_duration,
                "min_duration_seconds": min_duration,
                "max_duration_seconds": max_duration,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting pipeline metrics: {e}")
            return {"error": str(e)}
    
    async def list_active_executions(self) -> List[Dict[str, Any]]:
        """List all active pipeline executions.
        
        Returns:
            list: Active executions summary
        """
        try:
            active_list = []
            
            for execution_id, execution in self._active_executions.items():
                pipeline = self._pipelines.get(execution.pipeline_id)
                
                active_list.append({
                    "execution_id": execution_id,
                    "pipeline_id": execution.pipeline_id,
                    "pipeline_name": pipeline.name if pipeline else "Unknown",
                    "status": execution.status.value,
                    "started_at": execution.started_at.isoformat(),
                    "duration_seconds": (datetime.utcnow() - execution.started_at).total_seconds(),
                    "steps_completed": len(execution.steps_completed),
                    "total_steps": len(pipeline.steps) if pipeline else 0
                })
            
            return active_list
            
        except Exception as e:
            self.logger.error(f"Error listing active executions: {e}")
            return []
    
    def _validate_pipeline(self, pipeline: MLPipeline) -> bool:
        """Validate pipeline configuration."""
        try:
            # Check required fields
            if not pipeline.pipeline_id or not pipeline.name:
                self.logger.error("Pipeline ID and name are required")
                return False
            
            if not pipeline.steps:
                self.logger.error("Pipeline must have at least one step")
                return False
            
            # Validate step dependencies
            step_ids = {step.step_id for step in pipeline.steps}
            for step in pipeline.steps:
                for dep in step.dependencies:
                    if dep not in step_ids:
                        self.logger.error(f"Step {step.step_id} has invalid dependency: {dep}")
                        return False
            
            # Check for circular dependencies
            if self._has_circular_dependencies(pipeline.steps):
                self.logger.error("Pipeline has circular dependencies")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating pipeline: {e}")
            return False
    
    def _has_circular_dependencies(self, steps: List[PipelineStep]) -> bool:
        """Check for circular dependencies in pipeline steps."""
        def visit(step_id: str, visited: set, rec_stack: set) -> bool:
            visited.add(step_id)
            rec_stack.add(step_id)
            
            # Find step and check its dependencies
            step = next((s for s in steps if s.step_id == step_id), None)
            if step:
                for dep in step.dependencies:
                    if dep not in visited:
                        if visit(dep, visited, rec_stack):
                            return True
                    elif dep in rec_stack:
                        return True
            
            rec_stack.remove(step_id)
            return False
        
        visited = set()
        for step in steps:
            if step.step_id not in visited:
                if visit(step.step_id, visited, set()):
                    return True
        
        return False
    
    async def _execute_pipeline_task(self, execution_id: str, parameters: Dict[str, Any]) -> None:
        """Execute pipeline steps in order."""
        try:
            execution = self._active_executions[execution_id]
            pipeline = self._pipelines[execution.pipeline_id]
            
            execution.status = PipelineStatus.RUNNING
            
            # Build execution order considering dependencies
            execution_order = self._build_execution_order(pipeline.steps)
            
            # Execute steps
            step_results = {}
            
            for step in execution_order:
                try:
                    self.logger.info(f"Executing step: {step.step_id}")
                    
                    # Prepare step parameters
                    step_params = {**parameters, **step.parameters}
                    
                    # Add results from dependent steps
                    for dep in step.dependencies:
                        if dep in step_results:
                            step_params[f"dep_{dep}"] = step_results[dep]
                    
                    # Execute step with retry logic
                    result = await self._execute_step_with_retry(step, step_params)
                    step_results[step.step_id] = result
                    execution.steps_completed.append(step.step_id)
                    
                    # Store intermediate results if needed
                    if self.storage and result and isinstance(result, dict):
                        if "artifact_path" in result:
                            execution.artifacts[step.step_id] = result["artifact_path"]
                    
                    self.logger.info(f"Completed step: {step.step_id}")
                    
                except Exception as e:
                    self.logger.error(f"Step {step.step_id} failed: {e}")
                    execution.steps_failed.append(step.step_id)
                    
                    if step.required:
                        execution.status = PipelineStatus.FAILED
                        execution.error_message = f"Required step {step.step_id} failed: {e}"
                        break
            
            # Update execution status
            if execution.status == PipelineStatus.RUNNING:
                execution.status = PipelineStatus.COMPLETED
            
            execution.completed_at = datetime.utcnow()
            
            # Store execution metrics
            execution.metrics.update({
                "total_steps": len(pipeline.steps),
                "completed_steps": len(execution.steps_completed),
                "failed_steps": len(execution.steps_failed),
                "duration_seconds": (execution.completed_at - execution.started_at).total_seconds()
            })
            
            # Move to history
            self._execution_history.append(execution)
            del self._active_executions[execution_id]
            
            # Cleanup task reference
            if execution_id in self._execution_tasks:
                del self._execution_tasks[execution_id]
            
            # Store in database
            if self.db:
                await self._store_execution(execution)
            
            # Send notifications
            await self._send_pipeline_notifications(pipeline, execution)
            
            self.logger.info(f"Pipeline execution completed: {execution_id}")
            
        except asyncio.CancelledError:
            self.logger.info(f"Pipeline execution cancelled: {execution_id}")
            raise
        except Exception as e:
            self.logger.error(f"Error in pipeline execution {execution_id}: {e}")
            
            execution = self._active_executions.get(execution_id)
            if execution:
                execution.status = PipelineStatus.FAILED
                execution.completed_at = datetime.utcnow()
                execution.error_message = str(e)
                
                # Move to history
                self._execution_history.append(execution)
                del self._active_executions[execution_id]
    
    def _build_execution_order(self, steps: List[PipelineStep]) -> List[PipelineStep]:
        """Build step execution order respecting dependencies."""
        # Topological sort
        in_degree = {step.step_id: len(step.dependencies) for step in steps}
        queue = [step for step in steps if in_degree[step.step_id] == 0]
        result = []
        
        while queue:
            current = queue.pop(0)
            result.append(current)
            
            # Update in-degrees for dependent steps
            for step in steps:
                if current.step_id in step.dependencies:
                    in_degree[step.step_id] -= 1
                    if in_degree[step.step_id] == 0:
                        queue.append(step)
        
        return result
    
    async def _execute_step_with_retry(self, step: PipelineStep, parameters: Dict[str, Any]) -> Any:
        """Execute a pipeline step with retry logic."""
        last_error = None
        
        for attempt in range(step.retry_count + 1):
            try:
                # Get step function
                if step.step_type.value in self._step_registry:
                    func = self._step_registry[step.step_type.value]
                elif hasattr(step, 'function') and step.function:
                    func = step.function
                else:
                    raise ValueError(f"No function found for step type: {step.step_type.value}")
                
                # Execute with timeout
                result = await asyncio.wait_for(
                    self._call_step_function(func, parameters),
                    timeout=step.timeout_seconds
                )
                
                return result
                
            except Exception as e:
                last_error = e
                if attempt < step.retry_count:
                    self.logger.warning(f"Step {step.step_id} attempt {attempt + 1} failed, retrying: {e}")
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                else:
                    self.logger.error(f"Step {step.step_id} failed after {step.retry_count + 1} attempts: {e}")
        
        raise last_error
    
    async def _call_step_function(self, func: Callable, parameters: Dict[str, Any]) -> Any:
        """Call step function, handling both sync and async functions."""
        if asyncio.iscoroutinefunction(func):
            return await func(**parameters)
        else:
            # Run synchronous function in thread pool
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, lambda: func(**parameters))
    
    def _register_builtin_steps(self) -> None:
        """Register built-in pipeline steps."""
        
        def data_preprocessing_step(**kwargs) -> Dict[str, Any]:
            """Built-in data preprocessing step."""
            self.logger.info("Executing data preprocessing step")
            # This would typically process data
            return {"status": "completed", "records_processed": kwargs.get("record_count", 0)}
        
        def feature_engineering_step(**kwargs) -> Dict[str, Any]:
            """Built-in feature engineering step."""
            self.logger.info("Executing feature engineering step")
            # This would typically create features
            return {"status": "completed", "features_created": kwargs.get("feature_count", 0)}
        
        def model_training_step(**kwargs) -> Dict[str, Any]:
            """Built-in model training step."""
            self.logger.info("Executing model training step")
            # This would typically train a model
            return {"status": "completed", "model_path": f"/models/{kwargs.get('model_name', 'model')}.pkl"}
        
        def model_validation_step(**kwargs) -> Dict[str, Any]:
            """Built-in model validation step."""
            self.logger.info("Executing model validation step")
            # This would typically validate model performance
            return {"status": "completed", "accuracy": 0.95, "f1_score": 0.93}
        
        # Register built-in steps
        self.register_step_function("data_preprocessing", data_preprocessing_step)
        self.register_step_function("feature_engineering", feature_engineering_step)
        self.register_step_function("model_training", model_training_step)
        self.register_step_function("model_validation", model_validation_step)
    
    async def _store_pipeline(self, pipeline: MLPipeline) -> None:
        """Store pipeline configuration in database."""
        if not self.db:
            return
        
        try:
            doc = {
                "pipeline_id": pipeline.pipeline_id,
                "name": pipeline.name,
                "description": pipeline.description,
                "steps": [
                    {
                        "step_id": step.step_id,
                        "step_type": step.step_type.value,
                        "name": step.name,
                        "dependencies": step.dependencies,
                        "parameters": step.parameters,
                        "timeout_seconds": step.timeout_seconds,
                        "retry_count": step.retry_count,
                        "parallel": step.parallel,
                        "required": step.required
                    }
                    for step in pipeline.steps
                ],
                "schedule_cron": pipeline.schedule_cron,
                "max_parallel_executions": pipeline.max_parallel_executions,
                "notification_webhooks": pipeline.notification_webhooks,
                "metadata": pipeline.metadata,
                "created_at": datetime.utcnow()
            }
            
            await self.db.ml_pipelines.replace_one(
                {"pipeline_id": pipeline.pipeline_id},
                doc,
                upsert=True
            )
            
        except Exception as e:
            self.logger.error(f"Error storing pipeline: {e}")
    
    async def _store_execution(self, execution: PipelineExecution) -> None:
        """Store execution results in database."""
        if not self.db:
            return
        
        try:
            doc = {
                "execution_id": execution.execution_id,
                "pipeline_id": execution.pipeline_id,
                "status": execution.status.value,
                "started_at": execution.started_at,
                "completed_at": execution.completed_at,
                "steps_completed": execution.steps_completed,
                "steps_failed": execution.steps_failed,
                "error_message": execution.error_message,
                "metrics": execution.metrics,
                "artifacts": execution.artifacts
            }
            
            await self.db.pipeline_executions.insert_one(doc)
            
        except Exception as e:
            self.logger.error(f"Error storing execution: {e}")
    
    async def _send_pipeline_notifications(self, pipeline: MLPipeline, execution: PipelineExecution) -> None:
        """Send pipeline completion notifications."""
        try:
            if pipeline.notification_webhooks:
                notification_data = {
                    "pipeline_id": pipeline.pipeline_id,
                    "pipeline_name": pipeline.name,
                    "execution_id": execution.execution_id,
                    "status": execution.status.value,
                    "started_at": execution.started_at.isoformat(),
                    "completed_at": execution.completed_at.isoformat() if execution.completed_at else None,
                    "metrics": execution.metrics
                }
                
                # In production, this would send HTTP notifications
                self.logger.info(f"Pipeline notification: {notification_data}")
                
        except Exception as e:
            self.logger.error(f"Error sending notifications: {e}")

__all__ = [
    'PipelineIntegrator', 'MLPipeline', 'PipelineStep', 'PipelineExecution',
    'PipelineStatus', 'StepType'
]