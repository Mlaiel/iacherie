"""ETL Pipeline Orchestrator - Enterprise Data Pipeline Management
================================================================

Advanced orchestration for Extract, Transform, Load operations with
intelligent scheduling, monitoring, and parallel processing capabilities.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import json
import hashlib
from typing import Dict, List, Optional, Any, Callable, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import uuid
from pathlib import Path
import traceback

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker
import redis.asyncio as redis
import httpx
import aiofiles
from croniter import croniter


class PipelineStatus(Enum):
    """Pipeline execution status."""
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"


class StepType(Enum):
    """Pipeline step types."""
    EXTRACT = "extract"
    TRANSFORM = "transform"
    LOAD = "load"
    VALIDATE = "validate"
    NOTIFY = "notify"
    CUSTOM = "custom"


class ExecutionMode(Enum):
    """Pipeline execution modes."""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    CONDITIONAL = "conditional"
    BATCH = "batch"
    STREAMING = "streaming"


@dataclass
class DataSource:
    """Data source configuration."""
    id: str
    name: str
    type: str  # api, database, file, stream
    connection_params: Dict[str, Any]
    auth_config: Optional[Dict[str, Any]] = None
    rate_limit: Optional[int] = None
    retry_config: Dict[str, Any] = field(default_factory=lambda: {"max_retries": 3, "delay": 1})
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PipelineStep:
    """Individual pipeline step configuration."""
    id: str
    name: str
    type: StepType
    function: Optional[Callable] = None
    config: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    timeout: float = 300.0
    retry_config: Dict[str, Any] = field(default_factory=lambda: {"max_retries": 3, "delay": 1})
    enabled: bool = True
    priority: int = 0


@dataclass
class Pipeline:
    """ETL Pipeline definition."""
    id: str
    name: str
    description: str
    steps: List[PipelineStep]
    data_sources: List[DataSource]
    execution_mode: ExecutionMode = ExecutionMode.SEQUENTIAL
    schedule: Optional[str] = None  # Cron expression
    max_parallel_jobs: int = 1
    timeout: float = 3600.0
    enabled: bool = True
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PipelineExecution:
    """Pipeline execution instance."""
    id: str
    pipeline_id: str
    status: PipelineStatus
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    current_step: Optional[str] = None
    step_results: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class StepExecution:
    """Pipeline step execution instance."""
    id: str
    execution_id: str
    step_id: str
    status: PipelineStatus
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    input_data: Optional[Any] = None
    output_data: Optional[Any] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    metrics: Dict[str, Any] = field(default_factory=dict)


Base = declarative_base()


class PipelineExecutionModel(Base):
    """Pipeline execution database model."""
    __tablename__ = 'pipeline_executions'
    
    id = sa.Column(sa.String(36), primary_key=True)
    pipeline_id = sa.Column(sa.String(36), nullable=False)
    status = sa.Column(sa.String(20), nullable=False)
    started_at = sa.Column(sa.DateTime)
    completed_at = sa.Column(sa.DateTime)
    current_step = sa.Column(sa.String(100))
    step_results = sa.Column(sa.Text)
    errors = sa.Column(sa.Text)
    metrics = sa.Column(sa.Text)
    metadata = sa.Column(sa.Text)
    created_at = sa.Column(sa.DateTime, default=datetime.utcnow)


class ETLPipelineOrchestrator:
    """Advanced ETL pipeline orchestration engine."""
    
    def __init__(
        self,
        database_url: str,
        redis_url: str,
        config: Optional[Dict[str, Any]] = None
    ):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Database setup
        self.engine = create_async_engine(database_url)
        self.async_session = sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )
        
        # Redis setup for coordination and caching
        self.redis_url = redis_url
        self.redis_client = None
        
        # Pipeline state
        self.pipelines: Dict[str, Pipeline] = {}
        self.active_executions: Dict[str, PipelineExecution] = {}
        self.data_extractors: Dict[str, Callable] = {}
        self.data_transformers: Dict[str, Callable] = {}
        self.data_loaders: Dict[str, Callable] = {}
        
        # Scheduler state
        self.scheduler_running = False
        self.scheduler_task: Optional[asyncio.Task] = None
        self.execution_tasks: Dict[str, asyncio.Task] = {}
        
        # Performance metrics
        self.orchestrator_metrics = {
            'total_executions': 0,
            'successful_executions': 0,
            'failed_executions': 0,
            'average_execution_time': 0.0,
            'total_data_processed': 0
        }
        
        # Built-in extractors, transformers, loaders
        self._setup_built_in_functions()
    
    async def initialize(self):
        """Initialize the orchestrator."""
        # Create database tables
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        # Connect to Redis
        self.redis_client = redis.from_url(self.redis_url)
        
        self.logger.info("ETL Pipeline Orchestrator initialized")
    
    def _setup_built_in_functions(self):
        """Setup built-in data processing functions."""
        # Data extractors
        self.data_extractors = {
            'api_extractor': self._extract_from_api,
            'database_extractor': self._extract_from_database,
            'file_extractor': self._extract_from_file,
            'stream_extractor': self._extract_from_stream
        }
        
        # Data transformers
        self.data_transformers = {
            'json_transformer': self._transform_json,
            'csv_transformer': self._transform_csv,
            'sql_transformer': self._transform_sql,
            'custom_transformer': self._transform_custom
        }
        
        # Data loaders
        self.data_loaders = {
            'database_loader': self._load_to_database,
            'file_loader': self._load_to_file,
            'api_loader': self._load_to_api,
            'warehouse_loader': self._load_to_warehouse
        }
    
    def register_pipeline(self, pipeline: Pipeline):
        """Register a new pipeline."""
        self.pipelines[pipeline.id] = pipeline
        self.logger.info(f"Registered pipeline: {pipeline.name}")
    
    def register_extractor(self, name: str, extractor: Callable):
        """Register custom data extractor."""
        self.data_extractors[name] = extractor
        self.logger.info(f"Registered extractor: {name}")
    
    def register_transformer(self, name: str, transformer: Callable):
        """Register custom data transformer."""
        self.data_transformers[name] = transformer
        self.logger.info(f"Registered transformer: {name}")
    
    def register_loader(self, name: str, loader: Callable):
        """Register custom data loader."""
        self.data_loaders[name] = loader
        self.logger.info(f"Registered loader: {name}")
    
    async def start_scheduler(self):
        """Start the pipeline scheduler."""
        if self.scheduler_running:
            return
        
        self.scheduler_running = True
        self.scheduler_task = asyncio.create_task(self._scheduler_loop())
        self.logger.info("Pipeline scheduler started")
    
    async def stop_scheduler(self):
        """Stop the pipeline scheduler."""
        if not self.scheduler_running:
            return
        
        self.scheduler_running = False
        if self.scheduler_task:
            self.scheduler_task.cancel()
            try:
                await self.scheduler_task
            except asyncio.CancelledError:
                pass
        
        # Cancel all running executions
        for task in self.execution_tasks.values():
            task.cancel()
        
        if self.execution_tasks:
            await asyncio.gather(*self.execution_tasks.values(), return_exceptions=True)
        
        self.logger.info("Pipeline scheduler stopped")
    
    async def _scheduler_loop(self):
        """Main scheduler loop."""
        while self.scheduler_running:
            try:
                await self._check_scheduled_pipelines()
                await asyncio.sleep(60)  # Check every minute
            except Exception as e:
                self.logger.error(f"Scheduler error: {e}")
                await asyncio.sleep(60)
    
    async def _check_scheduled_pipelines(self):
        """Check for scheduled pipeline executions."""
        current_time = datetime.now()
        
        for pipeline in self.pipelines.values():
            if not pipeline.enabled or not pipeline.schedule:
                continue
            
            # Check if pipeline should run based on schedule
            cron = croniter(pipeline.schedule, current_time)
            next_run = cron.get_prev(datetime)
            
            # Check if we should run this pipeline
            last_run_key = f"pipeline_last_run:{pipeline.id}"
            last_run_str = await self.redis_client.get(last_run_key)
            
            if last_run_str:
                last_run = datetime.fromisoformat(last_run_str.decode())
                if next_run <= last_run:
                    continue
            
            # Check max parallel jobs
            running_count = len([
                ex for ex in self.active_executions.values()
                if ex.pipeline_id == pipeline.id and ex.status == PipelineStatus.RUNNING
            ])
            
            if running_count >= pipeline.max_parallel_jobs:
                continue
            
            # Create and start execution
            execution = await self.create_execution(pipeline.id)
            await self.start_execution(execution.id)
            
            # Update last run time
            await self.redis_client.set(
                last_run_key,
                current_time.isoformat(),
                ex=86400 * 7  # Expire in 7 days
            )
    
    async def create_execution(
        self, 
        pipeline_id: str,
        trigger_data: Optional[Dict[str, Any]] = None
    ) -> PipelineExecution:
        """Create a new pipeline execution."""
        if pipeline_id not in self.pipelines:
            raise ValueError(f"Pipeline not found: {pipeline_id}")
        
        execution = PipelineExecution(
            id=str(uuid.uuid4()),
            pipeline_id=pipeline_id,
            status=PipelineStatus.PENDING,
            metadata=trigger_data or {}
        )
        
        self.active_executions[execution.id] = execution
        
        # Persist to database
        async with self.async_session() as session:
            db_execution = PipelineExecutionModel(
                id=execution.id,
                pipeline_id=execution.pipeline_id,
                status=execution.status.value,
                metadata=json.dumps(execution.metadata)
            )
            session.add(db_execution)
            await session.commit()
        
        self.logger.info(f"Created pipeline execution: {execution.id}")
        return execution
    
    async def start_execution(self, execution_id: str):
        """Start a pipeline execution."""
        if execution_id not in self.active_executions:
            raise ValueError(f"Execution not found: {execution_id}")
        
        execution = self.active_executions[execution_id]
        pipeline = self.pipelines[execution.pipeline_id]
        
        execution.status = PipelineStatus.RUNNING
        execution.started_at = datetime.now()
        
        # Update database
        await self._update_execution_status(execution)
        
        # Start execution task
        task = asyncio.create_task(self._execute_pipeline(execution, pipeline))
        self.execution_tasks[execution_id] = task
        
        self.logger.info(f"Started pipeline execution: {execution_id}")
    
    async def _execute_pipeline(self, execution: PipelineExecution, pipeline: Pipeline):
        """Execute pipeline steps."""
        try:
            if pipeline.execution_mode == ExecutionMode.SEQUENTIAL:
                await self._execute_sequential(execution, pipeline)
            elif pipeline.execution_mode == ExecutionMode.PARALLEL:
                await self._execute_parallel(execution, pipeline)
            elif pipeline.execution_mode == ExecutionMode.CONDITIONAL:
                await self._execute_conditional(execution, pipeline)
            elif pipeline.execution_mode == ExecutionMode.BATCH:
                await self._execute_batch(execution, pipeline)
            elif pipeline.execution_mode == ExecutionMode.STREAMING:
                await self._execute_streaming(execution, pipeline)
            
            # Complete execution
            execution.status = PipelineStatus.COMPLETED
            execution.completed_at = datetime.now()
            
            # Update metrics
            self.orchestrator_metrics['successful_executions'] += 1
            
        except Exception as e:
            self.logger.error(f"Pipeline execution {execution.id} failed: {e}")
            execution.status = PipelineStatus.FAILED
            execution.errors.append(str(e))
            execution.completed_at = datetime.now()
            
            self.orchestrator_metrics['failed_executions'] += 1
        
        finally:
            # Update final status
            await self._update_execution_status(execution)
            self.orchestrator_metrics['total_executions'] += 1
            
            # Calculate average execution time
            if execution.started_at and execution.completed_at:
                exec_time = (execution.completed_at - execution.started_at).total_seconds()
                total_time = self.orchestrator_metrics['average_execution_time'] * (
                    self.orchestrator_metrics['total_executions'] - 1
                )
                self.orchestrator_metrics['average_execution_time'] = (
                    total_time + exec_time
                ) / self.orchestrator_metrics['total_executions']
            
            # Clean up
            if execution.id in self.execution_tasks:
                del self.execution_tasks[execution.id]
    
    async def _execute_sequential(self, execution: PipelineExecution, pipeline: Pipeline):
        """Execute pipeline steps sequentially."""
        context = {'data': None, 'metadata': {}}
        
        for step in pipeline.steps:
            if not step.enabled:
                continue
            
            execution.current_step = step.id
            await self._update_execution_status(execution)
            
            step_execution = StepExecution(
                id=str(uuid.uuid4()),
                execution_id=execution.id,
                step_id=step.id,
                status=PipelineStatus.RUNNING,
                started_at=datetime.now(),
                input_data=context['data']
            )
            
            try:
                result = await self._execute_step(step, context, pipeline)
                context['data'] = result
                
                step_execution.status = PipelineStatus.COMPLETED
                step_execution.output_data = result
                step_execution.completed_at = datetime.now()
                
                execution.step_results[step.id] = result
                
            except Exception as e:
                step_execution.status = PipelineStatus.FAILED
                step_execution.error_message = str(e)
                step_execution.completed_at = datetime.now()
                
                if step.retry_config.get('max_retries', 0) > step_execution.retry_count:
                    step_execution.retry_count += 1
                    await asyncio.sleep(step.retry_config.get('delay', 1))
                    # Retry logic would go here
                else:
                    raise
    
    async def _execute_parallel(self, execution: PipelineExecution, pipeline: Pipeline):
        """Execute pipeline steps in parallel where possible."""
        context = {'data': None, 'metadata': {}}
        completed_steps = set()
        
        while len(completed_steps) < len([s for s in pipeline.steps if s.enabled]):
            # Find steps that can run (dependencies met)
            ready_steps = [
                step for step in pipeline.steps
                if (step.enabled and 
                    step.id not in completed_steps and
                    all(dep in completed_steps for dep in step.dependencies))
            ]
            
            if not ready_steps:
                break
            
            # Execute ready steps in parallel
            tasks = []
            for step in ready_steps:
                task = asyncio.create_task(self._execute_step(step, context, pipeline))
                tasks.append((step, task))
            
            # Wait for completion
            for step, task in tasks:
                try:
                    result = await task
                    execution.step_results[step.id] = result
                    completed_steps.add(step.id)
                except Exception as e:
                    execution.errors.append(f"Step {step.id} failed: {str(e)}")
                    raise
    
    async def _execute_conditional(self, execution: PipelineExecution, pipeline: Pipeline):
        """Execute pipeline steps based on conditions."""
        # Conditional execution logic would be implemented here
        await self._execute_sequential(execution, pipeline)
    
    async def _execute_batch(self, execution: PipelineExecution, pipeline: Pipeline):
        """Execute pipeline in batch mode."""
        # Batch execution logic would be implemented here
        await self._execute_sequential(execution, pipeline)
    
    async def _execute_streaming(self, execution: PipelineExecution, pipeline: Pipeline):
        """Execute pipeline in streaming mode."""
        # Streaming execution logic would be implemented here
        await self._execute_sequential(execution, pipeline)
    
    async def _execute_step(
        self, 
        step: PipelineStep, 
        context: Dict[str, Any], 
        pipeline: Pipeline
    ) -> Any:
        """Execute individual pipeline step."""
        start_time = datetime.now()
        
        try:
            if step.type == StepType.EXTRACT:
                result = await self._execute_extract_step(step, context, pipeline)
            elif step.type == StepType.TRANSFORM:
                result = await self._execute_transform_step(step, context, pipeline)
            elif step.type == StepType.LOAD:
                result = await self._execute_load_step(step, context, pipeline)
            elif step.type == StepType.VALIDATE:
                result = await self._execute_validate_step(step, context, pipeline)
            elif step.type == StepType.NOTIFY:
                result = await self._execute_notify_step(step, context, pipeline)
            elif step.type == StepType.CUSTOM:
                result = await self._execute_custom_step(step, context, pipeline)
            else:
                raise ValueError(f"Unknown step type: {step.type}")
            
            # Update metrics
            execution_time = (datetime.now() - start_time).total_seconds()
            self.logger.info(f"Step {step.id} completed in {execution_time:.2f}s")
            
            return result
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            self.logger.error(f"Step {step.id} failed after {execution_time:.2f}s: {e}")
            raise
    
    async def _execute_extract_step(
        self, 
        step: PipelineStep, 
        context: Dict[str, Any], 
        pipeline: Pipeline
    ) -> Any:
        """Execute data extraction step."""
        extractor_name = step.config.get('extractor')
        if extractor_name not in self.data_extractors:
            raise ValueError(f"Extractor not found: {extractor_name}")
        
        extractor = self.data_extractors[extractor_name]
        
        # Find data source
        source_id = step.config.get('source_id')
        data_source = next(
            (ds for ds in pipeline.data_sources if ds.id == source_id), None
        )
        
        if not data_source:
            raise ValueError(f"Data source not found: {source_id}")
        
        return await extractor(data_source, step.config, context)
    
    async def _execute_transform_step(
        self, 
        step: PipelineStep, 
        context: Dict[str, Any], 
        pipeline: Pipeline
    ) -> Any:
        """Execute data transformation step."""
        transformer_name = step.config.get('transformer')
        if transformer_name not in self.data_transformers:
            raise ValueError(f"Transformer not found: {transformer_name}")
        
        transformer = self.data_transformers[transformer_name]
        return await transformer(context['data'], step.config, context)
    
    async def _execute_load_step(
        self, 
        step: PipelineStep, 
        context: Dict[str, Any], 
        pipeline: Pipeline
    ) -> Any:
        """Execute data loading step."""
        loader_name = step.config.get('loader')
        if loader_name not in self.data_loaders:
            raise ValueError(f"Loader not found: {loader_name}")
        
        loader = self.data_loaders[loader_name]
        
        # Find target configuration
        target_config = step.config.get('target', {})
        
        return await loader(context['data'], target_config, context)
    
    async def _execute_validate_step(
        self, 
        step: PipelineStep, 
        context: Dict[str, Any], 
        pipeline: Pipeline
    ) -> Any:
        """Execute data validation step."""
        # Validation logic would be implemented here
        return context['data']
    
    async def _execute_notify_step(
        self, 
        step: PipelineStep, 
        context: Dict[str, Any], 
        pipeline: Pipeline
    ) -> Any:
        """Execute notification step."""
        # Notification logic would be implemented here
        return context['data']
    
    async def _execute_custom_step(
        self, 
        step: PipelineStep, 
        context: Dict[str, Any], 
        pipeline: Pipeline
    ) -> Any:
        """Execute custom step using provided function."""
        if step.function:
            return await step.function(context['data'], step.config, context)
        else:
            raise ValueError(f"No function provided for custom step: {step.id}")
    
    # Built-in data processing functions
    async def _extract_from_api(
        self, 
        data_source: DataSource, 
        config: Dict[str, Any], 
        context: Dict[str, Any]
    ) -> Any:
        """Extract data from API endpoint."""
        url = data_source.connection_params.get('url')
        headers = data_source.connection_params.get('headers', {})
        
        # Add authentication if configured
        if data_source.auth_config:
            auth_type = data_source.auth_config.get('type')
            if auth_type == 'bearer':
                headers['Authorization'] = f"Bearer {data_source.auth_config['token']}"
            elif auth_type == 'api_key':
                headers[data_source.auth_config['header']] = data_source.auth_config['key']
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
    
    async def _extract_from_database(
        self, 
        data_source: DataSource, 
        config: Dict[str, Any], 
        context: Dict[str, Any]
    ) -> Any:
        """Extract data from database."""
        # Database extraction logic would be implemented here
        return []
    
    async def _extract_from_file(
        self, 
        data_source: DataSource, 
        config: Dict[str, Any], 
        context: Dict[str, Any]
    ) -> Any:
        """Extract data from file."""
        file_path = data_source.connection_params.get('path')
        
        async with aiofiles.open(file_path, 'r') as file:
            content = await file.read()
            
            file_type = data_source.connection_params.get('type', 'json')
            if file_type == 'json':
                return json.loads(content)
            elif file_type == 'csv':
                # CSV parsing logic would be implemented here
                return content
            else:
                return content
    
    async def _extract_from_stream(
        self, 
        data_source: DataSource, 
        config: Dict[str, Any], 
        context: Dict[str, Any]
    ) -> Any:
        """Extract data from stream."""
        # Stream extraction logic would be implemented here
        return []
    
    async def _transform_json(
        self, 
        data: Any, 
        config: Dict[str, Any], 
        context: Dict[str, Any]
    ) -> Any:
        """Transform JSON data."""
        # JSON transformation logic would be implemented here
        return data
    
    async def _transform_csv(
        self, 
        data: Any, 
        config: Dict[str, Any], 
        context: Dict[str, Any]
    ) -> Any:
        """Transform CSV data."""
        # CSV transformation logic would be implemented here
        return data
    
    async def _transform_sql(
        self, 
        data: Any, 
        config: Dict[str, Any], 
        context: Dict[str, Any]
    ) -> Any:
        """Transform data using SQL."""
        # SQL transformation logic would be implemented here
        return data
    
    async def _transform_custom(
        self, 
        data: Any, 
        config: Dict[str, Any], 
        context: Dict[str, Any]
    ) -> Any:
        """Transform data using custom logic."""
        # Custom transformation logic would be implemented here
        return data
    
    async def _load_to_database(
        self, 
        data: Any, 
        config: Dict[str, Any], 
        context: Dict[str, Any]
    ) -> Any:
        """Load data to database."""
        # Database loading logic would be implemented here
        return data
    
    async def _load_to_file(
        self, 
        data: Any, 
        config: Dict[str, Any], 
        context: Dict[str, Any]
    ) -> Any:
        """Load data to file."""
        file_path = config.get('path')
        
        async with aiofiles.open(file_path, 'w') as file:
            if isinstance(data, (dict, list)):
                await file.write(json.dumps(data, indent=2))
            else:
                await file.write(str(data))
        
        return data
    
    async def _load_to_api(
        self, 
        data: Any, 
        config: Dict[str, Any], 
        context: Dict[str, Any]
    ) -> Any:
        """Load data to API endpoint."""
        url = config.get('url')
        headers = config.get('headers', {})
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=data, headers=headers)
            response.raise_for_status()
            return response.json()
    
    async def _load_to_warehouse(
        self, 
        data: Any, 
        config: Dict[str, Any], 
        context: Dict[str, Any]
    ) -> Any:
        """Load data to data warehouse."""
        # Data warehouse loading logic would be implemented here
        return data
    
    async def _update_execution_status(self, execution: PipelineExecution):
        """Update execution status in database."""
        async with self.async_session() as session:
            result = await session.execute(
                sa.select(PipelineExecutionModel).where(
                    PipelineExecutionModel.id == execution.id
                )
            )
            db_execution = result.scalar_one_or_none()
            
            if db_execution:
                db_execution.status = execution.status.value
                db_execution.started_at = execution.started_at
                db_execution.completed_at = execution.completed_at
                db_execution.current_step = execution.current_step
                db_execution.step_results = json.dumps(execution.step_results)
                db_execution.errors = json.dumps(execution.errors)
                db_execution.metrics = json.dumps(execution.metrics)
                db_execution.metadata = json.dumps(execution.metadata)
                
                await session.commit()
    
    async def get_execution_status(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """Get pipeline execution status."""
        if execution_id in self.active_executions:
            execution = self.active_executions[execution_id]
            return {
                'id': execution.id,
                'pipeline_id': execution.pipeline_id,
                'status': execution.status.value,
                'started_at': execution.started_at.isoformat() if execution.started_at else None,
                'completed_at': execution.completed_at.isoformat() if execution.completed_at else None,
                'current_step': execution.current_step,
                'step_results': execution.step_results,
                'errors': execution.errors,
                'metrics': execution.metrics
            }
        
        # Check database
        async with self.async_session() as session:
            result = await session.execute(
                sa.select(PipelineExecutionModel).where(
                    PipelineExecutionModel.id == execution_id
                )
            )
            db_execution = result.scalar_one_or_none()
            
            if db_execution:
                return {
                    'id': db_execution.id,
                    'pipeline_id': db_execution.pipeline_id,
                    'status': db_execution.status,
                    'started_at': db_execution.started_at.isoformat() if db_execution.started_at else None,
                    'completed_at': db_execution.completed_at.isoformat() if db_execution.completed_at else None,
                    'current_step': db_execution.current_step,
                    'step_results': json.loads(db_execution.step_results) if db_execution.step_results else {},
                    'errors': json.loads(db_execution.errors) if db_execution.errors else [],
                    'metrics': json.loads(db_execution.metrics) if db_execution.metrics else {}
                }
        
        return None
    
    def get_orchestrator_metrics(self) -> Dict[str, Any]:
        """Get orchestrator performance metrics."""
        return self.orchestrator_metrics.copy()
    
    async def cancel_execution(self, execution_id: str) -> bool:
        """Cancel a running pipeline execution."""
        if execution_id in self.active_executions:
            execution = self.active_executions[execution_id]
            execution.status = PipelineStatus.CANCELLED
            execution.completed_at = datetime.now()
            
            # Cancel the task
            if execution_id in self.execution_tasks:
                self.execution_tasks[execution_id].cancel()
            
            await self._update_execution_status(execution)
            self.logger.info(f"Cancelled pipeline execution: {execution_id}")
            return True
        
        return False
    
    async def cleanup_old_executions(self, older_than_days: int = 30):
        """Clean up old pipeline executions."""
        cutoff_date = datetime.now() - timedelta(days=older_than_days)
        
        async with self.async_session() as session:
            result = await session.execute(
                sa.delete(PipelineExecutionModel).where(
                    sa.and_(
                        PipelineExecutionModel.status.in_(['completed', 'failed', 'cancelled']),
                        PipelineExecutionModel.completed_at < cutoff_date
                    )
                )
            )
            await session.commit()
            
            self.logger.info(f"Cleaned up {result.rowcount} old pipeline executions")


# Example usage
if __name__ == "__main__":
    async def main():
        # Initialize orchestrator
        orchestrator = ETLPipelineOrchestrator(
            database_url="postgresql+asyncpg://user:pass@localhost/db",
            redis_url="redis://localhost:6379"
        )
        
        await orchestrator.initialize()
        
        # Define data sources
        api_source = DataSource(
            id="api_source_1",
            name="External API",
            type="api",
            connection_params={
                "url": "https://api.example.com/data",
                "headers": {"Content-Type": "application/json"}
            },
            auth_config={
                "type": "bearer",
                "token": "your-api-token"
            }
        )
        
        # Define pipeline steps
        extract_step = PipelineStep(
            id="extract_1",
            name="Extract from API",
            type=StepType.EXTRACT,
            config={
                "extractor": "api_extractor",
                "source_id": "api_source_1"
            }
        )
        
        transform_step = PipelineStep(
            id="transform_1",
            name="Transform JSON",
            type=StepType.TRANSFORM,
            config={
                "transformer": "json_transformer"
            },
            dependencies=["extract_1"]
        )
        
        load_step = PipelineStep(
            id="load_1",
            name="Load to File",
            type=StepType.LOAD,
            config={
                "loader": "file_loader",
                "target": {
                    "path": "/tmp/output.json"
                }
            },
            dependencies=["transform_1"]
        )
        
        # Create pipeline
        pipeline = Pipeline(
            id=str(uuid.uuid4()),
            name="API to File ETL",
            description="Extract data from API and load to file",
            steps=[extract_step, transform_step, load_step],
            data_sources=[api_source],
            execution_mode=ExecutionMode.SEQUENTIAL,
            schedule="0 */6 * * *"  # Every 6 hours
        )
        
        orchestrator.register_pipeline(pipeline)
        
        # Start scheduler
        await orchestrator.start_scheduler()
        
        # Create manual execution
        execution = await orchestrator.create_execution(pipeline.id)
        await orchestrator.start_execution(execution.id)
        
        # Monitor execution
        while True:
            status = await orchestrator.get_execution_status(execution.id)
            if status and status['status'] in ['completed', 'failed', 'cancelled']:
                break
            await asyncio.sleep(5)
        
        print(f"Execution completed with status: {status['status']}")
        
        await orchestrator.stop_scheduler()
    
    asyncio.run(main())