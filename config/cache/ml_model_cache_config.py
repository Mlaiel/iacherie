"""ML Model Cache Configuration for IA-Influencer Agent Platform
============================================================

Professional caching system for AI/ML models used in content protection,
audio analysis, recommendation engines, and revenue prediction models.

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
import pickle
from datetime import datetime, timedelta
from pydantic import BaseModel, validator


class ModelType(str, Enum):
    """Types of ML models used in the platform"""    # Audio processing models
    AUDIO_FINGERPRINT = "audio_fingerprint"
    MUSIC_GENRE_CLASSIFICATION = "music_genre_classification"
    AUDIO_QUALITY_ASSESSMENT = "audio_quality_assessment"
    SPECTRAL_ANALYSIS = "spectral_analysis"
    
    # Video processing models
    VIDEO_FINGERPRINT = "video_fingerprint" 
    CONTENT_MODERATION = "content_moderation"
    SCENE_DETECTION = "scene_detection"
    
    # Image processing models
    IMAGE_FINGERPRINT = "image_fingerprint"
    CLIP_EMBEDDINGS = "clip_embeddings"
    PERCEPTUAL_HASH = "perceptual_hash"
    
    # Text processing models
    TEXT_FINGERPRINT = "text_fingerprint"
    BERT_EMBEDDINGS = "bert_embeddings"
    SENTIMENT_ANALYSIS = "sentiment_analysis"
    CONTENT_SIMILARITY = "content_similarity"
    
    # Recommendation models
    COLLABORATIVE_FILTERING = "collaborative_filtering"
    CONTENT_BASED_FILTERING = "content_based_filtering"
    HYBRID_RECOMMENDATION = "hybrid_recommendation"
    
    # Revenue prediction models
    REVENUE_FORECASTING = "revenue_forecasting"
    ENGAGEMENT_PREDICTION = "engagement_prediction"
    MARKET_ANALYSIS = "market_analysis"


class ModelFormat(str, Enum):
    """Model serialization formats"""    PYTORCH = "pytorch"
    TENSORFLOW = "tensorflow"
    ONNX = "onnx"
    SCIKIT_LEARN = "scikit_learn"
    HUGGING_FACE = "hugging_face"
    PICKLE = "pickle"
    JOBLIB = "joblib"


class CacheStrategy(str, Enum):
    """Model cache strategies"""    LAZY_LOADING = "lazy_loading"        # Load on first use
    EAGER_LOADING = "eager_loading"      # Preload all models
    SCHEDULED_LOADING = "scheduled_loading"  # Load based on schedule
    DEMAND_BASED = "demand_based"        # Load based on usage patterns


@dataclass
class ModelCacheSettings:
    """Cache settings for individual ML models"""    model_type: ModelType
    model_format: ModelFormat
    model_version: str
    model_size_mb: float
    memory_requirements_mb: int
    gpu_required: bool = False
    ttl_hours: int = 24
    priority: int = 1  # 1=highest, 5=lowest
    warmup_required: bool = False
    warmup_time_seconds: int = 0
    auto_refresh: bool = True
    refresh_interval_hours: int = 24


@dataclass
class MLModelCacheConfig:
    """Complete configuration for ML model caching"""    
    # Cache identification
    cache_name: str = "ml_models"
    namespace: str = "ia_influencer_ml"
    tenant_id: Optional[str] = None
    
    # Storage configuration
    redis_key_prefix: str = "ml_model"
    model_storage_path: str = "/models"
    temp_storage_path: str = "/tmp/models"
    
    # Memory management
    max_memory_usage_mb: int = 4096  # 4GB default
    max_models_in_memory: int = 50
    memory_cleanup_threshold: float = 0.85
    memory_check_interval_seconds: int = 300  # 5 minutes
    
    # Performance settings
    model_loading_timeout_seconds: int = 300  # 5 minutes
    concurrent_loading_limit: int = 3
    cache_strategy: CacheStrategy = CacheStrategy.DEMAND_BASED
    preload_popular_models: bool = True
    
    # Model configurations by type
    audio_models: Dict[str, ModelCacheSettings] = field(default_factory=lambda: {
        "chromaprint": ModelCacheSettings(
            model_type=ModelType.AUDIO_FINGERPRINT,
            model_format=ModelFormat.PYTORCH,
            model_version="1.0.0",
            model_size_mb=45.2,
            memory_requirements_mb=128,
            gpu_required=False,
            ttl_hours=48,
            priority=1,
            warmup_required=True,
            warmup_time_seconds=30
        ),
        "genre_classifier": ModelCacheSettings(
            model_type=ModelType.MUSIC_GENRE_CLASSIFICATION,
            model_format=ModelFormat.TENSORFLOW,
            model_version="2.1.0",
            model_size_mb=89.7,
            memory_requirements_mb=256,
            gpu_required=True,
            ttl_hours=24,
            priority=2,
            warmup_required=True,
            warmup_time_seconds=45
        )
    })
    
    video_models: Dict[str, ModelCacheSettings] = field(default_factory=lambda: {
        "video_fingerprint": ModelCacheSettings(
            model_type=ModelType.VIDEO_FINGERPRINT,
            model_format=ModelFormat.ONNX,
            model_version="1.2.0",
            model_size_mb=156.8,
            memory_requirements_mb=512,
            gpu_required=True,
            ttl_hours=24,
            priority=2,
            warmup_required=True,
            warmup_time_seconds=60
        )
    })
    
    text_models: Dict[str, ModelCacheSettings] = field(default_factory=lambda: {
        "bert_embeddings": ModelCacheSettings(
            model_type=ModelType.BERT_EMBEDDINGS,
            model_format=ModelFormat.HUGGING_FACE,
            model_version="bert-base-multilingual",
            model_size_mb=681.2,
            memory_requirements_mb=1024,
            gpu_required=True,
            ttl_hours=48,
            priority=1,
            warmup_required=True,
            warmup_time_seconds=90
        )
    })
    
    recommendation_models: Dict[str, ModelCacheSettings] = field(default_factory=lambda: {
        "collaborative_filter": ModelCacheSettings(
            model_type=ModelType.COLLABORATIVE_FILTERING,
            model_format=ModelFormat.SCIKIT_LEARN,
            model_version="1.0.3",
            model_size_mb=23.4,
            memory_requirements_mb=64,
            gpu_required=False,
            ttl_hours=12,
            priority=3,
            warmup_required=False
        )
    })
    
    revenue_models: Dict[str, ModelCacheSettings] = field(default_factory=lambda: {
        "revenue_forecaster": ModelCacheSettings(
            model_type=ModelType.REVENUE_FORECASTING,
            model_format=ModelFormat.PYTORCH,
            model_version="2.0.1",
            model_size_mb=67.3,
            memory_requirements_mb=192,
            gpu_required=True,
            ttl_hours=6,  # Shorter TTL for revenue models
            priority=1,
            warmup_required=True,
            warmup_time_seconds=40,
            auto_refresh=True,
            refresh_interval_hours=4
        )
    })
    
    # Security and access control
    encryption_enabled: bool = True
    access_control_enabled: bool = True
    model_integrity_check: bool = True
    audit_model_usage: bool = True
    
    # Monitoring and metrics
    metrics_enabled: bool = True
    performance_monitoring: bool = True
    usage_analytics: bool = True
    alert_thresholds: Dict[str, Any] = field(default_factory=lambda: {
        "memory_usage_max": 0.90,
        "loading_time_max_seconds": 120,
        "cache_miss_rate_max": 0.15,
        "model_accuracy_min": 0.85,
        "inference_time_max_ms": 500
    })

    def get_cache_key(self, model_name: str, model_type: ModelType, version: str) -> str:
        """Generate standardized cache key for ML model"""        key_components = [
            self.redis_key_prefix,
            self.namespace,
            model_type.value,
            model_name,
            version
        ]
        if self.tenant_id:
            key_components.insert(-2, self.tenant_id)
        return ":".join(key_components)
    
    def get_all_models(self) -> Dict[str, ModelCacheSettings]:
        """Get all configured models"""        all_models = {}
        all_models.update(self.audio_models)
        all_models.update(self.video_models)
        all_models.update(self.text_models)
        all_models.update(self.recommendation_models)
        all_models.update(self.revenue_models)
        return all_models
    
    def get_high_priority_models(self) -> List[str]:
        """Get list of high priority models (priority 1-2)"""        high_priority = []
        for name, settings in self.get_all_models().items():
            if settings.priority <= 2:
                high_priority.append(name)
        return high_priority


class MLModelCacheManager:
    """Manager for ML model cache operations"""    
    def __init__(self, config: MLModelCacheConfig):
        self.config = config
        self._loaded_models = {}
        self._model_metadata = {}
        self._performance_metrics = {}
    
    def calculate_memory_usage(self) -> Dict[str, float]:
        """Calculate current memory usage of cached models"""        total_memory_mb = 0
        memory_by_type = {}
        
        for model_name, settings in self.config.get_all_models().items():
            if model_name in self._loaded_models:
                memory_by_type[settings.model_type.value] = (
                    memory_by_type.get(settings.model_type.value, 0) + 
                    settings.memory_requirements_mb
                )
                total_memory_mb += settings.memory_requirements_mb
        
        return {
            "total_memory_mb": total_memory_mb,
            "memory_by_type": memory_by_type,
            "memory_utilization": total_memory_mb / self.config.max_memory_usage_mb,
            "available_memory_mb": self.config.max_memory_usage_mb - total_memory_mb
        }
    
    def get_model_load_priority(self) -> List[tuple]:
        """Get models ordered by loading priority"""        models = []
        for name, settings in self.config.get_all_models().items():
            models.append((name, settings.priority, settings.memory_requirements_mb))
        
        # Sort by priority (lower number = higher priority), then by memory usage
        return sorted(models, key=lambda x: (x[1], -x[2]))
    
    def generate_model_hash(self, model_path: str, model_version: str) -> str:
        """Generate hash for model integrity verification"""        hasher = hashlib.sha256()
        hasher.update(model_path.encode())
        hasher.update(model_version.encode())
        hasher.update(str(datetime.now().date()).encode())  # Include date for versioning
        return hasher.hexdigest()
    
    def get_cache_statistics(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics"""        memory_usage = self.calculate_memory_usage()
        
        return {
            "loaded_models_count": len(self._loaded_models),
            "total_configured_models": len(self.config.get_all_models()),
            "memory_usage": memory_usage,
            "cache_hit_rate": self._performance_metrics.get("cache_hit_rate", 0.0),
            "avg_loading_time_seconds": self._performance_metrics.get("avg_loading_time", 0.0),
            "models_by_priority": self._get_models_by_priority(),
            "gpu_models_count": self._count_gpu_models(),
            "last_cleanup_time": self._performance_metrics.get("last_cleanup_time"),
        }
    
    def _get_models_by_priority(self) -> Dict[int, int]:
        """Count models by priority level"""        priority_counts = {}
        for settings in self.config.get_all_models().values():
            priority_counts[settings.priority] = priority_counts.get(settings.priority, 0) + 1
        return priority_counts
    
    def _count_gpu_models(self) -> int:
        """Count models that require GPU"""        return sum(1 for settings in self.config.get_all_models().values() 
                  if settings.gpu_required)


# Environment-specific configurations
DEVELOPMENT_CONFIG = MLModelCacheConfig(
    cache_name="dev_ml_models",
    max_memory_usage_mb=1024,  # 1GB for dev
    max_models_in_memory=10,
    cache_strategy=CacheStrategy.LAZY_LOADING,
    preload_popular_models=False,
    encryption_enabled=False,
    performance_monitoring=False
)

TESTING_CONFIG = MLModelCacheConfig(
    cache_name="test_ml_models",
    max_memory_usage_mb=512,  # 512MB for tests
    max_models_in_memory=5,
    cache_strategy=CacheStrategy.LAZY_LOADING,
    preload_popular_models=False,
    encryption_enabled=False,
    audit_model_usage=False,
    metrics_enabled=False
)

PRODUCTION_CONFIG = MLModelCacheConfig(
    cache_name="prod_ml_models",
    max_memory_usage_mb=16384,  # 16GB for production
    max_models_in_memory=100,
    cache_strategy=CacheStrategy.DEMAND_BASED,
    preload_popular_models=True,
    encryption_enabled=True,
    audit_model_usage=True,
    performance_monitoring=True,
    model_integrity_check=True
)

# Export main classes
__all__ = [
    'ModelType',
    'ModelFormat',
    'CacheStrategy',
    'ModelCacheSettings',
    'MLModelCacheConfig',
    'MLModelCacheManager',
    'DEVELOPMENT_CONFIG',
    'TESTING_CONFIG',
    'PRODUCTION_CONFIG'
]
