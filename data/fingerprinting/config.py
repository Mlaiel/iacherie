"""IA Influencer Agent - Fingerprinting Configuration
================================================

Configuration management for the fingerprinting system with advanced optimization
and performance tuning capabilities for production environments.

Team Expertise: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + 
Microservices + Audio + DevOps + IA Prompt Engineer

Author: Fahed Mlaiel (mlaiel@live.de)
Email: mlaiel@live.de
Copyright: © 2025 Fahed Mlaiel - All Rights Reserved

⚠️  CRITICAL WARNING ⚠️
This code is PROPRIETARY and CONFIDENTIAL intellectual property.
Any unauthorized use, reproduction, distribution, or reverse engineering 
is STRICTLY PROHIBITED and will result in immediate legal action.

Unauthorized copying or theft of this concept, code, or methodology 
will be prosecuted to the FULL EXTENT OF THE LAW under German and 
International Copyright Laws.

For licensing inquiries, contact: mlaiel@live.de
"""
import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union
from enum import Enum
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class PerformanceProfile(Enum):
    """Performance optimization profiles"""    ULTRA_FAST = "ultra_fast"
    FAST = "fast"
    BALANCED = "balanced"
    QUALITY = "quality"
    ULTRA_QUALITY = "ultra_quality"

class ProcessingMode(Enum):
    """Processing mode configurations"""    SINGLE_THREADED = "single_threaded"
    MULTI_THREADED = "multi_threaded"
    GPU_ACCELERATED = "gpu_accelerated"
    DISTRIBUTED = "distributed"
    HYBRID = "hybrid"

@dataclass
class AudioFingerprintConfig:
    """Configuration for audio fingerprinting"""    # Core parameters
    sample_rate: int = 22050
    hop_length: int = 512
    n_fft: int = 2048
    n_mels: int = 128
    
    # Chromagram parameters
    n_chroma: int = 12
    chroma_stft_params: Dict[str, Any] = field(default_factory=lambda: {
        'hop_length': 512,
        'norm': 'inf',
        'threshold': 0.0
    })
    
    # Peak finding parameters
    peak_neighborhood_size: int = 20
    peak_min_distance: int = 10
    peak_threshold: float = 0.1
    
    # Hash generation
    hash_time_delta: float = 2.0
    hash_freq_bits: int = 10
    hash_time_bits: int = 6
    fingerprint_density: float = 0.1
    
    # Matching parameters
    match_threshold: float = 0.85
    min_match_count: int = 5
    time_tolerance: float = 2.0
    
    # Performance settings
    chunk_size: int = 1024 * 1024  # 1MB chunks
    max_workers: int = 4
    cache_size: int = 1000
    enable_gpu: bool = False

@dataclass
class VideoFingerprintConfig:
    """Configuration for video fingerprinting"""    # Frame extraction
    fps: Optional[float] = 1.0  # Extract 1 frame per second
    max_frames: int = 300
    frame_width: int = 128
    frame_height: int = 128
    
    # Visual features
    hist_bins: int = 256
    orb_features: int = 500
    sift_features: int = 1000
    
    # Temporal analysis
    motion_threshold: float = 0.1
    scene_change_threshold: float = 0.3
    temporal_window: int = 30
    
    # Deep learning features
    cnn_model: str = "resnet50"
    feature_layer: str = "avg_pool"
    batch_size: int = 32
    
    # Color analysis
    color_channels: List[str] = field(default_factory=lambda: ["HSV", "LAB", "RGB"])
    dominant_colors: int = 16
    
    # Matching parameters
    similarity_threshold: float = 0.75
    temporal_alignment_tolerance: float = 5.0
    min_sequence_length: int = 3
    
    # Performance
    gpu_memory_fraction: float = 0.7
    num_workers: int = 2
    prefetch_factor: int = 2

@dataclass
class ImageFingerprintConfig:
    """Configuration for image fingerprinting"""    # Hash types and sizes
    hash_size: int = 16
    dhash_size: int = 16
    phash_size: int = 32
    whash_size: int = 16
    
    # Feature extraction
    sift_features: int = 1000
    orb_features: int = 500
    akaze_features: int = 1000
    
    # Color analysis
    hist_bins: int = 256
    dominant_colors: int = 16
    color_spaces: List[str] = field(default_factory=lambda: ["RGB", "HSV", "LAB"])
    
    # Deep learning
    cnn_models: List[str] = field(default_factory=lambda: ["vgg16", "resnet50", "efficientnet"])
    feature_layers: Dict[str, str] = field(default_factory=lambda: {
        "vgg16": "fc2",
        "resnet50": "avg_pool",
        "efficientnet": "global_average_pooling2d"
    })
    
    # Image preprocessing
    resize_dimensions: tuple = (224, 224)
    normalize_mean: List[float] = field(default_factory=lambda: [0.485, 0.456, 0.406])
    normalize_std: List[float] = field(default_factory=lambda: [0.229, 0.224, 0.225])
    
    # Matching parameters
    hamming_threshold: int = 10
    feature_match_ratio: float = 0.7
    ransac_threshold: float = 5.0
    min_match_count: int = 10
    
    # Performance
    batch_processing: bool = True
    batch_size: int = 32
    enable_cuda: bool = False

@dataclass
class TextFingerprintConfig:
    """Configuration for text fingerprinting"""    # Language processing
    languages: List[str] = field(default_factory=lambda: ["en", "de", "fr", "es", "it"])
    max_text_length: int = 1000000  # 1M characters
    min_text_length: int = 50
    
    # N-gram analysis
    ngram_ranges: List[tuple] = field(default_factory=lambda: [(1, 1), (2, 2), (3, 3), (1, 2), (2, 3)])
    shingle_size: int = 5
    min_hash_size: int = 128
    
    # Embedding models
    embedding_models: Dict[str, str] = field(default_factory=lambda: {
        "sentence_transformer": "all-MiniLM-L6-v2",
        "bert": "bert-base-uncased",
        "distilbert": "distilbert-base-uncased"
    })
    
    # Feature extraction
    max_features: int = 10000
    tfidf_max_df: float = 0.95
    tfidf_min_df: int = 2
    
    # Stylometric features
    enable_stylometry: bool = True
    stylometric_features: List[str] = field(default_factory=lambda: [
        "avg_sentence_length", "avg_word_length", "punctuation_ratio",
        "uppercase_ratio", "digit_ratio", "stopword_ratio"
    ])
    
    # Similarity thresholds
    cosine_threshold: float = 0.8
    jaccard_threshold: float = 0.7
    edit_distance_threshold: float = 0.2
    
    # Performance
    chunk_size: int = 1000
    parallel_processing: bool = True
    cache_embeddings: bool = True

@dataclass
class VectorMatcherConfig:
    """Configuration for vector matching operations"""    # FAISS parameters
    index_type: str = "IVF"
    nlist: int = 100
    nprobe: int = 10
    dimension: int = 512
    
    # Search parameters
    k_neighbors: int = 10
    search_threshold: float = 0.8
    batch_search_size: int = 1000
    
    # Index optimization
    training_sample_size: int = 10000
    use_gpu: bool = False
    gpu_ids: List[int] = field(default_factory=list)
    
    # Memory management
    max_memory_usage: int = 8 * 1024 * 1024 * 1024  # 8GB
    index_cache_size: int = 100
    
    # Persistence
    auto_save_interval: int = 1000  # Save every 1000 additions
    backup_enabled: bool = True
    compression_enabled: bool = True

@dataclass
class FingerprintingSystemConfig:
    """Master configuration for the fingerprinting system"""    # Component configurations
    audio: AudioFingerprintConfig = field(default_factory=AudioFingerprintConfig)
    video: VideoFingerprintConfig = field(default_factory=VideoFingerprintConfig)
    image: ImageFingerprintConfig = field(default_factory=ImageFingerprintConfig)
    text: TextFingerprintConfig = field(default_factory=TextFingerprintConfig)
    vector_matcher: VectorMatcherConfig = field(default_factory=VectorMatcherConfig)
    
    # System-wide settings
    performance_profile: PerformanceProfile = PerformanceProfile.BALANCED
    processing_mode: ProcessingMode = ProcessingMode.MULTI_THREADED
    
    # Storage and caching
    storage_path: str = "/tmp/fingerprinting"
    cache_enabled: bool = True
    cache_ttl: int = 3600  # 1 hour
    
    # Logging and monitoring
    log_level: str = "INFO"
    enable_metrics: bool = True
    metrics_interval: int = 60  # seconds
    
    # Security
    enable_encryption: bool = True
    encryption_key_path: Optional[str] = None
    
    # Resource limits
    max_concurrent_jobs: int = 10
    memory_limit: int = 16 * 1024 * 1024 * 1024  # 16GB
    disk_space_limit: int = 100 * 1024 * 1024 * 1024  # 100GB

class ConfigManager:
    """Advanced configuration manager with environment-specific settings"""    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or os.getenv("FINGERPRINTING_CONFIG_PATH")
        self._config_cache: Dict[str, Any] = {}
        self.logger = logging.getLogger(__name__)
    
    def load_config(self, environment: str = "production") -> FingerprintingSystemConfig:
        """Load configuration for specific environment"""        try:
            if environment in self._config_cache:
                return self._config_cache[environment]
            
            config = self._create_environment_config(environment)
            self._apply_environment_overrides(config, environment)
            self._validate_config(config)
            
            self._config_cache[environment] = config
            self.logger.info(f"Configuration loaded for environment: {environment}")
            
            return config
            
        except Exception as e:
            self.logger.error(f"Failed to load configuration: {e}")
            return self._get_default_config()
    
    def _create_environment_config(self, environment: str) -> FingerprintingSystemConfig:
        """Create environment-specific configuration"""        base_config = FingerprintingSystemConfig()
        
        if environment == "development":
            # Development optimizations
            base_config.performance_profile = PerformanceProfile.FAST
            base_config.audio.cache_size = 100
            base_config.video.max_frames = 50
            base_config.image.batch_size = 8
            base_config.log_level = "DEBUG"
            base_config.max_concurrent_jobs = 2
            
        elif environment == "testing":
            # Testing optimizations
            base_config.performance_profile = PerformanceProfile.ULTRA_FAST
            base_config.audio.chunk_size = 512 * 512
            base_config.video.fps = 0.5
            base_config.text.max_text_length = 10000
            base_config.enable_metrics = False
            
        elif environment == "staging":
            # Staging environment (similar to production but with monitoring)
            base_config.performance_profile = PerformanceProfile.QUALITY
            base_config.processing_mode = ProcessingMode.MULTI_THREADED
            base_config.log_level = "INFO"
            base_config.enable_metrics = True
            
        elif environment == "production":
            # Production optimizations
            base_config.performance_profile = PerformanceProfile.ULTRA_QUALITY
            base_config.processing_mode = ProcessingMode.GPU_ACCELERATED
            base_config.audio.enable_gpu = True
            base_config.video.gpu_memory_fraction = 0.8
            base_config.image.enable_cuda = True
            base_config.vector_matcher.use_gpu = True
            base_config.enable_encryption = True
            
        return base_config
    
    def _apply_environment_overrides(self, config: FingerprintingSystemConfig, environment: str):
        """Apply environment variable overrides"""        # System-level overrides
        if os.getenv("FINGERPRINTING_PERFORMANCE_PROFILE"):
            config.performance_profile = PerformanceProfile(
                os.getenv("FINGERPRINTING_PERFORMANCE_PROFILE")
            )
        
        if os.getenv("FINGERPRINTING_PROCESSING_MODE"):
            config.processing_mode = ProcessingMode(
                os.getenv("FINGERPRINTING_PROCESSING_MODE")
            )
        
        # Audio overrides
        if os.getenv("AUDIO_SAMPLE_RATE"):
            config.audio.sample_rate = int(os.getenv("AUDIO_SAMPLE_RATE"))
        
        if os.getenv("AUDIO_ENABLE_GPU"):
            config.audio.enable_gpu = os.getenv("AUDIO_ENABLE_GPU").lower() == "true"
        
        # Video overrides
        if os.getenv("VIDEO_FPS"):
            config.video.fps = float(os.getenv("VIDEO_FPS"))
        
        if os.getenv("VIDEO_MAX_FRAMES"):
            config.video.max_frames = int(os.getenv("VIDEO_MAX_FRAMES"))
        
        # Storage overrides
        if os.getenv("FINGERPRINTING_STORAGE_PATH"):
            config.storage_path = os.getenv("FINGERPRINTING_STORAGE_PATH")
        
        # Resource limits
        if os.getenv("FINGERPRINTING_MEMORY_LIMIT"):
            config.memory_limit = int(os.getenv("FINGERPRINTING_MEMORY_LIMIT"))
    
    def _validate_config(self, config: FingerprintingSystemConfig):
        """Validate configuration parameters"""        # Validate storage path
        storage_path = Path(config.storage_path)
        if not storage_path.exists():
            storage_path.mkdir(parents=True, exist_ok=True)
            self.logger.info(f"Created storage directory: {storage_path}")
        
        # Validate resource limits
        if config.memory_limit < 1024 * 1024 * 1024:  # 1GB minimum
            raise ValueError("Memory limit must be at least 1GB")
        
        # Validate audio configuration
        if config.audio.sample_rate <= 0:
            raise ValueError("Audio sample rate must be positive")
        
        # Validate video configuration
        if config.video.fps and config.video.fps <= 0:
            raise ValueError("Video FPS must be positive")
        
        # Validate performance profile compatibility
        if (config.performance_profile == PerformanceProfile.ULTRA_QUALITY and 
            config.processing_mode == ProcessingMode.ULTRA_FAST):
            self.logger.warning(
                "Performance profile and processing mode may be incompatible"
            )
    
    def _get_default_config(self) -> FingerprintingSystemConfig:
        """Get failsafe default configuration"""        return FingerprintingSystemConfig()
    
    def optimize_for_hardware(self, config: FingerprintingSystemConfig) -> FingerprintingSystemConfig:
        """Optimize configuration based on available hardware"""        try:
            import psutil
            import torch
            
            # CPU optimization
            cpu_count = psutil.cpu_count(logical=True)
            config.audio.max_workers = min(cpu_count - 1, 8)
            config.video.num_workers = min(cpu_count // 2, 4)
            config.max_concurrent_jobs = min(cpu_count, 16)
            
            # Memory optimization
            available_memory = psutil.virtual_memory().available
            config.memory_limit = min(config.memory_limit, int(available_memory * 0.8))
            
            # GPU optimization
            if torch.cuda.is_available():
                gpu_count = torch.cuda.device_count()
                if gpu_count > 0:
                    config.audio.enable_gpu = True
                    config.image.enable_cuda = True
                    config.vector_matcher.use_gpu = True
                    config.vector_matcher.gpu_ids = list(range(gpu_count))
                    
                    # Adjust memory fractions based on GPU memory
                    for i in range(gpu_count):
                        gpu_memory = torch.cuda.get_device_properties(i).total_memory
                        if gpu_memory > 8 * 1024 * 1024 * 1024:  # 8GB+
                            config.video.gpu_memory_fraction = 0.8
                        else:
                            config.video.gpu_memory_fraction = 0.6
            
            self.logger.info(f"Configuration optimized for hardware: {cpu_count} CPUs, "
                           f"{available_memory // (1024**3)}GB RAM, "
                           f"{torch.cuda.device_count() if torch.cuda.is_available() else 0} GPUs")
            
        except ImportError:
            self.logger.warning("Hardware optimization libraries not available")
        except Exception as e:
            self.logger.error(f"Hardware optimization failed: {e}")
        
        return config
    
    def export_config(self, config: FingerprintingSystemConfig, path: str):
        """Export configuration to file"""        try:
            import json
            from dataclasses import asdict
            
            config_dict = asdict(config)
            with open(path, 'w') as f:
                json.dump(config_dict, f, indent=2, default=str)
            
            self.logger.info(f"Configuration exported to: {path}")
            
        except Exception as e:
            self.logger.error(f"Failed to export configuration: {e}")

# Global configuration instance
config_manager = ConfigManager()

def get_config(environment: str = "production") -> FingerprintingSystemConfig:
    """Get optimized configuration for the current environment"""    config = config_manager.load_config(environment)
    return config_manager.optimize_for_hardware(config)

def reset_config_cache():
    """Reset the configuration cache"""    config_manager._config_cache.clear()
