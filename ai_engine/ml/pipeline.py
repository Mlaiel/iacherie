"""ML Pipeline System

Advanced machine learning pipeline system for orchestrating complex workflows
including data processing, training, validation, and deployment.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  LEGAL WARNING ⚠️
This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use is strictly prohibited.
Contact: mlaiel@live.de
"""

import asyncio
import json
import time
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Union, Any, Callable, Tuple, AsyncGenerator
import logging
import networkx as nx
import pandas as pd
import numpy as np
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import yaml
import pickle

# Optional distributed computing libraries
try:
    import dask
    from dask import delayed
    from dask.distributed import Client, as_completed
    DASK_AVAILABLE = True
except ImportError:
    DASK_AVAILABLE = False
    dask = None
    delayed = None
    Client = None
    as_completed = None

# Optional experiment tracking libraries
try:
    import mlflow
    MLFLOW_AVAILABLE = True
except ImportError:
    MLFLOW_AVAILABLE = False
    mlflow = None

try:
    import wandb
    WANDB_AVAILABLE = True
except ImportError:
    WANDB_AVAILABLE = False
    wandb = None

logger = logging.getLogger(__name__)


class PipelineStatus(Enum):
    """
Pipeline execution status"""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"
    RETRYING = "retrying"


class StepStatus(Enum):
    """Pipeline step status"""

    WAITING = "waiting"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    RETRYING = "retrying"


class ExecutionMode(Enum):
    """Pipeline execution modes"""

    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    DISTRIBUTED = "distributed"
    STREAMING = "streaming"
    BATCH = "batch"
    HYBRID = "hybrid"


class ResourceType(Enum):
    """Resource types for pipeline steps"""

    CPU = "cpu"
    GPU = "gpu"
    MEMORY = "memory"
    STORAGE = "storage"
    NETWORK = "network"


@dataclass
class ResourceRequirement:
    """Resource requirements for pipeline steps"""
    cpu_cores: Optional[int] = None
    gpu_count: Optional[int] = None
    memory_gb: Optional[float] = None
    storage_gb: Optional[float] = None
    network_bandwidth_mbps: Optional[float] = None
    specialized_hardware: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        try:
            logger.info(f"Executing to_dict")
            
            # Implementation for to_dict
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"to_dict completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"to_dict failed: {e}")
            raise
            'cpu_cores': self.cpu_cores,
            'gpu_count': self.gpu_count,
            'memory_gb': self.memory_gb,
            'storage_gb': self.storage_gb,
            'network_bandwidth_mbps': self.network_bandwidth_mbps,
            'specialized_hardware': self.specialized_hardware
        }


@dataclass
class StepMetrics:
    """
Metrics for pipeline step execution"""
    step_id: str
        try:
            logger.info(f"Executing to_dict")
            
            # Implementation for to_dict
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"to_dict completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"to_dict failed: {e}")
            raise
    step_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_seconds: float = 0.0
    cpu_usage_percent: float = 0.0
    memory_usage_mb: float = 0.0
    gpu_usage_percent: float = 0.0
    disk_io_mb: float = 0.0
    network_io_mb: float = 0.0
    custom_metrics: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'step_id': self.step_id,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'duration_seconds': self.duration_seconds,
            'cpu_usage_percent': self.cpu_usage_percent,
            'memory_usage_mb': self.memory_usage_mb,
            'gpu_usage_percent': self.gpu_usage_percent,
            'disk_io_mb': self.disk_io_mb,
        try:
            logger.info(f"Executing to_dict")
            
            # Implementation for to_dict
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"to_dict completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"to_dict failed: {e}")
            raise
            'custom_metrics': self.custom_metrics
        }


@dataclass
class PipelineConfig:
    """
Configuration for ML pipeline"""
    name: str
    version: str = "1.0.0"
    description: str = ""
    execution_mode: ExecutionMode = ExecutionMode.SEQUENTIAL
    max_parallel_steps: int = 4
    timeout_seconds: Optional[int] = None
    retry_policy: Dict[str, Any] = field(default_factory=dict)
    error_handling: str = "stop"  # stop, continue, retry
    logging_level: str = "INFO"
    artifact_storage_path: str = "./artifacts"
    enable_caching: bool = True
    cache_ttl_seconds: int = 3600
    enable_monitoring: bool = True
    monitoring_interval_seconds: int = 30
    resource_limits: Dict[str, Any] = field(default_factory=dict)
    environment_variables: Dict[str, str] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'version': self.version,
            'description': self.description,
            'execution_mode': self.execution_mode.value,
            'max_parallel_steps': self.max_parallel_steps,
            'timeout_seconds': self.timeout_seconds,
            'retry_policy': self.retry_policy,
            'error_handling': self.error_handling,
            'logging_level': self.logging_level,
            'artifact_storage_path': self.artifact_storage_path,
            'enable_caching': self.enable_caching,
            'cache_ttl_seconds': self.cache_ttl_seconds,
            'enable_monitoring': self.enable_monitoring,
            'monitoring_interval_seconds': self.monitoring_interval_seconds,
            'resource_limits': self.resource_limits,
            'environment_variables': self.environment_variables,
            'tags': self.tags
        }


class PipelineStep(ABC):
        try:
            logger.info(f"Executing execute")
            
            # Implementation for execute
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"execute completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"execute failed: {e}")
            raise
    def __init__(
        self,
        step_id: str,
        name: str,
        description: str = "",
        dependencies: List[str] = None,
        resource_requirements: ResourceRequirement = None,
        timeout_seconds: Optional[int] = None,
        retry_attempts: int = 0,
        retry_delay_seconds: int = 60,
        enable_caching: bool = True,
        tags: List[str] = None
    ):
        self.step_id = step_id
        self.name = name
        self.description = description
        self.dependencies = dependencies or []
        self.resource_requirements = resource_requirements or ResourceRequirement()
        self.timeout_seconds = timeout_seconds
        self.retry_attempts = retry_attempts
        self.retry_delay_seconds = retry_delay_seconds
        self.enable_caching = enable_caching
        self.tags = tags or []
        
        # Runtime state
        self.status = StepStatus.WAITING
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self.error_message: Optional[str] = None
        self.outputs: Dict[str, Any] = {}
        self.metrics: Optional[StepMetrics] = None
        self.retry_count = 0
        
        # Logger
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}.{step_id}")
    
    @abstractmethod
    async def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the pipeline step"""
        pass
    
    def validate_inputs(self, inputs: Dict[str, Any]) -> bool:
        """
Validate step inputs"""
        return True
    
    def validate_outputs(self, outputs: Dict[str, Any]) -> bool:
        """
Validate step outputs"""
        return True
    
    async def run(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
Run the step with error handling and metrics"""
        self.status = StepStatus.RUNNING
        self.start_time = datetime.now()
        
        try:
            # Validate inputs
            if not self.validate_inputs(inputs):
                raise ValueError(f"Invalid inputs for step {self.step_id}")
            
            # Execute step
            outputs = await self.execute(inputs)
            
            # Validate outputs
            if not self.validate_outputs(outputs):
                raise ValueError(f"Invalid outputs from step {self.step_id}")
            
            self.outputs = outputs
            self.status = StepStatus.COMPLETED
            self.end_time = datetime.now()
            
            # Calculate metrics
            self.metrics = StepMetrics(
                step_id=self.step_id,
                start_time=self.start_time,
                end_time=self.end_time,
                duration_seconds=(self.end_time - self.start_time).total_seconds()
            )
            
            self.logger.info(f"Step {self.step_id} completed successfully")
            return outputs
            
        except Exception as e:
            self.status = StepStatus.FAILED
            self.error_message = str(e)
            self.end_time = datetime.now()
            
            self.logger.error(f"Step {self.step_id} failed: {e}")
            
            # Retry if configured
            if self.retry_count < self.retry_attempts:
                self.retry_count += 1
                self.status = StepStatus.RETRYING
                self.logger.info(f"Retrying step {self.step_id} (attempt {self.retry_count})")
                
                await asyncio.sleep(self.retry_delay_seconds)
                return await self.run(inputs)
            
            raise
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert step to dictionary representation"""
        return {
            'step_id': self.step_id,
            'name': self.name,
            'description': self.description,
            'dependencies': self.dependencies,
            'resource_requirements': self.resource_requirements.to_dict(),
            'timeout_seconds': self.timeout_seconds,
            'retry_attempts': self.retry_attempts,
            'retry_delay_seconds': self.retry_delay_seconds,
            'enable_caching': self.enable_caching,
            'tags': self.tags,
            'status': self.status.value,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'error_message': self.error_message,
            'retry_count': self.retry_count,
            'metrics': self.metrics.to_dict() if self.metrics else None
        }


class DataLoadingStep(PipelineStep):
    """
Data loading pipeline step"""
    
    def __init__(self, step_id: str, data_source: str, **kwargs):
        super().__init__(step_id, f"Load Data from {data_source}", **kwargs)
        self.data_source = data_source
    
    async def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Load data from specified source"""
        self.logger.info(f"Loading data from {self.data_source}")
        
        # Simulate data loading
        await asyncio.sleep(1)
        
        if self.data_source.endswith('.csv'):
            data = pd.read_csv(self.data_source)
        elif self.data_source.endswith('.json'):
            data = pd.read_json(self.data_source)
        elif self.data_source.endswith('.parquet'):
            data = pd.read_parquet(self.data_source)
        else:
            # Simulate loading
            data = pd.DataFrame(np.random.randn(1000, 10))
        
        return {'data': data, 'data_shape': data.shape}


class DataPreprocessingStep(PipelineStep):
    """Data preprocessing pipeline step"""
    
    def __init__(self, step_id: str, preprocessing_config: Dict[str, Any], **kwargs):
        super().__init__(step_id, "Data Preprocessing", **kwargs)
        self.preprocessing_config = preprocessing_config
    
    async def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Preprocess data according to configuration"""
        data = inputs.get('data')
        if data is None:
            raise ValueError("No data provided for preprocessing")
        
        self.logger.info("Preprocessing data")
        
        # Simulate preprocessing
        await asyncio.sleep(2)
        
        processed_data = data.copy()
        
        # Apply preprocessing steps
        if self.preprocessing_config.get('normalize', False):
            processed_data = (processed_data - processed_data.mean()) / processed_data.std()
        
        if self.preprocessing_config.get('remove_outliers', False):
            # Simple outlier removal
            q1 = processed_data.quantile(0.25)
            q3 = processed_data.quantile(0.75)
            iqr = q3 - q1
            processed_data = processed_data[~((processed_data < (q1 - 1.5 * iqr)) | (processed_data > (q3 + 1.5 * iqr))).any(axis=1)]
        
        return {
            'processed_data': processed_data,
            'preprocessing_stats': {
                'original_shape': data.shape,
                'processed_shape': processed_data.shape,
                'features_processed': list(processed_data.columns)
            }
        }


class ModelTrainingStep(PipelineStep):
    """Model training pipeline step"""
    
    def __init__(self, step_id: str, model_config: Dict[str, Any], **kwargs):
        super().__init__(step_id, "Model Training", **kwargs)
        self.model_config = model_config
    
    async def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Train machine learning model"""
        data = inputs.get('processed_data')
        if data is None:
            raise ValueError("No processed data provided for training")
        
        self.logger.info("Training model")
        
        # Simulate training
        training_epochs = self.model_config.get('epochs', 10)
        for epoch in range(training_epochs):
            await asyncio.sleep(0.5)  # Simulate training time per epoch
            self.logger.info(f"Training epoch {epoch + 1}/{training_epochs}")
        
        # Simulate model metrics
        training_metrics = {
            'final_loss': np.random.uniform(0.1, 0.5),
            'accuracy': np.random.uniform(0.8, 0.95),
            'training_time_seconds': training_epochs * 0.5
        }
        
        model_path = f"./models/model_{self.step_id}_{int(time.time())}.pkl"
        
        return {
            'model_path': model_path,
            'training_metrics': training_metrics,
            'model_config': self.model_config
        }


class ModelValidationStep(PipelineStep):
    """Model validation pipeline step"""
    
    def __init__(self, step_id: str, validation_config: Dict[str, Any], **kwargs):
        super().__init__(step_id, "Model Validation", **kwargs)
        self.validation_config = validation_config
    
    async def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Validate trained model"""
        model_path = inputs.get('model_path')
        if not model_path:
            raise ValueError("No model path provided for validation")
        
        self.logger.info("Validating model")
        
        # Simulate validation
        await asyncio.sleep(1)
        
        validation_metrics = {
            'validation_accuracy': np.random.uniform(0.75, 0.92),
            'validation_loss': np.random.uniform(0.15, 0.6),
            'f1_score': np.random.uniform(0.7, 0.9),
            'precision': np.random.uniform(0.7, 0.9),
            'recall': np.random.uniform(0.7, 0.9)
        }
        
        # Check if model meets validation criteria
        min_accuracy = self.validation_config.get('min_accuracy', 0.8)
        model_approved = validation_metrics['validation_accuracy'] >= min_accuracy
        
        return {
            'validation_metrics': validation_metrics,
            'model_approved': model_approved,
            'model_path': model_path
        }


class ModelDeploymentStep(PipelineStep):
    """Model deployment pipeline step"""
    
    def __init__(self, step_id: str, deployment_config: Dict[str, Any], **kwargs):
        super().__init__(step_id, "Model Deployment", **kwargs)
        self.deployment_config = deployment_config
    
    async def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Deploy validated model"""
        model_path = inputs.get('model_path')
        model_approved = inputs.get('model_approved', False)
        
        if not model_approved:
            raise ValueError("Model not approved for deployment")
        
        self.logger.info("Deploying model")
        
        # Simulate deployment
        await asyncio.sleep(2)
        
        deployment_info = {
            'deployment_id': f"deploy_{int(time.time())}",
            'endpoint_url': f"https://api.example.com/models/{self.step_id}",
            'deployment_time': datetime.now().isoformat(),
            'status': 'active'
        }
        
        return {
            'deployment_info': deployment_info,
            'model_path': model_path
        }


class MLPipeline:
    """Advanced ML pipeline orchestrator"""
    
    def __init__(self, config: PipelineConfig):
        self.config = config
        self.steps: Dict[str, PipelineStep] = {}
        self.execution_graph = nx.DiGraph()
        self.status = PipelineStatus.PENDING
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self.error_message: Optional[str] = None
        self.execution_id = str(uuid.uuid4())
        
        # Logging and monitoring
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}.{config.name}")
        self.artifacts = {}
        self.metrics = {}
        
        # Execution context
        self.executor = None
        self.dask_client = None
        
        # Create artifact storage directory
        Path(self.config.artifact_storage_path).mkdir(parents=True, exist_ok=True)
    
    def add_step(self, step: PipelineStep) -> 'MLPipeline':
        """Add a step to the pipeline"""
        self.steps[step.step_id] = step
        self.execution_graph.add_node(step.step_id, step=step)
        
        # Add dependencies
        for dep in step.dependencies:
            if dep not in self.steps:
                self.logger.warning(f"Dependency {dep} not found for step {step.step_id}")
            else:
                self.execution_graph.add_edge(dep, step.step_id)
        
        self.logger.info(f"Added step: {step.step_id}")
        return self
    
    def remove_step(self, step_id: str) -> 'MLPipeline':
        """Remove a step from the pipeline"""
        if step_id in self.steps:
            del self.steps[step_id]
            self.execution_graph.remove_node(step_id)
            self.logger.info(f"Removed step: {step_id}")
        return self
    
    def validate_pipeline(self) -> Tuple[bool, List[str]]:
        """Validate pipeline structure and dependencies"""
        errors = []
        
        # Check for cycles
        if not nx.is_directed_acyclic_graph(self.execution_graph):
            cycles = list(nx.simple_cycles(self.execution_graph))
            errors.append(f"Pipeline contains cycles: {cycles}")
        
        # Check for missing dependencies
        for step_id, step in self.steps.items():
            for dep in step.dependencies:
                if dep not in self.steps:
                    errors.append(f"Step {step_id} depends on missing step {dep}")
        
        # Check for isolated nodes
        isolated = list(nx.isolates(self.execution_graph))
        if isolated and len(self.steps) > 1:
            errors.append(f"Isolated steps found: {isolated}")
        
        return len(errors) == 0, errors
    
    def get_execution_order(self) -> List[str]:
        """Get topological order for pipeline execution"""
        try:
            return list(nx.topological_sort(self.execution_graph))
        except nx.NetworkXError as e:
            self.logger.error(f"Failed to determine execution order: {e}")
            raise
    
    def visualize_pipeline(self, output_path: Optional[str] = None) -> str:
        """Generate pipeline visualization"""
        import matplotlib.pyplot as plt
        
        plt.figure(figsize=(12, 8))
        
        # Create layout
        pos = nx.spring_layout(self.execution_graph, k=2, iterations=50)
        
        # Color nodes based on status
        node_colors = []
        for node in self.execution_graph.nodes():
            step = self.steps[node]
            if step.status == StepStatus.COMPLETED:
                node_colors.append('green')
            elif step.status == StepStatus.FAILED:
                node_colors.append('red')
            elif step.status == StepStatus.RUNNING:
                node_colors.append('yellow')
            else:
                node_colors.append('lightblue')
        
        # Draw graph
        nx.draw(
            self.execution_graph,
            pos,
            with_labels=True,
            node_color=node_colors,
            node_size=1500,
            font_size=8,
            font_weight='bold',
            arrows=True,
            arrowsize=20,
            edge_color='gray'
        )
        
        plt.title(f"ML Pipeline: {self.config.name}")
        
        if output_path:
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
        else:
            output_path = f"{self.config.artifact_storage_path}/pipeline_graph_{self.execution_id}.png"
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
        
        plt.close()
        return output_path
    
    async def execute_step(self, step_id: str, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single pipeline step"""
        step = self.steps[step_id]
        
        try:
            # Check resource requirements
            if not self._check_resources(step):
                raise RuntimeError(f"Insufficient resources for step {step_id}")
            
            # Execute step
            outputs = await step.run(inputs)
            
            # Store artifacts
            self._store_step_artifacts(step_id, outputs)
            
            return outputs
            
        except Exception as e:
            self.logger.error(f"Step {step_id} execution failed: {e}")
            raise
    
    async def execute_sequential(self, initial_inputs: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute pipeline sequentially"""
        execution_order = self.get_execution_order()
        current_outputs = initial_inputs or {}
        
        for step_id in execution_order:
            self.logger.info(f"Executing step: {step_id}")
            
            # Prepare inputs for this step
            step_inputs = self._prepare_step_inputs(step_id, current_outputs)
            
            # Execute step
            step_outputs = await self.execute_step(step_id, step_inputs)
            
            # Merge outputs
            current_outputs.update(step_outputs)
        
        return current_outputs
    
    async def execute_parallel(self, initial_inputs: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute pipeline with parallel processing where possible"""
        execution_order = self.get_execution_order()
        completed_steps = set()
        running_tasks = {}
        all_outputs = initial_inputs or {}
        
        while completed_steps != set(execution_order):
            # Find steps that can be executed
            ready_steps = []
            for step_id in execution_order:
                if (step_id not in completed_steps and 
                    step_id not in running_tasks and
                    all(dep in completed_steps for dep in self.steps[step_id].dependencies)):
                    ready_steps.append(step_id)
            
            # Limit parallel execution
            max_parallel = min(self.config.max_parallel_steps, len(ready_steps))
            ready_steps = ready_steps[:max_parallel]
            
            # Start new tasks
            for step_id in ready_steps:
                step_inputs = self._prepare_step_inputs(step_id, all_outputs)
                task = asyncio.create_task(self.execute_step(step_id, step_inputs))
                running_tasks[step_id] = task
                self.logger.info(f"Started parallel execution of step: {step_id}")
            
            # Wait for at least one task to complete
            if running_tasks:
                done, pending = await asyncio.wait(
                    running_tasks.values(),
                    return_when=asyncio.FIRST_COMPLETED
                )
                
                # Process completed tasks
                for task in done:
                    step_id = None
                    for sid, t in running_tasks.items():
                        if t == task:
                            step_id = sid
                            break
                    
                    if step_id:
                        try:
                            step_outputs = await task
                            all_outputs.update(step_outputs)
                            completed_steps.add(step_id)
                            del running_tasks[step_id]
                            self.logger.info(f"Completed step: {step_id}")
                        except Exception as e:
                            self.logger.error(f"Step {step_id} failed: {e}")
                            # Cancel remaining tasks
                            for remaining_task in running_tasks.values():
                                remaining_task.cancel()
                            raise
        
        return all_outputs
    
    async def execute_distributed(self, initial_inputs: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute pipeline with distributed computing"""
        try:
            from dask.distributed import Client, as_completed
            
            if not self.dask_client:
                self.dask_client = Client('localhost:8786')  # Assume Dask scheduler is running
            
            execution_order = self.get_execution_order()
            futures = {}
            all_outputs = initial_inputs or {}
            
            # Submit all steps as Dask tasks
            for step_id in execution_order:
                step_inputs = self._prepare_step_inputs(step_id, all_outputs)
                future = self.dask_client.submit(self._execute_step_sync, step_id, step_inputs)
                futures[step_id] = future
            
            # Wait for completion
            for future in as_completed(futures.values()):
                step_id = None
                for sid, f in futures.items():
                    if f == future:
                        step_id = sid
                        break
                
                if step_id:
                    try:
                        step_outputs = await future.result()
                        all_outputs.update(step_outputs)
                        self.logger.info(f"Completed distributed step: {step_id}")
                    except Exception as e:
                        self.logger.error(f"Distributed step {step_id} failed: {e}")
                        raise
            
            return all_outputs
            
        except ImportError:
            self.logger.warning("Dask not available, falling back to parallel execution")
            return await self.execute_parallel(initial_inputs)
    
    def _execute_step_sync(self, step_id: str, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Synchronous wrapper for step execution (for Dask)"""
        return asyncio.run(self.execute_step(step_id, inputs))
    
    def _prepare_step_inputs(self, step_id: str, all_outputs: Dict[str, Any]) -> Dict[str, Any]:
        """
Prepare inputs for a specific step"""
        step = self.steps[step_id]
        step_inputs = {}
        
        # Include outputs from dependency steps
        for dep_id in step.dependencies:
            if dep_id in self.steps:
                dep_outputs = self.steps[dep_id].outputs
                step_inputs.update(dep_outputs)
        
        # Include global outputs
        step_inputs.update(all_outputs)
        
        return step_inputs
    
    def _check_resources(self, step: PipelineStep) -> bool:
        """
Check if resources are available for step execution"""
        # Simple resource check implementation
        req = step.resource_requirements
        
        if req.cpu_cores and req.cpu_cores > psutil.cpu_count():
            return False
        
        if req.memory_gb:
            available_memory_gb = psutil.virtual_memory().available / (1024**3)
            if req.memory_gb > available_memory_gb:
                return False
        
        # Additional resource checks would go here
        return True
    
    def _store_step_artifacts(self, step_id: str, outputs: Dict[str, Any]):
        """
Store step artifacts for later retrieval"""
        artifact_path = Path(self.config.artifact_storage_path) / self.execution_id / step_id
        artifact_path.mkdir(parents=True, exist_ok=True)
        
        # Store outputs as JSON
        outputs_file = artifact_path / "outputs.json"
        try:
            with open(outputs_file, 'w') as f:
                json.dump(outputs, f, default=str, indent=2)
        except Exception as e:
            self.logger.warning(f"Failed to store outputs for step {step_id}: {e}")
        
        # Store step metadata
        metadata = self.steps[step_id].to_dict()
        metadata_file = artifact_path / "metadata.json"
        try:
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, default=str, indent=2)
        except Exception as e:
            self.logger.warning(f"Failed to store metadata for step {step_id}: {e}")
    
    async def execute(self, initial_inputs: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute the complete pipeline"""
        self.status = PipelineStatus.RUNNING
        self.start_time = datetime.now()
        
        try:
            # Validate pipeline
            is_valid, errors = self.validate_pipeline()
            if not is_valid:
                raise ValueError(f"Pipeline validation failed: {errors}")
            
            self.logger.info(f"Starting pipeline execution: {self.config.name}")
            
            # Choose execution mode
            if self.config.execution_mode == ExecutionMode.SEQUENTIAL:
                result = await self.execute_sequential(initial_inputs)
            elif self.config.execution_mode == ExecutionMode.PARALLEL:
                result = await self.execute_parallel(initial_inputs)
            elif self.config.execution_mode == ExecutionMode.DISTRIBUTED:
                result = await self.execute_distributed(initial_inputs)
            else:
                raise ValueError(f"Unsupported execution mode: {self.config.execution_mode}")
            
            self.status = PipelineStatus.COMPLETED
            self.end_time = datetime.now()
            
            # Generate final metrics
            self._generate_pipeline_metrics()
            
            # Store final results
            self._store_pipeline_results(result)
            
            # Generate visualization
            self.visualize_pipeline()
            
            self.logger.info(f"Pipeline execution completed successfully")
            return result
            
        except Exception as e:
            self.status = PipelineStatus.FAILED
            self.error_message = str(e)
            self.end_time = datetime.now()
            
            self.logger.error(f"Pipeline execution failed: {e}")
            raise
        finally:
            # Cleanup resources
            if self.dask_client:
                self.dask_client.close()
    
    def _generate_pipeline_metrics(self):
        """Generate overall pipeline metrics"""
        if not self.start_time or not self.end_time:
            return
        
        total_duration = (self.end_time - self.start_time).total_seconds()
        
        self.metrics = {
            'pipeline_id': self.execution_id,
            'total_duration_seconds': total_duration,
            'total_steps': len(self.steps),
            'completed_steps': sum(1 for step in self.steps.values() if step.status == StepStatus.COMPLETED),
            'failed_steps': sum(1 for step in self.steps.values() if step.status == StepStatus.FAILED),
            'success_rate': sum(1 for step in self.steps.values() if step.status == StepStatus.COMPLETED) / len(self.steps),
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat(),
            'status': self.status.value,
            'step_metrics': {step_id: step.metrics.to_dict() if step.metrics else None 
                           for step_id, step in self.steps.items()}
        }
    
    def _store_pipeline_results(self, results: Dict[str, Any]):
        """
Store final pipeline results"""
        results_path = Path(self.config.artifact_storage_path) / self.execution_id / "pipeline_results.json"
        results_path.parent.mkdir(parents=True, exist_ok=True)
        
        pipeline_results = {
            'config': self.config.to_dict(),
            'metrics': self.metrics,
            'results': results,
            'execution_id': self.execution_id
        }
        
        try:
            with open(results_path, 'w') as f:
                json.dump(pipeline_results, f, default=str, indent=2)
        except Exception as e:
            self.logger.warning(f"Failed to store pipeline results: {e}")
    
    def get_step_status(self, step_id: str) -> Dict[str, Any]:
        """Get status of a specific step"""
        if step_id not in self.steps:
            return {"error": f"Step {step_id} not found"}
        
        return self.steps[step_id].to_dict()
    
    def get_pipeline_status(self) -> Dict[str, Any]:
        """Get overall pipeline status"""
        return {
            'pipeline_id': self.execution_id,
            'name': self.config.name,
            'status': self.status.value,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'error_message': self.error_message,
            'metrics': self.metrics,
            'steps': {step_id: step.to_dict() for step_id, step in self.steps.items()}
        }
    
    @classmethod
    def from_yaml(cls, config_path: str) -> 'MLPipeline':
        """
Create pipeline from YAML configuration"""
        with open(config_path, 'r') as f:
            config_dict = yaml.safe_load(f)
        
        # Create pipeline config
        pipeline_config = PipelineConfig(**config_dict.get('pipeline', {}))
        pipeline = cls(pipeline_config)
        
        # Add steps
        for step_config in config_dict.get('steps', []):
            step_type = step_config.get('type')
            step_id = step_config.get('step_id')
            
            if step_type == 'data_loading':
                step = DataLoadingStep(step_id, **step_config)
            elif step_type == 'data_preprocessing':
                step = DataPreprocessingStep(step_id, **step_config)
            elif step_type == 'model_training':
                step = ModelTrainingStep(step_id, **step_config)
            elif step_type == 'model_validation':
                step = ModelValidationStep(step_id, **step_config)
            elif step_type == 'model_deployment':
                step = ModelDeploymentStep(step_id, **step_config)
            else:
                raise ValueError(f"Unknown step type: {step_type}")
            
            pipeline.add_step(step)
        
        return pipeline
    
    def to_yaml(self, output_path: str):
        """Export pipeline configuration to YAML"""
        config_dict = {
            'pipeline': self.config.to_dict(),
            'steps': [step.to_dict() for step in self.steps.values()]
        }
        
        with open(output_path, 'w') as f:
            yaml.dump(config_dict, f, default_flow_style=False, indent=2)


# Export main classes
__all__ = [
    'MLPipeline',
    'PipelineStep',
    'PipelineConfig',
    'PipelineStatus',
    'StepStatus',
    'ExecutionMode',
    'ResourceRequirement',
    'StepMetrics',
    'DataLoadingStep',
    'DataPreprocessingStep',
    'ModelTrainingStep',
    'ModelValidationStep',
    'ModelDeploymentStep'
]
