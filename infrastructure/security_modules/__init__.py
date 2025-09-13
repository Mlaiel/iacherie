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

# Vulnerability scanner
try:
    from .vulnerability_scanner import *
except ImportError:
    pass

__version__ = "2.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__status__ = "Production"

# Collect all exports from submodules
__all__ = []

for module_name in ['core_security', 'auth', 'access_control', 'certificate_manager', 
                   'compliance_auditor', 'encryption_manager', 'incident_responder',
                   'security_policies', 'threat_detector', 'vulnerability_scanner']:
    try:
        module = getattr(__import__(__name__ + '.' + module_name, fromlist=[module_name]), module_name)
        if hasattr(module, '__all__'):
            __all__.extend(module.__all__)
    except (ImportError, AttributeError):
        pass