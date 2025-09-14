"""
🔒 Backend Security Module - Enterprise Protection Framework
Comprehensive security implementation for Ainflue platform backend

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from .enterprise_security_framework import (
    EnterpriseSecurityFramework,
    SecurityLevel,
    ThreatType,
    AuthenticationMethod,
    create_security_framework,
    get_global_security_framework
)

__version__ = "1.0.0"
__all__ = [
    "EnterpriseSecurityFramework",
    "SecurityLevel", 
    "ThreatType",
    "AuthenticationMethod",
    "create_security_framework",
    "get_global_security_framework"
]