"""
Global Legal Compliance Framework for Ainflue Platform
Comprehensive compliance management for GDPR, CCPA, DMCA, PIPEDA, LGPD, and PDPA

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved - Unauthorized use prohibited
"""

from .global_compliance import GlobalComplianceManager
from .ccpa_compliance import CCPAComplianceManager
from .pipeda_compliance import PIPEDAComplianceManager
from .lgpd_compliance import LGPDComplianceManager
from .pdpa_compliance import PDPAComplianceManager

__all__ = [
    "GlobalComplianceManager",
    "CCPAComplianceManager", 
    "PIPEDAComplianceManager",
    "LGPDComplianceManager",
    "PDPAComplianceManager"
]

__version__ = "1.0.0"