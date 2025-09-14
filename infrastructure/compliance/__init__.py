"""
Compliance Module - Enterprise Legal and Regulatory Compliance
================================================================================

Expert Team: Security + Legal + DBA + DevOps
Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

🔒 Security: Compliance automation, security frameworks
⚖️ Legal: GDPR, CCPA, DMCA compliance management
🗄️ DBA: Data governance, audit trails, retention policies
⚙️ DevOps: Automated compliance monitoring, reporting

Enterprise compliance infrastructure for Ainflue platform supporting:
- GDPR compliance for EU creator data protection
- CCPA compliance for California privacy regulations
- DMCA compliance for content protection
- Automated compliance monitoring and reporting
- Audit trail management and documentation
- Global regulatory compliance frameworks
- Creator rights and content licensing compliance
"""

from .gdpr_compliance_manager import GDPRComplianceManager
from .ccpa_compliance_manager import CCPAComplianceManager
from .dmca_compliance_manager import DMCAComplianceManager
from .audit_compliance_manager import AuditComplianceManager
from .global_compliance_manager import GlobalComplianceManager
from .regulatory_compliance import RegulatoryCompliance
from .automated_compliance_checker import AutomatedComplianceChecker
from .compliance_reporting import ComplianceReporting
from .compliance_alerting import ComplianceAlerting
from .compliance_analytics import ComplianceAnalytics
from .regional_compliance import RegionalCompliance
from .compliance_documentation import ComplianceDocumentation

__all__ = [
    'GDPRComplianceManager',
    'CCPAComplianceManager',
    'DMCAComplianceManager',
    'AuditComplianceManager',
    'GlobalComplianceManager',
    'RegulatoryCompliance',
    'AutomatedComplianceChecker',
    'ComplianceReporting',
    'ComplianceAlerting',
    'ComplianceAnalytics',
    'RegionalCompliance',
    'ComplianceDocumentation'
]

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__description__ = "Enterprise compliance infrastructure for legal and regulatory requirements"