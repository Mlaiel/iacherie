"""
Compliance Module - Enterprise Regulatory Compliance for Ainflue
===============================================================

Advanced compliance infrastructure for GDPR, CCPA, DMCA, and other regulatory
requirements for the creator economy platform.

Author: Fahed Mlaiel (mlaiel@live.de)
Project: Ainflue Infrastructure
Version: 1.0 Production

⚠️ PROPRIÉTÉ INTELLECTUELLE - FAHED MLAIEL
==========================================
Cette architecture est la propriété intellectuelle EXCLUSIVE de Fahed Mlaiel (mlaiel@live.de).
"""

# Core compliance components
# Note: Using lazy imports to avoid circular import issues
try:
    from . import dmca_compliance_manager
except ImportError as e:
    dmca_compliance_manager = None
    import logging
    logging.getLogger(__name__).warning(f"DMCA compliance component not available: {e}")

# Advanced compliance components (Expert Implementation)
try:
    from . import gdpr_compliance_manager
    from . import ccpa_compliance_manager
    from . import audit_compliance_manager
    from . import global_compliance_manager
    from . import regulatory_compliance
    from . import automated_compliance_checker
    from . import compliance_reporting
    from . import compliance_alerting
    from . import compliance_analytics
    from . import regional_compliance
    from . import compliance_documentation
except ImportError as e:
    # Log import errors but continue
    import logging
    logging.getLogger(__name__).warning(f"Some compliance components not available: {e}")
    gdpr_compliance_manager = None
    ccpa_compliance_manager = None
    audit_compliance_manager = None
    global_compliance_manager = None
    regulatory_compliance = None
    automated_compliance_checker = None
    compliance_reporting = None
    compliance_alerting = None
    compliance_analytics = None
    regional_compliance = None
    compliance_documentation = None

__all__ = [
    "dmca_compliance_manager",
    "gdpr_compliance_manager",
    "ccpa_compliance_manager",
    "audit_compliance_manager",
    "global_compliance_manager",
    "regulatory_compliance",
    "automated_compliance_checker",
    "compliance_reporting",
    "compliance_alerting",
    "compliance_analytics",
    "regional_compliance",
    "compliance_documentation"
]

# Module metadata
__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__description__ = "Enterprise Compliance Infrastructure for Ainflue Creator Platform"

# Configuration for compliance regulations
AINFLUE_COMPLIANCE_CONFIG = {
    'supported_regulations': [
        'gdpr',      # General Data Protection Regulation (EU)
        'ccpa',      # California Consumer Privacy Act (US)
        'dmca',      # Digital Millennium Copyright Act (US)
        'coppa',     # Children's Online Privacy Protection Act (US)
        'pipeda',    # Personal Information Protection and Electronic Documents Act (Canada)
        'lgpd',      # Lei Geral de Proteção de Dados (Brazil)
        'pdpa',      # Personal Data Protection Act (Singapore)
        'dpa',       # Data Protection Act (UK)
    ],
    'compliance_features': [
        'data_protection', 'privacy_controls', 'content_protection',
        'audit_trails', 'consent_management', 'data_retention',
        'breach_notification', 'right_to_deletion', 'data_portability'
    ],
    'creator_protections': [
        'copyright_protection', 'content_attribution', 'revenue_protection',
        'collaboration_rights', 'fair_use_enforcement', 'takedown_protection'
    ]
}

# Business Logic Configuration for Creator Platform
CREATOR_PLATFORM_COMPLIANCE = {
    'content_compliance': {
        'copyright_protection': 'Automatic DMCA compliance for creator content',
        'content_attribution': 'Blockchain-based attribution and rights management',
        'fair_use_monitoring': 'AI-powered fair use detection and enforcement',
        'takedown_procedures': 'Automated DMCA takedown and counter-notice handling',
        'content_licensing': 'Rights management for content licensing and distribution'
    },
    'privacy_compliance': {
        'creator_data_protection': 'GDPR/CCPA compliant creator data handling',
        'audience_privacy': 'Privacy protection for creator audiences',
        'consent_management': 'Granular consent management for data processing',
        'data_minimization': 'Principle of data minimization implementation',
        'cross_border_transfers': 'Safe transfer mechanisms for global operations'
    },
    'platform_compliance': {
        'automated_compliance': 'Real-time compliance monitoring and enforcement',
        'audit_readiness': 'Continuous audit trail and documentation',
        'breach_response': 'Automated breach detection and notification systems',
        'regulatory_reporting': 'Automated reporting to regulatory authorities',
        'compliance_dashboard': 'Real-time compliance status and metrics'
    }
}