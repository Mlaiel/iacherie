"""☸️ Kubernetes Cluster Orchestrator - IA-Influencer-Agent Production Platform
===========================================================================
Expert: Lead Kubernetes Engineer + DevOps Specialist + Cloud Architect
Creator: Fahed Mlaiel <mlaiel@live.de>
===========================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE - AVERTISSEMENT LÉGAL ⚠️
Tout vol, copie ou utilisation non autorisée de ce code source,
de ce concept ou de cette propriété intellectuelle sans
l'autorisation écrite explicite de Fahed Mlaiel est strictement
interdite et constituera une violation des lois sur le droit d'auteur.

Professional Kubernetes cluster management for IA-Influencer multi-format 
content protection and monetization platform.

Enterprise cluster orchestration supporting:
- Multi-tier microservices deployment
- Auto-scaling and resource management
- High availability and disaster recovery
- Security and compliance enforcement
- Real-time monitoring and alerting
"""

import asyncio
import logging
import json
import yaml
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from pathlib import Path
import subprocess
import shlex
from kubernetes import client, config
from kubernetes.client.rest import ApiException

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DeploymentStatus(Enum):
    """
Deployment status enumeration"""

    PENDING = "pending"
    RUNNING = "running"
    READY = "ready"
    FAILED = "failed"
    SCALING = "scaling"
    UPDATING = "updating"
    TERMINATED = "terminated"

class ServiceType(Enum):
    """Kubernetes service type enumeration"""

    CLUSTER_IP = "ClusterIP"
    NODE_PORT = "NodePort"
    LOAD_BALANCER = "LoadBalancer"
    EXTERNAL_NAME = "ExternalName"

class NamespaceType(Enum):
    """Namespace type enumeration"""

    PRODUCTION = "production"
    STAGING = "staging"
    DEVELOPMENT = "development"
    MONITORING = "monitoring"
    SECURITY = "security"

@dataclass
class ClusterConfig:
    """Kubernetes cluster configuration"""
    name: str
    namespace: str
    replicas: int = 3
    image: str = ""
    resources: Dict[str, Any] = field(default_factory=dict)
    environment: Dict[str, str] = field(default_factory=dict)
    volumes: List[Dict[str, Any]] = field(default_factory=list)
    service_type: ServiceType = ServiceType.CLUSTER_IP
    ports: List[Dict[str, int]] = field(default_factory=list)
    labels: Dict[str, str] = field(default_factory=dict)

@dataclass
class DeploymentMetrics:
    """Deployment performance metrics"""
    deployment_name: str
    namespace: str
    replicas_desired: int
    replicas_available: int
    replicas_ready: int
    cpu_usage: float
    memory_usage: float
    network_in: float
    network_out: float
    timestamp: datetime

class KubernetesClusterOrchestrator:
    """
    Enterprise Kubernetes cluster orchestration system
    
    Provides comprehensive cluster management with:
    - Multi-namespace deployment orchestration
    - Auto-scaling and resource optimization
    - Health monitoring and recovery
    - Security and compliance management
    - Performance metrics and alerting
    """
    
    def __init__(self, config_path: Optional[Path] = None):
        """
Initialize cluster orchestrator"""
        self.logger = logger
        self.config_path = config_path or Path(__file__).parent / "config"
        self.deployments: Dict[str, ClusterConfig] = {}
        
        try:
            # Load Kubernetes configuration
            config.load_incluster_config()  # For in-cluster deployment
        except:
            try:
                config.load_kube_config()  # For local development
            except Exception as e:
                self.logger.warning(f"⚠️ Could not load Kubernetes config: {e}")
        
        # Initialize Kubernetes clients
        self.v1 = client.CoreV1Api()
        self.apps_v1 = client.AppsV1Api()
        self.autoscaling_v1 = client.AutoscalingV1Api()
        self.networking_v1 = client.NetworkingV1Api()
        
        self.logger.info("✅ Kubernetes cluster orchestrator initialized")
    
    async def register_deployment(self, config: ClusterConfig) -> str:
        """Register a new deployment configuration"""
        try:
            deployment_key = f"{config.namespace}/{config.name}"
            self.deployments[deployment_key] = config
            self.logger.info(f"📝 Registered deployment: {deployment_key}")
            return deployment_key
        except Exception as e:
            self.logger.error(f"❌ Failed to register deployment {config.name}: {e}")
            raise
    
    async def create_namespace(self, namespace: str, namespace_type: NamespaceType) -> bool:
        """Create a new Kubernetes namespace"""
        try:
            namespace_manifest = client.V1Namespace(
                metadata=client.V1ObjectMeta(
                    name=namespace,
                    labels={
                        "name": namespace,
                        "type": namespace_type.value,
                        "project": "ia-influencer-agent",
                        "managed-by": "cluster-orchestrator"
                    }
                )
            )
            
            self.v1.create_namespace(body=namespace_manifest)
            self.logger.info(f"📂 Created namespace: {namespace}")
            return True
            
        except ApiException as e:
            if e.status == 409:  # Namespace already exists
                self.logger.info(f"📂 Namespace already exists: {namespace}")
                return True
            else:
                self.logger.error(f"❌ Failed to create namespace {namespace}: {e}")
                return False
        except Exception as e:
            self.logger.error(f"❌ Failed to create namespace {namespace}: {e}")
            return False
    
    async def create_deployment(self, deployment_key: str) -> bool:
        """Create a Kubernetes deployment"""
        if deployment_key not in self.deployments:
            self.logger.error(f"❌ Deployment configuration not found: {deployment_key}")
            return False
        
        config = self.deployments[deployment_key]
        
        try:
            # Prepare container spec
            container = client.V1Container(
                name=config.name,
                image=config.image,
                ports=[
                    client.V1ContainerPort(container_port=port["port"])
                    for port in config.ports
                ],
                env=[
                    client.V1EnvVar(name=k, value=v)
                    for k, v in config.environment.items()
                ],
                resources=client.V1ResourceRequirements(
                    requests=config.resources.get("requests", {}),
                    limits=config.resources.get("limits", {})
                )
            )
            
            # Prepare pod template
            template = client.V1PodTemplateSpec(
                metadata=client.V1ObjectMeta(
                    labels={**config.labels, "app": config.name}
                ),
                spec=client.V1PodSpec(containers=[container])
            )
            
            # Prepare deployment spec
            spec = client.V1DeploymentSpec(
                replicas=config.replicas,
                selector=client.V1LabelSelector(
                    match_labels={"app": config.name}
                ),
                template=template
            )
            
            # Create deployment
            deployment = client.V1Deployment(
                api_version="apps/v1",
                kind="Deployment",
                metadata=client.V1ObjectMeta(
                    name=config.name,
                    namespace=config.namespace,
                    labels=config.labels
                ),
                spec=spec
            )
            
            self.apps_v1.create_namespaced_deployment(
                body=deployment,
                namespace=config.namespace
            )
            
            self.logger.info(f"🚀 Created deployment: {deployment_key}")
            return True
            
        except ApiException as e:
            if e.status == 409:  # Deployment already exists
                self.logger.info(f"🚀 Deployment already exists: {deployment_key}")
                return await self.update_deployment(deployment_key)
            else:
                self.logger.error(f"❌ Failed to create deployment {deployment_key}: {e}")
                return False
        except Exception as e:
            self.logger.error(f"❌ Failed to create deployment {deployment_key}: {e}")
            return False
    
    async def create_service(self, deployment_key: str) -> bool:
        """Create a Kubernetes service for deployment"""
        if deployment_key not in self.deployments:
            self.logger.error(f"❌ Deployment configuration not found: {deployment_key}")
            return False
        
        config = self.deployments[deployment_key]
        
        try:
            service = client.V1Service(
                api_version="v1",
                kind="Service",
                metadata=client.V1ObjectMeta(
                    name=config.name,
                    namespace=config.namespace,
                    labels=config.labels
                ),
                spec=client.V1ServiceSpec(
                    selector={"app": config.name},
                    ports=[
                        client.V1ServicePort(
                            port=port["port"],
                            target_port=port["target_port"]
                        )
                        for port in config.ports
                    ],
                    type=config.service_type.value
                )
            )
            
            self.v1.create_namespaced_service(
                body=service,
                namespace=config.namespace
            )
            
            self.logger.info(f"🌐 Created service: {deployment_key}")
            return True
            
        except ApiException as e:
            if e.status == 409:  # Service already exists
                self.logger.info(f"🌐 Service already exists: {deployment_key}")
                return True
            else:
                self.logger.error(f"❌ Failed to create service {deployment_key}: {e}")
                return False
        except Exception as e:
            self.logger.error(f"❌ Failed to create service {deployment_key}: {e}")
            return False
    
    async def update_deployment(self, deployment_key: str) -> bool:
        """Update an existing Kubernetes deployment"""
        if deployment_key not in self.deployments:
            self.logger.error(f"❌ Deployment configuration not found: {deployment_key}")
            return False
        
        config = self.deployments[deployment_key]
        
        try:
            # Get current deployment
            current = self.apps_v1.read_namespaced_deployment(
                name=config.name,
                namespace=config.namespace
            )
            
            # Update deployment
            current.spec.replicas = config.replicas
            current.spec.template.spec.containers[0].image = config.image
            
            self.apps_v1.patch_namespaced_deployment(
                name=config.name,
                namespace=config.namespace,
                body=current
            )
            
            self.logger.info(f"🔄 Updated deployment: {deployment_key}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to update deployment {deployment_key}: {e}")
            return False
    
    async def scale_deployment(self, deployment_key: str, replicas: int) -> bool:
        """Scale a deployment to specified number of replicas"""
        if deployment_key not in self.deployments:
            self.logger.error(f"❌ Deployment configuration not found: {deployment_key}")
            return False
        
        config = self.deployments[deployment_key]
        
        try:
            # Update replicas in config
            config.replicas = replicas
            
            # Scale deployment
            scale = client.V1Scale(
                metadata=client.V1ObjectMeta(
                    name=config.name,
                    namespace=config.namespace
                ),
                spec=client.V1ScaleSpec(replicas=replicas)
            )
            
            self.apps_v1.patch_namespaced_deployment_scale(
                name=config.name,
                namespace=config.namespace,
                body=scale
            )
            
            self.logger.info(f"📊 Scaled deployment {deployment_key} to {replicas} replicas")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to scale deployment {deployment_key}: {e}")
            return False
    
    async def delete_deployment(self, deployment_key: str) -> bool:
        """Delete a Kubernetes deployment"""
        if deployment_key not in self.deployments:
            self.logger.error(f"❌ Deployment configuration not found: {deployment_key}")
            return False
        
        config = self.deployments[deployment_key]
        
        try:
            # Delete deployment
            self.apps_v1.delete_namespaced_deployment(
                name=config.name,
                namespace=config.namespace
            )
            
            # Delete service
            try:
                self.v1.delete_namespaced_service(
                    name=config.name,
                    namespace=config.namespace
                )
            except:
                pass  # Service might not exist
            
            # Remove from registry
            del self.deployments[deployment_key]
            
            self.logger.info(f"🗑️ Deleted deployment: {deployment_key}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to delete deployment {deployment_key}: {e}")
            return False
    
    async def get_deployment_status(self, deployment_key: str) -> Optional[DeploymentStatus]:
        """Get current status of a deployment"""
        if deployment_key not in self.deployments:
            return None
        
        config = self.deployments[deployment_key]
        
        try:
            deployment = self.apps_v1.read_namespaced_deployment(
                name=config.name,
                namespace=config.namespace
            )
            
            status = deployment.status
            
            if status.ready_replicas == status.replicas:
                return DeploymentStatus.READY
            elif status.available_replicas and status.available_replicas > 0:
                return DeploymentStatus.RUNNING
            elif status.replicas and status.replicas > 0:
                return DeploymentStatus.PENDING
            else:
                return DeploymentStatus.FAILED
                
        except Exception as e:
            self.logger.error(f"❌ Failed to get deployment status {deployment_key}: {e}")
            return DeploymentStatus.FAILED
    
    async def get_deployment_metrics(self, deployment_key: str) -> Optional[DeploymentMetrics]:
        """Get performance metrics for a deployment"""
        if deployment_key not in self.deployments:
            return None
        
        config = self.deployments[deployment_key]
        
        try:
            deployment = self.apps_v1.read_namespaced_deployment(
                name=config.name,
                namespace=config.namespace
            )
            
            status = deployment.status
            
            return DeploymentMetrics(
                deployment_name=config.name,
                namespace=config.namespace,
                replicas_desired=status.replicas or 0,
                replicas_available=status.available_replicas or 0,
                replicas_ready=status.ready_replicas or 0,
                cpu_usage=0.0,  # Would need metrics server
                memory_usage=0.0,  # Would need metrics server
                network_in=0.0,  # Would need metrics server
                network_out=0.0,  # Would need metrics server
                timestamp=datetime.now()
            )
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get deployment metrics {deployment_key}: {e}")
            return None
    
    async def create_horizontal_pod_autoscaler(self, deployment_key: str, 
                                             min_replicas: int = 1, 
                                             max_replicas: int = 10,
                                             target_cpu_percent: int = 80) -> bool:
        """Create horizontal pod autoscaler for deployment"""
        if deployment_key not in self.deployments:
            self.logger.error(f"❌ Deployment configuration not found: {deployment_key}")
            return False
        
        config = self.deployments[deployment_key]
        
        try:
            hpa = client.V1HorizontalPodAutoscaler(
                api_version="autoscaling/v1",
                kind="HorizontalPodAutoscaler",
                metadata=client.V1ObjectMeta(
                    name=f"{config.name}-hpa",
                    namespace=config.namespace
                ),
                spec=client.V1HorizontalPodAutoscalerSpec(
                    scale_target_ref=client.V1CrossVersionObjectReference(
                        api_version="apps/v1",
                        kind="Deployment",
                        name=config.name
                    ),
                    min_replicas=min_replicas,
                    max_replicas=max_replicas,
                    target_cpu_utilization_percentage=target_cpu_percent
                )
            )
            
            self.autoscaling_v1.create_namespaced_horizontal_pod_autoscaler(
                body=hpa,
                namespace=config.namespace
            )
            
            self.logger.info(f"📈 Created HPA for deployment: {deployment_key}")
            return True
            
        except ApiException as e:
            if e.status == 409:  # HPA already exists
                self.logger.info(f"📈 HPA already exists for deployment: {deployment_key}")
                return True
            else:
                self.logger.error(f"❌ Failed to create HPA for {deployment_key}: {e}")
                return False
        except Exception as e:
            self.logger.error(f"❌ Failed to create HPA for {deployment_key}: {e}")
            return False
    
    async def deploy_full_stack(self, deployment_key: str) -> bool:
        """Deploy complete stack (namespace, deployment, service, HPA)"""
        if deployment_key not in self.deployments:
            self.logger.error(f"❌ Deployment configuration not found: {deployment_key}")
            return False
        
        config = self.deployments[deployment_key]
        
        try:
            # Create namespace
            await self.create_namespace(config.namespace, NamespaceType.PRODUCTION)
            
            # Create deployment
            if not await self.create_deployment(deployment_key):
                return False
            
            # Create service
            if not await self.create_service(deployment_key):
                return False
            
            # Create HPA
            await self.create_horizontal_pod_autoscaler(deployment_key)
            
            self.logger.info(f"🎯 Full stack deployed: {deployment_key}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to deploy full stack {deployment_key}: {e}")
            return False
    
    async def monitor_cluster(self) -> Dict[str, DeploymentMetrics]:
        """Monitor all deployments and return metrics"""
        metrics = {}
        
        for deployment_key in self.deployments:
            deployment_metrics = await self.get_deployment_metrics(deployment_key)
            if deployment_metrics:
                metrics[deployment_key] = deployment_metrics
        
        return metrics
    
    async def health_check_cluster(self) -> Dict[str, bool]:
        """
Perform health check on all deployments"""
        health_status = {}
        
        for deployment_key in self.deployments:
            status = await self.get_deployment_status(deployment_key)
            health_status[deployment_key] = status == DeploymentStatus.READY
        
        return health_status
    
    async def backup_cluster_config(self, backup_path: Path) -> bool:
        """
Backup cluster configurations to file"""
        try:
            backup_data = {
                'deployments': {},
                'timestamp': datetime.now().isoformat(),
                'version': '2.0.0'
            }
            
            for deployment_key, config in self.deployments.items():
                backup_data['deployments'][deployment_key] = {
                    'name': config.name,
                    'namespace': config.namespace,
                    'replicas': config.replicas,
                    'image': config.image,
                    'resources': config.resources,
                    'environment': config.environment,
                    'volumes': config.volumes,
                    'service_type': config.service_type.value,
                    'ports': config.ports,
                    'labels': config.labels
                }
            
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            with open(backup_path, 'w') as f:
                yaml.dump(backup_data, f, default_flow_style=False)
            
            self.logger.info(f"💾 Cluster configurations backed up to {backup_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to backup cluster configs: {e}")
            return False

# Global cluster orchestrator instance
_cluster_orchestrator: Optional[KubernetesClusterOrchestrator] = None

def get_cluster_orchestrator() -> KubernetesClusterOrchestrator:
    """Get global cluster orchestrator instance"""
    global _cluster_orchestrator
    if _cluster_orchestrator is None:
        _cluster_orchestrator = KubernetesClusterOrchestrator()
    return _cluster_orchestrator

async def initialize_cluster_orchestrator(config_path: Optional[Path] = None) -> KubernetesClusterOrchestrator:
    """
Initialize cluster orchestrator with configuration"""
    global _cluster_orchestrator
    _cluster_orchestrator = KubernetesClusterOrchestrator(config_path)
    return _cluster_orchestrator

# Export cluster orchestrator singleton
cluster_orchestrator = get_cluster_orchestrator()
