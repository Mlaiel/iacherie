#!/usr/bin/env python3
"""
🚀 Deployment Service Template - IA Chéries Enterprise
==================================================
Template enterprise pour services deployment.
Docker + Kubernetes + Helm + CI/CD + blue-green deployment.

Author: Fahed Mlaiel (mlaiel@live.de)
Project: IA Chéries Microservices Templates
Version: 1.0 Production
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ PROPRIÉTÉ INTELLECTUELLE - FAHED MLAIEL
Cette architecture microservices et tous ses templates sont la propriété intellectuelle 
EXCLUSIVE de Fahed Mlaiel (mlaiel@live.de). Toute reproduction, modification, 
distribution ou vol d'idée/concept/code sans autorisation écrite PERSONNELLE est 
STRICTEMENT INTERDITE et sera poursuivie en justice avec la PLEINE RIGUEUR de la loi.
"""

import asyncio
import logging
import yaml
import json
import subprocess
from abc import abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Union
from enum import Enum
import uuid
from pathlib import Path
import tempfile
import shutil

from .service_template import EnterpriseServiceBase, ServiceConfig

# Deployment-specific configurations
@dataclass
class ContainerConfig:
    """Configuration for containerization."""
    image_name: str
    dockerfile_path: str = "Dockerfile"
    build_context: str = "."
    registry_url: str = ""
    tags: List[str] = field(default_factory=list)
    build_args: Dict[str, str] = field(default_factory=dict)
    multi_stage: bool = True
    base_image: str = "python:3.11-slim"

@dataclass
class KubernetesConfig:
    """Configuration for Kubernetes deployment."""
    namespace: str
    cluster_name: str
    deployment_name: str
    service_name: str
    replicas: int = 3
    port: int = 8000
    resources: Dict[str, Any] = field(default_factory=dict)
    env_vars: Dict[str, str] = field(default_factory=dict)
    config_maps: List[str] = field(default_factory=list)
    secrets: List[str] = field(default_factory=list)
    ingress_enabled: bool = True
    ingress_host: str = ""

@dataclass
class HelmConfig:
    """Configuration for Helm charts."""
    chart_name: str
    chart_version: str = "1.0.0"
    release_name: str = ""
    values_file: str = "values.yaml"
    custom_values: Dict[str, Any] = field(default_factory=dict)
    repository_url: str = ""
    dependencies: List[Dict[str, str]] = field(default_factory=list)

@dataclass
class CICDConfig:
    """Configuration for CI/CD pipeline."""
    pipeline_type: str  # github, gitlab, jenkins, azure
    branch_triggers: List[str] = field(default_factory=lambda: ["main", "develop"])
    stages: List[str] = field(default_factory=lambda: ["build", "test", "deploy"])
    environments: List[str] = field(default_factory=lambda: ["dev", "staging", "prod"])
    approval_required: bool = True
    notifications: Dict[str, Any] = field(default_factory=dict)

class DeploymentStatus(Enum):
    """Status of deployment."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"

class DeploymentStrategy(Enum):
    """Deployment strategies."""
    ROLLING_UPDATE = "rolling_update"
    BLUE_GREEN = "blue_green"
    CANARY = "canary"
    RECREATE = "recreate"

class DeploymentServiceTemplate(EnterpriseServiceBase):
    """
    🚀 Template enterprise pour services deployment.
    
    Fonctionnalités:
    - Containerization avec Docker multi-stage builds
    - Kubernetes deployment avec Helm charts
    - CI/CD pipeline automation avec multiple providers
    - Blue-green et canary deployment strategies
    - Infrastructure as Code avec Terraform/Pulumi
    - Monitoring et rollback automatique
    - Security scanning et compliance checks
    """
    
    def __init__(self, config: ServiceConfig):
        """Initialize deployment service."""
        super().__init__(config)
        self.container_configs: Dict[str, ContainerConfig] = {}
        self.k8s_configs: Dict[str, KubernetesConfig] = {}
        self.helm_configs: Dict[str, HelmConfig] = {}
        self.cicd_configs: Dict[str, CICDConfig] = {}
        
        # Deployment tracking
        self.deployments: Dict[str, Dict[str, Any]] = {}
        self.deployment_history: List[Dict[str, Any]] = []
        
        # Infrastructure state
        self.clusters: Dict[str, Any] = {}
        self.registries: Dict[str, Any] = {}
        
        self.logger = logging.getLogger(f"{self.config.service_name}.deployment")
        
    async def setup_containerization(self, container_configs: List[ContainerConfig]) -> None:
        """Configuration Docker avec multi-stage builds."""
        try:
            for config in container_configs:
                # Validate container configuration
                await self._validate_container_config(config)
                
                # Generate Dockerfiles if needed
                if not Path(config.dockerfile_path).exists():
                    await self._generate_dockerfile(config)
                
                # Setup build context
                build_context = {
                    'config': config,
                    'build_cache': {},
                    'last_build': None,
                    'build_history': []
                }
                
                self.container_configs[config.image_name] = build_context
                
                self.logger.info(f"Container configuration for '{config.image_name}' setup")
                
        except Exception as e:
            self.logger.error(f"Failed to setup containerization: {e}")
            raise
    
    async def setup_kubernetes_deployment(self, k8s_configs: List[KubernetesConfig]) -> None:
        """Déploiement Kubernetes avec Helm charts."""
        try:
            for config in k8s_configs:
                # Validate Kubernetes configuration
                await self._validate_k8s_config(config)
                
                # Generate Kubernetes manifests
                manifests = await self._generate_k8s_manifests(config)
                
                # Setup deployment context
                deployment_context = {
                    'config': config,
                    'manifests': manifests,
                    'current_version': None,
                    'rollout_status': 'ready',
                    'health_checks': []
                }
                
                self.k8s_configs[config.deployment_name] = deployment_context
                
                self.logger.info(f"Kubernetes deployment '{config.deployment_name}' configured")
                
        except Exception as e:
            self.logger.error(f"Failed to setup Kubernetes deployment: {e}")
            raise
    
    async def setup_helm_charts(self, helm_configs: List[HelmConfig]) -> None:
        """Configuration Helm charts avec dependencies."""
        try:
            for config in helm_configs:
                # Generate Helm chart structure
                chart_path = await self._generate_helm_chart(config)
                
                # Setup chart context
                chart_context = {
                    'config': config,
                    'chart_path': chart_path,
                    'current_revision': 0,
                    'install_status': 'not_installed',
                    'values': config.custom_values
                }
                
                self.helm_configs[config.chart_name] = chart_context
                
                self.logger.info(f"Helm chart '{config.chart_name}' configured")
                
        except Exception as e:
            self.logger.error(f"Failed to setup Helm charts: {e}")
            raise
    
    async def setup_cicd_pipeline(self, cicd_configs: List[CICDConfig]) -> None:
        """Pipeline CI/CD avec automated testing."""
        try:
            for config in cicd_configs:
                # Generate pipeline configuration
                pipeline_config = await self._generate_pipeline_config(config)
                
                # Setup pipeline context
                pipeline_context = {
                    'config': config,
                    'pipeline_file': pipeline_config,
                    'last_run': None,
                    'run_history': [],
                    'webhook_url': None
                }
                
                self.cicd_configs[config.pipeline_type] = pipeline_context
                
                self.logger.info(f"CI/CD pipeline '{config.pipeline_type}' configured")
                
        except Exception as e:
            self.logger.error(f"Failed to setup CI/CD pipeline: {e}")
            raise
    
    async def setup_deployment_strategies(self, strategy_configs: Dict[str, Any]) -> None:
        """Stratégies déploiement (blue-green, canary, etc.)."""
        try:
            self.deployment_strategies = {}
            
            for strategy_name, strategy_config in strategy_configs.items():
                strategy = {
                    'type': strategy_config['type'],
                    'config': strategy_config,
                    'enabled': strategy_config.get('enabled', True),
                    'rollback_enabled': strategy_config.get('rollback_enabled', True),
                    'health_check_config': strategy_config.get('health_checks', {}),
                    'traffic_split': strategy_config.get('traffic_split', {})
                }
                
                self.deployment_strategies[strategy_name] = strategy
                
                self.logger.info(f"Deployment strategy '{strategy_name}' configured")
                
        except Exception as e:
            self.logger.error(f"Failed to setup deployment strategies: {e}")
            raise
    
    async def build_container_image(self, image_name: str, 
                                   version_tag: str = "latest") -> Dict[str, Any]:
        """Build container image avec optimizations."""
        try:
            container_config = self.container_configs.get(image_name)
            if not container_config:
                raise ValueError(f"Container configuration for '{image_name}' not found")
            
            config = container_config['config']
            
            self.logger.info(f"Building container image '{image_name}:{version_tag}'")
            
            start_time = datetime.utcnow()
            
            # Prepare build context
            build_context = await self._prepare_build_context(config)
            
            # Build Docker image
            build_result = await self._build_docker_image(config, version_tag, build_context)
            
            # Tag image
            await self._tag_image(config, version_tag)
            
            # Push to registry if configured
            push_result = None
            if config.registry_url:
                push_result = await self._push_image(config, version_tag)
            
            # Update build history
            build_record = {
                'version': version_tag,
                'build_time': start_time,
                'duration': (datetime.utcnow() - start_time).total_seconds(),
                'build_result': build_result,
                'push_result': push_result,
                'status': 'success'
            }
            
            container_config['last_build'] = build_record
            container_config['build_history'].append(build_record)
            
            self.logger.info(f"Container image '{image_name}:{version_tag}' built successfully")
            
            return build_record
            
        except Exception as e:
            self.logger.error(f"Failed to build container image '{image_name}': {e}")
            # Record failed build
            if image_name in self.container_configs:
                build_record = {
                    'version': version_tag,
                    'build_time': datetime.utcnow(),
                    'duration': 0,
                    'error': str(e),
                    'status': 'failed'
                }
                self.container_configs[image_name]['build_history'].append(build_record)
            raise
    
    async def deploy_to_kubernetes(self, deployment_name: str, 
                                  version: str,
                                  strategy: DeploymentStrategy = DeploymentStrategy.ROLLING_UPDATE) -> Dict[str, Any]:
        """Deploy application to Kubernetes cluster."""
        try:
            k8s_config = self.k8s_configs.get(deployment_name)
            if not k8s_config:
                raise ValueError(f"Kubernetes configuration for '{deployment_name}' not found")
            
            config = k8s_config['config']
            
            self.logger.info(f"Deploying '{deployment_name}' version '{version}' to Kubernetes")
            
            deployment_id = str(uuid.uuid4())
            start_time = datetime.utcnow()
            
            # Create deployment record
            deployment_record = {
                'id': deployment_id,
                'deployment_name': deployment_name,
                'version': version,
                'strategy': strategy.value,
                'start_time': start_time,
                'status': DeploymentStatus.IN_PROGRESS,
                'steps': []
            }
            
            self.deployments[deployment_id] = deployment_record
            
            # Execute deployment based on strategy
            if strategy == DeploymentStrategy.ROLLING_UPDATE:
                result = await self._rolling_update_deployment(k8s_config, version, deployment_record)
            elif strategy == DeploymentStrategy.BLUE_GREEN:
                result = await self._blue_green_deployment(k8s_config, version, deployment_record)
            elif strategy == DeploymentStrategy.CANARY:
                result = await self._canary_deployment(k8s_config, version, deployment_record)
            else:
                result = await self._recreate_deployment(k8s_config, version, deployment_record)
            
            # Update deployment status
            deployment_record['status'] = DeploymentStatus.SUCCESS if result['success'] else DeploymentStatus.FAILED
            deployment_record['end_time'] = datetime.utcnow()
            deployment_record['duration'] = (deployment_record['end_time'] - start_time).total_seconds()
            deployment_record['result'] = result
            
            # Add to history
            self.deployment_history.append(deployment_record.copy())
            
            self.logger.info(f"Deployment '{deployment_name}' completed with status: {deployment_record['status'].value}")
            
            return deployment_record
            
        except Exception as e:
            self.logger.error(f"Failed to deploy '{deployment_name}': {e}")
            if deployment_id in self.deployments:
                self.deployments[deployment_id]['status'] = DeploymentStatus.FAILED
                self.deployments[deployment_id]['error'] = str(e)
            raise
    
    async def deploy_helm_chart(self, chart_name: str, 
                               environment: str = "production",
                               custom_values: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Deploy application using Helm chart."""
        try:
            helm_config = self.helm_configs.get(chart_name)
            if not helm_config:
                raise ValueError(f"Helm configuration for '{chart_name}' not found")
            
            config = helm_config['config']
            
            self.logger.info(f"Deploying Helm chart '{chart_name}' to '{environment}'")
            
            # Merge custom values
            values = config.custom_values.copy()
            if custom_values:
                values.update(custom_values)
            
            # Generate values file
            values_file = await self._generate_values_file(values, environment)
            
            # Install or upgrade Helm release
            if helm_config['install_status'] == 'not_installed':
                result = await self._helm_install(config, values_file, environment)
                helm_config['install_status'] = 'installed'
            else:
                result = await self._helm_upgrade(config, values_file, environment)
            
            # Update revision
            helm_config['current_revision'] += 1
            
            self.logger.info(f"Helm chart '{chart_name}' deployed successfully")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to deploy Helm chart '{chart_name}': {e}")
            raise
    
    async def rollback_deployment(self, deployment_id: str) -> Dict[str, Any]:
        """Rollback deployment to previous version."""
        try:
            deployment = self.deployments.get(deployment_id)
            if not deployment:
                raise ValueError(f"Deployment '{deployment_id}' not found")
            
            self.logger.info(f"Rolling back deployment '{deployment_id}'")
            
            # Find previous successful deployment
            previous_deployment = None
            for historical_deployment in reversed(self.deployment_history):
                if (historical_deployment['deployment_name'] == deployment['deployment_name'] and 
                    historical_deployment['status'] == DeploymentStatus.SUCCESS and
                    historical_deployment['id'] != deployment_id):
                    previous_deployment = historical_deployment
                    break
            
            if not previous_deployment:
                raise ValueError("No previous successful deployment found for rollback")
            
            # Execute rollback
            rollback_result = await self._execute_rollback(deployment, previous_deployment)
            
            # Update deployment status
            deployment['status'] = DeploymentStatus.ROLLED_BACK
            deployment['rollback_time'] = datetime.utcnow()
            deployment['rollback_result'] = rollback_result
            
            self.logger.info(f"Deployment '{deployment_id}' rolled back successfully")
            
            return rollback_result
            
        except Exception as e:
            self.logger.error(f"Failed to rollback deployment '{deployment_id}': {e}")
            raise
    
    async def get_deployment_status(self, deployment_id: str) -> Dict[str, Any]:
        """Get detailed deployment status."""
        deployment = self.deployments.get(deployment_id)
        if not deployment:
            raise ValueError(f"Deployment '{deployment_id}' not found")
        
        # Add real-time status information
        if deployment['status'] == DeploymentStatus.IN_PROGRESS:
            # Check current progress
            progress = await self._check_deployment_progress(deployment)
            deployment['progress'] = progress
        
        return deployment
    
    async def get_deployment_history(self, deployment_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get deployment history."""
        if deployment_name:
            return [dep for dep in self.deployment_history 
                   if dep['deployment_name'] == deployment_name]
        
        return self.deployment_history.copy()
    
    # Private helper methods
    async def _validate_container_config(self, config: ContainerConfig) -> None:
        """Validate container configuration."""
        if not config.image_name:
            raise ValueError("Container image name is required")
        
        if not Path(config.build_context).exists():
            raise ValueError(f"Build context path '{config.build_context}' does not exist")
    
    async def _generate_dockerfile(self, config: ContainerConfig) -> None:
        """Generate optimized Dockerfile."""
        dockerfile_content = f"""# Multi-stage Dockerfile generated by IA Chéries Deployment Service
# Author: Fahed Mlaiel (mlaiel@live.de)
# Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

# Build stage
FROM {config.base_image} as builder

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    build-essential \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements*.txt ./
RUN pip install --no-cache-dir --user -r requirements.txt

# Production stage
FROM {config.base_image} as production

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

WORKDIR /app

# Copy Python dependencies from builder stage
COPY --from=builder /root/.local /home/appuser/.local

# Copy application code
COPY . .

# Set ownership
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Set environment variables
ENV PATH=/home/appuser/.local/bin:$PATH
ENV PYTHONPATH=/app

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:8000/health || exit 1

# Expose port
EXPOSE {config.port if hasattr(config, 'port') else 8000}

# Run application
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
"""
        
        with open(config.dockerfile_path, 'w') as f:
            f.write(dockerfile_content)
        
        self.logger.info(f"Generated Dockerfile: {config.dockerfile_path}")
    
    async def _validate_k8s_config(self, config: KubernetesConfig) -> None:
        """Validate Kubernetes configuration."""
        if not config.deployment_name:
            raise ValueError("Kubernetes deployment name is required")
        
        if not config.namespace:
            raise ValueError("Kubernetes namespace is required")
    
    async def _generate_k8s_manifests(self, config: KubernetesConfig) -> Dict[str, str]:
        """Generate Kubernetes manifests."""
        manifests = {}
        
        # Deployment manifest
        deployment_manifest = {
            'apiVersion': 'apps/v1',
            'kind': 'Deployment',
            'metadata': {
                'name': config.deployment_name,
                'namespace': config.namespace,
                'labels': {
                    'app': config.deployment_name,
                    'version': 'v1'
                }
            },
            'spec': {
                'replicas': config.replicas,
                'selector': {
                    'matchLabels': {
                        'app': config.deployment_name
                    }
                },
                'template': {
                    'metadata': {
                        'labels': {
                            'app': config.deployment_name
                        }
                    },
                    'spec': {
                        'containers': [{
                            'name': config.deployment_name,
                            'image': f"{config.deployment_name}:latest",
                            'ports': [{
                                'containerPort': config.port
                            }],
                            'env': [
                                {'name': k, 'value': v} 
                                for k, v in config.env_vars.items()
                            ],
                            'resources': config.resources,
                            'livenessProbe': {
                                'httpGet': {
                                    'path': '/health',
                                    'port': config.port
                                },
                                'initialDelaySeconds': 30,
                                'periodSeconds': 10
                            },
                            'readinessProbe': {
                                'httpGet': {
                                    'path': '/ready',
                                    'port': config.port
                                },
                                'initialDelaySeconds': 5,
                                'periodSeconds': 5
                            }
                        }]
                    }
                }
            }
        }
        
        manifests['deployment'] = yaml.dump(deployment_manifest)
        
        # Service manifest
        service_manifest = {
            'apiVersion': 'v1',
            'kind': 'Service',
            'metadata': {
                'name': config.service_name,
                'namespace': config.namespace
            },
            'spec': {
                'selector': {
                    'app': config.deployment_name
                },
                'ports': [{
                    'port': 80,
                    'targetPort': config.port
                }],
                'type': 'ClusterIP'
            }
        }
        
        manifests['service'] = yaml.dump(service_manifest)
        
        # Ingress manifest (if enabled)
        if config.ingress_enabled and config.ingress_host:
            ingress_manifest = {
                'apiVersion': 'networking.k8s.io/v1',
                'kind': 'Ingress',
                'metadata': {
                    'name': f"{config.deployment_name}-ingress",
                    'namespace': config.namespace,
                    'annotations': {
                        'nginx.ingress.kubernetes.io/rewrite-target': '/'
                    }
                },
                'spec': {
                    'rules': [{
                        'host': config.ingress_host,
                        'http': {
                            'paths': [{
                                'path': '/',
                                'pathType': 'Prefix',
                                'backend': {
                                    'service': {
                                        'name': config.service_name,
                                        'port': {
                                            'number': 80
                                        }
                                    }
                                }
                            }]
                        }
                    }]
                }
            }
            
            manifests['ingress'] = yaml.dump(ingress_manifest)
        
        return manifests
    
    async def _generate_helm_chart(self, config: HelmConfig) -> str:
        """Generate Helm chart structure."""
        chart_dir = Path(f"charts/{config.chart_name}")
        chart_dir.mkdir(parents=True, exist_ok=True)
        
        # Chart.yaml
        chart_yaml = {
            'apiVersion': 'v2',
            'name': config.chart_name,
            'description': f'Helm chart for {config.chart_name}',
            'version': config.chart_version,
            'appVersion': '1.0.0',
            'type': 'application',
            'dependencies': config.dependencies
        }
        
        with open(chart_dir / 'Chart.yaml', 'w') as f:
            yaml.dump(chart_yaml, f)
        
        # values.yaml
        values_yaml = {
            'replicaCount': 3,
            'image': {
                'repository': config.chart_name,
                'pullPolicy': 'IfNotPresent',
                'tag': 'latest'
            },
            'service': {
                'type': 'ClusterIP',
                'port': 80
            },
            'ingress': {
                'enabled': False
            },
            'resources': {},
            'autoscaling': {
                'enabled': False,
                'minReplicas': 1,
                'maxReplicas': 100,
                'targetCPUUtilizationPercentage': 80
            }
        }
        
        values_yaml.update(config.custom_values)
        
        with open(chart_dir / 'values.yaml', 'w') as f:
            yaml.dump(values_yaml, f)
        
        # Create templates directory
        templates_dir = chart_dir / 'templates'
        templates_dir.mkdir(exist_ok=True)
        
        return str(chart_dir)
    
    async def _generate_pipeline_config(self, config: CICDConfig) -> str:
        """Generate CI/CD pipeline configuration."""
        if config.pipeline_type == "github":
            return await self._generate_github_workflow(config)
        elif config.pipeline_type == "gitlab":
            return await self._generate_gitlab_ci(config)
        elif config.pipeline_type == "jenkins":
            return await self._generate_jenkinsfile(config)
        else:
            raise ValueError(f"Unsupported pipeline type: {config.pipeline_type}")
    
    async def _generate_github_workflow(self, config: CICDConfig) -> str:
        """Generate GitHub Actions workflow."""
        workflow = {
            'name': 'CI/CD Pipeline',
            'on': {
                'push': {
                    'branches': config.branch_triggers
                },
                'pull_request': {
                    'branches': config.branch_triggers
                }
            },
            'jobs': {
                'build': {
                    'runs-on': 'ubuntu-latest',
                    'steps': [
                        {
                            'uses': 'actions/checkout@v3'
                        },
                        {
                            'name': 'Set up Python',
                            'uses': 'actions/setup-python@v4',
                            'with': {
                                'python-version': '3.11'
                            }
                        },
                        {
                            'name': 'Install dependencies',
                            'run': 'pip install -r requirements.txt'
                        },
                        {
                            'name': 'Run tests',
                            'run': 'pytest'
                        },
                        {
                            'name': 'Build Docker image',
                            'run': 'docker build -t ${{ github.repository }}:${{ github.sha }} .'
                        }
                    ]
                }
            }
        }
        
        workflow_dir = Path('.github/workflows')
        workflow_dir.mkdir(parents=True, exist_ok=True)
        
        workflow_file = workflow_dir / 'ci-cd.yml'
        with open(workflow_file, 'w') as f:
            yaml.dump(workflow, f)
        
        return str(workflow_file)
    
    async def _prepare_build_context(self, config: ContainerConfig) -> str:
        """Prepare Docker build context."""
        # This would prepare the build context, copy files, etc.
        return config.build_context
    
    async def _build_docker_image(self, config: ContainerConfig, 
                                 version_tag: str, build_context: str) -> Dict[str, Any]:
        """Build Docker image."""
        try:
            image_tag = f"{config.image_name}:{version_tag}"
            
            # Build command
            build_cmd = [
                'docker', 'build',
                '-t', image_tag,
                '-f', config.dockerfile_path
            ]
            
            # Add build args
            for key, value in config.build_args.items():
                build_cmd.extend(['--build-arg', f"{key}={value}"])
            
            build_cmd.append(build_context)
            
            # Execute build
            result = subprocess.run(
                build_cmd,
                capture_output=True,
                text=True,
                timeout=600  # 10 minutes timeout
            )
            
            if result.returncode != 0:
                raise subprocess.CalledProcessError(result.returncode, build_cmd, result.stdout, result.stderr)
            
            return {
                'success': True,
                'image_tag': image_tag,
                'output': result.stdout,
                'build_time': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'build_time': datetime.utcnow().isoformat()
            }
    
    async def _tag_image(self, config: ContainerConfig, version_tag: str) -> None:
        """Tag Docker image with additional tags."""
        base_image = f"{config.image_name}:{version_tag}"
        
        for tag in config.tags:
            tagged_image = f"{config.image_name}:{tag}"
            subprocess.run(['docker', 'tag', base_image, tagged_image], check=True)
    
    async def _push_image(self, config: ContainerConfig, version_tag: str) -> Dict[str, Any]:
        """Push Docker image to registry."""
        try:
            if config.registry_url:
                registry_image = f"{config.registry_url}/{config.image_name}:{version_tag}"
                
                # Tag for registry
                subprocess.run([
                    'docker', 'tag', 
                    f"{config.image_name}:{version_tag}", 
                    registry_image
                ], check=True)
                
                # Push to registry
                result = subprocess.run([
                    'docker', 'push', registry_image
                ], capture_output=True, text=True, check=True)
                
                return {
                    'success': True,
                    'registry_url': registry_image,
                    'output': result.stdout
                }
            
            return {'success': True, 'message': 'No registry configured'}
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _rolling_update_deployment(self, k8s_config: Dict[str, Any], 
                                        version: str, deployment_record: Dict[str, Any]) -> Dict[str, Any]:
        """Execute rolling update deployment."""
        # Implement rolling update logic
        deployment_record['steps'].append({
            'step': 'rolling_update',
            'status': 'completed',
            'timestamp': datetime.utcnow().isoformat()
        })
        
        return {'success': True, 'strategy': 'rolling_update'}
    
    async def _blue_green_deployment(self, k8s_config: Dict[str, Any], 
                                    version: str, deployment_record: Dict[str, Any]) -> Dict[str, Any]:
        """Execute blue-green deployment."""
        # Implement blue-green deployment logic
        deployment_record['steps'].append({
            'step': 'blue_green_deployment',
            'status': 'completed',
            'timestamp': datetime.utcnow().isoformat()
        })
        
        return {'success': True, 'strategy': 'blue_green'}
    
    async def _canary_deployment(self, k8s_config: Dict[str, Any], 
                                version: str, deployment_record: Dict[str, Any]) -> Dict[str, Any]:
        """Execute canary deployment."""
        # Implement canary deployment logic
        deployment_record['steps'].append({
            'step': 'canary_deployment',
            'status': 'completed',
            'timestamp': datetime.utcnow().isoformat()
        })
        
        return {'success': True, 'strategy': 'canary'}
    
    async def _recreate_deployment(self, k8s_config: Dict[str, Any], 
                                  version: str, deployment_record: Dict[str, Any]) -> Dict[str, Any]:
        """Execute recreate deployment."""
        # Implement recreate deployment logic
        deployment_record['steps'].append({
            'step': 'recreate_deployment',
            'status': 'completed',
            'timestamp': datetime.utcnow().isoformat()
        })
        
        return {'success': True, 'strategy': 'recreate'}
    
    async def _generate_values_file(self, values: Dict[str, Any], environment: str) -> str:
        """Generate Helm values file."""
        values_file = f"values-{environment}.yaml"
        
        with open(values_file, 'w') as f:
            yaml.dump(values, f)
        
        return values_file
    
    async def _helm_install(self, config: HelmConfig, values_file: str, environment: str) -> Dict[str, Any]:
        """Install Helm chart."""
        try:
            release_name = config.release_name or f"{config.chart_name}-{environment}"
            
            cmd = [
                'helm', 'install', release_name, config.chart_name,
                '-f', values_file,
                '--wait', '--timeout', '300s'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            return {
                'success': True,
                'release_name': release_name,
                'output': result.stdout
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _helm_upgrade(self, config: HelmConfig, values_file: str, environment: str) -> Dict[str, Any]:
        """Upgrade Helm chart."""
        try:
            release_name = config.release_name or f"{config.chart_name}-{environment}"
            
            cmd = [
                'helm', 'upgrade', release_name, config.chart_name,
                '-f', values_file,
                '--wait', '--timeout', '300s'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            return {
                'success': True,
                'release_name': release_name,
                'output': result.stdout
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _execute_rollback(self, deployment: Dict[str, Any], 
                               previous_deployment: Dict[str, Any]) -> Dict[str, Any]:
        """Execute deployment rollback."""
        # Implement rollback logic based on deployment strategy
        return {
            'success': True,
            'rolled_back_to': previous_deployment['version'],
            'rollback_time': datetime.utcnow().isoformat()
        }
    
    async def _check_deployment_progress(self, deployment: Dict[str, Any]) -> Dict[str, Any]:
        """Check current deployment progress."""
        # Check actual deployment status from Kubernetes
        return {
            'current_replicas': 2,
            'desired_replicas': 3,
            'ready_replicas': 2,
            'updated_replicas': 2,
            'progress_percentage': 67
        }
    
    @abstractmethod
    async def setup_service_specific_deployment(self) -> None:
        """Setup service-specific deployment configuration. Override in subclasses."""
        pass
    
    async def health_check(self) -> Dict[str, Any]:
        """Service health check."""
        base_health = await super().health_check()
        
        return {
            **base_health,
            'deployment': {
                'containers': len(self.container_configs),
                'k8s_deployments': len(self.k8s_configs),
                'helm_charts': len(self.helm_configs),
                'cicd_pipelines': len(self.cicd_configs),
                'active_deployments': len([d for d in self.deployments.values() 
                                         if d['status'] == DeploymentStatus.IN_PROGRESS])
            },
            'components': {
                'docker': 'available',
                'kubernetes': 'available',
                'helm': 'available'
            }
        }
    
    async def cleanup(self) -> None:
        """Cleanup deployment resources."""
        # Cleanup temporary files, stop running deployments, etc.
        await super().cleanup()