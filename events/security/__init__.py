"""Events Security Module

Advanced security utilities for the Ainflue events system.
Ultra-sophisticated threat detection, access control, and compliance management.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

# Core security modules (existing)
from .encryption import EncryptionManager
from .authentication import SecurityManager

# Advanced security modules (new)
from .threat_detection_engine import ThreatDetectionEngine, ThreatLevel, ThreatIndicator, ThreatAnalysisResult
from .access_control_manager import AccessControlManager, Permission, BusinessRole, AuthorizationResult, PermissionScope
from .audit_trail_collector import AuditTrailCollector, AuditRecord, ComplianceValidation, ForensicAnalysis, AuditLevel

__all__ = [
    # Core security
    'EncryptionManager', 
    'SecurityManager',
    
    # Threat detection
    'ThreatDetectionEngine', 
    'ThreatLevel', 
    'ThreatIndicator', 
    'ThreatAnalysisResult',
    
    # Access control
    'AccessControlManager', 
    'Permission', 
    'BusinessRole', 
    'AuthorizationResult', 
    'PermissionScope',
    
    # Audit and compliance
    'AuditTrailCollector', 
    'AuditRecord', 
    'ComplianceValidation', 
    'ForensicAnalysis', 
    'AuditLevel'
]