"""
Container Infrastructure Management - Complete Module
====================================================
Enterprise container orchestration for Ainflue platform

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.
"""

# Core container functionality (from root files)
try:
    from .docker import (
        DockerManager, ImageBuilder, ContainerOrchestrator,
        docker_manager, image_builder, container_orchestrator
    )
except ImportError:
    DockerManager = ImageBuilder = ContainerOrchestrator = None
    docker_manager = image_builder = container_orchestrator = None

try:
    from .kubernetes import (
        KubernetesManager, ClusterManager, DeploymentManager, ServiceManager,
        kubernetes_manager, cluster_manager, deployment_manager, service_manager
    )
except ImportError:
    KubernetesManager = ClusterManager = DeploymentManager = ServiceManager = None
    kubernetes_manager = cluster_manager = deployment_manager = service_manager = None

try:
    from .helm import (
        HelmManager, ChartManager, HelmReleaseManager, RepositoryManager,
        helm_manager, chart_manager, helm_release_manager, repository_manager
    )
except ImportError:
    HelmManager = ChartManager = HelmReleaseManager = RepositoryManager = None
    helm_manager = chart_manager = helm_release_manager = repository_manager = None

try:
    from .operators import (
        OperatorManager, CustomResourceManager, ControllerManager,
        operator_manager, custom_resource_manager, controller_manager
    )
except ImportError:
    OperatorManager = CustomResourceManager = ControllerManager = None
    operator_manager = custom_resource_manager = controller_manager = None

try:
    from .networking import (
        NetworkingManager, LoadBalancerManager, IngressManager, DNSManager, ServiceMeshManager,
        networking_manager, load_balancer_manager, ingress_manager, dns_manager, service_mesh_manager
    )
except ImportError:
    NetworkingManager = LoadBalancerManager = IngressManager = DNSManager = ServiceMeshManager = None
    networking_manager = load_balancer_manager = ingress_manager = dns_manager = service_mesh_manager = None

# Specialized container modules
try:
    from .cluster_manager import ClusterManager as AdvancedClusterManager
except ImportError:
    AdvancedClusterManager = None

try:
    from .service_mesh_manager import ServiceMeshManager as AdvancedServiceMeshManager
except ImportError:
    AdvancedServiceMeshManager = None

try:
    from .ingress_controller import IngressController
except ImportError:
    IngressController = None

try:
    from .pod_scheduler import PodScheduler
except ImportError:
    PodScheduler = None

try:
    from .volume_manager import VolumeManager
except ImportError:
    VolumeManager = None

try:
    from .network_policy_manager import NetworkPolicyManager
except ImportError:
    NetworkPolicyManager = None

try:
    from .secret_manager import SecretManager
except ImportError:
    SecretManager = None

try:
    from .registry_manager import RegistryManager
except ImportError:
    RegistryManager = None

try:
    from .load_balancer import LoadBalancer
except ImportError:
    LoadBalancer = None

# Advanced container orchestration (Expert Implementation)
try:
    from .advanced_orchestration_manager import AdvancedOrchestrationManager
except ImportError:
    AdvancedOrchestrationManager = None

__all__ = [
    # Core container functionality
    'DockerManager', 'ImageBuilder', 'ContainerOrchestrator',
    'KubernetesManager', 'ClusterManager', 'DeploymentManager', 'ServiceManager',
    'HelmManager', 'ChartManager', 'HelmReleaseManager', 'RepositoryManager',
    'OperatorManager', 'CustomResourceManager', 'ControllerManager',
    'NetworkingManager', 'LoadBalancerManager', 'IngressManager', 'DNSManager', 'ServiceMeshManager',
    # Specialized modules
    'AdvancedClusterManager', 'AdvancedServiceMeshManager', 'IngressController',
    'PodScheduler', 'VolumeManager', 'NetworkPolicyManager', 
    'SecretManager', 'RegistryManager', 'LoadBalancer',
    # Advanced orchestration
    'AdvancedOrchestrationManager'
]
# Metadata
__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__description__ = "Container infrastructure module for Ainflue creator platform"

