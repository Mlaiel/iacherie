"""
Security Module for Ainflue Distribution Platform

This module provides comprehensive security management for content distribution,
including API security, credential management, access control, and threat detection.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

# Available imports - only import what exists
from .access_controller import (
    AccessController,
    Permission,
    Role,
    AccessContext,
    AccessRequest,
    AccessResult
)

from .threat_detector import (
    ThreatDetector,
    ThreatEvent,
    ThreatPattern,
    ThreatType,
    ThreatLevel
)

from .rate_limit_enforcer import (
    RateLimitEnforcer,
    RateLimitType,
    RateLimitRule,
    RateLimitResult
)

# TODO: Add imports for remaining security modules when implemented
# from .api_security_manager import APISecurityManager
# from .credential_vault import CredentialVault
# from .audit_logger import AuditLogger

__all__ = [
    # Access Control
    'AccessController',
    'Permission',
    'Role',
    'AccessContext',
    'AccessRequest',
    'AccessResult',
    
    # Threat Detection
    'ThreatDetector',
    'ThreatEvent',
    'ThreatPattern',
    'ThreatType',
    'ThreatLevel',
    
    # Rate Limiting
    'RateLimitEnforcer',
    'RateLimitType',
    'RateLimitRule',
    'RateLimitResult'
]

__version__ = "1.0.0"