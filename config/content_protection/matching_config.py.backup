"""Similarity Matching Configuration Module
=======================================

Professional similarity matching configuration for content comparison and duplicate detection.
Supports advanced vector similarity, fuzzy matching, and machine learning-based comparison.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA-Influencer Agent + Content Protection Platform
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps

⚠️  COPYRIGHT WARNING:
This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, modification, or distribution of this code
without explicit written permission from Fahed Mlaiel (mlaiel@live.de) is strictly prohibited.
Violators will be prosecuted to the full extent of the law.
"""
from typing import Dict, Any, List, Optional, Set, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
import os


class SimilarityMetric(str, Enum):
    """Similarity measurement metrics."""
    COSINE = "cosine"
    EUCLIDEAN = "euclidean"
    MANHATTAN = "manhattan"
    JACCARD = "jaccard"
    HAMMING = "hamming"
    PEARSON = "pearson"
    SPEARMAN = "spearman"
    MINKOWSKI = "minkowski"


class MatchingAlgorithm(str, Enum):
    """Matching algorithms for different content types."""
    # Vector-based algorithms
    FAISS_IVF = "faiss_ivf"
    FAISS_HNSW = "faiss_hnsw"
    ANNOY = "annoy"
    PINECONE = "pinecone"
    
    # Hash-based algorithms
    LOCALITY_SENSITIVE_HASHING = "lsh"
    MINHASH = "minhash"
    SIMHASH = "simhash"
    
    # ML-based algorithms
    SIAMESE_NETWORK = "siamese_network"
    CONTRASTIVE_LEARNING = "contrastive_learning"
    TRIPLET_LOSS = "triplet_loss"
    
    # Traditional algorithms
    DYNAMIC_TIME_WARPING = "dtw"
    CROSS_CORRELATION = "cross_correlation"
    FUZZY_MATCHING = "fuzzy_matching"


class ContentSimilarityType(str, Enum):
    """Types of content similarity."""
    EXACT_MATCH = "exact_match"          # 100% identical
    NEAR_DUPLICATE = "near_duplicate"    # >95% similar
    VARIANT = "variant"                  # 80-95% similar
    DERIVATIVE = "derivative"            # 60-80% similar
    INSPIRED = "inspired"                # 40-60% similar
    UNRELATED = "unrelated"              # <40% similar


@dataclass
class VectorMatchingConfig:
    """Vector-based similarity matching configuration."""
    algorithm: MatchingAlgorithm = MatchingAlgorithm.FAISS_IVF
    similarity_metric: SimilarityMetric = SimilarityMetric.COSINE
    vector_dimension: int = 512
    index_type: str = "IVF_FLAT"
    nprobe: int = 32
    num_clusters: int = 1024
    search_k: int = 100
    top_k_results: int = 50
    enable_pq_compression: bool = True
    pq_m: int = 16  # PQ segments
    enable_gpu_acceleration: bool = True
    memory_mapping: bool = True


@dataclass
class HashMatchingConfig:
    """Hash-based similarity matching configuration."""
    algorithm: MatchingAlgorithm = MatchingAlgorithm.LOCALITY_SENSITIVE_HASHING
    hash_size: int = 64
    num_hash_tables: int = 10
    hash_family: str = "random_projection"  # random_projection, cosine
    band_size: int = 5
    signature_length: int = 128
    enable_bloom_filter: bool = True
    bloom_filter_capacity: int = 1000000
    false_positive_rate: float = 0.01


@dataclass
class AudioMatchingConfig:
    """Audio similarity matching configuration."""
    primary_algorithm: MatchingAlgorithm = MatchingAlgorithm.FAISS_IVF
    fallback_algorithm: MatchingAlgorithm = MatchingAlgorithm.CROSS_CORRELATION
    exact_match_threshold: float = 0.98
    near_duplicate_threshold: float = 0.95
    variant_threshold: float = 0.85
    derivative_threshold: float = 0.70
    enable_tempo_invariant: bool = True
    enable_pitch_invariant: bool = True
    enable_time_stretching: bool = True
    max_time_shift_seconds: float = 5.0
    chromaprint_duration: int = 120
    spectral_window_size: int = 2048
    overlap_ratio: float = 0.5


@dataclass
class VideoMatchingConfig:
    """Video similarity matching configuration."""
    primary_algorithm: MatchingAlgorithm = MatchingAlgorithm.FAISS_HNSW
    fallback_algorithm: MatchingAlgorithm = MatchingAlgorithm.CROSS_CORRELATION
    exact_match_threshold: float = 0.95
    near_duplicate_threshold: float = 0.90
    variant_threshold: float = 0.80
    derivative_threshold: float = 0.65
    frame_comparison_strategy: str = "keyframes"  # all_frames, keyframes, adaptive
    keyframe_extraction_rate: int = 1  # per second
    enable_temporal_alignment: bool = True
    enable_resolution_invariant: bool = True
    enable_crop_detection: bool = True
    max_temporal_shift_seconds: float = 10.0
    motion_sensitivity: float = 0.3


@dataclass
class ImageMatchingConfig:
    """Image similarity matching configuration."""
    primary_algorithm: MatchingAlgorithm = MatchingAlgorithm.FAISS_IVF
    fallback_algorithm: MatchingAlgorithm = MatchingAlgorithm.LOCALITY_SENSITIVE_HASHING
    exact_match_threshold: float = 0.98
    near_duplicate_threshold: float = 0.92
    variant_threshold: float = 0.82
    derivative_threshold: float = 0.68
    enable_rotation_invariant: bool = True
    enable_scale_invariant: bool = True
    enable_color_invariant: bool = False
    enable_crop_detection: bool = True
    perceptual_hash_size: int = 16
    feature_detector: str = "orb"  # orb, sift, surf
    max_features: int = 500
    match_ratio_threshold: float = 0.75


@dataclass
class TextMatchingConfig:
    """Text similarity matching configuration."""
    primary_algorithm: MatchingAlgorithm = MatchingAlgorithm.SIAMESE_NETWORK
    fallback_algorithm: MatchingAlgorithm = MatchingAlgorithm.FUZZY_MATCHING
    exact_match_threshold: float = 0.95
    near_duplicate_threshold: float = 0.88
    variant_threshold: float = 0.75
    derivative_threshold: float = 0.60
    enable_semantic_matching: bool = True
    enable_syntactic_matching: bool = True
    enable_n_gram_analysis: bool = True
    n_gram_size: int = 3
    enable_stemming: bool = True
    enable_lemmatization: bool = True
    ignore_case: bool = True
    ignore_punctuation: bool = True
    min_text_length: int = 20
    max_sequence_length: int = 512


@dataclass
class PerformanceConfig:
    """Performance optimization configuration."""
    max_concurrent_comparisons: int = 100
    batch_size: int = 1000
    enable_parallel_processing: bool = True
    num_workers: int = 8
    memory_limit_gb: int = 16
    timeout_seconds: int = 300
    enable_caching: bool = True
    cache_size_mb: int = 1024
    cache_ttl_hours: int = 24
    enable_result_compression: bool = True
    compression_algorithm: str = "lz4"


@dataclass
class QualityConfig:
    """Quality assurance configuration."""
    enable_confidence_scoring: bool = True
    min_confidence_threshold: float = 0.7
    enable_multi_algorithm_validation: bool = True
    consensus_threshold: float = 0.8
    enable_human_validation: bool = False
    human_validation_threshold: float = 0.9
    enable_false_positive_reduction: bool = True
    enable_duplicate_removal: bool = True
    similarity_variance_threshold: float = 0.1


@dataclass
class AlertConfig:
    """Alert and notification configuration."""
    enable_real_time_alerts: bool = True
    alert_threshold_exact_match: float = 0.98
    alert_threshold_near_duplicate: float = 0.95
    enable_email_notifications: bool = True
    enable_webhook_notifications: bool = True
    enable_dashboard_notifications: bool = True
    notification_cooldown_minutes: int = 15
    batch_alert_enabled: bool = True
    batch_alert_interval_minutes: int = 60


class SimilarityMatchingConfig:
    """
    Professional similarity matching configuration manager.
    Provides industrial-grade configuration for content similarity analysis.
    """
    
    def __init__(self):
        # General matching settings
        self.enable_fuzzy_matching: bool = True
        self.enable_approximate_matching: bool = True
        self.enable_cross_modal_matching: bool = True
        self.matching_precision_mode: str = "balanced"  # performance, balanced, accuracy
        
        # Content type configurations
        self.vector_matching = VectorMatchingConfig()
        self.hash_matching = HashMatchingConfig()
        self.audio = AudioMatchingConfig()
        self.video = VideoMatchingConfig()
        self.image = ImageMatchingConfig()
        self.text = TextMatchingConfig()
        
        # System configurations
        self.performance = PerformanceConfig()
        self.quality = QualityConfig()
        self.alerts = AlertConfig()
        
        # Similarity thresholds by content type
        self.similarity_thresholds: Dict[str, Dict[str, float]] = {
            "audio": {
                "exact_match": 0.98,
                "near_duplicate": 0.95,
                "variant": 0.85,
                "derivative": 0.70
            },
            "video": {
                "exact_match": 0.95,
                "near_duplicate": 0.90,
                "variant": 0.80,
                "derivative": 0.65
            },
            "image": {
                "exact_match": 0.98,
                "near_duplicate": 0.92,
                "variant": 0.82,
                "derivative": 0.68
            },
            "text": {
                "exact_match": 0.95,
                "near_duplicate": 0.88,
                "variant": 0.75,
                "derivative": 0.60
            }
        }
        
        # Load environment configurations
        self._load_from_environment()
    
    def _load_from_environment(self) -> None:
        """Load configuration from environment variables."""
        # General settings
        self.matching_precision_mode = os.getenv("MATCHING_PRECISION_MODE", "balanced")
        self.enable_fuzzy_matching = os.getenv("MATCHING_FUZZY_ENABLED", "true").lower() == "true"
        
        # Vector matching settings
        self.vector_matching.vector_dimension = int(os.getenv("MATCHING_VECTOR_DIMENSION", "512"))
        self.vector_matching.top_k_results = int(os.getenv("MATCHING_TOP_K_RESULTS", "50"))
        
        # Performance settings
        self.performance.max_concurrent_comparisons = int(os.getenv("MATCHING_MAX_CONCURRENT", "100"))
        self.performance.batch_size = int(os.getenv("MATCHING_BATCH_SIZE", "1000"))
        self.performance.num_workers = int(os.getenv("MATCHING_NUM_WORKERS", "8"))
        self.performance.memory_limit_gb = int(os.getenv("MATCHING_MEMORY_LIMIT", "16"))
        
        # Thresholds
        audio_exact = float(os.getenv("MATCHING_AUDIO_EXACT_THRESHOLD", "0.98"))
        self.similarity_thresholds["audio"]["exact_match"] = audio_exact
        
        video_exact = float(os.getenv("MATCHING_VIDEO_EXACT_THRESHOLD", "0.95"))
        self.similarity_thresholds["video"]["exact_match"] = video_exact
        
        image_exact = float(os.getenv("MATCHING_IMAGE_EXACT_THRESHOLD", "0.98"))
        self.similarity_thresholds["image"]["exact_match"] = image_exact
        
        text_exact = float(os.getenv("MATCHING_TEXT_EXACT_THRESHOLD", "0.95"))
        self.similarity_thresholds["text"]["exact_match"] = text_exact
    
    def get_content_config(self, content_type: str) -> Dict[str, Any]:
        """Get matching configuration for specific content type."""
        content_configs = {
            "audio": self.audio,
            "video": self.video,
            "image": self.image,
            "text": self.text
        }
        
        config = content_configs.get(content_type.lower())
        if not config:
            raise ValueError(f"Unsupported content type: {content_type}")
        
        return {
            "content_type": content_type,
            "content_config": config.__dict__,
            "thresholds": self.similarity_thresholds.get(content_type, {}),
            "vector_matching": self.vector_matching.__dict__,
            "performance": self.performance.__dict__,
            "quality": self.quality.__dict__
        }
    
    def get_algorithm_config(self, algorithm: MatchingAlgorithm) -> Dict[str, Any]:
        """Get configuration for specific matching algorithm."""
        algorithm_configs = {
            # Vector algorithms
            MatchingAlgorithm.FAISS_IVF: {
                "index_type": self.vector_matching.index_type,
                "nprobe": self.vector_matching.nprobe,
                "num_clusters": self.vector_matching.num_clusters,
                "similarity_metric": self.vector_matching.similarity_metric
            },
            MatchingAlgorithm.FAISS_HNSW: {
                "M": 16,  # HNSW connectivity
                "efConstruction": 200,
                "efSearch": 100,
                "similarity_metric": self.vector_matching.similarity_metric
            },
            MatchingAlgorithm.ANNOY: {
                "n_trees": 100,
                "search_k": self.vector_matching.search_k,
                "metric": "angular" if self.vector_matching.similarity_metric == SimilarityMetric.COSINE else "euclidean"
            },
            
            # Hash algorithms
            MatchingAlgorithm.LOCALITY_SENSITIVE_HASHING: {
                "hash_size": self.hash_matching.hash_size,
                "num_hash_tables": self.hash_matching.num_hash_tables,
                "hash_family": self.hash_matching.hash_family
            },
            MatchingAlgorithm.MINHASH: {
                "num_perm": self.hash_matching.signature_length,
                "threshold": 0.8
            },
            MatchingAlgorithm.SIMHASH: {
                "hash_bits": self.hash_matching.hash_size,
                "distance_threshold": 3
            },
            
            # ML algorithms
            MatchingAlgorithm.SIAMESE_NETWORK: {
                "embedding_dimension": 128,
                "margin": 1.0,
                "learning_rate": 0.001
            },
            MatchingAlgorithm.CONTRASTIVE_LEARNING: {
                "temperature": 0.07,
                "embedding_dimension": 256
            },
            MatchingAlgorithm.TRIPLET_LOSS: {
                "margin": 0.5,
                "embedding_dimension": 128
            }
        }
        
        return algorithm_configs.get(algorithm, {})
    
    def get_similarity_type(self, similarity_score: float, content_type: str) -> ContentSimilarityType:
        """Determine similarity type based on score and content type."""
        thresholds = self.similarity_thresholds.get(content_type, {})
        
        if similarity_score >= thresholds.get("exact_match", 0.98):
            return ContentSimilarityType.EXACT_MATCH
        elif similarity_score >= thresholds.get("near_duplicate", 0.95):
            return ContentSimilarityType.NEAR_DUPLICATE
        elif similarity_score >= thresholds.get("variant", 0.85):
            return ContentSimilarityType.VARIANT
        elif similarity_score >= thresholds.get("derivative", 0.70):
            return ContentSimilarityType.DERIVATIVE
        elif similarity_score >= 0.40:
            return ContentSimilarityType.INSPIRED
        else:
            return ContentSimilarityType.UNRELATED
    
    def should_trigger_alert(self, similarity_score: float, content_type: str) -> bool:
        """Determine if similarity score should trigger an alert."""
        if not self.alerts.enable_real_time_alerts:
            return False
        
        if similarity_score >= self.alerts.alert_threshold_exact_match:
            return True
        
        if similarity_score >= self.alerts.alert_threshold_near_duplicate:
            return True
        
        return False
    
    def optimize_for_performance(self) -> None:
        """Optimize configuration for maximum performance."""
        self.matching_precision_mode = "performance"
        
        # Use faster algorithms
        self.audio.primary_algorithm = MatchingAlgorithm.LOCALITY_SENSITIVE_HASHING
        self.video.primary_algorithm = MatchingAlgorithm.LOCALITY_SENSITIVE_HASHING
        self.image.primary_algorithm = MatchingAlgorithm.LOCALITY_SENSITIVE_HASHING
        self.text.primary_algorithm = MatchingAlgorithm.FUZZY_MATCHING
        
        # Increase batch sizes
        self.performance.batch_size = 2000
        self.performance.max_concurrent_comparisons = 200
        
        # Reduce precision slightly
        self.vector_matching.nprobe = 16
        self.vector_matching.search_k = 50
    
    def optimize_for_accuracy(self) -> None:
        """Optimize configuration for maximum accuracy."""
        self.matching_precision_mode = "accuracy"
        
        # Use most accurate algorithms
        self.audio.primary_algorithm = MatchingAlgorithm.SIAMESE_NETWORK
        self.video.primary_algorithm = MatchingAlgorithm.SIAMESE_NETWORK
        self.image.primary_algorithm = MatchingAlgorithm.SIAMESE_NETWORK
        self.text.primary_algorithm = MatchingAlgorithm.SIAMESE_NETWORK
        
        # Enable quality features
        self.quality.enable_multi_algorithm_validation = True
        self.quality.enable_false_positive_reduction = True
        
        # Increase precision
        self.vector_matching.nprobe = 64
        self.vector_matching.search_k = 200
    
    def set_similarity_thresholds(self, content_type: str, thresholds: Dict[str, float]) -> None:
        """Set custom similarity thresholds for content type."""
        if content_type not in self.similarity_thresholds:
            raise ValueError(f"Unsupported content type: {content_type}")
        
        # Validate threshold values
        required_keys = ["exact_match", "near_duplicate", "variant", "derivative"]
        for key in required_keys:
            if key not in thresholds:
                raise ValueError(f"Missing threshold: {key}")
            
            if not 0.0 <= thresholds[key] <= 1.0:
                raise ValueError(f"Threshold {key} must be between 0.0 and 1.0")
        
        # Validate threshold ordering
        if not (thresholds["exact_match"] >= thresholds["near_duplicate"] >= 
                thresholds["variant"] >= thresholds["derivative"]):
            raise ValueError("Thresholds must be in descending order")
        
        self.similarity_thresholds[content_type] = thresholds
    
    def validate_configuration(self) -> List[str]:
        """Validate current configuration and return any issues."""
        issues = []
        
        # Validate performance settings
        if self.performance.max_concurrent_comparisons <= 0:
            issues.append("Max concurrent comparisons must be positive")
        
        if self.performance.batch_size <= 0:
            issues.append("Batch size must be positive")
        
        if self.performance.num_workers <= 0:
            issues.append("Number of workers must be positive")
        
        if self.performance.memory_limit_gb <= 0:
            issues.append("Memory limit must be positive")
        
        # Validate vector matching settings
        if self.vector_matching.vector_dimension <= 0:
            issues.append("Vector dimension must be positive")
        
        if self.vector_matching.top_k_results <= 0:
            issues.append("Top K results must be positive")
        
        # Validate thresholds for each content type
        for content_type, thresholds in self.similarity_thresholds.items():
            for threshold_name, threshold_value in thresholds.items():
                if not 0.0 <= threshold_value <= 1.0:
                    issues.append(f"{content_type} {threshold_name} threshold must be between 0.0 and 1.0")
        
        # Validate alert settings
        if self.alerts.enable_real_time_alerts:
            if not 0.0 <= self.alerts.alert_threshold_exact_match <= 1.0:
                issues.append("Alert threshold for exact match must be between 0.0 and 1.0")
            
            if not 0.0 <= self.alerts.alert_threshold_near_duplicate <= 1.0:
                issues.append("Alert threshold for near duplicate must be between 0.0 and 1.0")
        
        return issues
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "enable_fuzzy_matching": self.enable_fuzzy_matching,
            "enable_approximate_matching": self.enable_approximate_matching,
            "enable_cross_modal_matching": self.enable_cross_modal_matching,
            "matching_precision_mode": self.matching_precision_mode,
            "similarity_thresholds": self.similarity_thresholds,
            "vector_matching": self.vector_matching.__dict__,
            "hash_matching": self.hash_matching.__dict__,
            "audio": self.audio.__dict__,
            "video": self.video.__dict__,
            "image": self.image.__dict__,
            "text": self.text.__dict__,
            "performance": self.performance.__dict__,
            "quality": self.quality.__dict__,
            "alerts": self.alerts.__dict__
        }
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'SimilarityMatchingConfig':
        """Create configuration from dictionary."""
        config = cls()
        
        # Load basic settings
        basic_fields = [
            "enable_fuzzy_matching", "enable_approximate_matching",
            "enable_cross_modal_matching", "matching_precision_mode"
        ]
        
        for field in basic_fields:
            if field in config_dict:
                setattr(config, field, config_dict[field])
        
        # Load similarity thresholds
        if "similarity_thresholds" in config_dict:
            config.similarity_thresholds = config_dict["similarity_thresholds"]
        
        # Load component configurations
        component_map = {
            "vector_matching": config.vector_matching,
            "hash_matching": config.hash_matching,
            "audio": config.audio,
            "video": config.video,
            "image": config.image,
            "text": config.text,
            "performance": config.performance,
            "quality": config.quality,
            "alerts": config.alerts
        }
        
        for key, component in component_map.items():
            if key in config_dict:
                for attr_key, attr_value in config_dict[key].items():
                    setattr(component, attr_key, attr_value)
        
        return config
