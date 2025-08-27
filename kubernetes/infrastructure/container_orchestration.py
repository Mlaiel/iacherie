"""
Container Orchestration System

Provides comprehensive Kubernetes and Docker container orchestration
for the IA Influencer Agent platform with advanced deployment strategies.

Project: IA Influencer Agent + Content Protection Platform
Author: Fahed Mlaiel <mlaiel@live.de>

⚠️  PROPRIETARY SOFTWARE - UNAUTHORIZED USE STRICTLY PROHIBITED ⚠️
"""

import asyncio
import logging
import yaml
from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
from enum import Enum
from typing import Dict, List, Optional, Any, Union
from kubernetes import client, config
from kubernetes.client.rest import ApiException
import docker
import json

logger = logging.getLogger(__name__)

class OrchestrationPlatform(Enum):
    """Supported orchestration platforms"""
    KUBERNETES = "kubernetes"
    DOCKER_SWARM = "docker_swarm"
    DOCKER_COMPOSE = "docker_compose"

class DeploymentStrategy(Enum):
    """Deployment strategies"""
    ROLLING_UPDATE = "rolling_update"
    BLUE_GREEN = "blue_green"
    CANARY = "canary"
    RECREATE = "recreate"

@dataclass
class ContainerSpec:
    """Container specification"""
    name: str
    image: str
    tag: str = "latest"
    ports: List[Dict[str, Any]] = None
    env_vars: Dict[str, str] = None
    resources: Dict[str, Any] = None
    volume_mounts: List[Dict[str, str]] = None
    health_check: Dict[str, Any] = None
    command: Optional[List[str]] = None
    args: Optional[List[str]] = None

@dataclass
class ServiceSpec:
    """Service specification"""
    name: str
    containers: List[ContainerSpec]
    replicas: int = 1
    strategy: DeploymentStrategy = DeploymentStrategy.ROLLING_UPDATE
    labels: Dict[str, str] = None
    annotations: Dict[str, str] = None
    service_type: str = "ClusterIP"
    ingress_config: Optional[Dict[str, Any]] = None

@dataclass
class NamespaceSpec:
    """Namespace specification"""
    name: str
    labels: Dict[str, str] = None
    resource_quotas: Optional[Dict[str, Any]] = None
    network_policies: Optional[List[Dict[str, Any]]] = None

class ContainerOrchestrator:
    """Main container orchestration manager"""
    
    def __init__(self, platform: OrchestrationPlatform = OrchestrationPlatform.KUBERNETES):
        self.platform = platform
        self.k8s_client = None
        self.docker_client = None
        self._init_clients()
        
    def _init_clients(self):
        """Initialize orchestration clients"""
        try:
            if self.platform == OrchestrationPlatform.KUBERNETES:
                config.load_incluster_config()
                self.k8s_client = client.ApiClient()
                self.apps_v1 = client.AppsV1Api()
                self.core_v1 = client.CoreV1Api()
                self.networking_v1 = client.NetworkingV1Api()
                logger.info("Kubernetes client initialized")
            
            elif self.platform in [OrchestrationPlatform.DOCKER_SWARM, OrchestrationPlatform.DOCKER_COMPOSE]:
                self.docker_client = docker.from_env()
                logger.info("Docker client initialized")
                
        except Exception as e:
            logger.warning(f"Could not initialize orchestration clients: {e}")
    
    async def create_namespace(self, namespace_spec: NamespaceSpec) -> Dict[str, Any]:
        """Create Kubernetes namespace"""
        if self.platform != OrchestrationPlatform.KUBERNETES:
            return {'status': 'skipped', 'message': 'Not applicable for current platform'}
        
        try:
            namespace = client.V1Namespace(
                metadata=client.V1ObjectMeta(
                    name=namespace_spec.name,
                    labels=namespace_spec.labels or {}
                )
            )
            
            self.core_v1.create_namespace(body=namespace)
            
            # Create resource quotas if specified
            if namespace_spec.resource_quotas:
                quota = client.V1ResourceQuota(
                    metadata=client.V1ObjectMeta(
                        name=f"{namespace_spec.name}-quota"
                    ),
                    spec=client.V1ResourceQuotaSpec(
                        hard=namespace_spec.resource_quotas
                    )
                )
                self.core_v1.create_namespaced_resource_quota(
                    namespace=namespace_spec.name,
                    body=quota
                )
            
            logger.info(f"Created namespace: {namespace_spec.name}")
            return {'status': 'success', 'namespace': namespace_spec.name}
            
        except ApiException as e:
            if e.status == 409:  # Already exists
                logger.info(f"Namespace {namespace_spec.name} already exists")
                return {'status': 'exists', 'namespace': namespace_spec.name}
            else:
                logger.error(f"Failed to create namespace: {e}")
                return {'status': 'error', 'message': str(e)}
    
    async def deploy_service(self, service_spec: ServiceSpec, namespace: str = "default") -> Dict[str, Any]:
        """Deploy service to orchestration platform"""
        if self.platform == OrchestrationPlatform.KUBERNETES:
            return await self._deploy_k8s_service(service_spec, namespace)
        elif self.platform == OrchestrationPlatform.DOCKER_COMPOSE:
            return await self._deploy_docker_compose_service(service_spec)
        else:
            return {'status': 'error', 'message': f'Unsupported platform: {self.platform}'}
    
    async def _deploy_k8s_service(self, service_spec: ServiceSpec, namespace: str) -> Dict[str, Any]:
        """Deploy service to Kubernetes"""
        try:
            # Create deployment
            deployment = self._create_k8s_deployment(service_spec, namespace)
            deployment_result = self.apps_v1.create_namespaced_deployment(
                namespace=namespace,
                body=deployment
            )
            
            # Create service
            service = self._create_k8s_service(service_spec, namespace)
            service_result = self.core_v1.create_namespaced_service(
                namespace=namespace,
                body=service
            )
            
            # Create ingress if specified
            ingress_result = None
            if service_spec.ingress_config:
                ingress = self._create_k8s_ingress(service_spec, namespace)
                ingress_result = self.networking_v1.create_namespaced_ingress(
                    namespace=namespace,
                    body=ingress
                )
            
            logger.info(f"Deployed Kubernetes service: {service_spec.name}")
            return {
                'status': 'success',
                'deployment': deployment_result.metadata.name,
                'service': service_result.metadata.name,
                'ingress': ingress_result.metadata.name if ingress_result else None
            }
            
        except ApiException as e:
            logger.error(f"Failed to deploy Kubernetes service: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def _create_k8s_deployment(self, service_spec: ServiceSpec, namespace: str) -> client.V1Deployment:
        """Create Kubernetes deployment manifest"""
        containers = []
        
        for container_spec in service_spec.containers:
            container = client.V1Container(
                name=container_spec.name,
                image=f"{container_spec.image}:{container_spec.tag}",
                ports=[
                    client.V1ContainerPort(container_port=port['containerPort'])
                    for port in container_spec.ports or []
                ],
                env=[
                    client.V1EnvVar(name=k, value=v)
                    for k, v in (container_spec.env_vars or {}).items()
                ],
                resources=client.V1ResourceRequirements(
                    requests=container_spec.resources.get('requests', {}) if container_spec.resources else {},
                    limits=container_spec.resources.get('limits', {}) if container_spec.resources else {}
                ),
                volume_mounts=[
                    client.V1VolumeMount(
                        name=vm['name'],
                        mount_path=vm['mountPath']
                    )
                    for vm in container_spec.volume_mounts or []
                ],
                command=container_spec.command,
                args=container_spec.args
            )
            
            # Add health checks
            if container_spec.health_check:
                hc = container_spec.health_check
                if hc.get('httpGet'):
                    container.liveness_probe = client.V1Probe(
                        http_get=client.V1HTTPGetAction(
                            path=hc['httpGet']['path'],
                            port=hc['httpGet']['port']
                        ),
                        initial_delay_seconds=hc.get('initialDelaySeconds', 30),
                        period_seconds=hc.get('periodSeconds', 10)
                    )
            
            containers.append(container)
        
        # Deployment strategy
        strategy = None
        if service_spec.strategy == DeploymentStrategy.ROLLING_UPDATE:
            strategy = client.V1DeploymentStrategy(
                type="RollingUpdate",
                rolling_update=client.V1RollingUpdateDeployment(
                    max_surge="25%",
                    max_unavailable="25%"
                )
            )
        elif service_spec.strategy == DeploymentStrategy.RECREATE:
            strategy = client.V1DeploymentStrategy(type="Recreate")
        
        deployment = client.V1Deployment(
            api_version="apps/v1",
            kind="Deployment",
            metadata=client.V1ObjectMeta(
                name=service_spec.name,
                labels=service_spec.labels or {},
                annotations=service_spec.annotations or {}
            ),
            spec=client.V1DeploymentSpec(
                replicas=service_spec.replicas,
                selector=client.V1LabelSelector(
                    match_labels={"app": service_spec.name}
                ),
                template=client.V1PodTemplateSpec(
                    metadata=client.V1ObjectMeta(
                        labels={"app": service_spec.name, **(service_spec.labels or {})}
                    ),
                    spec=client.V1PodSpec(containers=containers)
                ),
                strategy=strategy
            )
        )
        
        return deployment
    
    def _create_k8s_service(self, service_spec: ServiceSpec, namespace: str) -> client.V1Service:
        """Create Kubernetes service manifest"""
        ports = []
        for container in service_spec.containers:
            for port in container.ports or []:
                ports.append(client.V1ServicePort(
                    name=f"port-{port['containerPort']}",
                    port=port.get('servicePort', port['containerPort']),
                    target_port=port['containerPort'],
                    protocol=port.get('protocol', 'TCP')
                ))
        
        service = client.V1Service(
            api_version="v1",
            kind="Service",
            metadata=client.V1ObjectMeta(
                name=f"{service_spec.name}-service",
                labels=service_spec.labels or {}
            ),
            spec=client.V1ServiceSpec(
                selector={"app": service_spec.name},
                ports=ports,
                type=service_spec.service_type
            )
        )
        
        return service
    
    def _create_k8s_ingress(self, service_spec: ServiceSpec, namespace: str) -> client.V1Ingress:
        """Create Kubernetes ingress manifest"""
        ingress_config = service_spec.ingress_config
        
        rules = []
        for rule in ingress_config.get('rules', []):
            http_paths = []
            for path in rule.get('paths', []):
                http_paths.append(client.V1HTTPIngressPath(
                    path=path['path'],
                    path_type=path.get('pathType', 'Prefix'),
                    backend=client.V1IngressBackend(
                        service=client.V1IngressServiceBackend(
                            name=f"{service_spec.name}-service",
                            port=client.V1ServiceBackendPort(
                                number=path['servicePort']
                            )
                        )
                    )
                ))
            
            rules.append(client.V1IngressRule(
                host=rule.get('host'),
                http=client.V1HTTPIngressRuleValue(paths=http_paths)
            ))
        
        ingress = client.V1Ingress(
            api_version="networking.k8s.io/v1",
            kind="Ingress",
            metadata=client.V1ObjectMeta(
                name=f"{service_spec.name}-ingress",
                labels=service_spec.labels or {},
                annotations=ingress_config.get('annotations', {})
            ),
            spec=client.V1IngressSpec(
                rules=rules,
                tls=ingress_config.get('tls', [])
            )
        )
        
        return ingress
    
    async def _deploy_docker_compose_service(self, service_spec: ServiceSpec) -> Dict[str, Any]:
        """Deploy service using Docker Compose"""
        try:
            compose_config = self._generate_docker_compose(service_spec)
            
            # Write compose file
            with open(f"docker-compose-{service_spec.name}.yml", 'w') as f:
                yaml.dump(compose_config, f)
            
            # Deploy using docker-compose
            import subprocess
            result = subprocess.run([
                'docker-compose', 
                '-f', f"docker-compose-{service_spec.name}.yml",
                'up', '-d'
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"Deployed Docker Compose service: {service_spec.name}")
                return {'status': 'success', 'service': service_spec.name}
            else:
                logger.error(f"Docker Compose deployment failed: {result.stderr}")
                return {'status': 'error', 'message': result.stderr}
                
        except Exception as e:
            logger.error(f"Failed to deploy Docker Compose service: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def _generate_docker_compose(self, service_spec: ServiceSpec) -> Dict[str, Any]:
        """Generate docker-compose configuration"""
        services = {}
        
        for container in service_spec.containers:
            service_config = {
                'image': f"{container.image}:{container.tag}",
                'restart': 'unless-stopped'
            }
            
            if container.ports:
                service_config['ports'] = [
                    f"{port.get('hostPort', port['containerPort'])}:{port['containerPort']}"
                    for port in container.ports
                ]
            
            if container.env_vars:
                service_config['environment'] = container.env_vars
            
            if container.volume_mounts:
                service_config['volumes'] = [
                    f"{vm.get('hostPath', vm['name'])}:{vm['mountPath']}"
                    for vm in container.volume_mounts
                ]
            
            if container.command:
                service_config['command'] = container.command
            
            if container.health_check:
                hc = container.health_check
                if hc.get('httpGet'):
                    service_config['healthcheck'] = {
                        'test': f"curl -f http://localhost:{hc['httpGet']['port']}{hc['httpGet']['path']} || exit 1",
                        'interval': f"{hc.get('periodSeconds', 30)}s",
                        'timeout': '10s',
                        'retries': 3
                    }
            
            services[container.name] = service_config
        
        return {
            'version': '3.8',
            'services': services
        }
    
    async def scale_service(self, service_name: str, replicas: int, namespace: str = "default") -> Dict[str, Any]:
        """Scale service replicas"""
        if self.platform == OrchestrationPlatform.KUBERNETES:
            try:
                self.apps_v1.patch_namespaced_deployment_scale(
                    name=service_name,
                    namespace=namespace,
                    body={'spec': {'replicas': replicas}}
                )
                
                logger.info(f"Scaled service {service_name} to {replicas} replicas")
                return {'status': 'success', 'replicas': replicas}
                
            except ApiException as e:
                logger.error(f"Failed to scale service: {e}")
                return {'status': 'error', 'message': str(e)}
        else:
            return {'status': 'error', 'message': 'Scaling not implemented for current platform'}
    
    async def update_service(self, service_spec: ServiceSpec, namespace: str = "default") -> Dict[str, Any]:
        """Update existing service"""
        if self.platform == OrchestrationPlatform.KUBERNETES:
            try:
                # Update deployment
                deployment = self._create_k8s_deployment(service_spec, namespace)
                self.apps_v1.patch_namespaced_deployment(
                    name=service_spec.name,
                    namespace=namespace,
                    body=deployment
                )
                
                logger.info(f"Updated service: {service_spec.name}")
                return {'status': 'success', 'service': service_spec.name}
                
            except ApiException as e:
                logger.error(f"Failed to update service: {e}")
                return {'status': 'error', 'message': str(e)}
        else:
            return {'status': 'error', 'message': 'Update not implemented for current platform'}
    
    async def delete_service(self, service_name: str, namespace: str = "default") -> Dict[str, Any]:
        """Delete service and related resources"""
        if self.platform == OrchestrationPlatform.KUBERNETES:
            try:
                # Delete deployment
                self.apps_v1.delete_namespaced_deployment(
                    name=service_name,
                    namespace=namespace
                )
                
                # Delete service
                self.core_v1.delete_namespaced_service(
                    name=f"{service_name}-service",
                    namespace=namespace
                )
                
                # Delete ingress if exists
                try:
                    self.networking_v1.delete_namespaced_ingress(
                        name=f"{service_name}-ingress",
                        namespace=namespace
                    )
                except ApiException:
                    pass  # Ingress might not exist
                
                logger.info(f"Deleted service: {service_name}")
                return {'status': 'success', 'service': service_name}
                
            except ApiException as e:
                logger.error(f"Failed to delete service: {e}")
                return {'status': 'error', 'message': str(e)}
        else:
            return {'status': 'error', 'message': 'Delete not implemented for current platform'}
    
    async def get_service_status(self, service_name: str, namespace: str = "default") -> Dict[str, Any]:
        """Get service status and health"""
        if self.platform == OrchestrationPlatform.KUBERNETES:
            try:
                # Get deployment status
                deployment = self.apps_v1.read_namespaced_deployment(
                    name=service_name,
                    namespace=namespace
                )
                
                # Get pods status
                pods = self.core_v1.list_namespaced_pod(
                    namespace=namespace,
                    label_selector=f"app={service_name}"
                )
                
                pod_statuses = []
                for pod in pods.items:
                    pod_statuses.append({
                        'name': pod.metadata.name,
                        'status': pod.status.phase,
                        'ready': all(condition.status == "True" 
                                   for condition in pod.status.conditions or []
                                   if condition.type == "Ready")
                    })
                
                return {
                    'status': 'success',
                    'deployment': {
                        'name': deployment.metadata.name,
                        'replicas': deployment.spec.replicas,
                        'ready_replicas': deployment.status.ready_replicas or 0,
                        'available_replicas': deployment.status.available_replicas or 0
                    },
                    'pods': pod_statuses
                }
                
            except ApiException as e:
                logger.error(f"Failed to get service status: {e}")
                return {'status': 'error', 'message': str(e)}
        else:
            return {'status': 'error', 'message': 'Status check not implemented for current platform'}
    
    async def create_platform_manifests(self, services: List[ServiceSpec], namespace: str = "ia-influencer") -> Dict[str, Any]:
        """Create complete platform manifests"""
        manifests = {
            'kubernetes': {},
            'docker_compose': {}
        }
        
        # Generate Kubernetes manifests
        k8s_manifests = []
        
        # Namespace
        namespace_manifest = {
            'apiVersion': 'v1',
            'kind': 'Namespace',
            'metadata': {
                'name': namespace,
                'labels': {
                    'project': 'ia-influencer-agent',
                    'environment': 'production'
                }
            }
        }
        k8s_manifests.append(namespace_manifest)
        
        # Services
        for service_spec in services:
            # Deployment
            deployment = self._create_k8s_deployment(service_spec, namespace)
            k8s_manifests.append(deployment.to_dict())
            
            # Service
            service = self._create_k8s_service(service_spec, namespace)
            k8s_manifests.append(service.to_dict())
            
            # Ingress
            if service_spec.ingress_config:
                ingress = self._create_k8s_ingress(service_spec, namespace)
                k8s_manifests.append(ingress.to_dict())
        
        manifests['kubernetes'] = k8s_manifests
        
        # Generate Docker Compose
        compose_services = {}
        for service_spec in services:
            compose_config = self._generate_docker_compose(service_spec)
            compose_services.update(compose_config['services'])
        
        manifests['docker_compose'] = {
            'version': '3.8',
            'services': compose_services
        }
        
        return {
            'status': 'success',
            'manifests': manifests
        }
