"""IA Influencer Agent - Core Fingerprinting Module
Digital fingerprinting system for multimedia content protection

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved to Fahed Mlaiel
Warning: Unauthorized use, copying, or distribution of this code is strictly prohibited

This module provides enterprise-grade digital fingerprinting capabilities for:
- Audio content fingerprinting (Chromaprint, MFCC, spectral analysis)
- Video content fingerprinting (perceptual hashing, optical flow, edge detection)
- Image content fingerprinting (perceptual hashing, SIFT, texture analysis)
- High-performance similarity search with FAISS integration
- Advanced analytics and forensic analysis
- Cryptographic hash generation and verification

Key Features:
- Multi-algorithm fingerprinting for maximum accuracy
- Real-time similarity matching and detection
- Automated duplicate content identification
- Forensic analysis and comprehensive reporting
- Async/await architecture for high throughput
- GPU acceleration support (CUDA)
- Vector-based similarity search (sub-second matching)
- Enterprise-level security implementations
"""
from .audio_fingerprint import AudioFingerprintEngine
from .video_fingerprint import VideoFingerprintEngine
from .image_fingerprint import ImageFingerprintEngine
from .fingerprint_manager import FingerprintManager, FingerprintResult, ContentType
from .fingerprint_analyzer import FingerprintAnalyzer, AnalysisReport, SimilarityCluster
from .similarity_engine import SimilarityEngine, SimilarityMatch
from .hash_generator import HashGenerator, HashResult

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__copyright__ = "Copyright © 2025 Fahed Mlaiel. All rights reserved."

# Import index and examples
from .index import (
    FingerprintingIndex,
    fingerprinting_index,
    get_fingerprinting_system,
    get_engine_for_content,
    get_supported_formats,
    validate_fingerprinting_system,
    get_fingerprinting_info
)

from .examples import (
    FingerprintingExamples,
    quick_demo_audio,
    quick_demo_security,
    quick_demo_workflow
)

# Import configuration
from .config import (
    FingerprintingConfig,
    FingerprintingConstants,
    DEFAULT_CONFIG,
    PRODUCTION_CONFIG,
    DEVELOPMENT_CONFIG,
    TESTING_CONFIG,
    get_config_from_environment,
    get_current_config
)

# Import tests
from .tests import (
    run_tests,
    TestFingerprintManager,
    TestHashGenerator,
    TestSimilarityEngine,
    TestFingerprintAnalyzer,
    TestFingerprintingIndex
)

# Export everything for easy access
__all__ = [
    # Core engines
    'AudioFingerprintEngine',
    'VideoFingerprintEngine', 
    'ImageFingerprintEngine',
    
    # Core services
    'FingerprintManager',
    'FingerprintAnalyzer',
    'SimilarityEngine',
    'HashGenerator',
    
    # Data classes
    'FingerprintResult',
    'ContentType',
    'AnalysisReport',
    'SimilarityCluster',
    'SimilarityMatch', 
    'HashResult',
    
    # Index and utilities
    'FingerprintingIndex',
    'fingerprinting_index',
    'get_fingerprinting_system',
    'get_engine_for_content',
    'get_supported_formats',
    'validate_fingerprinting_system',
    'get_fingerprinting_info',
    
    # Examples and demos
    'FingerprintingExamples',
    'quick_demo_audio',
    'quick_demo_security',
    'quick_demo_workflow',
    
    # Configuration
    'FingerprintingConfig',
    'FingerprintingConstants',
    'DEFAULT_CONFIG',
    'PRODUCTION_CONFIG',
    'DEVELOPMENT_CONFIG',
    'TESTING_CONFIG',
    'get_config_from_environment',
    'get_current_config',
    
    # Testing
    'run_tests',
    'TestFingerprintManager',
    'TestHashGenerator',
    'TestSimilarityEngine',
    'TestFingerprintAnalyzer',
    'TestFingerprintingIndex',
    
    # Module metadata
    '__version__',
    '__author__',
    '__email__',
    '__copyright__'
]

# Module configuration
SUPPORTED_AUDIO_FORMATS = ['.mp3', '.wav', '.flac', '.m4a', '.ogg', '.aac']
SUPPORTED_VIDEO_FORMATS = ['.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv', '.wmv']
SUPPORTED_IMAGE_FORMATS = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp', '.gif']

DEFAULT_SIMILARITY_THRESHOLD = 0.85
DEFAULT_VECTOR_DIMENSION = 512
DEFAULT_CACHE_SIZE = 1000
