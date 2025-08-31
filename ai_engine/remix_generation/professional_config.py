#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Professional Remix System Configuration
================================================================================
Module: ai_engine/remix_generation/professional_config.py
Author: Fahed Mlaiel (mlaiel@live.de)
Architecture: Production-Ready Enterprise Configuration (Level 4)
Created: 2025-01-20
================================================================================

Professional configuration for the AI remix system.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import os
from pathlib import Path


class DeploymentEnvironment(Enum):
    """Deployment environment types"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    ENTERPRISE = "enterprise"


@dataclass
class AIModelConfig:
    """Configuration for AI models"""
    # Model availability
    wavenet_enabled: bool = True
    musenet_enabled: bool = True
    aiva_enabled: bool = True
    magenta_enabled: bool = True
    jukebox_enabled: bool = True
    
    # Model performance settings
    gpu_acceleration: bool = True
    model_cache_size_gb: int = 8
    concurrent_model_loading: int = 3
    model_timeout_seconds: int = 300
    
    # Quality settings
    default_quality_threshold: float = 0.85
    minimum_quality_threshold: float = 0.70
    enable_quality_auto_adjustment: bool = True


@dataclass
class AudioProcessingConfig:
    """Configuration for audio processing"""
    # Audio format settings
    default_sample_rate: int = 44100
    supported_sample_rates: List[int] = field(default_factory=lambda: [22050, 44100, 48000, 96000])
    default_bit_depth: int = 24
    default_channels: int = 2
    
    # Processing settings
    buffer_size: int = 1024
    max_audio_duration_seconds: int = 600  # 10 minutes
    enable_real_time_processing: bool = True
    processing_latency_target_ms: float = 100.0
    
    # Quality settings
    enable_noise_reduction: bool = True
    enable_dynamic_range_optimization: bool = True
    enable_stereo_enhancement: bool = True


@dataclass
class CollaborationConfig:
    """Configuration for collaboration features"""
    # Session settings
    max_concurrent_sessions: int = 100
    max_collaborators_per_session: int = 10
    session_timeout_minutes: int = 480  # 8 hours
    
    # Real-time settings
    websocket_heartbeat_seconds: int = 30
    max_message_size_kb: int = 1024
    collaboration_latency_target_ms: float = 50.0
    
    # Conflict resolution
    default_conflict_resolution: str = "ai_mediated"
    enable_automatic_conflict_resolution: bool = True
    conflict_resolution_timeout_seconds: int = 30


@dataclass
class MasteringConfig:
    """Configuration for professional mastering"""
    # Mastering targets
    default_target_lufs: float = -16.0
    supported_mastering_targets: List[str] = field(default_factory=lambda: 
        ["streaming", "radio", "club", "vinyl", "cd", "audiophile"])
    
    # Quality settings
    enable_professional_mastering: bool = True
    enable_multiband_processing: bool = True
    enable_harmonic_enhancement: bool = True
    
    # Loudness standards
    streaming_lufs: float = -16.0
    radio_lufs: float = -12.0
    club_lufs: float = -8.0
    broadcast_lufs: float = -23.0
    vinyl_lufs: float = -18.0
    cd_lufs: float = -16.0
    audiophile_lufs: float = -20.0


@dataclass
class SecurityConfig:
    """Configuration for security features"""
    # Authentication
    enable_user_authentication: bool = True
    session_timeout_minutes: int = 120
    max_failed_login_attempts: int = 5
    
    # Rate limiting
    enable_rate_limiting: bool = True
    requests_per_minute: int = 60
    concurrent_requests_per_user: int = 5
    
    # Data protection
    enable_data_encryption: bool = True
    temporary_file_cleanup: bool = True
    audit_logging: bool = True


@dataclass
class PerformanceConfig:
    """Configuration for performance optimization"""
    # Resource limits
    max_cpu_cores: int = 0  # 0 = auto-detect
    max_memory_gb: int = 16
    max_gpu_memory_gb: int = 8
    
    # Caching
    enable_model_caching: bool = True
    enable_result_caching: bool = True
    cache_size_gb: int = 10
    cache_expiry_hours: int = 24
    
    # Processing
    enable_parallel_processing: bool = True
    max_concurrent_jobs: int = 5
    job_queue_size: int = 100


@dataclass
class StorageConfig:
    """Configuration for storage settings"""
    # Paths
    base_storage_path: str = "/tmp/ainflue_remix"
    input_storage_path: str = "/tmp/ainflue_remix/input"
    output_storage_path: str = "/tmp/ainflue_remix/output"
    temp_storage_path: str = "/tmp/ainflue_remix/temp"
    
    # Retention
    temp_file_retention_hours: int = 2
    output_file_retention_days: int = 30
    
    # Limits
    max_file_size_mb: int = 500
    max_storage_per_user_gb: int = 10


@dataclass
class MonitoringConfig:
    """Configuration for monitoring and logging"""
    # Logging
    log_level: str = "INFO"
    enable_detailed_logging: bool = True
    log_file_path: str = "/var/log/ainflue/remix.log"
    
    # Metrics
    enable_metrics_collection: bool = True
    metrics_retention_days: int = 30
    
    # Health checks
    health_check_interval_seconds: int = 30
    enable_performance_monitoring: bool = True


@dataclass
class ProfessionalRemixConfig:
    """Complete professional remix system configuration"""
    # Environment
    environment: DeploymentEnvironment = DeploymentEnvironment.PRODUCTION
    debug_mode: bool = False
    
    # Component configurations
    ai_models: AIModelConfig = field(default_factory=AIModelConfig)
    audio_processing: AudioProcessingConfig = field(default_factory=AudioProcessingConfig)
    collaboration: CollaborationConfig = field(default_factory=CollaborationConfig)
    mastering: MasteringConfig = field(default_factory=MasteringConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    performance: PerformanceConfig = field(default_factory=PerformanceConfig)
    storage: StorageConfig = field(default_factory=StorageConfig)
    monitoring: MonitoringConfig = field(default_factory=MonitoringConfig)
    
    # Feature flags
    enable_experimental_features: bool = False
    enable_advanced_ai_features: bool = True
    enable_cloud_integration: bool = False
    
    @classmethod
    def from_environment(cls, env: DeploymentEnvironment = None) -> 'ProfessionalRemixConfig':
        """Create configuration based on environment"""
        if env is None:
            env_str = os.getenv('AINFLUE_ENVIRONMENT', 'production').lower()
            env = DeploymentEnvironment(env_str)
        
        config = cls(environment=env)
        
        # Adjust settings based on environment
        if env == DeploymentEnvironment.DEVELOPMENT:
            config.debug_mode = True
            config.ai_models.model_cache_size_gb = 4
            config.performance.max_concurrent_jobs = 2
            config.security.enable_rate_limiting = False
            config.monitoring.log_level = "DEBUG"
            config.enable_experimental_features = True
            
        elif env == DeploymentEnvironment.STAGING:
            config.ai_models.model_cache_size_gb = 6
            config.performance.max_concurrent_jobs = 3
            config.monitoring.log_level = "INFO"
            
        elif env == DeploymentEnvironment.PRODUCTION:
            config.ai_models.model_cache_size_gb = 8
            config.performance.max_concurrent_jobs = 5
            config.security.enable_rate_limiting = True
            config.monitoring.log_level = "INFO"
            config.monitoring.enable_performance_monitoring = True
            
        elif env == DeploymentEnvironment.ENTERPRISE:
            config.ai_models.model_cache_size_gb = 16
            config.performance.max_concurrent_jobs = 10
            config.security.enable_data_encryption = True
            config.security.audit_logging = True
            config.collaboration.max_concurrent_sessions = 500
            config.enable_advanced_ai_features = True
            config.enable_cloud_integration = True
        
        return config
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            "environment": self.environment.value,
            "debug_mode": self.debug_mode,
            "ai_models": {
                "wavenet_enabled": self.ai_models.wavenet_enabled,
                "musenet_enabled": self.ai_models.musenet_enabled,
                "aiva_enabled": self.ai_models.aiva_enabled,
                "magenta_enabled": self.ai_models.magenta_enabled,
                "jukebox_enabled": self.ai_models.jukebox_enabled,
                "gpu_acceleration": self.ai_models.gpu_acceleration,
                "model_cache_size_gb": self.ai_models.model_cache_size_gb,
                "concurrent_model_loading": self.ai_models.concurrent_model_loading,
                "default_quality_threshold": self.ai_models.default_quality_threshold
            },
            "audio_processing": {
                "default_sample_rate": self.audio_processing.default_sample_rate,
                "default_bit_depth": self.audio_processing.default_bit_depth,
                "buffer_size": self.audio_processing.buffer_size,
                "max_audio_duration_seconds": self.audio_processing.max_audio_duration_seconds,
                "enable_real_time_processing": self.audio_processing.enable_real_time_processing,
                "processing_latency_target_ms": self.audio_processing.processing_latency_target_ms
            },
            "collaboration": {
                "max_concurrent_sessions": self.collaboration.max_concurrent_sessions,
                "max_collaborators_per_session": self.collaboration.max_collaborators_per_session,
                "session_timeout_minutes": self.collaboration.session_timeout_minutes,
                "default_conflict_resolution": self.collaboration.default_conflict_resolution,
                "collaboration_latency_target_ms": self.collaboration.collaboration_latency_target_ms
            },
            "mastering": {
                "default_target_lufs": self.mastering.default_target_lufs,
                "enable_professional_mastering": self.mastering.enable_professional_mastering,
                "enable_multiband_processing": self.mastering.enable_multiband_processing,
                "streaming_lufs": self.mastering.streaming_lufs,
                "radio_lufs": self.mastering.radio_lufs,
                "club_lufs": self.mastering.club_lufs
            },
            "performance": {
                "max_cpu_cores": self.performance.max_cpu_cores,
                "max_memory_gb": self.performance.max_memory_gb,
                "max_concurrent_jobs": self.performance.max_concurrent_jobs,
                "enable_parallel_processing": self.performance.enable_parallel_processing
            },
            "storage": {
                "base_storage_path": self.storage.base_storage_path,
                "max_file_size_mb": self.storage.max_file_size_mb,
                "temp_file_retention_hours": self.storage.temp_file_retention_hours
            },
            "monitoring": {
                "log_level": self.monitoring.log_level,
                "enable_metrics_collection": self.monitoring.enable_metrics_collection,
                "enable_performance_monitoring": self.monitoring.enable_performance_monitoring
            },
            "feature_flags": {
                "enable_experimental_features": self.enable_experimental_features,
                "enable_advanced_ai_features": self.enable_advanced_ai_features,
                "enable_cloud_integration": self.enable_cloud_integration
            }
        }
    
    def validate(self) -> List[str]:
        """Validate configuration and return any issues"""
        issues = []
        
        # Validate storage paths
        try:
            Path(self.storage.base_storage_path).mkdir(parents=True, exist_ok=True)
        except Exception as e:
            issues.append(f"Invalid storage path: {e}")
        
        # Validate resource limits
        if self.performance.max_memory_gb < 4:
            issues.append("Minimum 4GB memory required")
        
        if self.audio_processing.max_audio_duration_seconds > 3600:
            issues.append("Maximum audio duration should not exceed 1 hour")
        
        # Validate mastering settings
        if not (-30.0 <= self.mastering.default_target_lufs <= 0.0):
            issues.append("Target LUFS should be between -30 and 0")
        
        return issues


# Global configuration instance
professional_config = ProfessionalRemixConfig.from_environment()

# Export main functionality
__all__ = [
    "ProfessionalRemixConfig",
    "DeploymentEnvironment",
    "AIModelConfig",
    "AudioProcessingConfig",
    "CollaborationConfig",
    "MasteringConfig",
    "SecurityConfig",
    "PerformanceConfig",
    "StorageConfig",
    "MonitoringConfig",
    "professional_config"
]