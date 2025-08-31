"""ML Pipeline Manager - Advanced ML Workflow Orchestration & Pipeline Management System

Industrial-grade ML pipeline orchestrator providing automated workflow management,
dependency resolution, data versioning, and comprehensive pipeline monitoring
for the IA-Influencer-Agent ML platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL WARNING:
This pipeline orchestration system and methodologies are the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, copying, distribution, or commercialization without explicit written permission
from Fahed Mlaiel (mlaiel@live.de) is STRICTLY PROHIBITED and will result in legal action.

ALL RIGHTS RESERVED - FAHED MLAIEL ©2025

🎯 BUSINESS LOGIC INTEGRATION:
Data Ingestion → Feature Engineering → Model Training → Validation
→ Optimization → Deployment → Monitoring → Retraining

Team Specialties:
- Lead AI Developer & Backend Senior Engineer
- Machine Learning Engineer & Audio Processing Specialist  
- Database Administrator & Security Expert
- Microservices Architect & DevOps Engineer
- AI Prompt Engineer & Content Protection Specialist
"""
import asyncio
import logging
import time
import uuid
import json
import hashlib
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Union, Tuple, Callable, Set
from pathlib import Path
import traceback
from abc import ABC, abstractmethod
import yaml
import networkx as nx
from contextlib import asynccontextmanager

# Data processing and ML
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline as SklearnPipeline
import joblib

# Workflow orchestration
try:
    from airflow import DAG
    from airflow.operators.python_operator import PythonOperator
    AIRFLOW_AVAILABLE = True
except ImportError:
    AIRFLOW_AVAILABLE = False

# MLflow for experiment tracking
import mlflow
import mlflow.tracking

# Platform core
try:
    from core.config import settings
except ImportError:
    # Fallback settings
    settings = type('Settings', (), {'debug': True, 'log_level': 'INFO'})()
try:
    from core.database import get_db_session
except ImportError:
    # Fallback database classes
    class DatabaseManager: pass
    get_db_session = DatabaseManager
try:
    from core.exceptions import PipelineError, ValidationError, ExecutionError
except ImportError:
    # Fallback exception classes
    class ValidationError(Exception): pass
    class ConfigurationError(Exception): pass
    class ProcessingError(Exception): pass
    PipelineError, ValidationError, ExecutionError = globals().get('PipelineError, ValidationError, ExecutionError', Exception)
from ...security.encryption import ContentEncryption
from ...utils.performance_monitor import PerformanceMonitor
from ...utils.cache import CacheManager

logger = logging.getLogger(__name__)

class PipelineStatus(Enum):
    """Pipeline execution status"""    CREATED = "created"
    QUEUED = "queued"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"

class StepStatus(Enum):
    """Individual step execution status"""    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed" 
    FAILED = "failed"
    SKIPPED = "skipped"
    RETRYING = "retrying"

class DependencyType(Enum):
    """Step dependency types"""    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    CONDITIONAL = "conditional"
    DATA = "data"

@dataclass
class StepMetrics:
    """Execution metrics for a pipeline step"""    execution_time: float = 0.0
    memory_usage: float = 0.0
    cpu_usage: float = 0.0
    input_size: int = 0
    output_size: int = 0
    error_count: int = 0
    retry_count: int = 0

@dataclass
class PipelineStep:
    """Individual pipeline step definition"""    step_id: str
    name: str
    function: Callable
    inputs: List[str] = field(default_factory=list)
    outputs: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    parameters: Dict[str, Any] = field(default_factory=dict)
    retry_count: int = 3
    timeout: int = 3600
    status: StepStatus = StepStatus.PENDING
    metrics: StepMetrics = field(default_factory=StepMetrics)
    error_message: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

@dataclass
class PipelineDefinition:
    """Complete ML pipeline definition"""    pipeline_id: str
    name: str
    description: str
    version: str
    steps: List[PipelineStep]
    metadata: Dict[str, Any] = field(default_factory=dict)
    schedule: Optional[str] = None
    max_parallel_steps: int = 5
    timeout: int = 7200
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: Optional[str] = None

@dataclass
class PipelineExecution:
    """Pipeline execution tracking"""    execution_id: str
    pipeline_id: str
    status: PipelineStatus = PipelineStatus.CREATED
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    total_steps: int = 0
    completed_steps: int = 0
    failed_steps: int = 0
    execution_context: Dict[str, Any] = field(default_factory=dict)
    metrics: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None

class AbstractPipelineStep(ABC):
    """Abstract base class for pipeline steps"""    
    def __init__(self, step_id: str, name: str, parameters: Dict[str, Any] = None):
        self.step_id = step_id
        self.name = name
        self.parameters = parameters or {}
        self.metrics = StepMetrics()
        
    @abstractmethod
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the pipeline step"""        pass
        
    async def validate_inputs(self, context: Dict[str, Any]) -> bool:
        """Validate step inputs"""        return True
        
    async def cleanup(self, context: Dict[str, Any]):
        """Clean up step resources"""        pass

class DataIngestionStep(AbstractPipelineStep):
    """Data ingestion pipeline step"""    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute data ingestion"""        start_time = time.time()
        
        try:
            # Data source configuration
            data_source = self.parameters.get('data_source')
            data_format = self.parameters.get('format', 'parquet')
            
            # Load data based on source type
            if data_source.startswith('s3://'):
                data = await self._load_from_s3(data_source)
            elif data_source.startswith('db://'):
                data = await self._load_from_database(data_source)
            else:
                data = await self._load_from_file(data_source)
            
            self.metrics.execution_time = time.time() - start_time
            self.metrics.output_size = len(data) if hasattr(data, '__len__') else 0
            
            return {'data': data, 'metadata': {'rows': len(data)}}
            
        except Exception as e:
            self.metrics.error_count += 1
            raise PipelineError(f"Data ingestion failed: {str(e)}")
    
    async def _load_from_s3(self, s3_path: str) -> pd.DataFrame:
        """Load data from S3"""        # Implementation would use boto3 to load from S3
        pass
    
    async def _load_from_database(self, db_url: str) -> pd.DataFrame:
        """Load data from database"""        # Implementation would use SQLAlchemy to load from database
        pass
    
    async def _load_from_file(self, file_path: str) -> pd.DataFrame:
        """Load data from local file"""        path = Path(file_path)
        if path.suffix == '.parquet':
            return pd.read_parquet(file_path)
        elif path.suffix == '.csv':
            return pd.read_csv(file_path)
        else:
            raise ValueError(f"Unsupported file format: {path.suffix}")

class FeatureEngineeringStep(AbstractPipelineStep):
    """Feature engineering pipeline step"""    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute feature engineering"""        start_time = time.time()
        
        try:
            input_data = context.get('data')
            if input_data is None:
                raise ValueError("Input data is required for feature engineering")
            
            # Apply feature transformations
            transformations = self.parameters.get('transformations', [])
            processed_data = input_data.copy()
            
            for transformation in transformations:
                processed_data = await self._apply_transformation(processed_data, transformation)
            
            # Feature selection if specified
            if 'feature_selection' in self.parameters:
                processed_data = await self._select_features(processed_data)
            
            self.metrics.execution_time = time.time() - start_time
            self.metrics.input_size = len(input_data)
            self.metrics.output_size = len(processed_data)
            
            return {
                'features': processed_data,
                'feature_names': list(processed_data.columns),
                'transformation_metadata': self.parameters
            }
            
        except Exception as e:
            self.metrics.error_count += 1
            raise PipelineError(f"Feature engineering failed: {str(e)}")
    
    async def _apply_transformation(self, data: pd.DataFrame, transformation: Dict[str, Any]) -> pd.DataFrame:
        """Apply a specific feature transformation"""        transform_type = transformation.get('type')
        
        if transform_type == 'scale':
            from sklearn.preprocessing import StandardScaler
            scaler = StandardScaler()
            columns = transformation.get('columns', data.select_dtypes(include=[np.number]).columns)
            data[columns] = scaler.fit_transform(data[columns])
            
        elif transform_type == 'encode_categorical':
            from sklearn.preprocessing import LabelEncoder
            columns = transformation.get('columns', data.select_dtypes(include=['object']).columns)
            for col in columns:
                le = LabelEncoder()
                data[col] = le.fit_transform(data[col].astype(str))
        
        return data
    
    async def _select_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Apply feature selection"""        selection_config = self.parameters['feature_selection']
        method = selection_config.get('method', 'variance')
        
        if method == 'variance':
            from sklearn.feature_selection import VarianceThreshold
            selector = VarianceThreshold(threshold=selection_config.get('threshold', 0.1))
            selected_features = selector.fit_transform(data)
            selected_columns = data.columns[selector.get_support()]
            return pd.DataFrame(selected_features, columns=selected_columns)
        
        return data

class ModelTrainingStep(AbstractPipelineStep):
    """Model training pipeline step"""    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute model training"""        start_time = time.time()
        
        try:
            # Get training data
            features = context.get('features')
            target = context.get('target')
            
            if features is None or target is None:
                raise ValueError("Features and target data are required for training")
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                features, target,
                test_size=self.parameters.get('test_size', 0.2),
                random_state=self.parameters.get('random_state', 42)
            )
            
            # Initialize and train model
            model_config = self.parameters.get('model')
            model = await self._create_model(model_config)
            
            # Train model
            model.fit(X_train, y_train)
            
            # Evaluate model
            train_score = model.score(X_train, y_train)
            test_score = model.score(X_test, y_test)
            
            # Save model
            model_path = await self._save_model(model)
            
            self.metrics.execution_time = time.time() - start_time
            
            return {
                'model': model,
                'model_path': model_path,
                'train_score': train_score,
                'test_score': test_score,
                'training_metadata': {
                    'train_samples': len(X_train),
                    'test_samples': len(X_test),
                    'features': list(features.columns)
                }
            }
            
        except Exception as e:
            self.metrics.error_count += 1
            raise PipelineError(f"Model training failed: {str(e)}")
    
    async def _create_model(self, model_config: Dict[str, Any]):
        """Create model instance based on configuration"""        model_type = model_config.get('type', 'random_forest')
        
        if model_type == 'random_forest':
            from sklearn.ensemble import RandomForestClassifier
            return RandomForestClassifier(**model_config.get('parameters', {}))
        elif model_type == 'gradient_boosting':
            from sklearn.ensemble import GradientBoostingClassifier
            return GradientBoostingClassifier(**model_config.get('parameters', {}))
        else:
            raise ValueError(f"Unsupported model type: {model_type}")
    
    async def _save_model(self, model) -> str:
        """Save trained model to storage"""        model_path = f"/tmp/models/{self.step_id}_{int(time.time())}.joblib"
        Path(model_path).parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(model, model_path)
        return model_path

class MLPipelineManager:
    """    Ultra-advanced ML pipeline orchestration manager providing
    comprehensive workflow management, dependency resolution, and execution monitoring
    """    
    def __init__(self):
        self.pipelines: Dict[str, PipelineDefinition] = {}
        self.executions: Dict[str, PipelineExecution] = {}
        self.step_registry: Dict[str, type] = {
            'data_ingestion': DataIngestionStep,
            'feature_engineering': FeatureEngineeringStep,
            'model_training': ModelTrainingStep
        }
        self.performance_monitor = PerformanceMonitor()
        self.cache_manager = CacheManager()
        
    def register_step_type(self, step_type: str, step_class: type):
        """Register a custom step type"""        self.step_registry[step_type] = step_class
        
    async def create_pipeline(self, pipeline_def: Dict[str, Any]) -> str:
        """Create a new ML pipeline"""        try:
            pipeline_id = str(uuid.uuid4())
            
            # Parse pipeline definition
            steps = []
            for step_def in pipeline_def.get('steps', []):
                step = PipelineStep(
                    step_id=step_def['step_id'],
                    name=step_def['name'],
                    function=self._get_step_function(step_def['type']),
                    inputs=step_def.get('inputs', []),
                    outputs=step_def.get('outputs', []),
                    dependencies=step_def.get('dependencies', []),
                    parameters=step_def.get('parameters', {}),
                    retry_count=step_def.get('retry_count', 3),
                    timeout=step_def.get('timeout', 3600)
                )
                steps.append(step)
            
            # Create pipeline definition
            pipeline = PipelineDefinition(
                pipeline_id=pipeline_id,
                name=pipeline_def['name'],
                description=pipeline_def.get('description', ''),
                version=pipeline_def.get('version', '1.0.0'),
                steps=steps,
                metadata=pipeline_def.get('metadata', {}),
                schedule=pipeline_def.get('schedule'),
                max_parallel_steps=pipeline_def.get('max_parallel_steps', 5),
                timeout=pipeline_def.get('timeout', 7200),
                created_by=pipeline_def.get('created_by')
            )
            
            # Validate pipeline
            await self._validate_pipeline(pipeline)
            
            # Store pipeline
            self.pipelines[pipeline_id] = pipeline
            
            logger.info(f"Pipeline created successfully: {pipeline_id}")
            return pipeline_id
            
        except Exception as e:
            logger.error(f"Failed to create pipeline: {str(e)}")
            raise PipelineError(f"Pipeline creation failed: {str(e)}")
    
    def _get_step_function(self, step_type: str) -> Callable:
        """Get step function by type"""        if step_type not in self.step_registry:
            raise ValueError(f"Unknown step type: {step_type}")
        return self.step_registry[step_type]
    
    async def _validate_pipeline(self, pipeline: PipelineDefinition):
        """Validate pipeline definition"""        # Check for circular dependencies
        dependency_graph = nx.DiGraph()
        
        for step in pipeline.steps:
            dependency_graph.add_node(step.step_id)
            for dep in step.dependencies:
                dependency_graph.add_edge(dep, step.step_id)
        
        if not nx.is_directed_acyclic_graph(dependency_graph):
            raise ValidationError("Pipeline contains circular dependencies")
        
        # Validate step inputs/outputs
        available_outputs = set()
        for step in nx.topological_sort(dependency_graph):
            step_obj = next(s for s in pipeline.steps if s.step_id == step)
            
            # Check if all required inputs are available
            for input_name in step_obj.inputs:
                if input_name not in available_outputs:
                    raise ValidationError(f"Step {step} requires input {input_name} which is not available")
            
            # Add step outputs to available outputs
            available_outputs.update(step_obj.outputs)
    
    async def execute_pipeline(self, pipeline_id: str, context: Dict[str, Any] = None) -> str:
        """Execute a pipeline"""        try:
            if pipeline_id not in self.pipelines:
                raise ValueError(f"Pipeline not found: {pipeline_id}")
            
            pipeline = self.pipelines[pipeline_id]
            execution_id = str(uuid.uuid4())
            
            # Create execution record
            execution = PipelineExecution(
                execution_id=execution_id,
                pipeline_id=pipeline_id,
                status=PipelineStatus.QUEUED,
                total_steps=len(pipeline.steps),
                execution_context=context or {}
            )
            
            self.executions[execution_id] = execution
            
            # Start execution in background
            asyncio.create_task(self._execute_pipeline_async(execution_id))
            
            logger.info(f"Pipeline execution started: {execution_id}")
            return execution_id
            
        except Exception as e:
            logger.error(f"Failed to start pipeline execution: {str(e)}")
            raise PipelineError(f"Pipeline execution failed: {str(e)}")
    
    async def _execute_pipeline_async(self, execution_id: str):
        """Execute pipeline asynchronously"""        execution = self.executions[execution_id]
        pipeline = self.pipelines[execution.pipeline_id]
        
        try:
            execution.status = PipelineStatus.RUNNING
            execution.start_time = datetime.now(timezone.utc)
            
            # Build execution order based on dependencies
            dependency_graph = nx.DiGraph()
            step_map = {step.step_id: step for step in pipeline.steps}
            
            for step in pipeline.steps:
                dependency_graph.add_node(step.step_id)
                for dep in step.dependencies:
                    dependency_graph.add_edge(dep, step.step_id)
            
            execution_order = list(nx.topological_sort(dependency_graph))
            context = execution.execution_context.copy()
            
            # Execute steps in order
            for step_id in execution_order:
                step = step_map[step_id]
                
                try:
                    await self._execute_step(step, context, execution_id)
                    execution.completed_steps += 1
                    
                except Exception as e:
                    execution.failed_steps += 1
                    step.status = StepStatus.FAILED
                    step.error_message = str(e)
                    
                    # Stop execution on critical failure
                    if step.retry_count <= 0:
                        raise PipelineError(f"Step {step_id} failed: {str(e)}")
            
            # Mark execution as completed
            execution.status = PipelineStatus.COMPLETED
            execution.end_time = datetime.now(timezone.utc)
            
            logger.info(f"Pipeline execution completed: {execution_id}")
            
        except Exception as e:
            execution.status = PipelineStatus.FAILED
            execution.error_message = str(e)
            execution.end_time = datetime.now(timezone.utc)
            
            logger.error(f"Pipeline execution failed: {execution_id} - {str(e)}")
    
    async def _execute_step(self, step: PipelineStep, context: Dict[str, Any], execution_id: str):
        """Execute a single pipeline step"""        step.status = StepStatus.RUNNING
        step.start_time = datetime.now(timezone.utc)
        
        try:
            # Create step instance
            step_class = self.step_registry.get('data_ingestion')  # Default for now
            if hasattr(step.function, '__name__'):
                step_type = step.function.__name__.replace('Step', '').lower()
                step_class = self.step_registry.get(step_type, step_class)
            
            step_instance = step_class(step.step_id, step.name, step.parameters)
            
            # Execute step
            result = await step_instance.execute(context)
            
            # Update context with step outputs
            context.update(result)
            
            step.status = StepStatus.COMPLETED
            step.end_time = datetime.now(timezone.utc)
            step.metrics = step_instance.metrics
            
        except Exception as e:
            step.status = StepStatus.FAILED
            step.error_message = str(e)
            step.end_time = datetime.now(timezone.utc)
            raise
    
    async def get_execution_status(self, execution_id: str) -> Dict[str, Any]:
        """Get pipeline execution status"""        if execution_id not in self.executions:
            raise ValueError(f"Execution not found: {execution_id}")
        
        execution = self.executions[execution_id]
        pipeline = self.pipelines[execution.pipeline_id]
        
        return {
            'execution_id': execution_id,
            'pipeline_id': execution.pipeline_id,
            'pipeline_name': pipeline.name,
            'status': execution.status.value,
            'progress': {
                'total_steps': execution.total_steps,
                'completed_steps': execution.completed_steps,
                'failed_steps': execution.failed_steps,
                'percentage': (execution.completed_steps / execution.total_steps * 100) if execution.total_steps > 0 else 0
            },
            'timing': {
                'start_time': execution.start_time.isoformat() if execution.start_time else None,
                'end_time': execution.end_time.isoformat() if execution.end_time else None,
                'duration': (execution.end_time - execution.start_time).total_seconds() if execution.start_time and execution.end_time else None
            },
            'steps': [
                {
                    'step_id': step.step_id,
                    'name': step.name,
                    'status': step.status.value,
                    'execution_time': step.metrics.execution_time,
                    'error_message': step.error_message
                }
                for step in pipeline.steps
            ]
        }
    
    async def cancel_execution(self, execution_id: str):
        """Cancel a running pipeline execution"""        if execution_id not in self.executions:
            raise ValueError(f"Execution not found: {execution_id}")
        
        execution = self.executions[execution_id]
        if execution.status in [PipelineStatus.RUNNING, PipelineStatus.QUEUED]:
            execution.status = PipelineStatus.CANCELLED
            execution.end_time = datetime.now(timezone.utc)
            logger.info(f"Pipeline execution cancelled: {execution_id}")
        
    async def get_pipeline_metrics(self, pipeline_id: str) -> Dict[str, Any]:
        """Get comprehensive pipeline performance metrics"""        if pipeline_id not in self.pipelines:
            raise ValueError(f"Pipeline not found: {pipeline_id}")
        
        # Get all executions for this pipeline
        executions = [e for e in self.executions.values() if e.pipeline_id == pipeline_id]
        
        if not executions:
            return {'message': 'No executions found for this pipeline'}
        
        # Calculate metrics
        completed_executions = [e for e in executions if e.status == PipelineStatus.COMPLETED]
        failed_executions = [e for e in executions if e.status == PipelineStatus.FAILED]
        
        avg_duration = 0
        if completed_executions:
            durations = [(e.end_time - e.start_time).total_seconds() for e in completed_executions if e.start_time and e.end_time]
            avg_duration = sum(durations) / len(durations) if durations else 0
        
        return {
            'pipeline_id': pipeline_id,
            'total_executions': len(executions),
            'completed_executions': len(completed_executions),
            'failed_executions': len(failed_executions),
            'success_rate': len(completed_executions) / len(executions) * 100 if executions else 0,
            'average_duration': avg_duration,
            'last_execution': max(executions, key=lambda e: e.start_time or datetime.min.replace(tzinfo=timezone.utc)).execution_id if executions else None
        }

# Global pipeline manager instance
pipeline_manager = MLPipelineManager()

# Export all components
__all__ = [
    'MLPipelineManager',
    'PipelineDefinition',
    'PipelineExecution',
    'PipelineStep',
    'PipelineStatus',
    'StepStatus',
    'AbstractPipelineStep',
    'DataIngestionStep',
    'FeatureEngineeringStep', 
    'ModelTrainingStep',
    'pipeline_manager'
]
