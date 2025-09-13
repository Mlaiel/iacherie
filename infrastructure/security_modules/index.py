"""
Security Modules - Ainflue Infrastructure Enterprise
===================================================
Point d'entrée principal pour tous les services de sécurité

Author: Fahed Mlaiel (mlaiel@live.de)
Project: Ainflue Infrastructure Enterprise
Version: 2.0 Production
"""

# Imports principaux
from . import *

# Exports publics principaux
__all__ = [
    'SecurityManager',
    'AuthManager',
    'AccessController',
    'ThreatDetector',
    'EncryptionManager',
    'ComplianceAuditor',
    'IncidentResponder',
    'VulnerabilityScanner'
]

# Metadata
__version__ = "2.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__description__ = "Enterprise security infrastructure for Ainflue platform"

# Configuration sécurité métier Ainflue
AINFLUE_SECURITY_WORKFLOW = {
    'upload': 'Content security scanning and validation',
    'ai_processing': 'AI model security and privacy protection', 
    'protection': 'IP rights enforcement and watermarking security',
    'monetization': 'Payment security and fraud detection',
    'collaboration': 'Secure creator matching and communications',
    'seo': 'SEO security and content authenticity',
    'distribution': 'Secure multi-platform distribution'
}

# Compliance requirements pour créateurs
CREATOR_COMPLIANCE_REQUIREMENTS = {
    'GDPR': 'EU data protection compliance',
    'CCPA': 'California privacy compliance',
    'DMCA': 'Digital copyright compliance',
    'SOX': 'Financial reporting compliance',
    'COPPA': 'Children privacy compliance'
}