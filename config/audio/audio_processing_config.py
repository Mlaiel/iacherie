"""Audio Processing Configuration Module for IA-Influencer Agent Platform
=====================================================================

Professional audio processing configuration management for multi-format content creators.
Supports musicians, podcasters, video creators, and influencers.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA-Influencer Agent + Content Protection Platform
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps

Copyright Notice:
⚠️ STRICT COPYRIGHT WARNING ⚠️
This code and all associated concepts, algorithms, and implementations are the exclusive 
intellectual property of Fahed Mlaiel (mlaiel@live.de). Any unauthorized use, reproduction, 
distribution, modification, or appropriation of this code, in whole or in part, without 
explicit written permission from Fahed Mlaiel is strictly prohibited and will be prosecuted 
to the full extent of the law.

Contact: mlaiel@live.de for licensing inquiries.
"""

import logging
from enum import Enum
from typing import Dict, List, Optional, Union, Any, Tuple
from dataclasses import dataclass, field
from pathlib import Path
import numpy as np

logger = logging.getLogger(__name__)


class AudioProcessingMode(Enum):
    """
Audio processing operational modes"""

    REALTIME = "realtime"
    BATCH = "batch"
    STREAMING = "streaming"
    OFFLINE = "offline"


class AudioQualityTier(Enum):
    """Audio quality processing tiers"""

    BROADCAST = "broadcast"      # 96kHz/24bit - Professional broadcast
    STUDIO = "studio"           # 48kHz/24bit - Studio recording
    STREAMING = "streaming"     # 44.1kHz/16bit - High quality streaming
    PODCAST = "podcast"         # 22kHz/16bit - Speech optimized
    MOBILE = "mobile"           # 16kHz/16bit - Mobile optimized


class ProcessingComplexity(Enum):
    """Audio processing complexity levels"""

    MINIMAL = "minimal"         # Basic processing only
    STANDARD = "standard"       # Standard processing pipeline
    ADVANCED = "advanced"       # Advanced ML-enhanced processing
    ULTRA = "ultra"            # Full AI-powered processing


class AudioBufferStrategy(Enum):
    """Audio buffer management strategies"""

    FIXED = "fixed"             # Fixed buffer size
    ADAPTIVE = "adaptive"       # Adaptive buffer sizing
    PREDICTIVE = "predictive"   # ML-based buffer prediction
    REALTIME = "realtime"       # Ultra-low latency


@dataclass
class PerformanceMetrics:
    """Audio processing performance metrics configuration"""
    max_latency_ms: float = 10.0
    target_cpu_usage: float = 0.7
    memory_limit_mb: int = 512
    throughput_target: int = 1000  # files per hour
    quality_threshold: float = 0.95
    error_tolerance: float = 0.001


@dataclass
class AudioProcessingLimits:
    """
Audio processing resource limits"""
    max_file_size_mb: int = 500
    max_duration_seconds: int = 3600
    max_sample_rate: int = 192000
    max_bit_depth: int = 32
    max_channels: int = 8
    min_sample_rate: int = 8000
    min_bit_depth: int = 8
    concurrent_processes: int = 4


@dataclass
class MLProcessingConfig:
    """
Machine learning audio processing configuration"""
    enable_ai_enhancement: bool = True
    enable_noise_reduction: bool = True
    enable_auto_mastering: bool = False
    enable_vocal_isolation: bool = True
    enable_genre_detection: bool = True
    model_precision: str = "fp16"  # fp32, fp16, int8
    batch_inference: bool = True
    gpu_acceleration: bool = True
    model_cache_size: int = 1024  # MB


@dataclass
class SecurityConfig:
    """Audio processing security configuration"""
    enable_content_scanning: bool = True
    enable_copyright_detection: bool = True
    enable_malware_scanning: bool = True
    max_upload_rate: int = 10  # files per minute
    enable_watermarking: bool = True
    privacy_mode: bool = False
    audit_logging: bool = True


class AudioProcessingConfig:
    """
    Comprehensive audio processing configuration manager
    
    Manages all aspects of audio processing configuration for the IA-Influencer platform,
    supporting multiple content creator types and use cases.
    """
    
    def __init__(self):
        """
Initialize audio processing configuration"""
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Core configuration
        self._processing_mode = AudioProcessingMode.BATCH
        self._quality_tier = AudioQualityTier.STREAMING
        self._complexity = ProcessingComplexity.ADVANCED
        self._buffer_strategy = AudioBufferStrategy.ADAPTIVE
        
        # Performance and limits
        self.performance_metrics = PerformanceMetrics()
        self.processing_limits = AudioProcessingLimits()
        
        # ML and AI configuration
        self.ml_config = MLProcessingConfig()
        
        # Security configuration
        self.security_config = SecurityConfig()
        
        # Format support
        self._supported_formats = [
            "wav", "mp3", "flac", "aac", "ogg", "m4a", 
            "wma", "opus", "amr", "3gp"
        ]
        
        # Processing pipeline configuration
        self._pipeline_config = self._initialize_pipeline_config()
        
        # Platform-specific configurations
        self._platform_configs = self._initialize_platform_configs()
        
        self.logger.info("AudioProcessingConfig initialized successfully")
    
    def _initialize_pipeline_config(self) -> Dict[str, Any]:
        """Initialize processing pipeline configuration"""
        return {
            "preprocessing": {
                "normalize_audio": True,
                "remove_silence": True,
                "noise_gate_threshold": -50.0,  # dB
                "high_pass_filter": 80.0,  # Hz
                "low_pass_filter": 20000.0,  # Hz
                "dc_offset_removal": True
            },
            "enhancement": {
                "eq_enabled": True,
                "compression_enabled": True,
                "limiter_enabled": True,
                "stereo_widening": False,
                "harmonic_enhancement": True,
                "transient_shaping": False
            },
            "analysis": {
                "spectral_analysis": True,
                "tempo_detection": True,
                "key_detection": True,
                "loudness_analysis": True,
                "dynamic_range_analysis": True,
                "frequency_response_analysis": True
            },
            "postprocessing": {
                "dithering": True,
                "bit_depth_optimization": True,
                "metadata_embedding": True,
                "format_optimization": True,
                "quality_verification": True
            }
        }
    
    def _initialize_platform_configs(self) -> Dict[str, Dict[str, Any]]:
        """Initialize platform-specific configurations"""
        return {
            "spotify": {
                "target_lufs": -14.0,
                "peak_limit": -1.0,
                "sample_rate": 44100,
                "bit_depth": 16,
                "format": "ogg",
                "quality_profile": "high"
            },
            "youtube": {
                "target_lufs": -13.0,
                "peak_limit": -1.0,
                "sample_rate": 48000,
                "bit_depth": 16,
                "format": "aac",
                "quality_profile": "streaming"
            },
            "instagram": {
                "target_lufs": -16.0,
                "peak_limit": -2.0,
                "sample_rate": 44100,
                "bit_depth": 16,
                "format": "aac",
                "max_duration": 60
            },
            "tiktok": {
                "target_lufs": -16.0,
                "peak_limit": -1.0,
                "sample_rate": 44100,
                "bit_depth": 16,
                "format": "aac",
                "max_duration": 180
            },
            "podcast": {
                "target_lufs": -19.0,
                "peak_limit": -3.0,
                "sample_rate": 44100,
                "bit_depth": 16,
                "format": "mp3",
                "speech_optimization": True
            }
        }
    
    def get_processing_config(self, 
                            content_type: str = "music",
                            platform: Optional[str] = None) -> Dict[str, Any]:
        """
        Get optimized processing configuration
        
        Args:
            content_type: Type of content (music, speech, podcast, etc.)
            platform: Target platform (spotify, youtube, etc.)
            
        Returns:
            Optimized processing configuration
        """
        try:
            base_config = {
                "mode": self._processing_mode.value,
                "quality_tier": self._quality_tier.value,
                "complexity": self._complexity.value,
                "buffer_strategy": self._buffer_strategy.value,
                "pipeline": self._pipeline_config.copy()
            }
            
            # Apply content type optimizations
            if content_type == "speech":
                base_config["pipeline"]["preprocessing"]["high_pass_filter"] = 150.0
                base_config["pipeline"]["preprocessing"]["low_pass_filter"] = 8000.0
                base_config["pipeline"]["enhancement"]["eq_enabled"] = True
                self.ml_config.enable_vocal_isolation = True
                
            elif content_type == "music":
                base_config["pipeline"]["enhancement"]["stereo_widening"] = True
                base_config["pipeline"]["enhancement"]["harmonic_enhancement"] = True
                self.ml_config.enable_auto_mastering = True
                
            elif content_type == "podcast":
                base_config["pipeline"]["preprocessing"]["noise_gate_threshold"] = -45.0
                base_config["pipeline"]["enhancement"]["compression_enabled"] = True
                self.ml_config.enable_noise_reduction = True
            
            # Apply platform-specific settings
            if platform and platform in self._platform_configs:
                platform_config = self._platform_configs[platform]
                base_config.update({
                    "platform_settings": platform_config,
                    "target_lufs": platform_config["target_lufs"],
                    "peak_limit": platform_config["peak_limit"]
                })
            
            # Add ML configuration
            base_config["ml_config"] = {
                "ai_enhancement": self.ml_config.enable_ai_enhancement,
                "noise_reduction": self.ml_config.enable_noise_reduction,
                "auto_mastering": self.ml_config.enable_auto_mastering,
                "vocal_isolation": self.ml_config.enable_vocal_isolation,
                "genre_detection": self.ml_config.enable_genre_detection,
                "gpu_acceleration": self.ml_config.gpu_acceleration,
                "model_precision": self.ml_config.model_precision
            }
            
            return base_config
            
        except Exception as e:
            self.logger.error(f"Failed to get processing config: {e}")
            return self._get_fallback_config()
    
    def _get_fallback_config(self) -> Dict[str, Any]:
        """Get fallback configuration for error scenarios"""
        return {
            "mode": AudioProcessingMode.BATCH.value,
            "quality_tier": AudioQualityTier.STREAMING.value,
            "complexity": ProcessingComplexity.STANDARD.value,
            "buffer_strategy": AudioBufferStrategy.FIXED.value,
            "sample_rate": 44100,
            "bit_depth": 16,
            "channels": 2,
            "format": "wav"
        }
    
    def validate_processing_config(self, config: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate processing configuration
        
        Args:
            config: Configuration to validate
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []
        is_valid = True
        
        try:
            # Validate required fields
            required_fields = ["mode", "quality_tier", "complexity"]
            for field in required_fields:
                if field not in config:
                    errors.append(f"Missing required field: {field}")
                    is_valid = False
            
            # Validate sample rate
            if "sample_rate" in config:
                sample_rate = config["sample_rate"]
                if not (self.processing_limits.min_sample_rate <= 
                       sample_rate <= self.processing_limits.max_sample_rate):
                    errors.append(
                        f"Sample rate {sample_rate} out of range "
                        f"[{self.processing_limits.min_sample_rate}, "
                        f"{self.processing_limits.max_sample_rate}]"
                    )
                    is_valid = False
            
            # Validate bit depth
            if "bit_depth" in config:
                bit_depth = config["bit_depth"]
                if not (self.processing_limits.min_bit_depth <= 
                       bit_depth <= self.processing_limits.max_bit_depth):
                    errors.append(
                        f"Bit depth {bit_depth} out of range "
                        f"[{self.processing_limits.min_bit_depth}, "
                        f"{self.processing_limits.max_bit_depth}]"
                    )
                    is_valid = False
            
            # Validate channels
            if "channels" in config:
                channels = config["channels"]
                if not (1 <= channels <= self.processing_limits.max_channels):
                    errors.append(
                        f"Channel count {channels} out of range [1, "
                        f"{self.processing_limits.max_channels}]"
                    )
                    is_valid = False
            
        except Exception as e:
            errors.append(f"Validation error: {str(e)}")
            is_valid = False
        
        return is_valid, errors
    
    def get_performance_profile(self, target_latency: float) -> Dict[str, Any]:
        """
        Get performance-optimized configuration profile
        
        Args:
            target_latency: Target latency in milliseconds
            
        Returns:
            Performance-optimized configuration
        """
        try:
            if target_latency <= 5.0:
                # Ultra-low latency profile
                return {
                    "buffer_size": 64,
                    "processing_mode": AudioProcessingMode.REALTIME.value,
                    "buffer_strategy": AudioBufferStrategy.REALTIME.value,
                    "complexity": ProcessingComplexity.MINIMAL.value,
                    "enable_gpu": True,
                    "parallel_processing": True,
                    "cache_enabled": True
                }
            elif target_latency <= 20.0:
                # Low latency profile
                return {
                    "buffer_size": 256,
                    "processing_mode": AudioProcessingMode.REALTIME.value,
                    "buffer_strategy": AudioBufferStrategy.ADAPTIVE.value,
                    "complexity": ProcessingComplexity.STANDARD.value,
                    "enable_gpu": True,
                    "parallel_processing": True,
                    "cache_enabled": True
                }
            else:
                # High quality profile
                return {
                    "buffer_size": 1024,
                    "processing_mode": AudioProcessingMode.BATCH.value,
                    "buffer_strategy": AudioBufferStrategy.ADAPTIVE.value,
                    "complexity": ProcessingComplexity.ULTRA.value,
                    "enable_gpu": True,
                    "parallel_processing": True,
                    "cache_enabled": True
                }
                
        except Exception as e:
            self.logger.error(f"Failed to get performance profile: {e}")
            return self._get_fallback_config()
    
    def update_ml_config(self, **kwargs) -> bool:
        """
        Update machine learning configuration
        
        Args:
            **kwargs: ML configuration parameters
            
        Returns:
            Success status
        """
        try:
            for key, value in kwargs.items():
                if hasattr(self.ml_config, key):
                    setattr(self.ml_config, key, value)
                else:
                    self.logger.warning(f"Unknown ML config parameter: {key}")
            
            self.logger.info("ML configuration updated successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update ML config: {e}")
            return False
    
    def get_supported_formats(self) -> List[str]:
        """Get list of supported audio formats"""
        return self._supported_formats.copy()
    
    def is_format_supported(self, format_name: str) -> bool:
        """
Check if audio format is supported"""
        return format_name.lower() in self._supported_formats
    
    def get_platform_config(self, platform: str) -> Optional[Dict[str, Any]]:
        """
Get platform-specific configuration"""
        return self._platform_configs.get(platform.lower())
    
    def add_custom_platform(self, platform: str, config: Dict[str, Any]) -> bool:
        """
        Add custom platform configuration
        
        Args:
            platform: Platform name
            config: Platform configuration
            
        Returns:
            Success status
        """
        try:
            required_keys = ["target_lufs", "peak_limit", "sample_rate", 
                           "bit_depth", "format"]
            
            if not all(key in config for key in required_keys):
                missing = [key for key in required_keys if key not in config]
                self.logger.error(f"Missing required platform config keys: {missing}")
                return False
            
            self._platform_configs[platform.lower()] = config
            self.logger.info(f"Added custom platform config: {platform}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to add custom platform: {e}")
            return False
    
    @property
    def processing_mode(self) -> AudioProcessingMode:
        """Get current processing mode"""
        return self._processing_mode
    
    @processing_mode.setter
    def processing_mode(self, mode: AudioProcessingMode):
        """
Set processing mode"""
        self._processing_mode = mode
        self.logger.info(f"Processing mode set to: {mode.value}")
    
    @property
    def quality_tier(self) -> AudioQualityTier:
        """Get current quality tier"""
        return self._quality_tier
    
    @quality_tier.setter
    def quality_tier(self, tier: AudioQualityTier):
        """
Set quality tier"""
        self._quality_tier = tier
        self.logger.info(f"Quality tier set to: {tier.value}")
    
    def get_memory_usage_estimate(self, 
                                 sample_rate: int,
                                 duration: float,
                                 bit_depth: int,
                                 channels: int) -> Dict[str, float]:
        """
        Estimate memory usage for audio processing
        
        Args:
            sample_rate: Audio sample rate
            duration: Audio duration in seconds
            bit_depth: Audio bit depth
            channels: Number of channels
            
        Returns:
            Memory usage estimates in MB
        """
        try:
            # Raw audio memory
            samples = sample_rate * duration * channels
            bytes_per_sample = bit_depth / 8
            raw_memory = (samples * bytes_per_sample) / (1024 * 1024)
            
            # Processing buffers (typically 3-5x raw size)
            processing_memory = raw_memory * 4
            
            # ML model memory (if enabled)
            ml_memory = 0
            if self.ml_config.enable_ai_enhancement:
                ml_memory += 200  # AI enhancement model
            if self.ml_config.enable_noise_reduction:
                ml_memory += 150  # Noise reduction model
            if self.ml_config.enable_vocal_isolation:
                ml_memory += 300  # Vocal isolation model
            
            # Cache memory
            cache_memory = processing_memory * 0.5 if self._buffer_strategy == AudioBufferStrategy.ADAPTIVE else 0
            
            total_memory = raw_memory + processing_memory + ml_memory + cache_memory
            
            return {
                "raw_audio": round(raw_memory, 2),
                "processing_buffers": round(processing_memory, 2),
                "ml_models": round(ml_memory, 2),
                "cache": round(cache_memory, 2),
                "total_estimated": round(total_memory, 2)
            }
            
        except Exception as e:
            self.logger.error(f"Memory estimation failed: {e}")
            return {"total_estimated": 512.0}  # Fallback estimate
    
    def export_config(self) -> Dict[str, Any]:
        """Export complete configuration as dictionary"""
        try:
            return {
                "processing_mode": self._processing_mode.value,
                "quality_tier": self._quality_tier.value,
                "complexity": self._complexity.value,
                "buffer_strategy": self._buffer_strategy.value,
                "performance_metrics": {
                    "max_latency_ms": self.performance_metrics.max_latency_ms,
                    "target_cpu_usage": self.performance_metrics.target_cpu_usage,
                    "memory_limit_mb": self.performance_metrics.memory_limit_mb,
                    "throughput_target": self.performance_metrics.throughput_target,
                    "quality_threshold": self.performance_metrics.quality_threshold
                },
                "ml_config": {
                    "enable_ai_enhancement": self.ml_config.enable_ai_enhancement,
                    "enable_noise_reduction": self.ml_config.enable_noise_reduction,
                    "enable_auto_mastering": self.ml_config.enable_auto_mastering,
                    "enable_vocal_isolation": self.ml_config.enable_vocal_isolation,
                    "gpu_acceleration": self.ml_config.gpu_acceleration,
                    "model_precision": self.ml_config.model_precision
                },
                "supported_formats": self._supported_formats,
                "platform_configs": self._platform_configs,
                "pipeline_config": self._pipeline_config
            }
        except Exception as e:
            self.logger.error(f"Config export failed: {e}")
            return {}
