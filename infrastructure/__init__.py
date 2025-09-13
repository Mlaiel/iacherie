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
try:
    from .container import *
except ImportError:
    pass

try:
    from .deployment import *
except ImportError:
    pass

try:
    from .terraform import *
except ImportError:
    pass

try:
    from .ansible import *
except ImportError:
    pass

from .observability import (
    MonitoringManager, PrometheusManager, GrafanaManager, AlertManager, 
    MetricsCollector, LogAggregator,
    monitoring_manager, prometheus_manager, grafana_manager, alert_manager,
    metrics_collector, log_aggregator
)



from .security_modules import (
    SecurityManager, CertificateManager, VaultManager, PolicyManager, ComplianceManager,
    security_manager, certificate_manager, vault_manager, policy_manager, compliance_manager
)

from .storage_modules import (
    StorageManager, PersistentVolumeManager, BackupManager, ObjectStorageManager,
    storage_manager, pv_manager, backup_manager, object_storage_manager
)

from .scaling import (
    AutoscalingManager, HPAManager, VPAManager, ClusterAutoscaler,
    autoscaling_manager, hpa_manager, vpa_manager, cluster_autoscaler
)

from .deployment import (
    DeploymentManager, CICDManager, PipelineManager,
    BlueGreenDeployer, CanaryDeployer, RollingUpdater, FeatureFlagManager,
    PipelineOrchestrator, EnvironmentManager, RollbackManager, ValidationEngine, ReleaseManager
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