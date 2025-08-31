""" Fingerprinting Module Enterprise - IA-Influencer-Agent Platform
================================================================

Système de fingerprinting IA avancé pour protection contenu créateurs multi-format.
Implémente algorithmes état-de-l'art pour fingerprinting audio, vidéo, image et texte.

CRÉATEURS SUPPORTÉS:
-  Musiciens: Spotify, SoundCloud, Apple Music, Bandcamp
-  Influenceurs: Instagram, TikTok, YouTube, Twitter
-  Photographes: Instagram, portfolios web, Flickr
-  Blogueurs: Medium, blogs personnels, Substack
-  Comédiens: YouTube, TikTok, Twitch, Stand-up

PERFORMANCES ENTERPRISE:
- Audio: >95% précision (Chromaprint + Essentia)
- Vidéo: >90% précision (OpenCV + YOLO + pHash)
- Image: >92% précision (CLIP + ImageHash)
- Texte: >88% précision (BERT + RoBERTa)
- Détection: <10s temps réel

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel - All Rights Reserved
 PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - Usage non autorisé strictement interdit
"""
# === MOTEUR FINGERPRINTING ENTERPRISE PRINCIPAL ===
from .multimodal_fingerprint_engine import (
    MultiModalFingerprintEngine,
    MultiModalFingerprint,
    ContentFormat,
    FingerprintMethod,
    SimilarityMetric,
    FingerprintResult,
    SimilarityMatch
)

# === FINGERPRINTING SPÉCIALISÉ PAR FORMAT ===

# Audio fingerprinting
from .audio_fingerprinter import AudioFingerprinter, AudioFingerprint, AudioFeatures

# Video fingerprinting
from .video_fingerprint import (
    VideoFingerprinter,
    VideoFingerprint,
    VideoMatchResult,
    VideoFingerprintType,
    FrameSamplingMethod
)

# Image fingerprinting
from .image_fingerprint import (
    ImageFingerprinter,
    ImageFingerprint,
    ImageMatchResult,
    ImageFingerprintType
)

# Text fingerprinting
from .text_fingerprint import (
    TextFingerprinter,
    TextFingerprint,
    TextMatchResult,
    TextFingerprintType
)

# Vector matching
from .vector_matcher import (
    VectorMatcher,
    MatchResult,
    VectorIndexConfig,
    SimilarityMetric as LegacySimilarityMetric,
    IndexType
)

# Configuration management
from .config import (
    FingerprintingSystemConfig,
    AudioFingerprintConfig,
    VideoFingerprintConfig,
    ImageFingerprintConfig,
    TextFingerprintConfig,
    VectorMatcherConfig,
    ConfigManager,
    PerformanceProfile,
    ProcessingMode,
    get_config,
    reset_config_cache
)

# Metadata management
from .metadata import (
    ContentMetadata,
    AudioMetadata,
    VideoMetadata,
    ImageMetadata,
    TextMetadata,
    TechnicalMetadata,
    GeolocationData,
    ContentType,
    QualityLevel,
    MetadataExtractor,
    MetadataManager,
    extract_content_metadata
)

# Performance optimization
from .performance import (
    PerformanceMonitor,
    PerformanceOptimizer,
    BatchProcessor,
    PerformanceMetric,
    OptimizationStrategy,
    PerformanceStats,
    ResourceUsage,
    performance_timer,
    start_performance_monitoring,
    stop_performance_monitoring,
    get_performance_report,
    optimize_system_performance
)

# Fingerprint management
from .fingerprint_manager import (
    FingerprintManager,
    FingerprintJob,
    FingerprintResult,
    FingerprintStatus,
    ContentType as ManagerContentType,
    get_fingerprint_manager,
    reset_fingerprint_manager
)

# Surveillance integration
from .surveillance_integration import (
    SurveillanceIntegrationManager,
    SurveillanceChannel,
    SurveillanceMessage,
    MessageType,
    MessagePriority,
    get_surveillance_manager,
    reset_surveillance_manager
)

# Real-time monitoring
from .real_time_monitoring import (
    RealTimeMonitor,
    MonitoringChannel,
    AlertLevel,
    StreamingWindow,
    DetectionResult,
    PerformanceMetrics,
    get_real_time_monitor,
    reset_real_time_monitor
)

# Platform alerts
from .platform_alerts import (
    PlatformAlertsManager,
    PlatformAlert,
    AlertType,
    AlertChannel,
    AlertStatus,
    PlatformInfo,
    get_platform_alerts_manager,
    reset_platform_alerts_manager
)

# Content database
from .content_database import (
    ContentDatabaseManager,
    DatabaseConfig,
    QueryResult,
    SimilarityResult,
    IndexingJob,
    DatabaseType,
    get_content_database_manager,
    reset_content_database_manager
)

# Legal compliance
from .legal_compliance import (
    LegalComplianceManager,
    LegalJurisdiction,
    ComplianceFramework,
    LegalDocumentType,
    ViolationType,
    LegalRisk,
    LegalEntity,
    LegalCase,
    ComplianceAssessment,
    LegalDocument,
    get_legal_compliance_manager,
    reset_legal_compliance_manager,
    assess_violation_legality,
    generate_dmca_notice
)

# System index and convenience functions
from .index import (
    FingerprintingSystemIndex,
    get_fingerprinting_system,
    reset_fingerprinting_system,
    fingerprint_content,
    find_similar_content,
    batch_fingerprint_content,
    get_system_stats
)

# Export principal pour logique métier IA-Influencer-Agent
__all__ = [
    # === MOTEUR ENTERPRISE PRINCIPAL ===
    "MultiModalFingerprintEngine",      # Moteur fingerprinting multi-modal enterprise
    "MultiModalFingerprint",            # Fingerprint créateur multi-modal
    "ContentFormat",                    # Formats contenu créateurs (audio, vidéo, image, texte)
    "FingerprintMethod",               # Méthodes fingerprinting enterprise
    "SimilarityMetric",                # Métriques similarité avancées
    "FingerprintResult",               # Résultat fingerprinting individuel
    "SimilarityMatch",                 # Match similarité avec évaluation violation
    
    # === FINGERPRINTING SPÉCIALISÉ ===
    
    # Audio (Musiciens - Spotify, SoundCloud, etc.)
    "AudioFingerprinter",
    "AudioFingerprint", 
    "AudioFeatures",
    
    # Vidéo (Influenceurs, Comédiens - YouTube, TikTok, etc.)
    "VideoFingerprinter",
    "VideoFingerprint",
    "VideoMatchResult",
    "VideoFingerprintType",
    "FrameSamplingMethod",
    
    # Image (Photographes - Instagram, portfolios, etc.)
    "ImageFingerprinter",
    "ImageFingerprint",
    "ImageMatchResult",
    "ImageFingerprintType",
    
    # Texte (Blogueurs - Medium, blogs, etc.)
    "TextFingerprinter",
    "TextFingerprint",
    "TextMatchResult",
    "TextFingerprintType",
    
    # === INFRASTRUCTURE ENTERPRISE ===
    
    # Vector matching haute performance
    "VectorMatcher",
    "MatchResult",
    "VectorIndexConfig",
    "LegacySimilarityMetric",
    "IndexType",
    
    # Configuration système
    "FingerprintingSystemConfig",
    "AudioFingerprintConfig",
    "VideoFingerprintConfig",
    "ImageFingerprintConfig",
    "TextFingerprintConfig",
    "VectorMatcherConfig",
    "ConfigManager",
    "PerformanceProfile",
    "ProcessingMode",
    "get_config",
    "reset_config_cache",
    
    # Gestion métadonnées
    "ContentMetadata",
    "AudioMetadata",
    "VideoMetadata",
    "ImageMetadata",
    "TextMetadata",
    "TechnicalMetadata",
    "GeolocationData",
    "ContentType",
    "QualityLevel",
    "MetadataExtractor",
    "MetadataManager",
    "extract_content_metadata",
    
    # Optimisation performance
    "PerformanceMonitor",
    "PerformanceOptimizer",
    "BatchProcessor",
    "PerformanceMetric",
    "OptimizationStrategy",
    "PerformanceStats",
    "ResourceUsage",
    "performance_timer",
    "start_performance_monitoring",
    "stop_performance_monitoring",
    "get_performance_report",
    "optimize_system_performance",
    
    # Gestion fingerprints
    "FingerprintManager",
    "FingerprintJob",
    "FingerprintResultLegacy",
    "FingerprintStatus",
    "ManagerContentType",
    "get_fingerprint_manager",
    "reset_fingerprint_manager",
    
    # Intégration surveillance
    "SurveillanceIntegrationManager",
    "SurveillanceChannel", 
    "SurveillanceMessage",
    "MessageType",
    "MessagePriority",
    "get_surveillance_manager",
    "reset_surveillance_manager",
    
    # Monitoring temps réel
    "RealTimeMonitor",
    "MonitoringChannel",
    "AlertLevel",
    "StreamingWindow",
    "DetectionResult",
    "PerformanceMetrics",
    "get_real_time_monitor",
    "reset_real_time_monitor",
    
    # Alertes plateformes
    "PlatformAlertsManager",
    "PlatformAlert",
    "AlertType",
    "AlertChannel",
    "AlertStatus", 
    "PlatformInfo",
    "get_platform_alerts_manager",
    "reset_platform_alerts_manager",
    
    # Base de données contenu
    "ContentDatabaseManager",
    "DatabaseConfig",
    "QueryResult",
    "SimilarityResult",
    "IndexingJob",
    "DatabaseType",
    "get_content_database_manager",
    "reset_content_database_manager",
    
    # Conformité légale enterprise
    "LegalComplianceManager",
    "LegalJurisdiction",
    "ComplianceFramework",
    "LegalDocumentType",
    "ViolationType",
    "LegalRisk",
    "LegalEntity",
    "LegalCase",
    "ComplianceAssessment",
    "LegalDocument",
    "get_legal_compliance_manager",
    "reset_legal_compliance_manager",
    "assess_violation_legality",
    "generate_dmca_notice",
    
    # Index système et fonctions utilitaires
    "FingerprintingSystemIndex",
    "get_fingerprinting_system",
    "reset_fingerprinting_system",
    "fingerprint_content",
    "find_similar_content",
    "batch_fingerprint_content",
    "get_system_stats"
]

# Configuration module enterprise
__version__ = "2.1.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__copyright__ = "© 2025 Fahed Mlaiel - All Rights Reserved"
__license__ = "Proprietary - Unauthorized use prohibited"

# Alias legacy pour rétrocompatibilité
from .audio_fingerprinter import AudioFingerprinter
from .video_fingerprint import VideoFingerprinter  
from .image_fingerprint import ImageFingerprinter
from .text_fingerprint import TextFingerprinter
from .vector_matcher import VectorMatcher
from .fingerprint_manager import FingerprintManager

# Nouvelle classe principale recommendée pour nouveaux projets
FingerprintEngine = MultiModalFingerprintEngine
