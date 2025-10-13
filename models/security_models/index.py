"""
🔐 SECURITY MODELS INDEX - ENTERPRISE GRADE
==========================================

Point d'entrée central pour tous les modèles Security Enterprise
Support complet: Protection, Auth, Encryption, Compliance, Threat Intelligence

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
Architecture: Enterprise Security Models with advanced protection patterns
"""

from .base_security_model import BaseSecurityModel
from .content_protection_model import ContentProtectionModel
from .authentication_model import AuthenticationModel
from .authorization_model import AuthorizationModel
from .encryption_model import EncryptionModel
from .audit_log_model import AuditLogModel
from .violation_detection_model import ViolationDetectionModel
from .security_analytics_model import SecurityAnalyticsModel
from .threat_intelligence_model import ThreatIntelligenceModel
from .compliance_model import ComplianceModel
from .privacy_model import PrivacyModel
from .vulnerability_model import VulnerabilityModel
from .incident_response_model import IncidentResponseModel
from .security_metrics_model import SecurityMetricsModel

# Enterprise Security Models Collection
__all__ = [
    # Core Security Models
    'BaseSecurityModel',
    'ContentProtectionModel',
    'SecurityAnalyticsModel',
    'SecurityMetricsModel',
    
    # Authentication & Authorization
    'AuthenticationModel',
    'AuthorizationModel',
    'EncryptionModel',
    
    # Monitoring & Detection
    'AuditLogModel',
    'ViolationDetectionModel',
    'ThreatIntelligenceModel',
    'VulnerabilityModel',
    
    # Compliance & Response
    'ComplianceModel',
    'PrivacyModel',
    'IncidentResponseModel',
]

# Enterprise Security Registry
SECURITY_MODELS_REGISTRY = {
    'core': {
        'base': BaseSecurityModel,
        'protection': ContentProtectionModel,
        'analytics': SecurityAnalyticsModel,
        'metrics': SecurityMetricsModel,
    },
    'auth': {
        'authentication': AuthenticationModel,
        'authorization': AuthorizationModel,
        'encryption': EncryptionModel,
    },
    'monitoring': {
        'audit': AuditLogModel,
        'violations': ViolationDetectionModel,
        'threats': ThreatIntelligenceModel,
        'vulnerabilities': VulnerabilityModel,
    },
    'compliance': {
        'compliance': ComplianceModel,
        'privacy': PrivacyModel,
        'incident': IncidentResponseModel,
    }
}

def get_security_model(category: str, model_type: str):
    """
    Récupère un modèle Security Enterprise par catégorie et type
    
    Args:
        category: core, auth, monitoring, compliance
        model_type: Type spécifique de modèle security
        
    Returns:
        Classe du modèle Security Enterprise correspondant
    """
    return SECURITY_MODELS_REGISTRY.get(category, {}).get(model_type)

def list_available_security_models():
    """Liste tous les modèles Security Enterprise disponibles"""
    return SECURITY_MODELS_REGISTRY

# Security Models Enterprise Stats
SECURITY_MODELS_STATS = {
    'total_models': 14,
    'categories': 4,
    'core_models': 4,
    'auth_models': 3,
    'monitoring_models': 4,
    'compliance_models': 3,
    'enterprise_ready': True,
    'gdpr_compliant': True,
    'threat_detection': True,
    'encryption_enabled': True,
    'audit_trail_complete': True
}