"""
Content Fingerprint Cache Configuration for IA-Influencer Agent Platform
=======================================================================

Professional caching system specifically designed for AI-generated content fingerprints
supporting audio, video, image, and text content protection with high-performance retrieval.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA-Influencer Agent + Content Protection Platform
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps

Copyright Notice:
This code is the intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution of this code
without explicit written permission from the author is strictly prohibited.

Contact: mlaiel@live.de for licensing inquiries.
"""

from typing import Dict, Optional, List, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import hashlib
from pydantic import BaseModel, validator


class ContentType(str, Enum):
    """Supported content types for fingerprinting"""
    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image" 
    TEXT = "text"
    MIXED = "mixed"


class FingerprintAlgorithm(str, Enum):
    """Fingerprinting algorithms by content type"""
    # Audio algorithms
    CHROMAPRINT = "chromaprint"
    ESSENTIA = "essentia"
    SPECTRAL_HASH = "spectral_hash"
    
    # Video algorithms  
    PHASH = "phash"
    OPENCV_FEATURES = "opencv_features"
    YOLO_FRAMES = "yolo_frames"
    
    # Image algorithms
    CLIP_VECTORS = "clip_vectors"
    IMAGE_HASH = "image_hash"
    PERCEPTUAL_HASH = "perceptual_hash"
    
    # Text algorithms
    BERT_VECTORS = "bert_vectors"
    ROBERTA_VECTORS = "roberta_vectors"
    TF_IDF = "tf_idf"


class CacheStorageMode(str, Enum):
    """Storage modes for fingerprint data"""
    MEMORY_ONLY = "memory_only"
    PERSISTENT = "persistent"  
    HYBRID = "hybrid"
    DISTRIBUTED = "distributed"


@dataclass 
class FingerprintCacheSettings:
    """Core fingerprint cache settings"""
    content_type: ContentType
    algorithm: FingerprintAlgorithm
    ttl_seconds: int = 86400  # 24 hours default
    max_fingerprint_size: int = 1048576  # 1MB max per fingerprint
    compression_enabled: bool = True
    encryption_enabled: bool = True
    similarity_threshold: float = 0.85
    batch_processing_size: int = 100
    priority_level: int = 1  # 1=highest, 5=lowest


@dataclass
class ContentFingerprintCacheConfig:
    """Complete configuration for content fingerprint caching"""
    
    # Cache identification
    cache_name: str = "content_fingerprints"
    tenant_id: Optional[str] = None
    user_id: Optional[str] = None
    
    # Storage configuration
    storage_mode: CacheStorageMode = CacheStorageMode.HYBRID
    redis_key_prefix: str = "fingerprint"
    namespace: str = "ia_influencer"
    
    # Performance settings
    max_cache_size_mb: int = 1024  # 1GB default
    max_entries_per_type: int = 100000
    cleanup_interval_seconds: int = 3600  # 1 hour
    memory_threshold_percent: int = 80
    
    # Content type specific settings
    audio_settings: FingerprintCacheSettings = field(
        default_factory=lambda: FingerprintCacheSettings(
            content_type=ContentType.AUDIO,
            algorithm=FingerprintAlgorithm.CHROMAPRINT,
            ttl_seconds=172800,  # 48 hours for audio
            max_fingerprint_size=2097152,  # 2MB for audio
            similarity_threshold=0.95,
            priority_level=1
        )
    )
    
    video_settings: FingerprintCacheSettings = field(
        default_factory=lambda: FingerprintCacheSettings(
            content_type=ContentType.VIDEO,
            algorithm=FingerprintAlgorithm.PHASH,
            ttl_seconds=86400,  # 24 hours for video
            max_fingerprint_size=5242880,  # 5MB for video
            similarity_threshold=0.90,
            priority_level=2
        )
    )
    
    image_settings: FingerprintCacheSettings = field(
        default_factory=lambda: FingerprintCacheSettings(
            content_type=ContentType.IMAGE,
            algorithm=FingerprintAlgorithm.CLIP_VECTORS,
            ttl_seconds=86400,  # 24 hours for images
            max_fingerprint_size=524288,  # 512KB for images
            similarity_threshold=0.92,
            priority_level=2
        )
    )
    
    text_settings: FingerprintCacheSettings = field(
        default_factory=lambda: FingerprintCacheSettings(
            content_type=ContentType.TEXT,
            algorithm=FingerprintAlgorithm.BERT_VECTORS,
            ttl_seconds=43200,  # 12 hours for text
            max_fingerprint_size=131072,  # 128KB for text
            similarity_threshold=0.88,
            priority_level=3
        )
    )
    
    # Security and encryption
    encryption_key: Optional[str] = None
    access_control_enabled: bool = True
    audit_logging_enabled: bool = True
    
    # Monitoring and metrics
    metrics_enabled: bool = True
    performance_monitoring: bool = True
    alert_thresholds: Dict[str, float] = field(default_factory=lambda: {
        "cache_hit_rate_min": 0.85,
        "memory_usage_max": 0.90,
        "response_time_max_ms": 100,
        "error_rate_max": 0.01
    })

    def get_cache_key(self, content_hash: str, content_type: ContentType, user_id: str) -> str:
        """Generate standardized cache key for fingerprint"""
        key_components = [
            self.redis_key_prefix,
            self.namespace,
            content_type.value,
            user_id if self.tenant_id is None else self.tenant_id,
            content_hash
        ]
        return ":".join(key_components)
    
    def get_settings_for_content_type(self, content_type: ContentType) -> FingerprintCacheSettings:
        """Get cache settings for specific content type"""
        settings_map = {
            ContentType.AUDIO: self.audio_settings,
            ContentType.VIDEO: self.video_settings,
            ContentType.IMAGE: self.image_settings,
            ContentType.TEXT: self.text_settings
        }
        return settings_map.get(content_type, self.audio_settings)


class FingerprintCacheManager:
    """Manager for fingerprint cache operations"""
    
    def __init__(self, config: ContentFingerprintCacheConfig):
        self.config = config
        self._performance_metrics = {}
    
    def generate_content_hash(self, content_data: bytes, content_type: ContentType) -> str:
        """Generate consistent hash for content identification"""
        hasher = hashlib.sha256()
        hasher.update(content_type.value.encode())
        hasher.update(content_data)
        return hasher.hexdigest()
    
    def validate_fingerprint_size(self, fingerprint_data: bytes, content_type: ContentType) -> bool:
        """Validate fingerprint size against content type limits"""
        settings = self.config.get_settings_for_content_type(content_type)
        return len(fingerprint_data) <= settings.max_fingerprint_size
    
    def get_cache_metrics(self) -> Dict[str, Any]:
        """Get current cache performance metrics"""



        return {
            "cache_size_mb": self._performance_metrics.get("cache_size_mb", 0),
            "hit_rate": self._performance_metrics.get("hit_rate", 0.0),
            "miss_rate": self._performance_metrics.get("miss_rate", 0.0),
            "avg_response_time_ms": self._performance_metrics.get("avg_response_time_ms", 0),
            "total_fingerprints": self._performance_metrics.get("total_fingerprints", 0),
            "fingerprints_by_type": self._performance_metrics.get("fingerprints_by_type", {})
        }


# Environment-specific configurations
DEVELOPMENT_CONFIG = ContentFingerprintCacheConfig(
    cache_name="dev_content_fingerprints",
    storage_mode=CacheStorageMode.MEMORY_ONLY,
    max_cache_size_mb=256,  # Smaller for dev
    max_entries_per_type=10000,
    cleanup_interval_seconds=1800,  # 30 minutes
    metrics_enabled=True,
    performance_monitoring=False,  # Disabled for dev
    encryption_enabled=False  # Disabled for dev
)

TESTING_CONFIG = ContentFingerprintCacheConfig(
    cache_name="test_content_fingerprints", 
    storage_mode=CacheStorageMode.MEMORY_ONLY,
    max_cache_size_mb=128,  # Minimal for tests
    max_entries_per_type=1000,
    cleanup_interval_seconds=300,  # 5 minutes
    metrics_enabled=False,
    performance_monitoring=False,
    encryption_enabled=False,
    audit_logging_enabled=False
)

PRODUCTION_CONFIG = ContentFingerprintCacheConfig(
    cache_name="prod_content_fingerprints",
    storage_mode=CacheStorageMode.DISTRIBUTED,
    max_cache_size_mb=8192,  # 8GB for production
    max_entries_per_type=1000000,  # 1M fingerprints per type
    cleanup_interval_seconds=3600,  # 1 hour
    metrics_enabled=True,
    performance_monitoring=True,
    encryption_enabled=True,
    audit_logging_enabled=True,
    access_control_enabled=True
)

# Export main classes
__all__ = [
    'ContentType',
    'FingerprintAlgorithm', 
    'CacheStorageMode',
    'FingerprintCacheSettings',
    'ContentFingerprintCacheConfig',
    'FingerprintCacheManager',
    'DEVELOPMENT_CONFIG',
    'TESTING_CONFIG', 
    'PRODUCTION_CONFIG'
]
