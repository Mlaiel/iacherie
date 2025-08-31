"""IA Influencer Agent - Secrets Deployment Module
Enterprise secrets management and deployment

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved - Unauthorized use prohibited

⚠️  AVERTISSEMENT LEGAL STRICT ⚠️

Ce code et concept sont la propriété intellectuelle exclusive de :
👤 Fahed Mlaiel (mlaiel@live.de)
🏢 IA-Influencer Agent Platform

🚫 INTERDICTIONS ABSOLUES :
- Copie, reproduction ou utilisation sans autorisation écrite personnelle
- Distribution, modification ou dérivation du code
- Utilisation commerciale ou personnelle non autorisée
- Reverse engineering ou extraction de concepts

⚖️  CONSÉQUENCES LÉGALES :
Toute violation entraînera des poursuites judiciaires immédiates selon :
- Droit d'auteur international
- Propriété intellectuelle
- Code pénal pour vol de propriété

📧 Contact autorisé : mlaiel@live.de
📅 Copyright 2025 - Tous droits réservés
"""
__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"

from .config import SecretsConfig, get_config, set_config
from .vault_manager import VaultManager, VaultHealthChecker, InfluencerVaultManager
from .secret_rotator import SecretRotator, RotationStrategy, RotationStatus, EmergencyRotator, InfluencerSecretRotator, InfluencerEmergencyRotator
from .encryption_manager import EncryptionManager, EncryptionAlgorithm, KeyDerivationFunction, ContentProtectionEncryption
from .secret_injector import SecretInjector, InjectionMethod, SecretMapping, InjectionConfig, InfluencerSecretInjector
from .compliance_auditor import ComplianceAuditor, ComplianceFramework, AuditEventType, ComplianceStatus, InfluencerComplianceAuditor
from .certificate_manager import CertificateManager, CertificateType, CertificateStatus, KeyType, InfluencerCertificateManager
from .utils import SecurityUtils, ValidationUtils, NotificationUtils, KubernetesUtils, InfluencerPlatformUtils

# Import the main index module components
from .index import (
    InfluencerSecretsManager,
    create_secrets_manager,
    create_influencer_secrets_manager,
    initialize_platform_secrets,
    get_module_info,
    validate_environment,
    setup_logging
)

__all__ = [
    # Configuration
    "SecretsConfig",
    "get_config",
    "set_config",
    
    # Core managers
    "VaultManager",
    "VaultHealthChecker",
    "SecretRotator",
    "EncryptionManager",
    "SecretInjector",
    "ComplianceAuditor",
    "CertificateManager",
    
    # IA Influencer specialized managers
    "InfluencerVaultManager",
    "InfluencerSecretRotator",
    "InfluencerEmergencyRotator",
    "ContentProtectionEncryption",
    "InfluencerSecretInjector",
    "InfluencerComplianceAuditor",
    "InfluencerCertificateManager",
    "InfluencerPlatformUtils",
    
    # Unified manager and factory functions
    "InfluencerSecretsManager",
    "create_secrets_manager",
    "create_influencer_secrets_manager",
    "initialize_platform_secrets",
    
    # Helper functions
    "get_module_info",
    "validate_environment",
    "setup_logging",
    
    # Enums and constants
    "RotationStrategy",
    "RotationStatus",
    "EncryptionAlgorithm",
    "KeyDerivationFunction",
    "InjectionMethod",
    "ComplianceFramework",
    "AuditEventType",
    "ComplianceStatus",
    "CertificateType",
    "CertificateStatus",
    "KeyType",
    
    # Data classes
    "SecretMapping",
    "InjectionConfig",
    
    # Utilities
    "SecurityUtils",
    "ValidationUtils",
    "NotificationUtils",
    "KubernetesUtils",
    
    # Emergency tools
    "EmergencyRotator"
]

# Module metadata
__module_info__ = {
    "name": "IA Influencer Agent - Secrets Management",
    "description": "Enterprise-grade secrets management with encryption, rotation, compliance, and PKI",
    "team_specialties": [
        "🔐 Lead Dev IA + Backend Senior",
        "🛡️  ML Engineer + Security Expert", 
        "🗄️  DBA + Data Engineer",
        "🏗️  DevOps + Infrastructure",
        "📊 Audio Processing + Analytics",
        "🔗 Microservices + API Architecture",
        "📋 Compliance + Audit Specialist",
        "🎯 IA Prompt Engineering"
    ],
    "author": "Fahed Mlaiel",
    "email": "mlaiel@live.de",
    "copyright": "2025 - All rights reserved",
    "license": "Proprietary - Unauthorized use prohibited"
}
