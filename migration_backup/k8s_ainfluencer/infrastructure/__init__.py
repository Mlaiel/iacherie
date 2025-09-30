"""Infrastructure Deployment Module for IA Influencer Agent Platform

This module provides comprehensive infrastructure deployment and management
capabilities for the IA Influencer Agent platform, supporting multi-cloud
deployments, advanced security, compliance, and high-performance computing.

Industrial-grade infrastructure components:
- Multi-cloud provider abstraction (AWS, GCP, Azure)
- Container orchestration with Kubernetes
- Database provisioning and management
- Vector database infrastructure
- Monitoring and observability stack
- Advanced security and threat detection
- Performance optimization and caching
- Compliance and audit infrastructure
- Network security and service mesh
- Deployment orchestration and rollback management
- Environment management and provisioning
- Real-time alerting and notification systems

Project: IA Influencer Agent + Content Protection Platform
Author: Fahed Mlaiel <mlaiel@live.de>

⚠️  PROPRIETARY SOFTWARE - UNAUTHORIZED USE STRICTLY PROHIBITED ⚠️
⚠️  This software is protected by international copyright laws.         ⚠️
⚠️  Unauthorized reproduction, distribution, or use is strictly        ⚠️
⚠️  prohibited and may result in severe civil and criminal penalties.  ⚠️
⚠️  All rights reserved to Fahed Mlaiel (mlaiel@live.de).             ⚠️
"""# Core infrastructure managers
from .cloud_provider import CloudProviderManager
from .container_orchestration import ContainerOrchestrationManager
from .database_provisioning import DatabaseProvisioningManager
from .vector_database import VectorDatabaseManager
from .monitoring_stack import MonitoringStackManager
from .networking import NetworkingManager
from .load_balancing import LoadBalancerManager
from .resource_scaling import ResourceScalingManager
from .service_mesh import ServiceMeshManager
from .storage_management import StorageManager

# Advanced infrastructure managers
from .enterprise_security_infrastructure import EnterpriseSecurityInfrastructureManager
from .performance_optimization import PerformanceOptimizationManager
from .compliance_manager import ComplianceManager
from .compliance_audit import ComplianceAuditManager
from .communication_infrastructure import CommunicationInfrastructureManager
from .cloud_resource_management import CloudResourceManagementManager
from .content_protection_infrastructure import ContentProtectionInfrastructureManager
from .revenue_tracking_infrastructure import RevenueTrackingInfrastructureManager
from .realtime_alert_infrastructure import RealtimeAlertInfrastructureManager

# Deployment and environment managers
from .deployment_orchestrator import DeploymentOrchestrator
from .environment_manager import EnvironmentManager
from .rollback_manager import RollbackManager

# Main infrastructure manager
from .index import IAInfluencerInfrastructureManager

# Export all public interfaces
__all__ = [
    # Core managers
    'CloudProviderManager',
    'ContainerOrchestrationManager', 
    'DatabaseProvisioningManager',
    'VectorDatabaseManager',
    'MonitoringStackManager',
    'NetworkingManager',
    'LoadBalancerManager',
    'ResourceScalingManager',
    'ServiceMeshManager',
    'StorageManager',
    
    # Advanced managers
    'EnterpriseSecurityInfrastructureManager',
    'PerformanceOptimizationManager',
    'ComplianceManager',
    'ComplianceAuditManager',
    'CommunicationInfrastructureManager',
    'CloudResourceManagementManager',
    'ContentProtectionInfrastructureManager',
    'RevenueTrackingInfrastructureManager',
    'RealtimeAlertInfrastructureManager',
    
    # Deployment and environment managers
    'DeploymentOrchestrator',
    'EnvironmentManager',
    'RollbackManager',
    
    # Main infrastructure manager
    'IAInfluencerInfrastructureManager'
]

# Version information
__version__ = '3.0.0'
__author__ = 'Fahed Mlaiel'
__email__ = 'mlaiel@live.de'
__license__ = 'Proprietary'
