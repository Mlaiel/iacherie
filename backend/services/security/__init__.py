"""Backend Security Services Module

Consolidated security and compliance services for IA Influencer Agent Platform.
Provides enterprise-grade encryption, compliance management, and security monitoring.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 IA Influencer Agent Platform
All Rights Reserved - Unauthorized use, reproduction, or distribution prohibited.
"""

from .encryption.data_encryption import DataEncryptionService
from .encryption.key_management import KeyManagementService  
from .encryption.secure_storage import SecureStorageService
from .compliance.gdpr_manager import GDPRComplianceManager
from .compliance.dmca_handler import DMCAHandler
from .compliance.legal_validator import LegalValidator
from .monitoring.threat_detector import ThreatDetectionService
from .monitoring.security_audit import SecurityAuditService

__all__ = [
    "DataEncryptionService",
    "KeyManagementService", 
    "SecureStorageService",
    "GDPRComplianceManager",
    "DMCAHandler",
    "LegalValidator", 
    "ThreatDetectionService",
    "SecurityAuditService"
]

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel <mlaiel@live.de>"