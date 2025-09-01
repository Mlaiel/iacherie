"""Audio Agent Configuration - Enterprise Production Settings

Professional configuration management for the Audio Agent module with comprehensive
settings for AI models, business logic, security, and performance optimization.

Author: Fahed Mlaiel <mlaiel@live.de>
Project Team Specialties: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + IA Prompt Engineer

⚠️  PROPRIETARY CONFIGURATION - AUTHORIZED ACCESS ONLY ⚠️
This configuration contains proprietary settings and business logic owned exclusively by Fahed Mlaiel.
Unauthorized access, modification, or distribution is strictly prohibited.
"""
import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from pathlib import Path

@dataclass
class AudioProcessingConfig:
    """Core audio processing configuration"""
    
    # Audio Quality Settings
    DEFAULT_SAMPLE_RATE: int = 44100
    DEFAULT_BIT_DEPTH: int = 24
    DEFAULT_FRAME_LENGTH: int = 2048
    DEFAULT_HOP_LENGTH: int = 512
    
    # Neural Processing
    N_MELS: int = 128
    N_FFT: int = 2048
    MAX_FREQUENCY: float = 8000.0
    MIN_FREQUENCY: float = 20.0
    
    # Quality Thresholds
    MINIMUM_QUALITY_SCORE: float = 0.3
    ENHANCEMENT_THRESHOLD: float = 0.7
    PROFESSIONAL_QUALITY_THRESHOLD: float = 0.85
    
    # Performance Settings
    MAX_AUDIO_DURATION_SECONDS: float = 600.0  # 10 minutes
    MAX_FILE_SIZE_MB: int = 100
    PROCESSING_TIMEOUT_SECONDS: int = 300
    MAX_CONCURRENT_PROCESSING: int = 10
    
    # GPU Settings
    USE_GPU_ACCELERATION: bool = True
    GPU_MEMORY_LIMIT_GB: float = 8.0
    CUDA_DEVICE_ID: int = 0

@dataclass 
class AIModelsConfig:
    """AI models configuration and paths"""
    
    # Model Paths (configure according to your setup)
    DIFFUSION_MODEL_PATH: str = "facebook/musicgen-small"
    MUSIC_TRANSFORMER_PATH: str = "microsoft/DialoGPT-medium" 
    AUDIO_VAE_MODEL_PATH: str = "models/audio_vae_v1.pt"
    NOISE_REDUCTION_MODEL_PATH: str = "models/denoise_model_v2.pt"
    
    # Model Settings
    DIFFUSION_INFERENCE_STEPS: int = 50
    DIFFUSION_GUIDANCE_SCALE: float = 7.5
    TRANSFORMER_MAX_LENGTH: int = 512
    VAE_LATENT_DIM: int = 256
    
    # Generation Parameters
    DEFAULT_GENERATION_DURATION: float = 30.0
    MAX_GENERATION_DURATION: float = 300.0
    DEFAULT_CREATIVITY_LEVEL: float = 0.7
    DEFAULT_QUALITY_LEVEL: str = "high"

@dataclass
class BusinessConfig:
    """Business logic and workflow configuration"""
    
    # Creator Economy Settings
    ENABLE_COLLABORATION_MATCHING: bool = True
    ENABLE_REVENUE_PROJECTION: bool = True
    ENABLE_SEO_OPTIMIZATION: bool = True
    ENABLE_COPYRIGHT_PROTECTION: bool = True
    ENABLE_MULTI_PLATFORM_DISTRIBUTION: bool = True
    
    # Platform Integration
    SUPPORTED_PLATFORMS: List[str] = None
    DEFAULT_PLATFORMS: List[str] = None
    
    # Revenue Settings  
    BASE_REVENUE_RATE_PER_PLAY: float = 0.003
    PREMIUM_QUALITY_MULTIPLIER: float = 1.5
    COLLABORATION_REVENUE_SHARE: float = 0.3
    PLATFORM_COMMISSION_RATE: float = 0.15
    
    # SEO Settings
    AUTO_GENERATE_TITLES: bool = True
    AUTO_GENERATE_DESCRIPTIONS: bool = True
    AUTO_GENERATE_TAGS: bool = True
    MAX_TAGS_PER_AUDIO: int = 20
    
    # Collaboration Settings
    MAX_COLLABORATION_MATCHES: int = 10
    COLLABORATION_SCORE_THRESHOLD: float = 0.6
    
    def __post_init__(self):
        if self.SUPPORTED_PLATFORMS is None:
            self.SUPPORTED_PLATFORMS = [
                "spotify", "youtube", "soundcloud", "apple_music",
                "bandcamp", "tidal", "deezer", "amazon_music"
            ]
        
        if self.DEFAULT_PLATFORMS is None:
            self.DEFAULT_PLATFORMS = ["spotify", "youtube", "soundcloud"]

@dataclass
class SecurityConfig:
    """Security and protection configuration"""
    
    # Content Protection
    ENABLE_CONTENT_FINGERPRINTING: bool = True
    FINGERPRINT_ALGORITHM: str = "perceptual_hash"
    COPYRIGHT_PROTECTION_LEVEL: str = "high"
    
    # File Validation
    ENABLE_MALWARE_SCANNING: bool = True
    ALLOWED_FILE_EXTENSIONS: List[str] = None
    BLOCKED_FILE_EXTENSIONS: List[str] = None
    
    # API Security
    ENABLE_RATE_LIMITING: bool = True
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_PER_HOUR: int = 1000
    API_KEY_REQUIRED: bool = True
    
    # Encryption
    ENCRYPT_STORED_AUDIO: bool = True
    ENCRYPTION_ALGORITHM: str = "AES-256"
    ENABLE_END_TO_END_ENCRYPTION: bool = True
    
    # Audit Logging
    ENABLE_AUDIT_LOGGING: bool = True
    LOG_ALL_REQUESTS: bool = True
    LOG_PROCESSING_DETAILS: bool = True
    
    def __post_init__(self):
        if self.ALLOWED_FILE_EXTENSIONS is None:
            self.ALLOWED_FILE_EXTENSIONS = [
                ".wav", ".mp3", ".flac", ".aac", ".ogg", 
                ".m4a", ".aiff", ".wma", ".ape"
            ]
        
        if self.BLOCKED_FILE_EXTENSIONS is None:
            self.BLOCKED_FILE_EXTENSIONS = [
                ".exe", ".bat", ".sh", ".py", ".js", ".php"
            ]

@dataclass
class DatabaseConfig:
    """Database and storage configuration"""
    
    # Database Settings
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://localhost/audio_agent")
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 50
    DATABASE_TIMEOUT_SECONDS: int = 30
    
    # Redis Settings
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    REDIS_MAX_CONNECTIONS: int = 100
    CACHE_TTL_SECONDS: int = 3600
    
    # File Storage
    AUDIO_STORAGE_PATH: str = "/data/audio_agent/audio_files"
    TEMP_STORAGE_PATH: str = "/tmp/audio_agent"
    BACKUP_STORAGE_PATH: str = "/backup/audio_agent"
    
    # Storage Limits
    MAX_STORAGE_PER_CREATOR_GB: float = 10.0
    STORAGE_CLEANUP_INTERVAL_HOURS: int = 24
    DELETE_TEMP_FILES_AFTER_HOURS: int = 2

@dataclass
class MonitoringConfig:
    """Monitoring and metrics configuration"""
    
    # Prometheus Settings
    ENABLE_PROMETHEUS_METRICS: bool = True
    METRICS_PORT: int = 9090
    METRICS_PATH: str = "/metrics"
    
    # Health Checks
    ENABLE_HEALTH_CHECKS: bool = True
    HEALTH_CHECK_INTERVAL_SECONDS: int = 30
    HEALTH_CHECK_TIMEOUT_SECONDS: int = 5
    
    # Performance Monitoring
    TRACK_PROCESSING_TIMES: bool = True
    TRACK_MEMORY_USAGE: bool = True
    TRACK_GPU_USAGE: bool = True
    ALERT_ON_HIGH_LATENCY: bool = True
    
    # Alerting
    MAX_PROCESSING_TIME_SECONDS: float = 60.0
    MAX_MEMORY_USAGE_PERCENT: float = 85.0
    MAX_ERROR_RATE_PERCENT: float = 5.0
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    LOG_FILE_PATH: str = "/logs/audio_agent.log"
    LOG_ROTATION_SIZE_MB: int = 100
    LOG_RETENTION_DAYS: int = 30

class AudioAgentConfig:
    """Main configuration class combining all settings"""
    
    def __init__(self, environment: str = "production"):
        self.environment = environment
        
        # Initialize all configuration sections
        self.audio = AudioProcessingConfig()
        self.ai_models = AIModelsConfig()
        self.business = BusinessConfig()
        self.security = SecurityConfig()
        self.database = DatabaseConfig()
        self.monitoring = MonitoringConfig()
        
        # Apply environment-specific overrides
        self._apply_environment_config()
        
        # Validate configuration
        self._validate_config()
    
    def _apply_environment_config(self):
        """Apply environment-specific configuration overrides"""
        
        if self.environment == "development":
            # Development overrides
            self.audio.USE_GPU_ACCELERATION = False
            self.security.ENABLE_MALWARE_SCANNING = False
            self.security.API_KEY_REQUIRED = False
            self.monitoring.LOG_LEVEL = "DEBUG"
            self.ai_models.DIFFUSION_INFERENCE_STEPS = 20  # Faster for dev
            
        elif self.environment == "testing":
            # Testing overrides
            self.audio.MAX_AUDIO_DURATION_SECONDS = 60.0  # Shorter for tests
            self.audio.MAX_FILE_SIZE_MB = 10  # Smaller for tests
            self.security.RATE_LIMIT_PER_MINUTE = 1000  # Higher for tests
            self.database.DATABASE_URL = "sqlite:///test_audio_agent.db"
            
        elif self.environment == "production":
            # Production settings (already set as defaults)
            pass
    
    def _validate_config(self):
        """Validate configuration settings"""
        
        # Validate audio settings
        assert self.audio.DEFAULT_SAMPLE_RATE > 0
        assert self.audio.MAX_AUDIO_DURATION_SECONDS > 0
        assert self.audio.MAX_FILE_SIZE_MB > 0
        
        # Validate business settings
        assert 0 <= self.business.COLLABORATION_REVENUE_SHARE <= 1
        assert 0 <= self.business.PLATFORM_COMMISSION_RATE <= 1
        
        # Validate security settings
        assert len(self.security.ALLOWED_FILE_EXTENSIONS) > 0
        assert self.security.RATE_LIMIT_PER_MINUTE > 0
        
        # Validate paths exist or can be created
        for path in [
            self.database.AUDIO_STORAGE_PATH,
            self.database.TEMP_STORAGE_PATH,
            self.database.BACKUP_STORAGE_PATH
        ]:
            Path(path).mkdir(parents=True, exist_ok=True)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get configuration summary for logging"""
        return {
            "environment": self.environment,
            "audio_processing": {
                "sample_rate": self.audio.DEFAULT_SAMPLE_RATE,
                "gpu_enabled": self.audio.USE_GPU_ACCELERATION,
                "max_duration": self.audio.MAX_AUDIO_DURATION_SECONDS
            },
            "business_features": {
                "collaboration": self.business.ENABLE_COLLABORATION_MATCHING,
                "seo_optimization": self.business.ENABLE_SEO_OPTIMIZATION,
                "copyright_protection": self.business.ENABLE_COPYRIGHT_PROTECTION
            },
            "security": {
                "content_fingerprinting": self.security.ENABLE_CONTENT_FINGERPRINTING,
                "api_key_required": self.security.API_KEY_REQUIRED,
                "rate_limiting": self.security.ENABLE_RATE_LIMITING
            }
        }

# Global configuration instance
def get_config(environment: Optional[str] = None) -> AudioAgentConfig:
    """Get configuration instance for the specified environment"""
    if environment is None:
        environment = os.getenv("AUDIO_AGENT_ENV", "production")
    
    return AudioAgentConfig(environment)

# Default configuration for import
config = get_config()

# Export configuration classes
__all__ = [
    "AudioProcessingConfig",
    "AIModelsConfig", 
    "BusinessConfig",
    "SecurityConfig",
    "DatabaseConfig",
    "MonitoringConfig",
    "AudioAgentConfig",
    "get_config",
    "config"
]
