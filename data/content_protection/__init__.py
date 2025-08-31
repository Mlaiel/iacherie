""" Content Protection Module Enterprise - IA-Influencer-Agent Platform
=======================================================================

Système de protection contenu professionnel pour créateurs multi-format avec 
détection IA avancée, gestion droits automatisée et analytics complets.

LOGIQUE MÉTIER IA-INFLUENCER-AGENT:
Upload Multi-Format → Protection IA Droits → Fingerprinting Avancé → 
Surveillance Web → Détection Violations → Takedown Automatisé → Monétisation

CRÉATEURS PROTÉGÉS:
-  Musiciens (Spotify, SoundCloud, Apple Music)
-  Influenceurs (Instagram, TikTok, YouTube)  
-  Photographes (Instagram, portfolios web)
-  Blogueurs (Medium, blogs personnels)
-  Comédiens (YouTube, TikTok, Twitch)

PROTECTION MULTI-FORMAT:
-  Audio: Fingerprinting Chromaprint + Essentia
-  Vidéo: OpenCV + YOLO + pHash
-  Image: CLIP + ImageHash + Perceptual Hash
-  Texte: BERT + RoBERTa + NLP

Architecture Enterprise 3-Niveaux | Production-Ready

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel - All Rights Reserved
 PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - Usage non autorisé strictement interdit
"""
# Import core managers
from .content_protection_manager import (
    ContentProtectionManager,
    ProtectionConfig,
    ProtectionLevel,
    ViolationType,
    ProtectionStatus,
    ViolationAlert,
    ProtectionReport
)

from .rights_manager import (
    RightsManager,
    RightsType,
    LicenseStatus,
    RightsTransferType,
    RightsOwnership,
    LicenseAgreement,
    RightsVerification
)

from .violation_detector import (
    ViolationDetector,
    DetectionMethod,
    ViolationSeverity,
    DetectionConfig,
    ViolationEvidence,
    DetectionReport
)

from .takedown_manager import (
    TakedownManager,
    TakedownType,
    TakedownStatus,
    PlatformTakedownMethod,
    TakedownRequest,
    DMCANotice,
    TakedownResponse,
    TakedownResult
)

from .protection_analytics import (
    ProtectionAnalytics,
    AnalyticsMetric,
    TimeGranularity,
    ReportType,
    ProtectionMetrics,
    ViolationTrend,
    PlatformAnalytics,
    ThreatIntelligence,
    AnalyticsReport
)

# Import legal templates
from .legal_templates import (
    LegalTemplateManager,
    TemplateType,
    JurisdictionType,
    DMCATemplate,
    CopyrightNotice,
    LegalDocument,
    TemplateConfig
)

# Import new advanced modules
from .fingerprinting_engine import (
    FingerprintingEngine,
    ContentType,
    FingerprintMethod,
    FingerprintResult,
    SimilarityMatch,
    FingerprintConfig
)

from .platform_crawler import (
    PlatformCrawler,
    PlatformType,
    CrawlMethod,
    ContentStatus,
    CrawlTarget,
    CrawledContent,
    CrawlResult
)

from .revenue_tracker import (
    RevenueTracker,
    RevenueType,
    PlatformRevenue,
    CompensationMethod,
    RevenueRecord,
    ViolationImpact,
    CompensationClaim,
    RevenueAnalytics
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

# Export all public components
__all__ = [
    # Core managers
    "ContentProtectionManager",
    "RightsManager",
    "ViolationDetector", 
    "TakedownManager",
    "ProtectionAnalytics",
    
    # Advanced engines
    "FingerprintingEngine",
    "PlatformCrawler",
    "RevenueTracker",
    "LegalTemplateManager",
    
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
    
    # Content and method enums
    "ContentType",
    "PlatformType",
    "FingerprintMethod",
    "CrawlMethod",
    "DetectionMethod",
    
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
    "ReportType",
    "ContentStatus",
    "RevenueType",
    "PlatformRevenue",
    "CompensationMethod",
    "TemplateType",
    "JurisdictionType",
    
    # Data classes - Core
    "ViolationAlert",
    "ProtectionReport",
    "RightsOwnership",
    "LicenseAgreement", 
    "RightsVerification",
    "ViolationEvidence",
    "DetectionReport",
    "TakedownRequest",
    "DMCANotice",
    "TakedownResponse",
    "TakedownResult",
    "ProtectionMetrics",
    "ViolationTrend",
    "PlatformAnalytics",
    "ThreatIntelligence",
    "AnalyticsReport",
    
    # Data classes - Advanced
    "FingerprintResult",
    "SimilarityMatch",
    "CrawlTarget",
    "CrawledContent", 
    "CrawlResult",
    "RevenueRecord",
    "ViolationImpact",
    "CompensationClaim",
    "RevenueAnalytics",
    "DMCATemplate",
    "CopyrightNotice",
    "LegalDocument"
]
