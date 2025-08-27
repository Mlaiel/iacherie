"""
Vector Database System Constants and Configuration Values
========================================================

Centralized constants, enums, and configuration values for the vector database system.
This module defines all fixed values, thresholds, and system-wide configurations.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel - All Rights Reserved

⚠️ COPYRIGHT WARNING ⚠️
This code is protected by copyright law. Any unauthorized reproduction, distribution, 
modification, or use of this code without explicit written permission from 
Fahed Mlaiel (mlaiel@live.de) is strictly prohibited and will result in legal action.

For licensing and authorization requests, contact: mlaiel@live.de

TEAM SPECIALTIES:
- Lead AI Developer + Backend Senior Engineer: Fahed Mlaiel
- ML Engineer + Data Scientist: Advanced algorithms & optimization
- Database Administrator + Performance Specialist: Scalability & efficiency  
- Security Engineer + DevOps Engineer: System security & deployment
- Audio Processing Specialist: Audio fingerprinting & analysis
- Computer Vision Engineer: Image/video processing & recognition
- Microservices Architect: Distributed systems & API design
"""

from enum import Enum, IntEnum
from typing import Dict, List, Tuple, Any, Final

# ================================
# SYSTEM METADATA
# ================================

SYSTEM_NAME: Final[str] = "IA Influencer Agent Vector Database System"
SYSTEM_VERSION: Final[str] = "1.0.0"
SYSTEM_AUTHOR: Final[str] = "Fahed Mlaiel"
SYSTEM_EMAIL: Final[str] = "mlaiel@live.de"
SYSTEM_COPYRIGHT: Final[str] = "© 2025 Fahed Mlaiel - All Rights Reserved"
SYSTEM_LICENSE: Final[str] = "Proprietary - Unauthorized use prohibited"

# ================================
# CONTENT TYPE DEFINITIONS
# ================================

class ContentType(Enum):
    """Supported content types for vector database."""
    TEXT = "text"
    AUDIO = "audio"
    IMAGE = "image"
    VIDEO = "video"
    MULTIMODAL = "multimodal"


class AudioFormat(Enum):
    """Supported audio formats."""
    WAV = "wav"
    MP3 = "mp3"
    FLAC = "flac"
    AAC = "aac"
    OGG = "ogg"


class ImageFormat(Enum):
    """Supported image formats."""
    JPEG = "jpeg"
    PNG = "png"
    GIF = "gif"
    BMP = "bmp"
    TIFF = "tiff"
    WEBP = "webp"


class VideoFormat(Enum):
    """Supported video formats."""
    MP4 = "mp4"
    AVI = "avi"
    MOV = "mov"
    MKV = "mkv"
    WEBM = "webm"
    FLV = "flv"


# ================================
# BACKEND CONFIGURATIONS
# ================================

class BackendType(Enum):
    """Vector database backend types."""
    FAISS = "faiss"
    CHROMA = "chroma"
    PINECONE = "pinecone"
    WEAVIATE = "weaviate"
    QDRANT = "qdrant"


class FAISSIndexType(Enum):
    """FAISS index types."""
    FLAT = "flat"
    IVF_FLAT = "ivf_flat"
    IVF_PQ = "ivf_pq"
    HNSW = "hnsw"
    LSH = "lsh"


class DistanceMetric(Enum):
    """Distance metrics for similarity computation."""
    COSINE = "cosine"
    EUCLIDEAN = "euclidean"
    DOT_PRODUCT = "dot_product"
    MANHATTAN = "manhattan"
    HAMMING = "hamming"


# ================================
# EMBEDDING MODEL CONFIGURATIONS
# ================================

# Text Embedding Models
TEXT_EMBEDDING_MODELS: Final[Dict[str, Dict[str, Any]]] = {
    "all-MiniLM-L6-v2": {
        "dimension": 384,
        "max_length": 512,
        "language": "multilingual",
        "performance": "fast",
        "quality": "good"
    },
    "all-mpnet-base-v2": {
        "dimension": 768,
        "max_length": 512,
        "language": "english",
        "performance": "medium",
        "quality": "excellent"
    },
    "paraphrase-multilingual-MiniLM-L12-v2": {
        "dimension": 384,
        "max_length": 512,
        "language": "multilingual",
        "performance": "fast",
        "quality": "good"
    },
    "distilbert-base-nli-stsb-mean-tokens": {
        "dimension": 768,
        "max_length": 512,
        "language": "english",
        "performance": "medium",
        "quality": "very_good"
    }
}

# Audio Processing Parameters
AUDIO_PROCESSING_PARAMS: Final[Dict[str, Any]] = {
    "sample_rates": [8000, 16000, 22050, 44100, 48000],
    "default_sample_rate": 22050,
    "max_duration_seconds": 600,  # 10 minutes
    "min_duration_seconds": 0.1,
    "n_mfcc": 13,
    "n_chroma": 12,
    "n_mel": 128,
    "hop_length": 512,
    "win_length": 2048,
    "window": "hann"
}

# Image Processing Parameters
IMAGE_PROCESSING_PARAMS: Final[Dict[str, Any]] = {
    "default_size": (224, 224),
    "supported_sizes": [(224, 224), (256, 256), (512, 512)],
    "max_size": (4096, 4096),
    "min_size": (32, 32),
    "channels": [1, 3, 4],  # Grayscale, RGB, RGBA
    "color_modes": ["L", "RGB", "RGBA", "CMYK"]
}

# Video Processing Parameters
VIDEO_PROCESSING_PARAMS: Final[Dict[str, Any]] = {
    "max_frames": 100,
    "default_fps": 30,
    "frame_size": (224, 224),
    "max_duration_seconds": 3600,  # 1 hour
    "min_duration_seconds": 1.0,
    "supported_codecs": ["h264", "h265", "vp9", "av1"]
}

# ================================
# SIMILARITY AND SEARCH THRESHOLDS
# ================================

# Default Similarity Thresholds
DEFAULT_SIMILARITY_THRESHOLDS: Final[Dict[str, float]] = {
    ContentType.TEXT.value: 0.70,
    ContentType.AUDIO.value: 0.85,
    ContentType.IMAGE.value: 0.75,
    ContentType.VIDEO.value: 0.80,
    ContentType.MULTIMODAL.value: 0.75
}

# Duplicate Detection Thresholds
DUPLICATE_DETECTION_THRESHOLDS: Final[Dict[str, float]] = {
    ContentType.TEXT.value: 0.90,
    ContentType.AUDIO.value: 0.95,
    ContentType.IMAGE.value: 0.90,
    ContentType.VIDEO.value: 0.92,
    ContentType.MULTIMODAL.value: 0.88
}

# Search Result Limits
SEARCH_RESULT_LIMITS: Final[Dict[str, int]] = {
    "default_max_results": 100,
    "max_max_results": 1000,
    "min_max_results": 1,
    "recommended_max_results": 50
}

# ================================
# PERFORMANCE AND OPTIMIZATION
# ================================

# Memory Limits (in MB)
MEMORY_LIMITS: Final[Dict[str, int]] = {
    "max_vector_cache_mb": 1024,  # 1GB
    "max_metadata_cache_mb": 256,  # 256MB
    "max_embedding_batch_mb": 512,  # 512MB
    "warning_memory_usage_mb": 2048,  # 2GB
    "critical_memory_usage_mb": 4096  # 4GB
}

# Processing Batch Sizes
BATCH_SIZES: Final[Dict[str, int]] = {
    "text_embedding_batch": 32,
    "audio_processing_batch": 8,
    "image_processing_batch": 16,
    "video_processing_batch": 4,
    "similarity_search_batch": 64,
    "indexing_batch": 100
}

# Timeout Values (in seconds)
TIMEOUT_VALUES: Final[Dict[str, float]] = {
    "embedding_generation": 30.0,
    "similarity_search": 10.0,
    "index_building": 300.0,  # 5 minutes
    "backup_operation": 1800.0,  # 30 minutes
    "health_check": 5.0,
    "system_optimization": 600.0  # 10 minutes
}

# ================================
# STORAGE AND BACKUP
# ================================

# File Extensions
FILE_EXTENSIONS: Final[Dict[str, List[str]]] = {
    "index": [".faiss", ".index", ".bin"],
    "metadata": [".json", ".pkl", ".meta"],
    "backup": [".backup", ".bak", ".gz"],
    "config": [".yaml", ".yml", ".json", ".toml"],
    "log": [".log", ".txt"]
}

# Backup Configuration
BACKUP_CONFIG: Final[Dict[str, Any]] = {
    "max_backup_age_days": 30,
    "max_backup_count": 10,
    "compression_level": 6,
    "backup_chunk_size_mb": 100,
    "verify_backup": True,
    "encrypt_backup": False  # Can be enabled for production
}

# Storage Paths
DEFAULT_STORAGE_PATHS: Final[Dict[str, str]] = {
    "base_directory": "./vector_db_storage",
    "indices_directory": "indices",
    "metadata_directory": "metadata",
    "backups_directory": "backups",
    "logs_directory": "logs",
    "temp_directory": "temp",
    "config_directory": "config"
}

# ================================
# MONITORING AND HEALTH CHECKS
# ================================

# Health Check Intervals (in seconds)
HEALTH_CHECK_INTERVALS: Final[Dict[str, float]] = {
    "system_health": 60.0,
    "index_health": 300.0,  # 5 minutes
    "performance_metrics": 30.0,
    "resource_monitoring": 10.0,
    "backup_validation": 3600.0  # 1 hour
}

# Performance Thresholds
PERFORMANCE_THRESHOLDS: Final[Dict[str, float]] = {
    "max_query_time_ms": 1000.0,
    "max_indexing_time_ms": 5000.0,
    "min_cache_hit_rate": 0.7,
    "max_error_rate": 0.01,  # 1%
    "max_memory_usage_percent": 80.0,
    "max_cpu_usage_percent": 90.0,
    "min_disk_free_gb": 1.0
}

# ================================
# SECURITY AND VALIDATION
# ================================

# Input Validation Limits
VALIDATION_LIMITS: Final[Dict[str, Any]] = {
    "max_text_length": 10000,
    "max_audio_duration": 600,  # 10 minutes
    "max_image_size_pixels": 4096,
    "max_video_duration": 3600,  # 1 hour
    "max_metadata_size_kb": 100,
    "max_content_id_length": 255,
    "allowed_metadata_keys": 50
}

# Security Configuration
SECURITY_CONFIG: Final[Dict[str, Any]] = {
    "enable_input_sanitization": True,
    "enable_rate_limiting": True,
    "max_requests_per_minute": 1000,
    "enable_access_logging": True,
    "hash_algorithm": "sha256",
    "encryption_algorithm": "AES-256-GCM"  # For future use
}

# ================================
# ERROR CODES AND MESSAGES
# ================================

class ErrorCode(IntEnum):
    """System error codes."""
    SUCCESS = 0
    GENERAL_ERROR = 1000
    VALIDATION_ERROR = 1001
    BACKEND_ERROR = 1002
    EMBEDDING_ERROR = 1003
    SEARCH_ERROR = 1004
    STORAGE_ERROR = 1005
    MEMORY_ERROR = 1006
    TIMEOUT_ERROR = 1007
    PERMISSION_ERROR = 1008
    CONFIGURATION_ERROR = 1009
    NETWORK_ERROR = 1010


ERROR_MESSAGES: Final[Dict[int, str]] = {
    ErrorCode.SUCCESS: "Operation completed successfully",
    ErrorCode.GENERAL_ERROR: "An unknown error occurred",
    ErrorCode.VALIDATION_ERROR: "Input validation failed",
    ErrorCode.BACKEND_ERROR: "Vector database backend error",
    ErrorCode.EMBEDDING_ERROR: "Embedding generation failed",
    ErrorCode.SEARCH_ERROR: "Similarity search failed",
    ErrorCode.STORAGE_ERROR: "Storage operation failed",
    ErrorCode.MEMORY_ERROR: "Insufficient memory",
    ErrorCode.TIMEOUT_ERROR: "Operation timed out",
    ErrorCode.PERMISSION_ERROR: "Insufficient permissions",
    ErrorCode.CONFIGURATION_ERROR: "Configuration error",
    ErrorCode.NETWORK_ERROR: "Network communication error"
}

# ================================
# API CONFIGURATION
# ================================

# API Endpoints (for microservice integration)
API_ENDPOINTS: Final[Dict[str, str]] = {
    "health": "/health",
    "status": "/status",
    "embed": "/embed",
    "search": "/search",
    "index": "/index",
    "duplicate": "/duplicate",
    "collaboration": "/collaboration",
    "recommendation": "/recommendation",
    "backup": "/backup",
    "metrics": "/metrics"
}

# HTTP Status Codes
HTTP_STATUS_CODES: Final[Dict[str, int]] = {
    "ok": 200,
    "created": 201,
    "accepted": 202,
    "bad_request": 400,
    "unauthorized": 401,
    "forbidden": 403,
    "not_found": 404,
    "method_not_allowed": 405,
    "conflict": 409,
    "payload_too_large": 413,
    "rate_limit_exceeded": 429,
    "internal_server_error": 500,
    "bad_gateway": 502,
    "service_unavailable": 503,
    "gateway_timeout": 504
}

# ================================
# FEATURE FLAGS
# ================================

class FeatureFlag(Enum):
    """Feature flags for enabling/disabling functionality."""
    ENABLE_AUDIO_PROCESSING = "enable_audio_processing"
    ENABLE_VIDEO_PROCESSING = "enable_video_processing"
    ENABLE_GPU_ACCELERATION = "enable_gpu_acceleration"
    ENABLE_DISTRIBUTED_PROCESSING = "enable_distributed_processing"
    ENABLE_AUTO_OPTIMIZATION = "enable_auto_optimization"
    ENABLE_ADVANCED_ANALYTICS = "enable_advanced_analytics"
    ENABLE_REAL_TIME_MONITORING = "enable_real_time_monitoring"
    ENABLE_COLLABORATIVE_FILTERING = "enable_collaborative_filtering"


DEFAULT_FEATURE_FLAGS: Final[Dict[str, bool]] = {
    FeatureFlag.ENABLE_AUDIO_PROCESSING.value: True,
    FeatureFlag.ENABLE_VIDEO_PROCESSING.value: True,
    FeatureFlag.ENABLE_GPU_ACCELERATION.value: False,  # Requires setup
    FeatureFlag.ENABLE_DISTRIBUTED_PROCESSING.value: False,
    FeatureFlag.ENABLE_AUTO_OPTIMIZATION.value: True,
    FeatureFlag.ENABLE_ADVANCED_ANALYTICS.value: True,
    FeatureFlag.ENABLE_REAL_TIME_MONITORING.value: True,
    FeatureFlag.ENABLE_COLLABORATIVE_FILTERING.value: True
}

# ================================
# LOGGING CONFIGURATION
# ================================

# Log Levels
LOG_LEVELS: Final[Dict[str, str]] = {
    "debug": "DEBUG",
    "info": "INFO",
    "warning": "WARNING",
    "error": "ERROR",
    "critical": "CRITICAL"
}

# Log Format
LOG_FORMAT: Final[str] = (
    "%(asctime)s - %(name)s - %(levelname)s - "
    "%(filename)s:%(lineno)d - %(funcName)s - %(message)s"
)

# Log File Configuration
LOG_FILE_CONFIG: Final[Dict[str, Any]] = {
    "max_file_size_mb": 50,
    "backup_count": 5,
    "rotation_interval": "midnight",
    "encoding": "utf-8",
    "delay": False
}

# ================================
# COLLABORATION AND RECOMMENDATION
# ================================

# Collaboration Matching Weights
COLLABORATION_WEIGHTS: Final[Dict[str, float]] = {
    "content_similarity": 0.3,
    "skill_complementarity": 0.25,
    "interest_overlap": 0.2,
    "audience_alignment": 0.15,
    "availability_match": 0.1
}

# Recommendation Algorithm Weights
RECOMMENDATION_WEIGHTS: Final[Dict[str, float]] = {
    "content_similarity": 0.4,
    "user_preference": 0.3,
    "popularity_score": 0.15,
    "recency_factor": 0.1,
    "diversity_factor": 0.05
}

# ================================
# DEPLOYMENT AND SCALING
# ================================

# Container Configuration
CONTAINER_CONFIG: Final[Dict[str, Any]] = {
    "min_memory_mb": 512,
    "recommended_memory_mb": 2048,
    "min_cpu_cores": 1,
    "recommended_cpu_cores": 4,
    "port": 8000,
    "health_check_path": "/health",
    "graceful_shutdown_timeout": 30
}

# Scaling Parameters
SCALING_PARAMS: Final[Dict[str, Any]] = {
    "auto_scale_threshold_cpu": 70.0,
    "auto_scale_threshold_memory": 80.0,
    "scale_up_cooldown_seconds": 300,
    "scale_down_cooldown_seconds": 600,
    "min_instances": 1,
    "max_instances": 10
}

# ================================
# COPYRIGHT AND LEGAL
# ================================

COPYRIGHT_NOTICE: Final[str] = """
⚠️ COPYRIGHT WARNING ⚠️

This Vector Database System is the intellectual property of Fahed Mlaiel.

© 2025 Fahed Mlaiel - All Rights Reserved

This software represents over 3500+ hours of development work and contains 
proprietary algorithms, architectures, and implementations. 

UNAUTHORIZED USE IS STRICTLY PROHIBITED:
- No reproduction, distribution, or modification without explicit written permission
- Commercial use requires licensing agreement
- Reverse engineering is forbidden
- Educational use requires attribution

Violations will result in immediate legal action including but not limited to:
- Cease and desist orders
- Civil litigation for damages
- Criminal prosecution where applicable
- Injunctive relief

For licensing inquiries, contact: mlaiel@live.de
"""

LEGAL_DISCLAIMERS: Final[Dict[str, str]] = {
    "warranty": "This software is provided 'as is' without warranty of any kind.",
    "liability": "The author shall not be liable for any damages arising from use.",
    "trademark": "All trademarks are property of their respective owners.",
    "privacy": "System may collect performance and usage statistics for optimization."
}

# ================================
# EXPERT TEAM INFORMATION
# ================================

EXPERT_TEAM_ROLES: Final[Dict[str, Dict[str, str]]] = {
    "lead_ai_developer": {
        "name": "Fahed Mlaiel",
        "role": "Lead AI Developer + Backend Senior Engineer",
        "expertise": "AI algorithms, backend architecture, system design",
        "contact": "mlaiel@live.de"
    },
    "ml_engineer": {
        "role": "ML Engineer + Data Scientist",
        "expertise": "Machine learning algorithms, data analysis, optimization",
        "focus": "Embedding models, similarity algorithms, performance tuning"
    },
    "database_admin": {
        "role": "Database Administrator + Performance Specialist",
        "expertise": "Database optimization, indexing strategies, scalability",
        "focus": "Vector database backends, query optimization, storage"
    },
    "security_engineer": {
        "role": "Security Engineer + DevOps Engineer",
        "expertise": "System security, deployment automation, monitoring",
        "focus": "Data protection, access control, CI/CD pipelines"
    },
    "audio_specialist": {
        "role": "Audio Processing Specialist",
        "expertise": "Audio signal processing, music analysis, fingerprinting",
        "focus": "Audio feature extraction, similarity matching"
    },
    "vision_engineer": {
        "role": "Computer Vision Engineer",
        "expertise": "Image/video processing, deep learning, recognition",
        "focus": "Visual content analysis, embedding generation"
    },
    "microservices_architect": {
        "role": "Microservices Architect",
        "expertise": "Distributed systems, API design, service mesh",
        "focus": "System architecture, scalability, integration"
    }
}

# ================================
# UTILITY FUNCTIONS FOR CONSTANTS
# ================================

def get_default_config_for_content_type(content_type: ContentType) -> Dict[str, Any]:
    """Get default configuration for a specific content type."""
    configs = {
        ContentType.TEXT: {
            "embedding_model": "all-MiniLM-L6-v2",
            "similarity_threshold": DEFAULT_SIMILARITY_THRESHOLDS[ContentType.TEXT.value],
            "max_length": TEXT_EMBEDDING_MODELS["all-MiniLM-L6-v2"]["max_length"]
        },
        ContentType.AUDIO: {
            "sample_rate": AUDIO_PROCESSING_PARAMS["default_sample_rate"],
            "similarity_threshold": DEFAULT_SIMILARITY_THRESHOLDS[ContentType.AUDIO.value],
            "max_duration": AUDIO_PROCESSING_PARAMS["max_duration_seconds"]
        },
        ContentType.IMAGE: {
            "size": IMAGE_PROCESSING_PARAMS["default_size"],
            "similarity_threshold": DEFAULT_SIMILARITY_THRESHOLDS[ContentType.IMAGE.value],
            "max_size": IMAGE_PROCESSING_PARAMS["max_size"]
        },
        ContentType.VIDEO: {
            "max_frames": VIDEO_PROCESSING_PARAMS["max_frames"],
            "similarity_threshold": DEFAULT_SIMILARITY_THRESHOLDS[ContentType.VIDEO.value],
            "frame_size": VIDEO_PROCESSING_PARAMS["frame_size"]
        }
    }
    
    return configs.get(content_type, {})


def validate_feature_flag(flag_name: str) -> bool:
    """Validate if a feature flag is enabled."""
    return DEFAULT_FEATURE_FLAGS.get(flag_name, False)


def get_performance_threshold(metric_name: str) -> float:
    """Get performance threshold for a specific metric."""
    return PERFORMANCE_THRESHOLDS.get(metric_name, 0.0)


def get_error_message(error_code: int) -> str:
    """Get error message for an error code."""
    return ERROR_MESSAGES.get(error_code, "Unknown error")


# Export all constants and enums
__all__ = [
    # System metadata
    'SYSTEM_NAME', 'SYSTEM_VERSION', 'SYSTEM_AUTHOR', 'SYSTEM_EMAIL',
    'SYSTEM_COPYRIGHT', 'SYSTEM_LICENSE',
    
    # Enums
    'ContentType', 'AudioFormat', 'ImageFormat', 'VideoFormat',
    'BackendType', 'FAISSIndexType', 'DistanceMetric', 'ErrorCode', 'FeatureFlag',
    
    # Configuration dictionaries
    'TEXT_EMBEDDING_MODELS', 'AUDIO_PROCESSING_PARAMS', 'IMAGE_PROCESSING_PARAMS',
    'VIDEO_PROCESSING_PARAMS', 'DEFAULT_SIMILARITY_THRESHOLDS',
    'DUPLICATE_DETECTION_THRESHOLDS', 'SEARCH_RESULT_LIMITS',
    
    # Performance and optimization
    'MEMORY_LIMITS', 'BATCH_SIZES', 'TIMEOUT_VALUES', 'PERFORMANCE_THRESHOLDS',
    
    # Storage and backup
    'FILE_EXTENSIONS', 'BACKUP_CONFIG', 'DEFAULT_STORAGE_PATHS',
    
    # Monitoring and health
    'HEALTH_CHECK_INTERVALS', 'VALIDATION_LIMITS', 'SECURITY_CONFIG',
    
    # API and networking
    'API_ENDPOINTS', 'HTTP_STATUS_CODES',
    
    # Feature flags
    'DEFAULT_FEATURE_FLAGS',
    
    # Logging
    'LOG_LEVELS', 'LOG_FORMAT', 'LOG_FILE_CONFIG',
    
    # Collaboration and recommendation
    'COLLABORATION_WEIGHTS', 'RECOMMENDATION_WEIGHTS',
    
    # Deployment
    'CONTAINER_CONFIG', 'SCALING_PARAMS',
    
    # Legal and team info
    'COPYRIGHT_NOTICE', 'LEGAL_DISCLAIMERS', 'EXPERT_TEAM_ROLES',
    'ERROR_MESSAGES',
    
    # Utility functions
    'get_default_config_for_content_type', 'validate_feature_flag',
    'get_performance_threshold', 'get_error_message'
]
