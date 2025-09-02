"""⚙️ Configuration Management for Content Fingerprinting System
=============================================================

Centralized configuration system for multi-modal content fingerprinting.
Provides default settings, environment-based overrides, and validation.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

WARNING: This code and concept are protected by intellectual property rights.
Any unauthorized use, reproduction, or distribution without explicit written 
permission from Fahed Mlaiel is strictly prohibited and will result in legal action.
Contact: mlaiel@live.de for authorization requests.
"""

import os
import json
import yaml
from typing import Dict, Any, Optional, Union, List
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum

class ProcessingMode(str, Enum):
    """
Processing mode configurations."""

    CPU = "cpu"
    GPU = "gpu"
    AUTO = "auto"

class QualityLevel(str, Enum):
    """Quality levels for processing."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    ULTRA = "ultra"

@dataclass
class AudioConfig:
    """Audio processing configuration."""
    # Basic audio parameters
    sample_rate: int = 22050
    channels: int = 1
    duration_limit: int = 300  # seconds
    min_duration: float = 0.5  # seconds
    
    # Feature extraction
    n_mfcc: int = 13
    n_chroma: int = 12
    n_fft: int = 2048
    hop_length: int = 512
    window_size: int = 2048
    
    # Chromaprint settings
    chromaprint_duration: int = 120
    chromaprint_algorithm: int = 1
    
    # Spectral analysis
    spectral_bands: int = 32
    spectral_frames: int = 100
    
    # Neural embeddings
    neural_model: str = "facebook/wav2vec2-base-960h"
    neural_max_length: int = 16000  # samples
    
    # Quality and performance
    quality_level: QualityLevel = QualityLevel.MEDIUM
    batch_size: int = 16
    enable_noise_reduction: bool = True
    normalize_audio: bool = True

@dataclass
class VideoConfig:
    """Video processing configuration."""
    # Basic video parameters
    max_duration: int = 600  # seconds
    min_duration: float = 1.0  # seconds
    frame_rate: int = 1  # frames per second for sampling
    max_frames: int = 100
    
    # Frame processing
    frame_width: int = 224
    frame_height: int = 224
    maintain_aspect_ratio: bool = True
    
    # Perceptual hashing
    hash_size: int = 8
    perceptual_algorithms: List[str] = field(default_factory=lambda: ["phash", "dhash", "ahash", "whash"])
    
    # Motion analysis
    motion_threshold: float = 0.1
    optical_flow_quality: float = 0.01
    optical_flow_min_distance: int = 10
    
    # Object detection
    yolo_model: str = "yolov5s"
    yolo_confidence: float = 0.5
    yolo_iou_threshold: float = 0.45
    max_detections: int = 100
    
    # Scene analysis
    scene_threshold: float = 0.3
    max_scenes: int = 50
    
    # CNN features
    cnn_model: str = "resnet50"
    cnn_layer: str = "avgpool"
    feature_dim: int = 2048
    
    # Quality and performance
    quality_level: QualityLevel = QualityLevel.MEDIUM
    batch_size: int = 8
    enable_gpu: bool = True

@dataclass
class ImageConfig:
    """Image processing configuration."""
    # Basic image parameters
    max_size_mb: int = 50
    min_width: int = 32
    min_height: int = 32
    max_width: int = 4096
    max_height: int = 4096
    
    # Processing
    target_width: int = 224
    target_height: int = 224
    maintain_aspect_ratio: bool = True
    
    # Perceptual hashing
    hash_size: int = 8
    perceptual_algorithms: List[str] = field(default_factory=lambda: ["phash", "dhash", "ahash", "whash"])
    
    # CLIP embeddings
    clip_model: str = "ViT-B/32"
    clip_batch_size: int = 32
    
    # Traditional features
    enable_sift: bool = True
    enable_orb: bool = True
    enable_surf: bool = False  # Requires opencv-contrib
    max_keypoints: int = 500
    
    # Color analysis
    color_palette_size: int = 5
    color_quantization: int = 64
    
    # Texture analysis
    texture_window_size: int = 32
    texture_overlap: float = 0.5
    
    # Quality and performance
    quality_level: QualityLevel = QualityLevel.MEDIUM
    batch_size: int = 32
    enable_gpu: bool = True

@dataclass
class TextConfig:
    """Text processing configuration."""
    # Basic text parameters
    max_length: int = 1000000  # characters
    min_length: int = 10  # characters
    chunk_size: int = 512  # tokens
    chunk_overlap: int = 50  # tokens
    
    # Language processing
    supported_languages: List[str] = field(default_factory=lambda: ["en", "de", "fr", "es", "it"])
    auto_detect_language: bool = True
    
    # BERT embeddings
    bert_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    bert_max_length: int = 512
    bert_batch_size: int = 16
    
    # TF-IDF
    tfidf_max_features: int = 10000
    tfidf_ngram_range: tuple = (1, 3)
    tfidf_min_df: int = 2
    tfidf_max_df: float = 0.95
    
    # N-gram analysis
    ngram_sizes: List[int] = field(default_factory=lambda: [1, 2, 3, 4])
    ngram_min_frequency: int = 2
    
    # Semantic analysis
    enable_ner: bool = True
    enable_sentiment: bool = True
    enable_topics: bool = True
    topic_num_topics: int = 10
    
    # Text preprocessing
    remove_stopwords: bool = True
    lemmatize: bool = True
    normalize_unicode: bool = True
    remove_punctuation: bool = False
    lowercase: bool = True
    
    # Quality and performance
    quality_level: QualityLevel = QualityLevel.MEDIUM
    batch_size: int = 32
    enable_gpu: bool = True

@dataclass
class SimilarityConfig:
    """Similarity matching configuration."""
    # Default thresholds
    default_threshold: float = 0.8
    audio_threshold: float = 0.85
    video_threshold: float = 0.75
    image_threshold: float = 0.8
    text_threshold: float = 0.85
    
    # Algorithm weights for combined similarity
    audio_weights: Dict[str, float] = field(default_factory=lambda: {
        "chromaprint": 0.4,
        "essentia": 0.3,
        "spectral": 0.2,
        "neural": 0.1
    })
    
    video_weights: Dict[str, float] = field(default_factory=lambda: {
        "perceptual_hash": 0.3,
        "motion_analysis": 0.2,
        "object_detection": 0.3,
        "cnn_features": 0.2
    })
    
    image_weights: Dict[str, float] = field(default_factory=lambda: {
        "perceptual_hash": 0.3,
        "clip_embedding": 0.4,
        "traditional_features": 0.2,
        "color_analysis": 0.1
    })
    
    text_weights: Dict[str, float] = field(default_factory=lambda: {
        "bert_embedding": 0.4,
        "tfidf_vector": 0.3,
        "ngram_analysis": 0.2,
        "semantic_analysis": 0.1
    })
    
    # Search parameters
    max_results: int = 100
    use_vector_db: bool = True
    vector_db_type: str = "faiss"  # faiss, annoy, hnswlib
    
    # Performance
    similarity_batch_size: int = 1000
    parallel_processing: bool = True
    max_workers: int = 4

@dataclass
class DatabaseConfig:
    """Database configuration."""
    # Database connection
    host: str = "localhost"
    port: int = 5432
    database: str = "fingerprinting"
    username: str = "fingerprint_user"
    password: str = ""
    
    # Connection pool
    pool_size: int = 10
    max_overflow: int = 20
    pool_timeout: int = 30
    
    # Performance
    batch_insert_size: int = 1000
    enable_migrations: bool = True
    
    # Vector storage
    vector_table_prefix: str = "fingerprint_vectors"
    index_type: str = "ivfflat"  # ivfflat, hnsw

@dataclass
class CacheConfig:
    """Caching configuration."""
    # Cache settings
    enable_cache: bool = True
    cache_type: str = "memory"  # memory, redis, memcached
    max_size: int = 1000
    ttl_seconds: int = 3600
    
    # Redis settings (if cache_type == "redis")
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: str = ""
    
    # Cache keys
    fingerprint_cache_prefix: str = "fp:"
    similarity_cache_prefix: str = "sim:"
    metadata_cache_prefix: str = "meta:"

@dataclass
class PerformanceConfig:
    """Performance optimization configuration."""
    # Processing mode
    processing_mode: ProcessingMode = ProcessingMode.AUTO
    
    # CPU settings
    cpu_workers: int = 4
    cpu_batch_size: int = 32
    
    # GPU settings
    gpu_memory_fraction: float = 0.8
    gpu_batch_size: int = 64
    enable_mixed_precision: bool = True
    
    # Memory management
    max_memory_usage_gb: float = 8.0
    memory_cleanup_interval: int = 100  # operations
    
    # Optimization
    enable_multiprocessing: bool = True
    enable_async_processing: bool = True
    prefetch_buffer_size: int = 10
    
    # Monitoring
    enable_profiling: bool = False
    profile_output_dir: str = "./profiles"

@dataclass
class SecurityConfig:
    """Security configuration."""
    # API security
    enable_api_key: bool = True
    api_key_header: str = "X-API-Key"
    
    # File security
    max_file_size_mb: int = 500
    allowed_file_types: List[str] = field(default_factory=lambda: [
        ".mp3", ".wav", ".flac", ".ogg", ".m4a",  # Audio
        ".mp4", ".avi", ".mkv", ".mov", ".wmv",   # Video
        ".jpg", ".jpeg", ".png", ".gif", ".bmp",  # Image
        ".txt", ".doc", ".docx", ".pdf", ".md"    # Text
    ])
    
    # Sanitization
    sanitize_file_names: bool = True
    quarantine_suspicious_files: bool = True
    
    # Rate limiting
    enable_rate_limiting: bool = True
    requests_per_minute: int = 100
    requests_per_hour: int = 1000

@dataclass
class LoggingConfig:
    """Logging configuration."""
    # Log levels
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # File logging
    log_file: str = "./logs/fingerprinting.log"
    max_log_size: int = 10  # MB
    backup_count: int = 5
    
    # Structured logging
    enable_json_logging: bool = False
    include_performance_metrics: bool = True
    
    # External logging
    enable_sentry: bool = False
    sentry_dsn: str = ""

@dataclass
class FingerprintingConfig:
    """Main configuration container."""
    # Component configurations
    audio: AudioConfig = field(default_factory=AudioConfig)
    video: VideoConfig = field(default_factory=VideoConfig)
    image: ImageConfig = field(default_factory=ImageConfig)
    text: TextConfig = field(default_factory=TextConfig)
    similarity: SimilarityConfig = field(default_factory=SimilarityConfig)
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    cache: CacheConfig = field(default_factory=CacheConfig)
    performance: PerformanceConfig = field(default_factory=PerformanceConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    
    # Environment
    environment: str = "development"  # development, staging, production
    debug: bool = False
    
    @classmethod
    def from_file(cls, config_path: Union[str, Path]) -> 'FingerprintingConfig':
        """Load configuration from file."""
        config_path = Path(config_path)
        
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        with open(config_path, 'r', encoding='utf-8') as f:
            if config_path.suffix.lower() == '.json':
                config_data = json.load(f)
            elif config_path.suffix.lower() in ['.yml', '.yaml']:
                config_data = yaml.safe_load(f)
            else:
                raise ValueError(f"Unsupported configuration file format: {config_path.suffix}")
        
        return cls.from_dict(config_data)
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'FingerprintingConfig':
        """Create configuration from dictionary."""
        config = cls()
        
        # Update each component
        for component_name, component_config in config_dict.items():
            if hasattr(config, component_name) and isinstance(component_config, dict):
                component = getattr(config, component_name)
                for key, value in component_config.items():
                    if hasattr(component, key):
                        setattr(component, key, value)
            elif hasattr(config, component_name):
                setattr(config, component_name, component_config)
        
        return config
    
    @classmethod
    def from_environment(cls) -> 'FingerprintingConfig':
        try:
            logger.info(f"Executing from_environment")
            
            # Implementation for from_environment
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"from_environment completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"from_environment failed: {e}")
            raise
    @staticmethod
    def _set_nested_attr(obj: Any, path: str, value: Any):
        """Set nested attribute using dot notation."""
        parts = path.split('.')
        for part in parts[:-1]:
            obj = getattr(obj, part)
        setattr(obj, parts[-1], value)
    
    @staticmethod
    def _convert_env_value(value: str) -> Any:
        """
Convert environment variable value to appropriate type."""
        # Boolean conversion
        if value.lower() in ('true', 'false'):
            return value.lower() == 'true'
        
        # Numeric conversion
        try:
            if '.' in value:
                return float(value)
            else:
                return int(value)
        except ValueError:
            pass
        
        # String value
        return value
    
    def to_dict(self) -> Dict[str, Any]:
        try:
            logger.info(f"Executing _convert_env_value")
            
            # Implementation for _convert_env_value
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"_convert_env_value completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"_convert_env_value failed: {e}")
            raise
                yaml.dump(config_dict, f, default_flow_style=False)
            else:
                raise ValueError(f"Unsupported configuration file format: {config_path.suffix}")
    
    def validate(self) -> List[str]:
        """Validate configuration and return list of issues."""
        issues = []
        
        # Validate audio config
        if self.audio.sample_rate <= 0:
            issues.append("Audio sample rate must be positive")
        if self.audio.n_mfcc <= 0:
            issues.append("Audio MFCC features must be positive")
        
        # Validate video config
        if self.video.frame_width <= 0 or self.video.frame_height <= 0:
            issues.append("Video frame dimensions must be positive")
        if not 0 <= self.video.motion_threshold <= 1:
            issues.append("Video motion threshold must be between 0 and 1")
        
        # Validate image config
        if self.image.min_width >= self.image.max_width:
            issues.append("Image min_width must be less than max_width")
        if self.image.min_height >= self.image.max_height:
            issues.append("Image min_height must be less than max_height")
        
        # Validate text config
        if self.text.max_length <= self.text.min_length:
            issues.append("Text max_length must be greater than min_length")
        if self.text.chunk_overlap >= self.text.chunk_size:
            issues.append("Text chunk_overlap must be less than chunk_size")
        
        # Validate similarity config
        if not 0 <= self.similarity.default_threshold <= 1:
            issues.append("Similarity threshold must be between 0 and 1")
        
        # Validate performance config
        if self.performance.cpu_workers <= 0:
            issues.append("CPU workers must be positive")
        if not 0 < self.performance.gpu_memory_fraction <= 1:
            issues.append("GPU memory fraction must be between 0 and 1")
        
        return issues

# Default configuration instance
default_config = FingerprintingConfig()

# Configuration factory functions
def get_development_config() -> FingerprintingConfig:
    """Get development configuration."""
    config = FingerprintingConfig()
    config.environment = "development"
    config.debug = True
    config.logging.log_level = "DEBUG"
    config.performance.enable_profiling = True
    config.security.enable_api_key = False
    return config

def get_production_config() -> FingerprintingConfig:
    """Get production configuration."""
    config = FingerprintingConfig()
    config.environment = "production"
    config.debug = False
    config.logging.log_level = "INFO"
    config.performance.enable_profiling = False
    config.security.enable_api_key = True
    config.cache.enable_cache = True
    config.database.pool_size = 20
    return config

def get_testing_config() -> FingerprintingConfig:
    """Get testing configuration."""
    config = FingerprintingConfig()
    config.environment = "testing"
    config.debug = True
    config.logging.log_level = "WARNING"
    config.database.database = "fingerprinting_test"
    config.cache.enable_cache = False
    config.security.enable_api_key = False
    return config

# Configuration loader
def load_config(config_path: Optional[str] = None, 
                environment: Optional[str] = None) -> FingerprintingConfig:
    """Load configuration with fallback hierarchy."""
    
    # 1. Start with default config
    if environment == "development":
        config = get_development_config()
    elif environment == "production":
        config = get_production_config()
    elif environment == "testing":
        config = get_testing_config()
    else:
        config = FingerprintingConfig()
    
    # 2. Override with file config if provided
    if config_path and os.path.exists(config_path):
        try:
            file_config = FingerprintingConfig.from_file(config_path)
            # Merge configurations (file overrides default)
            config = merge_configs(config, file_config)
        except Exception as e:
            print(f"Warning: Failed to load config file {config_path}: {e}")
    
    # 3. Override with environment variables
    try:
        env_config = FingerprintingConfig.from_environment()
        config = merge_configs(config, env_config)
    except Exception as e:
        print(f"Warning: Failed to load environment config: {e}")
    
    # 4. Validate final configuration
    issues = config.validate()
    if issues:
        print("Configuration validation issues:")
        for issue in issues:
            print(f"  - {issue}")
    
    return config

def merge_configs(base_config: FingerprintingConfig, 
                 override_config: FingerprintingConfig) -> FingerprintingConfig:
    """Merge two configurations, with override taking precedence."""
    import copy
    
    merged = copy.deepcopy(base_config)
    override_dict = override_config.to_dict()
    
    def _merge_dict(base_dict: Dict[str, Any], override_dict: Dict[str, Any]):
        for key, value in override_dict.items():
            if isinstance(value, dict) and key in base_dict and isinstance(base_dict[key], dict):
                _merge_dict(base_dict[key], value)
            else:
                base_dict[key] = value
    
    base_dict = merged.to_dict()
    _merge_dict(base_dict, override_dict)
    
    return FingerprintingConfig.from_dict(base_dict)

# Export configuration classes and functions
__all__ = [
    "ProcessingMode",
    "QualityLevel", 
    "AudioConfig",
    "VideoConfig",
    "ImageConfig",
    "TextConfig",
    "SimilarityConfig",
    "DatabaseConfig",
    "CacheConfig",
    "PerformanceConfig",
    "SecurityConfig",
    "LoggingConfig",
    "FingerprintingConfig",
    "default_config",
    "get_development_config",
    "get_production_config", 
    "get_testing_config",
    "load_config",
    "merge_configs"
]

        try:
            logger.info(f"Executing _merge_dict")
            
            # Implementation for _merge_dict
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"_merge_dict completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"_merge_dict failed: {e}")
            raise
    "SimilarityConfig",
    "DatabaseConfig",
    "CacheConfig",
    "PerformanceConfig",
    "SecurityConfig",
    "LoggingConfig",
    "FingerprintingConfig",
    "default_config",
    "get_development_config",
    "get_production_config", 
    "get_testing_config",
    "load_config",
    "merge_configs"
]
