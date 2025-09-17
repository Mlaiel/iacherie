"""🚀 Platform Core Tenant Management - IA Influencer Agent Platform Enterprise
============================================================================
Module: backend/platform_core/tenant_management/
Author: Fahed Mlaiel (mlaiel@live.de)
============================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🎯 SYSTÈME DE GESTION MULTI-TENANT ENTERPRISE
Isolation complète des données et routage intelligent pour architecture SaaS
- Isolation de données par tenant avec chiffrement
- Routage dynamique et load balancing intelligent
- Gestion des quotas et limites en temps réel
- Facturation et analytics par tenant
"""

from .tenant_manager import (
    TenantManager,
    TenantDataIsolator,
    TenantConfig,
    TenantUsage,
    TenantStatus,
    TenantTier
)

from .tenant_data_isolator import (
    TenantDataIsolator as DataIsolator,
    IsolationLevel,
    DataClassification,
    TenantEncryptionConfig,
    TenantIsolationPolicy,
    get_tenant_data_isolator
)

from .tenant_router_engine import (
    TenantRouterEngine,
    RoutingStrategy,
    LoadBalancingAlgorithm,
    TenantPlan,
    RoutingDecision,
    RequestContext,
    get_tenant_router_engine
)

from .creator_workspace_manager import (
    CreatorWorkspaceManager,
    CreatorType,
    WorkspaceType,
    CollaborationLevel,
    ContentVisibility,
    CreatorProfile,
    WorkspaceConfig,
    get_creator_workspace_manager
)

from .tenant_scaling_orchestrator import (
    TenantScalingOrchestrator,
    ScalingDirection,
    ScalingStrategy,
    ResourceType,
    CloudProvider,
    ScalingEvent,
    get_tenant_scaling_orchestrator
)

from .tenant_compliance_monitor import (
    TenantComplianceMonitor,
    ComplianceFramework,
    DataSubjectRights,
    ComplianceStatus,
    DataLocation,
    PersonalDataRecord,
    ConsentRecord,
    get_tenant_compliance_monitor
)

__all__ = [
    # Core tenant management
    "TenantManager",
    "TenantDataIsolator", 
    "TenantConfig",
    "TenantUsage", 
    "TenantStatus",
    "TenantTier",
    
    # Data isolation
    "DataIsolator",
    "IsolationLevel",
    "DataClassification", 
    "TenantEncryptionConfig",
    "TenantIsolationPolicy",
    "get_tenant_data_isolator",
    
    # Routing engine
    "TenantRouterEngine",
    "RoutingStrategy",
    "LoadBalancingAlgorithm",
    "TenantPlan",
    "RoutingDecision", 
    "RequestContext",
    "get_tenant_router_engine",
    
    # Creator workspaces
    "CreatorWorkspaceManager",
    "CreatorType",
    "WorkspaceType", 
    "CollaborationLevel",
    "ContentVisibility",
    "CreatorProfile",
    "WorkspaceConfig",
    "get_creator_workspace_manager",
    
    # Scaling orchestrator
    "TenantScalingOrchestrator",
    "ScalingDirection",
    "ScalingStrategy",
    "ResourceType", 
    "CloudProvider",
    "ScalingEvent",
    "get_tenant_scaling_orchestrator",
    
    # Compliance monitor
    "TenantComplianceMonitor",
    "ComplianceFramework",
    "DataSubjectRights",
    "ComplianceStatus",
    "DataLocation",
    "PersonalDataRecord", 
    "ConsentRecord",
    "get_tenant_compliance_monitor"
]

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
