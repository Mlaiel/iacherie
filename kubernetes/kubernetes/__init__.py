"""
IA Influencer Agent - Kubernetes Deployment Module
Production-ready Kubernetes manifests for enterprise-grade deployment

Copyright (c) 2025 Fahed Mlaiel
Email: mlaiel@live.de
Project: IA Influencer Agent + Content Protection Platform

WARNING: This code and concept are protected by copyright.
Any unauthorized use, reproduction, or distribution without written 
permission from Fahed Mlaiel is strictly prohibited and will be 
prosecuted to the full extent of the law.

Module: backend.deployment.kubernetes
Purpose: Kubernetes orchestration for microservices architecture
Architecture: Cloud-native, scalable, enterprise deployment
"""

from .cluster_orchestrator import (
    KubernetesClusterOrchestrator,
    ClusterConfig,
    DeploymentStatus,
    ServiceType,
    NamespaceType,
    DeploymentMetrics,
    cluster_orchestrator,
    get_cluster_orchestrator,
    initialize_cluster_orchestrator
)

__version__ = "2.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__status__ = "Production"

# Kubernetes deployment components
__all__ = [
    "namespaces",
    "configmaps", 
    "secrets",
    "services",
    "deployments",
    "statefulsets",
    "ingress",
    "monitoring",
    "storage",
    "networking",
    "rbac",
    "hpa",
    "KubernetesClusterOrchestrator",
    "ClusterConfig",
    "DeploymentStatus",
    "ServiceType",
    "NamespaceType", 
    "DeploymentMetrics",
    "cluster_orchestrator",
    "get_cluster_orchestrator",
    "initialize_cluster_orchestrator"
]
