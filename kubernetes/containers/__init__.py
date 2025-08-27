"""
🐳 Containers Module - IA-Influencer-Agent Deployment Infrastructure
=====================================================================
Expert Team: DevOps Engineer + Cloud Architect + Security Engineer
Creator: Fahed Mlaiel <mlaiel@live.de>
Company: IA-Influencer-Agent Professional Platform
=====================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE - AVERTISSEMENT LÉGAL ⚠️
Tout vol, copie ou utilisation non autorisée de ce code source,
de ce concept ou de cette propriété intellectuelle sans
l'autorisation écrite explicite de Fahed Mlaiel est strictement
interdite et constituera une violation des lois sur le droit d'auteur.

Contact légal: mlaiel@live.de

Advanced containerization management for IA-Influencer-Agent platform.
Includes Docker, Kubernetes, Helm charts, service mesh, and container security.
"""

__version__ = "2.1.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__company__ = "IA-Influencer-Agent Platform"
__legal__ = "All rights reserved. Unauthorized use prohibited."

# Core imports
from typing import Any, Dict, List, Optional, Union, Tuple
import logging
import asyncio
from datetime import datetime

# Container management imports
from .docker_config import DockerConfigManager, DockerImageBuilder, DockerRegistryManager
from .kubernetes_config import KubernetesConfigManager, KubernetesDeploymentManager, KubernetesPodManager
from .container_orchestrator import ContainerOrchestrator, ServiceMeshManager, ContainerScaler
from .container_security import ContainerSecurityManager, VulnerabilityScanner, ComplianceValidator
from .container_monitoring import ContainerMonitoringManager, MetricsCollector, AlertManager
from .container_registry import ContainerRegistryManager, ImagePipelineManager, ArtifactManager
from .helm_manager import HelmChartManager, HelmDeploymentManager, HelmTemplateEngine
from .container_networking import ContainerNetworkManager, ServiceDiscoveryManager, LoadBalancerManager
from .container_storage import ContainerStorageManager, PersistentVolumeManager, StorageClassManager
from .container_backup import ContainerBackupManager, DataPersistenceManager, DisasterRecoveryManager

# Platform management
from .index import (
    ContainerPlatformManager,
    deploy_ia_influencer_platform,
    get_platform_health,
    get_platform_manager
)

# Module logger
logger = logging.getLogger(__name__)

# Container platform configuration
CONTAINER_PLATFORMS = {
    'docker': {
        'runtime': 'docker',
        'supported_architectures': ['amd64', 'arm64'],
        'registry_support': True
    },
    'kubernetes': {
        'runtime': 'containerd',
        'orchestration': True,
        'auto_scaling': True,
        'service_mesh': True
    },
    'helm': {
        'package_manager': True,
        'templating': True,
        'version_management': True
    }
}

# Export classes/functions
__all__ = [
    # Core managers
    "DockerConfigManager",
    "DockerImageBuilder", 
    "DockerRegistryManager",
    "KubernetesConfigManager",
    "KubernetesDeploymentManager",
    "KubernetesPodManager",
    
    # Orchestration
    "ContainerOrchestrator",
    "ServiceMeshManager",
    "ContainerScaler",
    
    # Security
    "ContainerSecurityManager",
    "VulnerabilityScanner",
    "ComplianceValidator",
    
    # Monitoring
    "ContainerMonitoringManager",
    "MetricsCollector",
    "AlertManager",
    
    # Registry & Pipeline
    "ContainerRegistryManager",
    "ImagePipelineManager",
    "ArtifactManager",
    
    # Helm
    "HelmChartManager",
    "HelmDeploymentManager",
    "HelmTemplateEngine",
    
    # Networking
    "ContainerNetworkManager",
    "ServiceDiscoveryManager",
    "LoadBalancerManager",
    
    # Storage
    "ContainerStorageManager",
    "PersistentVolumeManager",
    "StorageClassManager",
    
    # Backup & Recovery
    "ContainerBackupManager",
    "DataPersistenceManager",
    "DisasterRecoveryManager",
    
    # Platform Management
    "ContainerPlatformManager",
    "deploy_ia_influencer_platform",
    "get_platform_health",
    "get_platform_manager",
    
    # Configuration
    "CONTAINER_PLATFORMS"
]
