"""
AI Deployment Manager Service - Enterprise Multi-Cloud AI Deployment
Ainflue Platform - Microservices Architecture

© FAHED MLAIEL 2024-2025 - CONFIDENTIAL ENTERPRISE MODULE
"""

import asyncio
import json
import logging
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import yaml
import subprocess

class DeploymentStatus(Enum):
    """Deployment status states"""
    PENDING = "pending"
    DEPLOYING = "deploying"
    DEPLOYED = "deployed"
    UPDATING = "updating"
    ROLLING_BACK = "rolling_back"
    FAILED = "failed"
    TERMINATED = "terminated"

class CloudProvider(Enum):
    """Supported cloud providers"""
    AWS = "aws"
    AZURE = "azure"
    GCP = "gcp"
    KUBERNETES = "kubernetes"
    ON_PREMISE = "on_premise"

class DeploymentType(Enum):
    """Types of AI deployments"""
    INFERENCE_API = "inference_api"
    BATCH_PROCESSING = "batch_processing"
    STREAMING = "streaming"
    EDGE_DEPLOYMENT = "edge_deployment"
    SERVERLESS = "serverless"

@dataclass
class AIDeploymentConfig:
    """AI deployment configuration"""
    deployment_id: str
    model_id: str
    deployment_name: str
    deployment_type: DeploymentType
    cloud_provider: CloudProvider
    region: str
    instance_type: str
    min_replicas: int
    max_replicas: int
    auto_scaling: bool
    environment_variables: Dict[str, str]
    resource_requirements: Dict[str, str]
    security_config: Dict[str, Any]
    monitoring_config: Dict[str, Any]

@dataclass
class DeploymentResult:
    """Deployment execution result"""
    deployment_id: str
    config: AIDeploymentConfig
    status: DeploymentStatus
    endpoint_url: Optional[str]
    start_time: datetime
    end_time: Optional[datetime]
    duration_seconds: Optional[float]
    logs: List[str]
    metrics: Dict[str, Any]
    error_message: Optional[str]
    rollback_available: bool

@dataclass
class DeploymentMetrics:
    """Deployment performance metrics"""
    deployment_id: str
    requests_per_second: float
    average_latency_ms: float
    error_rate_percent: float
    cpu_utilization_percent: float
    memory_utilization_percent: float
    active_replicas: int
    timestamp: datetime

class AIDeploymentManager:
    """
    Enterprise AI Deployment Manager Service
    
    Manages AI model deployments across multiple cloud providers
    with support for auto-scaling, blue-green deployments, canary releases,
    monitoring, and automated rollbacks for enterprise AI infrastructure.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.deployments = {}
        self.deployment_history = {}
        self.cloud_configs = {}
        self.deployment_templates = {}
        
    async def initialize(self) -> bool:
        """Initialize AI deployment manager"""
        try:
            self.logger.info("Initializing AI Deployment Manager Service...")
            
            # Initialize cloud provider configurations
            await self._initialize_cloud_configs()
            
            # Load deployment templates
            await self._load_deployment_templates()
            
            # Setup monitoring
            await self._setup_deployment_monitoring()
            
            self.logger.info("AI Deployment Manager Service initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize AI Deployment Manager: {e}")
            return False
    
    async def _initialize_cloud_configs(self):
        """Initialize cloud provider configurations"""
        self.cloud_configs = {
            CloudProvider.AWS: {
                'regions': ['us-east-1', 'us-west-2', 'eu-west-1', 'ap-southeast-1'],
                'instance_types': {
                    'small': 't3.medium',
                    'medium': 'c5.large',
                    'large': 'c5.xlarge',
                    'gpu': 'p3.2xlarge'
                },
                'services': {
                    'container': 'ECS',
                    'serverless': 'Lambda',
                    'kubernetes': 'EKS'
                }
            },
            CloudProvider.AZURE: {
                'regions': ['eastus', 'westus2', 'westeurope', 'southeastasia'],
                'instance_types': {
                    'small': 'Standard_D2s_v3',
                    'medium': 'Standard_D4s_v3',
                    'large': 'Standard_D8s_v3',
                    'gpu': 'Standard_NC6s_v3'
                },
                'services': {
                    'container': 'ACI',
                    'serverless': 'Functions',
                    'kubernetes': 'AKS'
                }
            },
            CloudProvider.GCP: {
                'regions': ['us-central1', 'us-west1', 'europe-west1', 'asia-southeast1'],
                'instance_types': {
                    'small': 'e2-standard-2',
                    'medium': 'c2-standard-4',
                    'large': 'c2-standard-8',
                    'gpu': 'n1-standard-4-k80'
                },
                'services': {
                    'container': 'Cloud Run',
                    'serverless': 'Cloud Functions',
                    'kubernetes': 'GKE'
                }
            },
            CloudProvider.KUBERNETES: {
                'namespaces': ['ai-inference', 'ai-training', 'ai-batch'],
                'resource_quotas': {
                    'cpu': '100',
                    'memory': '200Gi',
                    'gpu': '10'
                }
            }
        }
    
    async def _load_deployment_templates(self):
        """Load deployment templates for different scenarios"""
        self.deployment_templates = {
            'inference_api': {
                'replicas': {'min': 2, 'max': 10},
                'resources': {
                    'cpu': '1000m',
                    'memory': '2Gi',
                    'storage': '10Gi'
                },
                'auto_scaling': {
                    'enabled': True,
                    'target_cpu': 70,
                    'target_memory': 80
                },
                'health_checks': {
                    'liveness_probe': '/health',
                    'readiness_probe': '/ready',
                    'startup_probe': '/startup'
                }
            },
            'batch_processing': {
                'replicas': {'min': 1, 'max': 50},
                'resources': {
                    'cpu': '2000m',
                    'memory': '4Gi',
                    'storage': '50Gi'
                },
                'auto_scaling': {
                    'enabled': True,
                    'target_cpu': 80,
                    'scale_on_queue': True
                }
            },
            'edge_deployment': {
                'replicas': {'min': 1, 'max': 3},
                'resources': {
                    'cpu': '500m',
                    'memory': '1Gi',
                    'storage': '5Gi'
                },
                'constraints': {
                    'lightweight': True,
                    'offline_capable': True
                }
            }
        }
    
    async def _setup_deployment_monitoring(self):
        """Setup deployment monitoring and alerting"""
        self.monitoring_config = {
            'metrics_collection_interval': 30,  # seconds
            'health_check_interval': 15,        # seconds
            'alert_thresholds': {
                'error_rate': 5.0,               # percent
                'latency_p99': 1000,             # milliseconds
                'cpu_utilization': 85,           # percent
                'memory_utilization': 90         # percent
            },
            'alerting_channels': ['email', 'slack', 'pagerduty']
        }
    
    async def deploy_model(self, config: AIDeploymentConfig) -> DeploymentResult:
        """
        Deploy AI model to specified cloud provider
        
        Args:
            config: Deployment configuration
            
        Returns:
            DeploymentResult: Deployment execution result
        """
        start_time = datetime.now()
        logs = []
        
        try:
            self.logger.info(f"Starting deployment: {config.deployment_id}")
            logs.append(f"Deployment started: {start_time.isoformat()}")
            
            # Validate deployment configuration
            validation_result = await self._validate_deployment_config(config)
            if not validation_result['valid']:
                raise ValueError(f"Invalid deployment config: {validation_result['errors']}")
            
            logs.append("Configuration validation passed")
            
            # Create deployment manifest
            manifest = await self._create_deployment_manifest(config)
            logs.append("Deployment manifest created")
            
            # Execute deployment based on cloud provider
            if config.cloud_provider == CloudProvider.KUBERNETES:
                deployment_result = await self._deploy_to_kubernetes(config, manifest)
            elif config.cloud_provider == CloudProvider.AWS:
                deployment_result = await self._deploy_to_aws(config, manifest)
            elif config.cloud_provider == CloudProvider.AZURE:
                deployment_result = await self._deploy_to_azure(config, manifest)
            elif config.cloud_provider == CloudProvider.GCP:
                deployment_result = await self._deploy_to_gcp(config, manifest)
            else:
                raise ValueError(f"Unsupported cloud provider: {config.cloud_provider}")
            
            logs.extend(deployment_result['logs'])
            endpoint_url = deployment_result['endpoint_url']
            
            # Wait for deployment to be ready
            await self._wait_for_deployment_ready(config.deployment_id, timeout=600)
            logs.append("Deployment is ready and healthy")
            
            # Setup monitoring
            await self._setup_deployment_monitoring_for_deployment(config.deployment_id)
            logs.append("Monitoring configured")
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            result = DeploymentResult(
                deployment_id=config.deployment_id,
                config=config,
                status=DeploymentStatus.DEPLOYED,
                endpoint_url=endpoint_url,
                start_time=start_time,
                end_time=end_time,
                duration_seconds=duration,
                logs=logs,
                metrics=await self._get_deployment_metrics(config.deployment_id),
                error_message=None,
                rollback_available=True
            )
            
            self.deployments[config.deployment_id] = result
            
            # Store in deployment history
            if config.model_id not in self.deployment_history:
                self.deployment_history[config.model_id] = []
            self.deployment_history[config.model_id].append(result)
            
            self.logger.info(f"Deployment completed successfully: {config.deployment_id}")
            return result
            
        except Exception as e:
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            error_message = str(e)
            logs.append(f"Deployment failed: {error_message}")
            
            result = DeploymentResult(
                deployment_id=config.deployment_id,
                config=config,
                status=DeploymentStatus.FAILED,
                endpoint_url=None,
                start_time=start_time,
                end_time=end_time,
                duration_seconds=duration,
                logs=logs,
                metrics={},
                error_message=error_message,
                rollback_available=False
            )
            
            self.deployments[config.deployment_id] = result
            
            self.logger.error(f"Deployment failed: {config.deployment_id} - {error_message}")
            raise
    
    async def _validate_deployment_config(self, config: AIDeploymentConfig) -> Dict[str, Any]:
        """Validate deployment configuration"""
        errors = []
        
        # Validate cloud provider support
        if config.cloud_provider not in self.cloud_configs:
            errors.append(f"Unsupported cloud provider: {config.cloud_provider}")
        
        # Validate region
        if config.cloud_provider != CloudProvider.KUBERNETES:
            supported_regions = self.cloud_configs[config.cloud_provider]['regions']
            if config.region not in supported_regions:
                errors.append(f"Unsupported region {config.region} for {config.cloud_provider}")
        
        # Validate instance type
        if config.cloud_provider != CloudProvider.KUBERNETES:
            instance_types = self.cloud_configs[config.cloud_provider]['instance_types']
            if config.instance_type not in instance_types.values():
                errors.append(f"Unsupported instance type: {config.instance_type}")
        
        # Validate replica counts
        if config.min_replicas < 1:
            errors.append("Minimum replicas must be at least 1")
        
        if config.max_replicas < config.min_replicas:
            errors.append("Maximum replicas must be >= minimum replicas")
        
        # Validate resource requirements
        required_resources = ['cpu', 'memory']
        for resource in required_resources:
            if resource not in config.resource_requirements:
                errors.append(f"Missing required resource: {resource}")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
    
    async def _create_deployment_manifest(self, config: AIDeploymentConfig) -> Dict[str, Any]:
        """Create deployment manifest for the specified cloud provider"""
        template = self.deployment_templates.get(config.deployment_type.value, self.deployment_templates['inference_api'])
        
        if config.cloud_provider == CloudProvider.KUBERNETES:
            return await self._create_kubernetes_manifest(config, template)
        elif config.cloud_provider == CloudProvider.AWS:
            return await self._create_aws_manifest(config, template)
        elif config.cloud_provider == CloudProvider.AZURE:
            return await self._create_azure_manifest(config, template)
        elif config.cloud_provider == CloudProvider.GCP:
            return await self._create_gcp_manifest(config, template)
        
        raise ValueError(f"Unsupported cloud provider: {config.cloud_provider}")
    
    async def _create_kubernetes_manifest(self, config: AIDeploymentConfig, template: Dict[str, Any]) -> Dict[str, Any]:
        """Create Kubernetes deployment manifest"""
        return {
            'apiVersion': 'apps/v1',
            'kind': 'Deployment',
            'metadata': {
                'name': config.deployment_name,
                'namespace': 'ai-inference',
                'labels': {
                    'app': config.deployment_name,
                    'model': config.model_id,
                    'deployment-id': config.deployment_id
                }
            },
            'spec': {
                'replicas': config.min_replicas,
                'selector': {
                    'matchLabels': {
                        'app': config.deployment_name
                    }
                },
                'template': {
                    'metadata': {
                        'labels': {
                            'app': config.deployment_name,
                            'model': config.model_id
                        }
                    },
                    'spec': {
                        'containers': [{
                            'name': 'ai-model',
                            'image': f'ainflue/ai-model:{config.model_id}',
                            'ports': [{'containerPort': 8080}],
                            'env': [
                                {'name': k, 'value': v} 
                                for k, v in config.environment_variables.items()
                            ],
                            'resources': {
                                'requests': config.resource_requirements,
                                'limits': config.resource_requirements
                            },
                            'livenessProbe': {
                                'httpGet': {
                                    'path': '/health',
                                    'port': 8080
                                },
                                'initialDelaySeconds': 30,
                                'periodSeconds': 10
                            },
                            'readinessProbe': {
                                'httpGet': {
                                    'path': '/ready',
                                    'port': 8080
                                },
                                'initialDelaySeconds': 10,
                                'periodSeconds': 5
                            }
                        }]
                    }
                }
            }
        }
    
    async def _create_aws_manifest(self, config: AIDeploymentConfig, template: Dict[str, Any]) -> Dict[str, Any]:
        """Create AWS ECS/Fargate deployment manifest"""
        return {
            'family': config.deployment_name,
            'networkMode': 'awsvpc',
            'requiresCompatibilities': ['FARGATE'],
            'cpu': config.resource_requirements.get('cpu', '1024'),
            'memory': config.resource_requirements.get('memory', '2048'),
            'containerDefinitions': [{
                'name': 'ai-model',
                'image': f'ainflue/ai-model:{config.model_id}',
                'portMappings': [{
                    'containerPort': 8080,
                    'protocol': 'tcp'
                }],
                'environment': [
                    {'name': k, 'value': v} 
                    for k, v in config.environment_variables.items()
                ],
                'healthCheck': {
                    'command': ['CMD-SHELL', 'curl -f http://localhost:8080/health || exit 1'],
                    'interval': 30,
                    'timeout': 5,
                    'retries': 3
                },
                'logConfiguration': {
                    'logDriver': 'awslogs',
                    'options': {
                        'awslogs-group': f'/aws/ecs/{config.deployment_name}',
                        'awslogs-region': config.region,
                        'awslogs-stream-prefix': 'ecs'
                    }
                }
            }]
        }
    
    async def _create_azure_manifest(self, config: AIDeploymentConfig, template: Dict[str, Any]) -> Dict[str, Any]:
        """Create Azure Container Instances manifest"""
        return {
            'location': config.region,
            'name': config.deployment_name,
            'properties': {
                'containers': [{
                    'name': 'ai-model',
                    'properties': {
                        'image': f'ainflue/ai-model:{config.model_id}',
                        'ports': [{
                            'port': 8080,
                            'protocol': 'TCP'
                        }],
                        'environmentVariables': [
                            {'name': k, 'value': v} 
                            for k, v in config.environment_variables.items()
                        ],
                        'resources': {
                            'requests': {
                                'cpu': float(config.resource_requirements.get('cpu', '1.0')),
                                'memoryInGB': float(config.resource_requirements.get('memory', '2.0'))
                            }
                        }
                    }
                }],
                'osType': 'Linux',
                'restartPolicy': 'Always',
                'ipAddress': {
                    'type': 'Public',
                    'ports': [{
                        'port': 8080,
                        'protocol': 'TCP'
                    }]
                }
            }
        }
    
    async def _create_gcp_manifest(self, config: AIDeploymentConfig, template: Dict[str, Any]) -> Dict[str, Any]:
        """Create Google Cloud Run manifest"""
        return {
            'apiVersion': 'serving.knative.dev/v1',
            'kind': 'Service',
            'metadata': {
                'name': config.deployment_name,
                'annotations': {
                    'run.googleapis.com/ingress': 'all'
                }
            },
            'spec': {
                'template': {
                    'metadata': {
                        'annotations': {
                            'autoscaling.knative.dev/minScale': str(config.min_replicas),
                            'autoscaling.knative.dev/maxScale': str(config.max_replicas),
                            'run.googleapis.com/cpu-throttling': 'false'
                        }
                    },
                    'spec': {
                        'containers': [{
                            'image': f'gcr.io/ainflue/ai-model:{config.model_id}',
                            'ports': [{
                                'containerPort': 8080
                            }],
                            'env': [
                                {'name': k, 'value': v} 
                                for k, v in config.environment_variables.items()
                            ],
                            'resources': {
                                'limits': {
                                    'cpu': config.resource_requirements.get('cpu', '1000m'),
                                    'memory': config.resource_requirements.get('memory', '2Gi')
                                }
                            }
                        }]
                    }
                }
            }
        }
    
    async def _deploy_to_kubernetes(self, config: AIDeploymentConfig, manifest: Dict[str, Any]) -> Dict[str, Any]:
        """Deploy to Kubernetes cluster"""
        try:
            # Write manifest to temporary file
            manifest_file = f"/tmp/{config.deployment_id}_manifest.yaml"
            with open(manifest_file, 'w') as f:
                yaml.dump(manifest, f)
            
            # Apply manifest using kubectl
            result = subprocess.run(
                ['kubectl', 'apply', '-f', manifest_file],
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode != 0:
                raise Exception(f"kubectl apply failed: {result.stderr}")
            
            # Create service for the deployment
            service_manifest = await self._create_kubernetes_service(config)
            service_file = f"/tmp/{config.deployment_id}_service.yaml"
            with open(service_file, 'w') as f:
                yaml.dump(service_manifest, f)
            
            service_result = subprocess.run(
                ['kubectl', 'apply', '-f', service_file],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            endpoint_url = f"http://{config.deployment_name}.ai-inference.svc.cluster.local:8080"
            
            return {
                'endpoint_url': endpoint_url,
                'logs': [
                    f"Kubernetes deployment applied: {result.stdout}",
                    f"Service created: {service_result.stdout}"
                ]
            }
            
        except Exception as e:
            raise Exception(f"Kubernetes deployment failed: {str(e)}")
    
    async def _create_kubernetes_service(self, config: AIDeploymentConfig) -> Dict[str, Any]:
        """Create Kubernetes service for deployment"""
        return {
            'apiVersion': 'v1',
            'kind': 'Service',
            'metadata': {
                'name': config.deployment_name,
                'namespace': 'ai-inference'
            },
            'spec': {
                'selector': {
                    'app': config.deployment_name
                },
                'ports': [{
                    'port': 8080,
                    'targetPort': 8080,
                    'protocol': 'TCP'
                }],
                'type': 'ClusterIP'
            }
        }
    
    async def _deploy_to_aws(self, config: AIDeploymentConfig, manifest: Dict[str, Any]) -> Dict[str, Any]:
        """Deploy to AWS ECS/Fargate"""
        # Simulate AWS deployment
        endpoint_url = f"https://{config.deployment_id}.{config.region}.elb.amazonaws.com"
        
        return {
            'endpoint_url': endpoint_url,
            'logs': [
                "ECS task definition registered",
                "ECS service created",
                "Load balancer configured",
                "Auto scaling group configured"
            ]
        }
    
    async def _deploy_to_azure(self, config: AIDeploymentConfig, manifest: Dict[str, Any]) -> Dict[str, Any]:
        """Deploy to Azure Container Instances"""
        # Simulate Azure deployment
        endpoint_url = f"https://{config.deployment_name}.{config.region}.azurecontainer.io"
        
        return {
            'endpoint_url': endpoint_url,
            'logs': [
                "Container group created",
                "Public IP assigned",
                "DNS name configured"
            ]
        }
    
    async def _deploy_to_gcp(self, config: AIDeploymentConfig, manifest: Dict[str, Any]) -> Dict[str, Any]:
        """Deploy to Google Cloud Run"""
        # Simulate GCP deployment
        endpoint_url = f"https://{config.deployment_name}-{config.region}.run.app"
        
        return {
            'endpoint_url': endpoint_url,
            'logs': [
                "Cloud Run service deployed",
                "HTTPS endpoint configured",
                "Auto scaling enabled"
            ]
        }
    
    async def _wait_for_deployment_ready(self, deployment_id: str, timeout: int = 600):
        """Wait for deployment to be ready"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            # Check deployment status
            if deployment_id in self.deployments:
                deployment = self.deployments[deployment_id]
                if deployment.status == DeploymentStatus.DEPLOYED:
                    # Simulate health check
                    await asyncio.sleep(2)
                    return True
            
            await asyncio.sleep(10)
        
        raise Exception(f"Deployment {deployment_id} did not become ready within {timeout} seconds")
    
    async def _setup_deployment_monitoring_for_deployment(self, deployment_id: str):
        """Setup monitoring for specific deployment"""
        # Simulate monitoring setup
        self.logger.info(f"Monitoring configured for deployment: {deployment_id}")
    
    async def _get_deployment_metrics(self, deployment_id: str) -> Dict[str, Any]:
        """Get current deployment metrics"""
        # Simulate metrics collection
        return {
            'requests_per_second': 45.2,
            'average_latency_ms': 89.5,
            'error_rate_percent': 0.5,
            'cpu_utilization_percent': 65.3,
            'memory_utilization_percent': 72.1,
            'active_replicas': 3
        }
    
    async def scale_deployment(self, deployment_id: str, target_replicas: int) -> bool:
        """Scale deployment to target number of replicas"""
        try:
            if deployment_id not in self.deployments:
                raise ValueError(f"Deployment not found: {deployment_id}")
            
            deployment = self.deployments[deployment_id]
            config = deployment.config
            
            # Validate replica count
            if target_replicas < config.min_replicas or target_replicas > config.max_replicas:
                raise ValueError(f"Target replicas {target_replicas} outside allowed range [{config.min_replicas}, {config.max_replicas}]")
            
            # Simulate scaling
            self.logger.info(f"Scaling deployment {deployment_id} to {target_replicas} replicas")
            
            # Update deployment status
            deployment.status = DeploymentStatus.UPDATING
            
            # Simulate scaling operation
            await asyncio.sleep(30)  # Simulate scaling time
            
            deployment.status = DeploymentStatus.DEPLOYED
            
            self.logger.info(f"Deployment scaled successfully: {deployment_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to scale deployment {deployment_id}: {e}")
            raise
    
    async def rollback_deployment(self, deployment_id: str, target_version: Optional[str] = None) -> bool:
        """Rollback deployment to previous version"""
        try:
            if deployment_id not in self.deployments:
                raise ValueError(f"Deployment not found: {deployment_id}")
            
            deployment = self.deployments[deployment_id]
            
            if not deployment.rollback_available:
                raise ValueError(f"Rollback not available for deployment: {deployment_id}")
            
            # Update deployment status
            deployment.status = DeploymentStatus.ROLLING_BACK
            
            self.logger.info(f"Rolling back deployment: {deployment_id}")
            
            # Simulate rollback operation
            await asyncio.sleep(60)  # Simulate rollback time
            
            deployment.status = DeploymentStatus.DEPLOYED
            
            self.logger.info(f"Deployment rolled back successfully: {deployment_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to rollback deployment {deployment_id}: {e}")
            raise
    
    async def terminate_deployment(self, deployment_id: str) -> bool:
        """Terminate deployment"""
        try:
            if deployment_id not in self.deployments:
                raise ValueError(f"Deployment not found: {deployment_id}")
            
            deployment = self.deployments[deployment_id]
            
            self.logger.info(f"Terminating deployment: {deployment_id}")
            
            # Update deployment status
            deployment.status = DeploymentStatus.TERMINATED
            deployment.end_time = datetime.now()
            
            # Simulate termination
            await asyncio.sleep(15)
            
            self.logger.info(f"Deployment terminated successfully: {deployment_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to terminate deployment {deployment_id}: {e}")
            raise
    
    def get_deployment_status(self, deployment_id: str) -> Optional[DeploymentResult]:
        """Get deployment status"""
        return self.deployments.get(deployment_id)
    
    def list_deployments(self, model_id: Optional[str] = None) -> List[DeploymentResult]:
        """List deployments, optionally filtered by model ID"""
        if model_id:
            return [d for d in self.deployments.values() if d.config.model_id == model_id]
        return list(self.deployments.values())
    
    def get_deployment_history(self, model_id: str) -> List[DeploymentResult]:
        """Get deployment history for model"""
        return self.deployment_history.get(model_id, [])
    
    async def get_deployment_logs(self, deployment_id: str) -> List[str]:
        """Get deployment logs"""
        if deployment_id in self.deployments:
            return self.deployments[deployment_id].logs
        return []
    
    async def get_deployment_metrics_history(self, deployment_id: str, hours: int = 24) -> List[DeploymentMetrics]:
        """Get deployment metrics history"""
        # Simulate metrics history
        metrics_history = []
        current_time = datetime.now()
        
        for i in range(hours):
            timestamp = current_time - timedelta(hours=i)
            metrics = DeploymentMetrics(
                deployment_id=deployment_id,
                requests_per_second=40.0 + (i % 10),
                average_latency_ms=85.0 + (i % 20),
                error_rate_percent=0.5 + (i % 3) * 0.1,
                cpu_utilization_percent=60.0 + (i % 15),
                memory_utilization_percent=70.0 + (i % 10),
                active_replicas=3 + (i % 3),
                timestamp=timestamp
            )
            metrics_history.append(metrics)
        
        return metrics_history
    
    async def generate_deployment_report(self) -> Dict[str, Any]:
        """Generate deployment status report"""
        total_deployments = len(self.deployments)
        
        status_counts = {}
        for deployment in self.deployments.values():
            status = deployment.status.value
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Calculate average deployment time
        successful_deployments = [d for d in self.deployments.values() if d.status == DeploymentStatus.DEPLOYED and d.duration_seconds]
        avg_deployment_time = sum(d.duration_seconds for d in successful_deployments) / len(successful_deployments) if successful_deployments else 0
        
        return {
            'summary': {
                'total_deployments': total_deployments,
                'status_distribution': status_counts,
                'success_rate': f"{(status_counts.get('deployed', 0)/total_deployments*100):.1f}%" if total_deployments > 0 else "0%",
                'avg_deployment_time_seconds': round(avg_deployment_time, 2)
            },
            'cloud_provider_distribution': self._get_cloud_provider_distribution(),
            'deployment_types': self._get_deployment_type_distribution(),
            'recommendations': self._generate_deployment_recommendations(),
            'generated_at': datetime.now().isoformat()
        }
    
    def _get_cloud_provider_distribution(self) -> Dict[str, int]:
        """Get distribution of deployments by cloud provider"""
        distribution = {}
        for deployment in self.deployments.values():
            provider = deployment.config.cloud_provider.value
            distribution[provider] = distribution.get(provider, 0) + 1
        return distribution
    
    def _get_deployment_type_distribution(self) -> Dict[str, int]:
        """Get distribution of deployments by type"""
        distribution = {}
        for deployment in self.deployments.values():
            dep_type = deployment.config.deployment_type.value
            distribution[dep_type] = distribution.get(dep_type, 0) + 1
        return distribution
    
    def _generate_deployment_recommendations(self) -> List[str]:
        """Generate deployment recommendations"""
        recommendations = []
        
        failed_deployments = [d for d in self.deployments.values() if d.status == DeploymentStatus.FAILED]
        if len(failed_deployments) > 0:
            recommendations.append("Investigate and fix failed deployments")
        
        # Check for single points of failure
        single_replica_deployments = [d for d in self.deployments.values() if d.config.min_replicas == 1]
        if len(single_replica_deployments) > 0:
            recommendations.append("Consider increasing minimum replicas for high availability")
        
        # Check for resource optimization
        high_cpu_deployments = []  # Would analyze actual metrics
        if high_cpu_deployments:
            recommendations.append("Optimize resource allocation for high CPU utilization deployments")
        
        return recommendations or ["Deployment infrastructure is well configured"]

# Service instance
ai_deployment_manager = AIDeploymentManager()