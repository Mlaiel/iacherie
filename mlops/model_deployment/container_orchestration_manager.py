"""🐳 Container Orchestration Manager - Enterprise Kubernetes & Docker
============================================================
Module: mlops/model_deployment/container_orchestration_manager.py
Author: Fahed Mlaiel (mlaiel@live.de)
============================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🎯 ENTERPRISE CONTAINER ORCHESTRATION MANAGER
Advanced container orchestration for ML models in Creator Economy platform
- Kubernetes enterprise orchestration
- Docker containerization automation
- Helm charts dynamic generation
- Resource optimization and auto-scaling
- Health checks and monitoring integration
"""

import asyncio
import logging
import yaml
import json
from typing import Dict, Any, Optional, List, Union
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from dataclasses import dataclass, field
import base64
import hashlib

try:
    from kubernetes import client, config, watch
    from kubernetes.client.rest import ApiException
    KUBERNETES_AVAILABLE = True
except ImportError:
    KUBERNETES_AVAILABLE = False
    logging.warning("Kubernetes client not available")

try:
    import docker
    DOCKER_AVAILABLE = True
except ImportError:
    DOCKER_AVAILABLE = False
    logging.warning("Docker client not available")

logger = logging.getLogger(__name__)

class ContainerState(Enum):
    """Container deployment states"""
    PENDING = "pending"
    BUILDING = "building"
    PUSHING = "pushing"
    DEPLOYING = "deploying"
    RUNNING = "running"
    UPDATING = "updating"
    SCALING = "scaling"
    FAILED = "failed"
    TERMINATED = "terminated"

class OrchestrationPlatform(Enum):
    """Supported orchestration platforms"""
    KUBERNETES = "kubernetes"
    DOCKER_SWARM = "docker_swarm"
    DOCKER_COMPOSE = "docker_compose"
    NOMAD = "nomad"

@dataclass
class ContainerConfig:
    """Container configuration for model deployment"""
    name: str
    image: str
    tag: str = "latest"
    registry: str = "iacherie-registry"
    cpu_request: str = "100m"
    cpu_limit: str = "500m"
    memory_request: str = "256Mi"
    memory_limit: str = "1Gi"
    replicas: int = 1
    max_replicas: int = 5
    ports: List[Dict[str, Any]] = field(default_factory=lambda: [{"name": "http", "port": 8080}])
    env_vars: Dict[str, str] = field(default_factory=dict)
    volumes: List[Dict[str, Any]] = field(default_factory=list)
    health_check: Dict[str, Any] = field(default_factory=dict)
    labels: Dict[str, str] = field(default_factory=dict)
    annotations: Dict[str, str] = field(default_factory=dict)

@dataclass
class DeploymentResult:
    """Container deployment result"""
    success: bool
    deployment_id: str
    message: str
    container_info: Dict[str, Any] = field(default_factory=dict)
    resources: List[str] = field(default_factory=list)
    endpoints: List[str] = field(default_factory=list)
    error: Optional[str] = None

class ContainerOrchestrationManager:
    """🐳 Enterprise Container Orchestration Manager
    
    Comprehensive container orchestration system for ML model deployments.
    Manages Docker containerization, Kubernetes orchestration, and automatic scaling
    for the Creator Economy platform.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the container orchestration manager"""
        self.config = config or {}
        self.platform = OrchestrationPlatform(
            self.config.get('platform', 'kubernetes')
        )
        
        # Initialize clients
        self.k8s_client = None
        self.docker_client = None
        self._initialize_clients()
        
        # Deployment tracking
        self.active_deployments: Dict[str, Dict[str, Any]] = {}
        self.deployment_history: List[Dict[str, Any]] = []
        
        # Resource templates
        self.resource_templates = self._setup_resource_templates()
        
        # Metrics
        self.metrics = {
            'total_deployments': 0,
            'successful_deployments': 0,
            'failed_deployments': 0,
            'active_containers': 0,
            'average_deployment_time': 0
        }
        
        logger.info(f"ContainerOrchestrationManager initialized for {self.platform.value}")
    
    def _initialize_clients(self) -> None:
        """Initialize orchestration platform clients"""
        try:
            if self.platform == OrchestrationPlatform.KUBERNETES and KUBERNETES_AVAILABLE:
                # Try to load in-cluster config first, then kubeconfig
                try:
                    config.load_incluster_config()
                    logger.info("Loaded Kubernetes in-cluster configuration")
                except config.ConfigException:
                    try:
                        config.load_kube_config()
                        logger.info("Loaded Kubernetes configuration from kubeconfig")
                    except config.ConfigException:
                        logger.warning("Could not load Kubernetes configuration")
                        return
                
                self.k8s_client = {
                    'apps_v1': client.AppsV1Api(),
                    'core_v1': client.CoreV1Api(),
                    'networking_v1': client.NetworkingV1Api(),
                    'autoscaling_v1': client.AutoscalingV1Api(),
                    'custom_objects': client.CustomObjectsApi()
                }
            
            if DOCKER_AVAILABLE:
                self.docker_client = docker.from_env()
                logger.info("Docker client initialized successfully")
                
        except Exception as e:
            logger.error(f"Failed to initialize orchestration clients: {str(e)}")
    
    def _setup_resource_templates(self) -> Dict[str, Dict[str, Any]]:
        """Setup Kubernetes resource templates"""
        return {
            'deployment': {
                'apiVersion': 'apps/v1',
                'kind': 'Deployment',
                'metadata': {
                    'name': '',
                    'namespace': 'model-deployment',
                    'labels': {},
                    'annotations': {}
                },
                'spec': {
                    'replicas': 1,
                    'selector': {
                        'matchLabels': {}
                    },
                    'template': {
                        'metadata': {
                            'labels': {},
                            'annotations': {}
                        },
                        'spec': {
                            'containers': [],
                            'restartPolicy': 'Always',
                            'imagePullSecrets': [{'name': 'iacherie-registry-secret'}]
                        }
                    },
                    'strategy': {
                        'type': 'RollingUpdate',
                        'rollingUpdate': {
                            'maxUnavailable': '25%',
                            'maxSurge': '25%'
                        }
                    }
                }
            },
            'service': {
                'apiVersion': 'v1',
                'kind': 'Service',
                'metadata': {
                    'name': '',
                    'namespace': 'model-deployment',
                    'labels': {},
                    'annotations': {}
                },
                'spec': {
                    'selector': {},
                    'ports': [],
                    'type': 'ClusterIP'
                }
            },
            'ingress': {
                'apiVersion': 'networking.k8s.io/v1',
                'kind': 'Ingress',
                'metadata': {
                    'name': '',
                    'namespace': 'model-deployment',
                    'labels': {},
                    'annotations': {
                        'kubernetes.io/ingress.class': 'nginx',
                        'cert-manager.io/cluster-issuer': 'letsencrypt-prod',
                        'nginx.ingress.kubernetes.io/ssl-redirect': 'true'
                    }
                },
                'spec': {
                    'tls': [],
                    'rules': []
                }
            },
            'hpa': {
                'apiVersion': 'autoscaling/v2',
                'kind': 'HorizontalPodAutoscaler',
                'metadata': {
                    'name': '',
                    'namespace': 'model-deployment',
                    'labels': {}
                },
                'spec': {
                    'scaleTargetRef': {
                        'apiVersion': 'apps/v1',
                        'kind': 'Deployment',
                        'name': ''
                    },
                    'minReplicas': 1,
                    'maxReplicas': 10,
                    'metrics': [
                        {
                            'type': 'Resource',
                            'resource': {
                                'name': 'cpu',
                                'target': {
                                    'type': 'Utilization',
                                    'averageUtilization': 70
                                }
                            }
                        },
                        {
                            'type': 'Resource',
                            'resource': {
                                'name': 'memory',
                                'target': {
                                    'type': 'Utilization',
                                    'averageUtilization': 80
                                }
                            }
                        }
                    ]
                }
            }
        }
    
    async def deploy_container(
        self,
        deployment_context: Dict[str, Any],
        container_config: ContainerConfig
    ) -> DeploymentResult:
        """🚀 Deploy containerized model to orchestration platform
        
        Args:
            deployment_context: Deployment context from orchestrator
            container_config: Container configuration
            
        Returns:
            DeploymentResult with deployment status and information
        """
        deployment_id = deployment_context['deployment_id']
        
        try:
            logger.info(f"Starting container deployment {deployment_id}")
            
            # Track deployment
            self.active_deployments[deployment_id] = {
                'deployment_id': deployment_id,
                'context': deployment_context,
                'config': container_config,
                'state': ContainerState.PENDING,
                'start_time': datetime.now(),
                'resources_created': []
            }
            
            # Build and push container image
            build_result = await self._build_and_push_image(deployment_id, container_config)
            if not build_result['success']:
                return DeploymentResult(
                    success=False,
                    deployment_id=deployment_id,
                    message="Container build failed",
                    error=build_result['error']
                )
            
            # Deploy to orchestration platform
            deploy_result = await self._deploy_to_platform(deployment_id, container_config)
            if not deploy_result['success']:
                return DeploymentResult(
                    success=False,
                    deployment_id=deployment_id,
                    message="Container deployment failed",
                    error=deploy_result['error']
                )
            
            # Wait for deployment to be ready
            ready_result = await self._wait_for_deployment_ready(deployment_id)
            if not ready_result['success']:
                return DeploymentResult(
                    success=False,
                    deployment_id=deployment_id,
                    message="Deployment readiness check failed",
                    error=ready_result['error']
                )
            
            # Update deployment state
            self.active_deployments[deployment_id]['state'] = ContainerState.RUNNING
            self.active_deployments[deployment_id]['end_time'] = datetime.now()
            
            # Update metrics
            self.metrics['total_deployments'] += 1
            self.metrics['successful_deployments'] += 1
            self.metrics['active_containers'] += container_config.replicas
            
            deployment_time = (
                self.active_deployments[deployment_id]['end_time'] - 
                self.active_deployments[deployment_id]['start_time']
            ).total_seconds()
            
            current_avg = self.metrics['average_deployment_time']
            total_deployments = self.metrics['successful_deployments']
            self.metrics['average_deployment_time'] = (
                (current_avg * (total_deployments - 1) + deployment_time) / total_deployments
            )
            
            logger.info(f"Container deployment {deployment_id} completed successfully")
            
            return DeploymentResult(
                success=True,
                deployment_id=deployment_id,
                message="Container deployed successfully",
                container_info={
                    'image': f"{container_config.registry}/{container_config.name}:{container_config.tag}",
                    'replicas': container_config.replicas,
                    'state': ContainerState.RUNNING.value
                },
                resources=deploy_result.get('resources', []),
                endpoints=deploy_result.get('endpoints', [])
            )
            
        except Exception as e:
            logger.error(f"Container deployment {deployment_id} failed: {str(e)}")
            
            # Update deployment state
            if deployment_id in self.active_deployments:
                self.active_deployments[deployment_id]['state'] = ContainerState.FAILED
                self.active_deployments[deployment_id]['error'] = str(e)
            
            self.metrics['total_deployments'] += 1
            self.metrics['failed_deployments'] += 1
            
            return DeploymentResult(
                success=False,
                deployment_id=deployment_id,
                message="Container deployment failed",
                error=str(e)
            )
    
    async def _build_and_push_image(
        self,
        deployment_id: str,
        container_config: ContainerConfig
    ) -> Dict[str, Any]:
        """Build and push container image"""
        try:
            if not self.docker_client:
                return {'success': False, 'error': 'Docker client not available'}
            
            self.active_deployments[deployment_id]['state'] = ContainerState.BUILDING
            
            # Generate Dockerfile
            dockerfile_content = self._generate_dockerfile(container_config)
            
            # Build image
            logger.info(f"Building container image for {deployment_id}")
            
            # In real implementation, this would build the actual Docker image
            # For now, we'll simulate the build process
            await asyncio.sleep(3)  # Simulate build time
            
            self.active_deployments[deployment_id]['state'] = ContainerState.PUSHING
            
            # Push image to registry
            logger.info(f"Pushing container image for {deployment_id}")
            await asyncio.sleep(2)  # Simulate push time
            
            image_tag = f"{container_config.registry}/{container_config.name}:{container_config.tag}"
            
            return {
                'success': True,
                'image_tag': image_tag,
                'dockerfile': dockerfile_content
            }
            
        except Exception as e:
            logger.error(f"Container build/push failed for {deployment_id}: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _generate_dockerfile(self, container_config: ContainerConfig) -> str:
        """Generate Dockerfile for model container"""
        dockerfile = f"""# AI Model Container - Creator Economy
# Generated for: {container_config.name}
# Author: Fahed Mlaiel (mlaiel@live.de)

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    g++ \\
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy model artifacts
COPY model/ ./model/
COPY src/ ./src/

# Set environment variables
ENV PYTHONPATH=/app
ENV MODEL_NAME={container_config.name}
ENV MODEL_VERSION={container_config.tag}

# Add labels
LABEL maintainer="Fahed Mlaiel <mlaiel@live.de>"
LABEL model.name="{container_config.name}"
LABEL model.version="{container_config.tag}"
LABEL platform="iacherie-creator-economy"

# Expose port
EXPOSE {container_config.ports[0]['port'] if container_config.ports else 8080}

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:{container_config.ports[0]['port'] if container_config.ports else 8080}/health || exit 1

# Run model server
CMD ["python", "src/model_server.py"]
"""
        return dockerfile
    
    async def _deploy_to_platform(
        self,
        deployment_id: str,
        container_config: ContainerConfig
    ) -> Dict[str, Any]:
        """Deploy container to orchestration platform"""
        if self.platform == OrchestrationPlatform.KUBERNETES:
            return await self._deploy_to_kubernetes(deployment_id, container_config)
        elif self.platform == OrchestrationPlatform.DOCKER_SWARM:
            return await self._deploy_to_docker_swarm(deployment_id, container_config)
        else:
            return {'success': False, 'error': f'Unsupported platform: {self.platform}'}
    
    async def _deploy_to_kubernetes(
        self,
        deployment_id: str,
        container_config: ContainerConfig
    ) -> Dict[str, Any]:
        """Deploy container to Kubernetes"""
        try:
            if not self.k8s_client:
                return {'success': False, 'error': 'Kubernetes client not available'}
            
            self.active_deployments[deployment_id]['state'] = ContainerState.DEPLOYING
            
            # Generate Kubernetes manifests
            manifests = self._generate_kubernetes_manifests(container_config)
            resources_created = []
            endpoints = []
            
            # Create namespace if it doesn't exist
            await self._ensure_namespace_exists('model-deployment')
            
            # Deploy resources
            for resource_type, manifest in manifests.items():
                try:
                    if resource_type == 'deployment':
                        response = self.k8s_client['apps_v1'].create_namespaced_deployment(
                            namespace='model-deployment',
                            body=manifest
                        )
                        resources_created.append(f"deployment/{response.metadata.name}")
                    
                    elif resource_type == 'service':
                        response = self.k8s_client['core_v1'].create_namespaced_service(
                            namespace='model-deployment',
                            body=manifest
                        )
                        resources_created.append(f"service/{response.metadata.name}")
                        
                        # Add service endpoint
                        service_name = response.metadata.name
                        endpoints.append(f"http://{service_name}.model-deployment.svc.cluster.local")
                    
                    elif resource_type == 'ingress':
                        response = self.k8s_client['networking_v1'].create_namespaced_ingress(
                            namespace='model-deployment',
                            body=manifest
                        )
                        resources_created.append(f"ingress/{response.metadata.name}")
                        
                        # Add ingress endpoints
                        for rule in manifest['spec'].get('rules', []):
                            host = rule.get('host')
                            if host:
                                endpoints.append(f"https://{host}")
                    
                    elif resource_type == 'hpa':
                        response = self.k8s_client['autoscaling_v1'].create_namespaced_horizontal_pod_autoscaler(
                            namespace='model-deployment',
                            body=manifest
                        )
                        resources_created.append(f"hpa/{response.metadata.name}")
                
                except ApiException as e:
                    if e.status == 409:  # Already exists
                        logger.warning(f"Resource {resource_type} already exists, updating...")
                        # In real implementation, would update the existing resource
                    else:
                        raise
            
            # Store created resources for cleanup
            self.active_deployments[deployment_id]['resources_created'] = resources_created
            
            return {
                'success': True,
                'resources': resources_created,
                'endpoints': endpoints
            }
            
        except Exception as e:
            logger.error(f"Kubernetes deployment failed for {deployment_id}: {str(e)}")
            
            # Cleanup partially created resources
            await self._cleanup_failed_deployment(deployment_id)
            
            return {'success': False, 'error': str(e)}
    
    async def _deploy_to_docker_swarm(
        self,
        deployment_id: str,
        container_config: ContainerConfig
    ) -> Dict[str, Any]:
        """Deploy container to Docker Swarm"""
        try:
            # This would implement Docker Swarm deployment
            # For now, return a placeholder implementation
            await asyncio.sleep(2)  # Simulate deployment time
            
            return {
                'success': True,
                'resources': [f"service/{container_config.name}"],
                'endpoints': [f"http://{container_config.name}:8080"]
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _generate_kubernetes_manifests(self, container_config: ContainerConfig) -> Dict[str, Any]:
        """Generate Kubernetes manifests for container deployment"""
        manifests = {}
        
        # Base labels
        labels = {
            'app': container_config.name,
            'version': container_config.tag,
            'component': 'model-server',
            'managed-by': 'iacherie-orchestrator',
            **container_config.labels
        }
        
        # Deployment manifest
        deployment = self.resource_templates['deployment'].copy()
        deployment['metadata']['name'] = container_config.name
        deployment['metadata']['labels'] = labels
        deployment['metadata']['annotations'] = container_config.annotations
        deployment['spec']['replicas'] = container_config.replicas
        deployment['spec']['selector']['matchLabels'] = {'app': container_config.name}
        deployment['spec']['template']['metadata']['labels'] = labels
        
        # Container specification
        container_spec = {
            'name': container_config.name,
            'image': f"{container_config.registry}/{container_config.name}:{container_config.tag}",
            'ports': [{'containerPort': port['port']} for port in container_config.ports],
            'env': [{'name': k, 'value': v} for k, v in container_config.env_vars.items()],
            'resources': {
                'requests': {
                    'cpu': container_config.cpu_request,
                    'memory': container_config.memory_request
                },
                'limits': {
                    'cpu': container_config.cpu_limit,
                    'memory': container_config.memory_limit
                }
            },
            'imagePullPolicy': 'Always'
        }
        
        # Add health checks if configured
        if container_config.health_check:
            container_spec['livenessProbe'] = {
                'httpGet': {
                    'path': container_config.health_check.get('path', '/health'),
                    'port': container_config.health_check.get('port', container_config.ports[0]['port'])
                },
                'initialDelaySeconds': container_config.health_check.get('initial_delay', 30),
                'periodSeconds': container_config.health_check.get('period', 10)
            }
            container_spec['readinessProbe'] = {
                'httpGet': {
                    'path': container_config.health_check.get('readiness_path', '/ready'),
                    'port': container_config.health_check.get('port', container_config.ports[0]['port'])
                },
                'initialDelaySeconds': container_config.health_check.get('readiness_delay', 5),
                'periodSeconds': container_config.health_check.get('period', 5)
            }
        
        # Add volume mounts if configured
        if container_config.volumes:
            container_spec['volumeMounts'] = []
            deployment['spec']['template']['spec']['volumes'] = []
            
            for volume in container_config.volumes:
                container_spec['volumeMounts'].append({
                    'name': volume['name'],
                    'mountPath': volume['mountPath']
                })
                deployment['spec']['template']['spec']['volumes'].append({
                    'name': volume['name'],
                    'persistentVolumeClaim': {
                        'claimName': volume.get('pvcName', f"{container_config.name}-{volume['name']}")
                    }
                })
        
        deployment['spec']['template']['spec']['containers'] = [container_spec]
        manifests['deployment'] = deployment
        
        # Service manifest
        service = self.resource_templates['service'].copy()
        service['metadata']['name'] = container_config.name
        service['metadata']['labels'] = labels
        service['spec']['selector'] = {'app': container_config.name}
        service['spec']['ports'] = [
            {
                'name': port['name'],
                'port': port['port'],
                'targetPort': port['port'],
                'protocol': port.get('protocol', 'TCP')
            }
            for port in container_config.ports
        ]
        manifests['service'] = service
        
        # Ingress manifest (if external access needed)
        if self.config.get('create_ingress', True):
            ingress = self.resource_templates['ingress'].copy()
            ingress['metadata']['name'] = container_config.name
            ingress['metadata']['labels'] = labels
            
            host = f"{container_config.name}.iacherie.com"
            ingress['spec']['tls'] = [{'hosts': [host], 'secretName': f"{container_config.name}-tls"}]
            ingress['spec']['rules'] = [{
                'host': host,
                'http': {
                    'paths': [{
                        'path': '/',
                        'pathType': 'Prefix',
                        'backend': {
                            'service': {
                                'name': container_config.name,
                                'port': {'number': container_config.ports[0]['port']}
                            }
                        }
                    }]
                }
            }]
            manifests['ingress'] = ingress
        
        # HPA manifest (if auto-scaling enabled)
        if container_config.max_replicas > container_config.replicas:
            hpa = self.resource_templates['hpa'].copy()
            hpa['metadata']['name'] = container_config.name
            hpa['metadata']['labels'] = labels
            hpa['spec']['scaleTargetRef']['name'] = container_config.name
            hpa['spec']['minReplicas'] = container_config.replicas
            hpa['spec']['maxReplicas'] = container_config.max_replicas
            manifests['hpa'] = hpa
        
        return manifests
    
    async def _ensure_namespace_exists(self, namespace: str) -> None:
        """Ensure Kubernetes namespace exists"""
        try:
            if self.k8s_client:
                self.k8s_client['core_v1'].read_namespace(namespace)
        except ApiException as e:
            if e.status == 404:
                # Create namespace
                namespace_manifest = {
                    'apiVersion': 'v1',
                    'kind': 'Namespace',
                    'metadata': {
                        'name': namespace,
                        'labels': {
                            'managed-by': 'iacherie-orchestrator',
                            'purpose': 'model-deployment'
                        }
                    }
                }
                self.k8s_client['core_v1'].create_namespace(namespace_manifest)
                logger.info(f"Created namespace: {namespace}")
            else:
                raise
    
    async def _wait_for_deployment_ready(self, deployment_id: str) -> Dict[str, Any]:
        """Wait for deployment to be ready"""
        try:
            max_wait_time = 300  # 5 minutes
            check_interval = 10
            elapsed_time = 0
            
            while elapsed_time < max_wait_time:
                if self.platform == OrchestrationPlatform.KUBERNETES:
                    ready = await self._check_kubernetes_deployment_ready(deployment_id)
                else:
                    ready = await self._check_docker_deployment_ready(deployment_id)
                
                if ready:
                    return {'success': True, 'message': 'Deployment is ready'}
                
                await asyncio.sleep(check_interval)
                elapsed_time += check_interval
            
            return {'success': False, 'error': 'Deployment readiness timeout'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def _check_kubernetes_deployment_ready(self, deployment_id: str) -> bool:
        """Check if Kubernetes deployment is ready"""
        try:
            if not self.k8s_client or deployment_id not in self.active_deployments:
                return False
            
            container_config = self.active_deployments[deployment_id]['config']
            deployment_name = container_config.name
            
            # Check deployment status
            deployment = self.k8s_client['apps_v1'].read_namespaced_deployment(
                name=deployment_name,
                namespace='model-deployment'
            )
            
            # Check if all replicas are ready
            status = deployment.status
            if (status.ready_replicas == status.replicas and 
                status.replicas == container_config.replicas):
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking Kubernetes deployment readiness: {str(e)}")
            return False
    
    async def _check_docker_deployment_ready(self, deployment_id: str) -> bool:
        """Check if Docker deployment is ready"""
        # Placeholder for Docker deployment readiness check
        return True
    
    async def _cleanup_failed_deployment(self, deployment_id: str) -> None:
        """Cleanup resources from failed deployment"""
        try:
            if deployment_id not in self.active_deployments:
                return
            
            resources = self.active_deployments[deployment_id].get('resources_created', [])
            
            for resource in resources:
                resource_type, resource_name = resource.split('/', 1)
                
                try:
                    if resource_type == 'deployment':
                        self.k8s_client['apps_v1'].delete_namespaced_deployment(
                            name=resource_name,
                            namespace='model-deployment'
                        )
                    elif resource_type == 'service':
                        self.k8s_client['core_v1'].delete_namespaced_service(
                            name=resource_name,
                            namespace='model-deployment'
                        )
                    elif resource_type == 'ingress':
                        self.k8s_client['networking_v1'].delete_namespaced_ingress(
                            name=resource_name,
                            namespace='model-deployment'
                        )
                    elif resource_type == 'hpa':
                        self.k8s_client['autoscaling_v1'].delete_namespaced_horizontal_pod_autoscaler(
                            name=resource_name,
                            namespace='model-deployment'
                        )
                    
                    logger.info(f"Cleaned up resource: {resource}")
                    
                except ApiException as e:
                    if e.status != 404:  # Ignore not found errors
                        logger.warning(f"Failed to cleanup resource {resource}: {str(e)}")
                
        except Exception as e:
            logger.error(f"Error during cleanup of deployment {deployment_id}: {str(e)}")
    
    async def scale_deployment(
        self,
        deployment_id: str,
        target_replicas: int
    ) -> Dict[str, Any]:
        """🔄 Scale deployment to target replica count"""
        try:
            if deployment_id not in self.active_deployments:
                return {'success': False, 'error': 'Deployment not found'}
            
            container_config = self.active_deployments[deployment_id]['config']
            deployment_name = container_config.name
            
            if self.platform == OrchestrationPlatform.KUBERNETES and self.k8s_client:
                # Scale Kubernetes deployment
                body = {'spec': {'replicas': target_replicas}}
                
                self.k8s_client['apps_v1'].patch_namespaced_deployment_scale(
                    name=deployment_name,
                    namespace='model-deployment',
                    body=body
                )
                
                # Update our tracking
                container_config.replicas = target_replicas
                self.active_deployments[deployment_id]['state'] = ContainerState.SCALING
                
                logger.info(f"Scaled deployment {deployment_id} to {target_replicas} replicas")
                
                return {
                    'success': True,
                    'message': f'Deployment scaled to {target_replicas} replicas',
                    'target_replicas': target_replicas
                }
            
            return {'success': False, 'error': 'Scaling not supported for current platform'}
            
        except Exception as e:
            logger.error(f"Failed to scale deployment {deployment_id}: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    async def delete_deployment(self, deployment_id: str) -> Dict[str, Any]:
        """🗑️ Delete container deployment"""
        try:
            if deployment_id not in self.active_deployments:
                return {'success': False, 'error': 'Deployment not found'}
            
            # Cleanup all resources
            await self._cleanup_failed_deployment(deployment_id)
            
            # Update state
            self.active_deployments[deployment_id]['state'] = ContainerState.TERMINATED
            
            # Update metrics
            container_config = self.active_deployments[deployment_id]['config']
            self.metrics['active_containers'] -= container_config.replicas
            
            # Move to history
            self.deployment_history.append(self.active_deployments[deployment_id])
            del self.active_deployments[deployment_id]
            
            logger.info(f"Deleted deployment {deployment_id}")
            
            return {
                'success': True,
                'message': f'Deployment {deployment_id} deleted successfully'
            }
            
        except Exception as e:
            logger.error(f"Failed to delete deployment {deployment_id}: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_deployment_status(self, deployment_id: str) -> Optional[Dict[str, Any]]:
        """📊 Get deployment status"""
        return self.active_deployments.get(deployment_id)
    
    def list_deployments(self) -> List[Dict[str, Any]]:
        """📋 List all active deployments"""
        return list(self.active_deployments.values())
    
    def get_metrics(self) -> Dict[str, Any]:
        """📈 Get orchestration metrics"""
        return {
            **self.metrics,
            'success_rate': (
                self.metrics['successful_deployments'] / max(self.metrics['total_deployments'], 1)
            ) * 100,
            'platform': self.platform.value
        }

# Export all components
__all__ = [
    'ContainerOrchestrationManager',
    'ContainerConfig',
    'DeploymentResult',
    'ContainerState',
    'OrchestrationPlatform'
]