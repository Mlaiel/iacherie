"""Advanced Audio Fingerprinting System for Content Protection.
Industrial-grade implementation for multi-format audio content identification and protection.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent - Audio Protection Suite
License: Proprietary - All rights reserved

WARNING: This code is proprietary and protected by copyright.
Any unauthorized use, reproduction, or distribution is strictly prohibited.
Contact: Fahed Mlaiel (mlaiel@live.de) for licensing agreements.

Team Specialization:
- Lead AI Developer: Fahed Mlaiel
- Backend Senior Engineer: Advanced system architecture
- ML Engineer: Machine learning algorithms implementation
- Database Administrator: High-performance data storage
- Security Engineer: Content protection and encryption
- Microservices Architect: Scalable system design
- Audio Processing Expert: Advanced signal processing
- DevOps Engineer: Production deployment and monitoring
- AI Prompt Engineer: Intelligent content analysis
"""
from .core import AudioFingerprintCore, FingerprintResult, MatchResult
from .hash_generator import (
    PerceptualHashGenerator, 
    HashComparator, 
    HashConfiguration
)
from .matching import (
    FingerprintMatchingEngine,
    SpectralMatcher,
    TemporalMatcher,
    MatchQuery,
    MatchCandidate,
    MatchResult as EngineMatchResult
)
from .database import (
    FingerprintDatabaseManager,
    FingerprintRecord,
    MatchRecord,
    QueryPerformanceRecord
)
from .config import (
    FingerprintingConfigManager,
    get_config,
    get_audio_config,
    get_fingerprinting_config,
    get_matching_config,
    get_database_config,
    get_security_config,
    get_performance_config,
    get_monitoring_config,
    Environment,
    ProtectionLevel
)
from .utils import (
    FileValidator,
    DataSerializer,
    PerformanceMonitor,
    TemporaryFileManager,
    AudioMetadata,
    format_duration,
    format_file_size,
    safe_filename,
    generate_unique_id,
    BatchProcessor
)
from .index import (
    AudioFingerprintingService,
    AudioFingerprintingAPI,
    create_service,
    create_api_service
)

import logging

# Configure logging for the fingerprinting module
logger = logging.getLogger(__name__)

# Version information
__version__ = "1.0.0"
__author__ = "Fahed Mlaiel <mlaiel@live.de>"
__copyright__ = "Copyright 2025, IA Influencer Agent - Audio Protection Suite"

# Export main classes and functions
__all__ = [
    # Core classes
    'AudioFingerprintCore',
    'FingerprintResult',
    'MatchResult',
    
    # Hash generation
    'PerceptualHashGenerator',
    'HashComparator',
    'HashConfiguration',
    
    # Matching engine
    'FingerprintMatchingEngine',
    'SpectralMatcher',
    'TemporalMatcher',
    'MatchQuery',
    'MatchCandidate',
    'EngineMatchResult',
    
    # Database integration
    'FingerprintDatabaseManager',
    'FingerprintRecord',
    'MatchRecord',
    'QueryPerformanceRecord',
    
    # Configuration management
    'FingerprintingConfigManager',
    'get_config',
    'get_audio_config',
    'get_fingerprinting_config',
    'get_matching_config',
    'get_database_config',
    'get_security_config',
    'get_performance_config',
    'get_monitoring_config',
    'Environment',
    'ProtectionLevel',
    
    # Utilities
    'FileValidator',
    'DataSerializer',
    'PerformanceMonitor',
    'TemporaryFileManager',
    'AudioMetadata',
    'format_duration',
    'format_file_size',
    'safe_filename',
    'generate_unique_id',
    'BatchProcessor',
    
    # Main service and API
    'AudioFingerprintingService',
    'AudioFingerprintingAPI',
    'create_service',
    'create_api_service',
    
    # Module metadata
    '__version__',
    '__author__',
    '__copyright__'
]


def get_system_info() -> dict:
    """Get comprehensive system information and capabilities."""
    try:
        import platform
        import psutil
        
        return {
            'module_version': __version__,
            'python_version': platform.python_version(),
            'system_platform': platform.system(),
            'architecture': platform.machine(),
            'cpu_count': psutil.cpu_count(),
            'memory_gb': round(psutil.virtual_memory().total / (1024**3), 2),
            'available_algorithms': [
                'chromaprint',
                'spectral_features',
                'perceptual_hash',
                'mfcc_features',
                'temporal_matching'
            ],
            'supported_formats': [
                'mp3', 'wav', 'flac', 'm4a', 'aac', 'ogg', 'wma'
            ]
        }
    except ImportError:
        return {
            'module_version': __version__,
            'note': 'System information requires psutil package'
        }


def create_fingerprinting_pipeline(config: dict = None) -> AudioFingerprintCore:
    """
    Create a complete fingerprinting pipeline with default configuration.
    
    Args:
        config: Optional configuration dictionary
        
    Returns:
        Configured AudioFingerprintCore instance
    """
    try:
        # Initialize configuration
        config_manager = FingerprintingConfigManager()
        
        if config:
            # Apply custom configuration
            for section, settings in config.items():
                for key, value in settings.items():
                    config_manager.update_runtime_setting(section, key, value)
        
        # Create core fingerprinting engine
        core_config = {
            'sample_rate': config_manager.audio_processing.sample_rate,
            'hop_length': config_manager.audio_processing.hop_length,
            'n_fft': config_manager.audio_processing.n_fft,
            'n_mels': config_manager.audio_processing.n_mels,
            'max_workers': config_manager.performance.max_concurrent_fingerprints,
            'similarity_threshold': config_manager.fingerprinting.similarity_threshold
        }
        
        fingerprint_core = AudioFingerprintCore(core_config)
        
        logger.info("Fingerprinting pipeline created successfully")
        return fingerprint_core
        
    except Exception as e:
        logger.error("Error creating fingerprinting pipeline: %s", str(e))
        raise


def create_complete_system(config: dict = None, database_url: str = None) -> AudioFingerprintingService:
    """
    Create a complete fingerprinting system ready for production use.
    
    Args:
        config: Optional configuration dictionary
        database_url: Optional database connection URL
        
    Returns:
        Fully configured AudioFingerprintingService instance
    """
    try:
        # Create service with configuration
        service = create_service(database_url=database_url)
        
        # Apply custom configuration if provided
        if config and service.config_manager:
            for section, settings in config.items():
                for key, value in settings.items():
                    service.config_manager.update_runtime_setting(section, key, value)
        
        logger.info("Complete fingerprinting system created successfully")
        return service
        
    except Exception as e:
        logger.error("Error creating complete system: %s", str(e))
        raise


# Initialize module-level logger
logging.getLogger(__name__).addHandler(logging.NullHandler())

# Module initialization message
logger.info("Audio Fingerprinting System v%s initialized", __version__)
logger.info("Developed by %s", __author__)
logger.info("⚠️  Proprietary software - Unauthorized use prohibited")