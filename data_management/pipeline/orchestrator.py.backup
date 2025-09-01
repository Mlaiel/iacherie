"""Advanced Data Pipeline Orchestrator
Professional Industrial Data Processing Engine

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 IA Influencer Agent Platform
License: Proprietary - All Rights Reserved

WARNING: This code is proprietary and confidential. Any unauthorized copying,
distribution, or use without explicit written permission from Fahed Mlaiel
is strictly prohibited and may result in legal action.
"""
import asyncio
import json
import logging
import uuid
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Union, Tuple, Any, Callable
from enum import Enum
from dataclasses import dataclass, field
import pandas as pd
import numpy as np
from abc import ABC, abstractmethod

from backend.core.database import get_database
from backend.core.exceptions import ProcessingError, ValidationError
from backend.core.security import SecurityManager
from backend.utils.monitoring import MetricsCollector
from backend.utils.storage import CloudStorageManager
from backend.utils.notifications import NotificationManager

logger = logging.getLogger(__name__)


class PipelineStatus(Enum):
    """Pipeline execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"
    RETRYING = "retrying"


class TaskType(Enum):
    """Data processing task types"""
    EXTRACTION = "extraction"
    TRANSFORMATION = "transformation"
    VALIDATION = "validation"
    ENRICHMENT = "enrichment"
    FINGERPRINTING = "fingerprinting"
    ANALYTICS = "analytics"
    STORAGE = "storage"
    NOTIFICATION = "notification"


class Priority(Enum):
    """Task priority levels"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class PipelineTask:
    """Data pipeline task definition"""
    id: str
    name: str
    task_type: TaskType
    processor_class: str
    input_data: Dict[str, Any]
    config: Dict[str, Any]
    dependencies: List[str] = field(default_factory=list)
    priority: Priority = Priority.NORMAL
    timeout_seconds: int = 3600
    retry_count: int = 3
    retry_delay: int = 60
    status: PipelineStatus = PipelineStatus.PENDING
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    output_data: Optional[Dict[str, Any]] = None
    metrics: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PipelineDefinition:
    """Data pipeline definition"""
    id: str
    name: str
    description: str
    user_id: str
    tasks: List[PipelineTask]
    schedule: Optional[str] = None
    enabled: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class TaskProcessor(ABC):
    """Abstract base class for task processors"""
    
    @abstractmethod
    async def process(self, input_data: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        """Process task with input data and configuration"""
        pass
    
    @abstractmethod
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate task configuration"""
        pass


class DataPipelineOrchestrator:
    """Advanced data pipeline orchestration engine"""
    
    def __init__(self):
        self.db = get_database()
        self.security = SecurityManager()
        self.metrics = MetricsCollector()
        self.storage = CloudStorageManager()
        self.notifications = NotificationManager()
        
        # Task processors registry
        self.processors: Dict[str, TaskProcessor] = {}
        
        # Pipeline execution tracking
        self.running_pipelines: Dict[str, asyncio.Task] = {}
        self.task_queue: asyncio.Queue = asyncio.Queue()
        
        # Configuration
        self.max_concurrent_pipelines = 10
        self.max_concurrent_tasks = 20
        self.cleanup_interval = 3600  # 1 hour
        
        # Initialize built-in processors
        self._register_builtin_processors()

    def _register_builtin_processors(self):
        """Register built-in task processors"""
        try:
            # Register core content processing processors
            builtin_processors = [
                {
                    "name": "content_analyzer",
                    "description": "Analyze content for SEO and quality metrics",
                    "input_types": ["video", "audio", "image", "text"],
                    "output_types": ["analysis_report"],
                    "processing_time": 30
                },
                {
                    "name": "fingerprint_generator", 
                    "description": "Generate content fingerprints for protection",
                    "input_types": ["video", "audio", "image"],
                    "output_types": ["fingerprint"],
                    "processing_time": 15
                },
                {
                    "name": "seo_optimizer",
                    "description": "Optimize content for search engines", 
                    "input_types": ["text", "metadata"],
                    "output_types": ["optimized_content"],
                    "processing_time": 10
                },
                {
                    "name": "platform_distributor",
                    "description": "Distribute content to multiple platforms",
                    "input_types": ["content_package"],
                    "output_types": ["distribution_report"],
                    "processing_time": 60
                },
                {
                    "name": "monetization_tracker",
                    "description": "Track content monetization metrics",
                    "input_types": ["content_id", "platform_data"],
                    "output_types": ["monetization_report"],
                    "processing_time": 5
                }
            ]
            
            # Register each processor
            for processor in builtin_processors:
                if not hasattr(self, 'registered_processors'):
                    self.registered_processors = {}
                    
                self.registered_processors[processor["name"]] = processor
                logger.info(f"Registered built-in processor: {processor['name']}")
                
            logger.info(f"Registered {len(builtin_processors)} built-in processors")
            
        except Exception as e:
            logger.error(f"Failed to register built-in processors: {e}")
            raise

    async def start(self):
        """Start the pipeline orchestrator"""
        logger.info("Starting data pipeline orchestrator")
        
        # Start worker tasks
        for i in range(self.max_concurrent_tasks):
            asyncio.create_task(self._task_worker(f"worker-{i}"))
        
        # Start cleanup task
        asyncio.create_task(self._cleanup_worker())
        
        # Start scheduler
        asyncio.create_task(self._scheduler_worker())

    async def register_processor(self, name: str, processor: TaskProcessor):
        """Register a custom task processor"""
        self.processors[name] = processor
        logger.info(f"Registered processor: {name}")

    async def create_pipeline(self, definition: PipelineDefinition) -> str:
        """Create a new data pipeline"""
        try:
            # Validate pipeline definition
            await self._validate_pipeline_definition(definition)
            
            # Store pipeline in database
            pipeline_id = await self._store_pipeline_definition(definition)
            
            logger.info(f"Created pipeline: {pipeline_id}")
            return pipeline_id
            
        except Exception as e:
            logger.error(f"Error creating pipeline: {str(e)}")
            raise ProcessingError(f"Pipeline creation failed: {str(e)}")

    async def _validate_pipeline_definition(self, definition: PipelineDefinition):
        """Validate pipeline definition"""
        if not definition.name:
            raise ValidationError("Pipeline name is required")
        
        if not definition.tasks:
            raise ValidationError("Pipeline must have at least one task")
        
        # Validate task dependencies
        task_ids = {task.id for task in definition.tasks}
        for task in definition.tasks:
            for dep_id in task.dependencies:
                if dep_id not in task_ids:
                    raise ValidationError(f"Task {task.id} has invalid dependency: {dep_id}")
        
        # Check for circular dependencies
        if self._has_circular_dependencies(definition.tasks):
            raise ValidationError("Pipeline has circular dependencies")
        
        # Validate processor classes
        for task in definition.tasks:
            if task.processor_class not in self.processors:
                raise ValidationError(f"Unknown processor class: {task.processor_class}")
            
            processor = self.processors[task.processor_class]
            if not processor.validate_config(task.config):
                raise ValidationError(f"Invalid config for task {task.id}")

    def _has_circular_dependencies(self, tasks: List[PipelineTask]) -> bool:
        """Check for circular dependencies in tasks"""
        # Build dependency graph
        graph = {task.id: task.dependencies for task in tasks}
        
        # Use DFS to detect cycles
        visited = set()
        rec_stack = set()
        
        def has_cycle(node):
            if node in rec_stack:
                return True
            if node in visited:
                return False
            
            visited.add(node)
            rec_stack.add(node)
            
            for neighbor in graph.get(node, []):
                if has_cycle(neighbor):
                    return True
            
            rec_stack.remove(node)
            return False
        
        for task_id in graph:
            if task_id not in visited:
                if has_cycle(task_id):
                    return True
        
        return False

    async def _store_pipeline_definition(self, definition: PipelineDefinition) -> str:
        """Store pipeline definition in database"""
        try:
            query = """
            INSERT INTO data_pipelines (
                id, name, description, user_id, definition,
                schedule, enabled, created_at, updated_at
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
            RETURNING id
            """
            
            pipeline_data = {
                'tasks': [self._task_to_dict(task) for task in definition.tasks],
                'metadata': {
                    'created_by': definition.user_id,
                    'version': '1.0'
                }
            }
            
            row = await self.db.fetchrow(
                query,
                definition.id,
                definition.name,
                definition.description,
                definition.user_id,
                json.dumps(pipeline_data),
                definition.schedule,
                definition.enabled,
                definition.created_at,
                definition.updated_at
            )
            
            return row['id']
            
        except Exception as e:
            logger.error(f"Error storing pipeline definition: {str(e)}")
            raise ProcessingError(f"Pipeline storage failed: {str(e)}")

    def _task_to_dict(self, task: PipelineTask) -> Dict[str, Any]:
        """Convert task to dictionary for storage"""
        return {
            'id': task.id,
            'name': task.name,
            'task_type': task.task_type.value,
            'processor_class': task.processor_class,
            'input_data': task.input_data,
            'config': task.config,
            'dependencies': task.dependencies,
            'priority': task.priority.value,
            'timeout_seconds': task.timeout_seconds,
            'retry_count': task.retry_count,
            'retry_delay': task.retry_delay,
            'status': task.status.value,
            'created_at': task.created_at.isoformat(),
            'started_at': task.started_at.isoformat() if task.started_at else None,
            'completed_at': task.completed_at.isoformat() if task.completed_at else None,
            'error_message': task.error_message,
            'output_data': task.output_data,
            'metrics': task.metrics
        }

    async def execute_pipeline(
        self,
        pipeline_id: str,
        input_data: Optional[Dict[str, Any]] = None,
        override_config: Optional[Dict[str, Any]] = None
    ) -> str:
        """Execute a data pipeline"""
        try:
            # Load pipeline definition
            definition = await self._load_pipeline_definition(pipeline_id)
            
            if not definition.enabled:
                raise ValidationError(f"Pipeline {pipeline_id} is disabled")
            
            # Create execution instance
            execution_id = str(uuid.uuid4())
            
            # Prepare tasks for execution
            tasks = self._prepare_tasks_for_execution(
                definition.tasks,
                input_data or {},
                override_config or {}
            )
            
            # Create execution record
            await self._create_execution_record(execution_id, pipeline_id, tasks)
            
            # Start pipeline execution
            execution_task = asyncio.create_task(
                self._execute_pipeline_async(execution_id, tasks)
            )
            
            self.running_pipelines[execution_id] = execution_task
            
            logger.info(f"Started pipeline execution: {execution_id}")
            return execution_id
            
        except Exception as e:
            logger.error(f"Error executing pipeline: {str(e)}")
            raise ProcessingError(f"Pipeline execution failed: {str(e)}")

    async def _load_pipeline_definition(self, pipeline_id: str) -> PipelineDefinition:
        """Load pipeline definition from database"""
        try:
            query = """
            SELECT id, name, description, user_id, definition,
                   schedule, enabled, created_at, updated_at
            FROM data_pipelines
            WHERE id = $1
            """
            
            row = await self.db.fetchrow(query, pipeline_id)
            
            if not row:
                raise ValidationError(f"Pipeline not found: {pipeline_id}")
            
            pipeline_data = json.loads(row['definition'])
            tasks = [self._dict_to_task(task_data) for task_data in pipeline_data['tasks']]
            
            return PipelineDefinition(
                id=row['id'],
                name=row['name'],
                description=row['description'],
                user_id=row['user_id'],
                tasks=tasks,
                schedule=row['schedule'],
                enabled=row['enabled'],
                created_at=row['created_at'],
                updated_at=row['updated_at']
            )
            
        except Exception as e:
            logger.error(f"Error loading pipeline definition: {str(e)}")
            raise ProcessingError(f"Pipeline loading failed: {str(e)}")

    def _dict_to_task(self, task_data: Dict[str, Any]) -> PipelineTask:
        """Convert dictionary to task object"""
        return PipelineTask(
            id=task_data['id'],
            name=task_data['name'],
            task_type=TaskType(task_data['task_type']),
            processor_class=task_data['processor_class'],
            input_data=task_data['input_data'],
            config=task_data['config'],
            dependencies=task_data['dependencies'],
            priority=Priority(task_data['priority']),
            timeout_seconds=task_data['timeout_seconds'],
            retry_count=task_data['retry_count'],
            retry_delay=task_data['retry_delay'],
            status=PipelineStatus(task_data['status']),
            created_at=datetime.fromisoformat(task_data['created_at']),
            started_at=datetime.fromisoformat(task_data['started_at']) if task_data['started_at'] else None,
            completed_at=datetime.fromisoformat(task_data['completed_at']) if task_data['completed_at'] else None,
            error_message=task_data['error_message'],
            output_data=task_data['output_data'],
            metrics=task_data['metrics']
        )

    def _prepare_tasks_for_execution(
        self,
        tasks: List[PipelineTask],
        input_data: Dict[str, Any],
        override_config: Dict[str, Any]
    ) -> List[PipelineTask]:
        """Prepare tasks for execution with input data and config overrides"""
        prepared_tasks = []
        
        for task in tasks:
            # Create a copy of the task
            prepared_task = PipelineTask(
                id=f"{task.id}_{uuid.uuid4().hex[:8]}",
                name=task.name,
                task_type=task.task_type,
                processor_class=task.processor_class,
                input_data={**task.input_data, **input_data},
                config={**task.config, **override_config},
                dependencies=task.dependencies,
                priority=task.priority,
                timeout_seconds=task.timeout_seconds,
                retry_count=task.retry_count,
                retry_delay=task.retry_delay,
                status=PipelineStatus.PENDING
            )
            
            prepared_tasks.append(prepared_task)
        
        return prepared_tasks

    async def _create_execution_record(
        self,
        execution_id: str,
        pipeline_id: str,
        tasks: List[PipelineTask]
    ):
        """Create execution record in database"""
        try:
            query = """
            INSERT INTO pipeline_executions (
                id, pipeline_id, status, tasks, created_at, updated_at
            ) VALUES ($1, $2, $3, $4, $5, $6)
            """
            
            tasks_data = [self._task_to_dict(task) for task in tasks]
            
            await self.db.execute(
                query,
                execution_id,
                pipeline_id,
                PipelineStatus.RUNNING.value,
                json.dumps(tasks_data),
                datetime.now(timezone.utc),
                datetime.now(timezone.utc)
            )
            
        except Exception as e:
            logger.error(f"Error creating execution record: {str(e)}")
            raise ProcessingError(f"Execution record creation failed: {str(e)}")

    async def _execute_pipeline_async(
        self,
        execution_id: str,
        tasks: List[PipelineTask]
    ):
        """Execute pipeline asynchronously"""
        try:
            logger.info(f"Executing pipeline: {execution_id}")
            
            # Build task dependency graph
            task_graph = self._build_task_graph(tasks)
            
            # Execute tasks in dependency order
            completed_tasks = set()
            task_results = {}
            
            while len(completed_tasks) < len(tasks):
                # Find tasks ready to execute
                ready_tasks = []
                for task in tasks:
                    if (task.id not in completed_tasks and
                        all(dep in completed_tasks for dep in task.dependencies)):
                        ready_tasks.append(task)
                
                if not ready_tasks:
                    raise ProcessingError("No tasks ready to execute - possible deadlock")
                
                # Execute ready tasks in parallel
                execution_tasks = []
                for task in ready_tasks:
                    # Merge results from dependencies
                    merged_input = task.input_data.copy()
                    for dep_id in task.dependencies:
                        if dep_id in task_results:
                            merged_input.update(task_results[dep_id])
                    
                    task.input_data = merged_input
                    execution_tasks.append(self._execute_task(task))
                
                # Wait for all ready tasks to complete
                results = await asyncio.gather(*execution_tasks, return_exceptions=True)
                
                # Process results
                for i, result in enumerate(results):
                    task = ready_tasks[i]
                    if isinstance(result, Exception):
                        task.status = PipelineStatus.FAILED
                        task.error_message = str(result)
                        task.completed_at = datetime.now(timezone.utc)
                        
                        # Fail the entire pipeline if critical task fails
                        if task.priority == Priority.CRITICAL:
                            raise ProcessingError(f"Critical task failed: {task.id}")
                    else:
                        task.status = PipelineStatus.COMPLETED
                        task.output_data = result
                        task.completed_at = datetime.now(timezone.utc)
                        task_results[task.id] = result
                    
                    completed_tasks.add(task.id)
                    
                    # Update task status in database
                    await self._update_task_status(execution_id, task)
            
            # Update execution status
            await self._update_execution_status(execution_id, PipelineStatus.COMPLETED)
            
            logger.info(f"Pipeline execution completed: {execution_id}")
            
        except Exception as e:
            logger.error(f"Pipeline execution failed: {execution_id} - {str(e)}")
            await self._update_execution_status(execution_id, PipelineStatus.FAILED, str(e))
            raise
        
        finally:
            # Clean up
            if execution_id in self.running_pipelines:
                del self.running_pipelines[execution_id]

    def _build_task_graph(self, tasks: List[PipelineTask]) -> Dict[str, List[str]]:
        """Build task dependency graph"""
        graph = {}
        for task in tasks:
            graph[task.id] = task.dependencies
        return graph

    async def _execute_task(self, task: PipelineTask) -> Dict[str, Any]:
        """Execute a single task"""
        try:
            logger.info(f"Executing task: {task.id}")
            
            task.status = PipelineStatus.RUNNING
            task.started_at = datetime.now(timezone.utc)
            
            # Get processor
            processor = self.processors[task.processor_class]
            
            # Set up timeout
            start_time = datetime.now(timezone.utc)
            
            # Execute with timeout
            result = await asyncio.wait_for(
                processor.process(task.input_data, task.config),
                timeout=task.timeout_seconds
            )
            
            # Calculate metrics
            end_time = datetime.now(timezone.utc)
            execution_time = (end_time - start_time).total_seconds()
            
            task.metrics = {
                'execution_time_seconds': execution_time,
                'memory_usage_mb': self._get_memory_usage(),
                'processed_records': result.get('processed_records', 0)
            }
            
            # Collect metrics
            await self.metrics.record_task_execution(
                task.id,
                task.task_type.value,
                execution_time,
                True
            )
            
            logger.info(f"Task completed: {task.id} in {execution_time:.2f}s")
            return result
            
        except asyncio.TimeoutError:
            error_msg = f"Task {task.id} timed out after {task.timeout_seconds}s"
            logger.error(error_msg)
            await self.metrics.record_task_execution(task.id, task.task_type.value, 0, False)
            raise ProcessingError(error_msg)
        
        except Exception as e:
            error_msg = f"Task {task.id} failed: {str(e)}"
            logger.error(error_msg)
            await self.metrics.record_task_execution(task.id, task.task_type.value, 0, False)
            raise ProcessingError(error_msg)

    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB"""
        try:
            import psutil
            process = psutil.Process()
            return process.memory_info().rss / 1024 / 1024
        except ImportError:
            return 0.0

    async def _update_task_status(self, execution_id: str, task: PipelineTask):
        """Update task status in database"""
        try:
            query = """
            UPDATE pipeline_executions
            SET tasks = jsonb_set(
                tasks,
                '{tasks}',
                (
                    SELECT jsonb_agg(
                        CASE 
                            WHEN elem->>'id' = $2 
                            THEN $3::jsonb 
                            ELSE elem 
                        END
                    )
                    FROM jsonb_array_elements(tasks->'tasks') elem
                )
            ),
            updated_at = NOW()
            WHERE id = $1
            """
            
            task_data = json.dumps(self._task_to_dict(task))
            await self.db.execute(query, execution_id, task.id, task_data)
            
        except Exception as e:
            logger.error(f"Error updating task status: {str(e)}")

    async def _update_execution_status(
        self,
        execution_id: str,
        status: PipelineStatus,
        error_message: Optional[str] = None
    ):
        """Update execution status in database"""
        try:
            query = """
            UPDATE pipeline_executions
            SET status = $2,
                error_message = $3,
                completed_at = CASE WHEN $2 IN ('completed', 'failed', 'cancelled') THEN NOW() ELSE completed_at END,
                updated_at = NOW()
            WHERE id = $1
            """
            
            await self.db.execute(query, execution_id, status.value, error_message)
            
        except Exception as e:
            logger.error(f"Error updating execution status: {str(e)}")

    async def _task_worker(self, worker_id: str):
        """Task worker for processing queued tasks"""
        logger.info(f"Started task worker: {worker_id}")
        
        while True:
            try:
                # Get task from queue
                task_info = await self.task_queue.get()
                
                if task_info is None:  # Shutdown signal
                    break
                
                # Process task
                await self._process_queued_task(task_info)
                
                # Mark task as done
                self.task_queue.task_done()
                
            except Exception as e:
                logger.error(f"Task worker {worker_id} error: {str(e)}")
                await asyncio.sleep(1)

    async def _process_queued_task(self, task_info: Dict[str, Any]):
        """Process a queued task from the pipeline"""
        try:
            import time
            import uuid
            
            task_id = task_info.get("task_id", str(uuid.uuid4()))
            processor_name = task_info.get("processor", "unknown")
            input_data = task_info.get("input_data", {})
            
            logger.info(f"Processing queued task {task_id} with processor {processor_name}")
            
            # Get processor configuration
            processor_config = self.registered_processors.get(processor_name)
            if not processor_config:
                raise ValueError(f"Unknown processor: {processor_name}")
            
            # Simulate task processing
            start_time = time.time()
            processing_time = processor_config.get("processing_time", 10)
            
            # Simulate progressive processing
            await asyncio.sleep(processing_time / 10)  # 10% of actual time for simulation
            
            # Create processing result
            result = {
                "task_id": task_id,
                "processor": processor_name,
                "status": "completed",
                "input_data": input_data,
                "output_data": {
                    "processed_at": int(time.time()),
                    "processing_duration": time.time() - start_time,
                    "result_type": processor_config.get("output_types", ["generic_output"])[0],
                    "success": True,
                    "metadata": {
                        "processor_version": "1.0",
                        "quality_score": 0.85,
                        "confidence": 0.9
                    }
                },
                "completed_at": int(time.time())
            }
            
            logger.info(f"Task {task_id} completed in {result['output_data']['processing_duration']:.2f}s")
            
            # Update task status
            if hasattr(self, 'task_results'):
                self.task_results = getattr(self, 'task_results', {})
                self.task_results[task_id] = result
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to process queued task {task_info.get('task_id', 'unknown')}: {e}")
            
            # Return error result
            return {
                "task_id": task_info.get("task_id"),
                "status": "failed", 
                "error": str(e),
                "failed_at": int(time.time())
            }

    async def _cleanup_worker(self):
        """Worker for cleaning up old executions"""
        while True:
            try:
                await self._cleanup_old_executions()
                await asyncio.sleep(self.cleanup_interval)
            except Exception as e:
                logger.error(f"Cleanup worker error: {str(e)}")
                await asyncio.sleep(60)

    async def _cleanup_old_executions(self):
        """Clean up old pipeline executions"""
        try:
            # Delete executions older than 30 days
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=30)
            
            query = """
            DELETE FROM pipeline_executions
            WHERE created_at < $1
            AND status IN ('completed', 'failed', 'cancelled')
            """
            
            result = await self.db.execute(query, cutoff_date)
            
            if result:
                deleted_count = result.split()[-1]
                logger.info(f"Cleaned up {deleted_count} old pipeline executions")
                
        except Exception as e:
            logger.error(f"Error cleaning up executions: {str(e)}")

    async def _scheduler_worker(self):
        """Worker for scheduled pipeline executions"""
        while True:
            try:
                await self._check_scheduled_pipelines()
                await asyncio.sleep(60)  # Check every minute
            except Exception as e:
                logger.error(f"Scheduler worker error: {str(e)}")
                await asyncio.sleep(60)

    async def _check_scheduled_pipelines(self):
        """Check for scheduled pipelines that need to run"""
        try:
            query = """
            SELECT id, schedule, user_id
            FROM data_pipelines
            WHERE enabled = true
            AND schedule IS NOT NULL
            """
            
            rows = await self.db.fetch(query)
            
            for row in rows:
                if self._should_run_scheduled_pipeline(row['schedule']):
                    await self.execute_pipeline(row['id'])
                    
        except Exception as e:
            logger.error(f"Error checking scheduled pipelines: {str(e)}")

    def _should_run_scheduled_pipeline(self, schedule: str) -> bool:
        """Check if scheduled pipeline should run now"""
        # This would implement cron-like scheduling logic
        # For now, return False
        return False

    async def get_pipeline_status(self, execution_id: str) -> Dict[str, Any]:
        """Get pipeline execution status"""
        try:
            query = """
            SELECT id, pipeline_id, status, tasks, created_at, 
                   completed_at, error_message, updated_at
            FROM pipeline_executions
            WHERE id = $1
            """
            
            row = await self.db.fetchrow(query, execution_id)
            
            if not row:
                raise ValidationError(f"Execution not found: {execution_id}")
            
            tasks_data = json.loads(row['tasks'])
            
            return {
                'id': row['id'],
                'pipeline_id': row['pipeline_id'],
                'status': row['status'],
                'tasks': tasks_data,
                'created_at': row['created_at'].isoformat(),
                'completed_at': row['completed_at'].isoformat() if row['completed_at'] else None,
                'error_message': row['error_message'],
                'updated_at': row['updated_at'].isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting pipeline status: {str(e)}")
            raise ProcessingError(f"Status retrieval failed: {str(e)}")

    async def cancel_pipeline(self, execution_id: str) -> bool:
        """Cancel a running pipeline execution"""
        try:
            if execution_id in self.running_pipelines:
                # Cancel the task
                task = self.running_pipelines[execution_id]
                task.cancel()
                
                # Update status
                await self._update_execution_status(
                    execution_id,
                    PipelineStatus.CANCELLED,
                    "Pipeline cancelled by user"
                )
                
                logger.info(f"Cancelled pipeline execution: {execution_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error cancelling pipeline: {str(e)}")
            raise ProcessingError(f"Pipeline cancellation failed: {str(e)}")

    async def list_pipelines(self, user_id: str) -> List[Dict[str, Any]]:
        """List pipelines for a user"""
        try:
            query = """
            SELECT id, name, description, schedule, enabled, 
                   created_at, updated_at
            FROM data_pipelines
            WHERE user_id = $1
            ORDER BY updated_at DESC
            """
            
            rows = await self.db.fetch(query, user_id)
            
            pipelines = []
            for row in rows:
                pipelines.append({
                    'id': row['id'],
                    'name': row['name'],
                    'description': row['description'],
                    'schedule': row['schedule'],
                    'enabled': row['enabled'],
                    'created_at': row['created_at'].isoformat(),
                    'updated_at': row['updated_at'].isoformat()
                })
            
            return pipelines
            
        except Exception as e:
            logger.error(f"Error listing pipelines: {str(e)}")
            raise ProcessingError(f"Pipeline listing failed: {str(e)}")

    async def get_pipeline_metrics(self, pipeline_id: str) -> Dict[str, Any]:
        """Get pipeline execution metrics"""
        try:
            query = """
            SELECT status, COUNT(*) as count,
                   AVG(EXTRACT(EPOCH FROM (completed_at - created_at))) as avg_duration
            FROM pipeline_executions
            WHERE pipeline_id = $1
            AND created_at >= NOW() - INTERVAL '30 days'
            GROUP BY status
            """
            
            rows = await self.db.fetch(query, pipeline_id)
            
            metrics = {
                'executions': {},
                'success_rate': 0.0,
                'average_duration': 0.0,
                'total_executions': 0
            }
            
            total_count = 0
            completed_count = 0
            total_duration = 0.0
            
            for row in rows:
                status = row['status']
                count = row['count']
                avg_duration = row['avg_duration'] or 0
                
                metrics['executions'][status] = count
                total_count += count
                
                if status == 'completed':
                    completed_count += count
                    total_duration += avg_duration * count
            
            metrics['total_executions'] = total_count
            
            if total_count > 0:
                metrics['success_rate'] = completed_count / total_count
            
            if completed_count > 0:
                metrics['average_duration'] = total_duration / completed_count
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error getting pipeline metrics: {str(e)}")
            raise ProcessingError(f"Metrics retrieval failed: {str(e)}")
