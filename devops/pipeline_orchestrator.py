"""
🚀 Pipeline Orchestrator - CI/CD Pipeline Automation Engine
===========================================================

Enterprise-grade CI/CD pipeline automation with multi-stage coordination,
parallel execution, artifact management, and quality gates integration.

Features:
- Multi-stage pipeline coordination and optimization
- Parallel execution with dependency management
- Artifact versioning and promotion workflows
- Pipeline performance analytics and bottleneck detection
- Integration with quality gates and security scanning
- Dynamic pipeline generation and templating
- Cross-platform deployment orchestration
- Pipeline-as-Code with version control integration

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
Role: DevOps Engineer + CI/CD Engineering + Pipeline Architecture + MLOps
"""

import asyncio
import logging
import json
import yaml
import hashlib
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from collections import defaultdict, deque
import uuid
import tempfile
import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)

class PipelineStatus(Enum):
    """Pipeline execution status"""
    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"
    SKIPPED = "skipped"

class StageType(Enum):
    """Pipeline stage types"""
    BUILD = "build"
    TEST = "test"
    SECURITY_SCAN = "security_scan"
    QUALITY_GATE = "quality_gate"
    PACKAGE = "package"
    DEPLOY = "deploy"
    VERIFY = "verify"
    PROMOTE = "promote"
    NOTIFY = "notify"

class TriggerType(Enum):
    """Pipeline trigger types"""
    MANUAL = "manual"
    WEBHOOK = "webhook"
    SCHEDULE = "schedule"
    TAG = "tag"
    BRANCH = "branch"
    PULL_REQUEST = "pull_request"

class ArtifactType(Enum):
    """Artifact types"""
    SOURCE_CODE = "source_code"
    BINARY = "binary"
    CONTAINER_IMAGE = "container_image"
    DOCUMENTATION = "documentation"
    TEST_RESULTS = "test_results"
    SECURITY_REPORT = "security_report"
    PACKAGE = "package"

@dataclass
class PipelineStage:
    """Pipeline stage definition"""
    stage_id: str
    name: str
    stage_type: StageType
    commands: List[str]
    environment: Dict[str, str]
    dependencies: List[str]
    parallel: bool = False
    timeout: int = 1800  # 30 minutes
    retry_count: int = 0
    condition: Optional[str] = None
    artifacts: Dict[str, str] = field(default_factory=dict)
    docker_image: Optional[str] = None

@dataclass
class PipelineExecution:
    """Pipeline execution instance"""
    execution_id: str
    pipeline_id: str
    trigger_type: TriggerType
    trigger_data: Dict[str, Any]
    status: PipelineStatus
    start_time: datetime
    end_time: Optional[datetime] = None
    stages: List[Dict[str, Any]] = field(default_factory=list)
    artifacts: Dict[str, str] = field(default_factory=dict)
    logs: List[str] = field(default_factory=list)
    metrics: Dict[str, float] = field(default_factory=dict)
    environment_vars: Dict[str, str] = field(default_factory=dict)

@dataclass
class Pipeline:
    """Pipeline definition"""
    pipeline_id: str
    name: str
    description: str
    repository: str
    branch: str
    stages: List[PipelineStage]
    triggers: List[Dict[str, Any]]
    environment_vars: Dict[str, str]
    notifications: List[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime
    version: str = "1.0.0"
    enabled: bool = True

@dataclass
class Artifact:
    """Pipeline artifact"""
    artifact_id: str
    name: str
    artifact_type: ArtifactType
    version: str
    size_bytes: int
    checksum: str
    storage_path: str
    created_at: datetime
    pipeline_execution_id: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    retention_days: int = 30

@dataclass
class QualityGate:
    """Quality gate definition"""
    gate_id: str
    name: str
    conditions: List[Dict[str, Any]]
    threshold_type: str  # AND, OR
    enabled: bool = True
    blocking: bool = True

class PipelineOrchestrator:
    """
    CI/CD Pipeline Automation Engine
    
    Responsibilities:
    - Multi-stage pipeline execution and coordination
    - Parallel and sequential stage execution management
    - Artifact lifecycle management and promotion
    - Quality gate enforcement and integration
    - Pipeline performance optimization and analytics
    - Dynamic pipeline generation from templates
    - Cross-environment deployment coordination
    - Pipeline monitoring and alerting
    """
    
    def __init__(self) -> None:
        # Pipeline management
        self.pipelines: Dict[str, Pipeline] = {}
        self.pipeline_executions: Dict[str, PipelineExecution] = {}
        self.execution_queue: deque = deque()
        self.active_executions: Dict[str, PipelineExecution] = {}
        
        # Artifact management
        self.artifacts: Dict[str, Artifact] = {}
        self.artifact_storage: Dict[str, str] = {}
        
        # Quality gates
        self.quality_gates: Dict[str, QualityGate] = {}
        
        # Pipeline templates
        self.pipeline_templates: Dict[str, Dict] = {}
        
        # Metrics and analytics
        self.pipeline_metrics: deque = deque(maxlen=10000)
        self.performance_analytics: Dict[str, Dict] = {}
        
        # Execution workers
        self.worker_pool_size = 5
        self.active_workers: Dict[str, Dict] = {}
        
        # Configuration
        self.orchestrator_config: Dict[str, Any] = {}
        
        self._initialize_pipeline_orchestrator()
        
        logger.info("PipelineOrchestrator initialized")

    def _initialize_pipeline_orchestrator(self) -> None:
        """Initialize pipeline orchestrator"""
        
        # Start background tasks
        asyncio.create_task(self._pipeline_execution_loop())
        asyncio.create_task(self._artifact_cleanup_loop())
        asyncio.create_task(self._metrics_collection_loop())
        asyncio.create_task(self._pipeline_monitoring_loop())
        
        # Initialize configurations
        self._setup_default_quality_gates()
        self._setup_pipeline_templates()
        self._setup_orchestrator_config()
        
        # Initialize worker pool
        for i in range(self.worker_pool_size):
            worker_id = f"worker_{i+1}"
            self.active_workers[worker_id] = {
                "status": "idle",
                "current_execution": None,
                "last_activity": datetime.now()
            }
        
        logger.info("Pipeline orchestrator initialization complete")

    def _setup_default_quality_gates(self) -> None:
        """Setup default quality gates"""
        
        # Code quality gate
        code_quality_gate = QualityGate(
            gate_id="code_quality",
            name="Code Quality Gate",
            conditions=[
                {
                    "metric": "code_coverage",
                    "operator": "greater_than",
                    "threshold": 80.0,
                    "unit": "percent"
                },
                {
                    "metric": "sonar_quality_gate",
                    "operator": "equals",
                    "threshold": "PASSED",
                    "unit": "status"
                },
                {
                    "metric": "technical_debt",
                    "operator": "less_than",
                    "threshold": 30.0,
                    "unit": "days"
                }
            ],
            threshold_type="AND",
            enabled=True,
            blocking=True
        )
        
        # Security gate
        security_gate = QualityGate(
            gate_id="security",
            name="Security Quality Gate",
            conditions=[
                {
                    "metric": "critical_vulnerabilities",
                    "operator": "equals",
                    "threshold": 0,
                    "unit": "count"
                },
                {
                    "metric": "high_vulnerabilities",
                    "operator": "less_than",
                    "threshold": 5,
                    "unit": "count"
                },
                {
                    "metric": "security_scan_status",
                    "operator": "equals",
                    "threshold": "PASSED",
                    "unit": "status"
                }
            ],
            threshold_type="AND",
            enabled=True,
            blocking=True
        )
        
        # Performance gate
        performance_gate = QualityGate(
            gate_id="performance",
            name="Performance Quality Gate",
            conditions=[
                {
                    "metric": "response_time_p95",
                    "operator": "less_than",
                    "threshold": 200.0,
                    "unit": "milliseconds"
                },
                {
                    "metric": "memory_usage",
                    "operator": "less_than",
                    "threshold": 512.0,
                    "unit": "megabytes"
                },
                {
                    "metric": "load_test_success_rate",
                    "operator": "greater_than",
                    "threshold": 99.0,
                    "unit": "percent"
                }
            ],
            threshold_type="AND",
            enabled=True,
            blocking=False  # Non-blocking for performance
        )
        
        self.quality_gates[code_quality_gate.gate_id] = code_quality_gate
        self.quality_gates[security_gate.gate_id] = security_gate
        self.quality_gates[performance_gate.gate_id] = performance_gate

    def _setup_pipeline_templates(self) -> None:
        """Setup pipeline templates"""
        
        # Web application template
        web_app_template = {
            "name": "Web Application Pipeline",
            "description": "Standard web application CI/CD pipeline",
            "stages": [
                {
                    "name": "Checkout",
                    "type": "build",
                    "commands": ["git clone ${REPOSITORY_URL}", "cd ${WORKSPACE}"],
                    "timeout": 300
                },
                {
                    "name": "Install Dependencies",
                    "type": "build",
                    "commands": ["npm install", "pip install -r requirements.txt"],
                    "timeout": 600
                },
                {
                    "name": "Lint Code",
                    "type": "test",
                    "commands": ["npm run lint", "flake8 .", "black --check ."],
                    "timeout": 300
                },
                {
                    "name": "Unit Tests",
                    "type": "test", 
                    "commands": ["npm test", "pytest --coverage"],
                    "timeout": 900
                },
                {
                    "name": "Security Scan",
                    "type": "security_scan",
                    "commands": ["npm audit", "bandit -r .", "trivy fs ."],
                    "timeout": 600
                },
                {
                    "name": "Build Application",
                    "type": "build",
                    "commands": ["npm run build", "docker build -t ${IMAGE_NAME}:${BUILD_NUMBER} ."],
                    "timeout": 1200
                },
                {
                    "name": "Quality Gate",
                    "type": "quality_gate",
                    "commands": ["sonar-scanner"],
                    "timeout": 600
                },
                {
                    "name": "Deploy to Staging",
                    "type": "deploy",
                    "commands": ["kubectl apply -f k8s/staging/", "helm upgrade --install staging ./chart"],
                    "timeout": 900
                },
                {
                    "name": "Integration Tests",
                    "type": "test",
                    "commands": ["newman run integration-tests.json"],
                    "timeout": 1200
                },
                {
                    "name": "Deploy to Production",
                    "type": "deploy",
                    "commands": ["kubectl apply -f k8s/production/", "helm upgrade --install production ./chart"],
                    "timeout": 900,
                    "condition": "branch == 'main' && quality_gate_passed"
                }
            ],
            "quality_gates": ["code_quality", "security", "performance"],
            "notifications": [
                {
                    "type": "slack",
                    "events": ["pipeline_failed", "pipeline_success"],
                    "webhook": "${SLACK_WEBHOOK_URL}"
                },
                {
                    "type": "email",
                    "events": ["pipeline_failed"],
                    "recipients": ["${TEAM_EMAIL}"]
                }
            ]
        }
        
        # Microservice template
        microservice_template = {
            "name": "Microservice Pipeline",
            "description": "Microservice CI/CD pipeline with container registry",
            "stages": [
                {
                    "name": "Checkout",
                    "type": "build",
                    "commands": ["git clone ${REPOSITORY_URL}", "cd ${WORKSPACE}"],
                    "timeout": 300
                },
                {
                    "name": "Build Service",
                    "type": "build",
                    "commands": ["docker build -t ${SERVICE_NAME}:${BUILD_NUMBER} .", "docker tag ${SERVICE_NAME}:${BUILD_NUMBER} ${REGISTRY}/${SERVICE_NAME}:${BUILD_NUMBER}"],
                    "timeout": 900
                },
                {
                    "name": "Unit Tests",
                    "type": "test",
                    "commands": ["docker run --rm ${SERVICE_NAME}:${BUILD_NUMBER} npm test"],
                    "timeout": 600
                },
                {
                    "name": "Security Scan",
                    "type": "security_scan",
                    "commands": ["trivy image ${SERVICE_NAME}:${BUILD_NUMBER}", "clair-scanner ${SERVICE_NAME}:${BUILD_NUMBER}"],
                    "timeout": 600
                },
                {
                    "name": "Push to Registry",
                    "type": "package",
                    "commands": ["docker push ${REGISTRY}/${SERVICE_NAME}:${BUILD_NUMBER}"],
                    "timeout": 600
                },
                {
                    "name": "Deploy to Dev",
                    "type": "deploy",
                    "commands": ["kubectl set image deployment/${SERVICE_NAME} ${SERVICE_NAME}=${REGISTRY}/${SERVICE_NAME}:${BUILD_NUMBER}"],
                    "timeout": 300
                },
                {
                    "name": "Contract Tests",
                    "type": "test",
                    "commands": ["pact-broker publish", "pact-broker verify"],
                    "timeout": 900
                },
                {
                    "name": "Promote to Production",
                    "type": "promote",
                    "commands": ["kubectl set image deployment/${SERVICE_NAME} ${SERVICE_NAME}=${REGISTRY}/${SERVICE_NAME}:${BUILD_NUMBER} -n production"],
                    "timeout": 600,
                    "condition": "tests_passed && security_scan_passed"
                }
            ],
            "quality_gates": ["security"],
            "parallel_stages": ["Unit Tests", "Security Scan"]
        }
        
        self.pipeline_templates["web_application"] = web_app_template
        self.pipeline_templates["microservice"] = microservice_template

    def _setup_orchestrator_config(self) -> None:
        """Setup orchestrator configuration"""
        
        self.orchestrator_config = {
            "max_concurrent_executions": 10,
            "max_queue_size": 100,
            "default_timeout": 3600,  # 1 hour
            "artifact_retention_days": 30,
            "log_retention_days": 90,
            "metrics_retention_days": 365,
            "worker_pool_size": 5,
            "execution_parallelism": 3,
            "artifact_storage_path": "/tmp/artifacts",
            "workspace_path": "/tmp/workspaces"
        }

    async def create_pipeline(
        self,
        name: str,
        description: str,
        repository: str,
        branch: str = "main",
        template: Optional[str] = None,
        stages: Optional[List[Dict[str, Any]]] = None,
        triggers: Optional[List[Dict[str, Any]]] = None,
        environment_vars: Optional[Dict[str, str]] = None
    ) -> str:
        """
        Create new CI/CD pipeline
        
        Args:
            name: Pipeline name
            description: Pipeline description
            repository: Source repository URL
            branch: Default branch
            template: Pipeline template to use
            stages: Custom stages (if not using template)
            triggers: Pipeline triggers
            environment_vars: Environment variables
            
        Returns:
            Pipeline ID
        """
        
        try:
            pipeline_id = str(uuid.uuid4())
            
            # Use template if specified
            if template and template in self.pipeline_templates:
                template_config = self.pipeline_templates[template]
                pipeline_stages = self._create_stages_from_template(template_config["stages"])
            elif stages:
                pipeline_stages = self._create_stages_from_config(stages)
            else:
                raise ValueError("Either template or stages must be specified")
            
            # Default triggers
            default_triggers = [
                {
                    "type": TriggerType.WEBHOOK.value,
                    "events": ["push", "pull_request"],
                    "branches": [branch]
                }
            ]
            
            pipeline = Pipeline(
                pipeline_id=pipeline_id,
                name=name,
                description=description,
                repository=repository,
                branch=branch,
                stages=pipeline_stages,
                triggers=triggers or default_triggers,
                environment_vars=environment_vars or {},
                notifications=[],
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            self.pipelines[pipeline_id] = pipeline
            
            logger.info(f"Pipeline created: {name} ({pipeline_id})")
            return pipeline_id
            
        except Exception as e:
            logger.error(f"Pipeline creation failed: {str(e)}")
            raise

    def _create_stages_from_template(self, template_stages: List[Dict[str, Any]]) -> List[PipelineStage]:
        """Create pipeline stages from template"""
        
        stages = []
        for stage_config in template_stages:
            stage = PipelineStage(
                stage_id=str(uuid.uuid4()),
                name=stage_config["name"],
                stage_type=StageType(stage_config["type"]),
                commands=stage_config["commands"],
                environment={},
                dependencies=[],
                timeout=stage_config.get("timeout", 1800),
                condition=stage_config.get("condition"),
                docker_image=stage_config.get("docker_image")
            )
            stages.append(stage)
        
        return stages

    def _create_stages_from_config(self, stage_configs: List[Dict[str, Any]]) -> List[PipelineStage]:
        """Create pipeline stages from configuration"""
        
        stages = []
        for config in stage_configs:
            stage = PipelineStage(
                stage_id=str(uuid.uuid4()),
                name=config["name"],
                stage_type=StageType(config["type"]),
                commands=config["commands"],
                environment=config.get("environment", {}),
                dependencies=config.get("dependencies", []),
                parallel=config.get("parallel", False),
                timeout=config.get("timeout", 1800),
                retry_count=config.get("retry_count", 0),
                condition=config.get("condition"),
                artifacts=config.get("artifacts", {}),
                docker_image=config.get("docker_image")
            )
            stages.append(stage)
        
        return stages

    async def trigger_pipeline(
        self,
        pipeline_id: str,
        trigger_type: TriggerType,
        trigger_data: Dict[str, Any],
        environment_overrides: Optional[Dict[str, str]] = None
    ) -> str:
        """
        Trigger pipeline execution
        
        Args:
            pipeline_id: Pipeline identifier
            trigger_type: Type of trigger
            trigger_data: Trigger-specific data
            environment_overrides: Environment variable overrides
            
        Returns:
            Execution ID
        """
        
        try:
            if pipeline_id not in self.pipelines:
                raise ValueError(f"Pipeline not found: {pipeline_id}")
            
            pipeline = self.pipelines[pipeline_id]
            
            if not pipeline.enabled:
                raise ValueError(f"Pipeline is disabled: {pipeline_id}")
            
            execution_id = str(uuid.uuid4())
            
            # Merge environment variables
            execution_env = pipeline.environment_vars.copy()
            if environment_overrides:
                execution_env.update(environment_overrides)
            
            execution = PipelineExecution(
                execution_id=execution_id,
                pipeline_id=pipeline_id,
                trigger_type=trigger_type,
                trigger_data=trigger_data,
                status=PipelineStatus.QUEUED,
                start_time=datetime.now(),
                environment_vars=execution_env
            )
            
            # Add to queue
            self.execution_queue.append(execution)
            self.pipeline_executions[execution_id] = execution
            
            logger.info(f"Pipeline triggered: {pipeline.name} (Execution: {execution_id})")
            return execution_id
            
        except Exception as e:
            logger.error(f"Pipeline trigger failed: {str(e)}")
            raise

    async def _execute_pipeline(self, execution -> None: PipelineExecution) -> None:
        """Execute pipeline stages"""
        
        try:
            pipeline = self.pipelines[execution.pipeline_id]
            execution.status = PipelineStatus.RUNNING
            execution.start_time = datetime.now()
            
            logger.info(f"Starting pipeline execution: {execution.execution_id}")
            
            # Create execution workspace
            workspace_path = await self._create_workspace(execution)
            execution.environment_vars["WORKSPACE"] = workspace_path
            
            # Execute stages
            for stage in pipeline.stages:
                # Check stage condition
                if stage.condition and not await self._evaluate_stage_condition(stage.condition, execution):
                    execution.stages.append({
                        "stage_id": stage.stage_id,
                        "name": stage.name,
                        "status": PipelineStatus.SKIPPED.value,
                        "start_time": datetime.now().isoformat(),
                        "end_time": datetime.now().isoformat(),
                        "reason": f"Condition not met: {stage.condition}"
                    })
                    continue
                
                # Check dependencies
                if not await self._check_stage_dependencies(stage, execution):
                    execution.stages.append({
                        "stage_id": stage.stage_id,
                        "name": stage.name,
                        "status": PipelineStatus.FAILED.value,
                        "start_time": datetime.now().isoformat(),
                        "end_time": datetime.now().isoformat(),
                        "reason": "Stage dependencies not satisfied"
                    })
                    execution.status = PipelineStatus.FAILED
                    break
                
                # Execute stage
                stage_result = await self._execute_stage(stage, execution, workspace_path)
                execution.stages.append(stage_result)
                
                # Check quality gates for quality_gate stages
                if stage.stage_type == StageType.QUALITY_GATE:
                    quality_gate_result = await self._evaluate_quality_gates(execution)
                    if not quality_gate_result["passed"]:
                        execution.status = PipelineStatus.FAILED
                        execution.logs.append(f"Quality gate failed: {quality_gate_result['reasons']}")
                        break
                
                # Break on stage failure
                if stage_result["status"] == PipelineStatus.FAILED.value:
                    execution.status = PipelineStatus.FAILED
                    break
            
            # Set final status
            if execution.status == PipelineStatus.RUNNING:
                execution.status = PipelineStatus.SUCCESS
            
            execution.end_time = datetime.now()
            
            # Cleanup workspace
            await self._cleanup_workspace(workspace_path)
            
            # Send notifications
            await self._send_pipeline_notifications(pipeline, execution)
            
            # Collect metrics
            await self._collect_pipeline_metrics(execution)
            
            logger.info(f"Pipeline execution completed: {execution.execution_id} - {execution.status.value}")
            
        except Exception as e:
            execution.status = PipelineStatus.FAILED
            execution.end_time = datetime.now()
            execution.logs.append(f"Pipeline execution error: {str(e)}")
            logger.error(f"Pipeline execution failed: {execution.execution_id} - {str(e)}")

    async def _create_workspace(self, execution: PipelineExecution) -> str:
        """Create execution workspace"""
        
        workspace_path = f"{self.orchestrator_config['workspace_path']}/{execution.execution_id}"
        Path(workspace_path).mkdir(parents=True, exist_ok=True)
        
        return workspace_path

    async def _cleanup_workspace(self, workspace_path -> None: str) -> None:
        """Cleanup execution workspace"""
        
        try:
            import shutil
            shutil.rmtree(workspace_path, ignore_errors=True)
        except Exception as e:
            logger.warning(f"Workspace cleanup failed: {str(e)}")

    async def _evaluate_stage_condition(self, condition: str, execution: PipelineExecution) -> bool:
        """Evaluate stage execution condition"""
        
        # Mock condition evaluation
        # In real implementation, parse and evaluate condition expressions
        if "branch == 'main'" in condition:
            return execution.trigger_data.get("branch", "") == "main"
        elif "quality_gate_passed" in condition:
            return execution.metrics.get("quality_gate_score", 0) > 0.8
        
        return True  # Default to true for mock

    async def _check_stage_dependencies(self, stage: PipelineStage, execution: PipelineExecution) -> bool:
        """Check if stage dependencies are satisfied"""
        
        if not stage.dependencies:
            return True
        
        for dep_stage_name in stage.dependencies:
            # Find dependency stage result
            dep_found = False
            for stage_result in execution.stages:
                if stage_result["name"] == dep_stage_name:
                    dep_found = True
                    if stage_result["status"] != PipelineStatus.SUCCESS.value:
                        return False
                    break
            
            if not dep_found:
                return False
        
        return True

    async def _execute_stage(
        self,
        stage: PipelineStage,
        execution: PipelineExecution,
        workspace_path: str
    ) -> Dict[str, Any]:
        """Execute individual pipeline stage"""
        
        stage_start = datetime.now()
        stage_result = {
            "stage_id": stage.stage_id,
            "name": stage.name,
            "status": PipelineStatus.RUNNING.value,
            "start_time": stage_start.isoformat(),
            "logs": [],
            "artifacts": {},
            "metrics": {}
        }
        
        try:
            logger.info(f"Executing stage: {stage.name} (Execution: {execution.execution_id})")
            
            # Prepare environment
            stage_env = execution.environment_vars.copy()
            stage_env.update(stage.environment)
            stage_env["STAGE_NAME"] = stage.name
            stage_env["EXECUTION_ID"] = execution.execution_id
            
            # Execute commands
            for command in stage.commands:
                # Substitute environment variables
                resolved_command = self._resolve_environment_variables(command, stage_env)
                
                # Mock command execution
                command_result = await self._execute_command(
                    resolved_command,
                    workspace_path,
                    stage_env,
                    stage.timeout
                )
                
                stage_result["logs"].append({
                    "command": resolved_command,
                    "exit_code": command_result["exit_code"],
                    "stdout": command_result["stdout"],
                    "stderr": command_result["stderr"]
                })
                
                if command_result["exit_code"] != 0:
                    stage_result["status"] = PipelineStatus.FAILED.value
                    stage_result["error"] = f"Command failed: {resolved_command}"
                    break
            
            # Handle artifacts
            if stage_result["status"] != PipelineStatus.FAILED.value:
                artifacts = await self._collect_stage_artifacts(stage, workspace_path, execution.execution_id)
                stage_result["artifacts"] = artifacts
                execution.artifacts.update(artifacts)
            
            # Set success status if no failures
            if stage_result["status"] == PipelineStatus.RUNNING.value:
                stage_result["status"] = PipelineStatus.SUCCESS.value
            
        except Exception as e:
            stage_result["status"] = PipelineStatus.FAILED.value
            stage_result["error"] = str(e)
            logger.error(f"Stage execution failed: {stage.name} - {str(e)}")
        
        finally:
            stage_result["end_time"] = datetime.now().isoformat()
            stage_result["duration"] = (datetime.now() - stage_start).total_seconds()
        
        return stage_result

    def _resolve_environment_variables(self, command: str, env_vars: Dict[str, str]) -> str:
        """Resolve environment variables in command"""
        
        resolved_command = command
        for var_name, var_value in env_vars.items():
            resolved_command = resolved_command.replace(f"${{{var_name}}}", var_value)
            resolved_command = resolved_command.replace(f"${var_name}", var_value)
        
        return resolved_command

    async def _execute_command(
        self,
        command: str,
        working_dir: str,
        env_vars: Dict[str, str],
        timeout: int
    ) -> Dict[str, Any]:
        """Execute shell command"""
        
        try:
            # Mock command execution
            await asyncio.sleep(0.5)  # Simulate execution time
            
            # Mock different command results
            if "test" in command.lower():
                # Mock test results
                import random
                success = random.random() > 0.1  # 90% success rate
                return {
                    "exit_code": 0 if success else 1,
                    "stdout": "Tests passed" if success else "Tests failed",
                    "stderr": "" if success else "Test failure details"
                }
            elif "build" in command.lower():
                # Mock build results
                return {
                    "exit_code": 0,
                    "stdout": "Build completed successfully",
                    "stderr": ""
                }
            elif "scan" in command.lower():
                # Mock security scan results
                return {
                    "exit_code": 0,
                    "stdout": "Security scan completed - no critical issues",
                    "stderr": ""
                }
            else:
                # Mock generic command success
                return {
                    "exit_code": 0,
                    "stdout": f"Command executed: {command}",
                    "stderr": ""
                }
                
        except Exception as e:
            return {
                "exit_code": 1,
                "stdout": "",
                "stderr": str(e)
            }

    async def _collect_stage_artifacts(
        self,
        stage: PipelineStage,
        workspace_path: str,
        execution_id: str
    ) -> Dict[str, str]:
        """Collect artifacts from stage execution"""
        
        artifacts = {}
        
        for artifact_name, artifact_path in stage.artifacts.items():
            try:
                # Mock artifact collection
                artifact_id = str(uuid.uuid4())
                storage_path = f"{self.orchestrator_config['artifact_storage_path']}/{execution_id}/{artifact_name}"
                
                # Create artifact record
                artifact = Artifact(
                    artifact_id=artifact_id,
                    name=artifact_name,
                    artifact_type=ArtifactType.BINARY,  # Default type
                    version="1.0.0",
                    size_bytes=1024,  # Mock size
                    checksum=hashlib.md5(artifact_name.encode()).hexdigest(),
                    storage_path=storage_path,
                    created_at=datetime.now(),
                    pipeline_execution_id=execution_id
                )
                
                self.artifacts[artifact_id] = artifact
                artifacts[artifact_name] = artifact_id
                
                logger.info(f"Artifact collected: {artifact_name} -> {artifact_id}")
                
            except Exception as e:
                logger.error(f"Artifact collection failed: {artifact_name} - {str(e)}")
        
        return artifacts

    async def _evaluate_quality_gates(self, execution: PipelineExecution) -> Dict[str, Any]:
        """Evaluate quality gates for pipeline"""
        
        try:
            gate_results = []
            overall_passed = True
            
            for gate_id, quality_gate in self.quality_gates.items():
                if not quality_gate.enabled:
                    continue
                
                gate_result = await self._evaluate_single_quality_gate(quality_gate, execution)
                gate_results.append(gate_result)
                
                if quality_gate.blocking and not gate_result["passed"]:
                    overall_passed = False
            
            return {
                "passed": overall_passed,
                "gate_results": gate_results,
                "reasons": [r["reason"] for r in gate_results if not r["passed"]]
            }
            
        except Exception as e:
            logger.error(f"Quality gate evaluation failed: {str(e)}")
            return {
                "passed": False,
                "gate_results": [],
                "reasons": [f"Quality gate evaluation error: {str(e)}"]
            }

    async def _evaluate_single_quality_gate(
        self,
        quality_gate: QualityGate,
        execution: PipelineExecution
    ) -> Dict[str, Any]:
        """Evaluate single quality gate"""
        
        try:
            condition_results = []
            
            for condition in quality_gate.conditions:
                condition_result = await self._evaluate_quality_condition(condition, execution)
                condition_results.append(condition_result)
            
            # Apply threshold logic (AND/OR)
            if quality_gate.threshold_type == "AND":
                gate_passed = all(result["passed"] for result in condition_results)
            else:  # OR
                gate_passed = any(result["passed"] for result in condition_results)
            
            return {
                "gate_id": quality_gate.gate_id,
                "name": quality_gate.name,
                "passed": gate_passed,
                "blocking": quality_gate.blocking,
                "condition_results": condition_results,
                "reason": f"Quality gate {'passed' if gate_passed else 'failed'}: {quality_gate.name}"
            }
            
        except Exception as e:
            logger.error(f"Quality gate evaluation failed: {quality_gate.gate_id} - {str(e)}")
            return {
                "gate_id": quality_gate.gate_id,
                "name": quality_gate.name,
                "passed": False,
                "blocking": quality_gate.blocking,
                "condition_results": [],
                "reason": f"Quality gate evaluation error: {str(e)}"
            }

    async def _evaluate_quality_condition(
        self,
        condition: Dict[str, Any],
        execution: PipelineExecution
    ) -> Dict[str, Any]:
        """Evaluate single quality condition"""
        
        try:
            metric_name = condition["metric"]
            operator = condition["operator"]
            threshold = condition["threshold"]
            
            # Mock metric values (in real implementation, get from monitoring/testing tools)
            mock_metrics = {
                "code_coverage": 85.5,
                "sonar_quality_gate": "PASSED",
                "technical_debt": 12.5,
                "critical_vulnerabilities": 0,
                "high_vulnerabilities": 2,
                "security_scan_status": "PASSED",
                "response_time_p95": 150.0,
                "memory_usage": 256.0,
                "load_test_success_rate": 99.5
            }
            
            current_value = mock_metrics.get(metric_name, 0)
            
            # Evaluate condition
            passed = False
            if operator == "greater_than":
                passed = current_value > threshold
            elif operator == "less_than":
                passed = current_value < threshold
            elif operator == "equals":
                passed = current_value == threshold
            elif operator == "not_equals":
                passed = current_value != threshold
            
            return {
                "metric": metric_name,
                "operator": operator,
                "threshold": threshold,
                "current_value": current_value,
                "passed": passed,
                "reason": f"{metric_name} {operator} {threshold}: {current_value} ({'✓' if passed else '✗'})"
            }
            
        except Exception as e:
            logger.error(f"Quality condition evaluation failed: {str(e)}")
            return {
                "metric": condition.get("metric", "unknown"),
                "passed": False,
                "reason": f"Condition evaluation error: {str(e)}"
            }

    async def _send_pipeline_notifications(self, pipeline -> None: Pipeline, execution -> None: PipelineExecution) -> None:
        """Send pipeline notifications"""
        
        try:
            for notification in pipeline.notifications:
                notification_type = notification.get("type")
                events = notification.get("events", [])
                
                # Check if notification should be sent
                should_notify = False
                if execution.status == PipelineStatus.SUCCESS and "pipeline_success" in events:
                    should_notify = True
                elif execution.status == PipelineStatus.FAILED and "pipeline_failed" in events:
                    should_notify = True
                
                if should_notify:
                    await self._send_notification(notification_type, notification, pipeline, execution)
                    
        except Exception as e:
            logger.error(f"Pipeline notification failed: {str(e)}")

    async def _send_notification(
        self,
        notification_type -> None: str,
        notification_config -> None: Dict[str, Any],
        pipeline -> None: Pipeline,
        execution -> None: PipelineExecution
    ) -> None:
        """Send specific notification"""
        
        try:
            message = self._build_notification_message(pipeline, execution)
            
            if notification_type == "slack":
                # Mock Slack notification
                webhook_url = notification_config.get("webhook")
                logger.info(f"Sending Slack notification to {webhook_url}: {message}")
            
            elif notification_type == "email":
                # Mock email notification
                recipients = notification_config.get("recipients", [])
                logger.info(f"Sending email notification to {recipients}: {message}")
            
            elif notification_type == "webhook":
                # Mock webhook notification
                webhook_url = notification_config.get("url")
                logger.info(f"Sending webhook notification to {webhook_url}: {message}")
                
        except Exception as e:
            logger.error(f"Notification sending failed: {notification_type} - {str(e)}")

    def _build_notification_message(self, pipeline: Pipeline, execution: PipelineExecution) -> str:
        """Build notification message"""
        
        status_emoji = "✅" if execution.status == PipelineStatus.SUCCESS else "❌"
        duration = (execution.end_time - execution.start_time).total_seconds() if execution.end_time else 0
        
        message = f"{status_emoji} Pipeline {pipeline.name}\n"
        message += f"Status: {execution.status.value}\n"
        message += f"Duration: {duration:.0f}s\n"
        message += f"Execution ID: {execution.execution_id}\n"
        
        if execution.status == PipelineStatus.FAILED:
            failed_stages = [s for s in execution.stages if s.get("status") == PipelineStatus.FAILED.value]
            if failed_stages:
                message += f"Failed Stage: {failed_stages[0]['name']}\n"
        
        return message

    async def _collect_pipeline_metrics(self, execution -> None: PipelineExecution) -> None:
        """Collect pipeline execution metrics"""
        
        try:
            duration = (execution.end_time - execution.start_time).total_seconds() if execution.end_time else 0
            
            metrics = {
                "execution_id": execution.execution_id,
                "pipeline_id": execution.pipeline_id,
                "status": execution.status.value,
                "duration": duration,
                "stage_count": len(execution.stages),
                "success_rate": 1.0 if execution.status == PipelineStatus.SUCCESS else 0.0,
                "timestamp": datetime.now()
            }
            
            # Add stage-specific metrics
            for stage_result in execution.stages:
                stage_duration = stage_result.get("duration", 0)
                metrics[f"stage_{stage_result['name']}_duration"] = stage_duration
            
            self.pipeline_metrics.append(metrics)
            
            # Update performance analytics
            pipeline_id = execution.pipeline_id
            if pipeline_id not in self.performance_analytics:
                self.performance_analytics[pipeline_id] = {
                    "total_executions": 0,
                    "success_count": 0,
                    "failure_count": 0,
                    "avg_duration": 0,
                    "last_execution": None
                }
            
            analytics = self.performance_analytics[pipeline_id]
            analytics["total_executions"] += 1
            if execution.status == PipelineStatus.SUCCESS:
                analytics["success_count"] += 1
            else:
                analytics["failure_count"] += 1
            
            # Update average duration
            analytics["avg_duration"] = (
                (analytics["avg_duration"] * (analytics["total_executions"] - 1) + duration) /
                analytics["total_executions"]
            )
            analytics["last_execution"] = datetime.now()
            
        except Exception as e:
            logger.error(f"Pipeline metrics collection failed: {str(e)}")

    # Background tasks
    async def _pipeline_execution_loop(self) -> None:
        """Background pipeline execution loop"""
        while True:
            try:
                await asyncio.sleep(5)  # Check every 5 seconds
                
                # Process execution queue
                while (self.execution_queue and 
                       len(self.active_executions) < self.orchestrator_config["max_concurrent_executions"]):
                    
                    execution = self.execution_queue.popleft()
                    
                    # Find available worker
                    available_worker = None
                    for worker_id, worker_info in self.active_workers.items():
                        if worker_info["status"] == "idle":
                            available_worker = worker_id
                            break
                    
                    if available_worker:
                        # Assign execution to worker
                        self.active_workers[available_worker]["status"] = "busy"
                        self.active_workers[available_worker]["current_execution"] = execution.execution_id
                        self.active_workers[available_worker]["last_activity"] = datetime.now()
                        
                        self.active_executions[execution.execution_id] = execution
                        
                        # Start execution
                        asyncio.create_task(self._execute_pipeline_with_worker(execution, available_worker))
                    else:
                        # No available workers, put back in queue
                        self.execution_queue.appendleft(execution)
                        break
                
            except Exception as e:
                logger.error(f"Pipeline execution loop error: {str(e)}")

    async def _execute_pipeline_with_worker(self, execution -> None: PipelineExecution, worker_id -> None: str) -> None:
        """Execute pipeline with assigned worker"""
        
        try:
            await self._execute_pipeline(execution)
        finally:
            # Release worker
            self.active_workers[worker_id]["status"] = "idle"
            self.active_workers[worker_id]["current_execution"] = None
            self.active_workers[worker_id]["last_activity"] = datetime.now()
            
            # Remove from active executions
            if execution.execution_id in self.active_executions:
                del self.active_executions[execution.execution_id]

    async def _artifact_cleanup_loop(self) -> None:
        """Background artifact cleanup loop"""
        while True:
            try:
                await asyncio.sleep(86400)  # Run daily
                
                # Cleanup expired artifacts
                cutoff_date = datetime.now() - timedelta(days=self.orchestrator_config["artifact_retention_days"])
                
                expired_artifacts = [
                    artifact_id for artifact_id, artifact in self.artifacts.items()
                    if artifact.created_at < cutoff_date
                ]
                
                for artifact_id in expired_artifacts:
                    artifact = self.artifacts[artifact_id]
                    try:
                        # Remove artifact file
                        Path(artifact.storage_path).unlink(missing_ok=True)
                        # Remove from registry
                        del self.artifacts[artifact_id]
                        logger.info(f"Expired artifact cleaned up: {artifact_id}")
                    except Exception as e:
                        logger.error(f"Artifact cleanup failed: {artifact_id} - {str(e)}")
                
            except Exception as e:
                logger.error(f"Artifact cleanup loop error: {str(e)}")

    async def _metrics_collection_loop(self) -> None:
        """Background metrics collection loop"""
        while True:
            try:
                await asyncio.sleep(300)  # Collect every 5 minutes
                
                # Collect orchestrator metrics
                await self._collect_orchestrator_metrics()
                
            except Exception as e:
                logger.error(f"Metrics collection loop error: {str(e)}")

    async def _collect_orchestrator_metrics(self) -> None:
        """Collect orchestrator-level metrics"""
        
        try:
            metrics = {
                "timestamp": datetime.now(),
                "active_pipelines": len([p for p in self.pipelines.values() if p.enabled]),
                "total_pipelines": len(self.pipelines),
                "active_executions": len(self.active_executions),
                "queued_executions": len(self.execution_queue),
                "total_artifacts": len(self.artifacts),
                "worker_utilization": len([w for w in self.active_workers.values() if w["status"] == "busy"]) / len(self.active_workers) * 100
            }
            
            # Calculate success rates
            recent_executions = [
                m for m in self.pipeline_metrics
                if m["timestamp"] >= datetime.now() - timedelta(hours=24)
            ]
            
            if recent_executions:
                success_rate = sum(m["success_rate"] for m in recent_executions) / len(recent_executions) * 100
                avg_duration = sum(m["duration"] for m in recent_executions) / len(recent_executions)
                
                metrics["success_rate_24h"] = success_rate
                metrics["avg_duration_24h"] = avg_duration
            
            self.pipeline_metrics.append(metrics)
            
        except Exception as e:
            logger.error(f"Orchestrator metrics collection failed: {str(e)}")

    async def _pipeline_monitoring_loop(self) -> None:
        """Background pipeline monitoring loop"""
        while True:
            try:
                await asyncio.sleep(60)  # Monitor every minute
                
                # Monitor active executions for timeouts
                current_time = datetime.now()
                for execution in list(self.active_executions.values()):
                    runtime = (current_time - execution.start_time).total_seconds()
                    max_runtime = self.orchestrator_config["default_timeout"]
                    
                    if runtime > max_runtime:
                        logger.warning(f"Pipeline execution timeout: {execution.execution_id}")
                        execution.status = PipelineStatus.FAILED
                        execution.end_time = current_time
                        execution.logs.append("Pipeline execution timed out")
                
            except Exception as e:
                logger.error(f"Pipeline monitoring loop error: {str(e)}")

    async def health_check(self) -> bool:
        """Pipeline orchestrator health check"""
        
        try:
            # Check worker pool health
            active_workers = len([w for w in self.active_workers.values() if w["status"] in ["idle", "busy"]])
            if active_workers < self.worker_pool_size / 2:
                logger.warning("Insufficient active workers")
                return False
            
            # Check queue size
            if len(self.execution_queue) > self.orchestrator_config["max_queue_size"]:
                logger.warning("Execution queue too large")
                return False
            
            # Check for stuck executions
            stuck_executions = 0
            for execution in self.active_executions.values():
                runtime = (datetime.now() - execution.start_time).total_seconds()
                if runtime > 7200:  # 2 hours
                    stuck_executions += 1
            
            if stuck_executions > 2:
                logger.warning("Too many stuck executions")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Pipeline orchestrator health check failed: {str(e)}")
            return False

    def get_pipeline_dashboard(self) -> Dict[str, Any]:
        """Get comprehensive pipeline dashboard"""
        
        # Calculate pipeline statistics
        total_pipelines = len(self.pipelines)
        enabled_pipelines = len([p for p in self.pipelines.values() if p.enabled])
        
        # Calculate execution statistics
        recent_executions = [
            m for m in self.pipeline_metrics
            if isinstance(m.get("timestamp"), datetime) and 
            m["timestamp"] >= datetime.now() - timedelta(hours=24)
        ]
        
        success_rate = (
            sum(m["success_rate"] for m in recent_executions) / len(recent_executions) * 100
            if recent_executions else 0
        )
        
        avg_duration = (
            sum(m["duration"] for m in recent_executions) / len(recent_executions)
            if recent_executions else 0
        )
        
        return {
            "timestamp": datetime.now().isoformat(),
            "pipelines": {
                "total_pipelines": total_pipelines,
                "enabled_pipelines": enabled_pipelines,
                "pipeline_templates": len(self.pipeline_templates)
            },
            "executions": {
                "active_executions": len(self.active_executions),
                "queued_executions": len(self.execution_queue),
                "total_executions": len(self.pipeline_executions),
                "success_rate_24h": success_rate,
                "avg_duration_24h": avg_duration
            },
            "workers": {
                "total_workers": len(self.active_workers),
                "busy_workers": len([w for w in self.active_workers.values() if w["status"] == "busy"]),
                "idle_workers": len([w for w in self.active_workers.values() if w["status"] == "idle"]),
                "worker_utilization": len([w for w in self.active_workers.values() if w["status"] == "busy"]) / len(self.active_workers) * 100
            },
            "artifacts": {
                "total_artifacts": len(self.artifacts),
                "storage_usage": sum(a.size_bytes for a in self.artifacts.values()),
                "artifact_types": list(set(a.artifact_type.value for a in self.artifacts.values()))
            },
            "quality_gates": {
                "total_gates": len(self.quality_gates),
                "enabled_gates": len([g for g in self.quality_gates.values() if g.enabled]),
                "blocking_gates": len([g for g in self.quality_gates.values() if g.blocking])
            },
            "performance": {
                "avg_execution_time": avg_duration,
                "queue_processing_time": len(self.execution_queue) * 2,  # Mock estimate
                "throughput_executions_per_hour": len(recent_executions) if recent_executions else 0
            }
        }

# Global pipeline orchestrator instance
pipeline_orchestrator = PipelineOrchestrator()

logger.info("🚀 Pipeline Orchestrator initialized - CI/CD pipeline automation engine")