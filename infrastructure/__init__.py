"""Infrastructure Module - IA-Influencer-Agent Platform
===========================================================
Enterprise-grade infrastructure management consolidation

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform
License: Proprietary - All rights reserved

WARNING: This code and concept are protected by copyright.
Any unauthorized use, reproduction, or distribution without written 
permission from Fahed Mlaiel is strictly prohibited and will be 
prosecuted to the full extent of the law.

This module consolidates all infrastructure components into a unified interface:
- Kubernetes orchestration and management
- Docker containerization and builds  
- Terraform Infrastructure as Code
- Ansible configuration management
- Monitoring (Prometheus, Grafana, ELK)
- Networking (Load balancers, ingress, DNS)
- Security (Certificates, secrets, policies)
- Storage (Persistent volumes, backups)
- Autoscaling (HPA, VPA, cluster scaling)
- Deployment (CI/CD pipelines)
- Helm charts and package management
- Custom operators and CRDs
"""

# Import all consolidated infrastructure modules
from .kubernetes import (
    KubernetesManager, ClusterOrchestrator, KubernetesDeploymentManager,
    PodManager, ServiceManager, ConfigMapManager, SecretManager, NamespaceManager,
    kubernetes_manager, cluster_orchestrator
)

from .docker import (
    DockerManager, ContainerManager, ImageBuilder, RegistryManager, DockerComposeManager,
    docker_manager, container_manager, image_builder, registry_manager, compose_manager
)

from .terraform import (
    TerraformManager, InfrastructureProvisioner, CloudResourceManager, StateManager,
    terraform_manager, infrastructure_provisioner, cloud_resource_manager, state_manager
)

from .ansible import (
    AnsibleManager, PlaybookRunner, ConfigurationManager, InventoryManager,
    ansible_manager, playbook_runner, configuration_manager, inventory_manager
)

from .monitoring import (
    MonitoringManager, PrometheusManager, GrafanaManager, AlertManager, 
    MetricsCollector, LogAggregator,
    monitoring_manager, prometheus_manager, grafana_manager, alert_manager,
    metrics_collector, log_aggregator
)

from .networking import (
    NetworkingManager, LoadBalancerManager, IngressManager, DNSManager, ServiceMeshManager,
    networking_manager, load_balancer_manager, ingress_manager, dns_manager, service_mesh_manager
)

from .security import (
    SecurityManager, CertificateManager, VaultManager, PolicyManager, ComplianceManager,
    security_manager, certificate_manager, vault_manager, policy_manager, compliance_manager
)

from .storage import (
    StorageManager, PersistentVolumeManager, BackupManager, ObjectStorageManager,
    storage_manager, pv_manager, backup_manager, object_storage_manager
)

from .autoscaling import (
    AutoscalingManager, HPAManager, VPAManager, ClusterAutoscaler,
    autoscaling_manager, hpa_manager, vpa_manager, cluster_autoscaler
)

from .deployment import (
    DeploymentManager, CICDManager, PipelineManager, ReleaseManager,
    get_deployment_manager, get_cicd_manager, get_pipeline_manager, get_release_manager
)

from .helm import (
    HelmManager, ChartManager, HelmReleaseManager, RepositoryManager,
    helm_manager, chart_manager, helm_release_manager, repository_manager
)

from .operators import (
    OperatorManager, CRDManager, CustomControllerManager, OperatorLifecycleManager,
    operator_manager, crd_manager, custom_controller_manager, operator_lifecycle_manager
)

__version__ = "2.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__status__ = "Production"

__all__ = [
    # Kubernetes consolidation
    "KubernetesManager",
    "ClusterOrchestrator", 
    "KubernetesDeploymentManager",
    "PodManager",
    "ServiceManager",
    "ConfigMapManager",
    "SecretManager",
    "NamespaceManager",
    
    # Docker consolidation
    "DockerManager",
    "ContainerManager",
    "ImageBuilder",
    "RegistryManager",
    "DockerComposeManager",
    
    # Terraform consolidation 
    "TerraformManager",
    "InfrastructureProvisioner",
    "CloudResourceManager",
    "StateManager",
    
    # Ansible consolidation
    "AnsibleManager",
    "PlaybookRunner",
    "ConfigurationManager", 
    "InventoryManager",
    
    # Monitoring consolidation
    "MonitoringManager",
    "PrometheusManager",
    "GrafanaManager",
    "AlertManager",
    "MetricsCollector",
    "LogAggregator",
    
    # Networking consolidation
    "NetworkingManager",
    "LoadBalancerManager",
    "IngressManager",
    "DNSManager",
    "ServiceMeshManager",
    
    # Security consolidation
    "SecurityManager",
    "CertificateManager",
    "VaultManager",
    "PolicyManager",
    "ComplianceManager",
    
    # Storage consolidation
    "StorageManager",
    "PersistentVolumeManager",
    "BackupManager",
    "ObjectStorageManager",
    
    # Autoscaling consolidation
    "AutoscalingManager",
    "HPAManager",
    "VPAManager",
    "ClusterAutoscaler",
    
    # Deployment consolidation
    "DeploymentManager",
    "CICDManager",
    "PipelineManager",
    "ReleaseManager",
    
    # Helm consolidation
    "HelmManager",
    "ChartManager",
    "ReleaseManager",
    "RepositoryManager",
    
    # Operators consolidation
    "OperatorManager",
    "CRDManager",
    "CustomControllerManager",
    "OperatorLifecycleManager"
]