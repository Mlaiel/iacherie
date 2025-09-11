#!/usr/bin/env python3
"""
⚙️ MLOps Pipeline Orchestrator - DevOps Implementation
DevOps Expert - Complete ML Pipeline Automation & Infrastructure Management

Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
Contact: mlaiel@live.de

Enterprise MLOps pipeline orchestration with CI/CD automation, infrastructure
provisioning, model deployment, and comprehensive monitoring integration.
"""

import asyncio
import logging
import json
import yaml
import subprocess
import time
import os
import tempfile
from typing import Dict, List, Tuple, Optional, Any, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from pathlib import Path
import threading
from concurrent.futures import ThreadPoolExecutor
import hashlib
import shutil
import git
import docker
import kubernetes
from kubernetes import client, config as k8s_config
import boto3
import paramiko
from jinja2 import Template

logger = logging.getLogger(__name__)

class PipelineStage(Enum):
    """MLOps pipeline stages"""
    DATA_VALIDATION = "data_validation"
    FEATURE_ENGINEERING = "feature_engineering"
    MODEL_TRAINING = "model_training"
    MODEL_VALIDATION = "model_validation"
    MODEL_TESTING = "model_testing"
    MODEL_PACKAGING = "model_packaging"
    DEPLOYMENT_STAGING = "deployment_staging"
    INTEGRATION_TESTING = "integration_testing"
    DEPLOYMENT_PRODUCTION = "deployment_production"
    MONITORING_SETUP = "monitoring_setup"
    ROLLBACK = "rollback"

class PipelineStatus(Enum):
    """Pipeline execution status"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"
    SKIPPED = "skipped"

class DeploymentTarget(Enum):
    """Deployment target environments"""
    LOCAL = "local"
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    EDGE = "edge"

class InfrastructureProvider(Enum):
    """Infrastructure providers"""
    KUBERNETES = "kubernetes"
    AWS = "aws"
    AZURE = "azure"
    GCP = "gcp"
    DOCKER = "docker"
    LOCAL = "local"

@dataclass
class PipelineStep:
    """Individual pipeline step definition"""
    step_id: str
    name: str
    stage: PipelineStage
    command: str
    dependencies: List[str] = field(default_factory=list)
    environment: Dict[str, str] = field(default_factory=dict)
    artifacts: List[str] = field(default_factory=list)
    timeout_minutes: int = 30
    retry_count: int = 2
    required: bool = True
    parallel: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'step_id': self.step_id,
            'name': self.name,
            'stage': self.stage.value,
            'command': self.command,
            'dependencies': self.dependencies,
            'environment': self.environment,
            'artifacts': self.artifacts,
            'timeout_minutes': self.timeout_minutes,
            'retry_count': self.retry_count,
            'required': self.required,
            'parallel': self.parallel
        }

@dataclass
class PipelineExecution:
    """Pipeline execution tracking"""
    execution_id: str
    pipeline_name: str
    trigger: str = "manual"
    started_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    status: PipelineStatus = PipelineStatus.PENDING
    current_stage: Optional[PipelineStage] = None
    step_results: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    artifacts: Dict[str, str] = field(default_factory=dict)
    logs: List[str] = field(default_factory=list)
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def duration_seconds(self) -> float:
        """Get execution duration in seconds"""
        end_time = self.completed_at or datetime.utcnow()
        return (end_time - self.started_at).total_seconds()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'execution_id': self.execution_id,
            'pipeline_name': self.pipeline_name,
            'trigger': self.trigger,
            'started_at': self.started_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'status': self.status.value,
            'current_stage': self.current_stage.value if self.current_stage else None,
            'step_results': self.step_results,
            'artifacts': self.artifacts,
            'logs': self.logs,
            'error_message': self.error_message,
            'metadata': self.metadata,
            'duration_seconds': self.duration_seconds
        }

@dataclass
class MLOpsConfig:
    """MLOps pipeline configuration"""
    project_name: str = "ml-project"
    workspace_path: str = "/tmp/mlops-workspace"
    git_repository: Optional[str] = None
    infrastructure_provider: InfrastructureProvider = InfrastructureProvider.LOCAL
    deployment_targets: List[DeploymentTarget] = field(default_factory=lambda: [DeploymentTarget.STAGING])
    enable_docker: bool = True
    enable_kubernetes: bool = False
    enable_monitoring: bool = True
    enable_alerting: bool = True
    artifact_storage_path: str = "/tmp/mlops-artifacts"
    max_parallel_steps: int = 3
    default_timeout_minutes: int = 60
    enable_rollback: bool = True
    notification_webhook: Optional[str] = None

class DockerManager:
    """Docker container management for MLOps"""
    
    def __init__(self):
        try:
            self.client = docker.from_env()
            logger.info("✅ Docker client connected")
        except Exception as e:
            logger.warning(f"⚠️ Docker not available: {str(e)}")
            self.client = None
    
    async def build_model_image(
        self,
        model_path: str,
        image_name: str,
        tag: str = "latest",
        creator_type: str = "general"
    ) -> str:
        """Build Docker image for ML model"""
        if not self.client:
            raise Exception("Docker client not available")
        
        # Create Dockerfile template based on creator type
        dockerfile_template = self._get_dockerfile_template(creator_type)
        
        # Prepare build context
        build_context = Path(model_path)
        dockerfile_path = build_context / "Dockerfile"
        
        with open(dockerfile_path, 'w') as f:
            f.write(dockerfile_template)
        
        logger.info(f"🐳 Building Docker image: {image_name}:{tag}")
        
        try:
            # Build image
            image, logs = self.client.images.build(
                path=str(build_context),
                tag=f"{image_name}:{tag}",
                rm=True,
                forcerm=True
            )
            
            # Collect build logs
            build_logs = []
            for log in logs:
                if 'stream' in log:
                    build_logs.append(log['stream'].strip())
            
            logger.info(f"✅ Docker image built successfully: {image.id}")
            return image.id
            
        except Exception as e:
            logger.error(f"❌ Docker build failed: {str(e)}")
            raise
    
    def _get_dockerfile_template(self, creator_type: str) -> str:
        """Get Dockerfile template for creator type"""
        base_template = """
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    build-essential \\
    curl \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy model and application code
COPY . .

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:8000/health || exit 1

# Expose port
EXPOSE 8000

# Start application
CMD ["python", "serve.py"]
"""
        
        if creator_type == "musician":
            return base_template.replace(
                "pip install --no-cache-dir -r requirements.txt",
                "pip install --no-cache-dir -r requirements.txt && apt-get update && apt-get install -y libsndfile1 ffmpeg"
            )
        elif creator_type == "photographer":
            return base_template.replace(
                "pip install --no-cache-dir -r requirements.txt",
                "pip install --no-cache-dir -r requirements.txt && apt-get update && apt-get install -y libgl1-mesa-glx libglib2.0-0"
            )
        else:
            return base_template
    
    async def push_image(self, image_name: str, tag: str, registry: str = "docker.io") -> bool:
        """Push image to registry"""
        if not self.client:
            return False
        
        try:
            full_image_name = f"{registry}/{image_name}:{tag}"
            
            # Tag image for registry
            image = self.client.images.get(f"{image_name}:{tag}")
            image.tag(full_image_name)
            
            # Push to registry
            push_logs = self.client.images.push(full_image_name)
            
            logger.info(f"📤 Image pushed to registry: {full_image_name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Image push failed: {str(e)}")
            return False

class KubernetesManager:
    """Kubernetes deployment management"""
    
    def __init__(self):
        try:
            k8s_config.load_incluster_config()
            logger.info("✅ Kubernetes in-cluster config loaded")
        except:
            try:
                k8s_config.load_kube_config()
                logger.info("✅ Kubernetes config loaded from ~/.kube/config")
            except Exception as e:
                logger.warning(f"⚠️ Kubernetes not available: {str(e)}")
                self.client = None
                return
        
        self.apps_v1 = client.AppsV1Api()
        self.core_v1 = client.CoreV1Api()
        self.networking_v1 = client.NetworkingV1Api()
    
    async def deploy_model(
        self,
        model_name: str,
        image_name: str,
        namespace: str = "default",
        replicas: int = 2,
        creator_type: str = "general"
    ) -> str:
        """Deploy ML model to Kubernetes"""
        if not hasattr(self, 'apps_v1'):
            raise Exception("Kubernetes client not available")
        
        deployment_name = f"{model_name}-deployment"
        
        # Create deployment manifest
        deployment = self._create_deployment_manifest(
            deployment_name, image_name, replicas, creator_type
        )
        
        # Create service manifest
        service = self._create_service_manifest(model_name, namespace)
        
        try:
            # Deploy to Kubernetes
            self.apps_v1.create_namespaced_deployment(
                body=deployment,
                namespace=namespace
            )
            
            self.core_v1.create_namespaced_service(
                body=service,
                namespace=namespace
            )
            
            logger.info(f"🚀 Model deployed to Kubernetes: {deployment_name}")
            return deployment_name
            
        except Exception as e:
            logger.error(f"❌ Kubernetes deployment failed: {str(e)}")
            raise
    
    def _create_deployment_manifest(
        self,
        name: str,
        image: str,
        replicas: int,
        creator_type: str
    ) -> Dict[str, Any]:
        """Create Kubernetes deployment manifest"""
        return {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": name,
                "labels": {
                    "app": name,
                    "creator-type": creator_type,
                    "managed-by": "mlops-orchestrator"
                }
            },
            "spec": {
                "replicas": replicas,
                "selector": {
                    "matchLabels": {
                        "app": name
                    }
                },
                "template": {
                    "metadata": {
                        "labels": {
                            "app": name,
                            "creator-type": creator_type
                        }
                    },
                    "spec": {
                        "containers": [
                            {
                                "name": "model-server",
                                "image": image,
                                "ports": [
                                    {
                                        "containerPort": 8000
                                    }
                                ],
                                "resources": {
                                    "requests": {
                                        "memory": "512Mi",
                                        "cpu": "250m"
                                    },
                                    "limits": {
                                        "memory": "2Gi",
                                        "cpu": "1000m"
                                    }
                                },
                                "livenessProbe": {
                                    "httpGet": {
                                        "path": "/health",
                                        "port": 8000
                                    },
                                    "initialDelaySeconds": 30,
                                    "periodSeconds": 10
                                },
                                "readinessProbe": {
                                    "httpGet": {
                                        "path": "/ready",
                                        "port": 8000
                                    },
                                    "initialDelaySeconds": 5,
                                    "periodSeconds": 5
                                }
                            }
                        ]
                    }
                }
            }
        }
    
    def _create_service_manifest(self, name: str, namespace: str) -> Dict[str, Any]:
        """Create Kubernetes service manifest"""
        return {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {
                "name": f"{name}-service",
                "namespace": namespace
            },
            "spec": {
                "selector": {
                    "app": f"{name}-deployment"
                },
                "ports": [
                    {
                        "protocol": "TCP",
                        "port": 80,
                        "targetPort": 8000
                    }
                ],
                "type": "ClusterIP"
            }
        }

class MLOpsPipelineOrchestrator:
    """
    ⚙️ Enterprise MLOps Pipeline Orchestrator
    
    Complete CI/CD automation for ML workflows with infrastructure provisioning,
    model deployment, monitoring, and rollback capabilities.
    """
    
    def __init__(self, config: MLOpsConfig):
        self.config = config
        self.pipelines: Dict[str, List[PipelineStep]] = {}
        self.executions: Dict[str, PipelineExecution] = {}
        self.docker_manager = DockerManager()
        self.k8s_manager = KubernetesManager()
        self.executor = ThreadPoolExecutor(max_workers=config.max_parallel_steps)
        
        # Initialize workspace
        self.workspace = Path(config.workspace_path)
        self.workspace.mkdir(parents=True, exist_ok=True)
        
        # Initialize artifact storage
        self.artifact_storage = Path(config.artifact_storage_path)
        self.artifact_storage.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"⚙️ MLOps Pipeline Orchestrator initialized: {config.project_name}")
    
    async def create_pipeline(
        self,
        pipeline_name: str,
        steps: List[PipelineStep],
        creator_type: str = "general"
    ) -> str:
        """
        Create MLOps pipeline definition
        
        Args:
            pipeline_name: Name of the pipeline
            steps: List of pipeline steps
            creator_type: Type of creator (musician, blogger, etc.)
            
        Returns:
            Pipeline ID
        """
        # Validate pipeline steps
        await self._validate_pipeline_steps(steps)
        
        # Store pipeline definition
        self.pipelines[pipeline_name] = steps
        
        # Create pipeline configuration file
        pipeline_config = {
            'name': pipeline_name,
            'creator_type': creator_type,
            'steps': [step.to_dict() for step in steps],
            'created_at': datetime.utcnow().isoformat()
        }
        
        config_file = self.workspace / f"{pipeline_name}.yaml"
        with open(config_file, 'w') as f:
            yaml.dump(pipeline_config, f, default_flow_style=False)
        
        logger.info(f"📋 Pipeline created: {pipeline_name} with {len(steps)} steps")
        return pipeline_name
    
    async def execute_pipeline(
        self,
        pipeline_name: str,
        trigger: str = "manual",
        parameters: Dict[str, Any] = None
    ) -> str:
        """
        Execute MLOps pipeline
        
        Args:
            pipeline_name: Name of pipeline to execute
            trigger: What triggered the execution
            parameters: Pipeline parameters
            
        Returns:
            Execution ID
        """
        if pipeline_name not in self.pipelines:
            raise ValueError(f"Pipeline '{pipeline_name}' not found")
        
        execution_id = f"{pipeline_name}-{int(time.time())}"
        
        # Create execution tracking
        execution = PipelineExecution(
            execution_id=execution_id,
            pipeline_name=pipeline_name,
            trigger=trigger,
            metadata=parameters or {}
        )
        
        self.executions[execution_id] = execution
        
        logger.info(f"🚀 Starting pipeline execution: {execution_id}")
        
        # Execute pipeline asynchronously
        asyncio.create_task(self._execute_pipeline_steps(execution))
        
        return execution_id
    
    async def _execute_pipeline_steps(self, execution: PipelineExecution):
        """Execute all pipeline steps"""
        try:
            execution.status = PipelineStatus.RUNNING
            steps = self.pipelines[execution.pipeline_name]
            
            # Group steps by stage for proper sequencing
            stages = self._group_steps_by_stage(steps)
            
            for stage, stage_steps in stages.items():
                execution.current_stage = stage
                logger.info(f"📊 Executing stage: {stage.value}")
                
                # Execute steps in parallel if possible
                parallel_steps = [step for step in stage_steps if step.parallel]
                sequential_steps = [step for step in stage_steps if not step.parallel]
                
                # Execute parallel steps
                if parallel_steps:
                    await self._execute_parallel_steps(execution, parallel_steps)
                
                # Execute sequential steps
                for step in sequential_steps:
                    await self._execute_single_step(execution, step)
                    
                    # Check if execution was cancelled or failed
                    if execution.status in [PipelineStatus.CANCELLED, PipelineStatus.FAILED]:
                        break
                
                if execution.status in [PipelineStatus.CANCELLED, PipelineStatus.FAILED]:
                    break
            
            # Complete execution
            if execution.status == PipelineStatus.RUNNING:
                execution.status = PipelineStatus.SUCCESS
                execution.completed_at = datetime.utcnow()
                logger.info(f"✅ Pipeline completed successfully: {execution.execution_id}")
            
        except Exception as e:
            execution.status = PipelineStatus.FAILED
            execution.error_message = str(e)
            execution.completed_at = datetime.utcnow()
            logger.error(f"❌ Pipeline failed: {execution.execution_id} - {str(e)}")
    
    def _group_steps_by_stage(self, steps: List[PipelineStep]) -> Dict[PipelineStage, List[PipelineStep]]:
        """Group pipeline steps by stage"""
        stages = {}
        for step in steps:
            if step.stage not in stages:
                stages[step.stage] = []
            stages[step.stage].append(step)
        
        # Sort stages by order
        stage_order = list(PipelineStage)
        sorted_stages = {}
        for stage in stage_order:
            if stage in stages:
                sorted_stages[stage] = stages[stage]
        
        return sorted_stages
    
    async def _execute_parallel_steps(
        self,
        execution: PipelineExecution,
        steps: List[PipelineStep]
    ):
        """Execute multiple steps in parallel"""
        tasks = []
        for step in steps:
            task = asyncio.create_task(self._execute_single_step(execution, step))
            tasks.append(task)
        
        # Wait for all parallel steps to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Check for failures
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                step = steps[i]
                execution.step_results[step.step_id] = {
                    'status': PipelineStatus.FAILED.value,
                    'error': str(result)
                }
                if step.required:
                    execution.status = PipelineStatus.FAILED
                    execution.error_message = f"Required parallel step failed: {step.step_id}"
                    break
    
    async def _execute_single_step(
        self,
        execution: PipelineExecution,
        step: PipelineStep
    ):
        """Execute a single pipeline step"""
        logger.info(f"⚡ Executing step: {step.name} ({step.step_id})")
        
        step_start_time = datetime.utcnow()
        step_result = {
            'step_id': step.step_id,
            'started_at': step_start_time.isoformat(),
            'status': PipelineStatus.RUNNING.value,
            'logs': [],
            'artifacts': []
        }
        
        execution.step_results[step.step_id] = step_result
        
        try:
            # Check dependencies
            if not await self._check_step_dependencies(execution, step):
                step_result['status'] = PipelineStatus.SKIPPED.value
                step_result['error'] = "Dependencies not met"
                logger.warning(f"⚠️ Step skipped due to dependencies: {step.step_id}")
                return
            
            # Prepare execution environment
            env = os.environ.copy()
            env.update(step.environment)
            env['MLOPS_EXECUTION_ID'] = execution.execution_id
            env['MLOPS_STEP_ID'] = step.step_id
            env['MLOPS_WORKSPACE'] = str(self.workspace)
            env['MLOPS_ARTIFACTS'] = str(self.artifact_storage)
            
            # Execute step with timeout
            timeout_seconds = step.timeout_minutes * 60
            
            for attempt in range(step.retry_count + 1):
                try:
                    # Execute command
                    result = await asyncio.wait_for(
                        self._run_command(step.command, env, execution),
                        timeout=timeout_seconds
                    )
                    
                    # Handle successful execution
                    step_result['status'] = PipelineStatus.SUCCESS.value
                    step_result['completed_at'] = datetime.utcnow().isoformat()
                    step_result['return_code'] = result['return_code']
                    step_result['stdout'] = result['stdout']
                    step_result['stderr'] = result['stderr']
                    
                    # Collect artifacts
                    artifacts = await self._collect_step_artifacts(step, execution)
                    step_result['artifacts'] = artifacts
                    execution.artifacts.update(artifacts)
                    
                    logger.info(f"✅ Step completed: {step.step_id}")
                    break
                    
                except asyncio.TimeoutError:
                    if attempt < step.retry_count:
                        logger.warning(f"⏰ Step timeout, retrying: {step.step_id} (attempt {attempt + 1})")
                        continue
                    else:
                        raise Exception(f"Step timed out after {timeout_seconds} seconds")
                
                except Exception as e:
                    if attempt < step.retry_count:
                        logger.warning(f"⚠️ Step failed, retrying: {step.step_id} (attempt {attempt + 1})")
                        continue
                    else:
                        raise e
        
        except Exception as e:
            step_result['status'] = PipelineStatus.FAILED.value
            step_result['error'] = str(e)
            step_result['completed_at'] = datetime.utcnow().isoformat()
            
            logger.error(f"❌ Step failed: {step.step_id} - {str(e)}")
            
            if step.required:
                execution.status = PipelineStatus.FAILED
                execution.error_message = f"Required step failed: {step.step_id}"
    
    async def _check_step_dependencies(
        self,
        execution: PipelineExecution,
        step: PipelineStep
    ) -> bool:
        """Check if step dependencies are satisfied"""
        for dep_step_id in step.dependencies:
            if dep_step_id not in execution.step_results:
                return False
            
            dep_result = execution.step_results[dep_step_id]
            if dep_result['status'] != PipelineStatus.SUCCESS.value:
                return False
        
        return True
    
    async def _run_command(
        self,
        command: str,
        env: Dict[str, str],
        execution: PipelineExecution
    ) -> Dict[str, Any]:
        """Run shell command with logging"""
        logger.debug(f"🔧 Running command: {command}")
        
        process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=env,
            cwd=str(self.workspace)
        )
        
        stdout, stderr = await process.communicate()
        
        result = {
            'return_code': process.returncode,
            'stdout': stdout.decode('utf-8') if stdout else '',
            'stderr': stderr.decode('utf-8') if stderr else ''
        }
        
        # Log command output
        if result['stdout']:
            execution.logs.append(f"STDOUT: {result['stdout']}")
        if result['stderr']:
            execution.logs.append(f"STDERR: {result['stderr']}")
        
        if process.returncode != 0:
            raise Exception(f"Command failed with return code {process.returncode}: {result['stderr']}")
        
        return result
    
    async def _collect_step_artifacts(
        self,
        step: PipelineStep,
        execution: PipelineExecution
    ) -> Dict[str, str]:
        """Collect artifacts generated by step"""
        artifacts = {}
        
        for artifact_pattern in step.artifacts:
            # Find files matching pattern
            artifact_files = list(self.workspace.glob(artifact_pattern))
            
            for artifact_file in artifact_files:
                if artifact_file.is_file():
                    # Copy to artifact storage
                    artifact_name = f"{execution.execution_id}/{step.step_id}/{artifact_file.name}"
                    artifact_path = self.artifact_storage / artifact_name
                    artifact_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    shutil.copy2(artifact_file, artifact_path)
                    artifacts[artifact_file.name] = str(artifact_path)
        
        return artifacts
    
    async def _validate_pipeline_steps(self, steps: List[PipelineStep]):
        """Validate pipeline step configuration"""
        step_ids = set()
        
        for step in steps:
            # Check for duplicate step IDs
            if step.step_id in step_ids:
                raise ValueError(f"Duplicate step ID: {step.step_id}")
            step_ids.add(step.step_id)
            
            # Check dependencies
            for dep in step.dependencies:
                if dep not in [s.step_id for s in steps]:
                    raise ValueError(f"Step {step.step_id} depends on non-existent step: {dep}")
        
        logger.info(f"✅ Pipeline validation passed for {len(steps)} steps")
    
    async def deploy_model_pipeline(
        self,
        model_path: str,
        model_name: str,
        target_environment: DeploymentTarget,
        creator_type: str = "general"
    ) -> str:
        """
        Create and execute deployment pipeline for ML model
        
        Args:
            model_path: Path to model files
            model_name: Name of the model
            target_environment: Deployment target
            creator_type: Type of creator
            
        Returns:
            Execution ID
        """
        pipeline_name = f"deploy-{model_name}-{target_environment.value}"
        
        # Create deployment pipeline steps
        steps = [
            PipelineStep(
                step_id="model_validation",
                name="Validate Model",
                stage=PipelineStage.MODEL_VALIDATION,
                command=f"python validate_model.py --model-path {model_path}",
                artifacts=["validation_report.json"],
                timeout_minutes=10
            ),
            PipelineStep(
                step_id="model_testing",
                name="Test Model",
                stage=PipelineStage.MODEL_TESTING,
                command=f"python test_model.py --model-path {model_path}",
                dependencies=["model_validation"],
                artifacts=["test_results.json"],
                timeout_minutes=15
            ),
            PipelineStep(
                step_id="docker_build",
                name="Build Docker Image",
                stage=PipelineStage.MODEL_PACKAGING,
                command=f"docker build -t {model_name}:latest {model_path}",
                dependencies=["model_testing"],
                artifacts=["docker_image_id.txt"],
                timeout_minutes=20
            )
        ]
        
        # Add deployment step based on target environment
        if target_environment == DeploymentTarget.PRODUCTION:
            if self.config.infrastructure_provider == InfrastructureProvider.KUBERNETES:
                steps.append(PipelineStep(
                    step_id="k8s_deploy",
                    name="Deploy to Kubernetes",
                    stage=PipelineStage.DEPLOYMENT_PRODUCTION,
                    command=f"kubectl apply -f k8s-deployment.yaml",
                    dependencies=["docker_build"],
                    artifacts=["deployment.yaml"],
                    timeout_minutes=10
                ))
        
        # Add monitoring setup
        if self.config.enable_monitoring:
            steps.append(PipelineStep(
                step_id="setup_monitoring",
                name="Setup Monitoring",
                stage=PipelineStage.MONITORING_SETUP,
                command=f"python setup_monitoring.py --model-name {model_name}",
                dependencies=["k8s_deploy"] if target_environment == DeploymentTarget.PRODUCTION else ["docker_build"],
                artifacts=["monitoring_config.json"],
                timeout_minutes=5
            ))
        
        # Create and execute pipeline
        await self.create_pipeline(pipeline_name, steps, creator_type)
        execution_id = await self.execute_pipeline(
            pipeline_name,
            trigger="deployment",
            parameters={
                'model_path': model_path,
                'model_name': model_name,
                'target_environment': target_environment.value,
                'creator_type': creator_type
            }
        )
        
        logger.info(f"🚀 Model deployment pipeline started: {execution_id}")
        return execution_id
    
    async def rollback_deployment(
        self,
        model_name: str,
        target_version: str,
        target_environment: DeploymentTarget
    ) -> str:
        """
        Rollback model deployment to previous version
        
        Args:
            model_name: Name of model to rollback
            target_version: Version to rollback to
            target_environment: Environment to rollback in
            
        Returns:
            Execution ID
        """
        pipeline_name = f"rollback-{model_name}-{target_environment.value}"
        
        steps = [
            PipelineStep(
                step_id="backup_current",
                name="Backup Current Deployment",
                stage=PipelineStage.ROLLBACK,
                command=f"kubectl get deployment {model_name} -o yaml > current_deployment_backup.yaml",
                artifacts=["current_deployment_backup.yaml"],
                timeout_minutes=5
            ),
            PipelineStep(
                step_id="rollback_deployment",
                name="Rollback to Previous Version",
                stage=PipelineStage.ROLLBACK,
                command=f"kubectl set image deployment/{model_name} {model_name}={model_name}:{target_version}",
                dependencies=["backup_current"],
                timeout_minutes=10
            ),
            PipelineStep(
                step_id="verify_rollback",
                name="Verify Rollback",
                stage=PipelineStage.ROLLBACK,
                command=f"python verify_deployment.py --model-name {model_name} --expected-version {target_version}",
                dependencies=["rollback_deployment"],
                artifacts=["rollback_verification.json"],
                timeout_minutes=15
            )
        ]
        
        await self.create_pipeline(pipeline_name, steps)
        execution_id = await self.execute_pipeline(
            pipeline_name,
            trigger="rollback",
            parameters={
                'model_name': model_name,
                'target_version': target_version,
                'target_environment': target_environment.value
            }
        )
        
        logger.info(f"🔄 Rollback pipeline started: {execution_id}")
        return execution_id
    
    def get_pipeline_status(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """Get status of pipeline execution"""
        if execution_id not in self.executions:
            return None
        
        execution = self.executions[execution_id]
        return execution.to_dict()
    
    def list_executions(
        self,
        pipeline_name: Optional[str] = None,
        status: Optional[PipelineStatus] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """List pipeline executions with filtering"""
        executions = list(self.executions.values())
        
        # Filter by pipeline name
        if pipeline_name:
            executions = [e for e in executions if e.pipeline_name == pipeline_name]
        
        # Filter by status
        if status:
            executions = [e for e in executions if e.status == status]
        
        # Sort by start time (newest first)
        executions.sort(key=lambda x: x.started_at, reverse=True)
        
        # Limit results
        executions = executions[:limit]
        
        return [e.to_dict() for e in executions]
    
    def get_mlops_analytics(self) -> Dict[str, Any]:
        """Get comprehensive MLOps analytics"""
        executions = list(self.executions.values())
        
        # Success rate
        total_executions = len(executions)
        successful_executions = len([e for e in executions if e.status == PipelineStatus.SUCCESS])
        success_rate = successful_executions / total_executions if total_executions > 0 else 0
        
        # Average execution time
        completed_executions = [e for e in executions if e.completed_at]
        avg_duration = sum(e.duration_seconds for e in completed_executions) / len(completed_executions) if completed_executions else 0
        
        # Pipeline distribution
        pipeline_distribution = {}
        for execution in executions:
            pipeline_distribution[execution.pipeline_name] = pipeline_distribution.get(execution.pipeline_name, 0) + 1
        
        # Stage success rates
        stage_stats = {}
        for execution in executions:
            for step_id, step_result in execution.step_results.items():
                stage = step_result.get('stage', 'unknown')
                if stage not in stage_stats:
                    stage_stats[stage] = {'total': 0, 'success': 0}
                
                stage_stats[stage]['total'] += 1
                if step_result['status'] == PipelineStatus.SUCCESS.value:
                    stage_stats[stage]['success'] += 1
        
        return {
            'mlops_orchestrator': 'v1.0',
            'project_name': self.config.project_name,
            'analytics_timestamp': datetime.utcnow().isoformat(),
            'execution_stats': {
                'total_executions': total_executions,
                'successful_executions': successful_executions,
                'failed_executions': len([e for e in executions if e.status == PipelineStatus.FAILED]),
                'success_rate': success_rate,
                'avg_duration_seconds': avg_duration
            },
            'pipeline_distribution': pipeline_distribution,
            'stage_success_rates': {
                stage: stats['success'] / stats['total'] if stats['total'] > 0 else 0
                for stage, stats in stage_stats.items()
            },
            'infrastructure': {
                'docker_enabled': self.config.enable_docker,
                'kubernetes_enabled': self.config.enable_kubernetes,
                'monitoring_enabled': self.config.enable_monitoring,
                'provider': self.config.infrastructure_provider.value
            }
        }
    
    def export_pipeline_config(self, pipeline_name: str, output_path: str) -> str:
        """Export pipeline configuration to file"""
        if pipeline_name not in self.pipelines:
            raise ValueError(f"Pipeline '{pipeline_name}' not found")
        
        steps = self.pipelines[pipeline_name]
        config = {
            'name': pipeline_name,
            'steps': [step.to_dict() for step in steps],
            'exported_at': datetime.utcnow().isoformat()
        }
        
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
        
        logger.info(f"📄 Pipeline config exported: {output_path}")
        return str(output_file)
    
    def get_mlops_summary(self) -> Dict[str, Any]:
        """Get MLOps orchestrator summary"""
        return {
            "mlops_pipeline_orchestrator": "v1.0",
            "project_name": self.config.project_name,
            "configuration": {
                "workspace_path": self.config.workspace_path,
                "infrastructure_provider": self.config.infrastructure_provider.value,
                "deployment_targets": [t.value for t in self.config.deployment_targets],
                "enable_docker": self.config.enable_docker,
                "enable_kubernetes": self.config.enable_kubernetes,
                "enable_monitoring": self.config.enable_monitoring
            },
            "current_state": {
                "total_pipelines": len(self.pipelines),
                "total_executions": len(self.executions),
                "active_executions": len([
                    e for e in self.executions.values()
                    if e.status == PipelineStatus.RUNNING
                ])
            },
            "capabilities": {
                "docker_available": self.docker_manager.client is not None,
                "kubernetes_available": hasattr(self.k8s_manager, 'apps_v1'),
                "git_integration": bool(self.config.git_repository),
                "automated_rollback": self.config.enable_rollback
            }
        }

async def main():
    """Example usage of MLOps Pipeline Orchestrator"""
    # Initialize MLOps orchestrator
    config = MLOpsConfig(
        project_name="ainflue-ml",
        workspace_path="/tmp/mlops-workspace",
        enable_docker=True,
        enable_kubernetes=False,  # Disabled for demo
        enable_monitoring=True
    )
    
    orchestrator = MLOpsPipelineOrchestrator(config)
    
    # Create a sample training pipeline
    training_steps = [
        PipelineStep(
            step_id="data_validation",
            name="Validate Training Data",
            stage=PipelineStage.DATA_VALIDATION,
            command="python validate_data.py --input data/train.csv",
            artifacts=["data_validation_report.json"],
            timeout_minutes=10
        ),
        PipelineStep(
            step_id="feature_engineering",
            name="Engineer Features",
            stage=PipelineStage.FEATURE_ENGINEERING,
            command="python engineer_features.py --input data/train.csv --output features/",
            dependencies=["data_validation"],
            artifacts=["features/*", "feature_metadata.json"],
            timeout_minutes=30
        ),
        PipelineStep(
            step_id="model_training",
            name="Train ML Model",
            stage=PipelineStage.MODEL_TRAINING,
            command="python train_model.py --features features/ --output models/",
            dependencies=["feature_engineering"],
            artifacts=["models/*", "training_metrics.json"],
            timeout_minutes=60
        )
    ]
    
    # Create pipeline
    pipeline_name = await orchestrator.create_pipeline(
        "musician-audio-classifier",
        training_steps,
        creator_type="musician"
    )
    
    # Execute pipeline
    execution_id = await orchestrator.execute_pipeline(
        pipeline_name,
        trigger="git_push",
        parameters={"model_type": "audio_classifier", "creator_type": "musician"}
    )
    
    print(f"🚀 Pipeline execution started: {execution_id}")
    
    # Wait a bit for demo (in real usage, this would be async)
    await asyncio.sleep(2)
    
    # Check pipeline status
    status = orchestrator.get_pipeline_status(execution_id)
    print(f"📊 Pipeline Status: {json.dumps(status, indent=2)}")
    
    # Get MLOps analytics
    analytics = orchestrator.get_mlops_analytics()
    print(f"📈 MLOps Analytics: {json.dumps(analytics, indent=2)}")
    
    # Export pipeline configuration
    config_file = orchestrator.export_pipeline_config(
        pipeline_name,
        "/tmp/pipeline_config.yaml"
    )
    print(f"📄 Pipeline config exported to: {config_file}")
    
    # Get summary
    summary = orchestrator.get_mlops_summary()
    print(f"⚙️ MLOps Summary: {json.dumps(summary, indent=2)}")

if __name__ == "__main__":
    asyncio.run(main())