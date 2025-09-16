"""
Pipeline Orchestration - AI/ML Pipeline Infrastructure
Enterprise workflow automation and scheduling with comprehensive pipeline management.

Created by: Fahed Mlaiel (mlaiel@live.de)
Copyright: EXCLUSIVE INTELLECTUAL PROPERTY - Fahed Mlaiel
WARNING: Unauthorized use, reproduction, or distribution is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.
"""

import asyncio
import logging
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Union, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
from enum import Enum
import yaml
import croniter
import redis
import boto3
from kubernetes import client, config as k8s_config
import airflow
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.bash_operator import BashOperator
from airflow.operators.kubernetes_pod_operator import KubernetesPodOperator
from airflow.operators.dummy_operator import DummyOperator
from airflow.sensors.s3_sensor import S3KeySensor
from airflow.hooks.S3_hook import S3Hook
import celery
from celery import Celery
import ray
from ray import workflow
import prefect
from prefect import Flow, Task, Parameter
from prefect.schedules import Schedule
from prefect.schedules.clocks import CronClock
import metaflow
from metaflow import FlowSpec, step, Parameter as MFParameter


class PipelineStatus(Enum):
    """Pipeline execution status"""
    PENDING = "pending"
    SCHEDULED = "scheduled"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"
    RETRYING = "retrying"


class TaskType(Enum):
    """Pipeline task types"""
    DATA_INGESTION = "data_ingestion"
    DATA_PREPROCESSING = "data_preprocessing"
    FEATURE_ENGINEERING = "feature_engineering"
    MODEL_TRAINING = "model_training"
    MODEL_VALIDATION = "model_validation"
    MODEL_DEPLOYMENT = "model_deployment"
    MODEL_MONITORING = "model_monitoring"
    BATCH_INFERENCE = "batch_inference"
    REAL_TIME_INFERENCE = "real_time_inference"
    DATA_QUALITY_CHECK = "data_quality_check"
    MODEL_EVALUATION = "model_evaluation"
    PIPELINE_CLEANUP = "pipeline_cleanup"


@dataclass
class PipelineTask:
    """Individual pipeline task definition"""
    task_id: str
    task_type: TaskType
    task_name: str
    task_description: str
    
    # Execution configuration
    executor_type: str  # python, bash, kubernetes, docker
    executor_config: Dict[str, Any]
    
    # Dependencies
    upstream_tasks: List[str]
    downstream_tasks: List[str]
    
    # Resource requirements
    cpu_cores: Optional[float] = None
    memory_gb: Optional[float] = None
    gpu_count: Optional[int] = None
    execution_timeout: Optional[timedelta] = None
    
    # Retry configuration
    max_retries: int = 3
    retry_delay: timedelta = timedelta(minutes=5)
    retry_exponential_backoff: bool = True
    
    # Monitoring
    alert_on_failure: bool = True
    alert_on_retry: bool = False
    alert_on_success: bool = False
    
    # Metadata
    tags: List[str] = None
    owner: str = None
    created_at: datetime = None
    updated_at: datetime = None


@dataclass
class PipelineDefinition:
    """Complete pipeline definition"""
    pipeline_id: str
    pipeline_name: str
    pipeline_description: str
    pipeline_version: str
    
    # Tasks and dependencies
    tasks: List[PipelineTask]
    task_dependencies: Dict[str, List[str]]
    
    # Scheduling
    schedule_expression: Optional[str] = None  # Cron expression
    timezone: str = "UTC"
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    
    # Configuration
    global_config: Dict[str, Any] = None
    environment_variables: Dict[str, str] = None
    secrets: List[str] = None
    
    # Resource limits
    max_concurrent_tasks: int = 10
    max_execution_time: timedelta = timedelta(hours=24)
    
    # Monitoring and alerting
    monitoring_enabled: bool = True
    alert_channels: List[str] = None
    sla_config: Dict[str, Any] = None
    
    # Metadata
    owner: str = None
    team: str = None
    tags: List[str] = None
    created_at: datetime = None
    updated_at: datetime = None


@dataclass
class PipelineExecution:
    """Pipeline execution instance"""
    execution_id: str
    pipeline_id: str
    pipeline_version: str
    
    # Execution state
    status: PipelineStatus
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    execution_context: Dict[str, Any] = None
    
    # Task executions
    task_executions: Dict[str, Dict[str, Any]] = None
    
    # Results and metrics
    execution_metrics: Dict[str, Any] = None
    output_artifacts: Dict[str, str] = None
    logs_location: Optional[str] = None
    
    # Error handling
    error_message: Optional[str] = None
    failed_task_id: Optional[str] = None
    retry_count: int = 0
    
    # Scheduling info
    scheduled_at: Optional[datetime] = None
    trigger_type: str = "manual"  # manual, scheduled, event_driven
    triggered_by: Optional[str] = None


class PipelineOrchestrationEngine:
    """Enterprise pipeline orchestration and workflow automation engine"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.redis_client = redis.Redis(
            host=config.get('redis_host', 'localhost'),
            port=config.get('redis_port', 6379),
            db=config.get('redis_db', 0)
        )
        self.s3_client = boto3.client('s3') if config.get('s3_enabled') else None
        self.logger = self._setup_logging()
        
        # Initialize orchestration backends
        self.orchestration_backend = config.get('orchestration_backend', 'airflow')
        self.executor_backend = config.get('executor_backend', 'kubernetes')
        
        # Pipeline registry
        self.pipeline_registry: Dict[str, PipelineDefinition] = {}
        self.active_executions: Dict[str, PipelineExecution] = {}
        
        # Components
        self.scheduler = PipelineScheduler(config)
        self.executor = PipelineExecutor(config)
        self.monitor = PipelineMonitor(config)
        self.artifact_manager = ArtifactManager(config)
        
        # Initialize backends
        self._initialize_orchestration_backends()
    
    def _setup_logging(self) -> logging.Logger:
        """Setup structured logging for pipeline orchestration"""
        logger = logging.getLogger('pipeline_orchestration')
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger
    
    def _initialize_orchestration_backends(self) -> None:
        """Initialize orchestration backends (Airflow, Prefect, etc.)"""
        try:
            if self.orchestration_backend == 'airflow':
                self._initialize_airflow()
            elif self.orchestration_backend == 'prefect':
                self._initialize_prefect()
            elif self.orchestration_backend == 'ray':
                self._initialize_ray_workflows()
            elif self.orchestration_backend == 'metaflow':
                self._initialize_metaflow()
            
            self.logger.info(f"Initialized orchestration backend: {self.orchestration_backend}")
            
        except Exception as e:
            self.logger.error(f"Error initializing orchestration backend: {e}")
    
    def _initialize_airflow(self) -> None:
        """Initialize Apache Airflow backend"""
        # Airflow initialization logic
        pass
    
    def _initialize_prefect(self) -> None:
        """Initialize Prefect backend"""
        # Prefect initialization logic
        pass
    
    def _initialize_ray_workflows(self) -> None:
        """Initialize Ray Workflows backend"""
        if not ray.is_initialized():
            ray.init(address=self.config.get('ray_address', 'auto'))
    
    def _initialize_metaflow(self) -> None:
        """Initialize Metaflow backend"""
        # Metaflow initialization logic
        pass
    
    async def register_pipeline(self, pipeline_definition: PipelineDefinition) -> str:
        """Register a new pipeline definition"""
        try:
            # Validate pipeline definition
            validation_result = await self._validate_pipeline_definition(pipeline_definition)
            if not validation_result['valid']:
                raise ValueError(f"Invalid pipeline definition: {validation_result['errors']}")
            
            # Store pipeline definition
            self.pipeline_registry[pipeline_definition.pipeline_id] = pipeline_definition
            
            # Store in Redis for persistence
            await self._store_pipeline_definition(pipeline_definition)
            
            # Create orchestration backend workflow
            await self._create_backend_workflow(pipeline_definition)
            
            self.logger.info(f"Registered pipeline: {pipeline_definition.pipeline_id}")
            return pipeline_definition.pipeline_id
            
        except Exception as e:
            self.logger.error(f"Error registering pipeline: {e}")
            raise
    
    async def _validate_pipeline_definition(self, pipeline: PipelineDefinition) -> Dict[str, Any]:
        """Validate pipeline definition for correctness"""
        errors = []
        warnings = []
        
        # Check required fields
        if not pipeline.pipeline_id:
            errors.append("Pipeline ID is required")
        
        if not pipeline.tasks:
            errors.append("Pipeline must have at least one task")
        
        # Validate task dependencies
        task_ids = {task.task_id for task in pipeline.tasks}
        for task in pipeline.tasks:
            for upstream_task in task.upstream_tasks:
                if upstream_task not in task_ids:
                    errors.append(f"Task {task.task_id} references unknown upstream task: {upstream_task}")
        
        # Check for circular dependencies
        if self._has_circular_dependencies(pipeline.tasks):
            errors.append("Pipeline has circular dependencies")
        
        # Validate schedule expression
        if pipeline.schedule_expression:
            try:
                croniter.croniter(pipeline.schedule_expression)
            except ValueError as e:
                errors.append(f"Invalid cron expression: {e}")
        
        # Resource validation
        for task in pipeline.tasks:
            if task.cpu_cores and task.cpu_cores <= 0:
                errors.append(f"Task {task.task_id} has invalid CPU requirement")
            
            if task.memory_gb and task.memory_gb <= 0:
                errors.append(f"Task {task.task_id} has invalid memory requirement")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
    
    def _has_circular_dependencies(self, tasks: List[PipelineTask]) -> bool:
        """Check if pipeline has circular dependencies using DFS"""
        # Build adjacency list
        graph = {task.task_id: task.downstream_tasks for task in tasks}
        
        visited = set()
        rec_stack = set()
        
        def dfs(node):
            if node in rec_stack:
                return True  # Circular dependency found
            
            if node in visited:
                return False
            
            visited.add(node)
            rec_stack.add(node)
            
            for neighbor in graph.get(node, []):
                if dfs(neighbor):
                    return True
            
            rec_stack.remove(node)
            return False
        
        for task_id in graph:
            if task_id not in visited:
                if dfs(task_id):
                    return True
        
        return False
    
    async def execute_pipeline(
        self,
        pipeline_id: str,
        execution_config: Optional[Dict[str, Any]] = None,
        trigger_type: str = "manual",
        triggered_by: Optional[str] = None
    ) -> str:
        """Execute a registered pipeline"""
        if pipeline_id not in self.pipeline_registry:
            raise ValueError(f"Pipeline {pipeline_id} not found")
        
        pipeline = self.pipeline_registry[pipeline_id]
        execution_id = str(uuid.uuid4())
        
        # Create execution instance
        execution = PipelineExecution(
            execution_id=execution_id,
            pipeline_id=pipeline_id,
            pipeline_version=pipeline.pipeline_version,
            status=PipelineStatus.PENDING,
            execution_context=execution_config or {},
            task_executions={},
            execution_metrics={},
            output_artifacts={},
            trigger_type=trigger_type,
            triggered_by=triggered_by,
            scheduled_at=datetime.utcnow()
        )
        
        self.active_executions[execution_id] = execution
        
        try:
            # Start pipeline execution
            await self._start_pipeline_execution(execution, pipeline)
            
            self.logger.info(f"Started pipeline execution: {execution_id}")
            return execution_id
            
        except Exception as e:
            execution.status = PipelineStatus.FAILED
            execution.error_message = str(e)
            await self._store_execution_state(execution)
            self.logger.error(f"Error executing pipeline: {e}")
            raise
    
    async def _start_pipeline_execution(
        self,
        execution: PipelineExecution,
        pipeline: PipelineDefinition
    ) -> None:
        """Start pipeline execution with task orchestration"""
        execution.status = PipelineStatus.RUNNING
        execution.started_at = datetime.utcnow()
        
        # Store initial execution state
        await self._store_execution_state(execution)
        
        # Execute pipeline based on backend
        if self.orchestration_backend == 'airflow':
            await self._execute_with_airflow(execution, pipeline)
        elif self.orchestration_backend == 'prefect':
            await self._execute_with_prefect(execution, pipeline)
        elif self.orchestration_backend == 'ray':
            await self._execute_with_ray(execution, pipeline)
        elif self.orchestration_backend == 'native':
            await self._execute_natively(execution, pipeline)
        else:
            raise ValueError(f"Unsupported orchestration backend: {self.orchestration_backend}")
    
    async def _execute_natively(
        self,
        execution: PipelineExecution,
        pipeline: PipelineDefinition
    ) -> None:
        """Execute pipeline using native orchestration"""
        
        # Build execution graph
        execution_graph = self._build_execution_graph(pipeline.tasks)
        
        # Execute tasks in topological order
        completed_tasks = set()
        running_tasks = {}
        
        while len(completed_tasks) < len(pipeline.tasks):
            # Find ready tasks (all dependencies completed)
            ready_tasks = []
            for task in pipeline.tasks:
                if (task.task_id not in completed_tasks and 
                    task.task_id not in running_tasks and
                    all(dep in completed_tasks for dep in task.upstream_tasks)):
                    ready_tasks.append(task)
            
            # Start ready tasks (respecting concurrency limits)
            while (ready_tasks and 
                   len(running_tasks) < pipeline.max_concurrent_tasks):
                task = ready_tasks.pop(0)
                
                # Start task execution
                task_execution = asyncio.create_task(
                    self._execute_task(execution.execution_id, task, execution.execution_context)
                )
                running_tasks[task.task_id] = task_execution
                
                self.logger.info(f"Started task: {task.task_id}")
            
            # Wait for at least one task to complete
            if running_tasks:
                done, pending = await asyncio.wait(
                    running_tasks.values(),
                    return_when=asyncio.FIRST_COMPLETED,
                    timeout=60  # Check every minute
                )
                
                # Process completed tasks
                for task_future in done:
                    # Find completed task
                    completed_task_id = None
                    for task_id, future in running_tasks.items():
                        if future == task_future:
                            completed_task_id = task_id
                            break
                    
                    if completed_task_id:
                        try:
                            task_result = await task_future
                            completed_tasks.add(completed_task_id)
                            del running_tasks[completed_task_id]
                            
                            # Update execution state
                            execution.task_executions[completed_task_id] = task_result
                            
                            self.logger.info(f"Completed task: {completed_task_id}")
                            
                        except Exception as e:
                            # Task failed
                            execution.status = PipelineStatus.FAILED
                            execution.error_message = f"Task {completed_task_id} failed: {e}"
                            execution.failed_task_id = completed_task_id
                            execution.completed_at = datetime.utcnow()
                            
                            # Cancel remaining tasks
                            for remaining_task in running_tasks.values():
                                remaining_task.cancel()
                            
                            await self._store_execution_state(execution)
                            return
            
            # Update execution state periodically
            await self._store_execution_state(execution)
        
        # All tasks completed successfully
        execution.status = PipelineStatus.SUCCESS
        execution.completed_at = datetime.utcnow()
        
        # Calculate execution metrics
        execution.execution_metrics = self._calculate_execution_metrics(execution)
        
        await self._store_execution_state(execution)
        self.logger.info(f"Pipeline execution completed: {execution.execution_id}")
    
    def _build_execution_graph(self, tasks: List[PipelineTask]) -> Dict[str, List[str]]:
        """Build task execution dependency graph"""
        graph = {}
        for task in tasks:
            graph[task.task_id] = task.downstream_tasks
        return graph
    
    async def _execute_task(
        self,
        execution_id: str,
        task: PipelineTask,
        execution_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute individual pipeline task"""
        task_start_time = datetime.utcnow()
        
        try:
            # Execute based on executor type
            if task.executor_type == 'python':
                result = await self._execute_python_task(task, execution_context)
            elif task.executor_type == 'bash':
                result = await self._execute_bash_task(task, execution_context)
            elif task.executor_type == 'kubernetes':
                result = await self._execute_kubernetes_task(task, execution_context)
            elif task.executor_type == 'docker':
                result = await self._execute_docker_task(task, execution_context)
            else:
                raise ValueError(f"Unsupported executor type: {task.executor_type}")
            
            task_end_time = datetime.utcnow()
            execution_duration = task_end_time - task_start_time
            
            return {
                'task_id': task.task_id,
                'status': 'success',
                'started_at': task_start_time.isoformat(),
                'completed_at': task_end_time.isoformat(),
                'execution_duration': execution_duration.total_seconds(),
                'result': result,
                'logs': result.get('logs', ''),
                'artifacts': result.get('artifacts', [])
            }
            
        except Exception as e:
            task_end_time = datetime.utcnow()
            execution_duration = task_end_time - task_start_time
            
            return {
                'task_id': task.task_id,
                'status': 'failed',
                'started_at': task_start_time.isoformat(),
                'completed_at': task_end_time.isoformat(),
                'execution_duration': execution_duration.total_seconds(),
                'error': str(e),
                'logs': '',
                'artifacts': []
            }
    
    async def _execute_python_task(
        self,
        task: PipelineTask,
        execution_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute Python task"""
        executor_config = task.executor_config
        
        # Get Python function/module to execute
        function_name = executor_config.get('function')
        module_name = executor_config.get('module')
        
        if function_name and module_name:
            # Import and execute function
            import importlib
            module = importlib.import_module(module_name)
            function = getattr(module, function_name)
            
            # Execute function with parameters
            parameters = executor_config.get('parameters', {})
            parameters.update(execution_context)
            
            result = await asyncio.get_event_loop().run_in_executor(
                None, function, parameters
            )
            
            return {
                'output': result,
                'logs': f"Executed {module_name}.{function_name}",
                'artifacts': []
            }
        else:
            raise ValueError("Python task requires 'function' and 'module' in executor_config")
    
    async def _execute_bash_task(
        self,
        task: PipelineTask,
        execution_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute Bash task"""
        executor_config = task.executor_config
        command = executor_config.get('command')
        
        if not command:
            raise ValueError("Bash task requires 'command' in executor_config")
        
        # Replace variables in command
        for key, value in execution_context.items():
            command = command.replace(f"${{{key}}}", str(value))
        
        # Execute command
        process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            raise RuntimeError(f"Command failed with exit code {process.returncode}: {stderr.decode()}")
        
        return {
            'output': stdout.decode(),
            'logs': stderr.decode(),
            'artifacts': [],
            'exit_code': process.returncode
        }
    
    async def _execute_kubernetes_task(
        self,
        task: PipelineTask,
        execution_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute Kubernetes task"""
        executor_config = task.executor_config
        
        # Create Kubernetes job spec
        job_spec = self._create_kubernetes_job_spec(task, execution_context)
        
        # Submit job to Kubernetes
        k8s_batch_api = client.BatchV1Api()
        
        try:
            # Create job
            job = k8s_batch_api.create_namespaced_job(
                namespace=executor_config.get('namespace', 'default'),
                body=job_spec
            )
            
            job_name = job.metadata.name
            
            # Wait for job completion
            await self._wait_for_kubernetes_job_completion(job_name, executor_config.get('namespace', 'default'))
            
            # Get job logs
            logs = await self._get_kubernetes_job_logs(job_name, executor_config.get('namespace', 'default'))
            
            # Clean up job
            k8s_batch_api.delete_namespaced_job(
                name=job_name,
                namespace=executor_config.get('namespace', 'default')
            )
            
            return {
                'output': 'Job completed successfully',
                'logs': logs,
                'artifacts': [],
                'job_name': job_name
            }
            
        except Exception as e:
            raise RuntimeError(f"Kubernetes job execution failed: {e}")
    
    def _create_kubernetes_job_spec(
        self,
        task: PipelineTask,
        execution_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create Kubernetes job specification"""
        executor_config = task.executor_config
        
        job_spec = {
            'apiVersion': 'batch/v1',
            'kind': 'Job',
            'metadata': {
                'name': f"{task.task_id}-{uuid.uuid4().hex[:8]}",
                'labels': {
                    'pipeline-id': execution_context.get('pipeline_id', ''),
                    'task-id': task.task_id,
                    'task-type': task.task_type.value
                }
            },
            'spec': {
                'template': {
                    'spec': {
                        'containers': [{
                            'name': 'task-container',
                            'image': executor_config.get('image', 'python:3.9'),
                            'command': executor_config.get('command', ['python']),
                            'args': executor_config.get('args', []),
                            'env': [
                                {'name': k, 'value': str(v)}
                                for k, v in execution_context.items()
                            ],
                            'resources': {
                                'requests': {},
                                'limits': {}
                            }
                        }],
                        'restartPolicy': 'Never'
                    }
                },
                'backoffLimit': task.max_retries
            }
        }
        
        # Add resource requirements
        if task.cpu_cores:
            job_spec['spec']['template']['spec']['containers'][0]['resources']['requests']['cpu'] = str(task.cpu_cores)
            job_spec['spec']['template']['spec']['containers'][0]['resources']['limits']['cpu'] = str(task.cpu_cores)
        
        if task.memory_gb:
            memory_str = f"{task.memory_gb}Gi"
            job_spec['spec']['template']['spec']['containers'][0]['resources']['requests']['memory'] = memory_str
            job_spec['spec']['template']['spec']['containers'][0]['resources']['limits']['memory'] = memory_str
        
        if task.gpu_count:
            job_spec['spec']['template']['spec']['containers'][0]['resources']['limits']['nvidia.com/gpu'] = str(task.gpu_count)
        
        return job_spec
    
    async def _wait_for_kubernetes_job_completion(self, job_name: str, namespace: str) -> None:
        """Wait for Kubernetes job to complete"""
        k8s_batch_api = client.BatchV1Api()
        
        while True:
            try:
                job = k8s_batch_api.read_namespaced_job(name=job_name, namespace=namespace)
                
                if job.status.succeeded:
                    return
                elif job.status.failed:
                    raise RuntimeError(f"Kubernetes job {job_name} failed")
                
                await asyncio.sleep(10)  # Check every 10 seconds
                
            except client.exceptions.ApiException as e:
                if e.status == 404:
                    raise RuntimeError(f"Kubernetes job {job_name} not found")
                else:
                    raise
    
    async def _get_kubernetes_job_logs(self, job_name: str, namespace: str) -> str:
        """Get logs from Kubernetes job"""
        k8s_core_api = client.CoreV1Api()
        
        try:
            # Get pods for the job
            pods = k8s_core_api.list_namespaced_pod(
                namespace=namespace,
                label_selector=f"job-name={job_name}"
            )
            
            if not pods.items:
                return "No pods found for job"
            
            # Get logs from the first pod
            pod_name = pods.items[0].metadata.name
            logs = k8s_core_api.read_namespaced_pod_log(
                name=pod_name,
                namespace=namespace
            )
            
            return logs
            
        except client.exceptions.ApiException:
            return "Could not retrieve job logs"
    
    async def _execute_docker_task(
        self,
        task: PipelineTask,
        execution_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute Docker task"""
        executor_config = task.executor_config
        
        # Build docker run command
        docker_image = executor_config.get('image')
        docker_command = executor_config.get('command', [])
        
        if not docker_image:
            raise ValueError("Docker task requires 'image' in executor_config")
        
        # Build environment variables
        env_vars = []
        for key, value in execution_context.items():
            env_vars.extend(['-e', f"{key}={value}"])
        
        # Build full command
        cmd = ['docker', 'run', '--rm'] + env_vars + [docker_image] + docker_command
        
        # Execute docker command
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            raise RuntimeError(f"Docker command failed with exit code {process.returncode}: {stderr.decode()}")
        
        return {
            'output': stdout.decode(),
            'logs': stderr.decode(),
            'artifacts': [],
            'exit_code': process.returncode
        }
    
    async def cancel_pipeline_execution(self, execution_id: str) -> bool:
        """Cancel running pipeline execution"""
        if execution_id not in self.active_executions:
            return False
        
        execution = self.active_executions[execution_id]
        
        if execution.status not in [PipelineStatus.RUNNING, PipelineStatus.PENDING]:
            return False
        
        try:
            # Cancel based on orchestration backend
            if self.orchestration_backend == 'native':
                # Cancel running tasks (implementation depends on task executors)
                pass
            
            execution.status = PipelineStatus.CANCELLED
            execution.completed_at = datetime.utcnow()
            
            await self._store_execution_state(execution)
            
            self.logger.info(f"Cancelled pipeline execution: {execution_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error cancelling pipeline execution: {e}")
            return False
    
    async def get_pipeline_status(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """Get current status of pipeline execution"""
        execution = self.active_executions.get(execution_id)
        
        if not execution:
            # Try to load from storage
            execution = await self._load_execution_state(execution_id)
        
        if not execution:
            return None
        
        return {
            'execution_id': execution.execution_id,
            'pipeline_id': execution.pipeline_id,
            'status': execution.status.value,
            'started_at': execution.started_at.isoformat() if execution.started_at else None,
            'completed_at': execution.completed_at.isoformat() if execution.completed_at else None,
            'task_executions': execution.task_executions,
            'execution_metrics': execution.execution_metrics,
            'error_message': execution.error_message,
            'failed_task_id': execution.failed_task_id,
            'retry_count': execution.retry_count
        }
    
    async def list_pipeline_executions(
        self,
        pipeline_id: Optional[str] = None,
        status_filter: Optional[PipelineStatus] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """List pipeline executions with optional filtering"""
        executions = []
        
        # Filter active executions
        for execution in self.active_executions.values():
            if pipeline_id and execution.pipeline_id != pipeline_id:
                continue
            if status_filter and execution.status != status_filter:
                continue
            
            execution_info = await self.get_pipeline_status(execution.execution_id)
            if execution_info:
                executions.append(execution_info)
        
        # Sort by start time (most recent first)
        executions.sort(key=lambda x: x.get('started_at', ''), reverse=True)
        
        return executions[:limit]
    
    def _calculate_execution_metrics(self, execution: PipelineExecution) -> Dict[str, Any]:
        """Calculate execution metrics and statistics"""
        if not execution.task_executions:
            return {}
        
        task_durations = []
        successful_tasks = 0
        failed_tasks = 0
        
        for task_exec in execution.task_executions.values():
            if task_exec.get('execution_duration'):
                task_durations.append(task_exec['execution_duration'])
            
            if task_exec.get('status') == 'success':
                successful_tasks += 1
            else:
                failed_tasks += 1
        
        total_duration = 0
        if execution.started_at and execution.completed_at:
            total_duration = (execution.completed_at - execution.started_at).total_seconds()
        
        return {
            'total_execution_time': total_duration,
            'task_count': len(execution.task_executions),
            'successful_tasks': successful_tasks,
            'failed_tasks': failed_tasks,
            'success_rate': successful_tasks / len(execution.task_executions) if execution.task_executions else 0,
            'average_task_duration': sum(task_durations) / len(task_durations) if task_durations else 0,
            'total_task_time': sum(task_durations),
            'parallelization_efficiency': sum(task_durations) / total_duration if total_duration > 0 else 0
        }
    
    async def _store_pipeline_definition(self, pipeline: PipelineDefinition) -> None:
        """Store pipeline definition in Redis"""
        pipeline_data = asdict(pipeline)
        self.redis_client.setex(
            f"pipeline_def:{pipeline.pipeline_id}",
            timedelta(days=365),
            json.dumps(pipeline_data, default=str)
        )
    
    async def _store_execution_state(self, execution: PipelineExecution) -> None:
        """Store execution state in Redis"""
        execution_data = asdict(execution)
        self.redis_client.setex(
            f"pipeline_exec:{execution.execution_id}",
            timedelta(days=90),
            json.dumps(execution_data, default=str)
        )
    
    async def _load_execution_state(self, execution_id: str) -> Optional[PipelineExecution]:
        """Load execution state from Redis"""
        try:
            data = self.redis_client.get(f"pipeline_exec:{execution_id}")
            if data:
                execution_dict = json.loads(data)
                # Convert back to PipelineExecution object
                return PipelineExecution(**execution_dict)
            return None
        except Exception:
            return None
    
    async def _create_backend_workflow(self, pipeline: PipelineDefinition) -> None:
        """Create workflow in orchestration backend"""
        if self.orchestration_backend == 'airflow':
            await self._create_airflow_dag(pipeline)
        elif self.orchestration_backend == 'prefect':
            await self._create_prefect_flow(pipeline)
        elif self.orchestration_backend == 'ray':
            await self._create_ray_workflow(pipeline)
    
    async def _create_airflow_dag(self, pipeline: PipelineDefinition) -> None:
        """Create Airflow DAG from pipeline definition"""
        # Implementation for Airflow DAG creation
        pass
    
    async def _create_prefect_flow(self, pipeline: PipelineDefinition) -> None:
        """Create Prefect Flow from pipeline definition"""
        # Implementation for Prefect Flow creation
        pass
    
    async def _create_ray_workflow(self, pipeline: PipelineDefinition) -> None:
        """Create Ray Workflow from pipeline definition"""
        # Implementation for Ray Workflow creation
        pass


class PipelineScheduler:
    """Schedule and trigger pipeline executions"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger('pipeline_scheduler')
        self.scheduled_pipelines: Dict[str, Dict[str, Any]] = {}
    
    async def schedule_pipeline(
        self,
        pipeline_id: str,
        schedule_expression: str,
        timezone: str = "UTC"
    ) -> None:
        """Schedule pipeline execution"""
        # Validate cron expression
        try:
            cron = croniter.croniter(schedule_expression)
        except ValueError as e:
            raise ValueError(f"Invalid cron expression: {e}")
        
        self.scheduled_pipelines[pipeline_id] = {
            'schedule_expression': schedule_expression,
            'timezone': timezone,
            'next_run': cron.get_next(datetime),
            'enabled': True
        }
        
        self.logger.info(f"Scheduled pipeline {pipeline_id} with expression: {schedule_expression}")
    
    async def check_scheduled_executions(self) -> List[str]:
        """Check for pipelines that need to be executed"""
        ready_pipelines = []
        current_time = datetime.utcnow()
        
        for pipeline_id, schedule_info in self.scheduled_pipelines.items():
            if schedule_info['enabled'] and current_time >= schedule_info['next_run']:
                ready_pipelines.append(pipeline_id)
                
                # Calculate next run time
                cron = croniter.croniter(schedule_info['schedule_expression'])
                schedule_info['next_run'] = cron.get_next(datetime)
        
        return ready_pipelines


class PipelineExecutor:
    """Execute pipeline tasks with different execution backends"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger('pipeline_executor')


class PipelineMonitor:
    """Monitor pipeline executions and generate alerts"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger('pipeline_monitor')
    
    async def monitor_execution(self, execution_id: str) -> None:
        """Monitor pipeline execution and generate alerts"""
        # Implementation for execution monitoring
        pass


class ArtifactManager:
    """Manage pipeline artifacts and outputs"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.s3_client = boto3.client('s3') if config.get('s3_enabled') else None
        self.logger = logging.getLogger('artifact_manager')
    
    async def store_artifact(
        self,
        execution_id: str,
        task_id: str,
        artifact_name: str,
        artifact_data: bytes
    ) -> str:
        """Store pipeline artifact"""
        if self.s3_client:
            artifact_key = f"pipeline_artifacts/{execution_id}/{task_id}/{artifact_name}"
            self.s3_client.put_object(
                Bucket=self.config['artifact_bucket'],
                Key=artifact_key,
                Body=artifact_data
            )
            return f"s3://{self.config['artifact_bucket']}/{artifact_key}"
        else:
            # Store locally
            artifact_path = Path(f"/tmp/pipeline_artifacts/{execution_id}/{task_id}")
            artifact_path.mkdir(parents=True, exist_ok=True)
            
            with open(artifact_path / artifact_name, 'wb') as f:
                f.write(artifact_data)
            
            return str(artifact_path / artifact_name)


# Factory function for creating pipeline orchestration engine
def create_pipeline_orchestration_engine(config: Dict[str, Any]) -> PipelineOrchestrationEngine:
    """Create pipeline orchestration engine instance"""
    return PipelineOrchestrationEngine(config)


# Helper functions for creating common pipeline tasks
def create_data_ingestion_task(
    task_id: str,
    data_source: Dict[str, Any],
    output_location: str
) -> PipelineTask:
    """Create data ingestion task"""
    return PipelineTask(
        task_id=task_id,
        task_type=TaskType.DATA_INGESTION,
        task_name=f"Data Ingestion - {task_id}",
        task_description=f"Ingest data from {data_source.get('type', 'unknown')} source",
        executor_type="python",
        executor_config={
            "module": "ainflue.ml.data_ingestion",
            "function": "ingest_data",
            "parameters": {
                "data_source": data_source,
                "output_location": output_location
            }
        },
        upstream_tasks=[],
        downstream_tasks=[]
    )


def create_model_training_task(
    task_id: str,
    model_config: Dict[str, Any],
    training_data_path: str,
    upstream_task_ids: List[str]
) -> PipelineTask:
    """Create model training task"""
    return PipelineTask(
        task_id=task_id,
        task_type=TaskType.MODEL_TRAINING,
        task_name=f"Model Training - {task_id}",
        task_description=f"Train {model_config.get('model_type', 'unknown')} model",
        executor_type="python",
        executor_config={
            "module": "ainflue.ml.training",
            "function": "train_model",
            "parameters": {
                "model_config": model_config,
                "training_data_path": training_data_path
            }
        },
        upstream_tasks=upstream_task_ids,
        downstream_tasks=[],
        cpu_cores=4.0,
        memory_gb=16.0,
        gpu_count=1,
        execution_timeout=timedelta(hours=12)
    )


def create_model_deployment_task(
    task_id: str,
    model_path: str,
    deployment_config: Dict[str, Any],
    upstream_task_ids: List[str]
) -> PipelineTask:
    """Create model deployment task"""
    return PipelineTask(
        task_id=task_id,
        task_type=TaskType.MODEL_DEPLOYMENT,
        task_name=f"Model Deployment - {task_id}",
        task_description="Deploy trained model to production",
        executor_type="kubernetes",
        executor_config={
            "image": "ainflue/model-deployment:latest",
            "command": ["python", "-m", "ainflue.ml.deployment"],
            "args": ["--model-path", model_path, "--config", json.dumps(deployment_config)],
            "namespace": "ml-production"
        },
        upstream_tasks=upstream_task_ids,
        downstream_tasks=[],
        cpu_cores=2.0,
        memory_gb=8.0
    )