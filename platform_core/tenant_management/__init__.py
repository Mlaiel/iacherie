""" Platform Core Tenant Management - IA Influencer Agent Platform Enterprise
============================================================================
Module: backend/platform_core/tenant_management/
Author: Fahed Mlaiel (mlaiel@live.de)
============================================================================

  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL 
© 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

 SYSTÈME DE GESTION MULTI-TENANT ENTERPRISE
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

__all__ = [
    "TenantManager",
    "TenantDataIsolator",
    "TenantConfig", 
    "TenantUsage",
    "TenantStatus",
    "TenantTier"
]

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
