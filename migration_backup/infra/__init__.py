# Ainflue Infrastructure Module
# =============================
# 
# Enterprise-grade infrastructure management for Ainflue platform
# Supports multi-cloud deployment and enterprise security
#
# Author: Fahed Mlaiel <mlaiel@live.de>
# Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
#
# ⚠️  PROPRIETARY SOFTWARE - UNAUTHORIZED USE STRICTLY PROHIBITED ⚠️

"""
Ainflue Infrastructure Module

This module provides enterprise-grade infrastructure management capabilities
for the Ainflue platform, supporting multi-cloud deployment and enterprise security.

Features:
    - Multi-cloud provider support (AWS, GCP, Azure)
    - Infrastructure as Code (Terraform, Ansible)
    - Container orchestration (Kubernetes, Helm)
    - Enterprise security and compliance
    - Monitoring and observability
    - Auto-scaling and resource management
"""

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel <mlaiel@live.de>"
__license__ = "Proprietary"

# Infrastructure management components
from .cloud_platform_manager import CloudPlatformManager
from .enterprise_deployment_orchestrator import EnterpriseDeploymentOrchestrator
from .infrastructure_configuration_manager import InfrastructureConfigurationManager
from .resource_provisioning_engine import ResourceProvisioningEngine

# Multi-cloud provider components
from .aws_infrastructure_provider import AWSInfrastructureProvider
from .azure_infrastructure_provider import AzureInfrastructureProvider
from .gcp_infrastructure_provider import GCPInfrastructureProvider
from .multi_cloud_orchestrator import MultiCloudOrchestrator
from .hybrid_cloud_management import HybridCloudManagement

__all__ = [
    # Core Infrastructure Management
    "CloudPlatformManager",
    "EnterpriseDeploymentOrchestrator", 
    "InfrastructureConfigurationManager",
    "ResourceProvisioningEngine",
    
    # Multi-Cloud Provider Integration
    "AWSInfrastructureProvider",
    "AzureInfrastructureProvider",
    "GCPInfrastructureProvider",
    "MultiCloudOrchestrator",
    "HybridCloudManagement",
]

# Configuration constants
SUPPORTED_CLOUD_PROVIDERS = ["aws", "azure", "gcp"]
SUPPORTED_ENVIRONMENTS = ["dev", "staging", "prod"]
DEFAULT_REGION_MAPPING = {
    "aws": "us-west-2",
    "azure": "West US 2", 
    "gcp": "us-west2"
}

# Infrastructure service endpoints
INFRASTRUCTURE_ENDPOINTS = {
    "monitoring": "/monitoring",
    "security": "/security",
    "networking": "/networking",
    "storage": "/storage",
    "deployment": "/deployment"
}

def get_infrastructure_info():
    """Get infrastructure module information."""
    return {
        "version": __version__,
        "author": __author__,
        "supported_providers": SUPPORTED_CLOUD_PROVIDERS,
        "supported_environments": SUPPORTED_ENVIRONMENTS,
        "endpoints": INFRASTRUCTURE_ENDPOINTS
    }

def validate_environment(environment: str) -> bool:
    """Validate if environment is supported."""
    return environment in SUPPORTED_ENVIRONMENTS

def validate_cloud_provider(provider: str) -> bool:
    """Validate if cloud provider is supported."""
    return provider in SUPPORTED_CLOUD_PROVIDERS

def get_default_region(provider: str) -> str:
    """Get default region for cloud provider."""
    return DEFAULT_REGION_MAPPING.get(provider, "us-west-1")