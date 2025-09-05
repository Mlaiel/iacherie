"""Advanced Multimedia Processing Platform
High-performance multimedia content processing, analysis, and distribution system.

Project Team: Lead AI Developer + Backend Senior Engineer + ML Engineer + 
              Database Administrator + Security Expert + Microservices Architect +
              Multimedia Processing Specialist + DevOps Engineer + AI Prompt Engineer

Created by: Fahed Mlaiel <mlaiel@live.de>

⚠️ STRICT COPYRIGHT WARNING ⚠️
This code is proprietary and confidential. Any unauthorized use, reproduction, 
distribution, or modification without written permission from Fahed Mlaiel 
(mlaiel@live.de) is strictly prohibited and will be prosecuted to the full 
extent of the law. All rights reserved.

Contact: mlaiel@live.de for licensing and authorization inquiries.
"""

# Import working modules
from .formats import (
    SupportedFormats,
    AudioFormat,
    VideoFormat,
    ImageFormat,
    ContentFormat
)

from .validators import (
    ContentValidator,
    MediaValidator,
    QualityValidator,
    ValidationResult,
    ValidationRule
)

from .distribution import (
    ContentDistributor,
    MonetizationEngine,
    YouTubeIntegration,
    InstagramIntegration,
    PlatformType,
    ContentType,
    MonetizationModel,
    DistributionConfig,
    MonetizationConfig,
    DistributionResult,
    RevenueData
)

from .monitoring import (
    ContentMonitor,
    YouTubeCrawler,
    InstagramCrawler,
    TikTokCrawler,
    ViolationType,
    MonitoringConfig,
    ViolationAlert,
    SearchResult
)

from .optimization import (
    ContentOptimizer,
    CompressionEngine,
    QualityEnhancer
)

from .protection import (
    ContentProtector,
    WatermarkEngine,
    FingerprintGenerator,
    WatermarkConfig
)

from .video import (
    VideoProcessor,
    VideoAnalyzer,
    VideoProcessingResult
)

from .metadata_extractor import (
    MetadataExtractor,
    AudioMetadata,
    VideoMetadata,
    ImageMetadata,
    MultimediaMetadata
)

# Version info
__version__ = "2.1.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"

__all__ = [
    # Format definitions
    "SupportedFormats",
    "AudioFormat", 
    "VideoFormat",
    "ImageFormat",
    "ContentFormat",
    
    # Validation
    "ContentValidator",
    "MediaValidator",
    "QualityValidator",
    "ValidationResult",
    "ValidationRule",
    
    # Distribution and Monetization
    "ContentDistributor",
    "MonetizationEngine",
    "YouTubeIntegration",
    "InstagramIntegration",
    "PlatformType",
    "ContentType",
    "MonetizationModel",
    "DistributionConfig",
    "MonetizationConfig",
    "DistributionResult",
    "RevenueData",
    
    # Content Monitoring
    "ContentMonitor",
    "YouTubeCrawler",
    "InstagramCrawler",
    "TikTokCrawler",
    "ViolationType",
    "MonitoringConfig",
    "ViolationAlert",
    "SearchResult",
    
    # Optimization
    "ContentOptimizer",
    "CompressionEngine",
    "QualityEnhancer",
    
    # Protection
    "ContentProtector",
    "WatermarkEngine",
    "FingerprintGenerator",
    "WatermarkConfig",
    
    # Video Processing
    "VideoProcessor",
    "VideoAnalyzer",
    "VideoProcessingResult",
    
    # Metadata Extraction
    "MetadataExtractor",
    "AudioMetadata",
    "VideoMetadata",
    "ImageMetadata",
    "MultimediaMetadata"
]
