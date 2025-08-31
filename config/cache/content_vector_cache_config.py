"""Content Vector Cache Configuration for IA-Influencer Agent Platform
==================================================================

Professional caching system for AI-generated content vectors supporting
FAISS similarity search, embeddings, and high-dimensional content matching.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA-Influencer Agent + Content Protection Platform
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps

Copyright Notice:
This code is the intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution of this code
without explicit written permission from the author is strictly prohibited.

Contact: mlaiel@live.de for licensing inquiries.
"""from typing import Dict, Optional, List, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import hashlib
import numpy as np
from datetime import datetime, timedelta
from pydantic import BaseModel, validator


class VectorType(str, Enum):
    """Types of vectors used in content protection"""    # Audio vectors
    AUDIO_CHROMAPRINT = "audio_chromaprint"
    AUDIO_SPECTRAL = "audio_spectral"
    AUDIO_MFCC = "audio_mfcc"
    AUDIO_EMBEDDINGS = "audio_embeddings"
    
    # Video vectors
    VIDEO_FRAME_FEATURES = "video_frame_features"
    VIDEO_OPTICAL_FLOW = "video_optical_flow"
    VIDEO_EMBEDDINGS = "video_embeddings"
    
    # Image vectors
    IMAGE_CLIP_EMBEDDINGS = "image_clip_embeddings"
    IMAGE_RESNET_FEATURES = "image_resnet_features"
    IMAGE_PERCEPTUAL_HASH = "image_perceptual_hash"
    
    # Text vectors
    TEXT_BERT_EMBEDDINGS = "text_bert_embeddings"
    TEXT_ROBERTA_EMBEDDINGS = "text_roberta_embeddings"
    TEXT_WORD2VEC = "text_word2vec"
    TEXT_TF_IDF = "text_tf_idf"
    
    # Hybrid/Multi-modal vectors
    MULTIMODAL_CLIP = "multimodal_clip"
    CONTENT_FUSION = "content_fusion"


class SimilarityMetric(str, Enum):
    """Similarity metrics for vector comparison"""    COSINE = "cosine"
    EUCLIDEAN = "euclidean"
    DOT_PRODUCT = "dot_product"
    MANHATTAN = "manhattan"
    JACCARD = "jaccard"
    HAMMING = "hamming"


class IndexType(str, Enum):
    """FAISS index types for different use cases"""    FLAT = "flat"                    # Exact search, brute force
    IVF_FLAT = "ivf_flat"           # Inverted file with flat quantizer
    IVF_PQ = "ivf_pq"               # Inverted file with product quantizer
    HNSW = "hnsw"                   # Hierarchical navigable small world
    LSH = "lsh"                     # Locality sensitive hashing


@dataclass
class VectorCacheSettings:
    """Cache settings for specific vector type"""    vector_type: VectorType
    dimensions: int
    similarity_metric: SimilarityMetric = SimilarityMetric.COSINE
    index_type: IndexType = IndexType.FLAT
    
    # Performance settings
    max_vectors: int = 100000
    batch_size: int = 1000
    search_nprobe: int = 10  # For IVF indices
    search_k_factor: int = 10  # For HNSW
    
    # Cache behavior
    ttl_hours: int = 24
    preload_index: bool = False
    index_rebuild_threshold: int = 10000  # Rebuild index after N additions
    
    # Compression and storage
    use_compression: bool = True
    precision: str = "float32"  # float16, float32, float64
    quantization_enabled: bool = False
    
    # Quality settings
    similarity_threshold: float = 0.80
    max_neighbors: int = 100
    enable_deduplication: bool = True


@dataclass
class ContentVectorCacheConfig:
    """Complete configuration for content vector caching"""    
    # Cache identification
    cache_name: str = "content_vectors"
    namespace: str = "ia_influencer_vectors"
    tenant_id: Optional[str] = None
    
    # Storage configuration
    redis_key_prefix: str = "vector"
    faiss_index_path: str = "/indices"
    vector_storage_path: str = "/vectors"
    
    # Global settings
    max_total_vectors: int = 1000000  # 1M vectors total
    max_index_size_mb: int = 2048     # 2GB per index
    global_similarity_threshold: float = 0.75
    
    # Vector type configurations
    audio_vectors: Dict[str, VectorCacheSettings] = field(default_factory=lambda: {
        "chromaprint": VectorCacheSettings(
            vector_type=VectorType.AUDIO_CHROMAPRINT,
            dimensions=32,  # Chromaprint hash size
            similarity_metric=SimilarityMetric.HAMMING,
            index_type=IndexType.FLAT,
            max_vectors=500000,
            ttl_hours=48,
            similarity_threshold=0.85,
            precision="int32"  # For hash vectors
        ),
        "spectral": VectorCacheSettings(
            vector_type=VectorType.AUDIO_SPECTRAL,
            dimensions=1025,  # FFT bins
            similarity_metric=SimilarityMetric.COSINE,
            index_type=IndexType.IVF_FLAT,
            max_vectors=200000,
            ttl_hours=24,
            similarity_threshold=0.80,
            use_compression=True
        ),
        "mfcc": VectorCacheSettings(
            vector_type=VectorType.AUDIO_MFCC,
            dimensions=13,  # Standard MFCC coefficients
            similarity_metric=SimilarityMetric.EUCLIDEAN,
            index_type=IndexType.HNSW,
            max_vectors=300000,
            similarity_threshold=0.75
        )
    })
    
    video_vectors: Dict[str, VectorCacheSettings] = field(default_factory=lambda: {
        "frame_features": VectorCacheSettings(
            vector_type=VectorType.VIDEO_FRAME_FEATURES,
            dimensions=2048,  # ResNet features
            similarity_metric=SimilarityMetric.COSINE,
            index_type=IndexType.IVF_PQ,
            max_vectors=100000,
            ttl_hours=24,
            similarity_threshold=0.82,
            quantization_enabled=True
        ),
        "optical_flow": VectorCacheSettings(
            vector_type=VectorType.VIDEO_OPTICAL_FLOW,
            dimensions=256,
            similarity_metric=SimilarityMetric.EUCLIDEAN,
            index_type=IndexType.IVF_FLAT,
            max_vectors=150000,
            similarity_threshold=0.78
        )
    })
    
    image_vectors: Dict[str, VectorCacheSettings] = field(default_factory=lambda: {
        "clip_embeddings": VectorCacheSettings(
            vector_type=VectorType.IMAGE_CLIP_EMBEDDINGS,
            dimensions=512,  # CLIP vector size
            similarity_metric=SimilarityMetric.COSINE,
            index_type=IndexType.HNSW,
            max_vectors=200000,
            ttl_hours=36,
            similarity_threshold=0.85,
            preload_index=True
        ),
        "perceptual_hash": VectorCacheSettings(
            vector_type=VectorType.IMAGE_PERCEPTUAL_HASH,
            dimensions=64,  # 8x8 hash
            similarity_metric=SimilarityMetric.HAMMING,
            index_type=IndexType.FLAT,
            max_vectors=500000,
            similarity_threshold=0.90,
            precision="int64"
        )
    })
    
    text_vectors: Dict[str, VectorCacheSettings] = field(default_factory=lambda: {
        "bert_embeddings": VectorCacheSettings(
            vector_type=VectorType.TEXT_BERT_EMBEDDINGS,
            dimensions=768,  # BERT-base size
            similarity_metric=SimilarityMetric.COSINE,
            index_type=IndexType.IVF_FLAT,
            max_vectors=250000,
            ttl_hours=12,  # Shorter for text
            similarity_threshold=0.83
        ),
        "tf_idf": VectorCacheSettings(
            vector_type=VectorType.TEXT_TF_IDF,
            dimensions=5000,  # Variable vocabulary size
            similarity_metric=SimilarityMetric.COSINE,
            index_type=IndexType.LSH,
            max_vectors=100000,
            similarity_threshold=0.70,
            use_compression=True
        )
    })
    
    # Index management
    index_rebuild_schedule: str = "0 2 * * *"  # Daily at 2 AM
    auto_index_optimization: bool = True
    parallel_search_enabled: bool = True
    search_timeout_seconds: int = 30
    
    # Memory management
    max_memory_usage_mb: int = 4096  # 4GB
    memory_cleanup_threshold: float = 0.85
    vector_batch_processing: bool = True
    lazy_loading: bool = True
    
    # Quality and validation
    duplicate_detection_enabled: bool = True
    vector_quality_check: bool = True
    outlier_detection_enabled: bool = True
    
    # Monitoring and metrics
    performance_monitoring: bool = True
    search_analytics: bool = True
    similarity_distribution_tracking: bool = True
    alert_thresholds: Dict[str, Any] = field(default_factory=lambda: {
        "search_latency_max_ms": 500,
        "index_build_time_max_minutes": 30,
        "memory_usage_max": 0.90,
        "similarity_score_min": 0.60,
        "index_accuracy_min": 0.95
    })

    def get_vector_cache_key(self, content_hash: str, vector_type: VectorType, 
                           version: str = "1.0") -> str:
        """Generate cache key for vector data"""        key_components = [
            self.redis_key_prefix,
            self.namespace,
            vector_type.value,
            content_hash,
            version
        ]
        if self.tenant_id:
            key_components.insert(-2, self.tenant_id)
        return ":".join(key_components)
    
    def get_index_cache_key(self, vector_type: VectorType, index_version: str = "latest") -> str:
        """Generate cache key for FAISS index"""        key_components = [
            self.redis_key_prefix,
            "index",
            self.namespace,
            vector_type.value,
            index_version
        ]
        if self.tenant_id:
            key_components.insert(-2, self.tenant_id)
        return ":".join(key_components)
    
    def get_all_vector_settings(self) -> Dict[str, VectorCacheSettings]:
        """Get all configured vector settings"""        all_settings = {}
        all_settings.update(self.audio_vectors)
        all_settings.update(self.video_vectors) 
        all_settings.update(self.image_vectors)
        all_settings.update(self.text_vectors)
        return all_settings
    
    def estimate_memory_usage(self) -> Dict[str, float]:
        """Estimate memory usage for all vector types"""        memory_usage = {}
        total_memory = 0
        
        for name, settings in self.get_all_vector_settings().items():
            # Calculate memory per vector based on dimensions and precision
            bytes_per_element = 4 if settings.precision == "float32" else 2  # float16
            vector_size_bytes = settings.dimensions * bytes_per_element
            total_vector_memory = (settings.max_vectors * vector_size_bytes) / (1024 * 1024)  # MB
            
            memory_usage[name] = total_vector_memory
            total_memory += total_vector_memory
        
        memory_usage["total_estimated_mb"] = total_memory
        memory_usage["within_limits"] = total_memory <= self.max_memory_usage_mb
        
        return memory_usage


class ContentVectorCacheManager:
    """Manager for content vector cache operations"""    
    def __init__(self, config: ContentVectorCacheConfig):
        self.config = config
        self._loaded_indices = {}
        self._vector_stats = {}
        self._search_metrics = {}
    
    def calculate_similarity_threshold(self, vector_type: VectorType, 
                                     confidence_level: float = 0.95) -> float:
        """Calculate dynamic similarity threshold based on vector type and confidence"""        base_settings = None
        for settings in self.config.get_all_vector_settings().values():
            if settings.vector_type == vector_type:
                base_settings = settings
                break
        
        if not base_settings:
            return self.config.global_similarity_threshold
        
        # Adjust threshold based on confidence level
        base_threshold = base_settings.similarity_threshold
        
        if confidence_level >= 0.99:
            return min(base_threshold + 0.10, 0.98)  # Very high confidence
        elif confidence_level >= 0.95:
            return base_threshold  # Standard threshold
        elif confidence_level >= 0.90:
            return max(base_threshold - 0.05, 0.60)  # Lower threshold
        else:
            return max(base_threshold - 0.10, 0.50)  # Minimum threshold
    
    def validate_vector_quality(self, vector: np.ndarray, vector_type: VectorType) -> Dict[str, Any]:
        """Validate vector quality and characteristics"""        quality_report = {
            "is_valid": True,
            "issues": [],
            "quality_score": 1.0,
            "recommendations": []
        }
        
        # Check for NaN or infinite values
        if np.isnan(vector).any():
            quality_report["is_valid"] = False
            quality_report["issues"].append("Contains NaN values")
            quality_report["quality_score"] *= 0.0
        
        if np.isinf(vector).any():
            quality_report["is_valid"] = False
            quality_report["issues"].append("Contains infinite values")
            quality_report["quality_score"] *= 0.0
        
        # Check vector magnitude
        magnitude = np.linalg.norm(vector)
        if magnitude == 0:
            quality_report["is_valid"] = False
            quality_report["issues"].append("Zero magnitude vector")
            quality_report["quality_score"] *= 0.0
        elif magnitude < 0.01:
            quality_report["issues"].append("Very small magnitude")
            quality_report["quality_score"] *= 0.7
        
        # Check for outliers (values beyond reasonable range)
        std_dev = np.std(vector)
        mean_val = np.mean(vector)
        outliers = np.abs(vector - mean_val) > 3 * std_dev
        outlier_ratio = np.sum(outliers) / len(vector)
        
        if outlier_ratio > 0.1:  # More than 10% outliers
            quality_report["issues"].append(f"High outlier ratio: {outlier_ratio:.2%}")
            quality_report["quality_score"] *= (1 - outlier_ratio)
        
        # Vector-type specific validations
        if vector_type in [VectorType.AUDIO_CHROMAPRINT, VectorType.IMAGE_PERCEPTUAL_HASH]:
            # Hash vectors should be binary or integer
            if not np.all(np.logical_or(vector == 0, vector == 1)):
                quality_report["recommendations"].append("Hash vectors should be binary")
        
        return quality_report
    
    def generate_vector_fingerprint(self, vector: np.ndarray, metadata: Dict[str, Any]) -> str:
        """Generate unique fingerprint for vector with metadata"""        hasher = hashlib.sha256()
        
        # Add vector data
        hasher.update(vector.tobytes())
        
        # Add metadata
        for key, value in sorted(metadata.items()):
            hasher.update(f"{key}:{value}".encode())
        
        # Add timestamp for versioning
        hasher.update(str(datetime.now().date()).encode())
        
        return hasher.hexdigest()
    
    def get_search_statistics(self) -> Dict[str, Any]:
        """Get comprehensive search statistics"""        return {
            "total_searches": self._search_metrics.get("total_searches", 0),
            "avg_search_time_ms": self._search_metrics.get("avg_search_time_ms", 0),
            "search_accuracy": self._search_metrics.get("search_accuracy", 0.0),
            "cache_hit_rate": self._search_metrics.get("cache_hit_rate", 0.0),
            "vector_counts_by_type": self._get_vector_counts_by_type(),
            "similarity_score_distribution": self._search_metrics.get("similarity_distribution", {}),
            "index_status": self._get_index_status(),
            "memory_usage": self.config.estimate_memory_usage()
        }
    
    def _get_vector_counts_by_type(self) -> Dict[str, int]:
        """Get vector counts by type"""        counts = {}
        for vector_type in VectorType:
            counts[vector_type.value] = self._vector_stats.get(vector_type.value, {}).get("count", 0)
        return counts
    
    def _get_index_status(self) -> Dict[str, Any]:
        """Get status of all indices"""        status = {}
        for name in self.config.get_all_vector_settings().keys():
            status[name] = {
                "loaded": name in self._loaded_indices,
                "last_updated": self._vector_stats.get(name, {}).get("last_updated"),
                "size_mb": self._vector_stats.get(name, {}).get("size_mb", 0),
                "vector_count": self._vector_stats.get(name, {}).get("count", 0)
            }
        return status


# Environment-specific configurations
DEVELOPMENT_CONFIG = ContentVectorCacheConfig(
    cache_name="dev_content_vectors",
    max_total_vectors=10000,  # Smaller for dev
    max_index_size_mb=256,    # 256MB for dev
    max_memory_usage_mb=512,  # 512MB for dev
    performance_monitoring=False,
    auto_index_optimization=False,
    parallel_search_enabled=False
)

TESTING_CONFIG = ContentVectorCacheConfig(
    cache_name="test_content_vectors",
    max_total_vectors=1000,   # Minimal for tests
    max_index_size_mb=64,     # 64MB for tests
    max_memory_usage_mb=128,  # 128MB for tests
    vector_quality_check=False,
    search_analytics=False,
    duplicate_detection_enabled=False
)

PRODUCTION_CONFIG = ContentVectorCacheConfig(
    cache_name="prod_content_vectors",
    max_total_vectors=10000000,  # 10M vectors for production
    max_index_size_mb=8192,      # 8GB per index
    max_memory_usage_mb=16384,   # 16GB for production
    performance_monitoring=True,
    auto_index_optimization=True,
    parallel_search_enabled=True,
    vector_quality_check=True,
    duplicate_detection_enabled=True,
    outlier_detection_enabled=True
)

# Export main classes
__all__ = [
    'VectorType',
    'SimilarityMetric',
    'IndexType',
    'VectorCacheSettings',
    'ContentVectorCacheConfig',
    'ContentVectorCacheManager',
    'DEVELOPMENT_CONFIG',
    'TESTING_CONFIG',
    'PRODUCTION_CONFIG'
]
