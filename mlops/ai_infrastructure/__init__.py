"""
AI Infrastructure Module
Enterprise-grade AI infrastructure management and orchestration

Components:
- Kubernetes orchestration and GPU cluster management
- Multi-cloud deployment and container optimization
- Resource management and auto-scaling
- Infrastructure security and health monitoring
- Environment management and edge deployment

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from .kubernetes_orchestrator import KubernetesOrchestrator
from .container_optimizer import ContainerOptimizer
from .multi_cloud_deployer import MultiCloudDeployer
from .load_balancer_optimizer import LoadBalancerOptimizer
from .resource_autoscaler import ResourceAutoscaler
from .resource_scheduler import ResourceScheduler
from .capacity_planner import CapacityPlanner
from .security_manager import SecurityManager
from .secrets_manager import SecretsManager
from .health_check_manager import HealthCheckManager
from .environment_manager import EnvironmentManager
from .edge_deployment_controller import EdgeDeploymentController

__version__ = "1.0.0"
__all__ = [
    "KubernetesOrchestrator",
    "ContainerOptimizer", 
    "MultiCloudDeployer",
    "LoadBalancerOptimizer",
    "ResourceAutoscaler",
    "ResourceScheduler",
    "CapacityPlanner",
    "SecurityManager",
    "SecretsManager",
    "HealthCheckManager",
    "EnvironmentManager",
    "EdgeDeploymentController"
]