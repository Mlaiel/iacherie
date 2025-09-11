"""MongoDB Security Module for Ainflue Platform
=============================================

Enterprise-grade security implementation for MongoDB including field-level encryption,
role-based access control, audit logging, and compliance validation.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved

WARNING: This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution without explicit written
permission is strictly prohibited and will result in legal action.
Contact: mlaiel@live.de

EXPERT ROLES IMPLEMENTED:
- Security Engineer: Zero-trust security model and threat detection
- DBA: Data encryption and access control
- Lead Dev IA: Security-first AI processing
- Backend Senior: Enterprise security architecture
- Compliance Specialist: GDPR/CCPA compliance validation
"""

import logging
from typing import Dict, Any, Optional

# Configure logging
logger = logging.getLogger(__name__)

# Module metadata
__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__copyright__ = "(c) 2025 Fahed Mlaiel - All Rights Reserved"
__license__ = "Proprietary - Unauthorized use prohibited"

# Track loaded security modules
_loaded_modules = []
_failed_modules = []

def _safe_import(module_name: str) -> bool:
    """Safely import a security module with error handling."""
    try:
        module = __import__(f"mongodb.security.{module_name}", fromlist=[module_name])
        globals().update(getattr(module, '__dict__', {}))
        _loaded_modules.append(module_name)
        logger.info(f"Successfully loaded security.{module_name}")
        return True
    except Exception as e:
        _failed_modules.append((module_name, str(e)))
        logger.warning(f"Failed to load security.{module_name}: {e}")
        return False

# Import security modules
_safe_import('encryption_manager')
_safe_import('access_control')
_safe_import('audit_logger')
_safe_import('compliance_validator')
_safe_import('data_masking')
_safe_import('security_monitor')
_safe_import('backup_encryption')

# Export public interface
__all__ = [
    # Core security classes
    'EncryptionManager',
    'AccessControlManager',
    'AuditLogger',
    'ComplianceValidator',
    'DataMasking',
    'SecurityMonitor',
    'BackupEncryption',
    
    # Utility functions
    'get_encryption_manager',
    'get_access_control',
    'get_audit_logger',
    'get_compliance_validator',
    'validate_security_config',
    
    # Module info
    '__version__',
    '__author__',
    'get_loaded_security_modules',
    'get_failed_security_modules'
]

def get_loaded_security_modules() -> list:
    """Get list of successfully loaded security modules."""
    return _loaded_modules.copy()

def get_failed_security_modules() -> list:
    """Get list of security modules that failed to load."""
    return _failed_modules.copy()

def validate_security_config() -> Dict[str, Any]:
    """Validate overall security configuration."""
    return {
        "loaded_modules": _loaded_modules,
        "failed_modules": _failed_modules,
        "security_status": "active" if _loaded_modules else "degraded",
        "encryption_available": "EncryptionManager" in globals(),
        "access_control_available": "AccessControlManager" in globals(),
        "audit_logging_available": "AuditLogger" in globals(),
        "compliance_ready": "ComplianceValidator" in globals()
    }

# Module initialization complete
logger.info(f"MongoDB Security module initialized - Version {__version__}")
if _failed_modules:
    logger.warning(f"Some security modules failed to load: {[name for name, _ in _failed_modules]}")