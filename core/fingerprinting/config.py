"""IA Influencer Agent - Fingerprinting Module Configuration
Configuration settings and constants for the fingerprinting system

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved to Fahed Mlaiel
Warning: Unauthorized use, copying, or distribution of this code is strictly prohibited
"""
import os
from typing import Dict, List, Any, Optional
from pathlib import Path
from dataclasses import dataclass


@dataclass
class FingerprintingConfig:
    """Configuration class for fingerprinting operations"""    
    # File processing settings
    max_file_size: int = 500 * 1024 * 1024  # 500MB
    supported_audio_formats: List[str] = None
    supported_video_formats: List[str] = None
    supported_image_formats: List[str] = None
    
    # Processing timeouts (seconds)
    audio_processing_timeout: int = 300  # 5 minutes
    video_processing_timeout: int = 600  # 10 minutes
    image_processing_timeout: int = 120  # 2 minutes
    
    # Quality settings
    min_audio_duration: float = 1.0  # seconds
    max_audio_duration: float = 3600.0  # 1 hour
    min_video_duration: float = 1.0  # seconds
    max_video_duration: float = 7200.0  # 2 hours
    min_image_resolution: int = 64  # 64x64 pixels
    max_image_resolution: int = 8192  # 8K resolution
    
    # Fingerprinting algorithm settings
    audio_sample_rate: int = 22050
    audio_frame_size: int = 2048
    video_frame_rate: int = 1  # frames per second for analysis
    image_hash_size: int = 16  # for perceptual hashing
    
    # Security settings
    default_hash_algorithm: str = 'sha256'
    salt_length: int = 16  # bytes
    hmac_algorithm: str = 'sha256'
    
    # Similarity settings
    similarity_threshold: float = 0.8
    max_similarity_results: int = 100
    vector_dimension: int = 128
    
    # Performance settings
    batch_size: int = 10
    max_concurrent_processes: int = 4
    cache_size: int = 1000
    enable_gpu: bool = False
    
    # Storage settings
    temp_directory: Optional[str] = None
    cache_directory: Optional[str] = None
    results_directory: Optional[str] = None
    
    # Logging settings
    log_level: str = 'INFO'
    log_file: Optional[str] = None
    enable_debug: bool = False
    
    def __post_init__(self):
        """Initialize default values and validate configuration"""        if self.supported_audio_formats is None:
            self.supported_audio_formats = [
                '.mp3', '.wav', '.flac', '.m4a', '.ogg', '.aac', '.wma'
            ]
        
        if self.supported_video_formats is None:
            self.supported_video_formats = [
                '.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv', '.wmv', '.m4v'
            ]
        
        if self.supported_image_formats is None:
            self.supported_image_formats = [
                '.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp', '.gif'
            ]
        
        # Set default directories if not specified
        if self.temp_directory is None:
            self.temp_directory = os.path.join(os.getcwd(), 'temp', 'fingerprinting')
        
        if self.cache_directory is None:
            self.cache_directory = os.path.join(os.getcwd(), 'cache', 'fingerprinting')
        
        if self.results_directory is None:
            self.results_directory = os.path.join(os.getcwd(), 'results', 'fingerprinting')
        
        # Create directories if they don't exist
        for directory in [self.temp_directory, self.cache_directory, self.results_directory]:
            Path(directory).mkdir(parents=True, exist_ok=True)
        
        # Validate configuration
        self._validate_config()
    
    def _validate_config(self):
        """Validate configuration values"""        if self.max_file_size <= 0:
            raise ValueError("max_file_size must be positive")
        
        if self.similarity_threshold < 0 or self.similarity_threshold > 1:
            raise ValueError("similarity_threshold must be between 0 and 1")
        
        if self.batch_size <= 0:
            raise ValueError("batch_size must be positive")
        
        if self.max_concurrent_processes <= 0:
            raise ValueError("max_concurrent_processes must be positive")
        
        if self.vector_dimension <= 0:
            raise ValueError("vector_dimension must be positive")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""        return {
            'max_file_size': self.max_file_size,
            'supported_formats': {
                'audio': self.supported_audio_formats,
                'video': self.supported_video_formats,
                'image': self.supported_image_formats
            },
            'timeouts': {
                'audio': self.audio_processing_timeout,
                'video': self.video_processing_timeout,
                'image': self.image_processing_timeout
            },
            'quality_limits': {
                'min_audio_duration': self.min_audio_duration,
                'max_audio_duration': self.max_audio_duration,
                'min_video_duration': self.min_video_duration,
                'max_video_duration': self.max_video_duration,
                'min_image_resolution': self.min_image_resolution,
                'max_image_resolution': self.max_image_resolution
            },
            'algorithm_settings': {
                'audio_sample_rate': self.audio_sample_rate,
                'audio_frame_size': self.audio_frame_size,
                'video_frame_rate': self.video_frame_rate,
                'image_hash_size': self.image_hash_size
            },
            'security': {
                'default_hash_algorithm': self.default_hash_algorithm,
                'salt_length': self.salt_length,
                'hmac_algorithm': self.hmac_algorithm
            },
            'similarity': {
                'threshold': self.similarity_threshold,
                'max_results': self.max_similarity_results,
                'vector_dimension': self.vector_dimension
            },
            'performance': {
                'batch_size': self.batch_size,
                'max_concurrent_processes': self.max_concurrent_processes,
                'cache_size': self.cache_size,
                'enable_gpu': self.enable_gpu
            },
            'storage': {
                'temp_directory': self.temp_directory,
                'cache_directory': self.cache_directory,
                'results_directory': self.results_directory
            },
            'logging': {
                'log_level': self.log_level,
                'log_file': self.log_file,
                'enable_debug': self.enable_debug
            }
        }
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'FingerprintingConfig':
        """Create configuration from dictionary"""        return cls(
            max_file_size=config_dict.get('max_file_size', 500 * 1024 * 1024),
            supported_audio_formats=config_dict.get('supported_formats', {}).get('audio'),
            supported_video_formats=config_dict.get('supported_formats', {}).get('video'),
            supported_image_formats=config_dict.get('supported_formats', {}).get('image'),
            audio_processing_timeout=config_dict.get('timeouts', {}).get('audio', 300),
            video_processing_timeout=config_dict.get('timeouts', {}).get('video', 600),
            image_processing_timeout=config_dict.get('timeouts', {}).get('image', 120),
            min_audio_duration=config_dict.get('quality_limits', {}).get('min_audio_duration', 1.0),
            max_audio_duration=config_dict.get('quality_limits', {}).get('max_audio_duration', 3600.0),
            min_video_duration=config_dict.get('quality_limits', {}).get('min_video_duration', 1.0),
            max_video_duration=config_dict.get('quality_limits', {}).get('max_video_duration', 7200.0),
            min_image_resolution=config_dict.get('quality_limits', {}).get('min_image_resolution', 64),
            max_image_resolution=config_dict.get('quality_limits', {}).get('max_image_resolution', 8192),
            audio_sample_rate=config_dict.get('algorithm_settings', {}).get('audio_sample_rate', 22050),
            audio_frame_size=config_dict.get('algorithm_settings', {}).get('audio_frame_size', 2048),
            video_frame_rate=config_dict.get('algorithm_settings', {}).get('video_frame_rate', 1),
            image_hash_size=config_dict.get('algorithm_settings', {}).get('image_hash_size', 16),
            default_hash_algorithm=config_dict.get('security', {}).get('default_hash_algorithm', 'sha256'),
            salt_length=config_dict.get('security', {}).get('salt_length', 16),
            hmac_algorithm=config_dict.get('security', {}).get('hmac_algorithm', 'sha256'),
            similarity_threshold=config_dict.get('similarity', {}).get('threshold', 0.8),
            max_similarity_results=config_dict.get('similarity', {}).get('max_results', 100),
            vector_dimension=config_dict.get('similarity', {}).get('vector_dimension', 128),
            batch_size=config_dict.get('performance', {}).get('batch_size', 10),
            max_concurrent_processes=config_dict.get('performance', {}).get('max_concurrent_processes', 4),
            cache_size=config_dict.get('performance', {}).get('cache_size', 1000),
            enable_gpu=config_dict.get('performance', {}).get('enable_gpu', False),
            temp_directory=config_dict.get('storage', {}).get('temp_directory'),
            cache_directory=config_dict.get('storage', {}).get('cache_directory'),
            results_directory=config_dict.get('storage', {}).get('results_directory'),
            log_level=config_dict.get('logging', {}).get('log_level', 'INFO'),
            log_file=config_dict.get('logging', {}).get('log_file'),
            enable_debug=config_dict.get('logging', {}).get('enable_debug', False)
        )
    
    @classmethod
    def from_file(cls, config_path: str) -> 'FingerprintingConfig':
        """Load configuration from JSON file"""        import json
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config_dict = json.load(f)
        
        return cls.from_dict(config_dict)
    
    def save_to_file(self, config_path: str):
        """Save configuration to JSON file"""        import json
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)


# Default configuration instance
DEFAULT_CONFIG = FingerprintingConfig()

# Environment-based configuration
def get_config_from_environment() -> FingerprintingConfig:
    """Create configuration from environment variables"""    config = FingerprintingConfig()
    
    # Override with environment variables if they exist
    if 'FINGERPRINTING_MAX_FILE_SIZE' in os.environ:
        config.max_file_size = int(os.environ['FINGERPRINTING_MAX_FILE_SIZE'])
    
    if 'FINGERPRINTING_SIMILARITY_THRESHOLD' in os.environ:
        config.similarity_threshold = float(os.environ['FINGERPRINTING_SIMILARITY_THRESHOLD'])
    
    if 'FINGERPRINTING_BATCH_SIZE' in os.environ:
        config.batch_size = int(os.environ['FINGERPRINTING_BATCH_SIZE'])
    
    if 'FINGERPRINTING_MAX_CONCURRENT' in os.environ:
        config.max_concurrent_processes = int(os.environ['FINGERPRINTING_MAX_CONCURRENT'])
    
    if 'FINGERPRINTING_ENABLE_GPU' in os.environ:
        config.enable_gpu = os.environ['FINGERPRINTING_ENABLE_GPU'].lower() in ('true', '1', 'yes')
    
    if 'FINGERPRINTING_LOG_LEVEL' in os.environ:
        config.log_level = os.environ['FINGERPRINTING_LOG_LEVEL']
    
    if 'FINGERPRINTING_TEMP_DIR' in os.environ:
        config.temp_directory = os.environ['FINGERPRINTING_TEMP_DIR']
    
    if 'FINGERPRINTING_CACHE_DIR' in os.environ:
        config.cache_directory = os.environ['FINGERPRINTING_CACHE_DIR']
    
    if 'FINGERPRINTING_RESULTS_DIR' in os.environ:
        config.results_directory = os.environ['FINGERPRINTING_RESULTS_DIR']
    
    return config


# Production-optimized configuration
PRODUCTION_CONFIG = FingerprintingConfig(
    max_file_size=1024 * 1024 * 1024,  # 1GB
    batch_size=20,
    max_concurrent_processes=8,
    cache_size=5000,
    enable_gpu=True,
    log_level='WARNING',
    enable_debug=False
)

# Development configuration
DEVELOPMENT_CONFIG = FingerprintingConfig(
    max_file_size=100 * 1024 * 1024,  # 100MB
    batch_size=5,
    max_concurrent_processes=2,
    cache_size=100,
    enable_gpu=False,
    log_level='DEBUG',
    enable_debug=True
)

# Testing configuration
TESTING_CONFIG = FingerprintingConfig(
    max_file_size=10 * 1024 * 1024,  # 10MB
    batch_size=2,
    max_concurrent_processes=1,
    cache_size=10,
    enable_gpu=False,
    log_level='DEBUG',
    enable_debug=True,
    audio_processing_timeout=30,
    video_processing_timeout=60,
    image_processing_timeout=30
)


# Configuration constants
class FingerprintingConstants:
    """Constants for fingerprinting operations"""    
    # File format MIME types
    AUDIO_MIME_TYPES = {
        '.mp3': 'audio/mpeg',
        '.wav': 'audio/wav',
        '.flac': 'audio/flac',
        '.m4a': 'audio/mp4',
        '.ogg': 'audio/ogg',
        '.aac': 'audio/aac'
    }
    
    VIDEO_MIME_TYPES = {
        '.mp4': 'video/mp4',
        '.avi': 'video/x-msvideo',
        '.mov': 'video/quicktime',
        '.mkv': 'video/x-matroska',
        '.webm': 'video/webm',
        '.flv': 'video/x-flv'
    }
    
    IMAGE_MIME_TYPES = {
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png',
        '.bmp': 'image/bmp',
        '.tiff': 'image/tiff',
        '.webp': 'image/webp',
        '.gif': 'image/gif'
    }
    
    # Algorithm names
    AUDIO_ALGORITHMS = ['chromaprint', 'spectral_hash', 'mfcc', 'tempo_rhythm']
    VIDEO_ALGORITHMS = ['perceptual_hash', 'histogram', 'optical_flow', 'edge_detection']
    IMAGE_ALGORITHMS = ['perceptual_hash', 'histogram', 'sift_features', 'texture_analysis']
    
    # Hash algorithms
    HASH_ALGORITHMS = ['sha256', 'sha3_256', 'blake2b', 'md5', 'sha1']
    SECURE_HASH_ALGORITHMS = ['sha256', 'sha3_256', 'blake2b']
    
    # Quality thresholds
    MIN_QUALITY_SCORE = 0.3
    GOOD_QUALITY_SCORE = 0.7
    EXCELLENT_QUALITY_SCORE = 0.9
    
    # Similarity thresholds
    LOW_SIMILARITY = 0.3
    MEDIUM_SIMILARITY = 0.6
    HIGH_SIMILARITY = 0.8
    VERY_HIGH_SIMILARITY = 0.95
    
    # Processing limits
    MAX_AUDIO_CHANNELS = 8
    MAX_VIDEO_TRACKS = 4
    MAX_IMAGE_LAYERS = 10
    
    # Memory limits (bytes)
    MAX_MEMORY_PER_PROCESS = 2 * 1024 * 1024 * 1024  # 2GB
    MAX_TOTAL_MEMORY = 8 * 1024 * 1024 * 1024  # 8GB


def get_current_config() -> FingerprintingConfig:
    """Get configuration based on current environment"""    env = os.environ.get('FINGERPRINTING_ENV', 'development').lower()
    
    if env == 'production':
        return PRODUCTION_CONFIG
    elif env == 'testing':
        return TESTING_CONFIG
    elif env == 'development':
        return DEVELOPMENT_CONFIG
    else:
        return get_config_from_environment()


# Export everything
__all__ = [
    'FingerprintingConfig',
    'FingerprintingConstants',
    'DEFAULT_CONFIG',
    'PRODUCTION_CONFIG',
    'DEVELOPMENT_CONFIG',
    'TESTING_CONFIG',
    'get_config_from_environment',
    'get_current_config'
]
