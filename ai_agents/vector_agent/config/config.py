"""Vector Agent Configuration - Enterprise-Grade Settings & Parameters

Ultra-comprehensive configuration management for vector operations with
production-ready defaults, environment-based overrides, and validation.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or commercialization is strictly prohibited.
Any attempt to steal the concept, idea, or code without explicit written authorization
from Fahed Mlaiel will result in immediate legal prosecution under German and international law.
"""import os
import json
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


@dataclass
class VectorConfig:
    """    Ultra-Advanced Vector Agent Configuration
    
    Comprehensive configuration management with production-ready defaults,
    environment variable support, and validation for all vector operations.
    """    
    # ===============================
    # CORE VECTOR PROCESSING SETTINGS
    # ===============================
    
    # Vector dimensions and processing
    default_vector_dimension: int = 512
    max_vector_dimension: int = 4096
    batch_size: int = 32
    max_batch_size: int = 1000
    
    # Performance and threading
    max_worker_threads: int = 8
    processing_timeout: float = 300.0  # 5 minutes
    batch_processing_interval: float = 1.0  # seconds
    
    # Memory management
    max_memory_usage_mb: int = 2048
    memory_cleanup_threshold: float = 0.85
    vector_cache_size: int = 10000
    
    # ===============================
    # FAISS INDEX CONFIGURATION
    # ===============================
    
    # Index types and parameters
    default_index_type: str = "flat"
    auto_index_selection: bool = True
    index_optimization_threshold: int = 1000  # vectors
    optimization_interval: float = 3600.0  # 1 hour
    
    # FAISS-specific settings
    faiss_nprobe: int = 32
    faiss_efSearch: int = 128
    faiss_efConstruction: int = 200
    faiss_M: int = 32  # HNSW parameter
    
    # ===============================
    # SIMILARITY SEARCH SETTINGS
    # ===============================
    
    # Search parameters
    similarity_threshold: float = 0.75
    default_max_results: int = 10
    max_search_results: int = 1000
    
    # Search optimization
    enable_search_optimization: bool = True
    adaptive_threshold_adjustment: bool = True
    cross_modal_search_boost: float = 1.0
    
    # Algorithm weights for different content types
    similarity_algorithm_weights: Dict[str, Dict[str, float]] = field(default_factory=lambda: {
        "audio": {"cosine": 0.4, "euclidean": 0.3, "pearson": 0.2, "spearman": 0.1},
        "video": {"cosine": 0.5, "euclidean": 0.3, "manhattan": 0.2},
        "image": {"cosine": 0.4, "euclidean": 0.3, "manhattan": 0.2, "jaccard": 0.1},
        "text": {"cosine": 0.6, "pearson": 0.2, "jaccard": 0.2},
        "default": {"cosine": 0.5, "euclidean": 0.3, "pearson": 0.2}
    })
    
    # ===============================
    # CACHING AND OPTIMIZATION
    # ===============================
    
    # Cache settings
    cache_size: int = 50000
    cache_ttl: int = 3600  # 1 hour
    enable_query_cache: bool = True
    cache_hit_rate_target: float = 0.7
    
    # Performance monitoring
    max_performance_history: int = 10000
    metrics_collection_interval: float = 60.0  # 1 minute
    performance_analysis_window: int = 86400  # 24 hours
    
    # ===============================
    # STORAGE AND PERSISTENCE
    # ===============================
    
    # File system settings
    persistence_dir: str = "/tmp/vector_agent"
    vector_storage_format: str = "numpy"  # numpy, hdf5, parquet
    metadata_storage_format: str = "sqlite"  # sqlite, postgresql, json
    
    # Backup and recovery
    enable_auto_backup: bool = True
    backup_interval: int = 86400  # 24 hours
    max_backup_files: int = 7
    compression_enabled: bool = True
    
    # Data retention
    auto_cleanup_enabled: bool = True
    max_document_age_days: int = 90
    cleanup_interval: int = 86400  # 24 hours
    
    # Auto-save settings
    auto_save_enabled: bool = True
    auto_save_interval: int = 1000  # every 1000 operations
    
    # ===============================
    # CONTENT TYPE SPECIFIC SETTINGS
    # ===============================
    
    # Content type configurations
    content_type_configs: Dict[str, Dict[str, Any]] = field(default_factory=lambda: {
        "audio": {
            "default_dimension": 512,
            "preferred_index_type": "ivf",
            "similarity_threshold": 0.75,
            "preprocessing": {
                "normalization": "l2",
                "feature_scaling": True,
                "noise_reduction": False
            }
        },
        "video": {
            "default_dimension": 1024,
            "preferred_index_type": "hnsw",
            "similarity_threshold": 0.80,
            "preprocessing": {
                "normalization": "standard",
                "feature_scaling": True,
                "temporal_weighting": True
            }
        },
        "image": {
            "default_dimension": 2048,
            "preferred_index_type": "ivf",
            "similarity_threshold": 0.85,
            "preprocessing": {
                "normalization": "minmax",
                "feature_scaling": False,
                "color_space_conversion": False
            }
        },
        "text": {
            "default_dimension": 384,
            "preferred_index_type": "flat",
            "similarity_threshold": 0.70,
            "preprocessing": {
                "normalization": "unit",
                "feature_scaling": False,
                "language_detection": True
            }
        }
    })
    
    # ===============================
    # LOGGING AND MONITORING
    # ===============================
    
    # Logging configuration
    log_level: str = "INFO"
    enable_performance_logging: bool = True
    enable_debug_logging: bool = False
    log_file_path: Optional[str] = None
    max_log_file_size_mb: int = 100
    
    # Monitoring and alerting
    enable_monitoring: bool = True
    monitoring_port: int = 8090
    health_check_interval: float = 30.0
    alert_thresholds: Dict[str, float] = field(default_factory=lambda: {
        "search_time_ms": 100.0,
        "error_rate": 0.05,
        "memory_usage": 0.85,
        "cache_hit_rate": 0.5
    })
    
    # ===============================
    # SECURITY AND VALIDATION
    # ===============================
    
    # Input validation
    enable_input_validation: bool = True
    max_query_vector_dimension: int = 8192
    max_metadata_size_kb: int = 100
    validate_vector_data: bool = True
    
    # Security settings
    enable_rate_limiting: bool = True
    max_requests_per_minute: int = 1000
    enable_request_logging: bool = True
    
    # ===============================
    # EXPERIMENTAL FEATURES
    # ===============================
    
    # Advanced features (experimental)
    enable_gpu_acceleration: bool = False
    enable_distributed_search: bool = False
    enable_ml_optimization: bool = False
    experimental_features: Dict[str, bool] = field(default_factory=lambda: {
        "adaptive_indexing": False,
        "auto_tuning": False,
        "predictive_caching": False,
        "quantum_similarity": False
    })
    
    # ===============================
    # INITIALIZATION AND VALIDATION
    # ===============================
    
    def __post_init__(self):
        """Post-initialization validation and environment variable loading"""        try:
            # Load environment variables
            self._load_environment_variables()
            
            # Validate configuration
            self._validate_configuration()
            
            # Ensure directories exist
            self._ensure_directories()
            
            # Set up derived configurations
            self._setup_derived_configs()
            
            logger.info("Vector configuration initialized successfully")
            
        except Exception as e:
            logger.error(f"Vector configuration initialization failed: {e}")
            raise ValueError(f"Configuration error: {str(e)}")
    
    def _load_environment_variables(self):
        """Load configuration from environment variables"""        env_mappings = {
            "VECTOR_AGENT_BATCH_SIZE": ("batch_size", int),
            "VECTOR_AGENT_MAX_WORKERS": ("max_worker_threads", int),
            "VECTOR_AGENT_CACHE_SIZE": ("cache_size", int),
            "VECTOR_AGENT_SIMILARITY_THRESHOLD": ("similarity_threshold", float),
            "VECTOR_AGENT_PERSISTENCE_DIR": ("persistence_dir", str),
            "VECTOR_AGENT_LOG_LEVEL": ("log_level", str),
            "VECTOR_AGENT_ENABLE_GPU": ("enable_gpu_acceleration", lambda x: x.lower() == "true"),
            "VECTOR_AGENT_MAX_MEMORY_MB": ("max_memory_usage_mb", int),
            "VECTOR_AGENT_AUTO_BACKUP": ("enable_auto_backup", lambda x: x.lower() == "true"),
        }
        
        for env_var, (attr_name, converter) in env_mappings.items():
            env_value = os.getenv(env_var)
            if env_value is not None:
                try:
                    converted_value = converter(env_value)
                    setattr(self, attr_name, converted_value)
                    logger.debug(f"Loaded {attr_name} = {converted_value} from {env_var}")
                except Exception as e:
                    logger.warning(f"Failed to convert {env_var}={env_value}: {e}")
    
    def _validate_configuration(self):
        """Validate configuration parameters"""        # Validate ranges
        if self.batch_size <= 0 or self.batch_size > self.max_batch_size:
            raise ValueError(f"batch_size must be between 1 and {self.max_batch_size}")
        
        if not (0.0 <= self.similarity_threshold <= 1.0):
            raise ValueError("similarity_threshold must be between 0.0 and 1.0")
        
        if self.max_worker_threads <= 0 or self.max_worker_threads > 64:
            raise ValueError("max_worker_threads must be between 1 and 64")
        
        if self.cache_size <= 0:
            raise ValueError("cache_size must be positive")
        
        if self.max_memory_usage_mb < 256:
            raise ValueError("max_memory_usage_mb must be at least 256")
        
        # Validate vector dimensions
        if self.default_vector_dimension <= 0:
            raise ValueError("default_vector_dimension must be positive")
        
        if self.max_vector_dimension < self.default_vector_dimension:
            raise ValueError("max_vector_dimension must be >= default_vector_dimension")
        
        # Validate file paths
        if not isinstance(self.persistence_dir, str) or not self.persistence_dir:
            raise ValueError("persistence_dir must be a non-empty string")
    
    def _ensure_directories(self):
        """Ensure required directories exist"""        try:
            Path(self.persistence_dir).mkdir(parents=True, exist_ok=True)
            
            # Create subdirectories
            subdirs = ["vectors", "indices", "cache", "backups", "logs"]
            for subdir in subdirs:
                Path(self.persistence_dir, subdir).mkdir(exist_ok=True)
                
        except Exception as e:
            logger.error(f"Failed to create directories: {e}")
            raise
    
    def _setup_derived_configs(self):
        """Set up derived configuration values"""        # Adjust thread pool size based on CPU count
        import multiprocessing
        cpu_count = multiprocessing.cpu_count()
        if self.max_worker_threads > cpu_count * 2:
            self.max_worker_threads = max(1, cpu_count * 2)
            logger.info(f"Adjusted max_worker_threads to {self.max_worker_threads} based on CPU count")
        
        # Adjust cache size based on available memory
        if self.cache_size * 1024 > self.max_memory_usage_mb * 1024 * 1024 * 0.5:
            # Cache shouldn't use more than 50% of max memory
            self.cache_size = int(self.max_memory_usage_mb * 512)  # Rough estimation
            logger.info(f"Adjusted cache_size to {self.cache_size} based on memory limits")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""        return asdict(self)
    
    def save_to_file(self, filepath: str) -> None:
        """Save configuration to JSON file"""        try:
            config_dict = self.to_dict()
            with open(filepath, 'w') as f:
                json.dump(config_dict, f, indent=2, default=str)
            logger.info(f"Configuration saved to {filepath}")
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
            raise
    
    @classmethod
    def load_from_file(cls, filepath: str) -> 'VectorConfig':
        """Load configuration from JSON file"""        try:
            with open(filepath, 'r') as f:
                config_dict = json.load(f)
            
            # Create instance with loaded configuration
            config = cls(**config_dict)
            logger.info(f"Configuration loaded from {filepath}")
            return config
            
        except Exception as e:
            logger.error(f"Failed to load configuration from {filepath}: {e}")
            raise
    
    def get_content_type_config(self, content_type: str) -> Dict[str, Any]:
        """Get configuration for specific content type"""        return self.content_type_configs.get(content_type, self.content_type_configs.get("default", {}))
    
    def get_similarity_weights(self, content_type: str) -> Dict[str, float]:
        """Get similarity algorithm weights for content type"""        return self.similarity_algorithm_weights.get(content_type, 
                                                   self.similarity_algorithm_weights.get("default", {}))
    
    def get_index_type_for_content(self, content_type: str) -> str:
        """Get preferred index type for content type"""        content_config = self.get_content_type_config(content_type)
        return content_config.get("preferred_index_type", self.default_index_type)
    
    def get_dimension_for_content(self, content_type: str) -> int:
        """Get default dimension for content type"""        content_config = self.get_content_type_config(content_type)
        return content_config.get("default_dimension", self.default_vector_dimension)
    
    def get_similarity_threshold_for_content(self, content_type: str) -> float:
        """Get similarity threshold for content type"""        content_config = self.get_content_type_config(content_type)
        return content_config.get("similarity_threshold", self.similarity_threshold)
    
    def update_from_dict(self, config_dict: Dict[str, Any]) -> None:
        """Update configuration from dictionary"""        try:
            for key, value in config_dict.items():
                if hasattr(self, key):
                    setattr(self, key, value)
                else:
                    logger.warning(f"Unknown configuration key: {key}")
            
            # Re-validate after updates
            self._validate_configuration()
            logger.info("Configuration updated successfully")
            
        except Exception as e:
            logger.error(f"Configuration update failed: {e}")
            raise
    
    def get_monitoring_config(self) -> Dict[str, Any]:
        """Get monitoring-specific configuration"""        return {
            "enabled": self.enable_monitoring,
            "port": self.monitoring_port,
            "health_check_interval": self.health_check_interval,
            "alert_thresholds": self.alert_thresholds.copy(),
            "performance_logging": self.enable_performance_logging
        }
    
    def get_security_config(self) -> Dict[str, Any]:
        """Get security-specific configuration"""        return {
            "input_validation": self.enable_input_validation,
            "rate_limiting": self.enable_rate_limiting,
            "max_requests_per_minute": self.max_requests_per_minute,
            "request_logging": self.enable_request_logging,
            "max_metadata_size_kb": self.max_metadata_size_kb
        }
    
    def __repr__(self) -> str:
        """String representation of configuration"""        key_settings = {
            "batch_size": self.batch_size,
            "max_workers": self.max_worker_threads,
            "cache_size": self.cache_size,
            "similarity_threshold": self.similarity_threshold,
            "persistence_dir": self.persistence_dir
        }
        return f"VectorConfig({', '.join(f'{k}={v}' for k, v in key_settings.items())})"


# ===============================
# CONFIGURATION FACTORY FUNCTIONS
# ===============================

def create_development_config() -> VectorConfig:
    """Create configuration optimized for development"""    return VectorConfig(
        batch_size=16,
        max_worker_threads=4,
        cache_size=5000,
        enable_debug_logging=True,
        auto_backup_enabled=False,
        max_memory_usage_mb=1024,
        processing_timeout=60.0
    )


def create_production_config() -> VectorConfig:
    """Create configuration optimized for production"""    return VectorConfig(
        batch_size=64,
        max_worker_threads=16,
        cache_size=100000,
        enable_debug_logging=False,
        auto_backup_enabled=True,
        max_memory_usage_mb=4096,
        processing_timeout=600.0,
        enable_monitoring=True,
        enable_performance_logging=True
    )


def create_testing_config() -> VectorConfig:
    """Create configuration optimized for testing"""    return VectorConfig(
        batch_size=8,
        max_worker_threads=2,
        cache_size=1000,
        persistence_dir="/tmp/vector_test",
        enable_debug_logging=True,
        auto_backup_enabled=False,
        max_memory_usage_mb=512,
        processing_timeout=30.0
    )


def get_config_for_environment(env: str = None) -> VectorConfig:
    """Get configuration based on environment"""    if env is None:
        env = os.getenv("VECTOR_AGENT_ENV", "development").lower()
    
    if env == "production":
        return create_production_config()
    elif env == "testing":
        return create_testing_config()
    else:
        return create_development_config()
