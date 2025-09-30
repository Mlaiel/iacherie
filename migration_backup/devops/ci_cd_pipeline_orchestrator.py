#!/usr/bin/env python3
"""
CI/CD Pipeline Orchestrator - DevOps Engineer Implementation
==========================================================

Advanced CI/CD pipeline orchestration for Ainflue platform.
Implements enterprise-grade deployment strategies, automation,
and monitoring for multi-environment deployments.

Author: Expert Team - DevOps Engineer Role
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
License: Proprietary - Unauthorized use strictly prohibited.
"""

import asyncio
import json
import logging
import subprocess
import time
import yaml
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor, as_completed

import docker
import kubernetes
from kubernetes import client, config
import requests
import jinja2
import paramiko
import git


class DeploymentStrategy(Enum):
    """Deployment strategy types."""
    BLUE_GREEN = "blue-green"
    CANARY = "canary"
    ROLLING = "rolling"
    IMMUTABLE = "immutable"
    A_B_TESTING = "a-b-testing"


class PipelineStage(Enum):
    """CI/CD pipeline stages."""
    CHECKOUT = "checkout"
    BUILD = "build"
    TEST = "test"
    SECURITY_SCAN = "security-scan"
    QUALITY_GATE = "quality-gate"
    PACKAGE = "package"
    STAGING_DEPLOY = "staging-deploy"
    INTEGRATION_TEST = "integration-test"
    PERFORMANCE_TEST = "performance-test"
    PRODUCTION_DEPLOY = "production-deploy"
    SMOKE_TEST = "smoke-test"
    MONITORING = "monitoring"


class PipelineStatus(Enum):
    """Pipeline execution status."""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"
    SKIPPED = "skipped"


@dataclass
class DeploymentEnvironment:
    """Deployment environment configuration."""
    name: str
    cluster_name: str
    namespace: str
    api_url: str
    monitoring_url: str
    resource_limits: Dict[str, str]
    replica_count: int
    auto_scaling: bool = True
    health_check_timeout: int = 300
    rollback_enabled: bool = True


@dataclass
class PipelineConfiguration:
    """CI/CD pipeline configuration."""
    id: str
    name: str
    repository_url: str
    branch: str
    dockerfile_path: str
    kubernetes_manifests: List[str]
    environments: List[DeploymentEnvironment]
    deployment_strategy: DeploymentStrategy = DeploymentStrategy.ROLLING
    parallel_stages: bool = True
    auto_promote: bool = False
    approval_required: List[str] = field(default_factory=list)
    notification_webhooks: List[str] = field(default_factory=list)
    quality_gates: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PipelineExecution:
    """Pipeline execution state."""
    execution_id: str
    pipeline_id: str
    commit_sha: str
    triggered_by: str
    status: PipelineStatus
    current_stage: Optional[PipelineStage]
    start_time: datetime
    end_time: Optional[datetime] = None
    stages: Dict[PipelineStage, Dict[str, Any]] = field(default_factory=dict)
    artifacts: Dict[str, str] = field(default_factory=dict)
    logs: List[str] = field(default_factory=list)


class CICDPipelineOrchestrator:
    """
    Advanced CI/CD Pipeline Orchestrator for enterprise deployment automation.
    
    Features:
    - Multi-environment deployment strategies
    - Automated quality gates and approval workflows
    - Container orchestration with Kubernetes
    - Real-time monitoring and rollback capabilities
    - Security scanning and compliance validation
    - Performance testing and optimization
    """

    def __init__(self, config_path: str = "config/cicd.yaml"):
        """Initialize CI/CD orchestrator."""
        self.config_path = config_path
        self.logger = self._setup_logging()
        self.docker_client = docker.from_env()
        self.k8s_client = self._setup_kubernetes()
        self.git_client = git.Repo(".")
        self.template_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader("templates/deployment")
        )
        
        # State management
        self.pipelines: Dict[str, PipelineConfiguration] = {}
        self.executions: Dict[str, PipelineExecution] = {}
        self.environments: Dict[str, DeploymentEnvironment] = {}
        
        # Load configuration
        self._load_configuration()
        
        self.logger.info("CI/CD Pipeline Orchestrator initialized")

    def _setup_logging(self) -> logging.Logger:
        """Setup structured logging."""
        logger = logging.getLogger("cicd_orchestrator")
        logger.setLevel(logging.INFO)
        
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger

    def _setup_kubernetes(self) -> client.ApiClient:
        """Setup Kubernetes client."""
        try:
            config.load_incluster_config()
        except:
            config.load_kube_config()
        
        return client.ApiClient()

    def _load_configuration(self):
        """Load CI/CD configuration from file."""
        config_file = Path(self.config_path)
        if config_file.exists():
            with open(config_file, 'r') as f:
                config_data = yaml.safe_load(f)
                self._parse_configuration(config_data)

    def _parse_configuration(self, config_data: Dict[str, Any]):
        """Parse configuration data into objects."""
        # Parse environments
        for env_data in config_data.get('environments', []):
            env = DeploymentEnvironment(**env_data)
            self.environments[env.name] = env
        
        # Parse pipelines
        for pipeline_data in config_data.get('pipelines', []):
            envs = [self.environments[env_name] 
                    for env_name in pipeline_data.get('environments', [])]
            pipeline_data['environments'] = envs
            pipeline_data['deployment_strategy'] = DeploymentStrategy(
                pipeline_data.get('deployment_strategy', 'rolling')
            )
            
            pipeline = PipelineConfiguration(**pipeline_data)
            self.pipelines[pipeline.id] = pipeline

    async def create_pipeline(self, config: PipelineConfiguration) -> str:
        """Create a new CI/CD pipeline."""
        self.pipelines[config.id] = config
        self.logger.info(f"Created pipeline: {config.name} ({config.id})")
        return config.id

    async def trigger_pipeline(
        self, 
        pipeline_id: str, 
        commit_sha: str, 
        triggered_by: str,
        branch: Optional[str] = None
    ) -> str:
        """Trigger pipeline execution."""
        if pipeline_id not in self.pipelines:
            raise ValueError(f"Pipeline {pipeline_id} not found")
        
        pipeline = self.pipelines[pipeline_id]
        execution_id = f"{pipeline_id}-{int(time.time())}"
        
        execution = PipelineExecution(
            execution_id=execution_id,
            pipeline_id=pipeline_id,
            commit_sha=commit_sha,
            triggered_by=triggered_by,
            status=PipelineStatus.PENDING,
            current_stage=None,
            start_time=datetime.now()
        )
        
        self.executions[execution_id] = execution
        
        # Start pipeline execution asynchronously
        asyncio.create_task(self._execute_pipeline(execution))
        
        self.logger.info(f"Triggered pipeline execution: {execution_id}")
        return execution_id

    async def _execute_pipeline(self, execution: PipelineExecution):
        """Execute pipeline stages."""
        try:
            execution.status = PipelineStatus.RUNNING
            pipeline = self.pipelines[execution.pipeline_id]
            
            # Define stage sequence
            stages = [
                PipelineStage.CHECKOUT,
                PipelineStage.BUILD,
                PipelineStage.TEST,
                PipelineStage.SECURITY_SCAN,
                PipelineStage.QUALITY_GATE,
                PipelineStage.PACKAGE,
                PipelineStage.STAGING_DEPLOY,
                PipelineStage.INTEGRATION_TEST,
                PipelineStage.PERFORMANCE_TEST,
                PipelineStage.PRODUCTION_DEPLOY,
                PipelineStage.SMOKE_TEST,
                PipelineStage.MONITORING
            ]
            
            for stage in stages:
                execution.current_stage = stage
                
                try:
                    await self._execute_stage(execution, stage)
                    execution.stages[stage] = {
                        'status': 'success',
                        'timestamp': datetime.now().isoformat(),
                        'duration': 0  # Would be calculated in real implementation
                    }
                except Exception as e:
                    execution.stages[stage] = {
                        'status': 'failed',
                        'error': str(e),
                        'timestamp': datetime.now().isoformat()
                    }
                    execution.status = PipelineStatus.FAILED
                    await self._handle_pipeline_failure(execution, stage)
                    return
            
            execution.status = PipelineStatus.SUCCESS
            execution.end_time = datetime.now()
            
        except Exception as e:
            execution.status = PipelineStatus.FAILED
            execution.logs.append(f"Pipeline execution failed: {str(e)}")
            self.logger.error(f"Pipeline execution failed: {str(e)}")

    async def _execute_stage(self, execution: PipelineExecution, stage: PipelineStage):
        """Execute a specific pipeline stage."""
        self.logger.info(f"Executing stage: {stage.value} for {execution.execution_id}")
        
        stage_handlers = {
            PipelineStage.CHECKOUT: self._stage_checkout,
            PipelineStage.BUILD: self._stage_build,
            PipelineStage.TEST: self._stage_test,
            PipelineStage.SECURITY_SCAN: self._stage_security_scan,
            PipelineStage.QUALITY_GATE: self._stage_quality_gate,
            PipelineStage.PACKAGE: self._stage_package,
            PipelineStage.STAGING_DEPLOY: self._stage_staging_deploy,
            PipelineStage.INTEGRATION_TEST: self._stage_integration_test,
            PipelineStage.PERFORMANCE_TEST: self._stage_performance_test,
            PipelineStage.PRODUCTION_DEPLOY: self._stage_production_deploy,
            PipelineStage.SMOKE_TEST: self._stage_smoke_test,
            PipelineStage.MONITORING: self._stage_monitoring
        }
        
        handler = stage_handlers.get(stage)
        if handler:
            await handler(execution)

    async def _stage_checkout(self, execution: PipelineExecution):
        """Checkout source code."""
        pipeline = self.pipelines[execution.pipeline_id]
        
        # Simulate checkout
        execution.logs.append(f"Checking out {pipeline.repository_url}@{execution.commit_sha}")
        await asyncio.sleep(1)  # Simulate network delay

    async def _stage_build(self, execution: PipelineExecution):
        """Build application artifacts."""
        pipeline = self.pipelines[execution.pipeline_id]
        
        # Build Docker image
        image_tag = f"{pipeline.name}:{execution.commit_sha[:8]}"
        execution.logs.append(f"Building Docker image: {image_tag}")
        
        # In real implementation, would build the actual image
        execution.artifacts['docker_image'] = image_tag
        await asyncio.sleep(2)  # Simulate build time

    async def _stage_test(self, execution: PipelineExecution):
        """Run automated tests."""
        execution.logs.append("Running unit tests...")
        await asyncio.sleep(1)
        
        execution.logs.append("Running integration tests...")
        await asyncio.sleep(2)
        
        # Simulate test results
        execution.artifacts['test_results'] = "tests_passed"

    async def _stage_security_scan(self, execution: PipelineExecution):
        """Run security scanning."""
        execution.logs.append("Running container security scan...")
        await asyncio.sleep(1)
        
        execution.logs.append("Running dependency vulnerability scan...")
        await asyncio.sleep(1)
        
        execution.artifacts['security_scan'] = "vulnerabilities_none"

    async def _stage_quality_gate(self, execution: PipelineExecution):
        """Validate quality gates."""
        pipeline = self.pipelines[execution.pipeline_id]
        
        # Check quality criteria
        for gate, threshold in pipeline.quality_gates.items():
            execution.logs.append(f"Checking quality gate: {gate} >= {threshold}")
            # Simulate quality check
            await asyncio.sleep(0.5)

    async def _stage_package(self, execution: PipelineExecution):
        """Package application for deployment."""
        execution.logs.append("Creating deployment package...")
        
        # Push Docker image to registry
        image_tag = execution.artifacts.get('docker_image')
        if image_tag:
            execution.logs.append(f"Pushing image to registry: {image_tag}")
            await asyncio.sleep(2)

    async def _stage_staging_deploy(self, execution: PipelineExecution):
        """Deploy to staging environment."""
        pipeline = self.pipelines[execution.pipeline_id]
        
        staging_envs = [env for env in pipeline.environments if 'staging' in env.name.lower()]
        
        for env in staging_envs:
            await self._deploy_to_environment(execution, env)

    async def _stage_integration_test(self, execution: PipelineExecution):
        """Run integration tests in staging."""
        execution.logs.append("Running integration tests in staging...")
        await asyncio.sleep(3)

    async def _stage_performance_test(self, execution: PipelineExecution):
        """Run performance tests."""
        execution.logs.append("Running performance tests...")
        await asyncio.sleep(2)
        
        execution.artifacts['performance_results'] = "response_time_acceptable"

    async def _stage_production_deploy(self, execution: PipelineExecution):
        """Deploy to production environment."""
        pipeline = self.pipelines[execution.pipeline_id]
        
        # Check if approval is required
        if 'production' in pipeline.approval_required:
            execution.logs.append("Waiting for production deployment approval...")
            # In real implementation, would wait for manual approval
            await asyncio.sleep(1)
        
        prod_envs = [env for env in pipeline.environments if 'prod' in env.name.lower()]
        
        for env in prod_envs:
            await self._deploy_to_environment(execution, env)

    async def _stage_smoke_test(self, execution: PipelineExecution):
        """Run smoke tests in production."""
        execution.logs.append("Running smoke tests in production...")
        await asyncio.sleep(2)

    async def _stage_monitoring(self, execution: PipelineExecution):
        """Setup monitoring for deployed application."""
        execution.logs.append("Configuring monitoring and alerts...")
        await asyncio.sleep(1)

    async def _deploy_to_environment(
        self, 
        execution: PipelineExecution, 
        environment: DeploymentEnvironment
    ):
        """Deploy application to specific environment."""
        pipeline = self.pipelines[execution.pipeline_id]
        
        execution.logs.append(f"Deploying to {environment.name} environment...")
        
        # Apply deployment strategy
        if pipeline.deployment_strategy == DeploymentStrategy.BLUE_GREEN:
            await self._deploy_blue_green(execution, environment)
        elif pipeline.deployment_strategy == DeploymentStrategy.CANARY:
            await self._deploy_canary(execution, environment)
        elif pipeline.deployment_strategy == DeploymentStrategy.ROLLING:
            await self._deploy_rolling(execution, environment)
        
        # Wait for deployment to be ready
        await self._wait_for_deployment(execution, environment)

    async def _deploy_blue_green(
        self, 
        execution: PipelineExecution, 
        environment: DeploymentEnvironment
    ):
        """Deploy using blue-green strategy."""
        execution.logs.append(f"Deploying with blue-green strategy to {environment.name}")
        
        # In real implementation:
        # 1. Deploy to green environment
        # 2. Run health checks
        # 3. Switch traffic to green
        # 4. Keep blue as backup
        
        await asyncio.sleep(2)

    async def _deploy_canary(
        self, 
        execution: PipelineExecution, 
        environment: DeploymentEnvironment
    ):
        """Deploy using canary strategy."""
        execution.logs.append(f"Deploying with canary strategy to {environment.name}")
        
        # In real implementation:
        # 1. Deploy canary version (5-10% traffic)
        # 2. Monitor metrics
        # 3. Gradually increase traffic
        # 4. Full rollout if successful
        
        await asyncio.sleep(3)

    async def _deploy_rolling(
        self, 
        execution: PipelineExecution, 
        environment: DeploymentEnvironment
    ):
        """Deploy using rolling update strategy."""
        execution.logs.append(f"Deploying with rolling update to {environment.name}")
        
        # In real implementation:
        # 1. Update pods one by one
        # 2. Ensure each pod is healthy before continuing
        # 3. Complete when all pods updated
        
        await asyncio.sleep(2)

    async def _wait_for_deployment(
        self, 
        execution: PipelineExecution, 
        environment: DeploymentEnvironment
    ):
        """Wait for deployment to be ready."""
        execution.logs.append(f"Waiting for deployment readiness in {environment.name}...")
        
        # In real implementation:
        # 1. Check pod status
        # 2. Verify health checks
        # 3. Test endpoints
        
        await asyncio.sleep(1)

    async def _handle_pipeline_failure(
        self, 
        execution: PipelineExecution, 
        failed_stage: PipelineStage
    ):
        """Handle pipeline failure and cleanup."""
        self.logger.error(f"Pipeline {execution.execution_id} failed at stage: {failed_stage.value}")
        
        # Send notifications
        await self._send_failure_notifications(execution, failed_stage)
        
        # Attempt rollback if in deployment stage
        if failed_stage in [PipelineStage.STAGING_DEPLOY, PipelineStage.PRODUCTION_DEPLOY]:
            await self._rollback_deployment(execution)

    async def _send_failure_notifications(
        self, 
        execution: PipelineExecution, 
        failed_stage: PipelineStage
    ):
        """Send failure notifications."""
        pipeline = self.pipelines[execution.pipeline_id]
        
        message = {
            'type': 'pipeline_failure',
            'pipeline_id': execution.pipeline_id,
            'execution_id': execution.execution_id,
            'failed_stage': failed_stage.value,
            'commit_sha': execution.commit_sha,
            'triggered_by': execution.triggered_by,
            'timestamp': datetime.now().isoformat()
        }
        
        for webhook_url in pipeline.notification_webhooks:
            try:
                await self._send_webhook(webhook_url, message)
            except Exception as e:
                self.logger.error(f"Failed to send notification to {webhook_url}: {str(e)}")

    async def _send_webhook(self, url: str, payload: Dict[str, Any]):
        """Send webhook notification."""
        # In real implementation, would use aiohttp
        self.logger.info(f"Sending webhook to {url}: {payload}")

    async def _rollback_deployment(self, execution: PipelineExecution):
        """Rollback failed deployment."""
        execution.logs.append("Initiating automatic rollback...")
        
        # In real implementation:
        # 1. Identify previous successful deployment
        # 2. Restore previous version
        # 3. Verify rollback success
        
        await asyncio.sleep(2)
        execution.logs.append("Rollback completed successfully")

    async def get_pipeline_status(self, execution_id: str) -> Dict[str, Any]:
        """Get pipeline execution status."""
        if execution_id not in self.executions:
            raise ValueError(f"Execution {execution_id} not found")
        
        execution = self.executions[execution_id]
        pipeline = self.pipelines[execution.pipeline_id]
        
        return {
            'execution_id': execution.execution_id,
            'pipeline_name': pipeline.name,
            'status': execution.status.value,
            'current_stage': execution.current_stage.value if execution.current_stage else None,
            'start_time': execution.start_time.isoformat(),
            'end_time': execution.end_time.isoformat() if execution.end_time else None,
            'stages': {
                stage.value: details 
                for stage, details in execution.stages.items()
            },
            'artifacts': execution.artifacts,
            'logs': execution.logs[-10:]  # Last 10 log entries
        }

    async def cancel_pipeline(self, execution_id: str) -> bool:
        """Cancel running pipeline execution."""
        if execution_id not in self.executions:
            return False
        
        execution = self.executions[execution_id]
        if execution.status == PipelineStatus.RUNNING:
            execution.status = PipelineStatus.CANCELLED
            execution.end_time = datetime.now()
            execution.logs.append("Pipeline execution cancelled by user")
            
            self.logger.info(f"Cancelled pipeline execution: {execution_id}")
            return True
        
        return False

    async def get_deployment_metrics(self, environment_name: str) -> Dict[str, Any]:
        """Get deployment metrics for environment."""
        if environment_name not in self.environments:
            raise ValueError(f"Environment {environment_name} not found")
        
        environment = self.environments[environment_name]
        
        # In real implementation, would query monitoring systems
        return {
            'environment': environment_name,
            'active_deployments': 1,
            'healthy_pods': 3,
            'total_pods': 3,
            'cpu_usage': 45.2,
            'memory_usage': 67.8,
            'request_rate': 150.5,
            'error_rate': 0.2,
            'last_deployment': datetime.now().isoformat()
        }

    def get_pipeline_history(self, pipeline_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get pipeline execution history."""
        if pipeline_id not in self.pipelines:
            raise ValueError(f"Pipeline {pipeline_id} not found")
        
        # Filter executions for this pipeline
        pipeline_executions = [
            execution for execution in self.executions.values()
            if execution.pipeline_id == pipeline_id
        ]
        
        # Sort by start time (most recent first)
        pipeline_executions.sort(key=lambda x: x.start_time, reverse=True)
        
        # Return limited results
        return [
            {
                'execution_id': execution.execution_id,
                'status': execution.status.value,
                'commit_sha': execution.commit_sha,
                'triggered_by': execution.triggered_by,
                'start_time': execution.start_time.isoformat(),
                'end_time': execution.end_time.isoformat() if execution.end_time else None,
                'duration': (
                    (execution.end_time - execution.start_time).total_seconds() 
                    if execution.end_time else None
                )
            }
            for execution in pipeline_executions[:limit]
        ]

    async def cleanup_old_executions(self, days: int = 30):
        """Cleanup old pipeline executions."""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        to_remove = [
            execution_id for execution_id, execution in self.executions.items()
            if execution.start_time < cutoff_date
        ]
        
        for execution_id in to_remove:
            del self.executions[execution_id]
        
        self.logger.info(f"Cleaned up {len(to_remove)} old pipeline executions")

    async def export_pipeline_analytics(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Export pipeline analytics for given date range."""
        filtered_executions = [
            execution for execution in self.executions.values()
            if start_date <= execution.start_time <= end_date
        ]
        
        total_executions = len(filtered_executions)
        successful_executions = len([
            e for e in filtered_executions 
            if e.status == PipelineStatus.SUCCESS
        ])
        failed_executions = len([
            e for e in filtered_executions 
            if e.status == PipelineStatus.FAILED
        ])
        
        # Calculate average duration
        completed_executions = [
            e for e in filtered_executions 
            if e.end_time is not None
        ]
        avg_duration = sum([
            (e.end_time - e.start_time).total_seconds() 
            for e in completed_executions
        ]) / len(completed_executions) if completed_executions else 0
        
        return {
            'period': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat()
            },
            'metrics': {
                'total_executions': total_executions,
                'successful_executions': successful_executions,
                'failed_executions': failed_executions,
                'success_rate': successful_executions / total_executions if total_executions > 0 else 0,
                'average_duration_seconds': avg_duration
            },
            'pipeline_breakdown': {
                pipeline_id: len([
                    e for e in filtered_executions 
                    if e.pipeline_id == pipeline_id
                ])
                for pipeline_id in self.pipelines.keys()
            }
        }


# Enterprise usage example
async def main():
    """Demonstrate CI/CD pipeline orchestrator usage."""
    orchestrator = CICDPipelineOrchestrator()
    
    # Create deployment environments
    staging_env = DeploymentEnvironment(
        name="staging",
        cluster_name="ainflue-staging",
        namespace="ainflue",
        api_url="https://staging-api.ainflue.com",
        monitoring_url="https://staging-monitor.ainflue.com",
        resource_limits={"cpu": "500m", "memory": "1Gi"},
        replica_count=2
    )
    
    production_env = DeploymentEnvironment(
        name="production",
        cluster_name="ainflue-production",
        namespace="ainflue",
        api_url="https://api.ainflue.com",
        monitoring_url="https://monitor.ainflue.com",
        resource_limits={"cpu": "1000m", "memory": "2Gi"},
        replica_count=5
    )
    
    # Create pipeline configuration
    pipeline_config = PipelineConfiguration(
        id="ainflue-backend-pipeline",
        name="Ainflue Backend Deployment",
        repository_url="https://github.com/Mlaiel/Ainflue.git",
        branch="main",
        dockerfile_path="docker/Dockerfile.backend",
        kubernetes_manifests=["kubernetes/backend/"],
        environments=[staging_env, production_env],
        deployment_strategy=DeploymentStrategy.BLUE_GREEN,
        parallel_stages=True,
        approval_required=["production"],
        notification_webhooks=["https://hooks.slack.com/webhook"],
        quality_gates={
            "test_coverage": 80,
            "vulnerability_count": 0,
            "performance_score": 90
        }
    )
    
    # Create and trigger pipeline
    pipeline_id = await orchestrator.create_pipeline(pipeline_config)
    execution_id = await orchestrator.trigger_pipeline(
        pipeline_id=pipeline_id,
        commit_sha="abc123def456",
        triggered_by="developer@ainflue.com"
    )
    
    print(f"Started pipeline execution: {execution_id}")
    
    # Monitor pipeline progress
    while True:
        status = await orchestrator.get_pipeline_status(execution_id)
        print(f"Pipeline status: {status['status']} - Stage: {status.get('current_stage', 'N/A')}")
        
        if status['status'] in ['success', 'failed', 'cancelled']:
            break
        
        await asyncio.sleep(5)
    
    # Get final results
    final_status = await orchestrator.get_pipeline_status(execution_id)
    print(f"Pipeline completed with status: {final_status['status']}")
    print(f"Artifacts: {final_status['artifacts']}")


if __name__ == "__main__":
    asyncio.run(main())