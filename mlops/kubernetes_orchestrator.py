"""
Kubernetes Orchestrator module
Enterprise implementation for Ainflue platform
"""

#!/usr/bin/env python3
"""
☸️ MLOps Kubernetes Orchestrator - Cloud-Native ML Deployment

Orchestrateur Kubernetes pour déploiements ML cloud-native enterprise.
Gestion complète du cycle de vie des workloads ML avec auto-scaling et monitoring.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
Role: DevOps Expert + Backend Senior + Infrastructure Architect
"""

import asyncio
import yaml
import json
import time
import hashlib
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple
import logging
from pathlib import Path
import base64

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WorkloadType(Enum):
    """Types de workloads ML"""
    TRAINING = "training"
    INFERENCE = "inference"
    BATCH_PROCESSING = "batch_processing"
    PIPELINE = "pipeline"
    NOTEBOOK = "notebook"
    MONITORING = "monitoring"


class DeploymentStrategy(Enum):
    """Stratégies de déploiement"""
    ROLLING_UPDATE = "rolling_update"
    BLUE_GREEN = "blue_green"
    CANARY = "canary"
    RECREATE = "recreate"


class ResourceType(Enum):
    """Types de ressources Kubernetes"""
    DEPLOYMENT = "Deployment"
    SERVICE = "Service"
    CONFIGMAP = "ConfigMap"
    SECRET = "Secret"
    INGRESS = "Ingress"
    HPA = "HorizontalPodAutoscaler"
    VPA = "VerticalPodAutoscaler"
    JOB = "Job"
    CRONJOB = "CronJob"
    STATEFULSET = "StatefulSet"


@dataclass
class ResourceRequirements:
    """Spécifications de ressources"""
    cpu_request: str = "100m"
    cpu_limit: str = "1000m"
    memory_request: str = "128Mi"
    memory_limit: str = "1Gi"
    gpu_count: int = 0
    gpu_type: str = "nvidia.com/gpu"
    storage_size: str = "10Gi"
    storage_class: str = "fast-ssd"


@dataclass
class AutoScalingConfig:
    """Configuration d'auto-scaling"""
    enabled: bool = True
    min_replicas: int = 1
    max_replicas: int = 10
    target_cpu_percentage: int = 70
    target_memory_percentage: int = 80
    custom_metrics: Dict[str, Any] = field(default_factory=dict)
    scale_down_delay: int = 300  # seconds
    scale_up_delay: int = 60     # seconds


@dataclass
class SecurityContext:
    """Contexte de sécurité pour pods"""
    run_as_non_root: bool = True
    run_as_user: int = 1000
    run_as_group: int = 1000
    fs_group: int = 1000
    read_only_root_filesystem: bool = True
    allow_privilege_escalation: bool = False
    drop_capabilities: List[str] = field(default_factory=lambda: ["ALL"])
    add_capabilities: List[str] = field(default_factory=list)


@dataclass
class MLWorkload:
    """Définition d'un workload ML"""
    name: str
    workload_type: WorkloadType
    image: str
    command: List[str] = field(default_factory=list)
    args: List[str] = field(default_factory=list)
    environment_variables: Dict[str, str] = field(default_factory=dict)
    secrets: Dict[str, str] = field(default_factory=dict)
    resource_requirements: ResourceRequirements = field(default_factory=ResourceRequirements)
    auto_scaling: AutoScalingConfig = field(default_factory=AutoScalingConfig)
    security_context: SecurityContext = field(default_factory=SecurityContext)
    volumes: List[Dict[str, Any]] = field(default_factory=list)
    labels: Dict[str, str] = field(default_factory=dict)
    annotations: Dict[str, str] = field(default_factory=dict)
    deployment_strategy: DeploymentStrategy = DeploymentStrategy.ROLLING_UPDATE
    namespace: str = "mlops"
    service_port: int = 8080
    health_check_path: str = "/health"
    readiness_check_path: str = "/ready"


@dataclass
class DeploymentStatus:
    """Statut d'un déploiement"""
    name: str
    namespace: str
    status: str
    replicas: int
    ready_replicas: int
    updated_replicas: int
    available_replicas: int
    created_at: datetime
    last_updated: datetime
    conditions: List[Dict[str, Any]] = field(default_factory=list)
    events: List[Dict[str, Any]] = field(default_factory=list)


class KubernetesClient:
    """Client Kubernetes simplifié pour demo"""
    
    def __init__(self, config_path -> None: Optional[str] = None) -> None:
        self.config_path = config_path
        self.cluster_info = {
            "name": "mlops-cluster",
            "version": "v1.28.0",
            "nodes": 5,
            "namespaces": ["default", "mlops", "monitoring", "logging"]
        }
        
        # Simulated cluster state
        self.deployments: Dict[str, Dict[str, Any]] = {}
        self.services: Dict[str, Dict[str, Any]] = {}
        self.configmaps: Dict[str, Dict[str, Any]] = {}
        self.secrets: Dict[str, Dict[str, Any]] = {}
    
    async def apply_manifest(self, manifest: Dict[str, Any]) -> bool:
        """Apply Kubernetes manifest"""
        try:
            resource_type = manifest.get('kind')
            metadata = manifest.get('metadata', {})
            name = metadata.get('name')
            namespace = metadata.get('namespace', 'default')
            
            resource_key = f"{namespace}/{name}"
            
            if resource_type == "Deployment":
                self.deployments[resource_key] = manifest
            elif resource_type == "Service":
                self.services[resource_key] = manifest
            elif resource_type == "ConfigMap":
                self.configmaps[resource_key] = manifest
            elif resource_type == "Secret":
                self.secrets[resource_key] = manifest
            
            logger.info(f"✅ Applied {resource_type}/{name} in namespace {namespace}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to apply manifest: {e}")
            return False
    
    async def get_deployment_status(self, name: str, namespace: str = "default") -> Optional[DeploymentStatus]:
        """Get deployment status"""
        resource_key = f"{namespace}/{name}"
        deployment = self.deployments.get(resource_key)
        
        if not deployment:
            return None
        
        # Simulate deployment status
        return DeploymentStatus(
            name=name,
            namespace=namespace,
            status="Running",
            replicas=3,
            ready_replicas=3,
            updated_replicas=3,
            available_replicas=3,
            created_at=datetime.now() - timedelta(hours=1),
            last_updated=datetime.now()
        )
    
    async def scale_deployment(self, name: str, replicas: int, namespace: str = "default") -> bool:
        """Scale deployment"""
        resource_key = f"{namespace}/{name}"
        deployment = self.deployments.get(resource_key)
        
        if not deployment:
            return False
        
        # Update replicas in manifest
        deployment['spec']['replicas'] = replicas
        logger.info(f"📈 Scaled deployment {name} to {replicas} replicas")
        return True
    
    async def delete_resource(self, resource_type: str, name: str, namespace: str = "default") -> bool:
        """Delete Kubernetes resource"""
        resource_key = f"{namespace}/{name}"
        
        if resource_type == "Deployment" and resource_key in self.deployments:
            del self.deployments[resource_key]
        elif resource_type == "Service" and resource_key in self.services:
            del self.services[resource_key]
        elif resource_type == "ConfigMap" and resource_key in self.configmaps:
            del self.configmaps[resource_key]
        elif resource_type == "Secret" and resource_key in self.secrets:
            del self.secrets[resource_key]
        else:
            return False
        
        logger.info(f"🗑️ Deleted {resource_type}/{name} from namespace {namespace}")
        return True
    
    async def get_cluster_info(self) -> Dict[str, Any]:
        """Get cluster information"""
        return self.cluster_info
    
    async def get_resource_usage(self, namespace: str = "mlops") -> Dict[str, Any]:
        """Get resource usage metrics"""
        # Simulate resource usage
        return {
            "cpu_usage": "2.5 cores",
            "memory_usage": "8.2 GB",
            "gpu_usage": "2/4 GPUs",
            "storage_usage": "150 GB",
            "pod_count": len(self.deployments),
            "namespace": namespace
        }


class KubernetesOrchestrator:
    """
    ☸️ Orchestrateur Kubernetes enterprise pour MLOps
    
    Fonctionnalités:
    - Déploiement automatisé de workloads ML
    - Auto-scaling intelligent avec métriques custom
    - Multi-strategy deployment (blue-green, canary, rolling)
    - Resource management optimisé pour ML
    - Security best practices enforcement
    - Monitoring et observability integration
    - Multi-tenant namespace management
    - GPU/TPU resource allocation
    """
    
    def __init__(self, config -> None: Optional[Dict[str, Any]] = None) -> None:
        self.config = config or {}
        self.client = KubernetesClient(self.config.get('kubeconfig_path'))
        self.default_namespace = self.config.get('default_namespace', 'mlops')
        
        # Deployment tracking
        self.active_deployments: Dict[str, MLWorkload] = {}
        self.deployment_history: List[Dict[str, Any]] = []
        
        # Resource templates
        self.resource_templates = {
            'training': self._get_training_template(),
            'inference': self._get_inference_template(),
            'batch_processing': self._get_batch_template()
        }
        
        logger.info("☸️ Kubernetes Orchestrator initialized for enterprise ML deployments")
    
    def _get_training_template(self) -> Dict[str, Any]:
        """Template pour workloads d'entraînement"""
        return {
            'resource_requirements': ResourceRequirements(
                cpu_request="2000m",
                cpu_limit="4000m",
                memory_request="4Gi",
                memory_limit="16Gi",
                gpu_count=1,
                storage_size="100Gi"
            ),
            'auto_scaling': AutoScalingConfig(
                enabled=False,  # Training jobs typically don't auto-scale
                min_replicas=1,
                max_replicas=1
            )
        }
    
    def _get_inference_template(self) -> Dict[str, Any]:
        """Template pour services d'inférence"""
        return {
            'resource_requirements': ResourceRequirements(
                cpu_request="500m",
                cpu_limit="2000m",
                memory_request="1Gi",
                memory_limit="4Gi",
                gpu_count=0,  # CPU inference by default
                storage_size="20Gi"
            ),
            'auto_scaling': AutoScalingConfig(
                enabled=True,
                min_replicas=2,
                max_replicas=20,
                target_cpu_percentage=70,
                target_memory_percentage=80
            )
        }
    
    def _get_batch_template(self) -> Dict[str, Any]:
        """Template pour traitement batch"""
        return {
            'resource_requirements': ResourceRequirements(
                cpu_request="1000m",
                cpu_limit="4000m",
                memory_request="2Gi",
                memory_limit="8Gi",
                storage_size="50Gi"
            ),
            'auto_scaling': AutoScalingConfig(
                enabled=True,
                min_replicas=1,
                max_replicas=10,
                target_cpu_percentage=80
            )
        }
    
    async def deploy_ml_workload(self, workload: MLWorkload) -> bool:
        """Déploie un workload ML sur Kubernetes"""
        try:
            logger.info(f"🚀 Deploying ML workload: {workload.name} ({workload.workload_type.value})")
            
            # Apply template defaults
            if workload.workload_type.value in self.resource_templates:
                template = self.resource_templates[workload.workload_type.value]
                self._apply_template_defaults(workload, template)
            
            # Create namespace if it doesn't exist
            await self._ensure_namespace(workload.namespace)
            
            # Generate Kubernetes manifests
            manifests = await self._generate_manifests(workload)
            
            # Apply manifests
            for manifest in manifests:
                success = await self.client.apply_manifest(manifest)
                if not success:
                    raise Exception(f"Failed to apply {manifest['kind']} manifest")
            
            # Track deployment
            self.active_deployments[f"{workload.namespace}/{workload.name}"] = workload
            
            # Record deployment history
            self.deployment_history.append({
                'workload_name': workload.name,
                'workload_type': workload.workload_type.value,
                'namespace': workload.namespace,
                'deployed_at': datetime.now(),
                'strategy': workload.deployment_strategy.value,
                'status': 'deployed'
            })
            
            logger.info(f"✅ Successfully deployed {workload.name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to deploy workload {workload.name}: {e}")
            
            # Record failed deployment
            self.deployment_history.append({
                'workload_name': workload.name,
                'workload_type': workload.workload_type.value,
                'namespace': workload.namespace,
                'deployed_at': datetime.now(),
                'strategy': workload.deployment_strategy.value,
                'status': 'failed',
                'error': str(e)
            })
            
            return False
    
    def _apply_template_defaults(self, workload -> None: MLWorkload, template -> None: Dict[str, Any]) -> None:
        """Apply template defaults to workload"""
        if 'resource_requirements' in template:
            template_resources = template['resource_requirements']
            for attr in ['cpu_request', 'cpu_limit', 'memory_request', 'memory_limit', 'gpu_count', 'storage_size']:
                if not getattr(workload.resource_requirements, attr, None):
                    setattr(workload.resource_requirements, attr, getattr(template_resources, attr))
        
        if 'auto_scaling' in template:
            template_scaling = template['auto_scaling']
            for attr in ['enabled', 'min_replicas', 'max_replicas', 'target_cpu_percentage']:
                if not getattr(workload.auto_scaling, attr, None):
                    setattr(workload.auto_scaling, attr, getattr(template_scaling, attr))
    
    async def _ensure_namespace(self, namespace -> None: str) -> None:
        """Ensure namespace exists"""
        namespace_manifest = {
            'apiVersion': 'v1',
            'kind': 'Namespace',
            'metadata': {
                'name': namespace,
                'labels': {
                    'managed-by': 'mlops-orchestrator',
                    'purpose': 'ml-workloads'
                }
            }
        }
        
        await self.client.apply_manifest(namespace_manifest)
    
    async def _generate_manifests(self, workload: MLWorkload) -> List[Dict[str, Any]]:
        """Generate Kubernetes manifests for workload"""
        manifests = []
        
        # ConfigMap for environment variables
        if workload.environment_variables:
            configmap = self._generate_configmap(workload)
            manifests.append(configmap)
        
        # Secrets
        if workload.secrets:
            secret = self._generate_secret(workload)
            manifests.append(secret)
        
        # Main workload resource (Deployment, Job, etc.)
        if workload.workload_type in [WorkloadType.INFERENCE, WorkloadType.MONITORING]:
            deployment = self._generate_deployment(workload)
            manifests.append(deployment)
            
            # Service for inference workloads
            if workload.workload_type == WorkloadType.INFERENCE:
                service = self._generate_service(workload)
                manifests.append(service)
                
                # HPA for auto-scaling
                if workload.auto_scaling.enabled:
                    hpa = self._generate_hpa(workload)
                    manifests.append(hpa)
        
        elif workload.workload_type in [WorkloadType.TRAINING, WorkloadType.BATCH_PROCESSING]:
            job = self._generate_job(workload)
            manifests.append(job)
        
        elif workload.workload_type == WorkloadType.PIPELINE:
            # For pipelines, create multiple jobs
            pipeline_jobs = self._generate_pipeline_jobs(workload)
            manifests.extend(pipeline_jobs)
        
        return manifests
    
    def _generate_configmap(self, workload: MLWorkload) -> Dict[str, Any]:
        """Generate ConfigMap manifest"""
        return {
            'apiVersion': 'v1',
            'kind': 'ConfigMap',
            'metadata': {
                'name': f"{workload.name}-config",
                'namespace': workload.namespace,
                'labels': {
                    'app': workload.name,
                    'workload-type': workload.workload_type.value,
                    'managed-by': 'mlops-orchestrator'
                }
            },
            'data': workload.environment_variables
        }
    
    def _generate_secret(self, workload: MLWorkload) -> Dict[str, Any]:
        """Generate Secret manifest"""
        # Encode secrets in base64
        encoded_secrets = {}
        for key, value in workload.secrets.items():
            encoded_secrets[key] = base64.b64encode(value.encode()).decode()
        
        return {
            'apiVersion': 'v1',
            'kind': 'Secret',
            'metadata': {
                'name': f"{workload.name}-secrets",
                'namespace': workload.namespace,
                'labels': {
                    'app': workload.name,
                    'workload-type': workload.workload_type.value,
                    'managed-by': 'mlops-orchestrator'
                }
            },
            'type': 'Opaque',
            'data': encoded_secrets
        }
    
    def _generate_deployment(self, workload: MLWorkload) -> Dict[str, Any]:
        """Generate Deployment manifest"""
        pod_spec = self._generate_pod_spec(workload)
        
        return {
            'apiVersion': 'apps/v1',
            'kind': 'Deployment',
            'metadata': {
                'name': workload.name,
                'namespace': workload.namespace,
                'labels': {
                    'app': workload.name,
                    'workload-type': workload.workload_type.value,
                    'managed-by': 'mlops-orchestrator',
                    **workload.labels
                },
                'annotations': workload.annotations
            },
            'spec': {
                'replicas': workload.auto_scaling.min_replicas,
                'strategy': {
                    'type': 'RollingUpdate' if workload.deployment_strategy == DeploymentStrategy.ROLLING_UPDATE else 'Recreate',
                    'rollingUpdate': {
                        'maxUnavailable': '25%',
                        'maxSurge': '25%'
                    } if workload.deployment_strategy == DeploymentStrategy.ROLLING_UPDATE else None
                },
                'selector': {
                    'matchLabels': {
                        'app': workload.name
                    }
                },
                'template': {
                    'metadata': {
                        'labels': {
                            'app': workload.name,
                            'workload-type': workload.workload_type.value,
                            **workload.labels
                        }
                    },
                    'spec': pod_spec
                }
            }
        }
    
    def _generate_job(self, workload: MLWorkload) -> Dict[str, Any]:
        """Generate Job manifest"""
        pod_spec = self._generate_pod_spec(workload)
        
        return {
            'apiVersion': 'batch/v1',
            'kind': 'Job',
            'metadata': {
                'name': workload.name,
                'namespace': workload.namespace,
                'labels': {
                    'app': workload.name,
                    'workload-type': workload.workload_type.value,
                    'managed-by': 'mlops-orchestrator',
                    **workload.labels
                }
            },
            'spec': {
                'backoffLimit': 3,
                'completions': 1,
                'parallelism': 1,
                'template': {
                    'metadata': {
                        'labels': {
                            'app': workload.name,
                            'workload-type': workload.workload_type.value
                        }
                    },
                    'spec': {
                        **pod_spec,
                        'restartPolicy': 'Never'
                    }
                }
            }
        }
    
    def _generate_pod_spec(self, workload: MLWorkload) -> Dict[str, Any]:
        """Generate pod specification"""
        container_spec = {
            'name': workload.name,
            'image': workload.image,
            'resources': {
                'requests': {
                    'cpu': workload.resource_requirements.cpu_request,
                    'memory': workload.resource_requirements.memory_request
                },
                'limits': {
                    'cpu': workload.resource_requirements.cpu_limit,
                    'memory': workload.resource_requirements.memory_limit
                }
            },
            'securityContext': {
                'runAsNonRoot': workload.security_context.run_as_non_root,
                'runAsUser': workload.security_context.run_as_user,
                'runAsGroup': workload.security_context.run_as_group,
                'readOnlyRootFilesystem': workload.security_context.read_only_root_filesystem,
                'allowPrivilegeEscalation': workload.security_context.allow_privilege_escalation,
                'capabilities': {
                    'drop': workload.security_context.drop_capabilities,
                    'add': workload.security_context.add_capabilities
                }
            }
        }
        
        # Add GPU resources if needed
        if workload.resource_requirements.gpu_count > 0:
            container_spec['resources']['limits'][workload.resource_requirements.gpu_type] = workload.resource_requirements.gpu_count
        
        # Add command and args
        if workload.command:
            container_spec['command'] = workload.command
        if workload.args:
            container_spec['args'] = workload.args
        
        # Add environment variables from ConfigMap
        if workload.environment_variables:
            container_spec['envFrom'] = [{
                'configMapRef': {
                    'name': f"{workload.name}-config"
                }
            }]
        
        # Add secrets
        if workload.secrets:
            if 'envFrom' not in container_spec:
                container_spec['envFrom'] = []
            container_spec['envFrom'].append({
                'secretRef': {
                    'name': f"{workload.name}-secrets"
                }
            })
        
        # Add health checks for long-running services
        if workload.workload_type in [WorkloadType.INFERENCE, WorkloadType.MONITORING]:
            container_spec['livenessProbe'] = {
                'httpGet': {
                    'path': workload.health_check_path,
                    'port': workload.service_port
                },
                'initialDelaySeconds': 30,
                'periodSeconds': 10
            }
            
            container_spec['readinessProbe'] = {
                'httpGet': {
                    'path': workload.readiness_check_path,
                    'port': workload.service_port
                },
                'initialDelaySeconds': 5,
                'periodSeconds': 5
            }
        
        # Pod specification
        pod_spec = {
            'containers': [container_spec],
            'securityContext': {
                'fsGroup': workload.security_context.fs_group
            }
        }
        
        # Add volumes if specified
        if workload.volumes:
            pod_spec['volumes'] = workload.volumes
            # Add volume mounts to container
            volume_mounts = []
            for volume in workload.volumes:
                volume_mounts.append({
                    'name': volume['name'],
                    'mountPath': volume.get('mountPath', f"/mnt/{volume['name']}")
                })
            container_spec['volumeMounts'] = volume_mounts
        
        return pod_spec
    
    def _generate_service(self, workload: MLWorkload) -> Dict[str, Any]:
        """Generate Service manifest"""
        return {
            'apiVersion': 'v1',
            'kind': 'Service',
            'metadata': {
                'name': f"{workload.name}-service",
                'namespace': workload.namespace,
                'labels': {
                    'app': workload.name,
                    'workload-type': workload.workload_type.value,
                    'managed-by': 'mlops-orchestrator'
                }
            },
            'spec': {
                'selector': {
                    'app': workload.name
                },
                'ports': [{
                    'port': 80,
                    'targetPort': workload.service_port,
                    'protocol': 'TCP'
                }],
                'type': 'ClusterIP'
            }
        }
    
    def _generate_hpa(self, workload: MLWorkload) -> Dict[str, Any]:
        """Generate HorizontalPodAutoscaler manifest"""
        return {
            'apiVersion': 'autoscaling/v2',
            'kind': 'HorizontalPodAutoscaler',
            'metadata': {
                'name': f"{workload.name}-hpa",
                'namespace': workload.namespace,
                'labels': {
                    'app': workload.name,
                    'managed-by': 'mlops-orchestrator'
                }
            },
            'spec': {
                'scaleTargetRef': {
                    'apiVersion': 'apps/v1',
                    'kind': 'Deployment',
                    'name': workload.name
                },
                'minReplicas': workload.auto_scaling.min_replicas,
                'maxReplicas': workload.auto_scaling.max_replicas,
                'metrics': [
                    {
                        'type': 'Resource',
                        'resource': {
                            'name': 'cpu',
                            'target': {
                                'type': 'Utilization',
                                'averageUtilization': workload.auto_scaling.target_cpu_percentage
                            }
                        }
                    },
                    {
                        'type': 'Resource',
                        'resource': {
                            'name': 'memory',
                            'target': {
                                'type': 'Utilization',
                                'averageUtilization': workload.auto_scaling.target_memory_percentage
                            }
                        }
                    }
                ],
                'behavior': {
                    'scaleDown': {
                        'stabilizationWindowSeconds': workload.auto_scaling.scale_down_delay
                    },
                    'scaleUp': {
                        'stabilizationWindowSeconds': workload.auto_scaling.scale_up_delay
                    }
                }
            }
        }
    
    def _generate_pipeline_jobs(self, workload: MLWorkload) -> List[Dict[str, Any]]:
        """Generate multiple jobs for pipeline workload"""
        # This is a simplified example - in production, would use workflow engines like Argo Workflows
        jobs = []
        
        pipeline_steps = [
            "data-preprocessing",
            "feature-engineering", 
            "model-training",
            "model-validation",
            "model-deployment"
        ]
        
        for i, step in enumerate(pipeline_steps):
            step_workload = MLWorkload(
                name=f"{workload.name}-{step}",
                workload_type=WorkloadType.TRAINING,
                image=workload.image,
                command=workload.command + [f"--step={step}"],
                environment_variables=workload.environment_variables,
                resource_requirements=workload.resource_requirements,
                security_context=workload.security_context,
                namespace=workload.namespace
            )
            
            job = self._generate_job(step_workload)
            jobs.append(job)
        
        return jobs
    
    async def scale_workload(self, name: str, replicas: int, namespace: str = None) -> bool:
        """Scale a workload"""
        namespace = namespace or self.default_namespace
        
        try:
            success = await self.client.scale_deployment(name, replicas, namespace)
            if success:
                # Update tracking
                workload_key = f"{namespace}/{name}"
                if workload_key in self.active_deployments:
                    self.active_deployments[workload_key].auto_scaling.min_replicas = replicas
                
                logger.info(f"📈 Scaled workload {name} to {replicas} replicas")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Failed to scale workload {name}: {e}")
            return False
    
    async def update_workload(self, workload: MLWorkload, strategy: DeploymentStrategy = None) -> bool:
        """Update an existing workload"""
        strategy = strategy or workload.deployment_strategy
        
        try:
            logger.info(f"🔄 Updating workload {workload.name} with {strategy.value} strategy")
            
            if strategy == DeploymentStrategy.BLUE_GREEN:
                return await self._blue_green_update(workload)
            elif strategy == DeploymentStrategy.CANARY:
                return await self._canary_update(workload)
            else:
                # Rolling update (default)
                return await self.deploy_ml_workload(workload)
                
        except Exception as e:
            logger.error(f"❌ Failed to update workload {workload.name}: {e}")
            return False
    
    async def _blue_green_update(self, workload: MLWorkload) -> bool:
        """Perform blue-green deployment"""
        # Create green deployment
        green_workload = workload
        green_workload.name = f"{workload.name}-green"
        
        # Deploy green version
        success = await self.deploy_ml_workload(green_workload)
        if not success:
            return False
        
        # Wait for green to be ready (simplified)
        await asyncio.sleep(10)
        
        # Switch traffic to green (update service selector)
        # In production, this would update the service selector
        logger.info(f"🔄 Switching traffic to green deployment: {green_workload.name}")
        
        # Remove blue deployment
        await self.delete_workload(workload.name.replace("-green", ""), workload.namespace)
        
        # Rename green to original name (simplified)
        workload.name = workload.name.replace("-green", "")
        
        return True
    
    async def _canary_update(self, workload: MLWorkload) -> bool:
        """Perform canary deployment"""
        # Create canary deployment with reduced replicas
        canary_workload = workload
        canary_workload.name = f"{workload.name}-canary"
        canary_workload.auto_scaling.min_replicas = 1  # Start with 1 replica
        
        # Deploy canary version
        success = await self.deploy_ml_workload(canary_workload)
        if not success:
            return False
        
        # Monitor canary for a period (simplified)
        logger.info(f"📊 Monitoring canary deployment: {canary_workload.name}")
        await asyncio.sleep(30)
        
        # If successful, gradually increase canary traffic
        for percentage in [10, 25, 50, 75, 100]:
            logger.info(f"📈 Increasing canary traffic to {percentage}%")
            await asyncio.sleep(10)
        
        # Replace original with canary
        await self.delete_workload(workload.name.replace("-canary", ""), workload.namespace)
        workload.name = workload.name.replace("-canary", "")
        
        return True
    
    async def delete_workload(self, name: str, namespace: str = None) -> bool:
        """Delete a workload and its resources"""
        namespace = namespace or self.default_namespace
        
        try:
            logger.info(f"🗑️ Deleting workload: {name}")
            
            # Delete associated resources
            resources_to_delete = [
                ("Deployment", name),
                ("Job", name),
                ("Service", f"{name}-service"),
                ("HorizontalPodAutoscaler", f"{name}-hpa"),
                ("ConfigMap", f"{name}-config"),
                ("Secret", f"{name}-secrets")
            ]
            
            for resource_type, resource_name in resources_to_delete:
                await self.client.delete_resource(resource_type, resource_name, namespace)
            
            # Remove from tracking
            workload_key = f"{namespace}/{name}"
            if workload_key in self.active_deployments:
                del self.active_deployments[workload_key]
            
            # Record deletion
            self.deployment_history.append({
                'workload_name': name,
                'namespace': namespace,
                'deleted_at': datetime.now(),
                'status': 'deleted'
            })
            
            logger.info(f"✅ Successfully deleted workload {name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to delete workload {name}: {e}")
            return False
    
    async def get_workload_status(self, name: str, namespace: str = None) -> Optional[DeploymentStatus]:
        """Get workload status"""
        namespace = namespace or self.default_namespace
        return await self.client.get_deployment_status(name, namespace)
    
    async def list_workloads(self, namespace: str = None) -> List[Dict[str, Any]]:
        """List all managed workloads"""
        if namespace:
            filtered_workloads = {
                k: v for k, v in self.active_deployments.items()
                if k.startswith(f"{namespace}/")
            }
        else:
            filtered_workloads = self.active_deployments
        
        workload_list = []
        for key, workload in filtered_workloads.items():
            status = await self.get_workload_status(workload.name, workload.namespace)
            
            workload_list.append({
                'name': workload.name,
                'namespace': workload.namespace,
                'workload_type': workload.workload_type.value,
                'image': workload.image,
                'status': status.status if status else 'Unknown',
                'replicas': status.replicas if status else 0,
                'ready_replicas': status.ready_replicas if status else 0
            })
        
        return workload_list
    
    async def get_cluster_metrics(self) -> Dict[str, Any]:
        """Get cluster-wide metrics"""
        cluster_info = await self.client.get_cluster_info()
        resource_usage = await self.client.get_resource_usage()
        
        return {
            'cluster_info': cluster_info,
            'resource_usage': resource_usage,
            'active_workloads': len(self.active_deployments),
            'total_deployments': len(self.deployment_history),
            'deployment_success_rate': self._calculate_success_rate()
        }
    
    def _calculate_success_rate(self) -> float:
        """Calculate deployment success rate"""
        if not self.deployment_history:
            return 0.0
        
        successful_deployments = len([
            d for d in self.deployment_history 
            if d.get('status') == 'deployed'
        ])
        
        return (successful_deployments / len(self.deployment_history)) * 100
    
    async def export_workload_config(self, name: str, namespace: str = None) -> Dict[str, Any]:
        """Export workload configuration as YAML"""
        namespace = namespace or self.default_namespace
        workload_key = f"{namespace}/{name}"
        
        if workload_key not in self.active_deployments:
            return {}
        
        workload = self.active_deployments[workload_key]
        manifests = await self._generate_manifests(workload)
        
        return {
            'workload_config': {
                'name': workload.name,
                'workload_type': workload.workload_type.value,
                'image': workload.image,
                'resource_requirements': {
                    'cpu_request': workload.resource_requirements.cpu_request,
                    'cpu_limit': workload.resource_requirements.cpu_limit,
                    'memory_request': workload.resource_requirements.memory_request,
                    'memory_limit': workload.resource_requirements.memory_limit,
                    'gpu_count': workload.resource_requirements.gpu_count
                },
                'auto_scaling': {
                    'enabled': workload.auto_scaling.enabled,
                    'min_replicas': workload.auto_scaling.min_replicas,
                    'max_replicas': workload.auto_scaling.max_replicas
                }
            },
            'kubernetes_manifests': manifests
        }


# Demo function
async def demo_kubernetes_orchestrator() -> None:
    """Démonstration de l'orchestrateur Kubernetes"""
    print("☸️ MLOps Kubernetes Orchestrator Demo")
    
    # Initialize orchestrator
    orchestrator = KubernetesOrchestrator({
        'default_namespace': 'mlops-demo'
    })
    
    # Create inference workload
    inference_workload = MLWorkload(
        name="sentiment-analyzer",
        workload_type=WorkloadType.INFERENCE,
        image="ainflue/sentiment-analyzer:v1.0.0",
        command=["python", "app.py"],
        environment_variables={
            "MODEL_PATH": "/models/sentiment",
            "LOG_LEVEL": "INFO",
            "PORT": "8080"
        },
        secrets={
            "API_KEY": "secret-api-key-123",
            "DB_PASSWORD": "secure-password"
        },
        resource_requirements=ResourceRequirements(
            cpu_request="200m",
            cpu_limit="500m",
            memory_request="256Mi",
            memory_limit="512Mi"
        ),
        auto_scaling=AutoScalingConfig(
            enabled=True,
            min_replicas=2,
            max_replicas=8,
            target_cpu_percentage=70
        ),
        namespace="mlops-demo"
    )
    
    # Deploy inference workload
    print(f"🚀 Deploying inference workload...")
    success = await orchestrator.deploy_ml_workload(inference_workload)
    print(f"✅ Deployment {'successful' if success else 'failed'}")
    
    # Create training workload
    training_workload = MLWorkload(
        name="model-training-job",
        workload_type=WorkloadType.TRAINING,
        image="ainflue/trainer:v1.0.0",
        command=["python", "train.py"],
        args=["--epochs=100", "--batch-size=32"],
        environment_variables={
            "DATASET_PATH": "/data/training",
            "OUTPUT_PATH": "/models/output"
        },
        resource_requirements=ResourceRequirements(
            cpu_request="2000m",
            cpu_limit="4000m",
            memory_request="4Gi",
            memory_limit="8Gi",
            gpu_count=1
        ),
        namespace="mlops-demo"
    )
    
    # Deploy training workload
    print(f"🤖 Deploying training workload...")
    success = await orchestrator.deploy_ml_workload(training_workload)
    print(f"✅ Training job {'deployed' if success else 'failed'}")
    
    # List workloads
    print(f"\n📋 Listing workloads...")
    workloads = await orchestrator.list_workloads("mlops-demo")
    for workload in workloads:
        print(f"  - {workload['name']} ({workload['workload_type']}) - {workload['status']}")
    
    # Scale inference workload
    print(f"\n📈 Scaling inference workload to 5 replicas...")
    success = await orchestrator.scale_workload("sentiment-analyzer", 5, "mlops-demo")
    print(f"✅ Scaling {'successful' if success else 'failed'}")
    
    # Get cluster metrics
    print(f"\n📊 Cluster metrics:")
    metrics = await orchestrator.get_cluster_metrics()
    print(f"  - Active workloads: {metrics['active_workloads']}")
    print(f"  - Total deployments: {metrics['total_deployments']}")
    print(f"  - Success rate: {metrics['deployment_success_rate']:.1f}%")
    print(f"  - Resource usage: {metrics['resource_usage']}")
    
    # Export workload config
    print(f"\n📄 Exporting workload configuration...")
    config = await orchestrator.export_workload_config("sentiment-analyzer", "mlops-demo")
    print(f"✅ Exported configuration for {config['workload_config']['name']}")
    print(f"  - Generated {len(config['kubernetes_manifests'])} Kubernetes manifests")


if __name__ == "__main__":
    asyncio.run(demo_kubernetes_orchestrator())