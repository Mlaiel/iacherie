"""Infrastructure Security Module - Ainflue Enterprise Platform
===============================================================
Comprehensive security services for enterprise infrastructure

Author: Fahed Mlaiel <mlaiel@live.de>
Project: Ainflue Infrastructure Enterprise  
License: Proprietary - All rights reserved

This module provides security services:
- Core security functionality
- Authentication and authorization
- Certificate management
- Encryption and key management
- Threat detection and response
- Compliance and auditing
- Vulnerability scanning
- Access control
- Incident response
"""

# Core security functionality (from root security.py)
try:
    from .core_security import *
except ImportError:
    pass

# Authentication module
try:
    from .auth import *
except ImportError:
    pass

# Access control
try:
    from .access_control import *
except ImportError:
    pass

# Certificate management
try:
    from .certificate_manager import *
except ImportError:
    pass

# Compliance auditing
try:
    from .compliance_auditor import *
except ImportError:
    pass

# Encryption management
try:
    from .encryption_manager import *
except ImportError:
    pass

# Incident response
try:
    from .incident_responder import *
except ImportError:
    pass

# Security policies
try:
    from .security_policies import *
except ImportError:
    pass

# Threat detection
try:
    from .threat_detector import *
except ImportError:
    pass

# GDPR compliance
try:
    from .gdpr_compliance import *
except ImportError:
    pass

# CCPA compliance
try:
    from .ccpa_compliance import *
except ImportError:
    pass

# DMCA compliance
try:
    from .dmca_compliance import *
except ImportError:
    pass

# NEW COMPLIANCE MODULES - Decomposed from compliance_manager.py
# Compliance base framework
try:
    from .compliance_base import *
except ImportError:
    pass

# Audit management
try:
    from .audit_manager import *
except ImportError:
    pass

# Legal framework
try:
    from .legal_framework import *
except ImportError:
    pass

# Compliance core orchestration
try:
    from .compliance_core import *
except ImportError:
    pass

__version__ = "2.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__status__ = "Production"

# Collect all exports from submodules
__all__ = []

# Updated module list to include new compliance modules
compliance_modules = ['core_security', 'auth', 'access_control', 'certificate_manager', 
                     'compliance_auditor', 'encryption_manager', 'incident_responder',
                     'security_policies', 'threat_detector', 'vulnerability_scanner',
                     'gdpr_compliance', 'ccpa_compliance', 'dmca_compliance',
                     'compliance_base', 'audit_manager', 'legal_framework', 'compliance_core']

for module_name in compliance_modules:
    try:
        module = getattr(__import__(__name__ + '.' + module_name, fromlist=[module_name]), module_name)
        if hasattr(module, '__all__'):
            __all__.extend(module.__all__)
    except (ImportError, AttributeError):
        pass

# Advanced enterprise security components (Expert Implementation)
try:
    from .zero_trust_security import *
except ImportError:
    pass