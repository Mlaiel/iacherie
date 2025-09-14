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

__all__ = [
    'EnterpriseComplianceCenter',
    'ComplianceReport',
    'GDPRChecker',
    'DMCAProtection'
]

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"