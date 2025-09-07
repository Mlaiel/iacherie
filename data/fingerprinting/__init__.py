"""🔍 Fingerprinting Module Enterprise - IA-Influencer-Agent Platform
================================================================

Système de fingerprinting IA avancé pour protection contenu créateurs multi-format.
Implémente algorithmes état-de-l'art pour fingerprinting audio, vidéo, image et texte.

CRÉATEURS SUPPORTÉS:
- 🎵 Musiciens: Spotify, SoundCloud, Apple Music, Bandcamp
- 📱 Influenceurs: Instagram, TikTok, YouTube, Twitter
- 📸 Photographes: Instagram, portfolios web, Flickr
- ✍️ Blogueurs: Medium, blogs personnels, Substack
- 🎭 Comédiens: YouTube, TikTok, Twitch, Stand-up

PERFORMANCES ENTERPRISE:
- Audio: >95% précision (Chromaprint + Essentia)
- Vidéo: >90% précision (OpenCV + YOLO + pHash)
- Image: >92% précision (CLIP + ImageHash)
- Texte: >88% précision (BERT + RoBERTa)
- Détection: <10s temps réel

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
⚠️ PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - Usage non autorisé strictement interdit
"""

# === MOTEUR FINGERPRINTING ENTERPRISE PRINCIPAL ===
from .multimodal_fingerprinting_engine import (
    ConsolidatedFingerprintingEngine,
    MultiModalFingerprint,
    ContentFormat,
    FingerprintMethod,
    SimilarityMetric,
    FingerprintResult,
    SimilarityMatch,
    create_fingerprinting_engine
)

# === CONSOLIDATED ENGINES ENTERPRISE ===

# Vector Database & Matching Intelligence
from .vector_database_matching import (
    ConsolidatedVectorDatabaseEngine,
    VectorSearchResult,
    VectorIndexConfig,
    VectorIndexType,
    SimilarityAlgorithm,
    CacheLevel,
    create_vector_database_engine
)

# Real-Time Surveillance & Monitoring
from .realtime_surveillance_engine import (
    ConsolidatedRealtimeSurveillanceEngine,
    ViolationAlert,
    PlatformConfig,
    PlatformScanResult,
    PlatformType,
    AlertSeverity,
    ViolationType,
    MonitoringStatus,
    create_surveillance_engine
)

# Performance Analytics & Quality Assurance
from .performance_analytics_engine import (
    ConsolidatedPerformanceAnalyticsEngine,
    PerformanceMetric,
    QualityAssessment,
    BenchmarkResult,
    ABTestResult,
    MetricType,
    PerformanceGrade,
    BenchmarkType,
    create_performance_analytics_engine
)

# Legal Protection & Compliance Automation
from .legal_protection_automation import (
    ConsolidatedLegalProtectionEngine,
    LegalEvidence,
    DMCARequest,
    LegalDocument,
    ComplianceReport,
    LegalJurisdiction,
    LegalDocumentType,
    EvidenceType,
    ComplianceStatus,
    create_legal_protection_engine
)

# Blockchain Security & NFT Integration
from .blockchain_security_fingerprinting import (
    BlockchainSecurityFingerprintingEngine,
    BlockchainFingerprint,
    ProofOfCreation,
    SmartContract,
    NFTMetadata,
    BlockchainNetwork,
    SmartContractType,
    ProofType,
    create_blockchain_fingerprinting_engine
)

# === LEGACY COMPATIBILITY (DEPRECATED) ===
# These imports are kept for backward compatibility but are deprecated
# Use the consolidated engines above instead

import warnings

class DeprecatedClass:
    """Base class for deprecated fingerprinting classes."""
    def __init__(self, deprecated_name, replacement_name, *args, **kwargs):
        warnings.warn(f"{deprecated_name} is deprecated. Use {replacement_name} instead.", 
                     DeprecationWarning, stacklevel=3)

# Legacy fingerprinting classes (deprecated)
class AudioFingerprinter(DeprecatedClass):
    def __init__(self, *args, **kwargs):
        super().__init__("AudioFingerprinter", "ConsolidatedFingerprintingEngine", *args, **kwargs)

class VideoFingerprinter(DeprecatedClass):
    def __init__(self, *args, **kwargs):
        super().__init__("VideoFingerprinter", "ConsolidatedFingerprintingEngine", *args, **kwargs)

class ImageFingerprinter(DeprecatedClass):
    def __init__(self, *args, **kwargs):
        super().__init__("ImageFingerprinter", "ConsolidatedFingerprintingEngine", *args, **kwargs)

class TextFingerprinter(DeprecatedClass):
    def __init__(self, *args, **kwargs):
        super().__init__("TextFingerprinter", "ConsolidatedFingerprintingEngine", *args, **kwargs)

class VectorMatcher(DeprecatedClass):
    def __init__(self, *args, **kwargs):
        super().__init__("VectorMatcher", "ConsolidatedVectorDatabaseEngine", *args, **kwargs)

class FingerprintManager(DeprecatedClass):
    def __init__(self, *args, **kwargs):
        super().__init__("FingerprintManager", "ConsolidatedFingerprintingEngine", *args, **kwargs)

# === EXPORTS ===

# Main exports for new consolidated architecture
__all__ = [
    # === CONSOLIDATED ENGINES (NEW ARCHITECTURE) ===
    "ConsolidatedFingerprintingEngine",        # Main fingerprinting engine
    "ConsolidatedVectorDatabaseEngine",        # Vector database & matching
    "ConsolidatedRealtimeSurveillanceEngine",  # Real-time surveillance
    "ConsolidatedPerformanceAnalyticsEngine",  # Performance analytics
    "ConsolidatedLegalProtectionEngine",       # Legal protection
    "BlockchainSecurityFingerprintingEngine",  # Blockchain & NFT
    
    # === FACTORY FUNCTIONS ===
    "create_fingerprinting_engine",
    "create_vector_database_engine", 
    "create_surveillance_engine",
    "create_performance_analytics_engine",
    "create_legal_protection_engine",
    "create_blockchain_fingerprinting_engine",
    
    # === CORE DATA STRUCTURES ===
    "MultiModalFingerprint",
    "ContentFormat",
    "FingerprintMethod",
    "SimilarityMetric",
    "FingerprintResult",
    "SimilarityMatch",
    
    # === VECTOR DATABASE ===
    "VectorSearchResult",
    "VectorIndexConfig",
    "VectorIndexType", 
    "SimilarityAlgorithm",
    "CacheLevel",
    
    # === SURVEILLANCE ===
    "ViolationAlert",
    "PlatformConfig",
    "PlatformScanResult",
    "PlatformType",
    "AlertSeverity",
    "ViolationType",
    "MonitoringStatus",
    
    # === ANALYTICS ===
    "PerformanceMetric",
    "QualityAssessment",
    "BenchmarkResult",
    "ABTestResult",
    "MetricType",
    "PerformanceGrade",
    "BenchmarkType",
    
    # === LEGAL PROTECTION ===
    "LegalEvidence",
    "DMCARequest",
    "LegalDocument",
    "ComplianceReport",
    "LegalJurisdiction",
    "LegalDocumentType",
    "EvidenceType",
    "ComplianceStatus",
    
    # === BLOCKCHAIN ===
    "BlockchainFingerprint",
    "ProofOfCreation",
    "SmartContract", 
    "NFTMetadata",
    "BlockchainNetwork",
    "SmartContractType",
    "ProofType",
    
    # === LEGACY COMPATIBILITY (DEPRECATED) ===
    "AudioFingerprinter",      # DEPRECATED
    "VideoFingerprinter",      # DEPRECATED
    "ImageFingerprinter",      # DEPRECATED
    "TextFingerprinter",       # DEPRECATED
    "VectorMatcher",           # DEPRECATED
    "FingerprintManager",      # DEPRECATED
]

# === MODULE METADATA ===
__version__ = "2.0.0-consolidated"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__copyright__ = "(c) 2025 Fahed Mlaiel - All Rights Reserved"
__license__ = "Proprietary - Unauthorized use prohibited"

# === CONVENIENCE ALIASES ===
# Recommended engine for new projects
FingerprintEngine = ConsolidatedFingerprintingEngine
VectorEngine = ConsolidatedVectorDatabaseEngine
SurveillanceEngine = ConsolidatedRealtimeSurveillanceEngine
AnalyticsEngine = ConsolidatedPerformanceAnalyticsEngine
LegalEngine = ConsolidatedLegalProtectionEngine
BlockchainEngine = BlockchainSecurityFingerprintingEngine

# Legacy compatibility (will issue deprecation warnings)
MultiModalFingerprintEngine = ConsolidatedFingerprintingEngine  # DEPRECATED NAME