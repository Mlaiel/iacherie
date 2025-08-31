"""🔒 Content Fingerprinting System for IA-Influencer-Agent
========================================================

Multi-modal content fingerprinting system supporting audio, video, image, and text content.
Provides advanced fingerprinting algorithms for content protection and similarity detection.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

WARNING: This code and concept are protected by intellectual property rights.
Any unauthorized use, reproduction, or distribution without explicit written 
permission from Fahed Mlaiel is strictly prohibited and will result in legal action.
Contact: mlaiel@live.de for authorization requests.
"""
# Core services
from .fingerprinting_service import FingerprintingService

# Content-specific services
from .audio import (
    AudioFingerprintingService,
    ChromaprintExtractor,
    EssentiaAnalyzer,
    SpectralHashGenerator,
    NeuralAudioEmbedding
)

from .video import (
    VideoFingerprintingService,
    PerceptualHashExtractor,
    OpticalFlowAnalyzer,
    ObjectDetectionAnalyzer,
    CNNFeatureExtractor
)

from .image import (
    ImageFingerprintingService,
    PerceptualImageHashing,
    CLIPEmbeddingExtractor,
    TraditionalFeatureExtractor,
    ColorAnalyzer,
    TextureAnalyzer
)

from .text import (
    TextFingerprintingService,
    BERTEmbeddingExtractor,
    SentenceTransformerExtractor,
    TFIDFAnalyzer,
    NGramAnalyzer,
    SemanticAnalyzer
)

# Data models and schemas
from .models import (
    ContentType,
    ProcessingStatus,
    SimilarityAlgorithm,
    FingerprintResult,
    SimilarityMatch,
    BatchProcessingJob,
    SimilaritySearchQuery,
    SimilaritySearchResult,
    AudioMetadata,
    VideoMetadata,
    ImageMetadata,
    TextMetadata,
    FingerprintData,
    ProcessingMetrics,
    QualityMetrics
)

# Utilities and helpers
from .utils import (
    FileHandler,
    DataProcessor,
    SimilarityCalculator,
    PerformanceOptimizer,
    VectorDatabase,
    ConfigManager,
    CacheManager,
    retry_on_failure,
    get_optimal_batch_size,
    setup_gpu_environment,
    validate_fingerprint_quality
)

# Exception handling
from .exceptions import (
    FingerprintingBaseException,
    FileProcessingError,
    UnsupportedFileFormatError,
    AlgorithmError,
    AudioProcessingError,
    VideoProcessingError,
    ImageProcessingError,
    TextProcessingError,
    ResourceError,
    ConfigurationError,
    ValidationError,
    handle_exception,
    log_exception
)

__version__ = "2.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"

# Main exports
# Import new enterprise modules
from .batch_processor import BatchProcessor, BatchJob, BatchJobStatus
from .monitoring import FingerprintingMonitor, MetricsCollector, AlertManager
from .optimization import PerformanceOptimizer, GPUAccelerator, CacheOptimizer
from .quality_assurance import QualityAssuranceSystem, ValidationRule, BenchmarkSuite
from .deployment import DeploymentOrchestrator, DeploymentConfig, ServiceConfig
from .security import SecurityManager, EncryptionManager, MFAManager

# Export main classes and functions for public API
__all__ = [
    # Core fingerprinting service
    'FingerprintingService',
    
    # Data models
    'ContentFingerprint', 'FingerprintMatch', 'BatchProcessingResult',
    'ContentType', 'MatchingAlgorithm', 'ProcessingStatus',
    
    # Audio fingerprinting
    'AudioFingerprintExtractor',
    
    # Configuration
    'FingerprintingConfig', 'AudioConfig', 'DatabaseConfig', 'CacheConfig',
    
    # Utilities
    'FingerprintDatabase', 'CacheManager', 'SecurityUtils',
    'format_duration', 'validate_file_type', 'calculate_file_hash',
    
    # Enterprise modules
    'BatchProcessor', 'BatchJob', 'BatchJobStatus',
    'FingerprintingMonitor', 'MetricsCollector', 'AlertManager',
    'PerformanceOptimizer', 'GPUAccelerator', 'CacheOptimizer',
    'QualityAssuranceSystem', 'ValidationRule', 'BenchmarkSuite',
    'DeploymentOrchestrator', 'DeploymentConfig', 'ServiceConfig',
    'SecurityManager', 'EncryptionManager', 'MFAManager'
]

# Package metadata
__package_info__ = {
    "name": "ia-influencer-agent-fingerprinting",
    "version": __version__,
    "description": "Advanced multi-modal content fingerprinting system",
    "author": __author__,
    "author_email": __email__,
    "license": "Proprietary",
    "copyright": "© 2025 Fahed Mlaiel. All rights reserved.",
    "documentation": "See README files for comprehensive documentation",
    "supported_content_types": ["audio", "video", "image", "text"],
    "algorithms": [
        "Chromaprint", "Essentia", "Spectral Hashing", "Neural Audio Embeddings",
        "Perceptual Video Hashing", "Optical Flow", "YOLO Object Detection",
        "Perceptual Image Hashing", "CLIP Embeddings", "Traditional CV Features", 
        "BERT Embeddings", "TF-IDF", "N-gram Analysis", "Semantic Analysis"
    ]
}
