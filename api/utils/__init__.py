"""Utility modules for IA Influencer Agent Platform
Comprehensive utility functions and classes for the entire platform

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent Platform with Multi-Content Protection
WARNING: This code is protected by copyright. Any unauthorized use, reproduction,
or distribution without written permission from Fahed Mlaiel is strictly prohibited.
"""# Audio Processing Utilities
from .audio_processing import (
    AudioAnalyzer,
    AudioFingerprinter,
    SpectralAnalyzer,
    ChromaprintProcessor,
    AudioProcessor,
    AudioProcessingError
)

# Business Logic Utilities  
from .business_logic import (
    ContentProcessor,
    RevenueCalculator,
    InfluencerMetrics,
    CollaborationMatcher,
    BusinessProcessor,
    BusinessLogicError
)

# Cache Management Utilities
from .cache_manager import (
    CacheManager,
    RedisHandler,
    MemoryOptimizer,
    PerformanceMonitor,
    CacheError
)

# Content Protection Utilities
from .content_protection import (
    FingerprintGenerator,
    PiracyDetector,
    ProtectionEngine,
    ContentProtectionError
)

# Data Processing Utilities
from .data_processing import (
    DataTransformer,
    DataValidator,
    BatchProcessor,
    StreamProcessor,
    DataProcessor,
    DataProcessingError
)

# Database Utilities
from .database_utils import (
    DatabaseConnectionManager,
    AsyncDatabaseManager,
    RedisManager,
    MongoDBManager,
    QueryBuilder,
    DatabaseMigrationManager,
    DatabaseUtils,
    DatabaseConfig,
    QueryResult,
    TransactionContext,
    DatabaseError
)

# Encryption Utilities
from .encryption_utils import (
    EncryptionManager,
    HashGenerator,
    TokenValidator,
    SecureStorage,
    EncryptionError
)

# Image Processing Utilities
from .image_processing import (
    ImageAnalyzer,
    ImageFingerprinter,
    PerceptualHasher,
    VisualContentProcessor,
    ImageProcessor,
    ImageProcessingError
)

# JSON Utilities
from .json_utils import (
    JSONProcessor,
    SchemaValidator,
    DataSerializer,
    ConfigParser,
    MetadataExtractor,
    JSONError
)

# Multimedia Converter
from .multimedia_converter import (
    AudioConverter,
    VideoConverter,
    ImageConverter,
    StreamingOptimizer,
    MultimediaConverter,
    ConversionError
)

# Notification Helper
from .notification_helper import (
    EmailChannel,
    SlackChannel,
    TelegramChannel,
    NotificationEngine,
    NotificationError
)

# Platform Integration
from .platform_integration import (
    SpotifyAPI,
    YouTubeAPI,
    InstagramAPI,
    TikTokAPI,
    TwitterAPI,
    PlatformIntegrationManager,
    PlatformError
)

# Security Utilities
from .security_utils import (
    PasswordManager,
    TwoFactorAuth,
    IPSecurityManager,
    RateLimiter,
    ThreatDetector,
    AuditLogger,
    SecurityManager,
    SecurityError
)

# Text Processing Utilities
from .text_processing import (
    TextPreprocessor,
    TextAnalyzer,
    ContentOptimizer,
    TextModerator,
    WordCloudGenerator,
    TextProcessor,
    ValidationSeverity,
    TextStats,
    SentimentAnalysis,
    KeywordAnalysis,
    LanguageAnalysis,
    ContentOptimization,
    TextProcessingError
)

# Validation Utilities
from .validation_utils import (
    BaseValidator,
    StringValidator,
    EmailValidator,
    PhoneValidator,
    URLValidator,
    IPAddressValidator,
    PasswordValidator,
    NumericValidator,
    DateTimeValidator,
    FileValidator,
    JSONValidator,
    CompositeValidator,
    DataValidator,
    BusinessRuleValidator,
    ValidationUtils,
    ValidationResult,
    ValidationReport,
    ValidationError
)

# Video Processing Utilities
from .video_processing import (
    VideoMetadataExtractor,
    VideoFrameExtractor,
    VideoFingerprinter,
    VideoAnalyzer,
    VideoOptimizer,
    VideoDuplicateDetector,
    VideoProcessor,
    VideoMetadata,
    VideoFingerprint,
    VideoAnalysisResult,
    VideoOptimizationResult,
    VideoProcessingError
)

from .audio_processing import (
    AudioAnalyzer,
    AudioFingerprinter,
    SpectralAnalyzer,
    ChromaprintProcessor,
    AudioFeatureExtractor
)

from .business_logic import (
    ContentProcessor,
    RevenueCalculator,
    InfluencerMetrics,
    CollaborationMatcher,
    MonetizationEngine
)

from .cache_manager import (
    CacheManager,
    RedisHandler,
    MemoryOptimizer,
    CacheStrategy,
    PerformanceMonitor
)

from .content_protection import (
    FingerprintGenerator,
    ContentValidator,
    PiracyDetector,
    ProtectionEngine,
    ViolationReporter
)

from .data_processing import (
    DataTransformer,
    DataValidator,
    DataNormalizer,
    BatchProcessor,
    StreamProcessor
)

from .encryption_utils import (
    EncryptionManager,
    HashGenerator,
    TokenValidator,
    SecureStorage,
    CryptoHelper
)

from .files import (
    guess_media_type,
    ALLOWED_MIME
)

from .image_processing import (
    ImageAnalyzer,
    ImageFingerprinter,
    PerceptualHasher,
    ImageFeatureExtractor,
    VisualContentProcessor
)

from .json_utils import (
    JSONProcessor,
    SchemaValidator,
    DataSerializer,
    ConfigParser,
    MetadataExtractor
)

from .multimedia_converter import (
    MediaConverter,
    FormatDetector,
    CompressionEngine,
    QualityOptimizer,
    BatchConverter
)

from .notification_helper import (
    NotificationManager,
    EmailSender,
    WebSocketNotifier,
    AlertProcessor,
    CommunicationHub
)

from .platform_integration import (
    SpotifyConnector,
    YouTubeConnector,
    InstagramConnector,
    TikTokConnector,
    PlatformManager
)

from .security_utils import (
    SecurityValidator,
    AuditLogger,
    ThreatDetector,
    AccessController,
    ComplianceChecker
)

from .text_processing import (
    TextAnalyzer,
    SemanticProcessor,
    ContentExtractor,
    LanguageDetector,
    TextFingerprinter
)

from .validation_utils import (
    InputValidator,
    ContentValidator,
    BusinessRuleValidator,
    DataIntegrityChecker,
    QualityAssurance
)

from .video_processing import (
    VideoAnalyzer,
    VideoFingerprinter,
    FrameExtractor,
    VideoFeatureExtractor,
    ContentAnalyzer
)

__all__ = [
    # Audio Processing
    "AudioAnalyzer",
    "AudioFingerprinter", 
    "SpectralAnalyzer",
    "ChromaprintProcessor",
    "AudioFeatureExtractor",
    
    # Business Logic
    "ContentProcessor",
    "RevenueCalculator",
    "InfluencerMetrics", 
    "CollaborationMatcher",
    "MonetizationEngine",
    
    # Cache Management
    "CacheManager",
    "RedisHandler",
    "MemoryOptimizer",
    "CacheStrategy",
    "PerformanceMonitor",
    
    # Content Protection
    "FingerprintGenerator",
    "ContentValidator",
    "PiracyDetector",
    "ProtectionEngine", 
    "ViolationReporter",
    
    # Data Processing
    "DataTransformer",
    "DataValidator",
    "DataNormalizer",
    "BatchProcessor",
    "StreamProcessor",
    
    # Encryption & Security
    "EncryptionManager",
    "HashGenerator",
    "TokenValidator",
    "SecureStorage",
    "CryptoHelper",
    
    # Files
    "guess_media_type",
    "ALLOWED_MIME",
    
    # Image Processing
    "ImageAnalyzer",
    "ImageFingerprinter",
    "PerceptualHasher",
    "ImageFeatureExtractor",
    "VisualContentProcessor",
    
    # JSON Processing
    "JSONProcessor",
    "SchemaValidator", 
    "DataSerializer",
    "ConfigParser",
    "MetadataExtractor",
    
    # Multimedia Conversion
    "MediaConverter",
    "FormatDetector",
    "CompressionEngine",
    "QualityOptimizer",
    "BatchConverter",
    
    # Notifications
    "NotificationManager",
    "EmailSender",
    "WebSocketNotifier", 
    "AlertProcessor",
    "CommunicationHub",
    
    # Platform Integration
    "SpotifyConnector",
    "YouTubeConnector",
    "InstagramConnector",
    "TikTokConnector",
    "PlatformManager",
    
    # Security Utils
    "SecurityValidator",
    "AuditLogger",
    "ThreatDetector",
    "AccessController",
    "ComplianceChecker",
    
    # Text Processing
    "TextAnalyzer",
    "SemanticProcessor",
    "ContentExtractor",
    "LanguageDetector",
    "TextFingerprinter",
    
    # Validation
    "InputValidator",
    "ContentValidator",
    "BusinessRuleValidator", 
    "DataIntegrityChecker",
    "QualityAssurance",
    
    # Video Processing
    "VideoAnalyzer",
    "VideoFingerprinter",
    "FrameExtractor",
    "VideoFeatureExtractor",
    "ContentAnalyzer",
]
