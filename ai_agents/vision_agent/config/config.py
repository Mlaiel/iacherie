"""Configuration Module - Enterprise Vision Agent Configuration System
==================================================================

Comprehensive configuration management for the Vision Agent system with
environment-aware settings, security controls, and performance tuning.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or commercialization is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.
"""
import os
import logging
from typing import Dict, Any, List, Optional, Union, Tuple
from dataclasses import dataclass, field
from pathlib import Path
import json
from enum import Enum
import yaml
from functools import lru_cache
import torch
import platform

logger = logging.getLogger(__name__)

class ProcessingMode(Enum):
    """Vision processing mode configuration"""    FAST = "fast"
    BALANCED = "balanced" 
    HIGH_QUALITY = "high_quality"
    ENTERPRISE = "enterprise"
    ULTRA_PERFORMANCE = "ultra_performance"

class PrivacyLevel(Enum):
    """Privacy protection levels"""    MINIMAL = "minimal"
    STANDARD = "standard"
    HIGH = "high"
    MAXIMUM = "maximum"
    ENTERPRISE_COMPLIANCE = "enterprise_compliance"

class DeploymentEnvironment(Enum):
    """Deployment environment types"""    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"
    ENTERPRISE = "enterprise"

class ModelPrecision(Enum):
    """Model precision levels"""    FP32 = "fp32"
    FP16 = "fp16"
    INT8 = "int8"
    DYNAMIC = "dynamic"

@dataclass
class ModelConfig:
    """Configuration for AI models"""    name: str
    path: Optional[str] = None
    url: Optional[str] = None
    version: str = "latest"
    confidence_threshold: float = 0.5
    enabled: bool = True
    cache_size: int = 100
    gpu_acceleration: bool = True
    max_batch_size: int = 8
    precision: ModelPrecision = ModelPrecision.FP32
    warm_up_samples: int = 5
    memory_fraction: float = 0.3
    inference_mode: str = "async"
    fallback_cpu: bool = True

@dataclass 
class PerformanceConfig:
    """Performance optimization settings"""    max_concurrent_tasks: int = 4
    memory_limit_mb: int = 2048
    cache_enabled: bool = True
    cache_size_mb: int = 512
    timeout_seconds: int = 30
    retry_attempts: int = 3
    batch_processing: bool = True
    gpu_memory_fraction: float = 0.7
    cpu_threads: Optional[int] = None
    async_processing: bool = True
    queue_max_size: int = 100
    worker_processes: int = 2
    optimization_level: str = "O2"
    tensor_parallelism: bool = False
    memory_mapping: bool = True

@dataclass
class SecurityConfig:
    """Security and privacy settings"""    privacy_level: PrivacyLevel = PrivacyLevel.STANDARD
    remove_exif: bool = True
    face_anonymization: bool = True
    watermark_removal: bool = False
    content_filtering: bool = True
    audit_logging: bool = True
    encrypted_storage: bool = True
    secure_deletion: bool = True
    access_control: bool = True
    rate_limiting: Dict[str, int] = field(default_factory=lambda: {
        "requests_per_minute": 60,
        "concurrent_requests": 10,
        "burst_limit": 100
    })
    allowed_file_types: List[str] = field(default_factory=lambda: [
        'jpg', 'jpeg', 'png', 'webp', 'tiff', 'bmp', 'gif',
        'mp4', 'avi', 'mov', 'mkv', 'webm'
    ])
    max_file_size_mb: int = 100
    content_validation: bool = True
    virus_scanning: bool = True

@dataclass
class QualityConfig:
    """Image and video quality settings"""    min_resolution: Tuple[int, int] = (640, 480)
    max_resolution: Tuple[int, int] = (4096, 4096)
    supported_formats: List[str] = field(default_factory=lambda: [
        'jpg', 'jpeg', 'png', 'webp', 'tiff', 'bmp', 'gif'
    ])
    video_formats: List[str] = field(default_factory=lambda: [
        'mp4', 'avi', 'mov', 'mkv', 'webm', 'flv', 'm4v'
    ])
    compression_quality: int = 85
    auto_enhancement: bool = True
    noise_reduction: bool = True
    sharpening: bool = False
    color_correction: bool = True
    histogram_equalization: bool = False
    denoising_strength: float = 0.3
    upscaling_method: str = "bicubic"
    downscaling_method: str = "lanczos"

@dataclass
class ProcessingOptions:
    """Processing pipeline options"""    enable_object_detection: bool = True
    enable_face_recognition: bool = True
    enable_ocr: bool = True
    enable_scene_analysis: bool = True
    enable_similarity_matching: bool = True
    enable_metadata_extraction: bool = True
    enable_content_filtering: bool = True
    enable_quality_assessment: bool = True
    enable_fingerprinting: bool = True
    enable_enhancement: bool = False
    enable_format_conversion: bool = True
    enable_compression: bool = True

@dataclass
class StorageConfig:
    """Storage configuration"""    storage_backend: str = "local"  # local, s3, gcs, azure
    base_path: str = "/tmp/vision_agent"
    cache_path: str = "/tmp/vision_cache"
    temp_path: str = "/tmp/vision_temp"
    models_path: str = "/models"
    results_path: str = "/results"
    backup_enabled: bool = True
    compression_enabled: bool = True
    cleanup_interval: int = 3600  # seconds
    max_storage_size_gb: int = 50
    retention_days: int = 30

@dataclass
class MonitoringConfig:
    """Monitoring and logging configuration"""    enable_metrics: bool = True
    enable_tracing: bool = True
    log_level: str = "INFO"
    metrics_port: int = 8080
    health_check_port: int = 8081
    prometheus_enabled: bool = True
    jaeger_enabled: bool = False
    custom_metrics: List[str] = field(default_factory=lambda: [
        "processing_time", "accuracy_score", "memory_usage", "gpu_utilization"
    ])
    alert_thresholds: Dict[str, float] = field(default_factory=lambda: {
        "max_processing_time": 30.0,
        "min_accuracy": 0.8,
        "max_memory_mb": 2048,
        "max_gpu_util": 0.9
    })

class VisionAgentConfig:
    """    Comprehensive configuration management for Vision Agent
    
    Handles environment-specific settings, model configurations,
    performance tuning, and security controls with enterprise-grade features.
    """    
    def __init__(self, config_path: Optional[str] = None, environment: Optional[str] = None):
        """Initialize configuration with optional config file and environment"""        self.config_path = config_path
        self.environment = environment or os.getenv('VISION_ENV', 'development')
        self._config_cache = {}
        
        # Initialize configurations
        self.models = self._load_model_configs()
        self.performance = self._load_performance_config()
        self.security = self._load_security_config()
        self.quality = self._load_quality_config()
        self.processing = self._load_processing_config()
        self.storage = self._load_storage_config()
        self.monitoring = self._load_monitoring_config()
        
        # Apply environment-specific overrides
        self._apply_environment_overrides()
        
        # Validate configuration
        self._validate_configuration()
        
        logger.info(f"Vision Agent configuration loaded for environment: {self.environment}")
    
    def _load_model_configs(self) -> Dict[str, ModelConfig]:
        """Load model configurations"""        base_configs = {
            "yolo": ModelConfig(
                name="YOLOv8",
                path=os.getenv('VISION_YOLO_MODEL_PATH', '/models/yolo_v8.pt'),
                confidence_threshold=float(os.getenv('VISION_YOLO_CONFIDENCE', '0.5')),
                max_batch_size=int(os.getenv('VISION_YOLO_BATCH_SIZE', '8')),
                precision=ModelPrecision(os.getenv('VISION_YOLO_PRECISION', 'fp32')),
                gpu_acceleration=os.getenv('VISION_GPU_ENABLED', 'true').lower() == 'true'
            ),
            "face_recognition": ModelConfig(
                name="FaceNet",
                path=os.getenv('VISION_FACE_MODEL_PATH', '/models/facenet.pkl'),
                confidence_threshold=float(os.getenv('VISION_FACE_CONFIDENCE', '0.6')),
                max_batch_size=int(os.getenv('VISION_FACE_BATCH_SIZE', '4')),
                precision=ModelPrecision.FP32
            ),
            "ocr": ModelConfig(
                name="TesseractOCR",
                path=os.getenv('VISION_OCR_MODEL_PATH', '/models/tesseract'),
                confidence_threshold=float(os.getenv('VISION_OCR_CONFIDENCE', '0.7')),
                gpu_acceleration=False  # Tesseract is CPU-based
            ),
            "scene_analysis": ModelConfig(
                name="Places365",
                path=os.getenv('VISION_SCENE_MODEL_PATH', '/models/places365.pth'),
                confidence_threshold=float(os.getenv('VISION_SCENE_CONFIDENCE', '0.5')),
                max_batch_size=int(os.getenv('VISION_SCENE_BATCH_SIZE', '16'))
            ),
            "similarity": ModelConfig(
                name="ResNet50",
                path=os.getenv('VISION_SIMILARITY_MODEL_PATH', '/models/resnet50.pth'),
                confidence_threshold=float(os.getenv('VISION_SIMILARITY_THRESHOLD', '0.8')),
                max_batch_size=int(os.getenv('VISION_SIMILARITY_BATCH_SIZE', '32'))
            )
        }
        
        # Load custom configurations if available
        if self.config_path and os.path.exists(self.config_path):
            with open(self.config_path, 'r') as f:
                custom_config = yaml.safe_load(f)
                if 'models' in custom_config:
                    for name, config in custom_config['models'].items():
                        if name in base_configs:
                            # Update existing configuration
                            for key, value in config.items():
                                if hasattr(base_configs[name], key):
                                    setattr(base_configs[name], key, value)
                        else:
                            # Add new model configuration
                            base_configs[name] = ModelConfig(**config)
        
        return base_configs
    
    def _load_performance_config(self) -> PerformanceConfig:
        """Load performance configuration"""        cpu_count = os.cpu_count() or 4
        
        return PerformanceConfig(
            max_concurrent_tasks=int(os.getenv('VISION_MAX_CONCURRENT', str(cpu_count))),
            memory_limit_mb=int(os.getenv('VISION_MEMORY_LIMIT', '2048')),
            cache_enabled=os.getenv('VISION_CACHE_ENABLED', 'true').lower() == 'true',
            cache_size_mb=int(os.getenv('VISION_CACHE_SIZE', '512')),
            timeout_seconds=int(os.getenv('VISION_TIMEOUT', '30')),
            retry_attempts=int(os.getenv('VISION_RETRY_ATTEMPTS', '3')),
            batch_processing=os.getenv('VISION_BATCH_PROCESSING', 'true').lower() == 'true',
            gpu_memory_fraction=float(os.getenv('VISION_GPU_MEMORY_FRACTION', '0.7')),
            cpu_threads=int(os.getenv('VISION_CPU_THREADS', str(cpu_count))),
            async_processing=os.getenv('VISION_ASYNC_PROCESSING', 'true').lower() == 'true',
            queue_max_size=int(os.getenv('VISION_QUEUE_MAX_SIZE', '100')),
            worker_processes=int(os.getenv('VISION_WORKER_PROCESSES', '2')),
            optimization_level=os.getenv('VISION_OPTIMIZATION_LEVEL', 'O2'),
            tensor_parallelism=os.getenv('VISION_TENSOR_PARALLELISM', 'false').lower() == 'true'
        )
    
    def _load_security_config(self) -> SecurityConfig:
        """Load security configuration"""        return SecurityConfig(
            privacy_level=PrivacyLevel(os.getenv('VISION_PRIVACY_LEVEL', 'standard')),
            remove_exif=os.getenv('VISION_REMOVE_EXIF', 'true').lower() == 'true',
            face_anonymization=os.getenv('VISION_FACE_ANONYMIZATION', 'true').lower() == 'true',
            watermark_removal=os.getenv('VISION_WATERMARK_REMOVAL', 'false').lower() == 'true',
            content_filtering=os.getenv('VISION_CONTENT_FILTERING', 'true').lower() == 'true',
            audit_logging=os.getenv('VISION_AUDIT_LOGGING', 'true').lower() == 'true',
            encrypted_storage=os.getenv('VISION_ENCRYPTED_STORAGE', 'true').lower() == 'true',
            secure_deletion=os.getenv('VISION_SECURE_DELETION', 'true').lower() == 'true',
            access_control=os.getenv('VISION_ACCESS_CONTROL', 'true').lower() == 'true',
            max_file_size_mb=int(os.getenv('VISION_MAX_FILE_SIZE_MB', '100')),
            content_validation=os.getenv('VISION_CONTENT_VALIDATION', 'true').lower() == 'true',
            virus_scanning=os.getenv('VISION_VIRUS_SCANNING', 'true').lower() == 'true'
        )
    
    def _load_quality_config(self) -> QualityConfig:
        """Load quality configuration"""        return QualityConfig(
            min_resolution=(
                int(os.getenv('VISION_MIN_WIDTH', '640')),
                int(os.getenv('VISION_MIN_HEIGHT', '480'))
            ),
            max_resolution=(
                int(os.getenv('VISION_MAX_WIDTH', '4096')),
                int(os.getenv('VISION_MAX_HEIGHT', '4096'))
            ),
            compression_quality=int(os.getenv('VISION_COMPRESSION_QUALITY', '85')),
            auto_enhancement=os.getenv('VISION_AUTO_ENHANCEMENT', 'true').lower() == 'true',
            noise_reduction=os.getenv('VISION_NOISE_REDUCTION', 'true').lower() == 'true',
            sharpening=os.getenv('VISION_SHARPENING', 'false').lower() == 'true',
            color_correction=os.getenv('VISION_COLOR_CORRECTION', 'true').lower() == 'true',
            histogram_equalization=os.getenv('VISION_HISTOGRAM_EQ', 'false').lower() == 'true',
            denoising_strength=float(os.getenv('VISION_DENOISING_STRENGTH', '0.3')),
            upscaling_method=os.getenv('VISION_UPSCALING_METHOD', 'bicubic'),
            downscaling_method=os.getenv('VISION_DOWNSCALING_METHOD', 'lanczos')
        )
    
    def _load_processing_config(self) -> ProcessingOptions:
        """Load processing pipeline configuration"""        return ProcessingOptions(
            enable_object_detection=os.getenv('VISION_ENABLE_OBJECT_DETECTION', 'true').lower() == 'true',
            enable_face_recognition=os.getenv('VISION_ENABLE_FACE_RECOGNITION', 'true').lower() == 'true',
            enable_ocr=os.getenv('VISION_ENABLE_OCR', 'true').lower() == 'true',
            enable_scene_analysis=os.getenv('VISION_ENABLE_SCENE_ANALYSIS', 'true').lower() == 'true',
            enable_similarity_matching=os.getenv('VISION_ENABLE_SIMILARITY', 'true').lower() == 'true',
            enable_metadata_extraction=os.getenv('VISION_ENABLE_METADATA', 'true').lower() == 'true',
            enable_content_filtering=os.getenv('VISION_ENABLE_CONTENT_FILTERING', 'true').lower() == 'true',
            enable_quality_assessment=os.getenv('VISION_ENABLE_QUALITY_ASSESSMENT', 'true').lower() == 'true',
            enable_fingerprinting=os.getenv('VISION_ENABLE_FINGERPRINTING', 'true').lower() == 'true',
            enable_enhancement=os.getenv('VISION_ENABLE_ENHANCEMENT', 'false').lower() == 'true',
            enable_format_conversion=os.getenv('VISION_ENABLE_FORMAT_CONVERSION', 'true').lower() == 'true',
            enable_compression=os.getenv('VISION_ENABLE_COMPRESSION', 'true').lower() == 'true'
        )
    
    def _load_storage_config(self) -> StorageConfig:
        """Load storage configuration"""        return StorageConfig(
            storage_backend=os.getenv('VISION_STORAGE_BACKEND', 'local'),
            base_path=os.getenv('VISION_BASE_PATH', '/tmp/vision_agent'),
            cache_path=os.getenv('VISION_CACHE_PATH', '/tmp/vision_cache'),
            temp_path=os.getenv('VISION_TEMP_PATH', '/tmp/vision_temp'),
            models_path=os.getenv('VISION_MODELS_PATH', '/models'),
            results_path=os.getenv('VISION_RESULTS_PATH', '/results'),
            backup_enabled=os.getenv('VISION_BACKUP_ENABLED', 'true').lower() == 'true',
            compression_enabled=os.getenv('VISION_STORAGE_COMPRESSION', 'true').lower() == 'true',
            cleanup_interval=int(os.getenv('VISION_CLEANUP_INTERVAL', '3600')),
            max_storage_size_gb=int(os.getenv('VISION_MAX_STORAGE_SIZE_GB', '50')),
            retention_days=int(os.getenv('VISION_RETENTION_DAYS', '30'))
        )
    
    def _load_monitoring_config(self) -> MonitoringConfig:
        """Load monitoring configuration"""        return MonitoringConfig(
            enable_metrics=os.getenv('VISION_ENABLE_METRICS', 'true').lower() == 'true',
            enable_tracing=os.getenv('VISION_ENABLE_TRACING', 'true').lower() == 'true',
            log_level=os.getenv('VISION_LOG_LEVEL', 'INFO').upper(),
            metrics_port=int(os.getenv('VISION_METRICS_PORT', '8080')),
            health_check_port=int(os.getenv('VISION_HEALTH_PORT', '8081')),
            prometheus_enabled=os.getenv('VISION_PROMETHEUS_ENABLED', 'true').lower() == 'true',
            jaeger_enabled=os.getenv('VISION_JAEGER_ENABLED', 'false').lower() == 'true'
        )
    
    def _apply_environment_overrides(self):
        """Apply environment-specific configuration overrides"""        if self.environment == 'production':
            self.performance.optimization_level = "O3"
            self.security.privacy_level = PrivacyLevel.HIGH
            self.monitoring.enable_tracing = True
            self.storage.backup_enabled = True
        elif self.environment == 'development':
            self.models["yolo"].precision = ModelPrecision.FP32
            self.performance.timeout_seconds = 60
            self.monitoring.log_level = "DEBUG"
        elif self.environment == 'enterprise':
            self.security.privacy_level = PrivacyLevel.ENTERPRISE_COMPLIANCE
            self.performance.tensor_parallelism = True
            self.storage.compression_enabled = True
            self.monitoring.enable_metrics = True
    
    def _validate_configuration(self):
        """Validate configuration settings"""        # Validate performance settings
        if self.performance.max_concurrent_tasks < 1:
            raise ValueError("max_concurrent_tasks must be at least 1")
        
        if self.performance.memory_limit_mb < 512:
            raise ValueError("memory_limit_mb must be at least 512")
        
        # Validate model paths
        for name, model_config in self.models.items():
            if model_config.enabled and model_config.path:
                model_path = Path(model_config.path)
                if not model_path.exists() and not model_config.url:
                    logger.warning(f"Model path does not exist and no URL provided: {model_config.path}")
        
        # Validate security settings
        if self.security.max_file_size_mb < 1:
            raise ValueError("max_file_size_mb must be at least 1")
        
        # Validate quality settings
        min_w, min_h = self.quality.min_resolution
        max_w, max_h = self.quality.max_resolution
        
        if min_w >= max_w or min_h >= max_h:
            raise ValueError("min_resolution must be smaller than max_resolution")
    
    @lru_cache(maxsize=32)
    def get_model_config(self, model_name: str) -> Optional[ModelConfig]:
        """Get configuration for a specific model"""        return self.models.get(model_name)
    
    def get_processing_mode_config(self, mode: ProcessingMode) -> Dict[str, Any]:
        """Get configuration for a specific processing mode"""        mode_configs = {
            ProcessingMode.FAST: {
                "batch_size": 16,
                "precision": ModelPrecision.FP16,
                "timeout": 15,
                "quality_threshold": 0.6
            },
            ProcessingMode.BALANCED: {
                "batch_size": 8,
                "precision": ModelPrecision.FP32,
                "timeout": 30,
                "quality_threshold": 0.7
            },
            ProcessingMode.HIGH_QUALITY: {
                "batch_size": 4,
                "precision": ModelPrecision.FP32,
                "timeout": 60,
                "quality_threshold": 0.85
            },
            ProcessingMode.ENTERPRISE: {
                "batch_size": 2,
                "precision": ModelPrecision.FP32,
                "timeout": 120,
                "quality_threshold": 0.9
            },
            ProcessingMode.ULTRA_PERFORMANCE: {
                "batch_size": 32,
                "precision": ModelPrecision.INT8,
                "timeout": 10,
                "quality_threshold": 0.5
            }
        }
        return mode_configs.get(mode, mode_configs[ProcessingMode.BALANCED])
    
    def update_config(self, section: str, key: str, value: Any):
        """Update a specific configuration value"""        if hasattr(self, section):
            config_section = getattr(self, section)
            if hasattr(config_section, key):
                setattr(config_section, key, value)
                logger.info(f"Updated configuration: {section}.{key} = {value}")
            else:
                logger.warning(f"Configuration key not found: {section}.{key}")
        else:
            logger.warning(f"Configuration section not found: {section}")
    
    def export_config(self, file_path: Optional[str] = None) -> Dict[str, Any]:
        """Export current configuration to dictionary or file"""        config_dict = {
            'environment': self.environment,
            'models': {name: {
                'name': model.name,
                'path': model.path,
                'url': model.url,
                'version': model.version,
                'confidence_threshold': model.confidence_threshold,
                'enabled': model.enabled,
                'cache_size': model.cache_size,
                'gpu_acceleration': model.gpu_acceleration,
                'max_batch_size': model.max_batch_size,
                'precision': model.precision.value,
                'inference_mode': model.inference_mode
            } for name, model in self.models.items()},
            'performance': {
                'max_concurrent_tasks': self.performance.max_concurrent_tasks,
                'memory_limit_mb': self.performance.memory_limit_mb,
                'cache_enabled': self.performance.cache_enabled,
                'timeout_seconds': self.performance.timeout_seconds,
                'gpu_memory_fraction': self.performance.gpu_memory_fraction,
                'async_processing': self.performance.async_processing
            },
            'security': {
                'privacy_level': self.security.privacy_level.value,
                'remove_exif': self.security.remove_exif,
                'face_anonymization': self.security.face_anonymization,
                'content_filtering': self.security.content_filtering,
                'audit_logging': self.security.audit_logging,
                'encrypted_storage': self.security.encrypted_storage
            },
            'quality': {
                'min_resolution': self.quality.min_resolution,
                'max_resolution': self.quality.max_resolution,
                'compression_quality': self.quality.compression_quality,
                'auto_enhancement': self.quality.auto_enhancement,
                'noise_reduction': self.quality.noise_reduction
            }
        }
        
        if file_path:
            with open(file_path, 'w') as f:
                yaml.dump(config_dict, f, default_flow_style=False, indent=2)
            logger.info(f"Configuration exported to: {file_path}")
        
        return config_dict
    
    def is_gpu_available(self) -> bool:
        """Check if GPU is available for processing"""        try:
            return torch.cuda.is_available() and self.performance.gpu_memory_fraction > 0
        except ImportError:
            return False
    
    def get_device_info(self) -> Dict[str, Any]:
        """Get device and system information"""        info = {
            'platform': platform.system(),
            'architecture': platform.architecture()[0],
            'cpu_count': os.cpu_count(),
            'python_version': platform.python_version(),
            'gpu_available': False,
            'gpu_count': 0,
            'gpu_memory_gb': 0
        }
        
        try:
            if torch.cuda.is_available():
                info['gpu_available'] = True
                info['gpu_count'] = torch.cuda.device_count()
                info['gpu_memory_gb'] = torch.cuda.get_device_properties(0).total_memory / (1024**3)
                info['gpu_name'] = torch.cuda.get_device_name(0)
        except ImportError:
            pass
        
        return info

# Global configuration instance
vision_config = None

def get_vision_config(config_path: Optional[str] = None, 
                     environment: Optional[str] = None) -> VisionAgentConfig:
    """Get or create global vision configuration instance"""    global vision_config
    
    if vision_config is None:
        vision_config = VisionAgentConfig(config_path=config_path, environment=environment)
    
    return vision_config

def reset_vision_config():
    """Reset global configuration (useful for testing)"""    global vision_config
    vision_config = None
        self.environment = os.getenv('ENVIRONMENT', 'development')
        
        # Initialize default configurations
        self._initialize_default_configs()
        
        # Load configuration from file if provided
        if config_path and os.path.exists(config_path):
            self._load_from_file(config_path)
        
        # Override with environment variables
        self._load_from_environment()

    def _initialize_default_configs(self):
        """Initialize default configuration values"""        
        # Processing mode configuration
        self.processing_mode = ProcessingMode.BALANCED
        
        # Performance configuration
        self.performance = PerformanceConfig(
            max_concurrent_tasks=4,
            memory_limit_mb=2048,
            cache_enabled=True,
            cache_size_mb=512,
            timeout_seconds=30,
            retry_attempts=3,
            batch_processing=True,
            gpu_memory_fraction=0.7
        )
        
        # Security configuration
        self.security = SecurityConfig(
            privacy_level=PrivacyLevel.STANDARD,
            remove_exif=True,
            face_anonymization=True,
            watermark_removal=False,
            content_filtering=True,
            audit_logging=True,
            encrypted_storage=True,
            secure_deletion=True
        )
        
        # Quality configuration
        self.quality = QualityConfig(
            min_resolution=(640, 480),
            max_resolution=(4096, 4096),
            supported_formats=['jpg', 'jpeg', 'png', 'webp', 'tiff', 'bmp'],
            compression_quality=85,
            auto_enhancement=True,
            noise_reduction=True,
            sharpening=False
        )
        
        # Model configurations
        self.models = {
            'object_detection': {
                'yolo': ModelConfig(
                    name='yolo_v8',
                    path='models/yolo/yolov8n.pt',
                    confidence_threshold=0.5,
                    enabled=True,
                    cache_size=50,
                    gpu_acceleration=True,
                    max_batch_size=8
                ),
                'ssd': ModelConfig(
                    name='ssd_mobilenet',
                    path='models/ssd/ssd_mobilenet_v2.pb',
                    confidence_threshold=0.4,
                    enabled=True,
                    cache_size=30,
                    gpu_acceleration=True,
                    max_batch_size=4
                )
            },
            'face_recognition': {
                'opencv': ModelConfig(
                    name='opencv_face_cascade',
                    path='models/opencv/haarcascade_frontalface_default.xml',
                    confidence_threshold=0.3,
                    enabled=True,
                    cache_size=20,
                    gpu_acceleration=False,
                    max_batch_size=1
                )
            },
            'feature_extraction': {
                'resnet50': ModelConfig(
                    name='resnet50',
                    path='models/resnet/resnet50_weights_tf_dim_ordering_tf_kernels_notop.h5',
                    confidence_threshold=0.0,
                    enabled=True,
                    cache_size=100,
                    gpu_acceleration=True,
                    max_batch_size=16
                )
            },
            'ocr': {
                'tesseract': ModelConfig(
                    name='tesseract',
                    path='/usr/share/tesseract-ocr/5/tessdata/',
                    confidence_threshold=0.6,
                    enabled=True,
                    cache_size=10,
                    gpu_acceleration=False,
                    max_batch_size=1
                )
            }
        }
        
        # Processing pipelines configuration
        self.pipelines = {
            'image_processing': {
                'enhancement_enabled': True,
                'quality_assessment': True,
                'format_conversion': True,
                'watermarking': False,
                'metadata_extraction': True
            },
            'video_analysis': {
                'frame_extraction': True,
                'scene_detection': True,
                'motion_analysis': True,
                'thumbnail_generation': True,
                'quality_assessment': True
            },
            'object_detection': {
                'multi_model_ensemble': True,
                'confidence_voting': True,
                'non_max_suppression': True,
                'class_filtering': True,
                'bbox_refinement': True
            },
            'face_processing': {
                'detection_enabled': True,
                'recognition_enabled': False,  # Privacy by default
                'emotion_analysis': False,
                'age_estimation': False,
                'anonymization_required': True
            }
        }
        
        # Storage configuration
        self.storage = {
            'temp_dir': '/tmp/vision_agent',
            'cache_dir': '/var/cache/vision_agent',
            'models_dir': '/opt/vision_agent/models',
            'logs_dir': '/var/log/vision_agent',
            'max_temp_size_mb': 1024,
            'cleanup_interval_hours': 24,
            'compression_enabled': True
        }
        
        # Logging configuration
        self.logging = {
            'level': 'INFO',
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            'file_logging': True,
            'console_logging': True,
            'max_log_size_mb': 100,
            'backup_count': 5,
            'structured_logging': True
        }
        
        # Monitoring configuration
        self.monitoring = {
            'metrics_enabled': True,
            'performance_tracking': True,
            'error_tracking': True,
            'health_checks': True,
            'metrics_export_interval': 60,
            'alert_thresholds': {
                'error_rate': 0.05,
                'response_time_p95': 5.0,
                'memory_usage': 0.8,
                'disk_usage': 0.9
            }
        }

    def _load_from_file(self, config_path: str):
        """Load configuration from JSON file"""        try:
            with open(config_path, 'r') as f:
                config_data = json.load(f)
            
            # Update configurations with file data
            self._update_config_from_dict(config_data)
            
            logger.info(f"Configuration loaded from {config_path}")
            
        except Exception as e:
            logger.error(f"Failed to load configuration from {config_path}: {e}")
            raise

    def _load_from_environment(self):
        """Load configuration from environment variables"""        try:
            # Processing mode
            if 'VISION_PROCESSING_MODE' in os.environ:
                mode_str = os.environ['VISION_PROCESSING_MODE'].upper()
                if hasattr(ProcessingMode, mode_str):
                    self.processing_mode = getattr(ProcessingMode, mode_str)
            
            # Performance settings
            if 'VISION_MAX_CONCURRENT_TASKS' in os.environ:
                self.performance.max_concurrent_tasks = int(os.environ['VISION_MAX_CONCURRENT_TASKS'])
            
            if 'VISION_MEMORY_LIMIT_MB' in os.environ:
                self.performance.memory_limit_mb = int(os.environ['VISION_MEMORY_LIMIT_MB'])
            
            if 'VISION_TIMEOUT_SECONDS' in os.environ:
                self.performance.timeout_seconds = int(os.environ['VISION_TIMEOUT_SECONDS'])
            
            # Security settings
            if 'VISION_PRIVACY_LEVEL' in os.environ:
                privacy_str = os.environ['VISION_PRIVACY_LEVEL'].upper()
                if hasattr(PrivacyLevel, privacy_str):
                    self.security.privacy_level = getattr(PrivacyLevel, privacy_str)
            
            if 'VISION_REMOVE_EXIF' in os.environ:
                self.security.remove_exif = os.environ['VISION_REMOVE_EXIF'].lower() == 'true'
            
            if 'VISION_FACE_ANONYMIZATION' in os.environ:
                self.security.face_anonymization = os.environ['VISION_FACE_ANONYMIZATION'].lower() == 'true'
            
            # Storage settings
            if 'VISION_TEMP_DIR' in os.environ:
                self.storage['temp_dir'] = os.environ['VISION_TEMP_DIR']
            
            if 'VISION_MODELS_DIR' in os.environ:
                self.storage['models_dir'] = os.environ['VISION_MODELS_DIR']
            
            # Logging settings
            if 'VISION_LOG_LEVEL' in os.environ:
                self.logging['level'] = os.environ['VISION_LOG_LEVEL'].upper()
            
            logger.info("Environment configuration applied")
            
        except Exception as e:
            logger.error(f"Failed to load environment configuration: {e}")

    def _update_config_from_dict(self, config_data: Dict[str, Any]):
        """Update configuration from dictionary"""        try:
            # Update performance config
            if 'performance' in config_data:
                perf_data = config_data['performance']
                for key, value in perf_data.items():
                    if hasattr(self.performance, key):
                        setattr(self.performance, key, value)
            
            # Update security config
            if 'security' in config_data:
                sec_data = config_data['security']
                for key, value in sec_data.items():
                    if hasattr(self.security, key):
                        if key == 'privacy_level' and isinstance(value, str):
                            setattr(self.security, key, PrivacyLevel(value))
                        else:
                            setattr(self.security, key, value)
            
            # Update quality config
            if 'quality' in config_data:
                qual_data = config_data['quality']
                for key, value in qual_data.items():
                    if hasattr(self.quality, key):
                        setattr(self.quality, key, value)
            
            # Update other configurations
            for config_name in ['models', 'pipelines', 'storage', 'logging', 'monitoring']:
                if config_name in config_data:
                    setattr(self, config_name, {
                        **getattr(self, config_name),
                        **config_data[config_name]
                    })
            
        except Exception as e:
            logger.error(f"Failed to update configuration from dictionary: {e}")

    def get_model_config(self, model_category: str, model_name: str) -> Optional[ModelConfig]:
        """Get configuration for specific model"""        try:
            if model_category in self.models:
                if model_name in self.models[model_category]:
                    model_data = self.models[model_category][model_name]
                    if isinstance(model_data, dict):
                        return ModelConfig(**model_data)
                    return model_data
            return None
        except Exception as e:
            logger.error(f"Failed to get model config for {model_category}/{model_name}: {e}")
            return None

    def get_pipeline_config(self, pipeline_name: str) -> Dict[str, Any]:
        """Get configuration for processing pipeline"""        return self.pipelines.get(pipeline_name, {})

    def is_feature_enabled(self, feature_name: str) -> bool:
        """Check if a feature is enabled"""        try:
            # Check in pipelines
            for pipeline_config in self.pipelines.values():
                if feature_name in pipeline_config:
                    return pipeline_config[feature_name]
            
            # Check in models
            for model_category in self.models.values():
                for model_config in model_category.values():
                    if isinstance(model_config, dict) and 'enabled' in model_config:
                        if model_config.get('name') == feature_name:
                            return model_config['enabled']
                    elif hasattr(model_config, 'enabled') and model_config.name == feature_name:
                        return model_config.enabled
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to check feature status for {feature_name}: {e}")
            return False

    def get_performance_settings(self) -> PerformanceConfig:
        """Get performance configuration"""        return self.performance

    def get_security_settings(self) -> SecurityConfig:
        """Get security configuration"""  
        return self.security

    def get_quality_settings(self) -> QualityConfig:
        """Get quality configuration"""        return self.quality

    def validate_configuration(self) -> bool:
        """Validate configuration settings"""        try:
            errors = []
            
            # Validate performance settings
            if self.performance.max_concurrent_tasks < 1:
                errors.append("max_concurrent_tasks must be >= 1")
            
            if self.performance.memory_limit_mb < 512:
                errors.append("memory_limit_mb must be >= 512")
            
            if self.performance.timeout_seconds < 5:
                errors.append("timeout_seconds must be >= 5")
            
            # Validate quality settings
            if self.quality.compression_quality < 1 or self.quality.compression_quality > 100:
                errors.append("compression_quality must be between 1-100")
            
            min_w, min_h = self.quality.min_resolution
            max_w, max_h = self.quality.max_resolution
            
            if min_w >= max_w or min_h >= max_h:
                errors.append("max_resolution must be larger than min_resolution")
            
            # Validate storage paths
            required_dirs = ['temp_dir', 'cache_dir', 'models_dir', 'logs_dir']
            for dir_key in required_dirs:
                if dir_key in self.storage:
                    dir_path = self.storage[dir_key]
                    if not os.path.isabs(dir_path):
                        errors.append(f"{dir_key} must be an absolute path")
            
            if errors:
                logger.error(f"Configuration validation failed: {errors}")
                return False
            
            logger.info("Configuration validation passed")
            return True
            
        except Exception as e:
            logger.error(f"Configuration validation error: {e}")
            return False

    def create_directories(self) -> bool:
        """Create required directories"""        try:
            dirs_to_create = [
                self.storage['temp_dir'],
                self.storage['cache_dir'],
                self.storage['models_dir'],
                self.storage['logs_dir']
            ]
            
            for dir_path in dirs_to_create:
                Path(dir_path).mkdir(parents=True, exist_ok=True)
                logger.info(f"Directory created/verified: {dir_path}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to create directories: {e}")
            return False

    def save_to_file(self, output_path: str) -> bool:
        """Save current configuration to file"""        try:
            config_dict = self.to_dict()
            
            with open(output_path, 'w') as f:
                json.dump(config_dict, f, indent=2, default=str)
            
            logger.info(f"Configuration saved to {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save configuration to {output_path}: {e}")
            return False

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""        try:
            return {
                'processing_mode': self.processing_mode.value,
                'performance': {
                    'max_concurrent_tasks': self.performance.max_concurrent_tasks,
                    'memory_limit_mb': self.performance.memory_limit_mb,
                    'cache_enabled': self.performance.cache_enabled,
                    'cache_size_mb': self.performance.cache_size_mb,
                    'timeout_seconds': self.performance.timeout_seconds,
                    'retry_attempts': self.performance.retry_attempts,
                    'batch_processing': self.performance.batch_processing,
                    'gpu_memory_fraction': self.performance.gpu_memory_fraction
                },
                'security': {
                    'privacy_level': self.security.privacy_level.value,
                    'remove_exif': self.security.remove_exif,
                    'face_anonymization': self.security.face_anonymization,
                    'watermark_removal': self.security.watermark_removal,
                    'content_filtering': self.security.content_filtering,
                    'audit_logging': self.security.audit_logging,
                    'encrypted_storage': self.security.encrypted_storage,
                    'secure_deletion': self.security.secure_deletion
                },
                'quality': {
                    'min_resolution': self.quality.min_resolution,
                    'max_resolution': self.quality.max_resolution,
                    'supported_formats': self.quality.supported_formats,
                    'compression_quality': self.quality.compression_quality,
                    'auto_enhancement': self.quality.auto_enhancement,
                    'noise_reduction': self.quality.noise_reduction,
                    'sharpening': self.quality.sharpening
                },
                'models': self.models,
                'pipelines': self.pipelines,
                'storage': self.storage,
                'logging': self.logging,
                'monitoring': self.monitoring
            }
            
        except Exception as e:
            logger.error(f"Failed to convert configuration to dict: {e}")
            return {}

    def get_environment_info(self) -> Dict[str, Any]:
        """Get environment information"""        return {
            'environment': self.environment,
            'config_path': self.config_path,
            'processing_mode': self.processing_mode.value,
            'privacy_level': self.security.privacy_level.value,
            'gpu_enabled': any(
                model.get('gpu_acceleration', False) 
                for category in self.models.values() 
                for model in category.values()
                if isinstance(model, dict)
            )
        }

# Global configuration instance
vision_config = VisionAgentConfig()

# Configuration validation
if not vision_config.validate_configuration():
    logger.warning("Configuration validation failed - using defaults")

# Create required directories
if not vision_config.create_directories():
    logger.warning("Failed to create some directories")
