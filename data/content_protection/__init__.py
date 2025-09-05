"""🛡️ Content Protection Module Enterprise - IA-Influencer-Agent Platform
=======================================================================

Système de protection contenu professionnel pour créateurs multi-format avec 
détection IA avancée, gestion droits automatisée et analytics complets.

LOGIQUE MÉTIER IA-INFLUENCER-AGENT:
Upload Multi-Format → Protection IA Droits → Fingerprinting Avancé → 
Surveillance Web → Détection Violations → Takedown Automatisé → Monétisation

CRÉATEURS PROTÉGÉS:
- 🎵 Musiciens (Spotify, SoundCloud, Apple Music)
- 📱 Influenceurs (Instagram, TikTok, YouTube)  
- 📸 Photographes (Instagram, portfolios web)
- ✍️ Blogueurs (Medium, blogs personnels)
- 🎭 Comédiens (YouTube, TikTok, Twitch)

PROTECTION MULTI-FORMAT:
- 🎵 Audio: Fingerprinting Chromaprint + Essentia
- 🎥 Vidéo: OpenCV + YOLO + pHash
- 📸 Image: CLIP + ImageHash + Perceptual Hash
- 📝 Texte: BERT + RoBERTa + NLP

Architecture Enterprise 3-Niveaux | Production-Ready

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
⚠️ PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - Usage non autorisé strictement interdit
"""# Import consolidated enterprise protection engines
from .protection_management_engine import (
    ProtectionManagementEngine,
    ProtectionLevel,
    ViolationType,
    ProtectionStatus,
    RightsType,
    LicenseStatus,
    RightsTransferType,
    AnalyticsMetric,
    TimeGranularity,
    ProtectionConfig,
    ViolationAlert,
    RightsOwnership,
    LicenseAgreement,
    ProtectionReport,
    ProtectionMetrics
)

from .fingerprinting_detection_engine import (
    FingerprintingDetectionEngine,
    ContentType,
    FingerprintMethod,
    ViolationSeverity,
    DetectionMethod,
    FingerprintConfig,
    FingerprintResult,
    SimilarityMatch,
    ViolationEvidence,
    DetectionConfig,
    DetectionReport
)

from .platform_monitoring_crawler import (
    PlatformMonitoringCrawler,
    PlatformType,
    CrawlMethod,
    ContentStatus,
    MonitoringMode,
    ThreatLevel,
    CrawlTarget,
    CrawledContent,
    CrawlResult,
    MonitoringConfig,
    PlatformCapabilities
)

from .legal_dmca_automation import (
    LegalDMCAAutomation,
    TakedownType,
    TakedownStatus,
    JurisdictionType,
    TemplateType,
    PlatformTakedownMethod,
    LegalStrength,
    DMCANotice,
    TakedownRequest,
    LegalDocument,
    TakedownResponse,
    TakedownResult,
    TemplateConfig
)

from .revenue_recovery_monetization import (
    RevenueRecoveryMonetization,
    RevenueType,
    PlatformRevenue,
    CompensationMethod,
    CurrencyType,
    RecoveryStatus,
    DamageType,
    RevenueRecord,
    ViolationImpact,
    CompensationClaim,
    RevenueAnalytics,
    LicensingOpportunity,
    RecoveryStrategy
)

from .blockchain_security_infrastructure import (
    BlockchainSecurityInfrastructure,
    BlockchainNetwork,
    SmartContractType,
    OwnershipProofType,
    DecentralizedStorageType,
    TransactionStatus,
    SecurityLevel,
    BlockchainConfig,
    OwnershipRecord,
    SmartContract,
    CryptographicProof,
    DecentralizedStorage,
    NFTProtection,
    LicenseSmartContract,
    BlockchainAnalytics
)

# Import unified service
from .index import (
    ContentProtectionService,
    ServiceConfig,
    ProtectionSummary,
    initialize_protection_service,
    quick_protection_setup
)

# Module metadata
__version__ = "2.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__description__ = "Industrial-grade content protection system for IA Influencer Agent"

# Export all consolidated enterprise components
__all__ = [
    # Consolidated Enterprise Engines
    "ProtectionManagementEngine",
    "FingerprintingDetectionEngine", 
    "PlatformMonitoringCrawler",
    "LegalDMCAAutomation",
    "RevenueRecoveryMonetization",
    "BlockchainSecurityInfrastructure",
    
    # Unified service
    "ContentProtectionService",
    "ServiceConfig",
    "ProtectionSummary",
    "initialize_protection_service",
    "quick_protection_setup",
    
    # Configuration classes
    "ProtectionConfig",
    "DetectionConfig",
    "FingerprintConfig",
    "TemplateConfig",
    "MonitoringConfig",
    "BlockchainConfig",
    
    # Content and method enums
    "ContentType",
    "PlatformType",
    "FingerprintMethod",
    "CrawlMethod",
    "DetectionMethod",
    "BlockchainNetwork",
    "SmartContractType",
    
    # Status and type enums
    "ProtectionLevel",
    "ViolationType", 
    "ProtectionStatus",
    "RightsType",
    "LicenseStatus",
    "RightsTransferType",
    "ViolationSeverity",
    "TakedownType",
    "TakedownStatus",
    "PlatformTakedownMethod",
    "AnalyticsMetric",
    "TimeGranularity",
    "ContentStatus",
    "RevenueType",
    "PlatformRevenue",
    "CompensationMethod",
    "TemplateType",
    "JurisdictionType",
    "MonitoringMode",
    "ThreatLevel",
    "CurrencyType",
    "RecoveryStatus",
    "DamageType",
    "OwnershipProofType",
    "DecentralizedStorageType",
    "TransactionStatus",
    "SecurityLevel",
    "LegalStrength",
    
    # Data classes - Core Protection
    "ViolationAlert",
    "ProtectionReport",
    "RightsOwnership",
    "LicenseAgreement", 
    "ViolationEvidence",
    "DetectionReport",
    "TakedownRequest",
    "DMCANotice",
    "TakedownResponse",
    "TakedownResult",
    "ProtectionMetrics",
    
    # Data classes - Advanced Features
    "FingerprintResult",
    "SimilarityMatch",
    "CrawlTarget",
    "CrawledContent", 
    "CrawlResult",
    "RevenueRecord",
    "ViolationImpact",
    "CompensationClaim",
    "RevenueAnalytics",
    "LegalDocument",
    "PlatformCapabilities",
    "LicensingOpportunity",
    "RecoveryStrategy",
    
    # Data classes - Blockchain
    "OwnershipRecord",
    "SmartContract",
    "CryptographicProof",
    "DecentralizedStorage",
    "NFTProtection",
    "LicenseSmartContract",
    "BlockchainAnalytics"
]
