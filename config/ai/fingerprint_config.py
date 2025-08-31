"""
AI Fingerprinting Configuration for IA-Influencer Agent Platform
================================================================

Professional fingerprinting AI configuration for content protection.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA-Influencer Agent + Content Protection Platform
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps

STRICT COPYRIGHT NOTICE:
This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, distribution, or reverse engineering
without explicit written permission is STRICTLY PROHIBITED and will be
prosecuted to the full extent of the law.

Contact: mlaiel@live.de for licensing inquiries.
"""

from typing import Dict, List, Optional, Union, Any, Tuple
from pydantic import BaseSettings, validator
from enum import Enum
from dataclasses import dataclass
import os


class FingerprintType(str, Enum):
    """Supported fingerprint types for content protection."""
    
    AUDIO_CHROMAPRINT = "audio_chromaprint"
    AUDIO_SPECTRAL = "audio_spectral"
    AUDIO_MFCC = "audio_mfcc"
    IMAGE_PHASH = "image_phash"
    IMAGE_DHASH = "image_dhash"
    IMAGE_WHASH = "image_whash"
    IMAGE_CLIP = "image_clip"
    VIDEO_FRAME = "video_frame"
    VIDEO_MOTION = "video_motion"
    TEXT_EMBEDDING = "text_embedding"
    TEXT_SEMANTIC = "text_semantic"
    MULTIMODAL_CLIP = "multimodal_clip"


class SimilarityMetric(str, Enum):
    """Similarity metrics for fingerprint matching."""
    
    COSINE = "cosine"
    EUCLIDEAN = "euclidean"
    MANHATTAN = "manhattan"
    HAMMING = "hamming"
    JACCARD = "jaccard"
    PEARSON = "pearson"
    SPEARMAN = "spearman"


@dataclass
class FingerprintSpec:
    """Specification for fingerprint algorithm configuration."""
    
    fingerprint_type: FingerprintType
    algorithm: str
    model_path: Optional[str] = None
    vector_dimension: int = 256
    similarity_metric: SimilarityMetric = SimilarityMetric.COSINE
    similarity_threshold: float = 0.85
    extraction_time_limit: int = 30  # seconds
    batch_size: int = 16
    requires_preprocessing: bool = True
    output_format: str = "vector"  # vector, hash, binary
    memory_requirement_mb: int = 512
    gpu_acceleration: bool = False
    custom_params: Optional[Dict[str, Any]] = None


class FingerprintAIConfig(BaseSettings):
    """
    Professional AI Fingerprinting Configuration for Content Protection.
    
    Manages all fingerprinting algorithms and similarity matching for audio,
    video, image, and text content protection across the platform.
    """
    
    # Core Fingerprinting Configuration
    FINGERPRINT_STORAGE_PATH: str = "/data/fingerprints"
    FINGERPRINT_INDEX_TYPE: str = "faiss"  # faiss, annoy, hnswlib
    VECTOR_DIMENSION: int = 512
    SIMILARITY_THRESHOLD_GLOBAL: float = 0.80
    
    # Performance Configuration
    BATCH_PROCESSING_SIZE: int = 32
    MAX_CONCURRENT_EXTRACTIONS: int = 4
    FINGERPRINT_CACHE_SIZE: int = 10000
    INDEX_REBUILD_INTERVAL: int = 3600  # seconds
    
    # Audio Fingerprinting
    AUDIO_SAMPLE_RATE: int = 22050
    AUDIO_CHUNK_SIZE: int = 4096
    AUDIO_OVERLAP_RATIO: float = 0.5
    CHROMAPRINT_ALGORITHM: str = "chromaprint"
    CHROMAPRINT_DURATION_MAX: int = 120  # seconds
    
    # Spectral Audio Features
    SPECTRAL_N_FFT: int = 2048
    SPECTRAL_HOP_LENGTH: int = 512
    SPECTRAL_N_MELS: int = 128
    MFCC_N_COMPONENTS: int = 13
    
    # Image Fingerprinting
    IMAGE_RESIZE_TARGET: Tuple[int, int] = (224, 224)
    IMAGE_HASH_SIZE: int = 8
    IMAGE_WAVELET_LEVELS: int = 4
    CLIP_IMAGE_MODEL: str = "openai/clip-vit-base-patch32"
    
    # Video Fingerprinting
    VIDEO_FRAME_SAMPLING_RATE: int = 1  # frames per second
    VIDEO_KEYFRAME_DETECTION: bool = True
    VIDEO_MOTION_THRESHOLD: float = 0.3
    VIDEO_SCENE_CHANGE_THRESHOLD: float = 0.7
    
    # Text Fingerprinting
    TEXT_EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    TEXT_MAX_LENGTH: int = 512
    TEXT_NGRAM_RANGE: Tuple[int, int] = (1, 3)
    TEXT_MIN_LENGTH: int = 50  # characters
    
    # Similarity Matching
    MATCH_CONFIDENCE_LEVELS: Dict[str, float] = {
        "high": 0.95,
        "medium": 0.85,
        "low": 0.70,
        "suspicious": 0.60
    }
    
    # Vector Store Configuration
    FAISS_INDEX_TYPE: str = "IndexFlatIP"  # Inner Product for cosine similarity
    FAISS_NPROBE: int = 10
    FAISS_TRAINING_SIZE: int = 10000
    
    # Monitoring and Analytics
    FINGERPRINT_ANALYTICS_ENABLED: bool = True
    MATCH_LOGGING_ENABLED: bool = True
    PERFORMANCE_MONITORING: bool = True
    
    class Config:
        env_prefix = "FINGERPRINT_"
        case_sensitive = False
        env_file = ".env"
    
    @validator("FINGERPRINT_STORAGE_PATH")
    def create_storage_path(cls, v):
        """Ensure fingerprint storage directory exists."""
        os.makedirs(v, exist_ok=True)
        os.makedirs(f"{v}/audio", exist_ok=True)
        os.makedirs(f"{v}/video", exist_ok=True)
        os.makedirs(f"{v}/image", exist_ok=True)
        os.makedirs(f"{v}/text", exist_ok=True)
        os.makedirs(f"{v}/indexes", exist_ok=True)
        return v
    
    def get_fingerprint_spec(self, fingerprint_type: FingerprintType) -> FingerprintSpec:
        """Get fingerprint specification by type."""
        specs = {
            FingerprintType.AUDIO_CHROMAPRINT: FingerprintSpec(
                fingerprint_type=FingerprintType.AUDIO_CHROMAPRINT,
                algorithm="chromaprint",
                vector_dimension=32,
                similarity_metric=SimilarityMetric.HAMMING,
                similarity_threshold=0.90,
                extraction_time_limit=self.CHROMAPRINT_DURATION_MAX,
                batch_size=8,
                output_format="binary",
                memory_requirement_mb=256,
                custom_params={
                    "sample_rate": self.AUDIO_SAMPLE_RATE,
                    "duration": self.CHROMAPRINT_DURATION_MAX,
                }
            ),
            
            FingerprintType.AUDIO_SPECTRAL: FingerprintSpec(
                fingerprint_type=FingerprintType.AUDIO_SPECTRAL,
                algorithm="spectral_centroid",
                vector_dimension=self.SPECTRAL_N_MELS,
                similarity_metric=SimilarityMetric.COSINE,
                similarity_threshold=0.85,
                extraction_time_limit=60,
                batch_size=16,
                output_format="vector",
                memory_requirement_mb=512,
                custom_params={
                    "n_fft": self.SPECTRAL_N_FFT,
                    "hop_length": self.SPECTRAL_HOP_LENGTH,
                    "n_mels": self.SPECTRAL_N_MELS,
                }
            ),
            
            FingerprintType.AUDIO_MFCC: FingerprintSpec(
                fingerprint_type=FingerprintType.AUDIO_MFCC,
                algorithm="mfcc",
                vector_dimension=self.MFCC_N_COMPONENTS * 10,  # temporal averaging
                similarity_metric=SimilarityMetric.COSINE,
                similarity_threshold=0.80,
                extraction_time_limit=60,
                batch_size=16,
                output_format="vector",
                memory_requirement_mb=384,
                custom_params={
                    "n_mfcc": self.MFCC_N_COMPONENTS,
                    "sample_rate": self.AUDIO_SAMPLE_RATE,
                }
            ),
            
            FingerprintType.IMAGE_PHASH: FingerprintSpec(
                fingerprint_type=FingerprintType.IMAGE_PHASH,
                algorithm="perceptual_hash",
                vector_dimension=64,  # 8x8 hash
                similarity_metric=SimilarityMetric.HAMMING,
                similarity_threshold=0.90,
                extraction_time_limit=10,
                batch_size=32,
                output_format="binary",
                memory_requirement_mb=128,
                custom_params={
                    "hash_size": self.IMAGE_HASH_SIZE,
                    "resize_target": self.IMAGE_RESIZE_TARGET,
                }
            ),
            
            FingerprintType.IMAGE_CLIP: FingerprintSpec(
                fingerprint_type=FingerprintType.IMAGE_CLIP,
                algorithm="clip_embedding",
                model_path=self.CLIP_IMAGE_MODEL,
                vector_dimension=512,
                similarity_metric=SimilarityMetric.COSINE,
                similarity_threshold=0.85,
                extraction_time_limit=15,
                batch_size=16,
                output_format="vector",
                memory_requirement_mb=1024,
                gpu_acceleration=True,
                custom_params={
                    "resize_target": self.IMAGE_RESIZE_TARGET,
                }
            ),
            
            FingerprintType.VIDEO_FRAME: FingerprintSpec(
                fingerprint_type=FingerprintType.VIDEO_FRAME,
                algorithm="frame_sampling",
                vector_dimension=512,
                similarity_metric=SimilarityMetric.COSINE,
                similarity_threshold=0.80,
                extraction_time_limit=120,
                batch_size=8,
                output_format="vector",
                memory_requirement_mb=2048,
                gpu_acceleration=True,
                custom_params={
                    "sampling_rate": self.VIDEO_FRAME_SAMPLING_RATE,
                    "keyframe_detection": self.VIDEO_KEYFRAME_DETECTION,
                    "motion_threshold": self.VIDEO_MOTION_THRESHOLD,
                }
            ),
            
            FingerprintType.TEXT_EMBEDDING: FingerprintSpec(
                fingerprint_type=FingerprintType.TEXT_EMBEDDING,
                algorithm="sentence_transformers",
                model_path=self.TEXT_EMBEDDING_MODEL,
                vector_dimension=384,
                similarity_metric=SimilarityMetric.COSINE,
                similarity_threshold=0.75,
                extraction_time_limit=30,
                batch_size=32,
                output_format="vector",
                memory_requirement_mb=512,
                custom_params={
                    "max_length": self.TEXT_MAX_LENGTH,
                    "min_length": self.TEXT_MIN_LENGTH,
                }
            ),
            
            FingerprintType.TEXT_SEMANTIC: FingerprintSpec(
                fingerprint_type=FingerprintType.TEXT_SEMANTIC,
                algorithm="tfidf_ngram",
                vector_dimension=1000,
                similarity_metric=SimilarityMetric.COSINE,
                similarity_threshold=0.70,
                extraction_time_limit=20,
                batch_size=64,
                output_format="vector",
                memory_requirement_mb=256,
                custom_params={
                    "ngram_range": self.TEXT_NGRAM_RANGE,
                    "max_features": 1000,
                }
            ),
        }
        
        return specs.get(fingerprint_type, self._get_default_spec(fingerprint_type))
    
    def _get_default_spec(self, fingerprint_type: FingerprintType) -> FingerprintSpec:
        """Get default specification for unknown fingerprint types."""



        return FingerprintSpec(
            fingerprint_type=fingerprint_type,
            algorithm="default",
            vector_dimension=self.VECTOR_DIMENSION,
            similarity_metric=SimilarityMetric.COSINE,
            similarity_threshold=self.SIMILARITY_THRESHOLD_GLOBAL,
        )
    
    def get_specs_by_content_type(self, content_type: str) -> List[FingerprintSpec]:
        """Get all fingerprint specs for a content type."""
        content_specs = {
            "audio": [
                FingerprintType.AUDIO_CHROMAPRINT,
                FingerprintType.AUDIO_SPECTRAL,
                FingerprintType.AUDIO_MFCC,
            ],
            "image": [
                FingerprintType.IMAGE_PHASH,
                FingerprintType.IMAGE_DHASH,
                FingerprintType.IMAGE_WHASH,
                FingerprintType.IMAGE_CLIP,
            ],
            "video": [
                FingerprintType.VIDEO_FRAME,
                FingerprintType.VIDEO_MOTION,
                FingerprintType.IMAGE_CLIP,  # for frames
            ],
            "text": [
                FingerprintType.TEXT_EMBEDDING,
                FingerprintType.TEXT_SEMANTIC,
            ],
            "multimodal": [
                FingerprintType.MULTIMODAL_CLIP,
            ]
        }
        
        types = content_specs.get(content_type.lower(), [])
        return [self.get_fingerprint_spec(fp_type) for fp_type in types]
    
    def get_optimal_algorithm(self, content_type: str, file_size_mb: float) -> FingerprintSpec:
        """Get optimal fingerprint algorithm based on content type and file size."""
        specs = self.get_specs_by_content_type(content_type)
        
        # For large files, prefer faster algorithms
        if file_size_mb > 100:
            fast_specs = [spec for spec in specs if spec.extraction_time_limit <= 30]
            if fast_specs:
                specs = fast_specs
        
        # For small files, prefer high-accuracy algorithms
        elif file_size_mb < 10:
            accurate_specs = [spec for spec in specs if spec.similarity_threshold >= 0.85]
            if accurate_specs:
                specs = accurate_specs
        
        # Return the first suitable spec (could be enhanced with more logic)
        return specs[0] if specs else self._get_default_spec(FingerprintType.AUDIO_CHROMAPRINT)
    
    def get_similarity_config(self) -> Dict[str, Any]:
        """Get similarity matching configuration."""



        return {
            "thresholds": self.MATCH_CONFIDENCE_LEVELS,
            "global_threshold": self.SIMILARITY_THRESHOLD_GLOBAL,
            "vector_dimension": self.VECTOR_DIMENSION,
            "index_config": {
                "type": self.FAISS_INDEX_TYPE,
                "nprobe": self.FAISS_NPROBE,
                "training_size": self.FAISS_TRAINING_SIZE,
            },
            "performance": {
                "batch_size": self.BATCH_PROCESSING_SIZE,
                "max_concurrent": self.MAX_CONCURRENT_EXTRACTIONS,
                "cache_size": self.FINGERPRINT_CACHE_SIZE,
                "rebuild_interval": self.INDEX_REBUILD_INTERVAL,
            }
        }
    
    def get_content_type_config(self, content_type: str) -> Dict[str, Any]:
        """Get configuration specific to content type."""
        configs = {
            "audio": {
                "sample_rate": self.AUDIO_SAMPLE_RATE,
                "chunk_size": self.AUDIO_CHUNK_SIZE,
                "overlap_ratio": self.AUDIO_OVERLAP_RATIO,
                "max_duration": self.CHROMAPRINT_DURATION_MAX,
                "spectral": {
                    "n_fft": self.SPECTRAL_N_FFT,
                    "hop_length": self.SPECTRAL_HOP_LENGTH,
                    "n_mels": self.SPECTRAL_N_MELS,
                },
                "mfcc": {
                    "n_components": self.MFCC_N_COMPONENTS,
                }
            },
            "image": {
                "resize_target": self.IMAGE_RESIZE_TARGET,
                "hash_size": self.IMAGE_HASH_SIZE,
                "wavelet_levels": self.IMAGE_WAVELET_LEVELS,
                "clip_model": self.CLIP_IMAGE_MODEL,
            },
            "video": {
                "frame_sampling_rate": self.VIDEO_FRAME_SAMPLING_RATE,
                "keyframe_detection": self.VIDEO_KEYFRAME_DETECTION,
                "motion_threshold": self.VIDEO_MOTION_THRESHOLD,
                "scene_change_threshold": self.VIDEO_SCENE_CHANGE_THRESHOLD,
            },
            "text": {
                "embedding_model": self.TEXT_EMBEDDING_MODEL,
                "max_length": self.TEXT_MAX_LENGTH,
                "min_length": self.TEXT_MIN_LENGTH,
                "ngram_range": self.TEXT_NGRAM_RANGE,
            }
        }
        
        return configs.get(content_type.lower(), {})


# Global fingerprinting configuration instance
fingerprint_ai_config = FingerprintAIConfig()
