"""
Content Detection Configuration Module
=====================================

Professional content detection configuration for AI-powered content analysis.
Supports real-time detection, classification, and content understanding.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA-Influencer Agent + Content Protection Platform
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps

  COPYRIGHT WARNING:
This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, modification, or distribution of this code
without explicit written permission from Fahed Mlaiel (mlaiel@live.de) is strictly prohibited.
Violators will be prosecuted to the full extent of the law.
"""

from typing import Dict, Any, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
import os


class DetectionMode(str, Enum):
    """Detection operation modes."""
    REALTIME = "realtime"
    BATCH = "batch"
    HYBRID = "hybrid"


class DetectionLevel(str, Enum):
    """Detection sensitivity levels."""
    LOW = "low"          # Basic detection, high performance
    MEDIUM = "medium"    # Balanced detection and performance
    HIGH = "high"        # Maximum detection accuracy
    ULTRA = "ultra"      # Enterprise-grade detection


class ContentCategory(str, Enum):
    """Content categories for detection."""
    MUSIC = "music"
    PODCAST = "podcast"
    VOICE = "voice"
    VIDEO = "video"
    MOVIE = "movie"
    SERIES = "series"
    IMAGE = "image"
    PHOTO = "photo"
    ARTWORK = "artwork"
    TEXT = "text"
    DOCUMENT = "document"
    SOCIAL_MEDIA = "social_media"


class DetectionEngine(str, Enum):
    """Available detection engines."""
    # Audio detection engines
    CHROMAPRINT = "chromaprint"
    ESSENTIA = "essentia"
    LIBROSA = "librosa"
    SPOTIFY_WEB_API = "spotify_web_api"
    
    # Video detection engines
    OPENCV = "opencv"
    YOLO = "yolo"
    DETECTRON2 = "detectron2"
    MEDIAPIPE = "mediapipe"
    
    # Image detection engines
    CLIP = "clip"
    RESNET = "resnet"
    EFFICIENTNET = "efficientnet"
    VIT = "vit"
    
    # Text detection engines
    BERT = "bert"
    ROBERTA = "roberta"
    GPT = "gpt"
    SPACY = "spacy"


@dataclass
class AudioDetectionConfig:
    """Audio content detection configuration."""
    engines: List[DetectionEngine] = field(default_factory=lambda: [
        DetectionEngine.CHROMAPRINT, DetectionEngine.ESSENTIA
    ])
    sample_rate: int = 22050
    chunk_duration: float = 10.0  # seconds
    overlap_duration: float = 2.0  # seconds
    min_confidence: float = 0.85
    enable_genre_detection: bool = True
    enable_mood_detection: bool = True
    enable_tempo_detection: bool = True
    enable_key_detection: bool = True
    enable_instrument_detection: bool = True
    enable_voice_activity_detection: bool = True
    spectral_features: List[str] = field(default_factory=lambda: [
        "mfcc", "chroma", "spectral_centroid", "zero_crossing_rate"
    ])
    noise_reduction: bool = True
    normalization: bool = True


@dataclass
class VideoDetectionConfig:
    """Video content detection configuration."""
    engines: List[DetectionEngine] = field(default_factory=lambda: [
        DetectionEngine.OPENCV, DetectionEngine.YOLO
    ])
    frame_sample_rate: int = 1  # frames per second
    resolution_threshold: Tuple[int, int] = (480, 360)  # min resolution
    quality_threshold: float = 0.7
    min_confidence: float = 0.80
    enable_object_detection: bool = True
    enable_face_detection: bool = True
    enable_scene_detection: bool = True
    enable_action_recognition: bool = True
    enable_ocr: bool = True
    enable_logo_detection: bool = True
    motion_detection_sensitivity: float = 0.5
    keyframe_extraction: bool = True
    thumbnail_generation: bool = True


@dataclass
class ImageDetectionConfig:
    """Image content detection configuration."""
    engines: List[DetectionEngine] = field(default_factory=lambda: [
        DetectionEngine.CLIP, DetectionEngine.RESNET
    ])
    min_resolution: Tuple[int, int] = (224, 224)
    max_file_size_mb: int = 50
    min_confidence: float = 0.88
    enable_object_detection: bool = True
    enable_face_recognition: bool = True
    enable_text_extraction: bool = True
    enable_nsfw_detection: bool = True
    enable_brand_detection: bool = True
    enable_color_analysis: bool = True
    enable_composition_analysis: bool = True
    supported_formats: Set[str] = field(default_factory=lambda: {
        "jpg", "jpeg", "png", "webp", "gif", "bmp", "tiff"
    })


@dataclass
class TextDetectionConfig:
    """Text content detection configuration."""
    engines: List[DetectionEngine] = field(default_factory=lambda: [
        DetectionEngine.BERT, DetectionEngine.ROBERTA
    ])
    max_sequence_length: int = 512
    min_text_length: int = 10
    min_confidence: float = 0.85
    enable_language_detection: bool = True
    enable_sentiment_analysis: bool = True
    enable_topic_classification: bool = True
    enable_named_entity_recognition: bool = True
    enable_plagiarism_detection: bool = True
    enable_toxicity_detection: bool = True
    enable_copyright_detection: bool = True
    supported_languages: List[str] = field(default_factory=lambda: [
        "en", "de", "fr", "es", "it", "pt", "nl", "ru", "ja", "ko", "zh"
    ])


@dataclass
class RealTimeConfig:
    """Real-time detection configuration."""
    enable_streaming: bool = True
    buffer_size_seconds: float = 30.0
    processing_interval_ms: int = 1000
    max_concurrent_streams: int = 100
    enable_adaptive_quality: bool = True
    latency_threshold_ms: int = 500
    enable_edge_processing: bool = False
    websocket_enabled: bool = True


@dataclass
class BatchConfig:
    """Batch processing configuration."""
    batch_size: int = 32
    max_batch_duration_minutes: int = 60
    enable_parallel_processing: bool = True
    max_workers: int = 8
    queue_priority_enabled: bool = True
    enable_checkpointing: bool = True
    retry_failed_items: bool = True
    progress_reporting_interval: int = 100


@dataclass
class MachineLearningConfig:
    """Machine learning models configuration."""
    model_precision: str = "fp16"  # fp32, fp16, int8
    enable_gpu_acceleration: bool = True
    model_caching: bool = True
    cache_size_gb: int = 2
    enable_model_ensemble: bool = True
    ensemble_voting: str = "soft"  # soft, hard
    enable_uncertainty_estimation: bool = True
    calibration_enabled: bool = True
    model_versioning: bool = True


@dataclass
class QualityAssuranceConfig:
    """Quality assurance and validation configuration."""
    enable_content_validation: bool = True
    enable_metadata_extraction: bool = True
    enable_duplicate_detection: bool = True
    similarity_threshold: float = 0.95
    enable_quality_scoring: bool = True
    min_quality_score: float = 0.7
    enable_content_classification: bool = True
    enable_anomaly_detection: bool = True
    validation_rules: List[str] = field(default_factory=lambda: [
        "file_integrity", "format_compliance", "content_completeness"
    ])


@dataclass
class OutputConfig:
    """Detection output configuration."""
    output_format: str = "json"  # json, xml, csv
    include_confidence_scores: bool = True
    include_metadata: bool = True
    include_thumbnails: bool = True
    include_embeddings: bool = False
    compression_enabled: bool = True
    encryption_enabled: bool = True
    versioning_enabled: bool = True
    retention_days: int = 365


class ContentDetectionConfig:
    """
    Professional content detection configuration manager.
    Provides industrial-grade configuration for AI-powered content analysis.
    """
    
    def __init__(self):
        # General detection settings
        self.detection_mode = DetectionMode.HYBRID
        self.detection_level = DetectionLevel.HIGH
        self.enable_multi_engine_fusion: bool = True
        self.confidence_fusion_method: str = "weighted_average"
        self.enable_cross_validation: bool = True
        
        # Content type configurations
        self.audio = AudioDetectionConfig()
        self.video = VideoDetectionConfig()
        self.image = ImageDetectionConfig()
        self.text = TextDetectionConfig()
        
        # Processing configurations
        self.realtime = RealTimeConfig()
        self.batch = BatchConfig()
        self.ml_config = MachineLearningConfig()
        self.quality_assurance = QualityAssuranceConfig()
        self.output = OutputConfig()
        
        # Performance settings
        self.max_concurrent_detections = 50
        self.timeout_seconds = 300
        self.memory_limit_gb = 8
        self.enable_performance_monitoring = True
        
        # Load environment configurations
        self._load_from_environment()
    
    def _load_from_environment(self) -> None:
        """Load configuration from environment variables."""
        # General settings
        detection_mode = os.getenv("DETECTION_MODE", "hybrid")
        self.detection_mode = DetectionMode(detection_mode)
        
        detection_level = os.getenv("DETECTION_LEVEL", "high")
        self.detection_level = DetectionLevel(detection_level)
        
        # Performance settings
        self.max_concurrent_detections = int(os.getenv("DETECTION_MAX_CONCURRENT", "50"))
        self.timeout_seconds = int(os.getenv("DETECTION_TIMEOUT", "300"))
        self.memory_limit_gb = int(os.getenv("DETECTION_MEMORY_LIMIT", "8"))
        
        # Audio settings
        self.audio.min_confidence = float(os.getenv("DETECTION_AUDIO_CONFIDENCE", "0.85"))
        self.audio.sample_rate = int(os.getenv("DETECTION_AUDIO_SAMPLE_RATE", "22050"))
        
        # Video settings
        self.video.min_confidence = float(os.getenv("DETECTION_VIDEO_CONFIDENCE", "0.80"))
        self.video.quality_threshold = float(os.getenv("DETECTION_VIDEO_QUALITY", "0.7"))
        
        # Image settings
        self.image.min_confidence = float(os.getenv("DETECTION_IMAGE_CONFIDENCE", "0.88"))
        self.image.max_file_size_mb = int(os.getenv("DETECTION_IMAGE_MAX_SIZE", "50"))
        
        # Text settings
        self.text.min_confidence = float(os.getenv("DETECTION_TEXT_CONFIDENCE", "0.85"))
        self.text.max_sequence_length = int(os.getenv("DETECTION_TEXT_MAX_LENGTH", "512"))
        
        # ML settings
        self.ml_config.enable_gpu_acceleration = os.getenv("DETECTION_GPU_ENABLED", "true").lower() == "true"
        self.ml_config.model_precision = os.getenv("DETECTION_MODEL_PRECISION", "fp16")
        
        # Batch settings
        self.batch.batch_size = int(os.getenv("DETECTION_BATCH_SIZE", "32"))
        self.batch.max_workers = int(os.getenv("DETECTION_BATCH_WORKERS", "8"))
    
    def get_detection_config(self, category: ContentCategory) -> Dict[str, Any]:
        """Get detection configuration for specific content category."""
        category_map = {
            ContentCategory.MUSIC: self.audio,
            ContentCategory.PODCAST: self.audio,
            ContentCategory.VOICE: self.audio,
            ContentCategory.VIDEO: self.video,
            ContentCategory.MOVIE: self.video,
            ContentCategory.SERIES: self.video,
            ContentCategory.IMAGE: self.image,
            ContentCategory.PHOTO: self.image,
            ContentCategory.ARTWORK: self.image,
            ContentCategory.TEXT: self.text,
            ContentCategory.DOCUMENT: self.text,
            ContentCategory.SOCIAL_MEDIA: self.text
        }
        
        content_config = category_map.get(category)
        if not content_config:
            raise ValueError(f"Unsupported content category: {category}")
        
        return {
            "category": category,
            "detection_mode": self.detection_mode,
            "detection_level": self.detection_level,
            "content_config": content_config.__dict__,
            "ml_config": self.ml_config.__dict__,
            "quality_assurance": self.quality_assurance.__dict__,
            "output": self.output.__dict__
        }
    
    def get_engine_config(self, engine: DetectionEngine) -> Dict[str, Any]:
        """Get configuration for specific detection engine."""
        engine_configs = {
            # Audio engines
            DetectionEngine.CHROMAPRINT: {
                "sample_rate": self.audio.sample_rate,
                "chunk_duration": self.audio.chunk_duration,
                "overlap_duration": self.audio.overlap_duration
            },
            DetectionEngine.ESSENTIA: {
                "spectral_features": self.audio.spectral_features,
                "enable_genre_detection": self.audio.enable_genre_detection,
                "enable_mood_detection": self.audio.enable_mood_detection
            },
            DetectionEngine.LIBROSA: {
                "spectral_features": self.audio.spectral_features,
                "sample_rate": self.audio.sample_rate
            },
            
            # Video engines
            DetectionEngine.OPENCV: {
                "frame_sample_rate": self.video.frame_sample_rate,
                "motion_sensitivity": self.video.motion_detection_sensitivity
            },
            DetectionEngine.YOLO: {
                "confidence_threshold": self.video.min_confidence,
                "enable_object_detection": self.video.enable_object_detection
            },
            DetectionEngine.DETECTRON2: {
                "confidence_threshold": self.video.min_confidence,
                "enable_instance_segmentation": True
            },
            
            # Image engines
            DetectionEngine.CLIP: {
                "min_resolution": self.image.min_resolution,
                "enable_text_extraction": self.image.enable_text_extraction
            },
            DetectionEngine.RESNET: {
                "enable_object_detection": self.image.enable_object_detection,
                "confidence_threshold": self.image.min_confidence
            },
            
            # Text engines
            DetectionEngine.BERT: {
                "max_sequence_length": self.text.max_sequence_length,
                "supported_languages": self.text.supported_languages
            },
            DetectionEngine.ROBERTA: {
                "max_sequence_length": self.text.max_sequence_length,
                "enable_sentiment_analysis": self.text.enable_sentiment_analysis
            }
        }
        
        return engine_configs.get(engine, {})
    
    def get_processing_config(self) -> Dict[str, Any]:
        """Get processing configuration based on detection mode."""
        config = {
            "detection_mode": self.detection_mode,
            "max_concurrent_detections": self.max_concurrent_detections,
            "timeout_seconds": self.timeout_seconds,
            "memory_limit_gb": self.memory_limit_gb
        }
        
        if self.detection_mode in [DetectionMode.REALTIME, DetectionMode.HYBRID]:
            config["realtime"] = self.realtime.__dict__
        
        if self.detection_mode in [DetectionMode.BATCH, DetectionMode.HYBRID]:
            config["batch"] = self.batch.__dict__
        
        return config
    
    def optimize_for_performance(self) -> None:
        """Optimize configuration for maximum performance."""
        self.detection_level = DetectionLevel.MEDIUM
        self.ml_config.model_precision = "fp16"
        self.ml_config.enable_model_ensemble = False
        self.batch.batch_size = 64
        self.batch.max_workers = min(16, os.cpu_count() or 8)
        
        # Reduce confidence requirements slightly
        self.audio.min_confidence = 0.8
        self.video.min_confidence = 0.75
        self.image.min_confidence = 0.83
        self.text.min_confidence = 0.8
    
    def optimize_for_accuracy(self) -> None:
        """Optimize configuration for maximum accuracy."""
        self.detection_level = DetectionLevel.ULTRA
        self.ml_config.model_precision = "fp32"
        self.ml_config.enable_model_ensemble = True
        self.ml_config.enable_uncertainty_estimation = True
        
        # Increase confidence requirements
        self.audio.min_confidence = 0.92
        self.video.min_confidence = 0.88
        self.image.min_confidence = 0.95
        self.text.min_confidence = 0.92
        
        # Enable all quality features
        self.quality_assurance.enable_content_validation = True
        self.quality_assurance.enable_duplicate_detection = True
        self.quality_assurance.enable_anomaly_detection = True
    
    def validate_configuration(self) -> List[str]:
        """Validate current configuration and return any issues."""
        issues = []
        
        # Validate confidence thresholds
        if not 0.5 <= self.audio.min_confidence <= 1.0:
            issues.append("Audio confidence threshold must be between 0.5 and 1.0")
        
        if not 0.5 <= self.video.min_confidence <= 1.0:
            issues.append("Video confidence threshold must be between 0.5 and 1.0")
        
        if not 0.5 <= self.image.min_confidence <= 1.0:
            issues.append("Image confidence threshold must be between 0.5 and 1.0")
        
        if not 0.5 <= self.text.min_confidence <= 1.0:
            issues.append("Text confidence threshold must be between 0.5 and 1.0")
        
        # Validate processing limits
        if self.max_concurrent_detections <= 0:
            issues.append("Max concurrent detections must be positive")
        
        if self.timeout_seconds <= 0:
            issues.append("Timeout must be positive")
        
        if self.memory_limit_gb <= 0:
            issues.append("Memory limit must be positive")
        
        # Validate batch settings
        if self.batch.batch_size <= 0:
            issues.append("Batch size must be positive")
        
        if self.batch.max_workers <= 0:
            issues.append("Max workers must be positive")
        
        # Validate real-time settings
        if self.realtime.buffer_size_seconds <= 0:
            issues.append("Buffer size must be positive")
        
        if self.realtime.processing_interval_ms <= 0:
            issues.append("Processing interval must be positive")
        
        return issues
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""



        return {
            "detection_mode": self.detection_mode,
            "detection_level": self.detection_level,
            "enable_multi_engine_fusion": self.enable_multi_engine_fusion,
            "confidence_fusion_method": self.confidence_fusion_method,
            "enable_cross_validation": self.enable_cross_validation,
            "max_concurrent_detections": self.max_concurrent_detections,
            "timeout_seconds": self.timeout_seconds,
            "memory_limit_gb": self.memory_limit_gb,
            "enable_performance_monitoring": self.enable_performance_monitoring,
            "audio": self.audio.__dict__,
            "video": self.video.__dict__,
            "image": self.image.__dict__,
            "text": self.text.__dict__,
            "realtime": self.realtime.__dict__,
            "batch": self.batch.__dict__,
            "ml_config": self.ml_config.__dict__,
            "quality_assurance": self.quality_assurance.__dict__,
            "output": self.output.__dict__
        }
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'ContentDetectionConfig':
        """Create configuration from dictionary."""
        config = cls()
        
        # Load basic settings
        if "detection_mode" in config_dict:
            config.detection_mode = DetectionMode(config_dict["detection_mode"])
        if "detection_level" in config_dict:
            config.detection_level = DetectionLevel(config_dict["detection_level"])
        
        # Load scalar settings
        scalar_fields = [
            "enable_multi_engine_fusion", "confidence_fusion_method", 
            "enable_cross_validation", "max_concurrent_detections",
            "timeout_seconds", "memory_limit_gb", "enable_performance_monitoring"
        ]
        
        for field in scalar_fields:
            if field in config_dict:
                setattr(config, field, config_dict[field])
        
        # Load component configurations
        component_map = {
            "audio": config.audio,
            "video": config.video,
            "image": config.image,
            "text": config.text,
            "realtime": config.realtime,
            "batch": config.batch,
            "ml_config": config.ml_config,
            "quality_assurance": config.quality_assurance,
            "output": config.output
        }
        
        for key, component in component_map.items():
            if key in config_dict:
                for attr_key, attr_value in config_dict[key].items():
                    setattr(component, attr_key, attr_value)
        
        return config
