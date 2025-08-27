"""
IA Influencer Agent - Kubernetes Orchestration Manager
Enterprise Kubernetes cluster management and deployment automation

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved - Unauthorized use prohibited

Features:
- Kubernetes cluster lifecycle management
- Pod autoscaling and resource optimization
- Service mesh integration
- Rolling deployments with zero downtime
- Health monitoring and self-healing
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum
import yaml
import json
from datetime import datetime, timedelta

from kubernetes import client, config, watch
from kubernetes.client.rest import ApiException
import prometheus_client

# Note: Import paths adjusted for actual deployment structure
import sys
import os
from .base_manager import BaseDeploymentManager

# Mock metrics collector for standalone operation
class MetricsCollector:
    """Mock metrics collector."""
    def __init__(self):
        pass


class DeploymentStrategy(Enum):
    """Kubernetes deployment strategies."""
    ROLLING_UPDATE = "RollingUpdate"
    RECREATE = "Recreate"
    BLUE_GREEN = "BlueGreen"
    CANARY = "Canary"


class ResourceType(Enum):
    """Kubernetes resource types."""
    DEPLOYMENT = "Deployment"
    SERVICE = "Service"
    CONFIGMAP = "ConfigMap"
    SECRET = "Secret"
    INGRESS = "Ingress"
    PERSISTENT_VOLUME = "PersistentVolume"
    NAMESPACE = "Namespace"
    STATEFULSET = "StatefulSet"


@dataclass
class KubernetesResource:
    """Kubernetes resource configuration."""
    name: str
    namespace: str
    resource_type: ResourceType
    spec: Dict[str, Any]
    labels: Optional[Dict[str, str]] = None
    annotations: Optional[Dict[str, str]] = None


@dataclass
class DeploymentConfig:
    """Deployment configuration."""
    name: str
    namespace: str
    image: str
    replicas: int
    strategy: DeploymentStrategy
    resource_limits: Dict[str, str]
    environment_variables: Dict[str, str]
    volumes: List[Dict[str, Any]]
    health_checks: Dict[str, Any]


class KubernetesManager(BaseDeploymentManager):
    """
    Enterprise Kubernetes orchestration manager.
    
    Manages Kubernetes clusters, deployments, and services for the
    IA Influencer Agent platform with enterprise-grade features.
    """

    def __init__(
        self,
        cluster_config: Optional[str] = None,
        namespace: str = "ia-influencer-agent",
        metrics_collector: Optional[MetricsCollector] = None
    ):
        super().__init__()
        self.namespace = namespace
        self.cluster_config = cluster_config
        self.metrics_collector = metrics_collector or MetricsCollector()
        
        # Initialize Kubernetes clients
        self._init_kubernetes_clients()
        
        # Resource management
        self.deployed_resources: Dict[str, KubernetesResource] = {}
        self.active_deployments: Dict[str, DeploymentConfig] = {}
        
        # Monitoring
        self.deployment_metrics = prometheus_client.Counter(
            'kubernetes_deployments_total',
            'Total number of deployments',
            ['namespace', 'deployment', 'status']
        )
        
        self.pod_metrics = prometheus_client.Gauge(
            'kubernetes_pods_active',
            'Number of active pods',
            ['namespace', 'deployment']
        )

    def _init_kubernetes_clients(self) -> None:
        """Initialize Kubernetes API clients."""
        try:
            if self.cluster_config:
                config.load_kube_config(config_file=self.cluster_config)
            else:
                config.load_incluster_config()
                
            self.v1_core = client.CoreV1Api()
            self.v1_apps = client.AppsV1Api()
            self.v1_networking = client.NetworkingV1Api()
            self.v1_rbac = client.RbacAuthorizationV1Api()
            self.v1_autoscaling = client.AutoscalingV1Api()
            
            self.logger.info("Kubernetes clients initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Kubernetes clients: {e}")
            raise

    async def create_namespace(self, namespace: str, labels: Optional[Dict[str, str]] = None) -> bool:
        """
        Create Kubernetes namespace.
        
        Args:
            namespace: Namespace name
            labels: Optional labels for the namespace
            
        Returns:
            True if successful, False otherwise
        """
        try:
            namespace_metadata = client.V1ObjectMeta(
                name=namespace,
                labels=labels or {}
            )
            
            namespace_body = client.V1Namespace(
                metadata=namespace_metadata
            )
            
            self.v1_core.create_namespace(body=namespace_body)
            self.logger.info(f"Namespace '{namespace}' created successfully")
            return True
            
        except ApiException as e:
            if e.status == 409:  # Namespace already exists
                self.logger.info(f"Namespace '{namespace}' already exists")
                return True
            else:
                self.logger.error(f"Failed to create namespace '{namespace}': {e}")
                return False

    async def deploy_application(self, config: DeploymentConfig) -> bool:
        """
        Deploy application to Kubernetes cluster.
        
        Args:
            config: Deployment configuration
            
        Returns:
            True if deployment successful, False otherwise
        """
        try:
            # Ensure namespace exists
            await self.create_namespace(config.namespace)
            
            # Create deployment
            deployment_created = await self._create_deployment(config)
            if not deployment_created:
                return False
            
            # Create service
            service_created = await self._create_service(config)
            if not service_created:
                return False
            
            # Create ingress if needed
            if self._requires_ingress(config):
                ingress_created = await self._create_ingress(config)
                if not ingress_created:
                    return False
            
            # Wait for deployment to be ready
            deployment_ready = await self._wait_for_deployment_ready(
                config.name, config.namespace
            )
            
            if deployment_ready:
                self.active_deployments[config.name] = config
                self.deployment_metrics.labels(
                    namespace=config.namespace,
                    deployment=config.name,
                    status='success'
                ).inc()
                
                self.logger.info(f"Application '{config.name}' deployed successfully")
                return True
            else:
                self.logger.error(f"Deployment '{config.name}' failed to become ready")
                return False
                
        except Exception as e:
            self.deployment_metrics.labels(
                namespace=config.namespace,
                deployment=config.name,
                status='failed'
            ).inc()
            
            self.logger.error(f"Failed to deploy application '{config.name}': {e}")
            return False

    async def _create_deployment(self, config: DeploymentConfig) -> bool:
        """Create Kubernetes deployment."""
        try:
            # Container specification
            container = client.V1Container(
                name=config.name,
                image=config.image,
                ports=[client.V1ContainerPort(container_port=8000)],
                env=[
                    client.V1EnvVar(name=k, value=v) 
                    for k, v in config.environment_variables.items()
                ],
                resources=client.V1ResourceRequirements(
                    requests=config.resource_limits,
                    limits=config.resource_limits
                ),
                liveness_probe=self._create_probe(config.health_checks.get('liveness')),
                readiness_probe=self._create_probe(config.health_checks.get('readiness'))
            )
            
            # Pod template
            pod_template = client.V1PodTemplateSpec(
                metadata=client.V1ObjectMeta(
                    labels={"app": config.name, "version": "v1"}
                ),
                spec=client.V1PodSpec(
                    containers=[container],
                    volumes=self._create_volumes(config.volumes)
                )
            )
            
            # Deployment specification
            deployment_spec = client.V1DeploymentSpec(
                replicas=config.replicas,
                selector=client.V1LabelSelector(
                    match_labels={"app": config.name}
                ),
                template=pod_template,
                strategy=self._create_deployment_strategy(config.strategy)
            )
            
            # Deployment object
            deployment = client.V1Deployment(
                api_version="apps/v1",
                kind="Deployment",
                metadata=client.V1ObjectMeta(
                    name=config.name,
                    namespace=config.namespace,
                    labels={"app": config.name, "managed-by": "ia-influencer-agent"}
                ),
                spec=deployment_spec
            )
            
            # Create deployment
            self.v1_apps.create_namespaced_deployment(
                namespace=config.namespace,
                body=deployment
            )
            
            self.logger.info(f"Deployment '{config.name}' created successfully")
            return True
            
        except ApiException as e:
            self.logger.error(f"Failed to create deployment '{config.name}': {e}")
            return False

    async def _create_service(self, config: DeploymentConfig) -> bool:
        """Create Kubernetes service."""
        try:
            service_spec = client.V1ServiceSpec(
                selector={"app": config.name},
                ports=[
                    client.V1ServicePort(
                        port=80,
                        target_port=8000,
                        protocol="TCP"
                    )
                ],
                type="ClusterIP"
            )
            
            service = client.V1Service(
                api_version="v1",
                kind="Service",
                metadata=client.V1ObjectMeta(
                    name=f"{config.name}-service",
                    namespace=config.namespace,
                    labels={"app": config.name}
                ),
                spec=service_spec
            )
            
            self.v1_core.create_namespaced_service(
                namespace=config.namespace,
                body=service
            )
            
            self.logger.info(f"Service '{config.name}-service' created successfully")
            return True
            
        except ApiException as e:
            self.logger.error(f"Failed to create service for '{config.name}': {e}")
            return False

    async def _create_ingress(self, config: DeploymentConfig) -> bool:
        """Create Kubernetes ingress."""
        try:
            ingress_spec = client.V1IngressSpec(
                rules=[
                    client.V1IngressRule(
                        host=f"{config.name}.ia-influencer-agent.com",
                        http=client.V1HTTPIngressRuleValue(
                            paths=[
                                client.V1HTTPIngressPath(
                                    path="/",
                                    path_type="Prefix",
                                    backend=client.V1IngressBackend(
                                        service=client.V1IngressServiceBackend(
                                            name=f"{config.name}-service",
                                            port=client.V1ServiceBackendPort(number=80)
                                        )
                                    )
                                )
                            ]
                        )
                    )
                ]
            )
            
            ingress = client.V1Ingress(
                api_version="networking.k8s.io/v1",
                kind="Ingress",
                metadata=client.V1ObjectMeta(
                    name=f"{config.name}-ingress",
                    namespace=config.namespace,
                    annotations={
                        "kubernetes.io/ingress.class": "nginx",
                        "cert-manager.io/cluster-issuer": "letsencrypt-prod"
                    }
                ),
                spec=ingress_spec
            )
            
            self.v1_networking.create_namespaced_ingress(
                namespace=config.namespace,
                body=ingress
            )
            
            self.logger.info(f"Ingress '{config.name}-ingress' created successfully")
            return True
            
        except ApiException as e:
            self.logger.error(f"Failed to create ingress for '{config.name}': {e}")
            return False

    async def scale_deployment(self, deployment_name: str, namespace: str, replicas: int) -> bool:
        """
        Scale deployment replicas.
        
        Args:
            deployment_name: Name of the deployment
            namespace: Kubernetes namespace
            replicas: Target number of replicas
            
        Returns:
            True if scaling successful, False otherwise
        """
        try:
            # Patch deployment with new replica count
            body = {"spec": {"replicas": replicas}}
            
            self.v1_apps.patch_namespaced_deployment_scale(
                name=deployment_name,
                namespace=namespace,
                body=body
            )
            
            self.logger.info(f"Deployment '{deployment_name}' scaled to {replicas} replicas")
            return True
            
        except ApiException as e:
            self.logger.error(f"Failed to scale deployment '{deployment_name}': {e}")
            return False

    async def rolling_update(self, deployment_name: str, namespace: str, new_image: str) -> bool:
        """
        Perform rolling update of deployment.
        
        Args:
            deployment_name: Name of the deployment
            namespace: Kubernetes namespace
            new_image: New container image
            
        Returns:
            True if update successful, False otherwise
        """
        try:
            # Get current deployment
            deployment = self.v1_apps.read_namespaced_deployment(
                name=deployment_name,
                namespace=namespace
            )
            
            # Update container image
            for container in deployment.spec.template.spec.containers:
                if container.name == deployment_name:
                    container.image = new_image
            
            # Apply update
            self.v1_apps.patch_namespaced_deployment(
                name=deployment_name,
                namespace=namespace,
                body=deployment
            )
            
            # Wait for rollout to complete
            rollout_complete = await self._wait_for_rollout_complete(
                deployment_name, namespace
            )
            
            if rollout_complete:
                self.logger.info(f"Rolling update completed for '{deployment_name}'")
                return True
            else:
                self.logger.error(f"Rolling update failed for '{deployment_name}'")
                return False
                
        except ApiException as e:
            self.logger.error(f"Failed to perform rolling update for '{deployment_name}': {e}")
            return False

    async def get_deployment_status(self, deployment_name: str, namespace: str) -> Dict[str, Any]:
        """
        Get deployment status and metrics.
        
        Args:
            deployment_name: Name of the deployment
            namespace: Kubernetes namespace
            
        Returns:
            Deployment status information
        """
        try:
            deployment = self.v1_apps.read_namespaced_deployment(
                name=deployment_name,
                namespace=namespace
            )
            
            pods = self.v1_core.list_namespaced_pod(
                namespace=namespace,
                label_selector=f"app={deployment_name}"
            )
            
            status = {
                "name": deployment_name,
                "namespace": namespace,
                "replicas": {
                    "desired": deployment.spec.replicas,
                    "current": deployment.status.replicas or 0,
                    "ready": deployment.status.ready_replicas or 0,
                    "available": deployment.status.available_replicas or 0
                },
                "conditions": [
                    {
                        "type": condition.type,
                        "status": condition.status,
                        "reason": condition.reason,
                        "message": condition.message
                    }
                    for condition in (deployment.status.conditions or [])
                ],
                "pods": [
                    {
                        "name": pod.metadata.name,
                        "status": pod.status.phase,
                        "ready": all(
                            condition.status == "True" 
                            for condition in (pod.status.conditions or [])
                            if condition.type == "Ready"
                        ),
                        "node": pod.spec.node_name,
                        "created": pod.metadata.creation_timestamp.isoformat()
                    }
                    for pod in pods.items
                ]
            }
            
            # Update metrics
            self.pod_metrics.labels(
                namespace=namespace,
                deployment=deployment_name
            ).set(len([p for p in status["pods"] if p["ready"]]))
            
            return status
            
        except ApiException as e:
            self.logger.error(f"Failed to get deployment status for '{deployment_name}': {e}")
            return {}

    async def delete_deployment(self, deployment_name: str, namespace: str) -> bool:
        """
        Delete deployment and associated resources.
        
        Args:
            deployment_name: Name of the deployment
            namespace: Kubernetes namespace
            
        Returns:
            True if deletion successful, False otherwise
        """
        try:
            # Delete deployment
            self.v1_apps.delete_namespaced_deployment(
                name=deployment_name,
                namespace=namespace
            )
            
            # Delete service
            try:
                self.v1_core.delete_namespaced_service(
                    name=f"{deployment_name}-service",
                    namespace=namespace
                )
            except ApiException:
                pass  # Service might not exist
            
            # Delete ingress
            try:
                self.v1_networking.delete_namespaced_ingress(
                    name=f"{deployment_name}-ingress",
                    namespace=namespace
                )
            except ApiException:
                pass  # Ingress might not exist
            
            # Remove from active deployments
            if deployment_name in self.active_deployments:
                del self.active_deployments[deployment_name]
            
            self.logger.info(f"Deployment '{deployment_name}' deleted successfully")
            return True
            
        except ApiException as e:
            self.logger.error(f"Failed to delete deployment '{deployment_name}': {e}")
            return False

    async def create_horizontal_pod_autoscaler(
        self,
        deployment_name: str,
        namespace: str,
        min_replicas: int = 1,
        max_replicas: int = 10,
        target_cpu_utilization: int = 70
    ) -> bool:
        """
        Create Horizontal Pod Autoscaler.
        
        Args:
            deployment_name: Name of the deployment
            namespace: Kubernetes namespace
            min_replicas: Minimum number of replicas
            max_replicas: Maximum number of replicas
            target_cpu_utilization: Target CPU utilization percentage
            
        Returns:
            True if HPA created successfully, False otherwise
        """
        try:
            hpa_spec = client.V1HorizontalPodAutoscalerSpec(
                scale_target_ref=client.V1CrossVersionObjectReference(
                    api_version="apps/v1",
                    kind="Deployment",
                    name=deployment_name
                ),
                min_replicas=min_replicas,
                max_replicas=max_replicas,
                target_cpu_utilization_percentage=target_cpu_utilization
            )
            
            hpa = client.V1HorizontalPodAutoscaler(
                api_version="autoscaling/v1",
                kind="HorizontalPodAutoscaler",
                metadata=client.V1ObjectMeta(
                    name=f"{deployment_name}-hpa",
                    namespace=namespace
                ),
                spec=hpa_spec
            )
            
            self.v1_autoscaling.create_namespaced_horizontal_pod_autoscaler(
                namespace=namespace,
                body=hpa
            )
            
            self.logger.info(f"HPA created for deployment '{deployment_name}'")
            return True
            
        except ApiException as e:
            self.logger.error(f"Failed to create HPA for '{deployment_name}': {e}")
            return False

    def _create_probe(self, probe_config: Optional[Dict[str, Any]]) -> Optional[client.V1Probe]:
        """Create health check probe."""
        if not probe_config:
            return None
            
        return client.V1Probe(
            http_get=client.V1HTTPGetAction(
                path=probe_config.get("path", "/health"),
                port=probe_config.get("port", 8000)
            ),
            initial_delay_seconds=probe_config.get("initial_delay", 30),
            period_seconds=probe_config.get("period", 10),
            timeout_seconds=probe_config.get("timeout", 5),
            failure_threshold=probe_config.get("failure_threshold", 3)
        )

    def _create_volumes(self, volumes_config: List[Dict[str, Any]]) -> List[client.V1Volume]:
        """Create volume specifications."""
        volumes = []
        for volume_config in volumes_config:
            if volume_config["type"] == "configMap":
                volumes.append(client.V1Volume(
                    name=volume_config["name"],
                    config_map=client.V1ConfigMapVolumeSource(
                        name=volume_config["config_map_name"]
                    )
                ))
            elif volume_config["type"] == "secret":
                volumes.append(client.V1Volume(
                    name=volume_config["name"],
                    secret=client.V1SecretVolumeSource(
                        secret_name=volume_config["secret_name"]
                    )
                ))
        return volumes

    def _create_deployment_strategy(self, strategy: DeploymentStrategy) -> client.V1DeploymentStrategy:
        """Create deployment strategy."""
        if strategy == DeploymentStrategy.ROLLING_UPDATE:
            return client.V1DeploymentStrategy(
                type="RollingUpdate",
                rolling_update=client.V1RollingUpdateDeployment(
                    max_surge="25%",
                    max_unavailable="25%"
                )
            )
        else:
            return client.V1DeploymentStrategy(type="Recreate")

    def _requires_ingress(self, config: DeploymentConfig) -> bool:
        """Check if deployment requires ingress."""
        return config.name in ["api-gateway", "frontend", "monitoring-dashboard"]

    async def _wait_for_deployment_ready(self, deployment_name: str, namespace: str, timeout: int = 600) -> bool:
        """Wait for deployment to be ready."""
        start_time = datetime.now()
        while (datetime.now() - start_time).total_seconds() < timeout:
            try:
                deployment = self.v1_apps.read_namespaced_deployment(
                    name=deployment_name,
                    namespace=namespace
                )
                
                if (deployment.status.ready_replicas and 
                    deployment.status.ready_replicas == deployment.spec.replicas):
                    return True
                    
                await asyncio.sleep(10)
                
            except ApiException:
                await asyncio.sleep(10)
                
        return False

    async def _wait_for_rollout_complete(self, deployment_name: str, namespace: str, timeout: int = 600) -> bool:
        """Wait for rollout to complete."""
        start_time = datetime.now()
        while (datetime.now() - start_time).total_seconds() < timeout:
            try:
                deployment = self.v1_apps.read_namespaced_deployment(
                    name=deployment_name,
                    namespace=namespace
                )
                
                for condition in (deployment.status.conditions or []):
                    if (condition.type == "Progressing" and 
                        condition.status == "True" and 
                        condition.reason == "NewReplicaSetAvailable"):
                        return True
                
                await asyncio.sleep(10)
                
            except ApiException:
                await asyncio.sleep(10)
                
        return False

    async def get_cluster_resources(self) -> Dict[str, Any]:
        """
        Get cluster resource usage and capacity.
        
        Returns:
            Cluster resource information
        """
        try:
            nodes = self.v1_core.list_node()
            pods = self.v1_core.list_pod_for_all_namespaces()
            
            cluster_info = {
                "nodes": {
                    "total": len(nodes.items),
                    "ready": len([n for n in nodes.items if self._is_node_ready(n)]),
                    "details": [
                        {
                            "name": node.metadata.name,
                            "status": self._get_node_status(node),
                            "capacity": node.status.capacity,
                            "allocatable": node.status.allocatable
                        }
                        for node in nodes.items
                    ]
                },
                "pods": {
                    "total": len(pods.items),
                    "running": len([p for p in pods.items if p.status.phase == "Running"]),
                    "pending": len([p for p in pods.items if p.status.phase == "Pending"]),
                    "failed": len([p for p in pods.items if p.status.phase == "Failed"])
                }
            }
            
            return cluster_info
            
        except ApiException as e:
            self.logger.error(f"Failed to get cluster resources: {e}")
            return {}

    def _is_node_ready(self, node: client.V1Node) -> bool:
        """Check if node is ready."""
        for condition in (node.status.conditions or []):
            if condition.type == "Ready" and condition.status == "True":
                return True
        return False

    def _get_node_status(self, node: client.V1Node) -> str:
        """Get node status."""
        for condition in (node.status.conditions or []):
            if condition.type == "Ready":
                return "Ready" if condition.status == "True" else "NotReady"
        return "Unknown"

    async def cleanup_resources(self) -> bool:
        """
        Cleanup orphaned resources and failed deployments.
        
        Returns:
            True if cleanup successful, False otherwise
        """
        try:
            # Get all namespaces managed by the platform
            namespaces = self.v1_core.list_namespace(
                label_selector="managed-by=ia-influencer-agent"
            )
            
            for namespace in namespaces.items:
                namespace_name = namespace.metadata.name
                
                # Clean up failed pods
                failed_pods = self.v1_core.list_namespaced_pod(
                    namespace=namespace_name,
                    field_selector="status.phase=Failed"
                )
                
                for pod in failed_pods.items:
                    self.v1_core.delete_namespaced_pod(
                        name=pod.metadata.name,
                        namespace=namespace_name
                    )
                
                # Clean up completed jobs
                completed_jobs = self.v1_core.list_namespaced_pod(
                    namespace=namespace_name,
                    field_selector="status.phase=Succeeded"
                )
                
                for pod in completed_jobs.items:
                    if pod.metadata.owner_references:
                        for owner in pod.metadata.owner_references:
                            if owner.kind == "Job":
                                # Delete old completed pods
                                creation_time = pod.metadata.creation_timestamp
                                if (datetime.now(creation_time.tzinfo) - creation_time).days > 7:
                                    self.v1_core.delete_namespaced_pod(
                                        name=pod.metadata.name,
                                        namespace=namespace_name
                                    )
            
            self.logger.info("Resource cleanup completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to cleanup resources: {e}")
            return False
