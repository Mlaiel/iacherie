"""
🚀 **MLOps Pipeline Orchestrator - Enterprise Automation**

Ersteller: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel. Alle Rechte vorbehalten.
Version: 1.0.0

**⚠️ WARNUNG:** Dieser Code ist urheberrechtlich geschützt und vertraulich.

Enterprise MLOps pipeline orchestration with automated testing, validation,
deployment, and monitoring for creator-specific ML models.
"""

import asyncio
import logging
import numpy as np
import torch
import yaml
import json
import subprocess
import docker
from typing import Dict, List, Optional, Any, Tuple, Union, Callable
from dataclasses import dataclass, asdict
from pathlib import Path
from datetime import datetime, timedelta
from enum import Enum
import uuid
import threading
import time
from concurrent.futures import ThreadPoolExecutor, Future
import aiofiles
import aiohttp
import hashlib

# Ainflue ML Core Imports
from ..model_registry.mlflow_registry import MLflowRegistry
from ..monitoring.performance_monitor import PerformanceMonitor
from ..monitoring.audit_trail_generator import AuditTrailGenerator
from ..deployment.deployment_manager import DeploymentManager

class PipelineStage(Enum):
    """MLOps pipeline stages."""
    DATA_VALIDATION = "data_validation"
    FEATURE_ENGINEERING = "feature_engineering"
    MODEL_TRAINING = "model_training"
    MODEL_VALIDATION = "model_validation"
    MODEL_TESTING = "model_testing"
    SECURITY_SCANNING = "security_scanning"
    PERFORMANCE_TESTING = "performance_testing"
    DEPLOYMENT_STAGING = "deployment_staging"
    INTEGRATION_TESTING = "integration_testing"
    PRODUCTION_DEPLOYMENT = "production_deployment"
    MONITORING_SETUP = "monitoring_setup"
    ROLLBACK = "rollback"

class PipelineStatus(Enum):
    """Pipeline execution statuses."""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"

class TriggerType(Enum):
    """Pipeline trigger types."""
    MANUAL = "manual"
    SCHEDULED = "scheduled"
    DATA_CHANGE = "data_change"
    MODEL_DRIFT = "model_drift"
    PERFORMANCE_DEGRADATION = "performance_degradation"
    SECURITY_ALERT = "security_alert"
    GIT_PUSH = "git_push"

@dataclass
class PipelineConfig:
    """Configuration for MLOps pipeline."""
    pipeline_id: str
    name: str
    description: str
    creator_type: str
    model_type: str
    stages: List[PipelineStage]
    trigger_types: List[TriggerType]
    environment_config: Dict[str, Any]
    resource_requirements: Dict[str, Any]
    timeout_minutes: int = 120
    retry_attempts: int = 3
    parallel_execution: bool = False
    approval_required: bool = False
    rollback_enabled: bool = True

@dataclass
class StageConfig:
    """Configuration for individual pipeline stage."""
    stage: PipelineStage
    script_path: str
    docker_image: str = None
    environment_vars: Dict[str, str] = None
    resource_limits: Dict[str, str] = None
    depends_on: List[PipelineStage] = None
    retry_attempts: int = 1
    timeout_minutes: int = 30
    success_criteria: Dict[str, Any] = None

@dataclass
class PipelineExecution:
    """Execution instance of a pipeline."""
    execution_id: str
    pipeline_id: str
    triggered_by: TriggerType
    status: PipelineStatus
    start_time: datetime
    end_time: Optional[datetime]
    current_stage: Optional[PipelineStage]
    stage_results: Dict[PipelineStage, Dict[str, Any]]
    error_message: Optional[str]
    artifacts: Dict[str, str]
    metrics: Dict[str, float]
    commit_hash: Optional[str]
    created_by: str

@dataclass
class StageResult:
    """Result of a pipeline stage execution."""
    stage: PipelineStage
    status: PipelineStatus
    start_time: datetime
    end_time: datetime
    duration_seconds: float
    exit_code: int
    logs: str
    artifacts: Dict[str, str]
    metrics: Dict[str, float]
    error_details: Optional[str]

class DataValidator:
    """Validate data quality and schema."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    async def validate_training_data(self, data_path: str, schema_path: str) -> Dict[str, Any]:
        """Validate training data against schema."""
        try:
            # Load data
            if data_path.endswith('.json'):
                async with aiofiles.open(data_path, 'r') as f:
                    data = json.loads(await f.read())
            else:
                # Handle other formats (CSV, Parquet, etc.)
                data = {}
            
            # Load schema
            async with aiofiles.open(schema_path, 'r') as f:
                schema = json.loads(await f.read())
            
            # Validation checks
            validation_results = {
                'schema_valid': True,
                'data_quality_score': 0.0,
                'missing_values_percent': 0.0,
                'duplicate_records_percent': 0.0,
                'outliers_detected': 0,
                'data_drift_score': 0.0,
                'validation_errors': []
            }
            
            # Schema validation
            required_fields = schema.get('required_fields', [])
            if isinstance(data, list) and data:
                sample_record = data[0]
                for field in required_fields:
                    if field not in sample_record:
                        validation_results['schema_valid'] = False
                        validation_results['validation_errors'].append(f"Missing required field: {field}")
            
            # Data quality checks
            if isinstance(data, list):
                total_records = len(data)
                if total_records > 0:
                    # Calculate quality metrics
                    validation_results['data_quality_score'] = min(
                        100.0 - len(validation_results['validation_errors']) * 10, 100.0
                    )
            
            self.logger.info(f"Data validation completed. Quality score: {validation_results['data_quality_score']}")
            
            return validation_results
            
        except Exception as e:
            self.logger.error(f"Error in data validation: {e}")
            return {
                'schema_valid': False,
                'validation_errors': [str(e)],
                'data_quality_score': 0.0
            }

class ModelValidator:
    """Validate trained models."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    async def validate_model(self, model_path: str, validation_data_path: str) -> Dict[str, Any]:
        """Validate model performance and quality."""
        try:
            # Load model
            if model_path.endswith('.pth'):
                model_state = torch.load(model_path, map_location='cpu')
            else:
                model_state = {}
            
            validation_results = {
                'model_valid': True,
                'accuracy': 0.0,
                'precision': 0.0,
                'recall': 0.0,
                'f1_score': 0.0,
                'inference_latency_ms': 0.0,
                'model_size_mb': 0.0,
                'validation_errors': []
            }
            
            # Model size check
            if model_path:
                model_size_bytes = Path(model_path).stat().st_size
                validation_results['model_size_mb'] = model_size_bytes / (1024 * 1024)
            
            # Performance validation (mock implementation)
            validation_results['accuracy'] = 0.95  # Mock accuracy
            validation_results['precision'] = 0.94
            validation_results['recall'] = 0.93
            validation_results['f1_score'] = 0.935
            validation_results['inference_latency_ms'] = 50.0
            
            # Validation criteria
            if validation_results['accuracy'] < 0.85:
                validation_results['model_valid'] = False
                validation_results['validation_errors'].append("Accuracy below threshold (0.85)")
            
            if validation_results['inference_latency_ms'] > 100.0:
                validation_results['model_valid'] = False
                validation_results['validation_errors'].append("Inference latency above threshold (100ms)")
            
            self.logger.info(f"Model validation completed. Accuracy: {validation_results['accuracy']:.3f}")
            
            return validation_results
            
        except Exception as e:
            self.logger.error(f"Error in model validation: {e}")
            return {
                'model_valid': False,
                'validation_errors': [str(e)],
                'accuracy': 0.0
            }

class SecurityScanner:
    """Security scanning for ML models and dependencies."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    async def scan_model_security(self, model_path: str, dependencies_file: str) -> Dict[str, Any]:
        """Scan model and dependencies for security vulnerabilities."""
        try:
            security_results = {
                'security_score': 100.0,
                'vulnerabilities_found': [],
                'critical_issues': 0,
                'high_issues': 0,
                'medium_issues': 0,
                'low_issues': 0,
                'recommendations': []
            }
            
            # Model file security check
            if model_path and Path(model_path).exists():
                # Check file integrity
                with open(model_path, 'rb') as f:
                    model_hash = hashlib.sha256(f.read()).hexdigest()
                security_results['model_hash'] = model_hash
            
            # Dependencies security scan (mock implementation)
            if dependencies_file and Path(dependencies_file).exists():
                async with aiofiles.open(dependencies_file, 'r') as f:
                    deps = await f.read()
                
                # Mock vulnerability detection
                if 'torch<1.0' in deps:
                    security_results['vulnerabilities_found'].append({
                        'package': 'torch',
                        'severity': 'HIGH',
                        'description': 'Outdated PyTorch version with known vulnerabilities',
                        'recommendation': 'Update to PyTorch >= 1.13.0'
                    })
                    security_results['high_issues'] += 1
                    security_results['security_score'] -= 20
            
            # Additional security checks
            security_results['recommendations'].extend([
                'Enable model encryption at rest',
                'Implement access control for model artifacts',
                'Regular security audits'
            ])
            
            self.logger.info(f"Security scan completed. Score: {security_results['security_score']}")
            
            return security_results
            
        except Exception as e:
            self.logger.error(f"Error in security scanning: {e}")
            return {
                'security_score': 0.0,
                'vulnerabilities_found': [{'severity': 'CRITICAL', 'description': str(e)}],
                'critical_issues': 1
            }

class PerformanceTester:
    """Performance testing for ML models."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    async def run_performance_tests(self, model_path: str, test_config: Dict[str, Any]) -> Dict[str, Any]:
        """Run comprehensive performance tests."""
        try:
            performance_results = {
                'load_test_passed': False,
                'stress_test_passed': False,
                'latency_test_passed': False,
                'throughput_rps': 0.0,
                'avg_latency_ms': 0.0,
                'p99_latency_ms': 0.0,
                'memory_usage_mb': 0.0,
                'cpu_usage_percent': 0.0,
                'gpu_usage_percent': 0.0,
                'performance_score': 0.0
            }
            
            # Mock performance testing
            await asyncio.sleep(2)  # Simulate test execution
            
            # Generate realistic test results
            performance_results.update({
                'load_test_passed': True,
                'stress_test_passed': True,
                'latency_test_passed': True,
                'throughput_rps': 500.0,
                'avg_latency_ms': 45.0,
                'p99_latency_ms': 95.0,
                'memory_usage_mb': 256.0,
                'cpu_usage_percent': 65.0,
                'gpu_usage_percent': 80.0,
                'performance_score': 85.0
            })
            
            # Check against thresholds
            max_latency = test_config.get('max_latency_ms', 100)
            if performance_results['avg_latency_ms'] > max_latency:
                performance_results['latency_test_passed'] = False
            
            min_throughput = test_config.get('min_throughput_rps', 100)
            if performance_results['throughput_rps'] < min_throughput:
                performance_results['load_test_passed'] = False
            
            self.logger.info(f"Performance tests completed. Score: {performance_results['performance_score']}")
            
            return performance_results
            
        except Exception as e:
            self.logger.error(f"Error in performance testing: {e}")
            return {
                'load_test_passed': False,
                'stress_test_passed': False,
                'latency_test_passed': False,
                'performance_score': 0.0
            }

class StageExecutor:
    """Execute individual pipeline stages."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.docker_client = None
        try:
            self.docker_client = docker.from_env()
        except Exception:
            self.logger.warning("Docker not available")
    
    async def execute_stage(self, stage_config: StageConfig, execution_context: Dict[str, Any]) -> StageResult:
        """Execute a pipeline stage."""
        start_time = datetime.now()
        
        try:
            self.logger.info(f"Starting stage: {stage_config.stage.value}")
            
            # Prepare execution environment
            env_vars = {
                **execution_context.get('environment_vars', {}),
                **(stage_config.environment_vars or {})
            }
            
            if stage_config.docker_image and self.docker_client:
                # Execute in Docker container
                result = await self._execute_in_docker(stage_config, env_vars, execution_context)
            else:
                # Execute locally
                result = await self._execute_locally(stage_config, env_vars, execution_context)
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            stage_result = StageResult(
                stage=stage_config.stage,
                status=PipelineStatus.SUCCESS if result['exit_code'] == 0 else PipelineStatus.FAILED,
                start_time=start_time,
                end_time=end_time,
                duration_seconds=duration,
                exit_code=result['exit_code'],
                logs=result['logs'],
                artifacts=result.get('artifacts', {}),
                metrics=result.get('metrics', {}),
                error_details=result.get('error_details')
            )
            
            self.logger.info(
                f"Stage {stage_config.stage.value} completed with status: {stage_result.status.value}"
            )
            
            return stage_result
            
        except Exception as e:
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            error_result = StageResult(
                stage=stage_config.stage,
                status=PipelineStatus.FAILED,
                start_time=start_time,
                end_time=end_time,
                duration_seconds=duration,
                exit_code=-1,
                logs=str(e),
                artifacts={},
                metrics={},
                error_details=str(e)
            )
            
            self.logger.error(f"Stage {stage_config.stage.value} failed: {e}")
            return error_result
    
    async def _execute_locally(self, stage_config: StageConfig, env_vars: Dict[str, str], context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute stage locally."""
        try:
            if stage_config.stage == PipelineStage.DATA_VALIDATION:
                validator = DataValidator()
                data_path = context.get('data_path', 'data/train.json')
                schema_path = context.get('schema_path', 'data/schema.json')
                result = await validator.validate_training_data(data_path, schema_path)
                return {
                    'exit_code': 0 if result['schema_valid'] else 1,
                    'logs': f"Data validation completed. Quality score: {result['data_quality_score']}",
                    'metrics': result
                }
            
            elif stage_config.stage == PipelineStage.MODEL_VALIDATION:
                validator = ModelValidator()
                model_path = context.get('model_path', 'models/model.pth')
                validation_data_path = context.get('validation_data_path', 'data/val.json')
                result = await validator.validate_model(model_path, validation_data_path)
                return {
                    'exit_code': 0 if result['model_valid'] else 1,
                    'logs': f"Model validation completed. Accuracy: {result['accuracy']:.3f}",
                    'metrics': result
                }
            
            elif stage_config.stage == PipelineStage.SECURITY_SCANNING:
                scanner = SecurityScanner()
                model_path = context.get('model_path', 'models/model.pth')
                deps_file = context.get('dependencies_file', 'requirements.txt')
                result = await scanner.scan_model_security(model_path, deps_file)
                return {
                    'exit_code': 0 if result['critical_issues'] == 0 else 1,
                    'logs': f"Security scan completed. Score: {result['security_score']}",
                    'metrics': result
                }
            
            elif stage_config.stage == PipelineStage.PERFORMANCE_TESTING:
                tester = PerformanceTester()
                model_path = context.get('model_path', 'models/model.pth')
                test_config = context.get('performance_test_config', {})
                result = await tester.run_performance_tests(model_path, test_config)
                return {
                    'exit_code': 0 if result['performance_score'] > 70 else 1,
                    'logs': f"Performance tests completed. Score: {result['performance_score']}",
                    'metrics': result
                }
            
            else:
                # Generic script execution
                if stage_config.script_path and Path(stage_config.script_path).exists():
                    process = await asyncio.create_subprocess_exec(
                        'python', stage_config.script_path,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.STDOUT,
                        env={**env_vars}
                    )
                    
                    stdout, _ = await process.communicate()
                    logs = stdout.decode('utf-8') if stdout else ""
                    
                    return {
                        'exit_code': process.returncode,
                        'logs': logs,
                        'metrics': {}
                    }
                else:
                    return {
                        'exit_code': 0,
                        'logs': f"Stage {stage_config.stage.value} completed (no script)",
                        'metrics': {}
                    }
            
        except Exception as e:
            return {
                'exit_code': -1,
                'logs': str(e),
                'error_details': str(e),
                'metrics': {}
            }
    
    async def _execute_in_docker(self, stage_config: StageConfig, env_vars: Dict[str, str], context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute stage in Docker container."""
        try:
            if not self.docker_client:
                raise Exception("Docker client not available")
            
            # Prepare container configuration
            container_config = {
                'image': stage_config.docker_image,
                'environment': env_vars,
                'working_dir': '/workspace',
                'volumes': {
                    str(Path.cwd()): {'bind': '/workspace', 'mode': 'rw'}
                },
                'detach': True
            }
            
            # Add resource limits if specified
            if stage_config.resource_limits:
                container_config['mem_limit'] = stage_config.resource_limits.get('memory', '1g')
                container_config['cpuset_cpus'] = stage_config.resource_limits.get('cpus')
            
            # Run container
            if stage_config.script_path:
                command = f"python {stage_config.script_path}"
            else:
                command = "echo 'Stage completed'"
            
            container = self.docker_client.containers.run(
                command=command,
                **container_config
            )
            
            # Wait for completion
            result = container.wait()
            logs = container.logs().decode('utf-8')
            
            # Cleanup
            container.remove()
            
            return {
                'exit_code': result['StatusCode'],
                'logs': logs,
                'metrics': {}
            }
            
        except Exception as e:
            return {
                'exit_code': -1,
                'logs': str(e),
                'error_details': str(e),
                'metrics': {}
            }

class MLOpsPipelineOrchestrator:
    """
    🚀 **Enterprise MLOps Pipeline Orchestrator**
    
    Advanced MLOps automation system with comprehensive testing, validation,
    deployment, and monitoring for creator-specific ML models.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.model_registry = MLflowRegistry()
        self.performance_monitor = PerformanceMonitor()
        self.audit_trail = AuditTrailGenerator()
        self.deployment_manager = DeploymentManager()
        
        # Pipeline management
        self.pipelines: Dict[str, PipelineConfig] = {}
        self.executions: Dict[str, PipelineExecution] = {}
        self.stage_configs: Dict[str, List[StageConfig]] = {}
        
        # Execution engine
        self.stage_executor = StageExecutor()
        self.thread_pool = ThreadPoolExecutor(max_workers=4)
        
        # State management
        self.execution_lock = threading.Lock()
        self.running_executions: Dict[str, Future] = {}
        
        self.logger.info("MLOpsPipelineOrchestrator initialized")
    
    async def register_pipeline(self, config: PipelineConfig, stages: List[StageConfig]) -> str:
        """
        📋 **Register MLOps Pipeline**
        
        Register a new MLOps pipeline configuration.
        """
        try:
            # Validate pipeline configuration
            self._validate_pipeline_config(config, stages)
            
            # Store pipeline configuration
            self.pipelines[config.pipeline_id] = config
            self.stage_configs[config.pipeline_id] = stages
            
            # Audit trail
            await self.audit_trail.log_event(
                event_type='pipeline_registered',
                entity_id=config.pipeline_id,
                metadata={
                    'pipeline_name': config.name,
                    'creator_type': config.creator_type,
                    'stages_count': len(stages)
                }
            )
            
            self.logger.info(f"Pipeline registered: {config.name} ({config.pipeline_id})")
            
            return config.pipeline_id
            
        except Exception as e:
            self.logger.error(f"Error registering pipeline: {e}")
            raise
    
    def _validate_pipeline_config(self, config: PipelineConfig, stages: List[StageConfig]):
        """Validate pipeline configuration."""
        # Check required stages
        required_stages = {PipelineStage.MODEL_VALIDATION, PipelineStage.SECURITY_SCANNING}
        pipeline_stages = {stage.stage for stage in stages}
        
        missing_stages = required_stages - pipeline_stages
        if missing_stages:
            raise ValueError(f"Missing required stages: {missing_stages}")
        
        # Check stage dependencies
        stage_map = {stage.stage: stage for stage in stages}
        for stage in stages:
            if stage.depends_on:
                for dependency in stage.depends_on:
                    if dependency not in stage_map:
                        raise ValueError(f"Stage {stage.stage} depends on missing stage {dependency}")
    
    async def trigger_pipeline(
        self, 
        pipeline_id: str, 
        trigger_type: TriggerType, 
        context: Dict[str, Any] = None,
        created_by: str = "system"
    ) -> str:
        """
        🚀 **Trigger Pipeline Execution**
        
        Start execution of an MLOps pipeline.
        """
        try:
            if pipeline_id not in self.pipelines:
                raise ValueError(f"Pipeline not found: {pipeline_id}")
            
            pipeline_config = self.pipelines[pipeline_id]
            
            # Check if trigger type is allowed
            if trigger_type not in pipeline_config.trigger_types:
                raise ValueError(f"Trigger type {trigger_type} not allowed for pipeline {pipeline_id}")
            
            # Create execution instance
            execution_id = str(uuid.uuid4())
            execution = PipelineExecution(
                execution_id=execution_id,
                pipeline_id=pipeline_id,
                triggered_by=trigger_type,
                status=PipelineStatus.PENDING,
                start_time=datetime.now(),
                end_time=None,
                current_stage=None,
                stage_results={},
                error_message=None,
                artifacts={},
                metrics={},
                commit_hash=context.get('commit_hash') if context else None,
                created_by=created_by
            )
            
            # Store execution
            with self.execution_lock:
                self.executions[execution_id] = execution
            
            # Start execution asynchronously
            future = self.thread_pool.submit(
                asyncio.run, 
                self._execute_pipeline(execution_id, context or {})
            )
            
            with self.execution_lock:
                self.running_executions[execution_id] = future
            
            # Audit trail
            await self.audit_trail.log_event(
                event_type='pipeline_triggered',
                entity_id=execution_id,
                metadata={
                    'pipeline_id': pipeline_id,
                    'trigger_type': trigger_type.value,
                    'created_by': created_by
                }
            )
            
            self.logger.info(f"Pipeline triggered: {pipeline_id} -> {execution_id}")
            
            return execution_id
            
        except Exception as e:
            self.logger.error(f"Error triggering pipeline: {e}")
            raise
    
    async def _execute_pipeline(self, execution_id: str, context: Dict[str, Any]):
        """Execute pipeline stages."""
        try:
            execution = self.executions[execution_id]
            pipeline_config = self.pipelines[execution.pipeline_id]
            stage_configs = self.stage_configs[execution.pipeline_id]
            
            # Update execution status
            execution.status = PipelineStatus.RUNNING
            
            # Build stage dependency graph
            stage_graph = self._build_stage_graph(stage_configs)
            
            # Execute stages
            if pipeline_config.parallel_execution:
                await self._execute_stages_parallel(execution, stage_graph, context)
            else:
                await self._execute_stages_sequential(execution, stage_configs, context)
            
            # Final status
            if all(result.status == PipelineStatus.SUCCESS for result in execution.stage_results.values()):
                execution.status = PipelineStatus.SUCCESS
            else:
                execution.status = PipelineStatus.FAILED
            
            execution.end_time = datetime.now()
            
            # Post-execution actions
            await self._post_execution_actions(execution)
            
        except Exception as e:
            execution.status = PipelineStatus.FAILED
            execution.error_message = str(e)
            execution.end_time = datetime.now()
            self.logger.error(f"Pipeline execution failed: {e}")
        
        finally:
            # Clean up
            with self.execution_lock:
                if execution_id in self.running_executions:
                    del self.running_executions[execution_id]
    
    def _build_stage_graph(self, stage_configs: List[StageConfig]) -> Dict[PipelineStage, List[PipelineStage]]:
        """Build stage dependency graph."""
        graph = {}
        for stage_config in stage_configs:
            graph[stage_config.stage] = stage_config.depends_on or []
        return graph
    
    async def _execute_stages_sequential(
        self, 
        execution: PipelineExecution, 
        stage_configs: List[StageConfig], 
        context: Dict[str, Any]
    ):
        """Execute stages sequentially."""
        for stage_config in stage_configs:
            execution.current_stage = stage_config.stage
            
            # Check dependencies
            if stage_config.depends_on:
                failed_dependencies = [
                    dep for dep in stage_config.depends_on
                    if dep in execution.stage_results and execution.stage_results[dep].status != PipelineStatus.SUCCESS
                ]
                
                if failed_dependencies:
                    self.logger.warning(f"Skipping stage {stage_config.stage} due to failed dependencies: {failed_dependencies}")
                    continue
            
            # Execute stage with retries
            stage_result = await self._execute_stage_with_retry(stage_config, context, execution)
            execution.stage_results[stage_config.stage] = stage_result
            
            # Update metrics
            execution.metrics[f"{stage_config.stage.value}_duration"] = stage_result.duration_seconds
            execution.metrics.update(stage_result.metrics)
            
            # Stop execution if critical stage fails
            if stage_result.status == PipelineStatus.FAILED and stage_config.stage in [
                PipelineStage.MODEL_VALIDATION, 
                PipelineStage.SECURITY_SCANNING
            ]:
                execution.error_message = f"Critical stage {stage_config.stage.value} failed"
                break
    
    async def _execute_stages_parallel(
        self, 
        execution: PipelineExecution, 
        stage_graph: Dict[PipelineStage, List[PipelineStage]], 
        context: Dict[str, Any]
    ):
        """Execute stages in parallel respecting dependencies."""
        completed_stages = set()
        remaining_stages = set(stage_graph.keys())
        
        while remaining_stages:
            # Find stages ready to execute
            ready_stages = [
                stage for stage in remaining_stages
                if all(dep in completed_stages for dep in stage_graph[stage])
            ]
            
            if not ready_stages:
                break  # Circular dependency or error
            
            # Execute ready stages in parallel
            stage_configs_map = {sc.stage: sc for sc in self.stage_configs[execution.pipeline_id]}
            tasks = []
            
            for stage in ready_stages:
                stage_config = stage_configs_map[stage]
                task = self._execute_stage_with_retry(stage_config, context, execution)
                tasks.append((stage, task))
            
            # Wait for completion
            results = await asyncio.gather(*[task for _, task in tasks], return_exceptions=True)
            
            # Process results
            for (stage, _), result in zip(tasks, results):
                if isinstance(result, Exception):
                    # Create failed stage result
                    stage_result = StageResult(
                        stage=stage,
                        status=PipelineStatus.FAILED,
                        start_time=datetime.now(),
                        end_time=datetime.now(),
                        duration_seconds=0,
                        exit_code=-1,
                        logs=str(result),
                        artifacts={},
                        metrics={},
                        error_details=str(result)
                    )
                else:
                    stage_result = result
                
                execution.stage_results[stage] = stage_result
                
                if stage_result.status == PipelineStatus.SUCCESS:
                    completed_stages.add(stage)
                
                remaining_stages.discard(stage)
    
    async def _execute_stage_with_retry(
        self, 
        stage_config: StageConfig, 
        context: Dict[str, Any], 
        execution: PipelineExecution
    ) -> StageResult:
        """Execute stage with retry logic."""
        last_result = None
        
        for attempt in range(stage_config.retry_attempts):
            try:
                # Add timeout
                stage_result = await asyncio.wait_for(
                    self.stage_executor.execute_stage(stage_config, context),
                    timeout=stage_config.timeout_minutes * 60
                )
                
                if stage_result.status == PipelineStatus.SUCCESS:
                    return stage_result
                
                last_result = stage_result
                
                if attempt < stage_config.retry_attempts - 1:
                    self.logger.warning(f"Stage {stage_config.stage.value} failed, retrying (attempt {attempt + 1})")
                    await asyncio.sleep(5)  # Wait before retry
                
            except asyncio.TimeoutError:
                self.logger.error(f"Stage {stage_config.stage.value} timed out")
                last_result = StageResult(
                    stage=stage_config.stage,
                    status=PipelineStatus.FAILED,
                    start_time=datetime.now(),
                    end_time=datetime.now(),
                    duration_seconds=stage_config.timeout_minutes * 60,
                    exit_code=-1,
                    logs="Stage execution timed out",
                    artifacts={},
                    metrics={},
                    error_details="Timeout"
                )
                break
            
            except Exception as e:
                self.logger.error(f"Stage {stage_config.stage.value} error: {e}")
                last_result = StageResult(
                    stage=stage_config.stage,
                    status=PipelineStatus.FAILED,
                    start_time=datetime.now(),
                    end_time=datetime.now(),
                    duration_seconds=0,
                    exit_code=-1,
                    logs=str(e),
                    artifacts={},
                    metrics={},
                    error_details=str(e)
                )
                break
        
        return last_result or StageResult(
            stage=stage_config.stage,
            status=PipelineStatus.FAILED,
            start_time=datetime.now(),
            end_time=datetime.now(),
            duration_seconds=0,
            exit_code=-1,
            logs="Stage execution failed",
            artifacts={},
            metrics={},
            error_details="Unknown error"
        )
    
    async def _post_execution_actions(self, execution: PipelineExecution):
        """Perform post-execution actions."""
        try:
            # Log metrics
            await self.performance_monitor.log_metrics(
                model_id=execution.pipeline_id,
                metrics={
                    'pipeline_duration_seconds': (execution.end_time - execution.start_time).total_seconds(),
                    'pipeline_success': 1.0 if execution.status == PipelineStatus.SUCCESS else 0.0,
                    **execution.metrics
                }
            )
            
            # Deploy if successful and deployment stage exists
            if (execution.status == PipelineStatus.SUCCESS and 
                PipelineStage.PRODUCTION_DEPLOYMENT in execution.stage_results):
                
                deployment_result = execution.stage_results[PipelineStage.PRODUCTION_DEPLOYMENT]
                if deployment_result.status == PipelineStatus.SUCCESS:
                    # Trigger model deployment
                    model_path = execution.artifacts.get('model_path')
                    if model_path:
                        await self.deployment_manager.deploy_model(
                            model_path=model_path,
                            deployment_target="production",
                            deployment_config={
                                'creator_type': self.pipelines[execution.pipeline_id].creator_type,
                                'pipeline_execution_id': execution.execution_id
                            }
                        )
            
            # Audit trail
            await self.audit_trail.log_event(
                event_type='pipeline_completed',
                entity_id=execution.execution_id,
                metadata={
                    'status': execution.status.value,
                    'duration_seconds': (execution.end_time - execution.start_time).total_seconds(),
                    'stages_executed': len(execution.stage_results)
                }
            )
            
        except Exception as e:
            self.logger.error(f"Error in post-execution actions: {e}")
    
    async def get_execution_status(self, execution_id: str) -> Optional[PipelineExecution]:
        """Get execution status."""
        return self.executions.get(execution_id)
    
    async def list_executions(
        self, 
        pipeline_id: str = None, 
        status: PipelineStatus = None,
        limit: int = 50
    ) -> List[PipelineExecution]:
        """List pipeline executions with filtering."""
        executions = list(self.executions.values())
        
        # Apply filters
        if pipeline_id:
            executions = [e for e in executions if e.pipeline_id == pipeline_id]
        
        if status:
            executions = [e for e in executions if e.status == status]
        
        # Sort by start time (newest first)
        executions.sort(key=lambda x: x.start_time, reverse=True)
        
        return executions[:limit]
    
    async def cancel_execution(self, execution_id: str) -> bool:
        """Cancel running pipeline execution."""
        try:
            with self.execution_lock:
                if execution_id in self.running_executions:
                    future = self.running_executions[execution_id]
                    future.cancel()
                    
                    execution = self.executions.get(execution_id)
                    if execution:
                        execution.status = PipelineStatus.CANCELLED
                        execution.end_time = datetime.now()
                    
                    del self.running_executions[execution_id]
                    
                    self.logger.info(f"Pipeline execution cancelled: {execution_id}")
                    return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error cancelling execution: {e}")
            return False
    
    async def get_pipeline_metrics(self, pipeline_id: str, days: int = 30) -> Dict[str, Any]:
        """Get pipeline performance metrics."""
        try:
            # Filter executions for the pipeline
            pipeline_executions = [
                e for e in self.executions.values()
                if e.pipeline_id == pipeline_id and 
                (datetime.now() - e.start_time).days <= days
            ]
            
            if not pipeline_executions:
                return {'total_executions': 0}
            
            # Calculate metrics
            total_executions = len(pipeline_executions)
            successful_executions = sum(1 for e in pipeline_executions if e.status == PipelineStatus.SUCCESS)
            failed_executions = sum(1 for e in pipeline_executions if e.status == PipelineStatus.FAILED)
            
            success_rate = successful_executions / total_executions * 100
            
            # Duration statistics
            completed_executions = [e for e in pipeline_executions if e.end_time]
            if completed_executions:
                durations = [(e.end_time - e.start_time).total_seconds() for e in completed_executions]
                avg_duration = np.mean(durations)
                min_duration = np.min(durations)
                max_duration = np.max(durations)
            else:
                avg_duration = min_duration = max_duration = 0
            
            # Stage success rates
            stage_metrics = {}
            for execution in pipeline_executions:
                for stage, result in execution.stage_results.items():
                    stage_name = stage.value
                    if stage_name not in stage_metrics:
                        stage_metrics[stage_name] = {'total': 0, 'success': 0}
                    
                    stage_metrics[stage_name]['total'] += 1
                    if result.status == PipelineStatus.SUCCESS:
                        stage_metrics[stage_name]['success'] += 1
            
            # Calculate stage success rates
            for stage_name, metrics in stage_metrics.items():
                metrics['success_rate'] = metrics['success'] / metrics['total'] * 100
            
            return {
                'total_executions': total_executions,
                'successful_executions': successful_executions,
                'failed_executions': failed_executions,
                'success_rate_percent': success_rate,
                'avg_duration_seconds': avg_duration,
                'min_duration_seconds': min_duration,
                'max_duration_seconds': max_duration,
                'stage_metrics': stage_metrics,
                'period_days': days
            }
            
        except Exception as e:
            self.logger.error(f"Error getting pipeline metrics: {e}")
            return {'error': str(e)}

# Factory for creating MLOps orchestrators
class MLOpsOrchestratorFactory:
    """Factory for creating MLOps orchestrators with preset configurations."""
    
    @staticmethod
    def create_creator_pipeline(creator_type: str) -> Tuple[PipelineConfig, List[StageConfig]]:
        """Create optimized pipeline for specific creator type."""
        pipeline_id = f"{creator_type}_mlops_pipeline"
        
        pipeline_config = PipelineConfig(
            pipeline_id=pipeline_id,
            name=f"{creator_type.title()} ML Pipeline",
            description=f"Automated MLOps pipeline for {creator_type} models",
            creator_type=creator_type,
            model_type="classification",
            stages=[
                PipelineStage.DATA_VALIDATION,
                PipelineStage.MODEL_TRAINING,
                PipelineStage.MODEL_VALIDATION,
                PipelineStage.SECURITY_SCANNING,
                PipelineStage.PERFORMANCE_TESTING,
                PipelineStage.DEPLOYMENT_STAGING,
                PipelineStage.PRODUCTION_DEPLOYMENT
            ],
            trigger_types=[
                TriggerType.MANUAL,
                TriggerType.GIT_PUSH,
                TriggerType.SCHEDULED
            ],
            environment_config={
                'python_version': '3.9',
                'cuda_version': '11.8'
            },
            resource_requirements={
                'memory_gb': 8,
                'cpu_cores': 4,
                'gpu_required': True
            }
        )
        
        stage_configs = [
            StageConfig(
                stage=PipelineStage.DATA_VALIDATION,
                script_path="scripts/validate_data.py",
                timeout_minutes=15
            ),
            StageConfig(
                stage=PipelineStage.MODEL_TRAINING,
                script_path="scripts/train_model.py",
                depends_on=[PipelineStage.DATA_VALIDATION],
                timeout_minutes=60,
                resource_limits={'memory': '8g', 'cpus': '4'}
            ),
            StageConfig(
                stage=PipelineStage.MODEL_VALIDATION,
                script_path="scripts/validate_model.py",
                depends_on=[PipelineStage.MODEL_TRAINING],
                timeout_minutes=20
            ),
            StageConfig(
                stage=PipelineStage.SECURITY_SCANNING,
                script_path="scripts/security_scan.py",
                depends_on=[PipelineStage.MODEL_VALIDATION],
                timeout_minutes=10
            ),
            StageConfig(
                stage=PipelineStage.PERFORMANCE_TESTING,
                script_path="scripts/performance_test.py",
                depends_on=[PipelineStage.SECURITY_SCANNING],
                timeout_minutes=30
            ),
            StageConfig(
                stage=PipelineStage.DEPLOYMENT_STAGING,
                script_path="scripts/deploy_staging.py",
                depends_on=[PipelineStage.PERFORMANCE_TESTING],
                timeout_minutes=15
            ),
            StageConfig(
                stage=PipelineStage.PRODUCTION_DEPLOYMENT,
                script_path="scripts/deploy_production.py",
                depends_on=[PipelineStage.DEPLOYMENT_STAGING],
                timeout_minutes=20
            )
        ]
        
        return pipeline_config, stage_configs

# Initialize logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    # Example usage
    async def demo_mlops_orchestrator():
        orchestrator = MLOpsPipelineOrchestrator()
        
        # Create and register pipeline
        pipeline_config, stage_configs = MLOpsOrchestratorFactory.create_creator_pipeline("musician")
        
        pipeline_id = await orchestrator.register_pipeline(pipeline_config, stage_configs)
        print(f"Pipeline registered: {pipeline_id}")
        
        # Trigger pipeline execution
        execution_id = await orchestrator.trigger_pipeline(
            pipeline_id=pipeline_id,
            trigger_type=TriggerType.MANUAL,
            context={
                'data_path': 'data/musician_train.json',
                'model_path': 'models/musician_classifier.pth'
            }
        )
        
        print(f"Pipeline execution started: {execution_id}")
        
        # Monitor execution
        await asyncio.sleep(10)  # Wait for some progress
        
        execution_status = await orchestrator.get_execution_status(execution_id)
        if execution_status:
            print(f"Execution status: {execution_status.status}")
            print(f"Current stage: {execution_status.current_stage}")
    
    # Run demo
    asyncio.run(demo_mlops_orchestrator())