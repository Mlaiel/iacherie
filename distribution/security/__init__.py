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

from .audit_logger import (
    AuditLogger,
    AuditEvent,
    AuditEventType,
    AuditSeverity,
    AuditLogConfig,
    log_authentication_event,
    log_api_call,
    log_security_violation,
    log_distribution_event
)

from .data_protection_manager import (
    DataProtectionManager,
    ConsentRecord,
    DataProcessingRecord,
    DataSubjectRequest,
    EncryptionConfig,
    DataCategory,
    ConsentType,
    DataSubjectRight
)

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
    'RateLimitResult',
    
    # Audit Logging
    'AuditLogger',
    'AuditEvent',
    'AuditEventType',
    'AuditSeverity',
    'AuditLogConfig',
    'log_authentication_event',
    'log_api_call',
    'log_security_violation',
    'log_distribution_event',
    
    # Data Protection
    'DataProtectionManager',
    'ConsentRecord',
    'DataProcessingRecord',
    'DataSubjectRequest',
    'EncryptionConfig',
    'DataCategory',
    'ConsentType',
    'DataSubjectRight'
]

__version__ = "1.0.0"