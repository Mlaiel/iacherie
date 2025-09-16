"""⚙️ DevOps Automation Module - Enterprise Implementation
======================================================

Module d'automation DevOps enterprise avec CI/CD avancé, Infrastructure as Code
et monitoring distribué pour Ainflue.

Author: Fahed Mlaiel (mlaiel@live.de)
Date: 14 Septembre 2025
"""

from .enterprise_devops_automation import (
    EnterpriseDevOpsAutomation,
    PipelineConfiguration,
    DeploymentJob,
    InfrastructureResource,
    MonitoringAlert,
    DeploymentStage,
    DeploymentStrategy,
    InfrastructureProvider,
    MonitoringLevel,
    AlertSeverity,
    initialize_devops_automation
)

# Phase 1: Infrastructure as Code (5 files) - COMPLETED ✅
from .infrastructure_orchestrator import (
    InfrastructureOrchestrator,
    InfrastructureConfig,
    InfrastructureResource as IaC_InfrastructureResource,
    DeploymentPlan,
    CloudProvider,
    InfrastructureState,
    RecoveryStrategy,
    create_infrastructure_orchestrator
)

from .terraform_automation import (
    TerraformAutomation,
    TerraformWorkspace,
    TerraformModule,
    TerraformPlan,
    StateFile,
    TerraformCommand,
    WorkspaceState,
    StateBackend,
    create_terraform_automation
)

from .kubernetes_orchestrator import (
    KubernetesOrchestrator,
    KubernetesCluster,
    ServiceDeployment,
    IngressRule,
    ServiceMeshConfig,
    ServiceMeshType,
    ScalingPolicy,
    ServiceType,
    IngressClass,
    create_kubernetes_orchestrator
)

from .cloud_provider_abstraction import (
    CloudProviderAbstraction,
    CloudResource,
    CloudAccount,
    MultiCloudDeployment,
    CloudProvider as CPA_CloudProvider,
    ResourceType,
    DeploymentStrategy as CPA_DeploymentStrategy,
    create_cloud_provider_abstraction
)

from .infrastructure_monitoring import (
    InfrastructureMonitoring,
    Metric,
    Alert,
    MonitoringDashboard,
    CapacityPrediction,
    MetricType,
    AlertSeverity as IM_AlertSeverity,
    MonitoringScope,
    ScalingDirection,
    create_infrastructure_monitoring
)

__version__ = "2.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"

__all__ = [
    # Core DevOps Automation
    "EnterpriseDevOpsAutomation",
    "PipelineConfiguration",
    "DeploymentJob",
    "InfrastructureResource",
    "MonitoringAlert",
    "DeploymentStage",
    "DeploymentStrategy",
    "InfrastructureProvider",
    "MonitoringLevel",
    "AlertSeverity",
    "initialize_devops_automation",
    
    # Phase 1: Infrastructure as Code - COMPLETED ✅
    # Infrastructure Orchestrator
    "InfrastructureOrchestrator",
    "InfrastructureConfig",
    "IaC_InfrastructureResource",
    "DeploymentPlan",
    "CloudProvider",
    "InfrastructureState",
    "RecoveryStrategy",
    "create_infrastructure_orchestrator",
    
    # Terraform Automation
    "TerraformAutomation",
    "TerraformWorkspace",
    "TerraformModule",
    "TerraformPlan",
    "StateFile",
    "TerraformCommand",
    "WorkspaceState",
    "StateBackend",
    "create_terraform_automation",
    
    # Kubernetes Orchestrator
    "KubernetesOrchestrator",
    "KubernetesCluster",
    "ServiceDeployment",
    "IngressRule",
    "ServiceMeshConfig",
    "ServiceMeshType",
    "ScalingPolicy",
    "ServiceType",
    "IngressClass",
    "create_kubernetes_orchestrator",
    
    # Cloud Provider Abstraction
    "CloudProviderAbstraction",
    "CloudResource",
    "CloudAccount",
    "MultiCloudDeployment",
    "CPA_CloudProvider",
    "ResourceType",
    "CPA_DeploymentStrategy",
    "create_cloud_provider_abstraction",
    
    # Infrastructure Monitoring
    "InfrastructureMonitoring",
    "Metric",
    "Alert",
    "MonitoringDashboard",
    "CapacityPrediction",
    "MetricType",
    "IM_AlertSeverity",
    "MonitoringScope",
    "ScalingDirection",
    "create_infrastructure_monitoring"
]