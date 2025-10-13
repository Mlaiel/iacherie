"""
🛡️ Enterprise Compliance Center - Conformité Enterprise
=======================================================

Centre compliance ultra-avancé pour conformité réglementaire.
GDPR, DMCA, protection données et audit automatisé.

Architecture: monitoring/enterprise_compliance_center/ (NIVEAU 2)
Responsabilité: Conformité GDPR/DMCA, audit légal, protection données

© 2025 Fahed Mlaiel - Architecture Monitoring Propriétaire Ultra-Avancée
"""

from .index import (
    EnterpriseComplianceCenter,
    ComplianceReport,
    GDPRChecker,
    DMCAProtection
)

# Import new compliance modules
from .creator_economy_gdpr_compliance_engine import CreatorEconomyGDPRComplianceEngine
from .dmca_copyright_protection_intelligence import DMCACopyrightProtectionIntelligence
from .creator_data_privacy_orchestrator import CreatorDataPrivacyOrchestrator
from .multi_jurisdiction_compliance_manager import MultiJurisdictionComplianceManager
from .creator_content_compliance_validator import CreatorContentComplianceValidator
from .audit_trail_intelligence_system import AuditTrailIntelligenceSystem

__all__ = [
    # Original modules
    'EnterpriseComplianceCenter',
    'ComplianceReport', 
    'GDPRChecker',
    'DMCAProtection',
    # New enterprise modules
    'CreatorEconomyGDPRComplianceEngine',
    'DMCACopyrightProtectionIntelligence',
    'CreatorDataPrivacyOrchestrator',
    'MultiJurisdictionComplianceManager',
    'CreatorContentComplianceValidator',
    'AuditTrailIntelligenceSystem'
]

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"