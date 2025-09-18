"""Enterprise SEO Management Package
Advanced enterprise-level SEO management and governance.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  AVERTISSEMENT LÉGAL OBLIGATOIRE:
==========================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques
"""

# Core Governance Framework
from .seo_governance_framework import SEOGovernanceFramework

# Phase 1: Security & Compliance
from .enterprise_security_manager import EnterpriseSecurityManager
from .legal_compliance_engine import LegalComplianceEngine
from .brand_protection_suite import BrandProtectionSuite
from .audit_trail_manager import AuditTrailManager

# Phase 2: Analytics & Strategy
from .executive_analytics_dashboard import ExecutiveAnalyticsDashboard
from .enterprise_strategy_engine import EnterpriseStrategyEngine
from .data_governance_platform import DataGovernancePlatform

__all__ = [
    # Core Governance
    "SEOGovernanceFramework",
    
    # Security & Compliance
    "EnterpriseSecurityManager",
    "LegalComplianceEngine", 
    "BrandProtectionSuite",
    "AuditTrailManager",
    
    # Analytics & Strategy
    "ExecutiveAnalyticsDashboard",
    "EnterpriseStrategyEngine",
    "DataGovernancePlatform"
]