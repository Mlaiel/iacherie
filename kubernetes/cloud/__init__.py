"""Cloud Deployment Module - Enterprise Multi-Cloud Infrastructure
Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

WARNING: This code is protected by copyright law. Any unauthorized copying, 
distribution, or use of this code without explicit written permission from 
Fahed Mlaiel (mlaiel@live.de) is strictly prohibited and will result in 
legal action.

Team Specialties: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + 
Microservices + Audio + DevOps + IA Prompt Engineer

This module provides enterprise-grade cloud deployment capabilities for the
IA Influencer Agent platform, supporting multi-cloud strategies, automated
provisioning, scaling, and optimization for creator content protection and
monetization systems.
"""
from .aws_deployment import AWSDeploymentManager
from .azure_deployment import AzureDeploymentManager
from .gcp_deployment import GCPDeploymentManager
from .multi_cloud_orchestrator import MultiCloudOrchestrator
from .cloud_provisioning import CloudProvisioningEngine
from .cloud_scaling import CloudAutoScaler
from .cloud_monitoring import CloudMonitoringService
from .cloud_security import CloudSecurityManager
from .cloud_storage import CloudStorageManager
from .cloud_networking import CloudNetworkManager
from .cloud_optimization import CloudCostOptimizer
from .cloud_backup import CloudBackupManager
from .cloud_migration import CloudMigrationService
from .disaster_recovery import DisasterRecoveryService
from .cloud_compliance import CloudComplianceManager

__version__ = "2.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"

# Export main classes
__all__ = [
    "AWSDeploymentManager",
    "AzureDeploymentManager", 
    "GCPDeploymentManager",
    "MultiCloudOrchestrator",
    "CloudProvisioningEngine",
    "CloudAutoScaler",
    "CloudMonitoringService",
    "CloudSecurityManager",
    "CloudStorageManager",
    "CloudNetworkManager",
    "CloudCostOptimizer",
    "CloudBackupManager",
    "CloudMigrationService",
    "DisasterRecoveryService",
    "CloudComplianceManager"
]
    "CloudNetworkManager",
    "CloudCostOptimizer",
    "CloudBackupManager",
    "CloudMigrationService",
    "DisasterRecoveryService",
    "CloudComplianceManager"
]
