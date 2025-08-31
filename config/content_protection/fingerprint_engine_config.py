"""Fingerprint Engine Configuration Module
======================================

Professional fingerprinting engine configuration for multi-format content protection.
Supports audio, video, image, and text fingerprinting with industrial-grade precision.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA-Influencer Agent + Content Protection Platform
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps

⚠️  COPYRIGHT WARNING:
This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, modification, or distribution of this code
without explicit written permission from Fahed Mlaiel (mlaiel@live.de) is strictly prohibited.
Violators will be prosecuted to the full extent of the law.
"""from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum
import os


class ContentType(str, Enum):
    """Supported content types for fingerprinting."""    AUDIO = "audio"
    VIDEO = "video" 
    IMAGE = "image"
    TEXT = "text"


class FingerprintAlgorithm(str, Enum):
    """Available fingerprinting algorithms by content type."""    # Audio algorithms
    CHROMAPRINT = "chromaprint"
    ESSENTIA_SPECTRAL = "essentia_spectral"
    LIBROSA_MFCC = "librosa_mfcc"
    
    # Video algorithms
    PERCEPTUAL_HASH = "perceptual_hash"
    YOLO_FRAME = "yolo_frame"
    OPENCV_ORB = "opencv_orb"
    
    # Image algorithms
    CLIP_EMBEDDINGS = "clip_embeddings"
    IMAGEHASH_AVERAGE = "imagehash_average"
    RESNET_FEATURES = "resnet_features"
    
    # Text algorithms
    BERT_EMBEDDINGS = "bert_embeddings"
    ROBERTA_SEMANTIC = "roberta_semantic"
    TFIDF_VECTORIZER = "tfidf_vectorizer"


@dataclass
class AudioFingerprintConfig:
    """Audio fingerprinting configuration."""    algorithm: FingerprintAlgorithm = FingerprintAlgorithm.CHROMAPRINT
    sample_rate: int = 22050
    n_fft: int = 2048
    hop_length: int = 512
    n_mfcc: int = 13
    window_size: float = 0.064
    overlap: float = 0.032
    precision_threshold: float = 0.95
    enable_spectral_analysis: bool = True
    enable_temporal_features: bool = True
    chromaprint_duration: int = 120  # seconds
    essentia_enabled: bool = True


@dataclass
class VideoFingerprintConfig:
    """Video fingerprinting configuration."""    algorithm: FingerprintAlgorithm = FingerprintAlgorithm.PERCEPTUAL_HASH
    frame_sample_rate: int = 1  # frames per second
    hash_size: int = 8
    yolo_model: str = "yolov5s"
    orb_features: int = 500
    precision_threshold: float = 0.90
    enable_object_detection: bool = True
    enable_scene_change_detection: bool = True
    max_duration: int = 300  # seconds
    quality_threshold: float = 0.7


@dataclass
class ImageFingerprintConfig:
    """Image fingerprinting configuration."""    algorithm: FingerprintAlgorithm = FingerprintAlgorithm.CLIP_EMBEDDINGS
    clip_model: str = "ViT-B/32"
    hash_size: int = 16
    resize_dimensions: tuple = (224, 224)
    precision_threshold: float = 0.92
    enable_perceptual_hash: bool = True
    enable_feature_extraction: bool = True
    color_mode: str = "RGB"
    normalization: bool = True


@dataclass
class TextFingerprintConfig:
    """Text fingerprinting configuration."""    algorithm: FingerprintAlgorithm = FingerprintAlgorithm.BERT_EMBEDDINGS
    bert_model: str = "bert-base-multilingual-cased"
    roberta_model: str = "roberta-base"
    max_sequence_length: int = 512
    precision_threshold: float = 0.88
    enable_semantic_analysis: bool = True
    enable_syntactic_analysis: bool = True
    min_text_length: int = 50
    language_detection: bool = True


@dataclass
class VectorStoreConfig:
    """Vector storage configuration for similarity matching."""    backend: str = "faiss"  # faiss, pinecone, weaviate
    index_type: str = "IVF_FLAT"
    dimension_size: int = 512
    num_clusters: int = 1024
    search_k: int = 100
    similarity_metric: str = "cosine"  # cosine, euclidean, manhattan
    batch_size: int = 1000
    enable_gpu: bool = True
    memory_mapping: bool = True


@dataclass
class PerformanceConfig:
    """Performance optimization configuration."""    max_workers: int = 8
    batch_processing_size: int = 50
    memory_limit_mb: int = 2048
    timeout_seconds: int = 300
    enable_caching: bool = True
    cache_ttl_hours: int = 24
    enable_parallel_processing: bool = True
    gpu_acceleration: bool = True


@dataclass
class SecurityConfig:
    """Security configuration for fingerprinting."""    encryption_algorithm: str = "AES-256-GCM"
    hash_algorithm: str = "SHA-256"
    secure_deletion: bool = True
    audit_logging: bool = True
    access_control: bool = True
    rate_limiting: bool = True
    max_requests_per_minute: int = 100


class FingerprintEngineConfig:
    """    Professional fingerprint engine configuration manager.
    Provides industrial-grade configuration for multi-format content fingerprinting.
    """    
    def __init__(self):
        self.audio = AudioFingerprintConfig()
        self.video = VideoFingerprintConfig()
        self.image = ImageFingerprintConfig()
        self.text = TextFingerprintConfig()
        self.vector_store = VectorStoreConfig()
        self.performance = PerformanceConfig()
        self.security = SecurityConfig()
        
        # Load environment-specific configurations
        self._load_from_environment()
    
    def _load_from_environment(self) -> None:
        """Load configuration from environment variables."""        # Audio configuration
        self.audio.sample_rate = int(os.getenv("FINGERPRINT_AUDIO_SAMPLE_RATE", "22050"))
        self.audio.precision_threshold = float(os.getenv("FINGERPRINT_AUDIO_PRECISION", "0.95"))
        
        # Video configuration
        self.video.precision_threshold = float(os.getenv("FINGERPRINT_VIDEO_PRECISION", "0.90"))
        self.video.max_duration = int(os.getenv("FINGERPRINT_VIDEO_MAX_DURATION", "300"))
        
        # Image configuration
        self.image.precision_threshold = float(os.getenv("FINGERPRINT_IMAGE_PRECISION", "0.92"))
        
        # Text configuration
        self.text.precision_threshold = float(os.getenv("FINGERPRINT_TEXT_PRECISION", "0.88"))
        self.text.max_sequence_length = int(os.getenv("FINGERPRINT_TEXT_MAX_LENGTH", "512"))
        
        # Vector store configuration
        self.vector_store.backend = os.getenv("FINGERPRINT_VECTOR_BACKEND", "faiss")
        self.vector_store.dimension_size = int(os.getenv("FINGERPRINT_VECTOR_DIMENSION", "512"))
        
        # Performance configuration
        self.performance.max_workers = int(os.getenv("FINGERPRINT_MAX_WORKERS", "8"))
        self.performance.memory_limit_mb = int(os.getenv("FINGERPRINT_MEMORY_LIMIT", "2048"))
        self.performance.gpu_acceleration = os.getenv("FINGERPRINT_GPU_ENABLED", "true").lower() == "true"
    
    def get_config_for_content_type(self, content_type: ContentType) -> Dict[str, Any]:
        """Get specific configuration for content type."""        config_map = {
            ContentType.AUDIO: self.audio,
            ContentType.VIDEO: self.video,
            ContentType.IMAGE: self.image,
            ContentType.TEXT: self.text
        }
        
        config = config_map.get(content_type)
        if not config:
            raise ValueError(f"Unsupported content type: {content_type}")
        
        return {
            "content_config": config.__dict__,
            "vector_store": self.vector_store.__dict__,
            "performance": self.performance.__dict__,
            "security": self.security.__dict__
        }
    
    def get_algorithm_config(self, algorithm: FingerprintAlgorithm) -> Dict[str, Any]:
        """Get configuration for specific algorithm."""        algorithm_configs = {
            # Audio algorithms
            FingerprintAlgorithm.CHROMAPRINT: {
                "duration": self.audio.chromaprint_duration,
                "sample_rate": self.audio.sample_rate,
                "window_size": self.audio.window_size,
                "overlap": self.audio.overlap
            },
            FingerprintAlgorithm.ESSENTIA_SPECTRAL: {
                "enabled": self.audio.essentia_enabled,
                "n_fft": self.audio.n_fft,
                "hop_length": self.audio.hop_length
            },
            FingerprintAlgorithm.LIBROSA_MFCC: {
                "n_mfcc": self.audio.n_mfcc,
                "sample_rate": self.audio.sample_rate
            },
            
            # Video algorithms
            FingerprintAlgorithm.PERCEPTUAL_HASH: {
                "hash_size": self.video.hash_size,
                "frame_rate": self.video.frame_sample_rate
            },
            FingerprintAlgorithm.YOLO_FRAME: {
                "model": self.video.yolo_model,
                "quality_threshold": self.video.quality_threshold
            },
            FingerprintAlgorithm.OPENCV_ORB: {
                "features": self.video.orb_features
            },
            
            # Image algorithms
            FingerprintAlgorithm.CLIP_EMBEDDINGS: {
                "model": self.image.clip_model,
                "dimensions": self.image.resize_dimensions
            },
            FingerprintAlgorithm.IMAGEHASH_AVERAGE: {
                "hash_size": self.image.hash_size
            },
            
            # Text algorithms
            FingerprintAlgorithm.BERT_EMBEDDINGS: {
                "model": self.text.bert_model,
                "max_length": self.text.max_sequence_length
            },
            FingerprintAlgorithm.ROBERTA_SEMANTIC: {
                "model": self.text.roberta_model,
                "max_length": self.text.max_sequence_length
            }
        }
        
        return algorithm_configs.get(algorithm, {})
    
    def validate_configuration(self) -> List[str]:
        """Validate current configuration and return any issues."""        issues = []
        
        # Validate precision thresholds
        if not 0.7 <= self.audio.precision_threshold <= 1.0:
            issues.append("Audio precision threshold must be between 0.7 and 1.0")
        
        if not 0.7 <= self.video.precision_threshold <= 1.0:
            issues.append("Video precision threshold must be between 0.7 and 1.0")
        
        if not 0.7 <= self.image.precision_threshold <= 1.0:
            issues.append("Image precision threshold must be between 0.7 and 1.0")
        
        if not 0.7 <= self.text.precision_threshold <= 1.0:
            issues.append("Text precision threshold must be between 0.7 and 1.0")
        
        # Validate performance settings
        if self.performance.max_workers < 1:
            issues.append("Max workers must be at least 1")
        
        if self.performance.memory_limit_mb < 512:
            issues.append("Memory limit must be at least 512MB")
        
        # Validate vector store settings
        if self.vector_store.dimension_size < 64:
            issues.append("Vector dimension size must be at least 64")
        
        return issues
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""        return {
            "audio": self.audio.__dict__,
            "video": self.video.__dict__,
            "image": self.image.__dict__,
            "text": self.text.__dict__,
            "vector_store": self.vector_store.__dict__,
            "performance": self.performance.__dict__,
            "security": self.security.__dict__
        }
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'FingerprintEngineConfig':
        """Create configuration from dictionary."""        config = cls()
        
        if "audio" in config_dict:
            for key, value in config_dict["audio"].items():
                setattr(config.audio, key, value)
        
        if "video" in config_dict:
            for key, value in config_dict["video"].items():
                setattr(config.video, key, value)
        
        if "image" in config_dict:
            for key, value in config_dict["image"].items():
                setattr(config.image, key, value)
        
        if "text" in config_dict:
            for key, value in config_dict["text"].items():
                setattr(config.text, key, value)
        
        if "vector_store" in config_dict:
            for key, value in config_dict["vector_store"].items():
                setattr(config.vector_store, key, value)
        
        if "performance" in config_dict:
            for key, value in config_dict["performance"].items():
                setattr(config.performance, key, value)
        
        if "security" in config_dict:
            for key, value in config_dict["security"].items():
                setattr(config.security, key, value)
        
        return config
