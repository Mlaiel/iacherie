"""IA Influencer Agent - Industrial Extractors Module
=================================================

Ultra-advanced professional extraction module for AI-powered content processing.
Implements enterprise-grade extraction capabilities for multimedia content analysis.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

WARNING: This code is protected by copyright law. Any unauthorized copying, 
distribution, or modification is strictly prohibited and will result in 
legal action. Contact mlaiel@live.de for licensing.

⚠️ STRICT COPYRIGHT PROTECTION ⚠️
This code is the intellectual property of Fahed Mlaiel (mlaiel@live.de).
UNAUTHORIZED USE STRICTLY PROHIBITED - Legal action will be taken.

Technical Team Expertise:
- Lead IA Developer: Advanced AI/ML algorithms and neural networks
- Backend Senior: Enterprise architecture and microservices
- ML Engineer: Machine learning pipelines and model optimization
- Database Administrator: Data architecture and optimization
- Security Specialist: Cybersecurity and data protection
- Microservices Architect: Distributed systems and scalability
- Audio Engineer: Digital signal processing and audio analysis
- DevOps Engineer: Infrastructure automation and deployment
- IA Prompt Engineer: Prompt optimization and AI interaction

Project Owner: Fahed Mlaiel - mlaiel@live.de

Module d'extraction de contenu multimédia et d'analyse IA
=========================================================

Ce module fournit des extracteurs industriels avancés pour :
- Extraction de contenu multimédia avec analyse IA
- Analyse de plateformes sociales et identification d'influenceurs
- Empreintes digitales et protection de contenu
- Analyse de revenus et monétisation
- Détection de collaborations et opportunités
- Surveillance et protection de marque
- Analytics et insights prédictifs
- Protection intellectuelle avancée

Tous les extracteurs utilisent des algorithmes d'IA propriétaires
pour fournir des analyses précises et des détections en temps réel.
"""# Import core extraction components
from .extraction_engine import (
    BaseExtractor, ExtractionRequest, ExtractionResult, 
    ExtractionStatus, ContentType, ExtractionPriority,
    ExtractionEngine, create_content_extraction_engine,
    create_realtime_extraction_engine, create_batch_extraction_engine
)

# Import content extractors
from .content_extractors import (
    AudioContentExtractor, VideoContentExtractor,
    ImageContentExtractor, TextContentExtractor,
    MetadataExtractor, ThumbnailExtractor,
    ContentMetadata, AudioFeatures, VideoFeatures,
    ImageFeatures, TextFeatures
)

# Import platform extractors
from .platform_extractors import (
    PlatformExtractor, YouTubeExtractor, InstagramExtractor,
    TikTokExtractor, TwitterExtractor, FacebookExtractor,
    SpotifyExtractor, PlatformExtractorFactory,
    PlatformMetadata, SocialMetrics, EngagementData
)

# Import fingerprint extractors
from .fingerprint_extractors import (
    FingerprintExtractor, AudioFingerprintExtractor,
    VideoFingerprintExtractor, ImageFingerprintExtractor,
    TextFingerprintExtractor, FingerprintResult,
    AudioFingerprint, VideoFingerprint, ImageFingerprint, TextFingerprint
)

# Import revenue extractors
from .revenue_extractors import (
    RevenueExtractor, YouTubeRevenueExtractor, SpotifyRevenueExtractor,
    InstagramRevenueExtractor, TikTokRevenueExtractor,
    RevenueMetrics, PlatformRevenueData, RevenueAlert,
    PlatformType, RevenueStatus
)

# Import collaboration extractors
from .collaboration_extractors import (
    CollaborationExtractor, CreatorMatcher, CollaborationAnalyzer,
    CreatorProfile, CollaborationMatch, CollaborationProposal,
    CollaborationType, MatchingCriteria, CollaborationStatus
)

# Import surveillance extractors
from .surveillance_extractors import (
    SurveillanceExtractor, ContentMonitor, InfringementDetector,
    SurveillanceReport, InfringementAlert, EvidencePackage,
    MonitoringProfile, ThreatLevel
)

# Import stream extractors
from .stream_extractors import (
    StreamExtractor, WebSocketExtractor, HTTPStreamExtractor,
    AudioStreamExtractor, VideoStreamExtractor, RedisStreamExtractor,
    LiveAPIExtractor, StreamManager, StreamMetadata, StreamType
)

# Import data extractors
from .data_extractors import (
    DataExtractor, JSONExtractor, CSVExtractor, XMLExtractor,
    ExcelExtractor, DatabaseExtractor, APIExtractor,
    DataExtractorFactory, StructuredDataMetadata
)

# Import web extractors
from .web_extractors import (
    WebExtractor, HTMLExtractor, ArticleExtractor, MetaTagExtractor,
    LinkExtractor, WebExtractorFactory, WebMetadata
)

# Import protection extractors (NEW)
from .protection_extractors import (
    ContentProtectionExtractor, DigitalWatermarkExtractor,
    ProtectionProfile, InfringementDetection, ProtectionLevel,
    InfringementType, ProtectionAction, create_protection_extractor_suite
)

# Import analytics extractors (NEW)
from .analytics_extractors import (
    PerformanceAnalyticsExtractor, AudienceAnalyticsExtractor,
    AnalyticsConfig, PerformanceMetrics, AudienceInsights,
    PredictiveInsights, AnalyticsType, InsightLevel,
    PredictionHorizon, create_analytics_extractor_suite
)

# Import coordination system
from .extraction_coordinator import (
    ExtractionCoordinator, ExtractionPlan, ExtractionStrategy,
    CoordinationMode, ExtractorRegistry
)

# Import main index orchestrator
from .index import (
    ExtractionOrchestrator, ExtractionJob, ExtractorCapability,
    ExtractionMode, PriorityLevel
)
from enum import Enum

# Import extraction components
from .content_extractors import (
    AudioContentExtractor, VideoContentExtractor, 
    ImageContentExtractor, TextContentExtractor,
    MetadataExtractor, ThumbnailExtractor
)

from .platform_extractors import (
    YouTubeExtractor, InstagramExtractor, TikTokExtractor,
    TwitterExtractor, FacebookExtractor, SpotifyExtractor,
    PlatformExtractorFactory, register_default_extractors
)

from .data_extractors import (
    JSONExtractor, CSVExtractor, XMLExtractor, ExcelExtractor,
    DataExtractorFactory, register_default_data_extractors
)

from .web_extractors import (
    HTMLExtractor, ArticleExtractor, WebExtractorFactory,
    register_default_web_extractors
)

from .stream_extractors import (
    WebSocketExtractor, HTTPStreamExtractor, AudioStreamExtractor,
    VideoStreamExtractor, RedisStreamExtractor, LiveAPIExtractor,
    StreamManager, stream_manager, register_default_stream_extractors
)

# Import new specialized extractors for IA protection and monetization
from .fingerprint_extractors import (
    AudioFingerprintExtractor, VideoFingerprintExtractor,
    ImageFingerprintExtractor, TextFingerprintExtractor,
    FingerprintManager, FingerprintResult, FingerprintExtractorFactory
)

from .revenue_extractors import (
    YouTubeRevenueExtractor, SpotifyRevenueExtractor,
    InstagramRevenueExtractor, TikTokRevenueExtractor,
    RevenueAnalyzer, PaymentProcessor, RevenueExtractorFactory,
    RevenueMetrics, RevenueSource, PaymentInfo
)

from .surveillance_extractors import (
    YouTubeSurveillanceExtractor, InstagramSurveillanceExtractor,
    TikTokSurveillanceExtractor, GenericWebSurveillanceExtractor,
    SurveillanceManager, ViolationAlert, MonitoringJob, EvidencePackage
)

from .collaboration_extractors import (
    CreatorProfileExtractor, CollaborationMatcher,
    CollaborationAnalyzer, CollaborationExtractorFactory,
    CreatorProfile, CollaborationMatch, CollaborationProposal
)

from .extraction_coordinator import (
    ExtractionOrchestrator, ExtractionRouter, ExtractionStrategy,
    CoordinationMode, orchestrator
)

# Import core base classes
from .extraction_engine import (
    BaseExtractor, ExtractionEngine, ExtractionRequest, ExtractionResult,
    ExtractionStatus, ExtractionPriority, ContentType
)

# Export main components
__all__ = [
    # Core Engine
    'BaseExtractor',
    'ExtractionEngine',
    'ExtractionRequest', 
    'ExtractionResult',
    'ExtractionStatus',
    'ExtractionPriority',
    'ContentType',
    
    # Content Extractors
    'AudioContentExtractor',
    'VideoContentExtractor',
    'ImageContentExtractor', 
    'TextContentExtractor',
    'MetadataExtractor',
    'ThumbnailExtractor',
    
    # Platform Extractors
    'YouTubeExtractor',
# Complete exports list for the extractors module
__all__ = [
    # Core extraction engine
    'BaseExtractor',
    'ExtractionRequest',
    'ExtractionResult', 
    'ExtractionStatus',
    'ContentType',
    'ExtractionPriority',
    'ExtractionEngine',
    'create_content_extraction_engine',
    'create_realtime_extraction_engine',
    'create_batch_extraction_engine',
    
    # Content extractors
    'AudioContentExtractor',
    'VideoContentExtractor',
    'ImageContentExtractor', 
    'TextContentExtractor',
    'MetadataExtractor',
    'ThumbnailExtractor',
    'ContentMetadata',
    'AudioFeatures',
    'VideoFeatures',
    'ImageFeatures',
    'TextFeatures',
    
    # Platform extractors
    'PlatformExtractor',
    'YouTubeExtractor',
    'InstagramExtractor',
    'TikTokExtractor',
    'TwitterExtractor',
    'FacebookExtractor',
    'SpotifyExtractor',
    'PlatformExtractorFactory',
    'PlatformMetadata',
    'SocialMetrics',
    'EngagementData',
    
    # Fingerprint extractors
    'FingerprintExtractor',
    'AudioFingerprintExtractor',
    'VideoFingerprintExtractor',
    'ImageFingerprintExtractor',
    'TextFingerprintExtractor',
    'FingerprintResult',
    'AudioFingerprint',
    'VideoFingerprint',
    'ImageFingerprint',
    'TextFingerprint',
    
    # Revenue extractors
    'RevenueExtractor',
    'YouTubeRevenueExtractor',
    'SpotifyRevenueExtractor',
    'InstagramRevenueExtractor',
    'TikTokRevenueExtractor',
    'RevenueMetrics',
    'PlatformRevenueData',
    'RevenueAlert',
    'PlatformType',
    'RevenueStatus',
    
    # Collaboration extractors
    'CollaborationExtractor',
    'CreatorMatcher',
    'CollaborationAnalyzer',
    'CreatorProfile',
    'CollaborationMatch',
    'CollaborationProposal',
    'CollaborationType',
    'MatchingCriteria',
    'CollaborationStatus',
    
    # Surveillance extractors
    'SurveillanceExtractor',
    'ContentMonitor',
    'InfringementDetector',
    'SurveillanceReport',
    'InfringementAlert',
    'EvidencePackage',
    'MonitoringProfile',
    'ThreatLevel',
    
    # Stream extractors
    'StreamExtractor',
    'WebSocketExtractor',
    'HTTPStreamExtractor',
    'AudioStreamExtractor',
    'VideoStreamExtractor', 
    'RedisStreamExtractor',
    'LiveAPIExtractor',
    'StreamManager',
    'StreamMetadata',
    'StreamType',
    
    # Data extractors
    'DataExtractor',
    'JSONExtractor',
    'CSVExtractor',
    'XMLExtractor',
    'ExcelExtractor',
    'DatabaseExtractor',
    'APIExtractor',
    'DataExtractorFactory',
    'StructuredDataMetadata',
    
    # Web extractors
    'WebExtractor',
    'HTMLExtractor',
    'ArticleExtractor',
    'MetaTagExtractor',
    'LinkExtractor',
    'WebExtractorFactory',
    'WebMetadata',
    
    # Protection extractors (NEW)
    'ContentProtectionExtractor',
    'DigitalWatermarkExtractor',
    'ProtectionProfile',
    'InfringementDetection',
    'ProtectionLevel',
    'InfringementType',
    'ProtectionAction',
    'create_protection_extractor_suite',
    
    # Analytics extractors (NEW)
    'PerformanceAnalyticsExtractor',
    'AudienceAnalyticsExtractor',
    'AnalyticsConfig',
    'PerformanceMetrics',
    'AudienceInsights',
    'PredictiveInsights',
    'AnalyticsType',
    'InsightLevel',
    'PredictionHorizon',
    'create_analytics_extractor_suite',
    
    # Coordination system
    'ExtractionCoordinator',
    'ExtractionPlan',
    'ExtractionStrategy',
    'CoordinationMode',
    'ExtractorRegistry',
    
    # Main orchestrator
    'ExtractionOrchestrator',
    'ExtractionJob',
    'ExtractorCapability',
    'ExtractionMode',
    'PriorityLevel',
    
    # Utility functions
    'extract_from_url',
    'extract_from_file', 
    'extract_from_data',
    'extract_content',
    'extract_metadata',
    'extract_fingerprint',
    'monitor_content',
    'analyze_revenue',
    'find_collaborations',
    'analyze_performance',
    'protect_content',
    'detect_infringement',
    'create_protection_profile',
    'generate_analytics_report',
    'get_extraction_result',
    'get_extraction_status'
]


# Module-level configuration
logger = logging.getLogger(__name__)

# Default extraction configuration
DEFAULT_EXTRACTION_CONFIG = {
    'max_workers': 10,
    'max_concurrent_extractions': 50,
    'default_timeout': 300,
    'enable_ai_features': True,
    'enable_protection': True,
    'enable_analytics': True,
    'cache_results': True,
    'monitoring_enabled': True
}

# Global extractor registry
_EXTRACTOR_REGISTRY = {}

def register_extractor(name: str, extractor_class: type):
    """Register a new extractor type"""
    _EXTRACTOR_REGISTRY[name] = extractor_class
    logger.info(f"Registered extractor: {name}")

def get_registered_extractors():
    """Get all registered extractors"""
    return _EXTRACTOR_REGISTRY.copy()

def create_extractor(name: str, **kwargs):
    """Create an extractor instance by name"""
    if name not in _EXTRACTOR_REGISTRY:
        raise ValueError(f"Unknown extractor type: {name}")
    
    extractor_class = _EXTRACTOR_REGISTRY[name]
    return extractor_class(**kwargs)


# Utility functions for common operations
async def extract_from_url(url: str, extraction_types: List[str] = None, **kwargs) -> ExtractionResult:
    """Extract data from a URL using appropriate extractors"""
    request = ExtractionRequest(
        source_url=url,
        extraction_types=extraction_types or ['content', 'metadata'],
        **kwargs
    )
    
    # Use default orchestrator
    orchestrator = ExtractionOrchestrator()
    return await orchestrator.process_extraction_job(request)

async def extract_from_file(file_path: str, extraction_types: List[str] = None, **kwargs) -> ExtractionResult:
    """Extract data from a file using appropriate extractors"""
    request = ExtractionRequest(
        source_path=file_path,
        extraction_types=extraction_types or ['content', 'metadata'],
        **kwargs
    )
    
    orchestrator = ExtractionOrchestrator()
    return await orchestrator.process_extraction_job(request)

async def extract_from_data(data: bytes, content_type: ContentType, extraction_types: List[str] = None, **kwargs) -> ExtractionResult:
    """Extract data from binary data using appropriate extractors"""
    request = ExtractionRequest(
        source_data=data,
        content_type=content_type,
        extraction_types=extraction_types or ['content', 'metadata'],
        **kwargs
    )
    
    orchestrator = ExtractionOrchestrator()
    return await orchestrator.process_extraction_job(request)

async def protect_content(content_data: Any, protection_level: ProtectionLevel = ProtectionLevel.STANDARD, **kwargs) -> ExtractionResult:
    """Apply content protection using protection extractors"""
    request = ExtractionRequest(
        source_data=content_data if isinstance(content_data, bytes) else str(content_data).encode(),
        extraction_types=['protection', 'fingerprint', 'watermark'],
        metadata={'protection_level': protection_level.value, **kwargs}
    )
    
    protector = ContentProtectionExtractor()
    return await protector.extract(request)

async def analyze_performance(data_sources: List[str], platforms: List[str] = None, **kwargs) -> ExtractionResult:
    """Analyze content performance using analytics extractors"""
    request = ExtractionRequest(
        source_data=json.dumps({'data_sources': data_sources}).encode(),
        extraction_types=['performance', 'analytics', 'insights'],
        metadata={
            'platforms': platforms or ['youtube', 'instagram'],
            'analytics_config': kwargs
        }
    )
    
    analyzer = PerformanceAnalyticsExtractor()
    return await analyzer.extract(request)

# Initialize default extractors
def _initialize_default_extractors():
    """Initialize and register default extractors"""
    try:
        # Register core extractors
        register_extractor('audio_content', AudioContentExtractor)
        register_extractor('video_content', VideoContentExtractor)
        register_extractor('image_content', ImageContentExtractor)
        register_extractor('text_content', TextContentExtractor)
        
        # Register platform extractors
        register_extractor('youtube', YouTubeExtractor)
        register_extractor('instagram', InstagramExtractor)
        register_extractor('tiktok', TikTokExtractor)
        register_extractor('spotify', SpotifyExtractor)
        
        # Register protection extractors
        register_extractor('content_protection', ContentProtectionExtractor)
        register_extractor('digital_watermark', DigitalWatermarkExtractor)
        
        # Register analytics extractors
        register_extractor('performance_analytics', PerformanceAnalyticsExtractor)
        register_extractor('audience_analytics', AudienceAnalyticsExtractor)
        
        logger.info("Default extractors initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize default extractors: {e}")

# Initialize on module import
_initialize_default_extractors()


async def initialize_extraction_system():
    """Initialize complete extraction system"""
    # Start orchestrator
    await orchestrator.start()
    
    logger.info("Extraction system initialized successfully")


async def shutdown_extraction_system():
    """Shutdown extraction system"""
    # Stop orchestrator
    await orchestrator.stop()
    
    logger.info("Extraction system shutdown completed")


# Main extraction function
async def extract_content(request: ExtractionRequest, strategy: ExtractionStrategy = ExtractionStrategy.INTELLIGENT) -> str:
    """Main extraction function - submit request and return plan ID"""
    return await orchestrator.submit_extraction(request, strategy)


async def get_extraction_result(plan_id: str) -> Optional[ExtractionResult]:
    """Get extraction result by plan ID"""
    return await orchestrator.get_extraction_result(plan_id)


async def get_extraction_status(plan_id: str) -> Optional[ExtractionStatus]:
    """Get extraction status by plan ID"""
    return await orchestrator.get_extraction_status(plan_id)


# Utility functions
def create_url_extraction_request(url: str, extraction_types: List[str] = None, priority: ExtractionPriority = ExtractionPriority.NORMAL) -> ExtractionRequest:
    """Create extraction request for URL"""
    return ExtractionRequest(
        source_url=url,
        extraction_types=extraction_types or ["content", "metadata"],
        priority=priority
    )


def create_file_extraction_request(file_path: str, extraction_types: List[str] = None, priority: ExtractionPriority = ExtractionPriority.NORMAL) -> ExtractionRequest:
    """Create extraction request for file"""
    return ExtractionRequest(
        source_path=file_path,
        extraction_types=extraction_types or ["content", "metadata"],
        priority=priority
    )


def create_data_extraction_request(data: bytes, content_type: ContentType = ContentType.TEXT, extraction_types: List[str] = None, priority: ExtractionPriority = ExtractionPriority.NORMAL) -> ExtractionRequest:
    """Create extraction request for raw data"""
    return ExtractionRequest(
        source_data=data,
        content_type=content_type,
        extraction_types=extraction_types or ["content", "metadata"],
        priority=priority
    )


# Advanced utility functions for IA protection and monetization
async def extract_fingerprint(content: Union[bytes, str], content_type: str) -> Optional[FingerprintResult]:
    """Extract fingerprint from content for protection"""
    try:
        fingerprint_manager = FingerprintManager()
        return await fingerprint_manager.extract_fingerprint(content, content_type)
    except Exception as e:
        logger.error(f"Fingerprint extraction failed: {e}")
        return None


async def monitor_content(content_fingerprints: List[str], platforms: List[str], keywords: List[str]) -> Optional[MonitoringJob]:
    """Start content monitoring for protection"""
    try:
        surveillance_manager = SurveillanceManager()
        return await surveillance_manager.create_monitoring_job(
            content_fingerprints, platforms, keywords
        )
    except Exception as e:
        logger.error(f"Content monitoring setup failed: {e}")
        return None


async def analyze_revenue(creator_id: str, platform: str, period_start: datetime, period_end: datetime) -> Dict[str, Any]:
    """Analyze revenue for creator on platform"""
    try:
        analyzer = RevenueAnalyzer()
        # This would fetch revenue data and analyze it
        return await analyzer.analyze_revenue_trends([])
    except Exception as e:
        logger.error(f"Revenue analysis failed: {e}")
        return {}


async def find_collaborations(creator_profile: CreatorProfile, criteria: List[MatchingCriteria]) -> List[CollaborationMatch]:
    """Find collaboration matches for creator"""
    try:
        matcher = CollaborationMatcher()
        return await matcher.find_collaboration_matches(creator_profile, criteria)
    except Exception as e:
        logger.error(f"Collaboration matching failed: {e}")
        return []


class ExtractionConfig:
    """Global extraction configuration"""
    
    # Performance settings
    MAX_CONCURRENT_EXTRACTIONS = 50
    EXTRACTION_TIMEOUT = 300  # 5 minutes
    MAX_CONTENT_SIZE = 100 * 1024 * 1024  # 100MB
    
    # Quality settings
    MIN_CONTENT_QUALITY = 0.7
    MAX_DUPLICATE_SIMILARITY = 0.95
    
    # Cache settings
    CACHE_ENABLED = True
    CACHE_TTL = 3600  # 1 hour
    MAX_CACHE_SIZE = 1000
    
    # Rate limiting
    RATE_LIMIT_REQUESTS = 100
    RATE_LIMIT_WINDOW = 60  # seconds
    
    # Retry settings
    MAX_RETRIES = 3
    RETRY_DELAY = 1.0


# Export all components
__all__ = [
    # Core extraction engine
    'BaseExtractor',
    'ExtractionEngine', 
    'ExtractionRequest',
    'ExtractionResult',
    'ExtractionStatus',
    'ExtractionPriority',
    'ContentType',
    
    # Content extractors
    'AudioContentExtractor',
    'VideoContentExtractor',
    'ImageContentExtractor', 
    'TextContentExtractor',
    'MetadataExtractor',
    'ThumbnailExtractor',
    
    # Platform extractors
    'YouTubeExtractor',
    'InstagramExtractor',
    'TikTokExtractor',
    'TwitterExtractor',
    'FacebookExtractor',
    'SpotifyExtractor',
    'PlatformExtractorFactory',
    
    # Data extractors
    'JSONExtractor',
    'CSVExtractor',
    'XMLExtractor',
    'ExcelExtractor',
    'DataExtractorFactory',
    
    # Web extractors
    'HTMLExtractor',
    'ArticleExtractor',
    'WebExtractorFactory',
    
    # Stream extractors
    'WebSocketExtractor',
    'HTTPStreamExtractor',
    'AudioStreamExtractor',
    'VideoStreamExtractor',
    'RedisStreamExtractor',
    'LiveAPIExtractor',
    'StreamManager',
    'stream_manager',
    
    # Advanced IA protection extractors
    'AudioFingerprintExtractor',
    'VideoFingerprintExtractor',
    'ImageFingerprintExtractor',
    'TextFingerprintExtractor',
    'FingerprintManager',
    'FingerprintResult',
    'FingerprintExtractorFactory',
    
    # Revenue and monetization extractors
    'YouTubeRevenueExtractor',
    'SpotifyRevenueExtractor',
    'InstagramRevenueExtractor',
    'TikTokRevenueExtractor',
    'RevenueAnalyzer',
    'PaymentProcessor',
    'RevenueExtractorFactory',
    'RevenueMetrics',
    'RevenueSource',
    'PaymentInfo',
    
    # Surveillance and protection extractors
    'YouTubeSurveillanceExtractor',
    'InstagramSurveillanceExtractor',
    'TikTokSurveillanceExtractor',
    'GenericWebSurveillanceExtractor',
    'SurveillanceManager',
    'ViolationAlert',
    'MonitoringJob',
    'EvidencePackage',
    
    # Collaboration extractors
    'CreatorProfileExtractor',
    'CollaborationMatcher',
    'CollaborationAnalyzer',
    'CollaborationExtractorFactory',
    'CreatorProfile',
    'CollaborationMatch',
    'CollaborationProposal',
    
    # Coordination and orchestration
    'ExtractionOrchestrator',
    'ExtractionRouter',
    'ExtractionStrategy',
    'CoordinationMode',
    'orchestrator',
    
    # Utility functions
    'extract_from_url',
    'extract_from_file',
    'extract_from_data',
    'extract_content',
    'extract_metadata',
    'extract_fingerprint',
    'monitor_content',
    'analyze_revenue',
    'find_collaborations',
    'get_extraction_result',
    'get_extraction_status',
    'create_url_extraction_request',
    'create_file_extraction_request',
    'create_data_extraction_request',
    
    # Configuration
    'ExtractionConfig'
]
