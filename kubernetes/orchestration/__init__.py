"""
IA Influencer Agent - Orchestration Deployment Module
Enterprise container orchestration and management

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved - Unauthorized use prohibited

Team Specialties:
- Lead Dev IA: Fahed Mlaiel
- Backend Senior: Fahed Mlaiel  
- ML Engineer: Fahed Mlaiel
- DBA: Fahed Mlaiel
- Security Expert: Fahed Mlaiel
- Microservices Architect: Fahed Mlaiel
- Audio Processing: Fahed Mlaiel
- DevOps Engineer: Fahed Mlaiel
- IA Prompt Engineer: Fahed Mlaiel

⚠️  PROPRIETARY SOFTWARE WARNING ⚠️
This code is the exclusive property of Fahed Mlaiel (mlaiel@live.de).
Any unauthorized use, copying, modification, or distribution of this code
without explicit written permission from the author is strictly prohibited
and may result in legal action. All rights reserved.
"""

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"

from .kubernetes_manager import KubernetesManager
from .helm_manager import HelmManager
from .cluster_manager import ClusterManager
from .service_mesh import ServiceMeshManager
from .orchestration_coordinator import OrchestrationCoordinator
from .container_registry import ContainerRegistryManager
from .load_balancer import LoadBalancerManager
from .automated_deployment import AutomatedDeploymentManager
from .configuration_manager import ConfigurationManager

__all__ = [
    "KubernetesManager",
    "HelmManager",
    "ClusterManager",
    "ServiceMeshManager",
    "OrchestrationCoordinator",
    "ContainerRegistryManager",
    "LoadBalancerManager",
    "AutomatedDeploymentManager",
    "ConfigurationManager"
]
