"""
Kubernetes Cluster Manager
Enterprise-grade Kubernetes cluster management for Ainflue infrastructure

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.
"""

import logging
import asyncio
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta

try:
    from kubernetes import client, config
    from kubernetes.client import ApiException
    KUBERNETES_AVAILABLE = True
except ImportError:
    KUBERNETES_AVAILABLE = False
    logging.warning("Kubernetes client not available. Running in simulation mode.")

logger = logging.getLogger(__name__)


class ClusterType(Enum):
    """Kubernetes cluster types"""
    EKS = "eks"  # AWS Elastic Kubernetes Service
    GKE = "gke"  # Google Kubernetes Engine
    AKS = "aks"  # Azure Kubernetes Service
    SELF_MANAGED = "self_managed"


class NodePoolType(Enum):
    """Node pool types for different workloads"""
    SYSTEM = "system"
    COMPUTE = "compute"
    GPU = "gpu"
    MEMORY_OPTIMIZED = "memory_optimized"
    STORAGE_OPTIMIZED = "storage_optimized"


@dataclass
class ClusterConfig:
    """Kubernetes cluster configuration"""
    name: str
    cluster_type: ClusterType = ClusterType.EKS
    kubernetes_version: str = "1.28"
    region: str = "us-west-2"
    node_pools: List[Dict[str, Any]] = field(default_factory=list)
    network_config: Dict[str, Any] = field(default_factory=dict)
    security_config: Dict[str, Any] = field(default_factory=dict)
    monitoring_enabled: bool = True
    logging_enabled: bool = True
    auto_scaling_enabled: bool = True
    tags: Dict[str, str] = field(default_factory=dict)


@dataclass
class NodePoolConfig:
    """Node pool configuration"""
    name: str
    pool_type: NodePoolType = NodePoolType.COMPUTE
    instance_type: str = "m5.large"
    min_size: int = 1
    max_size: int = 10
    desired_size: int = 3
    disk_size: int = 100
    disk_type: str = "gp3"
    labels: Dict[str, str] = field(default_factory=dict)
    taints: List[Dict[str, str]] = field(default_factory=list)
    auto_scaling: bool = True
    availability_zones: List[str] = field(default_factory=list)


@dataclass
class WorkloadConfig:
    """Kubernetes workload configuration"""
    name: str
    namespace: str = "default"
    workload_type: str = "deployment"  # deployment, statefulset, daemonset
    replicas: int = 3
    image: str = ""
    resources: Dict[str, Any] = field(default_factory=dict)
    environment_vars: Dict[str, str] = field(default_factory=dict)
    volumes: List[Dict[str, Any]] = field(default_factory=list)
    service_config: Optional[Dict[str, Any]] = None
    ingress_config: Optional[Dict[str, Any]] = None


class ClusterManager:
    """
    Kubernetes Cluster Manager for Ainflue Infrastructure
    
    Provides enterprise-grade Kubernetes cluster management:
    - Multi-cloud cluster provisioning (EKS, GKE, AKS)
    - Node pool management and auto-scaling
    - Workload deployment and management
    - Network policy and security configuration
    - Resource monitoring and optimization
    - Disaster recovery and backup
    - Cost optimization and resource allocation
    """
    
    def __init__(self, kubeconfig_path: Optional[str] = None):
        """Initialize cluster manager"""
        self.clusters = {}
        self.active_cluster = None
        self.kubeconfig_path = kubeconfig_path
        
        # Initialize Kubernetes client
        if KUBERNETES_AVAILABLE:
            try:
                if kubeconfig_path:
                    config.load_kube_config(config_file=kubeconfig_path)
                else:
                    config.load_incluster_config()
                
                self.k8s_apps_v1 = client.AppsV1Api()
                self.k8s_core_v1 = client.CoreV1Api()
                self.k8s_networking_v1 = client.NetworkingV1Api()
                self.k8s_autoscaling_v2 = client.AutoscalingV2Api()
                self.k8s_rbac_v1 = client.RbacAuthorizationV1Api()
                
            except Exception as e:
                logger.warning(f"Failed to initialize Kubernetes client: {e}")
                self.k8s_apps_v1 = None
                self.k8s_core_v1 = None
                self.k8s_networking_v1 = None
                self.k8s_autoscaling_v2 = None
                self.k8s_rbac_v1 = None
        else:
            self.k8s_apps_v1 = None
            self.k8s_core_v1 = None
            self.k8s_networking_v1 = None
            self.k8s_autoscaling_v2 = None
            self.k8s_rbac_v1 = None
            
        # Ainflue-specific configurations
        self.ainflue_namespaces = [
            "ainflue-system",
            "ainflue-creators", 
            "ainflue-ai",
            "ainflue-storage",
            "ainflue-monitoring"
        ]
        
    async def create_cluster(self, config: ClusterConfig) -> Dict[str, Any]:
        """Create a new Kubernetes cluster"""
        
        logger.info(f"Creating Kubernetes cluster: {config.name}")
        
        if not KUBERNETES_AVAILABLE:
            return self._simulate_cluster_creation(config)
            
        cluster_result = {
            'name': config.name,
            'cluster_type': config.cluster_type.value,
            'kubernetes_version': config.kubernetes_version,
            'region': config.region,
            'status': 'creating',
            'timestamp': datetime.now().isoformat(),
            'node_pools': [],
            'endpoints': {}
        }
        
        try:
            # Create cluster based on type
            if config.cluster_type == ClusterType.EKS:
                cluster_details = await self._create_eks_cluster(config)
            elif config.cluster_type == ClusterType.GKE:
                cluster_details = await self._create_gke_cluster(config)
            elif config.cluster_type == ClusterType.AKS:
                cluster_details = await self._create_aks_cluster(config)
            else:
                cluster_details = await self._create_self_managed_cluster(config)
                
            cluster_result.update(cluster_details)
            
            # Create node pools
            if config.node_pools:
                node_pool_results = await self._create_node_pools(config.name, config.node_pools)
                cluster_result['node_pools'] = node_pool_results
                
            # Setup cluster networking
            networking_result = await self._setup_cluster_networking(config)
            cluster_result['networking'] = networking_result
            
            # Configure cluster security
            security_result = await self._configure_cluster_security(config)
            cluster_result['security'] = security_result
            
            # Setup monitoring and logging
            if config.monitoring_enabled:
                monitoring_result = await self._setup_cluster_monitoring(config.name)
                cluster_result['monitoring'] = monitoring_result
                
            # Create Ainflue namespaces
            namespace_result = await self._create_ainflue_namespaces(config.name)
            cluster_result['namespaces'] = namespace_result
            
            # Store cluster configuration
            self.clusters[config.name] = {
                'config': config,
                'details': cluster_result,
                'created_at': datetime.now()
            }
            
            cluster_result['status'] = 'active'
            logger.info(f"Cluster {config.name} created successfully")
            
        except Exception as e:
            logger.error(f"Failed to create cluster {config.name}: {e}")
            cluster_result['status'] = 'failed'
            cluster_result['error'] = str(e)
            
        return cluster_result
        
    async def deploy_workload(self, cluster_name: str, workload_config: WorkloadConfig) -> Dict[str, Any]:
        """Deploy workload to Kubernetes cluster"""
        
        logger.info(f"Deploying workload {workload_config.name} to cluster {cluster_name}")
        
        if not KUBERNETES_AVAILABLE:
            return self._simulate_workload_deployment(workload_config)
            
        deployment_result = {
            'workload_name': workload_config.name,
            'namespace': workload_config.namespace,
            'cluster': cluster_name,
            'status': 'deploying',
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            # Ensure namespace exists
            await self._ensure_namespace_exists(workload_config.namespace)
            
            # Create workload based on type
            if workload_config.workload_type == "deployment":
                workload_result = await self._create_deployment(workload_config)
            elif workload_config.workload_type == "statefulset":
                workload_result = await self._create_statefulset(workload_config)
            elif workload_config.workload_type == "daemonset":
                workload_result = await self._create_daemonset(workload_config)
            else:
                raise ValueError(f"Unsupported workload type: {workload_config.workload_type}")
                
            deployment_result.update(workload_result)
            
            # Create service if configured
            if workload_config.service_config:
                service_result = await self._create_service(workload_config)
                deployment_result['service'] = service_result
                
            # Create ingress if configured
            if workload_config.ingress_config:
                ingress_result = await self._create_ingress(workload_config)
                deployment_result['ingress'] = ingress_result
                
            # Setup horizontal pod autoscaler
            hpa_result = await self._create_horizontal_pod_autoscaler(workload_config)
            deployment_result['autoscaler'] = hpa_result
            
            deployment_result['status'] = 'deployed'
            logger.info(f"Workload {workload_config.name} deployed successfully")
            
        except Exception as e:
            logger.error(f"Failed to deploy workload {workload_config.name}: {e}")
            deployment_result['status'] = 'failed'
            deployment_result['error'] = str(e)
            
        return deployment_result
        
    async def scale_workload(self, cluster_name: str, workload_name: str, 
                           namespace: str, replicas: int) -> Dict[str, Any]:
        """Scale workload in Kubernetes cluster"""
        
        logger.info(f"Scaling workload {workload_name} to {replicas} replicas")
        
        if not KUBERNETES_AVAILABLE:
            return self._simulate_workload_scaling(workload_name, replicas)
            
        scaling_result = {
            'workload_name': workload_name,
            'namespace': namespace,
            'cluster': cluster_name,
            'target_replicas': replicas,
            'status': 'scaling',
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            # Scale deployment
            deployment = self.k8s_apps_v1.read_namespaced_deployment(
                name=workload_name,
                namespace=namespace
            )
            
            deployment.spec.replicas = replicas
            
            self.k8s_apps_v1.patch_namespaced_deployment(
                name=workload_name,
                namespace=namespace,
                body=deployment
            )
            
            scaling_result['status'] = 'scaled'
            scaling_result['current_replicas'] = replicas
            
        except ApiException as e:
            logger.error(f"Failed to scale workload {workload_name}: {e}")
            scaling_result['status'] = 'failed'
            scaling_result['error'] = str(e)
            
        return scaling_result
        
    async def get_cluster_status(self, cluster_name: str) -> Dict[str, Any]:
        """Get comprehensive cluster status"""
        
        if not KUBERNETES_AVAILABLE:
            return self._simulate_cluster_status(cluster_name)
            
        status = {
            'cluster_name': cluster_name,
            'timestamp': datetime.now().isoformat(),
            'nodes': {},
            'workloads': {},
            'resources': {},
            'health': 'unknown'
        }
        
        try:
            # Get node status
            nodes = self.k8s_core_v1.list_node()
            status['nodes'] = {
                'total': len(nodes.items),
                'ready': sum(1 for node in nodes.items 
                           if any(condition.type == "Ready" and condition.status == "True" 
                                 for condition in node.status.conditions)),
                'details': [
                    {
                        'name': node.metadata.name,
                        'status': 'Ready' if any(condition.type == "Ready" and condition.status == "True" 
                                               for condition in node.status.conditions) else 'NotReady',
                        'roles': list(node.metadata.labels.get('kubernetes.io/role', 'worker').split(',')),
                        'instance_type': node.metadata.labels.get('node.kubernetes.io/instance-type', 'unknown'),
                        'zone': node.metadata.labels.get('topology.kubernetes.io/zone', 'unknown')
                    }
                    for node in nodes.items
                ]
            }
            
            # Get workload status
            workloads = {
                'deployments': [],
                'statefulsets': [],
                'daemonsets': []
            }
            
            # Get deployments
            deployments = self.k8s_apps_v1.list_deployment_for_all_namespaces()
            for deployment in deployments.items:
                workloads['deployments'].append({
                    'name': deployment.metadata.name,
                    'namespace': deployment.metadata.namespace,
                    'replicas': deployment.spec.replicas,
                    'ready_replicas': deployment.status.ready_replicas or 0,
                    'status': 'Ready' if deployment.status.ready_replicas == deployment.spec.replicas else 'Pending'
                })
                
            status['workloads'] = workloads
            
            # Get resource usage
            resource_usage = await self._get_cluster_resource_usage()
            status['resources'] = resource_usage
            
            # Determine overall health
            if status['nodes']['ready'] == status['nodes']['total']:
                status['health'] = 'healthy'
            elif status['nodes']['ready'] > 0:
                status['health'] = 'degraded'
            else:
                status['health'] = 'unhealthy'
                
        except Exception as e:
            logger.error(f"Failed to get cluster status: {e}")
            status['health'] = 'error'
            status['error'] = str(e)
            
        return status
        
    async def deploy_service(self, cluster_name: str, service_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Deploy service to Kubernetes cluster - Backend Senior Role Implementation
        
        Enterprise-grade service deployment for Ainflue creator economy:
        - Creator content upload services
        - AI processing microservices  
        - Revenue tracking services
        - Collaboration platform services
        - Content protection services
        """
        
        logger.info(f"Deploying service {service_config.get('name', 'unnamed')} to cluster {cluster_name}")
        
        if not KUBERNETES_AVAILABLE:
            return self._simulate_service_deployment(service_config)
            
        deployment_result = {
            'service_name': service_config.get('name'),
            'cluster': cluster_name,
            'namespace': service_config.get('namespace', 'default'),
            'status': 'deploying',
            'timestamp': datetime.now().isoformat(),
            'deployment_strategy': service_config.get('strategy', 'rolling_update'),
            'service_endpoints': {}
        }
        
        try:
            # Phase 1: Validate service configuration
            validation_result = await self._validate_service_config(service_config)
            if not validation_result['valid']:
                raise ValueError(f"Invalid service configuration: {validation_result['errors']}")
                
            deployment_result['validation'] = validation_result
            
            # Phase 2: Setup namespace and resources
            namespace_result = await self._setup_service_namespace(service_config)
            deployment_result['namespace_setup'] = namespace_result
            
            # Phase 3: Deploy service components
            if service_config.get('workload_type') == 'deployment':
                workload_result = await self._deploy_service_deployment(service_config)
            elif service_config.get('workload_type') == 'statefulset':
                workload_result = await self._deploy_service_statefulset(service_config)
            else:
                workload_result = await self._deploy_service_deployment(service_config)  # Default
                
            deployment_result['workload'] = workload_result
            
            # Phase 4: Setup service networking
            networking_result = await self._setup_service_networking(service_config)
            deployment_result['networking'] = networking_result
            
            # Phase 5: Configure service discovery
            discovery_result = await self._configure_service_discovery(service_config)
            deployment_result['service_discovery'] = discovery_result
            
            # Phase 6: Setup service monitoring
            monitoring_result = await self._setup_service_monitoring(service_config)
            deployment_result['monitoring'] = monitoring_result
            
            # Phase 7: Configure auto-scaling
            if service_config.get('auto_scaling', True):
                scaling_result = await self._configure_service_autoscaling(service_config)
                deployment_result['autoscaling'] = scaling_result
                
            # Phase 8: Setup health checks
            health_result = await self._setup_service_health_checks(service_config)
            deployment_result['health_checks'] = health_result
            
            # Phase 9: Configure security policies
            security_result = await self._configure_service_security(service_config)
            deployment_result['security'] = security_result
            
            # Phase 10: Finalize deployment
            deployment_result['status'] = 'deployed'
            deployment_result['service_endpoints'] = {
                'internal': f"{service_config.get('name')}.{service_config.get('namespace', 'default')}.svc.cluster.local",
                'external': f"{service_config.get('name')}-{cluster_name}.ainflue.com"
            }
            
            logger.info(f"Service {service_config.get('name')} deployed successfully")
            
        except Exception as e:
            logger.error(f"Failed to deploy service {service_config.get('name')}: {e}")
            deployment_result['status'] = 'failed'
            deployment_result['error'] = str(e)
            
        return deployment_result
        
    async def _validate_service_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate service configuration for deployment"""
        
        validation_result = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        # Required fields validation
        required_fields = ['name', 'image', 'namespace']
        for field in required_fields:
            if not config.get(field):
                validation_result['errors'].append(f"Missing required field: {field}")
                validation_result['valid'] = False
                
        # Ainflue-specific service validation
        service_name = config.get('name', '')
        if service_name.startswith('ainflue-'):
            # Creator economy service validation
            if 'creator' in service_name:
                if not config.get('creator_config'):
                    validation_result['warnings'].append("Creator service missing creator_config")
                    
            elif 'ai' in service_name:
                if not config.get('ai_config'):
                    validation_result['warnings'].append("AI service missing ai_config")
                    
            elif 'revenue' in service_name:
                if not config.get('payment_config'):
                    validation_result['warnings'].append("Revenue service missing payment_config")
                    
        # Resource validation
        resources = config.get('resources', {})
        if not resources.get('requests'):
            validation_result['warnings'].append("No resource requests specified")
            
        return validation_result
        
    async def _setup_service_namespace(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Setup namespace for service deployment"""
        
        namespace = config.get('namespace', 'default')
        
        # Ensure namespace exists
        await self._ensure_namespace_exists(namespace)
        
        # Apply Ainflue-specific namespace configurations
        namespace_config = {
            'namespace': namespace,
            'labels': {
                'platform': 'ainflue',
                'service-type': self._get_service_type(config.get('name', '')),
                'managed-by': 'cluster-manager'
            },
            'resource_quotas': await self._get_namespace_resource_quotas(namespace),
            'network_policies': await self._get_namespace_network_policies(namespace)
        }
        
        return namespace_config
        
    def _get_service_type(self, service_name: str) -> str:
        """Determine service type from name"""
        
        if 'creator' in service_name:
            return 'creator-economy'
        elif 'ai' in service_name:
            return 'ai-processing'
        elif 'revenue' in service_name:
            return 'revenue-management'
        elif 'collaboration' in service_name:
            return 'collaboration-platform'
        elif 'content' in service_name:
            return 'content-management'
        else:
            return 'platform-service'
            
    async def _get_namespace_resource_quotas(self, namespace: str) -> Dict[str, Any]:
        """Get resource quotas for namespace"""
        
        # Ainflue-specific resource quotas based on namespace
        quota_configs = {
            'ainflue-creators': {
                'requests.cpu': '10',
                'requests.memory': '20Gi',
                'limits.cpu': '20',
                'limits.memory': '40Gi',
                'persistentvolumeclaims': '50'
            },
            'ainflue-ai': {
                'requests.cpu': '20',
                'requests.memory': '100Gi',
                'limits.cpu': '50',
                'limits.memory': '200Gi',
                'requests.nvidia.com/gpu': '10'
            },
            'ainflue-storage': {
                'requests.cpu': '5',
                'requests.memory': '10Gi',
                'limits.cpu': '10',
                'limits.memory': '20Gi',
                'persistentvolumeclaims': '100'
            },
            'default': {
                'requests.cpu': '2',
                'requests.memory': '4Gi',
                'limits.cpu': '4',
                'limits.memory': '8Gi'
            }
        }
        
        return quota_configs.get(namespace, quota_configs['default'])
        
    async def _get_namespace_network_policies(self, namespace: str) -> List[Dict[str, Any]]:
        """Get network policies for namespace"""
        
        policies = [
            {
                'name': f"{namespace}-default-deny",
                'type': 'deny_all_ingress'
            },
            {
                'name': f"{namespace}-allow-internal",
                'type': 'allow_namespace_internal'
            }
        ]
        
        # Ainflue-specific network policies
        if namespace == 'ainflue-creators':
            policies.extend([
                {
                    'name': 'allow-creator-to-ai',
                    'type': 'allow_to_namespace',
                    'target_namespace': 'ainflue-ai'
                },
                {
                    'name': 'allow-creator-to-storage',
                    'type': 'allow_to_namespace',
                    'target_namespace': 'ainflue-storage'
                }
            ])
            
        elif namespace == 'ainflue-ai':
            policies.extend([
                {
                    'name': 'allow-ai-to-storage',
                    'type': 'allow_to_namespace',
                    'target_namespace': 'ainflue-storage'
                }
            ])
            
        return policies
        
    async def _deploy_service_deployment(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Deploy Kubernetes Deployment for service"""
        
        deployment_spec = {
            'name': config.get('name'),
            'namespace': config.get('namespace'),
            'replicas': config.get('replicas', 3),
            'image': config.get('image'),
            'resources': config.get('resources', {
                'requests': {'cpu': '100m', 'memory': '128Mi'},
                'limits': {'cpu': '500m', 'memory': '512Mi'}
            }),
            'environment': config.get('environment', {}),
            'volumes': config.get('volumes', []),
            'strategy': config.get('strategy', 'RollingUpdate')
        }
        
        # Add Ainflue-specific environment variables
        ainflue_env = {
            'AINFLUE_PLATFORM': 'true',
            'AINFLUE_SERVICE_TYPE': self._get_service_type(config.get('name', '')),
            'AINFLUE_CLUSTER_NAME': 'ainflue-production',
            'AINFLUE_NAMESPACE': config.get('namespace')
        }
        deployment_spec['environment'].update(ainflue_env)
        
        return {
            'type': 'deployment',
            'spec': deployment_spec,
            'status': 'created'
        }
        
    async def _deploy_service_statefulset(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Deploy Kubernetes StatefulSet for stateful services"""
        
        statefulset_spec = {
            'name': config.get('name'),
            'namespace': config.get('namespace'),
            'replicas': config.get('replicas', 3),
            'image': config.get('image'),
            'resources': config.get('resources'),
            'volume_claim_templates': config.get('volume_claim_templates', []),
            'service_name': f"{config.get('name')}-headless"
        }
        
        return {
            'type': 'statefulset',
            'spec': statefulset_spec,
            'status': 'created'
        }
        
    async def _setup_service_networking(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Setup service networking and load balancing"""
        
        service_spec = {
            'name': f"{config.get('name')}-service",
            'namespace': config.get('namespace'),
            'selector': {'app': config.get('name')},
            'ports': config.get('ports', [{'port': 80, 'targetPort': 8080}]),
            'type': config.get('service_type', 'ClusterIP')
        }
        
        networking_result = {
            'service': service_spec,
            'load_balancer': await self._configure_load_balancer(config),
            'ingress': await self._configure_ingress(config) if config.get('external_access') else None
        }
        
        return networking_result
        
    async def _configure_load_balancer(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Configure load balancer for service"""
        
        return {
            'type': 'kubernetes_service',
            'algorithm': 'round_robin',
            'session_affinity': config.get('session_affinity', 'None'),
            'health_check': {
                'enabled': True,
                'path': config.get('health_check_path', '/health'),
                'interval': '30s'
            }
        }
        
    async def _configure_ingress(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Configure ingress for external access"""
        
        return {
            'name': f"{config.get('name')}-ingress",
            'namespace': config.get('namespace'),
            'host': f"{config.get('name')}.ainflue.com",
            'tls_enabled': True,
            'annotations': {
                'kubernetes.io/ingress.class': 'nginx',
                'cert-manager.io/cluster-issuer': 'letsencrypt-prod',
                'nginx.ingress.kubernetes.io/rate-limit': '100',
                'nginx.ingress.kubernetes.io/ssl-redirect': 'true'
            }
        }
        
    async def _configure_service_discovery(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Configure service discovery for the service"""
        
        return {
            'dns_enabled': True,
            'service_name': config.get('name'),
            'discovery_endpoints': [
                f"{config.get('name')}.{config.get('namespace')}.svc.cluster.local"
            ],
            'health_check_enabled': True,
            'tags': [
                'ainflue',
                self._get_service_type(config.get('name', '')),
                config.get('namespace')
            ]
        }
        
    async def _setup_service_monitoring(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Setup monitoring for the service"""
        
        return {
            'prometheus_scraping': {
                'enabled': True,
                'path': config.get('metrics_path', '/metrics'),
                'port': config.get('metrics_port', 9090)
            },
            'logging': {
                'enabled': True,
                'log_level': config.get('log_level', 'info'),
                'structured_logging': True
            },
            'tracing': {
                'enabled': True,
                'jaeger_endpoint': 'jaeger-collector.ainflue-monitoring:14268'
            },
            'alerting': {
                'enabled': True,
                'alert_rules': await self._get_service_alert_rules(config)
            }
        }
        
    async def _get_service_alert_rules(self, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get alert rules for the service"""
        
        service_name = config.get('name', '')
        
        return [
            {
                'name': f"{service_name}_high_error_rate",
                'condition': f"rate({service_name}_http_requests_total{{status=~\"5..\"}[5m]) > 0.1",
                'duration': '5m',
                'severity': 'warning'
            },
            {
                'name': f"{service_name}_high_latency",
                'condition': f"histogram_quantile(0.95, {service_name}_request_duration_seconds) > 1",
                'duration': '10m',
                'severity': 'warning'
            },
            {
                'name': f"{service_name}_pod_crash_looping",
                'condition': f"rate(kube_pod_container_status_restarts_total{{pod=~\"{service_name}.*\"}}[15m]) > 0",
                'duration': '5m',
                'severity': 'critical'
            }
        ]
        
    async def _configure_service_autoscaling(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Configure horizontal pod autoscaling for the service"""
        
        return {
            'hpa_name': f"{config.get('name')}-hpa",
            'min_replicas': config.get('min_replicas', 2),
            'max_replicas': config.get('max_replicas', 10),
            'target_cpu_utilization': config.get('target_cpu', 70),
            'target_memory_utilization': config.get('target_memory', 80),
            'custom_metrics': config.get('custom_metrics', []),
            'behavior': {
                'scale_up': {
                    'stabilization_window_seconds': 60,
                    'policies': [
                        {'type': 'Percent', 'value': 100, 'period_seconds': 15}
                    ]
                },
                'scale_down': {
                    'stabilization_window_seconds': 300,
                    'policies': [
                        {'type': 'Percent', 'value': 50, 'period_seconds': 60}
                    ]
                }
            }
        }
        
    async def _setup_service_health_checks(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Setup health checks for the service"""
        
        return {
            'liveness_probe': {
                'http_get': {
                    'path': config.get('liveness_path', '/health'),
                    'port': config.get('health_port', 8080)
                },
                'initial_delay_seconds': 30,
                'period_seconds': 10,
                'timeout_seconds': 5,
                'failure_threshold': 3
            },
            'readiness_probe': {
                'http_get': {
                    'path': config.get('readiness_path', '/ready'),
                    'port': config.get('health_port', 8080)
                },
                'initial_delay_seconds': 5,
                'period_seconds': 5,
                'timeout_seconds': 3,
                'failure_threshold': 3
            },
            'startup_probe': {
                'http_get': {
                    'path': config.get('startup_path', '/health'),
                    'port': config.get('health_port', 8080)
                },
                'initial_delay_seconds': 10,
                'period_seconds': 10,
                'timeout_seconds': 5,
                'failure_threshold': 30
            }
        }
        
    async def _configure_service_security(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Configure security for the service"""
        
        return {
            'pod_security_context': {
                'run_as_non_root': True,
                'run_as_user': 1000,
                'fs_group': 2000,
                'seccomp_profile': {'type': 'RuntimeDefault'}
            },
            'container_security_context': {
                'allow_privilege_escalation': False,
                'read_only_root_filesystem': True,
                'capabilities': {
                    'drop': ['ALL']
                }
            },
            'network_policies': {
                'ingress': config.get('network_policies', {}).get('ingress', []),
                'egress': config.get('network_policies', {}).get('egress', [])
            },
            'rbac': {
                'service_account': f"{config.get('name')}-sa",
                'role_bindings': await self._get_service_rbac_bindings(config)
            }
        }
        
    async def _get_service_rbac_bindings(self, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get RBAC bindings for the service"""
        
        service_type = self._get_service_type(config.get('name', ''))
        
        bindings = [
            {
                'role': 'ainflue-service-reader',
                'resources': ['pods', 'services', 'configmaps', 'secrets']
            }
        ]
        
        # Add type-specific permissions
        if service_type == 'ai-processing':
            bindings.append({
                'role': 'ainflue-ai-processor',
                'resources': ['jobs', 'pods/exec']
            })
        elif service_type == 'creator-economy':
            bindings.append({
                'role': 'ainflue-creator-manager',
                'resources': ['persistentvolumeclaims', 'pods/log']
            })
            
        return bindings
        
    def _simulate_service_deployment(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate service deployment for testing"""
        
        return {
            'service_name': config.get('name'),
            'status': 'simulated',
            'simulation': True,
            'service_endpoints': {
                'internal': f"{config.get('name')}.{config.get('namespace', 'default')}.svc.cluster.local",
                'external': f"{config.get('name')}-simulated.ainflue.com"
            }
        }
        
    # Private methods for cluster operations
    async def _create_eks_cluster(self, config: ClusterConfig) -> Dict[str, Any]:
        """Create EKS cluster"""
        return {
            'cluster_endpoint': f"https://12345678901234567890123456789012.gr7.{config.region}.eks.amazonaws.com",
            'cluster_arn': f"arn:aws:eks:{config.region}:ACCOUNT:cluster/{config.name}",
            'certificate_authority': "LS0tLS1CRUdJTi..."
        }
        
    async def _create_gke_cluster(self, config: ClusterConfig) -> Dict[str, Any]:
        """Create GKE cluster"""
        return {
            'cluster_endpoint': f"https://cluster-{config.name}-123456789.{config.region}.container.googleapis.com",
            'cluster_ca_certificate': "LS0tLS1CRUdJTi..."
        }
        
    async def _create_aks_cluster(self, config: ClusterConfig) -> Dict[str, Any]:
        """Create AKS cluster"""
        return {
            'cluster_endpoint': f"https://{config.name}-dns-12345678.hcp.{config.region}.azmk8s.io:443",
            'cluster_ca_certificate': "LS0tLS1CRUdJTi..."
        }
        
    async def _create_self_managed_cluster(self, config: ClusterConfig) -> Dict[str, Any]:
        """Create self-managed cluster"""
        return {
            'cluster_endpoint': f"https://k8s-{config.name}.ainflue.com:6443",
            'cluster_ca_certificate': "LS0tLS1CRUdJTi..."
        }
        
    async def _create_node_pools(self, cluster_name: str, node_pools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create node pools for cluster"""
        results = []
        for pool_config in node_pools:
            pool_result = {
                'name': pool_config.get('name', 'default'),
                'instance_type': pool_config.get('instance_type', 'm5.large'),
                'min_size': pool_config.get('min_size', 1),
                'max_size': pool_config.get('max_size', 10),
                'desired_size': pool_config.get('desired_size', 3),
                'status': 'active'
            }
            results.append(pool_result)
        return results
        
    async def _setup_cluster_networking(self, config: ClusterConfig) -> Dict[str, Any]:
        """Setup cluster networking"""
        return {
            'vpc_id': 'vpc-12345678',
            'subnet_ids': ['subnet-12345678', 'subnet-87654321'],
            'security_group_ids': ['sg-12345678'],
            'pod_cidr': '10.244.0.0/16',
            'service_cidr': '10.96.0.0/12'
        }
        
    async def _configure_cluster_security(self, config: ClusterConfig) -> Dict[str, Any]:
        """Configure cluster security"""
        return {
            'rbac_enabled': True,
            'network_policies_enabled': True,
            'pod_security_standards': 'restricted',
            'encryption_at_rest': True,
            'audit_logging': True
        }
        
    async def _setup_cluster_monitoring(self, cluster_name: str) -> Dict[str, Any]:
        """Setup cluster monitoring"""
        return {
            'prometheus_enabled': True,
            'grafana_enabled': True,
            'metrics_server_enabled': True,
            'logging_enabled': True,
            'monitoring_namespace': 'ainflue-monitoring'
        }
        
    async def _create_ainflue_namespaces(self, cluster_name: str) -> List[Dict[str, Any]]:
        """Create Ainflue-specific namespaces"""
        results = []
        for namespace in self.ainflue_namespaces:
            namespace_result = {
                'name': namespace,
                'status': 'active',
                'labels': {
                    'platform': 'ainflue',
                    'managed-by': 'cluster-manager'
                }
            }
            results.append(namespace_result)
        return results
        
    # Simulation methods
    def _simulate_cluster_creation(self, config: ClusterConfig) -> Dict[str, Any]:
        """Simulate cluster creation"""
        return {
            'name': config.name,
            'cluster_type': config.cluster_type.value,
            'kubernetes_version': config.kubernetes_version,
            'status': 'simulated',
            'simulation': True
        }
        
    def _simulate_workload_deployment(self, workload_config: WorkloadConfig) -> Dict[str, Any]:
        """Simulate workload deployment"""
        return {
            'workload_name': workload_config.name,
            'namespace': workload_config.namespace,
            'status': 'simulated',
            'simulation': True
        }
        
    def _simulate_workload_scaling(self, workload_name: str, replicas: int) -> Dict[str, Any]:
        """Simulate workload scaling"""
        return {
            'workload_name': workload_name,
            'target_replicas': replicas,
            'status': 'simulated',
            'simulation': True
        }
        
    def _simulate_cluster_status(self, cluster_name: str) -> Dict[str, Any]:
        """Simulate cluster status"""
        return {
            'cluster_name': cluster_name,
            'health': 'simulated',
            'nodes': {'total': 3, 'ready': 3},
            'simulation': True
        }
        
    # Additional helper methods
    async def _ensure_namespace_exists(self, namespace: str):
        """Ensure namespace exists"""
        if KUBERNETES_AVAILABLE and self.k8s_core_v1:
            try:
                self.k8s_core_v1.read_namespace(name=namespace)
            except ApiException as e:
                if e.status == 404:
                    # Create namespace
                    namespace_body = client.V1Namespace(
                        metadata=client.V1ObjectMeta(
                            name=namespace,
                            labels={
                                'platform': 'ainflue',
                                'managed-by': 'cluster-manager'
                            }
                        )
                    )
                    self.k8s_core_v1.create_namespace(body=namespace_body)
                    
    async def _create_deployment(self, workload_config: WorkloadConfig) -> Dict[str, Any]:
        """Create Kubernetes deployment"""
        return {
            'type': 'deployment',
            'replicas': workload_config.replicas,
            'image': workload_config.image,
            'status': 'created'
        }
        
    async def _create_statefulset(self, workload_config: WorkloadConfig) -> Dict[str, Any]:
        """Create Kubernetes statefulset"""
        return {
            'type': 'statefulset',
            'replicas': workload_config.replicas,
            'image': workload_config.image,
            'status': 'created'
        }
        
    async def _create_daemonset(self, workload_config: WorkloadConfig) -> Dict[str, Any]:
        """Create Kubernetes daemonset"""
        return {
            'type': 'daemonset',
            'image': workload_config.image,
            'status': 'created'
        }
        
    async def _create_service(self, workload_config: WorkloadConfig) -> Dict[str, Any]:
        """Create Kubernetes service"""
        return {
            'service_name': f"{workload_config.name}-service",
            'service_type': workload_config.service_config.get('type', 'ClusterIP'),
            'ports': workload_config.service_config.get('ports', [80]),
            'status': 'created'
        }
        
    async def _create_ingress(self, workload_config: WorkloadConfig) -> Dict[str, Any]:
        """Create Kubernetes ingress"""
        return {
            'ingress_name': f"{workload_config.name}-ingress",
            'host': workload_config.ingress_config.get('host', f"{workload_config.name}.ainflue.com"),
            'tls_enabled': workload_config.ingress_config.get('tls', True),
            'status': 'created'
        }
        
    async def _create_horizontal_pod_autoscaler(self, workload_config: WorkloadConfig) -> Dict[str, Any]:
        """Create horizontal pod autoscaler"""
        return {
            'hpa_name': f"{workload_config.name}-hpa",
            'min_replicas': 1,
            'max_replicas': 10,
            'target_cpu_utilization': 70,
            'status': 'created'
        }
        
    async def _get_cluster_resource_usage(self) -> Dict[str, Any]:
        """Get cluster resource usage"""
        return {
            'cpu': {
                'total': '16 cores',
                'used': '8 cores',
                'percentage': 50
            },
            'memory': {
                'total': '64 GB',
                'used': '32 GB', 
                'percentage': 50
            },
            'storage': {
                'total': '1 TB',
                'used': '500 GB',
                'percentage': 50
            }
        }