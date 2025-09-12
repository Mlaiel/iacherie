"""🚀 ML Deployment Module - IA Influencer Agent Platform Enterprise
================================================================
Module: backend/ml/deployment/__init__.py
Author: Fahed Mlaiel (mlaiel@live.de)
================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🎯 MODULE DE DÉPLOIEMENT ML
Système complet de déploiement de modèles ML
- Docker et Kubernetes deployment
- Strategies avancées (Blue-Green, Canary)
- Auto-scaling et load balancing
- Health monitoring et rollback
"""

from .deployment_manager import (
    ModelDeploymentManager,
    DeploymentConfig,
    DeploymentInfo,
    PerformanceMetrics,
    DeploymentType,
    DeploymentStrategy,
    DeploymentStatus,
    DeploymentManagerFactory
)

from .containerization_manager import (
    ContainerizationManager,
    ContainerConfig,
    ImagePurpose,
    OptimizationLevel,
    SecurityLevel,
    BuildResult,
    ContainerMetrics
)

from .auto_scaling_manager import (
    AutoScalingManager,
    ScalingTrigger,
    ScalingPolicy,
    ScalingRule,
    ScalingAction,
    WorkloadPattern,
    ScalingMetric
)

from .load_balancing_optimizer import (
    LoadBalancingOptimizer,
    LoadBalancingAlgorithm,
    RoutingStrategy,
    BackendNode,
    RequestContext,
    RoutingDecision,
    PerformanceMetrics as LoadBalancingMetrics
)

from .cloud_deployment_orchestrator import (
    CloudDeploymentOrchestrator,
    CloudConfiguration,
    DeploymentSpec,
    DeploymentInstance,
    CloudProvider,
    DeploymentRegion,
    InstanceType,
    DeploymentStatus as CloudDeploymentStatus
)

# NEW - Deployment Rollback (PHASE 23)
from .deployment_rollback_manager import (
    DeploymentRollbackManager,
    DeploymentSnapshot,
    RollbackPlan,
    RollbackReason,
    DeploymentStatus as RollbackDeploymentStatus
)

__all__ = [
    # Core Deployment (Existing)
    'ModelDeploymentManager',
    'DeploymentConfig',
    'DeploymentInfo',
    'PerformanceMetrics',
    'DeploymentType',
    'DeploymentStrategy',
    'DeploymentStatus',
    'DeploymentManagerFactory',
    
    # Containerization (NEW - PHASE 3)
    "ContainerizationManager",
    "ContainerConfig",
    "ImagePurpose",
    "OptimizationLevel",
    "SecurityLevel",
    "BuildResult",
    "ContainerMetrics",
    
    # Auto-Scaling (NEW - PHASE 3)
    "AutoScalingManager",
    "ScalingTrigger",
    "ScalingPolicy",
    "ScalingRule",
    "ScalingAction",
    "WorkloadPattern",
    "ScalingMetric",
    
    # Load Balancing (NEW - PHASE 3)
    "LoadBalancingOptimizer",
    "LoadBalancingAlgorithm",
    "RoutingStrategy",
    "BackendNode",
    "RequestContext",
    "RoutingDecision",
    "LoadBalancingMetrics",
    
    # Cloud Deployment (NEW - PHASE 2)
    "CloudDeploymentOrchestrator",
    "CloudConfiguration",
    "DeploymentSpec",
    "DeploymentInstance",
    "CloudProvider",
    "DeploymentRegion",
    "InstanceType",
    "CloudDeploymentStatus",
    
    # Deployment Rollback (NEW - PHASE 23)
    "DeploymentRollbackManager",
    "DeploymentSnapshot",
    "RollbackPlan",
    "RollbackReason",
    "RollbackDeploymentStatus"
]

# Version du module
__version__ = "1.0.0"

# Metadata
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__copyright__ = "(c) 2025 Fahed Mlaiel. Tous droits réservés."