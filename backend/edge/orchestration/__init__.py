"""Edge Orchestration Module
==========================

Service orchestration and container management for edge computing infrastructure.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

# Service mesh
from .service_mesh import (
    EdgeServiceMesh,
    ServiceDiscovery,
    TrafficPolicy,
    create_service_mesh
)

# Container orchestrator
from .container_orchestrator import (
    ContainerOrchestrator,
    ContainerSpec,
    DeploymentStrategy,
    create_container_orchestrator
)

# Kubernetes edge
from .kubernetes_edge import (
    KubernetesEdge,
    EdgeCluster,
    WorkloadType,
    create_kubernetes_edge
)

# Workflow engine
from .workflow_engine import (
    WorkflowEngine,
    WorkflowDefinition,
    WorkflowStatus,
    create_workflow_engine
)

# Auto scaler
from .auto_scaler import (
    AutoScaler,
    ScalingPolicy,
    ScalingMetric,
    create_auto_scaler
)

# Deployment manager
from .deployment_manager import (
    DeploymentManager,
    DeploymentPlan,
    DeploymentStatus,
    create_deployment_manager
)

# Rollback controller
from .rollback_controller import (
    RollbackController,
    RollbackPolicy,
    create_rollback_controller
)

__all__ = [
    # Service mesh
    "EdgeServiceMesh",
    "ServiceDiscovery",
    "TrafficPolicy",
    "create_service_mesh",
    
    # Container orchestration
    "ContainerOrchestrator",
    "ContainerSpec",
    "DeploymentStrategy",
    "create_container_orchestrator",
    
    # Kubernetes edge
    "KubernetesEdge",
    "EdgeCluster",
    "WorkloadType",
    "create_kubernetes_edge",
    
    # Workflow engine
    "WorkflowEngine",
    "WorkflowDefinition",
    "WorkflowStatus",
    "create_workflow_engine",
    
    # Auto scaling
    "AutoScaler",
    "ScalingPolicy",
    "ScalingMetric",
    "create_auto_scaler",
    
    # Deployment management
    "DeploymentManager",
    "DeploymentPlan",
    "DeploymentStatus",
    "create_deployment_manager",
    
    # Rollback control
    "RollbackController",
    "RollbackPolicy",
    "create_rollback_controller"
]