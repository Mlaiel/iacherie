# -*- coding: utf-8 -*-
"""Security Tests Module - Ainflue Platform
==========================================

Comprehensive security testing module for the Ainflue platform.
Organized into dedicated test modules for different security aspects:

- test_authentication.py: Authentication security tests (password hashing, JWT, MFA)
- test_authorization.py: Authorization and access control tests  
- test_data_encryption.py: Data encryption and protection tests
- test_api_security.py: API security headers, CORS, validation tests
- test_vulnerability_scan.py: Vulnerability scanning and security auditing tests

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"

# Security test categories
SECURITY_TEST_CATEGORIES = [
    "authentication",
    "authorization", 
    "data_encryption",
    "api_security",
    "vulnerability_scan"
]

# Import all security test modules for convenience
try:
    from . import test_authentication
    from . import test_authorization
    from . import test_data_encryption
    from . import test_api_security
    from . import test_vulnerability_scan
    
    __all__ = [
        "test_authentication",
        "test_authorization", 
        "test_data_encryption",
        "test_api_security",
        "test_vulnerability_scan",
        "SECURITY_TEST_CATEGORIES"
    ]
except ImportError as e:
    # Graceful fallback if imports fail
    __all__ = ["SECURITY_TEST_CATEGORIES"]